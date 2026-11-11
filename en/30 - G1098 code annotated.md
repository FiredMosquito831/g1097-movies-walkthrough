# Chapter 30 — The G1098 code, annotated

**Objective:** to read every line of the G1098 app with the explanation glued to it — what it does, why it is there, what breaks if you remove it.

**Estimated time:** 90–120 min (active reading, with the project open alongside).

**Source:** `cod-final`, commit `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`.

**Rule:** the code is **unmodified, byte for byte**. Everything that appears with `//` or `<!-- -->` beyond the source is annotation.

---

## 30.0 What differs from G1097

The G1098 app is **functionally identical** to G1097: the same list, the same form, the same flow through `Intent`. The differences are in names, in order and in import hygiene. They are exactly the kind of difference that comes up on the test when you are asked to explain why two solutions that do the same thing look different.

| Aspect | G1098 | G1097 (reference) |
|---|---|---|
| The poster field in `Movie.java` | `private String posterUrl;` | `private String poster = null;` |
| Field initializer | none | `= null` |
| Position of the no-argument constructor | **after `toString()`**, before the getters (line 47) | last, after the setters (line 127) |
| Does `toString()` include the poster? | **YES** — `posterUrl` | yes, but as `poster` |
| `MainActivity.java` — unused imports | only `android.widget.Toast` | `java.util.Date` and `android.widget.Toast` |
| `MainActivity.java` — does it import `BigDecimal` or `Date`? | **neither** — the cleanest imports of all the groups | `Date` (unused) |
| `ItemActivity.java` — unused imports | **none** | `Switch`, `Toast`, `Snackbar`, `ActivityItemBinding` |
| `ItemActivity.java` — does it import `Switch`/`Toast`/`Snackbar`/`ActivityItemBinding`? | **none** | all four (all unused) |
| `activity_main.xml` | the FAB uses `@drawable/outline_add_2_24` | `@drawable/outline_add_24` |
| `activity_item.xml` | identical to G1097 | — |
| `AndroidManifest.xml` | identical to G1097 (only the theme differs: `Theme.G1098`) | `Theme.G1097` |
| `movie_item.xml` | **does not exist** | exists (prepared for S07, used by no code) |

### 30.0.1 The field is called `posterUrl`, not `poster`

Both groups have a tenth field of type `String` in `Movie`, in the same position in the 10-parameter constructor, with the same role: the address of the movie poster. Only the name differs.

The name does not stay in `Movie.java`, though. It propagates into **four** places:

```
Movie.java                          ItemActivity.java
-----------                         ------------------
private String posterUrl;           existing.getPosterUrl()      <- fillForm
public String getPosterUrl()        movie.setPosterUrl(...)      <- saveMovie
public void setPosterUrl(...)
```

**Why it matters:** if you paste a line from the G1097 code into a G1098 file, it will not compile. `existing.getPoster()` does not exist on a G1098 `Movie`, and neither does `movie.setPoster(...)`. The compiler catches you immediately — and that is exactly what you want from a rename.

**What you learn:** renaming a field is a refactor that the compiler checks in every place. That is why you rename with `Shift+F6` (Rename) in Android Studio, not with search and replace: the tool changes the getter, the setter and all the calls too.

### 30.0.2 The `= null` initializer is missing

G1098 writes `private String posterUrl;`. G1097 writes `private String poster = null;`.

**At runtime, the two are identical.** In Java, any reference field that is not initialized automatically receives `null` when the object is constructed. There is no "undefined value" as in C++.

**Why it still matters:** `= null` is **documentation**. It tells the reader: "this field can be absent; a movie without a poster is valid". The form without an initializer says nothing — the reader has to work out alone whether `null` is allowed or is an oversight.

**RISK:** both variants end up at `null`. If you call `.length()` or `.isEmpty()` on the value before it is set, you get a `NullPointerException`. It does not happen in the app: `fillForm` does `etPoster.setText(existing.getPosterUrl())`, and `setText(null)` is legal and shows an empty field.

**What you learn:** an explicit initialization to the default value is a comment, not a behaviour. Do not confuse the two when you read code.

### 30.0.3 The no-argument constructor sits after `toString()`

In G1098, the order of the members is:

```
line  6   class Movie
line  7   the 10 fields
line 18   Movie(10 parameters)
line 32   toString()
line 47   Movie()                 <- the empty constructor
line 50   getTitle() ... setPosterUrl()
```

In G1097, `Movie()` is the **last** method in the class, after the 20 getters and setters.

**The compiler has no preference.** The order of members in a Java class is free. The runtime is identical.

**Why it matters for the reader:** in G1098 you see **both** ways of creating a `Movie` next to each other — the 10-parameter constructor and the empty one — before you get into the 20 mechanical methods. In G1097 you have to scroll past 20 methods to find the empty constructor.

**What you learn:** the order of members is a reading contract. The healthy convention: fields, constructors, the display method, then the rest. G1098 follows it better than G1097, although both compile.

### 30.0.4 `toString()` includes the poster

G1098 prints `posterUrl='...'`. G1096 and G1099 **omit** the poster entirely. G1097 prints it, but under the name `poster`. So, of the four groups, only G1097 and G1098 have a complete `toString()`; G1098 is the only one that calls it `posterUrl`.

**Why it matters:** `ArrayAdapter` with `android.R.layout.simple_list_item_1` fills the row with `item.toString()`. So the poster URL **appears on the screen**, in the list. For a 60-character URL, the row becomes long and ugly — but the title and the rating come first, so the useful information stays visible.

**Why it is still worth it:** `toString()` is your debugging tool. `Log.d("MOVIE", movie.toString())` shows you all 10 fields. An incomplete `toString()` hides exactly the field you are looking for — and then you waste ten minutes believing the value was not set.

**RISK:** if the poster is `null`, the row contains `posterUrl='null'` — a text, not an error. The confusion comes when you think you saved the string `"null"`.

**What you learn:** `toString()` is a diagnostic contract. Completeness beats beauty.

### 30.0.5 `MainActivity` has a single dead import

G1098 imports `android.widget.Toast` and never uses it. G1097 has two dead imports: `java.util.Date` and `android.widget.Toast`.

**Why it matters:** an import does not reach the bytecode. It is an instruction for the compiler, resolved at compile time and then gone. It does not grow the APK, it loads nothing at runtime, it costs not a single millisecond.

The cost is **human**: the import suggests a dependency that does not exist. Whoever reads the file asks "where is the Toast shown?" and wastes time looking.

**What you learn:** an import is a statement. A false statement costs reading time, even if it costs nothing at runtime.

### 30.0.6 `MainActivity` imports neither `BigDecimal` nor `Date`

G1098 is the cleanest of all the groups when it comes to imports: apart from `Toast`, every import is used.

**Why it does not need `Date`:** the dates of the three demo movies are built like this:

```
new GregorianCalendar(2010, Calendar.JULY, 16).getTime()
```

`getTime()` returns a `Date`, but that `Date` is **consumed directly** as an argument in the `Movie` constructor. The type is written nowhere in the file, so no import is needed. You import for a **name** used in the code, not for a type that passes through an expression.

**Why it does not need `BigDecimal`:** the budget is a `double`, written as a literal (`160000000`). `BigDecimal` would only appear if you wrote `new BigDecimal("160000000")`.

**What you learn:** imports follow the identifiers actually written in the file. "This type appears somewhere in the call chain" is not a reason to import.

### 30.0.7 `ItemActivity` has no dead imports

G1098: all 30 imports are used. G1097: four dead imports — `android.widget.Switch`, `android.widget.Toast`, `com.google.android.material.snackbar.Snackbar` and `ActivityItemBinding`.

**Why `Switch` is dead everywhere:** all four groups declare in `ItemActivity`:

```
private MaterialSwitch swWatched;
```

`MaterialSwitch` is `com.google.android.material.materialswitch.MaterialSwitch`, not `android.widget.Switch`. Anyone who imports `android.widget.Switch` and then declares `MaterialSwitch` has an import that matches no name in the file. It is the classic test trap: the names look alike, the classes are different.

**Why `ActivityItemBinding` is dead:** it is the class generated by ViewBinding for `activity_item.xml`. It exists in the build, but G1097 does not use it in `ItemActivity` — the file works with `findViewById`.

**What you learn:** a file with no warnings is not luck, it is discipline. And `Switch` vs `MaterialSwitch` is the question that comes up on the test.

### 30.0.8 `outline_add_2_24` vs `outline_add_24`

In G1098's `res/drawable/` the file is called `outline_add_2_24.xml`. In G1097 it is called `outline_add_24.xml`. Both are 24dp "plus" vector icons, with the same viewport of 960 units, but with a different `pathData`: the plus in G1098 is drawn larger (from 120 to 840, that is, 720 units), the one in G1097 smaller (from 200 to 760, that is, 560 units). `_2_` marks the second variant of the same icon.

**Why it matters:** `@drawable/...` is resolved **at build time**, by AAPT2. The name is turned into an integer in `R.java`. If the resource is missing, the build fails with:

```
error: resource drawable/outline_add_2_24 (aka ro.ase.ie.g1098:drawable/outline_add_2_24) not found.
```

It is not a runtime crash. It is a compile error — the app does not even install.

**The practical consequence:** if you copy `activity_main.xml` into another project without copying the drawable too, the build fails. The solution is to copy both files, or to change the reference to a name that exists.

**What you learn:** references in XML are compile contracts. A wrong resource name shows up immediately, not after two test screens.

### 30.0.9 `activity_item.xml` is identical to G1097

The 452 lines are **byte-for-byte identical** to the form in G1097. The same four cards, the same IDs, the same styles, the same texts.

**Why it matters:** the form is the **stable** part of the app across groups. What varies from one group to another is the model (the field names) and the activities (imports, order). The layout is the same exercise copied by everyone.

**What you learn:** if you know `activity_item.xml` by heart from one group, you know it for all of them. The memorization effort is made once.

### 30.0.10 `AndroidManifest.xml` differs only in the theme

The only line that differs is:

```
android:theme="@style/Theme.G1098"
```

against `@style/Theme.G1097`. The activity names are relative to the package (`.activities.MainActivity`), so they contain neither "g1097" nor "g1098" in the text.

**Why it matters:** the manifest describes the app's **components**, not the code. It does not know what fields `Movie` has. That is why two apps with different models have identical manifests.

**What you learn:** when you change the group on the test, the manifest is the last place you should touch — and only at the theme.

### 30.0.11 G1098 has no `movie_item.xml`

G1097 has a `movie_item.xml` prepared for the next lab (RecyclerView), but **used by no code**. In the set of six files of this chapter, G1098 does not have it.

**Why it matters:** an unused layout changes nothing at runtime. It is not inflated, it consumes no memory, it does not appear on the screen. It is just a file in the project.

**What you learn:** its absence is not a regression. Both variants are correct; the difference is that G1097 shows you ahead of time what comes next.

### 30.0.12 The synthesis: what you learn from all the differences

| Difference | It is about | Does it show at runtime? | Does the compiler catch it? |
|---|---|---|---|
| `posterUrl` vs `poster` | names | no | **yes** |
| missing `= null` | documentation | no | no |
| constructor position | reading order | no | no |
| poster in `toString()` | diagnostics | **yes** (in the list) | no |
| dead imports | hygiene | no | no (lint only) |
| `outline_add_2_24` | resources | no | **yes** (build) |
| `movie_item.xml` absent | inventory | no | no |

The rule that ties them together: **the compiler checks names and resources, not intentions.** Everything that has to do with order, documentation and hygiene stays your job.

---

## 30.1 How to read this chapter

This is not an exercise chapter. It is a chapter of **reading with a magnifying glass**: you take each file of the app and go through it line by line, with the explanation right above.

- **Read the code first, the comment second.** Cover the comment block with your hand, say what the line does, then check.
- **The `THEORY` blocks** appear before each class and explain *why* the structure exists, not *how* it works.
- **The numbered blocks** ("1. Validation", "2. Cleanup") describe the steps of a method in execution order. The order is part of the lesson.
- **The `RISK:` and `BUG:` markers** flag the places where the code works today but can break, or where it already breaks.
- **The ASCII diagrams** show what you cannot see in the code: the object that travels between activities, the view hierarchy, the lifecycle.
- **Each file has exactly one code block**, whole. They are not fragments: you can read `ItemActivity.java` as a continuous document, from `package` to the last brace.
- **Do not memorize.** The goal is to be able to rebuild the file starting from a diagram.

---

## 30.2 `Movie.java` — the data model

The smallest file of the app and the only one that does not depend on Android. 129 lines, of which 20 are mechanical getters and setters.

