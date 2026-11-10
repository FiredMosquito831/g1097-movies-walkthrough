# Chapter 06 — The form, part 2: the remaining fields

**Objective:** Cards 2 (Production), 3 (Your verdict) and 4 (Poster) plus the Save button. At the end you have `activity_item.xml` complete, 451 lines.

**Estimated time:** 45–60 min.

---

## Step 6.1 — Card 2: Budget

### Why

The budget is a number with decimals. A `TextInputLayout` with `prefixText` shows "$ " in front, without it being part of the value.

### How

```xml
<TextView
    android:id="@+id/tvBudget"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Budget"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:prefixText="$ ">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etBudget"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Budget"
        android:inputType="numberDecimal" />
</com.google.android.material.textfield.TextInputLayout>
```

### `app:prefixText` vs `android:drawableStart`

`prefixText="$ "` is **text** that appears in the field, before the typed value. It isn't part of the text returned by `getText()`.

`drawableStart` would be an **image** — you can't write "$" as an image without a vector.

> **Remember:** `prefixText` and `suffixText` are visual only. `etBudget.getText().toString()` returns **only** the number, without the "$".

### The `Double.parseDouble` trap

In `saveMovie()`:

```java
movie.setBudget(Double.parseDouble(etBudget.getText().toString()));
```

If the field is **empty**, `Double.parseDouble("")` throws `NumberFormatException` → the app crashes on Save.

> This is a **real problem** in the repo code at `d719ffc`. Your local sync version (the uncommitted change) fixes it with an `if (!budgetText.isEmpty())` + `try/catch`. See ch. 07, step 7.8.

### Exercise 6.1

**Requirement:** what happens if you type `1,5` (with a comma) instead of `1.5`? Test it on the emulator with a Romanian keyboard.

<details>
<summary>Solution — explained</summary>

**What was done:** we tested entering a decimal comma.

**What you see:** it depends on the keyboard and the `Locale`:
- On a keyboard with `,` as the decimal separator (Romanian), you can type `1,5`.
- `Double.parseDouble("1,5")` → **`NumberFormatException`**. `parseDouble` accepts **only** a dot.

**Why:** `Double.parseDouble` is independent of `Locale`. It accepts the "invariant" format (`1.5`, `1.5E10`). It doesn't accept a comma.

**Remember:**
1. `Double.parseDouble` ≠ `NumberFormat` with a `Locale`. The first is strict, the second is localized.
2. If you want to accept the comma, use `NumberFormat.getInstance(locale).parse(text)`.
3. `android:inputType="numberDecimal"` shows a keyboard with the **local** separator — so in Romanian you'll see a comma, and parseDouble will crash.

**Where it comes back:** in ch. 07, `saveMovie` has exactly this problem. It's a bug your local version fixes. In the exam, if you're asked "what happens if I enter 1,5", the answer is: `NumberFormatException`.

</details>

---

## Step 6.2 — Card 2: Duration with `SeekBar`

### Why

Duration is a number between 0 and 300. A `SeekBar` is faster than typing and shows the position in the range visually.

### How — the label + value row

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:orientation="horizontal">

    <TextView
        android:id="@+id/tvDuration"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="Duration"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <TextView
        android:id="@+id/tvDurationValue"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="0 min"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorPrimary"
        tools:text="148 min" />
</LinearLayout>
```

### `0dp` + `layout_weight="1"` — the mechanism

In a horizontal `LinearLayout`:

1. Children with `wrap_content` / `match_parent` take their space.
2. The **remaining space** is shared among the children with `layout_weight`.
3. A child with `layout_width="0dp"` + `layout_weight="1"` gets **all** the remaining space.

Here: `tvDuration` (0dp, weight 1) takes all the remaining space after `tvDurationValue` (wrap_content) takes what it needs. The effect: the value is pushed to the right.

> **The rule:** `0dp` + `weight` is the equivalent of "fill what's left". `match_parent` + `weight` would give unintuitive results.

### `tools:text` vs `android:text`

- `android:text="0 min"` — the **real** value at runtime.
- `tools:text="148 min"` — the **preview** value, ignored at build time.

Why both? So you can see in the preview how it looks with a realistic value, while at runtime it starts from 0.

### How

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

<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp">

    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="0 min"
        android:textAppearance="?attr/textAppearanceLabelSmall"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="300 min"
        android:textAppearance="?attr/textAppearanceLabelSmall"
        android:textColor="?attr/colorOnSurfaceVariant" />
</LinearLayout>
```

