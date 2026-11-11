# Chapter 37 — The concepts, explained

**Objective:** to be able to answer "why?" for every mechanism in the Android app. Not "how it is written", but **why it exists**, **what the code would do without it** and **what breaks** when you understand it wrong.

**What this chapter is not:**

- It is not a cheatsheet. The cheatsheet is chapter 21: there you have the table of methods and the five-step recipe. Here you have the mechanism behind it.
- It is not a recipe. The recipes are chapters 33–35: there you have "how to do X in 10 minutes". Here you have "why X works this way".
- It is not annotated code. The annotated code is chapter 22: there every line has the explanation glued to it. Here every **concept** has the explanation glued to it.

**How to read it:** 24 concepts, each with exactly six rubrics, always in the same order:

| Rubric | The question it answers |
|---|---|
| **What it is** | the definition, in 2–4 sentences, with no undefined jargon |
| **Why it exists** | what problem it solves, what you would do by hand without it |
| **How it works** | the mechanism, step by step, with a diagram where it helps |
| **What breaks without it** | the concrete error, the concrete wrong behaviour |
| **Where you see it in G1097** | file + method + real code |
| **The typical confusion** | what people believe wrongly, and why it is wrong |

**The golden rule of the chapter:** every statement is verifiable in the real code. When a concept does not appear in G1097, I say so explicitly and show where it appears in the course projects — `DMA02`, `DMA05`, `DMA06`.

**The source of truth:** `D:\tmp\claude\dma-annot\src-G1097\` — the eight files (`MainActivity.java`, `ItemActivity.java`, `Movie.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`, `strings.xml`), plus `build.gradle.kts` from `cod-final`.

**Why a whole chapter of "why":** at the test, half the marks are given for code that compiles, and the other half for explanations. "An adapter ties the data to the list" is not an explanation — it is a tautology. The explanation is: *who* calls the adapter's methods, *when*, and *what the code would do if the adapter did not exist*. This chapter is built exactly on that difference.

**The map of the chapter:**

| Group | Concepts | What it covers |
|---|---|---|
| The foundation | 37.1–37.4 | the app, `Context`, resources, the manifest |
| Drawing | 37.5–37.7 | the view tree, the three passes, the layouts |
| The code–XML link | 37.8–37.9 | `findViewById`, ViewBinding |
| Time | 37.10–37.13 | `Activity`, the lifecycle, state, `Application` |
| Events | 37.14–37.15 | listeners, lambda |
| Data | 37.16–37.20 | model, adapter, ViewHolder, LayoutManager, ListView vs RecyclerView |
| The boundaries | 37.21–37.24 | `Intent`, `Bundle`, `ActivityResultLauncher`, Gradle |

---

## Concept 37.1 — What an Android app is

**What it is**

An Android app is an **APK** — a zip archive with compiled code (`classes.dex`), compiled resources (`resources.arsc` plus the `res/` folders), a manifest in binary form and a signature. At install time the system gives it its own **Linux user identifier** and its own data directory, and from then on it runs in an isolated **process**, with its own permissions. The app has no `main()` written by you: the system starts it and calls its components.

**Why it exists**

Because a phone runs dozens of apps at once, written by people who do not trust each other, on a device with limited memory and with a user who can press Home at any moment. Without this wrapper you would be personally responsible for: starting the process, isolating it from other apps, freeing memory when the system needs it, the lifecycle of the screens, loading the resources that match the language and density, and updating the code without losing the user's data. Android gives you all of that in one package, and in exchange it asks you one single thing: to declare in the manifest which components you have, so the system knows what it can start.

**How it works**

The full chain, from the build to the first pixel:

```
1. BUILD (on your computer)
   .java sources ──javac──> .class ──d8──> classes.dex
   res/ + AndroidManifest.xml ──aapt2──> binary resources + resources.arsc
                                    |
                                    v
                              app-debug.apk  (signed zip)

2. INSTALL (on the phone)
   PackageManagerService reads the manifest
     -> registers the components in the system index
     -> assigns a Linux UID, e.g. u0_a231
     -> creates /data/data/ro.ase.ie.g1097/

3. LAUNCH (you tap the icon)
   Launcher sends Intent(ACTION_MAIN, CATEGORY_LAUNCHER)
     -> system_server resolves the Intent to MainActivity
     -> no process yet? Zygote forks a new one
     -> ActivityThread.main() starts the message loop (Looper)
     -> Application.onCreate()
     -> MainActivity.onCreate() -> onStart() -> onResume()
     -> the first draw
```

Three things the diagram shows and that are easy to forget:

1. **The process does not exist until it is needed.** The icon in the launcher does not keep the app in memory. After you press Home and the system needs RAM, the process can be killed completely, and when you come back it starts again, with `onCreate` again.
2. **`Application.onCreate()` runs before any activity.** That is why the global initialisations live there (see 37.13).
3. **The UID is the security boundary.** Two apps with different UIDs cannot read each other's files. That is the sandbox, and it is the reason `Context` makes sense (see 37.2): it knows whose UID you are.

**What breaks without it**

- **Without a distinct `applicationId`** (or with it changed between versions): Android treats the build as a new app. It installs side by side, with a different data directory, and the user sees two icons. The old data is left orphaned.
- **Without the `MAIN` + `LAUNCHER` filter**: the app installs, but has no icon in the launcher. There is no way for the user to start it — only `adb shell am start`.
- **With a `minSdk` higher than the phone's version**: the install fails with `INSTALL_FAILED_OLDER_SDK`, before a single line of code runs.
- **With a crash in `Application.onCreate()`**: the process dies before the first activity is created. You see the crash in logcat without any screen having appeared — a confusing symptom, because "my app did not even open".

**Where you see it in G1097**

`build.gradle.kts` fixes the identity of the app:

```kotlin
android {
    namespace = "ro.ase.ie.g1097"
    defaultConfig {
        applicationId = "ro.ase.ie.g1097"
        minSdk = 33
        targetSdk = 37
    }
}
```

`AndroidManifest.xml` declares the wrapper and the two components:

```xml
<application
    android:label="@string/app_name"
    android:theme="@style/Theme.G1097">
    <activity android:name=".activities.MainActivity" android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
    <activity android:name=".activities.ItemActivity" android:exported="false" />
</application>
```

`MainActivity` is the only activity with the `LAUNCHER` filter — so the only entry gate. `ItemActivity` has `exported="false"`, meaning no other app can start it; only G1097 can open it, through the `Intent` in `initListeners()`.

**The typical confusion**

"The app is `MainActivity`." No. The app is the installed package, with its UID and its process; `MainActivity` is just the first screen, an object that is created and destroyed several times during a single run. The practical consequence: if you want a value that survives between screens, you do not put it in an activity — you put it in a model, in an `Application` or on disk.

The second confusion: "if the app is in recents, it means it is running". No. Recents holds a **task**, that is, a list of activities and their saved state — not a process. The process can be killed at any moment, and when you come back Android recreates the activities from the saved state. That is exactly where the need for `onSaveInstanceState` comes from (see 37.12).

The third: "one process = one app". No. One app can run in several processes (if you declare `android:process`), and one process can host activities from several apps in certain cases. For G1097, the two activities run in the same process — that is why the serialisation in `Intent` seems "instant" and why `serialVersionUID` is not a real problem here (see 37.16).

---

## Concept 37.2 — The Context

**What it is**

`Context` is an abstract class in Android that represents **the link between your code and the app's environment**. Through it you reach the resources (`getResources()`), the app package (`getPackageManager()`), the system services (`getSystemService()`), the file folders (`getFilesDir()`), the preferences (`getSharedPreferences()`) and the starting of other screens (`startActivity()`). `Activity`, `Service` and `Application` **are** `Context`, because they inherit from it.

**Why it exists**

Because a class that wants to display a translated text needs the translation table, and that table belongs to the app, not to the class. Without `Context` you would have two options, both bad: either a static global (`App.resources`) that breaks when the app has several configurations, or the explicit passing of dozens of objects through constructors. `Context` solves the problem with a single parameter that encapsulates the whole environment.

It also has a security role: the `Context` object knows **whose** UID you are. When you call `getSharedPreferences("x", MODE_PRIVATE)`, Android does not check permissions — the file is already in your private directory, because the UID inside the `Context` decided the path.

**How it works**

The real hierarchy, simplified to what matters:

```
                Context  (abstract: getResources, startActivity, ...)
                   ^
                   |
            ContextWrapper  (delegate: all methods go to mBase)
             ^          ^
             |          |
  ContextThemeWrapper   Application
        ^                  (has Resources, but NO UI theme)
        |
   Activity  (has both a window and a theme, plus WindowManager)
```

`ContextWrapper` implements nothing: it holds an `mBase` field of type `Context` and forwards every call. `ContextImpl` is the real implementation, created by the system. When you write `this` inside an activity, `this` is a `ContextThemeWrapper` that delegates to a `ContextImpl` tied to your app.

The difference that matters at the exam:

| | `Activity` (activity Context) | `getApplicationContext()` |
|---|---|---|
| has a theme (`?attr/colorPrimary`) | yes | no |
| can open a window (dialog, `startActivity`) | yes | only with `FLAG_ACTIVITY_NEW_TASK` |
| lives as long as the activity | yes | as long as the process |
| suitable for a singleton | **no** (memory leak) | yes |

**What breaks without it**

- **`Toast.makeText(this, ...)` inside an anonymous class**: `this` is the listener object, not the activity. Compile error, `incompatible types: <anonymous OnClickListener> cannot be converted to Context`. Fix: `MainActivity.this`.
- **An activity `Context` held in a `static` field**: the activity can no longer be collected by the garbage collector after `onDestroy`, because a static reference keeps it alive. The symptom is not a crash, but memory that grows with every rotation.
- **`getApplicationContext()` used for a dialog**: `WindowManager$BadTokenException: Unable to add window -- token null is not for an application`. The Application has no window.
- **Resources read without a `Context`**: `getString(R.string.app_name)` does not exist as a static method. Without a `Context` you have nowhere to take the resource table from.

**Where you see it in G1097**

Three places, all instructive:

```java
// MainActivity.onCreate — `this` is MainActivity, so a Context.
// ArrayAdapter needs it in order to load android.R.layout.simple_list_item_1.
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

```java
// MainActivity.initListeners — here `this` is NOT a Context.
// We are inside an anonymous class, so `this` is the OnClickListener.
// That is why you write MainActivity.this, not `this`.
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        launcher.launch(intent);
    }
});
```

```java
// ItemActivity.showReleaseDatePicker — `this` is ItemActivity,
// and DatePickerDialog needs a themed Context to build its window.
new DatePickerDialog(
        this,
        new DatePickerDialog.OnDateSetListener() { ... },
        releaseCal.get(Calendar.YEAR),
        ...
).show();
```

In `DMA06`, `NumberListAdapter` receives a `Context` through the constructor and uses it only for `LayoutInflater.from(context)` — the adapter needs nothing more, and it is a good example of minimal dependency:

```java
public NumberListAdapter(Context context, List<Integer> numbers) {
    this.layoutInflater = LayoutInflater.from(context);
    this.numbers = numbers;
}
```

**The typical confusion**

"`Context` is the app." Not quite: `Context` is the **interface to** the app. There are several `Context` objects in the same process — one per activity, one per service, one for `Application` — and they all delegate to the same `ContextImpl`. That is why `this` and `getApplicationContext()` are not interchangeable.

The second confusion: "`getApplicationContext()` is always the safe option". It is the safe option for **lifetime**, not for **functionality**. You are missing the theme, so any widget that reads `?attr/colorPrimary` will throw `InflateException` or take the default values. The practical rule: in the UI you use `this` (the activity); in a singleton or in an object that outlives the screen, you use `getApplicationContext()`.

The third: "`Context` is passed everywhere, as one extra parameter". No. An adapter needs it only to obtain a `LayoutInflater` or a `Resources`; if you keep it just to have it, you have coupled the class to the app's UI. The `NumberListAdapter` above is the correct model: it takes a `Context`, immediately extracts what it needs, and does not keep it.

---

## Concept 37.3 — Resources and the R class

**What it is**

Resources are everything that is not code: XML layouts, texts, colours, dimensions, images, strings, styles. They live in subfolders of `res/` (`layout/`, `values/`, `drawable/`, `mipmap/`, `xml/`). At build time, the **aapt2** tool compiles them into binary form and generates a Java class called **`R`**, in the package declared by `namespace`, which contains one `int` constant for each resource. `R.layout.activity_main`, `R.id.etTitle`, `R.array.movie_genre` are numbers, not objects.

**Why it exists**

Because the same code has to look different on different screens, in different languages, in dark mode. If you wrote `"Movie details"` directly in the code, you would have a single variant; if you wrote the file path, you would have a fragile string that breaks at every rename. `R` solves both: it gives you a **stable name at compile time** (`R.string.movie_details`) for a resource that is **resolved at runtime** into the variant that matches the current configuration. You write the name; the system picks the file.

**How it works**

```
res/
├── layout/activity_main.xml ──┐
├── layout/activity_item.xml ──┤
├── values/strings.xml ────────┤   aapt2
├── values/themes.xml ─────────┼──────────> R.java  (generated, do NOT edit)
├── drawable/outline_add_24.xml┤            public static final class id {
└── mipmap/ic_launcher.xml ────┘                public static final int etTitle = 0x7f0800a1;
                                                public static final int listView = 0x7f0800f3;
                                            }
                                            public static final class layout {
                                                public static final int activity_main = 0x7f0b001c;
                                            }
                                                     +
                                            resources.arsc  (the name -> value table, per configuration)
```

At runtime, `setContentView(R.layout.activity_main)` receives an `int`, looks it up in `resources.arsc`, finds the binary XML file and hands it to `LayoutInflater`. `findViewById(R.id.etTitle)` also receives an `int` and compares it with the IDs assigned to each view **during inflation**. So: `R.id.etTitle` is not the "name" of the view, it is a number that has to be identical in two places — in the XML and in the code.

The XML syntax has two forms that are often confused:

| Form | Meaning |
|---|---|
| `@+id/etTitle` | **creates** the ID if it does not already exist (the `+` sign) |
| `@id/etTitle` | **refers to** an ID that was already created |
| `@string/app_name` | refers to a resource in `values/strings.xml` |
| `@array/movie_genre` | refers to a `<string-array>` |
| `@drawable/outline_add_24` | refers to a vector or bitmap image |
| `@style/Theme.G1097` | refers to a style |
| `?attr/colorPrimary` | refers to an **attribute of the current theme**, not to a fixed resource |
| `@android:drawable/ic_menu_save` | refers to a resource of the **system**, not of yours |

**What breaks without it**

- **"Cannot resolve symbol R"**: it is not a resource problem, it is a **failed build**. `R.java` is generated only if aapt2 succeeded. Fix: Build → Clean Project, then Rebuild, and read the first error in the Build Output, not the last.
- **`AAPT: error: resource string/foo not found`**: you referred to a resource that does not exist. The build fails, but the message is clear — unlike missing IDs at runtime.
- **`Resources$NotFoundException`**: the resource exists at compile time but cannot be loaded at runtime — typically a wrong theme in the manifest or an `@style` that refers to another, non-existent `@style`.
- **`findViewById` returns `null`**: the ID exists in `R` (so compilation passes), but the view is not in the tree you are searching. The cause is not the resource, it is the wrong layout or the order of the calls (see 37.8).

**Where you see it in G1097**

`activity_main.xml` refers to three resources at once:

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:contentDescription="Add"
    app:srcCompat="@drawable/outline_add_24" />
```

`activity_item.xml` refers to an array defined in `strings.xml`:

```xml
<Spinner
    android:id="@+id/spGenre"
    android:entries="@array/movie_genre" />
```

and `strings.xml` contains exactly that array:

```xml
<string-array name="movie_genre">
    <item>Drama</item>
    <item>Action</item>
    ...
    <item>Mystery</item>
</string-array>
```

The consequence: `spGenre` has 10 elements **without `ItemActivity` writing a single letter of a genre**. `fillForm` only looks the text up in the list:

```java
for (int index = 0; index < spGenre.getCount(); index++) {
    if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
        spGenre.setSelection(index);
        break;
    }
}
```

If you add "Documentary" to `strings.xml`, the code sees it automatically. If you add it only in the code, the spinner does not have it.

`MainActivity` also uses a resource of the **system**, not of the app:

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

`android.R.layout.simple_list_item_1` is a layout shipped by Android, with a single `TextView`. You can see the `android.` prefix — that is what distinguishes it from `R.layout.*`, which is yours.

**The typical confusion**

"`R` is a class I write myself." No. `R.java` is generated on every build in `build/generated/`, and if you edit it, the changes disappear. That is why it does not appear in `src/` and why you will never find it in the repo.

The second: "the values in `R.id` are stable, I can save them". No. They are generated by aapt2 and can change from one build to the next when you add or remove resources. You never persist an `R.id` in a file, in a database or in a `SharedPreferences`. You persist the name (`"etTitle"`) or, better, a key of your own.

The third: "`@+id/` and `@id/` are synonyms". No. `@+id/x` **declares**; `@id/x` **refers**. If you use `@id/x` without having declared `x` anywhere, the build fails with `resource id/x not found`. In practice, the first occurrence in a file uses `@+id/`, the rest use `@id/` — but in day-to-day code you put `@+id/` everywhere, because it is idempotent.

The fourth, the most costly at the test: "`?attr/colorPrimary` and `@color/purple_500` are the same thing". No. `@color/...` is a fixed colour. `?attr/...` is a **theme role**: it is resolved at runtime to the colour the theme assigns to that role, so it changes automatically in dark mode. `activity_item.xml` uses `?attr/colorSurface`, `?attr/colorOnSurface`, `?attr/colorPrimary` for exactly this reason.

---

## Concept 37.4 — AndroidManifest.xml

**What it is**

`AndroidManifest.xml` is **the contract between your app and the operating system**. It declares which components the app has (`activity`, `service`, `broadcast receiver`, `content provider`), which permissions it requests, which theme it uses, which `Application` class runs and which `Intent`s each component can receive. The system reads it **at install time**, not at runtime, and builds from it the index through which it resolves any `Intent`.

**Why it exists**

Because the system has to know what it can start **before** it loads your code. When you tap an icon, Android does not have your process running yet — it only has a database of installed packages. Without the manifest, `startActivity(new Intent(this, ItemActivity.class))` would be a call to a class the system knows nothing about: it would not know whether it may create it, in which process, with which theme, with which keyboard mode.

It also has a security role. `android:exported` is the boundary: an activity with `exported="true"` can be started by any app on the phone; one with `exported="false"` only by your app. Without this declaration, any app could open any screen of anyone.

**How it works**

```
INSTALL
  APK -> PackageManagerService.parse
       -> for each <activity>: registers (class name, intent-filter, exported, theme)
       -> checks the requested permissions
       -> the index is now in /data/system/packages.xml

