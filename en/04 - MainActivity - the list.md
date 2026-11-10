# Chapter 04 — `MainActivity`: the movie list

**Objective:** a `MainActivity` that creates 3 demo movies, shows them in a `ListView` via `ArrayAdapter`, and has the FAB wired up (no navigation yet — that comes in ch. 08).

**Estimated time:** 30–45 min.

**Final file:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` (5455 B, SHA-256 `6c82723f8e099c87…`)

> **Note:** in this chapter we write `MainActivity` **without** `ActivityResultLauncher` and without `onItemClick`. Those come in ch. 08. Here only: demo data + list + a FAB that does nothing yet.

---

## Step 4.1 — The class skeleton

### Why

An `Activity` is a class with a **lifecycle** controlled by Android. You don't create it with `new MainActivity()`. The system instantiates it when needed and calls methods:

```
onCreate()   ← it's created
onStart()    ← it becomes visible
onResume()   ← it gets focus
onPause()    ← it loses focus
onStop()     ← it's no longer visible
onDestroy()  ← it's destroyed
```

You override only what you need. Here: `onCreate()`.

### How

```java
package ro.ase.ie.g1097.activities;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.List;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MainActivity extends AppCompatActivity {

    private FloatingActionButton fabInsert;
    private ListView listView;
    private final List<Movie> movies = new ArrayList<>();
    private ArrayAdapter<Movie> movieAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        addSampleMovies();

        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
        initControls();
        initListeners();
    }

    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        listView = findViewById(R.id.listView);
        listView.setAdapter(movieAdapter);
    }

    private void initListeners() {
        // filled in chapter 08
    }

    private void addSampleMovies() {
        // filled in at step 4.5
    }
}
```

### Why the fields are `private` and not local

`fabInsert`, `listView`, `movieAdapter` are used in **several methods** (`initControls`, `initListeners`, `onCreate`). If they were local to `onCreate`, you couldn't reach them from `initListeners`.

`movies` is `final` because the **reference** never changes — the same list, only its contents change (`add`, `set`). `final` on a collection doesn't mean "immutable", it means "you don't reassign it".

> **Remember:** `final List<Movie> movies = new ArrayList<>();` — you can do `movies.add(...)`, but not `movies = new ArrayList<>();`. It's a distinction that shows up in the exam.

---

## Step 4.2 — `setContentView` and the order of calls

### Why the order in `onCreate` matters

```java
super.onCreate(savedInstanceState);   // 1. runs the parent's lifecycle
setContentView(R.layout.activity_main); // 2. builds the view tree
addSampleMovies();                      // 3. fills the data list (no UI)
movieAdapter = new ArrayAdapter<>(...); // 4. creates the adapter over the list
initControls();                         // 5. findViewById + setAdapter
initListeners();                        // 6. wires the buttons
```

**Why `setContentView` before `findViewById`?** Because `findViewById` searches the view tree. Before `setContentView`, the tree doesn't exist → `null`.

**Why `addSampleMovies` before `new ArrayAdapter`?** Because `ArrayAdapter` receives the **reference** to the list. If you added movies afterwards, it would still work (same reference), but `notifyDataSetChanged()` would be required. Filling it beforehand means the adapter sees the list already populated at construction.

**Why `initControls` after `new ArrayAdapter`?** Because `initControls` calls `listView.setAdapter(movieAdapter)` — so `movieAdapter` must exist.

### The classic wrong order

```java
initControls();  // NullPointerException at listView.setAdapter(movieAdapter)
movieAdapter = new ArrayAdapter<>(...);
```

`movieAdapter` is `null` when it's used. **This is the most common exam mistake.**

### Exercise 4.2

**Requirement:** move `initControls()` **before** `movieAdapter = new ArrayAdapter<>(...)`. Run it. Read `Logcat`.

<details>
<summary>Hint</summary>

Look for `NullPointerException` and check the line in `MainActivity` that crashed.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we swapped the order of two lines in `onCreate`.

**What happens:** the app crashes at startup with:

```
java.lang.NullPointerException: Attempt to invoke virtual method
'void android.widget.ListView.setAdapter(android.widget.ListAdapter)'
on a null object reference
```

or, if `listView` is found but `movieAdapter` is `null`:

```
java.lang.NullPointerException
    at ro.ase.ie.g1097.activities.MainActivity.initControls(MainActivity.java:...)
