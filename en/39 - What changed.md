# Chapter 39 — What changed compared to the old version

**Objective:** to understand exactly what changed between the `ListView` application from chapter 22 and version 2 with `RecyclerView`, what stayed untouched and — most importantly — what that means for what you can be asked at the test.

**What we compare:** two snapshots of the same application, at two different moments.

| | The old version | Version 2 |
|---|---|---|
| Location | `D:\tmp\claude\site-build\stage\src\G1098\src\main\` | `D:\tmp\claude\dma-annot\src-v2\` |
| Base package | `ro.ase.ie.g1098` | `com.example.group1098` |
| List | `ListView` + `ArrayAdapter<Movie>` | `RecyclerView` + `MovieAdapter` |
| Row click | `setOnItemClickListener` | `IMovieListener` interface |
| Screens | 2 (`MainActivity`, `ItemActivity`) | 3 (+ `PlaceCiocanul`) |
| Files in the comparison | 6 (3 Java + 2 XML + manifest) | 11 |

**Why the comparison matters.** At the exam, the requirement "replace `ListView` with `RecyclerView`" **is no longer given from scratch** — the code you receive already has the migration done. What is given is the change on top of it: another `LayoutManager`, another row, another click, a correct notification. And if you do not know exactly what changed compared to the version from chapter 22, you risk looking in the code for a structure that no longer exists (a `listView`, an `ArrayAdapter`, a `setOnItemClickListener`) and losing precious minutes.

**How we compared, so you can redo the check yourself.** We took the old files, replaced only the `package` line (and, in `ItemActivity`, the two `ro.ase.ie.*` imports), then ran a line-by-line `diff`. The result is in 39.5: three files come out identical, the rest differ a lot. For the numbers in the chapter we counted the lines of each file separately.

> **The rule of the chapter:** every statement here is verifiable in the 11 files in `src-v2` or in the four in the old version. Where a statement comes from somewhere else (framework behaviour, chapter 23), I say so explicitly. Nothing is written from memory.

**The map of the chapter:**

| Section | What it covers | Level |
|---|---|---|
| 39.1 | the list XML and the three lines in `MainActivity` | layout + binding |
| 39.2 | the adapter, the contract of the three methods, recycling | architecture |
| 39.3 | the click chain, from the card down to the `launcher` | events |
| 39.4 | the new `PlaceCiocanul` screen and the bug in it | new code |
| 39.5 | the three identical files and what 60% means | inventory |
| 39.6 | what is lame in the new code, with repairs | quality |
| 39.7 | what is asked at the exam and where you look | strategy |

---

## 39.1 The list: `ListView` → `RecyclerView`

This is the only change you can see with the naked eye in the XML. And it is smaller than it looks: one tag, one ID and one attribute that disappears.

**Old** — `activity_main.xml`, the version with `ListView`:

```xml
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />
```

**New** — `activity_main.xml`, version 2:

```xml
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvMovies"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
```

Three differences, each with its explanation.

| Aspect | Old | New | Why |
|---|---|---|---|
| Tag | `<ListView>` | `<androidx.recyclerview.widget.RecyclerView>` | `RecyclerView` is not a framework class |
| ID | `@+id/listView` | `@+id/rvMovies` | `findViewById` looks for another name; `R.id.listView` disappears |
| Declarative content | `android:entries="@array/items"` | — (the attribute does not exist) | `RecyclerView` does not build its own adapter |
| `FrameLayout` children | 2 | 3 | the second FAB appeared (`btnVlad`) |

### Difference 1 — the tag: why the full class name

`<ListView>` works without a prefix because it is a framework widget: `LayoutInflater` has a shortcut that tries `android.widget.ListView` automatically, then `android.webkit.ListView` etc. `RecyclerView` **does not live in `android.widget`** — it comes from the `androidx.recyclerview` library, with its own package. To be able to instantiate it, the inflater needs the fully qualified class name, exactly as you write it in the `import`.

If you write `<RecyclerView ... />`, the inflate finds no class with that name and throws an exception at `setContentView`. Hence the rule you see in any AndroidX project: library widgets are written with the full name in XML (`androidx.recyclerview.widget.RecyclerView`, `com.google.android.material.card.MaterialCardView`), framework ones with the short name (`ListView`, `FrameLayout`, `TextView`).

### Difference 2 — the ID: it is not just a rename

`@+id/listView` → `@+id/rvMovies`. The `rv` prefix is the convention for `RecyclerView`, like `tv` for `TextView` or `btn` for `Button`. It matters for reading the code, not for how it works.

But the change has a consequence that the compiler catches immediately: `R.id.listView` **no longer exists** in the generated `R` class. Any `findViewById(R.id.listView)` left in the code does not compile — `cannot find symbol` error. It is one of the few cases where a layout change is signalled by the compiler, not by a crash at runtime. Use this: if you changed the XML and the project still compiles, you still have an `R.id.listView` somewhere to clean up.

### Difference 3 — `android:entries` disappears

`android:entries` was an attribute of `AbsListView`: you gave it a `string-array` from `strings.xml` and the widget built itself an internal `ArrayAdapter`. In the old version, the array had 20 entries:

```xml
    <string-array name="items">
        <item>Item 1</item>
        <item>Item 2</item>
        <!-- ... up to ... -->
        <item>Item 20</item>
    </string-array>
```

A detail worth emphasising, because it is a reading trap: **those 20 rows were never visible on screen**. `MainActivity.initControls()` called `listView.setAdapter(movieAdapter)` immediately after `setContentView`, and `setAdapter` replaces the adapter built from `entries`. So `android:entries="@array/items"` was decorative — a leftover from the first lab, when the list displayed "Item 1…Item 20" and had no model.

`RecyclerView` has no equivalent attribute. The content comes **exclusively** from the adapter set in code. This has two practical consequences:

- if you forget `setAdapter(...)`, the list is empty, with no error;
- if you forget `setLayoutManager(...)`, the list is empty, with no error — and with no warning at all in Logcat (chapter 23, exercise 23.10, the first hint).

### What happens in `MainActivity`

Here you see the second half of the migration. Old:

```java
    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        listView = findViewById(R.id.listView);
        listView.setAdapter(movieAdapter);
    }
