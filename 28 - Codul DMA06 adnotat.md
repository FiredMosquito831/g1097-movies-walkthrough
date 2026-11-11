# Capitolul 28 — Codul DMA06 adnotat

**Obiectiv:** să citești cele 14 fișiere ale proiectului `DMA06` cu explicații pe fiecare bloc — ce face linia, de ce e acolo, ce se strică dacă o scoți. Aplicația afișează aceleași numere de la 1 la 100 în trei feluri, ca să vezi exact ce adaugă fiecare treaptă.

**Sursa:** `DMA06/` la commitul `d719ffc` — 14 fișiere.

**Ce înveți din el:** cele trei trepte pe aceleași date — `ArrayAdapter`, `BaseAdapter` cu `ViewHolder` manual, `RecyclerView`.

**Timp estimat:** 60–90 min (citire activă).

> **Cum citești:** nu citi pasiv. Pentru fiecare bloc, acoperă explicația și încearcă să spui tu ce face. Dacă nu poți, ai găsit ce trebuie repetat.

---

## Harta fișierelor

| # | Fișier | Rol |
|---|---|---|
| 1 | `activities/MainActivity.java` | meniul cu trei butoane |
| 2 | `activities/SingleColumnActivity.java` | treapta 1 — `ListView` + `ArrayAdapter` |
| 3 | `activities/TwoColumnActivity.java` | treapta 2 — `ListView` + adapter propriu |
| 4 | `activities/RecyclerViewActivity.java` | treapta 3 — `RecyclerView` |
| 5 | `adapters/NumberListAdapter.java` | `BaseAdapter` cu `ViewHolder` manual |
| 6 | `adapters/NumberRecyclerAdapter.java` | `RecyclerView.Adapter` |
| 7 | `data/NumberData.java` | sursa: numerele 1–100 |
| 8 | `res/layout/activity_main.xml` | cele trei butoane |
| 9 | `res/layout/activity_single_column.xml` | un singur `ListView` |
| 10 | `res/layout/activity_two_column.xml` | antet + `ListView` |
| 11 | `res/layout/activity_recycler_view.xml` | antet + `RecyclerView` |
| 12 | `res/layout/item_number.xml` | rândul cu două coloane |
| 13 | `res/layout/layout_number_header.xml` | antetul cu două coloane |
| 14 | `AndroidManifest.xml` | declararea celor patru activități |

Trei pachete, trei responsabilități:

```
ro.ase.ie.dma06.activities   ← leagă totul, răspunde la input
ro.ase.ie.adapters           ← transformă date în rânduri
ro.ase.ie.data               ← produce date, nu știe ce e un View
```

> **Atenție la pachete:** ultimele două **nu** conțin `dma06` în declarație, deși folderele da. Detaliul e explicat la 28.1 și contează la test.

---

## 28.0 `MainActivity.java`, `activity_main.xml`, `AndroidManifest.xml` — intrarea în aplicație

### `MainActivity.java` — meniul

```java
package ro.ase.ie.dma06.activities;   // pachetul ecranelor — toate cele 4 activități stau aici

import android.content.Intent;        // „intenția" care pornește o altă activitate
import android.os.Bundle;             // starea salvată la rotire / revenire
import android.view.View;             // tipul returnat de findViewById
import androidx.appcompat.app.AppCompatActivity;   // activitatea de bază (AppCompat)
import ro.ase.ie.dma06.R;             // clasa generată din resurse; `dma06` vine din `namespace`

/** Opens each step of the demo. */
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);        // 1. ciclul de viață al părintelui
        setContentView(R.layout.activity_main);    // 2. umflă layout-ul cu cele 3 butoane

        openOnClick(R.id.btnStep1, SingleColumnActivity.class);    // 3. buton → treapta 1
        openOnClick(R.id.btnStep2, TwoColumnActivity.class);       //    buton → treapta 2
        openOnClick(R.id.btnStep3, RecyclerViewActivity.class);    //    buton → treapta 3
    }

    private void openOnClick(int buttonId, Class<?> activityClass) {
        View button = findViewById(buttonId);      // caută butonul în layout-ul curent
        button.setOnClickListener(v -> startActivity(new Intent(this, activityClass)));
    }
}
```

**De ce un helper și nu trei blocuri identice:** singurele lucruri care diferă între cele trei butoane sunt **id-ul** și **clasa**. Restul e același cod. Dacă ai adăuga o treapta 4, adaugi o linie, nu șapte.

**`Class<?>`** — al doilea parametru al constructorului `Intent(Context, Class<?>)` este clasa componentei care trebuie pornită. `<?>` înseamnă „orice clasă"; aici toate cele trei sunt activități.

**`this` din lambda** — într-o expresie lambda, `this` rămâne instanța care înconjoară lambda, adică `MainActivity`. Într-o clasă anonimă (`new View.OnClickListener() { ... }`), `this` ar fi instanța clasei anonime, care **nu** e `Context`, și ar trebui scris `MainActivity.this`. Aici lambda e mai scurtă exact din acest motiv.

**`startActivity` și nu `launcher`:** ecranele cele trei trepte nu întorc nimic. Nu ai nevoie de `registerForActivityResult`, pentru că nu aștepți un rezultat. Butonul Back te readuce în meniu, iar activitatea de meniu nu a fost distrusă.

**`View button` și nu `MaterialButton`:** helper-ul lucrează cu orice view care are `setOnClickListener`. `findViewById` e generic, dar tipul declarat aici e cel de care ai nevoie: `View`.

> **Fără declararea în manifest, click-ul crapă.** `startActivity` aruncă `ActivityNotFoundException` la runtime, nu la compilare. Compilatorul nu știe ce activități există în aplicație.

### `activity_main.xml` — cele trei butoane

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Rădăcina: coloană verticală, cu conținutul centrat pe verticală și padding pe toate laturile. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center_vertical"
    android:orientation="vertical"
    android:padding="24dp">

    <!-- Titlul ecranului: „From ListView to RecyclerView" -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/main_heading"
        android:textAppearance="?attr/textAppearanceHeadlineSmall" />

    <!-- Subtitlul: „The numbers from 1 to 100, displayed in three steps." -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:layout_marginBottom="24dp"
        android:text="@string/main_description"
        android:textAppearance="?attr/textAppearanceBodyMedium" />

    <!-- Butonul 1: id-ul btnStep1 este căutat în MainActivity.openOnClick -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="@string/step1_title" />

    <!-- Butonul 2: 8dp sub primul -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep2"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="@string/step2_title" />

    <!-- Butonul 3: 8dp sub al doilea -->
    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnStep3"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="@string/step3_title" />
