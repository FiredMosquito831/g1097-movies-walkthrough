# Chapter 33 — Recipes 1: the model and the UI

**Objective:** for every requirement that touches the model (`Movie`) or the UI (the form, the list, a new screen), you get the exact steps, in order, with the minimum code that compiles, with the explanation of the mechanism and with the mistake that costs marks.

**Estimated time:** 150–180 min for all 16 recipes; 10–15 min for a single one, which is what you have left on the test for one requirement.

**Source:** the G1097 app (Movies), commit `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`, `strings.xml`.

**The golden rule:** on the test you have **2 requirements in 30 minutes**. A recipe from here has to fit in 10–15 minutes, with time left for the check. If it takes you longer, you skipped a step or you rewrote a whole file instead of adding one line.

---

## 33.0 What you have in hand

### The app's files

| File | Role | What you change most often |
|---|---|---|
| `Movie.java` | the model: 10 private fields, a 10-parameter constructor, an empty constructor, getters/setters, `toString()` | a new field, getter/setter, constructor, `toString()` |
| `activity_item.xml` | the form in `ItemActivity`: `ScrollView` → `LinearLayout` → 4 cards | a new widget, a new input type |
| `ItemActivity.java` | reads the form and builds the `Movie`; `findViewById`, `fillForm`, `saveMovie` | field, `findViewById`, `fillForm`, `saveMovie` |
| `activity_main.xml` | the main screen: `FrameLayout` with a `ListView` and a `FloatingActionButton` | a control above the list |
| `MainActivity.java` | holds `List<Movie> movies`, `ArrayAdapter<Movie> movieAdapter`, `ActivityResultLauncher<Intent> launcher` | demo data, adapter, listeners |
| `movie_item.xml` | the `RecyclerView` row — **it exists, but no code uses it** | only when you migrate to `RecyclerView` |
| `AndroidManifest.xml` | declares the two activities | a new screen |
| `strings.xml` | `app_name`, `items` (20 demo strings), `movie_genre` (10 genres) | a new array for a `Spinner` |

> **Watch out for `movie_item.xml`:** the file is prepared for `RecyclerView`, but in G1097 **it is not inflated anywhere**. `MainActivity` uses `ArrayAdapter` with `android.R.layout.simple_list_item_1`. Whatever widget you add in `movie_item.xml` does not show until you do the migration from chapter 23. I say this explicitly in recipe 33.12.

`ItemActivity` uses `findViewById`, **not** ViewBinding: the 13 views are fields declared at class level (`etTitle`, `etRelease`, `spGenre`, `etBudget`, `sbDuration`, `rbRating`, `rgApproval`, `cbonWatchList`, `swWatched`, `etPoster`, `btMovieAction`, `tvDurationValue`, `tvWatchedValue`) and they are initialised in `initControls()`, after `setContentView`. `Movie implements Serializable`, which is why it can be sent through `Intent.putExtra` and read with `IntentCompat.getSerializableExtra`.

### The `Movie` model — the 10 fields

| Field | Type | Widget that produces it | Getter |
|---|---|---|---|
| `title` | `String` | `etTitle` (`TextInputEditText`) | `getTitle()` |
| `release` | `Date` | `etRelease` + `DatePickerDialog` | `getRelease()` |
| `genre` | `String` | `spGenre` (`Spinner`) | `getGenre()` |
| `budget` | `double` | `etBudget` (`TextInputEditText`, `numberDecimal`) | `getBudget()` |
| `duration` | `int` | `sbDuration` (`SeekBar`) | `getDuration()` |
| `rating` | `float` | `rbRating` (`RatingBar`) | `getRating()` |
| `watched` | `boolean` | `swWatched` (`MaterialSwitch`) | `isWatched()` |
| `approval` | `String` | `rgApproval` (`RadioGroup`) | `getApproval()` |
| `onWatchlist` | `boolean` | `cbonWatchList` (`MaterialCheckBox`) | `isOnWatchlist()` |
| `poster` | `String` | `etPoster` (`TextInputEditText`, `textUri`) | `getPoster()` |

The parameterised constructor has **exactly 10 parameters, in the order of the table**. There is also `public Movie() {}` — the empty constructor, used by `saveMovie()`.

### The data flow

```
MainActivity                          ItemActivity
  movies: List<Movie>                   form (13 views)
  movieAdapter: ArrayAdapter<Movie>     releaseCal: Calendar
  launcher: ActivityResultLauncher      position: int (-1 = insert)
        |                                     ^
        |  Intent + MOVIE_EXTRA (Movie)       |
        +-------------------------------------+
        |  Intent + MOVIE_EXTRA + POSITION_EXTRA
        v                                     |
  onActivityResult: add() or set()            |
  movieAdapter.notifyDataSetChanged()         |
```

### The four-layer rule

Any requirement that touches a new attribute goes through **the same four layers, in this order**:

1. **The model** — `Movie.java`: field, getter, setter, constructor, `toString()`.
2. **The form** — `activity_item.xml`: a widget with an `android:id`.
3. **The binding** — `ItemActivity.java`: field, `findViewById`, `fillForm`, `saveMovie`.
4. **The display** — `toString()` (for `ListView`) or `movie_item.xml` + adapter (for `RecyclerView`).

> **Why the order matters:** if you start with the XML, the code does not compile until the field exists in the model. If you start with `ItemActivity`, `findViewById` returns `null` until the ID exists in the XML. The model is the only layer that depends on no other one — so it goes first.

### The naming convention

| Prefix | Widget | Example in G1097 |
|---|---|---|
| `et` | `EditText` / `TextInputEditText` | `etTitle`, `etBudget`, `etPoster` |
| `tv` | `TextView` | `tvDurationValue`, `tvWatchedValue` |
| `sp` | `Spinner` | `spGenre` |
| `sb` | `SeekBar` | `sbDuration` |
| `rb` | `RatingBar` / `RadioButton` | `rbRating`, `rbPG13` |
| `rg` | `RadioGroup` | `rgApproval` |
| `cb` | `CheckBox` | `cbonWatchList` |
| `sw` | `Switch` | `swWatched` |
| `btn` | `Button` | `btnMovieAction` |
| `fab` | `FloatingActionButton` | `floatingActionButton` |

> The repo also has inconsistencies: the Java field is called `cbonWatchList`, but the ID is `cbOnWatchList`; the field is `btMovieAction`, but the ID is `btnMovieAction`. **The field name and the ID do not have to match** — `findViewById(R.id.cbOnWatchList)` ties the two names together. Follow exactly what is in the file.

### How to read a recipe

Each recipe has seven sections: the requirement, the files touched, the steps, why it works, the mistake that costs marks, the check, the exercises. The steps are in the order in which you do them on the test.

**The new IDs.** The recipes that add a widget create an ID that does not exist yet in the app — `etWriter`, `etYear`, `movieWriter`. You write it exactly as it appears in the code: `@+id/etWriter` in XML, `R.id.etWriter` in Java. The name must be unique in the project and must follow the prefix in the table above. The rest of the code is identical to what you have to write: no lines are missing, there are no abbreviations.

---

## Recipe 33.1 — Add a String attribute

### **The requirement, as it sounds in the test**

"Add the director's name to the movie (`writer`) and show it in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | field `writer`, getter, setter, the 11th parameter in the constructor, a line in `toString()` | yes |
| 2 | `activity_item.xml` | `TextInputLayout` + `TextInputEditText` with a new ID, in the "Basics" card | yes, if you want to enter the value from the form |
| 3 | `ItemActivity.java` | field, `findViewById`, `fillForm`, `saveMovie` | yes, together with step 2 |
| 4 | `MainActivity.java` | the 11th argument in the three `new Movie(...)` calls in `addSampleMovies()` | yes, after you change the constructor |
| 5 | `movie_item.xml` | a `TextView` for the row | only if you move to `RecyclerView` |

### **The steps, in order**

**Step 1 — `Movie.java`, at the end of the field list.** You add the field next to `poster`:

```java
private String title;
private Date release;
private String genre;
private double budget;
private int duration;
private float rating;
private boolean watched;
private String approval;
private boolean onWatchlist;
private String poster = null;
private String writer;
```

**Step 2 — `Movie.java`, after `setPoster()`.** The getter and the setter, in the same shape as the ones for the other fields:

```java
public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}
```

**Step 3 — `Movie.java`, the parameterised constructor.** You add the 11th parameter **at the end**, so that you do not move the order of the existing ones, and you assign it:

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

**Step 4 — `Movie.java`, `toString()`.** You add the line before the closing brace of the string:

```java
@Override
public String toString() {
    return "Movie{" +
            "title='" + title + '\'' +
            ", release=" + release +
            ", genre='" + genre + '\'' +
            ", budget=" + budget +
            ", duration=" + duration +
            ", rating=" + rating +
            ", watched=" + watched +
            ", approval='" + approval + '\'' +
            ", onWatchlist=" + onWatchlist +
            ", poster='" + poster + '\'' +
            ", writer='" + writer + '\'' +
            '}';
}
```

**Step 5 — `activity_item.xml`, in the "Basics" card, after the `etRelease` block.** You add a new text field. The ID chosen here is `etWriter`:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
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

**Step 6 — `ItemActivity.java`, at the class fields.** You add the reference, next to `etPoster`:

```java
private EditText etPoster;
private EditText etWriter;
```

**Step 7 — `ItemActivity.java`, in `initControls()`.** The binding to the XML:

```java
etPoster = findViewById(R.id.etPoster);
etWriter = findViewById(R.id.etWriter);
```

**Step 8 — `ItemActivity.java`, in `fillForm()`.** You fill the field when you open an existing movie:

```java
etPoster.setText(existing.getPoster());
etWriter.setText(existing.getWriter());
```

