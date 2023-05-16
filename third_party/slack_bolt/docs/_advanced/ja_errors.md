---
title: エラーの処理
lang: ja-jp
slug: errors
order: 3
---

<div class="section-content">
リスナー内でエラーが発生した場合に try/except ブロックを使用して直接エラーを処理することができます。アプリに関連するエラーは、`BoltError` 型です。Slack API の呼び出しに関連するエラーは、`SlackApiError` 型となります。

デフォルトでは、すべての処理されなかった例外のログはグローバルのエラーハンドラーによってコンソールに出力されます。グローバルのエラーを開発者自身で処理するには、`app.error(fn)` 関数を使ってグローバルのエラーハンドラーをアプリに設定します。
</div>

```python
@app.error
def custom_error_handler(error, body, logger):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")
```