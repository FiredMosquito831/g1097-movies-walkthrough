# Chapter 14 — DMA03: navigation, menus, and dialogs

**Objective:** understand the `DrawerLayout` + `NavigationView` + `MaterialToolbar` structure, menus (`PopupMenu` on a row, toolbar menu), Back button handling, and dialogs with `AlertDialog` / `Snackbar`.

**Estimated time:** 50–65 min.

**Source:** `DMA03/` at commit `d719ffc` — 40 files, first commits `42baa90`, `858f7ea`, `b7633cd` (2026-10-21).

> **Why it matters:** `G1097` has neither menus nor a drawer. But test questions like “how do you make a navigation drawer,” “what's the difference between `PopupMenu` and `NavigationView`,” or “how do you intercept Back” are common. Here you have the complete implementation.

---

## Step 14.1 — Drawer layout structure

### Why

A navigation drawer isn't a widget layered over the content. It's a **container hierarchy** with specific roles.

### How

`activity_main.xml`:

```xml
<androidx.drawerlayout.widget.DrawerLayout
    android:id="@+id/drawerLayout"
    ...>

    <androidx.coordinatorlayout.widget.CoordinatorLayout
        android:id="@+id/main"
        ...>

        <com.google.android.material.appbar.AppBarLayout ...>
            <com.google.android.material.appbar.MaterialToolbar
                android:id="@+id/topAppBar" ... />
        </com.google.android.material.appbar.AppBarLayout>

        <FrameLayout ...>
            <ListView
                android:id="@+id/listView" ... />
        </FrameLayout>

    </androidx.coordinatorlayout.widget.CoordinatorLayout>

    <com.google.android.material.navigation.NavigationView
        android:id="@+id/navigationView" ... />

</androidx.drawerlayout.widget.DrawerLayout>
```

### The hierarchy, level by level

```
DrawerLayout                      ← container that knows about the drawer
├── CoordinatorLayout  (id=main)  ← main content (first child = screen)
│   ├── AppBarLayout
│   │   └── MaterialToolbar       ← top bar with title, hamburger, menu
│   └── FrameLayout
│       └── ListView              ← content
└── NavigationView                ← drawer (second child = drawer)
```

### The `DrawerLayout` rule

> `DrawerLayout` has **at most two** direct children:
> 1. **content** (first child) — any `ViewGroup`;
> 2. **drawer** (second child) — usually `NavigationView`.
>
> The drawer must declare `android:layout_gravity="start"` (or `end`).

If you add a third child, the build won't fail, but the behavior becomes unpredictable.

### Why `CoordinatorLayout` instead of a plain `FrameLayout`

`CoordinatorLayout` is the container that knows how to coordinate `AppBarLayout` with the content: when scrolling, the bar can hide or collapse. If you use `LinearLayout`, the bar stays fixed and you lose the Material behavior.

### Why `FrameLayout` between `CoordinatorLayout` and `ListView`

`CoordinatorLayout` needs a `Behavior` on a child to know how to respond to scrolling. `ListView` doesn't have one by default, but it works when wrapped in a `FrameLayout` with `app:layout_behavior`.

### Exercise 14.1

**Requirement:** what happens if you move `NavigationView` **before** `CoordinatorLayout` in the XML?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you reversed the order of the two `DrawerLayout` children.

**What happens:** `DrawerLayout` treats the **first** child as the content. So `NavigationView` becomes the “screen,” and `CoordinatorLayout` becomes the drawer. Result: you see the menu as the main page, and the list appears when you swipe.

**Why:** `DrawerLayout` doesn't distinguish by type, only by position. First child = content, the others = drawers.

**Remember:**
1. The order in XML **matters** in `DrawerLayout`, just as in `FrameLayout` (chapter 03).
2. `android:layout_gravity="start"` on `NavigationView` specifies where the drawer appears.
3. One content area, one or two drawers (start + end).