```java
/*
 * ======================================================================================
 * FILE: Movie.java — THE DATA MODEL OF GROUP G1098
 * ======================================================================================
 * WHAT THIS FILE IS:
 *   A POJO class (Plain Old Java Object): 10 private fields, a constructor with 10
 *   parameters, an empty constructor, a toString() method and 20 getters/setters.
 *   Zero business logic. Zero android.* imports.
 *
 * WHY IT EXISTS:
 *   To carry a movie's data from one screen to another without depending on the UI.
 *   `MainActivity` holds a list of `Movie`; `ItemActivity` builds a `Movie`
 *   from the form's values and sends it back.
 *
 * WHO DEPENDS ON IT:
 *   - MainActivity: creates 3 demo movies and displays them through ArrayAdapter
 *   - ItemActivity: reads the fields in fillForm, writes them in saveMovie
 *   - Intent: serializes it with putExtra, because it implements Serializable
 *
 * WHAT IT DOES NOT DO:
 *   It validates nothing. It does not know what an EditText, a Spinner or an Intent is.
 *   It has no id: a movie's identity in the list is its POSITION, not a field.
 *   It does not format the date: formatting is the job of SimpleDateFormat in ItemActivity.
 *
 * WHAT BREAKS WITHOUT IT:
 *   The whole data flow. `Intent.putExtra` would have nothing to serialize, `ArrayAdapter`
 *   would have nothing to display, and `ItemActivity` would have to send 10 separate
 *   extras and reassemble them by hand in MainActivity.
 * ======================================================================================
 */

// ======================================================================================
// THE PACKAGE
// ======================================================================================
// `model` is the package that holds the DATA. `activities` holds the screens. The separation
// is not cosmetic: it allows Movie to be tested without an emulator, because it has no
// dependency on Android.
// ======================================================================================
package ro.ase.ie.g1098.model;

// ======================================================================================
// IMPORT 1: java.io.Serializable
// ======================================================================================
// WHAT IT IS: a MARKER interface — it has no method to implement.
// WHY HERE: `Intent.putExtra(String, Serializable)` is the simplest way to
//   send a whole object to another activity. Without `implements Serializable`,
//   the call `intent.putExtra(MOVIE_EXTRA, movie)` finds no matching
//   overload and does NOT COMPILE.
// WHAT HAPPENS AT RUNTIME: the JVM serializes the object graph into bytes, puts it
//   in a `Bundle`, and the receiving activity gets a DESERIALIZED COPY.
// RISK: without a declared `serialVersionUID`, the JVM computes one from the class structure.
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
//   format with `SimpleDateFormat` and you can compare two dates.
// WHY NOT `String`: you would store "16/07/2010" and lose the ability to compute.
//   `fillForm` would have to parse on every display, and `saveMovie` would have
//   to format on every save — two places where you can get the format wrong.
// WHY NOT `java.time.LocalDate`: it is newer and cleaner, but `Date` is
//   `Serializable` out of the box and it is the type required by the assignment statement.
// RISK: `Date` is MUTABLE. `getRelease()` returns the internal reference, not a copy,
//   so a careless caller can change the date in the object without going through the setter.
// ======================================================================================
import java.util.Date;

/*
 * ======================================================================================
 * WHAT EXACTLY HAPPENS ON SERIALIZATION
 * ======================================================================================
 *
 * 1. `putExtra(String, Serializable)` is checked at COMPILE time. If `Movie` did not
 *    implement the interface, the call would find no matching method.
 *
 * 2. At runtime, `ObjectOutputStream` writes into bytes:
 *      - the class name and `serialVersionUID`
 *      - every non-static and non-transient field, in declaration order
 *      - the references, as identifiers (a shared object is written only once)
 *
 * 3. `Date` is serializable, so `release` goes through without problems. If `Movie` held
 *    a `View`, a `Context` or a `Calendar`, serialization would throw
 *    `NotSerializableException`.
 *
 * 4. At the destination, `getSerializableExtra` rebuilds a NEW object graph.
 *    `Movie@A` in the list and `Movie@A'` in ItemActivity have the same content, but
 *    different addresses. `==` between them is `false`; `.equals` is not overridden,
 *    so still `false`.
 *
 * 5. `serialVersionUID` is missing. The JVM computes it from the class structure. In
 *    the same process, milliseconds pass between `putExtra` and `getSerializableExtra`,
 *    so the risk is nil. Between two versions of the app, the risk is real.
 * ======================================================================================
 */

/*
 * ======================================================================================
 * THEORY BLOCK: WHY A SEPARATE MODEL (POJO)
 * ======================================================================================
 *
 * 1. **Single Responsibility** — the class has a single reason to change: the structure
 *    of a movie's data changes. It does not change when a layout, a button
 *    or a colour changes. If you put `getText().toString()` here, the class would depend on
 *    `android.widget.EditText` and would have two reasons to change.
 *
 * 2. **Serializability** — being `Serializable` and with no references to `Context`,
 *    the object can cross the boundary between two activities. A `Movie` that held
 *    an `EditText` could not be serialized: `View` is not `Serializable`.
 *
 * 3. **Testability** — you can write a simple JVM test that creates a `Movie` and
 *    checks `getTitle()`. No emulator, no Android. That happens because
 *    the file contains no `import android.*`.
 *
 * 4. **No `id` field** — a movie's identity in the list is its POSITION, not an ID.
 *    The whole `POSITION_EXTRA` mechanism in the other two files comes from here.
 *    It is a didactic simplification: a real database would have a stable `id`.
 *
 * VISUAL: how the object travels between activities
 *
 *   [MainActivity]                      [Intent]                     [ItemActivity]
 *   movies.get(position)                                                  |
 *         |                                                               |
 *         +-- putExtra("movie", obj) --+                                  |
 *                                      |                                  |
 *                          serialize (JVM -> bytes)                      |
 *                                      |                                  |
 *                                      +-- Bundle -- startActivity --> --+
 *                                                                         |
 *                                                       getSerializableExtra(...)
 *                                                                         |
 *                                                          A COPY, not the original
 *
 *   The original stays in the list in MainActivity. Changes to the copy are NOT seen
 *   in the list. That is why MainActivity does `movies.set(position, movie)` at the end.
 * ======================================================================================
 */
public class Movie implements Serializable {

    // ==================================================================================
    // FIELD 1: title
    // ==================================================================================
    // TYPE: String — free text, of arbitrary length.
    // SOURCE WIDGET: `etTitle` (TextInputEditText) -> `getText().toString()`.
    // WHY String: the title is text, it has no numeric or date operations.
    // WHAT BREAKS IF IT IS WRONG: if it were `int`, "Inception" would not fit;
    //   if it were `char[]`, `ArrayAdapter` would display the array's address.
    // ==================================================================================
    private String title; //EditText

    // ==================================================================================
    // FIELD 2: release
    // ==================================================================================
    // TYPE: Date — a moment in time (here, only the day matters).
    // SOURCE WIDGET: `etRelease` + `DatePickerDialog`; it reaches the model from
    //   `releaseCal.getTime()`, NOT from the text in the EditText.
    // WHY Date: it allows formatting with `SimpleDateFormat` and comparison.
    // WHAT BREAKS IF IT IS WRONG: if it were `String`, `fillForm` would have to parse
    //   on every display, and a wrongly typed text would reach the model as it is.
    // ==================================================================================
    private Date release; //EditText date

    // ==================================================================================
    // FIELD 3: genre
    // ==================================================================================
    // TYPE: String — the text selected from the list ("Sci-Fi", "Animation", "Action").
    // SOURCE WIDGET: `spGenre` (Spinner) -> `getSelectedItem().toString()`.
    // WHY String and not `enum`: the genres come from `@array/movie_genre`, that is, from XML.
    //   With `enum`, adding a genre would require changing the Java code.
    // WHAT BREAKS IF IT IS WRONG: if you stored the position (`int`), changing the order
    //   in `arrays.xml` would retroactively change the genre of every saved movie.
    // ==================================================================================
    private String genre; //Spinner

    // ==================================================================================
    // FIELD 4: budget
    // ==================================================================================
    // TYPE: double — a number with decimals, precision of ~15–16 significant digits.
    // SOURCE WIDGET: `etBudget` (inputType=numberDecimal) -> `Double.parseDouble(...)`.
    // WHY double and not float: `float` has ~7 significant digits. For 160 000 000
    //   both are exact, but 160 000 001 would not be exactly representable in `float`.
    //   Besides, `Double.parseDouble` returns `double` — a `float` field would require a cast.
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
    // TYPE: float — the rating with half stars (0.0, 0.5, ..., 5.0).
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
    // WHY boolean: a switch's state is binary. `isChecked()` returns exactly that.
    // WHAT BREAKS IF IT IS WRONG: if it were `String` ("Yes"/"No"), every `if` would require
    //   a text comparison, and a lowercase "yes" would be treated as false.
    // WATCH OUT: the comment in the source says "Switch", but the real type is
    //   `MaterialSwitch`. `android.widget.Switch` is another class.
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
    //   no longer finds a match and checks nothing — silently.
    // WHAT BREAKS IF IT IS WRONG: if you stored the index (0..4), adding a button
    //   at the start of the group would change the meaning of every saved value.
    // ==================================================================================
    private String approval; //RadioGroup | RadioButtons

    // ==================================================================================
    // FIELD 9: onWatchlist
    // ==================================================================================
    // TYPE: boolean — true/false.
    // SOURCE WIDGET: `cbonWatchList` (MaterialCheckBox) -> `isChecked()`.
    // WHY boolean: a check box is binary. Independent of `watched`: you can have seen
    //   the movie AND keep it on the rewatch list.
    // WHAT BREAKS IF IT IS WRONG: if you reused `watched` for both, the two
    //   controls would contradict each other on save.
    // ==================================================================================
    private boolean onWatchlist; //Checkbox

    // ==================================================================================
    // FIELD 10: posterUrl
    // ==================================================================================
    // TYPE: String — a URL (or any text) to the movie poster.
    // SOURCE WIDGET: `etPoster` (inputType=textUri) -> `getText().toString()`.
    // THE DIFFERENCE FROM G1097: here the field is called `posterUrl` and does NOT have
    //   the `= null` initializer. The default value is still `null`; the difference is
    //   only in documentation. See 30.0.1 and 30.0.2.
    // RISK: `null` reaches `etPoster.setText(null)` on edit — legal, but it shows
    //   an empty field. If you called `.length()` on it, you would get a `NullPointerException`.
    // ==================================================================================
    private String posterUrl;

    // ==================================================================================
    // THE 10-PARAMETER CONSTRUCTOR
    // ==================================================================================
    // WHY IT EXISTS: `addSampleMovies()` in MainActivity creates the 3 demo movies
    //   in a single expression. Without it, there would be 10 setter calls per movie.
    //
    // THE TRAP: the order of the parameters is POSITIONAL. The names in the signature do not help
    //   at the call site — the compiler looks only at types and position.
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
    //   the code COMPILES. The movie is created. Only `title` receives the genre and
    //   `genre` receives the title. The compiler cannot help you here.
    // ==================================================================================
    public Movie(String title, Date release, String genre, double budget, int duration, float rating, boolean watched, String approval, boolean onWatchlist, String posterUrl) {

        // `this.title` = the class field; `title` = the parameter.
        // Without `this.`, the line would be `title = title` — self-assignment, the field stays null.
        this.title = title;

        // The same pattern for each of the 10 fields. All 10 lines
        // are structurally identical; if one is missing, the field keeps the
        // default value (null / 0 / 0.0 / false) and the bug only shows up on display.
        this.release = release;
        this.genre = genre;
        this.budget = budget;
        this.duration = duration;
        this.rating = rating;
        this.watched = watched;
        this.approval = approval;
        this.onWatchlist = onWatchlist;

        // The line that differs from G1097 only in the field name: `posterUrl`, not `poster`.
        this.posterUrl = posterUrl;
    }

    // ==================================================================================
    // toString() — THE DISPLAY CONTRACT IN THE LIST
    // ==================================================================================
    // WHY IT IS MANDATORY HERE:
    //   `ArrayAdapter` with `android.R.layout.simple_list_item_1` receives a `TextView`
    //   and fills it with `item.toString()`. Without an override, `Object.toString()` would
    //   return `ro.ase.ie.g1098.model.Movie@a1b2c3d` — the memory address.
    //
    // THE EXACT FLOW:
    //   ListView.getView(position) -> ArrayAdapter.getView(...) -> TextView.setText(
    //   movies.get(position).toString())
    //
    // WHY `@Override`: the compiler checks the signature. If you write `tostring()`
    //   with a lowercase letter, without the annotation you get no error — only your method
    //   is never called.
    //
    // THE FORMAT: generated by IntelliJ with Alt+Insert -> toString(). `'\''` is an
    //   escaped apostrophe, so it does not close the character literal.
    //
    // THE DIFFERENCE FROM G1096 AND G1099: `posterUrl` appears here too. The two groups
    //   omit the poster entirely. G1097 has it, but under the name `poster`.
    //
    // WHAT YOU SEE ON THE SCREEN: all 10 fields, on a single row, including the
    //   poster URL. Ugly, but correct. It is fixed in the next lab with RecyclerView.
    // ==================================================================================
    @Override
    public String toString() {

        // String concatenation with `+`. Each `+` creates a new object in memory.
        // For 10 fields, the difference is negligible; for large loops you would use
        // `StringBuilder`.
        return "Movie{" +

                // The text fields are wrapped in apostrophes, so the limits of the
                // value are visible: `title='Inception'`. Without them, `title=''` and `genre=''`
                // would be indistinguishable from an empty field.
                "title='" + title + '\'' +

                // `Date` is not wrapped in apostrophes: its `toString()` already produces
                // a readable format (`Sat Jul 16 00:00:00 GMT+03:00 2010`).
                ", release=" + release +

                // The comma at the start, not at the end: the last field needs no
                // separator, and `}` attaches correctly.
                ", genre='" + genre + '\'' +
                ", budget=" + budget +
                ", duration=" + duration +
                ", rating=" + rating +
                ", watched=" + watched +
                ", approval='" + approval + '\'' +
                ", onWatchlist=" + onWatchlist +

                // The last field: the poster. It is the only place in the app where the URL
                // appears on the screen, in the list row. If it were missing, `toString()` would
                // remain valid, but you would lose the field when debugging.
                ", posterUrl='" + posterUrl + '\'' +

                // The closing brace of the object, as text.
                '}';
    }

    // ==================================================================================
    // THE NO-ARGUMENT CONSTRUCTOR — THE POSITION THAT DIFFERS FROM G1097
    // ==================================================================================
    // WHY IT MUST BE WRITTEN EXPLICITLY:
    //   The Java rule: if you define ANY constructor with parameters, the compiler
    //   NO LONGER generates the no-argument constructor automatically.
    //   `saveMovie()` in ItemActivity does `Movie movie = new Movie();`.
    //   Without this constructor, the file does NOT COMPILE.
    //
    // WHY THE BODY IS EMPTY: all the fields receive the default values
    //   (null / 0 / 0.0 / false). The object is filled immediately with setters.
    //
    // WHY IT IS HERE AND NOT AT THE END: the position does not matter to the compiler.
    //   In G1098 it sits right after `toString()`, so the reader sees both
    //   constructors before the 20 mechanical methods. In G1097 it is the last one.
    // ==================================================================================
    public Movie() {
    }

    // ==================================================================================
    // GETTERS AND SETTERS — 20 METHODS, ALL MECHANICAL
    // ==================================================================================
    // WHY THEY EXIST: the fields are `private`. Code from other packages (and even from
    //   `activities`) cannot read or write them directly. The getters and setters
    //   are the only interface.
    //
    // WHY SO MANY: 10 fields x 2 = 20. They are generated automatically by IntelliJ
    //   (Alt+Insert -> Getter and Setter). You do not write them by hand on the test.
    //
    // THE NAMING CONVENTION:
    //   - `getX()` for objects and primitives, EXCEPT for boolean;
    //   - `isX()` for boolean — the JavaBeans convention.
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
    // by the model and only crashes in `fillForm`, at `dateFormat.format(null)`.
    public void setRelease(Date release) {
        this.release = release;
    }

