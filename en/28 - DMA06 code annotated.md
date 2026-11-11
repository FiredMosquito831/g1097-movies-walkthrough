# Chapter 28 — The DMA06 code, annotated

**Objective:** to read the 14 files of the `DMA06` project with the explanation glued to every line — what it does, why it is there, what breaks if you remove it. The app displays the same numbers from 1 to 100 in three ways, so you can see exactly what each step adds.

**Source:** `DMA06/` at commit `d719ffc` — 14 files, of which 7 Java and 7 XML.

**What you learn from it:** the three steps on the same data — `ArrayAdapter`, `BaseAdapter` with a manual `ViewHolder`, `RecyclerView`. Plus the one question that comes up on the test every year: **why `getView` was split into two methods**.

**Estimated time:** 90–120 min (active reading, with the files open alongside).

> **How to read:** each file has **a single code block**, in source order, with all the commentary inside. Do not skip the comments to get to the code: the commentary *is* the material. The code in the blocks is **identical to the files in the repo**; everything after `//` or between `/* */` (respectively between `<!-- -->` in XML) was added for explanation.

**Legend:**

| Marker | Meaning |
|---|---|
| `Theory:` | what the course / the documentation says about the concept behind it |
| `Logic:` | what the code does concretely, step by step |
| `Risk:` | what breaks if it is missing or wrong |
| `Ref:` | the chapter in test 1 where the concept is explained at length |
| `DANGER!` | a mistake that compiles but crashes at runtime |

---

## How the chapter is organized

Each file has **a single code block**, in source order. They are not fragments: you can copy the block, put it in a `.java` or `.xml` file and it compiles. The comments are part of the block, so they do not interrupt the reading.

The order follows the app's flow, not alphabetical order:

```
1.  MainActivity.java            ← where you land first
2.  activity_main.xml            ← what you see first
3.  AndroidManifest.xml          ← what makes everything else possible
4.  NumberData.java              ← where the data comes from
5.  SingleColumnActivity.java    ← step 1
6.  activity_single_column.xml   ← step 1 layout
7.  NumberListAdapter.java       ← the core of step 2
8.  TwoColumnActivity.java       ← step 2 screen
9.  activity_two_column.xml      ← step 2 layout
10. layout_number_header.xml     ← the shared header
11. NumberRecyclerAdapter.java   ← the core of step 3
12. RecyclerViewActivity.java    ← step 3 screen
13. activity_recycler_view.xml   ← step 3 layout
14. item_number.xml              ← the row shared by steps 2 and 3
```

**Why `NumberListAdapter` before `TwoColumnActivity`:** because the activity is just an adapter builder. If you read the activity first, you see four lines and understand nothing; if you read the adapter first, the activity becomes obvious.

**Why `item_number.xml` at the end:** because it is the only file that belongs to steps 2 and 3 at the same time. Read at the beginning, it looks like any old layout; read at the end, it is the proof that the difference between the two steps is not in the XML.

**Three things you will look up more than once:**

| What you look for | Where it is |
|---|---|
| `if (convertView == null)` | 28.6, `NumberListAdapter.getView` |
| the three mandatory methods | 28.10, `NumberRecyclerAdapter` |
| `setLayoutManager` | 28.11, `RecyclerViewActivity.onCreate` |

---

## File map

| # | File | Role |
|---|---|---|
| 1 | `activities/MainActivity.java` | the menu with three buttons |
| 2 | `activities/SingleColumnActivity.java` | step 1 — `ListView` + `ArrayAdapter` |
| 3 | `activities/TwoColumnActivity.java` | step 2 — `ListView` + custom adapter |
| 4 | `activities/RecyclerViewActivity.java` | step 3 — `RecyclerView` |
| 5 | `adapters/NumberListAdapter.java` | `BaseAdapter` with a manual `ViewHolder` |
| 6 | `adapters/NumberRecyclerAdapter.java` | `RecyclerView.Adapter` |
| 7 | `data/NumberData.java` | the source: numbers 1–100 |
| 8 | `res/layout/activity_main.xml` | the three buttons |
| 9 | `res/layout/activity_single_column.xml` | a single `ListView` |
| 10 | `res/layout/activity_two_column.xml` | header + `ListView` |
| 11 | `res/layout/activity_recycler_view.xml` | header + `RecyclerView` |
| 12 | `res/layout/item_number.xml` | the two-column row |
| 13 | `res/layout/layout_number_header.xml` | the two-column header |
| 14 | `AndroidManifest.xml` | the declaration of the four activities |

Three packages, three responsibilities:

```
ro.ase.ie.dma06.activities   ← ties everything together, answers input, knows the Context
ro.ase.ie.adapters           ← turns data into rows; does not know which screen shows them
ro.ase.ie.data               ← produces data; does not know what a View, a Context or an Adapter is
```

> **Watch out for the packages:** the last two do **not** contain `dma06` in the declaration, even though the folders do. The detail is explained in 28.3 and it matters for the test — if you write `import ro.ase.ie.dma06.data.NumberData`, the code does not compile, because that class does not exist in that package.

**Why the package split matters here:** the three steps are *the same app* with three renderings. If `NumberData` had known about `Context`, you could not have tested it without an emulator. If the adapters had known about activities, you could not have swapped `ListView` for `RecyclerView` without touching the screen too. The separation is not cosmetic: it is the reason step 3 reuses exactly the same data and exactly the same XML row.

---

## 28.0 `MainActivity.java` — the menu

The file has 26 lines and does one single thing: it starts one of the three activities. It touches no list, no adapter, no data.

```java
/*
 * ======================================================================================
 * FILE: MainActivity.java
 * ======================================================================================
 * LOCATION: DMA06/src/main/java/ro/ase/ie/dma06/activities/MainActivity.java
 * PACKAGE:  ro.ase.ie.dma06.activities
 * ROLE:     the app menu. Three buttons, three activities. It touches no list,
 *           no adapter, no data. All it does is start the right screen.
 *
 * FILE STRUCTURE (3 parts):
 *   1. imports          — 6 lines
 *   2. onCreate         — 8 lines: inflates the layout, then three identical calls
 *   3. openOnClick      — 4 lines: findViewById + listener
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - `startActivity` returns nothing; the screens do not send a result back.
 *   - `Class<?>` is a class type, not an instance. `SingleColumnActivity.class` is the object.
 *   - `this` inside a lambda is MainActivity, not the lambda. That is why `new Intent(this, ...)` works.
 *
 * FLOW:
 *   MainActivity  ──btnStep1──▶  SingleColumnActivity    (ListView + ArrayAdapter)
 *                 ──btnStep2──▶  TwoColumnActivity      (ListView + NumberListAdapter)
 *                 ──btnStep3──▶  RecyclerViewActivity    (RecyclerView + NumberRecyclerAdapter)
 * ======================================================================================
 */

// ======================================================================================
// BLOCK 1 — THE PACKAGE AND THE IMPORTS
// ======================================================================================
// The package is what gives the class its full name: ro.ase.ie.dma06.activities.MainActivity.
// It must match the folder here (activities/), unlike the `data` and `adapters` packages,
// where it does not match — see 28.3.
// ======================================================================================

package ro.ase.ie.dma06.activities;                     // the package of the screens; all 4 activities live here

import android.content.Intent;                          // the object that describes "I am starting activity X"
import android.os.Bundle;                               // the saved state; not used here
import android.view.View;                               // the type returned by findViewById
import androidx.appcompat.app.AppCompatActivity;        // the base activity, with the AppCompat theme
import ro.ase.ie.dma06.R;                               // the class generated from resources

// `import android.view.View` although you build no View: it is the type of the local
// variable in openOnClick. findViewById has been generic since API 26: <T extends View> T findViewById(int).
// Here the compiler has nothing to infer T from, because the result is assigned to a
// variable declared explicitly as `View`. So `View` appears in the code and needs an import.
//
// Why AppCompatActivity and not Activity: it brings AppCompatDelegate, which applies the
// Material theme on any Android version and swaps the widgets at inflate time for the
// compatible variants (AppCompatTextView, AppCompatButton).
//
// `R` is generated, not written. The import carries the prefix from `namespace` (ro.ase.ie.dma06),
// not from the folder. If you change the namespace in build.gradle.kts, the import changes
// by itself on the next build — but you must know where it comes from.

// ======================================================================================
// THEORY BLOCK: THREE SCREENS, ONE MENU
// ======================================================================================
/*
 * 1. WHAT AN ACTIVITY IS
 *    -   A component with its own window. It has its own lifecycle and its own
 *        view tree.
 *    -   It is declared in AndroidManifest.xml. Without the declaration, startActivity throws
 *        ActivityNotFoundException at runtime, not at compile time.
 *
 * 2. HOW TO START ANOTHER ONE
 *    -   `startActivity(new Intent(context, Clasa.class))`.
 *    -   The explicit Intent (with a class) is the only safe way inside the same app.
 *    -   The current activity is NOT destroyed: it is stopped and left on the stack (back stack).
 *
 * 3. THE STACK, AT EVERY STEP
 *    [MainActivity]                       ← at launch
 *    [MainActivity, SingleColumnActivity] ← after clicking button 1
 *    [MainActivity]                       ← after Back
 *    MainActivity is NOT recreated on return: it receives onRestart → onStart → onResume.
 *    That is why the menu's onCreate runs only once per instance.
 *
 * 4. WHY A HELPER
 *    The three buttons differ in exactly two things: the id and the class. The rest is
 *    identical. A parameterized helper removes six duplicated lines and makes obvious
 *    what varies.
 *
 * DIAGRAM:
 *
 *   click btnStep1
 *     └─ OnClickListener.onClick(v)
 *          └─ startActivity(new Intent(this, SingleColumnActivity.class))
 *               ├─ ActivityManager receives the request
 *               ├─ PackageManager checks: does .activities.SingleColumnActivity exist?
 *               ├─ MainActivity.onPause()           ← stays on the stack
 *               ├─ SingleColumnActivity.onCreate()  ← NEW instance
 *               └─ SingleColumnActivity.onResume()  ← visible, receives input
 */

/** Opens each step of the demo. */
public class MainActivity extends AppCompatActivity {   // the only activity with a LAUNCHER intent-filter

    // ==================================================================================
    // METHOD 1 — onCreate
    // ==================================================================================
    // Theory:  the first method of the lifecycle; it runs once per instance.
    // Logic:   1. super.onCreate  2. setContentView  3. three openOnClick calls
    // Risk:    `super.onCreate` must come first; the AppCompat delegate needs it
    //          before the window is touched.
    // Ref:     chapter 15 (Application and lifecycle).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);             // 1. starts the parent's lifecycle
        setContentView(R.layout.activity_main);         // 2. inflates activity_main.xml into the window

        openOnClick(R.id.btnStep1, SingleColumnActivity.class);    // 3. button 1 → step 1
        openOnClick(R.id.btnStep2, TwoColumnActivity.class);       //    button 2 → step 2
        openOnClick(R.id.btnStep3, RecyclerViewActivity.class);    //    button 3 → step 3
    }

    // `@Override` — the method exists in Activity. The annotation does not change behaviour, but
    // it tells the compiler to check the signature. If you wrote onCreate(Bundle b, int x),
    // without @Override you would have a new method, which is never called.
    //
    // `protected`, not `public` — Activity.onCreate is protected. The method is called by
    // the framework, not by your code.
    //
    // `savedInstanceState` — null on the first start, a Bundle when the activity is recreated
    // (rotation, theme change, return after it was destroyed in the background). It is not
    // used here: the menu has no state.
    //
    // The order of the three lines is not negotiable. setContentView needs the window
    // created by super.onCreate. openOnClick needs the tree built by
    // setContentView, because findViewById searches inside it. Reversed, the first two throw
    // exceptions, the third returns null.

    // ==================================================================================
    // METHOD 2 — openOnClick
    // ==================================================================================
    // Theory:  a helper that receives the button id and the class to start.
    // Logic:   1. findViewById  2. setOnClickListener  3. startActivity(new Intent(...))
    // Risk:    `findViewById` returns `View`, not `Button`; if the id does not exist in the layout
    //          it returns null and `setOnClickListener` throws NullPointerException.
    // Ref:     chapter 04 (MainActivity - list).
    // ==================================================================================
    private void openOnClick(int buttonId, Class<?> activityClass) {
        View button = findViewById(buttonId);           // finds the button in the tree inflated at step 2
        button.setOnClickListener(v -> startActivity(new Intent(this, activityClass)));
        //                              ↑ lambda: `this` = MainActivity, so it is a valid Context
    }

    // Why a helper and not three identical blocks: the only things that differ between
    // the three buttons are the id and the class. The rest is the same code. If you added a
    // step 4, you would add one line, not seven.
    //
    // `Class<?>` — the second parameter of the Intent(Context, Class<?>) constructor is
    // the class of the component to start. `<?>` means "any class"; here all
    // three are activities, but the type does not enforce it. You could write
    // `Class<? extends Activity>` and you would get an extra check at compile time.
    //
    // `this` inside the lambda — inside a lambda expression, `this` remains the instance that surrounds
    // the lambda, that is MainActivity. Inside an anonymous class (new View.OnClickListener() {...}),
    // `this` would be the instance of the anonymous class, which is NOT a Context, and you would have to write
    // MainActivity.this. The lambda is shorter here exactly for this reason.
    //
    // `v -> startActivity(...)` — the parameter v is the view that received the click, that is
    // the button. It is not used: we already know which button it is, because the listener is installed on it.
    //
    // `startActivity` and not `launcher`: the screens of the three steps return nothing. You do not
    // need registerForActivityResult, because you are not waiting for a result.
    //
    // `View button` and not `MaterialButton`: the helper works with any view that has
    // setOnClickListener. findViewById returns the declared type; here it is View, because
    // the helper needs nothing specific to a button.
    //
    // ==================================================================================
    // WHAT HAPPENS ON BACK
    // ==================================================================================
    //
    //   SingleColumnActivity.onPause()
    //     → SingleColumnActivity.onStop()
    //     → SingleColumnActivity.onDestroy()        ← the instance dies
    //     → MainActivity.onRestart()
    //     → MainActivity.onStart()
    //     → MainActivity.onResume()                 ← the menu returns, WITHOUT onCreate
    //
    // Why it matters: the menu's onCreate does not run a second time, so neither
    // setContentView nor openOnClick repeat. The buttons keep their
    // listeners because the view tree was not destroyed.
    //
    // What would happen if MainActivity had been destroyed in the meantime (low memory):
    // on return, onCreate runs again, with a non-null savedInstanceState. It does not
    // matter here, because the menu has no state to restore.
    //
    // ==================================================================================
    // WHAT THIS FILE DOES NOT DO
    // ==================================================================================
    //
    //   -   It creates no adapter.
    //   -   It reads no list.
    //   -   It does not know what a ViewHolder is.
    //   -   It keeps no reference to the activities it starts.
    //
    // The last line matters: after startActivity, MainActivity has no connection
    // with the screen it started. It cannot read data from it, cannot find out when it closes,
    // cannot receive anything back. If you needed a result, you would use
    // registerForActivityResult — but none of the three steps returns anything.
}
```

**What you must remember from this file:** it contains no line of list code. All the complexity of the chapter is in the three classes it starts. The menu is the proof that `startActivity` and `Intent` are independent of what the next screen displays.

**Without the declaration in the manifest, the click crashes.** `startActivity` throws `ActivityNotFoundException` at runtime, not at compile time. The compiler does not know which activities exist in the app — the check happens at runtime, when `PackageManager` looks for the component.

---

## 28.1 `activity_main.xml` — the three buttons

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FILE: activity_main.xml
     ==================================================================================
     LOCATION: DMA06/src/main/res/layout/activity_main.xml
     ROLE:     the menu layout: two texts (title + subtitle) and three buttons.
     CONTAINS: 2 × TextView, 3 × MaterialButton
     IDS:      btnStep1, btnStep2, btnStep3   ← the only ones touched from code
     ================================================================================== -->

<!-- Why the XML needs a header: a layout is rarely read top to bottom; usually
     you look it up by an id. The header tells you in three lines which ids exist, so you do not
     scroll 40 lines to find out whether the button is called btnStep1 or button1. -->

<!-- Root: a vertical column, with the group of children centred vertically and padding on all sides. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center_vertical"
    android:orientation="vertical"
    android:padding="24dp">

    <!-- The screen title: "From ListView to RecyclerView" (from strings.xml) -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/main_heading"
        android:textAppearance="?attr/textAppearanceHeadlineSmall" />

    <!-- The subtitle: "The numbers from 1 to 100, displayed in three steps." -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:layout_marginBottom="24dp"
        android:text="@string/main_description"
        android:textAppearance="?attr/textAppearanceBodyMedium" />

    <!-- Button 1: the id btnStep1 is looked up in MainActivity.openOnClick -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="@string/step1_title" />

    <!-- Button 2: 8dp below the first -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep2"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="@string/step2_title" />

    <!-- Button 3: 8dp below the second -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep3"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="@string/step3_title" />
</LinearLayout>

<!-- ======================================================================================
     WHAT TO REMEMBER FROM THE FILE
     ======================================================================================
     orientation="vertical"      the children stack one under another, in file order
     gravity="center_vertical"   centres the GROUP of children, not each child
     layout_gravity              would position the view inside its parent — a different attribute!
     padding="24dp"              inner margin on all four sides
     match_parent on the buttons as wide as the screen; wrap_content would make them uneven
     @+id/btnStep1               `+` = creates the id if it does not exist
     MaterialButton              full name, because it is not in android.widget
     ?attr/...                   attribute resolved from the current theme (Material3)
     @string/...                 text from a resource file, translatable
     layout_marginTop="8dp"      space between buttons, not padding inside them
     ====================================================================================== -->
