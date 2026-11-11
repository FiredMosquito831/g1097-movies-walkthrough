# Chapter 26 — The DMA03 code, annotated

**Objective:** to read the `DMA03` project block by block — every line explained: what it does, why it is there, what breaks if you remove it. By the end you should be able to rebuild from memory a drawer with a toolbar, a per-row context menu, and a dialog that creates controls.

**Estimated time:** 60–90 min (active reading).

**Source:** `DMA03/` at commit `d719ffc` — 8 files: two activities, the manifest, two layouts and three menus.

**What you learn from it:** `DrawerLayout`, `NavigationView`, `MaterialToolbar`, `PopupMenu`, `OnBackPressedCallback`, `AlertDialog`, `Snackbar`, views created from code.

> **How to read:** do not read passively. For every block, cover the explanation and try to say what it does yourself. If you cannot, you have found what needs repeating.
>
> **About the comments:** the files already contain a few comments written by the author (`// Long press shows the popup menu`, `// anchored to the pressed row`). I kept them. The comments added for this chapter look the same — still with `//` — but they are longer and explain **why**, not **what**. The code itself is untouched.

---

## 26.1 `MainActivity.java` — drawer, toolbar, menus

A single `onCreate`, seven responsibilities. The file has no helper methods — everything is inline. It is the densest file in the project and, in a test, the one most likely to ask you for a change.

### The imports — and one dead import

```java
package ro.ase.ie.dma03;

import android.content.Intent;          // ← IMPORTED BUT UNUSED. There is no Intent anywhere in the whole file.
import android.os.Bundle;               // the state saved on recreation (not used here)
import android.widget.ListView;         // the list of 20 rows
import android.widget.PopupMenu;        // the menu anchored on the row (long press)
import android.widget.Toast;            // the short message, with no action
```

**`import android.content.Intent` with no use at all** is not a style slip — it is the proof that `SecondActivity` is not started anywhere. An `Intent` would be the only way to open the second screen, and across the whole project it appears exactly once: on this line. The detail comes back in 26.2 and 26.3.

**Why `android.widget.*` and not `androidx.appcompat.widget.AppCompatListView`:** `ListView` has no AppCompat variant. `PopupMenu` does (`androidx.appcompat.widget.PopupMenu`), but the platform one is used here — it works, it just does not inherit the Material styling.

```java
import androidx.activity.EdgeToEdge;              // drawing under the system bars
import androidx.activity.OnBackPressedCallback;   // the modern Back button
import androidx.appcompat.app.AppCompatActivity;  // the base activity
import androidx.core.graphics.Insets;             // the rectangles of the system bars
import androidx.core.view.GravityCompat;          // START/END, safe for RTL
import androidx.core.view.ViewCompat;             // the insets listener
import androidx.core.view.WindowInsetsCompat;     // the inset types
import androidx.drawerlayout.widget.DrawerLayout; // the container with the drawer
```

**`GravityCompat` and not `Gravity`:** `Gravity.LEFT` is "physical left". `GravityCompat.START` is "the start of the reading direction" — left in Romanian, right in Arabic. It appears four times in the file: `closeDrawer` twice, `isDrawerOpen` and `openDrawer`. All of them must be the same direction as `layout_gravity` in the XML. Mixing `START`/`LEFT` produces a drawer that opens from one side and does not close from the same side.

**`androidx.drawerlayout` does not appear in `build.gradle.kts`.** It comes in transitively, through `libs.material`. If you ever remove Material from the dependencies, `DrawerLayout` disappears with it — even though it looks like a core component.

```java
import com.google.android.material.appbar.MaterialToolbar;   // the top bar, the Material 3 version
import com.google.android.material.navigation.NavigationView; // the drawer's content
```

**`MaterialToolbar` and not `androidx.appcompat.widget.Toolbar`:** the same base class, but with Material 3 styling applied automatically — height, typography, ripple. Both would work; `MaterialToolbar` needs less configuration to look right.

### The fields

```java
public class MainActivity extends AppCompatActivity {

    private DrawerLayout drawerLayout;   // used in 3 places: drawer listener, Back, hamburger
    private ListView listView;           // used in the long press listener
```

**Why fields and not local variables:** both are read from inside lambda listeners, which run **after** `onCreate` has finished. A local variable would be captured in the closure (a lambda only captures effectively final variables), but a field is clearer and lives as long as the activity does.

**`private`** — nothing outside needs them. `drawerLayout` could have been local too (all three uses are inside `onCreate`); it is a field out of habit, so it is at hand if you add new methods.

### The start of `onCreate` — the order is mandatory

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);       // 1. starts the parent's lifecycle
        EdgeToEdge.enable(this);                  // 2. allows drawing under the status bar and under the navigation bar
        setContentView(R.layout.activity_main);   // 3. inflates the XML and builds the view tree
