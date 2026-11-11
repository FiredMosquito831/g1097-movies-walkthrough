# Chapter 22 — The G1097 code, annotated

**Goal:** to read every line of the G1097 application with the explanation glued to it — what it does, why it is there, what breaks if you remove it.

**Estimated time:** 90–120 min (active reading, with the project open alongside).

**Source:** `cod-final`, commit `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`.

**Rule:** the code is **unmodified, byte for byte**. Everything that appears with `//` or `<!-- -->` beyond the source is annotation.

---

## 22.0 How to read this chapter

This is not an exercise chapter. It is a chapter of **reading with a magnifying glass**: you take each file of the application and go through it line by line, with the explanation right above.

- **Read the code first, the comment second.** Cover the comment block with your hand, say what the line does, then check.
- **The `THEORY` blocks** appear before each class and explain *why* the structure exists, not *how* it works.
- **The numbered blocks** ("1. Validation", "2. Cleanup") describe the steps of a method in execution order. The order is part of the lesson.
- **The `RISK:` and `BUG:` markers** flag the places where the code works today but can break, or where it already breaks.
- **The ASCII diagrams** show what you cannot see in the code: the object travelling between activities, the safe area of the screen, the recycling of rows in the list.
- **Do not memorise.** The goal is to be able to rebuild the file starting from a diagram.

---

## 22.1 `Movie.java` — the data model

```java
/*
 * ======================================================================================
 * FILE: Movie.java — THE DATA MODEL
 * ======================================================================================
 * WHAT THIS FILE IS:
 *   A POJO class (Plain Old Java Object): 10 private fields, one constructor with 10
 *   parameters, one empty constructor and 20 getters/setters. Zero business logic.
 *
 * WHY IT EXISTS:
 *   To carry a movie's data from one screen to another without depending on the UI.
 *   `MainActivity` holds a list of `Movie`; `ItemActivity` builds a `Movie`.
 *
 * WHAT IT KNOWS:
 *   Only the values: title, date, genre, budget, duration, rating, watched, approval,
 *   onWatchlist, poster. It does not know what an `EditText`, an `Intent` or a `ListView` is.
 *
 * WHAT WOULD BREAK WITHOUT IT:
 *   The entire data flow. `Intent.putExtra` would have nothing to serialise, `ArrayAdapter`
 *   would have nothing to display, and `ItemActivity` would have to send 10 separate extras
 *   and reassemble them by hand in `MainActivity`.
 * ======================================================================================
 */

package ro.ase.ie.g1097.model;

// ======================================================================================
// IMPORT 1: java.io.Serializable
// ======================================================================================
// WHAT IT IS: a MARKER interface — it has no method to implement.
// WHY HERE: `Intent.putExtra(String, Serializable)` is the simplest way to
//   send a whole object to another activity. Without `implements Serializable`,
//   the call `intent.putExtra(MOVIE_EXTRA, movie)` finds no matching overload
//   and DOES NOT COMPILE.
// WHAT HAPPENS AT RUNTIME: the JVM serialises the object graph into bytes, puts it
//   in the `Bundle`, and the receiving activity gets a DESERIALISED COPY.
// RISK: without a declared `serialVersionUID`, the JVM computes one from the class structure.
//   If you add a field between writing and reading (different processes), you get
//   `InvalidClassException`. Here the write and the read happen in the SAME process,
//   a few milliseconds apart, so the risk is theoretical.
// ======================================================================================
import java.io.Serializable;

// ======================================================================================
// IMPORT 2: java.util.Date
// ======================================================================================
// WHAT IT IS: a moment in time, stored internally as a number of milliseconds since 1 January 1970.
// WHY HERE: the release date must be a DATE, not a text. As a `Date` you can
//   sort, compare and format it with `SimpleDateFormat`.
// WHY NOT `String`: you would store "16/07/2010" and lose the ability to compute.
//   `fillForm` would have to parse on every display, and `saveMovie` would have to
//   format on every save — two places where you can get the format wrong.
// WHY NOT `java.time.LocalDate`: it is newer and cleaner, but `Date` is
//   `Serializable` out of the box and is the type required by the assignment statement.
// RISK: `Date` is MUTABLE. `getRelease()` returns the internal reference, not a copy,
//   so a careless caller can change the date in the object without going through the setter.
// ======================================================================================
import java.util.Date;

/*
 * ======================================================================================
 * THEORY BLOCK: WHY A SEPARATE MODEL (POJO)
 * ======================================================================================
 *
 * 1. **Single Responsibility** — the class has a single reason to change: the
 *    structure of a movie's data changes. It does not change when a layout, a button
 *    or a colour changes. If you put `getText().toString()` here, the class would depend on
 *    `android.widget.EditText` and would have two reasons to change.
 *
 * 2. **Serializability** — being `Serializable` and holding no references to a `Context`,
 *    the object can cross the boundary between two activities. A `Movie` that held
 *    an `EditText` could not be serialised: `View` is not `Serializable`.
 *
 * 3. **Testability** — you can write a simple JVM test that creates a `Movie` and
 *    checks `getTitle()`. No emulator, no Android. That happens because
 *    the file contains no `import android.*` at all.
 *
 * 4. **No `id` field** — a movie's identity in the list is its POSITION, not an ID.
 *    The whole `POSITION_EXTRA` mechanism in the other two files comes from this.
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
 *   The original stays in MainActivity's list. Changes to the copy are NOT visible
 *   in the list. That is why MainActivity calls `movies.set(position, movie)` at the end.
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
    //   on every display, and a badly typed text would reach the model as it is.
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
    //   in `arrays.xml` would retroactively change the genre of every saved movie.
    // ==================================================================================
    private String genre; //Spinner

    // ==================================================================================
    // FIELD 4: budget
    // ==================================================================================
    // TYPE: double — a number with decimals, precision of ~15–16 significant digits.
    // SOURCE WIDGET: `etBudget` (inputType=numberDecimal) -> `Double.parseDouble(...)`.
    // WHY double and not float: `float` has ~7 significant digits. For 160,000,000
    //   both are exact, but 160,000,001 would not be exactly representable in `float`.
    //   On top of that, `Double.parseDouble` returns `double` — a `float` field would need a cast.
    // WHAT BREAKS IF IT IS WRONG: if it were `int`, the decimals would be truncated;
    //   if it were `String`, you could not compare budgets.
    // ==================================================================================
    private double budget; //EditText number

    // ==================================================================================
    // FIELD 5: duration
    // ==================================================================================
    // TYPE: int — a whole number of minutes, 0..300.
    // SOURCE WIDGET: `sbDuration` (SeekBar) -> `getProgress()`.
    // WHY int: `SeekBar.getProgress()` returns `int`. Any other type would need a cast.
    // WHAT BREAKS IF IT IS WRONG: if it were `String`, `setProgress` would need parsing
    //   and you could save "abc" as a duration.
    // ==================================================================================
    private int duration; //SeekBar

    // ==================================================================================
    // FIELD 6: rating
    // ==================================================================================
    // TYPE: float — the score in half stars (0.0, 0.5, ..., 5.0).
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
    // WHAT BREAKS IF IT IS WRONG: if it were `String` ("Yes"/"No"), every `if` would need
    //   a text comparison, and a lowercase "yes" would be treated as false.
    // ==================================================================================
    private boolean watched; //Switch

    // ==================================================================================
    // FIELD 8: approval
    // ==================================================================================
    // TYPE: String — the TEXT of the selected radio button ("G", "PG", "PG-13", "R", "NC-17").
    // SOURCE WIDGET: `rgApproval` (RadioGroup) -> loop over the children + `getText()`.
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
    // WHY boolean: a check mark is binary. Independent of `watched`: you can have seen
    //   the movie AND keep it on the rewatch list.
    // WHAT BREAKS IF IT IS WRONG: if you reused `watched` for both, the two
    //   controls would contradict each other on save.
    // ==================================================================================
    private boolean onWatchlist; //Checkbox

    // ==================================================================================
    // FIELD 10: poster
    // ==================================================================================
    // TYPE: String — a URL (or any text) to the movie's poster.
    // SOURCE WIDGET: `etPoster` (inputType=textUri) -> `getText().toString()`.
    // WHY `= null` explicitly: a `String` is `null` by default anyway. The line is
    //   DOCUMENTATION: "this field may be missing". A movie without a poster is valid.
    // RISK: `null` reaches `etPoster.setText(null)` on edit — legal, but it shows
    //   an empty field. If you called `.length()` on it, you would get `NullPointerException`.
    // ==================================================================================
    private String poster = null;

    // ==================================================================================
    // THE CONSTRUCTOR WITH 10 PARAMETERS
    // ==================================================================================
    // WHY IT EXISTS: `addSampleMovies()` in MainActivity creates the 3 demo movies
    //   in a single expression. Without it, there would be 10 setter calls per movie.
    //
    // THE TRAP: the order of the parameters is POSITIONAL. The names in the signature do not help
    //   at the call site — the compiler only looks at types and position.
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
    //     10      String    poster         etPoster (textUri)
    //
    //   If you swap positions 1 and 3 (both String) or 7 and 9 (both boolean),
    //   the code COMPILES. The movie is created. It is just that `title` receives the genre and
    //   `genre` receives the title. The compiler cannot help you here.
    // ==================================================================================
    public Movie(String title, Date release, String genre, double budget, int duration, float rating, boolean watched, String approval, boolean onWatchlist, String poster) {

        // `this.title` = the class field; `title` = the parameter.
        // Without `this.`, the line would be `title = title` — self-assignment, the field stays null.
        this.title = title;

        // The same pattern for each of the 10 fields. All 10 lines
        // are structurally identical; if one is missing, the field keeps its
        // default value (null / 0 / 0.0 / false) and the bug only shows up at display time.
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

    // ==================================================================================
    // toString() — THE DISPLAY CONTRACT IN THE LIST
    // ==================================================================================
    // WHY IT IS MANDATORY HERE:
    //   `ArrayAdapter` with `android.R.layout.simple_list_item_1` receives a `TextView`
    //   and fills it with `item.toString()`. Without the override, `Object.toString()` would
    //   return `ro.ase.ie.g1097.model.Movie@a1b2c3d` — the address in memory.
    //
    // THE EXACT FLOW:
    //   ListView.getView(position) -> ArrayAdapter.getView(...) -> TextView.setText(
    //   movies.get(position).toString())
    //
    // WHY `@Override`: the compiler checks the signature. If you write `tostring()`
    //   in lowercase, without the annotation you get no error at all — your method
    //   is simply never called.
    //
    // THE FORMAT: generated by IntelliJ with Alt+Insert -> toString(). `'\''` is an
    //   escaped apostrophe, so that it does not close the character literal.
    //
    // WHAT YOU SEE ON SCREEN: all 10 fields, on a single line, including the poster
    //   URL. Ugly, but correct. It is fixed in the next chapter with RecyclerView
    //   and `movie_item.xml`.
    // ==================================================================================
    @Override
    public String toString() {

        // String concatenation with `+`. Every `+` creates a new object in memory.
        // For 10 fields the difference is negligible; for large loops you would use
        // `StringBuilder`.
        return "Movie{" +

                // The text fields are wrapped in apostrophes, so that the limits of the
                // value are visible: `title='Inception'`. Without them, `title=''` and `genre=''`
                // would be indistinguishable from an empty field.
                "title='" + title + '\'' +

                // `Date` is not wrapped in apostrophes: its `toString()` already produces
                // a readable format (`Sat Jul 16 00:00:00 GMT+03:00 2010`).
                ", release=" + release +

                // The comma at the start, not at the end: the last field does not need
                // a separator, and `}` is glued on correctly.
                ", genre='" + genre + '\'' +
                ", budget=" + budget +
                ", duration=" + duration +
                ", rating=" + rating +
                ", watched=" + watched +
                ", approval='" + approval + '\'' +
                ", onWatchlist=" + onWatchlist +
                ", poster='" + poster + '\'' +

                // The closing brace of the object, as text.
                '}';
    }

    // ==================================================================================
    // GETTERS AND SETTERS — 20 METHODS, ALL MECHANICAL
    // ==================================================================================
    // WHY THEY EXIST: the fields are `private`. Code in other packages (and even in
    //   `activities`) cannot read or write them directly. The getters and setters
    //   are the only interface.
    //
    // WHY SO MANY: 10 fields x 2 = 20. They are generated automatically by IntelliJ
    //   (Alt+Insert -> Getter and Setter). You do not write them by hand in the exam.
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
    // the constructor with 10 parameters.
    public void setTitle(String title) {
        this.title = title;
    }

    // GETTER for Date. WARNING: it returns the REFERENCE, not a copy.
    // RISK: `movie.getRelease().setTime(0)` would change the date in the object without a setter.
    //   A correct variant would be `return new Date(release.getTime());`.
    public Date getRelease() {
        return release;
    }

    // SETTER for Date. It does not validate `null` — a `Movie` with a null date is accepted
    // by the model and crashes only in `fillForm` (see BUG 2).
    public void setRelease(Date release) {
        this.release = release;
    }

    // GETTER for genre. The value comes from the Spinner, but the model does not know that.
    public String getGenre() {
        return genre;
    }

    // SETTER for genre. It does not check whether the value exists in `@array/movie_genre`.
    // Validation is the UI's responsibility, not the model's.
    public void setGenre(String genre) {
        this.genre = genre;
    }

    // GETTER for budget. `double` is copied by value — there are no aliasing
    // problems as with Date.
    public double getBudget() {
        return budget;
    }

    // SETTER for budget. It does not reject negative values: a budget of -5 would be accepted.
    // Validation should be done in `saveMovie`, before the call.
    public void setBudget(double budget) {
        this.budget = budget;
    }

    // GETTER for duration, in minutes.
    public int getDuration() {
        return duration;
    }

    // SETTER for duration. It does not clamp to 0..300 — the limit exists only in XML
    // (`android:max="300"`), that is, only in the UI.
    public void setDuration(int duration) {
        this.duration = duration;
    }

    // GETTER for rating. `float` — the score in half stars.
    public float getRating() {
        return rating;
    }

    // SETTER for rating. The parameter is `float`, exactly the type required by
    // `RatingBar.setRating(float)`.
    public void setRating(float rating) {
        this.rating = rating;
    }

    // ==================================================================================
    // WHY `isWatched()` AND NOT `getWatched()`
    // ==================================================================================
    // 1. THE JAVABEANS CONVENTION: for `boolean`, the getter is called `isX()`, not `getX()`.
    //    Reflection (and frameworks that read properties) look for the `is` prefix.
    // 2. CONSISTENCY: `isOnWatchlist()` follows the same rule. If one were
    //    `getWatched()` and the other `isOnWatchlist()`, the code would be hard to read.
    // 3. THE CODE DEPENDS ON THE NAME: `fillForm` calls `existing.isWatched()`. If you had
    //    written `getWatched()`, the call would not compile — and it has to be changed in two places.
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

    // GETTER for the "Watchlist" check mark. `is` prefix — again the JavaBeans convention.
    public boolean isOnWatchlist() {
        return onWatchlist;
    }

    // SETTER for the check mark.
    public void setOnWatchlist(boolean onWatchlist) {
        this.onWatchlist = onWatchlist;
    }

    // GETTER for the poster URL. It may return `null`.
    public String getPoster() {
        return poster;
    }

    // SETTER for the poster. It accepts `null` without complaining.
    public void setPoster(String poster) {
        this.poster = poster;
    }

    // ==================================================================================
    // THE CONSTRUCTOR WITHOUT PARAMETERS — THE LAST LINE OF THE FILE
    // ==================================================================================
    // WHY IT MUST BE WRITTEN EXPLICITLY:
    //   The Java rule: if you define ANY constructor with parameters, the compiler
    //   NO LONGER generates the no-argument constructor automatically.
    //   `saveMovie()` in ItemActivity does `Movie movie = new Movie();`.
    //   Without this constructor, the file DOES NOT COMPILE.
    //
    // WHY THE BODY IS EMPTY: all fields receive their default values
    //   (null / 0 / 0.0 / false). The object is filled immediately with setters.
    //
    // WHY IT IS AT THE END: the position does not matter to the compiler. It is at the end
    //   because that is how IntelliJ generated it and because the reader sees it after
    //   all the methods it depends on.
    // ==================================================================================
    public Movie() {
    }
}
```