```

**`layout_width="match_parent"` on the buttons** — buttons as wide as the screen, perfectly aligned. `wrap_content` would make them as wide as their text, and the three would have different widths — visibly ugly, because the texts have different lengths ("Step 1: ListView" vs "Step 3: RecyclerView").

**The texts come from `strings.xml`**, they are not written in the XML: `main_heading`, `main_description`, `step1_title`, `step2_title`, `step3_title`. A hardcoded text would raise a lint warning and could not be translated.

**`?attr/textAppearanceHeadlineSmall`** — the title style from the Material3 theme. `Theme.AdaptersDemo` has the parent `Theme.Material3.DayNight`, so all the `?attr/...` attributes resolve. `?attr` means "look the attribute up in the current theme", as opposed to `@style` which means "use exactly this style".

**Order in the XML = order on the screen.** A vertical `LinearLayout` places the children in file order. If you move the third button first, the visual order changes too, without a single line of Java code.

---

## 28.2 `AndroidManifest.xml` — the four activities

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FILE: AndroidManifest.xml
     ==================================================================================
     LOCATION: DMA06/src/main/AndroidManifest.xml
     ROLE:     declares the application, the theme and the four activities.
     CONTAINS: 1 × <application>, 4 × <activity>, 1 × <intent-filter>
     WATCH OUT: it has no `package` attribute; the name comes from `namespace` in build.gradle.kts.
     ================================================================================== -->

<!-- No `package=` — modern versions of the Android Gradle Plugin take the name from
     `namespace` (ro.ase.ie.dma06). That is why the relative names `.activities.MainActivity`
     resolve to ro.ase.ie.dma06.activities.MainActivity. The leading dot
     means "prepend the application name". -->

<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.AdaptersDemo">

        <!-- The only activity that can be started from outside: the launcher one.
             exported="true" is mandatory from Android 12 (API 31) for any
             component with an intent-filter. -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- The steps: started only from MainActivity, hence exported="false".
             android:label gives the title in the top bar of each screen. -->
        <activity
            android:name=".activities.SingleColumnActivity"
            android:exported="false"
            android:label="@string/step1_title" />

        <activity
            android:name=".activities.TwoColumnActivity"
            android:exported="false"
            android:label="@string/step2_title" />

        <activity
            android:name=".activities.RecyclerViewActivity"
            android:exported="false"
            android:label="@string/step3_title" />
    </application>
</manifest>

<!-- ======================================================================================
     WHAT TO REMEMBER FROM THE FILE
     ======================================================================================
     no package=              the name comes from namespace (build.gradle.kts)
     .activities.MainActivity the dot = prepends the applicationId
     exported="true"          only on MainActivity, the only one with MAIN + LAUNCHER
     exported="false"         the three steps: no other app can start them
     android:label            the ActionBar title, per activity
     supportsRtl="true"       that is why item_number.xml uses gravity="end", not "right"
     allowBackup="true"       the generated default; there is no data to save here
     no <uses-permission>     the app does not touch the network, the files or the sensors
     no android:icon          the project's default icon is used
     activity order           does not matter; only which one has MAIN + LAUNCHER matters
     ====================================================================================== -->

<!-- What happens if you forget an activity in the manifest: the compiler says nothing,
     because it does not know which classes extend Activity. At runtime, startActivity looks
     for the component in PackageManager, does not find it and throws:

       android.content.ActivityNotFoundException:
       Unable to find explicit activity class
       {ro.ase.ie.dma06/ro.ase.ie.dma06.activities.SingleColumnActivity};
       have you declared this activity in your AndroidManifest.xml?

     The message is explicit and appears immediately on the click — so the error is easy to find,
     unlike the one from a RecyclerView without a LayoutManager. -->
```

**`android:label` on each activity** — the title in the top bar. `Theme.Material3.DayNight` has an ActionBar, so the step 1 screen reads "Step 1: ListView", step 2 "Step 2: Two columns", step 3 "Step 3: RecyclerView".

**`supportsRtl="true"`** — allows the layouts to be mirrored in RTL languages. That is why in `item_number.xml` the second `TextView` uses `gravity="end"`, not `right`.

**The order of the activities in the manifest does not matter.** The one that starts at launch is the one with `MAIN` + `LAUNCHER`, not the first in the file. You can move them in any order.

**What is missing, and it is good that it is missing:** no permission (`<uses-permission>`), no `<service>`, no `<provider>`. The app does not touch the network, the files or the sensors. A clean lab manifest is also the best proof that everything that happens in the app is local.

---

## 28.3 `NumberData.java` — the data source

The file has 23 lines, of which 16 are code. The rest are comments — and that is normal: the question on the test is not "what does `getNumbers()` do", but "why is the constructor private".

```java
/*
 * ======================================================================================
 * FILE: NumberData.java
 * ======================================================================================
 * LOCATION: DMA06/src/main/java/ro/ase/ie/dma06/data/NumberData.java
 * PACKAGE:  ro.ase.ie.data          ← WATCH OUT: it does not contain `dma06`, although the folder does
 * ROLE:     the only data source of the app. It produces a list with the numbers 1..100.
 *           It does not know what a View, a Context, an Adapter or an activity is.
 *
 * FILE STRUCTURE (3 parts):
 *   1. constants      — 2 lines: FIRST_NUMBER, LAST_NUMBER
 *   2. constructor    — private and empty, with a comment that explains why it is empty
 *   3. getNumbers()   — 7 lines: loop and return
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - `final` on the class + `private` constructor + `static` methods = utility class.
 *   - The method returns a NEW list on every call, not a shared one.
 *   - Zero `android.*` imports: this class would also run on the desktop.
 * ======================================================================================
 */

// ======================================================================================
// BLOCK 1 — THE PACKAGE AND THE IMPORTS
// ======================================================================================
// The declared package does NOT contain `dma06`, although the folder is ro/ase/ie/dma06/data/.
// It is not a typo: that is how it is in the repo, and the same holds for the two
// adapters, which declare ro.ase.ie.adapters.
//
// Why it compiles: Gradle gives the compiler the explicit list of source files, and
// javac does not require the folder to match the package when the files are passed directly.
// The folder–package match matters only when the compiler looks for a class on the classpath.
//
// The practical consequence: imports use the declared package, not the folder path.
//   import ro.ase.ie.data.NumberData;          ← correct, that is how it is in the repo
//   import ro.ase.ie.dma06.data.NumberData;    ← wrong, the class does not exist there
//
// At runtime nothing changes: the ClassLoader loads by the name in the package, not by the
// folder path. Folders are only organization on disk.
// ======================================================================================

package ro.ase.ie.data;          // WATCH OUT: the declared package does NOT contain `dma06`

import java.util.ArrayList;      // the concrete implementation of the list
import java.util.List;           // the interface used in signatures

// Two imports, both from java.util. Zero android.* imports: the class could run
// in an ordinary JUnit test, without an emulator. The package split is not cosmetic —
// it allows the source to be tested without Android.

// ======================================================================================
// THEORY BLOCK: THE UTILITY CLASS
// ======================================================================================
/*
 * 1. WHAT IT IS
 *    A class that has no state and no instances. All the methods are `static`, so
 *    they are called on the class: `NumberData.getNumbers()`, never `new NumberData().get...`.
 *
 * 2. WHY A PRIVATE CONSTRUCTOR
 *    -   `private NumberData() {}` blocks `new NumberData()` from any other class.
 *    -   Without it, the compiler would generate an implicit public constructor and anyone
 *        could create pointless instances.
 *    -   It is not an error to have useless instances; it is noise. And noise hides intent.
 *    -   The private constructor also blocks inheritance: a subclass would have to call
 *        `super()`, which is inaccessible. That is why `final` on the class is almost redundant —
 *        but we write it anyway, to be explicit.
 *
 * 3. WHY STATIC METHODS
 *    -   They do not depend on any instance state.
 *    -   They are loaded once, with the class, not with every object.
 *    -   They can be called from any context, including from a JUnit test without Android.
 *
 * 4. ALTERNATIVES AND WHY THEY ARE NOT USED HERE
 *    -   Singleton: it would impose a shared instance. Here every screen wants ITS OWN list.
 *    -   Interface with `default` methods: there is nothing to implement — there is no contract,
 *        there is a single function.
 *    -   Class with a public constructor: it would have allowed `new NumberData()`, which makes no sense.
 *
 * 5. THE RULE YOU CAN SEE IN THE CODE
 *    `final class` + `private constructor` + `static methods` = the same combination as in
 *    java.lang.Math, java.util.Collections, java.util.Arrays. It is not a seminar trick;
 *    it is the pattern from the JDK.
 *
 * DIAGRAM:
 *
 *   NumberData                    (the class; it is never instantiated)
 *   ├── FIRST_NUMBER = 1          static final
 *   ├── LAST_NUMBER  = 100        static final
 *   ├── NumberData()              private  ← blocks `new`
 *   └── getNumbers()              static   ← the only access point
 */

/** The data source shared by all three steps. */
public final class NumberData {  // final: it cannot be extended; a utility class has nothing to inherit

    // ==================================================================================
    // BLOCK 2 — THE CONSTANTS
    // ==================================================================================
    // private  — nobody outside needs them
    // static   — they belong to the class, not to an instance (and there are no instances anyway)
    // final    — they never change; the compiler can substitute the value directly
    //
    // Why two constants and not 100 written directly: if you want 1–1000, you change a single
    // line. And the loop becomes readable: "from FIRST_NUMBER to LAST_NUMBER".
    // ==================================================================================
    private static final int FIRST_NUMBER = 1;    // the first number in the list
    private static final int LAST_NUMBER = 100;   // the last number, INCLUSIVE

    // ==================================================================================
    // BLOCK 3 — THE PRIVATE CONSTRUCTOR
    // ==================================================================================
    // Theory:  blocks instantiation; the class has only static methods.
    // Logic:   the body is intentionally empty; the comment documents the decision.
    // Risk:    if you remove it, the compiler generates an implicit public one and `new`
    //          becomes legal.
    // Ref:     course 2 (classes and objects).
    // ==================================================================================
    private NumberData() {
        // This class only has static methods
    }

    // Why the constructor is empty and does not throw: some utility classes write
    // `throw new AssertionError()` in the constructor, to catch calls made through reflection.
    // There is no need here: the constructor is private, and reflection is not a lab scenario.
    //
    // The comment inside — "This class only has static methods" — documents
    // WHY it is empty. An empty private constructor with no explanation looks like an oversight.

    // ==================================================================================
    // BLOCK 4 — getNumbers()
    // ==================================================================================
    // Theory:  a static method that builds a collection; it touches no state.
    // Logic:   1. create ArrayList  2. loop from 1 to 100  3. add  4. return
    // Risk:    if you returned a shared list (a static field), the changes made in one
    //          screen would show up in all the others.
    // Ref:     chapter 04 (MainActivity - list).
    // ==================================================================================
    public static List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();     // 1. a new list on every call
        for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {   // 2. 1..100
            numbers.add(number);                       // 3. autoboxing: int → Integer
        }
        return numbers;                                // 4. 100 elements
    }

    // A new list on every call — this is essential. There is no shared static field.
    // Each of the three activities calls getNumbers() in onCreate and receives
    // ITS OWN list. If it were a singleton, a change made in one screen would
    // show up in all the others, without you knowing where it came from.
    //
    // List in the signature, ArrayList in the implementation — you return the interface, you build
    // the implementation. Whoever receives the list does not depend on ArrayList; you can switch to
    // LinkedList without touching anything else. The rule is called "program to an interface".
    //
    // new ArrayList<>() with an empty diamond — the generic type is inferred from context (Java 7+).
    //
    // `<=` and not `<` — LAST_NUMBER is INCLUSIVE. The loop gives exactly 100 elements: 1..100.
    // With `<` you would have 99 — visible at once, because the last row would be 99.
    //
    // Autoboxing — numbers.add(number) receives an int, but the list is List<Integer>.
    // The compiler automatically converts it with Integer.valueOf(number). For the values
    // −128…127, Integer.valueOf returns cached instances, so for 1–100 no
    // 100 new objects are created.
    //
    // Why Integer and not int: Java generics do not accept primitive types. List<int>
    // does not compile. Hence the autoboxing, hence Integer in getItem in the adapters.
    //
    // ==================================================================================
    // WHEN THE CLASS IS LOADED
    // ==================================================================================
    //
    //   The first call to NumberData.getNumbers()
    //     → the ClassLoader loads NumberData
    //     → it initializes the static fields: FIRST_NUMBER = 1, LAST_NUMBER = 100
    //     → only then does it execute the body of the method
    //
    // Initialization happens once per process, not on every call. That is why
    // the constants can be read without any worry about order: they are ready before the first
    // method.
    //
    // ==================================================================================
    // WHY IT IS EASY TO TEST
    // ==================================================================================
    //
    //   @Test
    //   public void getNumbers_returnsHundredElements() {
    //       List<Integer> numbers = NumberData.getNumbers();
    //       assertEquals(100, numbers.size());
    //       assertEquals(Integer.valueOf(1), numbers.get(0));
    //       assertEquals(Integer.valueOf(100), numbers.get(99));
    //   }
    //
    // The test runs on the JVM, without an emulator, because no android.* type appears
    // in the file. If NumberData had received a Context to read resources, the test
    // would have needed Robolectric or a device. The package split is not
    // cosmetic: it decides whether you can test in 50 milliseconds or in 50 seconds.
}
```

**What you must remember:** the private constructor is not a formality — it is the only line that turns an ordinary class into a utility class. The rest (static methods, `final` on the class) completes it.

**Who calls `getNumbers()`:**

| Activity | What it does with the list |
|---|---|
| `SingleColumnActivity` | passes it straight to `ArrayAdapter` |
| `TwoColumnActivity` | passes it to `NumberListAdapter` |
| `RecyclerViewActivity` | passes it to `NumberRecyclerAdapter` |

The same data, three different renderings. That is the whole experiment. Each activity calls separately, because the three screens are independent: you can open step 2 straight from the menu, without having opened step 1.

**The real cost:** 300 `Integer` objects (3 × 100), all from the `Integer.valueOf` cache for 1–100. Practically zero new objects. If you had generated 1–10000, the cache would no longer cover it and you would have had 30000 objects — still acceptable, but not free.

---

## 28.4 `SingleColumnActivity.java` — step 1

The file has 31 lines, of which 18 are code, and it hides all the recycling in the SDK. Step 1 is not learned from the code, it is learned from what is *not* written in the code.

