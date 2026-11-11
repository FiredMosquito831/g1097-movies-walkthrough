# Chapter 18 — Requirement bank 2: bindings, views, adapters

**Objective:** to be able to solve, in 30 minutes and without looking at anything, any combination of two requirements out of the three that come up on the test: **bind a value to a widget**, **swap one widget for another**, **build an adapter**. All the examples are on the `G1097` app at commit `d719ffc` — exactly the code from `cod-final/`, not an approximate variant.

**The three things you get asked on the exam:**

| What you're asked | What you touch |
|---|---|
| "bind the value X to the widget Y" | `findViewById` + the right setter (`setText`, `setProgress`, `setRating`, `setChecked`, `setSelection`) |
| "swap a `TextView` for an `EditText`" | XML (the new widget) + `findViewById` (the field type) + reading the value in `saveMovie` |
| "build an adapter" | `RecyclerView.Adapter` + `ViewHolder` + `onBindViewHolder` (+ `LayoutManager` in the activity) |

**Path convention:** all the paths in the chapter are relative to `src/main/` inside the `app` module. So `res/layout/movie_item.xml` means `app/src/main/res/layout/movie_item.xml`, and `java/ro/ase/ie/g1097/model/Movie.java` means `app/src/main/java/ro/ase/ie/g1097/model/Movie.java`.

**The 30-minute rule:** a binding = 5–10 minutes, a widget swap = 10–15, an adapter = 20. If you're given two requirements, start with the one that can't break the build. A half-written adapter doesn't compile at all; a half-written binding compiles and simply does nothing.

**One detail that saves time:** the three requirements aren't independent. "Swap a widget" is also a binding, it just has five points to touch instead of two. And "build an adapter" contains the row binding — `bind()` in the `ViewHolder` is exactly "bind the value X to the widget Y", repeated for every field.

---

## Exercise 18.1 — `tvDurationValue` bound to a `SeekBar`

**Requirement:** `tvDurationValue` (a TextView, the "Production" card in `activity_item.xml`) must always show the value of the `sbDuration` `SeekBar`, in the form `"148 min."`. Bind them. Then explain why, when the form opens in edit mode, the label updates **without** `fillForm` touching it.

> The code in `d719ffc` already contains the binding (`ItemActivity.java`, `initListeners`). The exercise is to rewrite it from memory and explain the mechanism — because the mechanism is exactly what gets asked on the test.

**Files touched:** `java/ro/ase/ie/g1097/activities/ItemActivity.java` (the field, `initControls`, `initListeners`). The XML already has both views.

**How you approach it — your steps:**
1. Open `ItemActivity.java` and find `initControls()`. The line `tvDurationValue = findViewById(R.id.tvDurationValue);` is already there — the field exists, but nobody updates it.
2. Find `initListeners()`. Add `sbDuration.setOnSeekBarChangeListener(...)`. Write only `onProgressChanged` first, with `tvDurationValue.setText(progress + " min.")`. The other two methods stay empty — the interface demands them, even if they do nothing.
3. Open `fillForm(...)` and look for `tvDurationValue`. It isn't there. Run the app, open an existing movie and look at the Duration label: it shows 148, even though `fillForm` wrote nothing there.
4. Explain why: `sbDuration.setProgress(148)` in `fillForm` fired `onProgressChanged`. Then check the order in `onCreate`: `initControls(); initListeners();` run **before** `fillForm(existing)`.

**Hint 1 — if you get stuck at step 1:** `SeekBar` doesn't have `setOnProgressChangedListener`. The method is called `setOnSeekBarChangeListener` and takes a `SeekBar.OnSeekBarChangeListener` with three methods: `onProgressChanged`, `onStartTrackingTouch`, `onStopTrackingTouch`. Only the first one matters to you.

**Hint 2 — if you get stuck at step 3:** if the label stays at "0 min" when you edit a movie, the listener wasn't registered at the time of `setProgress`. Check the order in `onCreate`: `initListeners()` must run before `fillForm(existing)`.

<details>
<summary>Solution — explained</summary>

**What was done:** I bound `tvDurationValue` to `sbDuration` through a listener, not through a manual call. The label doesn't update "on save" or "on open" — it updates on every progress change, no matter who produces it.

**Code:**

```java
// ItemActivity.java — the field already exists
private TextView tvDurationValue;

// initControls() — already there
tvDurationValue = findViewById(R.id.tvDurationValue);

// initListeners() — the binding
sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {

    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {

    }
});
```

**Why:** `onProgressChanged` doesn't mean "the user moved a finger". It means "the progress value changed". `SeekBar` notifies the listener in two situations:

```
fillForm()                          ItemActivity.onCreate()
  sbDuration.setProgress(148)
        │
        ▼
  ProgressBar.setProgressInternal(148, fromUser = false, animate = false)
        │  (if the value differs from the current one)
        ▼
  refreshProgress(...) → onProgressRefresh(scale, fromUser = false, ...)
        │
        ▼
  SeekBar.onProgressRefresh(...) → mOnSeekBarChangeListener.onProgressChanged(seekBar, 148, false)
        │
        ▼
  tvDurationValue.setText("148 min.")
```

The third parameter, `fromUser`, is the only way to tell a drag from code: `true` = the user's finger, `false` = `setProgress` from code.

Direct consequences, all verifiable in the code from `d719ffc`:

1. `fillForm` does **not** need `tvDurationValue.setText(...)`. If you added it, it would be dead code — the listener already does it.
2. The order in `onCreate` matters. `initControls(); initListeners();` run before `fillForm(existing)` (which is called after `getIntent()`). If you moved `initListeners()` after `fillForm`, the listener wouldn't be registered at the time of `setProgress` and the label would stay at "0 min" from the XML.
3. If `onProgressChanged` had a side effect — saving to the database, a `Toast`, a network request — it would also fire during `fillForm`, without the user touching anything. The fix is `if (fromUser) { ... }`.
4. If the value is identical to the current one, `setProgress` notifies nothing (`ProgressBar` exits `setProgressInternal` early). So for a movie with duration 0 — the default value of an `int` — `fillForm` fires nothing, and the label stays at "0 min" from the XML. It happens to be right, but by luck, not by design.

**Remember:**
- `onProgressChanged(seekBar, progress, fromUser)` — `fromUser` is the field that matters, not `progress`.
- `onStartTrackingTouch` / `onStopTrackingTouch` fire **only** on a real touch. If you need "finished dragging", you use `onStopTrackingTouch`.
- `progress` is an `int`. For a `SeekBar` with `max="300"`, the values are 0..300.
- The listener is registered once, in `initListeners()`. Not directly in `onCreate`, not in `fillForm`.

