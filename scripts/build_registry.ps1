param(
  [string]$PackagesDir = "sample-packages",
  [string]$BaseUrl = "https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages",
  [string]$Out = "packages.index.json",
  [string]$SourceName = "azsos-ir-packages"
)

$ErrorActionPreference = "Stop"

python azsos.py registry build `
  --packages-dir $PackagesDir `
  --base-url $BaseUrl `
  --out $Out `
  --source-name $SourceName

Write-Host "Registry written to $Out"
