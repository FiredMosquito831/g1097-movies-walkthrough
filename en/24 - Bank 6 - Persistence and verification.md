# Chapter 24 — Bank 6: persistence and verification

**Objective:** to be able to demonstrate at the exam, in under a minute, that what you save **actually** reaches the list, with the right values, exactly once — and to know exactly what survives a rotation, leaving the app, and a restart. Bank 6 doesn't ask for spectacular code: it asks for **proof** that the chain works, plus real persistence, on disk.

**Where the data lives at d719ffc:** `private final List<Movie> movies = new ArrayList<>();` in `MainActivity`. Nothing on disk.

**The three levels of persistence:**

| Level | What survives | How |
|---|---|---|
| Form state | rotation | `onSaveInstanceState` |
| The list in memory | as long as the process lives | `ArrayList` in `MainActivity` |
| The list on disk | app restart | `SharedPreferences` / file / Room |

**What the requirement looks like at the exam:** "The data must be saved." Four words, two hidden requirements:

- **(a)** on Save, the movie appears in the list, with the right values;
- **(b)** on edit, the list updates **in place**, with no duplicates.

The rest of the chapter is about how you **demonstrate** (a) and (b) — and about what you answer when the professor asks "and after you close the app?"

**Three real defects at `d719ffc` that you will run into during verification.** They are not made-up scenarios; they are in the code:

| Defect | Where | Symptom |
|---|---|---|
| `Double.parseDouble("")` | `ItemActivity.saveMovie()`, line 173 | Save with an empty budget → `NumberFormatException`, the app crashes, nothing comes back to the list |
| `dateFormat.format(null)` | `ItemActivity.fillForm()`, line 88 | a `Movie` with `release == null` → `NullPointerException` when opening it for edit |
| `String.valueOf(double)` | `ItemActivity.fillForm()`, line 89 | the budget shows as `1.6E8` instead of `160000000` |

The first and the second kill requirement (a) before it even gets to run. The third doesn't crash anything, but it looks ugly and it is the one that makes you think "it wasn't saved" when in fact it was.

**Convention:** the UI texts stay in English, as in the app (`"Save Movie"`, `"Update Movie"`, `"Yes"`, `"No"`). The prose, the code comments and the explanations are in Romanian. The line numbers refer to `cod-final/` at commit `d719ffc`.

**Map of the exercises:**

| # | What you verify | The mechanism behind it | Level |
|---|---|---|---|
| 24.1 | the addition reaches the screen | `notifyDataSetChanged()` | list |
| 24.2 | the edit replaces, it doesn't add | `movies.set(position, ...)` | list |
| 24.3 | Back cancels | `RESULT_OK` + the copy through the `Intent` | navigation |
| 24.4 | the movie count is right | `movies.size()` + `Toast` | list |
| 24.5 | rotation | `onSaveInstanceState` | form |
| 24.6 | app restart | `SharedPreferences` + hand-built JSON | disk |
| 24.7 | a new attribute is saved and reloaded | a checklist of 6 checks | all |
| 24.8 | "it saves, but it doesn't show up" | triage: Logcat, breakpoint, `Toast` | debug |
| 24.9 | "it shows up twice" | `add` vs. `set` | debug |
| 24.10 | the exam | (a) + (b), end to end | all |

---

## Exercise 24.1 — You add a movie, it shows up in the list. What happens if you forget `notifyDataSetChanged()`?

**Requirement:** Add a movie from the form and confirm that it shows up in the list. Then temporarily **remove** `movieAdapter.notifyDataSetChanged()` from the add branch and describe exactly what you see on the first run, on the second addition, and in Logcat. At the end, say why the symptom is not "nothing happens" but "the list stays one step behind".

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` — the callback in `onCreate()` (lines 63–77), plus a `Log.d` line for diagnostics.

**How you approach it — your steps:**
1. Open `MainActivity.java` and read the callback at lines 63–77. Note the two branches: `position == -1` → `movies.add(movie)` (line 70); otherwise → `movies.set(position, movie)` (line 75). Both are followed by `movieAdapter.notifyDataSetChanged()` (lines 71 and 76).
2. Run the app. The list has 3 rows: Inception, Toy Story, The Matrix.
3. Tap the FAB, fill in the title "Dune", the budget `165000000`, pick a date, tap "Save Movie". Go back to the list: the 4th row appears. **That is the correct behaviour.**
4. Comment out line 71 (`// movieAdapter.notifyDataSetChanged();`), run again, add "Dune". Go back to the list: 3 rows remain. Add "Alien". Go back: as a rule "Dune" shows up, but not "Alien". Note the feeling: **the list is one step behind**.
5. Temporarily add a log right after `movies.add(movie)`:
   ```java
   Log.d("G1097", "dupa add: movies=" + movies.size()
           + " adapter=" + movieAdapter.getCount()
           + " listView=" + listView.getCount());
   ```
   Run and look in Logcat at the `G1097` filter. The three values must be equal. When they aren't, you have found the bug.
6. Put line 71 back and confirm that the three values are equal again after every operation.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 4</summary>

`ArrayAdapter` does not copy the list, it holds a **reference** to it. So `movies.add(movie)` modifies exactly the list the adapter reads. What is missing is not the data, but the **announcement** that the data has changed.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

`adapter.getCount()` returns `mObjects.size()`, i.e. the live value. `listView.getCount()` returns `mItemCount`, the value **cached** at the last `onChanged()`. The difference between them is exactly `notifyDataSetChanged()`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** nothing new in the final code — the chain was verified and it was demonstrated what breaks without the notification.

**Code:**

```java
// MainActivity, the callback in onCreate(), lines 63–77 — exists at d719ffc
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
        movieAdapter.notifyDataSetChanged();   // ← the only signal to the ListView
    } else {
        movies.set(position, movie);
        movieAdapter.notifyDataSetChanged();
    }
}
```

```java
// diagnostics — one line, in the callback, after notify
Log.d("G1097", "movies=" + movies.size()
        + " adapter=" + movieAdapter.getCount()
        + " listView=" + listView.getCount());
```

**Why:** the chain has four links and only the last one redraws:

