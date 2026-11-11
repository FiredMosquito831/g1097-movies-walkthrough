# Chapter 23 — Bank 5: the complete ListView → RecyclerView migration

**Objective:** to carry out the `ListView` → `RecyclerView` migration in ten separate requirements, each with its own checkpoint, so that you can stop anywhere and still have a project that compiles and runs.

**Why in 10 steps:** at the exam the requirement arrives piece by piece ("add the dependency", "write the adapter", "wire up the rating", "fix the notification"), not in one breath. Each exercise here is one such piece, with the intermediate state described explicitly: after step N the project compiles, and you know exactly what you see on screen. The single-piece version is exercise 18.5; here it is the same migration, sliced up.

**Starting state** (commit `d719ffc`, folder `cod-final`):
- `activities/MainActivity.java` — `ListView` + `ArrayAdapter<Movie>` + `setOnItemClickListener`, three sample movies in `addSampleMovies()`.
- `res/layout/activity_main.xml` — `<ListView android:id="@+id/listView" ... android:entries="@array/items" />` inside a `FrameLayout`, plus the FAB.
- `res/layout/movie_item.xml` — **it exists, it is complete, but nothing in the whole project references it**.
- `gradle/libs.versions.toml` and `build.gradle.kts` — **they do not contain `recyclerview`**, neither in `[versions]`, nor in `[libraries]`, nor in `dependencies`.
- `model/Movie.java` — `Serializable`, with `title`, `release` (`Date`), `genre`, `budget` (`double`), `duration` (`int`), `rating` (`float`), `watched`, `approval`, `onWatchlist`, `poster`.

**Final state:** `RecyclerView` with `LinearLayoutManager`, `MovieAdapter` with `MovieViewHolder` binding the whole card from `movie_item.xml` (title, genre · year subtitle, rating, duration + budget, three chips), click through a custom interface to `launcher`, insert and edit notified with `notifyItemInserted` / `notifyItemChanged`.

**Table: what changes**

| | ListView | RecyclerView |
|---|---|---|
| Dependency | comes with `appcompat` | `androidx.recyclerview:recyclerview`, declared separately |
| Widget in XML | `<ListView>` | `<androidx.recyclerview.widget.RecyclerView>` |
| List attribute | `android:entries="@array/items"` | doesn't exist; `tools:listitem` only for the preview |
| Adapter | `ArrayAdapter<Movie>` (ready-made) | `RecyclerView.Adapter<MovieViewHolder>` (written by you) |
| Row | `android.R.layout.simple_list_item_1` + `toString()` | `movie_item.xml` + `ViewHolder` |
| Recycling | manual (`convertView` + `setTag`) | automatic, through `ViewHolder` |
| Arrangement | `AbsListView`'s own | separate `LayoutManager`, mandatory |
| Row click | `setOnItemClickListener` | custom interface, bound on `itemView` |
| Notification | `notifyDataSetChanged()` | `notifyItemInserted` / `notifyItemChanged` / `notifyItemRemoved` |
| Animations | none | default `ItemAnimator` |
| Mandatory methods | `getView`, `getCount`, `getItem` | `onCreateViewHolder`, `onBindViewHolder`, `getItemCount` |

> **The ten-step rule:** dependency → XML → empty class → `ViewHolder` → `onCreateViewHolder` → text → rating → facts + chips → click → activity. The order is not accidental: each step needs the type created in the previous step, and the activity is touched last, so you never have two errors at once.

---

## Exercise 23.1 — The `androidx.recyclerview` dependency

**Requirement:** add the `androidx.recyclerview:recyclerview` library to the version catalog and to the module's dependency list, then sync Gradle. Not a single line of Java code is written and no layout is touched.

**Files touched:** `gradle/libs.versions.toml`, `build.gradle.kts`

**How you approach it — your steps:**
1. Open `gradle/libs.versions.toml`. Find the `[versions]` section — it starts with `agp = "9.4.1"` and ends with `coordinatorlayout = "1.3.0"`. Add a new line at the end of the section: `recyclerview = "1.4.0"`.
2. In the same file, scroll down to `[libraries]`. The last line is the one for `coordinatorlayout`. Add the `recyclerview` line below it, with the same `group` / `name` / `version.ref` shape.
3. Open `build.gradle.kts` in the module root. In the `dependencies { }` block, add `implementation(libs.recyclerview)` right after `implementation(libs.material)`.
4. Click **Sync Now** on the banner that appears at the top of Android Studio (or `File → Sync Project with Gradle Files`). Wait for the progress bar to finish.
5. Check: `Build → Make Project` must give `BUILD SUCCESSFUL`. Open the **External Libraries** panel in the Project view — `Gradle: androidx.recyclerview:recyclerview:1.4.0` must appear. On the phone screen absolutely nothing changes, because nobody uses the class yet.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

the name in `[libraries]` becomes the name used in `build.gradle.kts`, with dashes turned into dots. The alias `recyclerview` (a single word) is accessed as `libs.recyclerview`. If you wrote `androidx-recyclerview`, you would access `libs.androidx.recyclerview`. Here we use the short form, as with `appcompat` and `material`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 3</summary>

`implementation(...)` wants the **generated accessor**, not the Maven coordinates. `implementation("androidx.recyclerview:recyclerview:1.4.0")` would work that way too, but in this project every dependency goes through the catalog — if you write the coordinates directly, you lose the point on the requirement. If `libs.recyclerview` shows up red, the sync from step 4 hasn't happened yet.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added a version and a library entry to the catalog, then wired it into the module's dependency list. Zero Java code.

**Code:**

`gradle/libs.versions.toml` — the `[versions]` section, at the end:

```toml
[versions]
agp = "9.4.1"
junit = "4.13.2"
junitVersion = "1.3.0"
espressoCore = "3.7.0"
appcompat = "1.8.0"
material = "1.14.0"
activityKtx = "1.13.0"
constraintlayout = "2.2.2"
coordinatorlayout = "1.3.0"
recyclerview = "1.4.0"
```