**Where it comes back:** in `G1097`, the `FrameLayout` in `activity_main.xml` follows the same ordering rule: `ListView` first, FAB second (chapter 03, step 3.5).

</details>

---

## Step 14.2 — `MaterialToolbar`: hamburger and menu

### Why

`MaterialToolbar` is the top bar. It has three areas: navigation (left), title (center/left), actions (right).

### How — the toolbar menu

`res/menu/top_app_bar.xml`:

```xml
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">

    <item
        android:id="@+id/action_search"
        android:icon="@drawable/ic_search"
        android:title="Search"
        app:showAsAction="ifRoom" />

    <item
        android:id="@+id/action_share"
        android:icon="@drawable/ic_share"
        android:title="Share"
        app:showAsAction="ifRoom" />

    <!-- Items with "never" go into the ⋮ overflow menu -->
    <item
        android:id="@+id/action_settings"
        android:title="Settings"
        app:showAsAction="never" />
</menu>
```

### `app:showAsAction` — the three values

| Value | Effect |
|---|---|
| `ifRoom` | appears as an icon **if there's room**; otherwise goes into `⋮` |
| `never` | **always** goes into `⋮` |
| `always` | always appears as an icon (bad — fills up the bar) |

In DMA03: `search` and `share` are `ifRoom` (icons), `settings` is `never` (in overflow).

### How — wiring it up in code

```java
MaterialToolbar toolbar = findViewById(R.id.topAppBar);

// Hamburger (navigation) icon
toolbar.setNavigationOnClickListener(v -> {
    drawerLayout.openDrawer(GravityCompat.START);
});

// Search, share and overflow menu items
toolbar.setOnMenuItemClickListener(item -> {
    int id = item.getItemId();

    if (id == R.id.action_search) {
        Toast.makeText(this, "Search", Toast.LENGTH_SHORT).show();
        return true;
    } else if (id == R.id.action_share) {
        Toast.makeText(this, "Share", Toast.LENGTH_SHORT).show();
        return true;
    } else if (id == R.id.action_settings) {
        Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
        return true;
    }
    return false;
});
```

### Two different methods for two areas

| Area | Method | What you get |
|---|---|---|
| Navigation icon (left) | `setNavigationOnClickListener` | `View` |
| Actions (right) | `setOnMenuItemClickListener` | `MenuItem` |

> **Remember:** `return true` in `setOnMenuItemClickListener` means “I handled the click.” `return false` lets the event propagate (and closes the menu without an action).

### How the hamburger appears

`MaterialToolbar` displays the hamburger icon automatically if:
1. you've set a `DrawerLayout` as an `ActionBarDrawerToggle`, **or**
2. you've set `app:navigationIcon="@drawable/ic_menu"` in XML.

In DMA03, the icon comes from the theme (`NoActionBar` + custom toolbar). Check `activity_main.xml` for `app:navigationIcon`.

### Exercise 14.2

**Requirement:** change `action_settings` from `showAsAction="never"` to `"ifRoom"`. Run it. What do you see?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you changed how a menu item is displayed.

**What you see:** “Settings” appears as the third icon in the bar — but only if it has `android:icon` and there's room. In DMA03, `action_settings` **doesn't have** `android:icon`, so it appears as the text “Settings” in the bar. If there's no room, it still goes into `⋮`.

**Why:** `showAsAction="ifRoom"` means “show me directly if there's room.” Without an icon, it appears as text — and takes up a lot of space.

**Remember:**
1. `showAsAction` affects only **whether it appears in the bar**, not its functionality. `setOnMenuItemClickListener` receives the click in either case.
2. An item without an icon and with `ifRoom` looks bad. Rule of thumb: use an icon for `ifRoom`, no icon for `never`.
3. `always` is a trap: on small screens, items overlap.

**Where it comes back:** it doesn't, but this is a classic question: “where does a menu item appear?” Answer: it depends on `showAsAction` **and** the available space.

</details>

---

## Step 14.3 — `NavigationView`: the drawer

### Why