</LinearLayout>
```

**`orientation="vertical"`** — copiii se așază unul sub altul. `gravity="center_vertical"` centrează **grupul** de copii pe verticală în interiorul părintelui. Nu confunda cu `layout_gravity`, care poziționează view-ul în părintele lui.

**`padding="24dp"`** — margine interioară pe toate cele patru laturi. Butoanele nu ating marginile ecranului.

**`layout_width="match_parent"` pe butoane** — butoane late cât ecranul, aliniate perfect. `wrap_content` le-ar face late cât textul, iar cele trei ar avea lățimi diferite.

**Textele vin din `strings.xml`**, nu sunt scrise în XML: `main_heading`, `main_description`, `step1_title`, `step2_title`, `step3_title`. Un text hardcodat ar da warning de lint și nu s-ar putea traduce.

**`?attr/textAppearanceHeadlineSmall`** — stilul de titlu din tema Material3. `Theme.AdaptersDemo` are părintele `Theme.Material3.DayNight`, deci toate atributele `?attr/...` se rezolvă.

**`MaterialButton` e scris cu numele complet** (`com.google.android.material.button.MaterialButton`) pentru că nu e o clasă din `android.widget`, ci din biblioteca Material.

### `AndroidManifest.xml` — cele patru activități

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Nu există atribut `package`: numele aplicației vine din `namespace` în build.gradle.kts -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.AdaptersDemo">

        <!-- Singura activitate care poate fi pornită din exterior: cea din launcher -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Treptele: pornite doar din MainActivity, deci exported="false" -->
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

**Fără `package=`** — versiunile moderne de Android Gradle Plugin iau numele din `namespace` (`ro.ase.ie.dma06`). De aceea numele relative `.activities.MainActivity` se rezolvă în `ro.ase.ie.dma06.activities.MainActivity`.

**`exported="true"` doar pe `MainActivity`** — e singura care are `<intent-filter>` cu `MAIN` + `LAUNCHER`. Din Android 12 (API 31) declararea `exported` e obligatorie pentru orice componentă cu intent-filter. Celelalte trei sunt interne, deci `false`: nicio altă aplicație nu le poate porni.

**`android:label` pe fiecare activitate** — titlul din bara de sus. `Theme.Material3.DayNight` are ActionBar, deci pe ecranul treptei 1 scrie „Step 1: ListView", pe treapta 2 „Step 2: Two columns" etc.

**`supportsRtl="true"`** — permite oglindirea layout-urilor în limbile RTL. De aceea în `item_number.xml` al doilea `TextView` folosește `gravity="end"`, nu `right`.

---

## 28.1 `NumberData.java` — sursa de date

### Fișierul complet, adnotat

```java
package ro.ase.ie.data;          // ATENȚIE: pachetul declarat NU conține `dma06`

import java.util.ArrayList;      // implementarea concretă a listei
import java.util.List;           // interfața folosită în semnături

/** The data source shared by all three steps. */
public final class NumberData {

    private static final int FIRST_NUMBER = 1;    // primul număr din listă
    private static final int LAST_NUMBER = 100;   // ultimul număr, inclusiv

    private NumberData() {
        // This class only has static methods
    }

    public static List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();     // listă nouă la fiecare apel
        for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {
            numbers.add(number);                       // autoboxing: int → Integer
        }
        return numbers;
    }
}
```

### Pachetul nu coincide cu folderul

Folderul este `ro/ase/ie/dma06/data/`, dar pachetul declarat este `ro.ase.ie.data`. Nu e o greșeală de tipar de citit pe diagonală — e chiar așa în repo, și la fel stau lucrurile și la `NumberListAdapter` / `NumberRecyclerAdapter`, care declară `ro.ase.ie.adapters`.

**De ce compilează:** Gradle dă compilatorului lista explicită de fișiere sursă, iar `javac` nu impune ca folderul să coincidă cu pachetul când fișierele sunt date direct. Potrivirea folder–pachet contează doar când compilatorul **caută** o clasă pe classpath.

**Consecința practică:** importurile folosesc pachetul declarat, nu calea din folder:

```java
import ro.ase.ie.data.NumberData;          // corect, așa e în repo
// import ro.ase.ie.dma06.data.NumberData; // greșit — clasa nu există în pachetul ăsta
```

> Dacă „repari" pachetul ca să coincidă cu folderul, trebuie să schimbi și cele trei importuri din activități. La test, scrie exact ce e în repo.

### `final` pe clasă și constructor `private`

**`public final class NumberData`** — clasa nu poate fi extinsă. O clasă utilitară nu are ce să ofere prin moștenire; `final` închide discuția.

**Constructorul `private`** — nimeni nu poate face `new NumberData()`. Toate metodele sunt `static`, deci nu ai nevoie de instanță. E trucul standard pentru clase utilitare: dacă nu o poți instanța, nimeni nu o va face din greșeală.

**Comentariul din constructor** — „This class only has static methods" — documentează **de ce** e gol. Un constructor privat gol fără explicație arată ca o scăpare.

### Constantele

```java
private static final int FIRST_NUMBER = 1;
private static final int LAST_NUMBER = 100;
```

Două numere magice primesc nume. Dacă vrei 1–1000, schimbi o singură linie. Iar bucla devine citibilă: „de la `FIRST_NUMBER` până la `LAST_NUMBER`".

**`static`** — aparțin clasei, nu instanței (și oricum nu există instanțe).
**`final`** — nu se modifică niciodată.
**`private`** — nimeni din afară nu are nevoie de ele.

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

**Listă nouă la fiecare apel** — asta e esențial. Nu există un câmp `static` partajat. Fiecare dintre cele trei activități cheamă `getNumbers()` în `onCreate` și primește **propria** listă. Dacă ar fi un singleton, o modificare făcută într-un ecran ar apărea în toate celelalte, fără să știi de unde vine.

**`List` în semnătură, `ArrayList` în implementare** — returnai interfața, construiești implementarea. Cine primește lista nu depinde de `ArrayList`; poți schimba în `LinkedList` fără să atingi nimic altceva.

**`<=` și nu `<`** — `LAST_NUMBER` e **inclusiv**. Bucla dă exact 100 de elemente: 1, 2, …, 100. Cu `<` ai avea 99.

**Autoboxing** — `numbers.add(number)` primește un `int`, dar lista e `List<Integer>`. Compilatorul transformă automat în `Integer.valueOf(number)`. Pentru valorile −128…127, `Integer.valueOf` întoarce instanțe din cache, deci pentru 1–100 nu se creează 100 de obiecte noi.

**Zero importuri `android.*`** — clasa asta ar putea rula și pe desktop, într-un test JUnit obișnuit. Nu depinde de `Context`, `View` sau `Adapter`. Separarea pe pachete nu e cosmetică: ea permite testarea sursei fără emulator.

### Cine cheamă `getNumbers()`

| Activitate | Ce face cu lista |
|---|---|
| `SingleColumnActivity` | o dă direct lui `ArrayAdapter` |
| `TwoColumnActivity` | o dă lui `NumberListAdapter` |
| `RecyclerViewActivity` | o dă lui `NumberRecyclerAdapter` |

Aceleași date, trei randări diferite. Asta e tot experimentul.

---

## 28.2 `SingleColumnActivity.java` — treapta 1

### Fișierul complet, adnotat

```java
package ro.ase.ie.dma06.activities;

import android.os.Bundle;
import android.widget.ArrayAdapter;   // adapterul gata făcut din SDK
import android.widget.ListView;      // widget-ul care afișează lista

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.data.NumberData;    // pachetul declarat, nu folderul
import ro.ase.ie.dma06.R;


