# Chapter 15 — DMA02: the `Application` class and the lifecycle

**Objective:** to understand the lifecycle of an `Activity` (all seven methods), what the `Application` class is, how `ActivityLifecycleCallbacks` works, and how to send an implicit `Intent`.

**Estimated time:** 40–50 min.

**Source:** `DMA02/` — the first commit in the repo, `8b04238` (2026-10-13), 29 files.

> **Why it matters:** the lifecycle is **the most frequent theory question** on the exam. `G1097` only uses `onCreate`, but you need to know what happens in the rest and in what order.

---

## Step 15.1 — The seven lifecycle methods

### Why

Android doesn't call your code whenever it wants. It calls it in **well-defined moments**, and you override what you need.

### How — the full list

`DMA02/MainActivity` overrides all of them and writes to Logcat:

```java
private static final String TAG = MainActivity.class.getSimpleName();

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    Log.w(TAG, "onCreate");
}

@Override
protected void onStart() {
    super.onStart();
    Log.w(TAG, "onStart");
}

@Override
protected void onResume() {
    super.onResume();
    Log.w(TAG, "onResume");
}

@Override
protected void onPause() {
    super.onPause();
    Log.w(TAG, "onPause");
}

@Override
protected void onStop() {
    super.onStop();
    Log.w(TAG, "onStop");
}

@Override
protected void onDestroy() {
    super.onDestroy();
    Log.w(TAG, "onDestroy");
}
```

### The order and meaning

| Method | When it is called | What you usually do there |
|---|---|---|
| `onCreate()` | on creation, **only once** per instance | `setContentView`, `findViewById`, initializations |
| `onStart()` | when it becomes visible | registering system listeners |
| `onResume()` | when it gains focus (can receive input) | starting animations, camera, sensors |
| `onPause()` | when it loses focus (another activity comes on top) | stopping animations, quick save |
| `onStop()` | when it is no longer visible | releasing heavy resources |
| `onDestroy()` | when it is destroyed | canceling callbacks, releasing |
| `onRestart()` | between `onStop` and `onStart`, on return | rarely used |

### The order on launch and on close

```
START:  onCreate → onStart → onResume
END:    onPause → onStop → onDestroy
```

### What happens in each scenario

| Scenario | Methods called |
|---|---|
| You launch the app | `onCreate` → `onStart` → `onResume` |
| You press Home | `onPause` → `onStop` |
| You come back from Home | `onRestart` → `onStart` → `onResume` |
| Another activity comes on top (dialog) | `onPause` (and `onStop` if it covers everything) |
| You press Back | `onPause` → `onStop` → `onDestroy` |
| You rotate the screen | `onPause` → `onStop` → `onDestroy` → `onCreate` → `onStart` → `onResume` |

> **Note on rotation:** the activity is **destroyed and recreated**. That's why fields are lost if you don't save them in `onSaveInstanceState`. See chapter 10, test 13.

### Why `Log.w` and not `Log.d`

`Log.w` (warning) is visible by default in Logcat without changing the level filter. `Log.d` (debug) can be hidden. For a demo, `w` is the practical choice.

### Exercise 15.1

**Requirement:** without running, write in order which methods are called when: (a) you launch the app, (b) you press Home, (c) you come back, (d) you press Back.

<details>
<summary>Answer — explanatory</summary>

**What was done:** you reconstructed the sequences from the table.

**Answer:**

| | Sequence |
|---|---|
| (a) launch | `onCreate` → `onStart` → `onResume` |
| (b) Home | `onPause` → `onStop` |
| (c) return | `onRestart` → `onStart` → `onResume` |
| (d) Back | `onPause` → `onStop` → `onDestroy` |

**Why (c) has `onRestart`:** the activity was not destroyed, only stopped. `onRestart` marks "I'm coming back from a stop", distinct from the first launch.

**Remember:**
1. `onCreate` runs **only once** per instance. On rotation it's a new instance, so it runs again.
2. `onResume`/`onPause` are pairs; `onStart`/`onStop` are pairs.
3. `onDestroy` is **not** guaranteed — if the process is killed by the system, it is not called.

**Where it comes back:** in chapter 04, `MainActivity` only has `onCreate`. The rest of the methods are missing because you don't need them — but they **are called** anyway (the versions from `AppCompatActivity`).

</details>

---

## Step 15.2 — The `Application` class

### Why

`Application` is a **single object per process**, created **before any activity**. It's the place for global initializations: libraries, DI, logging, themes.

### How

`DMA02/DMA02App.java`:

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
    // ...
}
```

### Three essential things

1. **`extends Application`** — your class becomes the global object.
2. **`registerActivityLifecycleCallbacks(this)`** — you subscribe to the lifecycle of **all** activities.
3. **`DynamicColors.applyToActivitiesIfAvailable(this)`** — enables Material You (colors extracted from the wallpaper) on Android 12+.

### Why it must be declared in the manifest

`AndroidManifest.xml`:

```xml
<application
    android:name=".DMA02App"
    ...>
