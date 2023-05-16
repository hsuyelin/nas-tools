---
title: メッセージの送信
lang: ja-jp
slug: message-sending
order: 2
---

<div class="section-content">

リスナー関数内では、関連づけられた会話（例：リスナー実行のトリガーとなったイベントまたはアクションの発生元の会話）がある場合はいつでも `say()` を使用できます。`say()` には文字列または JSON ペイロードを指定できます。文字列の場合、送信できるのはテキストベースの単純なメッセージです。より複雑なメッセージを送信するには JSON ペイロードを指定します。指定したメッセージのペイロードは、関連づけられた会話内のメッセージとして送信されます。

リスナー関数の外でメッセージを送信したい場合や、より高度な処理（特定のエラーの処理など）を実行したい場合は、[Bolt インスタンスにアタッチされたクライアント](#web-api)の `client.chat_postMessage` を呼び出します。

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# 'knock knock' が含まれるメッセージをリッスンし、イタリック体で 'Who's there?' と返信
@app.message("knock knock")
def ask_who(message, say):
    say("_Who's there?_")
```
</div>

<details class="secondary-wrapper">
<summary markdown="0">
<h4 class="secondary-header">ブロックを用いたメッセージの送信</h4>
</summary>

<div class="secondary-content" markdown="0">
`say()` は、より複雑なメッセージペイロードを受け付けるので、メッセージに機能やリッチな構造を与えることが容易です。

リッチなメッセージレイアウトをアプリに追加する方法については、[API サイトのガイド](https://api.slack.com/messaging/composing/layouts)を参照してください。また、[Block Kit ビルダー](https://api.slack.com/tools/block-kit-builder?template=1)の一般的なアプリフローのテンプレートも見てみてください。

</div>

```python
# ユーザーが 📅 のリアクションをつけたら、日付ピッカーのついた section ブロックを送信
@app.event("reaction_added")
def show_datepicker(event, say):
    reaction = event["reaction"]
    if reaction == "calendar":
        blocks = [{
          "type": "section",
          "text": {"type": "mrkdwn", "text":"Pick a date for me to remind you"},
          "accessory": {
              "type": "datepicker",
              "action_id": "datepicker_remind",
              "initial_date":"2020-05-04",
              "placeholder": {"type": "plain_text", "text":"Select a date"}
          }
        }]
        say(
            blocks=blocks,
            text="Pick a date for me to remind you"
        )
```

</details>
