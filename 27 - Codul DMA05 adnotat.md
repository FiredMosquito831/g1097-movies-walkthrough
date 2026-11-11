# Capitolul 27 — Codul DMA05 adnotat

**Obiectiv:** să citești DMA05 ca pe un laborator de widget-uri — fiecare view din XML, fiecare listener din cod și fiecare linie de `ViewBinding`, cu explicația lângă ele.

**Timp estimat:** 45–60 min (citire activă).

**Sursa:** `DMA05/` la commitul `d719ffc` — 29 de fișiere, din care 3 contează pentru capitol: `MainActivity.java`, `activity_main.xml`, `AndroidManifest.xml`.

**Ce înveți din el:** `ViewBinding` (`ActivityMainBinding`), toate widget-urile de input și listenerii lor.

> **Cum citești:** DMA05 nu are logică de business. Are doar UI. Deci tot ce trebuie să înțelegi e legătura XML ↔ cod: ce tag produce ce câmp în `binding`, ce metodă de înregistrare primește ce interfață și de ce unele au lambda, iar altele clasă anonimă.

---

## 27.1 `MainActivity.java` — ViewBinding, linie cu linie

Fișierul are 88 de linii și face un singur lucru: construiește ecranul, îl pune pe display și leagă șapte listeneri. Îl luăm pe blocuri.

### Fișierul complet, adnotat

#### Blocul 1 — pachetul și importurile

```java
package ro.ase.ie.dma05;                              // namespace-ul modulului (build.gradle.kts)

import android.os.Bundle;                             // parametrul lui onCreate
import android.view.View;                             // parametrul lui onClick(View v)
import android.widget.RadioButton;                    // tipul butonului selectat
import android.widget.RadioGroup;                     // tipul parametrului din OnCheckedChangeListener
import android.widget.SeekBar;                        // interfața cu 3 metode
import android.widget.Toast;                          // feedback-ul tuturor listenerilor

import androidx.activity.EdgeToEdge;                  // desenare sub barele de sistem
import androidx.annotation.NonNull;                   // adnotarea din onCheckedChanged
import androidx.appcompat.app.AppCompatActivity;      // clasa de bază
import androidx.core.graphics.Insets;                 // cele 4 valori de padding
import androidx.core.view.ViewCompat;                 // listener-ul de insets
import androidx.core.view.WindowInsetsCompat;         // Type.systemBars()

import ro.ase.ie.dma05.databinding.ActivityMainBinding;   // ← clasa GENERATĂ
```

**`import ro.ase.ie.dma05.databinding.ActivityMainBinding` e singurul import care nu are un fișier în sursă.** Pachetul `databinding` nu există în `src/` — îl fabrică Gradle la build, din `activity_main.xml`. Dacă Android Studio subliniază linia cu roșu, nu ai făcut **Build → Make Project** după ce ai adăugat ultimul `android:id`.

**De ce lipsesc `Button`, `Switch`, `CheckBox`, `ToggleButton`, `RatingBar`, `EditText`, `ImageView`:** în fișier nu apare niciodată numele acestor tipuri. Le accesezi doar ca `binding.button`, `binding.switch1` etc. — compilatorul știe tipul din câmpul generat, tu nu-l mai scrii. `ViewBinding` elimină și importurile, nu doar `findViewById`.

**De ce `View` e importat deși nu-l instanțiezi:** e tipul parametrului din `onClick(View v)` și al parametrului `v` din lambda de insets.

#### Blocul 2 — clasa și câmpul

```java
public class MainActivity extends AppCompatActivity {

    ActivityMainBinding binding;                      // câmp, nu variabilă locală
```

**De ce `ActivityMainBinding`:** numele vine din numele fișierului de layout. Regula e mecanică: `activity_main.xml` → `ActivityMainBinding`, `activity_item.xml` → `ActivityItemBinding`. Nu se poate greși și nu se configurează nicăieri — `buildFeatures { viewBinding = true }` din `build.gradle.kts` e tot ce trebuie.

**De ce câmp și nu variabilă locală:** în DMA05 ar funcționa și local, pentru că totul se întâmplă în `onCreate`. Dar tiparul e câmp pentru că în orice aplicație reală binding-ul e atins și din `onSaveInstanceState`, și din metode ajutătoare, și din listeneri. `ActivityMainBinding binding;` fără `private` e package-private — funcționează, dar `private` ar fi stilul corect.

**Ce se întâmplă înainte de `inflate`:** câmpul e `null`. Nu e „gol", e referință nulă. Orice `binding.button` înainte de linia următoare dă `NullPointerException`.

#### Blocul 3 — `inflate`

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);           // 1. ciclul de viață al părintelui

        binding = ActivityMainBinding.inflate(getLayoutInflater());   // 2. XML → obiecte Java
