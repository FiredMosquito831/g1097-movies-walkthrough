# Chapter 27 — The DMA05 code, annotated

**Goal:** to read DMA05 as a widget laboratory — every view in the XML, every listener in the code and every `ViewBinding` line, with the explanation next to them. There is no business logic: there is only UI, and everything you can learn from it is **the link between XML and code**.

**Source:** `DMA05/` at commit `d719ffc` — 29 files, of which 3 matter for the chapter: `MainActivity.java`, `activity_main.xml`, `AndroidManifest.xml`. The fourth file that matters indirectly is `build.gradle.kts`, because that is where `viewBinding` is turned on.

**What you learn from it:** `ViewBinding` (`ActivityMainBinding`), all the input widgets and their listeners, plus the full flow `XML → View tree → screen`.

**Estimated time:** 60–90 min (active reading, with the file open next to you).

> **How to read:** each file is a **single continuous piece**, in source order. The comments are woven into it, as in an annotated file you can read from top to bottom. Do not skip the theory blocks: they explain the decisions that appear immediately after them. For each portion, cover the comment and try to say yourself what the next line does. If you cannot, you have found what needs repeating.

**Legend:** the code in the blocks below is **identical to the files in the repo**. Everything that appears after `//` or between `/* */` (respectively between `<!-- -->` in XML) was added for explanation. Comments do not change behaviour, but in XML they **cannot sit on the same line as an attribute** — that is why there they sit on separate lines, above the element.

---

## 27.0 File map

```
DMA05/
├── build.gradle.kts                          ← viewBinding = true (starts the generator)
├── src/main/
│   ├── AndroidManifest.xml                   ← declares the activity, theme, soft input
│   ├── java/ro/ase/ie/dma05/
│   │   └── MainActivity.java                 ← 88 lines: inflate + 7 listeners
│   └── res/
│       ├── layout/activity_main.xml          ← 17 IDs, 14 direct children
│       ├── drawable/ic_android_black_24dp.xml    ← the vector in the ImageView
│       ├── drawable/ic_launcher_background.xml
│       ├── drawable/ic_launcher_foreground.xml
│       ├── mipmap-anydpi/ic_launcher.xml
│       ├── mipmap-anydpi/ic_launcher_round.xml
│       ├── mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher*.webp
│       ├── values/colors.xml                 ← black, white
│       ├── values/strings.xml                ← only app_name = "DMA05"
│       ├── values/themes.xml                 ← Theme.DMA05
│       ├── values-night/themes.xml           ← the night variant
│       └── xml/backup_rules.xml, data_extraction_rules.xml
├── src/test/java/ro/ase/ie/dma05/ExampleUnitTest.java
├── src/androidTest/java/ro/ase/ie/dma05/ExampleInstrumentedTest.java
└── src/main/keepRules/rules.keep
```

**29 files, 3 relevant.** The rest are the Android Studio template: icons, empty tests, backup rules. We do not read them.

**Why 3 and not 4:** `build.gradle.kts` is not read line by line, but the two lines that matter are:

```kotlin
android {
    namespace = "ro.ase.ie.dma05"          // the application package (replaces `package` in the manifest)
    buildFeatures { viewBinding = true }   // ← without this, ActivityMainBinding does not exist
}
```

**`namespace` and `viewBinding` are the only things in the build that show up in the Java code.** `namespace` explains why `import ro.ase.ie.dma05.databinding.ActivityMainBinding;` has exactly that prefix. `viewBinding = true` explains why the class exists. The rest of the file — SDKs, dependencies, versions — does not change a single line of `MainActivity`.

**`minSdk = 33`** — the app runs only on Android 13+. It matters for `EdgeToEdge`: there are no compatibility branches for old APIs, and `WindowInsetsCompat` has a native implementation on every targeted device.

---

## 27.1 `MainActivity.java` — the whole file, annotated

The file has 88 lines and does a single thing: builds the screen, puts it on the display and wires seven listeners. We read it as a single document, from top to bottom.

