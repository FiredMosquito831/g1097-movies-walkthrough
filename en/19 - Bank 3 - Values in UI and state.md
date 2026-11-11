# Chapter 19 — Requirements bank 3: binding values to the UI and preserving state

**Objective:** to translate any requirement of the form "when X changes, the label should show Y" or "after the edit, the state should still be correct" into a concrete Android mechanism, on the G1097 app at commit `d719ffc`. In the exam the requirement never says "write a `TextWatcher`" — it says "when I type in the field, the label should update". The translation is your job.

**The four directions in which a value travels:**
| Direction | Mechanism |
|---|---|
| widget → label | listener (`onProgressChanged`, `onCheckedChanged`, `afterTextChanged`, ...) |
| widget → model | `saveMovie()` |
| model → widget | `fillForm()` |
| list → screen | `notifyDataSetChanged()` / `notifyItemChanged()` |

All ten exercises are variants of these four directions. Three of them (19.7, 19.8, 19.10) fix **real** defects in the code at `d719ffc`, they don't invent scenarios.

**Convention:** the strings in the UI stay in English, as in the app (`"Save Movie"`, `"Yes"`, `"No"`). The prose and explanations are in English.

---

## Exercise 19.1 — `tvWatchedValue` follows the switch

**Requirement:** `tvWatchedValue` shows `"Yes"` / `"No"` according to the state of `swWatched`. The code already exists at `d719ffc`. Explain **why** the label is already correct when you open an existing movie in edit mode, and what exactly breaks if you move `initListeners()` after the block that calls `fillForm(existing)`.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `initListeners()` (lines 144–149) and `onCreate()` (lines 73–83).

**How you approach it — your steps:**
1. Open `ItemActivity.java` and find `initListeners()` (line 131). Confirm that the `swWatched.setOnCheckedChangeListener(...)` block exists and writes to `tvWatchedValue`.
2. Open `onCreate()` (line 63) and note the order on paper: `initControls()` → `initListeners()` → the `if (existing != null)` block → `fillForm(existing)`.
3. Go into `fillForm` (line 86) and follow line 92: `swWatched.setChecked(existing.isWatched())`. Ask yourself what `setChecked` does when the value it receives is identical to the current one — the XML default is `false`.
4. Write the answer in two sentences: the listener is called on `setChecked` **if the value changes**; for `false` it doesn't change, but the label in the XML is already `"No"`.
5. Check on the emulator: open "Inception" (`watched = true`) → label `"Yes"`; open "The Matrix" (`watched = false`) → `"No"`. Then temporarily move `initListeners()` after the `if` block and repeat: "Inception" shows `"No"`. Put the order back.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 1</summary>

`CompoundButton.setChecked()` is not a mute setter. Read the source: it calls the listener, but only if the value changes (`if (mChecked != checked)`).

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 3</summary>

the XML has `android:text="No"` on `tvWatchedValue` (line 318). The `false` case doesn't trigger the listener, but the label is already correct — that's why it works "by luck".

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** nothing new — the block already exists. What's explained is the order and the condition.

**Code:**

```java
// ItemActivity.initListeners(), lines 144–149 — exists at d719ffc
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});
```

```java
// ItemActivity.onCreate(), lines 73–83 — the order is the whole secret
initControls();
initListeners();          // 1. the listener is registered

Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);   // 2. only now does setChecked() have someone to notify
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

**Why:** `CompoundButton.setChecked(boolean)` is not a plain `this.checked = checked`. The source from `CompoundButton`:

```java
public void setChecked(boolean checked) {
    if (mChecked != checked) {
        mChecked = checked;
        refreshDrawableState();
        // ...
        if (mOnCheckedChangeListener != null) {
            mOnCheckedChangeListener.onCheckedChanged(this, mChecked);
        }
    }
}
```

Two consequences, and both of them matter in the exam:

1. **The listener is called on programmatic calls too**, not only on touch. `fillForm` does `swWatched.setChecked(existing.isWatched())` (line 92), and the listener is already registered → the label updates itself.
2. **Only if the value changes.** `mChecked != checked` is the guard. The full table:

| `existing.isWatched()` | XML default | `setChecked()` | Listener | Label |
|---|---|---|---|---|
| `true` | `false` | changes | called | `"Yes"` ✔ |
| `false` | `false` | doesn't change | **not** called | `"No"` from XML ✔ |

The `false` case works **by luck**: the XML has `android:text="No"` on `tvWatchedValue` (line 318), so the starting value is already correct. If someone changed the XML to `"Yes"`, the movie with `watched = false` would show `"Yes"` and nobody would see why.

**Remember:** if you move `initListeners()` after the `if (existing != null)` block, `setChecked(true)` runs without a listener → the label stays `"No"` for a watched movie. It doesn't crash, it doesn't throw an error, it just lies. The robust fix isn't the order, it's a single method that writes the label, called from both places:

```java
private void updateWatchedLabel(boolean isChecked) {
    tvWatchedValue.setText(isChecked ? "Yes" : "No");
}

// in the listener:
updateWatchedLabel(isChecked);

