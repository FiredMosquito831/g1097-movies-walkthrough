# Chapter 13 — DMA05: ViewBinding and the input widgets

**Objective:** to understand `ViewBinding` — the modern alternative to `findViewById` — and to go through all the input widgets that the `G1097` app also uses, but here isolated, each with a `Toast`.

**Estimated time:** 40–55 min.

**Source:** `DMA05/` at commit `d719ffc` — 29 files.

> **Why it matters:** the `G1097` project has `buildFeatures { viewBinding = true }` in `build.gradle.kts`, but the code uses `findViewById`. So the feature is enabled and **unused** (see chapter 01, step 1.3). DMA05 shows what the code would look like if you used it.

---

## Step 13.1 — What `ViewBinding` is

### Why

`findViewById(R.id.etTitle)` has three problems:

1. **It's not type-safe.** If you write `TextView tv = findViewById(R.id.etTitle);` where `etTitle` is an `EditText`, the compiler won't catch you. Only at runtime do you get a `ClassCastException`.
2. **It returns `null`** if the ID doesn't exist in the current layout. Again, you only find out at runtime.
3. **Repetition.** 13 lines of `findViewById` in `ItemActivity`, each with the ID written by hand.

`ViewBinding` solves all three: it generates a Java class per layout, with a field for every view that has an `android:id`.

### How to enable it

