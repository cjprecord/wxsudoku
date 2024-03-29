;------------------------------------------------------------------------------
; wxSudoku Windows Installer Build Script
; Author: Cody Precord
; Language: NSIS
; Licence: wxWindows License
;------------------------------------------------------------------------------


;------------------------------ Start MUI Setup -------------------------------

; Global Variables
!define PRODUCT_NAME "wxSudoku"
!define PRODUCT_VERSION "0.1"
!define PRODUCT_PUBLISHER "Cody Precord"
!define PRODUCT_WEB_SITE "http://wxsudoku.googlecode.com"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "pixmaps\Sudoku.ico"
!define MUI_UNICON "pixmaps\Sudoku.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page (Read the Licence)
!insertmacro MUI_PAGE_LICENSE "COPYING"

; Components Page (Select what parts to install)
!insertmacro MUI_PAGE_COMPONENTS

; Directory page (Set Where to Install)
!insertmacro MUI_PAGE_DIRECTORY

; Instfiles page (Do the installation)
!insertmacro MUI_PAGE_INSTFILES

; Finish page (Post installation tasks)
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Run wxSudoku"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchSudoku"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

;------------------------------- End MUI Setup --------------------------------

 
;------------------------------ Start Installer -------------------------------

;---- Constants
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "wxsudoku.win32.${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\wxSudoku"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

;---- !defines for use with SHChangeNotify
!ifdef SHCNE_ASSOCCHANGED
!undef SHCNE_ASSOCCHANGED
!endif
!define SHCNE_ASSOCCHANGED 0x08000000

!ifdef SHCNF_FLUSH
!undef SHCNF_FLUSH
!endif
!define SHCNF_FLUSH        0x1000

; Prepare for installation
Function .onInit
  ; prevent running multiple instances of the installer
  System::Call 'kernel32::CreateMutexA(i 0, i 0, t "sudoku_installer") i .r1 ?e'
  Pop $R0
  StrCmp $R0 0 +3
    MessageBox MB_OK|MB_ICONEXCLAMATION "The installer is already running."
    Abort

  ; Check for existing installation warn before installing new one
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  StrCmp $R0 "" done

  MessageBox MB_YESNO|MB_ICONEXCLAMATION \
  "An existing installation of wxSudoku has been found. $\nDo you want to remove the previous version before installing $(^Name) ?" \
  IDNO done

  ; Run the uninstaller
  ClearErrors
  ExecWait '$R0 _?=$INSTDIR' ; Do not copy the uninstaller to a temp file

  done:
FunctionEnd

; Extract the files from the installer to the install location
Section "wxSudoku" SEC01
  SectionIn RO 1 2

  ; Check that Editra is not running before starting to copy the files
  FindProcDLL::FindProc "${PRODUCT_NAME}.exe"
  StrCmp $R0 0 continueInstall
    MessageBox MB_ICONSTOP|MB_OK "${PRODUCT_NAME} is still running please close all running instances and try to install again"
    Abort
  continueInstall:

  ; Extract the files and make shortcuts
  SetOverwrite try
  SetOutPath "$INSTDIR\"
  File /r ".\*.*"

  ; Add the shortcuts to the start menu and desktop
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}.exe"
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}.exe"
SectionEnd

; Add QuickLaunch Icon (That small icon bar next to the start button)
Section "Add Quick Launch Icon" SEC03
  SectionIn 1
  CreateShortCut "$QUICKLAUNCH\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}.exe"
SectionEnd

; Make/Install Shortcut links
Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

; Post installation setup
Section -Post
  ;---- Write registry keys for uninstaller
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Editra.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_NAME}.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Called if Run wxSudoku is checked on the last page of installer
Function LaunchSudoku
  Exec '"$INSTDIR\${PRODUCT_NAME}.exe" "$INSTDIR\CHANGELOG" '
FunctionEnd

; Description Texts for Component page
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Required core program files"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Add shortcut to Quick Launch Bar"
!insertmacro MUI_FUNCTION_DESCRIPTION_END
;------------------------------- End Installer --------------------------------


;----------------------------- Start Uninstaller ------------------------------

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  ; Remove all Files
  RmDir /r "$INSTDIR\"

  ; Remove all shortcuts
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$QUICKLAUNCH\${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"

  ; Cleanup Registry
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  SetAutoClose true
SectionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

;------------------------------ End Uninstaller -------------------------------