```java
/*
 * ======================================================================================
 * FILE: MainActivity.java
 * ======================================================================================
 * LOCATION: DMA05/src/main/java/ro/ase/ie/dma05/MainActivity.java
 * PACKAGE:  ro.ase.ie.dma05
 * ROLE:     the only activity of the application. It has no model, no data, no network.
 *           Builds the view tree from activity_main.xml and registers
 *           seven listeners, each with a Toast as its effect.
 *
 * FILE STRUCTURE (4 parts):
 *   1. imports                    — 15 lines, one of them generated
 *   2. the `binding` field        — 1 line
 *   3. onCreate                   — 64 lines, all the behaviour
 *   4. closing the class          — 2 lines
 *
 * WHAT YOU NEED TO KNOW BEFOREHAND:
 *   - `ActivityMainBinding` does NOT exist in the source. Gradle generates it at build.
 *   - `inflate` builds the tree; `setContentView` puts it on screen. Two steps.
 *   - Every `binding.<name>` is a field read, not a lookup in the tree.
 *   - Seven listeners, five interfaces, two styles (lambda / anonymous class).
 * ======================================================================================
 */

/*
 * ======================================================================================
 * THEORY BLOCK 1: VIEW BINDING
 * ======================================================================================
 *
 * 1. WHAT IT IS
 *    A Java class generated by the Android Gradle Plugin, one for each layout file
 *    in res/layout/. You do not write it, do not modify it, do not version it.
 *
 * 2. WHEN IT IS GENERATED
 *    At BUILD, not at runtime. AGP runs a generation task before compiling
 *    Java, writes the files into build/generated/... and puts them on the classpath.
 *    Consequence 1: if you add an android:id and do not run the build, the field does not exist.
 *    Consequence 2: the class does not appear in src/, so you will not find it by searching the project.
 *
 * 3. WHAT IT IS GENERATED FROM
 *    From res/layout/activity_main.xml. Each android:id="@+id/..." becomes a field
 *    public final with the type of the tag:
 *      <Button android:id="@+id/button">    ->  public final Button button;
 *      <SeekBar android:id="@+id/seekBar">  ->  public final SeekBar seekBar;
 *
 * 4. THE NAME RULE
 *    activity_main.xml  ->  ActivityMainBinding
 *    activity_item.xml  ->  ActivityItemBinding
 *    item_movie.xml     ->  ItemMovieBinding
 *    underscore + lowercase letter -> CamelCase; the Binding suffix is always added.
 *
 * 5. THE ACTIVATION CONDITION
 *    build.gradle.kts:
 *      android { buildFeatures { viewBinding = true } }
 *    Without it, the class is not generated and the import does not compile.
 *
 * 6. WHAT IT CONTAINS
 *    - one public final field per android:id
 *    - a private rootView field + the getRoot() method
 *    - two static inflate(...) methods
 *    - one static bind(View) method
 *
 * 7. WHAT IT DOES NOT DO
 *    - it is not DataBinding: no @{...} expressions in XML
 *    - it does not replace findViewById for IDs received at runtime
 *    - it does not generate fields for views without android:id
 *
 * THE GENERATION PIPELINE:
 *
 *   activity_main.xml
 *        │
 *        ├── aapt2 ──────────────▶ R.java (R.id.button, R.layout.activity_main)
 *        │
 *        └── AGP ViewBinding ────▶ ActivityMainBinding.java
 *                                      │
 *                                      ▼
 *                                  javac (compiles both)
 *                                      │
 *                                      ▼
 *                                  APK (the class is in the dex, like any class)
 */

/*
 * ======================================================================================
 * THEORY BLOCK 2: THE LIFECYCLE OF AN ACTIVITY
 * ======================================================================================
 *
 * 1. THE STATES, IN ORDER
 *    onCreate()   → the instance is built; here the layout is inflated and the listeners are wired
 *    onStart()    → the activity becomes visible, but not necessarily interactive
 *    onResume()   → the activity is in the foreground and receives input
 *    onPause()    → it loses focus; you save what is cheap, stop animations
 *    onStop()     → it is no longer visible; you release heavy resources
 *    onDestroy()  → the instance dies; here global listeners would be cancelled
 *    onRestart()  → after onStop, before onStart, when you come back into the activity
 *
 * 2. WHAT onCreate GUARANTEES
 *    - The Window already exists (created by ActivityThread before the call).
 *    - `setContentView` can be called after `super.onCreate`, without throwing.
 *    - `findViewById` returns null until after `setContentView`.
 *    - `savedInstanceState` is `null` on the first launch and a Bundle on recreation.
 *
 * 3. WHY `super.onCreate` COMES FIRST
 *    AppCompatActivity delegates the lifecycle to AppCompatDelegate. If you call
 *    `setContentView` before `super.onCreate`, the delegate does not yet have the `Context`
 *    and the theme, and the inflate throws. The rule is mechanical: super first, the rest after.
 *
 * 4. RECREATION ON ROTATION
 *    ROTATION → onPause → onStop → onSaveInstanceState → onDestroy
 *           → onCreate(savedInstanceState ≠ null) → onStart → onResume
 *    The instance is NEW. The `binding` field is reassigned. The listeners re-register.
 *    The state of widgets with `android:id` is restored automatically by the framework.
 *
 * 5. WHAT HAPPENS TO `binding` ON RECREATION
 *    The old binding stays attached to the old tree, which is destroyed. Both become
 *    eligible for garbage collection. There is no leak because you do not keep
 *    a static reference and you do not listen to anything global.
 *
 * THE STATE DIAGRAM:
 *
 *   STARTUP
 *     │
 *     ▼
 *   onCreate ──▶ onStart ──▶ onResume ──▶ [RUNNING]
 *                                            │
 *                                            ▼
 *                                         onPause
 *                                            │
 *                                            ▼
 *                                         onStop ──▶ onDestroy   (if it does not come back)
 *                                            │
 *                                            ▼
 *                                        onRestart ──▶ onStart ──▶ onResume
 */

/*
 * ======================================================================================
 * THEORY BLOCK 3: WINDOW INSETS AND EDGE-TO-EDGE
 * ======================================================================================
 *
 * 1. THE WINDOW HIERARCHY
 *    Activity
 *      └── Window (PhoneWindow)
 *            └── DecorView (FrameLayout)
 *                  ├── (optional) action bar
 *                  └── android.R.id.content (FrameLayout)
 *                        └── what you put there with setContentView
 *
 *    The system bars (status, navigation) are NOT children of the DecorView: they are separate
 *    windows, drawn by the system on top of it. That is why the content can end up
 *    "under" them when the window is edge-to-edge.
 *
 *    `setContentView(view)` does not put the view directly into the window: it adds it into
 *    `android.R.id.content`, a FrameLayout that fills all the remaining space.
 *
 * 2. WHAT INSETS ARE
 *    Four values (left, top, right, bottom), in pixels, that say how much of the screen
 *    edge is covered by something you must not cover with content:
 *      - statusBars()      → the top bar (clock, battery, notifications)
 *      - navigationBars()  → the bottom bar (buttons or gesture bar)
 *      - captionBar()      → the title bar in multi-window
 *      - ime()             → the keyboard
 *      - displayCutout()   → notch / hole in the screen
 *      - systemGestures()  → the system gesture areas
 *    `Type.systemBars()` = statusBars | navigationBars | captionBar.
 *
 * 3. EDGE-TO-EDGE
 *    By default, `decorFitsSystemWindows = true`: the system shrinks the window so that it
 *    fits between the bars. The content never reaches under the bar.
 *    `EdgeToEdge.enable(this)` sets `decorFitsSystemWindows = false`: the window
 *    stretches across the whole screen, and you receive the insets and decide what to do with them.
 *    Advantage: the content can draw under the bar (images, maps, video).
 *    Cost: you must apply the padding yourself, otherwise the first widget sits under the clock.
 *
 * 4. HOW THE INSETS TRAVEL
 *    System → DecorView → content → root → children
 *    Each view can:
 *      - ignore (return the received insets)
 *      - consume (return CONSUMED) → the dispatch stops
 *      - modify (return new insets) → the children receive the modified values
 *    The listener in DMA05 returns `insets`, so it consumes nothing.
 *
 * 5. WHY PADDING ON THE ROOT
 *    Padding on the root moves ALL the children into the safe area, with a single operation.
 *    Padding on a child moves only that child. And if the root has no padding,
 *    the first child sits under the status bar, no matter what padding the second one has.
 *
 * 6. WHAT `Type.systemBars()` DOES NOT COVER
 *    The keyboard. For IME you need `Type.ime()` and, usually, a second
 *    listener or a combination in the same listener. DMA05 does not do it, because
 *    all the fields are in the top half of the screen.
 *
 * THE DISPATCH DIAGRAM:
 *
 *   WindowInsets { systemBars: (0, 24, 0, 48), ime: (0, 0, 0, 0) }
 *        │
 *        ▼
 *   DecorView ──▶ content ──▶ LinearLayout (root)
 *                                  │  listener: setPadding(0, 24, 0, 48)
 *                                  │  return insets  ← does not consume
 *                                  ▼
 *                            Button, Switch, … receive the same insets,
 *                            but they have no listener, so they ignore them
 */

// ======================================================================================
// THE PACKAGE AND THE IMPORTS
// ======================================================================================
// The first line of any Java file: the package. Here it is not just organisation — it is also
// the source of the prefix for the generated class: `ro.ase.ie.dma05` + `.databinding`.
// ======================================================================================

package ro.ase.ie.dma05;                              // the module package; comes from `namespace` in build.gradle.kts

// --------------------------------------------------------------------------------------
// GROUP 1 — the classic Android API (android.*)
// Classes from the framework that exists on the device, not from bundled libraries.
// --------------------------------------------------------------------------------------

import android.os.Bundle;                             // onCreate's parameter: the state saved on rotation
import android.view.View;                             // the type of the parameter in onClick(View v) and of v in the insets lambda
import android.widget.RadioButton;                    // the type returned by group.findViewById(checkedId)
import android.widget.RadioGroup;                     // the type of the `group` parameter in OnCheckedChangeListener
import android.widget.SeekBar;                        // the interface with THREE methods — the only one that needs an anonymous class
import android.widget.Toast;                          // the feedback of all seven listeners

// --------------------------------------------------------------------------------------
// GROUP 2 — AndroidX (androidx.*)
// Libraries bundled into the APK, with the version pinned in build.gradle.kts.
// --------------------------------------------------------------------------------------

import androidx.activity.EdgeToEdge;                  // drawing under the system bars (activity-ktx 1.8+)
import androidx.annotation.NonNull;                   // a contract annotation, does not change the runtime
import androidx.appcompat.app.AppCompatActivity;      // the base class: Activity + AppCompat + delegate
import androidx.core.graphics.Insets;                 // the four padding values, in pixels
import androidx.core.view.ViewCompat;                 // registering the insets listener, compatible on any API
import androidx.core.view.WindowInsetsCompat;         // Type.systemBars() and the `insets` object

// --------------------------------------------------------------------------------------
// GROUP 3 — the GENERATED code (ro.ase.ie.dma05.databinding)
// This is the only import that has no corresponding file in src/.
// --------------------------------------------------------------------------------------

import ro.ase.ie.dma05.databinding.ActivityMainBinding;   // ← the class GENERATED at build from activity_main.xml

// --------------------------------------------------------------------------------------
// WHY Button, Switch, CheckBox, ToggleButton, RatingBar, EditText, ImageView ARE MISSING
// --------------------------------------------------------------------------------------
// The name of these types never appears in the file. You access them only as `binding.button`,
// `binding.switch1` etc. — the compiler knows the type from the generated field, you no longer write it.
// ViewBinding removes the imports too, not just findViewById.
//
// `View` is imported although you never instantiate one: it is the type of the parameter in onClick(View v)
// and of the `v` parameter in the insets lambda. `RadioButton` is imported because you
// declare it as the type of the local variable `selected`. `SeekBar` is imported because the name
// appears explicitly in `new SeekBar.OnSeekBarChangeListener()`.

// ======================================================================================
// THE CLASS AND THE FIELD
// ======================================================================================
// One class, one field. The field is the key to the whole file: it keeps the tree
// alive after onCreate finishes.
// ======================================================================================

public class MainActivity extends AppCompatActivity {   // AppCompatActivity = Activity + AppCompat + delegate

    ActivityMainBinding binding;                         // a field, not a local variable; null until inflate

    // ----------------------------------------------------------------------------------
    // WHY A FIELD AND NOT A LOCAL VARIABLE
    // ----------------------------------------------------------------------------------
    // In DMA05 a local would work too, because everything happens in onCreate. But the pattern
    // is a field because in any real application the binding is touched from onSaveInstanceState too,
    // and from helper methods, and from listeners. `ActivityMainBinding binding;` without
    // `private` is package-private — it works, but `private` would be the correct style.
    //
    // Before `inflate`, the field is `null`. It is not "empty", it is a null reference. Any
    // `binding.button` before the `inflate` line throws NullPointerException.
    //
    // Why it is not `static`: the binding belongs to the activity instance. On rotation,
    // onCreate runs again on a new instance and reassigns the field. A static field
    // would keep the old tree alive and would leak the memory of the destroyed activity.
    //
    // Why it is not `final`: because `inflate` is called in onCreate, not in the constructor.
    // ----------------------------------------------------------------------------------

    // ----------------------------------------------------------------------------------
    // THE METHOD: onCreate
    // ----------------------------------------------------------------------------------
    // WHEN IT IS CALLED: once per activity instance, after the Window
    //   has been created and before the tree is drawn.
    // WHAT IT RECEIVES: `savedInstanceState` — a Bundle with the state saved on rotation, or
    //   `null` on the first launch. In DMA05 it is never read: the state of the widgets
    //   is restored automatically, because they all have `android:id`.
    // WHAT IT MUST DO: call `super.onCreate` FIRST. Otherwise, the AppCompat delegate
    //   is not initialised and `setContentView` throws.
    // ----------------------------------------------------------------------------------
    @Override                                             // we override the method from AppCompatActivity
    protected void onCreate(Bundle savedInstanceState) {  // `protected`, as in the base class
        super.onCreate(savedInstanceState);               // 1. the parent's lifecycle — mandatory first

        // ------------------------------------------------------------------------------
        // STEP 2 — BUILDING THE TREE
        // ------------------------------------------------------------------------------
        // `ActivityMainBinding.inflate(...)` does THREE things, in a single expression:
        //   a. asks the LayoutInflater to parse res/layout/activity_main.xml
        //   b. creates the Java objects for each tag (LinearLayout, Button, …)
        //   c. walks the tree and fills the fields of the generated class, by `android:id`
        // The result is an ActivityMainBinding object that we keep in the field.
        //
        // getLayoutInflater() returns the activity's LayoutInflater, already bound to
        // its Context and its theme. That is why you do not write LayoutInflater.from(this) — it is
        // the same object, just obtained another way.
        //
        // The one-argument variant internally calls `inflate(inflater, null, false)`:
        // the tree is built completely, but stays UNATTACHED. It has no parent yet
        // and is not drawn. This lets `setContentView(binding.getRoot())` attach it
        // exactly once, in the right place. If `inflate` attached it itself,
        // `setContentView` would throw IllegalStateException: The specified child already
        // has a parent.
        // ------------------------------------------------------------------------------
        binding = ActivityMainBinding.inflate(getLayoutInflater());   // 2. XML → Java objects + filled fields

        /*
         * DIAGRAM 1 — how the tree is built and how the fields are filled:
         *
         * activity_main.xml (text)                          Java objects (heap)
         * ┌────────────────────────────────┐
         * │ <LinearLayout id="@+id/main">  │
         * │   ├─ <Button id="@+id/button"> │   LayoutInflater
         * │   ├─ <ImageView id="…">        │   ───────────────▶   creates one object
         * │   ├─ <Switch id="@+id/switch1">│                      per tag, with the attributes
         * │   ├─ <EditText id="…"> × 5     │                      read from XML
         * │   ├─ <CheckBox id="…">         │
         * │   ├─ <RadioGroup id="…">       │
         * │   │    ├─ <RadioButton id="…"> │
         * │   │    └─ <RadioButton id="…"> │
         * │   ├─ <ToggleButton id="…">     │
         * │   ├─ <ProgressBar id="…">      │
         * │   ├─ <SeekBar id="…">          │
         * │   └─ <RatingBar id="…">        │
         * └────────────────────────────────┘
         *                                              ┌──────────────────────────────────┐
         *                                              │ LinearLayout        (id = main)  │
         *                                              │   ├─ Button         (id = button)│
         *                                              │   ├─ ImageView                   │
         *                                              │   ├─ Switch         (id = switch1)│
         *                                              │   ├─ EditText × 5                │
         *                                              │   ├─ CheckBox                    │
         *                                              │   ├─ RadioGroup                  │
         *                                              │   │    ├─ RadioButton            │
         *                                              │   │    └─ RadioButton            │
         *                                              │   ├─ ToggleButton                │
         *                                              │   ├─ ProgressBar                 │
         *                                              │   ├─ SeekBar                     │
         *                                              │   └─ RatingBar                   │
         *                                              └────────────────┬─────────────────┘
         *                                                               │
         *                                             bind(root) walks the tree
         *                                             and, for each android:id,
         *                                             writes the reference into the matching field
         *                                                               │
         *                                              ┌────────────────▼─────────────────┐
         *                                              │ ActivityMainBinding              │
         *                                              │   rootView : LinearLayout        │
         *                                              │   main     : LinearLayout ───────┼──▶ the same object
         *                                              │   button   : Button ─────────────┼──▶ the same object
         *                                              │   switch1  : Switch ─────────────┼──▶ the same object
         *                                              │   … 17 fields                    │
         *                                              └──────────────────────────────────┘
         *
         * DIAGRAM 2 — how `binding.button` resolves to the view with id="button":
         *
         * XML:   android:id="@+id/button"
         *               │
         *               ├──────────────────────────────┬─────────────────────────────────────┐
         *               │ aapt2 (BUILD)                │ AGP ViewBinding (BUILD)             │
         *               ▼                              ▼                                     │
         *       R.id.button = 0x7f0800a3       public final Button button;                 │
         *       (illustrative int, stable in APK) (a field in the generated class)         │
         *               │                              │                                     │
         *               └──────────────┬───────────────┘                                     │
         *                              ▼                                                     │
         *               bind(root) at inflate:                                               │
         *                 button = ViewBindings.findChildViewById(root, R.id.button)         │
         *                 if (button == null) throw NullPointerException("Missing …")        │
         *                              │                                                     │
         *                              ▼                                                     │
         *               binding.button ───────────────────────────────────────────────────────┘
         *                 = getfield, O(1), with no lookup in the tree
         */

        // ------------------------------------------------------------------------------
        // STEP 3 — EDGE-TO-EDGE AND ATTACHMENT
        // ------------------------------------------------------------------------------
        // The order matters: first edge-to-edge, then the attachment, then the insets listener.
        //
        // EdgeToEdge.enable(this) sets decorFitsSystemWindows = false, makes the system
        // bars transparent and applies scrims (SystemBarStyle.auto) for contrast.
        // The result: the content is drawn under the bar, and you are responsible for
        // pushing it into the safe area — exactly what the listener below does.
        //
        // setContentView(binding.getRoot()) replaces setContentView(R.layout.activity_main).
        // getRoot() returns the root LinearLayout — exactly the view that has
        // android:id="@+id/main" in the XML.
        //
        // PITFALL NO. 1: if you also leave setContentView(R.layout.activity_main) after the
        // binding line, Android builds A SECOND TREE, completely separate. The second one
        // ends up on screen; `binding` points to the first. The seven listeners get
        // attached to views that nobody sees, and the app seems "dead" —
        // no Toast ever appears. It happens often when migrating from findViewById.
        // ------------------------------------------------------------------------------
        EdgeToEdge.enable(this);                      // 3. the window stretches UNDER the system bars
        setContentView(binding.getRoot());            // 4. the built tree reaches the screen

        /*
         * DIAGRAM 3 — the two-step flow, inflate vs setContentView:
         *
         * STEP 1 — BUILDING                            STEP 2 — ATTACHING
         * binding = ActivityMainBinding                 setContentView(binding.getRoot())
         *           .inflate(getLayoutInflater())
         *         │                                             │
         *         ▼                                             ▼
         *   activity_main.xml                            DecorView (the window)
         *         │                                             │
         *         ▼                                             ├─ android.R.id.content (FrameLayout)
         *   View tree                                           │     │
         *   (unattached, invisible,                             │     ▼
         *    no parent)                                         │  LinearLayout (root)
         *         │                                             │     ├─ Button
         *         ▼                                             │     ├─ ImageView
         *   ActivityMainBinding                                 │     └─ … the children
         *   (fields filled)                                     │
         *                                                       ▼
         *                                              the tree is on screen,
         *                                              ready for measure/layout
         *
         * Between the two lines: the tree exists in the heap, with all the attributes read,
         * but it has no parent and is not drawn. A findViewById on the activity would return
         * null, and binding.button.getWidth() would return 0.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: View.OnApplyWindowInsetsListener
        // ------------------------------------------------------------------------------
        // WHAT IT OBSERVES: the window insets — how much of the screen edge is
        //   covered by the system bars (status, navigation, caption).
        // WHEN IT FIRES: on every insets dispatch, that is on the first layout pass,
        //   on rotation, on window resize, when the keyboard opens
        //   (if you asked for Type.ime()) and when entering/leaving multi-window.
        // STYLE: lambda — the interface has A SINGLE method: onApplyWindowInsets(View, WindowInsetsCompat).
        // PARAMETERS: `v` = the view the listener is registered on (the root);
        //             `insets` = WindowInsetsCompat, the object with all the insets types.
        // RETURN: the insets that travel on to the children. `return insets` = do not consume.
        // ------------------------------------------------------------------------------
        ViewCompat.setOnApplyWindowInsetsListener(binding.getRoot(), (v, insets) -> {
            // a. pull out the four dimensions of the system bars, in pixels
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            // b. apply them as padding on the ROOT: all the children move into the safe area
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            // c. let the insets travel on, to the children
            return insets;
        });

        /*
         * DIAGRAM 4 — padding on the root vs padding on a child:
         *
         * THE CORRECT VARIANT: padding on the root
         * ┌───────────────────────────────────────────────┐
         * │ ███ status bar ███████████████████████████████ │  ← drawn OVER the content
         * │ ┌───────────────────────────────────────────┐ │
         * │ │ LinearLayout (root)                       │ │
         * │ │   paddingTop    = systemBars.top          │ │
         * │ │   paddingBottom = systemBars.bottom       │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Button                              │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Switch                              │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ … all the children, pushed together │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ └───────────────────────────────────────────┘ │
         * │ ███ navigation bar ██████████████████████████ │
         * └───────────────────────────────────────────────┘
         *
         * THE WRONG VARIANT: padding on a child
         * ┌───────────────────────────────────────────────┐
         * │ ███ status bar ███████████████████████████████ │
         * │ ┌───────────────────────────────────────────┐ │
         * │ │ LinearLayout (root) — no padding          │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Button  ← only it is pushed down    │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Switch  ← stays under the bar       │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ RatingBar ← stays under the bar     │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ └───────────────────────────────────────────┘ │
         * │ ███ navigation bar ██████████████████████████ │
         * └───────────────────────────────────────────────┘
         *
         * WHAT EACH LINE OF THE LAMBDA DOES:
         *   insets.getInsets(Type.systemBars())  → the 4 dimensions (status + navigation + caption)
         *   v.setPadding(left, top, right, bottom) → applies them as padding on the root
         *   return insets                        → lets the insets travel to the children
         *
         * return insets, not CONSUMED: if you returned CONSUMED, the dispatch would stop
         * at the root and no child would receive the insets any more. Here it does not matter,
         * because no child asks for them, but it is the general rule.
         *
         * PITFALL NO. 2: setPadding OVERWRITES the padding from the XML, it does not add to it.
         * The root in DMA05 has no android:padding, so nothing is lost. If it
         * had 16dp, the correct form would be v.setPadding(16dp + left, 16dp + top, ...).
         *
         * What Type.systemBars() does not cover: the keyboard. When an EditText opens,
         * the IME is not compensated — you would need Type.ime() in a second listener or
         * in the same one. In DMA05 the fields are at the top, so it is not visible.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: View.OnClickListener
        // ------------------------------------------------------------------------------
        // WHAT IT OBSERVES: a click — that is a down + up inside the bounds of the view,
        //   without the finger having left the view in between.
        // WHEN IT FIRES: on up, if the view is clickable and not disabled.
        //   It also fires on performClick() from code.
        // STYLE: anonymous class — the interface has a single method, so a lambda would have worked.
        //   The choice is didactic: see the lambda equivalent below.
        // ------------------------------------------------------------------------------
        binding.button.setOnClickListener(new View.OnClickListener() {
            // --------------------------------------------------------------------------
            // THE METHOD: onClick
            // --------------------------------------------------------------------------
            // `v` is the view that received the click — here, the same binding.button.
            // The parameter exists because the same listener instance can be
            // registered on several views; then `v` says which one was touched.
            // --------------------------------------------------------------------------
            @Override                                     // we override the method from the interface
            public void onClick(View v) {                 // `View`, not `Button`: the interface is declared on View
                Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show();
            }
        });

        // ------------------------------------------------------------------------------
        // WHY MainActivity.this AND NOT this
        // ------------------------------------------------------------------------------
        // Inside the anonymous class, `this` is the listener object, not the activity.
        // And Toast.makeText asks for a Context. MainActivity.this is the syntax by which you step
        // out of the anonymous class and reach the outer instance. In a lambda, `this`
        // refers to the instance that surrounds the lambda — that is, MainActivity — so
        // MainActivity.this would be redundant, but legal.
        //
        // The lambda equivalent of the whole block (it does NOT exist in the real file):
        //   binding.button.setOnClickListener(v ->
        //           Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show());
        //
        // THE ANATOMY OF Toast.makeText(...).show():
        //   Toast.makeText(...)   → static factory: builds the object, does not display it
        //   MainActivity.this     → the Context: where the resources and the package come from
        //   "Button clicked"      → the text, a CharSequence
        //   Toast.LENGTH_SHORT    → the duration: ~2 seconds (LENGTH_LONG ≈ 3.5 s)
        //   .show()               → attaches the Toast to the display queue
        //
        // .show() IS MANDATORY: without it you build the Toast object and throw it away — nothing
        // appears on screen. You get no exception, no compiler warning,
        // no runtime error. The line
        //   Toast.makeText(this, "x", Toast.LENGTH_SHORT);
        // is perfectly valid syntactically and completely useless. It is the most frequent
        // "invisible" mistake in Android: the code runs, the app does not crash, the feedback is missing.
        //
        // What happens behind the scenes, when you call .show():
        //   Toast.makeText(context, text, duration)
        //      ├── creates a Toast object (not yet visible)
        //      └── .show()
        //            ├── asks the system notification service to display it
        //            ├── the system puts it in a global QUEUE (one Toast at a time)
        //            ├── the Toast window appears above the app, without blocking input
        //            └── after the duration it disappears by itself — you do not have to close it
        //
        // Why Toast and not a TextView: the Toast does not need a parent in the layout.
        // It appears in a separate window (WindowManager, TYPE_TOAST), above the
        // app, and disappears by itself. Ten Toasts fired quickly are displayed
        // sequentially, one after another, each ~2 seconds — that is why one Toast per
        // SeekBar step produces a queue of tens of seconds.
        // ------------------------------------------------------------------------------

        // ------------------------------------------------------------------------------
        // LISTENER: CompoundButton.OnCheckedChangeListener (on Switch)
        // ------------------------------------------------------------------------------
        // WHAT IT OBSERVES: the `checked` state of a CompoundButton — on / off.
        // WHEN IT FIRES: on touch AND on setChecked(...) from code.
        // STYLE: lambda — the interface has a single method:
        //   onCheckedChanged(CompoundButton buttonView, boolean isChecked)
        // ------------------------------------------------------------------------------
        binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
            // `buttonView` = the widget that produced the change; here it is ignored.
            // `isChecked`  = the NEW state, not the old one.
            Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        // ------------------------------------------------------------------------------
        // LISTENER: CompoundButton.OnCheckedChangeListener (on CheckBox)
        // ------------------------------------------------------------------------------
        // The same interface, another widget. The lambda signature is identical because
        // CheckBox also extends CompoundButton.
        // ------------------------------------------------------------------------------
        binding.checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "CheckBox clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        /*
         * WHY THE SAME INTERFACE FOR TWO DIFFERENT WIDGETS
         *
         * Switch and CheckBox both extend CompoundButton, which declares
         * setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener). That is why
         * the lambda signature is identical: (CompoundButton buttonView, boolean isChecked).
         * It is not the widget type that decides the listener, but the BASE CLASS.
         *
         * THE HIERARCHY:
         *   View
         *    └── TextView
         *         └── Button
         *              └── CompoundButton          ← declares OnCheckedChangeListener
         *                   ├── CheckBox
         *                   ├── RadioButton
         *                   ├── Switch
         *                   └── ToggleButton
         *
         * "Switch clicked to " + isChecked → the concatenation calls String.valueOf(boolean),
         * so the text is ...true or ...false. You do not need an `if`.
         *
         * The listener also fires on changes from code: a setChecked(true) would
         * also produce a Toast. The practical consequence: if in an onCreate you restore
         * the state with setChecked(...), the listener registered BEFORE the restore will
         * produce side effects.
         *
         * Why Switch and not SwitchCompat: the layout uses <Switch>, the class from
         * android.widget. SwitchCompat would be androidx.appcompat.widget.SwitchCompat.
         * Both extend CompoundButton, so the listener is the same.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: SeekBar.OnSeekBarChangeListener
        // ------------------------------------------------------------------------------
        // WHAT IT OBSERVES: three different moments of the interaction with the bar:
        //   1. the start of the touch
        //   2. each value change
        //   3. the end of the touch
        // WHEN IT FIRES: at each of the three moments; onProgressChanged
        //   also fires on setProgress(...) from code, with fromUser = false.
        // STYLE: anonymous class — THREE abstract methods, so the interface is NOT functional.
        // ------------------------------------------------------------------------------
        binding.seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            // --------------------------------------------------------------------------
            // METHOD 1: onProgressChanged — the value changed
            // --------------------------------------------------------------------------
            // `seekBar`  = the bar that produced the event
            // `progress` = the NEW value, between 0 and android:max (100 by default)
            // `fromUser` = true if the change comes from the finger, false if it comes from code
            // --------------------------------------------------------------------------
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                Toast.makeText(MainActivity.this, "Progress changed to " + progress, Toast.LENGTH_SHORT).show();
            }

            // --------------------------------------------------------------------------
            // METHOD 2: onStartTrackingTouch — the finger touched the bar
            // --------------------------------------------------------------------------
            // It is called ONCE, at the start of the drag, before the first
            // value change. Empty body: there is nothing to do at the start.
            // --------------------------------------------------------------------------
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            // --------------------------------------------------------------------------
            // METHOD 3: onStopTrackingTouch — the finger was lifted
            // --------------------------------------------------------------------------
            // It is called ONCE, at the end of the drag. This is where you would save
            // the final value into a database or into a ViewModel — not at every
            // step. Empty body: DMA05 saves nothing.
            // --------------------------------------------------------------------------
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });

        /*
         * WHY A LAMBDA DOES NOT WORK HERE
         *
         * SeekBar.OnSeekBarChangeListener has THREE abstract methods. A functional
         * interface has exactly one. With three, you are forced into an anonymous class that
         * implements them all. The compiler has no way to guess what to put in
         * the other two methods.
         *
         * THE THREE MOMENTS:
         *   onProgressChanged     → on every value change
         *   onStartTrackingTouch  → when the finger touches the bar
         *   onStopTrackingTouch   → when the finger is lifted
         *
         * Why three and not one: "the value changed" is not the same thing as
         * "the user is interacting". onProgressChanged can come from code
         * (setProgress), from an animation or from the finger. The other two isolate the gesture.
         *
         * `fromUser` is true when the change comes from the user and false when it comes
         * from setProgress(...). Here it is ignored — the Toast appears in both cases.
         * The correct form would be `if (fromUser) { ... }`.
         *
         * Empty bodies are legal and mandatory. You must implement all
         * three methods; if you have nothing to do in one, you leave it empty. If you forget one,
         * the file does not compile: the anonymous class would be abstract.
         *
         * progress goes from 0 to android:max. In the XML there is no android:max, so
         * the default value is 100. Without android:progress, the initial value is 0.
         *
         * THE DIDACTIC DEFECT: one Toast per step means tens of Toasts for a single
         * drag, put in a queue. In ItemActivity (G1097) the same listener writes
         * into a TextView — the correct behaviour.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: RadioGroup.OnCheckedChangeListener
        // ------------------------------------------------------------------------------
        // WHAT IT OBSERVES: the selection of the group — which RadioButton is checked.
        // WHEN IT FIRES: when a child becomes checked, either on touch or on
        //   check(...) from code. It also fires with checkedId = -1 after clearCheck().
        // STYLE: anonymous class — the interface has a single method, so a lambda would have worked.
        //   Again, a didactic choice: the repo alternates the styles.
        // ------------------------------------------------------------------------------
        binding.radioGroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {

            // --------------------------------------------------------------------------
            // THE METHOD: onCheckedChanged
            // --------------------------------------------------------------------------
            // `group`     = the group that produced the event
            // `checkedId` = the RESOURCE ID of the checked button (R.id.radioButton1 or
            //               R.id.radioButton2), NOT its index (0 / 1) and NOT the object.
            //               It can be -1 if nothing is checked.
            // --------------------------------------------------------------------------
            @Override
            public void onCheckedChanged(@NonNull RadioGroup group, int checkedId) {
                // turns the ID received at runtime into the RadioButton object
                RadioButton selected = group.findViewById(checkedId);
                Toast.makeText(MainActivity.this, "Radio button clicked " + selected.getText(), Toast.LENGTH_SHORT).show();
            }
        });

        /*
         * checkedId IS A RESOURCE ID, NOT AN INDEX AND NOT THE OBJECT
         *
         * The value is R.id.radioButton1 or R.id.radioButton2 — an int generated by aapt2,
         * stable in the APK. The confusion "it is the position" is frequent and leads to findViewById(0),
         * which returns null.
         *
         * Why group.findViewById(checkedId) and not findViewById(checkedId): the lookup
         * is done in the group's subtree. Here the variant on the activity would also work,
         * because the IDs are unique in the layout — but the form with `group` is the conceptually
         * correct one: you look in the container that knows about the buttons.
         *
         * This is the only findViewById that survives with ViewBinding. The binding
         * gives you binding.radioButton1 and binding.radioButton2, but it has no way to
         * turn an int received at runtime into a field. The alternative:
         *   RadioButton selected = checkedId == R.id.radioButton1
         *           ? binding.radioButton1
         *           : binding.radioButton2;
         *
         * Why RadioGroup.OnCheckedChangeListener has a single method, yet still an anonymous
         * class: again, alternating style. A lambda would be perfectly valid.
         *
         * WATCH THE METHOD NAME: both CompoundButton and RadioGroup have
         * setOnCheckedChangeListener, but with different interfaces. It is neither an override
         * nor an overload: they are two methods declared in two classes with no inheritance
         * relationship (RadioGroup extends LinearLayout, not CompoundButton). The choice is made by
         * the type of the receiver.
         *
         * @NonNull comes from androidx.annotation. It does not change the runtime behaviour —
         * it is a contract for lint and for the reader: "the group is never null".
         *
         * PITFALL NO. 3: if checkedId were -1 (it happens after clearCheck()),
         * findViewById(-1) returns null and selected.getText() throws NPE. In DMA05
         * clearCheck() is never called, so it does not happen. In G1097, the first button has
         * android:checked="true" precisely so that "none selected" never exists.
         *
         * Why selected.getText() and not selected: RadioButton is a View; concatenating
         * a View would call toString(), which returns the class name plus hash.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: CompoundButton.OnCheckedChangeListener (on ToggleButton)
        // ------------------------------------------------------------------------------
        // The third widget with the same interface. The proof that the listener comes from
        // the base class, not from the concrete type of the widget.
        // ------------------------------------------------------------------------------
        binding.toggleButton.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "Toggle button clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        // ------------------------------------------------------------------------------
        // LISTENER: RatingBar.OnRatingBarChangeListener
        // ------------------------------------------------------------------------------
        // WHAT IT OBSERVES: the value of the stars — a `float`, not an `int`.
        // WHEN IT FIRES: on touch AND on setRating(...) from code.
        // STYLE: lambda — the interface has a single method:
        //   onRatingChanged(RatingBar ratingBar, float rating, boolean fromUser)
        // ------------------------------------------------------------------------------
        binding.ratingBar.setOnRatingBarChangeListener((ratingBar, rating, fromUser) -> {
            // `rating` is a float because android:stepSize="0.5" → 0.0, 0.5, 1.0, …
            // `fromUser` has the same meaning as in SeekBar.
            Toast.makeText(MainActivity.this, "Rating changed to " + rating, Toast.LENGTH_SHORT).show();
        });


    }                                                     // end of onCreate
}                                                         // end of the MainActivity class

/*
 * ======================================================================================
 * THE LISTENER FAMILIES — THE RULE THAT DECIDES THE STYLE
 * ======================================================================================
 *
 *                 does the interface have a single abstract method?
 *                               │
 *               ┌───────────────┴────────────────┐
 *              YES                               NO
 *               │                                 │
 *               ▼                                 ▼
 *       LAMBDA ALLOWED                  ANONYMOUS CLASS REQUIRED
 *       ─────────────                   ─────────────────────────
 *       View.OnClickListener            SeekBar.OnSeekBarChangeListener
 *         onClick(View)                   onProgressChanged(SeekBar, int, boolean)
 *                                         onStartTrackingTouch(SeekBar)
 *       CompoundButton.OnChecked...       onStopTrackingTouch(SeekBar)
 *         onCheckedChanged(CompoundButton, boolean)
 *                                       TextWatcher (unused in DMA05)
 *       RadioGroup.OnChecked...           beforeTextChanged(CharSequence, int, int, int)
 *         onCheckedChanged(RadioGroup, int) onTextChanged(CharSequence, int, int, int)
 *                                         afterTextChanged(Editable)
 *       RatingBar.OnRatingBar...
 *         onRatingChanged(RatingBar, float, boolean)
 *
 *       View.OnApplyWindowInsets...
 *         onApplyWindowInsets(View, WindowInsetsCompat)
 *
 * THE RULE, IN ONE SENTENCE: one abstract method → lambda allowed; two or
 * more → anonymous class required. The style in the repo alternates deliberately, so that
 * you see both forms on the same interface (button is an anonymous class, although it could have
 * been a lambda).
 *
 * THE TIMELINE OF FIRING:
 *
 *   BUTTON (click)
 *     ACTION_DOWN ──▶ ACTION_UP ──▶ performClick() ──▶ onClick(v)
 *     (if the finger leaves the view between down and up, the click does NOT fire)
 *
 *   SWITCH / CHECKBOX / TOGGLEBUTTON (checked)
 *     touch ──▶ toggle() ──▶ setChecked(!checked) ──▶ onCheckedChanged(view, isChecked)
 *     OR setChecked(true) from code ──▶ onCheckedChanged(view, true)
 *
 *   SEEKBAR (3 moments)
 *     ACTION_DOWN ──▶ onStartTrackingTouch(bar)
 *     ACTION_MOVE ──▶ onProgressChanged(bar, val, true)   ← many times
 *     ACTION_UP   ──▶ onStopTrackingTouch(bar)
 *     OR setProgress(50) from code ──▶ onProgressChanged(bar, 50, false)
 *
 *   RADIOGROUP (selection)
 *     touch on a RadioButton
 *       └── the child checks itself
 *             └── the group unchecks the other children
 *                   └── onCheckedChanged(group, R.id.radioButtonN)   ← once
 *     OR clearCheck() ──▶ onCheckedChanged(group, -1)   ← pitfall no. 3
 *
 *   RATINGBAR (float value)
 *     touch on the stars ──▶ onRatingChanged(bar, rating, true)
 *     OR setRating(3.5f) ──▶ onRatingChanged(bar, 3.5f, false)
 *
 * WHAT THEY ALL HAVE IN COMMON: the listener fires AFTER the state has changed, not
 * before. When you enter onCheckedChanged, isChecked is already the new value; when you enter
 * onProgressChanged, progress is already the new value. You do not have to read the state
 * from the widget — you receive it as a parameter.
 *
 * WHAT DIFFERS: the number of events per gesture. One click = one event. One SeekBar
 * drag = one start, N progress, one stop. One check = one event. That is why SeekBar
 * needs three methods, and CheckBox one.
 *
 * WHAT "FUNCTIONAL INTERFACE" MEANS IN JAVA: an interface with exactly one abstract
 * method. It can have any number of default and static methods, but a single method without
 * an implementation. View.OnClickListener has onClick abstract and nothing else.
 * SeekBar.OnSeekBarChangeListener has three abstract methods, so it is not functional.
 *
 * WHY A LAMBDA DOES NOT NEED new: the lambda expression IS the implementation of the abstract
 * method. The compiler generates a class (or an invokedynamic) and knows which method
 * to bind because there is only one. When there are three, it has no way to guess.
 *
 * AT RUNTIME: a lambda that captures no variables is a singleton. A lambda that
 * captures (MainActivity.this is captured implicitly) allocates an instance once,
 * at registration. The cost is negligible, but it exists.
 */
```

