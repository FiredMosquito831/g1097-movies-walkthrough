# Chapter 35 — Recipes 3: Intents, persistence, lifecycle

**Objective:** to be able to solve, in 10–15 minutes each, the exam requirements that are not about layout and not about adapters, but about **how data moves**: how an object leaves one screen, how it comes back modified, what happens when you press Back, what survives a rotation and what survives closing the app. This is where most marks are lost, because nothing crashes: the data simply does not arrive where it should.

**Reference app:** G1097 (Movies), commit `d719ffc`. Two activities — `MainActivity` (the list) and `ItemActivity` (the form) — a serializable model (`Movie`, 10 fields) and a list kept in memory: `private final List<Movie> movies = new ArrayList<>();`.

**The three families of requirements in this chapter:**

| Family | The recipes | The question it answers |
|---|---|---|
| Navigation and data between screens | 35.1 – 35.8 | "How does the movie get to the other screen, and how does it come back?" |
| Persistence | 35.9 – 35.11 | "What is lost on rotation? What is lost on close? How do I prove it?" |
| Lifecycle and debug | 35.12 – 35.13 | "In what order are the methods called, and why does the result not arrive?" |

**How each recipe is built.** They all have exactly the same seven sections, in the same order: the requirement as it sounds in the test, the files touched (with what is mandatory and what is "only if"), the numbered steps with complete code, the explanation of the mechanism, the mistake that costs marks, the check on the emulator and the exercises to practise. You can read any recipe on its own — the context is repeated briefly where needed.

**The golden rule of the chapter:** in Android, data is not "visible" from one screen to another. Every crossing is a **serialized copy** placed in a `Bundle`, and every return is a **code + an `Intent`** that the calling screen must read explicitly. There is no shared memory between activities, and when the process dies there is nothing left. All 13 recipes are variations on this theme.

**The starting state** — the full chain, as it exists in the code:

```text
MainActivity                          ItemActivity
------------                          ------------
fabInsert.onClick
  new Intent(MainActivity.this, ItemActivity.class)
  launcher.launch(intent)  --------->  onCreate
                                         intent without MOVIE_EXTRA
                                         existing == null -> position = -1
                                       saveMovie()
                                         new Movie() from the widgets
                                         setResult(RESULT_OK, intent)
                                         finish()
  callback  <-------------------------  { MOVIE_EXTRA, without POSITION_EXTRA }
  position == -1 -> movies.add(...)

listView.onItemClick(position)
  putExtra(MOVIE_EXTRA, movies.get(position))
  putExtra(POSITION_EXTRA, position)
  launcher.launch(intent)  --------->  onCreate
                                         existing != null
                                         position = position
                                         fillForm(existing)
                                       saveMovie()
                                         setResult(RESULT_OK, intent)
                                         finish()
  callback  <-------------------------  { MOVIE_EXTRA, POSITION_EXTRA }
  position != -1 -> movies.set(position, movie)
```

**Conventions.** The UI texts stay in English, as in the app (`"Save Movie"`, `"Update Movie"`, `"Edit movie"`). The prose, the code comments and the explanations are in Romanian. The field and identifier names are exactly the ones in `src-G1097` — including the asymmetries: the field is called `cbonWatchList`, but the id is `cbOnWatchList`; the field is `btMovieAction`, but the id is `btnMovieAction`. In the exam, one wrong letter in a `findViewById` does not give a compile error, it gives `null` at runtime.

---

## Recipe 35.1 — Start another activity

**The requirement, as it sounds in the test:** "When the user taps a row in the list, open the movie's detail screen."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `AndroidManifest.xml` | check that `ItemActivity` is declared with `android:name=".activities.ItemActivity"` | yes — a check, not a change |
| 2 | `activities/MainActivity.java` | build the explicit `Intent` and call `startActivity` / `launcher.launch` in `initListeners()` | yes |
| 3 | `activities/ItemActivity.java` | only if you add a new screen: `onCreate` + `setContentView` | only if the screen does not exist |
| 4 | `res/layout/activity_item.xml` | only if you add a new screen: its layout | only if the screen does not exist |

**The steps, in order:**

**Step 1 — check the manifest.** An activity that is not declared in `AndroidManifest.xml` cannot be started, however correct the `Intent` is. In G1097, the two activities are already there:

```xml
<activity
    android:name=".activities.MainActivity"
    android:exported="true"
    android:windowSoftInputMode="adjustResize">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
<activity
    android:name=".activities.ItemActivity"
    android:exported="false"
    android:windowSoftInputMode="adjustResize" />
```

`android:exported="false"` means: only your app can start `ItemActivity`. That is exactly what you want for an internal screen. `android:exported="true"` is mandatory only for the activity with `MAIN`/`LAUNCHER`, the one that appears in the launcher.

**Step 2 — build the `Intent` in `MainActivity.initListeners()`.** The exact place is the listener that already exists on the list:

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        startActivity(intent);
    }
});
```

Three things matter in those two lines:

- `MainActivity.this`, not `this`. We are inside an anonymous class (`new AdapterView.OnItemClickListener() { ... }`), so `this` would mean the listener, not the activity. `new Intent(this, ItemActivity.class)` does not compile there — the constructor asks for a `Context`, and `OnItemClickListener` is not one. If you use a lambda, `this` becomes the activity again and the confusion disappears.
- `ItemActivity.class` — the second parameter is the **target** class, not a string with its name. Android turns it into a `ComponentName` at start-up.
- `startActivity(intent)` — no result. The new screen appears on top, `MainActivity` stays alive in the back stack.

**Step 3 — the version from the app, with a result.** G1097 does not use `startActivity` for `ItemActivity`, but an `ActivityResultLauncher`, because it needs the movie back:

```java
Intent intent = new Intent(MainActivity.this, ItemActivity.class);
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);
launcher.launch(intent);
```

The difference at runtime is only who receives the answer: `startActivity` throws it away, `launcher.launch` sends it to the registered callback. The start itself is identical. Recipe 35.4 shows the registration of the launcher; here just remember that **the same `Intent`** goes in both cases.

**Step 4 — if you add a new screen.** In `ItemActivity`, the minimum skeleton that shows on screen is:

```java
public class ItemActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_item);
    }
}
```

Plus the manifest entry from step 1, with the correct package name: `.activities.ItemActivity` means `ro.ase.ie.g1097.activities.ItemActivity`.

**What happens at runtime, in order:**

```text
tap the row
  MainActivity.onPause
  ItemActivity.onCreate -> onStart -> onResume
  MainActivity.onStop            (stays in the back stack, not destroyed)

press Back in ItemActivity
  ItemActivity.onPause -> onStop -> onDestroy
  MainActivity.onRestart -> onStart -> onResume
```

**Why it works this way:** the explicit `Intent` is not "a link", it is a **request to the system**. `startActivity` sends the request to `ActivityManager`, which checks in the manifest that `ItemActivity` exists and that you are allowed to start it, then creates a new instance of the class. The two activities do not know each other directly: they share no fields, no memory, no reference. `MainActivity` is not destroyed when it leaves — it stays in the back stack, in the `stopped` state, and on `Back` it is merely restarted (`onRestart`), not recreated. That is why the list stays intact when you come back: the `MainActivity` object existed the whole time.

**The mistake that costs marks:**

1. **You forget the manifest entry.** Symptom: the app crashes when you tap the row, with `android.content.ActivityNotFoundException: Unable to find explicit activity class {ro.ase.ie.g1097/ro.ase.ie.g1097.activities.ItemActivity}; have you declared this activity in your AndroidManifest.xml?`. Cause: you created the class but did not declare it.
2. **You write `new Intent(this, ...)` in an anonymous class.** Symptom: compile error, `Intent(android.content.Context, java.lang.Class<?>)` does not apply. Cause: `this` is the listener. Fix: `MainActivity.this`.
3. **You use `startActivity` where the requirement says "return".** Symptom: the screen opens, you save, you come back and the list does not change — with no error at all. Cause: `startActivity` has no callback; the result is lost. You need `launcher.launch` (35.4).

**The check:** you run the app, tap "Inception" in the list. The screen with the form must appear, and the top bar must say "Edit movie". You press Back: you return to the list, the three rows are still there, in the same order. Then you tap the "+" FAB: the same screen, but with "Movie details" in the top bar and an empty form — proof that the screen is the same, only the extras differ.

**Practise:** [20.7](cap-20.html#ex-20-7) (an "Edit" button in the card, instead of tapping the row), [23.9](cap-23.html#ex-23-9) (a row click with the position and a callback, in the `RecyclerView` version).

---

## Recipe 35.2 — Send simple values through an Intent

**The requirement, as it sounds in the test:** "Send the title of the tapped movie to the detail screen and show it in the title bar."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | add the key constant and the `putExtra` in `initListeners()` | yes |
| 2 | `activities/ItemActivity.java` | read the value in `onCreate()` and display it | yes |
| 3 | `res/values/strings.xml` | only if you want the text in a string resource | no |

**The steps, in order:**

**Step 1 — put the key in a constant, in `MainActivity`.** Next to the two that already exist:

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
protected static final String TITLE_EXTRA = "title";
```

`protected static final` is not decoration: `ItemActivity` is in the same package (`ro.ase.ie.g1097.activities`), so it sees the constant without an import and without declaring it a second time. A single source for a string that must be identical in two files.