/**
 * Step 1: one column.
 * ArrayAdapter is enough because each row shows one text value.
 */
public class SingleColumnActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_single_column);   // rădăcina layout-ului ESTE ListView-ul

        ListView lvNumbers = findViewById(R.id.lvNumbers); // singurul view din layout

        // ArrayAdapter calls toString() on each number and shows it in a TextView
        ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
                this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
        lvNumbers.setAdapter(adapter);                     // leagă lista de widget
    }
}
```

### Cele trei argumente ale lui `ArrayAdapter`

```java
ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
        this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
```

| Argument | Ce e | De ce |
|---|---|---|
| `this` | `Context` | adapterul are nevoie de el ca să umfle rândul |
| `android.R.layout.simple_list_item_1` | layout **din sistem** | conține un singur `TextView`, cu id-ul `android.R.id.text1` |
| `NumberData.getNumbers()` | `List<Integer>` | datele; adapterul ține **referința**, nu o copie |

Generic-ul `ArrayAdapter<Integer>` trebuie să coincidă cu tipul listei. Dacă ai pune `ArrayAdapter<String>`, ai avea nevoie de `List<String>` — și ai pierde tipul numeric.

### Ce face `ArrayAdapter` în locul tău

**Cheamă `toString()` pe fiecare element.** Pentru `Integer`, `toString()` întoarce exact numărul: `1` → `"1"`. În listă apar „1", „2", „3" … „100".

**Reciclează rândurile.** `ArrayAdapter` implementează `getView` cu `convertView` — exact mecanismul din treapta 2, doar că e ascuns în SDK. Reciclarea **nu** e o invenție a `RecyclerView`; `ListView` o face de la început. Diferența e că aici nu o controlezi tu.

**Nu are `ViewHolder` vizibil.** `ArrayAdapter` caută `android.R.id.text1` în rândul primit și îl umple. Cu un singur `TextView`, căutarea e ieftină și nu merită un holder.

### Limita care naște treapta 2

`ArrayAdapter` știe **un singur** `TextView` per rând. Dacă vrei două coloane — zecimal și binar — nu ai unde să le pui. Nu e o limită de configurare, e o limită de design: un singur text per element.

Aici se termină treapta 1.

### `activity_single_column.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Rădăcina layout-ului este ListView-ul însuși: setContentView îl atașează direct. -->
<ListView xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/lvNumbers"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

**Rădăcina e `ListView`** — nu un `LinearLayout` care să-l învelească. `setContentView` primește direct lista, iar `findViewById(R.id.lvNumbers)` o găsește în arborele de view-uri al activității.

**`match_parent` pe ambele dimensiuni** — lista umple tot ecranul.

**Fără `android:entries`** — lista nu are date din XML. Singura sursă e adapterul. Dacă uiți `setAdapter`, ecranul rămâne gol, fără eroare.

**Fără `android:divider`** — separatorul vine din tema implicită a `ListView`-ului. La `RecyclerView` nu există așa ceva (vezi 28.6).

---

## 28.3 `NumberListAdapter.java` — treapta 2, adapterul propriu

### Blocul 1: declarația, `ViewHolder`, câmpurile, constructorul

```java
package ro.ase.ie.adapters;   // pachetul declarat nu conține `dma06`, deși folderul da

import android.content.Context;      // necesar doar pentru LayoutInflater
import android.view.LayoutInflater;  // transformă XML în obiecte View
import android.view.View;            // rândul (umflat sau reciclat)
import android.view.ViewGroup;       // părintele rândului: ListView-ul
import android.widget.BaseAdapter;   // clasa de bază pentru adaptoare proprii
import android.widget.TextView;      // cele două coloane

import java.util.List;               // interfața pentru lista de numere

import ro.ase.ie.dma06.R;            // resursele aplicației

/** Step 2: fills a two-column row for a ListView. */
public class NumberListAdapter extends BaseAdapter {

    private static class ViewHolder {
        TextView tvDecimal;   // referința la coloana 1
        TextView tvBinary;    // referința la coloana 2
    }

    private final List<Integer> numbers;          // sursa de date, ținută prin referință
    private final LayoutInflater layoutInflater;  // un singur inflater, refolosit

    public NumberListAdapter(Context context, List<Integer> numbers) {
        this.layoutInflater = LayoutInflater.from(context);  // îl obținem o dată, nu la fiecare rând
        this.numbers = numbers;                              // NU copiem lista
    }
```

**De ce `BaseAdapter` și nu `ArrayAdapter`:** `ArrayAdapter` e o implementare completă, gata făcută, pentru un singur text. `BaseAdapter` e scheletul: implementează interfețele `ListAdapter` și `SpinnerAdapter`, dar lasă **patru metode abstracte** — `getCount`, `getItem`, `getItemId`, `getView`. Tu scrii exact ce lipsește.

**De ce `ViewHolder` e o clasă interioară:** cele două `TextView`-uri trebuie să călătorească împreună. Un holder e o cutie cu două referințe, atârnată de rând cu `setTag`. Fără el, ai avea două variabile separate și niciun loc unde să le păstrezi între apeluri.

**De ce `private`:** doar acest adapter îl folosește. Nu apare în nicio semnătură publică.

**De ce `static`:** o clasă interioară non-statică ține o referință implicită la instanța exterioară (`this$0`). `ViewHolder`-ul e lipit de un `View`, iar `View`-ul poate trăi mai mult decât adapterul — `ListView` îl ține în RecycleBin. Dacă holder-ul ar ține adapterul, fiecare rând reciclat ar ține adapterul în viață. `static` elimină referința: holder-ul ține doar două `TextView`-uri. Logic, nici nu are nevoie de adapter ca să existe.

**De ce câmpurile holder-ului **nu** sunt `final`:** sunt atribuite **după** `new ViewHolder()`, în `getView`. Nu pot fi `final` pentru că nu sunt inițializate în constructor. Exact asta repară versiunea `RecyclerView`: mută `findViewById` în constructorul holder-ului și le poate face `final`.

**`private final List<Integer> numbers`** — referința nu se schimbă niciodată. Conținutul listei s-ar putea schimba, dar adapterul arată mereu spre aceeași listă.

**`private final LayoutInflater layoutInflater`** — `LayoutInflater.from(context)` face o căutare internă. O facem **o dată**, în constructor, nu la fiecare rând. În plus, `getView` nu mai are nevoie de `Context`.

**`this.numbers = numbers`** — nu se copiază lista. Adapterul primește referința la lista construită de `NumberData`. Dacă ai modifica lista din afară, adapterul ar vedea modificarea — dar nu ar redesena nimic fără `notifyDataSetChanged()`.

### Blocul 2: cele trei metode de „evidență"

```java
    @Override
    public int getCount() {
        return numbers.size();      // câte rânduri: exact elementele listei
    }

    @Override
    public Integer getItem(int position) {
        return numbers.get(position);   // obiectul de la poziția dată
    }

    @Override
    public long getItemId(int position) {
        // Each number is unique, so the number itself can be the ID
        return numbers.get(position);   // Integer → int → long (widening)
    }
```

