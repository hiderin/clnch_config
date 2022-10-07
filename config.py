import os
import sys
from clnch import *

################################################################################
# 追加したい機能のメモ
#-------------------------------------------------------------------------------
# ・時計の表示機能を使用してkeyhacのモードを表示させる              [showmode]
################################################################################

############################################################################
# 非アクティブ時の時計を利用したmode表示
############################################################################
# --------------------------------------------------------------------
# Vim_Flags
# --------------------------------------------------------------------

# メインのモードフラグ
# 0:ノーマルモード (通常のキーボード)
# 1:VimMode (Vimのノーマルモード)
# 2:InsertMode (Vimの挿入モード)
# 3:VisualMode (Vimのビジュアルモード)
# 4:CommandMode (Vimのコマンドモード)
# 5:SearchMode (検索モード EnterでVimModeに戻る)
mainmode = "1"

# VimMode でのコマンド入力中を示すフラグ
flg_mtd = 0

# コマンドの実行回数
repeatN = 0

# コマンドラインのコマンド
command_str =""

# ビジュアルモードの状態を示すフラグ
# 1:行単位の選択
# 2:矩形単位の選択
flg_selmode = 0

# スクロールバインドのオンオフ
flg_scroll = 0

# 日本語入力固定モード
flg_imemode ="1"

# EXCELLなどで日本語入力を固定する
flg_fixinput=0

# キーボードマクロの記録の状態を示すフラグ
    # 0:マクロ OFF
    # 1:マクロ記録中
    # 2:マクロ実行中
flg_mcr = "0"

# 設定処理
def configure(window):

    # --------------------------------------------------------------------
    # F1 キーでヘルプファイルを起動する
    def command_Help():
        print u"Helpを起動 :"
        help_path = os.path.join( getAppExePath(), 'doc\\index.html' )
        shellExecute( None, None, help_path, u"", u"" )
        print u"Done.\n"

    window.cmd_keymap[ "F1" ] = command_Help

    # --------------------------------------------------------------------
    # Ctrl-E で、入力中のファイルパスを編集する
    window.cmd_keymap[ "C-E" ] = window.command_Edit

    # --------------------------------------------------------------------
    # Alt-Space で、自動補完を一時的にOn/Offする
    window.keymap[ "A-Space" ] = window.command_AutoCompleteToggle

    # --------------------------------------------------------------------
    # テキストエディタを設定する
    if 0:
        window.editor = u"..\\LREdit\\LREdit.exe"
    # 呼び出し可能オブジェクトを設定 (高度な使用方法)
    if 1:
        def editor(path):
            shellExecute( None,None, u"..\\portvim\\gvim.exe", '--remote-silent "%s"'% path, "" )
        window.editor = editor

    # --------------------------------------------------------------------
    # ファイルタイプごとの動作設定
    window.association_list += [
        ( "*.mpg *.mpeg *.avi *.wmv", window.command_ShellExecute( None, u"wmplayer.exe", "/prefetch:7 /Play %param%", u"" ) ),
    ]

    # --------------------------------------------------------------------
    # 非アクティブ時の時計の形式
    if 1:
        # 年と秒を省略した短い形式
        window.clock_format = u"%m/%d(%a) %H:%M"
        #window.clock_format = u"%m/%d(%a) %H:%M"
    else:
        # 年月日(曜日) 時分秒 の全てを表示する
        window.clock_format = u"%Y/%m/%d(%a) %H:%M:%S"


    #現在の状態を表わす関数
    def show_keyhac_mode():
        showstr = ""
        global mainmode, flg_imemode

        #メインモードの表示
        if mainmode == "0":
            showstr = u"Nomal Mode  "
        elif mainmode == "1":
            showstr = u"VIM Mode    "
        elif mainmode == "2":
            showstr = u"Insert Mode "
        elif mainmode == "3":
            showstr = u"Visual Mode "
        elif mainmode == "4":
            showstr = u":" + command_str
        elif mainmode == "5":
            showstr = u"Search Mode "

        #日本語入力の表示
        if flg_imemode == "1":
            showstr = showstr + u"   JPN"
        else:
            showstr = showstr + u"   ENG"

        #マクロの状態の表示
        if flg_mcr == "1":
            showstr = showstr + u"   REC"
        else:
            showstr = showstr + u"      "

        window.clock_format = showstr

    def command_set_mode(mode_num):
        global mainmode
        mainmode = mode_num[0]
        show_keyhac_mode()

    def command_set_ime(mode_num):
        global flg_imemode
        flg_imemode = mode_num[0]
        show_keyhac_mode()

    def command_inp_cmd(mode_str):
        global command_str,mainmode
        mainmode = "4"
        command_str = mode_str[0]
        show_keyhac_mode()

    def command_set_mcr(mode_num):
        global flg_mcr
        flg_mcr = mode_num[0]
        show_keyhac_mode()

    # --------------------------------------------------------------------
    # 空欄コマンド
    #   コマンド名なしでEnterを押したときに実行されるコマンドです。
    #   この例では、ほかのアプリケーションをフォアグラウンド化するために使います。
    def command_QuickActivate( args, mod ):

        def callback( wnd, arg ):
            process_name, class_name = arg[0], arg[1]
            if (process_name==None or wnd.getProcessName()==process_name) and (class_name==None or wnd.getClassName()==class_name):
                wnd = wnd.getLastActivePopup()
                wnd.setForeground(True)
                return False
            return True

        if mod==MODKEY_SHIFT:
            pyauto.Window.enum( callback, ["C:\Dropbox\MySys\afxw32_157\AFXW.EXE",None] )
        elif mod==MODKEY_CTRL:
            pyauto.Window.enum( callback, ["notepad.exe","Notepad"] )
        elif mod==MODKEY_SHIFT|MODKEY_CTRL:
            pyauto.Window.enum( callback, ["mintty.exe","MinTTY"] )

    window.launcher.command_list += [ ( u"", command_QuickActivate ) ]

    # --------------------------------------------------------------------
    # "NetDrive" コマンド
    #   ネットワークドライブを割り当てるか解除を行います。
    #    NetDrive;L;\\server\share : \\machine\public を Lドライブに割り当てます
    #    NetDrive;L                : Lドライブの割り当てを解除します
    def command_NetDrive(args):
        
        if len(args)>=1:
            drive_letter = args[0]
            if len(args)>=2:
                path = args[1]
                checkNetConnection(path)
                if window.subProcessCall( [ "net", "use", drive_letter+":", os.path.normpath(path), "/yes" ], cwd=None, env=None, enable_cancel=False )==0:
                    print u"%s に %sドライブを割り当てました。" % ( path, drive_letter )
            else:
                if window.subProcessCall( [ "net", "use", drive_letter+":", "/D" ], cwd=None, env=None, enable_cancel=False )==0:
                    print u"%sドライブの割り当てを解除しました。" % ( drive_letter )
        else:
            print u"ドライブの割り当て : NetDrive;<ドライブ名>;<パス>"
            print u"ドライブの解除     : NetDrive;<ドライブ名>"

    def command_cmd(args):
        if len(args)==1:
            shellExecute( None, None, u"cmd.exe","/c", args[0])
        else:
            shellExecute( None, None, u"cmd.exe", u"", u"" )