```java
/*
 * ======================================================================================
 * FILE: SingleColumnActivity.java
 * ======================================================================================
 * LOCATION: DMA06/src/main/java/ro/ase/ie/dma06/activities/SingleColumnActivity.java
 * PACKAGE:  ro.ase.ie.dma06.activities
 * ROLE:     step 1. One ListView, one ArrayAdapter, one TextView per row.
 *           It writes no line of recycling code: ArrayAdapter does it in its place.
 *
 * FILE STRUCTURE (2 parts):
 *   1. imports     — 6 lines
 *   2. onCreate    — 10 lines, of which 4 build the adapter
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - `android.R.layout.simple_list_item_1` is a layout from the SYSTEM, not from the project.
 *   - `ArrayAdapter` calls `toString()` on each element. For Integer = the number.
 *   - `setAdapter` is all you need: ListView asks for getCount and getView by itself.
 * ======================================================================================
 */

// ======================================================================================
// BLOCK 1 — THE PACKAGE AND THE IMPORTS
// ======================================================================================
// Here the package matches the folder (activities/). The imports come in three groups:
// android.* (framework), androidx.* (bundled library) and ro.ase.* (your code).
// The separation is not required by the compiler, but it makes obvious what comes from where.
// ======================================================================================

package ro.ase.ie.dma06.activities;      // the package of the screens

import android.os.Bundle;                // the parameter of onCreate
import android.widget.ArrayAdapter;      // the ready-made adapter from the SDK
import android.widget.ListView;          // the widget that displays the list

import androidx.appcompat.app.AppCompatActivity;   // the base activity

import ro.ase.ie.data.NumberData;        // the declared package, not the folder
import ro.ase.ie.dma06.R;                // the app's resources

// ======================================================================================
// THEORY BLOCK: LISTVIEW + ARRAYADAPTER
// ======================================================================================
/*
 * 1. WHAT LISTVIEW DOES
 *    -   It is an AdapterView: a widget that does not know what it displays, but knows how to display.
 *    -   It asks an Adapter: "how many elements do you have?" (getCount) and "give me the row for
 *        position N" (getView).
 *    -   It keeps only the visible rows in the view tree. The rest do not exist.
 *    -   It has an internal RecycleBin: the rows that leave the screen are kept for
 *        reuse, by type (getItemViewType).
 *
 * 2. WHAT ARRAYADAPTER DOES
 *    -   It implements getCount, getItem, getItemId and getView.
 *    -   getView: if convertView is null, it inflates `resource`; otherwise it reuses it.
 *    -   Then it takes the element at the position and calls `toString()` on it, which it puts
 *        into a TextView.
 *    -   So: a single text per row. That is all.
 *
 * 3. WHAT `resource` MUST CONTAIN
 *    -   A TextView. Either the root itself (the simple_list_item_1 case), or a child
 *        with the id android.R.id.text1.
 *    -   If it is missing, ArrayAdapter throws a RuntimeException on the first row:
 *        "You must supply a resource ID for a TextView".
 *
 * 4. WHERE IT STOPS
 *    -   At the second TextView. ArrayAdapter has nowhere to put the second value.
 *    -   At per-column formatting. toString() gives a single string; you cannot right-align
 *        the second column with a monospaced font.
 *    -   At models without an overridden toString(): the list shows Movie@a1b2c3.
 *
 * 5. RECYCLING IS HIDDEN, NOT MISSING
 *    -   ArrayAdapter receives `convertView` and reuses it, exactly like a custom
 *        adapter. It is just that you do not see the parameter and cannot attach a ViewHolder.
 *    -   For a single TextView, the missing ViewHolder costs nothing: there is nothing to look up.
 *
 * 6. WHAT CODE RUNS FOR EACH ROW
 *    ListView.obtainView(position)
 *      └─ ArrayAdapter.getView(position, convertView, parent)
 *           ├─ convertView == null ?
 *           │     ├─ yes → inflater.inflate(simple_list_item_1, parent, false)
 *           │     └─ no  → view = convertView
 *           ├─ text = (TextView) view        ← mFieldId == 0, the root is a TextView
 *           └─ text.setText(getItem(position).toString())
 *
 * DIAGRAM:
 *
 *   ListView ──getCount()──▶ ArrayAdapter ──▶ List.size()
 *            ──getView(n)──▶ ArrayAdapter ──▶ convertView? inflate : reuse
 *                                          ──▶ getItem(n).toString()
 *                                          ──▶ textView.setText(...)
 */

/**
 * Step 1: one column.
 * ArrayAdapter is enough because each row shows one text value.
 */
public class SingleColumnActivity extends AppCompatActivity {   // an activity, with no state

    // ==================================================================================
    // METHOD 1 — onCreate
    // ==================================================================================
    // Theory:  the lifecycle; here the whole screen is built.
    // Logic:   1. super  2. setContentView  3. findViewById  4. build the adapter
    //          5. setAdapter
    // Risk:    if you forget setAdapter, the screen stays empty, with no error at all.
    // Ref:     chapter 12 (ListView vs RecyclerView).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);                       // 1. the parent's lifecycle
        setContentView(R.layout.activity_single_column);          // 2. the layout root IS the ListView

        ListView lvNumbers = findViewById(R.id.lvNumbers);        // 3. the only view in the layout

        // ArrayAdapter calls toString() on each number and shows it in a TextView
        ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
                this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
        //      ↑ Context   ↑ layout from the SYSTEM          ↑ List<Integer> with 100 elements
        lvNumbers.setAdapter(adapter);                            // 4. binds the list to the widget
    }

    // ArrayAdapter<Integer> — the generic must match the type of the list. The list is
    // List<Integer>, so the adapter is ArrayAdapter<Integer>. If you put
    // ArrayAdapter<String>, you would need a List<String> — and you would lose the numeric type.
    //
    // new ArrayAdapter<>(...) with the diamond — the type is inferred from the variable on the left.
    //
    // `this` as the first argument — it is the Context. The adapter needs it to obtain
    // the LayoutInflater with which it inflates the row. In NumberListAdapter you will see exactly
    // the same thing, only explicit: LayoutInflater.from(context).
    //
    // android.R.layout.simple_list_item_1 — the leading "android." is essential.
    // R.layout.simple_list_item_1 does not exist in the project; android.R is the framework's
    // resource package. The file is shipped by the system, not by you.
    //
    // NumberData.getNumbers() as the third argument — it is called once, in
    // onCreate. The result is a list of 100 elements, held by the adapter through
    // a reference. If you called getNumbers() again, you would have a new list, which the
    // adapter does not see.
    //
    // lvNumbers.setAdapter(adapter) — the last line and the most important one. Before it,
    // the ListView is empty and does not know that data exists. On the call, ListView registers a
    // DataSetObserver on the adapter and asks for a layout; only then do getCount() and getView() start.
    //
    // The order between findViewById and setAdapter does not matter — you can build the adapter
    // before finding the list. What matters is that both happen after setContentView,
    // otherwise findViewById returns null.
    //
    // ==================================================================================
    // WHAT ARRAYADAPTER DOES WITH convertView
    // ==================================================================================
    //
    //   ArrayAdapter.getView(position, convertView, parent)
    //     ├─ convertView == null ?
    //     │     ├─ yes → view = inflater.inflate(mResource, parent, false)
    //     │     └─ no  → view = convertView
    //     ├─ mFieldId == 0 ?
    //     │     ├─ yes → text = (TextView) view          ← the root is a TextView
    //     │     └─ no  → text = view.findViewById(mFieldId)
    //     └─ text.setText(getItem(position).toString())
    //
    // Recycling is IDENTICAL to the one in NumberListAdapter. The difference is that you do not see
    // the convertView parameter and cannot hang a ViewHolder off the row. For a single
    // TextView, that costs nothing — there is nothing to look up.
    //
    // ==================================================================================
    // WHAT HAPPENS IF YOU FORGET setAdapter
    // ==================================================================================
    //
    //   ListView without an adapter
    //     ├─ getCount() is never called
    //     ├─ getView() is never called
    //     ├─ the screen: white, with no rows
    //     └─ no exception, no message in Logcat
    //
    // It is the same class of error as a RecyclerView without a LayoutManager: a valid component,
    // in a valid state, that has nothing to display. It is not a bug of the framework; it is an
    // incomplete configuration.
    //
    // ==================================================================================
    // WHY THREE LINES ARE ENOUGH HERE AND ARE NOT ENOUGH AT STEP 2
    // ==================================================================================
    //
    //   Step 1: 1 column  → 1 TextView  → ArrayAdapter knows how
    //   Step 2: 2 columns → 2 TextViews → ArrayAdapter does NOT know how
    //   Step 3: 2 columns → 2 TextViews → RecyclerView.Adapter knows how
    //
    // The rule is not "ArrayAdapter is for simple lists". The rule is: ArrayAdapter knows
    // EXACTLY ONE text per row. As long as your row is one text, it is the best
    // tool. When the row has structure, you move to BaseAdapter.
}
```

### The three arguments of `ArrayAdapter`

```
ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
        this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
```

| Argument | What it is | Why |
|---|---|---|
| `this` | `Context` | the adapter needs it to inflate the row |
| `android.R.layout.simple_list_item_1` | a layout **from the system** | it contains a single `TextView`, with the id `android.R.id.text1` |
| `NumberData.getNumbers()` | `List<Integer>` | the data; the adapter holds the **reference**, not a copy |

**The second argument is an `int`, not a `View`.** It is the layout resource id, not the inflated layout. `ArrayAdapter` inflates it itself, once per new row. That is why you see no `inflate` in the activity.

### `toString()` — what it does and where it stops

**For `Integer`:** `Integer.toString(42)` returns `"42"`. The method is overridden in `Integer` and is equivalent to `String.valueOf(int)`. So step 1 displays exactly the decimal number, with no configuration.

**For a model of your own:** if you had `class Movie { String title; int year; }` without an overridden `toString()`, the list would show:

```
ro.ase.ie.model.Movie@a1b2c3d4
```

That is the default `Object.toString()`: the full class name, `@`, then `hashCode()` in hexadecimal. It is the most common source of "why does it look like that?" with `ArrayAdapter`.

**Where it stops, concretely, in this project:** you need **two** values per row — decimal and binary. `toString()` returns **a single** `String`. You could return `"42 / 101010"`, but then:

1. you would no longer have two `TextView`s, so you could not right-align the second column;
2. you could not put a monospaced font on the second column only;
3. you could not give the two columns different padding;
4. you could not change one column without parsing the string.

**The conclusion:** `toString()` is enough as long as the row is **a single text**. The moment the row has structure — two columns, an image and a text, a title and a subtitle — you need a layout of your own and an adapter that fills it. This is where step 1 ends.

**What you must remember before step 2:** `ArrayAdapter` is not "dumb", it is **specialized**. For a list of names or titles it is exactly right: one line of code, zero `findViewById`, zero `ViewHolder`. It becomes unsuitable only when the row has structure. And when it becomes unsuitable, the solution is not to extend it and override `getView` — but to drop down to `BaseAdapter`.

---

## 28.5 `activity_single_column.xml` — a single `ListView`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FILE: activity_single_column.xml
     ==================================================================================
     LOCATION: DMA06/src/main/res/layout/activity_single_column.xml
     ROLE:     the step 1 layout. A single element: the ListView, as the root.
     IDS:      lvNumbers
     ================================================================================== -->

<!-- The root of the layout is the ListView itself: setContentView attaches it directly.
     There is no need for a LinearLayout wrapping it — step 2 needs the
     wrapper because it also has a header; step 1 does not. -->
<ListView xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/lvNumbers"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

<!-- ======================================================================================
     ATTRIBUTES THAT LISTVIEW HAS AND THE FILE DOES NOT USE
     ======================================================================================
     android:divider="@null"              removes the separator between rows
     android:dividerHeight="1dp"          the thickness of the separator
     android:listSelector="..."           the background of the selected row
     android:choiceMode="singleChoice"    allows selection with radio/check
     android:fastScrollEnabled="true"     the fast scroll bar, for long lists
     android:stackFromBottom="true"       lists that grow from the bottom (chat)
     android:transcriptMode="normal"      auto-scroll to the last element
     android:cacheColorHint="#00000000"   removes the scroll artefact (old lists)
     ======================================================================================
     They are all attributes of the widget, not of the adapter. On RecyclerView none of them
     exists: their equivalents are LayoutManager, ItemDecoration or code.
     ====================================================================================== -->

<!-- ======================================================================================
     WHAT TO REMEMBER FROM THE FILE
     ======================================================================================
     root = ListView          setContentView receives the list directly
     match_parent × 2         the list fills the whole screen
     no android:entries       the data comes ONLY from the adapter; no setAdapter = empty screen
     no android:divider       the separator comes from the ListView's default theme
     no android:text          a ListView has no text of its own
     ====================================================================================== -->
```

**The root is `ListView`** — not a `LinearLayout` wrapping it. `setContentView` receives the list directly, and `findViewById(R.id.lvNumbers)` finds it in the activity's view tree.

**No `android:entries`** — the list has no data from the XML. The only source is the adapter. If you forget `setAdapter`, the screen stays empty, with no error.

**No `android:divider`** — the separator comes from the `ListView`'s default theme. On `RecyclerView` there is no such thing (see 28.11, `DividerItemDecoration`).

**Why a separate file for a single tag:** because `setContentView` needs a layout, and a layout with a single element is perfectly valid. The alternative — `setContentView(new ListView(this))` — would work, but you would lose everything related to the theme and to `LayoutParams`, plus you would no longer have an id for `findViewById`.

---

## 28.6 `NumberListAdapter.java` — step 2, the custom adapter

This is the central file of the chapter. Everything known about recycling, `ViewHolder`, `convertView`, `setTag` and `getTag` can be seen here, written by hand, without being hidden in the SDK.

```java
/*
 * ======================================================================================
 * FILE: NumberListAdapter.java
 * ======================================================================================
 * LOCATION: DMA06/src/main/java/ro/ase/ie/dma06/adapters/NumberListAdapter.java
 * PACKAGE:  ro.ase.ie.adapters        ← without `dma06`, like `data`
 * ROLE:     adapts List<Integer> to the two-column row (item_number.xml),
 *           for a ListView. It is the manual equivalent of ArrayAdapter.
 *
 * FILE STRUCTURE (4 parts):
 *   1. ViewHolder            — 4 lines: two references to TextView
 *   2. fields + constructor  — 8 lines: the list and the inflater
 *   3. bookkeeping           — 3 methods: getCount, getItem, getItemId
 *   4. getView               — 22 lines: creation OR reuse + filling
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - BaseAdapter leaves 4 abstract methods; it implements the rest.
 *   - `convertView` is the row recycled by ListView; `null` = there is none free.
 *   - `setTag` / `getTag` glue the ViewHolder to the row. Without them, NPE on the first scroll.
 *   - `findViewById` is called once per row, not on every display.
 * ======================================================================================
 */

// ======================================================================================
// BLOCK 1 — THE PACKAGE AND THE IMPORTS
// ======================================================================================
// The declared package is ro.ase.ie.adapters, although the folder is ro/ase/ie/dma06/adapters/.
// The same situation as with NumberData: it compiles, but the imports must use the
// declared package.
//
// The imports fall into three groups:
//   android.*   — framework: Context, LayoutInflater, View, ViewGroup, BaseAdapter, TextView
//   java.util   — List
//   ro.ase.*    — R (the resources)
// ======================================================================================

package ro.ase.ie.adapters;   // the declared package does not contain `dma06`, although the folder does

import android.content.Context;      // needed only for LayoutInflater
import android.view.LayoutInflater;  // turns XML into View objects
import android.view.View;            // the row (inflated or recycled)
import android.view.ViewGroup;       // the parent of the row: the ListView
import android.widget.BaseAdapter;   // the base class for custom adapters
import android.widget.TextView;      // the two columns

import java.util.List;               // the interface for the list of numbers

import ro.ase.ie.dma06.R;            // the app's resources

// ======================================================================================
// THEORY BLOCK: BASEADAPTER AND THE VIEWHOLDER PATTERN
// ======================================================================================
/*
 * 1. WHAT BASEADAPTER IS
 *    -   An abstract class from android.widget that implements ListAdapter and
 *        SpinnerAdapter.
 *    -   It implements everything related to observers, view types and enabled state:
 *        isEmpty(), areAllItemsEnabled(), isEnabled(int), getItemViewType(int),
 *        getViewTypeCount(), hasStableIds(), registerDataSetObserver().
 *    -   It leaves EXACTLY four methods abstract:
 *          getCount()                                                  how many elements there are
 *          getItem(int position)                                       the object at the position
 *          getItemId(int position)                                     the stable id
 *          getView(int position, View convertView, ViewGroup parent)   the row
 *
 * 2. WHEN EACH METHOD IS CALLED
 *    getCount()   — on every layout of the list, when computing the scroll bar, after
 *                   notifyDataSetChanged. It is the first question ever asked.
 *    getItem()    — It is NOT called by ListView in order to draw. It is called by
 *                   AdapterView.getItemAtPosition(), by performItemClick() and by
 *                   your code (including from getView, as here).
 *    getItemId()  — on click (performItemClick receives the id), on getSelectedItemId().
 *                   With hasStableIds() == true, ListView keeps the selection between
 *                   reloads.
 *    getView()    — for every visible row, on every layout, on every scroll
 *                   step, after every notifyDataSetChanged.
 *
 * 3. THE VIEWHOLDER PATTERN
 *    The problem: findViewById walks the tree. On a row with 2 views it is cheap;
 *    on 10 rows × 2 views × every scroll, it starts to matter.
 *    The solution: look it up once, when the row is created, and glue the result to the row
 *    with setTag(). On reuse, you take it back with getTag().
 *
 *    Without a holder:                     With a holder:
 *    ┌──────────────────────────┐          ┌──────────────────────────┐
 *    │ row (View)               │          │ row (View)               │
 *    │  ├─ tvDecimal            │          │  ├─ tvDecimal            │
 *    │  └─ tvBinary             │          │  ├─ tvBinary             │
 *    │  (looked up on every     │          │  └─ tag → ViewHolder     │
 *    │   display)               │          │      ├─ tvDecimal ───────┘
 *    └──────────────────────────┘          │      └─ tvBinary
 *                                          └──────────────────────────┘
 *
 * 4. WHY `static`
 *    A non-static inner class holds an implicit reference to the outer instance
 *    (`this$0`). The ViewHolder is attached to a View, and the View can live longer
 *    than the adapter (ListView keeps it in the RecycleBin). `static` removes the reference.
 *    On top of that, a non-static holder cannot be built without an adapter — which
 *    complicates any test.
 *
 * 5. THE LIFE OF A ROW
 *    creation:   inflate → findViewById × 2 → new ViewHolder → setTag → fill
 *    reuse:      getTag → fill
 *    exit:       the row enters the RecycleBin, with its tag and all
 *
 * 6. THE OBJECT GRAPH
 *
 *    TwoColumnActivity
 *      └── NumberListAdapter            (a local field; lives as long as the activity)
 *            ├── List<Integer>          (a REFERENCE to the list from NumberData)
 *            │     └── 100 × Integer
 *            ├── LayoutInflater         (a single one, reused)
 *            └── getView() creates:
 *                  ViewHolder           (glued to the row with setTag)
 *                    ├── tvDecimal ──┐
 *                    └── tvBinary  ──┤
 *                                    ▼
 *                  View (the LinearLayout from item_number.xml)
 *                    ├── TextView tvDecimal
 *                    └── TextView tvBinary
 *
 *    The arrows go one way only: the activity holds the adapter, the adapter holds the
 *    list and creates holders, the holder holds the views. No arrow goes back —
 *    that is why the holder can be `static`.
 */

/** Step 2: fills a two-column row for a ListView. */
public class NumberListAdapter extends BaseAdapter {   // extends the skeleton, not ArrayAdapter

    // ==================================================================================
    // BLOCK 2 — THE INNER CLASS ViewHolder
    // ==================================================================================
    // Theory:  the box that holds the references to the row's views, so you stop looking them up.
    // Logic:   two fields, that is all. No methods, no logic, no constructor.
    // Risk:    if it is not `static`, it holds a reference to the adapter (`this$0`) and prolongs
    //          its life as long as the row is in the RecycleBin.
    // Ref:     course 4 (ListView and adapters).
    // ==================================================================================
    private static class ViewHolder {
        TextView tvDecimal;   // the reference to column 1
        TextView tvBinary;    // the reference to column 2
    }

    // Why it is an inner class: the two TextViews must travel
    // together. A holder is a box with two references, hung off the row with setTag.
    // Without it, you would have two separate variables and nowhere to keep them
    // between calls.
    //
    // Why `private`: only this adapter uses it. It appears in no public
    // signature. (In NumberRecyclerAdapter it is `static class` without private, because the
    // type appears in the adapter's public signature.)
    //
    // Why the fields are NOT `final`: they are assigned AFTER `new ViewHolder()`, in
    // getView. They cannot be final because they are not initialized in the constructor. Exactly
    // this is what the RecyclerView version fixes: it moves findViewById into the holder's
    // constructor and can make them final.

    // ==================================================================================
    // BLOCK 3 — THE FIELDS AND THE CONSTRUCTOR
    // ==================================================================================
    // Theory:  two final references: the list and the inflater.
    // Logic:   both are set once, in the constructor.
    // Risk:    if you copied the list (`new ArrayList<>(numbers)`), you would have two lists and
    //          changes from outside would no longer be visible.
    // Ref:     chapter 12.
    // ==================================================================================
    private final List<Integer> numbers;          // the data source, held by reference
    private final LayoutInflater layoutInflater;  // a single inflater, reused

    public NumberListAdapter(Context context, List<Integer> numbers) {
        this.layoutInflater = LayoutInflater.from(context);  // obtained once, not on every row
        this.numbers = numbers;                              // we do NOT copy the list
    }

    // `private final List<Integer> numbers` — the reference never changes.
    // The content of the list could change, but the adapter always points at the same list.
    //
    // `private final LayoutInflater layoutInflater` — LayoutInflater.from(context) does
    // an internal lookup. We do it ONCE, in the constructor, not on every row. On top of that,
    // getView no longer needs a Context.
    //
    // `this.numbers = numbers` — the list is not copied. The adapter receives the reference to
    // the list built by NumberData. If you modified the list from outside, the adapter would
    // see the change — but it would not redraw anything without notifyDataSetChanged().
    //
    // Why the constructor validates nothing: it has nothing to validate. A null `context` would
    // crash anyway at LayoutInflater.from, and a null list would crash on the first getCount().