`NavigationView` is the Material component for a navigation drawer. It takes an XML menu and displays it as a list of rows with icons.

### How — the drawer menu

`res/menu/drawer_menu.xml` contains the items: `nav_inbox`, `nav_sent`, `nav_trash`, `nav_settings`.

### How — wiring it up

```java
NavigationView navigationView = findViewById(R.id.navigationView);

navigationView.setNavigationItemSelectedListener(item -> {
    int id = item.getItemId();

    if (id == R.id.nav_inbox) {
        toolbar.setTitle("Inbox");
    } else if (id == R.id.nav_sent) {
        toolbar.setTitle("Sent");
    } else if (id == R.id.nav_trash) {
        toolbar.setTitle("Trash");
    } else if (id == R.id.nav_settings) {
        Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
    }

    item.setChecked(true);
    drawerLayout.closeDrawer(GravityCompat.START);
    return true;
});
```

### The two lines that matter

```java
item.setChecked(true);
drawerLayout.closeDrawer(GravityCompat.START);
```

1. **`item.setChecked(true)`** — visually marks the selected item. Without it, the user won't know where they are.
2. **`closeDrawer`** — closes the drawer after selection. Without it, the drawer stays open over the content.

> **Remember:** `setNavigationItemSelectedListener` does **not** close the drawer automatically. You have to do it yourself.

### `GravityCompat.START` vs `Gravity.LEFT`

`START` follows the reading direction: in RTL, `START` = right. `LEFT` is always left — wrong in RTL. Same principle as `layout_gravity="bottom|end"` in chapter 03.

### Exercise 14.3

**Requirement:** remove `drawerLayout.closeDrawer(...)`. Run it and tap an item in the drawer. What happens?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you removed the line that closes the drawer.

**What you see:** the title in the toolbar changes (“Inbox,” “Sent,”…), but **the drawer stays open** over the list. The user has to swipe manually to close it.

**Why:** the selection listener is just a callback. It has no default closing behavior — each app decides (some have submenus and stay open).

**Remember:**
1. `closeDrawer(GravityCompat.START)` closes the drawer on the left. For the right: `GravityCompat.END`.
2. `item.setChecked(true)` is separate — you can do it before closing as well.
3. `return true` says that you handled the selection.

**Where it comes back:** it doesn't.

</details>

---

## Step 14.4 — `PopupMenu`: a menu anchored to a row

### Why

A contextual menu for a list item. It's not the same as the toolbar menu: it appears **next to the tapped row**, not in the bar.

### How

```java
listView = findViewById(R.id.listView);

// Long press shows the popup menu
listView.setOnItemLongClickListener((parent, view, position, id) -> {
    PopupMenu popup = new PopupMenu(this, view);   // anchored to the pressed row
    popup.getMenuInflater().inflate(R.menu.list_item_menu, popup.getMenu());

    popup.setOnMenuItemClickListener(menuItem -> {
        int itemId = menuItem.getItemId();
        String selected = listView.getItemAtPosition(position).toString();

        if (itemId == R.id.action_open) {
            Toast.makeText(this, "Open: " + selected, Toast.LENGTH_SHORT).show();
            return true;
        } else if (itemId == R.id.action_rename) {
            Toast.makeText(this, "Rename: " + selected, Toast.LENGTH_SHORT).show();
            return true;
        } else if (itemId == R.id.action_delete) {
            Toast.makeText(this, "Delete: " + selected, Toast.LENGTH_SHORT).show();
            return true;
        }
        return false;
    });

    popup.show();
    return true;   // true = long press handled
});
```

### The four things to remember

| Line | Why |
|---|---|
| `new PopupMenu(this, view)` | the second argument is the **anchor** — the tapped row. That's why you use `view` from `onItemLongClick` |
| `popup.getMenuInflater().inflate(...)` | the popup starts empty; you fill its menu from an XML file |
| `popup.show()` | without it, nothing appears. `setOnMenuItemClickListener` doesn't display it |
| `return true` | **consumes** the long press so the normal click isn't also triggered |

