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

            m = re.match(r"^(#{3,5})\s+(?:Exerci[iț]iu|Exercise)\s+(\d+\.\d+)(.*)$", ln)
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
    return text, items


def add_drill_checkpoint(md_text: str, num: str, items: list, lang: str) -> str:
    if num != "10":
        return md_text
    key = "drill:10"
    items.append({"key": key, "num": "10", "kind": "drill",
                  "title": "Drill" if lang == "en" else "Drill cronometrat"})
    marker = "## Timing table" if lang == "en" else "## Tabel de cronometrare"
    label = UI[lang]["check_drill"]
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
  <a class="brand" href="{brand_index}">Test 1 <span>· G1097</span></a>
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


def sidebar_html(active: str, lang: str, total_checks: int) -> str:
    ui = UI[lang]
    idx = 1 if lang == "en" else 0
    rows = [
        f'<a href="index.html" class="{"active" if active == "index" else ""}">'
        f'<span class="num">★</span> {ui["overview"]}</a>'
    ]
    for ch in CHAPTERS:
        num, label = ch[0], ch[1 + idx]
        cls = "active" if active == num else ""
        rows.append(
            f'<a href="cap-{num}.html" class="{cls}">'
            f'<span class="num">{num}</span> {htmlmod.escape(label)}</a>'
        )
    return (
        '<aside class="sidebar" id="sidebar">'
        f'<h2>{ui["chapters"]}</h2>'
        f'<nav>{"".join(rows)}</nav>'
        f'<div class="mini-progress" id="miniProgress" data-total="{total_checks}"></div>'
        '</aside>'
    )


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


# --------------------------------------------------------------- build
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "assets"))
os.makedirs(os.path.join(OUT, "en"))

ASSETS_SRC = os.path.join(HERE, "assets")
for f in ("style.css", "app.js"):
    shutil.copy2(os.path.join(ASSETS_SRC, f), os.path.join(OUT, "assets", f))

# ---- pass 1: parse all chapters in both languages, collect the check counts
parsed = {"ro": {}, "en": {}}
meta = []
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

# English falls back to Romanian content if a translation is absent
for ch in CHAPTERS:
    num = ch[0]
    if parsed["en"][num][0] is None:
        md_text, items = preprocess(open(os.path.join(SRC, ch[3]), encoding="utf-8").read(), "en")
        md_text = add_drill_checkpoint(md_text, num, items, "en")
        parsed["en"][num] = (md_text, items)

# totals are the same in both languages (same keys)
totals = {}
for num in parsed["ro"]:
    totals[num] = len(parsed["ro"][num][1])
total_checks = sum(totals.values())
print(f"TOTAL checks: {total_checks}")