    // GETTER for the genre. The value comes from the Spinner, but the model does not know that.
    public String getGenre() {
        return genre;
    }

    // SETTER for the genre. It does not check whether the value exists in `@array/movie_genre`.
    // Validation is the UI's responsibility, not the model's.
    public void setGenre(String genre) {
        this.genre = genre;
    }

    // GETTER for the budget. `double` is copied by value — there are no
    // aliasing problems as with Date.
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

    // GETTER for the rating. `float` — the rating with half stars.
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
    //    wrote `getWatched()`, the call does not compile — and it must be changed in two places.
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

    // SETTER for the guidance. The value is the radio button's text, not its ID.
    public void setApproval(String approval) {
        this.approval = approval;
    }

    // GETTER for the "Watchlist" check box. `is` prefix — again the JavaBeans convention.
    public boolean isOnWatchlist() {
        return onWatchlist;
    }

    // SETTER for the check box.
    public void setOnWatchlist(boolean onWatchlist) {
        this.onWatchlist = onWatchlist;
    }

    // GETTER for the poster URL. It can return `null`.
    // THE NAME: `getPosterUrl`, not `getPoster` — here you see the difference from G1097.
    //   `fillForm` in ItemActivity calls exactly this name.
    public String getPosterUrl() {
        return posterUrl;
    }

    // SETTER for the poster. It accepts `null` without complaining.
    // `saveMovie` calls `movie.setPosterUrl(etPoster.getText().toString())`.
    public void setPosterUrl(String posterUrl) {
        this.posterUrl = posterUrl;
    }
}
```

**Reference table — the 10 fields and their pair in the UI:**

| # | Field | Type | Getter | Setter | Widget |
|---|---|---|---|---|---|
| 1 | `title` | `String` | `getTitle()` | `setTitle()` | `etTitle` |
| 2 | `release` | `Date` | `getRelease()` | `setRelease()` | `etRelease` + dialog |
| 3 | `genre` | `String` | `getGenre()` | `setGenre()` | `spGenre` |
| 4 | `budget` | `double` | `getBudget()` | `setBudget()` | `etBudget` |
| 5 | `duration` | `int` | `getDuration()` | `setDuration()` | `sbDuration` |
| 6 | `rating` | `float` | `getRating()` | `setRating()` | `rbRating` |
| 7 | `watched` | `boolean` | `isWatched()` | `setWatched()` | `swWatched` |
| 8 | `approval` | `String` | `getApproval()` | `setApproval()` | `rgApproval` |
| 9 | `onWatchlist` | `boolean` | `isOnWatchlist()` | `setOnWatchlist()` | `cbOnWatchList` |
| 10 | `posterUrl` | `String` | `getPosterUrl()` | `setPosterUrl()` | `etPoster` |

**The three things that can be asked from this file:**

1. **Why `implements Serializable`?** So that it can be put into an `Intent` with `putExtra`.
2. **Is the object received in `ItemActivity` the original?** No. It is a deserialized copy.
3. **Why an explicit empty constructor?** A constructor with parameters suppresses the implicit constructor, and `saveMovie` does `new Movie()`.

---

## 30.3 `MainActivity.java` — the list and the navigation

The start screen. 145 lines, half of which are imports and signatures. The file that **owns the state** of the app: the `movies` list.

```java
/*
 * ======================================================================================
 * FILE: MainActivity.java — THE SCREEN WITH THE LIST
 * ======================================================================================
 * WHAT IT IS: the start activity. It holds the movie list, displays it with an `ArrayAdapter`
 *   in a `ListView` and starts `ItemActivity` for insert or edit.
 *
 * WHY IT EXISTS: it is the only place that owns the app's STATE (the `movies` list).
 *   `ItemActivity` is just a form that produces a `Movie` and sends it back.
 *
 * WHAT IT KNOWS: the list, the adapter, the two extras, the result launcher.
 *   It does not know what the form looks like and it does not validate data.
 *
 * WHAT IT DOES NOT DO: it saves nothing to disk. The list lives as long as the process lives.
 *   When the screen rotates, the activity is recreated and `addSampleMovies()` runs
 *   again — the added movies are lost. Persistence comes in the next lab.
 *
 * WHAT BREAKS WITHOUT IT: the app would start straight into a form with no list,
 *   and the saved result would have nowhere to return to.
 * ======================================================================================
 */

// ======================================================================================
// THE PACKAGE
// ======================================================================================
// `activities` holds the screens. The model sits in `model`, and `R` in the root of the package.
// ======================================================================================
package ro.ase.ie.g1098.activities;

// ======================================================================================
// IMPORTS — GROUPED BY SOURCE
// ======================================================================================
// android.*        — framework classes (Intent, Bundle, View, widgets)
// androidx.*       — Jetpack libraries (AppCompat, EdgeToEdge, insets, activity result)
// com.google.*     — Material Components (FloatingActionButton)
// java.util.*      — collections and dates
// ro.ase.ie.g1098  — the model and the generated R class
//
// HYGIENE NOTE: the only unused import in the file is `android.widget.Toast`.
//   G1097 has one more: `java.util.Date`. Both are harmless at runtime — an import
//   does not reach the bytecode — but it suggests a dependency that does not exist.
// ======================================================================================

// Intent: the object that describes "which activity you start" and what data it carries.
import android.content.Intent;

// Bundle: the saved-state bag the system keeps (used here only in the onCreate signature).
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
//   It is the only dead import of group G1098 in MainActivity.
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

// AppCompatActivity: the base activity with support for Material themes and the ActionBar.
import androidx.appcompat.app.AppCompatActivity;

// Insets: the pixel values of the bars that cover the content.
import androidx.core.graphics.Insets;

// ViewCompat: the compatible version of the View APIs (insets on any API).
import androidx.core.view.ViewCompat;

// WindowInsetsCompat: the description of the insets, independent of the Android version.
import androidx.core.view.WindowInsetsCompat;

// FloatingActionButton: the round button in the bottom-right corner.
import com.google.android.material.floatingactionbutton.FloatingActionButton;

// ArrayList: the concrete implementation of the list.
import java.util.ArrayList;

// Calendar: the date fields (YEAR, MONTH, DAY_OF_MONTH) and the month constants.
import java.util.Calendar;

// GregorianCalendar: the date constructor used in addSampleMovies.
//   `new GregorianCalendar(year, month, day).getTime()` produces a `Date` directly.
import java.util.GregorianCalendar;

// List: the declared type of the `movies` field (the interface, not the implementation).
import java.util.List;

// R: the build-generated class that maps the names from XML to integers.
import ro.ase.ie.g1098.R;

// Movie: the data model.
import ro.ase.ie.g1098.model.Movie;

/*
 * ======================================================================================
 * THEORY BLOCK: WHO HOLDS THE STATE AND WHO DISPLAYS IT
 * ======================================================================================
 *
 * 1. **A single owner of the list.** `movies` is `final` and is the only list
 *    in the app. `ItemActivity` has no list; it receives a `Movie` and returns a
 *    `Movie`. The "single source of truth" rule prevents lists that contradict each other.
 *
 * 2. **The adapter does not copy the list.** `new ArrayAdapter<>(this, layout, movies)` receives
 *    the REFERENCE to the list. The adapter reads from it on every `getView`. That is why
 *    `movies.add(...)` is seen immediately in the adapter — but the ListView does not redraw
 *    until after `notifyDataSetChanged()`.
 *
 * 3. **The order in onCreate is a contract.** `addSampleMovies()` must run
 *    before the adapter is created, so the list has content on the first bind.
 *    `initControls()` must run before `initListeners()`, so that
 *    `fabInsert` and `listView` are already bound when listeners are put on them.
 *
 * 4. **The launcher is registered in onCreate, not in a listener.** `registerForActivityResult`
 *    must be called before the activity reaches the STARTED state. Called from an
 *    `onClick`, it would throw `IllegalStateException`.
 *
 * THE LIFECYCLE, IN SHORT:
 *
 *   onCreate  -> super, EdgeToEdge, setContentView, insets, data, adapter,
 *                controls, listeners, launcher
 *   onStart   -> the activity becomes visible
 *   onResume  -> receives input
 *   onPause   -> loses input (ItemActivity appears on top of it)
 *   onStop    -> it is no longer visible
 *   onDestroy -> destroyed (rotation, back, process killed)
 *
 *   On returning from ItemActivity: onStart -> onResume -> the launcher's callback.
 * ======================================================================================
 */
public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // THE EXTRA KEYS — THE CONTRACT BETWEEN THE TWO ACTIVITIES
    // ==================================================================================
    // `protected static final`: `static` because it does not depend on an instance, `protected`
    //   so that it is visible from ItemActivity (the same `activities` package), `final`
    //   because the value never changes.
    // THE VALUE is an arbitrary String: "position" and "movie". The convention is that it be
    //   unique in the app; otherwise two extras with the same key overwrite each other.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";

    // The "+" button. The concrete type is FloatingActionButton, not View: we need
    // only setOnClickListener, which exists on any View, but the concrete type
    // documents what widget it is.
    private FloatingActionButton fabInsert;

    // The scrollable list.
    private ListView listView;

    // The result launcher. It is assigned in onCreate, AFTER initListeners().
    // `ActivityResultLauncher<Intent>`: starts an Intent and returns an ActivityResult.
    private ActivityResultLauncher<Intent> launcher;

    // THE LIST — the app's state. `final` means the reference does not change;
    // the content, yes. `List` is the interface; `ArrayList` is the implementation.
    // Initialization at the declaration guarantees the list exists before any method.
    private final List<Movie> movies = new ArrayList<>();

    // The adapter. It is created in onCreate, after the list already has the 3 demo movies.
    private ArrayAdapter<Movie> movieAdapter;

    /*
     * ==============================================================================
     * THEORY BLOCK: ACTIVITY RESULT API
     * ==============================================================================
     *
     * 1. Before AndroidX Activity 1.2, the result was taken with:
     *      startActivityForResult(intent, REQUEST_CODE);
     *      onActivityResult(requestCode, resultCode, data)
     *    Both are DEPRECATED. The problem: the request code was a global `int`, easy
     *    to duplicate, and the `onActivityResult` method grew with a `switch` for
     *    every activity started.
     *
     * 2. The new API binds a CALLBACK to a CONTRACT, once:
     *      launcher = registerForActivityResult(contract, callback)
     *      launcher.launch(intent)
     *
     * 3. `StartActivityForResult` is the generic contract: it receives an `Intent` and
     *    returns an `ActivityResult` (code + Intent).
     *
     * 4. The registration must be done in `onCreate`, before the STARTED state.
     *    A `launcher` registered too late throws `IllegalStateException`.
     *
     * 5. The callback runs on the UI thread, after `onResume`, when the activity is
     *    visible again. That is why `notifyDataSetChanged()` is safe there.
     * ==============================================================================
     */

    // ==================================================================================
    // onCreate — THE PLACE WHERE THE SCREEN IS BUILT
    // ==================================================================================
    // WHAT IT DOES: binds the layout, populates the list, creates the adapter, binds the widgets,
    //   installs the listeners and registers the result launcher.
    // HOW: in the order below. The order is part of the lesson.
    // RISK: if `initListeners()` ran before `initControls()`, `fabInsert`
    //   would be `null` and `setOnClickListener` would throw `NullPointerException`.
    // REF: the same skeleton in all the groups; chapter 22, section 22.2.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. The chain to the superclass. MANDATORY first: AppCompatActivity does its
        //    internal initialization (theme, fragment manager, saved state) here.
        //    If you move it lower, you get exceptions that are hard to diagnose.
        super.onCreate(savedInstanceState);

        // 2. Edge-to-edge: the content is drawn under the status bar and under the
        //    navigation bar. Without step 4, the first rows would sit under the clock.
        EdgeToEdge.enable(this);

        // 3. The layout. `R.layout.activity_main` is the ID generated for the file
        //    `res/layout/activity_main.xml`. From here on, `findViewById` can
        //    find the widgets.
        setContentView(R.layout.activity_main);

        // 4. Insets: we measure the system bars and turn them into padding on the root.
        //    `findViewById(R.id.main)` is the FrameLayout from the XML — that is why the ID
        //    `main` is mandatory there.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. How much the system bars take, in pixels.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Padding on all four sides. This way the content starts under
            //     the status bar and ends above the navigation bar.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. `return insets` = "I consumed nothing"; the children receive it further.
            return insets;
        });

        // 5. The demo data. It must run BEFORE the adapter is created,
        //    so the list has content on the first bind.
        addSampleMovies();

        // 6. The adapter. `android.R.layout.simple_list_item_1` is a layout from
        //    the framework: a single TextView. `this` is the Context required by the constructor.
        //    The third argument is the list — the adapter keeps the REFERENCE, not a copy.
        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

        // 7. Binding the widgets to the fields.
        initControls();

        // 8. Installing the listeners. It runs after initControls, so the widgets
        //    are already non-null.
        initListeners();

        // 9. The result launcher. It is registered ONCE, in onCreate.
        //    `StartActivityForResult` is the contract that says: "I start an activity
        //    and I want a result back".
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // The callback: an anonymous class that implements a single method.
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // 9a. We check the code. `RESULT_OK` means that ItemActivity
                        //     called `setResult(RESULT_OK, intent)`. If the user
                        //     pressed Back, the code is `RESULT_CANCELED` and we do nothing.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // 9b. The result Intent. It can theoretically be `null`, but
                            //     ItemActivity always sends it when the code is OK.
                            Intent intent = o.getData();

                            // 9c. We take the object out. `getSerializableExtra` returns
                            //     `Serializable`, so the cast to `Movie` is mandatory.
                            //     The object is A DESERIALIZED COPY, not the original.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // 9d. The position. A missing extra means insert, that is, -1.
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // 9e. The INSERT branch: the position is missing.
                            if(position == -1)
                            {
                                // We add at the end of the list.
                                movies.add(movie);

                                // We notify the adapter. Without this call, the ListView does not
                                // know the list has a new element and does not redraw.
                                movieAdapter.notifyDataSetChanged();
                            }
                            // 9f. The EDIT branch: the position exists.
                            else
                            {
                                // REPLACEMENT, not addition. `set` keeps the order.
                                movies.set(position, movie);

                                // Here too a notification is needed.
                                movieAdapter.notifyDataSetChanged();
                            }
                        }
                    }
                });
    }

    // ==================================================================================
    // initListeners — WHAT HAPPENS ON A PRESS
    // ==================================================================================
    // WHAT IT DOES: installs two listeners — one on the FAB (insert), one on the list row
    //   (edit).
    // HOW: `setOnClickListener` on the FAB; `setOnItemClickListener` on the ListView.
    // RISK: the listeners are anonymous classes. Inside them, `this` is NOT
    //   MainActivity, but the listener object. That is why you write `MainActivity.this`.
    // REF: chapter 22, section 22.2.
    // ==================================================================================
    private void initListeners() {

        // 1. FAB -> empty form (insert).
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // EXPLICIT Intent: (Context, Class). The second argument is the class
                // of the activity to start. An implicit Intent would look for
                // an app that knows how to do something, not our class.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // Starting through the launcher, not through `startActivityForResult` (deprecated).
                // The launcher knows which callback to call on return.
                launcher.launch(intent);
            }
        });

        // 2. Click on a row -> filled form (edit).
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                // 2a. The same explicit Intent.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // 2b. The object that travels. `movies.get(position)` is the movie
                //     on the pressed row. Serialization happens automatically.
                intent.putExtra(MOVIE_EXTRA, movies.get(position));

                // 2c. The position, so ItemActivity knows what to replace on return.
                intent.putExtra(POSITION_EXTRA, position);

                // 2d. Start.
                launcher.launch(intent);
            }
        });
    }

    // ==================================================================================
    // initControls — FINDVIEWBYID
    // ==================================================================================
    // WHAT IT DOES: binds the two widgets to fields and installs the adapter on the list.
    // HOW: `findViewById` with the ID from the XML; then `setAdapter`.
    // RISK: `findViewById` returns `null` if the ID does not exist in the layout that was set.
    //   A wrong ID gives no compile error — it gives a `NullPointerException` at runtime.
    // REF: `R.id.floatingActionButton` and `R.id.listView` from `activity_main.xml`.
    // ==================================================================================
    private void initControls() {

        // The ID in the XML is `floatingActionButton`, and the field is called `fabInsert`.
        // The names do not have to match; only the ID in `R.id` matters.
        fabInsert = findViewById(R.id.floatingActionButton);

        // The list.
        listView = findViewById(R.id.listView);

        // The adapter is installed on the list. From this moment, the ListView asks
        // the adapter what to display on each row.
        listView.setAdapter(movieAdapter);
    }

    // ==================================================================================
    // addSampleMovies — THE DEMO DATA
    // ==================================================================================
    // WHAT IT DOES: adds three movies to the list, so the screen is not empty on first launch.
    // HOW: three calls of the 10-parameter constructor.
    // RISK: the order of the arguments is POSITIONAL. Here there are 3 Strings and 2 booleans,
    //   so swapping them compiles. Check the table in 30.2.
    // REF: the `Movie(...)` constructor from `Movie.java`.
    // ==================================================================================
    private void addSampleMovies() {

        // MOVIE 1 — Inception.
        // `new GregorianCalendar(year, month, day)`: the month is 0-based! `Calendar.JULY` = 6,
        // not 7. `.getTime()` turns Calendar into Date, the type required by the constructor.
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
                "https://example.com/posters/inception.jpg"));

        // MOVIE 2 — Toy Story.
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

        // MOVIE 3 — The Matrix.
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
}
```

### 30.3.1 The order in `onCreate` — why it cannot be changed

```
onCreate
  |
  |-- 1. super.onCreate(savedState)        <- without it, AppCompat is not initialized
  |-- 2. EdgeToEdge.enable(this)           <- content under the system bars
  |-- 3. setContentView(activity_main)     <- from here on there are views
  |-- 4. insets pe R.id.main               <- padding on the root
  |-- 5. addSampleMovies()                 <- the list has content
  |-- 6. movieAdapter = new ArrayAdapter   <- the adapter receives the list
  |-- 7. initControls()                    <- fabInsert + listView + setAdapter
  |-- 8. initListeners()                   <- listeners on non-null objects
  +-- 9. launcher = registerForActivityResult(...)
