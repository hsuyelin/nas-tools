---
title: 認可（Authorization）
lang: ja-jp
slug: authorization
order: 5
---

<div class="section-content">
認可（Authorization）は、Slack からの受信リクエストを処理するにあたって、どのようなSlack
クレデンシャル (ボットトークンなど) を使用可能にするかを決定するプロセスです。

単一のワークスペースにインストールされるアプリでは、`token` パラメーターを使って `App` のコンストラクターにボットトークンを渡すという、シンプルな方法が使えます。それに対して、複数のワークスペースにインストールされるアプリでは、次の 2 つの方法のいずれかを使用する必要があります。簡単なのは、組み込みの OAuth サポートを使用する方法です。OAuth サポートは、OAuth フロー用のURLのセットアップとstateの検証を行います。詳細は「[OAuth を使った認証](#authenticating-oauth)」セクションを参照してください。

よりカスタマイズできる方法として、`App` をインスタンス化する関数に`authorize` パラメーターを指定する方法があります。`authorize` 関数から返される [`AuthorizeResult` のインスタンス](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/authorization/authorize_result.py)には、どのユーザーがどこで発生させたリクエストかを示す情報が含まれます。

`AuthorizeResult` には、いくつか特定のプロパティを指定する必要があり、いずれも `str` 型です。


- **`bot_token`**（xoxb）*または* **`user_token`**（xoxp）: どちらか一方が**必須**です。ほとんどのアプリでは、デフォルトの `bot_token` を使用すればよいでしょう。トークンを渡すことで、`say()` などの組み込みの関数を機能させることができます。
- **`bot_user_id`** および **`bot_id`** : `bot_token` を使用する場合に指定します。
- **`enterprise_id`** および **`team_id`** : アプリに届いたリクエストから見つけることができます。
- **`user_id`** : `user_token` を使用する場合に必須です。
</div>

```python
import os
from slack_bolt import App
# AuthorizeResult クラスをインポートします
from slack_bolt.authorization import AuthorizeResult

# これはあくまでサンプル例です（ユーザートークンがないことを想定しています）
# 実際にはセキュアな DB に認可情報を保存してください
installations = [
    {
      "enterprise_id":"E1234A12AB",
      "team_id":"T12345",
      "bot_token": "xoxb-123abc",
      "bot_id":"B1251",
      "bot_user_id":"U12385"
    },
    {
      "team_id":"T77712",
      "bot_token": "xoxb-102anc",
      "bot_id":"B5910",
      "bot_user_id":"U1239",
      "enterprise_id":"E1234A12AB"
    }
]

def authorize(enterprise_id, team_id, logger):
    # トークンを取得するためのあなたのロジックをここに記述します
    for team in installations:
        # 一部のチームは enterprise_id を持たない場合があります
        is_valid_enterprise = True if (("enterprise_id" not in team) or (enterprise_id == team["enterprise_id"])) else False
        if ((is_valid_enterprise == True) and (team["team_id"] == team_id)):
          # AuthorizeResult のインスタンスを返します
          # bot_id と bot_user_id を保存していない場合、bot_token を使って `from_auth_test_response` を呼び出すと、自動的に取得できます
          return AuthorizeResult(
              enterprise_id=enterprise_id,
              team_id=team_id,
              bot_token=team["bot_token"],
              bot_id=team["bot_id"],
              bot_user_id=team["bot_user_id"]
          )

    logger.error("No authorization information was found")

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    authorize=authorize
)
```
