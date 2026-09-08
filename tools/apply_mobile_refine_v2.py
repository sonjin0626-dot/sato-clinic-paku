from pathlib import Path
import shutil
import sys

ROOT = Path.cwd()
STYLE = ROOT / 'css' / 'style.css'

if not STYLE.exists():
    print('ERROR: css/style.css が見つかりません。index.html があるリポジトリ直下で実行してください。')
    sys.exit(1)

# Backup outside the repository.
BACKUP_DIR = ROOT.parent / f"{ROOT.name}-mobile-refine-v2-backup"
backup = BACKUP_DIR / 'css' / 'style.css'
backup.parent.mkdir(parents=True, exist_ok=True)
if not backup.exists():
    shutil.copy2(STYLE, backup)

style = STYLE.read_text(encoding='utf-8')

# Remove the previous generated Hours-only block if it is still the final generated block.
old_marker = '/* Figma mobile Hours: nodes 192:65 / 180:262 */'
if old_marker in style:
    idx = style.find(old_marker)
    tail = style[idx:]
    # The v1 script always appended this block at EOF. Only trim when the tail
    # looks like that generated block, to avoid deleting unrelated manual CSS.
    if 'Mobile refinement v2' not in tail and tail.count('@media') == 1:
        style = style[:idx].rstrip() + '\n'

marker = '/* Mobile refinement v2: Hours + mobile content hierarchy */'
if marker in style:
    print('INFO: v2 はすでに適用済みです。変更はありません。')
    sys.exit(0)

css = r'''

/* Mobile refinement v2: Hours + mobile content hierarchy */
@media (max-width: 767px) {
  /* ---------------------------------------------------------
     Hours
     - no horizontal scrolling
     - slightly narrower time column than the 390px mockup
     - both top and bottom Hours share the same behavior
     --------------------------------------------------------- */
  .hours {
    padding: 40px 0;
    overflow-x: clip;
  }

  .hours > .container {
    width: 100%;
    max-width: 100%;
    margin-inline: 0;
    padding-inline: 0;
  }

  .hours .table-background {
    width: 100%;
    max-width: 100%;
    margin: 0;
    overflow-x: hidden;
  }

  .hours table {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    margin: 0;
    table-layout: fixed;
  }

  /* 88px in the original 390px Figma was visually generous.
     80px keeps the 3-line time label readable while giving weekdays more room. */
  .hours .time-column,
  .hours thead th:first-child,
  .hours tbody th {
    width: 80px;
  }

  .hours th,
  .hours td {
    min-width: 0;
  }

  .hours thead th:first-child {
    padding-inline: 4px;
  }

  .hours thead th:not(:first-child),
  .hours tbody td {
    padding-inline: 2px;
  }

  .hours tbody th {
    height: auto;
    padding: 5px 4px;
  }

  .hours-period {
    width: 58px;
    max-width: 100%;
    margin-inline: auto;
  }

  .hours-notes {
    width: 100%;
    max-width: 100%;
    margin-top: 16px;
    padding-inline: 10px;
    overflow-wrap: anywhere;
  }

  .hours-notes p {
    max-width: 100%;
    white-space: normal;
  }

  /* ---------------------------------------------------------
     News
     Mobile priority is the announcement content itself.
     The desktop image remains; on smartphone it is omitted.
     --------------------------------------------------------- */
  .news-layout {
    display: block;
  }

  .news-layout > img {
    display: none;
  }

  .news-content {
    width: 100%;
  }

  .news h2 {
    margin-bottom: 0;
    text-align: center;
  }

  /* ---------------------------------------------------------
     Greeting
     Visual order: heading -> portrait -> copy
     --------------------------------------------------------- */
  .greeting-layout {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .greeting-content {
    display: contents;
  }

  .greeting-content h2 {
    order: 1;
    margin: 0;
    text-align: center;
  }

  .director {
    order: 2;
    width: min(100%, 386px);
    margin-inline: auto;
  }

  .greeting-text {
    order: 3;
  }

  /* ---------------------------------------------------------
     Services / Staff
     Visual order inside each item: heading -> photo -> detail
     --------------------------------------------------------- */
  .services .alternating-row,
  .staff .alternating-row {
    display: flex;
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .services .alternating-row .row-content,
  .staff .alternating-row .row-content {
    display: contents;
  }

  .services .alternating-row h3,
  .staff .alternating-row h3 {
    order: 1;
    margin: 0;
    text-align: left;
  }

  .services .alternating-row > img,
  .staff .alternating-row > img {
    order: 2;
    grid-column: auto;
    grid-row: auto;
    width: min(100%, 360px);
    height: auto;
    margin-inline: auto;
  }

  .services .alternating-row p,
  .staff .staff-details {
    order: 3;
  }

  /* ---------------------------------------------------------
     About
     Visual order: heading -> photo -> copy -> button
     --------------------------------------------------------- */
  .about-layout {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .about-content,
  .about-content > div:first-child {
    display: contents;
  }

  .about-content h2 {
    order: 1;
    margin: 0;
    text-align: center;
  }

  .about-layout > img {
    order: 2;
    width: 100%;
    height: auto;
    margin: 0;
  }

  .about-content p {
    order: 3;
  }

  .about-content .button-row {
    order: 4;
  }
}

@media (max-width: 380px) {
  .hours .time-column,
  .hours thead th:first-child,
  .hours tbody th {
    width: 72px;
  }

  .hours thead th:first-child {
    font-size: 13px;
  }
}
'''

STYLE.write_text(style.rstrip() + css + '\n', encoding='utf-8')

print('OK: モバイルレスポンシブ調整 v2 を適用しました。')
print(' - Hours: 左列を縮小し、横スクロールを抑止')
print(' - News: スマホ時の写真を非表示')
print(' - Greeting/About: 見出しを写真より先に表示')
print(' - Services/Staff: 各項目を 見出し→写真→本文/詳細 の順に表示')
print(f'Backup: {backup}')
print('次: Live Serverで 390px / 375px / 320px を確認してください。')
