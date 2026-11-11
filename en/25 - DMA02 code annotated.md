# Chapter 25 — The DMA02 code, annotated

**Objective:** to read the first lab project line by line — the `Application` class, the complete lifecycle, `DynamicColors` and an implicit `Intent` — with explanations for every block: what it does, why it is there, what breaks if you delete it.

**Source:** `DMA02/` at commit `d719ffc` (2026-11-09, "G1097_S07") — 4 files, 199 lines of code: `DMA02App.java` (62), `MainActivity.java` (64), `AndroidManifest.xml` (35), `activity_main.xml` (38).

**How to read this chapter.** Each file has, in order:

1. a **file header** (`/* ... */` in Java, `<!-- ... -->` in XML) — what it is, why it exists, what breaks without it;
2. a **THEORY BLOCK** before the class or the main node — the general rule behind the code;
3. **the code annotated line by line** — every line has a reason, and every method has a `THEORY / LOGIC / REF / RISK` block;
4. a **pitfalls** section and a **table of what breaks** if you delete each thing.

The added comments use four prefixes:

| Prefix | What it means |
|---|---|
| `THEORY:` | the rule behind the line — what the framework guarantees |
| `LOGIC:` | the concrete, numbered steps that the code executes |
| `REF:` | where the claim is verified (the Android 36 source, manifest, layout, `build.gradle.kts`) |
| `RISK:` | what breaks if the line is missing or changed |

> **Golden rule:** the code tokens are identical to the ones in the repo. Everything written after `//` or between `<!-- -->` was added for study. The comments do not change compilation and do not change behavior.

---

## 25.0 Project map

```
DMA02/
└── src/main/
    ├── AndroidManifest.xml              ← the contract with the system: 35 lines
    ├── java/ro/ase/ie/dma02/
    │   ├── DMA02App.java                ← Application + 7 callbacks: 62 lines
    │   └── MainActivity.java            ← 6 lifecycle methods + pressMe: 64 lines
    └── res/
        ├── layout/activity_main.xml     ← toolbar + text + button: 38 lines
        ├── values/themes.xml            ← the theme in light mode
        └── values-night/themes.xml      ← the theme in night mode
```

| File | Role | Without it |
|---|---|---|
| `DMA02App.java` | the single object of the process; subscription to the lifecycle; Material You | the manifest has nothing to instantiate: no error, just silence |
| `MainActivity.java` | the only activity; logs the lifecycle; launches the share sheet | the launcher has nothing to start: `ActivityNotFoundException` |
| `AndroidManifest.xml` | binds the classes to the system; declares the `Intent` filters | the APK does not install or the app does not appear in the launcher |
| `activity_main.xml` | the view tree of the screen | `R.layout.activity_main` does not exist: the build fails |

**The two worlds of the project:**

```
   JAVA CODE                           MANIFEST                         SYSTEM
   ─────────                           ────────                         ──────
   DMA02App      ── android:name ────► <application>  ◄── instantiates ─ ActivityThread
   MainActivity  ── android:name ────► <activity>     ◄── starts ─────── launcher
   pressMe       ── ACTION_SEND ─────► <intent-filter> ◄── resolves ──── PackageManager
   R.layout.activity_main ◄── name ─── activity       ◄── inflates ───── LayoutInflater
```

Without the arrow from the manifest, the classes exist only in the code: they compile, but they are never created. It is the first pitfall of the project and the hardest to track down, because it produces no error.

---

## 25.1 `DMA02App.java` — the `Application` class

### 25.1.1 The complete file, annotated

```java
/*
 * ======================================================================================
 * DMA02App.java — THE `Application` CLASS OF THE DMA02 PROJECT
 * ======================================================================================
 * WHAT IT IS:
 *   The class that becomes the single object of the Android process. The framework
 *   instantiates it once, at process start, BEFORE any activity.
 *
 * WHY IT EXISTS:
 *   1. It subscribes an observer to the lifecycle of ALL activities
 *      (`registerActivityLifecycleCallbacks`).
 *   2. It enables Material You globally (`DynamicColors.applyToActivitiesIfAvailable`).
 *   3. It writes the first Logcat message, as proof that global initialization ran.
 *
 * WHAT BREAKS WITHOUT IT:
 *   - without `android:name=".DMA02App"` in the manifest, the class is NOT instantiated:
 *     no error, no message — just silence in Logcat;
 *   - without `implements ActivityLifecycleCallbacks`, you receive no event at all;
 *   - without `DynamicColors`, the app stays on the fixed palette from `themes.xml`.
 *
 * THE ORDER, IN SHORT:
 *   new process → Application.attachBaseContext() → ContentProvider.onCreate()
 *              → DMA02App.onCreate() → MainActivity.onCreate() → onStart() → onResume()
 *
 * REF: android.app.Application (Android 36), the class documentation:
 *      "The Application class, or your subclass of the Application class, is
 *       instantiated before any other class when the process for your
 *       application/package is created."
 * ======================================================================================
 */

package ro.ase.ie.dma02;                    // the application package; identical to `namespace` in build.gradle.kts

import android.app.Activity;                // the type received by every callback: the observed activity
import android.app.Application;             // the base class — the single object of the process
import android.os.Bundle;                   // the saved state, received by two of the callbacks
import android.util.Log;                    // writing to Logcat

import androidx.annotation.NonNull;         // lint contract: the parameter must not be null
import androidx.annotation.Nullable;        // lint contract: the parameter may be null

import com.google.android.material.color.DynamicColors;   // Material You: colors extracted from the wallpaper

/*
 * ======================================================================================
 * THEORY BLOCK: `Application` — the single object of the process
 * ======================================================================================
 * 1. ONE PROCESS = ONE `Application`
 *    Android starts the app in a new process (by default). At the start of the process,
 *    `ActivityThread` creates EXACTLY ONE `Application` object. All activities,
 *    services and receivers in that process share it.
 *    Consequence: the fields of `Application` are "global" to the process, not to an
 *    activity. They are not reset on rotation and not recreated on navigation.
 *
 * 2. `Application` IS NOT AN ACTIVITY
 *    It has no window, no layout, it does not appear on screen. It is only an
 *    initialization point and a place for global state. That is why its `onCreate()`
 *    has no `setContentView` and receives no `Bundle`: it has no state to restore.
 *
 * 3. `onCreate()` — A SINGLE CALL, BEFORE ANY ACTIVITY
 *    The framework documentation: "Called when the application is starting, before any
 *    activity, service, or receiver objects (excluding content providers) have been
 *    created." So: content providers may be created before it, nothing else.
 *
 * 4. `ActivityLifecycleCallbacks` — THE OBSERVER PATTERN
 *    `Application` keeps a list of observers. Every lifecycle method of an activity
 *    calls, inside itself, `Application.dispatchActivityX(...)`, which iterates the
 *    list. By registering `this`, `DMA02App` receives events from ALL activities,
 *    without writing anything in them.
 *
 * 5. `DynamicColors` — MATERIAL YOU, GLOBAL
 *    `applyToActivitiesIfAvailable(this)` registers its own observer and applies a
 *    theme overlay to every activity, before `onCreate`. One single call, an effect
 *    across the whole app.
 *
 * ASCII: WHO IS CREATED FIRST
 *
 *   Zygote ──fork()──► new process
 *                         │
 *                         ├─ 1. Application.attachBaseContext()   (not in the code)
 *                         ├─ 2. ContentProvider.onCreate()        (if any)
 *                         ├─ 3. DMA02App.onCreate()               ◄── HERE
 *                         │       ├─ super.onCreate()
 *                         │       ├─ registerActivityLifecycleCallbacks(this)
 *                         │       ├─ DynamicColors.applyToActivitiesIfAvailable(this)
 *                         │       └─ Log.w(TAG, "onCreate")
 *                         └─ 4. MainActivity.onCreate()           ◄── only now
 * ======================================================================================
 */
public class DMA02App
        extends Application                                       // (1) DMA02App IS an Application
        implements Application.ActivityLifecycleCallbacks {       // (2) and IS the lifecycle observer

    // The Logcat tag. `getSimpleName()` returns "DMA02App", without the package.
    // `getName()` would have given "ro.ase.ie.dma02.DMA02App" — too long for a column.
    // It is not `static`: Application has a single instance per process, so an
    // instance field is enough. In MainActivity it is `static final`, because there
    // several instances may exist (on rotation) and the tag must belong to the class.
    private final String TAG = DMA02App.class.getSimpleName();

    // ==================================================================================
    // METHOD 1/8: onCreate() — THE ENTRY POINT OF THE PROCESS
    // ==================================================================================
    // THEORY: `Application.onCreate()` is called once, at process start, before any
    //         activity. It is the right place for global initializations:
    //         subscriptions, themes, libraries, DI.
    // LOGIC:
    //   1. `super.onCreate()` — the base class contract.
    //   2. `registerActivityLifecycleCallbacks(this)` — subscribing the observer.
    //   3. `DynamicColors.applyToActivitiesIfAvailable(this)` — the global theme.
    //   4. `Log.w(...)` — the proof that initialization has finished.
    // REF: android.app.Application#onCreate (Android 36); the class javadoc.
    // RISK: the order 2 → 3 → 4 is not accidental. The subscription and the theme must
    //       be done BEFORE the first activity is created; if you move them into
    //       MainActivity, they run too late for the first activity.
    @Override
    public void onCreate() {
        super.onCreate();                                  // step 0: the base class contract (empty here, but kept)
        registerActivityLifecycleCallbacks(this);          // step 1: "this" becomes the observer of all activities
        DynamicColors.applyToActivitiesIfAvailable(this);  // step 2: Material You, global, if available

        Log.w(TAG, "onCreate");                            // step 3: the first line in Logcat — before any activity
    }

    // ==================================================================================
    // CALLBACK 1/7: onActivityCreated(Activity, Bundle)
    // ==================================================================================
    // THEORY: it fires when an activity calls `super.onCreate(...)`.
    //         `bundle` is exactly `savedInstanceState`: `null` on first creation,
    //         non-null on recreation (rotation, return after a kill).
    // WHEN: inside `Activity.onCreate`, after `mFragments.dispatchCreate()`
    //       and before `mCalled = true`.
    // LOGIC: writes a single line in Logcat, with the activity's class name.
    // REF: Activity.java (android-36), line 1883 — `dispatchActivityCreated(...)`.
    // RISK: at this moment `setContentView` has NOT run yet (if the activity calls
    //       `super` first, as MainActivity does). So `findViewById` would return null:
    //       do not touch the views here.
    @Override
    public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
        Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());   // e.g. "onActivityCreatedMainActivity"
    }                                                                            // the space between text and name is missing

    // ==================================================================================
    // CALLBACK 2/7: onActivityDestroyed(Activity) — position 2 in the file, not in life
    // ==================================================================================
    // THEORY: it fires when the activity is definitively destroyed: Back, rotation,
    //         `finish()`. It is the counterpart of `onDestroy`.
    // WHEN: inside `Activity.onDestroy`, after the framework's cleanup.
    // LOGIC: writes a single line in Logcat.
    // REF: Activity.java (android-36), line 2971 — `dispatchActivityDestroyed()`.
    // RISK: it is NOT guaranteed. If the system kills the process for lack of memory,
    //       `onDestroy` does not run and the callback never comes. Do not save data here.
    @Override
    public void onActivityDestroyed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityDestroyed" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 3/7: onActivityPaused(Activity)
    // ==================================================================================
    // THEORY: it fires when the activity loses focus: another activity comes over it,
    //         a dialog, the share sheet, Home. The activity may still be visible.
    // WHEN: at the start of `Activity.onPause`, BEFORE the rest of the method body.
    // LOGIC: writes a single line in Logcat.
    // REF: Activity.java (android-36), line 2662 — `dispatchActivityPaused()`.
    // RISK: `onPause` blocks the transition to the next activity. Whatever you do here
    //       delays the next screen: keep the method short.
    @Override
    public void onActivityPaused(@NonNull Activity activity) {
        Log.w(TAG, "onActivityPaused" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 4/7: onActivityResumed(Activity)
    // ==================================================================================
    // THEORY: it fires when the activity becomes interactive: it is in the foreground
    //         and receives input. It is the counterpart of `onResume`.
    // WHEN: at the start of `Activity.onResume`, before the rest of the body.
    // LOGIC: writes a single line in Logcat.
    // REF: Activity.java (android-36), line 2228 — `dispatchActivityResumed()`.
    // RISK: here you may start animations and listeners; do not do heavy work, because
    //       it delays the first interactive frame.
    @Override
    public void onActivityResumed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityResumed" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 5/7: onActivitySaveInstanceState(Activity, Bundle)
    // ==================================================================================
    // THEORY: it fires when the system asks the activity to save its state, so that it
    //         can rebuild it after the process is killed. `bundle` is exactly the
    //         object that will reach `onCreate` on return.
    // WHEN: inside `Activity.onSaveInstanceState`. From Android 9 (API 28), after
    //       `onStop`; before that, it could come before `onStop`.
    // LOGIC: none — the method is empty on purpose.
    // REF: Activity.java (android-36), line 2565 — `dispatchActivitySaveInstanceState(...)`.
    // RISK: the Bundle travels through Binder; large data gives `TransactionTooLargeException`.
    //       DMA02 has no state to save, so the method stays empty.
    @Override
    public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {

    }

    // ==================================================================================
    // CALLBACK 6/7: onActivityStarted(Activity)
    // ==================================================================================
    // THEORY: it fires when the activity becomes visible, but not necessarily
    //         interactive. It is the counterpart of `onStart`.
    // WHEN: inside `Activity.onStart`, after `mFragments.doLoaderStart()`.
    // LOGIC: writes a single line in Logcat.
    // REF: Activity.java (android-36), line 2154 — `dispatchActivityStarted()`.
    // RISK: here the activity is visible, but does not receive input yet. Do not start
    //       animations that depend on focus.
    @Override
    public void onActivityStarted(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStarted" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 7/7: onActivityStopped(Activity)
    // ==================================================================================
    // THEORY: it fires when the activity is no longer visible: Home, another
    //         full-screen activity, screen off. It is the counterpart of `onStop`.
    // WHEN: inside `Activity.onStop`, after `mActivityTransitionState.onStop`.
    // LOGIC: writes a single line in Logcat.
    // REF: Activity.java (android-36), line 2893 — `dispatchActivityStopped()`.
    // RISK: the activity may be destroyed right after, without a guaranteed `onDestroy`.
    //       Do not keep here resources that must be released no matter what.
    @Override
    public void onActivityStopped(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStopped" + activity.getClass().getSimpleName());
    }
}   // closes the DMA02App class
```

