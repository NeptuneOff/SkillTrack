$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required"
    exit 10
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env created from .env.example"
}

docker compose up --build -d
python scripts/smoke_test.py
Write-Host "SkillTrack is ready: http://localhost:5173"
