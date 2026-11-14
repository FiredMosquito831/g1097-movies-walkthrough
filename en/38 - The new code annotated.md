# Chapter 38 — The new code annotated (14.11.2026)

**Goal:** to read every line of the **updated version** of the application — the one brought in on 14.11.2026 — with the explanation glued to it: what it does, why it is there, what breaks if you remove it. Compared with the old version (chapters 22 and 29–31), the app now has a `RecyclerView`, an adapter of its own, a click callback and a new screen.

**Estimated time:** 90–120 min (active reading, with the project open alongside).

**Source:** version 2 (14.11.2026), package `com.example.group1098` — 8 files annotated here: `MainActivity.java`, `MovieAdapter.java`, `IMovieListener.java`, `PlaceCiocanul.java`, `movie_item.xml`, `activity_main.xml`, `activity_place_ciocanul.xml`, `AndroidManifest.xml`. The three files left unchanged (`Movie.java`, `ItemActivity.java`, `activity_item.xml`) are sent to chapters 22 and 30.

**Rule:** the code is **unmodified, byte for byte**. Everything that appears with `//` or `<!-- -->` beyond the source is annotation. Nothing was reformatted, no line was deleted, no statement was added.

---

## 38.0 What is new, in 10 lines

1. **`ListView` → `RecyclerView`.** The `listView` field becomes `rvMovies`; the class comes from `androidx.recyclerview.widget`, not from the framework.
2. **`ArrayAdapter<Movie>` → `MovieAdapter`.** The adapter is no longer ready-made: it has `ViewHolder`, `onCreateViewHolder`, `onBindViewHolder` and `getItemCount` written by hand.
3. **Row click → interface of your own.** `setOnItemClickListener` disappears; `IMovieListener` appears, implemented by the activity and called from the `ViewHolder`.
4. **`movie_item.xml` is finally used.** In chapter 22 the file existed, but nobody inflated it. Now every row of the list is a card built from it.
5. **New screen: `PlaceCiocanul`.** A second FAB (`btnVlad`, bottom-left) opens a test screen, through the **same** `launcher`.
6. **The old code is kept commented out** in `MainActivity`, in three places. It is not an oversight: it is the migration shown live, with the before and after versions side by side.
7. **The list notification.** `movieAdapter.notifyDataSetChanged()` is called after every mutation (`add` on insert, `set` on edit) — the “twin” variant, not `notifyItemInserted`.
8. **The package changed:** `com.example.group1098`, with the subpackages `activities/`, `adapter/` and `model/`. The imports and `R` follow the new package.
9. **Three activities in the manifest**, not two. `PlaceCiocanul` must be declared, otherwise the `Intent` throws `ActivityNotFoundException` at runtime, with no compile error.
10. **Three files are identical byte for byte** to the old version, apart from the package lines: `Movie.java`, `ItemActivity.java`, `activity_item.xml`. They are not annotated again here.

### 38.0.1 The files that did not change

| File | State | Where you read it |
|---|---|---|
| `Movie.java` | identical to the old version, only `package ...model` differs | chapter 22, section 22.1 (and chapter 30 for the G1098 variant) |
| `ItemActivity.java` | identical, only the package and the two imports differ | chapter 22, section 22.3 |
| `activity_item.xml` | identical **with no difference at all** | chapter 22, section 22.5 |

**Why it matters that they are identical:** everything you learned about the form stays valid word for word. What changed is **only** the list screen and its bindings: the widget, the adapter, the click, the row layout and the manifest. That is exactly where you must look when you compare the two versions.

**Where all the rest shows up:** chapter 39 takes the differences one by one — from `ListView` to `RecyclerView`, from the ready-made adapter to the adapter of your own, from the list listener to the callback interface — and ties them to the exam requirements. This chapter is the **code reading**; chapter 39 is the **explanation of the migration**.

### 38.0.2 How to read the chapter

- **Read the code first, the comment second.** Cover the block above with your hand, say what the line does, then check.
- **The `THEORY` blocks** appear before each class and explain *why* the structure exists, not *how* it works.
- **The numbered steps** (“1. Validation”, “2. Inflate”) describe the order of execution. The order is part of the lesson.
- **The `RISK:`, `BUG:` and `DANGER!` markers** show where the code can break, where it already breaks and where the mistake produces no error at all.
- **The ASCII diagrams** show what you cannot see in the code: the recycling of rows, the path of the click, the view tree.
- **Compare with chapter 22.** There is the old version of the same two screens; the difference between them is precisely the subject of this section.

---

## 38.1 `MainActivity.java` — the list on a RecyclerView

