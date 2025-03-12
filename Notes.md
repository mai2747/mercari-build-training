# Build@Mercari Notes

This is a record of the things I notice while working on tasks and the commands I use.\
使ったコマンドと気づいたことの覚え書きをメインに残していくつもりです。

\- **Prep before using Python/Go** -
1. Launch Ubuntu
2. Activate the virtual environment

```
$ cd mercari-build-training/python
$ source .venv/bin/activate
```

### Step 4-1
```
$ uvicorn main:app --reload --port 9000
```
- `uvicorn` ... Pythonの ASGI (Asynchronous Server Gateway Interface) サーバー //SGIアプリケーションを実行するためのサーバー
- `main:app` ... main.py/app (FastAPIアプリ) を起動


```
$ curl -X GET 'http://127.0.0.1:9000'
```
- `-X` ... リクエストの種類の指定　（GET等）
- `GET` ... データ取得のリクエスト


```
$ curl -X POST --url 'http://localhost:9000/items' -d 'name=jacket'
```
- 'POST' ...　データ送信・作成のリクエスト
- '-d' ... POSTで指定の文字列データを送信する


[ref:\
[request (-X)](https://curl.se/docs/manpage.html#-X)\
[get (-G)](https://curl.se/docs/manpage.html#-G)\
[How to Send GET Requests With cURL](https://crawlbase.com/blog/how-to-send-get-requests-with-curl/#:~:text=A%20cURL%20GET%20request%20is,interaction%2C%20and%20testing%20web%20resources.)\
[コマンドまとめ](https://qiita.com/ryuichi1208/items/e4e1b27ff7d54a66dcd9)]

### Step 5
```
sqlite3.cennect().cursor()
```
- `cennect()` ... SQLiteデータベースへの接続を確立。データベースへのファイルパスを引数に。（なければ新規作成される）
- `cursor()` ... データベースでSQL文を実行するための「カーソルオブジェクト」を取得。データの取得、挿入、更新、削除などのSQL操作等。

```
cursor.fetchall()
```
- `fetchall()` ... SQLクエリを実行した結果すべてを取得。

```
sqlite3.connect(db, check_same_thread=False)
```
- `check_same_thread=False` ... 異なるスレッドからも接続を使えるようにする。もともと、SQLiteはデフォルトで、同じスレッドからのみデータベース接続を使用することを要求する。今回はエラー回避用に使ったけれど、根本解決する方法はあるのだろうか…。

```
pathlib.Path(__file__).parent.resolve()
```
- `__file__` ... 実行中のPythonファイルを指す。
- `pathlib.Path(__file__)`　... 実行中のPythonファイルのパスをPathオブジェクトとして取得する。
- `resolve()` ... 絶対パスに変換する。

[ref:\
[sqlite3 基本コマンドたち](https://qiita.com/saira/items/e08c8849cea6c3b5eb0c)]
