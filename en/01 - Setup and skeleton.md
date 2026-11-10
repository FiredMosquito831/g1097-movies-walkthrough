# Chapter 01 — Project setup and skeleton

**Objective:** by the end of this chapter you have an Android project that compiles and shows an empty screen, with the Material 3 theme, no ActionBar, and `minSdk 33`.

**Estimated time:** 25–40 min (first time).

---

## Step 1.1 — Create the project

### Why

An Android project isn't "a file". It's a **Gradle project** — a folder with a build recipe. Gradle reads the recipe, downloads the libraries, compiles the Java, packages the XML resources and produces an `.apk`. Android Studio doesn't compile anything by itself; it calls Gradle.

That's why, when something breaks, the first question is always: *what did Gradle say?*

### How

1. Android Studio → **File → New → New Project**.
2. Template: **Empty Views Activity** (NOT "Empty Activity" — that one is for Compose).
3. Fill in:

| Field | Value | Why |
|---|---|---|
| Name | `Movies1097` | the app name, shown under the icon |
| Package name | `ro.ase.ie.g1097` | **exactly** this; every import in the code depends on it |
| Save location | `.../Exams and tests/test 1/_progres/` | not in `cod-final/`, not in `dma2026/` |
| Language | **Java** | the project is in Java, not Kotlin |
| Minimum SDK | **API 33 ("Tiramisu")** | `minSdk = 33` in the repo |
| Build configuration language | **Kotlin DSL** | the files are `build.gradle.kts` |

4. **Finish**. Wait for "Gradle sync finished".

### Verify

In `app/build.gradle.kts` you must see `minSdk = 33`. If you put something else, change it now — not later.

> **Careful:** if the `compileSdk` Studio proposes is lower than 33, `minSdk 33` errors out. `compileSdk` must be ≥ `minSdk`.

---

## Step 1.2 — Understand the folder structure

### Why

Android has **two worlds** that compile together:

- **code** (`java/`) — what the app *does*;
- **resources** (`res/`) — what the app *looks like*: layouts, texts, colours, images.

Resources are not read from files at runtime. They are **compiled** into `R.java`, an automatically generated class that gives every resource an `int`. That's why you write `R.layout.activity_main` — it's an `int`, not a string.

### How

The structure you'll have:

```
app/
  src/main/
    AndroidManifest.xml          ← the app's "identity card"
    java/ro/ase/ie/g1097/
      MainActivity.java          ← the main screen
    res/
      layout/                    ← screen XML files
      values/                    ← strings, colors, themes
      values-night/              ← theme for dark mode
      drawable/                  ← vector images
      mipmap-*/                  ← the app icons
```

### Verify

Open `res/values/strings.xml`. It must contain `app_name`. Open `MainActivity.java` — it must be in the `ro.ase.ie.g1097` package.

> If your package is `ro.ase.ie.g1097` but the class is in a different subpackage, move it: right-click the file → **Refactor → Move**.

---

## Step 1.3 — The module's `build.gradle.kts`

### Why

This is the file that tells Gradle **which SDK**, **which libraries** and **which compilation options** the `app` module uses. Every line has a direct effect on the code you write.

### How

Open `app/build.gradle.kts`. Compare it with what you should have. **Don't copy blindly** — if your versions are newer, that's fine; just check that the *structure* matches.

```kotlin
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "ro.ase.ie.g1097"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "ro.ase.ie.g1097"
        minSdk = 33
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures { viewBinding = true }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.activity.ktx)
    implementation(libs.appcompat)
    implementation(libs.constraintlayout)
    implementation(libs.material)
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}
```

### Line-by-line explanation

