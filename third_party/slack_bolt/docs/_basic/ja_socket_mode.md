---
title: ソケットモードの利用
lang: ja-jp
slug: socket-mode
order: 16
---

<div class="section-content">
[ソケットモード](https://api.slack.com/apis/connections/socket)は、アプリに WebSocket での接続と、そのコネクション経由でのデータ受信を可能とします。Bolt for Python は、バージョン 1.2.0 からこれに対応しています。

ソケットモードでは、Slack からのペイロード送信を受け付けるエンドポイントをホストする HTTP サーバーを起動する代わりに WebSocket で Slack に接続し、そのコネクション経由でデータを受信します。ソケットモードを使う前に、アプリの管理画面でソケットモードの機能が有効になっていることを確認しておいてください。

ソケットモードを使用するには、環境変数に `SLACK_APP_TOKEN` を追加します。アプリのトークン（App-Level Token）は、アプリの設定の「**Basic Information**」セクションで確認できます。 

[組み込みのソケットモードアダプター](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/builtin)を使用するのがおすすめですが、サードパーティ製ライブラリを使ったアダプターの実装もいくつか存在しています。利用可能なアダプターの一覧です。

|内部的に利用する PyPI プロジェクト名|Bolt アダプター|
|-|-|
|[slack_sdk](https://pypi.org/project/slack-sdk/)|[slack_bolt.adapter.socket_mode](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/builtin)|
|[websocket_client](https://pypi.org/project/websocket_client/)|[slack_bolt.adapter.socket_mode.websocket_client](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/websocket_client)|
|[aiohttp](https://pypi.org/project/aiohttp/) (asyncio-based)|[slack_bolt.adapter.socket_mode.aiohttp](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/aiohttp)|
|[websockets](https://pypi.org/project/websockets/) (asyncio-based)|[slack_bolt.adapter.socket_mode.websockets](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/websockets)|

</div>

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 事前に Slack アプリをインストールし 'xoxb-' で始まるトークンを入手
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# ここでミドルウェアとリスナーの追加を行います

if __name__ == "__main__":
    # export SLACK_APP_TOKEN=xapp-***
    # export SLACK_BOT_TOKEN=xoxb-***
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

<details class="secondary-wrapper">
<summary markdown="0">
<h4 class="secondary-header">Async (asyncio) の利用</h4>
</summary>

<div class="secondary-content" markdown="0">
aiohttp のような asyncio をベースとしたアダプターを使う場合、アプリケーション全体が asyncio の async/await プログラミングモデルで実装されている必要があります。`AsyncApp` を動作させるためには `AsyncSocketModeHandler` とその async なミドルウェアやリスナーを利用します。

`AsyncApp` の使い方についての詳細は、[Async (asyncio) の利用](https://slack.dev/bolt-python/ja-jp/concepts#async)や、関連する[サンプルコード例](https://github.com/slackapi/bolt-python/tree/main/examples)を参考にしてください。
</div>

```python
from slack_bolt.app.async_app import AsyncApp
# デフォルトは aiohttp を使った実装
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

# ここでミドルウェアとリスナーの追加を行います

async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

</details>