    // ==================================================================================
    // BLOCK 4 — THE THREE BOOKKEEPING METHODS
    // ==================================================================================
    // Three short methods, each answering a question from ListView. None of them
    // draws anything.
    // ==================================================================================

    // ----------------------------------------------------------------------------------
    // METHOD 1 — getCount
    // ----------------------------------------------------------------------------------
    // Theory:  ListView's first question: how many rows are there?
    // Logic:   the size of the list.
    // Risk:    if you return 0, the list is empty; if you return more than size(),
    //          getView reaches an invalid position → IndexOutOfBoundsException.
    // Ref:     chapter 12.
    // ----------------------------------------------------------------------------------
    @Override
    public int getCount() {
        return numbers.size();      // how many rows: exactly the elements of the list
    }

    // ----------------------------------------------------------------------------------
    // METHOD 2 — getItem
    // ----------------------------------------------------------------------------------
    // Theory:  the object at the given position. It is NOT called by ListView for drawing.
    // Logic:   numbers.get(position), with the bounds check done by ArrayList.
    // Risk:    invalid position → IndexOutOfBoundsException; null element → NPE on
    //          unboxing in getView.
    // Ref:     chapter 12.
    // ----------------------------------------------------------------------------------
    @Override
    public Integer getItem(int position) {
        return numbers.get(position);   // the object at the given position
    }

    // ----------------------------------------------------------------------------------
    // METHOD 3 — getItemId
    // ----------------------------------------------------------------------------------
    // Theory:  the stable identity of the element, used on click and on selection.
    // Logic:   the numbers are unique, so the number itself is a valid id.
    // Risk:    in a list with duplicates, two rows would have the same id and the selection
    //          would jump between them.
    // Ref:     chapter 12.
    // ----------------------------------------------------------------------------------
    @Override
    public long getItemId(int position) {
        // Each number is unique, so the number itself can be the ID
        return numbers.get(position);   // Integer → int → long (widening)
    }

    // getCount() — the first thing ListView asks. It determines how many rows
    // exist and how long the scroll bar is. If you return 0, the list is empty.
    //
    // getItem(position) — the object at the given position. ListView calls it when someone
    // asks for the element at a position (getItemAtPosition), and the adapter calls it
    // itself in getView.
    //
    // getItemId(position) — the identity of the element. numbers.get(position) returns
    // Integer, which is unboxed to int and then widened to long (widening,
    // a safe implicit conversion). Because the numbers 1–100 are unique, the number
    // itself is a valid ID. In a list with duplicates (two movies with the same title)
    // you would need a separate id field.
    //
    // When getItemId is used: ListView calls it when it builds the arguments of a
    // click. The stable identity (hasStableIds() == true) would allow the widget to
    // keep the selection between reloads; here it is false by default, but the method must
    // be implemented anyway — it is abstract in BaseAdapter.
    //
    // @Override on all three — the methods come from Adapter / BaseAdapter. Without the annotation
    // they would still be overrides, but the compiler would not flag a wrong signature.
    //
    // Why getItem returns Integer and not int: the signature in Adapter is
    // `Object getItem(int)`. NumberListAdapter narrows it to Integer — allowed,
    // because Integer is a subtype of Object (return type covariance). The gain:
    // getView no longer needs a cast.
    //
    // THE TABLE OF THE FOUR METHODS:
    //
    //   Method          Who calls it                         When
    //   getCount()      ListView.onMeasure/layoutChildren    on every layout
    //   getItem(int)    AdapterView.getItemAtPosition        on demand / from getView
    //   getItemId(int)  AdapterView.getSelectedItemId        on click / selection
    //   getView(...)    AbsListView.obtainView               for every visible row

    // ==================================================================================
    // BLOCK 5 — getView, THE HEART OF THE ADAPTER
    // ==================================================================================
    // Theory:  the only method that produces a View. It has two branches: creation and reuse.
    // Logic:   1. if convertView is null → inflate + findViewById + setTag
    //          2. otherwise → getTag
    //          3. fill both TextViews
    //          4. return convertView
    // Risk:    without setTag, getTag returns null and the first line that touches the holder
    //          throws NullPointerException. The list works until the first scroll.
    // Ref:     chapter 12 (the section about recycling).
    // ==================================================================================
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;                       // declared before the if, used after it

        if (convertView == null) {
            // New row: inflate it and store its views
            convertView = layoutInflater.inflate(R.layout.item_number, parent, false);
            holder = new ViewHolder();                                      // the empty box
            holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);    // lookup 1
            holder.tvBinary = convertView.findViewById(R.id.tvBinary);      // lookup 2
            convertView.setTag(holder);                                     // glues the box to the row
        } else {
            // Reused row: get its stored views
            holder = (ViewHolder) convertView.getTag();                     // takes the box back
        }

        int number = getItem(position);                                     // Integer → int
        holder.tvDecimal.setText(String.valueOf(number));                   // column 1: "42"
        holder.tvBinary.setText(Integer.toBinaryString(number));            // column 2: "101010"

        return convertView;                                                 // THE SAME row, filled
    }

    // ----------------------------------------------------------------------------------
    // THE SIGNATURE — what each parameter means
    // ----------------------------------------------------------------------------------
    //
    //   position      which row of the list (0…99). It is NOT the position on the screen.
    //                 On the first screen: 0…9. After scrolling: 10, 11, …
    //   convertView   a row RECYCLED by ListView, or null if there is none
    //                 free. It is a View, not a ViewHolder — hence setTag/getTag.
    //   parent        the ListView asking for the row. You do not add it to the tree yourself;
    //                 ListView does it after getView returns. You only need it
    //                 for inflate, so the correct LayoutParams gets computed.
    //
    // ----------------------------------------------------------------------------------
    // THE TWO BRANCHES
    // ----------------------------------------------------------------------------------
    //
    //   convertView == null   →  NEW row:        inflate + findViewById + setTag
    //   convertView != null   →  REUSED row:     getTag, with no lookup at all
    //
    // At startup, ListView asks for the first ~10 rows with convertView == null — it has
    // nothing to recycle. Then, on every scroll, the row that leaves the screen enters the
    // RecycleBin and is handed back on the next call:
    //
    //   getView(0,  null, listView)    → null → inflate + findViewById + setTag
    //   getView(1,  null, listView)    → null → inflate + findViewById + setTag
    //   ...
    //   getView(9,  null, listView)    → null → inflate + findViewById + setTag
    //         ── you scroll one position ──
    //   getView(10, row0, listView)    → != null → getTag + setText
    //
    // Why the first calls have convertView == null: because the RecycleBin is empty.
    // There is no row that has left the screen, because you have not scrolled yet.
    //
    // Why getView(10, row0, ...) and not getView(10, row9, ...): ListView takes
    // the row from the head of the recycling list, not necessarily the last one out. The exact
    // order depends on the RecycleBin implementation; for you, all that matters is that A
    // recycled row arrives, not which one.
    //
    // ----------------------------------------------------------------------------------
    // convertView == null / setTag / getTag, STEP BY STEP
    // ----------------------------------------------------------------------------------
    //
    // STEP 1 — the first call, convertView == null:
    //
    //   ListView has no free row
    //     → getView(0, null, parent)
    //         convertView = layoutInflater.inflate(item_number, parent, false)
    //             ├─ creates the LinearLayout from the XML
    //             ├─ creates the two TextViews
    //             └─ does NOT attach it to parent (third argument = false)
    //         holder = new ViewHolder()                    ← empty object, two null fields
    //         holder.tvDecimal = convertView.findViewById(R.id.tvDecimal)
    //         holder.tvBinary  = convertView.findViewById(R.id.tvBinary)
    //         convertView.setTag(holder)                   ← the row now holds the holder
    //         setText × 2
    //         return convertView
    //
    // STEP 2 — the second call for the same row, after scrolling:
    //
    //   row 0 leaves the screen
    //     → ListView removes it from the tree and puts it in the RecycleBin
    //     → getView(10, row0, parent)
    //         convertView = row0                           ← it is NOT null
    //         holder = (ViewHolder) convertView.getTag()   ← exactly the holder from step 1
    //         setText × 2                                  ← only the text changes
    //         return convertView
    //
    // STEP 3 — what happens to the tag on recycling: nothing. setTag is not reset by
    // ListView, it is not touched by removeView, it is not cleared by the RecycleBin. The row
    // goes into the pool with the holder glued on and comes back with it. That is why it
    // works: the tag belongs to the row, not to the position.
    //
    // What the holder contains between calls: the same two references to the same
    // TextViews. The row is not rebuilt, so the views do not change either.
    // Only the text inside them changes.
    //
    // Why setTag is called only on the null branch: because that is the only place the
    // holder is created. On the else branch, the holder already exists, glued to the row. If you
    // called setTag on the else branch too, you would create a new holder on every display —
    // exactly what you were trying to avoid.
    //
    // ----------------------------------------------------------------------------------
    // DANGER! — the exact NPE when setTag is missing
    // ----------------------------------------------------------------------------------
    //
    // If you remove the line `convertView.setTag(holder);`, the code compiles. The list
    // displays correctly at startup — the first 10 rows go through the null branch, where
    // the holder is built locally. On the first scroll, however:
    //
    //   holder = (ViewHolder) convertView.getTag();   // getTag() → null
    //                                                 // the cast (ViewHolder) null → null
    //   ...
    //   holder.tvDecimal.setText(...);                // ← this is where it crashes
    //
    // Why the cast does not throw: a cast applied to null returns null. (ViewHolder) null
    // is legal. ClassCastException appears only when the object exists and is not of the
    // requested type. That is why the exception does not come from the cast line, but from
    // the first line that TOUCHES the holder.
    //
    // The exact exception, on ART:
    //
    //   java.lang.NullPointerException: Attempt to read from field
    //   'android.widget.TextView ro.ase.ie.adapters.NumberListAdapter$ViewHolder.tvDecimal'
    //   on a null object reference
    //       at ro.ase.ie.adapters.NumberListAdapter.getView(NumberListAdapter.java:47)
    //
    // Why "read from field" and not "invoke virtual method": because the first operation
    // is reading the field holder.tvDecimal, not the setText call. If the holder
    // existed, but tvDecimal were null (for example you forgot a findViewById), then
    // you would get the variant with the method:
    //
    //   java.lang.NullPointerException: Attempt to invoke virtual method
    //   'void android.widget.TextView.setText(java.lang.CharSequence)'
    //   on a null object reference
    //
    // The wrong-tag variant: if you put convertView.setTag("row"), the cast would
    // throw immediately:
    //
    //   java.lang.ClassCastException: java.lang.String cannot be cast to
    //   ro.ase.ie.adapters.NumberListAdapter$ViewHolder
    //       at ro.ase.ie.adapters.NumberListAdapter.getView(NumberListAdapter.java:44)
    //
    // Without setTag: the list works until the first scroll. Then it crashes with
    // NullPointerException. It is the most common mistake with a ListView with a custom
    // adapter — and the only one that gets past the compiler, past the first screen and past
    // the demo done without scrolling.
    //
    // How to debug it in 30 seconds: if the list looks right when opened and
    // crashes on scroll, it is almost certainly a missing setTag or one placed on the wrong branch.
    //
    // ----------------------------------------------------------------------------------
    // inflate — why (layout, parent, false)
    // ----------------------------------------------------------------------------------
    //
    // Why parent: so that the correct LayoutParams is generated for the row. Without it,
    // inflate does not know which parameters to create, and match_parent from the XML cannot be
    // interpreted. LayoutParams is the class that tells the parent how to place the child;
    // LinearLayout has LinearLayout.LayoutParams, ListView has AbsListView.LayoutParams.
    //
    // Why false: it means do NOT attach now. ListView will attach the row when its
    // turn comes. With true, inflate would return the PARENT, not the row — and you would get a
    // ListView instead of a row, with a ClassCastException at findViewById.
    //
    // What happens if you put null instead of parent: inflate has nowhere to take
    // the LayoutParams from, so the row gets default LayoutParams. On a row with
    // match_parent height, the result would be a row of zero or wrong height.
    // You see it immediately: the rows overlap or disappear.
    //
    // findViewById twice — only on the new row. The lookup walks the
    // view tree; on a row with two TextViews it is cheap, but multiplied by 100
    // rows and by every scroll it becomes visible.
    //
    // setTag(holder) — View.setTag(Object) is a free field on any View. It has
    // nothing to do with display; it is just a place where you hang an object. Here we glue
    // the holder to its row.
    //
    // getTag() — it returns Object, so a cast is needed. The cast is NOT checked by
    // the compiler: if you put something else in the tag, ClassCastException at runtime; if
    // you forgot setTag, getTag() returns null and you get a NullPointerException at
    // the first line that touches the holder.
    //
    // ----------------------------------------------------------------------------------
    // THE FILLING PART
    // ----------------------------------------------------------------------------------
    //
    //   int number = getItem(position);                    // Integer → int (unboxing)
    //   holder.tvDecimal.setText(String.valueOf(number));  // "42"
    //   holder.tvBinary.setText(Integer.toBinaryString(number));  // "101010"
    //
    // int number = getItem(position) — getItem returns Integer, the assignment
    // unboxes it. If the list contained null, you would have a NullPointerException here.
    // It does not happen here: NumberData produces 1–100.
    //
    // String.valueOf(number) — equivalent to Integer.toString(number). More explicit
    // than number + "", which creates an extra StringBuilder.
    //
    // Integer.toBinaryString(number) — the binary representation without leading zeros and
    // without a prefix: 1 → "1", 100 → "1100100". That is why the second column is not
    // nicely aligned to the left, and item_number.xml right-aligns it and gives it a
    // monospaced font.
    //
    // return convertView — returns exactly the row received, now filled. You do not build
    // a new View on every call; that is the whole saving.
    //
    // Why not return holder.tvDecimal or something else: ListView needs the
    // whole row, not a child. The row is the LinearLayout with two TextViews.
    //
    // ----------------------------------------------------------------------------------
    // THE RECYCLING CYCLE, WITH WHAT convertView HOLDS AT EACH MOMENT
    // ----------------------------------------------------------------------------------
    //
    //   SCREEN (10 visible rows)                   RecycleBin (the ListView's pool)
    //   ┌───────────────────────────────┐
    //   │ row 0    position 0   tag=H0  │
    //   │ row 1    position 1   tag=H1  │
    //   │ row 2    position 2   tag=H2  │
    //   │ ...                           │
    //   │ row 9    position 9   tag=H9  │
    //   └───────────────────────────────┘
    //
    //   ① YOU SCROLL UP by one row
    //      row 0 leaves at the top
    //        → ListView.removeView(row0)
    //        → RecycleBin.add(row0)           ← row0 keeps tag=H0
    //      ListView asks for the row for position 10:
    //        getView(10, row0, parent)
    //          convertView = row0              ← a View object, NOT null
    //          getTag()    = H0                ← the holder created at position 0
    //          H0.tvDecimal.setText("11")
    //          H0.tvBinary.setText("1011")
    //          return row0
    //
    //   ② THE SCREEN NOW LOOKS LIKE
    //   ┌───────────────────────────────┐
    //   │ row 1    position 1   tag=H1  │
    //   │ row 2    position 2   tag=H2  │
    //   │ ...                           │
    //   │ row 9    position 9   tag=H9  │
    //   │ row 0    position 10  tag=H0  │   ← the same View, different text
    //   └───────────────────────────────┘
    //
    //   ③ YOU SCROLL BACK DOWN
    //      row 0 leaves at the bottom → RecycleBin
    //      getView(0, row0, parent)
    //          getTag() = H0
    //          setText("1"), setText("1")   ← what was there at the start is rewritten
    //
    // What to remember from the diagram: convertView is not "some row", it is a specific
    // View object, with its tag. The position does not travel with the row; the text does.
    // That is why setText is ALWAYS done, on both branches — if you skipped
    // the filling on the else branch, the row would show the old text.
    //
    // How many rows exist in total: roughly as many as fit on the screen, plus
    // one or two in the buffer. Not 100. That is the whole win: 10 View objects instead of 100,
    // no matter how far you scroll.
    //
    // When the pool empties: on setAdapter with a new adapter, on notifyDataSetChanged
    // (partially), on the destruction of the ListView. It does not empty on scroll — that is why
    // it works.
    //
    // ----------------------------------------------------------------------------------
    // WHAT WOULD HAPPEN IF YOU IGNORED RECYCLING
    // ----------------------------------------------------------------------------------
    //
    // The wrong version, for comparison — it is NOT in the repo:
    //
    //   View row = layoutInflater.inflate(R.layout.item_number, parent, false);
    //   // ... findViewById, setText ...
    //   return row;
    //
    // -   100 rows inflated for 100 elements, although ~10 fit on the screen;
    // -   memory grows with every scroll, because every row left in the tree
    //     holds a View and two TextViews;
    // -   ListView has nothing left to recycle, so convertView no longer arrives either;
    // -   the scroll becomes jerky, because every frame inflates XML.
    //
    // The code would be CORRECT — it would display the same numbers — but it would be slow.
    // Recycling is optimization, not correctness. At 100 rows the difference is small; at
    // 10,000 rows it is the difference between an app that works and one that does not.
    //
    // What inflate costs: parsing the XML is cached by Resources, but building the
    // View objects is not. For a row with two TextViews, we are talking microseconds.
    // Multiplied by 100 rows and by every scroll frame, it reaches milliseconds —
    // exactly the budget of a 60fps frame (16 ms).
    //
    // ==================================================================================
    // WHAT HAPPENS IF YOU FORGET A findViewById
    // ==================================================================================
    //
    //   holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);
    //   // holder.tvBinary is missing
    //
    // It compiles. The list displays. The second column is empty on all rows. On
    // filling:
    //
    //   holder.tvBinary.setText(...)   →  NullPointerException:
    //     Attempt to invoke virtual method 'void android.widget.TextView.setText(...)'
    //     on a null object reference
    //
    // The difference from the missing setTag: there the holder is null, here the holder exists,
    // but one of its fields is null. The message says so: "invoke virtual method ... on a null
    // object reference" means the receiver of the call is null, that is tvBinary.
    //
    // ==================================================================================
    // WHY YOU CANNOT PUT DATA IN THE HOLDER
    // ==================================================================================
    //
    // You might be tempted to write:
    //
    //   holder.number = getItem(position);   // ← wrong
    //
    // and read the value on click. It does not work, because the holder is REUSED:
    // between bind and click, the row can be recycled for another position, and the value
    // in the holder would belong to another element. The holder holds VIEWS, not data. Data
    // goes into the views (setText), not into the holder.
    //
    // ==================================================================================
    // HOW IT COMPARES WITH ARRAYADAPTER
    // ==================================================================================
    //
    //   ArrayAdapter                      NumberListAdapter
    //   ├── getCount() → size()           ├── getCount() → size()
    //   ├── getItem() → list.get()        ├── getItem() → list.get()
    //   ├── getItemId() → position        ├── getItemId() → the number
    //   └── getView()                     └── getView()
    //         ├── inflate / reuse               ├── if (convertView == null)
    //         ├── findViewById(text1)           │     ├── inflate
    //         └── setText(toString())           │     ├── new ViewHolder
    //                                           │     ├── findViewById × 2
    //                                           │     └── setTag
    //                                           ├── else getTag
    //                                           └── setText × 2
    //
    // The same four methods, the same structure. The difference is that the second variant gives
    // you access to convertView and to the row's layout. All you gain is control; all
    // you pay is code.
    //
    // ==================================================================================
    // COMMON MISTAKES, IN ORDER OF FREQUENCY
    // ==================================================================================
    //
    //   1. setTag is missing → NPE on the first scroll.
    //   2. setTag placed on the else branch → a new holder is created on every display;
    //      it does not crash, but you lose the whole saving.
    //   3. findViewById called on every call, outside the if → it works, but
    //      the lookup happens 100 times more often than it should.
    //   4. inflate with `true` instead of `false` → ClassCastException or stuck-together rows.
    //   5. getCount() returns numbers.size() + 1 → IndexOutOfBoundsException on the last one.
    //   6. return holder.tvDecimal instead of convertView → ListView receives a TextView
    //      instead of the whole row; the second column disappears.
}
```

**What you must remember from this file:** the four methods of `BaseAdapter` are a contract, not a suggestion. `getCount` and `getView` are the only ones called for drawing; `getItem` and `getItemId` are for clicks and for your own code. And `setTag` / `getTag` are the bridge between the recycled row and its holder.

**Why `BaseAdapter` and not `ArrayAdapter`:** `ArrayAdapter` is a complete, ready-made implementation, for a single text. `BaseAdapter` is the skeleton: it implements the `ListAdapter` and `SpinnerAdapter` interfaces, but leaves **four abstract methods** — `getCount`, `getItem`, `getItemId`, `getView`. You write exactly what is missing.

**Why not extend `ArrayAdapter` and override `getView`:** you could. But you would inherit a constructor that requires a `resource` with `text1`, an `mFieldId` you do not use and a `getFilter()` that makes no sense. `BaseAdapter` gives you exactly the four methods, with no baggage.

---

## 28.7 `TwoColumnActivity.java` — step 2, the screen

The file is almost identical to step 1. The lesson is best seen by putting them side by side: seven identical lines, a single different class.

```java
/*
 * ======================================================================================
 * FILE: TwoColumnActivity.java
 * ======================================================================================
 * LOCATION: DMA06/src/main/java/ro/ase/ie/dma06/activities/TwoColumnActivity.java
 * PACKAGE:  ro.ase.ie.dma06.activities
 * ROLE:     step 2. The same ListView as step 1, but with a custom adapter that
 *           fills two columns.
 *
 * FILE STRUCTURE (2 parts):
 *   1. imports     — 7 lines
 *   2. onCreate    — 8 lines: layout, findViewById, adapter, setAdapter
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - The id `lvNumbers` is THE SAME as in step 1, but in another layout. No conflict.
 *   - The activity does not know what is in a row: it does not touch tvDecimal / tvBinary.
 *   - The difference from step 1 is a single class: NumberListAdapter.
 * ======================================================================================
 */