**Where it applies:** `swWatched` has exactly the same problem, with a `CompoundButton`. `fillForm` does `swWatched.setChecked(existing.isWatched())`, and `initListeners` has a `setOnCheckedChangeListener` that writes into `tvWatchedValue`. `fillForm` does **not** touch `tvWatchedValue` — and yet the label updates on edit. Same mechanism, different widget. If the test asks you to explain "why does it work without me writing anything", that's the answer.

</details>

---

## Exercise 18.2 — `etBudget` becomes a `SeekBar` (0–500 million, step 1 million)

**Requirement:** replace the `etBudget` field (`TextInputEditText`) with an `sbBudget` `SeekBar` that goes from 0 to 500 million, in steps of 1 million. A `tvBudgetValue` label shows the current value in the form `"$160M"`.

**Files touched:** `res/layout/activity_item.xml` (the "Production" card), `java/ro/ase/ie/g1097/activities/ItemActivity.java`.

**How you approach it — your steps:**
1. Open `activity_item.xml` and go to the "Production" card. Find `tvBudget` (the "Budget" label) and, right below it, the `TextInputLayout` that contains `etBudget` — the one with `app:prefixText="$ "` and `android:inputType="numberDecimal"`.
2. Delete the whole `TextInputLayout`, along with the `TextInputEditText` inside it. In its place put a horizontal `LinearLayout` with `tvBudgetValue` (weight 1, aligned left) and a small "max $500M" text (right), then a `SeekBar` with `id=sbBudget`, `max=500`, `min=0`.
3. Open `ItemActivity.java`. Change the field type: `private EditText etBudget;` becomes `private SeekBar sbBudget;`. Add `private TextView tvBudgetValue;`.
4. Touch every place where `etBudget` appears: `initControls()` (`findViewById`), `fillForm()` (setProgress), `saveMovie()` (getProgress × 1,000,000). In `initListeners()` you add the listener that writes "$160M".
5. Run it: open Inception → the slider sits at 160, the label shows "$160M". Move the slider → the label changes in steps of 1 million. Save → the budget in the list is the new one.

**Hint 1 — if you get stuck at step 2:** `SeekBar` has no "step". It has `max`. You make the steps yourself, by interpreting the value: progress 0..500 multiplied by `1_000_000`. There is no `android:stepSize` on `SeekBar` (there is on the Material `Slider`, a different widget).

**Hint 2 — if you get stuck at step 4:** if the build says "cannot find symbol: variable etBudget", you forgot one of the four places (the field plus the three uses). Search for `etBudget` in the file with Ctrl+F — you must get zero results before you run.

<details>
<summary>Solution — explained</summary>

**What was done:** I removed the `TextInputLayout` entirely (not just the `EditText` inside it) and put a slider plus a value label in its place. Then I moved the conversion into two places: on read (`fillForm`) and on write (`saveMovie`).

**Code:**

`res/layout/activity_item.xml` — replace the `TextInputLayout` block that contains `etBudget`:

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:orientation="horizontal">

    <TextView
        android:id="@+id/tvBudgetValue"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="$0M"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorPrimary" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="max $500M"
        android:textAppearance="?attr/textAppearanceLabelSmall"
        android:textColor="?attr/colorOnSurfaceVariant" />
</LinearLayout>

<SeekBar
    android:id="@+id/sbBudget"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:layout_marginBottom="16dp"
    android:max="500"
    android:min="0"
    android:progressTint="?attr/colorPrimary"
    android:thumbTint="?attr/colorPrimary" />
```

The `tvBudget` label ("Budget") stays untouched above — you still use it.

`ItemActivity.java` — five changes:

```java
// 1. the fields
private SeekBar sbBudget;        // replaces: private EditText etBudget;
private TextView tvBudgetValue;  // new

// 2. initControls()
sbBudget = findViewById(R.id.sbBudget);   // replaces: etBudget = findViewById(R.id.etBudget);
tvBudgetValue = findViewById(R.id.tvBudgetValue);

// 3. initListeners() — add
sbBudget.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvBudgetValue.setText("$" + progress + "M");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {

    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {

    }
});

// 4. fillForm() — replaces etBudget.setText(String.valueOf(existing.getBudget()));
sbBudget.setProgress((int) Math.round(existing.getBudget() / 1_000_000));

// 5. saveMovie() — replaces Double.parseDouble(etBudget.getText().toString())
movie.setBudget(sbBudget.getProgress() * 1_000_000.0);
```

**Why:**
- `SeekBar` has no steps: it has an integer range 0..500. "Step of 1 million" is your convention, not a widget setting. `max="500"` + `× 1_000_000` = 0..500,000,000.
- `Math.round` on the reverse read: `160_000_000 / 1_000_000 = 160.0` → 160. If the budget were 160,400,000, rounding brings it to 160 — you lose precision, but the step is 1M by definition.
- `fillForm` doesn't touch `tvBudgetValue`: the listener does, because `setProgress` fires `onProgressChanged` (exercise 18.1).
- `saveMovie` can no longer throw `NumberFormatException`. In the current code, `Double.parseDouble("")` crashed if you pressed Save with an empty budget. With a `SeekBar`, the value is always a valid `int`.
- `TextInputLayout` is removed whole, not just its child. It's built for a single `EditText` child and applies hint, counter, error and prefix to it — a `SeekBar` inside it doesn't behave as expected.

**Remember:**
- `android:min` on `SeekBar` exists since API 26. The project's `minSdk` is 33, so it works. On older APIs `min` is ignored and stays 0.
- `max` is the **maximum progress**, not the value. 500 means 500 million only because you multiply.
- If the requirement said "steps of 5 million", you'd have `max="100"` and `× 5_000_000`. Same structure, different number.
- `progressTint` / `thumbTint` are optional; you add them only so the slider looks like the rest of the theme.

**Where it applies:** any "swap X for Y" on the exam has the same five points to touch: the field, `initControls`, `initListeners` (if the new widget has a listener), `fillForm` (reading from the model), `saveMovie` (writing to the model). If you skip one, it either doesn't compile or it compiles and behaves wrongly — and the second one is worse, because nobody catches it until you run it.

</details>

---

## Exercise 18.3 — `rbRating` (`RatingBar`) becomes a `Spinner` with 1–5 stars

**Requirement:** replace the `rbRating` `RatingBar` (5 stars, step 0.5) with an `spRating` `Spinner` with five values: "1 star" … "5 stars". The value is saved in `Movie.rating` as a `float`.

**Files touched:** `res/values/strings.xml` (new array), `res/layout/activity_item.xml` (the "Your verdict" card), `java/ro/ase/ie/g1097/activities/ItemActivity.java`.

**How you approach it — your steps:**
1. Open `res/values/strings.xml` and add a `<string-array name="movie_rating">` with 5 items, next to `movie_genre`, in the same `<resources>`. Without it, `android:entries` doesn't compile.
2. Open `activity_item.xml`, the "Your verdict" card. Delete the `rbRating` `RatingBar` (the one with `numStars="5"`, `stepSize="0.5"`) and put a `Spinner` with `id=spRating` and `android:entries="@array/movie_rating"`.
3. Open `ItemActivity.java` and touch the four places: the field (`RatingBar rbRating` → `Spinner spRating`), `initControls()`, `fillForm()` and `saveMovie()`.
4. Write the conversion in both directions: on read `setSelection((int) rating - 1)`, clamped to 0..4; on write `setRating(position + 1)`.
5. Run it: edit a movie with rating 4.5 → the spinner shows "4 stars" (the half is lost). Save → the rating in the list is 4.

**Hint 1 — if you get stuck at step 4:** `Spinner` returns a **position** (0..4), not a value (1..5). `getSelectedItemPosition()` is the index, `getSelectedItem()` is the text ("3 stars"). For the rating you want the index.

**Hint 2 — if it still doesn't work at step 4:** if the rating is 0 (a new movie, an unset `float` field), `(int) 0 - 1 = -1` — an invalid index. Clamp it: `Math.max(0, Math.min(4, ...))`.

<details>
<summary>Solution — explained</summary>

**What was done:** I replaced a widget with a continuous value (0.0–5.0, step 0.5) with one with discrete values (5 positions). The difference isn't only visual: you need an explicit conversion in both directions, and precision is lost.

**Code:**

`res/values/strings.xml` — add next to `movie_genre`:

```xml
<string-array name="movie_rating">
    <item>1 star</item>
    <item>2 stars</item>
    <item>3 stars</item>
    <item>4 stars</item>
    <item>5 stars</item>