```java
/*
 * ======================================================================================
 * FILE: MainActivity.java — THE LIST SCREEN, VERSION 2
 * ======================================================================================
 * WHAT THIS FILE IS:
 *   The start activity. It holds the movie list in an `ArrayList<Movie>`, displays it
 *   with a `RecyclerView` through an adapter of its own (`MovieAdapter`) and starts
 *   `ItemActivity` — for insert, from the FAB, and for edit, from a click on a row.
 *
 * WHY IT EXISTS:
 *   It is the only place that holds the STATE of the app: the `movies` list. All the other
 *   screens receive a `Movie` through an `Intent` and return a `Movie` through the result.
 *   Without this class there is nowhere for the result to come back to.
 *
 * WHAT IT DEPENDS ON:
 *   - `Movie` (the model), `MovieAdapter` and `IMovieListener` (the `adapter` package),
 *   - `R.layout.activity_main` and four IDs: `main`, `rvMovies`,
 *     `floatingActionButton`, `btnVlad`,
 *   - the `ItemActivity` and `PlaceCiocanul` classes, started through an `Intent`.
 *
 * WHO DEPENDS ON IT:
 *   `ItemActivity` reads `MainActivity.MOVIE_EXTRA` and `MainActivity.POSITION_EXTRA`
 *   (it sees them because they are `protected static` and the file is in the SAME package).
 *   `AndroidManifest.xml` declares it with the LAUNCHER intent-filter.
 *
 * WHAT IT DOES NOT DO:
 *   It does not validate data, does not keep a “selected” position, does not save anything to disk.
 *   The list lives in memory and disappears with the process.
 *
 * WHAT BREAKS WITHOUT IT:
 *   The app would have no entry point: without the LAUNCHER activity, the icon
 *   starts nothing. And without `movies` here, the form would have somewhere to send
 *   the result to, but nobody would receive it.
 * ======================================================================================
 */

// ======================================================================================
// THE PACKAGE AND THE IMPORTS
// ======================================================================================
package com.example.group1098.activities;

// Intent: the object that describes “which activity you start” and what data it carries.
//   Here it appears three times: at the FAB, at the second FAB and in the result callback.
import android.content.Intent;

// Bundle: the state bag saved by the system. It appears only in the signature of `onCreate`.
import android.os.Bundle;

// View: the base class of any UI element. The type of the parameter in `onClick`.
import android.view.View;

// AdapterView: the base class for ListView/Spinner, used by
//   `AdapterView.OnItemClickListener`.
// RISK: UNUSED IMPORT in version 2. Its only reference remains in the commented
//   block from `initListeners`. The code compiles, but Android Studio shows it grey.
import android.widget.AdapterView;

// ArrayAdapter: the bridge between `List<Movie>` and the ListView rows.
// RISK: UNUSED IMPORT — likewise, it survives only in comments.
import android.widget.ArrayAdapter;

// ListView: the old version's widget. It does not even exist in the layout any more.
// RISK: UNUSED IMPORT — a leftover of the migration.
import android.widget.ListView;

// Toast: short messages on screen. It is not used anywhere in this file —
//   it was not in the old version either (chapter 22 flagged it the same way).
import android.widget.Toast;

// EdgeToEdge: drawing under the system bars (status + navigation).
import androidx.activity.EdgeToEdge;

// ActivityResult: the result returned by the secondary activity: code + Intent.
import androidx.activity.result.ActivityResult;

// ActivityResultCallback: the single-method interface, called on return.
import androidx.activity.result.ActivityResultCallback;

// ActivityResultLauncher: the object that starts the activity and keeps the link
//   to the callback. It is the `launcher` field.
import androidx.activity.result.ActivityResultLauncher;

// ActivityResultContracts: the predefined contracts. Here `StartActivityForResult`,
//   that is, exactly the old `startActivityForResult`, wrapped in a modern way.
import androidx.activity.result.contract.ActivityResultContracts;

// AppCompatActivity: the base activity, with a Material theme and AppCompat support.
import androidx.appcompat.app.AppCompatActivity;

// Insets: the pixel values of the bars that cover the content.
import androidx.core.graphics.Insets;

// ViewCompat: the compatible version of the View APIs (insets on any API).
import androidx.core.view.ViewCompat;

// WindowInsetsCompat: the description of the insets, independent of the Android version.
import androidx.core.view.WindowInsetsCompat;

// LinearLayoutManager: the only layout manager used here. It decides the ARRANGEMENT
//   of the rows in a vertical list — `RecyclerView` has no default one.
import androidx.recyclerview.widget.LinearLayoutManager;

// RecyclerView: the widget that replaces ListView. The container, not the adapter.
import androidx.recyclerview.widget.RecyclerView;

// IMovieListener: the click contract. MainActivity IMPLEMENTS it.
import com.example.group1098.adapter.IMovieListener;

// MovieAdapter: the adapter of your own, written in the `adapter` package.
import com.example.group1098.adapter.MovieAdapter;

// FloatingActionButton: the round button. There are TWO on this screen.
import com.google.android.material.floatingactionbutton.FloatingActionButton;

// ArrayList: the concrete implementation of the movie list.
import java.util.ArrayList;

// Calendar: the month constants (`Calendar.JULY`, `NOVEMBER`, `MARCH`).
import java.util.Calendar;

// GregorianCalendar: the quick “year, month, day” constructor in the demo data.
import java.util.GregorianCalendar;

// List: the list interface.
// RISK: UNUSED IMPORT — the field is declared `ArrayList<Movie>`, not `List<Movie>`.
import java.util.List;

// R: the class generated from resources. Here for `R.layout.activity_main` and `R.id.*`.
import com.example.group1098.R;

// Movie: the data model. The only dependency on the `model` package.
import com.example.group1098.model.Movie;

/*
 * ======================================================================================
 * THEORY BLOCK: ACTIVITY, RECYCLERVIEW, CALLBACK
 * ======================================================================================
 *
 * 1. **Activity = a screen with a state.** `MainActivity` is a `Context` (it has access to
 *    resources and to the system) and a `LifecycleOwner` (it has a lifecycle: onCreate ->
 *    onStart -> onResume -> onPause -> onStop -> onDestroy).
 *
 * 2. **RecyclerView = an opinion-free container.** It does not know what it displays, it does not
 *    know what a row looks like and it does not know in which direction it scrolls. All it knows is to ask
 *    the adapter: “how many rows are there?” and “give me the row at position N”.
 *
 * 3. **Adapter = the translator.** For each visible row, it creates (once)
 *    the view and then fills it with data (every time). The two moments are two
 *    different methods: `onCreateViewHolder` and `onBindViewHolder`.
 *
 * 4. **Callback = the return of the click.** A row is an inert view. For the click to reach
 *    the activity, the adapter receives an object that implements `IMovieListener`;
 *    here that object is `MainActivity` ITSELF (`new MovieAdapter(movies, this)`).
 *
 * 5. **Launcher = the contract with the result.** `registerForActivityResult` is called
 *    ONCE, in `onCreate`, before the activity becomes visible. The result arrives
 *    in `onActivityResult`, with a code (`RESULT_OK` / `RESULT_CANCELED`) and an `Intent`.
 *
 * THE VISUAL FLOW OF EACH ROW:
 *
 *   movies (ArrayList<Movie>)            <- the data, owned by the activity
 *        |
 *        v
 *   MovieAdapter                         <- getItemCount() + onBindViewHolder()
 *        |
 *        v
 *   RecyclerView  <--- LinearLayoutManager   <- WHERE the rows live
 *        |
 *        v
 *   movie_item.xml  ->  one card per movie
 *
 * WHO HOLDS WHAT:
 *
 *   MainActivity  ---- owns ------>  ArrayList<Movie> movies
 *        |                                  ^
 *        | creates                          | the same reference
 *        v                                  |
 *   MovieAdapter  ----------------------> movies
 *        |
 *        +---- forwards the click to -----> IMovieListener ( = MainActivity )
 *
 * WHY `implements IMovieListener` IS MANDATORY:
 *   `new MovieAdapter(movies, this)` requires the second argument to be an
 *   `IMovieListener`. Without `implements`, the line DOES NOT COMPILE — and that is good:
 *   the compiler checks exactly the contract you want.
 * ======================================================================================
 */

// The start activity. `implements IMovieListener` makes it the recipient of the clicks.
public class MainActivity extends AppCompatActivity implements IMovieListener {

    // ==================================================================================
    // THE TWO KEYS OF THE COMMUNICATION WITH ItemActivity
    // ==================================================================================
    // `static final` = class constant: the same value for all instances,
    //   set once, at compile time.
    // `protected` = visible in subclasses AND in the whole package. ItemActivity is in
    //   `com.example.group1098.activities`, so it sees the constants without an import.
    // WHY NOT `private`: ItemActivity would receive them as the literal text “movie” / “position”;
    //   a typing mistake would give a non-existent extra, with no error at all.
    // RISK: if you change the “movie” value here, ItemActivity sees it automatically — but
    //   any `getStringExtra("movie")` written by hand in another file would break silently.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";

    // The second key: the serialised movie. Same convention.
    protected static final String MOVIE_EXTRA = "movie";

    // The “+” FAB, from the bottom-right corner. It opens ItemActivity in insert mode.
    private FloatingActionButton fabInsert;

    // The old version's code, KEPT ON PURPOSE:
    // private ListView listView;
    // WHY IT STAYED: so the reader sees exactly what was replaced and with what. In the
    //   shipped code the comment has no effect; you can read it as a “before”.
    // REF: chapter 22, section 22.2 — the version in which the line was active.

    // The SUCCESSOR of `listView`: version 2's list container.
    private RecyclerView rvMovies;

    // The result launcher. A single object serves BOTH screens
    //   (`ItemActivity` and `PlaceCiocanul`), because both are started the same way.
    // RISK: it is assigned ONLY at the end of `onCreate`, but it is used in
    //   listeners created earlier. See the explanation of step 8 in `onCreate`.
    private ActivityResultLauncher<Intent> launcher;

    // THE LIST — the screen's only data source.
    // `final` means the REFERENCE never changes; the content does.
    //   That is why `movies.add(...)` is legal, and `movies = new ArrayList<>()` is not.
    // WHY `final` helps here: the adapter receives THIS reference; if you
    //   replaced the list with another, the adapter would stay on the old one, with no error.
    private final ArrayList<Movie> movies = new ArrayList<>();

    // The old version's code, kept commented out:
    //private ArrayAdapter<Movie> movieAdapter;
    // Note the spacing: the original had no space after `//`. It is the exact record
    //   of a line commented with Ctrl+/ in Android Studio, not rewritten by hand.
    // REF: chapter 22 — `ArrayAdapter` with `simple_list_item_1`.

    // The adapter of your own. The type is the class written in the `adapter` package, not a system one.
    private MovieAdapter movieAdapter;

    // The second FAB, added in version 2. Bottom-left; it opens the test screen.
    // The name (`btnVlad`) is the one from the XML (`@+id/btnVlad`) — it matches exactly.
    private FloatingActionButton btnVlad;

    // ==================================================================================
    // METHOD: onCreate — THE CONSTRUCTION OF THE SCREEN
    // ==================================================================================
    // WHAT IT DOES: it creates the screen, loads the demo data, builds the adapter, binds
    //   the views to the code, installs the two button listeners and registers
    //   the result launcher.
    // HOW: in the order below — and the order is the only part that is hard to fix.
    // RISK: each step depends on the previous one. Move `initControls()` after
    //   `initListeners()` and you get a `NullPointerException` on `fabInsert`,
    //   because the listener would bind to a field that is still `null`.
    // REF: chapter 22, 22.2 — the same scheme, with ListView instead of RecyclerView.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. The mandatory chain of the base class: without it, AppCompat does not
        //    install its delegate and the theme is not applied.
        super.onCreate(savedInstanceState);

        // 2. The windows draw under the system bars (status bar + navigation).
        EdgeToEdge.enable(this);

        // 3. The view tree is inflated from the XML. From this moment on,
        //    `findViewById` has something to look for.
        setContentView(R.layout.activity_main);

        // 4. The compensation of the bars: the `R.id.main` container receives padding equal to
        //    the height of the bars, so the first row does not sit under the status bar.
        //    The lambda receives `insets` and returns exactly what it received — the API contract.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. The “system bars” insets: status bar on top, navigation at the bottom.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Padding on all four sides. `left/right` also cover the RTL case,
            //     because they are already computed by the system in the right direction.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. The received object is returned: otherwise the system would consider the insets
            //     consumed and other views would no longer receive them.
            return insets;
        });

        // 5. The demo data: three movies, added BEFORE the adapter is created.
        //    (Technically, the order would not hurt: the adapter holds the reference to the list, not a copy.)
        addSampleMovies();

        // The old version's code, kept commented out — the ready-made adapter:
        // movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
        // WHAT IT DID: it bound the list to a standard row, which displayed `movie.toString()`,
        //   that is, the whole object, on a single line of text.
        // WHAT REPLACES IT: the line below, with the adapter of your own.

        // 6. The adapter of your own. `this` is the second parameter because MainActivity
        //    implements `IMovieListener` — it is the recipient of the clicks.
        //    The REFERENCE to the list is passed: the adapter sees any later change.
        movieAdapter = new MovieAdapter(movies, this);

        // 7a. The binding of the views: at this moment `rvMovies`, `fabInsert` and `btnVlad`
        //     receive the real objects. `movieAdapter` is already built, so
        //     `setAdapter` has something to receive.
        initControls();

        // 7b. The button listeners. They need the views from 7a — hence
        //     this order and not the reverse.
        initListeners();

        // 7c. The second listener, in a separate method: the `btnVlad` FAB.
        initSecondListener();

        // 8. The result launcher. `registerForActivityResult` must be called
        //    before the activity is STARTED; `onCreate` is the canonical place.
        //    The `StartActivityForResult` contract is the modern equivalent of the old
        //    `startActivityForResult(intent, REQUEST_CODE)`.
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // The callback: an anonymous class that implements a single method.
                new ActivityResultCallback<ActivityResult>() {

                    // It is called on the return from ItemActivity or PlaceCiocanul.
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // The gate: work is done only when the secondary screen has said
                        //   “I have a result”. `RESULT_CANCELED` (the Back button) does not
                        //   change anything in the list.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // The result Intent. It can be `null` if the activity
                            //   called `setResult(RESULT_OK)` without an Intent.
                            // RISK: `null` is not checked here. Today it is safe, because
                            //   ItemActivity always puts an Intent (chapter 22, 22.3),
                            //   and PlaceCiocanul never calls `setResult`.
                            Intent intent = o.getData();

                            // The travelling movie: a DESERIALISED COPY, not the original.
                            //   The cast is necessary: `getSerializableExtra` returns
                            //   `Serializable`, the common type of all the objects put in.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // The position: -1 = “does not exist”, that is, insert mode.
                            //   The default value -1 is precisely the app's convention.
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // Branch 1: no position -> a NEW movie.
                            if(position == -1)
                            {
                                // Addition at the end of the list.
                                movies.add(movie);

                                // The notification to the RecyclerView. Without it, the list stays
                                //   visually unchanged: the adapter does not observe the ArrayList.
                                // REF: chapter 23 — the fine-grained variant, `notifyItemInserted`.
                                movieAdapter.notifyDataSetChanged();
                            }

                            // Branch 2: valid position -> REPLACEMENT, not addition.
                            else
                            {
                                // `set` overwrites the element at the given position.
                                // RISK: if the list had changed in the meantime (deletion,
                                //   reordering), the position could point to another movie.
                                //   Here the list does not change outside these two branches.
                                movies.set(position, movie);

                                // The same notification: a row has changed.
                                movieAdapter.notifyDataSetChanged();
                            }
                        }
                    }
                });
    }

    // ==================================================================================
    // METHOD: initListeners — the INSERT FAB (and the old code, commented out)
    // ==================================================================================
    // WHAT IT DOES: it binds `fabInsert` to starting ItemActivity without extras. A single
    //   active listener; on top of that, it keeps version 1's list listener commented out.
    // HOW: 1) listener on the FAB; 2) build an explicit Intent; 3) launch.
    // RISK: `launcher` is still `null` at the moment the listener is created —
    //   but it is read only on click, when `onCreate` finished long ago.
    // REF: chapter 22, 22.2 — the same method, without the commented block.
    // ==================================================================================
    private void initListeners() {

        // Listener on the FAB. An anonymous class, not a lambda: the style of the project (and of the exam).
        fabInsert.setOnClickListener(new View.OnClickListener() {

            // It runs on every press.
            @Override
            public void onClick(View v) {

                // EXPLICIT Intent: the source (`MainActivity.this`) and the destination
                //   (`ItemActivity.class`). No extras: ItemActivity sees that it has no
                //   `MOVIE_EXTRA` and enters insert mode.
                // NOTE: the class is written with the full package name, although
                //   ItemActivity is in the SAME package. It is redundant, but legal.
                Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);

                // Starting through the launcher: the result will reach the callback from
                //   step 8 of `onCreate`.
                launcher.launch(intent);
            }
        });

        // ==============================================================================
        // THE OLD VERSION'S CODE — THE ROW CLICK, KEPT COMMENTED OUT
        // ==============================================================================
        // This is the most valuable didactic block in the file: it shows EXACTLY what was
        // lost when ListView was replaced by RecyclerView and where it was moved.
        //
        //   BEFORE (ListView):                 NOW (RecyclerView):
        //   listView.setOnItemClickListener    listener in MovieAdapter (on itemView)
        //   onItemClick(..., position, id)     onMovieClick(Movie, position)
        //   movies.get(position)               movies.get(position)
        //   putExtra(MOVIE_EXTRA, ...)         putExtra(MOVIE_EXTRA, ...)
        //   putExtra(POSITION_EXTRA, ...)      putExtra(POSITION_EXTRA, ...)
        //   launcher.launch(intent)            launcher.launch(intent)
        //
        // The last four lines are IDENTICAL to `onMovieClick` at the end of the file.
        // The difference is only WHO calls them: ListView before, the adapter now.
        /* listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);
                intent.putExtra(MOVIE_EXTRA, movies.get(position));
                intent.putExtra(POSITION_EXTRA, position);
                launcher.launch(intent);
            }
        });*/
        // WHY THE MOVE WAS NECESSARY: a RecyclerView row is not a list item
        //   observed by the widget, but an ordinary view. There is no “onItemClick”;
        //   the click is bound manually, on `itemView`, in the `ViewHolder` (38.2).
        // RISK: if you left both active (the uncommented block + `onMovieClick`),
        //   the click would start ItemActivity twice — two overlapping activities.
    }

    // ==================================================================================
    // METHOD: initSecondListener — THE SECOND FAB
    // ==================================================================================
    // WHAT IT DOES: it binds `btnVlad` to starting the `PlaceCiocanul` screen.
    // HOW: 1) listener; 2) explicit Intent; 3) the SAME launcher.
    // RISK: the same launcher also receives the result of this screen. PlaceCiocanul does not
    //   call `setResult`, so the returned code is `RESULT_CANCELED` and the callback
    //   does nothing — exactly the desired behaviour.
    // REF: `initListeners`, with a single difference: the destination class.
    // ==================================================================================
    private void initSecondListener() {

        // Listener on the second FAB (bottom-left, the hammer icon).
        btnVlad.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {

                // The variable is called `intent2` — enough not to be confused
                //   with `intent` from the method above, although they are in different methods.
                Intent intent2 = new Intent(MainActivity.this, com.example.group1098.activities.PlaceCiocanul.class);

                // The same launcher: a single result contract for two screens.
                launcher.launch(intent2);
            }
        });
    }

    // ==================================================================================
    // METHOD: initControls — FINDVIEWBYID AND THE CONFIGURATION OF THE LIST
    // ==================================================================================
    // WHAT IT DOES: it binds the Java fields to the views in the XML and configures the RecyclerView
    //   (layout manager + adapter).
    // HOW: 1) FAB; 2) RecyclerView; 3) layout manager; 4) adapter; 5) the second FAB.
    // RISK: `setLayoutManager` must be called BEFORE `setAdapter`. Without a layout
    //   manager, RecyclerView draws nothing and writes to Logcat:
    //   “No layout manager attached; skipping layout”.
    // REF: chapter 22, 22.2 — the same method, with `ListView.setAdapter` instead.
    // ==================================================================================
    private void initControls() {

        // 1. The insert FAB, by the ID from `activity_main.xml`.
        fabInsert = findViewById(R.id.floatingActionButton);

        // The old version's code, kept commented out — the binding of the ListView:
        // listView = findViewById(R.id.listView);
        // listView.setAdapter(movieAdapter);
        // NOTE: both lines are commented out, but `R.id.listView` does not even
        //   exist in the layout any more. If you uncommented them, the file WOULD NOT COMPILE.

        // 2. The RecyclerView. The `rvMovies` ID exists in version 2's layout.
        rvMovies = findViewById(R.id.rvMovies);

        // 3. Layout manager: MANDATORY, before the adapter. `this` is the Context.
        //    LinearLayoutManager = vertical list, one row under another.
        //    Other variants: GridLayoutManager (grid), StaggeredGridLayoutManager.
        rvMovies.setLayoutManager(new LinearLayoutManager(this));

        // 4. The adapter built in `onCreate`. From this moment on, the RecyclerView knows
        //    how many rows the list has and how to build them.
        rvMovies.setAdapter(movieAdapter);

        // 5. The second FAB. Looked up AFTER the adapter is bound — the order between
        //    views does not matter, they all exist from `setContentView`.
        btnVlad = findViewById(R.id.btnVlad);
    }

    // ==================================================================================
    // METHOD: addSampleMovies — THE DEMO DATA
    // ==================================================================================
    // WHAT IT DOES: it adds three movies built with the 10-parameter constructor to the list.
    // HOW: three `new Movie(...)` calls, each with the same order of arguments.
    // RISK: the constructor is POSITIONAL. Swapping two arguments of the SAME type
    //   (String with String, boolean with boolean) compiles and produces wrong data.
    // REF: chapter 22, 22.1 — the table of positions in `Movie`'s constructor.
    // ==================================================================================
    private void addSampleMovies() {

        // Movie 1. The arguments, by position:
        //   1 title="Inception", 2 release=16 July 2010, 3 genre="Sci-Fi",
        //   4 budget=160000000, 5 duration=148, 6 rating=4.5f,
        //   7 watched=true, 8 approval="PG-13", 9 onWatchlist=false, 10 posterUrl=...
        movies.add(new Movie(

                // 1. The title.
                "Inception",

                // 2. The date. `GregorianCalendar(year, month, day)` — the month is 0-based:
                //    `Calendar.JULY` is 6, not 7. `.getTime()` turns the calendar
                //    into a `Date`, the type required by the model.
                new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),

                // 3. The genre — free text, not an enum.
                "Sci-Fi",

                // 4. The budget — `double`, hence no suffix.
                160000000,

                // 5. The duration in minutes — `int`.
                148,

                // 6. The rating — `float`: the `f` suffix is MANDATORY. Without it,
                //    the literal `4.5` is a `double` and the call does not compile.
                4.5f,

                // 7. “I have watched the movie” — boolean.
                true,

                // 8. The parental guidance — the radio button's text.
                "PG-13",

                // 9. “On the rewatch list” — the second boolean, independent of the first.
                false,

                // 10. The poster URL. Here it is an example URL: the app
                //     downloads no image, so the value never reaches the screen.
                "https://example.com/posters/inception.jpg"));

        // Movie 2. The same structure, other values. `Calendar.NOVEMBER` = 10 (0-based).
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

        // Movie 3. `Calendar.MARCH` = 2 (0-based); rating 5f — the maximum score;
        //   `watched=false`, `onWatchlist=true`: the movie is set aside, not watched.
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
    // METHOD: onMovieClick — THE IMPLEMENTATION OF THE CLICK CONTRACT
    // ==================================================================================
    // WHAT IT DOES: it receives the movie and the position from the adapter, then starts ItemActivity
    //   in edit mode, with both extras.
    // HOW: 1) explicit Intent; 2) put the movie; 3) put the position; 4) launch.
    // RISK: the method uses `movies.get(position)`, NOT the `movie` parameter. The two
    //   are consistent here (the adapter reads from the same list). If the adapter
    //   received another list, the parameter would be the correct source.
    // REF: the commented block in `initListeners` — this is `onItemClick` moved.
    // ==================================================================================
    @Override
    public void onMovieClick(Movie movie, int position) {

        // 1. The same explicit Intent as at the FAB, but with extras.
        Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);

        // 2. The movie, serialised into the Bundle. `putExtra(String, Serializable)`.
        //    It is taken from the list by position — the screen's source of truth.
        intent.putExtra(MOVIE_EXTRA, movies.get(position));

        // 3. The position: its presence is the “edit mode” signal for ItemActivity.
        intent.putExtra(POSITION_EXTRA, position);

        // 4. The start. The result (the modified movie) arrives in the callback from `onCreate`
        //    and goes down the `movies.set(position, movie)` branch.
        launcher.launch(intent);
    }
}
```

**What changed compared with the old version, in three places:**

| Place | The old version (ch. 22) | Version 2 (here) |
|---|---|---|
| the list field | `ListView listView` | `RecyclerView rvMovies` |
| the adapter | `ArrayAdapter<Movie>` | `MovieAdapter` (a class of its own) |
| row click | `listView.setOnItemClickListener` | `onMovieClick`, called from the `ViewHolder` |
| configuration | `listView.setAdapter(...)` | `setLayoutManager(...)` + `setAdapter(...)` |
| the second button | does not exist | `btnVlad` -> `PlaceCiocanul` |

**The order in `onCreate`, at a single glance:**

```
onCreate
  |-- super.onCreate
  |-- EdgeToEdge.enable          the bars become transparent
  |-- setContentView             the view tree exists
  |-- insets on R.id.main        padding = status + navigation
  |-- addSampleMovies            movies = [Inception, Toy Story, The Matrix]
  |-- new MovieAdapter(movies, this)    the adapter holds the REFERENCE to `movies`
  |-- initControls               rvMovies + LayoutManager + setAdapter
  |-- initListeners              fabInsert -> launcher (launcher is still null)
  |-- initSecondListener         btnVlad  -> launcher (launcher is still null)
  +-- registerForActivityResult  launcher created
        |
        v
  the screen is visible; the first click finds `launcher` ALREADY assigned