```

New:

```java
    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        // listView = findViewById(R.id.listView);
        // listView.setAdapter(movieAdapter);
        rvMovies = findViewById(R.id.rvMovies);
        rvMovies.setLayoutManager(new LinearLayoutManager(this));
        rvMovies.setAdapter(movieAdapter);
        btnVlad = findViewById(R.id.btnVlad);
    }
```

Line by line: `findViewById(R.id.listView)` becomes `findViewById(R.id.rvMovies)`, `setAdapter` stays `setAdapter`, and between them a line appears with no counterpart in the old version — `setLayoutManager`.

The new line has a single role: to say where and how the rows are laid out. `new LinearLayoutManager(this)` means "a vertical column, one row under another". The alternatives you can get at the exam:

| Requirement | The object |
|---|---|
| vertical list (default) | `new LinearLayoutManager(this)` |
| horizontal list | `new LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)` |
| two-column grid | `new GridLayoutManager(this, 2)` |
| grid with different heights | `new StaggeredGridLayoutManager(2, StaggeredGridLayoutManager.VERTICAL)` |

`RecyclerView` has no preference of its own: without a `LayoutManager` it draws nothing. That is why this line is mandatory, not optional.

### The tree, old and new

```
OLD — activity_main.xml                  NEW — activity_main.xml
FrameLayout (id=main)                    FrameLayout (id=main)
│  orientation="horizontal"              │  orientation="horizontal"
│  (ignored by FrameLayout)              │  (ignored, still there)
│                                        │
├── ListView (id=listView)               ├── RecyclerView (id=rvMovies)
│     entries=@array/items               │     (no entries, no layoutManager
│     adapter: ArrayAdapter<Movie>       │      in XML — both in code)
│     row: simple_list_item_1            │     adapter: MovieAdapter
│                                        │     row: movie_item.xml
│                                        │
└── FAB (id=floatingActionButton)        ├── FAB (id=floatingActionButton)
      bottom|end → ItemActivity          │     bottom|end → ItemActivity
                                         │
      (2 children)                       └── FAB (id=btnVlad)
                                               bottom|start → PlaceCiocanul
                                         (3 children)
```

At runtime, each row of the `RecyclerView` is a tree of its own, built from `movie_item.xml`: a `MaterialCardView` that contains a `LinearLayout`, an `ImageView` and another `LinearLayout` with title, subtitle, rating, facts and four chips. About what gets filled from it and what stays static — 39.2 and 39.6.

A preview detail, not a runtime one: the new XML does not have `tools:listitem="@layout/movie_item"`, so in Android Studio the `RecyclerView` shows up as an empty rectangle. The attribute is `tools:`, so it disappears at build time and changes nothing in the application.

---

## 39.2 The adapter: `ArrayAdapter` → `MovieAdapter`

If 39.1 was the surface change, here is the substantial change. In the old version the adapter was **one line**; in version 2 it is **a whole file**, plus an interface.

**Old** — the field and the construction:

```java
    private ArrayAdapter<Movie> movieAdapter;
    // ...
    private final List<Movie> movies = new ArrayList<>();
    // ...
    movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

**New** — the same three places:

```java
    private MovieAdapter movieAdapter;
    // ...
    private final ArrayList<Movie> movies = new ArrayList<>();
    // ...
    movieAdapter = new MovieAdapter(movies, this);
```

Three immediate observations, all visible in the diff:

- The type of the field changes from `ArrayAdapter<Movie>` to `MovieAdapter` — your class, not a framework one.
- The type of the list changes from `List<Movie>` to `ArrayList<Movie>`, because **that is what the constructor requires** of `MovieAdapter` (`public MovieAdapter(ArrayList<Movie> movies, IMovieListener listener)`). It is not a style preference; if you leave `List<Movie>`, it does not compile.
- The second argument is no longer a layout, but `this` — the activity itself, in the role of listener. About that, 39.3.

The old line stays in the file, commented out:

```java
        // movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

### Why `ArrayAdapter` has no business here any more

`ArrayAdapter` is a **ready-made** adapter, built for a single case: a list of objects displayed as text. It receives three things at construction — a `Context`, a row layout ID and the data list — and knows how to do the rest by itself. The price is that it knows **a single kind of row**.

Three concrete reasons, in the order in which they hit you:

**1. The row has a single `TextView`.** `android.R.layout.simple_list_item_1` is a layout that comes with Android (hence `android.R`, not `R`) and contains exactly one `TextView`, with the ID `android.R.id.text1`. `ArrayAdapter` fills that single `TextView`. `movie_item.xml` does not have a root `TextView`: the root is a `MaterialCardView`, and inside it there are 10 widgets with their own IDs. `ArrayAdapter` has no mechanism through which to put a value into `movieRating` or into `chipWatched`.

**2. The only value it knows how to display is `toString()`.** `ArrayAdapter` does not ask you "what field do you want"; it takes the object and calls its `toString()`. And `Movie.toString()` in the project is the full dump:

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
                ", posterUrl='" + posterUrl + '\'' +
                '}';
    }
```

With `simple_list_item_1` + `toString()` (the pair from the table at the beginning of chapter 23), the old row displayed exactly this string — all 10 fields, on a single row, braces and all. It was not a list of movies, it was a list of `toString()`s.

**3. There is no position contract.** `ArrayAdapter` exposes `getView(position, convertView, parent)`, where recycling is done manually, through `convertView`. `RecyclerView` asks for another triad of methods and other types. You cannot "adapt" an `ArrayAdapter` to `RecyclerView` without replacing it completely.

### The contract of the three methods

`MovieAdapter` extends `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`. The base class has three abstract methods; if you do not write all three, the class does not compile. Here they are, with who calls them and when:

| Method | Who calls it | When | How many times | What it must do |
|---|---|---|---|---|
| `onCreateViewHolder(parent, viewType)` | `RecyclerView` | when it needs a new row, that is at the start and when recycling is no longer enough | once per "physical" row (the ones that fit on screen + a few spare) | to inflate `movie_item.xml` and return a new `MovieViewHolder` |
| `onBindViewHolder(holder, position)` | `RecyclerView` | before every display of a row | every time the row appears on screen, **including** when the same `ViewHolder` is reused for another movie | to write the data from `movies.get(position)` into the widgets in `holder` |
| `getItemCount()` | `RecyclerView` | at startup and after every notification | often | to return the number of elements, that is `movies.size()` |

