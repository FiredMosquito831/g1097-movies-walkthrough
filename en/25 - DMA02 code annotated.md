# Chapter 25 — The DMA02 code, annotated

**Objective:** to read the first lab project line by line — the `Application` class, the full lifecycle, `DynamicColors` and an implicit `Intent` — with explanations for every block: what it does, why it is there, what breaks if you delete it.

**Source:** `DMA02/` at commit `d719ffc` (2026-11-09, "G1097_S07") — 4 files: `DMA02App.java`, `MainActivity.java`, `AndroidManifest.xml`, `activity_main.xml`.

**What you learn from it:**
- what the **complete** lifecycle looks like — the six methods overridden by `MainActivity` and the seven callbacks that observe them;
- what an `Application` class does and why, without one line in the manifest, it never runs;
- how to enable Material You with **a single call**, globally;
- how to build an implicit `Intent` and why `setType` is not optional.

> **How to read this:** don't read passively. For each block, cover the explanation and try to say what it does yourself. If you can't, you have found what needs repeating. The project is small (125 lines of Java), but every line has a reason — and in the exam the questions come exactly on those reasons.

---

## 25.1 `DMA02App.java` — the `Application` class

### The complete file, annotated

```java
package ro.ase.ie.dma02;                    // the application package; identical to `namespace` in build.gradle.kts

import android.app.Activity;                // the type received by every callback: the observed activity
import android.app.Application;             // the base class — the single object of the process
import android.os.Bundle;                   // the saved state, received by two of the callbacks
import android.util.Log;                    // writing to Logcat

import androidx.annotation.NonNull;         // lint contract: the parameter must not be null
import androidx.annotation.Nullable;        // lint contract: the parameter may be null

import com.google.android.material.color.DynamicColors;   // Material You: colors extracted from the wallpaper

public class DMA02App
        extends Application                               // (1) the class becomes the application's Application
        implements Application.ActivityLifecycleCallbacks {   // (2) it subscribes to the lifecycle of all activities

    private final String TAG = DMA02App.class.getSimpleName();   // "DMA02App" — the label in the Tag column

    @Override
    public void onCreate() {
        super.onCreate();                                  // the inheritance chain; Application.onCreate is empty, but it is called
        registerActivityLifecycleCallbacks(this);          // "this" = the observer; from now on it receives all events
        DynamicColors.applyToActivitiesIfAvailable(this);  // Material You, if the device supports it

        Log.w(TAG, "onCreate");                            // the first message in Logcat — before any activity
    }
```

**Why `extends Application`:** `Application` is the object **unique per process**, created by the framework before any activity. By extending it, your class becomes that object: a safe place for global initializations that must run only once. The alternative — putting `registerActivityLifecycleCallbacks` and `DynamicColors` in `MainActivity.onCreate` — would mean repeating them in every activity and, worse, having them run **after** the first activity is already built.

**Why the class alone is not enough:** the link to the framework is made **only** from the manifest, through `android:name=".DMA02App"` (section 25.3). Without that line, Android instantiates the default `android.app.Application`, and `DMA02App` remains dead code: it compiles, but it is never created. No error, just silence in Logcat.

**Why `implements Application.ActivityLifecycleCallbacks`:** it is the **observer** pattern. Instead of overriding seven methods in every activity, you override them once here and you receive events from **all** activities. In DMA02 there is a single activity, so the gain is small — but the mechanism is what matters, and in `G1097` (two activities) it becomes useful immediately.

**Why `TAG`:** in Logcat, messages are grouped by tag. `getSimpleName()` returns `"DMA02App"`, without the package; `getName()` would have given `ro.ase.ie.dma02.DMA02App`. It is `private final`, not `static final` as in `MainActivity` — a style inconsistency, not a bug: `Application` has a single instance per process, so an instance field is enough.

**Why `onCreate` has exactly this order:**

1. `super.onCreate()` — the base class contract. In `Application`, the parent method is empty, but the chain may contain another class that does something; it is always kept.
2. `registerActivityLifecycleCallbacks(this)` — the subscription. It must be done **before** the first activity is created, otherwise the first event is lost.
3. `DynamicColors.applyToActivitiesIfAvailable(this)` — the theme. It must be applied **before** the first activity resolves its theme, otherwise the first screen keeps the fixed palette.
4. `Log.w(...)` — last, to mark "the global initialization has finished".

