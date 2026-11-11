# Test 1 — G1097: the Movies app, from scratch

**Target:** to be able to rebuild on your own, starting from an empty project, the `G1097` app at the state of commit **`d719ffc`** (`G1097_S07`, 2026-11-09) — and then to extend it.

**Source of truth:** `Android dev/dma2026-sync-2026-11-10/G1097/` (clean clone of the `mihaidoinea/dma2026` repo, branch `main`, HEAD `d719ffc`).
**Final code, copied here:** `cod-final/` — 17 files, with SHA-256 hashes in `cod-final/HASH-URI.txt`.

> **Golden rule:** don't copy. Type. Every time you copy, you lose exactly the exercise you'll be given on the test.
> When you make a mistake — and you will — read the error in `Build` before looking at the solution. The error tells you the file and the line.

---

## What you build

An app with **two screens**:

| Screen | What it does |
|---|---|
| `MainActivity` | Displays a list of movies. Floating “+” button at the bottom right. Tap a movie → you edit it. |
| `ItemActivity` | Full movie form: title, genre, date, budget, duration, rating, “recommended”, “watchlist”, parental guidance, poster. The button saves and returns. |

Data lives **in memory**, in an `ArrayList<Movie>` inside `MainActivity`. There is no database, no network, no files. Everything is lost when the app closes — and that is intentional.

```
MainActivity
  ├── List<Movie> movies        ← singura sursă de date
  ├── ArrayAdapter<Movie>       ← leagă lista de ListView
  └── ActivityResultLauncher    ← așteaptă răspuns de la ItemActivity
                │
                │  Intent + Movie (Serializable) + position
                ▼
ItemActivity
  ├── citește Movie din Intent (dacă există)
  ├── umple formularul
  └── la Save: construiește Movie nou → setResult(RESULT_OK) → finish()
```

---

## How to use this material

For each step:

1. **Read “Why” and “How”.** Do not skip “Why” — on the test you are asked to explain, not just to write code.
2. **Close the solution.** Do the exercise on your own.
3. **Run.** `Run ▶` on the emulator. If it doesn't compile, read the error.
4. **Only then** open the hint. If it still doesn't work, open the solution.
5. **Compare** your code with the solution **line by line**. Does anything differ? Ask yourself why.
6. **Check off** the step in the progress table below.

A step is “done” when: the code compiles, the app runs, and you can explain **without looking** why you wrote what you wrote.

---

## Chapter order

### Path 1 — Rebuild from scratch

| # | File | What you learn | Steps |
|---|---|---|---|
| 01 | [01 - Setup and skeleton.md](01%20-%20Setup%20and%20skeleton.md) | Project, Gradle, manifest, first running screen | 1.1–1.10 |
| 02 | [02 - The Movie model.md](02%20-%20The%20Movie%20model.md) | Model class, types, `Serializable`, constructors, getters | 2.1–2.9 |
| 03 | [03 - Main screen - layout.md](03%20-%20Main%20screen%20-%20layout.md) | `FrameLayout`, `ListView`, `FloatingActionButton`, vector drawable | 3.1–3.7 |
| 04 | [04 - MainActivity - the list.md](04%20-%20MainActivity%20-%20the%20list.md) | `onCreate`, `ArrayAdapter`, demo data, `Calendar`, insets | 4.1–4.10 |
| 05 | [05 - The form - part 1.md](05%20-%20The%20form%20-%20part%201.md) | `ScrollView`, `MaterialCardView`, `TextInputLayout`, `Spinner` | 5.1–5.11 |
| 06 | [06 - The form - part 2.md](06%20-%20The%20form%20-%20part%202.md) | `SeekBar`, `RatingBar`, `MaterialSwitch`, `CheckBox`, `RadioGroup`, `MaterialButton` | 6.1–6.12 |
| 07 | [07 - ItemActivity - reading and writing.md](07%20-%20ItemActivity%20-%20reading%20and%20writing.md) | `findViewById`, listeners, `DatePickerDialog`, `saveMovie` | 7.1–7.11 |
| 08 | [08 - Navigation and the result.md](08%20-%20Navigation%20and%20the%20result.md) | `Intent`, `ActivityResultLauncher`, `Serializable`, `RESULT_OK` | 8.1–8.9 |
| 09 | [09 - Edit mode.md](09%20-%20Edit%20mode.md) | `fillForm`, `position`, add vs. replace | 9.1–9.7 |
| 10 | [10 - Rebuild from scratch.md](10%20-%20Rebuild%20from%20scratch.md) | Final drill, timed, without the material | — |
| 11 | [11 - Extensions.md](11%20-%20Extensions.md) | `RecyclerView`, `ViewHolder`, `onBindViewHolder`, new attributes | 11.1–11.14 |