`gradle/libs.versions.toml` — the `[libraries]` section, at the end:

```toml
[libraries]
# ... the existing ones ...
coordinatorlayout = { group = "androidx.coordinatorlayout", name = "coordinatorlayout", version.ref = "coordinatorlayout" }
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

`build.gradle.kts` — the `dependencies` block, the new line is the last `implementation`:

```kotlin
dependencies {
    implementation(libs.activity.ktx)
    implementation(libs.appcompat)
    implementation(libs.constraintlayout)
    implementation(libs.material)
    implementation(libs.recyclerview)
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}
```

**Why:**
- `RecyclerView` is not part of the Android SDK and is not in `appcompat`. It is a separate AndroidX artifact with its own release cycle — that is why it has its own entry in the catalog.
- The catalog has two sections because they are two different things: `[versions]` holds the **numbers**, `[libraries]` holds the **coordinates**. A library can borrow another's version through `version.ref`, but here it has its own version.
- `implementation` means "I use it inside the module, I don't expose it to consumers". For an application (not a library) that is the right choice; `api` would only make sense in a library module.

**Remember:**
- Version `1.4.0` is the one used throughout the course (ch. 11, ch. 18). If Android Studio suggests a newer one at sync, accept it — the structure matters, not the number.
- `material` brings `recyclerview` in transitively, so it is possible the project compiles even without this step. Don't rely on it: you declare explicitly every library whose classes you use directly. Otherwise, an update to `material` can break your build without you having touched anything.
- The sync is not optional. Without it, Android Studio doesn't regenerate the `libs.*` accessors and everything that follows shows up red, even though the files are correct.

**Where it applies:** any requirement of the form "add library X". The same mechanics (version → library → `implementation` → sync) are used for Glide, Retrofit, Room too. If the exam asks "add the dependency", this is the complete answer, in three logical files and one sync.

</details>

---

## Exercise 23.2 — `ListView` → `RecyclerView` in the layout

**Requirement:** replace the widget in `activity_main.xml` with `RecyclerView` and fix strictly what is needed in `MainActivity` so the project compiles and the app doesn't crash. No adapter is created yet.

**Files touched:** `res/layout/activity_main.xml`, `java/ro/ase/ie/g1097/activities/MainActivity.java`

**How you approach it — your steps:**
1. Open `res/layout/activity_main.xml`. Find the `<ListView ... />` block — it is the first child of `FrameLayout`, it has `android:id="@+id/listView"` and `android:entries="@array/items"`.
2. Replace it with `<androidx.recyclerview.widget.RecyclerView ... />`, with `android:id="@+id/recyclerView"`, `layout_width`/`layout_height` `match_parent`, `tools:itemCount="3"` and `tools:listitem="@layout/movie_item"`. Delete `android:entries`.
3. Also delete `android:orientation="horizontal"` from `FrameLayout` — `FrameLayout` has no orientation, the attribute was ignored.
4. Open `MainActivity.java`. Delete `import android.widget.ListView;` and `import android.widget.AdapterView;`, add `import androidx.recyclerview.widget.RecyclerView;`.
5. Change the field `private ListView listView;` to `private RecyclerView recyclerView;`.
6. In `initControls()`: `listView = findViewById(R.id.listView);` becomes `recyclerView = findViewById(R.id.recyclerView);`, and the line `listView.setAdapter(movieAdapter);` is **deleted** (there is no adapter to put in yet).
7. In `initListeners()`: delete the entire `listView.setOnItemClickListener(new AdapterView.OnItemClickListener() { ... })` block. `RecyclerView` doesn't have that method — if you leave it, it won't compile.
8. Run it. You should see an empty screen with the FAB in the corner. Tap the FAB, fill in the form, save: the app **does not** crash, but the list stays empty.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

`RecyclerView` doesn't accept `android:entries`. The attribute belongs to `AbsListView` (the parent class of `ListView`), not to `RecyclerView`, which is a plain `ViewGroup`. If you leave it, the build passes, but the attribute is completely ignored — and it's a mistake the grader sees straight away.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

if you keep the `listView` id so you don't have to touch `MainActivity`, the code **compiles**, but at runtime you get `ClassCastException: androidx.recyclerview.widget.RecyclerView cannot be cast to android.widget.ListView`. `findViewById` is generic and casts to the requested type; the compiler cannot verify what object it actually finds in the XML. Renaming the id is what forces you to change the type.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we changed the widget in the XML, we changed the field type and the two calls that no longer make sense on `RecyclerView`. The list is now empty because it has no adapter — the state is correct for this step.

**Code:**

`res/layout/activity_main.xml` — the full file after the change:

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
        tools:itemCount="3"
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

`MainActivity.java` — exactly the four places touched:

```java
// 1. imports
import androidx.recyclerview.widget.RecyclerView;   // new
// DELETED: import android.widget.AdapterView;
// DELETED: import android.widget.ListView;

// 2. the field
private RecyclerView recyclerView;                  // was: private ListView listView;

// 3. initControls()
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    recyclerView = findViewById(R.id.recyclerView);
    // DELETED: listView.setAdapter(movieAdapter);
}

