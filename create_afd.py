######################################################################
# [[Wikipedia:削除依頼/ログ/yyyy年m月d日]]のページを自動作成するプログラム
# 現在の日付に9時間足した日付を算出し、その日付のページを作成します
# そのため、日付が変わる9時間前から次の日のページが作成できます
######################################################################

import datetime

import pywikibot
from pywikibot import config2 as config


def main():
    pywikibot.bot.writeToCommandLogFile()
    # 日付の指定
    now = datetime.datetime.now()
    date = now + datetime.timedelta(hours=9)  # 今の時刻に9時間足す

    # 日付を文字列型で整形
    d_string1 = date.strftime('%Y-%m-%d')  # yyyy-mm-dd 0埋め有り dateパラメータ用
    d_string2 = f'{date.year}年{date.month}月{date.day}日'  # yyyy年m月d日 0埋め無し ページ名用
    d_string3 = f'{date.month}月{date.day}日'  # m月d日 0埋め無し 節名用

    out_text = '== ' + d_string3 + ' =='\
        '\n<noinclude>{{purge}} - </noinclude>{{削除依頼/ログ日付|date=' + d_string1 + '}} {{削除依頼/ログ作成}}'\
        '\n<!-- 新規の依頼はこの下に付け足してください -->'

    if now.hour in [23, 0]:
        # 23時か0時で
        config.put_throttle = 0
        site = pywikibot.Site(user='YuukinBot2')
        site.login()

        page = pywikibot.Page(site, 'Wikipedia:削除依頼/ログ/' + d_string2)

        if not page.exists():
            # ページが存在しなければ
            pywikibot.output('\n\nWikipedia:削除依頼/ログ/' + d_string2 + 'を作成します。')

            page.text = out_text
            page.save(summary='Botによる: [[Wikipedia:削除依頼]]のログページ作成', minor=False)
        else:
            pywikibot.output('\n\nWikipedia:削除依頼/ログ/' + d_string2 + 'は既に存在します。')
    else:
        pywikibot.output('\n\n削除依頼ログページを作成すべき時刻ではありません。')


if __name__ == '__main__':
    main()