The real code from `MovieAdapter.java`:

```java
    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy");
        Movie movie = movies.get(position);
        holder.title.setText(movie.getTitle());
        holder.subtitle.setText(movie.getGenre().toString() + ". " + sdf.format(movie.getRelease()));

    }

    @Override
    public int getItemCount() {
        return movies.size();
    }
```

Read them in the order in which `RecyclerView` calls them, not in the order from the file: first `getItemCount()` (how many rows there are), then `onCreateViewHolder` for each row it needs, then `onBindViewHolder` for each row it is about to show.

### The recycling mechanism, in one picture

```
RecyclerView (with LinearLayoutManager)
│
├─ 1. "how many elements?"         → getItemCount()            → 3
│
├─ 2. "I need rows"                → onCreateViewHolder() × 4  → 4 × inflate(movie_item)
│        (as many as fit on screen + 1-2 in reserve)
│
├─ 3. "fill the rows"              → onBindViewHolder(holder, 0..3)
│        holder.title    ← movies.get(0).getTitle()
│        holder.subtitle ← movies.get(0).getGenre() + the year
│
├─ 4. scrolling: row 0 goes off screen
│        its ViewHolder is NOT thrown away — it goes into the recycling pool
│
└─ 5. scrolling: row 4 must be displayed
         → onCreateViewHolder is NOT called
         → onBindViewHolder is called (the same holder, 4)
         → the same widgets, other content
```

Step 5 is the whole point of `ViewHolder`: `findViewById` is done **once**, in the `ViewHolder` constructor, not on every scroll. For a list of 1000 movies, the `RecyclerView` version does `findViewById` a few times; an adapter that looked up the widgets in `onBindViewHolder` would do it thousands of times. Hence the rule: `findViewById` sits in the `ViewHolder` constructor, writing the values sits in `onBindViewHolder`.

### The comparison table

| Aspect | `ArrayAdapter<Movie>` (old) | `MovieAdapter` (new) |
|---|---|---|
| Who holds the rows | `ArrayAdapter`, with the list received at construction | `MovieAdapter`, with the reference `final ArrayList<Movie> movies` |
| Who fills the row | `ArrayAdapter`, with `toString()` | `onBindViewHolder`, field by field |
| The row layout | `android.R.layout.simple_list_item_1` (a `TextView`) | `R.layout.movie_item` (`MaterialCardView`, 10 widgets) |
| Recycling | `convertView` + `if (convertView == null) inflate` | `ViewHolder` recycled by `RecyclerView` |
| Mandatory methods | none — it is ready-made | three: `onCreateViewHolder`, `onBindViewHolder`, `getItemCount` |
| Who knows the position | the `position` parameter from `getView` | the `position` parameter from `onBindViewHolder` |
| Click | on the list, in the activity | on the row, in the adapter (39.3) |
| Notification | `notifyDataSetChanged()` | `notifyDataSetChanged()` or `notifyItem*` |

### Three details in the code worth seeing

**1. The adapter does not copy the list.** The constructor does `this.movies = movies;` — the same reference that `MainActivity` holds. That is why `movies.add(movie)` from the callback shows up in the list after `notifyDataSetChanged()`: nothing is synchronised, it is the same object. `getItemCount()` already returns the updated `movies.size()`; the notification is what tells `RecyclerView` to ask again.

**2. `MovieViewHolder` is a non-static inner class.** In chapter 12 the rule was "`ViewHolder` is made `static`". Here it is `class MovieViewHolder extends RecyclerView.ViewHolder` — without `static`, because it needs `movies` and `listener` from the outer instance and sees them directly. The `static` variant would have required both to be passed as parameters. Both are correct; the first is shorter, the second more explicit.

**3. The adapter's fields are package-private.** `final ArrayList<Movie> movies;` and `final IMovieListener listener;` have no `private`. It is not an oversight, but neither is it a great decision: the inner class would have seen them anyway, and without a modifier they become visible to the whole `com.example.group1098.adapter` package. `private` would have been enough and safer.

**What still uses the old path.** `MainActivity` keeps `movieAdapter.notifyDataSetChanged()` in both branches of the callback. It works — `RecyclerView` has the method too — but it loses the insertion animation and re-binds all the visible rows. The modern variant is exercise 23.10 from chapter 23.

---

## 39.3 The click: `setOnItemClickListener` → `IMovieListener` interface

Here is the least intuitive difference for someone coming from `ListView`, because it is not an API change, but an **architecture** change.

**Old** — the click sat on the list, in a single piece, in `initListeners()`:

```java
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);
                intent.putExtra(MOVIE_EXTRA, movies.get(position));
                intent.putExtra(POSITION_EXTRA, position);
                launcher.launch(intent);
            }
        });
```

**New** — the same code exists, but commented out:

```java
        /* listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);
                intent.putExtra(MOVIE_EXTRA, movies.get(position));
                intent.putExtra(POSITION_EXTRA, position);
                launcher.launch(intent);
            }
        });*/
```

The click itself moved to two places: into the adapter (which catches the event) and into a method of the activity (which does the navigation). Between them sits a 7-line interface.

### The interface

New file, `IMovieListener.java`, in full:

```java
package com.example.group1098.adapter;

import com.example.group1098.model.Movie;

public interface IMovieListener {
    void onMovieClick(Movie movie, int position);
}
```

A single method, two arguments: the object that was clicked and its position. That is all.

### Who implements it

`MainActivity` changes its class declaration:

```java
public class MainActivity extends AppCompatActivity implements IMovieListener {
```

and receives the method at the end of the file:

```java
    @Override
    public void onMovieClick(Movie movie, int position) {
        Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }
```

The body is identical to the one from the old listener, with a single difference in form: `ItemActivity.class` has become the full name `com.example.group1098.activities.ItemActivity.class`. `MainActivity` no longer has `ItemActivity` in its imports, so it needs the qualified name.

And the adapter receives the activity as listener, in the very construction line:

```java
        movieAdapter = new MovieAdapter(movies, this);
```