```

**Ce face `inflate(getLayoutInflater())`, pas cu pas:**

1. `getLayoutInflater()` întoarce `LayoutInflater`-ul activității, deja legat de `Context`-ul și de tema ei. De aceea nu scrii `LayoutInflater.from(this)` — e același obiect.
2. `inflate` citește `res/layout/activity_main.xml`, parsează fiecare tag și construiește obiectele: un `LinearLayout`, un `Button`, un `ImageView` și așa mai departe.
3. La final, parcurge arborele și **umple câmpurile publice** ale clasei generate cu referințele găsite, după `android:id`.
4. Întoarce obiectul `ActivityMainBinding`, pe care îl păstrezi în câmp.

**Aceasta e operația pe care o făcea `setContentView(R.layout.activity_main)` în interior.** Diferența: varianta clasică arunca rezultatul, iar tu îl recăutai cu `findViewById`. Acum rezultatul e păstrat.

**De ce varianta cu un singur argument:** există și `inflate(inflater, parent, attachToRoot)`. Într-o `Activity` nu ai nevoie de ele — `setContentView` furnizează părintele. Varianta cu `parent` se folosește în `Fragment` și în adaptoare.

#### Blocul 4 — `EdgeToEdge`, `setContentView` și insets

```java
        EdgeToEdge.enable(this);                      // 3. conținutul se desenează sub barele de sistem
        setContentView(binding.getRoot());            // 4. arborele construit ajunge pe ecran
        ViewCompat.setOnApplyWindowInsetsListener(binding.getRoot(), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
```

**`setContentView(binding.getRoot())` înlocuiește `setContentView(R.layout.activity_main)`.** `getRoot()` întoarce `LinearLayout`-ul rădăcină — exact view-ul care are `android:id="@+id/main"` în XML. Nu pui amândouă:

> **Capcana nr. 1 din acest fișier:** dacă lași și `setContentView(R.layout.activity_main)` după linia cu binding-ul, Android construiește **un al doilea arbore**, complet separat. Pe ecran ajunge al doilea; `binding` arată spre primul. Cei șapte listeneri se leagă pe view-uri pe care nu le vede nimeni, iar aplicația pare „moartă" — niciun Toast nu apare. Se întâmplă des la migrarea de la `findViewById`.

**De ce insets pe `binding.getRoot()` și nu pe un copil:** `setPadding` pe rădăcină mută **toți** descendenții în zona sigură. Aplicat pe `binding.button`, doar butonul ar fi împins; restul ar rămâne sub ceas și sub bara de navigare. Iar listener-ul trebuie înregistrat pe exact obiectul care e content view — padding pe un view care nu e pe ecran nu se vede.

**De ce `getRoot()` și nu `binding.main`:** în DMA05 rădăcina **are** ID, deci `binding.main` există și e același obiect. Dar `getRoot()` funcționează și când rădăcina nu are `android:id` — de aceea e convenția. `binding.main` e un câmp generat pe care codul nu-l folosește niciodată.

**Ce face fiecare linie din lambda:**

| Linie | Efect |
|---|---|
| `insets.getInsets(WindowInsetsCompat.Type.systemBars())` | scoate cele 4 dimensiuni ale barelor (status + navigare + caption) |
| `v.setPadding(left, top, right, bottom)` | le aplică drept padding pe rădăcină |
| `return insets` | lasă insets-urile să circule mai departe, la copii |

**`return insets`, nu `WindowInsetsCompat.CONSUMED`:** dacă ai întoarce `CONSUMED`, dispatch-ul s-ar opri la rădăcină și niciun copil nu ar mai primi insets-urile. Aici nu contează, dar e regula generală.

**Lambda aici e permisă** pentru că `OnApplyWindowInsetsListener` are o singură metodă: `onApplyWindowInsets(View, WindowInsetsCompat)`.

> **Capcana nr. 2:** `setPadding` **suprascrie** padding-ul din XML, nu îl adună. Rădăcina din DMA05 nu are `android:padding`, deci nu se pierde nimic. Dacă ar avea `16dp`, corect ar fi `v.setPadding(16dp + left, 16dp + top, ...)`.

**Ce nu acoperă `Type.systemBars()`:** tastatura. Când se deschide un `EditText`, IME-ul nu e compensat — ar trebui `WindowInsetsCompat.Type.ime()` într-un al doilea listener sau în același. În DMA05 câmpurile sunt în partea de sus, deci nu se vede problema.

#### Blocul 5 — `Button`, clasă anonimă

```java
        binding.button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show();
            }
        });
```

**`binding.button` e de tip `Button`** — tipul e dedus din tag-ul `<Button>` din XML. Metoda `setOnClickListener` e declarată pe `View`, deci o au toate widget-urile, nu doar butoanele.

**De ce clasă anonimă aici, când interfața are o singură metodă:** `View.OnClickListener` **este** interfață funcțională, deci lambda ar merge. Repo-ul alternează intenționat stilurile ca să le vezi pe amândouă. Echivalentul lambda al blocului întreg:

```java
// Aceeași funcționalitate, stil lambda — NU există în fișierul real.
binding.button.setOnClickListener(v ->
        Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show());