```

**Why `launcher` is last:** the listeners installed at step 8 contain `launcher.launch(...)`. If you called `launcher.launch` before `launcher` was assigned, you would get a `NullPointerException`. In practice it cannot happen: no click can reach the listener until `onCreate` has finished and the screen is drawn.

**Why `registerForActivityResult` cannot sit in a listener:** the registration must be done before the activity reaches the `STARTED` state. An `onClick` runs long after that, and Android throws `IllegalStateException: LifecycleOwner is attempting to register while current state is RESUMED`.

### 30.3.2 What happens on returning from `ItemActivity`

```
ItemActivity: setResult(RESULT_OK, intent) + finish()
      |
      v
MainActivity: onStart -> onResume
      |
      v
ActivityResultRegistry delivers the result
      |
      v
onActivityResult(ActivityResult o)
      |
      |-- o.getResultCode() == RESULT_OK ?
      |        |
      |        +-- NO  -> nothing (the user pressed Back)
      |        |
      |        +-- YES -> intent = o.getData()
      |                   movie = (Movie) getSerializableExtra("movie")
      |                   position = getIntExtra("position", -1)
      |                        |
      |                        +-- -1  -> movies.add(movie)
      |                        +-- >=0 -> movies.set(position, movie)
      |                        |
      |                        +-- movieAdapter.notifyDataSetChanged()
      v
ListView redraws the visible rows
```

**RISK:** if you forget `notifyDataSetChanged()`, the list in memory changes, but the screen stays unchanged until the next redraw (rotation, scrolling). It is the most frequent "invisible" bug in apps that use a `ListView`.

### 30.3.3 `MainActivity.this` vs `this`

```
Outside the anonymous class:    Inside `new View.OnClickListener() { ... }`:
-----------------------------   ------------------------------------------------
this          = MainActivity     this          = OnClickListener
MainActivity.this = MainActivity MainActivity.this = MainActivity
```

The `Intent(Context, Class)` constructor requires a `Context`. `MainActivity` **is** a `Context` (it extends `AppCompatActivity` -> `Context`), but `OnClickListener` is not. That is why you write `MainActivity.this`.

---

## 30.4 `ItemActivity.java` — the form

The largest Java file of the app: 218 lines, 13 widgets, 4 listeners and two methods that do all the work (`fillForm`, `saveMovie`). It is also the file with **zero dead imports** — the cleanest of all the groups.

```java
/*
 * ======================================================================================
 * FILE: ItemActivity.java — THE INSERT AND EDIT FORM
 * ======================================================================================
 * WHAT IT IS: the second activity. It shows a form with 13 controls, reads the values
 *   and packs them into a `Movie`, which it sends back to MainActivity.
 *
 * WHY IT EXISTS: MainActivity holds the list, but has no room on the screen for a form.
 *   Splitting into two activities is the classic "list + detail" pattern.
 *
 * WHAT IT KNOWS: the 13 widgets, a `Calendar` that is the source of truth for the date,
 *   a `SimpleDateFormat`, the position in the list (-1 = insert) and the extra keys.
 *
 * WHAT IT DOES NOT DO: it does not hold the list, it does not know what is before or after
 *   the edited movie, it does not save anything to disk. It produces a `Movie` and hands it over.
 *
 * WHAT BREAKS WITHOUT IT: the "+" button would open a non-existent activity, and
 *   a click on a row would throw `ActivityNotFoundException`.
 * ======================================================================================
 */

// ======================================================================================
// THE PACKAGE
// ======================================================================================
// The same package as MainActivity: `activities`. That is why `MainActivity.MOVIE_EXTRA`
// is visible here without an import — `protected` + the same package.
// ======================================================================================
package ro.ase.ie.g1098.activities;

// ======================================================================================
// IMPORTS — ALL USED
// ======================================================================================
// The difference from G1097: there were four dead imports there (`Switch`, `Toast`,
// `Snackbar`, `ActivityItemBinding`). Here every import corresponds to a name written
// in the file. The check is mechanical: look for the name in the body of the class.
// ======================================================================================

// DatePickerDialog: the date picker dialog.
import android.app.DatePickerDialog;

// Intent: the object we put the result in.
import android.content.Intent;

// Bundle: only in the onCreate signature.
import android.os.Bundle;

// View: the type of the onClick parameter and the base class of the widgets.
import android.view.View;

// Button: the "Save Movie" / "Update Movie" button.
import android.widget.Button;

// CheckBox: the "Watchlist" check box. The declared type is CheckBox, although the widget in the XML
//   is MaterialCheckBox — which extends CheckBox.
import android.widget.CheckBox;

// CompoundButton: the interface for switch/checkbox; `OnCheckedChangeListener` lives here.
import android.widget.CompoundButton;

// DatePicker: the parameter in onDateSet.
import android.widget.DatePicker;

// EditText: title, date, budget, poster.
import android.widget.EditText;

// RadioButton: the buttons in the guidance group.
import android.widget.RadioButton;

// RadioGroup: the container that guarantees the single selection.
import android.widget.RadioGroup;

// RatingBar: the stars.
import android.widget.RatingBar;

// SeekBar: the duration slider.
import android.widget.SeekBar;

// Spinner: the genre list.
import android.widget.Spinner;

// TextView: the two dynamic labels (the duration and the switch's value).
import android.widget.TextView;

// EdgeToEdge: drawing under the system bars.
import androidx.activity.EdgeToEdge;

// NonNull: an annotation on the onCheckedChanged parameter. It does not change behaviour;
//   it documents that Android guarantees a non-null object.
import androidx.annotation.NonNull;

// AppCompatActivity: the base class.
import androidx.appcompat.app.AppCompatActivity;

// IntentCompat: a compatible variant of `getSerializableExtra`, with an explicit type.
import androidx.core.content.IntentCompat;

// Insets / ViewCompat / WindowInsetsCompat: the same as in MainActivity.
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

// MaterialSwitch: the Material switch. NOT `android.widget.Switch` — that is another class.
import com.google.android.material.materialswitch.MaterialSwitch;

// ParseException: the exception thrown by `SimpleDateFormat.parse`.
import java.text.ParseException;

// SimpleDateFormat: the Date <-> String conversion.
import java.text.SimpleDateFormat;

// Calendar: the date fields and the source of truth for release.
import java.util.Calendar;

// Date: the type returned by `releaseCal.getTime()` and by `dateFormat.parse(...)`.
import java.util.Date;

// Locale: the regional format for dates.
import java.util.Locale;

// R and Movie.
import ro.ase.ie.g1098.R;
import ro.ase.ie.g1098.model.Movie;

/*
 * ======================================================================================
 * THEORY BLOCK: THE FORM AS A STATE MACHINE
 * ======================================================================================
 *
 * 1. **Two modes, a single activity.** `position == -1` means INSERT;
 *    `position >= 0` means EDIT. There are no two separate activities, because
 *    the form is identical; only the initial values and the button label differ.
 *
 * 2. **The widgets are the source of truth for 9 fields, Calendar for one.**
 *    The title is read from `etTitle`, the budget from `etBudget` etc. The date is NOT read
 *    from `etRelease`: the text is only a DISPLAY, the real value sits in `releaseCal`.
 *
 *        [etRelease]  --(display)-->  "16/07/2010"
 *        [releaseCal] --(value)-->  Date  --> saveMovie() --> Movie
 *
 * 3. **The result goes back through an Intent.** `setResult(RESULT_OK, intent)` +
 *    `finish()` is the mandatory pair. Without `finish()`, the activity stays
 *    open; without `setResult`, MainActivity receives `RESULT_CANCELED`.
 *
 * 4. **Validation is missing.** The form checks nothing: an empty budget crashes,
 *    a null date crashes, an unmarked guidance leaves `approval` null. They are real bugs,
 *    marked below with `BUG:`.
 *
 * WHAT HAPPENS ON EACH PRESS:
 *
 *   etRelease click      -> showReleaseDatePicker() -> dialog -> releaseCal + text
 *   btnMovieAction click -> saveMovie() -> Intent -> setResult -> finish
 *   swWatched toggle     -> tvWatchedValue.setText("Yes"/"No")
 *   sbDuration drag      -> tvDurationValue.setText(progress + " min.")
 * ======================================================================================
 */
public class ItemActivity extends AppCompatActivity {

    // ==================================================================================
    // THE 13 WIDGETS — fields, bound in initControls()
    // ==================================================================================
    // They are all `private`: nobody from outside is allowed to touch them. All are
    //   bound with `findViewById` in the same method, so an ID mistake is
    //   visible in a single place.
    // ==================================================================================

    // 1. The title — TextInputEditText.
    private EditText etTitle;

    // 2. The date — TextInputEditText, but it is NOT read from it (see releaseCal).
    private EditText etRelease;

    // 3. The genre — Spinner with `@array/movie_genre`.
    private Spinner spGenre;

    // 4. The budget — TextInputEditText with inputType=numberDecimal.
    private EditText etBudget;

    // 5. The duration — SeekBar 0..300.
    private SeekBar sbDuration;

    // 6. Rating — RatingBar with 5 stars and a step of 0.5.
    private RatingBar rbRating;

    // 7. The guidance — RadioGroup with 5 buttons.
    private RadioGroup rgApproval;

    // 8. The Watchlist check box — ID `cbOnWatchList`, field `cbonWatchList`.
    private CheckBox cbonWatchList;

    // 9. The switch — MaterialSwitch, NOT android.widget.Switch.
    private MaterialSwitch swWatched;

    // 10. The poster — TextInputEditText with inputType=textUri.
    private EditText etPoster;

    // 11. The action button — "Save Movie" or "Update Movie".
    private Button btMovieAction;

    // 12. The label that shows the current duration.
    private TextView tvDurationValue;

    // 13. The label that shows "Yes"/"No" for the switch.
    private TextView tvWatchedValue;

    // ==================================================================================
    // THE STATE OF THE FORM
    // ==================================================================================

    // THE MODE: -1 = insert, >= 0 = edit.
    // WHY `-1` and not `0`: `0` is a valid position in the list. The sentinel must
    //   be a value IMPOSSIBLE as a position.
    // WHO CHANGES IT: only `onCreate`, when it finds a movie in the Intent.
    private int position = -1;   // -1 = insert mode