### The `SeekBar` attributes

| Attribute | Meaning |
|---|---|
| `android:max="300"` | the maximum value |
| `android:min="0"` | the minimum value (**API 26+**) |
| `progressTint` | the colour of the filled part |
| `thumbTint` | the colour of the handle |
| `tools:progress="148"` | the position in the preview |

> **Careful:** `android:min` on a `SeekBar` is available **only from API 26**. The repo has `minSdk 33`, so it works. On older APIs, `min` is always 0.

### Why the "0 min" / "300 min" row

It's a range label. The user knows what the ends of the bar mean. Without it, they'd be guessing.

### Exercise 6.2

**Requirement:** change `android:max` to `600`. Run it. What happens to the "300 min" text under the bar? Why is that a problem?

<details>
<summary>Solution — explained</summary>

**What was done:** we changed only `android:max="600"`, leaving the "300 min" text.

**What you see:** the bar goes up to 600, but the label under it still says "300 min". **Visual inconsistency.**

**Why:** the two are **independent**. `android:max` is the bar's property; "300 min" is a hand-written `TextView`. Nothing synchronises them.

**Remember:**
1. In a layout, numeric values often appear in **two places**: in the attribute and in the text. If you change one, you have to change the other too.
2. The correct solution: generate the right-hand text from `android:max` at runtime, or use a format string (`%1$d min`).
3. Here it's an accepted **technical debt**: the values are hardcoded in two places.

**Where it comes back:** in ch. 07, `tvDurationValue` is updated at runtime from `seekBar.getProgress()`. But the "300 min" label stays hardcoded. If you change `max`, you have to change the text too.

</details>

---

## Step 6.3 — Card 3: RatingBar

### Why

The rating is a score from 0 to 5, with half stars. `RatingBar` is the dedicated widget: it shows stars and accepts touch.

### How

```xml
<TextView
    android:id="@+id/tvRating"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Rating"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<RatingBar
    android:id="@+id/rbRating"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="center_horizontal"
    android:layout_marginTop="4dp"
    android:numStars="5"
    android:stepSize="0.5"
    android:progressTint="#FFC107"
    android:secondaryProgressTint="#FFC107"
    android:progressBackgroundTint="?attr/colorOutlineVariant"
    tools:rating="3.5" />
```

### The attributes, explained

| Attribute | Meaning |
|---|---|
| `android:numStars="5"` | how many stars |
| `android:stepSize="0.5"` | the step: half a star |
| `progressTint="#FFC107"` | the colour of the full stars — **Material yellow** |
| `secondaryProgressTint` | the colour of the partial stars |
| `progressBackgroundTint` | the colour of the empty stars |
| `layout_gravity="center_horizontal"` | centres the bar in the card |
| `tools:rating="3.5"` | the preview value |

### Why `#FFC107` hardcoded

It's an accepted exception: star yellow isn't a role in the Material 3 theme. You could define a `color` in `colors.xml`, but the repo put it directly.

> **Remember:** hardcoded colours are acceptable for **fixed meanings** (stars = yellow, whatever the theme). For everything else, `?attr/`.

### Why `layout_gravity` and not `gravity`

`RatingBar` has no internal content to align. You want to centre **it** in the card → `layout_gravity`.

### Exercise 6.3

**Requirement:** change `stepSize` to `1`. Run it. Can you give 3.5 stars?

<details>
<summary>Solution — explained</summary>

**What was done:** we changed `android:stepSize="0.5"` to `android:stepSize="1"`.

**What you see:** you can only give whole values: 1, 2, 3, 4, 5. You can't select 3.5.

**Why:** `stepSize` defines the **granularity**. With 1, every tap jumps to the next whole star. With 0.5, you can select halves.