### 25.1.2 Why `Application` exists and why it runs before any activity

Android does not start the "app" as a monolithic process. It starts a **Linux process** and, inside it, a **main thread** (`ActivityThread`). At the start of that thread, the framework builds a single `Application` object, then, at the launcher's request, it builds the first activity. The order is not a style convention: it is imposed by `ActivityThread.handleBindApplication()`.

```
ActivityThread.handleBindApplication()
  │
  ├─ 1. makeApplication(...)                 ← creates the instance of the class from android:name
  │       └─ DMA02App()                      ← the constructor (we do not write it)
  │
  ├─ 2. app.attachBaseContext(context)       ← the base Context
  │
  ├─ 3. installContentProviders(...)         ← providers: BEFORE Application.onCreate
  │       └─ ContentProvider.onCreate()
  │
  ├─ 4. mInstrumentation.callApplicationOnCreate(app)
  │       └─ DMA02App.onCreate()             ◄── subscription + DynamicColors + first log
  │
  └─ 5. the message loop of the main thread  ← only now can activity requests arrive
          └─ launchActivity(...) → MainActivity
```

**Why not a `static` block:** a `static { ... }` block runs when the class is loaded, which can be triggered by any code, at any time, and it has no guaranteed `Context`. `Application.onCreate` runs exactly once per process, before any component, and receives a valid `Context`. It is the only place where you can register `ActivityLifecycleCallbacks` **before** the first activity exists.

**Why not in `MainActivity.onCreate`:** you would lose exactly the first event — `onActivityCreated` for `MainActivity` itself — and you would repeat the code in every activity. In DMA02 there is a single activity, so the difference is small; in `G1097` (two activities) it becomes visible.

**`Application` has no UI:** it has no window, no `setContentView`, it does not appear in recents. It is only a process object. That is why its `onCreate()` receives no `Bundle`: it has no state to restore.

> **Do not put cleanup in `onTerminate()`.** The method exists, but the documentation says it is called only in emulated environments; on a real device, the process is simply killed, without your code running.

### 25.1.3 The exact order: `Application.onCreate` → `Activity.onCreate` → `onStart` → `onResume`

```
TIME ─────────────────────────────────────────────────────────────────────────────►

DMA02App.onCreate()
  │  super.onCreate()
  │  registerActivityLifecycleCallbacks(this)
  │  DynamicColors.applyToActivitiesIfAvailable(this)
  │  Log.w("DMA02App", "onCreate")
  ▼
MainActivity.onCreate(savedInstanceState)
  │  super.onCreate(savedInstanceState)
  │    └─ Application.dispatchActivityCreated(this, savedInstanceState)
  │         └─ DMA02App.onActivityCreated(activity, bundle)      → log "onActivityCreatedMainActivity"
  │  setContentView(R.layout.activity_main)
  │  Log.w("MainActivity", "onCreate")                            → log "onCreate"
  ▼
MainActivity.onStart()
  │  super.onStart()
  │    └─ Application.dispatchActivityStarted(this)
  │         └─ DMA02App.onActivityStarted(activity)               → log "onActivityStartedMainActivity"
  │  Log.w("MainActivity", "onStart")                             → log "onStart"
  ▼
MainActivity.onResume()
  │  super.onResume()
  │    └─ Application.dispatchActivityResumed(this)               ← at the START of onResume
  │         └─ DMA02App.onActivityResumed(activity)               → log "onActivityResumedMainActivity"
  │  Log.w("MainActivity", "onResume")                            → log "onResume"
  ▼
THE SCREEN IS VISIBLE AND INTERACTIVE
```

**Why the log from `Application` appears first:** because `MainActivity` calls `super.onX()` **first**, and the dispatch to `Application` happens **inside** `super.onX()`. The order in Logcat does not say "the callback runs before the method", but "your log runs after `super`".

> If you wrote `Log.w(...)` **before** `super.onStart()`, the order would reverse: `MainActivity: onStart` would appear first, then `DMA02App: onActivityStartedMainActivity`. Same method, different order — only from the position of `super`.

**What you see in Logcat on a full start:**

```
DMA02App:      onCreate
DMA02App:      onActivityCreatedMainActivity
MainActivity:  onCreate
DMA02App:      onActivityStartedMainActivity
MainActivity:  onStart
DMA02App:      onActivityResumedMainActivity
MainActivity:  onResume
```

**What you see on exit (Home, then Back):**

```
DMA02App:      onActivityPausedMainActivity
MainActivity:  onPause
DMA02App:      onActivityStoppedMainActivity
MainActivity:  onStop
DMA02App:      onActivityDestroyedMainActivity
MainActivity:  onDestroy
```

### 25.1.4 What `registerActivityLifecycleCallbacks` observes

```
Application
  └─ mActivityLifecycleCallbacks : ArrayList<ActivityLifecycleCallbacks>
        └─ [0] DMA02App          ← registered by `registerActivityLifecycleCallbacks(this)`

Activity.onCreate()
  └─ super.onCreate()
       └─ getApplication().dispatchActivityCreated(this, bundle)
            └─ for (cb : mActivityLifecycleCallbacks)
                   cb.onActivityCreated(this, bundle)
                     └─ DMA02App.onActivityCreated(...) → Log.w(...)
```

The observer receives the **instance** of the activity, not just its name. That is why in `Application` you can do things that depend on the current activity — for example, mark in analytics which screen was opened — without the activity knowing it is being observed.

**The seven methods, in short:**

