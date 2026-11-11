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
    ("25", "Codul DMA02 adnotat", "DMA02 code annotated",
     "25 - Codul DMA02 adnotat.md", "25 - DMA02 code annotated.md"),
    ("26", "Codul DMA03 adnotat", "DMA03 code annotated",
     "26 - Codul DMA03 adnotat.md", "26 - DMA03 code annotated.md"),
    ("27", "Codul DMA05 adnotat", "DMA05 code annotated",
     "27 - Codul DMA05 adnotat.md", "27 - DMA05 code annotated.md"),
    ("28", "Codul DMA06 adnotat", "DMA06 code annotated",
     "28 - Codul DMA06 adnotat.md", "28 - DMA06 code annotated.md"),
    ("29", "Codul G1096 adnotat", "G1096 code annotated",
     "29 - Codul G1096 adnotat.md", "29 - G1096 code annotated.md"),
    ("30", "Codul G1098 adnotat", "G1098 code annotated",
     "30 - Codul G1098 adnotat.md", "30 - G1098 code annotated.md"),
    ("31", "Codul G1099 adnotat", "G1099 code annotated",
     "31 - Codul G1099 adnotat.md", "31 - G1099 code annotated.md"),
    ("32", "Planul ghidat", "The guided plan",
     "32 - Planul ghidat.md", "32 - The guided plan.md"),
    ("33", "Rețete 1 — modelul și interfața", "Recipes 1 — model and UI",
     "33 - Retete 1 - modelul si interfata.md", "33 - Recipes 1 - model and UI.md"),
    ("34", "Rețete 2 — bindinguri și adaptoare", "Recipes 2 — bindings and adapters",
     "34 - Retete 2 - bindinguri si adaptoare.md", "34 - Recipes 2 - bindings and adapters.md"),
    ("35", "Rețete 3 — Intent, persistență, ciclu de viață", "Recipes 3 — Intents, persistence, lifecycle",
     "35 - Retete 3 - Intent si persistenta.md", "35 - Recipes 3 - Intents and persistence.md"),
    ("36", "Bancul 7 — Intent și navigare", "Bank 7 — Intents and navigation",
     "36 - Bancul 7 - Intent si navigare.md", "36 - Bank 7 - Intents and navigation.md"),
    ("37", "Conceptele, explicate", "The concepts, explained",
     "37 - Conceptele explicate.md", "37 - The concepts explained.md"),
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
        "check_recipe": "Am exersat rețeta", "recipes": "rețete",
        "check_concept": "Am înțeles conceptul", "concepts": "concepte",
        "jump_title": "Sari la un fișier sau la o metodă",
        "jump_btn": "Metode",
        "download": "⬇ Descarcă fișierele adnotate (ZIP)",
        "download_note": "Aceleași fișiere, cu comentariile în ele — le deschizi în Android Studio sau în orice editor.",
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
        "check_recipe": "Practised this recipe", "recipes": "recipes",
        "check_concept": "I understand this concept", "concepts": "concepts",
        "jump_title": "Jump to a file or a method",
        "jump_btn": "Methods",
        "download": "⬇ Download the annotated files (ZIP)",
        "download_note": "The same files, with the comments in them — open them in Android Studio or any editor.",
        "lang_other": "RO", "lang_other_title": "Switch to Romanian",
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
    rc_word = "Recipe" if lang == "en" else "Rețeta"
    cp_word = "Concept" if lang == "en" else "Conceptul"

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

            m = re.match(r"^(#{2,4})\s+(?:Re[țt]eta|Recipe)\s+(\d+\.\d+)\s*[—–-]\s*(.+)$", ln)
            if m:
                num, title = m.group(2), m.group(3).strip()
                key = f"rc:{num}"
                items.append({"key": key, "num": num, "kind": "recipe", "title": title})
                out.append(f"## {rc_word} {num} — {title} {{#reteta-{num.replace('.', '-')}}}")
                out.append("")
                out.append(f'<div class="chk chk-rc" data-key="{key}">'
                           f'<span>{ui["check_recipe"]}</span></div>')
                out.append("")
                i += 1
                continue

            m = re.match(r"^(#{2,4})\s+(?:Conceptul|Concept)\s+(\d+\.\d+)\s*[—–-]\s*(.+)$", ln)
            if m:
                num, title = m.group(2), m.group(3).strip()
                key = f"cp:{num}"
                items.append({"key": key, "num": num, "kind": "concept", "title": title})
                out.append(f"## {cp_word} {num} — {title} {{#concept-{num.replace('.', '-')}}}")
                out.append("")
                out.append(f'<div class="chk chk-cp" data-key="{key}">'
                           f'<span>{ui["check_concept"]}</span></div>')
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
    elif num in ("29", "30", "31"):
        key = f"read:{num}"
        title = "Annotated code read"
        marker = f"## {num}.1"
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
    ("retete", "Rețete de examen", "Exam recipes",
     "Fiecare tip de cerință posibilă, pas cu pas: model, interfață, bindinguri, adaptoare, "
     "Intent, persistență — plus planul care te duce prin tot.",
     "Every possible requirement type, step by step: model, UI, bindings, adapters, "
     "Intents, persistence — plus the plan that walks you through all of it.",
     ["32", "33", "34", "35", "36"]),
    ("cod", "Referință", "Reference",
     "Cheatsheet-ul dens și conceptele explicate de la zero: ce sunt, de ce există, cum "
     "funcționează, ce se rupe fără ele.",
     "The dense cheatsheet and the concepts explained from first principles: what they are, "
     "why they exist, how they work, what breaks without them.",
     ["21", "37"]),
]
APPENDIX = ("anexe", "Anexe — celelalte grupe și proiectele de curs",
            "Appendix — the other groups and the course projects",
            "Codul adnotat al grupelor G1096, G1098 și G1099, proiectele DMA02/DMA03/DMA05/DMA06 "
            "și istoricul complet al repo-ului.",
            "The annotated code of groups G1096, G1098 and G1099, the DMA02/DMA03/DMA05/DMA06 "
            "projects and the complete repo history.",
            ["22", "29", "30", "31", "12", "13", "14", "15", "16", "25", "26", "27", "28"])

