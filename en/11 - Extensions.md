# Chapter 11 — Extensions: `RecyclerView`, binding, new attributes

**Objective:** Replace `ListView` + `ArrayAdapter` with `RecyclerView` + a custom adapter, using `ViewHolder` and `onBindViewHolder`. Then extend the model with new attributes and bind them in the list.

**Estimated time:** 90–120 min.

**Source:** `movie_item.xml` exists in the repo (`d719ffc`). `MovieAdapter.java` is **not** in the repo — it is your local work from 09.11, not committed. You will rebuild it here as an exercise, just like in the next lab.

---

## Part A — Why `RecyclerView`

### Step 11.1 — The problem with `ListView`

#### Why

`ListView` **recycles** views: it creates ~10 visible rows, then reuses them as you scroll. But it has three problems:

1. **`findViewById` for every row** — `ArrayAdapter.getView()` looks up the views every time. It's slow.
2. **Complex layouts** — `simple_list_item_1` has just one `TextView`. For a card with a poster, title, rating, and chips, you need a custom layout.
3. **No animations** — adding or deleting an item is not animated.

`RecyclerView` solves all three:
1. **`ViewHolder`** — holds references to views, found only once.
2. **Custom layout** — `movie_item.xml`.
3. **`ItemAnimator`** — free animations.

#### The fundamental difference

| | `ListView` | `RecyclerView` |
|---|---|---|
| Adapter | `ArrayAdapter` (provided) | `RecyclerView.Adapter` (you write it) |
| Views | `getView()` with `convertView` | `onCreateViewHolder` + `onBindViewHolder` |
| Recycling | manual (`convertView`) | automatic, through `ViewHolder` |
| Layout | always vertical | configurable (`LinearLayoutManager`, `GridLayoutManager`) |
| Animations | no | yes |

---

### Step 11.2 — `ViewHolder`: why it exists

#### Why

Without `ViewHolder`, `getView()` would do this:

```java
if (convertView == null) {
    convertView = inflater.inflate(R.layout.movie_item, parent, false);
}
TextView title = convertView.findViewById(R.id.movieTitle);  // ← la FIECARE apel
```

`findViewById` traverses the view tree. On a card with 10 elements, that's 10 lookups × N rows × M scrolls.

With `ViewHolder`:

```java
if (convertView == null) {
    convertView = inflater.inflate(R.layout.movie_item, parent, false);
    holder = new MovieViewHolder(convertView);   // ← o singură dată
    convertView.setTag(holder);
} else {
    holder = (MovieViewHolder) convertView.getTag();
}
```

The lookup happens **only once per recycled view**. After that, you reuse the references.

> **Remember:** `ViewHolder` = a cache of references. It isn't “a nice wrapper” — it's the main optimization.

---

### Step 11.3 — `movie_item.xml`: a row's layout

#### Why

A movie card has: poster, title, subtitle (genre · year), rating (stars + value), facts (duration · budget), status chips.

#### How

The file is in `cod-final/res/layout/movie_item.xml` (5821 B, 136 lines). Structure:

```
MaterialCardView (cornerRadius 16dp, elevation 3dp)
└── LinearLayout orizontal (padding 12dp)
    ├── ImageView moviePoster (96×140dp)
    └── LinearLayout vertical (weight 1)
        ├── TextView movieTitle (20sp, bold, maxLines 2)
        ├── TextView movieSubtitle (14sp, gri)
        ├── LinearLayout orizontal
        │   ├── RatingBar movieRating (small, isIndicator)
        │   └── TextView movieRatingValue
        ├── TextView movieFacts (13sp, gri)
        └── ChipGroup movieStatusGroup
            ├── Chip chipApproval
            ├── Chip chipWatched
            └── Chip chipWatchlist
```

#### Key attributes

