;Based on :
;Welcome/Finish Page Example Script
;Written by Joost Verburg
;
; NOTE: this script only wraps an already-frozen Windows build found in
;_win_bin. The payload must be produced with a Python 3 freezer
;(PyInstaller or equivalent).

;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  !define VERSION "3.0.0"

  Name "Métamorphose3"
  OutFile "metamorphose3_${VERSION}_setup.exe"
  !define MUI_ICON "metsetup.ico"
  !define MUI_UNICON "metsetup.ico"
  !define MUI_WELCOMEFINISHPAGE_BITMAP "wizard_i.bmp"
  !define MUI_UNWELCOMEFINISHPAGE_BITMAP "wizard_u.bmp"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKLM "Software\metamorphose3" ""

  ;Default installation folder
  InstallDir "$PROGRAMFILES\metamorphose3"

  VIProductVersion "3.0.0.0"
  VIAddVersionKey "ProductName" "Métamorphose3"
  VIAddVersionKey "CompanyName" "Ianaré Sévi"
  VIAddVersionKey "LegalCopyright" "(C) 2006-2015 Ianaré Sévi"
  VIAddVersionKey "FileDescription" "Installer for Métamorphose 3.${VERSION}"
  VIAddVersionKey "FileVersion" "${VERSION}"

  !define CSIDL_SYSTEM "0x25" ;System path

  XPStyle on
  SetCompressor /SOLID lzma
  
  ;Request application privileges for Windows Vista / 7
  RequestExecutionLevel admin
  
  ShowInstDetails show

;--------------------------------
;Variables

  Var MUI_TEMP
  Var STARTMENU_FOLDER

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING
  !define MUI_COMPONENTSPAGE_CHECKBITMAP "checks.bmp"

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "License.rtf"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  ;Start Menu Folder Page Configuration
  ;!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM"
  ;!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\metamorphose3"
  ;!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER

  !insertmacro MUI_PAGE_INSTFILES
  !define MUI_FINISHPAGE_RUN "$INSTDIR\metamorphose3.exe"
  !insertmacro MUI_PAGE_FINISH

  ;uninstall
  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_COMPONENTS
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

; win2000 needs GdiPlus.dll
Function win2000
  ReadRegStr $R0 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" CurrentVersion
  StrCmp $R0 "5.0" lbl_done

  lbl_done:

FunctionEnd

Section "Métamorphose3" Application

  SectionIn RO
  SetOutPath "$INSTDIR"

  File /r ..\..\..\_win_bin\*
  File ..\..\..\dll\gdiplus.dll
  File ..\..\..\dll\MSVCP71.DLL
  
  ;Install for all users
  SetShellVarContext all

  Call win2000

  ;Store installation folder
  WriteRegStr HKLM "Software\metamorphose3" "" $INSTDIR
  WriteRegStr HKLM "Software\metamorphose3" "version" ${VERSION}

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Métamorphose3.lnk" "$INSTDIR\metamorphose3.exe"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

Section "Right-click menu" Shell
  WriteRegStr HKCR "Directory\shell\Rename with Métamorphose3" "" ""
  WriteRegStr HKCR "Directory\shell\Rename with Métamorphose3\command" "" "$INSTDIR\metamorphose3.exe %L"
SectionEnd

Section "Desktop Shortcut" DShortCut
  CreateShortCut "$DESKTOP\Métamorphose3.lnk" "$INSTDIR\metamorphose3.exe"
SectionEnd

Section /o "Quicklaunch Shortcut" QShortCut
  CreateShortCut "$QUICKLAUNCH\Métamorphose3.lnk" "$INSTDIR\metamorphose3.exe"
SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_Application ${LANG_ENGLISH} "The main application files (required)."
  LangString DESC_Shell ${LANG_ENGLISH} "Add this right-click menu option: 'Rename with Métamorphose3'."
  LangString DESC_DShortCut ${LANG_ENGLISH} "Create a Desktop shortcut."
  LangString DESC_QShortCut ${LANG_ENGLISH} "Create a Quickstart shortcut."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${Application} $(DESC_Application)
    !insertmacro MUI_DESCRIPTION_TEXT ${Shell} $(DESC_Shell)
    !insertmacro MUI_DESCRIPTION_TEXT ${DShortCut} $(DESC_DShortCut)
    !insertmacro MUI_DESCRIPTION_TEXT ${QShortCut} $(DESC_QShortCut)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END


;--------------------------------
;Uninstaller Section

Section "un.Métamorphose" Uninstall

  SectionIn RO
  
  ;Uninstall for all users
  SetShellVarContext all

  Delete "$DESKTOP\Métamorphose3.lnk"
  Delete "$QUICKLAUNCH\Métamorphose3.lnk"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
  RMDir /r "$SMPROGRAMS\$MUI_TEMP"

  RMDir /r "$INSTDIR"

  ;DeleteRegKey HKCU "Software\metamorphose3"
  DeleteRegKey HKLM "Software\metamorphose3"
  DeleteRegKey HKCR "Directory\shell\Rename with Métamorphose3"
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\metamorphose3"

SectionEnd

Section /o "un.User files" UninstallUser
  
  ;remove config for current user
  SetShellVarContext current
  
  RMDir /r "$APPDATA\.metamorphose3"

SectionEnd

  ;Language strings
  LangString DESC_Uninstall ${LANG_ENGLISH} "The main application files (required)."
  LangString DESC_UninstallUser ${LANG_ENGLISH} "Current user's configuration and history files."

  ;Assign language strings to sections
  !insertmacro MUI_UNFUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${Uninstall} $(DESC_Uninstall)
    !insertmacro MUI_DESCRIPTION_TEXT ${UninstallUser} $(DESC_UninstallUser)
  !insertmacro MUI_UNFUNCTION_DESCRIPTION_END