**`getCount()`** — primul lucru pe care îl întreabă `ListView`. Determină câte rânduri există și cât de lungă e bara de scroll. Dacă întorci 0, lista e goală.

**`getItem(position)`** — obiectul de la poziția dată. `ListView` îl cheamă când raportează un click (`OnItemClickListener` primește elementul), iar adapterul îl cheamă singur în `getView`.

**`getItemId(position)`** — identitatea elementului. `numbers.get(position)` întoarce `Integer`, care se **unboxează** la `int` și apoi se **extinde** la `long` (widening, conversie implicită sigură). Pentru că numerele 1–100 sunt unice, numărul însuși e un ID valid. Într-o listă cu duplicate (două filme cu același titlu) ai avea nevoie de un câmp `id` separat.

**Când e folosit `getItemId`:** `ListView` îl cheamă când construiește argumentele unui click. Identitatea stabilă (`hasStableIds() == true`) ar permite widget-ului să păstreze selecția între reîncărcări; aici e `false` implicit, dar metoda trebuie oricum implementată — e abstractă în `BaseAdapter`.

**`@Override` pe toate trei** — metodele vin din `Adapter` / `BaseAdapter`. Fără adnotare ar fi tot override, dar compilatorul nu ți-ar semnala o semnătură greșită.

### Blocul 3: `getView` — inima adapterului

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

#### Semnătura

| Parametru | Ce înseamnă |
|---|---|
| `position` | al câtelea rând din listă (0…99) |
| `convertView` | un rând **reciclat** de `ListView`, sau `null` dacă nu există niciunul liber |
| `parent` | `ListView`-ul care cere rândul |

#### Cele două ramuri

```
convertView == null   →  rând NOU:     inflate + findViewById + setTag
convertView != null   →  rând REFOLOSIT: getTag, fără nicio căutare
```

La pornire, `ListView` cere primele ~10 rânduri cu `convertView == null` — nu are ce recicla. Apoi, la fiecare scroll, rândul care iese din ecran intră în RecycleBin și e dat înapoi la următorul apel:

```
getView(0,  null, listView)   → null → inflate + findViewById + setTag   (rând nou)
getView(1,  null, listView)   → null → inflate + findViewById + setTag   (rând nou)
...
getView(9,  null, listView)   → null → inflate + findViewById + setTag   (rând nou)
      ── derulezi o poziție ──
getView(10, rândul0, listView) → != null → getTag + setText             (rând refolosit)
```

**De ce `inflate(R.layout.item_number, parent, false)`:**

- `parent` e necesar ca să se genereze `LayoutParams`-ul corect pentru rând. Fără el, `layout_width="match_parent"` din XML nu are față de ce să se raporteze.
- `false` înseamnă **nu atașa acum**. `ListView` va atașa rândul când îi vine rândul. Cu `true`, `inflate` ar returna **părintele**, nu rândul — și ai primi un `ListView` în loc de un rând.

**`findViewById` de două ori** — doar pe rândul nou. Căutarea parcurge arborele de view-uri; pe un rând cu două `TextView`-uri e ieftină, dar înmulțită cu 100 de rânduri și cu fiecare scroll devine vizibilă.

**`convertView.setTag(holder)`** — `View.setTag(Object)` e un câmp liber pe orice `View`. Nu are legătură cu afișarea; e doar un loc unde atârni un obiect. Aici lipim holder-ul de rândul lui.

**`holder = (ViewHolder) convertView.getTag()`** — `getTag()` întoarce `Object`, deci e nevoie de cast. Cast-ul **nu e verificat** de compilator: dacă ai pus altceva în tag, `ClassCastException` la runtime; dacă ai uitat `setTag`, `getTag()` întoarce `null` și primești `NullPointerException` la prima linie care atinge holder-ul.

> **Fără `setTag`:** lista funcționează până la primul scroll. Apoi crapă cu `NullPointerException`. E cea mai frecventă greșeală la `ListView` cu adapter propriu.

#### Partea de umplere

```java
int number = getItem(position);                    // Integer → int (unboxing)
holder.tvDecimal.setText(String.valueOf(number));  // „42"
holder.tvBinary.setText(Integer.toBinaryString(number));  // „101010"
```

**`int number = getItem(position)`** — `getItem` întoarce `Integer`, atribuirea îl unboxează. Dacă lista ar conține `null`, aici ai avea `NullPointerException`. Aici nu se întâmplă: `NumberData` produce 1–100.

**`String.valueOf(number)`** — echivalent cu `Integer.toString(number)`. Mai explicit decât `number + ""`, care creează un `StringBuilder` în plus.

**`Integer.toBinaryString(number)`** — reprezentarea binară fără zerouri inițiale și fără prefix: `1` → `"1"`, `100` → `"1100100"`. De aceea coloana a doua nu e aliniată frumos la stânga — de asta `item_number.xml` o aliniază la dreapta și îi pune font monospațiat.

**`return convertView`** — întoarce exact rândul primit, acum umplut. Nu construiești un `View` nou la fiecare apel; asta e toată economia.

#### Ce s-ar întâmpla dacă ai ignora reciclarea

Dacă ai face `inflate` la fiecare apel și ai returna mereu un rând nou:

- 100 de rânduri umflate pentru 100 de elemente, deși pe ecran încap ~10;
- memoria crește cu fiecare scroll;
- `ListView` nu mai are ce recicla, deci nici `convertView` nu mai vine;
- scroll-ul devine sacadat.

Codul ar fi **corect** — ar afișa aceleași numere — dar ar fi lent. Reciclarea e optimizare, nu corectitudine.

---

## 28.4 `TwoColumnActivity.java`

### Fișierul complet, adnotat

```java
package ro.ase.ie.dma06.activities;

import android.os.Bundle;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.adapters.NumberListAdapter;   // adapterul propriu, din pachetul `adapters`
import ro.ase.ie.data.NumberData;             // aceleași date ca la treapta 1
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

        ListView lvNumbers = findViewById(R.id.lvNumbers);   // ACELAȘI id ca în treapta 1

        NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
        lvNumbers.setAdapter(adapter);
    }
}
```

**Același id, alt layout** — `lvNumbers` apare și în `activity_single_column.xml`, și în `activity_two_column.xml`. Nu e o problemă: id-urile sunt unice **per layout**, nu global. `findViewById` caută doar în arborele layout-ului curent, deci găsește `ListView`-ul din ecranul curent.

**`this` ca `Context`** — adapterul are nevoie de el pentru `LayoutInflater`. Aici e singurul loc în care activitatea atinge detaliul de inflate.

**Activitatea nu știe ce e într-un rând** — nu există `findViewById(R.id.tvDecimal)` aici. Cele două coloane sunt treaba adapterului. Dacă redenumești `tvDecimal` în XML, se schimbă doar `NumberListAdapter`.

**Comparație cu treapta 1:** aceeași structură, patru linii, doar clasa adapterului diferită. Lecția: **activitatea aproape nu se schimbă; adapterul e locul unde se întâmplă totul.**

