# Chapter 09 — Edit mode

**Objective:** `ItemActivity` receives an existing `Movie`, fills the form with its values, and on Save sends back the modified movie + position. `MainActivity` replaces it in the list.

**Estimated time:** 30–45 min.

**Final file:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — the complete version, with `fillForm` and the block from `onCreate`.

---

## Step 9.1 — Reading the `Intent` in `onCreate`

### Why

`ItemActivity` needs to know **why** it was opened:

- from the FAB → `Intent` without extras → insert mode;
- from a list click → `Intent` with `Movie` + `position` → edit mode.

### How

Add in `onCreate`, **after** `initListeners()`:

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

### Why `existing != null` is the correct test

Don't test `intent.hasExtra(MOVIE_EXTRA)` — although it would work. You test the **result** of the read:

- if the extra is missing → `null`;
- if the extra exists but is of another type → `null` (or an exception);
- if the extra exists and is a `Movie` → the object.

So `existing != null` is more robust.

### Why `setTitle("Edit movie")`

It changes the window title (in recents, in the top bar if there were one). It's visual feedback that you're in edit mode.

> **Note:** `setTitle` on an `Activity` sets the **window** title, not a `TextView`'s. With the `NoActionBar` theme you see nothing on screen — only in recents.

### Why `btMovieAction.setText("Update Movie")`

The button says "Save Movie" in insert mode and "Update Movie" in edit mode. Change the text and you change the user's expectation.

### Exercise 9.1

**Requirement:** also add a color change: in edit mode the button turns orange. How?

<details>
<summary>Hint</summary>

`MaterialButton` has `setBackgroundTintList(ColorStateList)`. Or you can use `setBackgroundColor`.

</details>

<details>
<summary>Solution — explanatory</summary>

**What was done:** we added inside the `if (existing != null)` block:

```java
btMovieAction.setBackgroundTintList(
        android.content.res.ColorStateList.valueOf(
                android.graphics.Color.parseColor("#FF9800")));
```

**What you see:** in edit mode the button turns orange.

**Why `setBackgroundTintList` and not `setBackgroundColor`:** `MaterialButton` uses a `MaterialShapeDrawable` as its background. `setBackgroundColor` would replace it and you'd lose the rounded corners + ripple. `setBackgroundTintList` **tints** the existing background.

**Remember:**
1. `MaterialButton` has special APIs: `setBackgroundTintList`, `setIconTint`, `setStrokeColor`.
2. `ColorStateList.valueOf(color)` creates a list with a single color for all states.
3. For theme colors: `MaterialColors.getColor(btMovieAction, com.google.android.material.R.attr.colorPrimary)`.

**Where it comes back:** it doesn't come back, but it's a useful technique for visually telling states apart.

</details>

---

## Step 9.2 — `fillForm`: filling the form

### Why

You have an existing `Movie`. You need to put each value into the corresponding widget. It's the inverse of `saveMovie`.

### How

```java
private void fillForm(Movie existing) {
    etTitle.setText(existing.getTitle());
    etRelease.setText(dateFormat.format(existing.getRelease()));
    etBudget.setText(String.valueOf(existing.getBudget()));
    sbDuration.setProgress(existing.getDuration());
    cbonWatchList.setChecked(existing.isOnWatchlist());
    swWatched.setChecked(existing.isWatched());
    rbRating.setRating(existing.getRating());
    etPoster.setText(existing.getPoster());
    for (int index = 0; index < spGenre.getCount(); index++) {
        if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
            spGenre.setSelection(index);
            break;
        }
    }
    for (int index = 0; index < rgApproval.getChildCount(); index++) {
        RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
        if (rb.getText().toString().equals(existing.getApproval())) {
            rgApproval.check(rgApproval.getChildAt(index).getId());
            break;
        }
    }
}
```

### Reverse mapping

| Model field | Widget | Write method |
|---|---|---|
| `title` | `etTitle` | `setText(String)` |
| `release` | `etRelease` | `setText(dateFormat.format(Date))` |
| `genre` | `spGenre` | `setSelection(index)` — **look up the index** |
| `budget` | `etBudget` | `setText(String.valueOf(double))` |
| `duration` | `sbDuration` | `setProgress(int)` |
| `rating` | `rbRating` | `setRating(float)` |
| `watched` | `swWatched` | `setChecked(boolean)` |
| `onWatchlist` | `cbonWatchList` | `setChecked(boolean)` |
| `poster` | `etPoster` | `setText(String)` |
| `approval` | `rgApproval` | `check(id)` — **look up the radio button** |

### Why `String.valueOf(existing.getBudget())`

`EditText.setText` accepts `CharSequence`, not `double`. `String.valueOf(double)` converts.

