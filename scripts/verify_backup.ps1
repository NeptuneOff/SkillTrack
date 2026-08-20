param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath
)

$ErrorActionPreference = 'Stop'
$SkillTrackRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$SkillTrackBackupPath = [IO.Path]::GetFullPath((Join-Path $SkillTrackRoot $BackupPath))
if (-not $SkillTrackBackupPath.StartsWith($SkillTrackRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'La sauvegarde à vérifier doit se trouver dans le projet SkillTrack.'
}
if (-not (Test-Path -LiteralPath $SkillTrackBackupPath -PathType Leaf)) {
    throw "Sauvegarde introuvable : $SkillTrackBackupPath"
}

$SkillTrackRestoreDb = 'skilltrack_restore_' + ([guid]::NewGuid().ToString('N').Substring(0, 10))
if ($SkillTrackRestoreDb -notmatch '^skilltrack_restore_[0-9a-f]{10}$') {
    throw 'Nom de base temporaire invalide.'
}
$SkillTrackContainerPath = '/tmp/' + $SkillTrackRestoreDb + '.dump'

Set-Location -LiteralPath $SkillTrackRoot
$SkillTrackDbUser = (docker compose exec -T db printenv POSTGRES_USER).Trim()
if ($LASTEXITCODE -ne 0 -or -not $SkillTrackDbUser) {
    throw 'Impossible de lire POSTGRES_USER dans le service db.'
}
docker compose cp $SkillTrackBackupPath "db:$SkillTrackContainerPath"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

try {
    docker compose exec -T db createdb -U $SkillTrackDbUser $SkillTrackRestoreDb
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    docker compose exec -T db pg_restore -U $SkillTrackDbUser -d $SkillTrackRestoreDb --no-owner --no-privileges $SkillTrackContainerPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $SkillTrackCountQuery = "SELECT 'users=' || (SELECT count(*) FROM users) || ', workouts=' || (SELECT count(*) FROM workouts) || ', goals=' || (SELECT count(*) FROM goals) || ', imports=' || (SELECT count(*) FROM import_jobs);"
    docker compose exec -T db psql -U $SkillTrackDbUser -d $SkillTrackRestoreDb --set ON_ERROR_STOP=1 -At -c $SkillTrackCountQuery
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host 'Restauration vérifiée dans une base temporaire isolée.'
} finally {
    docker compose exec -T db dropdb -U $SkillTrackDbUser --if-exists $SkillTrackRestoreDb | Out-Null
    docker compose exec -T db rm -f -- $SkillTrackContainerPath | Out-Null
}
