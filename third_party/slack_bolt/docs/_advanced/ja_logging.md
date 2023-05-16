---
title: ロギング
lang: ja-jp
slug: logging
order: 4
---

<div class="section-content">
デフォルトでは、アプリからのログ情報は、既定の出力先に出力されます。`logging` モジュールをインポートすれば、`basicConfig()` の `level` パラメーターでrootのログレベルを変更することができます。指定できるログレベルは、重要度の低い方から `debug`、`info`、`warning`、`error`、および `critical` です。 

グローバルのコンテキストとは別に、指定のログレベルに応じて単一のメッセージをログ出力することもできます。Bolt では [Python 標準の logging モジュール](https://docs.python.org/3/library/logging.html)が使われているため、このモジュールが持つすべての機能を利用できます。
</div>

```python
import logging

# グローバルのコンテキストの logger です
# logging をインポートする必要があります
logging.basicConfig(level=logging.DEBUG)

@app.event("app_mention")
def handle_mention(body, say, logger):
    user = body["event"]["user"]
    # 単一の logger の呼び出しです
    # グローバルの logger がリスナーに渡されています
    logger.debug(body)
    say(f"{user} mentioned your app")
```
