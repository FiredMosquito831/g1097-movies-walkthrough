# Chapter 02 — The `Movie` model

**Objective:** a `ro.ase.ie.g1097.model.Movie` class that holds all the data for one movie, is serializable (so it can travel between activities), and has constructors plus getters/setters.

**Estimated time:** 20–30 min.

**Final file:** `cod-final/java/ro/ase/ie/g1097/model/Movie.java` (3196 B, SHA-256 `feb7fffc5273fcbf…`)

---

## Step 2.1 — Why a separate model

### Why

You could keep the data in `MainActivity`, in 10 separate variables. Why not?

Because a movie **travels**: from `MainActivity` to `ItemActivity`, back, into the list, eventually into a database. You need a **package** that carries all the fields together, in a single object.

That is a **model** (or POJO — Plain Old Java Object): a class with no UI logic, just data.

### The golden rule

> The model **doesn't know** what an `EditText`, a `Spinner` or an `Intent` is. It has no `android.*` imports.

If `Movie.java` has `import android.widget.EditText`, you got the architecture wrong. The model is plain Java — it can be tested without an emulator.

### How

Create the package `ro.ase.ie.g1097.model` (right-click on `ro.ase.ie.g1097` → **New → Package**) and inside it the class `Movie`.

---

## Step 2.2 — The fields

### Why each type

Every field corresponds to **a widget** in the form. The type isn't chosen at random — it's chosen to match what the widget can produce.

| Field | Java type | Source widget | Why this type |
|---|---|---|---|
| `title` | `String` | `TextInputEditText` | free text |
| `release` | `Date` | `TextInputEditText` + `DatePickerDialog` | a **date**, not a string; so you can compute differences between dates |
| `genre` | `String` | `Spinner` | one of 10 texts |
| `budget` | `double` | `TextInputEditText` (`numberDecimal`) | money, with decimals |
| `duration` | `int` | `SeekBar` | progress is an `int` between min and max |
| `rating` | `float` | `RatingBar` | `RatingBar.getRating()` returns a `float` |
| `watched` | `boolean` | `MaterialSwitch` | tick |
| `approval` | `String` | `RadioGroup` | the text of the selected button ("G", "PG-13"…) |
| `onWatchlist` | `boolean` | `MaterialCheckBox` | tick |
| `poster` | `String` | `TextInputEditText` (`textUri`) | a URL |

> **Why `float` and not `double` for rating?** Because `RatingBar.getRating()` returns a `float`. If you used `double`, you'd have to convert on every read. You choose the type of the source.

> **Why `double` and not `float` for budget?** Because money needs precision; `float` loses digits at large values (160000000 becomes 1.6E8 with rounding errors).

### How

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;
import java.util.Date;

public class Movie implements Serializable {
    private String title;        // EditText
    private Date release;        // EditText date
    private String genre;        // Spinner
    private double budget;       // EditText number
    private int duration;        // SeekBar
    private float rating;        // RatingBar
    private boolean watched;     // Switch
    private String approval;     // RadioGroup | RadioButtons
    private boolean onWatchlist; // Checkbox
    private String poster = null;

