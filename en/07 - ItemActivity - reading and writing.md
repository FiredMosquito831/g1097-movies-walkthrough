# Chapter 07 — `ItemActivity`: reading and writing the form

**Objective:** a complete `ItemActivity` — wires up the 13 fields, shows a `DatePickerDialog`, updates values live (duration, switch) and builds a `Movie` on Save.

**Estimated time:** 45–60 min.

**Final file:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` (8306 B, SHA-256 `5d48a48e8bcb460d…`)

> **Careful:** in this chapter `ItemActivity` **doesn't have** `fillForm` yet (edit mode) — that comes in ch. 09. Here only **insert mode**: empty fields → you fill them in → Save.

---

## Step 7.1 — Create the class and declare it in the manifest

### Why

`ItemActivity` is the second screen. It must exist as a file **and** be declared in the manifest, otherwise `startActivity` throws `ActivityNotFoundException`.

### How

1. Right-click the package `ro.ase.ie.g1097.activities` → **New → Java Class** → `ItemActivity`.
2. In `AndroidManifest.xml`, add inside `<application>`:

```xml
<activity
    android:name=".activities.ItemActivity"
    android:exported="false"
    android:windowSoftInputMode="adjustResize" />
```

### Why `exported="false"`

`ItemActivity` isn't started from the launcher. Only from `MainActivity`, via an `Intent`. If it were `true`, any app on the phone could open it — a security risk.

> **Remember:** `exported="true"` only for the launcher activity (and for those that receive an external `intent-filter`). All the others: `false`.

---

## Step 7.2 — The skeleton and the fields

### Why

`ItemActivity` needs references to 13 views, plus 3 state fields (`position`, `releaseCal`, `dateFormat`).

### How

```java
package ro.ase.ie.g1097.activities;

import android.app.DatePickerDialog;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.RatingBar;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.IntentCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.materialswitch.MaterialSwitch;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class ItemActivity extends AppCompatActivity {

    private EditText etTitle;
    private EditText etRelease;
    private Spinner spGenre;
    private EditText etBudget;
    private SeekBar sbDuration;
    private RatingBar rbRating;
    private RadioGroup rgApproval;
    private CheckBox cbonWatchList;
    private MaterialSwitch swWatched;
    private EditText etPoster;
    private Button btMovieAction;
    private TextView tvDurationValue;
    private TextView tvWatchedValue;

    private int position = -1;   // -1 = insert mode
    private Calendar releaseCal = Calendar.getInstance();
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_item);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        initControls();
        initListeners();
    }

    private void initControls() {
        // step 7.3
    }

    private void initListeners() {
        // step 7.4
    }

    private void saveMovie() {
        // step 7.8
    }

    private void showReleaseDatePicker() {
        // step 7.7
    }
}
```

### Why `position = -1`

It's a **sentinel** (a special value). `-1` means "I'm not editing anything, I'm creating a new movie". Any value ≥ 0 means "I'm editing the movie at this position". See ch. 09.

### Why `releaseCal = Calendar.getInstance()`

The default date = **now**. If the user doesn't pick a date, the movie gets the current date. The alternative would be `null`, but then `saveMovie` would put `null` into the model and `fillForm` would crash.

### Why `dateFormat` is `final`

`SimpleDateFormat` is **mutable** and **not thread-safe**. Here it's used only on the UI thread, so it's fine. `final` guarantees it isn't reassigned.

> **Remember:** `SimpleDateFormat` with `Locale.getDefault()` respects the phone's language. For a fixed format regardless of language, use `Locale.US`.

### Why `IntentCompat` and not directly

`getSerializableExtra(String)` is **deprecated** in API 33+. `IntentCompat.getSerializableExtra(intent, key, Class)` is the modern variant, which explicitly requires the class type. See ch. 09.

---

## Step 7.3 — `initControls`: the 13 `findViewById` calls

### Why

Every field in the code must be bound to the view in XML. Without that, you get `null` and an NPE on first access.

### How

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
}
```

### The mismatched-names trap

Notice:

| Java field | XML ID | Why they differ |
|---|---|---|
| `cbonWatchList` | `cbOnWatchList` | a name chosen by the professor; it doesn't follow the convention |
| `btMovieAction` | `btnMovieAction` | `bt` vs `btn` |
| `etTitle` | `etTitle` | the same |

