# Chapter 21 — Cheatsheet: modules, classes and recipes

**Goal:** a dense reference. Everything that can be asked on the test, with the exact code and with "when you use it".

**Estimated time:** 30 min reading, then you come back to it like to any cheatsheet.

> **How to use it:** you don't read it cover to cover before the test. You skim it once now, then when you get stuck in an exercise you look up the section.

---

## 21.1 The G1097 file map

```
G1097/
├── build.gradle.kts                  namespace, minSdk 33, viewBinding=true
└── src/main/
    ├── AndroidManifest.xml           declares MainActivity + ItemActivity
    ├── java/ro/ase/ie/g1097/
    │   ├── model/Movie.java          THE DATA. No android.* imports
    │   ├── activities/MainActivity.java   THE LIST + navigation
    │   └── activities/ItemActivity.java   THE FORM
    └── res/
        ├── layout/activity_main.xml  FrameLayout + ListView + FAB
        ├── layout/activity_item.xml  ScrollView + 4 cards + button
        ├── layout/movie_item.xml     the row card (for RecyclerView)
        ├── values/strings.xml        app_name, items, movie_genre
        ├── values/themes.xml         Theme.Material3.DayNight.NoActionBar
        └── values-night/themes.xml   the dark variant
```

**The golden rule:** `model` doesn't know what a widget is. `activities` don't contain per-row display logic. `adapters` don't know what an `Activity` is.

---

## 21.2 The `Movie` model — how you add an attribute

### The existing fields and why they have their type

| Field | Type | Source widget | Why this type |
|---|---|---|---|
| `title` | `String` | `TextInputEditText` | free text |
| `release` | `Date` | `TextInputEditText` + `DatePickerDialog` | a date, so you can compute with it |
| `genre` | `String` | `Spinner` | one of 10 texts |
| `budget` | `double` | `TextInputEditText` (`numberDecimal`) | money with decimals |
| `duration` | `int` | `SeekBar` | progress is `int` |
| `rating` | `float` | `RatingBar` | `getRating()` returns `float` |
| `watched` | `boolean` | `MaterialSwitch` | checkbox |
| `approval` | `String` | `RadioGroup` | the text of the selected button |
| `onWatchlist` | `boolean` | `MaterialCheckBox` | checkbox |
| `poster` | `String` | `TextInputEditText` (`textUri`) | URL |

### The recipe: you add a new attribute (5 steps, in this order)

```java
// 1. Movie.java
private String writer;
public String getWriter() { return writer; }
public void setWriter(String writer) { this.writer = writer; }
// + add it to the constructor with 10 arguments (it becomes 11)

// 2. activity_item.xml — a TextInputLayout + TextInputEditText with android:id="@+id/etWriter"

// 3. ItemActivity.java
etWriter = findViewById(R.id.etWriter);          // initControls
etWriter.setText(existing.getWriter());          // fillForm
movie.setWriter(etWriter.getText().toString());  // saveMovie

// 4. movie_item.xml — a TextView with android:id="@+id/movieWriter"

// 5. MovieAdapter.java (if you use RecyclerView)
movieWriter = itemView.findViewById(R.id.movieWriter);   // ViewHolder
movieWriter.setText(movie.getWriter());                  // bind()
```

**If you stay on `ListView` + `ArrayAdapter`:** steps 4 and 5 disappear. But then the attribute is only visible through `toString()`:

```java
@Override
public String toString() {
    return title + " — " + writer + " (" + rating + ")";
}
```

> **Why the order matters:** the model first, the UI after. If you start with the XML, the code doesn't compile until you add the field.

### Attribute types and which widget produces them

| Type | Widget | How you read it |
|---|---|---|
| `String` | `EditText` | `getText().toString()` |
| `String` (from a list) | `Spinner` | `getSelectedItem().toString()` |
| `int` | `SeekBar` | `getProgress()` |
| `int` (from text) | `EditText` | `Integer.parseInt(getText().toString())` |
| `double` | `EditText` | `Double.parseDouble(getText().toString())` |
| `float` | `RatingBar` | `getRating()` |
| `boolean` | `Switch` / `CheckBox` | `isChecked()` |
| `ArrayList<String>` | `EditText` | `Arrays.asList(text.split(","))` |
| `String` (single choice) | `RadioGroup` | you iterate the children, `rb.isChecked()` |