**Step 2 — put the value in the `Intent`, in `MainActivity.initListeners()`:**

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, movies.get(position).getTitle());
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }
});
```

An `Intent` can carry any number of extras; they do not overwrite each other as long as the keys differ. The order in which you put them does not matter.

**Step 3 — read the value in `ItemActivity.onCreate()`, after `initControls()`:**

```java
Intent intent = getIntent();
String title = intent.getStringExtra(MainActivity.TITLE_EXTRA);
if (title != null) {
    setTitle(title);
}
```

`getIntent()` returns the `Intent` with which the activity was started. It stays valid for the whole life of the activity, including after a rotation — that is why it does not need to be saved in a `Bundle`.

**Step 4 — the table of methods, by type.** The pairs are fixed; there is no automatic conversion between types:

| What you send | What you write in the sender | What you read in the receiver | Value if missing |
|---|---|---|---|
| `String` | `putExtra(KEY, "Inception")` | `getStringExtra(KEY)` | `null` |
| `int` | `putExtra(KEY, 148)` | `getIntExtra(KEY, -1)` | the default you give |
| `long` | `putExtra(KEY, 160000000L)` | `getLongExtra(KEY, 0L)` | the default you give |
| `float` | `putExtra(KEY, 4.5f)` | `getFloatExtra(KEY, 0f)` | the default you give |
| `boolean` | `putExtra(KEY, true)` | `getBooleanExtra(KEY, false)` | the default you give |
| any object | `putExtra(KEY, movie)` | `IntentCompat.getSerializableExtra(...)` | `null` (35.3) |

Notice the asymmetry: `getStringExtra` has no default parameter, because `null` is a valid answer for a string. The rest mandatorily have a default, because primitives cannot be `null`.

**Step 5 — check that the key exists, if the default is not enough:**

```java
if (intent.hasExtra(MainActivity.TITLE_EXTRA)) {
    setTitle(intent.getStringExtra(MainActivity.TITLE_EXTRA));
}
```

`hasExtra` returns `true` even if the value put there is `null`, so it does not replace the `!= null` check; it complements it when you want to tell "the key is missing" from "the key exists with an empty value".

**Why it works this way:** an `Intent` is, at its base, a `Bundle` — a `String -> value` map that knows how to serialize itself. When you call `launcher.launch`, the system copies the bundle, hands it to another process or to the same process, and rebuilds it before `ItemActivity.onCreate`. That is why the key must be **identical** at both ends: there is no compile-time check between `putExtra("title", ...)` and `getStringExtra("Title")`, and the result is `null`, not an exception. The constant removes exactly this class of bugs. The default in `getIntExtra` is the mechanism by which the app code tells the two modes apart: `position` is missing on insert, so it becomes `-1`, and `-1` is exactly the "insert mode" convention in `ItemActivity`.

**The mistake that costs marks:**

1. **A key spelled differently at the two ends.** Symptom: `title` is `null`, `setTitle` is not called, the top bar stays "G1097" — with no error in Logcat. Cause: `"Title"` in one file, `"title"` in the other. Fix: the constant from step 1.
2. **You read with the method of another type.** Symptom: `getIntExtra` on a `String` extra returns `0` and Logcat shows a `W/Bundle: Key ... expected Integer but value was a java.lang.String`; conversely, `getStringExtra` on an `int` returns `null`. It does not crash, it just does not work. Cause: you changed the type on one side and forgot the other.
3. **You forget the right default.** Symptom: the position read is `0` instead of `-1`, and saving does `set(0, movie)` instead of `add(movie)` — the first movie is replaced. Cause: `getIntExtra(POSITION_EXTRA, 0)` instead of `-1`.

**The check:** you tap "Inception" — the top bar shows "Inception"; you press Back, then tap "Toy Story" — the bar shows "Toy Story". You tap the "+" FAB: the bar stays "Movie details", because `TITLE_EXTRA` is missing and `title` is `null`. If you see "null" written in the bar, you put the value in the `Intent` without checking `!= null`.

**Practise:** [17.1](cap-17.html#ex-17-1) (the `String` attribute that must get from the form into the list), [19.5](cap-19.html#ex-19-5) (a value computed in one screen and shown right after Save).

---

## Recipe 35.3 — Send a whole object (Serializable)

**The requirement, as it sounds in the test:** "Send the tapped movie, whole, so that the edit form is filled with its values."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `model/Movie.java` | check `implements Serializable` and that all 10 fields are serializable | yes — a check |
| 2 | `activities/MainActivity.java` | `putExtra(MOVIE_EXTRA, movies.get(position))` + `putExtra(POSITION_EXTRA, position)` | yes |
| 3 | `activities/ItemActivity.java` | `IntentCompat.getSerializableExtra(...)` + the `!= null` guard | yes |
| 4 | `activities/MainActivity.java` | `import androidx.core.content.IntentCompat;` | yes, if you use the modern version |

**The steps, in order:**

**Step 1 — check the model.** The class must implement `Serializable` and have a no-argument constructor:

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;
import java.util.Date;

public class Movie implements Serializable {
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

    public Movie() {
    }

    public Movie(String title, Date release, String genre, double budget, int duration,
                 float rating, boolean watched, String approval, boolean onWatchlist, String poster) {
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

    // getters and setters
}
```

All 10 types are serializable: `String` and the primitives are by definition, and `java.util.Date` implements `Serializable`. The no-argument constructor is needed by the code that rebuilds the object (and for `moviesFromJson` in 35.10).

**Step 2 — put the object in the `Intent`, in `MainActivity.initListeners()`:**

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

`putExtra(String, Serializable)` is the overload chosen automatically for a `Movie`. You do not need to do anything special: if the object implements `Serializable`, it compiles.

**Step 3 — read the object in `ItemActivity.onCreate()`:**

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

`IntentCompat.getSerializableExtra(Intent, String, Class<T>)` is the typed version from `androidx.core`. It returns `Movie` directly, without a cast, and works the same on all Android versions. The old version, `(Movie) intent.getSerializableExtra(MOVIE_EXTRA)`, still works, but it is marked deprecated since API 33 — and in `MainActivity` that is exactly how it appears in the callback:

```java
Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
```

The difference between the two files is not a bug, it is an inconsistency of the original code. In the exam, write the `IntentCompat` version in both places and say why.

**Step 4 — import what you need.** In `ItemActivity` it already exists:

```java
import androidx.core.content.IntentCompat;
```

If you use the modern version in `MainActivity` too, add the same import there.

**Step 5 — understand what travels.** Not the reference, but a **copy**:

```text
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
```

**Why it works this way:** an `Intent` cannot hold references to objects in an activity's heap, because it may cross the boundary between processes. That is why `putExtra` serializes the object into bytes, and `getSerializableExtra` deserializes it into a new object. `Serializable` is the classic Java mechanism: reflection over the fields, recursive writing of each one. The cost is real — for a `Movie` with 10 fields it is negligible, for a list of thousands of objects it would be a problem. The most important consequence is not performance, but **identity**: `Movie@A` and `Movie@A'` are two different objects. A change in the form is not visible in the list until you send the result back and do `movies.set(...)`.

**The mistake that costs marks:**

1. **You forget `implements Serializable`.** Symptom: at `putExtra`, the app crashes with `java.lang.RuntimeException: Parcelable encountered IOException writing serializable object` and, in the cause, `java.io.NotSerializableException: ro.ase.ie.g1097.model.Movie`. Cause: the class does not implement the interface. There is no compile-time check — `putExtra(String, Serializable)` only asks for the type, and the error appears at runtime.
2. **You add a field to `Movie` that is not serializable.** Symptom: the same crash, but only after you fill in that field. Cause: you put a `Context`, a `Drawable`, a `Bitmap` or a listener in the model. The rule: the model holds **data**, not resources and not references to the UI.
3. **You think you are modifying the object in the list.** Symptom: you change the title in the form, press Back without Save, and the list still shows the old title — and that is correct. Cause: you forgot that `existing` is a copy. If you want it to change, you need `setResult` + `movies.set(...)` (35.5).

**The check:** you tap "Inception" — the form opens full: title, date, genre "Sci-Fi", budget, duration, rating, "PG-13", poster. You change the title to "Inception 2" and press Back without Save: the list still shows "Inception". This proves two things at once — the copy worked, and the editing is not "live". Then you repeat and press "Update Movie": the list shows "Inception 2".

**Practise:** [24.2](cap-24.html#ex-24-2) (why `set` and not `add`), [19.9](cap-19.html#ex-19-9) (the list is not allowed to show old data after editing).

---

## Recipe 35.4 — Receive a result (ActivityResultLauncher)

**The requirement, as it sounds in the test:** "The detail screen must return the movie to the list, and the list must update immediately."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | the `ActivityResultLauncher<Intent>` field + `registerForActivityResult` in `onCreate()` | yes |
| 2 | `activities/MainActivity.java` | `launcher.launch(intent)` instead of `startActivity` | yes |
| 3 | `activities/MainActivity.java` | the `androidx.activity.result.*` imports | yes |
| 4 | `activities/ItemActivity.java` | `setResult(RESULT_OK, intent)` before `finish()` | yes, otherwise nothing comes back |

**The steps, in order:**

**Step 1 — declare the field.** Not a local variable, not a field of the listener: a field of the activity, next to the other views:

```java
private FloatingActionButton fabInsert;
private ListView listView;
private ActivityResultLauncher<Intent> launcher;
private final List<Movie> movies = new ArrayList<>();
private ArrayAdapter<Movie> movieAdapter;
```

The type is `ActivityResultLauncher<Intent>`: a launcher that receives an `Intent` at launch. There is also `ActivityResultLauncher<Void>` for contracts that need no input.

**Step 2 — register the launcher in `onCreate()`.** The exact place in the original code is **after** `initControls()` and `initListeners()`:

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
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
                        movieAdapter.notifyDataSetChanged();
                    } else {
                        movies.set(position, movie);
                        movieAdapter.notifyDataSetChanged();
                    }
                }
            }
        });
```

The order with `initListeners()` is not accidental, but not dangerous either: the FAB's listener is only **created** there, not executed. `launcher` is read only when the user presses the button, and by then `onCreate` has finished and the field is assigned. It would have been dangerous if `initListeners()` had called `launcher.launch(...)` directly — that would have given a `NullPointerException`.

**Step 3 — launch through the launcher, not through `startActivity`.** Both places in `initListeners()`:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        launcher.launch(intent);
    }
});

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

**Step 4 — the imports.** Without them it does not compile:

```java
import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
```

**Step 5 — understand what you get in the callback.** `ActivityResult` has exactly two things:

```java
o.getResultCode()   // int: RESULT_OK (-1), RESULT_CANCELED (0) or a custom code
o.getData()         // Intent: the extras put there by the other screen, or null
```

`getData()` can be `null` — for example when the user presses Back, a case in which you do not even enter the `RESULT_OK` branch. But it can also be `null` when someone calls `setResult(RESULT_OK)` without an `Intent`. The original code does not check, because `ItemActivity` always puts an `Intent`; if you add new branches yourself, check (35.6).