---

## 22.2 `MainActivity.java` — the list and navigation

```java
/*
 * ======================================================================================
 * FILE: MainActivity.java — THE SCREEN WITH THE LIST
 * ======================================================================================
 * WHAT IT IS: the start activity. It holds the list of movies, displays it with an `ArrayAdapter`
 *   in a `ListView` and starts `ItemActivity` for insert or edit.
 *
 * WHY IT EXISTS: it is the only place that owns the application STATE (the `movies` list).
 *   `ItemActivity` is just a form that produces a `Movie` and sends it back.
 *
 * WHAT IT KNOWS: the list, the adapter, the two extras, the result launcher.
 *   It does not know what the form looks like and it does not validate data.
 *
 * WHAT WOULD BREAK WITHOUT IT: the application would start directly in a form with no list,
 *   and the saved result would have nowhere to return to.
 * ======================================================================================
 */

package ro.ase.ie.g1097.activities;

// ======================================================================================
// IMPORTS — GROUPED BY SOURCE
// ======================================================================================
// android.*        — framework classes (Intent, Bundle, View, widgets)
// androidx.*       — Jetpack libraries (AppCompat, EdgeToEdge, insets, activity result)
// com.google.*     — Material Components (FloatingActionButton)
// java.util.*      — collections and dates
// ro.ase.ie.g1097  — the model and the generated R class
// ======================================================================================

// Intent: the object that describes "which activity you start" and what data it carries.
import android.content.Intent;

// Bundle: the state bag saved by the system (used here only in the onCreate signature).
import android.os.Bundle;

// View: the base class for any UI element. It appears in the listener signatures.
import android.view.View;

// AdapterView: the base class for ListView/Spinner. Here only for OnItemClickListener.
import android.widget.AdapterView;

// ArrayAdapter: the bridge between `List<Movie>` and the rows in the ListView.
import android.widget.ArrayAdapter;

// ListView: the widget that displays the scrollable list.
import android.widget.ListView;

// Toast: short messages. Imported in the source, but UNUSED in this file.
import android.widget.Toast;

// EdgeToEdge: enables drawing under the system bars (status + navigation).
import androidx.activity.EdgeToEdge;

// ActivityResult: the result returned by the secondary activity (code + Intent).
import androidx.activity.result.ActivityResult;

// ActivityResultCallback: the single-method interface, called on return.
import androidx.activity.result.ActivityResultCallback;

// ActivityResultLauncher: the object that starts the activity and holds the link to the callback.
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

// Date: the type stored in the model for the release date.
import java.util.Date;

// GregorianCalendar: the quick "year, month, day" constructor used in the demo data.
import java.util.GregorianCalendar;

// List: the list interface. The field is declared `List`, not `ArrayList`.
import java.util.List;

// The data model — the only dependency on `model`.
import ro.ase.ie.g1097.model.Movie;

// R: the class generated from resources. Here for `R.layout.activity_main` and `R.id.*`.
import ro.ase.ie.g1097.R;

/*
 * ======================================================================================
 * THEORY BLOCK: ACTIVITY, INTENT, ADAPTER
 * ======================================================================================
 *
 * 1. **Activity = a screen with a state.** `MainActivity` is a `Context` (it has access to
 *    resources, theme, system) and a `LifecycleOwner` (it has a lifecycle: onCreate ->
 *    onStart -> onResume -> onPause -> onStop -> onDestroy).
 *
 * 2. **Intent = a message.** An explicit `Intent` contains the target class and a `Bundle`
 *    of extras. Starting is done with `startActivity` (without a result) or with an
 *    `ActivityResultLauncher` (with a result).
 *
 * 3. **Adapter = the translator.** `ListView` does not know what a `Movie` is. `ArrayAdapter`
 *    does: for each position, it takes `movies.get(position)` and turns it into a
 *    UI row. Without an adapter, `ListView` would display a list of empty objects.
 *
 * 4. **The order in onCreate is a contract, not style.** Each step depends on the previous one:
 *    without `super`, AppCompat has no delegate; without `setContentView`, `findViewById`
 *    returns null; without an adapter, `setAdapter` receives null.
 *
 * VISUAL: the lifecycle during an insert
 *
 *   MainActivity:  onCreate -> onStart -> onResume -> onPause
 *                                                        |
 *                                                        v
 *   ItemActivity:                                   onCreate -> onStart -> onResume
 *                                                        |
 *                                                   (the user saves)
 *                                                        |
 *                                                   setResult + finish
 *                                                        |
 *   MainActivity:  onStart -> onResume -> [launcher callback] -> list redrawn
 *
 *   MainActivity is NOT destroyed while ItemActivity is on top. It is only
 *   stopped. That is why the `movies` list survives and why the callback can
 *   modify it directly.
 * ======================================================================================
 */
public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // THE EXTRA CONSTANTS
    // ==================================================================================
    // WHY CONSTANTS AND NOT LITERALS: the key "movie" is written in two files.
    //   If in one place you write "movie" and in another "Movie", `getSerializableExtra`
    //   returns `null` WITH NO ERROR AT ALL. The compiler does not help you with Strings.
    //
    // WHY `protected`: `ItemActivity` is in the same package, so `package-private` would
    //   work too. `protected` documents the intention: "it is used from
    //   subclasses / from nearby code".
    //
    // WHY `static`: the value belongs to the class, not to the instance. `MainActivity.MOVIE_EXTRA`
    //   can be written without a MainActivity object existing.
    //
    // WHY `final`: the key must never change at runtime.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";

    // ==================================================================================
    // FIELD 1: fabInsert
    // ==================================================================================
    // TYPE: FloatingActionButton — the "+" button.
    // WHY A FIELD: it is bound in `initControls` and used in `initListeners`.
    //   A local variable in `initControls` would die at the end of the method.
    // ==================================================================================
    private FloatingActionButton fabInsert;

    // ==================================================================================
    // FIELD 2: listView
    // ==================================================================================
    // TYPE: ListView — the widget that displays the rows.
    // WHY A FIELD: bound in `initControls`, a listener is attached to it in `initListeners`.
    // ==================================================================================
    private ListView listView;

    // ==================================================================================
    // FIELD 3: launcher
    // ==================================================================================
    // TYPE: ActivityResultLauncher<Intent> — the object returned by `registerForActivityResult`.
    // WHY A FIELD: it is created in `onCreate` and used in `initListeners`, in two
    //   places (the FAB and the row click).
    // ORDER RISK: `initListeners()` runs BEFORE this field is assigned.
    //   It works only because the listeners execute on CLICK, not at registration.
    // ==================================================================================
    private ActivityResultLauncher<Intent> launcher;

    // ==================================================================================
    // FIELD 4: movies
    // ==================================================================================
    // TYPE: `final List<Movie>` initialised with `ArrayList`.
    // WHY `List` and not `ArrayList`: the declared type is the interface. The implementation
    //   can be changed (e.g. `LinkedList`) without modifying the rest of the code.
    // WHY `final`: the REFERENCE never changes. You can do `movies.add(...)`,
    //   `movies.set(...)`, but not `movies = new ArrayList<>()`.
    // WHY `new ArrayList<>()` here: the list must exist before `onCreate`,
    //   because `ArrayAdapter` receives the reference to it.
    // ==================================================================================
    private final List<Movie> movies = new ArrayList<>();

    // ==================================================================================
    // FIELD 5: movieAdapter
    // ==================================================================================
    // TYPE: ArrayAdapter<Movie> — the adapter that links the list to the ListView.
    // WHY IT IS NOT `final`: it is assigned in `onCreate`, after `addSampleMovies()`.
    // WHY A FIELD: `notifyDataSetChanged()` is called from inside the callback,
    //   where you need the same instance.
    // ==================================================================================
    private ArrayAdapter<Movie> movieAdapter;

    // ==================================================================================
    // onCreate — THE SCREEN'S REAL CONSTRUCTOR
    // ==================================================================================
    // The signature is imposed by the framework: `protected void onCreate(Bundle)`.
    // `savedInstanceState` is `null` on first creation and a `Bundle` on recreation
    //   (screen rotation, theme change). Here it is NOT used: the list is lost
    //   on rotation. This is a known limitation of this commit.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // STEP 1: start the parent class's initialisation chain.
        // WHAT IT DOES: AppCompat installs its delegate, loads the theme, creates
        //   the ActionBar and prepares the `FragmentManager`.
        // WHAT BREAKS IF IT IS MISSING: `SuperNotCalledException` at `onStart`, or
        //   `NullPointerException` in `setContentView` because the delegate does not exist.
        // WHAT BREAKS IF IT IS TOO LATE (after setContentView): AppCompat can no longer
        //   apply the theme to the window; you may see a flash of the wrong colour.
        super.onCreate(savedInstanceState);

        // STEP 2: enable edge-to-edge mode.
        // WHAT IT DOES: sets the windows to draw under the system bars as well, so
        //   that the content can occupy the whole screen. The bars become transparent.
        // WHY BEFORE setContentView: the window configuration must be done
        //   before the first view is attached, otherwise you may see a recolouring.
        // CONSEQUENCE: the content goes UNDER the clock and under the navigation bar. That is why
        //   step 4 applies padding.
        EdgeToEdge.enable(this);

        // STEP 3: fill the window with the view tree from XML.
        // WHAT IT DOES: inflates `res/layout/activity_main.xml` and attaches it to the window.
        // WHY BEFORE findViewById: before this call, `findViewById` has
        //   nowhere to search and returns `null` for any ID.
        // WHAT BREAKS IF IT IS MISSING: white screen; any `findViewById` -> null -> NPE.
        setContentView(R.layout.activity_main);

        // STEP 4: apply padding equal to the system bars on the root.
        // ==============================================================================
        // VISUAL: the safe area
        //
        //   +--------------------------------------------------+  ^
        //   |  clock  battery  notifications                   |  | status bar (~24dp)
        //   +--------------------------------------------------+  v
        //   |                                                  |  ^
        //   |                                                  |  |
        //   |            CONTENT (padding applied)             |  | screen
        //   |                                                  |  |
        //   |                                                  |  |
        //   +--------------------------------------------------+  v
        //   |  back  home  recents                             |  ^  navigation bar (~48dp)
        //   +--------------------------------------------------+  v
        //
        //   Without padding: the first row of the list goes under the clock, and the FAB goes
        //   under the navigation bar and becomes impossible to tap.
        //   With padding on R.id.main: ALL children are pushed into the safe area.
        // ==============================================================================
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // Extracts the insets for "systemBars": status bar + navigation bar
            // + caption bar. It does not include the keyboard (IME), which would be `Type.ime()`.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // Applies padding on all four sides, in pixels.
            // WHY on the root: padding on a child would push only that child;
            //   the others would stay under the bars.
            // SIDE EFFECT: the padding is REAPPLIED on every insets change
            //   (rotation, navigation bar appearing/disappearing). `setPadding` does not add,
            //   it replaces — so it does not accumulate.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // `return insets` (not `CONSUMED`): the insets keep flowing to the
            // children. If you returned `WindowInsetsCompat.CONSUMED`, no child
            // would receive the information any more and each would have to apply its own padding.
            return insets;
        });

        // STEP 5: fill the list with 3 demo movies.
        // WHY BEFORE creating the adapter: the adapter receives the REFERENCE to the list.
        //   By filling the list first, the adapter already sees 3 elements at construction and
        //   you do not need `notifyDataSetChanged()`.
        // If you called `addSampleMovies()` after `new ArrayAdapter(...)`, it would work
        //   then too (same reference), but you would need a `notifyDataSetChanged()`
        //   for the ListView to redraw.
        addSampleMovies();

        // STEP 6: create the adapter.
        // Parameters:
        //   1. `this` — the Context (MainActivity is a Context).
        //   2. `android.R.layout.simple_list_item_1` — a layout that contains ONE TextView.
        //   3. `movies` — the data list, held by REFERENCE, not copied.
        // WHY `android.R.layout` and not `R.layout`: it is a layout from the framework,
        //   not from the project.
        // WHY `<>` (diamond): the compiler infers `ArrayAdapter<Movie>` from `movies`.
        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

        // STEP 7: bind the views to the fields and attach the adapter.
        // WHY AFTER creating the adapter: `initControls` does `listView.setAdapter(movieAdapter)`.
        //   If `movieAdapter` were null, `setAdapter(null)` would leave the list empty.
        initControls();

        // STEP 8: attach the listeners.
        // WHY AFTER `initControls`: the listeners need `fabInsert` and `listView`,
        //   which are assigned there. Before, they would be null -> NPE at registration.
        // NOTE: `launcher` is still null at this moment. See step 9.
        initListeners();

        // STEP 9: register the callback for the result.
        // ==============================================================================
        // WHY HERE AND NOT INSIDE A LISTENER:
        //   `registerForActivityResult` must be called BEFORE the activity
        //   reaches the STARTED state. Otherwise you get:
        //   "LifecycleOwner ... is attempting to register while current state is RESUMED.
        //    LifecycleOwners must call register before they are STARTED."
        //   That is why the registration sits in `onCreate`, not in `onClick`.
        //
        // THE FLOW:
        //   [onCreate] registerForActivityResult(contract, callback)
        //        |
        //        v
        //   [FAB click] launcher.launch(intent)
        //        |
        //        v
        //   ItemActivity opens; MainActivity -> onPause
        //        |
        //        v
        //   ItemActivity: setResult(RESULT_OK, intent) + finish()
        //        |
        //        v
        //   MainActivity returns: onStart -> onResume
        //        |
        //        v
        //   callback.onActivityResult(result)   <-- the list is modified here
        // ==============================================================================
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // The callback is an anonymous class. It can also be written as a lambda, but
                // the source uses the explicit form — useful in the exam for clarity.
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // MANDATORY CHECK: did a good result arrive?
                        // If the user presses Back, `ItemActivity` closes with
                        // RESULT_CANCELED, and `o.getData()` is null.
                        // Without this `if`, the next `intent.getSerializableExtra`
                        // would throw NullPointerException.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // Extracts the result Intent. It can be null if
                            // the activity called `setResult(RESULT_OK)` without an Intent —
                            // that does not happen here, but it is a theoretical risk.
                            Intent intent = o.getData();

                            // Reads the serialised object. The cast is needed because
                            // `getSerializableExtra` returns `Serializable`.
                            // RISK: if the object were not a `Movie`, the cast would throw
                            //   `ClassCastException` at runtime.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // Reads the position. The default value `-1` is the KEY
                            // of the whole protocol: -1 means "there is no position",
                            // that is, insert.
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // INSERT MODE: ItemActivity did not send a position.
                            if(position == -1)
                            {
                                // Adds at the end of the list.
                                movies.add(movie);

                                // Tells the adapter that the data has changed.
                                // WITHOUT THIS LINE: the movie is in the list, but
                                // the ListView does not redraw and the user
                                // sees nothing until the next recreation.
                                movieAdapter.notifyDataSetChanged();
                            }
                            // EDIT MODE: ItemActivity sent the position.
                            else
                            {
                                // Replaces the element at that position.
                                // `set` does not change the size of the list.
                                movies.set(position, movie);

                                // Here too it is mandatory: `set` notifies nobody.
                                movieAdapter.notifyDataSetChanged();
                            }
                        }

                        // If resultCode != RESULT_OK, we do nothing. The list stays
                        // untouched, exactly as before the form was opened.
                    }
                });
    }

    // ==================================================================================
    // initListeners — WHAT HAPPENS ON INTERACTION
    // ==================================================================================
    // Two actions: the FAB (insert) and the row click (edit).
    // Both start the SAME activity, with different extras.
    // ==================================================================================
    private void initListeners() {

        // FAB -> INSERT
        // Anonymous class `View.OnClickListener` with a single method `onClick`.
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // `MainActivity.this` AND NOT `this`.
                // ==========================================================================
                // WHY: inside the anonymous class, `this` is the LISTENER INSTANCE,
                //   not the activity. `new Intent(this, ItemActivity.class)` would look for a
                //   constructor `Intent(View.OnClickListener, Class)` — which does not exist —
                //   and would NOT compile.
                // `MainActivity.this` is the qualified reference to the outer instance,
                //   which IS a `Context`.
                // ==========================================================================
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // Starts the activity THROUGH THE LAUNCHER, not through `startActivity`.
                // WHY: `startActivity` starts the screen, but has nowhere to return
                //   the result to. `launcher.launch` knows who receives the answer.
                // WITHOUT EXTRAS: ItemActivity sees `existing == null` -> insert mode.
                launcher.launch(intent);
            }
        });

        // ROW CLICK -> EDIT
        // `AdapterView.OnItemClickListener` has a single method with 4 parameters.
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                // The parameters:
                //   `parent`   — the ListView (not used here)
                //   `view`     — the pressed row (not used here)
                //   `position` — the index in the adapter; THIS is what interests us
                //   `id`       — the row id; for ArrayAdapter it equals the position

                // The same kind of Intent: the same activity, different content.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // Sends the selected movie. `putExtra(String, Serializable)` is
                // the overload chosen because `Movie implements Serializable`.
                // THE OBJECT IS SERIALISED — a COPY arrives in ItemActivity.
                intent.putExtra(MOVIE_EXTRA, movies.get(position));

                // Sends the position too. It is the only thing that distinguishes edit from insert.
                // `int` -> `putExtra(String, int)`.
                intent.putExtra(POSITION_EXTRA, position);

                // Starts for a result, exactly as on insert.
                launcher.launch(intent);
            }
        });
    }

    // ==================================================================================
    // initControls — THE XML <-> CODE LINK
    // ==================================================================================
    // Three lines, three responsibilities: two `findViewById` and one adapter attachment.
    // ==================================================================================
    private void initControls() {

        // `findViewById` searches the tree inflated at `setContentView`.
        // In modern Java, the method is generic: the type is inferred from the variable on the left.
        //   The old equivalent: `(FloatingActionButton) findViewById(R.id.floatingActionButton)`.
        // If the ID does not exist in the layout, it returns `null` WITH NO error — NPE at the first access.
        fabInsert = findViewById(R.id.floatingActionButton);

        // The same for the list. The ID `listView` exists in `activity_main.xml`.
        listView = findViewById(R.id.listView);

        // Attaches the adapter. From this moment on, the ListView knows what to display.
        // WHY THE LAST LINE: it needs `listView` (already assigned) and
        //   `movieAdapter` (assigned in onCreate before this method is called).
        listView.setAdapter(movieAdapter);
    }

    // ==================================================================================
    // addSampleMovies — THE DEMO DATA
    // ==================================================================================
    // Three movies built with the 10-parameter constructor. This is where, in practice, the
    // positional trap described in 22.1 becomes visible: every call has exactly 10 arguments, in
    // the order of the signature.
    //
    // WHY IT EXISTS: so that you have something to see on first launch, without entering data by hand.
    // WHY IN CODE AND NOT IN RESOURCES: they are objects, not texts; an XML array would need
    //   parsing and type conversions.
    // ==================================================================================
    private void addSampleMovies() {

        // MOVIE 1: Inception
        // The arguments, in order:
        //   1. "Inception"                                          -> String title
        //   2. new GregorianCalendar(2010, Calendar.JULY, 16).getTime() -> Date release
        //   3. "Sci-Fi"                                             -> String genre
        //   4. 160000000                                            -> double budget
        //   5. 148                                                  -> int duration
        //   6. 4.5f                                                 -> float rating
        //   7. true                                                 -> boolean watched
        //   8. "PG-13"                                              -> String approval
        //   9. false                                                -> boolean onWatchlist
        //  10. "https://example.com/posters/inception.jpg"          -> String poster
        movies.add(new Movie(
                "Inception",

                // `GregorianCalendar(year, month, day)`:
                //   - the year is ABSOLUTE (2010), not relative;
                //   - the month is 0-INDEXED: `Calendar.JULY` = 6, not 7. That is why
                //     the constants are used, not the numbers — `new GregorianCalendar(2010, 7, 16)`
                //     would mean 16 AUGUST;
                //   - the day is 1-indexed, as in real life.
                // `.getTime()` turns the Calendar into a `Date` (milliseconds).
                //   `GregorianCalendar` IS a `Calendar`, but is NOT a `Date`.
                new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),

                // The genre — plain text, it does not have to exist in `@array/movie_genre`.
                "Sci-Fi",

                // The budget: an `int` literal (160,000,000) widened automatically to `double`.
                // It needs no suffix; `160000000.0` would be equivalent.
                160000000,

                // The duration: an `int` literal, in minutes.
                148,

                // The rating: a `float` literal. The `f` suffix is MANDATORY.
                // Without it, `4.5` would be a `double` and would not match the `float` parameter
                // without an explicit cast.
                4.5f,

                // `watched` — a movie that has been seen.
                true,

                // `approval` — the text of the radio button, not the ID.
                "PG-13",

                // `onWatchlist` — it is not on the rewatch list.
                false,

                // `poster` — a fictitious URL. It is not downloaded anywhere in this commit.
                "https://example.com/posters/inception.jpg"));

        // MOVIE 2: Toy Story
        // The same structure, different values. `Calendar.NOVEMBER` = 10 (0-indexed).
        // `4f` is also a `float` literal, just without decimals.
        // WARNING: the genre "Animation" does NOT exist in `@array/movie_genre` (Drama, Action,
        //   Comedy, Horror, Romance, Thriller, Sci-Fi, Adventure, Fantasy, Mystery).
        //   The consequence appears on edit: `fillForm` finds no match, the spinner
        //   stays on "Drama", and saving changes the movie's genre. See 22.3.
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

        // MOVIE 3: The Matrix
        // `Calendar.MARCH` = 2 (0-indexed). `5f` = maximum rating.
        // `watched = false` and `onWatchlist = true` — the combination "I have not seen it,
        // but I want to". It is the only movie of the three with this combination,
        // useful for checking the two independent controls.
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

**What to remember from this file:**

| Element | Why it matters |
|---|---|
| The order in `onCreate` | each step depends on the previous one; `launcher` is last |
| `EdgeToEdge` + insets | without padding on `R.id.main`, the content goes under the bars |
| `new ArrayAdapter(..., movies)` | it holds the REFERENCE to the list, not a copy |
| `notifyDataSetChanged()` | the only way the ListView learns about a change |
| `registerForActivityResult` | mandatory before `STARTED`, hence in `onCreate` |
| `MainActivity.this` | in the anonymous class, `this` is not a `Context` |

---

## 22.3 `ItemActivity.java` — the form

```java
/*
 * ======================================================================================
 * FILE: ItemActivity.java — THE INSERT / EDIT FORM
 * ======================================================================================
 * WHAT IT IS: an activity with 13 views, a Calendar and a date formatter.
 *   It builds a `Movie` from the values in the form and sends it back.
 *
 * WHY IT EXISTS: `MainActivity` is not allowed to create model objects from a form.
 *   The separation means the form can be changed (another layout, other fields) without
 *   touching the list.
 *
 * WHAT IT KNOWS: the current values of the 10 fields, the mode (insert or edit) and the position.
 *   It does not know what happens to the movie after `finish()`.
 *
 * WHAT WOULD BREAK WITHOUT IT: the application would only have the demo list, with no way
 *   to add or modify a movie.
 * ======================================================================================
 */

