# Chapter 29 — The G1096 code, annotated

**Objective:** to read every line of the G1096 app with the explanation glued to it — what it does, why it is there, what breaks if you remove it — and to see exactly how it differs from G1097, so you do not learn one variant and write another.

**Estimated time:** 90–120 min (active reading, with the project open alongside).

**Source:** `mihaidoinea/dma2026`, commit `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`. Group G1096 **does not have** `movie_item.xml`.

**Rule:** the code is **unmodified, byte for byte**. Everything that appears with `//`, `/* */` or `<!-- -->` beyond the source is annotation. The comments that already existed in the source (`//EditText`, `//Spinner`, `<!-- Header -->`) were kept exactly, and the annotation was built around them.

---

## 29.0 What differs from G1097

The app is the same: `MainActivity` holds a `List<Movie>`, an `ArrayAdapter` displays it in a `ListView`, the FAB opens `ItemActivity` through an `Intent`, the result comes back through an `ActivityResultLauncher`, and `ItemActivity` builds a `Movie` from the form. The same ten fields, the same widgets, the same two screen layouts.

The differences are few and small. That is exactly why they matter: they are precisely the places where an exam question can get two correct answers, depending on which group you read.

| Aspect | G1096 | G1097 (reference) |
|---|---|---|
| The poster field in `Movie.java` | `private String posterUrl;` | `private String poster = null;` |
| Field initializer | none | `= null` |
| Position of the no-argument constructor | **first**, before the one with parameters (line 18) | last, after the setters (line 127) |
| Does `toString()` include the poster? | **NO** | yes (`poster`) |
| `MainActivity.java` — unused imports | `java.math.BigDecimal` and `android.widget.Toast` | `java.util.Date` and `android.widget.Toast` |
| `MainActivity.java` — imports `java.util.Date`? | **no** | yes (unused) |
| `ItemActivity.java` — unused imports | `android.widget.Switch` | `Switch`, `Toast`, `Snackbar`, `ActivityItemBinding` |
| `ItemActivity.java` — imports `Toast`/`Snackbar`/`ActivityItemBinding`? | **no** | yes (all unused) |
| `activity_main.xml` | identical to G1097 | — |
| `activity_item.xml` | identical to G1097 | — |
| `AndroidManifest.xml` | identical to G1097 (only the theme differs: `Theme.G1096`) | `Theme.G1097` |
| `movie_item.xml` | **does not exist** | exists (prepared for S07, used by no code) |

### 29.0.1 The field name: `posterUrl` vs `poster`

G1096 declares `private String posterUrl;`. G1097 declares `private String poster = null;`. The difference is not merely lexical: it propagates into the **accessors**.

- G1096 has `getPosterUrl()` and `setPosterUrl(String)`.
- G1097 has `getPoster()` and `setPoster(String)`.

`ItemActivity` in G1096 calls `movie.setPosterUrl(etPoster.getText().toString())` in `saveMovie()` and `existing.getPosterUrl()` in `fillForm()`. If you paste code from chapter 22 into a G1096 project, the compiler stops with `cannot find symbol: method setPoster(java.lang.String)`. The error is not obvious to someone looking at the form — the field is called `etPoster`, but the model is called `posterUrl`.

**What you learn:** the name of a `private` field is not cosmetic. It becomes a public contract through the names of the accessors. When you rename the field, you must rename the accessors and update every place that calls them — here two, in `ItemActivity`.

**Semantic nuance:** `posterUrl` is more precise — it says the value is a link, not an image. `poster` is more general — it could be a local path, a file name or a `Drawable`. Both are correct. What matters is that they are consistent throughout the project.

### 29.0.2 The `= null` initializer

G1097 writes `private String poster = null;`. G1096 writes only `private String posterUrl;`. At runtime, **the behaviour is identical**: an object field is initialized to `null` by the JVM anyway, before any constructor runs.

So why does `= null` appear in G1097? It is **documentation**: the line says explicitly "this field may be missing; a movie without a poster is valid". A reader who sees `= null` does not wonder whether the missing value is a bug.

**What you learn:** in Java, `= null` on an instance field prevents nothing and changes nothing. There is no "safe initialization" through `= null`; there is only communicated intent. The opposite trap is real: writing `= null` on a `final` field, or initializing with `null` a variable you then use immediately, **hides** a `NullPointerException` instead of preventing it.

**The link to the empty constructor:** `new Movie()` leaves all ten fields at their default values (`null`, `0`, `0.0`, `false`). So `posterUrl` is `null` after `new Movie()`, whether or not the declaration says `= null`.

### 29.0.3 The position of the no-argument constructor

In G1096, `public Movie() { }` is **the first method in the class**, at line 18, immediately after the ten fields and before the constructor with parameters. In G1097, the same constructor is **the last method**, at line 127, after all twenty getters and setters.

For the compiler: **zero difference**. The order of methods in a class has no semantic meaning in Java. For the reader: G1096 shows you first "how an empty object is created", then "how a full object is created" — exactly the order in which they appear in the app: `saveMovie()` does `new Movie()` (empty, filled with setters), and `addSampleMovies()` does `new Movie(10 arguments)` (full, from an expression).

**What you learn:** position is a style decision, not a rule. IntelliJ generates constructors wherever you put them. What is **not** style is their existence: if you define any constructor with parameters, the compiler no longer generates the no-argument constructor automatically. `new Movie()` in `saveMovie()` would stop compiling. Both groups write it explicitly — just in different places.

**A formatting detail, visible in the source:** in G1096 the parameter list of the full constructor is broken over two lines (line 21 ends with `onWatchlist,`, line 22 begins with `String posterUrl)`), aligned under the first parameter. In G1097 it is on a single line. It changes nothing semantically; it only shows that the file went through another formatter or another window width.

### 29.0.4 `toString()` without the poster

The `toString()` in G1096 stops at `onWatchlist`. `posterUrl` **does not appear** in the returned text. In G1097, the last fragment is `", poster='" + poster + '\''`.

**The visible consequence:** in the list, the G1096 row does not display the poster URL. For a `ListView` row with `simple_list_item_1`, this is actually an advantage — the row is shorter and more readable.

**The hidden consequence, and this is the lesson:** `toString()` is written by hand. Adding a field to the class **does not** add it to `toString()` automatically. If you add a field and forget to put it in `toString()`, **nothing breaks**: the code compiles, the app runs, only the value is not visible anywhere. It is a silent bug, the opposite of a crash.

**What you learn:** `toString()` is a display contract, not a mirror of the class. You update it consciously, when you want to see the field. At the exam, if you are asked to "display all the attributes", count them on your fingers — ten fields, ten fragments.

**Nuance:** `Date` is not wrapped in apostrophes, because `Date.toString()` already produces a readable format (`Sat Jul 16 00:00:00 GMT+03:00 2010`). That format depends on the timezone and the locale, so it is not stable across devices.

### 29.0.5 The unused imports in `MainActivity.java`

G1096 imports `java.math.BigDecimal` and `android.widget.Toast`, both unused. G1097 imports `java.util.Date` and `android.widget.Toast`, both unused. The intersection is `Toast`; the difference is `BigDecimal` versus `Date`.

What each suggests about the file's history (plausible hypotheses, not facts from the source):

- **`BigDecimal`** — someone probably considered parsing the budget with exact decimal precision (`new BigDecimal(text)`), then gave up in favour of `Double.parseDouble` in `ItemActivity`. The import remained.
- **`Date`** (only in G1097) — someone probably worked with dates directly in `MainActivity`, then moved the logic into the model.
- **`Toast`** (in both) — probably a confirmation message on save, removed at some point. `Toast` is the import "that stays" in almost any Android project.

**An important, verifiable detail:** G1096 **does not** import `java.util.Date`, even though `Movie` has a `Date` field and `MainActivity` builds dates with `GregorianCalendar`. It does not need to: `new GregorianCalendar(...).getTime()` returns a `Date`, but the type is never **named** in the file. The import is needed only when you write the name of the type, not when you pass it along.

**What you learn:** an unused import does not break the build — `javac` gives no error, only `-Xlint:all` gives a warning. But it **lies about the dependencies**: whoever reads the file thinks `MainActivity` works with exact money or with dates, and it does neither.

### 29.0.6 The unused imports in `ItemActivity.java`

G1096 imports a single dead name: `android.widget.Switch`. G1097 imports four: `Switch`, `Toast`, `Snackbar` and `ActivityItemBinding`.

**Why `Switch` is dead in all four groups:** all of them declare `private MaterialSwitch swWatched;`, and `MaterialSwitch` is `com.google.android.material.materialswitch.MaterialSwitch`. No `Switch` name appears in the body of the file.

**And why it is good that it is dead:** `MaterialSwitch` extends `SwitchCompat`, which extends `CompoundButton`. It does **not** extend `android.widget.Switch`. If someone were to "fix" the import by using it — `private Switch swWatched;` — then `findViewById(R.id.swWatched)` would return a `MaterialSwitch` and the assignment would throw `ClassCastException` at runtime. The dead import is, in this case, a **defused** trap.

**`ActivityItemBinding`** (only in G1097) is the class generated by View Binding. If View Binding were enabled, you would write `ActivityItemBinding binding = ActivityItemBinding.inflate(getLayoutInflater());` and give up the 13 `findViewById` calls. G1096 does not do that — it uses classic `findViewById`, and the import does not exist at all.

**`Toast` and `Snackbar`** (only in G1097) are dead because `saveMovie()` shows no confirmation: it calls `setResult` and `finish()`, and the user sees the updated list. In G1096 the author never imported them.

**What you learn:** the number of dead imports does not measure the quality of the code, but it **tells a story** about what the author tried and abandoned. At the exam, if you are asked to identify the unused imports, the method is mechanical: for each import, look for the class name in the rest of the file.

### 29.0.7 `movie_item.xml` is missing

G1097 has a sixth file: `movie_item.xml`, a row layout with a card, a poster and state chips. G1096 does not have it at all.

**The functional difference is zero.** `MainActivity` in both groups uses `android.R.layout.simple_list_item_1`, not `R.layout.movie_item`. No line of code refers to the file. It exists in G1097 only as preparation for S07, where the list moves to `RecyclerView`.

**What you learn:** a resource file that no code refers to is dead weight. `R.layout.movie_item` appears in `R.java` only if the file exists, but nobody reads it. Deleting it does not change the app's behaviour — just a few hundred bytes in the APK.

**The link to the next lab:** in G1096, the move to `RecyclerView` requires creating `movie_item.xml` from scratch. In G1097, the file is already there and only needs to be wired up.

### 29.0.8 What stays identical — and why it matters

Three files are identical or nearly identical: `activity_main.xml`, `activity_item.xml` and `AndroidManifest.xml`. The last one differs only in the theme reference (`@style/Theme.G1096` versus `@style/Theme.G1097`).

This means that **everything you learn about layouts in chapter 22 applies here word for word**. The differences are in the Java code and in the model, not in the XML. If at the exam you are asked to explain an attribute in `activity_item.xml`, the answer is the same for both groups.

---

## 29.1 How to read this chapter

This is not a chapter of exercises. It is a chapter of **reading with a magnifying glass**: you take each file of the app and go through it line by line, with the explanation right above.

- **Read the code first, the comment second.** Cover the comment block with your hand, say what the line does, then check. If you read only the comment, you have the impression that you know; if you tried to predict the line, you really know.
- **The `THEORY BLOCK` blocks** appear before each class and each large XML section. They explain *why* the structure exists, not *how* it works. Read them first, then go into the code.
- **The blocks above the methods** have four fixed labels: `WHAT IT DOES`, `HOW`, `RISK`, `REF`. `REF` points to another place in the app or to another chapter where the same pattern appears.
- **The numbered steps** ("1. Validation", "2. Cleaning the old state", "3. Update") describe the order of execution. The order is part of the lesson: the same steps in another order produce another result.
- **The `RISK:`, `BUG:` and `DANGER!` markers** signal the places where the code works today but can break, or where it already breaks. They are the most valuable lines in the chapter — at the exam, exactly these are asked for.
- **The ASCII diagrams** show what is not visible in the code: the view tree, the object that travels between activities, the order in `onCreate`, the lifecycle.
- **Compare with chapter 22.** Every difference in 29.0 has an exact counterpart there. If you learn a single variant, you learn half the answer.
- **Do not memorize.** The goal is to be able to rebuild the file starting from a diagram. If you can draw the flow, the code comes by itself.

---

## 29.2 `Movie.java` — the data model