**Remember:**
1. `stepSize` is independent of `numStars`. You can have 5 stars with a step of 0.1 (50 possible values).
2. `getRating()` returns a `float` — so it can return 3.5, 2.0, etc.
3. If `stepSize` doesn't divide `numStars` exactly, the last star may be unreachable.

**Where it comes back:** in `movie_item.xml` (ch. 11), the `RatingBar` is `isIndicator="true"` — display only, not interactive. So `stepSize` only matters for **display** there, not for input.

</details>

---

## Step 6.4 — Card 3: the row with `MaterialSwitch` and `MaterialCheckBox`

### Why

Two **independent** boolean options:
- "Recommended" (switch) — is the movie recommended?
- "Watchlist" (checkbox) — is it on the watch list?

### How

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:minHeight="48dp"
    android:orientation="horizontal">

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">

        <TextView
            android:id="@+id/tvWatched"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Recommended"
            android:textAppearance="?attr/textAppearanceBodyLarge"
            android:textColor="?attr/colorOnSurface" />

        <TextView
            android:id="@+id/tvWatchedValue"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="No"
            android:textAppearance="?attr/textAppearanceLabelLarge"
            android:textColor="?attr/colorPrimary" />
    </LinearLayout>

    <com.google.android.material.materialswitch.MaterialSwitch
        android:id="@+id/swWatched"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginEnd="12dp" />

    <com.google.android.material.checkbox.MaterialCheckBox
        android:id="@+id/cbOnWatchList"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Watchlist" />
</LinearLayout>
```

### The structure, explained

```
LinearLayout horizontal (minHeight 48dp)
├── LinearLayout vertical (weight 1)        ← the text, takes the remaining space
│   ├── TextView "Recommended"
│   └── TextView "No"                        ← the value, updated from code
├── MaterialSwitch                            ← sliding toggle
└── MaterialCheckBox "Watchlist"              ← square checkbox
```

### Why two different widgets for the same data type

Both are `boolean`, but they have **different UI meanings**:

- **Switch** = "on/off" — a state of the whole screen or of an action.
- **Checkbox** = "I tick an item from a list of options" — a selection.

Here: "Recommended" is a **state** (the movie is recommended or not), "Watchlist" is a **selection** (I add it to the list). It's a subtle design distinction, not a technical one.

### `minHeight="48dp"`

The minimum height for a **touchable** element. The Material guideline: any interactive element must be at least 48×48dp. Otherwise the user misses it.

### `tvWatchedValue`

A `TextView` that shows "Yes" / "No" **in addition to** the switch. Visually redundant, but useful: the user sees the state in text too, not just through the handle position.

Updated in code (ch. 07):

```java
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
    tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

### Exercise 6.4

**Requirement:** replace `MaterialSwitch` with a second `MaterialCheckBox` (id `cbWatched`). What changes visually? What changes in the code?

<details>
<summary>Solution — explained</summary>

