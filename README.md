# AtCoderContest ACカウンター
作成者 jastaway

## 使い方
`member.txt`に対象のAtCoderユーザidを1行ごとに入力しておいてください。

カウントされたくないユーザがいれば`ignore.txt`に同様に入力してください。

`count_ac.py`の上部にある`contest_id`を変更してください。

実行する度にユーザidとパスワードを入力するのが手間な場合は、`MY_USER_ID`と`MY_PASSWORD`にそれぞれ入力してください。

この`README.md`があるディレクトリで`count_ac.py`を実行してください。

ユーザidとパスワードをソースコードに記入していない場合、標準入力で要求されるので入力してください。(パスワードは入力が表示されません。)

## 注意
APIの取得に間隔を設けています。そのため、(ユーザの人数)秒程度の時間がかかります。

~~コンテストの結果がAtCoder Problemsに反映されるまでに時間がかかるため、コンテスト直後は使えないかもしれません。しばらく時間を置いてから試してみてください。~~

~~(ProblemsのAPIを用いずに直接スクレイピングすればこの問題は解決できると思うので時間があれば実装してみたいです。してくれる人いれば嬉しいです。)~~

提出についてAtCoderのサイトを直接webスクレイピングするようにしました。そのため、ログイン情報が必要になりました。ログインしたくない方は前のバージョンを使用してください。

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
getpass
```
