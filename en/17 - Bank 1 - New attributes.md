# Chapter 17 — Requirement bank 1: adding an attribute

**Objective:** to execute "add an attribute" at the exam in 10–15 minutes per attribute, without forgetting any layer and without losing points on a `NullPointerException` or a `NumberFormatException`.

**What the requirement looks like at the exam:** "Add the attribute `<tip> <nume>` to the movie. Display it in the form and in the list." Two requirements, 30 minutes, one attribute or two.

**The chain of 5 steps:** 1. Model  2. Form layout  3. ItemActivity  4. Card layout  5. Adapter
> Rule: model → form → activity → card → adapter.

---

## Exercise 17.1 — `writer` (String): the reference attribute

**Requirement:** Add the `writer` (String) attribute to the movie — the screenwriter's name. Display it in the form, below the release date, and in the list.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private String writer;` next to `private String poster = null;`.
2. In the 10-parameter constructor, add `String writer` at the end of the list and `this.writer = writer;` at the end of the body.
3. In `toString()`, add the line `", writer='" + writer + '\'' +` after the `poster` line.
4. Add `getWriter()` and `setWriter()` next to `getPoster()`/`setPoster()`.
5. Compile. Three errors will show up in `MainActivity.addSampleMovies()` — add the 11th argument to each of the three `new Movie(...)` calls.
6. Open `res/layout/activity_item.xml`, find the `</com.google.android.material.textfield.TextInputLayout>` of `etRelease` (Card 1, Basics) and insert the label `TextView` plus the `TextInputLayout` with `etWriter` right there.
7. Open `activities/ItemActivity.java` and make four additions: the `private EditText etWriter;` field, the line in `initControls()`, the line in `fillForm()`, the line in `saveMovie()`.
8. Open `res/layout/movie_item.xml`: add the `movieWriter` `TextView` after `movieFacts`. In `MovieAdapter`, three lines: field, `findViewById`, `setText`.
9. Verify: Run, add a movie with "Christopher Nolan" in Writer. The list must show `writer='Christopher Nolan'` in the `toString()` text. Tap the movie: the Writer field is filled in.

**Hint 1 — if you get stuck at step 1:** the field is declared next to the other fields, at the top of the class, not in the constructor. If you put it in the constructor, the compiler treats it as a parameter and `this.writer` no longer exists.

**Hint 2 — if you get stuck at step 3:** `toString()` is right below the constructor. The new line goes between `", poster='" + poster + '\'' +` and `'}'`, with the comma at the start — the same style as all the other lines.

<details>
<summary>Solution — explained</summary>

**What was done:** I added the field in the model, the field in the form, the read/write in `ItemActivity`, the `TextView` in the card and the binding in the adapter.

**Code:**

Step 1 — `model/Movie.java`, four places:

```java
// 1a. the field, next to the others
private String writer;

// 1b. the full constructor — new parameter, AT THE END, after poster
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String writer) {
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
    this.writer = writer;          // the new line
}

// 1c. toString() — after the poster line, before '}'
", writer='" + writer + '\'' +

// 1d. getter/setter, next to the others
public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 1 (Basics), right after the `TextInputLayout` of `etRelease`:

```xml
<TextView
    android:id="@+id/tvWriter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Writer"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etWriter"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Writer"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Step 3 — `activities/ItemActivity.java`, four places:

```java
// 3a. the field, next to the others
private EditText etWriter;

// 3b. initControls() — at the end of the method
etWriter = findViewById(R.id.etWriter);

// 3c. fillForm() — at the end of the method
etWriter.setText(existing.getWriter());

// 3d. saveMovie() — before building the Intent
movie.setWriter(etWriter.getText().toString());
```

Step 4 — `res/layout/movie_item.xml`, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Writer"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 5 — `MovieAdapter.java`, three places:

```java
// 5a. field in MovieViewHolder
private final TextView movieWriter;

// 5b. in the MovieViewHolder constructor
movieWriter = itemView.findViewById(R.id.movieWriter);

// 5c. in bind()
movieWriter.setText(movie.getWriter() != null ? movie.getWriter() : "");
```

Step 6, mandatory — `activities/MainActivity.java`, `addSampleMovies()`. All three calls get an 11th argument, otherwise it **does not compile**:

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
        "Christopher Nolan"));   // ← the new argument
```

**Why:** each layer has its own representation of the same value — `String` in the model, `EditText` in the form, `setText`/`getText` in the activity, `TextView` in the card, `bind` in the adapter. A new attribute means five representations, not one.

**Remember:**
1. **The constructor is changed, not overloaded.** If you add a second constructor with 11 parameters and keep the 10-parameter one, you have two nearly identical constructors and `addSampleMovies` keeps working with the old one — the demo movie has `writer = null` and you never notice. You change the signature and fix the three calls.
2. **The empty constructor stays untouched.** It is declared at the end of `Movie` and is used by `saveMovie()` (`Movie movie = new Movie();`). Don't touch it.
3. **At `d719ffc` the card is not used.** The list in `MainActivity` is a `ListView` with an `ArrayAdapter` on `android.R.layout.simple_list_item_1`, so it displays **`toString()`**. Steps 4 and 5 have no visible effect until you do `RecyclerView` + `MovieAdapter` (chapter 11, steps 11.6–11.8). At the exam, if the teacher asks for "in the list", the step that matters at `d719ffc` is **1c**.
4. `ItemActivity` uses `findViewById`, not ViewBinding (although it is enabled in Gradle — see chapter 13). So you don't need to regenerate any `Binding` class.
5. If you forget step 3d, the attribute is saved as `null` on every edit: `saveMovie()` builds a **new** `Movie`, it doesn't modify the existing one.

**Where it applies:** any `String` attribute — `writer`, `country`, `studio`, `language`. The chain is identical.

</details>

---

## Exercise 17.2 — `year` (Integer): the numeric attribute that can be null

**Requirement:** Add the `year` (Integer) attribute to the movie — the release year. Numeric field in the form, four digits. Display it in the list.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private Integer year;` — with a capital `I`, it's a class, not a primitive.
2. In the full constructor, add `Integer year` at the end and `this.year = year;`.
3. In `toString()`, add `", year=" + year +`.
4. Add `getYear()` and `setYear()`; the return type and the parameter are `Integer`.
5. Compile and fix the three calls in `addSampleMovies()`: the 11th argument, `2010`, `1995`, `1999`.
6. In `activity_item.xml`, Card 1, after `etRelease`: `TextView` + `TextInputLayout` with `etYear`, `android:inputType="number"` and `android:maxLength="4"`.
7. In `ItemActivity.java`: the field, `initControls()`, `fillForm()` — with `String.valueOf(...)` — and `saveMovie()` — with an `isEmpty()` guard before `Integer.parseInt`.
8. Verify: Run, add a movie with the year 2024. The list shows `year=2024`. Edit a movie, clear the year, save — there must be no crash, and the list shows `year=null`.

**Hint 1 — if you get stuck at step 1:** `Integer` is a class in `java.lang`, like `String`. It needs no import, it's declared with a capital letter and it accepts `null`. `int` is the primitive, with the default value `0`.

