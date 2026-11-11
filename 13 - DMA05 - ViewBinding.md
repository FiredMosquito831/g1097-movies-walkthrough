# Capitolul 13 — DMA05: ViewBinding și widget-urile de input

**Obiectiv:** să înțelegi `ViewBinding` — alternativa modernă la `findViewById` — și să treci prin toate widget-urile de input pe care le folosește și aplicația `G1097`, dar aici izolate, fiecare cu un `Toast`.

**Timp estimat:** 40–55 min.

**Sursa:** `DMA05/` la commitul `d719ffc` — 29 de fișiere.

> **De ce contează:** proiectul `G1097` are `buildFeatures { viewBinding = true }` în `build.gradle.kts`, dar codul folosește `findViewById`. Deci feature-ul e activat și **nefolosit** (vezi capitolul 01, pasul 1.3). DMA05 arată cum ar arăta codul dacă l-ai folosi.

---

## Pasul 13.1 — Ce e `ViewBinding`

### De ce

`findViewById(R.id.etTitle)` are trei probleme:

1. **Nu e type-safe.** Dacă pui `TextView tv = findViewById(R.id.etTitle);` unde `etTitle` e un `EditText`, compilatorul nu te prinde. Abia la runtime ai `ClassCastException`.
2. **Întoarce `null`** dacă ID-ul nu există în layout-ul curent. Tot la runtime afli.
3. **Repetiție.** 13 linii de `findViewById` în `ItemActivity`, fiecare cu ID-ul scris de mână.

`ViewBinding` rezolvă toate trei: generează o clasă Java per layout, cu un câmp pentru fiecare view care are `android:id`.

### Cum se activează

În `app/build.gradle.kts` (sau `build.gradle.kts` al modulului, după restructurare):

```kotlin
android {
    // ...
    buildFeatures { viewBinding = true }
}
```

Apoi **Sync Project with Gradle Files**.

### Ce generează

Pentru `res/layout/activity_main.xml` → clasa `ActivityMainBinding`:

```
app/build/generated/data_binding_base_class_source_out/.../databinding/ActivityMainBinding.java
```

Regula de nume: `snake_case` devine `PascalCase` + sufixul `Binding`.

| Fișier layout | Clasă generată |
|---|---|
| `activity_main.xml` | `ActivityMainBinding` |
| `activity_item.xml` | `ActivityItemBinding` |
| `movie_item.xml` | `MovieItemBinding` |
| `item_number.xml` | `ItemNumberBinding` |

> **De reținut:** clasa se generează **la build**. Dacă nu ai făcut build după ce ai adăugat un `android:id`, nu o găsești. **Build → Make Project**.

### Ce conține clasa generată

Pentru fiecare view cu `android:id` în layout, un **câmp public final** cu tipul exact:

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

Tipul e dedus din tag-ul XML. `<Button>` → `Button`. Nu mai poți greși tipul.

### Exercițiu 13.1

**Cerință:** ce se întâmplă dacă un view **nu** are `android:id` în XML? Apare în clasa generată?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai verificat ce view-uri intră în `ActivityMainBinding`.

**Răspunsul:** **nu.** `ViewBinding` generează câmpuri doar pentru view-urile cu `android:id`. Cele fără ID nu pot fi referite din cod — și nici nu ai nevoie, pentru că nu le atingi.

**De ce:** binding-ul trebuie să știe ce nume să dea câmpului. Fără ID, nu are nume.

**De reținut:**
1. `<include>` **fără** ID → conținutul lui e accesibil prin `binding.<numeInclude>`, dar include-ul trebuie să aibă ID ca să ai un câmp.
2. `merge` și `ViewStub` au reguli speciale — nu intră în discuție aici.
3. ID-urile din XML devin nume de câmp **exact** (`switch1` → `binding.switch1`).

**Unde revine:** în `G1097`, `activity_item.xml` are 20 de ID-uri, dar codul folosește 13. Cu `ViewBinding` ai avea câmpuri pentru toate 20 — și nimeni nu s-ar plânge.

</details>

---

## Pasul 13.2 — `inflate` și `getRoot`

### De ce

`ViewBinding` nu înlocuiește `setContentView(int)`. Trebuie să **construiești** binding-ul, apoi să-i dai rădăcina lui `setContentView`.

### Cum

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