```

**Why `launcher` can be `null` in the listeners without crashing:** the anonymous class does not copy the field's value when it is created; it holds the reference to the `MainActivity` object and reads the field **at the moment of the click**. Between the creation of the listener and the first click lies all the rest of `onCreate`, so the assignment has been made. It is an order dependency that works, but it is worth knowing: if you called `launcher.launch(...)` **directly** in `onCreate`, before the registration line, you would get a `NullPointerException`.

---

## 38.2 `MovieAdapter.java` — the adapter, with a ViewHolder

This is the file that is missing from the old version. `ArrayAdapter` was a ready-made class: you gave it the list and a row layout, and it displayed the `toString()` of each element. Here the adapter is written by hand, because the row is no longer a `TextView`, but a whole card, with a poster, title, stars and four labels — and who fills them must be decided by you.

```java
/*
 * ======================================================================================
 * FILE: MovieAdapter.java — THE LIST ADAPTER
 * ======================================================================================
 * WHAT THIS FILE IS:
 *   The bridge between `ArrayList<Movie>` (data) and `RecyclerView` (UI). It extends
 *   `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>` and contains two classes:
 *   the adapter itself and the `ViewHolder` that holds the row's references.
 *
 * WHY IT EXISTS:
 *   `RecyclerView` does not know how to display a `Movie`. It only knows how to ask:
 *   “how many elements do you have?” (`getItemCount`), “give me a row view” (`onCreateViewHolder`)
 *   and “fill this view with the element at position N” (`onBindViewHolder`).
 *
 * WHAT IT DEPENDS ON:
 *   - `Movie` (the model) and `IMovieListener` (the click contract),
 *   - `R.layout.movie_item` (the row layout) and nine IDs from it,
 *   - `Chip` from Material Components, `RatingBar` and `ImageView` from the framework.
 *
 * WHO DEPENDS ON IT:
 *   `MainActivity` builds it (`new MovieAdapter(movies, this)`) and passes it
 *   to `rvMovies.setAdapter(...)`.
 *
 * WHAT IT DOES NOT DO:
 *   It does not own the list (it receives it by reference), does not decide the arrangement of the rows
 *   (the `LayoutManager` does), does not know what happens on click — it only notifies
 *   the listener.
 *
 * WHAT BREAKS WITHOUT IT:
 *   `rvMovies.setAdapter(...)` would have no argument; the list would stay empty on screen,
 *   although `movies` would have three elements.
 * ======================================================================================
 */

// The `adapter` package: separate from `activities` and from `model`. The adapter depends on both,
//   but neither of them depends on the adapter except MainActivity.
package com.example.group1098.adapter;

// LayoutInflater: the only way to turn an XML into a view tree.
import android.view.LayoutInflater;

// View: the type of the root of an inflated row and the type of the parameter in `onClick`.
import android.view.View;

// ViewGroup: the parent in which the row will sit (the RecyclerView itself).
//   The `Context` for the inflate is taken from it.
import android.view.ViewGroup;

// ImageView: the poster. Declared in the holder, but NOT FILLED in `onBindViewHolder`.
import android.widget.ImageView;

// RatingBar: the stars. Declared in the holder, but NOT FILLED — it stays at the XML value.
import android.widget.RatingBar;

// TextView: the card's four texts (title, subtitle, rating value, facts).
import android.widget.TextView;

// NonNull: a contract annotation. It does not change the bytecode; it tells lint (and
//   the reader) that the parameter is not allowed to be null, and that the return is not null.
import androidx.annotation.NonNull;

// RecyclerView: the base class. `RecyclerView.Adapter` and `RecyclerView.ViewHolder`
//   are the inner classes we extend here.
import androidx.recyclerview.widget.RecyclerView;

// R: `R.layout.movie_item` and the nine IDs looked up with `findViewById`.
import com.example.group1098.R;

// Movie: the element displayed.
import com.example.group1098.model.Movie;

// Chip: the rounded label from Material Components. Three of them per card.
import com.google.android.material.chip.Chip;

// SimpleDateFormat: turns `Date` into a year, for the “genre. year” subtitle.
import java.text.SimpleDateFormat;

// ArrayList: the type of the list received through the constructor.
import java.util.ArrayList;

/*
 * ======================================================================================
 * THEORY BLOCK: THE RecyclerView.Adapter CONTRACT
 * ======================================================================================
 *
 * 1. **Three mandatory methods, nothing else:**
 *      - `getItemCount()`        -> how many rows exist in total;
 *      - `onCreateViewHolder()`  -> builds an EMPTY row view;
 *      - `onBindViewHolder()`    -> fills an EXISTING view with data.
 *
 * 2. **Why two methods and not one.** `onCreateViewHolder` is expensive: it reads the XML
 *    and builds the view tree. It is called once for each
 *    row that fits on screen. `onBindViewHolder` is cheap: only `setText`.
 *    It is called every time a row reappears on scroll. If you had 10,000
 *    movies and 8 visible rows, ~10 views are created and they are bound thousands of times.
 *
 * 3. **Recycling.** When a row leaves the screen, its view is not thrown away: it goes
 *    into a pool. When a new row is needed, a view is taken out of the pool and
 *    re-bound — with no inflate. Hence the name “RecyclerView”.
 *
 *    screen:  [0][1][2][3][4][5][6][7]      (8 visible)
 *    you scroll down:
 *       row 0 leaves  ->  its view goes into the pool
 *       row 8 enters <-  it receives the recycled view, re-bound with its 8's data
 *
 * 4. **ViewHolder = the findViewById cache.** Without it, every bind would look up
 *    eight views through the tree again. The `ViewHolder` holds them once, in `final` fields.
 *    `RecyclerView` guarantees that the `ViewHolder` object travels together with its
 *    view, so `holder.title` is always the current row's TextView.
 *
 * 5. **The position is not yours.** `position` comes as a parameter at bind, but at click it no
 *    longer exists: it is requested with `getAbsoluteAdapterPosition()`. In the meantime, the list can
 *    change, and a position saved in a field would become wrong.
 *
 * 6. **`viewType`.** Here it is ignored: all the rows look the same. If you had two
 *    types of cards (watched movie / new movie), `getItemViewType(position)` would decide,
 *    and `onCreateViewHolder` would receive a different `viewType` and would inflate another XML.
 * ======================================================================================
 */