**Hint 2 — if you get stuck at step 7:** `etYear.setText(existing.getYear())` compiles, but at runtime it throws `Resources$NotFoundException`. The `Integer` is unboxed to `int` and reaches the `setText(int resid)` overload, which looks for a resource id. Force a `String` with `String.valueOf(...)`.

<details>
<summary>Solution — explained</summary>

**What was done:** I added the attribute as `Integer` (boxed, not primitive), read it with a guarded `parseInt` and displayed it with `String.valueOf`.

**Code:**

Step 1 — `model/Movie.java`:

```java
// 1a. the field — Integer, not int
private Integer year;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, Integer year) {
    // ... the other assignments ...
    this.year = year;
}

// 1c. toString()
", year=" + year +

// 1d. getter/setter
public Integer getYear() {
    return year;
}

public void setYear(Integer year) {
    this.year = year;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 1 (Basics), after `etRelease`:

```xml
<TextView
    android:id="@+id/tvYear"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Year"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etYear"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Year"
        android:inputType="number"
        android:maxLength="4" />
</com.google.android.material.textfield.TextInputLayout>
```

Step 3 — `activities/ItemActivity.java`:

```java
// 3a. the field
private EditText etYear;

// 3b. initControls()
etYear = findViewById(R.id.etYear);

// 3c. fillForm() — String.valueOf, NOT getYear() directly
etYear.setText(existing.getYear() != null
        ? String.valueOf(existing.getYear())
        : "");

// 3d. saveMovie() — guarded parsing
String yearText = etYear.getText().toString().trim();
movie.setYear(yearText.isEmpty() ? null : Integer.parseInt(yearText));
```

Step 4 — `res/layout/movie_item.xml`, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieYear"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Year"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 5 — `MovieAdapter.java`:

```java
private final TextView movieYear;

movieYear = itemView.findViewById(R.id.movieYear);

movieYear.setText(movie.getYear() != null ? String.valueOf(movie.getYear()) : "");
```

Step 6 — `MainActivity.addSampleMovies()`: the 11th argument on all three:

```java
        "https://example.com/posters/inception.jpg",
        2010));
```

**Why:** `Integer` and not `int` because "unknown year" is real information. With `int`, all three demo movies would have `year = 0` until you set them, and the card would show "0" — a lie. With `Integer`, the default value is `null` and you can display nothing.

**Remember:**
1. **The `setText(Integer)` trap.** `TextView` has two methods: `setText(CharSequence)` and `setText(int resid)`. If you write `etYear.setText(existing.getYear())`, the compiler **unboxes** the `Integer` to `int` and picks the second one — that is, it treats the year 2010 as a **resource id**. Result: `Resources$NotFoundException` at runtime. The fix is `String.valueOf(...)`, which forces a `String`.
2. `Integer.parseInt("")` throws `NumberFormatException`. Hence `isEmpty() ? null : ...`. `trim()` first, so a field with a single space doesn't pass as a number.
3. `android:inputType="number"` shows the numeric keyboard and blocks the minus sign and the comma. `maxLength="4"` limits it to four digits — but it doesn't validate that it's a plausible year ("0000" goes through).
4. `toString()` prints `year=null` for the missing value. At `d719ffc` that's all you see in the list — acceptable for the test.
5. The bug in `etBudget` is right next door: `Double.parseDouble(etBudget.getText().toString())` throws if the user types a decimal comma. It's not your job to fix it at the exam, but recognise it if you see it.

**Where it applies:** any numeric attribute that can be missing — `year`, `oscarsWon`, `seasonCount`.

</details>

---

## Exercise 17.3 — `popular` (boolean): the flag with a default value

**Requirement:** Add the `popular` (boolean) attribute to the movie — the movie is popular with the audience. In the form, a `Switch`. In the list, a "Popular" chip.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private boolean popular;` next to `private boolean watched;`.
2. In the full constructor, add `boolean popular` at the end and `this.popular = popular;`.
3. In `toString()`, add `", popular=" + popular +`.
4. Add `isPopular()` — not `getPopular()` — and `setPopular(boolean)`.
5. Compile and fix the three calls in `addSampleMovies()`: the 11th argument, `true` or `false`.
6. In `activity_item.xml`, Card 3 (Your verdict), after the `rgApproval` `RadioGroup`: a row with a "Popular" `TextView` and a `MaterialSwitch` with id `swPopular`. The import for `MaterialSwitch` already exists in `ItemActivity`.
7. In `ItemActivity.java`: the `private MaterialSwitch swPopular;` field, `initControls()`, `fillForm()` with `setChecked(existing.isPopular())`, `saveMovie()` with `movie.setPopular(swPopular.isChecked())`.
8. In `movie_item.xml`, in `movieStatusGroup`, after `chipWatchlist`: a `Chip` with id `chipPopular`. In the adapter: field, `findViewById`, `setVisibility`.
9. Verify: Run, add a movie with the switch on. The list shows `popular=true`. Open a movie with the switch off: the switch must be off, not on.

**Hint 1 — if you get stuck at step 2:** `boolean`, not `Boolean`. The primitive already has the value `false`, so it needs no initialisation in the declaration — and it can't be `null`.

**Hint 2 — if you get stuck at step 7:** if you forget `swPopular.setChecked(...)` in `fillForm`, no error appears. But `saveMovie()` builds a new `Movie`, so on the first edit the movie becomes unpopular — without the user touching the switch.

<details>
<summary>Solution — explained</summary>

**What was done:** I added the `boolean` field, a `MaterialSwitch` in the form, a chip in the card and `setVisibility` in the adapter.

**Code:**

Step 1 — `model/Movie.java`:

```java
// 1a. the field
private boolean popular;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, boolean popular) {
    // ... the other assignments ...
    this.popular = popular;
}

// 1c. toString()
", popular=" + popular +

// 1d. getter/setter — the isX() convention for boolean
public boolean isPopular() {
    return popular;
}

public void setPopular(boolean popular) {
    this.popular = popular;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 3 (Your verdict), after the `rgApproval` `RadioGroup`, before `</LinearLayout>`:

```xml
<View
    android:layout_width="match_parent"
    android:layout_height="1dp"
    android:layout_marginVertical="12dp"
    android:background="?attr/colorOutlineVariant" />

<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:minHeight="48dp"
    android:orientation="horizontal">

    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="Popular"
        android:textAppearance="?attr/textAppearanceBodyLarge"
        android:textColor="?attr/colorOnSurface" />

    <com.google.android.material.materialswitch.MaterialSwitch
        android:id="@+id/swPopular"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
</LinearLayout>
```

Step 3 — `activities/ItemActivity.java`:

```java
// 3a. the field — MaterialSwitch is already imported
private MaterialSwitch swPopular;

// 3b. initControls()
swPopular = findViewById(R.id.swPopular);

// 3c. fillForm()
swPopular.setChecked(existing.isPopular());

// 3d. saveMovie()
movie.setPopular(swPopular.isChecked());
```

Step 4 — `res/layout/movie_item.xml`, in `movieStatusGroup`, after `chipWatchlist`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipPopular"
    style="@style/Widget.Material3.Chip.Suggestion"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Popular"
    android:clickable="false"
    app:chipMinHeight="28dp"
    app:ensureMinTouchTargetSize="false" />
```