```

**The order is not negotiable.** `findViewById` called before `setContentView` returns `null` — it does not throw, it just gives you a `NullPointerException` later, on a line with no apparent connection.

**`EdgeToEdge.enable(this)`** makes the window take up the whole screen, including the areas under the clock and under the gesture bar. Without it, the app would have opaque system bars and you would not need the next block. With it, you **do** need it — otherwise the first row of the list goes under the clock.

### Insets — padding on the root

```java
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
```

**What it does:** when the system works out how much the bars occupy, it applies padding equal to them on the view with `id=main`. The content moves into the safe area, the background stays stretched across the whole screen.

**`R.id.main` is on the `CoordinatorLayout`, not on the `DrawerLayout`.** That matters: the padding is applied to the **content panel**, not to the drawer. `NavigationView` applies its own insets (it extends `ScrimInsetsFrameLayout`), so it needs no help. If you had put `id=main` on the `DrawerLayout`, you would have added padding on top of the drawer's padding.

**`return insets`** — not `WindowInsetsCompat.CONSUMED`. The insets travel on, to the children. If you consumed them, `AppBarLayout` would no longer know about them and `liftOnScroll` would receive wrong values.

**Why on the root and not on each child:** padding on the parent pushes **all** the children at once. Applied to each child separately, you would repeat the code and miss any view added later.

### The list and the context menu

```java
        listView = findViewById(R.id.listView);

        // Long press shows the popup menu
        listView.setOnItemLongClickListener((parent, view, position, id) -> {
```

**A four-parameter lambda** for `AdapterView.OnItemLongClickListener`:

| Parameter | What it is |
|---|---|
| `parent` | the `ListView` itself (not used here) |
| `view` | the **row** that was pressed — it becomes the menu's anchor |
| `position` | the row's index in the list |
| `id` | the item's id; for an `ArrayAdapter` it equals `position` |

**There is no `setOnItemClickListener` anywhere in the file.** A simple tap on a row does nothing. Only the long press reacts. It is a teaching choice: the project demonstrates the context menu, not navigation.

```java
            PopupMenu popup = new PopupMenu(this, view);   // anchored to the pressed row
            popup.getMenuInflater().inflate(R.menu.list_item_menu, popup.getMenu());
```

**`new PopupMenu(context, anchorView)`** — the second argument is the anchor. The menu appears stuck to the pressed row, not in the corner of the screen. If you passed `listView` instead of `view`, it would appear next to the list, that is, nowhere useful.

**`getMenuInflater()`** comes from the `Context` (the activity). **`inflate(resource, menu)`** — the second argument is the **destination** `Menu`, obtained with `popup.getMenu()`. It is not like `setContentView`, where you only pass the resource.

**Why `R.menu.list_item_menu` and not `R.menu.top_app_bar`:** they are two different menus, for two different contexts. `list_item_menu` has "Open / Rename / Delete" — actions on a row. `top_app_bar` has "Search / Share / Settings" — actions on the screen.

```java
            popup.setOnMenuItemClickListener(menuItem -> {
                int itemId = menuItem.getItemId();
                String selected = listView.getItemAtPosition(position).toString();
```

**`position` is captured from the outer lambda.** It is a method parameter, hence effectively final — Java allows the capture. If you tried to modify it in between (`position++`), the compiler would refuse.

**`getItemAtPosition(position)` returns a `CharSequence`** — the text from `@array/items`, because `ListView` built itself an `ArrayAdapter` from the `android:entries` attribute in the XML. You wrote no adapter in the code.

**`.toString()` is redundant** for a `String`, but harmless. It becomes necessary the moment you put objects in the list: there `toString()` is the display contract.

```java
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
```

**`return true` = "I handled the click".** The menu closes and the event stops travelling. **`return false`** = "not my concern" — the system tries the default handler.

**The three branches are identical apart from the text.** In an exercise, this is where something changes: `action_delete` would remove the item from the list, `action_rename` would open a dialog. The structure is ready for that — only the `Toast` needs replacing.

**`Toast.makeText(...).show()`** — two calls. `makeText` **builds**, `show()` **displays**. Without `.show()`, nothing happens, with no error. It is the most common mistake at the start.

```java
            popup.show();
            return true;   // true = long press handled, so the normal click doesn't also fire
        });
```

**`popup.show()`** — up to here you have only configured the menu. Only now does it appear on screen.

**`return true` from the long press listener** — tells the list "the long press was handled". If you returned `false`, the system would consider the long press unhandled and might also fire a normal click after it. The result: the menu appears and, at the same time, the click action runs.

**The order matters:** `popup.show()` **before** `return true`. The reverse is not possible — `return` ends the lambda.

### Binding the three components

```java
        drawerLayout = findViewById(R.id.drawerLayout);
        MaterialToolbar toolbar = findViewById(R.id.topAppBar);
        NavigationView navigationView = findViewById(R.id.navigationView);
```

**Three `findViewById` calls for three views from the XML.** All three ids must exist in `activity_main.xml`, otherwise you get `null` and a `NullPointerException` on the first call.

**`toolbar` and `navigationView` are local, `drawerLayout` is a field.** A real inconsistency in the code: all three are used only inside `onCreate`. It works with all three local; it works with all three as fields. Pick one variant and stick to it.

### The drawer listener

```java
        // Drawer item clicks
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
```

**What each branch does:** it changes the **title** of the top bar. The list content stays the same — the 20 "Item N" rows. The app is a navigation demo, not a data one.

**`toolbar.setTitle("Inbox")`** overrides `app:title="Inbox"` from the XML. The XML value is only the initial one; after the first click, the title comes from the code.

**`nav_settings` is handled differently** — a `Toast`, not a title. It is the only item in the "Other" submenu, so it makes no sense for it to change the screen title.

```java
            item.setChecked(true);
            drawerLayout.closeDrawer(GravityCompat.START);
            return true;
        });
```

**`item.setChecked(true)`** — the menu has `android:checkableBehavior="single"` (see 26.6), so it behaves like a radio button group: a single checked item. The explicit call guarantees the state after the drawer closes and after it is reopened.

**`closeDrawer(GravityCompat.START)`** — closes the drawer from the `start` side. It must match `android:layout_gravity="start"` in the XML. If it is `start` in the XML and `end` in the code, the drawer stays open.

**`return true`** — tells `NavigationView` that the click was handled. If you return `false`, the item is not marked visually as selected.

**Without `closeDrawer`, the drawer stays over the screen** after you pick an option. It is the first thing missing from a rushed implementation.

### The Back button — `OnBackPressedCallback`

```java
        // Back button closes the drawer first if it's open
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

**Why not `@Override public void onBackPressed()`:** the method was marked deprecated from API 33, and `OnBackPressedDispatcher` is the official mechanism. On top of that, the dispatcher allows **several** callbacks in a chain, each with its own priority — a single override cannot do that.

**`new OnBackPressedCallback(true)`** — the argument is the initial state: `true` = active. A disabled callback receives no events.

**`addCallback(this, ...)`** — the first argument is the `LifecycleOwner` (the activity). The dispatcher keeps the callback only while the activity is in `STARTED`. At `onStop`, the callback is removed automatically; at `onStart`, it comes back. You do not have to remove it manually.