### After the code: the seven families, in a table

| # | Line | Widget | Registration method | Interface | Methods | Style |
|---|---|---|---|---|---|---|
| 1 | 38 | `button` | `setOnClickListener` | `View.OnClickListener` | 1 | anonymous class |
| 2 | 45 | `switch1` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 3 | 49 | `checkBox` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 4 | 53 | `seekBar` | `setOnSeekBarChangeListener` | `SeekBar.OnSeekBarChangeListener` | **3** | anonymous class |
| 5 | 70 | `radioGroup` | `setOnCheckedChangeListener` | `RadioGroup.OnCheckedChangeListener` | 1 | anonymous class |
| 6 | 78 | `toggleButton` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 7 | 82 | `ratingBar` | `setOnRatingBarChangeListener` | `RatingBar.OnRatingBarChangeListener` | 1 | lambda |

### The map of the lines in the file

| Lines | What it contains |
|---|---|
| 1–17 | `package` + the 15 imports (3 groups) |
| 19–21 | the `MainActivity` class + the `binding` field |
| 23–24 | the header of `onCreate` |
| 25 | `super.onCreate(savedInstanceState)` |
| 27 | `ActivityMainBinding.inflate(getLayoutInflater())` |
| 29–30 | `EdgeToEdge.enable(this)` + `setContentView(binding.getRoot())` |
| 31–35 | the insets listener (lambda) |
| 38–43 | `button` — `View.OnClickListener` (anonymous class) |
| 45–47 | `switch1` — `CompoundButton.OnCheckedChangeListener` (lambda) |
| 49–51 | `checkBox` — the same interface (lambda) |
| 53–68 | `seekBar` — `SeekBar.OnSeekBarChangeListener` (3 methods, anonymous class) |
| 70–76 | `radioGroup` — `RadioGroup.OnCheckedChangeListener` (anonymous class) |
| 78–80 | `toggleButton` — `CompoundButton.OnCheckedChangeListener` (lambda) |
| 82–84 | `ratingBar` — `RatingBar.OnRatingBarChangeListener` (lambda) |
| 87–88 | the closing of `onCreate` and of the class |