    // THE SOURCE OF TRUTH FOR THE DATE.
    // `Calendar.getInstance()` = the CURRENT date and time. That is why the form starts
    //   with today's date, not with an empty date.
    // WHY NOT `null`: `saveMovie` calls `releaseCal.getTime()` unconditionally.
    //   A `null` would throw an NPE on the first save.
    // WHY `Calendar` and not `Date`: `Calendar` has fields (YEAR, MONTH, DAY_OF_MONTH)
    //   that `DatePickerDialog` reads and writes directly.
    private Calendar releaseCal = Calendar.getInstance();

    // THE DATE FORMATTER.
    // "dd/MM/yyyy" = day with 2 digits / month with 2 digits / year with 4 digits.
    //   WATCH OUT: `MM` = month, `mm` = minutes. Swapping them is a classic mistake.
    // `Locale.getDefault()` = the device language's format.
    // `final`: the reference does not change. The object, however, is MUTABLE.
    // RISK: `SimpleDateFormat` is not thread-safe. Here it is used exclusively on
    //   the UI thread, so there is no concurrency.
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    // ==================================================================================
    // onCreate — BUILDING THE FORM
    // ==================================================================================
    // WHAT IT DOES: binds the layout, binds the widgets, installs the listeners and then
    //   checks whether it was started for edit.
    // HOW: initControls -> initListeners -> reading the Intent -> fillForm.
    // RISK: the order matters. `fillForm` touches widgets, so it must run
    //   after `initControls`. The listeners must be installed before `fillForm`,
    //   otherwise `setChecked` would trigger the listener? No: the listener is installed
    //   before, and `setChecked` DOES TRIGGER IT — that is why the "Yes"/"No" label
    //   updates correctly on edit.
    // REF: chapter 22, section 22.3.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. The chain to the superclass, mandatory first.
        super.onCreate(savedInstanceState);

        // 2. Edge-to-edge.
        EdgeToEdge.enable(this);

        // 3. The form's layout.
        setContentView(R.layout.activity_item);

        // 4. Insets on the root. `R.id.main` is the ScrollView from the XML.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // 5. The widgets, before anything touches them.
        initControls();

        // 6. The listeners, before fillForm (so setChecked updates the label).
        initListeners();

        // 7. The Intent that started the activity. It can contain a movie (edit)
        //    or it can be empty (insert).
        Intent intent = getIntent();

        // 8. Reading the movie. `IntentCompat.getSerializableExtra` is the
        //    typed variant: the third argument is the class, so no cast is needed any more.
        //    The result is A DESERIALIZED COPY, not the original from the list.
        Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);

        // 9. If there is a movie, we are in EDIT mode.
        if (existing != null) {

            // 9a. The position in the list. If the extra is missing, it stays -1 — but
            //     in edit mode it is always sent by MainActivity.
            position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);

            // 9b. We fill the form with the movie's values.
            fillForm(existing);

            // 9c. The screen title (the top bar).
            setTitle("Edit movie");

            // 9d. The button label.
            btMovieAction.setText("Update Movie");
        }
    }

    // ==================================================================================
    // fillForm — MODEL -> WIDGETS
    // ==================================================================================
    // WHAT IT DOES: copies the 10 fields of a `Movie` into the 13 controls.
    // HOW: 9 direct settings + 2 matching loops (Spinner, RadioGroup).
    // RISK: `existing.getRelease()` can be `null` -> `dateFormat.format(null)`
    //   throws an NPE. `getPosterUrl()` can be `null` -> `setText(null)` is legal.
    // REF: this method's pair is `saveMovie` — every setting here has
    //   an inverse equivalent there.
    // ==================================================================================
    private void fillForm(Movie existing) {

        // 1. The title: String -> EditText.
        etTitle.setText(existing.getTitle());

        // 2. The date: Date -> formatted String. WATCH OUT: `releaseCal` is NOT updated
        //    here. See BUG 3 below.
        etRelease.setText(dateFormat.format(existing.getRelease()));

        // 3. The budget: double -> String. `String.valueOf` avoids `"" + budget`.
        etBudget.setText(String.valueOf(existing.getBudget()));

        // 4. The duration: int -> progress on the SeekBar.
        sbDuration.setProgress(existing.getDuration());

        // 5. The Watchlist check box.
        cbonWatchList.setChecked(existing.isOnWatchlist());

        // 6. The switch. `setChecked` triggers the listener installed in onCreate,
        //    so `tvWatchedValue` receives "Yes"/"No" with no extra code.
        swWatched.setChecked(existing.isWatched());

        // 7. The rating: float -> stars.
        rbRating.setRating(existing.getRating());

        // 8. The poster: String -> EditText. It can be `null`; `setText(null)` shows empty.
        etPoster.setText(existing.getPosterUrl());

        // 9. The genre: a search in the Spinner by TEXT.
        //    `getCount()` = the number of elements in `@array/movie_genre`.
        for(int index=0; index<spGenre.getCount(); index++)
        {
            // `getItemAtPosition(index)` returns `Object`; `.equals` compares the texts.
            if(spGenre.getItemAtPosition(index).equals(existing.getGenre()))
            {
                // We found the genre: we select it and leave the loop.
                spGenre.setSelection(index);

                // Without `break`, we would keep searching and could select another element
                // if the list contained duplicates.
                break;
            }
        }

        // 10. The guidance: a search in the RadioGroup by the button's TEXT.
        //     `getChildCount()` = 5. `getChildAt(index)` returns `View`.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            // Cast to RadioButton so the text can be read.
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // Match by text: "PG-13" in the model == "PG-13" in the XML.
            if(rb.getText().toString().equals(existing.getApproval()))
            {
                // `check` wants the ID, not the index. `check` automatically unchecks the rest.
                rgApproval.check(rgApproval.getChildAt(index).getId());

                // Only one button can be selected; we leave.
                break;
            }
        }
    }

    /*
     * ==============================================================================
     * THEORY BLOCK: findViewById vs ViewBinding
     * ==============================================================================
     *
     * 1. `findViewById(R.id.x)` searches the view tree at RUNTIME and returns
     *    `View`. The cast to the concrete type is implicit through the generic, but it is not
     *    checked by the compiler: a wrong ID or a wrong type only gives an error at
     *    runtime.
     *
     * 2. ViewBinding generates an `ActivityItemBinding` class with a field for each
     *    ID. `binding.etTitle` is checked at COMPILE time. Besides, there is no longer any need
     *    for 13 lines of `findViewById`.
     *
     * 3. Why it is not used here: this lab teaches the classic method.
     *    ViewBinding appears in DMA05, and the course treats it separately.
     *
     * 4. Mixing is allowed, but it costs: if you use binding for 12 fields
     *    and findViewById for the 13th, you have two mechanisms to maintain.
     * ==============================================================================
     */

    // ==================================================================================
    // initControls — THE 13 findViewById CALLS
    // ==================================================================================
    // WHAT IT DOES: binds each field to the widget with the corresponding ID.
    // HOW: `findViewById(R.id.x)` for each one.
    // RISK: a wrong ID returns `null` WITHOUT a compile error. The NPE shows up at
    //   the first access, somewhere far away. That is why they are all grouped here.
    // REF: the IDs from `activity_item.xml`.
    // ==================================================================================
    private void initControls() {

        // 1. Title.
        etTitle = findViewById(R.id.etTitle);

        // 2. Date.
        etRelease = findViewById(R.id.etRelease);

        // 3. The genre.
        spGenre = findViewById(R.id.spGenre);

        // 4. The budget.
        etBudget = findViewById(R.id.etBudget);

        // 5. The duration.
        sbDuration = findViewById(R.id.sbDuration);

        // 6. The rating.
        rbRating = findViewById(R.id.rbRating);

        // 7. The guidance.
        rgApproval = findViewById(R.id.rgApproval);

        // 8. The check box. The ID has a capital "On", the field has a lowercase "on": `cbOnWatchList` vs
        //    `cbonWatchList`. A typo here gives an NPE in fillForm.
        cbonWatchList = findViewById(R.id.cbOnWatchList);

        // 9. The switch.
        swWatched = findViewById(R.id.swWatched);

        // 10. The poster.
        etPoster = findViewById(R.id.etPoster);

        // 11. The button. The ID is `btnMovieAction`, the field `btMovieAction`.
        btMovieAction = findViewById(R.id.btnMovieAction);

        // 12. The duration label.
        tvDurationValue = findViewById(R.id.tvDurationValue);

        // 13. The switch label.
        tvWatchedValue = findViewById(R.id.tvWatchedValue);
    }

    // ==================================================================================
    // initListeners — THE 4 LISTENERS
    // ==================================================================================
    // WHAT IT DOES: binds the events to methods.
    // HOW: click on the date, click on the button, switch change, slider movement.
    // RISK: the listeners are anonymous classes; `this` inside is NOT the activity.
    // REF: `saveMovie()` and `showReleaseDatePicker()` are the methods called.
    // ==================================================================================
    private void initListeners() {

        // 1. Click on the date field -> dialog.
        //    `EditText` has no dedicated "click" event; `OnClickListener` works
        //    because EditText is a View.
        etRelease.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showReleaseDatePicker();
            }
        });

        // 2. Click on the button -> save.
        btMovieAction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveMovie();
            }
        });

        // 3. Switch -> the "Yes"/"No" label.
        //    `OnCheckedChangeListener` is also called when the change comes from CODE
        //    (`setChecked` in fillForm), not only from the user.
        swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                // Ternary: a single expression for both states.
                tvWatchedValue.setText(isChecked ? "Yes" : "No");
            }
        });

        // 4. Slider -> the duration label.
        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            // 4a. On every progress change — including when it comes from code.
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // `progress` is int; concatenation with a String converts it automatically.
                tvDurationValue.setText(progress + " min.");
            }

            // 4b. When the slider is touched. We need nothing here.
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            // 4c. When the finger is lifted. We need nothing here.
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });
    }

    // ==================================================================================
    // saveMovie — WIDGETS -> MODEL -> INTENT
    // ==================================================================================
    // WHAT IT DOES: builds a `Movie` from the form values, puts it in an
    //   Intent and sends it back to MainActivity.
    // HOW: 1) new Movie(); 2) 9 setters; 3) a loop for the guidance; 4) putExtra;
    //   5) setResult + finish.
    // RISK: `Double.parseDouble("")` throws `NumberFormatException`; `releaseCal`
    //   can contain an old date (see BUG 3).
    // REF: the inverse pair of `fillForm`.
    // ==================================================================================
    private void saveMovie() {

        // 1. An empty object. Here you can see why the no-argument constructor is mandatory.
        Movie movie = new Movie();

        // 2. The title, straight from the text.
        movie.setTitle(etTitle.getText().toString());

        // 3. The date — from the CALENDAR, not from the text.
        movie.setRelease(releaseCal.getTime());

        // 4. The genre — the text selected in the Spinner.
        movie.setGenre(spGenre.getSelectedItem().toString());

        // 5. The budget — parsing. BUG 1: if the user leaves the field empty,
        //    `Double.parseDouble("")` throws `NumberFormatException` and the app closes.
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));

        // 6. The duration — straight from the progress.
        movie.setDuration(sbDuration.getProgress());

        // 7. The rating.
        movie.setRating(rbRating.getRating());

        // 8. The switch.
        movie.setWatched(swWatched.isChecked());

        // 9. The check box.
        movie.setOnWatchlist(cbonWatchList.isChecked());

        // 10. The poster. It can be an empty string if the user wrote nothing.
        movie.setPosterUrl(etPoster.getText().toString());

        // 11. The guidance: we walk the group and take the text of the checked button.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // `isChecked()` — only one button can be checked in a RadioGroup.
            if(rb.isChecked())
            {
                movie.setApproval(rb.getText().toString());

                // We found the button; we stop searching.
                break;
            }
        }

        // 12. An Intent WITHOUT a target. We do not start an activity; we only carry data
        //     back. `new Intent()` is enough for `setResult`.
        Intent intent = new Intent();

        // 13. The object, serialized automatically.
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);

        // 14. The position, ONLY in edit mode. In insert, the key is missing, and
        //     `getIntExtra(..., -1)` in MainActivity returns -1.
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);

        // 15. The result. Without this call, MainActivity would receive RESULT_CANCELED.
        setResult(RESULT_OK, intent);

        // 16. Closing the activity. Without it, the form stays on the screen.
        finish();
    }

    // ==================================================================================
    // showReleaseDatePicker — THE DATE DIALOG
    // ==================================================================================
    // WHAT IT DOES: opens a `DatePickerDialog` positioned on the date in `releaseCal`.
    // HOW: 1) it tries to parse the current text; 2) it opens the dialog; 3) on confirmation,
    //   it writes into the calendar and into the text.
    // RISK: manually typed text only reaches the calendar if the dialog is opened.
    // REF: the only place that writes into `releaseCal` after initialization.
    // ==================================================================================
    private void showReleaseDatePicker() {

        // 1. The current text in the field.
        String current = etRelease.getText().toString();

        // 2. If it is not empty, it tries to turn it into a Date.
        if (!current.isEmpty()) {
            try {
                // `parse` returns `null` if the text cannot be interpreted.
                Date parsed = dateFormat.parse(current);

                // If we have a valid date, we put it in the calendar.
                if (parsed != null)
                    releaseCal.setTime(parsed);

            // 3. Invalid text: we ignore it. The dialog opens on the old date.
            } catch (ParseException ignored) { }
        }

        // 4. The dialog. The constructor requires: Context, listener, year, month, day.
        new DatePickerDialog(
                this,

                // 4a. The confirmation listener.
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {

                        // We write into the calendar. `month` is 0-based, exactly as Calendar wants it.
                        releaseCal.set(year, month, day);

                        // We clear any error shown on the field.
                        etRelease.setError(null);

                        // We update the displayed text from the calendar.
                        etRelease.setText(dateFormat.format(releaseCal.getTime()));
                    }
                },

                // 4b. The initial values: from the calendar, not from the text.
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)

        // 5. `show()` — without it, the dialog is built but does not appear.
        ).show();
    }
}
```

### 30.4.1 The three real bugs

**BUG 1 — empty budget.**

```
etBudget empty  ->  getText().toString() = ""
                ->  Double.parseDouble("")  ->  NumberFormatException
                ->  the app closes (if the exception is not caught)
