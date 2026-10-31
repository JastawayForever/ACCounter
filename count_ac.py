import os
import json
import re
import requests as rq

cwd = os.getcwd()

# --- 設定項目 ---
contest_id = 'abc482'    # コンテストID
my_user_id = 'jastaway'  # 自身のAtCoder ID
login_info_file = 'cookies.json'


def get_color(rate):
    """レートやdiffに応じたHTMLカラーコードを返す"""
    if rate is None:
        return '#999999'
    
    # 負のdiffは灰色扱い
    rate = max(0, rate)
    
    if rate < 400:
        return '#999999'
    elif rate < 800:
        return '#804000'
    elif rate < 1200:
        return '#008000'
    elif rate < 1600:
        return '#00C0C0'
    elif rate < 2000:
        return '#0000FF'
    elif rate < 2400:
        return '#C0C000'
    elif rate < 2800:
        return '#FF8000'
    else:
        return '#FF0000'


def read_member():
    """member.txt と ignore.txt から対象メンバーのリストを読み込む"""
    members = []
    ignore_set = set()

    ignore_path = os.path.join(cwd, 'ignore.txt')
    if os.path.exists(ignore_path):
        with open(ignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name:
                    ignore_set.add(name)

    member_path = os.path.join(cwd, 'member.txt')
    if os.path.exists(member_path):
        with open(member_path, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name and name not in ignore_set:
                    members.append(name)

    return members


def login_atcoder(session):
    """cookies.json を読み込み、セッションにセットする"""
    path = os.path.join(cwd, login_info_file)
    if not os.path.exists(path):
        print(f"Warning: {login_info_file} が見つかりません。非ログイン状態（公開順位表）で進行します。")
        return

    with open(path, 'r', encoding='utf-8') as f:
        login_info = json.load(f)

    if not login_info.get("value"):
        print("Warning: Cookie の値が空です。非ログイン状態で進行します。")
        return

    session.cookies.set(login_info["name"], login_info["value"])


def get_standings_json(session):
    """順位表JSONを一括取得する"""
    url = f'https://atcoder.jp/contests/{contest_id}/standings/json'
    res = session.get(url)
    if res.status_code != 200:
        raise RuntimeError(f"順位表JSONの取得に失敗しました (Status Code: {res.status_code})")
    return res.json()


def get_my_perf_and_after_rate(session):
    """成績シェアページから自分のperfとコンテスト後レートを取得する（未反映時は手入力）"""
    url = f'https://atcoder.jp/users/{my_user_id}/history/share/{contest_id}'
    try:
        res = session.get(url, timeout=5)
        if res.status_code == 200:
            text = res.text
            perf_match = re.search(r'パフォーマンス[^\d]*(\d+)', text) or re.search(r'Performance[^\d]*(\d+)', text)
            rate_match = re.search(r'→\s*(\d+)', text) or re.search(r'->\s*(\d+)', text)

            if perf_match and rate_match:
                return int(perf_match.group(1)), int(rate_match.group(1))
    except Exception as e:
        print(f"成績表からの自動取得スキップ: {e}")

    print("\n[情報] 成績表が未反映か取得できませんでした。手動入力してください（スキップする場合は空エンターで0扱いになります）。")
    perf_in = input("自分のパフォーマンス (perf): ").strip()
    after_rate_in = input("コンテスト後のレート (after_rate): ").strip()

    perf = int(perf_in) if perf_in.isdigit() else 0
    after_rate = int(after_rate_in) if after_rate_in.isdigit() else 0
    return perf, after_rate


def get_problem_models():
    """AtCoder Problems から各問題の diff 情報を取得する"""
    url = 'https://kenkoooo.com/atcoder/resources/problem-models.json'
    try:
        res = rq.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"AtCoder Problems API からの diff 取得スキップ: {e}")
    return {}


def format_time(elapsed_ns):
    """ナノ秒（10^-9 sec）を MM:SS 形式に変換"""
    sec = int(elapsed_ns) // 1_000_000_000
    return f"{sec // 60}:{sec % 60:02d}"


def main():
    session = rq.session()
    login_atcoder(session)

    # 1. 順位表JSONの一括取得
    print("順位表データを取得中...")
    standings = get_standings_json(session)

    task_info = standings.get('TaskInfo', [])
    standings_data = standings.get('StandingsData', [])

    # タスク対応マップ (例: 'abc479_a' -> 'A')
    task_map = {t['TaskScreenName']: t['Assignment'] for t in task_info}
    prob_letters = [t['Assignment'].lower() for t in task_info]

    # StandingsData を ユーザーID キーで辞書化（高速検索用）
    user_standings_map = {}
    for user_data in standings_data:
        u_screen = user_data.get('UserScreenName')
        u_name = user_data.get('UserName')
        if u_screen:
            user_standings_map[u_screen] = user_data
        if u_name:
            user_standings_map[u_name] = user_data

    # 2. サークルメンバーの Rated 判定 & 正解数集計
    members = read_member()
    count_rated = 0
    count_ac = {t['TaskScreenName']: 0 for t in task_info}

    for member_id in members:
        if member_id not in user_standings_map:
            continue
        user_data = user_standings_map[member_id]

        # Rated参加者の判定
        if not user_data.get('IsRated', False):
            continue

        count_rated += 1

        # 各問題のAC状況を集計 (Status == 1 または Score > 0)
        task_results = user_data.get('TaskResults', {})
        for task_screen_name, res in task_results.items():
            if res.get('Status') == 1 or res.get('Score', 0) > 0:
                if task_screen_name in count_ac:
                    count_ac[task_screen_name] += 1

    print(f"集計完了: Rated対象メンバー = {count_rated}名")
    
    print("\n--- 各問題のRatedメンバー内AC数 ---")
    for t in task_info:
        assignment = t['Assignment']  # 例: 'A', 'B'
        ac_cnt = count_ac[t['TaskScreenName']]
        print(f"  問題 {assignment}: {ac_cnt}名")
    print("-----------------------------------\n")

    # 3. 自分の情報設定
    my_standings = user_standings_map.get(my_user_id)
    if not my_standings:
        raise ValueError(f"エラー: 順位表データ内に my_user_id ('{my_user_id}') が見つかりませんでした。")

    data = {
        'contest_id': contest_id,
        'upper_id': contest_id.upper(),
        'rank': my_standings.get('Rank', 0),
        'before_rate': int(my_standings.get('OldRating', 0)),
        'before_rate_color': get_color(int(my_standings.get('OldRating', 0))),
        'cnt_solve': int(my_standings.get('TotalResult', {}).get('Accepted', 0)),
        'rated_member': count_rated,
    }

    # かかった最大時間
    total_elapsed = my_standings.get('TotalResult', {}).get('Elapsed', 0)
    data['max_time'] = format_time(total_elapsed)

    # 各問題（a~g）の初期化
    for letter in prob_letters:
        data[f'{letter}_subtime'] = '0:00'
        data[f'{letter}_suburl'] = ''
        data[f'{letter}_solve'] = 0

    # 自分の各問題AC時間・提出URLのセット
    my_task_results = my_standings.get('TaskResults', {})
    for task_screen_name, res in my_task_results.items():
        if task_screen_name in task_map:
            letter = task_map[task_screen_name].lower()
            if res.get('Status') == 1 or res.get('Score', 0) > 0:
                sub_id = res.get('SubmissionID')
                elapsed = res.get('Elapsed', 0)
                data[f'{letter}_subtime'] = format_time(elapsed)
                data[f'{letter}_suburl'] = f'https://atcoder.jp/contests/{contest_id}/submissions/{sub_id}'

    # 各問題のサークル内正解者数をセット
    for task_screen_name, solve_cnt in count_ac.items():
        if task_screen_name in task_map:
            letter = task_map[task_screen_name].lower()
            data[f'{letter}_solve'] = solve_cnt

    # 4. パフォーマンス & コンテスト後レートの取得
    print("パフォーマンスおよび更新後レートを取得中...")
    my_perf, after_rate = get_my_perf_and_after_rate(session)
    data['perf'] = my_perf
    data['perf_color'] = get_color(my_perf)
    data['after_rate'] = after_rate
    data['after_rate_color'] = get_color(after_rate)

    # 5. AtCoder Problems から diff 情報の取得
    print("各問題の diff 情報を取得中...")
    problem_models = get_problem_models()

    for t in task_info:
        task_screen_name = t['TaskScreenName']
        letter = t['Assignment'].lower()

        diff = None
        if task_screen_name in problem_models:
            diff_info = problem_models[task_screen_name]
            if 'difficulty' in diff_info:
                diff = int(diff_info['difficulty'])

        if diff is not None:
            data[f'{letter}_diff'] = diff
            data[f'{letter}_diff_color'] = get_color(diff)
        else:
            # diff 未反映時のデフォルト表示
            data[f'{letter}_diff'] = '---'
            data[f'{letter}_diff_color'] = '#999999'

    # 6. テンプレートファイルの書き出し
    template_path = os.path.join(cwd, 'blogtemplate.txt')
    output_path = os.path.join(cwd, 'template.txt')

    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()

        try:
            output_text = template_str.format(**data)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"\n[成功] 正常に {output_path} を出力しました！")
        except KeyError as e:
            print(f"\n[エラー] テンプレート内のキー {e} に対応するデータが見つかりませんでした。")
    else:
        print(f"\n[エラー] {template_path} が存在しません。")


if __name__ == '__main__':
    main()