Step 5 — `MovieAdapter.java`:

```java
private final Chip chipPopular;

chipPopular = itemView.findViewById(R.id.chipPopular);

chipPopular.setVisibility(movie.isPopular() ? View.VISIBLE : View.GONE);
```

Step 6 — `MainActivity.addSampleMovies()`: the 11th argument, `true` or `false`, on all three.

**Why:** `setVisibility` and not `setText("")`. A chip is a label that either exists or doesn't; if you keep it always visible and only change its text, the card has an empty rectangle for unpopular movies.

**Remember:**
1. **`fillForm` is not optional.** `saveMovie()` builds a new `Movie`. If you forget `swPopular.setChecked(...)`, you edit a popular movie, don't touch the switch, save — and the movie becomes unpopular. The default value `false` is what fools you: it throws no error, it just loses data.
2. **The `isPopular()` convention.** For `boolean`, the getter is `isX()`, not `getX()` — just like `isWatched()` and `isOnWatchlist()` in the model. `getPopular()` would compile, but it would be inconsistent.
3. **`View.GONE` in a `ChipGroup`.** `GONE` removes the chip from the layout, so the other chips close up. `INVISIBLE` keeps the space and leaves a hole.
4. **At `d719ffc` the chip is not visible.** `movie_item.xml` is not used by the `ListView` (see 17.1, point 3). The visible effect at the commit is only `popular=true` in `toString()`. Steps 4–5 become real after the move to `RecyclerView` (chapter 11).
5. `MaterialSwitch` instead of a plain `Switch` — the file already uses `com.google.android.material.materialswitch.MaterialSwitch` for `swWatched`, and the import exists.

**Where it applies:** any boolean flag — `popular`, `awarded`, `remastered`, `availableIn4K`.

</details>

---

## Exercise 17.4 — `imdbScore` (float): the decimal with a comma

**Requirement:** Add the `imdbScore` (float) attribute to the movie — the IMDb rating, between 0 and 10, with one decimal. Decimal field in the form, displayed in the list.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private float imdbScore;` next to `private float rating;`.
2. In the full constructor, add `float imdbScore` at the end and `this.imdbScore = imdbScore;`.
3. In `toString()`, add `", imdbScore=" + imdbScore +`.
4. Add `getImdbScore()` and `setImdbScore(float)`.
5. Compile and fix the three calls in `addSampleMovies()`: the 11th argument with the `f` suffix, for example `8.8f`.
6. In `activity_item.xml`, Card 2 (Production), after `etBudget`: label `TextView` + `TextInputLayout` with `app:suffixText="/ 10"` and `etImdbScore`, `inputType="numberDecimal"`, `maxLength="4"`.
7. In `ItemActivity.java`: the field, `initControls()`, `fillForm()` with `String.valueOf(...)`, `saveMovie()` with `replace(',', '.')` before `Float.parseFloat` and an `isEmpty()` guard.
8. In `movie_item.xml` and the adapter: the `movieImdbScore` `TextView`, bound with `"IMDb " + movie.getImdbScore()`.
9. Verify: Run, type `8,5` with a comma in the field and save. There must be no crash, and the list shows `imdbScore=8.5`.

**Hint 1 — if you get stuck at step 5:** the `float` literal needs the `f` suffix. `8.8` without the suffix is a `double` and doesn't fit a `float` parameter — the error is "incompatible types: possible lossy conversion from double to float".

**Hint 2 — if you get stuck at step 7:** `Float.parseFloat("8,5")` throws `NumberFormatException`, because the parser only accepts a dot. You normalise first — `text.replace(',', '.')` — and parse the result, not the original text.

<details>
<summary>Solution — explained</summary>

**What was done:** I added the `float` attribute, the decimal field and normalised the separator before parsing.

**Code:**

Step 1 — `model/Movie.java`:

```java
// 1a. the field
private float imdbScore;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, float imdbScore) {
    // ... the other assignments ...
    this.imdbScore = imdbScore;
}

// 1c. toString()
", imdbScore=" + imdbScore +

// 1d. getter/setter
public float getImdbScore() {
    return imdbScore;
}

