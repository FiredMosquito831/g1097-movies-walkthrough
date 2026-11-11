# Chapter 32 — The guided plan: from zero to "I can take the test"

You have read the chapters. You have done the exercises. Now the problem is no longer "what do I learn", but "in what order, how much time on each, and how do I know I am ready".

This chapter is the answer: **ten sessions, 18 hours, a single thread**. Each session has a goal, a time, what you read, what you practise and an exit test. You do not move on until you pass the test.

**What this chapter is not:** it is not a second theory. It does not explain `RecyclerView` and does not repeat the recipes. It points to them and tells you only what to take from each, in what order and for how long.

**How you use it:**

1. One session at a time, with the timer running. The sessions have different times because they have different difficulty — do not equalise them.
2. Read the "You are ready when" rubric **before** you start. It looks like a detail; in reality it is the only thing that tells you whether you have finished or just sat there.
3. If you do not pass the exit test, you do not move on. You repeat the session the next day. A repeated session costs 2 hours; a missing foundation costs the whole test.
4. You tick the table below. Progress is seen, not felt.

**What must exist before session 1:** the `Movies1097` project, compiling and running, built in chapters [01](cap-01.html)–[11](cap-11.html). If you do not have it, the plan has nothing to lean on — first the app, then the plan.

**The map of the ten sessions:**

| # | Session | Time | What remains after it | Chapters |
|---|---|---|---|---|
| 1 | The map | 2 h | you know which file you touch for any requirement | 21, 22 |
| 2 | The model | 1.5 h | you add an attribute in 8 minutes | 33.1–33.6, 17 |
| 3 | The interface | 1.5 h | you place a widget and a button with a listener | 33.11–33.16, 20 |
| 4 | The bindings | 2 h | you bind a widget to a label | 34.1–34.6, 18, 19 |
| 5 | The adapters | 2 h | you write an adapter from scratch | 34.7–34.9, 18 |
| 6 | RecyclerView | 2.5 h | you migrate the list in 25 minutes | 23, 34.10 |
| 7 | Intent | 2 h | you send and receive data between screens | 35.1–35.8, 36 |
| 8 | Persistence | 2 h | the data survives rotation and closing | 35.9–35.13, 24 |
| 9 | The simulation | 1.5 h | you take the test in 30 minutes | 17.10, 20.10 |
| 10 | Test day | 1 h | you have the 30-minute plan | 32.10 |

**What a session looks like.** They all have the same five rubrics, in the same order:

| Rubric | What it asks of you |
|---|---|
| **Goal** | one sentence: what you must know at the end |
| **Time** | how long it takes, split by activities |
| **You read** | exactly which chapters and sections, not "the material" |
| **You practise** | the exercises that fix the work of the session |
| **You are ready when** | a checkable test, not an impression |

> **The 18-hour rule:** if a session takes you twice as long, you are not slow — the session before it did not stick. Go back to it. The plan is sequential on purpose: each session uses something built in the previous one.

---

## 32.0 What the test looks like

Two requirements. Thirty minutes. The `G1097` app at the state in commit `d719ffc` — exactly the one you built in chapters 01–11.

Each requirement is a sentence of the form "Add the director's name to the movie and display it in the list" or "Send the selected movie to the detail screen and return the position". It is not a project: it is a localised change, in 2–5 files, that must compile and run at the end.

**The anatomy of a requirement.** "Add `writer` (String) to the movie and display it in the list" touches five files: `Movie.java`, `activity_item.xml`, `ItemActivity.java`, `MainActivity.java` (the constructor) and — if the list is on a `RecyclerView` — `movie_item.xml` plus the adapter. That is seven mandatory edits. If you know the order, it takes 8 minutes. If you improvise it, it takes 25 and you probably miss one.

**The families of requirements that can come up:**