// at the end of fillForm, after swWatched.setChecked(...):
updateWatchedLabel(existing.isWatched());
```

That way you're independent of the order and of the `mChecked != checked` guard.

**Where it applies:** any `CompoundButton` — `CheckBox`, `MaterialSwitch`, `RadioButton`. `RadioGroup.check(id)` has exactly the same guard (`if (id == mCheckedId) return;`), so `rgApproval.check(...)` in `fillForm` (line 108) only notifies the listener if it changes the selection. On rotation, the framework restores the switch state and calls `setChecked()` again → the label repairs itself.

</details>

---

## Exercise 19.2 — Character counter under `etTitle`

**Requirement:** under the title field a live text of the form `"12 / 50"` appears, updating on every keystroke. Typing past 50 characters is **blocked**, not just flagged.

**Files touched:** `cod-final/res/layout/activity_item.xml` (a new `TextView` + a changed margin) and `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` (`initControls`, `initListeners`).

**How you approach it — your steps:**
1. Open `activity_item.xml` and find the `TextInputLayout` of `etTitle` (lines 70–84). Change `android:layout_marginBottom="16dp"` (line 74) to `4dp`.
2. Add the `tvTitleCounter` `TextView` right after `</com.google.android.material.textfield.TextInputLayout>` (line 84), before the `<!-- Genre -->` comment.
3. In `ItemActivity.java`, add the three imports (`Editable`, `InputFilter`, `TextWatcher`), the `TITLE_MAX_LENGTH` field, the `tvTitleCounter` field and the `findViewById` in `initControls()`.
4. In `initListeners()`, add the two pieces: `etTitle.setFilters(...)` (the blocking) and `etTitle.addTextChangedListener(...)` (the counter).
5. Check on the emulator: type in the title — the counter goes up on every keystroke; at 50 characters typing adds nothing more; the X button in the field clears the text and the counter goes back to `"0 / 50"`.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 1</summary>

they're two different mechanisms. The counter is a `TextWatcher`; the blocking is an `InputFilter.LengthFilter`. One doesn't do the other's job.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

`TextWatcher` has three methods; the one you care about is `afterTextChanged(Editable s)`, and the length comes from `s.length()`. `LengthFilter` goes in an array: `new InputFilter[]{ new InputFilter.LengthFilter(50) }`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added a `TextView` under the title's `TextInputLayout`, registered an `InputFilter.LengthFilter(50)` and a `TextWatcher` that writes `length + " / 50"`.

**Code:**

In `activity_item.xml`, the `TextInputLayout` of `etTitle` has `android:layout_marginBottom="16dp"` (line 74). Change it to `4dp`, then add right after `</com.google.android.material.textfield.TextInputLayout>` (line 84), before the `<!-- Genre -->` comment:

```xml
<TextView
    android:id="@+id/tvTitleCounter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="end"
    android:layout_marginBottom="16dp"
    android:text="0 / 50"
    android:textAppearance="?attr/textAppearanceLabelSmall"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

In `ItemActivity.java`:

```java
// new imports
import android.text.Editable;
import android.text.InputFilter;
import android.text.TextWatcher;

// new fields, next to the others
private static final int TITLE_MAX_LENGTH = 50;
private TextView tvTitleCounter;

// initControls(), at the end
tvTitleCounter = findViewById(R.id.tvTitleCounter);

// initListeners(), at the end
etTitle.setFilters(new InputFilter[]{ new InputFilter.LengthFilter(TITLE_MAX_LENGTH) });
etTitle.addTextChangedListener(new TextWatcher() {
    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

    @Override
    public void onTextChanged(CharSequence s, int start, int before, int count) { }

    @Override
    public void afterTextChanged(Editable s) {
        tvTitleCounter.setText(s.length() + " / " + TITLE_MAX_LENGTH);
    }
});
```

**Why:**

- `setFilters` **replaces** the whole filter array, it doesn't add. If you already have a filter (say one that removes double spaces), put it in the same array: `new InputFilter[]{ new InputFilter.LengthFilter(50), otherFilter }`.
- `LengthFilter` acts on **every** text change, including programmatic `setText`. So if `fillForm` receives a 60-character title, only the first 50 make it into the field — and the model and the UI diverge without any message. It's a behaviour you need to be aware of, not a bug.
- `afterTextChanged` is the right callback: it receives the final `Editable`. `onTextChanged` is called during the change, and if you write to the text from there you get re-entrancy.
- The counter is correct after `fillForm` too, because the watcher is registered in `initListeners()`, which runs before the `if (existing != null)` block.
- `TextInputEditText` extends `AppCompatEditText` → `EditText` → `TextView`, so it has both `setFilters` and `addTextChangedListener`.
- The clear button (`app:endIconMode="clear_text"`, line 76) empties the text → the watcher is called → `"0 / 50"`.

**Remember:** Material has a ready-made counter on `TextInputLayout`: `app:counterEnabled="true"` and `app:counterMaxLength="50"`. It shows exactly `"12 / 50"` and turns red over the limit — but it **does not block typing**. If the requirement only says "counter", either variant is accepted; if it says "you shouldn't be able to type more", you need `LengthFilter`. In the exam write both, in one sentence: "the counter is `LengthFilter` + `TextWatcher`; Material has a visual one, but it doesn't block".

**Where it applies:** `etPoster` (URL limit), any field with a maximum length. The same `TextWatcher` is the basis of exercises 19.3 and 19.10.

</details>

---

## Exercise 19.3 — `tvBudgetValue` with thousands separators, while you type

**Requirement:** while the user types in `etBudget`, a `tvBudgetValue` label shows the budget formatted with thousands separators: `160000000` in the field → `$160,000,000` in the label.