</string-array>
```

`res/layout/activity_item.xml` — replace the `<RatingBar ... />` block:

```xml
<Spinner
    android:id="@+id/spRating"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:entries="@array/movie_rating"
    android:spinnerMode="dropdown" />
```

`ItemActivity.java`:

```java
// 1. the field
private Spinner spRating;   // replaces: private RatingBar rbRating;

// 2. initControls()
spRating = findViewById(R.id.spRating);

// 3. fillForm() — replaces rbRating.setRating(existing.getRating());
int stars = Math.max(0, Math.min(4, (int) existing.getRating() - 1));
spRating.setSelection(stars);

// 4. saveMovie() — replaces movie.setRating(rbRating.getRating());
movie.setRating(spRating.getSelectedItemPosition() + 1);
```

**Why:**
- `setRating(float)` → `setSelection(int)`: `RatingBar` has a continuous value, `Spinner` has an index. `-1` on read and `+1` on write are the conversion.
- `Math.max(0, Math.min(4, ...))`: a new movie has `rating = 0f` (the default value of a `float`), so `(int) 0 - 1 = -1`. A negative index makes no sense for a `Spinner`. The clamp brings it to 0, which is "1 star".
- `setRating(spRating.getSelectedItemPosition() + 1)`: the `int` widens automatically to `float`, so it matches the `setRating(float)` signature.
- `android:entries` binds the array straight from XML, without an `ArrayAdapter` in code — exactly the pattern `spGenre` already uses with `@array/movie_genre`.

**Remember:**
- You lose the half stars. `stepSize="0.5"` allowed 4.5; the `Spinner` only has 1..5. If the requirement says "1–5 stars", that's acceptable; if it says "keep 0.5", you need another widget — the Material `Slider` with `android:stepSize="0.5"`.
- `RatingBar` had `progressTint="#FFC107"`. A `Spinner` has no such thing. Don't try to reproduce the style; the requirement is functional.
- `RatingBar.setRating()` also fires `onRatingChanged(..., fromUser = false)` if you have a listener — same mechanism as in 18.1. Here you have no listener, so you don't see it.
- The variant without an array in XML: `ArrayAdapter.createFromResource(this, R.array.movie_rating, android.R.layout.simple_spinner_item)` plus `setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)`. Longer, but necessary when the list is built in code.

**Where it applies:** `spGenre` is exactly the same pattern — look at it as a model. And that's also where you see the difference: in `saveMovie`, `spGenre.getSelectedItem().toString()` takes the **text** ("Sci-Fi"), not the index. For the rating you want the index, for the genre you want the text. Pick based on what type the model field has.

</details>

---

## Exercise 18.4 — a second line in the `ListView` row (your own `BaseAdapter`)

**Requirement:** the row in the `ListView` must have **two lines**: the movie title and, below it, the genre with the year. Starting from `android.R.layout.simple_list_item_1`, add the second line.

**Files touched:** `res/layout/movie_row.xml` (new), `java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` (new), `java/ro/ase/ie/g1097/activities/MainActivity.java`.

**How you approach it — your steps:**
1. First try what's impossible: search for `simple_list_item_1` in the project (Ctrl+Shift+F). It isn't there — it's in the SDK, not in your project. Note that: there's no file for you to edit.
2. Create `res/layout/movie_row.xml` with a vertical `LinearLayout` and two `TextView`s: `rowTitle` and `rowSubtitle`.
3. Create the `ro.ase.ie.g1097.adapters` package and the `MovieListAdapter extends BaseAdapter` class. Write the skeleton first: `getCount`, `getItem`, `getItemId`, `getView` (empty).
4. Fill in `getView`: `if (convertView == null) { inflate; findViewById; setTag } else { getTag }`, then `setText` on the two views.
5. In `MainActivity`: change the field type and the line in `onCreate`. Run it: two lines per row, the click works unchanged.

**Hint 1 — if you get stuck at step 1:** `android.R.layout.simple_list_item_2` **does** exist and has two `TextView`s (`android.R.id.text1`, `android.R.id.text2`). But `ArrayAdapter` fills only `text1`; `text2` stays empty. So you still end up with your own adapter.

**Hint 2 — if you get stuck at step 4:** if rows repeat wrongly on scroll (the first movie shows up three times), you forgot `convertView.setTag(holder)` or you put `findViewById` outside the `if (convertView == null)` block.

<details>
<summary>Solution — explained</summary>

**What was done:** I gave up on `simple_list_item_1` and wrote my own row plus a `BaseAdapter` that fills it.

The part you have to be able to say at the exam: `android.R.layout.simple_list_item_1` is a file in `platforms/android-XX/data/res/layout/`, packaged in the SDK. It isn't in your project, so it can't be edited. You can't "add a line" to a layout you don't own.

**Code:**

`res/layout/movie_row.xml` (new):

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:paddingHorizontal="16dp"
    android:paddingVertical="12dp">

    <TextView
        android:id="@+id/rowTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ellipsize="end"
        android:maxLines="1"
        android:textSize="18sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/rowSubtitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="2dp"
        android:textColor="#757575"
        android:textSize="14sp" />
</LinearLayout>
```

`java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` (new — create the `adapters` package):