# ---- pass 2: write pages
for lang in ("ro", "en"):
    base = "" if lang == "ro" else "../"
    outdir = OUT if lang == "ro" else os.path.join(OUT, "en")
    ui = UI[lang]
    lcol = 1 if lang == "en" else 0

    for idx, ch in enumerate(CHAPTERS):
        num, label = ch[0], ch[1 + lcol]
        md_text, items = parsed[lang][num]
        body = render(md_text)
        other_href = f"en/cap-{num}.html" if lang == "ro" else f"../cap-{num}.html"
        page = HEAD.format(
            lang=lang,
            title=ui["ch_title"].format(num, label),
            desc=ui["ch_desc"].format(num, label),
            base=base,
            brand_index="index.html",
            other_href=other_href,
            other_label=ui["lang_other"],
            other_title=ui["lang_other_title"],
            sidebar=sidebar_html(num, lang, total_checks),
            main_attrs=f' data-chapter="{num}." data-total="{totals[num]}"',
            body=body,
            pager=pager_html(idx, lang),
        )
        open(os.path.join(outdir, f"cap-{num}.html"), "w", encoding="utf-8").write(page)

    # ---- index
    cards = []
    for ch in CHAPTERS:
        num, label = ch[0], ch[1 + lcol]
        items = parsed[lang][num][1]
        steps = sum(1 for x in items if x["kind"] == "step")
        exs = sum(1 for x in items if x["kind"] == "exercise")
        cards.append(
            f'<a class="chapter-card" href="cap-{num}.html" '
            f'data-chapter="{num}." data-total="{totals[num]}">'
            f'<div class="cc-top"><span class="cc-num">{num}</span>'
            f'<span class="cc-title">{htmlmod.escape(label)}</span></div>'
            f'<div class="cc-meta">{steps} {ui["steps"]} · {exs} {ui["exercises"]}'
            f'<span class="cc-done" style="float:right"></span></div>'
            f'<div class="bar"><i></i></div></a>'
        )

    if lang == "ro":
        hero_p = ("Aplicația <b>Movies</b>, reconstruită de la zero. 11 capitole, 97 de pași, "
                  "53 de exerciții. Fiecare pas are un „De ce”, un „Cum” și o verificare; fiecare "
                  "exercițiu are indiciu și soluție pliabile.")
        howto = """
<ol>
  <li><b>Bifează</b> căsuța de sub titlul fiecărui pas când l-ai terminat. Progresul
      se salvează automat în browser — fără cont, fără cookie-uri, fără server.</li>
  <li><b>Deschide indiciul</b> doar dacă te blochezi. <b>Soluția</b> doar după ce ai încercat.</li>
  <li><b>Rulează</b> aplicația după fiecare pas. Un pas nu e gata dacă nu compilează.</li>
  <li>La finalul capitolului 10 ai un <b>drill cronometrat</b>: reconstruiești tot, fără material.</li>
  <li>Progresul trăiește în acest browser. Dacă ștergi datele site-ului, îl pierzi —
      folosește <b>Export</b> ca să ai o copie.</li>
</ol>
<blockquote><p><b>Regula de aur:</b> nu copia. Tastează. Fiecare dată când copiezi, pierzi
exact exercițiul pe care îl vei da la test. Când greșești — și vei greși — citește eroarea
din <code>Build</code> înainte să te uiți la soluție.</p></blockquote>
<p>Sursa de adevăr este commitul <code>d719ffc</code> (<code>G1097_S07</code>, 2026-11-09)
din repo-ul <code>mihaidoinea/dma2026</code>. Materialul e construit strict pe grupa
<b>1097</b> — aplicația e aceeași la toate grupele, dar 1097 are varianta cea mai recentă.</p>
<p>Codul final, cu hash-uri SHA-256, este în folderul <code>cod-final/</code> al
materialului. Nu îl copia — îl reconstruiești.</p>
"""
    else:
        hero_p = ("The <b>Movies</b> app, rebuilt from scratch. 11 chapters, 97 steps, "
                  "53 exercises. Every step has a “Why”, a “How” and a check; every exercise "
                  "has a collapsible hint and solution.")
        howto = """
<ol>
  <li><b>Tick</b> the box under each step title when you finish it. Progress is saved
      automatically in your browser — no account, no cookies, no server.</li>
  <li><b>Open the hint</b> only if you get stuck. <b>The solution</b> only after you've tried.</li>
  <li><b>Run</b> the app after every step. A step is not done if it doesn't compile.</li>
  <li>At the end of chapter 10 there's a <b>timed drill</b>: rebuild everything, no material.</li>
  <li>Progress lives in this browser. If you clear the site data you lose it —
      use <b>Export</b> to keep a copy.</li>
</ol>
<blockquote><p><b>Golden rule:</b> don't copy. Type it. Every time you copy, you lose exactly
the exercise you'll be given in the test. When you get it wrong — and you will — read the
error from <code>Build</code> before you look at the solution.</p></blockquote>
<p>The source of truth is commit <code>d719ffc</code> (<code>G1097_S07</code>, 2026-11-09)
in the <code>mihaidoinea/dma2026</code> repository. The material is built strictly on group
<b>1097</b> — the app is the same for every group, but 1097 has the most recent version.</p>
<p>The final code, with SHA-256 hashes, is in the material's <code>cod-final/</code> folder.
Don't copy it — rebuild it.</p>
"""

    index_body = f"""
<section class="hero">
  <h1>Test 1 — G1097</h1>
  <p>{hero_p}</p>
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

<h2 style="margin-top:0">{ui["chapters"]}</h2>
<div class="chapter-grid" id="chapterGrid">
{''.join(cards)}
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
        other_href="en/index.html" if lang == "ro" else "../index.html",
        other_label=ui["lang_other"],
        other_title=ui["lang_other_title"],
        sidebar=sidebar_html("index", lang, total_checks),
        main_attrs="",
        body=index_body,
        pager="",
    )
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(page)

json.dump({"totalChecks": total_checks,
           "chapters": [{"num": c[0], "ro": c[1], "en": c[2], "checks": totals[c[0]]}
                        for c in CHAPTERS]},
          open(os.path.join(OUT, "assets", "structure.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("built RO + EN:", len(CHAPTERS), "chapters each")