# chapter number -> project folder under src/, for the annotated-code downloads
ANNOTATED = {
    "22": "G1097", "25": "DMA02", "26": "DMA03", "27": "DMA05",
    "28": "DMA06", "29": "G1096", "30": "G1098", "31": "G1099",
}

def download_html(num: str, base: str, ui: dict) -> str:
    return (
        f'<div class="dl-box">'
        f'<a class="dl-btn" href="{base}downloads/cap-{num}.zip" download>'
        f'{htmlmod.escape(ui["download"])}</a>'
        f'<p class="dl-note">{htmlmod.escape(ui["download_note"])}</p>'
        f'</div>'
    )


# ------------------------------------------------- in-page navigation
def _md_blocks(md: str):
    res, cur, lang = [], None, None
    for line in md.split("\n"):
        if cur is None:
            m = re.match(r"^\s*```(\w*)\s*$", line)
            if m:
                cur, lang = [], m.group(1)
        else:
            if re.match(r"^\s*```\s*$", line):
                res.append((lang, "\n".join(cur)))
                cur = None
            else:
                cur.append(line)
    return res


DECL_CLASS = re.compile(r"^\s*(?:public\s+)?(?:final\s+|abstract\s+)?class\s+(\w+)")
DECL_METHOD = re.compile(
    r"^\s*(?:public|protected|private)\s+"
    r"(?:static\s+|final\s+|abstract\s+|synchronized\s+)*"
    r"([\w<>\[\],.\s]*?)\s*(\w+)\s*\(")
DECL_ID = re.compile(r'android:id="@\+id/(\w+)"')