| Element | Attribute | Why |
|---|---|---|
| `MaterialCardView` | `app:cardCornerRadius="16dp"` | rounded corners |
| | `app:cardElevation="3dp"` | shadow (here **yes**, unlike the form cards) |
| | `app:cardUseCompatPadding="true"` | padding for the shadow on older APIs |
| `ImageView` | `layout_width="96dp"`, `layout_height="140dp"` | ~2:3 ratio, like a poster |
| | `scaleType="centerCrop"` | fills the space and crops without distorting |
| | `src="@android:drawable/ic_menu_gallery"` | placeholder |
| `LinearLayout` info | `layout_width="0dp"` + `layout_weight="1"` | takes all the remaining space |
| `TextView` title | `maxLines="2"`, `ellipsize="end"` | long titles are truncated with “…” |
| `RatingBar` | `style="?android:attr/ratingBarStyleSmall"` | small variant |
| | `isIndicator="true"` | **display only**, cannot be changed |
| `ChipGroup` | `singleLine="false"` | chips can wrap to the next line |
| `Chip` | `clickable="false"` | they are not buttons |
| | `ensureMinTouchTargetSize="false"` | 28dp high, not 48dp |

#### Why `isIndicator="true"`

In a list, the rating is **information**, not input. `isIndicator` makes the stars non-interactive. Without it, the user could change the rating directly in the list — and you'd need a listener to save it.

#### Why `ensureMinTouchTargetSize="false"`

Material enforces a minimum touch target of 48dp. A decorative 28dp `Chip` would be expanded to 48dp, breaking the layout. Disabling this is correct for **non-interactive** chips.

---

### Step 11.4 — Add `RecyclerView` to the project

#### Why

`RecyclerView` is **not** part of `appcompat` or `material`. It's a separate library: `androidx.recyclerview:recyclerview`.

#### How

1. In `gradle/libs.versions.toml`:

```toml
[versions]
recyclerview = "1.4.0"

[libraries]
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

2. In `app/build.gradle.kts`:

```kotlin
dependencies {
    // ... existente ...
    implementation(libs.recyclerview)
}
```

3. **Sync Project with Gradle Files**.

#### Exercise 11.4

**Requirement:** what happens if you try to use `RecyclerView` without adding the dependency?

<details>
<summary>Solution — explanation</summary>

**What was done:** I tried to declare `androidx.recyclerview.widget.RecyclerView` without the dependency.

**What happens:** a **compilation error**:

```
error: package androidx.recyclerview.widget does not exist
```

**Why:** `RecyclerView` is not in the Android SDK or in `appcompat`. It's a separate AndroidX library.

**Remember:**
1. `appcompat` provides `AppCompatActivity`, `Fragment`, etc.
2. `material` provides `MaterialCardView`, `Chip`, `MaterialButton`, etc.
3. `recyclerview` provides `RecyclerView`, `LinearLayoutManager`, `ViewHolder`.
4. `constraintlayout` provides `ConstraintLayout`.

Each library is added separately.

**Where it comes back:** if you want to load images from a URL, you need **another** library (Glide, Coil, Picasso). None of the libraries above include one.

</details>

---

### Step 11.5 — Replace `ListView` with `RecyclerView`

#### How

`activity_main.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".activities.MainActivity">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        tools:listitem="@layout/movie_item" />

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

#### What changed

| Before | Now | Why |
|---|---|---|
| `android:orientation="horizontal"` | **removed** | invalid on `FrameLayout` |
| `<ListView id=listView>` | `<RecyclerView id=recyclerView>` | new widget |
| `android:entries="@array/items"` | **removed** | `RecyclerView` has no `entries` |
| — | `tools:listitem="@layout/movie_item"` | preview with the actual card |

#### `tools:listitem`

It's the modern equivalent of `android:entries`, but **for preview only**. It tells Android Studio: “draw a row using this layout”. At runtime, it does nothing.

> **Remember:** `tools:*` = design time. `android:*` = runtime. `tools:listitem` is the best way to preview a `RecyclerView`.

---

## Part B — The adapter

### Step 11.6 — The `MovieAdapter` structure

#### Why

`RecyclerView.Adapter` has **three** required abstract methods:

1. `onCreateViewHolder(parent, viewType)` — creates an empty row.
2. `onBindViewHolder(holder, position)` — fills the row with data.
3. `getItemCount()` — how many rows there are.

Plus an optional `ViewHolder` inner class.

#### How

Create the `ro.ase.ie.g1097.adapters` package and the `MovieAdapter` class.

