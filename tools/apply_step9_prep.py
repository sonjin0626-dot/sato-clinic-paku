from pathlib import Path
import re
import shutil
import sys

ROOT = Path.cwd()
INDEX = ROOT / 'index.html'
STYLE = ROOT / 'css' / 'style.css'
MAIN_JS = ROOT / 'js' / 'main.js'

for path in (INDEX, STYLE, MAIN_JS):
    if not path.exists():
        print(f'ERROR: {path} が見つかりません。index.html があるリポジトリ直下で実行してください。')
        sys.exit(1)

# Safety backups: keep them OUTSIDE the repository so they cannot be committed by accident.
BACKUP_DIR = ROOT.parent / f"{ROOT.name}-step9-backup"
for path in (INDEX, STYLE, MAIN_JS):
    relative = path.relative_to(ROOT)
    backup = BACKUP_DIR / relative
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(path, backup)

index = INDEX.read_text(encoding='utf-8')
style = STYLE.read_text(encoding='utf-8')
main_js = MAIN_JS.read_text(encoding='utf-8')

changes = []

# 1) Hours: explicit 3-line labels like Figma mobile Hours nodes 192:65 / 180:262.
replacements = {
    '<th scope="row">午前 9:00〜12:00</th>': '<th scope="row"><span class="hours-period">午前<br>9:00〜<br>12:00</span></th>',
    '<th scope="row">午後 13:00〜18:00</th>': '<th scope="row"><span class="hours-period">午後<br>13:00〜<br>18:00</span></th>',
}
for old, new in replacements.items():
    count = index.count(old)
    if count:
        index = index.replace(old, new)
        changes.append(f'Hours label: {count}箇所')

# 2) Add the holiday note to both Hours note blocks, but only when missing.
holiday = '※祝祭日も診療を行っておりますが、休診日もございますので、事前にご確認ください。'
if holiday not in index:
    old = '<p>休診日：木曜・土曜午後・日曜</p>'
    count = index.count(old)
    if count:
        index = index.replace(old, old + f'<p>{holiday}</p>')
        changes.append(f'祝祭日注記: {count}箇所')
else:
    # If one copy already exists, ensure every Hours block has it.
    pattern = re.compile(r'(<div class="hours-notes"[^>]*>.*?<p>休診日：木曜・土曜午後・日曜</p>)(.*?</div>)', re.S)
    def ensure_holiday(match):
        block = match.group(0)
        if holiday in block:
            return block
        return match.group(1) + f'<p>{holiday}</p>' + match.group(2)
    new_index, count = pattern.subn(ensure_holiday, index)
    if new_index != index:
        index = new_index
        changes.append('祝祭日注記: 不足箇所を追加')

# 3) Fix only Yamamoto Hana's comment; keep the label "コメント" as requested.
yamamoto_pattern = re.compile(
    r'(<article class="alternating-row reverse">\s*<img[^>]+staff-yamamoto\.png.*?<h3>医療事務：山本 花</h3>.*?<li><strong>コメント</strong>：)(.*?)(</li>)',
    re.S,
)
yamamoto_text = '皆様に気持ちよくご利用いただけるよう、笑顔と真心を大切にしております。初めての方もどうぞ安心してお越しください。'
index, count = yamamoto_pattern.subn(lambda m: m.group(1) + yamamoto_text + m.group(3), index, count=1)
if count:
    changes.append('山本花コメント: 掲載原稿に修正')

# 4) Restore full department wording.
dep_old = '<li>予防医療健康診断</li><li>生活習慣病</li>'
dep_new = '<li>予防医療・健康診断</li><li>生活習慣病（高血圧、糖尿病等）の治療・管理</li>'
if dep_old in index:
    index = index.replace(dep_old, dep_new, 1)
    changes.append('診療科目表記: 正式表記に修正')