```

Without `android:name`, Android uses `android.app.Application` implicitly — and your class is never instantiated.

> **Note:** the full name is `.DMA02App` (with a leading dot), relative to the `namespace`. If you write just `DMA02App`, the manifest can't find the class.

### When `Application.onCreate` runs

**Before** `Activity.onCreate`. The order at app startup:

```
Application.onCreate
  → Activity.onCreate
    → Activity.onStart
      → Activity.onResume
```

### Exercise 15.2

**Requirement:** what happens if you forget `android:name=".DMA02App"` in the manifest? Does the code in `DMA02App` still run?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you compared the manifest with and without the attribute.

**Answer:** **no.** Without `android:name`, Android instantiates `android.app.Application` — your class is never created. `Log.w(TAG, "onCreate")` from `DMA02App` doesn't show up in Logcat. No error, just silence.

**Why:** the manifest is the only source for "which `Application` class do I use". Without it, the default is taken.

**Remember:**
1. `android:name` in `<application>` = your `Application` class.
2. `android:name` in `<activity>` = the activity's class.
3. Both use the path relative to the `namespace`, with a leading dot.

**Where it comes back:** in chapter 01, step 1.5 — the same mechanism for `MainActivity`.

</details>

---

## Step 15.3 — `ActivityLifecycleCallbacks`

### Why

You want to log the lifecycle of **all** activities from a single place, without overriding the methods in each one.

### How

`DMA02App` implements seven methods:

```java
@Override
public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
    Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());
}

@Override
public void onActivityStarted(@NonNull Activity activity) {
    Log.w(TAG, "onActivityStarted" + activity.getClass().getSimpleName());
}

@Override
public void onActivityResumed(@NonNull Activity activity) {
    Log.w(TAG, "onActivityResumed" + activity.getClass().getSimpleName());
}

@Override
public void onActivityPaused(@NonNull Activity activity) {
    Log.w(TAG, "onActivityPaused" + activity.getClass().getSimpleName());
}

@Override
public void onActivityStopped(@NonNull Activity activity) {
    Log.w(TAG, "onActivityStopped" + activity.getClass().getSimpleName());
}

@Override
public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {
}

@Override
public void onActivityDestroyed(@NonNull Activity activity) {
    Log.w(TAG, "onActivityDestroyed" + activity.getClass().getSimpleName());
}
```

### Correspondence with the activity's methods

| Activity method | Callback method |
|---|---|
| `onCreate` | `onActivityCreated(activity, savedInstanceState)` |
| `onStart` | `onActivityStarted(activity)` |
| `onResume` | `onActivityResumed(activity)` |
| `onPause` | `onActivityPaused(activity)` |
| `onStop` | `onActivityStopped(activity)` |
| `onSaveInstanceState` | `onActivitySaveInstanceState(activity, bundle)` |
| `onDestroy` | `onActivityDestroyed(activity)` |

### Call order

The callback from `Application` receives the event **before** the activity's method runs. So in Logcat you see:

```
DMA02App: onActivityCreatedMainActivity
MainActivity: onCreate
DMA02App: onActivityStartedMainActivity
MainActivity: onStart
...
```

> **Remember:** `ActivityLifecycleCallbacks` is useful for: centralized logging, analytics ("how many screens the user saw"), releasing global resources. It doesn't replace the activity's methods — it **observes** them.

### Exercise 15.3

**Requirement:** why does `onActivitySaveInstanceState` have `Bundle` as its second parameter, while the others don't?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you compared the signatures.

**Answer:** because `Activity.onSaveInstanceState(Bundle outState)` needs the `Bundle` to receive the state. The callback receives **the same** `Bundle`, so it can add or read.

**Why the others don't have any:** `onStart`, `onResume` etc. have no parameters — they don't need data.

**Remember:**
1. `ActivityLifecycleCallbacks` was added in API 14.
2. `onActivityCreated` receives `savedInstanceState` — useful to know whether it's a recreation (rotation) or a fresh start.
3. `Bundle` is `null` on first creation, non-null on recreation.

**Where it comes back:** in chapter 10, test 13 (rotation) — `savedInstanceState` is what you would have needed so as not to lose the form data.

</details>

---

## Step 15.4 — `DynamicColors` (Material You)

### Why

From Android 12, the system can extract a color palette from the wallpaper. `DynamicColors` enables this for your app.

### How

```java
@Override
public void onCreate() {
    super.onCreate();
    registerActivityLifecycleCallbacks(this);
    DynamicColors.applyToActivitiesIfAvailable(this);
    // ...
}
```

### What it does

If you run on Android 12+, the Material 3 theme receives the dynamic colors. On older versions, the call is ignored — no error.

### Why in `Application` and not in each activity

`applyToActivitiesIfAvailable(this)` applies to **all** activities created after that moment. One call, once.

> **Remember:** `DynamicColors` is part of `com.google.android.material`. You don't need another dependency — `libs.material` is already there.

### Exercise 15.4

**Requirement:** what happens if you change the wallpaper on Android 12+ with the app open?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you tested the dynamic behavior.

**Answer:** the app's colors **change** after the app is recreated (or restarted). On some devices they also update live.

**Why:** `DynamicColors` reads the palette in `Application.onCreate`. When the wallpaper changes, the system may recreate the process.

**Remember:**
1. `DynamicColors.applyToActivitiesIfAvailable(this)` — `this` is the `Application`, not the `Activity`.
2. On Android < 12, the call does nothing (thanks to `IfAvailable`).
3. Your explicit colors in `themes.xml` take priority.

**Where it comes back:** in `G1097`, the theme `Theme.Material3.DayNight.NoActionBar` supports dynamic colors, but the app **does not** call `DynamicColors` — so it uses the fixed Material 3 palette.

</details>

---

## Step 15.5 — Implicit `Intent`

### Why

All `Intent`s in `G1097` are **explicit** — they say exactly which class to start. An **implicit** `Intent` only says *what operation* you want, and the system picks the app.

### How

`MainActivity.pressMe(View)`:

```java
public void pressMe(View view) {
/*        Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse("https://developer.android.com"));
    startActivity(web);*/

/*    Intent call = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0212345678"));
    startActivity(call);*/

    Intent share = new Intent(Intent.ACTION_SEND);
    share.setType("text/plain");
    share.putExtra(Intent.EXTRA_TEXT, "Hello!");
    startActivity(Intent.createChooser(share, "Share via DMA"));
}
```

### The three actions, uncommented one at a time

| Action | What it opens | Why it's commented out |
|---|---|---|
| `ACTION_VIEW` + `https://...` | the browser | demonstrative |
| `ACTION_DIAL` + `tel:...` | the phone dialer | demonstrative |
| `ACTION_SEND` + `text/plain` | the **share sheet** | **active** |

