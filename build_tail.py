
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
  <p style="color:var(--fg-mute);font-size:.95rem">{htmlmod.escape(subtitle)}</p>
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
