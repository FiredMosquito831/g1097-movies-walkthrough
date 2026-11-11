# Chapter 36 — Requirement bank 7: intents and navigation

**Objective:** to master both directions of an `Intent` — outbound (what you send when you open a screen) and inbound (what you report when you close it) — so that any "send", "return", "open" requirement gets solved in 10–15 minutes, without guessing the name of the constant or of the method.

**What the requirement looks like at the exam:** "Send the selected movie to the detail screen and return the position." Two sentences, three things to do: a `putExtra` on the way out, a `setResult` on the way back and a branch in the callback. The rest of the chapter is variations on the same theme.

**The two directions, in a single picture:**

```
MainActivity                              ItemActivity
    |                                          |
    |  Explicit intent                         |
    |  putExtra(MOVIE_EXTRA, movie)   -------> |  getIntent()
    |  putExtra(POSITION_EXTRA, 0)             |  getSerializableExtra(...)
    |  launcher.launch(intent)                 |  getIntExtra(..., -1)
    |                                          |
    |  <------- setResult(RESULT_OK, intent)   |
    |           finish()                       |
    v
callback(ActivityResult)
    getResultCode()  -> WHAT happened
    getData()        -> WITH WHAT
```

**Three things almost everyone gets wrong:**

| The mistake | The effect | Where it shows up |
|---|---|---|
| You forget `setResult` | the parent receives `RESULT_CANCELED` and ignores everything | 36.3, 36.5 |
| You send `MOVIE_EXTRA` without `POSITION_EXTRA` on insert | `ItemActivity` enters edit mode with an empty object → `NullPointerException` in `fillForm` | 36.7 |
| You do `movies.add(movie)` on edit | the movie shows up twice, the original stays unchanged | 36.8 |

**The result codes — the table you memorize:**

| Constant | Value | Who sets it | What it means |
|---|---|---|---|
| `RESULT_OK` | `-1` | `ItemActivity.saveMovie()` | "I saved, look at the `Intent`" |
| `RESULT_CANCELED` | `0` | the system, when you press Back | "nothing happened" |
| `RESULT_FIRST_USER` | `1` | you | the first custom code available |
| `RESULT_DRAFT` | `2` | 36.4 | "I saved a draft" |
| `RESULT_DELETE` | `3` | 36.5 | "delete the row at this position" |

> The rule: any custom code must be **≥ 1**. `0` is already `RESULT_CANCELED`, and `-1` is `RESULT_OK`. A code of `0` would be read as "the user pressed Back".

**What is already in the code at `d719ffc`** — we invent nothing, we start from here:

- `MainActivity` has `protected static final String POSITION_EXTRA = "position";` and `MOVIE_EXTRA = "movie";`
- `MainActivity` has `private ActivityResultLauncher<Intent> launcher;`, registered with `registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), callback)` at the **end** of `onCreate`
- `ItemActivity` has `private int position = -1;` and reads the movie with `IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class)`
- `ItemActivity.saveMovie()` already does `setResult(RESULT_OK, intent)` + `finish()`

So half of the chain exists. The exercises add the missing pieces, one at a time.

**The chapter map:**

| # | What you add | Direction | Files |
|---|---|---|---|
| 36.1 | a `String` in the title | outbound | `MainActivity`, `ItemActivity` |
| 36.2 | two parameters in a subtitle | outbound | + `activity_item.xml` |
| 36.3 | a `boolean` back | inbound | `MainActivity`, `ItemActivity` |
| 36.4 | a custom result code | inbound | + `activity_item.xml` |
| 36.5 | delete with a position | inbound | + `activity_item.xml` |
| 36.6 | confirmation before deleting | — | `ItemActivity` |
| 36.7 | insert without a position | outbound + inbound | `MainActivity`, `ItemActivity` |
| 36.8 | edit with a position, no duplicate | outbound + inbound | `MainActivity`, `ItemActivity` |
| 36.9 | `ACTION_VIEW` to the browser | implicit | + `AndroidManifest.xml` |
| 36.10 | new attribute + Intent | all | all |

---

## Exercise 36.1 — Send a String and show it in the screen title

**Requirement:** When you press the "+" FAB, `MainActivity` sends `ItemActivity` a `String` with the screen title ("New movie"). `ItemActivity` reads it and puts it in the title bar with `setTitle(...)`. When you go into edit mode, the title stays "Edit movie".

**Files touched:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**How you approach it — your steps:**
1. Open `activities/MainActivity.java`. Under `protected static final String MOVIE_EXTRA = "movie";`, add `protected static final String TITLE_EXTRA = "title";`.
2. In `initListeners()`, in the listener of `fabInsert`, after `Intent intent = new Intent(MainActivity.this, ItemActivity.class);`, add `intent.putExtra(TITLE_EXTRA, "New movie");`.
3. Open `activities/ItemActivity.java`. In `onCreate`, right after `Intent intent = getIntent();`, add `String header = intent.getStringExtra(MainActivity.TITLE_EXTRA);`.
4. At the end of `onCreate`, turn the `if (existing != null)` block into an `if / else if`: the `else if (header != null)` branch does `setTitle(header);`.
5. Check: Run, press the FAB. The title bar of the form screen reads "New movie". Tap a movie in the list: the bar reads "Edit movie".

**Hint 1 — if you get stuck at step 1:** the extra constants are `String`s that live in `MainActivity` and are read from `ItemActivity`. They are `protected static`, so accessible from the same package `ro.ase.ie.g1097.activities`. Don't duplicate them in `ItemActivity` — if you write "title" in one place and "Title" in the other, the key doesn't match and you get `null` with no error at all.

**Hint 2 — if you get stuck at step 4:** `setTitle("Edit movie")` is already called in the `existing != null` branch. If you put `setTitle(header)` after the block, you overwrite it and the edit screen will read "New movie". That's why the two variants sit in an `if / else if`, not one after the other.

<details>
<summary>Solution — explained</summary>

**What was done:** a new constant in `MainActivity`, a `putExtra` at launch, a read in `ItemActivity` and an `else if` branch that displays it.

**Code:**

Step 1 — `activities/MainActivity.java`, next to the other constants:

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
protected static final String TITLE_EXTRA = "title";     // the new line
```

Step 2 — `MainActivity.initListeners()`, the FAB's listener:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, "New movie");      // the new line
        launcher.launch(intent);
    }
});
```

Steps 3 and 4 — `activities/ItemActivity.java`, `onCreate()`:

```java
Intent intent = getIntent();
String header = intent.getStringExtra(MainActivity.TITLE_EXTRA);   // the new line
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
} else if (header != null) {                                        // the new branch
    setTitle(header);
}
```

**Why:** `getStringExtra` returns `null` when the key is missing, not an exception. That turns "did the extra come in or not" into a decision you make yourself, with an `if`. In `MainActivity`, the click on a row doesn't put `TITLE_EXTRA`, so `header` is `null` there — exactly what you want, because the edit branch has its own title.