**It's not a mistake** — it's a naming inconsistency. But you must match them **exactly**, otherwise `findViewById` returns `null`.

> **Remember:** the XML ID and the Java field name are **independent**. The `et`/`sp`/`sb`/`rb`/`rg`/`cb`/`sw`/`tv`/`btn` convention is just a readability convention, not a rule of the language.

### Exercise 7.3

**Requirement:** what happens if you write `findViewById(R.id.etTitl)` (a typo)? When does the error appear?

<details>
<summary>Solution — explained</summary>

**What was done:** we introduced a typo in the ID.

**What happens:** **a compile error**, immediately:

```
error: cannot find symbol
variable etTitl
location: class R.id
```

**Why:** `R.id.etTitl` doesn't exist in the generated `R` class. The compiler knows every ID from XML — if it can't find one, it doesn't compile.

**Remember:**
1. `R.id.*` is **checked at compile time**. A wrong ID never reaches runtime.
2. If instead the **XML ID is missing** (you forgot `android:id`), compilation passes, but `findViewById` returns `null` → an NPE at runtime.
3. So: compile error = the ID doesn't exist; NPE = the ID exists but the view isn't in the current layout.

**Where it comes back:** in ch. 09, `fillForm` uses all 13 fields. A `null` there gives an NPE at `etTitle.setText(...)`.

</details>

---

## Step 7.4 — `initListeners`: clicks on the date and the button

### Why

Two actions:
- a click on the Release field → opens the calendar;
- a click on Save → saves and closes.

### How

```java
private void initListeners() {
    etRelease.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            showReleaseDatePicker();
        }
    });
    btMovieAction.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            saveMovie();
        }
    });
}
```

### Why `setOnClickListener` on an `EditText`

An `EditText` receives focus on touch, **not** a click. But `setOnClickListener` works: on the first touch it receives focus **and** fires the click.

> **Trap:** if the `EditText` has `android:focusable="false"`, the click never arrives. Not the case here.

### Old syntax vs lambda

The repo uses `new View.OnClickListener() { ... }` — the **classic anonymous** syntax. The modern equivalent:

```java
etRelease.setOnClickListener(v -> showReleaseDatePicker());
btMovieAction.setOnClickListener(v -> saveMovie());
```

Both compile. The repo keeps the old style for teaching clarity (you can see the type).

> **Remember:** lambdas are available from Java 8. The project has `VERSION_11`, so it works. But in the exam, if you're asked to "write the listener", both forms are accepted.

### Exercise 7.4

**Requirement:** rewrite both listeners with lambdas. Check that it works.

<details>
<summary>Solution — explained</summary>

**What was done:** we replaced the anonymous classes with lambda expressions.

```java
private void initListeners() {
    etRelease.setOnClickListener(v -> showReleaseDatePicker());
    btMovieAction.setOnClickListener(v -> saveMovie());
}
```

**Why it works:** `View.OnClickListener` is a **functional interface** — it has a single abstract method (`onClick(View)`). A lambda is allowed anywhere a functional interface is expected.

**Remember:**
1. A lambda = a short form for an anonymous class with **a single method**.
2. The `v` parameter is the `View` that fired the click. We don't use it here.
3. `this` inside an anonymous class refers to the anonymous class; inside a lambda, to the **outer class**. It's an important difference: if you needed `ItemActivity.this`, a lambda is safer.

**Where it comes back:** in ch. 11, `MovieAdapter` uses a lambda for `itemView.setOnClickListener(v -> ...)`. There `this` would have been ambiguous.

</details>

---

## Step 7.5 — A listener on the `SeekBar`

### Why

When you move the bar, the `tvDurationValue` text has to show the current value. Without a listener, it stays at "0 min".

### How

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

### Why three methods

`OnSeekBarChangeListener` has **three** abstract methods — it isn't a functional interface, so **you can't use a lambda**. You have to implement all three, even if two stay empty.

| Method | When it's called |
|---|---|
| `onProgressChanged` | on every value change |
| `onStartTrackingTouch` | when you put your finger on the handle |
| `onStopTrackingTouch` | when you lift your finger |

### The `fromUser` parameter

`true` = the change came from the user (they dragged the bar).
`false` = the change came from code (`setProgress(...)`).

