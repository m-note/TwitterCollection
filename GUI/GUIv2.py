# 全体的に参考にした: http://www.python-izm.com/contents/gui/layout_concept.shtml
import wx
#from get_Tweet import * # getTweets()のインポート
import GUI_action
import os


#--------------------------------------
#    フレームを継承した
#    トップレベルウィンドウクラス
#--------------------------------------
class CalcFrame(wx.Frame):

    def __init__(self):

        frame = wx.Frame.__init__(self, None, wx.ID_ANY, "Tweet Collector", size=(370,336))

        #    ステータスバーの初期化
        self.CreateStatusBar()
        self.SetStatusText("Tweet Collector Ver 0.0.1")
        self.GetStatusBar().SetBackgroundColour(None)

        #    メニューバーの初期化
        #self.SetMenuBar(CalcMenu())

        #    本体部分の構築
        root_panel = wx.Panel(self, wx.ID_ANY)

        file_open       = FileOpen(root_panel, self) # ファイルオープンでのアクションのためにselfを渡した
                                # 例えば、statusbarのテキストを変えたい場合は、
                                # frameにあるものを弄るので、selfを渡している。
        set_date = SetDate(root_panel)
        file_save = FileSave(root_panel, self)
        save_type = SaveType(root_panel)
        over_write = OverWrite(root_panel)
        executionbutton_panel = ExecutionButtonPanel(root_panel, self, file_open, file_save, set_date, save_type, over_write)


        # 配置していく
        root_layout = wx.BoxSizer(wx.VERTICAL)
        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "Users List:"), 0,  wx.GROW, border=7)
        root_layout.Add(file_open, 0, wx.GROW | wx.LEFT | wx.RIGHT, border=10)

        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "Set Date:"), 0, wx.GROW, border=7)
        root_layout.Add(set_date, 0, wx.GROW | wx.ALL, border=10)

        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "Save Folder:"), 0, wx.GROW, border=7)
        root_layout.Add(file_save, 0, wx.GROW | wx.ALL, border=10)
        root_layout.Add(save_type, 0, wx.GROW | wx.ALL, border=5)
        root_layout.Add(over_write, 0, wx.GROW | wx.ALL, border=5)

        root_layout.Add(executionbutton_panel, 0, flag=wx.ALIGN_CENTER, border=20)


        root_panel.SetSizer(root_layout)
        root_layout.Fit(root_panel)


#--------------------------------------
#          ファイルを開く
#--------------------------------------
class FileOpen(wx.Panel):

    def __init__(self, parent, parent_frame):
        self.parent_frame = parent_frame # 下のイベントで使うために代入している

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.file_pass = file_pass = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_LEFT, size=(320,20)) # self.に入れておかないと、イベントの設定で使えなかった
        self.button_open = button_open = wx.Button(self, 1000, "...")

        self.Bind(wx.EVT_BUTTON, self.click_button, button_open)

        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(file_pass, flag=wx.GROW)
        layout.Add(button_open, flag=wx.GROW)

        self.SetSizer(layout)

    # イベントの設定
    def click_button(self, event):
        if event.GetId() == 1000:
            GUI_action.fileopen_ACTION(self, event, self.parent_frame)


#--------------------------------------
#         　　日付の設定
#--------------------------------------
class SetDate(wx.Panel):

    def __init__(self,parent):

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.begin_year = begin_year = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_RIGHT, size=(40,20))
        self.begin_month = begin_month = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_RIGHT, size=(20,20))
        self.begin_day = begin_day = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_RIGHT, size=(20,20))
        self.end_year = end_year = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_RIGHT, size=(40,20))
        self.end_month = end_month = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_RIGHT, size=(20,20))
        self.end_day = end_day = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_RIGHT, size=(20,20))


        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(begin_year, flag=wx.GROW)
        layout.Add(wx.StaticText(self, wx.ID_ANY, " / "), flag=wx.GROW)
        layout.Add(begin_month, flag=wx.GROW)
        layout.Add(wx.StaticText(self, wx.ID_ANY, " / "), flag=wx.GROW)
        layout.Add(begin_day, flag=wx.GROW)

        layout.Add(wx.StaticText(self, wx.ID_ANY, "  ~  "), flag=wx.GROW)

        layout.Add(end_year, flag=wx.GROW)
        layout.Add(wx.StaticText(self, wx.ID_ANY, " / "), flag=wx.GROW)
        layout.Add(end_month, flag=wx.GROW)
        layout.Add(wx.StaticText(self, wx.ID_ANY, " / "), flag=wx.GROW)
        layout.Add(end_day, flag=wx.GROW)

        self.SetSizer(layout)