**Step 9 — `ItemActivity.java`, in `saveMovie()`.** You read the value into the object that goes to the list:

```java
movie.setPoster(etPoster.getText().toString());
movie.setWriter(etWriter.getText().toString());
```

**Step 10 — `MainActivity.java`, in `addSampleMovies()`.** The constructor now has 11 parameters, so all three calls get one more argument. The first one:

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
        "Christopher Nolan"));
```

The same for `"Toy Story"` and `"The Matrix"` — if you forget one, that is exactly where you will get the compilation error.

**Step 11 — only if you display the attribute in a `RecyclerView` row.** In `movie_item.xml` you add a `TextView` in the info column, and in the adapter you bind it in the `ViewHolder` and fill it in `bind()`. In G1097 this step **has no effect** because `movie_item.xml` is not used — see recipe 33.12.

### **Why it works this way**

`ArrayAdapter<Movie>` does not know what a `Movie` is: for each row it calls `toString()`. That is why the attribute appears in the list only if you add it to `toString()`. The parameterised constructor is the only place where a `Movie` receives values at creation; if you add the field and forget the parameter, the field stays `null` for all the demo movies. `findViewById` searches the view tree built by `setContentView`, which is why it is called after it, in `initControls()`, not in the field declaration.

> **Watch out for copy-paste between groups:** in G1097, `toString()` also includes `poster`; in G1099, `toString()` does not include it. If you work on another group, check the file before you add the line — otherwise you add an attribute into a `toString()` that looks different from what you thought.

### **The mistake that costs marks**

1. **You add the field and the getter, but not the parameter in the constructor.** Symptom: the code compiles, the app runs, but all the movies have `writer = null` and the row ends with `writer='null'`. Cause: the 10-parameter constructor has nowhere to receive the value, and `new Movie(...)` in `addSampleMovies()` does not send it.
2. **You add the parameter, but you do not update all three `new Movie(...)` calls.** Symptom: `error: constructor Movie in class Movie cannot be applied to given types; required: 11, found: 10`. Cause: you changed the signature, but not the callers. The compiler tells you exactly which line — read it before you look at the code.
3. **You forget `toString()`.** Symptom: you fill in the field, press Save, the new row appears, but it looks exactly as before. Cause: `ArrayAdapter` displays `toString()`, not the object's fields. The attribute is saved in the model, it just never reaches the screen.

### **The check**

Run the app. The list has three rows, and each one ends with `writer='...'`. Press the FAB, fill in the form, type a name in "Writer" and press "Save Movie": the fourth row contains the name. Tap the row: the "Writer" field is already filled in. Change the name and press "Update Movie": the row changes on the spot, without a fifth one appearing.

### **Practise**

[17.1 — `writer` (String): the reference attribute](cap-17.html#ex-17-1) · [17.10 — `writer` + `popular`: the two requirements, in 30 minutes](cap-17.html#ex-17-10) · [24.7 — the checklist after every "add an attribute"](cap-24.html#ex-24-7)

---

## Recipe 33.2 — Add a whole-number attribute (int)

### **The requirement, as it sounds in the test**

"Add the year in which the movie was made to it (`year`, `int`) and show it in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | field `int year`, getter, setter, the 11th parameter, a line in `toString()` | yes |
| 2 | `activity_item.xml` | `TextInputEditText` with `inputType="number"` and a new ID | yes, if you enter it from the form |
| 3 | `ItemActivity.java` | field, `findViewById`, `fillForm`, `saveMovie` with `Integer.parseInt` | yes, together with step 2 |
| 4 | `MainActivity.java` | the 11th argument in the three `new Movie(...)` calls | yes, after you change the constructor |

### **The steps, in order**

**Step 1 — `Movie.java`, at the fields.** An `int` is a primitive value: it cannot be `null`, and its default value is `0`.

```java
private String poster = null;
private int year;
```

**Step 2 — `Movie.java`, getter and setter.** For `int` you use `get`, not `is`:

```java
public int getYear() {
    return year;
}

public void setYear(int year) {
    this.year = year;
}
```

**Step 3 — `Movie.java`, the constructor.** The 11th parameter, at the end:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, int year) {
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
    this.year = year;
}
```

**Step 4 — `Movie.java`, `toString()`.** You add the line:

```java
", year=" + year +
```

**Step 5 — `activity_item.xml`, in the "Production" card, after the budget block.** The numeric field:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etYear"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Year"
        android:inputType="number" />
</com.google.android.material.textfield.TextInputLayout>
```

**Step 6 — `ItemActivity.java`, at the fields.**

```java
private EditText etYear;
```

**Step 7 — `ItemActivity.java`, in `initControls()`.**

```java
etYear = findViewById(R.id.etYear);
```

**Step 8 — `ItemActivity.java`, in `fillForm()`.** Here is the type trap: `setText` has two useful variants — `setText(CharSequence)` and `setText(int)`. If you give it an `int`, Java picks `setText(int)`, which treats it as a **resource ID**, not as text:

```java
etYear.setText(String.valueOf(existing.getYear()));
```

**Step 9 — `ItemActivity.java`, in `saveMovie()`.** `getText()` returns an `Editable`, not a number; you do the conversion yourself, with protection for the empty field:

```java
String rawYear = etYear.getText().toString().trim();
movie.setYear(rawYear.isEmpty() ? 0 : Integer.parseInt(rawYear));
```

**Step 10 — `MainActivity.java`, in `addSampleMovies()`.** The 11th argument, an `int` without quotes:

```java
"https://example.com/posters/inception.jpg",
2010));
```

### **Why it works this way**

`int` is primitive: it has no `null`, and if you do not initialise it, its value is `0`. `Integer.parseInt` turns a string into an `int` and throws `NumberFormatException` if the string is not a whole number — which is why the empty field has to be caught first. `String.valueOf(int)` does the reverse conversion and is mandatory at `setText`, because otherwise the `setText(int)` overload is called, which looks for a resource with that number.

### **The mistake that costs marks**

1. **`Integer.parseInt` on an empty field.** Symptom: you press Save without filling in the year and the app closes with `NumberFormatException: For input string: ""`. Cause: you skipped the `isEmpty()` check. The same error also appears for `"2010 "` with a space — hence the `.trim()`.
2. **`etYear.setText(existing.getYear())`.** Symptom: `Resources.NotFoundException` when you open an existing movie for editing. Cause: `setText(int)` treats the number as a resource ID. The correct form is `String.valueOf(...)`.
3. **You forget the 11th argument in a single `new Movie(...)`.** Symptom: a compilation error in `addSampleMovies()`, with the number of arguments required and found. Cause: the constructor changed, the calls did not.

### **The check**

Run the app: every row contains `year=...`. Add a movie with the year `2024` and check the fourth row. Tap the row: the "Year" field shows `2024`, not a resource number and not `0`. Leave the field empty on a new movie and press Save: the app stays open, and the row shows `year=0`.

### **Practise**

[17.2 — `year` (Integer): the numeric attribute that can be null](cap-17.html#ex-17-2) · [17.6 — `ageRestriction` (int): the slider with a displayed value](cap-17.html#ex-17-6) · [19.10 — exam combo: a value in a label + a validation error](cap-19.html#ex-19-10)

---

## Recipe 33.3 — Add an Integer attribute that can be null

### **The requirement, as it sounds in the test**

"Add the number of Oscar awards to the movie (`oscars`), which may be missing, and show it in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | field `Integer oscars`, getter, setter, the 11th parameter, a line in `toString()` | yes |
| 2 | `activity_item.xml` | `TextInputEditText` with `inputType="number"` and a new ID | yes, if you enter it from the form |
| 3 | `ItemActivity.java` | field, `findViewById`, `fillForm` with a `null` check, `saveMovie` with a value or `null` | yes, together with step 2 |
| 4 | `MainActivity.java` | the 11th argument: a number or `null` | yes, after you change the constructor |

### **The steps, in order**

**Step 1 — `Movie.java`, at the fields.** `Integer` is the wrapper class of `int`: it is a reference, so it can be `null`.

```java
private String poster = null;
private Integer oscars;
```

**Step 2 — `Movie.java`, getter and setter.**

```java
public Integer getOscars() {
    return oscars;
}

public void setOscars(Integer oscars) {
    this.oscars = oscars;
}
```

**Step 3 — `Movie.java`, the constructor.** The 11th parameter is `Integer`, not `int`:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, Integer oscars) {
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
    this.oscars = oscars;
}
```

**Step 4 — `Movie.java`, `toString()`.** `null` is displayed as the text `null`, it does not crash:

```java
", oscars=" + oscars +
```

**Step 5 — `activity_item.xml`, in the "Production" card.**

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etOscars"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Oscars (optional)"
        android:inputType="number" />