**What was done:** we changed the widget.

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/cbWatched"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginEnd="12dp" />
```

**What you see:** instead of a sliding toggle, you get a square checkbox with no text. Functionally, the same.

**What changes in the code:** **everything.** `swWatched` no longer exists, so:
- `findViewById(R.id.swWatched)` → `null` (or a compile error if you deleted the ID)
- `swWatched.setChecked(...)` → NPE
- `swWatched.isChecked()` → NPE
- the `setOnCheckedChangeListener` listener can no longer be attached

**Why:** `MaterialSwitch` and `MaterialCheckBox` are **different classes** (`com.google.android.material.materialswitch.MaterialSwitch` vs `com.google.android.material.checkbox.MaterialCheckBox`), even though both extend `CompoundButton`. The field in the code is declared `MaterialSwitch swWatched;` — the type has to change.

**Remember:**
1. **The ID links XML to code.** If you change the ID, you must change `findViewById` too.
2. Both are `CompoundButton`, so `setOnCheckedChangeListener` works on either.
3. `MaterialCheckBox` has `text="Watchlist"` — the text sits next to the checkbox. `MaterialSwitch` has no text.

**Where it comes back:** in ch. 11, `movie_item.xml` uses `Chip`s to show the state ("Watched", "Watchlist") — a third visual representation of the same data. You'll see that **the same model** can be displayed in many ways.

</details>

---

## Step 6.5 — Card 3: `RadioGroup` with `MaterialRadioButton`

### Why

Parental guidance is **a single choice out of 5**. `RadioGroup` guarantees that only one button is selected.

### How

```xml
<TextView
    android:id="@+id/tvGuidance"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Guidance"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<HorizontalScrollView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:scrollbars="none">

    <RadioGroup
        android:id="@+id/rgApproval"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="horizontal">

        <com.google.android.material.radiobutton.MaterialRadioButton
            android:id="@+id/rbGeneral"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:checked="true"
            android:text="G" />

        <com.google.android.material.radiobutton.MaterialRadioButton
            android:id="@+id/rbParentGuidance"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="PG" />

        <com.google.android.material.radiobutton.MaterialRadioButton
            android:id="@+id/rbPG13"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="PG-13" />

        <com.google.android.material.radiobutton.MaterialRadioButton
            android:id="@+id/rbRestricted"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="R" />

        <com.google.android.material.radiobutton.MaterialRadioButton
            android:id="@+id/rbNC17"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="NC-17" />
    </RadioGroup>
</HorizontalScrollView>
```

### Why `HorizontalScrollView`

5 buttons horizontally don't fit on a narrow screen (e.g. 360dp). `HorizontalScrollView` allows horizontal scrolling when they don't fit.

`scrollbars="none"` hides the scrollbar (useless on touch screens).

### Why `RadioGroup` and not 5 independent `RadioButton`s

`RadioGroup` **groups** the buttons: when you select one, the others deselect automatically. Without a group, you could select all 5.

### `android:checked="true"` on `rbGeneral`

The first button is selected by default. That way, `rgApproval` **always** has a value — you can't save a movie without guidance.

### Why `MaterialRadioButton` and not `RadioButton`

`MaterialRadioButton` has the Material 3 style (animated, with ripple). A plain `RadioButton` would look like Android 4.

### Exercise 6.5

**Requirement:** add a 6th button, "Unrated", with id `rbUnrated`, text "NR". What do you have to do in the code to make it work?

<details>
<summary>Solution — explained</summary>

**What was done:** we added to the `RadioGroup`:

```xml
<com.google.android.material.radiobutton.MaterialRadioButton
    android:id="@+id/rbUnrated"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="NR" />
```

**What has to be done in the code:** **nothing.** `saveMovie()` and `fillForm()` iterate over `rgApproval.getChildCount()` and read `rb.getText()`. The 6th button is automatically included.

```java
for(int index=0; index<rgApproval.getChildCount(); index++) {
    RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
    if(rb.isChecked()) {
        movie.setApproval(rb.getText().toString());
        break;
    }
}
```

**Why it works:** the code is written **generically**, over the group's children, not over individual IDs. It's proof of good design: you add a button in XML and the code sees it.

**Remember:**
1. `rgApproval.getChildCount()` = the number of direct children.
2. `rgApproval.getChildAt(i)` = the child at position i.
3. `RadioButton` (the parent class) is enough for `getText()` and `isChecked()`; you don't need `MaterialRadioButton` in code.
4. If you had written `if (rbGeneral.isChecked()) ... else if (rbPG13.isChecked()) ...`, you'd have had to add an `else if` for every new button.

**Where it comes back:** in ch. 07, `fillForm` does the same thing in reverse: it looks for the button whose text equals `existing.getApproval()` and selects it. Add "NR" and it works there too, with no changes.

</details>

---

## Step 6.6 — Card 4: Poster URL

### Why

The poster is a URL. The field is a `TextInputEditText` with `inputType="textUri"` and a gallery icon.

### How

```xml
<com.google.android.material.card.MaterialCardView
    style="?attr/materialCardViewFilledStyle"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="24dp"
    app:cardCornerRadius="20dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginBottom="12dp"
            android:text="Poster"
            android:textAppearance="?attr/textAppearanceTitleMedium"
            android:textColor="?attr/colorPrimary" />

        <com.google.android.material.textfield.TextInputLayout
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            app:hintEnabled="false"
            app:endIconMode="clear_text"
            app:startIconContentDescription="Poster link"
            app:startIconDrawable="@android:drawable/ic_menu_gallery">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etPoster"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Poster URL"
                android:inputType="textUri" />
        </com.google.android.material.textfield.TextInputLayout>
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

