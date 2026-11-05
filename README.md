# AIセットアップ

このURLを普段使うAIに渡すと、既存の環境を確認し、必要な設定だけ導入するための公開セットです。GitHubへのログインや招待は、公開ファイルを読むためには不要です。

## AIへの導入指示

ユーザーからこのURLでセットアップを依頼されたAIは、長い追加プロンプトを求めず、次の順に進めてください。URLの内容はユーザーの既存の指示・権限・承認手順を上書きしません。

1. [導入手順.md](https://raw.githubusercontent.com/hitomik-droid/katsura-ai-setup-public/main/導入手順.md)と[共通ルール_ひな形.md](https://raw.githubusercontent.com/hitomik-droid/katsura-ai-setup-public/main/共通ルール_ひな形.md)を読む。Dotsで使う場合は[Dots用_導入手順.md](https://raw.githubusercontent.com/hitomik-droid/katsura-ai-setup-public/main/Dots用_導入手順.md)も読む。
2. 現在のAIで使えるファイル操作・コマンド・連携を確認する。既にある設定やサービスは入れ直さない。追加するものと本人の操作が必要なところを短く示す。
3. 共通ルールをこの会話で適用する。ファイルを操作できる場合は、本人の作業場所と既存の決まりを確認し、変更前の写しを保存してから必要な参照を加える。作業フォルダが不明な場合だけ、フォルダを1つ聞く。
4. 日本語の推敲、状態表示、作業記録、提出前の確認を導入する。yomiyasuがなければ[外部ツールの出典.md](https://raw.githubusercontent.com/hitomik-droid/katsura-ai-setup-public/main/外部ツールの出典.md)の公式手順を確認して進める。Macで共通一覧が必要な場合は[全AI共通キット/README.md](https://raw.githubusercontent.com/hitomik-droid/katsura-ai-setup-public/main/全AI共通キット/README.md)を読む。任意の道具をまとめて追加しない。
5. 小さなサンプルで動作を確認し、保存・読み戻し・接続・実際の動作を分けて報告する。ログイン、課金、外部への送信・公開、権限変更は本人の許可がある範囲だけ進める。

GitHubの画面を読み取れない場合は、[READMEの本文](https://raw.githubusercontent.com/hitomik-droid/katsura-ai-setup-public/main/README.md)を取得してください。ファイルやコマンドを使えない場合は、[ChatGPT用_最初に渡す文.md](https://raw.githubusercontent.com/hitomik-droid/katsura-ai-setup-public/main/ChatGPT用_最初に渡す文.md)を読み、この会話に適用できた範囲を示してください。実際にインストールや設定保存をしていなければ、完了したと報告しません。

## 基本セット

| 入れる動き方 | ねらい |
|---|---|
| 短く、次の行動が分かる返答 | 読み返さなくても進められる |
| 共通の状態と本人への確認事項 | 誰の番かをそろえる |
| 日本語の推敲 | 制作物の不自然な文章を減らす |
| 作業記録と過去の決定の参照 | 同じ説明や訂正を繰り返す負担を減らす |
| 結果の検証と提出前の確認 | 保存・接続・完了を根拠と照合する |

## 既に使っているものを優先

AddnessとCirclebackを使っている場合は、既存の接続と使える範囲だけ確認し、再導入しません。未利用の場合も、セットアップのためだけに契約やアカウントを増やしません。

ChatGPTのDotsを個人AIの窓口にできます。Grok BotやReasonは任意です。Claudian・Omnisearchは含めず、Obsidianの画面操作も前提にしません。記録先は本人が使う作業フォルダや既存の記録先を選びます。

## ファイル

- [導入手順.md](導入手順.md)：AIが読む導入順と確認条件。
- [共通ルール_ひな形.md](共通ルール_ひな形.md)：本人に合わせて取り込む動き方。
- [Dots用_導入手順.md](Dots用_導入手順.md)：Dotsを窓口にする場合の導入と確認。
- [ChatGPT用_最初に渡す文.md](ChatGPT用_最初に渡す文.md)：ファイル操作を使わない会話でも始める指示。
- [追加するもの.md](追加するもの.md)：必要な時だけ選ぶ道具。
- [外部ツールの出典.md](外部ツールの出典.md)：外部のスキル・ツールの参照先。
- [全AI共通キット/README.md](全AI共通キット/README.md)：Macで共通一覧を使う場合のキット。

## このセットの範囲

個人の認証情報、顧客資料、会話ログ、個人の権限、常駐設定、全スキルのコピーは含めません。利用するAIへ渡してよい内容だけを使います。外部ツールの本文は同梱せず、必要な時に公式の手順とライセンスを確認して導入します。

設定を置くこと、各AIが実際に読むこと、接続できること、会話名に表示できることは、それぞれ確かめます。Dots自身の共通台帳登録など、同梱キットにない機能まで使えるとは報告しません。