// The adapter. The generic in `<...>` is the TYPE OF THE HOLDER, not the type of the element.
//   That is why `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`: the inner class
//   is referred to by its full name, because it appears in the signature of the class that contains it.
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    // ==================================================================================
    // THE TWO REFERENCES
    // ==================================================================================
    // The list is NOT copied: the adapter holds the reference received from the activity.
    //   The good consequence: `movies.add(...)` in MainActivity is seen here immediately,
    //   without having to rebuild the adapter.
    // The dangerous consequence: if MainActivity replaced the list with another
    //   (`movies = new ArrayList<>()`), the adapter would stay on the old one.
    // `final` = the reference is not reassigned. The content can change freely.
    // No access modifier = visible in the `adapter` package.
    final ArrayList<Movie> movies;

    // The click listener: who receives the event. Here, MainActivity.
    // RISK: `null` is not checked. If you built the adapter with `null`, everything would
    //   work until the first click, when you would get a NullPointerException.
    final IMovieListener listener;

    // ==================================================================================
    // THE CONSTRUCTOR — ONLY TWO ASSIGNMENTS
    // ==================================================================================
    // WHAT IT DOES: it receives the list and the listener and holds them for the adapter's whole life.
    // HOW: two assignments, no logic.
    // RISK: the list is not cloned. If you wanted a copy, you would need `new ArrayList<>(movies)`
    //   — but then the changes in the activity would no longer be seen in the list.
    // REF: `new MovieAdapter(movies, this)` in MainActivity, 38.1.
    // ==================================================================================
    public MovieAdapter(ArrayList<Movie> movies, IMovieListener listener) {

        // `this.movies` = the field; `movies` = the parameter. The same trap as in `Movie`.
        this.movies = movies;

        // The same pattern for the listener.
        this.listener = listener;
    }

    // ==================================================================================
    // METHOD: onCreateViewHolder — THE CONSTRUCTION OF AN EMPTY ROW
    // ==================================================================================
    // WHAT IT DOES: it inflates `movie_item.xml` into a new view and wraps it in a holder.
    // HOW: 1) take the inflater from the parent's context; 2) inflate the layout with `false`;
    //   3) return a new `MovieViewHolder`.
    // RISK: the third argument must be `false`. With `true`, the view would be glued
    //   to the parent immediately, and the RecyclerView would try to add it again -> crash.
    // REF: chapter 23, the exercise about `ViewHolder` — the same code, step by step.
    // ==================================================================================
    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {

        // 1. The inflater is taken FROM THE PARENT'S CONTEXT, not from the activity: the adapter
        //    does not have and must not have a reference to an Activity. `parent.getContext()`
        //    is the activity hosting the RecyclerView, so the theme is the right one.
        // 2. `inflate(R.layout.movie_item, parent, false)`:
        //      - first argument: the row's XML;
        //      - second: the parent, from which the correct `LayoutParams` are taken;
        //      - third, `false`: do NOT attach now. The RecyclerView decides when.
        //    “Do not attach” is the correct answer in 99% of adapter cases.
        // 3. The result is a card view, still with no data in it.
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.movie_item, parent, false);

        // 4. It is wrapped in the holder. From this moment on, `holder.title` etc. are valid:
        //    the holder's constructor does all the `findViewById` calls.
        return new MovieViewHolder(view);
    }

    // ==================================================================================
    // METHOD: onBindViewHolder — FILLING THE ROW WITH DATA
    // ==================================================================================
    // WHAT IT DOES: it takes the movie at the given position and writes the title and subtitle into the holder.
    // HOW: 1) a year formatter; 2) the movie; 3) the title; 4) “genre. year”.
    // RISK: only TWO fields out of nine are filled. The rest keep the XML values
    //   — see the BUG below.
    // REF: chapter 22, 22.6 — `movie_item.xml`, the card you see now.
    // ==================================================================================
    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {

        // 1. A formatter for the year. It is created ON EVERY BIND — a new object for
        //    each row, every time the row reappears on scroll.
        // RISK: `SimpleDateFormat` is expensive to construct. The correct way would be a field
        //   `private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy");`
        //   built once. Here, with three movies, it is not noticeable.
        // WARNING: `"yyyy"` is the calendar year. `"YYYY"` would be the week-year
        //   (ISO week-year) and would give 2027 for a few days of December 2026.
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy");

        // 2. The movie at the requested position. `position` is given by the RecyclerView and is
        //    guaranteed to be in the range 0..getItemCount()-1 during a bind.
        Movie movie = movies.get(position);

        // 3. The title. `setText` accepts a CharSequence; `getTitle()` returns a String.
        holder.title.setText(movie.getTitle());

        // 4. The subtitle: “genre. year”. Three observations, all verifiable:
        //    - `movie.getGenre()` is already a `String`; `.toString()` on a String
        //      returns the SAME object — it is redundant, but harmless.
        //      RISK: if `genre` were null, the call would throw a NullPointerException.
        //      DANGER!: the exception erupts in onBindViewHolder, during scrolling,
        //        not at start-up — a crash that appears only when the list reaches that
        //        movie. Here `addSampleMovies` and the form always put a genre, so it does not
        //        happen; but the model allows `null` through the empty constructor.
        //    - the separator is “. ” (dot and space), not “ · ” as the
        //      comment in `movie_item.xml` suggests. The visible result: “Sci-Fi. 2010”.
        //    - `sdf.format(movie.getRelease())` requires a non-null `Date`. If the movie
        //      had a null date (possible through the empty constructor), it would throw an NPE.
        holder.subtitle.setText(movie.getGenre().toString() + ". " + sdf.format(movie.getRelease()));

        // NOTE: the method ends here. There is no `super.onBindViewHolder` call.
        //   It is not mandatory — the base class does nothing in it.
    }

    // ==================================================================================
    // METHOD: getItemCount — HOW MANY ROWS THERE ARE
    // ==================================================================================
    // WHAT IT DOES: it returns the number of elements in the list.
    // HOW: `movies.size()`, read on every call — hence always up to date.
    // RISK: if you returned a constant value or a manually updated field,
    //   the RecyclerView would request binds for non-existent positions -> IndexOutOfBounds.
    // REF: `notifyDataSetChanged()` in MainActivity — the notification that makes the RecyclerView
    //   ask this method again.
    // ==================================================================================
    @Override
    public int getItemCount() {

        // The source of truth is the list, not a parallel counter.
        return movies.size();
    }

    /*
     * ==================================================================================
     * BUG: THE CARD DISPLAYS STATIC DATA FOR ALL THE MOVIES
     * ==================================================================================
     * `MovieViewHolder` looks up nine views, but `onBindViewHolder` writes only into two:
     * `title` and `subtitle`. The other seven stay exactly as they were inflated from XML:
     *
     *   from XML (the same value on EVERY row)        from the model (ignored)
     *   --------------------------------------------  ------------------------
     *   movieFacts      = "142 min  ·  $160M"          duration, budget
     *   movieRatingValue= "4.5"                        rating
     *   movieRating     = 0 stars (no `rating=` in XML)  rating
     *   chipApproval    = "Approved"                   approval
     *   chipWatched     = "Watched"                    watched
     *   chipWatchlist   = "Watchlist"                  onWatchlist
     *   moviePoster     = the gallery icon             posterUrl
     *
     * Consequence: Inception (148 min, $160M, PG-13) and Toy Story (81 min, $30M, G)
     * appear with the SAME facts and the SAME labels. The data is in the model, but never
     * reaches the screen. It is not a syntax error: it compiles and runs.
     * ==================================================================================
     */

    // ==================================================================================
    // THE INNER CLASS: MovieViewHolder
    // ==================================================================================
    // WHAT IT DOES: it holds the references of the card's nine views and binds the click.
    // HOW: `findViewById` once, in the constructor; the click on `itemView`.
    // RISK: it is a NON-static inner class — it holds an implicit reference to the adapter.
    //   Here that is convenient (it sees `movies` and `listener` directly), but it means the
    //   holder cannot live without the adapter.
    // REF: `RecyclerView.ViewHolder`, which holds `itemView` — the whole row's view.
    // ==================================================================================
    class MovieViewHolder extends RecyclerView.ViewHolder {

        // ==============================================================================
        // THE NINE FIELDS — THE findViewById CACHE
        // ==============================================================================
        // All `final`: they are assigned once, in the constructor, and never change again.
        //   A new row = a new holder = a new set of references.
        // The nine correspond to the nine IDs in `movie_item.xml` that the
        //   code uses. In the layout there are two more IDs that the holder does NOT look up:
        //   `movieStatusGroup` (the ChipGroup) and `chipCiocan` (the fourth chip).
        // ==============================================================================

        // The poster. Looked up, but never filled — see the BUG above.
        final ImageView poster;

        // The title — FILLED in `onBindViewHolder`.
        final TextView title;

        // The “genre. year” subtitle — FILLED in `onBindViewHolder`.
        final TextView subtitle;

        // The stars. Never set: `android:rating` does not exist in XML, so 0 stars.
        final RatingBar rating;

        // The numeric value of the rating. It stays “4.5” from XML for any movie.
        final TextView ratingValue;

        // “duration · budget”. It stays “142 min · $160M” from XML.
        final TextView facts;

        // The three status labels. They remain the texts from XML.
        final Chip chipApproval;
        final Chip chipWatched;
        final Chip chipWatchList;

        // ==============================================================================
        // THE HOLDER'S CONSTRUCTOR
        // ==============================================================================
        // WHAT IT DOES: it binds each field to its view in the received row and installs
        //   the click listener on the whole row.
        // HOW: `super(itemView)` mandatory, then nine `findViewById`, then a listener.
        // RISK: `findViewById` on `itemView`, NOT on the activity. If you looked in the
        //   activity, you would find the first view with that ID on the whole screen — not necessarily
        //   from the current row.
        // REF: chapter 22, 22.6 — the IDs looked up here are exactly the ones in the layout.
        // ==============================================================================
        public MovieViewHolder(@NonNull View itemView) {

            // `super(itemView)` is mandatory: the base class keeps the row's view
            //   and uses it for positioning and for animations.
            super(itemView);

            // Each `findViewById` returns a `View`; assigning it to a field of a
            //   concrete type does the cast automatically (generics), without a hand-written `(TextView)`.
            //   If the ID were missing from the layout, it would return `null` — no error at
            //   compile time, just an NPE at the first bind.
            poster = itemView.findViewById(R.id.moviePoster);
            title = itemView.findViewById(R.id.movieTitle);
            subtitle = itemView.findViewById(R.id.movieSubtitle);
            rating = itemView.findViewById(R.id.movieRating);
            ratingValue = itemView.findViewById(R.id.movieRatingValue);
            facts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchList = itemView.findViewById(R.id.chipWatchlist);

            // ==========================================================================
            // THE ROW CLICK
            // ==========================================================================
            // This is the whole mechanism that replaces `setOnItemClickListener`.
            // It binds on `itemView` — the whole card, not a specific text.
            // WHY in the constructor and not in bind: the listener is the same for the whole
            //   life of the view; binding it on every bind would allocate an object for nothing.
            // ==========================================================================
            itemView.setOnClickListener(new View.OnClickListener() {

                // It runs on press. `v` is the card.
                @Override
                public void onClick(View v) {

                    // The position is requested NOW, not held in a field.
                    // `getAbsoluteAdapterPosition()` returns the position in the
                    //   adapter's list, or `NO_POSITION` (-1) if the row was removed
                    //   from the list in the meantime (deletion animation, changed list).
                    int pos = getAbsoluteAdapterPosition();

                    // The guard: valid position? Without it, `movies.get(-1)` would throw
                    //   IndexOutOfBoundsException. Here no elements are deleted, but
                    //   the guard is mandatory as a pattern.
                    if (pos != RecyclerView.NO_POSITION) {

                        // The movie at that position.
                        Movie movie = movies.get(pos);

                        // The notification to the activity. `listener` is MainActivity.
                        //   From this call you reach `onMovieClick`, which starts
                        //   ItemActivity with two extras (38.1).
                        listener.onMovieClick(movie, pos);
                    }
                }
            });
        }
    }
}
```

**The order in which the RecyclerView calls the adapter:**

```
RecyclerView wants to display the list
   |
   |-- getItemCount() .............................. 3
   |
   |-- for every visible row (0, 1, 2):
   |     |-- onCreateViewHolder(parent, 0) ....... a NEW card, empty
   |     +-- onBindViewHolder(holder, position) .... title + subtitle written
   |
   +-- on scroll:
         |-- the view that leaves -> into the recycling pool
         +-- the view that enters:
               onBindViewHolder(RECYCLED holder, new position)
               (no onCreateViewHolder, no inflate)
