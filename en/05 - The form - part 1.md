# Chapter 05 — The form, part 1: structure and basic fields

**Objective:** `activity_item.xml` — a `ScrollView` with 4 Material cards. In this chapter you build the **structure** + **Card 1 (Basics)**: title, genre, release date. The remaining cards come in ch. 06.

**Estimated time:** 45–60 min.

**Final file:** `cod-final/res/layout/activity_item.xml` (21505 B, 451 lines, SHA-256 `242620d52ee3be63…`)

> **Tip:** this is the biggest file in the project. **Don't write it in one go.** Build it card by card, run it after each one, check it visually. A 451-line file written blind has a good chance of having an unclosed tag somewhere.

---

## Step 5.1 — Why `ScrollView` as the root

### Why

The form has 4 cards + a button, much taller than a phone screen. Without scrolling, the last fields would be unreachable.

`ScrollView` does **exactly one thing**: it allows vertical scrolling of a single child.

### The `ScrollView` rule

> `ScrollView` allows **exactly one child**. If you put two, the build fails with:
> `ScrollView can host only one direct child`

That's why the child is a vertical `LinearLayout`, which holds all the cards.

### How

```xml
<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- the cards -->

    </LinearLayout>
</ScrollView>
```

### The attributes, explained

| Attribute | Why |
|---|---|
| `android:id="@+id/main"` | for the insets — same as in `activity_main.xml` |
| `android:background="?attr/colorSurface"` | background from the theme (white in light, dark grey in dark). `?attr/` = a theme attribute, not a fixed colour |
| `android:fillViewport="true"` | if the content is shorter than the screen, stretch it to fill. Without it, you get a white background only as tall as the content, grey elsewhere |
| `paddingHorizontal="16dp"` | left + right, 16dp (Material standard) |
| `paddingTop/Bottom="24dp"` | space top/bottom |

### Why `?attr/colorSurface` and not `#FFFFFF`

`?attr/colorSurface` **resolves to the theme colour**. In light mode = white, in dark mode = dark grey. If you wrote `#FFFFFF`, in dark mode you'd have white on black — white text would be invisible.

> **Remember:** `?attr/name` = "ask the theme". `@color/name` = "use the fixed colour". For surface, text and outline colours, **always** `?attr/`.

### `paddingHorizontal` vs `paddingStart/End`

`paddingHorizontal` is a shortcut for `paddingLeft` + `paddingRight`. But in RTL (Arabic), `paddingLeft` stays the physical left, which is wrong. The RTL-correct variant would be `paddingStart` + `paddingEnd`.

> **Careful:** `android:paddingHorizontal` was introduced in API 26. The repo has `minSdk 33`, so it's fine. On older APIs you'd need `paddingLeft` + `paddingRight` or `paddingStart` + `paddingEnd`.

### Exercise 5.1

**Requirement:** remove `android:fillViewport="true"`. Run it on a tall emulator and observe the background. Then put it back.

<details>
<summary>Solution — explained</summary>

**What was done:** we removed `android:fillViewport="true"` from the `ScrollView`.

**What you see:** if the form is shorter than the screen (not the case here, but imagine it), the child `LinearLayout` stretches only as far as the content. The rest of the screen keeps the **window** background (which may be another colour), not `colorSurface`.

**Why:** `ScrollView` measures its child with `wrap_content` (the content height). `fillViewport="true"` tells it: "if it's smaller than the viewport, stretch it to the viewport height".

**Remember:**
1. `fillViewport` is useful when you want the background to cover the whole screen regardless of content.
2. In `activity_item.xml` the content is taller than the screen anyway, so the effect is only visible on tablets or in landscape.
3. It's good practice to always set it on a `ScrollView` with a single `LinearLayout` child.

**Where it comes back:** it doesn't come back explicitly, but it's relevant in ch. 11 if you put a `RecyclerView` inside a `ScrollView` — there `fillViewport` doesn't help, because the `RecyclerView` has its own scroll. That's solved with `nestedScrollingEnabled="false"` or, better, with a single `RecyclerView` with headers.

</details>

---

## Step 5.2 — The form header

### Why

The first two `TextView`s aren't inside a card. They're the screen title ("Movie details") and a subtitle ("Fill in the information below and save."). Their role: orientation.

### How