### `activity_two_column.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Coloană verticală: antetul sus (înălțime fixă), lista jos (restul ecranului). -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Antetul e un fișier separat, refolosit și de treapta 3 -->
    <include layout="@layout/layout_number_header" />

    <!-- ListView-ul ia tot spațiul rămas după antet -->
    <ListView
        android:id="@+id/lvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

**`<include layout="@layout/layout_number_header" />`** — conținutul fișierului inclus e umflat **în locul** tag-ului. Rezultatul e ca și cum ai fi scris antetul direct aici, dar definiția există într-un singur loc și e folosită de două ecrane.

**`layout_height="0dp"` + `layout_weight="1"`** — în `LinearLayout` vertical, `0dp` + `weight` înseamnă „ia tot ce rămâne după ceilalți". Antetul are `wrap_content`, deci își ia înălțimea lui; lista primește restul.

> **Fără `weight`:** dacă `ListView`-ul ar avea `match_parent`, ar cere toată înălțimea părintelui și antetul ar fi împins în afara ecranului. `0dp` + `weight="1"` e varianta corectă.

**De ce antetul e în afara listei:** rămâne fix când derulezi. Dacă ar fi primul element din listă, ar derula odată cu ea — și ai avea nevoie de un adapter cu două tipuri de rânduri (`getItemViewType`), mult mai complicat pentru un antet static.

### `layout_number_header.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Antetul cu două coloane. Nu are id-uri: codul nu îl atinge niciodată. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="?attr/colorSurfaceVariant"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="12dp">

    <!-- Coloana 1: „Decimal" -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="@string/decimal"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <!-- Coloana 2: „Binary", aliniată la dreapta -->
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

**`background="?attr/colorSurfaceVariant"`** — o nuanță diferită de fundal, ca antetul să se distingă de rânduri. Vine din tema Material3, deci funcționează și în dark mode.

**`textColor="?attr/colorOnSurfaceVariant"`** — culoarea de text potrivită pentru acel fundal. Perechea `colorSurfaceVariant` / `colorOnSurfaceVariant` e gândită împreună; dacă pui un `#888` hardcodat, în dark mode textul dispare.

**`textAppearanceLabelLarge`** — stilul de etichetă, mai mic și mai apăsat decât textul rândurilor (`BodyLarge`).

**Fără id-uri** — nimic din cod nu atinge antetul. E pur vizual.

**Alinierea trebuie să coincidă cu `item_number.xml`:** același `paddingHorizontal="16dp"`, același `weight="1"`, aceeași `gravity="end"` pe a doua coloană. Sunt două fișiere separate, deci potrivirea se face manual. Dacă schimbi padding-ul într-unul singur, antetul nu se mai aliniază cu rândurile — și se vede imediat.

---

## 28.5 `NumberRecyclerAdapter.java` — treapta 3

### Blocul 1: declarația, `ViewHolder`, câmpul, constructorul

```java
package ro.ase.ie.adapters;   // același pachet ca NumberListAdapter

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;                 // contract: parametru / rezultat care nu e null
import androidx.recyclerview.widget.RecyclerView;  // clasa de bază și ViewHolder-ul ei

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

**Parametrul generic** — `RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder>` declară **ce tip de holder** produce adapterul. De aici încolo, toate metodele lucrează cu `NumberViewHolder`, nu cu `RecyclerView.ViewHolder`: `onCreateViewHolder` îl returnează, `onBindViewHolder` îl primește. **Niciun cast nicăieri** — asta e câștigul față de `getTag()`.

**`NumberViewHolder extends RecyclerView.ViewHolder`** — clasa de bază ține `itemView` (rândul) și oferă metode precum `getAdapterPosition()`. Extinzând-o, holder-ul devine tipul pe care `RecyclerView` știe să îl gestioneze.

**`super(itemView)`** — obligatoriu. `RecyclerView.ViewHolder` nu are constructor fără parametri, deci compilatorul te obligă să îl chemi. El salvează rândul în `itemView`.

**`findViewById` în constructorul holder-ului** — asta e jumătatea de **creare**. Rulează o singură dată per holder, nu la fiecare afișare.

**Câmpurile `final`** — pot fi `final` pentru că sunt atribuite în constructor. La `NumberListAdapter` nu puteau, pentru că erau atribuite după `new ViewHolder()`. Diferența asta mică e exact motivul pentru care `RecyclerView` a mutat căutarea în constructor.

**`static class NumberViewHolder`** — din nou `static`, din aceleași două motive: fără referință implicită la adapter și fără dependență de o instanță a adapterului. Aici e `static class` fără `private`, pentru că tipul apare în semnătura publică a clasei (`RecyclerView.Adapter<...NumberViewHolder>`). La `NumberListAdapter` holder-ul e `private static class`, pentru că nu apare în nicio semnătură publică.

**Constructorul adapterului primește doar lista** — spre deosebire de `NumberListAdapter`, nu are nevoie de `Context`. Contextul se ia la nevoie din `parent.getContext()`, în `onCreateViewHolder`.

### Blocul 2: `onCreateViewHolder` — jumătatea de creare

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

**Când rulează:** doar când `RecyclerView` are nevoie de un holder **nou** — pool-ul de reciclare e gol. La pornire, pentru primele rânduri vizibile; apoi din ce în ce mai rar.

**`parent`** — `RecyclerView`-ul. Din el se ia `Context`-ul pentru inflater și el furnizează `LayoutParams`-ul.

**`viewType`** — aici e mereu 0, pentru că nu suprascriem `getItemViewType`. Dacă ai avea două feluri de rânduri (antet + element), ai returna 0/1 din `getItemViewType` și ai face `switch` aici, ca să umfli layout-ul potrivit.

**`LayoutInflater.from(parent.getContext())`** — nu mai e nevoie de un câmp `layoutInflater`, pentru că `parent` cară contextul cu el.

**`.inflate(R.layout.item_number, parent, false)`** — exact același apel ca la `ListView`: același layout, aceiași parametri, același `false`.

**`return new NumberViewHolder(view)`** — întoarce **holder-ul**, nu view-ul. `RecyclerView` are nevoie de holder ca să știe ce a creat și să îl poată recicla.

**`@NonNull`** — contract: `parent` nu e null, rezultatul nu e null. Lint-ul verifică.

### Blocul 3: `onBindViewHolder` și `getItemCount`

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

**Când rulează:** de fiecare dată când un rând **arată** un element — la prima afișare, la fiecare refolosire după scroll, după `notifyItemChanged`, după o animație.

**Nu există `convertView`** — holder-ul vine gata creat. Nu există `if (convertView == null)`, pentru că decizia a fost luată deja de `RecyclerView`.

**Nu există `findViewById`** — referințele sunt în holder, luate la creare.

**`numbers.get(position)` direct** — adapterul nu are `getItem(position)`. Dacă ai nevoie de el (de exemplu pentru un click), îl adaugi ca metodă proprie.

**`getItemCount()` înlocuiește `getCount()`** — același rol: câte elemente are lista.

> **Dacă `getItemCount()` minte:** dacă întoarce mai mult decât `numbers.size()`, `onBindViewHolder` ajunge la `numbers.get(position)` cu o poziție invalidă → `IndexOutOfBoundsException`. Dacă întoarce mai puțin, ultimele elemente pur și simplu nu apar.

### Ce face `RecyclerView` cu cele două metode

```
Un holder iese din ecran
    → RecyclerView îl pune în RecycledViewPool, pe tipul lui (viewType)

