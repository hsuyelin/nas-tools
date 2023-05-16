---
title: OAuth を使った認証
lang: ja-jp
slug: authenticating-oauth
order: 15
---

<div class="section-content">

Slack アプリを複数のワークスペースにインストールできるようにするためには、OAuth フローを実装した上で、アクセストークンなどのインストールに関する情報をセキュアな方法で保存する必要があります。アプリを初期化する際に `client_id`、`client_secret`、`scopes`、`installation_store`、`state_store` を指定することで、OAuth のエンドポイントのルート情報や stateパラメーターの検証をBolt for Python にハンドリングさせることができます。カスタムのアダプターを実装する場合は、SDK が提供する組み込みの[OAuth ライブラリ](https://slack.dev/python-slack-sdk/oauth/)を利用するのが便利です。これは Slack が開発したモジュールで、Bolt for Python 内部でも利用しています。

Bolt for Python によって `slack/oauth_redirect` という**リダイレクト URL** が生成されます。Slack はアプリのインストールフローを完了させたユーザーをこの URL にリダイレクトします。この**リダイレクト URL** は、アプリの設定の「**OAuth and Permissions**」であらかじめ追加しておく必要があります。この URL は、後ほど説明するように `OAuthSettings` というコンストラクタの引数で指定することもできます。

Bolt for Python は `slack/install` というルートも生成します。これはアプリを直接インストールするための「**Add to Slack**」ボタンを表示するために使われます。すでにワークスペースへのアプリのインストールが済んでいる場合に追加で各ユーザーのユーザートークンなどの情報を取得する場合や、カスタムのインストール用の URL を動的に生成したい場合などは、`oauth_settings` の `authorize_url_generator` でカスタムの URL ジェネレーターを指定することができます。

バージョン 1.1.0 以降の Bolt for Python では、[OrG 全体へのインストール](https://api.slack.com/enterprise/apps)がデフォルトでサポートされています。OrG 全体へのインストールは、アプリの設定の「**Org Level Apps**」で有効化できます。

Slack での OAuth を使ったインストールフローについて詳しくは、[API ドキュメントを参照してください](https://api.slack.com/authentication/oauth-v2)。

</div>

```python
import os
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

oauth_settings = OAuthSettings(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    scopes=["channels:read", "groups:read", "chat:write"],
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")
)

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=oauth_settings
)
```

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">OAuth デフォルト設定をカスタマイズ</h4>
</summary>

<div class="secondary-content" markdown="0">
`oauth_settings` を使って OAuth モジュールのデフォルト設定を上書きすることができます。このカスタマイズされた設定は App の初期化時に渡します。以下の情報を変更可能です:

- `install_path` : 「Add to Slack」ボタンのデフォルトのパスを上書きするために使用
- `redirect_uri` : リダイレクト URL のデフォルトのパスを上書きするために使用
- `callback_options` : OAuth フローの最後に表示するカスタムの成功ページと失敗ページの表示処理を提供するために使用
- `state_store` : 組み込みの `FileOAuthStateStore` に代わる、カスタムの stateに関するデータストアを指定するために使用
- `installation_store` : 組み込みの `FileInstallationStore` に代わる、カスタムのデータストアを指定するために使用

</div>

```python
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.response import BoltResponse

def success(args:SuccessArgs) -> BoltResponse:
    assert args.request is not None
    return BoltResponse(
        status=200,  # ユーザーをリダイレクトすることも可能
        body="Your own response to end-users here"
    )

def failure(args:FailureArgs) -> BoltResponse:
    assert args.request is not None
    assert args.reason is not None
    return BoltResponse(
        status=args.suggested_status_code,
        body="Your own response to end-users here"
    )

callback_options = CallbackOptions(success=success, failure=failure)

import os
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    oauth_settings=OAuthSettings(
        client_id=os.environ.get("SLACK_CLIENT_ID"),
        client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
        scopes=["app_mentions:read", "channels:history", "im:history", "chat:write"],
        user_scopes=[],
        redirect_uri=None,
        install_path="/slack/install",
        redirect_uri_path="/slack/oauth_redirect",
        state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states"),
        callback_options=callback_options,
    ),
)
```

</details>