package ro.ase.ie.g1097.activities;

// ======================================================================================
// IMPORTS — WHAT EACH ONE BRINGS
// ======================================================================================
// android.app.DatePickerDialog   — the date-picking dialog
// android.content.Intent         — reading the extras on the way in and building
//                                  the result Intent
// android.os.Bundle              — the onCreate signature
// android.view.View              — the parameter in the click listeners
// android.widget.*               — the form's 13 widgets
// androidx.activity.EdgeToEdge   — drawing under the system bars
// androidx.annotation.NonNull    — the OnCheckedChangeListener contract
// androidx.core.content.IntentCompat — typed reading of a Serializable (API 33+)
// androidx.core.view.*           — insets
// com.google.android.material.*  — MaterialSwitch, Snackbar
// java.text.*                    — date parsing and formatting
// java.util.*                    — Calendar, Date, Locale
// ro.ase.ie.g1097.*              — R, binding, model
// ======================================================================================

// The native calendar dialog. It opens on a click on the date field.
import android.app.DatePickerDialog;

// Intent: on the way in, it brings the movie to edit; on the way out, it carries the saved movie.
import android.content.Intent;

// Bundle: the state saved by the system. Unused in the body, only in the signature.
import android.os.Bundle;

// View: the parameter type in `OnClickListener`.
import android.view.View;

// Button: the type of the save button. In XML it is a `MaterialButton`, which extends Button.
import android.widget.Button;

// CheckBox: the declared type of the field, although the real object is a `MaterialCheckBox`.
import android.widget.CheckBox;

// CompoundButton: the common interface for Switch and CheckBox; it appears in the listener.
import android.widget.CompoundButton;

// DatePicker: the first parameter of the `OnDateSetListener` callback.
import android.widget.DatePicker;

// EditText: the declared type for the 4 text fields.
import android.widget.EditText;

// RadioButton: used in the loop over the children of the RadioGroup.
import android.widget.RadioButton;

// RadioGroup: the container of the 5 guidance buttons.
import android.widget.RadioGroup;

// RatingBar: the stars.
import android.widget.RatingBar;

// SeekBar: the duration slider.
import android.widget.SeekBar;

// Spinner: the drop-down list of genres.
import android.widget.Spinner;

// Switch: imported, but the field is declared `MaterialSwitch`.
import android.widget.Switch;

// TextView: the dynamic labels for duration and watched.
import android.widget.TextView;

// Toast: imported in the source, but UNUSED in this file.
import android.widget.Toast;

// EdgeToEdge: content under the system bars.
import androidx.activity.EdgeToEdge;

// NonNull: the annotation from the onCheckedChanged signature.
import androidx.annotation.NonNull;

// AppCompatActivity: the base class.
import androidx.appcompat.app.AppCompatActivity;

// IntentCompat: an API 33 compatible variant for reading a typed Serializable.
import androidx.core.content.IntentCompat;

// Insets: the values of the system bars.
import androidx.core.graphics.Insets;

// ViewCompat: the compatible insets listener.
import androidx.core.view.ViewCompat;

// WindowInsetsCompat: the insets types.
import androidx.core.view.WindowInsetsCompat;

// MaterialSwitch: the Material switch (not the framework one).
import com.google.android.material.materialswitch.MaterialSwitch;

// Snackbar: imported, but UNUSED. Leftover from an earlier version.
import com.google.android.material.snackbar.Snackbar;

// ParseException: the exception thrown by `SimpleDateFormat.parse`.
import java.text.ParseException;

// SimpleDateFormat: formatting and parsing "dd/MM/yyyy".
import java.text.SimpleDateFormat;

// Calendar: the source of truth for the date.
import java.util.Calendar;

// Date: the type in the model.
import java.util.Date;

// Locale: the date format depends on the device language.
import java.util.Locale;

// R: the IDs from the layout.
import ro.ase.ie.g1097.R;

// ActivityItemBinding: generated by View Binding. Imported, but UNUSED —
//   the source uses `findViewById`. Leftover from a variant with binding.
import ro.ase.ie.g1097.databinding.ActivityItemBinding;

