# Claude設定（Mac）

Claudeデスクトップ（Codeタブ）に2つを入れる道具です。

| 入る物 | すること |
|---|---|
| 会話名の点検フック（`名前の点検.py`） | ターンの終わりに会話名を読み、「状態の絵文字＋案件名｜作業名」でなければ1回だけ止めて直させる |
| ADHDスキル（i-have-adhd、MITライセンス、[ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)） | 返答を「次の行動から・番号つき・脇道なし」にする。常にオンにする |

## 入れ方

1. このリポジトリを手元に置き、`python3 Claude設定/入れる.py` を動かす。何も変えずに計画だけ出る。
2. 本人が計画を見てOKなら、`python3 Claude設定/入れる.py --apply` を動かす。変更前の `~/.claude/settings.json` は `settings.json.導入前_日時.bak` として残る。
3. Claudeデスクトップを開き直す。`claude` コマンドが無い時は、Codeタブで `/plugin marketplace add ayghri/i-have-adhd` と `/plugin install i-have-adhd@i-have-adhd` を打つ。
4. 新しい会話で確かめる。名前をわざと崩してターンを終えると止まること、返答が次の行動から始まることを見る。

もう一度動かしても、入っている物は入れ直しません。

## 端末ごとに分かれる物

会話・作業の状態はその端末の中（`~/Library/Application Support/Claude/`）にだけ保存されます。このキットは会話や記録を運びません。フックもその端末の会話しか読みません。同じClaudeアカウントのクラウドの会話はアカウントに付くので、端末を分けたい時は1台につき1つのアカウントで入ります。

## しない事

認証ファイル・CLAUDE.md・AGENTS.md・Codexの設定・権限の設定には触れません。秘密の値は入っていません。