// 4. initListeners() — only the FAB block remains
private void initListeners() {
    fabInsert.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            launcher.launch(intent);
        }
    });
    // Deleted entirely: listView.setOnItemClickListener(new AdapterView.OnItemClickListener() { ... });
}
```

**Why:**
- `android:entries="@array/items"` was already dead before the migration: `initControls()` called `listView.setAdapter(movieAdapter)`, which replaced the adapter built from `entries`. With `RecyclerView` the attribute disappears altogether, because it doesn't exist on `AbsListView`.
- `tools:listitem="@layout/movie_item"` is the modern replacement: it tells **only the editor** to draw a sample row using the real card. At runtime it does nothing. `tools:itemCount="3"` tells it how many sample rows to draw. It is the first place in the project that references `movie_item.xml` — until now the file was completely unused.
- `tools:` = design-time, `android:` = runtime. The rule holds for all `tools:*` attributes.
- `RecyclerView` doesn't have `setOnItemClickListener` by design: a row can have different clickable areas (card, poster, button). The click is bound manually, on `itemView`, in the adapter — step 23.9.

**Remember:**
- After 23.2 the app **runs**, but the list is empty. It's not a bug: `RecyclerView` without an adapter displays nothing, and `RecyclerView` without a `LayoutManager` displays nothing **with no error in Logcat whatsoever**. The second one is the classic exam trap.
- The `ArrayAdapter` is still built in `onCreate` and `notifyDataSetChanged()` is still called from the `launcher` callback. It doesn't get in the way at all — an unattached adapter has nothing to redraw. It is only cleaned up at 23.10, when we replace it with `MovieAdapter`.
- `@array/items` in `strings.xml` now remains with no consumer. You can delete it, but it's not mandatory and it earns no points.

**Where it applies:** any requirement "replace widget X with Y". The template is always the same: XML → the field type → `findViewById` → the calls that no longer exist on the new type. When you change the type, the compiler tells you exactly which calls died; you don't have to guess.

</details>

---

## Exercise 23.3 — `MovieAdapter` with the three mandatory methods

**Requirement:** create the `MovieAdapter` class in the `adapters` package, extending `RecyclerView.Adapter`, with the three abstract methods implemented. The class compiles, but it is not used by any activity — nothing changes on screen.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (new file)

**How you approach it — your steps:**
1. In Project view, right-click the `ro.ase.ie.g1097` package → `New → Package`, name `adapters`. (Or `New → Java Class` and type the full name `ro.ase.ie.g1097.adapters.MovieAdapter` — Android Studio creates the package too.)
2. `New → Java Class` in the new package, name `MovieAdapter`, type `Class`.
3. Write the declaration: `public class MovieAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder>`. Note that the generic parameter is still `RecyclerView.ViewHolder`, not one of your classes — your `ViewHolder` class shows up at 23.4.
4. Add the field `private final List<Movie> movies;` and a constructor that receives it.
5. Implement `getItemCount()`: `return movies.size();`.
6. Implement `onCreateViewHolder(...)` returning a minimal `ViewHolder` — `RecyclerView.ViewHolder` is **abstract**, so you need an anonymous subclass: `new RecyclerView.ViewHolder(new View(parent.getContext())) { }`.
7. Implement `onBindViewHolder(...)` with an empty body and a `// 23.6` comment.
8. `Build → Make Project`. It must say `BUILD SUCCESSFUL`. On screen: unchanged.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

`RecyclerView.Adapter` wants a single generic parameter — the type of the `ViewHolder`. If you leave it off (`extends RecyclerView.Adapter`), you get `raw use of parameterized class` and `onCreateViewHolder` has nothing type-safe to return. If you put `RecyclerView.Adapter<Movie>` (the model type), you get an error because `Movie` doesn't extend `ViewHolder`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

`new RecyclerView.ViewHolder(view)` doesn't compile — the class is `abstract`. It's not a syntax problem, it's by design: `ViewHolder` is meant to be subclassed. The `{ }` trick at the end creates an anonymous subclass, enough for a skeleton that displays nothing. At 23.4 we replace it with our own class.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we created the adapter skeleton. It has the data, it knows how many rows there are, but it doesn't know how to build or fill a row. It isn't wired anywhere.

**Code:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`, full file:

```java
package ro.ase.ie.g1097.adapters;

import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) {
        this.movies = movies;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View randGol = new View(parent.getContext());
        return new RecyclerView.ViewHolder(randGol) { };
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        // 23.6
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }
}
```

**Why:**
- The three methods are the only abstract ones in `RecyclerView.Adapter`. `onCreateViewHolder` builds an empty row, `onBindViewHolder` fills an existing row, `getItemCount` says how many rows there are. If one is missing, the class doesn't compile.
- `movies` is `final` and is **the same list** that `MainActivity` also holds. The adapter doesn't copy the data, it only reads it. That is why `movies.add(...)` from the activity shows up in the list without reassigning anything.
- `@NonNull` on the parameters and on the return value is a contract, not decoration: `RecyclerView` doesn't accept a null `ViewHolder` from `onCreateViewHolder`.
- `RecyclerView.ViewHolder` is `abstract`, so the anonymous subclass `{ }` is the only way to return something without writing a separate class.

**Remember:**
- An `Adapter` displays nothing by itself. It needs `setAdapter` **and** `setLayoutManager` on a `RecyclerView` (23.10). That is why steps 23.3–23.9 don't change the screen.
- `getItemCount()` must be in sync with the real list. If you return a value larger than `movies.size()`, `onBindViewHolder` reaches `movies.get(nonexistent_position)` and you get `IndexOutOfBoundsException` while scrolling, not at startup.
- The `adapters` package is one of the project's three packages (`model`, `activities`, `adapters`). The adapter is not allowed to know about `MainActivity` — it communicates back only through the interface from 23.9.

**Where it applies:** any requirement "create an adapter for `RecyclerView`". The skeleton is identical regardless of the model: three methods, a field with the list, a constructor. The only difference between adapters is what goes into `onCreateViewHolder` and `onBindViewHolder`.

</details>

---

## Exercise 23.4 — `MovieViewHolder` with the fields from `movie_item.xml`

**Requirement:** add to `MovieAdapter` a static inner class `MovieViewHolder` that holds references to all the views in the card and looks them up once, in the constructor. The adapter stays parameterized on `RecyclerView.ViewHolder` — the new class is not used yet.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**How you approach it — your steps:**
1. Open `res/layout/movie_item.xml` and note all the `android:id`s: `moviePoster`, `movieTitle`, `movieSubtitle`, `movieRating`, `movieRatingValue`, `movieFacts`, `movieStatusGroup`, `chipApproval`, `chipWatched`, `chipWatchlist`.
2. Open `MovieAdapter.java`. At the end of the class, before the closing brace, write `public static class MovieViewHolder extends RecyclerView.ViewHolder { }`.
3. Declare a `private final` field for each view you bind: `TextView` for the title, subtitle, rating value and facts; `RatingBar` for the rating; `Chip` for the three chips. `moviePoster` and `movieStatusGroup` stay unbound.
4. Write the constructor `public MovieViewHolder(@NonNull View itemView)`, with `super(itemView);` on the first line.
5. In the constructor, one line `field = itemView.findViewById(R.id.xxx);` for each.
6. Add the imports: `android.widget.RatingBar`, `android.widget.TextView`, `com.google.android.material.chip.Chip`, `ro.ase.ie.g1097.R`.
7. `Build → Make Project`. `BUILD SUCCESSFUL`. On screen: unchanged — the class is declared, but nobody instantiates it yet.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

the inner class goes **inside** `MovieAdapter`, not as a separate file. `static` is not optional: without it, every `ViewHolder` holds a reference to the adapter, and after recycling you're left with objects keeping each other alive.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

`findViewById` is called on `itemView`, not on `this` and not on `parent`. `ViewHolder` is not a `View` — it's just an object that holds one. If you write plain `findViewById(...)`, the compiler tells you the method doesn't exist in `ViewHolder`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added the class that holds the row's references. The `findViewById` lookup happens once, when the row is created, not on every display.

**Code:** add to `MovieAdapter.java`, before the class's final brace:

```java
    public static class MovieViewHolder extends RecyclerView.ViewHolder {

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
            movieTitle = itemView.findViewById(R.id.movieTitle);
            movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
            movieRating = itemView.findViewById(R.id.movieRating);
            movieRatingValue = itemView.findViewById(R.id.movieRatingValue);
            movieFacts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchlist = itemView.findViewById(R.id.chipWatchlist);
        }
    }
