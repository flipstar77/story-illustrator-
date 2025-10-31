; AutoHotkey Script - Auto-typer for browser (AFK-Safe)
; Press Ctrl+Alt+S to START the script
; Press Ctrl+Alt+X to STOP the script
; Press Ctrl+Alt+Q to QUIT the script completely
;
; INSTRUCTIONS:
; 1. Run this script (double-click the .ahk file)
; 2. Click in your browser's input field where you want to type
; 3. Press Ctrl+Alt+S to start
; 4. Go AFK - the script will keep running in the background
; 5. Press Ctrl+Alt+X when you return to stop

#Persistent
#NoEnv
SetWorkingDir %A_ScriptDir%
SetTimer, TypeCommand, Off
isRunning := false

; ===== CONFIGURATION (Edit these) =====
global intervalMs := 5000       ; Milliseconds between commands (5000 = 5 seconds)
global command := "go on"       ; The command to type
global typingDelay := 50        ; Delay between keypresses (ms) - makes it more natural
global useClipboard := false    ; Set to true for faster typing (pastes instead of typing)
; =====================================

; Start script with Ctrl+Alt+S
^!s::
    if (!isRunning) {
        isRunning := true
        SetTimer, TypeCommand, %intervalMs%
        TrayTip, Auto-typer Started, Typing "%command%" every %intervalMs%ms`nPress Ctrl+Alt+X to stop, 5, 1
        SoundBeep, 750, 100
    } else {
        TrayTip, Already Running, Auto-typer is already active!, 2, 2
    }
return

; Stop script with Ctrl+Alt+X
^!x::
    if (isRunning) {
        isRunning := false
        SetTimer, TypeCommand, Off
        TrayTip, Auto-typer Stopped, Script has been stopped`nPress Ctrl+Alt+S to restart, 3, 1
        SoundBeep, 500, 100
    } else {
        TrayTip, Not Running, Auto-typer is not active!, 2, 2
    }
return

; The typing function
TypeCommand:
    if (useClipboard) {
        ; Faster method: use clipboard paste
        ClipboardBackup := ClipboardAll
        Clipboard := command
        ClipWait, 1
        Send, ^v
        Sleep, 200
        Send, {Enter}
        Clipboard := ClipboardBackup
    } else {
        ; Natural typing method
        SetKeyDelay, %typingDelay%, %typingDelay%
        SendInput, %command%
        Sleep, 200
        Send, {Enter}
    }
return

; Exit script with Ctrl+Alt+Q
^!q::
    TrayTip, Exiting, Auto-typer script is closing..., 2
    Sleep, 500
    ExitApp
return

; Show status with Ctrl+Alt+I (Info)
^!i::
    if (isRunning) {
        status := "RUNNING"
    } else {
        status := "STOPPED"
    }
    TrayTip, Auto-typer Status, Status: %status%`nCommand: "%command%"`nInterval: %intervalMs%ms`n`nCtrl+Alt+S = Start`nCtrl+Alt+X = Stop`nCtrl+Alt+Q = Quit, 10, 1
return
