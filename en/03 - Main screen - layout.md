# Chapter 03 — The main screen: the layout

**Objective:** `activity_main.xml` — a `FrameLayout` with a full-screen `ListView` and a `FloatingActionButton` overlaid bottom-right.

**Estimated time:** 20–30 min.

**Final file:** `cod-final/res/layout/activity_main.xml` (1016 B, SHA-256 `230b1a3bf534d36e…`)

---

## Step 3.1 — What an XML layout is

### Why

An XML layout describes a **tree of views**. Every element is a Java class:

| XML | Java class |
|---|---|
| `<FrameLayout>` | `android.widget.FrameLayout` |
| `<ListView>` | `android.widget.ListView` |
| `<com.google.android.material.floatingactionbutton.FloatingActionButton>` | that exact class |

When you call `setContentView(R.layout.activity_main)`, Android:

1. reads the XML (already compiled to binary),
2. creates the Java objects (`new FrameLayout(context)`, `new ListView(context)`...),
3. links them into a tree (`parent.addView(child)`),
4. measures and draws.

So **XML isn't "configuration"** — it's code that runs at `setContentView`. Every attribute becomes a method call (`android:textSize="20sp"` → `setTextSize(...)`).

### The practical consequence

You can do anything in XML and the equivalent in Java. XML is preferred because it's declarative, it shows in the preview, and it separates "what it looks like" from "what it does".

---

## Step 3.2 — `FrameLayout` as the root

### Why `FrameLayout` and not `LinearLayout` or `ConstraintLayout`

`FrameLayout` stacks its children **on top of each other**, in XML order:

- the first child = the lowest (at the back);
- the last child = the highest (at the front).

That's exactly what you want: the list fills the screen, and the floating button **floats above it**, in the corner.

With `LinearLayout` you'd need a more complicated structure. With `ConstraintLayout` it would work, but it's overkill for 2 children.

### The trap in the repo

```xml
android:orientation="horizontal"
```

`FrameLayout` **doesn't have** an `orientation` attribute. The line is ignored by Android (no error, just a lint warning). It's left over from a `LinearLayout` the layout was transformed from.

> **Why do we keep it?** For fidelity to the repo. But you must **know** it's useless — in the exam, if you're asked to explain, the answer is: "invalid attribute for `FrameLayout`, ignored".

### How

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">
```

### Why the three `xmlns`

| Namespace | For what | Example attribute |
|---|---|---|
| `android:` | attributes from the Android framework | `android:layout_width` |
| `app:` | attributes from libraries (Material, AndroidX) | `app:srcCompat` |
| `tools:` | attributes **for the preview only**, stripped at build | `tools:context` |

`tools:context=".activities.MainActivity"` does nothing at runtime. It tells Android Studio which class to use for the preview (e.g. to suggest `findViewById`).

### Why `android:id="@+id/main"`

`@+id/` means "create the ID if it doesn't exist". The `main` ID is used in code:

```java
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)
```

If it's missing, `findViewById(R.id.main)` returns `null` and the insets aren't applied → the content goes under the status bar.

---

## Step 3.3 — `ListView`

### Why

`ListView` is the classic widget for vertical lists. It receives an `Adapter` that knows how many elements there are and what each one looks like.

### How

```xml
<ListView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:entries="@array/items" />
```

### The attributes, explained

| Attribute | Effect |
|---|---|
| `layout_width="match_parent"` | as wide as the parent (the FrameLayout) |
| `layout_height="match_parent"` | as tall as the parent |
| `android:entries="@array/items"` | **fills the list directly from XML** with the 20 "Item 1..20" rows |

### The `android:entries` trap

`android:entries` is a **shortcut** that automatically creates an `ArrayAdapter<String>` from the given resource. It's useful for a demo, but it **conflicts** with `setAdapter()` in code.

In `MainActivity.initControls()` you have:

```java
listView.setAdapter(movieAdapter);
```

That **replaces** the adapter created by `entries`. So `android:entries` becomes useless at runtime.

> **Why keep it then?** Because in the Android Studio preview you see a populated list instead of an empty rectangle. It's a design-time technique. At runtime, the code wins.

**Remember:** `android:entries` and `setAdapter()` are alternatives. If you have both, the last call wins.

### Exercise 3.3

**Requirement:** remove `android:entries="@array/items"` and check: (a) the Android Studio preview, (b) the app on the emulator. What differs?

<details>
<summary>Hint</summary>

The preview looks at `tools:` and `android:` for design-time. `setAdapter()` runs only on the device.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we removed `android:entries="@array/items"` from the `ListView`.

**What you see:** in the Android Studio preview, the list appears **empty** (a white rectangle). On the emulator, the list appears **populated** with Inception, Toy Story, The Matrix — because `setAdapter(movieAdapter)` in `MainActivity` fills it.

**Why:** `android:entries` is read **only at inflate**, that is, when Android builds the views. `setAdapter()` is called after `setContentView()`, so **after** inflate. The second replaces the first.

**Remember:**
1. The Android Studio preview **doesn't run Java code**. So anything that depends on `setAdapter()`, `notifyDataSetChanged()` etc. doesn't appear in the preview.
2. `android:entries` is a design-time shortcut, not a real solution.
3. For a realistic preview, use `tools:listitem="@layout/movie_item"` (see ch. 11).

**Where it comes back:** in chapter 11, when you move to `RecyclerView`, `android:entries` disappears completely and is replaced by `tools:listitem`, which is **only** for the preview. You'll see exactly the same design-time vs runtime distinction.

</details>

---

## Step 3.4 — `FloatingActionButton`

### Why

A FAB is the round button that floats above the content. In Material Design it's reserved for the screen's **primary action**. Here: "add a movie".

### How

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="bottom|end"
    android:layout_margin="16dp"
    android:contentDescription="Add"
    app:srcCompat="@drawable/outline_add_24" />
```

