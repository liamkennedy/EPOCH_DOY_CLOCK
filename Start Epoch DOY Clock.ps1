$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$pythonw = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if ($pythonw) {
    Start-Process -FilePath $pythonw.Source -ArgumentList "`"$scriptDir\epoch_doy_clock.py`""
    exit
}

$py = Get-Command py.exe -ErrorAction SilentlyContinue
if ($py) {
    Start-Process -FilePath $py.Source -ArgumentList "-3w", "`"$scriptDir\epoch_doy_clock.py`""
    exit
}

Add-Type -AssemblyName PresentationFramework
[System.Windows.MessageBox]::Show(
    "Python 3 was not found. Install Python 3 for Windows and ensure the Python launcher is enabled.",
    "Epoch DOY Clock"
)