The repo **ignores** the parameter — it updates the text in both cases. That's actually **correct**: you want the text to reflect the value regardless of the source. See ch. 09, where the `setProgress` in `fillForm` also triggers the update.

### Exercise 7.5

**Requirement:** change the listener so it shows "0 min" when progress is 0, and "N min." otherwise. Why is that a good idea?

<details>
<summary>Solution — explained</summary>

**What was done:** we added a condition on `progress`.

```java
@Override
public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
    if (progress == 0) {
        tvDurationValue.setText("0 min");
    } else {
        tvDurationValue.setText(progress + " min.");
    }
}
```

**Why it's a good idea:** consistency with the layout. In XML, `tvDurationValue` has `android:text="0 min"` (no full stop). If the listener always wrote "N min.", the first touch would give "0 min." — a pointless visual change.

**Remember:**
1. The initial text from XML and the text generated by code must be **consistent**.
2. `progress + " min."` does **concatenation** of `int` + `String` → `String`. It's not addition.
3. For correct pluralisation ("1 min" vs "2 min"), you need `getResources().getQuantityString(...)`.

**Where it comes back:** in `movie_item.xml` (ch. 11), `movieFacts` shows `duration + " min."` — the same convention.

</details>

---

## Step 7.6 — A listener on the `MaterialSwitch`

### Why

When you toggle the switch, the `tvWatchedValue` text has to show "Yes" / "No".

### How

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});
```

### Why `CompoundButton.OnCheckedChangeListener`

`MaterialSwitch` extends `SwitchCompat` → `CompoundButton`. The listener is defined on `CompoundButton`, so it works on **any** subclass: `Switch`, `CheckBox`, `RadioButton`, `ToggleButton`.

> **Remember:** `setOnCheckedChangeListener` is defined on `CompoundButton`. That's why it works identically on a switch and a checkbox.

### The ternary operator

`isChecked ? "Yes" : "No"` = a short form of an `if/else` that returns a value.

### Exercise 7.6

**Requirement:** add a similar listener on `cbonWatchList` that switches a new `TextView` (`tvWatchlistValue`) between "On list" and "Not on list". You also have to add the `TextView` to the layout.

<details>
<summary>Solution — explained</summary>

**What was done:** we added to `activity_item.xml`, next to the checkbox:

```xml
<TextView
    android:id="@+id/tvWatchlistValue"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Not on list"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorPrimary" />