1. `movies.add(movie)` moves the data. The list is the same instance the adapter received in its constructor (`new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, line 55).
2. `ArrayAdapter.getCount()` returns `mObjects.size()` — so it **already** sees 4 elements.
3. `ListView` never asks the list. It asks the adapter, but only when it is notified: `notifyDataSetChanged()` → `DataSetObservable.notifyChanged()` → `AdapterView.onChanged()`, which does `mItemCount = getAdapter().getCount()` and `requestLayout()`.
4. Without step 3, `mItemCount` stays 3. `ListView` has no reason to ask for a fourth row.

That is why the symptom is "one step behind": `ListView.onMeasure()` re-reads `mItemCount` from the adapter (`mItemCount = mAdapter == null ? 0 : mAdapter.getCount();`). On the next full measure pass — a rotation, coming back to the screen, a layout change — the missing row appears "by itself", and the one added right after it stays hidden. From the outside it looks like a list that lags, not like a bug.

There is also an ugly ending: if a layout pass runs **without** a measure, with `mItemCount` left behind, `ListView.layoutChildren()` throws:

```
java.lang.IllegalStateException: The content of the adapter has changed but
ListView did not receive a notification. Make sure your adapter calls
notifyDataSetChanged() when its content changes.
```

That message is the best teacher: it tells you exactly what you forgot.

**Remember:** `ArrayAdapter.add(movie)` calls `notifyDataSetChanged()` by itself at the end. So `movieAdapter.add(movie)` would work even without the explicit line — proof that what matters is not the mutation, but the **notification**. `movies.add(movie)` bypasses the adapter, which is why nobody notifies. This is also the short answer at the exam: "the adapter doesn't watch the list; you notify it".

**Where it applies:** any list + adapter pair — `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter` (where the equivalent is `notifyItemInserted` / `notifyItemChanged` / `notifyDataSetChanged`). The rule: **a single method that moves the data and notifies**, called from every place. If `movies.add` appears in two places and `notify` in only one, you already have the bug.

</details>

---

## Exercise 24.2 — You edit a movie, the list shows the NEW values. Why `set` and not `add`?

**Requirement:** Open "Inception", change the title to "Inception (2010)" and the budget to `200000000`, tap "Update Movie". The list must show the new values, and the number of rows must stay 3. Then explain why the code uses `movies.set(position, movie)` and not `movies.add(movie)`, and why you could not simply modify the object received in `ItemActivity`.

**Files touched:** `MainActivity.java` — the `else` branch of the callback (lines 73–77); `ItemActivity.java` — `saveMovie()` (lines 168–194), read, not modified.

**How you approach it — your steps:**
1. Run the app and tap the "Inception" row. The form opens pre-filled, and the button reads "Update Movie" — a sign that `position != -1`.
2. Change the title and the budget, tap "Update Movie". In the list, row 0 shows the new values; the list still has 3 rows.
3. Open `MainActivity.java` at line 75 and temporarily replace `movies.set(position, movie);` with `movies.add(movie);`. Run again and repeat the edit.
4. Look at the list: 4 rows. The first is the **old** "Inception", the last is the **new** "Inception (2010)". This is the difference between `set` and `add`, visible on screen.
5. Put `set` back. Then open `ItemActivity.java` at lines 76–83 and ask yourself why `fillForm(existing)` cannot "save" the changes directly into the parent's object.
6. Check: after Update, tap the row again → the form shows the new values. If it showed the old ones, you added instead of replacing.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 5</summary>

the object that leaves through the `Intent` is not the object in the list. `putExtra(String, Serializable)` serializes it, and the `Intent` goes through `system_server` (Binder), so at the destination a **new instance** is rebuilt. You modify the copy, not the original.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 3</summary>

`set(index, element)` replaces the element at the index and **keeps the size**. `add(element)` adds at the end and **grows the size**. Neither forces you to use the returned value — `add` returns `boolean`, `set` returns the old element — so the compiler doesn't warn you that you chose wrong.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** it was confirmed that the edit replaces, it was demonstrated what happens with `add`, and it was explained why the object in `ItemActivity` is a copy.

**Code:**

```java
// MainActivity, lines 73–77 — the correct version (d719ffc)
else {
    movies.set(position, movie);          // replaces at the index
    movieAdapter.notifyDataSetChanged();  // and refreshes the visible rows
}
```

```java
// wrong — leads to a duplicate (see also 24.9)
else {
    movies.add(movie);                    // the original stays at position
    movieAdapter.notifyDataSetChanged();  // and the copy appears at the end
}
```

```java
// ItemActivity, lines 76–83 — why you cannot modify the original
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);                   // reads from a COPY
    ...
}
```

**Why:** three independent reasons, all valid at the exam:

1. **`set` preserves the list's invariant.** An edit doesn't change the number of movies. `add` would turn 3 rows into 4, and requirement (b) at the exam — "no duplicates" — fails immediately.
2. **The object in `ItemActivity` is a copy.** `Movie implements Serializable` (line 6 of `Movie.java`). `putExtra` puts it in a `Bundle`, the `Intent` crosses Binder to `system_server` and back, and `getSerializableExtra` deserializes it into a new instance. Even if `ItemActivity` did `existing.setTitle("X")`, the object in `movies` would stay untouched. That is why the parent must **receive** the new object and install it itself.
3. **`saveMovie()` builds a new `Movie` anyway.** The first line of the method (168) is `Movie movie = new Movie();`. There is no path by which the changes reach the old object — and there doesn't need to be one.

Why the change is visible immediately: `ArrayAdapter.getView()` calls `toString()` on the object at that position. After `set`, the new object sits at `position`, so `toString()` returns the new values. The old object is no longer referenced by anyone and the garbage collector takes it.

`notifyDataSetChanged()` remains mandatory after `set` too: the number of rows doesn't change, but the **content** does, and `ListView` has to recycle and rebuild the visible rows.

**Remember:** `movies.set(position, movie)` throws `IndexOutOfBoundsException` if `position` is outside the list. `position` comes from an `Intent`, so it is "data from someone else" — don't trust it. The minimum guard, which also goes into the code from 24.10:

```java
if (position >= 0 && position < movies.size()) {
    movies.set(position, movie);
} else {
    Log.e("G1097", "position invalid: " + position + ", size=" + movies.size());
}
```

**Where it applies:** any "edit" in Android — `set` + `notifyItemChanged` in `RecyclerView`, `UPDATE ... WHERE id = ?` in SQLite, `map.put(key, value)` in a dictionary. Everywhere: replacement at a key, not addition. The `add`/`set` confusion is the most common source of duplicates at the test.

</details>

---

## Exercise 24.3 — You press Back without Save: nothing changes. What guarantees that?

**Requirement:** Open a movie, change the title, press Back (without "Update Movie"). The list must stay unchanged, and reopening the movie must show the original title. Explain **what exactly** in the code guarantees this — there are three independent mechanisms — and what would happen if you called `setResult(RESULT_OK, ...)` too early.

**Files touched:** `ItemActivity.java` — `saveMovie()` (lines 188–193); `MainActivity.java` — the callback (lines 63–77). Both read; possibly one log line for the demonstration.

**How you approach it — your steps:**
1. Run the app, open "Toy Story", change the title to "Toy Story 2", press Back (gesture or the system button).
2. The list: unchanged. Reopen "Toy Story": the title is still "Toy Story". Nothing was lost and nothing broke.
3. Open `ItemActivity.java` and look for every occurrence of `setResult`. There is a single line (192), immediately followed by `finish()` (193), both in `saveMovie()`.
4. Open `MainActivity.java` at line 63: `if (o.getResultCode() == RESULT_OK)`. Ask yourself what value `resultCode` has when the user presses Back.
5. Temporarily add a `Toast` in the callback, **before** the `if`, showing `o.getResultCode()` and whether `o.getData()` is `null`. Repeat both steps: Save → `-1` (RESULT_OK) and an `Intent`; Back → `0` (RESULT_CANCELED) and `null`.
6. Remove the `Toast`. Optionally, the dangerous experiment from "Why": put `setResult(RESULT_OK);` at the end of `onCreate()` and press Back.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 4</summary>

`RESULT_OK` is `-1`, `RESULT_CANCELED` is `0`. An activity that closes without calling `setResult` reports `RESULT_CANCELED`. Back doesn't call `saveMovie()`, so there is nobody to set anything else.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

`setResult` does not "reset" on Back. The code left set is used by `finish()`. That is why `setResult` is called as the **last** statement before `finish()`, never pre-emptively.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the three guarantees that make Back harmless were identified, and the trap of the sticky `setResult` was demonstrated.

**Code:**

```java
// ItemActivity.saveMovie(), lines 188–193 — the only place with setResult
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

```java
// MainActivity, line 63 — the entry gate
if (o.getResultCode() == RESULT_OK) {
    ...
}
```

**Why:** three independent mechanisms, each would be enough on its own:

1. **`setResult` is called only in `saveMovie()`.** And `saveMovie()` is wired only to the `btMovieAction` button (`initListeners()`, lines 138–143). Back doesn't go through there. Without `setResult`, `resultCode` stays `RESULT_CANCELED` (0).
2. **The callback filters.** Even if the result came with another code, `if (o.getResultCode() == RESULT_OK)` blocks anything else. The gate is in the parent, not in the child — which is good, because the parent is the one that owns the data.
3. **We copy, we don't share.** Even if `ItemActivity` modified the object it received (it did `existing.setTitle(...)`), that is a deserialized instance, separate from the one in `movies`. The parent doesn't see the change. (The detail is explained in 24.2.)