**Why `Log.w` and not `Log.d`:** `w` (warning) is visible by default in Logcat without changing the level filter; `d` (debug) may be hidden. For a demonstration, `w` is the practical choice.

**What happens if you delete each line:**

| Deleted line | Effect |
|---|---|
| `registerActivityLifecycleCallbacks(this)` | no error, no `onActivity*` message in Logcat — the app looks identical |
| `DynamicColors.applyToActivitiesIfAvailable(this)` | the fixed palette from `themes.xml`; on Android 12+ the app no longer follows the wallpaper |
| `Log.w(TAG, "onCreate")` | nothing functional; only the first row disappears from Logcat |
| `super.onCreate()` | nothing in `Application` (the base is empty), but it breaks the contract and is dangerous if the chain changes |
| `extends Application` | at startup: `ClassCastException` — the manifest asks for a class that is not an `Application` |

```java
    @Override
    public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
        Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());   // e.g. "onActivityCreatedMainActivity"
    }                                                                             // no space between the text and the class name

    @Override
    public void onActivityDestroyed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityDestroyed" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityPaused(@NonNull Activity activity) {
        Log.w(TAG, "onActivityPaused" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityResumed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityResumed" + activity.getClass().getSimpleName());
    }

    // the only method left empty: the interface requires it, but here we have nothing to save and we do not log
    @Override
    public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {

    }

    @Override
    public void onActivityStarted(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStarted" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityStopped(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStopped" + activity.getClass().getSimpleName());
    }
}
```

**Why all seven:** `ActivityLifecycleCallbacks` is an interface with seven **abstract** methods. You cannot implement only half of them: if you delete a method, the project **does not compile** (`DMA02App is not abstract and does not override abstract method ...`). That is why `onActivitySaveInstanceState` exists even though it does nothing.

**Correspondence with the activity's methods:**

| The activity's method | The callback in `Application` |
|---|---|
| `onCreate` | `onActivityCreated(activity, savedInstanceState)` |
| `onStart` | `onActivityStarted(activity)` |
| `onResume` | `onActivityResumed(activity)` |
| `onPause` | `onActivityPaused(activity)` |
| `onStop` | `onActivityStopped(activity)` |
| `onSaveInstanceState` | `onActivitySaveInstanceState(activity, bundle)` |
| `onDestroy` | `onActivityDestroyed(activity)` |

**Who runs first:** the callback is triggered **from inside** the base method. In the Android 36 source, `Activity.onCreate` calls `dispatchActivityCreated(...)` toward its end, `Activity.onStart` calls `dispatchActivityStarted()`, `Activity.onResume` calls `dispatchActivityResumed()` and so on. Because `MainActivity` writes `super.onX()` **first** and logs afterwards, in Logcat the order is:

```
DMA02App:    onActivityCreatedMainActivity
MainActivity: onCreate
DMA02App:    onActivityStartedMainActivity
MainActivity: onStart
...
```

> If you logged **before** `super.onStart()`, the order would invert. The order in Logcat is not "the callback comes before the method", it is "your log comes after `super`".

**Why `@Nullable Bundle bundle`:** on first creation, `savedInstanceState` is `null`; on recreation (rotation, return after the process was killed), it is the saved `Bundle`. The annotation documents this for lint and for the reader. `activity` is never `null`, which is why it is `@NonNull`.

**Why the concatenation looks ugly:** `"onActivityCreated" + activity.getClass().getSimpleName()` produces `onActivityCreatedMainActivity`, with no space. It is not a bug, but it is a reading trap: in Logcat it looks like a single word. If you want readability, you put `"onActivityCreated "` with a space.

**Why the methods are in alphabetical order:** `onActivityCreated`, `onActivityDestroyed`, `onActivityPaused`, `onActivityResumed`, `onActivitySaveInstanceState`, `onActivityStarted`, `onActivityStopped`. IntelliJ generates the implementations in alphabetical order, not in lifecycle order. The order in the file **is not** the execution order — a classic confusion when reading in a hurry.

**What happens if you delete `implements Application.ActivityLifecycleCallbacks`:** `registerActivityLifecycleCallbacks(this)` no longer compiles, because `this` is no longer of the required type. If you delete the call as well, the app compiles and runs, but with no lifecycle log at all.