```

The imports that get added at the top of the file:

```java
import android.widget.RatingBar;
import android.widget.TextView;

import com.google.android.material.chip.Chip;

import ro.ase.ie.g1097.R;
```

**Why:**
- `ViewHolder` exists exactly for this: `findViewById` is a search through the view tree, and without a `ViewHolder` it would happen on every display of every row, on every scroll. With it, it happens once per created row, then the references are reused.
- `static` is mandatory in practice: a non-static inner class keeps an implicit reference to the outer instance (`MovieAdapter`). With 10 visible rows you have 10 useless references, and if the adapter dies, the rows keep it alive.
- `moviePoster` stays unbound on purpose: the project has no image-loading library (Glide, Coil, Picasso), and `poster` is a text URL. The card displays the icon from the XML. Binding a real image is a different requirement.
- `movieStatusGroup` (the ChipGroup) doesn't need a reference: we hide the individual chips, and the group rearranges itself.

**Remember:**
- The fields are `final`: they are written once in the constructor and never touched again. If you make them mutable, nothing stops you from accidentally reassigning them in `bind`.
- The field type must be the real type from the XML. `movieRating` is a `RatingBar`, not a `TextView`; `chipApproval` is a `Chip` (from Material), not a `TextView`. A `findViewById` with the wrong type compiles and crashes at runtime with `ClassCastException`.
- The class is `public static`, not `private`: it appears as a generic parameter in the adapter's public signature. If you make it `private`, it still compiles internally, but you can no longer write `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>` from another file.

**Where it applies:** any `ViewHolder`, for any model. The rule: one field per view you modify from code, one `findViewById` in the constructor, `final` everywhere. Views you just leave as they are in the XML get no field.

</details>

---

## Exercise 23.5 — `onCreateViewHolder`: inflate `movie_item`

**Requirement:** bind `MovieViewHolder` to the adapter — change the generic parameter and make `onCreateViewHolder` inflate `R.layout.movie_item` and return a `MovieViewHolder` built on the inflated view.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**How you approach it — your steps:**
1. Open `MovieAdapter.java`.
2. Change the class declaration: `extends RecyclerView.Adapter<RecyclerView.ViewHolder>` becomes `extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`.
3. Change the `onCreateViewHolder` signature to return `MovieViewHolder` instead of `RecyclerView.ViewHolder`.
4. Replace the body: delete the two lines with `randGol` and the anonymous subclass; write `View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.movie_item, parent, false);` and `return new MovieViewHolder(view);`.
5. Also change the `onBindViewHolder` signature to take a `MovieViewHolder`.
6. Add `import android.view.LayoutInflater;`.
7. `Build → Make Project`. `BUILD SUCCESSFUL`. On screen: unchanged — the adapter is not attached to the `RecyclerView` yet.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 4</summary>

the third argument of `inflate` must be `false`. With `true`, `inflate` immediately attaches the row to `parent`, and `RecyclerView` throws `IllegalStateException` because it wants to control attachment itself. `false` means "build it, but let me place it".

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 5</summary>

if you changed the generic but forgot the signatures, you get `name clash: onBindViewHolder(RecyclerView.ViewHolder,int) and onBindViewHolder(MovieViewHolder,int) have the same erasure`. It's not a syntax error — it's the sign that you mixed the old type with the new one. Change both signatures in the same step.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the adapter now knows how to build a real row, from `movie_item.xml`. It still doesn't know how to fill it with data.

**Code:** `MovieAdapter.java` — the declaration and the two methods:

```java
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) {
        this.movies = movies;
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
        // 23.6
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }

    // ... MovieViewHolder from 23.4 ...
}
```

New import:

```java
import android.view.LayoutInflater;
```

**Why:**
- `LayoutInflater.from(parent.getContext())` — `inflate` needs a `Context`, and the `ViewHolder` doesn't have one. `parent` (the RecyclerView) has one, through `getContext()`.
- `parent` in `inflate` is not decorative: it gives the inflater the parent's correct `LayoutParams`. Without it, the card with `layout_width="match_parent"` would get default params and come out narrow.
- `false` for `attachToRoot` — `RecyclerView` attaches its rows itself, at its own moment. If `inflate` attached them, you'd have an extra row, unmanaged by the `LayoutManager`.
- The generic parameter makes `onBindViewHolder` type-safe: `holder` is `MovieViewHolder`, so you have direct access to `movieTitle` without a cast.

**Remember:**
- `onCreateViewHolder` runs **once per created row**, not once per item in the list. `RecyclerView` creates only as many rows as fit on screen plus a reserve, then reuses them. With 3 movies you see 3 rows; with 300, still as many as fit.
- `viewType` is the parameter that allows rows of different types in the same list. Here it is ignored, because we have a single row type.
- `@NonNull` on `parent` and on the return: `RecyclerView` tolerates neither a null `parent` nor a null `ViewHolder`.

**Remember — a visual check ahead of time:** if you want to see the card now, without waiting for 23.10, temporarily add in `MainActivity.initControls()`, after `findViewById`:

```java
recyclerView.setLayoutManager(new androidx.recyclerview.widget.LinearLayoutManager(this));
recyclerView.setAdapter(new ro.ase.ie.g1097.adapters.MovieAdapter(movies));
```

Run it: you see three empty cards (no text, because `bind` doesn't exist yet). **Delete the two lines immediately** — at 23.10 we write them properly, with the listener. Don't leave the temporary version in your exam solution.

**Where it applies:** any adapter with a single row type. The `inflate(R.layout.item_x, parent, false)` + `new XViewHolder(view)` template is identical for all of them; only the layout and class names change.

</details>

---

## Exercise 23.6 — `onBindViewHolder`: title and subtitle (genre · year)

**Requirement:** fill the row with data. `movieTitle` gets the movie title, `movieSubtitle` gets `genre · year`, with the year formatted with `SimpleDateFormat`.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**How you approach it — your steps:**
1. Open `MovieAdapter.java`.
2. Add in `MovieAdapter`, next to the `movies` field, a static formatter: `private static final SimpleDateFormat YEAR_FORMAT = new SimpleDateFormat("yyyy", Locale.getDefault());`.
3. Add the imports `java.text.SimpleDateFormat` and `java.util.Locale`.
4. In `MovieViewHolder`, add the method `public void bind(Movie movie)`, with `movieTitle.setText(movie.getTitle());` on the first line.
5. Below it, format the year: `String year = movie.getRelease() != null ? YEAR_FORMAT.format(movie.getRelease()) : "";`.
6. Add `movieSubtitle.setText(movie.getGenre() + " · " + year);`. Careful: the separator is `·` (U+00B7), with spaces around it, exactly as in the comment in `movie_item.xml`.
7. In `onBindViewHolder`, replace the comment with `holder.bind(movies.get(position));`.
8. `Build → Make Project`. `BUILD SUCCESSFUL`. On screen: unchanged (or, if you left the temporary check from 23.5, the cards now have a title and subtitle).

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 2</summary>

`SimpleDateFormat` is created **once**, as `static final`, not in `bind`. If you create it in `bind`, you build a new object on every display of every row — exactly the work the `ViewHolder` avoids. The `"yyyy"` pattern gives the four-digit year; `"yy"` would give `10` instead of `2010`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

the separator is not `-` and not `|`. It's `·` (middle dot), the character from the comment `<!-- genre · release year, e.g. "Sci-Fi · 2021" -->`. If you type it wrong from the keyboard, it shows up in the list as a box. Copy it from the comment in the XML.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the row now has text. `bind` is the method that translates a `Movie` into widgets; the rest of the steps just complete it.

**Code:** `MovieAdapter.java` — the new field, the imports and the `bind` method:

```java
import java.text.SimpleDateFormat;
import java.util.Locale;

