# 直近 2 日間 (JST) の内に作成された [[Wikipedia:削除依頼]] のサブページを一覧表示する
# 日付別ログページへの掲載漏れがある場合、 Bot のサブページに投稿

import datetime
import re

import pywikibot
import requests
from pywikibot import config2 as config


class Page(pywikibot.Page):
    def __init__(self, site, data):
        self.data = data
        super().__init__(site, data['title'])

    def put_transcludedin(self, data: dict):
        self.transcludedin_list = data[str(
            self.pageid)]['transcludedin'] if 'transcludedin' in data[str(self.pageid)] else None

    @property
    def oldest_rev_id(self) -> int:
        return self.data['revid']

    @property
    def page_id(self) -> int:
        return self.data['pageid']

    @property
    def oldest_rev_timestamp(self) -> datetime:
        return datetime.datetime.strptime(self.data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')

    @property
    def size(self) -> int:
        return self.data['newlen']

    @property
    def is_redirect(self) -> bool:
        return True if self.data.get('') == '' else False

    @property
    def user(self) -> str:
        return self.data['user']

    @property
    def user_id(self) -> int:
        return self.data['userid']

    @property
    def transcludedin(self) -> bool:
        return bool(self.transcludedin_list)

    @property
    def transcludedin_number(self) -> int:
        return len(self.transcludedin_list)


def get_day_of_week_jp(dt):
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    return(weekdays[dt.weekday()])


def apirequest(params):
    url = 'https://ja.wikipedia.org/w/api.php'
    r = requests.get(url=url, params=params)
    return r.json()


def main():
    site = pywikibot.Site(user='YuukinBot2')
    site.login()
    pywikibot.bot.writeToCommandLogFile()

    today = datetime.date.today()
    startdate = today - datetime.timedelta(days=1)
    enddate = startdate - datetime.timedelta(days=2)

    newpages_params = {
        'action': 'query',
        'format': 'json',
        'list': 'recentchanges',
        'utf8': 1,
        'rcstart': str(startdate) + 'T15:00:00.000Z',
        'rcend': str(enddate) + 'T15:00:00.000Z',
        'rcdir': 'older',
        'rcnamespace': '4',
        'rcprop': 'title|ids|timestamp|sizes|redirect|user|userid',
        'rclimit': 'max',
        'rctype': 'new'
    }

    data = apirequest(newpages_params)
    newpages = data['query']['recentchanges']
    new_afd_pages = [Page(site, p) for p in newpages if re.match(
        r'Wikipedia:削除依頼/[^(ログ)]', str(p['title'])) and 'redirect' not in p]

    transcludedin_params = {
        'action': 'query',
        'format': 'json',
        'prop': 'transcludedin',
        'rawcontinue': 1,
        'pageids': '|'.join(map(str, [p.pageid for p in new_afd_pages])),
        'utf8': 1,
        'tiprop': 'title',
        'tinamespace': '4',
        'tishow': '!redirect',
        'tilimit': 'max'
    }

    data = apirequest(transcludedin_params)
    transcludedin_list = data['query']['pages']
    for p in new_afd_pages:
        p.put_transcludedin(transcludedin_list)

    check_transcludedin = False
    entries = ''

    for p in new_afd_pages:
        if not p.exists():
            continue

        date = f'{p.oldest_rev_timestamp.year}年{p.oldest_rev_timestamp.month}月{p.oldest_rev_timestamp.day}日'\
            f' ({get_day_of_week_jp(p.oldest_rev_timestamp)}) '
        time = p.oldest_rev_timestamp.strftime('%R')
        id_and_time = f'{{{{oldid|{p.oldest_rev_id}|{date}{time} (UTC)}}}}'

        title = p.title().replace('=', '{{=}}')
        title_underscore = p.title(underscore=True).replace('=', '{{=}}')
        user = f'{{{{IPuser|{p.user}}}}}' if p.user_id == 0 else f'{{{{User|{p.user}}}}}'

        if p.transcludedin:
            transcludedin = f'参照読み込み: {{{{Fullurl|n=特別:リンク元'\
                f'|p=target={title_underscore}&hideredirs=1&hidelinks=1&namespace=4'\
                f'|s={p.transcludedin_number} ページ}}}}'
        else:
            transcludedin = f'\'\'\'<span style=\"color:red\">参照読み込み: </span>{{{{Fullurl|n=特別:リンク元'\
                f'|p=target={title_underscore}&hideredirs=1&hidelinks=1&namespace=4'\
                '|s=<span style=\"color:red\">0 ページ</span>|t=}}\'\'\''
            check_transcludedin = True

        entry = f'* {id_and_time} . . {{{{Page|{title}}}}} [{p.size}バイト] {user} {transcludedin}'
        entries += '\n' + entry

    pywikibot.output('一覧を生成しました。')
    pywikibot.output(entries)

    if check_transcludedin:
        summary = '最近作成された [[WP:AFD|削除依頼]] サブページの一覧です。毎日 15:15 (UTC) 頃に動作し、日付別ログページへの掲示が行われていないサブページがあったときのみ投稿します。'
        log = f'[[Wikipedia:削除依頼/ログ/{today.year}年{today.month}月{today.day}日]]'
        period = f'{enddate.year}年{enddate.month}月{enddate.day}日 ({get_day_of_week_jp(enddate)}) 15:00 (UTC) - '\
            f'{startdate.year}年{startdate.month}月{startdate.day}日 ({get_day_of_week_jp(startdate)}) 15:00 (UTC)'
        out_text = f'{summary}\n掲示先: {log}\n:集計期間: {period}\n{entries}'

        pywikibot.output('\n参照読み込みされていないページがあります！\n[[利用者:YuukinBot2/最近の削除依頼]] へと結果を投稿します。')
        config.put_throttle = 0

        page = pywikibot.Page(site, '利用者:YuukinBot2/最近の削除依頼')
        page.text = out_text
        page.save(summary='Botによる: 最近作成された [[WP:AfD|削除依頼]] の一覧を生成', minor=False)

    else:
        pywikibot.output('参照読み込みされていないページはありませんでした。')


if __name__ == '__main__':
    main()