```java
package ro.ase.ie.g1097.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.RatingBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.chip.Chip;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(int position);
    }

    private final List<Movie> movies;
    private final OnItemClickListener listener;
    private static final SimpleDateFormat dateFormat =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    public MovieAdapter(List<Movie> movies, OnItemClickListener listener) {
        this.movies = movies;
        this.listener = listener;
    }

    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        Movie movie = movies.get(position);
        holder.bind(movie, listener);
    }

    @Override
    public int getItemCount() {
        return movies != null ? movies.size() : 0;
    }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {
        // pasul 11.7
    }
}
```

#### Why `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`

The generic parameter is the **`ViewHolder` type** you use. This makes `onBindViewHolder` type-safe: `holder` is a `MovieViewHolder`, not a `RecyclerView.ViewHolder`.

#### Why define `interface OnItemClickListener` in the adapter

`RecyclerView` **does not have** `setOnItemClickListener`. It's a design choice: items can have only part of the card be clickable.

The solution: define an interface, receive it in the constructor, and call it on click.

> **Remember:** `ListView` has `setOnItemClickListener`; `RecyclerView` **doesn't**. You have to implement it yourself.

#### Why `static final SimpleDateFormat`

`SimpleDateFormat` is **expensive** to create (it parses the pattern). If you created one per row, you'd have 100 objects for 100 rows. Static means one shared instance for all of them.

> **Warning:** `SimpleDateFormat` is **not thread-safe**. It's only used on the UI thread here. If the adapter were used from multiple threads, this would be a bug.

#### Why `movies != null ? movies.size() : 0`

It's defensive. If `movies` were `null`, `getItemCount()` would throw an NPE and `RecyclerView` would crash during layout. Returning 0 means “empty list”.

---

### Step 11.7 — `ViewHolder` with `bind`

#### Why

`ViewHolder` holds the references. `bind()` moves the filling logic from `onBindViewHolder` into `ViewHolder`, so it can be reused.

#### How

```java
public static class MovieViewHolder extends RecyclerView.ViewHolder {
    private final ImageView moviePoster;
    private final TextView movieTitle;
    private final TextView movieSubtitle;
    private final RatingBar movieRating;
    private final TextView movieRatingValue;
    private final TextView movieFacts;
    private final Chip chipApproval;
    private final Chip chipWatched;
    private final Chip chipWatchlist;

    public MovieViewHolder(@NonNull View itemView) {
        super(itemView);
        moviePoster = itemView.findViewById(R.id.moviePoster);
        movieTitle = itemView.findViewById(R.id.movieTitle);
        movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
        movieRating = itemView.findViewById(R.id.movieRating);
        movieRatingValue = itemView.findViewById(R.id.movieRatingValue);
        movieFacts = itemView.findViewById(R.id.movieFacts);
        chipApproval = itemView.findViewById(R.id.chipApproval);
        chipWatched = itemView.findViewById(R.id.chipWatched);
        chipWatchlist = itemView.findViewById(R.id.chipWatchlist);
    }

    public void bind(Movie movie, OnItemClickListener listener) {
        if (movie == null) return;

        movieTitle.setText(movie.getTitle());

        String yearStr = movie.getRelease() != null
                ? dateFormat.format(movie.getRelease()) : "";
        String genreStr = movie.getGenre() != null ? movie.getGenre() : "";
        if (!genreStr.isEmpty() && !yearStr.isEmpty()) {
            movieSubtitle.setText(genreStr + " · " + yearStr);
        } else if (!genreStr.isEmpty()) {
            movieSubtitle.setText(genreStr);
        } else {
            movieSubtitle.setText(yearStr);
        }

        movieRating.setRating(movie.getRating());
        movieRatingValue.setText(String.valueOf(movie.getRating()));

        String durationStr = movie.getDuration() + " min.";
        String budgetStr = "";
        if (movie.getBudget() >= 1_000_000) {
            budgetStr = "$" + (long) (movie.getBudget() / 1_000_000) + "M";
        } else if (movie.getBudget() > 0) {
            budgetStr = "$" + (long) movie.getBudget();
        }
        if (!budgetStr.isEmpty()) {
            movieFacts.setText(durationStr + "  ·  " + budgetStr);
        } else {
            movieFacts.setText(durationStr);
        }

        if (movie.getApproval() != null && !movie.getApproval().isEmpty()) {
            chipApproval.setText(movie.getApproval());
            chipApproval.setVisibility(View.VISIBLE);
        } else {
            chipApproval.setVisibility(View.GONE);
        }

        chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
        chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

        itemView.setOnClickListener(v -> {
            if (listener != null) {
                int pos = getBindingAdapterPosition();
                if (pos != RecyclerView.NO_POSITION) {
                    listener.onItemClick(pos);
                }
            }
        });
    }
}
```

