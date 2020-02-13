##########################################################################
# 直近 2 日間 (JST) の内に作成された [[Wikipedia:削除依頼]] のサブページを一覧表示する
# 日付別ログページへの掲載漏れがある場合、 Bot のサブページに投稿
##########################################################################

import datetime
import re
import urllib

import requests
import pywikibot

today = datetime.date.today()
startdate = today - datetime.timedelta(days=1)
enddate = startdate - datetime.timedelta(days=2)

def get_day_of_week_jp(dt):
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    return(weekdays[dt.weekday()])


def apirequest(params):
    S = requests.Session()
    URL = 'https://ja.wikipedia.org/w/api.php'

    R = S.get(url=URL, params=params)
    DATA = R.json()

    return DATA


def makelist(newafdpages, transcludedin):
    revids = [rc['revid'] for rc in newafdpages]
    timestamps = [rc['timestamp'] for rc in newafdpages]
    sizes = [rc['newlen'] for rc in newafdpages]
    users = [rc['user'] for rc in newafdpages]
    userids = [rc['userid'] for rc in newafdpages]

    i = 0
    check_transcludedin = False
    item_list = list()

    for rc in newafdpages:
        this = transcludedin[str(rc['pageid'])]

        time_datetime = datetime.datetime.strptime(
            timestamps[i], '%Y-%m-%dT%H:%M:%SZ')
        date = f'{time_datetime.year}年{time_datetime.month}月{time_datetime.day}日 ({get_day_of_week_jp(time_datetime)}) '
        time = time_datetime.strftime('%R')
        id_and_time = f'{{{{oldid|{str(revids[i])}|{date}{time} (UTC)}}}}'

        title = this['title']
        underbar_title = title.replace(' ', '_')
        url_encoded_title = urllib.parse.quote(underbar_title)
        no_namespace_title = title.replace('Wikipedia:', '', 1)

        size = str(sizes[i])

        user = f'{{{{IPuser|{users[i]}}}}}' if userids[i] == 0 else f'{{{{User|{users[i]}}}}}'

    if 'transcludedin' in this:
        length = str(len(this['transcludedin']))
        transcludedin = f'参照読み込み: {{{{Fullurl|n=特別:リンク元|p=target={url_encoded_title}&hideredirs=1&hidelinks=1&namespace=4|s={length} ページ}}}}'
    else:
        transcludedin = f'<span style=\"color:red\">\'\'\'参照読み込み: </span>{{{{Fullurl|n=特別:リンク元'\
            f'|p=target={underbar_title}&hideredirs=1&hidelinks=1&namespace=4'\
            '|s=<span style=\"color:red\">0 ページ</span>}}\'\'\''
        check_transcludedin = True

    item = f'* {id_and_time} . . {{{{P|Wikipedia|{no_namespace_title}}}}} [{size}バイト] {user} {transcludedin}'
    item_list.append(item)

    i += 1

    if check_transcludedin:
        summary = '最近作成された [[WP:AFD|削除依頼]] サブページの一覧です。毎日 15:15 (UTC) 頃に動作し、日付別ログページへの掲示が行われていないサブページがあったときのみ投稿します。'
        log = f'[[Wikipedia:削除依頼/ログ/{today.year}年{today.month}月{today.day}日]]'
        period = f'{enddate.year}年{enddate.month}月{enddate.day}日 ({get_day_of_week_jp(enddate)}) 15:00 (UTC) - '\
            f'{startdate.year}年{startdate.month}月{startdate.day}日 ({get_day_of_week_jp(startdate)}) 15:00 (UTC)'

        out_text = '{}\n掲示先: {}\n:集計期間: {}\n\n{}'.format(summary, log, period, '\n'.join(item_list))
        post(out_text)

    print('done')


def post(out_text):
    print('\n参照読み込みされていないページがあります！\n[[利用者:YuukinBot2/最近の削除依頼]] へと結果を投稿します')

    site = pywikibot.Site()
    page = pywikibot.Page(site, '利用者:YuukinBot2/最近の削除依頼')

    page.text = out_text
    page.save(summary='Botによる: 最近作成された [[WP:AfD|削除依頼]] の一覧を生成', minor=False)


def main():
    newpages_params = {
        'action': 'query',
        'format': 'json',
        'list': 'recentchanges',
        'utf8': 1,
        'rcstart': str(startdate) + 'T15:00:00.000Z',
        'rcend': str(enddate) + 'T15:00:00.000Z',
        'rcdir': 'older',
        'rcnamespace': '4',
        'rcprop': 'title|ids|timestamp|sizes|user|userid',
        'rclimit': 'max',
        'rctype': 'new'
    }

    newpages = apirequest(newpages_params)['query']['recentchanges']

    newafdpages = [e for e in newpages if re.match(r'Wikipedia:削除依頼/[^(ログ)]', str(e['title']))]


    transcludedin_params = {
        'action': 'query',
        'format': 'json',
        'prop': 'transcludedin',
        'rawcontinue': 1,
        'pageids': '|'.join(map(str, [e['pageid'] for e in newafdpages])),
        'utf8': 1,
        'tiprop': 'title',
        'tinamespace': '4',
        'tishow': '!redirect',
        'tilimit': 'max'
    }

    transcludedin = apirequest(transcludedin_params)['query']['pages']

    makelist(newafdpages, transcludedin)


if __name__ == '__main__':
    main()