    // ... constructors and getters follow
}
```

Notice the comments on the right: the professor noted **which widget** produces each field. That's excellent documentation — keep it.

`poster = null` is explicit, even though a `String` is `null` by default anyway. It's a form of documentation: "it can be missing".

### Why `private`

Encapsulation. If the fields were `public`, anyone could write `movie.budget = -5`. With `private` + a setter, you can add validation later without changing every caller.

---

## Step 2.3 — `implements Serializable`

### Why

`Intent.putExtra(String, Serializable)` is **the only simple way** to send a whole object between two activities.

`Serializable` is a **marker** interface: it has no methods to implement. It's just a label that tells the JVM: "you may turn this object into a byte stream".

### How it actually works

When you call `intent.putExtra("movie", movie)`:

1. Android serializes the object (writes the fields into a `byte[]`).
2. The `byte[]` is placed in the `Intent` (which is itself serialized as a `Parcel`).
3. The `Intent` crosses the process boundary (if needed) or stays in memory.
4. In `ItemActivity`, `getSerializableExtra("movie")` deserializes — **it creates a new object**, with the same values.

> **Major trap:** the object you receive is a **copy**, not the same reference. If you modify it in `ItemActivity`, the object in `MainActivity` **does not change**. That's why, when editing, `ItemActivity` sends back the position and the new movie, and `MainActivity` does `movies.set(position, movie)`.

### What has to be serializable

All fields must be serializable. `String`, `Date`, the primitives — yes. If you had a field of type `Drawable` or `Context`, it would blow up with `NotSerializableException`.

### Exercise 2.3

**Requirement:** what happens if you add a field `private java.util.Calendar releaseCalendar;` to `Movie`? Reason it out mentally, then check.

<details>
<summary>Hint</summary>

Does `Calendar` implement `Serializable`? Check the docs: `java.util.Calendar implements Serializable, Cloneable, Comparable<Calendar>`.

</details>

<details>
<summary>Solution</summary>

**What was done:** you hypothetically added a field `private java.util.Calendar releaseCalendar;` to `Movie` and asked yourself whether it serializes.

**The answer:** **it works** — `java.util.Calendar` implements `Serializable`, so it does not throw `NotSerializableException`.

**Why it's still a bad idea:** you'd have **two sources of truth** for the same information — `release` (a `Date`) and `releaseCalendar` (a `Calendar`). They can diverge: you set `release` but forget `releaseCalendar`, and you have a movie that "came out in 2010" but whose calendar says 2011.

**Remember:**
1. **Serializability is a necessary condition, not a sufficient one.** A good model is also **normalized** — each piece of information has exactly one representation.
2. If you need both forms (Date for the UI, Calendar for calculations), convert on demand: `Calendar c = Calendar.getInstance(); c.setTime(release);` — don't store both.
3. `transient` fields are **not** serialized. If you have a derived field that shouldn't be sent between activities, mark it `transient`.

**Where it comes back:** in chapter 07 (step 7.2), `ItemActivity` has a `Calendar releaseCal` field — but that's **UI state**, not part of the model. The model only has `Date release`. The separation is correct: the model holds the data, the activity holds the temporary state of the form.

</details>

---

## Step 2.4 — The no-argument constructor

### Why

In `ItemActivity.saveMovie()` you have:

```java
Movie movie = new Movie();
movie.setTitle(...);
movie.setRelease(...);
// ...
```

An **empty** object is created, then filled field by field. You need `new Movie()` — that is, a constructor with no parameters.

> **Java gotcha:** if you **define** a constructor with parameters, the compiler **no longer generates** the no-argument constructor automatically. So you have to write it explicitly. That's why you find it at the **end** of the class in the repo — and it's a classic exam trap.

### How

```java
public Movie() {
}
```

Done. (In the repo it sits at the end of the file, after the getters. Its position in the file doesn't matter to the compiler.)

---

## Step 2.5 — The all-arguments constructor

### Why

In `MainActivity.addSampleMovies()` the demo movies are created **in a single expression**:

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
        "https://example.com/posters/inception.jpg"));
```

A constructor with 10 parameters keeps the code compact. The alternative — 10 setter lines per movie — would fill `MainActivity` with noise.

### The ordering trap

The 10 parameters are **positional**. Nothing stops you from writing `"PG-13"` where `true` belongs. The compiler won't catch it if the types happen to match (e.g. `String` vs `String`).

The order from the repo, which you follow **exactly**:

```
1. String title
2. Date release
3. String genre
4. double budget
5. int duration
6. float rating
7. boolean watched
8. String approval
9. boolean onWatchlist
10. String poster
```

### How

```java
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster) {
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

`this.title = title;` — `this` is required when the parameter has the same name as the field. Without `this`, you'd write `title = title;` (self-assignment, the field stays `null`).

### Exercise 2.5

**Requirement:** write a second constructor that takes only `title` and `genre` and leaves the rest at their default values. What values will `budget`, `duration`, `rating` have?

<details>
<summary>Hint</summary>

An undeclared `double` = `0.0`, an `int` = `0`, a `float` = `0.0f`, a `boolean` = `false`, a `String` = `null`, a `Date` = `null`.

</details>

<details>
<summary>Solution</summary>

```java
public Movie(String title, String genre) {
    this.title = title;
    this.genre = genre;
    // the rest keep their Java default values
}
```

`budget = 0.0`, `duration = 0`, `rating = 0.0f`, `watched = false`, `approval = null`, `onWatchlist = false`, `poster = null`, `release = null`.

**What was done:** you added an **overloaded** constructor — a second one, with two parameters, alongside the ten-parameter one.

**How overloading works:** Java picks the constructor by **signature** (the number and types of the parameters), not by name. `new Movie("Dune", "Sci-Fi")` finds the `(String, String)` one. `new Movie()` finds the empty one. `new Movie("Dune", date, "Sci-Fi", ...)` finds the ten-parameter one.

**Why the default values matter:** in Java, instance fields are automatically initialized to their default values (`0`, `false`, `null`). You **don't** have to write them. But you do have to know what they are, because the UI will display them.

**Remember:**
1. **Java default values:** `int`/`long`/`short`/`byte` = 0, `float`/`double` = 0.0, `boolean` = false, **any object = `null`**.
2. `release = null` is dangerous: `dateFormat.format(null)` throws `NullPointerException`.
3. A constructor that leaves fields `null` moves the responsibility for validation to the **consumer** (the UI). That's a design decision, not necessarily a mistake.

**Where it comes back:** in chapter 09 (step 9.3) you'll see exactly the NPE caused by `release = null`. Your local sync version fixes it with `if (existing.getRelease() != null)`. **The model allows null; the UI must defend itself.**

</details>

---

## Step 2.6 — Getters and setters

### Why

The code in both activities reads and writes fields through methods:

```java
movie.setTitle(etTitle.getText().toString());
// ...
existing.getRelease()
```

You're not allowed to do `movie.title` directly — it's `private`.

### The JavaBeans convention

| Field type | Getter | Setter |
|---|---|---|
| `String`, `Date` | `getTitle()` | `setTitle(String)` |
| `double` | `getBudget()` | `setBudget(double)` |
| `int` | `getDuration()` | `setDuration(int)` |
| `float` | `getRating()` | `setRating(float)` |
| `boolean` | **`isWatched()`** | `setWatched(boolean)` |

> **Careful with `boolean`:** the getter is `isWatched()`, not `getWatched()`. There's a trap here: in `MovieAdapter` (chapter 11) the code calls `movie.isWatched()` and `movie.isOnWatchlist()`. If you wrote `getWatched()`, the code won't compile.

### How

```java
public String getTitle() { return title; }
public void setTitle(String title) { this.title = title; }