**Files touched:** `cod-final/res/layout/activity_item.xml` (a new `TextView` after the budget's `TextInputLayout`, line 179) and `ItemActivity.java` (`initControls`, `initListeners`, a `NumberFormat` field).

**How you approach it — your steps:**
1. Open `activity_item.xml` and find the budget's `TextInputLayout` (lines 165–179). Change `android:layout_marginBottom="16dp"` (line 169) to `4dp`.
2. Add the `tvBudgetValue` `TextView` after `</com.google.android.material.textfield.TextInputLayout>` (line 179), before the `<!-- Duration -->` comment.
3. In `ItemActivity.java`, add `import java.text.NumberFormat;`, the `tvBudgetValue` field, the `budgetFormat` field and the `findViewById` in `initControls()`.
4. In `initListeners()`, add the watcher: read the text, check `isEmpty()`, then `try { Double.parseDouble(raw) } catch (NumberFormatException e)`.
5. Check on the emulator: type `160000000` → the label shows `$160,000,000`; delete everything → `$0`; paste `12a` → the label shows `—`.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

`NumberFormat.getNumberInstance(Locale.US)` groups with `,` and separates decimals with `.` — exactly what `Double.parseDouble` accepts.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

`Double.parseDouble("")` throws, so check `raw.isEmpty()` **before** the `try`. The formatting itself is `budgetFormat.format(value)`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** a `TextWatcher` on `etBudget` that reads the text, parses it and writes the formatted value into the label. The field stays unformatted.

**Code:**

In `activity_item.xml`, the budget's `TextInputLayout` has `android:layout_marginBottom="16dp"` (line 169). Change it to `4dp` and add after `</com.google.android.material.textfield.TextInputLayout>` (line 179), before `<!-- Duration -->`:

```xml
<TextView
    android:id="@+id/tvBudgetValue"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="end"
    android:layout_marginBottom="16dp"
    android:text="$0"
    android:textAppearance="?attr/textAppearanceLabelSmall"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

In `ItemActivity.java`:

```java
// new import
import java.text.NumberFormat;

// new field
private TextView tvBudgetValue;
private final NumberFormat budgetFormat = NumberFormat.getNumberInstance(Locale.US);

// initControls(), at the end
tvBudgetValue = findViewById(R.id.tvBudgetValue);

// initListeners(), at the end
etBudget.addTextChangedListener(new TextWatcher() {
    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

    @Override
    public void onTextChanged(CharSequence s, int start, int before, int count) { }

    @Override
    public void afterTextChanged(Editable s) {
        String raw = s.toString().trim();
        if (raw.isEmpty()) {
            tvBudgetValue.setText("$0");
            return;
        }
        try {
            double value = Double.parseDouble(raw);
            tvBudgetValue.setText("$" + budgetFormat.format(value));
        } catch (NumberFormatException e) {
            tvBudgetValue.setText("—");
        }
    }
});
```

**Why:**

- **The label formats, the field stays raw.** If you formatted the field too, you'd need a re-entrancy guard (you write to the text → the watcher is called again → you write again) and cursor repositioning. Here you need neither: the field isn't touched.
- `NumberFormat.getNumberInstance(Locale.US)` groups with `,` and separates decimals with `.` — exactly what `Double.parseDouble` accepts. With `Locale.getDefault()` on a Romanian phone you'd get `160.000.000`, and if you copied the value into the field, `parseDouble` would throw. A fixed locale = predictable behaviour.
- `Double.parseDouble("")` throws `NumberFormatException` — that's why `isEmpty()` is checked **before** the `try`. This is exactly line 173 in `saveMovie`, where the missing check produces a crash (see 19.10).
- You type `1` → `$1`; `16` → `$16`; `160` → `$160`; `1600` → `$1,600`; `160000000` → `$160,000,000`. Every keystroke returns a new label, with no state kept between calls.
- `NumberFormat.format(double)` keeps up to 3 decimals by default. For money, add `budgetFormat.setMaximumFractionDigits(2);` once, in `initControls`.
- The label is correct after `fillForm` too, because the `setText` in `fillForm` triggers the watcher.

**Remember:** the clean shape of the "widget → label" direction is a **pure function**: read the widget, compute, write the label. Don't keep the parsed value in an activity field and hope it stays in sync — on the first edit of the text you have two sources of truth.

**Where it applies:** any "preview" label — duration (19.4), rating, price. In 19.10 the same watcher also gets validation.

</details>

---

## Exercise 19.4 — `tvDurationValue` shows "1 h 22 min"

**Requirement:** `tvDurationValue` shows `"1 h 22 min"` when the `SeekBar` progress is at least 60, and `"22 min"` when it's below 60. At 148 → `"2 h 28 min"`, at 60 → `"1 h"`.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `onProgressChanged` (lines 150–165) plus a new method.

**How you approach it — your steps:**
1. Open `ItemActivity.java` and read `onProgressChanged` (lines 151–154). Note what it shows now: `progress + " min."`.
2. Write the `formatDuration(int totalMinutes)` method next to `saveMovie()`, with two branches: under 60 and over 60 (integer division + modulo).
3. Replace the body of `onProgressChanged` with a single call: `tvDurationValue.setText(formatDuration(progress));`.
4. Check on the emulator: drag the slider to 82 → `"1 h 22 min"`; to 60 → `"1 h"`; to 59 → `"59 min"`. Then open "Inception" (148) → `"2 h 28 min"` immediately, without touching the slider.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

the hours are `totalMinutes / 60`, the remaining minutes are `totalMinutes % 60`. The `minutes == 0` case must be handled separately, otherwise you get `"1 h 0 min"`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

`onProgressChanged` is called when `fillForm` does `sbDuration.setProgress(...)` too, with `fromUser == false`. That's why the label is correct when opening a movie — don't move the update into `onStopTrackingTouch`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we moved the formatting out of the listener into a separate method and replaced `progress + " min."` with a call to it.

**Code:**

```java
// ItemActivity — new method, next to saveMovie()
private String formatDuration(int totalMinutes) {
    if (totalMinutes < 60) {
        return totalMinutes + " min";
    }
    int hours = totalMinutes / 60;
    int minutes = totalMinutes % 60;
    return minutes == 0 ? hours + " h" : hours + " h " + minutes + " min";
}
```

```java
// onProgressChanged, replace line 153
@Override
public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
    tvDurationValue.setText(formatDuration(progress));
}
```

**Why:**

- Use the `progress` parameter, not `seekBar.getProgress()`. They're the same value, but the parameter is the callback's contract.
- `fromUser` is `false` when `fillForm` does `sbDuration.setProgress(existing.getDuration())` (line 90). The listener is called anyway → the label is correct right after `fillForm`, with no extra code. If you only updated in `onStopTrackingTouch`, the edit screen would show `"0 min"` for a 148-minute movie, because nobody dragged the slider.
- `ProgressBar.setProgressInternal` has the guard `if (progress == mProgress) return false;` — so for a movie with duration 0 the listener isn't called at all. The label in the XML is already `"0 min"` (line 201), so again it works by luck. If you change the XML text, put `updateDurationLabel(0)` at the end of `initControls`.
- `android:max="300"` (line 212) → the maximum value shown is `"5 h"`. The limits under the slider are hardcoded `"0 min"` / `"300 min"` (lines 228, 235) — if you change `max`, you have to change them too.
- 82 → `"1 h 22 min"`, 148 → `"2 h 28 min"`, 60 → `"1 h"`, 59 → `"59 min"`.

**Remember:** the variant at `d719ffc`, `progress + " min."`, has a trailing period that appears nowhere in the requirement and has no hour form. In the exam, if the requirement gives an exact example (`"1 h 22 min"`), the format is part of the grade — don't "improve" it.

**Where it applies:** any `SeekBar`/`ProgressBar` with a derived label. On `RatingBar` there's exactly the same pattern: `onRatingChanged(RatingBar ratingBar, float rating, boolean fromUser)` — and there too `fromUser` is `false` on the `setRating` from `fillForm`.

</details>

---

## Exercise 19.5 — Toast with the number of movies after Save

**Requirement:** after the user saves (whether they added or edited), `MainActivity` shows a `Toast` with how many movies are in the list. The number must be correct in both cases.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` — `onActivityResult` (lines 62–79).

