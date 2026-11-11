# Chapter 28 — The DMA06 code annotated

**Objective:** to read the 14 files of the `DMA06` project with explanations on every block — what the line does, why it is there, what breaks if you remove it. The app displays the same numbers from 1 to 100 in three ways, so you can see exactly what each step adds.

**Source:** `DMA06/` at commit `d719ffc` — 14 files.

**What you learn from it:** the three steps on the same data — `ArrayAdapter`, `BaseAdapter` with a manual `ViewHolder`, `RecyclerView`.

**Estimated time:** 60–90 min (active reading).

> **How to read:** do not read passively. For every block, cover the explanation and try to say what it does yourself. If you can't, you have found what needs repeating.

---

## File map

| # | File | Role |
|---|---|---|
| 1 | `activities/MainActivity.java` | the menu with three buttons |
| 2 | `activities/SingleColumnActivity.java` | step 1 — `ListView` + `ArrayAdapter` |
| 3 | `activities/TwoColumnActivity.java` | step 2 — `ListView` + custom adapter |
| 4 | `activities/RecyclerViewActivity.java` | step 3 — `RecyclerView` |
| 5 | `adapters/NumberListAdapter.java` | `BaseAdapter` with a manual `ViewHolder` |
| 6 | `adapters/NumberRecyclerAdapter.java` | `RecyclerView.Adapter` |
| 7 | `data/NumberData.java` | the source: the numbers 1–100 |
| 8 | `res/layout/activity_main.xml` | the three buttons |
| 9 | `res/layout/activity_single_column.xml` | a single `ListView` |
| 10 | `res/layout/activity_two_column.xml` | header + `ListView` |
| 11 | `res/layout/activity_recycler_view.xml` | header + `RecyclerView` |
| 12 | `res/layout/item_number.xml` | the two-column row |
| 13 | `res/layout/layout_number_header.xml` | the two-column header |
| 14 | `AndroidManifest.xml` | the declaration of the four activities |

Three packages, three responsibilities:

```
ro.ase.ie.dma06.activities   ← ties everything together, responds to input
ro.ase.ie.adapters           ← turns data into rows
ro.ase.ie.data               ← produces data, doesn't know what a View is
```

> **Watch out for the packages:** the last two **do not** contain `dma06` in their declaration, even though the folders do. The detail is explained in 28.1 and it matters for the test.

---

## 28.0 `MainActivity.java`, `activity_main.xml`, `AndroidManifest.xml` — the entry into the app

### `MainActivity.java` — the menu

```java
package ro.ase.ie.dma06.activities;   // the screens' package — all 4 activities live here

import android.content.Intent;        // the "intent" that starts another activity
import android.os.Bundle;             // the state saved on rotation / return
import android.view.View;             // the type returned by findViewById
import androidx.appcompat.app.AppCompatActivity;   // the base activity (AppCompat)
import ro.ase.ie.dma06.R;             // the class generated from resources; `dma06` comes from `namespace`

/** Opens each step of the demo. */
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);        // 1. the parent's lifecycle
        setContentView(R.layout.activity_main);    // 2. inflate the layout with the 3 buttons

        openOnClick(R.id.btnStep1, SingleColumnActivity.class);    // 3. button → step 1
        openOnClick(R.id.btnStep2, TwoColumnActivity.class);       //    button → step 2
        openOnClick(R.id.btnStep3, RecyclerViewActivity.class);    //    button → step 3
    }

    private void openOnClick(int buttonId, Class<?> activityClass) {
        View button = findViewById(buttonId);      // look up the button in the current layout
        button.setOnClickListener(v -> startActivity(new Intent(this, activityClass)));
    }
}
```

**Why a helper and not three identical blocks:** the only things that differ between the three buttons are the **id** and the **class**. The rest is the same code. If you added a step 4, you add one line, not seven.

**`Class<?>`** — the second parameter of the `Intent(Context, Class<?>)` constructor is the class of the component to start. `<?>` means "any class"; here all three are activities.

**`this` inside a lambda** — in a lambda expression, `this` stays the instance surrounding the lambda, that is `MainActivity`. In an anonymous class (`new View.OnClickListener() { ... }`), `this` would be the instance of the anonymous class, which is **not** a `Context`, and you would have to write `MainActivity.this`. Here the lambda is shorter for exactly this reason.

**`startActivity` and not a `launcher`:** the screens of the three steps return nothing. You don't need `registerForActivityResult`, because you are not waiting for a result. The Back button brings you back to the menu, and the menu activity was not destroyed.

**`View button` and not `MaterialButton`:** the helper works with any view that has `setOnClickListener`. `findViewById` returns the declared type; here it is `View`, because the helper doesn't need anything specific to a button.

> **Without the declaration in the manifest, the click crashes.** `startActivity` throws `ActivityNotFoundException` at runtime, not at compile time. The compiler doesn't know which activities exist in the app.

### `activity_main.xml` — the three buttons

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Root: a vertical column, with the content centered vertically and padding on all sides. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center_vertical"
    android:orientation="vertical"
    android:padding="24dp">

    <!-- The screen title: "From ListView to RecyclerView" -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/main_heading"
        android:textAppearance="?attr/textAppearanceHeadlineSmall" />

    <!-- The subtitle: "The numbers from 1 to 100, displayed in three steps." -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:layout_marginBottom="24dp"
        android:text="@string/main_description"
        android:textAppearance="?attr/textAppearanceBodyMedium" />

    <!-- Button 1: the id btnStep1 is looked up in MainActivity.openOnClick -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="@string/step1_title" />

    <!-- Button 2: 8dp below the first one -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep2"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="@string/step2_title" />

    <!-- Button 3: 8dp below the second one -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep3"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="@string/step3_title" />
</LinearLayout>
```

**`orientation="vertical"`** — the children are stacked one below the other. `gravity="center_vertical"` centers the **group** of children vertically inside the parent. Don't confuse it with `layout_gravity`, which positions the view within its parent.

**`padding="24dp"`** — inner margin on all four sides. The buttons don't touch the edges of the screen.

**`layout_width="match_parent"` on the buttons** — buttons as wide as the screen, perfectly aligned. `wrap_content` would make them as wide as their text, and the three would have different widths.

**The texts come from `strings.xml`**, they are not written in the XML: `main_heading`, `main_description`, `step1_title`, `step2_title`, `step3_title`. A hardcoded text would raise a lint warning and could not be translated.

**`?attr/textAppearanceHeadlineSmall`** — the title style from the Material3 theme. `Theme.AdaptersDemo` has `Theme.Material3.DayNight` as its parent, so all the `?attr/...` attributes resolve.

**`MaterialButton` is written with its full name** (`com.google.android.material.button.MaterialButton`) because it is not a class from `android.widget`, but from the Material library.

### `AndroidManifest.xml` — the four activities

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- There is no `package` attribute: the app name comes from `namespace` in build.gradle.kts -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.AdaptersDemo">

        <!-- The only activity that can be started from the outside: the launcher one -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- The steps: started only from MainActivity, hence exported="false" -->
        <activity
            android:name=".activities.SingleColumnActivity"
            android:exported="false"
            android:label="@string/step1_title" />

        <activity
            android:name=".activities.TwoColumnActivity"
            android:exported="false"
            android:label="@string/step2_title" />

        <activity
            android:name=".activities.RecyclerViewActivity"
            android:exported="false"
            android:label="@string/step3_title" />
    </application>
</manifest>
```