LAUNCH
  Explicit Intent  -> has the component (package + class) -> looks it up directly
  Implicit Intent  -> has action + category + data        -> matches against the intent-filters
                    -> 0 matches:  ActivityNotFoundException
                    -> 2+ matches: "Open with" dialog
                    -> checks exported before starting
```

The order of priority between manifest and code, which people often get backwards: **the manifest wins** for everything that belongs to the system (whether it can be started, with which theme, in which process, with which `launchMode`), and **the code wins** for everything that belongs to behaviour (what `onCreate` does, which listeners the button has). You cannot start an activity declared `exported="false"` from another app, no matter how much code you write.

**What breaks without it**

- **Undeclared activity**: `ActivityNotFoundException: Unable to find explicit activity class {ro.ase.ie.g1097/ro.ase.ie.g1097.activities.ItemActivity}. Have you declared this activity in your AndroidManifest.xml?` — the message tells you exactly what is missing.
- **Wrong `android:name`**: if you write `android:name="ItemActivity"` with no dot and no package, Android looks for `ro.ase.ie.g1097.ItemActivity`, not `.activities.ItemActivity`. The result is still `ActivityNotFoundException`, but the cause is different.
- **Missing `android:exported` on API 31+**: if the activity has an `<intent-filter>`, the build fails with a message from the manifest merger asking for an explicit value for `android:exported` on that component. It is not a warning, it is a build error.
- **Non-existent theme**: `Resources$NotFoundException` at startup, before `onCreate` — a crash you cannot catch in code.
- **Missing `LAUNCHER` filter**: the app installs, but does not appear in the launcher (see 37.1).

**Where you see it in G1097**

The whole file has 30 lines and every one of them matters:

```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:supportsRtl="true"
    android:theme="@style/Theme.G1097">
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
</application>
```

Four decisions, each with a consequence:

1. **`MainActivity` has `exported="true"`** because the launcher is another app and has to be able to start it. Without `true`, the icon would not work.
2. **`ItemActivity` has `exported="false"`** because it is an internal screen. Nobody from outside has any business in the movie form.
3. **`android:windowSoftInputMode="adjustResize"` on both** — when the keyboard appears, the window shrinks, and the `ScrollView` in `activity_item.xml` can scroll to the active field. Without it, the keyboard would cover the field.
4. **`android:theme="@style/Theme.G1097"` on `<application>`**, not on each activity — the theme is inherited. That is where all the `?attr/colorPrimary` in the layouts come from.

Notice what is **not** in the manifest: no layout, no `findViewById`, no logic. The manifest does not say what the app does, it only says **what exists** in it.

**The typical confusion**

"The manifest declares the layout." No. The layout is bound in code, through `setContentView(R.layout.activity_main)`. The manifest does not know what a layout is.

The second: "`exported="true"` means it is public/important". It only means **startable from another app**. An activity with `exported="false"` can be perfectly functional and essential — `ItemActivity` is exactly that.

The third: "I have to declare all the classes in the manifest". No, only the system's **components**: activities, services, receivers, providers. `Movie` does not appear in the manifest and does not need to.

The fourth, specific to this project: "if I add a new activity, I add it only in the code". If you do not declare it, `startActivity` throws `ActivityNotFoundException`. And the other way round: if you declare it but do not use it, nothing breaks — the system index just has a useless entry.

---

## Concept 37.5 — View and ViewGroup: the view tree

**What it is**

`View` is the base class for **any visual element**: a rectangle that knows how to draw itself, to receive touch, to have an ID, a position, a size and a visibility. `ViewGroup` is a subclass of `View` that **contains other `View`s** and decides where they sit. A `TextView` is a `View`; a `LinearLayout` is a `ViewGroup`; a `LinearLayout` that contains a `TextView` is a tree with two nodes.

**Why it exists**

Because an interface is a **composition**, not a flat list. A movie card has an image, a title, a subtitle, a rating bar and three chips — and the card sits in a list, which sits in a `FrameLayout`, which sits in a window. The tree is not an aesthetic choice: it is the only structure that allows **a single recursive traversal** for measuring, for drawing and for distributing touch. Without it you would need absolute coordinates for every element, and any change in screen size would ruin everything.

**How it works**

`LayoutInflater` reads the XML and, for each tag, creates the corresponding object **by reflection**, calling the two-parameter constructor `(Context, AttributeSet)`. `<FrameLayout>` becomes `new FrameLayout(context, attrs)`, `<TextView>` becomes `new TextView(context, attrs)`, and `<com.google.android.material.card.MaterialCardView>` becomes that class, with the full name. Then each child is added to its parent, and the parent keeps it in an internal list.

The tree of the main screen in G1097 (simplified — the upper part of the tree belongs to the system and the theme, not to your layout):

```
DecorView                       <- created by the system, not by you
└── LinearLayout (vertical)
    ├── [title bar / AppBar]    <- from the theme
    └── FrameLayout  android.R.id.content   <- this is where your layout goes
        └── FrameLayout  @id/main           <- the root from activity_main.xml
            ├── ListView  @id/listView
            │   ├── TextView   (row 0, inflated from simple_list_item_1)
            │   ├── TextView   (row 1)
            │   └── TextView   (row 2)
            └── FloatingActionButton  @id/floatingActionButton
```

And the tree of the form, which is deeper:

```
ScrollView  @id/main
└── LinearLayout (vertical)
    ├── TextView  "Movie details"
    ├── TextView  "Fill in the information below and save."
    ├── MaterialCardView  (Basics)
    │   └── LinearLayout (vertical)
    │       ├── TextView  @id/tvTile
    │       ├── TextInputLayout -> TextInputEditText @id/etTitle
    │       ├── TextView  @id/tvGenre
    │       ├── MaterialCardView -> Spinner @id/spGenre
    │       └── TextInputLayout -> TextInputEditText @id/etRelease
    ├── MaterialCardView  (Production)
    │   └── LinearLayout (vertical)
    │       ├── TextView @id/tvBudget
    │       ├── TextInputLayout -> TextInputEditText @id/etBudget
    │       ├── LinearLayout -> TextView @id/tvDuration + TextView @id/tvDurationValue
    │       ├── SeekBar @id/sbDuration
    │       └── LinearLayout -> two TextView (0 min / 300 min)
    ├── MaterialCardView  (Your verdict)
    │   └── LinearLayout (vertical)
    │       ├── TextView @id/tvRating
    │       ├── RatingBar @id/rbRating
    │       ├── View (separator 1dp)
    │       ├── LinearLayout -> TextView @id/tvWatched + TextView @id/tvWatchedValue
    │       │                    + MaterialSwitch @id/swWatched + MaterialCheckBox @id/cbOnWatchList
    │       ├── View (separator 1dp)
    │       ├── TextView @id/tvGuidance
    │       └── HorizontalScrollView -> RadioGroup @id/rgApproval -> 5 MaterialRadioButton
    ├── MaterialCardView  (Poster)
    │   └── LinearLayout -> TextInputLayout -> TextInputEditText @id/etPoster
    └── MaterialButton @id/btnMovieAction
```

Two direct consequences of the tree, which you will use at the test:

1. **`findViewById` searches the subtree**, not the whole app. If you call it on `rgApproval`, it finds only what is under it. If you call it on the `Activity`, it searches from `DecorView` down — so it finds everything in the layout set with `setContentView` (see 37.8).
2. **The order of the children is the order of drawing.** In a `FrameLayout`, the last child is drawn on top of the others. That is why the FAB comes after the `ListView` in `activity_main.xml` — otherwise it would be covered by the list.

**What breaks without it**

- **`IllegalStateException: ScrollView can host only one direct child`**: `ScrollView` is a `ViewGroup` that accepts exactly one child, because it has no way of deciding how to split the height between two. In `activity_item.xml`, that is exactly why all the content sits in a single `LinearLayout`.
- **A view added in code without `LayoutParams`**: `addView(view)` with no parameters uses the parent's default `LayoutParams`, which may be `WRAP_CONTENT`/`WRAP_CONTENT` — the element appears, but not where you expect.
- **`findViewById` on a view that is not in the tree**: it returns `null`, with no error. The symptom is a `NullPointerException` later, in a completely different method.
- **A `ViewGroup` that is not a `View`**: there is no such thing. `ViewGroup extends View`, so a `LinearLayout` can be put anywhere a `View` is accepted — including as a leaf inside another `LinearLayout`.

**Where you see it in G1097**

`activity_main.xml` is the simplest tree in the project — two leaves in a `FrameLayout`:

```xml
<FrameLayout
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">
    <ListView android:id="@+id/listView" ... />
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_gravity="bottom|end" ... />
</FrameLayout>
```

`activity_item.xml` shows the composition on four levels, with `MaterialCardView` as the section:

```xml
<ScrollView android:id="@+id/main" android:fillViewport="true">
    <LinearLayout android:orientation="vertical">
        <com.google.android.material.card.MaterialCardView>
            <LinearLayout android:orientation="vertical">
                <TextView android:id="@+id/tvTile" />
                <com.google.android.material.textfield.TextInputLayout>
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle" />
                </com.google.android.material.textfield.TextInputLayout>
```

`movie_item.xml` shows the tree of a **row**, not of a screen — and it is the only layout in G1097 that is not used yet:

```xml
<com.google.android.material.card.MaterialCardView>
    <LinearLayout android:orientation="horizontal">
        <ImageView android:id="@+id/moviePoster" />
        <LinearLayout android:layout_width="0dp" android:layout_weight="1"
                      android:orientation="vertical">
            <TextView android:id="@+id/movieTitle" />
            <TextView android:id="@+id/movieSubtitle" />
            ...
```

**The typical confusion**

"The root in the XML is the root of the screen." No. Above it there is also `android.R.id.content` (a `FrameLayout` put there by `AppCompatActivity`) and `DecorView`, put there by the system. The practical consequence: `findViewById(R.id.main)` finds your root, but `getWindow().getDecorView()` returns something completely different — and that is why the insets listener in G1097 is set on `R.id.main`, not on the decor.

The second: "`ViewGroup` and `View` are different things". `ViewGroup` **is** a `View`, with the right to have children. That is where the flexibility comes from: you can put a `LinearLayout` anywhere a `TextView` fits, and you can treat any `ViewGroup` as a `View` when you do not care about its children.

The third: "if a view is not visible, it does not exist". It exists, it just has `visibility="gone"` (it takes no space) or `"invisible"` (it takes space, but is not drawn). `findViewById` finds it in both cases, and `getWidth()` can be 0 for a `GONE`.

---

## Concept 37.6 — How a screen is drawn: measure, layout, draw

**What it is**

Drawing a screen happens in **three recursive passes** over the view tree: **measure** (how big each view wants to be), **layout** (where each one sits, in absolute coordinates relative to the parent) and **draw** (the actual drawing on a `Canvas`). Each step goes down from the root to the leaves, and the result of each one feeds the next.

**Why it exists**

Because the screen size is not known at compile time. One phone has 1080×2400 pixels, another 1440×3120, a tablet has a different ratio, and the user can rotate the screen or open the keyboard at any moment. If you wrote fixed coordinates, the layout would break on any other device. The three passes are the mechanism through which a **declarative** layout ("put it under the title, fill the width") becomes **concrete** positions ("left=0, top=312, right=1080, bottom=420").

**How it works**

The key is `MeasureSpec`: a packed `int` that contains a **mode** and a **size**.

| Mode | Meaning | Who gives it |
|---|---|---|
| `EXACTLY` | "you have exactly this many pixels" | the parent, when the child has `match_parent` or a fixed size |
| `AT_MOST` | "you have at most this many" | the parent, when the child has `wrap_content` |
| `UNSPECIFIED` | "do as you like" | a vertical `ScrollView`, a horizontal `HorizontalScrollView` |

The passes, on a real example from `movie_item.xml` — the text column has `layout_width="0dp"` and `layout_weight="1"`:

```
1. MEASURE  (top to bottom)
   the parent receives a MeasureSpec from its own parent
     -> computes the MeasureSpec of each child
     -> the child with wrap_content receives AT_MOST(the parent's width)
     -> the child with 0dp + weight receives, on the first pass, 0 or AT_MOST
     -> the parent adds up the requested heights, then splits the REST by weight
     -> second pass: the child with weight receives EXACTLY(the remaining space)
     -> each view saves its getMeasuredWidth() / getMeasuredHeight()

2. LAYOUT   (also top to bottom)
   the parent knows its absolute position
     -> computes the position of each child relative to it
     -> child.layout(left, top, right, bottom)
     -> each view saves getLeft(), getTop(), getWidth(), getHeight()

3. DRAW     (also top to bottom)
   the canvas draws: background -> own content (onDraw) -> children -> scrollbars
     -> a TextView draws the text, an ImageView draws the bitmap
     -> a ViewGroup draws nothing of its own, it only calls its children
```

What starts the three passes: `Choreographer`, synchronised with the screen's vsync (60, 90 or 120 times per second). When something changes, the view asks for a new pass:

| Call | What it invalidates | When you use it |
|---|---|---|
| `requestLayout()` | measure + layout + draw | you changed a size, a text that changes the height, you added a child |
| `invalidate()` | draw only | you changed a colour, a displayed value, without the size changing |

`setText()` on a `TextView` calls `requestLayout()` by itself if the new text has a different size — that is why you do not have to do it yourself. `setPadding()` calls `requestLayout()` — hence the effect of the insets listener in G1097.

**What breaks without it**

- **`getWidth()` in `onCreate()` returns 0**: in `onCreate` the tree exists (after `setContentView`), but has not been measured yet. The first measurement happens after `onResume`, when the window becomes visible. Fix: `view.post(() -> ...)` or `doOnLayout`.
- **`0dp` without `layout_weight`**: `0dp` means "zero pixels", not "fill". If you forget `weight`, the element disappears completely — you get no error, you get an empty space.
- **`layout_weight` on `wrap_content`**: it works, but it splits **the remaining space** after each child has taken its natural size. It is a classic source of layouts that look "almost right".
- **`ScrollView` with a `match_parent` child vertically**: `ScrollView` gives `UNSPECIFIED` vertically, so `match_parent` has nothing to relate to. That is why `activity_item.xml` has `android:fillViewport="true"` — it forces the child to fill the viewport when the content is shorter, without breaking scrolling when it is longer.

**Where you see it in G1097**

`movie_item.xml` — `0dp` + `weight` for the text column, so that it takes everything left after the poster:

```xml
<ImageView
    android:id="@+id/moviePoster"
    android:layout_width="96dp"
    android:layout_height="140dp" />

<LinearLayout
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    android:layout_weight="1"
    android:orientation="vertical">
```

`activity_recycler_view.xml` from `DMA06` — the same mechanism, vertically, so that the `RecyclerView` takes all the space left under the header:

```xml
<include layout="@layout/layout_number_header" />
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/rvNumbers"
    android:layout_width="match_parent"
    android:layout_height="0dp"
    android:layout_weight="1" />
```

`activity_item.xml` — `fillViewport`, which changes the child's MeasureSpec:

```xml
<ScrollView
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true">
```

And the insets listener in both activities, which **deliberately** causes a new layout pass:

```java
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
    return insets;
});
```

`setPadding` changes the usable size of the root, so it asks for `requestLayout()`. Without this call, the content would sit under the status bar — `EdgeToEdge.enable(this)` makes the window draw under the bars, and the padding is the compensation.

**The typical confusion**

"`match_parent` and `0dp` + `weight` are equivalent." No. `match_parent` asks for **all** of the parent's size, regardless of siblings — so in a horizontal `LinearLayout`, two children with `match_parent` overlap each other. `0dp` + `weight` asks for **a part** of the remaining space, proportional to `weight`. `match_parent` = "all of it", `0dp`+`weight` = "my share".

The second: "`onCreate` knows how big the screen is". No. `onCreate` builds the tree; the measurement happens afterwards, in the first layout pass. Any code that depends on dimensions has to be deferred.

The third: "`invalidate()` and `requestLayout()` are synonyms". No. `invalidate()` only redraws, keeping the positions; `requestLayout()` re-measures the whole subtree. If you change the text of a `TextView` and call only `invalidate()`, the new text can be cut off, because the height was not recalculated.

The fourth: "the three passes are separate in time". They are separate **logically**, but they run in the same drawing pass, one after the other, synchronised with vsync. That is why a layout change in `onCreate` produces no flicker: everything is resolved before the first frame is displayed.

---
## Concept 37.7 — The layouts: FrameLayout, LinearLayout, ConstraintLayout, ScrollView

**What it is**

A layout is a `ViewGroup` that implements an **arrangement rule** for its children. `FrameLayout` stacks them on top of each other, in the top-left corner. `LinearLayout` puts them in a single row or a single column, in the order from the XML. `ConstraintLayout` positions them through relations to the parent and to their siblings. `ScrollView` is a special `FrameLayout` that accepts **a single child** and lets it be taller than the screen, allowing scrolling.

**Why it exists**

Because "where each element sits" does not have a single correct answer. A screen with a single piece of content wants a `FrameLayout`; a form wants a column; a screen that has to look good on both phone and tablet wants relative constraints. If there were a single layout, it would have to be general enough for all of them — and it would be hard to use for any of them. Android chose **specialised layouts**, each with a simple algorithm, and you pick the right algorithm. It is exactly the opposite of a framework with absolute positioning: you do not say where, you say by which rule.

**How it works**

Each layout implements its own `onMeasure` and `onLayout`. The difference between them is the **algorithm**, not the API.

**`FrameLayout`** — a stack, all children in the top-left corner, the last one drawn on top:

```
+---------------------------+
| [child 1]                 |
| [child 2]  <- on top      |
| [child 3]                 |
+---------------------------+
```

The children can be moved with `android:layout_gravity` (`bottom|end`, `center`). It has no `weight`, no orientation. The order in the XML is the z-order.

**`LinearLayout`** — a single axis, `orientation="horizontal"` or `"vertical"`:

```
vertical:                     horizontal:
+-------------------+         +--------+--------+--------+
| [child 1]         |         | child1 | child2 | child3 |
| [child 2]         |         +--------+--------+--------+
| [child 3]         |
+-------------------+
```

The maths of `weight`, which is asked at the test:

```
total space of the parent:             360dp
children without weight ask for:        96dp + 12dp (margin) = 108dp
space left:                            360 - 108 = 252dp
sum of the weights:                    1
each child with weight:                252 * (weight / sum) = 252dp
```

So `weight` does **not** split the whole space, it splits **the rest**. If all the children have `0dp` + `weight`, then the rest is the whole space, and it looks like it splits everything — hence the confusion.

**`ConstraintLayout`** — each child has at least one horizontal and one vertical constraint:

```
        parent top
            |
   +--------+--------+
   |  [TextView]     |  <- start -> parent start, top -> parent top
   +--------+--------+
            |
        parent bottom