```xml
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Movie details"
    android:textAppearance="?attr/textAppearanceHeadlineMedium"
    android:textColor="?attr/colorOnSurface"
    android:textStyle="bold" />

<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:layout_marginBottom="20dp"
    android:text="Fill in the information below and save."
    android:textAppearance="?attr/textAppearanceBodyMedium"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

### Why `textAppearance` and not `textSize`

`?attr/textAppearanceHeadlineMedium` is a **complete style** from the Material 3 theme: size, weight, spacing, line height. `textSize="28sp"` would give only the size, without the rest.

> **Remember:** in Material 3 you use the **theme typography** (`textAppearance*`), not hardcoded values. That's how it stays consistent across screens.

### The colour hierarchy

| Attribute | Role | Where it's used |
|---|---|---|
| `?attr/colorOnSurface` | primary text | titles, values |
| `?attr/colorOnSurfaceVariant` | secondary text | subtitles, labels |
| `?attr/colorPrimary` | accent | section titles, active values |
| `?attr/colorOutline` | outline | field borders |
| `?attr/colorOutlineVariant` | weak outline | separators |

This hierarchy is **the whole Material 3 philosophy**: you don't pick colours, you pick **roles**. The theme resolves them.

### Exercise 5.2

**Requirement:** change `?attr/textAppearanceHeadlineMedium` to `?attr/textAppearanceDisplayLarge`. Run it. What do you notice? Go back.

<details>
<summary>Solution — explained</summary>

**What was done:** we changed the typography style of the title.

**What you see:** "Movie details" becomes **huge** (Display Large is ~57sp in Material 3, versus Headline Medium at ~28sp). It probably wraps onto two lines.

**Why:** `textAppearance*` are **scales** defined by Material 3. Each has its own size, weight, letter-spacing and line-height.

**Remember:**
1. The Material 3 scale: `DisplayLarge/Medium/Small`, `HeadlineLarge/Medium/Small`, `TitleLarge/Medium/Small`, `BodyLarge/Medium/Small`, `LabelLarge/Medium/Small`.
2. The golden rule: **one `Display`** per screen (if needed), `Headline` for screen titles, `Title` for section titles, `Body` for text, `Label` for field labels.
3. Don't mix `textSize` with `textAppearance` — the latter overrides the former.

**Where it comes back:** through the rest of the form. You'll see `TitleMedium` on the card titles ("Basics", "Production"), `LabelLarge` on field labels ("Title", "Genre"), `LabelSmall` on the `SeekBar` min/max values.

</details>

---

## Step 5.3 — `MaterialCardView` as a section container

### Why

The form is split into 4 visual sections: **Basics**, **Production**, **Your verdict**, **Poster**. Each is a card with rounded corners and a slightly different background.

`MaterialCardView` is the container. It's not just "a box with a shadow" — it's a Material component with predefined styles.

### How

```xml
<com.google.android.material.card.MaterialCardView
    style="?attr/materialCardViewFilledStyle"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:cardCornerRadius="20dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <!-- the card content -->

    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

### The attributes, explained

| Attribute | Why |
|---|---|
| `style="?attr/materialCardViewFilledStyle"` | Material 3 style: `surfaceContainerHighest` background, no shadow. Alternative: `materialCardViewOutlinedStyle` (transparent background, outline) |
| `layout_marginBottom="16dp"` | space between cards |
| `app:cardCornerRadius="20dp"` | rounded corners (Material 3 uses 12–28dp) |
| vertical `LinearLayout` + `padding="16dp"` | the content is stacked vertically, with inner padding |

### Why `style` and not individual attributes

`style="?attr/materialCardViewFilledStyle"` brings **a whole set** of attributes (background, shadow, outline, ripple). If you wrote them individually, you'd miss some and lose consistency with the theme.

> **Remember:** `style` = a set of reusable attributes. In Material 3, styles are exposed as `?attr/...` so they can be overridden by the theme.

### Why `wrap_content` on height

The card has to grow with its content. `match_parent` would make every card fill the whole screen.

### Exercise 5.3

**Requirement:** change `materialCardViewFilledStyle` to `materialCardViewOutlinedStyle` on the first card. Run it. What difference do you see?

<details>
<summary>Solution — explained</summary>

**What was done:** we changed the first card's style.

**What you see:**
- **Filled**: light grey background (in light mode), no shadow, no outline. The card "stands out" through colour.
- **Outlined**: transparent background (or `surface`), with a thin 1dp outline in `colorOutline`. The card "stands out" through a line.

**Why:** Material 3 has two card styles for two contexts. `Filled` for content that needs to stand out; `Outlined` for dense lists or when you want less visual weight.

**Remember:**
1. Both styles respect the theme (light/dark) automatically.
2. `Outlined` has `cardElevation=0`; `Filled` also has 0 in M3 (shadows were replaced by tonal colours).
3. Don't mix styles in the same screen without a reason — here all 4 cards are `Filled`.