| # | Callback | Triggered from | When | What you can do there |
|---|---|---|---|---|
| 1 | `onActivityCreated(activity, bundle)` | `Activity.onCreate` | on creation; `bundle` = `savedInstanceState` | initializations that depend on the activity, but **not** views |
| 2 | `onActivityStarted(activity)` | `Activity.onStart` | the activity becomes visible | starting visual resources |
| 3 | `onActivityResumed(activity)` | `Activity.onResume` | the activity becomes interactive | listeners, animations, "screen view" analytics |
| 4 | `onActivityPaused(activity)` | `Activity.onPause` | loses focus | stopping listeners, quick saving |
| 5 | `onActivityStopped(activity)` | `Activity.onStop` | no longer visible | releasing heavy resources |
| 6 | `onActivitySaveInstanceState(activity, bundle)` | `Activity.onSaveInstanceState` | the system asks for the state | small, serializable data |
| 7 | `onActivityDestroyed(activity)` | `Activity.onDestroy` | definitive destruction | final cleanup (if it gets the chance) |

**Why all seven:** the interface has seven **abstract** methods. You cannot implement only half: if you delete a method, the project **does not compile** (`DMA02App is not abstract and does not override abstract method ...`). That is why `onActivitySaveInstanceState` exists even though it does nothing.

> Since API 29, the interface also has `default` methods for the "pre" and "post" moments (`onActivityPreCreated`, `onActivityPostResumed` etc.). Those have an empty default implementation, so you are not required to override them. The seven in the table are the only abstract ones.

**Why the order in the file is not the execution order:** the methods appear alphabetically — `onActivityCreated`, `onActivityDestroyed`, `onActivityPaused`, `onActivityResumed`, `onActivitySaveInstanceState`, `onActivityStarted`, `onActivityStopped`. IntelliJ generates the implementations in alphabetical order, not in lifecycle order. The basic order is `Created → Started → Resumed → Paused → Stopped → Destroyed`; `SaveInstanceState` is interleaved before destruction (after `Stopped` on API 28+).

### 25.1.5 `android:name=".DMA02App"` — the only line that binds the class to the runtime

```
AndroidManifest.xml                         Runtime
───────────────────                         ───────
android:name=".DMA02App"   ─────────────►   ro.ase.ie.dma02.DMA02App
                                            (the dot = relative to `namespace`)

missing                    ─────────────►   android.app.Application
                                            (your class is NOT instantiated: silence)

wrong name                 ─────────────►   ClassNotFoundException at start
```

**Why the dot:** in the manifest, a name that starts with `.` is relative to the application package. Here `namespace = "ro.ase.ie.dma02"` in `build.gradle.kts`, so `.DMA02App` means `ro.ase.ie.dma02.DMA02App`. You can also write the full name, without the dot; both are equivalent.

**What happens if you forget the line:** Android uses the default `android.app.Application`. `DMA02App` is never created, so `onCreate()` does not run, the callbacks are not registered, `DynamicColors` is not applied and the first log does not appear. The app looks and works identically. **No error. Just silence.** It is the classic pitfall of the lab: you think you wrote the code, but the code does not run.

**What happens if the name is wrong:** at start, `ActivityThread` tries to instantiate the class and fails with `Unable to instantiate application ro.ase.ie.dma02.DMA02App: java.lang.ClassNotFoundException`. Here the error is loud, so it is easier to find than the missing line.

### 25.1.6 `DynamicColors.applyToActivitiesIfAvailable` — Material You

**What Material You does:** from Android 12 (API 31), the system extracts a palette from the wallpaper and exposes it as system resources: `system_accent1_*`, `system_accent2_*`, `system_neutral1_*`, `system_neutral2_*`. Material Components maps them onto the theme roles — `colorPrimary`, `colorOnPrimary`, `colorSurface` etc. — through a **theme overlay**. The result: the app picks up the wallpaper colors, without you writing a single color.

```
WALLPAPER
   │  (Android 12+, API 31+)
   ▼
The system palette: system_accent1_100 ... system_neutral2_900
   │
   ▼
DynamicColors.applyToActivitiesIfAvailable(app)
   │  registers its own ActivityLifecycleCallbacks
   ▼
onActivityPreCreated(activity)          ← before Activity.onCreate
   │  activity.getTheme().applyStyle(ThemeOverlay_Material3_DynamicColors_*, true)
   ▼
colorPrimary / colorSurface / ... come from the wallpaper
```

**Why a single call is enough:** the method does not apply the theme to a single activity. It registers an observer on `Application` — exactly the mechanism from 25.1.4 — and applies the overlay in `onActivityPreCreated`, that is **before** each activity resolves its theme. That is why the call sits in `Application.onCreate`: it catches all activities, including the first.

**Why it is a no-op below API 31:** the `system_accent1_*` resources do not exist before Android 12. The library checks `Build.VERSION.SDK_INT >= 31` and, if it is not met, registers nothing. It does not crash, it does not log an error — it simply does nothing, and the theme stays the one from `themes.xml`.

> **In DMA02, `minSdk = 33`.** The app cannot be installed on a device below Android 13, so any device it runs on has API ≥ 33, that is above the threshold of 31. In practice, here `DynamicColors` always applies. The no-op remains a theoretical notion useful for the exam question, not a real case of the project.

**The additional condition:** the overlay applied is a Material3 one. If the activity theme does not descend from `Theme.Material3`, there is no matching overlay and nothing changes. Here the theme is `Theme.DMA02` → `Base.Theme.DMA02` → `Theme.Material3.Dark` / `Theme.Material3.DayNight.NoActionBar`, so the condition is met.

### 25.1.7 `Log.w` vs `Log.d` — why a warning

The levels in `android.util.Log`, in increasing order:

| Level | Method | Value | When it appears in Logcat |
|---|---|---|---|
| VERBOSE | `Log.v` | 2 | only with the "Verbose" filter |
| DEBUG | `Log.d` | 3 | with the "Debug" filter or lower |
| INFO | `Log.i` | 4 | with the "Info" filter or lower |
| WARN | `Log.w` | 5 | with the "Warn" filter or lower |
| ERROR | `Log.e` | 6 | with the "Error" filter or lower |

Logcat shows the messages with a level **≥** the chosen filter. So:

- if you filter at **Info**, `Log.d` disappears, while `Log.w` remains;
- if you filter at **Warn**, only `Log.w` and `Log.e` remain;
- `Log.w` is conventionally shown in yellow, which makes it easy to find in a long list.

**Why `w` in the lab:** for visibility, not because something would be wrong. The messages are demonstrations, and `w` survives more aggressive filters than `d`. In addition, `d` is the level most often removed in release builds, through R8 rules of the `-assumenosideeffects` kind; the project has no such rules, but the convention remains.

> **Do not confuse the level with the tag.** `Log.w(TAG, "onCreate")` has two arguments: the first is the tag (`DMA02App` or `MainActivity`), the second is the message. In Logcat, the two columns are seen separately: `DMA02App: onCreate` means tag `DMA02App`, message `onCreate`.

### 25.1.8 What breaks if you delete each line from `DMA02App`

| Deleted line | Effect |
|---|---|
| `extends Application` | at start: `ClassCastException` — the manifest asks for a class that is not an `Application` |
| `implements Application.ActivityLifecycleCallbacks` | `registerActivityLifecycleCallbacks(this)` no longer compiles: `this` does not have the required type |
| `private final String TAG = ...` | does not compile: `TAG` no longer exists in the 8 methods |
| `super.onCreate()` | in `Application` the base is empty, so nothing visible; it breaks the contract, though, and it is dangerous if the chain changes |
| `registerActivityLifecycleCallbacks(this)` | no error, no `onActivity*` message in Logcat — the app looks identical |
| `DynamicColors.applyToActivitiesIfAvailable(this)` | the fixed palette from `themes.xml`; on Android 12+ the app no longer follows the wallpaper |
| `Log.w(TAG, "onCreate")` | nothing functional; only the first line in Logcat disappears |
| a callback method | does not compile: the interface has seven abstract methods |
| `@Override` | it compiles, but a name mistake becomes a new method, ignored by the framework |

### 25.1.9 Where the claims are verified

All the claims about the callback order can be verified in the Android source installed locally, in `$ANDROID_HOME/sources/android-36/android/app/Activity.java`. The search command is `grep -n "dispatchActivity" "$ANDROID_HOME/sources/android-36/android/app/Activity.java"`.

| Claim | The line in `Activity.java` (android-36) |
|---|---|
| `dispatchActivityCreated` is in `onCreate` | 1883 |
| `dispatchActivityStarted` is in `onStart` | 2154 |
| `dispatchActivityResumed` is in `onResume` | 2228 |
| `dispatchActivityPaused` is in `onPause` | 2662 |
| `dispatchActivityStopped` is in `onStop` | 2893 |
| `dispatchActivitySaveInstanceState` is in `onSaveInstanceState` | 2565 |
| `dispatchActivityDestroyed` is in `onDestroy` | 2971 |

> The line numbers are for `android-36`; in other SDK versions they may differ by a few lines. The method and the order stay the same. What matters for the exam: each dispatch is **inside** the method with the same name, not in a separate `performX()`.

### 25.1.10 `Application` vs `Activity` vs `Service`

| Criterion | `Application` | `Activity` | `Service` |
|---|---|---|---|
| Instances per process | exactly 1 | 0..n | 0..n |
| Has UI | no | yes | no |
| Lifecycle | `onCreate` → `onTerminate` (irrelevant) | 6 methods + `onRestart` | `onCreate` → `onStartCommand` → `onDestroy` |
| Role in DMA02 | global initialization | the screen | does not exist |
| Receives `Bundle` | no | yes, in `onCreate` | no |

**Why `Application` has no `onStart`/`onResume`:** it has no window and does not compete with other apps for the foreground. It exists as long as the process exists.

---

## 25.2 `MainActivity.java` — the lifecycle

### 25.2.1 The complete file, annotated

