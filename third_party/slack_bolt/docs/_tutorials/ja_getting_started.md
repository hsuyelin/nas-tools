---
title: Bolt 入門ガイド
order: 0
slug: getting-started
lang: ja-jp
layout: tutorial
permalink: /ja-jp/tutorial/getting-started
redirect_from:
  - /ja-jp/getting-started
  - /getting-started/ja-jp
---
# Bolt 入門ガイド

<div class="section-content">
このガイドでは、Bolt for Python を使った Slack アプリの設定と起動する方法について説明します。ここで説明する手順は、新しい Slack アプリを作成し、ローカルの開発環境をセットアップし、Slack ワークスペースからのメッセージをリッスンして応答するアプリを開発するという流れになります。
</div>

この手順を全て終わらせたら、あなたはきっと ⚡️[Slack アプリのはじめ方](https://github.com/slackapi/bolt-python/tree/main/examples/getting_started)のサンプルアプリを動作させたり、それに変更を加えたり、自分のアプリを作ったりすることができるようになるでしょう。

> 💡 このガイドでは[ソケットモード](https://api.slack.com/apis/connections/socket) を利用します。ソケットモードは、Slack アプリ開発をとりあえず始めてみるときやあなたのチームだけのためのアプリをつくるときにおすすめのやり方です。もしすでに HTTP をアプリのコミュニケーションプロトコルとしてするとわかっているなら、HTTP の方式に対応した同様のドキュメントである [Bolt 入門ガイド（HTTP）](/bolt-python/ja-jp/tutorial/getting-started-http) を参照してください。

---

### アプリを作成する {#create-an-app}
最初にやるべきこと : Bolt での開発を始める前に、[Slack アプリを作成](https://api.slack.com/apps/new)します。

> 💡 いつもの仕事のさまたげにならないように、別の開発用のワークスペースを使用することをおすすめします。[新しいワークスペースは無料で作成できます](https://slack.com/get-started#create)。

アプリ名を入力し（_後で変更可能_）、インストール先のワークスペースを選択したら、「`Create App`」ボタンをクリックすると、アプリの **Basic Information** ページが表示されます。

このページでは、アプリの概要や、重要な認証情報も確認できます。この情報は後ほど参照します。

![Basic Information ページ](../../assets/basic-information-page.png "Basic Information ページ")

ひと通り確認し、アプリのアイコンと説明を追加したら、アプリの構成 🔩 を始めましょう。

---

### トークンとアプリのインストール {#tokens-and-installing-apps}
Slack アプリでは、[Slack API へのアクセスの管理に OAuth を使用します](https://api.slack.com/docs/oauth)。アプリがインストールされると、トークンが発行されます。アプリはそのトークンを使って API メソッドを呼び出すことができます。

Slack アプリで使用できるトークンには、ユーザートークン（`xoxp`）とボットトークン（`xoxb`）、アプリレベルトークン（`xapp`）の 3 種類があります。
- [ユーザートークン](https://api.slack.com/authentication/token-types#user) を使用すると、アプリをインストールまたは認証したユーザーに成り代わって API メソッドを呼び出すことができます。1 つのワークスペースに複数のユーザートークンが存在する可能性があります。
- [ボットトークン](https://api.slack.com/authentication/token-types#bot) はボットユーザーに関連づけられ、1 つのワークスペースでは最初に誰かがそのアプリをインストールした際に一度だけ発行されます。どのユーザーがインストールを実行しても、アプリが使用するボットトークンは同じになります。_ほとんど_のアプリで使用されるのは、ボットトークンです。
- [アプリレベルトークン](https://api.slack.com/authentication/token-types#app) は、全ての組織（とその配下のワークスペースでの個々のユーザーによるインストール）を横断して、あなたのアプリを代理するものです。アプリレベルトークンは、アプリの WebSocket コネクションを確立するためによく使われます。

このガイドではボットトークンとアプリレベルトークンを使用します。

1. 左サイドバーの「**OAuth & Permissions**」をクリックし、「**Bot Token Scopes**」セクションまで下にスクロールします。「**Add an OAuth Scope**」をクリックします。

2. ここでは [`chat:write`](https://api.slack.com/scopes/chat:write) というスコープのみを追加します。このスコープは、アプリが参加しているチャンネルにメッセージを投稿することを許可します。

3. OAuth & Permissions ページの一番上までスクロールし、「**Install App to Workspace**」をクリックします。Slack の OAuth 確認画面 が表示されます。この画面で開発用ワークスペースへのアプリのインストールを承認します。

4. インストールを承認すると **OAuth & Permissions** ページが表示され、**Bot User OAuth Access Token** を確認できるでしょう。

![OAuth トークン](../../assets/bot-token.png "ボット用 OAuth トークン")

5. 次に「**Basic Informationのページ**」まで戻り、アプリトークンのセクションまで下にスクロールし「**Generate Token and Scopes**」をクリックしてアプリレベルトークンを作成します。このトークンに `connections:write` のスコープを付与し、作成された `xapp` トークンを保存します。これらのトークンは後ほど利用します。

6. 左サイドメニューの「**Socket Mode**」を有効にします。

> 💡 トークンはパスワードと同様に取り扱い、[安全な方法で保管してください](https://api.slack.com/docs/oauth-safety)。アプリはこのトークンを使って Slack ワークスペースで投稿をしたり、情報の取得をしたりします。

---

### プロジェクトをセットアップする {#setting-up-your-project}
初期設定が終わったら、新しい Bolt プロジェクトのセットアップを行いましょう。このプロジェクトが、あなたのアプリのロジックを処理するコードを配置する場所となります。

プロジェクトをまだ作成していない場合は、新しく作成しましょう。空のディレクトリを作成します。

```shell
mkdir first-bolt-app
cd first-bolt-app
```

次に、プロジェクトの依存関係を管理する方法として、[Python 仮想環境](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)を使ったおすすめの方法を紹介します。これはシステム Python に存在するパッケージとのコンフリクトを防ぐために推奨されている優れた方法です。[Python 3.6 以降](https://www.python.org/downloads/)の仮想環境を作成し、アクティブにしてみましょう。

```shell
python3 -m venv .venv
source .venv/bin/activate
```

`python3` へのパスがプロジェクトの中を指していることを確かめることで、仮想環境がアクティブになっていることを確認できます（[Windows でもこれに似たコマンドが利用できます](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment)）。

```shell
which python3
# 出力結果 : /path/to/first-bolt-app/.venv/bin/python3
```

Bolt for Python のパッケージを新しいプロジェクトにインストールする前に、アプリの設定時に作成された **ボットトークン** と **アプリレベルトークン** を保存しましょう。

1. **OAuth & Permissions ページのボットトークン (xoxb) をコピー**して、新しい環境変数に保存します。以下のコマンド例は Linux と macOS で利用できます。[Windows でもこれに似たコマンドが利用できます](https://superuser.com/questions/212150/how-to-set-env-variable-in-windows-cmd-line/212153#212153)。
```shell
export SLACK_BOT_TOKEN=xoxb-<ボットトークン>
```

2. **Basic Information ページのアプリレベルトークン（xapp）をコピー**して、別の環境変数に保存します。
```shell
export SLACK_APP_TOKEN=<アプリレベルトークン>
```

> 🔒 全てのトークンは安全に保管してください。少なくともパブリックなバージョン管理にチェックインするようなことは避けるべきでしょう。また、上にあった例のように環境変数を介してアクセスするようにしてください。詳細な情報は [アプリのセキュリティのベストプラクティス](https://api.slack.com/authentication/best-practices)のドキュメントを参照してください。


完了したら、アプリを作ってみましょう。以下のコマンドを使って、仮想環境に Python の `slack_bolt` パッケージをインストールします。

```shell
pip install slack_bolt
```

このディレクトリに「`app.py`」という名前の新しいファイルを作成し、以下のコードを追加します。

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

このようにトークンさえあれば、最初の Bolt アプリを作成することができます。「`app.py`」ファイルを保存して、コマンドラインで以下を実行します。

```script
python3 app.py
```

アプリが起動し、実行中であることが表示されます。🎉

---

### イベントを設定する {#setting-up-events}
アプリはワークスペース内の他のメンバーと同じように振る舞い、メッセージを投稿したり、絵文字リアクションを追加したり、イベントをリッスンして返答したりできます。

Slack ワークスペースで発生するイベント（メッセージが投稿されたときや、メッセージに対するリアクションがつけられたときなど）をリッスンするには、[Events API を使って特定の種類のイベントをサブスクライブします](https://api.slack.com/events-api)。

> 💡 このチュートリアルの序盤でソケットモードを有効にしました。ソケットモードを使うことで、アプリが公開された HTTP エンドポイントを公開せずに Events API やインタラクティブコンポーネントを利用できるようになります。このことは、開発時やファイヤーウォールの裏からのリクエストを受ける際に便利です。HTTP での方式はホスティング環境にデプロイするアプリや Slack App Directoryで配布されるアプリに適しています。HTTP での情報については[このドキュメント](/bolt-python/ja-jp/tutorial/getting-started-http)を参照してください。

それでは、私たちがどのイベントをリッスンしたいかを Slack に伝えましょう。

イベントが発生すると、そのイベントをトリガーしたユーザーやイベントが発生したチャンネルなど、イベントに関する情報が Slack からアプリに送信されます。アプリではこれらの情報を処理して、適切な応答を返します。

左側のサイドバーから **Event Subscriptions** にアクセスして、機能を有効にしてください。 **Subscribe to Bot Events** 配下で、ボットが受け取れる　イベントを追加することができます。4つのメッセージに関するイベントがあります。
- [`message.channels`](https://api.slack.com/events/message.channels) アプリが参加しているパブリックチャンネルのメッセージをリッスン
- [`message.groups`](https://api.slack.com/events/message.groups) アプリが参加しているプライベートチャンネルのメッセージをリッスン
- [`message.im`](https://api.slack.com/events/message.im) あなたのアプリとユーザーのダイレクトメッセージをリッスン
- [`message.mpim`](https://api.slack.com/events/message.mpim) あなたのアプリが追加されているグループ DM をリッスン

ボットが参加するすべての場所のメッセージをリッスンさせるには、これら 4 つのメッセージイベントをすべて選択します。ボットにリッスンさせるメッセージイベントの種類を選択したら、「**Save Changes**」ボタンをクリックします。

---

### メッセージをリッスンして応答する {#listening-and-responding-to-a-message}
アプリにロジックを組み込む準備が整いました。まずは `message()` メソッドを使用して、メッセージのリスナーをアタッチしましょう。

次の例では、アプリが参加するチャンネルとダイレクトメッセージに投稿されるすべてのメッセージをリッスンし、「hello」というメッセージに応答を返します。

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 'hello' を含むメッセージをリッスンします
# 指定可能なリスナーのメソッド引数の一覧は以下のモジュールドキュメントを参考にしてください：
# https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("hello")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    say(f"Hey there <@{message['user']}>!")

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

アプリを再起動し、ボットユーザーが参加しているチャンネルまたはダイレクトメッセージに「hello」というメッセージを投稿すれば、アプリが応答するでしょう。

これはごく基本的なコード例ですが、最終的にやりたいことを実現するためにアプリをカスタマイズするための起点として利用できます。プレーンテキストを送信する代わりにボタンを表示するという、もう少しインタラクティブな動作を試してみましょう。

---

### アクションを送信して応答する {#sending-and-responding-to-actions}

インタラクティブ機能を有効にすると、ボタン、選択メニュー、日付ピッカー、モーダル、ショートカットなどの機能が利用できるようになります。アプリ設定ページの「**Interactivity & Shortcuts**」にアクセスしてください。

> 💡 ソケットモードを有効にしているとき、デフォルトで基本的なインタラクティブ機能が有効になっていることに気づくでしょう。追加のアクションは不要です。もし HTTP を使っている場合、Slack からのイベント送信先である Request URL を設定する必要があります。

インタラクティビティが有効化されていれば、ショートカット、モーダル、インタラクティブコンポーネント (例：ボタン、選択メニュー、日付ピッカー) とのインタラクションはイベントとしてあなたのアプリに送信されます。

それでは、アプリのコードに戻り、これらのイベントを処理する為のロジックを追加しましょう。
- まず、インタラクティブコンポーネント（ここではボタン）を含んだメッセージをアプリから送信します。
- 次に、ユーザーから返されるボタンクリックのアクションをリッスンし、それに応答します。

以下のコードの後の部分を編集し、文字列だけのメッセージの代わりに、ボタンを含んだメッセージを送信するようにしてみます。

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 'hello' を含むメッセージをリッスンします
@app.message("hello")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text":"Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

`say()` の中の値を `blocks` という配列のオブジェクトに変えました。ブロックは Slack メッセージを構成するコンポーネントであり、テキストや画像、日付ピッカーなど、さまざまなタイプのブロックがあります。この例では `accessory` に `button` を持たせた「section」のブロックを、アプリからの応答に含めています。`blocks` を使用する場合、`text` は通知やアクセシビリティのためのフォールバックとなります。

ボタンを含む `accessory` オブジェクトでは、`action_id` を指定していることがわかります。これは、ボタンを一意に示す識別子として機能します。これを使って、アプリをどのアクションに応答させるかを指定できます。

> 💡 [Block Kit Builder](https://app.slack.com/block-kit-builder) を使用すると、インタラクティブなメッセージのプロトタイプを簡単に作成できます。自分自身やチームメンバーがメッセージのモックアップを作成し、生成される JSON をアプリに直接貼りつけることができます。

アプリを再起動し、アプリが参加しているチャンネルで「hello」と入力すると、ボタン付きのメッセージが表示されるようになりました。ただし、ボタンをクリックしても、*まだ*何も起こりません。

ハンドラーを追加して、ボタンがクリックされたときにフォローアップメッセージを送信するようにしてみましょう。

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンと署名シークレットを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 'hello' を含むメッセージをリッスンします
@app.message("hello")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text":"Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )

@app.action("button_click")
def action_button_click(body, ack, say):
    # アクションを確認したことを即時で応答します
    ack()
    # チャンネルにメッセージを投稿します
    say(f"<@{body['user']['id']}> clicked the button")

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

`app.action()` を使って、先ほど命名した `button_click` という `action_id` をリッスンしています。アプリを再起動し、ボタンをクリックすると、アプリからの「clicked the button」というメッセージが新たに表示されるでしょう。

---

### 次のステップ {#next-steps}
はじめての [Bolt for Python アプリ](https://github.com/slackapi/bolt-python/tree/main/examples/getting_started)をソケットモードを使って構築することができました。🎉

ここまでで基本的なアプリをセットアップして実行することはできたので、次は自分だけの Bolt アプリを作る方法を調べてみましょう。参考になりそうな記事をいくつかご紹介します。

* [基本的な概念](/bolt-python/ja-jp/concepts#basic)について読んでみてください。Bolt アプリがアクセスできるさまざまメソッドや機能について知ることができます。
* [`events()` メソッド](/bolt-python/ja-jp/concepts#event-listening)でボットがリッスンできるイベントをほかにも試してみましょう。すべてのイベントの一覧は [API サイト](https://api.slack.com/events)で確認できます。
* Bolt では、アプリにアタッチされたクライアントから [Web API メソッドを呼び出す](/bolt-python/ja-jp/concepts#web-api)ことができます。API サイトに [220 以上のメソッド](https://api.slack.com/methods)を一覧しています。
* [API サイト](https://api.slack.com/docs/token-types)でほかのタイプのトークンを確認してみてください。アプリで実行したいアクションによって、異なるトークンが必要になる場合があります。ソケットモードを使わないアプリでは、通常はボットトークン (`xoxb`) と署名シークレットが必要です。ソケットモードを使わない場合の例については、 HTTP 方式のやり方としてこのチュートリアルと対になっている [Bolt 入門ガイド（HTTP）](/bolt-python/ja-jp/tutorial/getting-started-http)を参照してください。