The order in `saveMovie()` matters: `setResult(...)` **before** `finish()`. The other way round, the result never arrives — `finish()` destroys the activity, and a `setResult` called after it has nobody left to read it.

**The trap:** `setResult` is sticky. If you call it at the end of `onCreate()` "just to be safe", then Back will report `RESULT_OK`, and `MainActivity` will enter the save branch with an `Intent` that has no `MOVIE_EXTRA`. The result is a `NullPointerException` at `intent.getSerializableExtra(...)` or, with a guard, a `null` movie added to the list. Demonstrate it once, then remove the line. The lesson: **the result is built when the user confirms, not when the screen opens.**

**Remember:** `o.getData()` can be `null` even with `RESULT_OK` (if someone called `setResult(RESULT_OK)` without an `Intent`). The guard from 24.10 — `if (o.getResultCode() == RESULT_OK && o.getData() != null)` — is not paranoia, it is exactly the scenario above.

**Where it applies:** any "form → list" pair: a confirmation dialog (`AlertDialog` with OK/Cancel), a settings screen, a wizard with steps. The universal rule: **Back = cancel, the explicit button = confirm**, and the parent checks the code, it doesn't trust the child.

</details>

---

## Exercise 24.4 — 3 additions + 1 edit: the movie count is right. Verification with a `Toast`

**Requirement:** Start from the 3 demo movies, add 3 new movies and edit one existing one. On every operation, a `Toast` shows `movies.size()`. At the end, the list must have **6** rows, and the three numbers — `movies.size()`, `movieAdapter.getCount()`, `listView.getCount()` — must be equal after every operation.

**Files touched:** `MainActivity.java` — a new `showCount(String)` method and two calls in the callback.

**How you approach it — your steps:**
1. Open `MainActivity.java` and add the method below, next to `addSampleMovies()`.
2. Call it at the end of each branch of the callback, after `notifyDataSetChanged()`.
3. Run and write down on paper, in order: `3` (start), `4`, `5`, `6` (the three additions), `6` (the edit).
4. Check the table below. If a row differs, stop and find out why before you continue — a wrong number at step 2 will produce a duplicate at step 5.
5. Also add the duplicate check (the `hasDuplicateTitles()` method), called in the same place. On a correct test it must always show `false`.
6. Final check on the emulator: after the four operations, count the rows by eye. Six. Tap the last movie added: the form opens with its values.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

`movies.size()` grows only on `add`. `set` doesn't change the size. So 3 + 3 = 6, and the edit leaves 6. If you get 7, you used `add` on the edit branch too (24.9). If you get 5, you used `set` on the add branch too — you overwrote a movie.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

`Toast.makeText(...)` needs a `Context`; in an activity that is `this`. `Toast.LENGTH_SHORT` is the duration constant. Don't forget `.show()` — without it, the object is built and nothing appears.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a cheap check was added that turns an assumption into proof: the number of elements in the list, in the adapter and in the `ListView`, shown after every operation.

**Code:**

```java
// MainActivity — the verification method
private void showCount(String step) {
    String message = step + ": " + movies.size() + " filme";
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    Log.d("G1097", message
            + " | adapter=" + movieAdapter.getCount()
            + " | listView=" + listView.getCount()
            + " | duplicate=" + hasDuplicateTitles());
}

private boolean hasDuplicateTitles() {
    for (int i = 0; i < movies.size(); i++) {
        for (int j = i + 1; j < movies.size(); j++) {
            if (Objects.equals(movies.get(i).getTitle(), movies.get(j).getTitle())) {
                return true;
            }
        }
    }
    return false;
}
```

```java
// the calls, in the callback
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
    showCount("dupa adaugare");
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
    showCount("dupa editare");
}
```

```java
// new import in MainActivity
import java.util.Objects;
```

**Why:** the expectation table, written before you run, is the best debugging tool. Without it, "I think there were six" is an impression; with it, 5 or 7 is a fact.

| Step | Action | `movies.size()` | `adapter.getCount()` | `listView.getCount()` | `duplicate` |
|---|---|---|---|---|---|
| 0 | startup | 3 | 3 | 3 | `false` |
| 1 | add "Dune" | 4 | 4 | 4 | `false` |
| 2 | add "Alien" | 5 | 5 | 5 | `false` |
| 3 | add "Arrival" | 6 | 6 | 6 | `false` |
| 4 | edit "Inception" | 6 | 6 | 6 | `false` |

Three numbers, three different sources: `movies.size()` is the truth in the model, `adapter.getCount()` is what the adapter sees, `listView.getCount()` is what the `ListView` managed to display. When the first differs from the second, you have two lists (or two adapters). When the second differs from the third, you forgot `notifyDataSetChanged()` (24.1).

`hasDuplicateTitles()` is the check that catches exactly the defect from 24.9 before it reaches the professor. Comparing by title is enough for the exam; the correct version, on `equals`/`hashCode`, is discussed in 24.9.

**Remember:** a `Toast` is for you, not for the user — at the exam it is accepted as proof, but in a real app you use `Log.d` or a status `TextView`. The `Toast` is shown on the main thread; the callback runs on the main thread, so it is safe. If you called `showCount` from a background thread, you would need `runOnUiThread`.

**Where it applies:** any requirement of the "show how many there are" or "check the count" kind. At the test, if the professor asks "display the number of movies", the `Toast` from 24.4 is the answer; if he asks for "permanently on screen", move the text into a `TextView` and update it in the same method — not in two different places.

</details>

---

## Exercise 24.5 — Rotation: what actually gets lost from the form. `onSaveInstanceState`

**Requirement:** Fill in the form in `ItemActivity`, turn the phone and write down, for each control, whether the value was kept. Then explicitly save the whole form with `onSaveInstanceState` / `onRestoreInstanceState`, so you don't depend on what the framework does. At the end, explain why the list in `MainActivity` behaves completely differently on the same rotation.

**Files touched:** `ItemActivity.java` — six new constants, `onSaveInstanceState`, `onRestoreInstanceState`; `MainActivity.java` — optional, the `Bundle` version at the end.

**How you approach it — your steps:**
1. Run the app, tap the FAB (insert mode), type "Test rotation", pick a date from the picker, move the `SeekBar` to 120, set 4 stars, turn the switch on. Rotate the emulator (`Ctrl+Left` / `Ctrl+Right`).
2. Note what was kept: the title, the displayed date, the duration, the rating, the switch. Almost everything. Now tap "Save Movie" and look at the movie in the list: **the date is today's**, not the one you picked. Here is the real loss.
3. Open `ItemActivity.java` and list the fields that are **not** `View`s: `position` (57), `releaseCal` (58), `dateFormat` (59). For each, ask yourself who reinitializes it on recreation.
4. Add the six `KEY_*` constants next to `position` and the two methods, after `onCreate()`.
5. Run the test from step 1 again, then tap "Save Movie". The date in the list must be the one you picked.
6. Open "Inception" (edit mode), change the title, rotate, tap "Update Movie". Then go back to `MainActivity`, add a movie and rotate there.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

the framework saves by itself the `View`s that have an `android:id` and `android:saveEnabled="true"` (the default). `EditText.getFreezesText()` returns `true`; `ProgressBar` (the base for `SeekBar` and `RatingBar`) saves its progress; `CompoundButton` saves its check state; `AbsSpinner` saves its position. What is **not** a `View` is not saved.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

in `MainActivity`, `movies` is a field of the activity, initialized inline with `new ArrayList<>()`. On rotation a new activity is created, hence a new, empty list. `addSampleMovies()` fills it again with the three demos. `ListView` saves only the scroll position, not the data.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** it was measured what survives without code, then the explicit saving of the form state was added — with the emphasis on `releaseCal`, the only field that really mattered.

**Code:**