> **Pitfall:** if you `return false`, the long press isn't consumed and `ListView` may also trigger `OnItemClick` — so the normal action also runs.

### `setOnItemLongClickListener` vs `setOnItemClickListener`

| | Trigger | Typical use |
|---|---|---|
| `setOnItemClickListener` | single tap | open details |
| `setOnItemLongClickListener` | long press | contextual menu, delete |

Both receive `(parent, view, position, id)`.

### Exercise 14.4

**Requirement:** change `return true` to `return false` at the end of `setOnItemLongClickListener`. What happens on a long press?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you changed the returned value.

**What you see:** the popup appears, but after you select an action, the normal click action may also be triggered (if a `setOnItemClickListener` is attached). DMA03 doesn't have one, so the visible effect is small — but the principle is important.

**Why:** `return true` = “I consumed the event.” `return false` = “I didn't consume it; pass it on.”

**Remember:**
1. The rule applies to **all** listeners that return a `boolean`: `onItemLongClick`, `onMenuItemClick`, `onTouch`.
2. `onItemClick` returns `void` — it can't consume anything.
3. If you want a long press to cancel the click, `return true` is required.

**Where it comes back:** in `ItemActivity` (chapter 07), `onDateSet` returns `void` — likewise, it doesn't consume anything. Only `boolean` can consume.

</details>

---

## Step 14.5 — The Back button: `OnBackPressedCallback`

### Why

When the drawer is open and you press Back, the right behavior is to close the drawer, not close the app. Modern Android requires `OnBackPressedCallback` (the `onBackPressed()` method is deprecated).

### How

```java
getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
    @Override
    public void handleOnBackPressed() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START);
        } else {
            setEnabled(false);
            getOnBackPressedDispatcher().onBackPressed();
        }
    }
});
```

### The mechanism, step by step

1. `addCallback(this, callback)` — register a callback tied to the activity's lifecycle.
2. `new OnBackPressedCallback(true)` — `true` = active immediately.
3. In `handleOnBackPressed`:
   - if the drawer is open → close it and **stop**;
   - otherwise → `setEnabled(false)` (disable the callback so you don't call yourself again) and invoke the default behavior.

> **Why `setEnabled(false)` before `onBackPressed()`:** if you leave the callback active and call `onBackPressed()`, you call yourself again → an infinite loop. Disabling it removes it from the chain for that call.

### Exercise 14.5

**Requirement:** remove `setEnabled(false)` from the `else` branch. Run it, open the drawer, close it, then press Back.

<details>
<summary>Answer — explanatory</summary>

**What was done:** you removed the callback's deactivation.

**What happens:** when you press Back with the drawer closed, `handleOnBackPressed` is called, enters the `else` branch, and calls `getOnBackPressedDispatcher().onBackPressed()` — which **calls you again**. Infinite recursion → `StackOverflowError`, or the app freezes.

**Why:** the dispatcher calls active callbacks in order. If yours is active and you call it, you call yourself.

**Remember:**
1. `setEnabled(false)` = removes the callback from the chain.
2. Alternative: `removeCallback` — but then you can't easily reactivate it.
3. `getOnBackPressedDispatcher().onBackPressed()` is the equivalent of the old `super.onBackPressed()`.

**Where it comes back:** it doesn't, but this is a test question: “how do you handle Back when a drawer is open?”

</details>

---

## Step 14.6 — `AlertDialog` and `Snackbar`

### Why

`DMA03` has a second screen (`SecondActivity`) that demonstrates two feedback components: a confirmation dialog and a `Snackbar` with an action.

> **Honest observation:** `SecondActivity` is declared in the manifest but **isn't started from anywhere**. `MainActivity` imports `Intent` but doesn't use it. It's a lab screen, left unconnected. You can open it only temporarily by adding a `startActivity` in `MainActivity`.

### How — `AlertDialog`

```java
public void btnClick(View view) {
    AlertDialog.Builder builder = new AlertDialog.Builder(SecondActivity.this);
    builder.setTitle("Add new control ...")
            .setMessage("Are you sure you want to add a new control?")
            .setCancelable(true)
            .setPositiveButton("Do it!", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    int id = addButton();
                    // Snackbar...
                }
            })
            .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    Toast.makeText(SecondActivity.this, "Object creation cancelled", Toast.LENGTH_LONG).show();
                }
            });
    builder.show();
}
```

### The parts of an `AlertDialog`

| Method | What it does |
|---|---|
| `setTitle` | dialog title |
| `setMessage` | text |
| `setCancelable(true)` | Back and tapping outside close it |
| `setPositiveButton` | button on the right (action) |
| `setNegativeButton` | button on the left (cancel) |
| `show()` | **required** — without it, nothing appears |

You can chain the methods (`builder` returns `builder`) — that's why `.setTitle(...).setMessage(...)` works.

### How — `Snackbar` with an action

```java
Snackbar.make(SecondActivity.this, inflatedLayout, "Cancel previous action.", Snackbar.LENGTH_LONG)
        .setAction("Cancel", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Button viewById = inflatedLayout.findViewById(id);
                inflatedLayout.removeView(viewById);
            }
        }).show();
```

> **Pitfall:** `Snackbar.make(context, view, text, duration)` — the second argument must be a `View` **from** the current view tree. Here it's `inflatedLayout`, not `SecondActivity.this` (which isn't a `View`).