**The logic, step by step:**

1. Back was pressed.
2. Is the drawer open? → close it. Done. The user stays on the screen.
3. Is the drawer closed? → `setEnabled(false)`, then re-send the event.

**Why `setEnabled(false)` before re-sending:** without it, `onBackPressed()` would enter the **same** callback again, which would see the drawer closed and re-send the event — infinite recursion, `StackOverflowError`. By disabling yourself, you let the next handler in the chain (the default one, which closes the activity) receive the event.

**`GravityCompat.START` three times** — `isDrawerOpen`, `closeDrawer`, and in the listener below. All three must be identical to `layout_gravity` in the XML.

### The hamburger

```java
        // Hamburger (navigation) icon
        toolbar.setNavigationOnClickListener(v -> {
            drawerLayout.openDrawer(GravityCompat.START);
        });
```

**What it does:** the icon on the left of the bar (the three lines) opens the drawer.

**The icon already exists in the XML** — `app:navigationIcon="@drawable/ic_menu"`. Without a listener it is purely decorative: it is visible, it can be pressed, nothing happens. The listener is what turns it into a button.

**Why not `ActionBarDrawerToggle`:** the classic variant links the icon, the drawer and accessibility automatically, but it requires the toolbar to be set as the `ActionBar` (`setSupportActionBar`). Here the toolbar is used as an ordinary view, so the link is made by hand. Less code, but also less automation — for example, the icon does not animate into an arrow when the drawer is open.

### The toolbar menu

```java
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
                // open settings
                Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
                return true;
            }
            return false;
        });
```

**The menu is already inflated** — `app:menu="@menu/top_app_bar"` in the XML. Here you only react to the click. If you had used `setSupportActionBar(toolbar)`, you would have overridden `onCreateOptionsMenu` and `onOptionsItemSelected`; with the toolbar as a plain view, this is the correct hook.

**`action_settings` has `app:showAsAction="never"`** — that is why it ends up in the "⋮" menu (overflow), not on the bar. `action_search` and `action_share` have `ifRoom` — they appear directly on the bar if they fit.

**The `// open settings` comment marks an empty spot.** The branch shows a `Toast`, but the intention was to open a settings screen. It is a TODO in disguise.

**The final `return false` is dead code** — all three ids are covered above. It stays correct: if you add a fourth item to the menu and forget to handle it, the click falls neatly into the default handler instead of throwing an exception.

---

## 26.2 `SecondActivity.java` — dialog and Snackbar

**Warning before anything else:** `SecondActivity` is declared in the manifest, but it is **not started anywhere**. There is no `Intent` in `MainActivity` — only the unused import. The screen is fully functional if you launch it manually (Run → Edit Configurations → Launch: Specified Activity), but in the shipped app it is unreachable. It is a lab screen left unconnected, not a compile bug.

### The imports

```java
package ro.ase.ie.dma03;

import android.app.AlertDialog;          // ← WATCH OUT: the PLATFORM version, not androidx.appcompat.app.AlertDialog
import android.content.DialogInterface;  // the interface for the dialog's buttons
import android.os.Bundle;
import android.util.DisplayMetrics;      // the screen density (for the dp→px conversion)
import android.util.TypedValue;          // applyDimension: dp → pixels
import android.view.View;                // the type of the parameter in btnClick
import android.view.ViewGroup;           // the base class for LayoutParams
import android.widget.Button;
import android.widget.LinearLayout;      // the container you add buttons to
import android.widget.Toast;
```

**`android.app.AlertDialog` vs `androidx.appcompat.app.AlertDialog`** — the difference is visible on screen. The platform variant uses the system's dialog theme; the AppCompat variant uses the app's theme. With `Theme.Material3.DayNight`, the dialog in this file will look like a system dialog, not a Material 3 one. Functionally identical; visually inconsistent.

**`DialogInterface`** is imported separately because the dialog's `OnClickListener` is an interface nested inside it: `DialogInterface.OnClickListener`.

```java
import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;   // the bottom bar with an action
```

**`Snackbar` comes from Material**, not from the platform. That is why `SecondActivity` needs `libs.material` in the dependencies — just like `MainActivity` does for the toolbar.

### The field and `onCreate`

```java
public class SecondActivity extends AppCompatActivity {

    LinearLayout inflatedLayout;   // no modifier = package-private; it is the root of activity_second.xml
```

**No `private`** — an inconsistency compared with `MainActivity`, where the fields are `private`. It breaks nothing (we are in the same package), but the convention is `private`.

**Why a field and not a local:** it is used in `btnClick`, in the Snackbar's action and in `addButton`. Three methods, one field.

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_second);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        inflatedLayout = findViewById(R.id.main);
    }