```

**Three things you will have been asked about this file:**

1. **“Why two methods, `onCreateViewHolder` and `onBindViewHolder`?”** Because the inflate is expensive and is done once per visible row, while binding the data is cheap and is done on every reappearance. Recycling is the whole point of the widget.
2. **“How does the click reach the activity?”** Through `IMovieListener`: the adapter does not know `MainActivity`, only the interface. The activity passes itself in the constructor.
3. **“Why `getAbsoluteAdapterPosition()` and not the `position` field from bind?”** Because the position can change between bind and click. The method requests it at the moment of the event and returns `NO_POSITION` when it is no longer valid.

---

## 38.3 `IMovieListener.java` — the click contract

The smallest file in the app: seven lines, a single method. It is, however, the piece that makes the difference between the old version and the new one: it replaces `AdapterView.OnItemClickListener`, which `ListView` offered ready-made, with a contract written by you.

```java
/*
 * ======================================================================================
 * FILE: IMovieListener.java — THE ROW CLICK CONTRACT
 * ======================================================================================
 * WHAT THIS FILE IS:
 *   An interface with a single method. It says what someone who wants to be
 *   notified when the user touches a row in the list must know how to do.
 *
 * WHY IT EXISTS:
 *   `RecyclerView` has no `setOnItemClickListener`. The click is bound manually, on
 *   `itemView`, in the `ViewHolder` (38.2) — and from there it must reach somewhere.
 *   The interface is that “somewhere”, without the adapter knowing who the recipient is.
 *
 * WHAT IT DEPENDS ON:
 *   Only on `Movie` (the parameter's type). It does not depend on Android, on `View`,
 *   on `Context` or on any class in the app.
 *
 * WHO DEPENDS ON IT:
 *   - `MovieAdapter` — it has an `IMovieListener` field and calls it on click;
 *   - `MainActivity` — it implements it and passes itself to the adapter.
 *
 * WHAT IT DOES NOT DO:
 *   It does not know what happens after the click, does not start activities, does not keep the position.
 *   It is only a signature.
 *
 * WHAT BREAKS WITHOUT IT:
 *   The adapter would have to receive a `MainActivity` directly — that is, exactly the coupling
 *   the interface avoids. And if you changed the method's signature, the two
 *   places that depend on it (the adapter and the activity) would refuse to compile.
 * ======================================================================================
 */

// The `adapter` package, not `activities`: the contract belongs to the adapter, which asks for it.
//   MainActivity imports it from here. The direction of the dependency: activities -> adapter -> model.
package com.example.group1098.adapter;

// `Movie` is the type carried by the event — not `Object`, not `View`.
import com.example.group1098.model.Movie;

/*
 * ======================================================================================
 * THEORY BLOCK: THE INTERFACE AS CALLBACK (INVERSION OF CONTROL)
 * ======================================================================================
 *
 * 1. **The problem.** A list row is an inert view: it knows how to draw itself, it does not know
 *    what “my being touched” means. Someone must decide what happens on click —
 *    and that someone is the ACTIVITY, not the adapter.
 *
 * 2. **The naive solution.** The adapter could receive `MainActivity` directly and could
 *    build the `Intent` itself. It would work, but the adapter would depend on three things
 *    that have nothing to do with drawing a card: the `ItemActivity` class, the
 *    `MOVIE_EXTRA` / `POSITION_EXTRA` constants and a `Context` for `startActivity`.
 *
 * 3. **The interface solution.** The adapter depends on A SINGLE name: `IMovieListener`.
 *    It does not know who implements it, nor what happens after the call. The activity passes
 *    itself (`this`) and takes on the behaviour.
 *
 * 4. **Inversion of control.** The adapter does not call the activity “by name”; it calls a
 *    method from a contract, and the activity has decided to respond to it. Control
 *    over “what happens” is inverted compared with the normal flow of calls.
 *
 * 5. **The practical consequence at the exam.** For the requirement “bind the row click to
 *    the start of another activity”, the answer has exactly three pieces:
 *      1) the interface (this file),
 *      2) the call from the ViewHolder (`listener.onMovieClick(...)`),
 *      3) `implements` on the activity + `new MovieAdapter(movies, this)`.
 * ======================================================================================
 */
// `public interface`: public = visible from any package; interface = a contract without
//   implementation. The methods are implicitly `public abstract`.
public interface IMovieListener {

    // ==================================================================================
    // METHOD: onMovieClick — THE CONTRACT'S ONLY REQUIREMENT
    // ==================================================================================
    // WHAT IT DOES: it defines what someone who wants to hear about a row click receives.
    // HOW: it has no body — each implementation decides what to do (here: start the screen).
    // RISK: `Movie` can be null if the list contained a null element; `position`
    //   is the position in the list, valid only if the list has not changed in the meantime.
    // REF: the call from `MovieAdapter.MovieViewHolder` and the implementation in MainActivity.
    // ==================================================================================
    void onMovieClick(Movie movie, int position);
}
```

**Why an interface and not an `Intent` sent directly from the adapter.** The adapter could, technically, build the `Intent` itself and start `ItemActivity`. Then it would depend on `ItemActivity`, on the `MOVIE_EXTRA` and `POSITION_EXTRA` constants and on a `Context` — three extra dependencies. With the interface, the adapter depends on a method name, and the activity remains the only place that knows what happens on click.

```
   WITHOUT the interface               WITH the interface
   -------------                       ------------
   MovieAdapter                        MovieAdapter
     |  knows ItemActivity              |  knows only IMovieListener
     |  knows MOVIE_EXTRA               |
     |  knows Context                   v
     +--> Intent                     MainActivity (implements)
          towards ItemActivity         |  knows ItemActivity
                                        +--> Intent towards ItemActivity
```

**The same functionality, written with a lambda.** The interface has a single abstract method, so it is a functional interface: `IMovieListener` can also be written as `(movie, position) -> { ... }`. Here the anonymous class / the implementation on the activity was chosen, because the exam asks for the explicit form, with `implements` in the class declaration.

---

## 38.4 `PlaceCiocanul.java` — the new screen

The third screen of the app and the simplest one: a single button, a single message. It is interesting not for what it does, but for the two patterns it shows — the `Window` variant of edge-to-edge and a classic `RISK` about `String.valueOf(int)`.

```java
/*
 * ======================================================================================
 * FILE: PlaceCiocanul.java — THE TEST SCREEN
 * ======================================================================================
 * WHAT THIS FILE IS:
 *   A minimal activity, opened by the second FAB on the main screen. It has a
 *   single button, which displays a `Toast`. It reads and writes no `Movie`.
 *
 * WHY IT EXISTS:
 *   It is a test screen added in version 2: it verifies that the second FAB
 *   starts an activity and that the manifest declares it. It has no role in the data flow.
 *
 * WHAT IT DEPENDS ON:
 *   - `R.layout.activity_place_ciocanul` and two IDs: `main`, `floatingActionButton2`;
 *   - `R.string.app_name` (used wrongly — see the RISK in `onCreate`);
 *   - the entry in `AndroidManifest.xml`, without which it cannot be started.
 *
 * WHO DEPENDS ON IT:
 *   Only `MainActivity.initSecondListener()`, which launches it through `launcher`.
 *
 * WHAT IT DOES NOT DO:
 *   It returns no result: it does not call `setResult`, so on return the code
 *   is `RESULT_CANCELED` and the callback in MainActivity does nothing.
 *
 * WHAT BREAKS WITHOUT IT:
 *   `btnVlad` would start a non-existent class -> `ActivityNotFoundException` at runtime.
 * ======================================================================================
 */

// The screens' package. MainActivity and ItemActivity are here too.
package com.example.group1098.activities;

// Bundle: only in the signature of `onCreate`, as everywhere.
import android.os.Bundle;

// View: the type of the parameter in `onClick`.
import android.view.View;

// Toast: the short message displayed on the button press.
import android.widget.Toast;

// AppCompatActivity: the same base as the other two activities.
import androidx.appcompat.app.AppCompatActivity;

// Insets: the values of the system bars.
import androidx.core.graphics.Insets;

// ViewCompat: the insets listener, compatible on any version.
import androidx.core.view.ViewCompat;

// WindowCompat: the edge-to-edge variant that receives a `Window`, not an activity.
//   MainActivity uses `EdgeToEdge.enable(this)`; this form is used here.
import androidx.core.view.WindowCompat;

// WindowInsetsCompat: the description of the insets.
import androidx.core.view.WindowInsetsCompat;

// R: the layout and the IDs.
import com.example.group1098.R;

// FloatingActionButton: the screen's only button.
import com.google.android.material.floatingactionbutton.FloatingActionButton;

// (two blank lines in the source — kept as they are)

/*
 * ======================================================================================
 * THEORY BLOCK: A THIRD SCREEN, AND TWO APIS FOR THE SAME THING
 * ======================================================================================
 *
 * 1. **One activity = one screen.** `PlaceCiocanul` is the app's third activity.
 *    It is declared in the manifest (38.8), started with an explicit `Intent` and closed with
 *    the system's Back button. That is all it takes for it to exist.
 *
 * 2. **Two edge-to-edge variants.** `MainActivity` uses `EdgeToEdge.enable(this)`,
 *    which receives the activity; here `WindowCompat.enableEdgeToEdge(getWindow())` is used,
 *    which receives the window. The effect is the same: the content is drawn under the
 *    system bars, and the padding is applied manually, from the insets. The two recipes coexist
 *    in the same project: a hygiene detail, not an error.
 *
 * 3. **Toast vs Snackbar.** A `Toast` appears over any screen, needs no parent
 *    and disappears by itself. A `Snackbar` needs a `CoordinatorLayout` and sits at the
 *    bottom of the screen. For a test message, a `Toast` is the minimal choice.
 *
 * 4. **What is missing for it to be a real screen:** a `RecyclerView` with an ID and an adapter, a
 *    correctly sized `ProgressBar`, a message from `strings.xml` instead of the hardcoded
 *    text and a `setResult` if the screen should return data.
 * ======================================================================================
 */
// The activity. No `implements`: this screen receives clicks from no list.
public class PlaceCiocanul extends AppCompatActivity {

    // The screen's button. The name `btn2` was chosen by the author; the ID in the XML is
    //   `floatingActionButton2`. The two do not have to match — the binding is done
    //   through `findViewById`, not by name.
    private FloatingActionButton btn2;

    // ==================================================================================
    // THE `string` FIELD — DECLARED, ASSIGNED, NEVER READ
    // ==================================================================================
    // RISK: the field is not used anywhere. It is “dead code”: no `getText`, no
    //   `Toast`, no `Log` reads it. The compiler does not complain, because
    //   the assignment is a valid side effect.
    // The name `string` is a weak choice too: it describes the TYPE, not the content.
    // ==================================================================================
    private String string;

    // ==================================================================================
    // METHOD: onCreate — THE WHOLE SCREEN, IN A SINGLE METHOD
    // ==================================================================================
    // WHAT IT DOES: it inflates the layout, applies the insets, binds the button to a Toast and
    //   assigns the `string` field (uselessly).
    // HOW: 1) super; 2) edge-to-edge; 3) setContentView; 4) insets; 5) findViewById;
    //   6) listener; 7) the wrong assignment of `string`.
    // RISK: unlike MainActivity, there is no `initControls()` and
    //   `initListeners()` here. With a single button, the separation is not worth it — but the order
    //   remains important: `findViewById` must come after `setContentView`.
    // REF: MainActivity (38.1) — the same scheme, with separate methods.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. The base class chain.
        super.onCreate(savedInstanceState);

        // 2. Edge-to-edge, the `Window` variant. `getWindow()` returns the activity's
        //    window; the method configures it to draw under the bars.
        // NOTE: it is the equivalent of `EdgeToEdge.enable(this)` in MainActivity,
        //    written with another API. Both do the same thing; the project mixes them.
        WindowCompat.enableEdgeToEdge(getWindow());

        // 3. The view tree from the new screen's layout.
        setContentView(R.layout.activity_place_ciocanul);