### Why `createChooser`

`ACTION_SEND` without `createChooser` would open the default share app (or show a dialog if there is no default). `createChooser(intent, title)` **always** forces the picker dialog, with the given title.

> **Remember:** `createChooser` is useful when you want the user to choose explicitly, not go with the default.

### `setType` is required for `ACTION_SEND`

Without `setType("text/plain")`, Android doesn't know which apps can receive the `Intent` → `ActivityNotFoundException`.

### `G1097` also has a receiving `intent-filter`

In `DMA02/AndroidManifest.xml` there is:

```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <category android:name="android.intent.category.DEFAULT" />
</intent-filter>
```

This means the app **shows up in the share sheet** — you can send text to it from another app.

### Exercise 15.5

**Requirement:** why is `new Intent(this, ItemActivity.class)` explicit, while `new Intent(Intent.ACTION_SEND)` is implicit?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you compared the two forms.

**Answer:**
- **Explicit:** you have a `ComponentName` — package + class. The system knows exactly what to start. `new Intent(context, ItemActivity.class)`.
- **Implicit:** you only have action + data. The system searches all installed apps for one that declares a matching `intent-filter`.

**Why it matters:**
1. Explicit = **within the app**, always the same class.
2. Implicit = **between apps**, can be any app that accepts it.

**Remember:**
1. `Intent(Context, Class)` → explicit.
2. `Intent(String action)` or `Intent(String action, Uri)` → implicit.
3. An implicit `Intent` can fail with `ActivityNotFoundException` if no app accepts it.

**Where it comes back:** in chapter 08, `launcher.launch(intent)` receives an explicit `Intent` — that's why it always works.

</details>

---

## Step 15.6 — Verification

### How

1. Open `DMA02` in Android Studio.
2. Run with **Logcat** open, filtered on `package:mine`.
3. You see in order: `DMA02App: onCreate`, then `onActivityCreatedMainActivity`, then `MainActivity: onCreate`, etc.
4. Press Home, come back, press the button. Follow the sequences.

### What to check in the code

- [ ] `DMA02App extends Application implements Application.ActivityLifecycleCallbacks`
- [ ] the manifest has `android:name=".DMA02App"`
- [ ] `registerActivityLifecycleCallbacks(this)` in `Application.onCreate`
- [ ] all 7 methods implemented
- [ ] `MainActivity` overrides all 6 lifecycle methods
- [ ] `pressMe` uses `ACTION_SEND` + `createChooser`

---

## Chapter 15 summary

- Lifecycle: `onCreate` → `onStart` → `onResume` → `onPause` → `onStop` → `onDestroy`, plus `onRestart`.
- Rotation = `onDestroy` + `onCreate` → state is lost without `onSaveInstanceState`.
- `Application` = single object per process, created before any activity.
- It is declared in the manifest with `android:name=".ClasaMea"`.
- `ActivityLifecycleCallbacks` = central observer for all activities.
- `DynamicColors` = Material You, Android 12+ only.
- `Intent` explicit = exact class. `Intent` implicit = action, the system chooses.

**Next chapter:** [16 - Istoricul repo-ului.md](16%20-%20Istoricul%20repo-ului.md)
