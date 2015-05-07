import os
import sys
from clnch import *

################################################################################
# 追加したい機能のメモ
#-------------------------------------------------------------------------------
# ・時計の表示機能を使用してkeyhacのモードを表示させる              [showmode]
################################################################################

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
        ( u"NetDrive",  command_NetDrive ),
        ( u"Vim",    window.command_ShellExecute( None, u"..\\portvim\\gvim.exe", u"", u"" ) ),
#        ( u"Vim",    command_vim),
#        ( u"cmd",    window.command_ShellExecute( None, u"cmd.exe", u"%param%", u"" ) ),
        ( u"cmd",    command_cmd),
        ( u"regedit",    window.command_ShellExecute( None, u"regedit.exe", u"", u"" ) ),
        ( u"Peggy",     window.command_ShellExecute( None, u"C:/ols/anchor/peggy/peggypro.exe", u"", u"" ) ),
        ( u"Becky",     window.command_ShellExecute( None, u"C:/ols/becky/B2.exe", u"", u"" ) ),
        ( u"FireFox",   window.command_ShellExecute( None, u"C:/Program Files/Mozilla Firefox/firefox.exe", u"", u"C:/Program Files/Mozilla Firefox" ) ),
        ( u"Google",    window.command_URL( u"http://www.google.com/search?ie=utf8&q=%param%", encoding=u"utf8" ) ),
        ( u"firestorage",    window.command_URL( u"http://firestorage.jp/", encoding=u"utf8" ) ),
        ( u"DropBox",    window.command_URL( u"https://www.dropbox.com/ja/", encoding=u"utf8" ) ),
        ( u"GitHub",    window.command_URL( u"https://github.com/hiderin/", encoding=u"utf8" ) ),
        ( u"Eijiro",    window.command_URL( u"http://eow.alc.co.jp/%param%/UTF-8/", encoding=u"utf8" ) ),
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