```

It has `app:layout_constraintStart_toStartOf`, `..._toEndOf`, `app:layout_constraintHorizontal_bias` (0 = left, 0.5 = centre, 1 = right), chains and `Guideline`. Its real advantage: **a single level of depth** for complex layouts, so measure does not repeat N times.

**`ScrollView`** — a `FrameLayout` that gives the child `UNSPECIFIED` vertically:

```
+-------------------+  <- viewport (the height of the screen)
| visible content   |
| ...               |
+-------------------+
| hidden content    |  <- it exists, you reach it by scrolling
| ...               |
+-------------------+
```

`android:fillViewport="true"` changes the behaviour when the content is **shorter** than the viewport: it stretches it to fill the screen. Without it, a short form would leave an empty area underneath, and the background would be the window's, not the content's.

**What breaks without it**

- **`FrameLayout` with `android:orientation`**: the attribute is **ignored**, with no warning in the build. That is exactly what happens in `activity_main.xml` in G1097 — it has `android:orientation="horizontal"` on a `FrameLayout`. It breaks nothing, but it betrays a misunderstanding: orientation makes no sense in a stack.
- **`ScrollView` with two children**: `IllegalStateException: ScrollView can host only one direct child`. It is not an arbitrary limitation — `ScrollView` has no way of deciding how to split the scrolling between two independent children.
- **`ConstraintLayout` with a child that has no constraints**: the view "jumps" to the top-left corner, with no error. Android Studio warns in the editor ("This view is not constrained"), but the build passes.
- **Horizontal `LinearLayout` with too many children**: they get squeezed and the last ones go off the screen, with no scroll. The symptom is cut-off content, not a crash.
- **`weight` forgotten on `0dp`**: the element has zero size and disappears. See 37.6.

**Where you see it in G1097**

`activity_main.xml` — a `FrameLayout` with two leaves, the FAB positioned with `layout_gravity`:

```xml
<FrameLayout
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">          <!-- ignored: FrameLayout has no orientation -->

    <ListView android:id="@+id/listView" ... />

    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp" ... />
</FrameLayout>
```

`activity_item.xml` — a `ScrollView` with **a single** vertical `LinearLayout` child, which contains four `MaterialCardView`s:

```xml
<ScrollView android:id="@+id/main" android:fillViewport="true">
    <LinearLayout android:orientation="vertical" android:paddingHorizontal="16dp">
        <MaterialCardView> ... Basics ... </MaterialCardView>
        <MaterialCardView> ... Production ... </MaterialCardView>
        <MaterialCardView> ... Your verdict ... </MaterialCardView>
        <MaterialCardView> ... Poster ... </MaterialCardView>
        <MaterialButton android:id="@+id/btnMovieAction" />
    </LinearLayout>
</ScrollView>
```

`movie_item.xml` — a horizontal `LinearLayout` with `weight` on the text column, and an inner horizontal `LinearLayout` for the rating row:

```xml
<LinearLayout android:orientation="horizontal" android:padding="12dp">
    <ImageView android:layout_width="96dp" android:layout_height="140dp" />
    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">
        ...
        <LinearLayout android:orientation="horizontal" android:gravity="center_vertical">
            <RatingBar android:id="@+id/movieRating" ... />
            <TextView android:id="@+id/movieRatingValue" ... />
        </LinearLayout>
```

`DMA02/activity_main.xml` — `ConstraintLayout`, the only one in the course projects that uses it:

```xml
<androidx.constraintlayout.widget.ConstraintLayout android:id="@+id/main">
    <com.google.android.material.appbar.MaterialToolbar
        android:id="@+id/toolbar"
        android:layout_height="?attr/actionBarSize" />
    <TextView
        android:id="@+id/textView"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    <Button
        android:id="@+id/button"
        app:layout_constraintBottom_toTopOf="@+id/textView"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

**The typical confusion**

"`FrameLayout` is for fragments, `LinearLayout` for the rest." There is no such rule. `FrameLayout` is the right choice whenever you have **overlapping elements** — a piece of content and a floating button over it, exactly as in `activity_main.xml`.

The second: "`weight` splits the total width". It splits **the rest**, after each child has taken its own size. If a child has a fixed `100dp`, that `100dp` is taken out of the calculation before the split.

The third: "`ConstraintLayout` is always better". It is better when you have many relations between elements; it is **worse** when you have a simple column, because you add constraints for nothing. `activity_item.xml` uses `LinearLayout` for a column — the correct choice.

The fourth: "`ScrollView` makes any content scrollable". No: only vertically, only one child, and only if that child is taller than the viewport. For horizontal you have `HorizontalScrollView` — used in `activity_item.xml` for the row of five radio buttons, which do not fit on a narrow screen.

---

## Concept 37.8 — findViewById and why it is fragile

**What it is**

`findViewById(int id)` is the method through which you ask a view — or an activity — to search its tree for a view with the given ID and return it. The signature is generic: `<T extends View> T findViewById(int id)`, which means **the type is inferred from the assignment**. It checks nothing at runtime: it does a cast, and if the type does not match, you get a `ClassCastException`.

**Why it exists**

Because XML and Java are two separate languages, and the link between them is made at runtime. In the XML you declared `<TextInputEditText android:id="@+id/etTitle" />`; in Java you need a reference to that object in order to read it. `findViewById` is the bridge: an `int` generated by aapt2, looked up in a tree of objects created by `LayoutInflater`.

**How it works**

There are **two** methods with the same name, and their difference is asked at the test:

| Call | Where it searches |
|---|---|
| `activity.findViewById(id)` | from `DecorView` down — that is, the whole screen, including the title bar |
| `view.findViewById(id)` | only in that view's subtree |

The implementation in `View` is a depth-first search with an ID check:

```
View.findViewById(id)
  ├── if this.mID == id -> return this
  └── if this is a ViewGroup -> for each child:
        └── child.findViewById(id)   (recursively)
  └── if nothing was found -> return null
```

The cost is proportional to the number of views in the subtree. For a form with 30 views and 13 calls, the cost is negligible — so **the reason `findViewById` is considered fragile is not performance**. The real reasons are three:

1. **It can return `null`** and the compiler does not warn you. `etTitle.setText(...)` on `null` throws `NullPointerException` at runtime, in a method that may be far from the call.
2. **It is not type-safe.** `TextView tv = findViewById(R.id.listView)` compiles, but throws `ClassCastException: android.widget.ListView cannot be cast to android.widget.TextView` at runtime.
3. **It is not refactor-safe.** You rename `etTitle` to `etMovieTitle` in the XML: the build fails with `cannot find symbol`, which is good. But if you **move** the view into another layout and forget to update `setContentView`, the build passes and you get `null`. The second situation is the one that costs.

**What breaks without it**

- **`findViewById` before `setContentView`**: the tree does not exist yet, so it returns `null` for any ID. The symptom is a `NullPointerException` in `initControls()`. The rule: `setContentView` first, `findViewById` after.
- **Correct ID, wrong layout**: `findViewById(R.id.etTitle)` in an activity that did `setContentView(R.layout.activity_main)` → `null`, with no compile error. The ID exists in `R`, but not in the current tree.
- **Wrong type**: `ClassCastException` at runtime, with the exact message naming the two classes.
- **Non-existent ID**: `cannot find symbol: variable etTitl` — a compile error, the best possible variant.

**Where you see it in G1097**

`ItemActivity.initControls()` — 13 calls, one after another, each with the type declared in the field:

```java
private void initControls() {
    etTitle = findViewById(R.id.etTitle);
    etRelease = findViewById(R.id.etRelease);
    spGenre = findViewById(R.id.spGenre);
    etBudget = findViewById(R.id.etBudget);
    sbDuration = findViewById(R.id.sbDuration);
    rbRating = findViewById(R.id.rbRating);
    rgApproval = findViewById(R.id.rgApproval);
    cbonWatchList = findViewById(R.id.cbOnWatchList);
    swWatched = findViewById(R.id.swWatched);
    etPoster = findViewById(R.id.etPoster);
    btMovieAction = findViewById(R.id.btnMovieAction);
    tvDurationValue = findViewById(R.id.tvDurationValue);
    tvWatchedValue = findViewById(R.id.tvWatchedValue);
}
```

`MainActivity.initControls()` — only two, but their order relative to `setAdapter` matters:

```java
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    listView = findViewById(R.id.listView);
    listView.setAdapter(movieAdapter);
}
```

`ItemActivity.onCreate()` — the mandatory order, visible in the first seven lines:

```java
super.onCreate(savedInstanceState);
EdgeToEdge.enable(this);
setContentView(R.layout.activity_item);          // 1. the tree exists
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...);  // 2. the first findViewById
initControls();                                   // 3. the rest
initListeners();
```

If you moved `initControls()` before `setContentView`, all 13 references would be `null` and the first one used would throw `NullPointerException`.

**The typical confusion**

"`findViewById` is slow, that is why ViewBinding is used." Performance is not the problem. A `findViewById` on a tree of 50 views takes microseconds, and in `onCreate` it runs only once. The problem is **compile-time safety**: the possible `null` and the unchecked cast. ViewBinding solves exactly these two things (see 37.9).

The second: "`findViewById` searches the whole app". No. It searches the subtree of the object you call it on. If you call it on the `Activity`, it reaches the whole screen because `Activity` delegates to the window; if you call it on a `View`, it searches only under it. The practical consequence: in an adapter, `findViewById` is called on `convertView`, not on the `Activity` — otherwise you would search the whole screen for every row (see 37.18).

The third: "if the ID exists in `R`, `findViewById` finds it". No. `R.id.etTitle` exists because aapt2 generated it from the XML, but the view exists **in the tree** only if the layout that contains it has been inflated. Two different things, which coincide only when everything is in order.

---

## Concept 37.9 — ViewBinding

**What it is**

ViewBinding is a feature of the Android Gradle plugin that **generates a Java class for every XML layout**. The class is named after the file (`activity_main.xml` → `ActivityMainBinding`), has a public field for every view with an `android:id`, of the correct type, and is obtained through an `inflate`. You no longer write `findViewById` at all.

**Why it exists**

To remove the three fragilities from 37.8 with a single change: **the link between XML and code is checked at compile time**. The generated class has exactly the fields for the IDs that exist in that layout, with the type from the XML. If you delete an ID, the build fails. If you rename it, the build fails. It cannot return `null` for a declared field, because `inflate` has already built the whole tree.

**How it works**

It is enabled with a single line in `build.gradle.kts`:

```kotlin
android {
    buildFeatures { viewBinding = true }
}
```

On the next build, AGP generates a class for each layout in the `namespace` package:

```
res/layout/activity_main.xml  ──build──>  ro.ase.ie.dma05.databinding.ActivityMainBinding
res/layout/activity_item.xml  ──build──>  ro.ase.ie.g1097.databinding.ActivityItemBinding
```

The generated class, simplified to what you use:

```java
public final class ActivityMainBinding {
    public final LinearLayout main;
    public final Button button;
    public final Switch switch1;
    public final EditText editTextText;
    // ... one field for each android:id in the layout

    public static ActivityMainBinding inflate(LayoutInflater inflater) { ... }
    public LinearLayout getRoot() { ... }   // the root of the layout, with the type from the XML
}
```

The lifecycle of a binding in an activity:

```
1. binding = ActivityMainBinding.inflate(getLayoutInflater());
      -> LayoutInflater reads the XML
      -> builds the tree
      -> fills the fields with findViewById, ONCE, in generated code

2. setContentView(binding.getRoot());
      -> the built tree becomes the content of the window

3. binding.button.setOnClickListener(...)
      -> direct access to the field, no lookup, no cast, no null
```

The difference from `findViewById` is not "less code" — although that too. It is that **`binding.button` does not compile if the button does not exist**. The mistake moves from runtime to compile time, and that is always an improvement.

**What breaks without it**

- **Without `buildFeatures { viewBinding = true }`**: `Cannot resolve symbol 'ActivityMainBinding'`. The class does not exist, because it was not generated. It is not an import problem — it is a configuration problem.
- **Binding for the wrong layout**: `ActivityItemBinding.inflate(...)` in an activity that should have loaded `activity_main.xml` compiles, but shows a different screen. You get no error, because both classes exist.
- **A view without an `android:id`**: it does not appear in the binding. You cannot reach it from code — which is correct, but it surprises you when you forgot the ID.
- **`binding` used after `onDestroy`**: it throws nothing, because the binding is just a Java object holding references to views. The problem is memory: if you keep the binding in a `static` field, you keep the whole tree alive.

**Where you see it in G1097**

**G1097 has `viewBinding = true` in `build.gradle.kts`, but does not use it.** `ItemActivity.initControls()` makes 13 `findViewById` calls, and `MainActivity.initControls()` two — plus one each in `onCreate`, for `R.id.main` in the insets listener. It is a didactic choice: at the test you may be asked either to explain why it is not used, or to migrate.

```kotlin
// cod-final/build.gradle.kts — the flag exists
android {
    namespace = "ro.ase.ie.g1097"
    buildFeatures { viewBinding = true }
}
```

The contrast is in `DMA05`, which uses it fully:

```java
import ro.ase.ie.dma05.databinding.ActivityMainBinding;

public class MainActivity extends AppCompatActivity {

    ActivityMainBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        binding = ActivityMainBinding.inflate(getLayoutInflater());

        EdgeToEdge.enable(this);
        setContentView(binding.getRoot());
        ViewCompat.setOnApplyWindowInsetsListener(binding.getRoot(), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        binding.button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show();
            }
        });

        binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });
```

Notice the three differences from G1097: there is no `initControls()`, there is no `findViewById` at all, and `binding.getRoot()` replaces `findViewById(R.id.main)` in the insets listener.

**The typical confusion**

"ViewBinding is DataBinding." No. DataBinding is a much heavier system: it allows expressions in XML (`android:text="@{movie.title}"`), variables, data observation. ViewBinding is only **the generation of typed references**. In practice, ViewBinding is enough for 95% of cases and does not have DataBinding's build cost.

The second: "ViewBinding replaces the layout". No. The XML stays exactly the same; only a Java class that wraps it is generated. `activity_item.xml` does not change at all if you enable ViewBinding.

The third: "ViewBinding does `findViewById` internally, so it is just as fragile". It does `findViewById` internally, but **only once**, in generated code, with the IDs read from the same XML. The fragility disappears because the generator and the XML are synchronised at build time, not because the lookup mechanism would be different.

The fourth, important at the exam: "if I have `viewBinding = true`, I have to use it". No. The flag only generates the classes; `findViewById` keeps working. G1097 is the proof: the flag is on, the code uses `findViewById`.

---

## Concept 37.10 — Activity: what it is and who creates it

**What it is**

An `Activity` is a **screen with a lifecycle**, declared in the manifest, started by an `Intent` and hosted by a window. It is not an object you construct: the system instantiates it by reflection, calls its methods in order and destroys it when it is no longer needed. `MainActivity` and `ItemActivity` are the two activities of G1097.

**Why it exists**

Because a screen has to have **an entry point the system knows about**. If you built the screens with `new`, the system would not know when to give them memory, when to take it back, how to save their state on rotation or how to bring them back after the process was killed. `Activity` is the contract: you say what to do in `onCreate`, the system decides **when** to do it.

**How it works**

The full chain, from `launcher.launch(intent)` to the first `onResume`:

```
MainActivity: launcher.launch(intent)
    |
    v
system_server: ActivityTaskManager
    |-- resolves the Intent to ItemActivity (from the manifest)
    |-- checks exported, permissions
    |-- the process already exists (G1097 is running) -> reuses it
    |
    v
ActivityThread (the app's main thread)
    |-- Instrumentation.newActivity(ItemActivity.class)
    |     -> reflection: constructor WITHOUT parameters
    |     -> if it is missing: InstantiationException
    |-- activity.attach(context, window, ...)
    |     -> receives the window, the resources, the theme
    |-- activity.onCreate(savedInstanceState)
    |     -> setContentView -> the view tree
    |-- activity.onStart()
    |-- activity.onResume()
    |-- the window becomes visible -> measure -> layout -> draw
```

Three consequences that are asked at the test:

1. **The constructor must have no parameters.** The system has no arguments to give you. That is why `MainActivity` and `ItemActivity` have no constructor written at all — the compiler gives them the implicit one.
2. **`onCreate` is not the constructor.** The constructor creates the empty object; `onCreate` receives the `Bundle` with the saved state and the window already attached. Any initialisation that touches the UI has to live in `onCreate`.
3. **An activity is not created with `new`.** `new MainActivity()` compiles, but the resulting object has no window, no attached resources, no lifecycle. Any `setContentView` on it throws.

**What breaks without it**

- **`new MainActivity()`**: it compiles, but the first access to `getWindow()` or `getResources()` throws `NullPointerException`. There is no compile warning — that is why it is a trap.
- **Activity not declared in the manifest**: `ActivityNotFoundException` at `launch`, with the message that tells you exactly what is missing (see 37.4).
- **A `static` or `private` class**: `InstantiationException: can't instantiate class ...; no empty constructor`. An activity must be `public` and have a public constructor with no parameters.
- **Heavy work in `onCreate`**: the screen appears white or frozen, because `onCreate` runs on the main thread, and drawing waits for it to finish.

**Where you see it in G1097**

The two activities, with everything they need in order to be activities:

```java
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ...
    }
}

public class ItemActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_item);
        ...
    }
}
```

The start, from `MainActivity.initListeners()`:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        launcher.launch(intent);
    }
});
```

`MainActivity.this` is the `Context` needed for the `Intent`; `ItemActivity.class` is the **component** — a `Class` object, not an instance. Nowhere in G1097 does `new ItemActivity()` appear.

**The typical confusion**

"The activity is the app." No — it is a screen. The app can have dozens; G1097 has two. See 37.1 for the difference.

The second: "I create the activity with `new`". No. The system creates it, by reflection, when an `Intent` asks for it. You request **the start**, you do not build the object.

The third: "`onCreate` is the constructor". No. The constructor creates the object; `onCreate` is the first callback of the lifecycle, with the state `Bundle` and with the window already prepared. The practical difference: in the constructor you do not have a fully attached `Context`, so you cannot call `getResources()` or `setContentView`.

The fourth: "an activity can be destroyed at any time, so `onDestroy` is guaranteed". No. On rotation, yes. On pressing Back, yes. When the system kills the process for memory, **no** — `onDestroy` does not run, and `onSaveInstanceState` has already run before. See 37.11 and 37.12.

---

## Concept 37.11 — The lifecycle

**What it is**

The lifecycle is **the sequence of methods the system calls on an activity** from creation to destruction: `onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`, plus `onRestart` on return. Each method corresponds to a state in which the activity may or may not be visible, have focus, receive input.

**Why it exists**

Because the system needs to **take memory** from apps that are not being used, and you need to **release resources** (camera, sensors, animations, listeners) exactly when the screen is no longer relevant. Without a lifecycle you would have two options: keep everything running (battery and memory wasted) or guess for yourself when the screen is visible (impossible — only the system knows who has focus). The lifecycle is the contract through which the system tells you what is happening, and you decide what to do.

**How it works**

The states and the transitions:

```
                     onCreate()
                        |
                        v
                    [CREATED]
                        |  onStart()
                        v
                    [STARTED]  <----------- onRestart() <-----+
                        |  onResume()                          |
                        v                                      |
                    [RESUMED]  <- the activity has focus       |
                        |                                      |
        +---------------+----------------+                     |
        |               |                |                     |
   the user        another app       presses Home         returns to the
   presses Back    in foreground     or screen off        foreground (from onStop)
        |               |                |                     |
        v               v                v                     |
     onPause()      onPause()        onPause()                 |
        |               |                |                     |
     onStop()        onStop()         onStop() ---------------+
        |               |                |
     onDestroy()    (the process can be killed at any time, without onDestroy)
```

The order on **rotation** — the one that produces the most bugs:

```
onPause -> onStop -> onSaveInstanceState -> onDestroy
   -> onCreate(savedInstanceState != null) -> onStart -> onResume
```

The order on **pressing Back**:

```
onPause -> onStop -> onDestroy          (no recreation)
```

What you put in each method, and why:

| Method | What you do | Why there |
|---|---|---|
| `onCreate` | `setContentView`, `findViewById`, structural initialisations | it runs once per instance |
| `onStart` | you register system listeners (sensors, broadcast) | the activity becomes visible |
| `onResume` | you start animations, the camera, you refresh the displayed data | the activity has focus |
| `onPause` | you stop animations, you quickly save what can be lost | you are about to lose focus |
| `onStop` | you release heavy resources, you unregister listeners | it is no longer visible |
| `onDestroy` | you cancel callbacks, you stop threads | the instance dies for good |

**What breaks without it**

- **A listener registered in `onResume` without unregistering in `onPause`**: after every return you have one more. The symptom is an event processed 3 times after 3 returns — with no error at all.
- **The camera held in `onStart` without releasing it in `onStop`**: another app cannot open the camera, and on some devices your app crashes at `open()`.
- **Work in `onCreate` that should have been in `onResume`**: the displayed data stays the one from creation, because on return `onCreate` does **not** run again.
- **Relying on `onDestroy`**: when the system kills the process, `onDestroy` does not run. Any saving placed there is lost exactly in the case where it mattered.

**Where you see it in G1097**

G1097 overrides **only `onCreate`**, in both activities. It has no `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`, `onSaveInstanceState`. That is enough for a didactic app, but it also means you have nowhere to see the lifecycle in action.

`DMA02` shows it fully — `MainActivity` overrides all six methods, each with a `Log`:

```java
@Override protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    Log.w(TAG, "onCreate");
}

@Override protected void onStart()   { super.onStart();   Log.w(TAG, "onStart"); }
@Override protected void onResume()  { super.onResume();  Log.w(TAG, "onResume"); }
@Override protected void onPause()   { super.onPause();   Log.w(TAG, "onPause"); }
@Override protected void onStop()    { super.onStop();    Log.w(TAG, "onStop"); }
@Override protected void onDestroy() { super.onDestroy(); Log.w(TAG, "onDestroy"); }
```

And `DMA02App` sees **the same transitions from the outside**, through `Application.ActivityLifecycleCallbacks`:

```java
public class DMA02App extends Application implements Application.ActivityLifecycleCallbacks {

    @Override
    public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
        DynamicColors.applyToActivitiesIfAvailable(this);
        Log.w(TAG, "onCreate");
    }

    @Override
    public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
        Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());
    }
    // ... onActivityStarted, onActivityResumed, onActivityPaused,
    //     onActivityStopped, onActivitySaveInstanceState, onActivityDestroyed
}
```

The difference between the two sources of logs is exactly what you have to remember: the activity's methods are called **on the activity**, while the callbacks in `Application` are called **on the app, for any activity**. The second way lets you see the lifecycle without modifying the activity — and it is how you can demonstrate it at the test.

**The typical confusion**

"`onDestroy` always runs." No. It runs when the activity is destroyed **on purpose** (Back, `finish()`, rotation, `configChanges`). When the system kills the process for memory, `onDestroy` does not run — the process disappears. That is why saving is not put in `onDestroy`.

The second: "`onPause` means the activity is finished". No. `onPause` means it lost focus — it can be partially covered by a dialog or by another activity. It can come back straight into `onResume`, without `onStop`.

The third: "`onCreate` runs on every return". No. It runs once per instance. On returning from Home, `onRestart` → `onStart` → `onResume` run. If you want to refresh the data on every return, the place is `onResume`.

The fourth: "`onStart` and `onResume` are almost identical". No. `onStart` = visible; `onResume` = visible **and** focused, that is, it receives input. Between them there can be a dialog covering the activity: `onPause` without `onStop`.

---

## Concept 37.12 — State: onSaveInstanceState vs SharedPreferences

**What it is**

They are **two different mechanisms** for not losing data, with different lifetimes. `onSaveInstanceState(Bundle)` saves **ephemeral** state into a `Bundle` kept by the system in memory: it survives rotation and recreation of the activity, but does not survive closing the app. `SharedPreferences` saves **durable** data into an XML file in the app's private directory: it survives stopping, restarting and updating, but not uninstalling.

**Why it exists**

Because they are two different problems, which are constantly confused. The first: "the user rotated the phone and lost what they had typed" — a **configuration** problem, solved with a `Bundle`. The second: "the user wants to find the movies again after closing the app" — a **persistence** problem, solved with a file, a database or `SharedPreferences`. A single mechanism cannot solve both: the `Bundle` is too ephemeral for persistence, and the file is too expensive for a value that lives 2 seconds.

**How it works**

The two lifetimes, on the same axis:

```
                    rotation        Home            process kill        restart
                       |              |                    |                |
Bundle:            survives        yes (if the task    NO               NO
                   (recreation)     is restored)
                       |              |                    |                |
SharedPreferences: survives        survives         survives         survives
```

The mechanism of the `Bundle`:

```
1. The user rotates the phone
2. The system: onPause -> onStop -> onSaveInstanceState(outState)
      -> your activity puts into outState what it wants to keep
3. onDestroy
4. The system creates a NEW instance of the same class
5. onCreate(savedInstanceState)   <- the bundle from step 2
      -> you read from it and put the state back into the widgets
```

The canonical form, which you know from chapter 21:

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

The mechanism of `SharedPreferences`, on the other hand, has nothing to do with the lifecycle: you write when you want, you read when you want, and the file sits in `/data/data/ro.ase.ie.g1097/shared_prefs/`. It is not wiped on rotation, not wiped on Home, not wiped on restart.

The criterion for choosing, in a table:

| Question | `Bundle` | `SharedPreferences` |
|---|---|---|
| Does it have to survive rotation? | yes | yes (but it is overkill) |
| Does it have to survive closing the app? | **no** | yes |
| How big is the data? | small (KB) | small (KB) — not for big lists |
| What kind of data? | anything `Serializable`/`Parcelable` | primitives, `String`, `Set<String>` |
| Who deletes it? | the system, on destruction | the user, on uninstall/clear data |

**What breaks without it**

- **Without `onSaveInstanceState`**: on rotation, the form empties. That is exactly what happens in G1097 — see below. The symptom is spectacular: you fill in five fields, rotate the phone, everything disappears.
- **Without the `savedInstanceState != null` check**: on the first creation the bundle is `null`, and `savedInstanceState.getString(...)` throws `NullPointerException` in `onCreate`. The app crashes on the first launch, not on rotation.
- **An object that is not `Serializable` put into the `Bundle`**: `RuntimeException: Parcelable encountered IOException writing serializable object`. It happens at runtime, not at compile time.
- **`SharedPreferences` used for UI state**: on every rotation you write to disk, and on the next launch the app "remembers" a form the user had abandoned. Wrong behaviour, with no error.
- **`SharedPreferences` for big lists**: the file is read entirely into memory on first access. For 10,000 movies you need a database, not preferences.

**Where you see it in G1097**

**G1097 does not override `onSaveInstanceState`.** The `savedInstanceState` parameter exists in the signature of both `onCreate`s, but it is not read anywhere:

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);   // savedInstanceState is ignored
    EdgeToEdge.enable(this);
    setContentView(R.layout.activity_item);
    ...
}
```

The consequence, verifiable on the emulator: you fill in the form in `ItemActivity`, rotate the phone, and all ten values entered are lost. `releaseCal` goes back to `Calendar.getInstance()`, the spinner goes back to "Drama", the rating to 0, and `swWatched` and `cbonWatchList` go back to `false`. It is a **real gap** in the code, not a choice — and a likely exercise at the test.

The second gap: `MainActivity` keeps the list in `private final List<Movie> movies = new ArrayList<>();` and fills it with `addSampleMovies()` on every `onCreate`. On rotation, the list is rebuilt from the three starting movies, and the movies added by the user disappear. Here the `Bundle` would be suitable, because `Movie implements Serializable` — so `outState.putSerializable("movies", new ArrayList<>(movies))` would work.

`SharedPreferences` **does not appear at all in G1097**. It appears in chapter 35 as a recipe and it is the correct mechanism for "the movies should stay after the app is closed" — a requirement G1097 does not have.

**The typical confusion**

"`SharedPreferences` is for state." No — it is for **durable preferences**: the last sort mode, the chosen theme, whether the tutorial was seen. The state of an unsent form is not a preference; it is something that has to disappear when the user closes the screen.

The second: "the `Bundle` survives restarting the app". No. It lives as long as the **task** in recents, in the system's memory. If the user closes the app from recents, the bundle disappears.

The third: "if I save in `onSaveInstanceState`, I need nothing else". You do need more, because `onSaveInstanceState` is **not** called when the user presses Back or when you call `finish()`. In those cases the activity dies for good and the state is lost on purpose.

The fourth: "I can put any object in a `Bundle`". Only `Serializable`, `Parcelable` and primitives. A `Context`, a `Drawable`, a `View` are not — and the error appears at runtime, when the bundle is written, not when you build it. See 37.16 and 37.22.

---
## Concept 37.13 — Application

**What it is**

`Application` is the class that represents **the app as a whole, during one run**. There is a single instance per process, it is created by the system **before any activity** and it lives until the process dies. If you want your own class, you write it and declare it in the manifest with `android:name=".ClassName"`; otherwise Android uses the default class `android.app.Application`.

**Why it exists**

Because there are initialisations that have to be done **once per process**, not once per screen: configuring a logging library, registering a crash handler, initialising a database, applying dynamic colours. If you put them in each activity's `onCreate`, they would run N times, and on rotation they would run again. `Application` is the only place in the app that the system guarantees runs exactly once, before anything else.

**How it works**

```
1. The system starts the process (fork from Zygote)
2. ActivityThread.main()
3. ActivityThread finds the class declared in the manifest:
      <application android:name=".DMA02App">
4. Instrumentation.newApplication(DMA02App.class, context)
      -> reflection: constructor with no parameters
5. application.attachBaseContext(context)
6. application.onCreate()          <-- this is where you do your initialisations
7. only now is the first activity created: onCreate -> onStart -> onResume
```

The order is guaranteed, and it is the reason `Application` works as a place for initialisation: there is no path through which an activity can run before `Application.onCreate()`.

What you can and cannot do in `Application`:

| You can | You cannot (or should not) |
|---|---|
| initialise libraries, a logger, a crash handler | show a dialog (you have no window) |
| register `ActivityLifecycleCallbacks` | assume there is a current activity |
| apply the theme / the dynamic colours | do heavy work (you block startup) |
| hold global state per process | hold per-user state (you have no UI) |

**What breaks without it**

- **Without `android:name` in the manifest**: your class is never instantiated. You get no error — `Application.onCreate()` simply does not run, and your initialisations are missing. The symptom is a library that "does not work" with no message at all.
- **Heavy work in `Application.onCreate()`**: every launch of the app waits. The white screen at launch gets longer, and on slow devices you can reach an ANR ("Application Not Responding").
- **Mutable state held in `Application`**: it works as long as the process lives, but it disappears when the system kills it. If you use it as an "in-memory database", the user loses data without closing the app.
- **The assumption that `Application` is unique in the world**: it is unique **per process**. If the app runs in two processes, you have two `Application` instances, each with its own state.

**Where you see it in G1097**

**G1097 has no `Application` class.** The manifest contains no `android:name` on `<application>`, so the default `android.app.Application` runs, which does nothing extra. It is a deliberate absence for the sake of simplicity: the app needs no global initialisations.

`DMA02` has one, and uses it for two things at once — the dynamic theme and the observation of the lifecycle:

```java
public class DMA02App
        extends Application
        implements Application.ActivityLifecycleCallbacks {

    private final String TAG = DMA02App.class.getSimpleName();

    @Override
    public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
        DynamicColors.applyToActivitiesIfAvailable(this);

        Log.w(TAG, "onCreate");
    }
```

The declaration in the manifest, the only line that makes the difference:

```xml
<application
    android:name=".DMA02App"
    android:label="@string/app_name"
    android:theme="@style/Theme.DMA02">
```

`registerActivityLifecycleCallbacks(this)` is the most useful part for the exam: from `Application` you can receive all seven lifecycle callbacks **for any activity**, without modifying any activity. `DMA02App` implements all of them, and `onActivitySaveInstanceState` is left empty — a detail that shows the interface requires all the methods, even if you do not use them.

`DynamicColors.applyToActivitiesIfAvailable(this)` is a perfect example of global initialisation: it applies the Material You palette to all activities, once, from a single place. Done in every activity, it would be duplicated code.

**The typical confusion**

"`Application` is a global singleton I can use anywhere." It is a singleton **per process**, not per installed app. And it is not a good place for business data: if the process dies, the data disappears. For data that has to remain, you need a file, `SharedPreferences` or a database.

The second: "`Application.onCreate()` runs on every activity". No — it runs once, at process start. When you come back to the app after Home, if the process survived, `Application.onCreate()` does **not** run again.

The third: "if I have `Application`, I can give up `Context` in activities". No. `Application` is a `Context`, but without a theme and without a window (see 37.2). Widgets need the activity's context.