**No `package=`** — modern versions of the Android Gradle Plugin take the name from `namespace` (`ro.ase.ie.dma06`). That is why the relative names `.activities.MainActivity` resolve to `ro.ase.ie.dma06.activities.MainActivity`.

**`exported="true"` only on `MainActivity`** — it is the only one with an `<intent-filter>` containing `MAIN` + `LAUNCHER`. Since Android 12 (API 31) declaring `exported` is mandatory for any component with an intent-filter. The other three are internal, hence `false`: no other app can start them.

**`android:label` on each activity** — the title in the top bar. `Theme.Material3.DayNight` has an ActionBar, so the step 1 screen reads "Step 1: ListView", step 2 reads "Step 2: Two columns", etc.

**`supportsRtl="true"`** — allows layouts to be mirrored in RTL languages. That is why in `item_number.xml` the second `TextView` uses `gravity="end"`, not `right`.

---

## 28.1 `NumberData.java` — the data source

### The complete file, annotated

```java
package ro.ase.ie.data;          // ATTENTION: the declared package does NOT contain `dma06`

import java.util.ArrayList;      // the concrete implementation of the list
import java.util.List;           // the interface used in signatures

/** The data source shared by all three steps. */
public final class NumberData {

    private static final int FIRST_NUMBER = 1;    // the first number in the list
    private static final int LAST_NUMBER = 100;   // the last number, inclusive

    private NumberData() {
        // This class only has static methods
    }

    public static List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();     // a new list on every call
        for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {
            numbers.add(number);                       // autoboxing: int → Integer
        }
        return numbers;
    }
}
```

### The package does not match the folder

The folder is `ro/ase/ie/dma06/data/`, but the declared package is `ro.ase.ie.data`. This is not a typo to skim past — it really is like that in the repo, and the same goes for `NumberListAdapter` / `NumberRecyclerAdapter`, which declare `ro.ase.ie.adapters`.

**Why it compiles:** Gradle hands the compiler the explicit list of source files, and `javac` does not require the folder to match the package when the files are given directly. The folder–package match only matters when the compiler **looks up** a class on the classpath.

**The practical consequence:** imports use the declared package, not the folder path:

```java
import ro.ase.ie.data.NumberData;          // correct, this is how it is in the repo
// import ro.ase.ie.dma06.data.NumberData; // wrong — the class does not exist in that package
```

> If you "fix" the package to match the folder, you also have to change the three imports in the activities. In the test, write exactly what is in the repo.

### `final` on the class and a `private` constructor

**`public final class NumberData`** — the class cannot be extended. A utility class has nothing to offer through inheritance; `final` closes the discussion.

**The `private` constructor** — nobody can do `new NumberData()`. All the methods are `static`, so you don't need an instance. It is the standard trick for utility classes: if you can't instantiate it, nobody will do it by mistake.

**The comment in the constructor** — "This class only has static methods" — documents **why** it is empty. An empty private constructor without an explanation looks like an oversight.

### The constants

```java
private static final int FIRST_NUMBER = 1;
private static final int LAST_NUMBER = 100;
```

Two magic numbers get names. If you want 1–1000, you change a single line. And the loop becomes readable: "from `FIRST_NUMBER` to `LAST_NUMBER`".

**`static`** — they belong to the class, not to an instance (and there are no instances anyway).
**`final`** — they never change.
**`private`** — nobody outside needs them.

### `getNumbers()`

```java
public static List<Integer> getNumbers() {
    List<Integer> numbers = new ArrayList<>();
    for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {
        numbers.add(number);
    }
    return numbers;
}
```

**A new list on every call** — this is essential. There is no shared `static` field. Each of the three activities calls `getNumbers()` in `onCreate` and receives **its own** list. If it were a singleton, a change made in one screen would appear in all the others, without you knowing where it came from.

**`List` in the signature, `ArrayList` in the implementation** — you return the interface, you build the implementation. Whoever receives the list doesn't depend on `ArrayList`; you can switch to `LinkedList` without touching anything else.

**`<=` and not `<`** — `LAST_NUMBER` is **inclusive**. The loop yields exactly 100 elements: 1, 2, …, 100. With `<` you would have 99.

**Autoboxing** — `numbers.add(number)` takes an `int`, but the list is `List<Integer>`. The compiler automatically turns it into `Integer.valueOf(number)`. For the values −128…127, `Integer.valueOf` returns cached instances, so for 1–100 no 100 new objects are created.

**Zero `android.*` imports** — this class could also run on the desktop, in an ordinary JUnit test. It doesn't depend on `Context`, `View` or `Adapter`. The package split is not cosmetic: it allows the source to be tested without an emulator.

### Who calls `getNumbers()`

| Activity | What it does with the list |
|---|---|
| `SingleColumnActivity` | passes it straight to `ArrayAdapter` |
| `TwoColumnActivity` | passes it to `NumberListAdapter` |
| `RecyclerViewActivity` | passes it to `NumberRecyclerAdapter` |

The same data, three different renderings. That is the whole experiment.

---

## 28.2 `SingleColumnActivity.java` — step 1

### The complete file, annotated

```java
package ro.ase.ie.dma06.activities;

import android.os.Bundle;
import android.widget.ArrayAdapter;   // the ready-made adapter from the SDK
import android.widget.ListView;      // the widget that displays the list

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.data.NumberData;    // the declared package, not the folder
import ro.ase.ie.dma06.R;


/**
 * Step 1: one column.
 * ArrayAdapter is enough because each row shows one text value.
 */
public class SingleColumnActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_single_column);   // the layout root IS the ListView

        ListView lvNumbers = findViewById(R.id.lvNumbers); // the only view in the layout

        // ArrayAdapter calls toString() on each number and shows it in a TextView
        ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
                this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
        lvNumbers.setAdapter(adapter);                     // binds the list to the widget
    }
}
```

