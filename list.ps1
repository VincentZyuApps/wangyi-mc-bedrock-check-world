#Requires -Version 5.1
<#
.SYNOPSIS
    List Minecraft Bedrock (NetEase) world saves.
.DESCRIPTION
    Displays folder name, world name, last saved time, and size for each save.
.PARAMETER NoColor
    Disable colored output.
.PARAMETER NoEmoji
    Disable emoji icons.
#>

param (
    [switch]$NoColor,
    [switch]$NoEmoji
)

# Save directory
$WorldsDir = "$env:APPDATA\MinecraftPC_Netease_PB\minecraftWorlds"

if (-not (Test-Path $WorldsDir)) {
    Write-Error "Cannot find save directory: $WorldsDir"
    exit 1
}

# Define Emoji (using Unicode escape sequences for compatibility)
$eFolder = if ($NoEmoji) { "" } else { [char]::ConvertFromUtf32(0x1F4C2) + " " }  # Folder
$eList   = if ($NoEmoji) { "" } else { [char]::ConvertFromUtf32(0x1F4DC) + " " }  # Scroll
$eWorld  = if ($NoEmoji) { "" } else { [char]::ConvertFromUtf32(0x1F30D) + " " }  # Globe
$eTime   = if ($NoEmoji) { "" } else { [char]::ConvertFromUtf32(0x1F552) + " " }  # Clock
$eSize   = if ($NoEmoji) { "" } else { [char]::ConvertFromUtf32(0x1F4BE) + " " }  # Floppy
$eCount  = if ($NoEmoji) { "" } else { [char]::ConvertFromUtf32(0x1F4CA) + " " }  # Chart

# Color output function
function Write-Color {
    param($Text, $Color = "White", [switch]$NoNewLine)
    if ($NoColor) {
        Write-Host $Text -NoNewline:$NoNewLine
    } else {
        Write-Host $Text -ForegroundColor $Color -NoNewline:$NoNewLine
    }
}

Write-Host ""
Write-Color "  $($eFolder)Reading save directory: " -Color Blue -NoNewLine
Write-Color $WorldsDir -Color Cyan
Write-Host "`n"

# Calculate folder size
function Get-FolderSize([string]$Path) {
    try {
        $files = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue
        if ($null -eq $files) { return 0 }
        ($files | Measure-Object -Property Length -Sum).Sum
    } catch {
        return 0
    }
}

# Format size to human readable
function Format-Size([long]$Bytes) {
    if ($Bytes -lt 1KB) { return "{0,6:N2} B" -f $Bytes }
    if ($Bytes -lt 1MB) { return "{0,6:N2} KB" -f ($Bytes / 1KB) }
    if ($Bytes -lt 1GB) { return "{0,6:N2} MB" -f ($Bytes / 1MB) }
    return "{0,6:N2} GB" -f ($Bytes / 1GB)
}

# Get display width (CJK chars = 2, others = 1)
function Get-DisplayWidth([string]$s) {
    $width = 0
    foreach ($char in $s.ToCharArray()) {
        if ([int]$char -gt 127) { $width += 2 } else { $width += 1 }
    }
    return $width
}

# Pad string to specified width
function Pad-String([string]$s, [int]$width) {
    $currentWidth = Get-DisplayWidth $s
    $padding = $width - $currentWidth
    if ($padding -lt 0) { $padding = 0 }
    return $s + (" " * $padding)
}

$worlds = @()

# Iterate directories
Get-ChildItem -Path $WorldsDir -Directory | ForEach-Object {
    $folderName = $_.Name
    $fullPath = $_.FullName
    $levelnamePath = Join-Path $fullPath "levelname.txt"
    $leveldatPath = Join-Path $fullPath "level.dat"

    if (Test-Path $levelnamePath) {
        $worldName = (Get-Content $levelnamePath -Raw -Encoding UTF8).Trim()
        $lastSaved = if (Test-Path $leveldatPath) { (Get-Item $leveldatPath).LastWriteTime } else { $null }
        $size = Get-FolderSize $fullPath
        
        $worlds += [PSCustomObject]@{
            Folder    = $folderName
            Name      = $worldName
            LastSaved = $lastSaved
            Size      = $size
        }
    }
}

# Sort by last saved time descending
$worlds = $worlds | Sort-Object LastSaved -Descending

if ($worlds.Count -eq 0) {
    Write-Host "  No valid saves found."
    exit 0
}

# Calculate max widths
$maxFolderWidth = ($worlds | ForEach-Object { Get-DisplayWidth $_.Folder } | Measure-Object -Maximum).Maximum
if ($maxFolderWidth -lt 12) { $maxFolderWidth = 12 }

$maxNameWidth = ($worlds | ForEach-Object { Get-DisplayWidth $_.Name } | Measure-Object -Maximum).Maximum
if ($maxNameWidth -lt 20) { $maxNameWidth = 20 }

# Print header
$hFolder = Pad-String "Folder" $maxFolderWidth
$hName   = Pad-String "World Name" $maxNameWidth
$hTime   = "Last Saved".PadRight(19)
$hSize   = "Size"

Write-Color "  No.   $hFolder  $hName  $hTime  $hSize" -Color White
Write-Host "  ----  $('-' * $maxFolderWidth)  $('-' * $maxNameWidth)  $('-' * 19)  $('-' * 10)"

# Print data rows
$i = 1
foreach ($w in $worlds) {
    $idx = "$i".PadLeft(4)
    $folder = Pad-String $w.Folder $maxFolderWidth
    $name = Pad-String $w.Name $maxNameWidth
    $timeStr = if ($null -ne $w.LastSaved) { $w.LastSaved.ToString("yyyy-MM-dd HH:mm:ss") } else { "Unknown" }
    $timeStr = $timeStr.PadRight(19)
    $sizeStr = Format-Size $w.Size

    Write-Color "  $idx" -Color Yellow -NoNewLine
    Write-Host "  " -NoNewLine
    Write-Color $folder -Color Cyan -NoNewLine
    Write-Host "  " -NoNewLine
    Write-Color $name -Color Green -NoNewLine
    Write-Host "  " -NoNewLine
    Write-Color $timeStr -Color Magenta -NoNewLine
    Write-Host "  " -NoNewLine
    Write-Color $sizeStr -Color Yellow
    $i++
}

Write-Host ""
Write-Color "  $($eCount)Total: $($worlds.Count) saves`n" -Color Blue