**Remember:**
1. **`setTitle(...)` is the method of `Activity`, not of the `ActionBar`.** `AppCompatActivity` exposes it directly and it works even when the bar is generated by the theme. `getSupportActionBar().setTitle(...)` would need a `null` check, because `getSupportActionBar()` can return `null` when the theme has no `ActionBar`.
2. **The order of the branches is the contract.** Editing always wins over the received title: if you came in with `MOVIE_EXTRA`, you are in edit mode, whatever `TITLE_EXTRA` you received.
3. **The key is just some `String`.** `"title"` has nothing to do with `R.string` or with `android:label`. It's only a label in the `Bundle`; what matters is that it's identical at both ends, which is why you keep it in a single constant.
4. **`getIntent()` returns the `Intent` the activity was created with.** Don't confuse it with the result `Intent` from `saveMovie()` — that one is a new object, built by you, and has nothing to do with the one received.
5. **Don't put visible text in `putExtra` if you can put a key.** Here the text is exactly what you want to display, so it's fine; but if it had been the screen's "mode", you would have sent `"insert"` / `"edit"` and picked the text in `ItemActivity`.

**Where it applies:** any simple value that customizes a secondary screen — a title, a mode (`"insert"` / `"edit"`), an entity id, a user name. The pattern is always the same: constant in the parent, `putExtra` at launch, `getXxxExtra` with a `null` guard in the child.

</details>

---

## Exercise 36.2 — Send two parameters (title + year) and show them in a subtitle

**Requirement:** The FAB sends **two** extras: the screen title and the current year. `ItemActivity` shows them together, in a single subtitle `TextView`, under the "Movie details" header, in the form `New movie · 2026`. In edit mode the subtitle stays the original one.

**Files touched:** `activities/MainActivity.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`.

**How you approach it — your steps:**
1. In `MainActivity`, add the second constant: `protected static final String YEAR_EXTRA = "year";`.
2. In the FAB's listener, after `putExtra(TITLE_EXTRA, ...)`, add `intent.putExtra(YEAR_EXTRA, Calendar.getInstance().get(Calendar.YEAR));`. `Calendar` is already imported in `MainActivity`.
3. In `res/layout/activity_item.xml`, the second `TextView` in the header (the one with the text "Fill in the information below and save.") has no `android:id`. Add `android:id="@+id/tvSubtitle"` to it.
4. In `ItemActivity`, add the field `private TextView tvSubtitle;`, the line `tvSubtitle = findViewById(R.id.tvSubtitle);` in `initControls()`.
5. In `onCreate`, read the year with `int year = intent.getIntExtra(MainActivity.YEAR_EXTRA, -1);` and, in the `else if (header != null)` branch, build the text.
6. Check: Run, FAB — the subtitle reads "New movie · 2026". Tap a movie — the subtitle stays "Fill in the information below and save.".

**Hint 1 — if you get stuck at step 3:** the subtitle `TextView` is the **second** one in the screen header, right after "Movie details". It has `textAppearanceBodyMedium` and `textColor="?attr/colorOnSurfaceVariant"`. Don't confuse it with the labels in the cards (`tvTile`, `tvGenre` etc.), which already have ids.

**Hint 2 — if you get stuck at step 5:** `getIntExtra` requires a default value, because an `int` can't be `null`. Use `-1` as "it didn't come in" and handle the case: if the year is missing, show only the title, with no separator. Otherwise you end up with "New movie · -1" on screen.

<details>
<summary>Solution — explained</summary>

**What was done:** a second numeric extra, an id for the subtitle `TextView`, a field and a line in `initControls`, plus building the text in `onCreate`.

**Code:**

Steps 1 and 2 — `activities/MainActivity.java`:

```java
protected static final String TITLE_EXTRA = "title";
protected static final String YEAR_EXTRA = "year";       // the new line
```

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, "New movie");
        intent.putExtra(YEAR_EXTRA, Calendar.getInstance().get(Calendar.YEAR));   // the new line
        launcher.launch(intent);
    }
});
```

Step 3 — `res/layout/activity_item.xml`, the second `TextView` in the root:

```xml
<TextView
    android:id="@+id/tvSubtitle"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:layout_marginBottom="20dp"
    android:text="Fill in the information below and save."
    android:textAppearance="?attr/textAppearanceBodyMedium"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

Steps 4 and 5 — `activities/ItemActivity.java`, three places:

```java
// 4a. the field, next to the other TextView fields
private TextView tvSubtitle;

// 4b. initControls() — at the end of the method
tvSubtitle = findViewById(R.id.tvSubtitle);

// 5. onCreate() — reading and building the text
Intent intent = getIntent();
String header = intent.getStringExtra(MainActivity.TITLE_EXTRA);
int year = intent.getIntExtra(MainActivity.YEAR_EXTRA, -1);        // the new line
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
} else if (header != null) {
    setTitle(header);
    tvSubtitle.setText(year == -1 ? header : header + " · " + year);   // the new line
}
```

**Why:** two extras mean two keys and two reads, but a single `Intent`. There is no such thing as "`putExtra` with two values": each value has its own key. The `·` separator (U+00B7) is the same character already used in `movie_item.xml` for the card subtitle, so the screens look consistent.

**Remember:**
1. **An `int` can't be `null`, so `getIntExtra` needs a default value.** Pick a value that can't be valid (`-1` for a year) and treat it as "absent". The `Integer` alternative with `getSerializableExtra` works, but it's clunkier and buys you nothing.
2. **The order of the `putExtra` calls doesn't matter, and neither does the order of the reads.** The `Bundle` is a map; only the keys matter.
3. **A `TextView` without an `android:id` can't be found from code.** `findViewById(R.id.tvSubtitle)` returns `null` and `setText` throws `NullPointerException` — that's why step 3 is mandatory, not optional.
4. **The separator goes in the code, not in the XML.** If you put it in `android:text`, you lose it at the first `setText`.
5. **Conditional display beats a visible default value.** `year == -1 ? header : header + " · " + year` avoids "New movie · -1", which looks like a bug.

**Where it applies:** any screen that needs context — "Edit movie · Inception", "Details · position 3", "Add grade · student 123". The rule: one extra per piece of information, a default value that can't be confused with a real value, a guard at display time.

</details>

---

## Exercise 36.3 — Return a "saved" boolean and react in MainActivity

**Requirement:** When `ItemActivity` saves, put a `boolean` with the key `"saved"` in the result `Intent`, set to `true`. `MainActivity` shows a `Toast` with "Movie saved" only when it receives `true`. If the user presses Back, nothing appears.

**Files touched:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**How you approach it — your steps:**
1. In `MainActivity`, add `protected static final String SAVED_EXTRA = "saved";` next to the other constants.
2. In `ItemActivity.saveMovie()`, after `intent.putExtra(MainActivity.MOVIE_EXTRA, movie);`, add `intent.putExtra(MainActivity.SAVED_EXTRA, true);`.
3. In `MainActivity`, in the launcher's callback, after `movieAdapter.notifyDataSetChanged();` in the `RESULT_OK` branch, add `if (intent.getBooleanExtra(SAVED_EXTRA, false)) { Toast... }`.
4. Add the guard `if (intent == null) return;` right after `Intent intent = o.getData();`.
5. Check: Run, add a movie, Save — "Movie saved" appears. Tap a movie, press Back — nothing appears.