```

**De ce `MainActivity.this` și nu `this`:** în interiorul clasei anonime, `this` e obiectul listener-ului, nu activitatea. Iar `Toast.makeText` cere un `Context`. `MainActivity.this` e sintaxa prin care ieși din clasa anonimă și ajungi la instanța exterioară.

> **Diferența care contează la examen:** într-o **lambda**, `this` se referă la instanța care înconjoară lambda — adică `MainActivity`. În **clasa anonimă**, `this` e clasa anonimă. De aceea lambda nu are nevoie de `MainActivity.this`, iar clasa anonimă are.

**`Toast.LENGTH_SHORT`** ≈ 2 secunde; `LENGTH_LONG` ≈ 3,5 secunde. **`.show()`** e obligatoriu: fără el construiești obiectul `Toast` și îl arunci — pe ecran nu apare nimic.

#### Blocul 6 — `Switch` și `CheckBox`, lambda

```java
        binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        binding.checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "CheckBox clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });
```

**Aceeași interfață pentru două widget-uri diferite.** `Switch` și `CheckBox` extind amândouă `CompoundButton`, care declară `setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener)`. De aceea semnătura lambda e identică: `(CompoundButton buttonView, boolean isChecked)`.

**`buttonView` e widget-ul care a declanșat** — util când aceeași lambda e partajată între mai multe controale. Aici e ignorat. **`isChecked` e noua stare**, nu cea veche.

**De ce lambda:** `OnCheckedChangeListener` are exact o metodă, `onCheckedChanged(CompoundButton, boolean)` → interfață funcțională.

**`"Switch clicked to " + isChecked`** — concatenarea apelează `String.valueOf(boolean)`, deci textul e `...true` sau `...false`. Nu ai nevoie de `if`.

**Listener-ul se declanșează și la schimbări din cod**, nu doar la atingere: un `setChecked(true)` ar produce și el Toast. Aici nu se întâmplă, dar e bine de știut.

#### Blocul 7 — `SeekBar`, clasă anonimă obligatorie

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

**De ce aici nu merge lambda:** `SeekBar.OnSeekBarChangeListener` are **trei** metode abstracte. O interfață funcțională are exact una. Cu trei, ești obligat la clasă anonimă care să le implementeze pe toate.

**Cele trei momente, și de ce există trei:**

| Metodă | Când apare | Parametri utili |
|---|---|---|
| `onProgressChanged` | la fiecare schimbare de valoare | `progress` = valoarea nouă, `fromUser` = vine de la deget? |
| `onStartTrackingTouch` | când degetul atinge bara | — |
| `onStopTrackingTouch` | când degetul se ridică | — |

**`fromUser`** e `true` când schimbarea vine de la utilizator și `false` când vine din `setProgress(...)`. Aici e ignorat — Toast-ul apare în ambele cazuri.

**Corpurile goale sunt legale și obligatorii.** Trebuie să implementezi toate cele trei metode; dacă nu ai ce face într-una, o lași goală. Dacă uiți una, fișierul nu compilează.

**`progress` merge de la 0 la `android:max`.** În XML nu există `android:max`, deci valoarea implicită e **100**.

> **Defectul didactic al acestui bloc:** un Toast pentru fiecare pas înseamnă zeci de Toaste la o singură tragere, puse în coadă. În `ItemActivity` (G1097) același listener scrie într-un `TextView` — comportamentul corect.

#### Blocul 8 — `RadioGroup`

```java
        binding.radioGroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull RadioGroup group, int checkedId) {
                RadioButton selected = group.findViewById(checkedId);
                Toast.makeText(MainActivity.this, "Radio button clicked " + selected.getText(), Toast.LENGTH_SHORT).show();
            }
        });
```

**`checkedId` e un ID de resursă, nu un index și nu obiectul.** Valoarea e `R.id.radioButton1` sau `R.id.radioButton2`. Confuzia „e poziția" e frecventă și duce la `findViewById(0)`.

**De ce `group.findViewById(checkedId)` și nu `findViewById(checkedId)`:** căutarea se face în subarborele grupului. Aici ar funcționa și varianta pe activitate, pentru că ID-urile sunt unice în layout — dar forma cu `group` e cea corectă conceptual.

**Acesta e singurul `findViewById` care supraviețuiește cu `ViewBinding`.** Binding-ul îți dă `binding.radioButton1` și `binding.radioButton2`, dar nu are cum să transforme un `int` primit la runtime într-un câmp. Ai două alternative:

```java
// varianta din fișier
RadioButton selected = group.findViewById(checkedId);

// varianta cu ID-uri comparate — echivalentă, nu există în fișier.
// Se folosește UNA dintre ele, nu amândouă: declară aceeași variabilă.
RadioButton selected = checkedId == R.id.radioButton1
        ? binding.radioButton1
        : binding.radioButton2;
