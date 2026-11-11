# Chapter 20 — Requirement bank 4: adding a control

**Objective:** to execute "put a button / a switch / a chip / a FAB" at the exam in 5–10 minutes per control, without forgetting `findViewById`, without `NullPointerException` and without putting the control in a layout that nobody reads.

**What the requirement looks like at the exam:** "Put a button here or another control." It can be anything: button, switch, chip, FAB, spinner, icon. Two requirements, 30 minutes. The teacher changes one word — "button" becomes "switch", "bottom-right" becomes "bottom-left" — and expects the same four-step chain.

**The recipe for any new control (4 steps):**
1. You put it in the XML, with an `android:id`
2. You grab it in code with `findViewById`
3. You attach a listener to it
4. You use it: read the value, change the text, hide it

> **The rule:** XML → `findViewById` → listener → action. Four steps, in that order, for any control. If you skip one, the control shows up but does nothing — and that's the only way you can lose points on such a simple requirement.

**The pocket table:**

| What you're asked for | XML tag | Listener | How you read it |
|---|---|---|---|
| Button | `MaterialButton` / `Button` | `setOnClickListener` | — |
| Switch | `MaterialSwitch` / `Switch` | `setOnCheckedChangeListener` | `isChecked()` |
| Chip | `Chip` | `setOnClickListener` (or `setOnCheckedChangeListener`, if it's `checkable`) | `isChecked()` |
| FAB | `FloatingActionButton` | `setOnClickListener` | — |
| Spinner | `Spinner` | `setOnItemSelectedListener` | `getSelectedItemPosition()` |
| Text field | `TextInputLayout` + `TextInputEditText` | `addTextChangedListener` | `getText().toString()` |

**Conventions — read once, before the first exercise:**
- The starting code is `cod-final/`, that is `G1097` at commit `d719ffc`. All the file names and ids in the chapter are the real ones.
- `activity_main.xml` has `FrameLayout` as its root. A control "above the list" goes in with `android:layout_gravity="top|start"`, and the `ListView` gets `android:layout_marginTop` so it doesn't sit underneath it.
- `movie_item.xml` **exists, but is not used by any adapter** at `d719ffc`: `MainActivity` builds `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, so the row is a single `TextView` with the movie's `toString()`. Any control you put in `movie_item.xml` doesn't show up on screen until you build the adapter — exercise 20.5 builds it.
- Exercises 20.4, 20.5, 20.7 and 20.8 work on the displayed list `visibleMovies` and on the `refreshList()` method, both introduced in 20.4. If you do an exercise without 20.4, replace `visibleMovies` with `movies` and `refreshList()` with `movieAdapter.notifyDataSetChanged()`.

---

## Exercise 20.1 — The "Clear form" button under "Save Movie"

**Requirement:** Add a "Clear form" button under the "Save Movie" button that empties all the form fields, without closing the screen and without touching the movie in the list.

**Files touched:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`.

**How you approach it — your steps:**
1. Open `res/layout/activity_item.xml` and scroll to the end. The last child of the vertical `LinearLayout` is `btnMovieAction` (`MaterialButton`, "Save Movie", height 60dp).
2. Right after the `</com.google.android.material.button.MaterialButton>` of `btnMovieAction`, but before `</LinearLayout>`, add a `MaterialButton` with `android:id="@+id/btnClear"`, `style="@style/Widget.Material3.Button.TextButton"`, `layout_width="match_parent"`, `layout_height="wrap_content"`, `layout_marginTop="8dp"` and `android:text="Clear form"`.
3. Open `activities/ItemActivity.java` and add the field `private Button btClear;` next to `private Button btMovieAction;`.
4. In `initControls()`, add `btClear = findViewById(R.id.btnClear);` at the end of the method.
5. In `initListeners()`, add `btClear.setOnClickListener(v -> clearForm());`.
6. Write the `clearForm()` method at the end of the class: it empties the three `EditText`s and resets `spGenre`, `sbDuration`, `rbRating`, `swWatched`, `cbonWatchList`, `rgApproval` — plus, mandatorily, `releaseCal`.
7. Check: Run, fill in the whole form, press "Clear form". All the fields empty out, the duration label reads "0 min.", the switch's label reads "No", the rating drops to zero. Then fill in only the title and save: the movie must have today's date, not the date you had picked before the clear.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

the button goes in as a sibling of `btnMovieAction`, not inside it. If you put it after `</LinearLayout>`, it becomes the second direct child of the `ScrollView` and you get "ScrollView can host only one direct child".

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

`sbDuration.setProgress(0)` and `swWatched.setChecked(false)` update their own labels, because the listeners from `initListeners()` are already attached. You don't have to write `tvDurationValue.setText("0 min.")` yourself.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a new button in the form, grabbed with `findViewById`, with a listener that calls a `clearForm()` method which brings every control back to its default value.

**Code (XML + Java):**

`res/layout/activity_item.xml` — after `btnMovieAction`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnClear"
    style="@style/Widget.Material3.Button.TextButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Clear form"
    app:icon="@android:drawable/ic_menu_close_clear_cancel"
    app:iconGravity="textStart" />
```

`activities/ItemActivity.java`:

```java
// the field, next to the others
private Button btClear;

// initControls(), at the end
btClear = findViewById(R.id.btnClear);

// initListeners(), at the end
btClear.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        clearForm();
    }
});

