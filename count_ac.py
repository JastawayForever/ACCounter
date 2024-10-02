import requests as rq
from bs4 import BeautifulSoup as BS
import os
import json
import time
import datetime
from getpass import getpass

cwd = os.getcwd()

contest_id = 'abc373' # コンテストごとにidを変えてください
MAX_PAGE = 3 # 提出ページの最大数

MY_USER_ID = '' # 自分のAtCoderユーザid (毎回入力しなくてもいいようにするにはここに入力してください)
MY_PASSWORD = '' # password

def get_start_end():
    time.sleep(1)
    req = rq.get('https://kenkoooo.com/atcoder/resources/contests.json')
    d = json.loads(req.text)
    for elem in d:
        if elem['id'] == contest_id:
            start = elem['start_epoch_second']
            end = start + elem['duration_second']
            return start, end
    print("contest not found")
    assert(False)

def read_member():
    fmember = open(cwd+'/member.txt', 'r')
    ret = []
    ignore_set = set()
    try:
        fignore = open(cwd+'/ignore.txt', 'r')
        for name in fignore.readlines():
            name = name.rstrip('\n')
            ignore_set.add(name)
    except:
        pass
    for name in fmember.readlines():
        name = name.rstrip('\n')
        if name in ignore_set:
            continue
        ret.append(name)
    return ret

def is_rated(user_id):
    time.sleep(1)
    share_url = 'https://atcoder.jp/users/{user_id}/history/share/{contest_id}'.format(user_id=user_id, contest_id=contest_id)
    req = rq.get(share_url)
    req.encoding = req.apparent_encoding
    if not req:
        return False
    return 'パフォーマンス' in req.text or 'Performance' in req.text

session = rq.session()

def login_atcoder():
    url = 'https://atcoder.jp/login'
    response = session.get(url)
    bs = BS(response.text, 'html.parser')
    authenticity = (bs.find(attrs={'name':'csrf_token'})).get('value')
    cookie = response.cookies
    user_id = MY_USER_ID
    password = MY_PASSWORD
    if user_id == '':
        user_id = input("自分のAtCoderのユーザidを入力してください : ")
    if password == '':
        password = getpass("password : ")
    login_info = {
        'username' : user_id,
        'password' : password,
        'csrf_token' : authenticity
    }
    res = session.post(url, data=login_info, cookies=cookie)
    if str(res.text).find('Username or Password is incorrect') != -1:
        print('Username or Password is incorrect')
        assert(False)

def get_ac_problems(user_id, start_time, end_time):
    ac_problems = set()
    for page in range(1, MAX_PAGE + 1):
        time.sleep(0.5)
        url = 'https://atcoder.jp/contests/{contest_id}/submissions?f.LanguageName=&f.Status=&f.Task=&f.User={user_id}&page={page_id}'.format(contest_id=contest_id, user_id=user_id, page_id=page)
        response = session.get(url)
        if not response:
            print("NOT_FOUND")
            break
        bs = BS(response.text, 'html.parser')
        table = bs.select_one('#main-container > div.row > div:nth-child(3) > div > div.table-responsive > table > tbody')
        if not table:
            break
        elems = table.find_all('tr')
        for elem in elems:
            sub_time = datetime.datetime.strptime(elem.select_one('time').contents[0], '%Y-%m-%d %H:%M:%S%z')
            sub_time = int(sub_time.timestamp())
            if not (start_time <= sub_time < end_time):
                continue
            is_ac = elem.select_one('span.label').contents[0]
            if is_ac != 'AC':
                continue
            problem_url = str(elem.select_one('a').attrs['href'])
            problem = problem_url[problem_url.find('/tasks/') + len('/tasks/'):]
            ac_problems.add(problem)
    return sorted(list(ac_problems))
    
if __name__ == '__main__':
    login_atcoder()
    start, end = get_start_end()
    members = read_member()
    count_ac = dict()
    count_rated = 0
    for user_id in members:
        if not is_rated(user_id):
            continue
        count_rated += 1
        ac_list = get_ac_problems(user_id, start, end)
        for problem in ac_list:
            if problem in count_ac:
                count_ac[problem] += 1
            else:
                count_ac[problem] = 1
    print(count_ac)
    print("rated_members =", count_rated)