// The model.
import ro.ase.ie.g1097.model.Movie;

/*
 * ======================================================================================
 * THEORY BLOCK: THE FORM AS A STATE MACHINE
 * ======================================================================================
 *
 * 1. **Two modes, one activity.** `ItemActivity` does not have two layouts and
 *    two classes. It has a `position` field that is `-1` (insert) or `>= 0` (edit).
 *    All the different behaviour derives from this field.
 *
 * 2. **The source of truth is not always the widget.** For 9 fields, the widget
 *    is the source (you read directly from it on save). For the date, the source is
 *    `releaseCal`, and the `EditText` is only a DISPLAY.
 *
 * 3. **The listeners are also a source of truth for the labels.** `tvDurationValue`
 *    and `tvWatchedValue` are not read on save; they are updated by the widget
 *    listeners. If a listener does not fire, the label lags behind.
 *
 * 4. **The result is an Intent.** The activity does not return an object through a return value;
 *    it puts it in an `Intent` and hands it over through `setResult`.
 *
 * VISUAL: the data flow in the form
 *
 *   [etTitle] -------------------------+
 *   [etRelease] --(display only)--+    |
 *                                 |    |
 *   [releaseCal] -----------------+----+---> saveMovie() ---> Movie ---> Intent
 *   [spGenre] -------------------------+                                    |
 *   [etBudget] ------------------------+                                    v
 *   [sbDuration] ----------------------+                            setResult(RESULT_OK)
 *   [rbRating] ------------------------+                                    |
 *   [swWatched] -----------------------+                                    v
 *   [cbonWatchList] -------------------+                                  finish()
 *   [rgApproval] --(loop)---+----------+
 *   [etPoster] ------------------------+
 * ======================================================================================
 */
public class ItemActivity extends AppCompatActivity {

    // ==================================================================================
    // THE 13 REFERENCES TO THE VIEWS
    // ==================================================================================
    // WHY 13: the form has 10 data fields + 2 dynamic labels + 1 button.
    //   The 7 fixed-label `TextView`s (`tvTile`, `tvGenre`, `tvBudget`,
    //   `tvDuration`, `tvRating`, `tvWatched`, `tvGuidance`) do NOT appear here: they are not
    //   read and they are not modified from code, so they need no reference.
    //
    // WHY THEY ARE ALL `private`: they are implementation details of the screen.
    // ==================================================================================

    // Field 1: the title. The real object in XML is a `TextInputEditText`, but the declared
    // type is `EditText` — the parent class. It is enough for `getText()`.
    private EditText etTitle;

    // Field 2: the date, as TEXT. The real value is in `releaseCal` (see below).
    private EditText etRelease;

    // Field 3: the genre. `Spinner` — the drop-down list from `@array/movie_genre`.
    private Spinner spGenre;

    // Field 4: the budget. `inputType="numberDecimal"` in XML.
    private EditText etBudget;

    // Field 5: the duration. `SeekBar` with max 300.
    private SeekBar sbDuration;

    // Field 6: the rating. `RatingBar` with 5 stars and a 0.5 step.
    private RatingBar rbRating;

    // Field 7: the parental guidance. `RadioGroup` with 5 buttons.
    private RadioGroup rgApproval;

    // Field 8: the "Watchlist" check mark.
    // WATCH THE NAME: the field is `cbonWatchList`, the ID is `cbOnWatchList`.
    //   One `o` missing on one side, one `O` extra on the other. It is not a typo to fix:
    //   that is how the source is. `findViewById(R.id.cbonWatchList)` would NOT compile.
    private CheckBox cbonWatchList;

    // Field 9: the "Recommended" switch. The real type is `MaterialSwitch`, which
    // extends `SwitchCompat` -> `CompoundButton`. Declared `MaterialSwitch` in order
    // to have access to all of its methods.
    private MaterialSwitch swWatched;

    // Field 10: the poster URL.
    private EditText etPoster;

    // Field 11: the save button.
    // WATCH THE NAME: the field is `btMovieAction`, the ID is `btnMovieAction`.
    private Button btMovieAction;

    // Field 12: the label that displays the duration ("148 min."). It is NOT read on
    // save — it is display only, updated by the SeekBar listener.
    private TextView tvDurationValue;

    // Field 13: the label that displays "Yes"/"No" for the switch.
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
    // "dd/MM/yyyy" = two-digit day / two-digit month / four-digit year.
    //   WARNING: `MM` = month, `mm` = minutes. Swapping them is a classic mistake.
    // `Locale.getDefault()` = the device language's format. Here the pattern is
    //   explicit, so Locale only influences the symbols and the internal order.
    // `final`: the reference does not change. The object, however, is MUTABLE.
    // RISK: `SimpleDateFormat` is not thread-safe. Here it is used exclusively on
    //   the UI thread, so there is no concurrency.
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    // ==================================================================================
    // onCreate — THREE PHASES: INFRASTRUCTURE, CONTROLS, MODE
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // Phase 0: the AppCompat chain. Without it, the theme and the delegate do not exist.
        super.onCreate(savedInstanceState);

        // Edge-to-edge: the content can occupy the whole screen, including under the bars.
        // Here the root is a `ScrollView` with `android:id="@+id/main"`.
        EdgeToEdge.enable(this);

        // Inflates `activity_item.xml`. All 13 `findViewById` calls depend on it.
        setContentView(R.layout.activity_item);

        // Insets on the ScrollView root. Identical to MainActivity, but here the padding
        // is applied to a container that SCROLLS: the content scrolls inside
        // the safe area, not under it.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Phase 1: bind the 13 views to the fields.
        // WHY FIRST: `fillForm` needs them, and so does `initListeners`.
        initControls();

        // Phase 2: attach the listeners.
        // WHY BEFORE `fillForm`: `fillForm` calls `setChecked` and `setProgress`.
        //   Those calls FIRE the listeners, which update the
        //   `tvWatchedValue` and `tvDurationValue` labels. If the listeners were attached after
        //   `fillForm`, the labels would keep the default values from XML.
        initListeners();

        // Phase 3: read the incoming Intent.
        Intent intent = getIntent();

