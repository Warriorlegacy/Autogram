# Autogram — Trigger GitHub Actions Publishing Pipeline
$token = "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"
$headers = @{
    "Authorization" = "Bearer $token"
    "Accept"        = "application/vnd.github+json"
    "User-Agent"    = "Autogram-Scheduler"
}
$body = '{"event_type": "publish-slot"}'

try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/Warriorlegacy/Autogram/dispatches" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Successfully dispatched publishing pipeline to GitHub Actions!" -ForegroundColor Green
} catch {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Failed to dispatch: $_" -ForegroundColor Red
}