### The attributes, explained

| Attribute | Why exactly this |
|---|---|
| `layout_width/height="wrap_content"` | the FAB has a fixed internal size (56dp by default); `wrap_content` respects it |
| `android:layout_gravity="bottom|end"` | **the key**: in a `FrameLayout`, `layout_gravity` positions the child. `bottom\|end` = bottom, right (or left in RTL, thanks to `supportsRtl`) |
| `android:layout_margin="16dp"` | distance from the edges, so it doesn't touch them |
| `android:contentDescription="Add"` | text for TalkBack (accessibility). **Mandatory** for images — lint errors out otherwise |
| `app:srcCompat="@drawable/outline_add_24"` | the icon. `srcCompat` (not `android:src`) for vector compatibility |

### Why `app:srcCompat` and not `android:src`

`android:src` on an `ImageView` (and the FAB is a specialised `ImageView`) doesn't support vectors on older Android versions without AppCompat. `app:srcCompat` is the safe variant, processed by AppCompat.

> **Remember:** `app:` = a library attribute. `android:` = a framework attribute. When an attribute doesn't exist in `android:`, you look for it in `app:`.

### Why `bottom|end` and not `bottom|right`

`end` respects the reading direction. In Arabic (RTL), `end` = left. `right` would always be the right, which would look wrong. The app has `android:supportsRtl="true"` in the manifest — so `end` matters.

### Exercise 3.4

**Requirement:** move the FAB to the **top-left** corner and increase the margin to 32dp. Check it on the emulator.

<details>
<summary>Hint</summary>

`layout_gravity` accepts combinations: `top|start`, `bottom|end`, `center`, etc.

</details>

<details>
<summary>Solution — explained</summary>

**What was done:** we changed `layout_gravity` from `bottom|end` to `top|start` and `layout_margin` from `16dp` to `32dp`.

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="top|start"
    android:layout_margin="32dp"
    android:contentDescription="Add"
    app:srcCompat="@drawable/outline_add_24" />