### The three arguments of `ArrayAdapter`

```java
ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
        this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
```

| Argument | What it is | Why |
|---|---|---|
| `this` | `Context` | the adapter needs it to inflate the row |
| `android.R.layout.simple_list_item_1` | a **system** layout | contains a single `TextView`, with the id `android.R.id.text1` |
| `NumberData.getNumbers()` | `List<Integer>` | the data; the adapter holds the **reference**, not a copy |

The `ArrayAdapter<Integer>` generic must match the type of the list. If you used `ArrayAdapter<String>`, you would need a `List<String>` — and you would lose the numeric type.

### What `ArrayAdapter` does for you

**It calls `toString()` on each element.** For `Integer`, `toString()` returns exactly the number: `1` → `"1"`. The list shows "1", "2", "3" … "100".

**It recycles rows.** `ArrayAdapter` implements `getView` with `convertView` — exactly the mechanism from step 2, only hidden inside the SDK. Recycling is **not** a `RecyclerView` invention; `ListView` has done it from the start. The difference is that here you don't control it.

**It has no visible `ViewHolder`.** `ArrayAdapter` looks up `android.R.id.text1` in the row it receives and fills it. With a single `TextView`, the lookup is cheap and not worth a holder.

### The limitation that gives birth to step 2

`ArrayAdapter` knows **a single** `TextView` per row. If you want two columns — decimal and binary — there is nowhere to put them. It is not a configuration limitation, it is a design limitation: one text per item.

Step 1 ends here.

### `activity_single_column.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- The layout root is the ListView itself: setContentView attaches it directly. -->
<ListView xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/lvNumbers"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

**The root is the `ListView`** — not a `LinearLayout` wrapping it. `setContentView` receives the list directly, and `findViewById(R.id.lvNumbers)` finds it in the activity's view tree.

**`match_parent` on both dimensions** — the list fills the whole screen.

**No `android:entries`** — the list has no data from XML. The only source is the adapter. If you forget `setAdapter`, the screen stays empty, with no error.

**No `android:divider`** — the separator comes from the `ListView`'s default theme. On `RecyclerView` there is no such thing (see 28.6).

---

## 28.3 `NumberListAdapter.java` — step 2, the custom adapter

### Block 1: the declaration, `ViewHolder`, the fields, the constructor

```java
package ro.ase.ie.adapters;   // the declared package does not contain `dma06`, though the folder does

import android.content.Context;      // needed only for LayoutInflater
import android.view.LayoutInflater;  // turns XML into View objects
import android.view.View;            // the row (inflated or recycled)
import android.view.ViewGroup;       // the row's parent: the ListView
import android.widget.BaseAdapter;   // the base class for custom adapters
import android.widget.TextView;      // the two columns

import java.util.List;               // the interface for the list of numbers

import ro.ase.ie.dma06.R;            // the app's resources

/** Step 2: fills a two-column row for a ListView. */
public class NumberListAdapter extends BaseAdapter {

    private static class ViewHolder {
        TextView tvDecimal;   // the reference to column 1
        TextView tvBinary;    // the reference to column 2
    }

    private final List<Integer> numbers;          // the data source, held by reference
    private final LayoutInflater layoutInflater;  // a single inflater, reused

    public NumberListAdapter(Context context, List<Integer> numbers) {
        this.layoutInflater = LayoutInflater.from(context);  // we get it once, not on every row
        this.numbers = numbers;                              // we do NOT copy the list
    }
```

**Why `BaseAdapter` and not `ArrayAdapter`:** `ArrayAdapter` is a complete, ready-made implementation for a single text. `BaseAdapter` is the skeleton: it implements the `ListAdapter` and `SpinnerAdapter` interfaces, but leaves **four abstract methods** — `getCount`, `getItem`, `getItemId`, `getView`. You write exactly what is missing.

**Why `ViewHolder` is an inner class:** the two `TextView`s have to travel together. A holder is a box with two references, hung on the row with `setTag`. Without it, you would have two separate variables and nowhere to keep them between calls.

**Why `private`:** only this adapter uses it. It doesn't appear in any public signature.

**Why `static`:** a non-static inner class holds an implicit reference to the outer instance (`this$0`). The `ViewHolder` is glued to a `View`, and the `View` can live longer than the adapter — `ListView` keeps it in its RecycleBin. If the holder held the adapter, every recycled row would keep the adapter alive. `static` removes the reference: the holder holds only two `TextView`s. Logically, it doesn't even need the adapter to exist.

**Why the holder's fields are not `final`:** they are assigned **after** `new ViewHolder()`, in `getView`. They cannot be `final` because they are not initialized in a constructor. This is exactly what the `RecyclerView` version fixes: it moves `findViewById` into the holder's constructor and can make them `final`.

**`private final List<Integer> numbers`** — the reference never changes. The contents of the list could change, but the adapter always points at the same list.

**`private final LayoutInflater layoutInflater`** — `LayoutInflater.from(context)` performs an internal lookup. We do it **once**, in the constructor, not on every row. On top of that, `getView` no longer needs a `Context`.

**`this.numbers = numbers`** — the list is not copied. The adapter receives the reference to the list built by `NumberData`. If you modified the list from the outside, the adapter would see the change — but it would not redraw anything without `notifyDataSetChanged()`.

### Block 2: the three "bookkeeping" methods

```java
    @Override
    public int getCount() {
        return numbers.size();      // how many rows: exactly the list's elements
    }

    @Override
    public Integer getItem(int position) {
        return numbers.get(position);   // the object at the given position
    }

    @Override
    public long getItemId(int position) {
        // Each number is unique, so the number itself can be the ID
        return numbers.get(position);   // Integer → int → long (widening)
    }
```

**`getCount()`** — the first thing `ListView` asks. It determines how many rows exist and how long the scrollbar is. If you return 0, the list is empty.

**`getItem(position)`** — the object at the given position. `ListView` calls it when someone asks for the item at a position (`getItemAtPosition`), and the adapter calls it itself inside `getView`.

**`getItemId(position)`** — the item's identity. `numbers.get(position)` returns an `Integer`, which is **unboxed** to `int` and then **widened** to `long` (widening, a safe implicit conversion). Because the numbers 1–100 are unique, the number itself is a valid ID. In a list with duplicates (two movies with the same title) you would need a separate `id` field.

**When `getItemId` is used:** `ListView` calls it when it builds the arguments of a click. A stable identity (`hasStableIds() == true`) would let the widget keep the selection across reloads; here it is `false` by default, but the method has to be implemented anyway — it is abstract in `BaseAdapter`.