```

The user presses "Save Movie" without filling in the budget. The form validates nothing. The correct solution would be a check before `parseDouble`, plus `etBudget.setError(...)`.

**BUG 2 — `null` date on edit.**

```
Movie with release == null  ->  fillForm  ->  dateFormat.format(null)
                            ->  NullPointerException
```

It can happen if a movie was created with `setRelease(null)` or if the data comes from an external source. In the app in front of you it does not happen, because `saveMovie` always writes `releaseCal.getTime()`.

**BUG 3 — the date is lost on edit without touching the field.**

This one is the most subtle and deserves to be followed step by step:

```
1. Click on the "Inception" row (release = 16/07/2010)
2. ItemActivity.onCreate -> fillForm(existing)
      etRelease.setText("16/07/2010")     <- only the TEXT
      releaseCal stays TODAY's date       <- from Calendar.getInstance()
3. The user changes only the title and presses "Update Movie"
4. saveMovie -> movie.setRelease(releaseCal.getTime())  -> TODAY's date
```

The movie loses its release date without the user touching the field. The correct thing would be for `fillForm` to also do `releaseCal.setTime(existing.getRelease())`. The `showReleaseDatePicker` method fixes the problem **only** if the user opens the dialog, because there the text is parsed into the calendar.

### 30.4.2 The form's flow, in two ways

```
INSERT                                  EDIT
------                                  ----
Intent without MOVIE_EXTRA              Intent with MOVIE_EXTRA + POSITION_EXTRA
      |                                       |
existing == null                        existing != null
      |                                       |
position = -1                           position = 0 (or another index)
empty form                              fillForm(existing)
button: "Save Movie"                    button: "Update Movie"
      |                                       |
saveMovie()                             saveMovie()
      |                                       |
Intent: only MOVIE_EXTRA                Intent: MOVIE_EXTRA + POSITION_EXTRA
      |                                       |
MainActivity: position == -1            MainActivity: position == 0
movies.add(movie)                       movies.set(0, movie)
```

### 30.4.3 Why `releaseCal` and not the text from the `EditText`

```
The user can:
  A. pick the date from the dialog  -> releaseCal is updated, the text is updated
  B. type manually in the field     -> the text changes, releaseCal does NOT
  C. not touch the field            -> the text stays as it was, releaseCal stays as it was

saveMovie always reads releaseCal.
  A -> correct
  B -> the typed date is IGNORED (whatever was in the calendar is saved)
  C -> correct in insert, WRONG in edit (see BUG 3)
```

That is why the `EditText` has `inputType="date"` and a click listener: the intention is for it to be used only through the dialog, not by typing.

---

## 30.5 `AndroidManifest.xml` — the map of the components

30 lines. It contains no code, no data: it declares **what components the app has** and with what theme it starts. It is the only file that must know about the existence of both activities.

```xml
<!-- ====================================================================================== -->
<!-- FILE: AndroidManifest.xml — The map of the components -->
<!-- ====================================================================================== -->
<!-- WHAT IT IS: the app's declaration to the Android system. It says what activities exist, -->
<!-- which one is the start one, with what theme it starts and what icon it has. -->
<!-- WHY IT EXISTS: without a manifest, Android does not know the app has an activity to launch. -->
<!-- `startActivity(new Intent(this, ItemActivity.class))` would throw -->
<!-- `ActivityNotFoundException` if ItemActivity were not declared here. -->
<!-- WHAT IT DOES NOT DO: it contains no code, no data, it does not know what fields `Movie` has. -->
<!-- It declares no permissions — the app needs none. -->
<!-- THE DIFFERENCE FROM G1097: a single line, `android:theme`. The rest is identical. -->
<!-- ====================================================================================== -->

<!-- The XML declaration. It must be the first thing in the file in the real variant. -->
<?xml version="1.0" encoding="utf-8"?>

<!-- MANIFEST — the root. -->
<!-- xmlns:android  -> the namespace of the framework attributes. -->
<!-- xmlns:tools    -> the namespace of the attributes for Android Studio. -->
<!-- HERE it is declared, but UNUSED: no `tools:` attribute -->
<!-- appears in the file. It is harmless, but it is a dead import at the -->
<!-- XML level. In `activity_main.xml` and `activity_item.xml` it is used -->
<!-- for `tools:context`. -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- APPLICATION — the app as a whole. A single element per APK. -->
    <!-- It has no `android:name`: there is no custom Application class. -->
    <application

        <!-- Automatic backup of the app's data. Here there is no data to save, -->
        <!-- but the attribute remains from the project template. -->
        android:allowBackup="true"

        <!-- The data extraction rules for Android 12+. The file is in -->
        <!-- res/xml/data_extraction_rules.xml. -->
        android:dataExtractionRules="@xml/data_extraction_rules"

        <!-- The backup rules for versions before Android 12. -->
        android:fullBackupContent="@xml/backup_rules"

        <!-- The app icon, from res/mipmap. -->
        android:icon="@mipmap/ic_launcher"

        <!-- The name shown under the icon, from res/values/strings.xml. -->
        android:label="@string/app_name"

        <!-- The round icon, for the launchers that ask for it. -->
        android:roundIcon="@mipmap/ic_launcher_round"

        <!-- Support for mirrored layout in RTL languages. -->
        android:supportsRtl="true"

        <!-- THE THEME. The only difference from G1097: there `Theme.G1097`. -->
        <!-- The theme is defined in res/values/themes.xml and res/values-night/themes.xml. -->
        android:theme="@style/Theme.G1098">

        <!-- ACTIVITY 1: MainActivity — the start screen. -->
        <!-- `android:name=".activities.MainActivity"` is a name RELATIVE to the app's -->
        <!-- package (the namespace in build.gradle.kts). The leading dot -->
        <!-- means "the app's package". -->
        <!-- `android:exported="true"` — MANDATORY for the activity with an intent-filter -->
        <!-- from Android 12 onwards. `true` means that other apps (the launcher) -->
        <!-- can start it. Without the attribute, the build fails. -->
        <!-- `android:windowSoftInputMode="adjustResize"` — when the keyboard appears, the window -->
        <!-- shrinks, so the ScrollView can scroll down to the active field. -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!-- INTENT FILTER — what kind of intents the activity can receive. -->
            <!-- MAIN + LAUNCHER = "this is the app that appears in the launcher". -->
            <!-- Only one activity in the app has this filter. -->
            <intent-filter>

                <!-- The main action. -->
                <action android:name="android.intent.action.MAIN" />

                <!-- The category that makes it visible in the launcher. -->
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ACTIVITY 2: ItemActivity — the form. -->
        <!-- `android:exported="false"` — it is started ONLY from inside the app, -->
        <!-- through an explicit Intent. No other app can launch it. -->
        <!-- It has no intent-filter: there is no point in it being discovered from outside. -->
        <!-- It has the same `windowSoftInputMode`, because it has text fields too. -->
        <activity
            android:name=".activities.ItemActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**Reference table — the attributes in the manifest:**

| Attribute | Value | Effect |
|---|---|---|
| `android:allowBackup` | `true` | allows backing up the app's data |
| `android:theme` | `@style/Theme.G1098` | the Material theme, defined in `themes.xml` |
| `android:exported` (Main) | `true` | the launcher can start it |
| `android:exported` (Item) | `false` | only the app can start it |
| `android:windowSoftInputMode` | `adjustResize` | the keyboard shrinks the window |
| `android:name` | `.activities.X` | a name relative to the app's package |

**Why there is no `package=`:** in modern versions of the Android Gradle Plugin, the package name is declared in `build.gradle.kts` (`namespace = "ro.ase.ie.g1098"`), not in the manifest. The `package` attribute was removed from the template.

---

## 30.6 `activity_main.xml` — the list screen

26 lines. A `FrameLayout` with exactly two children: the list (underneath) and the FAB (on top).

```xml
<!-- ====================================================================================== -->
<!-- FILE: activity_main.xml — THE SCREEN WITH THE LIST -->
<!-- ====================================================================================== -->
<!-- WHAT IT IS: a FrameLayout with exactly two children: ListView (fills everything) and FAB (on top of it). -->
<!-- WHY SO LITTLE: all the complexity is in `activity_item.xml` (the form). -->
<!-- Here only the skeleton of the list. -->
<!-- THE STRUCTURE: -->
<!-- FrameLayout (id=main) -->
<!-- |== ListView (id=listView)            <- first child = drawn first = underneath -->
<!-- +== FloatingActionButton (id=...)     <- second child = drawn over the list -->
<!-- THE ORDER OF THE CHILDREN IS MEANING, NOT STYLE: in a FrameLayout, each child is -->
<!-- drawn over the previous one. Reversed, the list would cover the button. -->
<!-- THE DIFFERENCE FROM G1097: a single attribute — the FAB's `app:srcCompat` uses -->
<!-- `@drawable/outline_add_2_24` instead of `@drawable/outline_add_24`. -->
<!-- ====================================================================================== -->

<!-- The XML declaration. -->
<?xml version="1.0" encoding="utf-8"?>

<!-- FRAMELAYOUT — the root container. -->
<!-- WHY FrameLayout and not LinearLayout: the children must OVERLAP. A LinearLayout -->
<!-- would put them next to each other (or one under the other), and the FAB would no longer float over the list. -->
<!-- WHY not ConstraintLayout: for two children, a FrameLayout is simpler and cheaper. -->
<!-- THE ATTRIBUTES, IN TURN: -->
<!-- xmlns:android   -> the framework attributes (layout_width, text, id...) -->
<!-- xmlns:app       -> the library attributes (Material, AndroidX) -->
<!-- xmlns:tools     -> attributes that exist ONLY in the Android Studio preview -->
<!-- and are REMOVED at build time. They never reach the APK. -->
<!-- android:id      -> @+id/main; `@+id/` CREATES the ID, `@id/` REFERENCES an existing one -->
<!-- layout_width    -> match_parent: takes the parent's full width -->
<!-- layout_height   -> match_parent: takes the full height -->
<!-- orientation     -> INVALID ATTRIBUTE on FrameLayout; it exists only on LinearLayout. -->
<!-- It is IGNORED by Android and produces a lint warning -->
<!-- ("Unknown attribute"). A leftover from a previous LinearLayout. -->
<!-- tools:context   -> only for preview; it tells Android Studio what activity -->
<!-- to use for the theme. Removed at build time. -->
<!-- WHY `android:id="@+id/main"` IS MANDATORY: the code does `findViewById(R.id.main)` -->
<!-- for the insets listener. Without this ID, the call would return `null` and -->
<!-- `setOnApplyWindowInsetsListener(null, ...)` would throw an NPE. -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!-- LISTVIEW — the scrollable list. -->
    <!-- WHY ListView and not RecyclerView: at this commit the classic ListView is taught. -->
    <!-- RecyclerView appears in the next lab. -->
    <!-- THE ATTRIBUTES: -->
    <!-- android:id              -> listView; used by `findViewById` in initControls -->
    <!-- layout_width/height     -> match_parent on both axes: the list fills the whole screen, -->
    <!-- including the area under the FAB. The FAB is drawn OVER the -->
    <!-- list, not the list next to it. -->
    <!-- android:entries         -> fills the list from XML with the elements from `@array/items`. -->
    <!-- AT RUNTIME, `listView.setAdapter(movieAdapter)` -->
    <!-- COMPLETELY REPLACES this adapter. `entries` remains -->
    <!-- only so the preview shows a full list. -->
    <!-- The runtime cost is zero after `setAdapter`. -->
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />

    <!-- FLOATING ACTION BUTTON — the "+" button. -->
    <!-- The full name is necessary because it is a class from the Material library, -->
    <!-- not one from the framework. The `com.google.android.material...` prefix is the class path. -->
    <!-- THE ATTRIBUTES: -->
    <!-- android:id          -> floatingActionButton; looked up in initControls -->
    <!-- layout_width/height -> wrap_content: the FAB has a fixed size imposed by the style -->
    <!-- (56dp by default). `match_parent` would stretch it over the whole screen. -->
    <!-- android:layout_gravity -> the position of THIS CHILD in ITS PARENT (FrameLayout). -->
    <!-- android:layout_margin  -> 16dp on all sides. Together with the insets padding -->
    <!-- applied to `R.id.main`, the button sits 16dp from the safe -->
    <!-- area, not from the physical edge. -->
    <!-- android:contentDescription -> the text read by TalkBack. MANDATORY for -->
    <!-- elements with no visible text; without it, lint gives -->
    <!-- an error ("ContentDescription"), and users with a -->
    <!-- screen reader hear only "button". -->
    <!-- app:srcCompat       -> the compatible variant for vector images. -->
    <!-- `android:src` would work on API 21+, but `srcCompat` -->
    <!-- is the AndroidX recommendation and the only one that supports -->
    <!-- vectors on all versions. -->
    <!-- THE DIFFERENCE FROM G1097: `@drawable/outline_add_2_24` vs `@drawable/outline_add_24`. -->
    <!-- Both files exist, but in different projects. If you move the XML without the drawable, -->
    <!-- the build fails with "resource drawable/outline_add_2_24 not found". -->
    <!-- ================================================================================== -->
    <!-- layout_gravity  vs  gravity -->
    <!-- ================================================================================== -->
    <!-- gravity         = how the ELEMENT arranges its children inside itself -->
    <!-- layout_gravity  = how the ELEMENT is arranged in its parent -->
    <!-- Example: a TextView with `gravity="center"` centres its TEXT. -->
    <!-- A TextView with `layout_gravity="center"` is centred IN THE PARENT. -->
    <!-- `bottom|end` = bottom, right. `end` respects the reading direction: in RTL it becomes -->
    <!-- left. `right` would have been fixed and would be wrong in RTL. -->
    <!-- WHY it works here: FrameLayout respects `layout_gravity` on children. -->
    <!-- ================================================================================== -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_2_24" />

</FrameLayout>
```

**Reference table for the attributes in this file:**

| Attribute | Value | Effect |
|---|---|---|
| `android:id` | `@+id/main` | creates the ID used by the insets |
| `android:layout_width/height` | `match_parent` | fills the parent |
| `android:orientation` | `horizontal` | **invalid** on FrameLayout, ignored |
| `android:entries` | `@array/items` | preview list, replaced at runtime |
| `android:layout_gravity` | `bottom\|end` | positions the FAB in the FrameLayout |
| `android:contentDescription` | `"Add"` | accessibility + lint |
| `app:srcCompat` | `@drawable/outline_add_2_24` | compatible vector image |
| `tools:context` | `.activities.MainActivity` | preview only |

