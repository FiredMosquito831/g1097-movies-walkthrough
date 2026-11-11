# Chapter 26 — The DMA03 code, annotated

**Objective:** to read the `DMA03` project line by line — every statement explained: what it does, why it is there, what breaks if you remove it. By the end you should be able to rebuild from memory a drawer with a toolbar, a per-row context menu and a dialog that creates controls.

**Estimated time:** 90–120 min (active reading; annotated chapters are read more slowly than the build ones).

**Source:** `DMA03/` at commit `d719ffc` — 8 files: two activities, the manifest, two layouts and three menus.

**What you learn from it:** `DrawerLayout`, `NavigationView`, `MaterialToolbar`, `PopupMenu`, `OnBackPressedCallback`, `AlertDialog`, `Snackbar`, views created from code.

> **How to read this:** don't read passively. Each file is **a single code block**, in source order, with the explanations woven into it. Cover the comment, say what the line does, then check. If you can't, you have found what needs repeating.

---

## 26.0 The annotation conventions

The chapter uses six kinds of markers, all **inside the code block**. You recognise them by shape, without memorising them.

| Marker | Where it appears | What it contains |
|---|---|---|
| `/* FILE: ... */` | at the start of the block | the role of the file, what it demonstrates, what it depends on |
| `/* THEORY BLOCK: ... */` | before a large section | the theory needed to understand the code that follows |
| `/* METHOD: ... */` | above every method | **Theory / Logic / Ref / Risk** — four fixed headings |
| `// 1.`, `// 2.`, `// 3.` | inside the methods | the execution steps, in the order they run |
| `// WARNING:` | next to a dangerous line | the mistake that compiles but crashes at runtime |
| `// RISK:` | next to a debatable choice | what breaks if you change or remove the line |

**Why four headings for every method:**

1. **Theory** — the concept behind it. Without it, the method is a recipe you forget after the test.
2. **Logic** — the concrete, numbered steps. This is the answer to "what does the method do".
3. **Ref** — where you find the topic in the materials. So that you can come back.
4. **Risk** — what breaks if the method is missing or written differently. This is the answer to "why doesn't it work".

**The golden rule of the chapter:** the actual code is **untouched, character for character**. Everything new is a comment. Each file is one continuous block, exactly like the source file: you will not find separate fragments of prose between the lines.

**The density is intentional.** In the reference file, roughly two to four lines of comment accompany every three to five lines of code. The chapter exceeds that ratio, because all the theory sits inside the block: every import, every field, every method and almost every line has its explanation, written as `//` or `/* */` in the same block.

### The file map

| File | Lines | Role | Section |
|---|---|---|---|
| `MainActivity.java` | 127 | the main screen: drawer, toolbar, two menus, Back | 26.1 |
| `SecondActivity.java` | 88 | dialog + Snackbar + buttons created from code | 26.2 |
| `AndroidManifest.xml` | 29 | the declaration of the two activities | 26.3 |
| `activity_main.xml` | 62 | the container hierarchy of the main screen | 26.4 |
| `activity_second.xml` | 17 | a `LinearLayout` with one button | 26.5 |
| `drawer_menu.xml` | 28 | the contents of the drawer | 26.6 |
| `list_item_menu.xml` | 12 | the per-row context menu | 26.6 |
| `top_app_bar.xml` | 22 | the top bar menu | 26.6 |

**Overall observation:** the project has 385 lines of code (325 without blank lines and comments) and roughly 2,500 lines of explanation in the present chapter. The ratio is intentional. In the exam what matters is knowing **why** each line is there, not reproducing the syntax.

---

## 26.1 `MainActivity.java` — drawer, toolbar, menus

A single `onCreate`, ten steps. The file has no helper methods — everything is inline. It is the densest file in the project and, in the test, the most likely one to ask you for a change. The block below is the whole file, in source order.