```java
package ro.ase.ie.g1097.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieListAdapter extends BaseAdapter {

    private static class ViewHolder {
        TextView rowTitle;
        TextView rowSubtitle;
    }

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;
    private final LayoutInflater inflater;

    public MovieListAdapter(Context context, List<Movie> movies) {
        this.inflater = LayoutInflater.from(context);
        this.movies = movies;
    }

    @Override
    public int getCount() {
        return movies.size();
    }

    @Override
    public Movie getItem(int position) {
        return movies.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = inflater.inflate(R.layout.movie_row, parent, false);
            holder = new ViewHolder();
            holder.rowTitle = convertView.findViewById(R.id.rowTitle);
            holder.rowSubtitle = convertView.findViewById(R.id.rowSubtitle);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        Movie movie = getItem(position);
        holder.rowTitle.setText(movie.getTitle());

        String year = movie.getRelease() != null
                ? YEAR_FORMAT.format(movie.getRelease())
                : "";
        holder.rowSubtitle.setText(movie.getGenre() + " · " + year);

        return convertView;
    }
}
```

`MainActivity.java` — three changes:

```java
// 1. new import
import ro.ase.ie.g1097.adapters.MovieListAdapter;

// 2. the field — change the type
private MovieListAdapter movieAdapter;   // was: private ArrayAdapter<Movie> movieAdapter;

// 3. onCreate — change the construction
movieAdapter = new MovieListAdapter(this, movies);
// was: movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

Nothing else. `listView.setAdapter(movieAdapter)` and `movieAdapter.notifyDataSetChanged()` stay unchanged — `BaseAdapter` has `notifyDataSetChanged()`.

**Why:**
- `getCount()` → how many rows there are.
- `getItem(position)` → the object at that position; `getItemId` → the id (the position is enough here).
- `getView` → the first half creates the row (once), the second fills it (on every display).
- `convertView == null` = a new row; otherwise it's a recycled row, brought in by `ListView` from off screen. That's why `setTag`/`getTag`: `findViewById` happens once per created row, not on every scroll.

**Remember:**
- `android:entries="@array/items"` in `activity_main.xml` is ignored when you call `setAdapter`. Delete it — otherwise, if you forget `setAdapter`, you see "Item 1…20" and wonder why.
- `setOnItemClickListener` in `MainActivity` works unchanged with `BaseAdapter` — `ListView` knows the position, not the adapter.
- `getItem` returns `Movie`, not `Object`: `listView.getItemAtPosition(position)` gives you a `Movie` directly, with no cast.
- `LayoutInflater.from(context)` is created once, in the constructor — not in `getView`.
- `ViewHolder` is a `private static class`, not a public class: it's an internal detail of the adapter.

**Where it applies:** exactly the same skeleton is used for `RecyclerView`, but there `ViewHolder` is mandatory and the methods are split in two (18.5). If you know 18.4, 18.5 is the same idea with a different signature.

</details>

---

## Exercise 18.5 — `ListView` → `RecyclerView`, the complete exam answer

**Requirement:** replace `ListView` + `ArrayAdapter` with `RecyclerView` + `MovieAdapter`. The row is `movie_item.xml` (already in the repo). Clicking a row must still open `ItemActivity` in edit mode.

> This is the "build an adapter" exercise in its complete form. Write it like on the exam: files in order, each with what it has to contain. If you know this one, 18.6, 18.9 and 18.10 are just differences from it.

**Files touched:** `gradle/libs.versions.toml`, `build.gradle.kts` (the `app` module), `res/layout/activity_main.xml`, `java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (new), `java/ro/ase/ie/g1097/activities/MainActivity.java`.

**How you approach it — your steps:**
1. Add the dependency: `gradle/libs.versions.toml` (one version + one library) and `build.gradle.kts` (`implementation(libs.recyclerview)`). Sync Gradle. Without it, step 3 doesn't compile.
2. `activity_main.xml`: replace `<ListView android:id="@+id/listView" .../>` with `<androidx.recyclerview.widget.RecyclerView android:id="@+id/recyclerView" .../>`. Delete `android:entries`.
3. Create `MovieAdapter.java` in the `adapters` package. Write the skeleton of the three abstract methods first (`onCreateViewHolder`, `onBindViewHolder`, `getItemCount`), then the `ViewHolder` with `findViewById`, then `bind()`.
4. `MainActivity`: change the fields (`ListView` → `RecyclerView`), build the adapter with the click listener, put `setLayoutManager` + `setAdapter` in `initControls()`, delete the `listView.setOnItemClickListener` block from `initListeners()`.
5. Run it: the list looks like before, the click opens the form, saving updates the row. If the list is empty with no error, see Hint 2.

**Hint 1 — if you get stuck at step 1:** `RecyclerView` isn't in `appcompat`, nor in `material`. It's `androidx.recyclerview:recyclerview`, a separate library. Without it: "cannot find symbol class RecyclerView".

**Hint 2 — if you get stuck at step 5:** if the list is empty and no error shows in Logcat, you forgot `setLayoutManager`. It's the only mistake that doesn't complain: a `RecyclerView` without a `LayoutManager` displays nothing.

<details>
<summary>Solution — explained</summary>

**What was done:** I added the dependency, changed the widget in XML, wrote an adapter with a `ViewHolder` and moved the click from `ListView` into the adapter. Five files, in the order below.

**Code:** five files, grouped into four steps.

### Step 0 — the dependency

`gradle/libs.versions.toml`:

```toml
[versions]
recyclerview = "1.4.0"

[libraries]
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

`build.gradle.kts` (the `app` module), inside `dependencies { }`:

```kotlin
implementation(libs.recyclerview)
```

If Android Studio suggests a newer version, accept it — the structure matters, not the number.

### Step 1 — `activity_main.xml`

```xml
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/recyclerView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:listitem="@layout/movie_item" />
```

`tools:listitem` is only for the Android Studio preview: it shows you what a row will look like. At runtime it does nothing. `android:entries` disappears — `RecyclerView` has no such attribute, and if you leave it, it's ignored and confusing.

### Step 2 — `MovieAdapter.java` (new file)

```java
package ro.ase.ie.g1097.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RatingBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.chip.Chip;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(int position);
    }

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;
    private final OnItemClickListener listener;

    public MovieAdapter(List<Movie> movies, OnItemClickListener listener) {
        this.movies = movies;
        this.listener = listener;
    }

    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position), listener);
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

        private final TextView movieTitle;
        private final TextView movieSubtitle;
        private final RatingBar movieRating;
        private final TextView movieRatingValue;
        private final TextView movieFacts;
        private final Chip chipApproval;
        private final Chip chipWatched;
        private final Chip chipWatchlist;

        public MovieViewHolder(@NonNull View itemView) {
            super(itemView);
            movieTitle = itemView.findViewById(R.id.movieTitle);
            movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
            movieRating = itemView.findViewById(R.id.movieRating);
            movieRatingValue = itemView.findViewById(R.id.movieRatingValue);
            movieFacts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchlist = itemView.findViewById(R.id.chipWatchlist);
        }

        public void bind(Movie movie, OnItemClickListener listener) {
            if (movie == null) return;

            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);

            movieRating.setRating(movie.getRating());
            movieRatingValue.setText(String.valueOf(movie.getRating()));

            movieFacts.setText(movie.getDuration() + " min.  ·  $"
                    + (long) (movie.getBudget() / 1_000_000) + "M");

            String approval = movie.getApproval();
            if (approval != null && !approval.isEmpty()) {
                chipApproval.setText(approval);
                chipApproval.setVisibility(View.VISIBLE);
            } else {
                chipApproval.setVisibility(View.GONE);
            }
            chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
            chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

            itemView.setOnClickListener(v -> {
                int pos = getBindingAdapterPosition();
                if (listener != null && pos != RecyclerView.NO_POSITION) {
                    listener.onItemClick(pos);
                }
            });
        }
    }
}
```

`moviePoster` stays unbound — the image still shows the icon from the XML. Actually loading the image is a different requirement; here it's only the text (see 18.6 for the URL).

### Step 3 — `MainActivity.java`

```java
// new imports
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.g1097.adapters.MovieAdapter;