        // TYPED reading of the serializable.
        // ==============================================================================
        // WHY `IntentCompat` AND NOT `intent.getSerializableExtra(...)`:
        //   The old method is deprecated since API 33. `IntentCompat.getSerializableExtra`
        //   also receives the expected class, so it checks the type before the cast
        //   and works identically on all versions.
        // WHY `MainActivity.MOVIE_EXTRA`: the same constant as when sending. A typo
        //   here would produce `null` with no error at all.
        // THE VALUE: `null` in insert mode (the FAB puts no extra).
        // ==============================================================================
        Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);

        // EDIT MODE: there is a movie in the Intent.
        if (existing != null) {

            // Reads the position. Here `-1` would mean "a movie sent without a position" —
            // a case that does not happen in the normal flow, but it would turn the save
            // into an insert (a duplicate).
            position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);

            // Fills the form with the values of the received movie.
            // THE OBJECT IS A COPY: the changes in the form do NOT reach the list in
            // MainActivity except through the result Intent.
            fillForm(existing);

            // Changes the screen title. `setTitle` is the Activity method,
            //   NOT the model setter — there is no conflict, the receiver differs.
            // WARNING: the application theme is `Theme.Material3.DayNight.NoActionBar`
            //   (see `themes.xml`), and the layout contains no `Toolbar`.
            //   Without an ActionBar, the title is not visible anywhere on screen — the change
            //   is real, but invisible. The visible feedback for the user
            //   is the button text, set on the next line.
            setTitle("Edit movie");

            // Changes the button text. The same button does insert or update;
            //   the label is the only visible difference for the user.
            btMovieAction.setText("Update Movie");
        }

        // INSERT MODE: `existing == null`. Nothing happens.
        //   `position` stays -1, the form keeps the default values from XML:
        //   empty title, date = today, genre = the first in the list, empty budget, duration 0,
        //   rating 0, switch off, check mark off, "G" checked, empty poster.
    }

    // ==================================================================================
    // fillForm — MODEL -> WIDGETS
    // ==================================================================================
    // 10 fields, in the order of the model. Each line is the inverse of a line in
    // `saveMovie`.
    // ==================================================================================
    private void fillForm(Movie existing) {

        // Text: `getText().toString()` on save, `setText(...)` on fill.
        // `setText` expects a `CharSequence`; `String` is a `CharSequence`.
        etTitle.setText(existing.getTitle());

        // BUG 2: `existing.getRelease()` can be `null`.
        // ==============================================================================
        // `SimpleDateFormat.format(null)` throws `NullPointerException`.
        // WHEN IT HAPPENS: when the edited movie has `release == null`. In the demo flow
        //   all 3 movies have a date, so the bug is not visible. It becomes real if a
        //   `Movie` is built with the empty constructor and saved without a date, or if
        //   the data comes from an external source.
        // FIX: `if (existing.getRelease() != null) { ... } else { etRelease.setText(""); }`
        // ==============================================================================
        etRelease.setText(dateFormat.format(existing.getRelease()));

        // BUG 3: `String.valueOf(double)` produces scientific notation for large values.
        // ==============================================================================
        // `String.valueOf(160000000.0)` -> "1.6E8".
        // The user sees "1.6E8" in the budget field. `Double.parseDouble("1.6E8")`
        //   works, so the value is saved correctly — but the display is ugly
        //   and looks like an error.
        // FIX: `String.format(Locale.getDefault(), "%.0f", existing.getBudget())`
        //   or a `DecimalFormat`.
        // ==============================================================================
        etBudget.setText(String.valueOf(existing.getBudget()));

        // `SeekBar.setProgress(int)` — the value is automatically clamped to 0..max.
        // If the duration in the model were 500, the bar would stop at 300.
        // SIDE EFFECT: if the value CHANGES, `onProgressChanged` fires
        //   and the `tvDurationValue` label updates. If the value is already 0
        //   (the default), the listener does NOT fire — but the label in XML is
        //   already "0 min", so the result is correct.
        sbDuration.setProgress(existing.getDuration());

        // `CheckBox.setChecked(boolean)` — it has no listener, so no chained reaction.
        cbonWatchList.setChecked(existing.isOnWatchlist());

        // `setChecked` on the switch FIRES `OnCheckedChangeListener`.
        // The effect: `tvWatchedValue` receives "Yes" or "No".
        // The order in `onCreate` depends on THIS line: the listener must
        //   already be attached when `fillForm` runs.
        swWatched.setChecked(existing.isWatched());

        // `RatingBar.setRating(float)` — the parameter is `float`, exactly the type in the model.
        // No listener: the stars are drawn directly.
        rbRating.setRating(existing.getRating());

        // `setText(null)` is legal: the field becomes empty. It does not throw.
        etPoster.setText(existing.getPoster());

        // ==============================================================================
        // THE LOOP FOR THE SPINNER — matching on TEXT
        // ==============================================================================
        // `Spinner` has no `setSelectionByValue`. It only has `setSelection(int)`.
        //   So you have to look for the index that corresponds to the value in the model.
        // `getCount()` = the number of elements in `@array/movie_genre`.
        // `getItemAtPosition(index)` returns `Object`; here, a `String`.
        // `equals` (not `==`): it compares content, not references.
        // CONCRETE RISK: "Animation" (Toy Story's genre) does not exist in
        //   `@array/movie_genre`. The loop finds nothing, the spinner stays on
        //   position 0 ("Drama"), and on save the movie changes its genre WITHOUT
        //   telling anyone. It is the most likely place where you will lose points
        //   in a live demonstration, because no error appears.
        // ==============================================================================
        for(int index=0; index<spGenre.getCount(); index++)
        {
            if(spGenre.getItemAtPosition(index).equals(existing.getGenre()))
            {
                // Sets the selection and stops the loop. Without `break`, it would keep going
                //   for nothing — but the result would be identical.
                spGenre.setSelection(index);
                break;
            }
        }

        // ==============================================================================
        // THE LOOP FOR THE RADIOGROUP — matching on the BUTTON TEXT
        // ==============================================================================
        // `getChildCount()` = 5 (the buttons from XML).
        // `getChildAt(index)` returns `View`; cast to `RadioButton` for `getText()`.
        // `check(id)` — RadioGroup wants the ID, not the index. Hence `getChildAt(index).getId()`.
        // WHY it is generic: you add a 6th button in XML and the code sees it
        //   with no modification at all.
        // RISK: the matching is done on text. Renaming "PG-13" -> "PG13" in XML breaks
        //   editing for movies saved with the old label.
        // ==============================================================================
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
            if(rb.getText().toString().equals(existing.getApproval()))
            {
                // `check` automatically unchecks any other button in the group.
                rgApproval.check(rgApproval.getChildAt(index).getId());
                break;
            }
        }
    }

    // ==================================================================================
    // initControls — THE 13 findViewById CALLS
    // ==================================================================================
    // WHY ALL IN ONE METHOD: if an ID is wrong, `findViewById` returns
    //   `null` with no error, and the NPE only appears at the first access — somewhere far away.
    //   Grouped here, you can visually check that every line has an existing ID.
    //
    // THE ORDER: it does not matter to the compiler. It is the order of the fields in the class,
    //   that is, the order in the form, top to bottom.
    // ==================================================================================
    private void initControls() {

        // 1. Title — TextInputEditText etTitle (the "Basics" card).
        etTitle = findViewById(R.id.etTitle);

        // 2. Date — TextInputEditText etRelease (the "Basics" card).
        etRelease = findViewById(R.id.etRelease);

        // 3. Genre — Spinner spGenre (the "Basics" card).
        spGenre = findViewById(R.id.spGenre);

        // 4. Budget — TextInputEditText etBudget (the "Production" card).
        etBudget = findViewById(R.id.etBudget);

        // 5. Duration — SeekBar sbDuration (the "Production" card).
        sbDuration = findViewById(R.id.sbDuration);

        // 6. Rating — RatingBar rbRating (the "Your verdict" card).
        rbRating = findViewById(R.id.rbRating);

        // 7. Guidance — RadioGroup rgApproval (the "Your verdict" card).
        rgApproval = findViewById(R.id.rgApproval);

        // 8. Watchlist — ID `cbOnWatchList` (with "On"), field `cbonWatchList` (without "O").
        cbonWatchList = findViewById(R.id.cbOnWatchList);

        // 9. Switch — MaterialSwitch swWatched.
        swWatched = findViewById(R.id.swWatched);

        // 10. Poster — TextInputEditText etPoster (the "Poster" card).
        etPoster = findViewById(R.id.etPoster);

        // 11. Button — ID `btnMovieAction`, field `btMovieAction`.
        btMovieAction = findViewById(R.id.btnMovieAction);

        // 12. Duration label — TextView tvDurationValue.
        tvDurationValue = findViewById(R.id.tvDurationValue);

        // 13. Switch label — TextView tvWatchedValue.
        tvWatchedValue = findViewById(R.id.tvWatchedValue);
    }

    // ==================================================================================
    // initListeners — FOUR LISTENERS
    // ==================================================================================
    // 1. click on etRelease   -> opens the date dialog
    // 2. click on the button  -> saveMovie()
    // 3. switch changed       -> updates "Yes"/"No"
    // 4. seekbar moved        -> updates "NNN min."
    // ==================================================================================
    private void initListeners() {

        // LISTENER 1: click on the date field.
        // ==============================================================================
        // WHY `setOnClickListener` ON AN `EditText`: an EditText receives focus on
        //   touch, not click. Still, `setOnClickListener` works: on the first
        //   touch it receives focus AND fires the click.
        // RISK: if the user presses a second time (the field already has focus), the click
        //   fires again — the dialog reopens. That is the desired behaviour.
        // BIGGER RISK: the field has `inputType="date"`, so the user CAN type.
        //   The typed text is not read into `releaseCal` until the dialog is opened.
        //   If they type and press Save directly, the old date from `releaseCal` is saved.
        // ==============================================================================
        etRelease.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showReleaseDatePicker();
            }
        });

        // LISTENER 2: click on the save button.
        // There is no validation before `saveMovie()`. See BUG 1.
        btMovieAction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveMovie();
            }
        });

        // LISTENER 3: the "Recommended" switch.
        // ==============================================================================
        // `CompoundButton.OnCheckedChangeListener` has a single method, with two parameters:
        //   `buttonView` — the switch that changed (unused here)
        //   `isChecked`  — the new state
        // `@NonNull` is the annotation from the interface signature; we copy it.
        // The ternary operator picks the text in a single expression.
        // IT ALSO FIRES PROGRAMMATICALLY: `fillForm` -> `swWatched.setChecked(...)`
        //   -> listener -> the label updates. That is why the order in onCreate matters.
        // ==============================================================================
        swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                tvWatchedValue.setText(isChecked ? "Yes" : "No");
            }
        });

        // LISTENER 4: the duration slider.
        // ==============================================================================
        // `SeekBar.OnSeekBarChangeListener` has THREE methods. All must be implemented,
        //   even if two are empty — otherwise the anonymous class does not compile.
        //
        // `onProgressChanged(seekBar, progress, fromUser)`:
        //   `progress`  — the new value (0..300)
        //   `fromUser`  — `true` if the user dragged the slider, `false` if
        //                 the value was set from code (`setProgress` in `fillForm`)
        //
        // WHY `fromUser` IS IGNORED HERE: we want the label to ALWAYS reflect
        //   the real value, regardless of who changed it. If you filtered on
        //   `fromUser`, on edit the label would stay at "0 min" until the first touch.
        // ==============================================================================
        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {

                // Concatenation: `int + String` -> String. Result: "148 min.".
                // The full stop is in the text, not in the value.
                tvDurationValue.setText(progress + " min.");
            }

            // Method 2: from touch to movement. We do not need it.
            // Empty body = intentional, not forgotten. The interface requires it.
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            // Method 3: when the finger is lifted. We do not need it.
            // This is where you could "commit" the value or trigger haptics.
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });
    }

    // ==================================================================================
    // saveMovie — WIDGETS -> MODEL -> INTENT
    // ==================================================================================
    // Five steps, in order:
    //   1. create the empty object
    //   2. read 9 fields directly from the widgets
    //   3. read the 10th field (approval) through a loop
    //   4. put the object in the Intent, plus the position if it exists
    //   5. setResult + finish
    // ==================================================================================
    private void saveMovie() {

        // STEP 1: an empty object. It works only because `Movie` has an explicitly written
        // no-argument constructor (see 22.1).
        Movie movie = new Movie();

        // STEP 2: the 9 simple fields.
        // Each line is the inverse of a line in `fillForm`.
        // `getText()` returns `Editable`; `toString()` turns it into a `String`.
        movie.setTitle(etTitle.getText().toString());

        // `releaseCal.getTime()` — NOT `etRelease.getText()`.
        // ==============================================================================
        // WHY: the calendar is the source of truth. The text can be empty, can be typed
        //   wrongly, can be in another format. The calendar was updated only by
        //   the dialog, with guaranteed valid values.
        // `getTime()` builds a NEW `Date` on every call, but with the same
        //   milliseconds.
        // ==============================================================================
        movie.setRelease(releaseCal.getTime());

        // `getSelectedItem()` returns `Object`; `toString()` turns it into a `String`.
        // RISK: if the spinner were empty, it would be `null` -> NPE. Here `entries` in XML
        //   guarantees at least one element.
        movie.setGenre(spGenre.getSelectedItem().toString());

        // BUG 1: `Double.parseDouble("")` throws `NumberFormatException`.
        // ==============================================================================
        // WHEN IT HAPPENS: on insert, the budget field is empty. The user presses
        //   "Save Movie" without filling in the budget -> the application closes.
        // WHY IT IS NOT VISIBLE IN THE DEMO: the 3 movies have a budget filled in, and on edit
        //   the field is filled by `fillForm`.
        // FIX: `String budgetText = etBudget.getText().toString();
        //              double budget = budgetText.isEmpty() ? 0 : Double.parseDouble(budgetText);`
        // ADDITIONAL RISK: on keyboards that produce a decimal comma ("1,5"),
        //   `parseDouble` throws the same exception — `Double.parseDouble` accepts only
        //   the full stop, regardless of `Locale`.
        // ==============================================================================
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));

        // `getProgress()` returns `int`, exactly the type of the field.
        movie.setDuration(sbDuration.getProgress());

        // `getRating()` returns `float`, exactly the type of the field.
        movie.setRating(rbRating.getRating());

        // `isChecked()` returns `boolean`.
        movie.setWatched(swWatched.isChecked());

        // The second check mark, independent of the first.
        movie.setOnWatchlist(cbonWatchList.isChecked());

        // The poster can be empty — `""`, not `null`. The model accepts both.
        movie.setPoster(etPoster.getText().toString());

        // STEP 3: the 10th field — the guidance.
        // ==============================================================================
        // RadioGroup has no "getSelectedItem". It has "getCheckedRadioButtonId()", but
        //   the source prefers the loop, so that it can take the TEXT, not the ID.
        // `getChildCount()` = 5. `getChildAt` -> `View` -> cast to `RadioButton`.
        // `isChecked()` — exactly one button is checked (RadioGroup guarantees that).
        // `break` after the first one found: the rest are unchecked anyway.
        // If no button were checked, `approval` would stay `null` — but the XML
        //   has `android:checked="true"` on the first one, so it does not happen.
        // ==============================================================================
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
            if(rb.isChecked())
            {
                movie.setApproval(rb.getText().toString());
                break;
            }
        }

        // STEP 4: build the RESULT Intent.
        // ==============================================================================
        // `new Intent()` WITH NO parameters: it is not a navigation Intent, but a
        //   data container. It has no target component; it is read by the launcher
        //   in MainActivity.
        // ==============================================================================
        Intent intent = new Intent();

        // `putExtra(String, Serializable)` — `Movie` implements the interface, so
        //   the overload is found. The object is serialised here.
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);

        // The position is sent ONLY in edit mode.
        // ==============================================================================
        // On insert, the key is missing. MainActivity reads with `getIntExtra(..., -1)`
        //   and receives exactly the sentinel. The absence of the key IS the "insert" information.
        // If you always sent the position (with -1), it would work identically — but the protocol
        //   would be less clear.
        // ==============================================================================
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);

        // STEP 5a: hand over the result.
        // `RESULT_OK` is the constant `Activity.RESULT_OK` (-1). Without this call,
        //   the activity would close with `RESULT_CANCELED` and MainActivity would ignore it.
        setResult(RESULT_OK, intent);

        // STEP 5b: close the activity.
        // WHY AFTER `setResult`: `finish()` schedules the closing and the handing over
        //   of the result. The other way round, the result could leave before it is set.
        // `finish()` does NOT destroy the activity immediately: it goes through onPause -> onStop
        //   -> onDestroy, and MainActivity comes back to the foreground.
        finish();
    }

    // ==================================================================================
    // showReleaseDatePicker — THE DATE DIALOG
    // ==================================================================================
    // The flow:
    //   1. read the current text from the field
    //   2. if it is not empty, parse it and update `releaseCal`
    //   3. open the dialog positioned on the values in `releaseCal`
    //   4. on confirmation, write into `releaseCal` and into the text
    // ==================================================================================
    private void showReleaseDatePicker() {

        // The current text, as a String. It can be "" (empty field) or "16/07/2010".
        String current = etRelease.getText().toString();

        // Only if there is text do we attempt parsing. An empty string would throw
        // `ParseException` and would be caught below — but the check is cheaper.
        if (!current.isEmpty()) {
            try {

                // `parse` returns a `Date` or throws `ParseException`.
                // It can also return `null` if the text is empty — hence the check.
                Date parsed = dateFormat.parse(current);

                // `setTime(Date)` copies the milliseconds into the Calendar.
                if (parsed != null)
                    releaseCal.setTime(parsed);

            // An EMPTY `catch`, named `ignored`.
            // ==========================================================================
            // WHY IT IS ACCEPTABLE: if the text is not a valid date, the desired
            //   behaviour is "start from the previous date". There is nothing to report
            //   and nothing to fix — the dialog opens anyway.
            // WHEN it would NOT be acceptable: if the error had to be shown to the user
            //   or if it hid a logic problem.
            // ==========================================================================
            } catch (ParseException ignored) { }
        }

        // Builds the dialog. Parameters:
        //   1. `this` — the Context
        //   2. the confirmation listener (anonymous class)
        //   3. the initial year
        //   4. the initial month — 0-INDEXED, exactly what `Calendar` expects
        //   5. the initial day — 1-indexed
        // `.show()` — without it, the dialog is built but does not appear.
        new DatePickerDialog(
                this,
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {

                        // Writes into the Calendar. WARNING: `set(year, month, day)` does NOT reset
                        // the time. The time stays the one from `Calendar.getInstance()` — that is,
                        // the moment the form was created.
                        // Consequence: two movies saved on the same day have Dates that
                        // differ at the millisecond level. For display (dd/MM/yyyy)
                        // it does not matter.
                        releaseCal.set(year, month, day);

                        // Clears any error message left on the field.
                        // `setError` is not called anywhere in this file, so
                        // the line is defensive — useful if validation is added later.
                        etRelease.setError(null);

                        // Writes the formatted text into the field. Here the link is visible:
                        // Calendar -> String -> EditText. On save, the path is the reverse:
                        // EditText -> (ignored) ; Calendar -> Date -> model.
                        etRelease.setText(dateFormat.format(releaseCal.getTime()));
                    }
                },
                // The initial values of the dialog, read from the Calendar.
                // `Calendar.MONTH` is already 0-indexed, so it is passed directly.
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)
        ).show();
    }
}
```

### The three real bugs in `ItemActivity`

| # | The line in the source | Trigger | Effect |
|---|---|---|---|
| **BUG 1** | `Double.parseDouble(etBudget.getText().toString())` | the budget field is empty | `NumberFormatException` -> crash |
| **BUG 2** | `dateFormat.format(existing.getRelease())` | the edited movie has `release == null` | `NullPointerException` -> crash |
| **BUG 3** | `String.valueOf(existing.getBudget())` | budget ≥ 10,000,000 | shows `1.6E8` instead of `160000000` |

**Which one shows up in the demo:** BUG 1 appears immediately if you press "Save Movie" without filling in the budget — it is the first thing you will hit if you run the application. BUG 2 and BUG 3 are not visible, because all 3 demo movies have a date and a budget filled in.

**Other risks (not bugs, but they can become ones):**

- Typing the date by hand in `etRelease` does not update `releaseCal` — the old date is saved.
- Toy Story's genre "Animation" does not exist in `@array/movie_genre`: on edit, the spinner stays on "Drama" and saving changes the genre with no error at all.
- `position` stays `-1` if `MOVIE_EXTRA` exists but `POSITION_EXTRA` is missing — the save becomes an insert, that is, a duplicate.

---

## 22.4 `activity_main.xml` — the list screen

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FILE: activity_main.xml — THE SCREEN WITH THE LIST
  ======================================================================================
  WHAT IT IS: a FrameLayout with exactly two children: the ListView (fills everything) and the FAB (on top of it).
  WHY SO LITTLE: all the complexity is in `movie_item.xml` (the future row)
    and in `activity_item.xml` (the form). Here only the skeleton.
  STRUCTURE:

    FrameLayout (id=main)
    |== ListView (id=listView)            <- first child = drawn first = underneath
    +== FloatingActionButton (id=...)     <- second child = drawn on top of the list

  THE ORDER OF THE CHILDREN IS MEANING, NOT STYLE: in a FrameLayout, each child is
    drawn on top of the previous one. Reversed, the list would cover the button.
  ======================================================================================
-->

<!--
  FRAMELAYOUT — the root container.
  WHY FrameLayout and not LinearLayout: the children must OVERLAP. A LinearLayout
    would put them next to each other (or one below the other), and the FAB would no longer float over the list.
  WHY not ConstraintLayout: for two children, a FrameLayout is simpler and cheaper.

  ATTRIBUTES, LINE BY LINE:
    xmlns:android   -> the framework attributes (layout_width, text, id...)
    xmlns:app       -> the library attributes (Material, AndroidX)
    xmlns:tools     -> attributes that exist ONLY in the Android Studio preview
                       and are REMOVED at build time. They never reach the APK.
    android:id      -> @+id/main; `@+id/` CREATES the ID, `@id/` REFERS to an existing one
    layout_width    -> match_parent: takes the full width of the parent
    layout_height   -> match_parent: takes the full height
    orientation     -> an INVALID attribute on FrameLayout; it exists only on LinearLayout.
                       It is IGNORED by Android and produces a lint warning
                       ("Unknown attribute"). Leftover from an earlier LinearLayout.
    tools:context   -> preview only; it tells Android Studio which activity
                       to use for the theme. Removed at build time.

  WHY `android:id="@+id/main"` IS MANDATORY: the code calls `findViewById(R.id.main)`
    for the insets listener. Without this ID, the call would return `null` and
    `setOnApplyWindowInsetsListener(null, ...)` would throw an NPE.
-->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!--
      LISTVIEW — the scrollable list.
      WHY ListView and not RecyclerView: at this commit the classic ListView is being taught.
        RecyclerView appears in the next lab, together with `movie_item.xml`.

      ATTRIBUTES:
        android:id              -> listView; used by `findViewById` in initControls
        layout_width/height     -> match_parent on both axes: the list occupies the whole screen,
                                   including the area under the FAB. The FAB is drawn ON TOP of the
                                   list, not the list around it.
        android:entries         -> fills the list from XML with the elements of `@array/items`
                                   (20 items, "Item 1".."Item 20").
                                   AT RUNTIME, `listView.setAdapter(movieAdapter)`
                                   COMPLETELY REPLACES this adapter. `entries` remains
                                   only so that the preview shows a full list.
                                   The runtime cost is zero after `setAdapter`.
    -->
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />

    <!--
      FLOATING ACTION BUTTON — the "+" button.
      The full name is required because it is a class from the Material library,
        not one from the framework. The `com.google.android.material...` prefix is the class path.

      ATTRIBUTES:
        android:id          -> floatingActionButton; looked up in initControls
        layout_width/height -> wrap_content: the FAB has a fixed size imposed by the style
                               (56dp by default). `match_parent` would stretch it over the whole screen.
        android:layout_gravity -> the position of THIS CHILD in ITS PARENT (the FrameLayout).
        android:layout_margin  -> 16dp on all sides. Together with the insets padding
                                  applied to `R.id.main`, the button sits 16dp from the safe
                                  area, not from the physical edge.
        android:contentDescription -> the text read by TalkBack. MANDATORY for
                                  elements with no visible text; without it, lint reports
                                  an error ("ContentDescription"), and screen-reader
                                  users hear only "button".
        app:srcCompat       -> the compatible variant for vector images.
                               `android:src` would work on API 21+, but `srcCompat`
                               is the AndroidX recommendation and the only one that supports
                               vectors on all versions.

      ==================================================================================
      layout_gravity  vs  gravity
      ==================================================================================
        gravity         = how the ELEMENT arranges its own children inside itself
        layout_gravity  = how the ELEMENT is arranged in its parent

        Example: a TextView with `gravity="center"` centres its TEXT.
                 A TextView with `layout_gravity="center"` is centred IN THE PARENT.

      `bottom|end` = bottom, right. `end` respects the reading direction: in RTL it becomes
        left. `right` would have been fixed and would be wrong in RTL.
      WHY it works here: FrameLayout honours `layout_gravity` on its children.
      ==================================================================================
    -->
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
| `app:srcCompat` | `@drawable/...` | a compatible vector image |
| `tools:context` | `.activities.MainActivity` | preview only |

---

## 22.5 `activity_item.xml` — the form

### 22.5.0 Three rules that apply throughout the file

**1. `?attr/` vs `@color/` vs `#RRGGBB`**