</com.google.android.material.textfield.TextInputLayout>
```

**Step 6 — `ItemActivity.java`, at the fields.**

```java
private EditText etOscars;
```

**Step 7 — `ItemActivity.java`, in `initControls()`.**

```java
etOscars = findViewById(R.id.etOscars);
```

**Step 8 — `ItemActivity.java`, in `fillForm()`.** Here there are two traps in one line. `existing.getOscars()` can be `null`, and `setText` with an `Integer` resolves to `setText(int)` through unboxing:

```java
etOscars.setText(existing.getOscars() == null ? "" : String.valueOf(existing.getOscars()));
```

**Step 9 — `ItemActivity.java`, in `saveMovie()`.** An empty field means "there is no value", that is `null`, not `0`:

```java
String rawOscars = etOscars.getText().toString().trim();
movie.setOscars(rawOscars.isEmpty() ? null : Integer.parseInt(rawOscars));
```

**Step 10 — `MainActivity.java`, in `addSampleMovies()`.** You can send a number or `null`:

```java
"https://example.com/posters/inception.jpg",
4));
```

For a movie with no awards, the 11th argument is `null`.

### **Why it works this way**

`Integer` is a reference, so it has two states that `int` does not have: a value and `null`. `null` is exactly the right answer to "I do not know" — if you used `0`, you would be claiming the movie has zero awards. On reading, `Integer.parseInt` returns an `int`, and the assignment wraps it automatically in an `Integer` (autoboxing). On writing, `String.valueOf(Object)` also accepts `null` and returns the text `"null"`, which is why in `fillForm` you check first and put an empty string.

### **The mistake that costs marks**

1. **`etOscars.setText(existing.getOscars())`.** Symptom: `Resources.NotFoundException` when editing, or a number displayed as a resource. Cause: `Integer` is unboxed to `int`, and Java picks `setText(int)`, the variant that receives a resource ID. `String.valueOf(...)` is mandatory.
2. **`existing.getOscars().intValue()` without a `null` check.** Symptom: `NullPointerException` in `fillForm` on the movies with no awards. Cause: you assumed the value exists. You check `== null` before any operation.
3. **You send `0` instead of `null` for "missing".** Symptom: nothing crashes, but the list shows `oscars=0` for movies you know nothing about. Cause: you used `int` or you put `0` as the default value. The difference between "zero" and "unknown" is exactly why the requirement asks for `Integer`.

### **The check**

Add a movie with `3` at Oscars: the row shows `oscars=3`. Tap the row: the field shows `3`. Delete the value, press Update: the row shows `oscars=null`, and the app does not close. Add a new movie with the field empty: `oscars=null`, with no exception.

### **Practise**

[17.2 — `year` (Integer): the numeric attribute that can be null](cap-17.html#ex-17-2) · [19.8 — `fillForm` crashes when `release` is `null`](cap-19.html#ex-19-8)

---

## Recipe 33.4 — Add a decimal attribute (float / double)

### **The requirement, as it sounds in the test**

"Add the IMDb score to the movie (`imdbScore`, `float`) and show it in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | field `float imdbScore`, getter, setter, the 11th parameter, a line in `toString()` | yes |
| 2 | `activity_item.xml` | `TextInputEditText` with `inputType="numberDecimal"` and a new ID | yes, if you enter it from the form |
| 3 | `ItemActivity.java` | field, `findViewById`, `fillForm`, `saveMovie` with `Float.parseFloat` | yes, together with step 2 |
| 4 | `MainActivity.java` | the 11th argument, with the `f` suffix | yes, after you change the constructor |

### **The steps, in order**

**Step 1 — `Movie.java`, at the fields.** `float` is the 32-bit decimal; `double` is also a decimal, on 64 bits. Here the requirement says `float`.

```java
private String poster = null;
private float imdbScore;
```

**Step 2 — `Movie.java`, getter and setter.**

```java
public float getImdbScore() {
    return imdbScore;
}

public void setImdbScore(float imdbScore) {
    this.imdbScore = imdbScore;
}
```

**Step 3 — `Movie.java`, the constructor.** The 11th parameter:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, float imdbScore) {
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
    this.imdbScore = imdbScore;
}
```

**Step 4 — `Movie.java`, `toString()`.**

```java
", imdbScore=" + imdbScore +
```

**Step 5 — `activity_item.xml`, in the "Your verdict" card, under the rating.**

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etImdbScore"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="IMDb score"
        android:inputType="numberDecimal" />
</com.google.android.material.textfield.TextInputLayout>
```

**Step 6 — `ItemActivity.java`, at the fields.**

```java
private EditText etImdbScore;
```

**Step 7 — `ItemActivity.java`, in `initControls()`.**

```java
etImdbScore = findViewById(R.id.etImdbScore);
```

**Step 8 — `ItemActivity.java`, in `fillForm()`.** `setText` has no variant for `float`; the conversion is explicit:

```java
etImdbScore.setText(String.valueOf(existing.getImdbScore()));
```

**Step 9 — `ItemActivity.java`, in `saveMovie()`.** The keyboard may produce a decimal comma depending on the language; you normalise it before parsing:

```java
String rawScore = etImdbScore.getText().toString().trim().replace(',', '.');
movie.setImdbScore(rawScore.isEmpty() ? 0f : Float.parseFloat(rawScore));
```

**Step 10 — `MainActivity.java`, in `addSampleMovies()`.** A `float` literal has the `f` suffix; without it, Java treats it as a `double` and does not accept it where a `float` is required:

```java
"https://example.com/posters/inception.jpg",
8.8f));
```

### **Why it works this way**

`float` and `double` are both decimals, but `float` has less precision and is the type required by widgets such as `RatingBar` (`getRating()` returns a `float`). `Float.parseFloat` also accepts scientific notation (`1.6E8`), but it does not accept the decimal comma, whatever the phone's language — hence the `replace(',', '.')`. At `setText`, there is no overload for `float`, so without `String.valueOf` the code does not even compile.

### **The mistake that costs marks**

1. **`Float.parseFloat` on an empty field.** Symptom: `NumberFormatException: empty String` at Save. Cause: you skipped the `isEmpty()` check. The same for `"8,5"` if you do not normalise the comma. The same trap already exists in the code at `budget`: `Double.parseDouble(etBudget.getText().toString())` in `saveMovie()` crashes in exactly the same way if you leave the budget empty.
2. **A literal without `f` in the constructor.** Symptom: `error: incompatible types: possible lossy conversion from double to float` at `8.8` in `addSampleMovies()`. Cause: `8.8` is a `double`; for `float` you write `8.8f`.
3. **`String.valueOf` on a large `double`.** Symptom: the form shows `1.6E8` instead of `160000000` (it happens at `budget`). Cause: `String.valueOf(double)` chooses the scientific representation for large values. For money you format with `String.format("%.0f", value)` or `DecimalFormat`.

### **The check**

Add a movie with `8.5` at IMDb: the row contains `imdbScore=8.5`. Tap the row: the field shows `8.5`, not `8.5f` and not an exception. Type `8,5` with a comma and save: the value becomes `8.5`. Leave the field empty: `imdbScore=0.0`, with no crash.

### **Practise**

[17.4 — `imdbScore` (float): the decimal with a comma](cap-17.html#ex-17-4) · [19.7 — `1.6E8` instead of `160000000`](cap-19.html#ex-19-7)

---

## Recipe 33.5 — Add a boolean attribute

### **The requirement, as it sounds in the test**

"Add a `classic` field (`boolean`) to the movie, tickable from the form, and show it in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | field `boolean classic`, getter `isClassic()`, setter, the 11th parameter, a line in `toString()` | yes |
| 2 | `activity_item.xml` | `MaterialCheckBox` with a new ID | yes, if you enter it from the form |
| 3 | `ItemActivity.java` | field, `findViewById`, `fillForm` with `setChecked`, `saveMovie` with `isChecked` | yes, together with step 2 |
| 4 | `MainActivity.java` | the 11th argument: `true` or `false` | yes, after you change the constructor |

### **The steps, in order**

**Step 1 — `Movie.java`, at the fields.** A primitive `boolean` has the default value `false`:

```java
private String poster = null;
private boolean classic;
```

**Step 2 — `Movie.java`, getter and setter.** For `boolean`, the JavaBeans convention asks for `is`, not `get`:

```java
public boolean isClassic() {
    return classic;
}

public void setClassic(boolean classic) {
    this.classic = classic;
}
```

**Step 3 — `Movie.java`, the constructor.** The 11th parameter:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, boolean classic) {
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
    this.classic = classic;
}
```

**Step 4 — `Movie.java`, `toString()`.**

```java
", classic=" + classic +
```

**Step 5 — `activity_item.xml`, in the "Your verdict" card, under the row with `swWatched` and `cbOnWatchList`.** The tick box:

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/cbClassic"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Classic" />
```

**Step 6 — `ItemActivity.java`, at the fields.** The type is `CheckBox`; `MaterialCheckBox` is a subclass of it, so `CheckBox` also works:

```java
private CheckBox cbClassic;
```

**Step 7 — `ItemActivity.java`, in `initControls()`.**

```java
cbClassic = findViewById(R.id.cbClassic);
```

**Step 8 — `ItemActivity.java`, in `fillForm()`.** Without this line, when editing the tick box always starts unticked and Save writes `false` again:

```java
cbClassic.setChecked(existing.isClassic());
```

**Step 9 — `ItemActivity.java`, in `saveMovie()`.** `isChecked()` returns exactly a `boolean`:

```java
movie.setClassic(cbClassic.isChecked());
```

**Step 10 — `MainActivity.java`, in `addSampleMovies()`.** The 11th argument:

```java
"https://example.com/posters/inception.jpg",
true));
```

### **Why it works this way**

`boolean` has only two values and a default value of `false`, so it needs no `null` checks. `CheckBox` and `Switch` are both `CompoundButton`, and the method that reports the state is `isChecked()`; the `setOnCheckedChangeListener` listener receives `(CompoundButton, boolean)` and works identically for both. `fillForm` is mandatory: without it, the object restored into the form does not reflect the value from the model, and the first Save loses it.

### **The mistake that costs marks**

1. **You forget `cbClassic.setChecked(existing.isClassic())` in `fillForm`.** Symptom: you edit a classic movie, the form shows the tick box unticked, you press Update and the movie becomes non-classic. Cause: the widget was not synchronised with the model when the screen was opened.
2. **You write `getClassic()` instead of `isClassic()`.** Symptom: it compiles, but it does not follow the JavaBeans convention and it shows in the code as an inconsistency. Cause: you copied the pattern from a non-`boolean` field. For `boolean`, the pair is `isX()` / `setX()`.
3. **You put `setChecked(true)` in `onCreate` as a "default value".** Symptom: when editing, the tick box always appears ticked, whatever the movie. Cause: you confused the field's default value with the state in the model; `fillForm` must be the only place that writes into the widget after `initControls()`.

### **The check**

Add a movie with the tick box on: the row shows `classic=true`. Tap the row: the tick box is on. Untick it, press Update: the row shows `classic=false`, and the movie is not duplicated. Add a new movie without touching the tick box: `classic=false`.

### **Practise**

[17.3 — `popular` (boolean): the flag with a default value](cap-17.html#ex-17-3) · [17.8 — `awarded` (boolean) with a conditional chip](cap-17.html#ex-17-8) · [19.1 — `tvWatchedValue` follows the switch](cap-19.html#ex-19-1)

---

## Recipe 33.6 — Add a list attribute (ArrayList<String>)

### **The requirement, as it sounds in the test**

"Add the list of actors to the movie (`actors`, `ArrayList<String>`), write them separated by commas in the form and show them in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | field `ArrayList<String> actors`, getter, setter, the 11th parameter, a line in `toString()` | yes |
| 2 | `activity_item.xml` | a single `TextInputEditText` with a new ID, for the text with commas | yes, if you enter them from the form |
| 3 | `ItemActivity.java` | field, `findViewById`, `fillForm` with `String.join`, `saveMovie` with `split` | yes, together with step 2 |
| 4 | `MainActivity.java` | the 11th argument: an `ArrayList<String>` | yes, after you change the constructor |

### **The steps, in order**

**Step 1 — `Movie.java`, at the fields.** The list is a reference; you initialise it so that it is not `null`:

```java
private String poster = null;
private ArrayList<String> actors = new ArrayList<>();
```

**Step 2 — `Movie.java`, getter and setter.** The getter returns the whole list, not one element:

```java
public ArrayList<String> getActors() {
    return actors;
}

