# Sync live credentials from .env into GitHub Actions secrets.
# Values are piped via stdin so they never appear on the command line, in the
# transcript, or in shell history. Only the NAMES and a length fingerprint are printed.
$ErrorActionPreference = 'Stop'
$repo = 'Warriorlegacy/Autogram'

function Get-EnvMap {
    $map = @{}
    foreach ($line in Get-Content .env -Encoding UTF8) {
        $t = $line.Trim()
        if (-not $t -or $t.StartsWith('#') -or -not $t.Contains('=')) { continue }
        $i = $t.IndexOf('=')
        $k = $t.Substring(0, $i).Trim()
        $v = $t.Substring($i + 1).Trim()
        if ($v.Length -ge 2 -and $v[0] -eq $v[$v.Length - 1] -and ($v[0] -eq '"' -or $v[0] -eq "'")) {
            $v = $v.Substring(1, $v.Length - 2)
        }
        if ($k) { $map[$k] = $v }
    }
    return $map
}

$env_ = Get-EnvMap
$names = @(
    'GROQ_API_KEY',
    'GEMINI_API_KEY',
    'IG_USER_ID',
    'IG_ACCESS_TOKEN',
    'META_GRAPH_ACCESS_TOKEN',
    'META_APP_ID',
    'META_APP_SECRET',
    'AUTOGRAM_OWNER_KEY'
)

$sha = [System.Security.Cryptography.SHA256]::Create()

foreach ($n in $names) {
    $v = $env_[$n]
    if (-not $v) {
        Write-Output ("  SKIP {0,-24} not present in .env" -f $n)
        continue
    }
    # Fingerprint only: proves what was sent without revealing it.
    $h = [System.BitConverter]::ToString(
            $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($v))
        ).Replace('-', '').Substring(0, 10)
    $v | gh secret set $n --repo $repo 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Output ("  OK   {0,-24} len={1,-4} sha={2}" -f $n, $v.Length, $h)
    } else {
        Write-Output ("  FAIL {0,-24} gh exited {1}" -f $n, $LASTEXITCODE)
    }
}

Write-Output ""
Write-Output "verifying names now present:"
gh secret list --repo $repo --json name,updatedAt |
    ConvertFrom-Json |
    Where-Object { $names -contains $_.name } |
    Sort-Object name |
    ForEach-Object { "   {0,-24} {1}" -f $_.name, $_.updatedAt }