#### Why `static class`

A `ViewHolder` is **one instance per visible row** (~10). If it weren't static, each one would hold a reference to `MovieAdapter` — with 100 rows, you'd have 100 unnecessary references. `static` removes that.

#### Why `findViewById` is in the constructor

It runs **only once per created view**, not on every bind. That's the optimization.

#### Why `getBindingAdapterPosition()` instead of `getAdapterPosition()`

`getAdapterPosition()` is **deprecated**. `getBindingAdapterPosition()` is the modern version; it accounts for `ConcatAdapter` (multiple adapters in one `RecyclerView`).

#### Why `NO_POSITION`

During a delete animation, a view may still be visible but have no valid position. `getBindingAdapterPosition()` returns `NO_POSITION` (-1). If you called `listener.onItemClick(-1)`, you'd get an `IndexOutOfBoundsException`.

#### Why `itemView.setOnClickListener` is in `bind`, not in the constructor

If you put the listener in the constructor, it would capture the position **when created** — but that changes when the view is recycled. Putting it in `bind` means `getBindingAdapterPosition()` is evaluated **when clicked**, so it's always correct.

> **This is the classic `RecyclerView` trap:** positions change and views are recycled. Any reference to a position must be evaluated at click time, not at bind time.

#### Budget formatting

```java
if (movie.getBudget() >= 1_000_000) {
    budgetStr = "$" + (long) (movie.getBudget() / 1_000_000) + "M";
}
```

`160000000 / 1000000 = 160.0` → `(long) 160.0 = 160` → `"$160M"`. Nice and compact.

`1_000_000` with underscores is just for readability — Java ignores them.

#### `View.GONE` vs `View.INVISIBLE`

| Value | Effect |
|---|---|
| `VISIBLE` | visible, takes up space |
| `INVISIBLE` | invisible, **takes up space** |
| `GONE` | invisible, **does not take up space** |

For chips, you want `GONE`: if it isn't “watched”, the chip disappears completely and the others rearrange themselves.

---

### Step 11.8 — Update `MainActivity`

#### How

```java
private RecyclerView recyclerView;
private MovieAdapter movieAdapter;

// în onCreate, înlocuiește:
// movieAdapter = new ArrayAdapter<>(...);
movieAdapter = new MovieAdapter(movies, position -> {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
});

// în initControls:
recyclerView = findViewById(R.id.recyclerView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));
recyclerView.setAdapter(movieAdapter);

// în initListeners: șterge listView.setOnItemClickListener(...)
```

#### `LayoutManager`

`RecyclerView` **doesn't know** how to arrange its items. It needs a `LayoutManager`:

| Manager | Arrangement |
|---|---|
| `LinearLayoutManager(this)` | vertical (default) |
| `LinearLayoutManager(this, HORIZONTAL, false)` | horizontal |
| `GridLayoutManager(this, 2)` | 2-column grid |
| `StaggeredGridLayoutManager(2, VERTICAL)` | grid with different item heights |

> **Remember:** without `setLayoutManager`, `RecyclerView` displays nothing. It doesn't show an error — just an empty list.

#### Why `notifyDataSetChanged()` stays

`RecyclerView.Adapter` also has `notifyDataSetChanged()`. It works the same way. But there are also more granular options:

| Method | Effect |
|---|---|
| `notifyDataSetChanged()` | rebuilds everything |
| `notifyItemInserted(pos)` | animates insertion |
| `notifyItemChanged(pos)` | animates the change |
| `notifyItemRemoved(pos)` | animates deletion |
| `notifyItemMoved(from, to)` | animates moving an item |

For adding/editing, the granular version looks nicer. But `notifyDataSetChanged()` is correct.