```

**De ce `RadioGroup.OnCheckedChangeListener` are o singură metodă, dar tot clasă anonimă:** din nou, stil alternat. Lambda ar fi perfect validă.

**`@NonNull` pe parametru** vine din `androidx.annotation`. Nu schimbă comportamentul la runtime — e contract pentru lint și pentru cititor: „grupul nu e niciodată null". Adnotarea pe o suprascriere e opțională; Android Studio o adaugă automat când generează metoda.

> **Capcana nr. 3:** dacă `checkedId` ar fi `-1` (se întâmplă după `clearCheck()`), `findViewById(-1)` întoarce `null` și `selected.getText()` aruncă `NullPointerException`. În DMA05 nu se apelează `clearCheck()`, deci nu se întâmplă. În `G1097`, primul buton are `android:checked="true"` tocmai ca să nu existe niciodată „niciunul selectat".

#### Blocul 9 — `ToggleButton`, `RatingBar` și închiderea clasei

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

**`ToggleButton` e al treilea widget cu aceeași interfață.** `CompoundButton` are acum trei consumatori în același fișier: `Switch`, `CheckBox`, `ToggleButton`. Asta e lecția blocului: nu tipul widget-ului decide listener-ul, ci **clasa de bază**.

**`RatingBar.OnRatingBarChangeListener`** are o metodă, `onRatingChanged(RatingBar, float, boolean)` → lambda. `rating` e `float` pentru că `stepSize="0.5"` — valorile sunt 0.0, 0.5, 1.0, … `fromUser` are același sens ca la `SeekBar`.

**`"Rating changed to " + rating`** afișează `3.0`, nu `3` — concatenarea unui `float` păstrează zecimala.

**Cele două linii goale de dinaintea acoladelor** sunt în fișierul real. Nu strică nimic; semnalează că blocul a fost scris incremental, listener cu listener.

### Ce nu are listener — și de ce

Șapte widget-uri au listener. Restul nu:

| View | De ce nu | Ce s-ar folosi dacă ai vrea |
|---|---|---|
| `imageView` | doar afișare | `setOnClickListener` (orice `View` îl are) |
| cele 5 `EditText` | se citesc la nevoie, nu la tastare | `addTextChangedListener(new TextWatcher(){...})` — **3 metode**, deci clasă anonimă |
| `progressBar` | e demonstrativ, rămâne la 0 | `setProgress(int)` din cod |
| `radioButton1/2` | grupul le acoperă | listener pe fiecare buton, rar util |

**`TextWatcher` e celălalt exemplu de interfață cu trei metode** pe care îl întâlnești des, lângă `SeekBar.OnSeekBarChangeListener`. Dacă la test ți se cere „reacționează când utilizatorul tastează", răspunsul e `TextWatcher` cu `beforeTextChanged`, `onTextChanged`, `afterTextChanged`.

### Cele șapte listeneri, într-un tabel

| # | Linia | Widget | Metodă de înregistrare | Interfață | Metode | Stil |
|---|---|---|---|---|---|---|
| 1 | 38 | `button` | `setOnClickListener` | `View.OnClickListener` | 1 | clasă anonimă |
| 2 | 45 | `switch1` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 3 | 49 | `checkBox` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 4 | 53 | `seekBar` | `setOnSeekBarChangeListener` | `SeekBar.OnSeekBarChangeListener` | **3** | clasă anonimă |
| 5 | 70 | `radioGroup` | `setOnCheckedChangeListener` | `RadioGroup.OnCheckedChangeListener` | 1 | clasă anonimă |
| 6 | 78 | `toggleButton` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 7 | 82 | `ratingBar` | `setOnRatingBarChangeListener` | `RatingBar.OnRatingBarChangeListener` | 1 | lambda |

**Regula, într-o propoziție:** o singură metodă abstractă → lambda permisă; două sau mai multe → clasă anonimă obligatorie. Stilul din repo alternează deliberat, ca să vezi ambele forme pe aceeași interfață (`button` e clasă anonimă, deși ar fi putut fi lambda).

---

## 27.2 `activity_main.xml` — inventarul widget-urilor

### Tabelul complet

| `android:id` | Widget | `inputType` / atribut cheie | Listener | Observații |
|---|---|---|---|---|
| `main` | `LinearLayout` (rădăcină) | `orientation="vertical"` | insets (nu listener de widget) | ID-ul **nu** e folosit de cod |
| `button` | `Button` | — | `setOnClickListener` — clasă anonimă | singurul `onClick` din fișier |
| `imageView` | `ImageView` | `app:srcCompat` | — | doar afișare |
| `switch1` | `Switch` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `editTextText` | `EditText` | `text` | — | text liber |
| `editTextTextPassword` | `EditText` | `textPassword` | — | mascat cu puncte |
| `editTextTextEmailAddress` | `EditText` | `textEmailAddress` | — | tastatură cu `@` |
| `editTextTime` | `EditText` | `time` | — | tastatură numerică |
| `editTextDate` | `EditText` | `date` | — | tastatură numerică |
| `checkBox` | `CheckBox` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `radioGroup` | `RadioGroup` | `orientation` implicit vertical | `setOnCheckedChangeListener` — clasă anonimă | primește `checkedId` |
| `radioButton1` | `RadioButton` | — | prin grup | „First Option" |
| `radioButton2` | `RadioButton` | — | prin grup | „Second Option" |
| `toggleButton` | `ToggleButton` | — | `setOnCheckedChangeListener` — lambda | `CompoundButton` |
| `progressBar` | `ProgressBar` | `style=?android:attr/progressBarStyleHorizontal` | — | rămâne la 0 |
| `seekBar` | `SeekBar` | `max` implicit **100** | `setOnSeekBarChangeListener` — clasă anonimă | 3 metode |
| `ratingBar` | `RatingBar` | `numStars="5"`, `stepSize="0.5"` | `setOnRatingBarChangeListener` — lambda | valoare `float` |

**17 ID-uri, 7 folosite în cod.** Celelalte 10 produc câmpuri în `ActivityMainBinding` pe care nimeni nu le atinge — și e perfect normal: binding-ul le generează pe toate, indiferent dacă le folosești.

### Fișierul, adnotat pe blocuri

#### Blocul 1 — rădăcina

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

**`LinearLayout` vertical** — copiii se stivuiesc de sus în jos, unul sub altul. Nu există `ScrollView`: pe un ecran mic, ultimele widget-uri (`SeekBar`, `RatingBar`) pot ieși din zona vizibilă. `G1097` învelește formularul într-un `ScrollView` exact din acest motiv.

**`android:id="@+id/main"`** — rădăcina are ID, deci `binding.main` există. Codul folosește însă `binding.getRoot()`, deci ID-ul e decorativ. E rămas din șablonul Android Studio.

**`xmlns:app`** — necesar pentru `app:srcCompat` de pe `ImageView`. **`xmlns:tools`** — necesar pentru `tools:context`.

**`tools:context=".MainActivity"`** — spune preview-ului ce activitate să simuleze (temă, bară). Se elimină la build; nu ajunge în APK.

**`layout_width="match_parent"` + `layout_height="match_parent"`** — rădăcina umple fereastra. Când insets-urile aplică padding, conținutul se strânge în interiorul barelor.

#### Blocul 2 — `Button`, `ImageView` și `Switch`

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

**`match_parent` pe lățime + `wrap_content` pe înălțime** — elementul ia toată lățimea disponibilă și exact înălțimea de care are nevoie. E combinația standard pentru rândurile unui formular vertical.

**`android:text="Button"` e hardcodat.** Lint dă warning `HardcodedText`. `strings.xml` conține doar `app_name` — DMA05 e laborator, nu produs. Într-o aplicație reală, fiecare text ar fi `@string/...`.

**`app:srcCompat` și nu `android:src`** — varianta AppCompat, necesară pentru `VectorDrawable` pe API-uri vechi și pentru `app:tint`. Fișierul `ic_android_black_24dp.xml` e un vector, nu un PNG.

**`ImageView` nu are listener** — e contraexemplul care arată că „fiecare widget are listener" e fals. Un `ImageView` e afișare pură; dacă vrei să reacționezi la atingere, îi pui `setOnClickListener` ca oricărui `View`.

**`Switch`** e comutatorul glisant: o singură valoare `boolean`, ca un `CheckBox`, dar cu altă formă. Extinde `CompoundButton`, deci primește exact același listener ca `CheckBox` și `ToggleButton` — lambda din blocul 6 al secțiunii 27.1.

**De ce ID-ul e `switch1` și nu `switch`:** generatorul de layout din Android Studio construiește ID-ul din numele widget-ului și adaugă un număr când numele simplu nu e disponibil. Restul au primit numele curat (`button`, `checkBox`, `seekBar`), `Switch` a primit `switch1`. Codul îl folosește exact așa: `binding.switch1`. Nu „corecta" numele — binding-ul se generează din XML, iar dacă schimbi ID-ul trebuie să schimbi și codul.

**`android:text="Switch"`** e eticheta de lângă buton, nu starea. **Nu are `android:checked`** → pornește oprit, iar primul Toast apare abia la prima atingere.

#### Blocul 3 — cele cinci `EditText`

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

**`android:ems="10"`** — „lățimea a 10 caractere M". E o măsură din generatorul de layout-uri. Cu `layout_width="match_parent"` nu mai are efect vizibil; rămâne ca rămășiță.

**`android:hint` nu e valoare.** Dispariție la prima tastă, iar `getText()` întoarce `""`, nu hint-ul. Confuzia „am citit hint-ul ca text" e o greșeală clasică la examen.

**`inputType` face două lucruri simultan:**

| Valoare | Tastatura afișată | Restricționează? |
|---|---|---|
| `text` | text normal | nu |
| `textPassword` | text normal | **da** — mascare cu puncte |
| `textEmailAddress` | cu `@` și `.` la îndemână | **nu** — doar optimizează tastatura |
| `time` | cifre și `:` | parțial — filtrează caracterele |
| `date` | cifre și `/` | parțial — filtrează caracterele |

> **`inputType` nu validează.** Poți tasta un email fără `@` într-un câmp `textEmailAddress` și o oră „99:99" într-un câmp `time`. Validarea e treaba ta, în cod.

**Niciun `EditText` nu are listener în cod.** Pentru reacție la tastare ar trebui `addTextChangedListener(new TextWatcher(){...})` — trei metode, deci clasă anonimă. DMA05 nu o face; `G1097` citește valorile abia la salvare, cu `getText().toString()`.

#### Blocul 4 — `CheckBox` și `RadioGroup`

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

**`CheckBox` = 0..n alegeri independente. `RadioGroup` = exact 0 sau 1.** Grupul impune excluderea reciprocă: când selectezi `radioButton2`, `radioButton1` se debifează automat. Doi `RadioButton` **fără** un `RadioGroup` în jur s-ar comporta ca niște checkbox-uri — asta e tot rolul containerului.

**`RadioGroup` nu are `android:orientation`** → implicit **vertical**. Cele două butoane se stivuiesc. În `G1097`, `rgApproval` are `orientation="horizontal"` și e învelit într-un `HorizontalScrollView`.

**Niciun buton nu e bifat la pornire.** `getCheckedRadioButtonId()` întoarce `-1` până la prima atingere, iar listener-ul nu se declanșează la inflate. În `G1097`, primul buton are `android:checked="true"` ca să existe mereu o valoare.

**Copiii au ID-uri**, deci `binding.radioButton1` și `binding.radioButton2` există. Codul nu le folosește — trece prin `group.findViewById(checkedId)`. Ambele căi sunt valide.

#### Blocul 5 — `ToggleButton`, `ProgressBar`, `SeekBar`, `RatingBar`

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

**`ToggleButton`** e un buton cu două stări. `android:text` e eticheta stării **ON**; eticheta stării OFF e implicit `"OFF"`. Pentru control complet există `android:textOn` / `android:textOff` — nefolosite aici, de unde inconsecvența „ToggleButton" / „OFF".

**`ProgressBar` fără `style`** ar fi cercul care se învârte la infinit. `?android:attr/progressBarStyleHorizontal` îl transformă în bară orizontală. Nu are `android:progress`, deci stă la 0 — și nu e atins niciodată din cod. E acolo ca inventar, nu ca funcționalitate.

**`SeekBar` fără `android:max`** → maximul implicit **100**. Fără `android:progress` → valoarea inițială 0. De aceea primul Toast după o atingere spune o valoare între 0 și 100.

**`SeekBar` extinde `ProgressBar`** (prin `AbsSeekBar`). De aceea are `getProgress()` și de aceea e „rudă" cu bara de deasupra — doar că adaugă degetul și cele trei evenimente de atingere.

**`RatingBar` cu `layout_width="wrap_content"`** — e lat cât cele 5 stele, nu cât ecranul. **`layout_gravity="center_horizontal"`** îl centrează pe axa transversală a `LinearLayout`-ului vertical. **`numStars="5"`** și **`stepSize="0.5"`** dau jumătăți de stea; valoarea implicită e 0, deci nicio stea aprinsă la pornire.

**`RatingBar` extinde `AbsSeekBar`**, deci și ea e un `ProgressBar` cu `getProgress()`. Familia e aceeași, comportamentul diferit.

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

**Nu există atribut `package`.** Din AGP 8, pachetul vine din `namespace = "ro.ase.ie.dma05"` în `build.gradle.kts`. De aceea `.MainActivity` (cu punct în față) se rezolvă corect: punctul înseamnă „pachetul aplicației".

**`android:exported="true"`** — obligatoriu din API 31 pentru orice componentă cu `intent-filter`. Fără el, build-ul eșuează. Înseamnă „alte aplicații au voie să pornească asta" — necesar pentru iconița din launcher.

**`android:windowSoftInputMode="adjustResize"`** — când apare tastatura, fereastra se micșorează în loc să fie panoramată. Cu edge-to-edge, combinația corectă ar fi `adjustResize` **plus** tratarea `Type.ime()` în listener-ul de insets. DMA05 tratează doar `systemBars()`, deci tastatura acoperă widget-urile de jos. Nu se vede, pentru că `EditText`-urile sunt sus.

**`android:theme="@style/Theme.DMA05"`** — definit în `values/themes.xml`, cu părintele `Theme.Material3.DayNight.NoActionBar`. `NoActionBar` explică de ce aplicația nu are bară de titlu: primul widget începe imediat sub bara de status, împins în jos doar de padding-ul de insets.

**`android:allowBackup` + `dataExtractionRules` + `fullBackupContent`** — șablonul Android Studio. Fișierele `res/xml/backup_rules.xml` și `res/xml/data_extraction_rules.xml` există în proiect.

**`android:supportsRtl="true"`** — interfața se oglindește în limbile cu scriere de la dreapta la stânga. **`android:roundIcon`** — iconița rotundă pentru Android 7.1+.

**`xmlns:tools` e declarat, dar nefolosit** — niciun atribut `tools:` nu apare în manifest. Rămășiță de șablon, inofensivă.

**Nu există permisiuni.** Aplicația nu accesează nimic protejat: nici internet, nici stocare, nici cameră. Un manifest fără `<uses-permission>` e normal pentru un laborator de widget-uri.

---

## 27.4 ViewBinding vs `findViewById`

### Comparația directă

| Criteriu | `findViewById` | `ViewBinding` |
|---|---|---|
| Când afli că ID-ul e greșit | la runtime, ca `null` | la compilare |
| Tipul returnat | `View`, cu cast | exact, dedus din tag |
| Linii de cod per view | 1 | 0 |
| Poate întoarce `null`? | **da** | nu, după `inflate` |
| Redenumire ID | manuală, se poate rata | build-ul pică |
| Layout greșit | același ID poate lipsi → `null` | o clasă per layout, imposibil de confundat |
| Cost la runtime | căutare în arbore | citirea unui câmp |

**Echivalentul clasic al fișierului**, pentru comparație. **Nu există în repo** — e scris aici doar ca termen de referință:

```java
// ILUSTRATIV — așa ar fi arătat MainActivity fără ViewBinding.
// Nu e cod din DMA05.
setContentView(R.layout.activity_main);

