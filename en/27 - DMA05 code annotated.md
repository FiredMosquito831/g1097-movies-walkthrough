# Chapter 27 — The DMA05 Code, Annotated

**Objective:** to read DMA05 like a widgets lab — every view in the XML, every listener in the code and every line of `ViewBinding`, with the explanation right next to them.

**Estimated time:** 45–60 min (active reading).

**Source:** `DMA05/` at commit `d719ffc` — 29 files, of which 3 matter for the chapter: `MainActivity.java`, `activity_main.xml`, `AndroidManifest.xml`.

**What you learn from it:** `ViewBinding` (`ActivityMainBinding`), all the input widgets and their listeners.

> **How to read it:** DMA05 has no business logic. It only has UI. So everything you need to understand is the link between XML and code: which tag produces which field in `binding`, which registration method takes which interface, and why some have a lambda while others have an anonymous class.

---

## 27.1 `MainActivity.java` — ViewBinding, line by line

The file has 88 lines and does one thing: it builds the screen, puts it on the display and wires seven listeners. We'll take it in blocks.

### The complete file, annotated

#### Block 1 — the package and the imports

```java
package ro.ase.ie.dma05;                              // the module's namespace (build.gradle.kts)

import android.os.Bundle;                             // the parameter of onCreate
import android.view.View;                             // the parameter of onClick(View v)
import android.widget.RadioButton;                    // the type of the selected button
import android.widget.RadioGroup;                     // the type of the parameter in OnCheckedChangeListener
import android.widget.SeekBar;                        // the interface with 3 methods
import android.widget.Toast;                          // the feedback of every listener

import androidx.activity.EdgeToEdge;                  // drawing under the system bars
import androidx.annotation.NonNull;                   // the annotation in onCheckedChanged
import androidx.appcompat.app.AppCompatActivity;      // the base class
import androidx.core.graphics.Insets;                 // the 4 padding values
import androidx.core.view.ViewCompat;                 // the insets listener
import androidx.core.view.WindowInsetsCompat;         // Type.systemBars()

import ro.ase.ie.dma05.databinding.ActivityMainBinding;   // ← the GENERATED class
```

**`import ro.ase.ie.dma05.databinding.ActivityMainBinding` is the only import with no file in the source.** The `databinding` package does not exist in `src/` — Gradle fabricates it at build time, from `activity_main.xml`. If Android Studio underlines the line in red, you didn't do **Build → Make Project** after adding the last `android:id`.

**Why `Button`, `Switch`, `CheckBox`, `ToggleButton`, `RatingBar`, `EditText`, `ImageView` are missing:** the names of these types never appear in the file. You access them only as `binding.button`, `binding.switch1` etc. — the compiler knows the type from the generated field, you no longer write it. `ViewBinding` removes the imports too, not just `findViewById`.

**Why `View` is imported even though you never instantiate it:** it's the type of the parameter in `onClick(View v)` and of the `v` parameter in the insets lambda.

#### Block 2 — the class and the field

```java
public class MainActivity extends AppCompatActivity {

    ActivityMainBinding binding;                      // a field, not a local variable
```

**Why `ActivityMainBinding`:** the name comes from the name of the layout file. The rule is mechanical: `activity_main.xml` → `ActivityMainBinding`, `activity_item.xml` → `ActivityItemBinding`. You can't get it wrong and it isn't configured anywhere — `buildFeatures { viewBinding = true }` in `build.gradle.kts` is all you need.

**Why a field and not a local variable:** in DMA05 a local would work too, because everything happens in `onCreate`. But the pattern is a field because in any real application the binding is also touched from `onSaveInstanceState`, from helper methods and from listeners. `ActivityMainBinding binding;` without `private` is package-private — it works, but `private` would be the correct style.

**What happens before `inflate`:** the field is `null`. It isn't "empty", it's a null reference. Any `binding.button` before the next line throws `NullPointerException`.

#### Block 3 — `inflate`

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);           // 1. the parent's lifecycle

        binding = ActivityMainBinding.inflate(getLayoutInflater());   // 2. XML → Java objects