| Line | What it does | Why it matters to you |
|---|---|---|
| `namespace` | the package where `R` is generated | if you change it, every `import ro.ase.ie.g1097.R` breaks |
| `applicationId` | the ID in the Play Store / on the phone | two apps with the same ID overwrite each other |
| `minSdk = 33` | the oldest Android version it runs on | below 33, some APIs used here don't exist |
| `targetSdk = 37` | which version it's optimised for | affects runtime behaviour |
| `buildFeatures { viewBinding = true }` | generates `ActivityMainBinding` classes etc. | **enabled, but the code doesn't use it** — see ch. 07, step 7.2 |
| `optimization { enable = false }` | disables R8 in release | otherwise the code would be minified and class names changed |
| `VERSION_11` | the Java language level | if you set 8, you can't use newer `var`, lambdas etc. |
| `implementation(libs.material)` | Material Components | **required** for `MaterialCardView`, `MaterialSwitch`, `Chip`, `MaterialButton` |

### Verify

**Build → Make Project** (Ctrl+F9). It must say `BUILD SUCCESSFUL`.

> **Common error:** `Unresolved reference: libs`. That means `gradle/libs.versions.toml` isn't synced. **File → Sync Project with Gradle Files**.

---

## Step 1.4 — `libs.versions.toml`

### Why

Modern Android Studio keeps library versions in a **version catalog**: a TOML file where you define a version once, then reference it with `libs.name`. The benefit: a single source of truth for versions across the whole project.

### How

Open `gradle/libs.versions.toml`. The content from the repo:

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