**How to use the map:** if you want to change a single behaviour, jump straight to its lines. If you want to understand the flow, read 23–35 (construction + insets), then 38–84 (the listeners, in file order). The rest is imports and braces.

### What has no listener — and why

Seven widgets have a listener. The rest do not:

| View | Why not | What you would use if you wanted to |
|---|---|---|
| `imageView` | display only | `setOnClickListener` (every `View` has it) |
| the 5 `EditText` | they are read when needed, not on typing | `addTextChangedListener(new TextWatcher(){...})` — **3 methods**, so an anonymous class |
| `progressBar` | it is demonstrative, it stays at 0 | `setProgress(int)` from code |
| `radioButton1/2` | the group covers them | a listener on each button, rarely useful |

**`TextWatcher` is the other example of a three-method interface** that you meet often, next to `SeekBar.OnSeekBarChangeListener`. If a test asks you "react when the user types", the answer is `TextWatcher` with `beforeTextChanged`, `onTextChanged`, `afterTextChanged`.

**Why the `EditText`s have no listener here:** DMA05 has nowhere to take the value. There is no save button, no model, no database. A `TextWatcher` would produce Toasts on every keystroke — and worse than with the `SeekBar`.

---

## 27.2 `activity_main.xml` — the whole file, annotated

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FILE: activity_main.xml
  ======================================================================================
  LOCATION: DMA05/src/main/res/layout/activity_main.xml
  ROLE:     the only layout of the application. A vertical LinearLayout with 14 direct children,
           which covers all the usual input widgets.
  IDs:     17 (the root + 16 children or descendants)
  USED IN CODE: 7 (button, switch1, checkBox, seekBar, radioGroup, toggleButton, ratingBar)
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: INFLATE → MEASURE → LAYOUT → DRAW
  ======================================================================================
  1. INFLATE (build + runtime)
     At build: aapt2 compiles the XML into a binary format and generates R.id.*.
     At runtime: LayoutInflater parses the binary XML and creates the Java objects.
     Each tag becomes an object; each android:* attribute becomes a value in
     the AttributeSet, read by the constructor.

  2. MEASURE
     The parent asks each child: "how big do you want to be?"
     The answer depends on the MeasureSpec, which has two components: mode + size.
       EXACTLY   → the size is imposed (match_parent or a fixed value)
       AT_MOST   → the child can be as big as it wants, but no bigger than that (wrap_content)
       UNSPECIFIED → no constraints (ScrollView vertically)
     The result: getMeasuredWidth() / getMeasuredHeight().

  3. LAYOUT
     The parent decides the position of each child: left, top, right, bottom.
     Vertical LinearLayout: each child receives top = the bottom of the previous child.
     The result: getLeft(), getTop(), getWidth(), getHeight().

  4. DRAW
     Each view draws its content: background, text, images, children.
     This is where the first pixel appears on screen.

  WHY IT MATTERS:
     - match_parent on width + wrap_content on height = a form row.
     - A LinearLayout without a ScrollView cannot be scrolled vertically: it measures
       the children with AT_MOST on the screen height, and whatever does not fit is clipped.
     - setPadding in the insets listener is applied BEFORE measure, so it
       changes the measurement, not just the drawing.
  ======================================================================================
