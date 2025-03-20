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

&rarr; &rarr; &rarr; MySQLやPostgreSQLでは複数スレッドや複数プロセスからの同時接続を前提に設計されているから、それらを使用する際は問題にならないそう。

```
pathlib.Path(__file__).parent.resolve()
```
- `__file__` ... 実行中のPythonファイルを指す。
- `pathlib.Path(__file__)`　... 実行中のPythonファイルのパスをPathオブジェクトとして取得する。
- `resolve()` ... 絶対パスに変換する。

[ref:\
[sqlite3 基本コマンドたち](https://qiita.com/saira/items/e08c8849cea6c3b5eb0c)\
[resolve() & absolute()](https://discuss.python.org/t/pathlib-absolute-vs-resolve/2573/3)\
[sqlite3/ check_same_thread=False](https://docs.python.org/3/library/sqlite3.html#:~:text=check_same_thread%20(bool)%20%E2%80%93%20If%20True,user%20to%20avoid%20data%20corruption.)]

### Step 7
```
docker run -v $(pwd)/data/text_en.png:/tmp/img.png wakanapo/tesseract-ocr tesseract /tmp/img.png stdout -l eng
```
- `run` ... docker containerを起動。
- `-v` ... volume / ホストマシン上のディレクトリやファイルを、コンテナ内にマウント*するためのオプション。
- `$(pwd)/data/text_en.png:/tmp/img.png` ... ホスト側のファイルパス : コンテナ側のファイルパス
- `wakanapo/tesseract-ocr` ... 使ってるimageの名前
- `tesseract /tmp/img.png` ... /tmp/img.pngの画像から文字を認識する (OCR, 光学文字認識ツール)
- ... 結果をターミナル画面に出す設定。output.txt にすればファイル出力も可能。
(*...ホストマシンのファイルやディレクトリをコンテナにリンクさせること？\
    　ホストのファイルをコンテナ内でそのままアクセスできるようにする。またdockerが管理するストレージ領域を使用する。)
simplify↓↓
```
docker run -v FILEPATH_in_HOST:PATH_in_CONTAINER IMAGE_NAME tesseract PATH_in_CONTAINER stdout -l eng
```
```
$ docker run -d -p 9000:9000 mercari-build-training/app:latest
62ad33a1d626848df63386d9281d8b4177102d0ffdac3d050c1e599f93e0833d
docker: Error response from daemon: driver failed programming external connectivity on endpoint cool_sanderson (e8b1f782463d8847ad461fd845cba21650b41d3aa9b6ad390f59b16b591d772d): Bind for 0.0.0.0:9000 failed: port is already allocated.
```
&uarr; ポート9000が既に使用されているらしい。
```
$ sudo lsof -i :9000
COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
docker-pr 33076 root    4u  IPv4 467717      0t0  TCP *:9000 (LISTEN)
docker-pr 33082 root    4u  IPv6 467722      0t0  TCP *:9000 (LISTEN)
```
&uarr; どのプロセスが使っているかを確認。これが原因でdocker runコマンドでポートの競合が発生しているよう。
```
$ docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                       NAMES
a16ccf80bd54   8b144e3d63dd   "/bin/sh -c '. /app/…"   45 minutes ago   Up 45 minutes   0.0.0.0:9000->9000/tcp, :::9000->9000/tcp   friendly_merkle
cfc473ab7219   a9ed9c431329   "/bin/sh"                2 hours ago      Up 2 hours                                                  cool_zhukovsky
```
&uarr; プロセスIDを確認。これを基に次のコマンドでコンテナを停止。（今回でいうfriendly_merkle）
```
$ docker stop friendly_merkle
friendly_merkle

$ docker run -d -p 9000:9000 mercari-build-training/app:latest
61194e959fb2116100c8db6b32424c2f3a7e61a09f5e87b7143ee512bff4fc0a
```
&uarr; いけた！！

```
RUN apk update && apk add --no-cache gcc musl-dev
```
- `apk` ... Alpine Linux のパッケージマネージャー
- `--no-cache` ... 言葉通り。イメージの容量を減らせるみたい。
- `gcc` ... Pythonの依存パッケージをビルドするときに必要
- `musl-dev` ... コンパイルに必要な開発ヘッダーが入っている\
インストールしたパッケージで動きはするものの、はて余分なものまでインストールしてしまっているのやら。

```
RUN addgroup -S mercari && adduser -S trainee -G mercari
```
- `addgroup -S` ... System Group / mercariの名でグループを作っている。
- `adduser -S trainee -G mercari` ... System User / traineeの名でシステムユーザーを作って、そのユーザーをmercariグループに所属させている。\
root userのままで動かすより、一般ユーザーとして動かすことでリスクを減らす。やらかさない。

```
RUN chown -R trainee:mercari /app
```
- `chown` ... change owner / ファイルやディレクトリの所有者とグループを変更。
- `-R` ... recurseve / 現ディレクトリ内のすべてのファイルとディレクトリに適用する。
- `trainee:mercari` ... 所有者をtrainee、グループをmercariに設定。
- `/app` ... 変更対象のフォルダ

  
### Step 8
CI / Continuous Integration / 継続的インテグレーション
... ソフトウェアの開発においてコードを頻繁に共有リポジトリにコミットする手法のこと。[(GitHub Docksより)](https://docs.github.com/ja/actions/about-github-actions/about-continuous-integration-with-github-actions) 自動的にビルドやテストを行う。