**How you approach it — your steps:**
1. Open `MainActivity.java` and read `onActivityResult` (lines 62–79). Identify the two branches: `position == -1` (insert) and `else` (edit).
2. Confirm that both branches end with `movieAdapter.notifyDataSetChanged()` — the Toast comes after them, not inside.
3. Add `Toast.makeText(MainActivity.this, movies.size() + " movies in the list", Toast.LENGTH_SHORT).show();` at the end of the `if (o.getResultCode() == RESULT_OK)` block, after the `if/else`.
4. Check on the emulator: start with 3 demo movies; press `+`, fill in, Save → `"4 movies in the list"`; then tap "Inception", change the title, Update → `"3 movies in the list"`.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

inside the anonymous `ActivityResultCallback` class, `this` is the callback, not the activity. Write `MainActivity.this`, otherwise it won't compile (there's no `Context`).

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

the number must be read **after** the mutation. If you put the Toast before `movies.add(movie)`, you show 3 instead of 4. `Toast` is already imported at line 9.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added a `Toast` at the end of the callback, after the list was modified and the adapter notified.

**Code:**

```java
// MainActivity.onCreate(), inside ActivityResultCallback
@Override
public void onActivityResult(ActivityResult o) {
    if (o.getResultCode() == RESULT_OK) {
        Intent intent = o.getData();
        Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
        int position = intent.getIntExtra(POSITION_EXTRA, -1);
        if (position == -1) {
            movies.add(movie);
            movieAdapter.notifyDataSetChanged();
        } else {
            movies.set(position, movie);
            movieAdapter.notifyDataSetChanged();
        }
        Toast.makeText(MainActivity.this,
                movies.size() + " movies in the list",
                Toast.LENGTH_SHORT).show();
    }
}
```

**Why:**

- **After both branches.** The insert changes the size (3 → 4), the edit doesn't (it stays 3). Both are correct — the condition is that `movies.size()` is read **after** the mutation.
- If you put the `Toast` before `movies.add(movie)`, you show 3 instead of 4. It's the classic off-by-one that shows up immediately on the emulator.
- `MainActivity.this`, not `this`: inside the anonymous `ActivityResultCallback` class, `this` is the callback, not the activity. `Toast.makeText(this, ...)` doesn't compile — there's no `Context`.
- `Toast` is already imported at line 9 and is unused at `d719ffc` — a sign that the exercise was planned.
- `o.getData()` can theoretically be `null`. Here it's safe, because `ItemActivity.saveMovie()` always calls `setResult(RESULT_OK, intent)` with a non-null `Intent`. An `if (intent == null) return;` costs one line and doesn't hurt anything.

**Remember:** the number is a property of the **model** (`movies`), not of the adapter. `movieAdapter.getCount()` would give the same result and would be even closer to what's on screen — but only because the adapter wraps exactly the same list. In `MainActivity`, the source of truth is `movies`.

**Where it applies:** any "N items" label. If you want a permanent `TextView` instead of a `Toast`, update it in the same place where you notify the adapter — never in a single branch.

</details>

---

## Exercise 19.6 — Rotation doesn't lose the form