---

## 25.2 `MainActivity.java` — the lifecycle

### The complete file, annotated

```java
package ro.ase.ie.dma02;

import android.content.Intent;              // used only in pressMe
import android.os.Bundle;                   // the parameter in onCreate
import android.util.Log;                    // writing to Logcat
import android.view.View;                   // the parameter in pressMe — required by android:onClick

import androidx.appcompat.app.AppCompatActivity;   // the AppCompat variant of Activity

public class MainActivity extends AppCompatActivity {

    private static final String TAG = MainActivity.class.getSimpleName();   // "MainActivity"

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);              // mandatory first; otherwise SuperNotCalledException
        setContentView(R.layout.activity_main);          // fills the window with the tree from the XML
        Log.w(TAG, "onCreate");                          // the activity's first log
    }
```

**Why `extends AppCompatActivity` and not `Activity`:** `AppCompatActivity` brings back (backports) the AppCompat behavior: inflation of compatible views, support for Material themes on older versions, `AppCompatDelegate` for dark mode. In addition, the `Theme.DMA02` theme descends from `Theme.Material3`, which descends from `Theme.AppCompat` — exactly what `AppCompatActivity` requires.

> The reverse is the trap: if you keep `AppCompatActivity` but change the theme to a platform one (without AppCompat), the app crashes at startup with `IllegalStateException: You need to use a Theme.AppCompat theme (or descendant) with this activity.`

**Why `TAG` is `static final`:** `MainActivity` can have several instances (on rotation, on return), but the tag is the same for all of them. `static` = it belongs to the class, not to the instance.

**Why `onCreate` has exactly this order:**

1. `super.onCreate(savedInstanceState)` — without it, the framework throws `SuperNotCalledException: Activity ... did not call through to super.onCreate()`. It is not a convention, it is a real check performed by `ActivityThread` after the method returns.
2. `setContentView(R.layout.activity_main)` — creates the view tree from the XML and attaches it to the window. Without it, the screen stays empty (white), and any `findViewById` would return `null`.
3. `Log.w(TAG, "onCreate")` — last, to mark "the activity is built".

**Why `R.layout.activity_main`:** `R` is the class generated at build time from the `res/` folder. The file name `activity_main.xml` becomes the constant `R.layout.activity_main`. If you rename the XML, the line no longer compiles — the link between the two files is **by name**.

**Why `savedInstanceState` is ignored:** DMA02 has no state to save (no field, no form). The parameter is `null` on first creation and non-`null` on recreation. On rotation, the activity is destroyed and recreated, and `onCreate` runs again — in Logcat you see `MainActivity: onCreate` again.

**What is missing compared to `G1097`:** the `EdgeToEdge.enable(this)` block and the insets listener. DMA02 does not have them. The consequence is visible on Android 15+: apps with `targetSdk ≥ 35` run edge-to-edge by default, and without a listener the content is drawn **under** the status bar — the toolbar goes under the clock. In `G1097`, `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` solves exactly this.

```java
    @Override
    protected void onDestroy() {
        super.onDestroy();                  // the framework's cleanup
        Log.w(TAG, "onDestroy");
    }

    @Override
    protected void onStart() {
        super.onStart();
        Log.w(TAG, "onStart");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.w(TAG, "onStop");
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.w(TAG, "onPause");
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.w(TAG, "onResume");
    }
```

**Why all six:** each override does exactly one thing — writes a row in Logcat. They are **observers**, not requirements: if you delete an entire method, the app still works, because the implementation from `AppCompatActivity` runs. You only lose the row in Logcat.

**Why `super` is first everywhere:** for a log, the order does not matter. But the convention for `onPause`, `onStop` and `onDestroy` is to do the cleanup **before** `super` (your resources still exist), and for `onCreate`, `onStart`, `onResume` — after `super`. Here all of them are after, for simplicity. What matters: `super` **must** be called. Without it, `ActivityThread` throws `SuperNotCalledException` after each method.

**The order in the file is not the execution order:** `onCreate`, `onDestroy`, `onStart`, `onStop`, `onPause`, `onResume` — again alphabetical, generated by IntelliJ. The real order at runtime:

```
startup:   onCreate → onStart → onResume
Home:      onPause → onStop
return:    onRestart → onStart → onResume
Back:      onPause → onStop → onDestroy
rotation:  onPause → onStop → onDestroy → onCreate → onStart → onResume
```

**Why `onDestroy` is not guaranteed:** if the system kills the process (low memory), `onDestroy` is not called. That is why you do not put data saving there — for saving there are `onPause`/`onStop` and `onSaveInstanceState`.

**Why the message is only `"onCreate"`:** in Logcat, the Tag column already says `MainActivity`, and the Message column says `onCreate`. Together: `MainActivity: onCreate`. The message does not repeat the tag.

```java
    public void pressMe(View view) {          // the signature is dictated by android:onClick="pressMe" in the XML
        // Variant 1, commented out: opens a URL in the default browser.
  /*      Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse("https://developer.android.com"));
        startActivity(web);*/
        // ↑ `Uri` is NOT imported in the file: if you uncomment the block, it does not compile.

        // Variant 2, commented out: opens the phone keypad, without dialing.
        /*Intent call = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0212345678"));
        startActivity(call);*/

        // Variant 3, active: share sheet.
        Intent share = new Intent(Intent.ACTION_SEND);                  // implicit Intent: action, no target class
        share.setType("text/plain");                                     // MIME — required for ACTION_SEND
        share.putExtra(Intent.EXTRA_TEXT, "Hello!");                     // the text that is sent
        startActivity(Intent.createChooser(share, "Share via DMA"));     // forced chooser, with a title

    }
}                                            // closes the MainActivity class
```

**Why the signature is exactly `public void pressMe(View view)`:** `android:onClick="pressMe"` in the layout is not a compile-time link, but a lookup **by reflection** at runtime. The framework looks in the view's Context (that is, in the activity) for a `public` method, returning `void`, with exactly one `View` parameter. If the name differs, the click crashes with:

```
IllegalStateException: Could not find method pressMe(View) in a parent or ancestor Context
for android:onClick attribute defined on view class android.widget.Button ...
```

**Why the `view` parameter is not used:** the method is called for a single button, so you do not need to tell the source apart. The parameter is required by the contract, even if you ignore it.

**Why the first two variants are commented out:** they are demonstrations kept in the code as teaching material. `ACTION_VIEW` + `https://` opens the browser; `ACTION_DIAL` + `tel:` opens the phone keypad **without** dialing — which is why it does not require the `CALL_PHONE` permission. The variant that actually dials, `ACTION_CALL`, would require it.

> The real trap: `Uri` is **not** imported (it does not appear in the import list). The blocks are commented out exactly so that it compiles. If you uncomment the first block, you get `cannot find symbol: class Uri` — you must add `import android.net.Uri;`.

**Why `ACTION_SEND` + `setType("text/plain")`:** an implicit `Intent` declares only **which operation** you want, not the class that performs it. The system looks for apps that have a matching `intent-filter`. `setType` is the main filter: without it, the system does not know which apps can receive the `Intent`.

| Deleted line | Effect |
|---|---|
| `share.setType("text/plain")` | no app matches; the chooser appears empty ("No apps can perform this action"), and a direct `startActivity` would give `ActivityNotFoundException` |
| `share.putExtra(Intent.EXTRA_TEXT, "Hello!")` | the share sheet opens, but the text sent is empty |
| `Intent.createChooser(...)` | Android may open the default share app directly, without a dialog |
| `startActivity(...)` | the `Intent` is built and thrown away; nothing happens |

**Why `createChooser`:** `ACTION_SEND` alone respects the default share app. `createChooser(intent, title)` **always** forces the choice dialog, with the given title ("Share via DMA"). It is useful when you want the user to decide consciously.

**Why `Intent.EXTRA_TEXT` and not `"android.intent.extra.TEXT"`:** the constant has exactly the same value, but the name is checked by the compiler. A hand-written string with a typo gives no error — the text just never arrives anywhere.

**The loop that closes:** the manifest declares an `intent-filter` for `ACTION_SEND` + `text/plain` (section 25.3). So **DMA02 appears in its own share sheet**. If you choose it, it starts a **second** instance of `MainActivity` (standard launch mode), and the first goes through `onPause` → `onStop`. And, because `MainActivity` never reads `getIntent().getStringExtra(Intent.EXTRA_TEXT)`, the received text is ignored: you only see a new, identical screen.