```java
/*
 * ======================================================================================
 * FILE: Movie.java — THE DATA MODEL OF THE APP
 * ======================================================================================
 * WHAT THIS FILE IS:
 *   A POJO class (Plain Old Java Object): 10 private fields, one no-argument
 *   constructor, one constructor with 10 parameters and 20 getters/setters.
 *   Zero business logic, zero references to Android.
 *
 * WHY IT EXISTS:
 *   It is the only type that crosses the boundary between the two activities.
 *   `MainActivity` holds `List<Movie>`; `ItemActivity` builds a `Movie` from the
 *   form and sends it back. The model is the binder between the two screens.
 *
 * WHAT IT DEPENDS ON:
 *   - `java.io.Serializable` — so the object can be put in an `Intent`.
 *   - `java.util.Date` — the type of the release date.
 *   Nothing from `android.*`. This is the property that makes it testable on the JVM.
 *
 * WHO DEPENDS ON IT:
 *   `MainActivity` (the list, the adapter, the extras), `ItemActivity` (`fillForm`,
 *   `saveMovie`), `ArrayAdapter` (through `toString()`).
 *
 * WHAT IT DOES NOT DO:
 *   - It validates nothing: it accepts an empty title, a negative budget, a null date.
 *   - It has no `id`: identity in the list is the POSITION.
 *   - It has no `equals()` / `hashCode()`: two movies with the same values are not
 *     "equal" for `List.remove()` or `List.contains()`.
 *   - It does not know what an `EditText`, a `Spinner` or an `Intent` is.
 *
 * WHAT BREAKS WITHOUT IT:
 *   `Intent.putExtra(MOVIE_EXTRA, movie)` would have no type; `ArrayAdapter` would
 *   have nothing to display; `ItemActivity` would have to send 10 separate extras, and
 *   `MainActivity` would recompose them by hand — 10 keys to keep in sync in two places.
 * ======================================================================================
 */

// The package = the path under `src/main/java`. Here `ro.ase.ie.g1096.model`.
// `model` is the subpackage that holds the data types; `activities` holds the screens.
// The separation is not cosmetic: `model` imports nothing from `activities`, so it
// can be tested and reused without Android.
package ro.ase.ie.g1096.model;

// ======================================================================================
// IMPORT 1: java.io.Serializable
// ======================================================================================
// WHAT IT IS: a MARKER interface — it has no method to implement.
// WHY HERE: `Intent.putExtra(String, Serializable)` is the simplest way to
//   send a whole object to another activity. Without `implements Serializable`,
//   the call `intent.putExtra(MOVIE_EXTRA, movie)` finds no matching overload
//   and DOES NOT COMPILE.
// WHAT HAPPENS AT RUNTIME: the JVM serializes the object graph into bytes, puts it
//   in the `Bundle`, and the receiving activity gets a deserialized COPY.
// RISK: with no `serialVersionUID` declared, the JVM computes one from the class structure.
//   If you add a field between writing and reading (different processes), you get
//   `InvalidClassException`. Here the writing and the reading happen in the SAME process,
//   a few milliseconds apart, so the risk is theoretical.
// ======================================================================================
import java.io.Serializable;

// ======================================================================================
// IMPORT 2: java.util.Date
// ======================================================================================
// WHAT IT IS: a moment in time, stored internally as a number of milliseconds since 1 January 1970.
// WHY HERE: the release date must be a DATE, not a text. As a `Date` you can
//   sort, compare and format with `SimpleDateFormat`.
// WHY NOT `String`: you would store "16/07/2010" and lose the ability to compute.
//   `fillForm` would have to parse on every display, and `saveMovie` would have to
//   format on every save — two places where you can get the format wrong.
// WHY NOT `java.time.LocalDate`: it is newer and cleaner, but `Date` is
//   `Serializable` out of the box and is the type used by the rest of the app.
// RISK: `Date` is MUTABLE. `getRelease()` returns the internal reference, not a copy,
//   so a careless caller can change the date in the object without going through the setter.
// ======================================================================================
import java.util.Date;

/*
 * ======================================================================================
 * THEORY BLOCK: WHY A SEPARATE MODEL (POJO) AND WHY `Serializable`
 * ======================================================================================
 *
 * 1. SINGLE RESPONSIBILITY
 *    The class has a single reason to change: the structure of a movie's data changes.
 *    It does not change when a layout, a button or a colour changes. If you put
 *    `getText().toString()` here, the class would depend on `android.widget.EditText` and
 *    would have two reasons to change.
 *
 * 2. SERIALIZABILITY
 *    `Intent.putExtra(String, Serializable)` is the simplest way to send a
 *    whole object to another activity. Without `implements Serializable`, the call
 *    `intent.putExtra(MOVIE_EXTRA, movie)` finds no matching overload and
 *    DOES NOT COMPILE. The interface has no methods: it only changes what the JVM can
 *    do with the object — turn it into bytes and back.
 *
 * 3. WHAT HAPPENS AT RUNTIME
 *    The JVM serializes the object graph into bytes, puts it in the `Bundle`, and the
 *    receiving activity gets a deserialized COPY. The original stays in the
 *    list in `MainActivity`.
 *
 *    [MainActivity]                      [Intent]                     [ItemActivity]
 *    movies.get(position)                                                  |
 *          |                                                               |
 *          +-- putExtra("movie", obj) --+                                  |
 *                                       |                                  |
 *                           serialize (JVM -> bytes)                      |
 *                                       |                                  |
 *                                       +-- Bundle -- startActivity --> --+
 *                                                                          |
 *                                                        getSerializableExtra(...)
 *                                                                          |
 *                                                           A COPY, not the original
 *
 *    The practical consequence: changing the copy is NOT visible in the list. That is why
 *    `MainActivity` does `movies.set(position, movie)` on return.
 *
 * 4. WHY NO `id` FIELD
 *    The identity of the movie in the list is the POSITION, not an ID. From this comes the whole
 *    `POSITION_EXTRA` mechanism in the other two files. It is a didactic simplification: a real
 *    database would have a stable `id`, and deleting a row would no longer move the
 *    identity of the others.
 *
 * 5. TESTABILITY
 *    In the file there is no `import android.*`. You can write a JVM test that creates
 *    a `Movie` and checks `getTitle()`. No emulator, no Android, no Robolectric.
 *
 * 6. THE NAMING CONVENTION FOR BOOLEANS
 *    `isWatched()` and `isOnWatchlist()`, not `getWatched()` and `getOnWatchlist()`.
 *    It is the JavaBeans convention: frameworks that read properties through reflection
 *    look for the `is` prefix for `boolean`. `fillForm` calls exactly these names.
 * ======================================================================================
 */

// `implements Serializable` = marker interface, with no method to implement.
// It only changes what the JVM can do with the object: turn it into bytes.
public class Movie implements Serializable {

    // ==================================================================================
    // FIELD 1: title
    // ==================================================================================
    // TYPE: String — free text, of arbitrary length.
    // SOURCE WIDGET: `etTitle` (TextInputEditText) -> `getText().toString()`.
    // WHY String: the title is text, it has no numeric or date operations.
    // WHAT BREAKS IF IT IS WRONG: if it were `int`, "Inception" would not fit;
    //   if it were `char[]`, `ArrayAdapter` would display the address of the array.
    // ==================================================================================
    private String title; //EditText

    // ==================================================================================
    // FIELD 2: release
    // ==================================================================================
    // TYPE: Date — a moment in time (here, only the day matters).
    // SOURCE WIDGET: `etRelease` + `DatePickerDialog`; in the model it arrives from
    //   `releaseCal.getTime()`, NOT from the text in the EditText.
    // WHY Date: it allows formatting with `SimpleDateFormat` and comparison.
    // WHAT BREAKS IF IT IS WRONG: if it were `String`, `fillForm` would have to parse
    //   on every display, and a mistyped text would reach the model as it is.
    // ==================================================================================
    private Date release; //EditText date

    // ==================================================================================
    // FIELD 3: genre
    // ==================================================================================
    // TYPE: String — the text selected from the list ("Sci-Fi", "Animation", "Action").
    // SOURCE WIDGET: `spGenre` (Spinner) -> `getSelectedItem().toString()`.
    // WHY String and not `enum`: the genres come from `@array/movie_genre`, that is, from XML.
    //   With an `enum`, adding a genre would require changing the Java code.
    // WHAT BREAKS IF IT IS WRONG: if you stored the position (`int`), changing the order
    //   in the resource list `@array/movie_genre` would retroactively change the genre
    //   of all saved movies.
    // ==================================================================================
    private String genre; //Spinner

    // ==================================================================================
    // FIELD 4: budget
    // ==================================================================================
    // TYPE: double — a number with decimals, precision of ~15–16 significant digits.
    // SOURCE WIDGET: `etBudget` (inputType=numberDecimal) -> `Double.parseDouble(...)`.
    // WHY double and not float: `float` has ~7 significant digits. For 160 000 000
    //   both are exact, but 160 000 001 would not be exactly representable in `float`.
    //   In addition, `Double.parseDouble` returns `double` — a `float` field would require a cast.
    // WHAT BREAKS IF IT IS WRONG: if it were `int`, the decimals would be truncated;
    //   if it were `String`, you could not compare budgets.
    // ==================================================================================
    private double budget; //EditText number

    // ==================================================================================
    // FIELD 5: duration
    // ==================================================================================
    // TYPE: int — a whole number of minutes, 0..300.
    // SOURCE WIDGET: `sbDuration` (SeekBar) -> `getProgress()`.
    // WHY int: `SeekBar.getProgress()` returns `int`. Any other type would require a cast.
    // WHAT BREAKS IF IT IS WRONG: if it were `String`, `setProgress` would require parsing
    //   and you could save "abc" as a duration.
    // ==================================================================================
    private int duration; //SeekBar

    // ==================================================================================
    // FIELD 6: rating
    // ==================================================================================
    // TYPE: float — the rating in half stars (0.0, 0.5, ..., 5.0).
    // SOURCE WIDGET: `rbRating` (RatingBar) -> `getRating()`.
    // WHY float: `RatingBar.getRating()` and `setRating(float)` work with `float`.
    //   A `double` field would make `setRating(existing.getRating())` NOT compile
    //   without an explicit cast.
    // WHAT BREAKS IF IT IS WRONG: if it were `int`, you would lose the half stars;
    //   if it were `String` ("4.5"), the comparisons would be lexicographic.
    // ==================================================================================
    private float rating; //RatingBar

    // ==================================================================================
    // FIELD 7: watched
    // ==================================================================================
    // TYPE: boolean — true/false.
    // SOURCE WIDGET: `swWatched` (MaterialSwitch) -> `isChecked()`.
    // WHY boolean: the state of a switch is binary. `isChecked()` returns exactly that.
    // WHAT BREAKS IF IT IS WRONG: if it were `String` ("Yes"/"No"), every `if` would require
    //   a text comparison, and a lowercase "yes" would be treated as false.
    // WATCH THE LABEL: in `activity_item.xml`, the switch is labelled
    //   "Recommended", not "Watched". The field says `watched`, the screen says something else.
    // ==================================================================================
    private boolean watched; //Switch

    // ==================================================================================
    // FIELD 8: approval
    // ==================================================================================
    // TYPE: String — the TEXT of the selected radio button ("G", "PG", "PG-13", "R", "NC-17").
    // SOURCE WIDGET: `rgApproval` (RadioGroup) -> a loop over the children + `getText()`.
    // WHY text and not the resource ID: the text survives reordering the buttons
    //   in XML. The ID is a value generated in `R.java`, stable only as long as
    //   you do not rename the button.
    // RISK: if you change the label in XML ("PG13" instead of "PG-13"), `fillForm`
    //   no longer finds the match and checks nothing — silently, with no error.
    // WHAT BREAKS IF IT IS WRONG: if you stored the index (0..4), adding a button
    //   at the start of the group would change the meaning of all saved values.
    // ==================================================================================
    private String approval; //RadioGroup | RadioButtons

    // ==================================================================================
    // FIELD 9: onWatchlist
    // ==================================================================================
    // TYPE: boolean — true/false.
    // SOURCE WIDGET: `cbonWatchList` (MaterialCheckBox) -> `isChecked()`.
    // WHY boolean: a checkbox is binary. Independent of `watched`: you can have seen
    //   the movie AND keep it on the rewatch list.
    // WHAT BREAKS IF IT IS WRONG: if you reused `watched` for both, the two
    //   controls would contradict each other on save — the last one read would win.
    // ==================================================================================
    private boolean onWatchlist; //Checkbox

    // ==================================================================================
    // FIELD 10: posterUrl — THE ONLY NAME DIFFERENCE FROM G1097
    // ==================================================================================
    // TYPE: String — a URL (or any text) pointing to the movie poster.
    // SOURCE WIDGET: `etPoster` (inputType=textUri) -> `getText().toString()`.
    // WHY `posterUrl` and not `poster`: the name says the value is a LINK, not a
    //   loaded image. In G1097 the field is called `poster` and has an explicit `= null`.
    // WHY NO `= null`: in Java an object field is `null` implicitly anyway. G1096
    //   does not write the initializer; the behaviour is identical, only the documentation differs.
    // RISK: `null` reaches `etPoster.setText(null)` on edit — legal, but it displays
    //   an empty field. If you called `.length()` on it, you would get `NullPointerException`.
    // NOTE: the app NEVER loads the image. There is no `ImageView`,
    //   no network library, no `INTERNET` permission in the manifest.
    //   The URL is stored as text and that is all.
    // ==================================================================================
    private String posterUrl;

    // ==================================================================================
    // THE NO-ARGUMENT CONSTRUCTOR — THE FIRST IN THE CLASS IN G1096
    // ==================================================================================
    // WHY IT MUST BE WRITTEN EXPLICITLY:
    //   The Java rule: if you define ANY constructor with parameters, the compiler
    //   no longer generates the no-argument constructor automatically.
    //   `saveMovie()` in ItemActivity does `Movie movie = new Movie();`.
    //   Without this constructor, the file DOES NOT COMPILE.
    //
    // WHY THE BODY IS EMPTY: all the fields get their default values
    //   (null / 0 / 0.0 / false). The object is filled immediately with setters.
    //
    // WHY IT IS FIRST HERE: the position does not matter to the compiler. In G1096 it sits
    //   immediately after the fields, so the reader sees first "the empty object", then
    //   "the full object". In G1097 the same constructor is the LAST method of the file.
    //   Both variants are correct; it is a style decision, not a rule.
    // ==================================================================================
    public Movie() {
    }

    // ==================================================================================
    // THE 10-PARAMETER CONSTRUCTOR
    // ==================================================================================
    // WHY IT EXISTS: `addSampleMovies()` in MainActivity creates the 3 demo movies
    //   in a single expression. Without it, there would be 10 setter calls per movie.
    //
    // THE TRAP: the order of the parameters is POSITIONAL. The names in the signature do not help
    //   at the call — the compiler looks only at types and position.
    //
    //   POSITION  TYPE      NAME           WIDGET THAT PRODUCES THE VALUE
    //   ---------------------------------------------------------------------------
    //      1      String    title          TextInputEditText etTitle
    //      2      Date      release        etRelease + DatePickerDialog
    //      3      String    genre          Spinner spGenre
    //      4      double    budget         etBudget (numberDecimal)
    //      5      int       duration       SeekBar sbDuration
    //      6      float     rating         RatingBar rbRating
    //      7      boolean   watched        MaterialSwitch swWatched
    //      8      String    approval       RadioGroup rgApproval
    //      9      boolean   onWatchlist    MaterialCheckBox cbOnWatchList
    //     10      String    posterUrl      etPoster (textUri)
    //
    //   If you swap positions 1 and 3 (both String) or 7 and 9 (both boolean),
    //   the code COMPILES. The movie is created. Only that `title` gets the genre and
    //   `genre` gets the title. The compiler cannot help you here.
    //
    // FORMATTING: in G1096 the parameter list is broken over two lines, the second aligned
    //   under the first parameter. In G1097 it is on a single line. Semantically: identical.
    // ==================================================================================
    public Movie(String title, Date release, String genre, double budget, int duration, float rating, boolean watched, String approval, boolean onWatchlist,
                 String posterUrl) {

        // `this.title` = the field of the class; `title` = the parameter.
        // Without `this.`, the line would be `title = title` — self-assignment, the field stays null.
        this.title = title;

        // The same pattern for each of the 10 fields. All 10 lines
        // are structurally identical; if one is missing, the field keeps its default
        // value (null / 0 / 0.0 / false) and the bug appears only on display.
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

    // ==================================================================================
    // toString() — THE DISPLAY CONTRACT IN THE LIST
    // ==================================================================================
    // WHY IT IS MANDATORY HERE:
    //   `ArrayAdapter` with `android.R.layout.simple_list_item_1` receives a `TextView`
    //   and fills it with `item.toString()`. Without the override, `Object.toString()` would
    //   return `ro.ase.ie.g1096.model.Movie@a1b2c3d` — the memory address.
    //
    // THE EXACT FLOW:
    //   ListView.getView(position) -> ArrayAdapter.getView(...) -> TextView.setText(
    //   movies.get(position).toString())
    //
    // WHY `@Override`: the compiler checks the signature. If you write `tostring()`
    //   with a lowercase letter, without the annotation you get no error — only your method
    //   is never called.
    //
    // THE DIFFERENCE FROM G1097: here `posterUrl` does NOT appear in the returned text.
    //   G1097 ends with `", poster='" + poster + '\''`. Here it ends with
    //   `onWatchlist`. Adding a field to the class does not add it here automatically.
    //
    // THE FORMAT: generated by IntelliJ with Alt+Insert -> toString(). `'\''` is an
    //   escaped apostrophe, so that it does not close the character literal.
    //
    // WHAT YOU SEE ON SCREEN: nine fields, on a single row. Ugly, but correct.
    //   It is fixed in the next lab with RecyclerView and a row layout.
    // ==================================================================================
    @Override
    public String toString() {

        // String concatenation with `+`. Each `+` creates a new object in memory.
        // For 9 fields, the difference is negligible; for large loops you would use
        // `StringBuilder`.
        return "Movie{" +

                // The text fields are wrapped in apostrophes, so that the boundaries of the
                // value are visible: `title='Inception'`. Without them, `title=''` and `genre=''`
                // would be indistinguishable from an empty field.
                "title='" + title + '\'' +

                // `Date` is not wrapped in apostrophes: its `toString()` already produces
                // a readable format (`Sat Jul 16 00:00:00 GMT+03:00 2010`).
                ", release=" + release +

                // The comma at the beginning, not at the end: the last field does not need
                // a separator, and `}` joins correctly.
                ", genre='" + genre + '\'' +
                ", budget=" + budget +
                ", duration=" + duration +
                ", rating=" + rating +
                ", watched=" + watched +
                ", approval='" + approval + '\'' +

                // THE LAST FIELD IN THE TEXT — and the last in the class that appears here.
                // `posterUrl` is missing. See difference 29.0.4.
                ", onWatchlist=" + onWatchlist +

                // The closing brace of the object, as text.
                '}';
    }

    // ==================================================================================
    // GETTERS AND SETTERS — 20 METHODS, ALL MECHANICAL
    // ==================================================================================
    // WHY THEY EXIST: the fields are `private`. Code from other packages (and even from
    //   `activities`) cannot read or write them directly. The getters and setters
    //   are the only interface.
    //
    // WHY SO MANY: 10 fields x 2 = 20. They are generated automatically by IntelliJ
    //   (Alt+Insert -> Getter and Setter). You do not write them by hand at the exam.
    //
    // THE NAMING CONVENTION:
    //   - `getX()` for objects and primitives, EXCEPT for boolean;
    //   - `isX()` for boolean — the JavaBeans convention.
    //
    // THE ORDER: the fields appear in the same order as the declarations, except for
    //   `watched`, which skips over `approval` and `onWatchlist` — its getter comes
    //   immediately after `rating`, then `approval`, then `onWatchlist`, then `posterUrl`.
    // ==================================================================================

    // GETTER: returns the reference to the String. String is immutable, so there is no
    // risk of modification from outside.
    public String getTitle() {
        return title;
    }

    // SETTER: `this.title` = the field, `title` = the parameter. The same trap as in
    // the 10-parameter constructor.
    public void setTitle(String title) {
        this.title = title;
    }

    // GETTER for Date. WATCH OUT: it returns the REFERENCE, not a copy.
    // RISK: `movie.getRelease().setTime(0)` would change the date in the object without the setter.
    //   A correct variant would be `return new Date(release.getTime());`.
    public Date getRelease() {
        return release;
    }

    // SETTER for Date. It does not validate `null` — a `Movie` with a null date is accepted
    // by the model and crashes only in `fillForm`, at `dateFormat.format(null)`.
    public void setRelease(Date release) {
        this.release = release;
    }

    // GETTER for the genre. The value comes from the Spinner, but the model does not know that.
    public String getGenre() {
        return genre;
    }

    // SETTER for the genre. It does not check whether the value exists in `@array/movie_genre`.
    // Validation is the responsibility of the UI, not of the model.
    public void setGenre(String genre) {
        this.genre = genre;
    }

    // GETTER for the budget. `double` is copied by value — there are no aliasing
    // problems as with Date.
    public double getBudget() {
        return budget;
    }

    // SETTER for the budget. It does not reject negative values: a budget of -5 would be accepted.
    // Validation should be done in `saveMovie`, before the call.
    public void setBudget(double budget) {
        this.budget = budget;
    }

    // GETTER for the duration, in minutes.
    public int getDuration() {
        return duration;
    }

    // SETTER for the duration. It does not limit to 0..300 — the limit exists only in XML
    // (`android:max="300"`), that is, only in the UI.
    public void setDuration(int duration) {
        this.duration = duration;
    }

    // GETTER for the rating. `float` — the rating in half stars.
    public float getRating() {
        return rating;
    }

    // SETTER for the rating. The parameter is `float`, exactly the type required by
    // `RatingBar.setRating(float)`.
    public void setRating(float rating) {
        this.rating = rating;
    }

    // ==================================================================================
    // WHY `isWatched()` AND NOT `getWatched()`
    // ==================================================================================
    // 1. THE JAVABEANS CONVENTION: for `boolean`, the getter is called `isX()`, not `getX()`.
    //    Reflection (and the frameworks that read properties) looks for the `is` prefix.
    // 2. CONSISTENCY: `isOnWatchlist()` follows the same rule. If one were
    //    `getWatched()` and the other `isOnWatchlist()`, the code would be hard to read.
    // 3. THE CODE DEPENDS ON THE NAME: `fillForm` calls `existing.isWatched()`. If you
    //    wrote `getWatched()`, the call would not compile — and it must be changed in two places.
    // ==================================================================================
    public boolean isWatched() {
        return watched;
    }

    // The setter stays `setWatched` — the `set` prefix is the same for all types.
    public void setWatched(boolean watched) {
        this.watched = watched;
    }

    // GETTER for the parental guidance ("PG-13" etc.).
    public String getApproval() {
        return approval;
    }

    // SETTER for the guidance. The value is the text of the radio button, not its ID.
    public void setApproval(String approval) {
        this.approval = approval;
    }

    // GETTER for the "Watchlist" checkbox. Prefix `is` — again the JavaBeans convention.
    public boolean isOnWatchlist() {
        return onWatchlist;
    }

    // SETTER for the checkbox.
    public void setOnWatchlist(boolean onWatchlist) {
        this.onWatchlist = onWatchlist;
    }

    // ==================================================================================
    // GETTER AND SETTER FOR THE POSTER — THE NAME THAT GIVES THE GROUP AWAY
    // ==================================================================================
    // Here difference 29.0.1 is visible in its most concrete form: the methods are called
    // `getPosterUrl` / `setPosterUrl`, not `getPoster` / `setPoster`.
    // `ItemActivity` in G1096 calls these two. Copying the code from
    // chapter 22 (written for G1097) produces `cannot find symbol`.
    // ==================================================================================
    public String getPosterUrl() {
        return posterUrl;
    }

    // SETTER for the poster. It accepts `null` without complaining.
    public void setPosterUrl(String posterUrl) {
        this.posterUrl = posterUrl;
    }

    // The closing brace of the class. After it there is nothing else in the file:
    // no inner class, no `enum`, no constant.
}
```

