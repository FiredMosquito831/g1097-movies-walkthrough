"""Build the bilingual (RO + EN) static study site.

Source:
  <test 1>/*.md          Romanian chapters
  <test 1>/en/*.md       English chapters

Output (site/):
  index.html, cap-01.html .. cap-11.html          Romanian
  en/index.html, en/cap-01.html .. cap-11.html    English
  assets/style.css, assets/app.js, assets/structure.json
"""
import html as htmlmod
import json
import os
import re
import shutil

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = HERE
OUT = os.path.join(HERE, "site")

# (num, ro_label, en_label, ro_file, en_file)
CHAPTERS = [
    ("01", "Setup și schelet", "Setup and skeleton",
     "01 - Setup si schelet.md", "01 - Setup and skeleton.md"),
    ("02", "Modelul Movie", "The Movie model",
     "02 - Modelul Movie.md", "02 - The Movie model.md"),
    ("03", "Ecranul principal", "Main screen",
     "03 - Ecranul principal - layout.md", "03 - Main screen - layout.md"),
    ("04", "MainActivity", "MainActivity",
     "04 - MainActivity - lista.md", "04 - MainActivity - the list.md"),
    ("05", "Formularul 1", "The form 1",
     "05 - Formularul - partea 1.md", "05 - The form - part 1.md"),
    ("06", "Formularul 2", "The form 2",
     "06 - Formularul - partea 2.md", "06 - The form - part 2.md"),
    ("07", "ItemActivity", "ItemActivity",
     "07 - ItemActivity - citire si scriere.md", "07 - ItemActivity - reading and writing.md"),
    ("08", "Navigare", "Navigation",
     "08 - Navigarea si rezultatul.md", "08 - Navigation and the result.md"),
    ("09", "Editare", "Edit mode",
     "09 - Modul de editare.md", "09 - Edit mode.md"),
    ("10", "Reconstruire", "Rebuild",
     "10 - Reconstruieste de la zero.md", "10 - Rebuild from scratch.md"),
    ("11", "Extensii", "Extensions",
     "11 - Extensii.md", "11 - Extensions.md"),
    ("12", "DMA06 — ListView vs RecyclerView", "DMA06 — ListView vs RecyclerView",
     "12 - DMA06 - ListView vs RecyclerView.md", "12 - DMA06 - ListView vs RecyclerView.md"),
    ("13", "DMA05 — ViewBinding", "DMA05 — ViewBinding",
     "13 - DMA05 - ViewBinding.md", "13 - DMA05 - ViewBinding.md"),
    ("14", "DMA03 — Navigare și meniuri", "DMA03 — Navigation and menus",
     "14 - DMA03 - Navigare si meniuri.md", "14 - DMA03 - Navigation and menus.md"),
    ("15", "DMA02 — Ciclu de viață", "DMA02 — Lifecycle",
     "15 - DMA02 - Application si ciclu de viata.md", "15 - DMA02 - Application and lifecycle.md"),
    ("16", "Istoricul repo-ului", "Repository history",
     "16 - Istoricul repo-ului.md", "16 - Repository history.md"),
    ("17", "Bancul 1 — Atribute noi", "Bank 1 — New attributes",
     "17 - Bancul 1 - Atribute noi.md", "17 - Bank 1 - New attributes.md"),
    ("18", "Bancul 2 — Bindinguri și adaptoare", "Bank 2 — Bindings and adapters",
     "18 - Bancul 2 - Bindinguri si adaptoare.md", "18 - Bank 2 - Bindings and adapters.md"),
    ("19", "Bancul 3 — Valori în UI", "Bank 3 — Values in the UI",
     "19 - Bancul 3 - Valori in UI si persistenta.md", "19 - Bank 3 - Values in UI and state.md"),
    ("20", "Bancul 4 — Controale noi", "Bank 4 — New controls",
     "20 - Bancul 4 - Controale noi.md", "20 - Bank 4 - New controls.md"),
    ("21", "Cheatsheet", "Cheatsheet",
     "21 - Cheatsheet.md", "21 - Cheatsheet.md"),
    ("22", "Codul adnotat", "Annotated code",
     "22 - Codul adnotat.md", "22 - Annotated code.md"),
    ("23", "Bancul 5 — Migrare ListView → RecyclerView", "Bank 5 — ListView to RecyclerView",
     "23 - Bancul 5 - Migrare ListView la RecyclerView.md", "23 - Bank 5 - ListView to RecyclerView.md"),
    ("24", "Bancul 6 — Persistență și verificare", "Bank 6 — Persistence and verification",
     "24 - Bancul 6 - Persistenta si verificare.md", "24 - Bank 6 - Persistence and verification.md"),
]