---

## 21.3 Layouts — which widget you put and how you reference it

### IDs: how you give them and how you get them

```xml
<!-- in XML -->
<Button
    android:id="@+id/btnClear"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Clear" />
```

```java
// in the code
Button btnClear = findViewById(R.id.btnClear);
```

**Rules:**
- `@+id/` = "create the ID if it doesn't exist". Only on the first occurrence.
- The name from XML becomes `R.id.<name>` exactly.
- Without `android:id` → you can't reference the view from the code.
- A wrong ID = **compile error** (`cannot find symbol variable`).
- A correct ID but the view in another layout = **`null`** at runtime.

### The prefix convention in the repo

| Prefix | Widget | Example |
|---|---|---|
| `et` | `EditText` / `TextInputEditText` | `etTitle` |
| `tv` | `TextView` | `tvDurationValue` |
| `sp` | `Spinner` | `spGenre` |
| `sb` | `SeekBar` | `sbDuration` |
| `rb` | `RatingBar` / `RadioButton` | `rbRating`, `rbGeneral` |
| `rg` | `RadioGroup` | `rgApproval` |
| `cb` | `CheckBox` | `cbOnWatchList` |
| `sw` | `Switch` | `swWatched` |
| `btn` / `bt` | `Button` | `btnMovieAction` |
| `fab` | `FloatingActionButton` | `fabInsert` |

> It isn't a rule of the language, it's a reading convention. But the repo has inconsistencies (`cbonWatchList` vs `cbOnWatchList`, `btMovieAction` vs `btnMovieAction`) — follow them exactly.

### Extracting the text from the layout

```java
String text = etTitle.getText().toString();       // EditText
String text = tvSomeLabel.getText().toString();   // TextView
String genre = spGenre.getSelectedItem().toString(); // Spinner
```

### The most used attributes

| Attribute | Values | Effect |
|---|---|---|
| `layout_width` / `layout_height` | `match_parent`, `wrap_content`, `0dp`+weight | size |
| `layout_weight` | number | splits the remaining space |
| `layout_gravity` | `bottom\|end` etc. | the position of the **element** in the parent |
| `gravity` | `center_vertical` etc. | the position of the **content** in the element |
| `padding` / `margin` | `16dp` | inside / outside |
| `textAppearance` | `?attr/textAppearanceBodyLarge` | typography from the theme |
| `textColor` | `?attr/colorOnSurface` | color from the theme |
| `inputType` | `textCapWords`, `numberDecimal`, `date`, `textUri` | keyboard + restriction |
| `visibility` | `visible`, `invisible`, `gone` | `GONE` takes no space |

---

## 21.4 `findViewById` vs `ViewBinding`

### `findViewById` (what the repo uses)

```java
setContentView(R.layout.activity_item);
etTitle = findViewById(R.id.etTitle);   // after setContentView, otherwise null
```

**Advantage:** explicit, you see the `R.id` ↔ XML link.
**Disadvantage:** it isn't type-safe, it can return `null`, lots of repetitive code.

### `ViewBinding` (the modern alternative)

```java
// build.gradle.kts
buildFeatures { viewBinding = true }

// in the Activity
ActivityItemBinding binding = ActivityItemBinding.inflate(getLayoutInflater());
setContentView(binding.getRoot());
binding.etTitle.setText("Dune");   // generated field, exact type, never null
```

**Advantage:** type-safe, no `findViewById`, safe refactoring.
**Disadvantage:** less explicit for learning.

> **The repo has `viewBinding = true` but doesn't use it.** If the test asks you to migrate, you know what to do — and you know how to explain why it isn't used.

---

## 21.5 Listeners — the complete table

| Widget | Method | Methods to implement | Lambda? |
|---|---|---|---|
| `Button` | `setOnClickListener` | 1 (`onClick`) | **yes** |
| `ListView` | `setOnItemClickListener` | 1 (`onItemClick`) | **yes** |
| `ListView` | `setOnItemLongClickListener` | 1 (`onItemLongClick`) → `boolean` | **yes** |
| `Switch`, `CheckBox`, `ToggleButton`, `RadioButton` | `setOnCheckedChangeListener` | 1 (`onCheckedChanged`) | **yes** |
| `RadioGroup` | `setOnCheckedChangeListener` | 1 (`onCheckedChanged(group, checkedId)`) | **yes** |
| `SeekBar` | `setOnSeekBarChangeListener` | **3** | **no** |
| `RatingBar` | `setOnRatingBarChangeListener` | 1 | **yes** |
| `EditText` | `addTextChangedListener` | 3 (`beforeTextChanged`, `onTextChanged`, `afterTextChanged`) | **no** |
| `Toolbar` | `setOnMenuItemClickListener` | 1 → `boolean` | **yes** |