-->

<!--
  THE ROOT — a vertical LinearLayout.
  WHY LinearLayout and not ConstraintLayout: for 14 children stacked vertically,
    LinearLayout is enough and simpler. ConstraintLayout would have added constraints
    for each child, with no benefit.
  WHY vertical: the children are stacked from top to bottom, one under another.
  WHY not a ScrollView: on a small screen, the last widgets (SeekBar, RatingBar) can
    go outside the visible area. G1097 wraps the form in a ScrollView for exactly
    this reason.

  THE ATTRIBUTES, LINE BY LINE:
    xmlns:android   → the framework attributes
    xmlns:app       → the library attributes (here, app:srcCompat on the ImageView)
    xmlns:tools     → attributes that exist ONLY in the preview and are stripped at build
    android:id      → @+id/main; the root has an ID, so binding.main exists, but the code
                      uses binding.getRoot()
    layout_width    → match_parent: fills the window
    layout_height   → match_parent: fills the window
    orientation     → vertical
    tools:context   → only for the preview; it tells Android Studio which activity
                      to simulate. Stripped at build.

  The space before `>` (tools:context=".MainActivity" >) is in the real file.
  XML ignores it. Do not "fix" it — the code must stay byte-identical.
-->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity" >

    <!--
      BUTTON — the first child; the only one with a click listener.
        android:id="@+id/button"              → the binding.button field (type Button)
        android:layout_width="match_parent"   → as wide as the parent (the whole column)
        android:layout_height="wrap_content"  → as tall as the text + the default padding
        android:text="Button"                 → the label; hardcoded, not from strings.xml

      match_parent on width + wrap_content on height = a form row.
      android:text is hardcoded; lint gives a HardcodedText warning. strings.xml contains only
      app_name — DMA05 is a lab, not a product.
    -->
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Button" />

    <!--
      IMAGEVIEW — the second child; no listener, display only.
        android:id="@+id/imageView"           → the binding.imageView field
        app:srcCompat="@drawable/…"           → the vector, through AppCompat (not android:src)
        layout_height="wrap_content"          → the intrinsic height of the drawable

      app:srcCompat and not android:src: the AppCompat variant, needed for VectorDrawable
      on old APIs and for app:tint. The file ic_android_black_24dp.xml is a vector.
      ImageView has no listener — it is the counterexample that shows that "every widget has
      a listener" is false.
    -->
    <ImageView
        android:id="@+id/imageView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        app:srcCompat="@drawable/ic_android_black_24dp" />

    <!--
      SWITCH — the third child; CompoundButton, check listener.
        android:id="@+id/switch1"             → the binding.switch1 field (not `switch`)
        android:text="Switch"                 → the label on the left, not the state
        no android:checked                    → it starts off

      Why the ID is switch1 and not switch: the layout generator in Android Studio
      builds the ID from the widget name and adds a number when the plain name
      is not available. The code uses it exactly like that: binding.switch1.
    -->
    <Switch
        android:id="@+id/switch1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Switch" />

    <!--
      EDITTEXT #1 — free text.
        android:id="@+id/editTextText"        → the binding.editTextText field
        android:ems="10"                      → a minimum width of 10 ems (ignored by match_parent)
        android:inputType="text"              → TYPE_CLASS_TEXT: QWERTY, no filtering
        android:hint="Text"                   → placeholder, disappears on the first keystroke

      android:ems="10" — "the width of 10 M characters". With layout_width="match_parent",
      the MeasureSpec is EXACTLY on width, so ems is ignored. It remains as a leftover.
      android:hint is NOT a value: getText() returns "", not the hint. The hint is drawn
      by the TextView itself, only while the text is empty.
    -->
    <EditText
        android:id="@+id/editTextText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:inputType="text"
        android:hint="Text" />

    <!--
      EDITTEXT #2 — password.
        android:id="@+id/editTextTextPassword" → the binding.editTextTextPassword field
        android:inputType="textPassword"       → masking with dots + suggestions turned off
        android:hint="Password"                → placeholder; NOT a value

      The masking is only visual: the real text stays in getText() and reaches the Bundle on
      rotation if you do not disable state saving. For a lab it is enough.
    -->
    <EditText
        android:id="@+id/editTextTextPassword"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Password"
        android:inputType="textPassword" />

    <!--
      EDITTEXT #3 — email.
        android:id="@+id/editTextTextEmailAddress" → the binding.editTextTextEmailAddress field
        android:inputType="textEmailAddress"       → keyboard with @ and ., no validation
        android:hint="Email"                       → placeholder

      inputType does not validate: you can type abc without @. The IME can offer address
      suggestions, but the field accepts anything.
    -->
    <EditText
        android:id="@+id/editTextTextEmailAddress"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Email"
        android:inputType="textEmailAddress" />

    <!--
      EDITTEXT #4 — time.
        android:id="@+id/editTextTime"        → the binding.editTextTime field
        android:inputType="time"              → numeric keyboard + time separator
        android:hint="Time"                   → placeholder

      The keyboard is numeric with `:`; the filter accepts digits and separators, but it also accepts
      99:99. Format validation remains the code's job.
    -->
    <EditText
        android:id="@+id/editTextTime"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Time"
        android:inputType="time" />

    <!--
      EDITTEXT #5 — date.
        android:id="@+id/editTextDate"        → the binding.editTextDate field
        android:inputType="date"              → numeric keyboard + date separator
        android:hint="Date"                   → placeholder

      The keyboard is numeric with `/`; it also accepts 99/99/9999. inputType is a contract with
      the keyboard, not with the data.
    -->
    <EditText
        android:id="@+id/editTextDate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Date"
        android:inputType="date" />

    <!--
      CHECKBOX — 0..n independent choices.
        android:id="@+id/checkBox"            → the binding.checkBox field
        android:text="CheckBox"               → the label on the right
        no android:checked                    → it starts unchecked
    -->
    <CheckBox
        android:id="@+id/checkBox"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="CheckBox" />

    <!--
      RADIOGROUP — the container enforces mutual exclusion between the children.
        android:id="@+id/radioGroup"          → the binding.radioGroup field
        no android:orientation                → vertical by default
        no android:checkedButton              → no button checked at startup

      CheckBox = 0..n independent choices. RadioGroup = exactly 0 or 1. Two RadioButtons
      without a RadioGroup around them would behave like checkboxes — that is the whole role of
      the container. RadioGroup extends LinearLayout, so it has orientation, gravity and
      layout_weight for the children.
    -->
    <RadioGroup
        android:id="@+id/radioGroup"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" >

        <!--
          OPTION 1.
            android:id="@+id/radioButton1"    → R.id.radioButton1, the value in checkedId
            android:text="First Option"       → the text returned by getText()
        -->
        <RadioButton
            android:id="@+id/radioButton1"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="First Option" />

        <!--
          OPTION 2.
            android:id="@+id/radioButton2"    → R.id.radioButton2, the value in checkedId
            android:text="Second Option"      → the text returned by getText()

          The children have IDs, so binding.radioButton1 and binding.radioButton2 exist.
          The code does not use them — it goes through group.findViewById(checkedId). Both paths
          are valid.
        -->
        <RadioButton
            android:id="@+id/radioButton2"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Second Option" />

    </RadioGroup>

    <!--
      TOGGLEBUTTON — a button with two states.
        android:id="@+id/toggleButton"        → the binding.toggleButton field
        android:text="ToggleButton"           → the label for the ON state; OFF is "OFF" by default
        no android:textOn / textOff           → hence the ON/OFF inconsistency
    -->
    <ToggleButton
        android:id="@+id/toggleButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="ToggleButton" />

    <!--
      PROGRESSBAR — demonstrative, it stays at 0.
        android:id="@+id/progressBar"         → the binding.progressBar field
        style="?android:attr/progressBarStyleHorizontal" → a bar, not a circle
        no android:progress                   → the default value 0

      Without the style, it would be the circle that spins forever. ?android:attr/... means
      "the attribute from the platform theme", not from the application theme.
    -->
    <ProgressBar
        android:id="@+id/progressBar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <!--
      SEEKBAR — sliding bar.
        android:id="@+id/seekBar"             → the binding.seekBar field
        no android:max                        → the default maximum 100
        no android:progress                   → the initial value 0

      SeekBar extends ProgressBar (through AbsSeekBar), which is why it has getProgress() and
      setProgress(int). The difference: it adds the finger and the three touch events.
    -->
    <SeekBar
        android:id="@+id/seekBar"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <!--
      RATINGBAR — 5 stars, step of 0.5.
        android:id="@+id/ratingBar"           → the binding.ratingBar field
        android:numStars="5"                  → 5 stars
        android:stepSize="0.5"                → half stars → a float value
        android:layout_gravity="center_horizontal" → centred horizontally
        layout_width="wrap_content"           → as wide as the stars, not as the screen

      RatingBar extends AbsSeekBar, so it is also a ProgressBar with getProgress().
      The default value is 0, so no star is lit at startup.
    -->
    <RatingBar
        android:id="@+id/ratingBar"
        android:numStars="5"
        android:layout_gravity="center_horizontal"
        android:stepSize="0.5"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