**`@Override` on all three** — the methods come from `Adapter` / `BaseAdapter`. Without the annotation they would still be overrides, but the compiler would not flag a wrong signature.

### Block 3: `getView` — the heart of the adapter

```java
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;

        if (convertView == null) {
            // New row: inflate it and store its views
            convertView = layoutInflater.inflate(R.layout.item_number, parent, false);
            holder = new ViewHolder();
            holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);
            holder.tvBinary = convertView.findViewById(R.id.tvBinary);
            convertView.setTag(holder);
        } else {
            // Reused row: get its stored views
            holder = (ViewHolder) convertView.getTag();
        }

        int number = getItem(position);
        holder.tvDecimal.setText(String.valueOf(number));
        holder.tvBinary.setText(Integer.toBinaryString(number));

        return convertView;
    }
```

#### The signature

| Parameter | What it means |
|---|---|
| `position` | which row of the list it is (0…99) |
| `convertView` | a row **recycled** by `ListView`, or `null` if none is free |
| `parent` | the `ListView` asking for the row |

#### The two branches

```
convertView == null   →  NEW row:      inflate + findViewById + setTag
convertView != null   →  REUSED row:   getTag, no lookup at all
```

At startup, `ListView` asks for the first ~10 rows with `convertView == null` — there is nothing to recycle. Then, on every scroll, the row that leaves the screen goes into the RecycleBin and is handed back on the next call:

```
getView(0,  null, listView)   → null → inflate + findViewById + setTag   (new row)
getView(1,  null, listView)   → null → inflate + findViewById + setTag   (new row)
...
getView(9,  null, listView)   → null → inflate + findViewById + setTag   (new row)
      ── you scroll one position ──
getView(10, row0, listView)   → != null → getTag + setText              (reused row)
```

**Why `inflate(R.layout.item_number, parent, false)`:**

- `parent` is needed so the correct `LayoutParams` is generated for the row. Without it, `inflate` doesn't know which parameters to create, and the `match_parent` in the XML cannot be interpreted.
- `false` means **do not attach now**. `ListView` will attach the row when its turn comes. With `true`, `inflate` would return the **parent**, not the row — and you would get a `ListView` instead of a row.

**`findViewById` twice** — only on the new row. The lookup walks the view tree; on a row with two `TextView`s it is cheap, but multiplied by 100 rows and by every scroll it becomes noticeable.

**`convertView.setTag(holder)`** — `View.setTag(Object)` is a free field on any `View`. It has nothing to do with display; it is just a place where you hang an object. Here we glue the holder to its row.

**`holder = (ViewHolder) convertView.getTag()`** — `getTag()` returns `Object`, so a cast is needed. The cast is **not checked** by the compiler: if you put something else in the tag, `ClassCastException` at runtime; if you forgot `setTag`, `getTag()` returns `null` and you get a `NullPointerException` on the first line that touches the holder.

> **Without `setTag`:** the list works until the first scroll. Then it crashes with a `NullPointerException`. It is the most common mistake with a `ListView` and a custom adapter.

#### The filling part

```java
int number = getItem(position);                    // Integer → int (unboxing)
holder.tvDecimal.setText(String.valueOf(number));  // "42"
holder.tvBinary.setText(Integer.toBinaryString(number));  // "101010"
```

**`int number = getItem(position)`** — `getItem` returns an `Integer`, the assignment unboxes it. If the list contained `null`, you would get a `NullPointerException` here. It doesn't happen here: `NumberData` produces 1–100.

**`String.valueOf(number)`** — equivalent to `Integer.toString(number)`. More explicit than `number + ""`, which creates an extra `StringBuilder`.

**`Integer.toBinaryString(number)`** — the binary representation without leading zeros and without a prefix: `1` → `"1"`, `100` → `"1100100"`. That is why the second column is not nicely aligned to the left, and `item_number.xml` aligns it to the right and gives it a monospaced font.

**`return convertView`** — returns exactly the row it received, now filled. You don't build a new `View` on every call; that is the whole saving.

#### What would happen if you ignored recycling

If you called `inflate` on every call and always returned a new row:

- 100 inflated rows for 100 items, even though only ~10 fit on the screen;
- memory grows with every scroll;
- `ListView` has nothing left to recycle, so `convertView` stops coming too;
- scrolling becomes jerky.

The code would be **correct** — it would display the same numbers — but it would be slow. Recycling is an optimization, not correctness.

---

## 28.4 `TwoColumnActivity.java`

### The complete file, annotated

```java
package ro.ase.ie.dma06.activities;

import android.os.Bundle;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.adapters.NumberListAdapter;   // the custom adapter, from the `adapters` package
import ro.ase.ie.data.NumberData;             // the same data as in step 1
import ro.ase.ie.dma06.R;


/**
 * Step 2: two columns in a ListView.
 * A custom adapter fills each column of the row layout.
 */
public class TwoColumnActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_two_column);

        ListView lvNumbers = findViewById(R.id.lvNumbers);   // THE SAME id as in step 1

        NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
        lvNumbers.setAdapter(adapter);
    }
}
```

**The same id, a different layout** — `lvNumbers` appears both in `activity_single_column.xml` and in `activity_two_column.xml`. That is not a problem: ids are unique **per layout**, not globally. `findViewById` searches only the tree of the current layout, so it finds the `ListView` of the current screen.

**`this` as `Context`** — the adapter needs it for `LayoutInflater`. This is the only place where the activity touches the inflation detail.

**The activity doesn't know what is in a row** — there is no `findViewById(R.id.tvDecimal)` here. The two columns are the adapter's job. If you rename `tvDecimal` in the XML, only `NumberListAdapter` changes.

**Comparison with step 1:** the same structure, four lines, only the adapter class different. The lesson: **the activity barely changes; the adapter is where everything happens.**

### `activity_two_column.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- A vertical column: the header on top (as tall as its content), the list below (the rest of the screen). -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- The header is a separate file, reused by step 3 as well -->
    <include layout="@layout/layout_number_header" />

    <!-- The ListView takes all the space left after the header -->
    <ListView
        android:id="@+id/lvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

**`<include layout="@layout/layout_number_header" />`** — the content of the included file is inflated **in place of** the tag. The result is as if you had written the header directly here, but the definition exists in a single place and is used by two screens.

**`layout_height="0dp"` + `layout_weight="1"`** — in a vertical `LinearLayout`, `0dp` + `weight` means "take everything left after the others". The header has `wrap_content`, so it takes its own height; the list gets the rest.

> **Without `weight`:** if the `ListView` had `match_parent`, it would ask for the parent's full height, overflow the bottom edge and get clipped. The header would stay at the top, but the list would no longer fit. `0dp` + `weight="1"` is the correct version.