```

**What `inflate(getLayoutInflater())` does, step by step:**

1. `getLayoutInflater()` returns the activity's `LayoutInflater`, already bound to its `Context` and its theme. That's why you don't write `LayoutInflater.from(this)` — it's the same object.
2. `inflate` reads `res/layout/activity_main.xml`, parses each tag and builds the objects: a `LinearLayout`, a `Button`, an `ImageView` and so on.
3. At the end, it walks the tree and **fills the public fields** of the generated class with the references it found, by `android:id`.
4. It returns the `ActivityMainBinding` object, which you keep in the field.

**This is the operation that `setContentView(R.layout.activity_main)` used to do internally.** The difference: the classic version threw the result away, and you looked it up again with `findViewById`. Now the result is kept.

**Why the single-argument variant:** there is also `inflate(inflater, parent, attachToRoot)`. In an `Activity` you don't need them — `setContentView` supplies the parent. The variant with `parent` is used in `Fragment`s and in adapters.

#### Block 4 — `EdgeToEdge`, `setContentView` and insets

```java
        EdgeToEdge.enable(this);                      // 3. the content is drawn under the system bars
        setContentView(binding.getRoot());            // 4. the built tree reaches the screen
        ViewCompat.setOnApplyWindowInsetsListener(binding.getRoot(), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
```

**`setContentView(binding.getRoot())` replaces `setContentView(R.layout.activity_main)`.** `getRoot()` returns the root `LinearLayout` — exactly the view that has `android:id="@+id/main"` in the XML. You don't put both:

> **Trap no. 1 in this file:** if you also leave `setContentView(R.layout.activity_main)` after the binding line, Android builds **a second tree**, completely separate. The second one reaches the screen; `binding` points to the first. The seven listeners attach to views nobody sees, and the app seems "dead" — no Toast ever appears. It happens often when migrating from `findViewById`.

**Why insets on `binding.getRoot()` and not on a child:** `setPadding` on the root moves **all** the descendants into the safe area. Applied to `binding.button`, only the button would be pushed; the rest would stay under the clock and under the navigation bar. And the listener must be registered on exactly the object that is the content view — padding on a view that isn't on screen isn't visible.

**Why `getRoot()` and not `binding.main`:** in DMA05 the root **does** have an ID, so `binding.main` exists and is the same object. But `getRoot()` also works when the root has no `android:id` — that's why it's the convention. `binding.main` is a generated field that the code never uses.

**What each line of the lambda does:**

| Line | Effect |
|---|---|
| `insets.getInsets(WindowInsetsCompat.Type.systemBars())` | extracts the 4 dimensions of the bars (status + navigation + caption) |
| `v.setPadding(left, top, right, bottom)` | applies them as padding on the root |
| `return insets` | lets the insets travel onward, to the children |

**`return insets`, not `WindowInsetsCompat.CONSUMED`:** if you returned `CONSUMED`, dispatch would stop at the root and no child would receive the insets anymore. It doesn't matter here, but it's the general rule.

**The lambda is allowed here** because `OnApplyWindowInsetsListener` has a single method: `onApplyWindowInsets(View, WindowInsetsCompat)`.

> **Trap no. 2:** `setPadding` **overwrites** the padding from the XML, it doesn't add to it. The root in DMA05 has no `android:padding`, so nothing is lost. If it had `16dp`, the correct thing would be `v.setPadding(16dp + left, 16dp + top, ...)`.

**What `Type.systemBars()` doesn't cover:** the keyboard. When an `EditText` opens, the IME is not compensated — you'd need `WindowInsetsCompat.Type.ime()` in a second listener or in the same one. In DMA05 the fields are at the top, so the problem doesn't show.

#### Block 5 — `Button`, anonymous class

```java
        binding.button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show();
            }
        });
```

**`binding.button` is of type `Button`** — the type is inferred from the `<Button>` tag in the XML. The `setOnClickListener` method is declared on `View`, so every widget has it, not just buttons.

**Why an anonymous class here, when the interface has a single method:** `View.OnClickListener` **is** a functional interface, so a lambda would work. The repo alternates styles on purpose so you see both. The lambda equivalent of the whole block:

```java
// The same functionality, lambda style — does NOT exist in the real file.
binding.button.setOnClickListener(v ->
        Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show());
```

**Why `MainActivity.this` and not `this`:** inside the anonymous class, `this` is the listener object, not the activity. And `Toast.makeText` needs a `Context`. `MainActivity.this` is the syntax that takes you out of the anonymous class and reaches the enclosing instance.

> **The difference that matters at the exam:** in a **lambda**, `this` refers to the instance surrounding the lambda — that is, `MainActivity`. In an **anonymous class**, `this` is the anonymous class. That's why the lambda doesn't need `MainActivity.this`, and the anonymous class does.

**`Toast.LENGTH_SHORT`** ≈ 2 seconds; `LENGTH_LONG` ≈ 3.5 seconds. **`.show()`** is mandatory: without it you build the `Toast` object and throw it away — nothing appears on screen.

#### Block 6 — `Switch` and `CheckBox`, lambda

```java
        binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        binding.checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "CheckBox clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });
```

**The same interface for two different widgets.** `Switch` and `CheckBox` both extend `CompoundButton`, which declares `setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener)`. That's why the lambda signature is identical: `(CompoundButton buttonView, boolean isChecked)`.

**`buttonView` is the widget that fired** — useful when the same lambda is shared between several controls. Here it's ignored. **`isChecked` is the new state**, not the old one.

**Why a lambda:** `OnCheckedChangeListener` has exactly one method, `onCheckedChanged(CompoundButton, boolean)` → functional interface.

**`"Switch clicked to " + isChecked`** — the concatenation calls `String.valueOf(boolean)`, so the text is `...true` or `...false`. You don't need an `if`.

**The listener also fires on changes made from code**, not only on touch: a `setChecked(true)` would produce a Toast too. It doesn't happen here, but it's good to know.

#### Block 7 — `SeekBar`, anonymous class required

```java
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
```

**Why a lambda doesn't work here:** `SeekBar.OnSeekBarChangeListener` has **three** abstract methods. A functional interface has exactly one. With three, you're forced into an anonymous class that implements all of them.

**The three moments, and why there are three:**

| Method | When it appears | Useful parameters |
|---|---|---|
| `onProgressChanged` | on every value change | `progress` = the new value, `fromUser` = does it come from the finger? |
| `onStartTrackingTouch` | when the finger touches the bar | — |
| `onStopTrackingTouch` | when the finger lifts | — |

**`fromUser`** is `true` when the change comes from the user and `false` when it comes from `setProgress(...)`. Here it's ignored — the Toast appears in both cases.

**Empty bodies are legal and mandatory.** You must implement all three methods; if you have nothing to do in one, you leave it empty. If you forget one, the file doesn't compile.

**`progress` goes from 0 to `android:max`.** There is no `android:max` in the XML, so the default value is **100**.

> **The didactic flaw of this block:** a Toast for every step means dozens of Toasts on a single drag, queued up. In `ItemActivity` (G1097) the same listener writes into a `TextView` — the correct behaviour.

#### Block 8 — `RadioGroup`

```java
        binding.radioGroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull RadioGroup group, int checkedId) {
                RadioButton selected = group.findViewById(checkedId);
                Toast.makeText(MainActivity.this, "Radio button clicked " + selected.getText(), Toast.LENGTH_SHORT).show();
            }
        });
```

**`checkedId` is a resource ID, not an index and not the object.** The value is `R.id.radioButton1` or `R.id.radioButton2`. The "it's the position" confusion is common and leads to `findViewById(0)`.

**Why `group.findViewById(checkedId)` and not `findViewById(checkedId)`:** the search is done in the group's subtree. Here the activity-wide variant would work too, because the IDs are unique in the layout — but the form with `group` is the conceptually correct one.

**This is the only `findViewById` that survives with `ViewBinding`.** The binding gives you `binding.radioButton1` and `binding.radioButton2`, but it has no way to turn an `int` received at runtime into a field. You have two alternatives:

```java
// the variant from the file
RadioButton selected = group.findViewById(checkedId);

// the variant with compared IDs — equivalent, does not exist in the file.
// Use ONE of them, not both: they declare the same variable.
RadioButton selected = checkedId == R.id.radioButton1
        ? binding.radioButton1
        : binding.radioButton2;
