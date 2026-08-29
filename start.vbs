Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = folder
pythonw = folder & "\.venv\Scripts\pythonw.exe"
app = folder & "\app.py"
If Not fso.FileExists(pythonw) Then
  MsgBox "Missing: " & pythonw, 16, "Two Agent Lab"
  WScript.Quit 1
End If
sh.Run """" & pythonw & """ """ & app & """", 0, False