---

## 29.3 `MainActivity.java` — the list and the navigation

```java
/*
 * ======================================================================================
 * FILE: MainActivity.java — THE SCREEN WITH THE LIST
 * ======================================================================================
 * WHAT IT IS: the start activity. It holds the list of movies, displays it with an
 *   `ArrayAdapter` in a `ListView` and starts `ItemActivity` for insert or edit.
 *
 * WHY IT EXISTS: it is the only place that owns the app's STATE (the `movies` list).
 *   `ItemActivity` is just a form that produces a `Movie` and sends it back.
 *   Without `MainActivity`, the saved result would have nowhere to return to.
 *
 * WHAT IT DEPENDS ON:
 *   - `activity_main.xml` — for `R.id.main`, `R.id.listView`, `R.id.floatingActionButton`.
 *   - `ItemActivity` — the class it starts through an `Intent`.
 *   - `Movie` — the type of the elements in the list.
 *   - `androidx.activity.result.*` — for `registerForActivityResult`.
 *
 * WHO DEPENDS ON IT:
 *   `AndroidManifest.xml` declares it as the LAUNCHER. `ItemActivity` reads its
 *   constants `MOVIE_EXTRA` and `POSITION_EXTRA`.
 *
 * WHAT IT DOES NOT DO:
 *   - It validates nothing: it accepts any `Movie` returned by the form.
 *   - It does not persist the list: on rotation or process death, the list is lost.
 *   - It has no row layout of its own: it uses `android.R.layout.simple_list_item_1`.
 *   - It does not load posters: the URL stays text in the model.
 *
 * WHAT BREAKS WITHOUT IT:
 *   The app would start directly in a form with no list. `MOVIE_EXTRA` and
 *   `POSITION_EXTRA` would not exist, so `ItemActivity` would not compile.
 * ======================================================================================
 */

// The `activities` package — the screens. Separate from `model`, so that it does not mix
// the data types with the UI ones.
package ro.ase.ie.g1096.activities;

// ======================================================================================
// IMPORTS — GROUPED BY SOURCE
// ======================================================================================
// android.*        — framework classes (Intent, Bundle, View, widgets)
// androidx.*       — Jetpack libraries (AppCompat, EdgeToEdge, insets, activity result)
// com.google.*     — Material Components (FloatingActionButton)
// java.util.*      — collections and dates
// ro.ase.ie.g1096  — the model and the generated R class
//
// IN G1096, TWO IMPORTS ARE DEAD: `java.math.BigDecimal` and
// `android.widget.Toast`. In G1097 the dead ones are `java.util.Date` and `Toast`.
// See difference 29.0.5.
// ======================================================================================

// Intent: the object that describes "which activity you start" and what data it carries.
import android.content.Intent;

// Bundle: the state bag saved by the system (used here only in the signature of onCreate).
import android.os.Bundle;

// View: the base class for any UI element. It appears in the listeners' signatures.
import android.view.View;

// AdapterView: the base class for ListView/Spinner. Here only for OnItemClickListener.
import android.widget.AdapterView;

// ArrayAdapter: the bridge between `List<Movie>` and the rows in the ListView.
import android.widget.ArrayAdapter;

// ListView: the widget that displays the scrollable list.
import android.widget.ListView;

// Toast: short messages. Imported in the source, but UNUSED in this file.
// It is part of difference 29.0.5 — it appears dead in both groups.
import android.widget.Toast;

// EdgeToEdge: enables drawing under the system bars (status + navigation).
import androidx.activity.EdgeToEdge;

// ActivityResult: the result returned by the secondary activity (code + Intent).
import androidx.activity.result.ActivityResult;

// ActivityResultCallback: the single-method interface, called on return.
import androidx.activity.result.ActivityResultCallback;

// ActivityResultLauncher: the object that starts the activity and keeps the link to the callback.
import androidx.activity.result.ActivityResultLauncher;

// ActivityResultContracts: the predefined contracts (here, StartActivityForResult).
import androidx.activity.result.contract.ActivityResultContracts;

// AppCompatActivity: the base activity with support for Material themes and ActionBar.
import androidx.appcompat.app.AppCompatActivity;

// Insets: the pixel values of the bars that cover the content.
import androidx.core.graphics.Insets;

// ViewCompat: the compatible version of the View APIs (insets on any API).
import androidx.core.view.ViewCompat;

// WindowInsetsCompat: the description of the insets, independent of the Android version.
import androidx.core.view.WindowInsetsCompat;

// FloatingActionButton: the round button in the bottom-right corner.
import com.google.android.material.floatingactionbutton.FloatingActionButton;

// BigDecimal: decimal numbers with EXACT precision. Imported in the source, but UNUSED.
// THE DIFFERENCE FROM G1097: there this import does not exist; instead there is `java.util.Date`,
//   also unused. Here `Date` is not even imported — and it is not needed, because
//   the name `Date` never appears in the file; `getTime()` is passed straight on.
import java.math.BigDecimal;

// ArrayList: the concrete implementation of the list.
import java.util.ArrayList;

// Calendar: the date fields (YEAR, MONTH, DAY_OF_MONTH) and the month constants.
import java.util.Calendar;

// GregorianCalendar: the quick "year, month, day" constructor used in the demo data.
import java.util.GregorianCalendar;

// List: the list interface. The field is declared `List`, not `ArrayList`.
import java.util.List;

// The R class, generated at build time from all the files in `res/`. Without it, `R.id.listView`
// would not exist as a symbol.
import ro.ase.ie.g1096.R;

// The data model — the only dependency towards `model`.
import ro.ase.ie.g1096.model.Movie;

/*
 * ======================================================================================
 * THEORY BLOCK: WHO OWNS THE STATE AND WHO DISPLAYS IT
 * ======================================================================================
 *
 * 1. A SINGLE OWNER OF THE LIST
 *    `movies` is an instance field in `MainActivity`. `ItemActivity` has no
 *    reference to it. The form produces a `Movie` and sends it back through
 *    `setResult`; only `MainActivity` decides what to do with it (`add` or `set`).
 *    This is the separation that makes the flow easy to follow.
 *
 * 2. `final` DOES NOT MEAN IMMUTABLE
 *    `private final List<Movie> movies = new ArrayList<>();`
 *    `final` blocks REASSIGNING the reference (`movies = new ArrayList<>()` does not
 *    compile), but does NOT block changing the contents. `movies.add(...)` and
 *    `movies.set(...)` are perfectly legal. It is exactly what we want: the same list,
 *    always, with contents that change.
 *
 * 3. THE ADAPTER HOLDS THE REFERENCE, NOT A COPY
 *    `new ArrayAdapter<>(this, ..., movies)` receives the list by reference. That is why
 *    `movies.add(movie)` is visible to the adapter — but only after
 *    `notifyDataSetChanged()`. ListView does not observe the list by itself.
 *
 * 4. TWO MODES, A SINGLE FORM
 *    - FAB  -> `Intent` WITHOUT extras -> `ItemActivity` in INSERT mode.
 *    - Row  -> `Intent` WITH `MOVIE_EXTRA` and `POSITION_EXTRA` -> EDIT mode.
 *    `ItemActivity` decides the mode by `existing != null`, not by a separate flag.
 *
 * 5. THE LIFECYCLE OF THE LIST
 *    The list lives as long as the activity. On rotation, Android destroys and recreates
 *    the activity, and `movies` is reinitialized with the 3 demo movies. There is no
 *    `onSaveInstanceState`, so the added movies are lost. See RISK below.
 * ======================================================================================
 */

// `extends AppCompatActivity` — the AndroidX base activity. It provides `setContentView`,
// `findViewById`, `getIntent`, `setResult`, `finish`, `RESULT_OK`.
public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // THE PROTOCOL CONSTANTS BETWEEN THE TWO ACTIVITIES
    // ==================================================================================
    // `protected static final` = class constant, visible in subclasses and in the package.
    // `ItemActivity` is in the SAME package (`ro.ase.ie.g1096.activities`), so it would
    // work even without `protected`. It is declared this way out of habit.
    //
    // WATCH OUT — A FINE TRAP: a `static final String` with a literal value is a
    // COMPILE-TIME CONSTANT. The compiler INLINES it into every class that uses it.
    // If you change "movie" to "film" and recompile only MainActivity,
    // the previously compiled ItemActivity keeps "movie" in its bytecode. It is solved with
    // a clean build. It is not asked at the exam, but it explains why public constants
    // change rarely.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";

    // The round "+" button. The type is the Material class, not `ImageButton`.
    private FloatingActionButton fabInsert;

    // The scrolling list. It fills the whole screen; the FAB floats over it.
    private ListView listView;

    // The result launcher. It is NOT initialized here — it gets a value in `onCreate`,
    // AFTER `initListeners()`. See the explanation at `initListeners`.
    private ActivityResultLauncher<Intent> launcher;

    // The list of movies — the only state of the app.
    // `final` = the reference never changes; the contents do.
    // `new ArrayList<>()` = the diamond operator; the type is inferred from the declaration.
    private final List<Movie> movies = new ArrayList<>();

    // The adapter that binds the list to the ListView. The generic type is `Movie`, so
    // `getItem(position)` returns `Movie`, not `Object`.
    private ArrayAdapter<Movie> movieAdapter;

    // ==================================================================================
    // onCreate — THE ORDER MATTERS
    // ==================================================================================
    // WHAT IT DOES: builds the screen, populates the demo list, creates the adapter, binds
    //   the controls to the code, attaches the listeners and registers the launcher.
    // HOW: 1. super 2. EdgeToEdge 3. setContentView 4. insets 5. demo data
    //   6. adapter 7. findViewById 8. listeners 9. launcher.
    // RISK: each step depends on the previous one. `findViewById` before
    //   `setContentView` returns null; `setAdapter` before `new ArrayAdapter`
    //   would give a NullPointerException.
    // REF: exactly the same order in G1097 (chapter 22, section 22.2).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. Starts the initialization chain of the base class. MANDATORY first.
        //    Without it, `AppCompat` does not install its delegate and the theme is not applied.
        super.onCreate(savedInstanceState);

        // 2. Enables edge-to-edge drawing: the content goes under the status bar and
        //    under the navigation bar. The consequence: we must handle the padding ourselves,
        //    otherwise the first row of text sits under the clock.
        EdgeToEdge.enable(this);

        // 3. Inflates the view tree from `activity_main.xml`. From this moment
        //    `findViewById` can find something. Before this call, it returns null.
        setContentView(R.layout.activity_main);

        // 4. Fixes the padding for the system bars.
        //    `findViewById(R.id.main)` = the root FrameLayout from the XML.
        //    The lambda is `View.OnApplyWindowInsetsListener` (a functional interface).
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. Extracts the dimensions of the system bars: status bar + navigation bar.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Applies them as padding on the root container. The children squeeze
            //     into it automatically; we do not have to touch each one.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. Returns `insets` UNconsumed, so that it also reaches the children.
            //     If you returned `WindowInsetsCompat.CONSUMED`, nobody else
            //     would receive the information anymore.
            return insets;
        });

        // 5. Puts the 3 demo movies in the list. This is done BEFORE creating the adapter,
        //    so that the adapter counts 3 elements from the start. If you did it after,
        //    it would work the same (the adapter holds the reference), but you would need
        //    `notifyDataSetChanged()` to redraw.
        addSampleMovies();

        // 6. Creates the adapter.
        //    `this` = Context (the activity).
        //    `android.R.layout.simple_list_item_1` = the row layout from the FRAMEWORK,
        //      not from the app. It contains a single TextView with the id `android.R.id.text1`.
        //      That is why the row displays the model's `toString()`.
        //    `movies` = the data source, by reference.
        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

        // 7. Binds the Java fields to the views from the XML.
        initControls();

        // 8. Attaches the listeners. Here `launcher` is still `null`, but it is OK:
        //    the listeners read the field only on CLICK, and by then step 9 has set it.
        initListeners();

        // 9. Registers the result contract. It MUST be called before
        //    the activity reaches the STARTED state, so `onCreate` is the right
        //    place. It returns an `ActivityResultLauncher<Intent>`.
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // The callback: an anonymous class that implements the single-method interface.
                // It runs on the main thread, after the secondary activity
                // has closed and this one has come back to the foreground.
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // FILTER 1: did it return something useful? `RESULT_OK` is -1.
                        // If the user pressed Back, the code is RESULT_CANCELED (0)
                        // and we do nothing — the list stays untouched.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // `getData()` = the Intent built by ItemActivity in `saveMovie()`.
                            // It can theoretically be null; here RESULT_OK guarantees it is not.
                            Intent intent = o.getData();

                            // Extracts the serialized object. WATCH OUT: it is A COPY.
                            // `getSerializableExtra(String)` is DEPRECATED since API 33;
                            // the modern variant is `IntentCompat.getSerializableExtra(...)`,
                            // already used in ItemActivity. Here the old variant remained —
                            // a real inconsistency between the two files.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // The second piece of information from the Intent: the position. Default -1 = "does not exist".
                            // -1 is the app's convention for "insert mode".
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // BRANCH 1: the position is missing -> NEW movie.
                            if(position == -1)
                            {
                                // Adds at the end of the list.
                                movies.add(movie);

                                // Notifies the adapter. Without this call, ListView does not know
                                // that the list has one more element and does not redraw.
                                movieAdapter.notifyDataSetChanged();
                            }
                            // BRANCH 2: the position exists -> REPLACEMENT, not addition.
                            else
                            {
                                // `set` overwrites the element at the given position.
                                // If you used `add`, you would have a duplicate.
                                movies.set(position, movie);
                                movieAdapter.notifyDataSetChanged();
                            }
                        }
                    }
                });
    }

    // ==================================================================================
    // initListeners — WHAT HAPPENS ON TAP
    // ==================================================================================
    // WHAT IT DOES: attaches two behaviours — the FAB starts the empty form, a click
    //   on a row starts the filled form.
    // HOW: 1. `fabInsert.setOnClickListener` 2. `listView.setOnItemClickListener`.
    // RISK: `launcher` is still null when this method runs. It is safe because
    //   the listeners run only after `onCreate`, when `launcher` has a value.
    // REF: the same anonymous-class pattern as in `ItemActivity.initListeners()`.
    // ==================================================================================
    private void initListeners() {

        // An anonymous class that implements `View.OnClickListener`.
        // `new View.OnClickListener() { ... }` = "an object that only knows how to react
        // to a click". It has no name, it is not reused.
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // `MainActivity.this` = the activity's Context.
                // `this` alone would be the listener (the anonymous class), not an activity —
                // and the constructor `Intent(Context, Class)` would receive the wrong type.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // NO extras! The absence of `MOVIE_EXTRA` is exactly the signal
                // that `ItemActivity` reads as "insert mode".
                launcher.launch(intent);
            }
        });

        // Listener for a click on a row. The interface has 4 parameters:
        //   parent   = the ListView
        //   view     = the pressed row (a TextView, here)
        //   position = the index in the list (0-based)
        //   id       = the id of the row; for ArrayAdapter it equals position
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                // The same target as the FAB — but this time we also carry data.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // The object on the pressed row. It is serialized automatically on `launch`.
                // `movies.get(position)` returns the REFERENCE from the list; `putExtra`
                // serializes it into a copy. The original stays untouched.
                intent.putExtra(MOVIE_EXTRA, movies.get(position));

                // The position, so that `ItemActivity` knows which row to replace on save.
                intent.putExtra(POSITION_EXTRA, position);

                // Starts the activity through the launcher, not through `startActivity`.
                // The difference: the launcher guarantees that the result reaches the callback.
                launcher.launch(intent);
            }
        });
    }

    // ==================================================================================
    // initControls — FINDVIEWBYID, PURE AND SIMPLE
    // ==================================================================================
    // WHAT IT DOES: binds the two views to the Java fields and installs the adapter.
    // HOW: 1. FAB 2. ListView 3. setAdapter.
    // RISK: `findViewById` returns null if the ID does not exist in the current layout.
    //   Here all three IDs exist in `activity_main.xml`.
    // REF: in `ItemActivity`, the same method has 13 lines, not 3.
    // ==================================================================================
    private void initControls() {

        // The ID in the XML is `@+id/floatingActionButton`; the field is called `fabInsert`.
        // The names differ, the ID matters.
        fabInsert = findViewById(R.id.floatingActionButton);

        // The ID in the XML is `@+id/listView`.
        listView = findViewById(R.id.listView);

        // Installs the adapter. From this moment the ListView has something to draw.
        // `android:entries="@array/items"` from the XML is IGNORED from now on.
        listView.setAdapter(movieAdapter);
    }

    // ==================================================================================
    // addSampleMovies — THE DEMO DATA
    // ==================================================================================
    // WHAT IT DOES: adds 3 movies to the list, so that the screen does not start empty.
    // HOW: 3 calls of the 10-parameter constructor, each with a `new GregorianCalendar`.
    // RISK: the order of the arguments is POSITIONAL. Swapping two arguments of the
    //   same type (String/String or boolean/boolean) compiles and produces wrong data.
    // REF: the constructor is documented in 29.2; here you see its ONLY consumer.
    // ==================================================================================
    private void addSampleMovies() {

        // MOVIE 1 — "Inception".
        // `new Movie(` opens the call; each argument is on its own line, so that the
        // position is visible. The order is the one from the signature: title, release, genre, budget,
        // duration, rating, watched, approval, onWatchlist, posterUrl.
        movies.add(new Movie(
                "Inception",                                              // 1. title
                // 2. release: `GregorianCalendar(year, month, day)` — THE MONTH IS 0-BASED!
                //    `Calendar.JULY` = 6, not 7. If you wrote `new GregorianCalendar(2010, 7, 16)`
                //    you would get 16 AUGUST. `getTime()` turns the Calendar into a Date.
                new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),
                "Sci-Fi",                                                 // 3. genre
                160000000,                                                // 4. budget (int -> double)
                148,                                                      // 5. duration (minutes)
                4.5f,                                                     // 6. rating (float!)
                true,                                                     // 7. watched
                "PG-13",                                                  // 8. approval
                false,                                                    // 9. onWatchlist
                "https://example.com/posters/inception.jpg"));            // 10. posterUrl

        // MOVIE 2 — "Toy Story".
        // The same structure. `4f` is a `float` literal; without the `f` it would be `double`
        // and the constructor would not find a match for the `float rating` parameter.
        movies.add(new Movie(
                "Toy Story",
                new GregorianCalendar(1995, Calendar.NOVEMBER, 22).getTime(),
                "Animation",
                30000000,
                81,
                4f,
                true,
                "G",
                false,
                "https://example.com/posters/toy-story.jpg"));

        // MOVIE 3 — "The Matrix".
        // The only one with `watched = false` and `onWatchlist = true`: the two booleans
        // are independent, and this movie demonstrates exactly that.
        movies.add(new Movie(
                "The Matrix",
                new GregorianCalendar(1999, Calendar.MARCH, 31).getTime(),
                "Action",
                63000000,
                136,
                5f,
                false,
                "R",
                true,
                "https://example.com/posters/the-matrix.jpg"));
    }

    // ==================================================================================
    // WHAT IS MISSING FROM THIS FILE — AND IS ASKED AT THE EXAM
    // ==================================================================================
    // - `onSaveInstanceState(Bundle)`: it does not exist. On rotation, the activity is
    //   recreated, `movies` is reinitialized, and the added movies DISAPPEAR.
    //   A REAL risk, not a theoretical one: turn the phone after adding a movie.
    // - `onResume()` / `onStart()`: they do not exist. No need; everything is done in `onCreate`.
    // - `onDestroy()`: it does not exist. There are no resources to release.
    // - Menu, `OptionsMenu`, `Toolbar`: they do not exist. The screen is just a list + FAB.
    // ==================================================================================
}
```

---

## 29.4 `ItemActivity.java` — the form

```java
/*
 * ======================================================================================
 * FILE: ItemActivity.java — THE ADD / EDIT FORM
 * ======================================================================================
 * WHAT IT IS: a screen with 13 controls, which reads the values from them, builds a
 *   `Movie` and sends it back to `MainActivity` through a result `Intent`.
 *
 * WHY IT EXISTS: it is the ONLY place that knows how to turn widgets into a model.
 *   `MainActivity` touches no `EditText`; it receives a ready-made `Movie`.
 *
 * WHAT IT DEPENDS ON:
 *   - `activity_item.xml` — for the 13 IDs (`etTitle` ... `btnMovieAction`).
 *   - `MainActivity` — for the constants `MOVIE_EXTRA` and `POSITION_EXTRA`.
 *   - `Movie` — the type it builds.
 *   - `IntentCompat` — for the typed reading of the serializable extra.
 *
 * WHO DEPENDS ON IT:
 *   `MainActivity` (starts it through `launcher`), `AndroidManifest.xml` (declares it).
 *
 * WHAT IT DOES NOT DO:
 *   - It validates nothing: an empty budget produces a `NumberFormatException`, not a message.
 *   - It persists nothing: it writes to no file, to no `SharedPreferences` and to no database.
 *   - It does not load the poster: `etPoster` is just text.
 *   - It does not know what happens to the `Movie` after `finish()`.
 *
 * WHAT BREAKS WITHOUT IT:
 *   The app would have a list, but no way to add or change a movie.
 *   The FAB would start a non-existent activity -> `ActivityNotFoundException`.
 * ======================================================================================
 */

// The same package as `MainActivity` — that is why it can use its constants
// without an import and without the fully qualified name.
package ro.ase.ie.g1096.activities;

// ======================================================================================
// IMPORTS — 24 NAMES, ONE OF WHICH IS DEAD
// ======================================================================================
// android.widget.*   — the 13 widget types + their listener interfaces
// androidx.*         — AppCompat, EdgeToEdge, insets, IntentCompat, @NonNull
// com.google.*       — MaterialSwitch (the only Material widget in the code)
// java.text.*        — SimpleDateFormat and its exception
// java.util.*        — Calendar, Date, Locale
//
// DEAD: `android.widget.Switch`. The field is `MaterialSwitch`, which extends
//   `SwitchCompat`, NOT `android.widget.Switch`. See difference 29.0.6.
// ======================================================================================

// DatePickerDialog: the calendar dialog that appears on a click on the date field.
import android.app.DatePickerDialog;

// Intent: the result object, built in `saveMovie()`.
import android.content.Intent;

// Bundle: only in the signature of onCreate.
import android.os.Bundle;

// View: the type of the parameter in OnClickListener.
import android.view.View;

// Button: the type of the `btMovieAction` field.
import android.widget.Button;

// CheckBox: the type of the `cbonWatchList` field.
import android.widget.CheckBox;

// CompoundButton: the base class for Switch/CheckBox; the listener interface is here.
import android.widget.CompoundButton;

// DatePicker: the first parameter of `onDateSet`.
import android.widget.DatePicker;

// EditText: the type of the `etTitle`, `etRelease`, `etBudget`, `etPoster` fields.
import android.widget.EditText;

// RadioButton: the type into which each child of `rgApproval` is CAST.
import android.widget.RadioButton;

// RadioGroup: the container that guarantees a single selection among the radio buttons.
import android.widget.RadioGroup;

// RatingBar: the type of the `rbRating` field.
import android.widget.RatingBar;

// SeekBar: the type of the `sbDuration` field.
import android.widget.SeekBar;

// Spinner: the type of the `spGenre` field.
import android.widget.Spinner;

// Switch: DEAD IMPORT. No `Switch` name appears in the file.
// DANGER! If you "fixed" the import by using it — `private Switch swWatched;` —
//   `findViewById(R.id.swWatched)` would return a `MaterialSwitch`, which is NOT
//   a subclass of `android.widget.Switch`, and you would get a `ClassCastException` at runtime.
import android.widget.Switch;

// TextView: the type of the `tvDurationValue` and `tvWatchedValue` fields.
import android.widget.TextView;

// EdgeToEdge: drawing under the system bars.
import androidx.activity.EdgeToEdge;

// NonNull: an annotation on the parameter of `onCheckedChanged`. Only documentation for
//   the compiler and for lint; it does not change the bytecode.
import androidx.annotation.NonNull;

// AppCompatActivity: the base class.
import androidx.appcompat.app.AppCompatActivity;

// IntentCompat: a compatible variant of reading the extras. `getSerializableExtra(
//   Intent, String, Class<T>)` is the typed variant, which no longer throws
//   ClassCastException and works on all APIs.
import androidx.core.content.IntentCompat;

// Insets / ViewCompat / WindowInsetsCompat: the same three classes as in MainActivity,
// for the same padding listener.
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

// MaterialSwitch: the Material widget for the toggle. It extends SwitchCompat,
// which extends CompoundButton — that is why the listener is `CompoundButton.OnCheckedChangeListener`.
import com.google.android.material.materialswitch.MaterialSwitch;

// ParseException: the exception thrown by `SimpleDateFormat.parse` on invalid text.
import java.text.ParseException;

// SimpleDateFormat: formats and parses "dd/MM/yyyy".
import java.text.SimpleDateFormat;

// Calendar: the type of `releaseCal` and the YEAR / MONTH / DAY_OF_MONTH constants.
import java.util.Calendar;

// Date: the type returned by `dateFormat.parse(...)`.
import java.util.Date;

// Locale: the formatting depends on the locale (month names, separators).
import java.util.Locale;

// The R class — for the 13 IDs.
import ro.ase.ie.g1096.R;

// The model built by the form.
import ro.ase.ie.g1096.model.Movie;

/*
 * ======================================================================================
 * THEORY BLOCK: THE FORM AS A FACTORY AND THE TWO MODES
 * ======================================================================================
 *
 * 1. ONE SCREEN, TWO MODES
 *    There is no `AddActivity` and no `EditActivity`. There is one `ItemActivity` that
 *    behaves differently depending on what it receives in the `Intent`:
 *
 *      Intent WITHOUT MOVIE_EXTRA   -> INSERT mode: empty form, "Save Movie" button
 *      Intent WITH    MOVIE_EXTRA  -> EDIT mode:   filled form, "Update Movie" button
 *
 *    The discriminant is `existing != null`, not a separate boolean flag. Less
 *    code, fewer places where the flag can be wrong.
 *
 * 2. THE DIRECTION OF THE DATA
 *    MainActivity --(Intent with Movie)--> ItemActivity --(form)--> new Movie
 *    ItemActivity --(setResult with new Movie)--> MainActivity
 *    The data flows in a single direction, a single time. There are no observers,
 *    no intermediate callbacks.
 *
 * 3. THE RESULT `Intent` IS NEVER STARTED
 *    `new Intent()` without a target does not describe a navigation. It is just a container
 *    for `putExtra`, which `setResult` sends back to the caller.
 *    The classic confusion: "why does it not have `IntentActivity.class`?" — because it
 *    starts nothing.
 *
 * 4. WHO IS THE SOURCE OF TRUTH FOR THE DATE
 *    NOT the text in `etRelease`. But `releaseCal`, a `Calendar`. The text is only
 *    a representation; the calendar is the value. `saveMovie()` reads from the calendar.
 *    The consequence: if you forget to sync the calendar with the text, you save another date.
 *    Here this forgetting EXISTS — see BUG 2.
 *
 * 5. THE LIFECYCLE OF A FORM
 *    onCreate -> (the user fills it in) -> saveMovie -> setResult -> finish
 *    -> onPause -> onStop -> onDestroy. There is no autosave, there is no
 *    "draft". If you press Back, everything you typed is lost, with no warning.
 * ======================================================================================
 */

// The same base class as MainActivity.
public class ItemActivity extends AppCompatActivity {

    // ==================================================================================
    // THE 13 WIDGET FIELDS — THE ORDER FOLLOWS THE FORM, NOT THE XML
    // ==================================================================================
    // They are declared in the order in which they appear on screen: title, date, genre, budget,
    // duration, rating, guidance, watchlist, switch, poster, button, two labels.
    // The type of each is exactly the class from the XML — `EditText`, not `TextInputEditText`,
    // because `TextInputEditText` is a subclass of `EditText`.
    // ==================================================================================

    // The movie title. `TextInputEditText` in the XML is an `EditText`, so it works.
    private EditText etTitle;

    // The release date. It is NOT typed: the click opens a `DatePickerDialog`.
    private EditText etRelease;

    // The genre, chosen from `@array/movie_genre`.
    private Spinner spGenre;

    // The budget, typed on a numeric keyboard with decimals.
    private EditText etBudget;

    // The duration, chosen with the 0..300 slider.
    private SeekBar sbDuration;

    // The rating, 0..5 stars with a 0.5 step.
    private RatingBar rbRating;

    // The radio group for the parental guidance.
    private RadioGroup rgApproval;

    // The "Watchlist" checkbox. The field name has an extra `b` compared to the ID: `cbonWatchList`.
    private CheckBox cbonWatchList;

    // The "Recommended" switch. THE TYPE IS MATERIAL, not `android.widget.Switch`.
    private MaterialSwitch swWatched;

    // The poster URL, typed with a URI-type keyboard.
    private EditText etPoster;

    // The save button. Its text changes in edit mode.
    private Button btMovieAction;

    // The "148 min." label next to the slider — it updates on every movement.
    private TextView tvDurationValue;

    // The "Yes"/"No" label next to the switch — it updates on every toggle.
    private TextView tvWatchedValue;

    // ==================================================================================
    // INTERNAL STATE — THREE FIELDS THAT ARE NOT WIDGETS
    // ==================================================================================
    // `position` = the mode. -1 means insert; any other value means edit.
    //   It is the ONLY mode flag in the class. There is no `boolean isEdit`.
    //
    // `releaseCal` = the source of truth for the date. Initialized with "now", so that the dialog
    //   starts somewhere even if the user has chosen nothing.
    //
    // `dateFormat` = the common formatter for display and parsing. `final` because
    //   the reference does not change; `SimpleDateFormat` is internally mutable, but here
    //   it is used only on the main thread.
    // ==================================================================================
    private int position = -1;   // -1 = insert mode
    private Calendar releaseCal = Calendar.getInstance();
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    // ==================================================================================
    // onCreate — BUILDS THE FORM, THEN FILLS IT IF NEEDED
    // ==================================================================================
    // WHAT IT DOES: inflates the layout, binds the 13 views, attaches the 4 listeners,
    //   then reads the `Intent` and decides whether the form starts empty or filled.
    // HOW: 1. super 2. EdgeToEdge 3. setContentView 4. insets 5. initControls
    //   6. initListeners 7. getIntent 8. read the extra 9. if it exists, fillForm + texts.
    // RISK: the order 5-6-9 is essential. `fillForm` calls `setChecked` and
    //   `setProgress`, which trigger the listeners. If the listeners were not attached
    //   before, the labels `tvWatchedValue` and `tvDurationValue` would stay at
    //   the values from the XML ("No", "0 min").
    // REF: the same order as in MainActivity.onCreate, plus the step of reading the Intent.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. The base class chain. Mandatory first.
        super.onCreate(savedInstanceState);

        // 2. Drawing under the system bars.
        EdgeToEdge.enable(this);

        // 3. Inflates `activity_item.xml`. From this moment `findViewById` finds the views.
        setContentView(R.layout.activity_item);

        // 4. Padding for the system bars, on the root `R.id.main` (the ScrollView).
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // 5. Binds the 13 fields to the views.
        initControls();

        // 6. Attaches the 4 listeners. It MUST be before `fillForm`, because
        //    `fillForm` will trigger `onCheckedChanged` and `onProgressChanged`.
        initListeners();

        // 7. Gets the Intent that started the activity.
        //    - On insert: an empty Intent, built by the FAB.
        //    - On edit: an Intent with MOVIE_EXTRA and POSITION_EXTRA, built by the row click.
        Intent intent = getIntent();

        // 8. Reads the serialized object, in the TYPED variant.
        //    `IntentCompat.getSerializableExtra(intent, key, Movie.class)` returns
        //    `Movie` or `null` directly, with no manual cast and without the deprecated method.
        //    WATCH OUT: the object received is a deserialized COPY, not the original from the list.
        Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);

        // 9. The mode discriminant: does the object exist or not.
        if (existing != null) {

            // 9a. Keeps the position for `saveMovie`. If it is missing, it stays -1 and
            //     `saveMovie` would send a new movie instead of replacing.
            position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);

            // 9b. Fills the 13 controls with the movie's values.
            fillForm(existing);

            // 9c. `setTitle` is the method of the ACTIVITY (it changes the title in the ActionBar),
            //     NOT `Movie.setTitle`. Same name, another class — a reading trap.
            setTitle("Edit movie");

            // 9d. Changes the button text. The user sees that they are saving a change.
            btMovieAction.setText("Update Movie");
        }
        // If `existing` is null, nothing is done: the form stays empty,
        // the button stays "Save Movie" from the XML, and `position` stays -1.
    }

    // ==================================================================================
    // fillForm — MODEL -> WIDGETS
    // ==================================================================================
    // WHAT IT DOES: copies the 10 values of a `Movie` into the 13 controls.
    // HOW: 8 direct setters, then 2 loops — one over the Spinner (by TEXT), one over the
    //   RadioGroup (by TEXT).
    // RISK: the two loops fail SILENTLY if the text does not match. The Spinner
    //   stays on the first position, the radio group stays on the button checked by default.
    // REF: the pair of this method is `saveMovie()` — there it goes the other way, widget -> model.
    // ==================================================================================
    private void fillForm(Movie existing) {

        // Plain text. `setText` accepts `null` and displays an empty field.
        etTitle.setText(existing.getTitle());

        // The date: `Date` -> text with `SimpleDateFormat`. WATCH OUT: this line does NOT
        // update `releaseCal`. See BUG 2 below.
        etRelease.setText(dateFormat.format(existing.getRelease()));

        // The budget: `double` -> text. `String.valueOf(double)` produces "1.6E8" for
        // 160 000 000, not "160000000". See BUG 3.
        etBudget.setText(String.valueOf(existing.getBudget()));

        // The duration: `int` -> progress on the slider. The value is automatically limited to 0..300.
        // This line TRIGGERS `onProgressChanged`, which updates the label.
        sbDuration.setProgress(existing.getDuration());

        // The checkbox: `boolean` -> `setChecked`. It triggers the listener only if the value
        // CHANGES compared to the current state.
        cbonWatchList.setChecked(existing.isOnWatchlist());

        // The switch: `boolean` -> `setChecked`. It triggers `onCheckedChanged`,
        // which writes "Yes"/"No" into `tvWatchedValue`.
        swWatched.setChecked(existing.isWatched());

        // The rating: `float` -> `setRating(float)`. The types match exactly.
        rbRating.setRating(existing.getRating());

        // The poster: `String` -> text. It can be `null`; `setText(null)` is legal.
        etPoster.setText(existing.getPosterUrl());

        // LOOP 1 — the Spinner has no "setValue(String)". It only has "setSelection(index)".
        // So we look for the index by text, comparing each element with the movie's genre.
        for(int index=0; index<spGenre.getCount(); index++)
        {
            // `getItemAtPosition` returns the element from `@array/movie_genre`.
            // `.equals` on the object from the adapter; if it were null, it would throw an NPE.
            if(spGenre.getItemAtPosition(index).equals(existing.getGenre()))
            {
                // We found the genre — select it.
                spGenre.setSelection(index);

                // Exit the loop: the first match is enough.
                break;
            }
            // If no match is found, the spinner stays at position 0.
            // RISK: no message, no error. Only the displayed genre is different.
        }

        // LOOP 2 — the RadioGroup has no "select by text" either.
        // We iterate over the CHILDREN of the group, not over a separate array.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            // CAST to RadioButton. It works because all the children in the XML are
            // `MaterialRadioButton`, which extends `RadioButton`.
            // RISK: if someone adds a separator `View` in the RadioGroup, this cast
            //   throws `ClassCastException` on edit.
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // Compares the TEXT of the button ("G", "PG", "PG-13", "R", "NC-17") with the value.
            if(rb.getText().toString().equals(existing.getApproval()))
            {
                // `check(id)` checks the button and automatically unchecks the other —
                // this is the guarantee that the RadioGroup provides.
                rgApproval.check(rgApproval.getChildAt(index).getId());

                // Exit the loop.
                break;
            }
        }
    }

    // ==================================================================================
    // initControls — 13 FINDVIEWBYID CALLS, ONE FOR EACH ID IN THE XML
    // ==================================================================================
    // WHAT IT DOES: binds each Java field to the view with the corresponding ID.
    // HOW: 13 mechanical assignments. The order follows the order of the fields.
    // RISK: a wrong ID -> `findViewById` returns null -> `NullPointerException`
    //   on first use, not here. The hardest class of bugs to debug.
    // REF: `MainActivity.initControls()` has only 3 lines; here there are 13.
    // ==================================================================================
    private void initControls() {

        // Each line has the same shape: `field = findViewById(R.id.id_from_xml);`
        // `findViewById` is generic since API 26: the type is inferred from the field on the left.
        etTitle = findViewById(R.id.etTitle);
        etRelease = findViewById(R.id.etRelease);
        spGenre = findViewById(R.id.spGenre);
        etBudget = findViewById(R.id.etBudget);
        sbDuration = findViewById(R.id.sbDuration);
        rbRating = findViewById(R.id.rbRating);
        rgApproval = findViewById(R.id.rgApproval);

        // WATCH THE NAMES: the field is `cbonWatchList`, the ID is `cbOnWatchList`.
        // An extra `b` in the field, a capital `O` in the ID. Both are correct.
        cbonWatchList = findViewById(R.id.cbOnWatchList);

        swWatched = findViewById(R.id.swWatched);
        etPoster = findViewById(R.id.etPoster);

        // The button: the field `btMovieAction`, the ID `btnMovieAction`.
        btMovieAction = findViewById(R.id.btnMovieAction);

        // The two labels that are updated from the listeners.
        tvDurationValue = findViewById(R.id.tvDurationValue);
        tvWatchedValue = findViewById(R.id.tvWatchedValue);
    }

    // ==================================================================================
    // initListeners — FOUR BEHAVIOURS
    // ==================================================================================
    // WHAT IT DOES: attaches: click on the date -> dialog; click on the button -> save;
    //   switch change -> label; slider movement -> label.
    // HOW: 4 anonymous classes, one of which implements an interface with 3 methods.
    // RISK: the order matters relative to `fillForm` — see onCreate, step 6.
    // REF: `MainActivity.initListeners()` has 2 listeners; here there are 4.
    // ==================================================================================
    private void initListeners() {

        // LISTENER 1 — click on the date field.
        // An `EditText` has no "onDateClick"; we use the generic click.
        etRelease.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Opens the calendar dialog. The method is below.
                showReleaseDatePicker();
            }
        });

        // LISTENER 2 — click on the save button.
        btMovieAction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Builds the Movie, puts it in the Intent, sets the result, closes.
                saveMovie();
            }
        });

        // LISTENER 3 — the switch change.
        // The interface is `CompoundButton.OnCheckedChangeListener`, not one of MaterialSwitch's own:
        // MaterialSwitch is a CompoundButton.
        swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                // Ternary operator: a single expression for both cases.
                // `isChecked` is the NEW value, not the old one.
                tvWatchedValue.setText(isChecked ? "Yes" : "No");
            }
        });

        // LISTENER 4 — the duration slider.
        // The interface has THREE methods. All must be implemented; two stay empty.
        // There are no default methods in a classic Java interface.
        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // `progress` = the new value, 0..300.
                // `fromUser` = true if it comes from the user's finger, false if it
                //   comes from `setProgress(...)`. Here it is IGNORED on purpose:
                //   we want the label to be correct also when `fillForm` calls
                //   `setProgress`, not only when the user drags.
                tvDurationValue.setText(progress + " min.");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
                // Empty: we do not care about the moment the drag starts.
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                // Empty: we do not care about the moment the drag ends.
                // Here you could save the value or show a message, if needed.
            }
        });
    }

    // ==================================================================================
    // saveMovie — WIDGETS -> MODEL -> INTENT -> RESULT
    // ==================================================================================
    // WHAT IT DOES: reads the 13 controls, builds a `Movie`, puts it in a result
    //   `Intent` together with the position (if it exists) and closes the screen.
    // HOW: 1. new Movie() 2. nine setters 3. loop over the RadioGroup 4. Intent
    //   5. putExtra 6. conditional position 7. setResult 8. finish.
    // RISK: `Double.parseDouble` on empty text throws `NumberFormatException`.
    //   See BUG 1 — it is the only reproducible crash in the app.
    // REF: the pair of `fillForm`; the consumer is the callback in MainActivity.
    // ==================================================================================
    private void saveMovie() {

        // 1. An empty object, filled immediately with setters. That is why the no-argument
        //    constructor is mandatory in the model.
        Movie movie = new Movie();

        // 2. The nine setters that correspond to one widget each.
        //    The order does not matter; only the widget -> setter pairs matter.
        movie.setTitle(etTitle.getText().toString());

        // THE DATE DOES NOT COME FROM THE TEXT, but from the calendar. The text can be invalid; the calendar cannot.
        // `getTime()` turns the Calendar -> Date.
        movie.setRelease(releaseCal.getTime());

        // The genre: the text selected in the Spinner. `getSelectedItem()` is not null as long as
        // the spinner has at least one element (the values from `@array/movie_genre`).
        movie.setGenre(spGenre.getSelectedItem().toString());

        // BUG 1: if `etBudget` is empty, `Double.parseDouble("")` throws
        // `NumberFormatException`, and the app closes. There is no try/catch
        // and there is no `isEmpty()` check.
        // The same line also rejects "1,5" (decimal comma, Romanian locale), but
        // accepts "1.6E8" (scientific notation).
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));

        // The duration: straight from the progress, with no conversion.
        movie.setDuration(sbDuration.getProgress());

        // The rating: `getRating()` returns `float`, exactly the field's type.
        movie.setRating(rbRating.getRating());

        // The switch: `isChecked()` -> boolean.
        movie.setWatched(swWatched.isChecked());

        // The checkbox: `isChecked()` -> boolean. Independent of the switch.
        movie.setOnWatchlist(cbonWatchList.isChecked());

        // The poster: free text. It can be empty — the model accepts it.
        movie.setPosterUrl(etPoster.getText().toString());

        // 3. The parental guidance: there is no direct getter on the RadioGroup, so we look for
        //    the checked button. The same loop as in `fillForm`, but with `isChecked()`.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // Exactly one button is checked (RadioGroup guarantee). If none were
            // checked, `approval` would stay null — but the XML checks `rbGeneral` by default.
            if(rb.isChecked())
            {
                // The saved value is the TEXT of the button, not the ID.
                movie.setApproval(rb.getText().toString());
                break;
            }
        }

        // 4. An Intent WITHOUT a target. It starts no activity: it is the container of the
        //    result, read by the callback in MainActivity.
        Intent intent = new Intent();

        // 5. Puts the movie. `putExtra(String, Serializable)` serializes the object.
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);

        // 6. The position is set ONLY in edit mode. In insert mode, its absence is
        //    exactly the signal that `MainActivity` reads as "add at the end".
        //    No braces: the `if` controls a single statement.
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);

        // 7. Sets the result code. `RESULT_OK` is -1 — the same value as
        //    "the position is missing", but completely unrelated. Here it is a result code,
        //    there it is a list index. A numeric coincidence, not a conflict.
        setResult(RESULT_OK, intent);

        // 8. Closes the activity. Without `finish()`, `setResult` never reaches
        //    the caller, because the activity would stay open.
        finish();
    }

    // ==================================================================================
    // showReleaseDatePicker — THE CALENDAR DIALOG
    // ==================================================================================
    // WHAT IT DOES: opens a `DatePickerDialog` positioned on the current date from
    //   `releaseCal`, and on confirmation writes the date into the calendar AND into the text.
    // HOW: 1. parses the existing text (if valid) 2. builds the dialog
    //   3. on confirmation, updates the calendar 4. formats it back into the EditText.
    // RISK: if the text in the field was typed by hand and is invalid, the parse
    //   fails silently and the dialog starts from the old date in the calendar.
    // REF: `SimpleDateFormat` is also used in `fillForm`; here in the opposite direction.
    // ==================================================================================
    private void showReleaseDatePicker() {

        // The current text in the field. It can be empty (new form) or a date formatted
        // by `fillForm` (edit mode) or text typed by hand by the user.
        String current = etRelease.getText().toString();

        // We parse only if there is something to parse.
        if (!current.isEmpty()) {
            try {
                // `parse` returns a `Date` or throws a `ParseException`.
                Date parsed = dateFormat.parse(current);

                // `parse` can theoretically return null; we check before using it.
                if (parsed != null)
                    // Syncs the calendar with the text. Here is where the text -> Calendar
                    // link happens, the one missing from `fillForm` (BUG 2).
                    releaseCal.setTime(parsed);
            } catch (ParseException ignored) { }
            // The exception is IGNORED on purpose: invalid text must not block the
            // dialog. It starts from the old date in the calendar.
            // RISK: the user never learns that their text was ignored.
        }

        // Builds the dialog. The parameters:
        //   1. `this` = Context
        //   2. the confirmation listener (anonymous class)
        //   3-5. the year, the month, the start day — THE MONTH IS 0-BASED (`Calendar.MONTH`)
        // `.show()` at the end: the dialog does not appear until it is called.
        new DatePickerDialog(
                this,
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {

                        // `month` also comes 0-based from DatePicker, so it matches
                        // directly with `Calendar.set(year, month, day)`. No conversion.
                        releaseCal.set(year, month, day);

                        // Clears any error previously displayed on the field. Here nothing
                        // ever sets an error, but the call is defensive.
                        etRelease.setError(null);

                        // Writes the date back into the field, in the same "dd/MM/yyyy" format.
                        etRelease.setText(dateFormat.format(releaseCal.getTime()));
                    }
                },
                // The start values: exactly the current state of the calendar.
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)
        ).show();
    }

    // ==================================================================================
    // THE THREE REAL BUGS IN THIS FILE
    // ==================================================================================
    // BUG 1 — EMPTY BUDGET -> CRASH
    //   `Double.parseDouble("")` throws `NumberFormatException`. The user presses
    //   "Save Movie" without filling in the budget, the app closes.
    //   100% reproducible. There is no validation, there is no try/catch.
    //
    // BUG 2 — THE DATE IS LOST ON EDIT
    //   `fillForm` writes the date into `etRelease`, but does NOT write it into `releaseCal`.
    //   `releaseCal` stays on `Calendar.getInstance()`, that is, "now", from the moment
    //   the activity was created. If the user edits a movie and does NOT touch the date
    //   field, `saveMovie` saves `releaseCal.getTime()` = TODAY's date.
    //   The movie "Inception" (2010) becomes "today", with no error.
    //   The correct thing would be for `fillForm` to also do `releaseCal.setTime(existing.getRelease())`.
    //
    // BUG 3 — SCIENTIFIC NOTATION IN THE BUDGET FIELD
    //   `String.valueOf(160000000.0)` produces "1.6E8", not "160000000".
    //   On edit, the field displays "1.6E8". Parsing it back works, so
    //   the data is correct — only the display is ugly. Cosmetic, but visible.
    //
    // AN ADDITIONAL RISK — THE GENRE THAT IS NOT FOUND
    //   If `@array/movie_genre` changes and the saved value no longer exists,
    //   `fillForm` leaves the spinner at position 0, with no message. On save, the movie's
    //   genre changes to the first element in the list.
    // ==================================================================================
}
```

---

## 29.5 `AndroidManifest.xml` — the app's map

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- ================================================================================== -->
<!-- FILE: AndroidManifest.xml — THE APP'S CONTRACT WITH THE SYSTEM                     -->
<!-- ================================================================================== -->
<!-- WHAT IT IS: the file that Android reads BEFORE executing any Java code.            -->
<!--   It declares which components the app has, which one is the start one, which      -->
<!--   theme it uses and which permissions it asks for.                                 -->
<!-- WHY IT EXISTS: without it, the system does not know that `MainActivity` exists.     -->
<!--   A Java class is not "an activity" just by extending AppCompatActivity; it         -->
<!--   becomes an activity only when it is declared here.                               -->
<!-- WHO DEPENDS ON IT: the build process (it merges it into the APK), the system        -->
<!--   launcher, `PackageManager`.                                                      -->
<!-- WHAT IT DOES NOT DO: it contains no code, no layouts, no navigation logic.          -->
<!-- WHAT BREAKS WITHOUT IT: the app would not install at all.                           -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- THE ROOT MANIFEST                                                                  -->
<!-- ================================================================================== -->
<!-- ATTRIBUTES:                                                                        -->
<!--   xmlns:android -> the namespace of the framework attributes                       -->
<!--   xmlns:tools   -> the namespace of the attributes for Android Studio               -->
<!--                                                                                    -->
<!-- NOTE: there is NO `package` attribute. In AGP 7+ the package is declared in         -->
<!--   `build.gradle` through `namespace = "ro.ase.ie.g1096"`. Old tutorials show       -->
<!--   `package="ro.ase.ie.g1096"` here; the syntax was moved.                          -->
<!--                                                                                    -->
<!-- `xmlns:tools` is DECLARED, but in this file it is NOT used: there is no             -->
<!--   `tools:...` attribute. The declaration is harmless, but useless.                 -->
<!-- ================================================================================== -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- ============================================================================== -->
    <!-- THE <application> ELEMENT — everything about the app as a whole                 -->
    <!-- ============================================================================== -->
    <!-- ATTRIBUTES, IN ORDER:                                                           -->
    <!--   allowBackup="true"            -> the system can save the app's data           -->
    <!--                                    (Android Auto Backup).                       -->
    <!--   dataExtractionRules           -> the backup rules for API 31+; it points      -->
    <!--                                    to `res/xml/data_extraction_rules.xml`.      -->
    <!--   fullBackupContent             -> the backup rules for API 30 and below;       -->
    <!--                                    it points to `res/xml/backup_rules.xml`.      -->
    <!--   icon / roundIcon              -> the icons from `res/mipmap`; the two variants -->
    <!--                                    cover the launchers that cut the corners.     -->
    <!--   label                         -> the name shown under the icon, from `strings.xml`. -->
    <!--   supportsRtl="true"            -> the layouts mirror in RTL languages.         -->
    <!--   theme                         -> the app's theme. HERE is the ONLY value       -->
    <!--                                    specific to the group: `Theme.G1096`. In G1097 -->
    <!--                                    it is `Theme.G1097`. Otherwise the file is    -->
    <!--                                    identical.                                   -->
    <!--                                                                                 -->
    <!-- WHAT DOES NOT EXIST HERE — and it matters: NO permission. There is no           -->
    <!--   `<uses-permission android:name="android.permission.INTERNET" />`.             -->
    <!--   The app makes no network request: the poster is stored as text and            -->
    <!--   is never downloaded.                                                          -->
    <!-- ============================================================================== -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.G1096">

        <!-- ========================================================================== -->
        <!-- ACTIVITY 1: MainActivity — THE START SCREEN                                 -->
        <!-- ========================================================================== -->
        <!-- android:name=".activities.MainActivity"                                     -->
        <!--   The leading dot is RELATIVE to the app's namespace.                       -->
        <!--   The full form would be `ro.ase.ie.g1096.activities.MainActivity`.         -->
        <!--                                                                             -->
        <!-- android:exported="true"                                                     -->
        <!--   MANDATORY since API 31 for any component with an intent-filter.           -->
        <!--   `true` = other apps can start this activity. It is required               -->
        <!--   for the launcher: the system must be able to start it.                    -->
        <!--   Without the attribute, the build fails with "Apps targeting Android 12    -->
        <!--   and higher are required to specify an explicit value for android:exported". -->
        <!--                                                                             -->
        <!-- android:windowSoftInputMode="adjustResize"                                  -->
        <!--   When the keyboard appears, the window SHRINKS, it is not covered. The     -->
        <!--   list stays visible above the keyboard.                                    -->
        <!-- ========================================================================== -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!-- THE LAUNCHER INTENT-FILTER                                            -->
            <!-- The MAIN + LAUNCHER pair is what makes the icon in the menu start the -->
            <!-- app. Without it, the activity would exist, but it would have no entry. -->
            <!--                                                                       -->
            <!-- `MAIN`     = the app's entry point.                                   -->
            <!-- `LAUNCHER` = it appears in the system's app list.                     -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <!-- The category: "show me in the launcher". -->
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ========================================================================== -->
        <!-- ACTIVITY 2: ItemActivity — THE FORM                                         -->
        <!-- ========================================================================== -->
        <!-- android:exported="false"                                                    -->
        <!--   `false` = ONLY our app can start it. No other app                        -->
        <!--   can open the form directly. It is the correct value for an               -->
        <!--   internal activity.                                                       -->
        <!--                                                                             -->
        <!-- It has NO intent-filter: it is not an entry point, it is opened from code  -->
        <!-- through `launcher.launch(new Intent(this, ItemActivity.class))`.            -->
        <!--                                                                             -->
        <!-- `windowSoftInputMode="adjustResize"` again: the form has text fields       -->
        <!-- at the bottom of a ScrollView, and the keyboard must shrink the            -->
        <!-- window so that scrolling works.                                            -->
        <!--                                                                             -->
        <!-- WATCH OUT: the element closes with `/>` because it has no children.        -->
        <!-- ========================================================================== -->
        <activity
            android:name=".activities.ItemActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**The map of the two activities:**

```
                    AndroidManifest.xml
                           |
        +------------------+-------------------+
        |                                      |
  MainActivity                          ItemActivity
  exported = true                       exported = false
  intent-filter MAIN+LAUNCHER           no intent-filter
  windowSoftInputMode = adjustResize    windowSoftInputMode = adjustResize
        |                                      ^
        |                                      |
        +---- launcher.launch(Intent) ---------+
              (only from inside the app)