Trebuie afișat un rând nou
    → pool-ul are un holder liber?
         da  → onBindViewHolder(holder, poziție)                  (ieftin)
         nu  → onCreateViewHolder(...) + onBindViewHolder(...)    (scump, o singură dată)
```

Acesta este exact `if (convertView == null)` din `getView`, doar că:

1. decizia o ia **framework-ul**, nu codul tău;
2. holder-ul e **tipat** — nu mai există `setTag`, `getTag` sau cast;
3. cele două ramuri sunt **metode separate**, deci poți raționa despre ele independent.

**De ce separarea contează dincolo de viteză:** `RecyclerView` poate reumple un holder existent fără să creeze nimic. La o schimbare de date (`notifyItemChanged(5)`), re-leagă doar rândul 5. La o animație de mutare, re-leagă doar ce s-a schimbat. Cu un singur `getView` care primește `convertView`, framework-ul ar fi trebuit să ghicească ce e creare și ce e umplere.

**Metode opționale pe care `ListView` nu le are:** `onViewRecycled(holder)` (holder-ul intră în pool — poți anula un download de imagine), `onViewAttachedToWindow` / `onViewDetachedFromWindow`, `getItemViewType`. Toate au implementări implicite; nu ești obligat să le scrii.

---

## 28.6 `RecyclerViewActivity.java`

### Fișierul complet, adnotat

```java
package ro.ase.ie.dma06.activities;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.DividerItemDecoration;   // linia dintre rânduri
import androidx.recyclerview.widget.LinearLayoutManager;    // aranjarea pe verticală
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

### Cele trei piese obligatorii

Un `RecyclerView` funcțional are nevoie de:

1. **`LayoutManager`** — cum se aranjează rândurile;
2. **adapter** — ce se afișează;
3. **`ItemAnimator`** — animațiile; vine implicit, nu îl configurezi aici.

`ListView` are toate trei băgate în el. `RecyclerView` le-a scos afară, ca să le poți schimba independent.

### De ce `LayoutManager` e separat

**`RecyclerView` nu știe să aranjeze.** Știe doar să recicleze holder-e și să întrebe un `LayoutManager` ce să facă: câți copii încap, unde stă fiecare, cum se calculează scroll-ul, cât măsoară fiecare rând.

**Consecința practică:** schimbi `LinearLayoutManager` cu `GridLayoutManager(this, 2)` și obții o grilă cu două coloane — **fără să modifici o linie în adapter**. La `ListView`, aranjarea e în codul widget-ului; nu ai cum să o schimbi.

**`new LinearLayoutManager(this)`** — constructorul cu un singur argument înseamnă vertical. Varianta completă: `LinearLayoutManager(context, orientation, reverseLayout)`.

**`setLayoutManager` înainte de `setAdapter`** — ordinea nu e fatală, dar e convenția. Ce **este** fatal: să uiți `setLayoutManager`. Atunci `RecyclerView` nu afișează nimic și nu dă eroare — doar un mesaj în Logcat: `No layout manager attached; skipping layout`.

### `DividerItemDecoration` — separatorul

**`ListView` are `android:divider` în XML.** `RecyclerView` nu are așa ceva. Liniile dintre rânduri sunt desenate de un `ItemDecoration`, iar `DividerItemDecoration` e decorarea gata făcută din bibliotecă.

**`layoutManager.getOrientation()`** — întoarce `RecyclerView.VERTICAL`, adică `1`. `DividerItemDecoration` așteaptă propria constantă, `DividerItemDecoration.VERTICAL`, care e tot `1`. Sunt două constante diferite ca semnificație, dar cu aceleași valori (`0` = orizontal, `1` = vertical în ambele clase), deci linia funcționează.

> **Compilatorul nu poate verifica:** ambele sunt `int`. Dacă ai schimba `LayoutManager`-ul pe orizontală, `getOrientation()` ar întoarce `0`, care e tot `DividerItemDecoration.HORIZONTAL` — deci codul rămâne corect. Potrivirea e reală, nu întâmplătoare, dar se bazează pe valori numerice, nu pe un tip comun.

**`addItemDecoration` înainte de `setAdapter`** — ordinea dintre ele nu contează. Decorarea se aplică la desenare, nu la setarea datelor.

### Adapterul și datele

```java
NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

**Fără `Context`** — adapterul îl ia din `parent` la creare.
**Fără `notifyDataSetChanged()`** — datele sunt fixe, iar `setAdapter` declanșează singur primul layout.

### `activity_recycler_view.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Aceeași structură ca la treapta 2: antet fix sus, listă jos. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Același antet, din același fișier -->
    <include layout="@layout/layout_number_header" />

    <!-- Numele complet: RecyclerView nu e în android.widget, ci în biblioteca AndroidX -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

**Numele complet e obligatoriu** — `RecyclerView` nu e o clasă din `android.widget`, deci XML-ul nu o poate prescurta. La fel se întâmplă cu orice view din biblioteci: `com.google.android.material.button.MaterialButton`, `androidx.recyclerview.widget.RecyclerView`.

**`0dp` + `weight="1"`** — aceeași logică: antetul `wrap_content`, lista ia restul.

**Nicio dependență explicită în `build.gradle.kts`** — nu există o linie `implementation(libs.recyclerview)`. Clasa se rezolvă pentru că biblioteca Material (`com.google.android.material:material`) aduce `androidx.recyclerview` tranzitiv. Dacă ai scoate Material, importul ar crăpa.

---

## 28.7 `item_number.xml` — un singur layout pentru două adaptere

### Fișierul complet, adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- One row with two columns. Steps 2 and 3 both use this layout. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="14dp">

    <!-- Coloana 1: numărul zecimal, aliniat la stânga -->
    <TextView
        android:id="@+id/tvDecimal"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:textAppearance="?attr/textAppearanceBodyLarge" />

    <!-- Coloana 2: numărul binar, aliniat la dreapta, cu font monospațiat -->
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

**Comentariul din capul fișierului** — „Steps 2 and 3 both use this layout" — e chiar miezul capitolului. Același fișier XML servește `ListView`-ul din treapta 2 și `RecyclerView`-ul din treapta 3. Diferența dintre cele două **nu e în layout**, ci în adapter.

**`orientation="horizontal"`** — două coloane, una lângă alta.

**`match_parent` × `wrap_content`** — rândul e lat cât lista și înalt cât conținutul. Înălțimea `wrap_content` se adaptează la font mărit; o înălțime fixă ar tăia textul.

**`paddingHorizontal="16dp"` / `paddingVertical="14dp"`** — spațiu interior. `paddingHorizontal` și `paddingVertical` există din API 26, iar proiectul are `minSdk 33`, deci merge.

