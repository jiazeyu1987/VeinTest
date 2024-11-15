Unicode true

RequestExecutionLevel admin

!define PRODUCT_NAME "PVaricesPlan" ;静脉软件
!define PRODUCT_VERSION_COMPLETE "0.0.0.0001"
!define PRODUCT_VERSION_RELASE "1"
!define PRODUCT_PUBLISHER "有限公司"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Launcher.exe"

SetCompressor lzma

!include "MUI2.nsh"
!include "WordFunc.nsh"
!include "FileFunc.nsh" ;包含计算文件大小的函数${GetSize}
!include "LogicLib.nsh"

!define MUI_ICON "..\icon.ico" ;这个会显示安装程序的图标F:\SurgeryBefore.ico
!define MUI_UNICON "..\icon.ico"

;欢迎页面
!insertmacro MUI_PAGE_WELCOME 
;许可协议页面
!insertmacro MUI_PAGE_LICENSE "license.txt"
;安装目录选择页面
;!define MUI_PAGE_CUSTOMFUNCTION_PRE dirLeave
!insertmacro MUI_PAGE_DIRECTORY
; 检测磁盘是否空间够
;PageEx directory
	;DirVerify leave
	;PageCallbacks "" "" dirLeave
;PageExEnd

;安装过程页面
!insertmacro MUI_PAGE_INSTFILES
;安装完成页面
;!define MUI_FINISHPAGE_RUN "$INSTDIR\YBest.Ads.exe" ; 完成后运行
!insertmacro MUI_PAGE_FINISH
;安装卸载过程页面
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE un.uninstallFinished
!insertmacro MUI_UNPAGE_INSTFILES
;安装界面包含的语言设置
!insertmacro MUI_LANGUAGE "SimpChinese" 

# 显示在安装文件或卸载文件属性页中
VIProductVersion "2.0.0.0"
VIAddVersionKey /LANG=2052 "ProductName" "静脉软件"
VIAddVersionKey /LANG=2052 "Comments" "软件版权归有限公司所有，他人不得复制或二次开发本程序。"
VIAddVersionKey /LANG=2052 "CompanyName" "有限公司"
VIAddVersionKey /LANG=2052 "LegalTrademarks" ""
VIAddVersionKey /LANG=2052 "LegalCopyright" "有限公司"
VIAddVersionKey /LANG=2052 "FileDescription" "静脉软件的安装包"
VIAddVersionKey /LANG=2052 "FileVersion" "2"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION_COMPLETE}"
OutFile "PVaricesPlan.exe"
InstallDir "$PROGRAMFILES\PVaricesPlan" ;默认安装目录
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show

BrandingText "静脉软件"
DirText "安装向导将把静脉软件安装在下列文件夹，如果要安装到其他文件夹请单击 [浏览(B)] 进行选择。"
Var KeepFolder1
Var KeepFolder2
Var InstallDir1
Var KeepFolder3
Section "MainSection" SEC01
	
	SetOutPath "$INSTDIR\PVaricesPlan"; 经过安装目录选择之后，$INSTDIR 目录会被重新赋值
	;SetOverwrite ifnewer
	File /r /x .git /x package "..\..\..\..\..\..\*"
	
	CreateDirectory "$SMPROGRAMS\PVaricesPlan"
	CreateShortCut "$SMPROGRAMS\PVaricesPlan\静脉软件.lnk" "$INSTDIR\PVaricesPlan\Launcher.exe" "" "$INSTDIR\GLPyModule\Project\PAAA\ProjectCache\PVaricesPlan\icon.ico"
	CreateShortCut "$DESKTOP\静脉软件.lnk" "$INSTDIR\PVaricesPlan\Launcher.exe" "" "$INSTDIR\PVaricesPlan\GLPyModule\Project\PAAA\ProjectCache\PVaricesPlan\icon.ico" ;这个应该写安装程序所在主机电脑上的路径
	CreateShortCut "$SMPROGRAMS\PVaricesPlan\卸载静脉软件.lnk" "$INSTDIR\uninstPVaricesPlan.exe"
	
	; 默认可以使用管理员权限运行程序，否则程序默认打开之后，会无法创建文件或文件夹
	; 针对当前用户有效
	WriteRegStr HKCU "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\PVaricesPlan\Launcher.exe" "RUNASADMIN"
	; 针对所有用户有效
	WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\PVaricesPlan\Launcher.exe" "RUNASADMIN"
	
SectionEnd

Section -Post
	; [Path\]exename.exe	; 将卸载程序写入指定的文件名(和可选路径)。仅在安装节或函数中有效，并要求在脚本中有一个卸载节。您可以多次调用此函数以写出卸载程序的一个或多个副本。
	WriteUninstaller "$INSTDIR\uninstPVaricesPlan.exe"
	WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Launcher.exe"
	WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "InstallPath" "$INSTDIR" ;$(^Name)
	WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "静脉软件" ;$(^Name)
	WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstPVaricesPlan.exe"
	WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\GLPyModule\Project\PAAA\ProjectCache\PVaricesPlan\icon.ico"
	WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION_COMPLETE}"
	;WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
	WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
	
  ; 自启动
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "PVaricesPlan" "$INSTDIR\PVaricesPlan\Launcher.exe"
	; 计算安装文件的大小
	${GetSize} "$INSTDIR\PVaricesPlan" "/S=OK" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"; 
	; root_key subkey key_name value
	WriteRegDWORD HKLM "${PRODUCT_DIR_REGKEY}" "Installed" 1
	WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "InstalledPath" "$INSTDIR"
	;写入完整版本号
	WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "version" "${PRODUCT_VERSION_COMPLETE}" 	
	WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "version_relase" "${PRODUCT_VERSION_RELASE}" ;写入发布版本号
	; 获取当前时间，并写入注册表
    !insertmacro GetTime
    ${GetTime} "" "L" $0 $1 $2 $3 $4 $5 $6
	; 用于在控制面板展示
    WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "InstallationDate" "$2/$1/$0 $4:$5:$6"
	; 用于程序获取
	WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "InstallationDate" "$2/$1/$0 $4:$5:$6" 