### Appendix — the other groups, the course projects and the repo history

| # | File | What you learn | Steps |
|---|---|---|---|
| 29 | [29 - G1096 code annotated.md](29%20-%20G1096%20code%20annotated.md) | G1096 code block by block, plus the differences from G1097 (`posterUrl`, dead imports, the empty constructor) | 29.1–29.9 |
| 30 | [30 - G1098 code annotated.md](30%20-%20G1098%20code%20annotated.md) | G1098 code block by block — the only group with a complete `toString()` and a different FAB drawable | 30.1–30.9 |
| 31 | [31 - G1099 code annotated.md](31%20-%20G1099%20code%20annotated.md) | G1099 code block by block, including the dead `android.media.Rating` import | 31.1–31.9 |
| 12 | [12 - DMA06 - ListView vs RecyclerView.md](12%20-%20DMA06%20-%20ListView%20vs%20RecyclerView.md) | The 3 steps on the same data: `ArrayAdapter` → `BaseAdapter` → `RecyclerView` | 12.1–12.7 |
| 13 | [13 - DMA05 - ViewBinding.md](13%20-%20DMA05%20-%20ViewBinding.md) | `ViewBinding` vs `findViewById`, all the input widgets | 13.1–13.6 |
| 14 | [14 - DMA03 - Navigation and menus.md](14%20-%20DMA03%20-%20Navigation%20and%20menus.md) | `DrawerLayout`, `NavigationView`, `PopupMenu`, Back, `AlertDialog`, `Snackbar` | 14.1–14.8 |
| 15 | [15 - DMA02 - Application and lifecycle.md](15%20-%20DMA02%20-%20Application%20and%20lifecycle.md) | The full lifecycle, the `Application` class, implicit `Intent` | 15.1–15.6 |
| 16 | [16 - Repository history.md](16%20-%20Repository%20history.md) | All 44 commits, per-session evolution, cross-group comparison | 16.1–16.6 |
| 25 | [25 - DMA02 code annotated.md](25%20-%20DMA02%20code%20annotated.md) | DMA02 code block by block: `Application`, lifecycle, implicit `Intent` | 25.1–25.6 |
| 26 | [26 - DMA03 code annotated.md](26%20-%20DMA03%20code%20annotated.md) | DMA03 code block by block: drawer, toolbar, menus, dialogs | 26.1–26.8 |
| 27 | [27 - DMA05 code annotated.md](27%20-%20DMA05%20code%20annotated.md) | DMA05 code block by block: `ViewBinding`, every widget | 27.1–27.6 |
| 28 | [28 - DMA06 code annotated.md](28%20-%20DMA06%20code%20annotated.md) | DMA06 code block by block: the three list steps | 28.1–28.10 |

> **Part I** builds your app. **Part II** covers the rest of the repo: the annotated code of the other three groups (29–31 — the same app, a different variant, with the differences from 1097 spelled out), the four course projects (which contain exactly what G1097 lacks — RecyclerView, ViewBinding, menus, the lifecycle) and the complete history.

### Path 2 — Exam exercises: 60 requirements

Every requirement has: the prompt, files touched, **"How you approach it — your steps"** (4–6 concrete actions), **two graduated hints**, then the collapsible solution with an explanation.