In `app/build.gradle.kts` (or the module's `build.gradle.kts`, after restructuring):

```kotlin
android {
    // ...
    buildFeatures { viewBinding = true }
}
```

Then **Sync Project with Gradle Files**.

### What it generates

For `res/layout/activity_main.xml` → class `ActivityMainBinding`:

```
app/build/generated/data_binding_base_class_source_out/.../databinding/ActivityMainBinding.java
```

Naming rule: `snake_case` becomes `PascalCase` + the `Binding` suffix.

| Layout file | Generated class |
|---|---|
| `activity_main.xml` | `ActivityMainBinding` |
| `activity_item.xml` | `ActivityItemBinding` |
| `movie_item.xml` | `MovieItemBinding` |
| `item_number.xml` | `ItemNumberBinding` |

> **Remember:** the class is generated **at build time**. If you haven't built after adding an `android:id`, you won't find it. **Build → Make Project**.

### What the generated class contains

For every view with an `android:id` in the layout, a **public final field** with the exact type:

```java
public final Button button;
public final Switch switch1;
public final CheckBox checkBox;
public final SeekBar seekBar;
public final RadioGroup radioGroup;
public final ToggleButton toggleButton;
public final RatingBar ratingBar;
// ...
public LinearLayout getRoot() { ... }
```

The type is inferred from the XML tag. `<Button>` → `Button`. You can no longer get the type wrong.

### Exercise 13.1

**Requirement:** what happens if a view does **not** have an `android:id` in XML? Does it appear in the generated class?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you checked which views end up in `ActivityMainBinding`.

**Answer:** **no.** `ViewBinding` generates fields only for views with an `android:id`. The ones without an ID can't be referenced from code — and you don't need them to be, because you never touch them.

**Why:** the binding needs to know what name to give the field. Without an ID, there's no name.

**Remember:**
1. `<include>` **without** an ID → its content is reachable through `binding.<numeInclude>`, but the include itself must have an ID for you to get a field.
2. `merge` and `ViewStub` have special rules — not covered here.
3. IDs from the XML become **exact** field names (`switch1` → `binding.switch1`).

**Where it comes back:** in `G1097`, `activity_item.xml` has 20 IDs, but the code uses 13. With `ViewBinding` you'd have fields for all 20 — and nobody would complain.

</details>

---

## Step 13.2 — `inflate` and `getRoot`

### Why

`ViewBinding` does not replace `setContentView(int)`. You have to **build** the binding, then hand its root to `setContentView`.

### How

`DMA05/MainActivity`:

```java
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
        // ...
    }
}
```

### The three steps

| Line | What it does |
|---|---|
| `ActivityMainBinding.inflate(getLayoutInflater())` | reads the XML and builds the view tree |
| `setContentView(binding.getRoot())` | puts the tree on screen |
| `binding.button`, `binding.seekBar` … | direct, type-safe access |

### Correspondence with the classic variant

`G1097/MainActivity` (chapter 04):

```java
setContentView(R.layout.activity_main);
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...);
fabInsert = findViewById(R.id.floatingActionButton);
listView = findViewById(R.id.listView);
```

`DMA05/MainActivity`:

```java
binding = ActivityMainBinding.inflate(getLayoutInflater());
setContentView(binding.getRoot());
ViewCompat.setOnApplyWindowInsetsListener(binding.getRoot(), ...);
// binding.button, binding.seekBar — done, no findViewById
```

The same three operations, but `findViewById` has disappeared completely.

### Why `getRoot()` and not `binding.main`

`binding.getRoot()` returns the **root** of the layout, regardless of its type. You could also write `binding.main` if the root has `android:id="@+id/main"` — and in DMA05 it does. But `getRoot()` is the convention: it works even if the root has no ID.

### Exercise 13.2

**Requirement:** replace `binding.getRoot()` with `binding.main` in `DMA05`. Does it compile? Does it run?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you changed the argument to `setContentView`.

**Does it compile?** **Yes** — `binding.main` is a generated field (the root has `android:id="@+id/main"`), of type `LinearLayout`.

**Does it run?** **Yes** — it looks identical.

**Why both work:** `getRoot()` returns the exact same object as `binding.main`; only the declared type differs — `View` instead of `LinearLayout`.

**Remember:**
1. `getRoot()` always exists. `binding.<id>` exists only if the root has an ID.
2. The type matters if you want to call type-specific methods (`LinearLayout.setOrientation`). For `setContentView`, it doesn't.
3. The repo convention is `getRoot()` — keep it.

**Where it comes back:** in `G1097`, `activity_main.xml` has `android:id="@+id/main"` **for insets**, not for binding. If you migrated to `ViewBinding`, you could use `binding.main` — but `getRoot()` is still recommended.

</details>

---

## Step 13.3 — The widgets and their listeners

### Why

`DMA05` puts all the input widgets on a single screen, each with a `Toast` confirming that its listener fired. It's a "widget laboratory".

### How — the inventory

From `activity_main.xml`:

| Widget | `android:id` | Listener | What it binds to |
|---|---|---|---|
| `Button` | `button` | `setOnClickListener` | click |
| `ImageView` | `imageView` | — | display only |
| `Switch` | `switch1` | `setOnCheckedChangeListener` | sliding toggle |
| `EditText` | `editTextText` | — | free text |
| `EditText` | `editTextTextPassword` | — | password |
| `EditText` | `editTextTextEmailAddress` | — | email |
| `EditText` | `editTextTime` | — | time |
| `EditText` | `editTextDate` | — | date |
| `CheckBox` | `checkBox` | `setOnCheckedChangeListener` | square checkbox |
| `RadioGroup` | `radioGroup` | `setOnCheckedChangeListener` | single choice |
| `ToggleButton` | `toggleButton` | `setOnCheckedChangeListener` | on/off |
| `RatingBar` | `ratingBar` | `setOnRatingBarChangeListener` | stars |
| `SeekBar` | `seekBar` | `setOnSeekBarChangeListener` | slider bar |

### How — the code

```java
binding.button.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show();
    }
});

binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
    Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
});

binding.checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
    Toast.makeText(MainActivity.this, "CheckBox clicked to " + isChecked, Toast.LENGTH_SHORT).show();
});

binding.seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        Toast.makeText(MainActivity.this, "Progress changed to " + progress, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {
    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {
    }
});

binding.radioGroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull RadioGroup group, int checkedId) {
        RadioButton selected = group.findViewById(checkedId);
        Toast.makeText(MainActivity.this, "Radio button clicked " + selected.getText(), Toast.LENGTH_SHORT).show();
    }
});

binding.toggleButton.setOnCheckedChangeListener((buttonView, isChecked) -> {
    Toast.makeText(MainActivity.this, "Toggle button clicked to " + isChecked, Toast.LENGTH_SHORT).show();
});

binding.ratingBar.setOnRatingBarChangeListener((ratingBar, rating, fromUser) -> {
    Toast.makeText(MainActivity.this, "Rating changed to " + rating, Toast.LENGTH_SHORT).show();
});
```

### Three listener families

| Interface | Methods | Lambda? | Widgets |
|---|---|---|---|
| `View.OnClickListener` | 1 (`onClick`) | **yes** | `Button`, `ImageView`, any `View` |
| `CompoundButton.OnCheckedChangeListener` | 1 (`onCheckedChanged`) | **yes** | `Switch`, `CheckBox`, `ToggleButton`, `RadioButton` |
| `SeekBar.OnSeekBarChangeListener` | **3** | **no** | `SeekBar` |
| `RadioGroup.OnCheckedChangeListener` | 1 (`onCheckedChanged`) | **yes** | `RadioGroup` |
| `RatingBar.OnRatingBarChangeListener` | 1 | **yes** | `RatingBar` |

> **Rule:** a single abstract method = lambda allowed. `SeekBar` has three, so an anonymous class is mandatory.

### `RadioGroup` — why `group.findViewById(checkedId)`

```java
RadioButton selected = group.findViewById(checkedId);
```

The `OnCheckedChangeListener` on `RadioGroup` receives the **ID** of the selected button (`checkedId`), not the object. To get the text, you look up the button by ID.

The alternative (used in `G1097`): you iterate over the children with `getChildCount()` / `getChildAt()` and look for `isChecked()`. Both work — the first is more direct when you have `checkedId`, the second is more portable when you want to extract the text.

### Exercise 13.3

**Requirement:** why does `binding.switch1` have a lambda listener, but `binding.seekBar` doesn't?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you compared the two calls.

**Answer:** `CompoundButton.OnCheckedChangeListener` has **one** method (`onCheckedChanged`), so it's a functional interface → lambda works. `SeekBar.OnSeekBarChangeListener` has **three** (`onProgressChanged`, `onStartTrackingTouch`, `onStopTrackingTouch`), so it's **not** functional → you need an anonymous class with all three implemented.

**Why `SeekBar` has three:** because there are three distinct moments — value change, touch start, touch end. `Switch` has a single moment: it changed.

**Remember:**
1. Lambda = **exactly one** abstract method.
2. If you forget one of the three methods, the class won't compile.
3. You can leave `onStartTrackingTouch` / `onStopTrackingTouch` empty — the body is mandatory, the behavior is not.

**Where it comes back:** in chapter 07, `ItemActivity` has exactly the same structure: `swWatched` with a lambda, `sbDuration` with an anonymous class.

</details>

---

## Step 13.4 — Why `G1097` doesn't use `ViewBinding`

### Why

You might think it's an oversight. It isn't — it's a deliberate teaching choice.

### The explanation

In `G1097/build.gradle.kts`:

```kotlin
buildFeatures { viewBinding = true }
```

The feature is **enabled**. But `MainActivity` and `ItemActivity` use `findViewById`.

**Why:** in the lab, `findViewById` shows explicitly the link between XML and code. With `ViewBinding`, part of the learning disappears — you no longer see that `R.id.etTitle` corresponds to an `android:id` in the XML.

> **Remember:** `viewBinding = true` without using it doesn't break anything. It generates some classes that stay unused. The runtime cost is zero.

### How you would migrate `ItemActivity` to `ViewBinding`

**Before:**

```java
setContentView(R.layout.activity_item);
etTitle = findViewById(R.id.etTitle);
etRelease = findViewById(R.id.etRelease);
// ... 13 lines
```

**After:**

```java
ActivityItemBinding binding = ActivityItemBinding.inflate(getLayoutInflater());
setContentView(binding.getRoot());
binding.etTitle.setText(...);
binding.etRelease.setText(...);
// no fields, no findViewById
```

The 13 fields `private EditText etTitle;` … disappear. They become `binding.etTitle` etc.

### Exercise 13.4

**Requirement:** what do you concretely gain and what do you lose when migrating `ItemActivity`?

<details>
<summary>Answer — explanatory</summary>

**What you gain:**
1. **Type safety** — `binding.etTitle` is a `TextInputEditText`, not an `EditText`. You can't get the type wrong.
2. **Less code** — 13 fields + 13 lines of `findViewById` disappear.
3. **Null safety** — the binding can't return `null` for an existing ID. `findViewById` can.
4. **Safe refactoring** — you rename the ID in XML, and the build fails if you don't update the code.

**What you lose:**
1. **The didactic explicitness** — you no longer see the `R.id.x` ↔ `android:id` link.
2. **The ease of reading the code in pieces** — `binding.` prefixes every access.
3. **Build time** — the generated classes get compiled (negligible).

**Remember:**
1. `ViewBinding` is **not** `DataBinding`. `DataBinding` allows expressions in XML (`@{...}`), `ViewBinding` only references.
2. `ViewBinding` doesn't mix well with `findViewById` on the same layout without care — but technically you can have both.
3. The migration is done layout by layout, not the whole project at once.

**Where it comes back:** in chapter 11, `MovieAdapter` could use `MovieItemBinding` instead of `itemView.findViewById(...)`. It would be cleaner, but the repo doesn't do it.

</details>

---

## Step 13.5 — `EditText` and `inputType`

### Why

`DMA05` has five `EditText`s, each with a different `inputType`. It's the clearest demonstration of the difference.

### How

| ID | `inputType` | Keyboard | Restriction |
|---|---|---|---|
| `editTextText` | `text` | normal text | accepts anything |
| `editTextTextPassword` | `textPassword` | text | masked with dots |
| `editTextTextEmailAddress` | `textEmailAddress` | with `@` and `.` | email suggestions |
| `editTextTime` | `time` | digits and `:` | time format |
| `editTextDate` | `date` | digits and `/` | date format |

### What matters for the test

`inputType` does **two** things at once:
1. picks the **keyboard** shown;
2. **restricts** the accepted characters.

`textPassword` masks the text. `numberDecimal` rejects letters. `textEmailAddress` rejects nothing, it only optimizes the keyboard.

> **Remember:** `inputType` does not validate. You can type an invalid email — `textEmailAddress` just puts `@` at your fingertips.

### Exercise 13.5

**Requirement:** in `DMA05`, change `editTextText` to `inputType="numberDecimal"`. Type "abc". What happens?

<details>
<summary>Answer — explanatory</summary>

**What was done:** you changed the field's type.

**What you see:** the keyboard becomes numeric. You type "a", "b", "c" — **they don't appear**.

**Why:** `numberDecimal` tells the `EditText` to accept only digits, dot and minus. Invalid keys are ignored at the `InputFilter` level, not at validation.

**Remember:**
1. `numberDecimal` **rejects** letters. `textEmailAddress` **rejects** nothing.
2. The restriction comes from `DigitsKeyListener`, set automatically by `inputType`.
3. If you need a custom restriction, you add `setFilters(new InputFilter[]{...})`.

**Where it comes back:** in `G1097`, `etBudget` has `numberDecimal`, `etPoster` has `textUri`, `etRelease` has `date`. Same mechanism, from chapter 05.

</details>

---

## Step 13.6 — Verification

### How

1. Open `DMA05` in Android Studio.
2. Run it.
3. Press each widget. A `Toast` with what happened should appear.
4. Check in `Build → Generated` that `ActivityMainBinding.java` exists.

### What to check in the code

- [ ] `build.gradle.kts` has `buildFeatures { viewBinding = true }`
- [ ] `ActivityMainBinding binding;` is a field, not a local variable
- [ ] `binding = ActivityMainBinding.inflate(getLayoutInflater())` in `onCreate`
- [ ] `setContentView(binding.getRoot())`
- [ ] insets applied to `binding.getRoot()`, not to `findViewById(R.id.main)`
- [ ] zero `findViewById` for the views in the layout
- [ ] `SeekBar` has an anonymous class, the others have lambdas

---

## Chapter 13 summary

- `ViewBinding` generates one class per layout, with a field per view that has an `android:id`.
- `inflate(getLayoutInflater())` → `setContentView(binding.getRoot())`.
- Type-safe, null-safe, less code than `findViewById`.
- `G1097` has the feature enabled but **unused** — a teaching choice.
- Three listener families: one method → lambda; three methods (`SeekBar`) → anonymous class.
- `inputType` picks the keyboard **and** restricts the characters.

**Next chapter:** [14 - DMA03 - Navigare si meniuri.md](14%20-%20DMA03%20-%20Navigare%20si%20meniuri.md)