SectionEnd


Section ".mrb" mrb_file
	DetailPrint "关联 mrb文件"
	SectionIn 1
	DeleteRegKey HKCR ".mrb"
	DeleteRegKey HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.mrb"
	StrCpy $0 "$INSTDIR\PVaricesPlan\Launcher.exe"
	WriteRegStr HKCR ".mrb" "" "Mrb.file"
	WriteRegStr HKCR "Mrb.file" "" "mrb_file"
	WriteRegStr HKCR "Mrb.file\DefaultIcon" "" "$0,0"
	WriteRegStr HKCR "Mrb.file\shell" "" ""
	WriteRegStr HKCR "Mrb.file\shell\open" "" ""
	WriteRegStr HKCR "Mrb.file\shell\open\command" "" '"$0" "%1"'
SectionEnd


/******************************

* 以下是安装程序的卸载部分 *

******************************/
Section Uninstall
	MessageBox MB_OKCANCEL "是否要卸载静脉软件" \
    /SD IDOK IDOK label_ok IDCANCEL label_cancel	
	label_cancel:
		Quit
	label_ok:
		; 停止mysql服务 并移除服务
		;call un.removeService ; 循环删除文件直至删除文件夹
		Delete "$SMPROGRAMS\PVaricesPlan\卸载静脉软件.lnk"
		Delete "$DESKTOP\静脉软件.lnk"
		Delete "$SMPROGRAMS\PVaricesPlan\静脉软件.lnk"
		RMDir "$SMPROGRAMS\PVaricesPlan"
		
		DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
		DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
		DeleteRegKey HKCR ".mrb"
		DeleteRegKey HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.mrb"
		DeleteRegKey HKCR "Mrb.file"
		Delete "$INSTDIR\uninstPVaricesPlan.exe"
		
		; 定义要保留的文件夹
		StrCpy $KeepFolder1 "logs"
		StrCpy $KeepFolder2 "ScreenShot"
		StrCpy $KeepFolder3 "splittool"

		; 获取安装目录路径
		StrCpy $InstallDir1 "$INSTDIR\PVaricesPlan"

		; 查找并删除不需要的文件夹
		FindFirst $0 $1 $InstallDir1\*.*

		loop:
			StrCmp $1 "" done
			StrCmp $1 "." next
			StrCmp $1 ".." next		
			StrCmp $1 $KeepFolder1 next
			StrCmp $1 $KeepFolder2 next
			StrCmp $1 $KeepFolder3 next
			RMDir /r "$InstallDir1\$1"
			; 删除文件
			Delete "$InstallDir1\$1"
		next:
			FindNext $0 $1
			Goto loop

		done:
			FindClose $0
		
		; true|false	;覆盖默认的自动关闭窗口标志(使用AutoCloseWindow为安装程序指定，卸载程序为false)。指定'true'使安装窗口在安装完成后立即消失，或指定'false'使它需要手动关闭。	
		SetAutoClose false	
SectionEnd


; 检测磁盘是否空间够
Function dirLeave
	GetInstDirError $0
		${SWitch} $0
			${Case} 0
				;MessageBox MB_OK "valid installation directory"
				${Break}
			${Case} 1
				MessageBox MB_OK "invalid installation directory!"
				Abort
				${Break}
			${Case} 2
				MessageBox MB_OK "not enough free space!"
				Abort
				${Break}
		${EndSwitch}
FunctionEnd

Function .onInit
InitPluginsDir

;创建互斥防止重复运行
; System::Call kernel32::CreateMutexA i表示类型
System::Call 'kernel32::CreateMutexA(i 0, i 0, t "Launcher") i .r1 ?e'
Pop $R0

StrCmp $R0 0 +3
MessageBox MB_OK|MB_ICONEXCLAMATION "有一个静脉软件安装向导已经运行！"
Abort
;禁止多次安装实例 start
ReadRegDWORD $0 HKLM '${PRODUCT_DIR_REGKEY}' "Installed"
IntCmp $0 +1 +4 ; +1不能少+，不知道为什么，带冒号的跳转的程序段整体算一步，+4从当前步的下一步开始，1，2，3，4
MessageBox MB_YESNO "静脉软件已安装在计算机中。如需重新安装，请卸载已有的安装。" IDYES true IDNO false
	true:
		ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
		;MessageBox MB_OK "$R0"
		exec $R0
	false:
		; Does nothing.
		Nop
FunctionEnd

Function un.uninstallFinished
	MessageBox MB_OK '卸载完成'
FunctionEnd