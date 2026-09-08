from pathlib import Path
from datetime import datetime
import re, shutil

START = '/* === HOURS + SKIP-LINK FINAL REFINE v3 START === */'
END = '/* === HOURS + SKIP-LINK FINAL REFINE v3 END === */'
CSS_BLOCK = '/* === HOURS + SKIP-LINK FINAL REFINE v3 START === */\n.hours { overflow-x: clip; }\n.hours .table-background { width:100%; max-width:100%; overflow-x:visible; background:transparent; }\n.hours table { width:964px; max-width:100%; min-width:0; margin-inline:auto; background:var(--paper); }\n.hours tbody tr { border-bottom:1px solid var(--border); }\n.hours tr > :first-child { border-right:1px solid var(--border); }\n\n.skip-link:focus {\n  position:fixed;\n  inset:8px auto auto 8px;\n  z-index:1000;\n  padding:6px 10px;\n  border:1px solid var(--border);\n  border-radius:4px;\n  background:#fff;\n  color:var(--primary);\n  font-size:13px;\n  line-height:20px;\n}\n.skip-link:focus-visible { outline:2px solid var(--primary); outline-offset:2px; }\n\n@media (max-width:767px) {\n  .hours > .container { width:100%; max-width:none; }\n  .hours .table-background,\n  .hours table { width:100%; max-width:100%; min-width:0; }\n  .hours .time-column { width:80px; }\n  .hours th,\n  .hours td { min-width:0; padding-inline:3px; }\n  .hours thead th { font-size:14px; line-height:20px; }\n  .hours tbody th,\n  .hours tbody td { font-size:16px; line-height:24px; }\n  .hours .hours-notes { width:calc(100% - 20px); max-width:964px; margin-inline:auto; }\n}\n\n@media (max-width:380px) {\n  .hours .time-column { width:72px; }\n  .hours th,\n  .hours td { padding-inline:2px; }\n  .hours tbody th,\n  .hours tbody td { font-size:15px; }\n}\n/* === HOURS + SKIP-LINK FINAL REFINE v3 END === */'


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "index.html").exists() and (candidate / "css" / "style.css").exists():
            return candidate
    raise FileNotFoundError("index.html と css/style.css があるリポジトリルートを見つけられませんでした。")


def backup_files(repo: Path, files):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = repo.parent / f"{repo.name}-backup-hours-v3-{stamp}"
    seen = set()
    for src in files:
        src = src.resolve()
        if src in seen or not src.exists():
            continue
        seen.add(src)
        rel = src.relative_to(repo.resolve())
        dst = backup_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return backup_root


def update_skip_links(repo: Path):
    count = 0
    pattern = re.compile(r'(<a\b(?=[^>]*\bclass=["\'][^"\']*\bskip-link\b[^"\']*["\'])(?=[^>]*\bhref=["\']#main["\'])[^>]*>)本文へ移動(</a>)', re.I)
    for path in repo.rglob("*.html"):
        if ".git" in path.parts or ".bak" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        new_text, n = pattern.subn(r"\1本文へ\2", text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            count += n
    return count


def update_hours_row_breaks(index_path: Path):
    text = index_path.read_text(encoding="utf-8")
    new = text.replace('<th scope="row">午前 9:00〜12:00</th>', '<th scope="row">午前<br>9:00〜<br>12:00</th>')
    new = new.replace('<th scope="row">午後 13:00〜18:00</th>', '<th scope="row">午後<br>13:00〜<br>18:00</th>')
    if new != text:
        index_path.write_text(new, encoding="utf-8")
        return True
    return False


def update_css(css_path: Path):
    text = css_path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new = pattern.sub(CSS_BLOCK, text) if pattern.search(text) else text.rstrip() + "\n\n" + CSS_BLOCK + "\n"
    if new != text:
        css_path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    try:
        repo = find_repo_root(Path.cwd())
    except FileNotFoundError as e:
        print("ERROR:", e)
        print("VS Codeのターミナルを sato-clinic-paku のルートで開いて実行してください。")
        return 1

    index_path = repo / "index.html"
    css_path = repo / "css" / "style.css"
    htmls = [p for p in repo.rglob("*.html") if ".git" not in p.parts and ".bak" not in p.name]
    backup_root = backup_files(repo, [index_path, css_path, *htmls])

    skip_count = update_skip_links(repo)
    row_changed = update_hours_row_breaks(index_path)
    css_changed = update_css(css_path)

    print("OK: Hours + skip-link 最終調整 v3 を適用しました。")
    print("Repository:", repo)
    print("Backup:", backup_root)
    print("skip-link 文言変更:", skip_count, "箇所")
    print("Hoursの時刻3行化:", "変更あり" if row_changed else "既に適用済み / 対象なし")
    print("CSS更新:", "変更あり" if css_changed else "既に最新")
    print("確認: 1440px / 390px / 375px / 320px でHoursの横スクロールがないことを確認してください。")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