**Requirement:** turn the phone in `ItemActivity` and the form keeps the title, budget, duration and rating. Implement `onSaveInstanceState` and explain what is actually lost without it.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — two new methods and five constants.

**How you approach it — your steps:**
1. Open `ItemActivity.java` and make the list of fields that are **not** `View`s: `position` (line 57), `releaseCal` (line 58), `dateFormat` (line 59).
2. Ask yourself, for each one, what happens on rotation: `position` is re-read from the `Intent`; `releaseCal` is reinitialised with `Calendar.getInstance()`; `dateFormat` is just a formatter, it holds no state.
3. Add the five `KEY_*` constants next to `position`.
4. Write `onSaveInstanceState` (the four values + `releaseCal.getTimeInMillis()`) and `onRestoreInstanceState` (symmetric, with `setTimeInMillis`).
5. Check on the emulator: open "Inception", change the title, budget, duration and rating, rotate the phone → the values stay. Then pick a date from the picker, rotate, press Update, reopen the movie → the date is the one chosen, not today's.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 1</summary>

the four fields in the requirement (`etTitle`, `etBudget`, `sbDuration`, `rbRating`) already save themselves — `EditText.getFreezesText()` returns `true`, and `ProgressBar` saves its progress. The field that does **not** get saved is `releaseCal`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

`onRestoreInstanceState` runs after `onStart`, so after `fillForm(existing)` in `onCreate` — your restoration wins over the model. If you restored at the start of `onCreate`, `fillForm` would overwrite your values.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added `onSaveInstanceState` / `onRestoreInstanceState` with the four values from the requirement plus `releaseCal` — the last one being the only one that really mattered.

**Code:**

```java
// new fields, next to position
private static final String KEY_TITLE = "key_title";
private static final String KEY_BUDGET = "key_budget";
private static final String KEY_DURATION = "key_duration";
private static final String KEY_RATING = "key_rating";
private static final String KEY_RELEASE = "key_release";
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
}
```

**Why:**

- `onSaveInstanceState` is called before the activity is destroyed by rotation, by "Don't keep activities" or by process death with state. It is **not** called on Back — there the user really did give up.
- `onRestoreInstanceState` is called **after** `onStart`, so after `onCreate`. That's essential: in `onCreate` `fillForm(existing)` has already run, which put the model values in. Your restoration comes after and wins. If you restored at the start of `onCreate`, `fillForm` would overwrite your values.
- **The four fields in the requirement already save themselves.** `EditText.getFreezesText()` returns `true`, and `ProgressBar` (from which `SeekBar` and `RatingBar` derive) saves its progress in `ProgressBar.SavedState`. They all have `android:id`, and `android:saveEnabled` is `true` by default. So rotation keeps them even without the code above — writing them explicitly is correct, but redundant. Say so in the exam: it shows you know what the framework does.
- **What is really lost is `releaseCal`.** It's an activity field, initialised with `Calendar.getInstance()` on every recreation. The text in `etRelease` survives (it's an `EditText`), but `saveMovie()` reads `releaseCal.getTime()` (line 171), not the field's text. So after rotation you press Update and save **today's date**, while the screen shows the old date. The line that matters in the whole exercise is `outState.putLong(KEY_RELEASE, ...)`.
- `position` survives with nothing: it's re-read from the `Intent`, and the system re-delivers the same `Intent` on recreation.
- `Bundle` has a practical limit of ~1 MB (`TransactionTooLargeException`). Don't put bitmaps, big lists or images in there. A `Movie` is small and `Serializable`, but you don't need it: the form isn't a valid `Movie` yet (the budget can be empty).

**Remember:** `android:configChanges="orientation|screenSize"` is **not** the solution. It hides the problem on rotation, but not on process death, and on top of that it skips resource reloading (the landscape layout would no longer be applied).

**Where it applies:** any activity field that isn't a `View` and doesn't come from the `Intent` — `releaseCal`, a search filter, a page index, an object being edited.

</details>

---

## Exercise 19.7 — `1.6E8` instead of `160000000`

**Requirement:** open "Inception" in edit mode. `etBudget` shows `1.6E8`. It's a real defect at `d719ffc`. Fix `fillForm` and explain why nothing crashes, even though the display is wrong.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `fillForm`, line 89.

**How you approach it — your steps:**
1. Open `ItemActivity.java` at line 89 and read `etBudget.setText(String.valueOf(existing.getBudget()));`.
2. Run the app and open the three demo movies one by one: "Inception" shows `1.6E8`, "Toy Story" shows `3.0E7`, "The Matrix" shows `6.3E7`.
3. Replace the line with an explicit format: `String.format(Locale.US, "%.0f", existing.getBudget())` or `BigDecimal.valueOf(...).toPlainString()`.
4. Check on the emulator: reopen all three → `160000000`, `30000000`, `63000000`. Press Update on "Inception" without touching the budget and reopen it → the value is still `160000000`.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

`String.valueOf(double)` calls `Double.toString(double)`, which switches to scientific notation from 10^7 upwards. All three demo values are above the threshold.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 3</summary>

`%.0f` = no decimals, no exponent, no separators. `Locale.US` is mandatory, otherwise `Locale.getDefault()` would put `,` as the decimal separator and `Double.parseDouble` would reject the text on Save.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we replaced `String.valueOf(...)` with an explicit format, without an exponent.

**Code:**