```java
/*
 * ======================================================================================
 * MainActivity.java — THE ONLY ACTIVITY OF THE DMA02 PROJECT
 * ======================================================================================
 * WHAT IT IS:
 *   The activity that appears in the launcher and owns the screen from `activity_main.xml`.
 *   It extends `AppCompatActivity`, not `Activity`: it needs the Material3/AppCompat theme.
 *
 * WHY IT EXISTS:
 *   1. It demonstrates the lifecycle: six overridden methods, each one only logs.
 *   2. It binds the layout to the code: `setContentView(R.layout.activity_main)`.
 *   3. It demonstrates an implicit `Intent`: `pressMe` opens the share sheet.
 *
 * WHAT BREAKS WITHOUT IT:
 *   - without `setContentView`, the screen stays empty and `findViewById` returns null;
 *   - without `super.onCreate`, the framework throws `SuperNotCalledException`;
 *   - without `pressMe`, `android:onClick` crashes on click, not at compile time.
 *
 * REF: android.app.Activity (Android 36); AppCompatActivity (androidx.appcompat).
 * ======================================================================================
 */

package ro.ase.ie.dma02;                             // the same package as DMA02App

import android.content.Intent;                       // used only in pressMe
import android.os.Bundle;                            // the parameter of onCreate
import android.util.Log;                             // writing to Logcat
import android.view.View;                            // the parameter of pressMe — required by android:onClick

import androidx.appcompat.app.AppCompatActivity;     // the AppCompat variant of Activity

/*
 * ======================================================================================
 * THEORY BLOCK: the lifecycle of an activity
 * ======================================================================================
 * 1. WHAT AN ACTIVITY IS
 *    A component with a window. The system creates it, shows it, hides it and
 *    destroys it by fixed rules. You do not call `onCreate`; the framework calls it.
 *
 * 2. THE SEVEN STATES (six methods + onRestart)
 *    onCreate → onStart → onResume → onPause → onStop → onDestroy
 *    `onRestart` appears only when returning from `onStop`.
 *
 * 3. `super` IS MANDATORY
 *    `ActivityThread` checks after every method whether you called `super`. If not,
 *    it throws `SuperNotCalledException`. It is not a convention, it is a runtime check.
 *
 * 4. `AppCompatActivity` vs `Activity`
 *    `AppCompatActivity` brings the AppCompat backport: compatible inflation, Material
 *    themes on old versions, `AppCompatDelegate` for dark mode. It requires a theme
 *    that descends from `Theme.AppCompat` (here: `Theme.Material3.*`).
 *
 * 5. THE ORDER IN THE FILE IS NOT THE EXECUTION ORDER
 *    The methods are in alphabetical order (generated by IntelliJ), not chronological.
 *
 * ASCII: THE COMPLETE CYCLE
 *
 *   onCreate ──► onStart ──► onResume ──► [visible, interactive]
 *                                            │
 *                          Home / another activity
 *                                            ▼
 *                                        onPause ──► onStop ──► [hidden]
 *                                                          │
 *                                        return ──► onRestart ──► onStart ──► onResume
 *                                                          │
 *                                        Back ──► onDestroy
 * ======================================================================================
 */
public class MainActivity extends AppCompatActivity {   // (1) an activity with AppCompat support

    // The Logcat tag: "MainActivity".
    // `static final` = it belongs to the class, not to the instance. On rotation a new
    // instance is created, but the tag stays the same — exactly what you want in Logcat.
    private static final String TAG = MainActivity.class.getSimpleName();

    // ==================================================================================
    // METHOD 1/7: onCreate(Bundle) — CONSTRUCTION
    // ==================================================================================
    // THEORY: the first method of the cycle. Here the layout is inflated and the views
    //         are bound. `savedInstanceState` is null on first creation and non-null
    //         on recreation (rotation, return after a kill).
    // LOGIC:
    //   1. `super.onCreate(...)` — mandatory first.
    //   2. `setContentView(...)` — creates the view tree.
    //   3. `Log.w(...)` — marks the end of construction.
    // REF: Activity.java (android-36), line 1861 — `onCreate`.
    // RISK: without `super`, `SuperNotCalledException`. Without `setContentView`, an empty screen.
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);              // step 1: the framework does its initializations
        setContentView(R.layout.activity_main);          // step 2: the XML becomes a tree of Views
        Log.w(TAG, "onCreate");                          // step 3: the first log of the activity
    }

    // ==================================================================================
    // METHOD 2/7: onDestroy() — DESTRUCTION
    // ==================================================================================
    // THEORY: the last method of the cycle. It appears on Back, on `finish()` or on rotation.
    //         It is NOT guaranteed: if the system kills the process, it does not run.
    // LOGIC: `super` + one line in Logcat.
    // REF: Activity.java (android-36), line 2932 — `onDestroy`.
    // RISK: do not put data saving here — it might not get the chance to run.
    //       For saving there are `onPause` / `onStop` / `onSaveInstanceState`.
    @Override
    protected void onDestroy() {
        super.onDestroy();                              // the framework's cleanup
        Log.w(TAG, "onDestroy");
    }

    // ==================================================================================
    // METHOD 3/7: onStart() — BECOMING VISIBLE
    // ==================================================================================
    // THEORY: the activity becomes visible, but does not receive input yet. It is the
    //         counterpart of `onStop`.
    // LOGIC: `super` + one line in Logcat.
    // REF: Activity.java (android-36), line 2148 — `onStart`.
    // RISK: here you cannot yet assume that the user can press anything.
    @Override
    protected void onStart() {
        super.onStart();                                // the framework makes its transition
        Log.w(TAG, "onStart");
    }

    // ==================================================================================
    // METHOD 4/7: onStop() — HIDING
    // ==================================================================================
    // THEORY: the activity is no longer visible: Home, another full-screen activity,
    //         screen off. It is the counterpart of `onStart`.
    // LOGIC: `super` + one line in Logcat.
    // REF: Activity.java (android-36), line 2889 — `onStop`.
    // RISK: after `onStop`, the activity may be destroyed without a guaranteed `onDestroy`.
    @Override
    protected void onStop() {
        super.onStop();                                 // the framework makes its transition
        Log.w(TAG, "onStop");
    }

    // ==================================================================================
    // METHOD 5/7: onPause() — LOSING FOCUS
    // ==================================================================================
    // THEORY: the activity loses focus: another activity comes over it, a dialog,
    //         the share sheet, Home. It may still be visible.
    // LOGIC: `super` + one line in Logcat.
    // REF: Activity.java (android-36), line 2660 — `onPause`.
    // RISK: `onPause` blocks the transition to the next activity. Whatever you do here
    //       delays the next screen.
    @Override
    protected void onPause() {
        super.onPause();                                // the framework makes its transition
        Log.w(TAG, "onPause");
    }

    // ==================================================================================
    // METHOD 6/7: onResume() — BECOMING INTERACTIVE
    // ==================================================================================
    // THEORY: the activity is in the foreground and receives input. It is the counterpart
    //         of `onPause`.
    // LOGIC: `super` + one line in Logcat.
    // REF: Activity.java (android-36), line 2226 — `onResume`.
    // RISK: here you may start animations and listeners; do not do heavy work, because
    //       it delays the first interactive frame.
    @Override
    protected void onResume() {
        super.onResume();                               // the framework makes its transition
        Log.w(TAG, "onResume");
    }

    // ==================================================================================
    // METHOD 7/7: pressMe(View) — AN IMPLICIT `Intent`
    // ==================================================================================
    // THEORY: `android:onClick="pressMe"` in the layout binds the button to this method
    //         through REFLECTION, not at compile time. The framework looks in the
    //         view's Context for a `public void` method with exactly one `View` parameter.
    // LOGIC:
    //   1. Variant 1 (commented out): ACTION_VIEW + https:// → browser.
    //   2. Variant 2 (commented out): ACTION_DIAL + tel: → phone dialer.
    //   3. Variant 3 (active): ACTION_SEND + text/plain → share sheet.
    // REF: Intent.java, Intent.ACTION_SEND, Intent.createChooser.
    // RISK: `Uri` is NOT imported. If you uncomment the first two variants, the file
    //       does not compile: `cannot find symbol: class Uri`.
    public void pressMe(View view) {                    // the signature is dictated by android:onClick="pressMe"
        // --------------------------------------------------------------------------
        // VARIANT 1 (commented out): opens a URL in the default browser.
        // --------------------------------------------------------------------------
        // `ACTION_VIEW` + `https://` = "show me this thing".
        // It would require `import android.net.Uri;` — that is why the block is commented out.
  /*      Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse("https://developer.android.com"));
        startActivity(web);*/

        // --------------------------------------------------------------------------
        // VARIANT 2 (commented out): opens the phone dialer, without calling.
        // --------------------------------------------------------------------------
        // `ACTION_DIAL` does NOT require the CALL_PHONE permission. The variant that
        // calls, `ACTION_CALL`, would require it.
        /*Intent call = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0212345678"));
        startActivity(call);*/

        // --------------------------------------------------------------------------
        // VARIANT 3 (active): share sheet.
        // --------------------------------------------------------------------------
        Intent share = new Intent(Intent.ACTION_SEND);                  // the action: "send"
        share.setType("text/plain");                                     // MIME: mandatory for resolution
        share.putExtra(Intent.EXTRA_TEXT, "Hello!");                     // the payload
        startActivity(Intent.createChooser(share, "Share via DMA"));     // forced chooser, with a title

    }
}   // closes the MainActivity class
```

### 25.2.2 Why `AppCompatActivity` and not `Activity`

`AppCompatActivity` is the AndroidX variant of `Activity`. It brings back (backports) the AppCompat behavior:

- **compatible inflation** — `AppCompatViewInflater` automatically turns `<TextView>` into `AppCompatTextView` etc., so that it looks the same on all versions;
- **Material themes on old versions** — `Theme.Material3.*` descends from `Theme.AppCompat`, so it needs an AppCompat activity;
- **`AppCompatDelegate`** — dark mode, locale, vector drawables.

> **The reverse pitfall:** if you keep `AppCompatActivity` but change the theme to a platform one (without AppCompat), the app crashes at start with `IllegalStateException: You need to use a Theme.AppCompat theme (or descendant) with this activity.` Here the theme `Theme.DMA02` → `Base.Theme.DMA02` → `Theme.Material3.Dark` / `Theme.Material3.DayNight.NoActionBar` is compatible.

**Why `TAG` is `static final` here, but `private final` in `DMA02App`:** `MainActivity` can have several instances (on rotation, on return), but the tag is the same for all of them — so it belongs to the class. `Application` has a single instance per process, so an instance field is enough. It is a style inconsistency, not a bug.

### 25.2.3 The order in the file vs the execution order

The methods appear in the file in alphabetical order: `onCreate`, `onDestroy`, `onStart`, `onStop`, `onPause`, `onResume`. IntelliJ generates the implementations that way. The real order at runtime is different:

```
start:     onCreate → onStart → onResume
Home:      onPause → onStop
return:    onRestart → onStart → onResume
Back:      onPause → onStop → onDestroy
rotation:  onPause → onStop → onDestroy → onCreate → onStart → onResume
```

> On rotation, `onSaveInstanceState` runs before destruction, so that the state can be rebuilt. In DMA02 it saves nothing, but the mechanism exists.

**Why all six methods are "empty":** each override does exactly one thing — writes a line in Logcat. They are **observers**, not requirements: if you delete a whole method, the app keeps working, because the implementation from `AppCompatActivity` runs. You only lose the line in Logcat.

**Why `super` is first everywhere:** for a log, the order does not matter. But the convention for `onPause`, `onStop` and `onDestroy` is to do the cleanup **before** `super` (your resources still exist), and for `onCreate`, `onStart`, `onResume` — after `super`. Here all of them are after, for simplicity. What matters: `super` **must** be called. Without it, `ActivityThread` throws `SuperNotCalledException` after every method.

### 25.2.4 `pressMe`: the three `Intent`s

An `Intent` can be built in two ways:

- **explicit** — `new Intent(this, MainActivity.class)`: you know exactly which class you want;
- **implicit** — `new Intent(Intent.ACTION_SEND)`: you declare only **which operation** you want, and the system looks for the apps that can do it.

All three variants in `pressMe` are implicit. The difference between them is the action and the data:

| Variant | Action | Data | Effect | Status |
|---|---|---|---|---|
| 1 | `ACTION_VIEW` | `https://developer.android.com` | opens the default browser | commented out: `Uri` is not imported |
| 2 | `ACTION_DIAL` | `tel:0212345678` | opens the phone dialer, **without** calling | commented out: `Uri` is not imported |
| 3 | `ACTION_SEND` | `text/plain` + `EXTRA_TEXT` | opens the share sheet | active |