| Form | When it is resolved | Does it change with the theme? | When it is used |
|---|---|---|---|
| `?attr/colorPrimary` | at runtime, from the current theme | **yes** | any semantic colour |
| `@color/my_color` | at build time, from `colors.xml` | no | fixed brand colours |
| `#FFC107` | at build time, as a literal | no | accepted exceptions (stars) |
| `@android:color/transparent` | a framework constant | no | "no background" |

The essential difference: `?attr/` is a **role**, `@color/` is a **value**. `?attr/colorPrimary` means "the theme's primary colour" and becomes another shade in dark mode. `@color/purple_500` stays purple in both themes.

**2. `0dp` + `layout_weight`**

```
Horizontal LinearLayout, total width 360dp
+--------------------------------------------------------------+
| TextView A        | TextView B                               |
| width=0dp         | width=wrap_content                       |
| weight=1          | (no weight)                              |
+-------------------+------------------------------------------+
|<---- the rest ---->|<----- as much as the text needs ------>|

The rule: `0dp` + `weight` = "I don't care about my width, give me what is left".
Without `0dp` (with `wrap_content`), the weight distributes the space AFTER each
child has taken its natural size — the result is hard to predict.
```

**3. `style=` vs explicit attributes**

`style="@style/Widget.Material3.TextInputLayout.OutlinedBox"` applies a **package** of attributes (outline, padding, colours, corners). An attribute written explicitly next to `style` **overrides** the one from the style. That is why `app:cardCornerRadius="20dp"` works on top of the card style.

### 22.5.1 The root and the header

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FILE: activity_item.xml — THE INSERT / EDIT FORM
  ======================================================================================
  STRUCTURE (4 cards + header + button):

    ScrollView (id=main)
    +== LinearLayout vertical
        |== TextView  "Movie details"               <- title
        |== TextView  "Fill in the information..."  <- subtitle
        |== MaterialCardView  [Basics]              <- title, genre, date
        |== MaterialCardView  [Production]          <- budget, duration
        |== MaterialCardView  [Your verdict]        <- rating, switch, check mark, guidance
        |== MaterialCardView  [Poster]              <- URL
        +== MaterialButton    "Save Movie"          <- the action

  WHY CARDS: they split a long form into visual sections. Each card has the
    same recipe: surface background, 20dp corners, 16dp inner padding.
  ======================================================================================
-->

<!--
  SCROLLVIEW — the container that allows scrolling.
  THE ABSOLUTE RULE: a ScrollView is allowed EXACTLY ONE direct child. Two children ->
    `IllegalStateException: ScrollView can host only one direct child`.
  That is why all the content sits in a single vertical LinearLayout.

  ATTRIBUTES:
    android:id          -> `main`, THE SAME name as in activity_main. It is not global:
                           the insets listener in ItemActivity looks for `R.id.main`,
                           and the ID must exist in EVERY layout that uses it.
    layout_width/height -> match_parent on both axes
    android:background  -> ?attr/colorSurface, the "surface" colour of the Material 3 theme.
                           In light mode it is almost white; in dark mode it is a very
                           dark grey. WHY NOT #FFFFFF: it would break dark mode —
                           light text would be invisible on a white background.
    android:fillViewport -> true: stretches the child to fill the viewport height
                           if the content is shorter than the screen. Without it,
                           the content would stick to the top and leave empty space below.
    tools:context       -> preview only
