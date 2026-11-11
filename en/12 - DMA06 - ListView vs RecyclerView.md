# Chapter 12 — DMA06: ListView vs. RecyclerView, in three stages

**Objective:** to understand exactly what changes between `ListView` with `ArrayAdapter`, `ListView` with a custom adapter, and `RecyclerView`. The professor built three screens using **the same data** (numbers 1–100), so the differences are visible.

**Estimated time:** 60–75 min.

**Source:** `DMA06/` at commit `d719ffc` — 37 files, last modified `2d891ef` (2026-11-04).

> **Why this matters to you:** in `G1097` at `d719ffc` you have `ListView` + `ArrayAdapter`. The move to `RecyclerView` that you made locally on 09.11 follows the steps in DMA06 **exactly**. Here you can see the mechanism clearly, with simple data and no form around it.

---

## Step 12.1 — DMA06 project structure

### Why

Before the code, look at how the packages are divided. It's the first example in the repo with a clear separation of responsibilities.

### How

```
DMA06/src/main/java/ro/ase/ie/dma06/
├── activities/
│   ├── MainActivity.java            ← menu with 3 buttons
│   ├── SingleColumnActivity.java    ← Stage 1: ListView + ArrayAdapter
│   ├── TwoColumnActivity.java       ← Stage 2: ListView + custom adapter
│   └── RecyclerViewActivity.java    ← Stage 3: RecyclerView
├── adapters/
│   ├── NumberListAdapter.java       ← BaseAdapter for ListView
│   └── NumberRecyclerAdapter.java   ← RecyclerView.Adapter
└── data/
    └── NumberData.java              ← source: 1..100
```

And in `res/layout/`:
- `activity_main.xml`, `activity_single_column.xml`, `activity_two_column.xml`, `activity_recycler_view.xml`
- `item_number.xml` — **the same row, used by stages 2 and 3**
- `layout_number_header.xml` — the two-column header

### Why the separation matters

Each package has a single role:

| Package | Role | Must not |
|---|---|---|
| `data` | produce data | know about `View`, `Adapter`, `Context` |
| `adapters` | transform data into rows | know about `Activity` |
| `activities` | tie everything together and respond to input | contain per-row display logic |

`NumberData` is the cleanest example:

```java
public final class NumberData {
    private static final int FIRST_NUMBER = 1;
    private static final int LAST_NUMBER = 100;

    private NumberData() {
        // This class only has static methods
    }

    public static List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();
        for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {
            numbers.add(number);
        }
        return numbers;
    }
}
```