```java
// before (d719ffc, line 89)
etBudget.setText(String.valueOf(existing.getBudget()));

// after — variant 1
etBudget.setText(String.format(Locale.US, "%.0f", existing.getBudget()));

// after — variant 2 (no locale dependency)
etBudget.setText(BigDecimal.valueOf(existing.getBudget()).toPlainString());
```

Variant 2 needs `import java.math.BigDecimal;`. `Locale` is already imported (line 36).

**Why:**

- The `Double.toString` spec is explicit: the decimal form is only used for `10^-3 ≤ |x| < 10^7`. `160000000.0` is above → `"1.6E8"`. The demo data all hit the bug: `160000000` → `"1.6E8"`, `30000000` → `"3.0E7"`, `63000000` → `"6.3E7"`.
- **Why it doesn't crash:** `Double.parseDouble("1.6E8")` returns `160000000.0`. So `saveMovie()` (line 173) reads back exactly the right value and saves it correctly. The defect is silent: the data is fine, the UI lies.
- **Why the user can't fix it from the keyboard:** `android:inputType="numberDecimal"` (line 178) gives a keyboard without `E`. And `setText` does **not** go through the key listener — it only goes through the filters in `setFilters`. That's exactly why the `E` gets into the field: `fillForm` writes it programmatically, bypassing the typing restriction.
- `String.format(Locale.US, "%.0f", x)`: no decimals, no exponent, no thousands separators. `Locale.US` is mandatory: without it `Locale.getDefault()` is used, and on a Romanian phone `%.2f` would produce `"160000000,00"` — which `Double.parseDouble` rejects.
- `BigDecimal.valueOf(double)` goes through `Double.toString` too, but `toPlainString()` never uses the exponent. Identical result, no locale. For money it's the more correct variant, because it shows the exact decimal value of the `double`, with no format rounding.
- `app:prefixText="$ "` (line 171) already puts `$` in front of the field — don't add another one.

**Remember:** never build the text of a number with `String.valueOf` or `"" + number` when the number can be large or is a `float`. Same trap with the rating: `String.valueOf(0.1f + 0.2f)` gives `"0.30000001"`. And if you want thousands separators, don't put them in the field — `Double.parseDouble("160,000,000")` throws. The separators belong in the label (19.3), not in the input.

**Where it applies:** any `setText` in a numeric field of the model — budget, rating, duration. And `Movie.toString()` has exactly the same problem: the row in the list shows `budget=1.6E8` (see 19.9).

</details>

---

## Exercise 19.8 — `fillForm` crashes when `release` is `null`

**Requirement:** `fillForm` throws a `NullPointerException` for a `Movie` without a release date. Add a guard and explain where the `null` comes from and why the stack trace shows a different line than yours. Then check the second defect in the same method: editing a movie changes its release date without you touching the field.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `fillForm`, line 88.

**How you approach it — your steps:**
1. Open `ItemActivity.java` at line 88 and read `etRelease.setText(dateFormat.format(existing.getRelease()));`.
2. Reproduce the case mentally: `Movie` has a no-argument constructor (line 127), so `new Movie()` leaves `release` as `null`. Such an object reaching `fillForm` reaches `dateFormat.format(null)`.
3. Replace the line with an `if (existing.getRelease() != null) { ... } else { etRelease.setText(""); }`, and in the `if` branch also add `releaseCal.setTime(existing.getRelease());`.
4. Check the second defect: run the app, open "Inception", press Update **without** touching the date field, reopen the movie → the date has become today.
5. Check after the fix: the same sequence → the date stays `16/07/2010`.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

`dateFormat` isn't `null` — the NPE comes from inside `SimpleDateFormat.format`, which does `calendar.setTime(null)`. Read the stack trace down to the `ItemActivity.fillForm` frame.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

`releaseCal` is only updated in `showReleaseDatePicker` (lines 199–204). If you don't open the picker, it stays on "now", and `saveMovie()` writes `releaseCal.getTime()` — not the field's text.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added the `null` guard **and** synced `releaseCal` with the date from the model.

**Code:**

```java
// before (d719ffc, line 88)
etRelease.setText(dateFormat.format(existing.getRelease()));

// after
if (existing.getRelease() != null) {
    releaseCal.setTime(existing.getRelease());
    etRelease.setText(dateFormat.format(existing.getRelease()));
} else {
    etRelease.setText("");
}
```

**Why:**

- **The NPE isn't yours, it's the framework's.** `dateFormat` isn't `null`. `SimpleDateFormat.format(Date)` delegates to `format(date, new StringBuffer(), new FieldPosition(0))`, which does `calendar.setTime(date)`, and `Calendar.setTime(null)` throws a `NullPointerException`. That's why the stack trace shows `java.text.SimpleDateFormat.format` and not line 88 — you have to go down the trace to the `ItemActivity.fillForm` frame to understand what happened. In the exam, that's the answer that counts: not "I put an `if`", but "the NPE comes from inside the formatter".
- **Where the `null` comes from:** `Movie` has a no-argument constructor (line 127) and implements `Serializable`. Any code that does `new Movie()` and forgets to call `setRelease(...)` leaves the field `null`. The app's flow doesn't produce that — `saveMovie()` always sets the date (line 171) — but `fillForm` is an entry point that isn't allowed to assume.
- `etRelease.setText("")` in the `else` branch: the user sees an empty field and can pick a date. `setText(null)` would work too (`TextView` treats `null` as empty text), but `""` is explicit.
- **The second defect, worse:** `fillForm` never synced `releaseCal`. The field is initialised with "now" and is only updated in `showReleaseDatePicker` (lines 199–204). So at `d719ffc`, if you open a movie and press Update **without** touching the date field, `saveMovie()` writes `releaseCal.getTime()` = today's date. The release date changes silently, with no error. It's the most dangerous of the chapter's three defects, because it's data loss, not a crash. The `releaseCal.setTime(existing.getRelease());` line in the `if` branch fixes it.
- The `else` branch leaves `releaseCal` on "now" — exactly what the default `DatePickerDialog` would propose too. That's acceptable.