-->
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <!--
      VERTICAL LINEARLAYOUT — the only child of the ScrollView.
      WHY vertical: the form flows from top to bottom.
      PADDING:
        paddingHorizontal="16dp" — 16dp left + right (shorthand for
          paddingLeft + paddingRight, available since API 26)
        paddingTop="24dp" / paddingBottom="24dp" — breathing room from the screen edges
      WHY 16dp: the base unit of Material Design for side margins.
      WHY wrap_content on the height: the content takes its natural height, and the
        ScrollView takes care of the scrolling.
    -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- Header -->

        <!--
          THE SCREEN TITLE — "Movie details".
          textAppearance="?attr/textAppearanceHeadlineMedium" — the complete typographic
            style (size, weight, spacing) from the Material 3 theme, not just
            a size. `?attr/` because the style depends on the theme.
          textColor="?attr/colorOnSurface" — the text colour suited to the
            surface it sits on. In dark mode it becomes white.
          textStyle="bold" — overrides the weight from textAppearance.
          WHY wrap_content on both axes: the text takes exactly the space it needs.
        -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Movie details"
            android:textAppearance="?attr/textAppearanceHeadlineMedium"
            android:textColor="?attr/colorOnSurface"
            android:textStyle="bold" />

        <!--
          THE SUBTITLE — "Fill in the information below and save."
          textAppearanceBodyMedium — smaller than the title.
          colorOnSurfaceVariant — a more muted shade than colorOnSurface,
            exactly the role for secondary text.
          marginTop 4dp + marginBottom 20dp — closeness to the title and distance
            from the first card.
        -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="20dp"
            android:text="Fill in the information below and save."
            android:textAppearance="?attr/textAppearanceBodyMedium"
            android:textColor="?attr/colorOnSurfaceVariant" />

        <!-- ============ CARD 1: Basics ============ -->

        <!--
          MATERIALCARDVIEW — the container of the "Basics" section.
          style="?attr/materialCardViewFilledStyle" — the "filled" card style from
            the Material 3 theme: coloured background, no outline, minimal shadow.
          app:cardCornerRadius="20dp" — rounded corners, on top of the value from the style.
          android:layout_marginBottom="16dp" — the distance to the next card.
          WHY `?attr/` for the style: in Material 3, the card style depends on the theme
            (filled vs elevated vs outlined). Referring through the attribute allows
            a global change of the look.

          WHY A SINGLE CHILD: MaterialCardView is designed for a single
            direct child (it is a specialised FrameLayout, not a list container).
            All the elements of the section are grouped in a vertical LinearLayout.
        -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <!--
              The INNER vertical LinearLayout — the content of the card.
              padding="16dp" on all sides: the content does not touch the card edge.
            -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!--
                  THE SECTION TITLE — "Basics".
                  textAppearanceTitleMedium — smaller than the screen title,
                    larger than the labels.
                  textColor="?attr/colorPrimary" — the theme's accent colour.
                    This is the only place in the card where the primary colour appears,
                    to mark the hierarchy.
                  marginBottom 12dp — separates the title from the first field.
                -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Basics"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Title -->

                <!--
                  THE FIELD LABEL — "Title".
                  WARNING: the ID is `tvTile`, not `tvTitle`. A typo in the source.
                    It is not used in the code, so it produces no error — but if you look it up
                    as `tvTitle`, you will not find it.
                  textAppearanceLabelLarge + colorOnSurfaceVariant — the standard style
                    for the label above a field.
                  marginBottom 4dp — closeness to the field it describes.
                -->
                <TextView
                    android:id="@+id/tvTile"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Title"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  TEXTINPUTLAYOUT — the wrapper of the text field.
                  WHY it exists: a plain `EditText` has no outline, no floating label,
                    no icons and no error message. `TextInputLayout` adds all of them.
                  style OutlinedBox — a visible outline, small corners. The alternative
                    "FilledBox" has a filled background.
                  app:hintEnabled="false" — DISABLES the floating label.
                    WHY: the label is already a separate `TextView` above (tvTile).
                    With the hint active, you would have TWO labels for the same field.
                  app:endIconMode="clear_text" — adds an "X" on the right that clears
                    the text. WARNING: it only clears the text in the `EditText`, NOT the value
                    in the model.
                  marginBottom 16dp — the distance to the next field.
                -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text">

                    <!--
                      THE TEXT FIELD — `etTitle`.
                      The real type is `TextInputEditText`, a subclass of `EditText`
                        that collaborates with `TextInputLayout` (it knows how to display the hint
                        inside the outline).
                      android:hint="Movie title" — the text shown when the field is empty.
                        It stays visible because `hintEnabled=false` only disables
                        the FLOATING label, not the content hint.
                      android:inputType="textCapWords" — the keyboard automatically capitalises
                        the first letter of each word. Suitable for titles.
                    -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Movie title"
                        android:inputType="textCapWords" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- Genre -->

                <!--
                  The "Genre" LABEL — `tvGenre`.
                  The same style as the title label: LabelLarge + colorOnSurfaceVariant.
                  It is not used in the code; it exists only for the human reader.
                -->
                <TextView
                    android:id="@+id/tvGenre"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Genre"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  THE SPINNER TRICK: an outlined card around it.
                  WHY: the native `Spinner` has no outline. The other fields are
                    `TextInputLayout.OutlinedBox` (1dp outline, 4dp corners). To make it
                    look the same, the spinner is wrapped in a card with:
                      - the outlined style (outline)
                      - a FIXED height of 56dp (the same as an OutlinedBox field)
                      - 4dp corners
                      - a TRANSPARENT background, so that only the outline is visible
                      - the strokeColor from the theme
                  app:cardBackgroundColor="@android:color/transparent" — `@android:color`
                    is a framework constant, not a project resource.
                  app:strokeColor="?attr/colorOutline" — the theme's outline colour.
                  WHY 56dp: the standard height of a Material text field.
                    If you used wrap_content, the spinner would be shorter and would
                    break the vertical alignment of the form.
                -->
                <com.google.android.material.card.MaterialCardView
                    style="?attr/materialCardViewOutlinedStyle"
                    android:layout_width="match_parent"
                    android:layout_height="56dp"
                    android:layout_marginBottom="16dp"
                    app:cardBackgroundColor="@android:color/transparent"
                    app:cardCornerRadius="4dp"
                    app:strokeColor="?attr/colorOutline">

                    <!--
                      THE SPINNER — `spGenre`.
                      android:entries="@array/movie_genre" — the values come from XML.
                        WHY `entries` STAYS HERE: ItemActivity never calls
                        `spGenre.setAdapter(...)`. The list is completely static.
                      android:paddingStart="4dp" — aligns the text with the one in the
                        TextInputLayout fields (which have inner padding).
                      android:spinnerMode="dropdown" — the list opens as a popup,
                        not as a modal dialog. `dialog` would be the window variant.
                      layout_height="match_parent" — fills the card's 56dp.
                    -->
                    <Spinner
                        android:id="@+id/spGenre"
                        android:layout_width="match_parent"
                        android:layout_height="match_parent"
                        android:entries="@array/movie_genre"
                        android:paddingStart="4dp"
                        android:spinnerMode="dropdown" />
                </com.google.android.material.card.MaterialCardView>

                <!-- Release date -->

                <!--
                  THE DATE FIELD — `etRelease`.
                  WHY `hintEnabled="true"` HERE and `false` for the title: here there is NO
                    separate TextView above. The label is the TextInputLayout's floating
                    hint, which rises when the field has text.
                  app:startIconDrawable="@android:drawable/ic_menu_my_calendar" —
                    the calendar icon on the left, which visually suggests that this is
                    a date field. `@android:drawable` = a framework resource.
                  app:startIconContentDescription="Release date" — the TalkBack text
                    for the icon. Without it, lint flags the missing description.
                  android:inputType="date" — the numeric keyboard with date characters.
                    WARNING: it does not prevent typing an invalid text; it only changes
                    the keyboard shown.
                  There is NO `android:layout_marginBottom` here: the card ends
                    right after this field, and the card's inner padding
                    provides the space.
                -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="true"
                    app:startIconContentDescription="Release date"
                    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

                    <!--
                      THE FIELD ITSELF — `etRelease`.
                      The text is "dd/MM/yyyy" and it is WRITTEN by `showReleaseDatePicker`.
                      The user can type, but the typed text does not reach
                      `releaseCal` until the dialog is reopened (see RISK in 22.3).
                    -->
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

        <!--
          The "Production" CARD — budget and duration.
          The same recipe as the first card: filled style, 20dp corners, marginBottom 16dp.
          The difference is the content, not the style. The uniformity is intentional:
            the user recognises the pattern after the first card.
        -->
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

                <!--
                  THE SECTION TITLE — "Production". The same attributes as "Basics".
                -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Production"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Budget -->

                <!--
                  The "Budget" LABEL — `tvBudget`. It is not used in the code.
                -->
                <TextView
                    android:id="@+id/tvBudget"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Budget"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  THE BUDGET FIELD — `etBudget`.
                  app:prefixText="$ " — FIXED text shown on the left of the value, inside the
                    outline. It is NOT part of the field's text: `getText()` returns
                    only the digits. That is why `Double.parseDouble` works.
                  app:hintEnabled="false" — the label is `tvBudget` above.
                  android:inputType="numberDecimal" — a numeric keyboard with a decimal point.
                    It does not guarantee that the text is a valid number: the user can
                    leave the field empty (see BUG 1).
                  marginBottom 16dp — the distance to the duration row.
                -->
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

                <!--
                  THE DURATION ROW — label on the left, value on the right.
                  android:gravity="center_vertical" — centres the children VERTICALLY
                    inside the row. WHY: the label and the value have different
                    heights; without centring they would sit aligned to the top.
                  WARNING: `gravity` here is on the LinearLayout, so it applies to
                    ITS CHILDREN. Do not confuse it with `layout_gravity`.
                  android:orientation="horizontal" — the children sit next to each other.
                -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">

                    <!--
                      The "Duration" LABEL — `tvDuration`.
                      android:layout_width="0dp" + android:layout_weight="1" —
                        it takes all the space left after the value on the right takes
                        its natural width. The effect: the value is pushed to the right.
                      Without `0dp`, the two texts would sit glued to the left.
                    -->
                    <TextView
                        android:id="@+id/tvDuration"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Duration"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!--
                      THE DURATION VALUE — `tvDurationValue`, updated by the
                        SeekBar listener.
                      android:text="0 min" — the initial value, matching progress 0.
                      textColor="?attr/colorPrimary" — the accent colour, so that it stands
                        out against the label.
                      tools:text="148 min" — ONLY in the preview: it shows how the text will look
                        when it has a real value. It never reaches the APK.
                    -->
                    <TextView
                        android:id="@+id/tvDurationValue"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorPrimary"
                        tools:text="148 min" />
                </LinearLayout>

                <!--
                  THE SEEKBAR — `sbDuration`.
                  android:max="300" — the maximum value. The default would be 100.
                  android:min="0" — available since API 26. `minSdk 33`, so it works.
                    Without it, the minimum would still be 0, but explicit is clearer.
                  android:progressTint="?attr/colorPrimary" — the colour of the travelled part.
                  android:thumbTint="?attr/colorPrimary" — the colour of the handle.
                  tools:progress="148" — preview only.
                  marginTop 8dp — separates the bar from the label row.
                  WARNING: `getProgress()` returns `int`, exactly the type in the model.
                -->
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

                <!--
                  THE MIN/MAX ROW — "0 min" on the left, "300 min" on the right.
                  paddingHorizontal="16dp" — aligns the labels with the start and
                    the end of the bar, not with the card edges.
                  The two values are HARDCODED. RISK: if you change the SeekBar's
                    `android:max`, you must also change the "300 min" text.
                  `0dp` + `weight=1` on the first text pushes the second one to the right.
                -->
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

        <!-- ============ CARD 3: Your verdict ============ -->

        <!--
          The "Your verdict" CARD — rating, switch, check mark, guidance.
          It is the densest card: three different controls and two separators.
        -->
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

                <!-- Rating -->

                <!--
                  The "Rating" LABEL — `tvRating`. It is not used in the code.
                  WARNING: it has no `marginBottom`, unlike the other labels.
                    The stars have their own `marginTop="4dp"`, so the space is provided
                    from the other side.
                -->
                <TextView
                    android:id="@+id/tvRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Rating"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  RATINGBAR — `rbRating`.
                  android:numStars="5" — 5 stars.
                  android:stepSize="0.5" — half stars. `getRating()` returns
                    `float` (e.g. 3.5), exactly the type in the model.
                  android:layout_gravity="center_horizontal" — centres the BAR in
                    the vertical parent. `gravity` would have centred the bar's children, not the bar.
                  Colours:
                    progressTint="#FFC107" — star yellow, HARDCODED. An accepted
                      exception: the meaning of "yellow star" does not depend on the theme.
                    secondaryProgressTint="#FFC107" — the same colour for the secondary
                      part (the half star).
                    progressBackgroundTint="?attr/colorOutlineVariant" — the empty stars,
                      from the theme.
                  tools:rating="3.5" — preview only.
                  WHY it has no listener: the rating is read directly on save with
                    `getRating()`. There is no label to update.
                -->
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

                <!--
                  SEPARATOR — a 1dp line.
                  WHY an empty `View`: there is no "divider" widget in XML.
                    A View with a 1dp height and a coloured background is the standard solution.
                  marginVertical="12dp" — equal space above and below.
                  background="?attr/colorOutlineVariant" — the outline colour,
                    discreet enough for a line.
                -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Recommended -->

                <!--
                  THE ROW WITH THE SWITCH AND THE CHECK MARK.
                  gravity="center_vertical" — aligns the three columns vertically.
                  minHeight="48dp" — the minimum touch target recommended by Material.
                    Without it, the row would be shorter than a finger.
                -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:minHeight="48dp"
                    android:orientation="horizontal">

                    <!--
                      THE TEXT COLUMN — 0dp + weight 1, so it takes all the space left
                      after the switch and the check mark.
                      vertical — the two texts sit one below the other.
                    -->
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">

                        <!--
                          The "Recommended" LABEL — `tvWatched`. It is not used in the code.
                          textAppearanceBodyLarge — larger than an ordinary label,
                            because it is the main text of the row.
                        -->
                        <TextView
                            android:id="@+id/tvWatched"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Recommended"
                            android:textAppearance="?attr/textAppearanceBodyLarge"
                            android:textColor="?attr/colorOnSurface" />

                        <!--
                          The "No" VALUE — `tvWatchedValue`, updated by the
                            switch listener: `isChecked ? "Yes" : "No"`.
                          The initial value "No" matches the switch being off.
                          textColor colorPrimary — highlights the value.
                        -->
                        <TextView
                            android:id="@+id/tvWatchedValue"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="No"
                            android:textAppearance="?attr/textAppearanceLabelLarge"
                            android:textColor="?attr/colorPrimary" />
                    </LinearLayout>

                    <!--
                      MATERIALSWITCH — `swWatched`.
                      WHY `MaterialSwitch` and not `Switch`: the Material variant has
                        animations and colours from the theme, plus the thumb with an icon.
                      marginEnd="12dp" — separates the switch from the check mark. `end` respects RTL.
                      It has NO text: the label is in the column on the left.
                      The listener is attached in the code, not in XML.
                    -->
                    <com.google.android.material.materialswitch.MaterialSwitch
                        android:id="@+id/swWatched"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="12dp" />

                    <!--
                      MATERIALCHECKBOX — `cbOnWatchList`.
                      The ID has "On" with a capital letter; the field in the code is `cbonWatchList`.
                      android:text="Watchlist" — the label is INSIDE THE
                        control, so it is tapped together with the check mark.
                      It is independent of the switch: you can check both.
                    -->
                    <com.google.android.material.checkbox.MaterialCheckBox
                        android:id="@+id/cbOnWatchList"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Watchlist" />
                </LinearLayout>

                <!--
                  The second separator, identical to the first.
                -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Guidance -->

                <!--
                  The "Guidance" LABEL — `tvGuidance`. It is not used in the code.
                -->
                <TextView
                    android:id="@+id/tvGuidance"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Guidance"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  HORIZONTALSCROLLVIEW — allows the group to scroll horizontally.
                  WHY: 5 radio buttons ("G", "PG", "PG-13", "R", "NC-17") do not fit
                    on a 360dp screen. Without scrolling, the last ones would be cut off.
                  android:scrollbars="none" — hides the scrollbar; on a row
                    of buttons it would look like a defect.
                  WARNING: HorizontalScrollView also accepts a single direct child.
                -->
                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none">

                    <!--
                      RADIOGROUP — `rgApproval`.
                      android:orientation="horizontal" — the buttons sit on one row.
                        The default would be vertical.
                      WHY RadioGroup and not 5 separate buttons: the group guarantees
                        that EXACTLY ONE is checked. `check(id)` automatically unchecks
                        the others.
                      The 5 buttons are direct children; the code walks them with
                        `getChildCount()` / `getChildAt()`.
                    -->
                    <RadioGroup
                        android:id="@+id/rgApproval"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <!--
                          BUTTON 1 — "G".
                          android:checked="true" — IT IS CHECKED BY DEFAULT.
                          WHY: the group must ALWAYS have a value. Without it,
                            `saveMovie` could leave `approval` null if the user
                            does not touch any button.
                          `MaterialRadioButton` — the Material variant, with animation
                            and colours from the theme.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbGeneral"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:checked="true"
                            android:text="G" />

                        <!--
                          BUTTON 2 — "PG". `rbParentGuidance`.
                          The text is the value that reaches the model.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbParentGuidance"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG" />

                        <!--
                          BUTTON 3 — "PG-13". `rbPG13`.
                          WARNING: the hyphen is part of the text and of the saved value.
                            Renaming it to "PG13" would break the matching in `fillForm`.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbPG13"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG-13" />

                        <!--
                          BUTTON 4 — "R". `rbRestricted`.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbRestricted"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="R" />

                        <!--
                          BUTTON 5 — "NC-17". `rbNC17`.
                          The last button; if you added a 6th, the code would read it
                            with no modification at all — the loop is generic.
                        -->
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

        <!--
          The "Poster" CARD — a single field.
          marginBottom="24dp" — larger than on the other cards, because
            the save button follows and there must be breathing room.
        -->
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

                <!--
                  THE URL FIELD — `etPoster`.
                  app:endIconMode="clear_text" — the clearing "X".
                  app:startIconDrawable="@android:drawable/ic_menu_gallery" — the gallery
                    icon, a visual hint for "image".
                  app:startIconContentDescription="Poster link" — the description for TalkBack.
                  app:hintEnabled="false" — there is no separate label above,
                    but the content hint stays visible.
                  android:inputType="textUri" — a keyboard optimised for URLs
                    (it has "/", ".", ":"). It does not validate the URL.
                -->
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

        <!--
          THE SAVE BUTTON — `btnMovieAction`.
          style="@style/Widget.Material3.Button" — the FILLED variant (solid background,
            white text). It is the default style, but written explicitly to be clear.
          android:layout_height="60dp" — taller than the standard (48dp), because
            it is the screen's primary action.
          app:cornerRadius="30dp" — EXACTLY half the height, so the button becomes
            a pill. The rule: cornerRadius = height / 2.
          app:icon="@android:drawable/ic_menu_save" — the save icon from the framework.
          app:iconGravity="textStart" — the icon sits before the text.
          android:text="Save Movie" — in edit mode, the code changes it to "Update Movie".
          android:textAppearance="?attr/textAppearanceLabelLarge" — the label style
            for Material buttons.
          WHY it has NO `layout_marginTop`: the card above has marginBottom 24dp.
        -->
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

### 22.5.2 Map of the widgets in the form

| # | ID in XML | Type | Field in `ItemActivity` | Read method |
|---|---|---|---|---|
| 1 | `etTitle` | `TextInputEditText` | `etTitle` | `getText().toString()` |
| 2 | `etRelease` | `TextInputEditText` | `etRelease` | (not read — `releaseCal`) |
| 3 | `spGenre` | `Spinner` | `spGenre` | `getSelectedItem().toString()` |
| 4 | `etBudget` | `TextInputEditText` | `etBudget` | `Double.parseDouble(...)` |
| 5 | `sbDuration` | `SeekBar` | `sbDuration` | `getProgress()` |
| 6 | `rbRating` | `RatingBar` | `rbRating` | `getRating()` |
| 7 | `rgApproval` | `RadioGroup` | `rgApproval` | loop + `isChecked()` |
| 8 | `cbOnWatchList` | `MaterialCheckBox` | `cbonWatchList` | `isChecked()` |
| 9 | `swWatched` | `MaterialSwitch` | `swWatched` | `isChecked()` |
| 10 | `etPoster` | `TextInputEditText` | `etPoster` | `getText().toString()` |
| 11 | `btnMovieAction` | `MaterialButton` | `btMovieAction` | `setOnClickListener` |
| 12 | `tvDurationValue` | `TextView` | `tvDurationValue` | `setText(...)` |
| 13 | `tvWatchedValue` | `TextView` | `tvWatchedValue` | `setText(...)` |

**Three observations you only see by comparing the columns:**

1. `etRelease` is the ONLY field read from a source other than the widget.
2. Two IDs do not match the field name: `cbOnWatchList` / `cbonWatchList` and `btnMovieAction` / `btMovieAction`.
3. Seven label `TextView`s (`tvTile`, `tvGenre`, `tvBudget`, `tvDuration`, `tvRating`, `tvWatched`, `tvGuidance`) appear in XML but not in the code — they need no reference.

---

## 22.6 `movie_item.xml` — the list card

**It is not used at this commit.** `MainActivity` does not reference it anywhere: there is no `MovieAdapter` and no `inflate(R.layout.movie_item, ...)`. It is the preparation for the next lab, where `ListView` + `ArrayAdapter` are replaced by `RecyclerView` + `MovieAdapter` + this layout.

Why it is worth reading now: it is the only file that shows what a **good** row should look like, in contrast with `simple_list_item_1` (a single `TextView` with the whole `toString()`).

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FILE: movie_item.xml — THE LIST ROW (for RecyclerView, the next lab)
  ======================================================================================
  STRUCTURE:

    MaterialCardView (root)
    +== LinearLayout horizontal
        |== ImageView  96x140dp          <- poster
        +== LinearLayout vertical, 0dp+weight=1
            |== TextView  movieTitle     <- 20sp, bold, max 2 lines
            |== TextView  movieSubtitle  <- "genre · year"
            |== LinearLayout horizontal
            |   |== RatingBar (small, indicator)
            |   +== TextView movieRatingValue
            |== TextView  movieFacts     <- "142 min · $160M"
            +== ChipGroup
                |== Chip chipApproval
                |== Chip chipWatched
                +== Chip chipWatchlist

  WHY THE CARD IS THE ROOT: each row is an independent visual unit,
    with its own shadow and corners. A plain `LinearLayout` would look like a table.
  ======================================================================================