MD_EXT = ["extra", "codehilite", "toc", "tables", "fenced_code", "attr_list",
          "md_in_html", "sane_lists"]

UI = {
    "ro": {
        "site_title": "Test 1 — G1097",
        "brand_sub": "· G1097",
        "chapters": "Capitole",
        "overview": "Prezentare generală",
        "theme_auto": "🌗 Auto", "theme_light": "☀️ Light", "theme_dark": "🌙 Dark",
        "prev": "← Înapoi", "next_ch": "Capitolul {} →", "prev_ch": "← Capitolul {}",
        "index_title": "Test 1 — G1097 — Aplicația Movies, de la zero",
        "index_desc": "Ghid complet de reconstruire a aplicației Android G1097 (Movies), "
                      "pas cu pas, cu exerciții, indicii, soluții și progres salvat local.",
        "ch_title": "Capitolul {} — {} · Test 1 — G1097",
        "ch_desc": "Capitolul {} din ghidul de reconstruire a aplicației G1097: {}.",
        "check_step": "Bifează pasul", "check_ex": "Am rezolvat", "check_drill": "Am terminat drill-ul",
        "lang_other": "EN", "lang_other_title": "Switch to English",
        "progress": "Progresul tău", "complete": "complet", "of": "din", "checks": "bife",
        "saved_local": "salvat local, fără cont",
        "export": "⬇ Export progres", "import": "⬆ Import progres", "reset": "Șterge progresul",
        "howto": "Cum se folosește", "about": "Despre material",
        "steps": "pași", "exercises": "exerciții",
        "done": "făcute",
    },
    "en": {
        "site_title": "Test 1 — G1097",
        "brand_sub": "· G1097",
        "chapters": "Chapters",
        "overview": "Overview",
        "theme_auto": "🌗 Auto", "theme_light": "☀️ Light", "theme_dark": "🌙 Dark",
        "prev": "← Back", "next_ch": "Chapter {} →", "prev_ch": "← Chapter {}",
        "index_title": "Test 1 — G1097 — The Movies app, from scratch",
        "index_desc": "A complete walkthrough for rebuilding the G1097 Android app (Movies), "
                      "step by step, with exercises, hints, solutions and locally saved progress.",
        "ch_title": "Chapter {} — {} · Test 1 — G1097",
        "ch_desc": "Chapter {} of the G1097 rebuild guide: {}.",
        "check_step": "Mark step done", "check_ex": "Solved", "check_drill": "Drill finished",
        "lang_other": "RO", "lang_other_title": "Comută pe română",
        "progress": "Your progress", "complete": "complete", "of": "of", "checks": "checks",
        "saved_local": "saved locally, no account",
        "export": "⬇ Export progress", "import": "⬆ Import progress", "reset": "Reset progress",
        "howto": "How to use this", "about": "About this material",
        "steps": "steps", "exercises": "exercises",
        "done": "done",
    },
}


def slug(text: str) -> str:
    t = text.lower()
    for a, b in (("ă", "a"), ("â", "a"), ("î", "i"), ("ș", "s"), ("ş", "s"),
                 ("ț", "t"), ("ţ", "t")):
        t = t.replace(a, b)
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")[:70]