**Why it works this way:** `registerForActivityResult` does not register a "request code", but an **entry in a registry held by `ComponentActivity`**. The registry is tied to the lifecycle: when the activity reaches `STARTED`, the system delivers the results that arrived while it was stopped. That is why the registration must be done **before `onCreate` finishes** — after that the activity has already passed the required state and the registry no longer accepts entries. When `ItemActivity` calls `setResult` and `finish()`, `ActivityManager` keeps the code and the `Intent`, and when `MainActivity` comes back to the foreground, the registry finds the matching entry and calls the callback. There is no "waiting" in `MainActivity`: between `launch` and the callback, `MainActivity` is stopped, not blocked.

**The mistake that costs marks:**

1. **You register the launcher in the listener.** Symptom: on the first click on the FAB, a crash with `java.lang.IllegalStateException: LifecycleOwner ro.ase.ie.g1097.activities.MainActivity@... is attempting to register while current state is RESUMED. LifecycleOwners must call register before they are STARTED.` Cause: `registerForActivityResult` must be called in `onCreate` (or in a field initializer), not at the moment of the click.
2. **You declare the field but forget to assign it.** Symptom: `NullPointerException` on `launcher.launch(intent)`. Cause: you declared `private ActivityResultLauncher<Intent> launcher;` and skipped the line with `registerForActivityResult`.
3. **You mix `startActivity` with `launcher.launch`.** Symptom: one path works (editing), the other does not (the FAB), although the code looks almost the same. Cause: one of the two places still uses `startActivity`, so the result has nowhere to go.

**The check:** put a `Log.d("G1097", "callback code=" + o.getResultCode())` in the first line of the callback. You tap the FAB → fill in the title → "Save Movie" → Logcat shows `callback code=-1`. You tap the FAB → Back without Save → nothing appears, because `RESULT_CANCELED` does not enter the branch. If nothing appears on Save either, check step 1 and step 3.

**Practise:** [20.3](cap-20.html#ex-20-3) (the same launcher, used for a custom result code), [24.1](cap-24.html#ex-24-1) (what happens if you forget `notifyDataSetChanged()` after the callback).

---

## Recipe 35.5 — Return a modified object

**The requirement, as it sounds in the test:** "When the save button is pressed, the modified movie replaces the row in the list, without a duplicate appearing."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `saveMovie()`: you build the `Movie`, put the extras, `setResult`, `finish()` | yes |
| 2 | `activities/MainActivity.java` | in the callback: `movies.set(position, movie)` + `notifyDataSetChanged()` | yes |
| 3 | `activities/ItemActivity.java` | `position` read from `POSITION_EXTRA` in `onCreate()` | yes — otherwise you do not know what you are replacing |

**The steps, in order:**

**Step 1 — build the object from the widgets, in `ItemActivity.saveMovie()`:**

```java
private void saveMovie() {
    Movie movie = new Movie();
    movie.setTitle(etTitle.getText().toString());
    movie.setRelease(releaseCal.getTime());
    movie.setGenre(spGenre.getSelectedItem().toString());
    movie.setBudget(Double.parseDouble(etBudget.getText().toString()));
    movie.setDuration(sbDuration.getProgress());
    movie.setRating(rbRating.getRating());
    movie.setWatched(swWatched.isChecked());
    movie.setOnWatchlist(cbonWatchList.isChecked());
    movie.setPoster(etPoster.getText().toString());
    for (int index = 0; index < rgApproval.getChildCount(); index++) {
        RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
        if (rb.isChecked()) {
            movie.setApproval(rb.getText().toString());
            break;
        }
    }
    // step 2
}
```

Two details that get forgotten: `movie.setRelease(releaseCal.getTime())` — the date comes from the `Calendar`, **not** from the text in `etRelease`; and `setApproval` is read from a loop over the `RadioGroup`, because `RadioGroup` has no `getText()`, it has children.

**Step 2 — put the object and the position in the result `Intent`:**

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1) {
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
}
setResult(RESULT_OK, intent);
finish();
```

`new Intent()` with no parameters — it is not an `Intent` that starts something, it is just a carrier for extras. The condition `if (position != -1)` is exactly what tells insert from edit: on insert you have no position to send, and the missing key makes `getIntExtra(POSITION_EXTRA, -1)` in the callback return `-1`, that is, insert again.

**Step 3 — read the position on open, in `ItemActivity.onCreate()`:**

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

The field is declared with the insert value, so you do not depend on any branch:

```java
private int position = -1;   // -1 = insert mode
```

**Step 4 — in the `MainActivity` callback, replace, do not add:**

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
        movieAdapter.notifyDataSetChanged();
    } else {
        movies.set(position, movie);
        movieAdapter.notifyDataSetChanged();
    }
}
```

`List.set(int index, E element)` replaces the element at the given position and returns the old element. It does not change the size of the list. `List.add(E element)` adds at the end and increases the size. They are two different operations, and confusing them is the most frequent bug in the app.

**Step 5 — notify the adapter.** `movieAdapter.notifyDataSetChanged()` after every mutation. `ArrayAdapter` holds the **reference** to the `movies` list, so it sees the new content immediately; but the `ListView` does not observe the list, it only observes what the adapter told it at the last bind. Without `notifyDataSetChanged()`, the row stays drawn with the old values until the next redraw (scrolling, rotation, coming back from another screen).

**Why it works this way:** the result of an activity has two components — a code and an `Intent`. `setResult(RESULT_OK, intent)` writes both into a field of the activity, and `finish()` sends them to the caller. `MainActivity` receives a **deserialized** `Movie`, that is, a new object built from bytes; the only thing that ties it to the row in the list is `position`, which you sent separately precisely because the object does not know where it lives. That is why the chain has three mandatory links: the position sent on the way out, the position sent on the way back, and `set` instead of `add`. If any of them is missing, the movie appears twice or disappears.

**The mistake that costs marks:**

1. **`add` instead of `set` on the edit branch.** Symptom: you edit "Inception", press "Update Movie", and the list has 4 rows — old "Inception" and new "Inception". Cause: the `else` branch does `movies.add(movie)` or is missing entirely, and everything falls through to `add`.
2. **You forget `setResult` before `finish()`.** Symptom: the form closes, but the list does not change at all; in the callback `o.getResultCode()` is `0` (`RESULT_CANCELED`). Cause: you called `finish()` on its own. `finish()` sends the current code, which by default is `RESULT_CANCELED`.
3. **You do not send `POSITION_EXTRA`.** Symptom: the same duplicate as in point 1, although the callback code is correct. Cause: you forgot `intent.putExtra(POSITION_EXTRA, position)` in `saveMovie()`, so `getIntExtra(..., -1)` returns `-1` and the branch chosen is `add`.

**The check:** the list has 3 movies. You tap "Toy Story", change the title to "Toy Story 2", press "Update Movie". The list must still have **3** rows, and row 2 must be "Toy Story 2". Then you tap the FAB, fill in the title "Dune", "Save Movie": the list has **4** rows. If it has 5, you have `add` on the edit branch. If it still has 3 after the insert, you forgot `notifyDataSetChanged()`.

**Practise:** [24.2](cap-24.html#ex-24-2) (why `set` and not `add`), [24.9](cap-24.html#ex-24-9) (debug: after editing the movie appears twice).

---
## Recipe 35.6 — Return a result code (delete)

**The requirement, as it sounds in the test:** "Add the ability to delete a movie: the detail screen closes with a custom code, and the list removes the row when it receives that code."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | the `RESULT_DELETE` constant, the `deleteMode` field, the `deleteMovie()` method | yes |
| 2 | `activities/MainActivity.java` | the `DELETE_MODE_EXTRA` constant + `setOnItemLongClickListener` on the list | yes |
| 3 | `activities/MainActivity.java` | the `else if` branch in the launcher callback | yes |
| 4 | `res/layout/activity_item.xml` | **nothing** — we reuse the button that already exists | no |

**The steps, in order:**

**Step 1 — put the delete mode key in `MainActivity`, next to the other two:**

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
protected static final String DELETE_MODE_EXTRA = "delete_mode";
```

**Step 2 — add a long press on the row, in `MainActivity.initListeners()`.** The normal click opens editing; holding opens the same screen, but in delete mode:

```java
listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
    @Override
    public boolean onItemLongClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        intent.putExtra(DELETE_MODE_EXTRA, true);
        launcher.launch(intent);
        return true;
    }
});
```

`return true` means "I consumed the event". If you return `false`, lifting the finger also triggers the normal click, so the screen would open twice.

**Step 3 — declare the custom code in `ItemActivity`.** Any custom code must be **at least 1**, because 0 is `RESULT_CANCELED` and -1 is `RESULT_OK`:

```java
public static final int RESULT_DELETE = 2;
```

**Step 4 — read the mode in `ItemActivity.onCreate()`.** After the block that fills the form:

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}

deleteMode = intent.getBooleanExtra(MainActivity.DELETE_MODE_EXTRA, false);
if (deleteMode) {
    setTitle("Delete movie");
    btMovieAction.setText("Delete movie");
}
```

The new field, next to `position`:

```java
private boolean deleteMode = false;
```

The order matters: `deleteMode` is read **after** the `if (existing != null)` block, otherwise the "Update Movie" text set by that block would overwrite "Delete movie".

**Step 5 — tie the button to two actions.** The existing listener in `initListeners()` becomes:

```java
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        if (deleteMode) {
            deleteMovie();
        } else {
            saveMovie();
        }
    }
});
```

The listener reads the `deleteMode` field only on click, so it does not matter that `initListeners()` runs before the extra is read in `onCreate`.

**Step 6 — write `deleteMovie()`:**

```java
private void deleteMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_DELETE, intent);
    finish();
}
```