```java
/*
 * ======================================================================================
 * FILE: MainActivity.java
 * ======================================================================================
 * ROLE:
 *   The main screen of the DMA03 app. A single `onCreate` that ties together five
 *   components: the list, the context menu, the drawer, the top bar and the Back button.
 *
 * WHAT IT DEMONSTRATES:
 *   1. DrawerLayout + NavigationView   — side menu sliding over the content.
 *   2. MaterialToolbar                 — title, hamburger icon, actions menu.
 *   3. PopupMenu                       — context menu anchored to a row.
 *   4. OnBackPressedCallback           — intercepting the Back button.
 *
 * DEPENDS ON:
 *   - androidx.activity           → EdgeToEdge, OnBackPressedCallback
 *   - com.google.android.material → MaterialToolbar, NavigationView
 *   - androidx.drawerlayout       → DrawerLayout (brought in transitively by `material`)
 *
 * WHAT IT DOES NOT DO:
 *   - it does not start SecondActivity (there is no `startActivity` anywhere in the file);
 *   - it saves nothing in `savedInstanceState`;
 *   - it has no hand-written adapter — the list is fed from `@array/items`.
 *
 * REF: ch. 14 — DMA03: navigation, menus and dialogs.
 * ======================================================================================
 */

package ro.ase.ie.dma03;

// ======================================================================================
// IMPORT 1: android.content.Intent — IMPORTED BUT UNUSED
// ======================================================================================
// WHAT IT IS: the description of an action or of a screen to start.
// WHY IT IS HERE: the only way to open SecondActivity would be
//   `startActivity(new Intent(this, SecondActivity.class))`.
// WHY IT IS A PROBLEM: there is no `new Intent(...)` anywhere in the file, no
//   `startActivity`. The import is the ONLY trace of the missing link.
// HOW TO CHECK: Ctrl+F for "Intent" across the whole project → a single result, this line.
// ======================================================================================
import android.content.Intent;

// ======================================================================================
// IMPORT 2: android.os.Bundle — the state saved on recreation
// ======================================================================================
// WHAT IT IS: a key-value dictionary that the system keeps between instances.
// WHY IT IS HERE: the signature of `onCreate(Bundle)` requires it.
// WHY IT IS USELESS HERE: the code never reads `savedInstanceState`. On rotation,
//   everything returns to the initial state: the title "Inbox", "Inbox" checked, the list at the top.
// ======================================================================================
import android.os.Bundle;

// ======================================================================================
// IMPORT 3: android.widget.ListView — the list of 20 rows
// ======================================================================================
// WHAT IT IS: a `ViewGroup` that displays a scrollable vertical list.
// WHY IT IS HERE: the main screen is, in practice, a list with a context menu.
// WHY NOT `RecyclerView`: 20 static rows, no animations, no complicated recycled
//   views. `ListView` is enough and requires zero adapter code.
// ======================================================================================
import android.widget.ListView;

// ======================================================================================
// IMPORT 4: android.widget.PopupMenu — the menu anchored to a row
// ======================================================================================
// WHAT IT IS: a floating menu, attached to a specific view (the anchor).
// WHY IT IS HERE: a long press on a row must open Open / Rename / Delete
//   next to that row, not in the corner of the screen.
// WHY NOT `androidx.appcompat.widget.PopupMenu`: it would have worked, but the platform
//   variant is enough. The difference only shows in the background style and the ripple.
// ======================================================================================
import android.widget.PopupMenu;

// ======================================================================================
// IMPORT 5: android.widget.Toast — the short message, with no action
// ======================================================================================
// WHAT IT IS: a text that appears and disappears on its own, without blocking the screen.
// WHY IT IS HERE: all the menu branches are demonstrations — a `Toast` is enough.
// WHY NOT `Snackbar`: `Snackbar` needs a parent view and an extra `.show()`
//   call. For a confirmation with no action, `Toast` is more direct.
// ======================================================================================
import android.widget.Toast;

// ======================================================================================
// IMPORTS 6-13: androidx.* — the activity infrastructure
// ======================================================================================
// EdgeToEdge              → drawing under the system bars (API 21+).
// OnBackPressedCallback   → the modern mechanism for the Back button.
// AppCompatActivity       → the base activity, with AppCompat support.
// Insets                  → the rectangles of the system bars, in pixels.
// GravityCompat           → START/END, safe for RTL.
// ViewCompat              → the insets listener, compatible on all API levels.
// WindowInsetsCompat      → the insets types (systemBars, ime, displayCutout).
// DrawerLayout            → the drawer container (comes in transitively through `material`).
// ======================================================================================
import androidx.activity.EdgeToEdge;
import androidx.activity.OnBackPressedCallback;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.GravityCompat;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.drawerlayout.widget.DrawerLayout;

// ======================================================================================
// IMPORTS 14-15: Material — the bar and the drawer
// ======================================================================================
// MaterialToolbar  → `Toolbar` with Material 3 styling applied automatically.
// NavigationView   → the drawer contents: menu, icons, check marks, its own insets.
// ======================================================================================
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.navigation.NavigationView;

/*
 * ======================================================================================
 * THEORY BLOCK: ACTIVITY AND THE LIFECYCLE
 * ======================================================================================
 *
 * 1. WHAT AN ACTIVITY IS
 *    -   An Android component with its own window. The system creates it, shows it,
 *        hides it and destroys it by its own rules.
 *    -   You do not instantiate it with `new MainActivity()`. The system starts it,
 *        based on an `Intent` or on the launcher icon.
 *    -   It has a lifecycle with states: CREATED → STARTED → RESUMED → PAUSED →
 *        STOPPED → DESTROYED. Between states, the system calls callback methods.
 *
 * 2. `onCreate` — THE FIRST CALLBACK, ONCE PER INSTANCE
 *    -   This is where the interface is built: `setContentView`, `findViewById`, listeners.
 *    -   It is called at startup and at every recreation (rotation, theme change,
 *        language change). On recreation it receives `savedInstanceState` with the data
 *        saved previously — here it is `null` the first time and is always ignored.
 *    -   It is not the place for long operations: the block runs on the main thread,
 *        and the system waits for it to finish before drawing the first frame.
 *
 * 3. THE MANDATORY ORDER IN `onCreate`
 *    -   `super.onCreate(...)` FIRST. The parent initializes the infrastructure
 *        (including the `OnBackPressedDispatcher` used below).
 *    -   `setContentView(...)` BEFORE any `findViewById`. Otherwise you get
 *        `null`, not an exception — and the `NullPointerException` appears later, on a
 *        line with no apparent connection.
 *    -   `findViewById` and listeners AFTER `setContentView`.
 *
 * 4. WHY A SINGLE `onCreate` IS A DIDACTIC PROBLEM, NOT A TECHNICAL ONE
 *    -   It works perfectly. But seven responsibilities in a 100-line method
 *        are hard to read and even harder to test.
 *    -   In a real application: private methods `setupToolbar()`, `setupDrawer()`,
 *        `setupList()`. Here they are left inline so that you see the real order of the calls.
 *
 * 5. WHAT "CONTEXT" MEANS
 *    -   `this` from an activity is a `Context` (more precisely a `ContextThemeWrapper`):
 *        it gives access to resources, to the app theme and to the system services.
 *    -   Widgets require a THEMED context. `getApplicationContext()` does not have the
 *        activity theme — that is why `new Button(SecondActivity.this)` and not
 *        `new Button(getApplicationContext())`.
 *
 * REF: ch. 15 — DMA02: Application and lifecycle; the documentation of
 *      `android.app.Activity` and `androidx.activity.ComponentActivity`.
 * ======================================================================================
 */

public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // FIELD 1: drawerLayout
    // ==================================================================================
    // WHAT IT IS: the reference to the `DrawerLayout` from the XML.
    // WHERE IT IS USED: in three places — the drawer listener (`closeDrawer`),
    //   the Back callback (`isDrawerOpen` + `closeDrawer`) and the hamburger (`openDrawer`).
    // WHY IT IS A FIELD AND NOT A LOCAL: all three uses are in `onCreate`, so
    //   a local would have worked too. It is a field out of habit, so that it is at hand if
    //   you add new methods.
    // `private` — nothing outside needs it.
    // ==================================================================================
    private DrawerLayout drawerLayout;

    // ==================================================================================
    // FIELD 2: listView
    // ==================================================================================
    // WHAT IT IS: the reference to the list from the XML.
    // WHERE IT IS USED: in the long-press listener, to read the text of the pressed
    //   row (`getItemAtPosition(position)`).
    // WHY IT IS A FIELD: the long-press lambda runs AFTER `onCreate` has finished.
    //   A local variable would be captured in the closure (a lambda captures only
    //   effectively final variables), but a field is clearer and lives as long as
    //   the activity does.
    // ==================================================================================
    private ListView listView;

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: onCreate(Bundle savedInstanceState)
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   The creation callback of the activity. It runs once per instance, on the main
     *   thread, before the first frame is drawn. This is where the whole view tree is
     *   built and all the listeners are bound.
     *
     * LOGIC (the real order in the code):
     *   1. `super.onCreate`                — initializes the parent (including the Back dispatcher)
     *   2. `EdgeToEdge.enable`             — the window extends under the system bars
     *   3. `setContentView`                — inflates `activity_main.xml`
     *   4. insets on `R.id.main`           — padding so you don't sit under the clock
     *   5. `listView` + long press         — `PopupMenu` anchored to the row
     *   6. `drawerLayout`/`toolbar`/`nav`  — the three components found by id
     *   7. drawer listener                 — changes the title, closes the drawer
     *   8. Back callback                   — closes the drawer or delegates
     *   9. hamburger                       — opens the drawer
     *  10. toolbar menu                    — Search / Share / Settings
     *
     * REF:
     *   ch. 14 (sections 14.1–14.6), the documentation of `Activity#onCreate`.
     *
     * RISK:
     *   - `findViewById` before `setContentView` → `null`, then an NPE in a listener.
     *   - `super.onCreate` omitted → `SuperNotCalledException` at runtime.
     *   - listeners moved before `setContentView` → they receive `null` views.
     * ----------------------------------------------------------------------------------
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // STEP 1: super.onCreate — starts the parent's lifecycle.
        // Without it, `getOnBackPressedDispatcher()` below would receive an unconfigured
        // dispatcher. `@Override` is also a check: if the signature is wrong,
        // the compiler warns you.
        super.onCreate(savedInstanceState);

        // STEP 2: EdgeToEdge — the window extends under the status bar and under the
        // navigation bar. It calls `WindowCompat.setDecorFitsSystemWindows(window, false)`.
        // Without it, the app would have opaque system bars and you would not need the
        // insets block below. With it, you DO need it — otherwise the first row in the
        // list goes under the clock.
        EdgeToEdge.enable(this);

        // STEP 3: setContentView — `LayoutInflater` reads the XML, creates the
        // Java objects for every tag and attaches them to the window.
        // From this moment, `findViewById` can find something. Before, the tree does not exist.
        // `R.layout` is the layout resource (the whole file); `R.id` is an identifier
        // inside a view. Two different namespaces, generated in the same `R.java`.
        setContentView(R.layout.activity_main);

        // STEP 4: insets — when the system calculates how much the bars occupy, it applies
        // to the view with `id=main` a padding equal to them. The content moves into the
        // safe area, the background stays stretched across the whole screen.
        //
        // `ViewCompat.setOnApplyWindowInsetsListener` registers a compatible listener:
        // on old APIs it uses the old methods, on new APIs the new ones.
        // The listener runs immediately after `setContentView` and then on every
        // change (rotation, keyboard, bars appearing/disappearing). It does not run once
        // — that is why the code inside it must be idempotent.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            // `Type.systemBars()` = status bar + navigation bar + caption bar.
            // It does not include the keyboard (`Type.ime()`) nor the cutout (`Type.displayCutout()`).
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // `setPadding` OVERWRITES the existing padding. If the `CoordinatorLayout`
            // had `android:padding="8dp"` in the XML, those 8dp would disappear at the first
            // insets pass. The correct way would be `v.setPadding(base + insets.left, ...)`, with the base
            // values saved in a field. Here the XML has no padding, so it does not show.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // `return insets` — NOT `WindowInsetsCompat.CONSUMED`. The insets go further,
            // to the children. If you consumed them, `AppBarLayout` would no longer know about them
            // and `liftOnScroll` would receive wrong values. You consume only when you have fully
            // handled the area yourself and want to stop the propagation.
            return insets;
        });

        // STEP 5: the list. The method is generic (`<T extends View> T findViewById(int)`),
        // so the compiler infers the type from the assignment; no cast is needed.
        // The search is done on the activity, that is, across the whole window tree. If you had
        // two views with the same id in different layouts, you would get the first one found —
        // that is why ids must be unique within a layout.
        listView = findViewById(R.id.listView);

        // `setOnItemLongClickListener` registers a listener for a long press
        // on ANY row of the list. There is no "per-row" listener: `ListView` has a single
        // one, for all the rows, and it tells you in the parameters which row was pressed.
        //
        // Lambda with four parameters for `AdapterView.OnItemLongClickListener`:
        //   parent   : AdapterView<?> — the `ListView` itself (not used here)
        //   view     : View           — the pressed ROW; it becomes the anchor of the menu
        //   position : int            — the index of the row in the list, 0-based
        //   id       : long           — the id of the item; for `ArrayAdapter` it is
        //                               equal to `position`. The type is `long` because
        //                               `AdapterView` can also work with ids from
        //                               databases (`SQLite` uses `long`).
        //
        // There is NO `setOnItemClickListener` anywhere in the file. A simple tap on a row
        // does nothing. Only the long press reacts. It is a didactic choice:
        // the project demonstrates the context menu, not navigation.
        //
        // What happens on a simple tap, concretely: `ListView` receives `ACTION_DOWN`,
        // starts a `CheckForLongPress` with the system timeout (~500 ms), and on
        // `ACTION_UP` without a click listener nothing happens. The row does not even
        // stay highlighted — `ListView` in `CHOICE_MODE_NONE` mode keeps no selection.
        //
        // Why the listener is on the list and not on the adapter: the adapter produces views,
        // not events. `ListView` is the one that knows the position and the pressed row.
        //
        // ------------------------------------------------------------------------------
        // METHOD (lambda): onItemLongClick(parent, view, position, id)
        // THEORY: callback for a long press on a list row.
        // LOGIC:  1. builds a `PopupMenu` anchored to `view`;
        //         2. inflates `list_item_menu`;
        //         3. registers the item listener;
        //         4. `show()` and `return true`.
        // REF:    26.1.9–26.1.11
        // RISK:   without `return true`, the normal click fires as well.
        // ------------------------------------------------------------------------------
        // Long press shows the popup menu
        listView.setOnItemLongClickListener((parent, view, position, id) -> {
            // `new PopupMenu(this, view)` — `this` is the context (the activity, for the
            // theme), `view` is the anchor. `PopupWindow` calculates the position starting from
            // the view's rectangle and places it below if it fits, or above
            // if it does not. That is why the menu appears attached to the row, not in the corner of the screen.
            //
            // Why NOT `listView` as the anchor: `ListView` is a large rectangle, as big as the whole
            // screen. The menu would appear at its edge — that is, at the top, next to the bar — and would
            // cover the pressed row. Why NOT `toolbar`: it would look like an overflow menu
            // of the bar, not like a context menu.
            PopupMenu popup = new PopupMenu(this, view);   // anchored to the pressed row

            // `getMenuInflater()` comes from `Context` (the activity) and returns a
            // `MenuInflater` — a parser for `<menu>`, not for layouts.
            // `inflate(resource, menu)` — the second argument is the DESTINATION `Menu`,
            // obtained with `popup.getMenu()`. It is not like `setContentView`, where you pass only
            // the resource. Why `R.menu.list_item_menu` and not `top_app_bar`: they are two
            // different menus, for two different contexts. `list_item_menu` has
            // "Open / Rename / Delete" — actions on a row. `top_app_bar` has
            // "Search / Share / Settings" — actions on the screen.
            //
            // What happens if you forget `inflate`: the menu is empty. `popup.show()` displays
            // a rectangle with no items, and the listener is never called.
            popup.getMenuInflater().inflate(R.menu.list_item_menu, popup.getMenu());

            // `setOnMenuItemClickListener` is called BEFORE `popup.show()`;
            // if you register it afterwards, the menu is already displayed and the clicks in the first
            // second are lost.
            popup.setOnMenuItemClickListener(menuItem -> {
                // `getItemId()` — the id from the XML (`R.id.action_open` etc.). Not the position:
                // if you reorder the items in the XML, the ids stay the same, the positions do not.
                int itemId = menuItem.getItemId();

                // `position` is captured from the outer lambda. It is a method parameter,
                // hence effectively final — Java allows capturing it. If you tried to
                // modify it in the meantime (`position++`), the compiler would refuse.
                //
                // `getItemAtPosition(position)` returns a `CharSequence` — the text from
                // `@array/items`, because `ListView` built its own
                // `ArrayAdapter` from the `android:entries` attribute in the XML. You wrote
                // no adapter in the code.
                //
                // `.toString()` is redundant for a `String`, but harmless. It becomes
                // necessary the moment you put objects in the list: there `toString()`
                // is the display contract.
                String selected = listView.getItemAtPosition(position).toString();

                // `return true` = "I handled the click". The menu closes and
                // the event no longer circulates. `return false` = "I don't care" —
                // the system tries the default handler.
                //
                // What exactly happens with `return false` on a `PopupMenu`: `PopupMenu`
                // closes the menu anyway, on click. The value propagates to
                // `MenuBuilder.performItemAction`, which, if it is not consumed, continues
                // with the item's default action — for example an `Intent` set on
                // the item. Here the items have no `Intent`, so `false` changes nothing
                // visible. But the contract remains: `true` = handled.
                if (itemId == R.id.action_open) {
                    // `Toast.makeText(...).show()` — two calls. `makeText`
                    // BUILDS, `show()` DISPLAYS. Without `.show()`, nothing happens,
                    // with no error. It is the most frequent mistake at the beginning.
                    // `LENGTH_SHORT` ≈ 2 seconds; `LENGTH_LONG` ≈ 3.5 seconds. The values
                    // are hints, not guarantees: the manufacturer can adjust the duration.
                    Toast.makeText(this, "Open: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_rename) {
                    Toast.makeText(this, "Rename: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_delete) {
                    Toast.makeText(this, "Delete: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                }
                // The final `return false` is dead code — all three ids are
                // covered above. It stays correct: if you add a fourth item
                // in `list_item_menu.xml` and forget to handle it, the click falls nicely into
                // the default handler instead of doing something unpredictable.
                return false;
            });

            // `popup.show()` — up to here you have only configured the menu. Only now does it appear
            // on screen. The order is: build → inflate → register listener → display.
            popup.show();

            // `return true` from the long-press listener — tells the list "the long
            // press was handled". If you returned `false`, the system would consider the
            // long press unhandled and could also trigger a normal click after
            // it. The result: the menu appears and, at the same time, the click action runs.
            //
            // The mechanism behind it: `AdapterView` keeps an internal flag
            // (`mHasPerformedLongPress`). The listener sets it only if it returns
            // `true`. At `ACTION_UP`, if the flag is set, the click is ignored. If not,
            // `performClick()` runs normally.
            //
            // The order matters: `popup.show()` BEFORE `return true`. The reverse is not
            // possible — `return` ends the lambda.
            return true;   // true = long press handled, so the normal click doesn't also fire
        });


        // STEP 6: binding the three components. All three ids must exist
        // in `activity_main.xml`, otherwise you get `null` and a `NullPointerException`
        // on the first call. The order of the three lines does not matter — they are independent.
        // All that matters is that they come after `setContentView`.
        //
        // `toolbar` and `navigationView` are LOCAL, `drawerLayout` is a FIELD.
        // A real inconsistency in the code: all three are used only in `onCreate`.
        // It works with all three local; it works with all three as fields. Pick one
        // variant and stick to it.
        drawerLayout = findViewById(R.id.drawerLayout);
        MaterialToolbar toolbar = findViewById(R.id.topAppBar);
        NavigationView navigationView = findViewById(R.id.navigationView);


        // STEP 7: the drawer listener.
        //
        // What each branch does: it changes the TITLE of the top bar. The contents of the list
        // stay the same — the 20 "Item N" entries. The app is a demonstration of
        // navigation, not of data.
        //
        // `toolbar.setTitle("Inbox")` overwrites `app:title="Inbox"` from the XML.
        // The value in the XML is only the initial one; after the first click, the title comes from the code.
        //
        // `nav_settings` is treated differently — a `Toast`, not a title. It is the only item
        // in the "Other" submenu, so it makes no sense for it to change the screen title.
        //
        // Why `item.getItemId()` and not `item.getTitle()`: the title is visible text,
        // which can be translated or changed. The id is stable. The comparison with `R.id.*`
        // is the only one that survives a language change.
        //
        // What happens if no `if` matches: the listener continues,
        // calls `item.setChecked(true)` and closes the drawer. The unknown item
        // stays checked, but the title does not change. It is not an error — it is a default
        // behaviour.
        //
        // ------------------------------------------------------------------------------
        // METHOD (lambda): onMenuItemClick(item) — the drawer selection
        // THEORY: callback for an item in the `NavigationView`.
        // LOGIC:  1. reads the id; 2. updates the title; 3. sets the check mark;
        //         4. closes the drawer; 5. `return true`.
        // REF:    26.1.13
        // RISK:   without `closeDrawer`, the drawer stays over the screen.
        // ------------------------------------------------------------------------------
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

            // `item.setChecked(true)` — the menu has `android:checkableBehavior="single"`
            // (see 26.6), so it behaves like a group of radio buttons: a single
            // checked item. The explicit call guarantees the state after the drawer
            // closes and after it is reopened.
            //
            // Why `setChecked` is needed explicitly if the menu is already "single":
            // `checkableBehavior` makes the group exclusive, but it does not mean that
            // `NavigationView` marks the item automatically on click. The code does not
            // rely on the default behaviour — it sets it itself. It is a defensive
            // choice, a good one.
            item.setChecked(true);

            // `closeDrawer(GravityCompat.START)` — closes the drawer from the `start` side.
            // It must match `android:layout_gravity="start"` from the XML. If
            // the XML says `start` and the code says `end`, the drawer stays open.
            //
            // Why `setNavigationItemSelectedListener` does NOT close the drawer itself:
            // `NavigationView` is a menu container. It has no reference to
            // `DrawerLayout` and does not know that one exists. They are neighbours in the tree, not
            // parent-child. The listener is only a callback: "item X was pressed".
            // What you do with the information — change the title, close the drawer, start a
            // screen — is your decision, in your code.
            //
            // The practical consequence: if you forget `closeDrawer`, the drawer stays over
            // the screen after the selection. The user sees the changed title but does not see
            // the content. It is the first thing missing from a hasty implementation.
            drawerLayout.closeDrawer(GravityCompat.START);

            // `return true` — tells `NavigationView` that the click was handled. If you
            // return `false`, the item is not marked visually as selected. The documented contract
            // of the old variant (`OnNavigationItemSelectedListener`) is explicit:
            // "true to display the item as the selected item". The new variant
            // (`MenuItem.OnMenuItemClickListener`) propagates the value into `MenuBuilder`,
            // and `NavigationView` uses it the same way.
            //
            // Why the code still calls `setChecked(true)`: because it relies on the
            // contract, not on the implementation. If `NavigationView` changed, the check mark
            // would remain correct.
            return true;
        });

        // STEP 8: the Back button. Why not `@Override public void onBackPressed()`:
        // the method was marked deprecated starting with API 33, and `OnBackPressedDispatcher`
        // is the official mechanism. On top of that, the dispatcher allows SEVERAL
        // callbacks in a chain, each with its own priority — a single override
        // cannot do that.
        //
        // `new OnBackPressedCallback(true)` — the argument is the initial state:
        // `true` = active. A disabled callback receives no events.
        //
        // `addCallback(this, ...)` — the first argument is the `LifecycleOwner` (the activity).
        // The dispatcher keeps the callback only while the activity is in `STARTED`.
        // At `onStop`, the callback is removed automatically; at `onStart`, it comes back. You do not
        // have to remove it manually. The variant without a `LifecycleOwner` leaves the callback in
        // the list until you remove it — if you forget, it holds a reference to the activity.
        //
        // The logic, step by step:
        //   1. Back was pressed.
        //   2. Is the drawer open? → close it. Done. The user stays on the screen.
        //   3. Is the drawer closed? → `setEnabled(false)`, then re-send the event.
        //
        // Why `setEnabled(false)` before re-sending: without it,
        // `onBackPressed()` would enter the SAME callback again, which would see the
        // drawer closed and re-send the event — infinite recursion,
        // `StackOverflowError`. By disabling yourself, you let the next handler
        // in the chain (the default one, which closes the activity) receive the event.
        //
        // The exact mechanism: `OnBackPressedDispatcher` keeps the callbacks in an
        // ordered collection. `onBackPressed()` walks it from the last added to
        // the first and stops at the first ACTIVE callback that handles the event.
        // If your callback re-enters without disabling itself, the walk finds it
        // again. `setEnabled(false)` removes it from the collection of active
        // callbacks, so the walk moves on.
        //
        // What the "default handler" is: `ComponentActivity` registers a fallback
        // that calls `super.onBackPressed()` — that is, `finish()` on the activity. If
        // it did not exist, Back would be ignored.
        //
        // Why not `finish()` directly: `finish()` would close the activity, but it would skip
        // any other callback in the chain (for example a `NavController` that should
        // handle Back first). Delegating keeps the chain intact.
        //
        // ------------------------------------------------------------------------------
        // METHOD: handleOnBackPressed()
        // THEORY: the callback that intercepts Back before the system.
        // LOGIC:  1. if the drawer is open, close it;
        //         2. otherwise disable yourself and delegate the event.
        // REF:    26.1.14
        // RISK:   without `setEnabled(false)`, infinite recursion.
        // ------------------------------------------------------------------------------
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


        // STEP 9: the hamburger. The icon on the left of the bar (the three lines) opens
        // the drawer. The icon already exists in the XML — `app:navigationIcon="@drawable/ic_menu"`.
        // Without a listener, it is purely decorative: it is visible, it can be pressed, nothing happens.
        // The listener is what turns it into a button.
        //
        // `setNavigationOnClickListener` — a single listener for the toolbar's navigation
        // icon. It receives no position or id: it is a single button.
        //
        // Why not `ActionBarDrawerToggle`: the classic variant binds the icon, the drawer
        // and accessibility automatically, but it requires the toolbar to be set as
        // the `ActionBar` (`setSupportActionBar`). Here the toolbar is used as an ordinary
        // view, so the binding is done manually. It is less code, but also less
        // automation — for example, the icon does not animate into an arrow when the drawer is
        // open, and the accessibility description is not updated automatically.
        //
        // `GravityCompat.START` — the same direction as `layout_gravity` in the XML.
        // The fourth occurrence in the file.
        // Hamburger (navigation) icon
        toolbar.setNavigationOnClickListener(v -> {
            drawerLayout.openDrawer(GravityCompat.START);
        });

        // STEP 10: the toolbar menu. The menu is already inflated —
        // `app:menu="@menu/top_app_bar"` from the XML. Here you only react to clicks.
        // If you had used `setSupportActionBar(toolbar)`, you would have overridden
        // `onCreateOptionsMenu` and `onOptionsItemSelected`; with the toolbar as a plain
        // view, this is the right hook.
        //
        // `action_settings` has `app:showAsAction="never"` — that is why it ends up in the
        // "⋮" menu (overflow), not on the bar. `action_search` and `action_share` have
        // `ifRoom` — they appear directly on the bar if they fit.
        //
        // The comment `// open settings` marks an empty spot. The branch displays a
        // `Toast`, but the intention was to open a settings screen. It is a disguised
        // TODO.
        //
        // The final `return false` is dead code — all three ids are covered
        // above. It stays correct: if you add a fourth item to the menu and forget
        // to handle it, the click falls nicely into the default handler instead of throwing
        // an exception.
        //
        // What happens with `return false` on an overflow item: `Toolbar`
        // propagates the value to `MenuBuilder`, which tries the item's default
        // action (an `Intent`, an `ActionProvider`). Here there is neither,
        // so the menu closes and that is all.
        //
        // ------------------------------------------------------------------------------
        // METHOD (lambda): onMenuItemClick(item) — the bar menu
        // THEORY: callback for Search / Share / Settings.
        // LOGIC:  1. reads the id; 2. shows a `Toast`; 3. `return true`.
        // REF:    26.1.16
        // RISK:   `return false` on an unknown id lets the event circulate.
        // ------------------------------------------------------------------------------
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
    }
}
```

**What to remember from this file:** a single `onCreate` with ten steps; the order `super` → `EdgeToEdge` → `setContentView` → `findViewById` is mandatory; `GravityCompat.START` appears four times and must be identical to `layout_gravity` in the XML; `NavigationView` does not close the drawer itself; the Back callback disables itself before delegating.

---

## 26.2 `SecondActivity.java` — dialog and Snackbar

**Careful before anything else:** `SecondActivity` is declared in the manifest, but **it is not started anywhere**. There is no `Intent` in `MainActivity` — only the unused import. The screen is fully functional if you launch it manually (Run → Edit Configurations → Launch: Specified Activity), but in the delivered app it is unreachable. It is a lab screen left unlinked, not a compile bug.

```java
/*
 * ======================================================================================
 * FILE: SecondActivity.java
 * ======================================================================================
 * ROLE:
 *   A lab screen for three things that do not fit in MainActivity:
 *     1. a confirmation dialog built with `AlertDialog.Builder`;
 *     2. a `Snackbar` with an undo action;
 *     3. a view created from code (`new Button`) and added to the tree.
 *
 * WHAT IT DEMONSTRATES:
 *   1. AlertDialog.Builder   — a chain of setters + `show()`.
 *   2. Snackbar.make(...)    — transient feedback with an action button.
 *   3. addButton()           — `new Button(ctx)`, `setId`, `LayoutParams`, `addView`.
 *
 * DEPENDS ON:
 *   - android.app.AlertDialog        → the PLATFORM variant (not AppCompat)
 *   - com.google.android.material    → Snackbar
 *   - android:onClick="btnClick"     → the link from the XML, through reflection
 *
 * WHAT IT DOES NOT DO:
 *   - it is not started from MainActivity (no `Intent` in the whole project);
 *   - it does not save the added buttons across rotation;
 *   - it validates nothing — any click on "Do it!" adds a button.
 *
 * REF: ch. 14 (the section on dialogs), the documentation of `AlertDialog.Builder`,
 *      `Snackbar`, `ViewGroup.LayoutParams`.
 * ======================================================================================
 */