```

and in `ItemActivity`:

```java
private TextView tvWatchlistValue;
// in initControls:
tvWatchlistValue = findViewById(R.id.tvWatchlistValue);
// in initListeners:
cbonWatchList.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchlistValue.setText(isChecked ? "On list" : "Not on list"));
```

**Why it works:** `CompoundButton.OnCheckedChangeListener` is shared by switches and checkboxes.

**Remember:**
1. Here you used a **lambda** — `OnCheckedChangeListener` has a single method, so it's functional.
2. You couldn't with the `SeekBar`, because it has three methods.
3. The rule: **one abstract method = a lambda is allowed**.

**Where it comes back:** in ch. 11, `MovieAdapter` no longer needs listeners on the switch/checkbox — the state is only displayed through `Chip`s.

</details>

---

## Step 7.7 — `DatePickerDialog`

### Why

The date is picked from a calendar, not typed. `DatePickerDialog` is the standard Android dialog.

### How

```java
private void showReleaseDatePicker() {
    String current = etRelease.getText().toString();
    if (!current.isEmpty()) {
        try {
            Date parsed = dateFormat.parse(current);
            if (parsed != null)
                releaseCal.setTime(parsed);
        } catch (ParseException ignored) { }
    }

    new DatePickerDialog(
            this,
            new DatePickerDialog.OnDateSetListener() {
                @Override
                public void onDateSet(DatePicker view, int year, int month, int day) {
                    releaseCal.set(year, month, day);
                    etRelease.setError(null);
                    etRelease.setText(dateFormat.format(releaseCal.getTime()));
                }
            },
            releaseCal.get(Calendar.YEAR),
            releaseCal.get(Calendar.MONTH),
            releaseCal.get(Calendar.DAY_OF_MONTH)
    ).show();
}
```

### The flow, step by step

1. **Read the current text** from `etRelease`.
2. **If it isn't empty**, try to parse it with `dateFormat`. If that succeeds, update `releaseCal`.
3. **Open the dialog**, positioned on the date in `releaseCal`.
4. **On confirmation**, `onDateSet` receives `year`, `month`, `day`.
5. **Update** `releaseCal` and the field text.

### Why `month` is 0-indexed here too

`DatePickerDialog` returns `month` from 0 (January = 0), just like `Calendar`. So `releaseCal.set(year, month, day)` works directly, with no `-1`.

> **Careful:** `DatePicker` (the widget) has a 0-indexed `getMonth()`, but `DatePickerDialog` gives you the value directly correct for `Calendar.set`. Don't confuse them.

### Why `catch (ParseException ignored) { }`

If the user typed something invalid ("abc"), `parse` throws. We ignore it and carry on with the date from `releaseCal` — the calendar opens on the previous date or on today.

> **Remember:** an empty `catch` is acceptable **only** when the error doesn't change the desired behaviour. Here: "if the text is invalid, ignore it".

### Why `etRelease.setError(null)`

It clears any error shown previously. In the repo, `setError` is never called with a non-null value — so the line is defensive, with no practical effect.

### Exercise 7.7

**Requirement:** add validation: if the chosen date is in the future, show `etRelease.setError("Release date cannot be in the future")` and don't update the field.

<details>
<summary>Hint</summary>

Compare `releaseCal.getTime()` with `new Date()` (now). `Date.after(other)` returns `true` if it's later.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added a condition in `onDateSet`.

```java
@Override
public void onDateSet(DatePicker view, int year, int month, int day) {
    Calendar chosen = Calendar.getInstance();
    chosen.set(year, month, day);
    if (chosen.after(Calendar.getInstance())) {
        etRelease.setError("Release date cannot be in the future");
        return;
    }
    releaseCal.set(year, month, day);
    etRelease.setError(null);
    etRelease.setText(dateFormat.format(releaseCal.getTime()));
}
```

**Why `chosen.after(Calendar.getInstance())`:** `Calendar` has `after(Calendar)`. For `Date`, you have `date.after(new Date())`.

**Remember:**
1. `setError` shows a red message under the field and an icon. It's the standard validation mechanism.
2. An early `return` = you don't update `releaseCal` and don't change the text.
3. `setError(null)` clears the previous error — here it becomes **useful**, not just defensive.

**Where it comes back:** in `saveMovie` (step 7.8) you could validate similarly before building the `Movie`.

</details>

---

## Step 7.8 — `saveMovie`: building the model

### Why

On Save, you have to read **all** 10 UI fields and build a `Movie`. Then send it back.

### How

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

### The source of each field

| Model field | Source | Method |
|---|---|---|
| `title` | `etTitle` | `getText().toString()` |
| `release` | `releaseCal` | `getTime()` |
| `genre` | `spGenre` | `getSelectedItem().toString()` |
| `budget` | `etBudget` | `Double.parseDouble(getText().toString())` |
| `duration` | `sbDuration` | `getProgress()` |
| `rating` | `rbRating` | `getRating()` |
| `watched` | `swWatched` | `isChecked()` |
| `onWatchlist` | `cbonWatchList` | `isChecked()` |
| `poster` | `etPoster` | `getText().toString()` |
| `approval` | `rgApproval` | iterate over the children |

### Why `releaseCal` and not `etRelease`

Because `releaseCal` is the source of truth. The text can be empty or invalid; the calendar always holds a valid value. See step 5.6.

### The `Double.parseDouble` trap on an empty field

If `etBudget` is empty, `Double.parseDouble("")` throws `NumberFormatException` → **the app crashes**.

This is a **real** problem in `d719ffc`. Your local sync version fixes it like this:

```java
String budgetText = etBudget.getText().toString().trim();
if (!budgetText.isEmpty()) {
    try {
        movie.setBudget(Double.parseDouble(budgetText));
    } catch (NumberFormatException e) {
        movie.setBudget(0);
    }
} else {
    movie.setBudget(0);
}
```

> **Decision:** in the base material we keep the repo version (fidelity). But you **know** it's a bug. If you want to fix it, use the variant above — it's an improvement, not a deviation.

### Why `break` in the radio loop

Once you've found the checked button, there's no point continuing. `break` exits the loop.

### Why `if (position != -1)` on `putExtra`

If it's insert mode (`position == -1`), you don't send the position. `MainActivity` will interpret its absence as "add at the end". See ch. 08.

### Exercise 7.8 — the trap

**Requirement:** run the app, open the form, **leave the budget empty**, press Save. Read `Logcat`.

<details>
<summary>Solution — explained</summary>

**What was done:** we tested saving with an empty budget.

**What happens:** the app **crashes**:

```
java.lang.NumberFormatException: For input string: ""
    at java.lang.Double.parseDouble(Double.java:...)
    at ro.ase.ie.g1097.activities.ItemActivity.saveMovie(ItemActivity.java:173)