public void setImdbScore(float imdbScore) {
    this.imdbScore = imdbScore;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 2 (Production), after `etBudget`:

```xml
<TextView
    android:id="@+id/tvImdbScore"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="IMDb score"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:suffixText="/ 10">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etImdbScore"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="IMDb score"
        android:inputType="numberDecimal"
        android:maxLength="4" />
</com.google.android.material.textfield.TextInputLayout>
```

Step 3 — `activities/ItemActivity.java`:

```java
// 3a. the field
private EditText etImdbScore;

// 3b. initControls()
etImdbScore = findViewById(R.id.etImdbScore);

// 3c. fillForm() — String.valueOf always gives a dot
etImdbScore.setText(String.valueOf(existing.getImdbScore()));

// 3d. saveMovie() — the comma becomes a dot BEFORE parseFloat
String scoreText = etImdbScore.getText().toString().trim().replace(',', '.');
movie.setImdbScore(scoreText.isEmpty() ? 0f : Float.parseFloat(scoreText));
```

Step 4 — `res/layout/movie_item.xml`, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieImdbScore"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="IMDb 0.0"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 5 — `MovieAdapter.java`:

```java
private final TextView movieImdbScore;

movieImdbScore = itemView.findViewById(R.id.movieImdbScore);

movieImdbScore.setText("IMDb " + movie.getImdbScore());
```

Step 6 — `MainActivity.addSampleMovies()`: the 11th argument, of type `float` — write `8.8f`, with the `f`, otherwise it's a `double` and it won't compile:

```java
        "https://example.com/posters/inception.jpg",
        8.8f));
```

**Why:** `Float.parseFloat` uses a locale-independent dot. A user with a Romanian keyboard types `8,5`, and `Float.parseFloat("8,5")` throws `NumberFormatException` — the app closes on Save. `replace(',', '.')` costs one call and removes the whole bug.

**Remember:**
1. **The decimal comma is the standard trap on any decimal field.** `Double.parseDouble` and `Float.parseFloat` only accept a dot. If you want to accept both, you normalise before parsing.
2. `String.valueOf(float)` always produces a dot, so `fillForm` is safe — you don't need the reverse conversion.
3. `Float.parseFloat("")` throws. Hence the `isEmpty()` guard. `Float.parseFloat("8,")` throws the same way, so the `replace` must be applied before, not after.
4. **`float` vs `double`.** `Movie` already has `double budget` (money, precision) and `float rating` (a score, one decimal). `imdbScore` is also a score → `float`, like `rating`. The literal in `addSampleMovies` needs the `f` suffix.
5. Alternative: instead of an `EditText`, a `RatingBar` with `android:numStars="10"` and `android:stepSize="0.5"`; then `saveMovie` is `movie.setImdbScore(rbImdb.getRating())`, with no parsing at all. Less code, fewer errors — but the teacher asked for a field, not stars.

**Where it applies:** any decimal attribute — `imdbScore`, `price`, `latitude`.

</details>

---

## Exercise 17.5 — `actors` (ArrayList\<String\>): a list in a single field

**Requirement:** Add the `actors` (ArrayList\<String\>) attribute to the movie — the actors' names. In the form, a single text field, names separated by commas. In the list, display them separated by commas.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `import java.util.ArrayList;` at the top and the field `private ArrayList<String> actors = new ArrayList<>();`.
2. In the full constructor, add `ArrayList<String> actors` at the end and `this.actors = actors;`.
3. In `toString()`, add `", actors=" + actors +` — `List.toString()` adds the square brackets by itself.
4. Add `getActors()` and `setActors(ArrayList<String>)`.
5. Compile and fix the three calls in `addSampleMovies()`: the 11th argument is a list, `new ArrayList<>(Arrays.asList("Leonardo DiCaprio", "Joseph Gordon-Levitt"))`. Add `import java.util.Arrays;` in `MainActivity`.
6. In `activity_item.xml`, Card 1, after `etRelease`: label `TextView` + `TextInputLayout` with `etActors` and the hint `"Actor 1, Actor 2, Actor 3"`.
7. In `ItemActivity.java`: the field, `initControls()`, `fillForm()` with `String.join(", ", existing.getActors())` and a `null` guard.
8. In `saveMovie()`: a new list, a loop over `etActors.getText().toString().split(",")`, `trim()` on each element, `isEmpty()` before `add`.
9. In `movie_item.xml` and the adapter: the `movieActors` `TextView`, bound with `String.join(", ", movie.getActors())`.
10. Verify: Run, type `A, B, C` and save — the list shows `actors=[A, B, C]`. Then clear the field and save: it must show `actors=[]`, not `actors=[]` with an empty element inside.

**Hint 1 — if you get stuck at step 1:** initialise the field on the spot, `= new ArrayList<>()`. Otherwise it's `null` until someone sets it, and `toString()` and the card have to check for `null` on every display.

**Hint 2 — if you get stuck at step 8:** `"".split(",")` doesn't return an empty array, it returns `[""]` — an array with a single empty element. Without `if (!trimmed.isEmpty())`, a field left empty produces a list with an empty `String`, and the card shows a lonely comma.

<details>
<summary>Solution — explained</summary>

**What was done:** I added `ArrayList<String>` in the model, an `EditText` where the user writes the comma-separated list, `split` on save and `String.join` on display.

**Code:**

Step 1 — `model/Movie.java`:

```java
import java.util.ArrayList;   // new import, at the top

// 1a. the field — initialised, so it isn't null
private ArrayList<String> actors = new ArrayList<>();

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, ArrayList<String> actors) {
    // ... the other assignments ...
    this.actors = actors;
}

// 1c. toString() — List.toString() already gives "[a, b]"
", actors=" + actors +

// 1d. getter/setter
public ArrayList<String> getActors() {
    return actors;
}

public void setActors(ArrayList<String> actors) {
    this.actors = actors;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 1 (Basics), after `etRelease`:

```xml
<TextView
    android:id="@+id/tvActors"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Actors"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etActors"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Actor 1, Actor 2, Actor 3"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Step 3 — `activities/ItemActivity.java`:

```java
import java.util.ArrayList;   // new import, at the top

// 3a. the field
private EditText etActors;

// 3b. initControls()
etActors = findViewById(R.id.etActors);

// 3c. fillForm() — the list becomes text
etActors.setText(existing.getActors() != null
        ? String.join(", ", existing.getActors())
        : "");

// 3d. saveMovie() — the text becomes a list
ArrayList<String> actors = new ArrayList<>();
for (String name : etActors.getText().toString().split(",")) {
    String trimmed = name.trim();
    if (!trimmed.isEmpty()) {
        actors.add(trimmed);
    }
}
movie.setActors(actors);
```

Step 4 — `res/layout/movie_item.xml`, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieActors"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Actors"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 5 — `MovieAdapter.java`:

```java
private final TextView movieActors;

movieActors = itemView.findViewById(R.id.movieActors);

movieActors.setText(movie.getActors() != null
        ? String.join(", ", movie.getActors())
        : "");
```

Step 6 — `MainActivity.addSampleMovies()`: the 11th argument is a list, not a `String`:

```java
        "https://example.com/posters/inception.jpg",
        new ArrayList<>(Arrays.asList("Leonardo DiCaprio", "Joseph Gordon-Levitt"))));
```

**Why:** a single `EditText` with a separator is the cheapest way to enter a list on a phone. `split` on save, `join` on display — two conversions, both one line each.

**Remember:**
1. **`"".split(",")` returns `[""]`**, an array with a single empty element — not an empty array. Without the `if (!trimmed.isEmpty())` guard, a field left empty produces a list with an empty `String`, and the card shows a lonely comma.
2. **`"a,,b".split(",")` returns `["a", "", "b"]`.** The double comma doesn't disappear, it produces an empty element in the middle. That's why `trim()` + `isEmpty()` are done on each element, not on the whole text.
3. `String.join` is available from API 26; `minSdk` is 33, so it's fine. The alternative without a new import: `android.text.TextUtils.join(", ", list)`.
4. **`ArrayList<String>` is `Serializable`**, so `Intent.putExtra(MOVIE_EXTRA, movie)` works unchanged. `List<String>` would also work at runtime (the real object is still an `ArrayList`), but the requirement says `ArrayList` — declare `ArrayList`.
5. `List.toString()` gives `[Inception, ...]` with square brackets. At `d719ffc` that's what you see in the list, because the `ArrayAdapter` displays `toString()`. Ugly, but visible — enough for the test.
6. `new ArrayList<>(Arrays.asList(...))` needs `import java.util.Arrays;` in `MainActivity`. The alternative without an import: `new ArrayList<>(List.of(...))` — also needs an import.

**Where it applies:** any simple list — `actors`, `tags`, `languages`, `awards`.

</details>

---

## Exercise 17.6 — `ageRestriction` (int): the slider with a displayed value

**Requirement:** Add the `ageRestriction` (int) attribute to the movie — the recommended minimum age, between 0 and 21. In the form, a `SeekBar` with the value shown above it. In the list, "+18" or "All ages".

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private int ageRestriction;` next to `private int duration;`.
2. In the full constructor, add `int ageRestriction` at the end and `this.ageRestriction = ageRestriction;`.
3. In `toString()`, add `", ageRestriction=" + ageRestriction +`.
4. Add `getAgeRestriction()` and `setAgeRestriction(int)`.
5. Compile and fix the three calls in `addSampleMovies()`: the 11th argument, a plain `int`, for example `13`.
6. In `activity_item.xml`, Card 2, after the `sbDuration` + `tvDurationValue` block: the `View` separator, a row with the "Minimum age" label and the `tvAgeRestrictionValue` `TextView`, then the `sbAgeRestriction` `SeekBar` with `android:min="0"` and `android:max="21"`.
7. In `ItemActivity.java`: the two fields, `initControls()`, then the listener in `initListeners()` — which runs before `fillForm()` —, `setProgress` in `fillForm()`, `getProgress()` in `saveMovie()`.
8. In `movie_item.xml` and the adapter: the `movieAgeRestriction` `TextView`, bound with `"+" + movie.getAgeRestriction()` or "All ages" for 0.
9. Verify: Run, drag the slider — the label changes in real time. Save with 18, then reopen the movie: the slider is at 18 **and** the label shows "18+", not "0+".

**Hint 1 — if you get stuck at step 6:** copy the `sbDuration` + `tvDurationValue` block from the same card and change only `android:max` from `300` to `21`. The structure is identical, including the `View` separator above it.

**Hint 2 — if you get stuck at step 7:** the listener must be attached in `initListeners()`, not in `fillForm()`. `onCreate` runs `initControls()` → `initListeners()` → `fillForm()`, so the `setProgress` in `fillForm` triggers `onProgressChanged` and the label updates itself. If you attach the listener after `fillForm`, the label stays at "0+" next to a slider at 18.

<details>
<summary>Solution — explained</summary>

**What was done:** I added the `int` attribute, a `SeekBar` with `max="21"`, a `TextView` for the value and a listener that keeps the label in sync.

**Code:**

Step 1 — `model/Movie.java`:

```java
// 1a. the field
private int ageRestriction;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, int ageRestriction) {
    // ... the other assignments ...
    this.ageRestriction = ageRestriction;
}