package ro.ase.ie.dma03;

// ======================================================================================
// IMPORT 1: android.app.AlertDialog — CAREFUL, the PLATFORM variant
// ======================================================================================
// WHAT IT IS: the standard dialog of the Android system.
// WHY IT IS A DEBATABLE CHOICE: there is also `androidx.appcompat.app.AlertDialog`.
//   The platform variant uses `android.R.attr.alertDialogTheme` of the current
//   theme; the AppCompat variant forces the library's theme and style. With
//   `Theme.Material3.DayNight.NoActionBar`, the visual difference may be small or
//   nil, but the AppCompat variant is the one that respects the app theme in all
//   cases. Functionally they are identical.
// WHY IT MATTERS ANYWAY: if the app theme were a pure AppCompat one (without
//   Material3), `android.app.AlertDialog` would fall back to the system style — buttons
//   coloured differently, another font, another shadow.
// ======================================================================================
import android.app.AlertDialog;

// ======================================================================================
// IMPORT 2: android.content.DialogInterface — the interface of the dialog buttons
// ======================================================================================
// WHAT IT IS: the interface that contains the dialog's `OnClickListener`.
// WHY IT IS IMPORTED SEPARATELY: `OnClickListener` is an interface NESTED inside it:
//   `DialogInterface.OnClickListener`. Without the import, you would have to write the full name.
// ======================================================================================
import android.content.DialogInterface;

// ======================================================================================
// IMPORT 3: android.os.Bundle — the state saved on recreation
// ======================================================================================
// The signature of `onCreate(Bundle)` requires it. The code never reads it.
// ======================================================================================
import android.os.Bundle;

// ======================================================================================
// IMPORTS 4-5: android.util.DisplayMetrics + android.util.TypedValue
// ======================================================================================
// USED ONLY IN `addButton`, for the 50dp → pixels conversion.
// `DisplayMetrics` = the screen density (how many pixels one dp has).
// `TypedValue.applyDimension` = the conversion itself, for any unit.
// THE RESULT IS DEAD CODE (see 26.2.7). The imports stay because the line that uses
// them exists.
// ======================================================================================
import android.util.DisplayMetrics;
import android.util.TypedValue;

// ======================================================================================
// IMPORTS 6-7: android.view.View + android.view.ViewGroup
// ======================================================================================
// `View` — the type of the parameter in `btnClick(View view)`. The signature is imposed by
//   `android:onClick` in the XML.
// `ViewGroup` — the base class for `LayoutParams`. `ViewGroup.LayoutParams` is
//   the type required by `setLayoutParams`; `LinearLayout.LayoutParams` would be the subtype
//   with `weight`.
// ======================================================================================
import android.view.View;
import android.view.ViewGroup;

// ======================================================================================
// IMPORTS 8-10: android.widget.Button + LinearLayout + Toast
// ======================================================================================
// `Button`        — the widget created from code.
// `LinearLayout`  — the container into which the buttons are added.
// `Toast`         — the cancellation message from the negative button.
// ======================================================================================
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;

// ======================================================================================
// IMPORTS 11-15: androidx.* — the activity infrastructure
// ======================================================================================
// Identical to the ones in MainActivity: EdgeToEdge, AppCompatActivity, Insets,
// ViewCompat, WindowInsetsCompat. The insets block is copied word for word.
// ======================================================================================
import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

// ======================================================================================
// IMPORT 16: com.google.android.material.snackbar.Snackbar
// ======================================================================================
// WHAT IT IS: the feedback bar at the bottom of the screen, with text + an optional action.
// WHY IT COMES FROM MATERIAL: `Snackbar` is not part of the platform. That is why
//   `SecondActivity` needs `libs.material` in the dependencies — just like
//   `MainActivity` for the toolbar.
// WHAT WOULD HAPPEN WITH `Toast`: you would lose the action button. `Toast` has no
//   `setAction`, cannot be closed by the user and has no indefinite duration.
//   For "undo the last action", `Snackbar` is the only option in the platform.
// ======================================================================================
import com.google.android.material.snackbar.Snackbar;

/*
 * ======================================================================================
 * THEORY BLOCK: THREE KINDS OF FEEDBACK AND A VIEW BUILT FROM CODE
 * ======================================================================================
 *
 * 1. DIALOG — BLOCKS, DEMANDS A DECISION
 *    -   `AlertDialog` appears over the screen, in a separate window. The user
 *        must answer before continuing.
 *    -   It is built with `AlertDialog.Builder`: an object that gathers the configuration
 *        (title, message, buttons) and only at `show()` creates the dialog.
 *    -   Every setter returns THE SAME builder → a chain of calls.
 *
 * 2. TOAST — PASSES BY, DEMANDS NOTHING
 *    -   Short text, no action, no layout. It appears and disappears on its own.
 *    -   It does not need a parent view: it is drawn in its own window.
 *
 * 3. SNACKBAR — PASSES BY, BUT CAN BE UNDONE
 *    -   A bar at the bottom of the screen, with text + an optional action button.
 *    -   UNLIKE TOAST, it needs a VIEW: it is inserted into the view tree,
 *        not into a separate window. Hence the second argument
 *        in `make(...)`.
 *    -   With a `CoordinatorLayout` parent, it can be swiped away and
 *        can push a FAB upwards. With a `LinearLayout`, it works, but
 *        without those bonuses.
 *
 * 4. A VIEW BUILT FROM CODE
 *    -   Every widget has a constructor that requires a THEMED `Context`.
 *    -   A view created from code has no id, no `LayoutParams` and is not in the tree.
 *        Three separate operations:
 *          a) `setId(...)`            → so that it can be found with `findViewById`;
 *          b) `setLayoutParams(...)`  → so that the parent knows how to measure it;
 *          c) `parent.addView(...)`   → so that it enters the tree and is drawn.
 *    -   The order matters: `addView` without `LayoutParams` works (the parent
 *        generates some defaults), but `findViewById` without `setId` finds nothing.
 *
 * 5. WHY A VIEW ADDED FROM CODE DISAPPEARS ON ROTATION
 *    -   The view tree is rebuilt from the XML at every recreation.
 *    -   The added button lives only in the old instance of the activity.
 *    -   To survive, it would have to be saved in `savedInstanceState` (a list of
 *        ids/texts) and rebuilt in `onCreate`.
 *
 * REF: ch. 14 (dialogs and Snackbar), the documentation of `AlertDialog.Builder`,
 *      `Snackbar`, `ViewGroup.addView`.
 * ======================================================================================
 */

public class SecondActivity extends AppCompatActivity {