```

**Why `RadioGroup.OnCheckedChangeListener` has a single method, yet still uses an anonymous class:** again, alternating style. A lambda would be perfectly valid.

**`@NonNull` on the parameter** comes from `androidx.annotation`. It doesn't change runtime behaviour — it's a contract for lint and for the reader: "the group is never null". The annotation on an override is optional; Android Studio adds it automatically when it generates the method.

> **Trap no. 3:** if `checkedId` were `-1` (it happens after `clearCheck()`), `findViewById(-1)` returns `null` and `selected.getText()` throws `NullPointerException`. In DMA05 `clearCheck()` is never called, so it doesn't happen. In `G1097`, the first button has `android:checked="true"` precisely so that "nothing selected" never exists.

#### Block 9 — `ToggleButton`, `RatingBar` and closing the class

```java
        binding.toggleButton.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "Toggle button clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        binding.ratingBar.setOnRatingBarChangeListener((ratingBar, rating, fromUser) -> {
            Toast.makeText(MainActivity.this, "Rating changed to " + rating, Toast.LENGTH_SHORT).show();
        });


    }
}
```

**`ToggleButton` is the third widget with the same interface.** `CompoundButton` now has three consumers in the same file: `Switch`, `CheckBox`, `ToggleButton`. That's the lesson of the block: it isn't the widget type that decides the listener, it's the **base class**.

**`RatingBar.OnRatingBarChangeListener`** has one method, `onRatingChanged(RatingBar, float, boolean)` → lambda. `rating` is `float` because of `stepSize="0.5"` — the values are 0.0, 0.5, 1.0, … `fromUser` has the same meaning as in `SeekBar`.

**`"Rating changed to " + rating`** displays `3.0`, not `3` — concatenating a `float` keeps the decimal.

**The two blank lines before the braces** are in the real file. They break nothing; they signal that the block was written incrementally, listener by listener.

### What has no listener — and why

Seven widgets have a listener. The rest don't:

| View | Why not | What you'd use if you wanted to |
|---|---|---|
| `imageView` | display only | `setOnClickListener` (every `View` has it) |
| the 5 `EditText`s | read when needed, not on typing | `addTextChangedListener(new TextWatcher(){...})` — **3 methods**, so an anonymous class |
| `progressBar` | it's demonstrative, stays at 0 | `setProgress(int)` from code |
| `radioButton1/2` | the group covers them | a listener on each button, rarely useful |

**`TextWatcher` is the other example of a three-method interface** that you meet often, next to `SeekBar.OnSeekBarChangeListener`. If the test asks you to "react when the user types", the answer is `TextWatcher` with `beforeTextChanged`, `onTextChanged`, `afterTextChanged`.

### The seven listeners, in a table

| # | Line | Widget | Registration method | Interface | Methods | Style |
|---|---|---|---|---|---|---|
| 1 | 38 | `button` | `setOnClickListener` | `View.OnClickListener` | 1 | anonymous class |
| 2 | 45 | `switch1` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 3 | 49 | `checkBox` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 4 | 53 | `seekBar` | `setOnSeekBarChangeListener` | `SeekBar.OnSeekBarChangeListener` | **3** | anonymous class |
| 5 | 70 | `radioGroup` | `setOnCheckedChangeListener` | `RadioGroup.OnCheckedChangeListener` | 1 | anonymous class |
| 6 | 78 | `toggleButton` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 7 | 82 | `ratingBar` | `setOnRatingBarChangeListener` | `RatingBar.OnRatingBarChangeListener` | 1 | lambda |

**The rule, in one sentence:** one abstract method → lambda allowed; two or more → anonymous class required. The repo's style alternates deliberately, so you see both forms on the same interface (`button` is an anonymous class, although it could have been a lambda).

---

## 27.2 `activity_main.xml` — the widget inventory

### The complete table

| `android:id` | Widget | `inputType` / key attribute | Listener | Notes |
|---|---|---|---|---|
| `main` | `LinearLayout` (root) | `orientation="vertical"` | insets (not a widget listener) | the ID is **not** used by the code |
| `button` | `Button` | — | `setOnClickListener` — anonymous class | the only `onClick` in the file |
| `imageView` | `ImageView` | `app:srcCompat` | — | display only |
| `switch1` | `Switch` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `editTextText` | `EditText` | `text` | — | free text |
| `editTextTextPassword` | `EditText` | `textPassword` | — | masked with dots |
| `editTextTextEmailAddress` | `EditText` | `textEmailAddress` | — | keyboard with `@` |
| `editTextTime` | `EditText` | `time` | — | numeric keyboard |
| `editTextDate` | `EditText` | `date` | — | numeric keyboard |
| `checkBox` | `CheckBox` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `radioGroup` | `RadioGroup` | `orientation` defaults to vertical | `setOnCheckedChangeListener` — anonymous class | receives `checkedId` |
| `radioButton1` | `RadioButton` | — | via the group | "First Option" |
| `radioButton2` | `RadioButton` | — | via the group | "Second Option" |
| `toggleButton` | `ToggleButton` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `progressBar` | `ProgressBar` | `style=?android:attr/progressBarStyleHorizontal` | — | stays at 0 |
| `seekBar` | `SeekBar` | `max` defaults to **100** | `setOnSeekBarChangeListener` — anonymous class | 3 methods |
| `ratingBar` | `RatingBar` | `numStars="5"`, `stepSize="0.5"` | `setOnRatingBarChangeListener` — lambda | `float` value |

**17 IDs, 7 used in the code.** The other 10 produce fields in `ActivityMainBinding` that nobody touches — and that's perfectly normal: the binding generates them all, whether you use them or not.

### The file, annotated in blocks

#### Block 1 — the root

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity" >
```

**Vertical `LinearLayout`** — the children are stacked from top to bottom, one under another. There is no `ScrollView`: on a small screen, the last widgets (`SeekBar`, `RatingBar`) can go outside the visible area. `G1097` wraps the form in a `ScrollView` for exactly this reason.

