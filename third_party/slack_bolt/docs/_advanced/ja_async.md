---
title: Async（asyncio）の使用
lang: ja-jp
slug: async
order: 2
---

<div class="section-content">
非同期バージョンの Bolt を使用する場合は、`App` の代わりに `AsyncApp` インスタンスをインポートして初期化します。`AsyncApp` では <a href="https://docs.aiohttp.org/">AIOHTTP</a> を使って API リクエストを行うため、`aiohttp` をインストールする必要があります（`requirements.txt` に追記するか、`pip install aiohttp` を実行します）。

非同期バージョンのプロジェクトのサンプルは、リポジトリの <a href="https://github.com/slackapi/bolt-python/tree/main/examples">`examples` フォルダ</a>にあります。
</div>

```python
# aiohttp のインストールが必要です
from slack_bolt.async_app import AsyncApp
app = AsyncApp()

@app.event("app_mention")
async def handle_mentions(event, client, say):  # 非同期関数
    api_response = await client.reactions_add(
        channel=event["channel"],
        timestamp=event["ts"],
        name="eyes",
    )
    await say("What's up?")

if __name__ == "__main__":
    app.start(3000)
```

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">他のフレームワークを使用する</h4>
</summary>

<div class="secondary-content" markdown="0">

`AsyncApp#start()` では内部的に [`AIOHTTP`](https://docs.aiohttp.org/) のWebサーバーが実装されています。必要に応じて、受信リクエストの処理に `AIOHTTP` 以外のフレームワークを使用することができます。

この例では [Sanic](https://sanicframework.org/) を使用しています。すべてのアダプターのリストについては、[`adapter` フォルダ](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter) を参照してください。

以下のコマンドを実行すると、必要なパッケージをインストールして、Sanic サーバーをポート 3000 で起動します。

```bash
# 必要なパッケージをインストールします
pip install slack_bolt sanic uvicorn
# ソースファイルを async_app.py として保存します
uvicorn async_app:api --reload --port 3000 --log-level debug
```
</div>

```python
from slack_bolt.async_app import AsyncApp
app = AsyncApp()

# ここには Sanic に固有の記述はありません
# AsyncApp はフレームワークやランタイムに依存しません
@app.event("app_mention")
async def handle_app_mentions(say):
    await say("What's up?")

import os
from sanic import Sanic
from sanic.request import Request
from slack_bolt.adapter.sanic import AsyncSlackRequestHandler

# App のインスタンスから Sanic 用のアダプターを作成します
app_handler = AsyncSlackRequestHandler(app)
# Sanic アプリを作成します
api = Sanic(name="awesome-slack-app")

@api.post("/slack/events")
async def endpoint(req: Request):
    # app_handler では内部的にアプリのディスパッチメソッドが実行されます
    return await app_handler.handle(req)

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
```
</details>