# 5) Remove obsolete "news under construction" fallback HTML.
index, aside_count = re.subn(
    r'\s*<aside class="notice-information"[^>]*>.*?</aside>',
    '', index, flags=re.S,
)
index, dialog_count = re.subn(
    r'\s*<dialog id="notice-dialog"[^>]*>.*?</dialog>',
    '', index, flags=re.S,
)
if aside_count or dialog_count:
    changes.append(f'旧お知らせHTML削除: aside={aside_count}, dialog={dialog_count}')

# 6) Remove obsolete notice-dialog JavaScript block.
main_js, js_count = re.subn(
    r'\nconst dialog = document\.querySelector\("#notice-dialog"\);\n'
    r'document\.querySelectorAll\("\[data-notice\]"\)\.forEach\(link => \{.*?\n\}\);\s*$',
    '\n', main_js, flags=re.S,
)
if js_count:
    changes.append('旧お知らせdialog JavaScript削除')

# 7) Remove dead old notice/dialog CSS rules.
old_css_patterns = [
    r'^\.notice-information \{[^\n]*\}\n?',
    r'^\.notice-information:target \{[^\n]*\}\n?',
    r'^\.notice-information h2,dialog h2 \{[^\n]*\}\n?',
    r'^dialog \{[^\n]*\}\n?',
    r'^dialog::backdrop \{[^\n]*\}\n?',
    r'^dialog form \{[^\n]*\}\n?',
]
removed_css = 0
for pat in old_css_patterns:
    style, n = re.subn(pat, '', style, flags=re.M)
    removed_css += n
if removed_css:
    changes.append(f'旧お知らせCSS削除: {removed_css}ルール')

# 8) Add Figma-derived smartphone Hours overrides once.
marker = '/* Figma mobile Hours: nodes 192:65 / 180:262 */'
mobile_hours_css = r'''

/* Figma mobile Hours: nodes 192:65 / 180:262 */
@media (max-width: 767px) {
  .hours {
    padding: 40px 0;
  }

  /* FigmaではHoursだけ390px幅いっぱいを使い、横スクロールさせない。 */
  .hours > .container {
    width: 100%;
    max-width: none;
  }

  .hours h2 {
    margin-bottom: 16px;
    font-size: 36px;
    line-height: 52px;
    letter-spacing: 1.08px;
  }

  .hours .table-background {
    width: 100%;
    overflow: visible;
  }

  .hours table {
    width: 100%;
    min-width: 0;
    margin-inline: 0;
    table-layout: fixed;
  }

  .hours .time-column,
  .hours thead th:first-child,
  .hours tbody th {
    width: 88px;
  }

  .hours thead th {
    height: 64px;
    padding: 12px 8px;
    font-size: 14px;
    line-height: 20px;
    white-space: nowrap;
  }

  .hours tbody th {
    height: auto;
    padding: 5px 8px;
    font-size: 16px;
    line-height: 24px;
  }

  .hours tbody td {
    height: 64px;
    padding: 12px 8px;
    font-size: 16px;
    line-height: 24px;
  }

  .hours-period {
    display: block;
    width: 58px;
    margin-inline: auto;
    text-align: center;
    font-weight: 500;
    line-height: 24px;
  }

  .hours-notes {
    width: 100%;
    margin-top: 16px;
    padding: 0 10px;
    font-size: 14px;
    line-height: 20px;
    font-weight: 500;
  }

  .hours-notes p + p {
    margin-top: 8px;
  }

  .hours-notes p:nth-child(-n + 2) {
    color: var(--muted);
  }

  .hours-notes p:nth-child(n + 3) {
    color: var(--text);
  }
}
'''
if marker not in style:
    style = style.rstrip() + mobile_hours_css + '\n'
    changes.append('スマホHours: Figma準拠CSS追加')

INDEX.write_text(index, encoding='utf-8')
STYLE.write_text(style, encoding='utf-8')
MAIN_JS.write_text(main_js, encoding='utf-8')

print('OK: STEP9前の整合性修正とHoursレスポンシブ修正を適用しました。')
for c in changes:
    print(' -', c)
print('\nバックアップ:')
print(f' - {BACKUP_DIR}')
print('\n次: Live Serverで390px表示を確認 → git diff → commit/push')