**`android:id="@+id/main"`** — the root has an ID, so `binding.main` exists. The code however uses `binding.getRoot()`, so the ID is decorative. It's left over from the Android Studio template.

**`xmlns:app`** — needed for `app:srcCompat` on the `ImageView`. **`xmlns:tools`** — needed for `tools:context`.

**`tools:context=".MainActivity"`** — tells the preview which activity to simulate (theme, bar). It's stripped at build time; it doesn't reach the APK.

**`layout_width="match_parent"` + `layout_height="match_parent"`** — the root fills the window. When the insets apply padding, the content shrinks inside the bars.

#### Block 2 — `Button`, `ImageView` and `Switch`

```xml
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Button" />

    <ImageView
        android:id="@+id/imageView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        app:srcCompat="@drawable/ic_android_black_24dp" />

    <Switch
        android:id="@+id/switch1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Switch" />
```

**`match_parent` on width + `wrap_content` on height** — the element takes the whole available width and exactly the height it needs. It's the standard combination for the rows of a vertical form.

**`android:text="Button"` is hardcoded.** Lint gives the `HardcodedText` warning. `strings.xml` contains only `app_name` — DMA05 is a lab, not a product. In a real application, every text would be `@string/...`.

**`app:srcCompat` and not `android:src`** — the AppCompat variant, needed for `VectorDrawable` on old APIs and for `app:tint`. The file `ic_android_black_24dp.xml` is a vector, not a PNG.

**`ImageView` has no listener** — it's the counterexample that shows "every widget has a listener" is false. An `ImageView` is pure display; if you want to react to touch, you give it `setOnClickListener` like any `View`.

**`Switch`** is the sliding switch: a single `boolean` value, like a `CheckBox`, but with a different shape. It extends `CompoundButton`, so it gets exactly the same listener as `CheckBox` and `ToggleButton` — the lambda from block 6 of section 27.1.

**Why the ID is `switch1` and not `switch`:** Android Studio's layout generator builds the ID from the widget name and adds a number when the plain name isn't available. The rest got the clean name (`button`, `checkBox`, `seekBar`), `Switch` got `switch1`. The code uses it exactly like that: `binding.switch1`. Don't "fix" the name — the binding is generated from the XML, and if you change the ID you have to change the code too.

**`android:text="Switch"`** is the label next to the button, not the state. **It has no `android:checked`** → it starts off, and the first Toast appears only on the first touch.

#### Block 3 — the five `EditText`s

```xml
    <EditText
        android:id="@+id/editTextText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:inputType="text"
        android:hint="Text" />

    <EditText
        android:id="@+id/editTextTextPassword"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Password"
        android:inputType="textPassword" />

    <EditText
        android:id="@+id/editTextTextEmailAddress"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Email"
        android:inputType="textEmailAddress" />

    <EditText
        android:id="@+id/editTextTime"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Time"
        android:inputType="time" />

    <EditText
        android:id="@+id/editTextDate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Date"
        android:inputType="date" />
```

**`android:ems="10"`** — "the width of 10 M characters". It's a measure from the layout generator. With `layout_width="match_parent"` it no longer has a visible effect; it stays as a leftover.

**`android:hint` is not a value.** It disappears on the first key, and `getText()` returns `""`, not the hint. The "I read the hint as text" confusion is a classic exam mistake.

**`inputType` does two things at once:**

| Value | Keyboard shown | Restricts? |
|---|---|---|
| `text` | normal text | no |
| `textPassword` | normal text | **yes** — masking with dots |
| `textEmailAddress` | with `@` and `.` at hand | **no** — it only optimises the keyboard |
| `time` | digits and `:` | partially — it filters the characters |
| `date` | digits and `/` | partially — it filters the characters |

> **`inputType` does not validate.** You can type an email without `@` in a `textEmailAddress` field and a time "99:99" in a `time` field. Validation is your job, in the code.

**No `EditText` has a listener in the code.** To react to typing you'd need `addTextChangedListener(new TextWatcher(){...})` — three methods, so an anonymous class. DMA05 doesn't do it; `G1097` reads the values only on save, with `getText().toString()`.

#### Block 4 — `CheckBox` and `RadioGroup`

```xml
    <CheckBox
        android:id="@+id/checkBox"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="CheckBox" />

    <RadioGroup
        android:id="@+id/radioGroup"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" >

        <RadioButton
            android:id="@+id/radioButton1"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="First Option" />

        <RadioButton
            android:id="@+id/radioButton2"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Second Option" />

    </RadioGroup>
```

**`CheckBox` = 0..n independent choices. `RadioGroup` = exactly 0 or 1.** The group enforces mutual exclusion: when you select `radioButton2`, `radioButton1` is unchecked automatically. Two `RadioButton`s **without** a `RadioGroup` around them would behave like checkboxes — that's the whole role of the container.