| # | File | Requirement type | Exercises |
|---|---|---|---|
| 17 | [17 - Bank 1 - New attributes.md](17%20-%20Bank%201%20-%20New%20attributes.md) | Add an attribute (`String`, `Integer`, `boolean`, `float`, `ArrayList`, new class) | 17.1–17.10 |
| 18 | [18 - Bank 2 - Bindings and adapters.md](18%20-%20Bank%202%20-%20Bindings%20and%20adapters.md) | Bind values, change a widget, build an adapter | 18.1–18.10 |
| 19 | [19 - Bank 3 - Values in UI and state.md](19%20-%20Bank%203%20-%20Values%20in%20UI%20and%20state.md) | Value → label, widget → model, list → screen, rotation | 19.1–19.10 |
| 20 | [20 - Bank 4 - New controls.md](20%20-%20Bank%204%20-%20New%20controls.md) | Add a button, switch, chip, FAB, spinner | 20.1–20.10 |
| 23 | [23 - Bank 5 - ListView to RecyclerView.md](23%20-%20Bank%205%20-%20ListView%20to%20RecyclerView.md) | The complete migration, in 10 steps that each compile | 23.1–23.10 |
| 24 | [24 - Bank 6 - Persistence and verification.md](24%20-%20Bank%206%20-%20Persistence%20and%20verification.md) | Does the data save? Verification, debugging, `SharedPreferences` | 24.1–24.10 |

### Path 3 — Explained code + cheatsheet

| # | File | What it contains |
|---|---|---|
| 21 | [21 - Cheatsheet.md](21%20-%20Cheatsheet.md) | File map, model, IDs, ViewBinding, the listener table, the adapter decision tree, intents, lifecycle, common errors, exam recipes |
| 22 | [22 - Annotated code.md](22%20-%20Annotated%20code.md) | All six G1097 files explained block by block, plus the complete flow |

### Path 4 — Exam recipes

Every requirement type that can come up, on one page: the exact steps, the files touched, the minimum code that compiles, why it works and the mistake that costs marks. Start with the plan.

| # | File | What it contains | Checks |
|---|---|---|---|
| 32 | [32 - The guided plan.md](32%20-%20The%20guided%20plan.md) | 10 sessions, ~18 h, with exact pointers to what you read and practise across the whole site | 10 |
| 33 | [33 - Recipes 1 - model and UI.md](33%20-%20Recipes%201%20-%20model%20and%20UI.md) | 16 recipes: attributes (String, int, Integer, float, boolean, list, composed, derived), type change, rename, widgets, buttons, a new screen | 16 |
| 34 | [34 - Recipes 2 - bindings and adapters.md](34%20-%20Recipes%202%20-%20bindings%20and%20adapters.md) | 14 recipes: values bound to labels, conditional visibility, validation, `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter`, the full migration, grid, header, click with callback | 14 |
| 35 | [35 - Recipes 3 - Intents and persistence.md](35%20-%20Recipes%203%20-%20Intents%20and%20persistence.md) | 13 recipes: start an activity, simple extras, `Serializable` object, result, result code, implicit `Intent`, rotation, `SharedPreferences` + JSON, `Application` | 13 |
| 36 | [36 - Bank 7 - Intents and navigation.md](36%20-%20Bank%207%20-%20Intents%20and%20navigation.md) | 10 exam-style exercises, with graduated hints and an explained solution | 10 |

---

## Progress table

Check items as you finish them. A chapter is done only when the app **runs** at the end of it.