**Hint 1 — if you get stuck at step 2:** `saveMovie()` already builds `Intent intent = new Intent();` and puts the movie in it. The boolean goes into the **same** `Intent`, before `setResult`. If you make a new `Intent` after `setResult`, it goes nowhere.

**Hint 2 — if you get stuck at step 3:** `getBooleanExtra` also requires a default value — `false`. Don't check `== true` with `getBooleanExtra(SAVED_EXTRA)` without the second argument: the method has no such overload and it doesn't compile.

<details>
<summary>Solution — explained</summary>

**What was done:** a boolean flag in the result `Intent` and a reaction in the parent's callback, conditioned by the flag.

**Code:**

`activities/MainActivity.java`:

```java
protected static final String SAVED_EXTRA = "saved";     // the new line
```

`activities/ItemActivity.java`, `saveMovie()` — the end of the method:

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.SAVED_EXTRA, true);         // the new line
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

`activities/MainActivity.java`, the launcher's callback:

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    if (intent == null) return;                          // the new guard
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    movieAdapter.notifyDataSetChanged();
    if (intent.getBooleanExtra(SAVED_EXTRA, false)) {     // the new reaction
        Toast.makeText(MainActivity.this, "Movie saved", Toast.LENGTH_SHORT).show();
    }
}
```

**Why:** the result code says the *class* of the event ("OK"), and the extras say the *details*. A `boolean` in the `Intent` is the cheapest way to pass along a piece of information that has no value of its own — you don't have to invent a new result code for something that can be expressed as "yes / no".

**Remember:**
1. **`RESULT_OK` without an `Intent` is possible.** `setResult(RESULT_OK)` exists as a single-argument overload and leaves `o.getData()` as `null`. That's why the `if (intent == null) return;` guard isn't decorative — without it, the first `getSerializableExtra` throws `NullPointerException`.
2. **The default value of `getBooleanExtra` is your decision.** With `false`, a missing key means "nothing happened" — exactly the semantics you want. With `true`, any `RESULT_OK` result would show the toast.
3. **A flag doesn't replace the data.** If you also need the movie, you send it separately; the flag only qualifies the result. Don't pack the `boolean` into `Movie` — it has no business being in the model.
4. **The toast is shown on the UI thread, from the callback.** The launcher's callback runs on the main thread, so `Toast.makeText(...).show()` is safe. From a `Thread` or an `Executor` it would throw `RuntimeException`.
5. **The alternative to a flag is a custom result code** (exercise 36.4). Choose a flag when you already have `RESULT_OK` and only want to add nuance; choose a custom code when the event is fundamentally different.

**Where it applies:** any "tell me if it happened" — save succeeded, form validated, user authenticated, sync finished. The pattern: `putExtra` with a `boolean` in the result `Intent`, `getBooleanExtra` with a default of `false` in the parent.

</details>

---

## Exercise 36.4 — The second button that returns a different result

**Requirement:** Add a second button to `ItemActivity`, "Save as draft", under "Save Movie". Pressed, it closes the screen with the custom code `RESULT_DRAFT` (the value `2`) and **without** changing the list. `MainActivity` shows "Draft saved" when it receives that code, and the list stays unchanged.

**Files touched:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**How you approach it — your steps:**
1. In `activity_item.xml`, after `btnMovieAction`, add a `MaterialButton` with `android:id="@+id/btnDraft"`, style `@style/Widget.Material3.Button.TonalButton`, text "Save as draft".
2. In `ItemActivity`, add the constant `public static final int RESULT_DRAFT = 2;` right under the class declaration, before the fields.
3. Add the field `private Button btDraft;`, the line in `initControls()` and the listener in `initListeners()`.
4. Write the `saveDraft()` method: `setResult(RESULT_DRAFT);` then `finish();`. No `Intent`.
5. In `MainActivity`, in the callback, add the `else if (o.getResultCode() == ItemActivity.RESULT_DRAFT)` branch with a `Toast`.
6. Check: Run, FAB, fill in the title, press "Save as draft" — "Draft saved" appears, the list still has 3 rows. Then Save Movie — the list has 4.

**Hint 1 — if you get stuck at step 2:** `RESULT_OK` is `-1`, `RESULT_CANCELED` is `0`, `RESULT_FIRST_USER` is `1`. So `2` is free. If you use `0`, the system treats it as "the user pressed Back" and your branch never runs.

**Hint 2 — if you get stuck at step 5:** on this branch `o.getData()` is `null`, because `setResult(RESULT_DRAFT)` has no `Intent`. Don't call `getData().getIntExtra(...)` — check only the code and show the toast.

<details>
<summary>Solution — explained</summary>

**What was done:** a new button, a custom result constant, a method that closes the screen with no data and a new branch in the parent's callback.

**Code:**

`res/layout/activity_item.xml` — after `btnMovieAction`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnDraft"
    style="@style/Widget.Material3.Button.TonalButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Save as draft"
    app:icon="@android:drawable/ic_menu_edit" />
```

`activities/ItemActivity.java`:

```java
public static final int RESULT_DRAFT = 2;      // under the class declaration

private Button btDraft;

// initControls()
btDraft = findViewById(R.id.btnDraft);

// initListeners()
btDraft.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveDraft();
    }
});

// the new method
private void saveDraft() {
    setResult(RESULT_DRAFT);
    finish();
}
```