// ======================================================================================
// BLOCK 1 — THE PACKAGE AND THE IMPORTS
// ======================================================================================
// Compared with SingleColumnActivity, the `android.widget.ArrayAdapter` import is gone and
// `ro.ase.ie.adapters.NumberListAdapter` has appeared. The rest is identical.
// ======================================================================================

package ro.ase.ie.dma06.activities;      // the package of the screens

import android.os.Bundle;                // the parameter of onCreate
import android.widget.ListView;          // THE SAME widget as step 1

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.adapters.NumberListAdapter;   // the custom adapter, from the `adapters` package
import ro.ase.ie.data.NumberData;             // the same data as in step 1
import ro.ase.ie.dma06.R;

// ======================================================================================
// THEORY BLOCK: FROM ARRAYADAPTER TO BASEADAPTER
// ======================================================================================
/*
 * 1. WHAT STAYS IDENTICAL
 *    -   The widget: ListView.
 *    -   The data: NumberData.getNumbers().
 *    -   The cycle: onCreate → setContentView → findViewById → new Adapter → setAdapter.
 *    -   Recycling: ListView still does it; it is just that now you write it.
 *
 * 2. WHAT CHANGES
 *    -   The adapter: ArrayAdapter (SDK) → NumberListAdapter (yours).
 *    -   The row layout: android.R.layout.simple_list_item_1 → item_number.xml.
 *    -   The number of columns: 1 → 2.
 *    -   Who calls findViewById: the SDK → your code, once per row.
 *
 * 3. WHAT THE ACTIVITY MUST DO EXTRA
 *    -   Nothing, apart from passing `this` (Context) to the custom adapter.
 *    -   ArrayAdapter took the Context through the constructor; NumberListAdapter likewise.
 *    -   So the difference shows only in the type of the variable.
 *
 * 4. WHAT THE ACTIVITY MUST NOT DO
 *    -   Know the ids inside the row (tvDecimal, tvBinary).
 *    -   Know how many columns the row has.
 *    -   Touch convertView, ViewHolder or recycling.
 *    Any such line would be a leak of responsibility: the activity would have to be
 *    changed when the row changes.
 *
 * DIAGRAM OF RESPONSIBILITIES:
 *
 *   TwoColumnActivity                 NumberListAdapter
 *   ├── setContentView(layout)        ├── getCount()   → 100
 *   ├── findViewById(lvNumbers)       ├── getItem(n)
 *   ├── new NumberListAdapter(        ├── getItemId(n)
 *   │       this,                     └── getView(n, convertView, parent)
 *   │       NumberData.getNumbers())        ├── inflate / getTag
 *   └── setAdapter(adapter)                 ├── findViewById × 2
 *                                           └── setText × 2
 *
 * 5. WHY THE IDS DO NOT CLASH
 *    R.id.lvNumbers is a single int constant, generated once for all layouts.
 *    The value is the same, and findViewById looks for it in the tree attached to the
 *    current activity. If you had two ListViews with the same id IN THE SAME layout, the
 *    first one found would be returned — and the second would be inaccessible.
 */

/**
 * Step 2: two columns in a ListView.
 * A custom adapter fills each column of the row layout.
 */
public class TwoColumnActivity extends AppCompatActivity {

    // ==================================================================================
    // METHOD 1 — onCreate
    // ==================================================================================
    // Theory:  the same lifecycle; only the adapter class changes.
    // Logic:   1. super  2. setContentView  3. findViewById  4. new NumberListAdapter
    //          5. setAdapter
    // Risk:    `this` must be a Context; if you passed something else, LayoutInflater.from
    //          would throw.
    // Ref:     chapter 12.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);                    // 1. the lifecycle
        setContentView(R.layout.activity_two_column);          // 2. includes the header + ListView

        ListView lvNumbers = findViewById(R.id.lvNumbers);     // 3. THE SAME id as in step 1

        NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
        //                                ↑ Context                  ↑ List<Integer> with 100
        lvNumbers.setAdapter(adapter);                         // 4. binds the list to the widget
    }

    // The same id, another layout — lvNumbers appears both in activity_single_column.xml and in
    // activity_two_column.xml. It is not a problem: ids are unique PER LAYOUT, not globally.
    // findViewById looks only in the current layout's tree, so it finds the ListView
    // of the current screen.
    //
    // `this` as the Context — the adapter needs it for the LayoutInflater. Here it is
    // the only place where the activity touches the inflate detail.
    //
    // The activity does not know what is in a row — there is no findViewById(R.id.tvDecimal)
    // here. The two columns are the adapter's business. If you rename tvDecimal in the
    // XML, only NumberListAdapter changes.
    //
    // Comparison with step 1: the same structure, four lines, only the adapter class
    // different. The lesson: the activity hardly changes; the adapter is where everything
    // happens.
    //
    // What would happen if you passed `null` as the Context: LayoutInflater.from(null) throws
    // NullPointerException in the adapter's constructor, so at
    // new NumberListAdapter(null, ...). The error appears early, in onCreate, not on the first
    // row — good for debugging.
    //
    // ==================================================================================
    // WHY THE ACTIVITY DOES NOT NEED `implements`
    // ==================================================================================
    //
    // No interface is needed because the activity does not receive events from the
    // adapter. There is no "onItemBound" or "onRowCreated". The adapter is a passive object:
    // ListView asks, it answers. The activity only builds it and hands it over.
    //
    // If you wanted to react to a click on a row, you would have two options:
    //   1. lvNumbers.setOnItemClickListener(...)  → in the activity, with the position
    //   2. a listener put on the row, in getView  → in the adapter
    // Neither is needed here: the rows are not clickable.
    //
    // ==================================================================================
    // WHAT WOULD HAPPEN IF YOU PUT THE ADAPTER IN A STATIC FIELD
    // ==================================================================================
    //
    //   private static NumberListAdapter adapter;   // ← wrong
    //
    // The adapter holds the list and, through the holders, the views. A static field would
    // keep the adapter alive after the activity is destroyed, and the views in the holders
    // would hold the old tree. The result: a memory leak that grows with every
    // rotation. The adapter is always an instance field (or a local variable, as
    // here) — never static.
}
```

**Why the block insists on "what the activity must not do":** because most mistakes with `ListView` come from trying to control the row from the activity. `findViewById(R.id.tvDecimal)` inside an activity returns `null` — the rows are not yet in the activity's tree, they are created on demand by the adapter. If you need a view from a row, you take it from the adapter, not from the activity.

---

## 28.8 `activity_two_column.xml` — header + list

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FILE: activity_two_column.xml
     ==================================================================================
     LOCATION: DMA06/src/main/res/layout/activity_two_column.xml
     ROLE:     the step 2 layout: fixed header at the top, ListView below.
     CONTAINS: 1 × include (layout_number_header), 1 × ListView
     IDS:      lvNumbers
     ================================================================================== -->

<!-- A vertical column: the header at the top (as tall as its content), the list below (the rest of the screen). -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- The header is a separate file, reused by step 3 as well.
         The content of the included file is inflated IN PLACE OF the tag: the result is as if
         you had written the header directly here, but the definition exists in a single place. -->
    <include layout="@layout/layout_number_header" />

    <!-- The ListView takes all the space left after the header.
         0dp + weight="1" = "my base size is zero; take from the free space".
         With match_parent, the list would ask for the parent's whole height, would overflow the
         bottom edge and would be clipped. -->
    <ListView
        android:id="@+id/lvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>

<!-- ======================================================================================
     HOW THE SPACE IS DIVIDED, CONCRETELY
     ======================================================================================
     Screen: 800dp tall.
       the header: wrap_content → measures the text + padding 12dp × 2 ≈ 60dp
       the list:   0dp + weight 1 → receives 800 − 60 = 740dp

     If the list had match_parent:
       the header: 60dp
       the list:   asks for 800dp → total 860dp → overflows by 60dp
       result: the last rows go under the screen edge and cannot be scrolled
               to the end, because ListView believes it has room

     Why 0dp and not wrap_content with weight: weight is applied to the space REMAINING after
     the base size. With 0dp, the base is zero, so the whole available height enters
     the weight calculation. With wrap_content, the list would receive "the height of the content
     + a share of the rest", which is not what you want.
     ====================================================================================== -->

<!-- ======================================================================================
     WHAT TO REMEMBER FROM THE FILE
     ======================================================================================
     <include>                the header is defined once, used by 2 screens
     0dp + weight="1"         the list takes the rest after the header
     match_parent + weight    WRONG: the list would overflow the bottom edge
     header outside the list  stays fixed on scroll; inside the list it would scroll with it
     child order              the header first, the list second; weight does not change the order
     ====================================================================================== -->
```

**Why the header is outside the list:** it stays fixed when you scroll. If it were the first element in the list, it would scroll with it — and you would need an adapter with two row types (`getItemViewType`), much more complicated for a static header.

**What happens if you put `include` after `ListView`:** the header would appear **below** the list. The order of the children in a vertical `LinearLayout` is the XML order, and `weight` does not change the order, it only divides the space.

**`<include>` and `layout_*`:** you can override layout attributes on the `<include>` tag (for example `android:layout_marginTop`). You cannot override the `android:id` of the included root unless you declare it explicitly on the `include`. There is no need here: the header has no id.

---

## 28.9 `layout_number_header.xml` — the reused header

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FILE: layout_number_header.xml
     ==================================================================================
     LOCATION: DMA06/src/main/res/layout/layout_number_header.xml
     ROLE:     the two-column header, reused by steps 2 and 3.
     CONTAINS: 2 × TextView ("Decimal", "Binary")
     IDS:      none — nothing in the code touches it
     ================================================================================== -->

<!-- Why a file with no ids still has a header: because it is reused. A file
     used by two screens is read twice as often as one used by a single
     one. And the fact that it has no ids is information: it means you can change any
     text in it without touching Java. -->

<!-- The two-column header. It has no ids: the code never touches it. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="?attr/colorSurfaceVariant"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="12dp">

    <!-- Column 1: "Decimal", aligned to the left (default) -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="@string/decimal"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <!-- Column 2: "Binary", aligned to the right.
         gravity="end" respects the reading direction; "right" would always have stayed on the right. -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:gravity="end"
        android:text="@string/binary"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />
</LinearLayout>

<!-- ======================================================================================
     WHAT TO REMEMBER FROM THE FILE
     ======================================================================================
     background="?attr/colorSurfaceVariant"      a different shade, works in dark mode
     textColor="?attr/colorOnSurfaceVariant"     the pair designed together with the background
     textAppearanceLabelLarge                    a label, smaller than BodyLarge
     paddingVertical="12dp"                      tighter than the row (14dp), on purpose
     alignment identical to item_number.xml      padding 16dp, weight 1, gravity end
     ====================================================================================== -->
```

**`background="?attr/colorSurfaceVariant"`** — a different background shade, so the header stands out from the rows. It comes from the Material3 theme, so it works in dark mode too.

**`textColor="?attr/colorOnSurfaceVariant"`** — the text colour suited to that background. The pair `colorSurfaceVariant` / `colorOnSurfaceVariant` is designed together; if you put a hardcoded `#888`, in dark mode the text disappears.

**The alignment must match `item_number.xml`:** the same `paddingHorizontal="16dp"`, the same `weight="1"`, the same `gravity="end"` on the second column. They are two separate files, so the matching is done by hand. If you change the padding in only one of them, the header no longer lines up with the rows — and you see it immediately.

**Why `paddingVertical="12dp"` here and `14dp` in the row:** the header is slightly tighter, so it reads as a label, not a row. The 2dp difference is intentional, not an oversight.

---

## 28.10 `NumberRecyclerAdapter.java` — step 3, the adapter

The same row, the same data, another contract. The difference from `NumberListAdapter` is not cosmetic: there are three mandatory methods instead of four, and `getView` has been cut in two.

