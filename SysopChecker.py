import datetime
from time import sleep

import requests
from dateutil.relativedelta import relativedelta

S = requests.Session()
URL = 'https://ja.wikipedia.org/w/api.php'

sysop_id_list = list()
sysop_name_list = list()
no_contribs_list = list()
no_logs_list = list()

now = datetime.datetime.utcnow()
td = relativedelta(months=3)
three_month_ago = now - td
end = three_month_ago.isoformat(timespec='milliseconds') + 'Z'


get_sysop_params = {
    "action": "query",
    "format": "json",
    "list": "allusers",
    "utf8": 1,
    "augroup": "sysop",
    "aurights": "",
    "aulimit": "100",
    "auwitheditsonly": 1
}

r = S.get(url=URL, params=get_sysop_params)
data = r.json()['query']['allusers']


for entry in data:
    sysop_id_list.append(entry['userid'])
    sysop_name_list.append(entry['name'])


for (id, name) in zip(sysop_id_list, sysop_name_list):
    sleep(1)

    get_contribs_params = {
        "action": "query",
        "format": "json",
        "list": "usercontribs",
        "utf8": 1,
        "uclimit": "1",
        "ucend": end,
        "ucuserids": id
    }

    r = S.get(url=URL, params=get_contribs_params)
    data = r.json()['query']['usercontribs']

    if len(data) == 0:
        no_contribs_list.append(name)


for name in no_contribs_list:
    sleep(1)

    get_logs_params = {
        "action": "query",
        "format": "json",
        "list": "logevents",
        "utf8": 1,
        "leprop": "ids",
        "leend": end,
        "leuser": name,
        "lelimit": "1"
    }

    r = S.get(url=URL, params=get_logs_params)
    data = r.json()['query']['logevents']

    if len(data) == 0:
        no_logs_list.append(name)

print(no_logs_list)