public void setActors(ArrayList<String> actors) {
    this.actors = actors;
}
```

**Step 3 — `Movie.java`, the constructor.** The 11th parameter:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, ArrayList<String> actors) {
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
    this.actors = actors;
}
```

**Step 4 — `Movie.java`, `toString()`.** A list is displayed with square brackets and commas, through its own `toString()`:

```java
", actors=" + actors +
```

**Step 5 — `activity_item.xml`, in the "Basics" card, under the director field.** A single text field holds the whole list:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etActors"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Actors, separated by commas"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

**Step 6 — `ItemActivity.java`, at the fields.**

```java
private EditText etActors;
```

**Step 7 — `ItemActivity.java`, in `initControls()`.**

```java
etActors = findViewById(R.id.etActors);
```

**Step 8 — `ItemActivity.java`, in `fillForm()`.** You turn the list back into text, with the separator the user expects:

```java
etActors.setText(String.join(", ", existing.getActors()));
```

**Step 9 — `ItemActivity.java`, in `saveMovie()`.** You cut the text at the comma, trim the spaces and skip the empty pieces:

```java
ArrayList<String> actors = new ArrayList<>();
for (String name : etActors.getText().toString().split(",")) {
    String trimmed = name.trim();
    if (!trimmed.isEmpty()) {
        actors.add(trimmed);
    }
}
movie.setActors(actors);
```

**Step 10 — `MainActivity.java`, in `addSampleMovies()`.** You build the list before the call or directly in the argument:

```java
"https://example.com/posters/inception.jpg",
new ArrayList<>(Arrays.asList("Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"))));
```

Add the `java.util.Arrays` import in `MainActivity`.

### **Why it works this way**

An `EditText` holds a single string, so the list is encoded in a text with a separator. `String.split(",")` returns an array of strings, and `new ArrayList<>(...)` makes it modifiable. `String.join(", ", list)` does the reverse trip and is available on API 26+, and the project's `minSdk` is 33. `ArrayList` and `String` are both `Serializable`, so the list travels through the `Intent` with no extra configuration.

### **The mistake that costs marks**

1. **`Arrays.asList(text.split(","))` and then `add(...)`.** Symptom: `UnsupportedOperationException` when you try to add one more actor. Cause: `Arrays.asList` returns a fixed-size list, not an `ArrayList`. Wrap it: `new ArrayList<>(Arrays.asList(...))`.
2. **An empty field treated as a list with one element.** Symptom: after Save with no actors, the row shows `actors=[""]` or `actors=[]` depending on the implementation. Cause: `"".split(",")` returns an array with a single empty string. Check `trimmed.isEmpty()` before `add`.
3. **You forget `trim()`.** Symptom: the list shows `["Leonardo DiCaprio", " Joseph Gordon-Levitt"]`, with a leading space, and searching by name no longer finds the actor. Cause: the separator is `", "`, not `","`; the space stays in the string.

### **The check**

Add a movie with `A, B, C` at actors: the row shows `actors=[A, B, C]`. Tap the row: the field shows `A, B, C`, with spaces after the commas. Delete a name and save: the list has two elements. Leave the field empty: `actors=[]`, with no exception.

### **Practise**