#    def command_vim(args):
#        if len(args)==1:
#            shellExecute( None, None, u"..\\portvim\\vim73\\gvim.exe", '--remote-silent ',args[0])
#        else:
#            shellExecute( None, None, u"..\\portvim\\vim73\\gvim.exe", '--remote-silent ', u"" )
#
#    def command_vimfiler(args):
#        if len(args)==1:
#            shellExecute( None, None, u"..\\portvim\\vim73\\gvim.exe", '--remote-silent ','-c ":VimFilerDouble %s"' % args[0])
#        else:
#            shellExecute( None, None, u"..\\portvim\\vim73\\gvim.exe", '--remote-silent ', '-c ":VimFilerDouble"' )

    # --------------------------------------------------------------------
    # コマンドを登録する
    window.launcher.command_list += [
#        ( u"Vim",    command_vim),
#        ( u"cmd",    window.command_ShellExecute( None, u"cmd.exe", u"%param%", u"" ) ),
        ( u"NetDrive",  command_NetDrive ),
        ( u"cmd",    command_cmd),
        ( u"Vim",    window.command_ShellExecute( None, u"..\\portvim\\gvim.exe", u"", u"" ) ),
        ( u"xammp",    window.command_ShellExecute( None, u"C:\\xampp\\xampp-control.exe", u"", u"" ) ),
        ( u"Vix",    window.command_ShellExecute( None, u"..\\programfiles\\vix221\\ViX.exe", u"", u"" ) ),
        ( u"dentaku", window.command_ShellExecute( None, u"..\\programfiles\\Mdentaku\\Mdentaku.exe", u"", u"" ) ),
        ( u"regedit",    window.command_ShellExecute( None, u"regedit.exe", u"", u"" ) ),
        ( u"Mail",     window.command_ShellExecute( None, u"..\\..\\PASSフォルダ\\ThunderbirdPortable\\ThunderbirdPortable.exe", u"", u"" ) ),
        ( u"ReduceMemory",     window.command_ShellExecute( None, u"..\\programfiles\\ReduceMemory\\ReduceMemory.exe", u"", u"" ) ),
        ( u"ReduceMemory64",     window.command_ShellExecute( None, u"..\\programfiles\\ReduceMemory\\ReduceMemory_x64.exe", u"", u"" ) ),
        ( u"AvidemuxPortable",     window.command_ShellExecute( None, u"..\\programfiles\\AvidemuxPortable\\AvidemuxPortable.exe", u"", u"" ) ),
        ( u"GimpPortable",     window.command_ShellExecute( None, u"..\\programfiles\\GimpPortable\\GIMPPortable.exe", u"", u"" ) ),
        ( u"InkscapePortable",     window.command_ShellExecute( None, u"..\\programfiles\\InkscapePortable\\InkscapePortable.exe", u"", u"" ) ),
        ( u"Yoyaku",   window.command_ShellExecute( None, u"C:\\Program Files\\Microsoft Office 15\\root\\office15\\EXCEL.EXE", u"\\\\htlsrv\\みんなの共有フォルダー\\★予約★\\橋本\\予約料金計算(yoyaku).xlsx", u"" ) ),
        ( u"ID_ListFile",   window.command_ShellExecute( None, u"C:\\Program Files\\Microsoft Office 15\\root\\office15\\EXCEL.EXE", u"\\\\Htlsrv\\みんなの共有フォルダー\\★予約★\\インターネット管理画面（ID).xlsx", u"" ) ),
        ( u"taion",    window.command_ShellExecute( None, u"C:\\Program Files\\Microsoft Office 15\\root\\office15\\EXCEL.EXE", u"Z:\\★予約★\\体温検温表\\N.橋本■■体温記録表.xlsx", u"" ) ),
#"
        ( u"Google",    window.command_URL( u"http://www.google.com/search?ie=utf8&q=%param%", encoding=u"utf8" ) ),
        ( u"teratail",    window.command_URL( u"https://teratail.com/", encoding=u"utf8" ) ),
        ( u"firestorage",    window.command_URL( u"http://firestorage.jp/", encoding=u"utf8" ) ),
        ( u"DataDeliver",    window.command_URL( u"https://datadeliver.net/login", encoding=u"utf8" ) ),
        ( u"DropBox",    window.command_URL( u"https://www.dropbox.com/ja/", encoding=u"utf8" ) ),
        ( u"GitHub",    window.command_URL( u"https://github.com/hiderin/", encoding=u"utf8" ) ),
        ( u"TL-lincoln",    window.command_URL( u"https://www.tl-lincoln.net/accomodation/Ascsc1000InitAction.do", encoding=u"utf8" ) ),
        ( u"Kanxashi",    window.command_URL( u"http://member.kanxashi.com/", encoding=u"utf8" ) ),
        ( u"Kuchikomi",    window.command_URL( u"https://member.cuticomi.com/", encoding=u"utf8" ) ),
        ( u"Gmail",    window.command_URL( u"https://mail.google.com/mail/", encoding=u"utf8" ) ),
        ( u"DataDeliver",    window.command_URL( u"https://www.datadeliver.net/", encoding=u"utf8" ) ),
        ( u"bitbucket",    window.command_URL( u"https://bitbucket.org/hiderin215", encoding=u"utf8" ) ),
        ( u"Eijiro",    window.command_URL( u"http://eow.alc.co.jp/%param%/UTF-8/", encoding=u"utf8" ) ),
        #keyhac用コマンド
        ( u"setmod",    command_set_mode),
        ( u"setime",    command_set_ime),
        ( u"inpcmd",    command_inp_cmd),
        ( u"setmcr",    command_set_mcr),
    ]
    # --------------------------------------------------------------------
    # スタートメニューの中のショートカットをコマンドとして登録する
    if 1:
        startmenu_items = []

        MAX_PATH = 260
        CSIDL_PROGRAMS = 2
        CSIDL_COMMON_PROGRAMS = 23

        buf = ctypes.create_unicode_buffer(MAX_PATH)

        ctypes.windll.shell32.SHGetSpecialFolderPathW( None, buf, CSIDL_PROGRAMS, 0 )
        programs_dir = buf.value

        ctypes.windll.shell32.SHGetSpecialFolderPathW( None, buf, CSIDL_COMMON_PROGRAMS, 0 )
        common_programs_dir = buf.value
        
        startmenu_dirs = [
            programs_dir,
            common_programs_dir
        ]
        
        for startmenu_dir in startmenu_dirs:
            for location, dirs, files in os.walk( startmenu_dir ):
                for filename in files:
                    if not filename.lower().endswith(".lnk"):
                        continue
                    name, ext = os.path.splitext(filename)    
                    item = ( name, window.command_ShellExecute( None, os.path.join(location,filename), u"", u"" ) )
                    startmenu_items.append(item)
                    
        startmenu_items.sort()
        
        window.launcher.command_list += startmenu_items

# リストウインドウの設定処理
def configure_ListWindow(window):

    # --------------------------------------------------------------------
    # F1 キーでヘルプファイルを表示する

    def command_Help():
        print u"Helpを起動 :"
        help_path = os.path.join( getAppExePath(), 'doc\\index.html' )
        shellExecute( None, None, help_path, u"", u"" )
        print u"Done.\n"

    window.keymap[ "F1" ] = command_Help