```

---

## 29.6 `activity_main.xml` — the list screen

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- ================================================================================== -->
<!-- FILE: activity_main.xml — THE SCREEN WITH THE LIST                                 -->
<!-- ================================================================================== -->
<!-- WHAT IT IS: a FrameLayout with exactly two children: the ListView (fills it all) and the FAB (over it). -->
<!-- WHY SO LITTLE: all the complexity is in `activity_item.xml` (the form).            -->
<!--   Here only the skeleton.                                                          -->
<!-- STRUCTURE:                                                                         -->
<!--                                                                                    -->
<!--   FrameLayout (id=main)                                                            -->
<!--   |== ListView (id=listView)            <- first child = drawn first = underneath   -->
<!--   +== FloatingActionButton (id=...)     <- second child = drawn over the list       -->
<!--                                                                                    -->
<!-- THE ORDER OF THE CHILDREN IS MEANING, NOT STYLE: in a FrameLayout, each child is    -->
<!--   drawn over the previous one. Reversed, the list would cover the button.          -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- FRAMELAYOUT — the root container                                                    -->
<!-- ================================================================================== -->
<!-- WHY FrameLayout and not LinearLayout: the children must OVERLAP. A LinearLayout     -->
<!--   would place them next to each other, and the FAB would no longer float over it.   -->
<!-- WHY not ConstraintLayout: for two children, a FrameLayout is simpler.              -->
<!--                                                                                    -->
<!-- ATTRIBUTES:                                                                        -->
<!--   xmlns:android   -> the framework attributes                                      -->
<!--   xmlns:app       -> the library attributes (Material, AndroidX)                   -->
<!--   xmlns:tools     -> attributes that exist ONLY in the preview and are removed at  -->
<!--                      build time. They never reach the APK.                         -->
<!--   android:id      -> @+id/main; `@+id/` CREATES the ID, `@id/` REFERS to it        -->
<!--   layout_width    -> match_parent: it takes the parent's full width                 -->
<!--   layout_height   -> match_parent: it takes the full height                        -->
<!--   orientation     -> INVALID ATTRIBUTE on FrameLayout; it exists only on LinearLayout. -->
<!--                      It is IGNORED by Android and produces a lint warning          -->
<!--                      ("Unknown attribute"). A leftover from a previous LinearLayout. -->
<!--   tools:context   -> only for the preview; it tells Android Studio which            -->
<!--                      activity to use for the theme.                                -->
<!--                                                                                    -->
<!-- WHY `android:id="@+id/main"` IS MANDATORY: the code does                           -->
<!--   `findViewById(R.id.main)` for the insets listener. Without this ID, the call     -->
<!--   would return null and `setOnApplyWindowInsetsListener(null, ...)` would throw an NPE. -->
<!-- ================================================================================== -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!-- ============================================================================== -->
    <!-- LISTVIEW — the scrolling list                                                   -->
    <!-- ============================================================================== -->
    <!-- WHY ListView and not RecyclerView: at this commit the classic ListView is taught. -->
    <!--   RecyclerView appears in the next lab, together with a row layout of its own.  -->
    <!--   G1096 does not even have `movie_item.xml`.                                    -->
    <!--                                                                                 -->
    <!-- ATTRIBUTES:                                                                     -->
    <!--   android:id            -> listView; used by `findViewById` in initControls      -->
    <!--   layout_width/height   -> match_parent on both axes: the list fills the whole  -->
    <!--                            screen, including the area under the FAB. The FAB is  -->
    <!--                            drawn OVER the list, not the list next to it.         -->
    <!--   android:entries       -> fills the list from the XML with the elements from    -->
    <!--                            `@array/items`. AT RUNTIME, `listView.setAdapter`    -->
    <!--                            (movieAdapter) COMPLETELY REPLACES this adapter.      -->
    <!--                            `entries` remains only so that the preview shows a    -->
    <!--                            full list. The runtime cost is zero after `setAdapter`. -->
    <!--                                                                                 -->
    <!-- RISK: the last row in the list can sit under the FAB. The list has no bottom     -->
    <!--   padding, and the button is drawn over it. With 3 movies you miss it; with 30, not. -->
    <!-- ============================================================================== -->
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />

    <!-- ============================================================================== -->
    <!-- FLOATING ACTION BUTTON — the "+" button                                         -->
    <!-- ============================================================================== -->
    <!-- The full name is needed because it is a class from the Material library,        -->
    <!--   not one from the framework. The `com.google.android.material...` prefix is the path. -->
    <!--                                                                                 -->
    <!-- ATTRIBUTES:                                                                     -->
    <!--   android:id          -> floatingActionButton; looked up in initControls         -->
    <!--   layout_width/height -> wrap_content: the FAB has a fixed size imposed by       -->
    <!--                          the style (56dp by default). `match_parent` would stretch it. -->
    <!--   android:layout_gravity -> the position of THIS CHILD in ITS PARENT (the FrameLayout). -->
    <!--   android:layout_margin  -> 16dp on all sides. Together with the insets padding  -->
    <!--                          applied on `R.id.main`, the button sits 16dp from the   -->
    <!--                          safe area, not from the physical edge.                  -->
    <!--   android:contentDescription -> the text read by TalkBack. MANDATORY for         -->
    <!--                          elements with no visible text; without it, lint         -->
    <!--                          warns ("ContentDescription"), and users with a          -->
    <!--                          screen reader hear only "button".                       -->
    <!--   app:srcCompat       -> the compatible variant for vector images.               -->
    <!--                          `android:src` would work on API 21+, but `srcCompat`    -->
    <!--                          is the AndroidX recommendation.                         -->
    <!--                                                                                 -->
    <!-- layout_gravity  vs  gravity:                                                    -->
    <!--   gravity         = how the ELEMENT arranges ITS children inside itself          -->
    <!--   layout_gravity  = how the ELEMENT is arranged in its parent                    -->
    <!--                                                                                 -->
    <!-- `bottom|end` = bottom, right. `end` respects the reading direction: in RTL it    -->
    <!--   becomes left. `right` would have been fixed and would be wrong in RTL.         -->
    <!-- ============================================================================== -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_24" />

</FrameLayout>
```