**Why the first two are commented out:** they are demonstrations kept in the code as teaching material. Both use `Uri.parse(...)`, and `android.net.Uri` does **not** appear in the import list. If you uncomment the first block, the compiler gives `cannot find symbol: class Uri`. Add `import android.net.Uri;` and it compiles.

**Why `ACTION_DIAL` and not `ACTION_CALL`:** `ACTION_DIAL` opens the dialer with the number filled in, and the user presses the call button. It does not need the `CALL_PHONE` permission. `ACTION_CALL` would call directly and would require the permission in the manifest and at runtime.

**Why `ACTION_SEND` + `setType("text/plain")`:** an implicit `Intent` declares only **which operation** you want, not the class that performs it. The system looks for the apps that have a matching `<intent-filter>`. `setType` is the main filter: without it, the system does not know which apps can receive the `Intent`.

| Deleted line | Effect |
|---|---|
| `share.setType("text/plain")` | no app matches; the chooser appears empty ("No apps can perform this action"), and `startActivity` directly would give `ActivityNotFoundException` |
| `share.putExtra(Intent.EXTRA_TEXT, "Hello!")` | the share sheet opens, but the text sent is empty |
| `Intent.createChooser(...)` | Android may open the default share app directly, without a dialog |
| `startActivity(...)` | the `Intent` is built and thrown away; nothing happens |

**Why `Intent.EXTRA_TEXT` and not `"android.intent.extra.TEXT"`:** the constant has exactly the same value, but the name is checked by the compiler. A hand-written string with a typo gives no error — the text just goes nowhere.

**Why `createChooser`:** `ACTION_SEND` alone respects the default share app. `createChooser(intent, title)` **always** forces the choice dialog, with the given title ("Share via DMA"). It is useful when you want the user to decide consciously. Internally, `createChooser` builds an `Intent` with the `ACTION_CHOOSER` action, puts the original `Intent` in `EXTRA_INTENT` and the title in `EXTRA_TITLE`.

### 25.2.5 The share sheet flow

```
pressMe(view)
  │
  ├─ 1. new Intent(Intent.ACTION_SEND)          action = "send"
  ├─ 2. share.setType("text/plain")             MIME = what kind of content
  ├─ 3. share.putExtra(EXTRA_TEXT, "Hello!")    the payload
  └─ 4. Intent.createChooser(share, "Share via DMA")
        │
        ▼
   PackageManager.queryIntentActivities(intent, MATCH_DEFAULT_ONLY)
        │  looks for ALL the apps with an <intent-filter> that accept
        │  ACTION_SEND + text/plain + category DEFAULT
        ▼
   ┌─────────────────────────────────────────────┐
   │  Share via DMA                              │
   │  ┌───────────┐ ┌───────────┐ ┌───────────┐  │
   │  │ Gmail     │ │ Messages  │ │ DMA02     │  │  ← DMA02 appears thanks to
   │  └───────────┘ └───────────┘ └───────────┘  │    the filter in the manifest
   └─────────────────────────────────────────────┘
        │
        ▼
   the chosen app receives the Intent with EXTRA_TEXT = "Hello!"
```

**The loop that closes:** the manifest declares an `<intent-filter>` for `ACTION_SEND` + `text/plain` (section 25.3). So **DMA02 appears in its own share sheet**. If you choose it, it starts a **second** instance of `MainActivity` (standard launch mode), and the first one goes through `onPause` → `onStop`. And, because `MainActivity` never reads `getIntent().getStringExtra(Intent.EXTRA_TEXT)`, the received text is ignored: you only see a new, identical screen.

**Why `startActivity` and not `startActivityForResult`:** you do not need any result back. `startActivityForResult` (or `registerForActivityResult`) is used when you wait for data — as in `G1097`, at the form.

### 25.2.6 What breaks if you delete each thing from `MainActivity`

| Deleted element | Effect |
|---|---|
| `extends AppCompatActivity` | does not compile anymore: `super.onCreate`, `setContentView` and `onCreate` do not exist in `Object` |
| `super.onCreate(savedInstanceState)` | `SuperNotCalledException` at start |
| `setContentView(...)` | white screen; any `findViewById` would return `null` |
| a lifecycle method | nothing functional; only the line in Logcat disappears |
| `super.onX()` from a method | `SuperNotCalledException` after that method |
| `public` from `pressMe` | reflection does not find the method: `IllegalStateException` on click |
| the whole `pressMe` | `android:onClick` has nothing to call: `IllegalStateException` on click |
| `share.setType(...)` | empty chooser: no app matches |
| `Intent.createChooser(...)` | the default app may open directly, without a dialog |

### 25.2.7 What the project does not do (and why it matters)

DMA02 is a teaching skeleton. A few things you will see in the following projects are intentionally missing:

| Missing | Where it appears | What it means |
|---|---|---|
| `EdgeToEdge` + insets listener | `G1097` | on Android 15+ the content goes under the status bar |
| View Binding | `DMA05` | `findViewById` returns a generic `View`, with a manual cast |
| `onSaveInstanceState` | `G1097` | the state is lost on rotation |
| options menu | `DMA03` | there is no `onCreateOptionsMenu` |
| a second activity | `G1097` | there is no navigation, only one screen |

**Why it matters:** each gap is a concept that appears in a later chapter. If you understand what DMA02 does **not** do, you understand better what the other projects add. For example, `EdgeToEdge` is not an aesthetic feature: it is the consequence of the fact that, from Android 15, apps with `targetSdk ≥ 35` draw by default under the system bars.

> DMA02 has `targetSdk = 37`, so on an Android 15+ device it already runs edge-to-edge, only without handling the insets. The toolbar may go under the clock. It is the first "technical debt" that `G1097` pays off.

---

## 25.3 `AndroidManifest.xml`

### 25.3.1 The complete file, annotated

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ↑ the XML declaration: the mandatory first line. A comment BEFORE it would make
     the document invalid, that is why the header sits after it. -->

<!--
  ======================================================================================
  AndroidManifest.xml — THE APP'S CONTRACT WITH THE ANDROID SYSTEM
  ======================================================================================
  WHAT IT IS:
    The file that tells the system which components the app has, which permissions it
    asks for and which `Intent`s it accepts. Without it, the APK cannot be installed.

  WHY IT EXISTS:
    1. it binds `DMA02App` to the runtime (`android:name=".DMA02App"`);
    2. it declares `MainActivity` and the filter that makes it visible in the launcher;
    3. it declares the filter that makes the app visible in the share sheet.

  WHAT BREAKS WITHOUT IT:
    - without `<application android:name>`, `DMA02App` is not instantiated: silence;
    - without `MAIN` + `LAUNCHER`, the app does not appear in the launcher;
    - without `exported="true"`, the build fails on targetSdk ≥ 31.

  REF: AndroidManifest.xml (Android 36); build.gradle.kts, `namespace`.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: the manifest as a registry of components
  ======================================================================================
  1. `<manifest>` — the root. It contains `package` (or `namespace` in build.gradle.kts)
     and the XML namespaces.
  2. `<application>` — a single node per APK. Its attributes apply to the whole
     app: name, icon, theme, backup.
  3. `<activity>` — a component with a window. Each one has `android:name` and, if it
     has an `<intent-filter>`, `android:exported`.
  4. `<intent-filter>` — which `Intent`s the component accepts. `MAIN` + `LAUNCHER` =
     entry point; `SEND` + `DEFAULT` + `text/plain` = share receiver.
  ======================================================================================
-->

