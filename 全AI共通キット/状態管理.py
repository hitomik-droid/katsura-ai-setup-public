#!/usr/bin/env python3
"""Mac用・標準ライブラリだけの全AI共通状態CLI。JSONはデータとしてのみ扱う。"""
import argparse
import contextlib
import datetime as dt
import fcntl
import html
import json
import os
import re
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlsplit

AGENTS = ('claude', 'codex', 'grok', 'reason', 'cursor')
STATUS = {'working': '🤖 作業中', 'needs_you': '🔴 本人判断待ち', 'waiting_reply': '💬 返事待ち', 'waiting': '⏸️ 期日・レビュー待ち', 'done': '✅ 完了'}
DIR = 'AI状態管理'
MARKER = '全AI共通キット-v1'
BEGIN = '<!-- 全AI共通状態:開始 -->'
END = '<!-- 全AI共通状態:終了 -->'
BLOCK = BEGIN + '\n全AI共通の状態・確認事項は `AI状態管理/共通ルール.md` を読み、開始・状態変更・終了時に同フォルダの `状態管理.py` で登録・一覧取得する。既存の承認・送信・秘密保持ルールを優先する。\n' + END
FIELDS = {'agent','session_id','title','status','asks','next_step','waiting_for','link','result','verified','seq','title_synced'}

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def existing_workspace(value):
    p = Path(value).expanduser().resolve()
    if not p.is_dir():
        raise ValueError('workspaceは本人が指定した既存フォルダが必要')
    return p

def safe_file(p):
    if p.is_symlink() or (p.exists() and not p.is_file()):
        raise ValueError('リンクまたは通常ファイル以外への書込みを拒否: ' + p.name)

def atomic(p, value):
    safe_file(p)
    fd, name = tempfile.mkstemp(prefix='一時_', dir=p.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(value)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, p)
    finally:
        if os.path.exists(name):
            os.unlink(name)