# --------------------------------------------------------------- preprocess
def preprocess(raw: str, lang: str):
    items = []
    lines = raw.split("\n")
    out = []
    in_fence = False
    i = 0
    ui = UI[lang]
    step_word = "Step" if lang == "en" else "Pasul"
    ex_word = "Exercise" if lang == "en" else "Exercițiu"

    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(ln)
            i += 1
            continue

        if not in_fence:
            m = re.match(r"^(#{2,4})\s+(?:Pasul|Step)\s+(\d+\.\d+)\s*[—-]\s*(.+)$", ln)
            if m:
                num, title = m.group(2), m.group(3).strip()
                key = f"step:{num}"
                items.append({"key": key, "num": num, "kind": "step", "title": title})
                out.append(f"## {step_word} {num} — {title} {{#pasul-{num.replace('.', '-')}}}")
                out.append("")
                out.append(f'<div class="chk" data-key="{key}">'
                           f'<span>{ui["check_step"]}</span></div>')
                out.append("")
                i += 1
                continue

            m = re.match(r"^(#{2,5})\s+(?:Exerci[iț]iu(?:l)?|Exercise)\s+(\d+\.\d+)(.*)$", ln)
            if m:
                num, tail = m.group(2), m.group(3).strip(" —-–")
                key = f"ex:{num}"
                items.append({"key": key, "num": num, "kind": "exercise",
                              "title": tail or f"{ex_word} {num}"})
                label = f"{ex_word} {num}" + (f" — {tail}" if tail else "")
                out.append(f"### {label} {{#ex-{num.replace('.', '-')}}}")
                out.append("")
                out.append(f'<div class="chk chk-ex" data-key="{key}">'
                           f'<span>{ui["check_ex"]}</span></div>')
                out.append("")
                i += 1
                continue

            if re.match(r"^\s*<details>\s*$", ln):
                block = [ln]
                depth = 1
                i += 1
                while i < len(lines) and depth > 0:
                    l2 = lines[i]
                    if re.match(r"^\s*<details>\s*$", l2):
                        depth += 1
                    elif re.match(r"^\s*</details>\s*$", l2):
                        depth -= 1
                    block.append(l2)
                    i += 1
                txt = "\n".join(block)
                txt = re.sub(r"<details>", '<details markdown="1">', txt, count=1)
                txt = re.sub(r"<summary>\s*(?:Indiciu|Hint)\s*</summary>",
                             '<summary><span class="sum-ico">💡</span> '
                             + ("Hint" if lang == "en" else "Indiciu") + "</summary>", txt)
                txt = re.sub(r"<summary>\s*(?:Solu[iț]ie|Solution)([^<]*)</summary>",
                             '<summary><span class="sum-ico">✅</span> '
                             + ("Solution" if lang == "en" else "Soluție") + r"\1</summary>", txt)
                txt = re.sub(r"<summary>\s*(?:R[aă]spuns(?:uri)?|Answers?)\s*</summary>",
                             '<summary><span class="sum-ico">📘</span> '
                             + ("Answers" if lang == "en" else "Răspunsuri") + "</summary>", txt)
                out.append(txt)
                continue

        out.append(ln)
        i += 1

    text = "\n".join(out)
    text = re.sub(r"\]\((\d\d)%20-%20[^)]*\.md\)", r"](cap-\1.html)", text)
    text = re.sub(r"\]\((?:README|index)\.md\)", r"](index.html)", text)
    text = fix_lists(text)
    return text, items


def fix_lists(text: str) -> str:
    """Markdown needs a blank line before a list that follows a paragraph.
    Chapters often write '**Cum abordezi:**' immediately followed by '1. ...',
    which collapses into one paragraph. Insert the blank line."""
    lines = text.split("\n")
    out = []
    in_fence = False
    prev_blank = True
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(ln)
            prev_blank = False
            continue
        if not in_fence:
            is_list = bool(re.match(r"^\s*(?:[-*+]|\d+\.)\s+\S", ln))
            if is_list and not prev_blank:
                prev = out[-1] if out else ""
                if prev.strip() and not re.match(r"^\s*(?:[-*+]|\d+\.)\s+\S", prev) \
                        and not re.match(r"^#{1,6}\s", prev) \
                        and not prev.lstrip().startswith(">") \
                        and not prev.lstrip().startswith("<"):
                    out.append("")
        out.append(ln)
        prev_blank = (ln.strip() == "")
    return "\n".join(out)


