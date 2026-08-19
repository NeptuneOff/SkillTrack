class SkillTrackError(Exception):
    """Base class for domain errors."""


class NotFoundError(SkillTrackError):
    pass


class ForbiddenError(SkillTrackError):
    pass


class ValidationError(SkillTrackError):
    pass


class ImportErrorReport(SkillTrackError):
    def __init__(self, errors: list[dict[str, object]]):
        super().__init__("Import contains invalid rows")
        self.errors = errors