`this` is `MainActivity`, which has just promised through `implements` that it knows `onMovieClick`.

### The complete chain

```
 1. the user touches the card
          │
          ▼
 2. itemView.setOnClickListener           ← in the MovieViewHolder constructor
    (MovieAdapter.java)
          │  onClick(View v)
          ▼
 3. int pos = getAbsoluteAdapterPosition();
    if (pos != RecyclerView.NO_POSITION) {
        Movie movie = movies.get(pos);
        listener.onMovieClick(movie, pos);   ← the call through the interface
    }
          │
          ▼
 4. IMovieListener.onMovieClick(Movie, int)  ← the contract (separate file)
          │
          ▼
 5. MainActivity.onMovieClick(...)          ← the implementation
        Intent intent = new Intent(...)
        intent.putExtra(MOVIE_EXTRA, ...)
        intent.putExtra(POSITION_EXTRA, ...)
        launcher.launch(intent)
          │
          ▼
 6. ItemActivity (the form, just as before)
```

The code of link 2–3, exactly as it is in the file:

```java
            itemView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    int pos = getAbsoluteAdapterPosition();
                    if (pos != RecyclerView.NO_POSITION) {
                        Movie movie = movies.get(pos);
                        listener.onMovieClick(movie, pos);
                    }
                }
            });
```

### Why `RecyclerView` has no `setOnItemClickListener`

Because it would make no sense to have one. A `RecyclerView` row can contain any number of interactive areas — a card, a chip, a delete button, a poster. A single listener on the list would have had to guess what exactly was touched. The solution chosen by AndroidX: each row puts its own listeners on its own areas, and whoever wants to find out the result receives it through a callback that they define.

Hence one more practical consequence: **the adapter does not know what happens with the click**. `MovieAdapter` does not import `Intent`, does not import `ItemActivity`, does not know `MainActivity`. It only knows that there is someone who promised `onMovieClick(Movie, int)`. You can change the destination of the click without touching the adapter.

### The table of the two mechanisms

| | Old (`ListView`) | New (`RecyclerView`) |
|---|---|---|
| Where it is registered | `listView.setOnItemClickListener(...)` | `itemView.setOnClickListener(...)` in the `ViewHolder` |
| Who holds the listener | the list widget | each row, individually |
| The callback type | `AdapterView.OnItemClickListener` (framework) | `IMovieListener` (yours) |
| The signature | `onItemClick(parent, view, position, id)` | `onMovieClick(Movie, int)` |
| What you receive | the position and the id of the row | the whole object and the position |
| Who implements it | an anonymous class, in the activity | the activity itself |
| Where the navigation code sits | in `initListeners()` | in `onMovieClick(...)`, a public method |

### Four nuances you can see in the code

**1. The position is computed at click time, not at binding time.** `getAbsoluteAdapterPosition()` is evaluated at the moment of the touch. If you had captured `position` in the `ViewHolder` constructor or in `onBindViewHolder`, after the first recycling you would have opened the wrong movie — exactly the trap from chapter 23, exercise 23.9.

**2. `getAbsoluteAdapterPosition()` vs `getBindingAdapterPosition()`.** Version 2 uses the first form; chapter 23 uses the second. For a single adapter attached to the `RecyclerView`, the result is identical. The difference appears with `ConcatAdapter`: the absolute position is in the full list, the "binding" one is in the adapter that produced the row.

**3. The listener is bound in the `ViewHolder` constructor, not in `bind`.** Both variants are correct, as long as the position is resolved at click time. Here binding in the constructor is done once per row, not on every re-bind; in chapter 23 binding in `bind` is chosen for readability, because `bind` already receives `movie` and `listener`.

**4. There is no `null` check on the listener.** `MovieAdapter` assumes it received a valid listener. `new MovieAdapter(movies, null)` compiles, and the first click throws `NullPointerException`. The variant from chapter 23 checks `listener != null`; it is a difference of robustness, not of behaviour.

**A detail to read carefully:** the method `onMovieClick(Movie movie, int position)` receives the movie, but does not use it — it writes `movies.get(position)` in `putExtra`. It works, because both come from the same list and the same position. But if the adapter ever received a filtered or sorted list, the two would diverge, and the code would open a different movie than the one touched. The correct form would be `intent.putExtra(MOVIE_EXTRA, movie);`. It is the kind of duplication that an exam with "explain what this line does" can expose.

---

## 39.4 The new screen: `PlaceCiocanul`

The third structural difference compared to the old version has nothing to do with the list: it is a screen that simply **did not exist**. In the old version, the manifest declared two activities; in version 2, three.

### What it is

A test screen. It has no list, no form, it saves nothing: it has a background, a button and a short message. The name ("put the hammer") and the message text show that it was written as a quick check — a place where you tap and immediately see whether the link between the second button on the main screen and a second activity works.

The whole file, 42 lines:

```java
package com.example.group1098.activities;

import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.group1098.R;
import com.google.android.material.floatingactionbutton.FloatingActionButton;


public class PlaceCiocanul extends AppCompatActivity {

    private FloatingActionButton btn2;
    private String string;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WindowCompat.enableEdgeToEdge(getWindow());
        setContentView(R.layout.activity_place_ciocanul);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        btn2 = findViewById(R.id.floatingActionButton2);

        btn2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(PlaceCiocanul.this, "Caca", Toast.LENGTH_LONG).show();
            }
        });

        string = String.valueOf(R.string.app_name);
    }
}
```

### What it does

Three things, in the order from `onCreate`:

1. **Enables edge-to-edge** and applies the padding for the system bars — exactly like `MainActivity` and `ItemActivity`, only with another entry method (see below).
2. **Binds the button** `floatingActionButton2` to a `Toast` that displays the text `"Caca"` for `Toast.LENGTH_LONG` (3.5 seconds).
3. **Assigns a field** `string` the result of `String.valueOf(R.string.app_name)`. The field is not read anywhere.

The layout, in short: a `RelativeLayout` with the id `main` (which the insets listener needs), a `RecyclerView` without an id, a `FloatingActionButton` with the id `floatingActionButton2` and a `ProgressBar` 6dp wide. What does not work in it — 39.6.

### How you get to it