<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
    <!-- ↑ xmlns:android = the prefix of all the android: attributes.
         xmlns:tools = the tools: prefix; here it is declared, but no tools:
         attribute appears in the file — a leftover from the template. -->

    <!--
      ==================================================================================
      THE <application> NODE — the global attributes of the app
      ==================================================================================
      android:name=".DMA02App"              ← THE LINK to DMA02App.java
      android:allowBackup="true"            ← automatic backup of the data
      android:dataExtractionRules="..."     ← backup rules for Android 12+
      android:fullBackupContent="..."       ← backup rules for Android 11 and below
      android:icon / roundIcon              ← the launcher icon
      android:label="@string/app_name"      ← the displayed name: "DMA02"
      android:supportsRtl="true"            ← mirroring for RTL languages
      android:theme="@style/Theme.DMA02"    ← the app theme
      ==================================================================================
    -->
    <application
        android:name=".DMA02App"
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA02">
        <!-- ↑ after the `>` we can put comments: they are between elements, not inside
             the tag. Inside an XML tag, between attributes, a comment would make the
             document invalid. -->

        <!--
          ==================================================================================
          THE MAIN ACTIVITY
          ==================================================================================
          android:name=".MainActivity"        ← the class that is instantiated
          android:exported="true"             ← mandatory: the launcher is another app
          android:windowSoftInputMode="..."   ← the keyboard behavior (inert here)
          ==================================================================================
        -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <!-- ↑ the activity that appears in the launcher and has the layout from 25.4. -->

            <!--
              FILTER 1: MAIN + LAUNCHER
              MAIN      = "this is the entry point"
              LAUNCHER  = "show me in the launcher"
            -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <!-- ↑ without this filter, the app does not appear in the launcher. -->

            <!--
              FILTER 2: SEND + DEFAULT + text/plain
              SEND       = "I receive content sent by other apps"
              DEFAULT    = mandatory for implicit resolution
              text/plain = plain text only
              → the app appears in its own share sheet and in those of others.
            -->
                <intent-filter>
                    <action android:name="android.intent.action.SEND" />
                    <category android:name="android.intent.category.DEFAULT" />
                    <data android:mimeType="text/plain" />
                </intent-filter>
            <!-- ↑ the inconsistent indentation (16 spaces) is in the repo; it changes nothing. -->


        </activity>
    </application>

</manifest>
```

### 25.3.2 `android:name=".DMA02App"` — the link to the code

This is the most important line in the file, because it is the only link between the class from 25.1 and the runtime.

```
AndroidManifest.xml                         Runtime
───────────────────                         ───────
android:name=".DMA02App"   ─────────────►   ro.ase.ie.dma02.DMA02App
                                            (the dot = relative to `namespace`)

missing                    ─────────────►   android.app.Application
                                            (your class is NOT instantiated: silence)

wrong name                 ─────────────►   ClassNotFoundException at start
```

**Why the dot:** in the manifest, a name that starts with `.` is relative to the application package. Here `namespace = "ro.ase.ie.dma02"` in `build.gradle.kts`, so `.DMA02App` means `ro.ase.ie.dma02.DMA02App`. You can also write the full name, without the dot; both are equivalent.

**What happens if you forget the line:** Android uses the default `android.app.Application`. `DMA02App` is never created, so `onCreate()` does not run, the callbacks are not registered, `DynamicColors` is not applied and the first log does not appear. The app looks and works identically. **No error. Just silence.** It is the classic pitfall of the lab: you think you wrote the code, but the code does not run.

**What happens if the name is wrong:** at start, `ActivityThread` tries to instantiate the class and fails with `Unable to instantiate application ro.ase.ie.dma02.DMA02App: java.lang.ClassNotFoundException`. Here the error is loud, so it is easier to find than the missing line.

### 25.3.3 `android:exported="true"` — mandatory, not optional

From Android 12 (API 31), any component with an `<intent-filter>` must explicitly declare `android:exported`. Without the attribute, the build fails:

```
Apps targeting Android 12 and higher are required to specify an explicit value
for `android:exported` when the corresponding component has an intent filter defined.
```

**Why `true` here:** the launcher is **another** app. For it to be able to start `MainActivity`, the component must be exported. If you set `false`, the launcher (another UID) would no longer see the activity: the app would no longer appear in the launcher.

**Why it is not a security problem:** the activity does nothing sensitive: it shows a text and a button. If it read private data, you would limit access with permissions or verify the caller.

### 25.3.4 The two `<intent-filter>`s

| Filter | Action | Category | Data | Effect |
|---|---|---|---|---|
| 1 | `android.intent.action.MAIN` | `android.intent.category.LAUNCHER` | — | the app appears in the launcher |
| 2 | `android.intent.action.SEND` | `android.intent.category.DEFAULT` | `text/plain` | the app appears in the share sheet |

**Filter 1 — `MAIN` + `LAUNCHER`:** `MAIN` says "this is the entry point"; `LAUNCHER` says "show me in the launcher". Without it, the app can be started only from another app or from `adb`, not from the icon.

**Filter 2 — `SEND` + `DEFAULT` + `text/plain`:** it filters which implicit `Intent`s the activity accepts.

- `SEND` = the action "send content";
- `DEFAULT` = mandatory for `startActivity`: the system resolves with `MATCH_DEFAULT_ONLY`, so a filter without `DEFAULT` never matches;
- `text/plain` = limits it to plain text. Without it, the app would appear in share for any type of content.

> The filter is **only a receiver**. The code does not read the received text, so the app appears in the share sheet and ignores it. It is the second half of the demonstration from 25.2.5.

**Why `DEFAULT` and not `LAUNCHER` on the second filter:** `LAUNCHER` would mean "show me in the launcher" — it makes no sense here. `DEFAULT` is the category required by implicit resolution; without it, the filter is not taken into account by `PackageManager`.

### 25.3.5 The attributes in `<application>`

| Attribute | What it does | If you delete it |
|---|---|---|
| `android:name` | binds the `Application` class | the class does not run; no error, just silence |
| `android:allowBackup` | allows automatic backup of the app data | the default applies (`true` on most devices) |
| `android:dataExtractionRules` | the backup/transfer rules for **Android 12+** | the default rules apply |
| `android:fullBackupContent` | the backup rules for **Android 11 and below** | the default rules apply |
| `android:icon` | the launcher icon | the system's default icon |
| `android:label` | the name shown under the icon and in recents | the app name becomes the package name |
| `android:roundIcon` | the round variant for launchers that ask for it | `android:icon` is used |
| `android:supportsRtl` | mirrors the layouts for RTL languages | the interface is no longer mirrored |
| `android:theme` | the app theme | the platform theme: the Material components no longer look right |

**Why two backup files:** `fullBackupContent` is read by Android 11 and below; `dataExtractionRules` by Android 12+. Both are generated by the template and cover two API ranges. If you delete the files `res/xml/backup_rules.xml` and `data_extraction_rules.xml` but leave the attributes, the build fails with "resource not found".

**Why `android:label="@string/app_name"`:** the name "DMA02" sits in `res/values/strings.xml`, not hardcoded in the manifest. That way it can be translated, and lint does not give `HardcodedText`.

### 25.3.6 The theme: `Theme.DMA02`

`Theme.DMA02` is defined in `res/values/themes.xml` as `parent="Base.Theme.DMA02"`, and `Base.Theme.DMA02` has **two** parents, depending on the system mode:

| File | Parent | Effect |
|---|---|---|
| `values/themes.xml` (light mode) | `Theme.Material3.Dark` | the app is **dark** and has an ActionBar |
| `values-night/themes.xml` (night mode) | `Theme.Material3.DayNight.NoActionBar` | the app is dark and **does not** have an ActionBar |

The result is a real inconsistency of the repo: the app is always dark, and the window title bar appears only in light mode — where, on top of it, there is also the `MaterialToolbar` from the layout. Nothing crashes, but it explains why the screen looks different with the system theme on light versus night.

> `Theme.Material3.Dark` is not a `DayNight` theme: in light mode it stays dark. That is why the app does not follow the system setting, it just ignores it. `Theme.Material3.DayNight.NoActionBar` from `values-night` would have followed it, but it is used only at night.

### 25.3.7 What breaks if you delete each thing from the manifest

| Deleted element | Effect |
|---|---|
| `android:name=".DMA02App"` | `DMA02App` does not run: no error, just silence |
| `android:name=".MainActivity"` | the build fails: the activity has no name |
| `android:exported="true"` | the build fails on targetSdk ≥ 31 |
| the `MAIN` + `LAUNCHER` filter | the app does not appear in the launcher |
| the `SEND` + `DEFAULT` + `text/plain` filter | the app no longer appears in the share sheet |
| `android:theme` | the platform theme: `AppCompatActivity` crashes at start |
| `android:icon` / `roundIcon` | the system's default icon |
| `android:label` | the app name becomes the package name |
| `xmlns:android` | all `android:` attributes become invalid: the build fails |
| `xmlns:tools` | nothing: it is declared, but unused in the manifest |

### 25.3.8 Why there is no `<uses-permission>`

The manifest declares no permission. It is not an omission: the actions used do not require one.

| Action | Required permission | Why |
|---|---|---|
| `ACTION_SEND` | none | it sends through other apps; they take care of permissions |
| `ACTION_VIEW` + `https://` | none | the browser already has `INTERNET` |
| `ACTION_DIAL` | none | it opens the dialer, it does not call |
| `ACTION_CALL` | `CALL_PHONE` | it would call directly — it is not used |

> If you added `ACTION_CALL`, you would need `<uses-permission android:name="android.permission.CALL_PHONE" />` in the manifest **and** a request at runtime (Android 6+). DMA02 needs none of this.

---

## 25.4 `activity_main.xml`

### 25.4.1 The complete file, annotated

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ↑ the XML declaration: the mandatory first line. -->

<!--
  ======================================================================================
  activity_main.xml — THE VIEW TREE OF THE SCREEN
  ======================================================================================
  WHAT IT IS:
    The layout inflated by `setContentView(R.layout.activity_main)` in MainActivity.onCreate.
    A ConstraintLayout with three children: a toolbar, a centered text and a button.

  WHY IT EXISTS:
    1. it defines what is seen on screen;
    2. it binds the button to the `pressMe` method through `android:onClick`;
    3. it provides the ids used by the code (`main`, `toolbar`, `textView`, `button`).

  WHAT BREAKS WITHOUT IT:
    - `R.layout.activity_main` no longer exists: the build fails;
    - without a `Button`, `pressMe` cannot be called;
    - without `android:onClick`, the click does nothing.

  REF: activity_main.xml; R.layout.activity_main; MainActivity.onCreate.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: ConstraintLayout and the XML → code links
  ======================================================================================
  1. CONSTRAINTS, NOT ORDER
     Each child is positioned through relations to the parent or to its siblings, not
     through the order in the file. A view without constraints is placed at (0,0).

  2. `@+id/...` vs `@id/...`
     `@+id/textView` creates the id if it does not exist; `@id/textView` refers to it.
     In practice, `@+id` also works when the id already exists.

  3. `android:onClick` — REFLECTION
     It is not a compile-time link. On click, the framework looks in the view's
     Context for a `public void` method with exactly one `View` parameter.

  4. `?attr/...` — values from the theme
     `?attr/actionBarSize` and `?attr/textAppearanceBodyLarge` are resolved at runtime
     from the activity theme, they are not fixed values.
  ======================================================================================
