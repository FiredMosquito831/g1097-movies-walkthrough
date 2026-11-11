# Chapter 16 — The complete repository history

**Objective:** see how the `dma2026` repository evolved from the first commit to `d719ffc` — 44 commits, 9 projects, 13 October → 9 November 2026.

**Estimated time:** 25–35 min (reading).

**Source:** `git log` on `mihaidoinea/dma2026`, branch `main`, HEAD `d719ffc`.

> **Why it's useful:** in the exam, questions like "what was added in S05?" or "why does the code look like this?" are answered from the history. And you see how a professor builds their material incrementally.

---

## Step 16.1 — The big picture

### The numbers

| | |
|---|---|
| Commits | **44** |
| First date | **13 October 2026** — `8b04238` "DMA02" |
| Last date | **9 November 2026** — `d719ffc` "G1097_S07" |
| Projects | 9 (DMA02, DMA03, DMA05, DMA06, G1096, G1097, G1098, G1099) |
| Days with commits | 13, 19, 21, 22, 26, 27, 29 Oct · 2, 3, 4, 9 Nov |
| Merges | 3 (`e2ba1f5`, `9dc5ebc` + the first) |

### Structure by period

| Period | What happened |
|---|---|
| **13 Oct** | first commit: `DMA02` — the lifecycle demonstration |
| **19–22 Oct** | `DMA03` (navigation) + **S04 for all 4 groups** |
| **26–29 Oct** | **major restructuring** + **S05 for all groups** |
| **2–4 Nov** | **S06 for all groups** + `DMA06` (ListView/RecyclerView) |
| **9 Nov** | `G1097_S07` — only `movie_item.xml` |

---

## Step 16.2 — The complete chronology

### 13 October

| Commit | What |
|---|---|
| `8b04238` | **DMA02** — the first commit in the repo. `Application` class + the activity lifecycle |

### 19 October

| Commit | What |
|---|---|
| `a08f665` | **G1097_S04** — the first commit of your group. Gradle skeleton + `MainActivity` (24 lines) + `activity_main.xml` (19 lines) |

### 21 October — the busiest day (13 commits)

| Commit | What |
|---|---|
| `063ceed`, `ba82276`, `42baa90`, `858f7ea` | **DMA03** — navigation, menus, dialogs (4 commits) |
| `f8f653b` | **G1097_S04** — `ItemActivity` appears (43 lines), `activity_item.xml` (10 lines), `strings.xml` (22 lines). **This is where ListView is born** |
| `1993e6c` | **G1097_S04** — `gradle-daemon-jvm.properties` (12 lines, configuration) |
| `695bb34`, `a7610f3`, `902e1a0` | **G1098_S04** (3 commits) |
| `7a5b342`, `680f602` | **G1096_S04** (2 commits) |
| `919b765`, `11eb644` | **G1099_S04** (2 commits) |
| `7d43292` | "Add course information to README" — the repo README |

**What actually happened:** in a single day, the professor laid down the skeleton for all 4 groups and finished DMA03. Each group got 2–3 separate commits — hence the large number.

### 22 October

| Commit | What |
|---|---|
| `b7633cd` | **DMA03** — the project's last commit |
| `e2ba1f5` | **Merge** remote-tracking branch 'origin/main' |

### 26 October — the restructuring

| Commit | What |
|---|---|
| `51863a3` | **"Project restructured"** — the most important structural commit |
| `2e4e176` | **G1097_S05** — `activities/` + `model/` packages, `Movie.java` appears (14 lines), `outline_add_24.xml`, `activity_item.xml` **+115 lines** |
| `8a91c82` | **G1097_S05** — `ItemActivity` **+62 lines** (the form logic) |

### What "Project restructured" did

The commit moved the structure from **one module per group** (`G1097/app/src/main/...`) to **module at project level**:

```
BEFORE                           AFTER
G1097/                           G1097/
├── app/                         ├── src/main/         ← src moves up
│   ├── build.gradle.kts         ├── build.gradle.kts
│   ├── src/main/                └── gradle/
│   └── gradle/                      
├── gradlew                      (the wrapper disappears)
├── gradlew.bat
└── settings.gradle.kts
```

