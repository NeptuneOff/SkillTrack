"""End-to-end API smoke test for a running SkillTrack stack.

The probe creates uniquely named records and removes them in a ``finally``
block. It exercises real PostgreSQL writes without polluting the demo account.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
import io
import json
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str
    duration_ms: float


class SmokeFailure(RuntimeError):
    """Raised when a smoke-test assertion is not satisfied."""


class ApiClient:
    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token: str | None = None

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        json_body: dict[str, Any] | None = None,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        expected: tuple[int, ...] = (200,),
    ) -> tuple[int, dict[str, str], Any]:
        request_headers = {"Accept": "application/json", **(headers or {})}
        payload = body
        if json_body is not None:
            payload = json.dumps(json_body).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        if self.token:
            request_headers["Authorization"] = f"Bearer {self.token}"
        request = Request(
            f"{self.base_url}{path}",
            data=payload,
            headers=request_headers,
            method=method,
        )
        try:
            response = urlopen(request, timeout=self.timeout)
        except HTTPError as exc:
            response = exc
        try:
            status = response.status
            raw = response.read()
            response_headers = {key.lower(): value for key, value in response.headers.items()}
        finally:
            response.close()
        content_type = response_headers.get("content-type", "")
        if "json" in content_type and raw:
            decoded: Any = json.loads(raw)
        else:
            decoded = raw.decode("utf-8-sig", errors="replace")
        if status not in expected:
            detail = decoded if isinstance(decoded, str) else json.dumps(decoded, ensure_ascii=False)
            raise SmokeFailure(f"{method} {path}: HTTP {status}, expected {expected}: {detail[:500]}")
        return status, response_headers, decoded


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def multipart_csv(filename: str, content: str) -> tuple[bytes, str]:
    boundary = f"----skilltrack-{uuid4().hex}"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode()
    body += content.encode("utf-8")
    body += f"\r\n--{boundary}--\r\n".encode("ascii")
    return body, f"multipart/form-data; boundary={boundary}"


def wait_for_mail(mailhog_url: str, marker: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    endpoint = f"{mailhog_url.rstrip('/')}/api/v2/messages?limit=50"
    while time.monotonic() < deadline:
        try:
            with urlopen(endpoint, timeout=min(timeout, 5)) as response:
                if marker in response.read().decode("utf-8", errors="replace"):
                    return
        except (HTTPError, URLError, TimeoutError, OSError):
            pass
        time.sleep(0.25)
    raise SmokeFailure(f"notification '{marker}' not found in MailHog within {timeout:g}s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exercise the principal SkillTrack API flows and clean up afterwards.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--email", default="demo@skilltrack.dev")
    parser.add_argument("--password", default="DemoPassword123!")
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--mailhog-url", help="When set, also verify the goal-completion email.")
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = ApiClient(args.base_url, args.timeout)
    marker = f"smoke-{datetime.now(UTC):%Y%m%dT%H%M%S}-{uuid4().hex[:8]}"
    checks: list[Check] = []
    cleanup_errors: list[str] = []
    workout_ids: list[str] = []
    goal_ids: list[str] = []
    import_ids: list[str] = []
    failure: str | None = None

    def check(name: str, operation) -> Any:
        started = time.perf_counter()
        try:
            result = operation()
        except Exception as exc:
            checks.append(Check(name, False, str(exc), round((time.perf_counter() - started) * 1000, 2)))
            raise
        checks.append(Check(name, True, "ok", round((time.perf_counter() - started) * 1000, 2)))
        return result

    try:

        def health_check() -> None:
            _, headers, payload = client.request("/health")
            require(payload == {"status": "ok", "app": "SkillTrack"}, "unexpected health payload")
            require(headers.get("x-content-type-options") == "nosniff", "missing nosniff header")
            require(headers.get("x-frame-options") == "DENY", "missing clickjacking protection")
            require(bool(headers.get("x-request-id")), "missing request correlation ID")

        check("health_and_security_headers", health_check)

        def unauthorised_check() -> None:
            client.token = "invalid-token"
            client.request("/dashboard", expected=(401,))
            client.token = None

        check("jwt_rejects_invalid_token", unauthorised_check)

        def login_check() -> None:
            _, _, payload = client.request(
                "/auth/login",
                method="POST",
                json_body={"email": args.email, "password": args.password},
            )
            require(isinstance(payload, dict) and bool(payload.get("access_token")), "login returned no access token")
            client.token = payload["access_token"]

        check("jwt_login", login_check)

        def dashboard_check() -> None:
            _, _, profile = client.request("/users/me")
            require(profile.get("email") == args.email, "profile is not the authenticated user")
            _, _, dashboard = client.request("/dashboard")
            expected_fields = {
                "workout_count",
                "set_count",
                "total_volume",
                "weekly_volume",
                "recent_workouts",
                "goals",
            }
            require(expected_fields <= set(dashboard), "dashboard is missing real-data fields")
            require(isinstance(dashboard["workout_count"], int), "dashboard workout_count is not numeric")

        check("profile_and_dashboard", dashboard_check)

        workout_payload = {
            "title": f"Jury smoke workout {marker}",
            "date": date.today().isoformat(),
            "type": "Technique",
            "intensity": 6,
            "duration_minutes": 42,
            "notes": "Created automatically by scripts/smoke_test.py",
            "sets": [
                {
                    "exercise": "Tuck planche smoke",
                    "category": "figure",
                    "set_count": 3,
                    "reps": 5,
                    "load_kg": 0,
                    "duration_seconds": 12,
                    "difficulty": 6,
                    "assistance_kg": 0,
                    "notes": marker,
                }
            ],
        }

        def workout_crud_check() -> str:
            _, _, created = client.request("/workouts", method="POST", json_body=workout_payload)
            workout_id = created.get("id")
            require(bool(workout_id), "workout creation returned no ID")
            workout_ids.append(workout_id)
            require(len(created.get("sets", [])) == 1, "workout exercise was not persisted")
            updated_payload = {**workout_payload, "title": f"Jury smoke workout updated {marker}", "intensity": 7}
            _, _, updated = client.request(f"/workouts/{workout_id}", method="PUT", json_body=updated_payload)
            require(updated.get("title") == updated_payload["title"], "workout title update was not persisted")
            require(updated.get("intensity") == 7, "workout intensity update was not persisted")
            return workout_id

        workout_id = check("workout_and_exercise_crud", workout_crud_check)

        goal_payload = {
            "skill": f"Jury smoke goal {marker}",
            "goal_type": "figure",
            "target": "Hold for 10 seconds",
            "current_level": "5 seconds",
            "current_value": 5,
            "target_value": 10,
            "unit": "secondes",
            "priority": "haute",
            "notes": marker,
            "status": "actif",
            "deadline": date.today().isoformat(),
            "is_done": False,
        }

        def goal_crud_check() -> str:
            _, _, created = client.request("/goals", method="POST", json_body=goal_payload)
            goal_id = created.get("id")
            require(bool(goal_id), "goal creation returned no ID")
            goal_ids.append(goal_id)
            completed_payload = {**goal_payload, "status": "termine", "is_done": True, "current_value": 10}
            _, _, completed = client.request(f"/goals/{goal_id}", method="PUT", json_body=completed_payload)
            require(completed.get("status") == "termine", "goal completion status was not persisted")
            require(completed.get("is_done") is True, "goal completion boolean is inconsistent")
            return goal_id

        goal_id = check("goal_crud_and_completion", goal_crud_check)

        if args.mailhog_url:
            check("goal_completion_notification", lambda: wait_for_mail(args.mailhog_url, goal_payload["skill"], args.timeout))

        def export_check() -> None:
            _, json_headers, exported = client.request("/exports/json")
            require("attachment" in json_headers.get("content-disposition", ""), "JSON is not downloadable")
            require({"metadata", "profile", "workouts", "goals", "imports"} <= set(exported), "JSON export is incomplete")
            require(exported["profile"].get("email") == args.email, "JSON export is not user-scoped")
            require(any(item.get("id") == workout_id for item in exported["workouts"]), "created workout absent from JSON")
            require(any(item.get("id") == goal_id for item in exported["goals"]), "created goal absent from JSON")

            _, csv_headers, csv_content = client.request("/exports/csv")
            require("attachment" in csv_headers.get("content-disposition", ""), "CSV is not downloadable")
            rows = list(csv.DictReader(io.StringIO(csv_content)))
            record_types = {row.get("record_type") for row in rows}
            require({"metadata", "profile", "workout", "training_set", "goal"} <= record_types, "CSV export is incomplete")
            require(any(row.get("workout_id") == workout_id for row in rows), "created workout absent from CSV")
            require(any(row.get("goal_id") == goal_id for row in rows), "created goal absent from CSV")
            require("_sa_instance_state" not in csv_content, "CSV contains ORM internals")

        check("complete_json_and_csv_exports", export_check)

        imported_title = f"Jury smoke import {marker}"
        import_content = (
            "date,title,type,intensity,duration_minutes,workout_notes,exercise,category,set_count,reps,"
            "load_kg,duration_seconds,difficulty,assistance_kg,set_notes\n"
            f"{date.today().isoformat()},{imported_title},Technique,6,30,{marker},Smoke hold,figure,2,0,0,10,5,0,valid\n"
            f"{date.today().isoformat()},Invalid {marker},Technique,99,30,bad,Bad set,figure,1,0,0,1,5,0,rejected\n"
        )

        def import_check() -> None:
            body, content_type = multipart_csv(f"{marker}.csv", import_content)
            _, _, report = client.request(
                "/imports/csv",
                method="POST",
                body=body,
                headers={"Content-Type": content_type},
            )
            import_id = report.get("import_id") or report.get("id")
            require(bool(import_id), "CSV import returned no history ID")
            import_ids.append(import_id)
            require(report.get("status") == "completed_with_errors", "mixed CSV did not report partial errors")
            require(report.get("imported_rows", 0) >= 1, "valid CSV row was not imported")
            require(report.get("rejected_rows", 0) >= 1, "invalid CSV row was not rejected")
            require(bool(report.get("errors")), "CSV error report is empty")

            _, _, workouts = client.request("/workouts")
            matches = [item for item in workouts if item.get("title") == imported_title]
            require(len(matches) == 1, "valid imported workout was not persisted exactly once")
            workout_ids.append(matches[0]["id"])
            _, _, history = client.request("/imports/history")
            matches = [item for item in history if item.get("id") == import_id]
            require(len(matches) == 1 and bool(matches[0].get("errors")), "import history lost the error report")

        check("csv_import_with_error_report", import_check)

    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        if client.token:
            for import_id in reversed(import_ids):
                try:
                    client.request(f"/imports/history/{import_id}", method="DELETE")
                except Exception as exc:
                    cleanup_errors.append(f"import {import_id}: {exc}")
            for goal_id in reversed(goal_ids):
                try:
                    client.request(f"/goals/{goal_id}", method="DELETE")
                except Exception as exc:
                    cleanup_errors.append(f"goal {goal_id}: {exc}")
            for created_workout_id in reversed(workout_ids):
                try:
                    client.request(f"/workouts/{created_workout_id}", method="DELETE")
                except Exception as exc:
                    cleanup_errors.append(f"workout {created_workout_id}: {exc}")

    passed = failure is None and not cleanup_errors and all(item.passed for item in checks)
    report = {
        "schema_version": "1.0",
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "base_url": args.base_url,
        "passed": passed,
        "checks": [asdict(item) for item in checks],
        "cleanup": {"passed": not cleanup_errors, "errors": cleanup_errors},
        "failure": failure,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