**Where it comes back:** `movie_item.xml` (ch. 11) uses `MaterialCardView` **without** `style`, with an explicit `app:cardElevation="3dp"` — because there the card is a list item, not a form section. You'll see the difference in approach.

</details>

---

## Step 5.4 — `TextInputLayout` + `TextInputEditText`

### Why

A plain `EditText` looks like a line. `TextInputLayout` is the **container** that adds:

- a floating hint (a label that rises when you type);
- an outline (outlined) or a background (filled);
- start/end icons;
- error messages;
- prefix/suffix.

`TextInputEditText` is the specialised `EditText` that works correctly inside a `TextInputLayout`.

> **The rule:** `TextInputLayout` has **exactly one** child, which must be a `TextInputEditText` (or a nested `TextInputLayout`, but that's rare).

### How — the "Title" field

```xml
<TextView
    android:id="@+id/tvTile"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Title"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

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

### Why a separate `TextView` above

You could use the `TextInputLayout`'s `hint` as the label. But the repo chooses another approach: a `TextView` **above** ("Title"), plus `app:hintEnabled="false"` which disables the floating hint, plus `android:hint` on the `TextInputEditText` as a placeholder.

**Why?** Because the label above stays **visible all the time**, including when the field is filled. The floating hint moves into the outline and becomes small. For a long form, the fixed label is more readable.

> **Naming trap:** `android:id="@+id/tvTile"` — "Tile", not "Title". It's a **typo in the repo**. Don't fix it if you want fidelity, but know it's a typo. It isn't used in code (it doesn't appear in `initControls`), so it breaks nothing.

### `app:hintEnabled="false"`

Disables the `TextInputLayout`'s floating hint. If it were `true` (the default), you'd have **two** labels: the `TextView` above and the floating hint in the outline. Redundant.

### `app:endIconMode="clear_text"`

Adds an "X" on the right of the field that clears the text. Useful for long fields.

Possible values: `none`, `clear_text`, `password_toggle`, `dropdown_menu`, `custom`.

### `android:inputType`

| Value | Effect |
|---|---|
| `textCapWords` | text keyboard, each word capitalised |
| `numberDecimal` | numeric keyboard with decimals |
| `date` | keyboard with digits and `/` |
| `textUri` | keyboard with `/` and `.com` |

`inputType` does **two** things: it picks the keyboard and it **restricts** the accepted characters.

### Exercise 5.4

**Requirement:** change `inputType` from `textCapWords` to `textPassword` on the Title field. Run it, type something. What happens? Why would you never do this here?

<details>
<summary>Solution — explained</summary>

**What was done:** we changed `android:inputType="textCapWords"` to `android:inputType="textPassword"`.

**What you see:** the typed text appears as **dots** (••••). The keyboard is a normal text one, but the characters are masked.

**Why:** `textPassword` is a flag that tells the `EditText` to mask the text and not save it into suggestions. It's for passwords, obviously.

**Remember:**
1. `inputType` combines **three** dimensions: class (text/number/phone), variation (capWords, password) and flags (noSuggestions, visiblePassword).
2. `textPassword` on a movie title would make the app unusable — but it's a good demonstration that `inputType` **changes behaviour**, not just the keyboard.
3. For URLs, `textUri` is the right choice (ch. 06, poster).

**Where it comes back:** on the Budget field (`numberDecimal`) and the Poster field (`textUri`). You'll see that `numberDecimal` **rejects letters** — if you try to type "abc", nothing happens.

</details>

---

## Step 5.5 — `Spinner` with `android:entries`

### Why

Genre is a choice from 10 fixed options. A `Spinner` (dropdown) is the right widget: it takes little space and shows the options on demand.

### How

The repo wraps the `Spinner` in a `MaterialCardView` to give it an outline that looks like the other `OutlinedBox` fields:

```xml
<TextView
    android:id="@+id/tvGenre"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Genre"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.card.MaterialCardView
    style="?attr/materialCardViewOutlinedStyle"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:layout_marginBottom="16dp"
    app:cardBackgroundColor="@android:color/transparent"
    app:cardCornerRadius="4dp"
    app:strokeColor="?attr/colorOutline">

    <Spinner
        android:id="@+id/spGenre"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/movie_genre"
        android:paddingStart="4dp"
        android:spinnerMode="dropdown" />
</com.google.android.material.card.MaterialCardView>
```

### Why the `MaterialCardView` trick

The native `Spinner` has no outline. To make it look consistent with the `OutlinedBox` `TextInputLayout`s (which have a 1dp outline and 4dp corners), you wrap it in an `Outlined` card with:

- `cardBackgroundColor="@android:color/transparent"` — so it doesn't cover the parent card's background;
- `cardCornerRadius="4dp"` — the same as `TextInputLayout`;
- `strokeColor="?attr/colorOutline"` — the same outline colour;
- `layout_height="56dp"` — the standard height of a Material field.

The result: visually, it looks like an `OutlinedBox` field with a dropdown.

### `android:entries` vs adapter

Just like with `ListView`, `android:entries="@array/movie_genre"` automatically creates an `ArrayAdapter<String>` from the resource. Here it is **not** replaced by code — `ItemActivity` doesn't call `spGenre.setAdapter(...)`. So `entries` is the real source.

> **Remember:** in the `ListView` from `MainActivity`, `entries` was replaced by `setAdapter`. In the `Spinner`, `entries` stays. Same syntax, different behaviour depending on what the code does.

### `spinnerMode="dropdown"`

Two modes:
- `dropdown` — a popup under the spinner (the default on modern Android);
- `dialog` — a modal dialog.

`dropdown` is faster for short lists.

### Exercise 5.5

**Requirement:** add a second `Spinner` below Genre, for "Language" (Romanian, English, French), with `android:id="@+id/spLanguage"`. Don't use it in code. Check it visually.

<details>
<summary>Hint</summary>

The simplest way: add a new `string-array` in `strings.xml` and copy the `TextView` + `MaterialCardView` + `Spinner` structure.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added to `strings.xml`:

```xml
<string-array name="movie_language">
    <item>Română</item>
    <item>Engleză</item>
    <item>Franceză</item>
</string-array>
```

and in the layout, after the Genre block:

```xml
<TextView
    android:id="@+id/tvLanguage"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Language"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.card.MaterialCardView
    style="?attr/materialCardViewOutlinedStyle"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:layout_marginBottom="16dp"
    app:cardBackgroundColor="@android:color/transparent"
    app:cardCornerRadius="4dp"
    app:strokeColor="?attr/colorOutline">

    <Spinner
        android:id="@+id/spLanguage"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/movie_language"
        android:paddingStart="4dp"
        android:spinnerMode="dropdown" />
</com.google.android.material.card.MaterialCardView>
```

**How to check:** run it, tap the spinner, see the 3 languages. Nothing is saved anywhere — it's visual only.

**Why it works without code:** `android:entries` is enough to populate it. The `Spinner` creates its adapter itself.

**Remember:**
1. A `Spinner` **without** `entries` and **without** `setAdapter` = empty.
2. A `Spinner` with `entries` = populated, with no line of code.
3. To read the selection: `spGenre.getSelectedItem().toString()`.

**Where it comes back:** in ch. 07, `saveMovie()` does exactly `movie.setGenre(spGenre.getSelectedItem().toString())`. And `fillForm` searches the text in the list to set the selection — because `Spinner` has no `setSelectionByText`, only `setSelection(index)`.

</details>

---

## Step 5.6 — The date field: `TextInputLayout` with an icon

### Why

The release date isn't typed — it's picked from a calendar. But the field has to look like a normal field, with a calendar icon.

### How

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="true"
    app:startIconContentDescription="Release date"
    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etRelease"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Release date"
        android:inputType="date" />
</com.google.android.material.textfield.TextInputLayout>
```

### The difference from the Title field

| | Title | Release |
|---|---|---|
| `hintEnabled` | `false` | **`true`** |
| separate label above | yes (`tvTile`) | **no** |
| start icon | no | **yes** (`ic_menu_my_calendar`) |
| `inputType` | `textCapWords` | `date` |

Here the floating hint is used: "Release date" rises into the outline when you type. There's no `TextView` above.

**Why different approaches?** A design inconsistency in the repo. Both work. In the exam, if you're asked to explain, say: "the Title field has a fixed label; the Release field uses a floating hint". It's not a mistake, it's a choice.

### `app:startIconDrawable`

The icon on the left. `@android:drawable/ic_menu_my_calendar` is a **system** icon (Android has had it since API 1). You don't need a file of your own.

### `app:startIconContentDescription`

Text for TalkBack. Mandatory when you have a `startIconDrawable`, otherwise lint errors out.

### Why `inputType="date"` even though the field is read-only in practice

The user **doesn't type** the date — they pick it from a `DatePickerDialog` (ch. 07). But `inputType="date"` makes the keyboard numeric with `/`, in case they want to type it manually. And the `SimpleDateFormat` in the code can parse "16/07/2010".

> **Careful:** the field is **not** `editable=false`. The user can type. But `showReleaseDatePicker()` parses the existing text, so if they type something invalid the `ParseException` is **ignored** (`catch (ParseException ignored) { }`) and the calendar starts from the current date. See ch. 07.

### Exercise 5.6

**Requirement:** add `app:endIconMode="clear_text"` to the Release field. Run it, type a date, press X. What happens to `releaseCal`?

<details>
<summary>Solution — explained</summary>

**What was done:** we added `app:endIconMode="clear_text"` to the date's `TextInputLayout`.

**What you see:** an X appears on the right. You press it, the text disappears.

**What happens to `releaseCal`:** **nothing.** `releaseCal` keeps its previous value (or `Calendar.getInstance()` if you never picked a date).

**Why:** `clear_text` clears **only the text in the `EditText`**. It has nothing to do with `releaseCal`, which is a separate Java field. In `saveMovie()`, `movie.setRelease(releaseCal.getTime())` — so the movie gets the **old date**, not `null`, even though the field is empty.

**Remember:**
1. The **source of truth** is `releaseCal`, not the text in the `EditText`. The text is just a representation.
2. If you want clearing to reset the date, you must add a listener on `endIconMode` or check in `saveMovie` whether the text is empty.
3. It's a **real bug** in the repo: you can save a movie with the date you picked earlier, even though the field looks empty.

**Where it comes back:** in ch. 07, `showReleaseDatePicker()` **parses the text** to initialise the calendar. If the text is empty, `releaseCal` stays as it was. So clearing the text resets nothing — and it's a trap you'll see in the exam.

</details>

---

## Step 5.7 — Visual verification of Card 1

### How

1. Run it. Open `ItemActivity` — but **you don't have navigation yet**. So temporarily, to see the layout:
   - Open `activity_item.xml` → the **Design** tab.
   - Or temporarily change `setContentView(R.layout.activity_main)` in `MainActivity` to `setContentView(R.layout.activity_item)`. **Revert immediately afterwards.**
2. Check:
   - The title "Movie details" at the top.
   - The "Basics" card with the "Basics" label in `colorPrimary`.
   - The Title field with a label above and an X on the right.
   - The Genre spinner with an outline, 56dp tall.
   - The Release field with a calendar icon on the left.

### Checklist

- [ ] `ScrollView` with `android:id="@+id/main"`, `fillViewport="true"`, `background="?attr/colorSurface"`
- [ ] single child `LinearLayout` vertical, padding 16/24/24
- [ ] header: 2 `TextView`s
- [ ] Card 1 `MaterialCardView` with `materialCardViewFilledStyle`, `cardCornerRadius="20dp"`
- [ ] inside the card: vertical `LinearLayout`, padding 16dp
- [ ] "Basics" label with `TitleMedium` + `colorPrimary`
- [ ] `tvTile` + `TextInputLayout` (hintEnabled=false, endIconMode=clear_text) + `etTitle`
- [ ] `tvGenre` + `MaterialCardView` outlined + `Spinner` with `entries`
- [ ] `TextInputLayout` with `startIconDrawable` + `etRelease`

---

## Step 5.8 — Reflection exercise

**Requirement:** why does `TextInputLayout` have `layout_width="match_parent"` but the label `TextView` has `wrap_content`?

<details>
<summary>Answer — explained</summary>

**What was done:** the labels (`tvTile`, `tvGenre`) are `wrap_content`; the fields (`TextInputLayout`, the `MaterialCardView` with the spinner) are `match_parent`.

**Why:** a label should take up **only as much as its text**. If it were `match_parent`, it would be an invisible box as wide as the screen — no visual effect, but pointless. A field should take up **the full available width**, so you have room to type.

**Remember:**
1. `wrap_content` = as much as the content.
2. `match_parent` = as much as the parent.
3. `0dp` + `layout_weight` = share the remaining space (see ch. 06, the Duration row).

**Where it comes back:** in ch. 06, the row with `tvDuration` + `tvDurationValue` uses `0dp` + `layout_weight="1"` on the first one, to push the value to the right. Three ways of sizing, three purposes.

</details>

---

## Chapter 05 summary

- `ScrollView` = one child, `fillViewport` for a full background.
- `MaterialCardView` with `style="?attr/materialCardViewFilledStyle"` = a section.
- `TextInputLayout` + `TextInputEditText` = a field with outline, icons, hint.
- `hintEnabled="false"` + a `TextView` above = a fixed label.
- `Spinner` inside an outlined `MaterialCardView` = a dropdown that looks like a field.
- `?attr/color*` = colour roles, not fixed colours.

**Next chapter:** [06 - The form - part 2.md](06%20-%20The%20form%20-%20part%202.md)