---

## 30.7 `activity_item.xml` — the form

452 lines, identical to G1097. Four cards, a header, a button. It is the longest file of the app and the only one that is hard to memorize — that is why the structure matters more than each attribute.

### 30.7.0 Three rules that apply throughout the file

**1. `?attr/` vs `@color/` vs `#RRGGBB`**

| Form | When it is resolved | Does it change with the theme? | When it is used |
|---|---|---|---|
| `?attr/colorPrimary` | at runtime, from the current theme | **yes** | any semantic colour |
| `@color/my_color` | at build time, from `colors.xml` | no | fixed brand colours |
| `#FFC107` | at build time, literal | no | accepted exceptions (the stars) |
| `@android:color/transparent` | framework constant | no | "no background" |

The essential difference: `?attr/` is a **role**, `@color/` is a **value**. `?attr/colorPrimary` means "the theme's primary colour" and becomes another shade in dark mode. `@color/purple_500` stays purple in both themes.

**2. `0dp` + `layout_weight`**

```
Horizontal LinearLayout, total width 360dp
+--------------------------------------------------------------+
| TextView A        | TextView B                               |
| width=0dp         | width=wrap_content                       |
| weight=1          | (no weight)                              |
+-------------------+------------------------------------------+
|<---- the rest --->|<------ as much as the text asks for ----->|

The rule: `0dp` + `weight` = "I don't care about my width, give me what is left".
Without `0dp` (with `wrap_content`), the weight distributes the space AFTER each
child has taken its natural size — the result is hard to predict.
```

**3. `style=` vs explicit attributes**

`style="@style/Widget.Material3.TextInputLayout.OutlinedBox"` applies a **bundle** of attributes (outline, padding, colours, corners). An attribute written explicitly next to `style` **overrides** the one from the style. That is why `app:cardCornerRadius="20dp"` works over the card's style.

### 30.7.1 The annotated file

```xml
<!-- ====================================================================================== -->
<!-- FILE: activity_item.xml — THE INSERT / EDIT FORM -->
<!-- ====================================================================================== -->
<!-- WHAT IT IS: a ScrollView with a single child (a vertical LinearLayout), which contains -->
<!-- a header, four cards and a button. -->
<!-- WHY IT EXISTS: it is the screen where the user enters a movie's data. -->
<!-- WHO USES IT: ItemActivity, through `setContentView(R.layout.activity_item)`. -->
<!-- WHAT IT DOES NOT DO: it does not validate, it does not save, it does not know what a `Movie` is. -->
<!-- THE STRUCTURE (4 cards + header + button): -->
<!-- ScrollView (id=main) -->
<!-- +== vertical LinearLayout -->
<!-- |== TextView  "Movie details"               <- title -->
<!-- |== TextView  "Fill in the information..."  <- subtitle -->
<!-- |== MaterialCardView  [Basics]              <- title, genre, date -->
<!-- |== MaterialCardView  [Production]          <- budget, duration -->
<!-- |== MaterialCardView  [Your verdict]        <- rating, switch, check box, guidance -->
<!-- |== MaterialCardView  [Poster]              <- URL -->
<!-- +== MaterialButton    "Save Movie"          <- the action -->
<!-- WHY CARDS: they split a long form into visual sections. Each card has -->
<!-- the same recipe: surface background, 20dp corners, 16dp inner padding. -->
<!-- ====================================================================================== -->

<!-- The XML declaration. -->
<?xml version="1.0" encoding="utf-8"?>

<!-- SCROLLVIEW — the root. -->
<!-- WHY ScrollView: the form is taller than the screen. Without it, the last -->
<!-- fields would be inaccessible. -->
<!-- THE RULE: a ScrollView has EXACTLY ONE child. If you put two, you get an error at inflate -->
<!-- ("ScrollView can host only one direct child"). -->
<!-- THE ATTRIBUTES: -->
<!-- android:id="@+id/main"        -> looked up by the insets listener in ItemActivity -->
<!-- android:fillViewport="true"   -> the child is stretched at least to the height -->
<!-- of the viewport, even if the content is shorter -->
<!-- android:background="?attr/colorSurface" -> the theme background, not a fixed white -->
<!-- tools:context                 -> preview only -->
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <!-- VERTICAL LINEARLAYOUT — the only child of the ScrollView. -->
    <!-- All the sections sit here, one under the other. -->
    <!-- `paddingHorizontal` + `paddingTop/Bottom` = 16dp sideways, 24dp top/bottom. -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- Header -->
        <!-- THE SCREEN TITLE, the in-page variant. -->
        <!-- `textAppearanceHeadlineMedium` is a Material typography role: -->
        <!-- size, weight and spacing consistent with the rest of the app. -->
        <!-- `?attr/colorOnSurface` = the text colour suited to the current surface. -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Movie details"
            android:textAppearance="?attr/textAppearanceHeadlineMedium"
            android:textColor="?attr/colorOnSurface"
            android:textStyle="bold" />

        <!-- THE SUBTITLE. `colorOnSurfaceVariant` is a weaker shade, for secondary -->
        <!-- text. `layout_marginBottom="20dp"` separates the header from the first card. -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="20dp"
            android:text="Fill in the information below and save."
            android:textAppearance="?attr/textAppearanceBodyMedium"
            android:textColor="?attr/colorOnSurfaceVariant" />

        <!-- ============================================================================ -->
        <!-- BLOCK: MaterialCardView — the three styles used in this file                  -->
        <!-- ============================================================================ -->
        <!-- `?attr/materialCardViewFilledStyle`  = filled background, no outline.         -->
        <!-- `?attr/materialCardViewOutlinedStyle` = transparent background, with outline. -->
        <!-- `?attr/materialCardViewElevatedStyle` = raised background, with shadow.       -->
        <!-- Here: the first three cards are FILLED, the Spinner's card is OUTLINED.      -->
        <!-- `app:cardCornerRadius` overrides the corner from the style.                  -->
        <!-- `app:strokeColor` only makes sense on the outlined style.                    -->
        <!-- ============================================================================ -->
        <!-- ============ CARD 1: Basics ============ -->
        <!-- CARD 1 — title, genre, date. -->
        <!-- `style="?attr/materialCardViewFilledStyle"` = filled background, no outline. -->
        <!-- `app:cardCornerRadius="20dp"` overrides the style's default corner. -->
        <!-- `layout_marginBottom="16dp"` = the space between the cards. -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <!-- The card's content: a vertical LinearLayout with 16dp padding. -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!-- The section title. `colorPrimary` makes it visible as a card title. -->
                <!-- `textAppearanceTitleMedium` = smaller than the screen title. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Basics"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Title -->
                <!-- THE FIELD LABEL. It has an ID (`tvTile`), but the code does NOT use it: -->
                <!-- it is only for readability and for possible tests. -->
                <!-- `textAppearanceLabelLarge` = small label, capitals in the theme. -->
                <TextView
                    android:id="@+id/tvTile"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Title"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- TEXTINPUTLAYOUT — the wrapper of the title field. -->
                <!-- `OutlinedBox` = a visible outline around the field. -->
                <!-- `app:hintEnabled="false"` = no floating label; the label is -->
                <!-- the TextView above. -->
                <!-- `app:endIconMode="clear_text"` = adds an X that empties the field. -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text">

                    <!-- THE FIELD ITSELF. The ID `etTitle` is looked up in initControls. -->
                    <!-- `inputType="textCapWords"` = the keyboard starts with a capital -->
                    <!-- on every word. It is not validation, only comfort. -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Movie title"
                        android:inputType="textCapWords" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- Genre -->
                <!-- The label for the Spinner. ID `tvGenre`, unused in the code. -->
                <TextView
                    android:id="@+id/tvGenre"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Genre"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- THE SPINNER IS WRAPPED IN A CARD. -->
                <!-- WHY: the Spinner has no outline of its own. The card gives it the border -->
                <!-- and the corners, so it looks like a TextInput field. -->
                <!-- `cardBackgroundColor="@android:color/transparent"` = no background, -->
                <!-- only outline. -->
                <!-- `strokeColor="?attr/colorOutline"` = the theme's outline colour. -->
                <!-- `layout_height="56dp"` = the standard height of a Material field. -->
                <com.google.android.material.card.MaterialCardView
                    style="?attr/materialCardViewOutlinedStyle"
                    android:layout_width="match_parent"
                    android:layout_height="56dp"
                    android:layout_marginBottom="16dp"
                    app:cardBackgroundColor="@android:color/transparent"
                    app:cardCornerRadius="4dp"
                    app:strokeColor="?attr/colorOutline">

                    <!-- THE SPINNER. `entries="@array/movie_genre"` fills the list from XML. -->
                    <!-- `spinnerMode="dropdown"` = the list opens as a popup, -->
                    <!-- not as a modal dialog. -->
                    <!-- The ID `spGenre` is looked up in initControls and used in -->
                    <!-- fillForm (setSelection) and saveMovie (getSelectedItem). -->
                    <Spinner
                        android:id="@+id/spGenre"
                        android:layout_width="match_parent"
                        android:layout_height="match_parent"
                        android:entries="@array/movie_genre"
                        android:paddingStart="4dp"
                        android:spinnerMode="dropdown" />
                </com.google.android.material.card.MaterialCardView>

                <!-- Release date -->
                <!-- THE DATE FIELD. -->
                <!-- `hintEnabled="true"` = the "Release date" label floats above -->
                <!-- when the field has text. -->
                <!-- `startIconDrawable="@android:drawable/ic_menu_my_calendar"` = the -->
                <!-- framework calendar icon, on the left. -->
                <!-- `startIconContentDescription` = the text read by TalkBack for the icon. -->
                <!-- WATCH OUT: `etRelease` is NOT read in saveMovie. The real value sits -->
                <!-- in `releaseCal`. See BUG 3 in 30.4. -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="true"
                    app:startIconContentDescription="Release date"
                    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

                    <!-- THE FIELD. `inputType="date"` = a numeric keyboard with separators. -->
                    <!-- Clicking it opens DatePickerDialog (listener in ItemActivity). -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etRelease"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Release date"
                        android:inputType="date" />
                </com.google.android.material.textfield.TextInputLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ============ CARD 2: Production ============ -->
        <!-- CARD 2 — budget and duration. -->
        <!-- The same recipe as the first card: filled style, 20dp corner, 16dp padding. -->
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

                <!-- Budget -->
                <!-- The budget field label. ID `tvBudget`, unused in the code. -->
                <TextView
                    android:id="@+id/tvBudget"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Budget"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- THE BUDGET FIELD. -->
                <!-- `app:prefixText="$ "` = a prefix shown inside the field, but -->
                <!-- NOT part of the text read by `getText()`. -->
                <!-- `inputType="numberDecimal"` = a numeric keyboard with a decimal separator. -->
                <!-- BUG 1: if the user leaves the field empty, `Double.parseDouble("")` -->
                <!-- throws NumberFormatException in saveMovie. -->
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

                <!-- Duration -->
                <!-- THE DURATION ROW: label on the left, value on the right. -->
                <!-- `gravity="center_vertical"` = alignment on the vertical centre. -->
                <!-- `orientation="horizontal"` = the children sit next to each other. -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">

                    <!-- THE "Duration" LABEL. -->
                    <!-- `layout_width="0dp"` + `layout_weight="1"` = takes all the remaining space, -->
                    <!-- pushing the value to the right. -->
                    <TextView
                        android:id="@+id/tvDuration"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Duration"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!-- THE DURATION VALUE. It is updated from the code, in -->
                    <!-- `onProgressChanged`, with `progress + " min."`. -->
                    <!-- `tools:text="148 min"` = a value ONLY for preview; at runtime -->
                    <!-- the text starts from "0 min". -->
                    <TextView
                        android:id="@+id/tvDurationValue"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorPrimary"
                        tools:text="148 min" />
                </LinearLayout>

                <!-- THE SEEKBAR. -->
                <!-- `max="300"` and `min="0"` = the range. `min` is available from API 26; -->
                <!-- on older versions it would be ignored. -->
                <!-- `progressTint` and `thumbTint` = the colour of the bar and the handle, from the theme. -->
                <!-- `tools:progress="148"` = preview only. -->
                <!-- The ID `sbDuration` is used in initControls, fillForm, saveMovie -->
                <!-- and in the progress listener. -->
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

                <!-- THE MIN/MAX ROW: two labels, "0 min" on the left and "300 min" -->
                <!-- on the right. `paddingHorizontal="16dp"` aligns them with the edges -->
                <!-- of the bar, which has inner padding. -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal"
                    android:paddingHorizontal="16dp">

                    <!-- The minimum. `0dp` + `weight=1` pushes the other one to the right. -->
                    <TextView
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelSmall"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!-- The maximum. -->
                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="300 min"
                        android:textAppearance="?attr/textAppearanceLabelSmall"
                        android:textColor="?attr/colorOnSurfaceVariant" />
                </LinearLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ============ CARD 3: Your verdict ============ -->
        <!-- CARD 3 — rating, switch, check box, guidance. The most complex card: -->
        <!-- it contains two separators and a horizontally scrollable RadioGroup. -->
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
                    android:text="Your verdict"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Rating -->
                <!-- The rating label. ID `tvRating`, unused in the code. -->
                <TextView
                    android:id="@+id/tvRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Rating"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- RATINGBAR — the stars. -->
                <!-- `numStars="5"` = five stars. -->
                <!-- `stepSize="0.5"` = half stars. Without it, only whole stars. -->
                <!-- `progressTint="#FFC107"` = a literal yellow, not from the theme. It is an -->
                <!-- accepted exception: the stars' colour must not change with the theme. -->
                <!-- `layout_gravity="center_horizontal"` = centred in the card. -->
                <!-- The ID `rbRating` is used in initControls, fillForm, saveMovie. -->
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

                <!-- SEPARATOR — a 1dp line. -->
                <!-- An empty `View`, used only for the line. `colorOutlineVariant` is -->
                <!-- the theme's separator colour. -->
                <!-- `layout_marginVertical="12dp"` = space above and below. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Recommended -->
                <!-- THE "Recommended" ROW: text on the left, switch and check box on the right. -->
                <!-- `minHeight="48dp"` = the minimum touch target recommended by Material. -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:minHeight="48dp"
                    android:orientation="horizontal">

                    <!-- THE TEXT COLUMN: two vertical TextViews. -->
                    <!-- `0dp` + `weight=1` = takes all the free space, pushing -->
                    <!-- the controls to the right. -->
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">

                        <!-- The main label. -->
                        <TextView
                            android:id="@+id/tvWatched"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Recommended"
                            android:textAppearance="?attr/textAppearanceBodyLarge"
                            android:textColor="?attr/colorOnSurface" />

                        <!-- THE SWITCH'S VALUE, as text. It is updated from the -->
                        <!-- `onCheckedChanged` listener with "Yes"/"No". It starts from "No". -->
                        <TextView
                            android:id="@+id/tvWatchedValue"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="No"
                            android:textAppearance="?attr/textAppearanceLabelLarge"
                            android:textColor="?attr/colorPrimary" />
                    </LinearLayout>

                    <!-- THE MATERIAL SWITCH. ID `swWatched`, field `MaterialSwitch swWatched`. -->
                    <!-- WATCH OUT: it is not `android.widget.Switch`. That is why the import -->
                    <!-- `android.widget.Switch` would be dead. -->
                    <com.google.android.material.materialswitch.MaterialSwitch
                        android:id="@+id/swWatched"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="12dp" />

                    <!-- THE "Watchlist" CHECK BOX. ID `cbOnWatchList` (with a capital "On"). -->
                    <!-- The type in the XML is MaterialCheckBox; the field in the code is -->
                    <!-- declared `CheckBox` — MaterialCheckBox extends CheckBox. -->
                    <com.google.android.material.checkbox.MaterialCheckBox
                        android:id="@+id/cbOnWatchList"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Watchlist" />
                </LinearLayout>

                <!-- The second separator, identical to the first. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Guidance -->
                <!-- The label of the guidance group. ID `tvGuidance`, unused in the code. -->
                <TextView
                    android:id="@+id/tvGuidance"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Guidance"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- HORIZONTALSCROLLVIEW — allows horizontal scrolling. -->
                <!-- WHY: five radio buttons do not fit on a narrow screen. -->
                <!-- `scrollbars="none"` = no visible scroll bar. -->
                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none">

                    <!-- ==================================================================== -->
                    <!-- BLOCK: RadioGroup — why it guarantees the single selection           -->
                    <!-- ==================================================================== -->
                    <!-- A RadioGroup tracks which button is checked and, when one receives  -->
                    <!-- `android:checked="true"`, it automatically unchecks the other one.   -->
                    <!-- `check(id)` in the code does the same operation, programmatically.  -->
                    <!-- That is why fillForm can do a single match and `break`.             -->
                    <!-- `getChildCount()` counts the DIRECT CHILDREN, that is, the 5 radio buttons. -->
                    <!-- ==================================================================== -->
                    <!-- RADIOGROUP — guarantees the single selection. -->
                    <!-- `orientation="horizontal"` = the buttons sit on one row. -->
                    <!-- The ID `rgApproval` is used in initControls, fillForm, -->
                    <!-- saveMovie and in the text matching loops. -->
                    <RadioGroup
                        android:id="@+id/rgApproval"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <!-- BUTTON 1: "G". `android:checked="true"` = selected by default. -->
                        <!-- This is the reason why an empty form still has -->
                        <!-- a valid guidance on save. -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbGeneral"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:checked="true"
                            android:text="G" />

                        <!-- BUTTON 2: "PG". -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbParentGuidance"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG" />

                        <!-- BUTTON 3: "PG-13". The text is the matching key in fillForm. -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbPG13"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG-13" />

                        <!-- BUTTON 4: "R". -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbRestricted"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="R" />

                        <!-- BUTTON 5: "NC-17". -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbNC17"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="NC-17" />
                    </RadioGroup>
                </HorizontalScrollView>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ============ CARD 4: Poster ============ -->
        <!-- CARD 4 — the poster URL. The only card with a single field. -->
        <!-- `layout_marginBottom="24dp"` = more space before the button. -->
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

                <!-- The section title. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Poster"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- THE POSTER FIELD. -->
                <!-- `endIconMode="clear_text"` = an X to empty it. -->
                <!-- `startIconDrawable="@android:drawable/ic_menu_gallery"` = a -->
                <!-- framework gallery icon. -->
                <!-- `inputType="textUri"` = a keyboard with `/` and `.com`, suited for a URL. -->
                <!-- The ID `etPoster` is used in initControls, fillForm, saveMovie. -->
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

        <!-- Save -->
        <!-- THE ACTION BUTTON. -->
        <!-- `style="@style/Widget.Material3.Button"` = a filled button, with corners. -->
        <!-- `layout_height="60dp"` = taller than the default, for easy touching. -->
        <!-- `app:cornerRadius="30dp"` = fully rounded corners (half the height). -->
        <!-- `app:icon="@android:drawable/ic_menu_save"` = the save icon. -->
        <!-- `app:iconGravity="textStart"` = the icon before the text. -->
        <!-- The ID `btnMovieAction` is looked up in initControls; the text is changed -->
        <!-- in onCreate to "Update Movie" for edit mode. -->
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

### 30.7.2 The view hierarchy, in short

```
ScrollView (main)
 |
 +-- LinearLayout (vertical)
      |
      +-- TextView "Movie details"
      +-- TextView "Fill in the information below and save."
      |
      +-- MaterialCardView [Basics]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Basics"
      |         +-- TextView "Title"  (tvTile)
      |         +-- TextInputLayout
      |         |    +-- TextInputEditText etTitle
      |         +-- TextView "Genre"  (tvGenre)
      |         +-- MaterialCardView
      |         |    +-- Spinner spGenre
      |         +-- TextInputLayout
      |              +-- TextInputEditText etRelease
      |
      +-- MaterialCardView [Production]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Production"
      |         +-- TextView "Budget"  (tvBudget)
      |         +-- TextInputLayout
      |         |    +-- TextInputEditText etBudget
      |         +-- LinearLayout (horizontal)
      |         |    +-- TextView "Duration" (0dp, weight=1)
      |         |    +-- TextView tvDurationValue
      |         +-- SeekBar sbDuration
      |         +-- LinearLayout (horizontal)
      |              +-- TextView "0 min" (0dp, weight=1)
      |              +-- TextView "300 min"
      |
      +-- MaterialCardView [Your verdict]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Your verdict"
      |         +-- TextView "Rating"  (tvRating)
      |         +-- RatingBar rbRating
      |         +-- View (separator)
      |         +-- LinearLayout (horizontal)
      |         |    +-- LinearLayout (vertical, 0dp, weight=1)
      |         |    |    +-- TextView "Recommended" (tvWatched)
      |         |    |    +-- TextView tvWatchedValue
      |         |    +-- MaterialSwitch swWatched
      |         |    +-- MaterialCheckBox cbOnWatchList
      |         +-- View (separator)
      |         +-- TextView "Guidance" (tvGuidance)
      |         +-- HorizontalScrollView
      |              +-- RadioGroup rgApproval
      |                   +-- MaterialRadioButton rbGeneral   "G"
      |                   +-- MaterialRadioButton rbParentGuidance "PG"
      |                   +-- MaterialRadioButton rbPG13      "PG-13"
      |                   +-- MaterialRadioButton rbRestricted "R"
      |                   +-- MaterialRadioButton rbNC17      "NC-17"
      |
      +-- MaterialCardView [Poster]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Poster"
      |         +-- TextInputLayout
      |              +-- TextInputEditText etPoster
      |
      +-- MaterialButton btnMovieAction "Save Movie"