**Why the header is outside the list:** it stays fixed when you scroll. If it were the first item in the list, it would scroll along with it — and you would need an adapter with two row types (`getItemViewType`), much more complicated for a static header.

### `layout_number_header.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- The two-column header. It has no ids: the code never touches it. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="?attr/colorSurfaceVariant"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="12dp">

    <!-- Column 1: "Decimal" -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="@string/decimal"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <!-- Column 2: "Binary", aligned to the right -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:gravity="end"
        android:text="@string/binary"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />
</LinearLayout>
```

**`background="?attr/colorSurfaceVariant"`** — a different background shade, so the header stands out from the rows. It comes from the Material3 theme, so it works in dark mode too.

**`textColor="?attr/colorOnSurfaceVariant"`** — the text color suited to that background. The `colorSurfaceVariant` / `colorOnSurfaceVariant` pair is designed together; if you hardcode a `#888`, the text disappears in dark mode.

**`textAppearanceLabelLarge`** — the label style, smaller and bolder than the row text (`BodyLarge`).

**No ids** — nothing in the code touches the header. It is purely visual.

**The alignment must match `item_number.xml`:** the same `paddingHorizontal="16dp"`, the same `weight="1"`, the same `gravity="end"` on the second column. They are two separate files, so the match is made by hand. If you change the padding in only one of them, the header no longer lines up with the rows — and it shows immediately.

---

## 28.5 `NumberRecyclerAdapter.java` — step 3

### Block 1: the declaration, `ViewHolder`, the field, the constructor

```java
package ro.ase.ie.adapters;   // the same package as NumberListAdapter

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;                 // contract: a parameter / result that is not null
import androidx.recyclerview.widget.RecyclerView;  // the base class and its ViewHolder

import java.util.List;

import ro.ase.ie.dma06.R;

/**
 * Step 3: fills the same row for a RecyclerView.
 * The ViewHolder is required here, and getView is split into two methods.
 */
public class NumberRecyclerAdapter
        extends RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder> {

    static class NumberViewHolder extends RecyclerView.ViewHolder {
        final TextView tvDecimal;
        final TextView tvBinary;

        NumberViewHolder(@NonNull View itemView) {
            super(itemView);
            tvDecimal = itemView.findViewById(R.id.tvDecimal);
            tvBinary = itemView.findViewById(R.id.tvBinary);
        }
    }

    private final List<Integer> numbers;

    public NumberRecyclerAdapter(List<Integer> numbers) {
        this.numbers = numbers;
    }
```

**The generic parameter** — `RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder>` declares **what type of holder** the adapter produces. From here on, all the methods work with `NumberViewHolder`, not with `RecyclerView.ViewHolder`: `onCreateViewHolder` returns it, `onBindViewHolder` receives it. **No cast anywhere** — that is the gain over `getTag()`.

**`NumberViewHolder extends RecyclerView.ViewHolder`** — the base class holds `itemView` (the row) and offers methods such as `getAdapterPosition()`. By extending it, the holder becomes the type `RecyclerView` knows how to manage.

**`super(itemView)`** — mandatory. `RecyclerView.ViewHolder` has no no-argument constructor, so the compiler forces you to call it. It stores the row in `itemView`.

**`findViewById` in the holder's constructor** — this is the **creation** half. It runs once per holder, not on every display.

**The `final` fields** — they can be `final` because they are assigned in the constructor. In `NumberListAdapter` they could not be, because they were assigned after `new ViewHolder()`. This small difference is exactly why `RecyclerView` moved the lookup into the constructor.

**`static class NumberViewHolder`** — `static` again, for the same two reasons: no implicit reference to the adapter and no dependency on an adapter instance. Here it is a `static class` without `private`: the type appears in the class's public signature (`RecyclerView.Adapter<...NumberViewHolder>`), so there is no point hiding it. In `NumberListAdapter` the holder is a `private static class`, because it doesn't appear in any public signature.

**The adapter's constructor takes only the list** — unlike `NumberListAdapter`, it doesn't need a `Context`. The context is taken when needed from `parent.getContext()`, in `onCreateViewHolder`.

### Block 2: `onCreateViewHolder` — the creation half

```java
    @NonNull
    @Override
    public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Runs only when a new row is needed
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_number, parent, false);
        return new NumberViewHolder(view);
    }
```

**When it runs:** only when `RecyclerView` needs a **new** holder — the recycling pool is empty. At startup, for the first visible rows; then less and less often.

**`parent`** — the `RecyclerView`. The `Context` for the inflater is taken from it, and it supplies the `LayoutParams`.

**`viewType`** — here it is always 0, because we don't override `getItemViewType`. If you had two kinds of rows (header + item), you would return 0/1 from `getItemViewType` and `switch` here, to inflate the right layout.

**`LayoutInflater.from(parent.getContext())`** — there is no longer any need for a `layoutInflater` field, because `parent` carries the context with it.

**`.inflate(R.layout.item_number, parent, false)`** — exactly the same call as with `ListView`: the same layout, the same parameters, the same `false`.

**`return new NumberViewHolder(view)`** — returns the **holder**, not the view. `RecyclerView` needs the holder so it knows what it created and can recycle it.

**`@NonNull`** — contract: `parent` is not null, the result is not null. Lint checks it.

### Block 3: `onBindViewHolder` and `getItemCount`

```java
    @Override
    public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
        // Runs each time a row shows a number
        int number = numbers.get(position);
        holder.tvDecimal.setText(String.valueOf(number));
        holder.tvBinary.setText(Integer.toBinaryString(number));
    }

    @Override
    public int getItemCount() {
        return numbers.size();
    }
```

**When it runs:** every time a row **shows** an item — on first display, on every reuse after a scroll, after `notifyItemChanged`, after an animation.

**There is no `convertView`** — the holder arrives already created. There is no `if (convertView == null)`, because the decision has already been made by `RecyclerView`.

**There is no `findViewById`** — the references are in the holder, taken at creation time.

**`numbers.get(position)` directly** — the adapter has no `getItem(position)`. If you need it (for a click, for example), you add it as your own method.

**`getItemCount()` replaces `getCount()`** — the same role: how many items the list has.

> **If `getItemCount()` lies:** if it returns more than `numbers.size()`, `onBindViewHolder` reaches `numbers.get(position)` with an invalid position → `IndexOutOfBoundsException`. If it returns less, the last items simply don't appear.

### What `RecyclerView` does with the two methods

