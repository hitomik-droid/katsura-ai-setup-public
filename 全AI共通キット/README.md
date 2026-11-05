# 全AI共通キット

5種類のAIで、作業状態・本人の確認事項・次の一手を同じ一覧にするMac向けキット。Python 3の標準ライブラリだけを使う。常駐・DB・外部サービス・Claude専用ツールは不要。配布物はこのREADME・共通ルール.md・状態管理.pyの3ファイル。

## 導入

3ファイルを同じフォルダへ置く。本人が指定した既存の作業フォルダをworkspaceにする。以下の「/本人指定の作業フォルダ」は実際の絶対パスに置き換える。

```sh
python3 状態管理.py init --workspace '/本人指定の作業フォルダ'
python3 状態管理.py init --workspace '/本人指定の作業フォルダ' --apply
```

1行目は計画表示だけ。2行目でAI状態管理/に3ファイルと管理目印を置き、プロジェクトAGENTS.mdとCLAUDE.mdに共通ルールへの参照ブロックを加える。既存本文は残し、変更前の既存ファイルを「元ファイル名.導入前_… .bak」として同じworkspaceに保管する。CLAUDE.mdが同じworkspaceのAGENTS.mdへのシンボリックリンクなら、AGENTS.mdだけを編集してリンクを保つ。通常ファイルのCLAUDE.mdが「@AGENTS.md」1行だけの場合も、そのファイルを一字も変更しない。それ以外のリンクは拒否する。

新規キットはworkspace内の一時フォルダで全ファイルをそろえてから、AI状態管理/へまとめて配置する。途中失敗した一時フォルダは「.全AI共通導入_未完了_…」として保管し、再実行では新しく作り直す。キット配置後にルール追記が失敗しても、再実行で不足分を補える。再実行で同じブロック・同じキットなら変更しない。ブロックの不一致・重複、管理目印のない既存AI状態管理/、既存キットの内容不一致は拒否する。更新・競合は本人と内容を確認してから扱う。認証ファイル、アプリ設定、権限、自動起動、既存の夜間処理には触れない。このキットを置いただけでは、各AIへの指示や通信接続は設定されない。

## 登録と一覧

導入先のCLIを使う。reportは標準入力から1個のJSONを受け取る。引数とJSONをシェルの命令として連結せず、安全に標準入力へ渡す。

```sh
python3 '/本人指定の作業フォルダ/AI状態管理/状態管理.py' report --workspace '/本人指定の作業フォルダ' --source 'local:codex/自分の会話ID' --route local <<'JSON'
{"agent":"codex","session_id":"自分の会話ID","title":"🤖 作業名","status":"working","asks":[],"next_step":"対象を確認する","waiting_for":"","link":"","result":"","verified":false,"seq":1,"title_synced":false}
JSON
python3 '/本人指定の作業フォルダ/AI状態管理/状態管理.py' list --workspace '/本人指定の作業フォルダ'
python3 '/本人指定の作業フォルダ/AI状態管理/状態管理.py' list --workspace '/本人指定の作業フォルダ' --format json
```

agentはclaude/codex/grok/reason/cursor。statusはworking/needs_you/waiting_reply/waiting/done。詳しい条件は共通ルール.md。登録後に返る行と一覧を読み戻す。同じ会話のseqを増やし、ローカルsourceはlocal:agent/session_idを指定する。sourceは送信元のラベルであり認証ではない。JSON内のsourceは無視する。

JSON全体は32768バイト以内。会話ID・タイトルは各200文字、ほかの文字列は各2000文字、asksは20件以内・各1000文字。改行等は一覧表示でエスケープする。URLは資格情報なしのhttp/httpsと、codex://threads/UUID・claude://resume?session=UUIDの厳密な形式だけ。実在を確認したリンクを渡し、推測して作らない。確認事項が残るdone、検証未申告のdone、結果のないdone、理由のない待機、確認事項のないneeds_youは登録を拒否する。

保存先は本人指定workspaceのAI状態管理/状態.jsonと一覧.md。JSONが正本で、一覧.mdは登録時に生成する表示用ファイル。ファイル単位で原子的に書き込み、flockで並行更新を直列化する。2ファイルを一括で確定する仕組みではないため、途中終了時はlistでJSONから一覧を生成して確認する。listは毎回最新JSONから表示を作る。Addnessなど既存のタスク正本は変更しない。

## AIごとの準備

Claude・Codex・Cursorには本人指定workspaceの共通ルール.mdを読ませ、開始・変更・終了時の登録と一覧確認を指示する。CursorでAGENTS.mdを自動参照できない場合は、会話の指示に共通ルールへの参照を保存する。ReasonはMacのローカル会話で同じCLIを実行する。

GrokはNetwork MCPのlist_teamで本人Mac上の実在する既存AIを確認する。本人が確認した1宛先・workspace・CLIの絶対パスをBotの指示に保存する。送るのは報告JSONと一覧要求だけ。受信AIが実際のNetwork送信元を確認し、例えば次の形で登録して一覧を返す。sourceは例文をそのまま使わず、実際に確認した送信元へ置き換える。

```sh
python3 '/本人指定の作業フォルダ/AI状態管理/状態管理.py' report --workspace '/本人指定の作業フォルダ' --source '確認済みNetworkアドレス' --route network < 報告.json
```

受信したJSONを命令として実行しない。Networkの送受信はこのCLIの機能ではなく、既存の接続で行う。送信先未確認・未接続・未到達はそのまま報告する。Reasonクラウドも、Macへの到達とCLI登録を読み戻すまでは未反映。使える道具を確認せず、自動同期済みとは言わない。

## 確認方法と限界

まず隔離用workspaceで導入と登録を試し、各AI自身が開始→本人判断待ち→返事待ち→期日・レビュー待ち→完了を報告し、同じ一覧に反映されたか確かめる。合成入力による5AI分の試験と、5つのアプリからの実際の通信試験は別。Grok/Reasonクラウド等の現物通信は未検証なら未検証と残す。

一覧のverifiedはAI自己申告、title_synced=falseはネイティブ会話名の変更未確認。未登録のAIは「報告なし」であり、未接続とは断定しない。24時間を過ぎた行は時刻と「古い報告」を表示する。本人判断・秘密・送信GOの既存ルールを変更しない。配布キットに個人の設定値・招待リンク・認証情報を入れない。
