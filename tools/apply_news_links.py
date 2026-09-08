#!/usr/bin/env python3
"""現在の index.html のお知らせリンクだけを安全に差し替える。

リポジトリルートで実行:
    python tools/apply_news_links.py

- index.html 全体を作り直さない
- 既存レスポンシブ/ヘッダー/その他セクションを保持
- 変更前に index.html.bak-news を作成
"""
from pathlib import Path
import re
import shutil
import sys

root = Path.cwd()
index = root / "index.html"
if not index.exists():
    sys.exit("ERROR: リポジトリルートで実行してください。index.html が見つかりません。")

links = {
    "インフルエンザ予防接種について": "./news/influenza.html",
    "年末年始の休診について": "./news/year-end.html",
    "健康診断のご案内": "./news/checkup.html",
    "新型コロナウイルス対策について": "./news/covid19.html",
    "オンライン診療の導入について": "./news/online.html",
    "過去のお知らせ": "./news/index.html",
}

text = index.read_text(encoding="utf-8")
original = text

for label, href in links.items():
    # ラベルが一致するa要素だけを対象にし、class等は保持する。
    pattern = re.compile(
        r'<a(?P<attrs>[^>]*)>\s*' + re.escape(label) + r'\s*</a>',
        flags=re.S,
    )

    def repl(match):
        attrs = match.group("attrs")
        attrs = re.sub(r'\s+href\s*=\s*(["\']).*?\1', '', attrs, flags=re.S | re.I)
        attrs = re.sub(r'\s+data-notice\s*=\s*(["\']).*?\1', '', attrs, flags=re.S | re.I)
        attrs = attrs.rstrip()
        return f'<a{attrs} href="{href}">{label}</a>'

    text, count = pattern.subn(repl, text, count=1)
    if count != 1:
        sys.exit(f"ERROR: TOPページで『{label}』のリンクを1件特定できませんでした。変更を中止します。")

backup = root / "index.html.bak-news"
if not backup.exists():
    shutil.copy2(index, backup)

index.write_text(text, encoding="utf-8")
print("OK: index.html のお知らせ6リンクを更新しました。")
print(f"Backup: {backup}")