```
A holder leaves the screen
    → RecyclerView puts it in the RecycledViewPool, under its type (viewType)

A new row has to be displayed
    → does the pool have a free holder?
         yes → onBindViewHolder(holder, position)                 (cheap)
         no  → onCreateViewHolder(...) + onBindViewHolder(...)    (expensive, once)
```

This is exactly the `if (convertView == null)` from `getView`, except that:

1. the **framework** makes the decision, not your code;
2. the holder is **typed** — there is no more `setTag`, `getTag` or cast;
3. the two branches are **separate methods**, so you can reason about them independently.

**Why the separation matters beyond speed:** `RecyclerView` can refill an existing holder without creating anything. On a data change (`notifyItemChanged(5)`), it rebinds only row 5. On a move animation, it rebinds only what changed. With a single `getView` that receives `convertView`, the framework would have had to guess what is creation and what is filling.

**Optional methods that `ListView` doesn't have:** `onViewRecycled(holder)` (the holder enters the pool — you can cancel an image download), `onViewAttachedToWindow` / `onViewDetachedFromWindow`, `getItemViewType`. All have default implementations; you are not forced to write them.

---

## 28.6 `RecyclerViewActivity.java`

### The complete file, annotated

```java
package ro.ase.ie.dma06.activities;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.DividerItemDecoration;   // the line between rows
import androidx.recyclerview.widget.LinearLayoutManager;    // the vertical arrangement
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.adapters.NumberRecyclerAdapter;
import ro.ase.ie.data.NumberData;
import ro.ase.ie.dma06.R;


/**
 * Step 3: the same two columns in a RecyclerView.
 * RecyclerView needs a LayoutManager, and dividers are added separately.
 */
public class RecyclerViewActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_recycler_view);

        RecyclerView rvNumbers = findViewById(R.id.rvNumbers);

        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        rvNumbers.setLayoutManager(layoutManager);
        rvNumbers.addItemDecoration(
                new DividerItemDecoration(this, layoutManager.getOrientation()));

        NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
        rvNumbers.setAdapter(adapter);
    }
}
```

### The three mandatory pieces

A working `RecyclerView` needs:

1. **`LayoutManager`** — how the rows are arranged;
2. **adapter** — what is displayed;
3. **`ItemAnimator`** — the animations; it comes by default, you don't configure it here.

`ListView` has the arrangement built into it and only limited animations. `RecyclerView` pulled the pieces out, so you can change them independently.

### Why `LayoutManager` is separate

**`RecyclerView` doesn't know how to arrange.** It only knows how to recycle holders and to ask a `LayoutManager` what to do: how many children fit, where each one sits, how the scroll is computed, how tall each row is.

**The practical consequence:** you swap `LinearLayoutManager` for `GridLayoutManager(this, 2)` and get a two-column grid — **without changing a single line in the adapter**. With `ListView`, the arrangement is in the widget's code; there is no way to change it.

**`new LinearLayoutManager(this)`** — the single-argument constructor means vertical. The full version: `LinearLayoutManager(context, orientation, reverseLayout)`.

**`setLayoutManager` before `setAdapter`** — the order is not fatal, but it is the convention. What **is** fatal: forgetting `setLayoutManager`. Then `RecyclerView` displays nothing and raises no error — just a message in Logcat: `No layout manager attached; skipping layout`.

### `DividerItemDecoration` — the separator

**`ListView` has `android:divider` in XML.** `RecyclerView` has no such thing. The lines between rows are drawn by an `ItemDecoration`, and `DividerItemDecoration` is the ready-made decoration from the library.

**`layoutManager.getOrientation()`** — returns `RecyclerView.VERTICAL`, that is `1`. `DividerItemDecoration` expects its own constant, `DividerItemDecoration.VERTICAL`, which is also `1`. They are two constants different in meaning but with the same values (`0` = horizontal, `1` = vertical in both classes), so the line works.

> **The compiler cannot check it:** both are `int`. If you switched the `LayoutManager` to horizontal, `getOrientation()` would return `0`, which is also `DividerItemDecoration.HORIZONTAL` — so the code stays correct. The match is real, not accidental, but it relies on numeric values, not on a shared type.

**`addItemDecoration` before `setAdapter`** — the order between them doesn't matter. The decoration is applied at drawing time, not when the data is set.

### The adapter and the data

```java
NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

**No `Context`** — the adapter takes it from `parent` at creation time.
**No `notifyDataSetChanged()`** — the data is fixed, and `setAdapter` triggers the first layout by itself.

### `activity_recycler_view.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- The same structure as in step 2: a fixed header on top, the list below. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- The same header, from the same file -->
    <include layout="@layout/layout_number_header" />

    <!-- The full name: RecyclerView is not in android.widget, but in the AndroidX library -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

**The full name is mandatory** — `RecyclerView` is not a class from `android.widget`, so the XML cannot shorten it. The same happens with any view from libraries: `com.google.android.material.button.MaterialButton`, `androidx.recyclerview.widget.RecyclerView`.

**`0dp` + `weight="1"`** — the same logic: the header is `wrap_content`, the list takes the rest.

**No explicit dependency in `build.gradle.kts`** — there is no `implementation(libs.recyclerview)` line. The class resolves because the Material library (`com.google.android.material:material`) brings `androidx.recyclerview` transitively. If you removed Material, the import would break.

---

## 28.7 `item_number.xml` — a single layout for two adapters

### The complete file, annotated

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- One row with two columns. Steps 2 and 3 both use this layout. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="14dp">

    <!-- Column 1: the decimal number, aligned to the left -->
    <TextView
        android:id="@+id/tvDecimal"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:textAppearance="?attr/textAppearanceBodyLarge" />

    <!-- Column 2: the binary number, aligned to the right, with a monospaced font -->
    <TextView
        android:id="@+id/tvBinary"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:fontFamily="monospace"
        android:gravity="end"
        android:textAppearance="?attr/textAppearanceBodyLarge" />