**Step 7 — add the branch in the `MainActivity` callback:**

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    movieAdapter.notifyDataSetChanged();
} else if (o.getResultCode() == ItemActivity.RESULT_DELETE) {
    Intent data = o.getData();
    if (data != null) {
        int position = data.getIntExtra(POSITION_EXTRA, -1);
        if (position >= 0 && position < movies.size()) {
            movies.remove(position);
            movieAdapter.notifyDataSetChanged();
        }
    }
}
```

`movies.remove(position)` with an `int` means "remove the element at index `position`" (`List.remove(int)`), not "remove the object `position`". The second variant would be `movies.remove(movies.get(position))` and would search by `equals`.

**Why it works this way:** `setResult` has two arguments precisely because the result has two dimensions: **the code** says *what happened* (`OK` = save, `RESULT_DELETE` = delete, `CANCELED` = nothing), and **the `Intent`** says *with what*. The callback in `MainActivity` cannot guess what the user wanted, so the code is the only signal. `Activity` keeps the code in an internal field, initially `RESULT_CANCELED`; `setResult` only writes it, and `finish()` sends it to the caller. That is why the order `setResult` → `finish()` is mandatory, and a custom code must be positive: negative values and zero are reserved by the system. The fact that we reuse `btMovieAction` is not an aesthetic compromise — it is exactly what you would do if you had no time to touch the layout, and in the exam it saves a whole step (XML + `findViewById` + a new listener).

**The mistake that costs marks:**

1. **A custom code equal to 0.** Symptom: you press "Delete movie", the screen closes, the list does not change, and in the callback `getResultCode()` is `0`. Cause: you declared `RESULT_DELETE = 0` or forgot `setResult` entirely. Zero is `RESULT_CANCELED`, that is, exactly "the user gave up".
2. **`o.getData()` used without a check.** Symptom: `NullPointerException` on the new branch, although the `RESULT_OK` branch works. Cause: a result can come with a valid code and without an `Intent`; `getData()` returns `null`, and `getIntExtra` on `null` crashes.
3. **You delete from the list without `notifyDataSetChanged()`.** Symptom: the movie disappears from the model, but the row stays on screen until the next redraw; if you tap it again, the position no longer matches. Cause: you forgot the adapter notification.

**The check:** you hold on "The Matrix". The detail screen opens with "Delete movie" on the button and "Delete movie" in the top bar. You press the button: you return to the list, and the list has **2** rows. Then you hold on a row and press Back: the list still has 2 rows — proof that Back sends `RESULT_CANCELED`, not `RESULT_DELETE`. Finally you tap the FAB: the button says "Save Movie", not "Delete movie", because in insert mode `deleteMode` is `false`.

**Practise:** [20.3](cap-20.html#ex-20-3) (exactly this chain, with a separate button in the layout), [24.4](cap-24.html#ex-24-4) (checking the number of movies with a `Toast`).

---

## Recipe 35.7 — Implicit intent

**The requirement, as it sounds in the test:** "The user holds on the field with the poster link and the app opens the link in the browser."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `setOnLongClickListener` on `etPoster` + `Intent(ACTION_VIEW, Uri)` | yes |
| 2 | `activities/ItemActivity.java` | the `android.net.Uri` and `android.content.ActivityNotFoundException` imports | yes |
| 3 | `AndroidManifest.xml` | `<queries>` for `ACTION_VIEW` — only if you use `resolveActivity` | only if |

**The steps, in order:**

**Step 1 — put the listener in `ItemActivity.initListeners()`.** Not on click, but on **long click**: an `EditText` needs the click to receive focus and the keyboard, so an `OnClickListener` would steal exactly the editing gesture.

```java
etPoster.setOnLongClickListener(new View.OnLongClickListener() {
    @Override
    public boolean onLongClick(View v) {
        String url = etPoster.getText().toString().trim();
        if (url.isEmpty()) {
            etPoster.setError("Poster URL is empty");
            return true;
        }
        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
        try {
            startActivity(intent);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(ItemActivity.this, "No app can open this link", Toast.LENGTH_SHORT).show();
        }
        return true;
    }
});
```

**Step 2 — add the imports.** `Toast` already exists in the file; the two are missing:

```java
import android.content.ActivityNotFoundException;
import android.net.Uri;
```

**Step 3 — the version with a check before launching.** If you do not want to catch the exception, you first ask who can answer:

```java
Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
if (intent.resolveActivity(getPackageManager()) != null) {
    startActivity(intent);
} else {
    Toast.makeText(ItemActivity.this, "No app can open this link", Toast.LENGTH_SHORT).show();
}
```

Watch out though: since Android 11, `resolveActivity` is filtered by **package visibility**. Without a `<queries>` declaration in the manifest, the method can return `null` even when a browser exists. The declaration looks like this:

```xml
<queries>
    <intent>
        <action android:name="android.intent.action.VIEW" />
        <data android:scheme="https" />
    </intent>
</queries>
```

That is why the `try`/`catch` version is safer in the exam: it does not depend on the manifest.

**Step 4 — other implicit actions, the same mechanism.** You only change the action and the `Uri`:

```java
// browser
new Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com/posters/inception.jpg"));

// phone
new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0744000000"));

// e-mail
new Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:test@example.com"));

// text sharing — here you also need a type
Intent share = new Intent(Intent.ACTION_SEND);
share.setType("text/plain");
share.putExtra(Intent.EXTRA_TEXT, etTitle.getText().toString());
startActivity(Intent.createChooser(share, "Share movie"));
```

`Intent.createChooser` shows a dialog with all the apps that can answer, instead of picking one. For `ACTION_SEND` it is almost mandatory: otherwise the system may automatically pick an app the user did not expect.

**Step 5 — what happens to your activity.** When the browser opens, `ItemActivity` receives `onPause`, then `onStop`. You get no result, because you used `startActivity`, not a launcher. When you come back with Back, `ItemActivity` is merely restarted (`onRestart` → `onStart` → `onResume`), and the form is intact.

**Why it works this way:** an implicit `Intent` does not name a class, it describes **what you want to happen**: an action (`ACTION_VIEW`) and a piece of data (`Uri`). The system queries the `PackageManager`, which knows which activities in which apps declared compatible `intent-filter`s, and starts the right one — or shows a chooser if there are several. You never find out which app answered, and your app needs no permissions for that. The difference from the explicit `Intent` in 35.1 is exactly this: explicit means "class X", implicit means "anyone who knows how to do Y with data Z". If nobody knows, `startActivity` throws `ActivityNotFoundException` — the only case in which an implicit `Intent` crashes.

**The mistake that costs marks:**

1. **`Uri.parse` without a scheme.** Symptom: `ActivityNotFoundException` for any link written without `https://`, although the link looks valid. Cause: `Uri.parse("www.example.com")` produces a `Uri` with a `null` scheme, which no browser accepts. Fix: validate or complete the scheme first.
2. **A click listener instead of a long click.** Symptom: you tap the field, the browser opens and you can no longer type in it. Cause: `setOnClickListener` on an `EditText` replaces the normal focus behaviour.
3. **`startActivity` without `try`/`catch` and without a check.** Symptom: a crash with `ActivityNotFoundException` on the emulator without a browser. Cause: you assumed the target app exists.

**The check:** you fill `etPoster` with `https://example.com/posters/inception.jpg`, hold on the field: the browser opens on that link. You come back with Back: the form is intact, with all the values. You empty the field and hold again: the error "Poster URL is empty" appears on the field, without anything opening.

**Practise:** [18.6](cap-18.html#ex-18-6) (the poster URL shown in a `TextView`), [17.7](cap-17.html#ex-17-7) (validating a mandatory field before doing anything with its value).

---

## Recipe 35.8 — Back vs finish() vs setResult

**The requirement, as it sounds in the test:** "Explain what comes back to the list when you press Back, when you press Save, and when you press Save immediately followed by Back."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `setResult(RESULT_OK, intent)` before `finish()` in `saveMovie()` | yes — it already exists |
| 2 | `activities/MainActivity.java` | the `if (o.getResultCode() == RESULT_OK)` guard | yes — it already exists |
| 3 | `activities/ItemActivity.java` | `OnBackPressedCallback` — only if you want to change Back's behaviour | only if |

**The steps, in order:**

**Step 1 — understand the three notions, which are not synonyms:**

| Notion | What it is | Who produces it |
|---|---|---|
| **Back** | a user gesture that closes the current activity | the system, through `OnBackPressedDispatcher` |
| **`finish()`** | the method that asks for the activity to close | your code (or Back, indirectly) |
| **`setResult(code, intent)`** | writes the result that will be sent to the caller | your code |

Back is **not** `finish()` called by you: Back is an event which, if not intercepted, leads to `finish()`. And `finish()` does **not** imply an `OK` result: it sends what is in the internal field, that is, `RESULT_CANCELED` if you wrote nothing else.

**Step 2 — write the end of `saveMovie()` correctly:**

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1) {
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
}
setResult(RESULT_OK, intent);
finish();
```

The order is the only one that works: `setResult` **writes**, `finish()` **sends**. In reverse, the result is lost.

**Step 3 — know all the scenarios.** The table below is the complete answer to the requirement:

| What the user does | What runs | Code sent | What `MainActivity` does |
|---|---|---|---|
| Back without Save | the implicit `finish()` | `RESULT_CANCELED` (0) | nothing — the `== RESULT_OK` guard does not pass |
| Save | `setResult(RESULT_OK)` + `finish()` | `RESULT_OK` (-1) | `add` or `set`, then `notifyDataSetChanged()` |
| Save, then Back immediately | the first `finish()` closes; the second Back no longer reaches `ItemActivity` | `RESULT_OK` | the same as for Save |
| `finish()` without `setResult` | `finish()` | `RESULT_CANCELED` | nothing |
| `setResult(RESULT_OK)` without `finish()` | nothing, for now | — | nothing until it closes |
| `setResult(RESULT_OK)`, then Back | Back → `finish()` → sends the written result | `RESULT_OK` | `add` or `set` |
| `finish()`, then `setResult(...)` | the second call is ignored | `RESULT_CANCELED` | nothing |

The last two rows are the real traps. `setResult` sends nothing; it only remembers. So if you call it too early — for example in `onCreate`, to "be sure" — and the user presses Back, the list receives `RESULT_OK` with an `Intent` that may not even contain the movie. And if you call `finish()` before `setResult`, the second call has no effect.

**Step 4 — the correct version if you want to change Back's behaviour.** You do not override `onBackPressed()` (deprecated since API 33), you register a callback:

```java
getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
    @Override
    public void handleOnBackPressed() {
        setResult(RESULT_CANCELED);
        finish();
    }
});
```

The import is `androidx.activity.OnBackPressedCallback`. In practice, for this app you do not need it: the default behaviour is exactly right.

**Step 5 — check the order with `Log`.** Put one log before `setResult` and one in the callback:

```java
// ItemActivity.saveMovie()
Log.d("G1097", "saveMovie: setResult OK, position=" + position);
setResult(RESULT_OK, intent);
finish();