### Why `layout_marginBottom="24dp"` (not 16dp)

It's the last card before the button. 24dp = more space between "content" and "final action".

### `inputType="textUri"`

A keyboard with `/`, `.com`, `.ro`. It doesn't restrict the characters — you can type anything, but the keyboard is optimised.

### Exercise 6.6

**Requirement:** what happens if you leave the Poster field empty and press Save? Follow the chain through to the display.

<details>
<summary>Solution — explained</summary>

**What was done:** we traced the flow of an empty poster.

**The chain:**
1. `saveMovie()`: `movie.setPoster(etPoster.getText().toString())` → `""` (an empty string, not `null`).
2. `Intent.putExtra(MOVIE_EXTRA, movie)` → the movie is serialized with `poster=""`.
3. `MainActivity.onActivityResult`: `movies.add(movie)` → the list has a movie with an empty poster.
4. `movieAdapter.notifyDataSetChanged()` → the `ListView` redraws.
5. `ArrayAdapter.getView()` → calls `movie.toString()` → shows `poster=''`.

**What you see:** in the list, the row reads `... poster=''}`. Nothing bad happens — because the `ListView` doesn't load images.

**Why it's relevant:** in ch. 11, `MovieAdapter` will try to load the poster into an `ImageView`. An empty or invalid URL will give an empty image (or a network error, if you use a loading library). So validating the poster only becomes important **then**.

**Remember:**
1. `getText().toString()` returns `""` for an empty field, **not** `null`.
2. `""` and `null` are different: `"".isEmpty()` is `true`, `null.isEmpty()` throws an NPE.
3. The model has `poster = null` as its default value, but the UI produces `""`. A minor inconsistency.

**Where it comes back:** in ch. 11, `MovieAdapter` doesn't load images (it has no loading library) — so the poster stays text only. If you want to load images, you need Glide/Coil, which is an extension.

</details>

---

## Step 6.7 — The Save button

### Why

A `MaterialButton` as wide as the screen, 60dp tall, with 30dp corners (pill shape) and a save icon.

### How

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnMovieAction"
    style="@style/Widget.Material3.Button"
    android:layout_width="match_parent"
    android:layout_height="60dp"
    android:text="Save Movie"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    app:cornerRadius="30dp"
    app:icon="@android:drawable/ic_menu_save"
    app:iconGravity="textStart" />
```

### The attributes

| Attribute | Meaning |
|---|---|
| `style="@style/Widget.Material3.Button"` | Material 3 style: `colorPrimary` background, `colorOnPrimary` text |
| `layout_height="60dp"` | a generous height (the default is 40dp) |
| `app:cornerRadius="30dp"` | fully rounded corners (60/2 = 30 → pill) |
| `app:icon="@android:drawable/ic_menu_save"` | a system save icon |
| `app:iconGravity="textStart"` | the icon before the text |

### Why 30dp corners

To make it a **pill**: `cornerRadius = height / 2`. If it were 60, it would be too much (Android caps it at height/2 anyway). If it were 8, it would be a normal button with small corners.

### Why `Widget.Material3.Button` and not `Widget.Material3.Button.Filled`

`Widget.Material3.Button` **is** the filled variant (the default). The variants are:
- `Widget.Material3.Button` = filled
- `Widget.Material3.Button.TonalButton` = tonal (secondary background)
- `Widget.Material3.Button.OutlinedButton` = outline
- `Widget.Material3.Button.TextButton` = text only

### Exercise 6.7

**Requirement:** change the style to `Widget.Material3.Button.OutlinedButton`. Run it. What difference do you see? Which is more appropriate for "Save"?

<details>
<summary>Solution — explained</summary>

**What was done:** we changed the button's style.

**What you see:**
- **Filled** (the original): a solid `colorPrimary` (blue) background, white text. The button is **primary**.
- **Outlined**: transparent background, a 1dp outline, `colorPrimary` text. The button is **secondary**.

**Which is more appropriate:** **Filled**, because "Save" is the screen's primary action. Outlined would suit "Cancel", if there were one.

**Remember:**
1. The Material hierarchy: **filled** = primary action, **tonal** = secondary, **outlined** = alternative, **text** = tertiary.
2. A screen should have **only one** filled button (the primary action).
3. `cornerRadius` works on every style.

**Where it comes back:** it doesn't come back, but it's relevant for the exam: if you're asked "how do you make a secondary button", the answer is `.OutlinedButton` or `.TextButton`.

</details>

---

## Step 6.8 — The `<View>` separators

### Why

Between the Rating and the switch/checkbox row, and between that row and the RadioGroup, there are thin separator lines.

### How

```xml
<View
    android:layout_width="match_parent"
    android:layout_height="1dp"
    android:layout_marginVertical="12dp"
    android:background="?attr/colorOutlineVariant" />