```java
// ItemActivity — new fields, next to position (line 57)
private static final String KEY_TITLE = "key_title";
private static final String KEY_BUDGET = "key_budget";
private static final String KEY_DURATION = "key_duration";
private static final String KEY_RATING = "key_rating";
private static final String KEY_RELEASE = "key_release";
private static final String KEY_RELEASE_TEXT = "key_release_text";
```

```java
// ItemActivity — after onCreate()
@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putString(KEY_TITLE, etTitle.getText().toString());
    outState.putString(KEY_BUDGET, etBudget.getText().toString());
    outState.putInt(KEY_DURATION, sbDuration.getProgress());
    outState.putFloat(KEY_RATING, rbRating.getRating());
    outState.putLong(KEY_RELEASE, releaseCal.getTimeInMillis());
    outState.putString(KEY_RELEASE_TEXT, etRelease.getText().toString());
}

@Override
protected void onRestoreInstanceState(@NonNull Bundle savedInstanceState) {
    super.onRestoreInstanceState(savedInstanceState);
    etTitle.setText(savedInstanceState.getString(KEY_TITLE, ""));
    etBudget.setText(savedInstanceState.getString(KEY_BUDGET, ""));
    sbDuration.setProgress(savedInstanceState.getInt(KEY_DURATION, 0));
    rbRating.setRating(savedInstanceState.getFloat(KEY_RATING, 0f));
    releaseCal.setTimeInMillis(
            savedInstanceState.getLong(KEY_RELEASE, System.currentTimeMillis()));
    etRelease.setText(savedInstanceState.getString(KEY_RELEASE_TEXT, ""));
}
```

```java
// MainActivity — the Bundle version, if you want the list to survive rotation
private static final String KEY_MOVIES = "key_movies";

@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putSerializable(KEY_MOVIES, new ArrayList<>(movies));
}
```

```java
// MainActivity.onCreate() — the restoration, before the adapter is created
if (savedInstanceState != null) {
    ArrayList<?> saved = savedInstanceState.getSerializable(KEY_MOVIES, ArrayList.class);
    if (saved != null) {
        for (Object item : saved) {
            if (item instanceof Movie) {
                movies.add((Movie) item);
            }
        }
    }
}
if (movies.isEmpty()) {
    addSampleMovies();
}
```

**Why:** on rotation, the activity is destroyed and recreated. What happens to each thing:

| What | Survives? | Why |
|---|---|---|
| `etTitle`, `etRelease`, `etBudget`, `etPoster` | yes | `EditText.getFreezesText()` returns `true`, so the text goes into the `SavedState` |
| `sbDuration`, `rbRating` | yes | `ProgressBar.onSaveInstanceState()` saves `progress` |
| `swWatched`, `cbonWatchList`, each `RadioButton` | yes | `CompoundButton` saves the check state |
| `spGenre` | yes | `AbsSpinner` saves the selected position |
| `tvDurationValue`, `tvWatchedValue` | apparently yes | `TextView` does **not** save its text (`freezesText` is `false`), but the listeners recalculate it: `setProgress` and `setChecked` call them on restore |
| `releaseCal` | **no** | it is a field of the activity, reinitialized with `Calendar.getInstance()` |
| `position` | yes | it is re-read from the `Intent`, and the system re-delivers the same `Intent` |
| `movies` (MainActivity) | **no** | a field of the activity, recreated empty; `ListView` saves only the scroll position |

Two ordering details, both essential:

- **`onRestoreInstanceState` runs after `onStart`**, so after `fillForm(existing)` from `onCreate`. Your restoration wins over the model. If you restored at the beginning of `onCreate`, `fillForm` would overwrite your values.
- **The framework's restoration also runs after `onCreate`**, in `Activity.onRestoreInstanceState` → `mWindow.restoreHierarchyState(...)`. That is why, in edit mode, after rotation the form shows what you typed, not what is in the model — the desired behaviour.