```java
/*
 * ======================================================================================
 * FILE: NumberRecyclerAdapter.java
 * ======================================================================================
 * LOCATION: DMA06/src/main/java/ro/ase/ie/dma06/adapters/NumberRecyclerAdapter.java
 * PACKAGE:  ro.ase.ie.adapters
 * ROLE:     adapts List<Integer> to THE SAME two-column row (item_number.xml),
 *           but for a RecyclerView. The ViewHolder is mandatory, and getView is
 *           split into two methods.
 *
 * FILE STRUCTURE (5 parts):
 *   1. ViewHolder            — 10 lines: final fields + constructor with findViewById
 *   2. field + constructor   — 5 lines: only the list, no Context
 *   3. onCreateViewHolder    — 6 lines: creates the row and the holder
 *   4. onBindViewHolder      — 6 lines: fills the holder
 *   5. getItemCount          — 3 lines: how many elements there are
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - Three mandatory abstract methods: onCreateViewHolder, onBindViewHolder,
 *     getItemCount. There is no getView.
 *   - The generic parameter <NumberViewHolder> removes all the casts.
 *   - `super(itemView)` is mandatory in the holder's constructor.
 *   - There is no `convertView`: RecyclerView decides by itself which holder to reuse.
 * ======================================================================================
 */

// ======================================================================================
// BLOCK 1 — THE PACKAGE AND THE IMPORTS
// ======================================================================================
// Compared with NumberListAdapter, Context, BaseAdapter and the inflater as a field have
// disappeared; NonNull and RecyclerView have appeared. The `android.view.View` import
// remains: it is the type of the parameter in the holder's constructor.
// ======================================================================================

package ro.ase.ie.adapters;   // the same package as NumberListAdapter

import android.view.LayoutInflater;   // for inflate, in onCreateViewHolder
import android.view.View;             // the holder's itemView
import android.view.ViewGroup;        // the parent in onCreateViewHolder
import android.widget.TextView;       // the two columns

import androidx.annotation.NonNull;                 // contract: a parameter / result that is not null
import androidx.recyclerview.widget.RecyclerView;  // the base class and its ViewHolder

import java.util.List;

import ro.ase.ie.dma06.R;

// ======================================================================================
// THEORY BLOCK: RECYCLERVIEW.ADAPTER
// ======================================================================================
/*
 * 1. WHAT IT IS
 *    -   The abstract class that binds the data to RecyclerView.
 *    -   It has THREE abstract methods:
 *          onCreateViewHolder(ViewGroup parent, int viewType) → ViewHolder
 *          onBindViewHolder(ViewHolder holder, int position) → void
 *          getItemCount()                                    → int
 *    -   All the others have default implementations.
 *
 * 2. WHY IT HAS NO getView
 *    -   Because RecyclerView never asks for a View. It asks for a ViewHolder.
 *    -   A ViewHolder is a box with a View inside (itemView) plus references to
 *        its children. RecyclerView holds holders, not views.
 *    -   Why: so it can reuse a holder WITHOUT knowing what is in it. For that it
 *        needs a stable type (the holder), not some View.
 *
 * 3. WHY THREE METHODS AND NOT ONE
 *    -   Creation (inflate + findViewById) is expensive and rare.
 *    -   Filling (setText) is cheap and frequent.
 *    -   By separating them, RecyclerView can call only the second, thousands of times,
 *        without paying for the first.
 *    -   getItemCount is the third because RecyclerView must know how many positions
 *        exist BEFORE asking for any holder.
 *
 * 4. WHAT HAPPENS WITH THE OTHER METHODS
 *    getItemId(int)             → NO_ID (-1) by default; enabled with setHasStableIds(true)
 *    getItemViewType(int)       → 0 by default; for rows of different types
 *    onViewRecycled(holder)     → empty; good for cancelling an image download
 *    onViewAttachedToWindow     → empty; the holder enters the screen
 *    onViewDetachedFromWindow   → empty; the holder leaves the screen
 *    onAttachedToRecyclerView   → empty; the adapter is bound to a RecyclerView
 *    onDetachedFromRecyclerView → empty; the adapter is unbound
 *
 * 5. WHO CALLS WHAT
 *    RecyclerView + LayoutManager decide:
 *      - how many holders fit on the screen
 *      - which holder is reused for which position
 *      - when a new holder is needed
 *    The adapter only answers: "here is a new holder" / "I have filled the holder".
 *
 * 6. WHY IT IS AN ABSTRACT CLASS AND NOT AN INTERFACE
 *    Because it has state: the observer list (AdapterDataObservable), the reference to
 *    RecyclerView and the default implementations of the optional methods. An interface
 *    cannot hold state.
 *
 * DIAGRAM OF THE THREE METHODS:
 *
 *   RecyclerView                         Adapter
 *   ── getItemCount() ──────────────────▶ 100
 *   ── "I need a holder" ───────────────▶ onCreateViewHolder(parent, 0)
 *                                            └─ inflate + new NumberViewHolder
 *   ── "fill it for position 7" ────────▶ onBindViewHolder(holder, 7)
 *                                            └─ setText × 2
 *   ── "the holder left the screen" ────▶ (it goes into the pool; the adapter is not asked)
 */

/**
 * Step 3: fills the same row for a RecyclerView.
 * The ViewHolder is required here, and getView is split into two methods.
 */
public class NumberRecyclerAdapter
        extends RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder> {
        //                       ↑ the holder type, as a generic parameter

    // ==================================================================================
    // BLOCK 2 — THE INNER CLASS NumberViewHolder
    // ==================================================================================
    // Theory:  mandatory; RecyclerView.Adapter is parameterized with it.
    // Logic:   the constructor receives itemView, calls super(itemView) and looks up the children.
    // Risk:    without `super(itemView)`, RecyclerView has nothing to recycle — the holder has
    //          no associated View.
    // Ref:     chapter 12.
    // ==================================================================================
    static class NumberViewHolder extends RecyclerView.ViewHolder {
        final TextView tvDecimal;   // final: assigned in the constructor, never changes again
        final TextView tvBinary;    // final: assigned in the constructor, never changes again

        NumberViewHolder(@NonNull View itemView) {
            super(itemView);                                        // mandatory: saves the row
            tvDecimal = itemView.findViewById(R.id.tvDecimal);      // lookup 1, once per holder
            tvBinary = itemView.findViewById(R.id.tvBinary);        // lookup 2, once per holder
        }
    }

    // The generic parameter — RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder>
    // declares WHAT TYPE OF HOLDER the adapter produces. From here on, all the methods
    // work with NumberViewHolder, not with RecyclerView.ViewHolder: onCreateViewHolder
    // returns it, onBindViewHolder receives it. NO cast anywhere — that is the
    // gain over getTag().
    //
    // Why NumberRecyclerAdapter.NumberViewHolder and not just NumberViewHolder: in the
    // `extends` declaration you are not yet inside the class, so the name of the inner
    // class must be qualified. In the rest of the file you can write just NumberViewHolder.
    //
    // super(itemView) — mandatory. RecyclerView.ViewHolder has no constructor without
    // parameters, so the compiler forces you to call it. It saves the row in itemView.
    //
    // findViewById in the holder's constructor — this is the CREATION half. It runs
    // once per holder, not on every display.
    //
    // The final fields — they can be final because they are assigned in the constructor. In
    // NumberListAdapter they could not, because they were assigned after `new ViewHolder()`.
    // This small difference is exactly why RecyclerView moved the lookup
    // into the constructor.
    //
    // static class NumberViewHolder — static again, for the same two reasons: no
    // implicit reference to the adapter and no dependency on an adapter instance.
    // Here it is `static class` without `private`: the type appears in the class's public
    // signature (RecyclerView.Adapter<...NumberViewHolder>), so there is no point hiding it.
    // In NumberListAdapter the holder is `private static class`, because it appears in
    // no public signature.
    //
    // @NonNull on itemView — contract: RecyclerView never gives you null. The annotation
    // does not change the runtime; it is read by lint and by Android Studio.

    // ==================================================================================
    // BLOCK 3 — THE FIELD AND THE CONSTRUCTOR
    // ==================================================================================
    // Theory:  it receives only the list; the Context is taken from `parent` on creation.
    // Logic:   this.numbers = numbers.
    // Risk:    if you also asked for a Context, you would have an extra parameter that is not
    //          used anywhere in the class.
    // Ref:     chapter 12.
    // ==================================================================================
    private final List<Integer> numbers;   // the data source, by reference

    public NumberRecyclerAdapter(List<Integer> numbers) {
        this.numbers = numbers;   // we do NOT copy the list
    }

    // The adapter's constructor receives only the list — unlike
    // NumberListAdapter, it does not need a Context. The context is taken when needed from
    // parent.getContext(), in onCreateViewHolder.
    //
    // Why it has no LayoutInflater as a field: because it can take one from `parent` on
    // every creation, and creations are rare. A field would be a premature optimization —
    // and would require a Context in the constructor.

    // ==================================================================================
    // BLOCK 4 — onCreateViewHolder, THE CREATION HALF
    // ==================================================================================
    // Theory:  creates a NEW holder: inflates the row and builds the box.
    // Logic:   1. LayoutInflater.from(parent.getContext())
    //          2. inflate(item_number, parent, false)
    //          3. new NumberViewHolder(view)
    // Risk:    if you forget `false`, inflate returns the parent, not the row.
    // Ref:     chapter 12.
    // ==================================================================================
    @NonNull
    @Override
    public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Runs only when a new row is needed
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_number, parent, false);   // THE SAME layout as step 2
        return new NumberViewHolder(view);                       // the holder, not the view
    }

    // When it runs: only when RecyclerView needs a NEW holder — the recycling pool
    // is empty. At startup, for the first visible rows; then less and less
    // often.
    //
    // `parent` — the RecyclerView. The Context for the inflater is taken from it, and it
    // supplies the LayoutParams.
    //
    // `viewType` — here it is always 0, because we do not override getItemViewType. If you
    // had two kinds of rows (header + item), you would return 0/1 from getItemViewType
    // and switch here, to inflate the right layout.
    //
    // LayoutInflater.from(parent.getContext()) — a layoutInflater field is no longer
    // needed, because `parent` carries the context with it.
    //
    // .inflate(R.layout.item_number, parent, false) — exactly the same call as with ListView:
    // the same layout, the same parameters, the same false.
    //
    // return new NumberViewHolder(view) — returns the HOLDER, not the view. RecyclerView
    // needs the holder so it knows what it created and can recycle it.
    //
    // @NonNull — contract: parent is not null, the result is not null. Lint checks it.
    //
    // Why the method does not return View: because RecyclerView does not work with Views.
    // It works with holders, which know what children they contain. A returned View would
    // have to be re-inspected on every reuse — exactly what ViewHolder avoids.

    // ==================================================================================
    // BLOCK 5 — onBindViewHolder AND getItemCount
    // ==================================================================================
    // Theory:  fills an existing holder with the data at the given position.
    // Logic:   1. numbers.get(position)  2. setText × 2
    // Risk:    if you do a `findViewById` here, you have lost the whole gain of the holder.
    // Ref:     chapter 12.
    // ==================================================================================
    @Override
    public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
        // Runs each time a row shows a number
        int number = numbers.get(position);                          // Integer → int
        holder.tvDecimal.setText(String.valueOf(number));            // column 1
        holder.tvBinary.setText(Integer.toBinaryString(number));     // column 2
    }

    // ----------------------------------------------------------------------------------
    // METHOD 3 — getItemCount
    // ----------------------------------------------------------------------------------
    // Theory:  replaces getCount() from BaseAdapter.
    // Logic:   the size of the list.
    // Risk:    if it lies, onBindViewHolder receives an invalid position.
    // Ref:     chapter 12.
    // ----------------------------------------------------------------------------------
    @Override
    public int getItemCount() {
        return numbers.size();   // 100
    }

    // When onBindViewHolder runs: every time a row SHOWS an element —
    // on the first display, on every reuse after a scroll, after notifyItemChanged,
    // after an animation.
    //
    // There is no convertView — the holder arrives already created. There is no
    // `if (convertView == null)`, because the decision has already been made by RecyclerView.
    //
    // There is no findViewById — the references are in the holder, taken at creation.
    //
    // numbers.get(position) directly — the adapter has no getItem(position). If you need
    // it (for example for a click), you add it as a method of your own.
    //
    // getItemCount() replaces getCount() — the same role: how many elements the list has.
    //
    // If getItemCount() lies: if it returns more than numbers.size(),
    // onBindViewHolder reaches numbers.get(position) with an invalid position →
    // IndexOutOfBoundsException. If it returns less, the last elements simply
    // do not appear.
    //
    // Why onBindViewHolder returns void: because the holder is already at RecyclerView.
    // Nothing needs to be returned — the method only modifies an object that RecyclerView
    // already has. In getView, the return was necessary because ListView had no other
    // way to find out which view to add.
    //
    // What happens if you tap on a row: nothing. There is no listener. In a real
    // app, you would put an OnClickListener on holder.itemView right in onBindViewHolder —
    // and you would take care to use holder.getAdapterPosition(), not `position`, because
    // the position can change between the bind and the click.
    //
    // ==================================================================================
    // GETVIEW()  vs  onCreateViewHolder() + onBindViewHolder() — THE SAME PICTURE, SPLIT
    // ==================================================================================
    //
    // ┌─────────────────────────────────────────────────────────────────────────────────┐
    // │                          LISTVIEW: A SINGLE METHOD                              │
    // │                                                                                 │
    // │   getView(position, convertView, parent)                                        │
    // │   ├─────────────────────────────────────────────────────────────────────────┐   │
    // │   │ PART A — CREATION                                     only if null     │   │
    // │   │   if (convertView == null) {                                           │   │
    // │   │       convertView = inflate(...)          ← XML → objects              │   │
    // │   │       holder = new ViewHolder()            ← the empty box              │   │
    // │   │       holder.tvDecimal = findViewById(...) ← lookup                     │   │
    // │   │       holder.tvBinary  = findViewById(...) ← lookup                     │   │
    // │   │       convertView.setTag(holder)           ← glues the box              │   │
    // │   │   }                                                                    │   │
    // │   ├─────────────────────────────────────────────────────────────────────────┤   │
    // │   │ PART B — FILLING                                 on EVERY call          │   │
    // │   │   else { holder = getTag() }              ← takes the box              │   │
    // │   │   holder.tvDecimal.setText(...)                                        │   │
    // │   │   holder.tvBinary.setText(...)                                         │   │
    // │   │   return convertView                                                   │   │
    // │   └─────────────────────────────────────────────────────────────────────────┘   │
    // │                                                                                 │
    // │   ↑ the two parts are in the SAME method, separated only by an `if`             │
    // └─────────────────────────────────────────────────────────────────────────────────┘
    //
    //                                     ↓  the split  ↓
    //
    // ┌─────────────────────────────────────────────────────────────────────────────────┐
    // │                       RECYCLERVIEW: TWO SEPARATE METHODS                        │
    // │                                                                                 │
    // │   onCreateViewHolder(parent, viewType)      onBindViewHolder(holder, position)  │
    // │   ├──────────────────────────────────┐      ├──────────────────────────────────┤
    // │   │ PART A — CREATION                │      │ PART B — FILLING                 │
    // │   │   View view = inflate(...)       │      │   int number = numbers.get(pos)  │
    // │   │   return new NumberViewHolder(   │      │   holder.tvDecimal.setText(...)  │
    // │   │       view)                      │      │   holder.tvBinary.setText(...)   │
    // │   │       ├─ super(itemView)         │      │   (void — returns nothing)       │
    // │   │       ├─ findViewById × 2        │      │                                  │
    // │   │       └─ final fields            │      │                                  │
    // │   └──────────────────────────────────┘      └──────────────────────────────────┘
    // │                                                                                 │
    // │   WHO DECIDES WHICH ONE IS CALLED:                                              │
    // │     empty pool          → onCreateViewHolder + onBindViewHolder                 │
    // │     pool has a holder   → only onBindViewHolder                                 │
    // │                                                                                 │
    // │   WHO TAKES THE PLACE OF convertView: the internal pool (RecycledViewPool)      │
    // │   WHO TAKES THE PLACE OF setTag/getTag: the adapter's generic type              │
    // └─────────────────────────────────────────────────────────────────────────────────┘
    //
    // Read the diagram from top to bottom, then from bottom to top. Top: one method, two
    // branches, an `if` that separates them. Bottom: two methods, each with a single branch,
    // and the decision moved into the framework. THE SAME WORK, DIVIDED DIFFERENTLY.
    //
    // WHAT IS GAINED CONCRETELY:
    //   refilling without creation  the pool gives a ready-made holder; only onBindViewHolder
    //   animations                  RecyclerView knows which holder moved
    //   partial updates             notifyItemChanged(5) rebinds only position 5
    //   typed code                  the holder is a parameter, not an Object from a tag
    //   testability                 you can test onBindViewHolder with a holder built by hand
    //
    // WHAT IS LOST: two methods instead of one, one extra generic parameter,
    // a mandatory super(itemView). For a list of 100 numbers, the gain is small.
    // For a list of 10,000 images, it is the difference between 60fps and 20fps.
    //
    // ==================================================================================
    // WHAT HAPPENS IF YOU FORGET super(itemView)
    // ==================================================================================
    //
    //   NumberViewHolder(@NonNull View itemView) {
    //       // super(itemView);   ← removed
    //       tvDecimal = itemView.findViewById(R.id.tvDecimal);
    //   }
    //
    // It does not compile: RecyclerView.ViewHolder has no constructor without parameters, and
    // the compiler tries to call super() implicitly. The error is at compile time, not at
    // runtime — so you catch it immediately:
    //
    //   error: constructor ViewHolder in class ViewHolder cannot be applied to given types;
    //     required: View
    //     found: no arguments
    //
    // If you called super(null), it would compile, but itemView would be null and RecyclerView
    // would crash on the first layout, when it tries to add the holder to the tree.
    //
    // ==================================================================================
    // RECYCLEDVIEWPOOL — WHAT IT HOLDS AND WHEN IT EMPTIES
    // ==================================================================================
    //
    //   RecycledViewPool
    //     ├── SparseArray<ScrapData> per viewType
    //     │     ├── viewType 0 → list of holders (max 5 by default)
    //     │     └── viewType 1 → list of holders
    //     └── each holder holds itemView + the references from the constructor
    //
    // By default, the pool keeps a maximum of 5 holders per type. The rest are left to
    // be collected. For a list with 10 visible rows, 5 in the pool are enough.
    //
    // It empties on setAdapter with another adapter, on setRecycledViewPool(null) and on
    // the destruction of the RecyclerView. It does not empty on scroll.
    //
    // ==================================================================================
    // HOW TO ADD A CLICK ON A ROW
    // ==================================================================================
    //
    //   @Override
    //   public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
    //       int number = numbers.get(position);
    //       holder.tvDecimal.setText(String.valueOf(number));
    //       holder.tvBinary.setText(Integer.toBinaryString(number));
    //       holder.itemView.setOnClickListener(v ->
    //               Toast.makeText(v.getContext(),
    //                       "Position " + holder.getAdapterPosition(),
    //                       Toast.LENGTH_SHORT).show());
    //   }
    //
    // Why getAdapterPosition() and not `position`: between the moment of the bind and the
    // moment of the click, the list can change (an element deleted, one added). `position`
    // is the value from the bind, which can be stale; getAdapterPosition() returns the
    // current position. In the repo code there is no click, so there is no problem either.
    //
    // ==================================================================================
    // WHY THE HOLDER DOES NOT NEED THE ADAPTER
    // ==================================================================================
    //
    // A ViewHolder holds itemView and two children. It needs no list, no position or
    // adapter in order to exist. That is why it can be `static`: it depends on no
    // instance of the outer class. All the information arrives as a parameter.
    //
    // In NumberListAdapter, the holder is built in getView and filled immediately, in the same
    // place. Here it is built in onCreateViewHolder and filled in another method, with data
    // received as a parameter. The design difference shows in the constructor's signature.
}
```

**What you must remember from this file:** `RecyclerView.Adapter` has exactly three abstract methods and **no `getView`**. The reason is that `RecyclerView` never asks for a `View` — it asks for a `ViewHolder`. And the holder is typed through the generic parameter, so all the casts disappear.

**Why `getItemCount()` is not called `getCount()`:** because it is not the same interface. `BaseAdapter` implements `ListAdapter`, which has `getCount()`. `RecyclerView.Adapter` is an independent class, with its own naming. The resemblance is functional, not contractual.

**What happens with `getItemId`:** in `RecyclerView.Adapter` it exists, but returns `NO_ID` (`-1`) by default. If you want stable ids, you override the method and call `setHasStableIds(true)` on the adapter. There is no need here: there is no selection.

---

## 28.11 `RecyclerViewActivity.java` — step 3, the screen