> **Note:** `String.valueOf(160000000.0)` returns `"1.6E8"`! Not `"160000000"`. You'll see `1.6E8` in the field. It's a **real problem** in the repo.

Check: `Double.toString(160000000.0)` → `"1.6E8"`. Yes.

**The correct solution** would be `String.format(Locale.US, "%.0f", existing.getBudget())` or `new BigDecimal(...).toPlainString()`.

### Why `spGenre.setSelection(index)` and not `setSelection(text)`

`Spinner` **does not have** `setSelectionByText`. It only has `setSelection(int position)`.

So you have to search for the index manually:

```java
for (int index = 0; index < spGenre.getCount(); index++) {
    if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
        spGenre.setSelection(index);
        break;
    }
}
```

`getItemAtPosition(index)` returns `Object` — here a `String`, because `entries` creates an `ArrayAdapter<String>`.

### Why `.equals()` and not `==`

`==` compares **references**. The `String`s from `entries` and the one from `Movie` are different objects, even if they have the same text. `.equals()` compares **content**.

> **This is a classic test mistake:** `==` on `String` compares references, not values.

### Why `rgApproval.check(id)` and not `rb.setChecked(true)`

Both would work. But `rgApproval.check(id)` is the **group** method: it guarantees the other buttons get deselected. `rb.setChecked(true)` could leave two buttons checked if the group isn't in sync.

### Exercise 9.2

**Requirement:** what happens if `existing.getGenre()` is `"Documentary"` and it's not in `movie_genre`? Trace it mentally.

<details>
<summary>Solution — explanatory</summary>

**What was done:** we traced the loop when the genre is not found.

**What happens:** the loop ends without `break`. `spGenre.setSelection(...)` **is not called**. So the spinner stays on the **first** option (`Drama`).

**What you see:** the form shows genre `Drama`, although the movie is `Documentary`. On Save, the movie will get `Drama` — **silently corrupted data**.

**Why:** there's no `else` to signal "the genre doesn't exist". The loop is purely optimistic.

**Remember:**
1. **Search loops without an `else`** can hide invalid data.
2. Solution: after the loop, check whether you found something. If not, add the missing option or set a default value.
3. Here it's a **real risk**: if the teacher adds a new genre in `movie_genre` and the user saves a movie with it, then edits it, the genre is lost.

**Where it comes back:** in ch. 11, `MovieAdapter` displays `movie.getGenre()` directly — so the correct genre appears in the list, but the form shows it wrong. Inconsistency.

</details>

---

## Step 9.3 — The `release == null` trap

### Why

`dateFormat.format(null)` throws a `NullPointerException`.

### When it happens

If a movie was created with the empty constructor and **without** `setRelease`:

```java
Movie movie = new Movie();
movie.setTitle("Test");
// release stays null
```

Then `fillForm` calls `dateFormat.format(existing.getRelease())` → **NPE**.

### Repo version (`d719ffc`)

```java
etRelease.setText(dateFormat.format(existing.getRelease()));
```

**Crashes** if `release` is `null`.

### Your local version (uncommitted change)

```java
if (existing.getRelease() != null) {
    releaseCal.setTime(existing.getRelease());
    etRelease.setText(dateFormat.format(existing.getRelease()));
}
```

**Doesn't crash** — it skips over.

### Exercise 9.3

**Requirement:** create a movie with `release = null` (add it manually in `addSampleMovies`), then try to edit it. What happens with the repo version?

<details>
<summary>Solution — explanatory</summary>

**What was done:** we added in `addSampleMovies`:

```java
Movie broken = new Movie();
broken.setTitle("No date");
broken.setGenre("Drama");
movies.add(broken);
```

**What happens:** on click on "No date", `ItemActivity` crashes:

```
java.lang.NullPointerException: Attempt to invoke virtual method
'java.lang.String java.text.SimpleDateFormat.format(java.util.Date)'
on a null object reference
```

**Why:** `SimpleDateFormat.format(null)` has nothing to format. It throws NPE.

**Remember:**
1. **Any method that receives an object can throw NPE if it receives `null`.**
2. `String.valueOf(null)` **does not** throw — it returns `"null"`. But `dateFormat.format(null)` throws.
3. The difference: `String.valueOf` is static and accepts `Object`; `format` is an instance method and requires a non-null `Date`.

**The fix:** add the `if (existing.getRelease() != null)` check. That's exactly what your local version does.

**Where it comes back:** in ch. 11, `MovieAdapter` already has the check:

```java
String yearStr = movie.getRelease() != null ? dateFormat.format(movie.getRelease()) : "";
```

It's handled correctly there.

</details>

---

## Step 9.4 — The complete edit flow

