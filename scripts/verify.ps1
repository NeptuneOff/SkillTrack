param(
    [switch]$SkipPerformance,
    [switch]$SkipE2E,
    [switch]$SkipProductionBuild
)

$ErrorActionPreference = 'Stop'
$SkillTrackRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $SkillTrackRoot

function Invoke-SkillTrackCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [Parameter(Mandatory = $true)]
        [string[]]$CommandArguments
    )
    & $Executable @CommandArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Commande en échec ($LASTEXITCODE) : $Executable $($CommandArguments -join ' ')"
    }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop est requis et doit être disponible dans le PATH.'
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python 3 est requis pour les scénarios smoke et performance.'
}
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
    Write-Host 'Fichier .env local créé depuis .env.example.'
}

$SkillTrackArtifacts = Join-Path $SkillTrackRoot 'artifacts/validation'
New-Item -ItemType Directory -Path $SkillTrackArtifacts -Force | Out-Null

Invoke-SkillTrackCommand docker @('compose', 'config', '--quiet')
Invoke-SkillTrackCommand docker @('compose', '--file', 'docker-compose.prod.yml', 'config', '--quiet')
if (-not $SkipProductionBuild) {
    Invoke-SkillTrackCommand docker @('compose', '--file', 'docker-compose.prod.yml', 'build', 'backend', 'frontend')
}
Invoke-SkillTrackCommand docker @('compose', 'up', '--build', '--detach', '--wait', '--wait-timeout', '180', '--remove-orphans')
Invoke-SkillTrackCommand docker @('compose', 'exec', '-T', 'db', 'sh', '-c', 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" --set ON_ERROR_STOP=1 -Atc "SELECT current_database(), version();"')
Invoke-SkillTrackCommand docker @('compose', 'exec', '-T', 'backend', 'alembic', '-c', 'app/alembic.ini', 'current', '--check-heads')
Invoke-SkillTrackCommand docker @('compose', 'exec', '-T', 'backend', 'ruff', 'check', 'app', 'tests')
Invoke-SkillTrackCommand docker @('compose', 'exec', '-T', 'backend', 'mypy', 'app')
Invoke-SkillTrackCommand docker @(
    'compose', 'exec', '-T', 'backend', 'pytest', '-q',
    '--cov=app', '--cov-fail-under=90', '--cov-report=term-missing',
    '--cov-report=xml:/tmp/backend-coverage.xml', '--junitxml=/tmp/backend-junit.xml'
)
Invoke-SkillTrackCommand docker @('compose', 'cp', 'backend:/tmp/backend-coverage.xml', 'artifacts/validation/backend-coverage.xml')
Invoke-SkillTrackCommand docker @('compose', 'cp', 'backend:/tmp/backend-junit.xml', 'artifacts/validation/backend-junit.xml')
Invoke-SkillTrackCommand docker @('compose', 'exec', '-T', 'frontend', 'npm', 'run', 'lint')
Invoke-SkillTrackCommand docker @(
    'compose', 'exec', '-T', 'frontend', 'npm', 'test', '--', '--run',
    '--reporter=default', '--reporter=junit', '--outputFile.junit=/tmp/frontend-junit.xml'
)
Invoke-SkillTrackCommand docker @('compose', 'cp', 'frontend:/tmp/frontend-junit.xml', 'artifacts/validation/frontend-junit.xml')
Invoke-SkillTrackCommand docker @('compose', 'exec', '-T', 'frontend', 'npm', 'run', 'build')
if (-not $SkipE2E) {
    Invoke-SkillTrackCommand docker @('compose', '--profile', 'test', 'run', '--rm', 'e2e')
}
Invoke-SkillTrackCommand python @(
    'scripts/smoke_test.py', '--mailhog-url', 'http://localhost:8025',
    '--output', 'artifacts/validation/smoke.json'
)

if (-not $SkipPerformance) {
    Invoke-SkillTrackCommand python @(
        'scripts/performance_test.py', '--users', '20', '--requests', '200',
        '--output', 'artifacts/performance/latest.json'
    )
}

Write-Host "Vérification complète réussie. Rapports : $SkillTrackArtifacts"