// the new method, at the end of the class
private void clearForm() {
    etTitle.setText("");
    etRelease.setText("");
    etRelease.setError(null);
    releaseCal = Calendar.getInstance();   // the trap: the text doesn't hold the date
    spGenre.setSelection(0);
    etBudget.setText("");
    sbDuration.setProgress(0);
    rbRating.setRating(0f);
    swWatched.setChecked(false);
    cbonWatchList.setChecked(false);
    rgApproval.check(R.id.rbGeneral);
    etPoster.setText("");
    etTitle.requestFocus();
}
```

**Why:** every control has its own write method — `setText`, `setSelection`, `setProgress`, `setRating`, `setChecked`, `check`. `clearForm()` calls all of them, in the order of the form, so you can visually check that you didn't skip any.

**Remember:**
1. **`releaseCal` is not emptied by `etRelease.setText("")`.** `saveMovie()` doesn't read the field's text, it reads `releaseCal.getTime()`. If you don't reset the calendar, after "Clear form" and "Save Movie" the movie gets the old date back, even though the field was empty. It's the most common mistake with this button.
2. **`setProgress(0)` and `setChecked(false)` trigger the listeners.** The `tvDurationValue` and `tvWatchedValue` labels update themselves. If you set them too, it doesn't hurt; if you forget them, it's still correct.
3. **The button doesn't save.** It doesn't call `saveMovie()`, it doesn't call `setResult`, it doesn't call `finish()`. It empties and that's it.
4. **The trap behind it:** after "Clear form", `etBudget` is empty, and `saveMovie()` does `Double.parseDouble("")` → `NumberFormatException`. If the teacher presses Save right after Clear, the app crashes. The minimal defence, at the start of `saveMovie()`: `if (etBudget.getText().toString().isEmpty()) { etBudget.setError("Budget required"); return; }`.

**Where it applies:** any requirement of the kind "a button that resets the form", "a cancel button", "empties the fields". The same `clearForm()` is also used after a successful Save, if you want to stay on the screen.

</details>

---

## Exercise 20.2 — A second FAB, bottom-left, that shows the number of movies

**Requirement:** Add a second `FloatingActionButton` to `activity_main.xml`, in the bottom-left corner. On press, it shows a `Toast` with the number of movies in the list.

**Files touched:** `res/layout/activity_main.xml`, `activities/MainActivity.java`.

**How you approach it — your steps:**
1. Open `res/layout/activity_main.xml`. The root is `FrameLayout`; the children are the `ListView` (`listView`) and the existing FAB (`floatingActionButton`, with `layout_gravity="bottom|end"`).
2. After the existing FAB, add a second `FloatingActionButton` with `android:id="@+id/fabCount"`, `android:layout_gravity="bottom|start"`, `android:layout_margin="16dp"`, `android:contentDescription="Show movie count"` and `app:srcCompat` pointing to an icon.
3. Open `activities/MainActivity.java` and add the field `private FloatingActionButton fabCount;` next to `fabInsert`.
4. In `initControls()`, add `fabCount = findViewById(R.id.fabCount);`.
5. In `initListeners()`, add `fabCount.setOnClickListener(...)` which shows `Toast.makeText(MainActivity.this, movies.size() + " movies", Toast.LENGTH_SHORT).show();`.
6. Check: Run. A second round button appears bottom-left. Tap it: "3 movies". Add a movie, tap it again: "4 movies".

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

`FrameLayout` positions its children by `android:layout_gravity`. `bottom|end` = bottom-right, `bottom|start` = bottom-left. If you forget `layout_gravity`, the button sits in the top-left corner, on top of the list.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

`Toast.makeText(...)` needs a `Context`. In an anonymous class you write `MainActivity.this`; in a lambda `this` is already `MainActivity`. `MainActivity.this` works in both cases, so it's the safe choice.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a second FAB in the same `FrameLayout`, in the opposite corner, with a listener that reads the size of the list and shows it in a `Toast`.

**Code (XML + Java):**

`res/layout/activity_main.xml` — after the `floatingActionButton` FAB:

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/fabCount"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="bottom|start"
    android:layout_margin="16dp"
    android:contentDescription="Show movie count"
    app:srcCompat="@android:drawable/ic_menu_info_details" />
```

`activities/MainActivity.java`:

```java
private FloatingActionButton fabCount;

// initControls()
fabCount = findViewById(R.id.fabCount);

// initListeners()
fabCount.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Toast.makeText(MainActivity.this,
                movies.size() + " movies",
                Toast.LENGTH_SHORT).show();
    }
});
```

**Why:** `FrameLayout` has no rows or columns — each child positions itself through `layout_gravity`. The second FAB is just another child, in the free corner. `Toast` is the cheapest way to show a value: one line, no new layout, no dialog.

**Remember:**
1. **`movies.size()` is the total number; `visibleMovies.size()` is the displayed number.** If you did 20.4 and the switch is on, the two differ. Pick the one that was asked for and say at the exam which one you're using.
2. **`Toast` doesn't block the app.** It disappears on its own after about two seconds (`LENGTH_SHORT`) or three (`LENGTH_LONG`).
3. **`android:contentDescription` is not decorative.** Without it, lint gives a warning, and TalkBack announces "button" without saying what it does.
4. **Two FABs don't overlap** if one is `bottom|start` and the other is `bottom|end`. If you put both in the same corner, the last one drawn covers the first.
5. **The icon can be anything.** I used `@android:drawable/ic_menu_info_details` so the difference is visible; you can reuse `@drawable/outline_add_24`, but then the buttons look identical and the teacher can't see that you added something.

**Where it applies:** any "another floating button", "info button", "show a number". The same pattern: a new child in the `FrameLayout`, a different `layout_gravity`, a listener that reads a value.

</details>

---

## Exercise 20.3 — The "Delete" button in `ItemActivity`, with its own result code

**Requirement:** Add a "Delete movie" button to `ItemActivity` that closes the screen with its own result code (`RESULT_DELETE`), and `MainActivity` removes the movie from the list when it receives that code. The button doesn't appear when you're adding a new movie.

**Files touched:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**How you approach it — your steps:**
1. In `activity_item.xml`, after `btnMovieAction`, add a `MaterialButton` with `android:id="@+id/btnDelete"`, style `@style/Widget.Material3.Button.OutlinedButton`, text "Delete movie" and the color `?attr/colorError`.
2. In `ItemActivity.java`, add the constant `public static final int RESULT_DELETE = 2;` right under the class declaration, next to the fields.
3. Add the field `private Button btDelete;`, the line in `initControls()` and the listener in `initListeners()`.
4. Write the `deleteMovie()` method: put `position` into the Intent, call `setResult(RESULT_DELETE, intent)` and `finish()`.
5. At the end of `onCreate`, after the `if (existing != null)` block, add `btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);`.
6. In `MainActivity.java`, in the launcher callback, add the branch `else if (o.getResultCode() == ItemActivity.RESULT_DELETE)`.
7. Check: Run, tap a movie, press Delete — the row disappears from the list. Tap the "+" FAB: the Delete button isn't visible.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