public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;

    // ... constructor, onCreateViewHolder ...

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position));
    }

    // ... getItemCount ...

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

        // ... the fields and constructor from 23.4 ...

        public void bind(Movie movie) {
            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);
        }
    }
}
```

**Why:**
- `bind` receives `Movie`, not the position: the `ViewHolder` shouldn't know where it sits in the list. The position is the adapter's business, the object is the row's business.
- `YEAR_FORMAT` is `static final` in the outer class, not in `ViewHolder`. It's a single object for all rows, and the static inner class has access to the private static fields of the class containing it.
- The `movie.getRelease() != null` check is defensive: the model has a no-argument constructor and a setter, so a `Movie` can exist with a null `release`. `YEAR_FORMAT.format(null)` would throw `NullPointerException` right during scrolling.
- `Locale.getDefault()` on the formatter: for `"yyyy"` it doesn't change the digits for us, but it's the correct form. A formatter without an explicit `Locale` is flagged by lint.

**Remember:**
- `SimpleDateFormat` is **not thread-safe**. Here it's used only on the UI thread, so it's fine. If the adapter also ran from another thread, you'd need a formatter per thread or `java.time` (`DateTimeFormatter`, which is immutable).
- `bind` is called on **every** display, not once per row. A recycled row gets a different movie, so `bind` must overwrite **all** fields, not just the ones that change. This rule becomes critical with the chips (23.8).
- `movie.getRelease()` is a `Date`, not a `String`. You don't need `toString()` — the formatter accepts it directly.

**Where it applies:** any text field derived from the model. If the value is computed (year from a date, formatted price, plural), the computation lives in `bind`, not in the model — the model stays pure data.

</details>

---

## Exercise 23.7 — Rating: `movieRating` + `movieRatingValue`

**Requirement:** wire up the rating. `movieRating` (RatingBar) gets the value as stars, `movieRatingValue` (TextView) gets the value written with one decimal.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**How you approach it — your steps:**
1. Open `MovieAdapter.java` and find the `bind` method in `MovieViewHolder`.
2. Add `movieRating.setRating(movie.getRating());` after the subtitle line.
3. Add `movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));`.
4. Check in `movie_item.xml` that `movieRating` has `android:stepSize="0.5"` and `android:isIndicator="true"` — otherwise `setRating(4.5f)` would round to 4 or 5 stars.
5. `Build → Make Project`. `BUILD SUCCESSFUL`. On screen: unchanged (or, with the temporary check, the stars appear on the card).

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

`String.valueOf(movie.getRating())` would work too, but it gives `4.5` for 4.5f and `4.0` for 4f — acceptable. `String.format` gives you exact control over the number of decimals, which matters if the rating comes with more. Don't use `String.format` without a `Locale`: on a phone set to Romanian you'd get `4,5`, while the card design has `4.5`.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 4</summary>

if the stars all look full or all empty, it's not from the code — it's from `stepSize`. With `stepSize="1"`, `setRating(4.5f)` shows 4 or 5 stars, depending on how it rounds internally. `stepSize="0.5"` allows half stars.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added two lines in `bind`. The RatingBar gets a `float`, the TextView gets formatted text.

**Code:** in `MovieViewHolder.bind(Movie movie)`, after the subtitle line:

```java
movieRating.setRating(movie.getRating());
movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));
```

**Why:**
- `RatingBar.setRating(float)` expects exactly the model's type (`float rating`). You don't need a cast.
- `%.1f` = one decimal, rounded. `4.5f` → `4.5`, `4f` → `4.0`, `5f` → `5.0`. Consistent across all cards.
- `Locale.US` fixes the decimal separator to the dot, regardless of the phone's language. It's a design choice: the card has `android:text="4.5"` as an example, so the dot is the screen's visual convention.
- `isIndicator="true"` in the XML makes the stars non-interactive. Without it, the user could change the rating right in the list, and the value would be lost on recycling.

**Remember:**
- `RatingBar` is a subclass of `ProgressBar`; `setRating` is its method, not `setProgress`. `setProgress` would work too (the scale is 0..numStars*100 internally), but it's semantically wrong.
- The two views are bound separately on purpose: the bar is visual, the text is precise. If you bound only the bar, a rating of 4.3 would look identical to 4.5.
- `movieRatingValue` has `android:text="4.5"` in the XML as design text. If `bind` doesn't overwrite it, all cards would show `4.5` — exactly the kind of bug that goes unnoticed at first glance.

**Where it applies:** any visual-value + text-value pair. `SeekBar` + `TextView` with the duration in `ItemActivity` (`tvDurationValue`) is bound the same way, except there the value comes from the control, not from the model.

</details>

---

## Exercise 23.8 — `movieFacts` and the chips with `setVisibility`

**Requirement:** bind the facts line (duration + budget formatted as `$160M`) and the three status chips. Each chip appears only if the movie has that property, and **disappears** if it doesn't.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**How you approach it — your steps:**
1. Open `MovieAdapter.java`, the `bind` method.
2. Add `movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM", movie.getDuration(), movie.getBudget() / 1_000_000));`.
3. For `chipApproval`: take `String approval = movie.getApproval();`. If it's non-null and non-empty, `chipApproval.setText(approval);` and `setVisibility(View.VISIBLE);`. Otherwise just `setVisibility(View.GONE);`.
4. For `chipWatched`: `chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);`.
5. For `chipWatchlist`: `chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);`.
6. Check the `android.view.View` import — it's already there from 23.3.
7. `Build → Make Project`. `BUILD SUCCESSFUL`. On screen: unchanged (or, with the temporary check, the cards are complete).

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 3</summary>