```

**The insets block is identical to the one in `MainActivity`** — copied. Here `R.id.main` is on the root `LinearLayout`, not on a `CoordinatorLayout`. It works the same way: padding on the root, the children move into the safe area.

**`inflatedLayout = findViewById(R.id.main)` is the last line** — after `setContentView`. If it came before, it would get `null` and the first `addView` would throw a `NullPointerException`.

**The name `inflatedLayout` is misleading:** it is not a layout "inflated" at runtime, it is the layout from the XML. The inflating was done by `setContentView`. The name suggests the intention — a container you add views to — not the mechanism.

### `btnClick` — the contract with `android:onClick`

```java
    public void btnClick(View view) {
```

**The signature is imposed by the XML.** In `activity_second.xml`, the button has `android:onClick="btnClick"`. At runtime, Android looks up, through reflection, a method `public void btnClick(View)` in the activity's context.

**The consequence:** if you make it `private`, or change its parameter to `Object`, or rename it without changing the XML, **the build passes**. The error appears on click: `IllegalStateException: Could not find method btnClick(View) in a parent or ancestor Context`. One of the few places in Android where the mistake is not visible at build time.

**`view` is the pressed button.** It is not used here — the code does not need to know which button it was.

### The dialog

```java
        AlertDialog.Builder builder = new AlertDialog.Builder(SecondActivity.this);
        builder.setTitle("Add new control ...")
                .setMessage("Are you sure you want to add a new control?")
                .setCancelable(true)
```

**`AlertDialog.Builder`** — builds the dialog piece by piece. Every setter returns the **same** builder, which is why they can be chained. The chain ends with `setNegativeButton`, and `builder.show()` at the end of the method displays the dialog.

**`SecondActivity.this` and not `this`:** inside a listener, `this` would mean the listener. `SecondActivity.this` is the syntax for the outer class instance. Here we are still in the method body, so `this` would have worked — but the explicit form is a good habit, because in two steps you will be inside `onClick`.

**`setCancelable(true)` is the default value.** Written explicitly, it documents the behaviour: it can be closed with Back or with a tap outside. The consequence: if the user closes it that way, **no** button runs — neither "Do it!" nor "Cancel". If you need a guaranteed action, you need `setOnCancelListener`.

```java
                .setPositiveButton("Do it!", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        int id = addButton();
```

**The positive button** is the main action — it appears on the right, coloured. The text "Do it!" is explicit; "OK" would be vague.

**`int id = addButton();`** — creates the button **before** the Snackbar, so you have something to delete. The returned id is the only link to the new button: you have no reference to the object, only a number.

**`which`** is `DialogInterface.BUTTON_POSITIVE` here. It is not used — each button has its own listener.

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

**`Snackbar.make(context, view, text, duration)`** — four arguments:

| Argument | Role |
|---|---|
| `SecondActivity.this` | the context, for the theme and resources |
| `inflatedLayout` | the reference view; the Snackbar looks for a suitable parent and appears at the bottom |
| `"Cancel previous action."` | the text |
| `Snackbar.LENGTH_LONG` | ~10 seconds (`LENGTH_SHORT` = ~4 s) |

**`inflatedLayout` is a plain `LinearLayout`, not a `CoordinatorLayout`.** The Snackbar works, but without the CoordinatorLayout benefits: it cannot be swiped away and it does not automatically push a FAB up. For a demo screen that is enough.

**`setAction("Cancel", listener)`** — adds the button on the right. The text is short on purpose: an "Undo last action" would crowd the message on small screens.

**`id` is captured from the outer lambda.** It is a local `int` variable, assigned only once → effectively final → it can be captured. If you wrote `id++` between the declaration and the use, the compiler would refuse the capture.

**`inflatedLayout.findViewById(id)`** — works because the button was given an explicit id with `setId(counter)`. Without `setId`, `findViewById` would return `null` and `removeView(null)` would throw a `NullPointerException`.

**`removeView(viewById)`** — takes the view out of the container. The button disappears from the screen; the object stays in memory until the next garbage collection.

**`.show()` at the end** — without it, the Snackbar is built and never displayed. The same trap as with `Toast`.

**When it is displayed:** the Snackbar is created **inside** the positive button's `onClick`, so it appears after the dialog has closed. If you created it before `builder.show()`, it would appear under the dialog.

```java
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        Toast.makeText(SecondActivity.this, "Object creation cancelled", Toast.LENGTH_LONG).show();
                    }
                });
        builder.show();
```

**The negative button** — cancel. Just a `Toast`, no state change.

**`builder.show()`** — creates the dialog and displays it. Equivalent to `builder.create().show()`. It is called **once**, after the chain of setters has ended.

**Why `show()` is separate and not in the chain:** because the chain ends with `;` after `setNegativeButton`, and `show()` is a method of the builder, not a setter. `builder.setTitle(...).show()` would also have worked, but the code chooses the explicit form.

### `addButton` — creating a view from code

```java
    int counter = 0;
    public int addButton()
    {
```

**The `counter` field is declared between methods** — legal in Java, unusual as style. It has two roles at once: id generator and source for the label.

**`public int addButton()`** — public because it is called from `onClick`, but also because it could be called from XML. It returns the id, so the caller can find the button later.

**Brace on the next line** — a style different from the rest of the file (K&R). Cosmetic, no effect.

```java
        DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
        int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50,
                displayMetrics);
```

**Dead code.** `hPixels` is computed and **never used**. The intention was probably `newBtn.setHeight(hPixels)` or a `LayoutParams` with a height of 50dp. The compiler gives a warning (`variable hPixels is never used`), not an error.

**What it does anyway, useful to know:** `TypedValue.applyDimension(COMPLEX_UNIT_DIP, 50, metrics)` converts 50dp into physical pixels, using the screen density. At 3x, it returns 150. It is the correct conversion when you need pixels in a calculation — for animations or for `setPadding`, for example.

**Why not `50 * getResources().getDisplayMetrics().density`:** it is equivalent, but `applyDimension` also handles `SP`, `PT`, `MM`, `IN` with the same signature. One function, all the units.

```java
        Button newBtn = new Button(SecondActivity.this);
        newBtn.setText("Button_" + (++counter));
        newBtn.setId(counter);
```

**`new Button(Context)`** — the constructor needs a **themed context**. `SecondActivity.this` has the `Theme.DMA03` theme. If you passed `getApplicationContext()`, the button would lose the theme and, on some Material attributes, would throw an exception at inflate.

**`++counter` (pre-increment)** — increments first, then uses. The first button is `Button_1`, and `counter` becomes 1. With `counter++` (post-increment), the first would be `Button_0` and you would have a button with id 0.

**`setId(counter)`** — ids 1, 2, 3... Resource ids live in the `0x7f......` range, so they do not collide. `View.NO_ID` is `-1`, so 0 would have been an unfortunate value — one more reason for the pre-increment.

**Without `setId`, the button exists but is impossible to find** with `findViewById`. It would appear on screen and you could no longer delete it.

```java
        ViewGroup.LayoutParams layoutParams =
                new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT);
        newBtn.setLayoutParams(layoutParams);