The fourth: "`Application` is the place for `SharedPreferences`". It can be — but not because it is `Application`. `SharedPreferences` is obtained from any `Context`, and the file is the same. The only difference is who holds the reference.

---

## Concept 37.14 — Listeners: what they are and who calls them

**What it is**

A listener is **an object that implements an interface the widget knows about**, and the widget calls it when something happens. `View.OnClickListener` has a single method, `onClick(View)`. You give it an object that implements it through `setOnClickListener(...)`, and the widget keeps it in a field and calls it when the user touches the view.

**Why it exists**

Because the widget cannot know what you want to do. A `Button` knows how to draw itself and detect touch, but it does not know that in your app it means "open the form". Without listeners you would have two options, both bad: extend `Button` for every button (one class per behaviour) or check periodically whether it was pressed (polling, impossible to do correctly). The listener is **inversion of control**: you do not ask the widget, the widget notifies you.

**How it works**

The full chain, from the finger to your code:

```
1. The finger touches the screen
2. Kernel -> InputDispatcher -> your app
3. ViewRootImpl.dispatchInputEvent()
4. DecorView.dispatchTouchEvent()      <- goes down the tree
5. each ViewGroup decides which child cares (hit test on the coordinates)
6. Button.dispatchTouchEvent()
7. Button.onTouchEvent(MotionEvent)
      -> ACTION_DOWN: it is marked "pressed" and redrawn
      -> ACTION_UP:   if the finger is still on the button -> performClick()
8. View.performClick()
      -> if mOnClickListener != null -> mOnClickListener.onClick(this)
9. your code runs, ON THE MAIN THREAD
```

Three things that follow from the chain:

1. **The listener runs on the main thread (UI thread).** Any long operation in `onClick` blocks drawing. That is where the rule comes from: in a listener you do no I/O, you do not sleep, you do not wait for the network.
2. **`setOnClickListener` stores the reference, it does not copy it.** One listener per widget for a given type of event — if you set it twice, the second one replaces the first, with no warning.
3. **The listener is called only if the view is `clickable`.** `setOnClickListener` makes the view clickable automatically; if you take it out of `clickable`, the listener stays set but is no longer called.

The six types of listeners in G1097, with what each one receives:

| Setter method | Interface | Methods | What you receive |
|---|---|---|---|
| `setOnClickListener` | `View.OnClickListener` | 1 | `View v` |
| `setOnItemClickListener` | `AdapterView.OnItemClickListener` | 1 | `parent, view, position, id` |
| `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | `buttonView, isChecked` |
| `setOnSeekBarChangeListener` | `SeekBar.OnSeekBarChangeListener` | **3** | see below |
| `setOnDateSetListener` | `DatePickerDialog.OnDateSetListener` | 1 | `view, year, month, day` |
| `setOnApplyWindowInsetsListener` | `androidx.core.view.OnApplyWindowInsetsListener` | 1 | `v, insets` |

**What breaks without it**

- **Listener not set**: the button is pressed, it animates (ripple), but nothing happens. Zero errors, zero logs. The hardest symptom to debug, because everything looks fine.
- **Listener set on the wrong view**: you press the button, another button's action happens. It happens when you copy a block of code and forget to change the variable.
- **`NullPointerException` in the listener**: a field used in `onClick` is `null`, usually because the listener was set before that field was initialised. That is exactly the trap in G1097 with `launcher` (see below).
- **Heavy work in the listener**: the interface freezes on press. It does not crash, it just does not respond — and the user presses again, three times.

**Where you see it in G1097**

`MainActivity.initListeners()` — two listeners, both of them use `launcher`, which is initialised **after** this method:

```java
private void initListeners() {
    fabInsert.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            launcher.launch(intent);      // launcher is still null AT THIS MOMENT
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
}
```

The order in `onCreate` is:

```java
initControls();                                    // 1
initListeners();                                   // 2  <- the listeners are SET here
launcher = registerForActivityResult(...);         // 3  <- launcher becomes non-null here
```

Nothing breaks here, and it is worth understanding why: at step 2 `onClick` is not called, only an object is **stored**. `onClick` runs only when the user touches the button, long after `onCreate` has finished. If you moved `launcher.launch(intent)` outside `onClick` — for example directly into `initListeners()` — you would have a `NullPointerException`.

`ItemActivity.initListeners()` — four listeners, including one with **three** methods:

```java
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveMovie();
    }
});

swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});

sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) { }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) { }
});
```

`onProgressChanged` is called **also** when you change the progress from code (`setProgress`), not only on touch. The `fromUser` parameter says which of the two it is — G1097 ignores it on purpose, because the label has to reflect the value in both situations. If you filtered with `if (fromUser)`, `fillForm` would set the progress without updating the label, and when editing you would see "0 min" for a 148-minute movie.

**The typical confusion**

"The listener runs on another thread, so I can do whatever I want in it." No. It runs on the main thread. For long operations you need a background thread, and then you come back to the main thread with the result.

The second: "`setOnClickListener` returns something". No, it returns `void`. You cannot chain calls and you cannot check whether it was set.

The third: "if I set two listeners, both are called". No. The second replaces the first, because the widget holds **a single** reference. If you need two behaviours, you put them in the same method.

The fourth: "the listener is called when the value changes from code". It depends on the widget. `SeekBar.onProgressChanged` **yes** (hence `fromUser`); `CompoundButton.onCheckedChanged` **yes**; `RadioGroup.onCheckedChanged` **yes**. But `ListView.onItemClick` does not — that one is only for touch. The general rule: if the method is called `onXChanged`, it is also called on a programmatic change; if it is called `onXClick`, only on interaction.

---

## Concept 37.15 — Lambda and functional interfaces

**What it is**

A **functional interface** is an interface with **exactly one abstract method**. A **lambda** is a short way of writing the implementation of that method, with no class, no name, no `new`. `(a, b) -> a + b` is the equivalent of `new FunctionalInterface() { public int apply(int a, int b) { return a + b; } }`, just without all the wrapping.

**Why it exists**

Because a listener with a single method asks for six lines of ceremony for a single expression. In `MainActivity`:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        launcher.launch(intent);
    }
});
```

six lines, of which **one** matters. Lambda reduces it to:

```java
fabInsert.setOnClickListener(v -> launcher.launch(intent));
```

The gain is not aesthetic. The gain is that **the intention becomes visible**: you see at a glance what happens on click, without reading through types and annotations.

**How it works**

The rule is mechanical: **a single abstract method = lambda allowed**. Two or more = anonymous class required.

| Interface | Abstract methods | Lambda? |
|---|---|---|
| `View.OnClickListener` | 1 (`onClick`) | **yes** |
| `AdapterView.OnItemClickListener` | 1 (`onItemClick`) | **yes** |
| `CompoundButton.OnCheckedChangeListener` | 1 (`onCheckedChanged`) | **yes** |
| `View.OnLongClickListener` | 1 (`onLongClick`) | **yes** |
| `SeekBar.OnSeekBarChangeListener` | **3** | **no** |
| `TextWatcher` | **3** | **no** |
| `androidx.core.view.OnApplyWindowInsetsListener` | 1 (`onApplyWindowInsets`) | **yes** |

The syntax, on the three forms you will use:

```java
// 1. one parameter, one expression
view.setOnClickListener(v -> doSomething());

// 2. one parameter, block (with braces, if you need several statements)
view.setOnClickListener(v -> {
    Intent intent = new Intent(this, ItemActivity.class);
    launcher.launch(intent);
});

// 3. two parameters
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

Three rules that produce compile errors if you break them:

1. **The parameters can be shortened, not extended.** You can write `v ->` instead of `(View v) ->`, but you cannot add parameters the interface does not have.
2. **Captured local variables must be effectively final.** You cannot modify them in the lambda. A field of the class, on the other hand, can be modified — because it is not captured by value, but through `this`.
3. **`this` inside a lambda is the outer instance.** In an anonymous class, `this` is the anonymous class. The difference is crucial in G1097.

**What breaks without it**

- **Lambda on an interface with three methods**: `SeekBar.OnSeekBarChangeListener is not a functional interface` — a compile error, a clear message. You cannot "solve" it with a lambda; you need an anonymous class.
- **Modifying a local variable in a lambda**: `Variable used in lambda expression should be final or effectively final`. It happens when you try to accumulate a total inside a `for`.
- **Wrong `this`**: in a lambda, `this` is the activity — so `Toast.makeText(this, ...)` works. In an anonymous class, `this` is the listener — so you need `MainActivity.this`. The confusion produces compile errors that are hard to read ("cannot be converted to Context").
- **Capturing a field that changes**: a lambda sees the value **at the moment of execution**, not at the moment of creation, for fields. For local variables, it sees the value from creation. Two different behaviours, the same syntax.

**Where you see it in G1097**

G1097 uses **a single lambda**, in both activities, and it is the most interesting one in the whole code:

```java
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
    return insets;
});
```

Why here and not elsewhere: `OnApplyWindowInsetsListener` has **a single** method (`onApplyWindowInsets`), so the lambda is allowed. The rest of the listeners in G1097 are written as **anonymous classes**, although most of them could have been lambdas:

```java
// G1097 — anonymous class (6 lines for one statement)
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});

// equivalent lambda (2 lines)
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

The only one that **cannot** be a lambda is `SeekBar.OnSeekBarChangeListener`, because it has three methods — and that is exactly how it appears in the code, with two empty methods:

```java
sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }
    @Override public void onStartTrackingTouch(SeekBar seekBar) { }
    @Override public void onStopTrackingTouch(SeekBar seekBar) { }
});
```

`DMA05` shows the contrast — the same widgets, written with lambdas:

```java
binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
    Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
});

binding.checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
    Toast.makeText(MainActivity.this, "CheckBox clicked to " + isChecked, Toast.LENGTH_SHORT).show();
});

binding.ratingBar.setOnRatingBarChangeListener((ratingBar, rating, fromUser) -> {
    Toast.makeText(MainActivity.this, "Rating changed to " + rating, Toast.LENGTH_SHORT).show();
});
```

Notice that `DMA05` writes `MainActivity.this` even inside a lambda. Here it is not mandatory — `this` would have been `MainActivity` anyway — but it is correct and readable. In `binding.radioGroup.setOnCheckedChangeListener(...)`, `DMA05` still uses an anonymous class, although `RadioGroup.OnCheckedChangeListener` has **one** single method (`onCheckedChanged(group, checkedId)`) and would have allowed a lambda; the code inside needs `group.findViewById(checkedId)`.

**The typical confusion**

"Lambda is always better." No. For `SeekBar` and `TextWatcher` it is not possible. And for a listener that needs `this` as an object (not as a `Context`), the anonymous class can be clearer.

The second: "a lambda creates a new object on every call". Not necessarily. The compiler can reuse an instance if the lambda captures nothing. In any case, the cost is negligible — it is not a criterion for choosing.

The third: "`this` in a lambda is the lambda". No — it is exactly the opposite of the anonymous class. In a lambda, `this` is **the instance in which the lambda is written**. That is why `Toast.makeText(this, ...)` works in a lambda inside an activity, but not in an anonymous class inside the same activity.

The fourth: "I can modify a local variable in a lambda". No, if it is local. You can modify a **field** of the class. The difference shows at compile time: `Variable used in lambda expression should be final or effectively final`.

---

## Concept 37.16 — The model (POJO) and Serializable

**What it is**

A **POJO** (*Plain Old Java Object*) is a class that contains only data: private fields, getters, setters, constructors, possibly `toString()` and `equals()`. It has no business logic, it does not depend on Android, it does not know what an `EditText` is. `Serializable` is a **marker interface** — it has no methods — that tells the JVM that the objects of the class can be turned into a stream of bytes and rebuilt.

**Why it exists**

The POJO exists for three reasons that are visible directly in the code. **Separation**: the `Movie` class has a single reason to change — the structure of a movie's data. **Testability**: you can test `Movie` without an emulator, because the file has no `import android.*` at all. **Transportability**: an object with no `Context` and no `View` can cross the boundary between two activities.

`Serializable` exists because that boundary **does not allow references**. When `MainActivity` sends a `Movie` to `ItemActivity`, the two activities run in the same process, but they communicate through `Binder`, that is, through bytes. You cannot send a reference; you have to send a **serialised copy**.

**How it works**

Serialisation, step by step:

```
MainActivity                          Binder                    ItemActivity
------------                          ------                    ------------
movies.get(0)  ->  Movie@A
                        |
                        | putExtra("movie", Movie@A)
                        v
              ObjectOutputStream
                 writes to bytes:
                   - the class name + serialVersionUID
                   - every non-static, non-transient field
                        |
                        v
                  Bundle { "movie" -> byte[] }
                        |
                        | (Binder transaction, ~1MB limit)
                        v
              ObjectInputStream
                 reads the bytes, creates Movie@A'
                 (the constructor is NOT called!)
                        |
                        v
                                          existing = Movie@A'   <- NEW object
```

Three consequences, all visible in the code:

1. **The object you receive is a copy.** `Movie@A'` has the same values, but a different address. Modifying it does not touch the list in `MainActivity`. That is why `saveMovie()` builds a **new** `Movie` and sends it back, and `MainActivity` does `movies.set(position, movie)`.
2. **The constructor does not run on deserialisation.** The JVM creates the object without calling it. That is why `Movie` has an explicit empty constructor — not for serialisation, but for `new Movie()` in `saveMovie()`.
3. **`serialVersionUID` is computed automatically** from the structure of the class if you do not declare it. If you add a field between writing and reading, the two values no longer match and you get `InvalidClassException`. In G1097 the risk is theoretical: the write and the read happen in the same process, milliseconds apart.

What is and is not serialisable:

| Serializable | Not serialisable |
|---|---|
| the primitives and their wrappers | `Context`, `Activity`, `Application` |
| `String` | `View`, `Drawable`, `Bitmap` |
| `Date`, `Calendar` | `Thread`, `Socket`, `InputStream` |
| `ArrayList`, `HashMap` (if the elements are) | any class without `implements Serializable` |
| any class that implements `Serializable` | a `transient` field (it is skipped on write) |

**What breaks without it**

- **Without `implements Serializable`**: `intent.putExtra(MOVIE_EXTRA, movie)` does not find any suitable overload. A **compile error**, not a runtime one: `no suitable method found for putExtra(String,Movie)`.
- **With a non-serialisable field**: `NotSerializableException: ro.ase.ie.g1097.model.Movie` at runtime, when the bundle is written. It happens if you add a field of type `Drawable` or `Context`.
- **Without an empty constructor**: `saveMovie()` does `new Movie()` — if you only have the 10-parameter constructor, it does not compile. In Java, a constructor with parameters **suppresses** the implicit constructor.
- **With a `null` `release`**: `fillForm` calls `dateFormat.format(existing.getRelease())`, and `SimpleDateFormat.format(null)` throws `NullPointerException`. It happens if a movie is built without a date — for example if you send `MOVIE_EXTRA` without the user having chosen a date.
- **With an empty `budget`**: `Double.parseDouble("")` throws `NumberFormatException` in `saveMovie()`. An empty numeric field is the most frequent source of crashes in the form.

**Where you see it in G1097**

`Movie.java` — 10 fields, two constructors, 20 getters/setters, `toString()`:

```java
public class Movie implements Serializable {
    private String title;        // EditText
    private Date release;        // EditText date
    private String genre;        // Spinner
    private double budget;       // EditText number
    private int duration;        // SeekBar
    private float rating;        // RatingBar
    private boolean watched;     // Switch
    private String approval;     // RadioGroup | RadioButtons
    private boolean onWatchlist; // Checkbox
    private String poster = null;

    public Movie(String title, Date release, String genre, double budget, int duration,
                 float rating, boolean watched, String approval, boolean onWatchlist, String poster) { ... }

    public Movie() { }           // needed for new Movie() in saveMovie()
```

The comments to the right of each field are not decorative: they document **where the value comes from**. The model does not know what a `SeekBar` is, but someone reading the class knows that `duration` is populated from one.

`toString()` is the display contract for `ArrayAdapter`:

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
            ", poster='" + poster + '\'' +
            '}';
}
```

That is why the list in `MainActivity` shows rows of the form `Movie{title='Inception', release=..., genre='Sci-Fi', ...}` — `ArrayAdapter` calls `toString()` on each element (see 37.17). If you changed `toString()` to return only the title, the list would look clean, with no other change.

The transport, in two places:

```java
// MainActivity — sending
intent.putExtra(MOVIE_EXTRA, movies.get(position));