-->

<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">
    <!-- ↑ the root: ConstraintLayout, id `main` (unused in DMA02, used in G1097
         for insets). `tools:context` is only for the IDE preview and
         disappears at build. -->

    <!--
      ==================================================================================
      MATERIALTOOLBAR — the title bar drawn by the app
      ==================================================================================
      android:id="@+id/toolbar"                    ← the view id (unused in the code)
      android:layout_width="match_parent"          ← takes the full width
      android:layout_height="?attr/actionBarSize"  ← the standard bar height (56dp)
      app:title="@string/app_name"                 ← the title: "DMA02"
      No constraints → placed at (0,0) by ConstraintLayout.
      ==================================================================================
    -->
    <com.google.android.material.appbar.MaterialToolbar
        android:id="@+id/toolbar"
        android:layout_width="match_parent"
        android:layout_height="?attr/actionBarSize"
        app:title="@string/app_name"/>
    <!-- ↑ it is NOT set as the ActionBar: there is no `setSupportActionBar(toolbar)`. -->

    <!--
      ==================================================================================
      TEXTVIEW — the centered text
      ==================================================================================
      android:text="Hello World!"                             ← hardcoded text
      android:textAppearance="?attr/textAppearanceBodyLarge"  ← the typographic style from the theme
      four constraints to the parent                          ← centered on both axes
      ==================================================================================
    -->
    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        android:textAppearance="?attr/textAppearanceBodyLarge"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    <!-- ↑ `wrap_content` + four constraints = centered, with the size of the text. -->

    <!--
      ==================================================================================
      BUTTON — the only XML → code link in the project
      ==================================================================================
      android:onClick="pressMe"                             ← the name of the method in MainActivity
      app:layout_constraintBottom_toTopOf="@+id/textView"   ← it sits above the text
      app:layout_constraintTop_toTopOf="parent"             ← it starts from the top
      ==================================================================================
    -->
    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Button"
        app:layout_constraintBottom_toTopOf="@+id/textView"
        app:layout_constraintEnd_toEndOf="parent"
        android:onClick="pressMe"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    <!-- ↑ click → reflection → MainActivity.pressMe(view). -->

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 25.4.2 Why `ConstraintLayout`

Each child is positioned through **relations** to the parent or to its siblings, not through order. It is the layout generated by the "Empty Views Activity" template and it suits simple screens: a centered text, a button above it.

**Why `android:id="@+id/main"`:** in DMA02 it is not used anywhere — no line of code does `findViewById(R.id.main)`. In `G1097` it becomes essential: `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` needs it. If you delete it here, DMA02 still works; if you delete it in `G1097`, the code that does `findViewById(R.id.main)` no longer compiles.

**Why `tools:context=".MainActivity"`:** it tells the IDE which activity to use for the preview (theme, `android:onClick` resolution). At build time, the attribute is removed — it does not reach the APK.

### 25.4.3 `MaterialToolbar`

The attributes that matter are `android:layout_height="?attr/actionBarSize"` and `app:title="@string/app_name"`. `?attr/actionBarSize` takes the standard bar height (56dp) from the theme. `app:title` is the Material attribute, not `android:title`. The toolbar has `match_parent` on width and **no constraint** — in `ConstraintLayout`, a view without constraints is placed at the corner (0,0) with its measured size. It works, but "by accident": if you add another view above, the toolbar does not move.

> No code calls `setSupportActionBar(toolbar)`. So the toolbar is just a styled view with a title, not the activity's ActionBar: it receives no options menu, no back navigation button.

### 25.4.4 `TextView`

The attributes that matter are `android:text="Hello World!"` and `android:textAppearance="?attr/textAppearanceBodyLarge"`. Four constraints (top, bottom, start, end) to the parent = centered on both axes. `?attr/textAppearanceBodyLarge` takes the "body large" typographic style from the Material 3 theme (16sp), instead of hardcoding `textSize`.

> `"Hello World!"` is hardcoded text: lint gives the `HardcodedText` warning, and the text cannot be translated. The correct way would be `@string/hello_world` in `strings.xml`.

### 25.4.5 `Button` and `android:onClick`

The attributes that matter are `android:onClick="pressMe"` and `app:layout_constraintBottom_toTopOf="@+id/textView"`. The button is tied to the `TextView` through `bottom_toTopOf`: it sits above the text, centered horizontally. Together with `top_toTopOf="parent"`, it occupies the upper half of the screen. `@+id/textView` also works without the `+` (the id is already declared above), but it is harmless.

**How `android:onClick` binds to the code:** on click, the `View` looks in the chain of `Context`s (activity, application) for a `public` method, returning `void`, with exactly one `View` parameter, whose name is `pressMe`. If it does not find it, it throws:

```
IllegalStateException: Could not find method pressMe(View) in a parent or ancestor Context
for android:onClick attribute defined on view class android.widget.Button ...
```

> `android:onClick` is the **only** link between XML and code in the whole project. The name in the XML must be identical to the method in `MainActivity` — otherwise `IllegalStateException` on click, not at compile time.

### 25.4.6 What breaks if you delete each block from the layout

| Deleted block | Effect |
|---|---|
| the `Button` | `pressMe` can no longer be called; the app shows only the text |
| `android:onClick="pressMe"` | the click does nothing; no error, no trace in Logcat |
| the `TextView` | the `bottom_toTopOf` reference is left without a target: the constraint is ignored, and the button sticks to the top edge |
| `MaterialToolbar` | the screen is left without a title; the rest works |
| `android:id="@+id/main"` | nothing in DMA02; `G1097` would no longer compile |
| `xmlns:app` | all `app:` attributes become invalid → the build fails |
| `xmlns:tools` | `tools:context` becomes invalid → the build fails |
| `tools:context` | only the IDE preview loses the theme; the build works |

### 25.4.7 The order of the attributes does not matter

In XML, the order of the attributes in a tag is irrelevant to the runtime. `android:id` can be first or last; `android:onClick` can sit anywhere. The order in the file is a readability convention (and, sometimes, the order in which the template wrote them).

> What **matters** is the order of the **elements**: `ConstraintLayout` does not depend on it, but a `LinearLayout` does. In DMA02 everything is a `ConstraintLayout`, so the order of the children does not change the positions — only the drawing order (z-order), and here they do not overlap.

---

## 25.5 The complete flow

### 25.5.1 Starting the process and the first activity

```
STARTING THE PROCESS
  Zygote → fork → ActivityThread.main
    ├── Application.attachBaseContext()                 (not in the code)
    ├── ContentProvider.onCreate()                      (if any; not the case here)
    └── DMA02App.onCreate()
          ├── super.onCreate()
          ├── registerActivityLifecycleCallbacks(this)
          ├── DynamicColors.applyToActivitiesIfAvailable(this)
          └── Log.w("DMA02App", "onCreate")
                ↓
  MainActivity (new instance)
    ├── DMA02App.onActivityCreated(MainActivity, null)  ← from inside super.onCreate
    ├── MainActivity.onCreate
    │     ├── super.onCreate(...)          → the dispatch above
    │     ├── setContentView(activity_main)
    │     └── Log.w("MainActivity", "onCreate")
    ├── DMA02App.onActivityStarted   → MainActivity.onStart   → Log
    ├── DMA02App.onActivityResumed   → MainActivity.onResume  → Log
    └── the screen is visible
```

**What one reads from the diagram:**

1. `Application.onCreate` runs **before** any activity — that is why the subscription and the theme sit there.
2. Every method of the activity has a paired callback, triggered from inside `super`.
3. `setContentView` runs **after** `onActivityCreated`, so the callback cannot touch the views.
4. On rotation, the complete destruction and creation chain runs again — that is why `onCreate` appears twice in Logcat.

### 25.5.2 Pressing the button and the share sheet

```
BUTTON PRESS
  Button.onClick → reflection → MainActivity.pressMe(view)
    ├── new Intent(ACTION_SEND)
    ├── setType("text/plain")
    ├── putExtra(EXTRA_TEXT, "Hello!")
    └── startActivity(createChooser(share, "Share via DMA"))
          ↓
  MainActivity.onPause → onStop          (the chooser is another activity, on top of it)
  ChooserActivity opens
    ├── DMA02 also appears in the list (the SEND filter from the manifest)
    └── you choose an app
          ↓
  MainActivity.onStart → onResume        (on return)
```

**Why `onPause` → `onStop` and not `onDestroy`:** the chooser is a system activity, opened **on top of** `MainActivity`. Your activity is not destroyed, only hidden. On return, `onStart` → `onResume`, without `onCreate`.

**If you choose DMA02 from the chooser:** a **new** instance of `MainActivity` is created, and the old one stays behind. The text `"Hello!"` is ignored, because `MainActivity` does not read `getIntent()`. It is the complete demonstration of an implicit `Intent`: the sender and the receiver are the same app.

### 25.5.3 Back, Home and rotation

```
PRESSING BACK (from MainActivity)
  onPause → onStop → onDestroy
    └── DMA02App.onActivityDestroyed

PRESSING HOME
  onPause → onStop
    └── the process may be killed by the system at any time

RETURNING FROM HOME
  onRestart → onStart → onResume
    └── `onRestart` is NOT overridden in MainActivity, so it does not appear in Logcat

ROTATION
  onPause → onStop → onSaveInstanceState → onDestroy
  → onActivityCreated → onCreate → onStart → onResume    (new instance!)
```

**Why rotation is the best test:** it goes through almost the whole cycle, twice, and demonstrates that `onCreate` does not run once per app, but once per activity instance. In Logcat you see:

```
DMA02App:      onActivityPausedMainActivity
MainActivity:  onPause
DMA02App:      onActivityStoppedMainActivity
MainActivity:  onStop
DMA02App:      onActivityDestroyedMainActivity
MainActivity:  onDestroy
DMA02App:      onActivityCreatedMainActivity
MainActivity:  onCreate
DMA02App:      onActivityStartedMainActivity
MainActivity:  onStart
DMA02App:      onActivityResumedMainActivity
MainActivity:  onResume
```

**Why `Application.onCreate` does not appear a second time:** the process did not die. `Application` lives as long as the process lives, not as long as the activity lives. On rotation only the activity is recreated.

### 25.5.4 Scenario table

| Scenario | The sequence of methods | What appears in Logcat |
|---|---|---|
| Start from the launcher | `onCreate → onStart → onResume` | `onActivityCreatedMainActivity`, `onCreate`, `onActivityStartedMainActivity`, `onStart`, `onActivityResumedMainActivity`, `onResume` |
| Home | `onPause → onStop` | `onActivityPausedMainActivity`, `onPause`, `onActivityStoppedMainActivity`, `onStop` |
| Return from Home | `onRestart → onStart → onResume` | `onActivityStartedMainActivity`, `onStart`, `onActivityResumedMainActivity`, `onResume` |
| Back | `onPause → onStop → onDestroy` | `onActivityPausedMainActivity`, `onPause`, `onActivityStoppedMainActivity`, `onStop`, `onActivityDestroyedMainActivity`, `onDestroy` |
| Rotation | `onPause → onStop → onSaveInstanceState → onDestroy → onCreate → onStart → onResume` | the two chains, one after the other |
| Share sheet | `onPause → onStop`, then `onStart → onResume` on return | `onActivityPausedMainActivity`, `onPause`, `onActivityStoppedMainActivity`, `onStop`, then `onActivityStartedMainActivity`, `onStart`, `onActivityResumedMainActivity`, `onResume` |

**Why `onRestart` does not appear in the right-hand column:** `MainActivity` does not override it, so it writes nothing in Logcat. The framework calls it, but you have no line for it. It is the only "gap" of the demonstration: six methods are logged, the seventh is not.

> If you want to see it, add to `MainActivity` an `onRestart()` method that calls `super.onRestart()` and writes `Log.w(TAG, "onRestart")`. It is not in the project, but the mechanism is identical to the other six.

---

## 25.6 Real pitfalls in DMA02

| Place | Pitfall | Effect |
|---|---|---|
| `MainActivity` | `Uri` is not imported | you uncomment the `ACTION_VIEW` block → it does not compile |
| `MainActivity` | the methods are in alphabetical order | the order in the file ≠ the execution order |
| `MainActivity` | no `EdgeToEdge` + insets | on Android 15+ the content goes under the status bar |
| `MainActivity` | `pressMe` without `public` | reflection does not find the method: crash on click |
| `AndroidManifest.xml` | the `SEND` filter is not read in the code | the app appears in the share sheet, but ignores the text |
| `AndroidManifest.xml` | `adjustResize` without text fields | inert attribute |
| `AndroidManifest.xml` | `xmlns:tools` declared, but unused | noise, not a bug |
| `AndroidManifest.xml` | `android:name` absent | `DMA02App` does not run: silence |
| `themes.xml` | `Theme.Material3.Dark` in `values`, `DayNight.NoActionBar` in `values-night` | the app is always dark; an ActionBar only in light mode |
| `activity_main.xml` | toolbar without constraints | placed at (0,0) "by accident" |
| `activity_main.xml` | `"Hello World!"` and `"Button"` hardcoded | lint `HardcodedText`, no translation |
| `activity_main.xml` | `android:id="@+id/main"` unused | dead code in DMA02; useful in `G1097` |

**Pitfall 1 — `Uri` not imported.** It is the only pitfall in the Java code that shows up at **compile time**, not at runtime. That is why the blocks are commented out: the demonstration code cannot run without an extra import.

**Pitfall 2 — the alphabetical order.** Whoever reads the file from top to bottom believes that `onCreate` is followed by `onDestroy`. In reality, `onDestroy` is the last method of the cycle. The order in the file is a choice of the IDE, not a statement about the runtime.

**Pitfall 3 — `EdgeToEdge`.** The project has `targetSdk = 37`. On Android 15+ (API 35+), apps with `targetSdk ≥ 35` run edge-to-edge by default. Without an insets listener, the content is drawn **under** the status bar, and the toolbar goes under the clock. In `G1097`, `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` solves exactly that.

**Pitfall 4 — `android:name` absent.** It produces no error. It is the "silent" pitfall of the lab: the app looks identical, but `DMA02App` does not run. The only proof is the missing `DMA02App: onCreate` line in Logcat.

**Pitfall 5 — the theme.** `Theme.Material3.Dark` in `values` and `Theme.Material3.DayNight.NoActionBar` in `values-night` produce an always-dark app, with an ActionBar only in light mode. It does not crash, but it looks inconsistent.

### 25.6.1 Three reading pitfalls

**1. `Log.w` does not mean "error".** The `w` level is warning, not error. The messages in DMA02 are demonstrations, not problems. If you filter Logcat at `Error`, you see none of them.

**2. `onCreate` does not mean "once per app".** It means "once per activity instance". On rotation, `MainActivity.onCreate` runs again; `DMA02App.onCreate` does not.

**3. `Application` does not mean "the app start".** The process can exist even without a visible activity (for example, a `ContentProvider` or a `Service`). `Application.onCreate` runs at process start, not when the screen opens.

---

## 25.7 What to remember

| File | The essence |
|---|---|
| `DMA02App.java` | `Application` + `ActivityLifecycleCallbacks`; `onCreate` runs before any activity; `DynamicColors` is applied globally, once |
| `MainActivity.java` | six lifecycle methods, all with `super` first; `pressMe` = an implicit `Intent` with `ACTION_SEND` |
| `AndroidManifest.xml` | `android:name=".DMA02App"` binds the class; `exported="true"` mandatory; two filters: `LAUNCHER` and `SEND` |
| `activity_main.xml` | `ConstraintLayout`; `android:onClick="pressMe"` is the only XML → code link |

**Ten statements to remember:**

1. `Application` is **one per process**, created before any activity. It has no UI and no `Bundle`.
2. `Application.onCreate` is the place for global initializations: subscriptions, themes, libraries.
3. `ActivityLifecycleCallbacks` has **seven** abstract methods. You implement all of them or it does not compile.
4. The callbacks are triggered **from inside** the base method (`super.onX()`), not before it.
5. If `MainActivity` calls `super` first, the log from `Application` appears first in Logcat.
6. `MainActivity` overrides six methods only to log. Deleting an override breaks nothing; deleting `super` gives `SuperNotCalledException`.
7. The order of the methods in the file is alphabetical, not chronological: `onCreate → onStart → onResume → onPause → onStop → onDestroy`.
8. `android:onClick="pressMe"` requires exactly `public void pressMe(View)`; otherwise a crash on click, not at build.
9. `ACTION_SEND` without `setType` has no target; `createChooser` forces the choice dialog.
10. The app appears in its own share sheet (the `SEND` filter), but it does not read the received text.

### 25.7.1 The code ↔ concept correspondence

| Construct in the code | The concept | The section |
|---|---|---|
| `extends Application` | a single object per process | 25.1.2 |
| `implements Application.ActivityLifecycleCallbacks` | the observer pattern | 25.1.4 |
| `registerActivityLifecycleCallbacks(this)` | the subscription to all activities | 25.1.4 |
| `DynamicColors.applyToActivitiesIfAvailable(this)` | global Material You | 25.1.6 |
| `Log.w(TAG, ...)` | the log level and visibility | 25.1.7 |
| `android:name=".DMA02App"` | the manifest ↔ class link | 25.1.5, 25.3.2 |
| `super.onCreate(savedInstanceState)` | the `super` contract | 25.2.3 |
| `setContentView(R.layout.activity_main)` | inflating the layout | 25.2.1 |
| `android:onClick="pressMe"` | the XML → code reflection | 25.4.5 |
| `Intent.ACTION_SEND` + `setType` | an implicit `Intent` | 25.2.4 |
| `Intent.createChooser(...)` | a forced chooser | 25.2.4 |
| `<intent-filter>` `SEND` + `DEFAULT` | the share receiver | 25.3.4 |

**Three things that are not visible from the code:**

- **The manifest is half of the app.** Without `android:name`, the `Application` class is dead code; without `MAIN` + `LAUNCHER`, the activity does not appear in the launcher; without `SEND`, it does not appear in the share sheet.
- **`DynamicColors` is a no-op below API 31.** It does not crash, it does not log: it simply does nothing. In DMA02, `minSdk = 33`, so it never happens.
- **`Log.w` does not mean "error".** It only means "warning level": high enough to stay visible when you filter Logcat at Info.

---

## Chapter 25 summary

- `Application` = the single object per process, created before any activity. Without `android:name` in the manifest, the class does not exist at runtime — no error, just silence.
- `Application.onCreate` is the place for global initializations: registering the callbacks and `DynamicColors`. Both must be done before the first activity.
- `ActivityLifecycleCallbacks` has seven abstract methods: you implement all of them or it does not compile. `onActivitySaveInstanceState` is the only empty one.
- The callbacks are triggered from inside the base method (`super.onX()`); because `MainActivity` calls `super` first, the log from `Application` appears first in Logcat.
- `MainActivity` overrides six methods only to log. Deleting an override breaks nothing; deleting `super` gives `SuperNotCalledException`.
- The order of the methods in the file is alphabetical, not chronological: `onCreate → onStart → onResume → onPause → onStop → onDestroy`.
- `android:onClick="pressMe"` requires exactly `public void pressMe(View)`; otherwise a crash on click, not at build.
- `ACTION_SEND` without `setType` has no target; `createChooser` forces the choice dialog.
- The app appears in its own share sheet (the `SEND` filter), but it does not read the received text.
- `Uri` is not imported: the commented blocks in `pressMe` do not compile if you uncomment them.

**Back to** [cheatsheet](21%20-%20Cheatsheet.md) **or to** [the overview](index.html).