`View.GONE`, not `View.INVISIBLE`. `INVISIBLE` hides the view but keeps its space, so the card is left with an empty stripe under the facts. `GONE` removes it from the layout entirely, and `ChipGroup` rearranges the remaining chips.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck on the budget formatting</summary>

`movie.getBudget()` is a `double` in whole units (`160000000`), not in millions. You divide by `1_000_000` to get to `160`, then format with `%.0f` to cut the decimals. If you forget the division, you get `$160000000M`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added the facts line and the three chips, each with both branches — visible **and** hidden.

**Code:** in `MovieViewHolder.bind(Movie movie)`, after the rating lines:

```java
movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
        movie.getDuration(), movie.getBudget() / 1_000_000));

String approval = movie.getApproval();
if (approval != null && !approval.isEmpty()) {
    chipApproval.setText(approval);
    chipApproval.setVisibility(View.VISIBLE);
} else {
    chipApproval.setVisibility(View.GONE);
}
chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
```

**Why:**
- `%d min  ·  $%.0fM` — `%d` for `int duration`, `%.0f` for `double budget / 1_000_000`. Two spaces around the `·`, to match `android:text="142 min  ·  $160M"` in the XML.
- `Locale.US` for the budget: if you used `Locale.getDefault()` in a language that groups thousands, you could get unwanted separators. Here `%.0f` doesn't group, but fixing the locale is the correct habit for values displayed with a currency symbol.
- `chipApproval` needs **text** in addition to visibility: the XML has `android:text="Approved"` as design text, and the real value comes from `movie.getApproval()` (`"PG-13"`, `"G"`, `"R"`).
- The three chips are independent: a movie can be both approved and watched and on the watchlist.

**Remember:**
- **The recycling trap:** every chip must get **both** branches, `VISIBLE` and `GONE`. If you write only `if (movie.isWatched()) chipWatched.setVisibility(View.VISIBLE);` without an `else`, a recycled row that was "Watched" keeps the chip lit for the next movie too. It's the classic `RecyclerView` bug and the only place in these exercises where you can't see from the code that something is missing.
- `View.INVISIBLE` vs `View.GONE`: the first keeps the space, the second frees it. For chips you want `GONE`.
- `movieStatusGroup` is not touched. `ChipGroup` recalculates its arrangement by itself when a child becomes `GONE`.

**Where it applies:** any conditional element in a `RecyclerView` row — badges, status icons, buttons that appear only for certain items. The rule is always the same: an `if` with both branches, never just the "show" branch.

</details>

---

## Exercise 23.9 — Row click with `getBindingAdapterPosition()` and a callback

**Requirement:** make the row clickable. The adapter receives a listener in the constructor; on click, it calls it with the row's **current** position, not the one from creation. `MainActivity` is not touched yet.

