<#
.SYNOPSIS
  Installs the Sundered Realms Iris pack on top of your local Iris "overworld" pack.

.DESCRIPTION
  1. Copies your overworld pack (default: C:\Users\William Turturici\Downloads\overworld) to
     <Server>\plugins\Iris\packs\sundered-realms
  2. Overlays this repository's pack\ folder (new dimension, regions, biomes, generators,
     structures, loot, monsters) on top of that copy.
  3. Removes the copied dimensions\overworld.json so the pack only exposes the new dimension.

  Your original overworld folder is never modified.

.EXAMPLE
  .\install.ps1 -Server "C:\MinecraftServer"

.EXAMPLE
  .\install.ps1 -Source "D:\packs\overworld" -Server "C:\MinecraftServer" -Force
#>
param(
    [string]$Source = "C:\Users\William Turturici\Downloads\overworld",
    [Parameter(Mandatory = $true)][string]$Server,
    [string]$PackName = "sundered-realms",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$overlay = Join-Path $PSScriptRoot "pack"

if (-not (Test-Path (Join-Path $Source "dimensions\overworld.json"))) {
    # Allow pointing at a folder that contains the pack one level down (e.g. an extracted zip).
    $nested = Get-ChildItem -Path $Source -Directory -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName "dimensions\overworld.json") } | Select-Object -First 1
    if ($nested) { $Source = $nested.FullName }
    else { throw "No dimensions\overworld.json under '$Source'. Point -Source at your Iris overworld pack folder." }
}
if (-not (Test-Path $overlay)) { throw "Overlay folder '$overlay' is missing. Run this script from iris-packs\sundered-realms." }

$packs = Join-Path $Server "plugins\Iris\packs"
$dest = Join-Path $packs $PackName
if (Test-Path $dest) {
    if (-not $Force) { throw "'$dest' already exists. Re-run with -Force to replace it." }
    Remove-Item -Recurse -Force $dest
}
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Write-Host "Copying base overworld pack from $Source ..."
robocopy $Source $dest /E /XD .git .github /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying the base pack (exit $LASTEXITCODE)." }

Write-Host "Overlaying Sundered Realms content ..."
robocopy $overlay $dest /E /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying the overlay (exit $LASTEXITCODE)." }

$oldDim = Join-Path $dest "dimensions\overworld.json"
if (Test-Path $oldDim) { Remove-Item $oldDim }

Write-Host ""
Write-Host "Installed to $dest" -ForegroundColor Green
Write-Host "Create a world in-game or from the console with:"
Write-Host "    /iris create name=aerthos type=$PackName"
Write-Host "Or make it the default world by adding this to bukkit.yml:"
Write-Host "    worlds:"
Write-Host "      world:"
Write-Host "        generator: Iris:$PackName"
