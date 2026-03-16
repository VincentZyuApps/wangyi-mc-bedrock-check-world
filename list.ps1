<#
.SYNOPSIS
    列出 Minecraft 基岩版（网易）存档信息。
    支持颜色输出、Emoji 标识、手动对齐。
#>

param (
    [switch]$NoColor,
    [switch]$NoEmoji
)

# 存档目录
$WorldsDir = "$env:APPDATA\MinecraftPC_Netease_PB\minecraftWorlds"

if (-not (Test-Path $WorldsDir)) {
    Write-Error "找不到存档目录: $WorldsDir"
    exit
}

# 定义 Emoji
$eFolder = if ($NoEmoji) { "" } else { "📂 " }
$eList   = if ($NoEmoji) { "" } else { "📜 " }
$eWorld  = if ($NoEmoji) { "" } else { "🌍 " }
$eTime   = if ($NoEmoji) { "" } else { "🕒 " }
$eSize   = if ($NoEmoji) { "" } else { "💾 " }
$eCount  = if ($NoEmoji) { "" } else { "📊 " }

# 颜色设置（PowerShell 原生支持 Write-Host -ForegroundColor）
function Write-Color {
    param($Text, $Color = "White", [switch]$NoNewLine)
    if ($NoColor) {
        Write-Host $Text -NoNewline:$NoNewLine
    } else {
        Write-Host $Text -ForegroundColor $Color -NoNewline:$NoNewLine
    }
}

Write-Host ""
Write-Color "  $eFolder 正在读取存档目录: " -Color Blue -NoNewLine
Write-Color $WorldsDir -Color Cyan
Write-Host "`n"

# 计算文件夹大小的函数
function Get-FolderSize([string]$Path) {
    try {
        $files = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue
        if ($null -eq $files) { return 0 }
        ($files | Measure-Object -Property Length -Sum).Sum
    } catch {
        return 0
    }
}

# 格式化大小
function Format-Size([long]$Bytes) {
    if ($Bytes -lt 1KB) { return "{0:N2} B" -f $Bytes }
    if ($Bytes -lt 1MB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    if ($Bytes -lt 1GB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    return "{0:N2} GB" -f ($Bytes / 1GB)
}

# 获取字符显示宽度（简单处理中文）
function Get-DisplayWidth([string]$s) {
    $width = 0
    foreach ($char in $s.ToCharArray()) {
        if ([int]$char -gt 127) { $width += 2 } else { $width += 1 }
    }
    return $width
}

# 填充字符串到指定宽度
function Pad-String([string]$s, [int]$width) {
    $currentWidth = Get-DisplayWidth $s
    $padding = $width - $currentWidth
    if ($padding -lt 0) { $padding = 0 }
    return $s + (" " * $padding)
}

$worlds = @()

# 遍历目录
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

# 排序
$worlds = $worlds | Sort-Object LastSaved -Descending

if ($worlds.Count -eq 0) {
    Write-Host "  未发现有效存档。"
    exit
}

# 计算最大宽度
$maxFolderWidth = ($worlds | ForEach-Object { Get-DisplayWidth $_.Folder } | Measure-Object -Maximum).Maximum
if ($maxFolderWidth -lt 8) { $maxFolderWidth = 8 }

$maxNameWidth = ($worlds | ForEach-Object { Get-DisplayWidth $_.Name } | Measure-Object -Maximum).Maximum
if ($maxNameWidth -lt 20) { $maxNameWidth = 20 }

# 打印表头
$hFolder = Pad-String ("$eList 文件夹名") ($maxFolderWidth + (if ($NoEmoji) {0} else {2}))
$hName   = Pad-String ("$eWorld 世界名称") ($maxNameWidth + (if ($NoEmoji) {0} else {2}))
$hTime   = ("$eTime 最后保存时间").PadRight(19 + (if ($NoEmoji) {0} else {2}))
$hSize   = "$eSize 大小"

Write-Color "  序号  $hFolder  $hName  $hTime  $hSize" -Color White
Write-Host "  ----  $('-' * $maxFolderWidth)  $('-' * $maxNameWidth)  $('-' * 19)  $('-' * 10)"

# 打印数据
$i = 1
foreach ($w in $worlds) {
    $idx = "$i".PadLeft(4)
    $folder = Pad-String $w.Folder $maxFolderWidth
    $name = Pad-String $w.Name $maxNameWidth
    $timeStr = if ($null -ne $w.LastSaved) { $w.LastSaved.ToString("yyyy-MM-dd HH:mm:ss") } else { "未知" }
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
Write-Color "  $eCount 共 $($worlds.Count) 个存档`n" -Color Blue