**`0dp` + `layout_weight="1"` pe ambele `TextView`-uri** — fiecare ia jumătate din lățime. E echivalentul a „50% / 50%". Dacă ai pune `wrap_content`, fiecare coloană ar fi lată cât textul ei, iar coloanele nu s-ar mai alinia între rânduri.

**`fontFamily="monospace"`** — cifrele au aceeași lățime, deci numerele binare se aliniază frumos la dreapta. E un font din sistem, nu un fișier adăugat în proiect.

**`gravity="end"`** — aliniere la dreapta care respectă direcția de citire. Cu `supportsRtl="true"` în manifest, într-o limbă RTL devine automat la stânga. `right` ar fi rămas mereu la dreapta.

**Fără `android:text`** — rândul e gol în preview și se umple la runtime. Fără adapter, ai vedea 100 de rânduri goale.

**Cele două id-uri sunt contractul** — `tvDecimal` și `tvBinary` sunt căutate de **ambele** adaptoare. Dacă le redenumești, trebuie schimbate în două fișiere Java.

### Același layout, două apeluri `inflate`

```java
// NumberListAdapter.getView
convertView = layoutInflater.inflate(R.layout.item_number, parent, false);

// NumberRecyclerAdapter.onCreateViewHolder
View view = LayoutInflater.from(parent.getContext())
        .inflate(R.layout.item_number, parent, false);
```

Același fișier, aceiași parametri, același `false`. Singurul lucru care diferă e metoda din jur: una primește un `convertView` posibil reciclat, cealaltă creează un holder nou.

---

## 28.8 Comparația finală, linie cu linie

### Corespondența exactă între cele două adaptere

| # | `NumberListAdapter` (ListView) | `NumberRecyclerAdapter` (RecyclerView) | Când rulează |
|---|---|---|---|
| 1 | `public int getCount()` | `public int getItemCount()` | la fiecare măsurare a listei |
| 2 | `public Integer getItem(int position)` | — (se folosește direct `numbers.get(position)`) | la click, respectiv la bind |
| 3 | `public long getItemId(int position)` | — (`getItemId` e opțional, implicit `NO_ID`) | la click |
| 4 | `public View getView(int position, View convertView, ViewGroup parent)` | `onCreateViewHolder(parent, viewType)` + `onBindViewHolder(holder, position)` | la nevoie |
| 5 | `if (convertView == null)` | decizia o ia `RecyclerView`: pool-ul e gol? | la nevoie |
| 6 | `layoutInflater.inflate(R.layout.item_number, parent, false)` | `LayoutInflater.from(parent.getContext()).inflate(...)` | o dată per rând creat |
| 7 | `holder = new ViewHolder()` | `new NumberViewHolder(view)` | o dată per rând creat |
| 8 | `holder.tvDecimal = convertView.findViewById(...)` | `tvDecimal = itemView.findViewById(...)` în constructor | o dată per rând creat |
| 9 | `convertView.setTag(holder)` | `super(itemView)` + evidența internă a `RecyclerView` | o dată per rând creat |
| 10 | `holder = (ViewHolder) convertView.getTag()` | holder-ul vine ca parametru în `onBindViewHolder` | la fiecare afișare |
| 11 | `holder.tvDecimal.setText(...)` | `holder.tvDecimal.setText(...)` | la fiecare afișare |
| 12 | `return convertView` | `void` — holder-ul e deja la `RecyclerView` | la fiecare afișare |

### Ce dispare la trecerea pe `RecyclerView`

| Dispărut | Înlocuit de |
|---|---|
| parametrul `convertView` | pool-ul intern de holder-e |
| `setTag(holder)` / `getTag()` | tipul generic `RecyclerView.Adapter<...NumberViewHolder>` |
| cast-ul `(ViewHolder)` | parametrul `holder`, deja tipat |
| `if (convertView == null)` | decizia internă a `RecyclerView` |
| `return convertView` | `onBindViewHolder` întoarce `void` |
| câmpul `layoutInflater` | `LayoutInflater.from(parent.getContext())` |
| `getItem(position)` | `numbers.get(position)` direct |

### Ce apare la trecerea pe `RecyclerView`

| Apărut | Rol |
|---|---|
| parametrul generic `RecyclerView.Adapter<...>` | tipul holder-ului, verificat la compilare |
| `onCreateViewHolder` | crearea, separată de umplere |
| `onBindViewHolder` | umplerea, fără creare |
| `getItemCount` | înlocuiește `getCount` |
| `super(itemView)` | obligatoriu în constructorul holder-ului |
| `@NonNull` | contracte verificate de lint |
| `viewType` | suport pentru mai multe tipuri de rânduri |
| `LayoutManager` | aranjarea, separată de conținut |
| `ItemDecoration` | separatorii, separați de layout |

### Cele trei trepte, pe aceleași date

| | Treapta 1 | Treapta 2 | Treapta 3 |
|---|---|---|---|
| Widget | `ListView` | `ListView` | `RecyclerView` |
| Adapter | `ArrayAdapter<Integer>` | `NumberListAdapter` | `NumberRecyclerAdapter` |
| Bază | — | `BaseAdapter` | `RecyclerView.Adapter` |
| Layout rând | `android.R.layout.simple_list_item_1` | `item_number.xml` | `item_number.xml` |
| Coloane per rând | 1 | 2 | 2 |
| `ViewHolder` | ascuns în SDK | manual, `setTag`/`getTag` | obligatoriu, automat |
| Creare rând | în `ArrayAdapter` | în `getView`, ramura `null` | `onCreateViewHolder` |
| Umplere rând | în `ArrayAdapter` | în `getView`, după `if` | `onBindViewHolder` |
| Aranjare | verticală fixă | verticală fixă | `LayoutManager` |
| Separator | `android:divider` din temă | `android:divider` din temă | `DividerItemDecoration` |
| Animații | nu | nu | da, implicite |
| `notifyDataSetChanged` | da | da | da (sau `notifyItemChanged`) |

### Aceleași date, trei liste independente

Fiecare activitate cheamă `NumberData.getNumbers()` în `onCreate`. Rezultatul: **trei liste diferite**, cu aceleași valori. Nu există stare partajată între ecrane. Dacă ai modifica lista în treapta 2, treapta 3 nu ar vedea nimic — pentru că are propria copie.

### Răspunsuri scurte pentru test

**„De ce nu ajunge `ArrayAdapter`?"**
Pentru că știe un singur `TextView` per rând. Pentru două coloane ai nevoie de un layout propriu și de un adapter care să îl umple.

**„Ce face `convertView`?"**
Primește rândul care a ieșit din ecran, ca să îl refolosești. Fără el, s-ar umfla 100 de rânduri pentru 100 de elemente.

**„De ce `ViewHolder` e `static`?"**
Ca să nu țină o referință implicită la adapter. Holder-ul e doar o cutie cu referințe la view-uri; nu are nevoie de instanța exterioară.

**„De ce s-a despărțit `getView`?"**
Pentru că face două lucruri cu costuri diferite: creare (scumpă, rară) și umplere (ieftină, frecventă). `RecyclerView` poate chema doar a doua.