Button button = findViewById(R.id.button);
Switch switch1 = findViewById(R.id.switch1);
CheckBox checkBox = findViewById(R.id.checkBox);
SeekBar seekBar = findViewById(R.id.seekBar);
RadioGroup radioGroup = findViewById(R.id.radioGroup);
ToggleButton toggleButton = findViewById(R.id.toggleButton);
RatingBar ratingBar = findViewById(R.id.ratingBar);
```

Șapte linii în plus, șapte ocazii de a greși un ID și șapte cast-uri ascunse. În `ViewBinding`, toate șapte liniile dispar — rămâne doar prefixul `binding.` în fața fiecărui acces.

### Ce conține clasa generată

Pentru fiecare `android:id` din layout, un câmp public final cu tipul exact. În DMA05 sunt **17**:

| Câmp generat | Tip | Folosit în cod? |
|---|---|---|
| `main` | `LinearLayout` | nu (se folosește `getRoot()`) |
| `button` | `Button` | **da** |
| `imageView` | `ImageView` | nu |
| `switch1` | `Switch` | **da** |
| `editTextText` | `EditText` | nu |
| `editTextTextPassword` | `EditText` | nu |
| `editTextTextEmailAddress` | `EditText` | nu |
| `editTextTime` | `EditText` | nu |
| `editTextDate` | `EditText` | nu |
| `checkBox` | `CheckBox` | **da** |
| `radioGroup` | `RadioGroup` | **da** |
| `radioButton1` | `RadioButton` | nu |
| `radioButton2` | `RadioButton` | nu |
| `toggleButton` | `ToggleButton` | **da** |
| `progressBar` | `ProgressBar` | nu |
| `seekBar` | `SeekBar` | **da** |
| `ratingBar` | `RatingBar` | **da** |

**Numele câmpului e ID-ul, literă cu literă.** `switch1` → `binding.switch1`; `editTextTextEmailAddress` → `binding.editTextTextEmailAddress`. Nu există conversie, nu există prescurtări.

**`getRoot()` există întotdeauna**, indiferent dacă rădăcina are ID. `binding.main` există doar pentru că rădăcina are `@+id/main`.

### De ce `binding` e câmp, nu variabilă locală

În DMA05, un local ar fi suficient — totul se întâmplă în `onCreate`. Câmpul e tiparul pentru că:

1. în aplicații reale binding-ul e atins din mai multe metode;
2. clasele anonime din listeneri pot avea nevoie de el;
3. la rotire, `onCreate` rulează din nou și **reasignează** câmpul — nu rămâne un binding vechi.

**Nu e o scurgere de memorie** într-o `Activity`: activitatea și binding-ul mor împreună. Într-un `Fragment` ar fi — de aceea acolo se folosește tiparul `_binding` cu `onDestroyView`.

### Ce nu face `ViewBinding`

- **Nu e `DataBinding`.** Nu permite expresii în XML (`@{...}`), nu leagă direct modele de view-uri. Doar referințe.
- **Nu înlocuiește `findViewById` pentru ID-uri primite la runtime** — ca `checkedId` din `RadioGroup`.
- **Nu generează câmpuri pentru view-uri fără `android:id`.** Fără ID, nu are ce nume să dea câmpului.

---

## 27.5 Fluxul complet

```
PORNIRE
  AndroidManifest: <intent-filter> MAIN + LAUNCHER
    ↓
  MainActivity.onCreate(savedInstanceState = null)
    ├── super.onCreate                → activitatea e legată de Window
    ├── ActivityMainBinding.inflate(getLayoutInflater())
    │     ├── parsează activity_main.xml
    │     ├── creează LinearLayout(main) + 14 copii direcți
    │     └── umple 17 câmpuri: main, button, imageView, …, ratingBar
    ├── EdgeToEdge.enable(this)       → fereastra desenează sub bare
    ├── setContentView(binding.getRoot())   → arborele ajunge pe ecran
    ├── setOnApplyWindowInsetsListener(root)
    └── 7 × setOn...Listener          → niciun Toast încă

