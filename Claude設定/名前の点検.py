#!/usr/bin/env python3
"""Claudeデスクトップ（Codeタブ）の会話名を、ターンの終わりに点検するStopフック。

決まり：このキットの 会話名と改名.md
- 形は「状態の絵文字＋案件名｜作業名」。【フォルダ】は付けない。
- 形が違えば1回だけ止めて、set_session_title（session_id は self）で直させる。
- デスクトップアプリの会話でなければ（CLI・Codex・ほかの端末の物）何もしない。
- 読むのはこの端末の記録だけ。ほかの端末の会話には触れない。
"""
import json
import os
import sys
import time
from pathlib import Path

EMOJIS = ("🔴", "🩷", "🤖", "💬", "⏸️", "⏸", "✅")
RECORDS = Path.home() / "Library/Application Support/Claude/claude-code-sessions"
RULE = "https://github.com/hitomik-droid/katsura-ai-setup-public/blob/main/会話名と改名.md"


def find_record(cli_id: str):
    if not cli_id or not RECORDS.is_dir():
        return None
    needle = cli_id.encode()
    files = sorted(RECORDS.glob("*/*/local_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    cutoff = time.time() - 3 * 86400
    for path in files:
        try:
            if path.stat().st_mtime < cutoff:
                break
            raw = path.read_bytes()
        except OSError:
            continue
        if needle not in raw:
            continue
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        if cli_id in (rec.get("cliSessionId"), rec.get("lastAssistantCliSessionId")):
            return rec
    return None


def problems(title: str):
    out = []
    head = next((e for e in EMOJIS if title.startswith(e)), None)
    if head is None:
        out.append("先頭に状態の絵文字（🔴🩷🤖💬⏸️✅のどれか1つ）が無い")
    if "【" in title or "】" in title:
        out.append("【フォルダ】が付いている（今は付けない）")
    if "｜" not in title:
        out.append("「案件名｜作業名」の全角｜が無い")
    if head == "🤖":
        out.append("ターンを終えるのに🤖（作業中）のまま。裏で作業が続いている時だけ🤖でよい")
    return out


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if data.get("stop_hook_active"):
        return 0
    rec = find_record(data.get("session_id", ""))
    if not rec or rec.get("scheduledTaskId") or rec.get("isArchived"):
        return 0
    title = (rec.get("title") or "").strip()
    found = problems(title)
    if not found:
        return 0
    reason = (
        f"会話名が決まりの形ではありません（今の名前：{title or '無し'}）。"
        + "／".join(found)
        + "。終える前に set_session_title（session_id は self）で「状態の絵文字＋案件名｜作業名」に直し、"
        "get_session（self）で読み戻してください。絵文字は🔴本人の番／🩷2人で使う時のもう1人の番／🤖作業中／💬ほかの人の返事待ち／⏸️待機中／✅終わった。"
        "頼み事を送ってから返事が来るまでは名前を変えない（その時は直さずに終えてよい）。"
        f"決まりの全文：{RULE}"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