```

**`ViewGroup.LayoutParams`** — the base class. `LinearLayout` accepts it. If you need `layout_weight`, you need `LinearLayout.LayoutParams` — the base class has no such field.

**`MATCH_PARENT` on the width** — the button fills the container, like the original button in the XML. **`WRAP_CONTENT` on the height** — as much as the text needs.

**Without `setLayoutParams`**, `addView` applies the container's default values — also `MATCH_PARENT`/`WRAP_CONTENT` for a `LinearLayout`, so practically the same result. Explicit is safer when the container changes.

```java
        inflatedLayout.addView(newBtn);
        return counter;
    }
}
```

**`addView`** — adds at the end of the vertical `LinearLayout`, so below the existing button. The second button appears under the first, the third under the second.

**`return counter`** — the id just assigned. The caller keeps it in `id` and uses it in the Snackbar's action.

**What happens on rotation:** `counter` resets to 0, and the added buttons disappear — they are not saved in `savedInstanceState`. On rotation the activity is recreated, `onCreate` runs again, and `activity_second.xml` has a single button again.

---

## 26.3 `AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
```

**`xmlns:tools` is declared but unused** — no `tools:*` attribute in the file. Leftover from the template. It breaks nothing, but lint flags it.

**No `<uses-permission>`** — the app needs nothing. Not internet, not storage. All the data is in memory.

```xml
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA03">
```

**`allowBackup="true"`** — the app takes part in the system's automatic backup. For an app with no persistent data, it is irrelevant.

**`dataExtractionRules`** (API 31+) and **`fullBackupContent`** (below API 31) — files that say what gets saved. Both point to `res/xml/`. If one is missing, the build passes, but lint warns.

**`supportsRtl="true"`** — the interface is mirrored in RTL languages. Hence the importance of `GravityCompat.START` instead of `Gravity.LEFT`.

**`android:theme="@style/Theme.DMA03"`** — the theme applies to **all** activities that have no `android:theme` of their own. Both inherit it.

```xml
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
```

**`.MainActivity`** — the leading dot means "in the app's package", that is, `ro.ase.ie.dma03.MainActivity`. The full form would be identical.

**`android:exported="true"`** — mandatory for the component with an `intent-filter` from API 31 onwards. Without it, the build **fails**. It is the only activity that can be started from outside — by the launcher.

**`intent-filter` with `MAIN` + `LAUNCHER`** — the pair that creates the icon in the launcher. `MAIN` = the entry point, `LAUNCHER` = it appears in the app list. Both are needed.

**`windowSoftInputMode="adjustResize"`** — when the keyboard appears, the window shrinks instead of panning. There is no `EditText` here, so the attribute is useless — but it is harmless and prepares the ground for a screen with fields.

```xml
        <activity
            android:name=".SecondActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**`android:exported="false"`** — no outside app can start it. Correct: it is an internal screen.

**No `intent-filter`** — it has no entry point. It does not appear in the launcher.

**Here is the final proof:** `SecondActivity` is declared, but **nothing starts it**. `MainActivity` contains no `Intent`. The screen is a lab left unconnected — complete code, reachable only if you launch it manually from Android Studio.

**What it would have taken to connect it:** in `MainActivity`, a `startActivity(new Intent(this, SecondActivity.class))` — for example in the `nav_settings` branch or on `action_open` in the context menu. The `android.content.Intent` import is already there, a sign that the intention was there.

---

## 26.4 `activity_main.xml` — the container hierarchy

### The tree, by levels

```
DrawerLayout (id=drawerLayout)                    ← the root; exactly 2 children
├── CoordinatorLayout (id=main)                   ← the content panel (first child)
│   ├── AppBarLayout
│   │   └── MaterialToolbar (id=topAppBar)
│   └── FrameLayout
│       └── ListView (id=listView)
└── NavigationView (id=navigationView)            ← the drawer (second child)
```

**The `DrawerLayout` rule:** exactly **two** direct children. The first is the content, the second is the drawer. The second **must** have `android:layout_gravity="start"` (or `end`) — otherwise it is treated as a second content panel and never opens.

**Why `CoordinatorLayout` and not `FrameLayout` directly:** it coordinates `AppBarLayout` with the list — the `liftOnScroll` effect needs it. Without a `CoordinatorLayout`, the bar does not know when the list scrolls.

**Why another `FrameLayout` between `CoordinatorLayout` and `ListView`:** `CoordinatorLayout` needs a child to apply `layout_behavior` to. `ListView` could be that child itself, but the `FrameLayout` isolates the behaviour and leaves room for a FAB or an "empty list" `TextView` in the future.

### The root

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- DrawerLayout: exactly 2 direct children — the content and the drawer -->
<androidx.drawerlayout.widget.DrawerLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/drawerLayout"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
```

**`@+id/drawerLayout`** — the `+` sign means "create the id if it does not exist". The first occurrence in an XML file must have the `+`; in code you use `R.id.drawerLayout` without it.

**`match_parent` × 2** — the container covers the whole screen, including the areas under the bars. `EdgeToEdge` only makes sense this way: the content stretches, and the insets padding keeps it in the safe area.

**`xmlns:app`** — the namespace for the attributes defined by libraries (`app:menu`, `app:title`). Without it, `app:menu` is not recognised.

### The content panel

```xml
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
```

**`xmlns:android` and `xmlns:app` are declared again** — although they are already on the `DrawerLayout`. Redundant, but legal: namespaces are inherited, and the redeclaration is ignored. It breaks nothing; some editors add them automatically.

**`@+id/main`** — this is where `findViewById(R.id.main)` in the code comes from, for the insets. The id is on the **content**, not on the `DrawerLayout` — so the insets padding does not touch the drawer.

### The top bar

```xml
    <com.google.android.material.appbar.AppBarLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#6750A4"
        app:liftOnScroll="true"
        app:liftOnScrollColor="#4F378B"
        app:liftOnScrollTargetViewId="@id/listView">
```

**`#6750A4`** — the Material 3 base purple, **hardcoded**. It does not adapt to dark mode: in the dark the bar stays light purple. The correct thing would be `?attr/colorPrimary`.

**`liftOnScroll="true"`** — when the list scrolls, the bar changes its colour to `liftOnScrollColor` (`#4F378B`, also hardcoded) and gets a shadow. It is the "app bar that lifts" effect.