    // ==================================================================================
    // FIELD: inflatedLayout
    // ==================================================================================
    // WHAT IT IS: the root from `activity_second.xml` — a vertical `LinearLayout`.
    // WHY IT IS A FIELD AND NOT A LOCAL: it is used in THREE methods — `onCreate` (initialization),
    //   `btnClick` (Snackbar) and `addButton` (`addView`).
    // WITHOUT `private` — an inconsistency compared to `MainActivity`, where the fields are
    //   `private`. It breaks nothing (we are in the same package), but the convention is `private`.
    // THE NAME IS MISLEADING: it is not a layout "inflated" at runtime, it is the layout from the XML.
    //   The inflation was done by `setContentView`. The name suggests the intention — a container
    //   into which views are added — not the mechanism.
    // ==================================================================================
    LinearLayout inflatedLayout;

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: onCreate(Bundle savedInstanceState)
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   The creation callback. This is where `activity_second.xml` is inflated and the
     *   reference to the container into which the buttons will be added is obtained.
     *
     * LOGIC:
     *   1. `super.onCreate` — the parent.
     *   2. `EdgeToEdge.enable` — drawing under the bars.
     *   3. `setContentView` — inflates the layout.
     *   4. insets on `R.id.main` — padding for the system bars.
     *   5. `inflatedLayout = findViewById(R.id.main)` — the reference to the container.
     *
     * REF: ch. 14, the documentation of `Activity#onCreate`.
     *
     * RISK:
     *   - `inflatedLayout` initialized before `setContentView` → `null`, then
     *     `NullPointerException` on the first `addView`.
     * ----------------------------------------------------------------------------------
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_second);

        // The insets block is IDENTICAL to the one in MainActivity — copied. Here
        // `R.id.main` is on the root `LinearLayout`, not on a `CoordinatorLayout`.
        // It works the same way: padding on the root, the children move into the safe area.
        //
        // Why it is copied and not extracted into a utility function: in a lab
        // project, copying is acceptable. In a real application, you would have a function
        // `applyInsets(View root)` in a utility class — or you would use
        // `ViewCompat.setOnApplyWindowInsetsListener` once, in a base
        // class.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // The LAST line — after `setContentView`. If it came before, it would receive `null`
        // and the first `addView` would throw `NullPointerException`.
        //
        // What `findViewById(R.id.main)` does here: it searches the tree of
        // `activity_second.xml`. The id `main` also exists in `activity_main.xml`, but
        // the two layouts never coexist in the same tree — each
        // activity has its own window. It is not a collision.
        inflatedLayout = findViewById(R.id.main);
    }

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: btnClick(View view)
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   A public method, with a fixed signature, called through REFLECTION by the platform when
     *   the button with `android:onClick="btnClick"` from the XML is pressed. There is no
     *   `setOnClickListener` anywhere in the code — the whole link is in the XML.
     *
     * LOGIC:
     *   1. Creates an `AlertDialog.Builder` with the activity context.
     *   2. Chains: title → message → cancelable → positive button → negative button.
     *   3. In the positive button: `addButton()` returns the id of the new button.
     *   4. Shows a `Snackbar` with the "Cancel" action, which deletes the button by id.
     *   5. In the negative button: only a `Toast`.
     *   6. `builder.show()` — only here does the dialog appear on screen.
     *
     * REF:
     *   ch. 14 (the section on dialogs), the documentation of `android:onClick`,
     *   `AlertDialog.Builder`, `Snackbar.make`.
     *
     * RISK:
     *   - the method made `private` → it compiles, but on click:
     *     `IllegalStateException: Could not find method btnClick(View) ...`
     *   - the parameter changed from `View` to another type → the same exception, at runtime.
     *   - `builder.show()` forgotten → the dialog is built and never displayed.
     * ----------------------------------------------------------------------------------
     */
    public void btnClick(View view) {
        // The signature is IMPOSED by the XML. In `activity_second.xml`, the button has
        // `android:onClick="btnClick"`. At runtime, Android looks, through reflection, for a
        // method `public void btnClick(View)` in the activity context.
        //
        // THE CONSEQUENCE: if you make it `private`, or change its parameter to `Object`,
        // or rename it without modifying the XML, COMPILATION PASSES. The error appears
        // on click: `IllegalStateException: Could not find method btnClick(View) in a
        // parent or ancestor Context`. One of the few places in Android where
        // the mistake is not visible at build time.
        //
        // `view` is the pressed button. It is not used here — the code does not need to know
        // which button it was. But the parameter is mandatory: reflection looks for exactly
        // the signature with a `View`.
        //
        // Why `public` and not `protected`: reflection looks for public methods.
        // `protected` or package-private are not found from the `View` that makes
        // the call (another package).
        //
        // THE MODERN ALTERNATIVE: `setOnClickListener` in `onCreate`. It is safer
        // (the compiler checks), but more verbose. `android:onClick` is accepted
        // for demonstrations; Google considers it outdated for new code.

        // `AlertDialog.Builder` — builds the dialog piece by piece. Every
        // setter returns THE SAME builder, that is why they can be chained. The chain
        // ends with `setNegativeButton`, and `builder.show()` at the end of the method
        // displays the dialog.
        //
        // Why the chain works: `setTitle`, `setMessage`, `setCancelable`,
        // `setPositiveButton`, `setNegativeButton` all have `return this;` in
        // their implementation. It is not magic — it is the "fluent builder" convention.
        //
        // `SecondActivity.this` and not `this`: inside a listener, `this` would
        // mean the listener. `SecondActivity.this` is the syntax for the instance of the
        // outer class. Here we are still in the body of the method, so `this` would have worked —
        // but the explicit form is a good habit, because in two steps you will be in
        // `onClick`.
        AlertDialog.Builder builder = new AlertDialog.Builder(SecondActivity.this);
        builder.setTitle("Add new control ...")
                .setMessage("Are you sure you want to add a new control?")

                // `setCancelable(true)` is the default value. Written explicitly,
                // it documents the behaviour: it can be closed with Back or with a tap
                // outside. The consequence: if the user closes it that way, NO button
                // runs — neither "Do it!" nor "Cancel". If you need a guaranteed
                // action, you need `setOnCancelListener`.
                //
                // With `setCancelable(false)`, the dialog can no longer be closed except
                // through the two buttons. For a critical confirmation that is the correct
                // choice; for an ordinary one, it annoys the user.
                .setCancelable(true)

                // The positive button is the main action — it appears on the right, coloured.
                // The text "Do it!" is explicit; "OK" would be vague.
                //
                // `which` is `DialogInterface.BUTTON_POSITIVE` here. It is not used —
                // each button has its own listener. If you had a single listener
                // for all the buttons, `which` would be the only way to tell them apart.
                //
                // Why the listener is an anonymous class and not a lambda:
                // `DialogInterface.OnClickListener` has a single abstract method,
                // so a lambda would work too (`(dialog, which) -> { ... }`). The code
                // chooses the old form, from the Java 7 generation. Both compile; a lambda
                // is shorter.
                .setPositiveButton("Do it!", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        // Creates the button BEFORE the Snackbar, so that you have something to delete.
                        // The returned id is the ONLY link to the new button: you have no
                        // reference to the object, only a number.
                        int id = addButton();

                        // `Snackbar.make(context, view, text, duration)` — four arguments:
                        //   context  : SecondActivity.this — for the theme and resources
                        //   view     : inflatedLayout — the reference view
                        //   text     : "Cancel previous action."
                        //   duration : Snackbar.LENGTH_LONG ≈ 2.75 s
                        //
                        // WHY the second argument must be a VIEW: `Snackbar`
                        // is not a separate window like the `Toast`. It is an ordinary view,
                        // added to the existing tree. To know where to add it,
                        // it needs a starting point: it starts from the given view
                        // and walks up through the parents until it finds a `CoordinatorLayout` or
                        // `android.R.id.content`. Without a `View`, it has nowhere to
                        // start from — that is why there is no
                        // `make(Context, String, int)` overload.
                        //
                        // What exactly happens with `inflatedLayout`: it is a plain
                        // `LinearLayout`. `Snackbar` walks up from it to `android.R.id.content`
                        // (the window container) and adds its bar there. The result:
                        // the bar appears at the bottom, over the content.
                        //
                        // What you would gain with a `CoordinatorLayout`: `SwipeDismissBehavior`
                        // (you swipe to close it) and the coordination with a
                        // `FloatingActionButton` (the FAB moves up while the
                        // Snackbar is visible). Here there is no FAB, so the difference is
                        // only the swipe.
                        Snackbar.make(SecondActivity.this, inflatedLayout, "Cancel previous action.", Snackbar.LENGTH_LONG)

                                // `setAction("Cancel", listener)` — adds the button on the
                                // right. The text is short on purpose: an "Undo last
                                // action" would crowd the message on small screens.
                                //
                                // The text and the label are both "Cancel" — an unfortunate
                                // naming choice. The message "Cancel previous action."
                                // says what happened; the button "Cancel" should
                                // be "Undo", because it UNDOES the addition, not cancels
                                // the Snackbar. Functionally, the button deletes the added button.
                                .setAction("Cancel", new View.OnClickListener() {
                                    @Override
                                    public void onClick(View v) {
                                        // `id` is captured from the outer lambda. It is an
                                        // `int` local variable, assigned a single
                                        // time → effectively final → it can be captured.
                                        // If you wrote `id++` between the declaration and
                                        // the use, the compiler would refuse the capture.
                                        //
                                        // `inflatedLayout.findViewById(id)` — works
                                        // because the button received an explicit id with
                                        // `setId(counter)`. Without `setId`, `findViewById`
                                        // would return `null` and `removeView(null)` would
                                        // throw `NullPointerException`.
                                        Button viewById = inflatedLayout.findViewById(id);

                                        // `removeView(viewById)` — removes the view from the
                                        // container. The button disappears from the screen; the object
                                        // stays in memory until the next garbage
                                        // collection.
                                        inflatedLayout.removeView(viewById);
                                    }
                                }).show();
                        // `.show()` at the end — without it, the Snackbar is built and
                        // never displayed. The same trap as with `Toast`.
                        //
                        // The moment of display: the Snackbar is created INSIDE the `onClick` of the
                        // positive button, so it appears after the dialog has closed.
                        // If you created it before `builder.show()`, it would appear under
                        // the dialog.
                        //
                        // The `LENGTH_LONG` duration: ~2.75 seconds (the values in
                        // `SnackbarManager`: 1,500 ms for `SHORT`, 2,750 ms for
                        // `LONG`). Enough for the user to press "Cancel".
                        // `LENGTH_INDEFINITE` would keep the bar until an action or a
                        // swipe — too aggressive for a confirmation.

                    }
                })

                // The negative button — cancel. Only a `Toast`, no state change.
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        Toast.makeText(SecondActivity.this, "Object creation cancelled", Toast.LENGTH_LONG).show();
                    }
                });

        // `builder.show()` — creates the dialog and displays it. Equivalent to
        // `builder.create().show()`. It is called ONCE, after the chain of
        // setters has ended.
        //
        // Why `show()` is separate and not in the chain: because the chain ends with `;`
        // after `setNegativeButton`, and `show()` is a method of the builder, not a
        // setter. `builder.setTitle(...).show()` would have worked too, but the code chooses the
        // explicit form.
        //
        // What happens if you call `show()` twice: two dialogs are created,
        // both displayed. The second appears over the first. It is not an exception — just a visual
        // bug.
        //
        // What happens if you call a setter after `show()`: it has no effect on the
        // displayed dialog. The builder copies the values into the dialog at `create()`;
        // after that, the setters modify only the builder, not the live dialog.
        builder.show();
    }


    // ==================================================================================
    // FIELD: counter
    // ==================================================================================
    // DECLARED BETWEEN METHODS — legal in Java, unusual as style.
    // TWO ROLES AT ONCE: id generator and source for the label.
    // WHY NOT `static`: it would be shared between instances. On recreation, the new activity
    //   would continue from the old value — ids that do not repeat, but also a counter
    //   that grows to infinity. Here `counter` is per instance, so it resets on
    //   rotation.
    // ==================================================================================
    int counter = 0;

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: addButton()
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   A view built from code is an ordinary Java object until you add it to a
     *   parent. It needs three things to be useful:
     *     1. a THEMED CONTEXT (the constructor);
     *     2. an ID (so that it can be found again);
     *     3. LayoutParams (so that the parent knows how to measure it).
     *
     * LOGIC:
     *   1. Converts 50dp to pixels (the result is ignored — dead code).
     *   2. Creates `new Button(SecondActivity.this)`.
     *   3. Sets the text with pre-increment: "Button_1", "Button_2", ...
     *   4. Sets the id = counter (1, 2, 3, ...).
     *   5. Creates `ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)`.
     *   6. `addView(newBtn)` — adds it at the end of the `LinearLayout`.
     *   7. Returns the id, so that the caller can delete the button.
     *
     * REF:
     *   ch. 14 (the section on dynamic views), the documentation of `View#setId`,
     *   `ViewGroup.LayoutParams`, `ViewGroup#addView`.
     *
     * RISK:
     *   - application context instead of activity → you lose the theme;
     *   - `setId` forgotten → the button cannot be found and deleted;
     *   - `counter` not saved → on rotation the buttons disappear and the ids repeat.
     * ----------------------------------------------------------------------------------
     */
    public int addButton()
    {
        // DEAD CODE. `hPixels` is computed and NEVER used. The intention was probably
        // `newBtn.setHeight(hPixels)` or a `LayoutParams` with a 50dp height.
        // The compiler gives a warning (`variable hPixels is never used`), not an error.
        //
        // What it does anyway, useful to know: `TypedValue.applyDimension(COMPLEX_UNIT_DIP,
        // 50, metrics)` converts 50dp into physical pixels, using the screen
        // density. At 3x, it returns 150. It is the correct conversion when you need
        // pixels in a calculation — for example for animations or for `setPadding`.
        //
        // Why not `50 * getResources().getDisplayMetrics().density`: it is equivalent,
        // but `applyDimension` also handles `SP`, `PT`, `MM`, `IN` with the same
        // signature. One function, all the units.
        //
        // Why `DisplayMetrics` is obtained only once:
        // `getResources().getDisplayMetrics()` returns the object of the current
        // configuration. Called several times, it returns the same object. It is not an expensive
        // operation, but it is pointless to repeat it.
        DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
        int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50,
                displayMetrics);

        // `new Button(Context)` — the constructor requires a THEMED CONTEXT.
        // `SecondActivity.this` has the `Theme.DMA03` theme. If you passed
        // `getApplicationContext()`, the button would lose the theme and, on some Material
        // attributes, would throw an exception at inflate.
        //
        // Why `new Button(ctx)` and not `LayoutInflater.from(ctx).inflate(...)`:
        // for a simple button, the constructor is more direct. The inflater makes sense
        // when you want a whole XML layout, with styles and children.
        Button newBtn = new Button(SecondActivity.this);

        // `++counter` (pre-increment) — increments first, then uses. The first
        // button is `Button_1`, and `counter` becomes 1. With `counter++` (post-increment),
        // the first would be `Button_0` and you would have a button with id 0.
        newBtn.setText("Button_" + (++counter));

        // `setId(counter)` — ids 1, 2, 3... The resource ids are in the
        // `0x7f......` range, so they do not collide. `View.NO_ID` is `-1`, so 0 would have been
        // an unfortunate value — one more reason for the pre-increment.
        //
        // WITHOUT `setId`, the button exists but is impossible to find with `findViewById`.
        // It would appear on screen and you could no longer delete it.
        //
        // Why small ids are safe: `findViewById` searches by the integer
        // value. An id of 1 does not collide with `R.id.button` (which is `0x7f0b....`).
        // The only requirement is that it be unique in the subtree you search in.
        //
        // THE MODERN ALTERNATIVE: `View.generateViewId()` returns a unique, guaranteed id.
        // It would be safer if you had several sources of ids. Here `counter` is
        // enough.
        newBtn.setId(counter);

        // `ViewGroup.LayoutParams` — the base class. `LinearLayout` accepts it. If you
        // need `layout_weight`, you must use `LinearLayout.LayoutParams` — the base
        // class does not have that field.
        //
        // `MATCH_PARENT` on the width — the button fills the container, like the original button
        // from the XML. `WRAP_CONTENT` on the height — as much as the text needs.
        //
        // What the two constants mean: `MATCH_PARENT` = `-1` (fills the parent),
        // `WRAP_CONTENT` = `-2` (as much as the content). They are negative values on purpose,
        // so that they are not confused with real dimensions in pixels.
        //
        // WITHOUT `setLayoutParams`, `addView` applies the container's default
        // values — also `MATCH_PARENT`/`WRAP_CONTENT` for `LinearLayout`,
        // so practically the same result. Explicit is safer when the container
        // changes.
        //
        // What happens if you pass `LinearLayout.LayoutParams`: it works even
        // better — the parent no longer has to convert.
        // `ViewGroup.LayoutParams` is accepted because
        // `LinearLayout.generateLayoutParams(ViewGroup.LayoutParams)` knows how to
        // wrap it.
        ViewGroup.LayoutParams layoutParams =
                new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT);
        newBtn.setLayoutParams(layoutParams);

        // `addView` — adds at the end of the vertical `LinearLayout`, so below the
        // existing button. The second button appears below the first, the third below the second.
        //
        // `addView` has two effects: it attaches the view to the tree and triggers a
        // layout request (`requestLayout`). The button appears immediately, without you doing
        // anything else.
        inflatedLayout.addView(newBtn);

        // `return counter` — the id just assigned. The caller keeps it in `id` and
        // uses it in the Snackbar action.
        //
        // What happens on rotation: `counter` resets to 0, and the added buttons
        // disappear — they are not saved in `savedInstanceState`. On rotation,
        // the activity is recreated, `onCreate` runs again, and
        // `activity_second.xml` once again has a single button.
        //
        // Why the ids reset too: if you added buttons again after rotation,
        // the first would again receive id 1. It collides with nothing, because the old
        // buttons disappeared together with the tree.
        return counter;
    }
}
```

**What to remember from this file:** `android:onClick` requires `public void btnClick(View)`; `AlertDialog.Builder` chains, and `show()` is mandatory; `Snackbar.make` requires a `View` because it is inserted into the tree; a view created from code needs a themed context, `setId` and `LayoutParams`; `SecondActivity` is not started anywhere.

---

## 26.3 `AndroidManifest.xml`

The file that declares the app and the two activities. Without the manifest entry, an activity does not exist for the system — even if the `.java` file compiles.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FILE: AndroidManifest.xml
  ======================================================================================
  ROLE:
    Declares the app and the two activities. Without the manifest entry, an
    activity does not exist for the system — even if the .java file compiles.

  WHAT IT DEMONSTRATES:
    1. `android:exported` — who can start the activity.
    2. `intent-filter` MAIN + LAUNCHER — who appears in the launcher.
    3. `android:supportsRtl` — why `layout_gravity="start"` mirrors.

  REF: ch. 01 (setup and skeleton), the documentation of `<manifest>`, `<activity>`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <manifest>
  ======================================================================================
  `xmlns:android` — the namespace of the platform attributes. Without it, `android:name`
    is not recognised.
  `xmlns:tools` — the namespace of the design-time attributes. DECLARED BUT UNUSED:
    no `tools:*` attribute in the file. A leftover from the template. It breaks nothing, but lint
    flags it.
  WITHOUT `<uses-permission>` — the app needs nothing. Neither internet nor
    storage. All the data is in memory.
  ======================================================================================
-->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!--
      ==================================================================================
      ELEMENT: <application>
      ==================================================================================
      A single element per app. All the activities, services and receivers
      are its children.

      ATTRIBUTES:
      `allowBackup="true"` — the app takes part in the system's automatic backup.
        For an app with no persistent data, it is irrelevant.
      `dataExtractionRules` (API 31+) and `fullBackupContent` (below API 31) — files
        that say what is saved. Both point to `res/xml/`. If one is missing,
        the build passes, but lint warns.
      `icon` and `roundIcon` — two different resources for the launcher: the square icon
        and the round one. Some launchers use the round shape, others mask
        the square one.
      `label="@string/app_name"` — the app name, from `strings.xml` (`DMA03`).
        It is not literal text, so it can be translated.
      `supportsRtl="true"` — the interface mirrors in RTL languages. Hence
        the importance of `GravityCompat.START` instead of `Gravity.LEFT`. Without this
        attribute, `start` would behave like `left` even in Arabic.
      `theme="@style/Theme.DMA03"` — the theme applies to ALL activities that do not have
        their own `android:theme`. Both inherit it. The chain is `Theme.DMA03` →
        `Base.Theme.DMA03` → `Theme.Material3.DayNight.NoActionBar`.

      WHY `NoActionBar` IN THE THEME NAME: the app draws its own bar, with
        `MaterialToolbar`. If the theme had an `ActionBar`, you would see two overlapping
        bars — one from the system, one yours.
      ==================================================================================
    -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA03">

        <!--
          ==============================================================================
          ELEMENT: <activity> MainActivity
          ==============================================================================
          `.MainActivity` — the leading dot means "in the app package",
            that is, `ro.ase.ie.dma03.MainActivity`. The full form would be identical.
          `exported="true"` — mandatory for the component with an `intent-filter` from
            API 31 onwards. Without it, the build FAILS. It is the only activity that
            can be started from outside — by the launcher.
          `windowSoftInputMode="adjustResize"` — when the keyboard appears, the window
            shrinks, it does not pan. Here there is no `EditText`, so the
            attribute is useless — but it is harmless and prepares the ground for a
            screen with fields.
          `adjustResize` vs `adjustPan`: `adjustResize` shrinks the window and lets
            the content rearrange itself; `adjustPan` moves the window up to keep
            the field visible. For forms, `adjustResize` is almost always the correct
            choice.
          ==============================================================================
        -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!--
              ==========================================================================
              ELEMENT: <intent-filter> MAIN + LAUNCHER
              ==========================================================================
              The pair that creates the icon in the launcher.
              `MAIN` = the entry point; `LAUNCHER` = it appears in the app list.
              Both are necessary.
              Only `MAIN`: the app does not appear in the launcher, but it can be started
                explicitly with an `Intent`.
              Only `LAUNCHER`: it is not recognised as an entry point, so it still does not appear.
              ==========================================================================
            -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!--
          ==============================================================================
          ELEMENT: <activity> SecondActivity
          ==============================================================================
          `exported="false"` — no app from outside can start it. Correct: it is
            an internal screen.
          WITHOUT an `intent-filter` — it has no entry point. It does not appear in the launcher.

          HERE IS THE FINAL PROOF: `SecondActivity` is declared, but NOTHING starts it.
            `MainActivity` contains no `Intent`. The screen is a lab left
            unlinked — complete code, accessible only if you launch it manually from Android
            Studio.

          WHAT WOULD HAVE BEEN NEEDED TO LINK IT: in `MainActivity`, a
            `startActivity(new Intent(this, SecondActivity.class))` — for example in
            the `nav_settings` branch or on `action_open` in the context menu.
            The `android.content.Intent` import already exists, a sign that the intention was
            there.

          WHY `exported="false"` DOES NOT PREVENT THE MANUAL LAUNCH FROM THE IDE: Android
            Studio installs the app in debug mode and starts the activity with the app's
            debug privileges, not as a foreign app.
            The `exported` restriction applies to other apps, not to the app itself.
          ==============================================================================
        -->
        <activity
            android:name=".SecondActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**What to remember from this file:** `exported="true"` + `MAIN`/`LAUNCHER` = the start screen; `SecondActivity` is declared, but unlinked; `supportsRtl="true"` is the reason why `start` mirrors.

---

## 26.4 `activity_main.xml` — the container hierarchy

Six nested containers, each with a single responsibility. The block below is the whole file, in source order.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FILE: activity_main.xml
  ======================================================================================
  ROLE:
    Builds the main screen from six nested containers. Each has a
    single responsibility; together they produce the drawer + app bar + list effect.

  WHAT IT DEMONSTRATES:
    1. DrawerLayout with exactly two children: content + drawer.
    2. CoordinatorLayout that coordinates AppBarLayout with the list.
    3. MaterialToolbar with title, hamburger and menu.
    4. NavigationView with `layout_gravity="start"` (RTL-safe).

  REF: ch. 14 (section 14.1), the documentation of `DrawerLayout`, `CoordinatorLayout`,
       `AppBarLayout`, `NavigationView`.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: HOW AN ANDROID SCREEN IS DRAWN
  ======================================================================================
  1. THE VIEW TREE
     Every screen is a tree: a root `ViewGroup` with children, which can in turn be
     `ViewGroup`s.
     `View` = something that is drawn (text, image, button).
     `ViewGroup` = something that contains other views and positions them.

  2. THE THREE PHASES
     MEASURE: every view calculates its desired size, based on
       `LayoutParams` and on the space offered by the parent.
     LAYOUT: the parent decides the position (left, top) of every child.
     DRAW: every view draws itself on the canvas.
     The three phases repeat at every `requestLayout()` — for example when you add
     a button with `addView`.

  3. `match_parent` vs `wrap_content`
     `match_parent` (`-1`): "fill all the parent's space".
     `wrap_content` (`-2`): "as much as I need to show my content".
     They are special values, not dimensions in pixels.

  4. WHY THE CONTAINERS ARE NESTED
     Each `ViewGroup` adds A SINGLE behaviour:
       DrawerLayout      → lateral sliding;
       CoordinatorLayout → coordination between children (app bar + scroll);
       AppBarLayout      → collapse on scroll;
       FrameLayout       → simple overlap, no positioning;
       LinearLayout      → stacking.
     A single container cannot do all the behaviours. You compose them.

  5. WHY A `FrameLayout` BETWEEN `CoordinatorLayout` AND `ListView`
     `CoordinatorLayout` applies a `Behavior` to the DIRECT CHILD.
     `ListView` could itself be the direct child, but the `FrameLayout` isolates
     the behaviour and leaves room for a FAB or an "empty list" `TextView` in
     the future.

  REF: the documentation of `View`, `ViewGroup`, `View.MeasureSpec`, `CoordinatorLayout`.
  ======================================================================================
-->

<!--
  ======================================================================================
  THE TREE, BY LEVELS — AND EACH ONE'S RESPONSIBILITY
  ======================================================================================
  DrawerLayout (id=drawerLayout)          ← knows how to slide a panel over the content;
  │                                          it draws nothing itself;
  │                                          it keeps track of the "open/closed" state
  ├── CoordinatorLayout (id=main)         ← the content panel (the first child);
  │   │                                      coordinates the behaviours of the children
  │   ├── AppBarLayout                    ← holds the bar; knows how to rise on scroll
  │   │   └── MaterialToolbar (topAppBar) ← title, hamburger, menu, clicks
  │   │
  │   └── FrameLayout                     ← support for `layout_behavior`;
  │       │                                  isolates the list from CoordinatorLayout
  │       └── ListView (listView)         ← 20 rows from @array/items;
  │                                          receives the long press
  │
  └── NavigationView (navigationView)     ← the drawer: menu + icons + its own
                                             insets; slides in from `start`

  THE TABLE OF RESPONSIBILITIES:
  Level 1  DrawerLayout        slides the drawer over the content
  Level 2  CoordinatorLayout   coordinates AppBarLayout with the list
  Level 3  AppBarLayout        holds the bar and applies liftOnScroll
  Level 4  MaterialToolbar     title, hamburger, menu
  Level 5  FrameLayout         applies layout_behavior to the list
  Level 6  ListView            displays the rows

  WHAT BREAKS IF A LEVEL IS MISSING:
  DrawerLayout     → there is no drawer;
  CoordinatorLayout → the bar does not react to scroll;
  AppBarLayout     → the bar does not rise, does not collapse;
  MaterialToolbar  → the screen has no bar;
  FrameLayout      → the list is drawn under the bar;
  ListView         → the screen is empty.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: DrawerLayout (the root)
  ======================================================================================
  `@+id/drawerLayout` — the `+` sign means "create the id if it does not exist". The first
    occurrence in an XML file must have `+`; in the code you use
    `R.id.drawerLayout` without it.
  `match_parent` x 2 — the container covers the whole screen, including the areas under the bars.
    `EdgeToEdge` only makes sense this way: the content stretches, and the insets padding
    keeps it in the safe area.
  `xmlns:app` — the namespace for the attributes defined by libraries (`app:menu`,
    `app:title`). Without it, `app:menu` is not recognised.

  WHY `DrawerLayout` IS THE ROOT AND NOT `CoordinatorLayout`: because the drawer
    must cover the WHOLE screen, including the bar. If `DrawerLayout` were a child
    of `CoordinatorLayout`, the drawer would be pushed by the bar and would start below it.
  ======================================================================================
-->
<androidx.drawerlayout.widget.DrawerLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/drawerLayout"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

<!--
  ======================================================================================
  THE `DrawerLayout` RULE: EXACTLY TWO CHILDREN
  ======================================================================================
  THE CANONICAL RULE: exactly TWO direct children.
    1. The FIRST child — the content. Any `ViewGroup`; here `CoordinatorLayout`.
       It fills all the space.
    2. The SECOND child — the drawer. Here `NavigationView`. It must have
       `android:layout_gravity="start"` (or `end`).

  WHAT "EXACTLY" MEANS TECHNICALLY: `DrawerLayout` accepts more children, but the
    contract is: ONE content + AT MOST one drawer on each edge. You can have a
    `start` drawer and an `end` one at the same time. You cannot have two on the same edge —
    `IllegalStateException` at inflate: "Child drawer has absolute gravity ... but
    this DrawerLayout already has a drawer view along that edge".

  HOW `DrawerLayout` DECIDES WHICH ONE IS THE DRAWER: by `android:layout_gravity`. A child
    without gravity (or with `top`/`bottom`) is treated as CONTENT and drawn over
    the others, across the whole screen. That is why a `NavigationView` without `layout_gravity` would
    cover the screen and would never open.

  WHY THE ORDER MATTERS: the first child is the content by contract and by the drawing
    order. Children are drawn in the XML order, so the drawer (the second) is
    drawn over the content. If you put the drawer first, it would be drawn first
    and the content would cover it — although `DrawerLayout` would still treat it as a drawer,
    because it has gravity.

  WHAT HAPPENS IF YOU PUT A THIRD CHILD WITHOUT GRAVITY: it is treated as the second
    content panel, drawn over the first, across the whole screen. The build passes; the screen
    looks as if the content had been replaced. A bug that is hard to diagnose,
    because the XML is valid.

  WHY `DrawerLayout` IS NOT AN ORDINARY `ViewGroup`: it has its own logic for
    intercepting gestures (`onInterceptTouchEvent`), for measuring the drawer and
    for animation. That is why it cannot be replaced with a `FrameLayout` + `TranslationX`
    written by hand without a lot of code.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: CoordinatorLayout (the content panel)
  ======================================================================================
  `xmlns:android` and `xmlns:app` are declared AGAIN — although they are already on
    `DrawerLayout`. Redundant, but legal: namespaces are inherited, and
    redeclaring them is ignored. It breaks nothing; some editors add them automatically.
  `@+id/main` — this is where `findViewById(R.id.main)` from the code comes from, for the insets.
    The id is on the CONTENT, not on the `DrawerLayout` — so the insets padding does not touch
    the drawer.
  `match_parent` x 2 — the content fills the space left after `DrawerLayout` measures it.
    In practice, the whole screen.

  WHY `CoordinatorLayout` AND NOT DIRECTLY `FrameLayout`: it coordinates `AppBarLayout`
    with the list — the `liftOnScroll` effect needs it. Without `CoordinatorLayout`,
    the bar does not know when the list scrolls.

  WHAT IT DOES CONCRETELY: it keeps a `Behavior` for every direct child. `AppBarLayout`
    has a `Behavior` that listens to scroll; the `FrameLayout` with
    `app:layout_behavior="@string/appbar_scrolling_view_behavior"` has one that is
    pushed down by the height of the bar. Without the coordinator, the two do not communicate.
  ======================================================================================
-->
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!--
      ================================================================================
      ELEMENT: AppBarLayout (the top bar)
      ================================================================================
      A vertical `LinearLayout` with a single purpose: to hold the bar and apply the
      scroll behaviours to it. It does not have to contain only a toolbar; it can
      also contain a `TabLayout`.

      ATTRIBUTES:
      `wrap_content` on the height — the bar has the height of the child
        (`?attr/actionBarSize`). `match_parent` would stretch it across the whole screen.
      `#6750A4` — the base Material 3 purple, HARDCODED. It does not adapt to dark mode:
        in the dark the bar stays light purple. The correct value would be `?attr/colorPrimary`.
      `liftOnScroll="true"` — when the list scrolls, the bar changes its colour to
        `liftOnScrollColor` (#4F378B, also hardcoded) and receives a shadow. It is the
        "app bar that rises" effect.
      `liftOnScrollColor` — the destination colour of the transition. Without it, the transition
        would use a colour derived from the theme.
      `liftOnScrollTargetViewId="@id/listView"` — tells `AppBarLayout` WHICH
        view scrolls. Without it, `AppBarLayout` tries to detect the scrollable view
        itself; when the view is nested (here the `ListView` is in a `FrameLayout`),
        the detection can pick another view or produce flicker. The explicit id
        removes the ambiguity — it is the recommendation from the Material documentation for
        nested scrollable views.
      `@id/listView` and not `@+id/listView`: the id is already created by `ListView`, which
        appears further down in the same file. `@+id` would create a new id, and the reference would
        point to something else (or would give a duplicate error).

      HOW "LIFT ON SCROLL" WORKS IN SHORT: `AppBarLayout` listens to the scroll
        events of the target view. When it receives a scroll down, it animates the background
        towards `liftOnScrollColor` and adds a shadow; when it reaches the top, it returns.
        It is a colour transition, not a height change.
      ================================================================================
    -->
    <com.google.android.material.appbar.AppBarLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#6750A4"
        app:liftOnScroll="true"
        app:liftOnScrollColor="#4F378B"
        app:liftOnScrollTargetViewId="@id/listView">

        <!--
          ==============================================================================
          ELEMENT: MaterialToolbar
          ==============================================================================
          `?attr/actionBarSize` — the standard bar height (56dp). Do not hardcode
            `56dp`: on some themes and orientations it differs.
          `android:background="@android:color/transparent"` — the toolbar is
            transparent, the colour comes from `AppBarLayout`. Otherwise you would have two layers
            of purple, and `liftOnScroll` would change only one.
          `app:title="Inbox"` — the initial title. The code overwrites it with
            `toolbar.setTitle(...)` on a drawer click.
          `app:titleTextColor` and `app:navigationIconTint` — white. Without them, the text would
            be black on purple in the light theme. `navigationIconTint` is needed separately
            because the vector icon has its own colour (#000000 in
            `ic_menu.xml`).
          `app:navigationIcon="@drawable/ic_menu"` — the three lines. The drawing is a
            24dp `VectorDrawable`; the real colour is given by `navigationIconTint`.
          `app:menu="@menu/top_app_bar"` — inflates the menu directly from the XML. That is why
            `onCreate` has no `onCreateOptionsMenu`.
          `app:theme="@style/ThemeOverlay.Material3.Dark.ActionBar"` — applies a dark
            theme ONLY to the toolbar, so that the text and icons are light.
            The alternative would have been to set each colour individually.
          `app:theme` and not `android:theme`: `app:theme` is read by `Toolbar` and
            applied only to its subtree. `android:theme` would change the theme of the whole
            window.
          `app:` everywhere and not `android:`: the attributes `title`, `titleTextColor`,
            `navigationIcon`, `menu`, `layout_scrollFlags` are defined by libraries
            (AppCompat/Material), not by the platform. With `android:` they would be ignored or would
            have another meaning.

          `app:layout_scrollFlags="scroll|enterAlways|snap"` — the behaviour on
            scrolling:
              scroll       → the bar leaves the screen when you scroll down;
              enterAlways  → it comes back as soon as you scroll up, wherever you are in the list;
              snap         → it stops completely visible or completely hidden, never
                             halfway.

          WHAT HAPPENS IF YOU REMOVE `app:menu`: the bar is left without
            Search/Share/Settings, and `toolbar.setOnMenuItemClickListener` is never
            called again. It is not an error — just a dead listener.
          WHAT HAPPENS IF YOU REMOVE `app:navigationIcon`: the hamburger disappears, and
            `setNavigationOnClickListener` has nothing to press. The drawer stays
            accessible only through the swipe gesture from the edge of the screen.
          ==============================================================================
        -->
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

    </com.google.android.material.appbar.AppBarLayout>

    <!--
      ================================================================================
      ELEMENT: FrameLayout + ListView
      ================================================================================
      `app:layout_behavior="@string/appbar_scrolling_view_behavior"` — without it,
        the `FrameLayout` would be drawn from `y=0`, that is UNDER the bar, and the first
        rows would be covered. The behaviour pushes it down by exactly the height of
        the bar.
      Why it is a string and not a class: `app:layout_behavior` accepts the full name
        of the `Behavior` class. `@string/appbar_scrolling_view_behavior` is an alias
        defined by Material for
        `com.google.android.material.appbar.AppBarLayout$ScrollingViewBehavior`. This way
        you do not depend on the internal name of the class.

      `android:entries="@array/items"` — `ListView` builds its own
        `ArrayAdapter` from the 20 strings in `strings.xml`. There is NO
        adapter in the code — that is why `listView.getItemAtPosition(position)` returns
        a `String` directly.
      What it does exactly: in the `ListView` constructor, the attribute is read and
        `setAdapter(new ArrayAdapter<>(context, android.R.layout.simple_list_item_1,
        entries))` is called. The row layout is the standard platform one — a `TextView`.
      `android:nestedScrollingEnabled="true"` — lets the list pass the
        scroll events to the parent (`CoordinatorLayout`), so that `liftOnScroll`
        works. Without it, the list "swallows" the scroll and the bar does not react.
      `match_parent` on the height — the list fills all the space left after the bar.
        `wrap_content` would have let it grow indefinitely.

      WHY `ListView` AND NOT `RecyclerView` HERE: 20 static rows, no
        animations, no complicated recycled views. `ListView` is enough and requires
        zero code. `RecyclerView` would have required an adapter, a `ViewHolder` and a
        `LayoutManager` — the topic of chapter 12.
      WHAT HAPPENS IF YOU REMOVE THE `FrameLayout`: `ListView` would receive
        `app:layout_behavior` and would work, but you would lose the place for a FAB or
        an "empty list" `TextView`. The `FrameLayout` is an extension layer, not a
        technical necessity.
      ================================================================================
    -->
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

</androidx.coordinatorlayout.widget.CoordinatorLayout>

    <!--
      ================================================================================
      ELEMENT: NavigationView (the drawer)
      ================================================================================
      `layout_width="wrap_content"` — the drawer has the width of its content, not of the
        screen. `match_parent` would cover everything and would no longer look like a drawer. Material
        recommends ~280dp; `wrap_content` comes close.
      `layout_height="match_parent"` — across the whole height.
      `android:layout_gravity="start"` — THE ATTRIBUTE THAT MAKES THE DIFFERENCE. Without it,
        `NavigationView` is treated as the second content panel and never opens.
        It must be identical to `GravityCompat.START` in the code.
      `app:menu="@menu/drawer_menu"` — the drawer contents come from the XML.
        `NavigationView` inflates it itself; the code only listens to clicks.
      `NavigationView` applies its insets itself — it extends
        `ScrimInsetsFrameLayout`, which adds padding for the status bar. That is why it
        does not need the insets block from the code.
      ================================================================================
    -->
    <com.google.android.material.navigation.NavigationView
        android:id="@+id/navigationView"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        app:menu="@menu/drawer_menu" />

</androidx.drawerlayout.widget.DrawerLayout>

<!--
  ======================================================================================
  `layout_gravity="start"` AND RTL
  ======================================================================================
  WHAT `start` MEANS: "the start of the reading direction". In Romanian, English, German
  — the left. In Arabic, Hebrew, Persian — the right.

  HOW IT IS RESOLVED: `DrawerLayout` calls `Gravity.getAbsoluteGravity(gravity,
  layoutDirection)` and turns `START` into `LEFT` or `RIGHT`, depending on the
  layout direction of the view. The result is used for measuring and positioning.

  WHY `android:supportsRtl="true"` IS NEEDED IN THE MANIFEST: without it, the app does not
  receive an RTL direction from the system, and `start` behaves like `left` even in
  Arabic. With it, the whole interface mirrors: the toolbar, the text, the drawer.

  WHAT HAPPENS IN THE CODE IF YOU MIX `START` AND `LEFT`:

  LTR (Romanian):
    XML: layout_gravity="start"  → the drawer is on the LEFT
    Code: openDrawer(GravityCompat.START) → looks for the drawer from START = LEFT → OK

  RTL (Arabic):
    XML: layout_gravity="start"  → the drawer is on the RIGHT
    Code: openDrawer(GravityCompat.START) → looks for the drawer from START = RIGHT → OK

  RTL with the wrong code:
    XML: layout_gravity="start"  → the drawer is on the RIGHT
    Code: openDrawer(Gravity.LEFT) → looks for the drawer from the LEFT → it does not exist → nothing

  THE RULE: `layout_gravity` in the XML and `GravityCompat.*` in the code must use
  the same relative constant (`start`/`end`). Never `left`/`right` mixed with
  `start`/`end`.

  WHY `GravityCompat` AND NOT `Gravity`: `GravityCompat.START` is defined in
  the compatibility library and is equal to `Gravity.START` on the APIs that have it.
  On old APIs, `GravityCompat` does the conversion. In practice, with `minSdk 33`, you
  could also use `Gravity.START` — but `GravityCompat` is the convention and costs nothing.

  WHAT HAPPENS WITH `layout_gravity="end"`: the drawer comes from the right in LTR and from
  the left in RTL. Useful for a second drawer (for example settings). The code would have to
  use `GravityCompat.END` for it.

  WHY `NavigationView` HAS NO DEFAULT `layout_gravity`: because `DrawerLayout`
  cannot guess which edge you want. Without gravity, the child is treated as content — and
  the screen looks as if the drawer had been glued over the list.
  ======================================================================================
-->
```

**What to remember from this file:** `DrawerLayout` has exactly two children, and the role of each is given by `layout_gravity`; `id=main` is on the content, not on the drawer; `CoordinatorLayout` + `AppBarLayout` + `layout_behavior` produce the bar-that-rises effect; `NavigationView` applies its insets itself.

---

## 26.5 `activity_second.xml`

The layout of the lab screen: a single vertical `LinearLayout` with a single `Button`, linked to the code through `android:onClick`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FILE: activity_second.xml
  ======================================================================================
  ROLE:
    The layout of the lab screen. A single vertical `LinearLayout` with a
    single `Button`, linked to the code through `android:onClick`.

  WHAT IT DEMONSTRATES:
    1. `android:onClick` — the XML → method link, through reflection.
    2. Vertical `LinearLayout` — the container into which buttons are added from code.
    3. `tools:context` — an attribute that exists only for the IDE preview.

  REF: ch. 14 (the section on dialogs), the documentation of `android:onClick`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: LinearLayout (the root)
  ======================================================================================
  A vertical `LinearLayout` — the children stack from top to bottom. That is why the buttons
    added from code appear one below the other, not on top of each other.
  `android:orientation="vertical"` — mandatory for vertical stacking.
    The default value is `horizontal`, so without the attribute the buttons would sit next to
    each other.
  `android:id="@+id/main"` — used twice in the code: for the insets and for
    `inflatedLayout`. The id repeats compared to `activity_main.xml`, but it is not a
    problem: the two layouts never coexist in the same tree.
  `xmlns:app` is declared, but UNUSED — no `app:*` attribute in the file.
    A leftover from the template, flagged by lint.
  `xmlns:tools` — the namespace of the design-time attributes. Used only once,
    for `tools:context`.
  `tools:context=".SecondActivity"` — only for the Android Studio preview: it
    tells the editor which theme and which class to use. Removed at build time, it does not reach
    the APK. Without it, the preview uses the app theme and does not know which activity
    to simulate.
  ======================================================================================
-->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".SecondActivity">

    <!--
      ================================================================================
      ELEMENT: Button
      ================================================================================
      `android:onClick="btnClick"` — binds the button to the `btnClick(View)` method in the
        activity, through reflection. There is NO `setOnClickListener` in the code — the whole
        link is here.
      Why it works without code: on click, Android looks for the method in the activity
        context. If it does not find it, the exception appears AT RUNTIME, not at compile time.
      How it searches exactly: `View.performClick()` calls the `onClick` that was set; if there is
        none, `View` has a `DeclaredOnClickListener` created at inflate, which holds
        the method name and the context. On click, it looks for the method with reflection, in the context
        and in its parents.

      `android:id="@+id/button"` is NOT used anywhere — neither in the code nor in another
        XML. It is useful only if you want to reference it later. The buttons created
        from code receive numeric ids (1, 2, 3...), not resource ids.
      `match_parent` on the width — the button fills the screen. The buttons added from code
        receive the same `MATCH_PARENT`, so they look identical.
      `wrap_content` on the height — as much as the text needs, plus the default padding
        of the Material button.
      WITHOUT `padding` on the `LinearLayout` — the buttons touch the edges of the screen.
        Cosmetic, not functional.
      WHY `Button` AND NOT `MaterialButton`: `Button` is styled automatically by the Material3
        theme (through `buttonStyle` in the theme), so it looks like a `MaterialButton`.
        The difference only shows if you want specific attributes (`app:icon`,
        `app:cornerRadius`).
      WHAT HAPPENS IF YOU ADD `android:enabled="false"`: the button no longer receives
        clicks, so `btnClick` is no longer called. Useful for blocking an action
        until a condition.
      ================================================================================
    -->
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:onClick="btnClick"
        android:text="Button" />
</LinearLayout>
```

**What to remember:** `android:onClick` is the only link between the XML and `btnClick`; the vertical `LinearLayout` is the reason why the added buttons appear one below the other.

---

## 26.6 The menus (`res/menu/*.xml`)

Three files, three different purposes. All are inflated from XML — none is built in code. Each file has its own block, in source order.

### 26.6.1 `drawer_menu.xml` — the drawer contents

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FILE: drawer_menu.xml
  ======================================================================================
  ROLE:
    The drawer contents: three navigation destinations + a separate setting.
    `NavigationView` inflates it itself, through `app:menu="@menu/drawer_menu"`.

  WHAT IT DEMONSTRATES:
    1. `checkableBehavior="single"` — an exclusive group, like a radio group.
    2. an `item` without an id, with a nested `menu` — a section subtitle.
    3. the `nav_*` ids — exactly the ones checked in `MainActivity`.

  REF: ch. 14 (the section on menus), the documentation of `Menu`, `MenuItem`, `SubMenu`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <menu>
  ======================================================================================
  The root of any menu file. It contains `<group>` and `<item>`.
  ======================================================================================
-->
<menu xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- checkableBehavior="single" = radio group: a single checked item -->
    <!--
      ================================================================================
      ELEMENT: <group android:checkableBehavior="single">
      ================================================================================
      The group behaves like a radio group: when you select "Sent", "Inbox" is
      unchecked automatically. The possible values:

        single → a single checked item per group (radio);
        all    → every item can be checked independently (checkbox);
        none   → no item can be checked.

      `android:checked="true"` on `nav_inbox` — the initial state. Without it, on the first
      open no item is checked, although the toolbar displays "Inbox".
      `android:icon` — every item has a vector icon from `res/drawable/`.
      `NavigationView` displays them to the left of the title.
      `android:title` is literal text, not `@string/...` — it works, but it is not
      translated. For a real application, all the titles should be in
      `strings.xml`.
      ================================================================================
    -->
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

    <!--
      ================================================================================
      ELEMENT: <item android:title="Other"> with a nested <menu>
      ================================================================================
      An `<item>` WITHOUT an id, which contains a `<menu>` — the trick for a SECTION
      SUBTITLE. "Other" appears as a grey label, and "Settings" below it, separate from
      the main group.

      WHY `nav_settings` IS OUTSIDE THE GROUP: it is not part of the main navigation
      (Inbox/Sent/Trash), but a setting. The visual separation suggests
      the difference.
      THE CONSEQUENCE IN THE CODE: `nav_settings` is not checkable, so `item.setChecked(true)`
      has no visual effect on it. Its branch displays a `Toast`.
      WHAT HAPPENS IF YOU PUT `nav_settings` IN THE SAME GROUP: it would become the fourth
      radio button. On click, "Inbox" would be unchecked and "Settings" would stay checked —
      although it is not a navigation destination. The separation is not only visual, it is semantic.
      ================================================================================
    -->
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

### 26.6.2 `list_item_menu.xml` — the context menu

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FILE: list_item_menu.xml
  ======================================================================================
  ROLE:
    The context menu of a row: Open / Rename / Delete. Inflated by `PopupMenu`
    in `MainActivity`, on long press.

  WHAT IT DEMONSTRATES:
    1. A minimal menu, with no icons and no `showAsAction`.
    2. The `action_*` ids — exactly the ones checked in the code.

  REF: ch. 14 (the section on menus), the documentation of `PopupMenu`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <menu> with three <item>s
  ======================================================================================
  DELIBERATE MINIMALISM: no icons, no `showAsAction`. A `PopupMenu` has no
    bar — all the items appear in the list, so `showAsAction` would be ignored.

  THE THREE IDS ARE EXACTLY THE ONES CHECKED IN `MainActivity`: `action_open`,
    `action_rename`, `action_delete`. If you rename one in the XML without modifying
    the code, that branch no longer runs — and you get no compile error,
    just an `if` that never matches again.

  WITHOUT `android:icon` — a short context menu reads faster without
    icons. With icons, `PopupMenu` displays them, but they take up more space.

  THE ORDER OF THE ITEMS = THE ORDER IN THE MENU. `Open`, `Rename`, `Delete` appear from top to
    bottom. If you want `Delete` last (as a destructive action), this order is already
    correct.

  WHY `Delete` HAS NO RED STYLE: Android menus have no standard attribute
    for a "dangerous item". You could set a coloured `SpannableString` in the code,
    but it is not a widespread practice.
  ======================================================================================
-->
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

### 26.6.3 `top_app_bar.xml` — the bar menu

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FILE: top_app_bar.xml
  ======================================================================================
  ROLE:
    The top bar menu: Search, Share and Settings. Inflated by `MaterialToolbar`
    through `app:menu="@menu/top_app_bar"`.

  WHAT IT DEMONSTRATES:
    1. `app:showAsAction` — all the values and their effect at runtime.
    2. `app:` vs `android:` — why the namespace matters.
    3. The overflow — where the items that do not fit end up.

  REF: ch. 14 (the section on menus), the documentation of `Menu`, `MenuItem`,
       `android:showAsAction`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <menu> with xmlns:app
  ======================================================================================
  `xmlns:app` is MANDATORY here: `showAsAction` is an attribute defined by the AppCompat
    library, not by the platform. Without the `app` namespace, the attribute would not be recognised.

  `app:showAsAction` AND NOT `android:showAsAction` — the attribute is defined by the AppCompat
    library, not by the platform. With `android:` it would be silently ignored on the new
    versions. Why it is ignored: `android:showAsAction` is read only by the framework
    `ActionBar` (API 11+). The app uses `Theme.Material3.DayNight.NoActionBar`
    and a `MaterialToolbar` as a plain view — there is no framework `ActionBar` to
    read the attribute.

  ALL THE `showAsAction` VALUES AND WHAT HAPPENS AT RUNTIME:

    never                (0) → the item ALWAYS sits in the overflow (the "⋮" menu),
                               regardless of space;
    ifRoom               (1) → the item appears on the bar IF IT FITS; otherwise in the overflow;
    always               (2) → the item ALWAYS appears on the bar, even if it crowds
                               the title;
    withText             (4) → MODIFIER: it also displays the title, not only the icon
                               (it combines with `ifRoom`/`always`);
    collapseActionView   (8) → the item has an `ActionView` that collapses to an
                               icon and expands on click (e.g. `SearchView`).

  HOW THEY COMBINE: `withText` and `collapseActionView` are FLAGS, not states. They are
    written with `|`:
      app:showAsAction="ifRoom|withText"          → on the bar, with icon AND text
      app:showAsAction="always|collapseActionView" → always on the bar, with a collapsible
                                                     ActionView

  WHAT THE TOOLBAR DOES CONCRETELY, IN ORDER:
    1. It measures the available width (the screen minus the navigation icon minus the title).
    2. It walks the items in the XML order.
    3. For every `always`: it puts it on the bar, regardless of space.
    4. For every `ifRoom`: it puts it on the bar if there is still room; otherwise in the overflow.
    5. For every `never`: it puts it directly in the overflow.
    6. The overflow appears only if it has at least one item.

  THE ORDER IN THE XML = THE ORDER ON THE BAR, from left to right (after the navigation
    icon). In the overflow, the order is preserved.

  THE TITLES ARE LITERAL, not resources — the same observation as for `drawer_menu.xml`.
  ======================================================================================
-->
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">

    <!--
      ================================================================================
      ELEMENT: action_search — ifRoom
      ================================================================================
      `ifRoom` — it appears on the bar if it fits; otherwise in the overflow. On a narrow phone,
      one of Search and Share may fall into the overflow. On a tablet both appear.
      The behaviour depends on the screen width, on the orientation and on the length of the
      title.
      `android:icon="@drawable/ic_search"` — the vector icon from `res/drawable/`.
      ================================================================================
    -->
    <item
        android:id="@+id/action_search"
        android:icon="@drawable/ic_search"
        android:title="Search"
        app:showAsAction="ifRoom" />

    <!--
      ================================================================================
      ELEMENT: action_share — ifRoom
      ================================================================================
      The second `ifRoom` action. If the bar has no room for both, the second one
      (in the XML order) falls into the overflow first.
      ================================================================================
    -->
    <item
        android:id="@+id/action_share"
        android:icon="@drawable/ic_share"
        android:title="Share"
        app:showAsAction="ifRoom" />

    <!--
      ================================================================================
      ELEMENT: action_settings — never
      ================================================================================
      `never` — it ALWAYS sits in the overflow, regardless of space. It has no icon: in the
      overflow, the text is enough. The items with an icon in the overflow display their
      icon; the ones without, only the text.

      WHAT HAPPENS IF YOU PUT `always` ON ALL THREE: the bar becomes crowded, the title
      "Inbox" is truncated, and on small screens the items overlap the title.
      `always` is used only for critical actions, at most one or two.
      WHAT HAPPENS IF YOU PUT `withText` WITHOUT `ifRoom`: `withText` alone does not say
      where the item should sit. In practice, it is always combined with `ifRoom` or `always`.
      ================================================================================
    -->
    <!-- Items with "never" go into the ⋮ overflow menu -->
    <item
        android:id="@+id/action_settings"
        android:title="Settings"
        app:showAsAction="never" />
</menu>
```

**What to remember from the menus:** `showAsAction` has five values, but only three are states (`never`, `ifRoom`, `always`); `withText` and `collapseActionView` are flags. `app:` is mandatory; `android:` is ignored by AppCompat.

---

## 26.7 Complete flows

The section gathers, in a single place, the four flows you can be given as a scenario in the test: startup, opening the drawer, the context menu and Back. Each has a diagram and a list of effects.

### 26.7.1 Startup — from the icon to the first frame

```
┌──────────────┐
│ LAUNCHER     │  the user taps the icon
└──────┬───────┘
       │ Intent MAIN + LAUNCHER
       ▼
┌──────────────────────────────────────────────────────────────┐
│ ActivityManagerService                                       │
│  - reads AndroidManifest.xml                                 │
│  - finds `.MainActivity` for the MAIN/LAUNCHER filter        │
│  - creates the app process (if it does not exist)            │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ MainActivity                                                 │
│  constructor → onCreate → onStart → onResume                 │
│                                                              │
│  onCreate:                                                   │
│    1. super.onCreate                                         │
│    2. EdgeToEdge.enable                                      │
│    3. setContentView(activity_main)                          │
│         └── the view tree is built                           │
│    4. insets on R.id.main                                    │
│    5. listView + long-press listener                         │
│    6. drawerLayout / toolbar / navigationView                │
│    7. drawer listener                                        │
│    8. Back callback                                          │
│    9. hamburger listener                                     │
│   10. toolbar menu listener                                  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ MEASURE → LAYOUT → DRAW                                      │
│  - DrawerLayout measures the content and the drawer          │
│  - CoordinatorLayout measures the AppBar and FrameLayout     │
│  - ListView creates the first visible rows                   │
│  - the first frame appears on screen                         │
└──────────────────────────────────────────────────────────────┘
```

**What you can say in the test in three sentences:** the launcher sends an `Intent` with `MAIN` + `LAUNCHER`; the system finds the activity in the manifest and creates it; `onCreate` builds the tree, binds the listeners, and the system draws the first frame.

**What does not happen:** no read from `savedInstanceState`, no network request, no database. The screen is completely static.

### 26.7.2 The drawer state — a state machine

```
                    openDrawer(START)
   ┌────────────┐ ──────────────────────► ┌────────────┐
   │   CLOSED   │                         │    OPEN    │
   │            │ ◄────────────────────── │            │
   └────────────┘   closeDrawer(START)    └────────────┘
         ▲                or Back                 │
         │                                        │
         │  click on an item in                   │
         │  NavigationView                        │
         └────────────────────────────────────────┘
                  (closeDrawer from the listener)

   Swipe from the edge:  CLOSED → OPEN  (native DrawerLayout gesture)
   Swipe towards edge:   OPEN → CLOSED  (native DrawerLayout gesture)
   Click on the scrim:   OPEN → CLOSED  (default behaviour)
```

**The transitions and who triggers them:**

| Transition | Trigger | Code |
|---|---|---|
| CLOSED → OPEN | hamburger | `toolbar.setNavigationOnClickListener` → `openDrawer(START)` |
| CLOSED → OPEN | swipe from the edge | native `DrawerLayout` |
| OPEN → CLOSED | item click | `navigationView.setNavigationItemSelectedListener` → `closeDrawer(START)` |
| OPEN → CLOSED | Back | `OnBackPressedCallback` → `closeDrawer(START)` |
| OPEN → CLOSED | click on the scrim | native `DrawerLayout` |
| OPEN → CLOSED | swipe towards the edge | native `DrawerLayout` |

**Why `DrawerLayout` needs an explicit `closeDrawer` if the native gesture closes it:** the native gesture exists, but it is not enough. The user who presses a menu item expects the drawer to close immediately — not to swipe it themselves. `closeDrawer` performs the transition programmatically, with an animation.

**What happens if you call `closeDrawer` when the drawer is already closed:** nothing. The method checks the state and does nothing if it is already closed. It throws no exception. The same for `openDrawer` when it is already open.

### 26.7.3 Selecting an item from the drawer — sequence

```
User                      NavigationView            MainActivity              DrawerLayout
    │                          │                         │                         │
    │  click "Sent"            │                         │                         │
    ├─────────────────────────►│                         │                         │
    │                          │  onMenuItemClick(item)  │                         │
    │                          ├────────────────────────►│                         │
    │                          │                         │                         │
    │                          │                         │  id == nav_sent?        │
    │                          │                         │  → toolbar.setTitle     │
    │                          │                         │    ("Sent")             │
    │                          │                         │                         │
    │                          │                         │  item.setChecked(true)  │
    │                          │◄────────────────────────┤                         │
    │                          │  (checks "Sent",        │                         │
    │                          │   unchecks "Inbox")     │                         │
    │                          │                         │                         │
    │                          │                         │  closeDrawer(START)     │
    │                          │                         ├────────────────────────►│
    │                          │                         │                         │
    │                          │                         │  return true            │
    │                          │◄────────────────────────┤                         │
    │                          │                         │                         │
    │  the drawer slides back  │                         │                         │
    │◄─────────────────────────┴─────────────────────────┴─────────────────────────┤
```

**The exact order in the code:** first the title changes, then `setChecked`, then `closeDrawer`, then `return true`. If you moved `closeDrawer` before `setChecked`, the check mark would be applied to an already hidden menu — it works, but you cannot see it.

**What the user sees:** the drawer slides back, the bar title becomes "Sent", and on reopening "Sent" is checked and "Inbox" is not. The list does not change — the 20 "Item N" entries remain.

### 26.7.4 The context menu — sequence

```
User                      ListView                 PopupMenu              MainActivity
    │                        │                         │                        │
    │  long press            │                         │                        │
    │  on row 5              │                         │                        │
    ├───────────────────────►│                         │                        │
    │                        │  onItemLongClick(       │                        │
    │                        │    parent, view, 5, 5)  │                        │
    │                        ├────────────────────────►│                        │
    │                        │                         │                        │
    │                        │                         │  new PopupMenu(this,   │
    │                        │                         │      view)             │
    │                        │                         │  inflate(list_item_    │
    │                        │                         │      menu)             │
    │                        │                         │  setOnMenuItemClick... │
    │                        │                         │  show()                │
    │                        │                         │                        │
    │  the menu appears next │                         │                        │
    │  to row 5              │                         │                        │
    │◄───────────────────────┴─────────────────────────┤                        │
    │                        │                         │                        │
    │  click "Delete"        │                         │                        │
    ├────────────────────────┼────────────────────────►│                        │
    │                        │                         │  itemId == action_     │
    │                        │                         │      delete            │
    │                        │                         │  selected = "Item 6"   │
    │                        │◄────────────────────────┤  Toast "Delete:        │
    │                        │  getItemAtPosition(5)   │      Item 6"           │
    │                        │                         │  return true           │
    │                        │                         │                        │
    │  the menu closes       │                         │                        │
    │◄───────────────────────┴─────────────────────────┘                        │
```

**Careful with the index:** `position` is 0-based, so row 5 displays "Item 6". It is not a bug — it is the Java convention.

**Why `selected` is computed in the menu listener and not in the long-press one:** because `position` is captured and stays valid. You could compute it earlier and capture it, but you would have an extra variable. Computing it on click is more direct.

### 26.7.5 Back — the two branches

```
                         ┌─────────────────────┐
                         │  Back pressed       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ dispatcher.onBackPressed()    │
                    │ walks the callbacks           │
                    │ from the last to the first    │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ is our callback active?       │
                    └───────┬───────────────┬───────┘
                            │ YES           │ NO
                            ▼               ▼
              ┌─────────────────────┐   ┌──────────────────────┐
              │ isDrawerOpen(START) │   │ the next callback   │
              └──────┬───────┬──────┘   │ or fallback          │
                     │ YES   │ NO       │   └─ finish()        │
                     ▼       ▼          └──────────────────────┘
        ┌────────────────┐  ┌──────────────────────────────┐
        │ closeDrawer    │  │ setEnabled(false)            │
        │                │  │ onBackPressed()              │
        │ stay on screen │  │   └─ fallback → finish()     │
        └────────────────┘  └──────────────────────────────┘
```

**The two branches, one sentence each:** drawer open → you close it and stay; drawer closed → you disable yourself and let the system close the activity.

**Why not `finish()` directly in the second branch:** you would skip any other callback in the chain. If you added a `NavController` or a second callback, Back should reach them first.

### 26.7.6 `SecondActivity` — the complete flow

```
MANUAL LAUNCH
  onCreate
    ├── super.onCreate
    ├── EdgeToEdge.enable
    ├── setContentView(activity_second)
    ├── insets on R.id.main
    └── inflatedLayout = findViewById(R.id.main)

CLICK "Button"
  android:onClick → reflection → btnClick(View)
    ├── AlertDialog.Builder(SecondActivity.this)
    ├── setTitle / setMessage / setCancelable
    ├── setPositiveButton("Do it!", listener)
    ├── setNegativeButton("Cancel", listener)
    └── builder.show()

CLICK "Do it!"
  ├── id = addButton()
  │     ├── new Button(SecondActivity.this)
  │     ├── setText("Button_1")
  │     ├── setId(1)
  │     ├── setLayoutParams(MATCH_PARENT, WRAP_CONTENT)
  │     └── inflatedLayout.addView(newBtn)
  └── Snackbar.make(..., inflatedLayout, "Cancel previous action.", LENGTH_LONG)
        ├── setAction("Cancel", listener)
        └── show()
              └── CLICK "Cancel"
                    ├── findViewById(1)
                    └── removeView(the button)

CLICK "Cancel" (in the dialog)
  └── Toast "Object creation cancelled"
```

**What you see on screen, in order:** the dialog, then the new button below the original one, then the Snackbar at the bottom. If you press "Cancel" on the Snackbar, the button disappears; the Snackbar closes anyway.

**What happens if you press "Do it!" three times:** the dialog closes after each click, so you have to reopen it. Each "Do it!" adds a button and a Snackbar. The Snackbars replace each other (a single visible Snackbar per parent).

### 26.7.7 What happens in memory

```
ActivityManagerService
    └── MainActivity (instance)
          ├── mDecorView (the window)
          │     └── DrawerLayout
          │           ├── CoordinatorLayout (id=main)
          │           │     ├── AppBarLayout
          │           │     │     └── MaterialToolbar
          │           │     │           ├── navigationIcon view
          │           │     │           └── menu items
          │           │     └── FrameLayout
          │           │           └── ListView
          │           │                 └── adapter (ArrayAdapter)
          │           │                       └── 20 Strings
          │           └── NavigationView
          │                 └── Menu (from drawer_menu.xml)
          └── fields:
                ├── drawerLayout  → reference to a view
                └── listView      → reference to a view
```

**The listeners and the lifecycle:** every listener is an object attached to a view (`ListView.mOnItemLongClickListener`, `Toolbar.mOnMenuItemClickListener`, `Toolbar.mNavigationOnClickListener`, `NavigationView.mListener`, `OnBackPressedDispatcher.callbacks`). All of them hold a reference to `MainActivity` (through a capture or through a field) and are held by views owned by the activity. The Activity → View → Listener → Activity cycle is broken when the activity is destroyed. It is not a leak.

**On rotation:** the system calls `onSaveInstanceState` (if implemented), then `onPause` → `onStop` → `onDestroy` on the old instance. It creates a NEW instance and calls `onCreate` again. All the old views are garbage collected; all the listeners die with them. The state that is not saved is lost: the title, the check mark, the list position.

**What should be saved for a real application:** the current title (String), the id of the checked item, the list position (`ListView` saves it itself, if it has an id), the buttons added in `SecondActivity` (a list of ids + texts).

**Why `counter` resets:** it is an instance field, not `static`. The new instance starts with `counter = 0`. If it were `static`, it would survive rotation, but it would live as long as the process and would grow to infinity.

**When a leak would appear:** if you put a listener in a `static` (for example `private static List<View.OnClickListener> listeners`) or in an application-level singleton. Then the reference would outlive the activity and would keep it alive.

---

## 26.8 Pitfalls — symptom, cause, remedy

The section is written as a diagnostic table. In the test, the question "what happens if…" is answered from the "Symptom" column.

### 26.8.1 Pitfalls in `MainActivity`

| # | What you do wrong | Symptom | Cause | Remedy |
|---|---|---|---|---|
| 1 | You forget `closeDrawer` in the drawer listener | the title changes, but the drawer stays over the screen | `NavigationView` does not know about `DrawerLayout` | `drawerLayout.closeDrawer(GravityCompat.START)` |
| 2 | You forget `setEnabled(false)` in the Back callback | `StackOverflowError` on Back with the drawer closed | the callback re-enters itself | disable yourself before `onBackPressed()` |
| 3 | You use `Gravity.LEFT` in one place and `START` in another | it works in Romanian, it breaks in RTL | different constants | use `GravityCompat.START` everywhere |
| 4 | You forget `return true` on the long press | the menu appears and the click fires too | `mHasPerformedLongPress` stays `false` | `return true` after `popup.show()` |
| 5 | You forget `popup.show()` | nothing appears on long press | the menu is built but not displayed | call `show()` |
| 6 | You forget `popup.getMenuInflater().inflate(...)` | empty menu, no items | the `Menu` was not filled | inflate with `R.menu.list_item_menu` |
| 7 | You use `toolbar` as the `PopupMenu` anchor | the menu appears under the bar, not next to the row | wrong anchor | use `view` (the row) |
| 8 | You use `listView` as the anchor | the menu appears at the edge of the list | the anchor is too large | use `view` |
| 9 | You forget `app:menu` on the toolbar | the bar has no Search/Share/Settings | the menu is not inflated | add `app:menu="@menu/top_app_bar"` |
| 10 | You forget `app:navigationIcon` | there is no hamburger | the icon is not set | add `app:navigationIcon="@drawable/ic_menu"` |
| 11 | You forget `setNavigationOnClickListener` | the hamburger is decorative | nobody listens to the click | register the listener |
| 12 | You forget `setOnMenuItemClickListener` | the menu items do nothing | nobody listens to the click | register the listener |
| 13 | You use `android:showAsAction` | the attribute is ignored | AppCompat reads `app:` | use `app:showAsAction` |
| 14 | You put `always` on all the items | the title is truncated, the bar is crowded | `always` ignores space | use `ifRoom` |

**Why pitfall 2 is the most serious:** `StackOverflowError` cannot be caught elegantly and crashes the app immediately. There is no useful message in the log — just a huge stack trace, with `handleOnBackPressed` repeated thousands of times.

**Why pitfall 1 is the most frequent:** it seems that `NavigationView` should close the drawer itself. It does not, because it has no reference to it. It is a separation of responsibilities, not an oversight.

### 26.8.2 Pitfalls in `SecondActivity`

| # | What you do wrong | Symptom | Cause | Remedy |
|---|---|---|---|---|
| 1 | You make `btnClick` `private` | it compiles, it crashes on click with `IllegalStateException` | reflection looks for public methods | `public void btnClick(View)` |
| 2 | You change the parameter to `Object` | the same exception on click | the signature does not match | keep `View` |
| 3 | You forget `builder.show()` | the dialog does not appear | the builder is built but not displayed | call `show()` |
| 4 | You forget `.show()` on the Snackbar | the Snackbar does not appear | built but not displayed | add `.show()` |
| 5 | You forget `setId` in `addButton` | the button appears but cannot be deleted | `findViewById` returns `null` | `newBtn.setId(counter)` |
| 6 | You use `getApplicationContext()` | the button loses the theme / crashes at inflate | unthemed context | `SecondActivity.this` |
| 7 | You write `counter++` instead of `++counter` | the first button has id 0 | post-increment | `++counter` |
| 8 | You do not save the buttons in `savedInstanceState` | they disappear on rotation | the tree is rebuilt from the XML | save the ids and rebuild |
| 9 | You call `Snackbar.make` with a `Context` instead of a `View` | it does not compile | the overload does not exist | the second argument is a `View` |
| 10 | You forget `setLayoutParams` | the button has default dimensions | the parent generates `LayoutParams` | set them explicitly |

**Why pitfall 6 is subtle:** `getApplicationContext()` compiles and, on some themes, works. The error appears only when the widget needs a theme attribute that exists only in the activity theme. Then you get an `InflateException` or a completely unstyled widget.

**Why pitfall 8 is not a bug but a limitation:** a view added from code is not part of the XML, so it cannot be rebuilt automatically. Saving it in a `Bundle` is your responsibility.

### 26.8.3 Pitfalls in the XML

| # | What you do wrong | Symptom | Cause | Remedy |
|---|---|---|---|---|
| 1 | You put `NavigationView` without `layout_gravity` | the drawer covers the screen and does not open | it is treated as the second content | `android:layout_gravity="start"` |
| 2 | You put a third child in `DrawerLayout` | the content is covered | the child without gravity is treated as content | only content + drawer |
| 3 | You put two children with `start` | `IllegalStateException` at inflate | a single drawer per edge | one `start`, one `end` |
| 4 | You remove `app:layout_behavior` | the list is drawn under the bar | `CoordinatorLayout` does not know how to push it | add the behaviour |
| 5 | You remove `liftOnScrollTargetViewId` | the lift can be jerky or applied to another view | the automatic detection is unreliable when the view is nested | add the id |
| 6 | You remove `android:nestedScrollingEnabled` | the scroll does not reach `CoordinatorLayout` | the list swallows the events | set it to `true` |
| 7 | You put `match_parent` on `NavigationView` | the drawer covers the whole screen | wrong width | `wrap_content` |
| 8 | You put `id=main` on `DrawerLayout` | padding on top of the drawer's padding | insets applied to the root | put the id on the content |
| 9 | You put `android:background` on the toolbar | two layers of purple | the colour comes from `AppBarLayout` | `@android:color/transparent` |
| 10 | You hardcode `56dp` | the bar looks wrong on other themes | fixed height | `?attr/actionBarSize` |

**Why pitfall 1 is the most deceptive:** the XML is valid, the build passes, the app starts. Only the drawer does not open — and no log says why. You have to know the rule in order to diagnose it.

**Why pitfall 8 is hard to see:** the extra padding is small (the status bar height) and looks like a design margin. On a phone with a notch, the difference is more visible.

### 26.8.4 How to check each behaviour manually

| # | What you check | How | The correct result |
|---|---|---|---|
| 1 | The drawer opens | press the hamburger | `NavigationView` slides in from the left over the content |
| 2 | The drawer closes on selection | open the drawer, press "Sent" | the drawer slides back, the title becomes "Sent" |
| 3 | The check mark is exclusive | open the drawer again | "Sent" is checked, "Inbox" is not |
| 4 | The context menu is anchored | long press on "Item 7" | the menu appears next to row 7, not under the toolbar |
| 5 | Back closes the drawer | open the drawer, press Back | the drawer closes, the app stays open |
| 6 | Back closes the app | with the drawer closed, press Back | the app closes, with no crash |
| 7 | The bar menu works | press Search, Share, then Settings from "⋮" | three different `Toast`s |
| 8 | `SecondActivity` is unreachable | walk through all the screens of the app | there is no path to it |
| 9 | The dialog and the Snackbar | launch `SecondActivity` manually, press the button, "Do it!", then "Cancel" on the Snackbar | a new button, then it disappears |

**How to check 8 without launching it manually:** search for `SecondActivity` across the whole code. The only occurrences are in the manifest, in its own file and in `tools:context`. No `Intent`, no `startActivity`.

**How to check 4 precisely:** long press the first row and the last one. The menu must appear below on the first and above on the last — `PopupWindow` moves it so that it fits.

**How to check 6 without closing the app by mistake:** open the drawer, press Back (it closes), press Back again (the app closes). If you have a `StackOverflowError`, the app crashes on the second Back — exactly the symptom of pitfall 2.

**What you cannot check without an RTL device:** the `start`/`end` behaviour. You can change the system language to Arabic or Hebrew, or you can force the direction from the developer options ("Force RTL layout direction").

---

## 26.9 The XML ↔ code links

Almost every bug in small Android projects is a broken link between a name in the XML and a name in the code. The table gathers all of them.

| In XML | In code | What breaks if they differ |
|---|---|---|
| `android:layout_gravity="start"` | `GravityCompat.START` | the drawer does not open / does not close |
| `@+id/drawerLayout` | `R.id.drawerLayout` | `NullPointerException` |
| `@+id/topAppBar` | `R.id.topAppBar` | `NullPointerException` |
| `@+id/navigationView` | `R.id.navigationView` | `NullPointerException` |
| `@+id/listView` | `R.id.listView` | `NullPointerException` |
| `@+id/main` | `R.id.main` (insets) | no padding, content under the bars |
| `android:onClick="btnClick"` | `public void btnClick(View)` | `IllegalStateException` on click |
| `app:menu="@menu/top_app_bar"` | `toolbar.setOnMenuItemClickListener` | dead listener |
| `app:menu="@menu/drawer_menu"` | `navigationView.setNavigationItemSelectedListener` | dead listener |
| `@+id/action_open` etc. | `R.id.action_open` etc. | the branch no longer runs |
| `@+id/nav_inbox` etc. | `R.id.nav_inbox` etc. | the branch no longer runs |
| `android:entries="@array/items"` | `listView.getItemAtPosition(...)` | empty list |
| `app:liftOnScrollTargetViewId="@id/listView"` | `@+id/listView` | the lift can be jerky or applied to another view |

**The general rule:** every `R.id.*` in the code must have an `@+id/*` in the XML. Every `@+id/*` in the XML that is used in the code must have an `R.id.*`. An id without a pair gives no compile error — only a `null` or a dead `if`.

**How to check quickly:** `Ctrl+Click` on `R.id.name` in Android Studio. If it takes you to the XML, the link exists. If not, you have a wrong or missing id.

**Why `@+id` has the `+` only the first time:** `+` means "create the id". The second occurrence in another XML file can use `@id/...` (without `+`), because the id already exists in `R`. In practice, `@+id` works the second time too — it just creates nothing any more.

### 26.9.1 How to read a stack trace for the project's five exceptions

**1. `NullPointerException` on a `findViewById`**

```
java.lang.NullPointerException: Attempt to invoke virtual method
    'void android.widget.ListView.setOnItemLongClickListener(...)'
    on a null object reference
    at ro.ase.ie.dma03.MainActivity.onCreate(MainActivity.java:40)
```

**How to read it:** the last line of the trace is the exact place. "on a null object reference" means that `listView` is `null`. The cause: `findViewById` was called before `setContentView`, or the id does not exist in the XML.

**2. `IllegalStateException: Could not find method btnClick(View)`**

```
java.lang.IllegalStateException: Could not find method btnClick(View) in a
    parent or ancestor Context for android:onClick attribute defined on view
    class android.widget.Button with id 'button'
    at android.view.View$DeclaredOnClickListener.resolveMethod(...)
```

**How to read it:** the message says exactly which method is missing and on which view. Causes: the method is `private`, has another parameter, or was renamed without modifying the XML.

**3. `StackOverflowError` on Back**

```
java.lang.StackOverflowError:
    at ro.ase.ie.dma03.MainActivity$1.handleOnBackPressed(MainActivity.java:94)
    at androidx.activity.OnBackPressedDispatcher.onBackPressed(...)
    at ro.ase.ie.dma03.MainActivity$1.handleOnBackPressed(MainActivity.java:98)
    at androidx.activity.OnBackPressedDispatcher.onBackPressed(...)
    ... (thousands of identical lines)
```

**How to read it:** two lines repeating to infinity. The cause: `onBackPressed()` is called from the callback that should handle it, without `setEnabled(false)`.

**4. `IllegalStateException: Child drawer has absolute gravity`**

```
java.lang.IllegalStateException: Child drawer has absolute gravity LEFT but
    this DrawerLayout already has a drawer view along that edge
    at androidx.drawerlayout.widget.DrawerLayout.addDrawerChild(...)
```

**How to read it:** you have two children with `layout_gravity` on the same edge. The cause: a second `NavigationView` with `start`, or a `FrameLayout` with an accidental `layout_gravity="left"`.

**5. `InflateException` on `setContentView`**

```
android.view.InflateException: Binary XML file line #17: Error inflating class
    com.google.android.material.appbar.MaterialToolbar
    Caused by: java.lang.IllegalArgumentException: The style on this component
    requires your app theme to be Theme.MaterialComponents (or a descendant).
```

**How to read it:** the last "Caused by" line is the real cause. Here: the app theme is not Material. The cause: `Theme.DMA03` was changed, or `setContentView` runs in a context with another theme.

**The general reading rule:** from top to bottom, the last "Caused by" line is the cause; the first line in the trace that contains `ro.ase.ie.dma03` is the place in your code. The rest are library calls — useful only if you want to understand the mechanism.

**What you must not do:** read the whole trace from top to bottom and stop at the first Android line. The cause is almost always in the last "Caused by" and in the first line of your code.

---

## 26.10 What to remember

| File | The essence |
|---|---|
| `MainActivity.java` | `onCreate` does everything: insets, list, drawer, Back, hamburger, menu. `GravityCompat.START` four times, identical to the XML. |
| `SecondActivity.java` | `android:onClick` requires `public void name(View)`. `setId` is what makes the button findable. `hPixels` is dead code. |
| `AndroidManifest.xml` | `exported="true"` + `MAIN`/`LAUNCHER` = the start screen. `SecondActivity` is declared, but unlinked. |
| `activity_main.xml` | `DrawerLayout` with exactly 2 children; the second has `layout_gravity="start"`. `id=main` is on the content, not on the drawer. |
| `activity_second.xml` | a vertical `LinearLayout` with one button linked through `android:onClick`. |
| `drawer_menu.xml` | `checkableBehavior="single"` = radio group. An `item` without an id + a nested `menu` = a section subtitle. |
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

1. **You forget `closeDrawer`** — the drawer stays over the screen after the selection.
2. **You forget `setEnabled(false)` in the Back callback** — `StackOverflowError` on Back with the drawer closed.
3. **You put `Gravity.LEFT` in one place and `START` in another** — it works in Romanian, it breaks in RTL.
4. **You remove `app:layout_behavior`** — the list is drawn under the bar.
5. **You remove `liftOnScrollTargetViewId`** — the lift can be jerky or applied to another view.
6. **You remove `setId` from `addButton`** — the Snackbar can no longer find the button to delete.
7. **You make `btnClick` private** — it compiles, it crashes on click.

### The five exam questions the chapter answers

| Question | The short answer | Section |
|---|---|---|
| Why does `DrawerLayout` have exactly two children? | the first = content, the second = drawer; the role is given by `layout_gravity` | 26.4.4 |
| Why does `setNavigationItemSelectedListener` not close the drawer? | `NavigationView` has no reference to `DrawerLayout` | 26.1.13 |
| Why `setEnabled(false)` before `onBackPressed()`? | otherwise the callback re-enters itself, infinite recursion | 26.1.14 |
| Why does `Snackbar.make` require a `View`? | the Snackbar is inserted into the tree, not into a separate window | 26.2.6 |
| Why does `SecondActivity` never appear? | it is declared in the manifest, but no `Intent` starts it | 26.3 |

---

## 26.11 Glossary

The terms that appear in the chapter and that a test can ask for without defining them. The definitions are short on purpose: one term, one sentence, one example from the project.

| Term | Definition | Where it appears |
|---|---|---|
| **Activity** | a component with its own window, started by the system | `MainActivity`, `SecondActivity` |
| **Context** | access to resources, theme and system services | `this` in `new PopupMenu(this, view)` |
| **Themed context** | a context that has a theme applied | `SecondActivity.this` at `new Button(...)` |
| **View** | any drawable element | `ListView`, `Button`, `Toolbar` |
| **ViewGroup** | a view that contains other children and positions them | `DrawerLayout`, `LinearLayout` |
| **LayoutParams** | the contract between child and parent about dimensions | `ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)` |
| **Inflater** | a parser that turns XML into objects | `LayoutInflater`, `MenuInflater` |
| **Listener** | an object that waits for an event | `setOnItemLongClickListener` |
| **Lambda** | a concise implementation of a functional interface | all the listeners in the project |
| **Insets** | the areas occupied by the system bars | the block in `onCreate` |
| **Drawer** | a sliding panel over the content | `NavigationView` |
| **Scrim** | the semi-transparent layer behind the drawer | drawn by `DrawerLayout` |
| **Overflow** | the "⋮" menu for the items that do not fit on the bar | `action_settings` |
| **ActionView** | a view that replaces the icon of a menu item | `SearchView` (not used here) |
| **RTL** | right-to-left; the reading direction for Arabic/Hebrew | `layout_gravity="start"` |
| **dp** | density-independent pixel | `?attr/actionBarSize` (56dp) |
| **Manifest** | the file that declares the app's components | `AndroidManifest.xml` |
| **exported** | whether a component can be started from another app | `MainActivity` = `true` |
| **Intent** | the description of an action or of a screen to start | the unused import |
| **Reflection** | looking up a method by name, at runtime | `android:onClick` |
| **Snackbar** | a feedback bar with an optional action | `SecondActivity` |
| **Dialog** | a modal window that demands a decision | `AlertDialog` |
| **Toast** | a short message, with no action | all the menu branches |
| **State** | the data that should survive recreation | `savedInstanceState` |

### Five pairs of terms that get confused

**1. `View` vs `ViewGroup`** — `ViewGroup` **is** a `View` (it inherits from it), but it has children. A `Button` is a `View`, a `LinearLayout` is a `ViewGroup`. In XML, both are tags; in code, both are `View`s.

**2. `LayoutInflater` vs `MenuInflater`** — the first reads layouts (`<LinearLayout>`, `<Button>`), the second reads menus (`<menu>`, `<item>`). They do not replace each other.

**3. `Toast` vs `Snackbar`** — `Toast` needs no view and cannot be cancelled; `Snackbar` needs a view and can have an action. `Toast` appears in a separate window, `Snackbar` in the screen's tree.

**4. `PopupMenu` vs `ContextMenu`** — `PopupMenu` is anchored to a view and appears next to it; `ContextMenu` appears centred, like a dialog, after `registerForContextMenu`. Here `PopupMenu` is used.

**5. `Gravity.LEFT` vs `GravityCompat.START`** — the first is the physical left, the second is the start of the reading direction. In LTR they are equal in effect; in RTL they differ. The code uses exclusively `START`.

**Why the glossary is at the end and not at the beginning:** terms are learned better after you have seen them in context. If you read it first, you would memorise definitions without examples. Now, every definition reminds you of a line from the project.

**How to use it before the test:** cover the "Definition" column and try to explain the term in two sentences, with an example from `DMA03`. If you can't, you have a section to reread.

---

## Chapter 26 summary

- `MainActivity` has a single `onCreate` with ten steps; the order `super` → `EdgeToEdge` → `setContentView` → `findViewById` is mandatory.
- `DrawerLayout` has exactly two children: the content and the drawer. The drawer is recognised by `layout_gravity="start"`.
- `id=main` is on the `CoordinatorLayout`, not on the `DrawerLayout` — the insets apply only to the content, and `NavigationView` takes care of its own.
- `MaterialToolbar` has two click areas, with two different listeners: `setNavigationOnClickListener` (hamburger) and `setOnMenuItemClickListener` (Search/Share/Settings).
- `PopupMenu` is anchored to the pressed row and needs `return true` so that it does not also trigger the normal click.
- `OnBackPressedCallback` solves Back in two steps: it closes the drawer, then disables itself and re-sends the event. Without `setEnabled(false)`, infinite recursion.
- `AlertDialog.Builder` chains; `show()` is mandatory. Here it is the platform variant, not AppCompat.
- `Snackbar` needs `.show()` and a reference view; its action can delete a view added from code.
- Views created from code need three things: a themed context, `LayoutParams`, `setId` if you want to find them again.
- `SecondActivity` is declared in the manifest, but **it is not started anywhere** — the `Intent` import in `MainActivity` is the only trace of the missing link.

**Back to** [cheatsheet](21%20-%20Cheatsheet.md), to [the DMA03 build chapter](14%20-%20DMA03%20-%20Navigare%20si%20meniuri.md) **or to** [the overview](index.html).