```

**Why:** `movieAdapter` is a `private` field that hasn't been initialized yet. In Java, an object field that hasn't been assigned holds `null`. `setAdapter(null)` doesn't throw immediately, but the `ListView` can't display anything; if `listView` itself is `null`, `listView.setAdapter(...)` throws an NPE instantly.

**Remember:**
1. **The order of initializations is critical.** The rule: *define before you use*.
2. `findViewById` returns `null` if the ID doesn't exist or isn't in the tree yet.
3. The NPE tells you the **file and line** — read it, don't guess.

**Where it comes back:** in ch. 07, `ItemActivity.initControls()` must be called **after** `setContentView`, otherwise **all** 13 `findViewById` calls return `null`. And in ch. 08, `launcher` must be initialized **before** `initListeners` uses it in `onClick`.

</details>

---

## Step 4.3 — `ArrayAdapter`

### Why

`ListView` doesn't know how to display a `Movie`. It needs an **adapter** that answers two questions:

- how many elements are there? (`getCount()`)
- what does the element at position `i` look like? (`getView(i, ...)`)

`ArrayAdapter` is the ready-made implementation for lists of objects. It calls `toString()` on each element and puts it into a `TextView`.

### How

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

Three arguments:

| Argument | What it is | Why |
|---|---|---|
| `this` | `Context` | the adapter needs a context to create views |
| `android.R.layout.simple_list_item_1` | a layout **from Android**, not from the project | contains a single `TextView` with the id `android.R.id.text1` |
| `movies` | `List<Movie>` | the data source — a **reference**, not a copy |

### `android.R` vs `R`

- `android.R.layout.simple_list_item_1` → a resource from the **Android system** (exists on every phone)
- `R.layout.activity_main` → a resource from **your project**

That's why you don't need a `simple_list_item_1.xml` file — it's already in Android.

### The `notifyDataSetChanged` trap

`ArrayAdapter` holds the reference to the list, but it **doesn't observe** changes to it automatically. If you do `movies.add(movie)`, the list changes, but the `ListView` **doesn't redraw** until you call:

```java
movieAdapter.notifyDataSetChanged();
```

> **Remember:** `notifyDataSetChanged()` is mandatory after any change to the list. In ch. 08 you'll see it twice, in `onActivityResult`.

### Exercise 4.3

**Requirement:** add to `onCreate`, after `initListeners()`, the line `movies.add(new Movie("Test", null, "Drama", 0, 0, 0f, false, "G", false, null));` — **without** `notifyDataSetChanged()`. Run it. Does "Test" appear in the list?

<details>
<summary>Hint</summary>

Think about when the `ListView` reads its data: at `setAdapter`, or on every frame?

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added a movie after the adapter was already set on the list, without notifying.

**What you see:** "Test" **doesn't appear**. The list stays at the 3 demo movies.

**Why:** `ListView` builds its views once, when it receives the adapter (`setAdapter`), and reuses them on scroll. It has no mechanism for "observing" the list. `notifyDataSetChanged()` is the explicit signal: "the data changed, rebuild".

**Remember:**
1. `ArrayAdapter` + `ListView` = a "push" model: you have to notify.
2. `RecyclerView.Adapter` (ch. 11) is the same — still `notifyDataSetChanged()` or finer variants (`notifyItemInserted`, `notifyItemChanged`).
3. If you added the movie **before** `new ArrayAdapter<>(...)`, it would appear without notification, because the adapter would be built with the list already populated.

**Where it comes back:** in ch. 08, `onActivityResult` does exactly `movies.add(movie); movieAdapter.notifyDataSetChanged();`. If you forget the second line, the movie is saved into the list but **doesn't appear** — and you'll think the save isn't working.

</details>

---

## Step 4.4 — `findViewById`

### Why

`findViewById(R.id.x)` searches the view tree for an element with the ID `x`. It's like a `document.getElementById()`.

### How

```java
fabInsert = findViewById(R.id.floatingActionButton);
listView = findViewById(R.id.listView);
```

### Why `R.id.floatingActionButton`

In XML you have `android:id="@+id/floatingActionButton"`. The `@+id/` creates the ID in `R.id`. So in code: `R.id.floatingActionButton`.

### Why no cast is needed

In modern Java (and with a recent `compileSdk`), `findViewById` is **generic**:

```java
public <T extends View> T findViewById(int id)
```

The compiler infers the type from the assignment. So `ListView listView = findViewById(R.id.listView);` works without `(ListView)`.

> **History:** in old code you saw `(ListView) findViewById(R.id.listView)`. The explicit cast is no longer necessary, but you'll meet it in examples.

### The trap: `findViewById` after `setContentView`

If you call `findViewById` before `setContentView`, it returns `null`. That's why `initControls()` is called **after** `setContentView`.

### Exercise 4.4

**Requirement:** move `initControls();` **before** `setContentView(R.layout.activity_main);`. What happens?

<details>
<summary>Solution — explained</summary>

**What was done:** we moved the `initControls()` call before `setContentView`.

**What happens:** `fabInsert` and `listView` receive `null`. Then `listView.setAdapter(movieAdapter)` throws:

```
NullPointerException: Attempt to invoke virtual method 'void android.widget.ListView.setAdapter(...)' on a null object reference
```

**Why:** `setContentView` is what **builds** the view tree from XML. Before it, `findViewById` has nowhere to search.

**Remember:**
1. The mandatory order in `onCreate`: `super.onCreate` → `setContentView` → `findViewById`.
2. `findViewById` returns `null`, it does **not** throw when it can't find something — so the error appears later, at the first call on the `null` object. That makes debugging harder.
3. If a `findViewById` returns `null` and the ID **exists** in XML, check: (a) did you call `setContentView` with the right layout? (b) is the element in **that** layout or in an included one?

**Where it comes back:** in ch. 07, `ItemActivity` has 13 `findViewById` calls. If one returns `null`, you'll get an NPE in `fillForm` or `saveMovie`, not in `initControls`. Same cause, different place it shows up.

</details>

---

## Step 4.5 — The demo data: `GregorianCalendar`

### Why

You need 3 movies to see a populated list. Each has a **release date**. How do you build a `Date` from a day, month and year?

`java.util.Date` is just a `long` (milliseconds since 1970). It has no friendly constructors. `GregorianCalendar` is the class that knows how to build a date from components.

### How

```java
private void addSampleMovies() {
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
```

### The month trap

`Calendar.JULY` = **6**, not 7! Months are indexed from 0:

| Constant | Actual value | Index |
|---|---|---|
| `Calendar.JANUARY` | January | 0 |
| `Calendar.FEBRUARY` | February | 1 |
| … | … | … |
| `Calendar.JULY` | July | 6 |
| `Calendar.DECEMBER` | December | 11 |

That's why you use the constants, not numbers. `new GregorianCalendar(2010, 7, 16)` would be **16 August 2010**, not 16 July.

> **This is the most common `Calendar` mistake.** In the exam, if you're asked for "16 July 2010", you write `Calendar.JULY`, not `7`.

### Why `.getTime()`

`GregorianCalendar` **is** a `Calendar`, not a `Date`. `getTime()` converts it to a `Date` (extracts the milliseconds).

```
GregorianCalendar(2010, JULY, 16)  --getTime()-->  Date(millis)
```

### Why `4f` and not `4.0`

`4f` is a `float` literal. `4.0` would be a `double` and wouldn't fit the `float rating` parameter without a cast. `4.5f`, `5f` — same.

### Why `160000000` and not `160_000_000`

Both are valid in Java 7+. The repo uses the form without underscores. `160_000_000` is more readable, but be consistent.

### Exercise 4.5

**Requirement:** add a fourth demo movie: "Interstellar", 7 November 2014, "Sci-Fi", budget 165000000, 169 minutes, rating 4.5, watched `true`, approval "PG-13", watchlist `false`, poster `https://example.com/posters/interstellar.jpg`.

<details>
<summary>Hint</summary>

November = `Calendar.NOVEMBER`. Parameter order: title, release, genre, budget, duration, rating, watched, approval, onWatchlist, poster.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added a fourth `movies.add(new Movie(...))` at the end of `addSampleMovies()`.

```java
movies.add(new Movie(
        "Interstellar",
        new GregorianCalendar(2014, Calendar.NOVEMBER, 7).getTime(),
        "Sci-Fi",
        165000000,
        169,
        4.5f,
        true,
        "PG-13",
        false,
        "https://example.com/posters/interstellar.jpg"));
```

**How to check:** run it. A fourth row appears in the list: `Movie{title='Interstellar', release=..., ...}`.

**Why it works with no other changes:** `addSampleMovies()` is called **before** `new ArrayAdapter<>(...)`. The adapter is built with the list already complete, so you don't need `notifyDataSetChanged()`.

**Remember:**
1. The constructor's parameter order is **positional**. `169` (int) in position 5, `4.5f` (float) in 6. If you swap them, the compiler **won't** catch it (both are numeric, with an implicit `int`→`float` conversion), but the data will be wrong.
2. `Calendar.NOVEMBER` = 10, not 11.
3. If you forget `.getTime()`, you have a `GregorianCalendar`, not a `Date` → compile error (incompatible type).

**Where it comes back:** in ch. 09, `fillForm` will format `existing.getRelease()` with `SimpleDateFormat("dd/MM/yyyy")`. If `release` is `null` (a movie created with the empty constructor and no setRelease), you'll get an NPE. That's why your local sync version adds an `if (existing.getRelease() != null)`.

</details>

---

## Step 4.6 — `EdgeToEdge` and insets

### Why

From Android 15, apps are displayed **edge-to-edge** by default: the content extends under the status bar and under the navigation bar. Pretty, but the text at the top overlaps the clock.

The solution: apply **padding** equal to the height of the system bars.

### How

```java
EdgeToEdge.enable(this);
setContentView(R.layout.activity_main);
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
    return insets;
});
```

### Line by line

| Line | What it does |
|---|---|
| `EdgeToEdge.enable(this)` | allows drawing under the system bars |
| `findViewById(R.id.main)` | the root of the layout — that's why it has `android:id="@+id/main"` |
| `insets.getInsets(Type.systemBars())` | the bar heights (status at the top, navigation at the bottom, possibly sides) |
| `v.setPadding(...)` | pushes the content inside the safe area |
| `return insets` | lets the insets keep flowing (if you don't consume them) |

### Why `ViewCompat` and not directly

`ViewCompat.setOnApplyWindowInsetsListener` is the variant compatible with all Android versions. The native API (`View.setOnApplyWindowInsetsListener`) has different signatures across versions.

### Why it's applied to `R.id.main`

Because `main` is the **root** (`FrameLayout`). If you applied padding to the `ListView`, the FAB would stay under the navigation bar. Applying it to the root pushes **all** children inside.

### Exercise 4.6

**Requirement:** remove the `ViewCompat.setOnApplyWindowInsetsListener(...)` block. Run it. What happens to the text in the list and to the FAB?

<details>
<summary>Solution — explained</summary>

**What was done:** we removed the insets listener, keeping `EdgeToEdge.enable(this)`.

**What you see:** the first row of the list goes **under the status bar** (the clock and battery overlap "Inception"). The FAB goes **under the navigation bar** (the gesture buttons partly cover it).

**Why:** `EdgeToEdge.enable()` tells the system "let me draw under the bars". Without compensating padding, the content really does end up under them.

**Remember:**
1. `EdgeToEdge` + insets = a pair. One without the other gives overlaps.
2. The padding is applied to the **root**, not to the children.
3. `return insets` (not `WindowInsetsCompat.CONSUMED`) lets the insets keep flowing — if you had a `BottomNavigationView`, it would need them.

**Where it comes back:** `ItemActivity` does exactly the same thing, but on `R.id.main` from `activity_item.xml` — which is a `ScrollView`. The difference: there the `ScrollView` has `android:fillViewport="true"`, so the padding applies to the scrollable content. You'll see it works the same.

</details>

---

## Step 4.7 — Empty `initListeners` (for now)

### Why

In the repo, `initListeners()` contains two listeners:

```java
fabInsert.setOnClickListener(...)   // opens ItemActivity
listView.setOnItemClickListener(...) // opens ItemActivity with the movie
```

But both use `launcher`, which is initialized **after** `initListeners()` in `onCreate`. So in this chapter, `initListeners()` is empty — you fill it in ch. 08.

### How

```java
private void initListeners() {
    // filled in chapter 08
}
```

### Why not write it completely from the start

Because `launcher` would be `null` when you press the button → NPE. The order in the repo is:

```java
initControls();
initListeners();     // ← here launcher is still null!
launcher = registerForActivityResult(...);
```

> **Careful:** this is a **real trap in the repo code**. `initListeners` registers listeners that **capture** the `launcher` field — but the listener doesn't run at registration, it runs at click. At click time, `launcher` is already initialized. So it works **by accident**, thanks to deferred execution.
>
> If you called `fabInsert.performClick()` right after `initListeners()`, you'd get an NPE. It's a lesson about **initialization order vs. execution time**.

---

## Step 4.8 — Verification

### How

1. Run the app.
2. You see 3 rows in the list.
3. The text of each row looks like `Movie{title='Inception', release=..., ...}` — long, ugly, but complete.
4. The FAB is visible bottom-right. If you press it, **nothing happens** (empty listener).

### What to check in the code

- [ ] `movies` is a `final List<Movie>` initialized with `new ArrayList<>()`
- [ ] `onCreate` calls in order: `super`, `EdgeToEdge`, `setContentView`, insets, `addSampleMovies`, `new ArrayAdapter`, `initControls`, `initListeners`
- [ ] `initControls` does `findViewById` + `listView.setAdapter(movieAdapter)`
- [ ] `addSampleMovies` adds 3 movies with `GregorianCalendar`
- [ ] `initListeners` is empty

---

## Step 4.9 — Reflection exercise

**Requirement:** why `List<Movie>` and not `ArrayList<Movie>` as the field type?

<details>
<summary>Answer — explained</summary>

**What was done:** the field is declared `private final List<Movie> movies = new ArrayList<>();`.

**Why `List` and not `ArrayList`:** `List` is the **interface**, `ArrayList` is an **implementation**. By declaring the type as the interface, you can swap the implementation at any time (`LinkedList`, `CopyOnWriteArrayList`) without touching the rest of the code. The code that uses `movies` only knows it's an ordered list with `add`, `get`, `set`, `size` — it doesn't care how it's implemented.

**Remember:**
1. **Program to the interface, not to the implementation.** It's a SOLID principle (Dependency Inversion).
2. `new ArrayList<>()` with the diamond operator — the compiler infers `<Movie>` from the field type.
3. `final` + interface = fixed reference, mutable contents.

**Where it comes back:** in ch. 11, `MovieAdapter` receives `List<Movie> movies` in its constructor — again an interface. If it received `ArrayList`, it would be needlessly restrictive.

</details>

---

## Step 4.10 — Synthesis: `MainActivity` at this stage

```java
package ro.ase.ie.g1097.activities;

import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.List;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MainActivity extends AppCompatActivity {

    private FloatingActionButton fabInsert;
    private ListView listView;
    private final List<Movie> movies = new ArrayList<>();
    private ArrayAdapter<Movie> movieAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        addSampleMovies();

        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
        initControls();
        initListeners();
    }

    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        listView = findViewById(R.id.listView);
        listView.setAdapter(movieAdapter);
    }

    private void initListeners() {
        // chapter 08
    }

    private void addSampleMovies() {
        // the 3 movies
    }
}
```

### Test questions

1. Why does `ArrayAdapter` need `this`?
2. What happens if you forget `listView.setAdapter(movieAdapter)`?
3. Why is `Calendar.JULY` 6?
4. Why are the insets applied to `R.id.main`?
5. What does `final` do to `movies`?

<details>
<summary>Answers — explained</summary>

**1. Why does `ArrayAdapter` need `this`?**
The first parameter is `Context`. The adapter needs it to **create views** (`LayoutInflater.from(context)`) and to access resources. `Activity` **is** a `Context`.

**2. What happens if you forget `setAdapter`?**
The `ListView` keeps the adapter from `android:entries` (Item 1..20) or, if you removed `entries`, it's empty. The movies are in `movies` but aren't displayed anywhere. **No error** — just an empty list. It's a silent bug, hard to catch.

**3. Why is `Calendar.JULY` 6?**
`Calendar` indexes months from 0 (`JANUARY = 0`). It's a historical decision from Java 1.1, kept for compatibility. Use the **constants**, never numbers.

**4. Why insets on `R.id.main`?**
`main` is the root of the tree. Padding on the root pushes **all** children into the safe area. On a single child, the others would stay under the bars.

**5. What does `final` do to `movies`?**
It prevents **reassigning** the reference (`movies = ...` doesn't compile). The contents stay mutable (`add`, `set`, `clear` work). It's a guarantee that the list is the same for the whole lifetime of the activity.

</details>

---

## Chapter 04 summary

- `onCreate`: `super` → `EdgeToEdge` → `setContentView` → insets → data → adapter → controls → listeners.
- `ArrayAdapter` + `ListView` = a push model; `notifyDataSetChanged()` mandatory after changes.
- `findViewById` after `setContentView`, otherwise `null`.
- `GregorianCalendar` with `Calendar.MONTH` (0-indexed) + `.getTime()`.
- Insets on the root, with `ViewCompat`.

**Next chapter:** [05 - The form - part 1.md](05%20-%20The%20form%20-%20part%201.md)