**`RadioGroup` has no `android:orientation`** → it defaults to **vertical**. The two buttons are stacked. In `G1097`, `rgApproval` has `orientation="horizontal"` and is wrapped in a `HorizontalScrollView`.

**No button is checked at start.** `getCheckedRadioButtonId()` returns `-1` until the first touch, and the listener doesn't fire at inflate. In `G1097`, the first button has `android:checked="true"` so that a value always exists.

**The children have IDs**, so `binding.radioButton1` and `binding.radioButton2` exist. The code doesn't use them — it goes through `group.findViewById(checkedId)`. Both paths are valid.

#### Block 5 — `ToggleButton`, `ProgressBar`, `SeekBar`, `RatingBar`

```xml
    <ToggleButton
        android:id="@+id/toggleButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="ToggleButton" />

    <ProgressBar
        android:id="@+id/progressBar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <SeekBar
        android:id="@+id/seekBar"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <RatingBar
        android:id="@+id/ratingBar"
        android:numStars="5"
        android:layout_gravity="center_horizontal"
        android:stepSize="0.5"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
</LinearLayout>
```

**`ToggleButton`** is a button with two states. `android:text` is the label of the **ON** state; the label of the OFF state is `"OFF"` by default. For full control there are `android:textOn` / `android:textOff` — unused here, hence the inconsistency "ToggleButton" / "OFF".

**`ProgressBar` without `style`** would be the circle spinning forever. `?android:attr/progressBarStyleHorizontal` turns it into a horizontal bar. It has no `android:progress`, so it sits at 0 — and it's never touched from the code. It's there as inventory, not as functionality.

**`SeekBar` without `android:max`** → the default maximum is **100**. Without `android:progress` → the initial value is 0. That's why the first Toast after a touch says a value between 0 and 100.

**`SeekBar` extends `ProgressBar`** (through `AbsSeekBar`). That's why it has `getProgress()` and why it's "related" to the bar above — it just adds the finger and the three touch events.

**`RatingBar` with `layout_width="wrap_content"`** — it's as wide as the 5 stars, not as the screen. **`layout_gravity="center_horizontal"`** centres it on the cross axis of the vertical `LinearLayout`. **`numStars="5"`** and **`stepSize="0.5"`** give half stars; the default value is 0, so no star is lit at start.

**`RatingBar` extends `AbsSeekBar`**, so it too is a `ProgressBar` with `getProgress()`. Same family, different behaviour.

---

## 27.3 `AndroidManifest.xml`

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
        android:theme="@style/Theme.DMA05">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
```

**There is no `package` attribute.** Since AGP 8, the package comes from `namespace = "ro.ase.ie.dma05"` in `build.gradle.kts`. That's why `.MainActivity` (with a leading dot) resolves correctly: the dot means "the application's package".

**`android:exported="true"`** — mandatory since API 31 for any component with an `intent-filter`. Without it, the build fails. It means "other applications are allowed to start this" — needed for the launcher icon.

**`android:windowSoftInputMode="adjustResize"`** — when the keyboard appears, the window shrinks instead of being panned. With edge-to-edge, the correct combination would be `adjustResize` **plus** handling `Type.ime()` in the insets listener. DMA05 handles only `systemBars()`, so the keyboard covers the bottom widgets. It doesn't show, because the `EditText`s are at the top.

**`android:theme="@style/Theme.DMA05"`** — defined in `values/themes.xml`, with the parent `Theme.Material3.DayNight.NoActionBar`. `NoActionBar` explains why the app has no title bar: the first widget starts right under the status bar, pushed down only by the insets padding.

**`android:allowBackup` + `dataExtractionRules` + `fullBackupContent`** — the Android Studio template. The files `res/xml/backup_rules.xml` and `res/xml/data_extraction_rules.xml` exist in the project.

**`android:supportsRtl="true"`** — the interface mirrors in right-to-left languages. **`android:roundIcon`** — the round icon for Android 7.1+.

**`xmlns:tools` is declared but unused** — no `tools:` attribute appears in the manifest. A template leftover, harmless.

**There are no permissions.** The app doesn't access anything protected: not internet, not storage, not camera. A manifest without `<uses-permission>` is normal for a widgets lab.

---

## 27.4 ViewBinding vs `findViewById`

### The direct comparison

| Criterion | `findViewById` | `ViewBinding` |
|---|---|---|
| When you find out the ID is wrong | at runtime, as `null` | at compile time |
| Returned type | `View`, with a cast | exact, inferred from the tag |
| Lines of code per view | 1 | 0 |
| Can it return `null`? | **yes** | no, after `inflate` |
| Renaming an ID | manual, can be missed | the build fails |
| Wrong layout | the same ID may be missing → `null` | one class per layout, impossible to confuse |
| Runtime cost | a search in the tree | reading a field |

**The classic equivalent of the file**, for comparison. **It does not exist in the repo** — it's written here only as a reference point:

```java
// ILLUSTRATIVE — this is how MainActivity would have looked without ViewBinding.
// It is not code from DMA05.
setContentView(R.layout.activity_main);