        // 4. The insets, on the `R.id.main` container in this layout (a RelativeLayout).
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. The system bars.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Padding equal to the bars.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. The received object is returned.
            return insets;
        });

        // 5. The button, by the ID from `activity_place_ciocanul.xml`.
        btn2 = findViewById(R.id.floatingActionButton2);

        // 6. The button's listener: a Toast. The whole behaviour of the screen.
        btn2.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {

                // `PlaceCiocanul.this` = the Context (in the anonymous class, `this` would be
                //   the listener). `Toast.LENGTH_LONG` = ~3.5 seconds.
                // RISK: the text is hardcoded in the code, not in `strings.xml`. Lint gives
                //   the “HardcodedText” warning, and the text cannot be translated.
                //   Before any submission, it must be replaced with a real message.
                Toast.makeText(PlaceCiocanul.this, "Caca", Toast.LENGTH_LONG).show();
            }
        });

        // 7. THE LAST LINE OF THE METHOD — and the most instructive one.
        // ==================================================================================
        // RISK: `String.valueOf(R.string.app_name)` does NOT return the app's name.
        // ==================================================================================
        // `R.string.app_name` is an `int`: the resource's numeric ID, generated in `R.java`.
        // `String.valueOf` has several overloads; with an `int` it picks the one that
        //   turns the number into digits. The result is a text of the form “2131689472”,
        //   not “Group1098”.
        //
        //   WRONG:   String.valueOf(R.string.app_name)      -> "2131689472"
        //   CORRECT: getString(R.string.app_name)           -> "Group1098"
        //   CORRECT: String.valueOf(getString(R.string.app_name))
        //
        // WHY IT IS NOT SEEN: the value is displayed nowhere. The `string` field is
        //   dead, so the bug has no visible effect — for now. The first attempt to
        //   put it into a `TextView` would display a number.
        // TO REMEMBER: `R.<type>.<name>` is ALWAYS an `int`. The text is obtained only through
        //   `getString(...)` / `getText(...)` / `getDrawable(...)`, that is, through `Resources`.
        string = String.valueOf(R.string.app_name);
    }
}
```

**The flow of this screen, end to end:**

```
MainActivity                         PlaceCiocanul                     system
------------                         -------------                     ------
btnVlad.onClick
  |
  |-- Intent(MainActivity.this, PlaceCiocanul.class)
  +-- launcher.launch(intent)
            |
            v
                                     onCreate
                                       |-- WindowCompat.enableEdgeToEdge
                                       |-- setContentView(activity_place_ciocanul)
                                       |-- insets on R.id.main
                                       |-- btn2 = findViewById(...)
                                       |-- btn2.setOnClickListener
                                       +-- string = String.valueOf(R.string.app_name)  <- RISK
            |
            v
                                     press FAB -> Toast "Caca" (3.5 s)
            |
            v
                                     Back button
                                       |
                                       +-- no setResult -> RESULT_CANCELED
            |
            v
MainActivity.onActivityResult(o)
  +-- o.getResultCode() == RESULT_OK ? NO -> nothing happens
```

**Why the screen breaks nothing, although it has a bug.** `MainActivity` filters on `RESULT_OK`. `PlaceCiocanul` never calls `setResult`, so on return the code is `RESULT_CANCELED` and the callback touches neither the list nor the adapter. A test screen that sends no result is harmless by construction — but only for as long as it remains a test.

---

## 38.5 `movie_item.xml` — the card, finally used

In chapter 22 this file existed and was complete, but **nobody inflated it**: `MainActivity` used `android.R.layout.simple_list_item_1`, that is, a single `TextView` with the movie's `toString()`. Now it is the layout of every row: `MovieAdapter.onCreateViewHolder` inflates it, and `MovieViewHolder` looks up its IDs.

The difference is visible immediately on screen: instead of a line of text of 300 characters, each movie has a card with a poster, title, subtitle, stars and labels.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FILE: movie_item.xml — THE CARD OF A SINGLE MOVIE                                       -->
<!-- ====================================================================================== -->
<!-- WHAT IT IS: the layout of a list row. It is inflated once for each visible row         -->
<!--   and re-bound with data on every reappearance (recycling — see 38.2).                 -->
<!-- WHY IT EXISTS: RecyclerView needs an XML to repeat. This is it. -->
<!-- WHAT IT DEPENDS ON: the Material theme (MaterialCardView, the Chip.Suggestion styles)  -->
<!--   and the @string/chip_ciocan_name resource. It depends on no Java class.              -->
<!-- WHO DEPENDS ON IT: MovieAdapter — through R.layout.movie_item and nine IDs from here.   -->
<!-- WHAT IT DOES NOT DO: it does not display real data by itself. The android:text values  -->
<!--   below are PLACEHOLDERS that are seen at runtime if the adapter does not overwrite them. -->
<!-- WHAT BREAKS WITHOUT IT: inflate(R.layout.movie_item, ...) would not compile; the list   -->
<!--   would remain without rows, although the adapter would have something to display.     -->
<!-- ====================================================================================== -->
<!-- THE TREE STRUCTURE (11 IDs declared, 9 used by the code):                              -->
<!--   MaterialCardView                          root = itemView (the whole card)            -->
<!--     +- LinearLayout, horizontal, padding 12dp                                         -->
<!--         +- ImageView    moviePoster         96 x 140dp                                -->
<!--         +- LinearLayout, vertical, 0dp + weight 1                                      -->
<!--             +- TextView   movieTitle        20sp, bold, max 2 lines                    -->
<!--             +- TextView   movieSubtitle     14sp, grey                                 -->
<!--             +- LinearLayout, horizontal                                                -->
<!--             |    +- RatingBar  movieRating      5 stars, indicator                     -->
<!--             |    +- TextView   movieRatingValue “4.5”                                  -->
<!--             +- TextView   movieFacts        “142 min · $160M”                          -->
<!--             +- ChipGroup  movieStatusGroup                                            -->
<!--                 +- Chip   chipApproval      “Approved”                                 -->
<!--                 +- Chip   chipWatched       “Watched” + icon                           -->
<!--                 +- Chip   chipWatchlist     “Watchlist”                                -->
<!--                 +- Chip   chipCiocan        @string/chip_ciocan_name                  -->
<!-- ====================================================================================== -->
<!-- MATERIALCARDVIEW — the row's root.                                                     -->
<!-- WHY A CARD and not a LinearLayout: each row is an independent visual unit, with        -->
<!--   its own corners and shadow. A plain LinearLayout would look like a table.            -->
<!-- layout_width="match_parent" — the row takes the list's full width.                     -->
<!-- layout_height="wrap_content" — the content gives the height (the 140dp poster).        -->
<!-- layout_marginHorizontal="12dp" / layout_marginVertical="6dp" — air around the card.    -->
<!-- RISK: marginHorizontal and marginVertical were introduced in API 26. With minSdk 24     -->
<!--   (from build.gradle.kts), on Android 7.0–7.1 they are ignored: the card touches the edges. -->
<!-- cardCornerRadius="16dp" — rounded corners; cardElevation="3dp" — shadow.              -->
<!-- cardUseCompatPadding="true" — internal padding so the shadow is not clipped on old APIs. -->
<!-- NOTE: the root has NO android:id. It does not need one: itemView in the ViewHolder is   -->
<!--   this very card, and the adapter does not look it up with findViewById.               -->
<!-- ====================================================================================== -->
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

    <!-- HORIZONTAL LINEARLAYOUT — poster on the left, information on the right. -->
    <!-- padding="12dp" — the content does not touch the card's edge. -->
    <!-- WHY horizontal: the poster and the text column sit side by side, as in a poster. -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="12dp">

        <!-- Poster -->
        <!-- IMAGEVIEW — the movie's poster. -->
        <!-- 96 x 140dp — ratio ~2:3, like a poster. FIXED dimensions: the poster does not  -->
        <!--   change size according to the text on the right.                              -->
        <!-- background="#11000000" — black with alpha 0x11 (~7% opacity). The format is     -->
        <!--   #AARRGGBB: alpha first, then red, green, blue.                               -->
        <!-- scaleType="centerCrop" — fills the 96x140dp cropping the edges, without        -->
        <!--   distorting. fitXY would stretch the image; centerInside would leave empty bands. -->
        <!-- contentDescription="Movie poster" — the text read by TalkBack. -->
        <!-- src="@android:drawable/ic_menu_gallery" — a provisional image, from the system  -->
        <!--   resources, not from the project.                                             -->
        <!-- RISK: the adapter looks this view up in the holder (the `poster` field) but NEVER -->
        <!--   fills it. On screen the gallery icon always appears, for any movie.           -->
        <ImageView
            android:id="@+id/moviePoster"
            android:layout_width="96dp"
            android:layout_height="140dp"
            android:background="#11000000"
            android:scaleType="centerCrop"
            android:contentDescription="Movie poster"
            android:src="@android:drawable/ic_menu_gallery" />

        <!-- Info column -->
        <!-- THE INFORMATION COLUMN — 0dp + weight 1. -->
        <!-- WHY 0dp: the width is not fixed; it takes all the rest left after the poster. -->
        <!-- WHY weight="1": the only child with weight receives all the free space. Without -->
        <!--   it, 0dp would mean zero width and the text would disappear. -->
        <!-- marginStart="12dp" — separates the text from the poster; `start` respects RTL. -->
        <!-- orientation="vertical" — the elements flow from top to bottom. -->
        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:layout_marginStart="12dp"
            android:orientation="vertical">

            <!-- THE TITLE — movieTitle. -->
            <!-- textSize="20sp" + textStyle="bold" — a strong hierarchy; the title is -->
            <!--   the row's main element. -->
            <!-- maxLines="2" — at most two lines. -->
            <!-- ellipsize="end" — if it does not fit, it is cut with “...” at the end. Without it, -->
            <!--   the text would be cut brutally at the edge. -->
            <!-- android:text="Movie title" — PLACEHOLDER. Here the adapter writes -->
            <!--   movie.getTitle(), so the XML value is not seen at runtime. -->
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
            <!-- THE SUBTITLE — movieSubtitle. -->
            <!-- textSize="14sp" — secondary to the title; marginTop="2dp" — glued to it. -->
            <!-- textColor="#757575" — a hardcoded grey. The correct way would be ?attr/colorOnSurfaceVariant, -->
            <!--   so that it adapts to dark mode. Here it is a fixed colour. -->
            <!-- PLACEHOLDER: the adapter writes “genre. year” — with a dot, not with “·” as in the XML. -->
            <TextView
                android:id="@+id/movieSubtitle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Genre · Year"
                android:textSize="14sp"
                android:textColor="#757575" />

            <!-- Rating -->
            <!-- THE RATING ROW — horizontal, vertically centred. -->
            <!-- gravity="center_vertical" — the stars and the number line up on the middle -->
            <!--   of the height, not at the top. -->
            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <!-- RATINGBAR — the stars. -->
                <!-- style="?android:attr/ratingBarStyleSmall" — the small variant, with stars -->
                <!--   of ~14dp; a system style, not Material. -->
                <!-- numStars="5" — five stars; stepSize="0.5" — half stars. -->
                <!-- isIndicator="true" — it only displays, it cannot be changed by -->
                <!--   touch. Without it, the user would change each row's score. -->
                <!-- RISK: there is no android:rating and the adapter sets nothing, so -->
                <!--   ALL the rows show zero stars, whatever the score in the model. -->
                <RatingBar
                    android:id="@+id/movieRating"
                    style="?android:attr/ratingBarStyleSmall"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:numStars="5"
                    android:stepSize="0.5"
                    android:isIndicator="true" />

                <!-- THE NUMERIC VALUE — movieRatingValue, the number to the right of the stars. -->
                <!-- textSize="13sp", grey; marginStart="6dp" — separates it from the stars. -->
                <!-- BUG: the value is the static “4.5” from the XML and is not written by -->
                <!--   the adapter. All the rows show 4.5, regardless of the movie. -->
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
            <!-- “FACTS” — the duration and the budget, on a single line of text. -->
            <!-- The example in the XML: “142 min  ·  $160M” (two spaces before the separator). -->
            <!-- textSize="13sp", light grey (#9E9E9E) — the most secondary information. -->
            <!-- BUG: this text is static too. The adapter does not write it, so all
            <!--   three movies display the same duration and the same budget. -->
            <TextView
                android:id="@+id/movieFacts"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="142 min  ·  $160M"
                android:textSize="13sp"
                android:textColor="#9E9E9E" />

            <!-- Status chips: approval, watched, watchlist -->
            <!-- CHIPGROUP — the labels' container. -->
            <!-- match_parent — it has the column's full width; marginTop="8dp" — separates it from -->
            <!--   the text above. -->
            <!-- chipSpacingHorizontal="6dp" — 6dp between the labels. -->
            <!-- singleLine="false" — if they do not fit on one line, they wrap to the next. -->
            <!-- NOTE: the group has an ID (movieStatusGroup) but the adapter does NOT look it up. -->
            <com.google.android.material.chip.ChipGroup
                android:id="@+id/movieStatusGroup"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                app:chipSpacingHorizontal="6dp"
                app:singleLine="false">

                <!-- CHIP 1 — the parental guidance (“Approved”). -->
                <!-- style="@style/Widget.Material3.Chip.Suggestion" — the Material 3 style -->
                <!--   for suggestion labels: a discreet background, no outline. -->
                <!-- android:text="Approved" — static text. Here -->
                <!--   movie.getApproval() should appear: “PG-13”, “R”, “G”. -->
                <!-- android:clickable="false" — the label is not pressed. WHY IT MATTERS: -->
                <!--   without it, the Chip would consume the touch, and the row click (bound -->
                <!--   on itemView) would no longer fire when you press exactly on the label. -->
                <!-- chipMinHeight="28dp" — shorter than the standard (32dp by default). -->
                <!-- ensureMinTouchTargetSize="false" — it accepts a touch target below 48dp. -->
                <!--   Here that is fine: the label is not pressed anyway. -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipApproval"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Approved"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />

                <!-- CHIP 2 — “Watched”. -->
                <!-- The only difference from the first: app:chipIcon, a tick from the system -->
                <!--   resources (@android:drawable/checkbox_on_background). -->
                <!-- Static text: it should depend on movie.isWatched(). -->
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

                <!-- CHIP 3 — “Watchlist”. -->
                <!-- Static text: it should depend on movie.isOnWatchlist(). -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipWatchlist"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Watchlist"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />

                <!-- CHIP 4 — chipCiocan. -->
                <!-- The text comes from @string/chip_ciocan_name — a text resource, not a -->
                <!--   literal. It is the only chip without text written directly in the layout. -->
                <!-- NOTE: the ID does not appear in MovieViewHolder, so this chip is never -->
                <!--   modified from code. It is a fourth decorative label. -->
                <!-- WATCH the spacing: "false"/> — no space before />. It is -->
                <!--   the only chip written like this; the file is exactly as it was saved. -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipCiocan"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="@string/chip_ciocan_name"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false"/>
            </com.google.android.material.chip.ChipGroup>
        </LinearLayout>
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

**What is seen on screen and why.** The faithful result of this layout, with the adapter from 38.2, is the following — it is worth reading as a diagnosis, not as a sketch:

| Element | The displayed value | Comes from |
|---|---|---|
| title | “Inception” / “Toy Story” / “The Matrix” | **model** (`getTitle()`) |
| subtitle | “Sci-Fi. 2010”, “Animation. 1995”, “Action. 1999” | **model** (`getGenre()`, `getRelease()`) |
| stars | 0 stars, for all of them | XML (`android:rating` is missing) |
| rating value | “4.5”, for all of them | XML (placeholder) |
| facts | “142 min · $160M”, for all of them | XML (placeholder) |
| chip 1 | “Approved”, for all of them | XML |
| chip 2 | “Watched”, for all of them | XML |
| chip 3 | “Watchlist”, for all of them | XML |
| chip 4 | the text from `@string/chip_ciocan_name` | XML (resource) |
| poster | the gallery icon, for all of them | XML (`@android:drawable/...`) |

Two elements are correct, nine are identical on every card. It is exactly the kind of defect you discover by reading `onBindViewHolder` **and** the layout together — neither one alone shows it.

---

## 38.6 `activity_main.xml` — RecyclerView and the second FAB

Compared with the old version, two changes: `ListView` became `RecyclerView`, and the single FAB became two. The rest of the skeleton — `FrameLayout` with `id=main` for the insets — is identical.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FILE: activity_main.xml — THE LIST SCREEN                                             -->
<!-- ====================================================================================== -->
<!-- WHAT IT IS: a FrameLayout with three children: RecyclerView (fills everything), the    -->
<!--   insert FAB (bottom-right) and the FAB towards the test screen (bottom-left).         -->
<!-- WHY IT EXISTS: it is the only layout that contains the list. The complexity of a row   -->
<!--   is in movie_item.xml; here there is only the skeleton.                               -->
<!-- WHO DEPENDS ON IT: MainActivity — through R.layout.activity_main and three IDs:        -->
<!--   main, rvMovies, floatingActionButton.                                               -->
<!-- WHAT IT DOES NOT DO: it does not define what a row looks like (that comes from movie_item.xml)
<!--   and does not set the order (LinearLayoutManager does that).                          -->
<!-- WHAT BREAKS WITHOUT IT: setContentView would have nothing to load; findViewById(R.id.main) -->
<!--   would return null and the insets listener would throw a NullPointerException.        -->
<!-- ====================================================================================== -->
<!-- FRAMELAYOUT — the root container. -->
<!-- WHY FrameLayout and not LinearLayout: the children must OVERLAP. The buttons          -->
<!--   float over the list; a LinearLayout would put them one next to the other (or one under -->
<!--   the other), and the FABs would no longer float.                                      -->
<!-- WHY not ConstraintLayout: for three children, FrameLayout is enough and                -->
<!--   cheaper to read.                                                                    -->
<!-- THE ORDER OF THE CHILDREN IS MEANINGFUL: each child is drawn over the previous one.    -->
<!--   RecyclerView is FIRST, so it sits underneath; the FABs come over it.                -->
<!-- ATTRIBUTES: xmlns:android = framework; xmlns:app = libraries (Material); xmlns:tools   -->
<!--   = preview only, removed at build.                                                    -->
<!-- android:id="@+id/main" — the container on which the insets padding is applied.          -->
<!--   @+id/ CREATES the ID; @id/ would REFER to an existing one.                           -->
<!-- android:orientation="horizontal" — INVALID ATTRIBUTE on FrameLayout: `orientation`     -->
<!--   exists only on LinearLayout. It is IGNORED by Android and produces a lint warning    -->
<!--   (“Unknown attribute”). Harmless noise, left over from a previous LinearLayout. It    -->
<!--   changes nothing at runtime and is not worth “fixing” unless you are explicitly asked. -->
<!-- tools:context — only for the preview: which activity lends its theme in the editor.    -->
<!-- WHY android:id="@+id/main" IS MANDATORY: the code calls findViewById(R.id.main)        -->
<!--   for the insets listener. Without an ID, the call would return null and               -->
<!--   setOnApplyWindowInsetsListener(null, ...) would throw a NullPointerException.        -->
<!-- ====================================================================================== -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!-- RECYCLERVIEW — the list. -->
    <!-- The class's full name is mandatory: RecyclerView is not part of the
    <!--   framework widgets, but of the AndroidX library. In XML you write the
    <!--   class's full path. -->
    <!-- android:id="@+id/rvMovies" — looked up in initControls, where it receives
    <!--   a LayoutManager and an adapter. -->
    <!-- layout_width/height = match_parent — the list fills the screen, including the area under
    <!--   the buttons. The buttons are drawn OVER it, not next to it. -->
    <!-- WHAT IT DOES NOT HAVE, UNLIKE LISTVIEW: -->
    <!--   - no android:entries: RecyclerView does not know how to build its own
    <!--     rows from resources; it needs an adapter; -->
    <!--   - no tools:listitem: the preview attribute that would show in the editor what
    <!--     a row looks like. Without it, the preview appears empty. It does not affect runtime. -->
    <!-- RISK: because the list stretches over the whole screen, and the buttons are drawn over -->
    <!--   it, the last row can sit under the FABs. The correct remedy is paddingBottom on -->
    <!--   the list + clipToPadding="false". -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvMovies"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

    <!-- FAB 1 — the insert. -->
    <!-- layout_gravity="bottom|end" — bottom, right. `end` respects the reading direction;
    <!--   in RTL it becomes left. `right` would be fixed and wrong in RTL. -->
    <!-- layout_margin="16dp" — 16dp from the safe area (the insets padding is applied
    <!--   on R.id.main, not on the FAB). -->
    <!-- contentDescription="Add" — the text read by TalkBack. Mandatory for a button
    <!--   with no visible text; without it, lint gives the “ContentDescription” error. -->
    <!-- app:srcCompat — the compatible variant for vector images; it supports vectors
    <!--   on all versions, unlike android:src. -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_24" />

    <!-- FAB 2 — btnVlad, the button towards the test screen. -->
    <!-- It is NEW compared with the old version. It sits on the opposite side from the first:
    <!--   bottom|start — bottom, left. -->
    <!-- android:clickable="true" — redundant: FloatingActionButton is clickable by
    <!--   construction. It does not appear on the first FAB; here it was added explicitly. -->
    <!-- contentDescription="Ciocan" — again, for TalkBack. -->
    <!-- app:srcCompat="@drawable/buton_ciocan" — the project's own icon. -->
    <!-- WHY it exists: it opens PlaceCiocanul, the test screen (38.4). The binding is done
    <!--   in initSecondListener, through the same launcher. -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/btnVlad"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:clickable="true"
        android:layout_margin="16dp"
        android:contentDescription="Ciocan"
        android:layout_gravity="bottom|start"
        app:srcCompat="@drawable/buton_ciocan"/>
</FrameLayout>
```