**Remember:** any `format(...)` on a value that can be `null` needs a guard — `SimpleDateFormat` and `NumberFormat` both throw NPE. Watch out for the dangerous contrast: `String.valueOf(null)` does **not** throw, it returns `"null"`. So one kind of code hides the `null`, another crashes. You need to know which does what.

**Where it applies:** `dateFormat.format` in `showReleaseDatePicker` (already protected by `parsed != null`, line 201), any formatter in `fillForm`, any `NumberFormat.format` on a `Double` you're not sure is set. `Movie.toString()` is safe — string concatenation turns `null` into `"null"`.

</details>

---

## Exercise 19.9 — The list must not show stale data after editing

**Requirement:** after you edit a movie, the row in the list shows the new values. Explain the difference between `notifyDataSetChanged()` and `notifyItemChanged(int)` and say exactly when each one is correct.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` — `onActivityResult` (lines 68–77). If you built `MovieAdapter` in chapter 11, also `adapters/MovieAdapter.java`.

**How you approach it — your steps:**
1. Open `MainActivity.java` and read `onActivityResult` (lines 62–79). Note that both branches already call `notifyDataSetChanged()` — so the question is "why is it needed", not "what's missing".
2. Check what the adapter wraps: line 55, `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)` — the same reference to the list, not a copy.
3. Write the chain from `notifyDataSetChanged()` to the redraw: `BaseAdapter` → `DataSetObservable.notifyChanged()` → the observer in `AbsListView` → `mDataChanged = true` + `requestLayout()`.
4. Write the variant for `RecyclerView`: `notifyItemInserted(movies.size() - 1)` on insert, `notifyItemChanged(position)` on edit.
5. Check on the emulator: comment out `notifyDataSetChanged()` only on the `else` branch, edit a movie → the row keeps the old values. Put it back → the row updates.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 4</summary>

`ArrayAdapter` has no `notifyItemChanged`. That method only exists on `RecyclerView.Adapter`, so on `ListView` the only correct variant is `notifyDataSetChanged()`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

the order is "mutate, then notify". And the object in the `Intent` is a new (deserialised) instance, so without `movies.set(position, movie)` the edit is lost even with a correct notify.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the correct variant for `ListView` was kept, and the fine-grained variant for `RecyclerView` was written.

**Code:**

```java
// MainActivity — ListView + ArrayAdapter (the state at d719ffc, correct)
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

```java
// MainActivity — if you switched to RecyclerView (MovieAdapter, chapter 11)
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyItemInserted(movies.size() - 1);
} else {
    movies.set(position, movie);
    movieAdapter.notifyItemChanged(position);
}
```

**Why:**

- **The adapter doesn't copy the list.** `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)` (line 55) keeps a reference to the **same** `ArrayList`. So `movies.set(position, movie)` changes what the adapter would return from `getItem(position)` — but nobody tells the `ListView` to re-read. `notifyDataSetChanged()` is the signal: `BaseAdapter` → `DataSetObservable.notifyChanged()` → the observer in `AbsListView` marks `mDataChanged = true` and asks for a layout.
- **`notifyItemChanged(int)` doesn't exist on `ArrayAdapter`.** It's declared on `RecyclerView.Adapter`. Calling it on a `ListView` adapter is a compile error, not a runtime one — so you can't "get it wrong quietly".
- **With `ListView`**, `notifyDataSetChanged()` is the only correct variant. It rebuilds all visible rows. For 3–4 movies, the cost is zero.
- **With `RecyclerView`**, the fine-grained variants are correct **and** animated: `notifyItemChanged(position)` rebinds a single row, `notifyItemInserted(index)` animates the insert. `notifyDataSetChanged()` works too, but it rebinds everything and kills the animations.
- **Order: first mutate, then notify.** `notifyItemChanged(position)` before `movies.set(...)` is a rebind request that executes at the next layout — it usually still picks up the new object, because `set` runs synchronously right after. But `notifyItemInserted(size)` before `add` is guaranteed wrong: `RecyclerView` validates the item count and throws `IndexOutOfBoundsException: Inconsistency detected`. The habit "mutate, then notify" is the only one that's always correct.
- **Why the object must be replaced:** `getSerializableExtra` **deserialises**. The `Movie` coming back from `ItemActivity` is a new instance, not the one in the list. Without `movies.set(position, movie)`, the edit is lost even with a perfect notify.
- At `d719ffc`, the row text is `Movie.toString()`: the `ArrayAdapter` with `simple_list_item_1` has `mFieldId == 0` and does `text.setText(item.toString())`. So any changed field changes the row — that's why a missing notify shows up immediately, with the whole field dump.

**Remember:** `notifyDataSetChanged` = "anything might have changed, rebind everything". `notifyItem*` = "exactly this changed". The first is always correct; the second is correct only if the index and the data agree. Both must be called from the main thread.

**Where it applies:** any list update — insert, edit, delete. The same reasoning underlies `DiffUtil` (chapter 11): it computes the series of `notifyItem*` for you.

</details>

---

## Exercise 19.10 — Exam combo: value in the label + validation error

