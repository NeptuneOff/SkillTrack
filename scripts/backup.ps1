param(
    [string]$Destination = 'artifacts/backups'
)

$ErrorActionPreference = 'Stop'
$SkillTrackRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$SkillTrackDestination = [IO.Path]::GetFullPath((Join-Path $SkillTrackRoot $Destination))
if (-not $SkillTrackDestination.StartsWith($SkillTrackRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Le dossier de sauvegarde doit rester dans le projet SkillTrack.'
}

New-Item -ItemType Directory -Path $SkillTrackDestination -Force | Out-Null
$SkillTrackBackupName = 'skilltrack-{0}.dump' -f (Get-Date -Format 'yyyyMMdd-HHmmss')
$SkillTrackContainerPath = '/tmp/' + $SkillTrackBackupName
$SkillTrackHostPath = Join-Path $SkillTrackDestination $SkillTrackBackupName

Set-Location -LiteralPath $SkillTrackRoot
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --file="$1"' sh $SkillTrackContainerPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

try {
    docker compose cp "db:$SkillTrackContainerPath" $SkillTrackHostPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    docker compose exec -T db rm -f -- $SkillTrackContainerPath | Out-Null
}

$SkillTrackHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $SkillTrackHostPath).Hash
Write-Host "Sauvegarde créée : $SkillTrackHostPath"
Write-Host "SHA-256 : $SkillTrackHash"
