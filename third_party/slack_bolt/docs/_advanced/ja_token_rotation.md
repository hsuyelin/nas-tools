---
title: トークンのローテーション
lang: ja-jp
slug: token-rotation
order: 6
---

<div class="section-content">
Bolt for Python [v1.7.0](https://github.com/slackapi/bolt-python/releases/tag/v1.7.0) から、アクセストークンのさらなるセキュリティ強化のレイヤーであるトークンローテーションの機能に対応しています。トークンローテーションは [OAuth V2 の RFC](https://datatracker.ietf.org/doc/html/rfc6749#section-10.4) で規定されているものです。

既存の Slack アプリではアクセストークンが無期限に存在し続けるのに対して、トークンローテーションを有効にしたアプリではアクセストークンが失効するようになります。リフレッシュトークンを利用して、アクセストークンを長期間にわたって更新し続けることができます。

[Bolt for Python の組み込みの OAuth 機能](https://slack.dev/bolt-python/ja-jp/concepts#authenticating-oauth) を使用していれば、Bolt for Python が自動的にトークンローテーションの処理をハンドリングします。

トークンローテーションに関する詳細は [API ドキュメント](https://api.slack.com/authentication/rotation)を参照してください。
</div>