| Chapter | Read | Exercises done | Runs | Can explain |
|---|---|---|---|---|
| 01 Setup | ☐ | ☐ | ☐ | ☐ |
| 02 Model | ☐ | ☐ | ☐ | ☐ |
| 03 Layout Main | ☐ | ☐ | ☐ | ☐ |
| 04 MainActivity | ☐ | ☐ | ☐ | ☐ |
| 05 Form 1 | ☐ | ☐ | ☐ | ☐ |
| 06 Form 2 | ☐ | ☐ | ☐ | ☐ |
| 07 ItemActivity | ☐ | ☐ | ☐ | ☐ |
| 08 Navigation | ☐ | ☐ | ☐ | ☐ |
| 09 Editing | ☐ | ☐ | ☐ | ☐ |
| 10 Rebuild | ☐ | ☐ | ☐ | ☐ |
| 11 Extensions | ☐ | ☐ | ☐ | ☐ |

---

## Folder structure

```
Exams and tests/test 1/
  README.md                          ← acest fișier
  01 ... 11                          ← capitolele
  cod-final/                         ← codul exact la commitul d719ffc
    AndroidManifest.xml
    build.gradle.kts                 ← build.gradle.kts al modulului G1097
    build-root.gradle.kts            ← build.gradle.kts de la rădăcină
    settings.gradle.kts
    gradle.properties
    gradle/libs.versions.toml
    java/ro/ase/ie/g1097/model/Movie.java
    java/ro/ase/ie/g1097/activities/MainActivity.java
    java/ro/ase/ie/g1097/activities/ItemActivity.java
    res/layout/activity_main.xml
    res/layout/activity_item.xml
    res/layout/movie_item.xml
    res/values/strings.xml
    res/values/colors.xml
    res/values/themes.xml
    res/values-night/themes.xml
    res/drawable/outline_add_24.xml
    HASH-URI.txt
  _progres/                          ← aici lucrezi tu (vezi mai jos)
```

---

## Word version (recommended for reading)

**`Test 1 - G1097 Movies.docx`** — all the material in a single document, **128 pages**.

| | |
|---|---|
| Page | A4, **1.5 cm** margins on all sides |
| Body font | Segoe UI 10.5 pt, line spacing 1.1 |
| Code font | Consolas 8.5 pt, with **syntax highlighting** (tango theme) |
| Table of contents | auto-generated, 124 titles on 3 levels |
| Footer | page number + total, on every page |
| Formatting | headings colored by level (blue → green → violet), code cards with border, tables with blue header and alternating rows, quotes with a yellow bar |

> **Warning:** in Word, `<details>` blocks (Hint / Solution) **cannot be collapsed** — they are converted into visible sections, with level-5 headings. So you see the solution immediately below the exercise. If you want to work without seeing the answer, use the `.md` files (which collapse in any Markdown viewer) or cover the bottom part of the page.

---

## Where you work

**Do not** work in `cod-final/` and **do not** work in `Android dev/dma2026/` (your working clone).
Create your project in `Exams and tests/test 1/_progres/` (the folder exists, it is empty) or anywhere you like, just not in the two above.

Project name when creating it: **`Movies1097`** (or `G1097` — however you like; leave the namespace as `ro.ase.ie.g1097`).

---

## What is NOT in this material

- It does **not** contain the code of groups 1096/1098/1099. The app is the same for all groups; 1097 has the most recent variant. We rely strictly on 1097.
- It does **not** contain `DMA02`, `DMA03`, `DMA05`, `DMA06` (the course projects).
- It does **not** contain `MovieAdapter.java` from `cod-final/`, because it is **not in the repo** at `d719ffc`. The adapter exists only as an uncommitted local modification in the old sync folder. You build it in chapter 11, as an extension — exactly like in the next lab.

---

## Version notes (read from the repo, not from memory)

| | |
|---|---|
| AGP | `9.4.1` |
| `compileSdk` | `37` (new syntax: `compileSdk { version = release(37) }`) |
| `minSdk` | `33` |
| `targetSdk` | `37` |
| Java | `VERSION_11` (source + target) |
| Material | `1.14.0` |
| AppCompat | `1.8.0` |
| activity-ktx | `1.13.0` |
| viewBinding | `true` (enabled, but unused in the code — see ch. 07) |

If Android Studio suggests newer versions when you create the project, **accept them** — it's not a problem. What matters is understanding the structure, not the numbers.