Two pieces: a second FAB in `activity_main.xml` and a listener in `MainActivity`.

The button, added as the third child of the `FrameLayout`:

```xml
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/btnVlad"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:clickable="true"
        android:layout_margin="16dp"
        android:contentDescription="Ciocan"
        android:layout_gravity="bottom|start"
        app:srcCompat="@drawable/buton_ciocan"/>
```

`bottom|start` puts it in the corner opposite the add FAB, which has `bottom|end`. The icon comes from `@drawable/buton_ciocan` — a file that does not exist in the old version nor in `cod-final`; it must be added to the project, otherwise the build fails on resources.

The link, in a separate method:

```java
    private void initSecondListener() {
        btnVlad.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent2 = new Intent(MainActivity.this, com.example.group1098.activities.PlaceCiocanul.class);
                launcher.launch(intent2);
            }
        });
    }
```

Called in `onCreate`, immediately after `initListeners()`:

```java
        movieAdapter = new MovieAdapter(movies, this);
        initControls();
        initListeners();
        initSecondListener();
```

The order matters: `btnVlad` is found in `initControls()`, and `initSecondListener()` needs it. If you reversed the two, `btnVlad` would be `null` and you would get a `NullPointerException` at `setOnClickListener`.

In the manifest, the third activity:

```xml
        <activity
            android:name=".activities.PlaceCiocanul"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
```

`exported="false"` is correct: the screen is opened only from the application, not from outside. `windowSoftInputMode="adjustResize"` is useless here — the screen has no text field at all — but it was copied after the other two entries.

### The alarm signal: `String.valueOf(R.string.app_name)`

The line at the end of `onCreate` is the only place in the entire code of version 2 that is **wrong**, not just unfinished.

```java
        string = String.valueOf(R.string.app_name);
```

`R.string.app_name` **is not a piece of text**. It is an `int` field generated by AAPT, which holds the numeric ID of the resource — something of the form `2131689600`. `String.valueOf` has an overload for `int`, so the result is the string of digits of the ID, not the name of the application.

```java
// what the line does
String.valueOf(R.string.app_name)   →  "2131689600"     // the ID, as text

// what it should do
getString(R.string.app_name)        →  "G1098"          // the resource text
```

The difference between `R.string.x` and `getString(R.string.x)` is exactly the difference between "the number at the till" and "the product". `R.string.app_name` is the key; `getString(...)` is the method that returns the value from `strings.xml`, formatting included if the resource has parameters.

In practice, the bug has no visible effect: the field `string` is not used anywhere. It is a line that does nothing bad and nothing good — but it is exactly the kind of line that a test with "what does it display?" can turn into lost marks.

### A style inconsistency: two APIs for the same thing

`MainActivity` and `ItemActivity` start edge-to-edge with `EdgeToEdge.enable(this)` (from `androidx.activity`); `PlaceCiocanul` starts with `WindowCompat.enableEdgeToEdge(getWindow())` (from `androidx.core`). Both do the same thing — they allow drawing under the system bars. It is not an error, it is a style inconsistency, visible in the `import`s.

### What happens with the result

`PlaceCiocanul` is launched with the **same** `launcher` as `ItemActivity`. On return the same `onActivityResult` callback runs, but since the screen never calls `setResult`, the returned code is `RESULT_CANCELED` and the `if (o.getResultCode() == RESULT_OK)` branch does not run. The list stays untouched — functionally correct, but the test screen is tied to the result mechanism of the form without needing it.

### Its place in the application tree

```
MainActivity (launcher)
├── FAB "add"    (floatingActionButton, bottom|end)   → ItemActivity   (carries/returns Movie)
└── FAB "hammer" (btnVlad, bottom|start)              → PlaceCiocanul  (carries nothing, returns nothing)
                                                              │
                                            FAB floatingActionButton2 → Toast
                                            RecyclerView without id   → empty
                                            ProgressBar 6dp           → decoration
```

Three screens, two links, a single real data flow (the one towards `ItemActivity`). `PlaceCiocanul` is an intentional dead end.

---

## 39.5 What stayed identical

Here is the part that matters most for the exam, and it is the one you see least.

### The three files

| File | Lines | What differs from the old version |
|---|---|---|
| `Movie.java` | 130 | only the `package` line |
| `ItemActivity.java` | 217 | the `package` line + the two `ro.ase.ie.*` imports |
| `activity_item.xml` | 451 | nothing — text identical character by character |
| **Total** | **798** | |

The check, so you can redo it: we replaced in the old file `package ro.ase.ie.g1098.model;` with `package com.example.group1098.model;` and compared with `diff`. The result: zero differences. In `ItemActivity`, same thing, after also replacing `import ro.ase.ie.g1098.R;` with `import com.example.group1098.R;` and `import ro.ase.ie.g1098.model.Movie;` with the `com.example.group1098.*` variant.

A point of honesty: the old files have CRLF line terminators, the new ones have LF in some cases. The difference is invisible in the editor and changes no character in the code. The text itself is identical — with the exception of the package line, which is the only real change.

### What the number means

```
Total lines in the 11 files in src-v2 .............. 1,350
of which manifest ..................................    33
code + layout (the base of the percentages) ........ 1,317

Identical to the old version .......................   798   (60.6% of 1,317)
Changed or new .....................................   519   (39.4% of 1,317)
```

Roughly **60% of the application was not touched**. And it is not just any part: these are exactly the three files that define the exam.

| File | What it contains | The chapters that cover it |
|---|---|---|
| `Movie.java` | 10 fields, a constructor with 10 parameters, an empty constructor, 20 getters/setters, `toString()` | 02, 22.1, 17, 33 |
| `ItemActivity.java` | reading the 10 fields from the form, `fillForm`, `saveMovie`, `DatePickerDialog` | 07, 09, 22.3 |
| `activity_item.xml` | 4 Material cards: Basics, Details, Approval, Poster; all 10 controls | 05, 06, 20, 22.5 |

What that means concretely: **any requirement that touches the model or the form is solved with the code you already knew**. You add a field in `Movie` — the same three places (field, constructor, getter/setter). You add a control in the form — the same `findViewById`, the same reading in `saveMovie`, the same writing in `fillForm`. No recipe from chapters 33–35 changed because of `RecyclerView`, as long as the requirement does not touch the list.