</LinearLayout>
```

**The comment at the top of the file** — "Steps 2 and 3 both use this layout" — is the very core of the chapter. The same XML file serves the `ListView` of step 2 and the `RecyclerView` of step 3. The difference between the two is **not in the layout**, but in the adapter.

**`orientation="horizontal"`** — two columns, one next to the other.

**`match_parent` × `wrap_content`** — the row is as wide as the list and as tall as its content. The `wrap_content` height adapts to an enlarged font; a fixed height would clip the text.

**`paddingHorizontal="16dp"` / `paddingVertical="14dp"`** — inner spacing. `paddingHorizontal` and `paddingVertical` exist since API 26, and the project has `minSdk 33`, so it works.

**`0dp` + `layout_weight="1"` on both `TextView`s** — each takes half the width. It is the equivalent of "50% / 50%". If you used `wrap_content`, each column would be as wide as its text, and the columns would no longer line up across rows.

**`fontFamily="monospace"`** — the digits have the same width, so the binary numbers line up nicely on the right. It is a system font, not a file added to the project.

**`gravity="end"`** — right alignment that respects the reading direction. With `supportsRtl="true"` in the manifest, in an RTL language it automatically becomes left. `right` would have stayed right forever.

**No `android:text`** — the row is empty in the preview and is filled at runtime. Without an adapter, you would see 100 empty rows.

**The two ids are the contract** — `tvDecimal` and `tvBinary` are looked up by **both** adapters. If you rename them, they have to be changed in two Java files.

### The same layout, two `inflate` calls

The block below juxtaposes two real fragments, each labelled with the method it comes from.

```java
// NumberListAdapter.getView
convertView = layoutInflater.inflate(R.layout.item_number, parent, false);

// NumberRecyclerAdapter.onCreateViewHolder
View view = LayoutInflater.from(parent.getContext())
        .inflate(R.layout.item_number, parent, false);
```

The same file, the same parameters, the same `false`. The only thing that differs is the surrounding method: one receives a possibly recycled `convertView`, the other creates a new holder.

---

## 28.8 The final comparison, line by line

### The exact correspondence between the two adapters

| # | `NumberListAdapter` (ListView) | `NumberRecyclerAdapter` (RecyclerView) | When it runs |
|---|---|---|---|
| 1 | `public int getCount()` | `public int getItemCount()` | on every measurement of the list |
| 2 | `public Integer getItem(int position)` | — (`numbers.get(position)` is used directly) | on demand (`getItemAtPosition`), and at bind time respectively |
| 3 | `public long getItemId(int position)` | — (`getItemId` is optional, `NO_ID` by default) | on click |
| 4 | `public View getView(int position, View convertView, ViewGroup parent)` | `onCreateViewHolder(parent, viewType)` + `onBindViewHolder(holder, position)` | when needed |
| 5 | `if (convertView == null)` | `RecyclerView` makes the decision: is the pool empty? | when needed |
| 6 | `layoutInflater.inflate(R.layout.item_number, parent, false)` | `LayoutInflater.from(parent.getContext()).inflate(...)` | once per created row |
| 7 | `holder = new ViewHolder()` | `new NumberViewHolder(view)` | once per created row |
| 8 | `holder.tvDecimal = convertView.findViewById(...)` | `tvDecimal = itemView.findViewById(...)` in the constructor | once per created row |
| 9 | `convertView.setTag(holder)` | `super(itemView)` + `RecyclerView`'s internal bookkeeping | once per created row |
| 10 | `holder = (ViewHolder) convertView.getTag()` | the holder arrives as a parameter in `onBindViewHolder` | on every display |
| 11 | `holder.tvDecimal.setText(...)` | `holder.tvDecimal.setText(...)` | on every display |
| 12 | `return convertView` | `void` — the holder is already with `RecyclerView` | on every display |

### What disappears when moving to `RecyclerView`

| Gone | Replaced by |
|---|---|
| the `convertView` parameter | the internal holder pool |
| `setTag(holder)` / `getTag()` | the generic type `RecyclerView.Adapter<...NumberViewHolder>` |
| the `(ViewHolder)` cast | the `holder` parameter, already typed |
| `if (convertView == null)` | `RecyclerView`'s internal decision |
| `return convertView` | `onBindViewHolder` returns `void` |
| the `layoutInflater` field | `LayoutInflater.from(parent.getContext())` |
| `getItem(position)` | `numbers.get(position)` directly |

### What appears when moving to `RecyclerView`

| New | Role |
|---|---|
| the generic parameter `RecyclerView.Adapter<...>` | the holder type, checked at compile time |
| `onCreateViewHolder` | creation, separated from filling |
| `onBindViewHolder` | filling, without creation |
| `getItemCount` | replaces `getCount` |
| `super(itemView)` | mandatory in the holder's constructor |
| `@NonNull` | contracts checked by lint |
| `viewType` | support for several row types |
| `LayoutManager` | the arrangement, separated from the content |
| `ItemDecoration` | the separators, separated from the layout |

### The three steps, on the same data

| | Step 1 | Step 2 | Step 3 |
|---|---|---|---|
| Widget | `ListView` | `ListView` | `RecyclerView` |
| Adapter | `ArrayAdapter<Integer>` | `NumberListAdapter` | `NumberRecyclerAdapter` |
| Base | — | `BaseAdapter` | `RecyclerView.Adapter` |
| Row layout | `android.R.layout.simple_list_item_1` | `item_number.xml` | `item_number.xml` |
| Columns per row | 1 | 2 | 2 |
| `ViewHolder` | hidden in the SDK | manual, `setTag`/`getTag` | mandatory, automatic |
| Row creation | in `ArrayAdapter` | in `getView`, the `null` branch | `onCreateViewHolder` |
| Row filling | in `ArrayAdapter` | in `getView`, after the `if` | `onBindViewHolder` |
| Arrangement | fixed vertical | fixed vertical | `LayoutManager` |
| Separator | `android:divider` from the theme | `android:divider` from the theme | `DividerItemDecoration` |
| Animations | no | no | yes, default |
| `notifyDataSetChanged` | yes | yes | yes (or `notifyItemChanged`) |

### The same data, three independent lists

Each activity calls `NumberData.getNumbers()` in `onCreate`. The result: **three different lists**, with the same values. There is no shared state between screens. If you modified the list in step 2, step 3 would see nothing — because it has its own copy.

### Short answers for the test

**"Why isn't `ArrayAdapter` enough?"**
Because it knows a single `TextView` per row. For two columns you need your own layout and an adapter that fills it.

**"What does `convertView` do?"**
It receives the row that left the screen, so you can reuse it. Without it, 100 rows would be inflated for 100 items.

**"Why is `ViewHolder` `static`?"**
So that it doesn't hold an implicit reference to the adapter. The holder is just a box with references to views; it doesn't need the outer instance.

**"Why was `getView` split?"**
Because it does two things with different costs: creation (expensive, rare) and filling (cheap, frequent). `RecyclerView` can call only the second one.

**"Why is `LayoutManager` separate?"**
So that the arrangement is independent of the content. You switch the list to a grid without touching the adapter.

**"What happens without `setLayoutManager`?"**
`RecyclerView` displays nothing and raises no error. Just a message in Logcat.

---

## 28.9 The complete flow

### Startup

```
STARTUP
  MainActivity.onCreate
    ├── setContentView(activity_main)
    ├── openOnClick(btnStep1, SingleColumnActivity.class)
    ├── openOnClick(btnStep2, TwoColumnActivity.class)
    └── openOnClick(btnStep3, RecyclerViewActivity.class)
