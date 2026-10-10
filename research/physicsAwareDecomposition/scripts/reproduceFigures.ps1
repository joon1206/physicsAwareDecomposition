param([string]$OutputRoot = "", [string]$Python = "")
$padProject = Split-Path -Parent $PSScriptRoot
if ($OutputRoot) { $env:PAD_OUTPUT_ROOT = $OutputRoot }
if (-not $Python) {
    $padBundled = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $padBundled) { $Python = $padBundled } else { $Python = "python" }
}
& $Python (Join-Path $PSScriptRoot "generatePlots.py")
if ($LASTEXITCODE -ne 0) { throw "Figure generation failed" }