The real loss is `releaseCal`. The text in `etRelease` survives (it's an `EditText`), but `saveMovie()` reads `releaseCal.getTime()` (line 171), not the field's text. So after rotation you press Update and save **today's date**, while the screen shows the old date. It doesn't crash, it doesn't warn — it just lies. The line that matters in the whole exercise is `outState.putLong(KEY_RELEASE, ...)`.

Why the list in `MainActivity` behaves differently: there is no `View` to hold it. `ListView` saves in `AbsListView.SavedState` only positions and selections (`selectedId`, `firstId`, `position`, `viewTop`, `checkState`) — **never data**. `ArrayAdapter` is not a `View`, so it is not in the hierarchy. And `movies` is `final` and initialized inline: every new instance of `MainActivity` gets a new `ArrayList`, and `addSampleMovies()` fills it with exactly the three demos. The movie you added doesn't "disappear" — it was never anywhere other than the old activity's heap. The movie you added doesn't "disappear" — it was never anywhere other than the old activity's heap.

**Remember:** `android:configChanges="orientation|screenSize"` is **not** the solution. It hides the problem on rotation, but not on process death or with "Don't keep activities" (Developer options), and on top of that you skip the resource reload — the landscape layout would never apply again.

A `Bundle` has a practical limit of ~1 MB (`TransactionTooLargeException`). Three to six movies are nothing; a list of thousands of objects or a bitmap has no business being there. For large lists, use a `ViewModel` (survives rotation, but not process death) or the disk (24.6).

**Where it applies:** any activity field that is not a `View` and doesn't come from an `Intent` — `releaseCal`, a search filter, a page index, an object being edited. And any list that must look the same after rotation: `Bundle` for small lists, `ViewModel` for medium ones, disk for everything that must stay.

</details>

---

## Exercise 24.6 — Real persistence: the list is lost when the app closes. `SharedPreferences` + hand-built JSON

**Requirement:** Add a movie, close the app from Recents (swipe), reopen it. The movie is gone. Explain why, then save the list into `SharedPreferences` as JSON — **hand-built**, with `StringBuilder`, no Gson, no Moshi, no new dependency in `build.gradle.kts`. On startup, the list is loaded from the preferences; if it is empty (first run), the three demos are added and written to disk.

**Files touched:** `MainActivity.java` — `onCreate()` (lines 53–55), `onPause()`, five new methods (`saveMovies`, `loadMovies`, `moviesToJson`, `moviesFromJson`, `escape`) and six imports.

**How you approach it — your steps:**
1. Run the app, add "Dune", close it from Recents, reopen it. The list has 3 rows. Confirm the symptom before you write code.
2. In `MainActivity`, replace the `addSampleMovies();` call (line 53) with the load from preferences plus a "seed" on the first run.
3. Write `moviesToJson()` with `StringBuilder`. For each movie, an object with the 10 fields. Don't forget `escape()` for the strings — otherwise a title with quotation marks breaks the whole file.
4. Write `moviesFromJson()` with `JSONArray` / `JSONObject` from `org.json` (they come with Android, they are not external libraries) and handle `JSONException`.
5. Call `saveMovies()` in `onPause()`. Check on disk with `adb`.
6. Test with a title that contains quotation marks and with one that contains diacritics.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

`movies` is `final`, so `movies = loadMovies();` does **not** compile. Use `movies.addAll(loadMovies());` or `movies.clear(); movies.addAll(...);`. The adapter holds the reference to the list, not to the content — that is why you never reassign, you only modify.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

`new JSONArray(json)` throws `JSONException` if the string is invalid. Catch it and start with an empty list — the app repairs itself on the next run. To read the fields use `optString` / `optInt` / `optDouble` / `optBoolean`, which return a default value instead of throwing.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the list was serialized manually into JSON and written to `SharedPreferences` on every `onPause`, then reloaded in `onCreate`, with the demos seeded only on the first run.

**Code:**

```java
// MainActivity — new fields, next to POSITION_EXTRA / MOVIE_EXTRA
private static final String PREFS_NAME = "g1097_movies";
private static final String KEY_MOVIES_JSON = "movies_json";
```

```java
// MainActivity.onCreate() — replaces addSampleMovies() from line 53
movies.addAll(loadMovies());
if (movies.isEmpty()) {
    addSampleMovies();
    saveMovies();               // first run: the demos reach the disk
}

movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
initControls();
initListeners();
```

```java
// MainActivity — writing and reading
@Override
protected void onPause() {
    super.onPause();
    saveMovies();               // every exit from the screen writes the list
}

private boolean saveMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = moviesToJson();
    boolean ok = prefs.edit().putString(KEY_MOVIES_JSON, json).commit();
    Log.d("G1097", "saveMovies: " + movies.size() + " filme, "
            + json.length() + " caractere, ok=" + ok);
    return ok;
}

private List<Movie> loadMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = prefs.getString(KEY_MOVIES_JSON, null);
    List<Movie> loaded = moviesFromJson(json);
    Log.d("G1097", "loadMovies: " + loaded.size() + " filme din " + PREFS_NAME);
    return loaded;
}
```

```java
// hand-built JSON — no Gson, no Moshi
private String moviesToJson() {
    StringBuilder sb = new StringBuilder("[");
    for (int i = 0; i < movies.size(); i++) {
        Movie m = movies.get(i);
        if (i > 0) sb.append(',');
        sb.append('{')
          .append("\"title\":\"").append(escape(m.getTitle())).append("\",")
          .append("\"release\":").append(m.getRelease() == null ? 0L : m.getRelease().getTime()).append(',')
          .append("\"genre\":\"").append(escape(m.getGenre())).append("\",")
          .append("\"budget\":").append(BigDecimal.valueOf(m.getBudget()).toPlainString()).append(',')
          .append("\"duration\":").append(m.getDuration()).append(',')
          .append("\"rating\":").append(m.getRating()).append(',')
          .append("\"watched\":").append(m.isWatched()).append(',')
          .append("\"approval\":\"").append(escape(m.getApproval())).append("\",")
          .append("\"onWatchlist\":").append(m.isOnWatchlist()).append(',')
          .append("\"poster\":\"").append(escape(m.getPoster())).append("\"")
          .append('}');
    }
    return sb.append(']').toString();
}

private static String escape(String value) {
    if (value == null) return "";
    return value.replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t");
}
```

```java
// reading — org.json comes with Android, it is not an external library
private List<Movie> moviesFromJson(String json) {
    List<Movie> result = new ArrayList<>();
    if (json == null || json.isEmpty()) return result;
    try {
        JSONArray array = new JSONArray(json);
        for (int i = 0; i < array.length(); i++) {
            JSONObject o = array.getJSONObject(i);
            Movie m = new Movie();
            m.setTitle(o.optString("title", ""));
            m.setRelease(new Date(o.optLong("release", 0L)));
            m.setGenre(o.optString("genre", ""));
            m.setBudget(o.optDouble("budget", 0));
            m.setDuration(o.optInt("duration", 0));
            m.setRating((float) o.optDouble("rating", 0));
            m.setWatched(o.optBoolean("watched", false));
            m.setApproval(o.optString("approval", ""));
            m.setOnWatchlist(o.optBoolean("onWatchlist", false));
            m.setPoster(o.optString("poster", ""));
            result.add(m);
        }
    } catch (JSONException e) {
        Log.e("G1097", "JSON invalid — pornesc cu lista goala", e);
    }
    return result;
}
```

```java
// new imports in MainActivity
import android.content.SharedPreferences;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.math.BigDecimal;
```

**Why:** when the app closes, the process dies and with it the whole heap: `movies`, the adapter, the activities. RAM is not persistence. `SharedPreferences` writes an XML file to `/data/data/ro.ase.ie.g1097/shared_prefs/g1097_movies.xml`, which the system keeps until uninstall or "Clear data". On the first read, the whole file is loaded into memory; `edit()` builds a mutable copy, and `commit()` / `apply()` writes it back.

The choice of `SharedPreferences` + JSON over other options:

| Option | When you use it | Cost |
|---|---|---|
| `SharedPreferences` + JSON | small lists, the exam, a prototype | the whole file rewritten on every save; no queries |
| a file in `filesDir` | larger data, export | you handle the reading/writing and the errors yourself |
| `Room` / SQLite | large lists, search, relations | entity, DAO, database, migrations |

Three decisions in the code that are worth explaining:

- **`BigDecimal.valueOf(...).toPlainString()`** instead of `String.valueOf(double)`. Exactly the lesson from the table at the start of the chapter: `String.valueOf(160000000.0)` gives `1.6E8`. JSON accepts scientific notation, so it would reload correctly — but the file becomes unreadable, and if you read it with another tool (or with your eyes) you look like you saved something else. `toPlainString()` writes `160000000`.
- **`commit()` instead of `apply()`.** `commit()` writes synchronously and returns a `boolean` — so you **can verify**. `apply()` writes asynchronously and returns nothing. For six movies, the time difference is negligible; for a large list, use `apply()` in production and `commit()` only in tests.
- **`onPause()`, not `onDestroy()`.** `onDestroy()` is not guaranteed: if the process is killed, it is not called. `onPause()` is called on every exit from the screen. You save a little more often than needed — correct and safe.

**Remember:** `escape()` is mandatory and the order matters: backslash first, then quotation marks. If you reverse them, `\"` becomes `\\"` and the JSON breaks. A title like `He said "hi"` without escaping produces an invalid file, and on startup `new JSONArray(...)` throws — the app starts with an empty list and it looks like "everything was lost".

`release` is saved as a `long` (`Date.getTime()`), not as a string. A `Date` formatted as text depends on the `Locale` and the time zone; a `long` is unambiguous. `0` is the sentinel for "no date" and is turned into `new Date(0)` on read, so that we don't introduce `null` — `fillForm` at `d719ffc` crashes on `release == null` (line 88).

**Where it applies:** any data that must survive the process. At the exam, if the requirement says "the data must be saved" and doesn't say "in a database", `SharedPreferences` + JSON is the fastest answer and the easiest to explain. If the professor explicitly asks for "on app restart", this is the demonstration: you close from Recents, reopen, the movie is there.

**Verification on the emulator:**

1. Add "Dune", close from Recents, reopen → "Dune" is in the list, and the demos weren't duplicated.
2. The file on disk:
   ```
   adb shell run-as ro.ase.ie.g1097 cat shared_prefs/g1097_movies.xml
   ```
   You must see `&quot;title&quot;` and the rest of the fields. `run-as` only works on a `debug` build (the default in Android Studio).
3. Add a movie with the title `He said "hi"` → restart → the title is intact, and in the XML the sequence appears as `\&quot;hi\&quot;` (`FastXmlSerializer` escapes the quotation marks as `&quot;` even in text).
4. Reset: `adb shell pm clear ro.ase.ie.g1097` (or Settings → Apps → Storage → Clear data) → on the next startup the three demos are back.

</details>

---

## Exercise 24.7 — The checklist after every "add an attribute": 6 checks

**Requirement:** Add a new attribute to the movie (choose `writer`, String, or `language`, String) and go through **six** checks that prove the attribute is saved **and** reloaded correctly. Write the checklist as a procedure you repeat for every attribute, not as a story about this attribute.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java` (and `movie_item.xml` + adapter, if you display the attribute in the row).

**How you approach it — your steps:**
1. Do the classic chain from chapter 17: field + getter/setter + `toString()` + constructor in `Movie`, control in XML, `findViewById`, `fillForm`, `saveMovie`. Compile.
2. Go through checks 1–6 below, in order, noting the result of each. Don't skip any "because it's visible".
3. For every check that fails, note the layer: model, form, activity, list or disk. Almost always an attribute "that doesn't save" is in fact an attribute that saves but doesn't **reload** — something missing from `fillForm`.
4. Run the checklist again after you fix it. A checklist that isn't run twice isn't a checklist, it's an attempt.
5. Final check: add a movie with the attribute filled in, close the app, reopen, open the movie in edit. The value must be there, in the list and in the form.

<details markdown="1">
<summary>Hint 1 — if you get stuck at check 3</summary>

put a `Toast` with `movie.toString()` in `saveMovie()`, right before `setResult`. If the attribute appears there, `saveMovie` is correct and the problem is further on. If it shows `null` or `0`, the problem is in reading from the widget.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at check 6</summary>

if you did 24.6, the JSON has exactly 10 hand-written fields. A new attribute isn't saved to disk until you add both the line in `moviesToJson()` **and** the line in `moviesFromJson()`. It is the most common place where an attribute "disappears on restart".

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** "add an attribute" was turned into a six-step verifiable procedure, each step with a clear symptom if it is skipped.

**Code:** the checklist itself, with what you check, how you check it, and what you see if you skipped the step.

| # | Check | How | If it's missing |
|---|---|---|---|
| 1 | **The model** has the field, getter, setter, `toString()` and it's in the constructor | it compiles; `movie.toString()` contains the attribute | compile errors in `addSampleMovies()`, if you changed the constructor |
| 2 | **The form** has the control in XML, with an `android:id`, wired through `findViewById` | open the screen; it doesn't crash | `NullPointerException` in `onCreate`, or the field isn't on the screen |
| 3 | **`saveMovie()`** writes the attribute into `Movie` | a `Toast` with `movie.toString()` before `setResult` | the value stays at its default (`null`, `0`, `false`) |
| 4 | **`fillForm()`** reads the attribute from `Movie` | open the movie in edit | the field is empty, even though the value shows in the list |
| 5 | **The list** displays the attribute | look at the row; if you use an adapter, at its `TextView` too | saved, but invisible — the least serious |
| 6 | **Survival**: rotation + restart | rotate in the form; close from Recents and reopen | the value is lost on rotation (`onSaveInstanceState`) or on restart (the JSON from 24.6) |

```java
// check 3 — the Toast that proves what leaves towards the list
Log.d("G1097", "saveMovie: " + movie.toString());
Toast.makeText(this, movie.getTitle() + " / " + movie.getWriter(),
        Toast.LENGTH_SHORT).show();
```

```java
// check 4 — the line that is most often missing from fillForm()
etWriter.setText(existing.getWriter() == null ? "" : existing.getWriter());
```

```java
// check 6 — the two lines from the persistence in 24.6
sb.append("\"writer\":\"").append(escape(m.getWriter())).append("\",");  // moviesToJson
m.setWriter(o.optString("writer", ""));                                 // moviesFromJson
```

**Why:** the chain has six layers and each has its own way of failing silently:

```
Movie  →  XML  →  findViewById  →  saveMovie  →  fillForm  →  list  →  disk
  1        2          2                3             4          5        6
```

An attribute can be correct in five layers and wrong in the sixth. The symptoms are different and they send you straight to the layer:

- **It shows in the list, but not in the form** → `fillForm` is missing (check 4). The list reads `toString()`, the form reads `fillForm`.
- **It shows in the form, but not in the list** → `toString()` or the adapter is missing (check 5).
- **It shows everywhere, but disappears on restart** → it's missing from the JSON (check 6).
- **It shows everywhere, but disappears on rotation** → it's missing from `onSaveInstanceState` (check 6, first part).
- **It's `null` in `saveMovie`** → the read from the widget is missing (check 3).

The order of the checks is not accidental: from the model towards the disk, from the cheapest to fix to the most expensive. A compile error at step 1 makes checks 2–6 pointless.

**Remember:** check 6 is the one Bank 6 adds on top of the chain from chapter 17. Without it, your attribute lives as long as the process lives — exactly like the whole list at `d719ffc`. At the exam, if you have time for only one extra check, do this one: rotation and restart are the only ones that catch the hidden `releaseCal`.

**Where it applies:** any new attribute, whatever its type. For a `Date`, check 4 has an extra trap: `fillForm` must format with `dateFormat` and must not receive `null` (otherwise an NPE, line 88). For a `double`, check 4 must use `BigDecimal.toPlainString()`, not `String.valueOf` (otherwise `1.6E8`). The checklist stays the same; only the code in each box changes.

</details>

---

## Exercise 24.8 — Debug: the movie saves, but it doesn't show up in the list. 5 causes, 5 checks

**Requirement:** You added a movie, pressed Save, but nothing shows up in the list. List **five** possible causes, in the order you check them, and for each say what tool you use (Logcat, breakpoint, `Toast`) and what exactly makes you rule it out. Don't guess — triage.

**Files touched:** `MainActivity.java` (the callback, `showCount`), `ItemActivity.java` (`saveMovie`). Diagnostics only; the code stays unchanged at the end.

**How you approach it — your steps:**
1. Reproduce the bug on purpose: comment out `notifyDataSetChanged()` in the add branch. Run, add a movie. Confirm the symptom.
2. Put a `Toast` in `saveMovie()`, right before `setResult`, with `movie.getTitle()`. If it appears, the save ran; if not, the exception is before it.
3. Put a `Toast` in the callback, before the `if`, with `o.getResultCode()`, `o.getData() != null` and `position`. That way you learn whether the result arrived and which branch you enter.
4. Put a breakpoint on the `movies.add(movie)` line and run in debug. Inspect `movies.size()` before and after, then `movieAdapter.getCount()` and `listView.getCount()`.
5. Go through the triage table below and note, for each cause, what value you got.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

a `Toast` that doesn't appear doesn't necessarily mean the method didn't run — it can mean the activity crashed before it. Check Logcat for `FATAL EXCEPTION` before you draw a conclusion.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

the breakpoint goes on the line in the callback, not in `ItemActivity`. There you see `movies`, `movie` and `position` at the same time — exactly the three variables that decide what happens.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a five-branch triage was built, each with a distinct signature in the three values (`movies.size()`, `adapter.getCount()`, `listView.getCount()`) and with the right tool.

**Code:** the diagnostic tools, in the order you add them.

```java
// 1. in ItemActivity.saveMovie(), before setResult
Log.d("G1097", "saveMovie: " + movie);

// 2. in MainActivity, in the callback, before the if
Log.d("G1097", "result: code=" + o.getResultCode()
        + " data=" + (o.getData() != null)
        + " position=" + (o.getData() == null ? "?" : o.getData().getIntExtra(POSITION_EXTRA, -1)));

// 3. after each branch
Log.d("G1097", "dupa: movies=" + movies.size()
        + " adapter=" + movieAdapter.getCount()
        + " listView=" + listView.getCount());
```

```bash
# filtering Logcat on our tag
adb logcat -s G1097:D
```

**Why:** the five causes, with their signature:

| # | Cause | Signature | How you confirm | The fix |
|---|---|---|---|---|
| 1 | `notifyDataSetChanged()` is missing | `movies=4`, `adapter=4`, `listView=3` | the log from step 3 | add the line (24.1) |
| 2 | the result doesn't arrive: `setResult` not called, wrong code, or an exception before it | the `Toast` in `saveMovie` doesn't appear, or `code=0` | a `Toast` in `saveMovie` + a log in the callback | check the `setResult` → `finish()` order; catch the exception (empty budget — see 24.10) |
| 3 | the wrong branch: `position != -1` on add | `movies=3`, but a title changed | a log with `position` in the callback | `position` is put into the `Intent` only on edit (24.9) |
| 4 | the adapter looks at another list | `movies=4`, `adapter=3` | the log from step 3 | a single `ArrayList`, a single reference; you don't reassign `movies` |
| 5 | the row exists, but it isn't visible | `movies=adapter=listView=4`, but the row isn't on screen | `listView.getLastVisiblePosition()`; `movies.get(size-1).toString()` | empty title, scrolled list, or a `toString()` without the attribute |

Cause 2 deserves emphasis, because it is the only one that leaves no trace in the list: if `saveMovie()` throws before `setResult` — and at `d719ffc` it does on an empty budget (`Double.parseDouble("")`, line 173) — the activity crashes, `MainActivity` comes back on screen with the list untouched, and it looks like "Save does nothing". Logcat has the `FATAL EXCEPTION` and the full stack; that is the first thing you read, not the last.

Cause 3 is the one that fools you most often: the list **did change**, it just doesn't grow. A `position` left over from a previous edit (or sent wrongly as `0`) makes `movies.set(0, movie)` and overwrites the first movie. The distinguishing sign: `movies.size()` stays constant, but the content at one index changes.

Cause 5 is the only one where the data is correct and the visual lies. Three variants: the title is `""` (the row has height, but it is empty), the list is scrolled and the new row is below the bottom edge (`ListView` doesn't scroll automatically on add), or `toString()` doesn't contain the attribute you're looking for.

The triage order, from cheap to expensive: **Logcat → `Toast` → breakpoint**. Logcat is free and tells you whether it crashed; the `Toast` tells you whether the method ran; the breakpoint shows you the exact state. Don't start with the breakpoint — you lose ten minutes to find out what the log already said.

**Remember:** the three numbers (`movies`, `adapter`, `listView`) are a complete triage in two seconds. Each combination points to a different cause:

- `movies == adapter > listView` → missing notification (cause 1).
- `movies > adapter` → two lists / two adapters (cause 4).
- `movies == adapter == listView` but the row isn't visible → cause 5.
- `movies` doesn't grow at all → causes 2 or 3.

**Where it applies:** any "it saved, but it isn't visible". In `RecyclerView` the triage is identical, only the third number becomes `adapter.getItemCount()` after `notifyItemInserted`. In a database, the first number becomes the result of a `SELECT COUNT(*)`.

</details>

---

## Exercise 24.9 — Debug: after an edit, the movie shows up twice. `add` vs. `set`

**Requirement:** You edit "The Matrix" and, after Update, two "The Matrix" rows appear in the list: the old one and the new one. Explain why, show the line that produces the duplicate, fix it — and say what you do if you already used `set` in the wrong place, so that a movie was overwritten.

**Files touched:** `MainActivity.java` — the callback (lines 63–77), plus optionally a cleanup method.

**How you approach it — your steps:**
1. Reproduce: in the callback, replace `movies.set(position, movie);` with `movies.add(movie);`. Edit "The Matrix" and change the rating.
2. Look at the list: 4 rows, two with "The Matrix". The first is the old one, the last is the new one. The number grew — so it is not a display problem, it is a data problem.
3. Open the first "The Matrix" again: it has the old values. The second: the new values. Confirm that they are two distinct objects.
4. Put `set` back and confirm that the list returns to 3 rows, with the new values at the right position.
5. Experiment the other way round too: in the add branch, replace `movies.add(movie);` with `movies.set(0, movie);`. Add a movie. The list still has 3 rows, and "Inception" is gone. This is the other symptom of the same confusion.
6. Write `removeDuplicates()` and run it on the list already corrupted at step 2.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 5</summary>

`set(0, movie)` doesn't throw any exception — index 0 is valid. It simply replaces the first element. That is why the bug is dangerous: it doesn't report itself, it just loses data.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

`Movie` doesn't have `equals` and `hashCode`, so `movies.remove(movie)` compares by identity and will never find the "same" movie. Either you deduplicate manually, by title + date, or you add `equals`/`hashCode` to `Movie` — the second option is the correct one.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the `add`/`set` confusion was identified in both its forms, the correct branch was fixed, and a cleanup was written for the data already corrupted.

**Code:**

```java
// WRONG — duplicate: the original stays at position, the copy is added at the end
else {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
}

// CORRECT — replacement in place, the size doesn't change
else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

```java
// cleaning up an already corrupted list — O(n²), enough for the exam
private void removeDuplicates() {
    for (int i = movies.size() - 1; i >= 0; i--) {
        for (int j = 0; j < i; j++) {
            if (sameMovie(movies.get(i), movies.get(j))) {
                movies.remove(i);
                break;
            }
        }
    }
    movieAdapter.notifyDataSetChanged();
}

private boolean sameMovie(Movie a, Movie b) {
    if (a.getTitle() == null || b.getTitle() == null) return false;
    if (!a.getTitle().equals(b.getTitle())) return false;
    if (a.getRelease() == null || b.getRelease() == null) return false;
    return a.getRelease().getTime() == b.getRelease().getTime();
}
```

```java
// the correct version, long term — in Movie.java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Movie)) return false;
    Movie other = (Movie) o;
    return Objects.equals(title, other.title)
            && Objects.equals(release, other.release);
}

@Override
public int hashCode() {
    return Objects.hash(title, release);
}
```

```java
// new import in Movie.java
import java.util.Objects;
```

**Why:** `add` and `set` answer two different questions:

| Method | The question | Effect | Size |
|---|---|---|---|
| `add(element)` | "add a new movie" | inserts at the end | +1 |
| `set(index, element)` | "replace the movie at the index" | replaces, the rest stay | unchanged |

An edit is the second question. The button is called "Update Movie", `position` comes from the `Intent`, and the user modified an existing movie — he didn't create one. `add` is the answer to a different question.

Why the duplicate ends up in the list and doesn't resolve itself: `movies` is a plain list, with no uniqueness constraints. Nothing prevents two objects with the same title. `ArrayAdapter` displays both, because for it they are two elements.

**The second form of the same confusion:** `set` used on add. If `position` isn't `-1` when you add (for example you sent `POSITION_EXTRA` as `0`, or you forgot to take it out of a reused `Intent`), `movies.set(position, movie)` **overwrites** the movie at that index. The list doesn't grow, no error appears, but a movie is gone. The fix cannot be done from code — the old movie no longer exists in memory. What you can do:

1. **Stop the loss:** `position` is put into the `Intent` **only** in edit mode (`if (position != -1)`), exactly as on line 190 of `ItemActivity`.
2. **Validate the index** before `set`: `if (position >= 0 && position < movies.size())`.
3. **Rebuild the lost data** manually (re-enter the movie) or start over from the demos with "Clear data" — if you have persistence (24.6), delete the preferences file too.

**Remember:** `Movie` doesn't have `equals`/`hashCode` at `d719ffc`, so `List.remove(Object)`, `List.contains(...)` and `Set<Movie>` behave on identity, not on content. Two movies with the same title are "different" for collections. If you add `equals`/`hashCode`, `removeDuplicates()` simplifies to:

```java
Set<Movie> unique = new LinkedHashSet<>(movies);
movies.clear();          // movies is final — it cannot be reassigned
movies.addAll(unique);
movieAdapter.notifyDataSetChanged();
```

**Where it applies:** any editable list. In `RecyclerView`, the equivalents are `notifyItemInserted` (add) and `notifyItemChanged` (set) — the same confusion, another API. In a database, `INSERT` vs. `UPDATE ... WHERE id = ?`; there the database saves you partially, because an `INSERT` without a duplicate primary key is rejected.

</details>

---

## Exercise 24.10 — The exam: "the data must be saved"

**Requirement:** The exam requirement has two parts: **(a)** on Save, the movie appears in the list with the right values; **(b)** on edit, the list updates in place, with no duplicates. Implement both, then demonstrate them with a timed six-step scenario in which every step has an expected result. Include the guards that keep requirement (a) from failing on an empty budget or a missing date.

**Files touched:** `MainActivity.java` — the callback; `ItemActivity.java` — `saveMovie()` and `fillForm()`.

**How you approach it — your steps:**
1. Write the acceptance scenario first (the table below), with the exact values you will enter. Don't improvise during the demonstration.
2. Fix the three real defects: empty budget (`NumberFormatException`), `release` null (`NullPointerException`), budget shown as `1.6E8`.
3. Add the `Intent` guard in the callback: `o.getData() != null` and a valid `position`.
4. Run the scenario once, timed. Note where you lose time.
5. Run again, with "Don't keep activities" enabled (Developer options) — the simulation of activity death. Then close from Recents and reopen, if you did 24.6.
6. Final check: every row in the table passes, and `hasDuplicateTitles()` returns `false` at the end.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

`Double.parseDouble("")` throws `NumberFormatException`, and `dateFormat.format(null)` throws `NullPointerException` in `calendar.setTime(null)`. Both are before `setResult`, so the app crashes and the parent receives nothing. They are not "improvements" — they are conditions for requirement (a) to be demonstrable.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 3</summary>

`o.getData()` can be `null` even with `RESULT_OK` (if someone called `setResult(RESULT_OK)` without an `Intent`). And `position` can be any integer — an `Intent` is not a typed contract. Both guards are two lines.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the three real defects were fixed, the result and index guards were added, and the acceptance scenario that demonstrates (a) and (b) in under five minutes was written.

**Code:**

```java
// ItemActivity.saveMovie() — the version with validation
private void saveMovie() {
    String title = etTitle.getText().toString().trim();
    if (title.isEmpty()) {
        etTitle.setError("Title is required");
        etTitle.requestFocus();
        return;
    }

    String budgetText = etBudget.getText().toString().trim().replace(',', '.');
    if (budgetText.isEmpty()) {
        etBudget.setError("Budget is required");
        etBudget.requestFocus();
        return;
    }
    double budget;
    try {
        budget = Double.parseDouble(budgetText);
    } catch (NumberFormatException e) {
        etBudget.setError("Not a valid number");
        etBudget.requestFocus();
        return;
    }

    Movie movie = new Movie();
    movie.setTitle(title);
    movie.setRelease(releaseCal.getTime());
    movie.setGenre(spGenre.getSelectedItem().toString());
    movie.setBudget(budget);
    movie.setDuration(sbDuration.getProgress());
    movie.setRating(rbRating.getRating());
    movie.setWatched(swWatched.isChecked());
    movie.setOnWatchlist(cbonWatchList.isChecked());
    movie.setPoster(etPoster.getText().toString());
    for (int index = 0; index < rgApproval.getChildCount(); index++) {
        RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
        if (rb.isChecked()) {
            movie.setApproval(rb.getText().toString());
            break;
        }
    }

    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
    if (position != -1)
        intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_OK, intent);
    finish();
}
```

```java
// ItemActivity.fillForm() — the two fixed lines
// new import in ItemActivity: java.math.BigDecimal
etRelease.setText(existing.getRelease() == null
        ? ""
        : dateFormat.format(existing.getRelease()));
etBudget.setText(BigDecimal.valueOf(existing.getBudget()).toPlainString());
```

```java
// MainActivity — the final callback, with all the guards
if (o.getResultCode() == RESULT_OK && o.getData() != null) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);

    if (movie == null) {
        Log.e("G1097", "rezultat OK, dar fara Movie in Intent");
        return;
    }
    if (position == -1) {
        movies.add(movie);
    } else if (position >= 0 && position < movies.size()) {
        movies.set(position, movie);
    } else {
        Log.e("G1097", "position invalid: " + position + ", size=" + movies.size());
        return;
    }
    movieAdapter.notifyDataSetChanged();
    showCount(position == -1 ? "dupa adaugare" : "dupa editare");  // showCount comes from 24.4
}
```

**Why:** requirement (a) has three conditions, all necessary: the form produces a complete `Movie` (validation), the result reaches the parent (`RESULT_OK` + `Intent`), and the parent adds it and notifies. Requirement (b) has two: the right branch (`set`, not `add`) and a valid index.

The acceptance scenario — you run it exactly like this, with these values:

| Step | Action | Expected result | What it demonstrates |
|---|---|---|---|
| 0 | startup | 3 rows | the initial state |
| 1 | add "Dune", budget `165000000`, date `01/10/2021` | 4 rows, "Dune" with the values entered | (a) |
| 2 | tap "Dune", change the title to "Dune: Part One", Update | 4 rows, the new title, **without** a second "Dune" | (b) |
| 3 | tap "Inception", Update without any change | 4 rows, "Inception" unchanged | (b) — `set` with the same value breaks nothing |
| 4 | add "Alien" with an **empty** budget | the error appears on the field, the app does **not** crash, the list stays at 4 | (a) — the guard |
| 5 | fill in "Alien"'s budget with `100000000` and save | 5 rows | (a) |
| 6 | close from Recents, reopen | still 5 rows (the 3 demos + Dune + Alien) | persistence (24.6) |

The table is also the answer to the question "how do you verify?". Every row has an observable result on screen, not an impression.

The three fixed defects, and why each one matters for (a):

- **Empty budget** → `NumberFormatException` in `saveMovie`, before `setResult`. The app crashes, the parent receives nothing, the user sees the list untouched. Without the guard, requirement (a) cannot be demonstrated with an incomplete form — and at the exam the form is almost always incomplete on the first Save.
- **`release` null** → `NullPointerException` in `fillForm`, at `dateFormat.format(null)` (line 88). It doesn't happen at `d719ffc` with the demo data, but it does happen with a `Movie` built by hand or loaded from JSON without a date. A three-line guard.
- **`1.6E8`** → it doesn't crash, but it looks like a bug and makes you think the value got corrupted. `BigDecimal.valueOf(...).toPlainString()` writes `160000000`. Bonus: `Double.parseDouble("160000000")` works, so the round trip is correct.

**Remember:** the order in `saveMovie()` is the contract: validate → build the `Movie` → `setResult` → `finish()`. Any `return` before `setResult` means "nothing happened", and that is exactly the desired behaviour for an invalid form. Any `setResult` before validation means you send an incomplete movie.

`position` is the only variable that decides between (a) and (b). Default `-1` in `getIntExtra`, put into the `Intent` only on edit, validated before `set`. Three rules, three lines.

**Where it applies:** any "save" requirement at the exam. Whatever the entity — movie, student, product, grade — the chain is the same: validated form → new `Movie`/`Student`/`Product` → `setResult` → a parent that does `add` or `set` → `notify`. Only the field names change.

</details>

---

## Recap — what you check at the test

| The exam requirement | The mechanism | Exercise |
|---|---|---|
| "you add a movie and it shows up in the list" | `notifyDataSetChanged()` after every mutation | 24.1 |
| "you edit and the list shows the new values" | `movies.set(position, movie)` | 24.2 |
| "you press Back and nothing changes" | `setResult` only on Save + the `RESULT_OK` guard | 24.3 |
| "show how many movies there are" | `movies.size()` in a `Toast` / `TextView` | 24.4 |
| "rotation doesn't lose the data" | `onSaveInstanceState` + the fields that aren't `View`s | 24.5 |
| "the data stays after a restart" | `SharedPreferences` + hand-built JSON | 24.6 |
| "add an attribute" | a checklist of 6 checks | 24.7 |
| "it saves, but it doesn't show up" | triage on three numbers: `movies` / `adapter` / `listView` | 24.8 |
| "it shows up twice" | `add` vs. `set` | 24.9 |
| "the data must be saved" | (a) + (b), with validation and a validated index | 24.10 |

Three sentences to memorise:

1. **The adapter doesn't watch the list; you notify it.** `movies.add(...)` moves the data, `notifyDataSetChanged()` makes it visible. Without the second, the first is invisible.
2. **Editing means `set`, adding means `add`.** The same confusion produces either a duplicate or a lost movie — and neither throws an exception.
3. **RAM is not persistence.** An `ArrayList` lives as long as the process; rotation loses the list, a restart loses everything. `onSaveInstanceState` holds the form, `SharedPreferences` holds the list.