#### Exercise 11.8

**Requirement:** replace `notifyDataSetChanged()` with the granular options, depending on `position`.

<details>
<summary>Hint</summary>

In `onActivityResult`: if `position == -1`, it's an insertion at the end (`movies.size() - 1`). Otherwise, it's an update at `position`.

</details>

<details>
<summary>Solution — explanation</summary>

**What was done:** I replaced the global notification with a specific one.

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyItemInserted(movies.size() - 1);
} else {
    movies.set(position, movie);
    movieAdapter.notifyItemChanged(position);
}
```

**What you see:** the new movie **slides** into the list with a short animation. The edited movie's content changes with a fade.

**Why:** `RecyclerView` has a default `ItemAnimator` that animates `notifyItemInserted`, `notifyItemChanged`, etc. `notifyDataSetChanged()` **doesn't** trigger animations because it announces that “everything has changed”.

**Remember:**
1. `movies.size() - 1` = the position of the newly added item (the index is 0-based).
2. Order: **first** modify the list, **then** notify. If you notify first, `RecyclerView` reads an inconsistent list → `IndexOutOfBoundsException`.
3. `notifyItemChanged(position)` comes after `movies.set(position, movie)`.

**Where it comes back:** if you add deletion (swipe-to-delete), use `notifyItemRemoved(position)`.

</details>

---

## Part C — Extending the model

### Step 11.9 — Add a new attribute: `country`

#### Why

You want to add a “country of production” — a `String` that appears on the card. You need to change **five** places, in order.

#### The correct order (important!)

1. **Model** (`Movie.java`) — field + getter/setter + constructor.
2. **Form layout** (`activity_item.xml`) — a new field.
3. **`ItemActivity`** — `findViewById`, `fillForm`, `saveMovie`.
4. **Card layout** (`movie_item.xml`) — a new `TextView`.
5. **`MovieAdapter`** — `findViewById` in `ViewHolder`, `setText` in `bind`.

> **Rule:** model first, UI after. If you start with the UI, you'll get compile errors until you finish the model.

#### How — step 1: model

```java
private String country;

// în constructorul complet, adaugă la final:
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String country) {
    // ...
    this.country = country;
}

public String getCountry() { return country; }
public void setCountry(String country) { this.country = country; }
```

> **Warning:** you changed the constructor signature. All `new Movie(...)` calls with 10 arguments **will no longer compile**. You'll need to update `addSampleMovies` in `MainActivity`.

**Safer alternative:** keep the old constructor and add a new one with 11 parameters. But then you have two nearly identical constructors — confusing.

**Recommendation:** change the constructor and update every call. It's cleaner.

#### How — step 2: the form

In `activity_item.xml`, in Card 1 (Basics), after Release:

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

#### How — step 3: `ItemActivity`

```java
private EditText etCountry;

// initControls:
etCountry = findViewById(R.id.etCountry);

// fillForm:
etCountry.setText(existing.getCountry());

// saveMovie:
movie.setCountry(etCountry.getText().toString());
```

#### How — step 4: the card

In `movie_item.xml`, after `movieFacts`:

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

#### How — step 5: the adapter

```java
// în ViewHolder:
private final TextView movieCountry;

// în constructor:
movieCountry = itemView.findViewById(R.id.movieCountry);