def add_drill_checkpoint(md_text: str, num: str, items: list, lang: str) -> str:
    """Add a single 'I finished this' checkbox to chapters that have no numbered steps."""
    if num == "10":
        key = "drill:10"
        title = "Drill" if lang == "en" else "Drill cronometrat"
        marker = "## Timing table" if lang == "en" else "## Tabel de cronometrare"
        label = UI[lang]["check_drill"]
    elif num == "21":
        key = "read:21"
        title = "Cheatsheet read"
        marker = "## 21.2" if lang == "en" else "## 21.2"
        label = "Am citit cheatsheet-ul" if lang != "en" else "I read the cheatsheet"
    elif num == "22":
        key = "read:22"
        title = "Annotated code read"
        marker = "## 22.2" if lang == "en" else "## 22.2"
        label = "Am citit codul adnotat" if lang != "en" else "I read the annotated code"
    else:
        return md_text
    items.append({"key": key, "num": num, "kind": "drill", "title": title})
    insert = (f'<div class="chk chk-drill" data-key="{key}">'
              f'<span>{label}</span></div>\n\n')
    return md_text.replace(marker, insert + marker, 1)


def balance_details(html_text: str) -> str:
    """md_in_html sometimes emits an extra </details> (or drops one) at the end of
    a block that ends the document. Normalise: drop stray closes, append missing ones."""
    out = []
    depth = 0
    pos = 0
    for m in re.finditer(r"<details[^>]*>|</details\s*>", html_text):
        out.append(html_text[pos:m.start()])
        tag = m.group(0)
        if tag.startswith("</"):
            if depth > 0:
                depth -= 1
                out.append(tag)
            # else: stray close -> drop it
        else:
            depth += 1
            out.append(tag)
        pos = m.end()
    out.append(html_text[pos:])
    body = "".join(out)
    if depth > 0:
        body += "</details>" * depth
    return body


def render(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=MD_EXT,
        extension_configs={"codehilite": {"guess_lang": False, "css_class": "codehilite"}},
    )
    return balance_details(md.convert(md_text))



