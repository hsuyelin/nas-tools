---
title: カスタムのアダプター
lang: ja-jp
slug: custom-adapters
order: 1
---

<div class="section-content">
[アダプター](#adapters)はフレキシブルで、あなたが使用したいフレームワークに合わせた調整も可能です。アダプターでは、次の 2 つの要素が必須となっています。

- `__init__(app:App)` : コンストラクター。Bolt の `App` のインスタンスを受け取り、保持します。
- `handle(req:Request)` : Slack からの受信リクエストを受け取り、解析を行う関数。通常は `handle()` という名前です。リクエストを [`BoltRequest`](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/request/request.py) のインスタンスに合った形にして、保持している Bolt アプリに引き渡します。

`BoltRequest` のインスタンスの作成では、以下の 4 種類のパラメーターを指定できます。

| パラメーター | 説明 | 必須 |
|-----------|-------------|-----------|
| `body: str` | そのままのリクエストボディ | **Yes** |
| `query: any` | クエリストリング | No |
| `headers:Dict[str, Union[str, List[str]]]` | リクエストヘッダー | No |
| `context:BoltContext` | リクエストのコンテキスト情報 | No |

アダプターは、Bolt アプリからの [`BoltResponse` のインスタンス](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/response/response.py)を返します。

カスタムのアダプターに関連した詳しいサンプルについては、[組み込みのアダプター](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter)の実装を参考にしてください。
</div>

```python
# Flask で必要なパッケージをインポートします
from flask import Request, Response, make_response

from slack_bolt.app import App
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse

# この例は Flask アダプターを簡略化したものです
# もう少し詳しい完全版のサンプルは、adapter フォルダをご覧ください
# github.com/slackapi/bolt-python/blob/main/slack_bolt/adapter/flask/handler.py

# HTTP リクエストを取り込み、標準の BoltRequest に変換します
def to_bolt_request(req:Request) -> BoltRequest:
    return BoltRequest(
        body=req.get_data(as_text=True),
        query=req.query_string.decode("utf-8"),
        headers=req.headers,
    )

# BoltResponse を取り込み、標準の Flask レスポンスに変換します
def to_flask_response(bolt_resp:BoltResponse) -> Response:
    resp:Response = make_response(bolt_resp.body, bolt_resp.status)
    for k, values in bolt_resp.headers.items():
        for v in values:
            resp.headers.add_header(k, v)
    return resp

# アプリからインスタンス化します
# Flask アプリを受け取ります
class SlackRequestHandler:
    def __init__(self, app:App):
        self.app = app

    # Slack からリクエストが届いたときに
    # Flask アプリの handle() を呼び出します
    def handle(self, req:Request) -> Response:
        # この例では OAuth に関する部分は扱いません
        if req.method == "POST":
            # Bolt へのリクエストをディスパッチし、処理とルーティングを行います
            bolt_resp:BoltResponse = self.app.dispatch(to_bolt_request(req))
            return to_flask_response(bolt_resp)

        return make_response("Not Found", 404)
```