**Why `startActivity` and not `startActivityForResult`:** you do not need any result back. `startActivityForResult` (or `registerForActivityResult`) is used when you are waiting for data — as in `G1097`, with the form.

---

## 25.3 `AndroidManifest.xml`

### The complete file, annotated

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ↑ the XML declaration: a mandatory first line; without it, the build rejects the file. -->

<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
<!-- ↑ xmlns:android = the prefix of all android: attributes. xmlns:tools = the prefix of tools:;
     at d719ffc it is declared, but no tools: attribute appears in the file — a leftover from the template. -->

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
        <!-- ↑ each attribute, explained in the table below. -->

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <!-- ↑ the main activity: the only one in the app. -->

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <!-- ↑ filter 1: MAIN + LAUNCHER = the app appears in the launcher. -->

                <intent-filter>
                    <action android:name="android.intent.action.SEND" />
                    <category android:name="android.intent.category.DEFAULT" />
                    <data android:mimeType="text/plain" />
                </intent-filter>
            <!-- ↑ filter 2: receives text from the share sheet. Its indentation is inconsistent in the repo. -->


        </activity>
    </application>

</manifest>
```

**Why `android:name=".DMA02App"` is the most important line in the file:** it is the only link between the code from 25.1 and the runtime. The leading dot means "relative to the `namespace`" — that is, `ro.ase.ie.dma02.DMA02App`. Without the line, Android uses `android.app.Application` and your class is not instantiated. With the name written wrong (`DMA02App` without the dot, or another package), the app crashes at startup with `ClassNotFoundException`.

**The attributes in `<application>`:**

| Attribute | What it does | If you delete it |
|---|---|---|
| `android:name` | binds the `Application` class | the class does not run; no error, just silence |
| `android:allowBackup` | allows automatic backup of the app's data | the default applies (`true` on most devices) |
| `android:dataExtractionRules` | the backup/transfer rules for **Android 12+** | the default rules apply |
| `android:fullBackupContent` | the backup rules for **Android 11 and below** | the default rules apply |
| `android:icon` | the launcher icon | the system's default icon |
| `android:label` | the name shown under the icon and in recents | the app name becomes the package name |
| `android:roundIcon` | the round variant for launchers that ask for it | `android:icon` is used |
| `android:supportsRtl` | mirrors the layouts for RTL languages | the interface is no longer mirrored |
| `android:theme` | the app's theme | the platform theme: Material components no longer look right |

**Why two backup files:** `fullBackupContent` is read by Android 11 and below; `dataExtractionRules` by Android 12+. Both are generated by the template and cover two API ranges. If you delete the files `res/xml/backup_rules.xml` and `data_extraction_rules.xml` but leave the attributes, the build fails with "resource not found".

**Why `android:theme="@style/Theme.DMA02"`:** `Theme.DMA02` is defined in `res/values/themes.xml` as `parent="Base.Theme.DMA02"`, and `Base.Theme.DMA02` has **two** parents, depending on the system mode:

| File | Parent | Effect |
|---|---|---|
| `values/themes.xml` (light mode) | `Theme.Material3.Dark` | the app is **dark** and has an ActionBar |
| `values-night/themes.xml` (night mode) | `Theme.Material3.DayNight.NoActionBar` | the app is dark and has **no** ActionBar |

The result is a real inconsistency in the repo: the app is always dark, and the window title bar appears only in light mode — where, on top of it, there is also the `MaterialToolbar` from the layout. Nothing crashes, but it explains why the screen looks different with the system theme on light versus night.

**Why `android:exported="true"`:** from Android 12 (API 31), any component with an `intent-filter` must explicitly declare `exported`. Without the attribute, the build fails: "Apps targeting Android 12 and higher are required to specify an explicit value for `android:exported`". The value `true` is mandatory here: the launcher is **another** app, so it must be able to start `MainActivity`.

**Why `android:windowSoftInputMode="adjustResize"`:** when the keyboard appears, the window is resized so that it does not cover the active field. DMA02 has no text field at all, so the attribute is inert — a leftover from the template. On Android 15+, with edge-to-edge, `adjustResize` is ignored anyway in favor of insets.

**Why the `MAIN` + `LAUNCHER` filter:** `MAIN` says "this is the entry point"; `LAUNCHER` says "show me in the launcher". Without it, the app can only be started from another app or from `adb`, not from the icon.

**Why the `SEND` + `DEFAULT` + `text/plain` filter:** it filters which implicit `Intent`s the activity accepts. `DEFAULT` is mandatory for `startActivity`: the system resolves with `MATCH_DEFAULT_ONLY`, so a filter without `DEFAULT` never matches. `text/plain` limits it to text — without it, the app would appear in the share sheet for any content type.

> The filter is **only a receiver**. The code does not read the received text, so the app appears in the share sheet and ignores it. It is the second half of the demonstration from 25.2.

---

## 25.4 `activity_main.xml`

### The complete file, annotated

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">
    <!-- ↑ the root: ConstraintLayout, id `main` (unused in DMA02, used in G1097 for insets). -->

    <com.google.android.material.appbar.MaterialToolbar
        android:id="@+id/toolbar"
        android:layout_width="match_parent"
        android:layout_height="?attr/actionBarSize"
        app:title="@string/app_name"/>
    <!-- ↑ the title bar: no constraints, so ConstraintLayout places it at (0,0). -->

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
    <!-- ↑ the centered text: four constraints = centered horizontally and vertically. -->

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
    <!-- ↑ the button: `android:onClick="pressMe"` is the only XML → code link in the whole project. -->

</androidx.constraintlayout.widget.ConstraintLayout>
```