**The drawing order in `FrameLayout`:**

```
        +--------------------------------------+
        |  RecyclerView  (first child)         |   <- drawn FIRST, underneath
        |  [card Inception]                    |
        |  [card Toy Story]                    |
        |  [card The Matrix]                   |
        |                                      |
        |  (FAB)                       (FAB)   |   <- drawn OVER the list
        +---[btnVlad]--------[+]--------------+
             bottom|start   bottom|end

  Child 1 = RecyclerView   -> the background
  Child 2 = FAB “+”        -> over the list
  Child 3 = FAB “hammer”   -> over the list, on the left
```

**Reference table for the two FABs:**

| | `floatingActionButton` | `btnVlad` |
|---|---|---|
| position | `bottom\|end` (right) | `bottom\|start` (left) |
| icon | `@drawable/outline_add_24` | `@drawable/buton_ciocan` |
| `contentDescription` | “Add” | “Ciocan” |
| `clickable` | implicit | `"true"` explicit (redundant) |
| opens | `ItemActivity` (insert) | `PlaceCiocanul` |
| listener | `initListeners()` | `initSecondListener()` |
| launcher | the same | the same |

---

## 38.7 `activity_place_ciocanul.xml` — the new screen's layout

This is a **skeleton**, not a functional screen: `PlaceCiocanul.java` uses only two of the four views, and the `RecyclerView` here does not even have an ID. It is worth reading for the three signals an unfinished layout gives.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FILE: activity_place_ciocanul.xml — THE TEST SCREEN                                    -->
<!-- ====================================================================================== -->
<!-- WHAT IT IS: the layout of the PlaceCiocanul screen. It contains a RecyclerView without an ID, a FAB, -->
<!--   a narrow ProgressBar and nothing else.                                               -->
<!-- WHY IT EXISTS: it is the skeleton of the new screen brought in version 2. Two views     -->
<!--   are used from it: the main container (for the insets) and the FAB (for the Toast).   -->
<!-- WHO DEPENDS ON IT: PlaceCiocanul.java — through R.layout.activity_place_ciocanul,       -->
<!--   R.id.main and R.id.floatingActionButton2.                                            -->
<!-- WHAT IT DOES NOT DO: it displays no list (the RecyclerView has no ID, so it cannot be  -->
<!--   configured from code) and displays no progress (the ProgressBar is bound to          -->
<!--   nothing).                                                                            -->
<!-- WHAT BREAKS WITHOUT IT: setContentView(R.layout.activity_place_ciocanul) would not compile. -->
<!-- ====================================================================================== -->
<!-- RELATIVELAYOUT — the root container. -->
<!-- WHY RelativeLayout: the children are positioned through relative rules (“above      -->
<!--   X”, “to the right of the parent”). Here, however, NO rule is used, so                -->
<!--   it is a container without a purpose — a FrameLayout would be equivalent.             -->
<!-- android:id="@+id/main" — used by findViewById(R.id.main) for the insets.               -->
<!-- android:orientation="vertical" — INVALID ATTRIBUTE on RelativeLayout: it exists only on -->
<!--   LinearLayout. Ignored at runtime; noise, exactly as in activity_main.xml.            -->
<!-- tools:context — only for the preview.                                                 -->
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".activities.PlaceCiocanul"
    android:orientation="vertical">

    <!-- RECYCLERVIEW WITHOUT AN ID — skeleton. -->
    <!-- wrap_content / wrap_content — if it had content, it would size itself after it;
    <!--   like this, with zero rows, it is 0x0. -->
    <!-- PROBLEM 1: it has no android:id. Without an ID it cannot be found with findViewById, so
    <!--   no code can give it a LayoutManager or an adapter. -->
    <!-- PROBLEM 2: without a LayoutManager, a RecyclerView draws nothing and writes to
    <!--   Logcat “No layout manager attached; skipping layout”. -->
    <!-- Conclusion: it is a space holder for a future screen, not a list. -->
    <androidx.recyclerview.widget.RecyclerView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />

    <!-- FAB — the only functional view. -->
    <!-- android:id="@+id/floatingActionButton2" — looked up in onCreate as btn2. -->
    <!-- android:clickable="true" — redundant, as at btnVlad on the main screen. -->
    <!-- app:srcCompat="@drawable/outline_add_24" — the same icon as the insert
    <!--   FAB. Here it adds nothing; it is inherited. -->
    <!-- tools:layout_editor_absoluteX / absoluteY — editor-ONLY attributes: the guides
    <!--   used by the layout editor to place the view on the canvas. They do NOT exist at runtime
    <!--   and are removed at build. -->
    <!-- RISK: because there is no layout_alignParent* / layout_center* and no
    <!--   layout_gravity, the child is placed by default in the top-left corner (0,0) — not
    <!--   where the preview shows it (334dp, 655dp). -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:clickable="true"
        app:srcCompat="@drawable/outline_add_24"
        tools:layout_editor_absoluteX="334dp"
        tools:layout_editor_absoluteY="655dp" />

    <!-- PROGRESSBAR — skeleton. -->
    <!-- style="?android:attr/progressBarStyle" — the system's default style: an animated,
    <!--   indeterminate circle. -->
    <!-- layout_width="6dp" — the width is 6dp, while the height is wrap_content.
    <!--   The result: a squashed circle, almost invisible. The correct way would be wrap_content on
    <!--   both axes. -->
    <!-- It is bound to no code: it has no ID and is not started/stopped from anywhere. -->
    <ProgressBar
        style="?android:attr/progressBarStyle"
        android:layout_width="6dp"
        android:layout_height="wrap_content" />