</LinearLayout>
```

### After the code: the inventory of the widgets

| `android:id` | Widget | `inputType` / key attribute | Listener | Notes |
|---|---|---|---|---|
| `main` | `LinearLayout` (root) | `orientation="vertical"` | insets (not a widget listener) | the ID is **not** used by the code |
| `button` | `Button` | — | `setOnClickListener` — anonymous class | the only `onClick` in the file |
| `imageView` | `ImageView` | `app:srcCompat` | — | display only |
| `switch1` | `Switch` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `editTextText` | `EditText` | `text` | — | free text |
| `editTextTextPassword` | `EditText` | `textPassword` | — | masked with dots |
| `editTextTextEmailAddress` | `EditText` | `textEmailAddress` | — | keyboard with `@` |
| `editTextTime` | `EditText` | `time` | — | numeric keyboard |
| `editTextDate` | `EditText` | `date` | — | numeric keyboard |
| `checkBox` | `CheckBox` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `radioGroup` | `RadioGroup` | `orientation` vertical by default | `setOnCheckedChangeListener` — anonymous class | receives `checkedId` |
| `radioButton1` | `RadioButton` | — | through the group | "First Option" |
| `radioButton2` | `RadioButton` | — | through the group | "Second Option" |
| `toggleButton` | `ToggleButton` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `progressBar` | `ProgressBar` | `style=?android:attr/progressBarStyleHorizontal` | — | stays at 0 |
| `seekBar` | `SeekBar` | `max` default **100** | `setOnSeekBarChangeListener` — anonymous class | 3 methods |
| `ratingBar` | `RatingBar` | `numStars="5"`, `stepSize="0.5"` | `setOnRatingBarChangeListener` — lambda | `float` value |

**17 IDs, 7 used in code.** The other 10 produce fields in `ActivityMainBinding` that nobody touches — and it is perfectly normal: the binding generates them all, whether you use them or not. The extra IDs cost only one reference per field, filled once at `inflate`. On top of that, the IDs are needed for **state restoration** on rotation: without an ID, a widget does not save its state.

### The 14 direct children, one by one

| # | Widget | What it is, in one sentence |
|---|---|---|
| 1 | `Button` | a button with text; the only view in the layout that receives `setOnClickListener` |
| 2 | `ImageView` | displays a vector; it does not react to anything, it is decoration |
| 3 | `Switch` | a sliding on/off switch; `CompoundButton`, like `CheckBox` |
| 4 | `EditText` (`text`) | free field, QWERTY keyboard, no filtering |
| 5 | `EditText` (`textPassword`) | field masked with dots, no suggestions |
| 6 | `EditText` (`textEmailAddress`) | keyboard with `@` and `.`, but it accepts any text |
| 7 | `EditText` (`time`) | numeric keyboard with `:`; it also accepts "99:99" |
| 8 | `EditText` (`date`) | numeric keyboard with `/`; it also accepts "99/99/9999" |
| 9 | `CheckBox` | an independent check; 0..n such checks |
| 10 | `RadioGroup` | a container with two `RadioButton`s; it enforces exactly 0 or 1 selection |
| 11 | `ToggleButton` | a button with two states; the text in the XML is the ON label |
| 12 | `ProgressBar` | a demonstrative horizontal bar; it stays at 0 |
| 13 | `SeekBar` | a sliding bar 0..100; the only one with three events |
| 14 | `RatingBar` | five stars with a step of 0.5; a `float` value |

**Why exactly these 14:** they are the inventory of input widgets that the test exercises ask for. Each appears once, so that you can compare behaviours: three `CompoundButton`s (`Switch`, `CheckBox`, `ToggleButton`), two bars (`ProgressBar`, `SeekBar`), a single family of exclusive selection (`RadioGroup` + `RadioButton`), five variations of `EditText`.

### `inputType` — the full table

| Value | Android constant | Keyboard shown | Restricts? | Validates? |
|---|---|---|---|---|
| `text` | `TYPE_CLASS_TEXT` | a normal QWERTY | no | no |
| `textPassword` | `TYPE_CLASS_TEXT \| TYPE_TEXT_VARIATION_PASSWORD` | QWERTY, no suggestions | **yes** — masking with dots, no auto-correct | no |
| `textEmailAddress` | `TYPE_CLASS_TEXT \| TYPE_TEXT_VARIATION_EMAIL_ADDRESS` | QWERTY with `@` and `.` | **no** — it only optimises the keyboard | no |
| `time` | `TYPE_CLASS_DATETIME \| TYPE_DATETIME_VARIATION_TIME` | digits and `:` | partially — it filters to digits and separators | no |
| `date` | `TYPE_CLASS_DATETIME \| TYPE_DATETIME_VARIATION_DATE` | digits and `/` | partially — it filters to digits and separators | no |

> **`inputType` does not validate.** You can type an email without `@` in a `textEmailAddress` field and a time "99:99" in a `time` field. Validation is your job, in the code. `inputType` is a **contract with the keyboard**, not with the data.

### The three channels through which the XML reaches the code

```
activity_main.xml
      │
      ├── CHANNEL 1: android:id ──────────────▶ ViewBinding (BUILD)
      │     @+id/button                         → public final Button button;
      │                                         → binding.button
      │     link verified at compile time
      │
      ├── CHANNEL 2: behaviour attributes ────▶ the widget (RUNTIME)
      │     android:inputType="time"            → setInputType(...) in the constructor
      │     android:max="100"                   → setMax(100)
      │     android:checked="true"              → setChecked(true)
      │     android:hint="Time"                 → setHint("Time")
      │     link read at inflate, not verified by you
      │
      └── CHANNEL 3: style and theme ──────────▶ the appearance (RUNTIME)
            ?android:attr/progressBarStyleHorizontal → the style of the bar
            Theme.DMA05                        → colours, typography, shapes
            link through ?attr/... attributes and style=