**Why `ConstraintLayout`:** each child is positioned through **relationships** relative to the parent or to siblings, not by order. It is the layout generated by the "Empty Views Activity" template and it suits simple screens: a centered text, a button above it.

**Why `android:id="@+id/main"`:** in DMA02 it is not used anywhere — no line of code calls `findViewById(R.id.main)`. In `G1097` it becomes essential: `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` needs it. If you delete it here, DMA02 still works; if you delete it in `G1097`, the app crashes at startup with `NullPointerException`.

**Why `tools:context=".MainActivity"`:** it tells the IDE which activity to use for the preview (theme, resolution of `android:onClick`). At build time, the attribute is stripped — it does not reach the APK.

**`MaterialToolbar`:**

```xml
android:layout_height="?attr/actionBarSize"
app:title="@string/app_name"
```

`?attr/actionBarSize` takes the standard bar height (56dp) from the theme. `app:title` is the Material attribute, not `android:title`. The toolbar is `match_parent` in width and has **no constraint** — in `ConstraintLayout`, a view without constraints is placed at the (0,0) corner with its measured size. It works, but "by accident": if you add another view above, the toolbar does not move.

> No code calls `setSupportActionBar(toolbar)`. So the toolbar is just a styled view with a title, not the activity's ActionBar: it receives no options menu, no back navigation button.

**`TextView`:**

```xml
android:text="Hello World!"
android:textAppearance="?attr/textAppearanceBodyLarge"
```

Four constraints (top, bottom, start, end) relative to the parent = centered on both axes. `?attr/textAppearanceBodyLarge` takes the "body large" typographic style from the Material 3 theme (16sp), instead of hardcoding `textSize`.

> `"Hello World!"` is hardcoded text: lint gives a `HardcodedText` warning, and the text cannot be translated. The correct approach would be `@string/hello_world` in `strings.xml`.

**`Button`:**

```xml
android:onClick="pressMe"
app:layout_constraintBottom_toTopOf="@+id/textView"
```

The button is tied to the `TextView` through `bottom_toTopOf`: it sits above the text, centered horizontally. Together with `top_toTopOf="parent"`, it occupies the upper half of the screen. `@+id/textView` also works without the `+` (the id is already declared above), but it is harmless.

> `android:onClick` is the **only** link between XML and code in the whole project. The name in the XML must be identical to the method in `MainActivity` — otherwise `IllegalStateException` on click, not at compile time.

**What happens if you delete each block:**