### What actually changed in `MainActivity`

Even in the file that changed the most, half is the same. Verified by comparing block by block:

| Block | State |
|---|---|
| `POSITION_EXTRA`, `MOVIE_EXTRA` | identical |
| `addSampleMovies()` — the three sample movies | identical, line by line |
| The `launcher` callback (`onActivityResult`) | identical |
| `fabInsert.setOnClickListener` | identical, except `ItemActivity.class` written with the full name |
| The fields | `ListView` → `RecyclerView`, `ArrayAdapter` → `MovieAdapter`, `List` → `ArrayList`, plus `btnVlad` |
| `initControls()` | + `setLayoutManager`, + `btnVlad` |
| `initListeners()` | the list listener removed (commented out) |
| `onMovieClick(...)` | new method, the body of the old listener |

So `MainActivity` is not "rewritten" either: it has three real changes (the types, `initControls`, the click) and two additions (the second FAB, the new method).

### What is no longer the same, although it does not look it

Three small things, which have nothing to do with the list:

1. **The base package**: `ro.ase.ie.g1098` → `com.example.group1098`. All the `ro.ase.ie...R` imports become `com.example.group1098.R`.
2. **The theme in the manifest**: `@style/Theme.G1098` → `@style/Theme.Group1098`. If the name does not exist in `themes.xml`, the application does not start.
3. **New resources**: `@string/chip_ciocan_name` and `@drawable/buton_ciocan` do not exist in the old version or in `cod-final`. They were added in the version 2 project; they are not among the 11 files, so I cannot verify them here — but the XML asks for them, and the build does not pass without them.

### The conclusion of the section

The application was not rewritten. It was **retrofitted**: the display mechanism of the list was changed (4 files: `activity_main.xml`, `MainActivity`, `MovieAdapter` + `IMovieListener`) and a test screen was added (2 files), while the model and the form stayed word for word in their place.

That is also the good news for the exam: 60% of the code you knew is still there, unchanged, and the 40% that changed is concentrated in three mechanisms you can count on your fingers — the list, the adapter, the click.

---

## 39.6 What is still left to do in the code (what is lame)

The code of version 2 compiles and runs. It is not clean, though: it has leftovers from the old version, an unfinished screen and a list row filled a quarter of the way. All of the following is verifiable in the files.

### 1. `android:orientation` on a container that does not have it

`activity_main.xml`, on the `FrameLayout`:

```xml
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">
```

`FrameLayout` has no `orientation` attribute. The attribute is **ignored** by Android and produces at most a lint warning ("Unknown attribute"). It comes from the old version, where it was equally useless — we inherited it, we did not add it.

The same problem, mirrored, in `activity_place_ciocanul.xml`, on a `RelativeLayout`:

```xml
    tools:context=".activities.PlaceCiocanul"
    android:orientation="vertical">
```

**Why it matters.** Not because it bothers anything now, but because it becomes functional exactly when you least expect it. If an exam requirement sounds like "change the `FrameLayout` into a `LinearLayout` so you can put a title above the list", the `orientation="horizontal"` attribute suddenly starts to matter: the list and the title are laid out **next to each other**, not one under the other, and the FAB no longer floats over anything. The result looks like a bug you wrote, although the line was there from the start.

**The fix:** delete the attribute from both files. If you need a `LinearLayout`, write `orientation` explicitly, with the value you want.

### 2. `activity_place_ciocanul.xml`: a `RecyclerView` that will display nothing

```xml
    <androidx.recyclerview.widget.RecyclerView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
```

Three problems — two in the XML, one in the code:

| Problem | Where | Effect |
|---|---|---|
| no `android:id` | XML | `findViewById` has nothing to look for; the code cannot reach it |
| `wrap_content` on both axes | XML | even with an adapter, it would size itself after the content, not after the screen |
| no `LayoutManager` and no `setAdapter` | code | `RecyclerView` does not know how to arrange the rows and has nothing to arrange |

And in `PlaceCiocanul.java` there is **no** reference to it at all: the screen's `initControls` is a single line, `btn2 = findViewById(R.id.floatingActionButton2);`. So the widget is inert: it occupies a 0×0 rectangle in the top-left corner and that is it.

**The fix**, if you want to use it: `android:id="@+id/rvCiocane"`, `layout_width="match_parent"`, `layout_height="match_parent"`, then in `onCreate`: `findViewById`, `setLayoutManager(new LinearLayoutManager(this))`, `setAdapter(...)`. If not, delete it — a dead widget in a layout is an invitation to confusion.

**Also in the same file**, two things you see only on the phone, not in the editor. The button has `tools:layout_editor_absoluteX="334dp"` and `tools:layout_editor_absoluteY="655dp"` — **editor** attributes, which tell Android Studio where to draw it in the preview and are removed at build time. And the `ProgressBar` has `android:layout_width="6dp"`. In a `RelativeLayout` with no rule at all (`layout_below`, `layout_alignParentBottom` etc.), all children are placed in the top-left corner. So on the phone the button and the `ProgressBar` overlap, and the bar is 6 pixels wide — not a visible indicator.

### 3. `movie_item.xml`: 10 widgets, 2 filled

The exact number, from the file: **10 widgets with `android:id`** (an `ImageView`, four `TextView`s, a `RatingBar`, four `Chip`s), plus a `ChipGroup` that groups the last ones — 11 IDs in total.

`MovieViewHolder` binds **9** of them, through `findViewById`:

```java
            poster = itemView.findViewById(R.id.moviePoster);
            title = itemView.findViewById(R.id.movieTitle);
            subtitle = itemView.findViewById(R.id.movieSubtitle);
            rating = itemView.findViewById(R.id.movieRating);
            ratingValue = itemView.findViewById(R.id.movieRatingValue);
            facts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchList = itemView.findViewById(R.id.chipWatchlist);
```

`onBindViewHolder` writes into **two**: `title` and `subtitle`.

```java
        holder.title.setText(movie.getTitle());
        holder.subtitle.setText(movie.getGenre().toString() + ". " + sdf.format(movie.getRelease()));
```

The rest stay with the static values from the XML:

