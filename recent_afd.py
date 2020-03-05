##########################################################################
# 直近 2 日間 (JST) の内に作成された [[Wikipedia:削除依頼]] のサブページを一覧表示する
# 日付別ログページへの掲載漏れがある場合、 Bot のサブページに投稿
##########################################################################

import datetime
import re
import urllib

import requests

import pywikibot
from pywikibot import config2 as config

today = datetime.date.today()
startdate = today - datetime.timedelta(days=1)
enddate = startdate - datetime.timedelta(days=2)


def get_day_of_week_jp(dt):
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    return(weekdays[dt.weekday()])


def apirequest(params):
    s = requests.Session()
    url = 'https://ja.wikipedia.org/w/api.php'
    r = s.get(url=url, params=params)
    data = r.json()
    return data


def main():
    pywikibot.bot.writeToCommandLogFile()

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

    data = apirequest(newpages_params)
    newpages = data['query']['recentchanges']

    new_afd_pages = [e for e in newpages if re.match(r'Wikipedia:削除依頼/[^(ログ)]', str(e['title']))]

    transcludedin_params = {
        'action': 'query',
        'format': 'json',
        'prop': 'transcludedin',
        'rawcontinue': 1,
        'pageids': '|'.join(map(str, [e['pageid'] for e in new_afd_pages])),
        'utf8': 1,
        'tiprop': 'title',
        'tinamespace': '4',
        'tishow': '!redirect',
        'tilimit': 'max'
    }

    data = apirequest(transcludedin_params)
    transcludedin_list = data['query']['pages']

    pageids = [e['pageid'] for e in new_afd_pages]
    revids = [e['revid'] for e in new_afd_pages]
    timestamps = [e['timestamp'] for e in new_afd_pages]
    sizes = [e['newlen'] for e in new_afd_pages]
    users = [e['user'] for e in new_afd_pages]
    userids = [e['userid'] for e in new_afd_pages]

    i = 0
    check_transcludedin = False
    entries = ''

    for e in new_afd_pages:
        t = transcludedin_list[str(pageids[i])]

        time_datetime = datetime.datetime.strptime(
            timestamps[i], '%Y-%m-%dT%H:%M:%SZ')
        date = f'{time_datetime.year}年{time_datetime.month}月{time_datetime.day}日 ({get_day_of_week_jp(time_datetime)}) '
        time = time_datetime.strftime('%R')
        id_and_time = f'{{{{oldid|{str(revids[i])}|{date}{time} (UTC)}}}}'

        title = t['title']
        underbar_title = title.replace(' ', '_')
        url_encoded_title = urllib.parse.quote(underbar_title)
        no_namespace_title = title.replace('Wikipedia:', '', 1)

        size = str(sizes[i])

        user = f'{{{{IPuser|{users[i]}}}}}' if userids[i] == 0 else f'{{{{User|{users[i]}}}}}'

        if 'transcludedin' in t:
            length = str(len(t['transcludedin']))
            transcludedin = f'参照読み込み: {{{{Fullurl|n=特別:リンク元|p=target={url_encoded_title}&hideredirs=1&hidelinks=1&namespace=4|s={length} ページ}}}}'
        else:
            transcludedin = f'<span style=\"color:red\">\'\'\'参照読み込み: </span>{{{{Fullurl|n=特別:リンク元'\
                f'|p=target={underbar_title}&hideredirs=1&hidelinks=1&namespace=4'\
                '|s=<span style=\"color:red\">0 ページ</span>}}\'\'\''
            check_transcludedin = True

        entry = f'* {id_and_time} . . {{{{P|Wikipedia|{no_namespace_title}}}}} [{size}バイト] {user} {transcludedin}'
        entries += '\n' + entry

        i = i + 1

    pywikibot.output('一覧を生成しました。')
    pywikibot.output(entries)

    if check_transcludedin:
        summary = '最近作成された [[WP:AFD|削除依頼]] サブページの一覧です。毎日 15:15 (UTC) 頃に動作し、日付別ログページへの掲示が行われていないサブページがあったときのみ投稿します。'
        log = f'[[Wikipedia:削除依頼/ログ/{today.year}年{today.month}月{today.day}日]]'
        period = f'{enddate.year}年{enddate.month}月{enddate.day}日 ({get_day_of_week_jp(enddate)}) 15:00 (UTC) - '\
            f'{startdate.year}年{startdate.month}月{startdate.day}日 ({get_day_of_week_jp(startdate)}) 15:00 (UTC)'

        out_text = f'{summary}\n掲示先: {log}\n:集計期間: {period}\n{entries}'

        pywikibot.output('\n参照読み込みされていないページがあります！\n[[利用者:YuukinBot2/最近の削除依頼]] へと結果を投稿します。')

        site = pywikibot.Site(user='YuukinBot2')
        site.login()

        page = pywikibot.Page(site, '利用者:YuukinBot2/最近の削除依頼')
        config.put_throttle = 0

        page.text = out_text
        page.save(summary='Botによる: 最近作成された [[WP:AfD|削除依頼]] の一覧を生成', minor=False)

    else:
        pywikibot.output('参照読み込みされていないページはありませんでした。')


if __name__ == '__main__':
    main()