### `Snackbar` vs `Toast`

| | `Toast` | `Snackbar` |
|---|---|---|
| Position | at the bottom, over anything | at the bottom, in the specified container |
| Action button | no | **yes** (`setAction`) |
| Duration | `LENGTH_SHORT` / `LENGTH_LONG` | `LENGTH_SHORT` / `LENGTH_LONG` / `LENGTH_INDEFINITE` |
| Can be dismissed | no | yes (swipe) |
| Requires an anchor `View` | no | **yes** |

> **Remember:** `Snackbar` is preferred when you offer an undo action (“Undo”). `Toast` is still useful for simple confirmations.

### Exercise 14.6

**Requirement:** replace `Toast.makeText(...)` in `setNegativeButton` with a `Snackbar`. What needs to change?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you changed the feedback method.

```java
.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
    @Override
    public void onClick(DialogInterface dialog, int which) {
        Snackbar.make(SecondActivity.this, inflatedLayout,
                "Object creation cancelled", Snackbar.LENGTH_LONG).show();
    }
})
```

**What needs to change:** the second argument to `Snackbar.make` — a `View` from the tree. You already have `inflatedLayout`. `SecondActivity.this` is a `Context`, not a `View`.

**Remember:**
1. `Snackbar.make(Context, View, CharSequence, int)` — the complete signature.
2. Receiver: `Snackbar` is an **abstract** class; `make(...)` returns a concrete instance.
3. Don't forget `.show()`.

**Where it comes back:** it doesn't.

</details>

---

## Step 14.7 — Creating views in code

### Why

`addButton()` creates a `Button` **without XML**. It's the opposite of everything you've done so far — and it's useful to know that it's possible.

### How

```java
int counter = 0;

public int addButton() {
    DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
    int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50,
            displayMetrics);

    Button newBtn = new Button(SecondActivity.this);
    newBtn.setText("Button_" + (++counter));
    newBtn.setId(counter);

    ViewGroup.LayoutParams layoutParams =
            new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT);
    newBtn.setLayoutParams(layoutParams);

    inflatedLayout.addView(newBtn);
    return counter;
}
```

### What happens, step by step

1. `new Button(context)` — creates the widget directly, without inflating it.
2. `setText(...)` — the text.
3. `setId(counter)` — **a unique ID**. Without it, the view can't be found later with `findViewById`.
4. `new ViewGroup.LayoutParams(...)` — the dimensions. Without them, the view appears at `0×0`.
5. `inflatedLayout.addView(newBtn)` — adds it to the existing container.

### Why `setId` is essential