| Widget | The value from `movie_item.xml` | Does it change? |
|---|---|---|
| `movieTitle` | `"Movie title"` | yes, from `movie.getTitle()` |
| `movieSubtitle` | `"Genre · Year"` | yes, from the genre + the release year |
| `moviePoster` | `@android:drawable/ic_menu_gallery` | no — `posterUrl` is not used |
| `movieRating` | `numStars=5`, `stepSize=0.5`, no progress | no — it stays empty |
| `movieRatingValue` | `"4.5"` | no |
| `movieFacts` | `"142 min  ·  $160M"` | no |
| `chipApproval` | `"Approved"` | no |
| `chipWatched` | `"Watched"` | no |
| `chipWatchlist` | `"Watchlist"` | no |
| `chipCiocan` | `@string/chip_ciocan_name` | no — it is not even declared in the `ViewHolder` |
| `movieStatusGroup` | — (group) | it is not referenced anywhere |

**The effect on screen:** every card shows the title and subtitle correctly, but **all** of them have the same "4.5" value, the same "142 min · $160M" and the same four chips — including the "hammer" chip, on every movie. A movie of 81 minutes shows "142 min". A movie with rating 5 shows "4.5".

It is not a bug that crashes: it is a bug that **lies**. And it is hard to notice, because on the first row it looks plausible.

**The fix** is exercise 23.7 and 23.8 from chapter 23: in `onBindViewHolder`, also write `holder.rating.setRating(movie.getRating())`, `holder.ratingValue.setText(String.format("%.1f", movie.getRating()))`, compose `facts` from the duration and the budget, then set the visibility of the chips depending on `approval`, `watched` and `onWatchlist` — without forgetting the `else` branch (`View.GONE`), otherwise the recycled rows keep the chips of the previous movie.

### 4. The `Toast` in `PlaceCiocanul` has test text

```java
                Toast.makeText(PlaceCiocanul.this, "Caca", Toast.LENGTH_LONG).show();
```

The text has nothing to do with the application. The screen is a test, and the message was left over from the first run.

**The fix:** a neutral text ("PlaceCiocanul works") or, better, `getString(R.string.app_name)` — which is also the correct demonstration of the difference explained in 39.4.

### And three more smaller things

**5. `notifyDataSetChanged()` instead of `notifyItem*`.** In the `launcher` callback, both branches — `movies.add(movie)` and `movies.set(position, movie)` — are followed by `movieAdapter.notifyDataSetChanged();`. It works, but it re-binds all the visible rows and loses the animation. The correct variant: `notifyItemInserted(movies.size() - 1)` on insert, `notifyItemChanged(position)` on edit (chapter 23, exercise 23.10).

**6. Dead code from the old version, left in place.** In `MainActivity`:

```java
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;
// ...
import java.util.List;
```

None of them is used any more: `AdapterView`, `ArrayAdapter`, `ListView` and `Toast` appear only in comments, and `List` was replaced by `ArrayList`. In addition, two commented-out blocks: the line with `new ArrayAdapter<>(...)` and the entire `setOnItemClickListener` listener. Java gives no error for unused imports, only a warning — so the code compiles.

The cost is not technical, it is a reading cost: at the exam, an `import android.widget.ListView;` in a file that no longer has a `ListView` makes you look for a structure that does not exist. Delete them.

**7. `MainActivity.onMovieClick` ignores the `movie` parameter.** The method receives the movie and then writes `movies.get(position)` in the extra. It works as long as the position and the object come from the same list, but it is a useless duplication. `intent.putExtra(MOVIE_EXTRA, movie);` is shorter and more correct.

### The table of repairs, in short

| # | Where | Repair | Effect |
|---|---|---|---|
| 1 | both layouts | removed `android:orientation` from the containers that do not have it | the warning goes away and so does the trap when changing the container |
| 2 | `activity_place_ciocanul.xml` | id + `LinearLayoutManager` + adapter, or deletion; positioning rules for the FAB and the `ProgressBar` | the screen actually displays something, with no overlaps |
| 3 | `MovieAdapter` | `onBindViewHolder` completed with rating, facts, chips | each card shows its own movie's data |
| 4 | `PlaceCiocanul` | `Toast` with a real message | the screen no longer looks like an unfinished test |
| 5 | `MainActivity` | `notifyItemInserted` / `notifyItemChanged` | animation + less work |
| 6 | `MainActivity` | imports and commented blocks deleted | code easier to read at the exam |
| 7 | `MainActivity.onMovieClick` | `putExtra(MOVIE_EXTRA, movie)` | a single source of truth |

None of the seven gets in the way at the exam. All seven are exactly what you could receive as an additional requirement.

---

## 39.7 What it means for the exam

Two things, both of which change the way you approach the requirement.

### 1. The requirement "change `ListView` to `RecyclerView`" is already done

If at the test you receive the version 2 project and the requirement sounds like "replace `ListView` with `RecyclerView`", it is a trap or a reading check: the code **is already migrated**. What you can realistically be asked is to **modify** on top of the migration. Here is the correspondence between a requirement and the exact place you touch:

| The requirement that sounds like this | What you touch | Where it is explained |
|---|---|---|
| "Arrange the list in two columns" | `new GridLayoutManager(this, 2)` in `initControls` | 39.1 |
| "Make the list horizontal" | `new LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)` | 39.1 |
| "Change what is visible in each row" | `movie_item.xml` + `onBindViewHolder` | 39.2, 39.6 |
| "Fill the rating / duration / chips" | `onBindViewHolder` + `View.GONE` branches | 39.2, ch. 23 (23.7, 23.8) |
| "Click on a chip, not on the whole card" | `chipX.setOnClickListener` in the `ViewHolder` | 39.3 |
| "Long click to delete" | `setOnLongClickListener` + `notifyItemRemoved(position)` | 39.3 |
| "Notify the list after saving, with animation" | `notifyItemInserted` / `notifyItemChanged` | 39.2, 39.6 |
| "Add a new field in the row" | `movie_item.xml` + field in the `ViewHolder` + line in `onBindViewHolder` | 39.2 |
| "Change the destination of the click" | only `MainActivity.onMovieClick` | 39.3 |