// fields — ListView disappears
private RecyclerView recyclerView;
private MovieAdapter movieAdapter;

// onCreate — replace the ArrayAdapter line
movieAdapter = new MovieAdapter(movies, new MovieAdapter.OnItemClickListener() {
    @Override
    public void onItemClick(int position) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }
});

// initControls() — replaces listView = findViewById(...) and setAdapter
recyclerView = findViewById(R.id.recyclerView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));
recyclerView.setAdapter(movieAdapter);

// initListeners() — DELETE the whole listView.setOnItemClickListener block
```

`notifyDataSetChanged()` in the `launcher` callback stays unchanged — `RecyclerView.Adapter` has the same method.

**Why:**
- `RecyclerView.Adapter` has **three** mandatory abstract methods: `onCreateViewHolder` (creates an empty row), `onBindViewHolder` (fills an existing row), `getItemCount` (how many rows). If one is missing, the class doesn't compile.
- `ViewHolder` is **mandatory**, not optional like with `ListView`. `RecyclerView` uses it to hold the references and stop looking them up with `findViewById` on every display.
- `ViewHolder` is `static` because otherwise every instance would hold a reference to the adapter. With ~10 visible rows you'd have ~10 useless references.
- `onCreateViewHolder` runs **once per created row**; `onBindViewHolder` runs **on every display**. Exactly like the two halves of `getView` in 18.4.
- The click is in `bind`, not in the constructor: if you put it in the constructor, it would capture the position from creation time, which changes on recycling. In `bind`, `getBindingAdapterPosition()` is evaluated at click time.
- `getBindingAdapterPosition()` can return `RecyclerView.NO_POSITION` (-1) during an animation. Without the check, you get an `IndexOutOfBoundsException` at `movies.get(-1)`.
- `launcher` is declared **after** `movieAdapter` in `onCreate`, but the listener runs at click time, much later. It isn't a problem — but you have to be able to explain why.

**Remember:**
- The order on the exam: dependency → XML → adapter → activity. If you start with the adapter, it doesn't compile and you can't tell whether it's the adapter or the dependency.
- `setLayoutManager` is mandatory. Without it: empty list, zero errors.
- `getItemCount()` returns `movies.size()`. If you return something else, you get an `IndexOutOfBoundsException` in `bind`.
- `RecyclerView` **has no** `setOnItemClickListener`. That's why you need your own interface.
- `notifyDataSetChanged()` rebuilds everything, without animations. For animations: `notifyItemInserted`, `notifyItemChanged`, `notifyItemRemoved`.

**Where it applies:** chapter 11 has the same class laid out step by step, and chapter 12 has the mechanism on simple data (numbers 1–100), so you can see the difference between `ListView` and `RecyclerView` without a form around it. Here you have the exam variant: compact, in the order you write it.

</details>

---

## Exercise 18.6 — the poster URL in a `TextView`

**Requirement:** in `MovieAdapter.bind()`, show the poster URL in a `TextView` in the row. No image loading — just the text.

**Files touched:** `res/layout/movie_item.xml`, `java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (the class from 18.5).