**Reference table for the attributes in this file:**

| Attribute | Value | Effect |
|---|---|---|
| `android:id` | `@+id/main` | creates the ID used by the insets |
| `android:layout_width/height` | `match_parent` | fills the parent |
| `android:layout_gravity` | `bottom\|end` | positions the FAB in the FrameLayout |
| `android:contentDescription` | `"Add"` | accessibility + lint |
| `app:srcCompat` | `@drawable/outline_add_24` | compatible vector image |
| `tools:context` | `.activities.MainActivity` | preview only |
| `android:orientation` | `horizontal` | **invalid** on FrameLayout, ignored |

---

## 29.7 `activity_item.xml` — the form

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- ================================================================================== -->
<!-- FILE: activity_item.xml — THE ADD / EDIT FORM                                       -->
<!-- ================================================================================== -->
<!-- WHAT IT IS: a ScrollView with a single vertical LinearLayout child, split into      -->
<!--   four cards (Basics, Production, Your verdict, Poster) plus the save button.       -->
<!-- WHY IT EXISTS: it is the only layout that `ItemActivity` works with. The 13 IDs     -->
<!--   looked up in `initControls()` are all here.                                       -->
<!-- WHO DEPENDS ON IT: `ItemActivity` (through `setContentView(R.layout.activity_item)`). -->
<!-- WHAT IT DOES NOT DO: it does not validate, does not display errors, has no helper    -->
<!--   text for invalid fields. It is strictly structure.                                -->
<!-- WHAT BREAKS WITHOUT IT: `setContentView` would throw `Resources.NotFoundException`, -->
<!--   and every `findViewById` would return null.                                       -->
<!--                                                                                    -->
<!-- IDENTICAL TO G1097. All the observations in chapter 22, section 22.5, apply         -->
<!--   here word for word.                                                              -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- RULE 1: `?attr/` vs `@color/` vs `#RRGGBB`                                          -->
<!-- ================================================================================== -->
<!--   ?attr/colorPrimary   -> resolved at RUNTIME, from the current theme; it changes   -->
<!--                           in dark mode. It is a ROLE, not a value.                  -->
<!--   @color/my_color      -> resolved at BUILD time, from `colors.xml`; it does not change. -->
<!--   #FFC107              -> a literal, at build time; an accepted exception (the stars). -->
<!--   @android:color/...   -> a framework constant.                                     -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- RULE 2: `0dp` + `layout_weight`                                                     -->
<!-- ================================================================================== -->
<!--   Horizontal LinearLayout, total width 360dp:                                       -->
<!--   +--------------------------------------------------------------+                 -->
<!--   | TextView A        | TextView B                               |                 -->
<!--   | width=0dp         | width=wrap_content                       |                 -->
<!--   | weight=1          | (no weight)                              |                 -->
<!--   +-------------------+------------------------------------------+                 -->
<!--   |<=== the rest =====>|<====== as much as the text asks ========>|                 -->
<!--                                                                                    -->
<!--   `0dp` + `weight` = "I do not care about my width, give me what is left".          -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- RULE 3: `style=` vs explicit attributes                                             -->
<!-- ================================================================================== -->
<!--   `style="@style/Widget.Material3.TextInputLayout.OutlinedBox"` applies a PACKAGE   -->
<!--   of attributes. An attribute written explicitly next to `style` OVERRIDES the one  -->
<!--   from the style. That is why `app:cardCornerRadius="20dp"` works over the card style. -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- SCROLLVIEW — the root                                                                -->
<!-- ================================================================================== -->
<!-- WHY ScrollView: the form is taller than a phone screen. Without it,                  -->
<!--   the save button would be unreachable on small screens.                            -->
<!-- RULE: a ScrollView accepts EXACTLY ONE child. A second one would produce an          -->
<!--   exception at inflate time ("ScrollView can host only one direct child").           -->
<!--                                                                                    -->
<!-- ATTRIBUTES:                                                                        -->
<!--   android:id="@+id/main"     -> used by the insets listener in ItemActivity.        -->
<!--   layout_width/height        -> match_parent on both axes.                          -->
<!--   android:background         -> `?attr/colorSurface`, the theme's background colour. -->
<!--                                 Without it, the background would be the default and  -->
<!--                                 could differ from the rest of the app.              -->
<!--   android:fillViewport="true"-> the child is stretched to cover at least the screen, -->
<!--                                 even if it has less content.                        -->
<!--   tools:context              -> preview only.                                       -->
<!-- ================================================================================== -->
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <!-- ============================================================================== -->
    <!-- THE CONTENT — a single vertical LinearLayout                                    -->
    <!-- ============================================================================== -->
    <!-- `paddingHorizontal` and `paddingTop/Bottom` exist since API 26. On older        -->
    <!--   versions they would be ignored; the project uses EdgeToEdge, so the API is    -->
    <!--   modern anyway.                                                                -->
    <!-- ============================================================================== -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- ========================================================================== -->
        <!-- THE SCREEN HEADER                                                          -->
        <!-- ========================================================================== -->
        <!-- Two static TextView widgets, WITHOUT an id: they are never read from code. -->
        <!-- The first: the large title, with the theme's headline style.               -->
        <!-- Header -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Movie details"
            android:textAppearance="?attr/textAppearanceHeadlineMedium"
            android:textColor="?attr/colorOnSurface"
            android:textStyle="bold" />

        <!-- The second: the subtitle, smaller, with the secondary colour. -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="20dp"
            android:text="Fill in the information below and save."
            android:textAppearance="?attr/textAppearanceBodyMedium"
            android:textColor="?attr/colorOnSurfaceVariant" />

        <!-- ========================================================================== -->
        <!-- CARD 1 — "Basics": title, genre, date                                      -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 1: Basics ============ -->
        <!-- A MaterialCardView with the "filled" style: coloured background, no outline. -->
        <!-- `cardCornerRadius="20dp"` is written explicitly and OVERRIDES the value    -->
        <!--   from the style.                                                          -->
        <!-- ========================================================================== -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <!-- The inner vertical container, with 16dp padding on all sides. -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!-- The section title. `?attr/colorPrimary` makes it coloured. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Basics"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- THE "Title" LABEL — id `tvTile`, not `tvTitle`.                  -->
                <!--   A real typo in the source. It is not used anywhere in Java, so -->
                <!--   the typo has no effect. But if you wanted to use it,           -->
                <!--   `findViewById(R.id.tvTitle)` would return null.                -->
                <!-- Title -->
                <TextView
                    android:id="@+id/tvTile"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Title"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- THE TITLE FIELD, wrapped in a TextInputLayout.                   -->
                <!--   `hintEnabled="false"` -> no floating label; the hint from the  -->
                <!--     EditText behaves like an ordinary placeholder.               -->
                <!--   `endIconMode="clear_text"` -> adds an X that clears the field. -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text">

                    <!-- `TextInputEditText` is a subclass of `EditText`, so it binds -->
                    <!--   to the `private EditText etTitle` field.                    -->
                    <!-- `textCapWords` -> the keyboard capitalizes each word.         -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Movie title"
                        android:inputType="textCapWords" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- THE "Genre" LABEL. -->
                <!-- Genre -->
                <TextView
                    android:id="@+id/tvGenre"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Genre"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- THE SPINNER, WRAPPED IN A CARD.                                  -->
                <!--   WHY: `Spinner` has no Material "outlined" style. The trick     -->
                <!--   is a MaterialCardView with an outline, 56dp tall (the standard -->
                <!--   height of a Material field), in which the spinner fills all.   -->
                <!--   `cardBackgroundColor="@android:color/transparent"` -> no       -->
                <!--   background of its own, so that the parent card shows through.  -->
                <com.google.android.material.card.MaterialCardView
                    style="?attr/materialCardViewOutlinedStyle"
                    android:layout_width="match_parent"
                    android:layout_height="56dp"
                    android:layout_marginBottom="16dp"
                    app:cardBackgroundColor="@android:color/transparent"
                    app:cardCornerRadius="4dp"
                    app:strokeColor="?attr/colorOutline">

                    <!-- `entries` fills the spinner from `@array/movie_genre` — the values -->
                    <!--   defined in a file in `res/values/`, not in this one.             -->
                    <!-- `spinnerMode="dropdown"` -> the list opens as a popup,             -->
                    <!--   not as a modal dialog.                                          -->
                    <Spinner
                        android:id="@+id/spGenre"
                        android:layout_width="match_parent"
                        android:layout_height="match_parent"
                        android:entries="@array/movie_genre"
                        android:paddingStart="4dp"
                        android:spinnerMode="dropdown" />
                </com.google.android.material.card.MaterialCardView>

                <!-- THE DATE FIELD.                                                  -->
                <!--   `hintEnabled="true"` (the default value, written explicitly) -> -->
                <!--   the "Release date" label FLOATS above when the field has text. -->
                <!--   `startIconDrawable` -> the calendar icon on the left.          -->
                <!--   `startIconContentDescription` -> the text read by TalkBack      -->
                <!--   for the icon.                                                  -->
                <!-- Release date -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="true"
                    app:startIconContentDescription="Release date"
                    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

                    <!-- `inputType="date"` -> a numeric keyboard with `/` and `-`.   -->
                    <!--   The field stays EDITABLE: the user can type invalid text,  -->
                    <!--   and `showReleaseDatePicker` ignores it silently.           -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etRelease"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Release date"
                        android:inputType="date" />
                </com.google.android.material.textfield.TextInputLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ========================================================================== -->
        <!-- CARD 2 — "Production": budget and duration                                 -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 2: Production ============ -->
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

                <!-- The section title. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Production"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- THE "Budget" LABEL. -->
                <!-- Budget -->
                <TextView
                    android:id="@+id/tvBudget"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Budget"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- THE BUDGET FIELD.                                                -->
                <!--   `prefixText="$ "` -> displays "$ " in front of the value,      -->
                <!--   without adding it to the text. It is only visual.              -->
                <!--   `inputType="numberDecimal"` -> a numeric keyboard with a       -->
                <!--   decimal point. The comma is not available on all keyboards.    -->
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

                <!-- THE DURATION ROW: label + current value.                         -->
                <!--   `layout_weight="1"` on the label -> it takes all the remaining -->
                <!--   space, and the value sits on the right, against the margin.    -->
                <!-- Duration -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">

                    <!-- `width="0dp"` + `weight="1"` = "take what is left". -->
                    <TextView
                        android:id="@+id/tvDuration"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Duration"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!-- THE CURRENT VALUE. The initial text is "0 min" (WITHOUT a dot), -->
                    <!--   but Java writes "0 min." (WITH a dot) on the first update.    -->
                    <!--   A real cosmetic inconsistency between the XML and the code.    -->
                    <!--   `tools:text` is only for the preview; it never reaches the APK. -->
                    <TextView
                        android:id="@+id/tvDurationValue"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorPrimary"
                        tools:text="148 min" />
                </LinearLayout>

                <!-- THE DURATION SLIDER.                                             -->
                <!--   `android:max="300"` -> the maximum value.                      -->
                <!--   `android:min="0"` -> an attribute available since API 26; on   -->
                <!--     older versions it is ignored and the minimum stays 0 anyway. -->
                <!--   `progressTint` / `thumbTint` -> the colour of the bar and of   -->
                <!--     the handle, taken from the current theme.                    -->
                <!--   `tools:progress="148"` -> preview only.                        -->
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

                <!-- The legend under the slider: 0 on the left, 300 on the right. -->
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
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ========================================================================== -->
        <!-- CARD 3 — "Your verdict": rating, switch, checkbox, guidance                -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 3: Your verdict ============ -->
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

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Your verdict"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- THE "Rating" LABEL. -->
                <!-- Rating -->
                <TextView
                    android:id="@+id/tvRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Rating"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- THE RATINGBAR.                                                   -->
                <!--   `numStars="5"` -> five stars.                                  -->
                <!--   `stepSize="0.5"` -> half stars.                                -->
                <!--   `#FFC107` -> HARDCODED amber, not from the theme. In dark mode -->
                <!--     it stays the same. An accepted exception, not a theme role.  -->
                <!--   `layout_gravity="center_horizontal"` -> centred in the vertical -->
                <!--     parent.                                                      -->
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

                <!-- Separator: a 1dp line, coloured from the theme. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- THE "Recommended" ROW + switch + checkbox.                       -->
                <!--   `minHeight="48dp"` -> the minimum touch target recommended by  -->
                <!--   Material.                                                      -->
                <!-- Recommended -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:minHeight="48dp"
                    android:orientation="horizontal">

                    <!-- The text column: label + value. -->
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">

                        <!-- WATCH THE SEMANTICS: the label says "Recommended",     -->
                        <!--   but the field in the model is called `watched`. The  -->
                        <!--   two do not mean the same thing. It is an             -->
                        <!--   inconsistency between the UI and the model, not a    -->
                        <!--   functional bug: the switch saves exactly what it shows. -->
                        <TextView
                            android:id="@+id/tvWatched"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Recommended"
                            android:textAppearance="?attr/textAppearanceBodyLarge"
                            android:textColor="?attr/colorOnSurface" />

                        <!-- The textual value of the switch. It starts at "No" and is -->
                        <!--   rewritten by the listener with "Yes"/"No".              -->
                        <TextView
                            android:id="@+id/tvWatchedValue"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="No"
                            android:textAppearance="?attr/textAppearanceLabelLarge"
                            android:textColor="?attr/colorPrimary" />
                    </LinearLayout>

                    <!-- THE TOGGLE. The full Material type, exactly the type of the -->
                    <!--   `private MaterialSwitch swWatched;` field.               -->
                    <com.google.android.material.materialswitch.MaterialSwitch
                        android:id="@+id/swWatched"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="12dp" />

                    <!-- THE "Watchlist" CHECKBOX. A Material type, but the Java field -->
                    <!--   is `CheckBox` — MaterialCheckBox is a subclass, so it works. -->
                    <com.google.android.material.checkbox.MaterialCheckBox
                        android:id="@+id/cbOnWatchList"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Watchlist" />
                </LinearLayout>

                <!-- The second separator. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- THE "Guidance" LABEL. -->
                <!-- Guidance -->
                <TextView
                    android:id="@+id/tvGuidance"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Guidance"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- FIVE RADIO BUTTONS DO NOT FIT on a narrow screen. That is why they are -->
                <!--   put in a HorizontalScrollView: they can be scrolled sideways.        -->
                <!--   `scrollbars="none"` -> no visible scrollbar.                         -->
                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none">

                    <!-- THE RADIOGROUP. `orientation="horizontal"` -> the buttons sit  -->
                    <!--   on one row. The group's guarantee: exactly ONE is checked.   -->
                    <RadioGroup
                        android:id="@+id/rgApproval"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <!-- `android:checked="true"` -> the default selection. Without it, -->
                        <!--   no button would be checked and `approval` would stay         -->
                        <!--   null on save.                                                -->
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

                        <!-- The text "PG-13" is EXACTLY the value saved in the model. -->
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
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ========================================================================== -->
        <!-- CARD 4 — "Poster"                                                          -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 4: Poster ============ -->
        <!-- The only card with A SINGLE field. The "Poster" label has no id, unlike the -->
        <!--   other section labels.                                                    -->
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

                <!-- THE URL FIELD.                                                   -->
                <!--   `inputType="textUri"` -> a keyboard with `/`, `.` and `.com`.  -->
                <!--   `startIconDrawable` -> the gallery icon.                       -->
                <!--   `endIconMode="clear_text"` -> the clearing X.                  -->
                <!--   NO preview: there is no ImageView, there is no loading.        -->
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

        <!-- ========================================================================== -->
        <!-- THE SAVE BUTTON                                                            -->
        <!-- ========================================================================== -->
        <!--   `layout_height="60dp"` + `cornerRadius="30dp"` -> a pill shape.          -->
        <!--   `app:icon` -> the save icon, from the framework.                         -->
        <!--   `iconGravity="textStart"` -> the icon sits before the text.              -->
        <!--   The text is "Save Movie"; in edit mode, `ItemActivity` changes it to     -->
        <!--   "Update Movie" through `btMovieAction.setText(...)`.                     -->
        <!-- ========================================================================== -->
        <!-- Save -->
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

    </LinearLayout>