**„De ce `LayoutManager` e separat?"**
Ca aranjarea să fie independentă de conținut. Schimbi listă în grilă fără să atingi adapterul.

**„Ce se întâmplă fără `setLayoutManager`?"**
`RecyclerView` nu afișează nimic și nu dă eroare. Doar un mesaj în Logcat.

---

## 28.9 Fluxul complet

### Pornirea

```
PORNIRE
  MainActivity.onCreate
    ├── setContentView(activity_main)
    ├── openOnClick(btnStep1, SingleColumnActivity.class)
    ├── openOnClick(btnStep2, TwoColumnActivity.class)
    └── openOnClick(btnStep3, RecyclerViewActivity.class)
```

### Treapta 1 — `ListView` + `ArrayAdapter`

```
CLICK „Step 1: ListView"
  startActivity(new Intent(this, SingleColumnActivity.class))
    ↓
  SingleColumnActivity.onCreate
    ├── setContentView(activity_single_column)      ← rădăcina e ListView-ul
    ├── findViewById(R.id.lvNumbers)
    ├── NumberData.getNumbers()                      → List<Integer> cu 100 de elemente
    ├── new ArrayAdapter(this, simple_list_item_1, list)
    └── lvNumbers.setAdapter(adapter)
          ↓
  ListView întreabă getCount()                       → 100
  ListView cere getView(0..9, null, listView)        → 10 rânduri umflate
  Scroll → getView(10, rândReciclat, listView)       → doar setText
```

### Treapta 2 — `ListView` + `NumberListAdapter`

```
CLICK „Step 2: Two columns"
  startActivity(new Intent(this, TwoColumnActivity.class))
    ↓
  TwoColumnActivity.onCreate
    ├── setContentView(activity_two_column)          ← include antetul + ListView
    ├── findViewById(R.id.lvNumbers)
    ├── new NumberListAdapter(this, NumberData.getNumbers())
    └── lvNumbers.setAdapter(adapter)
          ↓
  ListView întreabă getCount()                       → 100
  getView(0, null, parent)
    ├── inflate(item_number, parent, false)
    ├── new ViewHolder()
    ├── findViewById(tvDecimal) + findViewById(tvBinary)
    └── setTag(holder)
  getView(10, convertView, parent)
    ├── getTag() → holder
    └── setText × 2
```

### Treapta 3 — `RecyclerView`

```
CLICK „Step 3: RecyclerView"
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
  RecyclerView întreabă getItemCount()               → 100
  LayoutManager măsoară și decide câți holderi încap
  onCreateViewHolder(parent, 0)
    ├── inflate(item_number, parent, false)
    └── new NumberViewHolder(view)
          ├── super(itemView)
          └── findViewById(tvDecimal) + findViewById(tvBinary)
  onBindViewHolder(holder, 0..9)                     → setText × 2
  Scroll → holder reciclat → onBindViewHolder(holder, 10) → setText × 2
```

### Ciclul de viață al unui rând

| Moment | `ListView` | `RecyclerView` |
|---|---|---|
| rândul apare prima dată | `getView(pos, null, parent)` → inflate + findViewById | `onCreateViewHolder` + `onBindViewHolder` |
| rândul iese din ecran | `View`-ul intră în RecycleBin | holder-ul intră în RecycledViewPool |
| rândul reapare | `getView(pos, convertView, parent)` → getTag + setText | `onBindViewHolder(holder, pos)` |
| datele se schimbă | `notifyDataSetChanged()` → tot ecranul reumplut | `notifyItemChanged(pos)` → doar rândul respectiv |
| apeși pe un rând | `OnItemClickListener` → `getItem(position)` | listener pus pe view, în `onBindViewHolder` |

**Ultima linie e o diferență de design, nu de API:** `ListView` are un listener global pe listă; `RecyclerView` nu are `OnItemClickListener`. Îl pui pe fiecare rând, în `onBindViewHolder`, de obicei pe `holder.itemView`. Aici nu e nevoie — niciun rând nu e clickabil.

### Ce nu se schimbă deloc

- `NumberData` — aceeași sursă, aceleași 100 de numere.
- `item_number.xml` — același rând, aceleași două coloane.
- `layout_number_header.xml` — același antet.
- Textul afișat — „1 / 1", „2 / 10", …, „100 / 1100100".

Se schimbă doar **cine** produce rândurile și **cum** sunt aranjate.

---

## 28.10 Ce să reții

- **Trei trepte, aceleași date.** `ArrayAdapter` → `BaseAdapter` cu `ViewHolder` manual → `RecyclerView.Adapter`. Diferența nu e în layout, ci în adapter.
- **`convertView`** e rândul reciclat. `null` = rând nou; non-`null` = refolosește-l.
- **`setTag` / `getTag`** lipesc `ViewHolder`-ul de rând. Fără `setTag`, `getTag` întoarce `null` și lista crapă la primul scroll.
- **`ViewHolder` e `static`** ca să nu țină referință la adapter. La `ListView` e `private static`; la `RecyclerView` e `static` (package-private), pentru că apare în semnătura publică.
- **`getView` s-a despărțit** în `onCreateViewHolder` (creare, rară și scumpă) și `onBindViewHolder` (umplere, frecventă și ieftină).
- **`LayoutManager` e separat** ca aranjarea să fie independentă de conținut. Fără el, `RecyclerView` e gol și tăcut.
- **`RecyclerView` nu are `OnItemClickListener`** global și nu are `android:divider`. Le înlocuiește cu listener pe rând și `ItemDecoration`.
- **`getItemCount()` mincinos** → `IndexOutOfBoundsException` în `onBindViewHolder`.
- **`inflate(layout, parent, false)`** — `parent` pentru `LayoutParams`, `false` ca să nu atașeze acum.
- **Pachetele `data` și `adapters` nu conțin `dma06`** în declarație, deși folderele da. Importurile folosesc pachetul declarat.
- **`NumberData.getNumbers()` întoarce o listă nouă** la fiecare apel. Trei ecrane, trei liste independente.

---

## Rezumat capitol 28

- `DMA06` = trei trepte pe aceleași numere 1–100: `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter`.
- `NumberData` e curat: `final`, constructor `private`, metodă `static`, zero importuri `android.*`.
- Treapta 1: trei linii de adapter, un singur `TextView`, nicio reciclare scrisă de tine.
- Treapta 2: `getView` cu `if (convertView == null)`, `ViewHolder` + `setTag`/`getTag`, `findViewById` o singură dată per rând.
- Treapta 3: `onCreateViewHolder` + `onBindViewHolder` + `getItemCount`, holder tipat, fără cast.
- `item_number.xml` e comun treptelor 2 și 3 — dovada că diferența e în adapter.
- `LayoutManager` și `ItemDecoration` sunt piesele pe care `ListView` le avea înăuntru și `RecyclerView` le-a scos afară.
- `activity_two_column.xml` și `activity_recycler_view.xml` sunt aproape identice: doar widget-ul diferă.

**Înapoi la** [capitolul 12](12%20-%20DMA06%20-%20ListView%20vs%20RecyclerView.md) **sau la** [cheatsheet](21%20-%20Cheatsheet.md).