// ItemActivity — receiving (the modern, typed variant)
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
```

`IntentCompat.getSerializableExtra(intent, key, Class)` is the variant from `androidx.core` that returns the correct type without a cast. The old variant, `intent.getSerializableExtra(key)`, returns `Serializable` and requires an explicit cast.

**The typical confusion**

"`Serializable` and `Parcelable` are the same thing." No. `Serializable` is the Java mechanism, based on reflection — simple to use, but slow. `Parcelable` is the Android mechanism, written by hand — much faster, but with ~30 lines of code per class. For a small object sent between two screens, `Serializable` is the reasonable choice; for big lists or frequent `Bundle`s, `Parcelable`.

The second: "the object received is the original". No. It is a deserialised copy. The practical consequence is the whole editing architecture of G1097: `ItemActivity` cannot modify the movie in the list, because it does not have the movie in the list. That is why it sends a new object back, and `MainActivity` puts it at the position it received.

The third: "`Serializable` makes the object persistent". No. It produces a stream of bytes, that is all. Persistence on disk is another problem (file, `SharedPreferences`, database).

The fourth: "`isWatched()` is a mistake, it should be `getWatched()`". No. The JavaBeans convention asks for `isX()` for a primitive `boolean`. Both work, but `isX()` is the idiomatic form — and it is the one some serialisation libraries expect.

---

## Concept 37.17 — Adapter: what it is and why it exists

**What it is**

An adapter is **the bridge between a data source and a list widget**. The widget does not know what a `Movie` is; the adapter does, and translates for it: "I have this many elements", "give me the view for the element at position 3". `ArrayAdapter` is the generic implementation for a list of objects displayed through a single text; `BaseAdapter` and `RecyclerView.Adapter` are the base classes for adapters of your own.

**Why it exists**

Because `ListView` needs an answer to two questions it cannot work out by itself: **how many rows there are** and **what row i looks like**. Without an adapter you would have two options, both impossible at scale. The first: you create all the views yourself and add them to a `LinearLayout` — for 1000 movies you have 1000 views in memory, no matter how many are visible. The second: you teach `ListView` about `Movie` — but then `ListView` would depend on your model, and a second model would require a second `ListView`.

The adapter solves both: `ListView` stays generic, and you give it an object that knows how to answer. And, crucially, the adapter is called **only for the visible rows** — that is where the efficiency comes from (see 37.18).

**How it works**

Who calls the adapter's methods: **`ListView`**, not you. You only set the adapter once.

```
MainActivity                          ListView                       ArrayAdapter
------------                          --------                       ------------
movies: List<Movie>
    |
    | new ArrayAdapter<>(this,
    |     simple_list_item_1, movies)
    +---------------------------->  setAdapter(adapter)
                                         |
                                         | 1. getCount()  -> 3
                                         |    "I need 3 rows"
                                         |
                                         | 2. getView(0, null, parent)
                                         |       -> inflates a simple TextView
                                         |       -> setText(movies.get(0).toString())
                                         | 3. getView(1, null, parent)
                                         | 4. getView(2, null, parent)
                                         v
                                    displays 3 rows

the user scrolls (if there were 100 movies):
    row 0 goes off screen -> convertView = row 0
    ListView calls getView(7, convertView, parent)
      -> the adapter reuses the view and only changes the text
```

Four moments when `ListView` asks the adapter something:

| Moment | Method | What happens |
|---|---|---|
| at `setAdapter` | `getCount()` | it finds out how many rows there are |
| at drawing | `getView(position, convertView, parent)` | it asks for the view of each visible row |
| at scrolling | `getView(...)` with `convertView` | it asks for a new row, offering a recycled one |
| at `notifyDataSetChanged()` | `getCount()` + `getView(...)` | it re-queries everything that is visible |

`ArrayAdapter` has a particularity that explains everything you see in the list: **it calls `toString()` on each element** and puts the result into a single `TextView`. That is why the rows in G1097 look like printed Java objects, not like movie titles.

**What breaks without it**

- **Without `setAdapter`**: the list is empty, with no error at all. A `ListView` without an adapter has nothing to ask, so it draws nothing. The symptom is identical to "my list is empty", even though the data exists.
- **Without `notifyDataSetChanged()`**: the list shows the data from the last bind. You add a movie, the list stays at three rows, even though `movies.size()` is 4. `ListView` **does not observe** the list — it cannot, it is a plain `ArrayList`.
- **Adapter created with another list**: `new ArrayAdapter<>(this, layout, new ArrayList<>())` instead of `movies` → the list is forever empty, because you modify one list and the adapter reads another.
- **`notifyDataSetChanged()` before the change**: `IndexOutOfBoundsException`, because the adapter re-queries `getCount()` and then asks for rows that do not exist in the list yet.

**Where you see it in G1097**

Three lines, in three different places, and each one matters:

```java
// MainActivity.onCreate — the adapter holds the REFERENCE to `movies`, not a copy
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

// MainActivity.initControls — binding to the widget
listView.setAdapter(movieAdapter);

// MainActivity — the result callback, AFTER every change to the list
movies.add(movie);
movieAdapter.notifyDataSetChanged();
```

The order in the callback is the contract:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();      // first you change, then you notify
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

`android.R.layout.simple_list_item_1` is the row layout: a single `TextView` with the ID `android.R.id.text1`. `ArrayAdapter` fills it with `toString()`. If you want a row with several views, you need an adapter of your own — exactly what `DMA06` shows.

`DMA06/TwoColumnActivity` — a `BaseAdapter` of its own, for two columns:

```java
ListView lvNumbers = findViewById(R.id.lvNumbers);
NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
lvNumbers.setAdapter(adapter);
```

`DMA06/NumberListAdapter` — the four methods that `BaseAdapter` requires:

```java
@Override public int getCount()  { return numbers.size(); }
@Override public Integer getItem(int position) { return numbers.get(position); }
@Override public long getItemId(int position) { return numbers.get(position); }
@Override public View getView(int position, View convertView, ViewGroup parent) { ... }
```

`getItemId` is interesting: it returns **the number itself**, not the position, because the numbers are unique. In G1097, `Movie` has no ID, so the identity is the position — hence the whole `POSITION_EXTRA` mechanism.

**The typical confusion**

"The adapter is the list." No. The adapter **reads** the list. `ArrayAdapter` receives a reference to `movies` and reads it on every `getView`. That is why `movies.add(...)` is seen immediately in the adapter — but only after `notifyDataSetChanged()`.

The second: "the adapter observes the list and updates itself". No. `ArrayList` has no notification mechanism. That is why `notifyDataSetChanged()`, `notifyItemInserted()`, `notifyItemRemoved()` exist. Without them, `ListView` believes the list is unchanged.

The third: "`notifyDataSetChanged()` redraws the list". It does not redraw — it **announces** that the data has changed, and `ListView` decides what to re-query. The effect is the rebuilding of the visible rows, with no animations.

The fourth: "one adapter per row". No — one adapter per **list**. It produces all the rows, one by one, and it is called as many times as the widget needs rows.

---

## Concept 37.18 — ViewHolder and row recycling

**What it is**

`ViewHolder` is a small object that **keeps the references to the views of a row**, so they are not looked up again on every display. Recycling is the mechanism through which the list widget **reuses the views that go off screen** for the rows that come in, instead of creating new ones.

**Why it exists**

Because `findViewById` and `inflate` are expensive, and a list scrolls. Without recycling, a list of 1000 elements would have 1000 view trees in memory — regardless of the fact that 8 are visible. Without `ViewHolder`, every scroll would do `findViewById` for each view in the row, dozens of times per second. Together, the two turn an O(n) memory operation and O(n) lookups into an O(1) memory operation and O(1) lookups per displayed row.

**How it works**

The recycling, step by step, on a list of 100 elements with 7 visible rows:

```
Initial state — 7 views created, 7 visible rows:

  screen:  [0][1][2][3][4][5][6]
  pool:    (empty)

You scroll down by one row:

  row 0 goes off the top
     -> ListView takes it and puts it in the pool as `convertView`
  row 7 comes in at the bottom
     -> ListView calls getView(7, convertView = row 0, parent)

  getView(7, convertView, parent):
     convertView != null?
       YES -> you do NOT inflate again. You reuse the existing view.
              holder = (ViewHolder) convertView.getTag()
       NO  -> you inflate the row once, create the holder,
              findViewById for each view,
              convertView.setTag(holder)

     then, in both cases:
       holder.tvDecimal.setText(String.valueOf(numbers.get(7)))
       holder.tvBinary.setText(Integer.toBinaryString(numbers.get(7)))
       return convertView

Result: for 100 elements there are ~8 views, created only once.
```

The cost, compared:

| | Without recycling | With recycling, without ViewHolder | With both |
|---|---|---|---|
| `inflate` per row | 1 | 1 (the first time) | 1 (the first time) |
| `findViewById` per displayed row | N | N | **0** |
| views in memory for 1000 | 1000 | ~8 | ~8 |

`ViewHolder` does not save `inflate` — recycling does that. `ViewHolder` saves **the lookups**. They are two independent optimisations, which combine.

In `RecyclerView`, `ViewHolder` is no longer optional: `RecyclerView.Adapter` has `ViewHolder` in its generic signature, and `onCreateViewHolder` / `onBindViewHolder` are separate precisely so that it is impossible to miss the separation.

**What breaks without it**

- **Without recycling** (you ignore `convertView` and inflate every time): the list works, but scrolling becomes jerky on long lists, and memory grows proportionally to the number of rows visited. It is not a crash, it is jank.
- **Without `setTag`**: `holder = (ViewHolder) convertView.getTag()` returns `null`, then `holder.tvDecimal` throws `NullPointerException` on the first scroll. It happens if you forget `convertView.setTag(holder)` in the `if` branch.
- **With `setTag` but without `getTag`**: `findViewById` on every row — it works, but you lose the optimisation.
- **With a field not set in `bind`**: the recycled row keeps the value from the previous element. The classic symptom: you scroll and see one movie's title over another's poster. The cause: you set the text only conditionally, and on the `else` branch you left the old value.
- **A `ViewHolder` that holds the data**: if you put `Movie movie` in the `ViewHolder` and forget to update it in `bind`, you have exactly the same symptom, but harder to find.

**Where you see it in G1097**

G1097 uses `ArrayAdapter`, which has **internal** recycling — that is why the code shows no `convertView`. The recycling happens, you just do not see it:

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

`ArrayAdapter.getView(position, convertView, parent)` reuses `convertView` if it exists and does `setText(movies.get(position).toString())`. For a single `TextView`, that is enough.

`DMA06` shows the mechanism explicitly, in two variants. `NumberListAdapter` — `ListView` with a manual `ViewHolder`:

```java
@Override
public View getView(int position, View convertView, ViewGroup parent) {
    ViewHolder holder;

    if (convertView == null) {
        // new row: inflate + cache the references
        convertView = layoutInflater.inflate(R.layout.item_number, parent, false);
        holder = new ViewHolder();
        holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);
        holder.tvBinary = convertView.findViewById(R.id.tvBinary);
        convertView.setTag(holder);
    } else {
        // recycled row: take the references from the tag
        holder = (ViewHolder) convertView.getTag();
    }

    int number = getItem(position);
    holder.tvDecimal.setText(String.valueOf(number));
    holder.tvBinary.setText(Integer.toBinaryString(number));

    return convertView;
}

private static class ViewHolder {
    TextView tvDecimal;
    TextView tvBinary;
}
```

`NumberRecyclerAdapter` — the same idea, but `ViewHolder` is mandatory and `getView` is split in two:

```java
static class NumberViewHolder extends RecyclerView.ViewHolder {
    final TextView tvDecimal;
    final TextView tvBinary;

    NumberViewHolder(@NonNull View itemView) {
        super(itemView);
        tvDecimal = itemView.findViewById(R.id.tvDecimal);
        tvBinary = itemView.findViewById(R.id.tvBinary);
    }
}

@NonNull
@Override
public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
    // runs only when a NEW row is needed
    View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.item_number, parent, false);
    return new NumberViewHolder(view);
}

@Override
public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
    // runs every time the row displays a number
    int number = numbers.get(position);
    holder.tvDecimal.setText(String.valueOf(number));
    holder.tvBinary.setText(Integer.toBinaryString(number));
}
```

The split is exactly the `if (convertView == null)` / `else` from `ListView`, but done by the framework: `onCreateViewHolder` is the "new row" branch, `onBindViewHolder` is the part that always runs.

**The typical confusion**

"`ViewHolder` holds the row's data." No — it holds the row's **views**. The data is put in on every `bind`, because the row is reused for another element. If you put data in the `ViewHolder` and forget to update it, the row shows the previous element's data.

The second: "recycling means fewer rows are created". No — it means fewer **views** are created. The logical rows are as many as the list has elements; the physical views are only as many as fit on the screen plus a few.

The third: "`RecyclerView` recycles better than `ListView`". It recycles **more explicitly** and with a configurable pool, but the basic mechanism is the same. The real difference is that `RecyclerView` forces you to separate creation from binding (see 37.20).

The fourth: "if the list has 3 elements, recycling does not matter". Correct — and that is why G1097 can use `ArrayAdapter` with no worry at all. Recycling matters from a few dozen elements upwards.

---
## Concept 37.19 — LayoutManager

**What it is**

`LayoutManager` is the object that decides, for a `RecyclerView`, **where each row sits** and **when it has to be recycled**. It is the one that knows whether the list is arranged vertically, horizontally, in a grid or in a staggered grid. It comes in three ready-made implementations: `LinearLayoutManager`, `GridLayoutManager`, `StaggeredGridLayoutManager`.

**Why it exists**

Because `RecyclerView` was designed as a **recycling engine**, not as a list. It knows how to keep a pool of views, to hand them out and take them back, to run animations. It does not know — and should not know — how the elements are arranged. This separation allows the arrangement to change without touching the adapter: the same `NumberRecyclerAdapter` works with a vertical `LinearLayoutManager`, a horizontal one, or a `GridLayoutManager` with 3 columns, without a single line changed.

**How it works**

The relation between the four components:

```
RecyclerView
├── LayoutManager        <- where each row sits, which is the visible window
├── Adapter              <- what data each row has, what it looks like
├── ItemAnimator         <- what animation runs on insert/delete
└── ItemDecoration       <- what is drawn BETWEEN rows (separators, margins)
```

The cycle, on every scroll:

```
1. RecyclerView receives a scroll event
2. LayoutManager computes which positions should be visible now
      -> "rows 5..12"
3. for each position that comes in:
      -> asks the adapter for a ViewHolder
         -> from the pool, if one exists (onBindViewHolder)
         -> a new one, if not (onCreateViewHolder)
4. LayoutManager positions each view: layout(left, top, right, bottom)
5. for each position that goes out:
      -> the ViewHolder goes back into the pool
```

`LinearLayoutManager` — a single axis, with `getOrientation()` returning `VERTICAL` or `HORIZONTAL`. This method is used in `DMA06` to configure the divider:

```java
LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
rvNumbers.addItemDecoration(
        new DividerItemDecoration(this, layoutManager.getOrientation()));
```

`GridLayoutManager` — it receives the number of columns in the constructor: `new GridLayoutManager(this, 3)`. `StaggeredGridLayoutManager` — it receives the number of columns and the orientation, and allows different heights per element.

**What breaks without it**

- **Without `setLayoutManager`**: `RecyclerView` displays **nothing**. It does not crash, it throws no exception — it just stays empty, and logcat shows `RecyclerView: No layout manager attached; skipping layout`. It is the most frequent mistake on first use, because `ListView` did not need anything like it.
- **`LinearLayoutManager` with the wrong `context`**: it compiles and works, but the theme and the resources come from another context. The symptom can be a divider with the wrong colour.
- **`GridLayoutManager` with 0 columns**: `IllegalArgumentException: spanCount should be at least 1`.
- **Changing the `LayoutManager` after `setAdapter`**: it works, but it causes a complete re-layout. It is not an error, it is an expensive operation.

**Where you see it in G1097**

**G1097 has no `RecyclerView`**, so no `LayoutManager` either. `activity_main.xml` uses a `ListView`, which has its arrangement implemented internally — vertical, with no alternative.

`DMA06/RecyclerViewActivity` is the complete example, in seven lines:

```java
RecyclerView rvNumbers = findViewById(R.id.rvNumbers);

LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
rvNumbers.addItemDecoration(
        new DividerItemDecoration(this, layoutManager.getOrientation()));

NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

The order matters and is worth noticing: `LayoutManager` **before** the adapter. `RecyclerView` can receive the adapter without a layout manager, but it will draw nothing until it receives the layout manager too. Why: the adapter says *how many* elements there are, the layout manager says *which* of them are visible.

`activity_recycler_view.xml` shows why `RecyclerView` needs `0dp` + `weight` to take the rest of the screen under the header:

```xml
<include layout="@layout/layout_number_header" />
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/rvNumbers"
    android:layout_width="match_parent"
    android:layout_height="0dp"
    android:layout_weight="1" />
```

**The typical confusion**

"`RecyclerView` is a `ListView` with animations." No. `RecyclerView` is an empty container that delegates **everything**: the arrangement to the `LayoutManager`, the data to the `Adapter`, the recycling to the `RecycledViewPool`, the animations to the `ItemAnimator`, the separators to the `ItemDecoration`. `ListView` had all of these built in, in a single class that was hard to extend.

The second: "`LayoutManager` draws the rows". No — it computes positions and calls `layout(...)` on each view. The drawing is done by `RecyclerView` through `draw()`, and the content of each row is drawn by the views inside it.

The third: "`ListView` has no layout manager". It does — it is implicit and fixed (vertical). That is why you cannot change it. `RecyclerView` took the decision out of the class and made it a parameter.

The fourth: "`DividerItemDecoration` is part of `RecyclerView`". No — it is an `ItemDecoration`, that is, a separate object that you add. `ListView` had `android:divider` as an XML attribute; `RecyclerView` took that out too.

---

## Concept 37.20 — ListView vs RecyclerView

**What it is**

They are **two list widgets** with the same mission and different philosophies. `ListView` is the old variant: it does everything itself — recycling, arrangement, separators — and gives you a single extension point, `getView()`. `RecyclerView` is the new variant: an empty container that splits the responsibilities between `Adapter`, `LayoutManager`, `ItemAnimator` and `ItemDecoration`.

**Why it exists — both of them**

`ListView` has existed since the first versions of Android and it works. `RecyclerView` appeared in `androidx` because `ListView` had three structural limitations you could not fix without breaking compatibility: recycling was **implicit** and easy to miss, the arrangement was **fixed** (vertical), and the notifications were **global** (`notifyDataSetChanged()` rebuilt everything, with no animations). `RecyclerView` solved all three through separation: recycling is mandatory through `ViewHolder`, the arrangement is a parameter, the notifications are granular.