def _decls(code: str, kind: str):
    """Class / method declarations (java) or android:id values (xml), first occurrence only."""
    out, seen = [], set()
    for i, line in enumerate(code.split("\n")):
        if kind == "xml":
            m = DECL_ID.search(line)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                out.append((i, m.group(1), "id"))
            continue
        m = DECL_CLASS.match(line)
        if m and ("class", m.group(1)) not in seen:
            seen.add(("class", m.group(1)))
            out.append((i, m.group(1), "class"))
            continue
        m = DECL_METHOD.match(line)
        if not m:
            continue
        before = line[:line.index("(")]
        if "=" in before or ";" in before:
            continue
        name = m.group(2)
        kind = "ctor" if (out and out[0][2] == "class" and name == out[0][1]) else "method"
        if (kind, name) in seen:
            continue
        seen.add((kind, name))
        out.append((i, name, kind))
    return out


def subnav_html(body: str, jump_html: str, ui: dict) -> str:
    """Sticky in-page navigation built from the page's own h2/h3 headings."""
    h2s = re.findall(r'<h2 id="([^"]*)">(.*?)</h2>', body, re.S)
    heads = re.findall(r'<(h[23]) id="([^"]*)">(.*?)</\1>', body, re.S)
    if len(h2s) >= 5:                       # long pages: top level only
        heads = [h for h in heads if h[0] == "h2"]
    links = []
    for tag, hid, raw in heads:
        txt = re.sub(r"<[^>]+>", "", raw)
        txt = re.sub(r"\s+", " ", txt).strip()
        if not txt:
            continue
        short = txt.split("—")[0].strip() if "—" in txt else txt
        if len(short) > 42:
            short = short[:40].rstrip() + "…"
        cls = "sn" if tag == "h2" else "sn sn-sub"
        links.append(f'<a class="{cls}" href="#{hid}">{htmlmod.escape(short)}</a>')
    if len(links) < 2:
        return ""
    more = ""
    if jump_html:
        more = (
            f'<button class="sn-more" id="snMore" type="button" aria-expanded="false">'
            f'{htmlmod.escape(ui["jump_btn"])}</button>'
            f'<div class="sn-panel" id="snPanel" hidden>{jump_html}</div>'
        )
    return (
        f'<nav class="subnav" id="subnav"><div class="subnav-inner">'
        f'{"".join(links)}{more}</div></nav>'
    )


def annotate_code_nav(body: str, md_text: str, num: str, ui: dict):
    """Inject an <a id> on every declaration line and return (body, jump_nav_html)."""
    blocks = _md_blocks(md_text)
    pres = list(re.finditer(r"<pre>(.*?)</pre>", body, re.S))
    if not pres or len(pres) != len(blocks):
        return body, ""
    h2s = [(m.start(), m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip())
           for m in re.finditer(r'<h2 id="([^"]*)">(.*?)</h2>', body, re.S)]

    edits, groups = [], []
    for k, (m, (tag, code)) in enumerate(zip(pres, blocks)):
        if tag not in ("java", "xml"):
            continue
        found = _decls(code, tag)
        if not found:
            continue
        inner = m.group(1).split("\n")
        anchors = []
        for i, name, kind in found:
            if not (0 <= i < len(inner)):
                continue
            aid = f"m-{num}-{k}-{i}"
            inner[i] = f'<a id="{aid}"></a>' + inner[i]
            anchors.append((aid, name, kind))
        edits.append((m.start(), m.end(), "<pre>" + "\n".join(inner) + "</pre>"))
        title, hid = "", ""
        for hp, h_id, h_txt in h2s:
            if hp < m.start():
                title, hid = h_txt, h_id
        groups.append((hid, title or f"#{k}", anchors))

    if not edits:
        return body, ""
    out, pos = [], 0
    for start, end, new in edits:
        out.append(body[pos:start])
        out.append(new)
        pos = end
    out.append(body[pos:])
    body = "".join(out)

    items = []
    for hid, title, anchors in groups:
        links = "".join(
            f'<a class="j-{kind}" href="#{aid}">{htmlmod.escape(name)}</a>'
            for aid, name, kind in anchors
        )
        items.append(
            f'<details class="jump-file"><summary>'
            f'<a href="#{hid}">{htmlmod.escape(title)}</a>'
            f'<span class="jump-n">{len(anchors)}</span></summary>'
            f'<div class="jump-links">{links}</div></details>'
        )
    nav = (
        f'<nav class="jump"><p class="jump-title">{htmlmod.escape(ui["jump_title"])}</p>'
        f'{"".join(items)}</nav>'
    )
    return body, nav


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
  <button id="codeBtn" type="button" title="{code_title}">⌨ {code_label}</button>
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
<aside id="codePanel" class="code-panel" aria-hidden="true" data-base="{base}">
  <div class="cp-resize" id="cpResize" title="Drag"></div>
  <div class="cp-head">
    <span class="cp-title">{code_panel_title}</span>
    <input id="cpSearch" type="search" placeholder="{code_search}" autocomplete="off">
    <button id="cpClose" type="button" aria-label="Close">✕</button>
  </div>
  <div class="cp-body">
    <nav id="cpTree" class="cp-tree"><p class="cp-hint">{code_hint}</p></nav>
    <div id="cpCode" class="cp-code"><p class="cp-hint">{code_hint}</p></div>
  </div>