// 1c. toString()
", ageRestriction=" + ageRestriction +

// 1d. getter/setter
public int getAgeRestriction() {
    return ageRestriction;
}

public void setAgeRestriction(int ageRestriction) {
    this.ageRestriction = ageRestriction;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 2 (Production), after the `sbDuration` block:

```xml
<View
    android:layout_width="match_parent"
    android:layout_height="1dp"
    android:layout_marginVertical="12dp"
    android:background="?attr/colorOutlineVariant" />

<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:orientation="horizontal">

    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="Minimum age"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <TextView
        android:id="@+id/tvAgeRestrictionValue"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="0+"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorPrimary" />
</LinearLayout>

<SeekBar
    android:id="@+id/sbAgeRestriction"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:min="0"
    android:max="21"
    android:progressTint="?attr/colorPrimary"
    android:thumbTint="?attr/colorPrimary" />
```

Step 3 — `activities/ItemActivity.java`, four places:

```java
// 3a. the fields
private SeekBar sbAgeRestriction;
private TextView tvAgeRestrictionValue;

// 3b. initControls()
sbAgeRestriction = findViewById(R.id.sbAgeRestriction);
tvAgeRestrictionValue = findViewById(R.id.tvAgeRestrictionValue);

// 3c. initListeners() — before fillForm, so the label updates itself
sbAgeRestriction.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvAgeRestrictionValue.setText(progress + "+");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) { }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) { }
});

// 3d. fillForm() — a single call; the listener does the rest
sbAgeRestriction.setProgress(existing.getAgeRestriction());

// 3e. saveMovie() — getProgress() returns an int directly
movie.setAgeRestriction(sbAgeRestriction.getProgress());
```

Step 4 — `res/layout/movie_item.xml`, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieAgeRestriction"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Age"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 5 — `MovieAdapter.java`:

```java
private final TextView movieAgeRestriction;

movieAgeRestriction = itemView.findViewById(R.id.movieAgeRestriction);

movieAgeRestriction.setText(movie.getAgeRestriction() == 0
        ? "All ages"
        : "+" + movie.getAgeRestriction());
```

Step 6 — `MainActivity.addSampleMovies()`: the 11th argument, a plain `int`:

```java
        "https://example.com/posters/inception.jpg",
        13));
```

**Why:** a `SeekBar` needs no parsing — `getProgress()` returns exactly the `int` you need. It's the only widget in the file that gives you the right type directly, with no conversion.

**Remember:**
1. **The order in `onCreate` does the magic.** `initControls()` → `initListeners()` → `fillForm()`. Because the listener is attached **before** `fillForm`, the `setProgress(...)` in `fillForm` triggers `onProgressChanged` and the label updates itself. If you attached the listener after `fillForm`, you'd have to write `tvAgeRestrictionValue.setText(...)` in `fillForm` too — otherwise on edit the slider shows 13 and the label shows "0+".
2. A `SeekBar` has no "step". All 22 integer values are selectable. If you want only 0, 6, 12, 16, 18, 21, you use a `Spinner` with `android:entries="@array/age_restriction"` and `Integer.parseInt(spAge.getSelectedItem().toString())`.
3. `android:min` is available from API 26; `minSdk` 33, so it's fine. `sbDuration` already uses it.
4. `progress + "+"` is `int` + `String` concatenation → `String`. You don't need `String.valueOf`.
5. `SeekBar.OnSeekBarChangeListener` has three methods; two stay empty. That's not a mistake — they're required by the interface.

**Where it applies:** any bounded integer attribute — `ageRestriction`, `discount`, `quantity`.

</details>

---

## Exercise 17.7 — `country` (String) with validation: the required field

**Requirement:** Add the `country` (String) attribute to the movie. The field is required: if it's empty, saving is blocked, an error appears on the field and the form stays open.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private String country;` next to `poster`.
2. In the full constructor, add `String country` at the end and `this.country = country;`.
3. In `toString()`, add `", country='" + country + '\'' +`.
4. Add `getCountry()` and `setCountry(String)`.
5. Compile and fix the three calls in `addSampleMovies()`: the 11th argument, `"USA"`, `"SUA"`, `"UK"`.
6. In `activity_item.xml`, Card 1, after `etRelease`: label `TextView` + `TextInputLayout` with `etCountry`.
7. In `ItemActivity.java`: the field, `initControls()`, `fillForm()` with `etCountry.setText(existing.getCountry())`.
8. In `saveMovie()`, as the **first** statement: read the text, `trim()`, and if it's empty — `setError`, `requestFocus`, `return`.
9. In `movie_item.xml` and the adapter: the `movieCountry` `TextView`, with a `null` guard.
10. Verify: Run, leave the country empty and press Save. The form must stay open, with the red message on the field. Type "Romania" and press again: it saves and appears in the list.

**Hint 1 — if you get stuck at step 8:** the guard goes at the start of `saveMovie()`, before `Movie movie = new Movie();`. If you put it after building the object, you've done the work for nothing and it's easy to forget the `return`.

**Hint 2 — if you get stuck at step 8:** without the `return` after `setError`, the method continues, saves the movie with the empty country, calls `setResult(RESULT_OK)` and `finish()` — exactly what you wanted to prevent, just with a red message shown for a moment.

<details>
<summary>Solution — explained</summary>

**What was done:** the full chain from 17.1 for `country`, plus a guard at the start of `saveMovie`.

**Code:**

Step 1 — `model/Movie.java`:

```java
private String country;

public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String country) {
    // ... the other assignments ...
    this.country = country;
}

", country='" + country + '\'' +

public String getCountry() {
    return country;
}

public void setCountry(String country) {
    this.country = country;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 1 (Basics), after `etRelease`:

```xml
<TextView
    android:id="@+id/tvCountry"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Country"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etCountry"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Country"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Step 3 — `activities/ItemActivity.java`, with the validation in `saveMovie`:

```java
// 3a. the field
private EditText etCountry;

// 3b. initControls()
etCountry = findViewById(R.id.etCountry);

// 3c. fillForm()
etCountry.setText(existing.getCountry());

// 3d. saveMovie() — the FIRST statement in the method
private void saveMovie() {
    String country = etCountry.getText().toString().trim();
    if (country.isEmpty()) {
        etCountry.setError("Country is required");
        etCountry.requestFocus();
        return;                       // ← without it, saving continues
    }

    Movie movie = new Movie();
    // ... the rest of the method, unchanged ...
    movie.setCountry(country);        // use the already cleaned variable
    // ...
}
```

Step 4 — `res/layout/movie_item.xml`, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieCountry"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Country"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 5 — `MovieAdapter.java`:

```java
private final TextView movieCountry;

movieCountry = itemView.findViewById(R.id.movieCountry);

movieCountry.setText(movie.getCountry() != null ? movie.getCountry() : "");
```

Step 6 — `MainActivity.addSampleMovies()`: the 11th argument, `"USA"`, `"SUA"`, etc.

**Why:** the `return` after the error. Without it, the method continues, builds the `Movie` with the empty country, calls `setResult(RESULT_OK)` and `finish()` — exactly what you wanted to prevent, just with a red message shown for a moment.

**Remember:**
1. **You validate before building the object.** If you validate at the end, after `new Movie()`, you've done the work for nothing and you risk forgetting the `return`.
2. **`trim()` before `isEmpty()`.** A field with a single space isn't "empty" for `String.isEmpty()`, but it is empty for a human. `"   ".trim().isEmpty()` → `true`.
3. **The error doesn't clear itself.** `setError(...)` stays on the field until you clear it with `setError(null)`. The file already does this for `etRelease` in the date callback — the same pattern.
4. **`etCountry.setError` vs `TextInputLayout.setError`.** The first is what the file already uses and it shows a popup with an icon. The second shows the message below the box, without a popup — but you need a reference to the `TextInputLayout`, not the `EditText`. Both work with `app:hintEnabled="false"`.
5. **Don't validate in `fillForm`.** On edit, an old movie without a country must be able to open; the error only appears when you press Save.
6. `requestFocus()` moves the cursor to the wrong field. Without it, the user sees the error but has to hunt for the field.

**Where it applies:** any required field — `country`, `title`, `email`. For several fields, you repeat the guard for each, in the form's order, and do a single `return` after all of them.

</details>

---

## Exercise 17.8 — `awarded` (boolean) with a conditional chip

**Requirement:** Add the `awarded` (boolean) attribute to the movie — the movie has won an award. In the form, a checkbox. In the card, an "Awarded" chip that appears **only** if the attribute is `true`.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java`. Add `private boolean awarded;` next to `watched`.
2. In the full constructor, add `boolean awarded` at the end and `this.awarded = awarded;`.
3. In `toString()`, add `", awarded=" + awarded +`.
4. Add `isAwarded()` and `setAwarded(boolean)`.
5. Compile and fix the three calls in `addSampleMovies()`: the 11th argument, `true` or `false`.
6. In `activity_item.xml`, Card 3, after the `rgApproval` `RadioGroup`: a `MaterialCheckBox` with id `cbAwarded` and the text "Awarded".
7. In `ItemActivity.java`: the `private CheckBox cbAwarded;` field, `initControls()`, `fillForm()` with `setChecked(existing.isAwarded())`, `saveMovie()` with `movie.setAwarded(cbAwarded.isChecked())`.
8. In `movie_item.xml`, in `movieStatusGroup`, after `chipWatchlist`: a `Chip` with id `chipAwarded`.
9. In the adapter: the field, `findViewById`, then in `bind()` — `chipAwarded.setVisibility(movie.isAwarded() ? View.VISIBLE : View.GONE)`, with both branches.
10. Verify: Run, add a movie with the box checked — the list shows `awarded=true`. After you do the `RecyclerView` (chapter 11), scroll the list to a movie without the box: the "Awarded" chip must not appear.

**Hint 1 — if you get stuck at step 6:** `MaterialCheckBox` extends `CheckBox`, so you can hold it in a `CheckBox` field — exactly how the file does it with `cbOnWatchList`: declared as `CheckBox` in Java, built as `MaterialCheckBox` in XML.

**Hint 2 — if you get stuck at step 9:** write `setVisibility(movie.isAwarded() ? View.VISIBLE : View.GONE)`, not an `if` without an `else`. `ViewHolder`s are recycled: a row that displayed an awarded movie is reused for one that isn't and keeps the chip.

<details>
<summary>Solution — explained</summary>

**What was done:** I added the attribute, a checkbox in the form and a chip in `movieStatusGroup`, with visibility set on every `bind`.

**Code:**

Step 1 — `model/Movie.java`:

```java
private boolean awarded;

public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, boolean awarded) {
    // ... the other assignments ...
    this.awarded = awarded;
}