`activities/MainActivity.java` — the callback becomes:

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    if (intent == null) return;
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    movieAdapter.notifyDataSetChanged();
} else if (o.getResultCode() == ItemActivity.RESULT_DRAFT) {     // the new branch
    Toast.makeText(MainActivity.this, "Draft saved", Toast.LENGTH_SHORT).show();
}
```

**Why:** `setResult(int)` and `setResult(int, Intent)` are two different methods. The first closes the screen with a code and nothing more; the second adds data too. A draft has no data to send — the parent only needs to know that it happened, so it can show the message. That's why the button doesn't touch `movies`.

**Remember:**
1. **Custom codes start at `1`.** `RESULT_FIRST_USER` is defined exactly for this; `2` is just as good and easier to read when you have several. `0` and `-1` are taken by the system.
2. **A custom code doesn't need an `Intent`.** If you have no data to send, `setResult(RESULT_DRAFT)` is enough. The parent checks `getResultCode()` and doesn't touch `getData()`.
3. **The order of the branches in the callback is the order of priorities.** `RESULT_OK` first, then the custom codes; a final `else if` with no condition would also catch `RESULT_CANCELED`, which is usually not what you want.
4. **The button validates nothing.** A draft can have empty fields — that's the point. If you still want validation, you put it in `saveDraft()` before `setResult`, not in the parent.
5. **The two buttons have to look different.** `Widget.Material3.Button.TonalButton` has a tonal background, "Save Movie" is filled. At the exam, the visual difference is half the UX marks.

**Where it applies:** any "second way of closing the screen" — save as draft, cancel with a reason, send for approval, mark as seen. Each one gets a custom code and, if it needs one, an `Intent` with data.

</details>

---
## Exercise 36.5 — Delete a movie from ItemActivity and send the position back

**Requirement:** Add a "Delete movie" button to `ItemActivity`, visible only when you edit an existing movie. Pressed, it closes the screen with the custom code `RESULT_DELETE` and sends the row's position back. `MainActivity` removes the movie from the list at that position and redraws.

**Files touched:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**How you approach it — your steps:**
1. In `activity_item.xml`, after `btnDraft` (or after `btnMovieAction`, if you didn't do 36.4), add a `MaterialButton` with `android:id="@+id/btnDelete"`, style `@style/Widget.Material3.Button.OutlinedButton`, text "Delete movie" and the colour `?attr/colorError`.
2. In `ItemActivity`, add the constant `public static final int RESULT_DELETE = 3;` next to `RESULT_DRAFT`.
3. Add the field `private Button btDelete;`, the line in `initControls()` and the listener in `initListeners()`.
4. Write the `deleteMovie()` method: put `position` in the `Intent`, then `setResult(RESULT_DELETE, intent)` and `finish()`.
5. At the end of `onCreate`, after the `if / else if` block, add `btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);`.
6. In `MainActivity`, in the callback, add the `else if (o.getResultCode() == ItemActivity.RESULT_DELETE)` branch that reads the position and does `movies.remove(position)`.
7. Check: Run, tap "Toy Story", press Delete — the row disappears, the list has 2. Press the FAB: the Delete button is not visible.

**Hint 1 — if you get stuck at step 4:** `position` is the field in `ItemActivity`, set in `onCreate` only when you came in with `MOVIE_EXTRA`. In insert mode it stays `-1`, so the button is hidden and you have no position to send. Don't read the position from `getIntent()` in `deleteMovie()` — the field already has it.

**Hint 2 — if you get stuck at step 6:** `movies.remove(position)` has two overloads: `remove(int index)` and `remove(Object o)`. With an `int`, Java picks the first — good. But if the position comes in wrong (for example `-1`), `remove(-1)` throws `IndexOutOfBoundsException`. Check the range first.

<details>
<summary>Solution — explained</summary>

**What was done:** a button that is only visible in edit mode, a custom result code, an `Intent` that carries the position and a delete branch in the parent.

**Code:**

`res/layout/activity_item.xml` — after `btnDraft`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnDelete"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Delete movie"
    android:textColor="?attr/colorError"
    app:icon="@android:drawable/ic_menu_delete"
    app:iconTint="?attr/colorError"
    app:strokeColor="?attr/colorError" />
```

`activities/ItemActivity.java`:

```java
public static final int RESULT_DRAFT = 2;
public static final int RESULT_DELETE = 3;      // the new line

private Button btDelete;

// initControls()
btDelete = findViewById(R.id.btnDelete);

// initListeners()
btDelete.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        deleteMovie();
    }
});

// the new method
private void deleteMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_DELETE, intent);
    finish();
}

// onCreate(), at the end, after the if / else if block
btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);
```

`activities/MainActivity.java` — the callback:

```java
} else if (o.getResultCode() == ItemActivity.RESULT_DELETE) {
    Intent data = o.getData();
    if (data == null) return;
    int position = data.getIntExtra(POSITION_EXTRA, -1);
    if (position >= 0 && position < movies.size()) {
        movies.remove(position);
        movieAdapter.notifyDataSetChanged();
    }
}
```

**Why:** deleting needs a single thing: **which** row. The position is the only piece of information that ties the detail screen to the parent's list, because `ItemActivity` doesn't hold the reference to the list. The `RESULT_DELETE` code says *what* to do with the position; without it, the parent would think it has to replace the row.

**Remember:**
1. **`View.GONE`, not `View.INVISIBLE`.** `INVISIBLE` hides the button but keeps the space; the form is left with a 60dp hole under the save button. `GONE` removes the space too.
2. **The button is hidden after `position` has been set.** If you put the line before the `if (existing != null)` block, `position` is still `-1` and the button stays hidden even in edit mode.
3. **The range guard is not optional.** `movies.remove(-1)` throws `IndexOutOfBoundsException`; `movies.remove(99)` the same. The position comes from another UI process and has to be treated as external input.
4. **`notifyDataSetChanged()` after `remove`.** Without it, the movie disappears from the `ArrayList` but stays on screen until the next redraw — and at the exam it looks as if the delete didn't work.
5. **The position breaks if the list changes in the meantime.** If a movie were added at the front between opening the screen and pressing Delete, the position would point to a different row. In this app that can't happen (a single active screen), but in real apps it's solved with a stable id, not with the index.

**Where it applies:** any "delete from the detail screen" — movie, student, product, grade. The pattern: custom code `RESULT_DELETE`, `Intent` with the position (or with the id), new branch in the callback, range guard, `notify`.

</details>

---

## Exercise 36.6 — Confirmation with an AlertDialog before deleting

**Requirement:** The "Delete movie" button no longer deletes directly: it opens an `AlertDialog` with the title "Delete movie", the message `Delete "Toy Story"?` and two buttons, "Delete" and "Cancel". Only "Delete" calls `deleteMovie()`; "Cancel" closes the dialog and nothing happens.

