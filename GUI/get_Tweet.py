from bs4 import BeautifulSoup
import httplib2
import pandas as pd
import datetime
from math import isnan
import re


def getTweets(request_url): # cf. http://goo.gl/yhJHWe
    # ブログから Content-Body を取得する
    h = httplib2.Http('.cache') #by httplib2
    try:
        response, content = h.request(request_url)
        content = content.decode("utf-8")
    except:
        return (float("nan"), float("nan")) #, float("nan"))

    # HTML をパースする
    soup = BeautifulSoup(content, "lxml")
    # 記事タイトルの入った <div> の一覧を取得する ('class' 要素が 'title' のもの)
    tweet_list = soup.find_all('p', {'class': 'tl-text'})
    timestamp_list = soup.find_all('p', {'class': 'tl-posted'}) # ここからretweetなのか postなのか、あと時刻がわかる
    userID_list = soup.find_all('p', {'class': 'tl-name'})# retweetなら、元ツイートの人の名前が入るみたい

    return (tweet_list, timestamp_list) #, userID_list)

# リプライと引用ツイートの区別がしっかりつくようにしないと
# アカウントごとにファイルを作るようにしようかな

def CleanTweets(tweet_list, timestamp_list, user): #, userID_list):
    tweet_cleaned_list = [] #; timestamp_cleaned_list = [] # ; userID_cleaned_list = []
    rawlink_cleaned_list = []; tweet_type_list = []; tweet_time_list = []; quoted_list = []; replyto_list = []

    if type(tweet_list)==float and type(timestamp_list)==float: # float型なら、nanを取っている
        return (tweet_cleaned_list.append(float("nan")),
                rawlink_cleaned_list.append(float("nan")),
                tweet_type_list.append(float("nan")), tweet_time_list.append(float("nan")),
                quoted_list.append(float("nan")), replyto_list.append(float("nan")))

    for tweet, timestamp in zip(tweet_list, timestamp_list):
        # 先にTweetTypeを確認
        try:
            rules =  re.compile(r">(?P<p2>.+) at <")
            result = rules.search(str(timestamp))
            tweet_type = result.group("p2")
        except:
            next

        # 引用RTとReplyの別処理
        if tweet_type != "retweeted" and re.search(r'RT', str(tweet)) != None: # 引用RT対策
            rules =  re.compile(r"\<p class=\"tl-text\"\>(\s?)(?P<p1>.+?)(\s?)(?P<p2>RT)(\s?)(?P<p3>.+)\<\/p\>")
            result = rules.search(str(tweet))
            tweet_cleaned_list.append(result.group("p1"))

            tweet_type_list.append("quote")
            quoted_list.append(result.group("p3"))
            replyto_list.append(float("nan"))

        elif tweet_type != "retweeted" and re.search(r'\<p class=\"tl-text\"\>(\s?)<a href=\".+?\" target=\"_blank\">\@(?P<p1>.+?)\<\/a\>(\s?)(?P<p2>.+)', str(tweet)) != None: # Reply対策(文頭にReply)
            rules =  re.compile(r'<a href=\".+?\" target=\"_blank\">\@(?P<p1>.+?)\<\/a\>(\s?)(?P<p2>.+)')
            result = rules.search(str(tweet))
            replyto_list.append(result.group("p1"))
            tweet_cleaned_list.append(re.sub(r"<\/p\>", "", result.group("p2")))

            tweet_type_list.append("reply")
            quoted_list.append(float("nan"))

        elif tweet_type != "retweeted" and re.search(r'\<p class=\"tl-text\"\>(?P<p2>.+?)(\s?)<a href=\".+?\" target=\"_blank\">(\s?)\@(?P<p1>.+?)\<\/a\>\<\/p\>', str(tweet)) != None: # Reply対策(文末にReply)
            rules =  re.compile(r'\<p class=\"tl-text\"\>(?P<p2>.+?)<a href=\".+?\" target=\"_blank\">(\s?)\@(?P<p1>.+?)\<\/a\>\<\/p\>')
            result = rules.search(str(tweet))
            tweet_cleaned_list.append(re.sub(r"<\/p\>", "", result.group("p2")))

            # ツイート途中のリプライなどが、上のままだど抜けてしまうので処理
            rules2 = re.compile(r"(?P<p3>.\w+)(<)*")
            result2 = rules2.search(result.group("p1"))
            replyto_list.append(result2.group("p3"))

            tweet_type_list.append("reply")
            quoted_list.append(float("nan"))

        # 公式コメント付きRT
        elif tweet_type != "retweeted" and re.search(r"\<p class=\"tl-text\"\>(\s?)(?P<p1>.+?)(\s?)<a href=\"(?P<p2>http://t.co.+?)\" target=\"_blank\" title=(.+)><span class=\"invisible\">https://</span>twitter.", str(tweet)) != None: # 公式コメント付きRT
            rules =  re.compile(r"\<p class=\"tl-text\"\>(\s?)(?P<p1>.+?)(\s?)<a href=\"(?P<p2>http://t.co.+?)\" target=\"_blank\" title=(.+)><span class=\"invisible\">https://</span>twitter.")
            result = rules.search(str(tweet))
            tweet_cleaned_list.append(re.sub(r"<\/p\>|\s", "", result.group("p1")))
            quoted_list.append(re.sub(r"<\/p\>", "", result.group("p2")))

            replyto_list.append(float("nan"))
            tweet_type_list.append("comment-retweet")

        else:
            rules =  re.compile(r"(?P<p1>\<p class=\"tl-text\"\>)(?P<p2>.+)(?P<p3>\<\/p\>)")
            result = rules.search(str(tweet))
            try:
                tweet_cleaned_list.append(result.group("p2"))
            except:
                tweet_cleaned_list.append("***取得失敗***")

            rules =  re.compile(r">(?P<p2>.+) at <")
            result = rules.search(str(timestamp))
            try:
                tweet_type_list.append(result.group("p2"))
            except:
                tweet_type_list.append(float("nan"))

            quoted_list.append(float("nan"))
            replyto_list.append(float("nan"))

        # 全てに共通
        try:
            rules =  re.compile(r">(?P<p3>\d\d\:\d\d:\d\d)</a></p>")
            result = rules.search(str(timestamp))
            tweet_time_list.append(result.group("p3"))

            rules =  re.compile(r"\<a href=\"(?P<p1>.+)\" target")
            result = rules.search(str(timestamp))
            rawlink_cleaned_list.append(result.group("p1"))
        except:
            tweet_time_list.append(float("nan"))
            rawlink_cleaned_list.append(float("nan"))


    return(tweet_cleaned_list, rawlink_cleaned_list, tweet_type_list, tweet_time_list, quoted_list, replyto_list)


def getUserLists(user_list_pass):
    user_pd = pd.read_csv(user_list_pass)
    return (user_pd.ix[:,"screen_name"], user_pd)  # 0という列番号で指定していたのを10/10変更


def makeDateList(date_start, date_end):
    date_list = []

    while date_start != date_end:
        date_list.append(date_start)
        date_start += datetime.timedelta(days = 1)
    date_list.append(date_start)

    return date_list