**Files touched:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**How you approach it — your steps:**
1. Open `MovieAdapter.java`.
2. Declare the interface inside `MovieAdapter`, at the top, before the fields: `public interface OnItemClickListener { void onItemClick(int position); }`.
3. Add the field `private final OnItemClickListener listener;`.
4. Change the constructor: `public MovieAdapter(List<Movie> movies, OnItemClickListener listener)`, with `this.listener = listener;`.
5. Change `onBindViewHolder` to call `holder.bind(movies.get(position), listener);`.
6. Change the `bind` signature to `public void bind(Movie movie, OnItemClickListener listener)`.
7. At the end of `bind`, add the click block on `itemView`, with the `getBindingAdapterPosition() != RecyclerView.NO_POSITION` check.
8. `Build → Make Project`. `BUILD SUCCESSFUL`. On screen: unchanged — `MainActivity` doesn't build a `MovieAdapter` yet, so the constructor change breaks nothing.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 7</summary>

the listener is bound in `bind`, **not** in the `ViewHolder` constructor. In the constructor, `getBindingAdapterPosition()` would be evaluated once, when the row is created, and would lag behind on recycling — you'd open the wrong movie after the first scroll.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck on the position check</summary>

`getBindingAdapterPosition()` can return `RecyclerView.NO_POSITION` (that is, `-1`) when the row is being removed or during an animation. Without the `if`, you reach `movies.get(-1)` and get `IndexOutOfBoundsException`. Check **also** for a null listener, if you allow the adapter to be built without one.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the adapter now has a communication channel to the activity. It doesn't know `MainActivity`, `Intent` or `ItemActivity` — just an interface with one method.

**Code:** `MovieAdapter.java` — the parts touched:

```java
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(int position);
    }

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;
    private final OnItemClickListener listener;

    public MovieAdapter(List<Movie> movies, OnItemClickListener listener) {
        this.movies = movies;
        this.listener = listener;
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position), listener);
    }

    // ... onCreateViewHolder, getItemCount ...

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

        // ... the fields and constructor ...

        public void bind(Movie movie, OnItemClickListener listener) {
            // ... the lines from 23.6, 23.7, 23.8 ...

            itemView.setOnClickListener(v -> {
                int pos = getBindingAdapterPosition();
                if (listener != null && pos != RecyclerView.NO_POSITION) {
                    listener.onItemClick(pos);
                }
            });
        }
    }
}
```

**Why:**
- `RecyclerView` **doesn't have** `setOnItemClickListener`. It's a design decision: a row can have several clickable areas, and a global listener would be ambiguous. The solution is your own interface.
- `itemView` is `ViewHolder`'s public field holding the row's root — here the `MaterialCardView` from `movie_item.xml`. A click anywhere on the card triggers the listener.
- `getBindingAdapterPosition()` is evaluated **at click time**, not at `bind`. That's why it's correct even after inserts, deletions or recycling.
- The interface is declared in the adapter, not in `MainActivity`: the adapter defines its contract, the activity implements it. The other way around would mean the adapter depends on the activity.

**Remember:**
- `getBindingAdapterPosition()` is the modern version of `getAdapterPosition()` (deprecated). The difference: the new one accounts for `ConcatAdapter` and for the position in the adapter that produced the row.
- `NO_POSITION` is the constant `-1`. The check is not decorative — without it, a click during an insert animation crashes the app.
- The lambda `v -> { ... }` implements `View.OnClickListener`. The long equivalent is `new View.OnClickListener() { public void onClick(View v) { ... } }`.
- The listener can also be passed as a method reference from the activity (`this::openItem`), but only after 23.10, when the activity builds the adapter.

**Where it applies:** any event in a list row — click, long click, click on a chip, click on the poster. All are bound in `bind`, all use `getBindingAdapterPosition()`, all check for `NO_POSITION`.

</details>

---

## Exercise 23.10 — `MainActivity`: `LayoutManager`, `setAdapter`, `notifyItem*`

**Requirement:** wire the adapter to the `RecyclerView`, delete everything that belonged to `ListView` and `ArrayAdapter`, move the click into the adapter's callback and replace `notifyDataSetChanged()` with `notifyItemInserted` / `notifyItemChanged`.

**Files touched:** `java/ro/ase/ie/g1097/activities/MainActivity.java`

**How you approach it — your steps:**
1. Open `MainActivity.java`. Delete `import android.widget.ArrayAdapter;`.
2. Add the imports `androidx.recyclerview.widget.LinearLayoutManager`, `androidx.recyclerview.widget.RecyclerView` (if missing) and `ro.ase.ie.g1097.adapters.MovieAdapter`.
3. Change the field `private ArrayAdapter<Movie> movieAdapter;` to `private MovieAdapter movieAdapter;`.
4. In `onCreate`, replace `movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);` with `movieAdapter = new MovieAdapter(movies, this::openItem);`.
5. In `initControls()`, after `recyclerView = findViewById(R.id.recyclerView);`, add `recyclerView.setLayoutManager(new LinearLayoutManager(this));` and `recyclerView.setAdapter(movieAdapter);`.
6. In the `launcher` callback: `movieAdapter.notifyDataSetChanged();` in the insert branch becomes `movieAdapter.notifyItemInserted(movies.size() - 1);`; the one in the edit branch becomes `movieAdapter.notifyItemChanged(position);`.
7. Add the method `private void openItem(int position)` that builds the `Intent` to `ItemActivity` with `MOVIE_EXTRA` and `POSITION_EXTRA` and calls `launcher.launch(intent);`.
8. Run it. You should see three cards: **Inception** (Sci-Fi · 2010, 4.5, `148 min · $160M`, chips PG-13 + Watched), **Toy Story** (Animation · 1995, 4.0, `81 min · $30M`, chips G + Watched), **The Matrix** (Action · 1999, 5.0, `136 min · $63M`, chips R + Watchlist). Click a card → the form opens filled in. Save changes → the row updates with an animation. FAB → empty form → save → a new row appears in the list with an animation.

<details markdown="1">
<summary>Hint 1 — if you get stuck at step 8 and the list is empty, with no error in Logcat</summary>

you forgot `setLayoutManager`. It's the only mistake in the whole chapter that doesn't complain at all: `RecyclerView` without a `LayoutManager` doesn't know how to arrange the rows and displays nothing, no exception, no warning.