public Date getRelease() { return release; }
public void setRelease(Date release) { this.release = release; }

public String getGenre() { return genre; }
public void setGenre(String genre) { this.genre = genre; }

public double getBudget() { return budget; }
public void setBudget(double budget) { this.budget = budget; }

public int getDuration() { return duration; }
public void setDuration(int duration) { this.duration = duration; }

public float getRating() { return rating; }
public void setRating(float rating) { this.rating = rating; }

public boolean isWatched() { return watched; }
public void setWatched(boolean watched) { this.watched = watched; }

public String getApproval() { return approval; }
public void setApproval(String approval) { this.approval = approval; }

public boolean isOnWatchlist() { return onWatchlist; }
public void setOnWatchlist(boolean onWatchlist) { this.onWatchlist = onWatchlist; }

public String getPoster() { return poster; }
public void setPoster(String poster) { this.poster = poster; }
```

### Android Studio shortcut

**Alt+Insert** (or right-click → **Generate**) → **Getter and Setter** → select all fields → OK. It generates all 20 methods. **Write them manually once anyway**, so you know what you're generating.

### Exercise 2.6

**Requirement:** why does `getDuration()` return `int` but `getBudget()` return `double`, when both are numbers? Answer without looking at the table.

<details>
<summary>Answer</summary>

**What was done:** you answered a "why is the type like that" question without writing code.

**The answer:** because their **source** differs. `SeekBar.getProgress()` returns `int` — progress is an integer between `min` and `max`. The budget comes from a text field with decimals (`numberDecimal`) and is read with `Double.parseDouble`, which returns `double`.

**The general rule:** **the field type = the type of the source**. If the source is `int`, the field is `int`. If the source is `double`, the field is `double`. That way you avoid conversions on every read/write.

**Remember:**
1. The `int` → `double` conversion is **implicit** (no data lost). The `double` → `int` conversion is **explicit** (you lose decimals).
2. If you had used `int budget`, you'd lose the decimals on every save.
3. If you had used `double duration`, you'd get `148.0` instead of `148` — pointless.

**Where it comes back:** in chapter 07 (step 7.8), `saveMovie` does exactly the reverse conversions: `sbDuration.getProgress()` (int) → `setDuration(int)`, `Double.parseDouble(...)` (double) → `setBudget(double)`. The types match, no cast needed.

</details>

---

## Step 2.7 — `toString()`

### Why

`ArrayAdapter` — the one used in `MainActivity` — **doesn't know** how to display a `Movie`. It receives a list of objects and, for each one, calls `toString()`. If you don't override `toString()`, the `ListView` will show:

```
ro.ase.ie.g1097.model.Movie@a1b2c3d
```

which is useless. So `toString()` is **the display mechanism** for the list in chapter 04.

> Important: in chapter 11, when you move to `RecyclerView`, `toString()` is **no longer used** — the adapter reads the individual fields with getters. But until then, it's the only way the list shows anything.

### How

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
            '}';
}
```

### Why it looks like that

`'\''` is an escaped `'`. The `Key{key='value', ...}` format is generated by IntelliJ/Android Studio (**Alt+Insert → toString()**), not invented by the professor.

### Warning

If you leave `toString()` like that, the `ListView` will show **everything** — including the poster URL and all 10 fields, on a single line. It will look terrible.

But that's **how it is in the repo** at commit `d719ffc`. The list looks ugly until chapter 11, when `RecyclerView` + `movie_item.xml` make it pretty. It's proof that the app is a work in progress, not finished.

### Exercise 2.7