result codes are `int`s. `RESULT_OK` = -1, `RESULT_CANCELED` = 0, `RESULT_FIRST_USER` = 1. Any custom code must be ≥ 1; use 2 or `RESULT_FIRST_USER`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

`o.getData()` can be `null` when the result has no Intent. Check `data != null` before `getIntExtra`, otherwise you get a `NullPointerException` right on the new branch.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a new button in the form, a result constant, an `Intent` that carries the position and a new branch in the callback in `MainActivity`.

**Code (XML + Java):**

`res/layout/activity_item.xml` — after `btnMovieAction`:

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
public static final int RESULT_DELETE = 2;

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

// onCreate(), after the if (existing != null) block
btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);
```

`activities/MainActivity.java` — the launcher callback becomes:

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    refreshList();   // or movieAdapter.notifyDataSetChanged()
} else if (o.getResultCode() == ItemActivity.RESULT_DELETE) {
    Intent data = o.getData();
    if (data != null) {
        int position = data.getIntExtra(POSITION_EXTRA, -1);
        if (position >= 0 && position < movies.size()) {
            movies.remove(position);
            refreshList();   // or movieAdapter.notifyDataSetChanged()
        }
    }
}
```

**Why:** `setResult` carries two things — a code and an optional `Intent`. The code says *what happened*, the Intent says *with what*. `RESULT_OK` means save, `RESULT_DELETE` means delete; `MainActivity` needs the position so it knows which row to remove.

**Remember:**
1. **The custom code must be ≥ 1.** 0 is `RESULT_CANCELED`, -1 is `RESULT_OK`. A code of 0 would be treated as "the user pressed Back".
2. **`position` is the field in `ItemActivity`,** set in `onCreate` only when you came in with `MOVIE_EXTRA`. In insert mode it stays -1, so the button hides itself.
3. **Hide the button with `View.GONE`, not `INVISIBLE`.** GONE removes the space it takes too; otherwise the form has a 60dp hole under the save button.
4. **Without `refreshList()` (or `notifyDataSetChanged()`), the movie disappears from `movies` but stays on screen** until the next redraw. The list and the model are kept in sync by hand — that's the theme of the whole chapter.
5. **Deletion doesn't ask for confirmation here.** If you have 30 free seconds, wrap `deleteMovie()` in an `AlertDialog`; but finish the result chain first, because that's the point.

**Where it applies:** any "close with a result that isn't OK" — delete, cancel, "add to favorites" from a secondary screen. The pattern is always the same: custom constant, `setResult`, new branch in the callback.

</details>

---

## Exercise 20.4 — A `Switch` above the list that filters the watched movies

**Requirement:** Add a `Switch` to `MainActivity`, above the list, with the text "Only watched". When it's on, the list shows only the movies with `watched == true`; when it's off, it shows all of them. The list redraws immediately, and the movies aren't lost.

**Files touched:** `res/layout/activity_main.xml`, `activities/MainActivity.java`.

**How you approach it — your steps:**
1. In `activity_main.xml`, add a `MaterialSwitch` with `android:id="@+id/swOnlyWatched"`, `android:layout_gravity="top|start"`, `android:layout_margin="16dp"` and `android:text="Only watched"`, as the last child of the `FrameLayout`.
2. Give the `ListView` `android:layout_marginTop="72dp"`, so the first row doesn't sit under the switch.
3. In `MainActivity.java`, add the fields `private MaterialSwitch swOnlyWatched;` and `private final List<Movie> visibleMovies = new ArrayList<>();`.
4. Change the adapter to work on `visibleMovies`, not on `movies`.
5. Add the line in `initControls()` and the listener in `initListeners()`.
6. Write `refreshList()`: it empties `visibleMovies`, fills it from `movies` according to the switch state and calls `notifyDataSetChanged()`.
7. Replace `movies.get(position)` in the click with `visibleMovies.get(position)` and send `movies.indexOf(movie)` as the position.
8. Check: Run. Turn the switch on: only Inception and Toy Story remain (both have `watched = true`). Add a new movie with the switch on: it doesn't appear until you turn the switch off.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 6</summary>

don't filter `movies` directly. `movies` is the data source; if you empty it, the movies are lost for good. Filtering happens in a second list, `visibleMovies`, which the adapter reads.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

`ArrayAdapter` keeps the reference to the list it received in the constructor. If you change the list's contents (`clear()` + `add()`), the adapter sees the change after `notifyDataSetChanged()`. If you replace the reference (`visibleMovies = new ArrayList<>()`), the adapter stays on the old list and you no longer see anything.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a displayed list separate from the source list, a switch that rebuilds it and a single redraw point (`refreshList()`).

**Code (XML + Java):**

`res/layout/activity_main.xml`:

```xml
<com.google.android.material.materialswitch.MaterialSwitch
    android:id="@+id/swOnlyWatched"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="top|start"
    android:layout_margin="16dp"
    android:text="Only watched" />
```

and, on the `ListView`:

```xml
android:layout_marginTop="72dp"
```

`activities/MainActivity.java`:

```java
private MaterialSwitch swOnlyWatched;
private final List<Movie> visibleMovies = new ArrayList<>();

// onCreate — the adapter binds to the displayed list
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, visibleMovies);
initControls();
initListeners();
// ... launcher ...
refreshList();   // at the end of onCreate

// initControls()
swOnlyWatched = findViewById(R.id.swOnlyWatched);

// initListeners()
swOnlyWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        refreshList();
    }
});

// the new method
private void refreshList() {
    visibleMovies.clear();
    for (Movie movie : movies) {
        if (!swOnlyWatched.isChecked() || movie.isWatched()) {
            visibleMovies.add(movie);
        }
    }
    movieAdapter.notifyDataSetChanged();
}
```