**How you approach it — your steps:**
1. Open `movie_item.xml` and go to the info column (the one with `layout_weight="1"`). Find `movieFacts` and put a `TextView` with `id=moviePosterUrl` below it, one line, `ellipsize="middle"`.
2. Open `MovieAdapter.java`. Add `private final TextView moviePosterUrl;` in `MovieViewHolder` and `moviePosterUrl = itemView.findViewById(R.id.moviePosterUrl);` in the constructor.
3. In `bind()`, after `movieFacts`, read `movie.getPoster()` and handle three cases: `null`, `""`, a valid value.
4. Run it: Inception shows the URL, a movie added without a poster shows nothing (the row doesn't grow by an empty line).

**Hint 1 — if you get stuck at step 3:** `poster` has `= null` in the model, but the form writes `""` when the field is empty (`etPoster.getText().toString()`). You need both checks: `poster != null && !poster.isEmpty()`.

**Hint 2 — if you get stuck at step 4:** if the row without a poster still has an empty gap below `movieFacts`, you used `View.INVISIBLE`. It has to be `View.GONE`.

<details>
<summary>Solution — explained</summary>

**What was done:** I added a `TextView` to the row and bound it to `Movie.poster`. We don't load the image — we show the address as text, which is enough for the requirement and brings in no new library.

**Code:**

`res/layout/movie_item.xml` — after `movieFacts`, before the `ChipGroup`:

```xml
<TextView
    android:id="@+id/moviePosterUrl"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:ellipsize="middle"
    android:maxLines="1"
    android:textColor="#9E9E9E"
    android:textSize="12sp" />
```

`MovieAdapter.java` — three additions:

```java
// 1. field in MovieViewHolder
private final TextView moviePosterUrl;

// 2. in the constructor, after movieFacts
moviePosterUrl = itemView.findViewById(R.id.moviePosterUrl);

// 3. in bind(), after movieFacts.setText(...)
String poster = movie.getPoster();
if (poster != null && !poster.isEmpty()) {
    moviePosterUrl.setText(poster);
    moviePosterUrl.setVisibility(View.VISIBLE);
} else {
    moviePosterUrl.setVisibility(View.GONE);
}
```

**Why:**
- `movie.getPoster()` has two "no value" states: `null` (the field is initialized `= null` in the model, and `new Movie()` doesn't touch it) and `""` (the form saves empty text). Both must be handled the same way.
- `ellipsize="middle"` cuts the middle of a long URL, keeping the start and the extension — more useful than `end` for a link.
- `maxLines="1"` is mandatory together with `ellipsize`; otherwise the `TextView` grows to two or three lines and the card gets deformed.
- `View.GONE` removes the view from the layout, so even `layout_marginTop="4dp"` no longer counts. `View.INVISIBLE` would keep it and you'd see a gap.

**Remember:**
- `setText(null)` doesn't throw, but it leaves an empty `TextView` that still takes the line. The explicit check is for `GONE`, not for `setText`.
- The check happens on **every** `bind`, in both branches. A recycled row that had a poster and now doesn't must go back to `GONE`.
- If you wanted the real image, you'd need a library (Glide, Coil) and a network permission. For the exam, text is the correct answer to "show the poster".

**Where it applies:** you'll use exactly the same pattern for any optional field — `writer` (18.10), `approval` (18.9), `poster`. The only difference is the type: `String` with two empty states, `boolean` with none.

</details>

---

## Exercise 18.7 — `LinearLayoutManager` → `GridLayoutManager` with 2 columns

**Requirement:** change the vertical list into a 2-column grid. Then explain what does **not** have to be modified, and why.

**Files touched:** `java/ro/ase/ie/g1097/activities/MainActivity.java` — a single line (plus the import).

**How you approach it — your steps:**
1. Open `MainActivity.java` and go to `initControls()`. Find `new LinearLayoutManager(this)`.
2. Change it to `new GridLayoutManager(this, 2)`. Change the import: `androidx.recyclerview.widget.GridLayoutManager` instead of `LinearLayoutManager`.
3. Run it. Don't touch anything else — not the adapter, not `movie_item.xml`, not `getItemCount`.
4. Note what changed visually (margins, clipped titles, heights) and what stayed identical (the row content, the click, saving).

**Hint 1 — if you get stuck at step 2:** `GridLayoutManager` is in the same package as `LinearLayoutManager` (`androidx.recyclerview.widget`). The second parameter is the number of columns, not the height.

**Hint 2 — if you get stuck at step 4:** the answer to "why doesn't the adapter change" is that the `LayoutManager` receives views already filled by the adapter and only arranges them. It doesn't know what's in them, so there's nothing for it to modify.

<details>
<summary>Solution — explained</summary>

**What was done:** I changed one object. The adapter, the row XML and the rest of the activity stayed untouched.

**Code:**

```java
// before
recyclerView.setLayoutManager(new LinearLayoutManager(this));

// after
recyclerView.setLayoutManager(new GridLayoutManager(this, 2));
```

Import: `androidx.recyclerview.widget.GridLayoutManager`. The `LinearLayoutManager` import becomes useless — delete it (a warning, not an error, but clean code gets points).

**What does NOT change — the answer they want on the exam:**
- `MovieAdapter` — zero lines.
- `movie_item.xml` — zero lines.
- `onCreateViewHolder`, `onBindViewHolder`, `getItemCount` — unchanged.
- The row click, `notifyDataSetChanged()`, the flow to `ItemActivity` — unchanged.

**Why:** `RecyclerView` separates **what you display** (the adapter) from **how you arrange it** (the LayoutManager). With `ListView` the arrangement was fixed, vertical, always — that's why there the change would have meant a different widget. With `RecyclerView` it's a swappable object.

**What changes visually (and should be noticed):**
- each card is half as wide;
- `layout_marginHorizontal="12dp"` in `movie_item.xml` applies **per cell**, so between columns there's 24dp and at the screen edge also 24dp;
- `app:cardUseCompatPadding="true"` adds extra padding — the cards look narrower than you'd expect;
- `movieTitle` has `maxLines="2"`: at half width, titles get clipped more often;
- `movieFacts` ("148 min. · $160M") may not fit on one line.

**Remember:**
- Without `setLayoutManager`, `RecyclerView` shows nothing and throws no error. It's the most common mistake on the exam.
- `LinearLayoutManager(context)` — vertical (the default).
- `LinearLayoutManager(context, RecyclerView.HORIZONTAL, false)` — horizontal.
- `GridLayoutManager(context, spanCount)` — a grid with N columns.
- `StaggeredGridLayoutManager(2, RecyclerView.VERTICAL)` — a grid with different heights.
- For a row that should take the full width in a grid (a header, for example): `gridLayoutManager.setSpanSizeLookup(new GridLayoutManager.SpanSizeLookup() { @Override public int getSpanSize(int position) { return position == 0 ? 2 : 1; } });`

**Where it applies:** if the exam asks for a "horizontal list", it's `new LinearLayoutManager(this, RecyclerView.HORIZONTAL, false)` — still one line, still without touching the adapter. Any requirement about *arrangement* is solved in `MainActivity`, not in the adapter.

</details>

---

## Exercise 18.8 — the row shows `Inception (2010)`: `toString()` or your own adapter?

**Requirement:** the row in the `ListView` (still `ArrayAdapter`, meaning before 18.5) must show `Inception (2010)`. Give **two** solutions and compare them.

**Files touched:** solution A → `java/ro/ase/ie/g1097/model/Movie.java`; solution B → `res/layout/movie_row.xml` + `java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` (from 18.4).

**How you approach it — your steps:**
1. Open `Movie.java` and find `toString()`. It already exists, in debug format (`Movie{title='...', release=...}`).
2. Solution A: replace it with `title + " (" + year + ")"`. You get the year with `SimpleDateFormat("yyyy")`, not with `getYear()`.
3. Run it. The list shows "Inception (2010)". You haven't touched any other file.
4. Solution B: undo `toString()` (go back to the debug format) and modify `MovieListAdapter.getView` from 18.4.
5. Write the comparison: files, lines, time, side effects, what you can do extra.

**Hint 1 — if you get stuck at step 2:** `ArrayAdapter` doesn't know what a `Movie` is. It calls `toString()` on each element — that's the only control point over the text.

**Hint 2 — if it still doesn't work at step 2:** `Date.getYear()` returns the year minus 1900 and is deprecated. 2010 becomes 110. Use `SimpleDateFormat("yyyy", Locale.getDefault())`.

<details>
<summary>Solution — explained</summary>

**What was done:** two correct answers to the same requirement, at very different costs.

**Code:** two solutions, both complete.

### Solution A — `toString()`

`Movie.java`:

```java
import java.text.SimpleDateFormat;
import java.util.Locale;

// ...

private static final SimpleDateFormat YEAR_FORMAT =
        new SimpleDateFormat("yyyy", Locale.getDefault());

@Override
public String toString() {
    String year = release != null ? YEAR_FORMAT.format(release) : "?";
    return title + " (" + year + ")";
}
```

This **replaces** the debug `toString()` that currently exists in `Movie.java`. `ArrayAdapter` calls it for each row, so the list shows exactly what the method returns. Zero changes in `MainActivity`.

### Solution B — your own adapter

From 18.4, you change only the fill line in `getView`:

```java
holder.rowTitle.setText(movie.getTitle() + " (" + year + ")");
holder.rowSubtitle.setVisibility(View.GONE);
```

(or you remove `rowSubtitle` from `movie_row.xml` entirely, if the row has a single line).

### The comparison

| | A: `toString()` | B: your own adapter |
|---|---|---|
| Files | 1 (`Movie.java`) | 2–3 |
| Lines written | ~8 | ~45 |
| Time | 2 minutes | 15 minutes |
| Format | one only, global | as many as you want, per screen |
| Style (bold, grey, two lines, icons) | no | yes |
| Side effects | changes **any** `toString()`: logs, debugger, `Toast`, other adapters | none |
| When you pick it | the requirement is only "the row should show X" | the requirement asks for two lines, colors, several views |

**Why:** A works because `ArrayAdapter` calls `mObjects.get(position).toString()` and puts the result in `android.R.id.text1`. There is no other field. So the only control point over the text is `toString()`.

**Remember:**
- The year trap: `movie.getRelease().getYear()` returns the **year − 1900** and is deprecated. 2010 becomes 110. Use `SimpleDateFormat("yyyy")` or `Calendar`.
- `SimpleDateFormat` is expensive to construct; `static final` = one for all rows. It isn't thread-safe, but here you're on the UI thread.
- `toString()` isn't "just for debug" in Java — any code that calls it uses it. `ArrayAdapter` is exactly such code.
- If the exam asks for **both** the short format **and** two lines, the answer is B. A can't do two lines.
- If you already have your own adapter (18.4), A makes no sense: you already have the place to change the text, without touching the model.

**Where it applies:** if you see `ArrayAdapter` in the exam code and the requirement is about the row text, your first reflex is `toString()`. If you see `BaseAdapter` or `RecyclerView.Adapter`, you modify `getView` / `bind`. The rule: **don't change the model to solve a display problem** if you already have your own adapter.

</details>

---

## Exercise 18.9 — the approval `Chip`, bound and hidden with `View.GONE`

**Requirement:** bind `chipApproval` from `movie_item.xml` to `movie.getApproval()` and hide it with `View.GONE` when the approval is empty.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`. The XML already has the chip, with `android:text="Approved"` hardcoded.

**How you approach it — your steps:**
1. Open `movie_item.xml` and find `chipApproval` — it's there, in the `movieStatusGroup` `ChipGroup`, with `android:text="Approved"` and `android:clickable="false"`.
2. Open `MovieAdapter.java`. Add `private final Chip chipApproval;` in `MovieViewHolder` and `chipApproval = itemView.findViewById(R.id.chipApproval);` in the constructor.
3. In `bind()`, write the two-branch logic: valid value → `setText` + `VISIBLE`; otherwise → `GONE`.
4. Run it: Inception shows "PG-13", Toy Story "G", The Matrix "R". A movie without an approval shows no chip at all.

**Hint 1 — if you get stuck at step 2:** `Chip` extends `TextView` (through `AppCompatCheckBox`), so it has `setText`. The import is `com.google.android.material.chip.Chip`, not `android.widget.*`.

**Hint 2 — if you get stuck at step 4:** if a recycled row keeps the previous movie's chip, you set `setVisibility(VISIBLE)` only on the positive branch. Both branches must set visibility.

<details>
<summary>Solution — explained</summary>

**What was done:** I bound a `Chip` to a `String` field that can be empty, with complete hiding when it has no value.

**Code:**

```java
// 1. field in MovieViewHolder
private final Chip chipApproval;

// 2. in the constructor
chipApproval = itemView.findViewById(R.id.chipApproval);

// 3. in bind(), after movieFacts
String approval = movie.getApproval();
if (approval != null && !approval.trim().isEmpty()) {
    chipApproval.setText(approval);
    chipApproval.setVisibility(View.VISIBLE);
} else {
    chipApproval.setVisibility(View.GONE);
}
```

Import: `com.google.android.material.chip.Chip`.

**Why:**
- `Chip` extends `AppCompatCheckBox`, which extends `TextView` — so `setText()` exists and works normally.
- `View.GONE` = removed from the layout, takes no space. `View.INVISIBLE` = takes space but isn't visible. In a `ChipGroup`, `INVISIBLE` leaves a hole between the chips.
- `trim()`: the form can produce `" "` if the user types a space. `isEmpty()` alone doesn't catch that case.
- `null`: `new Movie()` with no arguments leaves `approval = null`. `approval.isEmpty()` would throw a `NullPointerException` — hence the `!= null` check **before** anything else.

**Remember:**
- `setVisibility` happens on **every** `bind`, in both branches. If you put it only on `VISIBLE`, a recycled row keeps the previous movie's chip. That's the classic recycling bug and you see it immediately when you scroll.
- If all three chips are `GONE`, the `ChipGroup` still has `layout_marginTop="8dp"` and a height of 0 — that is, 8dp of dead space below `movieFacts`. Refinement: keep `movieStatusGroup` in the `ViewHolder` too and hide it when all three are empty.
- `chipApproval` has `android:clickable="false"` — it's a label, not a button. Don't add a listener.
- `app:chipMinHeight="28dp"` and `app:ensureMinTouchTargetSize="false"` are already in the XML; don't touch them, they're there so the chip isn't huge.
- The `"Approved"` text in the XML is only for the preview. If you forget to bind it, all rows show "Approved" — and it looks like it works.

**Where it applies:** `chipWatched` and `chipWatchlist` are exactly the same pattern, but with `boolean`:

```java
chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
```

Here there's no "empty": a `boolean` is always `true` or `false`. That's why they don't need a `null` check — only both branches of the ternary.

</details>

---

## Exercise 18.10 — combo: the `writer` attribute, in XML and in `bind()`

**Requirement:** add a `TextView` for `writer` in `movie_item.xml` and bind it in `MovieAdapter.bind()`. The movie has to have the field — otherwise the requirement can't be written.

**Files touched:** `java/ro/ase/ie/g1097/model/Movie.java`, `res/layout/movie_item.xml`, `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`. Optionally, if the exam also asks for entering the value: `res/layout/activity_item.xml` + `ItemActivity.java`.

**How you approach it — your steps:**
1. Open `Movie.java`. It has no `writer`. Add the field, the getter and the setter. Then decide: do you also put it in the constructor, or only as a setter?
2. If you put it in the constructor, update the 3 `new Movie(...)` calls in `addSampleMovies()` — otherwise it doesn't compile. If not, add a value with the setter, so you have something to see.
3. Open `movie_item.xml` and put the `movieWriter` `TextView` below `movieFacts` (or below `movieSubtitle`, if you want it next to the title).
4. Open `MovieAdapter.java`: field in the `ViewHolder`, `findViewById` in the constructor, the branch in `bind()`.
5. Run it: Inception shows "Written by Christopher Nolan". A movie without a writer doesn't show the line at all.

**Hint 1 — if you get stuck at step 1:** the order is model → layout → adapter. If you start with the XML, you end up writing `movie.getWriter()` in an adapter where the method doesn't exist yet, and you don't understand the error.

**Hint 2 — if you get stuck at step 5:** if everything compiles but you see nothing on screen, all 3 demo movies have `writer == null` and the `TextView` is `GONE`. Put a value into one sample — otherwise it looks like you did nothing.

<details>
<summary>Solution — explained</summary>

**What was done:** I added a new attribute to the model, a new view to the row, and the binding between them. This is the exercise that shows up most often on the exam: "add the attribute X and display it in the list".

**Code:** three files, in the order you write them.

### Step 1 — `Movie.java`

```java
private String writer;

public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}
```

Then you decide about the constructor. The recommended variant: add the parameter **at the end** of the 10-argument constructor.

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, String writer) {
    this.title = title;
    this.release = release;
    this.genre = genre;
    this.budget = budget;
    this.duration = duration;
    this.rating = rating;
    this.watched = watched;
    this.approval = approval;
    this.onWatchlist = onWatchlist;
    this.poster = poster;
    this.writer = writer;
}
```

`MainActivity.addSampleMovies()` — the 3 calls get one more argument at the end:

```java
"https://example.com/posters/inception.jpg",
"Christopher Nolan"));
```

**Why at the end:** if you put `writer` after `title`, you'd have to shift all the arguments in all 3 calls — more chances for a mistake, more time. At the end, you add one line per call.

The alternative without the constructor: leave the constructor untouched and do `movies.get(0).setWriter("Christopher Nolan");` in `addSampleMovies()`. It works, but it's less clean — the model has a field the constructor doesn't cover.

### Step 2 — `movie_item.xml`

After `movieFacts`, before the `ChipGroup`:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:ellipsize="end"
    android:maxLines="1"
    android:textColor="#616161"
    android:textSize="13sp" />
```

### Step 3 — `MovieAdapter.java`

```java
// 1. field in MovieViewHolder
private final TextView movieWriter;

// 2. in the constructor
movieWriter = itemView.findViewById(R.id.movieWriter);

// 3. in bind(), after movieFacts
String writer = movie.getWriter();
if (writer != null && !writer.isEmpty()) {
    movieWriter.setText("Written by " + writer);
    movieWriter.setVisibility(View.VISIBLE);
} else {
    movieWriter.setVisibility(View.GONE);
}
```

**Why:**
- The order model → layout → adapter isn't a preference: if you add the `TextView` in the XML but forget `findViewById`, the compiler doesn't complain — `bind()` simply doesn't touch it, and the row looks empty. If you forget the field in the model, it **doesn't compile** (`getWriter()` doesn't exist). The compiler only catches you in one direction.
- `Movie` is `Serializable`: a new `String` needs nothing special. `Date` was already serializable, `String` too. You don't need `serialVersionUID`.
- The "Written by " prefix goes in `bind`, not in the model. The model holds data, not display text. If tomorrow you want another language, you change one place.

**Remember:**
- If the exam also asks for the form, it's exactly the five steps from 18.2, on a text field: `activity_item.xml` (`TextInputLayout` + `etWriter`), field in `ItemActivity`, `initControls`, `fillForm` → `etWriter.setText(existing.getWriter())`, `saveMovie` → `movie.setWriter(etWriter.getText().toString())`.
- Check it visually. A correctly bound attribute that's always `GONE` looks exactly like an unbound attribute.
- If you add the field to the constructor, the number of arguments changes — every other `new Movie(...)` in the project has to be updated. In `d719ffc` there are exactly 3, all in `addSampleMovies()`. `saveMovie()` uses `new Movie()` with no arguments, so it isn't affected.
- `toString()` doesn't have to be touched. If you leave it in the debug format, it breaks nothing.

**Where it applies:** this is the general pattern for "add the attribute X". Three mandatory files (model, layout, adapter) plus two optional ones if the form is also required (form layout, `ItemActivity`). Count them at the start, so you know when you're done.

</details>

---

## Chapter 18 summary

### The three recipes, in minimal form

**1. Bind the value X to the widget Y** (5 minutes)

```
findViewById(R.id.widgetY)  →  field
listener (if the widget changes)  →  widgetY.setX(value)
```

If the widget changes on its own (SeekBar, Switch, CheckBox, RatingBar), you need a listener. If the value comes from the model and is displayed once, you only need the setter.

**2. Swap one widget for another** (10–15 minutes)

Five points, in this order:

| # | Where | What you do |
|---|---|---|
| 1 | XML | remove the old widget (with its `TextInputLayout`, if it has one) and put the new widget, with an `id` |
| 2 | the field | change the type: `private EditText etBudget;` → `private SeekBar sbBudget;` |
| 3 | `initControls` | `findViewById` on the new id |
| 4 | `fillForm` | read from the model and write into the widget (the conversion, if the types differ) |
| 5 | `saveMovie` | read from the widget and write into the model (the reverse conversion) |

**3. Build an adapter** (20 minutes)

```
dependency (if it's RecyclerView)
  → XML: new widget + delete android:entries
  → Adapter: onCreateViewHolder / onBindViewHolder / getItemCount + ViewHolder
  → Activity: setLayoutManager + setAdapter (+ click)
```

### What you say when you're asked to explain

| Question | The short answer |
|---|---|
| Why does the label update without me touching it? | `setProgress` / `setChecked` fires the listener with `fromUser = false` |
| Why is `ViewHolder` `static`? | otherwise every instance holds a reference to the adapter |
| Why is the click in `bind`, not in the constructor? | the position changes on recycling; in `bind` it's evaluated at click time |
| Why `View.GONE` and not `INVISIBLE`? | `GONE` removes the view from the layout, leaves no gap |
| Why doesn't `ArrayAdapter` work for two lines? | it knows a single `TextView` (`android.R.id.text1`) |
| What doesn't change when you switch to a grid? | the adapter and the row XML — only the `LayoutManager` |
| Why is `toString()` a valid solution? | `ArrayAdapter` calls it on every element |

### The 30-minute plan

| Minutes | What you do |
|---|---|
| 0–2 | Read the requirements and note the files touched for each |
| 2–10 | Solve the binding or widget requirement (compiles fast, low risk) |
| 10–12 | Run it. If it doesn't work, fix it **before** you start the adapter |
| 12–28 | The adapter: dependency → XML → class → activity |
| 28–30 | Run again, check the click and the save, remove unused imports |

### Final checklist

- [ ] I touched every file in "Files touched" for each exercise.
- [ ] `etBudget` / `rbRating` / `listView` no longer appear anywhere in the code after the swap (Ctrl+F).
- [ ] `setLayoutManager` is called before `setAdapter`.
- [ ] Every `if` branch in `bind()` sets visibility, not just the positive one.
- [ ] I ran the app: I add a movie, edit a movie, save, see the result in the list.