// în bind:
movieCountry.setText(movie.getCountry() != null ? movie.getCountry() : "");
```

#### Exercise 11.9

**Requirement:** complete all 5 steps. Run the app. Check: add a movie with the country “USA”; it appears on the card.

<details>
<summary>Solution — explanation</summary>

**What was done:** I added a `country` attribute throughout the entire chain.

**What to check:**
1. `addSampleMovies` — all 3 `new Movie(...)` calls now have an 11th argument.
2. `MovieAdapter` — `movieCountry.setText(...)` does not throw an NPE.
3. The form — the field appears in Card 1.
4. The card — the country appears under “142 min · $160M”.

**Why 5 steps:** each layer has its own representation of the data:
- model: Java field
- form: `EditText`
- `ItemActivity`: read/write
- card: `TextView`
- adapter: binding

**Remember:**
1. **Order matters.** Model → form → activity → card → adapter.
2. If you forget a step, either the data won't be saved or the field won't appear.
3. On a test, if asked to “add an attribute”, list the 5 steps.

**Where it comes back:** every new attribute follows exactly the same chain.

</details>

---

### Step 11.10 — Add a derived attribute: `isRecent`

#### Why

A **derived** attribute is not saved — it's calculated. “Recent movie” = released in the last 5 years.

#### How

```java
// în Movie.java:
public boolean isRecent() {
    if (release == null) return false;
    Calendar fiveYearsAgo = Calendar.getInstance();
    fiveYearsAgo.add(Calendar.YEAR, -5);
    return release.after(fiveYearsAgo.getTime());
}
```

#### Why it isn't a field

If you saved `isRecent` as a `boolean`, it would become outdated: a movie that's recent today won't be recent in 5 years. **A derived value is calculated from the source data**, not stored.

> **Remember:** `isRecent()` is a method, not a field getter. It has no setter. It does not appear in the constructor.

#### How to display it

In `movie_item.xml`, add a `Chip`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipRecent"
    style="@style/Widget.Material3.Chip.Assist"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Recent"
    android:clickable="false"
    app:chipMinHeight="28dp"
    app:ensureMinTouchTargetSize="false" />
```

In the adapter:

```java
chipRecent.setVisibility(movie.isRecent() ? View.VISIBLE : View.GONE);
```

#### Exercise 11.10

**Requirement:** add `isRecent` and display it. What happens with “Inception” (2010)? What about “Dune” (2021)?

<details>
<summary>Solution — explanation</summary>

**What was done:** I added the `isRecent()` method and the chip.

**What you see (in 2026):**
- “Inception” (2010) → **not** recent (16 years)
- “Dune” (2021) → **not** recent (5 years, right on the cutoff — depends on the month)
- A movie from 2024 → **yes**, it's recent

**Why:** `fiveYearsAgo.add(Calendar.YEAR, -5)` subtracts 5 years from the current date. `release.after(fiveYearsAgo)` is `true` if the movie is newer.