The row click becomes:

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Movie movie = visibleMovies.get(position);
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movie);
        intent.putExtra(POSITION_EXTRA, movies.indexOf(movie));
        launcher.launch(intent);
    }
});
```

And in the launcher callback, both `movieAdapter.notifyDataSetChanged()` calls are replaced with `refreshList()`.

**Why:** two lists, two roles. `movies` = the truth; `visibleMovies` = what you see. `refreshList()` rebuilds the second from the first, every time the filter or the data changes. The adapter doesn't know about the filter — it only sees the list it has.

**Remember:**
1. **The new imports:** `import android.widget.CompoundButton;` and `import com.google.android.material.materialswitch.MaterialSwitch;` in `MainActivity.java`. Without them the code doesn't compile; Android Studio only adds them automatically if you press on the suggestion.
2. **`movies.indexOf(movie)` works because `Movie` has no `equals()`.** `indexOf` compares references, and both lists hold the same objects. If you added an `equals()` by title, two movies with the same title would become indistinguishable.
3. **`refreshList()` is called in three places:** at the end of `onCreate`, in the switch listener and after every result from `ItemActivity`. If you forget one, the list stays out of sync exactly in the case the teacher tests.
4. **`MaterialSwitch` needs the Material3 theme.** The app's theme is `Theme.G1097`, with parent `Theme.Material3.DayNight.NoActionBar`, so it works with no change.
5. **`layout_marginTop="72dp"` on the `ListView` is not cosmetic.** Without it, the first row sits under the switch and you can't tap it.
6. **The filter doesn't change `watched`.** A movie removed from the list keeps its value; only what you see changes, not what's in the model.

**Where it applies:** any filter — "only watchlist", "only rating ≥ 4", "only the chosen genre". Only the condition in the `if` changes; the rest stays identical.

</details>

---

## Exercise 20.5 — A "New" `Chip` in the card, for movies released in the last 5 years

**Requirement:** Add a `Chip` with the text "New" to `movie_item.xml`, visible only when the movie was released in the last 5 years.

**Files touched:** `res/layout/movie_item.xml`, `adapters/MovieAdapter.java` (new), `activities/MainActivity.java`.

**Careful — the trap of this exercise:** at `d719ffc`, `movie_item.xml` isn't used by any adapter. `MainActivity` has `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, so the row is a single `TextView` with the movie's `toString()`. If you put the chip in `movie_item.xml` and run, nothing happens. For it to appear, you need an adapter that inflates `movie_item.xml` — you build it here, in about 70 lines including imports.

**How you approach it — your steps:**
1. In `movie_item.xml`, find the `movieStatusGroup` `ChipGroup` and its last child, `chipWatchlist`. After it, add a `Chip` with `android:id="@+id/chipNew"`, text "New" and `android:visibility="gone"`.
2. Create the package `ro.ase.ie.g1097.adapters` and the class `MovieAdapter extends ArrayAdapter<Movie>`.
3. Write the constructor `(Context, List<Movie>)`, which calls `super(context, 0, movies)`.
4. Override `getView()`: inflate `R.layout.movie_item` if `convertView` is null, get the movie with `getItem(position)` and bind the title, subtitle, rating, facts and the existing chips.
5. Compute "new": `Calendar fiveYearsAgo = Calendar.getInstance(); fiveYearsAgo.add(Calendar.YEAR, -5);` and compare with `movie.getRelease()`.
6. Set `chipNew.setVisibility(isNew ? View.VISIBLE : View.GONE);`.
7. In `MainActivity`, change `new ArrayAdapter<>(...)` to `new MovieAdapter(this, visibleMovies)`.
8. Check: Run. Inception (2010) and Toy Story (1995) have no chip; add a movie with today's date — it appears with "New". Add one from 2015 — no chip.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

`ArrayAdapter` asks for a layout in the constructor, but if you override `getView()` you can pass `0`. Nothing is inflated with it; you only use it so `getItem()` and `getCount()` are ready-made.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

`convertView` is reused. If you set `chipNew` visible for a new movie and don't hide it for the next one, the chip stays stuck on the recycled row. That's why `setVisibility` is done on every `getView`, in both branches — `VISIBLE` and `GONE`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a new chip in the card, a custom adapter for the `ListView` and the 5-year rule in `getView()`.

**Code (XML + Java):**

`res/layout/movie_item.xml` — in the `movieStatusGroup` `ChipGroup`, after `chipWatchlist`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipNew"
    style="@style/Widget.Material3.Chip.Suggestion"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="New"
    android:clickable="false"
    android:visibility="gone"
    app:chipMinHeight="28dp"
    app:ensureMinTouchTargetSize="false" />
```

`java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (new file):

```java
package ro.ase.ie.g1097.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.RatingBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.google.android.material.chip.Chip;

import java.util.Calendar;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends ArrayAdapter<Movie> {

    public MovieAdapter(@NonNull Context context, @NonNull List<Movie> movies) {
        super(context, 0, movies);
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext())
                    .inflate(R.layout.movie_item, parent, false);
        }

        Movie movie = getItem(position);
        if (movie == null) {
            return convertView;
        }

        TextView tvTitle = convertView.findViewById(R.id.movieTitle);
        TextView tvSubtitle = convertView.findViewById(R.id.movieSubtitle);
        RatingBar rbRating = convertView.findViewById(R.id.movieRating);
        TextView tvRatingValue = convertView.findViewById(R.id.movieRatingValue);
        TextView tvFacts = convertView.findViewById(R.id.movieFacts);
        Chip chipApproval = convertView.findViewById(R.id.chipApproval);
        Chip chipWatched = convertView.findViewById(R.id.chipWatched);
        Chip chipWatchlist = convertView.findViewById(R.id.chipWatchlist);
        Chip chipNew = convertView.findViewById(R.id.chipNew);

        tvTitle.setText(movie.getTitle());

        if (movie.getRelease() != null) {
            Calendar release = Calendar.getInstance();
            release.setTime(movie.getRelease());
            tvSubtitle.setText(movie.getGenre() + " · " + release.get(Calendar.YEAR));
        } else {
            tvSubtitle.setText(movie.getGenre());
        }

        rbRating.setRating(movie.getRating());
        tvRatingValue.setText(String.valueOf(movie.getRating()));
        tvFacts.setText(String.format(Locale.getDefault(), "%d min  ·  $%,.0f",
                movie.getDuration(), movie.getBudget()));

        chipApproval.setText(movie.getApproval());
        chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
        chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

        Calendar fiveYearsAgo = Calendar.getInstance();
        fiveYearsAgo.add(Calendar.YEAR, -5);
        boolean isNew = movie.getRelease() != null
                && movie.getRelease().after(fiveYearsAgo.getTime());
        chipNew.setVisibility(isNew ? View.VISIBLE : View.GONE);

        return convertView;
    }
}
```