`ListView` has not been removed from Android — it is still there, it still works, and it is the right choice for a simple list. G1097 uses it exactly that way.

**How it works**

The comparison of the pipelines, step by step:

```
ListView                                RecyclerView
--------                                ------------
setAdapter(adapter)                     setLayoutManager(lm)
                                        setAdapter(adapter)

ListView:                               RecyclerView + LayoutManager:
  getCount()                              getItemCount()
  getView(0, null, parent)                onCreateViewHolder(parent, viewType)  <- once
     -> inflate                            onBindViewHolder(holder, 0)         <- always
     -> findViewById
     -> setText
  getView(1, null, parent)
     -> inflate
     ...
                                        on scroll:
on scroll:                                LayoutManager decides which positions come in
  getView(7, convertView, parent)         pool of ViewHolder (not of View)
     -> convertView != null?              onCreateViewHolder only if the pool is empty
     -> getTag / setTag                   onBindViewHolder for each
     -> setText
```

The correspondence table, which is asked at the test:

| `ListView` / `BaseAdapter` | `RecyclerView.Adapter` | When it runs |
|---|---|---|
| `getCount()` | `getItemCount()` | when needed |
| `getView()`, the `convertView == null` branch | `onCreateViewHolder()` | once per created row |
| `getView()`, the `setText` part | `onBindViewHolder()` | on every display |
| `ViewHolder` + manual `setTag`/`getTag` | `RecyclerView.ViewHolder` mandatory | — |
| `android:divider` in XML | `DividerItemDecoration` added in code | — |
| `notifyDataSetChanged()` | `notifyItemInserted/Changed/Removed` | after every mutation |

The differences that matter in practice:

| Criterion | `ListView` | `RecyclerView` |
|---|---|---|
| recycling | implicit, easy to miss | mandatory through `ViewHolder` |
| arrangement | vertical only | any `LayoutManager` |
| animations on change | no | yes, through `ItemAnimator` |
| granular notification | no | yes (`notifyItem*`) |
| separators | XML attribute | `ItemDecoration` |
| code for a simple list | 3 lines | 5–6 lines + an adapter class |

**What breaks without it**

- **Migrating `ListView` → `RecyclerView` without `setLayoutManager`**: the list appears empty, with a warning in logcat. See 37.19.
- **A `getView` that does not reuse `convertView`**: the list works, but scrolling is jerky. It is not an error.
- **`notifyDataSetChanged()` in `RecyclerView`**: it works, but you lose the animations and you rebuild everything. It is not wrong, it is just less efficient than `notifyItemInserted`.
- **`RecyclerView` without a determined `layout_height`** (for example `wrap_content` inside a `ScrollView`): the height is computed wrongly, and the list appears cut off or completely empty. `RecyclerView` needs a known height in order to know how many rows to create.

**Where you see it in G1097**

G1097 uses **`ListView` + `ArrayAdapter`**, the minimal choice for three rows:

```java
// activity_main.xml
<ListView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:entries="@array/items" />
```

```java
// MainActivity.onCreate
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

Notice `android:entries="@array/items"` in the XML: it is a static binding to the array of 20 elements in `strings.xml`. It is **replaced** at runtime by `listView.setAdapter(movieAdapter)` in `initControls()`. The two mechanisms do not combine — `setAdapter` wins.

`DMA06` has all three variants, in three activities, exactly so you can compare them:

| Activity | Widget | Adapter | Row |
|---|---|---|---|
| `SingleColumnActivity` | `ListView` | `ArrayAdapter<Integer>` | one `TextView` |
| `TwoColumnActivity` | `ListView` | `NumberListAdapter extends BaseAdapter` | two `TextView`s |
| `RecyclerViewActivity` | `RecyclerView` | `NumberRecyclerAdapter` | two `TextView`s |

The same list of numbers from 1 to 100, the same row layout (`item_number.xml`), three implementations. The difference between `TwoColumnActivity` and `RecyclerViewActivity` is exactly what you have to be able to explain:

```java
// TwoColumnActivity — 2 lines
NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
lvNumbers.setAdapter(adapter);

// RecyclerViewActivity — 6 lines
LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
rvNumbers.addItemDecoration(new DividerItemDecoration(this, layoutManager.getOrientation()));
NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

**The typical confusion**

"`RecyclerView` is always faster." No. For 3 elements, `ListView` + `ArrayAdapter` is faster **and** less code. `RecyclerView` wins on long lists, on animations and on varied arrangements.

The second: "`ListView` is deprecated, it is no longer used". It is not marked `@Deprecated` and it works. Google recommends `RecyclerView` for new code, but `ListView` remains valid — and at the exam it may be explicitly required.

The third: "`RecyclerView` does not need a `ViewHolder`". It does — it is part of the generic signature `RecyclerView.Adapter<VH extends ViewHolder>`. You cannot write an adapter without one.

The fourth: "`ArrayAdapter` works with `RecyclerView` too". No. `ArrayAdapter` extends `BaseAdapter`, so it is a `ListAdapter` — the interface `ListView` requires — not a `RecyclerView.Adapter`. For `RecyclerView` you need an adapter of your own.

---

## Concept 37.21 — Intent

**What it is**

An `Intent` is **a message through which you ask the system to do something**. It contains an **action** (`ACTION_VIEW`, `ACTION_SEND`, `ACTION_MAIN`), a target **component** (optional), **data** (a `Uri`), a **category** and **extras** (a `Bundle`). When it has a component, it is called **explicit** and it goes exactly there. When it does not, it is called **implicit** and the system looks for whoever can handle it.

**Why it exists**

Because an app should not have to know which other apps the phone has. If you want to send a text, you do not want to know the internal class of the messaging app — you want to say "I have a text to share, who can take it?". `Intent` is that declaration. For internal navigation, the explicit `Intent` solves a simpler problem: it gives the system a component it can instantiate, without you building it (see 37.10).

**How it works**

The two kinds, with their path through the system:

```
EXPLICIT
  new Intent(MainActivity.this, ItemActivity.class)
     |
     |-- component = { ro.ase.ie.g1097, .activities.ItemActivity }
     v
  system_server: looks up the component in the manifest
     -> does it exist?  no -> ActivityNotFoundException
     -> exported? no and you come from another app -> SecurityException
     -> starts it

IMPLICIT
  new Intent(Intent.ACTION_SEND).setType("text/plain")
     |
     |-- action = ACTION_SEND, type = text/plain, no component
     v
  system_server: PackageManager.queryIntentActivities()
     -> 0 matches   -> ActivityNotFoundException
     -> 1 match     -> starts it directly
     -> 2+ matches  -> Intent.createChooser() or a system dialog
```

The anatomy of an `Intent`:

| Field | Method | Example |
|---|---|---|
| component | `new Intent(context, Class.class)` | `ItemActivity.class` |
| action | `setAction(...)` | `Intent.ACTION_SEND` |
| data | `setData(Uri)` | `Uri.parse("https://...")` |
| MIME type | `setType(...)` | `"text/plain"` |
| category | `addCategory(...)` | `Intent.CATEGORY_LAUNCHER` |
| extras | `putExtra(...)` | `putExtra("movie", movie)` |
| flags | `setFlags(...)` | `FLAG_ACTIVITY_NEW_TASK` |

**What breaks without it**

- **Non-existent component**: `ActivityNotFoundException: Unable to find explicit activity class {...}`. The cause is either the wrong class or the manifest (see 37.4).
- **Implicit `Intent` with no handler**: `ActivityNotFoundException: No Activity found to handle Intent { act=android.intent.action.SEND ... }`. It happens on emulators without messaging apps.
- **Implicit `Intent` with a handler, but without `setType`**: many apps filter by MIME type, so without it no handler is found.
- **An `Intent` with no target used with `startActivity`**: `ActivityNotFoundException`, because it has no component and no action. It is exactly the case where the `Intent` is correctly built — but for `setResult`, not for `startActivity` (see below).

**Where you see it in G1097**

Three `Intent`s, each with a different role:

```java
// 1. MainActivity.initListeners — explicit, to ItemActivity, with no extras (insert)
Intent intent = new Intent(MainActivity.this, ItemActivity.class);
launcher.launch(intent);

// 2. MainActivity.initListeners — explicit, with two extras (edit)
Intent intent = new Intent(MainActivity.this, ItemActivity.class);
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);
launcher.launch(intent);

// 3. ItemActivity.saveMovie — WITHOUT a target, for the result
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

The third one is the confusing one. `new Intent()` with no parameters is not a mistake: a result `Intent` starts nothing, it **travels back** to the activity that launched it. It only needs extras. If you put a component in it, it would be ignored.

`DMA02` shows an **implicit** `Intent`, the only one in the course projects:

```java
public void pressMe(View view) {
    Intent share = new Intent(Intent.ACTION_SEND);
    share.setType("text/plain");
    share.putExtra(Intent.EXTRA_TEXT, "Hello!");
    startActivity(Intent.createChooser(share, "Share via DMA"));
}
```

`Intent.createChooser(...)` is necessary when there are several handlers: instead of letting the system choose, it shows a dialog. Without it, Android would choose the last app used or show its own dialog — `createChooser` gives you control over the title.

The method is bound to the XML through `android:onClick="pressMe"`:

```xml
<Button
    android:id="@+id/button"
    android:onClick="pressMe" />
```

This is a **declarative** listener binding: the system looks for the method `pressMe(View)` in the activity and calls it. It works, but it is not recommended — it appears nowhere in the code, so it is hard to find, and renaming the method breaks the binding at runtime, not at compile time.

**The typical confusion**

"`Intent` is the data." No — it is **the envelope**. The data sits in the extras `Bundle` (see 37.22). The `Intent` has a destination, an action and flags too.

The second: "an `Intent` with no component is useless". On the contrary — it is the only way to ask for a result `Intent` to exist, and the only way to launch an app you do not know (implicit).

The third: "explicit and implicit `Intent` are synonyms when there is a single handler". No. An explicit `Intent` bypasses resolution and goes straight to the component; an implicit one goes through the `PackageManager` and can find **another** app than the one you had in mind. For internal navigation, explicit is the only correct variant.

The fourth: "`putExtra` can receive any object". Only primitives, `String`, `Serializable`, `Parcelable` and arrays of them. A `View` or a `Context` does not pass — and the error appears at runtime, when the bundle is written.

---

## Concept 37.22 — Bundle and what travels between activities

**What it is**

A `Bundle` is **a key-value collection** in which the keys are `String`s and the values are primitives, `String`, `Serializable`, `Parcelable` or arrays of them. The extras of an `Intent` **are** a `Bundle`: `putExtra(key, value)` writes into it, `getXxxExtra(key)` reads from it. The `Bundle` is also the mechanism through which the system gives you back the saved state (see 37.12).

**Why it exists**

Because the boundary between two Android components is a **process** boundary, not an object boundary. Even if `MainActivity` and `ItemActivity` run in the same process, the communication goes through `Binder`, which transports only bytes. A `Bundle` is the structure that knows how to turn Java values into bytes and back, in a way the system can transport and store.

**How it works**

What happens to each value, along the way:

```
MainActivity                                  ItemActivity
------------                                  ------------
intent.putExtra("position", 0)
   -> Bundle.putInt("position", 0)
   -> stored as an int (not as an object)

intent.putExtra("movie", movie)
   -> Bundle.putSerializable("movie", movie)
   -> when needed: ObjectOutputStream -> byte[]

   Bundle { "position" -> 0,
            "movie"    -> byte[] }

        |  Binder transaction
        |  (shared buffer, ~1 MB per process)
        v

ItemActivity.getIntent()
   -> the same Bundle, but with the values deserialised on demand
   -> getIntExtra("position", -1)            -> 0
   -> getSerializableExtra("movie")          -> Movie@A'  (COPY)
```

Three practical consequences:

1. **The key is a contract.** `"movie"` on one side and `"Movie"` on the other → `null`, with no error at all. That is why G1097 keeps the keys in constants: `protected static final String MOVIE_EXTRA = "movie";`.
2. **The default value is mandatory on reading.** `getIntExtra(key, -1)` needs a value to return when the key is missing. G1097 uses `-1` as a **sentinel** for "there is no position", that is, the insert mode.
3. **There is a size limit.** `Binder` has a buffer of ~1 MB per process. A large `Bitmap` or a list of thousands of objects produces `TransactionTooLargeException` — an exception that appears at `launch`, not at `putExtra`.

The reading types, with the default value:

| Method | Returned type | Default in G1097 |
|---|---|---|
| `getIntExtra(key, def)` | `int` | `-1` |
| `getStringExtra(key)` | `String` or `null` | — |
| `getBooleanExtra(key, def)` | `boolean` | — |
| `getSerializableExtra(key)` | `Serializable` (needs a cast) | — |
| `IntentCompat.getSerializableExtra(intent, key, Class)` | typed | — |

**What breaks without it**

- **Wrong key**: `null` or the default value, with no error. The most frequent `Intent` bug, and the reason the keys live in constants.
- **Wrong type on reading**: `getIntExtra` on a key that holds a `String` returns the default value, not an exception. `getSerializableExtra` with a wrong cast throws `ClassCastException`.
- **`TransactionTooLargeException`**: when sending a large object. The symptom is a crash in `launcher.launch(intent)`, with a message about the `Binder transaction`.
- **Unsuitable default value**: `getIntExtra(POSITION_EXTRA, 0)` instead of `-1` would make every insert be treated as an edit of the first movie. Watch out for the sentinel.
- **A mutable object modified after `putExtra`**: it is not seen in the other activity, because the serialisation happened at `putExtra`. The behaviour is correct, but counter-intuitive.

**Where you see it in G1097**

Three places, which form a complete circuit:

```java
// MainActivity — writing (two extras)
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);

// ItemActivity — reading, with a sentinel
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    ...
}

// ItemActivity — writing back
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);

// MainActivity — reading in the callback
Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
int position = intent.getIntExtra(POSITION_EXTRA, -1);
if (position == -1) {
    movies.add(movie);
} else {
    movies.set(position, movie);
}
```

Notice the asymmetry in `saveMovie()`: `POSITION_EXTRA` is put **only** if `position != -1`. On insert, `position` is `-1`, so the extra is missing, and `MainActivity` receives the default value `-1` and takes the `add` branch. On edit, `position` is `0` or higher, the extra exists, and `MainActivity` takes the `set` branch. A single `int` encodes two modes of operation.

**The typical confusion**

"The `Bundle` is the same object at both ends." No. It is serialised on writing and deserialised on reading. The consequence: the `Movie` object in `ItemActivity` is a copy, and modifying it does not touch the list (see 37.16).

The second: "`putExtra` accepts anything". Only types that `Bundle` can write. A `Context`, a `View`, a `Drawable` are not accepted — and the error appears at runtime.

The third: "the `Bundle` is for permanent data". No. It lives as long as the `Intent` or as long as the task. For persistence you need a file, `SharedPreferences` or a database (see 37.12).

The fourth: "if I send a big list, it works". Up to ~1 MB. Above that, `TransactionTooLargeException`. For big lists, send an ID and read from the database in the other activity.

---

## Concept 37.23 — ActivityResultLauncher

**What it is**

`ActivityResultLauncher<Intent>` is the object through which **you start an activity and receive a result back**. It is obtained from `registerForActivityResult(contract, callback)`, and the launch is done with `launcher.launch(intent)`. It replaces the old pair `startActivityForResult()` + `onActivityResult()`, which was deprecated.

**Why it exists**

Because the old mechanism had three structural problems. The first: **request codes** (`REQUEST_CODE = 1`) that you had to manage by hand, with a risk of collision. The second: **a single callback for all the results** — `onActivityResult(requestCode, resultCode, data)` — a `switch` that grew with every screen. The third, the most serious: if the activity was **recreated** (on rotation) while the child screen was open, the result was lost or arrived at another instance.

`ActivityResultLauncher` solves all three: each launch has its own callback, there are no request codes, and the registration survives recreation because it is held by the `ActivityResultRegistry`, not by the activity instance.

**How it works**

The complete cycle:

```
1. onCreate()
     launcher = registerForActivityResult(
                    new ActivityResultContracts.StartActivityForResult(),
                    callback)
        |
        |-- registers the callback in a registry held by ComponentActivity
        |-- the key is generated automatically, not by you
        v

2. launcher.launch(intent)
        |
        |-- starts ItemActivity (like any startActivity)
        |-- records that this launch is waiting for a result
        v

3. ItemActivity: setResult(RESULT_OK, intent) + finish()
        |
        v

4. MainActivity comes back to the foreground
        |
        |-- ActivityResultRegistry finds the callback for this launch
        v
   callback.onActivityResult(ActivityResult o)
        |-- o.getResultCode()  -> RESULT_OK / RESULT_CANCELED
        |-- o.getData()        -> the Intent with the extras (may be null)
```

The registration rule, which produces the most frequent exception: **`registerForActivityResult` must be called before the activity is `STARTED`.** In practice, in `onCreate`. If you move it into a listener, you get:

```
IllegalStateException: LifecycleOwner ... is attempting to register while
current state is RESUMED. LifecycleOwners must call register before they are STARTED.
```

The reason: the registry has to know which callbacks exist **before** receiving a result, and the result can arrive at any time after `onStart`.

**What breaks without it**

- **`registerForActivityResult` inside a listener**: `IllegalStateException` on the first click. It is the classic trap of migrating from the old API.
- **Without `setResult` in the child**: the parent receives `RESULT_CANCELED` and ignores everything. It happens when you press Back "to test" and believe you saved.
- **`o.getData()` used without a check**: `NullPointerException` when the result comes without an `Intent` (for example `RESULT_CANCELED`). G1097 checks `getResultCode() == RESULT_OK` first, but does not check `getData()` — a real risk if someone calls `setResult(RESULT_OK)` without an `Intent`.
- **Two simultaneous launches with the same launcher**: it works, but the callback cannot tell which one came back first. For simultaneous cases you need separate launches.

**Where you see it in G1097**

The field declaration and the registration, at the **end** of `onCreate`:

```java
private ActivityResultLauncher<Intent> launcher;