</ScrollView>
```

**The map of the widgets in the form — what each setter reads:**

| `Movie` field | Widget | ID | Read method |
|---|---|---|---|
| `title` | TextInputEditText | `etTitle` | `getText().toString()` |
| `release` | TextInputEditText + dialog | `etRelease` | `releaseCal.getTime()` |
| `genre` | Spinner | `spGenre` | `getSelectedItem().toString()` |
| `budget` | TextInputEditText | `etBudget` | `Double.parseDouble(...)` |
| `duration` | SeekBar | `sbDuration` | `getProgress()` |
| `rating` | RatingBar | `rbRating` | `getRating()` |
| `watched` | MaterialSwitch | `swWatched` | `isChecked()` |
| `approval` | RadioGroup | `rgApproval` | loop + `isChecked()` |
| `onWatchlist` | MaterialCheckBox | `cbOnWatchList` | `isChecked()` |
| `posterUrl` | TextInputEditText | `etPoster` | `getText().toString()` |

---

## 29.8 The complete flow

### 29.8.1 Starting the app

```
START
  AndroidManifest: intent-filter MAIN + LAUNCHER
    |
    v
  MainActivity.onCreate(savedInstanceState = null)
    |
    |== super.onCreate                 -> AppCompat installs its delegate
    |== EdgeToEdge.enable(this)         -> the windows draw under the bars
    |== setContentView(activity_main)   -> the view tree exists
    |== insets on R.id.main             -> padding = status bar + nav bar
    |== addSampleMovies()               -> movies = [Inception, Toy Story, The Matrix]
    |== new ArrayAdapter(this,
    |       android.R.layout.simple_list_item_1, movies)
    |                                   -> movieAdapter holds the REFERENCE to `movies`
    |== initControls()                  -> fabInsert, listView, setAdapter
    |== initListeners()                 -> FAB + item click (launcher is still null)
    +== registerForActivityResult(...)  -> launcher created
          |
          v
  ListView displays 3 rows:
    "Movie{title='Inception', release=..., genre='Sci-Fi', ..., onWatchlist=false}"
    "Movie{title='Toy Story', ...}"
    "Movie{title='The Matrix', ...}"
