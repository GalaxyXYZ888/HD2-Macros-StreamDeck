#Requires AutoHotkey v2.0
#SingleInstance Force

; This tells Windows to treat the 'Navigation' signals as 'Number' signals
; even if Shift is being held down.
; This prevents the "Shift-Up" stutter in games.

*NumpadUp::Numpad8
*NumpadDown::Numpad2
*NumpadLeft::Numpad4
*NumpadRight::Numpad6
*NumpadHome::Numpad7
*NumpadPgUp::Numpad9
*NumpadEnd::Numpad1
*NumpadPgDn::Numpad3
*NumpadIns::Numpad0
*NumpadClear::Numpad5
*NumpadDot::NumpadDot