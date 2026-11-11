# Chapter 34 — Recipes 2: bindings and adapters

**Objective:** to solve in 10–15 minutes any requirement of the kind "bind value X to widget Y" or "make an adapter", on the **G1097 (Movies)** app, commit `d719ffc`. Each recipe has the exact steps, the minimal code that compiles, the mechanism behind it and the mistake that costs marks.

**Source:** `cod-final` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`, `strings.xml`. Every ID, method and field in the chapter exists exactly like that in these files.

**Path convention:** all paths are relative to `src/main/`. So `java/ro/ase/ie/g1097/activities/ItemActivity.java` means `app/src/main/java/ro/ase/ie/g1097/activities/ItemActivity.java`, and `res/layout/movie_item.xml` means `app/src/main/res/layout/movie_item.xml`.

---

## What a "binding" means for the exam

The word covers three different things, solved in different ways:

| Situation | Mechanism | Recipes |
|---|---|---|
| Widget → label, while the user is working | listener on the widget, `setText` in the callback | 34.1, 34.2, 34.4, 34.6 |
| Widget → model, on save | `getText()` / `getProgress()` / `isChecked()` + setter | 34.3, 34.5 |
| Model → list row | adapter: `ArrayAdapter`, `BaseAdapter` or `RecyclerView.Adapter` | 34.7–34.14 |

The first two are done in `ItemActivity` and cannot break the build: if you get them wrong, the app compiles and simply does not do what it should. The third is done in a new class and, written halfway, **does not compile at all**. That is why, in the exam, the order is: first the form requirement, then the adapter.

**Detail verified in the source:** `ItemActivity` uses `findViewById`, although `build.gradle.kts` has `buildFeatures { viewBinding = true }` and the file imports `ro.ase.ie.g1097.databinding.ActivityItemBinding`. The import is dead — it is used nowhere. In the exam you write `findViewById`, as in the repo.

**The 30-minute rule:** a simple binding = 5 minutes, one with validation = 10, an adapter = 15–20, the full migration = 25. If you are given two requirements, start with the one that cannot break the build.

**Three checks before any recipe:**

1. `setContentView(R.layout.activity_item)` runs **before** any `findViewById`. Otherwise you get a `NullPointerException`.
2. `initControls()` runs **before** `initListeners()` and **before** `fillForm(existing)`. This order appears explicitly in `onCreate`.
3. Every ID you write in Java must exist in the XML. An ID that exists in no layout gives a compile error (`cannot find symbol`). An ID that exists but belongs to another view compiles and returns `null` from `findViewById` — it crashes on the first touch. Check in the XML, not in autocomplete.

---

## Recipe 34.1 — Bind a value to a label, live

**The requirement, as it sounds in the test**

"Bind the label `tvDurationValue` to the slider `sbDuration`, so that the value updates live, in the form `148 min.`"

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `java/ro/ase/ie/g1097/activities/ItemActivity.java` | you add the listener on `sbDuration`, in `initListeners()` | **yes** |
| 2 | `res/layout/activity_item.xml` | nothing — `sbDuration` and `tvDurationValue` already exist | no, you only check |

**The steps, in order**

**Step 1 — check the widgets in the XML.** In `activity_item.xml`, the "Production" card contains:

```xml
<SeekBar
    android:id="@+id/sbDuration"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:max="300"
    android:min="0"
    android:progressTint="?attr/colorPrimary"
    android:thumbTint="?attr/colorPrimary"
    tools:progress="148" />
```

and, above it, the label:

```xml
<TextView
    android:id="@+id/tvDurationValue"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="0 min"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorPrimary"
    tools:text="148 min" />
```

Note: `android:text="0 min"` is the **design** text, written by hand. `tools:text="148 min"` is visible only in the Android Studio preview, not on the phone.

**Step 2 — the fields already exist.** In `ItemActivity.java`:

```java
private SeekBar sbDuration;
private TextView tvDurationValue;
```

**Step 3 — `findViewById` already exists.** In `initControls()`:

```java
sbDuration = findViewById(R.id.sbDuration);
tvDurationValue = findViewById(R.id.tvDurationValue);
```

**Step 4 — you add the binding.** In `initListeners()`, at the end of the method:

```java
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

The two empty methods are mandatory: `SeekBar.OnSeekBarChangeListener` has **three** abstract methods, so the anonymous class must implement all of them. You cannot use a lambda here — a lambda needs an interface with a **single** abstract method.

**Step 5 — check the order in `onCreate`.** It must be exactly this:

```java
initControls();
initListeners();

Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

`initListeners()` runs **before** `fillForm(existing)`. This makes the binding active at the moment `fillForm` calls `sbDuration.setProgress(148)`.

**Why it works this way**

A `SeekBar` has no "value" property that updates itself in the label. It has a listener with three methods, and `onProgressChanged` is called on **every** change of the progress — whether it comes from the user's finger (`fromUser = true`) or from code (`fromUser = false`). That is why, when `fillForm` does `sbDuration.setProgress(148)`, the label updates without `fillForm` knowing about it. The order in `onCreate` guarantees that the listener is registered before the first programmatic change.

**The mistake that costs marks**

1. **You write only `onStopTrackingTouch`.** Symptom: the label updates only when you lift your finger, and during the movement it lags behind. Cause: you put `setText` in the method that announces the **end** of the touch, not the change of value.
2. **You bind the wrong label.** Symptom: the "Duration" text disappears from the form. Cause: you wrote `tvDuration` (the static label next to the slider) instead of `tvDurationValue` (the value). Both start the same way.
3. **You move `initListeners()` after `fillForm`.** Symptom: the empty form works, but when editing a movie the label stays at "0 min". Cause: `setProgress(148)` ran before the listener existed.

**The check**

You run the app and open the empty form. The Duration label reads `0 min.` — **with a dot**, although the XML has `0 min` without one. The dot is the proof that your code ran, not the text from the XML. You move the slider: the number follows your finger, with no delay. You tap "Inception" in the list (duration 148): the label shows `148 min.` immediately, without touching the slider.

**Practise**

- [18.1](cap-18.html#ex-18-1) — exactly this binding, rewritten from memory.
- [19.1](cap-19.html#ex-19-1) — the same mechanism on `swWatched`.
- [19.4](cap-19.html#ex-19-4) — the same label, formatted as "1 h 22 min".

---

## Recipe 34.2 — Bind a value at initialisation

**The requirement, as it sounds in the test**

"When the form opens, the labels `tvDurationValue` and `tvWatchedValue` must start from the real state of the widgets, not from the text written in the XML."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `ItemActivity.java` | you add the `syncLabels()` method and call it in `initControls()` | **yes** |
| 2 | `ItemActivity.java` | you also call it at the end of `fillForm(...)` | **yes**, if you want it to be correct in edit mode too |
| 3 | `activity_item.xml` | nothing | no |

**The steps, in order**

**Step 1 — you write the method.** At the end of the `ItemActivity` class, after `showReleaseDatePicker()`:

```java
private void syncLabels() {
    tvDurationValue.setText(sbDuration.getProgress() + " min.");
    tvWatchedValue.setText(swWatched.isChecked() ? "Yes" : "No");
}
```

**Step 2 — you call it at initialisation.** In `initControls()`, after the last `findViewById`:

```java
private void initControls() {

    etTitle = findViewById(R.id.etTitle);
    etRelease = findViewById(R.id.etRelease);
    spGenre = findViewById(R.id.spGenre);
    etBudget = findViewById(R.id.etBudget);
    sbDuration = findViewById(R.id.sbDuration);
    rbRating = findViewById(R.id.rbRating);
    rgApproval = findViewById(R.id.rgApproval);
    cbonWatchList = findViewById(R.id.cbOnWatchList);
    swWatched = findViewById(R.id.swWatched);
    etPoster = findViewById(R.id.etPoster);
    btMovieAction = findViewById(R.id.btnMovieAction);
    tvDurationValue = findViewById(R.id.tvDurationValue);
    tvWatchedValue = findViewById(R.id.tvWatchedValue);

    syncLabels();
}
```

**Step 3 — you also call it after `fillForm`.** In edit mode, `fillForm` changes the state of the widgets **after** `initControls` has already run. Add the call at the end of the method:

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

    syncLabels();
}
```

**Why it works this way**

The text in the XML (`android:text="0 min"`, `android:text="No"`) is a **static** value, copied into every instance of the layout. The widget, on the other hand, has a state of its own: `getProgress()` and `isChecked()`. At startup, the two coincide by accident; after `fillForm`, they no longer do. A single method that reads the widget and writes the label, called at both moments, guarantees that the label never lies. You do not need a listener for this — you need a single point of truth.