@contextlib.contextmanager
def lock(p):
    safe_file(p)
    with p.open('a', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield

def managed(ws):
    p = ws / DIR
    if p.is_symlink() or not p.is_dir():
        raise ValueError('先にinit --applyで導入する')
    marker = p / '管理目印.txt'
    safe_file(marker)
    if not marker.exists() or marker.read_text(encoding='utf-8') != MARKER:
        raise ValueError('管理目印が一致しない')
    return p

def rule_changes(ws):
    changes = {}
    for name in ('AGENTS.md', 'CLAUDE.md'):
        p = ws / name
        if p.is_symlink():
            if name == 'CLAUDE.md' and p.resolve() == (ws / 'AGENTS.md').resolve() and not (ws / 'AGENTS.md').is_symlink():
                continue
            raise ValueError('既存ルールのリンク先へは書き込まない: ' + name)
        safe_file(p)
        old = p.read_text(encoding='utf-8') if p.exists() else ''
        if name == 'CLAUDE.md' and old in ('@AGENTS.md', '@AGENTS.md\n'):
            continue
        if old.count(BEGIN) or old.count(END):
            if old.count(BEGIN) != 1 or old.count(END) != 1 or BEGIN not in old or END not in old or old.index(BEGIN) > old.index(END):
                raise ValueError('管理ブロックが重複・破損: ' + name)
            actual = old[old.index(BEGIN):old.index(END)+len(END)]
            if actual != BLOCK:
                raise ValueError('管理ブロックが不一致: ' + name)
        else:
            changes[p] = old + ('\n\n' if old else '') + BLOCK + '\n'
    return changes

def init(ws, apply):
    src = Path(__file__).resolve().parent
    copies = {n: (src/n).read_text(encoding='utf-8') for n in ('状態管理.py','共通ルール.md','README.md')}
    target = ws / DIR
    def plan():
        if target.exists() or target.is_symlink():
            managed(ws)
            for n, data in copies.items():
                p = target/n
                safe_file(p)
                if not p.exists() or p.read_text(encoding='utf-8') != data:
                    raise ValueError('既存キットが不一致。自動上書きしない: ' + n)
        return rule_changes(ws)
    changes = plan()
    if not apply:
        print(json.dumps({'mode':'計画のみ','workspace':str(ws),'kit':'変更なし' if target.exists() else '新規配置','rules':[p.name for p in changes]}, ensure_ascii=False))
        return
    with lock(ws / '.全AI共通導入.lock'):
        changes = plan()
        if not target.exists():
            # 不完全なキットを正式な保存先へ出さない。失敗したstageは削除せず保管する。
            stage = Path(tempfile.mkdtemp(prefix='.全AI共通導入_未完了_', dir=ws))
            for n, data in copies.items():
                atomic(stage/n, data)
            atomic(stage/'管理目印.txt', MARKER)
            if target.exists() or target.is_symlink():
                raise ValueError('配置直前に保存先が作られたため中止。stageは保管済み')
            os.rename(stage, target)
        for p, data in changes.items():
            if p.exists():
                fd, backup = tempfile.mkstemp(prefix=p.name+'.導入前_', suffix='.bak', dir=ws)
                with os.fdopen(fd,'w',encoding='utf-8') as f:
                    f.write(p.read_text(encoding='utf-8'))
            atomic(p, data)
    print(json.dumps({'mode':'導入済み','workspace':str(ws),'rules_updated':[p.name for p in changes]},ensure_ascii=False))

def string(v, name, limit=2000):
    if not isinstance(v,str) or len(v)>limit or any(ord(c)<32 and c not in '\n\t' for c in v):
        raise ValueError(name+'の型・長さ・制御文字が不正')
    return v

def validate(data, source, route):
    if not isinstance(data,dict) or not FIELDS.issubset(data) or set(data)-FIELDS-{'source'}:
        raise ValueError('報告の必須フィールド不足または未定義フィールド')
    d = {k:data[k] for k in FIELDS}
    if d['agent'] not in AGENTS or d['status'] not in STATUS:
        raise ValueError('AIまたは状態が不正')
    for k in ('session_id','title','next_step','waiting_for','link','result'):
        string(d[k],k,200 if k in ('session_id','title') else 2000)
    if not d['session_id'].strip() or not d['title'].strip():
        raise ValueError('会話ID・名前は必須')
    if type(d['seq']) is not int or not 0 < d['seq'] <= 9007199254740991:
        raise ValueError('seqは正の整数が必要')
    if type(d['verified']) is not bool or type(d['title_synced']) is not bool:
        raise ValueError('verified/title_syncedは真偽値が必要')
    if not isinstance(d['asks'],list) or len(d['asks'])>20:
        raise ValueError('asksは20件以内の配列が必要')
    for v in d['asks']:
        if not string(v,'asks',1000).strip():
            raise ValueError('空の確認事項は不可')
    if d['link']:
        u = urlsplit(d['link'])
        uuid = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        native = re.fullmatch(r'(?:codex://threads/' + uuid + r'|claude://resume\?session=' + uuid + r')', d['link'])
        web = u.scheme in ('https','http') and bool(u.netloc) and not u.username and not u.password
        if not (web or native) or any(c.isspace() for c in d['link']):
            raise ValueError('linkは資格情報なしhttp/https、codex://threads/UUID、claude://resume?session=UUIDだけ')
    if d['status']=='done' and (not d['verified'] or d['asks'] or not d['result'].strip()):
        raise ValueError('完了にはverified=true・asks空・resultが必要')
    if d['status'] in ('waiting','waiting_reply') and not d['waiting_for'].strip():
        raise ValueError('待ち状態にはwaiting_forが必要')
    if d['status']=='needs_you' and not d['asks']:
        raise ValueError('本人判断待ちにはasksが必要')
    string(source,'source',300)
    if not source.strip() or any(c.isspace() for c in source):
        raise ValueError('確認済みsourceを指定する')
    if route == 'local' and source != 'local:'+d['agent']+'/'+d['session_id']:
        raise ValueError('ローカルsourceはlocal:AI/会話IDと一致させる')
    if route == 'network' and source.startswith('local:'):
        raise ValueError('Networkでは確認済みNetwork送信元を指定する')
    d.update(source=source,route=route,registered_at=now())
    return d

def read_rows(p):
    path = p/'状態.json'
    safe_file(path)
    if not path.exists():
        return []
    d = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(d,list):
        raise ValueError('台帳形式が不正')
    return d

def escape(v):
    return html.escape(str(v),quote=True).replace('|','&#124;').replace('\\','&#92;').replace('\n','<br>').replace('\r','').replace('`','&#96;').replace('[','&#91;').replace(']','&#93;')

def markdown(rows):
    lines=['# 全AI共通一覧','', 'verifiedはAIの自己申告。実機到達・結果の独立検証とは別。24時間より前は「古い報告」。報告なしは未接続の断定ではない。','', '| AI | 会話 | 状態 | 本人の確認事項 | 次の一手 | 待ち先・理由 | リンク | 結果 | 検証の自己申告 | タイトル同期 | 最終登録 | 送信元・経路 |','|---|---|---|---|---|---|---|---|---|---|---|---|']
    for agent in AGENTS:
        group=sorted([r for r in rows if r['agent']==agent],key=lambda r:r['session_id'])
        if not group:
            lines.append('| '+agent+' | — | 報告なし | — | — | — | — | — | — | — | — | — |')
        for r in group:
            age=dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(r['registered_at'])
            timestamp=r['registered_at']+('（古い報告）' if age.total_seconds()>86400 else '')
            vals=[agent,r['title']+' / '+r['session_id'],STATUS[r['status']], ' / '.join(r['asks']) or 'なし',r['next_step'],r['waiting_for'],r['link'],r['result'],str(r['verified']).lower()+'（自己申告）',str(r['title_synced']).lower(),timestamp,r['source']+' / '+r['route']]
            lines.append('| '+' | '.join(escape(v) for v in vals)+' |')
    return '\n'.join(lines)+'\n'

def report(ws,source,route):
    p=managed(ws)
    raw=sys.stdin.buffer.read(32769)
    if len(raw)>32768:
        raise ValueError('入力は32768バイト以内')
    d=validate(json.loads(raw.decode('utf-8')),source,route)
    with lock(p/'状態.lock'):
        rows=read_rows(p)
        for r in rows:
            if (r['agent'],r['session_id'])==(d['agent'],d['session_id']):
                if r['source']!=source or r['route']!=route:
                    raise ValueError('既存会話の送信元・経路は変更不可')
                if d['seq']<=r['seq']:
                    raise ValueError('古いseqを拒否。最新値より増やす')
        rows=[r for r in rows if (r['agent'],r['session_id'])!=(d['agent'],d['session_id'])]+[d]
        atomic(p/'状態.json',json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
        atomic(p/'一覧.md',markdown(rows))
    print(json.dumps(d,ensure_ascii=False))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('init','report','list'):
        p=sub.add_parser(name)
        p.add_argument('--workspace',required=True)
        if name=='init': p.add_argument('--apply',action='store_true')
        if name=='report':
            p.add_argument('--source',required=True)
            p.add_argument('--route',choices=('local','network'),required=True)
        if name=='list': p.add_argument('--format',choices=('markdown','json'),default='markdown')
    args=parser.parse_args()
    try:
        ws=existing_workspace(args.workspace)
        if args.command=='init': init(ws,args.apply)
        elif args.command=='report': report(ws,args.source,args.route)
        else:
            p=managed(ws)
            with lock(p/'状態.lock'):
                rows=read_rows(p)
            print(json.dumps({'rows':rows,'agents_without_report':[a for a in AGENTS if not any(r['agent']==a for r in rows)],'verified_meaning':'AI自己申告。実機・結果の独立検証ではない'},ensure_ascii=False,indent=2) if args.format=='json' else markdown(rows),end='\n')
    except (ValueError,OSError,UnicodeError,TypeError,KeyError) as e:
        print('エラー: '+str(e),file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    sys.exit(main())