</aside>
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
    for slug, ro_t, en_t, ro_s, en_s, nums in SECTIONS + [APPENDIX]:
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
    rcs = sum(1 for x in items if x["kind"] == "recipe")
    cps = sum(1 for x in items if x["kind"] == "concept")
    meta = []
    if steps:
        meta.append(f'{steps} {ui["steps"]}')
    if exs:
        meta.append(f'{exs} {ui["exercises"]}')
    if rcs:
        meta.append(f'{rcs} {ui["recipes"]}')
    if cps:
        meta.append(f'{cps} {ui["concepts"]}')
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
            parsed[lang][num] = ("", [])
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
    if not parsed["en"][num][0]:
        ro_path = os.path.join(SRC, ch[3])
        if not os.path.isfile(ro_path):
            parsed["en"][num] = ("", [])
            continue
        md_text, items = preprocess(open(ro_path, encoding="utf-8").read(), "en")
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
    "retete": {
        "ro": ("<b>Rețete de examen.</b> Fiecare tip de cerință care poate pica, pe o pagină: "
               "pașii exacți, fișierele atinse, codul minim care compilează, de ce merge așa și "
               "greșeala care costă puncte. Începe cu <b>planul ghidat</b> — te duce prin site, "
               "sesiune cu sesiune."),
        "en": ("<b>Exam recipes.</b> Every requirement type that can come up, on one page: the "
               "exact steps, the files touched, the minimum code that compiles, why it works and "
               "the mistake that costs marks. Start with the <b>guided plan</b> — it walks you "
               "through the site, session by session."),
    },
    "cod": {
        "ro": ("<b>Referință.</b> Două lucruri care nu se învață pe de rost, ci se înțeleg: "
               "<b>cheatsheet-ul</b> — harta fișierelor, ID-uri, listeneri, adaptoare, intents, "
               "erori frecvente — și <b>conceptele explicate de la zero</b>: ce este un View, un "
               "adapter, un Intent, un ciclu de viață, de ce există fiecare și ce se rupe fără el."),
        "en": ("<b>Reference.</b> Two things you don't memorise, you understand: the "
               "<b>cheatsheet</b> — file map, IDs, listeners, adapters, intents, common errors — "
               "and <b>the concepts explained from first principles</b>: what a View is, an "
               "adapter, an Intent, a lifecycle, why each exists and what breaks without it."),
    },
    "anexe": {
        "ro": ("<b>Anexe.</b> Codul adnotat al celorlalte grupe (G1096, G1098, G1099) — aceeași "
               "aplicație, altă variantă, cu diferențele față de 1097 scoase în evidență — plus "
               "proiectele de curs (DMA02, DMA03, DMA05, DMA06), adică exact lucrurile care lipsesc "
               "din G1097: RecyclerView, ViewBinding, meniuri, ciclu de viață. Și istoricul complet "
               "al repo-ului."),
        "en": ("<b>Appendix.</b> The annotated code of the other groups (G1096, G1098, G1099) — the "
               "same app, a different variant, with the differences from 1097 spelled out — plus the "
               "course projects (DMA02, DMA03, DMA05, DMA06), which is exactly what G1097 lacks: "
               "RecyclerView, ViewBinding, menus, the lifecycle. And the complete repo history."),
    },
}


