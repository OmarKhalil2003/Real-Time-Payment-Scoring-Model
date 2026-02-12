Write-Host ""
Write-Host "============================================================"
Write-Host "🚀 Starting Real-Time Payment Scoring System..."
Write-Host "============================================================"

docker compose up --build -d

Write-Host ""
Write-Host "⏳ Waiting for dashboard to be ready..."

$maxRetries = 20
$retry = 0
$ready = $false

while (-not $ready -and $retry -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch {
        Start-Sleep -Seconds 2
        $retry++
    }
}

if ($ready) {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "✅ Dashboard is ready!"
    Write-Host "👉 Opening http://localhost:8501"
    Write-Host "============================================================"
    Write-Host ""
    Start-Process "http://localhost:8501"
} else {
    Write-Host "⚠️ Dashboard did not become ready in time."
    Write-Host "Please open http://localhost:8501 manually."
}