</RelativeLayout>
```

**The three signals of an unfinished layout:**

| Signal | Here | What it means |
|---|---|---|
| view without an ID | the `RecyclerView` | the code can never configure it |
| degenerate size | `ProgressBar` 6dp wide | visually it is not seen; it makes no functional sense |
| attribute of another container | `android:orientation` on `RelativeLayout` | a leftover from a previous `LinearLayout` |

**Why it is not a compile error.** All three are perfectly legal for `aapt2`: the XML is valid, the resources are generated, the app starts, the FAB works. The defects are of **intent**, not of syntax — exactly the category that passes the build and is only seen when someone opens the screen.

---

## 38.8 `AndroidManifest.xml` — three activities

The only file that is neither code nor layout: it is the **contract with the operating system**. Here you declare what components the app has, which is the entry point, what theme it uses and what backup it is allowed to make.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FILE: AndroidManifest.xml — THE CONTRACT WITH THE SYSTEM                               -->
<!-- ====================================================================================== -->
<!-- WHAT IT IS: the app's component declaration: three activities, the theme, the icons,   -->
<!--   the backup rules. It contains no executable code.                                    -->
<!-- WHY IT EXISTS: Android does not “discover” the classes. An activity that is not declared -->
<!--   here simply cannot be started — neither from the launcher, nor with an Intent.       -->
<!-- WHAT IT DOES NOT DO: it contains no `package`. Starting with AGP 8, the app's identity comes from -->
<!--   namespace + applicationId in build.gradle.kts. The relative names here               -->
<!--   (.activities.MainActivity) are resolved against that namespace.                     -->
<!-- WHAT BREAKS WITHOUT IT: the app would not install. And without exported="true" on      -->
<!--   the LAUNCHER activity, the icon would exist, but would start nothing.                -->
<!-- ====================================================================================== -->
<!-- THE ROOT. xmlns:tools is needed for the tools: attributes (none appears here,          -->
<!--   but the namespace is kept from the template generated by Android Studio).            -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- THE APPLICATION — the global attributes. -->
    <!--   allowBackup="true"                      the system can save the app's data -->
    <!--   dataExtractionRules="@xml/data_extraction_rules"   rules for Android 12+ -->
    <!--   fullBackupContent="@xml/backup_rules"   rules for Android 11 and older -->
    <!--   icon / roundIcon                        the icons from mipmap -->
    <!--   label="@string/app_name"                the name displayed under the icon -->
    <!--   supportsRtl="true"                      supports a mirrored layout for RTL -->
    <!--   theme="@style/Theme.Group1098"          the global theme, inherited by the activities -->
    <!--     that do not set their own -->
    <!-- NOTE: no permission is declared. The app does not use the network, -->
    <!--   the camera or storage — so it needs no <uses-permission>. -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.Group1098">

        <!-- ACTIVITY 1 — MainActivity, THE ENTRY POINT. -->
        <!-- android:name=".activities.MainActivity" — the leading dot is a
        <!--   shorthand: the full class becomes com.example.group1098.activities.
        <!--   MainActivity, where the prefix comes from the namespace.           -->
        <!-- android:exported="true" — MANDATORY here. From Android 12 (API 31), any -->
        <!--   component with an intent-filter must declare exported explicitly; otherwise -->
        <!--   the app DOES NOT INSTALL. `true` = it can be started from outside -->
        <!--   the app, exactly what the launcher does.                          -->
        <!-- android:windowSoftInputMode="adjustResize" — when the keyboard appears, the window -->
        <!--   shrinks instead of being covered. Here there are no text fields, -->
        <!--   but the attribute is kept uniformly.                              -->
        <!-- INTENT-FILTER — the recipe by which the system recognises the start screen: -->
        <!--   action MAIN = “start the app”; category LAUNCHER = “show it in -->
        <!--   the launcher”. Without this block, the app would install and could not be -->
        <!--   started from the icon.                                             -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ACTIVITY 2 — ItemActivity, the form. -->
        <!-- exported="false" — it can be started ONLY from inside the app. It is
        <!--   correct: nobody outside has anything to look for in a form that receives
        <!--   a Movie. Contrary to appearances, `false` does not prevent the explicit Intent from
        <!--   MainActivity: that one works because it comes from the same package. -->
        <!-- windowSoftInputMode="adjustResize" — HERE it matters: the form has four
        <!--   EditTexts, a spinner, a SeekBar, a RatingBar, a RadioGroup, two
        <!--   checkboxes and a switch. Without the attribute, the keyboard would cover the lower fields. -->
        <!-- Undeclared, launcher.launch(intent) would throw ActivityNotFoundException at
        <!--   runtime — with no compile error at all. -->
        <activity
            android:name=".activities.ItemActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />

        <!-- ACTIVITY 3 — PlaceCiocanul, the test screen. -->
        <!-- It is version 2's ADDITION. Without this entry, the btnVlad FAB would throw
        <!--   ActivityNotFoundException on the first click. -->
        <!-- exported="false" — like ItemActivity: it is started only from the app. -->
        <!-- windowSoftInputMode="adjustResize" — uniform, although the screen has no fields. -->
        <activity
            android:name=".activities.PlaceCiocanul"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**The three activities, at a single glance:**

```
AndroidManifest.xml
 |
 |-- MainActivity      exported = true    LAUNCHER (MAIN)     <- entry from the icon
 |-- ItemActivity      exported = false   no intent-filter    <- internal Intent only
 +-- PlaceCiocanul     exported = false   no intent-filter    <- internal Intent only

  Who can start what:
     the system launcher     ->  MainActivity  (the only exported one)
     MainActivity            ->  ItemActivity  (explicit Intent, same package)
     MainActivity            ->  PlaceCiocanul (explicit Intent, same package)
     any other app           ->  NOTHING
```

**Three things that are not visible in the file and are asked at the exam:**

1. **Why is there no `package="..."`?** Because AGP 8 moved the app's identity into `build.gradle.kts`: `namespace` gives the name of the `R` class, and `applicationId` gives the system identifier. The manifest uses relative names, which are resolved against `namespace`.
2. **Why is `exported` mandatory?** From API 31, a component with an `intent-filter` and no explicit `exported` blocks the installation. It is one of the few errors that show at install time, not at compile time.
3. **Why `adjustResize` on all three?** For uniformity. It really matters only on `ItemActivity`, the only one with text fields; but a consistent attribute is easier to read than one placed “where it belongs”.

---

## 38.9 What to retain from each file

| File | The essence | The trap |
|---|---|---|
| `MainActivity.java` | the order in `onCreate`; `RecyclerView` + `LayoutManager` + `setAdapter`; the result callback; `notifyDataSetChanged` after `add`/`set` | `launcher` is assigned after the listeners; `getData()` is not checked for `null` |
| `MovieAdapter.java` | the contract with three methods; `ViewHolder` as a `findViewById` cache; click on `itemView` with `NO_POSITION` | only 2 of 9 views are filled — the card displays static data |
| `IMovieListener.java` | the click contract; the adapter does not know the activity | if you change the signature, it breaks in two places (adapter + activity) |
| `PlaceCiocanul.java` | the third screen; `WindowCompat.enableEdgeToEdge`; `Toast` | `String.valueOf(R.string.app_name)` returns the numeric ID, not the text |
| `movie_item.xml` | the row's card; 11 IDs, 9 used; non-clickable chips so the click passes to the card | the placeholders from the XML reach the screen if the adapter does not write them |
| `activity_main.xml` | `FrameLayout` with the list underneath and two FABs on top | `android:orientation` invalid; the last row can sit under the FABs |
| `activity_place_ciocanul.xml` | skeleton: `RecyclerView` without an ID, 6dp `ProgressBar` | `tools:layout_editor_absoluteX/Y` have no effect at runtime |
| `AndroidManifest.xml` | three activities; only `MainActivity` exported, with LAUNCHER | an undeclared activity = `ActivityNotFoundException` at runtime |

### The 10 things you will have been asked

1. **Why `RecyclerView` and not `ListView`?** Automatic recycling through `ViewHolder`, a separate layout manager, implicit animations, fine-grained notifications per position.
2. **Why `setLayoutManager` before `setAdapter`?** Without a layout manager, `RecyclerView` does not know how to arrange the rows and draws nothing.
3. **Why two methods, `onCreateViewHolder` and `onBindViewHolder`?** The inflate is expensive and is done once; binding the data is cheap and is done on every reappearance.
4. **How does the click reach the activity?** Through `IMovieListener`: the adapter calls the interface, `MainActivity` implements it. The adapter does not know who the recipient is.
5. **Why `this` in `new MovieAdapter(movies, this)`?** Because `MainActivity` implements `IMovieListener`; `this` is the callback itself.
6. **Why `getAbsoluteAdapterPosition()` on click?** The position can change between bind and click; the method requests it at the moment of the event and can return `NO_POSITION`.
7. **Why `inflate(..., parent, false)`?** The third argument `false` = do not attach now; the `RecyclerView` attaches by itself. With `true`, the view would be added twice.
8. **Why `notifyDataSetChanged()` after every change?** Because the adapter does not observe the `ArrayList`; it must be notified. The fine-grained variant is `notifyItemInserted` / `notifyItemChanged`.
9. **Why `android:clickable="false"` on the chips?** So that they do not consume the touch; otherwise the row click would not fire when you press exactly on the label.
10. **Why is `String.valueOf(R.string.app_name)` wrong?** `R.string.*` is an `int` (a resource ID); `String.valueOf` turns it into digits. The correct way is `getString(...)`.

---

## Chapter 38 summary

- Version 2 changes **only the list screen** and its bindings: widget, adapter, click, row layout, manifest. `Movie.java` and `ItemActivity.java` are identical to the old version apart from the package lines, and `activity_item.xml` is identical with no difference at all.
- `RecyclerView` requires three things that `ListView` did not: a **layout manager**, an **adapter of your own** and, for the click, a **callback written by you**.
- The adapter has exactly three mandatory methods; `ViewHolder` is the `findViewById` cache, and `onBindViewHolder` is the only place where the data reaches the UI.
- `MainActivity implements IMovieListener` and passes itself to the adapter: the activity is the recipient of the click.
- The order in `onCreate` is not cosmetic: `addSampleMovies` -> adapter -> `initControls` -> listeners -> `registerForActivityResult`.
- The old code kept commented out shows the migration live: `ListView`, `ArrayAdapter` and `setOnItemClickListener` are exactly the three things that `RecyclerView` removes.
- Three real defects, all with no compile error: the card displays static data for seven of the nine views, `PlaceCiocanul` turns a resource ID into digits, and `activity_place_ciocanul.xml` is a skeleton with a `RecyclerView` without an ID.
- Two harmless noises, to be flagged and left alone: `android:orientation` on `FrameLayout` (38.6) and on `RelativeLayout` (38.7).

**Back to** [cheatsheet](21%20-%20Cheatsheet.md) **or to** [the overview](index.html).