**Requirement:** while the user types in `etBudget`, the `tvBudgetValue` label shows the value immediately, and if the text isn't a number an error appears on the field. Pressing Save with an empty budget must **not** crash the app.

**Files touched:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `initListeners` (the watcher) and `saveMovie` (line 173).

**How you approach it — your steps:**
1. Start from the watcher built in 19.3. Don't write another one — extend that one.
2. Split `afterTextChanged` into three branches: empty (clear the error, show `$0`), valid (format, clear the error), invalid (show `—`, set the error).
3. Open `saveMovie()` at line 173 and replace `movie.setBudget(Double.parseDouble(...))` with the guarded variant: `isEmpty()` → `setError` + `requestFocus` + `return`; then `try/catch` around the parsing.
4. Check on the emulator: empty the budget and press Save → the app does **not** crash, the error appears on the field, the activity stays open. Type `abc` → error. Delete and type `100` → the error disappears. Save → you're back in the list with 4 movies.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

use `afterTextChanged`, not `onTextChanged` — only there do you have the final `Editable`. `setError(null)` on the empty and valid branches is just as important as `setError("...")` on the invalid one.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 3</summary>

`Double.parseDouble("")` throws `NumberFormatException`. The `return` must come **before** `setResult`/`finish()`, otherwise you send an incomplete movie to `MainActivity`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the watcher from 19.3 got validation, and `saveMovie` got a parsing guard.

**Code:**

```java
// initListeners() — replaces the watcher from 19.3
etBudget.addTextChangedListener(new TextWatcher() {
    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

    @Override
    public void onTextChanged(CharSequence s, int start, int before, int count) { }

    @Override
    public void afterTextChanged(Editable s) {
        String raw = s.toString().trim();
        if (raw.isEmpty()) {
            tvBudgetValue.setText("$0");
            etBudget.setError(null);
            return;
        }
        try {
            double value = Double.parseDouble(raw);
            tvBudgetValue.setText("$" + budgetFormat.format(value));
            etBudget.setError(null);
        } catch (NumberFormatException e) {
            tvBudgetValue.setText("—");
            etBudget.setError("Not a valid number");
        }
    }
});
```

```java
// saveMovie() — replace line 173
String budgetText = etBudget.getText().toString().trim();
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
movie.setBudget(budget);
```

**Why:**

- **`afterTextChanged`, not `onTextChanged`.** `onTextChanged` is called during the change; if you write to the text from there, you get re-entrancy. `afterTextChanged` receives the final `Editable` and is the only callback where changing the text is legal (with a guard).
- **Empty doesn't mean invalid.** An empty field means "the user hasn't typed yet" — putting a red error on a virgin form is wrong. Empty → clear the error, show `$0`.
- **`setError(null)` on the valid branch.** Without it, the red icon stays after the user corrects the value. That's the "correct state preservation" half of the requirement: the error is state too.
- **`Double.parseDouble("")` throws** `NumberFormatException: empty String`. At `d719ffc`, line 173 calls it unconditionally, so Save with an empty budget **crashes the app**. The guard in `saveMovie` is mandatory even with the watcher, because the watcher only shows the error — it doesn't stop the button.
- **`return` before `setResult`/`finish()`.** The activity stays open, the user sees the error, nothing goes back to `MainActivity`. If you called `setResult` first and exited after, `MainActivity` would receive an incomplete movie.
- `Double.parseDouble` also accepts `"NaN"`, `"Infinity"` and hex float (`"0x1p3"`). If the exam is strict, add after parsing: `if (!Double.isFinite(value)) { ... }`.
- The `numberDecimal` keyboard restricts typing, but not pasting, not hardware keyboards and not `setText`. Validation stays mandatory.
- `etBudget.setError(...)` is the simple variant. With a `TextInputLayout` around it, you can use `TextInputLayout.setError(...)` — but then you need an `android:id` on the layout (it doesn't have one now, line 165).

**Remember:** the requirement "bind the value to the UI" almost always means: a listener, a label, and the error cleared on **all** branches. There are three branches: empty, valid, invalid. If you miss one, the state stays wrong — exactly what gets graded in the exam.

**Where it applies:** `etTitle` (required, not empty), `etPoster` (URL check), `etRelease` (parsing with `SimpleDateFormat`, which throws `ParseException` instead of `NumberFormatException` — same structure, different exception type).

</details>

---

## Recap — what you check in the exam

| Exam requirement | Mechanism | Exercise |
|---|---|---|
| "when X changes, the label should show Y" | listener on the widget | 19.1, 19.2, 19.3, 19.4 |
| "the field shouldn't accept more than N" | `InputFilter.LengthFilter` | 19.2 |
| "after Save, show how many there are" | `movies.size()` after the mutation | 19.5 |
| "rotation doesn't lose the data" | `onSaveInstanceState` + the fields that aren't `View`s | 19.6 |
| "it shows `1.6E8`" | `String.format("%.0f")` / `BigDecimal.toPlainString()` | 19.7 |
| "it crashes when the date is missing" | `null` guard; the NPE comes from the framework | 19.8 |
| "the list shows old data" | `notifyDataSetChanged` vs. `notifyItemChanged` | 19.9 |
| "show the value + error" | `TextWatcher` + `setError` on all branches | 19.10 |

Three sentences to memorise:

1. **The listener is called on programmatic calls too**, but only if the value changes — that's why `fillForm` works, and why it sometimes works "by luck".
2. **The framework saves the `View`s that have an `id` by itself.** What it doesn't save are your fields — `releaseCal` is the canonical example.
3. **`String.valueOf(number)` lies for large values or `float`s.** Explicit format, always.