`activities/MainActivity.java` — a single line:

```java
movieAdapter = new MovieAdapter(this, visibleMovies);   // before: new ArrayAdapter<>(...)
```

**Why:** `ListView` doesn't know how to fill a complex layout. The default `ArrayAdapter` inflates `simple_list_item_1`, that is a `TextView`. For the card in `movie_item.xml` to appear, you need an adapter that inflates it and binds each view to its own field.

**Remember:**
1. **`movie_item.xml` existed, but it was dead.** That's the trap: the file is in the repo, it looks good in the preview, but no code loads it. A control put there doesn't appear until the adapter exists.
2. **`convertView` is recycled.** All the `setVisibility` calls are made on every `getView`, not only when you create the row. Otherwise, a chip from row 3 appears on row 10 after scrolling.
3. **The 5-year rule:** `Calendar.add(Calendar.YEAR, -5)` accounts for leap years; `Date.after` is a strict comparison. A movie released exactly 5 years and one day ago isn't "New".
4. **`ListView` ignores the margin on the row's root.** `AbsListView` uses `AbsListView.LayoutParams`, which doesn't keep margins; the space between cards comes from `app:cardUseCompatPadding="true"`, already in the layout.
5. **`getView` runs on every scroll.** Don't do heavy work there; two `Calendar.getInstance()` per row are acceptable, but if you want, move them into a field of the adapter.

**Where it applies:** any "show a chip / a badge / a label based on a condition". The condition changes, the rest of the chain stays: field in the XML, `findViewById` in `getView`, `setVisibility`.

</details>

---

## Exercise 20.6 — Replace the FAB's icon with a new `VectorDrawable`

**Requirement:** Change the FAB's icon in `activity_main.xml` to another one, created by you as a `VectorDrawable` (File → New → Vector Asset). The old icon stays in the project.

**Files touched:** `res/drawable/ic_star_24.xml` (new), `res/layout/activity_main.xml`.

**How you approach it — your steps:**
1. In Android Studio, right-click the `res` folder → New → Vector Asset.
2. Asset Type: **Clip Art**. Click the "Clip Art" button, search for "star", pick the icon, OK.
3. Name: `ic_star_24`. Size: 24dp x 24dp. Next → Finish. `res/drawable/ic_star_24.xml` appears.
4. Open `activity_main.xml`, find the `floatingActionButton` FAB and change `app:srcCompat="@drawable/outline_add_24"` to `app:srcCompat="@drawable/ic_star_24"`.
5. Also change `android:contentDescription` from "Add" to something that describes the new action.
6. Check: Run. The round button now has a star. If it appears black on the colored background, add `app:tint="?attr/colorOnPrimaryContainer"` to the FAB or remove `android:tint` from the vector.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 1</summary>

the dialog has two screens. The first picks the type and the icon; the second picks the name and the color. If you close it on the first, nothing was created.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

the name matters. `ic_star_24` becomes `R.drawable.ic_star_24`. Resources want lowercase letters, digits and underscores — no capitals, no hyphens, no spaces.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a new vector file in `res/drawable/` and a single reference changed in the layout.

**Code (XML + Java):**

`res/drawable/ic_star_24.xml` — generated by the wizard, looks like this:

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF000000"
        android:pathData="M12,17.27L18.18,21l-1.64,-7.03L22,9.24l-7.19,-0.61L12,2 9.19,8.63 2,9.24l5.46,4.73L5.82,21z" />
</vector>
```

`res/layout/activity_main.xml` — the FAB becomes:

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="bottom|end"
    android:layout_margin="16dp"
    android:contentDescription="Add to favorites"
    app:srcCompat="@drawable/ic_star_24" />
```

**Why:** a `VectorDrawable` is a drawing described by coordinates (`pathData`), not by pixels. A file of a few hundred bytes looks good at any density, because the system renders it at the requested size.

**Remember:**
1. **`app:srcCompat`, not `android:src`.** The FAB uses `srcCompat`; `android:src` works on new API levels, but not on all versions, and lint warns you.
2. **`android:tint="#000000"` in the vector is a trap.** If you leave it, the icon is black wherever you put it. In a FAB, `app:tint` (by default `?attr/colorOnPrimaryContainer` in Material3) overrides the vector's tint; in a plain `ImageView`, it doesn't.
3. **`android:contentDescription` describes the action, not the drawing:** "Add to favorites", not "star".
4. **The old vector stays in the project.** Don't delete it unless you're asked to; if you delete it and something still references it, the build fails with "resource not found".
5. **The 10-second version, if you don't have time for the dialog:** `app:srcCompat="@android:drawable/btn_star_big_on"`. It works, but the "create a vector asset" requirement isn't met.

**Where it applies:** any "change the icon", "put an arrow", "add an icon to the button". `app:icon` on a `MaterialButton` works exactly the same way.

</details>

---

## Exercise 20.7 — An "Edit" button in the card, instead of tapping the whole row

**Requirement:** Add an "Edit" `MaterialButton` to the card in `movie_item.xml` that opens `ItemActivity` in edit mode. Tapping any other area of the card no longer does anything.

**Files touched:** `res/layout/movie_item.xml`, `adapters/MovieAdapter.java`, `activities/MainActivity.java`.

**Assumes:** the adapter from 20.5.

**How you approach it — your steps:**
1. In the info column of `movie_item.xml`, after the `movieStatusGroup` `ChipGroup`, add a `MaterialButton` with `android:id="@+id/btnEdit"`, style `@style/Widget.Material3.Button.TextButton`, text "Edit" and `android:layout_gravity="end"`.
2. In the adapter, add the `OnEditClickListener` interface with the method `onEditClick(int position)`.
3. Add the field `private final OnEditClickListener listener;` and the matching parameter in the constructor.
4. In `getView`, grab the button and attach `btnEdit.setOnClickListener(v -> listener.onEditClick(position));`.
5. In `MainActivity`, delete (or comment out) the `listView.setOnItemClickListener(...)` block from `initListeners()`.
6. Add the method `openForEdit(int listPosition)`: get the movie from `visibleMovies`, put `movies.indexOf(movie)` as the position and launch `ItemActivity`.
7. Change the adapter construction to `new MovieAdapter(this, visibleMovies, this::openForEdit)`.
8. Check: Run. Tap the card outside the button — nothing. Tap "Edit" — the filled-in form opens, the screen title is "Edit movie", and the save button reads "Update Movie".

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 6</summary>