```

---

## 30.8 The complete flow

### 30.8.1 Starting the app

```
LAUNCHER
  |
  |== Android reads AndroidManifest.xml
  |== finds the activity with MAIN + LAUNCHER
  |== starts .activities.MainActivity
        |
        v
  MainActivity.onCreate
    |== super.onCreate
    |== EdgeToEdge.enable
    |== setContentView(activity_main)
    |== insets on R.id.main
    |== addSampleMovies()        -> 3 movies in the list
    |== movieAdapter = ArrayAdapter(simple_list_item_1, movies)
    |== initControls()           -> fabInsert, listView, setAdapter
    |== initListeners()          -> FAB + item click
    +== launcher = registerForActivityResult(...)
        |
        v
  onStart -> onResume
        |
        v
  the ListView asks the adapter for 3 rows
        |
        v
  ArrayAdapter.getView -> TextView.setText(movie.toString())
        |
        v
  THE SCREEN SHOWS 3 ROWS
```

### 30.8.2 Insert — FAB

```
PRESS "+"
  |
  |== fabInsert.onClick
  |== new Intent(MainActivity.this, ItemActivity.class)
  |== launcher.launch(intent)
        |
        v
  ItemActivity.onCreate
    |== setContentView(activity_item)
    |== initControls()          -> 13 findViewById
    |== initListeners()         -> 4 listeners
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
    |== movie = getSerializableExtra(MOVIE_EXTRA)     <- A COPY
    |== position = getIntExtra(POSITION_EXTRA, -1)    -> -1
    |== movies.add(movie)
    +== movieAdapter.notifyDataSetChanged()
          |
          v
  the ListView redraws -> the 4th row appears
```

### 30.8.3 Edit — click on a row

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
    |== existing = IntentCompat.getSerializableExtra(...)   <- COPY
    |== existing != null
    |     |== position = 0
    |     |== fillForm(existing)     -> 10 fields filled
    |     |== setTitle("Edit movie")
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

### 30.8.4 The object that travels

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
                                                       (NEW object, new address)
                                    |
                        fillForm(existing) reads
                        saveMovie() creates Movie@D
                                    |
                                    v
                          Result Intent { "movie" -> Movie@D,
                                          "position" -> 0 }
                                    |
                                    v
                          movies.set(0, Movie@D)
                                    |
                                    v
                          Movie@A stays in the heap until GC
```

**The practical consequence:** a change in the form is not seen in the list until `movies.set(...)`. There is no "link" between the object in the list and the one in the form — they are two distinct objects.

### 30.8.5 Row recycling in the ListView

```
The ListView has 7 visible rows, the list has 100 elements.

  screen: [0][1][2][3][4][5][6]

  you scroll down:
    row 0 goes out upwards   ->  convertView = row 0
    row 7 comes in downwards <-  ArrayAdapter.getView(7, convertView, parent)

  ArrayAdapter:
    if convertView != null:
        reuses the view (no longer inflates the XML)
    TextView.setText(movies.get(7).toString())

  WHY it matters: without recycling, 100 rows would mean 100 inflates.
    With recycling, there are ~8 views for however many elements.

  WHY `notifyDataSetChanged()` is necessary:
    The ListView does NOT observe the list. It only knows what the adapter told it at the last bind.
    `notifyDataSetChanged()` -> adapter.notifyChanged() -> the ListView re-binds
    the visible rows.
```

---

## 30.9 What to remember from each file

| File | The essence | The trap |
|---|---|---|
| `Movie.java` | serializable POJO, 10 fields, explicit empty constructor, `isX()` for booleans, complete `toString()` | the 10-parameter constructor is POSITIONAL |
| `MainActivity.java` | the order in `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` | `launcher` is assigned AFTER `initListeners` |
| `ItemActivity.java` | 13 `findViewById` calls, `releaseCal` as source of truth, a generic loop over the `RadioGroup`, `setResult` + `finish` | empty budget -> crash; the date is lost on edit |
| `AndroidManifest.xml` | two activities, correct `exported`, the theme | `exported="true"` mandatory on the activity with an intent-filter |
| `activity_main.xml` | `FrameLayout` + the order of the children + `layout_gravity` on the FAB | `android:orientation` is invalid on FrameLayout |
| `activity_item.xml` | `ScrollView` with one child, `MaterialCardView` as a section, `TextInputLayout`, a wrapped `Spinner` | `hintEnabled` must be matched with the existence of the label |

### The 10 things you will have been asked

1. **Why `implements Serializable`?** So that it can be put into an `Intent` with `putExtra`.
2. **Is the object received the original?** No. It is a deserialized copy.
3. **Why an explicit empty constructor?** A constructor with parameters suppresses the implicit constructor, and `saveMovie` does `new Movie()`.
4. **Why `isWatched()`?** The JavaBeans convention for `boolean`.
5. **Why `notifyDataSetChanged()`?** The ListView does not observe the list; the adapter must announce it.
6. **Why `MainActivity.this`?** In the anonymous class, `this` is the listener, not the `Context`.
7. **Why `releaseCal` and not `etRelease`?** The calendar is the source of truth; the text can be invalid.
8. **Why is `fromUser` ignored?** The label must reflect the value even when it comes from code.
9. **Why `0dp` + `weight`?** "Take all the remaining space", not "take the natural size".
10. **Why `?attr/` and not `@color/`?** `?attr/` is a theme role and adapts to dark mode.

### The 5 differences from G1097 that you must be able to state

1. **`posterUrl` vs `poster`** — the name propagates into the getter, the setter and the two calls in `ItemActivity`.
2. **No `= null`** — identical behaviour, poorer documentation.
3. **The empty constructor after `toString()`** — reading order, not compilation order.
4. **`toString()` with `posterUrl`** — a complete `toString()`; G1096 and G1099 omit it.
5. **`outline_add_2_24`** — a resource reference valid only if the drawable exists in the project.

---

## Chapter 30 summary

- The model does not touch the UI; the activities contain no row logic.
- `onCreate`: `super` -> `EdgeToEdge` -> `setContentView` -> insets -> data -> adapter -> controls -> listeners -> launcher.
- `releaseCal` is the source of truth for the date, not the text in the `EditText`.
- The loop over the `RadioGroup` makes the code generic — you add buttons in XML, the code sees them.
- `setResult(RESULT_OK, intent)` + `finish()` is the mandatory pair.
- `notifyDataSetChanged()` after any change to the list.
- G1098 is the cleanest when it comes to imports: a single dead import (`Toast` in `MainActivity`) and zero in `ItemActivity`.
- Three real bugs: empty budget, a null `release`, the date lost on edit without touching the field.
- The differences from G1097 are in names, order and hygiene — the app does exactly the same thing.

**Back to** [cheatsheet](21%20-%20Cheatsheet.md) **or to** [the overview](index.html).