For `removeView`, the code does this:

```java
Button viewById = inflatedLayout.findViewById(id);
inflatedLayout.removeView(viewById);
```

`findViewById(id)` needs an ID. That's why `setId(counter)` stores the ID, and `addButton()` returns it so it can be used by `Snackbar`.

> **Caution:** `setId(counter)` uses values 1, 2, 3… These could conflict with IDs generated from `R.id` (which are large numbers, but not guaranteed to be). It works in practice; `View.generateViewId()` would be the correct approach.

### `DisplayMetrics` and `TypedValue`

```java
DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50, displayMetrics);
```

Converts 50dp to pixels. **But**: `hPixels` isn't used anywhere in the code! The line is just a demonstration — it shows how to convert dp → px.

> **Remember:** in XML, `50dp` is already converted by Android. In code, you have to do the conversion yourself with `TypedValue.applyDimension`.

### Exercise 14.7

**Requirement:** why use `new ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)` instead of `setWidth`/`setHeight` directly on `Button`?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you compared the two approaches.

**The answer:** `View` **doesn't have** `setWidth`/`setHeight`. Dimensions are provided through `LayoutParams`, which the parent reads during measurement.

**Why:** a view doesn't know how much space it has — it only knows what it requests. The parent decides. That's why `LayoutParams` belongs to the child–parent relationship, not to the view.

**Remember:**
1. `ViewGroup.LayoutParams.MATCH_PARENT` = -1, `WRAP_CONTENT` = -2. They are special constants, not pixel values.
2. The correct type of `LayoutParams` depends on the parent: `LinearLayout.LayoutParams` for `LinearLayout`, `FrameLayout.LayoutParams` for `FrameLayout`.
3. For `LinearLayout`, you can also set `weight` through `LinearLayout.LayoutParams`.

**Where it comes back:** in chapter 06, `layout_weight="1"` in XML is exactly `LinearLayout.LayoutParams.weight = 1` in code.

</details>

---

## Step 14.8 — Verification

### How

1. Open `DMA03` in Android Studio.
2. Run it. Check each of the following:
   - the hamburger icon opens the drawer;
   - a drawer item changes the title and closes the drawer;
   - long-pressing a row opens the popup;
   - pressing Back with the drawer open closes it instead of closing the app;
   - Search / Share / Settings in the toolbar show a `Toast`.

### What to check in the code

- [ ] `DrawerLayout` has exactly 2 children: `CoordinatorLayout` + `NavigationView`
- [ ] `NavigationView` has `layout_gravity="start"`
- [ ] `toolbar.setNavigationOnClickListener` opens the drawer
- [ ] `toolbar.setOnMenuItemClickListener` handles the 3 actions
- [ ] `navigationView.setNavigationItemSelectedListener` calls `setChecked(true)` + `closeDrawer`
- [ ] `PopupMenu` is anchored to `view` (the row), not the activity
- [ ] `OnBackPressedCallback` calls `setEnabled(false)` before `onBackPressed()`

---

## Chapter 14 summary

- `DrawerLayout` = 2 children: content (first) + drawer (second), with `layout_gravity="start"`.
- `MaterialToolbar` = `setNavigationOnClickListener` (left) + `setOnMenuItemClickListener` (right).
- `showAsAction`: `ifRoom` / `never` / `always`.
- `NavigationView` doesn't close the drawer by itself — call `closeDrawer` explicitly.
- `PopupMenu` is anchored to the row; use `return true` to consume the long press.
- `OnBackPressedCallback` with `setEnabled(false)` before calling itself again, otherwise recursion.
- `AlertDialog` = `Builder` + `show()`. `Snackbar` = `make(context, view, text, duration)` + optional action.
- Views created in code: `new Button(ctx)`, `setId`, `setLayoutParams`, `addView`.

**Next chapter:** [15 - DMA02 - Application si ciclu de viata.md](15%20-%20DMA02%20-%20Application%20si%20ciclu%20de%20viata.md)