// ... in onCreate, after initControls() and initListeners():
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

The position in `onCreate` is significant: `initListeners()` runs **before**, and the listeners use `launcher`. Nothing breaks because `onClick` does not execute in `onCreate` — but if someone moved `launcher.launch(...)` directly into `initListeners()`, they would get a `NullPointerException`. The correct order would be the other way round, but the code works through the delay in execution.

The callback is an **anonymous class**, not a lambda, although `ActivityResultCallback` has a single method. A lambda would have been equivalent:

```java
launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
        result -> {
            if (result.getResultCode() == RESULT_OK) {
                Intent data = result.getData();
                ...
            }
        });
```

The launch, in two listeners:

```java
// FAB — insert
fabInsert.setOnClickListener(v -> launcher.launch(new Intent(MainActivity.this, ItemActivity.class)));

// row — edit
listView.setOnItemClickListener((parent, view, position, id) -> {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
});
```

**The typical confusion**

"`registerForActivityResult` can be called anywhere". No — only before `STARTED`. In practice, in `onCreate`. Inside a listener, it throws.

The second: "the callback runs immediately after `launch`". No. It runs when the child activity closes and the parent comes back to the foreground. Seconds or minutes can pass between `launch` and the callback.

The third: "`ActivityResultLauncher` is just a wrapper over `startActivityForResult`". No. It is a new mechanism, with its own registry, which survives the recreation of the activity. The old pair was based on request codes and on a single callback.

The fourth: "one launcher per launch". No — one launcher per **type of contract**. G1097 has a single launcher, used for both launches (insert and edit), because both use the same contract: `StartActivityForResult`.

---

## Concept 37.24 — Gradle: what it does and why you need dependencies

**What it is**

Gradle is **the build system** of the Android project. It reads the `build.gradle.kts` files, downloads the dependencies, compiles the Java code, compiles the resources with aapt2, turns the bytecode into `classes.dex` with d8, packs everything into an APK and signs it. Without it you would have to run seven tools by hand, in the correct order, with the correct parameters.

**Why it exists**

Because an Android build has **far more stages** than a `javac`. You have to compile resources, generate `R.java`, merge the manifests from the libraries with yours, convert Java bytecode into the Dalvik format, pack everything into an archive, sign it. And you have to do it the same way on your machine and on your colleague's. Gradle does this **declaratively**: you describe what you want, it decides how.

The second role, just as important: **the dependencies**. `AppCompatActivity`, `MaterialCardView`, `RecyclerView` are not in the Android SDK — they are `androidx` and Material libraries, downloaded by Gradle from Maven repositories and put on the compilation classpath and into the APK.

**How it works**

The complete pipeline, triggered by a single button:

```
build.gradle.kts + settings.gradle.kts + gradle/libs.versions.toml
        |
        v
1. CONFIGURATION
     - reads the plugins (com.android.application, the version from the catalog)
     - reads the `android { }` block: namespace, sdk versions, buildFeatures
     - resolves the dependencies from `dependencies { }` (downloads .aar / .jar)

2. COMPILING RESOURCES
     res/ + AndroidManifest.xml --aapt2--> binary resources + R.java + resources.arsc

3. COMPILING CODE
     .java --javac--> .class --d8--> classes.dex

4. PACKAGING
     classes.dex + res/ + resources.arsc + binary manifest --zip--> APK

5. SIGNING
     APK --apksigner--> signed APK (debug or release)

6. INSTALL (optional, from Android Studio)
     adb install app-debug.apk
```

The structure of the files in an Android project, with the role of each:

| File | Role |
|---|---|
| `settings.gradle.kts` | which modules the project has and from which repositories they are downloaded |
| `build.gradle.kts` (root) | common plugins, applied with `apply false` |
| `build.gradle.kts` (module) | the module configuration: `namespace`, SDK versions, dependencies |
| `gradle/libs.versions.toml` | the version catalog — a single place for all the numbers |
| `gradle.properties` | Gradle settings (JVM memory, configuration cache) |

The types of dependency, which get confused:

| Configuration | Goes into the APK? | Visible at compile time? | For what |
|---|---|---|---|
| `implementation` | yes | yes, only in the module | runtime libraries |
| `api` | yes | yes, and in the modules that depend on you | only in libraries |
| `compileOnly` | no | yes | annotations, APIs provided by the platform |
| `testImplementation` | no | only in the JVM tests | JUnit |
| `androidTestImplementation` | no (separate APK) | only in the instrumented tests | Espresso |

**What breaks without it**

- **Missing dependency**: at compile time, `cannot find symbol: class RecyclerView`. At runtime, if you managed to compile with `compileOnly`, `NoClassDefFoundError`.
- **Incompatible version**: `Manifest merger failed` or, worse, a crash at runtime because of a method that does not exist in the loaded version.
- **`minSdk` too low for a library**: `uses-sdk:minSdkVersion 21 cannot be smaller than version 24 declared in library`. The build fails, with a clear message.
- **Failed sync**: `R` is not generated, so `Cannot resolve symbol R` everywhere. The symptom is misleading — it looks like a code problem, in fact it is a build problem.
- **`namespace` different from the package in `AndroidManifest.xml`**: the build fails with `Namespace not specified` or, in older versions, `R` is generated in another package than the one you import.

**Where you see it in G1097**

`cod-final/build.gradle.kts` — everything that matters, in 44 lines:

```kotlin
plugins {
    alias(libs.plugins.android.application)     // the plugin, with the version from the catalog
}

android {
    namespace = "ro.ase.ie.g1097"
    compileSdk {
        version = release(37)                    // the new AGP syntax
    }

    defaultConfig {
        applicationId = "ro.ase.ie.g1097"
        minSdk = 33
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures { viewBinding = true }         // generates the binding classes (see 37.9)

    buildTypes {
        release {
            optimization { enable = false }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.activity.ktx)            // EdgeToEdge, registerForActivityResult
    implementation(libs.appcompat)               // AppCompatActivity
    implementation(libs.constraintlayout)        // ConstraintLayout
    implementation(libs.material)                // MaterialCardView, Chip, MaterialSwitch
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}
```

Each dependency has a reason that is verifiable in the code:

| Dependency | Where the import comes from | What would be missing |
|---|---|---|
| `activity-ktx` | `androidx.activity.EdgeToEdge`, `androidx.activity.result.*` | `EdgeToEdge.enable(this)`, `ActivityResultLauncher` |
| `appcompat` | `androidx.appcompat.app.AppCompatActivity` | the base class of both activities |
| `constraintlayout` | `androidx.constraintlayout.widget.ConstraintLayout` | used in `DMA02`, not in G1097 |
| `material` | `com.google.android.material.*` | the FAB, `MaterialCardView`, `TextInputLayout`, `Chip`, `MaterialSwitch` |

The last row is the most instructive: `constraintlayout` is declared but **unused** in G1097. The dependency breaks nothing, it only adds to the size of the APK. It is an example of a "dependency inherited from the template".

`settings.gradle.kts` — a project with eight modules:

```kotlin
rootProject.name = "DMA2026"
include(":G1096")
include(":G1097")
include(":G1098")
include(":G1099")
include(":DMA02")
include(":DMA03")
include(":DMA05")
include(":DMA06")
```

Each module has its own `build.gradle.kts`, with its own `namespace` and its own `applicationId`. That is why G1097 and G1098 are separate apps, although they are in the same project — they have different `applicationId`s.

`gradle/libs.versions.toml` — the version catalog, which keeps all the numbers in a single place:

```toml
[versions]
agp = "9.4.1"
appcompat = "1.8.0"
material = "1.14.0"
activityKtx = "1.13.0"
constraintlayout = "2.2.2"

[libraries]
appcompat = { group = "androidx.appcompat", name = "appcompat", version.ref = "appcompat" }
material = { group = "com.google.android.material", name = "material", version.ref = "material" }
activity-ktx = { group = "androidx.activity", name = "activity-ktx", version.ref = "activityKtx" }
constraintlayout = { group = "androidx.constraintlayout", name = "constraintlayout", version.ref = "constraintlayout" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
```

That is where `libs.appcompat`, `libs.material`, `libs.plugins.android.application` come from. The advantage: a single version for all eight modules. If you update `material` to `1.15.0`, you do it in one place.

**The typical confusion**

"Gradle downloads code into my app." No — it downloads libraries onto your computer, puts them on the classpath at compile time and **packs** into the APK whatever is marked `implementation`. There is no code that "installs itself separately".

The second: "Sync means build". No. **Sync** reads the configuration and resolves the dependencies — that is why after a sync the classes from the libraries appear in autocomplete. **Build** compiles and produces the APK. You can have a successful sync and a failed build.

The third: "`namespace` and `applicationId` are the same thing". No. `namespace` is the package in which `R` and `BuildConfig` are generated; `applicationId` is the identity of the app on the phone. They can be different, and sometimes they have to be — for example when you have two variants (demo and paid) with the same code.

The fourth: "if I add a dependency, I have to import it too". No — you add the dependency in `build.gradle.kts`, you sync, then you write the `import`. If you forget the sync, the import does not resolve, even though the line in Gradle is correct.

---

## The map of the concepts

The table that links the 24 concepts. The "depends on" column shows what you have to understand first; the "is used by" column shows where the idea goes next.

| # | Concept | Depends on | Is used by | The question it answers |
|---|---|---|---|---|
| 37.1 | The Android app | — | all of them | "what gets installed and what starts?" |
| 37.2 | `Context` | 37.1 | 37.3, 37.9, 37.13, 37.17 | "where do I get the resources and the services from?" |
| 37.3 | Resources and `R` | 37.2 | 37.4, 37.5, 37.8 | "where does `R.id.etTitle` come from?" |
| 37.4 | `AndroidManifest.xml` | 37.1 | 37.10, 37.21 | "who knows that my activity exists?" |
| 37.5 | `View` / `ViewGroup` | 37.3 | 37.6, 37.7, 37.8 | "why is the screen a tree?" |
| 37.6 | measure / layout / draw | 37.5 | 37.7 | "when do I know how big a view is?" |
| 37.7 | The layouts | 37.5, 37.6 | 37.19 | "why does it look like this and not otherwise?" |
| 37.8 | `findViewById` | 37.3, 37.5 | 37.9, 37.18 | "how do I get from the XML to the object?" |
| 37.9 | ViewBinding | 37.8, 37.24 | 37.14 | "why not `findViewById`?" |
| 37.10 | `Activity` | 37.1, 37.4 | 37.11, 37.21 | "who creates the screen?" |
| 37.11 | The lifecycle | 37.10 | 37.12, 37.13 | "when does my code run?" |
| 37.12 | State | 37.11, 37.22 | 37.16 | "where do I save so I do not lose it?" |
| 37.13 | `Application` | 37.2, 37.11 | 37.24 | "where do I put the global initialisation?" |
| 37.14 | Listeners | 37.5 | 37.15, 37.23 | "who calls my code on click?" |
| 37.15 | Lambda | 37.14 | 37.23 | "why six lines for one?" |
| 37.16 | The model / `Serializable` | — | 37.17, 37.22 | "how does data get from one screen to another?" |
| 37.17 | Adapter | 37.16 | 37.18, 37.20 | "who tells the list what to display?" |
| 37.18 | `ViewHolder` / recycling | 37.17 | 37.19, 37.20 | "why are 1000 rows not created?" |
| 37.19 | `LayoutManager` | 37.7, 37.18 | 37.20 | "who decides where each row sits?" |
| 37.20 | `ListView` vs `RecyclerView` | 37.17, 37.18, 37.19 | — | "which one do I choose?" |
| 37.21 | `Intent` | 37.4, 37.10 | 37.22, 37.23 | "how do I ask for something to happen?" |
| 37.22 | `Bundle` | 37.16, 37.21 | 37.12, 37.23 | "what can travel?" |
| 37.23 | `ActivityResultLauncher` | 37.14, 37.21, 37.22 | — | "how do I get an answer back?" |
| 37.24 | Gradle | 37.1, 37.9 | all of them | "where do the classes that are not in the SDK come from?" |

**Three chains you can follow to check that you understood the chapter:**

```
Chain 1 — from XML to object
  37.3 (aapt2 generates R.id.etTitle)
    -> 37.5 (LayoutInflater builds the tree)
      -> 37.8 (findViewById searches the tree)
        -> 37.9 (ViewBinding does the lookup once, generated)

Chain 2 — from data to screen
  37.16 (Movie, a serialisable POJO)
    -> 37.17 (the adapter reads the list)
      -> 37.18 (ViewHolder caches the row's views)
        -> 37.19 (LayoutManager decides which rows are visible)
          -> 37.20 (ListView vs RecyclerView: who does what)

Chain 3 — from a click to another screen
  37.14 (the listener is called by the widget)
    -> 37.21 (the Intent describes what you want)
      -> 37.22 (the Bundle carries the data)
        -> 37.10 (the system creates ItemActivity)
          -> 37.23 (the launcher receives the result)
            -> 37.12 (if you do not save, rotation loses everything)
```

**The reverse map — from symptom to concept:**

| Symptom | Concepts to read |
|---|---|
| `NullPointerException` in `initControls` | 37.8, 37.10 |
| The list is empty, with no error | 37.17, 37.18 |
| The movie does not appear after Save | 37.17, 37.23 |
| The form empties on rotation | 37.11, 37.12 |
| `ActivityNotFoundException` | 37.4, 37.21 |
| `Cannot resolve symbol R` | 37.3, 37.24 |
| `ScrollView can host only one direct child` | 37.5, 37.7 |
| The element with `0dp` disappeared | 37.6, 37.7 |
| `IllegalStateException` at `registerForActivityResult` | 37.23 |
| `TransactionTooLargeException` | 37.22 |
| `ClassCastException` at `findViewById` | 37.8, 37.9 |
| The row shows another element's data | 37.18 |
| `RecyclerView` displays nothing | 37.19, 37.20 |
| `NotSerializableException` | 37.16, 37.22 |
| The app crashes before the first screen | 37.1, 37.13 |

---

## Chapter 37 summary

**The six rubrics, in one sentence each:**

1. **What it is** — the definition, with no jargon.
2. **Why it exists** — the problem it solves, what you would do by hand without it.
3. **How it works** — the mechanism, with who calls whom.
4. **What breaks without it** — the concrete error or the concrete wrong behaviour.
5. **Where you see it in G1097** — file, method, real code.
6. **The typical confusion** — what is believed wrongly, and why it is wrong.

**The 24 concepts, in a table to memorise:**

| Group | Concepts | The central idea |
|---|---|---|
| The foundation | 37.1–37.4 | the app is a package with a UID; `Context` is the link to the environment; `R` is an index of resources; the manifest is the contract with the system |
| Drawing | 37.5–37.7 | the screen is a tree; drawing has three passes; each layout has an algorithm |
| The code–XML link | 37.8–37.9 | `findViewById` searches and can return `null`; ViewBinding binds at compile time |
| Time | 37.10–37.13 | the system creates activities; the lifecycle says when you run; state has two lifetimes; `Application` runs once |
| Events | 37.14–37.15 | the widget calls you; one abstract method = lambda |
| Data | 37.16–37.20 | the model does not know the UI; the adapter translates; ViewHolder caches; LayoutManager arranges; ListView vs RecyclerView is a choice |
| The boundaries | 37.21–37.24 | `Intent` is the message; `Bundle` is the envelope; the launcher waits for the answer; Gradle builds everything |

**Ten sentences that are asked at the test, in the form in which they have to be said:**

1. **The app has no `main()`.** The system starts it when an `Intent` asks for a component declared in the manifest, and the process can be killed at any time without the user closing anything.
2. **`Context` is the interface to the app's environment, not the app.** There are several instances in the same process, and the one of type `Activity` has a theme and a window, the one of type `Application` does not.
3. **`R` contains numbers generated at build time, not data.** `R.id.etTitle` exists only if aapt2 ran, and its value is never persisted.
4. **The manifest says what exists, not what it does.** Without `<activity>` you cannot start the screen, no matter how much code you write.
5. **The screen is a tree, and drawing traverses it three times:** measure, layout, draw. That is why `getWidth()` in `onCreate` is 0.
6. **`findViewById` can return `null` and does not check the type.** ViewBinding moves both checks to compile time, because it generates fields from the same XML.
7. **The activity is created by the system, by reflection, with a constructor with no parameters.** `new MainActivity()` compiles and is completely non-functional.
8. **`onDestroy` does not run when the system kills the process.** That is why saving is done in `onSaveInstanceState`, not in `onDestroy`.
9. **The adapter is called by the widget, not by you.** You set it once; `ListView` asks it `getCount()` and `getView()` for each visible row.
10. **The object that travels through an `Intent` is a copy.** That is why editing sends a new object back and the parent does `movies.set(position, movie)`.

**Three things G1097 does not have, and why they matter:**

| Missing | The consequence | Where the example is |
|---|---|---|
| `onSaveInstanceState` | the form empties on rotation; the list resets to the three starting movies | 37.12 |
| an `Application` class | there is no place for global initialisation; the manifest has no `android:name` | `DMA02` |
| `RecyclerView` | the list is limited to `ArrayAdapter` with a single text per row | `DMA06` |

**What comes next:** if you want to apply what you understood here, chapters 33–35 give you the recipes, chapter 21 gives you the memento, and chapter 36 gives you the exam-style exercises. This chapter remains the one you come back to when the question starts with "why".