", awarded=" + awarded +

public boolean isAwarded() {
    return awarded;
}

public void setAwarded(boolean awarded) {
    this.awarded = awarded;
}
```

Step 2 — `res/layout/activity_item.xml`, in Card 3 (Your verdict), after `RadioGroup`:

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/cbAwarded"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Awarded" />
```

Step 3 — `activities/ItemActivity.java`:

```java
// 3a. the field — plain CheckBox, already imported
private CheckBox cbAwarded;

// 3b. initControls()
cbAwarded = findViewById(R.id.cbAwarded);

// 3c. fillForm()
cbAwarded.setChecked(existing.isAwarded());

// 3d. saveMovie()
movie.setAwarded(cbAwarded.isChecked());
```

Step 4 — `res/layout/movie_item.xml`, in `movieStatusGroup`, after `chipWatchlist`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipAwarded"
    style="@style/Widget.Material3.Chip.Suggestion"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Awarded"
    android:clickable="false"
    app:chipMinHeight="28dp"
    app:chipIcon="@android:drawable/star_on"
    app:ensureMinTouchTargetSize="false" />
```

Step 5 — `MovieAdapter.java`:

```java
private final Chip chipAwarded;

chipAwarded = itemView.findViewById(R.id.chipAwarded);

// in bind() — MANDATORY on every row, not only when it's true
chipAwarded.setVisibility(movie.isAwarded() ? View.VISIBLE : View.GONE);
```

Step 6 — `MainActivity.addSampleMovies()`: the 11th argument, `true` or `false`, on all three.

**Why:** `setVisibility` with both branches. An `if (movie.isAwarded()) chipAwarded.setVisibility(View.VISIBLE);` without an `else` is the classic `RecyclerView` bug: the recycled row keeps the previous movie's state, and a movie without an award shows up with the "Awarded" chip from the neighbour before it.

**Remember:**
1. **`bind()` must set the visibility every time.** `ViewHolder`s are recycled — a row that displayed an awarded movie is reused for one that isn't. If you don't reset it, the chip stays. The rule: any property that depends on data is set in `bind`, not in the constructor.
2. **`View.GONE` in a `ChipGroup`.** `GONE` removes the chip from the layout, so the other chips close up. `INVISIBLE` keeps the space and leaves a hole between the chips.
3. **`isAwarded()`, not `getAwarded()`.** The convention for `boolean` is `isX()`.
4. **At `d719ffc` the chip isn't visible at all.** `movie_item.xml` is not used by the `ListView` (see 17.1, point 3). The visible effect at the commit is only `awarded=true` in `toString()`. Steps 4–5 become real after the move to `RecyclerView` (chapter 11).
5. The checkbox is a `MaterialCheckBox`, but the Java field is a `CheckBox` — `MaterialCheckBox` extends `CheckBox`, so `findViewById` into a `CheckBox` works. The file does the same with `cbOnWatchList`.

**Where it applies:** any conditional UI element — chips, icons, badges, entire sections.

</details>

---

## Exercise 17.9 — `cast` (ArrayList\<Actor\>): the composite attribute

**Requirement:** Add an `Actor` class with two fields, `name` and `role`, and the `cast` (ArrayList\<Actor\>) attribute in `Movie`. In the form, actors are written as `Name:Role`, separated by commas. In the list, they appear as `Name (Role)`.

**Files touched:** `model/Actor.java` (new file), `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Create `model/Actor.java` **before** anything else: package `ro.ase.ie.g1097.model`, `implements Serializable`, the `name` and `role` fields, empty constructor, two-parameter constructor, getters/setters, `toString()` returning `name + " (" + role + ")"`.
2. Open `model/Movie.java`. Add `import java.util.ArrayList;` and the field `private ArrayList<Actor> cast = new ArrayList<>();`.
3. In the full constructor, add `ArrayList<Actor> cast` at the end and `this.cast = cast;`.
4. In `toString()`, add `", cast=" + cast +`.
5. Add `getCast()` and `setCast(ArrayList<Actor>)`.
6. Compile and fix the three calls in `addSampleMovies()`: the 11th argument is a list of `Actor`, `new ArrayList<>(Arrays.asList(new Actor("...", "..."), ...))`.
7. In `activity_item.xml`, Card 1, after `etRelease`: label `TextView` + `TextInputLayout` with `etCast` and `app:helperText="Name:Role, Name:Role"`.
8. In `ItemActivity.java`: the field, `initControls()`, `fillForm()` with `castToText(...)`, `saveMovie()` with `parseCast(...)`. Write the two private methods at the end of the class.
9. In `movie_item.xml` and the adapter: the `movieCast` `TextView`, bound with `TextUtils.join(", ", movie.getCast())` — with `import android.text.TextUtils;`.
10. Verify: Run, type `Tom Hanks:Forrest, Robin Wright:Jenny` and save. No `NotSerializableException` must appear. The list shows `cast=[Tom Hanks (Forrest), Robin Wright (Jenny)]`. Reopen the movie: the field shows `Tom Hanks:Forrest, Robin Wright:Jenny` again, not the format with parentheses.