```

Note that the row does **not** contain the poster URL: the `toString()` in G1096 stops at `onWatchlist`.

### 29.8.2 Insert — FAB

```
PRESS FAB
  fabInsert.onClick
    |
    |== new Intent(MainActivity.this, ItemActivity.class)   (WITHOUT extras)
    +== launcher.launch(intent)
          |
          v
  MainActivity: onPause
  ItemActivity: onCreate
    |
    |== setContentView(activity_item)
    |== insets on R.id.main
    |== initControls()          -> 13 findViewById
    |== initListeners()         -> 4 listeners (before fillForm!)
    |== getIntent()             -> Intent without MOVIE_EXTRA
    +== existing == null        -> position stays -1, empty form
          |
          v
  THE USER FILLS IT IN AND PRESSES "Save Movie"
    |
    |== saveMovie()
    |     |== new Movie()
    |     |== 9 setters from the widgets
    |     |== loop over rgApproval -> the 10th setter
    |     |== Intent without a target
    |     |== putExtra(MOVIE_EXTRA, movie)
    |     |== (position == -1, so POSITION_EXTRA is NOT set)
    |     |== setResult(RESULT_OK, intent)
    |     +== finish()
    |
    v
  ItemActivity: onPause -> onStop -> onDestroy
  MainActivity: onStart -> onResume -> callback
    |
    |== resultCode == RESULT_OK ?
    |== intent = o.getData()
    |== movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA)   <- A COPY
    |== position = intent.getIntExtra(POSITION_EXTRA, -1)           -> -1
    |== movies.add(movie)
    +== movieAdapter.notifyDataSetChanged()
          |
          v
  ListView redraws -> the 4th row appears