// MainActivity, first line of onActivityResult
Log.d("G1097", "callback: code=" + o.getResultCode() + " data=" + o.getData());
```

**Why it works this way:** every `Activity` has an internal field for the result code, initialized to `RESULT_CANCELED`. `setResult` overwrites it. `finish()` asks `ActivityManager` to close the activity and, at the same time, tells it which code and which `Intent` to deliver to the caller. `ActivityManager` keeps the result until the caller returns to `STARTED`, then hands it to the results registry, which calls the callback. Back is just an event that reaches the same `finish()` if you do not intercept it — that is why Back "cancels" by default: not because someone decided so, but because the initial value of the field is `RESULT_CANCELED`.

**The mistake that costs marks:**

1. **`setResult` after `finish()`.** Symptom: the form closes, the list does not change, and in Logcat the callback sees `code=0`. Cause: the reverse order. `finish()` already sent `RESULT_CANCELED`.
2. **`setResult` in `onCreate`, to be "ready".** Symptom: you press Back without saving and, sometimes, the list changes or crashes with a `NullPointerException` on `getSerializableExtra`. Cause: the stored result is also sent on Back, and the `Intent` does not contain the movie.
3. **Expecting Back to keep the changes.** Symptom: you edit five fields, press Back, the list shows the old values — and that is the correct behaviour. Cause: the changes live only in the widgets; they reach the list only through `saveMovie()`.

**The check:** three tests, each with Logcat open. (1) You open a movie, press Back: no `callback` line appears. (2) You open, press "Update Movie": `callback: code=-1` appears. (3) You open, press "Update Movie", then Back immediately: a single `callback: code=-1` line appears, not two — the second press has nothing left to close.

**Practise:** [24.3](cap-24.html#ex-24-3) (you press Back without Save: nothing changes — what guarantees that), [24.2](cap-24.html#ex-24-2) (why editing means `set`).

---

## Recipe 35.9 — The form survives rotation

**The requirement, as it sounds in the test:** "Rotate the screen while you fill in the form: the values entered must not be lost, and on save the date must stay the one displayed."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `onSaveInstanceState` with `releaseCal` | yes |
| 2 | `activities/ItemActivity.java` | the restore in `onCreate()`, after `fillForm()` | yes |
| 3 | `activities/ItemActivity.java` | `fillForm()`: you sync `releaseCal` with the edited movie | yes — the real trap |
| 4 | `activities/MainActivity.java` | `onSaveInstanceState` with the list — only if the requirement talks about the list | only if |

**The steps, in order:**

**Step 1 — know what saves itself.** On rotation, Android destroys the activity and recreates it. Before destruction, every **view with an `android:id`** saves its internal state, and after `onCreate` it restores it. In `ItemActivity`, that means:

| Widget | What is saved automatically | Why |
|---|---|---|
| `etTitle`, `etRelease`, `etBudget`, `etPoster` | the text | `EditText.getFreezesText()` returns `true` |
| `sbDuration` | the progress | `ProgressBar` saves its `mProgress` |
| `rbRating` | the progress (so the rating) | it inherits from `ProgressBar` |
| `cbonWatchList`, `swWatched` | the check | `CompoundButton` saves its `mChecked` |
| `rgApproval` | the id of the checked button | `RadioGroup` saves `mCheckedId` |
| `spGenre` | the selected position | `AbsSpinner` saves the position |

What is **not** saved: your fields (`position`, `releaseCal`), plus the texts in `tvDurationValue` and `tvWatchedValue` — a plain `TextView` does not save its text unless it has `android:freezesText="true"`.

**Step 2 — notice why the labels rebuild anyway.** `tvDurationValue` and `tvWatchedValue` look lost, but they are not: on restore, `sbDuration` receives the saved progress through `setProgress(...)`, which triggers `onProgressChanged`, and the listener rewrites the label. Likewise, `swWatched` is restored through `setChecked(...)`, which triggers `onCheckedChanged`. The labels are **derived**, and the listener re-derives them. The lesson: a `TextView` that shows a derived value needs no saving of its own as long as its source is restored and the listener exists.

**Step 3 — save `releaseCal`.** Here is the real trap. `releaseCal` is a `Calendar`, not a view, so it does not save itself. Add to `ItemActivity`:

```java
private static final String KEY_RELEASE_MILLIS = "release_millis";

@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putLong(KEY_RELEASE_MILLIS, releaseCal.getTimeInMillis());
}
```

**Step 4 — restore it in `onCreate()`, after the block that fills the form.** The order is not optional:

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}

if (savedInstanceState != null) {
    releaseCal.setTimeInMillis(
            savedInstanceState.getLong(KEY_RELEASE_MILLIS, releaseCal.getTimeInMillis()));
}
```

Why after: on rotation, `getIntent()` returns the same `Intent`, so `fillForm(existing)` runs again and would overwrite `releaseCal` with the movie's date. The user's value, saved in the `Bundle`, must be applied **last**.

**Step 5 — also fix the sync in `fillForm()`.** Without this step the recipe is not finished: in the original code, `fillForm` writes the date into `etRelease`, but **not** into `releaseCal`. And `saveMovie()` reads `releaseCal.getTime()`. The consequence: you open a movie for editing, do not touch the date field, press "Update Movie" — and the movie gets **today's** date.

```java
private void fillForm(Movie existing) {
    etTitle.setText(existing.getTitle());
    etRelease.setText(dateFormat.format(existing.getRelease()));
    if (existing.getRelease() != null) {
        releaseCal.setTime(existing.getRelease());
    }
    etBudget.setText(String.valueOf(existing.getBudget()));
    sbDuration.setProgress(existing.getDuration());
    cbonWatchList.setChecked(existing.isOnWatchlist());
    swWatched.setChecked(existing.isWatched());
    rbRating.setRating(existing.getRating());
    etPoster.setText(existing.getPoster());
    for (int index = 0; index < spGenre.getCount(); index++) {
        if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
            spGenre.setSelection(index);
            break;
        }
    }
    for (int index = 0; index < rgApproval.getChildCount(); index++) {
        RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
        if (rb.getText().toString().equals(existing.getApproval())) {
            rgApproval.check(rgApproval.getChildAt(index).getId());
            break;
        }
    }
}
```

The `!= null` guard is needed because `dateFormat.format(null)` throws a `NullPointerException` on the line above — a movie with `release == null` crashes before it reaches `releaseCal`.

**Step 6 — the list in `MainActivity`, if the requirement asks for it.** Rotation destroys `MainActivity` too. On recreation, `addSampleMovies()` runs again on an empty list, so the movies added by the user disappear. The minimum solution is a `Bundle`:

```java
private static final String KEY_MOVIES = "movies";

@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putSerializable(KEY_MOVIES, new ArrayList<>(movies));
}
```

and in `onCreate()`, right after `addSampleMovies()`:

```java
if (savedInstanceState != null) {
    Object saved = savedInstanceState.getSerializable(KEY_MOVIES);
    if (saved instanceof ArrayList) {
        movies.clear();
        movies.addAll((ArrayList<Movie>) saved);
    }
}
```

It needs `import androidx.annotation.NonNull;` in `MainActivity`. `ArrayList<Movie>` is serializable because `Movie` is serializable. Watch out: `getSerializable(String)` is deprecated since API 33; in the exam it works, and the modern version is `BundleCompat`. This solution keeps the list only across rotation — for restarting the app see 35.10.

**Why it works this way:** rotation is a **configuration change**. Instead of rearranging the existing views, Android chooses the simple and safe solution: it destroys the activity (`onPause` → `onStop` → `onDestroy`) and recreates it (`onCreate` → `onStart` → `onResume`). Before destruction, `onSaveInstanceState` is called on every view in the tree, and the state is gathered into a `Bundle` that the system keeps. On recreation, `onCreate` runs **before** the views are restored: that is why `fillForm(existing)` can write into the `EditText` without worry, and then the framework puts the user's saved text over it. Your fields are not part of the tree, so for them the `Bundle` must be filled in manually. And `releaseCal` is the perfect case: its value is not visible anywhere in the UI, but it is the one that reaches the model on save.

**The mistake that costs marks:**

1. **You do not sync `releaseCal` in `fillForm`.** Symptom: you edit a movie, do not touch the date, save — the date becomes today, with no error at all. Cause: `etRelease` shows the correct date, but `saveMovie()` reads `releaseCal`, which stayed `Calendar.getInstance()`.
2. **You restore `releaseCal` before `fillForm`.** Symptom: rotation seems to work, but if you rotate while editing and save, the date goes back to the one in the movie — the user's change is ignored. Cause: the reverse order in `onCreate`; `fillForm` overwrote the restored value.
3. **You think `tvDurationValue` needs its own saving.** Symptom: you add useless code and, sometimes, introduce a sync bug. Cause: you forgot that the `sbDuration` listener rewrites the label on restore.

**The check:** you open "Inception", change the title to "Test", take the duration to 200, turn the switch on, choose "R", open the date picker and choose 01/01/2020. You rotate the screen: all five values are there, and the labels show "200 min." and "Yes". You press "Update Movie": in the list, the movie has the date 01/01/2020, not today's date. Then you rotate the list: the three movies plus the ones you added are still there.