#--------------------------------------
#    　　　　　　保存先
#--------------------------------------
class FileSave(wx.Panel):

    def __init__(self, parent, parent_frame): # parentというのは、root_panelだったもの
        self.parent_frame = parent_frame # 下のイベントで使うために代入している
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.file_pass = file_pass = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_LEFT, size=(320,20))
        self.button_save = button_save = wx.Button(self, 1000, "...")

        self.Bind(wx.EVT_BUTTON, self.click_button, button_save)

        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(file_pass, flag=wx.GROW)
        layout.Add(button_save, flag=wx.GROW)


        self.SetSizer(layout)

    # イベントの設定
    def click_button(self, event):
        if event.GetId() == 1000:
            GUI_action.filesave_ACTION(self, event, self.parent_frame)

#--------------------------------------
#    　　　　　　保存形式
#--------------------------------------
class SaveType(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        button_array = ("csv (UTF-8)", "csv (Shift-JIS)", "pickel")
        self.radio_box = radio_box = wx.RadioBox(self, wx.ID_ANY, "File Type", choices=button_array, style=wx.RA_HORIZONTAL)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(radio_box)

        self.SetSizer(layout)


#--------------------------------------
#   　　　　 重複の確認
#--------------------------------------
class OverWrite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        button_array = ("No", "Yes") # Noなら既にダウンロードしたものはスキップ
        self.radio_box = radio_box = wx.RadioBox(self, wx.ID_ANY, "Overwrite", choices=button_array, style=wx.RA_HORIZONTAL)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(radio_box)

        self.SetSizer(layout)


#--------------------------------------
#   　　　　 実行ボタン部分
#--------------------------------------
class ExecutionButtonPanel(wx.Panel):

    def __init__(self, parent, parent_frame,
                 file_open, file_save, set_date, save_type, over_write): # parentというのは、root_panelだったもの
        self.parent_frame = parent_frame # 下のイベントで使うために代入している
        self.file_open = file_open; self.file_save = file_save
        self.set_date = set_date; self.save_type = save_type; self.over_write = over_write

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.button_collect = button_collect = wx.Button(self, 1000, "Collect!")

        self.Bind(wx.EVT_BUTTON, self.click_button, button_collect)

        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(button_collect,  border=20)

        self.SetSizer(layout)

    # イベントの設定
    def click_button(self, event):
        if event.GetId() == 1000:
            user_list_pass = self.file_open.file_pass.GetValue()
            file_save_pass = self.file_save.file_pass.GetValue()
            GUI_action.execute(self, event, self.parent_frame, user_list_pass, file_save_pass,
                               begin_year = self.set_date.begin_year.GetValue(),
                               begin_month = self.set_date.begin_month.GetValue(),
                               begin_day = self.set_date.begin_day.GetValue(),
                               end_year = self.set_date.end_year.GetValue(),
                               end_month = self.set_date.end_month.GetValue(),
                               end_day = self.set_date.end_day.GetValue(),
                               save_type = self.save_type.radio_box.GetStringSelection(),
                               over_write = self.over_write.radio_box.GetStringSelection(),
                               button_collect = self.button_collect)

#--------------------------------------
#    カスタムフレームを初期化して
#    アプリケーションを開始
#--------------------------------------
# class MyApp(wx.App):
#     def OnInit(self):
#         frame = CalcFrame()
#         frame.Show(True)
#         self.SetTopWindow(frame)
#         return True
#
# if __name__ == "__main__":
#     app = MyApp(0)
#     app.MainLoop()


if __name__ == "__main__":

    application = wx.App()
    frame = CalcFrame()
    frame.Show()
    application.MainLoop()