```

### Step 1 — `ListView` + `ArrayAdapter`

```
CLICK "Step 1: ListView"
  startActivity(new Intent(this, SingleColumnActivity.class))
    ↓
  SingleColumnActivity.onCreate
    ├── setContentView(activity_single_column)      ← the root is the ListView
    ├── findViewById(R.id.lvNumbers)
    ├── NumberData.getNumbers()                      → List<Integer> with 100 elements
    ├── new ArrayAdapter(this, simple_list_item_1, list)
    └── lvNumbers.setAdapter(adapter)
          ↓
  ListView asks getCount()                           → 100
  ListView calls getView(0..9, null, listView)       → 10 inflated rows
  Scroll → getView(10, recycledRow, listView)        → just setText
```

### Step 2 — `ListView` + `NumberListAdapter`

```
CLICK "Step 2: Two columns"
  startActivity(new Intent(this, TwoColumnActivity.class))
    ↓
  TwoColumnActivity.onCreate
    ├── setContentView(activity_two_column)          ← includes the header + ListView
    ├── findViewById(R.id.lvNumbers)
    ├── new NumberListAdapter(this, NumberData.getNumbers())
    └── lvNumbers.setAdapter(adapter)
          ↓
  ListView asks getCount()                           → 100
  getView(0, null, parent)
    ├── inflate(item_number, parent, false)
    ├── new ViewHolder()
    ├── findViewById(tvDecimal) + findViewById(tvBinary)
    └── setTag(holder)
  getView(10, convertView, parent)
    ├── getTag() → holder
    └── setText × 2
```

### Step 3 — `RecyclerView`

```
CLICK "Step 3: RecyclerView"
  startActivity(new Intent(this, RecyclerViewActivity.class))
    ↓
  RecyclerViewActivity.onCreate
    ├── setContentView(activity_recycler_view)
    ├── findViewById(R.id.rvNumbers)
    ├── new LinearLayoutManager(this) → setLayoutManager
    ├── addItemDecoration(new DividerItemDecoration(...))
    ├── new NumberRecyclerAdapter(NumberData.getNumbers())
    └── setAdapter
          ↓
  RecyclerView asks getItemCount()                   → 100
  LayoutManager measures and decides how many holders fit
  onCreateViewHolder(parent, 0)
    ├── inflate(item_number, parent, false)
    └── new NumberViewHolder(view)
          ├── super(itemView)
          └── findViewById(tvDecimal) + findViewById(tvBinary)
  onBindViewHolder(holder, 0..9)                     → setText × 2
  Scroll → recycled holder → onBindViewHolder(holder, 10) → setText × 2
```

### The lifecycle of a row

| Moment | `ListView` | `RecyclerView` |
|---|---|---|
| the row appears for the first time | `getView(pos, null, parent)` → inflate + findViewById | `onCreateViewHolder` + `onBindViewHolder` |
| the row leaves the screen | the `View` enters the RecycleBin | the holder enters the RecycledViewPool |
| the row reappears | `getView(pos, convertView, parent)` → getTag + setText | `onBindViewHolder(holder, pos)` |
| the data changes | `notifyDataSetChanged()` → the whole screen refilled | `notifyItemChanged(pos)` → only that row |
| you tap a row | `OnItemClickListener` → `getItemAtPosition(position)` | a listener set on the view, in `onBindViewHolder` |

**The last row is a design difference, not an API one:** `ListView` has a global listener on the list; `RecyclerView` has no `OnItemClickListener`. You put it on each row, in `onBindViewHolder`, usually on `holder.itemView`. Here it isn't needed — no row is clickable.

### What doesn't change at all

- `NumberData` — the same source, the same 100 numbers.
- `item_number.xml` — the same row, the same two columns.
- `layout_number_header.xml` — the same header.
- The displayed text — "1 / 1", "2 / 10", …, "100 / 1100100".

Only **who** produces the rows and **how** they are arranged changes.

---

## 28.10 What to remember

- **Three steps, the same data.** `ArrayAdapter` → `BaseAdapter` with a manual `ViewHolder` → `RecyclerView.Adapter`. The difference is not in the layout, but in the adapter.
- **`convertView`** is the recycled row. `null` = a new row; non-`null` = reuse it.
- **`setTag` / `getTag`** glue the `ViewHolder` to the row. Without `setTag`, `getTag` returns `null` and the list crashes on the first scroll.
- **`ViewHolder` is `static`** so it doesn't hold a reference to the adapter. In `ListView` it is `private static`; in `RecyclerView` it is `static` (package-private), because it appears in the public signature.
- **`getView` was split** into `onCreateViewHolder` (creation, rare and expensive) and `onBindViewHolder` (filling, frequent and cheap).
- **`LayoutManager` is separate** so the arrangement is independent of the content. Without it, `RecyclerView` is empty and silent.
- **`RecyclerView` has no global `OnItemClickListener`** and no `android:divider`. It replaces them with a per-row listener and an `ItemDecoration`.
- **A lying `getItemCount()`** → `IndexOutOfBoundsException` in `onBindViewHolder`.
- **`inflate(layout, parent, false)`** — `parent` for the `LayoutParams`, `false` so it doesn't attach now.
- **The `data` and `adapters` packages don't contain `dma06`** in their declaration, even though the folders do. Imports use the declared package.
- **`NumberData.getNumbers()` returns a new list** on every call. Three screens, three independent lists.

---

## Chapter 28 summary

- `DMA06` = three steps on the same numbers 1–100: `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter`.
- `NumberData` is clean: `final`, a `private` constructor, a `static` method, zero `android.*` imports.
- Step 1: three lines of adapter, a single `TextView`, no recycling written by you.
- Step 2: `getView` with `if (convertView == null)`, `ViewHolder` + `setTag`/`getTag`, `findViewById` once per row.
- Step 3: `onCreateViewHolder` + `onBindViewHolder` + `getItemCount`, a typed holder, no cast.
- `item_number.xml` is shared by steps 2 and 3 — the proof that the difference is in the adapter.
- `LayoutManager` and `ItemDecoration` are the pieces `ListView` kept inside (fixed arrangement, divider from XML), and `RecyclerView` pulled them out.
- `activity_two_column.xml` and `activity_recycler_view.xml` are almost identical: only the widget differs.

**Back to** [chapter 12](12%20-%20DMA06%20-%20ListView%20vs%20RecyclerView.md) **or to the** [cheatsheet](21%20-%20Cheatsheet.md).