Button button = findViewById(R.id.button);
Switch switch1 = findViewById(R.id.switch1);
CheckBox checkBox = findViewById(R.id.checkBox);
SeekBar seekBar = findViewById(R.id.seekBar);
RadioGroup radioGroup = findViewById(R.id.radioGroup);
ToggleButton toggleButton = findViewById(R.id.toggleButton);
RatingBar ratingBar = findViewById(R.id.ratingBar);
```

Seven extra lines, seven chances to get an ID wrong and seven hidden casts. In `ViewBinding`, all seven lines disappear — only the `binding.` prefix remains in front of each access.

### What the generated class contains

For each `android:id` in the layout, a public final field with the exact type. In DMA05 there are **17**:

| Generated field | Type | Used in the code? |
|---|---|---|
| `main` | `LinearLayout` | no (`getRoot()` is used) |
| `button` | `Button` | **yes** |
| `imageView` | `ImageView` | no |
| `switch1` | `Switch` | **yes** |
| `editTextText` | `EditText` | no |
| `editTextTextPassword` | `EditText` | no |
| `editTextTextEmailAddress` | `EditText` | no |
| `editTextTime` | `EditText` | no |
| `editTextDate` | `EditText` | no |
| `checkBox` | `CheckBox` | **yes** |
| `radioGroup` | `RadioGroup` | **yes** |
| `radioButton1` | `RadioButton` | no |
| `radioButton2` | `RadioButton` | no |
| `toggleButton` | `ToggleButton` | **yes** |
| `progressBar` | `ProgressBar` | no |
| `seekBar` | `SeekBar` | **yes** |
| `ratingBar` | `RatingBar` | **yes** |

**The field name is the ID, letter for letter.** `switch1` → `binding.switch1`; `editTextTextEmailAddress` → `binding.editTextTextEmailAddress`. There's no conversion, no abbreviations.

**`getRoot()` always exists**, whether or not the root has an ID. `binding.main` exists only because the root has `@+id/main`.

### Why `binding` is a field, not a local variable

In DMA05, a local would be enough — everything happens in `onCreate`. The field is the pattern because:

1. in real applications the binding is touched from several methods;
2. the anonymous classes in the listeners may need it;
3. on rotation, `onCreate` runs again and **reassigns** the field — no old binding remains.

**It's not a memory leak** in an `Activity`: the activity and the binding die together. In a `Fragment` it would be — that's why the `_binding` pattern with `onDestroyView` is used there.

### What `ViewBinding` does not do

- **It is not `DataBinding`.** It doesn't allow expressions in XML (`@{...}`), it doesn't bind models to views directly. Only references.
- **It doesn't replace `findViewById` for IDs received at runtime** — like `checkedId` from `RadioGroup`.
- **It doesn't generate fields for views without `android:id`.** Without an ID, there's no name to give the field.

---

## 27.5 The complete flow

```
STARTUP
  AndroidManifest: <intent-filter> MAIN + LAUNCHER
    ↓
  MainActivity.onCreate(savedInstanceState = null)
    ├── super.onCreate                → the activity is bound to the Window
    ├── ActivityMainBinding.inflate(getLayoutInflater())
    │     ├── parses activity_main.xml
    │     ├── creates LinearLayout(main) + 14 direct children
    │     └── fills 17 fields: main, button, imageView, …, ratingBar
    ├── EdgeToEdge.enable(this)       → the window draws under the bars
    ├── setContentView(binding.getRoot())   → the tree reaches the screen
    ├── setOnApplyWindowInsetsListener(root)
    └── 7 × setOn...Listener          → no Toast yet

FIRST LAYOUT PASS
  the insets arrive
    └── v.setPadding(left, top, right, bottom)
          └── all the children move into the safe area

THE USER PRESSES THE BUTTON
  touch → performClick → listener.onClick(v)
    └── Toast.makeText(MainActivity.this, "Button clicked", LENGTH_SHORT).show()
          └── Toast window, ~2 seconds, disappears on its own

