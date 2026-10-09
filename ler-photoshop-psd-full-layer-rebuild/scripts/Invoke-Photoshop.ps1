[CmdletBinding(DefaultParameterSetName = 'Probe')]
param(
    [Parameter(ParameterSetName = 'Probe')][switch]$ProbeOnly,
    [Parameter(Mandatory = $true, ParameterSetName = 'Execute')][string]$ScriptPath,
    [string]$ProgId = 'Photoshop.Application.200',
    [ValidateRange(1, 999)][int]$ExpectedMajorVersion = 27,
    [string]$ExpectedApplicationPath,
    [string]$ResultPath
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This bridge requires Windows COM automation.' }
$resultAbsolute = $null
if ($ResultPath) {
    $resultAbsolute = [System.IO.Path]::GetFullPath($ResultPath)
    if (Test-Path -LiteralPath $resultAbsolute) { throw "Result already exists: $resultAbsolute" }
    $parent = [System.IO.Path]::GetDirectoryName($resultAbsolute)
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw "Result parent does not exist: $parent" }
}
$scriptText = $null
if ($PSCmdlet.ParameterSetName -eq 'Execute') {
    $resolved = (Resolve-Path -LiteralPath $ScriptPath -ErrorAction Stop).Path
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { throw 'ScriptPath must be a file.' }
    $scriptText = [System.IO.File]::ReadAllText($resolved, [System.Text.Encoding]::UTF8)
    if ([string]::IsNullOrWhiteSpace($scriptText)) { throw 'JSX script is empty.' }
}
if (-not ('LerPhotoshop.NativeBridge' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace LerPhotoshop {
    public static class NativeBridge {
        [DllImport("ole32.dll", CharSet=CharSet.Unicode, PreserveSig=false)]
        private static extern void CLSIDFromProgID(string progID, out Guid clsid);
        [DllImport("oleaut32.dll", PreserveSig=false)]
        private static extern void GetActiveObject(ref Guid clsid, IntPtr reserved,
            [MarshalAs(UnmanagedType.IUnknown)] out object result);
        public static object Attach(string progID) {
            Guid clsid;
            CLSIDFromProgID(progID, out clsid);
            object result;
            GetActiveObject(ref clsid, IntPtr.Zero, out result);
            return result;
        }
    }
}
'@
}
try {
    $photoshop = [LerPhotoshop.NativeBridge]::Attach($ProgId)
} catch {
    throw "Cannot attach to a running $ProgId. No fallback or application launch attempted. $($_.Exception.Message)"
}
try {
    $version = [string]$photoshop.Version
    if ([int]($version.Split('.')[0]) -ne $ExpectedMajorVersion) {
        throw "Version mismatch: expected major $ExpectedMajorVersion, got $version. No task JSX executed."
    }
    $probeParts = ([string]$photoshop.DoJavaScript('app.path.fsName + "|" + app.documents.length;')).Split('|')
    $applicationPath = $probeParts[0]
    if ($ExpectedApplicationPath -and
        -not [string]::Equals($applicationPath.TrimEnd('\', '/'),
            $ExpectedApplicationPath.TrimEnd('\', '/'), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Application path mismatch: $applicationPath. No task JSX executed."
    }
    if ($PSCmdlet.ParameterSetName -eq 'Execute') {
        $result = [string]$photoshop.DoJavaScript($scriptText)
    } else {
        $result = [PSCustomObject]@{
            transport = 'Windows COM + JSX'
            progId = $ProgId
            version = $version
            applicationPath = $applicationPath
            documentCount = [int]$probeParts[1]
            attachedToExistingProcess = $true
            taskScriptExecuted = $false
        } | ConvertTo-Json
    }
    if ($resultAbsolute) {
        $bytes = (New-Object System.Text.UTF8Encoding($false)).GetBytes($result)
        $stream = [System.IO.File]::Open($resultAbsolute, [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
    }
    Write-Output $result
} finally {
    if ($null -ne $photoshop -and [System.Runtime.InteropServices.Marshal]::IsComObject($photoshop)) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($photoshop)
    }
}