Consequences:
- `gradlew`, `gradlew.bat`, the Gradle wrapper **disappear** from each module
- `libs.versions.toml` moves to the root level
- `settings.gradle.kts` remains only at the root

> **Remember:** before 26 Oct, each group was an independent project. After, they're all modules of a single project. That's why `G1097`'s `build.gradle.kts` at `d719ffc` only has `plugins { alias(libs.plugins.android.application) }` — versions come from the root catalog.

### 27 October — S05 for all groups

| Commit | What |
|---|---|
| `a1c6b74`, `e65cc20` | **G1096_S05** |
| `f7c12dc` | **G1097_S05** — `ItemActivity` reworked, `Movie` +37 lines, `activity_item` +29, `strings` +12 |
| `8fbcf29` | **G1097_S05** — a single line changed (a fix) |
| `71da3c8` | **G1098_S05** |
| `de8a681`, `be7f6b8` | **G1099_S05** |

### 29 October

| Commit | What |
|---|---|
| `4a60b5d` | **G1098_S05** — the last S05, two days behind the other groups |

### 2 November

| Commit | What |
|---|---|
| `2efafdb` | **G1097_S06** — `activity_item.xml` **+306 lines** (the big form), `MainActivity` +52, `Movie` +19. **The largest commit in G1097's history** |

### 3 November

| Commit | What |
|---|---|
| `99740e7` | **G1096_S06** |
| `c14a1f2` | **G1099_S06** |
| `2a1ae9a` | **G1099** — "Add fields and methods for movie details management" (`ItemActivity` +85) |
| `02499dc` | **G1099** — "Add getters and setters for Movie class attributes" (`Movie` +80) |
| `8c878b6` | **G1099** — "Initialize movie adapter and add sample movies" (`MainActivity` +12) |

**Observation:** the three descriptive commits touch **G1099**, not G1098. And they're written in a different style: English sentences ("Add getters and setters…") instead of `G1099_S06`.

> **Why it's interesting:** it suggests part of the G1099 code was committed by someone else (probably a student who contributed to the repo, or the professor working in another style). The rest of the history is uniform: `G<group>_S<session>`.

### 4 November — the biggest day after 21 Oct

| Commit | What |
|---|---|
| `43e4c85`, `e58023a` | **G1098_S06** (two commits with the same message) |
| `9dc5ebc` | **Merge** remote-tracking branch 'origin/main' |
| `4e6b729`, `2d891ef` | **DMA06** — the ListView/RecyclerView project |
| `2c4fc99` | **G1096_S06** |
| `f7fb315` | **G1097_S06** — `ItemActivity` **+125 lines** (validation, date picker), `Movie` **+83**, `build.gradle.kts` +2 |
| `e58023a` → `44139d7` | **G1099_S06** |

### 9 November

| Commit | What |
|---|---|
| `d719ffc` | **G1097_S07** — **only `movie_item.xml`, +136 lines.** No Java code |

---

## Step 16.3 — G1097's evolution, session by session

### The table you need to know

| Session | Date | What was added | Lines of Java |
|---|---|---|---|
| **S04** | 19 + 21 Oct | skeleton, `MainActivity`, `ItemActivity`, a minimal `activity_item`, `strings` | ~90 |
| **S05** | 26–27 Oct | `activities`/`model` packages, `Movie`, FAB, the medium form | ~250 |
| **S06** | 2 + 4 Nov | the big form (`+306` XML lines), validation, date picker | ~300 |
| **S07** | 9 Nov | **only the card layout** for the future `RecyclerView` | **0** |

### What that means concretely

**S04** — the app has two empty screens that can open. The buttons do nothing useful.

**S05** — the `Movie` model appears. The form has fields. The list shows something.

**S06** — the form is complete: all 10 fields, `DatePickerDialog`, validation, `SeekBar` with a live value.

**S07** — the professor prepares **the next lab**: he commits `movie_item.xml`, the pretty card with poster, title, stars, chips. But he doesn't write the adapter.