Notice: `private` constructor (it can't be instantiated), `static` method, zero `android.*` imports.

> **Remember:** `private` on a constructor is the standard trick for a utility class. If you can't instantiate it, no one can do so by mistake.

---

## Step 12.2 — Stage 1: `ListView` with `ArrayAdapter`

### Why

This is the minimal version. It works only when the row has **a single text**.

### How

`SingleColumnActivity`:

```java
ListView lvNumbers = findViewById(R.id.lvNumbers);
// ArrayAdapter calls toString() on each number and shows it in a TextView
ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
        this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
lvNumbers.setAdapter(adapter);
```

Three lines. That's it.

### What you see

A list with “1,” “2,” “3” … “100,” one per row.

### Why it works without any custom layout

`android.R.layout.simple_list_item_1` is a **system** layout that contains a `TextView` with the id `android.R.id.text1`. `ArrayAdapter` fills it with each element's `toString()`.

For `Integer`, `toString()` returns exactly the number. So `1` → `"1"`.

### The limitation

What do you do if you want **two** columns — decimal and binary? `ArrayAdapter` has a single `TextView`. You can't.

That's where Stage 1 ends.

### Exercise 12.2

**Requirement:** why `ArrayAdapter<Integer>` and not `ArrayAdapter<String>`? What would happen with the latter?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you compared the two generic type variants.

**The answer:** `ArrayAdapter<Integer>` holds a `List<Integer>`. `ArrayAdapter<String>` would require a `List<String>`, so you would have converted each number to a string **before** putting it in the list.

**What you lose:** the type. If you have a `List<String>`, you can no longer call `Integer.toBinaryString(...)` without parsing back. You would throw away the information and then recover it.

**Remember:**
1. The generic type must match the type of the source list.
2. `ArrayAdapter` doesn't need `Integer` — `Object` would also work. But then you'd lose compile-time checking.
3. `toString()` is called on the element, regardless of its type.

**Where it comes back:** in Stage 2, the custom adapter also receives a `List<Integer>` — and only there does the type really matter, because you use it in `Integer.toBinaryString()`.

</details>

---

## Step 12.3 — Stage 2: `ListView` with a custom adapter (`BaseAdapter`)

### Why

You need **two columns** in a row. `ArrayAdapter` only knows about one `TextView`. So you write the adapter yourself.

### How — the row layout

`res/layout/item_number.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- One row with two columns. Steps 2 and 3 both use this layout. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="14dp">

    <TextView
        android:id="@+id/tvDecimal"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:textAppearance="?attr/textAppearanceBodyLarge" />

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

Two `TextView`s with `0dp` + `layout_weight="1"` → each takes half the width.

> **Notice the comment in the XML:** “Steps 2 and 3 both use this layout.” The same file serves both adapters. This proves that the difference between `ListView` and `RecyclerView` **isn't in the layout**, but in the adapter.

### How — the adapter

`adapters/NumberListAdapter.java`:

```java
public class NumberListAdapter extends BaseAdapter {

    private static class ViewHolder {
        TextView tvDecimal;
        TextView tvBinary;
    }

    private final List<Integer> numbers;
    private final LayoutInflater layoutInflater;

    public NumberListAdapter(Context context, List<Integer> numbers) {
        this.layoutInflater = LayoutInflater.from(context);
        this.numbers = numbers;
    }

    @Override
    public int getCount() {
        return numbers.size();
    }

    @Override
    public Integer getItem(int position) {
        return numbers.get(position);
    }

    @Override
    public long getItemId(int position) {
        // Each number is unique, so the number itself can be the ID
        return numbers.get(position);
    }

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
}
```

### The four `BaseAdapter` methods

| Method | Question it answers | Who calls it |
|---|---|---|
| `getCount()` | how many rows are there? | `ListView` |
| `getItem(position)` | which object is at position i? | `ListView` (on click) |
| `getItemId(position)` | what stable ID does it have? | `ListView` (`OnItemClickListener` receives `id`) |
| `getView(...)` | what does row i look like? | `ListView`, for every visible row |

### The `convertView` + `ViewHolder` mechanism — the essence

This is the whole performance secret. `ListView` **doesn't create 100 rows** for 100 elements. It creates ~10 (as many as fit on screen) and **reuses** them while scrolling.

That's why `getView` receives `convertView`:

```
convertView == null   →  NEW row: inflate it from XML, find the views, save them in ViewHolder
convertView != null   →  REUSED row: get the saved ViewHolder; don't search for anything
```

`convertView.setTag(holder)` attaches the `ViewHolder` to the row. When the row is reused, `convertView.getTag()` retrieves it.

**Without `ViewHolder`:** on every scroll, `findViewById` would search through the tree twice per row. With 100 rows and lots of scrolling, it would be noticeably slow.

**With `ViewHolder`:** the search happens just once per created row.

### Why `getItemId` returns the number itself

```java
return numbers.get(position);
```

Because the numbers are unique. In a list with duplicates (e.g., movies with the same title), you'd need a separate `id`.

> **Remember:** `getItemId` is used by `ListView` only if you call `setHasStableIds(true)`. By default, it's ignored. But it's a good idea to implement it correctly.

### Exercise 12.3

**Requirement:** what happens if you forget `convertView.setTag(holder)`?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you removed the line that attaches the `ViewHolder` to the row.

**What happens:** when scrolling, `convertView != null`, so the `else` branch is entered:

```java
holder = (ViewHolder) convertView.getTag();   // getTag() returns null
```

Then `holder.tvDecimal.setText(...)` → **`NullPointerException`**. The list crashes the first time a row is reused, that is, as soon as you scroll.

**Why:** `setTag` and `getTag` are a pair. Without the first, the second returns `null`.

**Remember:**
1. `View.setTag(Object)` / `getTag()` is a free field on any `View` — you use it to attach data.
2. If you forget `setTag`, you get no compile-time error. It only shows up when scrolling.
3. The modern alternative is `RecyclerView.ViewHolder`, which does this automatically (see Stage 3).

**Where it comes back:** in Stage 3, `RecyclerView` **requires** a `ViewHolder` — you can't forget `setTag` because you no longer write it yourself.

</details>

---

## Step 12.4 — Stage 3: `RecyclerView`

### Why

`RecyclerView` does the same thing as Stage 2, but:

- **`ViewHolder` is required** — not optional, as with `ListView`;
- **`getView` is split into two methods** — creation and binding;
- **`LayoutManager` is separate** — you can switch between vertical/grid/horizontal without touching the adapter;
- **free animations** when inserting/deleting.

### How — the activity

`RecyclerViewActivity`:

```java
RecyclerView rvNumbers = findViewById(R.id.rvNumbers);
LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

### How — the layout

`activity_recycler_view.xml`:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <include layout="@layout/layout_number_header" />

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

`layout_height="0dp"` + `layout_weight="1"` → the `RecyclerView` takes all the space left after the header.

> **Caution:** a `RecyclerView` with `wrap_content` inside a vertical `LinearLayout` works, but you lose efficient recycling (it measures all the content). `0dp` + `weight` or `match_parent` is the correct approach.

### How — the adapter

`adapters/NumberRecyclerAdapter.java`:

```java
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

    @NonNull
    @Override
    public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Runs only when a new row is needed
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_number, parent, false);
        return new NumberViewHolder(view);
    }

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
}
```

### Exact correspondence with Stage 2

| `BaseAdapter` (ListView) | `RecyclerView.Adapter` | When it runs |
|---|---|---|
| `getCount()` | `getItemCount()` | when needed |
| `getView(...)` **first part**: `if (convertView == null) { inflate; findViewById; setTag }` | `onCreateViewHolder(...)` | **once** per created row |
| `getView(...)` **second part**: `setText(...)` | `onBindViewHolder(...)` | on **every** display of the row |
| `ViewHolder` + manual `setTag`/`getTag` | `RecyclerView.ViewHolder` — automatic | — |

The professor's comments in the code say exactly this:

```
// Runs only when a new row is needed      → onCreateViewHolder
// Runs each time a row shows a number     → onBindViewHolder
```

> **Remember:** `RecyclerView` doesn't have `getView` because it **split** the two responsibilities that were mixed together in `ListView` in a single method with `if (convertView == null)`.

### Why `ViewHolder` is `static`

```java
static class NumberViewHolder extends RecyclerView.ViewHolder {
```

If it weren't static, each `ViewHolder` would hold an implicit reference to the `NumberRecyclerAdapter` instance. With ~10 visible rows, you'd have ~10 unnecessary references. `static` eliminates them.

> **The same rule** applies to `MovieAdapter` in G1097 (chapter 11).

### Why `@NonNull`

```java
@NonNull
@Override
public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType)
```

These are contract annotations. `RecyclerView` guarantees that it won't pass `null` as `parent`, and you guarantee that you won't return `null`. Lint checks this.

### Exercise 12.4

**Requirement:** replace `LinearLayoutManager` with `GridLayoutManager(this, 2)`. Run it. What changes? Do you need to modify the adapter?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you changed only the `LayoutManager`:

```java
rvNumbers.setLayoutManager(new GridLayoutManager(this, 2));
```

**What you see:** the rows are arranged in **two columns**, like a grid. Each cell is still `item_number.xml` (which already has two columns inside it).

**Does the adapter need to be modified?** **No.** Not a single line.

**Why:** `RecyclerView` separates **what you display** (adapter) from **how you arrange it** (LayoutManager). With `ListView`, the arrangement was fixed — always vertical.

**Remember:**
1. `LinearLayoutManager(context)` — vertical (default).
2. `LinearLayoutManager(context, RecyclerView.HORIZONTAL, false)` — horizontal.
3. `GridLayoutManager(context, spanCount)` — grid with N columns.
4. `StaggeredGridLayoutManager(spanCount, orientation)` — grid with different heights.
5. Without `setLayoutManager`, `RecyclerView` **displays nothing** — and doesn't give an error.

**Where it comes back:** in G1097 (chapter 11), `MainActivity` uses `LinearLayoutManager(this)`. If you wanted a horizontal list of posters, you'd change one line.

</details>

---

## Step 12.5 — The final comparison, using the same data

### Why

Three screens, the same numbers 1–100, the same `item_number.xml` in stages 2 and 3. Only the adapter differs.

### The table to know for the test

| | Stage 1 | Stage 2 | Stage 3 |
|---|---|---|---|
| Widget | `ListView` | `ListView` | `RecyclerView` |
| Adapter | `ArrayAdapter` | custom `BaseAdapter` | `RecyclerView.Adapter` |
| Row layout | `simple_list_item_1` (system) | `item_number.xml` | `item_number.xml` |
| Columns per row | 1 | 2 | 2 |
| `ViewHolder` | implicit, hidden | **manual** (`setTag`/`getTag`) | **required**, automatic |
| Binding method | `getView()` | `getView()` | `onBindViewHolder()` |
| Creation method | — | in `getView`, `if (convertView == null)` | `onCreateViewHolder()` |
| Arrangement | fixed vertical | fixed vertical | `LayoutManager` — configurable |
| Animations | no | no | yes |

### What to answer on the test

**“What's the difference between ListView and RecyclerView?”**
`RecyclerView` requires a `ViewHolder`, separates creation from binding (`onCreateViewHolder` / `onBindViewHolder`), delegates arrangement to a `LayoutManager`, and provides animations. `ListView` has a single `getView()` with `if (convertView == null)` and a fixed arrangement.

**“Why isn't ArrayAdapter enough?”**
Because it knows about only one `TextView` per row. For two columns, you need a custom layout and an adapter that fills it.

**“What does convertView do?”**
It reuses rows that move off screen. Without it, 100 rows would be inflated for 100 elements.

---

## Step 12.6 — Verify

### How

1. Open `DMA06` in Android Studio.
2. Run it. From the menu, press the three buttons one by one.
3. Stage 1: list with one number per row.
4. Stage 2: list with two columns (decimal | binary).
5. Stage 3: the same two columns, but with `RecyclerView`.
6. Scroll quickly through all three. Stage 3 should be the smoothest.

### What to check in the code

- [ ] `NumberData` has no `android.*` imports
- [ ] `item_number.xml` is used by **both** adapters
- [ ] `NumberListAdapter extends BaseAdapter` with 4 methods
- [ ] `NumberListAdapter` has `ViewHolder` + `setTag`/`getTag`
- [ ] `NumberRecyclerAdapter extends RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder>`
- [ ] `NumberViewHolder` is `static`
- [ ] `RecyclerViewActivity` calls `setLayoutManager` **before** `setAdapter`

---

## Step 12.7 — Synthesis exercise

**Requirement:** write the complete `NumberRecyclerAdapter` from memory, without looking. What three methods are required?

<details>
<summary>Answer — explanatory</summary>

**Three required methods:**
1. `onCreateViewHolder(parent, viewType)` → `@NonNull NumberViewHolder`
2. `onBindViewHolder(holder, position)` → `void`
3. `getItemCount()` → `int`

Plus the inner `ViewHolder` class, `static`, which extends `RecyclerView.ViewHolder`.

**Why exactly three:** `RecyclerView.Adapter` declares them `abstract`. If you don't implement them, the class won't compile.

**What's optional:** `getItemViewType`, `getItemId`, `onViewRecycled`, `onAttachedToRecyclerView` — they all have default implementations.

**Remember:**
1. **Three methods**, not four as with `BaseAdapter` (`getCount`, `getItem`, `getItemId`, `getView`).
2. `getItemCount()` replaces `getCount()`.
3. There's no `getItem(position)` — you write it yourself if you need it, as a custom method.

**Where it comes back:** in chapter 11, `MovieAdapter` has exactly the same three methods, except it works with `Movie` instead of `Integer`.

</details>

---

## Chapter 12 summary

- `DMA06` = three stages using the same data: `ArrayAdapter` → `BaseAdapter` → `RecyclerView.Adapter`.
- `item_number.xml` is shared by stages 2 and 3 — only the adapter differs.
- `convertView` + `ViewHolder` + `setTag`/`getTag` = recycling in `ListView`.
- `onCreateViewHolder` / `onBindViewHolder` = `getView` split in two in `RecyclerView`.
- `LayoutManager` separates arrangement from content.
- Without `setLayoutManager`, `RecyclerView` is empty — with no error.

**Next chapter:** [13 - DMA05 - ViewBinding.md](13%20-%20DMA05%20-%20ViewBinding.md)