**Hint 1 — if you get stuck at step 1:** `implements Serializable` on `Actor` is not optional. `Movie` travels through `Intent.putExtra(String, Serializable)` and serialisation walks the whole object graph — a non-serialisable `Actor` gives a `NotSerializableException` on Save, not at compile time.

**Hint 2 — if you get stuck at step 8:** use `entry.split(":", 2)`, with the limit 2. Without a limit, a role containing `:` produces three elements, `parts.length == 2` becomes false and the entry is thrown away without any message.

<details>
<summary>Solution — explained</summary>

**What was done:** I created the `Actor` class, added the list in `Movie`, wrote two conversion methods in `ItemActivity` (text → list and list → text) and displayed the list in the card.

**Code:**

Step 1 — `model/Actor.java`, new file:

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;

public class Actor implements Serializable {   // ← mandatory

    private String name;
    private String role;

    public Actor() {
    }

    public Actor(String name, String role) {
        this.name = name;
        this.role = role;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    // the format for the CARD, not for the form
    @Override
    public String toString() {
        return name + " (" + role + ")";
    }
}
```

Step 2 — `model/Movie.java`:

```java
import java.util.ArrayList;   // new import

// 2a. the field
private ArrayList<Actor> cast = new ArrayList<>();

// 2b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, ArrayList<Actor> cast) {
    // ... the other assignments ...
    this.cast = cast;
}

// 2c. toString() — uses Actor.toString()
", cast=" + cast +

// 2d. getter/setter
public ArrayList<Actor> getCast() {
    return cast;
}

public void setCast(ArrayList<Actor> cast) {
    this.cast = cast;
}
```

Step 3 — `res/layout/activity_item.xml`, in Card 1 (Basics), after `etRelease`:

```xml
<TextView
    android:id="@+id/tvCast"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Cast"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text"
    app:helperText="Name:Role, Name:Role">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etCast"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Cast"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Step 4 — `activities/ItemActivity.java`, with two new methods:

```java
import java.util.ArrayList;   // new import

// 4a. the field
private EditText etCast;

// 4b. initControls()
etCast = findViewById(R.id.etCast);

// 4c. fillForm() — list → text
etCast.setText(existing.getCast() != null ? castToText(existing.getCast()) : "");

// 4d. saveMovie() — text → list
movie.setCast(parseCast(etCast.getText().toString()));

// 4e. the two methods, at the end of the class
private ArrayList<Actor> parseCast(String text) {
    ArrayList<Actor> cast = new ArrayList<>();
    for (String entry : text.split(",")) {
        String[] parts = entry.split(":", 2);      // limit 2 — see below
        if (parts.length == 2) {
            String name = parts[0].trim();
            String role = parts[1].trim();
            if (!name.isEmpty()) {
                cast.add(new Actor(name, role));
            }
        }
    }
    return cast;
}

private String castToText(ArrayList<Actor> cast) {
    StringBuilder sb = new StringBuilder();
    for (Actor actor : cast) {
        if (sb.length() > 0) {
            sb.append(", ");
        }
        sb.append(actor.getName()).append(":").append(actor.getRole());
    }
    return sb.toString();
}
```

Step 5 — `res/layout/movie_item.xml`, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieCast"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Cast"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 6 — `MovieAdapter.java`:

```java
import android.text.TextUtils;   // new import

private final TextView movieCast;

movieCast = itemView.findViewById(R.id.movieCast);

// TextUtils.join calls toString() on each element
movieCast.setText(movie.getCast() != null
        ? TextUtils.join(", ", movie.getCast())
        : "");
```

Step 7 — `MainActivity.addSampleMovies()`: the 11th argument is a list of `Actor`:

```java
        "https://example.com/posters/inception.jpg",
        new ArrayList<>(Arrays.asList(
                new Actor("Leonardo DiCaprio", "Cobb"),
                new Actor("Joseph Gordon-Levitt", "Arthur")))));
```

**Why:** `Actor` must be `Serializable` because `Movie` travels through `Intent.putExtra(String, Serializable)`, and Java serialisation walks the **whole object graph**. A non-serialisable `Actor` gives no error at compile time — it gives a `NotSerializableException` at runtime, exactly when you press Save, that is, in front of the teacher.