Notice the pattern: **all** of them go through one of the files touched by the migration. No new requirement sends you into `Movie` or into `ItemActivity`, because those have nothing to do with the list.

The difference in attitude compared to chapter 23: there you **build** the adapter from scratch, with ten steps and intermediate checkpoints; here you **modify** an adapter that exists. At the exam, the second is the likely variant — so read `MovieAdapter` until you can rewrite it from memory, but do not start from an empty file.

### 2. What stays the same

All the recipes from chapters 33–35 stay valid. But with a clarification that you see only when you apply them: **the list at the end of them is now `RecyclerView`**.

| Type of requirement | What changes compared to the recipe | What stays identical |
|---|---|---|
| add an attribute in the model | nothing | the three places in `Movie`: field, constructor, getter/setter |
| bind a new control in the form | nothing | `findViewById`, the reading in `saveMovie`, the writing in `fillForm` |
| send data between screens | nothing | `putExtra` / `setResult` / the `launcher` callback |
| save persistently | nothing | the whole `ItemActivity` file (39.5) |
| **display the new attribute in the list** | **yes** — it is added in `movie_item.xml`, in the `ViewHolder` and in `onBindViewHolder` | the rest |
| **notify the list after a change** | **yes** — `MovieAdapter`, not `ArrayAdapter`; `notifyItem*` is the correct variant | the branches in the callback |

The last two rows are the only places where the `RecyclerView` comes into play. They are also the only places where marks are lost, because that is where two things you knew separately meet: the model (chapters 02, 17) and the adapter (chapters 18, 23).

**Concretely, what "`notifyDataSetChanged()` and `MovieAdapter` come into play" means:** if the requirement is "add a `country` field and display it in the list", the complete chain is:

```
Movie.java          → field + constructor + getter/setter        (unchanged compared to the recipe)
activity_item.xml   → one more EditText                          (unchanged)
ItemActivity.java   → findViewById + reading in saveMovie        (unchanged)
movie_item.xml      → one more TextView                          (new: the row)
MovieAdapter.java   → field in ViewHolder + one line in bind     (new: the adapter)
MainActivity.java   → nothing, if the list is already notified   (unchanged)
```

The first three lines are the recipe you knew. The last two are the novelty. This is where the time goes at the exam.

### The four mistakes that cost marks in version 2

1. **You forget `setLayoutManager`.** Empty list, with no error at all in Logcat. It is the only mistake in the whole chapter that does not complain at all (chapter 23, the first hint from 23.10).
2. **You fill only part of the row.** The version 2 code does exactly that: 2 fields out of 10. It looks plausible on the first row, but the data is static (39.6, point 3).
3. **Chips without the `else` branch.** The recycled rows keep the previous movie's status — the classic "recycling bug".
4. **`notifyItemInserted(movies.size())`** instead of `movies.size() - 1`. `Inconsistency detected`, only on insert.

### What a complete answer looks like

If at the test you receive "change the list so that it also displays the rating", the answer has three parts, all outside the model and the form: the widget in `movie_item.xml` (if it is missing), the field and the `findViewById` in the `ViewHolder`, the line in `onBindViewHolder` plus `notifyDataSetChanged()` if the data changes from somewhere else. Three places — exactly the 40% that changed in version 2.

---

## Chapter 39 summary

**What changed, in four lines:**

| Area | Old | New | Section |
|---|---|---|---|
| The list widget | `<ListView id=listView entries=@array/items>` | `<RecyclerView id=rvMovies>`, without `entries` | 39.1 |
| The adapter | `ArrayAdapter<Movie>` + `simple_list_item_1` + `toString()` | `MovieAdapter` + `movie_item.xml` + 3 methods | 39.2 |
| The click | `setOnItemClickListener`, on the list | `IMovieListener` interface, on each row | 39.3 |
| Screens | 2 | 3 (+ `PlaceCiocanul`) | 39.4 |

**What stayed identical:**

| File | Lines | Difference |
|---|---|---|
| `Movie.java` | 130 | only `package` |
| `ItemActivity.java` | 217 | `package` + 2 imports |
| `activity_item.xml` | 451 | none |

798 out of 1,317 lines of code and layout — roughly 60% of the application — was not touched. The model and the form behave exactly as in chapters 22, 33–35.

**The three new mechanisms you must be able to write from memory:**

```java
// 1. wiring the list — MainActivity.initControls(), copied from the source
rvMovies = findViewById(R.id.rvMovies);
rvMovies.setLayoutManager(new LinearLayoutManager(this));
rvMovies.setAdapter(movieAdapter);

// 2. the adapter contract — MovieAdapter, signatures abbreviated
onCreateViewHolder(parent, viewType) → inflate(R.layout.movie_item) + new MovieViewHolder(view)
onBindViewHolder(holder, position)   → holder.title.setText(...); holder.subtitle.setText(...)
getItemCount()                       → movies.size()

// 3. the click — MovieAdapter.MovieViewHolder, copied from the source
itemView.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        int pos = getAbsoluteAdapterPosition();
        if (pos != RecyclerView.NO_POSITION) {
            Movie movie = movies.get(pos);
            listener.onMovieClick(movie, pos);
        }
    }
});
```

**What is lame in the version 2 code** — seven things, all real: `orientation` on `FrameLayout`; `RecyclerView` without id and without a `LayoutManager` in `PlaceCiocanul`; `onBindViewHolder` filling 2 out of 10 widgets; `Toast` with test text; `notifyDataSetChanged()` instead of `notifyItem*`; imports and commented blocks left over from the old version; the `movie` parameter ignored in `onMovieClick`.

**Three sentences to remember:**

1. The migration was not done from scratch, it was done **on top of** the existing code — and you can see it: 60% of the lines are untouched.
2. `RecyclerView` has no click on the list; the click is put on the row, and the adapter reports it through the interface — the chain is always the same and you learn it once.
3. At the exam, the requirement almost certainly touches one of the three places: `setLayoutManager`, `onBindViewHolder`, or the click chain. The rest is code you already knew.

**For the code annotated line by line**, see chapter 38. **For the step-by-step migration, with intermediate checkpoints**, see chapter 23. This chapter was about **why** and about **what it means** — the other two chapters are about **how**.
