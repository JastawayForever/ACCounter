# AtCoderContest ACカウンター
作成者 jastaway

## 使い方
`member.txt`に対象のAtCoderユーザidを1行ごとに入力しておいてください。

カウントされたくないユーザがいれば`ignore.txt`に同様に入力してください。

`count_ac.py`の上部にある`contest_id`を変更してください。

`cookies.json`の`"value"`にブラウザのcookieのログイン情報を入力してください。

chromeの場合、ログインした状態のatcoderのページでF12等でデベロッパーツールを開き、上のタブから アプリケーション → ストレージ → Cookie → https://atcoder.jp → REVEL_SESSIONの値をコピーしてペーストしてください。

この`README.md`があるディレクトリで`count_ac.py`を実行してください。

## 注意
APIの取得に間隔を設けています。そのため、O(ユーザの人数)秒程度の時間がかかります。

提出についてAtCoderのサイトを直接webスクレイピングするようにしました。そのため、ログイン情報が必要になりました。ログインしたくない方はv1.0を使用してください。

コンテストの情報はProblemsのAPIを使用しているので、コンテスト直後は追加されていないかもしれません。ご注意ください。

## 必要モジュール
自分のpythonの環境に以下のモジュールがインストールされていなければ入れてください
```
requests
bs4
os
json
time
datetime
```
