from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil

STYLE_START = '/* === SUBPAGE HEADER SHARED GRADIENT v1 START === */'
STYLE_END = '/* === SUBPAGE HEADER SHARED GRADIENT v1 END === */'
NEWS_START = '/* === NEWS SUBPAGE MOBILE + HEADER v1 START === */'
NEWS_END = '/* === NEWS SUBPAGE MOBILE + HEADER v1 END === */'

STYLE_BLOCK = '/* === SUBPAGE HEADER SHARED GRADIENT v1 START === */\n/*\n  Shared lower-page header.\n  Reuses the TOP hero color language without copying the hero image/catchcopy.\n  Future STEP9 pages can use:\n  <header class="site-header subpage-header">...</header>\n*/\n.subpage-header.site-header {\n  position: relative;\n  inset: auto;\n  z-index: 20;\n  width: 100%;\n  min-height: 130px;\n  height: auto;\n  padding: 10px 20px 10px 10px;\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  gap: 24px;\n  background: linear-gradient(\n    90deg,\n    #bcd9dd 0%,\n    #3b529a 30.7%,\n    #3752a0 30.8%,\n    #315999 86%\n  );\n}\n\n.subpage-header .logo,\n.subpage-header .logo img {\n  width: 320px;\n  height: auto;\n  flex-shrink: 0;\n}\n\n.subpage-header nav {\n  margin: 0;\n}\n\n@media (max-width: 1100px) {\n  .subpage-header.site-header {\n    min-height: 110px;\n    padding: 14px 32px;\n    align-items: flex-start;\n  }\n\n  .subpage-header .logo,\n  .subpage-header .logo img {\n    width: 300px;\n  }\n}\n\n@media (max-width: 767px) {\n  .subpage-header.site-header {\n    min-height: 100px;\n    padding: 14px 20px;\n  }\n\n  .subpage-header .logo,\n  .subpage-header .logo img {\n    width: 220px;\n  }\n}\n\n@media (max-width: 480px) {\n  .subpage-header.site-header {\n    min-height: 92px;\n    padding: 12px 16px;\n  }\n\n  .subpage-header .logo,\n  .subpage-header .logo img {\n    width: 190px;\n  }\n}\n/* === SUBPAGE HEADER SHARED GRADIENT v1 END === */'
NEWS_BLOCK = '/* === NEWS SUBPAGE MOBILE + HEADER v1 START === */\n/*\n  news.css is loaded after style.css, so repeat only the background override\n  with the existing News-page specificity.\n*/\n.news-page .subpage-header.site-header {\n  background: linear-gradient(\n    90deg,\n    #bcd9dd 0%,\n    #3b529a 30.7%,\n    #3752a0 30.8%,\n    #315999 86%\n  );\n}\n\n@media (max-width: 767px) {\n  /*\n    On the News archive page, prioritize the list itself on smartphones.\n    Desktop/tablet keep the supplied photo.\n  */\n  .news-archive__image {\n    display: none;\n  }\n\n  .news-archive__layout {\n    grid-template-columns: minmax(0, 1fr);\n    gap: 0;\n  }\n}\n/* === NEWS SUBPAGE MOBILE + HEADER v1 END === */'


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (
            (candidate / "index.html").exists()
            and (candidate / "css" / "style.css").exists()
            and (candidate / "css" / "news.css").exists()
            and (candidate / "news" / "index.html").exists()
        ):
            return candidate
    raise FileNotFoundError(
        "index.html / css/style.css / css/news.css / news/index.html がある"
        " sato-clinic-paku のルートを見つけられませんでした。"
    )


def backup(repo: Path, files: list[Path]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = repo.parent / f"{repo.name}-backup-subpage-header-v1-{stamp}"

    for src in files:
        rel = src.relative_to(repo)
        dst = backup_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    return backup_root


def upsert_block(path: Path, start: str, end: str, block: str) -> str:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)

    if pattern.search(text):
        new_text = pattern.sub(block, text)
        status = "更新"
    else:
        new_text = text.rstrip() + "\n\n" + block + "\n"
        status = "追加"

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return status
    return "変更なし"


def main() -> int:
    try:
        repo = find_repo_root(Path.cwd())
    except FileNotFoundError as exc:
        print("ERROR:", exc)
        print("VS Codeのターミナルを sato-clinic-paku のルートで開いて実行してください。")
        return 1

    style_css = repo / "css" / "style.css"
    news_css = repo / "css" / "news.css"

    backup_root = backup(repo, [style_css, news_css])

    style_status = upsert_block(
        style_css, STYLE_START, STYLE_END, STYLE_BLOCK
    )
    news_status = upsert_block(
        news_css, NEWS_START, NEWS_END, NEWS_BLOCK
    )

    print("OK: 下層共通グラデーションヘッダー + News一覧スマホ画像非表示を適用しました。")
    print("Repository:", repo)
    print("Backup:", backup_root)
    print("css/style.css:", style_status)
    print("css/news.css:", news_status)
    print()
    print("確認ポイント:")
    print("  1. news/index.html のPC・タブレットではNews写真が表示される")
    print("  2. 767px以下ではNews写真が非表示になる")
    print("  3. News一覧・各News詳細のヘッダーがTOPと同系統のグラデーションになる")
    print("  4. TOPページのHero/Headerには変更がない")
    print("  5. 390px / 375px / 320px で横スクロールが発生しない")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