**The rule:** a single abstract method = functional interface = lambda allowed.

### The two styles

```java
// anonymous class (repo)
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});

// lambda (equivalent)
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

> **`this` in an anonymous class** = the anonymous class → you need `MainActivity.this`. **`this` in a lambda** = the outer class → `this` is enough.

---

## 21.6 Adapters — which, when, how

### The decision tree

```
Do you have a list of objects?
├── yes
│   ├── Does the row have a SINGLE text?
│   │   └── ArrayAdapter  →  new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, list)
│   ├── Does the row have several views?
│   │   └── you need your own adapter
│   │       ├── on ListView  →  BaseAdapter with getView() + ViewHolder + setTag
│   │       └── on RecyclerView → RecyclerView.Adapter + ViewHolder + onCreate/onBind
│   └── ...
└── no → you don't need an adapter
```

### `ArrayAdapter` (what the repo uses)

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
listView.setAdapter(movieAdapter);
```

- It calls `toString()` on each element.
- **A single** `TextView` per row.
- After any change to the list: `movieAdapter.notifyDataSetChanged();`

### `BaseAdapter` for `ListView` (two columns)

```java
public class MovieListAdapter extends BaseAdapter {
    private static class ViewHolder {
        TextView tvTitle;
        TextView tvSubtitle;
    }

    private final List<Movie> movies;
    private final LayoutInflater inflater;

    public MovieListAdapter(Context context, List<Movie> movies) {
        this.inflater = LayoutInflater.from(context);
        this.movies = movies;
    }

    @Override public int getCount() { return movies.size(); }
    @Override public Movie getItem(int position) { return movies.get(position); }
    @Override public long getItemId(int position) { return position; }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = inflater.inflate(R.layout.movie_item, parent, false);
            holder = new ViewHolder();
            holder.tvTitle = convertView.findViewById(R.id.movieTitle);
            holder.tvSubtitle = convertView.findViewById(R.id.movieSubtitle);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }
        Movie movie = getItem(position);
        holder.tvTitle.setText(movie.getTitle());
        holder.tvSubtitle.setText(movie.getGenre());
        return convertView;
    }
}
```

> **`convertView` + `ViewHolder` + `setTag`/`getTag`** = recycling. Without them, `findViewById` on every scroll.

### `RecyclerView.Adapter` (when you want animations and flexibility)

```java
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) { this.movies = movies; }

    @NonNull @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position));
    }

    @Override public int getItemCount() { return movies.size(); }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {
        private final TextView movieTitle;

        public MovieViewHolder(@NonNull View itemView) {
            super(itemView);
            movieTitle = itemView.findViewById(R.id.movieTitle);
        }

        public void bind(Movie movie) {
            movieTitle.setText(movie.getTitle());
        }
    }
}
```

Plus in `MainActivity`:

```java
RecyclerView recyclerView = findViewById(R.id.recyclerView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));   // MANDATORY
recyclerView.setAdapter(movieAdapter);
```

### The `BaseAdapter` ↔ `RecyclerView.Adapter` correspondence

| `BaseAdapter` | `RecyclerView.Adapter` | When it runs |
|---|---|---|
| `getCount()` | `getItemCount()` | when needed |
| `getView()`, the `if (convertView == null)` part | `onCreateViewHolder()` | once per created row |
| `getView()`, the `setText` part | `onBindViewHolder()` | on every display |
| `ViewHolder` + manual `setTag`/`getTag` | automatic `RecyclerView.ViewHolder` | — |

### Notifications

| Method | When | Effect |
|---|---|---|
| `notifyDataSetChanged()` | any change | rebuilds everything (no animations) |
| `notifyItemInserted(pos)` | you added at `pos` | animates the insertion |
| `notifyItemChanged(pos)` | you modified at `pos` | animates the change |
| `notifyItemRemoved(pos)` | you deleted from `pos` | animates the deletion |