**The mistake that costs marks**

1. **You call `syncLabels()` before `findViewById`.** Symptom: `NullPointerException` at startup, in `initControls`. Cause: you put the call at the beginning of the method, not at the end.
2. **You call it only in `initControls()`.** Symptom: the empty form is correct, but when editing "Inception" the label shows `0 min.` and `No`, although the slider is at 148 and the switch is on. Cause: `fillForm` changed the widgets after the labels had already been written.
3. **You rely on `android:text` from the XML.** Symptom: the label looks correct until the first change made from code. Cause: you confused the design text with the value.

**The check**

Empty form: `0 min.` and `No`. You tap "Inception" (148 minutes, watched): `148 min.` and `Yes`. You tap "The Matrix" (136 minutes, unwatched): `136 min.` and `No`. Between the two openings, the labels change **without** you moving anything — that shows `syncLabels()` runs on every opening.

**Practise**

- [18.1](cap-18.html#ex-18-1) — the listener variant, for comparison.
- [19.6](cap-19.html#ex-19-6) — what happens to the same values when the screen rotates.

---

## Recipe 34.3 — Read a widget into the model, on save

**The requirement, as it sounds in the test**

"When the Save button is pressed, build the `Movie` object by reading all the widgets in the form and send it back to `MainActivity`."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `ItemActivity.java` | you complete `saveMovie()` with one read line per widget | **yes** |
| 2 | `ItemActivity.java` | you check that `btMovieAction` has a listener that calls `saveMovie()` | **yes** |
| 3 | `Movie.java` | nothing — all the setters exist | no |

**The steps, in order**

**Step 1 — check the entry into the method.** In `initListeners()`:

```java
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveMovie();
    }
});
```

**Step 2 — write the body of `saveMovie()`.** The complete method, in `ItemActivity.java`:

```java
private void saveMovie() {
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

    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
    if (position != -1)
        intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_OK, intent);
    finish();
}
```

**Step 3 — check the reading table.** Each widget has exactly one read method, and the type matches the setter:

| Widget | Read | Type in `Movie` | Setter |
|---|---|---|---|
| `etTitle` | `getText().toString()` | `String` | `setTitle` |
| `etRelease` | `releaseCal.getTime()` | `Date` | `setRelease` |
| `spGenre` | `getSelectedItem().toString()` | `String` | `setGenre` |
| `etBudget` | `Double.parseDouble(getText().toString())` | `double` | `setBudget` |
| `sbDuration` | `getProgress()` | `int` | `setDuration` |
| `rbRating` | `getRating()` | `float` | `setRating` |
| `swWatched` | `isChecked()` | `boolean` | `setWatched` |
| `cbonWatchList` | `isChecked()` | `boolean` | `setOnWatchlist` |
| `etPoster` | `getText().toString()` | `String` | `setPoster` |
| `rgApproval` | you iterate the children until `isChecked()` | `String` | `setApproval` |

**Why it works this way**

The form is the only source of data at the moment of saving: there is no "half-built" `Movie` object to be updated. The method creates a new object with the no-argument constructor and fills it through setters, in an order that does not matter to the compiler but follows the order of the form. Then the object leaves through an `Intent`, and `MainActivity` receives it in its `launcher` callback and puts it in the list (`add`) or replaces it (`set`), depending on whether `position` is `-1` or not.

**The mistake that costs marks**

1. **Empty numeric field.** Symptom: the app closes on Save, with `NumberFormatException: For input string: ""`. Cause: `Double.parseDouble("")` throws, and you did not validate beforehand. The fix is recipe 34.5.
2. **The date read from text.** Symptom: the code does not compile, or the date is lost. Cause: you tried `new Date(etRelease.getText().toString())` — `Date` has no constructor from a `String`. The date lives in `releaseCal`, and `etRelease` only displays it.
3. **You forget `setResult(RESULT_OK, intent)`.** Symptom: the form closes, but the list does not change. Cause: the callback in `MainActivity` checks `o.getResultCode() == RESULT_OK` and ignores anything else.

**The check**

You fill in the form and press Save Movie. You return to the list, and the movie appears. In edit mode, the button reads "Update Movie", and on save the row changes its values without a new row appearing. You close the form with Back, without saving: the list stays unchanged.

**Practise**

- [17.1](cap-17.html#ex-17-1) — the same path, for a new attribute.
- [19.7](cap-19.html#ex-19-7) — what happens to the budget displayed as `1.6E8`.
- [19.8](cap-19.html#ex-19-8) — `fillForm` that crashes when `release` is `null`.

---

## Recipe 34.4 — Show or hide a widget conditionally

**The requirement, as it sounds in the test**

"The label `tvWatchedValue` must be visible only while the switch `swWatched` is on; when the switch is off, the label disappears completely."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `ItemActivity.java` | you add `setVisibility` in the switch's listener | **yes** |
| 2 | `ItemActivity.java` | you set the visibility at initialisation too, in `initControls()` | **yes** |
| 3 | `activity_item.xml` | nothing | no |

**The steps, in order**

**Step 1 — the listener, with both branches.** In `initListeners()`, you replace the existing listener with:

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
        tvWatchedValue.setVisibility(isChecked ? View.VISIBLE : View.GONE);
    }
});
```

**Step 2 — the initial state.** The listener is called only when the value **changes**. On opening, the switch is off and nothing changes, so the label would stay visible with the text "No". Add at the end of `initControls()`, after the `findViewById` calls:

```java
tvWatchedValue.setVisibility(swWatched.isChecked() ? View.VISIBLE : View.GONE);
```

**Step 3 — check the import.** `ItemActivity.java` already has `import android.view.View;` (it uses it in `onClick(View v)`). Nothing needs to be added.

**A type detail, verified in the source:** `swWatched` is declared in the XML as `com.google.android.material.materialswitch.MaterialSwitch`, and the field in `ItemActivity` has exactly the type `MaterialSwitch`. The file also imports `android.widget.Switch`, but the import is dead — there is no plain `Switch` in the app. The listener works because `MaterialSwitch` extends `SwitchCompat`, which extends `CompoundButton`; that is why the parameter type in `onCheckedChanged` is `CompoundButton`, not `MaterialSwitch`.

**Why it works this way**

`setVisibility(int)` changes the way the view takes part in the layout. `View.VISIBLE` shows it, `View.INVISIBLE` hides it but keeps its space, `View.GONE` removes it from the calculation completely — the row shrinks and the views below it move up. The listener catches only the **changes**, not the state at startup, which is why the second call is needed, made once, in `initControls()`. The two calls are independent: one is for the user, the other for the first display.

**The mistake that costs marks**

1. **Only the `VISIBLE` branch.** Symptom: the label appears when you turn the switch on, but no longer disappears when you turn it off. Cause: you wrote `if (isChecked) { setVisibility(View.VISIBLE); }` without an `else`. It is the same mistake that, in an adapter, makes recycled rows keep the previous movie's status.
2. **`View.INVISIBLE` instead of `View.GONE`.** Symptom: the label is not visible, but under "Recommended" a one-line gap remains, and the card does not shrink. Cause: `INVISIBLE` keeps the space.
3. **No step 2.** Symptom: on opening, the "No" label is visible although the switch is off; only after you press the switch twice does it disappear. Cause: you thought the listener also runs at initialisation.

**The check**

You open the empty form: under "Recommended" no "No" appears — the row has only the label and the switch. You turn the switch on: "Yes" appears, and the row grows. You turn it off: "Yes" disappears and the row shrinks back. You open "Inception" (watched): the label is visible from the start, because `fillForm` turned the switch on.

**Practise**

- [17.8](cap-17.html#ex-17-8) — a chip that appears only under a condition.
- [18.9](cap-18.html#ex-18-9) — the approval chip, bound and hidden with `View.GONE`.

---

## Recipe 34.5 — Validation with an error message

**The requirement, as it sounds in the test**

"On Save, if the title is empty or the budget is not a number, saving stops and the guilty field shows an error message."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `ItemActivity.java` | you add the `validateForm()` method | **yes** |
| 2 | `ItemActivity.java` | you call `validateForm()` at the start of `saveMovie()` | **yes** |
| 3 | `activity_item.xml` | nothing — `etTitle` and `etBudget` already have an ID | no |

**The steps, in order**

**Step 1 — you write the validation.** In `ItemActivity.java`, above `saveMovie()`:

```java
private boolean validateForm() {
    etTitle.setError(null);
    etBudget.setError(null);

    String title = etTitle.getText().toString().trim();
    if (title.isEmpty()) {
        etTitle.setError("The title is required");
        etTitle.requestFocus();
        return false;
    }

    String budget = etBudget.getText().toString().trim();
    if (budget.isEmpty()) {
        etBudget.setError("The budget is required");
        etBudget.requestFocus();
        return false;
    }

    try {
        Double.parseDouble(budget);
    } catch (NumberFormatException e) {
        etBudget.setError("The budget must be a number");
        etBudget.requestFocus();
        return false;
    }

    return true;
}
```

The first two lines clear the errors from the previous press: `setError(null)` hides the icon. Without them, the message stays on the field even after the user has corrected it. In `showReleaseDatePicker()` the same pattern already exists, on `etRelease`.

**Step 2 — you call it first.** `saveMovie()`, the complete method:

```java
private void saveMovie() {
    if (!validateForm()) {
        return;
    }

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

    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
    if (position != -1)
        intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_OK, intent);
    finish();
}
```

**Step 3 — check the order.** The guard must be the **first** statement in `saveMovie()`, before `Double.parseDouble(...)`. If you moved the validation lower — for example right after `movie.setBudget(...)` — the exception would be thrown before the message reached the screen, and the app would close.

**Why it works this way**

`setError(CharSequence)` is a method of `TextView`: it attaches an error message to the view, and Android shows a red icon on the right and a popup with the text. It stops nothing by itself — that is why `validateForm()` returns `boolean` and `saveMovie()` exits immediately with `return`. `requestFocus()` moves the focus to the guilty field, and the `ScrollView` in `activity_item.xml` usually scrolls to it. The order matters: the validation runs **before** `Double.parseDouble`, otherwise the exception thrown by the parsing arrives before your message.

**The mistake that costs marks**

1. **You validate after parsing.** Symptom: the app closes with `NumberFormatException` before you get to see the message. Cause: `Double.parseDouble` is called higher up in the method than `validateForm()`.
2. **You show the error but save anyway.** Symptom: the red icon appears, but the movie is saved anyway and the screen closes. Cause: you forgot the `return` after `setError`.
3. **You do not use `trim()`.** Symptom: a field with a single space passes validation, and a movie with the title " " appears in the list. Cause: `" ".isEmpty()` is `false`.

**The check**

You delete the title and press Save: you stay on the form, the Title field has a red icon and the message "The title is required". You type a title, delete the budget, press Save: the error moves to Budget. You fill in both and press Save: you return to the list and the movie appears. The message disappears by itself when you press Save again after correcting.

**Practise**

- [17.7](cap-17.html#ex-17-7) — the required field, the complete variant.
- [19.10](cap-19.html#ex-19-10) — exam combo: value in the label plus a validation error.

---

## Recipe 34.6 — Synchronise two widgets

**The requirement, as it sounds in the test**

"When the switch `swWatched` is on, tick `cbOnWatchList` automatically; when it is off, untick it."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `ItemActivity.java` | you add `cbonWatchList.setChecked(isChecked)` in the switch's listener | **yes** |
| 2 | `ItemActivity.java` | you reverse the order of two lines in `fillForm(...)` | **yes**, otherwise editing corrupts the data |
| 3 | `activity_item.xml` | nothing | no |

**The steps, in order**

**Step 1 — the synchronisation, in one direction only.** In `initListeners()`:

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
        cbonWatchList.setChecked(isChecked);
    }
});
```

One direction only: the switch commands, the checkbox listens. You do not also put a listener on the checkbox that turns the switch on.

**Step 2 — you fix the order in `fillForm`.** The current code has, in this order:

```java
cbonWatchList.setChecked(existing.isOnWatchlist());
swWatched.setChecked(existing.isWatched());
```

After step 1, `swWatched.setChecked(...)` triggers the listener, which writes into the checkbox — so the value from the model is overwritten. Reverse them:

```java
swWatched.setChecked(existing.isWatched());
cbonWatchList.setChecked(existing.isOnWatchlist());
```

Now the switch is set first (and possibly overwrites the checkbox), and the checkbox receives the value from the model at the end. The last one to write wins, and the last one is the model.

**Why it works this way**

Unlike `SeekBar`, where the listener receives `fromUser`, `CompoundButton.OnCheckedChangeListener` has **no** such parameter: `setChecked(...)` from code triggers the listener exactly like a user touch. That is why the synchronisation propagates from `fillForm` too. Android does not call the listener again if the requested value is identical to the current one (`setChecked` checks first), which makes the chain stop by itself after one step — provided there is only one direction.

**The mistake that costs marks**

1. **Synchronisation in both directions.** Symptom: you press the switch, the checkbox gets ticked, but the switch jumps back to off — or the two stay in different states. Cause: you put a listener on the checkbox too, which commands the switch. Android blocks re-entry on the **same** button, but not between two different buttons, so the result depends on the order in which the calls propagate. The simple rule: one direction only, and the second widget just listens.
2. **You do not fix the order in `fillForm`.** Symptom: you edit "Inception" (watched, but not on the watchlist), press Save without touching anything, and the movie now appears on the watchlist too. Cause: `swWatched.setChecked(true)` ran after `cbonWatchList.setChecked(false)` and ticked the checkbox through the listener.
3. **You put the synchronisation in `saveMovie()`.** Symptom: in the list the values are correct, but in the form the checkbox does not move when you press the switch. Cause: the synchronisation must be in the listener, not at save time.

**The check**

You open the empty form: you turn the switch on → the Watchlist checkbox ticks itself. You turn it off → it unticks. You open "Inception" (watched, not on the watchlist): the switch is on, the checkbox stays unticked — the model was not altered. You open "The Matrix" (unwatched, on the watchlist): the switch is off, the checkbox stays ticked. You press Save without changes: in the list, the chips stay the same.

**Practise**

- [19.1](cap-19.html#ex-19-1) — the label that follows the switch.
- [18.1](cap-18.html#ex-18-1) — the same kind of binding, on a `SeekBar`.

---

## Recipe 34.7 — ArrayAdapter with toString()

**The requirement, as it sounds in the test**

"Display the list of movies in a `ListView` using `ArrayAdapter` and explain why each row shows `Movie{title='Inception', ...}`."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `MainActivity.java` | the `ArrayAdapter<Movie>` field, its construction, `setAdapter` | **yes** |
| 2 | `MainActivity.java` | `notifyDataSetChanged()` after `add` / `set` | **yes** |
| 3 | `activity_main.xml` | nothing — `listView` already exists | no |
| 4 | `movie_item.xml` | nothing — it is **not used** in this variant | no |

**The steps, in order**

**Step 1 — the field.** In `MainActivity.java`, next to the other fields:

```java
private ListView listView;
private final List<Movie> movies = new ArrayList<>();
private ArrayAdapter<Movie> movieAdapter;
```

**Step 2 — you build the adapter, after the list has data.** In `onCreate`, right after `addSampleMovies()`:

```java
addSampleMovies();

movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
initControls();
initListeners();
```

The order in the repo is: first the data, then the adapter. Not because something would crash otherwise, but because that is how the chain reads correctly. The adapter receives the **reference** to the list, not a copy, and `ListView` asks `getCount()` only at the first layout, after `onCreate` has finished — so the reverse order would display the full list too. The difference appears only if you modify the list after the first layout: then you would need `notifyDataSetChanged()`.

**Step 3 — you attach it to the list.** In `initControls()`:

```java
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    listView = findViewById(R.id.listView);
    listView.setAdapter(movieAdapter);
}
```

**Step 4 — you notify after every change.** In the `launcher` callback:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

**Why it works this way**

`ArrayAdapter` is an adapter ready-made for the simplest case: a list of objects and a row with **a single `TextView`**. The layout `android.R.layout.simple_list_item_1` has exactly a `TextView` as its root, and when it is not given a field ID, `ArrayAdapter` uses the root of the row as the text. Because the elements are of type `Movie`, not `String`, the adapter has no text to put there directly — so it calls `toString()` on each element. `Movie.toString()` is generated by IntelliJ and prints all ten fields, hence the long row you see. The `movies` list is the same instance the activity holds, but `ListView` does not observe changes in it: that is why `notifyDataSetChanged()` is mandatory after `add` and `set`.

**The mistake that costs marks**

1. **You forget `notifyDataSetChanged()`.** Symptom: you save a movie, return to the list and nothing has changed; you close and reopen the app and the movie appears. Cause: the list changed, but `ListView` was not told.
2. **You forget `setAdapter`.** Symptom: the list shows `Item 1` … `Item 20`, not the movies. Cause: `activity_main.xml` has `android:entries="@array/items"`, and `ListView` builds an adapter for itself from that array when it is not given another one. The 20 entries are exactly the `string-array` named `items` in `strings.xml`.
3. **You put `R.layout.movie_item` instead of `android.R.layout.simple_list_item_1`.** Symptom: `IllegalStateException: ArrayAdapter requires the resource ID to be a TextView`, on the first display. Cause: the root of `movie_item.xml` is a `MaterialCardView`, not a `TextView`, and `ArrayAdapter` tries to treat the whole row as a `TextView`. For that layout you need an adapter of your own — recipe 34.8.

**The check**

You run the app: three rows, each a long string that starts with `Movie{title='Inception'` and continues with `release=…, genre='Sci-Fi', budget=1.6E8, …`. You press the FAB, fill in, save: the fourth row appears at the end. You tap a row: the form opens with the movie's data, and on save the row changes its text without a new one appearing.

**Practise**

- [18.8](cap-18.html#ex-18-8) — `Inception (2010)`: `toString()` or an adapter of your own?
- [24.1](cap-24.html#ex-24-1) — what exactly happens if you forget `notifyDataSetChanged()`.
- [24.2](cap-24.html#ex-24-2) — why `set` and not `add` when editing.

---

## Recipe 34.8 — BaseAdapter with a ViewHolder

**The requirement, as it sounds in the test**

"Replace `ArrayAdapter` with a `BaseAdapter` of your own, which fills the card from `movie_item.xml`: title, subtitle, rating, facts and the three chips."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` | new file: the complete class | **yes** |
| 2 | `MainActivity.java` | you change the field type and the construction of the adapter | **yes** |
| 3 | `res/layout/movie_item.xml` | nothing — it is complete, you only use it | no |

**The steps, in order**

**Step 1 — you create the package and the file.** Right-click on `ro.ase.ie.g1097` → `New → Package`, name `adapters`. In it, `New → Java Class`, name `MovieListAdapter`.

**Step 2 — you write the complete class.** `MovieListAdapter.java`:

```java
package ro.ase.ie.g1097.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.RatingBar;
import android.widget.TextView;

import com.google.android.material.chip.Chip;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieListAdapter extends BaseAdapter {

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private static class ViewHolder {
        TextView movieTitle;
        TextView movieSubtitle;
        RatingBar movieRating;
        TextView movieRatingValue;
        TextView movieFacts;
        Chip chipApproval;
        Chip chipWatched;
        Chip chipWatchlist;
    }

    private final List<Movie> movies;
    private final LayoutInflater layoutInflater;

    public MovieListAdapter(Context context, List<Movie> movies) {
        this.layoutInflater = LayoutInflater.from(context);
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
            convertView = layoutInflater.inflate(R.layout.movie_item, parent, false);
            holder = new ViewHolder();
            holder.movieTitle = convertView.findViewById(R.id.movieTitle);
            holder.movieSubtitle = convertView.findViewById(R.id.movieSubtitle);
            holder.movieRating = convertView.findViewById(R.id.movieRating);
            holder.movieRatingValue = convertView.findViewById(R.id.movieRatingValue);
            holder.movieFacts = convertView.findViewById(R.id.movieFacts);
            holder.chipApproval = convertView.findViewById(R.id.chipApproval);
            holder.chipWatched = convertView.findViewById(R.id.chipWatched);
            holder.chipWatchlist = convertView.findViewById(R.id.chipWatchlist);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        bind(holder, getItem(position));
        return convertView;
    }

    private void bind(ViewHolder holder, Movie movie) {
        holder.movieTitle.setText(movie.getTitle());

        String year = movie.getRelease() != null
                ? YEAR_FORMAT.format(movie.getRelease())
                : "";
        holder.movieSubtitle.setText(movie.getGenre() + " · " + year);

        holder.movieRating.setRating(movie.getRating());
        holder.movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

        holder.movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
                movie.getDuration(), movie.getBudget() / 1_000_000));

        String approval = movie.getApproval();
        if (approval != null && !approval.isEmpty()) {
            holder.chipApproval.setText(approval);
            holder.chipApproval.setVisibility(View.VISIBLE);
        } else {
            holder.chipApproval.setVisibility(View.GONE);
        }
        holder.chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
        holder.chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
    }
}
```

**Step 3 — you change the adapter in the activity.** In `MainActivity.java`:

```java
import ro.ase.ie.g1097.adapters.MovieListAdapter;

private MovieListAdapter movieAdapter;
```

In `onCreate`:

```java
movieAdapter = new MovieListAdapter(this, movies);
```

In `initControls()`, the line stays the same:

```java
listView.setAdapter(movieAdapter);
```

The notifications stay `movieAdapter.notifyDataSetChanged();` — `BaseAdapter` has the method, like any adapter.

**Step 4 — you delete the import that has become useless.** `import android.widget.ArrayAdapter;` is no longer used. It does not block the build, but it leaves a warning.

**Why it works this way**

`BaseAdapter` is the base class for any `ListView` adapter. It has a single truly mandatory method — `getView` — plus `getCount`, which you must implement so that it says how many rows exist. `ListView` does not create a row for each element: it creates only as many as fit on the screen and **recycles** them while scrolling, sending them back into `getView` through the `convertView` parameter. If `convertView` is `null`, the row must be inflated from the XML; if not, you reuse it. To avoid looking up the eight views with `findViewById` on every reuse, you put them in a `ViewHolder` object and attach it to the row with `setTag`. On reuse, `getTag()` gives you exactly last time's object.

**The mistake that costs marks**

1. **You forget `convertView.setTag(holder)`.** Symptom: `NullPointerException` in `getView`, on the first scroll, on the line `holder.movieTitle`. Cause: the `else` branch receives a recycled row, but `getTag()` returns `null`.
2. **Inflated with `null` instead of `parent`.** Symptom: the card does not stretch across the full width, and `layout_marginHorizontal` seems ignored. Cause: `inflate(R.layout.movie_item, null)` has nowhere to take the parent's `LayoutParams` from. The correct form is `inflate(R.layout.movie_item, parent, false)`.
3. **Chips without the `else` branch.** Symptom: you scroll the list, and a movie that is not on the watchlist appears with the "Watchlist" chip lit. Cause: the recycled row keeps the visibility from the previous movie. Each chip needs **both** branches, `VISIBLE` and `GONE`.

**The check**

You run it: three cards. The first: "Inception", "Sci-Fi · 2010", 4.5 stars, "148 min  ·  $160M", the chips `PG-13` and `Watched`. The second: "Toy Story", "Animation · 1995", 4.0, "81 min  ·  $30M", `G` and `Watched`. The third: "The Matrix", "Action · 1999", 5.0, "136 min  ·  $63M", `R` and `Watchlist`. You add a movie: the fourth card appears at the end, with its data.

**Practise**

- [18.4](cap-18.html#ex-18-4) — the second line in the `ListView` row.
- [18.6](cap-18.html#ex-18-6) — the poster URL in a `TextView` in the same card.

---

## Recipe 34.9 — RecyclerView.Adapter from scratch

**The requirement, as it sounds in the test**

"Write from scratch a `RecyclerView.Adapter` that displays the movies in `movie_item.xml`, with `ViewHolder`, `onCreateViewHolder`, `onBindViewHolder` and `getItemCount`."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `adapters/MovieAdapter.java` | new file: the complete class | **yes** |
| 2 | `activity_main.xml` | you replace `<ListView>` with `<androidx.recyclerview.widget.RecyclerView>` | **yes** |
| 3 | `MainActivity.java` | `setLayoutManager` + `setAdapter` | **yes** |
| 4 | `gradle/libs.versions.toml`, `build.gradle.kts` | the `androidx.recyclerview` dependency | **yes**, if it is not already added |

**The steps, in order**

**Step 1 — the dependency.** `RecyclerView` does not come with `appcompat`, unlike `ListView`. In `gradle/libs.versions.toml`:

```toml
[versions]
recyclerview = "1.4.0"

[libraries]
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

In `build.gradle.kts`, in `dependencies { }`:

```kotlin
implementation(libs.recyclerview)
```

Then `Sync Now`.

**Step 2 — the widget in the layout.** In `activity_main.xml`, `<ListView>` becomes:

```xml
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

The ID stays `listView`. An ID is just a name: you can keep it so as not to touch `findViewById`. The Java field, however, is renamed to `recyclerView`, because it now holds a different type of object.

**Step 3 — the adapter class.** `MovieAdapter.java`:

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

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) {
        this.movies = movies;
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
        holder.bind(movies.get(position));
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

        public void bind(Movie movie) {
            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);

            movieRating.setRating(movie.getRating());
            movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

            movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
                    movie.getDuration(), movie.getBudget() / 1_000_000));

            String approval = movie.getApproval();
            if (approval != null && !approval.isEmpty()) {
                chipApproval.setText(approval);
                chipApproval.setVisibility(View.VISIBLE);
            } else {
                chipApproval.setVisibility(View.GONE);
            }
            chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
            chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
        }
    }
}
```

**Step 4 — attaching it, in `MainActivity`.** Three lines, all mandatory:

```java
private RecyclerView recyclerView;
private MovieAdapter movieAdapter;

// in onCreate, after addSampleMovies()
movieAdapter = new MovieAdapter(movies);

// in initControls()
recyclerView = findViewById(R.id.listView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));
recyclerView.setAdapter(movieAdapter);
```

The imports: `androidx.recyclerview.widget.LinearLayoutManager`, `androidx.recyclerview.widget.RecyclerView`, `ro.ase.ie.g1097.adapters.MovieAdapter`.

**Step 5 — the notification.** After `movies.add(movie)` or `movies.set(position, movie)`:

```java
movieAdapter.notifyDataSetChanged();
```

`notifyItemInserted` works too, but the difference is discussed in recipe 34.14.

**Why it works this way**

`RecyclerView.Adapter` splits `getView` in two, to separate the expensive work from the cheap work. `onCreateViewHolder` runs once per row built: it inflates the XML and looks up the views. `onBindViewHolder` runs on every display of a row, including after recycling: it only writes the values. `getItemCount` says how many rows exist. `ViewHolder` is no longer optional and no longer needs `setTag` — `RecyclerView` holds it itself. On the other hand, `RecyclerView` does not know **how** to arrange the rows: that is why it needs a `LayoutManager`, which is set separately and mandatorily.

**The mistake that costs marks**

1. **You forget `setLayoutManager`.** Symptom: white screen, with no error in Logcat. Cause: `RecyclerView` has an adapter, but there is no one to measure and place the rows. It is the most expensive mistake in the chapter, because it leaves no trace.
2. **`getItemCount()` does not match the list.** Symptom: `IndexOutOfBoundsException` while scrolling, not at startup. Cause: you returned `movies.size() + 1` or forgot to update the method after changing the data source.
3. **`onCreateViewHolder` returns `null`.** Symptom: `NullPointerException` in `RecyclerView`, right after startup. Cause: you wrote the method so that it compiles, without returning a `ViewHolder`.

**The check**

You run it: three cards, identical to those in recipe 34.8. You scroll (if you have more movies): the rows are reused, without flickering. You press the FAB, save: the fourth card appears. Click on a card: for now nothing happens — the click is wired in recipe 34.13.

**Practise**

- [23.3](cap-23.html#ex-23-3) — the adapter skeleton, step by step.
- [23.4](cap-23.html#ex-23-4) — `MovieViewHolder` with the fields from `movie_item.xml`.
- [23.5](cap-23.html#ex-23-5) — `onCreateViewHolder` with `inflate`.
- [18.5](cap-18.html#ex-18-5) — the full migration, in a single exam answer.

---

## Recipe 34.10 — Full migration ListView → RecyclerView

**The requirement, as it sounds in the test**

"Migrate the list from `ListView` to `RecyclerView`: add the dependency, change the layout, write the adapter and wire it in the activity."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `gradle/libs.versions.toml` | the `recyclerview` version and library | **yes** |
| 2 | `build.gradle.kts` | `implementation(libs.recyclerview)` | **yes** |
| 3 | `res/layout/activity_main.xml` | `<ListView>` → `<androidx.recyclerview.widget.RecyclerView>` | **yes** |
| 4 | `adapters/MovieAdapter.java` | new file, with a `ViewHolder` and a click callback | **yes** |
| 5 | `MainActivity.java` | the field type, `LayoutManager`, `setAdapter`, `notifyItem*` | **yes** |
| 6 | `movie_item.xml` | nothing — it finally becomes used | no |

**The steps, in order**

**Step 1 — the dependency.** `gradle/libs.versions.toml`, at the end of the `[versions]` section:

```toml
recyclerview = "1.4.0"
```

In `[libraries]`, under `coordinatorlayout`:

```toml
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

`build.gradle.kts`, in `dependencies { }`, after `implementation(libs.material)`:

```kotlin
implementation(libs.recyclerview)
```

`Sync Now`, then `Build → Make Project`. You must get `BUILD SUCCESSFUL`, and `androidx.recyclerview:recyclerview:1.4.0` must appear in `External Libraries`.

**Step 2 — the layout.** In `activity_main.xml`, you replace the `<ListView … />` block with:

```xml
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

Two things change and two stay:

- the **tag** changes — `<ListView>` becomes `<androidx.recyclerview.widget.RecyclerView>`;
- `android:entries="@array/items"` disappears — it is a `ListView` attribute; on `RecyclerView` it has no effect, and the rows come from the adapter anyway;
- `layout_width` / `layout_height` stay on `match_parent`;
- the **ID** `listView` stays. An ID is just a name, and keeping it means `findViewById(R.id.listView)` does not need to be touched. The Java field is renamed to `recyclerView`, because it now holds a `RecyclerView` — the field name and the XML ID are independent. If you do want to rename the ID as well, use `Refactor → Rename`: a manual rename only in the XML leaves `R.id.listView` in Java and the build fails.

**Step 3 — the adapter.** `adapters/MovieAdapter.java`, complete file:

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
            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);

            movieRating.setRating(movie.getRating());
            movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

            movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
                    movie.getDuration(), movie.getBudget() / 1_000_000));

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

**Step 4 — `MainActivity`, the fields and imports.** You remove `android.widget.AdapterView`, `android.widget.ArrayAdapter` and `android.widget.ListView`; you add:

```java
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.g1097.adapters.MovieAdapter;
```

The fields become:

```java
private FloatingActionButton fabInsert;
private RecyclerView recyclerView;
private ActivityResultLauncher<Intent> launcher;
private final List<Movie> movies = new ArrayList<>();
private MovieAdapter movieAdapter;
```

**Step 5 — `onCreate`.** Building the adapter and the callback:

```java
addSampleMovies();

movieAdapter = new MovieAdapter(movies, this::openItem);
initControls();
initListeners();

launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
        new ActivityResultCallback<ActivityResult>() {
            @Override
            public void onActivityResult(ActivityResult o) {
                if (o.getResultCode() == RESULT_OK) {
                    Intent intent = o.getData();
                    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
                    int position = intent.getIntExtra(POSITION_EXTRA, -1);
                    if (position == -1) {
                        movies.add(movie);
                        movieAdapter.notifyItemInserted(movies.size() - 1);
                    } else {
                        movies.set(position, movie);
                        movieAdapter.notifyItemChanged(position);
                    }
                }
            }
        });
```

**Step 6 — `initControls`.** The three mandatory lines:

```java
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    recyclerView = findViewById(R.id.listView);
    recyclerView.setLayoutManager(new LinearLayoutManager(this));
    recyclerView.setAdapter(movieAdapter);
}
```

**Step 7 — `initListeners`.** The `listView.setOnItemClickListener(...)` block disappears completely: `RecyclerView` has no such thing, and if you leave it, it does not even compile, because `recyclerView` is another type. Only the FAB remains:

```java
private void initListeners() {
    fabInsert.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            launcher.launch(intent);
        }
    });
}
```

**Step 8 — the click method.** You add it in `MainActivity`:

```java
private void openItem(int position) {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
}
```

**Why it works this way**

The migration moves three responsibilities out of `ListView` into three separate places. The arrangement of the rows moves into the `LayoutManager`; the building and filling of the row move into the adapter; the click moves from a listener of the list into a callback of the adapter, because `RecyclerView` has no `setOnItemClickListener`. `movie_item.xml` was prepared exactly for this: it existed in the project, but no `findViewById`, no `LayoutInflater` and no adapter referred to it. Now it becomes the row of the list, and `ArrayAdapter` disappears together with `toString()`.

**The mistake that costs marks**

1. **You forget `setLayoutManager`.** Symptom: white screen, FAB visible, zero errors. Cause: a `RecyclerView` without a `LayoutManager` has no one to arrange the rows. It does not show in Logcat, it does not show in the build — only on the screen.
2. **`notifyItemInserted(movies.size())`.** Symptom: `IndexOutOfBoundsException: Inconsistency detected`, only when you insert, not at startup. Cause: after `add`, the last valid index is `movies.size() - 1`.
3. **`listView.setOnItemClickListener(...)` stays in `initListeners`.** Symptom: `cannot find symbol: method setOnItemClickListener`. Cause: you changed the field type to `RecyclerView` but left the old code. Delete the whole block, not just the line inside it.

**The check**

You run it: the list looks exactly as before the migration, but with cards, not long text. Click on "Inception": the form opens with its data, the button reads "Update Movie". You change the rating, save: only that card changes, with a short animation. FAB, new movie, Save: the new card appears at the end, with an insertion animation. You scroll down and up: the position is kept.

**Practise**

- [23.1](cap-23.html#ex-23-1) — the dependency, in isolation.
- [23.2](cap-23.html#ex-23-2) — `ListView` → `RecyclerView` in the layout.
- [23.10](cap-23.html#ex-23-10) — `LayoutManager`, `setAdapter`, `notifyItem*`.
- [18.5](cap-18.html#ex-18-5) — the same migration, in a single piece.

---

## Recipe 34.11 — GridLayoutManager, two columns

**The requirement, as it sounds in the test**

"Display the movies in two columns, without modifying the adapter and without touching the row layout."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `MainActivity.java` | you replace `LinearLayoutManager` with `GridLayoutManager` | **yes** |
| 2 | `adapters/MovieAdapter.java` | nothing | no |
| 3 | `res/layout/movie_item.xml` | nothing | no |

**The steps, in order**

**Step 1 — the import.** In `MainActivity.java`:

```java
import androidx.recyclerview.widget.GridLayoutManager;
```

**Step 2 — a single line.** In `initControls()`, you replace:

```java
recyclerView.setLayoutManager(new LinearLayoutManager(this));
```

with:

```java
recyclerView.setLayoutManager(new GridLayoutManager(this, 2));
```

**Step 3 — you check that you have touched nothing else.** The adapter stays `MovieAdapter`, the row stays `movie_item.xml`, `setAdapter` stays the same. If you felt the need to change something in `bind`, you have gone outside the requirement.

**Why it works this way**

The `LayoutManager` is the only one responsible for arranging the rows. `GridLayoutManager` extends `LinearLayoutManager` and divides the available width into `spanCount` columns; each row receives the width of one column, and `RecyclerView` works out by itself how many rows fit. The adapter does not know and must not know how many columns exist — it still receives positions from 0 to `getItemCount() - 1` and fills the same card. That is why the change is one line, not a rewrite.

**The mistake that costs marks**

1. **`new GridLayoutManager(this, 0)`.** Symptom: `IllegalArgumentException: spanCount should be at least 1`, when the screen opens. Cause: the number of columns must be at least 1.
2. **You build the manager but forget to attach it.** Symptom: white screen, no error. Cause: you wrote `new GridLayoutManager(this, 2);` as a standalone statement, instead of `recyclerView.setLayoutManager(new GridLayoutManager(this, 2));`.
3. **You put `GridLayoutManager` on a `ListView`.** Symptom: it does not compile. Cause: `ListView` has a different arrangement system; the recipe assumes you have already done the migration from 34.10.

**The check**

You run it: the three movies appear two per row — "Inception" and "Toy Story" on top, "The Matrix" alone on the second row, on the left. Each card has half the width, and the 96dp poster remains visible. You add a movie: the second column of the last row is filled. You turn the phone to landscape: you still see two columns, wider.

**Practise**

- [18.7](cap-18.html#ex-18-7) — `LinearLayoutManager` → `GridLayoutManager`, with the on-screen check.

---

## Recipe 34.12 — Header in the list (two row types)

**The requirement, as it sounds in the test**

"The first row of the list must be a header that displays the number of movies; the rest of the rows remain the usual cards."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `adapters/MovieAdapter.java` | the type constants, `getItemViewType`, `getItemCount`, `onCreateViewHolder`, `onBindViewHolder`, `HeaderViewHolder` | **yes** |
| 2 | `adapters/MovieAdapter.java` | the `- 1` offset in `bind` and in the click callback | **yes** |
| 3 | `MainActivity.java` | nothing — `openItem` receives the whole index from the list | no |

**The steps, in order**

**Step 1 — two constants and the generic type.** At the top of `MovieAdapter`, next to the fields:

```java
private static final int TYPE_HEADER = 0;
private static final int TYPE_MOVIE = 1;
```

The class declaration changes from `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>` to:

```java
public class MovieAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {
```

The reason: the adapter now produces **two** types of `ViewHolder`, so the generic type must be their common ancestor.

**Step 2 — the row count includes the header.** `getItemCount()`:

```java
@Override
public int getItemCount() {
    return movies.size() + 1;
}
```

**Step 3 — you say what type each position has.** The new method:

```java
@Override
public int getItemViewType(int position) {
    return position == 0 ? TYPE_HEADER : TYPE_MOVIE;
}
```

**Step 4 — you build the right row.** `onCreateViewHolder`:

```java
@NonNull
@Override
public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
    if (viewType == TYPE_HEADER) {
        TextView header = new TextView(parent.getContext());
        header.setTextSize(16f);
        header.setPadding(32, 32, 32, 16);
        return new HeaderViewHolder(header);
    }

    View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.movie_item, parent, false);
    return new MovieViewHolder(view);
}
```

The header is built directly in code, so that you do not add a whole XML file for a single `TextView`. In a real project you would make a separate `header_item.xml`; here the difference is only where the view comes from.

**Step 5 — you fill the right row, with an offset.** `onBindViewHolder`:

```java
@Override
public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
    if (holder instanceof HeaderViewHolder) {
        ((HeaderViewHolder) holder).bind(movies.size());
    } else {
        ((MovieViewHolder) holder).bind(movies.get(position - 1), listener);
    }
}
```

`position - 1` is essential: position 0 is the header, so the first movie sits at position 1 in the adapter and at index 0 in the list.

**Step 6 — the header class.** In `MovieAdapter`, next to `MovieViewHolder`:

```java
static class HeaderViewHolder extends RecyclerView.ViewHolder {

    private final TextView text;

    HeaderViewHolder(@NonNull View itemView) {
        super(itemView);
        text = (TextView) itemView;
    }

    void bind(int count) {
        text.setText("Saved movies: " + count);
    }
}
```

**Step 7 — the same offset in the click callback.** In `MovieViewHolder.bind(...)`, the last block becomes:

```java
itemView.setOnClickListener(v -> {
    int pos = getBindingAdapterPosition();
    if (listener != null && pos != RecyclerView.NO_POSITION) {
        listener.onItemClick(pos - 1);
    }
});
```

Without `- 1`, a click on the first card would open the second movie, and a click on the last card would throw `IndexOutOfBoundsException` in `openItem`.

**Why it works this way**

`RecyclerView` treats each row type separately: it asks `getItemViewType` before creating a row, keeps a pool of recycled rows for each type and calls `onCreateViewHolder` only when it has nothing to recycle. That is why the header and the cards never mix, although they are in the same list. The price is that all positions after the header are shifted by one, and the shift must be applied in two places: when reading the movie and when reporting the position to the activity. `getItemCount` must include the header, otherwise the last movie is no longer displayed.

**The mistake that costs marks**

1. **You forget `position - 1`.** Symptom: a click on "Inception" opens "Toy Story"; a click on the last card closes the app with `IndexOutOfBoundsException`. Cause: the adapter position includes the header, the list index does not.
2. **You forget `getItemViewType`.** Symptom: the list shows four identical rows with "Saved movies: 3" and no card. Cause: the default implementation returns 0 for any position, and 0 is exactly `TYPE_HEADER` — so all rows are treated as a header.
3. **You forget to update `getItemCount`.** Symptom: the header does not appear at all, or the last movie is missing from the list. Cause: you changed `onCreateViewHolder`, but the row count stayed `movies.size()`.

**The check**

You run it: the first row reads "Saved movies: 3", below it are the three cards. You add a movie: the header becomes "Saved movies: 4", and the new card appears at the end. Click on the first card: "Inception" opens, not "Toy Story". Click on the last card: "The Matrix" opens, without crashing.

**Practise**

- [23.4](cap-23.html#ex-23-4) — the `ViewHolder` with the fields from the card.
- [23.8](cap-23.html#ex-23-8) — conditional elements in the row, the same type logic.

---

## Recipe 34.13 — Click in the adapter, with a callback to the activity

**The requirement, as it sounds in the test**

"On a click on a card, open the movie in `ItemActivity`, in edit mode. The adapter is not allowed to know the activity."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `adapters/MovieAdapter.java` | the `OnItemClickListener` interface, the field, the constructor parameter, the click in `bind` | **yes** |
| 2 | `MainActivity.java` | `new MovieAdapter(movies, this::openItem)` + the `openItem(int)` method | **yes** |
| 3 | `MainActivity.java` | you delete `listView.setOnItemClickListener(...)` | **yes** |

**The steps, in order**

**Step 1 — the contract, declared in the adapter.** At the top of `MovieAdapter`:

```java
public interface OnItemClickListener {
    void onItemClick(int position);
}
```

**Step 2 — the field and the constructor.** The adapter receives the listener once, at construction:

```java
private final List<Movie> movies;
private final OnItemClickListener listener;

public MovieAdapter(List<Movie> movies, OnItemClickListener listener) {
    this.movies = movies;
    this.listener = listener;
}
```

**Step 3 — you pass it on.** `onBindViewHolder`:

```java
@Override
public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
    holder.bind(movies.get(position), listener);
}
```

**Step 4 — you wire the click in `bind`, not in the constructor.** The `bind` method in `MovieViewHolder`, complete:

```java
public void bind(Movie movie, OnItemClickListener listener) {
    movieTitle.setText(movie.getTitle());

    String year = movie.getRelease() != null
            ? YEAR_FORMAT.format(movie.getRelease())
            : "";
    movieSubtitle.setText(movie.getGenre() + " · " + year);

    movieRating.setRating(movie.getRating());
    movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

    movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
            movie.getDuration(), movie.getBudget() / 1_000_000));

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
```

`onCreateViewHolder`, `getItemCount` and the `MovieViewHolder` constructor remain the ones from recipe 34.9.

**Step 5 — the activity implements the contract.** In `MainActivity.onCreate`:

```java
movieAdapter = new MovieAdapter(movies, this::openItem);
```

The `openItem` method, added in `MainActivity`:

```java
private void openItem(int position) {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
}
```

`this::openItem` is a method reference: it has the same signature as the method in the interface (`int` → `void`), so the compiler accepts it in place of an anonymous class.

**Step 6 — you delete the old click.** In `initListeners()`, the `listView.setOnItemClickListener(...)` block disappears. `RecyclerView` does not have the method, and if you did the migration from 34.10, it does not even compile.

**Why it works this way**

`RecyclerView` has no `setOnItemClickListener` — a design decision, because a row can have several clickable areas, and a global listener would be ambiguous. The solution is for the adapter to declare its own interface, and for the activity to implement it. The adapter does not know `MainActivity`, `Intent` or `ItemActivity`: it only knows how to announce "position N was pressed". The position is read **at the moment of the click**, with `getBindingAdapterPosition()`, not at `bind`, because in the meantime the list can change. `NO_POSITION` (`-1`) appears during insertion or deletion animations, when the row no longer has a valid position.

**The mistake that costs marks**

1. **You wire the click in the `ViewHolder` constructor.** Symptom: after the first scroll, a click on a card opens another movie. Cause: `getBindingAdapterPosition()` would be evaluated only once, at the creation of the row, and falls behind on recycling.
2. **You use the `position` parameter from `onBindViewHolder` in the lambda.** Symptom: after you insert a movie, clicks open the neighbouring movie. Cause: the position was captured at bind time, and the insertion shifted all positions after it.
3. **You do not check `NO_POSITION`.** Symptom: `IndexOutOfBoundsException` if you press a card exactly during the insertion animation. Cause: `movies.get(-1)`.

**The check**

You run it: click on each card, in order — the correct movie opens, with its data, and the button reads "Update Movie". You scroll to the bottom and back, press again: still correct. You add a movie, then press it immediately: the new movie opens, not its neighbour.

**Practise**

- [23.9](cap-23.html#ex-23-9) — click with `getBindingAdapterPosition()` and a callback.
- [20.7](cap-20.html#ex-20-7) — an "Edit" button in the card, instead of touching the whole row.

---

## Recipe 34.14 — notifyItem* vs notifyDataSetChanged

**The requirement, as it sounds in the test**

"After Save, the list must update correctly, with animation, without losing its scroll position."

**Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `MainActivity.java` | in the `launcher` callback, you replace `notifyDataSetChanged()` with `notifyItemInserted` / `notifyItemChanged` | **yes** |
| 2 | `adapters/MovieAdapter.java` | nothing — the methods come from `RecyclerView.Adapter` | no |

**The steps, in order**

**Step 1 — the insertion branch.** In the `launcher` callback:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyItemInserted(movies.size() - 1);
} else {
    movies.set(position, movie);
    movieAdapter.notifyItemChanged(position);
}
```

**Step 2 — deletion, if the requirement asks for it.** For a movie removed from the list, the order is the same — first you modify the list, then you notify:

```java
movies.remove(position);
movieAdapter.notifyItemRemoved(position);
```

**Step 3 — you check that no `notifyDataSetChanged()` has been left** in the callback. A single remaining call cancels the benefit of the others: `RecyclerView` rebinds everything and loses the animations.

**The correspondence table:**

| What you do with the list | Method | What index it receives |
|---|---|---|
| you add at the end | `notifyItemInserted(index)` | the index of the new element, i.e. `movies.size() - 1` after `add` |
| you modify an element | `notifyItemChanged(index)` | the index of the modified element |
| you delete an element | `notifyItemRemoved(index)` | the **old** index of the deleted element |
| you move an element | `notifyItemMoved(from, to)` | both positions |
| you replace the whole content | `notifyDataSetChanged()` | none |

**Why it works this way**

`notifyDataSetChanged()` does not say **what** changed, only that something changed: `RecyclerView` considers all rows invalid, rebinds them all, cancels the animations in progress and may lose the scroll position. `notifyItemInserted(index)` says exactly where a new element appeared: `RecyclerView` inserts a single row, runs the insertion animation, keeps the other rows untouched and keeps the scroll. All the `notifyItem*` methods assume that the list has **already** been modified — they announce a change that has happened, they do not produce it.

**The mistake that costs marks**

1. **`notifyItemInserted(movies.size())` after `add`.** Symptom: `IndexOutOfBoundsException: Inconsistency detected. Invalid item position`, only on insertion. Cause: after `add`, the last valid index is `movies.size() - 1`; you notified an index that does not exist.
2. **You notify before modifying the list.** Symptom: the same inconsistency exception, or an empty row that appears and disappears. Cause: `RecyclerView` validates the number of elements at the moment of the notification; if the list has not changed yet, the number does not match.
3. **You call `notifyDataSetChanged()` "to be safe".** Symptom: everything works, but without animations, and the scroll can jump to the start of the list on every save. Cause: the global notification invalidates all rows, so `RecyclerView` no longer has a position to keep.

**The check**

You scroll the list to the last movie, press the FAB, save: the new card appears at the end with a short animation, and the list stays scrolled near where you were. You edit a movie in the middle: only that card changes its values, with a brief highlight, and the others do not flicker. You delete a movie (if you implemented deletion): the card disappears with an animation, and the list closes up.

**Practise**

- [24.1](cap-24.html#ex-24-1) — what happens if you forget the notification.
- [24.2](cap-24.html#ex-24-2) — why `set` and not `add` when editing.
- [24.9](cap-24.html#ex-24-9) — the movie that appears twice after editing.
- [19.9](cap-19.html#ex-19-9) — the list is not allowed to show old data after editing.

---

## Recipe 34.15 — Attach an event to any widget

**The requirement, as it sounds in the test:** "When you press button X, Y should happen" or "when you move the slider, the label should update."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `res/layout/activity_item.xml` | the widget, with `android:id` | only if it is a new widget |
| 2 | `activities/ItemActivity.java` | the field, the line in `initControls()`, the listener in `initListeners()` | **yes** |

**The steps, in order:**

**Step 1 — pick the listener by the widget's type.** There is no single listener; each widget has its own. The table below is all you need.

| Widget | How to attach | What you get in the callback |
|---|---|---|
| `Button`, `MaterialButton`, any `View` | `setOnClickListener` | `View v` — the view that was pressed |
| `EditText` | `addTextChangedListener` | `s`, `start`, `before`, `count` |
| `SeekBar` | `setOnSeekBarChangeListener` | `progress`, `fromUser` |
| `RatingBar` | `setOnRatingBarChangeListener` | `rating`, `fromUser` |
| `Switch`, `MaterialSwitch`, `CheckBox` | `setOnCheckedChangeListener` | `buttonView`, `isChecked` |
| `RadioGroup` | `setOnCheckedChangeListener` | `group`, `checkedId` |
| `Spinner` | `setOnItemSelectedListener` | `parent`, `view`, `position`, `id` |
| `ListView` | `setOnItemClickListener` | `parent`, `view`, `position`, `id` |
| `ListView` (long press) | `setOnItemLongClickListener` | the same, but returns `boolean` |

**Step 2 — attach the listener in `initListeners()`, not in `onCreate()`.** In `G1097`, `onCreate()` calls `initControls()` then `initListeners()`. The order matters: in `initListeners()` the widgets are already bound through `findViewById`, so you cannot get a `NullPointerException`.

```java
private void initListeners() {
    btMovieAction.setOnClickListener(v -> saveMovie());
    sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
        @Override
        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
            tvDurationValue.setText(progress + " min");
        }
        @Override public void onStartTrackingTouch(SeekBar seekBar) { }
        @Override public void onStopTrackingTouch(SeekBar seekBar) { }
    });
}
```

**Step 3 — write the body of the event.** Three forms, all correct; pick the one that reads best:

```java
// 1. anonymous class — explicit, works for any interface
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveMovie();
    }
});

// 2. lambda — only for interfaces with a SINGLE method (functional interfaces)
btMovieAction.setOnClickListener(v -> saveMovie());

// 3. method reference — when the method has exactly the required signature
btMovieAction.setOnClickListener(this::onSaveClicked);
```

`View.OnClickListener` has a single method (`onClick`), so a lambda works. `SeekBar.OnSeekBarChangeListener` has three, so a lambda does **not** work — you need the anonymous class with all three, even if two stay empty.

**Step 4 — if the event has to read another widget's value**, read it inside the callback, not outside it:

```java
// CORRECT: you read at the moment of the click
btMovieAction.setOnClickListener(v ->
        Toast.makeText(this, etTitle.getText().toString(), Toast.LENGTH_SHORT).show());

// WRONG: you read once, at attach time — the value stays frozen at that moment
String title = etTitle.getText().toString();
btMovieAction.setOnClickListener(v ->
        Toast.makeText(this, title, Toast.LENGTH_SHORT).show());
```

**Why it works this way:** a listener is not "an event" — it is **an object you hand to a widget**, and the widget calls it when something happens. You never call `onClick()` yourself; Android does, on the main thread, after it receives the event from the system. That is why the code in the callback runs *later*, not at attach time — and why you must read the state inside it, not before.

**The mistake that costs marks:**

- **Listener attached before `setContentView`** → `findViewById` returns `null` → `NullPointerException` on the first touch. In `G1097` the order is correct; if you add code in `onCreate`, put it after `initControls()`.
- **Lambda on an interface with several methods** → does not compile. `SeekBar.OnSeekBarChangeListener` has three methods; use the anonymous class.
- **Value read outside the callback** → the event uses the stale value. Read inside.
- **Self-triggering listener** → `setChecked(true)` from code calls `onCheckedChanged` exactly like a touch. If the callback calls `setChecked` again, you loop. Check `fromUser` or a `boolean isBinding` flag.

**The check:** run it, press the widget, see the effect. Then change the value **from code** (in `fillForm`) and check that the listener does not undo what `fillForm` set.

**Practise:** [20.1](cap-20.html#ex-20-1), [18.1](cap-18.html#ex-18-1), [19.1](cap-19.html#ex-19-1)

---

## The table of the 15 recipes

| # | Recipe | Typical requirement | Files touched | Minutes |
|---|---|---|---|---|
| 34.1 | Bind a value to a label, live | slider → label, on every movement | `ItemActivity.java` | 5 |
| 34.2 | Bind a value at initialisation | the label starts from the widget's state | `ItemActivity.java` | 5 |
| 34.3 | Read a widget into the model, on save | Save → a complete `Movie` object | `ItemActivity.java` | 10 |
| 34.4 | Show or hide a widget conditionally | label visible only when the switch is on | `ItemActivity.java` | 5 |
| 34.5 | Validation with an error message | empty title / invalid budget → `setError` | `ItemActivity.java` | 10 |
| 34.6 | Synchronise two widgets | switch → checkbox | `ItemActivity.java` | 5 |
| 34.7 | ArrayAdapter with `toString()` | a simple list, one text per row | `MainActivity.java` | 5 |
| 34.8 | BaseAdapter with a ViewHolder | a complete card on a `ListView` | `adapters/MovieListAdapter.java`, `MainActivity.java` | 20 |
| 34.9 | RecyclerView.Adapter from scratch | a complete card on a `RecyclerView` | `adapters/MovieAdapter.java`, `activity_main.xml`, `MainActivity.java` | 20 |
| 34.10 | Full migration ListView → RecyclerView | dependency + layout + adapter + activity | 5 files | 25 |
| 34.11 | GridLayoutManager, two columns | a list in two columns | `MainActivity.java` | 3 |
| 34.12 | Header in the list | two row types | `adapters/MovieAdapter.java` | 15 |
| 34.13 | Click in the adapter, with a callback | card → `ItemActivity` | `adapters/MovieAdapter.java`, `MainActivity.java` | 10 |
| 34.14 | notifyItem* vs notifyDataSetChanged | an update with animation | `MainActivity.java` | 5 |
| 34.15 | Attach an event to any widget | "when you press X, Y should happen" | `ItemActivity.java` | 5 |

---

## Chapter 34 summary

**The chain everything depends on.** A binding has three links: the view in the XML (with an ID), the reference in Java (`findViewById`, after `setContentView`) and the moment the binding becomes active (a listener or an explicit call). If any is missing, the code compiles and does nothing.

**The order that is not negotiable.** `setContentView` → `initControls` → `initListeners` → `fillForm`. `initListeners` before `fillForm` makes the bindings catch the values set from code too. Once you add synchronisations between widgets, the order of the lines in `fillForm` becomes part of the logic: the last one to write wins.

**The adapter, in brief.** `ArrayAdapter` for a single `TextView` and `toString()`. `BaseAdapter` for several views on a `ListView`: `getView` + `convertView` + `ViewHolder` + `setTag`. `RecyclerView.Adapter` for several views on a `RecyclerView`: `onCreateViewHolder` + `onBindViewHolder` + `getItemCount` + a mandatory `ViewHolder`.

**Three things `RecyclerView` does not forgive:**

1. No `setLayoutManager` — empty list, no error.
2. No `notifyItem*` after modifying the list — the list does not update.
3. A `getItemCount()` that does not match the list — `IndexOutOfBoundsException` while scrolling, not at startup.

**What you say when you are asked to explain**

| Question | The short answer |
|---|---|
| Why does the label update without me touching it? | the listener is called on any change, including `setProgress` / `setChecked` from code |
| Why `View.GONE` and not `INVISIBLE`? | `GONE` takes the view out of the layout, `INVISIBLE` keeps its space |
| Why does `setError` not stop the save by itself? | it attaches a message to the view; your `return` does the stopping |
| Why must `fillForm` take the listener into account? | `setChecked` from code triggers the listener exactly like a touch |
| Why does the `ArrayAdapter` row show `Movie{...}`? | the adapter calls `toString()` on each element |
| Why `ViewHolder`? | a cache of references, so you do not look up the views on every scroll |
| Why `setLayoutManager`? | `RecyclerView` does not know by itself how to arrange the rows |
| Why is the click in `bind`, not in the constructor? | the position changes on recycling; in `bind` it is read at the moment of the click |
| Why can `getBindingAdapterPosition()` give `-1`? | the row has no valid position during an animation |
| Why `notifyItemInserted` and not `notifyDataSetChanged`? | the fine-grained notification rebinds a single row and keeps the animations |

**Final checklist, before you close the exam**

- [ ] I ran the app: empty form, edited form, save, list.
- [ ] Every `findViewById` has an ID that exists in the XML.
- [ ] Every `if` branch that changes visibility also has an `else`.
- [ ] `setLayoutManager` is called before `setAdapter`.
- [ ] After every `add` / `set` / `remove` there is a notification.
- [ ] No `notifyDataSetChanged()` is left where the requirement asks for animation.
- [ ] `ItemActivity` uses `findViewById`, not `ActivityItemBinding` — that import is dead in the repo.