**Files touched:** `activities/ItemActivity.java` (and, if you didn't do 36.5, `res/layout/activity_item.xml`).

**How you approach it — your steps:**
1. In `ItemActivity`, add the imports `androidx.appcompat.app.AlertDialog` and `android.content.DialogInterface`.
2. Write a new `confirmDelete()` method that builds the dialog with `new AlertDialog.Builder(this)`.
3. Chain the calls: `.setTitle(...)`, `.setMessage(...)`, `.setPositiveButton("Delete", listener)`, `.setNegativeButton("Cancel", null)`, `.show()`.
4. In the listener of the `btnDelete` button, replace `deleteMovie();` with `confirmDelete();`.
5. Check: Run, tap a movie, press Delete — the dialog appears with the movie's title. "Cancel" does nothing, "Delete" removes the row.

**Hint 1 — if you get stuck at step 1:** there are two classes with the same name: `android.app.AlertDialog` (the platform one) and `androidx.appcompat.app.AlertDialog` (AppCompat). The app uses the Material 3 theme through AppCompat, so import the `androidx.appcompat.app.AlertDialog` variant. The one in `android.app` compiles and runs, but uses the platform style and doesn't follow the app's theme — different colours, corners and typography.

**Hint 2 — if you get stuck at step 3:** `setNegativeButton("Cancel", null)` is legal: the second argument is a `DialogInterface.OnClickListener` and can be `null`, in which case the button only closes the dialog. You don't need an empty class.

<details>
<summary>Solution — explained</summary>

**What was done:** an `AlertDialog` built with a builder, two buttons and a single place where the delete is actually called.

**Code:**

`activities/ItemActivity.java` — new imports, in the `androidx` block:

```java
import androidx.appcompat.app.AlertDialog;
```

and in the `android` block:

```java
import android.content.DialogInterface;
```

The new method and the modified listener:

```java
private void confirmDelete() {
    new AlertDialog.Builder(this)
            .setTitle("Delete movie")
            .setMessage("Delete \"" + etTitle.getText().toString() + "\"?")
            .setPositiveButton("Delete", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    deleteMovie();
                }
            })
            .setNegativeButton("Cancel", null)
            .show();
}
```

```java
// initListeners() — the listener of btDelete
btDelete.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        confirmDelete();          // instead of deleteMovie();
    }
});
```

**Why:** the dialog is a second decision point between the user and an irreversible operation. `deleteMovie()` stays unchanged — it does the work; `confirmDelete()` only asks for permission. This separation matters: if you put the dialog inside `deleteMovie()`, you would need a second dialog if you ever call the delete from somewhere else.

**Remember:**
1. **`this` in `new AlertDialog.Builder(this)` is `ItemActivity`.** We are in an instance method, not in an anonymous inner class, so `this` is the activity. Inside an `OnClickListener`, `this` would be the listener — that's why you write `ItemActivity.this` there if you need a context.
2. **The dialog closes itself on a button click; `finish()` closes the screen.** The real order: click on "Delete" → listener → `deleteMovie()` → `setResult` → `finish()` → the activity closes, and the dialog disappears along with it.
3. **`setNegativeButton("Cancel", null)`** — a `null` listener means "just close". The alternative with an empty listener does the same thing, with three extra lines.
4. **The message uses the title from the form, not from the model.** `etTitle.getText()` reflects what the user sees right now, including unsaved changes. If you used `existing.getTitle()`, you would show a title that is no longer on screen.
5. **Don't block the UI thread.** `AlertDialog.show()` is non-blocking: the method returns immediately, and the answer comes in the listener. That's why `deleteMovie()` can't be called "after" `show()` in the same method — it would delete before the user presses anything.

**Where it applies:** any irreversible action — delete, exit without saving, reset the form, send over the network. The pattern: a separate method for the action, a confirmation method that wraps it, the button's listener calls the confirmation.

</details>

---

## Exercise 36.7 — Send a new Movie, with no position (insert)

**Requirement:** Trace and verify the complete path of a **new** movie: FAB → `ItemActivity` without `MOVIE_EXTRA` and without `POSITION_EXTRA` → Save → `MainActivity` receives `RESULT_OK`, reads the position as `-1` and does `movies.add(movie)`. Add a `Toast` with `movies.size()` after every insert, as proof.

**Files touched:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**How you approach it — your steps:**
1. Open `MainActivity.initListeners()` and look at the FAB's listener: `new Intent(MainActivity.this, ItemActivity.class)` plus `TITLE_EXTRA` and `YEAR_EXTRA`. **Nothing else.**
2. Open `ItemActivity.onCreate()`: `existing` is `null`, so the `if` block doesn't run, `position` stays `-1`, the form is empty.
3. Open `ItemActivity.saveMovie()`: `intent.putExtra(MainActivity.POSITION_EXTRA, position)` is inside `if (position != -1)`, so it **doesn't run**.
4. Open the callback in `MainActivity`: `intent.getIntExtra(POSITION_EXTRA, -1)` returns `-1` because the key is missing, so the branch is `movies.add(movie)`.
5. Add the proof: after `movieAdapter.notifyDataSetChanged();` in the insert branch, a `Toast` with `movies.size()`.
6. Check: Run, FAB, fill in, Save — the list has 4 rows, the toast reads "4 movies". Repeat — 5 rows, "5 movies".

**Hint 1 — if you get stuck at step 1:** the temptation is to also send an empty `Movie`, so it isn't `null` in `ItemActivity`. Don't do it: `existing != null` would trigger `fillForm(emptyMovie)`, and `dateFormat.format(null)` throws `NullPointerException` immediately. The absence of the extra is exactly the "insert mode" signal.

**Hint 2 — if you get stuck at step 3:** don't add `intent.putExtra(POSITION_EXTRA, -1)` "just to have it". It works, but it turns a clear contract ("the key is missing = insert") into a fragile one ("the value is -1 = insert"). Leave the key out.

<details>
<summary>Solution — explained</summary>

**What was done:** we confirmed the four points of the insert path and added visible proof of the number of items.

**Code:**

`activities/MainActivity.java` — the FAB's listener, final form:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, "New movie");
        intent.putExtra(YEAR_EXTRA, Calendar.getInstance().get(Calendar.YEAR));
        launcher.launch(intent);
        // no MOVIE_EXTRA  -> ItemActivity enters insert mode
        // no POSITION_EXTRA -> nothing to replace
    }
});
```

`activities/ItemActivity.java` — `onCreate()`, the insert branch:

```java
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    // ... edit mode
}
// here: existing == null, position == -1, empty form
```

`activities/ItemActivity.java` — `saveMovie()`, the end:

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.SAVED_EXTRA, true);
if (position != -1)                                   // in insert: false
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

`activities/MainActivity.java` — the callback, the insert branch with the proof:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
    Toast.makeText(MainActivity.this, movies.size() + " movies", Toast.LENGTH_SHORT).show();
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

**Why:** the insert needs no information about the row, because the row doesn't exist yet. All the parent needs to know is "add at the end". `position == -1` is how the two screens agree on this, without a second result code.

**Remember:**
1. **`getIntExtra(key, -1)` returns `-1` both when the key is missing and when the value really is `-1`.** From the parent's point of view, the two cases are identical — and that's fine, because both mean "insert".
2. **Don't send `MOVIE_EXTRA` with an empty object.** `existing != null` would be `true`, `fillForm` would run on a `Movie` with no date, and `dateFormat.format(null)` would throw `NullPointerException`. It's the most common mistake at the exam.
3. **`movies.add(movie)` adds at the end.** The position of the new row is `movies.size() - 1` after the call. If you want to insert at the front, you use `movies.add(0, movie)` — but then every position sent afterwards shifts by one.
4. **The toast with `movies.size()` is the cheapest proof.** At the exam, the teacher sees immediately that the list grows by exactly one, not by two and not by zero.
5. **`notifyDataSetChanged()` is mandatory here too.** `add` moves the data, `notify` makes it visible. The order between them doesn't matter, but both have to be there.

**Where it applies:** any creation of a new entity from a secondary screen — movie, student, product, order. The path: parent with no identity extras → child with `position == -1` → result with no position → `add` + `notify`.

</details>

---
## Exercise 36.8 — Edit and send back without duplicating (position)

**Requirement:** Tap a movie in the list, change the title in the form, press "Update Movie". The list must have the **same number** of rows, and the row you tapped must show the new values. The movie must not appear twice.

**Files touched:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**How you approach it — your steps:**
1. In `MainActivity.initListeners()`, check the row click listener: it puts `MOVIE_EXTRA` **and** `POSITION_EXTRA`, then `launcher.launch(intent)`.
2. In `ItemActivity.onCreate()`, check that `position` is a **field**, not a local variable, and that it is set from `intent.getIntExtra(MainActivity.POSITION_EXTRA, -1)`.
3. In `ItemActivity.saveMovie()`, check that `POSITION_EXTRA` is put back only when `position != -1`.
4. In `MainActivity`, in the callback, check the `else` branch: `movies.set(position, movie)`, not `movies.add(movie)`.
5. Add the range guard before `set`, so the position can't fall outside the list.
6. Check: Run, tap "Inception", change the title to "Inception (2010)", Update — the list still has 3 rows, the first one has the new title.

**Hint 1 — if you get stuck at step 2:** `position` is read in `onCreate`, but used in `saveMovie()`, which runs much later, from a listener. A local variable declared in `onCreate` would only be visible there; `saveMovie()` wouldn't compile. It has to be a field of the class, exactly like `private int position = -1;` in the current code.

**Hint 2 — if you get stuck at step 4:** `movies.set(position, movie)` replaces the element at the index and **keeps** the list size. `movies.add(movie)` grows the list by one. Both compile, both run without an exception — only one is correct.

<details>
<summary>Solution — explained</summary>

**What was done:** we checked the complete edit chain: two extras on the way out, a field that survives until Save, an extra on the way back and a `set` in the parent.

**Code:**

`activities/MainActivity.java` — click on a row:

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));      // the object, serialized
        intent.putExtra(POSITION_EXTRA, position);               // the row index
        launcher.launch(intent);
    }
});
```