**Practise:** [24.5](cap-24.html#ex-24-5) (what is actually lost from the form on rotation), [19.6](cap-19.html#ex-19-6) (rotation does not lose the form).

---

## Recipe 35.10 — The list survives app close (SharedPreferences + JSON)

**The requirement, as it sounds in the test:** "The data must be saved: you add a movie, close the app from Recents, reopen it, and the movie is still in the list."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | two constants: the preferences file name and the JSON key | yes |
| 2 | `activities/MainActivity.java` | you replace `addSampleMovies();` with a load + populate on the first run | yes |
| 3 | `activities/MainActivity.java` | an `onPause()` that saves | yes |
| 4 | `activities/MainActivity.java` | five methods: `saveMovies`, `loadMovies`, `moviesToJson`, `moviesFromJson`, `escape` | yes |
| 5 | `activities/MainActivity.java` | six imports | yes |
| 6 | `build.gradle.kts` | **nothing** — `org.json` comes with Android, it is not a dependency | no |

**The steps, in order:**

**Step 1 — declare the constants, next to the extra keys:**

```java
private static final String PREFS_NAME = "g1097_movies";
private static final String KEY_MOVIES_JSON = "movies_json";
```

**Step 2 — replace `addSampleMovies();` in `onCreate()`.** The line stands alone, between the insets block and the creation of the adapter:

```java
movies.addAll(loadMovies());
if (movies.isEmpty()) {
    addSampleMovies();
    saveMovies();               // first run: the demos land on disk
}

movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
initControls();
initListeners();
```

`movies` is declared `private final List<Movie> movies = new ArrayList<>();`. That is why you do **not** write `movies = loadMovies();` — it does not compile. The adapter holds the reference to the list, not to the content, so the list is never reassigned; it is only modified through `addAll` / `clear` / `add` / `set` / `remove`.

**Step 3 — save on every exit from the screen:**

```java
@Override
protected void onPause() {
    super.onPause();
    saveMovies();
}
```

`onPause`, not `onDestroy`: `onDestroy` is not guaranteed — if the process is killed, it is not called. `onPause` is called on every exit from the screen, including when you open `ItemActivity` or when you press Home.

**Step 4 — write and read:**

```java
private boolean saveMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = moviesToJson();
    boolean ok = prefs.edit().putString(KEY_MOVIES_JSON, json).commit();
    Log.d("G1097", "saveMovies: " + movies.size() + " filme, "
            + json.length() + " caractere, ok=" + ok);
    return ok;
}

private List<Movie> loadMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = prefs.getString(KEY_MOVIES_JSON, null);
    List<Movie> loaded = moviesFromJson(json);
    Log.d("G1097", "loadMovies: " + loaded.size() + " filme din " + PREFS_NAME);
    return loaded;
}
```

**Step 5 — build the JSON by hand, with `StringBuilder`.** No Gson, no Moshi, no new dependency. All 10 fields, in the same order:

```java
private String moviesToJson() {
    StringBuilder sb = new StringBuilder("[");
    for (int i = 0; i < movies.size(); i++) {
        Movie m = movies.get(i);
        if (i > 0) sb.append(',');
        sb.append('{')
          .append("\"title\":\"").append(escape(m.getTitle())).append("\",")
          .append("\"release\":").append(m.getRelease() == null ? 0L : m.getRelease().getTime()).append(',')
          .append("\"genre\":\"").append(escape(m.getGenre())).append("\",")
          .append("\"budget\":").append(BigDecimal.valueOf(m.getBudget()).toPlainString()).append(',')
          .append("\"duration\":").append(m.getDuration()).append(',')
          .append("\"rating\":").append(m.getRating()).append(',')
          .append("\"watched\":").append(m.isWatched()).append(',')
          .append("\"approval\":\"").append(escape(m.getApproval())).append("\",")
          .append("\"onWatchlist\":").append(m.isOnWatchlist()).append(',')
          .append("\"poster\":\"").append(escape(m.getPoster())).append("\"")
          .append('}');
    }
    return sb.append(']').toString();
}

private static String escape(String value) {
    if (value == null) return "";
    return value.replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t");
}
```

The order in `escape` matters: backslash first, then quotes. In reverse, `\"` would become `\\"` and the JSON would break.

**Step 6 — read the JSON with `org.json`:**

```java
private List<Movie> moviesFromJson(String json) {
    List<Movie> result = new ArrayList<>();
    if (json == null || json.isEmpty()) return result;
    try {
        JSONArray array = new JSONArray(json);
        for (int i = 0; i < array.length(); i++) {
            JSONObject o = array.getJSONObject(i);
            Movie m = new Movie();
            m.setTitle(o.optString("title", ""));
            m.setRelease(new Date(o.optLong("release", 0L)));
            m.setGenre(o.optString("genre", ""));
            m.setBudget(o.optDouble("budget", 0));
            m.setDuration(o.optInt("duration", 0));
            m.setRating((float) o.optDouble("rating", 0));
            m.setWatched(o.optBoolean("watched", false));
            m.setApproval(o.optString("approval", ""));
            m.setOnWatchlist(o.optBoolean("onWatchlist", false));
            m.setPoster(o.optString("poster", ""));
            result.add(m);
        }
    } catch (JSONException e) {
        Log.e("G1097", "invalid JSON — starting with an empty list", e);
    }
    return result;
}
```

`optString` / `optInt` / `optLong` / `optDouble` / `optBoolean` return a default value instead of throwing. `getString` would throw a `JSONException` if the key is missing — useful when you want to find out that the file is corrupt, harmful when you want the app to start.

**Step 7 — add the imports:**

```java
import android.content.SharedPreferences;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.math.BigDecimal;
```

**Step 8 — also save after every result received.** `onPause` covers the exit from the screen, but if the process is killed right after an insert, the movie has not had time to be written. One line in the callback closes the gap:

```java
movies.add(movie);
movieAdapter.notifyDataSetChanged();
saveMovies();
```

**Why it works this way:** when the app is closed from Recents, the process is killed, and with it the whole heap disappears: `movies`, the adapter, the activities. RAM is not persistence. `SharedPreferences` writes an XML file in `/data/data/ro.ase.ie.g1097/shared_prefs/g1097_movies.xml`, which the system keeps until uninstall or "Clear data". On the first read, the whole file is loaded into memory; `edit()` builds a modifiable copy, and `commit()` writes it synchronously and returns a `boolean` — that is why you can check in Logcat whether the write succeeded. `apply()` would write asynchronously and return nothing. For a list of a few movies, the time difference is negligible, and `commit()` gives you the proof.

Three decisions worth explaining in the exam:

- **`BigDecimal.valueOf(...).toPlainString()`** instead of `String.valueOf(double)`. `String.valueOf(160000000.0)` produces `1.6E8`. JSON accepts scientific notation, so it would reload correctly, but the file becomes unreadable. `toPlainString()` writes `160000000`.
- **`release` as a `long`** (`Date.getTime()`), not as text. A formatted `Date` depends on the `Locale` and the time zone; a `long` is unambiguous. `0` is the sentinel for "no date" and becomes `new Date(0)` on read, so that you do not introduce `null` — `fillForm` crashes on `release == null`.
- **JSON built by hand**, not Gson. Gson is not in the project's dependencies, and `org.json` comes with the Android SDK. In the exam, "no new dependencies" is often an explicit requirement.


**The mistake that costs marks:**

1. **`movies = loadMovies();`** Symptom: compile error `cannot assign a value to final variable movies`. Cause: the list is `final` because the adapter holds the reference to it. Fix: `movies.addAll(loadMovies());`.
2. **No `escape()`.** Symptom: you add a movie with the title `He said "hi"`, close the app, reopen it — the list is empty, although the file exists. Cause: the quotes closed the JSON string early, and `new JSONArray(...)` threw a `JSONException`; the code starts with an empty list.
3. **Unconditional population with demos.** Symptom: after every restart, the three demo movies appear again, on top of the saved ones. Cause: you left `addSampleMovies();` without the `if (movies.isEmpty())` guard.
4. **Saving in `onDestroy()`.** Symptom: it works when you press Back, it does not work when you close from Recents. Cause: `onDestroy` is not called when the process is killed.

**The check:** you add the movie "Dune", close the app from Recents (swipe), reopen it: the list has **4** rows, and the demos have not doubled. Then you add a movie with the title `He said "hi"`, restart: the title is intact. In Logcat, `saveMovies: 4 filme, ... caractere, ok=true` appears on every exit from the screen. The check on disk is the subject of recipe 35.11.

**Practise:** [24.6](cap-24.html#ex-24-6) (the reference implementation, with the same approach), [24.10](cap-24.html#ex-24-10) (the exam: "the data must be saved").

---
## Recipe 35.11 — Verify persistence

**The requirement, as it sounds in the test:** "Prove that the data really is saved: show the file on disk and prove that the list reloads after a full restart."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | `Log.d` in `saveMovies()` and `loadMovies()` | yes — the evidence |
| 2 | terminal / Android Studio | `adb shell run-as ... cat shared_prefs/g1097_movies.xml` | yes |
| 3 | terminal / Android Studio | `adb shell am force-stop` and `adb shell pm clear` | yes |
| 4 | `activities/MainActivity.java` | a `Toast` with the number of movies — an alternative to Logcat | no |

**The steps, in order:**

**Step 1 — put evidence in the code, not in your eyes.** Without logs, "it is saved" is an impression. The two lines from 35.10 are enough:

```java
Log.d("G1097", "saveMovies: " + movies.size() + " filme, "
        + json.length() + " caractere, ok=" + ok);
Log.d("G1097", "loadMovies: " + loaded.size() + " filme din " + PREFS_NAME);
```

`ok` is the result of `commit()`. If it is `false`, the file was not written — and you find that out immediately, not after you lose the movie.

**Step 2 — read the file from disk.** The app is in a `debug` build (the default in Android Studio), so `run-as` works:

```bash
adb shell run-as ro.ase.ie.g1097 cat shared_prefs/g1097_movies.xml
```

You must see something like:

```xml
<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
    <string name="movies_json">[{&quot;title&quot;:&quot;Inception&quot;,&quot;release&quot;:1279231200000,&quot;genre&quot;:&quot;Sci-Fi&quot;,...}]</string>
</map>
```

Three things are checked here: that the file exists, that it has the `movies_json` key and that the 10 fields are visible inside. `&quot;` is just how the XML serializer escapes the quotes — the JSON inside is correct.

**Step 3 — test the three different deaths.** They are not equivalent:

| Test | Command / gesture | What it proves |
|---|---|---|
| Rotation | Ctrl+Left / Ctrl+Right in the emulator | `onSaveInstanceState` (35.9), **not** persistence |
| Close from Recents | swipe on the card | the process dies, `onPause` saved |
| Forced stop | `adb shell am force-stop ro.ase.ie.g1097` | the process dies without `onDestroy` |
| Emulator restart | cold boot | the file survives the reboot |

```bash
adb shell am force-stop ro.ase.ie.g1097
adb shell monkey -p ro.ase.ie.g1097 -c android.intent.category.LAUNCHER 1
```

The second command starts the app from the launcher. If the list comes back, persistence works independently of the activity lifecycle.

**Step 4 — check the clean start.** `pm clear` deletes all the app's data, including the preferences:

```bash
adb shell pm clear ro.ase.ie.g1097
```

On the next start you must see exactly **3** movies — the demo ones. That proves that the `if (movies.isEmpty())` branch works and that the population does not repeat over the existing data.

**Step 5 — check the escape with hostile data.** Add, one at a time:

- a title with quotes: `He said "hi"`;
- a title with accented characters: `Amélie`;
- a title with a backslash: `C:\Movies`;
- a large budget: `160000000`.

After each one, close from Recents and reopen. All four must come back identical. If the list becomes empty after one of them, `escape()` is missing or has the wrong order.

**Step 6 — read the filtered Logcat.** Do not search through thousands of lines:

```bash
adb logcat -s G1097
```

You see only your logs, in order: `loadMovies: 3 filme din g1097_movies`, then, on every exit from the screen, `saveMovies: 3 filme, ... ok=true`.

**Why it works this way:** `SharedPreferences` is an XML file written by `FastXmlSerializer` in the app's private directory. It does not depend on the process, the activity or the lifecycle: once `commit()` has returned `true`, the data is on disk. That is why the correct check is not "I close and open the screen", but "I kill the process and restart". `force-stop` is the harshest test available without a reboot: the system no longer calls anything from the app, exactly as when the user swipes from Recents. `run-as` works because the `debug` build is `debuggable`, and `run-as` runs the process with the app's UID — that is why it can read `/data/data/ro.ase.ie.g1097/`, where otherwise you have no access.

**The mistake that costs marks:**

1. **You check only by rotating.** Symptom: it "works" on rotation, but the movie disappears on close. Cause: rotation is covered by `onSaveInstanceState` (35.9), not by `SharedPreferences`. They are two different mechanisms, with different lifetimes.
2. **`pm clear` before noting the expected result.** Symptom: "all the data was lost" — and it really was lost, because you deleted it. Cause: `pm clear` is a full reset, not a persistence test.
3. **You look at the file with another app or under another UID.** Symptom: `Permission denied` on `cat`. Cause: you forgot `run-as` or you are running on a `release` build.

**The check:** the full protocol, in order: (1) `pm clear`, you start, you see 3 movies; (2) you add "Dune", you see 4; (3) `adb shell run-as ro.ase.ie.g1097 cat shared_prefs/g1097_movies.xml` and you find `Dune` in the JSON; (4) `am force-stop`, you start from the launcher, you still see 4; (5) you close from Recents, reopen, you still see 4; (6) you add a title with quotes, repeat steps 4–5, the title is intact. If all six pass, persistence is proven.

**Practise:** [24.7](cap-24.html#ex-24-7) (the 6-check checklist after every new attribute), [24.6](cap-24.html#ex-24-6) (the implementation you verify here).

---

## Recipe 35.12 — Application and the lifecycle

**The requirement, as it sounds in the test:** "Explain the order of the lifecycle methods for the two screens and add an `Application` class that logs every transition."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `MovieApp.java` (new, in `ro.ase.ie.g1097`) | `extends Application`, `onCreate`, `registerActivityLifecycleCallbacks` | yes |
| 2 | `AndroidManifest.xml` | `android:name=".MovieApp"` on `<application>` | yes |
| 3 | `activities/MainActivity.java` | `Log.d` in `onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy` | only if you do not use the callbacks |
| 4 | `activities/ItemActivity.java` | the same | only if you do not use the callbacks |

**The steps, in order:**

**Step 1 — remember the order, for each transition:**

```text
START:     Application.onCreate
           MainActivity.onCreate -> onStart -> onResume

OPEN ItemActivity:
           MainActivity.onPause
           ItemActivity.onCreate -> onStart -> onResume
           MainActivity.onStop

BACK from ItemActivity:
           ItemActivity.onPause -> onStop -> onDestroy
           MainActivity.onRestart -> onStart -> onResume

HOME:
           MainActivity.onPause -> onStop            (stays in memory)

ROTATION:
           onPause -> onStop -> onSaveInstanceState -> onDestroy
           onCreate -> onStart -> onRestoreInstanceState -> onResume

CLOSE FROM RECENTS:
           onPause -> onStop
           the process dies; onDestroy is NOT guaranteed
```

The rule to remember: **`onCreate` → `onStart` → `onResume` on entry, `onPause` → `onStop` → `onDestroy` on exit**, and `onRestart` appears only when the activity comes back from `stopped`, not from `destroyed`.

**Step 2 — create `MovieApp.java` in the root package.** The file sits next to `MainActivity` and `ItemActivity`, but in `ro.ase.ie.g1097`, not in `ro.ase.ie.g1097.activities`:
```java
package ro.ase.ie.g1097;

import android.app.Activity;
import android.app.Application;
import android.os.Bundle;
import android.util.Log;

public class MovieApp extends Application {

    private static final String TAG = "G1097";

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "MovieApp.onCreate");

        registerActivityLifecycleCallbacks(new ActivityLifecycleCallbacks() {
            @Override
            public void onActivityCreated(Activity activity, Bundle savedInstanceState) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onCreate");
            }

            @Override
            public void onActivityStarted(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onStart");
            }

            @Override
            public void onActivityResumed(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onResume");
            }

            @Override
            public void onActivityPaused(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onPause");
            }

            @Override
            public void onActivityStopped(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onStop");
            }

            @Override
            public void onActivitySaveInstanceState(Activity activity, Bundle outState) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onSaveInstanceState");
            }

            @Override
            public void onActivityDestroyed(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onDestroy");
            }
        });
    }
}
```

The interface has exactly seven methods and all of them must be implemented. A single place where you put the logs — you no longer touch each activity.

**Step 3 — register the class in the manifest.** Without this line, `MovieApp` is never instantiated and you see no log at all:

```xml
<application
    android:name=".MovieApp"
    android:allowBackup="true"
    android:dataExtractionRules="@xml/data_extraction_rules"
    android:fullBackupContent="@xml/backup_rules"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:supportsRtl="true"
    android:theme="@style/Theme.G1097">
```

The leading dot means "in the app's package": `.MovieApp` is `ro.ase.ie.g1097.MovieApp`. For activities, the dot combines with the full name: `.activities.MainActivity`.

**Step 4 — use `Application` as the common place for the list, if the requirement asks for it.** `Application` lives as long as the process, so a list kept there survives the rotation of both activities:

```java
// in MovieApp, next to TAG
private final List<Movie> movies = new ArrayList<>();

public List<Movie> getMovies() {
    return movies;
}
```

Plus the three imports missing from `MovieApp`:

```java
import java.util.ArrayList;
import java.util.List;
import ro.ase.ie.g1097.model.Movie;
```

In `MainActivity`, the list is no longer created locally (and you need `import ro.ase.ie.g1097.MovieApp;`, because the activity is in another package):

```java
private List<Movie> movies;   // no `final`, no `new ArrayList<>()`

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

    movies = ((MovieApp) getApplication()).getMovies();
    if (movies.isEmpty()) {
        addSampleMovies();
    }
    movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
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
                        } else {
                            movies.set(position, movie);
                        }
                        movieAdapter.notifyDataSetChanged();
                    }
                }
            });
}
```

Two ordering traps: the assignment must be done **before** the adapter is created (the adapter receives the reference), and **not** in the field initializer. `getApplication()` returns `null` there, because field initializers run in the constructor, and `attach()` — which ties the activity to the application — is called after the constructor.

**Step 5 — know what `Application` does NOT solve.** The list in `Application` survives rotation and navigation, but does **not** survive the death of the process. For a restart you need 35.10. `onTerminate()` exists in the API, but on real devices it is never called — do not put saving there.

**Why it works this way:** `Application` is an object created by the system before any activity and destroyed with the process. It has no UI and does not appear in the back stack; it is just a common reference point. `registerActivityLifecycleCallbacks` registers an observer that `ActivityThread` calls for **every** activity of the app, in the same order in which it would call the activity's methods. That is why the logs come out in the correct order without modifying `MainActivity` or `ItemActivity`. Rotation is what produces the confusion: it looks like a "restart", but it is a destruction and recreation of the activity, not of the process — that is why `Application.onCreate` appears once, and `MainActivity.onCreate` appears every time.

**The mistake that costs marks:**

1. **You forget `android:name` in the manifest.** Symptom: `MovieApp.onCreate` never appears in Logcat, although the class exists and compiles. Cause: the system does not know how to instantiate it.
2. **You put the saving in `onTerminate()`.** Symptom: the data is lost on close, although you wrote the "correct" code. Cause: `onTerminate` is not called on real devices, only in the old emulator.
3. **`getApplication()` in the field initializer.** Symptom: `NullPointerException` at start-up, on the line that takes the list from the application. Cause: the fields are initialized in the constructor, before `attach()`.

**The check:** you open Logcat filtered on `G1097`, start the app. The order must be: `MovieApp.onCreate`, `MainActivity.onCreate`, `MainActivity.onStart`, `MainActivity.onResume`. You tap a row: `MainActivity.onPause`, `ItemActivity.onCreate`, `ItemActivity.onStart`, `ItemActivity.onResume`, `MainActivity.onStop`. You press Back: `ItemActivity.onPause`, `onStop`, `onDestroy`, then `MainActivity.onRestart`, `onStart`, `onResume`. You rotate in `ItemActivity`: `onPause`, `onStop`, `onSaveInstanceState`, `onDestroy`, `onCreate`, `onStart`, `onResume` — and **no** extra `MovieApp.onCreate`.

**Practise:** [24.5](cap-24.html#ex-24-5) (rotation, step by step), [19.6](cap-19.html#ex-19-6) (rotation does not lose the form).

---

## Recipe 35.13 — Debug: the data does not arrive where it should

**The requirement, as it sounds in the test:** "The movie is saved, but it does not appear in the list. Find the cause and explain in what order you check."

**Files touched:**

| # | File | What you do | Mandatory? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `Log.d` before `setResult` | yes |
| 2 | `activities/MainActivity.java` | `Log.d` in the first line of the callback | yes |
| 3 | `activities/MainActivity.java` | `Log.d` after `add` / `set` with `movies.size()` | yes |
| 4 | any suspicious file | you change **nothing** until you have the three numbers | yes — discipline |

**The steps, in order:**

**Step 1 — put three logs, in three places.** Do not guess; measure where the chain breaks:

```java
// ItemActivity.saveMovie(), before setResult
Log.d("G1097", "1 saveMovie: position=" + position
        + " title=" + movie.getTitle()
        + " extras=" + intent.getExtras());

// MainActivity.onActivityResult(), first line
Log.d("G1097", "2 callback: code=" + o.getResultCode() + " data=" + o.getData());

// MainActivity, after add / set
Log.d("G1097", "3 list: size=" + movies.size());
```

Three numbers, three questions: (1) did anything leave the form? (2) did anything reach the callback? (3) did it enter the list?

**Step 2 — read the result like a triage.** Each combination has a single plausible cause:

| What you see in Logcat | Where it broke | The likely cause |
|---|---|---|
| no log `1` | in `ItemActivity` | the button is not tied to `saveMovie()`, or the app crashed before |
| `1` appears, `2` does not | between activities | you used `startActivity` instead of `launcher.launch`, or you forgot `setResult` |
| `2` appears with `code=0` | the result | `finish()` without `setResult`, or `setResult` after `finish` |
| `2` appears with `code=-1`, `data=null` | the result `Intent` | `setResult(RESULT_OK)` without an `Intent` |
| `2` appears with `code=-1`, but `title=null` in `1` | in the form | the field was empty; `movie.getTitle()` is `""` |
| `2` appears correctly, `3` does not | in the callback | an exception before `add`, or the `== RESULT_OK` guard does not pass |
| `3` grows, the screen does not | adapter | `notifyDataSetChanged()` is missing |
| `3` grows by 1, but the list has a duplicate | the position | `position` ended up `-1` and `add` ran on the edit branch |

**Step 3 — check the six real causes, in order of cost.** They all appear in this app's code:

1. **A different key.** `"movie"` in one file, `"Movie"` in the other. Symptom: `getSerializableExtra` returns `null`, without an exception. Check: log `intent.getExtras()` and compare the keys with the constants.
2. **`RESULT_CANCELED` from a missing `setResult`.** Symptom: `code=0` in the callback. Check: `saveMovie()` ends with `setResult` **before** `finish()`.
3. **`data == null`.** Symptom: `NullPointerException` on `o.getData().getSerializableExtra(...)`. Check: `if (o.getData() != null)`.
4. **`position == -1` on edit.** Symptom: a duplicate. Cause: `POSITION_EXTRA` was not put on the way out or on the way back. Check: log `position` at both ends.
5. **The object is a copy.** Symptom: you change something in the form, the list does not change. It is not a bug — it is the mechanism. Check: if `movies.get(position) != movie` (reference identity), you are on the right track.
6. **A missing `notifyDataSetChanged()`.** Symptom: `movies.size()` grows, the screen stays put. Check: after every mutation of the list, a single notification.

**Step 4 — isolate with a `Toast`, if you have no Logcat.** The same information, visible on screen:

```java
Toast.makeText(MainActivity.this,
        "code=" + o.getResultCode() + " size=" + movies.size(),
        Toast.LENGTH_LONG).show();
```

In the exam, a `Toast` is faster than Logcat, because you demonstrate on the spot, in front of the teacher.

**Step 5 — check the order, not just the values.** A chain can be correct piece by piece and wrong as a whole. The order in `MainActivity.onCreate` is: `addSampleMovies()` → `movieAdapter` → `initControls()` → `initListeners()` → `registerForActivityResult`. If you move `registerForActivityResult` into a listener, you get an `IllegalStateException`; if you move `initControls()` after `initListeners()`, the listeners bind to `null` fields and crash on the first click.

**Why it works this way:** the result of an activity crosses four hops — `ItemActivity` → `ActivityManager` → `MainActivity`'s results registry → callback — and each hop can lose something: a code not set, an `Intent` without a key, a key with another name, a guard that does not pass. A single `Log` at each hop turns "it does not work" into a question with a binary answer: the first log that is missing is the faulty hop. That is why the triage always starts with the three numbers, not with reading the code: the code looks correct even when one string differs by a letter.

**The mistake that costs marks:**

1. **You change the code before measuring.** Symptom: after three consecutive "fixes", the bug persists and you have introduced another one. Cause: you skipped step 1. Three logs cost a minute; guessing costs ten.
2. **You look at `movies.size()` instead of `movieAdapter.getCount()`.** Symptom: the numbers look correct, but the screen is empty. Cause: the adapter may not be tied to the list (`setAdapter` missing) or may be tied to another instance. Check both numbers.
3. **You conclude "it was not saved" when in fact it was not reloaded.** Symptom: on restart the list is empty, although the log `saveMovies: ok=true` appears. Cause: `loadMovies()` reads a different file name or a different key than `saveMovies()`. Check the `PREFS_NAME` / `KEY_MOVIES_JSON` pair.

**The check:** you deliberately provoke each cause and confirm that the triage catches it. (1) You change the key on the read side, only in `ItemActivity`: the form opens empty, in insert mode, although you tapped an existing row — `existing` is `null`, so `position` stays `-1`. (2) You comment out `setResult`: log `2` shows `code=0`. (3) You comment out `notifyDataSetChanged()`: log `3` grows, the screen does not. (4) You comment out `putExtra(POSITION_EXTRA, position)` from `saveMovie()`: log `1` shows `position=0`, log `2` shows `position=-1`, the list does `add` and the duplicate appears. After each one, you go back to the correct code.

**Practise:** [24.8](cap-24.html#ex-24-8) (the movie is saved, but it does not appear in the list — 5 causes, 5 checks), [24.9](cap-24.html#ex-24-9) (after editing, the movie appears twice).

---

## The table of the 13 recipes

| # | Recipe | When you use it | The mechanism | Files |
|---|---|---|---|---|
| 35.1 | Start another activity | "open the detail screen" | explicit `Intent` + `startActivity` | `MainActivity`, manifest |
| 35.2 | Send simple values | "send the title / the position" | `putExtra` + `getStringExtra` / `getIntExtra` | `MainActivity`, `ItemActivity` |
| 35.3 | Send a whole object | "fill the form with the tapped movie" | `Serializable` + `IntentCompat` | `Movie`, both activities |
| 35.4 | Receive a result | "the list updates after Save" | `ActivityResultLauncher` + `registerForActivityResult` | `MainActivity` |
| 35.5 | Return a modified object | "editing replaces the row" | `setResult(RESULT_OK)` + `movies.set` | `ItemActivity`, `MainActivity` |
| 35.6 | Return a result code | "delete the movie" | a custom code ≥ 1 + a branch in the callback | `ItemActivity`, `MainActivity` |
| 35.7 | Implicit intent | "open the link in the browser" | `ACTION_VIEW` + `Uri` | `ItemActivity` |
| 35.8 | Back vs `finish()` vs `setResult` | "what comes back when you press Back" | the internal code, initially `RESULT_CANCELED` | `ItemActivity` |
| 35.9 | The form survives rotation | "I rotate and lose nothing" | `onSaveInstanceState` + `releaseCal` | `ItemActivity` |
| 35.10 | The list survives close | "the data must be saved" | `SharedPreferences` + hand-built JSON | `MainActivity` |
| 35.11 | Verify persistence | "prove that it was saved" | `run-as`, `force-stop`, `pm clear` | terminal, `MainActivity` |
| 35.12 | `Application` and the lifecycle | "explain the order of the methods" | `Application` + `ActivityLifecycleCallbacks` | `MovieApp`, manifest |
| 35.13 | Debug: the data does not arrive | "it is saved, but it does not appear" | three logs, triage by hops | both activities |

**How to choose in 30 seconds:** if the requirement says "send" → 35.2 or 35.3; "return" → 35.4, 35.5 or 35.6; "delete" → 35.6; "open in another app" → 35.7; "rotation" → 35.9; "restart" or "save" → 35.10; "explain" → 35.8 or 35.12; "it does not work" → 35.13.

## Chapter 35 summary

- **An `Intent` carries a copy, not a reference.** `putExtra` serializes, `getSerializableExtra` deserializes. A change in the form is not visible in the list until `movies.set(position, movie)`.
- **Keys are contracts.** `MOVIE_EXTRA` and `POSITION_EXTRA` are `protected static final` in `MainActivity` precisely so that they do not differ between files. One changed letter gives `null`, not an error.
- **The result has a code and an `Intent`.** `setResult` writes, `finish()` sends. The default code is `RESULT_CANCELED`; any custom code must be at least 1.
- **`position == -1` means insert, anything else means edit.** `add` grows the list, `set` replaces. The confusion produces either a duplicate or a lost movie, with no exception at all.
- **The launcher is registered in `onCreate`, in a field.** Not in a listener, not in a local variable. `startActivityForResult` is history.
- **Rotation destroys the activity, not the process.** Views with an `id` save themselves; your fields do not. `releaseCal` must be saved manually and synced in `fillForm`.
- **Closing the app destroys the process.** Only `SharedPreferences` (or a file, or Room) survives. `onPause` saves, `onDestroy` is not guaranteed.
- **The JSON is built by hand, with `escape()`.** Without escape, a title with quotes empties the list on the next start, with no visible error.
- **Three logs beat any guess.** What leaves the form, what reaches the callback, what enters the list — the first one missing is the faulty hop.

Three sentences to remember:

1. **Data is not visible from one screen to another; it is sent and returned.** Every crossing is a copy, every return is a code plus an `Intent`.
2. **RAM is not persistence, and rotation is not a restart.** `onSaveInstanceState` keeps the form across a rotation; `SharedPreferences` keeps the list across a restart. They do not replace each other.
3. **When something does not arrive where it should, measure, do not read.** Three `Log.d` in three places show exactly where the chain broke — and most of the time the place is not the one you were looking at.