```

**What you see:** the button jumps to the top-left corner, further from the edges.

**Why it works:** in a `FrameLayout`, `layout_gravity` is the attribute that controls a child's position inside its parent. Without it, the child is placed at `top|start` by default.

**Remember:**
1. `layout_gravity` = the position of the **child in the parent**.
2. `gravity` (without `layout_`) = the position of the **content in the child** (e.g. the text in a `TextView`).
3. Confusing the two is a classic exam mistake.

**Where it comes back:** in `activity_item.xml` (ch. 05–06) you'll see `android:gravity="center_vertical"` on `LinearLayout`s — that centres the **children** vertically. And you'll see `android:layout_gravity="center_horizontal"` on the `RatingBar` — that centres the bar in its parent. Same word, two meanings.

</details>

---

## Step 3.5 — The order of children in `FrameLayout`

### Why

In a `FrameLayout`, **the XML order = the stacking order**. The first child is at the bottom, the last is on top.

In `activity_main.xml`, the `ListView` is first and the FAB is second. So the FAB is **above** the list.

### What would happen the other way round

If you put the FAB first, the list would be drawn over it. The button would be invisible (or partly, if the list had a transparent background — but `ListView` has an opaque background).

### Exercise 3.5

**Requirement:** reverse the order of the two children. Run it. What do you notice? Then put them back.

<details>
<summary>Solution — explained</summary>

**What was done:** we moved the `<FloatingActionButton .../>` block **before** the `<ListView .../>` block.

**What you see:** the FAB **disappears** from the screen. The list covers it completely.

**Why:** `FrameLayout` draws its children in XML order. The first drawn is the first "glued" to the background; each subsequent one is drawn on top. If the list (opaque, `match_parent`) is drawn after the FAB, it covers it.

**Remember:**
1. **The XML order matters** in a `FrameLayout` (and in a `RelativeLayout`, but there explicit rules can also be used).
2. In a `LinearLayout` the order is horizontal/vertical, not by depth.
3. If you want an element "on top" in a `FrameLayout`, you put it **last**.

**Where it comes back:** in `movie_item.xml` (ch. 11), the `MaterialCardView` contains a horizontal `LinearLayout` with an `ImageView` + a text column. There the order is left-to-right, because it's a `LinearLayout`, not a `FrameLayout`. You'll see the difference immediately.

</details>

---

## Step 3.6 — Visual verification

### Why

A layout that compiles can look completely wrong. You check **visually**, not just with `BUILD SUCCESSFUL`.

### How

1. Open `activity_main.xml` → the **Design** tab (top right).
2. Check:
   - The list fills the whole screen.
   - The FAB is in the bottom-right corner, 16dp from the edges.
   - The list shows "Item 1" … "Item 20" (from `entries`).
3. Run it on the emulator: the list shows **movies** (Inception, Toy Story, The Matrix) — because `setAdapter` replaced the adapter from XML.

### The design vs runtime difference

| | Preview | Emulator |
|---|---|---|
| Source of the list | `android:entries` | `setAdapter(movieAdapter)` |
| What you see | Item 1..20 | Inception, Toy Story, The Matrix |
| Text per row | `Item N` | `Movie{title='...', ...}` (because of `toString()`) |

That's the proof that `setAdapter` wins.

---

## Step 3.7 — Synthesis exercise

**Requirement:** without looking at the solution, write `activity_main.xml` from memory. Then compare it with `cod-final/res/layout/activity_main.xml`.

### What to check

- [ ] `FrameLayout` root with `android:id="@+id/main"`
- [ ] the three `xmlns` (`android`, `app`, `tools`)
- [ ] `tools:context=".activities.MainActivity"`
- [ ] `ListView` with `android:id="@+id/listView"`, `match_parent`/`match_parent`, `entries`
- [ ] `FloatingActionButton` with `android:id="@+id/floatingActionButton"`, `layout_gravity="bottom|end"`, `layout_margin="16dp"`, `contentDescription`, `app:srcCompat`
- [ ] **the order**: `ListView` first, FAB second

### Test questions

1. Why `FrameLayout` and not `LinearLayout`?
2. What does `android:orientation="horizontal"` do on a `FrameLayout`?
3. Why `app:srcCompat` and not `android:src`?
4. What happens if you put the FAB before the list?
5. What's the difference between `android:gravity` and `android:layout_gravity`?

<details>
<summary>Answers — explained</summary>

**1. Why `FrameLayout` and not `LinearLayout`?**
`FrameLayout` stacks its children on top of each other — exactly what's needed for a button that "floats" over the list. `LinearLayout` would put them **next to each other** (horizontal) or **one below the other** (vertical), so the list and the button would share the screen instead of overlapping.

**2. What does `android:orientation="horizontal"` do on a `FrameLayout`?**
**Nothing.** `FrameLayout` doesn't have an `orientation` attribute. Android ignores unknown attributes at inflate (it doesn't throw), but lint gives a warning. The line is left over from a previous `LinearLayout`.

**3. Why `app:srcCompat` and not `android:src`?**
`app:srcCompat` is processed by AppCompat and knows how to load a `VectorDrawable` on any Android version. `android:src` on a normal `ImageView` doesn't natively support vectors on API < 21 (here `minSdk=33`, so technically it would work, but the convention stays `srcCompat` for portability).

**4. What happens if you put the FAB before the list?**
The list, being `match_parent` and opaque, is drawn **over** the FAB. The button becomes invisible and untouchable.

**5. `android:gravity` vs `android:layout_gravity`?**
- `gravity` = how the **own content** is aligned (the text in a `TextView`, the children in a `LinearLayout`).
- `layout_gravity` = how **the element itself** is aligned in its parent.

Example: a `TextView` with `android:gravity="center"` → the text centres inside the `TextView`. A `TextView` with `android:layout_gravity="center"` → the `TextView` centres in its parent.

</details>

---

## Chapter 03 summary

- `FrameLayout` = stacking; the XML order = the drawing order.
- `ListView` fills everything; `android:entries` is only for the preview, `setAdapter` wins at runtime.
- FAB positioned with `layout_gravity="bottom|end"`, icon with `app:srcCompat`.
- `android:orientation` on a `FrameLayout` is useless (leftover).
- `android:id="@+id/main"` is used by the insets in code.

**Next chapter:** [04 - MainActivity - the list.md](04%20-%20MainActivity%20-%20the%20list.md)