`activities/ItemActivity.java` — the field and the read:

```java
private int position = -1;   // FIELD, not a local

// onCreate()
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

`activities/ItemActivity.java` — `saveMovie()`, the end:

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.SAVED_EXTRA, true);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);   // round trip
setResult(RESULT_OK, intent);
finish();
```

`activities/MainActivity.java` — the callback, with a guard:

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    if (intent == null) return;
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else if (position >= 0 && position < movies.size()) {
        movies.set(position, movie);          // REPLACEMENT
    } else {
        return;                               // invalid position: we do nothing
    }
    movieAdapter.notifyDataSetChanged();
}
```

**Why:** the position is the only link between the row in the list and the detail screen. It makes the full round trip: `MainActivity` puts it on the way out, `ItemActivity` keeps it in a field, puts it on the way back, `MainActivity` uses it in `set`. If it's missing anywhere along the path, `getIntExtra` returns `-1` and the edited movie becomes a new movie added at the end.

**Remember:**
1. **The object received in `ItemActivity` is a copy.** `Intent` serializes `Movie` at `putExtra` and deserializes it on read. Changes to the fields of `existing` don't show up in the parent's list. That's why `saveMovie()` builds a new `Movie` and sends it back — that is the only way the change reaches the list.
2. **`position` has to be a field.** It is read in `onCreate` and used in `saveMovie()`, called from a listener. A local variable doesn't survive.
3. **`Movie` has to stay `Serializable`.** If you remove `implements Serializable`, `putExtra(String, Serializable)` no longer compiles, and a `Parcelable` variant would need `writeToParcel` and `CREATOR`. For the exam, `Serializable` is enough.
4. **`IntentCompat.getSerializableExtra(intent, key, Movie.class)` is the modern variant.** `intent.getSerializableExtra(key)` is deprecated since API 33 and returns `Serializable`, so you need a cast. The `Class<T>` variant does the cast safely.
5. **The range guard also catches the accidentally sent `position == -1`.** If you put `POSITION_EXTRA` with `-1` on insert, the `position == -1` branch treats it as an addition anyway — but if someone sends `99`, without the guard you get `IndexOutOfBoundsException`.

**Where it applies:** any edit that has to update a list — movie, student, product, grade. The rule of the three `position`s: you send it out, you keep it in a field, you send it back.

</details>

---

## Exercise 36.9 — Implicit intent: open a link in the browser

**Requirement:** Add a button "Open poster in browser" to `ItemActivity`, in the "Poster" card. Pressed, it takes the URL from `etPoster` and opens it in an external app with `Intent.ACTION_VIEW`. If the field is empty, show an error on the field; if there is no app that can open the link, show a `Toast`.

**Files touched:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `AndroidManifest.xml`.

**How you approach it — your steps:**
1. In `activity_item.xml`, in Card 4 (Poster), after the `TextInputLayout` of `etPoster`, add a `MaterialButton` with `android:id="@+id/btnOpenPoster"`, style `@style/Widget.Material3.Button.TextButton`.
2. In `ItemActivity`, add the import `android.net.Uri`.
3. Add the field `private Button btOpenPoster;`, the line in `initControls()` and the listener in `initListeners()`.
4. Write the `openInBrowser(String url)` method: a guard for empty, the `https://` prefix if the scheme is missing, `Uri.parse`, `new Intent(Intent.ACTION_VIEW, uri)`.
5. Check availability with `intent.resolveActivity(getPackageManager()) != null` before `startActivity`.
6. In `AndroidManifest.xml`, add the `<queries>` block with the `VIEW` action and the `https` scheme, so that it is a direct child of `<manifest>`.
7. Check: Run, type `https://developer.android.com` in Poster, press the button — the browser opens. Empty the field and press — the error appears on the field, with no crash.

**Hint 1 — if you get stuck at step 4:** `Uri.parse("example.com")` produces a URI **with no scheme**. Such a URI has no way of being opened by a browser, and `resolveActivity` returns `null`. That's why the `https://` prefix is added before `Uri.parse`, not after.

**Hint 2 — if you get stuck at step 6:** on Android 11+ (API 30), apps no longer see all the other installed apps. `resolveActivity` filters by visibility, so without `<queries>` it returns `null` even when Chrome is installed. `startActivity` would work — only the check fails, and you show "no app" unfairly.

<details>
<summary>Solution — explained</summary>

**What was done:** a new button, a method that builds an implicit `Intent`, an availability check and the `<queries>` declaration in the manifest.

**Code:**

`res/layout/activity_item.xml` — in Card 4, after the `TextInputLayout` of `etPoster`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnOpenPoster"
    style="@style/Widget.Material3.Button.TextButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Open poster in browser"
    app:icon="@android:drawable/ic_menu_view" />
```

`activities/ItemActivity.java` — import and method:

```java
import android.net.Uri;
```

```java
private Button btOpenPoster;

// initControls()
btOpenPoster = findViewById(R.id.btnOpenPoster);

// initListeners()
btOpenPoster.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        openInBrowser(etPoster.getText().toString().trim());
    }
});