### Cei trei pași

| Linie | Ce face |
|---|---|
| `ActivityMainBinding.inflate(getLayoutInflater())` | citește XML-ul și construiește arborele de view-uri |
| `setContentView(binding.getRoot())` | pune arborele pe ecran |
| `binding.button`, `binding.seekBar` … | acces direct, type-safe |

### Corespondența cu varianta clasică

`G1097/MainActivity` (capitolul 04):

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
// binding.button, binding.seekBar — gata, fără findViewById
```

Aceleași trei operații, dar `findViewById` a dispărut complet.

### De ce `getRoot()` și nu `binding.main`

`binding.getRoot()` întoarce **rădăcina** layout-ului, indiferent de tipul ei. Ai putea scrie și `binding.main` dacă rădăcina are `android:id="@+id/main"` — și în DMA05 are. Dar `getRoot()` e convenția: funcționează chiar dacă rădăcina nu are ID.

### Exercițiu 13.2

**Cerință:** înlocuiește `binding.getRoot()` cu `binding.main` în `DMA05`. Compilează? Rulează?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai schimbat argumentul lui `setContentView`.

**Compilează?** **Da** — `binding.main` e un câmp generat (rădăcina are `android:id="@+id/main"`), de tip `LinearLayout`.

**Rulează?** **Da** — arată identic.

**De ce funcționează amândouă:** `getRoot()` întoarce exact același obiect ca `binding.main`, doar că tipul declarat e `View` în loc de `LinearLayout`.

**De reținut:**
1. `getRoot()` există mereu. `binding.<id>` există doar dacă rădăcina are ID.
2. Tipul contează dacă vrei să apelezi metode specifice (`LinearLayout.setOrientation`). Pentru `setContentView`, nu contează.
3. Convenția din repo e `getRoot()` — o păstrezi.

**Unde revine:** în `G1097`, `activity_main.xml` are `android:id="@+id/main"` **pentru insets**, nu pentru binding. Dacă ai migra la `ViewBinding`, ai putea folosi `binding.main` — dar tot `getRoot()` e recomandat.

</details>

---

## Pasul 13.3 — Widget-urile și listenerii lor

### De ce

`DMA05` pune într-un singur ecran toate widget-urile de input, fiecare cu un `Toast` care confirmă că listener-ul s-a declanșat. E un „laborator de widget-uri".

### Cum — inventarul

Din `activity_main.xml`:

| Widget | `android:id` | Listener | Ce se leagă |
|---|---|---|---|
| `Button` | `button` | `setOnClickListener` | click |
| `ImageView` | `imageView` | — | doar afișare |
| `Switch` | `switch1` | `setOnCheckedChangeListener` | bifă glisantă |
| `EditText` | `editTextText` | — | text liber |
| `EditText` | `editTextTextPassword` | — | parolă |
| `EditText` | `editTextTextEmailAddress` | — | email |
| `EditText` | `editTextTime` | — | oră |
| `EditText` | `editTextDate` | — | dată |
| `CheckBox` | `checkBox` | `setOnCheckedChangeListener` | bifă pătrată |
| `RadioGroup` | `radioGroup` | `setOnCheckedChangeListener` | alegere unică |
| `ToggleButton` | `toggleButton` | `setOnCheckedChangeListener` | on/off |
| `RatingBar` | `ratingBar` | `setOnRatingBarChangeListener` | stele |
| `SeekBar` | `seekBar` | `setOnSeekBarChangeListener` | bară glisantă |

### Cum — codul

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

### Trei familii de listeneri

| Interfață | Metode | Lambda? | Widget-uri |
|---|---|---|---|
| `View.OnClickListener` | 1 (`onClick`) | **da** | `Button`, `ImageView`, orice `View` |
| `CompoundButton.OnCheckedChangeListener` | 1 (`onCheckedChanged`) | **da** | `Switch`, `CheckBox`, `ToggleButton`, `RadioButton` |
| `SeekBar.OnSeekBarChangeListener` | **3** | **nu** | `SeekBar` |
| `RadioGroup.OnCheckedChangeListener` | 1 (`onCheckedChanged`) | **da** | `RadioGroup` |
| `RatingBar.OnRatingBarChangeListener` | 1 | **da** | `RatingBar` |

> **Regula:** o singură metodă abstractă = lambda permisă. `SeekBar` are trei, deci clasă anonimă obligatoriu.

### `RadioGroup` — de ce `group.findViewById(checkedId)`

```java
RadioButton selected = group.findViewById(checkedId);
```

`OnCheckedChangeListener` de pe `RadioGroup` primește **ID-ul** butonului selectat (`checkedId`), nu obiectul. Ca să afli textul, cauți butonul după ID.

Alternativa (folosită în `G1097`): iterezi peste copii cu `getChildCount()` / `getChildAt()` și cauți `isChecked()`. Ambele funcționează — prima e mai directă când ai `checkedId`, a doua e mai portabilă când vrei să extragi textul.

### Exercițiu 13.3

**Cerință:** de ce `binding.switch1` are listener cu lambda, dar `binding.seekBar` nu?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai comparat cele două apeluri.

**Răspunsul:** `CompoundButton.OnCheckedChangeListener` are **o** metodă (`onCheckedChanged`), deci e interfață funcțională → lambda merge. `SeekBar.OnSeekBarChangeListener` are **trei** (`onProgressChanged`, `onStartTrackingTouch`, `onStopTrackingTouch`), deci **nu** e funcțională → trebuie clasă anonimă cu toate trei implementate.

**De ce are `SeekBar` trei:** pentru că are trei momente distincte — schimbare de valoare, început de atingere, sfârșit de atingere. `Switch` are un singur moment: s-a schimbat.

**De reținut:**
1. Lambda = **exact o** metodă abstractă.
2. Dacă uiți o metodă din cele trei, clasa nu compilează.
3. Poți lăsa goale `onStartTrackingTouch` / `onStopTrackingTouch` — corpul e obligatoriu, comportamentul nu.

**Unde revine:** în capitolul 07, `ItemActivity` are exact aceeași structură: `swWatched` cu lambda, `sbDuration` cu clasă anonimă.

</details>

---

## Pasul 13.4 — De ce `G1097` nu folosește `ViewBinding`

### De ce

Ai putea crede că e o omisiune. Nu e — e o alegere didactică.

### Explicația

În `G1097/build.gradle.kts`:

```kotlin
buildFeatures { viewBinding = true }
```

Feature-ul e **activat**. Dar `MainActivity` și `ItemActivity` folosesc `findViewById`.

**De ce:** la laborator, `findViewById` arată explicit legătura dintre XML și cod. Cu `ViewBinding`, o parte din învățare dispare — nu mai vezi că `R.id.etTitle` corespunde unui `android:id` din XML.

> **De reținut:** `viewBinding = true` fără să-l folosești nu strică nimic. Generează niște clase care rămân nefolosite. Costul e zero la runtime.

### Cum ai migra `ItemActivity` la `ViewBinding`

**Înainte:**

```java
setContentView(R.layout.activity_item);
etTitle = findViewById(R.id.etTitle);
etRelease = findViewById(R.id.etRelease);
// ... 13 linii
```

**După:**

```java
ActivityItemBinding binding = ActivityItemBinding.inflate(getLayoutInflater());
setContentView(binding.getRoot());
binding.etTitle.setText(...);
binding.etRelease.setText(...);
// fără câmpuri, fără findViewById
```

Cele 13 câmpuri `private EditText etTitle;` … dispar. Devin `binding.etTitle` etc.

### Exercițiu 13.4

**Cerință:** ce se câștigă concret și ce se pierde la migrarea `ItemActivity`?

<details>
<summary>Răspuns — explicativ</summary>

**Ce se câștigă:**
1. **Type safety** — `binding.etTitle` e `TextInputEditText`, nu `EditText`. Nu poți greși tipul.
2. **Mai puțin cod** — 13 câmpuri + 13 linii de `findViewById` dispar.
3. **Null safety** — binding-ul nu poate întoarce `null` pentru un ID existent. `findViewById` poate.
4. **Refactor sigur** — redenumești ID-ul în XML, build-ul pică dacă nu actualizezi codul.

**Ce se pierde:**
1. **Explicitul didactic** — nu mai vezi legătura `R.id.x` ↔ `android:id`.
2. **Ușurința de a citi codul pe bucăți** — `binding.` prefixează fiecare acces.
3. **Timpul de build** — clasele generate se compilează (neglijabil).

**De reținut:**
1. `ViewBinding` **nu** e `DataBinding`. `DataBinding` permite expresii în XML (`@{...}`), `ViewBinding` doar referințe.
2. `ViewBinding` nu funcționează cu `findViewById` amestecat pe același layout fără să ai grijă — dar tehnic poți avea amândouă.
3. Migrarea se face layout cu layout, nu tot proiectul deodată.

**Unde revine:** în capitolul 11, `MovieAdapter` ar putea folosi `MovieItemBinding` în loc de `itemView.findViewById(...)`. Ar fi mai curat, dar repo-ul nu o face.

</details>

---

## Pasul 13.5 — `EditText` și `inputType`

### De ce

`DMA05` are cinci `EditText`-uri, fiecare cu alt `inputType`. E cea mai clară demonstrație a diferenței.

### Cum

| ID | `inputType` | Tastatură | Restricție |
|---|---|---|---|
| `editTextText` | `text` | text normal | acceptă orice |
| `editTextTextPassword` | `textPassword` | text | mascat cu puncte |
| `editTextTextEmailAddress` | `textEmailAddress` | cu `@` și `.` | sugestii de email |
| `editTextTime` | `time` | cifre și `:` | format oră |
| `editTextDate` | `date` | cifre și `/` | format dată |

### Ce contează la test

`inputType` face **două** lucruri simultan:
1. alege **tastatura** afișată;
2. **restricționează** caracterele acceptate.

`textPassword` maschează textul. `numberDecimal` respinge literele. `textEmailAddress` nu respinge nimic, doar optimizează tastatura.

> **De reținut:** `inputType` nu validează. Poți tasta un email invalid — `textEmailAddress` doar îți pune `@` la îndemână.

### Exercițiu 13.5

**Cerință:** în `DMA05`, schimbă `editTextText` în `inputType="numberDecimal"`. Scrie „abc". Ce se întâmplă?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai schimbat tipul câmpului.

**Ce se vede:** tastatura devine numerică. Tastezi „a", „b", „c" — **nu apar**.

**De ce:** `numberDecimal` spune `EditText`-ului să accepte doar cifre, punct și minus. Tastele invalide sunt ignorate la nivel de `InputFilter`, nu la validare.

**De reținut:**
1. `numberDecimal` **respinge** literele. `textEmailAddress` **nu** respinge nimic.
2. Restricția vine din `DigitsKeyListener`, setat automat de `inputType`.
3. Dacă ai nevoie de o restricție custom, adaugi `setFilters(new InputFilter[]{...})`.

**Unde revine:** în `G1097`, `etBudget` are `numberDecimal`, `etPoster` are `textUri`, `etRelease` are `date`. Același mecanism, din capitolul 05.

</details>

---

## Pasul 13.6 — Verificare

### Cum

1. Deschide `DMA05` în Android Studio.
2. Rulează.
3. Apasă fiecare widget. Ar trebui să apară un `Toast` cu ce s-a întâmplat.
4. Verifică în `Build → Generated` că `ActivityMainBinding.java` există.

### Ce verifici în cod

- [ ] `build.gradle.kts` are `buildFeatures { viewBinding = true }`
- [ ] `ActivityMainBinding binding;` e câmp, nu variabilă locală
- [ ] `binding = ActivityMainBinding.inflate(getLayoutInflater())` în `onCreate`
- [ ] `setContentView(binding.getRoot())`
- [ ] insets aplicate pe `binding.getRoot()`, nu pe `findViewById(R.id.main)`
- [ ] zero `findViewById` pentru view-urile din layout
- [ ] `SeekBar` are clasă anonimă, celelalte au lambda

---

## Rezumat capitol 13

- `ViewBinding` generează o clasă per layout, cu un câmp per view cu `android:id`.
- `inflate(getLayoutInflater())` → `setContentView(binding.getRoot())`.
- Type-safe, null-safe, mai puțin cod decât `findViewById`.
- `G1097` are feature-ul activat dar **nefolosit** — alegere didactică.
- Trei familii de listeneri: o metodă → lambda; trei metode (`SeekBar`) → clasă anonimă.
- `inputType` alege tastatura **și** restricționează caracterele.

**Următorul capitol:** [14 - DMA03 - Navigare si meniuri.md](14%20-%20DMA03%20-%20Navigare%20si%20meniuri.md)