`position` in `getView` is the position in the displayed list, not in `movies`. When you filter (20.4), the two differ. That's why `MainActivity` receives the position from the list and translates it with `movies.indexOf(movie)`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

the listener is attached on every `getView`, not once. If you put it only in the `convertView == null` branch, the recycled row's button will open the movie that was there on the first inflation.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a button in the card, a callback interface in the adapter and a public open method in `MainActivity`.

**Code (XML + Java):**

`res/layout/movie_item.xml` — in the info column, after the `ChipGroup`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnEdit"
    style="@style/Widget.Material3.Button.TextButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="end"
    android:minWidth="0dp"
    android:minHeight="0dp"
    android:text="Edit"
    app:icon="@android:drawable/ic_menu_edit"
    app:iconGravity="textStart" />
```

`adapters/MovieAdapter.java` — three additions:

```java
public interface OnEditClickListener {
    void onEditClick(int position);
}

private final OnEditClickListener listener;

public MovieAdapter(@NonNull Context context, @NonNull List<Movie> movies,
                    @NonNull OnEditClickListener listener) {
    super(context, 0, movies);
    this.listener = listener;
}

// in getView, after the other findViewById calls
MaterialButton btnEdit = convertView.findViewById(R.id.btnEdit);
btnEdit.setOnClickListener(v -> listener.onEditClick(position));
```

`activities/MainActivity.java`:

```java
// initListeners() — the listView.setOnItemClickListener(...) block is deleted entirely

// the new method
private void openForEdit(int listPosition) {
    if (listPosition < 0 || listPosition >= visibleMovies.size()) {
        return;
    }
    Movie movie = visibleMovies.get(listPosition);
    Intent intent = new Intent(this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movie);
    intent.putExtra(POSITION_EXTRA, movies.indexOf(movie));
    launcher.launch(intent);
}

// onCreate
movieAdapter = new MovieAdapter(this, visibleMovies, this::openForEdit);
```

**Why:** the button needs a path back to `MainActivity`. The interface is that path: the adapter doesn't know what `MainActivity` is, it only knows that someone wants to find out the tapped position. `this::openForEdit` is the method that receives the position.

**Remember:**
1. **New import in the adapter:** `import com.google.android.material.button.MaterialButton;`. Without it, `findViewById(R.id.btnEdit)` returns `View`, not `MaterialButton`.
2. **`this::openForEdit`** is the lambda equivalent of `new OnEditClickListener() { public void onEditClick(int p) { openForEdit(p); } }`. It works because the interface has a single method.
3. **The quick version, without an interface:** `((MainActivity) getContext()).openForEdit(position)` directly in the adapter. It compiles and works at the exam, but it creates a dependency from `adapters` to `activities` — exactly what chapter 12 says to avoid.
4. **The listener goes outside the `if (convertView == null)` block.** `convertView` is reused, but the listener has to know the new position.
5. **The button consumes only its own clicks.** The rest of the card no longer reacts because you deleted `setOnItemClickListener`; if you want the whole card clickable, put `setOnClickListener` on `convertView`, and then the button is redundant.
6. **`android:minWidth="0dp"` and `android:minHeight="0dp"`** shrink the button to its text; otherwise `MaterialButton` enforces 48dp and inflates the card.

**Where it applies:** any "button in the list row" — per-row delete, favorite, share. The same chain: interface in the adapter, method in the activity, translated position.

</details>

---

## Exercise 20.8 — A `Spinner` above the list for sorting

**Requirement:** Add a `Spinner` to `MainActivity`, above the list, with three options — "As added", "Title A-Z", "Rating (best first)". When the option changes, the list reorders.

**Files touched:** `res/values/strings.xml`, `res/layout/activity_main.xml`, `activities/MainActivity.java`.

**How you approach it — your steps:**
1. In `strings.xml`, add a `<string-array name="sort_options">` with the three texts, next to `movie_genre`.
2. In `activity_main.xml`, add a `Spinner` with `android:id="@+id/spSort"`, `android:layout_gravity="top|end"`, `android:layout_margin="16dp"`, `android:entries="@array/sort_options"` and `android:spinnerMode="dropdown"`.
3. The `ListView` already has `android:layout_marginTop="72dp"` if you did 20.4; if not, add it now.
4. In `MainActivity.java`, add the field `private Spinner spSort;` and the line in `initControls()`.
5. In `initListeners()`, attach `setOnItemSelectedListener` with both methods — `onItemSelected` calls `sortMovies(position)`, `onNothingSelected` stays empty.
6. Write `sortMovies(int mode)`: 0 → `refreshList()`, 1 → sort by title, 2 → sort by rating descending, then `notifyDataSetChanged()`.
7. Check: Run. Pick "Title A-Z": Inception, The Matrix, Toy Story. Pick "Rating (best first)": The Matrix (5), Inception (4.5), Toy Story (4). Pick "As added": the initial order.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 5</summary>

`Spinner` needs **two** methods in the listener, even if `onNothingSelected` does nothing. If you try it with a lambda, it doesn't compile — the interface isn't functional.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

sorting is done on `visibleMovies`, not on `movies`. `movies` keeps the insertion order, and "As added" restores it through `refreshList()`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a string-array with the options, a spinner in the top corner, a listener with two methods and a sort method with three branches.

**Code (XML + Java):**

`res/values/strings.xml` — next to `movie_genre`:

```xml
<string-array name="sort_options">
    <item>As added</item>
    <item>Title A-Z</item>
    <item>Rating (best first)</item>
</string-array>
```

`res/layout/activity_main.xml`:

```xml
<Spinner
    android:id="@+id/spSort"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="top|end"
    android:layout_margin="16dp"
    android:entries="@array/sort_options"
    android:spinnerMode="dropdown" />