// the new method
private void openInBrowser(String url) {
    if (url.isEmpty()) {
        etPoster.setError("Add a poster link first");
        return;
    }
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        url = "https://" + url;
    }
    Uri uri = Uri.parse(url);
    Intent intent = new Intent(Intent.ACTION_VIEW, uri);
    if (intent.resolveActivity(getPackageManager()) != null) {
        startActivity(intent);
    } else {
        Toast.makeText(this, "No app can open this link", Toast.LENGTH_SHORT).show();
    }
}
```

`AndroidManifest.xml` — a direct child of `<manifest>`, before `<application>`:

```xml
<queries>
    <intent>
        <action android:name="android.intent.action.VIEW" />
        <data android:scheme="https" />
    </intent>
</queries>
```

**Why:** an explicit `Intent` names the class to start (`new Intent(this, ItemActivity.class)`); an implicit one describes **what you want to happen** and lets the system pick the app. `ACTION_VIEW` + an `https` URI means "show me this address", and the system hands it to the browser or to the app that declared itself able to open it. You need no permissions and you don't need to know which browser the user has.

**Remember:**
1. **`<queries>` is about *visibility*, not about permissions.** Since Android 11, `PackageManager` hides undeclared apps. `resolveActivity` returns `null` without `<queries>`, even though `startActivity` would have worked. Two correct solutions: you declare `<queries>` (check first) or you catch `ActivityNotFoundException` (try and defend yourself).
2. **`Uri.parse(null)` throws `NullPointerException`.** Not `IllegalArgumentException`, not `null` — an exception. That's why the `url.isEmpty()` guard is the first line of the method, not a formality.
3. **A URI with no scheme is opened by nobody.** `"example.com"` has no `scheme`, and the manifest filters look exactly at the scheme. The `https://` prefix is mandatory if you let the user type a "bare" address.
4. **`ACTION_VIEW` doesn't ask for the `INTERNET` permission.** The permission is asked for by the app that actually downloads the page — the browser. Your app only starts an `Intent`.
5. **Don't use `ACTION_VIEW` for your own files.** For a file from your app you need `FileProvider` and `content://`; `file://` throws `FileUriExposedException` since API 24.

**Where it applies:** any "open in another app" — link in the browser, map with `geo:`, phone with `tel:`, e-mail with `mailto:`, share with `ACTION_SEND`. The pattern: build the URI, build the `Intent` with the right action, check or catch the exception, start it.

</details>

---

## Exercise 36.10 — Exam combo: new attribute + sent through an Intent

**Requirement:** Add the `trailer` attribute (String) to the movie — the link to the trailer. Show it in the form, in the "Poster" card, under the poster link. In the list, a **long press** on a row opens the trailer in the browser. The attribute has to survive the full round trip through the `Intent`: saved in `ItemActivity`, arriving in `MainActivity`, read on the long press.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`, `util/IntentUtils.java` (new), `AndroidManifest.xml`.

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private String trailer;` next to `private String poster = null;`.
2. In the constructor with 10 parameters, add `String trailer` at the end of the list and `this.trailer = trailer;` at the end of the body.
3. In `toString()`, add `", trailer='" + trailer + '\'' +` after the `poster` line.
4. Add `getTrailer()` and `setTrailer()` next to `getPoster()`/`setPoster()`.
5. Compile: three errors show up in `MainActivity.addSampleMovies()`. Add the 11th argument to each of the three `new Movie(...)` calls.
6. In `activity_item.xml`, in Card 4, after the `TextInputLayout` of `etPoster`, add `TextInputLayout` + `TextInputEditText` with `android:id="@+id/etTrailer"`.
7. In `ItemActivity`: the field `private EditText etTrailer;`, the line in `initControls()`, the line in `fillForm()`, the line in `saveMovie()`.
8. Create `util/IntentUtils.java` with the static method `openInBrowser(Activity, String)`.
9. In `MainActivity.initListeners()`, add `setOnItemLongClickListener` that reads `movies.get(position).getTrailer()` and calls the helper. **Return `true`.**
10. Check: Run, add a movie with the trailer `https://www.youtube.com/watch?v=dQw4w9WgXcQ`, hold on the row — the browser opens. Hold on "Inception" — the demo trailer opens.

**Hint 1 — if you get stuck at step 5:** the constructor is **positional**. The 11th argument has to be exactly `String`, and if you put it in a different position than in the declaration, the compiler complains about types or, worse, it passes and mixes up the values. The order of the parameters and the order of the arguments have to be identical.

**Hint 2 — if you get stuck at step 9:** `setOnItemLongClickListener` has a `boolean` as its return value. If you return `false`, the event isn't consumed and the normal click fires too — that is, after the browser opens, the edit screen opens on top of it. `return true;` in both branches.

<details>
<summary>Solution — explained</summary>

**What was done:** a new attribute in the model, its field in the form, reading and writing in `ItemActivity`, the new arguments in the demo data, an implicit navigation helper and a long-press listener in `MainActivity`.

**Code:**

Steps 1–4 — `model/Movie.java`:

```java
private String poster = null;
private String trailer;                       // the new field

public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String trailer) {
    // ... the same assignments
    this.poster = poster;
    this.trailer = trailer;                   // the new line
}

// toString(), after the poster line
", trailer='" + trailer + '\'' +

public String getTrailer() {
    return trailer;
}

public void setTrailer(String trailer) {
    this.trailer = trailer;
}
```

Step 5 — `MainActivity.addSampleMovies()`, all three calls:

```java
movies.add(new Movie(
        "Inception",
        new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),
        "Sci-Fi",
        160000000,
        148,
        4.5f,
        true,
        "PG-13",
        false,
        "https://example.com/posters/inception.jpg",
        "https://www.youtube.com/watch?v=YoHD9XEInc0"));   // ← the 11th argument
```

```java
// Toy Story
"https://example.com/posters/toy-story.jpg",
"https://www.youtube.com/watch?v=xNWSGRD5CzU"));

// The Matrix
"https://example.com/posters/the-matrix.jpg",
"https://www.youtube.com/watch?v=vKQi3bBA1y8"));
```

Step 6 — `res/layout/activity_item.xml`, in Card 4, after the `TextInputLayout` of `etPoster`:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="12dp"
    app:hintEnabled="false"
    app:endIconMode="clear_text"
    app:startIconContentDescription="Trailer link"
    app:startIconDrawable="@android:drawable/ic_media_play">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etTrailer"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Trailer URL"
        android:inputType="textUri" />
</com.google.android.material.textfield.TextInputLayout>
```

Step 7 — `activities/ItemActivity.java`, four places:

```java
private EditText etTrailer;

// initControls()
etTrailer = findViewById(R.id.etTrailer);

// fillForm()
etTrailer.setText(existing.getTrailer() != null ? existing.getTrailer() : "");

// saveMovie()
movie.setTrailer(etTrailer.getText().toString());
```

Step 8 — `util/IntentUtils.java`, new file:

```java
package ro.ase.ie.g1097.util;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;

public final class IntentUtils {

    private IntentUtils() {
    }