PRIMA AȘEZARE ÎN PAGINĂ (layout pass)
  insets sosesc
    └── v.setPadding(stânga, sus, dreapta, jos)
          └── toți copiii se mută în zona sigură

UTILIZATORUL APASĂ BUTONUL
  touch → performClick → listener.onClick(v)
    └── Toast.makeText(MainActivity.this, "Button clicked", LENGTH_SHORT).show()
          └── fereastră Toast, ~2 secunde, dispare singură

UTILIZATORUL TRAGE SEEKBAR
  onStartTrackingTouch(seekBar)          → corp gol
  onProgressChanged(seekBar, 1, true)    → Toast "Progress changed to 1"
  onProgressChanged(seekBar, 2, true)    → Toast "Progress changed to 2"
  …                                      → zeci de Toaste, puse în coadă
  onStopTrackingTouch(seekBar)           → corp gol

UTILIZATORUL APASĂ UN RADIOBUTTON
  RadioGroup debifează celălalt buton
    └── onCheckedChanged(group, R.id.radioButton2)
          ├── group.findViewById(R.id.radioButton2) → RadioButton
          └── Toast "Radio button clicked Second Option"

UTILIZATORUL DESCHIDE TASTATURA
  adjustResize micșorează fereastra
    └── IME-ul NU e compensat (listener-ul tratează doar systemBars)
          └── widget-urile de jos pot fi acoperite