```

`activities/MainActivity.java`:

```java
private Spinner spSort;

// initControls()
spSort = findViewById(R.id.spSort);

// initListeners()
spSort.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
    @Override
    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        sortMovies(position);
    }

    @Override
    public void onNothingSelected(AdapterView<?> parent) {
    }
});

// the new method
private void sortMovies(int mode) {
    if (mode == 0) {
        refreshList();
        return;
    }
    if (mode == 1) {
        visibleMovies.sort((a, b) -> a.getTitle().compareToIgnoreCase(b.getTitle()));
    } else if (mode == 2) {
        visibleMovies.sort((a, b) -> Float.compare(b.getRating(), a.getRating()));
    }
    movieAdapter.notifyDataSetChanged();
}
```

**Why:** `List.sort(Comparator)` reorders the list in place. The comparator receives two movies and returns a negative number if the first one comes first. For rating descending, we swap the arguments: `Float.compare(b, a)`.

**Remember:**
1. **`onItemSelected` is also called on startup, with position 0.** `sortMovies(0)` runs right after the listener is attached, without the user touching anything. That's normal.
2. **`compareToIgnoreCase` vs. `compareTo`:** the first treats "inception" and "Inception" the same; the second separates them by ASCII code, with capitals first.
3. **`Float.compare(b.getRating(), a.getRating())`** — if you write `(int)(b - a)`, the ratings 4.5 and 4.2 both become 0 and the order is arbitrary. Don't truncate floats in a comparator.
4. **The sort isn't preserved after filtering:** `refreshList()` rebuilds the list in the order from `movies`. If you want it to stay, call `sortMovies(spSort.getSelectedItemPosition())` at the end of `refreshList()`.
5. **`android:entries` is enough for a static spinner.** For options that change from code, you need an `ArrayAdapter<String>` and `setAdapter`.

**Where it applies:** any "sort by", "filter by", "pick a category". Only the comparator changes.

</details>

---

## Exercise 20.9 — `TextInputLayout` with `endIconMode="clear_text"` and what the clear does NOT do

**Requirement:** The teacher asks for a quick-clear button on the Title field. **Check the code first:** at `d719ffc`, `etTitle` already has `app:endIconMode="clear_text"` on its `TextInputLayout`. So the real requirement at the exam is to know how to put the attribute on any field — do it on `etBudget`, which doesn't have it — and to explain what it doesn't solve.

**Files touched:** `res/layout/activity_item.xml` (and, for the explanation, `activities/ItemActivity.java`).

**How you approach it — your steps:**
1. Open `activity_item.xml` and look for `etTitle`. Above it is a `TextInputLayout` with `app:endIconMode="clear_text"` as its last attribute. Confirm: the X button appears when the field has text.
2. Look for `etBudget` (Card 2, Production). Its `TextInputLayout` has `app:hintEnabled="false"` and `app:prefixText="$ "`, but no `endIconMode`.
3. Add `app:endIconMode="clear_text"` to the budget's `TextInputLayout` — not to the `TextInputEditText`.
4. Check: Run, open the form, type something into Budget. An X appears at the right end; tap it and the text disappears.
5. Press Save right after you emptied Budget: the app crashes with `NumberFormatException`. Note down why — that's the theory question.
6. Open `ItemActivity.java` and trace `saveMovie()`: `Double.parseDouble(etBudget.getText().toString())`. Confirm that the clear didn't touch anything else.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

the attribute sits on the `TextInputLayout`, not on the `TextInputEditText`. If you put it on the edit text, it's ignored without an error — and the button doesn't appear.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

`endIconMode` has fixed values: `clear_text`, `password_toggle`, `dropdown_menu`, `custom`, `none`. Anything else gives a build error, with the attribute's name.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the `endIconMode="clear_text"` attribute on the budget's `TextInputLayout`; the title already had it. Zero lines of Java.

**Code (XML + Java):**

`res/layout/activity_item.xml` — the budget block, with the new attribute marked:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:prefixText="$ "
    app:endIconMode="clear_text">   <!-- the new line -->

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etBudget"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Budget"
        android:inputType="numberDecimal" />
</com.google.android.material.textfield.TextInputLayout>
```

The title block, already in the code, for comparison:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Movie title"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

**Why:** `clear_text` is a mode of the `TextInputLayout`: it adds an `ImageButton` with an X automatically and, on press, calls `editText.setText("")`. You write no listener and keep no reference to the button.

**Remember — what the clear does NOT do:**
1. **It doesn't reset the model.** The `Movie` in `movies` stays untouched. The text in the field is only a working copy; the model changes only at `saveMovie()`.
2. **It doesn't reset `releaseCal`.** For `etRelease`, `saveMovie()` uses `releaseCal.getTime()`, not the text. If you clear the date text and press Save, the movie still gets the old date.
3. **It doesn't reset the other controls.** The SeekBar, the RatingBar, the switch, the checkbox, the radiogroup and the spinner stay exactly as they were. Each has its own reset: `setProgress`, `setRating`, `setChecked`, `check`, `setSelection`.
4. **It doesn't validate.** An empty field is perfectly valid for `TextInputLayout`; `Double.parseDouble("")` throws `NumberFormatException` only at Save.
5. **It doesn't save and doesn't close the screen.** It doesn't touch `setResult` and doesn't call `finish()`.
6. **It doesn't empty another field.** Each `TextInputLayout` has its own end icon; the X on Title knows nothing about Budget.

**Where it applies:** any text field. It's the cheapest point at the exam — one attribute, zero lines of Java — but also the easiest to explain wrong.

</details>

---

## Exercise 20.10 — The exam combination: the "Duplicate movie" button

**Requirement:** Add a "Duplicate movie" button to `ItemActivity` that saves the movie from the form twice: once normally and once more as a new entry in the list. The button also works when you're editing an existing movie.