    public static void openInBrowser(Activity activity, String url) {
        if (url == null || url.trim().isEmpty()) {
            Toast.makeText(activity, "No link to open", Toast.LENGTH_SHORT).show();
            return;
        }
        String fixed = url.trim();
        if (!fixed.startsWith("http://") && !fixed.startsWith("https://")) {
            fixed = "https://" + fixed;
        }
        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(fixed));
        try {
            activity.startActivity(intent);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(activity, "No app can open this link", Toast.LENGTH_SHORT).show();
        }
    }
}
```

Step 9 — `activities/MainActivity.java`, in `initListeners()`:

```java
import ro.ase.ie.g1097.util.IntentUtils;
```

```java
listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
    @Override
    public boolean onItemLongClick(AdapterView<?> parent, View view, int position, long id) {
        IntentUtils.openInBrowser(MainActivity.this, movies.get(position).getTrailer());
        return true;      // consumes the event
    }
});
```

**Why:** the exercise ties the two halves of the chapter together. The new attribute has to go through five representations before it reaches the screen (model → form → activity → `Intent` → list), and at the end it is used by an implicit `Intent`. If any link is missing, the chain breaks silently: `getTrailer()` returns `null`, and the helper shows "No link to open" instead of opening the browser.

**Remember:**
1. **`return true` in `onItemLongClick` is mandatory.** Otherwise the event propagates to the `OnItemClickListener` too, so after the browser the edit screen opens as well. Two actions from a single touch.
2. **The helper uses `try / catch`, not `resolveActivity`.** It's the variant that doesn't need `<queries>`: you don't ask whether an app exists, you try and defend yourself if it doesn't. For an external link it's sufficient and less fragile.
3. **`url == null` has to be checked before `Uri.parse`.** `Uri.parse(null)` throws `NullPointerException`, and a demo `Movie` without a trailer (or one built before the attribute existed) has exactly `null`.
4. **`fillForm` needs a guard.** `etTrailer.setText(null)` shows an empty field, but if you add a `TextWatcher` or a `setError`, `null` becomes a problem. `existing.getTrailer() != null ? ... : ""` costs three words.
5. **The order of the constructor parameters is the contract.** `trailer` after `poster`, in the declaration and in all three calls. If you put it between `approval` and `onWatchlist`, the compiler doesn't stop you — `String` next to `String` passes, and the data gets mixed up.

**Where it applies:** exactly the format "add an attribute and use it in an `Intent`" — trailer link, site address, phone number, coordinates. The chain from chapter 17 (five layers) plus the two directions from chapter 36 (outbound and inbound) cover most exam requirements that combine the model with navigation.

</details>

---

## Recap — what you check at the test

| The requirement at the exam | The mechanism | Exercise |
|---|---|---|
| "send a text to the next screen" | `putExtra(TITLE_EXTRA, ...)` + `getStringExtra` | 36.1 |
| "send two values" | two keys, two reads, a single `null` guard | 36.2 |
| "tell me if it was saved" | `putExtra(SAVED_EXTRA, true)` + `getBooleanExtra(..., false)` | 36.3 |
| "the second button closes differently" | `RESULT_DRAFT = 2` + a new branch in the callback | 36.4 |
| "delete the movie from the detail screen" | `RESULT_DELETE` + position + `movies.remove` | 36.5 |
| "ask for confirmation first" | `AlertDialog.Builder` around `deleteMovie()` | 36.6 |
| "add a new movie" | no `MOVIE_EXTRA`, no `POSITION_EXTRA` → `add` | 36.7 |
| "edit without duplicating" | `POSITION_EXTRA` round trip → `set` | 36.8 |
| "open a link" | `ACTION_VIEW` + `Uri.parse` + `<queries>` or `try/catch` | 36.9 |
| "new attribute + navigation" | the chain from chapter 17 + `ACTION_VIEW` on long press | 36.10 |

**The checklist before Run — six checks, in the order in which they break:**

| # | Check | The symptom if it's missing |
|---|---|---|
| 1 | The extra constant has the same value in both activities | `null` on read, with no error |
| 2 | `position` is a **field** in `ItemActivity`, not a local | it doesn't compile in `saveMovie()` |
| 3 | `setResult(...)` is called before `finish()` | the parent receives `RESULT_CANCELED` |
| 4 | `o.getData()` is checked for `null` | `NullPointerException` on the branch without an `Intent` |
| 5 | `add` on insert, `set` on edit | a duplicate or a lost movie |
| 6 | `notifyDataSetChanged()` after every mutation | the list shows old data |

**Three sentences to memorize:**

1. **An `Intent` carries data; a result code says what happened.** `putExtra` on the way out, `setResult(code, intent)` on the way back, `getResultCode()` + `getData()` in the callback. Four methods, two directions.
2. **The object that travels is a copy.** Serialization at `putExtra` and deserialization on read produce a new object. Changing it doesn't touch the list; only `movies.set(position, newMovie)` touches it.
3. **`registerForActivityResult` is called in `onCreate`, not in a listener.** At `d719ffc` it is the very last statement in `onCreate`, after `initListeners()`. Moved into an `onClick`, it throws `IllegalStateException: LifecycleOwner is attempting to register while current state is RESUMED`.

---

## Chapter 36 summary

**What you built:** a complete navigation path between two activities — data on the way out, data on the way back, custom result codes, confirmation, delete, insert, edit and an implicit `Intent` to the browser.

**The table of methods, by direction:**

| Direction | Method | Where | Who reads it |
|---|---|---|---|
| outbound | `putExtra(String, String)` | `MainActivity`, at `launch` | `getStringExtra` |
| outbound | `putExtra(String, int)` | `MainActivity`, at `launch` | `getIntExtra(key, -1)` |
| outbound | `putExtra(String, Serializable)` | `MainActivity`, click on a row | `IntentCompat.getSerializableExtra` |
| inbound | `setResult(int, Intent)` | `ItemActivity.saveMovie()` | `getResultCode()` + `getData()` |
| inbound | `setResult(int)` | `ItemActivity.saveDraft()` | only `getResultCode()` |
| launch | `launcher.launch(intent)` | `MainActivity` | — |
| registration | `registerForActivityResult(...)` | `MainActivity.onCreate()` | — |

**The four traps that cost marks:**

1. **You forget `setResult`.** The screen closes with `RESULT_CANCELED` and the parent ignores everything. It happens when you press Back "to test" and think you saved.
2. **You send `MOVIE_EXTRA` without `POSITION_EXTRA`.** `ItemActivity` enters edit mode with an empty object, `fillForm` reaches `dateFormat.format(null)` and throws `NullPointerException`.
3. **You do `add` instead of `set`.** The edited movie shows up twice, the original stays unchanged, and the list grows on every Update.
4. **You move `registerForActivityResult` into a listener.** `IllegalStateException` on the first click, because the registration has to be done during the activity's construction, when the state is `CREATED`.

**What comes next:** if the exam asks "send data between screens", you have 36.1–36.8. If it asks "open something outside the app", you have 36.9. If it asks for both plus a new attribute, you have 36.10 — and, behind it, the chain from chapter 17.
