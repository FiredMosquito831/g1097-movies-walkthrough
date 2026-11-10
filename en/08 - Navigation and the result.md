# Chapter 08 — Navigation and the result

**Objective:** the FAB opens `ItemActivity`; `ItemActivity` sends a `Movie` back; `MainActivity` adds it to the list and redraws.

**Estimated time:** 30–45 min.

**Files changed:** `MainActivity.java` (adds `launcher` + the complete `initListeners`)

---

## Step 8.1 — Why not a plain `startActivity`

### Why

You could do:

```java
Intent intent = new Intent(this, ItemActivity.class);
startActivity(intent);
```

It works — but **you get nothing back**. `ItemActivity` would close, and you'd never find out what the user saved.

You need **two-way communication**:

```
MainActivity --Intent--> ItemActivity
MainActivity <--Intent-- ItemActivity   (result)
```

### How it's done

| Method | Status | Recommended? |
|---|---|---|
| `startActivityForResult(intent, REQUEST_CODE)` | **deprecated** since API 30 | no |
| `registerForActivityResult(...)` | current | **yes** |

The repo uses the modern variant.

---

## Step 8.2 — `registerForActivityResult`

### Why

`registerForActivityResult` registers a **callback** that will be invoked when the child activity closes with a result. It must be called **before** the activity is started (ideally in `onCreate`).

### How

```java
private ActivityResultLauncher<Intent> launcher;

// in onCreate, after initListeners():
launcher = registerForActivityResult(
        new ActivityResultContracts.StartActivityForResult(),
        new ActivityResultCallback<ActivityResult>() {
            @Override
            public void onActivityResult(ActivityResult result) {
                if (result.getResultCode() == RESULT_OK) {
                    Intent data = result.getData();
                    Movie movie = (Movie) data.getSerializableExtra(MOVIE_EXTRA);
                    int position = data.getIntExtra(POSITION_EXTRA, -1);
                    if (position == -1) {
                        movies.add(movie);
                    } else {
                        movies.set(position, movie);
                    }
                    movieAdapter.notifyDataSetChanged();
                }
            }
        });
```

### The two arguments

| Argument | What it is |
|---|---|
| `new ActivityResultContracts.StartActivityForResult()` | the **contract**: defines the input type (`Intent`) and the output type (`ActivityResult`) |
| `new ActivityResultCallback<ActivityResult>() { ... }` | the **callback**: what you do with the result |

### Why `ActivityResult` and not `Intent`

`ActivityResult` contains **three** things:

| Method | What it returns |
|---|---|
| `getResultCode()` | `RESULT_OK` or `RESULT_CANCELED` |
| `getData()` | the `Intent` with the extras (can be `null`) |
| `getResultCode()` | the result code |

If you received an `Intent` directly, you'd lose `resultCode` — and you wouldn't know whether the user saved or pressed Back.

### Exercise 8.2

**Requirement:** what happens if you forget `if (result.getResultCode() == RESULT_OK)`?

<details>
<summary>Solution — explained</summary>

**What was done:** we removed the `resultCode` check.

**What happens:** when the user presses **Back** (without saving), `ItemActivity` closes with `RESULT_CANCELED` and `getData()` = `null`. Your code would do:

```java
Movie movie = (Movie) data.getSerializableExtra(MOVIE_EXTRA);  // NPE: data is null
```

→ **crash**.

**Why:** `getData()` is `null` when no result was set. `resultCode` is the only way to tell "saved" from "gave up".

**Remember:**
1. `RESULT_OK` = the activity set a result with `setResult(RESULT_OK, intent)`.
2. `RESULT_CANCELED` = anything else (Back, forced close, `finish()` without `setResult`).
3. **Always** check `resultCode` before `getData()`.

**Where it comes back:** in ch. 09, when you edit a movie and press Back, `MainActivity` must **not** change anything. The `RESULT_OK` check is what guarantees that.

</details>

---

## Step 8.3 — The constants for the extras

### Why

The keys in an `Intent` are **strings**. If you write `"movie"` in one place and `"Movie"` in another, you get `null` with no error at all.