**Files touched:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**How you approach it — your steps:**
1. In `activity_item.xml`, after `btnMovieAction` (and after `btnDelete`, if you did 20.3), add a `MaterialButton` with `android:id="@+id/btnDuplicate"`, style `OutlinedButton`, text "Duplicate movie".
2. In `ItemActivity`, extract the movie construction from `saveMovie()` into a `buildMovie()` method that returns a `Movie`.
3. `saveMovie()` becomes short: `Movie movie = buildMovie();` + Intent + `setResult`.
4. Add the field `btDuplicate`, the line in `initControls()` and the listener in `initListeners()`.
5. Write `duplicateMovie()`: put the movie into the Intent, put `DUPLICATE_EXTRA = true`, **without** `POSITION_EXTRA`, then `setResult(RESULT_OK, intent)` and `finish()`.
6. In `MainActivity`, add the constant `public static final String DUPLICATE_EXTRA = "duplicate";` next to the others.
7. In the callback, if `getBooleanExtra(DUPLICATE_EXTRA, false)` is true, add the movie twice.
8. Check: Run, fill in the form, press "Duplicate movie". Two identical rows appear in the list. Edit an existing movie and press "Duplicate movie": the list grows by one copy, the original movie stays.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 5</summary>

`RESULT_OK` alone can't say "add twice". You need a second information channel in the same Intent — a `boolean` extra. The result code stays `RESULT_OK`, because the operation is still a save.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 7</summary>

if you send `POSITION_EXTRA`, `MainActivity` takes the edit branch and replaces the existing movie, it doesn't add. For a duplicate, the position has to be missing — then `getIntExtra(POSITION_EXTRA, -1)` returns -1, that is "insert".

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** reading the form pulled out into a `buildMovie()` method, a new button that sends a flag instead of a position and a new branch in the callback.

**Code (XML + Java):**

`res/layout/activity_item.xml` — after `btnMovieAction`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnDuplicate"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Duplicate movie"
    app:icon="@android:drawable/ic_menu_add"
    app:iconGravity="textStart" />
```

`activities/ItemActivity.java`:

```java
private Button btDuplicate;

// initControls()
btDuplicate = findViewById(R.id.btnDuplicate);

// initListeners()
btDuplicate.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        duplicateMovie();
    }
});

// buildMovie() — the body of the old saveMovie(), without the Intent
private Movie buildMovie() {
    Movie movie = new Movie();
    movie.setTitle(etTitle.getText().toString());
    movie.setRelease(releaseCal.getTime());
    movie.setGenre(spGenre.getSelectedItem().toString());
    movie.setBudget(Double.parseDouble(etBudget.getText().toString()));
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
    return movie;
}

// saveMovie() becomes
private void saveMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, buildMovie());
    if (position != -1) {
        intent.putExtra(MainActivity.POSITION_EXTRA, position);
    }
    setResult(RESULT_OK, intent);
    finish();
}

// the new method
private void duplicateMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, buildMovie());
    intent.putExtra(MainActivity.DUPLICATE_EXTRA, true);
    setResult(RESULT_OK, intent);
    finish();
}
```

`activities/MainActivity.java`:

```java
public static final String DUPLICATE_EXTRA = "duplicate";

// in the launcher callback
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (intent.getBooleanExtra(DUPLICATE_EXTRA, false)) {
        movies.add(movie);
        movies.add(movie);
    } else if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    refreshList();   // or movieAdapter.notifyDataSetChanged()
}
```

**Why:** `buildMovie()` separates "read the form" from "what you do with the result". `saveMovie()` and `duplicateMovie()` use the same read, but send different results: one with a position (replaces), one with a flag (adds twice).

**Remember:**
1. **The two rows are the same object.** `movies.add(movie)` twice puts the same reference. When you edit one, the other stays on the old object, because `movies.set(position, movieNou)` only replaces the edited index. For independent copies, add a copy constructor to `Movie`:

```java
public Movie(Movie other) {
    this(other.title, other.release, other.genre, other.budget, other.duration,
         other.rating, other.watched, other.approval, other.onWatchlist, other.poster);
}
```

and in `MainActivity`: `movies.add(new Movie(movie)); movies.add(movie);`

2. **Without `POSITION_EXTRA`, the result is treated as an insert.** `getIntExtra(POSITION_EXTRA, -1)` returns -1, and the `position == -1` branch adds. You don't have to send anything special for "don't edit".
3. **The order of the branches matters.** `DUPLICATE_EXTRA` is checked before `position == -1`; otherwise the duplicate would go in only once.
4. **`buildMovie()` can throw `NumberFormatException`** if Budget is empty — just like `saveMovie()`. If you have time, put the check in `buildMovie()`, once for both buttons.
5. **The button is also useful in edit mode:** you duplicate the edited movie, with the values from the form, without changing the original.

**Where it applies:** exactly the format "another button that does something with the movie" — duplicate, save as draft, save and add to watchlist. The `buildMovie()` refactor is what saves you when the teacher asks for the second button that saves.

</details>

---

## Recap — the 10 requirements in one table

| # | Control | File | Listener | What passes between screens |
|---|---|---|---|---|
| 20.1 | `MaterialButton` | `activity_item.xml` | `setOnClickListener` | — |
| 20.2 | `FloatingActionButton` | `activity_main.xml` | `setOnClickListener` | — |
| 20.3 | `MaterialButton` | `activity_item.xml` | `setOnClickListener` | `RESULT_DELETE` + position |
| 20.4 | `MaterialSwitch` | `activity_main.xml` | `setOnCheckedChangeListener` | — |
| 20.5 | `Chip` | `movie_item.xml` | — (computed in `getView`) | — |
| 20.6 | `VectorDrawable` | `res/drawable/` | — | — |
| 20.7 | `MaterialButton` | `movie_item.xml` | `setOnClickListener` | position (through the interface) |
| 20.8 | `Spinner` | `activity_main.xml` | `setOnItemSelectedListener` | — |
| 20.9 | `TextInputLayout` | `activity_item.xml` | internal (`clear_text`) | — |
| 20.10 | `MaterialButton` | `activity_item.xml` | `setOnClickListener` | `RESULT_OK` + `DUPLICATE_EXTRA` |

> **The time trick:** seven of the ten exercises are "XML → `findViewById` → listener → action". Only 20.5 and 20.7 ask for an adapter, and 20.6 has no Java at all. If you get "put a button" at the exam, it's 20.1 or 20.2. If you get "put a button that deletes", it's 20.3. If you get "put a control that changes what you see in the list", it's 20.4 or 20.8.