| Deleted block | Effect |
|---|---|
| the `Button` | `pressMe` can no longer be called; the app displays only the text |
| `android:onClick="pressMe"` | the click does nothing; no error, no trace in Logcat |
| the `TextView` | the `bottom_toTopOf` reference is left without a target: the constraint is ignored, and the button sticks to the top edge |
| `MaterialToolbar` | the screen is left without a title; the rest works |
| `android:id="@+id/main"` | nothing in DMA02; `G1097` would crash on insets |
| `xmlns:app` | all `app:` attributes become invalid → the build fails |

### Real traps in DMA02

| Place | Trap | Effect |
|---|---|---|
| `MainActivity` | `Uri` is not imported | you uncomment the `ACTION_VIEW` block → it does not compile |
| `MainActivity` | the methods are in alphabetical order | the order in the file ≠ the execution order |
| `MainActivity` | no `EdgeToEdge` + insets | on Android 15+ the content goes under the status bar |
| `AndroidManifest.xml` | the `SEND` filter is not read in the code | the app appears in the share sheet but ignores the text |
| `AndroidManifest.xml` | `adjustResize` with no text fields | inert attribute |
| `themes.xml` | `Theme.Material3.Dark` in `values`, `DayNight.NoActionBar` in `values-night` | the app is always dark; ActionBar only in light mode |
| `activity_main.xml` | toolbar without constraints | placed at (0,0) "by accident" |
| `activity_main.xml` | `"Hello World!"` and `"Button"` hardcoded | lint `HardcodedText`, no translation |

---

## 25.5 The complete flow

```
PROCESS STARTUP
  Zygote → fork → ActivityThread.main
    ├── Application.attachBaseContext()                 (does not appear in the code)
    ├── ContentProvider.onCreate()                      (if one exists; not the case here)
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
    └── you pick an app
          ↓
  MainActivity.onStart → onResume        (on return)

BACK PRESS (from MainActivity)
  onPause → onStop → onDestroy
    └── DMA02App.onActivityDestroyed

ROTATION
  onPause → onStop → onDestroy
  → onActivityCreated → onCreate → onStart → onResume    (new instance!)
```

**What you read from the diagram:**

1. `Application.onCreate` runs **before** any activity — which is why the subscription and the theme live there.
2. Each method of the activity has a paired callback, triggered from inside its `super`.
3. `pressMe` does not change any state: it only builds an `Intent` and hands control to the system.
4. On rotation, the full destruction and creation chain runs again — which is why `onCreate` appears twice in Logcat.

---

## 25.6 What to remember

| File | The essence |
|---|---|
| `DMA02App.java` | `Application` + `ActivityLifecycleCallbacks`; `onCreate` runs before any activity; `DynamicColors` is applied globally, only once |
| `MainActivity.java` | six lifecycle methods, all with `super` first; `pressMe` = implicit `Intent` with `ACTION_SEND` |
| `AndroidManifest.xml` | `android:name=".DMA02App"` binds the class; `exported="true"` mandatory; two filters: `LAUNCHER` and `SEND` |
| `activity_main.xml` | `ConstraintLayout`; `android:onClick="pressMe"` is the only XML → code link |

---

## Chapter 25 summary

- `Application` = the single object per process, created before any activity. Without `android:name` in the manifest, the class does not exist at runtime — no error, just silence.
- `Application.onCreate` is the place for global initializations: registering the callbacks and `DynamicColors`. Both must be done before the first activity.
- `ActivityLifecycleCallbacks` has seven abstract methods: you implement all of them or it does not compile. `onActivitySaveInstanceState` is the only empty one.
- The callbacks are triggered from inside the base method (`super.onX()`); because `MainActivity` calls `super` first, the log from `Application` appears first in Logcat.
- `MainActivity` overrides six methods only to log. Deleting an override breaks nothing; deleting `super` gives `SuperNotCalledException`.
- The order of the methods in the file is alphabetical, not chronological: `onCreate → onStart → onResume → onPause → onStop → onDestroy`.
- `android:onClick="pressMe"` requires exactly `public void pressMe(View)`; otherwise a crash on click, not at build time.
- `ACTION_SEND` without `setType` has no target; `createChooser` forces the choice dialog.
- The app appears in its own share sheet (the `SEND` filter), but it does not read the received text.
- `Uri` is not imported: the commented blocks in `pressMe` do not compile if you uncomment them.

**Back to** [cheatsheet](21%20-%20Cheatsheet.md) **or to** [the overview](index.html).