### The proof that S07 is preparation, not delivery

```bash
git show --stat d719ffc
# G1097/src/main/res/layout/movie_item.xml | 136 +++++++++++++++++++
# 1 file changed, 136 insertions(+)

git grep "movie_item" HEAD
# (empty)
```

The file is committed, but **no code references it**. There's no `MovieAdapter`, no `setAdapter` with it, no `tools:listitem`.

> **Conclusion:** at `d719ffc`, the G1097 app is **functional on `ListView`** and has a card layout **prepared but unwired**. Moving to `RecyclerView` is the next lab's topic — which you did locally on 09.11.

---

## Step 16.4 — Comparing the groups

### What differs

| Group | Commits | Last commit | Has S07? | Has `movie_item.xml`? |
|---|---|---|---|---|
| **G1096** | 6 | `2c4fc99` 4 Nov (S06) | no | no |
| **G1097** | 11 | `d719ffc` 9 Nov (S07) | **yes** | **yes** |
| **G1098** | 8 | `e58023a` 4 Nov (S06) | no | no |
| **G1099** | 8 | `44139d7` 4 Nov (S06) | no | no |

### What's identical

At `d719ffc`, **all four** have:

```java
import android.widget.ArrayAdapter;
import android.widget.ListView;

private ListView listView;
private ArrayAdapter<Movie> movieAdapter;
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

The app is the same. Only these differ:
- **G1097** has `movie_item.xml` on top (the RecyclerView preparation)
- **G1099** has 3 commits written in another style (03.11)

### Why G1097 is "the most recent variant"

Because it has **11 commits** versus 6–8, and because it's **the only one with S07**. When the user said "strictly group 1097", that was the criterion.

---

## Step 16.5 — What you can learn from the history

### Three exam questions

**"In which session did `Movie.java` appear?"**
S05, commit `2e4e176` (26 Oct). It has 14 lines — just the fields.

**"When was `DatePickerDialog` added?"**
S06, commit `f7fb315` (4 Nov), `ItemActivity` +125 lines. (`2efafdb` on 2 Nov is the XML form.)

**"Why is `activity_item.xml` 451 lines?"**
Because it was built in three waves: 10 lines in S04, +115 in S05, +306 in S06.

### The command that gives you everything

```bash
git log --reverse --format='%h %ad %s' --date=short -- G1097
```

And for a specific commit:

```bash
git show --stat f7fb315     # which files it touched
git show f7fb315 -- G1097/src/main/java/ro/ase/ie/g1097/model/Movie.java   # the exact diff
```

---

## Step 16.6 — Process lessons

### How the professor works

1. **Small, frequent commits.** 13 commits in one day. Each group gets what it needs, separately.
2. **Uniform messages:** `G<group>_S<session>`. You can reconstruct everything from `git log`.
3. **One commit per group per session.** A single "S06 all groups" commit would have made the history unreadable.
4. **Rare but large restructurings.** `51863a3` touched the whole repo. One commit, one architectural change.
5. **Prepares the next lab in advance.** `movie_item.xml` is committed a week before it's used.

### What you learn for your own code

- One commit = one change with its own meaning. Don't mix "add the form" with "move folders".
- Messages should say **what**, not "update" or "fix".
- When you restructure, do it in a separate commit, so you can go back.
- If you add something not yet used, say so in the message ("prepare layout for RecyclerView").

---

## Chapter 16 summary

- **44 commits**, 13 Oct → 9 Nov, 9 projects.
- **21 Oct** = the day with the most commits (13) — all groups' skeletons + DMA03.
- **26 Oct** = "Project restructured" — from independent modules to modules of one project.
- **G1097**: S04 (90 lines) → S05 (250) → S06 (300) → **S07 (0 Java lines)**.
- **S07** = only `movie_item.xml`, not wired to anything. Preparation for the next lab.
- All groups have `ListView` at `d719ffc`. RecyclerView isn't in the repo — only in `DMA06` (as a demonstration) and in your local work.
- G1099 has 3 commits in another style (03.11) — possibly an external contribution.

**End of part two.** Back to the [overview](index.html).
