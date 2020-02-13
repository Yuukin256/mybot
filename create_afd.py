######################################################################
# [[Wikipedia:削除依頼/ログ/yyyy年m月d日]]のページを自動作成するプログラム
# 現在の日付に9時間足した日付を算出し、その日付のページを作成します
# そのため、日付が変わる9時間前から次の日のページが作成できます
######################################################################

import datetime

import pywikibot


def main():
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

    if now.hour == 23 or 0:
        # 23時か0時であれば削除依頼のログページを投稿
        print('\n\nWikipedia:削除依頼/ログ/' + d_string2 + 'を作成します。')
        site = pywikibot.Site()
        page = pywikibot.Page(site, 'Wikipedia:削除依頼/ログ/' + d_string2)

        page.text = out_text
        page.save(summary='Botによる: [[Wikipedia:削除依頼]]のログページ作成', minor=False)

    else:
        print('\n\n削除依頼ログページを作成すべき時刻ではないため、処理を終了します。')


if __name__ == '__main__':
    main()
