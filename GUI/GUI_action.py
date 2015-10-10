import os
import wx
import get_Tweet  # getTweets()のインポート
import subprocess
import datetime # datetimeモジュールのインポート
import pandas as pd
import time
import random

def fileopen_ACTION(fileopen_frame, event, parent_frame):
#参考: http://plaza.rakuten.co.jp/kugutsushi/diary/201010090002/
    """ ファイルを開く """
    dirname = ''
    filters = 'csv files (*.csv)|*.csv'
    dlg = wx.FileDialog(fileopen_frame, "csvファイルを選択してください", dirname, "", filters, wx.FD_FILE_MUST_EXIST)

    if dlg.ShowModal() == wx.ID_OK:
        filename = dlg.GetFilename()
        dirname = dlg.GetDirectory()
        path = os.path.join(dirname, filename)
        fileopen_frame.file_pass.SetValue(path)

    dlg.Destroy()
    dirname = ''



def filesave_ACTION(filesave_frame, event, parent_frame):
    """ フォルダを開く """
    dirname = ''
    #filters = 'files (*.*)|*.*'
    dlg = wx.DirDialog(filesave_frame, "保存先ディレクトリを選択してください", "", wx.DIRP_DEFAULT_STYLE)

    if dlg.ShowModal() == wx.ID_OK:
        dirname = dlg.GetPath()
        filesave_frame.file_pass.SetValue(dirname)

    dlg.Destroy()
    dirname = ''


def execute(execute_frame, event, parent_frame, user_list_pass, file_save_pass, begin_year, begin_month, begin_day,
            end_year, end_month, end_day, save_type, over_write, button_collect):

    # Tweet取得開始時の処理
    button_collect.Disable() # 処理中はボタンを使えなくする
    parent_frame.SetStatusText("Getting Tweets:") #ステータスバーの表示を変える

    msg = user_list_pass + "\n" + file_save_pass + "\n" +\
                    begin_year + begin_month + begin_day +  "\n" + end_year+end_month+end_day+"\n"+save_type+"\n"+over_write
    dial = wx.MessageBox(msg, 'Info', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
    if dial == 16: #キャンセルが選択されたら処理しない
        parent_frame.SetStatusText("Collection Cancelled")
        button_collect.Enable()
        return 0

    # Tweetを取得する関数に渡す前に情報を整理する
    try:
        date_start = datetime.datetime.strptime(begin_year + "-" + begin_month + "-" + begin_day, '%Y-%m-%d')
        date_end = datetime.datetime.strptime(end_year + "-" + end_month + "-" + end_day, '%Y-%m-%d')
    except:
        wx.MessageBox("Date shoud be yyyy/mm/dd", 'Error', wx.OK | wx.ICON_ERROR)
        parent_frame.SetStatusText("Collection Cancelled")
        button_collect.Enable()
        return 0
    if value_check(date_start, parent_frame, button_collect) == False:
        return 0
    if value_check(date_end, parent_frame, button_collect) == False:
        return 0
    if user_list_pass == "" or file_save_pass == "":
        wx.MessageBox("Please select appropriate file / folder", 'Error', wx.OK | wx.ICON_ERROR)
        parent_frame.SetStatusText("Collection Cancelled")
        button_collect.Enable()
        return 0

    # ユーザーリストの取得
    user_list, user_pd = get_Tweet.getUserLists(user_list_pass)

    # Twilogから情報を取得する
    date_list = get_Tweet.makeDateList(date_start, date_end) # 日付のリストを作る


    user_num = 1
    all_user = len(user_list)
    for user in user_list:
        status = "Getting Tweets: " + user + "(" + str(user_num) + " out of " + str(all_user) + ")"
        parent_frame.SetStatusText(status) #ステータスバーの表示を変える

        # pandasの初期化
        results_df = pd.DataFrame()

        for date in date_list:
            # Twilogへのリクエスト用URLを作る
            request_url = "http://twilog.org/" + user + "/date-" + str(date.year)[2:] + date.strftime('%m%d')
            # 生データを入手して (タグとかが残っている)、整形する
            tweet_list, timestamp_list = get_Tweet.getTweets(request_url)
            tweet_list, rawlink_cleaned_list, tweet_type_list, tweet_time_list, quoted_list, replyto_list = get_Tweet.CleanTweets(tweet_list, timestamp_list, user)

            # pandasにまとめる
            results_df = results_df.append(pd.DataFrame({"ID": [user for i in range(len(tweet_list))],
                                                        "Date": [date.strftime('%Y-%m-%d') for i in range(len(tweet_list))],
                                                        "Time": tweet_time_list,
                                                        "Tweet": tweet_list,
                                                        "Type": tweet_type_list,
                                                        "URL": rawlink_cleaned_list,
                                                        "ReplyTo": replyto_list,
                                                        "Quoted": quoted_list},
                                                        columns = ['ID', 'Date', 'Time', 'Tweet', 'Type', "ReplyTo", "Quoted", "URL"]))

            time.sleep(random.uniform(0.9,1.8)) # 連続で取得しないように待機

        # pandasを保存する
        pandasSave(results_df.reset_index(drop=True), file_save_pass, save_type, user, date_start, date_end) # インデックス番号を振りなおした上で保存する

        user_num += 1


    # Tweet取得終了時の処理
    parent_frame.SetStatusText("Tweets Collected!") #ステータスバーの表示を変える
    try: # 鳴らせたら音を鳴らす
        audio_file = "finish.mp3" ; return_code = subprocess.call(["afplay", audio_file])
    except:
        pass
    button_collect.Enable() # 処理が終わると再びボタンを使えるようにする


def pandasSave(results_df, file_save_pass, save_type, id, date_start, date_end):

    if save_type == "csv (UTF-8)":
        save_path = os.path.join(file_save_pass, (id + "." + date_start.strftime('%Y-%m-%d') + "_" + date_end.strftime('%Y-%m-%d') + ".csv"))
        results_df.to_csv(save_path, mode='w', index=False)
    elif save_type == "csv (Shift-JIS)":
        save_path = os.path.join(file_save_pass, (id + "." + date_start.strftime('%Y-%m-%d') + "_" + date_end.strftime('%Y-%m-%d') + ".csv"))
        results_df.to_csv(save_path, mode='w', encoding='Shift_JIS', index=False)
    elif save_type == "pickel":
        save_path = os.path.join(file_save_pass, (id + "." + date_start.strftime('%Y-%m-%d') + "_" + date_end.strftime('%Y-%m-%d') + ".pkl"))
        results_df.to_pickle(save_path, mode='w', index=False)
    else:
        wx.MessageBox("File type not defined", 'Error', wx.OK | wx.ICON_ERROR)


def value_check(value, parent_frame, button_collect):
    if value < datetime.datetime.strptime("2008-04-01", '%Y-%m-%d'):
        wx.MessageBox("Twitter did not exist.", 'Error', wx.OK | wx.ICON_ERROR) ; parent_frame.SetStatusText("Collection Cancelled"); button_collect.Enable(); return (False);

    today = datetime.datetime.today()
    if value >= today:
        wx.MessageBox("You can't get today or future Tweets.", 'Error', wx.OK | wx.ICON_ERROR) ; parent_frame.SetStatusText("Collection Cancelled"); button_collect.Enable(); return (False);


#####################
###     メモ      ####
#####################
# メモリに乗り切れないほどData.Frameが大きくなったら: http://sinhrks.hatenablog.com/entry/2014/11/21/231534