```

### 29.8.3 Edit — click on a row

```
CLICK ON ROW 1
  listView.onItemClick(parent, view, position = 0, id = 0)
    |
    |== new Intent(MainActivity.this, ItemActivity.class)
    |== putExtra(MOVIE_EXTRA, movies.get(0))    <- SERIALIZATION
    |== putExtra(POSITION_EXTRA, 0)
    +== launcher.launch(intent)
          |
          v
  ItemActivity.onCreate
    |
    |== initControls() + initListeners()
    |== existing = IntentCompat.getSerializableExtra(intent, MOVIE_EXTRA, Movie.class)
    |                                                        <- a COPY, typed
    |== existing != null
    |     |== position = 0
    |     |== fillForm(existing)     -> 8 setters + 2 loops
    |     |     |== sbDuration.setProgress(...)  -> triggers onProgressChanged
    |     |     |== swWatched.setChecked(...)    -> triggers onCheckedChanged
    |     |     +== (that is why the listeners must be attached BEFORE)
    |     |== setTitle("Edit movie")            <- the ACTIVITY's method
    |     +== btMovieAction.setText("Update Movie")
    +== (the form shows the existing movie)
          |
          v
  THE USER CHANGES IT AND PRESSES "Update Movie"
    |
    |== saveMovie()
    |     |== new Movie() + 10 setters
    |     |== putExtra(MOVIE_EXTRA, movie)
    |     |== position != -1 -> putExtra(POSITION_EXTRA, 0)
    |     +== setResult + finish()
    |
    v
  MainActivity callback
    |== position = 0 (not -1)
    |== movies.set(0, movie)        <- REPLACEMENT, not addition
    +== notifyDataSetChanged()
          |
          v
  Row 1 is redrawn with the new data
```

### 29.8.4 The object that travels

```
MainActivity                          Intent / Bundle                ItemActivity
------------                          ---------------                ------------

movies: List<Movie>
  [0] Movie@A  ---------------------+
  [1] Movie@B                       |
  [2] Movie@C                       |
                                    |  putExtra("movie", Movie@A)
                                    v
                          serialize(Movie@A) -> bytes
                                    |
                                    v
                          Bundle { "movie" -> bytes,
                                   "position" -> 0 }
                                    |
                                    v
                          deserialize(bytes) -> Movie@A'
                                    |
                                    v
                                                       existing = Movie@A'
                                                       (a NEW object, a new address)
                                    |
                        fillForm(existing) reads
                        saveMovie() creates Movie@D
                                    |
                                    v
                          result Intent { "movie" -> Movie@D,
                                          "position" -> 0 }
                                    |
                                    v
                          movies.set(0, Movie@D)
                                    |
                                    v
                          Movie@A stays in the heap until GC
```

**The practical consequence:** the change in the form is not visible in the list until `movies.set(...)`. There is no "binding" between the object in the list and the one in the form — they are two distinct objects. If you changed `Movie@A'` and closed the activity with Back, `Movie@A` would stay unchanged.

### 29.8.5 The poster: stored, never displayed

```
  etPoster (textUri)
      |
      | getText().toString()
      v
  Movie.posterUrl  (String)
      |
      | putExtra -> serialize -> Bundle -> deserialize
      v
  Movie.posterUrl'  (String)
      |
      | toString()  -- does NOT include it
      | ImageView   -- does NOT exist
      | network     -- does NOT exist
      v
  (stays in the model, invisible)
```

Three proofs that the poster is never used as an image:

1. `Movie.toString()` does not include it — the row in the list does not show it.
2. `activity_item.xml` contains no `ImageView`.
3. `AndroidManifest.xml` contains no `<uses-permission android:name="android.permission.INTERNET" />`, and no Java file imports a network library.

So `posterUrl` is, at this stage, **a text field like any other**.

### 29.8.6 What happens on rotation

```
  Phone rotated 90°
    |
    v
  MainActivity: onPause -> onStop -> onDestroy   (the instance is THROWN AWAY)
    |
    v
  MainActivity: onCreate(savedInstanceState != null)
    |
    |== addSampleMovies()   -> movies = [Inception, Toy Story, The Matrix]
    |== ...                 -> the list returns to the 3 demo movies
    v
  The movies added by the user HAVE DISAPPEARED.
```

There is no `onSaveInstanceState(Bundle)` in `MainActivity`, so `movies` is not saved. It is a real limitation of the app, not a theory: add a movie, rotate the phone, the movie disappears.

The form has the same problem: `ItemActivity` does not save the state of the fields, so on rotation the form empties (or is refilled from the `Intent`, in edit mode).

---

## 29.9 What to remember from each file

| File | The essence | The trap |
|---|---|---|
| `Movie.java` | a serializable POJO, 10 fields, an explicit empty constructor **first**, `isX()` for booleans, `toString()` without the poster | the 10-parameter constructor is POSITIONAL; `posterUrl` not `poster` |
| `MainActivity.java` | the order in `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` | `launcher` is assigned AFTER `initListeners`; the list is lost on rotation |
| `ItemActivity.java` | 13 `findViewById` calls, `releaseCal` as the source of truth, a generic loop over the `RadioGroup`, `setResult` + `finish` | empty budget -> crash; the date is lost on edit; scientific notation |
| `AndroidManifest.xml` | two activities, correct `exported`, no permissions | `exported` mandatory since API 31; `Theme.G1096` is the only group difference |
| `activity_main.xml` | `FrameLayout` + the order of the children + `layout_gravity` on the FAB | `android:orientation` is invalid on FrameLayout |
| `activity_item.xml` | a `ScrollView` with one child, `MaterialCardView` as a section, `TextInputLayout`, a wrapped `Spinner` | `hintEnabled` must be correlated with the existence of the label; `tvTile` is a typo |

### The 10 things you will have been asked

1. **Why `implements Serializable`?** So that the object can be put in an `Intent` with `putExtra`.
2. **Is the object received the original?** No. It is a deserialized copy; that is why `MainActivity` does `movies.set(...)`.
3. **Why an explicit empty constructor?** A constructor with parameters suppresses the implicit constructor, and `saveMovie` does `new Movie()`. In G1096 it is the first in the class; in G1097, the last.
4. **Why `isWatched()`?** The JavaBeans convention for `boolean`.
5. **Why `notifyDataSetChanged()`?** ListView does not observe the list; the adapter must announce the change.
6. **Why `MainActivity.this`?** In the anonymous class, `this` is the listener, not the `Context`.
7. **Why `releaseCal` and not `etRelease`?** The calendar is the source of truth; the text can be invalid. **But** `fillForm` does not update it — BUG 2.
8. **Why is `fromUser` ignored?** The label must reflect the value also when it comes from `fillForm`, not only when the user drags.
9. **Why `0dp` + `weight`?** "Take all the remaining space", not "take the natural size".
10. **Why `?attr/` and not `@color/`?** `?attr/` is a theme role and adapts to dark mode.

### The differences you will have been asked about for G1096

1. **What is the poster field called?** `posterUrl`, with the accessors `getPosterUrl()` / `setPosterUrl(...)`.
2. **Which imports are dead in `MainActivity`?** `java.math.BigDecimal` and `android.widget.Toast`.
3. **Which import is dead in `ItemActivity`?** `android.widget.Switch` — and it would be dangerous if it were used, because `MaterialSwitch` is not a subclass of `Switch`.
4. **Where is the no-argument constructor?** First, at line 18, immediately after the fields.
5. **What is missing from `toString()`?** `posterUrl`.
6. **Which file is missing compared to G1097?** `movie_item.xml` — and no code used it.

---

## Chapter 29 summary

- The model does not touch the UI; the activities contain no row logic.
- `onCreate`: `super` -> `EdgeToEdge` -> `setContentView` -> insets -> data -> adapter -> controls -> listeners -> launcher.
- `releaseCal` is the source of truth for the date, **but `fillForm` does not update it** — the date is lost on edit.
- The loop over the `RadioGroup` makes the code generic — you add buttons in XML, the code sees them.
- `setResult(RESULT_OK, intent)` + `finish()` is the mandatory pair.
- `notifyDataSetChanged()` after any change to the list.
- `posterUrl` is stored as text and is never displayed: there is no `ImageView`, no network, no `INTERNET` permission.
- The list does not survive rotation: there is no `onSaveInstanceState`.
- Three real bugs: empty budget, date lost on edit, scientific notation.
- Compared to G1097: `posterUrl` instead of `poster`, the empty constructor first, `toString()` without the poster, other dead imports, no `movie_item.xml`.

**Back to** [cheatsheet](21%20-%20Cheatsheet.md) **or to** [the overview](index.html).