ROTIREA ECRANULUI
  onDestroy → onCreate(savedInstanceState ≠ null)
    ├── binding = ActivityMainBinding.inflate(...)   → obiect nou
    ├── setContentView(binding.getRoot())            → arbore nou
    ├── cei 7 listeneri se înregistrează din nou
    └── starea widget-urilor cu android:id se restaurează automat
          ├── textul din EditText
          ├── bifa din Switch / CheckBox / ToggleButton
          ├── progresul din SeekBar
          └── valoarea din RatingBar
```

**De ce starea se restaurează fără cod:** `Activity.onSaveInstanceState` salvează automat ierarhia de view-uri, iar fiecare `View` cu `android:id` își salvează starea proprie. De aceea toate widget-urile din DMA05 au ID-uri — nu doar pentru `binding`, ci și pentru supraviețuirea la rotire.

**Ce nu se salvează:** Toastele (dispar) și orice valoare care nu e stare de widget — de exemplu un contor ținut într-un câmp al activității. Pentru acelea ai nevoie de `onSaveInstanceState` propriu.

---

## 27.6 Ce să reții

### Tabelul fișierelor

| Fișier | Esența |
|---|---|
| `MainActivity.java` | `inflate` → `getRoot` → insets → 7 listeneri; un singur `findViewById`, pe grup, pentru `checkedId` |
| `activity_main.xml` | `LinearLayout` vertical, 14 copii, 17 ID-uri, fiecare widget de input o dată |
| `AndroidManifest.xml` | fără `package` (vine din `namespace`), `exported="true"`, `adjustResize`, temă `NoActionBar` |

### Cele cinci capcane reale

| # | Capcana | Simptomul |
|---|---|---|
| 1 | `setContentView(R.layout.activity_main)` lăsat lângă binding | doi arbori; listenerii pe cel invizibil; aplicația pare moartă |
| 2 | `setPadding` pe rădăcină fără să aduni padding-ul din XML | padding-ul original dispare |
| 3 | `checkedId == -1` la `RadioGroup` | `findViewById(-1)` → `null` → NPE la `getText()` |
| 4 | Toast pe fiecare `onProgressChanged` | zeci de Toaste în coadă la o tragere |
| 5 | `LinearLayout` fără `ScrollView` | pe ecrane mici, `RatingBar` iese din zona vizibilă |

### Ce trebuie să poți spune fără să te uiți

1. **`ActivityMainBinding.inflate(getLayoutInflater())`** construiește arborele și umple câmpurile. **`setContentView(binding.getRoot())`** îl pune pe ecran. În această ordine.
2. **Insets pe `getRoot()`** pentru că padding-ul pe rădăcină mută toți copiii în zona sigură.
3. **O metodă → lambda. Trei metode → clasă anonimă.** `SeekBar` e singurul cu trei.
4. **`MainActivity.this`** e obligatoriu în clasa anonimă, inutil în lambda.
5. **`checkedId` e ID, nu index** — de aceea `group.findViewById(checkedId)`.
6. **`CompoundButton`** e clasa de bază pentru `Switch`, `CheckBox`, `ToggleButton` — de aceea aceeași semnătură de listener la toate trei.
7. **`inputType` alege tastatura și filtrează caracterele, dar nu validează.**

---

## Rezumat capitol 27

- `ViewBinding` generează `ActivityMainBinding` din `activity_main.xml`: 17 câmpuri, unul per `android:id`.
- `inflate(getLayoutInflater())` → `setContentView(binding.getRoot())` înlocuiește `setContentView(R.layout...)` + `findViewById`.
- Insets-urile se aplică pe `binding.getRoot()`, niciodată pe un copil.
- Șapte listeneri, cinci interfețe: `View.OnClickListener`, `CompoundButton.OnCheckedChangeListener` (×3), `RadioGroup.OnCheckedChangeListener`, `SeekBar.OnSeekBarChangeListener`, `RatingBar.OnRatingBarChangeListener`.
- Lambda pentru interfețe cu o metodă; clasă anonimă pentru `SeekBar`, care are trei.
- `RadioGroup` impune excluderea reciprocă; `checkedId` e un ID de resursă, nu o poziție.
- `inputType` schimbă tastatura și filtrează, dar nu validează nimic.
- `progressBar` și `imageView` sunt în layout, dar neatinse în cod — inventar, nu funcționalitate.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [capitolul 13 — DMA05: ViewBinding](13%20-%20DMA05%20-%20ViewBinding.md).