**Remember:**
1. **Derived attributes** are calculated, not stored.
2. `Calendar.add` modifies the object **in place** (it doesn't return a new one).
3. `Date.after(Date)` compares points in time.
4. The result depends on the **current date** — the test is not deterministic. For tests, you need an injectable date.

**Where it comes back:** any attribute that depends on “now” (age, days until release, “new”) is derived and has the same testing problem.

</details>

---

### Step 11.11 — Add an action: delete a movie

#### Why

The list grows, but you can't delete anything. Add a delete button to each card.

#### How — step 1: the interface

In `MovieAdapter`:

```java
public interface OnItemClickListener {
    void onItemClick(int position);
    void onDeleteClick(int position);
}
```

Or, more cleanly, use two separate interfaces. Here we'll extend the existing one.

#### How — step 2: the card

In `movie_item.xml`, add an `ImageButton`:

```xml
<ImageButton
    android:id="@+id/btnDelete"
    android:layout_width="40dp"
    android:layout_height="40dp"
    android:layout_gravity="top|end"
    android:background="?attr/selectableItemBackgroundBorderless"
    android:contentDescription="Delete"
    android:src="@android:drawable/ic_menu_delete" />
```

#### How — step 3: the adapter

```java
// în ViewHolder:
private final ImageButton btnDelete;

// constructor:
btnDelete = itemView.findViewById(R.id.btnDelete);

// bind:
btnDelete.setOnClickListener(v -> {
    int pos = getBindingAdapterPosition();
    if (pos != RecyclerView.NO_POSITION && listener != null) {
        listener.onDeleteClick(pos);
    }
});
```

#### How — step 4: `MainActivity`

```java
movieAdapter = new MovieAdapter(movies, new MovieAdapter.OnItemClickListener() {
    @Override
    public void onItemClick(int position) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }

    @Override
    public void onDeleteClick(int position) {
        movies.remove(position);
        movieAdapter.notifyItemRemoved(position);
    }
});
```

#### Exercise 11.11

**Requirement:** implement deletion. Test it: delete the first movie, then edit the second. What happens?

<details>
<summary>Solution — explanation</summary>

**What was done:** I added the delete button and the complete flow.

**What you see:** the movie disappears with an animation.

**What happens when you edit after deletion:** **it works correctly**, because `position` is recalculated on click using the **current** position in the list.

**But** if you had kept a reference to a position (for example, in a `selectedPosition` field), you would have edited the wrong movie.

**Remember:**
1. `movies.remove(position)` **before** `notifyItemRemoved(position)`.
2. After deletion, all following positions **shift** by -1.
3. `getBindingAdapterPosition()` is evaluated on click → always correct.
4. For “undo”, you'd need a `Snackbar` with an action and would have to keep the deleted movie.

**Where it comes back:** the “delete + undo” pattern is standard in Material Design. `Snackbar.make(view, "Deleted", LENGTH_LONG).setAction("Undo", ...)`.

</details>

---

### Step 11.12 — Extension: search the list

#### Why

You don't need search for 3 movies. You do for 50. Add a `SearchView` or an `EditText` that filters the list.

#### How — the simple version

In `activity_main.xml`, above the `RecyclerView`... but `FrameLayout` doesn't stack children vertically. It needs to be changed to a vertical `LinearLayout` or a `CoordinatorLayout`.

**Minimal solution:** replace `FrameLayout` with a vertical `LinearLayout`:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <com.google.android.material.textfield.TextInputLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_margin="8dp"
        app:startIconDrawable="@android:drawable/ic_menu_search">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/etSearch"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:hint="Search movies" />
    </com.google.android.material.textfield.TextInputLayout>

    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <androidx.recyclerview.widget.RecyclerView
            android:id="@+id/recyclerView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            tools:listitem="@layout/movie_item" />

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

#### Why `layout_weight="1"` on `FrameLayout`

A vertical `LinearLayout` with a `TextInputLayout` (wrap_content) and a `FrameLayout` (0dp, weight 1): the second child takes all the remaining space. So the list fills the screen below the search box.

#### How to filter

```java
private final List<Movie> allMovies = new ArrayList<>();  // lista completă
private final List<Movie> movies = new ArrayList<>();     // lista filtrată

// în onCreate, după addSampleMovies:
allMovies.addAll(movies);

// în initListeners:
etSearch.addTextChangedListener(new TextWatcher() {
    @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
    @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}

    @Override
    public void afterTextChanged(Editable s) {
        String query = s.toString().toLowerCase().trim();
        movies.clear();
        if (query.isEmpty()) {
            movies.addAll(allMovies);
        } else {
            for (Movie m : allMovies) {
                if (m.getTitle() != null && m.getTitle().toLowerCase().contains(query)) {
                    movies.add(m);
                }
            }
        }
        movieAdapter.notifyDataSetChanged();
    }
});
```

#### Exercise 11.12

**Requirement:** implement search. Test it: type “in”; see Inception and Interstellar. Clear the field; see them all.

<details>
<summary>Solution — explanation</summary>

**What was done:** I separated the full list (`allMovies`) from the displayed list (`movies`).

**Why two lists:** if you filter `movies` **in place**, you lose the items that were removed. You need an untouched source list.

**Remember:**
1. The **displayed list** is a projection of the source list.
2. `movies.clear()` + `movies.addAll(...)` — don't reassign `movies`, because the adapter holds a reference to it.
3. `toLowerCase()` on both sides — case-insensitive search.
4. `contains(query)` — partial matching.
5. `notifyDataSetChanged()` after every change.

**The trap:** if you wrote `movies = filteredList;`, the adapter would still hold a reference to the **old** list → nothing would update.

**Where it comes back:** the same pattern applies to sorting and filtering by genre or rating.

</details>

---

### Step 11.13 — Extension: `DiffUtil` (advanced level)

#### Why

`notifyDataSetChanged()` rebuilds **everything**. For large lists, it's slow and loses animations. `DiffUtil` calculates the differences and notifies only about what changed.

#### How

```java
public void updateMovies(List<Movie> newMovies) {
    DiffUtil.DiffResult diff = DiffUtil.calculateDiff(new DiffUtil.Callback() {
        @Override public int getOldListSize() { return movies.size(); }
        @Override public int getNewListSize() { return newMovies.size(); }

        @Override
        public boolean areItemsTheSame(int oldPos, int newPos) {
            return movies.get(oldPos).getTitle().equals(newMovies.get(newPos).getTitle());
        }

        @Override
        public boolean areContentsTheSame(int oldPos, int newPos) {
            Movie a = movies.get(oldPos);
            Movie b = newMovies.get(newPos);
            return a.getTitle().equals(b.getTitle())
                    && a.getRating() == b.getRating()
                    && a.getBudget() == b.getBudget()
                    && a.getDuration() == b.getDuration();
        }
    });
    movies.clear();
    movies.addAll(newMovies);
    diff.dispatchUpdatesTo(this);
}
```

#### Why `areItemsTheSame` vs `areContentsTheSame`

| Method | Question |
|---|---|
| `areItemsTheSame` | “is this the same item?” (identity) |
| `areContentsTheSame` | “does it look the same?” (content) |

If it's the same item but the content is different → change animation.
If it's a different item → insertion/deletion animation.

> **Remember:** without a real `id`, `areItemsTheSame` relies on the title — which may be duplicated. It's a compromise. With a `long id`, it would be correct.

---

### Step 11.14 — Final exercise: add 3 attributes

**Requirement:** add `director` (String), `language` (String) and `sequel` (boolean) to the model, form, card, and adapter. Then display them.

#### Checklist

- [ ] `Movie`: 3 fields, getters/setters, updated constructor
- [ ] `activity_item.xml`: 2 `TextInputLayout` + 1 `MaterialSwitch`
- [ ] `ItemActivity`: 3 `findViewById`, 3 in `fillForm`, 3 in `saveMovie`
- [ ] `movie_item.xml`: 2 `TextView` + 1 `Chip`
- [ ] `MovieAdapter`: 3 references in `ViewHolder`, 3 `setText`/`setVisibility` calls in `bind`
- [ ] `MainActivity.addSampleMovies`: 3 new arguments per movie

#### Test questions

1. Why is the model changed **before** the UI?
2. What happens if you add the field to the model but forget it in `saveMovie`?
3. What happens if you add a `TextView` to the card but forget `findViewById` in `ViewHolder`?
4. Why doesn't `isRecent` have a setter?

<details>
<summary>Answers — explanation</summary>

**1. Why the model first?**
Because the UI **depends** on the model. If you start with the UI, the code won't compile until you add the field. Model → UI means the app can compile at every step.

**2. If you add the field but forget it in `saveMovie`?**
The field stays `null` (or `false`) for every saved movie. It's not an error — just missing data. A **silent bug**, the hardest kind to catch.

**3. If you add a `TextView` but forget `findViewById`?**
`movieDirector` stays `null` in `ViewHolder`. In `bind`, `movieDirector.setText(...)` → **NPE while scrolling**, not at launch. So the bug appears later.

**4. Why doesn't `isRecent` have a setter?**
Because it's **derived**. If you could set it, you'd have two sources of truth: `release` and `isRecent`, which could diverge. A derived value is always calculated from its source.

</details>

---

## Chapter 11 summary

- `RecyclerView` = `ViewHolder` (reference cache) + `onBindViewHolder` (binding) + `LayoutManager`.
- `ViewHolder` must be `static`; put `findViewById` in the constructor, where it runs once.
- Evaluate `getBindingAdapterPosition()` **on click**, not during bind.
- `notifyItemInserted/Changed/Removed` = animations; `notifyDataSetChanged` = rebuild everything.
- New attribute = 5 steps: model → form → activity → card → adapter.
- Derived attribute = method, not field.
- Filtering = source list + displayed list, never reassignment.

---

## What comes next

You've rebuilt and extended the app. Natural next steps:

| Extension | What you learn |
|---|---|
| Persistence with `Room` | database, `@Entity`, `@Dao`, `LiveData` |
| Image loading with Glide/Coil | network, cache, placeholder |
| `ViewModel` + `LiveData` | survive rotation, MVVM architecture |
| Navigation with `Navigation Component` | navigation graph, `Safe Args` |
| `Fragment`s | reusable screens, `FragmentManager` |
| Testing with JUnit + Espresso | unit tests, UI tests |

Each is a separate topic to learn. The current app is the foundation.