**`liftOnScrollTargetViewId="@id/listView"`** — tells `AppBarLayout` **which** view scrolls. Without it, `AppBarLayout` automatically looks for a scrollable view among its siblings; since the `ListView` is hidden inside the `FrameLayout`, it does not find it and the effect never triggers.

```xml
        <com.google.android.material.appbar.MaterialToolbar
            android:id="@+id/topAppBar"
            android:layout_width="match_parent"
            android:layout_height="?attr/actionBarSize"
            android:background="@android:color/transparent"
            app:title="Inbox"
            app:titleTextColor="@android:color/white"
            app:navigationIcon="@drawable/ic_menu"
            app:navigationIconTint="@android:color/white"
            app:menu="@menu/top_app_bar"
            app:layout_scrollFlags="scroll|enterAlways|snap"
            app:theme="@style/ThemeOverlay.Material3.Dark.ActionBar" />
```

**`?attr/actionBarSize`** — the standard bar height (56dp). Do not hardcode `56dp`: on some themes and orientations it differs.

**`android:background="@android:color/transparent"`** — the toolbar is transparent, the colour comes from the `AppBarLayout`. Otherwise you would have two layers of purple, and `liftOnScroll` would only change one of them.

**`app:title="Inbox"`** — the initial title. The code overrides it with `toolbar.setTitle(...)` on a drawer click.

**`app:titleTextColor` and `app:navigationIconTint`** — white. Without them, the text would be black on purple in light theme. `navigationIconTint` is needed separately because the vector icon has its own colour (`#000000` in `ic_menu.xml`).

**`app:navigationIcon="@drawable/ic_menu"`** — the three lines. The drawing is a 24dp `VectorDrawable`; the actual colour is given by `navigationIconTint`.

**`app:menu="@menu/top_app_bar"`** — inflates the menu straight from XML. That is why `onCreate` has no `onCreateOptionsMenu`.

**`app:layout_scrollFlags="scroll|enterAlways|snap"`** — the scroll behaviour:

| Flag | Effect |
|---|---|
| `scroll` | the bar goes off screen when you scroll down |
| `enterAlways` | it comes back as soon as you scroll up, wherever you are in the list |
| `snap` | it stops either fully visible or fully hidden, never halfway |

**`app:theme="@style/ThemeOverlay.Material3.Dark.ActionBar"`** — applies a dark theme **only** to the toolbar, so the text and icons are light. The alternative would have been to set each colour separately.

### The list

```xml
    </com.google.android.material.appbar.AppBarLayout>

    <!-- layout_behavior: tells CoordinatorLayout that this view sits UNDER the app bar -->
    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_behavior="@string/appbar_scrolling_view_behavior">

        <ListView
            android:id="@+id/listView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:entries="@array/items"
            android:nestedScrollingEnabled="true" />
    </FrameLayout>
```

**`app:layout_behavior="@string/appbar_scrolling_view_behavior"`** — without it, the `FrameLayout` would be drawn from `y=0`, that is **under** the bar, and the first rows would be covered. The behaviour pushes it down by exactly the bar's height.

**`android:entries="@array/items"`** — `ListView` builds itself an `ArrayAdapter` from the 20 strings in `strings.xml`. **There is no adapter in the code** — which is why `listView.getItemAtPosition(position)` returns a `String` directly.

**`android:nestedScrollingEnabled="true"`** — lets the list pass the scroll events to the parent (`CoordinatorLayout`), so that `liftOnScroll` works. Without it, the list "swallows" the scroll and the bar does not react.

**`match_parent` on the height** — the list fills all the space left after the bar. `wrap_content` would have let it grow without limit.

### The drawer

```xml
</androidx.coordinatorlayout.widget.CoordinatorLayout>

    <com.google.android.material.navigation.NavigationView
        android:id="@+id/navigationView"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        app:menu="@menu/drawer_menu" />

</androidx.drawerlayout.widget.DrawerLayout>
```

**`layout_width="wrap_content"`** — the drawer is as wide as its content, not as the screen. `match_parent` would cover everything and would no longer look like a drawer. Material recommends ~280dp; `wrap_content` comes close.

**`layout_height="match_parent"`** — the full height.

**`android:layout_gravity="start"`** — **the attribute that makes the difference.** Without it, the `NavigationView` is treated as a second content panel and never opens. It must be identical to `GravityCompat.START` in the code.

**`app:menu="@menu/drawer_menu"`** — the drawer's content comes from the XML. `NavigationView` inflates it itself; the code only listens for clicks.

**`NavigationView` applies its own insets** — it extends `ScrimInsetsFrameLayout`, which adds padding for the status bar. That is why it needs no insets block in the code.

---

## 26.5 `activity_second.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".SecondActivity">
```

**A vertical `LinearLayout`** — the children stack from top to bottom. That is why the buttons added from code appear one under the other, not on top of each other.

**`android:id="@+id/main"`** — used twice in the code: for the insets and for `inflatedLayout`. The id repeats the one in `activity_main.xml`, but that is not a problem: the two layouts never coexist in the same tree.

**`xmlns:app` is declared but unused** — no `app:*` attribute in the file. Leftover from the template, flagged by lint.

**`tools:context=".SecondActivity"`** — only for the Android Studio preview: it tells the editor which theme and which class to use. Removed at build time, it does not reach the APK.

```xml
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:onClick="btnClick"
        android:text="Button" />