-->

<!--
  MATERIALCARDVIEW — the root of the row.
  ATTRIBUTES:
    layout_width="match_parent"  — the row occupies the full width of the list
    layout_height="wrap_content" — the height given by the content (the 140dp poster)
    layout_marginHorizontal="12dp" — 12dp left/right; the card does not touch the edges
    layout_marginVertical="6dp"   — 6dp top/bottom; separates the rows from each other
    app:cardCornerRadius="16dp"   — rounded corners
    app:cardElevation="3dp"       — shadow. HERE the shadow is PRESENT, unlike
                                    the cards in the form (which are "filled",
                                    with no shadow). A list row must stand out
                                    from the background.
    app:cardUseCompatPadding="true" — adds inner padding so that the shadow is not
                                    clipped by the card bounds on older APIs.
                                    On API 21+ its effect is keeping the shadow visible.
-->
<com.google.android.material.card.MaterialCardView
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginHorizontal="12dp"
    android:layout_marginVertical="6dp"
    app:cardCornerRadius="16dp"
    app:cardElevation="3dp"
    app:cardUseCompatPadding="true">

    <!--
      HORIZONTAL LINEARLAYOUT — poster on the left, information on the right.
      padding="12dp" — the content does not touch the card edge.
      WHY horizontal: the poster and the text column sit side by side.
    -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="12dp">

        <!-- Poster -->

        <!--
          IMAGEVIEW — the poster.
          layout_width="96dp" / layout_height="140dp" — a ratio of ~2:3, like a movie
            poster. FIXED dimensions: the image does not change size depending
            on the text on the right.
          android:background="#11000000" — black with alpha 0x11 (~7% opacity).
            It is a visible PLACEHOLDER while there is no image.
          android:scaleType="centerCrop" — fills the 96x140dp by cropping the edges,
            without distorting. `fitXY` would stretch the image; `centerInside` would leave
            empty bands.
          android:contentDescription="Movie poster" — mandatory for TalkBack.
          android:src="@android:drawable/ic_menu_gallery" — a provisional image.
            At runtime, the adapter would replace it with the real poster.
        -->
        <ImageView
            android:id="@+id/moviePoster"
            android:layout_width="96dp"
            android:layout_height="140dp"
            android:background="#11000000"
            android:scaleType="centerCrop"
            android:contentDescription="Movie poster"
            android:src="@android:drawable/ic_menu_gallery" />

        <!-- Info column -->

        <!--
          THE INFORMATION COLUMN — 0dp + weight 1.
          WHY: the poster is a fixed 96dp; the rest of the width (360 - 96 - margins) must
            be taken by the text column. With `wrap_content`, long text would push
            the card beyond the screen.
          marginStart="12dp" — separates the text from the poster. `start` respects RTL.
          orientation="vertical" — the elements flow from top to bottom.
        -->
        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:layout_marginStart="12dp"
            android:orientation="vertical">

            <!--
              THE TITLE — `movieTitle`.
              textSize="20sp" + textStyle="bold" — a strong hierarchy; the title is
                the main element of the row.
              maxLines="2" — a maximum of two lines. Without it, a long title would push
                the rest of the content down and break the alignment of the rows.
              ellipsize="end" — the cut text ends with "…".
              WHY both: `maxLines` limits, `ellipsize` signals that there is
                more text. `maxLines` alone would cut abruptly, with no hint.
            -->
            <TextView
                android:id="@+id/movieTitle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Movie title"
                android:textSize="20sp"
                android:textStyle="bold"
                android:maxLines="2"
                android:ellipsize="end" />

            <!-- genre · release year, e.g. "Sci-Fi · 2021" -->

            <!--
              THE SUBTITLE — "genre · year".
              textSize="14sp" — smaller than the title.
              textColor="#757575" — a hardcoded grey.
              RISK: in dark mode, #757575 on a dark background has low contrast.
                It should be `?attr/colorOnSurfaceVariant`.
              marginTop="2dp" — glued to the title, like a continuation of it.
            -->
            <TextView
                android:id="@+id/movieSubtitle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Genre · Year"
                android:textSize="14sp"
                android:textColor="#757575" />

            <!-- Rating -->

            <!--
              THE RATING ROW — stars + numeric value.
              gravity="center_vertical" — aligns the stars with the text.
              marginTop="6dp" — separates from the subtitle.
            -->
            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <!--
                  THE SMALL RATINGBAR — `movieRating`.
                  style="?android:attr/ratingBarStyleSmall" — the small framework style
                    (stars of ~12dp). `?android:attr/` = an attribute from the framework theme,
                    not from the application theme.
                  android:isIndicator="true" — the stars are DISPLAY ONLY. They cannot be
                    touched and have no listener. Without it, the user could change
                    the rating from a list row.
                  numStars=5, stepSize=0.5 — the same values as in the form, so that it
                    looks identical.
                -->
                <RatingBar
                    android:id="@+id/movieRating"
                    style="?android:attr/ratingBarStyleSmall"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:numStars="5"
                    android:stepSize="0.5"
                    android:isIndicator="true" />

                <!--
                  THE NUMERIC VALUE — "4.5".
                  marginStart="6dp" — separates it from the stars.
                  textSize="13sp", grey — secondary text.
                  WHY it exists: small stars are hard to read exactly; the digit gives
                    the precise value.
                -->
                <TextView
                    android:id="@+id/movieRatingValue"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:text="4.5"
                    android:textSize="13sp"
                    android:textColor="#757575" />
            </LinearLayout>

            <!-- Facts: duration + budget -->

            <!--
              FACTS — "142 min · $160M".
              A single TextView with two values separated by "·".
              textSize="13sp", a lighter grey (#9E9E9E) — third-level information.
              WHY a single TextView and not two: they are information of the same rank,
                on one line, with no need for separate alignment.
            -->
            <TextView
                android:id="@+id/movieFacts"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="142 min  ·  $160M"
                android:textSize="13sp"
                android:textColor="#9E9E9E" />

            <!-- Status chips: approval, watched, watchlist -->

            <!--
              CHIPGROUP — the container of the three status labels.
              app:chipSpacingHorizontal="6dp" — 6dp between the chips.
              app:singleLine="false" — allows moving to a second line if
                they do not all fit. `true` would cut them off.
              marginTop="8dp" — separates from the facts row.
              WHY ChipGroup and not three TextViews: chips have standardised background,
                corners and padding; they look like labels, not like text.
            -->
            <com.google.android.material.chip.ChipGroup
                android:id="@+id/movieStatusGroup"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                app:chipSpacingHorizontal="6dp"
                app:singleLine="false">

                <!--
                  CHIP 1 — the parental guidance ("Approved").
                  style="@style/Widget.Material3.Chip.Suggestion" — the suggestion chip
                    style: a discreet background, an outline.
                  android:clickable="false" — it is NOT a button. Without it, the chip would
                    get a ripple on touch and would suggest an action that does not exist.
                  app:chipMinHeight="28dp" — a small height, like a label.
                  app:ensureMinTouchTargetSize="false" — WHY: Material forces
                    a 48dp touch target by default, which would inflate the row.
                    For a non-clickable element, the forcing is pointless.
                -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipApproval"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Approved"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />

                <!--
                  CHIP 2 — "Watched".
                  app:chipIcon="@android:drawable/checkbox_on_background" — a check mark
                    inside the chip, so that it can be told apart from the other two
                    without reading the text.
                -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipWatched"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Watched"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:chipIcon="@android:drawable/checkbox_on_background"
                    app:ensureMinTouchTargetSize="false" />

                <!--
                  CHIP 3 — "Watchlist".
                  The same style, without an icon. All three are status labels,
                    not filters.
                -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipWatchlist"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Watchlist"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />
            </com.google.android.material.chip.ChipGroup>
        </LinearLayout>
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

**What you only see by comparing with `activity_item.xml`:**

| Aspect | `activity_item.xml` (form) | `movie_item.xml` (row) |
|---|---|---|
| Card | `filled`, no shadow, 20dp corners | `elevation 3dp`, 16dp corners |
| Colours | all from the theme (`?attr/`) | three hardcoded greys |
| Text | `textAppearance` styles | explicit `textSize` |
| Rating | editable | `isIndicator="true"` |
| Controls | interactive | all `clickable="false"` |

The row is intentionally more "physical" (shadow, fixed dimensions) and less tied to the theme. It is a design decision, not a mistake — but hardcoding the colours remains a risk for dark mode.

---

## 22.7 How it all fits together — the complete flow

### 22.7.1 Starting the application

```
STARTUP
  MainActivity.onCreate(savedInstanceState = null)
    |
    |== super.onCreate                 -> AppCompat installs its delegate
    |== EdgeToEdge.enable(this)         -> the windows draw under the bars
    |== setContentView(activity_main)   -> the view tree exists
    |== insets on R.id.main             -> padding = status bar + nav bar
    |== addSampleMovies()               -> movies = [Inception, Toy Story, The Matrix]
    |== new ArrayAdapter(this,
    |       simple_list_item_1, movies) -> movieAdapter holds the REFERENCE to `movies`
    |== initControls()                  -> fabInsert, listView, setAdapter
    |== initListeners()                 -> FAB + item click (launcher is still null)
    +== registerForActivityResult(...)  -> launcher created
          |
          v
  ListView shows 3 rows:
    "Movie{title='Inception', release=..., genre='Sci-Fi', ...}"
    "Movie{title='Toy Story', ...}"
    "Movie{title='The Matrix', ...}"
```

### 22.7.2 Insert — FAB

```
PRESS THE FAB
  fabInsert.onClick
    |
    |== new Intent(MainActivity.this, ItemActivity.class)   (no extras)
    +== launcher.launch(intent)
          |
          v
  MainActivity: onPause
  ItemActivity: onCreate
    |
    |== setContentView(activity_item)
    |== insets on R.id.main
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
    |     |== Intent with no target
    |     |== putExtra(MOVIE_EXTRA, movie)
    |     |== (position == -1, so POSITION_EXTRA is NOT added)
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
  ListView redraws -> the 4th row appears
```

### 22.7.3 Edit — click on a row

```
CLICK ON ROW 1
  listView.onItemClick(parent, view, position = 0, id = 0)
    |
    |== new Intent(MainActivity.this, ItemActivity.class)
    |== putExtra(MOVIE_EXTRA, movies.get(0))    <- SERIALISATION
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
  THE USER MODIFIES AND PRESSES "Update Movie"
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

### 22.7.4 The object that travels

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
                          result Intent { "movie" -> Movie@D,
                                          "position" -> 0 }
                                    |
                                    v
                          movies.set(0, Movie@D)
                                    |
                                    v
                          Movie@A stays in the heap until GC
```

**The practical consequence:** a change in the form is not visible in the list until `movies.set(...)`. There is no "link" between the object in the list and the one in the form — they are two distinct objects.

### 22.7.5 Recycling the rows in a ListView

```
The ListView has 7 visible rows, the list has 100 elements.

  screen: [0][1][2][3][4][5][6]

  you scroll down:
    row 0 goes out at the top  ->  convertView = row 0
    row 7 comes in at the bottom <-  ArrayAdapter.getView(7, convertView, parent)

  ArrayAdapter:
    if convertView != null:
        reuses the view (no longer inflates the XML)
    TextView.setText(movies.get(7).toString())

  WHY it matters: without recycling, 100 rows would mean 100 inflates.
    With recycling, there are ~8 views for however many elements.

  WHY `notifyDataSetChanged()` is necessary:
    The ListView does NOT observe the list. It only knows what the adapter told it at the last bind.
    `notifyDataSetChanged()` -> adapter.notifyChanged() -> the ListView rebinds
    the visible rows.
```

---

## 22.8 What to retain from each file

| File | The essence | The trap |
|---|---|---|
| `Movie.java` | a serialisable POJO, 10 fields, an explicit empty constructor, `isX()` for booleans, `toString()` = the display contract | the 10-parameter constructor is POSITIONAL |
| `MainActivity.java` | the order in `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` | `launcher` is assigned AFTER `initListeners` |
| `ItemActivity.java` | 13 `findViewById`, `releaseCal` as the source of truth, a generic loop over the `RadioGroup`, `setResult` + `finish` | empty budget -> crash; null date -> crash |
| `activity_main.xml` | `FrameLayout` + the order of the children + `layout_gravity` on the FAB | `android:orientation` is invalid on a FrameLayout |
| `activity_item.xml` | a `ScrollView` with one child, `MaterialCardView` as a section, `TextInputLayout`, a wrapped `Spinner` | `hintEnabled` must be correlated with the existence of the label |
| `movie_item.xml` | a list card, `weight` for the text column, chips for the status | it is not used yet; hardcoded colours |

### The 10 things you will have been asked

1. **Why `implements Serializable`?** So that it can be put in an `Intent` with `putExtra`.
2. **Is the object received the original?** No. It is a deserialised copy.
3. **Why an explicit empty constructor?** A constructor with parameters suppresses the implicit one, and `saveMovie` does `new Movie()`.
4. **Why `isWatched()`?** The JavaBeans convention for `boolean`.
5. **Why `notifyDataSetChanged()`?** The ListView does not observe the list; the adapter must announce it.
6. **Why `MainActivity.this`?** In the anonymous class, `this` is the listener, not the `Context`.
7. **Why `releaseCal` and not `etRelease`?** The calendar is the source of truth; the text can be invalid.
8. **Why is `fromUser` ignored?** The label must reflect the value even when it comes from code.
9. **Why `0dp` + `weight`?** "Take all the remaining space", not "take the natural size".
10. **Why `?attr/` and not `@color/`?** `?attr/` is a theme role and adapts to dark mode.

---

## Chapter 22 summary

- The model does not touch the UI; the activities contain no row logic.
- `onCreate`: `super` -> `EdgeToEdge` -> `setContentView` -> insets -> data -> adapter -> controls -> listeners -> launcher.
- `releaseCal` is the source of truth for the date, not the text in the `EditText`.
- The loop over the `RadioGroup` makes the code generic — you add buttons in XML, the code sees them.
- `setResult(RESULT_OK, intent)` + `finish()` is the mandatory pair.
- `notifyDataSetChanged()` after any change to the list.
- `movie_item.xml` exists, but is not wired in — preparation for the next lab.
- Three real bugs: empty budget, `release` null, scientific notation.

**Back to the** [cheatsheet](21%20-%20Cheatsheet.md) **or to the** [overview](index.html).