```

**Channel 1 is the only one verified by the compiler.** If you change `android:id` in the XML and forget to change the code, the build fails at `binding.oldId`. That is why `ViewBinding` is considered "type-safe": the link is mechanical, not textual.

**Channel 2 is not verified by anyone.** `android:inputType="time"` produces a behaviour at runtime, but nobody stops you from reading the value as an `int` and crashing at parsing. The attributes are read by the widget's constructor from the `AttributeSet`, at inflate.

**Channel 3 is the most invisible one.** `?android:attr/progressBarStyleHorizontal` resolves an attribute from the platform theme. If the theme changed, the bar would look different, with no change in the XML or the Java.

---

## 27.3 `AndroidManifest.xml` — the whole file, annotated

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FILE: AndroidManifest.xml
  ======================================================================================
  LOCATION: DMA05/src/main/AndroidManifest.xml
  ROLE:     declares the application, the theme and the only activity. Without it, the icon does not start.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: THE MANIFEST
  ======================================================================================
  1. WHAT IT IS
     An XML file that declares the application to the operating system, BEFORE running
     any line of Java. The system reads it at install time and when starting a component.

  2. WHO USES IT
     - at install: which permissions the app asks for, which components it has
     - at launch: which is the start activity (intent-filter MAIN + LAUNCHER)
     - at navigation: which activities can be started from other apps (exported)
     - at runtime: which theme the app has, which soft input mode the activity has

  3. MANIFEST MERGER
     At build, AGP combines your manifest with the manifests of the libraries (AppCompat,
     Material, activity-ktx). Each library declares its components and
     permissions. The result is a single manifest, in the APK.
     The tools: attributes resolve conflicts:
       tools:node="merge"     → combine
       tools:node="replace"   → replace
       tools:node="remove"    → remove
     DMA05 has no conflicts, so it does not use tools: in the manifest.

  4. THE ATTRIBUTES IN <application>
     android:allowBackup="true"          → the system can save the application data
     android:dataExtractionRules         → the backup rules for Android 12+
     android:fullBackupContent           → the backup rules for older versions
     android:icon / roundIcon            → the icons
     android:label="@string/app_name"    → the name in the launcher
     android:supportsRtl="true"          → support for right-to-left writing
     android:theme="@style/Theme.DMA05"  → the application theme

  5. THE ATTRIBUTES IN <activity>
     android:name=".MainActivity"        → the class; the dot means the application namespace
     android:exported="true"             → it can be started from outside (needed by the launcher)
     android:windowSoftInputMode="adjustResize" → how it reacts to the keyboard

  6. INTENT-FILTER
     <action android:name="android.intent.action.MAIN" />
     <category android:name="android.intent.category.LAUNCHER" />
     The MAIN + LAUNCHER combination is what makes the activity appear in the launcher.
     Without it, the activity exists, but nobody starts it.

  7. WHAT DMA05 DOES NOT HAVE
     - no <uses-permission>              → it does not access anything protected
     - no <service>, <receiver>          → a single activity
     - no package attribute              → it comes from namespace (AGP 8+)
  ======================================================================================
-->

<!--
  There is no `package` attribute: since AGP 8, the package comes from
  namespace = "ro.ase.ie.dma05" in build.gradle.kts. If you left package in, the build
  would fail with a message saying the attribute is no longer supported in the source manifest.
  namespace is used both for R and for the generated databinding class.
-->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!--
      <application> — everything that concerns the application as a whole.
        allowBackup + dataExtractionRules + fullBackupContent → the Android Studio template;
          the files res/xml/backup_rules.xml and data_extraction_rules.xml exist in the project
        icon / roundIcon      → the icons (roundIcon for Android 7.1+)
        label                 → the name in the launcher, from strings.xml (the only entry there)
        supportsRtl           → the interface mirrors itself in RTL languages
        theme                 → Theme.DMA05, defined in values/themes.xml
    -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA05">

        <!--
          THE ONLY ACTIVITY.
            android:name=".MainActivity"   → the leading dot means "the application
                                             namespace"; so ro.ase.ie.dma05.MainActivity
            android:exported="true"        → mandatory since API 31 for any component
                                             with an intent-filter; without it, the build fails.
                                             It means "other applications are allowed to start
                                             this" — needed for the launcher icon.
            windowSoftInputMode="adjustResize" → asks the system to shrink the window
                                             when the keyboard appears. With edge-to-edge on
                                             API 30+, the window is NO longer resized
                                             by the system: the application must consume
                                             WindowInsetsCompat.Type.ime(). DMA05 handles
                                             only systemBars(), so the keyboard covers
                                             the bottom widgets. It is not visible, because
                                             the EditTexts are at the top.
        -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!--
              INTENT-FILTER — what makes the activity visible in the launcher.
              Without it, the activity exists, but nobody starts it; you can start it only
              with adb shell am start, if you know the full name.
            -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
```

### After the code: what the manifest declares

**`android:theme="@style/Theme.DMA05"`** — defined in `values/themes.xml`, with the parent `Theme.Material3.DayNight.NoActionBar`. `NoActionBar` explains why the application has no title bar: the first widget starts immediately under the status bar, pushed down only by the insets padding.

**`xmlns:tools` is declared, but unused** — no `tools:` attribute appears in the manifest. A template leftover, harmless.

**There are no permissions.** The application does not access anything protected: neither internet, nor storage, nor camera. A manifest without `<uses-permission>` is normal for a widget lab.

**Why `.MainActivity` with a dot:** the leading dot means "the full name is formed by concatenating with `namespace`". So `.MainActivity` becomes `ro.ase.ie.dma05.MainActivity`. Without the dot, it would be interpreted as a full name and you would have to write it all.

---

## 27.4 ViewBinding vs `findViewById`

### The direct comparison

| Criterion | `findViewById` | `ViewBinding` |
|---|---|---|
| When you find out the ID is wrong | at runtime, as `null` | at compile time |
| The type returned | `View`, with a cast | exact, inferred from the tag |
| Lines of code per view | 1 | 0 |
| Can it return `null`? | **yes** | no, after `inflate` |
| Renaming an ID | manual, can be missed | the build fails |
| Wrong layout | the same ID can be missing → `null` | one class per layout, impossible to confuse |
| Runtime cost | a lookup in the tree | a field read |
| Verification | runtime | build |

**The classic equivalent of the file**, for comparison. **It does not exist in the repo** — it is written here only as a reference point:

```java
// ILLUSTRATIVE — this is how MainActivity would have looked without ViewBinding.
// It is not code from DMA05.
setContentView(R.layout.activity_main);

Button button = findViewById(R.id.button);
Switch switch1 = findViewById(R.id.switch1);
CheckBox checkBox = findViewById(R.id.checkBox);
SeekBar seekBar = findViewById(R.id.seekBar);
RadioGroup radioGroup = findViewById(R.id.radioGroup);
ToggleButton toggleButton = findViewById(R.id.toggleButton);
RatingBar ratingBar = findViewById(R.id.ratingBar);
```

Seven extra lines, seven chances to get an ID wrong and seven hidden casts. In `ViewBinding`, all seven lines disappear — only the `binding.` prefix remains in front of each access.

### What each one costs, at runtime

```
findViewById(R.id.button)                    binding.button
        │                                          │
        ▼                                          ▼
View.findViewById(int id)                    getfield
  ├─ this.mID == id ?                          ActivityMainBinding.button
  │     return this                                 │
  ├─ for (child : children)                         │
  │     child.findViewById(id)  ← recursive         │
  └─ return null                                     ▼
        │                                       O(1)
        ▼                                       zero allocations
  O(n) in the subtree                           zero lookups
  + a temporary int[] allocation in ViewGroup
```

**What it means concretely:** `findViewById` on a tree with 17 views makes up to 17 `int` comparisons and, if the view is the last one, walks the whole tree. For a single call it is negligible. The problem appears when you call it in the `onBindViewHolder` of a list with 1000 rows: 1000 × O(n) on every scroll. `ViewBinding` moves the whole lookup into a single `bind`, at `inflate`.

**Why `findViewById` needs a cast:** the method is declared `public final <T extends View> T findViewById(int id)` in the modern API, so the cast is implicit through inference. In old code, the signature returned `View` and the cast was explicit: `(Button) findViewById(...)`. `ViewBinding` needs no cast at all, because the field's type is already the correct one.

**Why `findViewById` can return `null`:** the lookup is done at runtime, and the compiler does not know which IDs exist in the layout. A wrong ID or a view that is not in the current tree returns `null`, and the first access throws `NullPointerException`. `ViewBinding` checks at `bind` and throws immediately, with the message `Missing required view with ID: …` — earlier and clearer.

### What the generated class contains

For each `android:id` in the layout, a public final field with the exact type. In DMA05 there are **17**:

| Generated field | Type | Used in code? |
|---|---|---|
| `main` | `LinearLayout` | no (`getRoot()` is used) |
| `button` | `Button` | **yes** |
| `imageView` | `ImageView` | no |
| `switch1` | `Switch` | **yes** |
| `editTextText` | `EditText` | no |
| `editTextTextPassword` | `EditText` | no |
| `editTextTextEmailAddress` | `EditText` | no |
| `editTextTime` | `EditText` | no |
| `editTextDate` | `EditText` | no |
| `checkBox` | `CheckBox` | **yes** |
| `radioGroup` | `RadioGroup` | **yes** |
| `radioButton1` | `RadioButton` | no |
| `radioButton2` | `RadioButton` | no |
| `toggleButton` | `ToggleButton` | **yes** |
| `progressBar` | `ProgressBar` | no |
| `seekBar` | `SeekBar` | **yes** |
| `ratingBar` | `RatingBar` | **yes** |

**The field name is the ID, letter for letter.** `switch1` → `binding.switch1`; `editTextTextEmailAddress` → `binding.editTextTextEmailAddress`. There is no conversion, no abbreviations.

**`getRoot()` always exists**, whether or not the root has an ID. `binding.main` exists only because the root has `@+id/main`.

**Why the fields are `public final`:** `public` so that you can read them directly, `final` so that you cannot reassign them. They are filled once, in the generated constructor, and never change again. A `binding.button = null` does not compile.

### A small, complete example

DMA05 has 17 fields, too many to see the shape of the class. An imaginary layout with three IDs looks like this:

```java
// RECONSTRUCTION for an imaginary layout `activity_demo.xml`:
//   <LinearLayout android:id="@+id/main">
//       <Button   android:id="@+id/btnOk" />
//       <TextView android:id="@+id/tvResult" />
//   </LinearLayout>
// It does not exist in the repo; it is here so that you can see the minimal shape of the generated class.

public final class ActivityDemoBinding implements ViewBinding {

    private final LinearLayout rootView;      // the root, for getRoot()
    public final LinearLayout main;           // field for @+id/main
    public final Button btnOk;                // field for @+id/btnOk
    public final TextView tvResult;           // field for @+id/tvResult

    private ActivityDemoBinding(LinearLayout rootView, LinearLayout main,
                                Button btnOk, TextView tvResult) {
        this.rootView = rootView;             // private constructor: only the factories call it
        this.main = main;
        this.btnOk = btnOk;
        this.tvResult = tvResult;
    }

    @Override
    public LinearLayout getRoot() { return rootView; }   // the ViewBinding contract

    public static ActivityDemoBinding inflate(LayoutInflater inflater) {
        return inflate(inflater, null, false);           // the one-argument variant
    }

    public static ActivityDemoBinding inflate(LayoutInflater inflater,
                                              ViewGroup parent, boolean attachToRoot) {
        View root = inflater.inflate(R.layout.activity_demo, parent, attachToRoot);
        return bind(root);                               // after inflate, fills the fields
    }

    public static ActivityDemoBinding bind(View rootView) {
        int id;
        id = R.id.main;
        LinearLayout main = ViewBindings.findChildViewById(rootView, id);
        if (main == null) {
            throw new NullPointerException("Missing required view with ID: "
                    + rootView.getResources().getResourceName(id));
        }
        id = R.id.btnOk;
        Button btnOk = ViewBindings.findChildViewById(rootView, id);
        if (btnOk == null) {
            throw new NullPointerException("Missing required view with ID: "
                    + rootView.getResources().getResourceName(id));
        }
        id = R.id.tvResult;
        TextView tvResult = ViewBindings.findChildViewById(rootView, id);
        if (tvResult == null) {
            throw new NullPointerException("Missing required view with ID: "
                    + rootView.getResources().getResourceName(id));
        }
        return new ActivityDemoBinding((LinearLayout) rootView, main, btnOk, tvResult);
    }
}
```

**What can be seen in the example and also applies to DMA05:**

1. **One field per ID, plus `rootView`.** The root has two references: `rootView` (private, for `getRoot()`) and `main` (public, for the ID). They are the same object.
2. **The constructor is private.** You cannot do `new ActivityDemoBinding(...)` from your code. The only ways to obtain a binding are `inflate` and `bind`.
3. **`bind` is the only place with lookups.** Three IDs → three `findChildViewById`. After `bind`, no lookup.
4. **Failure is immediate and explicit.** If an ID is missing from the tree, `bind` throws `NullPointerException` with the resource name, it does not return `null` onwards.
5. **The cast happens once, on the root.** `(LinearLayout) rootView` — because `inflate` returns `View`, and the field is `LinearLayout`. The other fields receive the exact type from `findChildViewById`, without a cast.

**Why `bind` is public:** you can use it when you already have a view inflated another way — for example in a `RecyclerView.Adapter`, where the parent does the inflating. `bind(view)` gives you the fields without inflating once more.

### Why `binding` is a field, not a local variable

In DMA05, a local would be enough — everything happens in `onCreate`. The field is the pattern because:

1. in real applications the binding is touched from several methods;
2. the anonymous classes in the listeners may need it;
3. on rotation, `onCreate` runs again and **reassigns** the field — no old binding remains.

**It is not a memory leak** in an `Activity`: the activity and the binding die together. In a `Fragment` it would be — that is why there the `_binding` pattern with `onDestroyView` is used.

### What `ViewBinding` does not do

- **It is not `DataBinding`.** It does not allow expressions in XML (`@{...}`), it does not bind models directly to views. References only.
- **It does not replace `findViewById` for IDs received at runtime** — like `checkedId` from `RadioGroup`.
- **It does not generate fields for views without `android:id`.** Without an ID, it has no name to give the field.
- **It does not generate code for `include`s** unless the include has an ID; then the field has the type of the included binding.
- **It does not validate the XML semantically.** A `TextView` with `android:text="123"` and a wrong `inputType` compiles; the binding only links references.

**Why `findViewById` still exists in the file:** for `checkedId`. It is the only case where the ID is not known at compile time. All the other 16 IDs are known, so they have a field.

---

## 27.5 The complete flow

```
STARTUP
  AndroidManifest: <intent-filter> MAIN + LAUNCHER
    ↓
  MainActivity.onCreate(savedInstanceState = null)
    ├── super.onCreate                → the activity is bound to the Window
    ├── ActivityMainBinding.inflate(getLayoutInflater())
    │     ├── parses activity_main.xml
    │     ├── creates LinearLayout(main) + 14 direct children
    │     └── fills 17 fields: main, button, imageView, …, ratingBar
    ├── EdgeToEdge.enable(this)       → the window draws under the bars
    ├── setContentView(binding.getRoot())   → the tree reaches the screen
    ├── setOnApplyWindowInsetsListener(root)
    └── 7 × setOn...Listener          → no Toast yet

THE FIRST LAYOUT PASS
  the insets arrive
    └── v.setPadding(left, top, right, bottom)
          └── all the children move into the safe area

THE USER PRESSES THE BUTTON
  touch → performClick → listener.onClick(v)
    └── Toast.makeText(MainActivity.this, "Button clicked", LENGTH_SHORT).show()
          └── Toast window, ~2 seconds, disappears by itself

THE USER DRAGS THE SEEKBAR
  onStartTrackingTouch(seekBar)          → empty body
  onProgressChanged(seekBar, 1, true)    → Toast "Progress changed to 1"
  onProgressChanged(seekBar, 2, true)    → Toast "Progress changed to 2"
  …                                      → tens of Toasts, put in a queue
  onStopTrackingTouch(seekBar)           → empty body

THE USER PRESSES A RADIOBUTTON
  RadioGroup unchecks the other button
    └── onCheckedChanged(group, R.id.radioButton2)
          ├── group.findViewById(R.id.radioButton2) → RadioButton
          └── Toast "Radio button clicked Second Option"

THE USER OPENS THE KEYBOARD
  adjustResize no longer resizes the window (edge-to-edge, API 30+)
    └── the IME is NOT compensated (the listener handles only systemBars)
          └── the bottom widgets can be covered

ROTATING THE SCREEN
  onDestroy → onCreate(savedInstanceState ≠ null)
    ├── binding = ActivityMainBinding.inflate(...)   → new object
    ├── setContentView(binding.getRoot())            → new tree
    ├── the 7 listeners register again
    └── the state of the widgets with android:id is restored automatically
          ├── the text in the EditTexts
          ├── the check in Switch / CheckBox / ToggleButton
          ├── the progress in SeekBar
          └── the value in RatingBar
```

**Why the state is restored without code:** `Activity.onSaveInstanceState` saves the view hierarchy automatically, and each `View` with an `android:id` saves its own state. That is why all the widgets in DMA05 have IDs — not just for `binding`, but also for surviving rotation.

**What is not saved:** the Toasts (they disappear) and any value that is not widget state — for example a counter kept in a field of the activity. For those you need your own `onSaveInstanceState`.

**Why the listeners register again:** on rotation, the old tree is destroyed and a new one is built. The listeners were attached to the old views, which no longer exist. `onCreate` runs again and attaches them to the new views.

**What happens to `binding` on rotation:** the field is reassigned. The old binding becomes eligible for garbage collection together with the old tree. No reference to it remains, because the old activity is destroyed.

---

## 27.6 What to remember

### The file table

| File | The essence |
|---|---|
| `MainActivity.java` | `inflate` → `getRoot` → insets → 7 listeners; a single `findViewById`, on the group, for `checkedId` |
| `activity_main.xml` | vertical `LinearLayout`, 14 children, 17 IDs, each input widget once |
| `AndroidManifest.xml` | no `package` (it comes from `namespace`), `exported="true"`, `adjustResize`, `NoActionBar` theme |
| `build.gradle.kts` | `namespace` + `buildFeatures { viewBinding = true }` — the only lines that show up in the code |

### The five real pitfalls

| # | Pitfall | The symptom |
|---|---|---|
| 1 | `setContentView(R.layout.activity_main)` left next to the binding | two trees; the listeners on the invisible one; the app seems dead |
| 2 | `setPadding` on the root without adding the padding from the XML | the original padding disappears |
| 3 | `checkedId == -1` on `RadioGroup` | `findViewById(-1)` → `null` → NPE at `getText()` |
| 4 | a Toast on every `onProgressChanged` | tens of Toasts queued on a single drag |
| 5 | `LinearLayout` without a `ScrollView` | on small screens, the `RatingBar` goes outside the visible area |

### What you must be able to say without looking

1. **`ActivityMainBinding.inflate(getLayoutInflater())`** builds the tree and fills the fields. **`setContentView(binding.getRoot())`** puts it on screen. In that order.
2. **Insets on `getRoot()`** because padding on the root moves all the children into the safe area.
3. **One method → lambda. Three methods → anonymous class.** `SeekBar` is the only one with three.
4. **`MainActivity.this`** is mandatory in the anonymous class, useless in the lambda.
5. **`checkedId` is an ID, not an index** — that is why `group.findViewById(checkedId)`.
6. **`CompoundButton`** is the base class for `Switch`, `CheckBox`, `ToggleButton` — that is why the same listener signature for all three.
7. **`inputType` chooses the keyboard and filters the characters, but does not validate.**
8. **`Toast.makeText(...)` without `.show()`** displays nothing and gives no error — the quietest mistake in the file.
9. **`ViewBinding` is generated at build**, not at runtime: if you add an ID and do not run the build, the field does not exist.
10. **`binding` is a field**, so that it survives between methods and is reassigned on rotation.

### The diagrams, in one sentence each

| Diagram | What it says |
|---|---|
| 1. the tree + the fields | `inflate` turns XML into objects and, in the same step, fills the fields by `android:id` |
| 2. `binding.button` | resolving an ID goes through `R.id` at build and becomes a field read at runtime |
| 3. the two-step flow | `inflate` builds the tree, `setContentView` attaches it to the window |
| 4. padding on the root vs the child | padding on the root moves all the children; on a child, only that child |
| 5. lambda vs anonymous class | the number of abstract methods decides the style, not preference |
| 6. `findViewById` vs `binding.button` | an O(n) lookup in the tree vs an O(1) field read |

---

## Chapter 27 summary

- `ViewBinding` generates `ActivityMainBinding` from `activity_main.xml`: 17 fields, one per `android:id`.
- `inflate(getLayoutInflater())` → `setContentView(binding.getRoot())` replaces `setContentView(R.layout...)` + `findViewById`.
- The insets are applied on `binding.getRoot()`, never on a child.
- Seven widget listeners, five interfaces: `View.OnClickListener`, `CompoundButton.OnCheckedChangeListener` (×3), `RadioGroup.OnCheckedChangeListener`, `SeekBar.OnSeekBarChangeListener`, `RatingBar.OnRatingBarChangeListener` — plus the insets listener, which is not on a widget.
- Lambda for single-method interfaces; anonymous class for `SeekBar`, which has three.
- `RadioGroup` enforces mutual exclusion; `checkedId` is a resource ID, not a position.
- `inputType` changes the keyboard and filters, but validates nothing.
- `progressBar` and `imageView` are in the layout, but untouched in the code — inventory, not functionality.
- `Toast.makeText(...).show()` — without `.show()`, nothing appears and no error warns you.

**Back to** [cheatsheet](21%20-%20Cheatsheet.md) **or to** [chapter 13 — DMA05: ViewBinding](13%20-%20DMA05%20-%20ViewBinding.md).