CODE_LABELS = {'ro': {'code_label': 'Cod', 'code_title': 'Deschide browserul de cod', 'code_panel_title': 'dma2026 — cod sursă', 'code_search': 'Caută fișier…', 'code_hint': 'Alege un fișier din stânga.'}, 'en': {'code_label': 'Code', 'code_title': 'Open the code browser', 'code_panel_title': 'dma2026 — source code', 'code_search': 'Search a file…', 'code_hint': 'Pick a file on the left.'}}


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
        code_label=CODE_LABELS[lang]["code_label"],
        code_title=CODE_LABELS[lang]["code_title"],
        code_panel_title=CODE_LABELS[lang]["code_panel_title"],
        code_search=CODE_LABELS[lang]["code_search"],
        code_hint=CODE_LABELS[lang]["code_hint"],
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
        jump = ""
        if num in ANNOTATED:
            body, jump = annotate_code_nav(body, md_text, num, ui)
            block = download_html(num, base, ui)
            cut = body.find("<h2")
            body = (body[:cut] + block + body[cut:]) if cut > 0 else body + block
        sub = subnav_html(body, jump, ui)
        if sub:
            body = sub + body
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
            code_label=CODE_LABELS[lang]["code_label"],
            code_title=CODE_LABELS[lang]["code_title"],
            code_panel_title=CODE_LABELS[lang]["code_panel_title"],
            code_search=CODE_LABELS[lang]["code_search"],
            code_hint=CODE_LABELS[lang]["code_hint"],
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
        f'<div class="pc-meta"><b>{len(APPENDIX[5])}</b> '
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
<p><b>Panoul de cod:</b> butonul <code>⌨ Cod</code> din dreapta sus deschide un browser cu
tot codul sursă al repo-ului — arbore de fișiere în stânga, cod colorat în dreapta. Trage
de marginea lui stângă ca să-l lărgești sau să-l îngustezi. E <b>read-only</b>: editezi în
Android Studio.</p>
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
<p><b>Code panel:</b> the <code>⌨ Code</code> button in the top right opens a browser with the
whole repo source — file tree on the left, highlighted code on the right. Drag its left edge
to widen or narrow it. It is <b>read-only</b>: you edit in Android Studio.</p>
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
        code_label=CODE_LABELS[lang]["code_label"],
        code_title=CODE_LABELS[lang]["code_title"],
        code_panel_title=CODE_LABELS[lang]["code_panel_title"],
        code_search=CODE_LABELS[lang]["code_search"],
        code_hint=CODE_LABELS[lang]["code_hint"],
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


# --------------------------------------------------------------- code browser
CODE_SRC = os.path.join(HERE, "src")
CODE_OUT = os.path.join(OUT, "code")

LEXERS = {
    ".java": "java",
    ".xml": "xml",
    ".kts": "kotlin",
    ".toml": "toml",
    ".properties": "ini",
    ".md": "markdown",
    ".bat": "batch",
    ".gitignore": "text",
    ".keep": "text",
    ".gradlew": "bash",
}