THE USER DRAGS THE SEEKBAR
  onStartTrackingTouch(seekBar)          → empty body
  onProgressChanged(seekBar, 1, true)    → Toast "Progress changed to 1"
  onProgressChanged(seekBar, 2, true)    → Toast "Progress changed to 2"
  …                                      → dozens of Toasts, queued up
  onStopTrackingTouch(seekBar)           → empty body

THE USER PRESSES A RADIOBUTTON
  RadioGroup unchecks the other button
    └── onCheckedChanged(group, R.id.radioButton2)
          ├── group.findViewById(R.id.radioButton2) → RadioButton
          └── Toast "Radio button clicked Second Option"

THE USER OPENS THE KEYBOARD
  adjustResize shrinks the window
    └── the IME is NOT compensated (the listener handles only systemBars)
          └── the bottom widgets can be covered

SCREEN ROTATION
  onDestroy → onCreate(savedInstanceState ≠ null)
    ├── binding = ActivityMainBinding.inflate(...)   → new object
    ├── setContentView(binding.getRoot())            → new tree
    ├── the 7 listeners register again
    └── the state of widgets with android:id is restored automatically
          ├── the text in EditText
          ├── the check in Switch / CheckBox / ToggleButton
          ├── the progress in SeekBar
          └── the value in RatingBar
```

**Why the state is restored without code:** `Activity.onSaveInstanceState` saves the view hierarchy automatically, and each `View` with an `android:id` saves its own state. That's why all the widgets in DMA05 have IDs — not just for `binding`, but also for surviving rotation.

**What is not saved:** the Toasts (they disappear) and any value that isn't widget state — for example a counter held in a field of the activity. For those you need your own `onSaveInstanceState`.

---

## 27.6 What to remember

### The file table

| File | The essence |
|---|---|
| `MainActivity.java` | `inflate` → `getRoot` → insets → 7 listeners; a single `findViewById`, on the group, for `checkedId` |
| `activity_main.xml` | vertical `LinearLayout`, 14 children, 17 IDs, each input widget once |
| `AndroidManifest.xml` | no `package` (it comes from `namespace`), `exported="true"`, `adjustResize`, `NoActionBar` theme |

### The five real traps

| # | Trap | Symptom |
|---|---|---|
| 1 | `setContentView(R.layout.activity_main)` left next to the binding | two trees; the listeners on the invisible one; the app seems dead |
| 2 | `setPadding` on the root without adding the padding from the XML | the original padding disappears |
| 3 | `checkedId == -1` in `RadioGroup` | `findViewById(-1)` → `null` → NPE at `getText()` |
| 4 | a Toast on every `onProgressChanged` | dozens of Toasts queued on a single drag |
| 5 | `LinearLayout` without a `ScrollView` | on small screens, the `RatingBar` goes outside the visible area |

### What you must be able to say without looking

1. **`ActivityMainBinding.inflate(getLayoutInflater())`** builds the tree and fills the fields. **`setContentView(binding.getRoot())`** puts it on screen. In that order.
2. **Insets on `getRoot()`** because padding on the root moves all the children into the safe area.
3. **One method → lambda. Three methods → anonymous class.** `SeekBar` is the only one with three.
4. **`MainActivity.this`** is mandatory in the anonymous class, pointless in the lambda.
5. **`checkedId` is an ID, not an index** — that's why `group.findViewById(checkedId)`.
6. **`CompoundButton`** is the base class for `Switch`, `CheckBox`, `ToggleButton` — that's why the same listener signature on all three.
7. **`inputType` chooses the keyboard and filters the characters, but does not validate.**

---

## Chapter 27 summary

- `ViewBinding` generates `ActivityMainBinding` from `activity_main.xml`: 17 fields, one per `android:id`.
- `inflate(getLayoutInflater())` → `setContentView(binding.getRoot())` replaces `setContentView(R.layout...)` + `findViewById`.
- The insets are applied on `binding.getRoot()`, never on a child.
- Seven listeners, five interfaces: `View.OnClickListener`, `CompoundButton.OnCheckedChangeListener` (×3), `RadioGroup.OnCheckedChangeListener`, `SeekBar.OnSeekBarChangeListener`, `RatingBar.OnRatingBarChangeListener`.
- Lambda for single-method interfaces; anonymous class for `SeekBar`, which has three.
- `RadioGroup` enforces mutual exclusion; `checkedId` is a resource ID, not a position.
- `inputType` changes the keyboard and filters, but validates nothing.
- `progressBar` and `imageView` are in the layout but untouched in the code — inventory, not functionality.

**Back to** [cheatsheet](21%20-%20Cheatsheet.md) **or to** [chapter 13 — DMA05: ViewBinding](13%20-%20DMA05%20-%20ViewBinding.md).
