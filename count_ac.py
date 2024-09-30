import requests as rq
import os
import json
import time

cwd = os.getcwd()

contest_id = 'abc373' # コンテストごとにidを変えてください

def get_start_end():
    time.sleep(1)
    req = rq.get('https://kenkoooo.com/atcoder/resources/contests.json')
    d = json.loads(req.text)
    for elem in d:
        if elem['id'] == contest_id:
            start = elem['start_epoch_second']
            end = start + elem['duration_second']
            return start, end
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

def is_reated(user_id):
    time.sleep(1)
    share_url = 'https://atcoder.jp/users/{user_id}/history/share/{contest_id}'.format(user_id=user_id, contest_id=contest_id)
    req = rq.get(share_url)
    req.encodeing = req.apparent_encoding
    if not req:
        return False
    return 'パフォーマンス' in req.text or 'Performance' in req.text

def get_ac_problems(user_id, start_time, end_time):
    time.sleep(1)
    url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={user_id}&from_second={unix_second}".format(user_id=user_id, unix_second=start_time)
    req = rq.get(url)
    d = json.loads(req.text)
    ret = set()
    for submition in d:
        if submition['contest_id'] != contest_id:
            continue
        if start_time <= submition['epoch_second'] <= end_time:
            if submition['result'] == 'AC':
                ret.add(submition['problem_id'])
    return sorted(list(ret))
    
if __name__ == '__main__':
    start, end = get_start_end()
    members = read_member()
    count_ac = dict()
    count_rated = 0
    for user_id in members:
        if not is_reated(user_id):
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