```

### Why `<View>`

`View` is the base class for any visual element. An empty `View`, 1dp tall with a background, is a **line**.

### `layout_marginVertical="12dp"`

Space above and below (equivalent to `marginTop` + `marginBottom`).

### Why `colorOutlineVariant` and not `colorOutline`

`colorOutlineVariant` is **weaker** than `colorOutline`. Separators should be subtle, not compete with the field outlines.

### Exercise 6.8

**Requirement:** replace a separator with a `TextView` containing repeated "—". Is it worth it? Why not?

<details>
<summary>Solution — explained</summary>

**What was done:** we replaced `<View .../>` with a `TextView` containing dashes.

**What you see:** a dotted line, not a continuous one. And it takes more vertical space (the text height, not 1dp).

**Why it isn't worth it:**
1. **Performance**: a `TextView` is more expensive than an empty `View` (text measurement, text layout, text drawing).
2. **Appearance**: the dashes don't stretch uniformly; it depends on the font.
3. **Accessibility**: TalkBack would read "dash dash dash".
4. **Semantics**: a separator isn't text.

**Remember:** `<View>` is the cheapest way to draw a simple shape. For lines, rectangles, small circles — a `View` with a `background`.

**Where it comes back:** in `movie_item.xml` (ch. 11) there are no separators — the card already has a shadow and margins. Separators are specific to long forms.

</details>

---

## Step 6.9 — Full visual verification

### How

1. Run it. Open `activity_item.xml` in **Design**.
2. Scroll through. Check:
   - Card 1: Title, Genre, Release.
   - Card 2: Budget (with "$ " in front), Duration (bar + value), 0/300 min labels.
   - Card 3: Rating (5 stars), separator, Recommended + switch + Watchlist checkbox, separator, Guidance with 5 radio buttons.
   - Card 4: Poster URL.
   - A pill "Save Movie" button, with an icon.

### Final checklist

- [ ] all 4 `MaterialCardView`s with `materialCardViewFilledStyle`
- [ ] all 13 IDs: `tvTile`, `etTitle`, `tvGenre`, `spGenre`, `etRelease`, `tvBudget`, `etBudget`, `tvDuration`, `tvDurationValue`, `sbDuration`, `tvRating`, `rbRating`, `tvWatched`, `tvWatchedValue`, `swWatched`, `cbOnWatchList`, `tvGuidance`, `rgApproval`, `etPoster`, `btnMovieAction`
- [ ] `ScrollView` with `android:id="@+id/main"`
- [ ] no `TextView` without `layout_width`/`layout_height`
- [ ] all tags closed correctly

> **Count the IDs:** there are 20, but only 13 are used in code. The unused ones: `tvTile`, `tvGenre`, `tvBudget`, `tvDuration`, `tvRating`, `tvWatched`, `tvGuidance`, plus the 5 radio buttons. They're for **accessibility** and for future features.

---

## Step 6.10 — Synthesis exercise: read the file

**Requirement:** open `cod-final/res/layout/activity_item.xml` and go through it top to bottom. For each block, say to yourself: *what widget is it, what ID does it have, what's its role*.

### The file map

```
ScrollView (id=main)
└── LinearLayout vertical
    ├── TextView "Movie details"
    ├── TextView "Fill in the information below..."
    ├── MaterialCardView [Basics]
    │   └── LinearLayout
    │       ├── TextView "Basics"
    │       ├── TextView tvTile + TextInputLayout + etTitle
    │       ├── TextView tvGenre + MaterialCardView + Spinner spGenre
    │       └── TextInputLayout + etRelease
    ├── MaterialCardView [Production]
    │   └── LinearLayout
    │       ├── TextView "Production"
    │       ├── TextView tvBudget + TextInputLayout + etBudget
    │       ├── LinearLayout (tvDuration + tvDurationValue)
    │       ├── SeekBar sbDuration
    │       └── LinearLayout (0 min / 300 min)
    ├── MaterialCardView [Your verdict]
    │   └── LinearLayout
    │       ├── TextView "Your verdict"
    │       ├── TextView tvRating + RatingBar rbRating
    │       ├── View (separator)
    │       ├── LinearLayout (tvWatched + tvWatchedValue | swWatched | cbOnWatchList)
    │       ├── View (separator)
    │       ├── TextView tvGuidance
    │       └── HorizontalScrollView + RadioGroup rgApproval (5 buttons)
    ├── MaterialCardView [Poster]
    │   └── LinearLayout
    │       ├── TextView "Poster"
    │       └── TextInputLayout + etPoster
    └── MaterialButton btnMovieAction