| Family | How it sounds | Where you learn it | Exercises |
|---|---|---|---|
| New attribute | "add `writer` and display it" | [33.1](cap-33.html#reteta-33-1)–[33.6](cap-33.html#reteta-33-6) | 17.1–17.10 |
| New widget | "add a button / switch / spinner" | [33.11](cap-33.html#reteta-33-11)–[33.16](cap-33.html#reteta-33-16) | 20.1–20.10 |
| Binding | "the value from the slider should appear in the label" | [34.1](cap-34.html#reteta-34-1)–[34.6](cap-34.html#reteta-34-6) | 18.1–18.3, 19.1–19.4 |
| Adapter | "the row should show two lines" | [34.7](cap-34.html#reteta-34-7)–[34.9](cap-34.html#reteta-34-9) | 18.4, 18.8 |
| Migration | "move the list to `RecyclerView`" | [23](cap-23.html), [34.10](cap-34.html#reteta-34-10) | 23.1–23.10, 18.5 |
| Intent | "send / return" | [35.1](cap-35.html#reteta-35-1)–[35.8](cap-35.html#reteta-35-8) | 36.1–36.10 |
| Persistence | "the data should not be lost" | [35.9](cap-35.html#reteta-35-9)–[35.13](cap-35.html#reteta-35-13) | 24.5–24.10 |

**What "solved" means.** Four conditions, in this order:

1. **It compiles.** A compilation error cancels everything else — in the test there is no "almost".
2. **It runs.** The app starts and does not crash on the first click.
3. **It is visible.** The required behaviour is on screen: the new row appears, the label changes, the screen comes back with data.
4. **You can explain.** Why you put the line there and not somewhere else. Without an explanation, the requirement is half done.

**What is not required.** The app has no database, network, files or automated tests. The requirements stay inside the code you have: model, layouts, activities, adapters, `Intent`.

**The two clocks.** Out of 30 minutes, 5 go on reading and planning, 22 on the two requirements, 3 on compiling and running. The minute-by-minute split is in section 32.10. Here, remember one single thing: **no requirement is allowed to take more than 12 minutes**. If at minute 12 it does not compile, leave it and move to the second — otherwise you lose both.

---

## Step 32.1 — Session 1 — The map

**Goal:** by the end of the session you know, without opening anything, which file must be touched for each type of requirement.

**Time:** 2 h — 60 min reading, 30 min writing `Movie.java` on paper, 30 min comparison and correction.

**You read:**
- [21](cap-21.html) in full, 30 minutes. You do not learn it, you skim it: 21.1 (the file map), 21.2 (how you add an attribute), 21.5 (the listener table), 21.6 (adapters), 21.7 (intents). The rest you leave for the sessions that need it.
- [22](cap-22.html) — only sections 22.1 (`Movie.java`) and 22.3 (`ItemActivity.java`). They are the two files you touch in almost any requirement.

**You practise:**
- You close everything: editor, chapters, cheatsheet, phone. You take an A4 sheet and write `Movie.java` from memory, in 30 minutes: `package`, `implements Serializable`, the 10 fields with their types, the constructor with 10 parameters, `toString()`.
- Then you open `cod-final/java/ro/ase/ie/g1097/model/Movie.java` and compare **line by line**. You do not count the mistakes — you note which of them would have cost you in the test: a wrong type (`int` instead of `float`), a forgotten field, `getWatched()` instead of `isWatched()`.

**You are ready when:** you can name the app's 6 files and what each one does from memory, in less than 2 minutes, without looking at the table.

**The 6 files and their boundaries:**

| File | Role | What it contains | What it is not allowed to contain |
|---|---|---|---|
| `model/Movie.java` | the data | 10 fields, constructor, getters/setters, `toString()` | `android.*` imports, `findViewById` |
| `activities/MainActivity.java` | the list | `List<Movie>`, `ArrayAdapter`, `launcher`, `addSampleMovies()` | form logic |
| `activities/ItemActivity.java` | the form | widget fields, `initControls`, `initListeners`, `fillForm`, `saveMovie` | direct access to the list in `MainActivity` |
| `res/layout/activity_main.xml` | the list screen | `FrameLayout` + `ListView` + FAB | logic |
| `res/layout/activity_item.xml` | the form | `ScrollView` + 4 cards + button | logic |
| `res/layout/movie_item.xml` | the list row | the card with `movieTitle`, `movieSubtitle` etc. | — (not used at `d719ffc`) |

There are four more context files — `AndroidManifest.xml`, `strings.xml`, `themes.xml`, `build.gradle.kts` — but you touch them only at setup, not in the test requirements.

> **The session's trap:** `movie_item.xml` exists in the project, but `ArrayAdapter` does not use it. If you ask yourself "where is the row displayed", the answer at `d719ffc` is `toString()`, not the XML. This confusion costs marks on any requirement that says "display it in the list": it depends on which adapter you are on.

---

## Step 32.2 — Session 2 — The model

**Goal:** you add any simple attribute to the model — field, getter, setter, constructor parameter, line in `toString()` — without looking at any example.

**Time:** 1.5 h — 40 min recipes, 50 min exercises.

**You read:**
- [33.1](cap-33.html#reteta-33-1) in full — the `String` attribute, the reference recipe. All the others are variations on it.
- [33.2](cap-33.html#reteta-33-2)–[33.6](cap-33.html#reteta-33-6) — only the differences: the type, the widget, the read method, what happens when the value can be `null`.

**You practise:**
- [17.1](cap-17.html#ex-17-1) — `writer` (String), the reference attribute.
- [17.3](cap-17.html#ex-17-3) — `popular` (boolean), the flag with a default value.
- [17.5](cap-17.html#ex-17-5) — `actors` (`ArrayList<String>`), the list in a single field.

**You are ready when:** you add a `String` attribute from scratch, in the form and in the list, in less than 8 minutes, without looking at any chapter.

**The 7 points — the order you repeat until you know it by heart:**

| # | Where | What you put |
|---|---|---|
| 1 | `Movie.java` | the field + getter + setter |
| 2 | `Movie.java` | the constructor parameter **and** the 3 `new Movie(...)` calls in `addSampleMovies()` |
| 3 | `Movie.java` | the line in `toString()` |
| 4 | `activity_item.xml` | the widget, with an `android:id` |
| 5 | `ItemActivity.java` | the field + `findViewById` in `initControls()` |
| 6 | `ItemActivity.java` | `fillForm()` + `saveMovie()` |
| 7 | `movie_item.xml` + adapter | only if you display in a `RecyclerView` row |

**The type dictates the widget and the read method:**

| Type | Widget | How you read it | The recipe |
|---|---|---|---|
| `String` | `TextInputEditText` | `getText().toString()` | [33.1](cap-33.html#reteta-33-1) |
| `int` | `SeekBar` | `getProgress()` | [33.2](cap-33.html#reteta-33-2) |
| `Integer` | `EditText` | `Integer.parseInt(...)`, only after `isEmpty()` | [33.3](cap-33.html#reteta-33-3) |
| `float` / `double` | `RatingBar` / `EditText` | `getRating()` / `Double.parseDouble(...)` | [33.4](cap-33.html#reteta-33-4) |
| `boolean` | `MaterialSwitch` / `CheckBox` | `isChecked()` | [33.5](cap-33.html#reteta-33-5) |
| `ArrayList<String>` | `EditText` | `Arrays.asList(text.split(","))` | [33.6](cap-33.html#reteta-33-6) |

> **The session's trap:** the constructor has 10 parameters. When you add the 11th, the three calls in `addSampleMovies()` become invalid at the same time. The compiler gives you three errors on the same signature line — it is not one error, it is three. You fix the signature, then all three calls, in a single pass through the file.

---

## Step 32.3 — Session 3 — The interface

**Goal:** you put any widget into an existing layout, give it an ID, bind it from code and attach a listener to it, in the correct order.

**Time:** 1.5 h — 35 min recipes, 45 min exercises, 10 min rereading.

**You read:**
- [33.11](cap-33.html#reteta-33-11)–[33.16](cap-33.html#reteta-33-16): widget in the form, widget in the row, button, control above the list, swapping one widget for another, new screen.
- [21](cap-21.html), section 21.3, only if you have forgotten the prefix convention (`et`, `tv`, `sp`, `sb`, `rb`, `rg`, `cb`, `sw`, `btn`, `fab`).

**You practise:**
- [20.1](cap-20.html#ex-20-1) — the "Clear form" button under "Save Movie".
- [20.3](cap-20.html#ex-20-3) — the "Delete" button in `ItemActivity`, with its own result code.

**You are ready when:** you add a button with a listener in 5 minutes, timed, from the XML tag to `setOnClickListener`.

**The button recipe, in 4 steps — you know it by heart or you reread it:**

```xml
<!-- 1. activity_item.xml, after btnMovieAction -->
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnClear"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:text="Clear form" />
```

```java
// 2. the class field
private Button btnClear;

// 3. initControls()
btnClear = findViewById(R.id.btnClear);

// 4. initListeners()
btnClear.setOnClickListener(v -> { /* what the button does */ });
```

**Where each control goes:**

| The requirement says | Where you go in | What you touch |
|---|---|---|
| "in the form" | `activity_item.xml` | an existing card, at its end |
| "above the list" | `activity_main.xml` | between `FrameLayout` and `ListView`, or in `FrameLayout` with `layout_gravity="top"` |
| "in the list row" | `movie_item.xml` | the row's card + the adapter |
| "a new screen" | new file `activity_*.xml` + class + manifest | three places, not one |

> **The session's trap:** `findViewById` returns `null` if it is called before `setContentView`, but also if the ID exists in another layout. The first variant gives a `NullPointerException` on the first click; the second one too, but only on the wrong screen. Both are fixed the same way: you check that the ID is in the layout you set.

---

## Step 32.4 — Session 4 — The bindings

**Goal:** you bind any widget to any label — live, at initialisation — and you read the widget into the model on save.

**Time:** 2 h — 50 min recipes, 60 min exercises, 10 min rereading.

**You read:**
- [34.1](cap-34.html#reteta-34-1)–[34.6](cap-34.html#reteta-34-6): value into the label live, value at initialisation, reading into the model, conditional visibility, validation, synchronisation between two widgets.

**You practise:**
- [18.1](cap-18.html#ex-18-1) — `tvDurationValue` bound to a `SeekBar`.
- [18.2](cap-18.html#ex-18-2) — `etBudget` becomes a `SeekBar` (0–500 million, step 1 million).
- [19.1](cap-19.html#ex-19-1) — `tvWatchedValue` follows the switch.

**You are ready when:** you bind a `SeekBar` to a `TextView` without looking at anything — the three methods, in order, in 4 minutes.

**How many methods the listener has — that decides the style:**

| Widget | Methods to implement | Style |
|---|---|---|
| `Button` | 1 (`onClick`) | lambda |
| `Switch`, `CheckBox`, `RadioButton` | 1 (`onCheckedChanged`) | lambda |
| `RatingBar` | 1 (`onRatingChanged`) | lambda |
| `RadioGroup` | 1 (`onCheckedChanged(group, checkedId)`) | lambda |
| `SeekBar` | **3** | anonymous class |
| `EditText` | **3** (`before` / `on` / `after`) | anonymous class |

**The rule:** one abstract method = functional interface = lambda allowed. Three methods = anonymous class, no discussion.

```java
// SeekBar: three methods, two empty
sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }
    @Override public void onStartTrackingTouch(SeekBar seekBar) { }
    @Override public void onStopTrackingTouch(SeekBar seekBar) { }
});
```

> **The session's trap:** the listener does not fire when you set the value from code. `sbDuration.setProgress(148)` does not call `onProgressChanged`, so the label stays empty until the user touches the slider. The solution is recipe [34.2](cap-34.html#reteta-34-2): you call the same logic in `onCreate` too, after `initControls()`.

---

## Step 32.5 — Session 5 — The adapters

**Goal:** you choose the right adapter for the requirement and write it from scratch, with `ViewHolder`, without copying from the chapter.

**Time:** 2 h — 50 min recipes, 60 min exercises, 10 min rereading.

**You read:**
- [34.7](cap-34.html#reteta-34-7) — `ArrayAdapter` with `toString()`.
- [34.8](cap-34.html#reteta-34-8) — `BaseAdapter` with `ViewHolder` for `ListView`.
- [34.9](cap-34.html#reteta-34-9) — `RecyclerView.Adapter` from scratch.

**You practise:**
- [18.4](cap-18.html#ex-18-4) — the second line in the `ListView` row, with a custom `BaseAdapter`.
- [18.8](cap-18.html#ex-18-8) — the row shows `Inception (2010)`: `toString()` or a custom adapter?

**You are ready when:** you write the three methods of a `RecyclerView.Adapter` from memory, in 6 minutes, with `ViewHolder` included and without a compiler.

**The decision tree:**

```
Does the row have a SINGLE text?
├── yes → ArrayAdapter + toString()            (34.7)
└── no  → custom adapter
          ├── on ListView      → BaseAdapter + getView() + ViewHolder + setTag   (34.8)
          └── on RecyclerView  → onCreateViewHolder / onBindViewHolder / getItemCount  (34.9)
```

**The correspondence between the two custom adapters:**

| `BaseAdapter` | `RecyclerView.Adapter` | When it runs |
|---|---|---|
| `getCount()` | `getItemCount()` | when needed |
| `getView()`, the `if (convertView == null)` part | `onCreateViewHolder()` | once per created row |
| `getView()`, the `setText` part | `onBindViewHolder()` | on every display |
| `ViewHolder` + manual `setTag` / `getTag` | automatic `RecyclerView.ViewHolder` | — |

**The three methods, the skeleton you write from memory:**

```java
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) { this.movies = movies; }

    @NonNull @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position));
    }

    @Override public int getItemCount() { return movies.size(); }
}
```

> **The session's trap:** `notifyDataSetChanged()` is called **after** you have modified the list, never before. The other way round, the adapter counts the old size and either does not display the new row or throws `IndexOutOfBoundsException` on scroll. The order is: `movies.add(...)`, then `notifyDataSetChanged()`.
## Step 32.6 — Session 6 — RecyclerView

**Goal:** you migrate the list from `ListView` to `RecyclerView` in 25 minutes, without reading anything during the migration.

**Time:** 2.5 h — 60 min chapter 23, 30 min recipe 34.10, 60 min the timed migration plus redoing it.

**You read:**
- [23](cap-23.html) in full. The 10 exercises **are** the 10 steps of the migration, in the order in which each step compiles.
- [34.10](cap-34.html#reteta-34-10) after the chapter, as a condensed recap of the same migration.

**You practise:**
- [18.5](cap-18.html#ex-18-5) — `ListView` → `RecyclerView`, the complete exam answer.

**You are ready when:** you do the complete migration, from `ListView` to `RecyclerView`, in 25 minutes, with the app running at the end.

**The 10 steps, with each one's file:**

| # | Step | File | What changes |
|---|---|---|---|
| 1 | the dependency | `build.gradle.kts` | `androidx.recyclerview:recyclerview` |
| 2 | the layout | `activity_main.xml` | `ListView` → `RecyclerView`, with a new ID |
| 3 | the adapter | `MovieAdapter.java` (new) | the three mandatory methods |
| 4 | `ViewHolder` | `MovieAdapter.java` | the fields from `movie_item.xml` |
| 5 | `onCreateViewHolder` | `MovieAdapter.java` | `inflate` + `new MovieViewHolder(view)` |
| 6 | `onBindViewHolder` | `MovieAdapter.java` | title + subtitle (genre · year) |
| 7 | rating | `MovieAdapter.java` | `movieRating` + `movieRatingValue` |
| 8 | chips | `MovieAdapter.java` | `movieFacts` + `setVisibility` |
| 9 | row click | `MovieAdapter.java` | `getBindingAdapterPosition()` + callback |
| 10 | `MainActivity` | `MainActivity.java` | `LayoutManager`, `setAdapter`, `notifyItem*` |

**The plan for the 25 minutes:**

| Minute | What you do |
|---|---|
| 0–5 | `activity_main.xml`: you replace `ListView` with `RecyclerView` |
| 5–15 | `MovieAdapter`: the class, `ViewHolder`, `onCreateViewHolder`, `getItemCount` |
| 15–20 | `onBindViewHolder`: you bind the real fields from `movie_item.xml` |
| 20–25 | `MainActivity`: `setLayoutManager`, `setAdapter`, `notifyItemInserted` / `notifyItemChanged` |

> **The session's trap:** an empty `RecyclerView`, with no error in Logcat, almost always has the same cause — you forgot `setLayoutManager(...)`. Without it, the `RecyclerView` does not know how to arrange the rows and draws nothing. The second cause, just as silent: `getItemCount()` returns `0` because you bound the adapter to a different list than the one you add to.

---

## Step 32.7 — Session 7 — Intent

**Goal:** you send and receive data between the two screens, in both directions, with a result code, without guessing the name of the constant or of the method.

**Time:** 2 h — 50 min recipes, 60 min exercises, 10 min rereading.

**You read:**
- [35.1](cap-35.html#reteta-35-1)–[35.8](cap-35.html#reteta-35-8): starting an activity, simple extras, a whole object, receiving the result, returning a modified object, a custom result code, an implicit `Intent`, Back vs. `finish()`.

**You practise — bank 7:**
- [36.1](cap-36.html#ex-36-1) — a `String` sent and displayed in the screen title.
- [36.3](cap-36.html#ex-36-3) — a "saved" `boolean` returned to `MainActivity`.
- [36.5](cap-36.html#ex-36-5) — deleting a movie, with the position sent back.
- [36.7](cap-36.html#ex-36-7) — a new `Movie`, without a position (insert).

**You are ready when:** you explain, in two sentences each, why the object received in `ItemActivity` is a copy and why `setResult` must be called before `finish()`.

**The two directions, in a single picture:**

```
MainActivity                                  ItemActivity
    |  explicit Intent                          |
    |  putExtra(MOVIE_EXTRA, movie)  -------->  |  getIntent()
    |  putExtra(POSITION_EXTRA, 0)              |  IntentCompat.getSerializableExtra(...)
    |  launcher.launch(intent)                  |  fillForm(existing)
    |                                           |
    |  <------- setResult(RESULT_OK, intent)    |
    |           finish()                        |
    v
callback: getResultCode()  →  WHAT happened
          getData()        →  WITH WHAT
```

**The table of methods, by direction:**

| Direction | Method | Where | Who reads it |
|---|---|---|---|
| outbound | `putExtra(CHEIE, "text")` | `MainActivity`, at `launch` | `getStringExtra(CHEIE)` |
| outbound | `putExtra(CHEIE, 3)` | `MainActivity`, at `launch` | `getIntExtra(CHEIE, -1)` |
| outbound | `putExtra(CHEIE, movie)` | `MainActivity`, row click | `IntentCompat.getSerializableExtra(...)` |
| back | `setResult(RESULT_OK, intent)` | `ItemActivity.saveMovie()` | `getResultCode()` + `getData()` |
| launch | `launcher.launch(intent)` | `MainActivity` | — |
| registration | `registerForActivityResult(...)` | `MainActivity.onCreate()` | — |

**The four traps, in the order in which they hit you:**

1. **The object received is a copy.** The `Intent` serialises the object on the way out and deserialises it on the way back. You modify the copy, not the original — that is why editing is not done directly on the list in `MainActivity`, but through `setResult`.
2. **`setResult` before `finish()`.** The other way round, `finish()` closes the activity and `setResult` no longer reaches anywhere; the parent receives `RESULT_CANCELED`.
3. **The key written twice.** `"movie"` in one place and `"Movie"` in another → `null`, with no error at all. That is why `MOVIE_EXTRA` and `POSITION_EXTRA` are constants in `MainActivity`.
4. **The position sent on insert.** A missing `POSITION_EXTRA` means `-1` at `getIntExtra`, that is "add". If you send `0` for a new movie, `MainActivity` takes the edit branch and replaces the first movie in the list.

> **The session's trap:** `registerForActivityResult` is called in `onCreate`, not in a listener. Moved into an `onClick`, it throws `IllegalStateException` on the first click, because the registration must be done while the activity is being built.

---

## Step 32.8 — Session 8 — Persistence

**Goal:** the data survives screen rotation and closing the app, and you know exactly which mechanism covers which case.

**Time:** 2 h — 50 min recipes, 60 min exercises, 10 min rereading.

**You read:**
- [35.9](cap-35.html#reteta-35-9)–[35.13](cap-35.html#reteta-35-13): rotation, `SharedPreferences` with hand-built JSON, checking that it was saved, the `Application` class, debugging data loss.

**You practise:**
- [24.6](cap-24.html#ex-24-6) — real persistence: the list is lost on closing, `SharedPreferences` + JSON.
- [24.7](cap-24.html#ex-24-7) — the checklist after every "add an attribute": 6 checks.

**You are ready when:** you save the list to `SharedPreferences` on every change and read it at startup, and after rotation the form is intact.

**What survives what:**

| Event | `onSaveInstanceState` | `SharedPreferences` | `Application` |
|---|---|---|---|
| screen rotation | yes | yes | yes |
| Home, then coming back | yes | yes | yes |
| the system kills the process in the background | yes, through `Bundle` | yes | **no** |
| the user closes the app | **no** | yes | **no** |

**Hand-built JSON — what you must know how to write:**

```java
// saving, in MainActivity, after every add / set
JSONArray array = new JSONArray();
for (Movie movie : movies) {
    JSONObject obj = new JSONObject();
    try {
        obj.put("title", movie.getTitle());
        obj.put("genre", movie.getGenre());
        obj.put("duration", movie.getDuration());
        obj.put("rating", movie.getRating());
        array.put(obj);
    } catch (JSONException e) {
        e.printStackTrace();
    }
}
getSharedPreferences("movies", MODE_PRIVATE).edit()
        .putString("list", array.toString())
        .apply();
```

On reading you take the reverse route: `getString("list", "[]")` → `new JSONArray(json)` → for each element `new Movie()` + setters + `movies.add(...)`.

**The 6 checks from 24.7, in short:** the field exists in the model · it appears in the form · it is filled on edit · it is saved · it is visible in the list · it is visible after rotation too.

> **The session's trap:** `onSaveInstanceState` saves the **state of the widgets**, not the list of movies. If you want the added movies not to disappear on closing, you need `SharedPreferences`. They are two different problems and they are solved in two different places.

---

## Step 32.9 — Session 9 — The simulation

**Goal:** to work for 30 minutes under test conditions and to know exactly where you lose time, not where you think you lose it.

**Time:** 1.5 h — 30 min simulation, 15 min correction, 45 min redoing it.

**You read:**
- Nothing. Only the statements of the two exercises, once, at the start. If you open a chapter, the simulation is worth nothing anymore.

**You practise:**
- [17.10](cap-17.html#ex-17-10) — `writer` + `popular`: the two requirements, in 30 minutes.
- [20.10](cap-20.html#ex-20-10) — the exam combination: the "Duplicate movie" button.

**You are ready when:** you finish both requirements in 30 minutes, with the app running, without opening any chapter and without looking at the solution.

**The protocol, exactly like this:**

1. You start the timer at 30 minutes. You do not stop it, you do not rewind it.
2. You read both statements in full, once, without writing anything.
3. You work. The solutions are folded away in files — you do not open them under any circumstances.
4. At minute 30 you stop, wherever you are. You note where you were.
5. Only now do you open the solutions and correct.

**The marking grid — you apply it yourself:**

| Criterion | Points |
|---|---|
| it compiles | 1 |
| it runs | 1 |
| requirement 1 is visible on screen | 2 |
| requirement 2 is visible on screen | 2 |
| you can explain every line added | 2 |
| you finished in 30 minutes | 2 |

Below 7 out of 10: you are not ready. You note **what** slowed you down — not "I was slow", but "I lost 6 minutes looking for `fillForm`" or "I forgot the third call in `addSampleMovies()`". Every concrete delay has a recipe in the table in 32.12.

**Then you reread what you got wrong:** you open the exact recipe of the thing that blocked you, you read it once, then you redo the exercise from scratch, timed. The second time you must come in under 20 minutes.

> **The session's trap:** the temptation to "check the solution for a second". One second costs the whole simulation — because from then on you no longer know whether you solved it yourself or recognised the answer.

---

## Step 32.10 — Session 10 — Test day

**Goal:** you have a 30-minute plan and you know exactly what you reread in the hour before, so that you do not go into the test with your head in the material.

**Time:** 1 h — 40 min rereading, 20 min repeating out loud.

**You read:**
- The 7 points and the 10 steps below. Nothing else. You do not open chapters, you do not open solved exercises.

**You practise:**
- You say out loud, without looking: the 7 points, the 10 steps of the migration, the error table in 32.12.

**You are ready when:** you say the 7 points in order in 90 seconds and the 10 steps in 3 minutes, without stopping.

**What you reread — the 7 points of adding an attribute:**

| # | Where | What you put |
|---|---|---|
| 1 | `Movie.java` | field + getter + setter |
| 2 | `Movie.java` | constructor parameter + the 3 calls in `addSampleMovies()` |
| 3 | `Movie.java` | the line in `toString()` |
| 4 | `activity_item.xml` | the widget, with an ID |
| 5 | `ItemActivity.java` | field + `findViewById` in `initControls()` |
| 6 | `ItemActivity.java` | `fillForm()` + `saveMovie()` |
| 7 | `movie_item.xml` + adapter | only on `RecyclerView` |

**What you reread — the 10 steps of the migration:** the dependency · the layout · the adapter · `ViewHolder` · `onCreateViewHolder` · `onBindViewHolder` · rating · chips · click · `MainActivity`.

**What you do NOT reread:**

- Code word for word. `toString()` is not memorised — it is generated with Alt+Insert in 5 seconds.
- Chapters 01–16. Setup, layouts, the repo history — they do not come up in the test.
- The lifecycle theory. You retain only four things: `onCreate` builds, `onSaveInstanceState` saves, `setResult` reports, `finish()` closes.
- The solved exercises. Rereading the solutions before the test gives you the feeling of safety without also giving you the ability.

**The first 5 minutes of the test:**

| Minute | What you do |
|---|---|
| 0–1 | you read both requirements in full, without writing anything |
| 1–2 | you note in the corner the files touched by each requirement |
| 2–3 | you decide the order: first is the requirement that touches `Movie.java`, because it changes the constructor |
| 3–5 | you open the files in the established order and do not close them again |

**How you split the 30 minutes:**

| Minute | What you do |
|---|---|
| 0–5 | reading + plan |
| 5–17 | requirement 1, complete, up to compilation |
| 17–27 | requirement 2 |
| 27–30 | you compile, run, fix what is visible on screen |

> **The minute-27 rule:** if it does not compile, you comment out the last change — not the whole requirement. A requirement that compiles halfway scores more points than one that does not compile at all. And you never leave the test with a file in which you have left a syntax error: that cancels the part that was working too.

---

## 32.11 If you have less time

Three variants, from "I have a weekend" to "I have two hours before the test". Each one also says what you risk.

**3 days (~9 h):** you do sessions **2, 4, 6, 7, 9** — you skip 1, 3, 5, 8, 10.

| What you cut | What you risk |
|---|---|
| the map (1), the interface (3), the custom adapters (5), persistence (8), test day (10) | if a custom `BaseAdapter` or `SharedPreferences` comes up, you improvise; without session 1 you lose time in the test looking for the file |

It covers: new attribute, binding, `RecyclerView` migration, `Intent`, simulation. It is exactly the core of the test.

**1 day (~5 h):** recipes [33.1](cap-33.html#reteta-33-1)–[33.5](cap-33.html#reteta-33-5), [34.1](cap-34.html#reteta-34-1), [34.10](cap-34.html#reteta-34-10), [35.1](cap-35.html#reteta-35-1)–[35.5](cap-35.html#reteta-35-5), then the simulation [17.10](cap-17.html#ex-17-10).

| What you cut | What you risk |
|---|---|
| the custom adapters (34.8, 34.9), persistence (35.9–35.13), the new widgets (33.11–33.16) | a requirement with `SharedPreferences` or with a second `TextView` in the row stays unsolved |

**2 hours:** only recipes [33.1](cap-33.html#reteta-33-1), [34.10](cap-34.html#reteta-34-10), [35.1](cap-35.html#reteta-35-1) and the simulation [17.10](cap-17.html#ex-17-10).

| What you cut | What you risk |
|---|---|
| everything else | you cover only the simple attribute, the migration and a basic `Intent` — but you cover well exactly three things that come up often |

> **The choice that matters:** if you have time for only one recipe, it is [33.1](cap-33.html#reteta-33-1). It touches five files and appears in almost any compound requirement.

---

## 32.12 If you got something wrong

The diagnostic table. You look at the symptom, not at the code — you read the code afterwards.

| Symptom | Probable cause | The recipe |
|---|---|---|
| I added the attribute, but it does not appear in the list | you did not touch `movie_item.xml` + the adapter | [33.12](cap-33.html#reteta-33-12) |
| On edit the value is lost | you forgot `fillForm` (or the field's line in it) | [34.2](cap-34.html#reteta-34-2)–[34.3](cap-34.html#reteta-34-3) |
| The list does not update after saving | you forgot `notifyDataSetChanged()` | [34.14](cap-34.html#reteta-34-14) |
| `RecyclerView` appears empty, with no error | you forgot `setLayoutManager` | [34.10](cap-34.html#reteta-34-10) |
| The app crashes on Save | `Double.parseDouble` on an empty field | [33.4](cap-33.html#reteta-33-4) |
| `RESULT_CANCELED` comes back | you forgot `setResult` before `finish()` | [35.5](cap-35.html#reteta-35-5) |
| The data disappears on rotation | you forgot `onSaveInstanceState` | [35.9](cap-35.html#reteta-35-9) |
| The edited movie appears twice | `movies.add(...)` instead of `movies.set(position, ...)` | [35.5](cap-35.html#reteta-35-5) |
| The new field is `null` in all the demo rows | you forgot the constructor parameter or one of the 3 calls | [33.1](cap-33.html#reteta-33-1) |
| The label updates only when you move the widget | the listener does not fire on the value set from code | [34.2](cap-34.html#reteta-34-2) |
| After rotation, the `Spinner` goes back to the first option | `onSaveInstanceState` does not save the selection | [35.9](cap-35.html#reteta-35-9) |
| The new button does not react to a click | `findViewById` on another ID or a listener set before `setContentView` | [33.13](cap-33.html#reteta-33-13) |

**How you use it:** you do not look for the "close" symptom. You look for exactly what you see on screen or in Logcat. If the symptom is not in the table, the general rule is: first the compilation, then the link between XML and code (`findViewById`), then the link between code and model (`saveMovie` / `fillForm`), then the notification of the list.

---

## 32.13 The ten basic operations

The test does not ask you to "add an attribute" in the abstract. It asks for a **concrete operation**: "add the director", "put a delete button", "make the duration show under the slider". All of them reduce to ten operations. If you know these, you know everything that can come up.

| # | The operation | How it sounds in the test | Recipe | Session | Practise |
|---|---|---|---|---|---|
| 1 | **Add a field to the movie** | "add the director / the year / the genre / a list of actors" | [33.1](cap-33.html#reteta-33-1)–[33.6](cap-33.html#reteta-33-6) | 2 | [17.1](cap-17.html#ex-17-1), [17.3](cap-17.html#ex-17-3), [17.5](cap-17.html#ex-17-5) |
| 2 | **Add a composed field** | "add a list of actors, each with a name and a role" | [33.7](cap-33.html#reteta-33-7) | 2 | [17.9](cap-17.html#ex-17-9) |
| 3 | **Add a button** | "put a Clear form button under Save" | [33.13](cap-33.html#reteta-33-13) | 3 | [20.1](cap-20.html#ex-20-1) |
| 4 | **Attach an event** | "when the button is pressed, X should happen" | [34.15](cap-34.html#reteta-34-15) | 3–4 | [20.1](cap-20.html#ex-20-1), [18.1](cap-18.html#ex-18-1) |
| 5 | **Delete a movie** | "a Delete button in the detail screen" | [35.6](cap-35.html#reteta-35-6) | 7 | [36.5](cap-36.html#ex-36-5) |
| 6 | **Bind a value to a label** | "the duration should show under the slider, live" | [34.1](cap-34.html#reteta-34-1) | 4 | [18.1](cap-18.html#ex-18-1), [19.1](cap-19.html#ex-19-1) |
| 7 | **Swap a widget** | "the budget from EditText to SeekBar" | [33.15](cap-33.html#reteta-33-15) | 3 | [18.2](cap-18.html#ex-18-2) |
| 8 | **Migrate to RecyclerView** | "the list from ListView to RecyclerView" | [34.10](cap-34.html#reteta-34-10) | 6 | [18.5](cap-18.html#ex-18-5) |
| 9 | **Send data through an Intent** | "send the movie to the detail screen" | [35.2](cap-35.html#reteta-35-2), [35.3](cap-35.html#reteta-35-3) | 7 | [36.1](cap-36.html#ex-36-1), [36.7](cap-36.html#ex-36-7) |
| 10 | **Persist the list** | "the data should survive closing the app" | [35.10](cap-35.html#reteta-35-10) | 8 | [24.6](cap-24.html#ex-24-6) |

### How to practise them: in pairs, the way they come in the test

The test gives you **two** requirements. That is why you do not practise the operations separately, but in pairs — exactly the combinations that show up:

1. **Field + display** — operations 1 and 6. "Add the director and show it in the list."
2. **Button + event** — 3 and 4. "Put a button that clears the form."
3. **Button + delete** — 3 and 5. "Put a button that deletes the movie."
4. **Field + Intent** — 1 and 9. "Add a field and send it to the detail screen."
5. **Migration + display** — 8 and 6. "Move to RecyclerView and show the duration in the row."

Each pair is done in **30 minutes, on a timer, with the solution closed**. Five pairs, five simulations — and you have covered everything that can come up.

### What you do in the first 5 minutes of the test

1. Read both requirements once, in full, before opening any file.
2. Write down on paper the **files** each requirement touches. If you come up with more than three per requirement, you have not understood it — read it again.
3. Start with the requirement that touches the **model** (`Movie.java`), because the second one may use it.
4. If one of the requirements is "migrate to RecyclerView", start with **the other one**: the migration eats 20 of the 30 minutes.
5. Leave 3 minutes at the end for: running the app, adding a movie, editing a movie.

---

## Chapter 32 summary

**What you have covered:** ten sessions, 18 hours, from "I know what files the app has" to "I take the test in 30 minutes".

| # | Session | Time | The exit test |
|---|---|---|---|
| 1 | The map | 2 h | you name the 6 files and their role in 2 minutes |
| 2 | The model | 1.5 h | a complete `String` attribute in under 8 minutes |
| 3 | The interface | 1.5 h | a button with a listener in 5 minutes |
| 4 | The bindings | 2 h | `SeekBar` → `TextView` without looking |
| 5 | The adapters | 2 h | the three methods of `RecyclerView.Adapter` from memory |
| 6 | RecyclerView | 2.5 h | the complete migration in 25 minutes |
| 7 | Intent | 2 h | you explain the copy and the order `setResult` / `finish()` |
| 8 | Persistence | 2 h | list saved in `SharedPreferences` and read at startup |
| 9 | The simulation | 1.5 h | two requirements in 30 minutes, without material |
| 10 | Test day | 1 h | the 7 points in 90 seconds |

**Three things you take with you:**

1. **The order, not the memory.** You do not have to know the code by heart; you have to know which file you go into first. The model first, then the XML, then `findViewById`, then `fillForm` / `saveMovie`, then the notification.
2. **The exit test, not the feeling.** "I understood" is not a criterion. "I can write it from memory in 8 minutes" is.
3. **The diagnostic table.** When something does not work, the symptom tells you the recipe. You do not read the whole chapter to find one line.

**What comes next:** if you have passed all ten exit tests, there is nothing left to read — there is something to do. Redo [17.10](cap-17.html#ex-17-10) and [20.10](cap-20.html#ex-20-10) until you come in under 25 minutes, then stop. The rest before the test does more than the twenty-first exercise.