def build_code_browser():
    """Highlight every source file into site/code/<n>.html and write tree.json."""
    from pygments import highlight as pyg_highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter

    if not os.path.isdir(CODE_SRC):
        print("code browser: no src/ folder — skipped")
        return 0

    os.makedirs(CODE_OUT, exist_ok=True)
    rels = []
    for root, dirs, files in os.walk(CODE_SRC):
        dirs.sort()
        for f in sorted(files):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, CODE_SRC).replace("\\", "/")
            rels.append(rel)

    rels.sort(key=lambda p: (p.lower(), p))

    fmt = HtmlFormatter(nowrap=True, cssclass="hl")
    entries = []
    for i, rel in enumerate(rels):
        full = os.path.join(CODE_SRC, rel.replace("/", os.sep))
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        ext = "." + rel.rsplit(".", 1)[-1] if "." in rel.rsplit("/", 1)[-1] else ""
        if rel.endswith(".gitignore") or rel.endswith(".keep") or rel.endswith("gradlew"):
            ext = "." + rel.rsplit("/", 1)[-1]
        name = LEXERS.get(ext, "text")
        try:
            lexer = get_lexer_by_name(name, stripall=False)
        except Exception:
            lexer = get_lexer_by_name("text")
        try:
            html = pyg_highlight(text, lexer, fmt)
        except Exception:
            html = ("<span>" + text.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;") + "</span>")
        with open(os.path.join(CODE_OUT, f"{i}.html"), "w", encoding="utf-8") as out:
            out.write(html)
        entries.append({
            "i": i,
            "p": rel,
            "n": rel.rsplit("/", 1)[-1],
            "l": name,
            "b": len(text.encode("utf-8")),
        })

    with open(os.path.join(OUT, "assets", "tree.json"), "w", encoding="utf-8") as fh:
        json.dump({"files": entries}, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"code browser: {len(entries)} files")
    return len(entries)


build_code_browser()


# --------------------------------------------------------------- downloads
def _norm_code(text: str, kind: str):
    if kind == "xml":
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    else:
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"//[^\n]*", "", text)
    return tuple(l.strip() for l in text.replace("\r\n", "\n").split("\n") if l.strip())


README_TXT = """Fisierele adnotate / Annotated files
====================================

Acestea sunt fisierele sursa ale aplicatiei, cu comentariile de explicatie
adaugate. Codul propriu-zis este identic cu cel din repo-ul
mihaidoinea/dma2026 la commitul d719ffc - singura diferenta sunt liniile
de comentariu.

These are the app's source files with the explanatory comments added. The
code itself is identical to mihaidoinea/dma2026 at commit d719ffc - the only
difference is the comment lines.

Cum le folosesti / How to use them
----------------------------------
1. Dezarhiveaza / Unzip.
2. Structura respecta proiectul real: <Proiect>/src/main/...
   O poti deschide direct in Android Studio (File > Open) sau copia peste
   proiectul tau.
3. Fisierele NU sunt un proiect complet - lipsesc build.gradle si resursele
   care nu sunt acoperite in capitol. Sunt pentru citit si comparat.

by FiredMosquito831
"""


def build_annotated_downloads():
    """One ZIP per annotated chapter, with the annotated files in their real paths."""
    import zipfile

    out = os.path.join(OUT, "downloads")
    os.makedirs(out, exist_ok=True)
    made, skipped = 0, []
    for num, proj in ANNOTATED.items():
        ch = ch_by_num(num)
        md_path = os.path.join(SRC, ch[3])
        root = os.path.join(CODE_SRC, proj)
        if not os.path.isfile(md_path) or not os.path.isdir(root):
            skipped.append(num)
            continue
        index = {}
        for dirpath, _, files in os.walk(root):
            for f in files:
                if not f.endswith((".java", ".xml")):
                    continue
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, CODE_SRC).replace("\\", "/")
                kind = "xml" if f.endswith(".xml") else "java"
                try:
                    body = open(full, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                index[_norm_code(body, kind)] = rel
        md = open(md_path, encoding="utf-8").read()
        written = 0
        zpath = os.path.join(out, f"cap-{num}.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("CITESTE.txt", README_TXT)
            for lang, body in _md_blocks(md):
                if lang not in ("java", "xml"):
                    continue
                rel = index.get(_norm_code(body, lang))
                if rel:
                    z.writestr(rel, body.replace("\r\n", "\n").rstrip() + "\n")
                    written += 1
        if written:
            made += 1
        else:
            os.remove(zpath)
            skipped.append(num)
    print(f"downloads: {made} archives" + (f" (skipped {skipped})" if skipped else ""))
    return made


build_annotated_downloads()
