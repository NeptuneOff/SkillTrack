param(
    [switch]$Production,
    [ValidateRange(30, 600)]
    [int]$WaitTimeout = 180
)

$ErrorActionPreference = 'Stop'
$SkillTrackRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $SkillTrackRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop est requis et doit être disponible dans le PATH.'
}
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw 'Docker Desktop est installé mais son moteur ne répond pas.'
}

if (-not (Test-Path -LiteralPath '.env')) {
    if ($Production) {
        throw 'Créez un fichier .env dédié à la production avant d’utiliser -Production.'
    }
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
    Write-Host 'Fichier .env créé depuis .env.example. Changez SECRET_KEY avant un déploiement public.'
}

if ($Production) {
    $SkillTrackEnvironment = @{}
    foreach ($SkillTrackLine in Get-Content -LiteralPath '.env') {
        if ($SkillTrackLine -match '^\s*([^#][^=]*)=(.*)$') {
            $SkillTrackEnvironment[$Matches[1].Trim()] = $Matches[2].Trim()
        }
    }
    $SkillTrackSecret = [string]$SkillTrackEnvironment['SECRET_KEY']
    $SkillTrackDbPassword = [string]$SkillTrackEnvironment['POSTGRES_PASSWORD']
    if ($SkillTrackSecret.Length -lt 32 -or $SkillTrackSecret -eq 'change-this-secret-for-local-demo') {
        throw 'SECRET_KEY doit être remplacée par une valeur aléatoire d’au moins 32 caractères en production.'
    }
    if (-not $SkillTrackDbPassword -or $SkillTrackDbPassword -eq 'skilltrack') {
        throw 'POSTGRES_PASSWORD doit être remplacé par un secret dédié en production.'
    }
}

$SkillTrackComposeArgs = @('compose')
if ($Production) {
    $SkillTrackComposeArgs += @('--file', 'docker-compose.prod.yml')
}

& docker @SkillTrackComposeArgs config --quiet
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& docker @SkillTrackComposeArgs up --build --detach --wait --wait-timeout $WaitTimeout --remove-orphans
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& docker @SkillTrackComposeArgs ps
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'SkillTrack est prêt : interface http://localhost:5173'
if (-not $Production) {
    Write-Host 'API http://localhost:8000/docs - Emails de démonstration http://localhost:8025'
}