Here you can see what `ListView` kept inside: `LayoutManager`, `ItemDecoration`, `ItemAnimator`. Each is a separate object, set from code.

```java
/*
 * ======================================================================================
 * FILE: RecyclerViewActivity.java
 * ======================================================================================
 * LOCATION: DMA06/src/main/java/ro/ase/ie/dma06/activities/RecyclerViewActivity.java
 * PACKAGE:  ro.ase.ie.dma06.activities
 * ROLE:     step 3. The same row, the same data, but with a RecyclerView. Here you see
 *           what ListView kept inside: LayoutManager, ItemDecoration, ItemAnimator.
 *
 * FILE STRUCTURE (2 parts):
 *   1. imports     — 10 lines, of which 3 from androidx.recyclerview
 *   2. onCreate    — 12 lines: layout, RecyclerView, LayoutManager, decoration, adapter
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - Without setLayoutManager, RecyclerView displays NOTHING and gives no error.
 *   - DividerItemDecoration takes the orientation as an `int`, not as an object.
 *   - The adapter does not receive a Context: it takes it from `parent` on creation.
 * ======================================================================================
 */

// ======================================================================================
// BLOCK 1 — THE PACKAGE AND THE IMPORTS
// ======================================================================================
// Three new imports compared with step 2, all from androidx.recyclerview:
//   RecyclerView            the widget
//   LinearLayoutManager     the arrangement
//   DividerItemDecoration   the separator
// ======================================================================================

package ro.ase.ie.dma06.activities;      // the package of the screens

import android.os.Bundle;                // the parameter of onCreate

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.DividerItemDecoration;   // the line between rows
import androidx.recyclerview.widget.LinearLayoutManager;    // the vertical arrangement
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.adapters.NumberRecyclerAdapter;
import ro.ase.ie.data.NumberData;
import ro.ase.ie.dma06.R;

// ======================================================================================
// THEORY BLOCK: THE FOUR PIECES OF A RECYCLERVIEW
// ======================================================================================
/*
 * 1. ADAPTER — THE CONTENT
 *    What is displayed. It creates holders and fills them. It does not know where they sit.
 *
 * 2. LAYOUTMANAGER — THE ARRANGEMENT
 *    Where they sit. How many rows fit, how tall each one is, how the scroll is computed.
 *    Without it, RecyclerView has nobody to tell it what to draw.
 *
 * 3. ITEMDECORATION — THE DECORATION
 *    What is drawn over or under the rows: separators, margins, shadows.
 *    Unlike ListView, there is no `android:divider` in the XML.
 *
 * 4. ITEMANIMATOR — THE ANIMATION
 *    How the rows move when the data changes. It comes by default (DefaultItemAnimator);
 *    you do not configure it here.
 *
 * THE SEPARATION:
 *
 *   ┌──────────────────────────────────────────────────────────────────────────────┐
 *   │                            RecyclerView                                      │
 *   │                                                                              │
 *   │   ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐   ┌──────────┐  │
 *   │   │   Adapter    │   │  LayoutManager   │   │ItemDecoration│   │ Animator │  │
 *   │   │  (content)   │   │  (arrangement)   │   │(separators)  │   │(movement)│  │
 *   │   └──────┬───────┘   └────────┬─────────┘   └──────┬───────┘   └────┬─────┘  │
 *   │          │                    │                    │                │        │
 *   │   what is seen          where it is seen       what is seen    how it        │
 *   │   in each row           on the screen          between rows    moves         │
 *   └──────────────────────────────────────────────────────────────────────────────┘
 *
 *   ListView had all four crammed into a single class. That is why you could not
 *   change the arrangement without changing the widget.
 *
 * THE PRACTICAL CONSEQUENCE:
 *   -   You swap LinearLayoutManager for GridLayoutManager(2) → a grid, with no
 *       change in the adapter.
 *   -   You add an ItemDecoration → separators, without touching the adapter.
 *   -   You swap the adapter → other content, without touching the arrangement.
 *
 * WHY "FOUR" AND NOT THREE:
 *   ItemAnimator exists and works even if you do not configure it. A RecyclerView without
 *   setItemAnimator has a DefaultItemAnimator, which animates additions, deletions and
 *   moves. If you remove it with setItemAnimator(null), the animations disappear, but the
 *   list works.
 */

/**
 * Step 3: the same two columns in a RecyclerView.
 * RecyclerView needs a LayoutManager, and dividers are added separately.
 */
public class RecyclerViewActivity extends AppCompatActivity {

    // ==================================================================================
    // METHOD 1 — onCreate
    // ==================================================================================
    // Theory:  the lifecycle; here the four pieces are assembled.
    // Logic:   1. super  2. setContentView  3. findViewById
    //          4. LayoutManager + setLayoutManager
    //          5. DividerItemDecoration + addItemDecoration
    //          6. adapter + setAdapter
    // Risk:    without setLayoutManager, the screen stays empty, with no exception.
    // Ref:     chapter 12 and chapter 23 (the ListView → RecyclerView migration).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);                          // 1. the lifecycle
        setContentView(R.layout.activity_recycler_view);             // 2. header + RecyclerView

        RecyclerView rvNumbers = findViewById(R.id.rvNumbers);       // 3. the only RecyclerView

        LinearLayoutManager layoutManager = new LinearLayoutManager(this);   // 4. vertical arrangement
        rvNumbers.setLayoutManager(layoutManager);                          //    ← MANDATORY
        rvNumbers.addItemDecoration(
                new DividerItemDecoration(this, layoutManager.getOrientation()));  // 5. separator
        //                                ↑ Context   ↑ the orientation, as an int

        NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
        rvNumbers.setAdapter(adapter);                               // 6. the content
    }

    // The order of the three settings: setLayoutManager → addItemDecoration → setAdapter.
    // The order is not fatal between them, but setLayoutManager MUST come before
    // any layout. If you forget it, RecyclerView draws nothing, no matter how many
    // decorations and adapters you add.
    //
    // LinearLayoutManager(this) — the single-argument constructor means vertical.
    // The full variant: LinearLayoutManager(context, orientation, reverseLayout).
    // Here orientation would be RecyclerView.VERTICAL (1), and reverseLayout false.
    //
    // layoutManager.getOrientation() — returns RecyclerView.VERTICAL, that is 1.
    // DividerItemDecoration expects its own constant, DividerItemDecoration.VERTICAL,
    // which is also 1. They are two constants different in meaning, but with the same values
    // (0 = horizontal, 1 = vertical in both classes), so the line works.
    //
    // DANGER! The compiler cannot check it: both are int. If you switched the
    // LayoutManager to horizontal, getOrientation() would return 0, which is also
    // DividerItemDecoration.HORIZONTAL — so the code stays correct. The match is real,
    // not accidental, but it relies on numeric values, not on a common type.
    //
    // addItemDecoration before setAdapter — the order between them does not matter.
    // The decoration is applied at drawing time, not when the data is set.
    //
    // Why rvNumbers is declared RecyclerView and not View: because you need
    // setLayoutManager, addItemDecoration and setAdapter — all methods of the class.
    // findViewById is generic, so it infers the type from the variable.
    //
    // Why notifyDataSetChanged() is not called: the data is fixed, and setAdapter
    // triggers the first layout by itself. notifyDataSetChanged() would be redundant and
    // would cause a pointless refill.

    // ==================================================================================
    // WHAT THE LAYOUTMANAGER DOES ON EVERY FRAME
    // ==================================================================================
    //
    //   RecyclerView.onLayout()
    //     └─ LayoutManager.onLayoutChildren(recycler, state)
    //          ├─ computes how many children fit in the available space
    //          ├─ asks the pool for holders for the visible positions
    //          ├─ calls adapter.onBindViewHolder(holder, position) for each one
    //          ├─ measures and positions each row (layoutDecorated)
    //          └─ throws the holders that left the screen into the pool
    //
    // GridLayoutManager — new GridLayoutManager(this, 2) arranges in two columns.
    // The adapter stays unchanged, item_number.xml stays unchanged.
    //
    // StaggeredGridLayoutManager — columns with different heights, like a Pinterest.
    // Likewise, with no changes in the adapter.
    //
    // setReverseLayout(true) — the list grows from the bottom up, like a chat. Also from the
    // LayoutManager.
    //
    // ==================================================================================
    // WHAT HAPPENS WITHOUT setLayoutManager
    // ==================================================================================
    //
    //   Nothing. And that is exactly the problem.
    //
    //   RecyclerView without a LayoutManager
    //     ├─ setAdapter(adapter)        → success, no exception
    //     ├─ addItemDecoration(...)     → success, no exception
    //     ├─ onMeasure()                → measures 0 × 0
    //     ├─ onLayout()                 → Log.e: "No layout manager attached; skipping layout"
    //     └─ the screen                 → empty
    //
    //   The exact message from Logcat:
    //     E/RecyclerView: No layout manager attached; skipping layout
    //
    //   Why it does not throw an exception: because RecyclerView is designed to work even
    //   without content. An empty RecyclerView is a valid state (for example before the
    //   data is loaded). The framework cannot know whether you forgot to set the manager
    //   or whether you intentionally have no data yet.
    //
    //   Why it is the ugliest error in the chapter: it compiles, it runs, it does not crash, but
    //   the screen is empty. All the other mistakes in the chapter show up immediately; this one
    //   shows up only if you know to look in Logcat.
    //
    //   The diagnostic order for an empty RecyclerView:
    //     1) do you have setLayoutManager?
    //     2) do you have setAdapter?
    //     3) does getItemCount() return more than 0?
    //     4) does the layout root have a non-zero height?
    //   In 90% of cases, the answer is to the first question.

    // ==================================================================================
    // THE SEPARATION DIAGRAM: CONTENT vs ARRANGEMENT
    // ==================================================================================
    //
    // ┌─────────────────────────────────────────────────────────────────────────────────┐
    // │              WHAT IS DISPLAYED      vs.        HOW IT IS ARRANGED              │
    // │                                                                                 │
    // │   ADAPTER (content)                      LAYOUTMANAGER (arrangement)            │
    // │   ├── getItemCount() → 100                ├── how many rows fit                 │
    // │   ├── onCreateViewHolder → the row        ├── where each row sits               │
    // │   ├── onBindViewHolder → the text         ├── how tall each one is              │
    // │   └── getItemViewType → the type          ├── how the scroll is computed         │
    // │                                           └── which holder is reused            │
    // │                                                                                 │
    // │   It does not know:                       It does not know:                     │
    // │   ├── how many rows fit                   ├── what is in a row                  │
    // │   ├── where the row sits                  ├── what data exists                   │
    // │   └── how it scrolls                      └── how many elements there are        │
    // │                                                                                 │
    // │   ─────────────────────────────────────────────────────────────────────────     │
    // │                                                                                 │
    // │   THE SAME DATA + THE SAME ADAPTER:                                             │
    // │                                                                                 │
    // │   LinearLayoutManager      GridLayoutManager(2)        StaggeredGrid(2)          │
    // │   ┌───┐                    ┌───┬───┐                   ┌───┬───┐                 │
    // │   │ 1 │                    │ 1 │ 2 │                   │ 1 │ 2 │                 │
    // │   ├───┤                    ├───┼───┤                   │   ├───┤                 │
    // │   │ 2 │                    │ 3 │ 4 │                   │ 3 │ 4 │                 │
    // │   ├───┤                    ├───┼───┤                   ├───┼───┤                 │
    // │   │ 3 │                    │ 5 │ 6 │                   │ 5 │ 6 │                 │
    // │   └───┘                    └───┴───┘                   └───┴───┘                 │
    // │                                                                                 │
    // │   zero changes in the adapter, zero changes in item_number.xml                  │
    // └─────────────────────────────────────────────────────────────────────────────────┘
    //
    // Why the separation matters at the exam: the question "what must we set on a
    // RecyclerView for it to display something" has the answer "adapter + LayoutManager". If
    // you answer only "adapter", you have lost half the marks — and, more importantly,
    // you have lost exactly the difference from ListView.
    //
    // What "content" and "arrangement" mean in practice: the content is what is seen in
    // each row (the decimal and the binary number). The arrangement is where each
    // row is seen (one under another, in two columns, reversed). They are two independent
    // questions, so two independent objects.

    // ==================================================================================
    // DIVIDERITEMDECORATION — THE SEPARATOR
    // ==================================================================================
    //
    // ListView has android:divider in the XML. RecyclerView has no such thing. The lines
    // between rows are drawn by an ItemDecoration, and DividerItemDecoration is the
    // ready-made decoration from the library.
    //
    // How it works, in three steps:
    //   1. RecyclerView draws the rows (through the LayoutManager)
    //   2. ItemDecoration.onDraw()      → draws UNDER the content (before the children)
    //   3. ItemDecoration.onDrawOver()  → draws OVER the content (after the children)
    //
    // DividerItemDecoration uses onDraw and draws a line at the bottom edge of
    // each row, except the last one.
    //
    // layoutManager.getOrientation() — tells the decoration whether the lines are horizontal
    // or vertical. For a vertical list, the separator is a horizontal line between the
    // rows. For a horizontal list, it would be a vertical line between the columns.
    //
    // What happens if you put the wrong orientation: the separator is drawn on the other
    // axis — that is vertical lines over the rows, or overlapping horizontal lines. It does
    // not crash, it just looks wrong. It is the kind of bug you see at first glance.
    //
    // Why it is not in the XML: because RecyclerView has no separator attributes of its own.
    // Everything related to drawing is done from code, through ItemDecoration. That is the
    // price of the separation: more code, more control.
    //
    // ==================================================================================
    // LISTVIEW vs RECYCLERVIEW — THE DIFFERENCES IN THIS FILE
    // ==================================================================================
    //
    //   ListView (steps 1 and 2)            RecyclerView (step 3)
    //   ├── internal, fixed arrangement     ├── explicit setLayoutManager(...)
    //   ├── android:divider in the theme    ├── addItemDecoration(...) in code
    //   ├── limited animations              ├── default ItemAnimator
    //   ├── adapter with getView            ├── adapter with 3 methods
    //   └── internal recycling              └── RecycledViewPool, also internal
    //
    // Three extra configuration lines, three extra capabilities. Nothing in this file
    // exists in steps 1 and 2 — and exactly that is the lesson of the chapter.
    //
    // ==================================================================================
    // WHAT HAPPENS IF YOU PUT THE DECORATION AFTER setAdapter
    // ==================================================================================
    //
    //   It works. addItemDecoration does not depend on the adapter; the decoration is applied
    //   at the drawing phase, which happens after the layout anyway. The recommended order
    //   (manager → decoration → adapter) is a reading convention, not a requirement.
    //
    // What IS a requirement: setLayoutManager before RecyclerView receives the first
    // layout. If you set it after the view has already been measured, RecyclerView calls
    // requestLayout() — that is why, in practice, you set it in onCreate, before
    // anything else.
    //
    // ==================================================================================
    // WHY `this` AS THE FIRST ARGUMENT TO LinearLayoutManager AND TO DividerItemDecoration
    // ==================================================================================
    //
    // Both need a Context:
    //   - LinearLayoutManager uses it for Resources (dimensions, density);
    //   - DividerItemDecoration uses it to obtain the separator drawable
    //     from the current theme.
    //
    // It is not the same Context as for the adapter: the adapter receives none, because it
    // takes it from `parent` in onCreateViewHolder. Here, in onCreate, you do not yet have a
    // `parent`, so `this` is the only source.
}
```

**What you must remember from this file:** a working `RecyclerView` needs **adapter + LayoutManager**. The rest (`ItemDecoration`, `ItemAnimator`) are optional. And if you forget `setLayoutManager`, you get no exception — just an empty screen and one line in Logcat.

**Why `ListView` could not be decomposed:** because the arrangement was in `AbsListView.layoutChildren`, and the separator in `android:divider`. Both were private. `RecyclerView` was written from scratch to expose these points as swappable objects.

---

## 28.12 `activity_recycler_view.xml` — header + `RecyclerView`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FILE: activity_recycler_view.xml
     ==================================================================================
     LOCATION: DMA06/src/main/res/layout/activity_recycler_view.xml
     ROLE:     the step 3 layout: THE SAME header, THE SAME structure as step 2,
               only the widget differs.
     CONTAINS: 1 × include (layout_number_header), 1 × RecyclerView
     IDS:      rvNumbers
     ================================================================================== -->

<!-- The same structure as in step 2: fixed header at the top, list below.
     The difference between the two files is exactly one tag. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- The same header, from the same file -->
    <include layout="@layout/layout_number_header" />

    <!-- The full name: RecyclerView is not in android.widget, but in the AndroidX library.
         The XML has no imports, so the full name is the only way to refer to a class
         from another package. The same happens with MaterialButton. -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>

<!-- ======================================================================================
     ATTRIBUTES THAT RECYCLERVIEW HAS AND THE FILE DOES NOT USE
     ======================================================================================
     android:clipToPadding="false"        the rows are drawn under the padding too
     android:scrollbars="vertical"        the scroll bar, if you want it explicit
     android:overScrollMode="never"       no "elastic" effect at the edges
     app:layoutManager="androidx.recyclerview.widget.LinearLayoutManager"
                                          the arrangement straight from the XML, without code
     app:spanCount="2"                    the number of columns for GridLayoutManager
     tools:listitem="@layout/item_number" only in the preview, not at runtime
     ======================================================================================
     `app:layoutManager` is the only one that can really replace a line of code. But it
     creates the manager with the no-argument constructor, so you cannot configure
     the orientation or reverseLayout. In practice, it is set from code.
     ====================================================================================== -->

<!-- ======================================================================================
     WHAT TO REMEMBER FROM THE FILE
     ======================================================================================
     full name               androidx.recyclerview.widget.RecyclerView
     rvNumbers               prefix rv = RecyclerView, lv = ListView
     0dp + weight="1"        the same logic: the header wrap_content, the list takes the rest
     no android:divider      the separator comes from DividerItemDecoration, in code
     no direct dependency    RecyclerView arrives transitively through the Material library
     ====================================================================================== -->
