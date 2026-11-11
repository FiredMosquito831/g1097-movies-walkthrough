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


