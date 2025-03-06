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
- `GET` ... データ取得のリクエスト\


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