</details>

<details markdown="1">
<summary>Hint 2 — if you get stuck at step 6</summary>

`notifyItemInserted` wants **the index of the new item**, not the list size. After `movies.add(movie)`, the new item is at `movies.size() - 1`. If you write `notifyItemInserted(movies.size())`, you get `IndexOutOfBoundsException: Inconsistency detected. Invalid item position ... itemCount is ...`.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** the activity no longer knows what `ListView` or `ArrayAdapter` is. It has a `RecyclerView`, a `MovieAdapter` built with a callback, a `LayoutManager` and fine-grained notifications.

**Code:** `MainActivity.java` — the full file after the migration:

```java
package ro.ase.ie.g1097.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.List;

import ro.ase.ie.g1097.adapters.MovieAdapter;
import ro.ase.ie.g1097.model.Movie;
import ro.ase.ie.g1097.R;

public class MainActivity extends AppCompatActivity {

    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";
    private FloatingActionButton fabInsert;
    private RecyclerView recyclerView;
    private ActivityResultLauncher<Intent> launcher;
    private final List<Movie> movies = new ArrayList<>();
    private MovieAdapter movieAdapter;

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

        movieAdapter = new MovieAdapter(movies, this::openItem);
        initControls();
        initListeners();

        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {
                        if (o.getResultCode() == RESULT_OK) {
                            Intent intent = o.getData();
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);
                            if (position == -1) {
                                movies.add(movie);
                                movieAdapter.notifyItemInserted(movies.size() - 1);
                            } else {
                                movies.set(position, movie);
                                movieAdapter.notifyItemChanged(position);
                            }
                        }
                    }
                });
    }

    private void openItem(int position) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }

    private void initListeners() {
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);
                launcher.launch(intent);
            }
        });
    }

    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(movieAdapter);
    }

    private void addSampleMovies() {
        // unchanged from d719ffc — the three sample movies
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
}
```

**Why:**
- `setLayoutManager(new LinearLayoutManager(this))` — `RecyclerView` doesn't know how to arrange anything on its own. `LinearLayoutManager` = vertical list, the visual equivalent of `ListView`. For a grid you'd use `GridLayoutManager(this, 2)`.
- `this::openItem` is a method reference implementing `MovieAdapter.OnItemClickListener`. The long equivalent: `new MovieAdapter.OnItemClickListener() { public void onItemClick(int position) { openItem(position); } }`.
- `openItem` can use `launcher` even though it is declared further down in `onCreate`: the method runs on click, long after `onCreate` has finished. The same logic was in the `ListView` version.
- `notifyItemInserted(movies.size() - 1)` — after `add`, the last index is `size() - 1`. `RecyclerView` animates only the new row, it doesn't rebuild the list.
- `notifyItemChanged(position)` — a single row rebinds, with a transition animation. `movies.set(...)` happens **before** the notification.

**Remember:**
- The "mutate, then notify" order is not stylistic. `notifyItemInserted` before `add` makes `RecyclerView` validate a number of items that doesn't match and throws `Inconsistency detected`.
- `notifyDataSetChanged()` would work too, but it rebuilds everything and cancels the animations. In the exam, if the requirement says "animate the insertion", the answer is `notifyItemInserted`.
- `ArrayAdapter` disappears completely from the activity: field, construction, import. `android.R.layout.simple_list_item_1` no longer exists anywhere — the row is `movie_item.xml`, through `MovieAdapter`.
- The order `movieAdapter = ...` **before** `initControls()` matters: `initControls` calls `setAdapter(movieAdapter)`, so the field must already be built.

**Final check — what you should see on screen:**

| Movie | Subtitle | Rating | Facts | Chips |
|---|---|---|---|---|
| Inception | Sci-Fi · 2010 | 4.5 | 148 min · $160M | PG-13, Watched |
| Toy Story | Animation · 1995 | 4.0 | 81 min · $30M | G, Watched |
| The Matrix | Action · 1999 | 5.0 | 136 min · $63M | R, Watchlist |

Plus: click a card → the form opens with the movie's data and the button reads "Update Movie"; save → the row changes with an animation; FAB → empty form → save → a new row at the end of the list, with an insert animation.

**Where it applies:** any list in a modern Android app. The `setLayoutManager` + `setAdapter` + fine-grained notifications template is identical for any model; only the adapter and the row layout change. If the exam also asks for `ItemTouchHelper` (swipe-to-delete), it attaches exactly on the `recyclerView`, after `setAdapter`.

</details>

---

## Recap — what was touched, in order

| Step | File | What was added | Compiles | Visible on screen |
|---|---|---|---|---|
| 23.1 | `libs.versions.toml`, `build.gradle.kts` | the `recyclerview` dependency | yes | nothing |
| 23.2 | `activity_main.xml`, `MainActivity` | the widget + the field type | yes | empty screen + FAB |
| 23.3 | `MovieAdapter.java` (new) | the class + 3 methods | yes | nothing |
| 23.4 | `MovieAdapter.java` | `MovieViewHolder` + `findViewById` | yes | nothing |
| 23.5 | `MovieAdapter.java` | `inflate(movie_item)` | yes | nothing |
| 23.6 | `MovieAdapter.java` | title + subtitle | yes | nothing |
| 23.7 | `MovieAdapter.java` | rating + value | yes | nothing |
| 23.8 | `MovieAdapter.java` | facts + 3 chips | yes | nothing |
| 23.9 | `MovieAdapter.java` | the click interface | yes | nothing |
| 23.10 | `MainActivity.java` | `LayoutManager` + `setAdapter` + `notifyItem*` | yes | **the complete list** |

**Three mistakes that cost points in the exam:**
1. `RecyclerView` without `setLayoutManager` — empty list, zero errors. There's no way to debug it from Logcat.
2. Chips without the `else` branch in `bind` — recycled rows keep the previous movie's status.
3. `notifyItemInserted(movies.size())` instead of `movies.size() - 1` — `Inconsistency detected`, only when you insert, not at startup.