```

**Why:** `Double.parseDouble("")` can't convert an empty string into a number. It throws `NumberFormatException`, which isn't caught → it propagates → the app closes.

**Remember:**
1. **Any** `parseXxx` throws on invalid input: `Integer.parseInt`, `Double.parseDouble`, `SimpleDateFormat.parse`.
2. `getText().toString()` returns `""` for an empty field, **not** `null`. So a `!= null` check doesn't help — you need `!isEmpty()`.
3. `try/catch` is mandatory when you parse user input.

**Where it comes back:** in ch. 09, `fillForm` has the opposite problem: `dateFormat.format(existing.getRelease())` throws an NPE if `release` is `null`. The same category of bug: **unsafe input used without a check**.

</details>

---

## Step 7.9 — Verification

### How

1. Run the app.
2. From `MainActivity`, press the FAB → **nothing happens** (you don't have navigation yet, ch. 08).
3. To test `ItemActivity` in isolation, temporarily add to `MainActivity.onCreate`:

```java
startActivity(new Intent(this, ItemActivity.class));
```

4. Fill in the form, press Save. The app closes (finish), but you don't see the result — because you don't have `launcher` yet.

### What to check

- [ ] 13 `findViewById` calls with no NPE
- [ ] a click on Release opens the calendar
- [ ] moving the bar updates `tvDurationValue`
- [ ] toggling the switch updates `tvWatchedValue`
- [ ] Save doesn't crash (with the budget filled in)
- [ ] Save **crashes** with an empty budget → you've confirmed you understood the bug

---

## Step 7.10 — Reflection exercise

**Requirement:** why does `ItemActivity` build a **new** `Movie` on Save, instead of modifying an existing one?

<details>
<summary>Answer — explained</summary>

**What was done:** on Save, the code does `Movie movie = new Movie();` — a new object, whether it's an insert or an edit.

**Why:** the model is **immutable from the activity's point of view**. `ItemActivity` has no reference to the object in `MainActivity` (it received a **copy** through serialization). So it can't modify the original.

The solution: build a new object, send it back, and let `MainActivity` decide what to do with it:
- insert → `movies.add(movie)`
- edit → `movies.set(position, movie)`

**Remember:**
1. **Serialization creates copies.** You can't modify the parent object by reference.
2. The "send the result back" pattern is standard in Android for editing.
3. The alternative would be `startActivityForResult` with a mutable `Parcelable` or a shared `ViewModel` — but that's overkill here.

**Where it comes back:** ch. 08 (`onActivityResult`) and ch. 09 (`position`).

</details>

---

## Step 7.11 — Compare with the original

```bash
diff "cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java" \
     "_progres/Movies1097/app/src/main/java/ro/ase/ie/g1097/activities/ItemActivity.java"
```

At this stage you'll have **intentional differences**: `fillForm` and the block in `onCreate` that reads the `Intent` are missing (they come in ch. 09). Everything else should be identical.

---

## Chapter 07 summary

- `initControls` = 13 `findViewById` calls, after `setContentView`.
- `OnSeekBarChangeListener` has 3 methods → no lambda.
- `OnCheckedChangeListener` has 1 method → a lambda is fine.
- `DatePickerDialog` with a 0-indexed `month`, `releaseCal` as the source of truth.
- `saveMovie` builds a new `Movie` from the UI.
- `Double.parseDouble("")` = `NumberFormatException` — a real bug in the repo.

**Next chapter:** [08 - Navigation and the result.md](08%20-%20Navigation%20and%20the%20result.md)