# --------------------------------------------------------------- sections
# (slug, RO title, EN title, RO subtitle, EN subtitle, chapter numbers)
SECTIONS = [
    ("rescrie", "Rescrie de la 0", "Rebuild from scratch",
     "Construiești aplicația G1097 pas cu pas, de la proiect gol până la starea din repo.",
     "You build the G1097 app step by step, from an empty project to the repo state.",
     ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11"]),
    ("exercitii", "Exerciții tip test", "Exam-style exercises",
     "60 de cerințe ca la examen, pe codul real din 1097. Pași, indicii, soluții.",
     "60 exam-style requirements on the real 1097 code. Steps, hints, solutions.",
     ["17", "18", "19", "20", "23", "24"]),
    ("cod", "Codul explicat + cheatsheet", "Explained code + cheatsheet",
     "Fiecare fișier comentat bloc cu bloc, plus o referință densă de rețete.",
     "Every file annotated block by block, plus a dense reference of recipes.",
     ["21", "22"]),
]
APPENDIX = ("anexe", "Anexe — proiectele de curs", "Appendix — the course projects",
            "Proiectele DMA02/DMA03/DMA05/DMA06 și istoricul complet al repo-ului.",
            "The DMA02/DMA03/DMA05/DMA06 projects and the complete repo history.",
            ["12", "13", "14", "15", "16"])

SECTION_OF = {}
for slug, _, _, _, _, nums in SECTIONS + [APPENDIX]:
    for n in nums:
        SECTION_OF[n] = slug


def ch_by_num(num):
    for ch in CHAPTERS:
        if ch[0] == num:
            return ch
    raise KeyError(num)


# --------------------------------------------------------------- templates
HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="{base}assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📱</text></svg>">
</head>
<body data-lang="{lang}">
<header class="topbar">
  <button id="menuBtn" type="button" aria-label="Menu">☰</button>
  <a class="brand" href="{brand_index}">G1097</a>
  <nav class="sections">{section_nav}</nav>
  <div class="spacer"></div>
  <a class="btn lang" href="{other_href}" title="{other_title}">{other_label}</a>
  <button id="themeBtn" type="button" title="Theme">🌗 Auto</button>
</header>
<div class="layout">
{sidebar}
<main{main_attrs}>
{body}
{pager}
</main>
</div>
<script src="{base}assets/app.js"></script>
</body>
</html>
"""


def section_nav_html(active_section: str, lang: str) -> str:
    idx_t = 1 if lang == "en" else 2
    parts = []
    for slug, ro_t, en_t, _ro_s, _en_s, _nums in SECTIONS:
        label = en_t if lang == "en" else ro_t
        cls = "sec active" if slug == active_section else "sec"
        parts.append(f'<a class="{cls}" href="{slug}.html">{htmlmod.escape(label)}</a>')
    return "".join(parts)


def sidebar_html(active: str, lang: str, total_checks: int) -> str:
    ui = UI[lang]
    lcol = 1 if lang == "en" else 0
    out = ['<aside class="sidebar" id="sidebar">']
    for slug, ro_t, en_t, ro_s, en_s, nums in [SECTIONS[0], APPENDIX, SECTIONS[1], SECTIONS[2]]:
        label = en_t if lang == "en" else ro_t
        out.append(f'<h2><a href="{slug}.html">{htmlmod.escape(label)}</a></h2>')
        out.append('<nav>')
        for num in nums:
            ch = ch_by_num(num)
            lbl = ch[1 + lcol]
            cls = "active" if active == num else ""
            out.append(
                f'<a href="cap-{num}.html" class="{cls}">'
                f'<span class="num">{num}</span> {htmlmod.escape(lbl)}</a>'
            )
        out.append('</nav>')
    out.append(f'<div class="mini-progress" id="miniProgress" data-total="{total_checks}"></div>')
    out.append('</aside>')
    return "".join(out)


def pager_html(idx: int, lang: str) -> str:
    ui = UI[lang]
    lcol = 1 if lang == "en" else 0
    parts = ['<nav class="pager">']
    if idx > 0:
        pnum, plabel = CHAPTERS[idx - 1][0], CHAPTERS[idx - 1][1 + lcol]
        parts.append(
            f'<a class="prev" href="cap-{pnum}.html">'
            f'<span class="dir">{ui["prev_ch"].format(pnum)}</span>'
            f'<span class="ttl">{htmlmod.escape(plabel)}</span></a>'
        )
    else:
        parts.append(
            f'<a class="prev" href="index.html">'
            f'<span class="dir">{ui["prev"]}</span>'
            f'<span class="ttl">{ui["overview"]}</span></a>'
        )
    if idx < len(CHAPTERS) - 1:
        nnum, nlabel = CHAPTERS[idx + 1][0], CHAPTERS[idx + 1][1 + lcol]
        parts.append(
            f'<a class="next" href="cap-{nnum}.html">'
            f'<span class="dir">{ui["next_ch"].format(nnum)}</span>'
            f'<span class="ttl">{htmlmod.escape(nlabel)}</span></a>'
        )
    parts.append("</nav>")
    return "\n".join(parts)


def chapter_card_html(num: str, lang: str, parsed, totals) -> str:
    ui = UI[lang]
    lcol = 1 if lang == "en" else 0
    ch = ch_by_num(num)
    label = ch[1 + lcol]
    items = parsed[lang][num][1]
    steps = sum(1 for x in items if x["kind"] == "step")
    exs = sum(1 for x in items if x["kind"] == "exercise")
    meta = []
    if steps:
        meta.append(f'{steps} {ui["steps"]}')
    if exs:
        meta.append(f'{exs} {ui["exercises"]}')
    if not meta:
        meta.append("—")
    return (
        f'<a class="chapter-card" href="cap-{num}.html" '
        f'data-chapter="{num}." data-total="{totals[num]}">'
        f'<div class="cc-top"><span class="cc-num">{num}</span>'
        f'<span class="cc-title">{htmlmod.escape(label)}</span></div>'
        f'<div class="cc-meta">{" · ".join(meta)}'
        f'<span class="cc-done" style="float:right"></span></div>'
        f'<div class="bar"><i></i></div></a>'
    )


def section_check_total(nums, totals) -> int:
    return sum(totals[n] for n in nums)


# --------------------------------------------------------------- build
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "assets"))
os.makedirs(os.path.join(OUT, "en"))

ASSETS_SRC = os.path.join(HERE, "assets")
for f in ("style.css", "app.js"):
    shutil.copy2(os.path.join(ASSETS_SRC, f), os.path.join(OUT, "assets", f))

# ---- pass 1: parse all chapters in both languages
parsed = {"ro": {}, "en": {}}
missing_en = []

for ch in CHAPTERS:
    num = ch[0]
    for lang, fname in (("ro", ch[3]), ("en", ch[4])):
        path = os.path.join(SRC, fname) if lang == "ro" else os.path.join(SRC, "en", fname)
        if not os.path.isfile(path):
            missing_en.append(f"{lang}/{fname}")
            parsed[lang][num] = (None, [])
            continue
        raw = open(path, encoding="utf-8").read()
        md_text, items = preprocess(raw, lang)
        md_text = add_drill_checkpoint(md_text, num, items, lang)
        parsed[lang][num] = (md_text, items)

if missing_en:
    print("MISSING (will fall back to RO):")
    for m in missing_en:
        print("  ", m)

for ch in CHAPTERS:
    num = ch[0]
    if parsed["en"][num][0] is None:
        md_text, items = preprocess(open(os.path.join(SRC, ch[3]), encoding="utf-8").read(), "en")
        md_text = add_drill_checkpoint(md_text, num, items, "en")
        parsed["en"][num] = (md_text, items)

totals = {num: len(parsed["ro"][num][1]) for num in parsed["ro"]}
total_checks = sum(totals.values())
print(f"TOTAL checks: {total_checks}")

HERO = {
    "rescrie": {
        "ro": ("<b>Rescrie de la 0.</b> Pornești de la un proiect gol și ajungi la aplicația "
               "completă, în 11 capitole. Fiecare pas are un „De ce”, un „Cum” și o verificare. "
               "La final, un drill cronometrat."),
        "en": ("<b>Rebuild from scratch.</b> You start from an empty project and end with the "
               "complete app, in 11 chapters. Every step has a “Why”, a “How” and a check. "
               "At the end, a timed drill."),
    },
    "exercitii": {
        "ro": ("<b>Exerciții tip test.</b> 60 de cerințe exact în stilul celor de la examen, pe "
               "codul real din 1097. Fiecare are planul de lucru pas cu pas, două indicii gradate "
               "și soluția explicată."),
        "en": ("<b>Exam-style exercises.</b> 60 requirements in the exam's own style, on the real "
               "1097 code. Each has a step-by-step plan, two graduated hints and an explained "
               "solution."),
    },
    "cod": {
        "ro": ("<b>Codul explicat + cheatsheet.</b> Fiecare fișier din aplicație, comentat bloc cu "
               "bloc — ce face, de ce e acolo, ce se strică dacă îl ștergi. Plus o referință densă "
               "de rețete pentru examen."),
        "en": ("<b>Explained code + cheatsheet.</b> Every file in the app, annotated block by "
               "block — what it does, why it's there, what breaks if you delete it. Plus a dense "
               "reference of exam recipes."),
    },
    "anexe": {
        "ro": ("<b>Anexe.</b> Proiectele de curs (DMA02, DMA03, DMA05, DMA06) — exact lucrurile "
               "care lipsesc din G1097: RecyclerView, ViewBinding, meniuri, ciclu de viață — și "
               "istoricul complet al repo-ului."),
        "en": ("<b>Appendix.</b> The course projects (DMA02, DMA03, DMA05, DMA06) — exactly what "
               "G1097 lacks: RecyclerView, ViewBinding, menus, the lifecycle — and the complete "
               "repo history."),
    },
}


def section_page(slug, ro_t, en_t, ro_s, en_s, nums, lang, outdir, base, ui, lcol):
    """Write a section landing page."""
    title = en_t if lang == "en" else ro_t
    subtitle = en_s if lang == "en" else ro_s
    hero = HERO[slug][lang]
    cards = "".join(chapter_card_html(n, lang, parsed, totals) for n in nums)
    stotal = section_check_total(nums, totals)
    label_checks = "bife" if lang != "en" else "checks"
    label_progress = "Progresul tău" if lang != "en" else "Your progress"

    body = f"""
<section class="hero">
  <p class="eyebrow">{htmlmod.escape(title)}</p>
  <h1>{htmlmod.escape(title)}</h1>
  <p>{hero}</p>
</section>

<section class="progress-card">
  <h2>{label_progress}</h2>
  <div class="bar"><i id="sectionBar"></i></div>
  <div class="progress-meta">
    <span><b id="sectionPct">0%</b> · <b id="sectionDone">0</b> / <b id="sectionTotal">{stotal}</b> {label_checks}</span>
  </div>
</section>

<div class="chapter-grid" id="sectionGrid" data-section-total="{stotal}">
{cards}
</div>
"""
    page = HEAD.format(
        lang=lang,
        title=f"{title} · Test 1 — G1097",
        desc=subtitle,
        base=base,
        brand_index="index.html",
        section_nav=section_nav_html(slug, lang),
        other_href=(f"en/{slug}.html" if lang == "ro" else f"../{slug}.html"),
        other_label=ui["lang_other"],
        other_title=ui["lang_other_title"],
        sidebar=sidebar_html("", lang, total_checks),
        main_attrs=f' data-section="{slug}"',
        body=body,
        pager="",
    )
    open(os.path.join(outdir, f"{slug}.html"), "w", encoding="utf-8").write(page)


for lang in ("ro", "en"):
    base = "" if lang == "ro" else "../"
    outdir = OUT if lang == "ro" else os.path.join(OUT, "en")
    ui = UI[lang]
    lcol = 1 if lang == "en" else 0

    # ---- individual chapters
    for idx, ch in enumerate(CHAPTERS):
        num, label = ch[0], ch[1 + lcol]
        md_text, _items = parsed[lang][num]
        body = render(md_text)
        page = HEAD.format(
            lang=lang,
            title=ui["ch_title"].format(num, label),
            desc=ui["ch_desc"].format(num, label),
            base=base,
            brand_index="index.html",
            section_nav=section_nav_html(SECTION_OF.get(num, ""), lang),
            other_href=(f"en/cap-{num}.html" if lang == "ro" else f"../cap-{num}.html"),
            other_label=ui["lang_other"],
            other_title=ui["lang_other_title"],
            sidebar=sidebar_html(num, lang, total_checks),
            main_attrs=f' data-chapter="{num}." data-total="{totals[num]}"',
            body=body,
            pager=pager_html(idx, lang),
        )
        open(os.path.join(outdir, f"cap-{num}.html"), "w", encoding="utf-8").write(page)

    # ---- the three sections + appendix
    for slug, ro_t, en_t, ro_s, en_s, nums in SECTIONS:
        section_page(slug, ro_t, en_t, ro_s, en_s, nums, lang, outdir, base, ui, lcol)
    section_page(*APPENDIX, lang=lang, outdir=outdir, base=base, ui=ui, lcol=lcol)

    # ---- root index: the chooser
    picks = []
    for slug, ro_t, en_t, ro_s, en_s, nums in SECTIONS:
        title = en_t if lang == "en" else ro_t
        subtitle = en_s if lang == "en" else ro_s
        stotal = section_check_total(nums, totals)
        picks.append(
            f'<a class="path-card" href="{slug}.html">'
            f'<div class="pc-title">{htmlmod.escape(title)}</div>'
            f'<div class="pc-sub">{htmlmod.escape(subtitle)}</div>'
            f'<div class="pc-meta"><b>{len(nums)}</b> '
            + ("capitole" if lang != "en" else "chapters")
            + f' · <b>{stotal}</b> '
            + ("bife" if lang != "en" else "checks")
            + '</div></a>'
        )
    atotal = section_check_total(APPENDIX[5], totals)
    picks.append(
        f'<a class="path-card path-card-soft" href="anexe.html">'
        f'<div class="pc-title">{htmlmod.escape(APPENDIX[2] if lang == "en" else APPENDIX[1])}</div>'
        f'<div class="pc-sub">{htmlmod.escape(APPENDIX[4] if lang == "en" else APPENDIX[3])}</div>'
        f'<div class="pc-meta"><b>5</b> '
        + ("capitole" if lang != "en" else "chapters")
        + f' · <b>{atotal}</b> '
        + ("bife" if lang != "en" else "checks")
        + '</div></a>'
    )

    if lang == "ro":
        intro = ("Aplicația <b>G1097 (Movies)</b>, explicată pe trei căi. Alege ce ți se potrivește "
                 "acum — poți reveni oricând, iar progresul e același în toate.")
        howto = """
<ol>
  <li>Alege una din cele trei căi de mai sus.</li>
  <li><b>Bifează</b> căsuța de sub fiecare titlu când ai terminat. Progresul se salvează
      în browser — fără cont, fără cookie-uri, fără server.</li>
  <li><b>Indiciul</b> doar dacă te blochezi. <b>Soluția</b> doar după ce ai încercat.</li>
  <li>Progresul trăiește în acest browser. Dacă ștergi datele site-ului, îl pierzi —
      folosește <b>Export</b> ca să ai o copie.</li>
</ol>
<blockquote><p><b>Regula de aur:</b> nu copia. Tastează. Fiecare dată când copiezi, pierzi
exact exercițiul pe care îl vei da la test.</p></blockquote>
<p>Sursa de adevăr e commitul <code>d719ffc</code> (<code>G1097_S07</code>, 2026-11-09) din
repo-ul <code>mihaidoinea/dma2026</code>. Materialul e construit strict pe grupa <b>1097</b>.</p>
"""
    else:
        intro = ("The <b>G1097 (Movies)</b> app, explained three ways. Pick whichever fits you "
                 "right now — you can come back anytime, and the progress is shared.")
        howto = """
<ol>
  <li>Pick one of the three paths above.</li>
  <li><b>Tick</b> the box under each title when you finish it. Progress is saved in your
      browser — no account, no cookies, no server.</li>
  <li><b>The hint</b> only if you get stuck. <b>The solution</b> only after you've tried.</li>
  <li>Progress lives in this browser. If you clear the site data you lose it —
      use <b>Export</b> to keep a copy.</li>
</ol>
<blockquote><p><b>Golden rule:</b> don't copy. Type it. Every time you copy, you lose exactly
the exercise you'll be given in the test.</p></blockquote>
<p>The source of truth is commit <code>d719ffc</code> (<code>G1097_S07</code>, 2026-11-09)
in the <code>mihaidoinea/dma2026</code> repository. The material is built strictly on group
<b>1097</b>.</p>
"""

    index_body = f"""
<section class="hero">
  <h1>Test 1 — G1097</h1>
  <p>{intro}</p>
</section>

<section class="progress-card">
  <h2>{ui["progress"]}</h2>
  <div class="bar"><i id="globalBar"></i></div>
  <div class="progress-meta">
    <span><b id="globalPct">0%</b> {ui["complete"]}</span>
    <span><b id="globalDone">0</b> {ui["of"]} <b id="globalTotal">{total_checks}</b> {ui["checks"]}</span>
    <span>{ui["saved_local"]}</span>
  </div>
  <div class="tools">
    <button id="exportBtn" type="button">{ui["export"]}</button>
    <button id="importBtn" type="button">{ui["import"]}</button>
    <button id="resetBtn" type="button" class="danger">{ui["reset"]}</button>
    <input id="importFile" type="file" accept="application/json" hidden>
  </div>
</section>

<h2 style="margin-top:0">{'Alege o cale' if lang != 'en' else 'Pick a path'}</h2>
<div class="path-grid">
{''.join(picks)}
</div>

<h2>{ui["howto"]}</h2>
{howto}
"""

    page = HEAD.format(
        lang=lang,
        title=ui["index_title"],
        desc=ui["index_desc"],
        base=base,
        brand_index="index.html",
        section_nav=section_nav_html("", lang),
        other_href=("en/index.html" if lang == "ro" else "../index.html"),
        other_label=ui["lang_other"],
        other_title=ui["lang_other_title"],
        sidebar=sidebar_html("", lang, total_checks),
        main_attrs="",
        body=index_body,
        pager="",
    )
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(page)

json.dump({"totalChecks": total_checks,
           "sections": [{"slug": s[0], "chapters": s[5],
                         "checks": section_check_total(s[5], totals)} for s in SECTIONS] +
                       [{"slug": APPENDIX[0], "chapters": APPENDIX[5],
                         "checks": section_check_total(APPENDIX[5], totals)}],
           "chapters": [{"num": c[0], "ro": c[1], "en": c[2], "checks": totals[c[0]],
                         "section": SECTION_OF.get(c[0], "")} for c in CHAPTERS]},
          open(os.path.join(OUT, "assets", "structure.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("built:", len(CHAPTERS), "chapters +", len(SECTIONS), "sections + appendix")