> **The order:** first you modify the list, **then** you notify. Otherwise `IndexOutOfBoundsException`.

---

## 21.7 Intents and results

### A simple launch (without a result)

```java
Intent intent = new Intent(this, ItemActivity.class);
startActivity(intent);
```

### Launching with a result (what the repo uses)

```java
// MainActivity
private ActivityResultLauncher<Intent> launcher;

launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
        result -> {
            if (result.getResultCode() == RESULT_OK) {
                Intent data = result.getData();
                Movie movie = IntentCompat.getSerializableExtra(data, MOVIE_EXTRA, Movie.class);
                int position = data.getIntExtra(POSITION_EXTRA, -1);
                if (position == -1) movies.add(movie);
                else movies.set(position, movie);
                movieAdapter.notifyDataSetChanged();
            }
        });

// sending
Intent intent = new Intent(this, ItemActivity.class);
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);
launcher.launch(intent);
```

```java
// ItemActivity — sending the result
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

### The keys and the constants

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
```

> **The classic mistake:** you write `"movie"` in one place and `"Movie"` in another → you get `null` with no error. Hence the constants.

### What has to be serializable

```java
public class Movie implements Serializable { ... }
```

`String`, `Date`, the primitives — yes. `Context`, `Drawable` — no.

> **The object you receive is a COPY**, not the same reference. That's why the edit screen sends a result back instead of modifying directly.

---

## 21.8 The lifecycle

```
START:     onCreate → onStart → onResume
HOME:      onPause → onStop
RETURN:    onRestart → onStart → onResume
BACK:      onPause → onStop → onDestroy
ROTATION:  onPause → onStop → onDestroy → onCreate → onStart → onResume
```

| Method | What you do |
|---|---|
| `onCreate` | `setContentView`, `findViewById`, initializations |
| `onStart` | register system listeners |
| `onResume` | start animations, camera |
| `onPause` | stop animations, quick save |
| `onStop` | release resources |
| `onDestroy` | cancel callbacks |

### Keeping state on rotation

```java
@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putString("title", etTitle.getText().toString());
    outState.putInt("duration", sbDuration.getProgress());
}

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_item);
    initControls();
    if (savedInstanceState != null) {
        etTitle.setText(savedInstanceState.getString("title"));
        sbDuration.setProgress(savedInstanceState.getInt("duration"));
    }
}
```

---

## 21.9 Widgets: reading and writing

| Widget | You read | You write | Listener |
|---|---|---|---|
| `EditText` | `getText().toString()` | `setText(String)` | `addTextChangedListener` |
| `TextView` | `getText().toString()` | `setText(CharSequence)` | — |
| `Spinner` | `getSelectedItem().toString()` | `setSelection(int)` | `setOnItemSelectedListener` |
| `SeekBar` | `getProgress()` | `setProgress(int)` | `setOnSeekBarChangeListener` |
| `RatingBar` | `getRating()` | `setRating(float)` | `setOnRatingBarChangeListener` |
| `Switch` / `CheckBox` | `isChecked()` | `setChecked(boolean)` | `setOnCheckedChangeListener` |
| `RadioGroup` | `getCheckedRadioButtonId()` or you iterate the children | `check(int id)` | `setOnCheckedChangeListener` |
| `Button` | — | `setText(...)`, `setEnabled(bool)` | `setOnClickListener` |
| any `View` | — | `setVisibility(View.GONE)` | — |

### `RadioGroup` — the two ways of reading it

```java
// way 1: with checkedId (direct)
int checkedId = rgApproval.getCheckedRadioButtonId();
RadioButton rb = findViewById(checkedId);
String approval = rb.getText().toString();

// way 2: iterating the children (what the repo uses — it also works if you add buttons)
for (int i = 0; i < rgApproval.getChildCount(); i++) {
    RadioButton rb = (RadioButton) rgApproval.getChildAt(i);
    if (rb.isChecked()) {
        movie.setApproval(rb.getText().toString());
        break;
    }
}
```

> Way 2 is more robust: you add a button in XML, the code sees it without changes.

---

## 21.10 Frequent errors and their cause