```

**The full name is mandatory** — `RecyclerView` is not a class from `android.widget`, so the XML cannot shorten it. The same happens with any view from a library: `com.google.android.material.button.MaterialButton`, `androidx.recyclerview.widget.RecyclerView`.

**No explicit dependency in `build.gradle.kts`** — there is no `implementation(libs.recyclerview)` line. The class resolves because the Material library (`com.google.android.material:material`) brings `androidx.recyclerview` transitively. If you removed Material, the import would break.

**Why `rvNumbers` and not `lvNumbers`:** the id is different from the one in steps 1 and 2, although it could have been the same (different layouts). The difference is intentional: `rv` = `RecyclerView`, `lv` = `ListView`. When you read `findViewById(R.id.rvNumbers)`, you immediately know what widget type you are getting.

**What would happen if you put a `ListView` instead of a `RecyclerView`:** it would compile (if you also changed `findViewById`), but `setLayoutManager` would not exist on `ListView`. So you cannot swap one for the other without also changing the code. The layout is almost identical; the class is not.

---

## 28.13 `item_number.xml` — a single layout for two adapters

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FILE: item_number.xml
     ==================================================================================
     LOCATION: DMA06/src/main/res/layout/item_number.xml
     ROLE:     the two-column row. Used by NumberListAdapter AND by
               NumberRecyclerAdapter. It is the proof that the difference between steps is
               not in the layout, but in the adapter.
     CONTAINS: 1 × horizontal LinearLayout, 2 × TextView
     IDS:      tvDecimal, tvBinary   ← the contract of both adapters
     ================================================================================== -->

<!-- Why the header is the most important one in the chapter: because the file is used by
     TWO adapters. If you change an id here, you must change it in two Java
     files. If you change a padding, it changes in both steps. A shared layout
     is a shared contract. -->

<!-- One row with two columns. Steps 2 and 3 both use this layout. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="14dp">

    <!-- Column 1: the decimal number, aligned to the left.
         0dp + weight="1" = half the width. With wrap_content, each column would be
         as wide as its text, and the columns would no longer line up between rows. -->
    <TextView
        android:id="@+id/tvDecimal"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:textAppearance="?attr/textAppearanceBodyLarge" />

    <!-- Column 2: the binary number, aligned to the right, with a monospaced font.
         monospace = digits of the same width, so the binary numbers line up nicely.
         gravity="end" respects the reading direction (supportsRtl="true" in the manifest). -->
    <TextView
        android:id="@+id/tvBinary"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:fontFamily="monospace"
        android:gravity="end"
        android:textAppearance="?attr/textAppearanceBodyLarge" />
</LinearLayout>

<!-- ======================================================================================
     WHAT TO REMEMBER FROM THE FILE
     ======================================================================================
     match_parent × wrap_content      as wide as the list, as tall as the content
     paddingHorizontal 16dp           inner space; available since API 26, minSdk 33
     paddingVertical 14dp             more generous than the header (12dp)
     0dp + weight="1" on both         the equivalent of 50% / 50%
     fontFamily="monospace"           only on the binary column
     gravity="end"                    alignment that respects RTL
     no android:text                  the row is empty until the adapter fills it
     tvDecimal / tvBinary             the contract of both adapters
     ======================================================================================
     HOW A ROW IS MEASURED
     ======================================================================================
     Horizontal LinearLayout, two children with 0dp + weight 1:
       1. the parent receives the width of the list (match_parent)
       2. it subtracts the horizontal padding: 16dp + 16dp = 32dp
       3. it divides the rest by the sum of the weights: (L − 32) / 2 for each
       4. each TextView receives exactly half, no matter how much text it has
       5. the height: wrap_content → the taller of the two, plus padding 14dp × 2

     That is why the two columns line up perfectly between rows, although the texts have
     different lengths: the width does not depend on the content. With wrap_content it would
     depend, and the second column would "jump" on every row.
     ====================================================================================== -->
```

**The comment at the head of the file** — "Steps 2 and 3 both use this layout" — is the very core of the chapter. The same XML file serves the `ListView` of step 2 and the `RecyclerView` of step 3. The difference between the two **is not in the layout**, but in the adapter.

**`match_parent` × `wrap_content`** — the row is as wide as the list and as tall as the content. The `wrap_content` height adapts to a larger font; a fixed height would clip the text.

**`fontFamily="monospace"`** — the digits have the same width, so the binary numbers line up nicely on the right. It is a system font, not a file added to the project.

**No `android:text`** — the row is empty in the preview and gets filled at runtime. Without an adapter, you would see 100 empty rows.

**The two ids are the contract** — `tvDecimal` and `tvBinary` are looked up by **both** adapters. If you rename them, they must be changed in two Java files.

### The same layout, two `inflate` calls

```
// NumberListAdapter.getView
convertView = layoutInflater.inflate(R.layout.item_number, parent, false);

// NumberRecyclerAdapter.onCreateViewHolder
View view = LayoutInflater.from(parent.getContext())
        .inflate(R.layout.item_number, parent, false);
```

The same file, the same parameters, the same `false`. The only thing that differs is the method around it: one receives a possibly recycled `convertView`, the other creates a new holder.

**What this means for the exam:** if you are asked to explain why `item_number.xml` is the same in both steps, the answer is "because the layout describes **the row**, not **the list**". The row is independent of who arranges it. `ListView` and `RecyclerView` differ in the way they produce and reuse rows, not in what is inside a row.

---

## 28.14 The final comparison, method by method

### The exact correspondence between the two adapters

| # | `NumberListAdapter` (ListView) | `NumberRecyclerAdapter` (RecyclerView) | When it runs |
|---|---|---|---|
| 1 | `public int getCount()` | `public int getItemCount()` | on every measurement of the list |
| 2 | `public Integer getItem(int position)` | — (`numbers.get(position)` is used directly) | on demand (`getItemAtPosition`), respectively at bind |
| 3 | `public long getItemId(int position)` | — (`getItemId` is optional, `NO_ID` by default) | on click |
| 4 | `public View getView(int position, View convertView, ViewGroup parent)` | `onCreateViewHolder(parent, viewType)` + `onBindViewHolder(holder, position)` | when needed |
| 5 | `if (convertView == null)` | the decision is made by `RecyclerView`: is the pool empty? | when needed |
| 6 | `layoutInflater.inflate(R.layout.item_number, parent, false)` | `LayoutInflater.from(parent.getContext()).inflate(...)` | once per created row |
| 7 | `holder = new ViewHolder()` | `new NumberViewHolder(view)` | once per created row |
| 8 | `holder.tvDecimal = convertView.findViewById(...)` | `tvDecimal = itemView.findViewById(...)` in the constructor | once per created row |
| 9 | `convertView.setTag(holder)` | `super(itemView)` + the internal bookkeeping of `RecyclerView` | once per created row |
| 10 | `holder = (ViewHolder) convertView.getTag()` | the holder arrives as a parameter in `onBindViewHolder` | on every display |
| 11 | `holder.tvDecimal.setText(...)` | `holder.tvDecimal.setText(...)` | on every display |
| 12 | `return convertView` | `void` — the holder is already at `RecyclerView` | on every display |

**How to read the table:** each row is a single responsibility, not a line of code. Rows 1–3 are the "bookkeeping" (how many, which, what id). Rows 4–9 are the "creation". Rows 10–12 are the "filling". The vertical division of the table is exactly the vertical division of the code.

**What has no counterpart:** `getItem` and `getItemId` have no mandatory equivalent in `RecyclerView.Adapter`. `getItem` disappears because `onBindViewHolder` receives the position directly and has the list in a field. `getItemId` exists, but it is optional and returns `NO_ID` by default.

### What disappears when moving to `RecyclerView`

| Gone | Replaced by |
|---|---|
| the `convertView` parameter | the internal pool of holders |
| `setTag(holder)` / `getTag()` | the generic type `RecyclerView.Adapter<...NumberViewHolder>` |
| the `(ViewHolder)` cast | the `holder` parameter, already typed |
| `if (convertView == null)` | the internal decision of `RecyclerView` |
| `return convertView` | `onBindViewHolder` returns `void` |
| the `layoutInflater` field | `LayoutInflater.from(parent.getContext())` |
| `getItem(position)` | `numbers.get(position)` directly |
| `Context` in the constructor | `parent.getContext()` on creation |

**Why `Context` disappears from the constructor:** because `onCreateViewHolder` receives `parent`, and `parent.getContext()` is exactly the context you need. One fewer parameter in the constructor means a class that is easier to test: you can build the adapter without an activity.

### What appears when moving to `RecyclerView`

| Added | Role |
|---|---|
| the generic parameter `RecyclerView.Adapter<...>` | the holder type, checked at compile time |
| `onCreateViewHolder` | creation, separate from filling |
| `onBindViewHolder` | filling, without creation |
| `getItemCount` | replaces `getCount` |
| `super(itemView)` | mandatory in the holder's constructor |
| `@NonNull` | contracts checked by lint |
| `viewType` | support for several row types |
| `LayoutManager` | the arrangement, separate from the content |
| `ItemDecoration` | the separators, separate from the layout |

### The three steps, on the same data

| | Step 1 | Step 2 | Step 3 |
|---|---|---|---|
| Widget | `ListView` | `ListView` | `RecyclerView` |
| Adapter | `ArrayAdapter<Integer>` | `NumberListAdapter` | `NumberRecyclerAdapter` |
| Base | — | `BaseAdapter` | `RecyclerView.Adapter` |
| Row layout | `android.R.layout.simple_list_item_1` | `item_number.xml` | `item_number.xml` |
| Columns per row | 1 | 2 | 2 |
| `ViewHolder` | hidden in the SDK | manual, `setTag`/`getTag` | mandatory, automatic |
| Row creation | in `ArrayAdapter` | in `getView`, the `null` branch | `onCreateViewHolder` |
| Row filling | in `ArrayAdapter` | in `getView`, after the `if` | `onBindViewHolder` |
| Arrangement | fixed vertical | fixed vertical | `LayoutManager` |
| Separator | `android:divider` from the theme | `android:divider` from the theme | `DividerItemDecoration` |
| Animations | no | no | yes, default |
| `notifyDataSetChanged` | yes | yes | yes (or `notifyItemChanged`) |

**The same line of data, three costs:** step 1 is the cheapest to write and the most limited. Step 2 is the most explicit and the most verbose. Step 3 is the most flexible and the most "ceremonious" at first sight — but all the ceremony is paid once, when writing, not at runtime.

### Short answers for the test

**"Why is `ArrayAdapter` not enough?"**
Because it knows a single `TextView` per row. For two columns you need a layout of your own and an adapter that fills it.

**"What does `convertView` do?"**
It receives the row that left the screen, so you can reuse it. Without it, 100 rows would be inflated for 100 elements.

**"Why is `ViewHolder` `static`?"**
So that it does not hold an implicit reference to the adapter. The holder is just a box with references to views; it does not need the outer instance.

**"Why was `getView` split?"**
Because it does two things with different costs: creation (expensive, rare) and filling (cheap, frequent). `RecyclerView` can call only the second.

**"Why is `LayoutManager` separate?"**
So that the arrangement is independent of the content. You switch the list to a grid without touching the adapter.

**"What happens without `setLayoutManager`?"**
`RecyclerView` displays nothing and gives no error. Only the message `No layout manager attached; skipping layout` in Logcat.

**"How many methods does `RecyclerView.Adapter` require?"**
Three: `onCreateViewHolder`, `onBindViewHolder`, `getItemCount`. It has no `getView`, because it neither receives nor returns `View`s, but `ViewHolder`s.

**"Why does `NumberData` have a private constructor?"**
Because all the methods are static and there is no state. The private constructor blocks `new NumberData()`, which would make no sense. It is the utility class pattern from the JDK.

---

## 28.15 The complete flow

### Startup

```
STARTUP
  MainActivity.onCreate
    ├── setContentView(activity_main)
    ├── openOnClick(btnStep1, SingleColumnActivity.class)
    ├── openOnClick(btnStep2, TwoColumnActivity.class)
    └── openOnClick(btnStep3, RecyclerViewActivity.class)
```

### Step 1 — `ListView` + `ArrayAdapter`

```
CLICK "Step 1: ListView"
  startActivity(new Intent(this, SingleColumnActivity.class))
    ↓
  SingleColumnActivity.onCreate
    ├── setContentView(activity_single_column)      ← the root is the ListView
    ├── findViewById(R.id.lvNumbers)
    ├── NumberData.getNumbers()                      → List<Integer> with 100 elements
    ├── new ArrayAdapter(this, simple_list_item_1, list)
    └── lvNumbers.setAdapter(adapter)
          ↓
  ListView asks getCount()                           → 100
  ListView asks for getView(0..9, null, listView)    → 10 rows inflated
  Scroll → getView(10, recycledRow, listView)        → only setText
```

### Step 2 — `ListView` + `NumberListAdapter`

```
CLICK "Step 2: Two columns"
  startActivity(new Intent(this, TwoColumnActivity.class))
    ↓
  TwoColumnActivity.onCreate
    ├── setContentView(activity_two_column)          ← includes the header + ListView
    ├── findViewById(R.id.lvNumbers)
    ├── new NumberListAdapter(this, NumberData.getNumbers())
    └── lvNumbers.setAdapter(adapter)
          ↓
  ListView asks getCount()                           → 100
  getView(0, null, parent)
    ├── inflate(item_number, parent, false)
    ├── new ViewHolder()
    ├── findViewById(tvDecimal) + findViewById(tvBinary)
    └── setTag(holder)
  getView(10, convertView, parent)
    ├── getTag() → holder
    └── setText × 2
```

### Step 3 — `RecyclerView`

```
CLICK "Step 3: RecyclerView"
  startActivity(new Intent(this, RecyclerViewActivity.class))
    ↓
  RecyclerViewActivity.onCreate
    ├── setContentView(activity_recycler_view)
    ├── findViewById(R.id.rvNumbers)
    ├── new LinearLayoutManager(this) → setLayoutManager
    ├── addItemDecoration(new DividerItemDecoration(...))
    ├── new NumberRecyclerAdapter(NumberData.getNumbers())
    └── setAdapter
          ↓
  RecyclerView asks getItemCount()                   → 100
  LayoutManager measures and decides how many holders fit
  onCreateViewHolder(parent, 0)
    ├── inflate(item_number, parent, false)
    └── new NumberViewHolder(view)
          ├── super(itemView)
          └── findViewById(tvDecimal) + findViewById(tvBinary)
  onBindViewHolder(holder, 0..9)                     → setText × 2
  Scroll → recycled holder → onBindViewHolder(holder, 10) → setText × 2
```

### The lifecycle of a row

| Moment | `ListView` | `RecyclerView` |
|---|---|---|
| the row appears for the first time | `getView(pos, null, parent)` → inflate + findViewById | `onCreateViewHolder` + `onBindViewHolder` |
| the row leaves the screen | the `View` enters the RecycleBin | the holder enters the RecycledViewPool |
| the row reappears | `getView(pos, convertView, parent)` → getTag + setText | `onBindViewHolder(holder, pos)` |
| the data changes | `notifyDataSetChanged()` → the whole screen refilled | `notifyItemChanged(pos)` → only that row |
| you tap a row | `OnItemClickListener` → `getItemAtPosition(position)` | a listener put on the view, in `onBindViewHolder` |

**The last row is a design difference, not an API difference:** `ListView` has a global listener on the list; `RecyclerView` has no `OnItemClickListener`. You put one on each row, in `onBindViewHolder`, usually on `holder.itemView`. There is no need here — no row is clickable.

### What does not change at all

- `NumberData` — the same source, the same 100 numbers.
- `item_number.xml` — the same row, the same two columns.
- `layout_number_header.xml` — the same header.
- The displayed text — "1 / 1", "2 / 10", …, "100 / 1100100".

Only **who** produces the rows and **how** they are arranged changes.

---

## 28.16 What to remember

- **Three steps, the same data.** `ArrayAdapter` → `BaseAdapter` with a manual `ViewHolder` → `RecyclerView.Adapter`. The difference is not in the layout, but in the adapter.
- **`convertView`** is the recycled row. `null` = a new row; non-`null` = reuse it.
- **`setTag` / `getTag`** glue the `ViewHolder` to the row. Without `setTag`, `getTag` returns `null` and the list crashes on the first scroll — with `NullPointerException: Attempt to read from field ... on a null object reference`.
- **`ViewHolder` is `static`** so that it holds no reference to the adapter. In `ListView` it is `private static`; in `RecyclerView` it is `static` (package-private), because it appears in the public signature.
- **`getView` was split** into `onCreateViewHolder` (creation, rare and expensive) and `onBindViewHolder` (filling, frequent and cheap).
- **`LayoutManager` is separate** so that the arrangement is independent of the content. Without it, `RecyclerView` is empty and silent.
- **`RecyclerView` has no global `OnItemClickListener`** and no `android:divider`. It replaces them with a per-row listener and `ItemDecoration`.
- **A lying `getItemCount()`** → `IndexOutOfBoundsException` in `onBindViewHolder`.
- **`inflate(layout, parent, false)`** — `parent` for `LayoutParams`, `false` so it does not attach now.
- **The `data` and `adapters` packages do not contain `dma06`** in the declaration, although the folders do. The imports use the declared package.
- **`NumberData.getNumbers()` returns a new list** on every call. Three screens, three independent lists.
- **`ArrayAdapter` calls `toString()`** on each element. It works for a single text; it stops at the second `TextView`.

---

## Chapter 28 summary

- `DMA06` = three steps on the same numbers 1–100: `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter`.
- `NumberData` is clean: `final`, `private` constructor, `static` method, zero `android.*` imports.
- Step 1: three lines of adapter, a single `TextView`, no recycling written by you.
- Step 2: `getView` with `if (convertView == null)`, `ViewHolder` + `setTag`/`getTag`, `findViewById` once per row.
- Step 3: `onCreateViewHolder` + `onBindViewHolder` + `getItemCount`, typed holder, no cast.
- `item_number.xml` is shared by steps 2 and 3 — the proof that the difference is in the adapter.
- `LayoutManager` and `ItemDecoration` are the pieces `ListView` kept inside (fixed arrangement, divider from XML), and `RecyclerView` brought them out.
- `activity_two_column.xml` and `activity_recycler_view.xml` are almost identical: only the widget differs.

**Back to** [chapter 12](12%20-%20DMA06%20-%20ListView%20vs%20RecyclerView.md) **or to the** [cheatsheet](21%20-%20Cheatsheet.md).