**Requirement:** temporarily change `toString()` to return only `title + " (" + rating + ")"`. Run the app from chapter 04 (after you finish it) and notice the difference. Then **go back** to the repo version.

<details>
<summary>Hint</summary>

Don't forget that the `ListView` uses `android.R.layout.simple_list_item_1`, which has a single `TextView`. Everything you return appears on one line.

</details>

<details>
<summary>Solution</summary>

```java
@Override
public String toString() {
    return title + " (" + rating + ")";
}
```

**What was done:** you overrode `toString()` with a compact form that returns only the title and the rating.

**What you see:** in the list, `Inception (4.5)`, `Toy Story (4.0)`, `The Matrix (5.0)` — far more readable than `Movie{title='Inception', release=Mon Jul 16...}`.

**Why it works:** `ArrayAdapter.getView()` calls `toString()` on each element and puts the result into a `TextView`. So **whatever** you return appears on the list row. It's an implicit contract: if you want the list to look good with `ArrayAdapter`, `toString()` has to be friendly.

**Remember:**
1. **`toString()` is the display contract** for `ArrayAdapter`. It's not just for debugging.
2. `rating` is a `float`; `" (" + rating + ")"` converts to `String` automatically.
3. Go back to the full version after the exercise — fidelity to the repo matters for the exam.

**Where it comes back:** in chapter 11, `RecyclerView` **no longer uses** `toString()`. `MovieAdapter.bind()` reads the individual fields with getters. So `toString()` becomes irrelevant for display — but stays useful for debugging.

**The lesson:** `toString()` isn't just for debugging; with `ArrayAdapter` it's **the display contract**.

</details>

---

## Step 2.8 — Verifying the model

### Why

Before you build the UI, you verify the model is correct. A wrong model propagates through the rest of the app.

### How

The final file must look exactly like `cod-final/java/ro/ase/ie/g1097/model/Movie.java`. Compare with:

```bash
# in Git Bash, from the test 1 folder
diff <(cat cod-final/java/ro/ase/ie/g1097/model/Movie.java) <(cat "_progres/Movies1097/app/src/main/java/ro/ase/ie/g1097/model/Movie.java")
```

Or just open both files side by side in Android Studio and compare visually.

### Checklist

- [ ] the package is `ro.ase.ie.g1097.model`
- [ ] `implements Serializable`
- [ ] 10 `private` fields, exactly the types from the table
- [ ] the comments naming the source widget
- [ ] an **explicit** no-argument constructor
- [ ] a 10-argument constructor, in the correct order
- [ ] 20 getters/setters, `isWatched`/`isOnWatchlist` for the booleans
- [ ] `toString()` overridden

> **The file name must be `Movie.java`** and the class `public class Movie`. If not, Java won't compile.

---

## Step 2.9 — Reflection exercise

**Requirement:** without looking at the code, write on paper what `new Movie("Dune", 2021, "Sci-Fi")` looks like. Does it compile? Why / why not?

<details>
<summary>Answer</summary>

**It doesn't compile.** You have no `Movie(String, int, String)` constructor. You only have `Movie()` and `Movie(String, Date, String, double, int, float, boolean, String, boolean, String)`.

Java doesn't do implicit conversions from `int` to `Date`. You need:

```java
new Movie("Dune", new GregorianCalendar(2021, Calendar.OCTOBER, 22).getTime(),
          "Sci-Fi", /* ... the rest */);
```

or, more simply, the empty constructor plus setters.

**The lesson:** constructors are **overloaded** by signature (the types and number of parameters), not by name. If you want convenience, add a `Movie(String title, String genre)` constructor.

</details>

---

## Chapter 02 summary

- `Movie` is a serializable POJO, with no Android imports.
- 10 fields, each with the type dictated by its source widget.
- An **explicit** empty constructor + a full constructor with 10 parameters.
- Getters/setters, with `isX()` for booleans.
- `toString()` is the display contract for `ArrayAdapter`.

### Self-check

1. Why does `Movie` have no `import android.*`?
2. What happens if you forget the empty constructor?
3. Why isn't the object received in `ItemActivity` "the same" object?
4. Why does `toString()` matter for `ListView` but not for `RecyclerView`?

<details>
<summary>Answers</summary>

1. Because the model has to be testable and reusable without Android. If it imported `EditText`, it would depend on the UI.
2. `new Movie()` won't compile — the compiler saw a custom constructor and no longer generates the implicit one.
3. `Intent` serializes/deserializes — a copy by value, not by reference. That's why editing sends a result back instead of modifying directly.
4. `ArrayAdapter` implicitly calls `toString()` on the elements; `RecyclerView.Adapter` calls the methods you write in `onBindViewHolder`.

</details>

---

**Next chapter:** [03 - Main screen - layout.md](03%20-%20Main%20screen%20-%20layout.md)