### How

1. The user taps a movie in the list.
2. `onItemClick` → `intent.putExtra(MOVIE_EXTRA, movies.get(position))` + `putExtra(POSITION_EXTRA, position)`.
3. `launcher.launch(intent)`.
4. `ItemActivity.onCreate` → reads `existing` → `position = ...` → `fillForm(existing)`.
5. The form is populated.
6. The user modifies, presses "Update Movie".
7. `saveMovie()` → builds a new `Movie` → `putExtra(MOVIE_EXTRA, movie)` + `putExtra(POSITION_EXTRA, position)` → `setResult(RESULT_OK)`.
8. `MainActivity.onActivityResult` → `position != -1` → `movies.set(position, movie)`.
9. `notifyDataSetChanged()` → the list refreshes.

### Why `movies.set(position, movie)` and not `movies.add`

`set` **replaces** the element at the given position. `add` would append a duplicate at the end.

### Exercise 9.4

**Requirement:** change `movies.set(position, movie)` to `movies.add(movie)`. Run, edit a movie. What happens?

<details>
<summary>Solution — explanatory</summary>

**What was done:** we replaced `set` with `add` in `onActivityResult`.

**What you see:** after editing, the movie appears **twice** in the list: the old version at the original position, the new version at the end.

**Why:** `add` appends to the end. It doesn't delete anything.

**Remember:**
1. `List.set(index, element)` = replaces, the size stays the same.
2. `List.add(element)` = appends at the end, the size grows.
3. `position` is the only piece of information that tells you **where** to replace.

**Where it comes back:** it doesn't come back, but it's a test question: "what's the difference between `add` and `set`?"

</details>

---

## Step 9.5 — Full verification

### How

1. Run.
2. You see 3 movies.
3. Tap "Inception" → the form opens with all fields filled in.
4. The button says "Update Movie".
5. Change the title to "Inception (2010)".
6. Press Update.
7. **Verify:** the list still has 3 movies, the first one is now "Inception (2010)".

### What to check

- [ ] `fillForm` fills all 10 fields
- [ ] `position` is set correctly
- [ ] the button says "Update Movie"
- [ ] `movies.set(position, movie)` replaces, doesn't add
- [ ] the list stays at 3 elements

### Edge tests

- [ ] you edit, then press **Back** → the list stays unchanged
- [ ] you edit, save, then edit again → the values are the new ones
- [ ] you add a new movie, then edit it → it works

---

## Step 9.6 — Reflection exercise: why `position` and not `id`

**Requirement:** why `position` (index in the list) and not a unique `id` per movie?

<details>
<summary>Answer — explanatory</summary>

**What was done:** the repo uses the list position as the identifier.

**Why it's problematic:**
1. **The position changes** if you add/remove elements. If you sent `position = 2` and meanwhile an element were added at the start, you'd edit the wrong movie.
2. **It's not stable** across sessions. On restart, the list is rebuilt from 0.
3. **It's not unique** in a semantic sense — two steps can have the same position at different times.

**Why it works here:** the list doesn't change while you're in `ItemActivity`. So the position is stable for the duration of the edit.

**How it should be done correctly:** each `Movie` would have a `long id` generated at creation (e.g. `System.currentTimeMillis()` or a counter). On edit, you'd send the `id`, and `MainActivity` would look up the movie with that `id`.

**Remember:**
1. **An index is not an identity.** It's a position in a structure that can change.
2. For small, static lists, an index is acceptable. For dynamic lists, you need an `id`.
3. In databases (Room, SQLite), `id` is mandatory.

**Where it comes back:** in ch. 11, `RecyclerView.Adapter` uses `getBindingAdapterPosition()` — also an index. But there it's safe, because the list doesn't change during a bind.

</details>

---

## Step 9.7 — Compare with the original

```bash
diff "cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java" \
     "_progres/Movies1097/app/src/main/java/ro/ase/ie/g1097/activities/ItemActivity.java"
```

At this stage, your file should be **identical** to `cod-final` (minus any exercises you did).

---

## Chapter 09 summary

- `getIntent()` + `IntentCompat.getSerializableExtra` → you detect the mode.
- `fillForm` = the inverse of `saveMovie`.
- `Spinner` doesn't have `setSelection(text)` → you look up the index.
- `RadioGroup.check(id)` guarantees exclusivity.
- `String.valueOf(double)` can produce scientific notation (`1.6E8`).
- `dateFormat.format(null)` = NPE — a real bug in the repo.
- `movies.set(position, movie)` replaces; `add` would duplicate.

**Next chapter:** [10 - Reconstruieste de la zero.md](10%20-%20Reconstruieste%20de%20la%20zero.md)