| Symptom | Cause | Fix |
|---|---|---|
| `NullPointerException` in `initControls` | `findViewById` before `setContentView` | move the call after it |
| `NullPointerException` at `setAdapter` | `movieAdapter` not initialized | create the adapter first |
| Empty list, no error | you forgot `setAdapter` | add it |
| The movie doesn't appear after Save | you forgot `notifyDataSetChanged()` | add it |
| `NumberFormatException` at Save | empty numeric field | `if (!text.isEmpty())` + `try/catch` |
| `NullPointerException` when editing | `release` is `null` | `if (existing.getRelease() != null)` |
| `ClassNotFoundException` at launch | the activity isn't in the manifest | declare it |
| `ActivityNotFoundException` | the class doesn't exist or the name is wrong | check `android:name` |
| Spinner on the wrong first option | the text isn't in the list | check `movie_genre` |
| `Resources$NotFoundException` | wrong theme name | check `themes.xml` + manifest |
| `ScrollView can host only one direct child` | two children | put a `LinearLayout` |
| "Cannot resolve symbol R" | the build failed | Build → Clean + Rebuild |

---

## 21.11 Quick recipes for the exam

### "Add an attribute X and show it in the list"

1. `Movie.java`: field + getter + setter + in the constructor
2. `activity_item.xml`: widget with `android:id`
3. `ItemActivity`: `findViewById` + `fillForm` + `saveMovie`
4. `movie_item.xml`: `TextView` with an id (if it's a RecyclerView) **or** `toString()` (if it's a ListView)
5. Adapter: `findViewById` in the `ViewHolder` + `setText` in `bind`

### "Swap one widget for another"

1. XML: replace the tag, keep `android:id` (or change it in the code too)
2. Code: change the field type (`EditText` → `SeekBar`)
3. Code: change the reading (`getText()` → `getProgress()`)
4. Code: change the writing (`setText()` → `setProgress()`)
5. Code: change the listener if needed

### "Make an adapter"

1. Create `adapters/MovieAdapter.java`
2. `onCreateViewHolder` → inflate the layout + `ViewHolder`
3. `onBindViewHolder` → `holder.bind(movie)`
4. `getItemCount` → `movies.size()`
5. In `MainActivity`: `setLayoutManager` + `setAdapter`

### "Add a button"

1. XML: `<Button android:id="@+id/btnX" ... />`
2. `findViewById`
3. `setOnClickListener`
4. In the listener: what it has to do

### "Make the value from a widget appear in a label"

1. Get the widget and the label with `findViewById`
2. Attach the right listener to the widget
3. In the listener: `label.setText(...)`
4. If you also want it at initialization: call the same logic in `onCreate` or set it in XML

---

## 21.12 What to say on the test when you're asked to "explain"

| Question | The short answer |
|---|---|
| Why `Movie implements Serializable`? | so that it can be sent through `Intent.putExtra` between activities |
| Why is the received object a copy? | `Intent` serializes/deserializes |
| Why `isWatched()` and not `getWatched()`? | the JavaBeans convention for `boolean` |
| Why `Arrays.asList()` in an `EditText`? | a text field holds a single string; the list is split by comma |
| Why `View.GONE` and not `INVISIBLE`? | `GONE` takes no space |
| Why `notifyDataSetChanged()`? | the adapter doesn't observe the list on its own |
| Why `setLayoutManager` on `RecyclerView`? | otherwise it doesn't know how to arrange the rows |
| Why `ViewHolder`? | a cache of references, so you don't look up the views on every scroll |
| Why `calendar` for the date? | `Date` is just a `long`, `Calendar` knows how to build from day/month/year |
| Why `Calendar.JULY` = 6? | the months are indexed from 0 |

---

## Chapter 21 summary

- Model → form → activity → card → adapter. Always in this order.
- `findViewById` after `setContentView`. A wrong ID = compile error; a missing ID = `null` at runtime.
- One abstract method = lambda. Three methods (`SeekBar`, `TextWatcher`) = anonymous class.
- `ArrayAdapter` for one text; your own adapter for several views.
- `notifyDataSetChanged()` after any change to the list.
- `Intent` with a result: `registerForActivityResult` + `setResult(RESULT_OK)`.
- Rotation destroys the activity — save in `onSaveInstanceState`.

**Next chapter:** [22 - Codul adnotat.md](22%20-%20Codul%20adnotat.md)