[17.5 — `actors` (ArrayList\<String\>): a list in a single field](cap-17.html#ex-17-5) · [17.9 — `cast` (ArrayList\<Actor\>): the composite attribute](cap-17.html#ex-17-9)

## Recipe 33.7 — Add a composite attribute (a new class)

### **The requirement, as it sounds in the test**

"Add a director (`director`) with a name and a nationality to the movie, as a separate object, and show it in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Director.java` | a new class in `ro.ase.ie.g1097.model`, with `implements Serializable` | yes |
| 2 | `Movie.java` | field `Director director`, getter, setter, the 11th parameter, a line in `toString()` | yes |
| 3 | `activity_item.xml` | two `TextInputEditText` with new IDs (name, nationality) | yes, if you enter it from the form |
| 4 | `ItemActivity.java` | two fields, `findViewById`, `fillForm` with a `null` check, `saveMovie` with `new Director(...)` | yes, together with step 3 |
| 5 | `MainActivity.java` | the 11th argument: `new Director(...)` | yes, after you change the constructor |

### **The steps, in order**

**Step 1 — a new file `Director.java`, in the package `ro.ase.ie.g1097.model`.** The class is a POJO like `Movie`, with one detail that is not optional: `implements Serializable`.

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;

public class Director implements Serializable {

    private String name;
    private String nationality;

    public Director(String name, String nationality) {
        this.name = name;
        this.nationality = nationality;
    }

    public Director() {
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getNationality() {
        return nationality;
    }

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }

    @Override
    public String toString() {
        return "Director{name='" + name + "', nationality='" + nationality + "'}";
    }
}
```

**Step 2 — `Movie.java`, at the fields.** The field is a reference to an object, not a text:

```java
private String poster = null;
private Director director;
```

**Step 3 — `Movie.java`, getter and setter.**

```java
public Director getDirector() {
    return director;
}

public void setDirector(Director director) {
    this.director = director;
}
```

**Step 4 — `Movie.java`, the constructor.** The 11th parameter is `Director`:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, Director director) {
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
    this.director = director;
}
```

**Step 5 — `Movie.java`, `toString()`.** You do not concatenate the director's fields: you call `Director`'s `toString()`, which has to exist:

```java
", director=" + director +
```

**Step 6 — `activity_item.xml`, in the "Basics" card, under the text director field.** Two fields, one under the other:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etDirectorName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Director name"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etDirectorNationality"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Director nationality"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

**Step 7 — `ItemActivity.java`, at the fields.**

```java
private EditText etDirectorName;
private EditText etDirectorNationality;
```

**Step 8 — `ItemActivity.java`, in `initControls()`.**

```java
etDirectorName = findViewById(R.id.etDirectorName);
etDirectorNationality = findViewById(R.id.etDirectorNationality);
```

**Step 9 — `ItemActivity.java`, in `fillForm()`.** `director` can be `null` on the demo movies or on a movie saved before the change; you check before asking for `getName()`:

```java
if (existing.getDirector() != null) {
    etDirectorName.setText(existing.getDirector().getName());
    etDirectorNationality.setText(existing.getDirector().getNationality());
} else {
    etDirectorName.setText("");
    etDirectorNationality.setText("");
}
```

**Step 10 — `ItemActivity.java`, in `saveMovie()`.** You build the composite object from the two fields:

```java
movie.setDirector(new Director(
        etDirectorName.getText().toString(),
        etDirectorNationality.getText().toString()));
```

**Step 11 — `MainActivity.java`, in `addSampleMovies()`.** The 11th argument is an object:

```java
"https://example.com/posters/inception.jpg",
new Director("Christopher Nolan", "British")));
```

Add the `ro.ase.ie.g1097.model.Director` import.

### **Why it works this way**

`Movie implements Serializable`, and serialisation is **recursive**: at `putExtra`, Java writes into bytes the object and everything it reaches through its fields. If `Director` is not `Serializable` too, the chain breaks exactly at the `director` field, even though `Movie` is serialisable. On reading, `IntentCompat.getSerializableExtra` rebuilds the whole graph — which is why the object received in `ItemActivity` is a complete copy, director and all.

### **The mistake that costs marks**

1. **`Director` without `implements Serializable`.** Symptom: the app closes when you tap a row in the list, with `Parcelable encountered IOException writing serializable object` and `Caused by: NotSerializableException: ro.ase.ie.g1097.model.Director`. Cause: the serialisation of `Movie` reaches the `director` field and does not know how to write it. The compiler does not warn you — the error is only at runtime.
2. **`fillForm` without the `null` check.** Symptom: `NullPointerException` in `fillForm` on the demo movies, which have `director = null`. Cause: you called `existing.getDirector().getName()` without checking.
3. **You forget `toString()` in `Director`.** Symptom: the row shows `director=ro.ase.ie.g1097.model.Director@1a2b3c` instead of a name. Cause: `Movie.toString()` concatenates the object, and without `toString()` the default variant from `Object` is used, which displays the class name and the hash.

### **The check**

Add a movie with the director "Christopher Nolan", nationality "British": the row contains `director=Director{name='Christopher Nolan', nationality='British'}`. Tap the row: both fields are filled in. Change the nationality and press Update: the row changes, with no crash. Tap a demo movie: the fields are empty, no exception appears.

### **Practise**

[17.9 — `cast` (ArrayList\<Actor\>): the composite attribute](cap-17.html#ex-17-9) · [18.10 — combo: the `writer` attribute, in XML and in `bind()`](cap-18.html#ex-18-10)

---

## Recipe 33.8 — Add a derived (computed) attribute

### **The requirement, as it sounds in the test**

"Add the decade in which the movie came out to it (`decade`), computed from the release date, and show it in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | getter `getDecade()` that computes from `release`; a line in `toString()` | yes |
| 2 | `activity_item.xml` | nothing | no |
| 3 | `ItemActivity.java` | nothing | no |
| 4 | `MainActivity.java` | nothing | no |

### **The steps, in order**

**Step 1 — `Movie.java`, after `getRelease()`.** You add no field, no setter, no parameter in the constructor. You add only the method that computes:

```java
public int getDecade() {
    if (release == null) {
        return 0;
    }
    Calendar calendar = Calendar.getInstance();
    calendar.setTime(release);
    int year = calendar.get(Calendar.YEAR);
    return (year / 10) * 10;
}
```

**Step 2 — `Movie.java`, the import.** `Calendar` has to be imported if it is not already:

```java
import java.util.Calendar;
```

**Step 3 — `Movie.java`, `toString()`.** You call the method, not a field:

```java
", decade=" + getDecade() +
```

That is all. You do not touch the XML, you do not touch `ItemActivity`, you do not touch `MainActivity`.

### **Why it works this way**

A derived attribute has no storage: its value is a function of other fields, computed on every read. If you stored it in a field, you would have to update it manually on every change of the date — and `fillForm` and `saveMovie` could produce contradictory values. `Calendar` is needed because `Date` is only a moment in time; `Date.getYear()` is deprecated and returns the year **minus 1900**, so do not use it.

### **The mistake that costs marks**

1. **You add a field and a setter for a derived attribute.** Symptom: the code compiles, but after you edit the date, `decade` stays old. Cause: you stored a value that should have been computed; two sources of truth contradict each other.
2. **You do not check `release == null`.** Symptom: `NullPointerException` in `toString()` on a movie with no date, that is exactly when the list is redrawn. Cause: `calendar.setTime(null)` throws an exception.
3. **You use `release.getYear()`.** Symptom: for 2010 you get `110`. Cause: the method is deprecated and counts the years from 1900. `Calendar.get(Calendar.YEAR)` returns the correct calendar year.

### **The check**

The list shows `decade=2010` for Inception, `decade=1990` for Toy Story and The Matrix. Edit a movie's date to 1985 and save: the row shows `decade=1980`, without your having touched any new field. A movie with a missing date shows `decade=0`, with no crash.

### **Practise**

[17.8 — `awarded` (boolean) with a conditional chip](cap-17.html#ex-17-8) · [19.4 — `tvDurationValue` shows "1 h 22 min"](cap-19.html#ex-19-4)

---

## Recipe 33.9 — Change the type of an existing attribute

### **The requirement, as it sounds in the test**

"Change the rating's type from `float` to `double`, without breaking the form and the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | the field, the getter, the setter and the constructor parameter become `double` | yes |
| 2 | `ItemActivity.java` | `fillForm` needs a cast at `setRating(float)` | yes |
| 3 | `activity_item.xml` | nothing | no |
| 4 | `MainActivity.java` | the literals `4.5f`, `4f`, `5f` stay valid | no |

### **The steps, in order**

**Step 1 — `Movie.java`, the field.**

```java
private double rating;
```

**Step 2 — `Movie.java`, getter and setter.** Both change together with the field:

```java
public double getRating() {
    return rating;
}

public void setRating(double rating) {
    this.rating = rating;
}
```

**Step 3 — `Movie.java`, the constructor.** The parameter becomes `double`:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             double rating, boolean watched, String approval, boolean onWatchlist,
             String poster) {
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
}
```

**Step 4 — `Movie.java`, `toString()`.** Nothing changes: concatenation with `+` accepts any primitive type.

**Step 5 — `ItemActivity.java`, in `fillForm()`.** `RatingBar.setRating` asks for `float`, and `getRating()` now returns `double`. The conversion from `double` to `float` is **narrowing** and needs an explicit cast:

```java
rbRating.setRating((float) existing.getRating());
```

**Step 6 — `ItemActivity.java`, in `saveMovie()`.** Here no cast is needed: `rbRating.getRating()` returns a `float`, and a `float` widens automatically to a `double`:

```java
movie.setRating(rbRating.getRating());
```

**Step 7 — `MainActivity.java`, in `addSampleMovies()`.** The literals `4.5f`, `4f`, `5f` stay valid: a `float` widens automatically to a `double`. You can leave them as they are or write them `4.5`, `4.0`, `5.0`.

### **Why it works this way**

Java does conversions automatically only when **no information is lost**: `float` → `double` is a widening, so it works without a cast; `double` → `float` is a narrowing, so it asks for an explicit cast and may lose precision. `RatingBar` was designed with `float`, so at the boundary between the model (`double`) and the widget (`float`) you have to convert yourself. The rest of the chain — `toString()`, `Intent`, `ArrayAdapter` — does not depend on the exact type of the decimal.

### **The mistake that costs marks**

1. **You forget the cast in `fillForm`.** Symptom: `error: incompatible types: possible lossy conversion from double to float` at `rbRating.setRating(existing.getRating())`. Cause: you changed the model, but the widget still has `setRating(float)`.
2. **You change the field, but not the getter and the setter.** Symptom: errors in a chain at `setRating(double)` and `getRating()` — the signature no longer matches the field. Cause: the attribute's type is the contract made of field + getter + setter + parameter; all four change together.
3. **You make the reverse change, at `budget` (`double` → `float`), and forget `String.valueOf`.** Symptom: the form shows `1.6E8` instead of `160000000`. Cause: the scientific representation of `double`; for money you format with `String.format("%.0f", value)`.

### **The check**

The list shows `rating=4.5`, `rating=4.0`, `rating=5.0`. Tap a row: the stars show exactly the value from the model, and the field does not crash. Change the rating to 3.5 and save: the row shows `rating=3.5`. The compilation passes with no conversion warnings.

### **Practise**

[18.2 — `etBudget` becomes a `SeekBar` (0–500 million, step 1 million)](cap-18.html#ex-18-2) · [18.3 — `rbRating` (`RatingBar`) becomes a `Spinner` with 1–5 stars](cap-18.html#ex-18-3) · [19.7 — `1.6E8` instead of `160000000`](cap-19.html#ex-19-7)

---

## Recipe 33.10 — Rename an attribute and propagate it through the code

### **The requirement, as it sounds in the test**

"Rename the `poster` field to `posterUrl` and update all the code that uses it."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `Movie.java` | the field, the getter, the setter, the constructor parameter, the line in `toString()` | yes |
| 2 | `ItemActivity.java` | `getPoster()` → `getPosterUrl()`, `setPoster()` → `setPosterUrl()` | yes |
| 3 | `MainActivity.java` | nothing: the constructor is positional, the parameter name is not visible at the call | no |
| 4 | `activity_item.xml` | nothing: the ID `etPoster` is independent of the field name | no |

### **The steps, in order**

**Step 1 — `Movie.java`, the field.** You change the name, not the type:

```java
private String posterUrl = null;
```

**Step 2 — `Movie.java`, the getter and the setter.** Their names are the class's public contract; they change mandatorily together with the field:

```java
public String getPosterUrl() {
    return posterUrl;
}

public void setPosterUrl(String posterUrl) {
    this.posterUrl = posterUrl;
}
```

**Step 3 — `Movie.java`, the constructor.** The parameter is renamed and the assignment uses the new name:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String posterUrl) {
    this.title = title;
    this.release = release;
    this.genre = genre;
    this.budget = budget;
    this.duration = duration;
    this.rating = rating;
    this.watched = watched;
    this.approval = approval;
    this.onWatchlist = onWatchlist;
    this.posterUrl = posterUrl;
}
```

**Step 4 — `Movie.java`, `toString()`.** The line uses the field, so it changes:

```java
", posterUrl='" + posterUrl + '\'' +
```

The label in the text (`posterUrl=`) is cosmetic, but you change it so that it does not mislead.

**Step 5 — `ItemActivity.java`, in `fillForm()`.** The old call no longer compiles:

```java
etPoster.setText(existing.getPosterUrl());
```

**Step 6 — `ItemActivity.java`, in `saveMovie()`.** The same:

```java
movie.setPosterUrl(etPoster.getText().toString());
```

**Step 7 — you check whether other calls still exist.** Search the whole project for `getPoster` and `setPoster`. In G1097 there is no other one; if you added one yourself in an earlier recipe, you update that one too.

### **Why it works this way**

The field is `private`, so its name is not visible from outside the class; the getter and the setter are the only contract. When you rename the getter, all the calls that use it become compilation errors — and this is the good variant: the compiler gives you the complete list of places to change. `MainActivity` is not touched because there the constructor is called positionally: `new Movie(..., "https://...")` does not contain the parameter name.

### **The mistake that costs marks**

1. **You rename the field, but leave the getter `getPoster()`.** Symptom: the code compiles, but the class has a `posterUrl` field and a `getPoster()` getter that returns `posterUrl`. Cause: you changed only half of the contract; it is legal, but inconsistent and hard to read.
2. **You rename the getter and forget one call.** Symptom: `error: cannot find symbol method getPoster()` in `ItemActivity`. Cause: you changed the contract, but not all the callers. It is not a logic mistake — you solve it by reading the error.
3. **You also rename the `etPoster` ID "so that it matches".** Symptom: a compilation error at `findViewById(R.id.etPoster)` after you changed the XML. Cause: you confused the Java field name with the ID in the XML. They are independent: you can have the field `etPoster` and the ID `etPosterUrl`, as long as `findViewById` uses the correct ID.

### **The check**

The project compiles with no reference to `getPoster` or `setPoster`. The list shows `posterUrl='https://...'`. Tap a row: the "Poster URL" field is filled in. Change the URL and save: the row updates.

### **Practise**

[17.10 — `writer` + `popular`: the two requirements, in 30 minutes](cap-17.html#ex-17-10) · [24.7 — the checklist after every "add an attribute"](cap-24.html#ex-24-7)

---

## Recipe 33.11 — Add a widget to the form

### **The requirement, as it sounds in the test**

"Add under the release date a label that shows the chosen year, updated when you change the date."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `activity_item.xml` | a `TextView` with a new ID, under the `etRelease` block | yes |
| 2 | `ItemActivity.java` | field, `findViewById`, an update in `onDateSet` and in `fillForm` | yes |
| 3 | `Movie.java` | nothing | no |

### **The steps, in order**

**Step 1 — `activity_item.xml`, in the "Basics" card, immediately after the `TextInputLayout` of `etRelease`.** The label:

```xml
<TextView
    android:id="@+id/tvReleaseYear"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:text="Year: —"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorPrimary" />
```

**Step 2 — `ItemActivity.java`, at the fields.**

```java
private TextView tvReleaseYear;
```

**Step 3 — `ItemActivity.java`, in `initControls()`.**

```java
tvReleaseYear = findViewById(R.id.tvReleaseYear);
```

**Step 4 — `ItemActivity.java`, in `onDateSet` from `showReleaseDatePicker()`.** Here you already have the year as a parameter, so you do not parse the text again:

```java
public void onDateSet(DatePicker view, int year, int month, int day) {
    releaseCal.set(year, month, day);
    etRelease.setError(null);
    etRelease.setText(dateFormat.format(releaseCal.getTime()));
    tvReleaseYear.setText("Year: " + year);
}
```

**Step 5 — `ItemActivity.java`, in `fillForm()`.** Here is the app's real trap: `fillForm` writes into `etRelease`, but it **does not synchronise `releaseCal`**. If you add the label without fixing this, when editing the label shows today's year, and Save writes today's date. You synchronise both:

```java
etRelease.setText(dateFormat.format(existing.getRelease()));
releaseCal.setTime(existing.getRelease());
tvReleaseYear.setText("Year: " + releaseCal.get(Calendar.YEAR));
```

**Step 6 — `ItemActivity.java`, in `clearForm()` if you added the button from recipe 33.13.** You reset the label too:

```java
tvReleaseYear.setText("Year: —");
```

### **Why it works this way**

The label is a **mirror** of the state, not a second source of truth: you update it from `releaseCal`, exactly in the places where `releaseCal` changes. `onDateSet` is the only place where the user chooses a date, and `fillForm` is the only place where the form receives an existing date. If you update the label from `etRelease.getText()`, you parse a text you have just formatted — a useless and fragile operation.

### **The mistake that costs marks**

1. **You forget `fillForm`.** Symptom: you edit a movie, the label shows "Year: —" or today's year, although the date field shows the movie's date. Cause: you updated the label only in `onDateSet`, which is not called when the screen is opened.
2. **You do not synchronise `releaseCal` in `fillForm`.** Symptom: you edit a movie from 2010, you do not touch the date, you press Update and the movie becomes "released today". Cause: `releaseCal` stayed at `Calendar.getInstance()` from the field initialisation; `saveMovie` writes `releaseCal.getTime()`, not the text in `etRelease`. It is a real bug of the app, not only of the recipe.
3. **You update the label from `etRelease.getText()` in `onDateSet`.** Symptom: it works, but after the user types a date by hand and then opens the picker, the label can lag behind. Cause: you have two sources of truth; use `releaseCal`.

### **The check**

Open the form: the label shows "Year: —". Press on the date, choose 16 July 2010: the field shows `16/07/2010`, the label shows "Year: 2010". Save: the row contains `release=...2010`. Tap the row: the label shows "Year: 2010" from the start, without opening the picker. Press Update without touching the date: the year stays 2010.

### **Practise**

[18.1 — `tvDurationValue` bound to a `SeekBar`](cap-18.html#ex-18-1) · [19.2 — a character counter under `etTitle`](cap-19.html#ex-19-2) · [19.4 — `tvDurationValue` shows "1 h 22 min"](cap-19.html#ex-19-4) · [19.8 — `fillForm` crashes when `release` is `null`](cap-19.html#ex-19-8)

## Recipe 33.12 — Add a widget to the list row

### **The requirement, as it sounds in the test**

"Add to the list row a `TextView` that shows the movie's director."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `movie_item.xml` | a `TextView` with a new ID, in the info column | yes, but with **no effect** in the current app |
| 2 | `Movie.java` | the `writer` attribute (recipe 33.1) and its line in `toString()` | yes, for the `ListView` |
| 3 | `MovieAdapter.java` | a field in the `ViewHolder`, `findViewById`, `setText` in `bind()` | only if you did the migration to `RecyclerView` |
| 4 | `MainActivity.java` | nothing, as long as you stay on `ArrayAdapter` | no |

### **The steps, in order**

**Step 0 — what you need to know before the first step.** `movie_item.xml` **exists in G1097, but no code uses it**. `MainActivity` creates `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, and `simple_list_item_1` is a system layout with **a single `TextView`**. No `inflate` touches `movie_item.xml`. The file is prepared for `RecyclerView` and becomes active only at the migration from chapter 23. The recipe assumes that `writer` already exists in `Movie` (recipe 33.1); if not, you add the field, the getter, the setter and the line in `toString()` first.

**Step 1 — `movie_item.xml`, in the info column, after `movieSubtitle`.** You add the `TextView`:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Writer"
    android:textSize="13sp"
    android:textColor="#616161"
    android:maxLines="1"
    android:ellipsize="end" />
```

**Step 2 — if you stay on `ListView`.** Nothing new shows: the row is drawn by `simple_list_item_1`, which knows nothing about `movieWriter`. The only way for the attribute to appear is `toString()` in `Movie`. You extend the existing method with `writer` (or rewrite it compactly, if you want a shorter row):

```java
@Override
public String toString() {
    return title + " — " + writer + " (" + rating + ")";
}
```

This is the correct variant for `ListView` and it is the one that earns marks on the test if `RecyclerView` is not explicitly asked of you.

**Step 3 — if you migrated to `RecyclerView`.** In `MovieAdapter`, in the `ViewHolder`, you add the field and bind it:

```java
private final TextView movieWriter;

public MovieViewHolder(@NonNull View itemView) {
    super(itemView);
    movieTitle = itemView.findViewById(R.id.movieTitle);
    movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
    movieWriter = itemView.findViewById(R.id.movieWriter);
}
```

**Step 4 — `MovieAdapter`, in `bind()`.** You fill the field from the model:

```java
movieWriter.setText(movie.getWriter());
```

**Step 5 — `MainActivity`, after any change to the list.** The adapter does not notice the change by itself:

```java
movieAdapter.notifyDataSetChanged();
```

### **Why it works this way**

`ArrayAdapter` has a single contract with the row: it takes the object from the list and turns it into text through `toString()`. It does not read `movie_item.xml` and does not look for views by ID. `RecyclerView` is the one that needs a row layout and its own adapter, with a `ViewHolder`; only then does `findViewById` have something to find. That is why, in G1097, adding to `movie_item.xml` is a **preparatory** change, not a visible one.

### **The mistake that costs marks**

1. **You add the widget in `movie_item.xml` and wait for it to appear.** Symptom: you run the app, add a movie, the row looks exactly as before. Cause: the file is not inflated anywhere; `ArrayAdapter` uses `simple_list_item_1`.
2. **You add the attribute in the model, but not in `toString()`.** Symptom: the same, the row does not change, although the value is saved. Cause: for `ListView`, `toString()` is the only window onto the screen.
3. **You change the list, but forget `notifyDataSetChanged()`.** Symptom: after Save, the data is in `movies`, but the list shows the old content until you scroll or rotate the screen. Cause: the adapter holds a reference to the list, but it is not notified to redraw.

### **The check**

With `ListView`: add a movie with a director and check that the row contains the director's name through `toString()`. With `RecyclerView`: after the migration, the row has an extra `TextView`, and on scroll the text stays correct (it does not get mixed between rows). In both cases, after editing the row updates without a duplicate.

### **Practise**

[18.4 — a second line in the `ListView` row (your own `BaseAdapter`)](cap-18.html#ex-18-4) · [18.6 — the poster URL in a `TextView`](cap-18.html#ex-18-6) · [18.8 — the row shows `Inception (2010)`: `toString()` or a custom adapter?](cap-18.html#ex-18-8) · [23.4 — `MovieViewHolder` with the fields from `movie_item.xml`](cap-23.html#ex-23-4) · [23.6 — `onBindViewHolder`: title and subtitle](cap-23.html#ex-23-6)

---

## Recipe 33.13 — Add a button

### **The requirement, as it sounds in the test**

"Add a 'Clear form' button to the form that empties all the fields, without closing the screen."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `activity_item.xml` | `MaterialButton` with a new ID, under the Save button | yes |
| 2 | `ItemActivity.java` | field, `findViewById`, listener, the `clearForm()` method | yes |
| 3 | `Movie.java` | nothing | no |

### **The steps, in order**

**Step 1 — `activity_item.xml`, after `btnMovieAction`.** The button, with the same width and a secondary style:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnClear"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:layout_marginTop="12dp"
    android:text="Clear form" />
```

**Step 2 — `ItemActivity.java`, at the fields.**

```java
private Button btnClear;
```

**Step 3 — `ItemActivity.java`, in `initControls()`.**

```java
btnClear = findViewById(R.id.btnClear);
```

**Step 4 — `ItemActivity.java`, in `initListeners()`.** The listener calls the method, it does not contain the logic:

```java
btnClear.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        clearForm();
    }
});
```

**Step 5 — `ItemActivity.java`, the new `clearForm()` method.** It empties every widget and, mandatorily, resets `releaseCal`:

```java
private void clearForm() {
    etTitle.setText("");
    etRelease.setText("");
    releaseCal = Calendar.getInstance();
    spGenre.setSelection(0);
    etBudget.setText("");
    sbDuration.setProgress(0);
    rbRating.setRating(0);
    swWatched.setChecked(false);
    cbonWatchList.setChecked(false);
    rgApproval.check(R.id.rbGeneral);
    etPoster.setText("");
    tvDurationValue.setText("0 min.");
    tvWatchedValue.setText("No");
}
```

**Step 6 — `ItemActivity.java`, check the imports.** `Calendar` is already imported; `Button` is already imported. You add nothing.

### **Why it works this way**

The button is only a trigger: `setOnClickListener` runs your method. `clearForm()` has to touch **all** the form's data sources, not only the visible ones. `releaseCal` is an invisible source: `saveMovie()` writes `releaseCal.getTime()`, so if you leave it untouched, the button empties the date field, but Save still writes the old date. `rgApproval.check(R.id.rbGeneral)` is needed because a `RadioGroup` has no "empty state": it always has one button selected.

### **The mistake that costs marks**

1. **You empty `etRelease`, but not `releaseCal`.** Symptom: you press Clear, the date field is empty, you press Save and the movie has the old date. Cause: you cleaned the text, not the state. `releaseCal = Calendar.getInstance()` is the line that matters.
2. **You forget `rgApproval.check(R.id.rbGeneral)`.** Symptom: after Clear, `PG-13` or `R` stays selected. Cause: a `RadioGroup` is not emptied by `setChecked(false)` on its children; you select a button explicitly.
3. **You put the clearing logic directly in the listener.** Symptom: it works, but the code becomes hard to read and you cannot reuse the clearing after Save. Cause: you mixed the trigger with the action; the separate `clearForm()` method is the clean answer.

### **The check**

Fill in the form, press "Clear form": all the fields are empty, the slider is at 0, the stars at 0, the approval is on `G`, and the labels show "0 min." and "No". Press Save: the movie is saved with the empty values, with no crash and with no old date. The "Save Movie" button stays functional.

### **Practise**

[20.1 — the "Clear form" button under "Save Movie"](cap-20.html#ex-20-1) · [20.3 — the "Delete" button in `ItemActivity`, with its own result code](cap-20.html#ex-20-3) · [20.10 — the exam combination: the "Duplicate movie" button](cap-20.html#ex-20-10)

---

## Recipe 33.14 — Add a control above the list

### **The requirement, as it sounds in the test**

"Add above the list a button that sorts the movies by title."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `activity_main.xml` | you change the root from `FrameLayout` to a vertical `LinearLayout` and wrap the list + the FAB in a `FrameLayout` | yes |
| 2 | `MainActivity.java` | field, `findViewById`, a listener that sorts the list and notifies the adapter | yes |
| 3 | `Movie.java` | nothing | no |

### **The steps, in order**

**Step 1 — `activity_main.xml`, the root.** `FrameLayout` overlaps its children: a control placed first is covered by the `ListView`, which has `match_parent`. To have a row above the list, the root becomes a vertical `LinearLayout`, and the list and the FAB stay together in a `FrameLayout` with `layout_weight="1"`:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".activities.MainActivity">

    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnSort"
        style="@style/Widget.Material3.Button.TonalButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginHorizontal="16dp"
        android:layout_marginTop="8dp"
        android:text="Sort by title" />

    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <ListView
            android:id="@+id/listView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:entries="@array/items" />

        <com.google.android.material.floatingactionbutton.FloatingActionButton
            android:id="@+id/floatingActionButton"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="bottom|end"
            android:layout_margin="16dp"
            android:contentDescription="Add"
            app:srcCompat="@drawable/outline_add_24" />
    </FrameLayout>
</LinearLayout>
```

> Keep `android:id="@+id/main"` on the root: the insets listener in `onCreate` looks for it. `android:entries="@array/items"` on the `ListView` is ignored at runtime, because `initControls()` calls `listView.setAdapter(movieAdapter)`.

**Step 2 — `MainActivity.java`, at the fields.**

```java
private Button btnSort;
```

**Step 3 — `MainActivity.java`, in `initControls()`.**

```java
btnSort = findViewById(R.id.btnSort);
```

**Step 4 — `MainActivity.java`, in `initListeners()`.** You sort the list **in place** and notify the adapter:

```java
btnSort.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Collections.sort(movies, new Comparator<Movie>() {
            @Override
            public int compare(Movie m1, Movie m2) {
                return m1.getTitle().compareToIgnoreCase(m2.getTitle());
            }
        });
        movieAdapter.notifyDataSetChanged();
    }
});
```

**Step 5 — `MainActivity.java`, the imports.** You add:

```java
import java.util.Collections;
import java.util.Comparator;
```

### **Why it works this way**

`movieAdapter` was built with `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)` and holds the **reference** to the `movies` list. If you sort that same list, the adapter sees the new order; if you replaced the reference with a new list, the adapter would stay on the old one. `Collections.sort` sorts in place, and `notifyDataSetChanged()` is the signal to the `ListView` to redraw the rows. `compareToIgnoreCase` makes the sort case-insensitive, so that "toy story" does not end up after "The Matrix" because of the ASCII code.

### **The mistake that costs marks**

1. **You put the button directly in the `FrameLayout`, above the `ListView`.** Symptom: the button is not visible at all, although it is in the XML. Cause: `FrameLayout` overlaps its children, and the `ListView` with `match_parent` covers it. The solution is the vertical parent + `layout_weight`.
2. **You replace the list instead of sorting it.** Symptom: `error: cannot assign a value to final variable movies` or, if you removed `final`, the list is sorted but the screen does not change. Cause: `movies` is `final` and, more importantly, the adapter holds the reference to it; it has to be sorted in place.
3. **You forget `notifyDataSetChanged()`.** Symptom: you press the button, the order in memory changes, but the list looks the same until the next addition. Cause: the adapter does not notice changes to the list by itself.

### **The check**

The initial list is Inception, Toy Story, The Matrix. Press "Sort by title": the order becomes Inception, The Matrix, Toy Story. Add a movie with the title "Alien" and press again: Alien goes to the top. The FAB stays visible at the bottom right, and the list scrolls correctly.

### **Practise**

[20.2 — the second FAB, bottom left, which shows the number of movies](cap-20.html#ex-20-2) · [20.4 — a `Switch` above the list that filters the watched movies](cap-20.html#ex-20-4) · [20.8 — a `Spinner` above the list for sorting](cap-20.html#ex-20-8) · [24.1 — what happens if you forget `notifyDataSetChanged()`](cap-24.html#ex-24-1)

---

## Recipe 33.15 — Swap one widget for another

### **The requirement, as it sounds in the test**

"Replace the `swWatched` `Switch` with a `CheckBox`, without breaking the saving and without changing the ID."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `activity_item.xml` | you replace the `MaterialSwitch` tag with `MaterialCheckBox`, you keep `android:id="@+id/swWatched"` | yes |
| 2 | `ItemActivity.java` | you change the field's type from `MaterialSwitch` to `CheckBox`; the rest stays | yes |
| 3 | `ItemActivity.java` | you change the `MaterialSwitch` import to `CheckBox` | yes |
| 4 | `Movie.java` | nothing: `isWatched()` and `setWatched()` do not change | no |

### **The steps, in order**

**Step 1 — `activity_item.xml`, in the "Your verdict" card.** You replace the tag, but **keep the ID**:

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/swWatched"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginEnd="12dp"
    android:text="Watched" />
```

**Step 2 — `ItemActivity.java`, the field.** The type changes, the name stays:

```java
private CheckBox swWatched;
```

**Step 3 — `ItemActivity.java`, the imports.** You remove `com.google.android.material.materialswitch.MaterialSwitch` and add:

```java
import android.widget.CheckBox;
```

**Step 4 — `ItemActivity.java`, `initControls()`.** The line stays almost identical; `findViewById` returns the new type, because the ID is the same:

```java
swWatched = findViewById(R.id.swWatched);
```

**Step 5 — `ItemActivity.java`, `fillForm()`.** `CheckBox` is a `CompoundButton`, so the method exists unchanged:

```java
swWatched.setChecked(existing.isWatched());
```

**Step 6 — `ItemActivity.java`, `saveMovie()`.** The same:

```java
movie.setWatched(swWatched.isChecked());
```

**Step 7 — `ItemActivity.java`, `initListeners()`.** The listener stays on `CompoundButton`, the type the two widgets have in common:

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});
```

### **Why it works this way**

The ID is the contract between the XML and the code: `findViewById(R.id.swWatched)` looks in the view tree for a view with that ID and returns it with the real type from the XML. `CheckBox` and `MaterialSwitch` are both subclasses of `CompoundButton`, which defines `isChecked()`, `setChecked()` and `setOnCheckedChangeListener()`. That is why, if you keep the ID, the only changes are the tag in the XML, the field's type and the import. The model is not touched at all.

### **The mistake that costs marks**

1. **You also change the ID, but forget `findViewById`.** Symptom: `error: cannot find symbol variable swWatched` or, if you changed only the XML, `NullPointerException` at `swWatched.setChecked(...)`. Cause: the ID in the XML and the one in `R.id` have to be identical. If you rename the ID, you change it in **all** the places.
2. **You change the field's type, but leave the `MaterialSwitch` import.** Symptom: `error: cannot find symbol class MaterialSwitch` after you deleted the tag, or `incompatible types` at the assignment. Cause: the old import stayed and the new one is missing.
3. **You use `Switch.OnCheckedChangeListener`.** Symptom: `error: cannot find symbol` — no such interface exists. Cause: the listener is defined in `CompoundButton`, the common parent class.

### **The check**

The form shows a square tick box instead of the switch. Add a movie with the tick box on: the row shows `watched=true`. Tap the row: the tick box is on, and the "Yes" label is displayed. Untick it: the label becomes "No" immediately. Save: the row shows `watched=false`.

### **Practise**

[18.2 — `etBudget` becomes a `SeekBar` (0–500 million, step 1 million)](cap-18.html#ex-18-2) · [18.3 — `rbRating` (`RatingBar`) becomes a `Spinner` with 1–5 stars](cap-18.html#ex-18-3) · [20.9 — `TextInputLayout` with `endIconMode="clear_text"` and what the clearing does NOT do](cap-20.html#ex-20-9)

---

## Recipe 33.16 — Add a new screen (Activity + layout + manifest)

### **The requirement, as it sounds in the test**

"Add a new screen that shows the movie's title and genre, opened with a long press on the row in the list."

### **Files touched**

| # | File | What you do | Required? |
|---|---|---|---|
| 1 | `activity_detail.xml` | a new layout, with `TextView`s with new IDs | yes |
| 2 | `DetailActivity.java` | a new class in `ro.ase.ie.g1097.activities` | yes |
| 3 | `AndroidManifest.xml` | `<activity android:name=".activities.DetailActivity" android:exported="false" />` | yes |
| 4 | `MainActivity.java` | `setOnItemLongClickListener` that starts the screen with `startActivity` | yes |

### **The steps, in order**

**Step 1 — `res/layout/activity_detail.xml`, a new file.** A simple layout, with a `LinearLayout` root:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp">

    <TextView
        android:id="@+id/tvDetailTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Movie title"
        android:textAppearance="?attr/textAppearanceHeadlineMedium"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/tvDetailGenre"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="Genre"
        android:textAppearance="?attr/textAppearanceBodyLarge" />
</LinearLayout>
```

**Step 2 — `DetailActivity.java`, a new file in `ro.ase.ie.g1097.activities`.** It reads the movie from the `Intent` with `IntentCompat`, exactly like `ItemActivity`:

```java
package ro.ase.ie.g1097.activities;

import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.IntentCompat;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class DetailActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);

        TextView tvDetailTitle = findViewById(R.id.tvDetailTitle);
        TextView tvDetailGenre = findViewById(R.id.tvDetailGenre);

        Movie movie = IntentCompat.getSerializableExtra(
                getIntent(), MainActivity.MOVIE_EXTRA, Movie.class);

        if (movie != null) {
            tvDetailTitle.setText(movie.getTitle());
            tvDetailGenre.setText(movie.getGenre());
        }
    }
}
```

**Step 3 — `AndroidManifest.xml`, in `<application>`, after `ItemActivity`.** Without this entry, the screen cannot be started:

```xml
<activity
    android:name=".activities.DetailActivity"
    android:exported="false" />
```

**Step 4 — `MainActivity.java`, in `initListeners()`.** You add the long press, next to `setOnItemClickListener`:

```java
listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
    @Override
    public boolean onItemLongClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, DetailActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        startActivity(intent);
        return true;
    }
});
```

**Step 5 — `MainActivity.java`, the imports.** `Intent` and `AdapterView` are already imported; `DetailActivity` is in the same package, so it needs no import.

### **Why it works this way**

Every `Activity` has to be declared in `AndroidManifest.xml`, otherwise the system does not know it and `startActivity` throws `ActivityNotFoundException`. `android:exported="false"` is correct for an internal screen: only your app can start it. `setContentView` has to be called before `findViewById`, because it is what builds the view tree. `IntentCompat.getSerializableExtra` is the variant the app uses for `Serializable` on API 33+, where the old method is deprecated. Unlike `ItemActivity`, this screen is started with `startActivity`, not with `launcher`, because it has no result to return.

### **The mistake that costs marks**

1. **You forget the manifest entry.** Symptom: the app closes on the long press, with `ActivityNotFoundException: Unable to find explicit activity class ... DetailActivity; have you declared this activity in your AndroidManifest.xml?`. Cause: the class exists, but the system does not know it.
2. **You forget `setContentView`.** Symptom: `NullPointerException` at `tvDetailTitle.setText(...)`, because `findViewById` finds nothing in a tree that does not exist. Cause: you skipped the line that loads the layout.
3. **You return `false` from `onItemLongClick`.** Symptom: the long press opens the new screen, but immediately after it the edit screen opens too. Cause: `false` means "the event was not consumed", so the `ListView` also sends the normal click. `return true` consumes it.

### **The check**

Long-press "Inception": the new screen opens, with the title "Inception" and the genre "Sci-Fi". The Back button takes you back to the list, without changing anything. Short-press the same row: the edit form opens, not the new screen. Add a movie and long-press it: the new screen shows its title.

### **Practise**

[23.9 — row click with `getBindingAdapterPosition()` and a callback](cap-23.html#ex-23-9) · [24.2 — you edit a movie, the list shows the NEW values. Why `set` and not `add`?](cap-24.html#ex-24-2) · [24.4 — 3 additions + 1 edit: the number of movies is correct](cap-24.html#ex-24-4)

---

## The table of the 16 recipes

| Recipe | What you add | Files touched | Time | Exercise |
|---|---|---|---|---|
| 33.1 | `String` attribute | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.1](cap-17.html#ex-17-1) |
| 33.2 | `int` attribute | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.6](cap-17.html#ex-17-6) |
| 33.3 | `Integer` attribute (nullable) | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.2](cap-17.html#ex-17-2) |
| 33.4 | `float` / `double` attribute | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.4](cap-17.html#ex-17-4) |
| 33.5 | `boolean` attribute | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 10 min | [17.3](cap-17.html#ex-17-3) |
| 33.6 | `ArrayList<String>` attribute | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.5](cap-17.html#ex-17-5) |
| 33.7 | composite attribute (new class) | `Director`, `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 15 min | [17.9](cap-17.html#ex-17-9) |
| 33.8 | derived attribute | `Movie` | 5 min | [19.4](cap-19.html#ex-19-4) |
| 33.9 | you change an attribute's type | `Movie`, `ItemActivity` | 8 min | [18.3](cap-18.html#ex-18-3) |
| 33.10 | you rename an attribute | `Movie`, `ItemActivity` | 8 min | [17.10](cap-17.html#ex-17-10) |
| 33.11 | new widget in the form | `activity_item`, `ItemActivity` | 10 min | [18.1](cap-18.html#ex-18-1) |
| 33.12 | new widget in the row | `movie_item`, adapter (if it exists) | 10 min | [23.6](cap-23.html#ex-23-6) |
| 33.13 | new button | `activity_item`, `ItemActivity` | 10 min | [20.1](cap-20.html#ex-20-1) |
| 33.14 | control above the list | `activity_main`, `MainActivity` | 12 min | [20.8](cap-20.html#ex-20-8) |
| 33.15 | you swap one widget for another | `activity_item`, `ItemActivity` | 8 min | [18.2](cap-18.html#ex-18-2) |
| 33.16 | new screen | new layout, `DetailActivity`, manifest, `MainActivity` | 15 min | [23.9](cap-23.html#ex-23-9) |

---

## Chapter 33 summary

- **The order is always the same:** model → XML → `ItemActivity` → display. The model first, because it depends on nothing; the XML second, because `findViewById` needs an ID; the binding third; the display last.
- **A new attribute has four places in the model:** field, getter, setter, parameter in the constructor — plus `toString()` if you want it to show in the `ListView`. All five change together.
- **The constructor is positional.** When you add a parameter to it, you update all the `new Movie(...)` calls. The compiler tells you exactly how many arguments are missing.
- **`setText` has two faces.** `setText(CharSequence)` writes text; `setText(int)` looks for a resource. For numbers, `String.valueOf(...)` is mandatory — otherwise the `int` becomes a resource ID and you get `Resources.NotFoundException`.
- **You parse with protection.** `Integer.parseInt`, `Float.parseFloat` and `Double.parseDouble` throw `NumberFormatException` on an empty string. You check `isEmpty()` and do `trim()`; for decimals you normalise the comma.
- **`fillForm` is the mirror of `saveMovie`.** Every widget read at save time has to be written at load time. The app's real trap: `fillForm` does not synchronise `releaseCal`, so an edit without touching the date saves today's date.
- **`ListView` displays `toString()`.** `movie_item.xml` exists, but no code uses it; it becomes active only at the migration to `RecyclerView`.
- **The ID is the contract.** You can change the widget's type without touching the model, if you keep the ID; if you rename it, you change it in the XML and in every `findViewById`.
- **A new screen has three mandatory parts:** a layout, a class that calls `setContentView` before `findViewById`, and an entry in `AndroidManifest.xml`. Without the manifest, `ActivityNotFoundException`.
