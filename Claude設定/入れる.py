#!/usr/bin/env python3
"""Claudeデスクトップ（Mac）に、会話名の点検フックとADHDスキルを入れる。

使い方:
  python3 入れる.py            # 計画を表示するだけ（何も変えない）
  python3 入れる.py --apply    # 入れる。変更前の settings.json は .bak に写して残す

すること（--apply の時）:
  1. 名前の点検.py を ~/.claude/katsura-hooks/ に写す
  2. ~/.claude/settings.json の hooks.Stop に名前の点検を1つ足す（同じ物があれば足さない）
  3. ADHDスキル（i-have-adhd、MITライセンス、github.com/ayghri/i-have-adhd）を
     settings.json の extraKnownMarketplaces と enabledPlugins に足す
  4. ~/.claude/.i-have-adhd-always を置く（ADHDスキルを常にオンにする目印）
  5. claude コマンドがあれば、ADHDスキルを入れる命令も動かす

しない事: 認証ファイル・CLAUDE.md・AGENTS.md・Codexの設定・権限の設定には触れない。
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
CLAUDE = HOME / ".claude"
SETTINGS = CLAUDE / "settings.json"
HOOK_DIR = CLAUDE / "katsura-hooks"
HOOK_SRC = Path(__file__).resolve().parent / "名前の点検.py"
HOOK_DST = HOOK_DIR / "名前の点検.py"
ADHD_FLAG = CLAUDE / ".i-have-adhd-always"
HOOK_CMD = (
    "/bin/sh -c 'F=\"$HOME/.claude/katsura-hooks/名前の点検.py\"; [ -f \"$F\" ] || exit 0; "
    "PY=/opt/homebrew/bin/python3; [ -x \"$PY\" ] || PY=python3; exec \"$PY\" \"$F\"'"
)
MARKET = {"source": {"source": "github", "repo": "ayghri/i-have-adhd"}}
PLUGIN = "i-have-adhd@i-have-adhd"


def load_settings():
    if not SETTINGS.exists():
        return {}
    return json.loads(SETTINGS.read_text(encoding="utf-8"))


def has_hook(settings):
    for group in settings.get("hooks", {}).get("Stop", []):
        for hook in group.get("hooks", []):
            if "名前の点検.py" in hook.get("command", ""):
                return True
    return False


def plan(settings):
    steps = []
    if not HOOK_DST.exists() or HOOK_DST.read_bytes() != HOOK_SRC.read_bytes():
        steps.append(f"名前の点検.py を {HOOK_DST} に写す")
    if not has_hook(settings):
        steps.append("settings.json の hooks.Stop に名前の点検を足す")
    if settings.get("extraKnownMarketplaces", {}).get("i-have-adhd") != MARKET:
        steps.append("settings.json の extraKnownMarketplaces に i-have-adhd を足す")
    if settings.get("enabledPlugins", {}).get(PLUGIN) is not True:
        steps.append(f"settings.json の enabledPlugins で {PLUGIN} をオンにする")
    if not ADHD_FLAG.exists():
        steps.append(f"{ADHD_FLAG} を置く（ADHDスキルを常にオン）")
    return steps


def apply(settings):
    stamp = time.strftime("%Y%m%d%H%M%S")
    if SETTINGS.exists():
        backup = SETTINGS.with_name(f"settings.json.導入前_{stamp}.bak")
        shutil.copy2(SETTINGS, backup)
        print(f"写しを残した: {backup}")
    HOOK_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HOOK_SRC, HOOK_DST)
    if not has_hook(settings):
        settings.setdefault("hooks", {}).setdefault("Stop", []).append(
            {"hooks": [{"type": "command", "command": HOOK_CMD, "timeout": 10}]}
        )
    settings.setdefault("extraKnownMarketplaces", {})["i-have-adhd"] = MARKET
    settings.setdefault("enabledPlugins", {})[PLUGIN] = True
    tmp = SETTINGS.with_name("settings.json.書き込み中")
    tmp.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(tmp.read_text(encoding="utf-8"))
    tmp.replace(SETTINGS)
    ADHD_FLAG.touch()
    claude = shutil.which("claude")
    if claude:
        for args in (["plugin", "marketplace", "add", "ayghri/i-have-adhd"], ["plugin", "install", PLUGIN]):
            result = subprocess.run([claude, *args], capture_output=True, text=True)
            print(f"claude {' '.join(args)} → 終了コード {result.returncode}")
    else:
        print("claude コマンドが無いので、Codeタブで次の2つを打つ:")
        print("  /plugin marketplace add ayghri/i-have-adhd")
        print(f"  /plugin install {PLUGIN}")


def self_test():
    sample = {"session_id": "存在しない会話", "stop_hook_active": False}
    result = subprocess.run(
        [sys.executable, str(HOOK_DST)], input=json.dumps(sample), capture_output=True, text=True
    )
    return result.returncode == 0 and result.stdout.strip() == ""


def main():
    if sys.platform != "darwin":
        print("Mac用です。ほかのOSでは何も変えずに止めます。")
        return 1
    settings = load_settings()
    steps = plan(settings)
    if not steps:
        print("入れる物はありません（もう入っています）。")
        return 0
    print("入れる物:")
    for step in steps:
        print(f"- {step}")
    if "--apply" not in sys.argv:
        print("まだ何も変えていません。入れる時は --apply を付けて動かします。")
        return 0
    apply(settings)
    left = plan(load_settings())
    print("読み戻し: " + ("全部入った" if not left else "残り " + " / ".join(left)))
    print("フックの空うち試験: " + ("通った" if self_test() else "失敗"))
    print("Claudeデスクトップを開き直すと効きます。")
    return 0 if not left else 1


if __name__ == "__main__":
    sys.exit(main())