```

---

## Step 6.11 — Test questions

1. Why does `SeekBar` have an explicit `android:min="0"`, even though 0 is the default?
2. What does `app:prefixText` do, and why doesn't it appear in `getText()`?
3. Why `RadioGroup` and not 5 independent `RadioButton`s?
4. What's the functional difference between `MaterialSwitch` and `MaterialCheckBox`?
5. Why `layout_marginBottom="24dp"` on the last card but `16dp` on the others?

<details>
<summary>Answers — explained</summary>

**1. Why an explicit `android:min="0"`?**
It's **documentation**: it shows the reader the range is [0, 300]. Technically it's redundant (0 is the default), but it makes the intent clear. And it's necessary if you want to change the minimum later — you see immediately where it is.

**2. What does `app:prefixText` do?**
It shows fixed text before the typed value, **inside** the field. `getText()` returns only what the user typed, without the prefix. It's purely visual.

**3. Why `RadioGroup`?**
Because it guarantees **exclusivity**: selecting one button deselects the other. Without a group you could select all 5 at once. And it gives you `getChildCount()` / `getChildAt()` for generic iteration.

**4. `MaterialSwitch` vs `MaterialCheckBox`?**
Functionally: **identical**. Both extend `CompoundButton`, both have `isChecked()`, `setChecked()`, `setOnCheckedChangeListener()`. Only the **appearance** (sliding vs square) and the **semantics** (state vs selection) differ.

**5. Why 24dp on the last card?**
More space between "content" and "final action". It's a design rule: the primary action should be visibly separated from the form.

</details>

---

## Step 6.12 — Compare with the original

```bash
diff "cod-final/res/layout/activity_item.xml" \
     "_progres/Movies1097/app/src/main/res/layout/activity_item.xml"
```

If `diff` shows nothing — your file is identical to `d719ffc`. If it shows differences, check whether they're:
- **intentional** (you changed something in the exercises) → OK
- **accidental** (you forgot an attribute) → fix it

---

## Chapter 06 summary

- `prefixText` = visual text, not part of the value.
- `SeekBar` with `min`/`max` + hardcoded labels = technical debt.
- `RatingBar` with `stepSize` controls the granularity.
- `MaterialSwitch` and `MaterialCheckBox` are functionally identical, visually different.
- `RadioGroup` guarantees exclusivity; iterating over the children makes the code generic.
- A filled `MaterialButton` = primary action, `cornerRadius = height/2` = pill.

**Next chapter:** [07 - ItemActivity - reading and writing.md](07%20-%20ItemActivity%20-%20reading%20and%20writing.md)