### How

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
```

### Why `protected static final`

| Modifier | Why |
|---|---|
| `protected` | accessible from `ItemActivity` (a subclass? no — but in the **same package** `activities`, so `protected` is enough) |
| `static` | belongs to the class, not to an instance |
| `final` | never changes |

> **Careful:** `protected` in Java means "accessible from subclasses **and** from the same package". `ItemActivity` is in `ro.ase.ie.g1097.activities`, just like `MainActivity` — so it works. If it were in another package, `protected` wouldn't be enough (you'd need `public`).

### Exercise 8.3

**Requirement:** move `ItemActivity` into the package `ro.ase.ie.g1097` (not `activities`). What happens to `MainActivity.MOVIE_EXTRA`?

<details>
<summary>Solution — explained</summary>

**What was done:** we moved the class into another package.

**What happens:** **a compile error**:

```
error: MOVIE_EXTRA has protected access in MainActivity
```

**Why:** `protected` allows access from subclasses and from the **same package**. `ItemActivity` is not a subclass of `MainActivity` and is no longer in the same package → no access.

**Remember:**
1. The access hierarchy: `private` < `package-private` (no modifier) < `protected` < `public`.
2. `protected` is **wider** than package-private only through subclasses, not through packages.
3. If you want access from any package, use `public`.

**Where it comes back:** it doesn't, but it's a classic exam question about access modifiers.

</details>

---

## Step 8.4 — Complete `initListeners`

### Why

Now you have `launcher`, so you can wire the FAB and the list click.

### How

```java
private void initListeners() {
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
}
```

### `MainActivity.this` vs `this`

Inside the anonymous class `new View.OnClickListener() { ... }`, `this` refers to the **anonymous class**, not to `MainActivity`. So `new Intent(this, ...)` would error (the type `View.OnClickListener` isn't a `Context`).

The solution: `MainActivity.this` — an explicit reference to the outer instance.

> **Remember:** in a lambda, `this` refers to the **outer** class. So `new Intent(this, ItemActivity.class)` would work in a lambda, but not in an anonymous class. It's an important difference.

### `launcher.launch(intent)` vs `startActivity(intent)`

`launcher.launch(intent)`:
1. starts the activity,
2. guarantees that `onActivityResult` will be called on close.

`startActivity(intent)`:
1. starts the activity,
2. **you get nothing back**.

### Exercise 8.4

**Requirement:** rewrite both listeners with lambdas. What happens to `MainActivity.this`?

<details>
<summary>Solution — explained</summary>

**What was done:** we replaced the anonymous classes with lambdas.

```java
private void initListeners() {
    fabInsert.setOnClickListener(v -> {
        Intent intent = new Intent(this, ItemActivity.class);
        launcher.launch(intent);
    });

    listView.setOnItemClickListener((parent, view, position, id) -> {
        Intent intent = new Intent(this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    });
}
```

**What happens to `MainActivity.this`:** **it's no longer needed.** In a lambda, `this` refers to the **outer** instance (`MainActivity`). So `new Intent(this, ...)` works directly.

**Why:** a lambda doesn't create a "real" anonymous class with its own `this` — it's a function that captures the context. `this` stays that of the class that defines it.

**Remember:**
1. **Anonymous class**: `this` = the anonymous class → you need `MainActivity.this`.
2. **Lambda**: `this` = the outer class → `this` is enough.
3. `OnItemClickListener` has **four** parameters, but it's still functional (a single method `onItemClick`). A lambda works.

**Where it comes back:** in ch. 11, `MovieAdapter` uses a lambda for `setOnClickListener` — there `this` is `MovieViewHolder`, and `MainActivity` isn't directly accessible. That's why a **callback** is used (`OnItemClickListener` defined in the adapter).

</details>

---

## Step 8.5 — The complete flow, traced

### How

1. The user presses the FAB.
2. `fabInsert.setOnClickListener` → `launcher.launch(intent)`.
3. `ItemActivity.onCreate` → `initControls`, `initListeners`.
4. The user fills in the form, presses Save.
5. `saveMovie()` → `setResult(RESULT_OK, intent)` → `finish()`.
6. `ItemActivity` closes.
7. `MainActivity.onActivityResult` is called with an `ActivityResult`.
8. `resultCode == RESULT_OK` → extract `Movie` and `position`.
9. `position == -1` → `movies.add(movie)`.
10. `movieAdapter.notifyDataSetChanged()` → the `ListView` redraws.
11. The movie appears in the list.

### The diagram

```
MainActivity                    ItemActivity
    |                                |
    |-- launcher.launch(intent) ---->|
    |                                | onCreate
    |                                | initControls
    |                                | initListeners
    |                                | (the user fills it in)
    |                                | saveMovie()
    |                                | setResult(RESULT_OK, intent)
    |                                | finish()
    |<---- onActivityResult ---------|
    |  resultCode = RESULT_OK        |
    |  data = intent with Movie      |
    |                                |
    | movies.add(movie)              |
    | notifyDataSetChanged()         |
    | ListView redraws               |
```

### Exercise 8.5

**Requirement:** add a `Toast` in `onActivityResult` that shows the title of the received movie. Run it, save a movie, see the toast.

<details>
<summary>Hint</summary>

`Toast.makeText(context, text, Toast.LENGTH_SHORT).show();`

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we added a `Toast` after extracting the movie.

```java
if (result.getResultCode() == RESULT_OK) {
    Intent data = result.getData();
    Movie movie = (Movie) data.getSerializableExtra(MOVIE_EXTRA);
    int position = data.getIntExtra(POSITION_EXTRA, -1);
    Toast.makeText(this, "Saved: " + movie.getTitle(), Toast.LENGTH_SHORT).show();
    // ... the rest
}
```

**What you see:** on save, a toast appears at the bottom with "Saved: Interstellar".

**Why it works:** `Toast` is a non-blocking message, shown for 2 seconds. It doesn't stop execution.

**Remember:**
1. `Toast.makeText(context, text, duration)` — `context` is `this` (MainActivity).
2. `LENGTH_SHORT` = 2s, `LENGTH_LONG` = 3.5s.
3. `show()` is mandatory — without it, the toast doesn't appear.
4. `Toast` is useful for quick debugging, but it **doesn't** replace `Log.d`.

**Where it comes back:** it doesn't, but it's a debugging tool you'll use often.

</details>

---

## Step 8.6 — `getSerializableExtra` vs `IntentCompat`

### Why

The repo uses two different variants:

- `MainActivity`: `(Movie) intent.getSerializableExtra(MOVIE_EXTRA)`
- `ItemActivity`: `IntentCompat.getSerializableExtra(intent, MOVIE_EXTRA, Movie.class)`

### Why they differ

`getSerializableExtra(String)` is **deprecated** in API 33+. `IntentCompat` is the modern variant, which requires the class type.

The repo updated only `ItemActivity`, not `MainActivity`. It's an inconsistency — both work, but the one in `MainActivity` gives a compile warning.

> **Remember:** if you see a yellow warning on `getSerializableExtra`, it's not an error. The code works. But the modern variant is `IntentCompat`.

### Exercise 8.6

**Requirement:** update `MainActivity` to use `IntentCompat.getSerializableExtra(data, MOVIE_EXTRA, Movie.class)`. Check that it works.

<details>
<summary>Solution — explained</summary>

**What was done:** we replaced the line in `onActivityResult`.

```java
import androidx.core.content.IntentCompat;
// ...
Movie movie = IntentCompat.getSerializableExtra(data, MOVIE_EXTRA, Movie.class);
```

**Why it works:** `IntentCompat` is a compatibility class that calls the right method depending on the Android version.

**Remember:**
1. `IntentCompat.getSerializableExtra` does **not** return `Serializable`, it returns `Movie` directly — no cast.
2. If the type doesn't match, it returns `null` (or throws, depending on the version).
3. It's the recommended variant for new code.

**Where it comes back:** it doesn't.

</details>

---

## Step 8.7 — Initialization order (the repo's trap)

### Why

In `onCreate` from the repo:

```java
initControls();
initListeners();     // ← registers listeners that use `launcher`
launcher = registerForActivityResult(...);   // ← launcher initialized AFTER
```

### Why it works anyway

Because `initListeners` **doesn't call** `launcher.launch(...)` immediately. It only **registers** a listener that, **on click**, will call `launcher.launch(...)`.

By the time of the click, `launcher` is already initialized. So it works.

### When it would crash

If you called `fabInsert.performClick()` right after `initListeners()`:

```
NullPointerException: Attempt to invoke virtual method
'void ActivityResultLauncher.launch(Object)' on a null object reference
```

### Exercise 8.7

**Requirement:** add `fabInsert.performClick();` right after `initListeners();`. Run it. What happens?

<details>
<summary>Solution — explained</summary>

**What was done:** we forced a programmatic click before `launcher` was initialized.

**What happens:** **a crash** with an NPE:

```
java.lang.NullPointerException: Attempt to invoke virtual method
'void androidx.activity.result.ActivityResultLauncher.launch(java.lang.Object)'
on a null object reference
    at ro.ase.ie.g1097.activities.MainActivity$1.onClick(MainActivity.java:...)
```

**Why:** `performClick()` runs the listener **immediately**. At that moment, `launcher` is still `null` (the initialization line hasn't executed).

**Remember:**
1. **Initialization order** matters when code runs **immediately**.
2. It **doesn't matter** when code runs **later** (on click, on a callback).
3. The safest approach: initialize `launcher` **before** `initListeners()`. The repo doesn't, but it works by accident.

**Recommendation:** move `launcher = registerForActivityResult(...)` **before** `initListeners()`. It's a safe improvement.

</details>

---

## Step 8.8 — Full verification

### How

1. Run it.
2. You see 3 movies in the list.
3. Press the FAB → the empty form opens.
4. Fill in: title "Dune", genre "Sci-Fi", date 22/10/2021, budget 165000000, duration 155, rating 4, switch ON, watchlist OFF, guidance "PG-13", empty poster.
5. Press Save.
6. **Check:** the list now has 4 movies, the last one is Dune.

### What to check

- [ ] the FAB opens the form
- [ ] Save adds the movie to the list
- [ ] Back (without Save) adds **nothing**
- [ ] `notifyDataSetChanged()` is called (the movie appears immediately)
- [ ] `resultCode` is checked before `getData()`

---

## Step 8.9 — Test questions

1. Why `launcher.launch()` and not `startActivity()`?
2. What does `ActivityResult` contain?
3. Why `MainActivity.this` in the anonymous class but `this` in the lambda?
4. What happens if you forget `setResult(RESULT_OK, intent)` in `saveMovie`?
5. Why `notifyDataSetChanged()` after `movies.add()`?

<details>
<summary>Answers — explained</summary>

**1. Why `launcher.launch()`?**
`startActivity()` starts the activity without waiting for a result. `launcher.launch()` starts the activity **and** registers the callback that will be invoked on close.

**2. What does `ActivityResult` contain?**
`getResultCode()` (`RESULT_OK` / `RESULT_CANCELED`) and `getData()` (the `Intent` with extras, can be `null`).

**3. `MainActivity.this` vs `this`?**
In the anonymous class, `this` = the anonymous class instance (which isn't a `Context`). In the lambda, `this` = the outer class instance (`MainActivity`, which is a `Context`).

**4. What happens if you forget `setResult`?**
`ItemActivity` closes with `RESULT_CANCELED` (the default). `MainActivity` sees `resultCode != RESULT_OK` and does **nothing**. The movie is lost with no error at all.

**5. Why `notifyDataSetChanged()`?**
`ArrayAdapter` doesn't observe changes to the list. Without a notification, the `ListView` keeps the old views.

</details>

---

## Chapter 08 summary

- `registerForActivityResult` + `launcher.launch()` = two-way communication.
- `ActivityResult` contains `resultCode` + `data`; you always check `resultCode`.
- `static final` constants for the `Intent` keys.
- `MainActivity.this` in anonymous classes, `this` in lambdas.
- `notifyDataSetChanged()` mandatory after changing the list.

**Next chapter:** [09 - Edit mode.md](09%20-%20Edit%20mode.md)