[libraries]
junit = { group = "junit", name = "junit", version.ref = "junit" }
ext-junit = { group = "androidx.test.ext", name = "junit", version.ref = "junitVersion" }
espresso-core = { group = "androidx.test.espresso", name = "espresso-core", version.ref = "espressoCore" }
appcompat = { group = "androidx.appcompat", name = "appcompat", version.ref = "appcompat" }
material = { group = "com.google.android.material", name = "material", version.ref = "material" }
activity-ktx = { group = "androidx.activity", name = "activity-ktx", version.ref = "activityKtx" }
constraintlayout = { group = "androidx.constraintlayout", name = "constraintlayout", version.ref = "constraintlayout" }
coordinatorlayout = { group = "androidx.coordinatorlayout", name = "coordinatorlayout", version.ref = "coordinatorlayout" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
```

### Exercise 1.4

**Requirement:** add a catalog entry for `androidx.recyclerview:recyclerview:1.4.0`, named `recyclerview`. Don't use it yet — just declare it.

<details>
<summary>Hint</summary>

You need two things: an entry in `[versions]` (e.g. `recyclerview = "1.4.0"`) and one in `[libraries]` referencing it with `version.ref`.

</details>

<details>
<summary>Solution</summary>

**What was done:** you added a **catalog entry** — a version declaration and a library reference. You haven't added the library to the build yet.

```toml
[versions]
# ... existing ...
recyclerview = "1.4.0"

[libraries]
# ... existing ...
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

**How it works:** `[versions]` holds the version **number** under a name. `[libraries]` holds the Maven **coordinates** (`group:name:version`) and links the version via `version.ref`. When you write `libs.recyclerview` in `build.gradle.kts`, Gradle resolves the chain: `libs.recyclerview` → `androidx.recyclerview:recyclerview:1.4.0`.

**Why two entries and not one:** if you wrote the version directly in `[libraries]`, you'd repeat it for every library in the same group. With `version.ref`, you change it in one place — every library referencing it updates.

**Remember:**
1. The catalog is **declarative**. It downloads nothing. The download happens when the library appears in `dependencies { }`.
2. `Sync Project with Gradle Files` regenerates the `libs.*` accessors. Without a sync, Android Studio doesn't see the new entry.
3. Names in `[libraries]` with hyphens (`activity-ktx`) become `libs.activity.ktx` — dots, not hyphens. TOML normalizes them.

**Where it comes back:** in chapter 11 (step 11.4) you add `implementation(libs.recyclerview)` to `dependencies`. Only then is the library downloaded and `RecyclerView` available in code. The same entry, but used.

</details>

---

## Step 1.5 — `AndroidManifest.xml`

### Why

The manifest is **the only file Android reads before any code starts**. It tells the system:

- which activities exist and which one is first;
- which permissions the app requests;
- which theme it has;
- which icon it has.

Without an activity marked `MAIN` + `LAUNCHER`, the app doesn't appear in the launcher.

### How

Open `app/src/main/AndroidManifest.xml`. The final target:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
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

</manifest>
```

> **You don't have `ItemActivity` yet.** For now declare only `MainActivity`. You add the second activity at step 7.1, when you create it. If you declare it now, the build fails with "class not found".

### Explanation

| Attribute | Meaning |
|---|---|
| `android:name=".activities.MainActivity"` | the leading dot = the `namespace` package + the rest. So `ro.ase.ie.g1097.activities.MainActivity` |
| `android:exported="true"` | required for the launcher activity; without it, Android 12+ refuses to install |
| `android:exported="false"` | `ItemActivity` is started only from inside the app |
| `windowSoftInputMode="adjustResize"` | when the keyboard appears, the layout shrinks instead of being covered |
| `android:theme="@style/Theme.G1097"` | the theme applies to the whole app |

> **Watch out for `.activities.`** — in the repo, the activities live in the `activities` subpackage. If at step 1.1 you left `MainActivity` in the root package, you have two options: (a) move the class into `activities` (recommended, that's the repo structure), or (b) write `android:name=".MainActivity"`. **Choose (a)** — the rest of the material assumes `ro.ase.ie.g1097.activities`.

### Exercise 1.5

**Requirement:** move `MainActivity` into the `activities` subpackage and update the manifest. Run the app — it must still start.

<details>
<summary>Hint</summary>

Right-click `MainActivity.java` → **Refactor → Move** → choose `ro.ase.ie.g1097.activities`. Android Studio updates the `package` in the file and the manifest by itself.

</details>

<details>
<summary>Solution</summary>

```java
package ro.ase.ie.g1097.activities;
```

and in the manifest:

```xml
android:name=".activities.MainActivity"
```

**What was done:** you moved the `MainActivity` class from the root package `ro.ase.ie.g1097` into the subpackage `ro.ase.ie.g1097.activities`, and updated the reference in the manifest.

**How it works:** the `package` in the `.java` file **is** the class's position in the package hierarchy — it's not just a label. When you move the file into the `activities/` folder, you must also declare `package ro.ase.ie.g1097.activities;` to match. The manifest uses the **relative path** to the `namespace`: `.activities.MainActivity` = `ro.ase.ie.g1097` + `.activities.MainActivity`.

**Why it matters:** `android:name` in the manifest is resolved by `PackageManager` at install time. If the name doesn't match a real class, the app crashes at startup with `ClassNotFoundException` — not at compile time.

**Remember:**
1. **The package and the folder must match.** Java allows them not to (the compiler doesn't check), but the tools (Android Studio, Gradle, the manifest) rely on the correspondence.
2. `Refactor → Move` does **three** things at once: moves the file, changes the `package`, updates every reference (including the manifest).
3. If you move it manually (drag & drop), you have to do all three yourself.

**Where it comes back:** in chapter 07 (step 7.1), `ItemActivity` is created directly inside `activities`. And in chapter 08 (step 8.3), the discussion about `protected` depends on both activities being in the **same package**.

</details>

---

## Step 1.6 — The Material 3 theme, without an ActionBar

### Why

The theme decides **everything** about appearance: colours, typography, shapes, shadows. The repo uses `Theme.Material3.DayNight.NoActionBar`:

- **Material3** → the Material components you'll use have the correct style;
- **DayNight** → switches automatically between light and dark based on the phone setting;
- **NoActionBar** → no implicit title bar; each screen draws its own content from the top.

`NoActionBar` matters: `activity_item.xml` starts directly with a `ScrollView` that has `android:id="@+id/main"` and padding from insets. If an ActionBar existed, the content would be pushed down and the padding would come out wrong.

### How

`res/values/themes.xml`:

```xml
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Base.Theme.G1097" parent="Theme.Material3.DayNight.NoActionBar">
        <!-- Customize your light theme here. -->
    </style>

    <style name="Theme.G1097" parent="Base.Theme.G1097" />
</resources>
```

`res/values-night/themes.xml`:

```xml
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Base.Theme.G1097" parent="Theme.Material3.DayNight.NoActionBar">
        <!-- Customize your dark theme here. -->
    </style>
</resources>
```

### Why two files?

`values-night/` is read **only** when the phone is in dark mode. Android overlays resources: first it takes `values/`, then, if `values-night/` exists and it's night mode, it overrides with `values-night/`.

That's why `Base.Theme.G1097` is defined in **both** — you can customise the light and dark colours separately. `Theme.G1097` is defined only in `values/`, because it inherits from `Base.Theme.G1097` and will automatically pick the correct version.

> If your name is different (e.g. `Theme.Movies1097`), use it consistently: in `themes.xml` **and** in `AndroidManifest.xml`. A wrong name = `Resources$NotFoundException` at startup.

### Exercise 1.6

**Requirement:** change `colorPrimary` in the light theme to a dark blue (`#1565C0`) and check on the emulator that the future buttons use it. Then switch the phone to dark mode and observe what happens.

<details>
<summary>Hint</summary>

Add `<item name="colorPrimary">#1565C0</item>` in `Base.Theme.G1097` in `values/themes.xml`. To see the effect you need a component that uses `colorPrimary` — you don't have one yet. **Come back to this exercise after chapter 03.**

</details>

<details>
<summary>Solution</summary>

```xml
<style name="Base.Theme.G1097" parent="Theme.Material3.DayNight.NoActionBar">
    <item name="colorPrimary">#1565C0</item>
</style>
```

**What was done:** you added an `<item>` to the base style, which **overrides** `colorPrimary` inherited from `Theme.Material3.DayNight.NoActionBar`.

**How it works:** a `<style>` with a `parent` **inherits** all the parent's attributes, then can override the ones it declares. So `Base.Theme.G1097` has all the Material 3 colours, except `colorPrimary`, which is dark blue.

**Why you can't see anything yet:** no component in the "Hello World" screen uses `colorPrimary`. The `TextView` uses `textColor` (which is `colorOnSurface`), not `colorPrimary`. So the change is **inert** until a FAB, a `MaterialButton`, a card title etc. appear.

**Remember:**
1. **Style inheritance** is the chain: `Theme.G1097` → `Base.Theme.G1097` → `Theme.Material3.DayNight.NoActionBar` → … → `Theme.MaterialComponents`.
2. `values-night/themes.xml` **overrides** `Base.Theme.G1097` only in dark mode. If you don't put an `<item>` there, the colour from `values/` stays.
3. A theme attribute is referenced with `?attr/name` in a layout, `?attr/` in XML, `MaterialColors.getColor(view, R.attr.name)` in code.

**Where it comes back:** in chapter 03, the FAB uses `colorPrimaryContainer` as its background. In chapter 06, the filled `MaterialButton` uses `colorPrimary`. Only there do you see the blue.

</details>

---

## Step 1.7 — `strings.xml`

### Why

Texts aren't written directly in the layout. They go in `strings.xml` and are referenced with `@string/name`. Three reasons:

1. **Translation** — add `values-ro/strings.xml` and you have the app in Romanian, without touching the layout.
2. **One place to change** — you rename the app from one place.
3. **Lint errors avoided** — Android Studio warns you if you hardcode texts.

> **Assumed exception in the repo:** many texts in `activity_item.xml` are written directly (`android:text="Movie details"`). That's the professor's choice for readability in the lab. In your code you can do the same, but **know why** you're doing it.

### How

`res/values/strings.xml`:

```xml
<resources>
    <string name="app_name">G1097</string>

    <string-array name="items">
        <item>Item 1</item>
        <item>Item 2</item>
        <!-- ... up to Item 20 ... -->
    </string-array>

    <string-array name="movie_genre">
        <item>Drama</item>
        <item>Action</item>
        <item>Comedy</item>
        <item>Horror</item>
        <item>Romance</item>
        <item>Thriller</item>
        <item>Sci-Fi</item>
        <item>Adventure</item>
        <item>Fantasy</item>
        <item>Mystery</item>
    </string-array>
</resources>
```

### What the two arrays are

- **`items`** — 20 rows "Item 1" … "Item 20". They are **demo** data, used by `ListView` through `android:entries="@array/items"` in `activity_main.xml`. They don't come from code. You'll replace them with the real movies in chapter 04.
- **`movie_genre`** — the 10 genres, used by `Spinner` through `android:entries="@array/movie_genre"`. These **stay** — they're the real genre list in the form.

### Exercise 1.7

**Requirement:** add the genre `Documentary` to `movie_genre`, in the 3rd position (that is, between `Action` and `Comedy`). What happens to a movie that had the genre `Comedy` saved before?

<details>
<summary>Hint</summary>

Think about how `fillForm` finds the genre: it compares the **text**, not the index. See `ItemActivity.fillForm`, the loop `for(int index=0; index<spGenre.getCount(); index++)`.

</details>

<details>
<summary>Solution</summary>

```xml
<string-array name="movie_genre">
    <item>Drama</item>
    <item>Action</item>
    <item>Documentary</item>
    <item>Comedy</item>
    <!-- ... -->
</string-array>
```

The movie with the genre `Comedy` **stays correct**: `fillForm` searches by text (`spGenre.getItemAtPosition(index).equals(existing.getGenre())`), not by position. So you can insert anywhere without breaking the data.

**What was done:** you added an element to `movie_genre` **in the middle** of the array, not at the end. Every genre after it shifts its index by +1.

**What you see:** in the `Spinner`, the order of the options changes. `Documentary` appears in position 3. But a movie saved with `genre = "Comedy"` is still found correctly when edited.

**Why:** `Movie.genre` is a `String` ("Comedy"), not an index. `fillForm` **searches** the text in the list and only then computes the index:

```java
for (int index = 0; index < spGenre.getCount(); index++) {
    if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
        spGenre.setSelection(index);
        break;
    }
}
```

So the index is **derived** from the text, not stored.

**Remember:**
1. **Store the value, not the position.** A position in a list that can change is a fragile reference.
2. If `Movie` had `int genreIndex`, the insertion would have broken every movie after position 2.
3. The same principle applies to `RadioGroup`: you store the **text** of the button ("PG-13"), not its index.

**Where it comes back:** in chapter 09 (step 9.2), the search loop in `fillForm` is exactly the mechanism that makes insertion possible. And in chapter 11 (step 11.13), `DiffUtil.areItemsTheSame` has the same problem: without a stable `id`, it relies on the title.

</details>

---

## Step 1.8 — `colors.xml` and the vector drawable

### Why

`colors.xml` in the repo contains only black and white — the rest of the colours come from the Material theme. You keep them because the template references them.

`outline_add_24.xml` is a **vector icon** (a `VectorDrawable`): a plus sign, drawn with an SVG `pathData`. It's used as the icon of the floating button. The advantage over a PNG: it scales perfectly at any density, with no multiple files.

### How

`res/values/colors.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
```

`res/drawable/outline_add_24.xml`:

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:height="24dp"
    android:tint="#000000"
    android:viewportHeight="960"
    android:viewportWidth="960"
    android:width="24dp">

    <path android:fillColor="@android:color/white"
        android:pathData="M440,520L200,520L200,440L440,440L440,200L520,200L520,440L760,440L760,520L520,520L520,760L440,760L440,520Z" />
</vector>
```

### How to read `pathData`

`M440,520` = **M**ove to (440, 520). `L200,520` = **L**ine to (200, 520). Uppercase letters mean absolute coordinates, lowercase relative.

It draws a plus: you start at (440,520), go left to (200,520), up to (200,440), right to (440,440)... and so on, until the shape closes. The coordinate system is 960×960 (`viewport`), but the icon displays at 24dp (`width`/`height`).

> **You don't have to draw paths yourself.** Android Studio has **File → New → Vector Asset** with ready-made Material icons. But you need to know what a `VectorDrawable` is, because it can be an exam question.

### Exercise 1.8

**Requirement:** create a `VectorDrawable` named `ic_delete_24.xml` that draws a diagonal line (a simplified "X"). Use `File → New → Vector Asset → Clip Art → Delete`.

<details>
<summary>Hint</summary>

If you use Vector Asset, Android Studio writes the path itself. Then check the file is in `res/drawable/` and that you can reference `@drawable/ic_delete_24` from a layout.

</details>

<details>
<summary>Solution</summary>

The generated file looks similar to:

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal">
    <path android:fillColor="@android:color/white"
        android:pathData="M6,19c0,1.1 0.9,2 2,2h8c1.1,0 2,-0.9 2,-2V7H6v12zM19,4h-3.5l-1,-1h-5l-1,1H5v2h14V4z" />
</vector>
```

Notice `viewportWidth="24"` — a different coordinate system than the plus sign (960). Both are valid; the viewport is just the space in which the coordinates are expressed.

**What was done:** you generated a `VectorDrawable` with an SVG path that draws the "Delete" shape (a waste bin), using Vector Asset Studio.

**How a `VectorDrawable` works:** the path is a **sequence of commands** in its own coordinate system (`viewportWidth` × `viewportHeight`). The commands are letters:

| Letter | Meaning |
|---|---|
| `M x,y` | **M**ove to — moves the "pen" to (x, y) without drawing |
| `L x,y` | **L**ine to — draws a line to (x, y) |
| `H x` | **H**orizontal line to — a horizontal line to x |
| `V y` | **V**ertical line to — a vertical line to y |
| `C` / `S` | **C**ubic / **S**mooth curve — Bézier curves |
| `Z` | **Z** — closes the shape (a line back to the start point) |

Uppercase letters = **absolute** coordinates; lowercase = **relative** to the current position.

**Why `24` in Vector Asset and `960` in the plus sign:** the `viewport` is just the coordinate space, not the final size. `android:width="24dp"` is the displayed size. A path expressed in 960×960 scales to 24dp just as well as one in 24×24 — only the coordinates differ.

**Remember:**
1. **`VectorDrawable` = a vector image**, not a bitmap. It scales without loss, one file for all densities.
2. `android:tint="?attr/colorControlNormal"` allows **recolouring** from the theme — that's why the icon adapts to dark mode.
3. You don't have to write paths by hand. Vector Asset Studio has thousands of Material icons.

**Where it comes back:** in chapter 11 (step 11.11) you add an `ImageButton` with `@android:drawable/ic_menu_delete` — a **system** icon, not a custom vector. The difference: `@android:drawable/` = an Android resource, `@drawable/` = a resource of your own project.

</details>

---

## Step 1.9 — `.gitignore`

### Why

The `build/` folder contains the compilation output: hundreds of MB, regenerable, different on every machine. It doesn't go into git.

### How

`app/.gitignore`:

```
/build
```

Simple. In the repo, the G1097 module has exactly that. The root has a bigger `.gitignore` (with `.gradle`, `.idea`, `local.properties`), but for you, in `_progres/`, it doesn't matter — you're not committing.

---

## Step 1.10 — The first run

### Why

Until it runs, you have no proof the setup is correct. Don't move to chapter 02 until you see the app on the emulator.

### How

1. **Device Manager** → create an emulator if you don't have one: **Pixel 7, API 34 or 35** (anything ≥ 33).
2. Press **Run ▶** (Shift+F10).
3. Wait: the first build can take 2–5 minutes.

### Verify

- The app appears in the launcher with the name `G1097` (or `Movies1097`).
- On open you see a centred "Hello World!".
- In `Logcat` there are no red `FATAL EXCEPTION` lines.

### Exercise 1.10 — trap

**Requirement:** open `Logcat`, filter by `package:mine`, close the app from recents and reopen it. Find the line that confirms `MainActivity` was created.

<details>
<summary>Hint</summary>

Look for `Displayed ro.ase.ie.g1097/.activities.MainActivity` or `START u0 {act=android.intent.action.MAIN ...}`.

</details>

<details>
<summary>Solution</summary>

In Logcat you'll see something like:

```
ActivityTaskManager: START u0 {act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] flg=0x10200000 cmp=ro.ase.ie.g1097/.activities.MainActivity} 
ActivityTaskManager: Displayed ro.ase.ie.g1097/.activities.MainActivity: +412ms
```

That tells you two things: (1) the manifest is correct, (2) how long startup took. If you see `Unable to instantiate activity`, the manifest has the wrong name.

**What was done:** you filtered Logcat by `package:mine` and found the line that confirms the activity was created.

**How the filter works:** `package:mine` is a Logcat filter that shows only messages from your app's processes. Without it, Logcat is a stream of thousands of lines from the whole system.

**Why `START u0 {cmp=ro.ase.ie.g1097/.activities.MainActivity}` is the proof:** `cmp` = component. The format is `package/class-relative-to-package`. So `ro.ase.ie.g1097` + `.activities.MainActivity` = exactly what you declared in the manifest. If it were wrong, you'd see `ActivityNotFoundException` or `Unable to instantiate`.

**Remember:**
1. **Logcat is the main debugging tool.** `package:mine` is the first filter you set.
2. `Displayed ... +412ms` tells you the startup time — useful for performance.
3. The levels: `V` (verbose), `D` (debug), `I` (info), `W` (warning), `E` (error), `F` (fatal). `FATAL EXCEPTION` = crash.
4. A crash isn't visible "on screen" — only in Logcat.

**Where it comes back:** at every step in the following chapters, when something breaks. `NullPointerException` and `NumberFormatException` are read in Logcat, not guessed.

</details>

---

## Chapter 01 summary

You now have:

- a Gradle project that compiles;
- `minSdk 33`, Java 11, Material 3, `NoActionBar`;
- a `MainActivity` in `ro.ase.ie.g1097.activities`, declared in the manifest;
- `strings.xml` with `items` (20) and `movie_genre` (10);
- `outline_add_24.xml`;
- the `Theme.G1097` theme with a night variant.

**You don't have yet:** any `Movie` class, any layout of your own, any logic.

### Self-check (without looking)

1. Why is `android:exported="true"` required on `MainActivity`?
2. What happens if `namespace` differs from `applicationId`?
3. Why doesn't `values-night/themes.xml` contain `Theme.G1097` too?
4. What does `buildFeatures { viewBinding = true }` do, and why doesn't the current code use it?

<details>
<summary>Answers</summary>

1. From Android 12 (API 31), any activity with an `intent-filter` must declare `exported` explicitly. Without it, installation fails. `true` = it can be started from outside (the launcher is "outside").
2. `namespace` decides the package of the `R` class; `applicationId` decides the app's identity in the system. They can differ. If you change `namespace`, you must update every `import ...R`.
3. Because `Theme.G1097` inherits `Base.Theme.G1097`, and Android resolves the inheritance at runtime, taking `Base` from the appropriate configuration folder (values or values-night). The definition in `values/` is enough.
4. It generates classes like `ActivityMainBinding` that replace `findViewById` with direct, type-safe field access. The repo code uses `findViewById` — so the feature is enabled but unused. You'll use it optionally in chapter 11.

</details>

---

**Next chapter:** [02 - The Movie model.md](02%20-%20The%20Movie%20model.md)