</LinearLayout>
```

**`android:onClick="btnClick"`** — binds the button to the `btnClick(View)` method in the activity, through reflection. **There is no `setOnClickListener` in the code** — the whole binding is here.

**Why it works with no code:** on click, Android looks for the method in the activity's context. If it does not find it, the exception appears **at runtime**, not at compile time.

**`android:id="@+id/button"` is not used anywhere** — neither in the code nor in another XML. It is only useful if you want to reference it later. The buttons created from code get numeric ids (1, 2, 3...), not resource ids.

**`match_parent` on the width** — the button fills the screen. The buttons added from code get the same `MATCH_PARENT`, so they look identical.

**No `padding` on the `LinearLayout`** — the buttons touch the edges of the screen. Cosmetic, not functional.

---

## 26.6 The menus (`res/menu/*.xml`)

Three files, three different purposes. All of them are inflated from XML — none is built in code.

### `drawer_menu.xml` — the drawer's content

```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- checkableBehavior="single" = radio group: a single checked item -->
    <group android:checkableBehavior="single">
        <item
            android:id="@+id/nav_inbox"
            android:icon="@drawable/ic_inbox"
            android:title="Inbox"
            android:checked="true" />
        <item
            android:id="@+id/nav_sent"
            android:icon="@drawable/ic_send"
            android:title="Sent" />
        <item
            android:id="@+id/nav_trash"
            android:icon="@drawable/ic_delete"
            android:title="Trash" />
    </group>
```

**`android:checkableBehavior="single"`** — the group behaves like a radio group: when you select "Sent", "Inbox" is unchecked automatically. The possible values: `single`, `all`, `none`.

**`android:checked="true"` on `nav_inbox`** — the initial state. Without it, on the first open no item is checked, although the toolbar shows "Inbox".

**`android:icon`** — each item has a vector icon from `res/drawable/`. `NavigationView` shows them to the left of the title.

**`android:title` is literal text, not `@string/...`** — it works, but it is not translated. For a real app, all the titles should be in `strings.xml`.

```xml
    <item android:title="Other">
        <menu>
            <item
                android:id="@+id/nav_settings"
                android:icon="@drawable/ic_settings"
                android:title="Settings" />
        </menu>
    </item>
</menu>
```

**An `<item>` with no id, containing a `<menu>`** — the trick for a **section subtitle**. "Other" appears as a grey label, and "Settings" below it, separate from the main group.

**Why `nav_settings` is outside the group** — it is not part of the main navigation (Inbox/Sent/Trash), it is a setting. The visual separation suggests the difference.

**The consequence in the code:** `nav_settings` is not checkable, so `item.setChecked(true)` has no visual effect on it. Its branch shows a `Toast`.

### `list_item_menu.xml` — the context menu

```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/action_open"
        android:title="Open" />
    <item
        android:id="@+id/action_rename"
        android:title="Rename" />
    <item
        android:id="@+id/action_delete"
        android:title="Delete" />
</menu>
```

**Deliberate minimalism:** no icons, no `showAsAction`. A `PopupMenu` has no bar — all the items appear in the list, so `showAsAction` would be ignored.

**The three ids are exactly the ones checked in `MainActivity`:** `action_open`, `action_rename`, `action_delete`. If you rename one in the XML without changing the code, that branch no longer runs — and you get no compile error, just an `if` that never enters again.

**No `android:icon`** — a short context menu reads faster without icons. With icons, `PopupMenu` displays them, but they take up more space.

### `top_app_bar.xml` — the bar's menu

```xml
<?xml version="1.0" encoding="utf-8"?>
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

**`app:showAsAction` and not `android:showAsAction`** — the attribute is defined by the AppCompat library, not by the platform. With `android:` it would be silently ignored on newer versions.

**The three values that matter:**

| Value | Effect |
|---|---|
| `ifRoom` | appears on the bar if it fits; otherwise in the overflow |
| `never` | always in the "⋮" menu |
| `always` | always on the bar, even if it crowds the title |

**`action_search` and `action_share` have `ifRoom`** — on a narrow phone, one of them may fall into the overflow. On a tablet both appear.

**`action_settings` has `never` and no icon** — in the overflow, the text is enough. Items with an icon in the overflow show their icon; those without show only the text.

**The order in the XML = the order on the bar**, from left to right (after the navigation icon). In the overflow, the order is preserved.

**The titles are literals**, not resources — the same observation as for `drawer_menu.xml`.

---

## 26.7 The full flow

### Startup

```
LAUNCHER → MainActivity
  onCreate
    ├── super.onCreate
    ├── EdgeToEdge.enable
    ├── setContentView(activity_main)
    │     └── DrawerLayout
    │           ├── CoordinatorLayout (id=main)
    │           │     ├── AppBarLayout → MaterialToolbar (id=topAppBar)
    │           │     └── FrameLayout → ListView (id=listView)
    │           │           └── automatic adapter from @array/items → 20 rows
    │           └── NavigationView (id=navigationView, gravity=start)
    ├── insets on R.id.main        → padding for the system bars
    ├── listView = findViewById
    ├── listView.setOnItemLongClickListener   → PopupMenu
    ├── drawerLayout / toolbar / navigationView = findViewById
    ├── navigationView.setNavigationItemSelectedListener
    ├── getOnBackPressedDispatcher().addCallback
    ├── toolbar.setNavigationOnClickListener
    └── toolbar.setOnMenuItemClickListener
```

**No state instruction** — nothing is read from `savedInstanceState`, nothing is saved. On rotation, everything returns to the initial state.

### Opening the drawer

```
PRESS HAMBURGER
  toolbar.setNavigationOnClickListener
    └── drawerLayout.openDrawer(GravityCompat.START)
          └── NavigationView slides in from the left over the content

PICK "Sent"
  navigationView.setNavigationItemSelectedListener(item)
    ├── id == R.id.nav_sent → toolbar.setTitle("Sent")
    ├── item.setChecked(true)              → "Inbox" is unchecked (checkableBehavior=single)
    ├── drawerLayout.closeDrawer(START)    → the drawer retracts
    └── return true                        → click handled

EFFECT: the bar's title changes. The list stays the same — 20 "Item N" rows.
```

### The context menu

```
LONG PRESS ON ROW 5
  listView.setOnItemLongClickListener(parent, view, position=5, id=5)
    ├── new PopupMenu(this, view)          → anchored on the pressed row
    ├── inflate(R.menu.list_item_menu)     → Open / Rename / Delete
    ├── popup.show()
    └── return true                        → no normal click afterwards

PICK "Delete"
  popup.setOnMenuItemClickListener(menuItem)
    ├── selected = listView.getItemAtPosition(5).toString()   → "Item 6"
    ├── id == R.id.action_delete
    ├── Toast "Delete: Item 6"
    └── return true                        → the menu closes
```

**Watch the index:** `position` is 0-based, so row 5 displays "Item 6". It is not a bug — it is the Java convention.

### The Back button

```
DRAWER OPEN + BACK
  OnBackPressedCallback.handleOnBackPressed()
    ├── isDrawerOpen(START) == true
    └── closeDrawer(START)                 → you stay on the screen

DRAWER CLOSED + BACK
  OnBackPressedCallback.handleOnBackPressed()
    ├── isDrawerOpen(START) == false
    ├── setEnabled(false)                  → you disable yourself, so you don't call yourself again
    └── getOnBackPressedDispatcher().onBackPressed()
          └── the default handler → finish() → the app closes
```

### The unconnected screen

```
MainActivity ──X──> SecondActivity
                    (no Intent anywhere)

If you launch it manually:
  SecondActivity.onCreate
    ├── setContentView(activity_second)    → vertical LinearLayout + one Button
    ├── insets on R.id.main
    └── inflatedLayout = findViewById(R.id.main)

  CLICK on "Button"
    └── android:onClick → btnClick(View)
          └── AlertDialog.Builder
                ├── Title: "Add new control ..."
                ├── Message: "Are you sure you want to add a new control?"
                ├── Cancelable: true
                ├── Positive "Do it!"
                │     ├── id = addButton()          → Button_1, id=1, added to the layout
                │     └── Snackbar LENGTH_LONG "Cancel previous action."
                │           └── action "Cancel"
                │                 ├── findViewById(id)
                │                 └── removeView(...)   → the button disappears
                ├── Negative "Cancel"
                │     └── Toast "Object creation cancelled"
                └── builder.show()
```

**The big picture:** `MainActivity` demonstrates navigation (drawer + toolbar + context menu + Back). `SecondActivity` demonstrates the dialog and the dynamic manipulation of the view tree. They are two separate labs, glued into the same project.

---

## 26.8 What to remember

| File | The essence |
|---|---|
| `MainActivity.java` | `onCreate` does everything: insets, list, drawer, Back, hamburger, menu. `GravityCompat.START` four times, identical to the XML. |
| `SecondActivity.java` | `android:onClick` requires `public void name(View)`. `setId` is what makes the button findable. `hPixels` is dead code. |
| `AndroidManifest.xml` | `exported="true"` + `MAIN`/`LAUNCHER` = the start screen. `SecondActivity` is declared but not connected. |
| `activity_main.xml` | `DrawerLayout` with exactly 2 children; the second has `layout_gravity="start"`. `id=main` is on the content, not on the drawer. |
| `activity_second.xml` | A vertical `LinearLayout` with one button bound through `android:onClick`. |
| `drawer_menu.xml` | `checkableBehavior="single"` = radio group. An `item` with no id + a nested `menu` = section subtitle. |
| `list_item_menu.xml` | Three actions, no icons. The ids must match the ones in the code. |
| `top_app_bar.xml` | `app:showAsAction`: `ifRoom` on the bar, `never` in the overflow. |

### The six links that must be identical

| In XML | In code | What breaks if they differ |
|---|---|---|
| `android:layout_gravity="start"` | `GravityCompat.START` | the drawer does not open / does not close |
| `@+id/drawerLayout` | `R.id.drawerLayout` | `NullPointerException` |
| `@+id/topAppBar` | `R.id.topAppBar` | `NullPointerException` |
| `@+id/navigationView` | `R.id.navigationView` | `NullPointerException` |
| `@+id/main` | `R.id.main` (insets) | no padding, content under the bars |
| `android:onClick="btnClick"` | `public void btnClick(View)` | `IllegalStateException` on click |

### The mistakes a test would catch

1. **You forget `closeDrawer`** — the drawer stays over the screen after a selection.
2. **You forget `setEnabled(false)` in the Back callback** — `StackOverflowError` on Back with the drawer closed.
3. **You put `Gravity.LEFT` in one place and `START` in another** — works in Romanian, breaks in RTL.
4. **You remove `app:layout_behavior`** — the list is drawn under the bar.
5. **You remove `liftOnScrollTargetViewId`** — the bar no longer reacts to scrolling.
6. **You remove `setId` from `addButton`** — the Snackbar can no longer find the button to delete.
7. **You make `btnClick` private** — it compiles, it crashes on click.

---

## Chapter 26 summary

- `MainActivity` has a single `onCreate` with seven responsibilities; the order `super` → `EdgeToEdge` → `setContentView` → `findViewById` is mandatory.
- `DrawerLayout` has exactly two children: the content and the drawer. The drawer is recognised by `layout_gravity="start"`.
- `id=main` is on the `CoordinatorLayout`, not on the `DrawerLayout` — the insets apply only to the content, and `NavigationView` takes care of its own.
- `MaterialToolbar` has two click areas, with two different listeners: `setNavigationOnClickListener` (hamburger) and `setOnMenuItemClickListener` (Search/Share/Settings).
- `PopupMenu` is anchored on the pressed row and needs `return true` so that it does not also trigger the normal click.
- `OnBackPressedCallback` solves Back in two steps: close the drawer, then disable yourself and re-send the event. Without `setEnabled(false)`, infinite recursion.
- `AlertDialog.Builder` chains; `show()` is mandatory. Here it is the platform variant, not AppCompat.
- `Snackbar` needs `.show()` and a reference view; its action can delete a view added from code.
- Views created from code need three things: a themed context, `LayoutParams`, `setId` if you want to find them again.
- `SecondActivity` is declared in the manifest, but it is **not started anywhere** — the `Intent` import in `MainActivity` is the only trace of the missing link.

**Back to** [the cheatsheet](21%20-%20Cheatsheet.md), to [the DMA03 build chapter](14%20-%20DMA03%20-%20Navigare%20si%20meniuri.md) **or to** [the overview](index.html).