**Remember:**
1. **`implements Serializable` on `Actor` is mandatory.** `ArrayList` is serialisable, but that doesn't help: every element must be too. The symptom is clear — the form works, and on Save the app closes with `NotSerializableException: ro.ase.ie.g1097.model.Actor`.
2. **`split(":", 2)` and not `split(":")`.** With the limit 2, everything after the first `:` stays in the second element: `"Robert Downey Jr.:Tony Stark:Iron Man"` → role `"Tony Stark:Iron Man"`. Without a limit → three elements, `parts.length == 2` is false, and the entry is silently thrown away.
3. **Two formats, two methods.** `Actor.toString()` gives `"Tom Hanks (Forrest)"` — a **display** format. The text field wants `"Tom Hanks:Forrest"` — an **input** format. If you try to round-trip through `toString()`, you're parsing parentheses and you break on the first name with a parenthesis. That's why `castToText` builds `Name:Role` explicitly.
4. **`String.join` doesn't work on `List<Actor>`.** The signature is `String.join(CharSequence, Iterable<? extends CharSequence>)`, and `Actor` is not a `CharSequence` — compile error. `TextUtils.join(CharSequence, Iterable<?>)` accepts anything and calls `toString()` on each element. Hence the import.
5. **`parts.length == 2` drops the entries without a `:`.** That's a decision: `"Tom Hanks"` alone has no role, so it doesn't become an `Actor`. The alternative is to accept an empty role — but then the card shows `Tom Hanks ()`.
6. **The empty constructor in `Actor`** isn't used by the code, but you keep it: any model class that will end up in `Gson`, `Room` or `Parcelable` needs it. It costs two lines.
7. **The order of the steps matters more than in 17.1.** If you do `Movie` before `Actor`, nothing compiles. The new file first, then the model that uses it.

**Where it applies:** any composite attribute — `cast`, `awards` (a list of objects), `screenings` (a list of times + hall).

</details>

---

## Exercise 17.10 — `writer` + `popular`: both requirements, in 30 minutes

**Requirement:** Add two attributes to the movie: `writer` (String) and `popular` (boolean). Both must appear in the form and in the list. Time: 30 minutes.

**Files touched:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (optional).

**How you approach it — your steps:**
1. Open `model/Movie.java` and do **both** attributes in a single pass: the two fields, both parameters in the constructor, both lines in `toString()`, all four getters/setters.
2. Compile immediately. Fix the three calls in `addSampleMovies()` — two new arguments each, in the order `writer`, `popular`.
3. Open `activity_item.xml` once: `etWriter` in Card 1 after `etRelease`, `swPopular` in Card 3 after `rgApproval`.
4. Open `ItemActivity.java` once: both fields, both `findViewById` in `initControls()`, both lines in `fillForm()`, both in `saveMovie()`.
5. Open `movie_item.xml` once: `movieWriter` and `moviePopular`, next to each other, after `movieFacts`.
6. In the adapter: two fields, two `findViewById`, two `setText`.
7. Verify in three touches: add a movie with both filled in → it appears in the list; edit it and change only `writer` → `popular` stays as it was; clear `writer` → the field becomes empty, it doesn't keep the old value.

**Hint 1 — if you get stuck at step 1:** don't do the five-step chain twice. You open each file once and put both attributes in the same edit — five passes, not ten. At the exam the difference is between finishing in 20 minutes and not finishing.

**Hint 2 — if you get stuck at step 2:** the order of the constructor arguments must be respected in all three calls: `..., poster, writer, popular`. Here the compiler catches you, because `String` and `boolean` can't be confused. If both new attributes had been `String`, a swap would have compiled and saved the screenwriter in the country field, with no error at all.

<details>
<summary>Solution — explained</summary>

**What was done:** I treated the two attributes as a single wave of changes — five files, five passes, both attributes in each.

**Code:**

Step 1 — `model/Movie.java`, both fields in a single edit:

```java
// 1a. the fields
private String writer;
private boolean popular;

// 1b. the constructor — two new arguments, in the order writer, popular
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String writer, boolean popular) {
    // ... the other assignments ...
    this.writer = writer;
    this.popular = popular;
}

// 1c. toString() — two lines
", writer='" + writer + '\'' +
", popular=" + popular +

// 1d. getters/setters — four methods
public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}

public boolean isPopular() {
    return popular;
}

public void setPopular(boolean popular) {
    this.popular = popular;
}
```

Step 2 — `res/layout/activity_item.xml`, both fields in the same visit:

```xml
<!-- Card 1 (Basics), after etRelease: etWriter -->
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etWriter"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Writer"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>

<!-- Card 3 (Your verdict), after rgApproval: swPopular -->
<com.google.android.material.materialswitch.MaterialSwitch
    android:id="@+id/swPopular"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Popular" />
```

Step 3 — `activities/ItemActivity.java`, six places, a single pass:

```java
// 3a. the fields
private EditText etWriter;
private MaterialSwitch swPopular;

// 3b. initControls()
etWriter = findViewById(R.id.etWriter);
swPopular = findViewById(R.id.swPopular);

// 3c. fillForm()
etWriter.setText(existing.getWriter());
swPopular.setChecked(existing.isPopular());

// 3d. saveMovie()
movie.setWriter(etWriter.getText().toString());
movie.setPopular(swPopular.isChecked());
```

Step 4 — `res/layout/movie_item.xml`, two `TextView`s next to each other, after `movieFacts`:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Writer"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />

<TextView
    android:id="@+id/moviePopular"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Popular"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Step 5 — `MovieAdapter.java`, two fields, two `findViewById`, two `setText`:

```java
private final TextView movieWriter;
private final TextView moviePopular;

movieWriter = itemView.findViewById(R.id.movieWriter);
moviePopular = itemView.findViewById(R.id.moviePopular);

movieWriter.setText(movie.getWriter() != null ? movie.getWriter() : "");
moviePopular.setText(movie.isPopular() ? "Popular" : "");
```

Step 6 — `MainActivity.addSampleMovies()`: **two** new arguments on **each** of the three calls:

```java
        "https://example.com/posters/inception.jpg",
        "Christopher Nolan",   // writer
        true));                // popular
```

**Why:** two attributes mean two values, not two chains. The model is edited once for both fields, the form once for both widgets, the activity once for both read/write pairs. Ten passes become five, and at the exam the difference is between finishing in 20 minutes and not finishing.

**Remember:**
1. **The order of the constructor parameters must be respected in all three calls.** Here the compiler helps you: `String` and `boolean` can't be confused. But if the two new attributes had both been `String`, a swap would have compiled and saved the screenwriter in the country field — with no error. The compiler only catches you when the types differ.
2. **Compile after step 1, before the XML.** As soon as you change the constructor signature, `addSampleMovies` has three errors. You see them in `Build`, fix them, then move on to the UI. If you leave everything for the end, you no longer know which error comes from what.
3. **`fillForm` and `saveMovie` are done together, per attribute.** An attribute with `fillForm` but without `saveMovie` never gets saved; one with `saveMovie` but without `fillForm` resets on every edit. Both of them compile.
4. **The time budget, realistically:** 2 min model + 8 min form + 8 min activity + 4 min card + 4 min adapter + 4 min build and check on the emulator = 30.
5. **The final check, in three touches:** you add a new movie with both filled in → it appears in the list; you edit it and change only `writer` → `popular` stays as it was; you edit it and clear `writer` → the field becomes empty, the old value doesn't stay.
6. If the teacher asks for "in the list" and you're on `d719ffc`, the step that matters is `toString()`: without the two lines from 1c, the values are saved but not visible (see 17.1, point 3).

**Where it applies:** exactly the exam format. Any combination of two attributes — `writer` + `popular`, `country` + `year`, `awarded` + `imdbScore` — is solved with the same five passes.

</details>
