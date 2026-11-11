# Capitolul 28 — Codul DMA06 adnotat

**Obiectiv:** să citești cele 14 fișiere ale proiectului `DMA06` cu explicația lipită de fiecare linie — ce face, de ce e acolo, ce se strică dacă o scoți. Aplicația afișează aceleași numere de la 1 la 100 în trei feluri, ca să vezi exact ce adaugă fiecare treaptă.

**Sursa:** `DMA06/` la commitul `d719ffc` — 14 fișiere, dintre care 7 Java și 7 XML.

**Ce înveți din el:** cele trei trepte pe aceleași date — `ArrayAdapter`, `BaseAdapter` cu `ViewHolder` manual, `RecyclerView`. Plus singura întrebare care pică la test în fiecare an: **de ce s-a despărțit `getView` în două metode**.

**Timp estimat:** 90–120 min (citire activă, cu fișierele deschise alături).

> **Cum citești:** fiecare fișier are **un singur bloc de cod**, în ordinea din sursă, cu tot comentariul înăuntru. Nu sări peste comentarii ca să ajungi la cod: comentariul *este* materia. Codul din blocuri e **identic cu fișierele din repo**; tot ce apare după `//` sau între `/* */` (respectiv între `<!-- -->` în XML) a fost adăugat pentru explicare.

**Legendă:**

| Marcaj | Sens |
|---|---|
| `Teorie:` | ce spune cursul / documentația despre conceptul din spate |
| `Logică:` | ce face concret codul, pas cu pas |
| `Risc:` | ce se strică dacă lipsește sau e greșit |
| `Ref:` | capitolul din test 1 în care e explicat conceptul pe larg |
| `DANGER!` | greșeală care compilează, dar crapă la runtime |

---

## Cum e organizat capitolul

Fiecare fișier are **un singur bloc de cod**, în ordinea din sursă. Nu sunt fragmente: poți copia blocul, îl pui într-un fișier `.java` sau `.xml` și compilează. Comentariile sunt parte din bloc, ca să nu întrerupă citirea.

Ordinea urmează fluxul aplicației, nu ordinea alfabetică:

```
1.  MainActivity.java            ← unde ajungi prima dată
2.  activity_main.xml            ← ce vezi prima dată
3.  AndroidManifest.xml          ← ce face posibil tot restul
4.  NumberData.java              ← de unde vin datele
5.  SingleColumnActivity.java    ← treapta 1
6.  activity_single_column.xml   ← layout-ul treptei 1
7.  NumberListAdapter.java       ← miezul treptei 2
8.  TwoColumnActivity.java       ← ecranul treptei 2
9.  activity_two_column.xml      ← layout-ul treptei 2
10. layout_number_header.xml     ← antetul comun
11. NumberRecyclerAdapter.java   ← miezul treptei 3
12. RecyclerViewActivity.java    ← ecranul treptei 3
13. activity_recycler_view.xml   ← layout-ul treptei 3
14. item_number.xml              ← rândul comun treptelor 2 și 3
```

**De ce `NumberListAdapter` înainte de `TwoColumnActivity`:** pentru că activitatea e doar un constructor de adapter. Dacă citești întâi activitatea, vezi patru linii și nu înțelegi nimic; dacă citești întâi adapterul, activitatea devine evidentă.

**De ce `item_number.xml` la final:** pentru că e singurul fișier care aparține simultan treptelor 2 și 3. Citit la început, pare un layout oarecare; citit la final, e dovada că diferența dintre cele două trepte nu e în XML.

**Trei lucruri pe care le vei căuta de mai multe ori:**

| Ce cauți | Unde e |
|---|---|
| `if (convertView == null)` | 28.6, `NumberListAdapter.getView` |
| cele trei metode obligatorii | 28.10, `NumberRecyclerAdapter` |
| `setLayoutManager` | 28.11, `RecyclerViewActivity.onCreate` |

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
ro.ase.ie.dma06.activities   ← leagă totul, răspunde la input, cunoaște Context-ul
ro.ase.ie.adapters           ← transformă date în rânduri; nu știe ce ecran le afișează
ro.ase.ie.data               ← produce date; nu știe ce e un View, un Context sau un Adapter
```

> **Atenție la pachete:** ultimele două **nu** conțin `dma06` în declarație, deși folderele da. Detaliul e explicat la 28.3 și contează la test — dacă scrii `import ro.ase.ie.dma06.data.NumberData`, codul nu compilează, pentru că acea clasă nu există în pachetul ăla.

**De ce contează împărțirea pe pachete aici:** cele trei trepte sunt *aceeași aplicație* cu trei randări. Dacă `NumberData` ar fi știut de `Context`, n-ai fi putut-o testa fără emulator. Dacă adaptoarele ar fi știut de activități, n-ai fi putut schimba `ListView` cu `RecyclerView` fără să atingi și ecranul. Separarea nu e cosmetică: ea e motivul pentru care treapta 3 refolosește exact aceleași date și exact același rând XML.

---

## 28.0 `MainActivity.java` — meniul

Fișierul are 26 de linii și face un singur lucru: pornește una dintre cele trei activități. Nu atinge nicio listă, niciun adapter, nicio dată.

```java
/*
 * ======================================================================================
 * FIȘIER: MainActivity.java
 * ======================================================================================
 * LOCAȚIE:  DMA06/src/main/java/ro/ase/ie/dma06/activities/MainActivity.java
 * PACHET:   ro.ase.ie.dma06.activities
 * ROL:      meniul aplicației. Trei butoane, trei activități. Nu atinge nicio listă,
 *           niciun adapter, nicio dată. Tot ce face e să pornească ecranul potrivit.
 *
 * STRUCTURA FIȘIERULUI (3 părți):
 *   1. importuri        — 6 linii
 *   2. onCreate         — 8 linii: umflă layout-ul, apoi trei apeluri identice
 *   3. openOnClick      — 4 linii: findViewById + listener
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - `startActivity` nu întoarce nimic; ecranele nu trimit rezultat înapoi.
 *   - `Class<?>` e un tip de clasă, nu o instanță. `SingleColumnActivity.class` e obiectul.
 *   - `this` dintr-o lambda e MainActivity, nu lambda. De aceea `new Intent(this, ...)` merge.
 *
 * FLUXUL:
 *   MainActivity  ──btnStep1──▶  SingleColumnActivity    (ListView + ArrayAdapter)
 *                 ──btnStep2──▶  TwoColumnActivity      (ListView + NumberListAdapter)
 *                 ──btnStep3──▶  RecyclerViewActivity    (RecyclerView + NumberRecyclerAdapter)
 * ======================================================================================
 */

// ======================================================================================
// BLOCUL 1 — PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Pachetul e cel care dă numele complet al clasei: ro.ase.ie.dma06.activities.MainActivity.
// El trebuie să coincidă cu folderul aici (activities/), spre deosebire de pachetele
// `data` și `adapters`, unde nu coincide — vezi 28.3.
// ======================================================================================

package ro.ase.ie.dma06.activities;                     // pachetul ecranelor; toate cele 4 activități stau aici

import android.content.Intent;                          // obiectul care descrie „pornesc activitatea X"
import android.os.Bundle;                               // starea salvată; aici nu e folosită
import android.view.View;                               // tipul returnat de findViewById
import androidx.appcompat.app.AppCompatActivity;        // activitatea de bază, cu tema AppCompat
import ro.ase.ie.dma06.R;                               // clasa generată din resurse

// `import android.view.View` deși nu construiești niciun View: e tipul variabilei locale
// din openOnClick. findViewById e generic din API 26: <T extends View> T findViewById(int).
// Aici compilatorul nu are de unde deduce T, pentru că rezultatul se atribuie unei
// variabile declarate explicit `View`. Deci `View` apare în cod și are nevoie de import.
//
// De ce AppCompatActivity și nu Activity: aduce AppCompatDelegate, care aplică tema
// Material pe orice versiune de Android și înlocuiește widget-urile la inflate cu
// variantele compatibile (AppCompatTextView, AppCompatButton).
//
// `R` e generată, nu scrisă. Importul are prefixul din `namespace` (ro.ase.ie.dma06),
// nu din folder. Dacă schimbi namespace în build.gradle.kts, importul se schimbă singur
// la următorul build — dar tu trebuie să știi de unde vine.

// ======================================================================================
// THEORY BLOCK: TREI ECRANE, UN MENIU
// ======================================================================================
/*
 * 1. CE ESTE O ACTIVITATE
 *    -   O componentă cu fereastră proprie. Are propriul ciclu de viață și propriul
 *        arbore de view-uri.
 *    -   Se declară în AndroidManifest.xml. Fără declarație, startActivity aruncă
 *        ActivityNotFoundException la runtime, nu la compilare.
 *
 * 2. CUM SE PORNESTE ALTA
 *    -   `startActivity(new Intent(context, Clasa.class))`.
 *    -   Intent-ul explicit (cu clasă) e singurul mod sigur în aceeași aplicație.
 *    -   Activitatea curentă NU e distrusă: e oprită și lăsată pe stivă (back stack).
 *
 * 3. STIVA, LA FIECARE PAS
 *    [MainActivity]                       ← la lansare
 *    [MainActivity, SingleColumnActivity] ← după click pe butonul 1
 *    [MainActivity]                       ← după Back
 *    MainActivity NU se recreează la revenire: primește onRestart → onStart → onResume.
 *    De aceea onCreate-ul meniului rulează o singură dată per instanță.
 *
 * 4. DE CE UN HELPER
 *    Cele trei butoane diferă prin exact două lucruri: id-ul și clasa. Restul e
 *    identic. Un helper parametrizat elimină șase linii duplicate și face evident
 *    ce variază.
 *
 * DIAGRAMA:
 *
 *   click btnStep1
 *     └─ OnClickListener.onClick(v)
 *          └─ startActivity(new Intent(this, SingleColumnActivity.class))
 *               ├─ ActivityManager primește cererea
 *               ├─ PackageManager verifică: există .activities.SingleColumnActivity?
 *               ├─ MainActivity.onPause()           ← rămâne pe stivă
 *               ├─ SingleColumnActivity.onCreate()  ← instanță NOUĂ
 *               └─ SingleColumnActivity.onResume()  ← vizibilă, primește input
 */

/** Opens each step of the demo. */
public class MainActivity extends AppCompatActivity {   // singura activitate cu intent-filter LAUNCHER

    // ==================================================================================
    // METODA 1 — onCreate
    // ==================================================================================
    // Teorie:  prima metodă a ciclului de viață; rulează o dată per instanță.
    // Logică:  1. super.onCreate  2. setContentView  3. trei apeluri openOnClick
    // Risc:    `super.onCreate` trebuie să fie primul; delegate-ul AppCompat are nevoie
    //          de el înainte ca fereastra să fie atinsă.
    // Ref:     capitolul 15 (Application și ciclu de viață).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);             // 1. lansează ciclul de viață al părintelui
        setContentView(R.layout.activity_main);         // 2. umflă activity_main.xml în fereastră

        openOnClick(R.id.btnStep1, SingleColumnActivity.class);    // 3. buton 1 → treapta 1
        openOnClick(R.id.btnStep2, TwoColumnActivity.class);       //    buton 2 → treapta 2
        openOnClick(R.id.btnStep3, RecyclerViewActivity.class);    //    buton 3 → treapta 3
    }

    // `@Override` — metoda există în Activity. Adnotarea nu schimbă comportamentul, dar
    // îi spune compilatorului să verifice semnătura. Dacă ai scrie onCreate(Bundle b, int x),
    // fără @Override ai avea o metodă nouă, care nu e chemată niciodată.
    //
    // `protected`, nu `public` — Activity.onCreate e protected. Metoda e chemată de
    // framework, nu de codul tău.
    //
    // `savedInstanceState` — null la prima pornire, un Bundle când activitatea e recreată
    // (rotire, schimbare de temă, revenire după ce a fost distrusă în fundal). Aici nu e
    // folosit: meniul nu are stare.
    //
    // Ordinea celor trei linii nu e negociabilă. setContentView are nevoie de fereastra
    // creată de super.onCreate. openOnClick are nevoie de arborele construit de
    // setContentView, pentru că findViewById caută în el. Inversate, primele două dau
    // excepții, a treia întoarce null.

    // ==================================================================================
    // METODA 2 — openOnClick
    // ==================================================================================
    // Teorie:  un helper care primește id-ul butonului și clasa de pornit.
    // Logică:  1. findViewById  2. setOnClickListener  3. startActivity(new Intent(...))
    // Risc:    `findViewById` întoarce `View`, nu `Button`; dacă id-ul nu există în layout
    //          întoarce null și `setOnClickListener` dă NullPointerException.
    // Ref:     capitolul 04 (MainActivity - listă).
    // ==================================================================================
    private void openOnClick(int buttonId, Class<?> activityClass) {
        View button = findViewById(buttonId);           // caută butonul în arborele umflat la pasul 2
        button.setOnClickListener(v -> startActivity(new Intent(this, activityClass)));
        //                              ↑ lambda: `this` = MainActivity, deci e Context valid
    }

    // De ce un helper și nu trei blocuri identice: singurele lucruri care diferă între
    // cele trei butoane sunt id-ul și clasa. Restul e același cod. Dacă ai adăuga o
    // treaptă 4, adaugi o linie, nu șapte.
    //
    // `Class<?>` — al doilea parametru al constructorului Intent(Context, Class<?>) este
    // clasa componentei care trebuie pornită. `<?>` înseamnă „orice clasă"; aici toate
    // trei sunt activități, dar tipul nu o impune. Ai putea scrie
    // `Class<? extends Activity>` și ai avea o verificare în plus la compilare.
    //
    // `this` din lambda — într-o expresie lambda, `this` rămâne instanța care înconjoară
    // lambda, adică MainActivity. Într-o clasă anonimă (new View.OnClickListener() {...}),
    // `this` ar fi instanța clasei anonime, care NU e Context, și ar trebui scris
    // MainActivity.this. Aici lambda e mai scurtă exact din acest motiv.
    //
    // `v -> startActivity(...)` — parametrul v e view-ul care a primit click-ul, adică
    // butonul. Nu e folosit: știm deja ce buton e, pentru că listener-ul e instalat pe el.
    //
    // `startActivity` și nu `launcher`: ecranele celor trei trepte nu întorc nimic. Nu ai
    // nevoie de registerForActivityResult, pentru că nu aștepți un rezultat.
    //
    // `View button` și nu `MaterialButton`: helper-ul lucrează cu orice view care are
    // setOnClickListener. findViewById întoarce tipul declarat; aici e View, pentru că
    // helper-ul nu are nevoie de nimic specific unui buton.
    //
    // ==================================================================================
    // CE SE ÎNTÂMPLĂ LA BACK
    // ==================================================================================
    //
    //   SingleColumnActivity.onPause()
    //     → SingleColumnActivity.onStop()
    //     → SingleColumnActivity.onDestroy()        ← instanța moare
    //     → MainActivity.onRestart()
    //     → MainActivity.onStart()
    //     → MainActivity.onResume()                 ← meniul revine, FĂRĂ onCreate
    //
    // De ce contează: onCreate-ul meniului nu rulează a doua oară, deci nici
    // setContentView, nici openOnClick nu se repetă. Butoanele își păstrează
    // listener-ii pentru că arborele de view-uri nu a fost distrus.
    //
    // Ce s-ar întâmpla dacă MainActivity ar fi distrusă între timp (memorie puțină):
    // la revenire, onCreate rulează din nou, cu savedInstanceState nenull. Aici nu
    // contează, pentru că meniul nu are stare de restaurat.
    //
    // ==================================================================================
    // CE NU FACE FIȘIERUL ĂSTA
    // ==================================================================================
    //
    //   -   Nu creează niciun adapter.
    //   -   Nu citește nicio listă.
    //   -   Nu știe ce e un ViewHolder.
    //   -   Nu ține nicio referință la activitățile pe care le pornește.
    //
    // Ultima linie e importantă: după startActivity, MainActivity nu are nicio legătură
    // cu ecranul pornit. Nu poate citi date din el, nu poate afla când se închide, nu
    // primește nimic înapoi. Dacă ai avea nevoie de un rezultat, ai folosi
    // registerForActivityResult — dar niciuna dintre cele trei trepte nu întoarce ceva.
}
```

**Ce trebuie să reții din fișierul ăsta:** nu conține nicio linie de listă. Toată complexitatea capitolului e în cele trei clase pe care le pornește. Meniul e dovada că `startActivity` și `Intent` sunt independente de ce afișează ecranul următor.

**Fără declararea în manifest, click-ul crapă.** `startActivity` aruncă `ActivityNotFoundException` la runtime, nu la compilare. Compilatorul nu știe ce activități există în aplicație — verificarea se face la runtime, când `PackageManager` caută componenta.

---

## 28.1 `activity_main.xml` — cele trei butoane

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FIȘIER: activity_main.xml
     ==================================================================================
     LOCAȚIE:  DMA06/src/main/res/layout/activity_main.xml
     ROL:      layout-ul meniului: două texte (titlu + subtitlu) și trei butoane.
     CONȚINE:  2 × TextView, 3 × MaterialButton
     ID-URI:   btnStep1, btnStep2, btnStep3   ← singurele atinse din cod
     ================================================================================== -->

<!-- De ce XML-ul are nevoie de antet: un layout se citește rar de sus în jos; de obicei
     îl cauți după un id. Antetul îți spune în trei linii ce id-uri există, ca să nu
     derulezi 40 de linii ca să afli dacă butonul se numește btnStep1 sau button1. -->

<!-- Rădăcina: coloană verticală, cu grupul de copii centrat pe verticală și padding pe toate laturile. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center_vertical"
    android:orientation="vertical"
    android:padding="24dp">

    <!-- Titlul ecranului: „From ListView to RecyclerView" (din strings.xml) -->
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

<!-- ======================================================================================
     CE TREBUIE REȚINUT DIN FIȘIER
     ======================================================================================
     orientation="vertical"      copiii se așază unul sub altul, în ordinea din fișier
     gravity="center_vertical"   centrează GRUPUL de copii, nu fiecare copil
     layout_gravity              ar poziționa view-ul în părintele lui — alt atribut!
     padding="24dp"              margine interioară pe toate cele patru laturi
     match_parent pe butoane     late cât ecranul; wrap_content le-ar face inegale
     @+id/btnStep1               `+` = creează id-ul dacă nu există
     MaterialButton              nume complet, pentru că nu e în android.widget
     ?attr/...                   atribut rezolvat din tema curentă (Material3)
     @string/...                 text dintr-un fișier de resurse, traductibil
     layout_marginTop="8dp"      spațiu între butoane, nu padding în ele
     ====================================================================================== -->
```

**`layout_width="match_parent"` pe butoane** — butoane late cât ecranul, aliniate perfect. `wrap_content` le-ar face late cât textul, iar cele trei ar avea lățimi diferite — vizibil urât, pentru că textele au lungimi diferite („Step 1: ListView" vs „Step 3: RecyclerView").

**Textele vin din `strings.xml`**, nu sunt scrise în XML: `main_heading`, `main_description`, `step1_title`, `step2_title`, `step3_title`. Un text hardcodat ar da warning de lint și nu s-ar putea traduce.

**`?attr/textAppearanceHeadlineSmall`** — stilul de titlu din tema Material3. `Theme.AdaptersDemo` are părintele `Theme.Material3.DayNight`, deci toate atributele `?attr/...` se rezolvă. `?attr` înseamnă „caută atributul în tema curentă", spre deosebire de `@style` care înseamnă „folosește exact stilul ăsta".

**Ordinea în XML = ordinea pe ecran.** `LinearLayout` vertical așază copiii în ordinea din fișier. Dacă muți al treilea buton primul, se schimbă și ordinea vizuală, fără nicio linie de cod Java.

---

## 28.2 `AndroidManifest.xml` — cele patru activități

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FIȘIER: AndroidManifest.xml
     ==================================================================================
     LOCAȚIE:  DMA06/src/main/AndroidManifest.xml
     ROL:      declară aplicația, tema și cele patru activități.
     CONȚINE:  1 × <application>, 4 × <activity>, 1 × <intent-filter>
     ATENȚIE:  nu are atribut `package`; numele vine din `namespace` în build.gradle.kts.
     ================================================================================== -->

<!-- Fără `package=` — versiunile moderne de Android Gradle Plugin iau numele din
     `namespace` (ro.ase.ie.dma06). De aceea numele relative `.activities.MainActivity`
     se rezolvă în ro.ase.ie.dma06.activities.MainActivity. Punctul de la început
     înseamnă „lipește numele aplicației în față". -->

<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.AdaptersDemo">

        <!-- Singura activitate care poate fi pornită din exterior: cea din launcher.
             exported="true" e obligatoriu din Android 12 (API 31) pentru orice
             componentă cu intent-filter. -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Treptele: pornite doar din MainActivity, deci exported="false".
             android:label dă titlul din bara de sus a fiecărui ecran. -->
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

<!-- ======================================================================================
     CE TREBUIE REȚINUT DIN FIȘIER
     ======================================================================================
     fără package=            numele vine din namespace (build.gradle.kts)
     .activities.MainActivity punctul = lipește applicationId-ul în față
     exported="true"          doar pe MainActivity, singura cu MAIN + LAUNCHER
     exported="false"         cele trei trepte: nicio altă aplicație nu le poate porni
     android:label            titlul din ActionBar, per activitate
     supportsRtl="true"       de aceea gravity="end" în item_number.xml, nu "right"
     allowBackup="true"       valoarea implicită generată; aici nu există date de salvat
     fără <uses-permission>   aplicația nu atinge rețeaua, fișierele sau senzorii
     fără android:icon        se folosește iconița implicită a proiectului
     ordinea activităților    nu contează; contează doar care are MAIN + LAUNCHER
     ====================================================================================== -->

<!-- Ce se întâmplă dacă uiți o activitate din manifest: compilatorul nu zice nimic,
     pentru că el nu știe ce clase extind Activity. La runtime, startActivity caută
     componenta în PackageManager, nu o găsește și aruncă:

       android.content.ActivityNotFoundException:
       Unable to find explicit activity class
       {ro.ase.ie.dma06/ro.ase.ie.dma06.activities.SingleColumnActivity};
       have you declared this activity in your AndroidManifest.xml?

     Mesajul e explicit și apare imediat la click — deci eroarea e ușor de găsit,
     spre deosebire de cea de la RecyclerView fără LayoutManager. -->
```

**`android:label` pe fiecare activitate** — titlul din bara de sus. `Theme.Material3.DayNight` are ActionBar, deci pe ecranul treptei 1 scrie „Step 1: ListView", pe treapta 2 „Step 2: Two columns", pe treapta 3 „Step 3: RecyclerView".

**`supportsRtl="true"`** — permite oglindirea layout-urilor în limbile RTL. De aceea în `item_number.xml` al doilea `TextView` folosește `gravity="end"`, nu `right`.

**Ordinea activităților în manifest nu contează.** Cea care pornește la lansare e cea cu `MAIN` + `LAUNCHER`, nu prima din fișier. Poți să le muți în orice ordine.

**Ce lipsește și e bine că lipsește:** nicio permisiune (`<uses-permission>`), niciun `<service>`, niciun `<provider>`. Aplicația nu atinge rețeaua, fișierele sau senzorii. Un manifest de laborator curat e și cea mai bună dovadă că tot ce se întâmplă în aplicație e local.

---

## 28.3 `NumberData.java` — sursa de date

Fișierul are 23 de linii, dintre care 16 de cod. Restul sunt comentarii — și e normal: întrebarea de la test nu e „ce face `getNumbers()`", ci „de ce constructorul e privat".

```java
/*
 * ======================================================================================
 * FIȘIER: NumberData.java
 * ======================================================================================
 * LOCAȚIE:  DMA06/src/main/java/ro/ase/ie/dma06/data/NumberData.java
 * PACHET:   ro.ase.ie.data          ← ATENȚIE: nu conține `dma06`, deși folderul da
 * ROL:      singura sursă de date a aplicației. Produce o listă cu numerele 1..100.
 *           Nu știe ce e un View, un Context, un Adapter sau o activitate.
 *
 * STRUCTURA FIȘIERULUI (3 părți):
 *   1. constante      — 2 linii: FIRST_NUMBER, LAST_NUMBER
 *   2. constructor    — privat și gol, cu un comentariu care explică de ce e gol
 *   3. getNumbers()   — 7 linii: buclă și return
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - `final` pe clasă + constructor `private` + metode `static` = clasă utilitară.
 *   - Metoda întoarce o listă NOUĂ la fiecare apel, nu una partajată.
 *   - Zero importuri `android.*`: clasa asta ar rula și pe desktop.
 * ======================================================================================
 */

// ======================================================================================
// BLOCUL 1 — PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Pachetul declarat NU conține `dma06`, deși folderul este ro/ase/ie/dma06/data/.
// Nu e o greșeală de tipar: așa e în repo, și la fel stau lucrurile la cele două
// adaptoare, care declară ro.ase.ie.adapters.
//
// De ce compilează: Gradle dă compilatorului lista explicită de fișiere sursă, iar
// javac nu impune ca folderul să coincidă cu pachetul când fișierele sunt date direct.
// Potrivirea folder–pachet contează doar când compilatorul caută o clasă pe classpath.
//
// Consecința practică: importurile folosesc pachetul declarat, nu calea din folder.
//   import ro.ase.ie.data.NumberData;          ← corect, așa e în repo
//   import ro.ase.ie.dma06.data.NumberData;    ← greșit, clasa nu există acolo
//
// La runtime nu se schimbă nimic: ClassLoader încarcă după numele din pachet, nu după
// calea din folder. Folderele sunt doar organizare pe disc.
// ======================================================================================

package ro.ase.ie.data;          // ATENȚIE: pachetul declarat NU conține `dma06`

import java.util.ArrayList;      // implementarea concretă a listei
import java.util.List;           // interfața folosită în semnături

// Două importuri, ambele din java.util. Zero importuri android.*: clasa ar putea rula
// într-un test JUnit obișnuit, fără emulator. Separarea pe pachete nu e cosmetică —
// ea permite testarea sursei fără Android.

// ======================================================================================
// THEORY BLOCK: CLASA UTILITARĂ (UTILITY CLASS)
// ======================================================================================
/*
 * 1. CE ESTE
 *    O clasă care nu are stare și nu are instanțe. Toate metodele sunt `static`, deci
 *    se cheamă pe clasă: `NumberData.getNumbers()`, niciodată `new NumberData().get...`.
 *
 * 2. DE CE CONSTRUCTOR PRIVAT
 *    -   `private NumberData() {}` blochează `new NumberData()` din orice altă clasă.
 *    -   Fără el, compilatorul ar genera un constructor public implicit și oricine ar
 *        putea crea instanțe fără sens.
 *    -   Nu e o eroare să ai instanțe inutile; e zgomot. Iar zgomotul ascunde intenția.
 *    -   Constructorul privat mai blochează și moștenirea: o subclasă ar trebui să cheme
 *        `super()`, care e inaccesibil. De aceea `final` pe clasă e aproape redundant —
 *        dar îl scriem oricum, ca să fie explicit.
 *
 * 3. DE CE METODE STATIC
 *    -   Nu depind de nicio stare a instanței.
 *    -   Se încarcă o singură dată, cu clasa, nu cu fiecare obiect.
 *    -   Pot fi chemate din orice context, inclusiv dintr-un test JUnit fără Android.
 *
 * 4. ALTERNATIVE ȘI DE CE NU SUNT FOLOSITE AICI
 *    -   Singleton: ar impune o instanță partajată. Aici fiecare ecran vrea lista LUI.
 *    -   Interfață cu metode `default`: nu ai ce implementa — nu există contract, există
 *        o singură funcție.
 *    -   Clasă cu constructor public: ar fi permis `new NumberData()`, care nu are sens.
 *
 * 5. REGULA CARE SE VEDE ÎN COD
 *    `final class` + `private constructor` + `static methods` = aceeași combinație ca în
 *    java.lang.Math, java.util.Collections, java.util.Arrays. Nu e un truc de seminar;
 *    e tiparul din JDK.
 *
 * DIAGRAMA:
 *
 *   NumberData                    (clasa; nu se instanțiază niciodată)
 *   ├── FIRST_NUMBER = 1          static final
 *   ├── LAST_NUMBER  = 100        static final
 *   ├── NumberData()              private  ← blochează `new`
 *   └── getNumbers()              static   ← singurul punct de acces
 */

/** The data source shared by all three steps. */
public final class NumberData {  // final: nu poate fi extinsă; o clasă utilitară nu are ce moșteni

    // ==================================================================================
    // BLOCUL 2 — CONSTANTELE
    // ==================================================================================
    // private  — nimeni din afară nu are nevoie de ele
    // static   — aparțin clasei, nu instanței (și oricum nu există instanțe)
    // final    — nu se modifică niciodată; compilatorul poate înlocui valoarea direct
    //
    // De ce două constante și nu 100 scris direct: dacă vrei 1–1000, schimbi o singură
    // linie. Iar bucla devine citibilă: „de la FIRST_NUMBER până la LAST_NUMBER".
    // ==================================================================================
    private static final int FIRST_NUMBER = 1;    // primul număr din listă
    private static final int LAST_NUMBER = 100;   // ultimul număr, INCLUSIV

    // ==================================================================================
    // BLOCUL 3 — CONSTRUCTORUL PRIVAT
    // ==================================================================================
    // Teorie:  blochează instanțierea; clasa are doar metode statice.
    // Logică:  corpul e gol intenționat; comentariul documentează decizia.
    // Risc:    dacă îl scoți, compilatorul generează unul public implicit și `new`
    //          devine legal.
    // Ref:     curs 2 (clase și obiecte).
    // ==================================================================================
    private NumberData() {
        // This class only has static methods
    }

    // De ce constructorul e gol și nu aruncă excepție: unele clase utilitare scriu
    // `throw new AssertionError()` în constructor, ca să prindă apelurile prin reflecție.
    // Aici nu e nevoie: constructorul e privat, iar reflecția nu e un scenariu de laborator.
    //
    // Comentariul din interior — „This class only has static methods" — documentează
    // DE CE e gol. Un constructor privat gol fără explicație arată ca o scăpare.

    // ==================================================================================
    // BLOCUL 4 — getNumbers()
    // ==================================================================================
    // Teorie:  metodă statică ce construiește o colecție; nu atinge nicio stare.
    // Logică:  1. creează ArrayList  2. buclă de la 1 la 100  3. add  4. return
    // Risc:    dacă ai returna o listă partajată (câmp static), modificările dintr-un
    //          ecran ar apărea în toate celelalte.
    // Ref:     capitolul 04 (MainActivity - listă).
    // ==================================================================================
    public static List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();     // 1. listă nouă la fiecare apel
        for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {   // 2. 1..100
            numbers.add(number);                       // 3. autoboxing: int → Integer
        }
        return numbers;                                // 4. 100 de elemente
    }

    // Listă nouă la fiecare apel — asta e esențial. Nu există un câmp static partajat.
    // Fiecare dintre cele trei activități cheamă getNumbers() în onCreate și primește
    // PROPRIA listă. Dacă ar fi un singleton, o modificare făcută într-un ecran ar
    // apărea în toate celelalte, fără să știi de unde vine.
    //
    // List în semnătură, ArrayList în implementare — returnezi interfața, construiești
    // implementarea. Cine primește lista nu depinde de ArrayList; poți schimba în
    // LinkedList fără să atingi nimic altceva. Regula se numește „programează la interfață".
    //
    // new ArrayList<>() cu diamant gol — tipul generic se deduce din context (Java 7+).
    //
    // `<=` și nu `<` — LAST_NUMBER e INCLUSIV. Bucla dă exact 100 de elemente: 1..100.
    // Cu `<` ai avea 99 — și s-ar vedea imediat în listă, pentru că ultimul rând ar fi 99.
    //
    // Autoboxing — numbers.add(number) primește un int, dar lista e List<Integer>.
    // Compilatorul transformă automat în Integer.valueOf(number). Pentru valorile
    // −128…127, Integer.valueOf întoarce instanțe din cache, deci pentru 1–100 nu se
    // creează 100 de obiecte noi.
    //
    // De ce Integer și nu int: genericele Java nu acceptă tipuri primitive. List<int>
    // nu compilează. De aici autoboxing-ul, de aici și Integer în getItem la adaptoare.
    //
    // ==================================================================================
    // CÂND SE ÎNCARCĂ CLASA
    // ==================================================================================
    //
    //   Primul apel NumberData.getNumbers()
    //     → ClassLoader încarcă NumberData
    //     → inițializează câmpurile statice: FIRST_NUMBER = 1, LAST_NUMBER = 100
    //     → abia apoi execută corpul metodei
    //
    // Inițializarea se face o singură dată per proces, nu la fiecare apel. De aceea
    // constantele pot fi citite fără nicio grijă de ordine: sunt gata înainte de prima
    // metodă.
    //
    // ==================================================================================
    // DE CE E UȘOR DE TESTAT
    // ==================================================================================
    //
    //   @Test
    //   public void getNumbers_returnsHundredElements() {
    //       List<Integer> numbers = NumberData.getNumbers();
    //       assertEquals(100, numbers.size());
    //       assertEquals(Integer.valueOf(1), numbers.get(0));
    //       assertEquals(Integer.valueOf(100), numbers.get(99));
    //   }
    //
    // Testul rulează pe JVM, fără emulator, pentru că în fișier nu apare niciun tip
    // android.*. Dacă NumberData ar fi primit un Context ca să citească resurse, testul
    // ar fi avut nevoie de Robolectric sau de un device. Separarea pe pachete nu e
    // cosmetică: ea decide dacă poți testa în 50 de milisecunde sau în 50 de secunde.
}
```

**Ce trebuie să reții:** constructorul privat nu e o formalitate — e singura linie care transformă o clasă oarecare într-o clasă utilitară. Restul (metode statice, `final` pe clasă) o completează.

**Cine cheamă `getNumbers()`:**

| Activitate | Ce face cu lista |
|---|---|
| `SingleColumnActivity` | o dă direct lui `ArrayAdapter` |
| `TwoColumnActivity` | o dă lui `NumberListAdapter` |
| `RecyclerViewActivity` | o dă lui `NumberRecyclerAdapter` |

Aceleași date, trei randări diferite. Asta e tot experimentul. Fiecare activitate cheamă separat, pentru că cele trei ecrane sunt independente: poți deschide treapta 2 direct din meniu, fără să fi deschis treapta 1.

**Costul real:** 300 de `Integer` (3 × 100), toate din cache-ul `Integer.valueOf` pentru 1–100. Practic zero obiecte noi. Dacă ai fi generat 1–10000, cache-ul nu ar mai acoperi și ai fi avut 30000 de obiecte — încă acceptabil, dar nu gratuit.

---

## 28.4 `SingleColumnActivity.java` — treapta 1

Fișierul are 31 de linii, dintre care 18 de cod, și ascunde toată reciclarea în SDK. Treapta 1 nu se învață din cod, se învață din ce *nu* scrie în cod.

```java
/*
 * ======================================================================================
 * FIȘIER: SingleColumnActivity.java
 * ======================================================================================
 * LOCAȚIE:  DMA06/src/main/java/ro/ase/ie/dma06/activities/SingleColumnActivity.java
 * PACHET:   ro.ase.ie.dma06.activities
 * ROL:      treapta 1. Un ListView, un ArrayAdapter, un TextView per rând.
 *           Nu scrie nicio linie de reciclare: ArrayAdapter o face în locul ei.
 *
 * STRUCTURA FIȘIERULUI (2 părți):
 *   1. importuri   — 6 linii
 *   2. onCreate    — 10 linii, dintre care 4 construiesc adapterul
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - `android.R.layout.simple_list_item_1` e un layout din SISTEM, nu din proiect.
 *   - `ArrayAdapter` cheamă `toString()` pe fiecare element. Pentru Integer = numărul.
 *   - `setAdapter` e tot ce trebuie: ListView cere singur getCount și getView.
 * ======================================================================================
 */

// ======================================================================================
// BLOCUL 1 — PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Aici pachetul coincide cu folderul (activities/). Importurile sunt în trei grupuri:
// android.* (framework), androidx.* (bibliotecă împachetată) și ro.ase.* (codul tău).
// Separarea nu e obligatorie pentru compilator, dar face evident ce vine de unde.
// ======================================================================================

package ro.ase.ie.dma06.activities;      // pachetul ecranelor

import android.os.Bundle;                // parametrul lui onCreate
import android.widget.ArrayAdapter;      // adapterul gata făcut din SDK
import android.widget.ListView;          // widget-ul care afișează lista

import androidx.appcompat.app.AppCompatActivity;   // activitatea de bază

import ro.ase.ie.data.NumberData;        // pachetul declarat, nu folderul
import ro.ase.ie.dma06.R;                // resursele aplicației

// ======================================================================================
// THEORY BLOCK: LISTVIEW + ARRAYADAPTER
// ======================================================================================
/*
 * 1. CE FACE LISTVIEW
 *    -   Este un AdapterView: un widget care nu știe ce afișează, dar știe să afișeze.
 *    -   Cere unui Adapter: „câte elemente ai?" (getCount) și „dă-mi rândul pentru
 *        poziția N" (getView).
 *    -   Ține doar rândurile vizibile în arborele de view-uri. Restul nu există.
 *    -   Are un RecycleBin intern: rândurile care ies din ecran sunt păstrate pentru
 *        refolosire, pe tipuri (getItemViewType).
 *
 * 2. CE FACE ARRAYADAPTER
 *    -   Implementează getCount, getItem, getItemId și getView.
 *    -   getView: dacă convertView e null, umflă `resource`; altfel refolosește.
 *    -   Apoi ia elementul de la poziție și îi cheamă `toString()`, pe care îl pune
 *        într-un TextView.
 *    -   Deci: un singur text per rând. Atât.
 *
 * 3. CE TREBUIE SĂ CONȚINĂ `resource`
 *    -   Un TextView. Fie rădăcina însăși (cazul simple_list_item_1), fie un copil
 *        cu id-ul android.R.id.text1.
 *    -   Dacă lipsește, ArrayAdapter aruncă RuntimeException la primul rând:
 *        „You must supply a resource ID for a TextView".
 *
 * 4. UNDE SE OPREȘTE
 *    -   La al doilea TextView. ArrayAdapter nu are unde să pună a doua valoare.
 *    -   La formatare per coloană. toString() dă un singur șir; nu poți alinia
 *        coloana a doua la dreapta cu font monospațiat.
 *    -   La modele fără toString() suprascris: în listă apare Movie@a1b2c3.
 *
 * 5. RECICLAREA E ASCUNSĂ, NU LIPSĂ
 *    -   ArrayAdapter primește `convertView` și îl refolosește, exact ca un adapter
 *        propriu. Doar că tu nu vezi parametrul și nu poți pune un ViewHolder.
 *    -   Pentru un singur TextView, lipsa ViewHolder-ului nu costă: nu ai ce căuta.
 *
 * 6. CE COD SE EXECUTĂ LA FIECARE RÂND
 *    ListView.obtainView(position)
 *      └─ ArrayAdapter.getView(position, convertView, parent)
 *           ├─ convertView == null ?
 *           │     ├─ da  → inflater.inflate(simple_list_item_1, parent, false)
 *           │     └─ nu  → view = convertView
 *           ├─ text = (TextView) view        ← mFieldId == 0, rădăcina e TextView
 *           └─ text.setText(getItem(position).toString())
 *
 * DIAGRAMA:
 *
 *   ListView ──getCount()──▶ ArrayAdapter ──▶ List.size()
 *            ──getView(n)──▶ ArrayAdapter ──▶ convertView? inflate : reuse
 *                                          ──▶ getItem(n).toString()
 *                                          ──▶ textView.setText(...)
 */

/**
 * Step 1: one column.
 * ArrayAdapter is enough because each row shows one text value.
 */
public class SingleColumnActivity extends AppCompatActivity {   // o activitate, fără stare

    // ==================================================================================
    // METODA 1 — onCreate
    // ==================================================================================
    // Teorie:  ciclul de viață; aici se construiește tot ecranul.
    // Logică:  1. super  2. setContentView  3. findViewById  4. construiește adapterul
    //          5. setAdapter
    // Risc:    dacă uiți setAdapter, ecranul rămâne gol, fără nicio eroare.
    // Ref:     capitolul 12 (ListView vs RecyclerView).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);                       // 1. ciclul de viață al părintelui
        setContentView(R.layout.activity_single_column);          // 2. rădăcina layout-ului ESTE ListView-ul

        ListView lvNumbers = findViewById(R.id.lvNumbers);        // 3. singurul view din layout

        // ArrayAdapter calls toString() on each number and shows it in a TextView
        ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
                this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
        //      ↑ Context   ↑ layout din SISTEM            ↑ List<Integer> cu 100 de elemente
        lvNumbers.setAdapter(adapter);                            // 4. leagă lista de widget
    }

    // ArrayAdapter<Integer> — generic-ul trebuie să coincidă cu tipul listei. Lista e
    // List<Integer>, deci adapterul e ArrayAdapter<Integer>. Dacă ai pune
    // ArrayAdapter<String>, ai avea nevoie de List<String> — și ai pierde tipul numeric.
    //
    // new ArrayAdapter<>(...) cu diamant — tipul se deduce din variabila din stânga.
    //
    // `this` ca prim argument — e Context-ul. Adapterul are nevoie de el ca să obțină
    // LayoutInflater-ul cu care umflă rândul. În NumberListAdapter vei vedea exact
    // același lucru, doar că explicit: LayoutInflater.from(context).
    //
    // android.R.layout.simple_list_item_1 — „android." de la început e esențial.
    // R.layout.simple_list_item_1 nu există în proiect; android.R e pachetul de resurse
    // al framework-ului. Fișierul e livrat de sistem, nu de tine.
    //
    // NumberData.getNumbers() ca al treilea argument — se cheamă o singură dată, în
    // onCreate. Rezultatul e o listă de 100 de elemente, ținută de adapter prin
    // referință. Dacă ai chema getNumbers() din nou, ai avea o listă nouă, pe care
    // adapterul nu o vede.
    //
    // lvNumbers.setAdapter(adapter) — ultima linie și cea mai importantă. Înainte de ea,
    // ListView-ul e gol și nu știe că există date. La apel, ListView înregistrează un
    // DataSetObserver pe adapter și cere un layout; abia atunci încep getCount() și getView().
    //
    // Ordinea dintre findViewById și setAdapter nu contează — poți construi adapterul
    // înainte de a găsi lista. Ce contează e ca ambele să se întâmple după setContentView,
    // altfel findViewById întoarce null.
    //
    // ==================================================================================
    // CE FACE ARRAYADAPTER CU convertView
    // ==================================================================================
    //
    //   ArrayAdapter.getView(position, convertView, parent)
    //     ├─ convertView == null ?
    //     │     ├─ da  → view = inflater.inflate(mResource, parent, false)
    //     │     └─ nu  → view = convertView
    //     ├─ mFieldId == 0 ?
    //     │     ├─ da  → text = (TextView) view          ← rădăcina e TextView
    //     │     └─ nu  → text = view.findViewById(mFieldId)
    //     └─ text.setText(getItem(position).toString())
    //
    // Reciclarea e IDENTICĂ cu cea din NumberListAdapter. Diferența e că tu nu vezi
    // parametrul convertView și nu poți atârna un ViewHolder de rând. Pentru un singur
    // TextView, asta nu costă nimic — nu ai ce căuta.
    //
    // ==================================================================================
    // CE SE ÎNTÂMPLĂ DACĂ UIȚI setAdapter
    // ==================================================================================
    //
    //   ListView fără adapter
    //     ├─ getCount() nu e chemată niciodată
    //     ├─ getView() nu e chemată niciodată
    //     ├─ ecranul: alb, fără rânduri
    //     └─ nicio excepție, niciun mesaj în Logcat
    //
    // E aceeași clasă de eroare ca RecyclerView fără LayoutManager: o componentă validă,
    // într-o stare validă, care nu are ce afișa. Nu e un bug al framework-ului; e o
    // configurare incompletă.
    //
    // ==================================================================================
    // DE CE TREI LINII AJUNG AICI ȘI NU AJUNG LA TREAPTA 2
    // ==================================================================================
    //
    //   Treapta 1: 1 coloană  → 1 TextView  → ArrayAdapter știe
    //   Treapta 2: 2 coloane  → 2 TextView  → ArrayAdapter NU știe
    //   Treapta 3: 2 coloane  → 2 TextView  → RecyclerView.Adapter știe
    //
    // Regula nu e „ArrayAdapter e pentru liste simple". Regula e: ArrayAdapter știe
    // EXACT UN text per rând. Atât timp cât rândul tău e un text, e cel mai bun
    // instrument. Când rândul are structură, treci la BaseAdapter.
}
```

### Cele trei argumente ale lui `ArrayAdapter`

```
ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
        this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
```

| Argument | Ce e | De ce |
|---|---|---|
| `this` | `Context` | adapterul are nevoie de el ca să umfle rândul |
| `android.R.layout.simple_list_item_1` | layout **din sistem** | conține un singur `TextView`, cu id-ul `android.R.id.text1` |
| `NumberData.getNumbers()` | `List<Integer>` | datele; adapterul ține **referința**, nu o copie |

**Al doilea argument e un `int`, nu un `View`.** E id-ul resursei de layout, nu layout-ul umflat. `ArrayAdapter` îl umflă singur, o dată per rând nou. De aceea nu vezi niciun `inflate` în activitate.

### `toString()` — ce face și unde se oprește

**Pentru `Integer`:** `Integer.toString(42)` întoarce `"42"`. Metoda e suprascrisă în `Integer` și e echivalentă cu `String.valueOf(int)`. Deci treapta 1 afișează exact numărul zecimal, fără configurare.

**Pentru un model propriu:** dacă ai avea `class Movie { String title; int year; }` fără `toString()` suprascris, în listă ar apărea:

```
ro.ase.ie.model.Movie@a1b2c3d4
```

Asta e `Object.toString()` implicit: numele complet al clasei, `@`, apoi `hashCode()` în hexazecimal. E cea mai frecventă sursă de „de ce arată așa?" la `ArrayAdapter`.

**Unde se oprește, concret, în acest proiect:** ai nevoie de **două** valori per rând — zecimal și binar. `toString()` întoarce **un singur** `String`. Ai putea returna `"42 / 101010"`, dar atunci:

1. n-ai mai avea două `TextView`-uri, deci n-ai putea alinia coloana a doua la dreapta;
2. n-ai putea pune font monospațiat doar pe a doua coloană;
3. n-ai putea da padding diferit celor două coloane;
4. n-ai putea schimba o coloană fără să parsezi string-ul.

**Concluzia:** `toString()` e suficient atât timp cât rândul e **un singur text**. În momentul în care rândul are structură — două coloane, o imagine și un text, un titlu și un subtitlu — ai nevoie de un layout propriu și de un adapter care să îl umple. Aici se termină treapta 1.

**Ce trebuie să reții înainte de treapta 2:** `ArrayAdapter` nu e „prost", e **specializat**. Pentru o listă de nume sau de titluri e exact ce trebuie: o linie de cod, zero `findViewById`, zero `ViewHolder`. Devine nepotrivit doar când rândul are structură. Iar când devine nepotrivit, soluția nu e să-l extinzi și să suprascrii `getView` — ci să cobori la `BaseAdapter`.

---

## 28.5 `activity_single_column.xml` — un singur `ListView`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FIȘIER: activity_single_column.xml
     ==================================================================================
     LOCAȚIE:  DMA06/src/main/res/layout/activity_single_column.xml
     ROL:      layout-ul treptei 1. Un singur element: ListView-ul, ca rădăcină.
     ID-URI:   lvNumbers
     ================================================================================== -->

<!-- Rădăcina layout-ului este ListView-ul însuși: setContentView îl atașează direct.
     Nu e nevoie de un LinearLayout care să îl învelească — treapta 2 are nevoie de
     wrapper pentru că are și antet; treapta 1 nu are. -->
<ListView xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/lvNumbers"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

<!-- ======================================================================================
     ATRIBUTE PE CARE LISTVIEW LE ARE ȘI FIȘIERUL NU LE FOLOSEȘTE
     ======================================================================================
     android:divider="@null"              scoate separatorul dintre rânduri
     android:dividerHeight="1dp"          grosimea separatorului
     android:listSelector="..."           fundalul rândului selectat
     android:choiceMode="singleChoice"    permite selecție cu radio/check
     android:fastScrollEnabled="true"     bara de scroll rapidă, pentru liste lungi
     android:stackFromBottom="true"       liste care cresc de jos (chat)
     android:transcriptMode="normal"      auto-scroll la ultimul element
     android:cacheColorHint="#00000000"   elimină artefactul de scroll (liste vechi)
     ======================================================================================
     Toate sunt atribute ale widget-ului, nu ale adapterului. La RecyclerView niciuna
     nu există: echivalentele lor sunt LayoutManager, ItemDecoration sau cod.
     ====================================================================================== -->

<!-- ======================================================================================
     CE TREBUIE REȚINUT DIN FIȘIER
     ======================================================================================
     rădăcină = ListView      setContentView primește direct lista
     match_parent × 2         lista umple tot ecranul
     fără android:entries     datele vin DOAR din adapter; fără setAdapter = ecran gol
     fără android:divider     separatorul vine din tema implicită a ListView-ului
     fără android:text        un ListView nu are text propriu
     ====================================================================================== -->
```

**Rădăcina e `ListView`** — nu un `LinearLayout` care să-l învelească. `setContentView` primește direct lista, iar `findViewById(R.id.lvNumbers)` o găsește în arborele de view-uri al activității.

**Fără `android:entries`** — lista nu are date din XML. Singura sursă e adapterul. Dacă uiți `setAdapter`, ecranul rămâne gol, fără eroare.

**Fără `android:divider`** — separatorul vine din tema implicită a `ListView`-ului. La `RecyclerView` nu există așa ceva (vezi 28.11, `DividerItemDecoration`).

**De ce un fișier separat pentru un singur tag:** pentru că `setContentView` are nevoie de un layout, iar un layout cu un singur element e perfect valid. Alternativa — `setContentView(new ListView(this))` — ar funcționa, dar ai pierde tot ce ține de temă și de `LayoutParams`, plus că n-ai mai avea id pentru `findViewById`.

---

## 28.6 `NumberListAdapter.java` — treapta 2, adapterul propriu

Acesta e fișierul central al capitolului. Tot ce se știe despre reciclare, `ViewHolder`, `convertView`, `setTag` și `getTag` se vede aici, scris de mână, fără să fie ascuns în SDK.

```java
/*
 * ======================================================================================
 * FIȘIER: NumberListAdapter.java
 * ======================================================================================
 * LOCAȚIE:  DMA06/src/main/java/ro/ase/ie/dma06/adapters/NumberListAdapter.java
 * PACHET:   ro.ase.ie.adapters        ← fără `dma06`, ca și `data`
 * ROL:      adaptează List<Integer> la rândul cu două coloane (item_number.xml),
 *           pentru un ListView. Este echivalentul manual al lui ArrayAdapter.
 *
 * STRUCTURA FIȘIERULUI (4 părți):
 *   1. ViewHolder            — 4 linii: două referințe la TextView
 *   2. câmpuri + constructor — 8 linii: lista și inflater-ul
 *   3. evidență              — 3 metode: getCount, getItem, getItemId
 *   4. getView               — 22 de linii: creare SAU refolosire + umplere
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - BaseAdapter lasă 4 metode abstracte; restul le implementează el.
 *   - `convertView` e rândul reciclat de ListView; `null` = nu există niciunul liber.
 *   - `setTag` / `getTag` lipesc ViewHolder-ul de rând. Fără ele, NPE la primul scroll.
 *   - `findViewById` se cheamă o singură dată per rând, nu la fiecare afișare.
 * ======================================================================================
 */

// ======================================================================================
// BLOCUL 1 — PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Pachetul declarat e ro.ase.ie.adapters, deși folderul e ro/ase/ie/dma06/adapters/.
// Aceeași situație ca la NumberData: compilează, dar importurile trebuie să folosească
// pachetul declarat.
//
// Importurile se împart în trei grupuri:
//   android.*   — framework: Context, LayoutInflater, View, ViewGroup, BaseAdapter, TextView
//   java.util   — List
//   ro.ase.*    — R (resursele)
// ======================================================================================

package ro.ase.ie.adapters;   // pachetul declarat nu conține `dma06`, deși folderul da

import android.content.Context;      // necesar doar pentru LayoutInflater
import android.view.LayoutInflater;  // transformă XML în obiecte View
import android.view.View;            // rândul (umflat sau reciclat)
import android.view.ViewGroup;       // părintele rândului: ListView-ul
import android.widget.BaseAdapter;   // clasa de bază pentru adaptoare proprii
import android.widget.TextView;      // cele două coloane

import java.util.List;               // interfața pentru lista de numere

import ro.ase.ie.dma06.R;            // resursele aplicației

// ======================================================================================
// THEORY BLOCK: BASEADAPTER ȘI TIPARUL VIEWHOLDER
// ======================================================================================
/*
 * 1. CE ESTE BASEADAPTER
 *    -   O clasă abstractă din android.widget care implementează ListAdapter și
 *        SpinnerAdapter.
 *    -   Implementează tot ce ține de observatori, tipuri de view și enabled state:
 *        isEmpty(), areAllItemsEnabled(), isEnabled(int), getItemViewType(int),
 *        getViewTypeCount(), hasStableIds(), registerDataSetObserver().
 *    -   Lasă abstracte EXACT patru metode:
 *          getCount()                                                  câte elemente sunt
 *          getItem(int position)                                       obiectul de la poziție
 *          getItemId(int position)                                     id-ul stabil
 *          getView(int position, View convertView, ViewGroup parent)   rândul
 *
 * 2. CÂND E CHEMATA FIECARE METODĂ
 *    getCount()   — la fiecare layout al listei, la calculul barei de scroll, după
 *                   notifyDataSetChanged. Este prima întrebare pusă vreodată.
 *    getItem()    — NU e chemată de ListView ca să deseneze. E chemată de
 *                   AdapterView.getItemAtPosition(), de performItemClick() și de
 *                   codul tău (inclusiv din getView, ca aici).
 *    getItemId()  — la click (performItemClick primește id-ul), la getSelectedItemId().
 *                   Cu hasStableIds() == true, ListView păstrează selecția între
 *                   reîncărcări.
 *    getView()    — pentru fiecare rând vizibil, la fiecare layout, la fiecare pas de
 *                   scroll, după fiecare notifyDataSetChanged.
 *
 * 3. TIPARUL VIEWHOLDER
 *    Problema: findViewById parcurge arborele. Pe un rând cu 2 view-uri e ieftin;
 *    pe 10 rânduri × 2 view-uri × fiecare scroll, începe să conteze.
 *    Soluția: cauți o singură dată, la crearea rândului, și lipești rezultatul de rând
 *    cu setTag(). La refolosire, îl iei înapoi cu getTag().
 *
 *    Fără holder:                          Cu holder:
 *    ┌──────────────────────────┐          ┌──────────────────────────┐
 *    │ rând (View)              │          │ rând (View)              │
 *    │  ├─ tvDecimal            │          │  ├─ tvDecimal            │
 *    │  └─ tvBinary             │          │  ├─ tvBinary             │
 *    │  (căutate la fiecare     │          │  └─ tag → ViewHolder     │
 *    │   afișare)               │          │      ├─ tvDecimal ───────┘
 *    └──────────────────────────┘          │      └─ tvBinary
 *                                          └──────────────────────────┘
 *
 * 4. DE CE `static`
 *    O clasă interioară non-statică ține o referință implicită la instanța exterioară
 *    (`this$0`). ViewHolder-ul e atașat de un View, iar View-ul poate trăi mai mult
 *    decât adapterul (ListView îl ține în RecycleBin). `static` elimină referința.
 *    În plus, un holder non-static nu poate fi construit fără un adapter — ceea ce
 *    încurcă orice test.
 *
 * 5. CICLUL UNUI RÂND
 *    creare:     inflate → findViewById × 2 → new ViewHolder → setTag → umplere
 *    refolosire: getTag → umplere
 *    ieșire:     rândul intră în RecycleBin, cu tag-ul lui cu tot
 *
 * 6. GRAFUL DE OBIECTE
 *
 *    TwoColumnActivity
 *      └── NumberListAdapter            (câmp local; trăiește cât activitatea)
 *            ├── List<Integer>          (REFERINȚĂ la lista din NumberData)
 *            │     └── 100 × Integer
 *            ├── LayoutInflater         (unul singur, refolosit)
 *            └── getView() creează:
 *                  ViewHolder           (lipit de rând cu setTag)
 *                    ├── tvDecimal ──┐
 *                    └── tvBinary  ──┤
 *                                    ▼
 *                  View (LinearLayout-ul din item_number.xml)
 *                    ├── TextView tvDecimal
 *                    └── TextView tvBinary
 *
 *    Săgețile merg într-un singur sens: activitatea ține adapterul, adapterul ține
 *    lista și creează holder-e, holder-ul ține view-urile. Nicio săgeată nu se
 *    întoarce — de aceea holder-ul poate fi `static`.
 */

/** Step 2: fills a two-column row for a ListView. */
public class NumberListAdapter extends BaseAdapter {   // extinde scheletul, nu ArrayAdapter

    // ==================================================================================
    // BLOCUL 2 — CLASA INTERIOARĂ ViewHolder
    // ==================================================================================
    // Teorie:  cutia care ține referințele la view-urile rândului, ca să nu le mai cauți.
    // Logică:  două câmpuri, atât. Nu are metode, nu are logică, nu are constructor.
    // Risc:    dacă nu e `static`, ține o referință la adapter (`this$0`) și prelungește
    //          viața acestuia cât timp rândul e în RecycleBin.
    // Ref:     curs 4 (ListView și adaptoare).
    // ==================================================================================
    private static class ViewHolder {
        TextView tvDecimal;   // referința la coloana 1
        TextView tvBinary;    // referința la coloana 2
    }

    // De ce e o clasă interioară: cele două TextView-uri trebuie să călătorească
    // împreună. Un holder e o cutie cu două referințe, atârnată de rând cu setTag.
    // Fără el, ai avea două variabile separate și niciun loc unde să le păstrezi
    // între apeluri.
    //
    // De ce `private`: doar acest adapter îl folosește. Nu apare în nicio semnătură
    // publică. (La NumberRecyclerAdapter e `static class` fără private, pentru că
    // tipul apare în semnătura publică a adapterului.)
    //
    // De ce câmpurile NU sunt `final`: sunt atribuite DUPĂ `new ViewHolder()`, în
    // getView. Nu pot fi final pentru că nu sunt inițializate în constructor. Exact
    // asta repară versiunea RecyclerView: mută findViewById în constructorul
    // holder-ului și le poate face final.

    // ==================================================================================
    // BLOCUL 3 — CÂMPURILE ȘI CONSTRUCTORUL
    // ==================================================================================
    // Teorie:  două referințe finale: lista și inflater-ul.
    // Logică:  ambele se stabilesc o singură dată, în constructor.
    // Risc:    dacă ai copia lista (`new ArrayList<>(numbers)`), ai avea două liste și
    //          modificările din afară nu s-ar mai vedea.
    // Ref:     capitolul 12.
    // ==================================================================================
    private final List<Integer> numbers;          // sursa de date, ținută prin referință
    private final LayoutInflater layoutInflater;  // un singur inflater, refolosit

    public NumberListAdapter(Context context, List<Integer> numbers) {
        this.layoutInflater = LayoutInflater.from(context);  // îl obținem o dată, nu la fiecare rând
        this.numbers = numbers;                              // NU copiem lista
    }

    // `private final List<Integer> numbers` — referința nu se schimbă niciodată.
    // Conținutul listei s-ar putea schimba, dar adapterul arată mereu spre aceeași listă.
    //
    // `private final LayoutInflater layoutInflater` — LayoutInflater.from(context) face
    // o căutare internă. O facem O DATĂ, în constructor, nu la fiecare rând. În plus,
    // getView nu mai are nevoie de Context.
    //
    // `this.numbers = numbers` — nu se copiază lista. Adapterul primește referința la
    // lista construită de NumberData. Dacă ai modifica lista din afară, adapterul ar
    // vedea modificarea — dar nu ar redesena nimic fără notifyDataSetChanged().
    //
    // De ce constructorul nu validează nimic: nu are ce. `context` null ar crăpa oricum
    // la LayoutInflater.from, iar o listă null ar crăpa la primul getCount().

    // ==================================================================================
    // BLOCUL 4 — CELE TREI METODE DE EVIDENȚĂ
    // ==================================================================================
    // Trei metode scurte, fiecare răspunde la o întrebare a lui ListView. Niciuna nu
    // desenează nimic.
    // ==================================================================================

    // ----------------------------------------------------------------------------------
    // METODA 1 — getCount
    // ----------------------------------------------------------------------------------
    // Teorie:  prima întrebare a lui ListView: câte rânduri există?
    // Logică:  dimensiunea listei.
    // Risc:    dacă întorci 0, lista e goală; dacă întorci mai mult decât size(),
    //          getView ajunge la o poziție invalidă → IndexOutOfBoundsException.
    // Ref:     capitolul 12.
    // ----------------------------------------------------------------------------------
    @Override
    public int getCount() {
        return numbers.size();      // câte rânduri: exact elementele listei
    }

    // ----------------------------------------------------------------------------------
    // METODA 2 — getItem
    // ----------------------------------------------------------------------------------
    // Teorie:  obiectul de la poziția dată. NU e chemată de ListView pentru desenare.
    // Logică:  numbers.get(position), cu verificarea de bounds făcută de ArrayList.
    // Risc:    poziție invalidă → IndexOutOfBoundsException; element null → NPE la
    //          unboxing în getView.
    // Ref:     capitolul 12.
    // ----------------------------------------------------------------------------------
    @Override
    public Integer getItem(int position) {
        return numbers.get(position);   // obiectul de la poziția dată
    }

    // ----------------------------------------------------------------------------------
    // METODA 3 — getItemId
    // ----------------------------------------------------------------------------------
    // Teorie:  identitatea stabilă a elementului, folosită la click și la selecție.
    // Logică:  numerele sunt unice, deci numărul însuși e un id valid.
    // Risc:    într-o listă cu duplicate, două rânduri ar avea același id și selecția
    //          ar sări între ele.
    // Ref:     capitolul 12.
    // ----------------------------------------------------------------------------------
    @Override
    public long getItemId(int position) {
        // Each number is unique, so the number itself can be the ID
        return numbers.get(position);   // Integer → int → long (widening)
    }

    // getCount() — primul lucru pe care îl întreabă ListView. Determină câte rânduri
    // există și cât de lungă e bara de scroll. Dacă întorci 0, lista e goală.
    //
    // getItem(position) — obiectul de la poziția dată. ListView îl cheamă când cineva
    // cere elementul de la o poziție (getItemAtPosition), iar adapterul îl cheamă
    // singur în getView.
    //
    // getItemId(position) — identitatea elementului. numbers.get(position) întoarce
    // Integer, care se unboxează la int și apoi se extinde la long (widening,
    // conversie implicită sigură). Pentru că numerele 1–100 sunt unice, numărul
    // însuși e un ID valid. Într-o listă cu duplicate (două filme cu același titlu)
    // ai avea nevoie de un câmp id separat.
    //
    // Când e folosit getItemId: ListView îl cheamă când construiește argumentele unui
    // click. Identitatea stabilă (hasStableIds() == true) ar permite widget-ului să
    // păstreze selecția între reîncărcări; aici e false implicit, dar metoda trebuie
    // oricum implementată — e abstractă în BaseAdapter.
    //
    // @Override pe toate trei — metodele vin din Adapter / BaseAdapter. Fără adnotare
    // ar fi tot override, dar compilatorul nu ți-ar semnala o semnătură greșită.
    //
    // De ce getItem întoarce Integer și nu int: semnătura din Adapter e
    // `Object getItem(int)`. NumberListAdapter o restrânge la Integer — allowed,
    // pentru că Integer e subtip al lui Object (return type covariance). Câștigul:
    // getView nu mai are nevoie de cast.
    //
    // TABELUL CELOR PATRU METODE:
    //
    //   Metodă          Cine o cheamă                        Când
    //   getCount()      ListView.onMeasure/layoutChildren    la fiecare layout
    //   getItem(int)    AdapterView.getItemAtPosition        la cerere / din getView
    //   getItemId(int)  AdapterView.getSelectedItemId        la click / selecție
    //   getView(...)    AbsListView.obtainView               pentru fiecare rând vizibil

    // ==================================================================================
    // BLOCUL 5 — getView, INIMA ADAPTERULUI
    // ==================================================================================
    // Teorie:  singura metodă care produce un View. Are două ramuri: creare și refolosire.
    // Logică:  1. dacă convertView e null → inflate + findViewById + setTag
    //          2. altfel → getTag
    //          3. umple ambele TextView-uri
    //          4. returnează convertView
    // Risc:    fără setTag, getTag întoarce null și prima linie care atinge holder-ul
    //          dă NullPointerException. Lista merge până la primul scroll.
    // Ref:     capitolul 12 (secțiunea despre reciclare).
    // ==================================================================================
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;                       // declarat înainte de if, folosit după

        if (convertView == null) {
            // New row: inflate it and store its views
            convertView = layoutInflater.inflate(R.layout.item_number, parent, false);
            holder = new ViewHolder();                                      // cutia goală
            holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);    // căutare 1
            holder.tvBinary = convertView.findViewById(R.id.tvBinary);      // căutare 2
            convertView.setTag(holder);                                     // lipește cutia de rând
        } else {
            // Reused row: get its stored views
            holder = (ViewHolder) convertView.getTag();                     // ia cutia înapoi
        }

        int number = getItem(position);                                     // Integer → int
        holder.tvDecimal.setText(String.valueOf(number));                   // coloana 1: „42"
        holder.tvBinary.setText(Integer.toBinaryString(number));            // coloana 2: „101010"

        return convertView;                                                 // ACELAȘI rând, umplut
    }

    // ----------------------------------------------------------------------------------
    // SEMNĂTURA — ce înseamnă fiecare parametru
    // ----------------------------------------------------------------------------------
    //
    //   position      al câtelea rând din listă (0…99). NU e poziția pe ecran.
    //                 La primul ecran: 0…9. După scroll: 10, 11, …
    //   convertView   un rând RECICLAT de ListView, sau null dacă nu există niciunul
    //                 liber. E un View, nu un ViewHolder — de aici setTag/getTag.
    //   parent        ListView-ul care cere rândul. Nu îl adaugi tu în arbore;
    //                 ListView o face după ce getView întoarce. Îți trebuie doar
    //                 pentru inflate, ca să se calculeze LayoutParams-ul corect.
    //
    // ----------------------------------------------------------------------------------
    // CELE DOUĂ RAMURI
    // ----------------------------------------------------------------------------------
    //
    //   convertView == null   →  rând NOU:       inflate + findViewById + setTag
    //   convertView != null   →  rând REFOLOSIT: getTag, fără nicio căutare
    //
    // La pornire, ListView cere primele ~10 rânduri cu convertView == null — nu are
    // ce recicla. Apoi, la fiecare scroll, rândul care iese din ecran intră în
    // RecycleBin și e dat înapoi la următorul apel:
    //
    //   getView(0,  null, listView)    → null → inflate + findViewById + setTag
    //   getView(1,  null, listView)    → null → inflate + findViewById + setTag
    //   ...
    //   getView(9,  null, listView)    → null → inflate + findViewById + setTag
    //         ── derulezi o poziție ──
    //   getView(10, rândul0, listView) → != null → getTag + setText
    //
    // De ce primele apeluri au convertView == null: pentru că RecycleBin-ul e gol.
    // Nu există niciun rând care să fi ieșit din ecran, pentru că nu ai derulat încă.
    //
    // De ce getView(10, rândul0, ...) și nu getView(10, rândul9, ...): ListView ia
    // rândul din capul listei de reciclare, nu neapărat ultimul ieșit. Ordinea exactă
    // ține de implementarea RecycleBin; pentru tine contează doar că UN rând reciclat
    // vine, nu care anume.
    //
    // ----------------------------------------------------------------------------------
    // convertView == null / setTag / getTag, PAS CU PAS
    // ----------------------------------------------------------------------------------
    //
    // PASUL 1 — primul apel, convertView == null:
    //
    //   ListView nu are niciun rând liber
    //     → getView(0, null, parent)
    //         convertView = layoutInflater.inflate(item_number, parent, false)
    //             ├─ creează LinearLayout-ul din XML
    //             ├─ creează cele două TextView-uri
    //             └─ NU îl atașează de parent (al treilea argument = false)
    //         holder = new ViewHolder()                    ← obiect gol, două câmpuri null
    //         holder.tvDecimal = convertView.findViewById(R.id.tvDecimal)
    //         holder.tvBinary  = convertView.findViewById(R.id.tvBinary)
    //         convertView.setTag(holder)                   ← rândul ține acum holder-ul
    //         setText × 2
    //         return convertView
    //
    // PASUL 2 — al doilea apel pentru același rând, după scroll:
    //
    //   rândul 0 iese din ecran
    //     → ListView îl scoate din arbore și îl pune în RecycleBin
    //     → getView(10, rândul0, parent)
    //         convertView = rândul0                        ← NU e null
    //         holder = (ViewHolder) convertView.getTag()   ← exact holder-ul de la pasul 1
    //         setText × 2                                  ← doar textul se schimbă
    //         return convertView
    //
    // PASUL 3 — ce se întâmplă cu tag-ul la reciclare: nimic. setTag nu e resetat de
    // ListView, nu e atins de removeView, nu e curățat de RecycleBin. Rândul pleacă
    // în pool cu holder-ul lipit și se întoarce cu el. De aceea funcționează: tag-ul
    // e al rândului, nu al poziției.
    //
    // Ce conține holder-ul între apeluri: aceleași două referințe la aceleași
    // TextView-uri. Rândul nu se reconstruiește, deci nici view-urile nu se schimbă.
    // Se schimbă doar textul din ele.
    //
    // De ce setTag e chemat doar pe ramura null: pentru că doar acolo se creează
    // holder-ul. Pe ramura else, holder-ul există deja, lipit de rând. Dacă ai chema
    // setTag și pe else, ai crea un holder nou la fiecare afișare — exact ce
    // încercai să eviți.
    //
    // ----------------------------------------------------------------------------------
    // DANGER! — exact NPE-ul când lipsește setTag
    // ----------------------------------------------------------------------------------
    //
    // Dacă scoți linia `convertView.setTag(holder);`, codul compilează. Lista se
    // afișează corect la pornire — primele 10 rânduri trec prin ramura null, unde
    // holder-ul e construit local. La primul scroll, însă:
    //
    //   holder = (ViewHolder) convertView.getTag();   // getTag() → null
    //                                                 // cast-ul (ViewHolder) null → null
    //   ...
    //   holder.tvDecimal.setText(...);                // ← aici crapă
    //
    // De ce cast-ul nu aruncă: un cast aplicat lui null întoarce null. (ViewHolder) null
    // e legal. ClassCastException apare doar când obiectul există și nu e de tipul
    // cerut. De aceea excepția nu vine de la linia cu cast, ci de la prima linie care
    // ATINGE holder-ul.
    //
    // Excepția exactă, pe ART:
    //
    //   java.lang.NullPointerException: Attempt to read from field
    //   'android.widget.TextView ro.ase.ie.adapters.NumberListAdapter$ViewHolder.tvDecimal'
    //   on a null object reference
    //       at ro.ase.ie.adapters.NumberListAdapter.getView(NumberListAdapter.java:47)
    //
    // De ce „read from field" și nu „invoke virtual method": pentru că prima operație
    // e citirea câmpului holder.tvDecimal, nu apelul setText. Dacă holder-ul ar
    // exista, dar tvDecimal ar fi null (de exemplu ai uitat un findViewById), atunci
    // ai primi varianta cu metoda:
    //
    //   java.lang.NullPointerException: Attempt to invoke virtual method
    //   'void android.widget.TextView.setText(java.lang.CharSequence)'
    //   on a null object reference
    //
    // Varianta cu tag greșit: dacă ai pune convertView.setTag("rând"), cast-ul ar
    // arunca imediat:
    //
    //   java.lang.ClassCastException: java.lang.String cannot be cast to
    //   ro.ase.ie.adapters.NumberListAdapter$ViewHolder
    //       at ro.ase.ie.adapters.NumberListAdapter.getView(NumberListAdapter.java:44)
    //
    // Fără setTag: lista funcționează până la primul scroll. Apoi crapă cu
    // NullPointerException. E cea mai frecventă greșeală la ListView cu adapter
    // propriu — și singura care trece de compilare, de primul ecran și de demo-ul
    // făcut fără să derulezi.
    //
    // Cum o depanezi în 30 de secunde: dacă lista se vede corect la deschidere și
    // crapă la scroll, e aproape sigur setTag lipsă sau pus pe ramura greșită.
    //
    // ----------------------------------------------------------------------------------
    // inflate — de ce (layout, parent, false)
    // ----------------------------------------------------------------------------------
    //
    // De ce parent: ca să se genereze LayoutParams-ul corect pentru rând. Fără el,
    // inflate nu știe ce parametri să creeze, iar match_parent din XML nu se poate
    // interpreta. LayoutParams e clasa care spune părintelui cum să așeze copilul;
    // LinearLayout are LinearLayout.LayoutParams, ListView are AbsListView.LayoutParams.
    //
    // De ce false: înseamnă NU atașa acum. ListView va atașa rândul când îi vine
    // rândul. Cu true, inflate ar returna PĂRINTELE, nu rândul — și ai primi un
    // ListView în loc de un rând, cu ClassCastException la findViewById.
    //
    // Ce se întâmplă dacă pui null în loc de parent: inflate nu are de unde lua
    // LayoutParams-ul, deci rândul primește LayoutParams implicite. Pe un rând cu
    // match_parent înălțime, rezultatul ar fi un rând de înălțime zero sau greșită.
    // Se vede imediat: rândurile se suprapun sau dispar.
    //
    // findViewById de două ori — doar pe rândul nou. Căutarea parcurge arborele de
    // view-uri; pe un rând cu două TextView-uri e ieftină, dar înmulțită cu 100 de
    // rânduri și cu fiecare scroll devine vizibilă.
    //
    // setTag(holder) — View.setTag(Object) e un câmp liber pe orice View. Nu are
    // legătură cu afișarea; e doar un loc unde atârni un obiect. Aici lipim
    // holder-ul de rândul lui.
    //
    // getTag() — întoarce Object, deci e nevoie de cast. Cast-ul NU e verificat de
    // compilator: dacă ai pus altceva în tag, ClassCastException la runtime; dacă
    // ai uitat setTag, getTag() întoarce null și primești NullPointerException la
    // prima linie care atinge holder-ul.
    //
    // ----------------------------------------------------------------------------------
    // PARTEA DE UMPLERE
    // ----------------------------------------------------------------------------------
    //
    //   int number = getItem(position);                    // Integer → int (unboxing)
    //   holder.tvDecimal.setText(String.valueOf(number));  // „42"
    //   holder.tvBinary.setText(Integer.toBinaryString(number));  // „101010"
    //
    // int number = getItem(position) — getItem întoarce Integer, atribuirea îl
    // unboxează. Dacă lista ar conține null, aici ai avea NullPointerException.
    // Aici nu se întâmplă: NumberData produce 1–100.
    //
    // String.valueOf(number) — echivalent cu Integer.toString(number). Mai explicit
    // decât number + "", care creează un StringBuilder în plus.
    //
    // Integer.toBinaryString(number) — reprezentarea binară fără zerouri inițiale și
    // fără prefix: 1 → "1", 100 → "1100100". De aceea coloana a doua nu e aliniată
    // frumos la stânga, iar item_number.xml o aliniază la dreapta și îi pune font
    // monospațiat.
    //
    // return convertView — întoarce exact rândul primit, acum umplut. Nu construiești
    // un View nou la fiecare apel; asta e toată economia.
    //
    // De ce nu return holder.tvDecimal sau altceva: ListView are nevoie de rândul
    // întreg, nu de un copil. Rândul e LinearLayout-ul cu două TextView-uri.
    //
    // ----------------------------------------------------------------------------------
    // CICLUL DE RECICLARE, CU CE ȚINE convertView ÎN FIECARE MOMENT
    // ----------------------------------------------------------------------------------
    //
    //   ECRAN (10 rânduri vizibile)                RecycleBin (pool-ul ListView-ului)
    //   ┌───────────────────────────────┐
    //   │ rând 0   poziția 0   tag=H0   │
    //   │ rând 1   poziția 1   tag=H1   │
    //   │ rând 2   poziția 2   tag=H2   │
    //   │ ...                           │
    //   │ rând 9   poziția 9   tag=H9   │
    //   └───────────────────────────────┘
    //
    //   ① DERULEZI SUS cu un rând
    //      rând 0 iese pe sus
    //        → ListView.removeView(rând0)
    //        → RecycleBin.add(rând0)          ← rând0 păstrează tag=H0
    //      ListView cere rândul pentru poziția 10:
    //        getView(10, rând0, parent)
    //          convertView = rând0             ← obiect View, NU null
    //          getTag()    = H0                ← holder-ul creat la poziția 0
    //          H0.tvDecimal.setText("11")
    //          H0.tvBinary.setText("1011")
    //          return rând0
    //
    //   ② ECRANUL ARATĂ ACUM
    //   ┌───────────────────────────────┐
    //   │ rând 1   poziția 1   tag=H1   │
    //   │ rând 2   poziția 2   tag=H2   │
    //   │ ...                           │
    //   │ rând 9   poziția 9   tag=H9   │
    //   │ rând 0   poziția 10  tag=H0   │   ← același View, alt text
    //   └───────────────────────────────┘
    //
    //   ③ DERULEZI JOS înapoi
    //      rând 0 iese pe jos → RecycleBin
    //      getView(0, rând0, parent)
    //          getTag() = H0
    //          setText("1"), setText("1")   ← se rescrie ce era la început
    //
    // Ce trebuie să reții din diagramă: convertView nu e „un rând oarecare", e un
    // obiect View anume, cu tag-ul lui. Poziția nu călătorește cu rândul; textul da.
    // De aceea setText se face ÎNTOTDEAUNA, pe ambele ramuri — dacă ai sări peste
    // umplere pe ramura else, rândul ar afișa textul vechi.
    //
    // Câte rânduri există în total: aproximativ atâtea câte încap pe ecran, plus
    // unul-doi în buffer. Nu 100. Ăsta e tot câștigul: 10 obiecte View în loc de 100,
    // indiferent cât derulezi.
    //
    // Când se golește pool-ul: la setAdapter cu un adapter nou, la notifyDataSetChanged
    // (parțial), la distrugerea ListView-ului. Nu se golește la scroll — de asta
    // funcționează.
    //
    // ----------------------------------------------------------------------------------
    // CE S-AR ÎNTÂMPLA DACĂ AI IGNORA RECICLAREA
    // ----------------------------------------------------------------------------------
    //
    // Varianta greșită, pentru comparație — NU e în repo:
    //
    //   View row = layoutInflater.inflate(R.layout.item_number, parent, false);
    //   // ... findViewById, setText ...
    //   return row;
    //
    // -   100 de rânduri umflate pentru 100 de elemente, deși pe ecran încap ~10;
    // -   memoria crește cu fiecare scroll, pentru că fiecare rând rămas în arbore
    //     ține un View și două TextView;
    // -   ListView nu mai are ce recicla, deci nici convertView nu mai vine;
    // -   scroll-ul devine sacadat, pentru că fiecare cadru umflă XML.
    //
    // Codul ar fi CORECT — ar afișa aceleași numere — dar ar fi lent. Reciclarea e
    // optimizare, nu corectitudine. La 100 de rânduri diferența e mică; la 10.000
    // de rânduri e diferența dintre o aplicație care merge și una care nu.
    //
    // Cât costă inflate: parsarea XML-ului e cache-uită de Resources, dar construirea
    // obiectelor View nu. Pentru un rând cu două TextView-uri, vorbim de microsecunde.
    // Înmulțit cu 100 de rânduri și cu fiecare cadru de scroll, ajunge la milisecunde —
    // exact bugetul unui cadru de 60fps (16 ms).
    //
    // ==================================================================================
    // CE SE ÎNTÂMPLĂ DACĂ UIȚI UN findViewById
    // ==================================================================================
    //
    //   holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);
    //   // holder.tvBinary lipsește
    //
    // Compilează. Lista se afișează. Coloana a doua e goală pe toate rândurile. La
    // umplere:
    //
    //   holder.tvBinary.setText(...)   →  NullPointerException:
    //     Attempt to invoke virtual method 'void android.widget.TextView.setText(...)'
    //     on a null object reference
    //
    // Diferența față de lipsa lui setTag: acolo holder-ul e null, aici holder-ul există,
    // dar un câmp al lui e null. Mesajul o spune: „invoke virtual method ... on a null
    // object reference" înseamnă că receptorul apelului e null, adică tvBinary.
    //
    // ==================================================================================
    // DE CE NU SE POT PUNE DATE ÎN HOLDER
    // ==================================================================================
    //
    // Ai putea fi tentat să scrii:
    //
    //   holder.number = getItem(position);   // ← greșit
    //
    // și să citești valoarea la click. Nu funcționează, pentru că holder-ul e REFOLOSIT:
    // între bind și click, rândul poate fi reciclat pentru altă poziție, iar valoarea
    // din holder ar fi a altui element. Holder-ul ține VIEW-URI, nu date. Datele se
    // pun în view-uri (setText), nu în holder.
    //
    // ==================================================================================
    // CUM SE COMPARĂ CU ARRAYADAPTER
    // ==================================================================================
    //
    //   ArrayAdapter                      NumberListAdapter
    //   ├── getCount() → size()           ├── getCount() → size()
    //   ├── getItem() → list.get()        ├── getItem() → list.get()
    //   ├── getItemId() → poziția         ├── getItemId() → numărul
    //   └── getView()                     └── getView()
    //         ├── inflate / reuse               ├── if (convertView == null)
    //         ├── findViewById(text1)           │     ├── inflate
    //         └── setText(toString())           │     ├── new ViewHolder
    //                                           │     ├── findViewById × 2
    //                                           │     └── setTag
    //                                           ├── else getTag
    //                                           └── setText × 2
    //
    // Aceleași patru metode, aceeași structură. Diferența e că a doua variantă îți dă
    // acces la convertView și la layout-ul rândului. Tot ce câștigi e control; tot ce
    // plătești e cod.
    //
    // ==================================================================================
    // GREȘELI FRECVENTE, ÎN ORDINEA FRECVENȚEI
    // ==================================================================================
    //
    //   1. Lipsește setTag → NPE la primul scroll.
    //   2. setTag pus pe ramura else → se creează un holder nou la fiecare afișare;
    //      nu crapă, dar pierzi toată economia.
    //   3. findViewById chemat la fiecare apel, în afara if-ului → funcționează, dar
    //      căutarea se face de 100 de ori mai des decât trebuie.
    //   4. inflate cu `true` în loc de `false` → ClassCastException sau rânduri lipite.
    //   5. getCount() întoarce numbers.size() + 1 → IndexOutOfBoundsException la ultimul.
    //   6. return holder.tvDecimal în loc de convertView → ListView primește un TextView
    //      în loc de rândul întreg; coloana a doua dispare.
}
```

**Ce trebuie să reții din fișierul ăsta:** cele patru metode ale lui `BaseAdapter` sunt un contract, nu o sugestie. `getCount` și `getView` sunt singurele chemate pentru desenare; `getItem` și `getItemId` sunt pentru click și pentru codul tău. Iar `setTag` / `getTag` sunt puntea dintre rândul reciclat și holder-ul lui.

**De ce `BaseAdapter` și nu `ArrayAdapter`:** `ArrayAdapter` e o implementare completă, gata făcută, pentru un singur text. `BaseAdapter` e scheletul: implementează interfețele `ListAdapter` și `SpinnerAdapter`, dar lasă **patru metode abstracte** — `getCount`, `getItem`, `getItemId`, `getView`. Tu scrii exact ce lipsește.

**De ce nu extinzi `ArrayAdapter` și suprascrii `getView`:** ai putea. Dar ai moșteni un constructor care cere un `resource` cu `text1`, un `mFieldId` pe care nu îl folosești și un `getFilter()` care nu are sens. `BaseAdapter` îți dă exact cele patru metode, fără bagaj.

---

## 28.7 `TwoColumnActivity.java` — treapta 2, ecranul

Fișierul e aproape identic cu treapta 1. Lecția se vede cel mai bine punându-le alături: șapte linii identice, o singură clasă diferită.

```java
/*
 * ======================================================================================
 * FIȘIER: TwoColumnActivity.java
 * ======================================================================================
 * LOCAȚIE:  DMA06/src/main/java/ro/ase/ie/dma06/activities/TwoColumnActivity.java
 * PACHET:   ro.ase.ie.dma06.activities
 * ROL:      treapta 2. Același ListView ca treapta 1, dar cu un adapter propriu care
 *           umple două coloane.
 *
 * STRUCTURA FIȘIERULUI (2 părți):
 *   1. importuri   — 7 linii
 *   2. onCreate    — 8 linii: layout, findViewById, adapter, setAdapter
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - Id-ul `lvNumbers` e ACELAȘI ca în treapta 1, dar în alt layout. Nu e conflict.
 *   - Activitatea nu știe ce e într-un rând: nu atinge tvDecimal / tvBinary.
 *   - Diferența față de treapta 1 e o singură clasă: NumberListAdapter.
 * ======================================================================================
 */

// ======================================================================================
// BLOCUL 1 — PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Față de SingleColumnActivity, importul `android.widget.ArrayAdapter` a dispărut și
// a apărut `ro.ase.ie.adapters.NumberListAdapter`. Restul e identic.
// ======================================================================================

package ro.ase.ie.dma06.activities;      // pachetul ecranelor

import android.os.Bundle;                // parametrul lui onCreate
import android.widget.ListView;          // ACELAȘI widget ca treapta 1

import androidx.appcompat.app.AppCompatActivity;

import ro.ase.ie.adapters.NumberListAdapter;   // adapterul propriu, din pachetul `adapters`
import ro.ase.ie.data.NumberData;             // aceleași date ca la treapta 1
import ro.ase.ie.dma06.R;

// ======================================================================================
// THEORY BLOCK: DE LA ARRAYADAPTER LA BASEADAPTER
// ======================================================================================
/*
 * 1. CE RĂMÂNE IDENTIC
 *    -   Widget-ul: ListView.
 *    -   Datele: NumberData.getNumbers().
 *    -   Ciclul: onCreate → setContentView → findViewById → new Adapter → setAdapter.
 *    -   Reciclarea: tot ListView o face; doar că acum o scrii tu.
 *
 * 2. CE SE SCHIMBĂ
 *    -   Adapterul: ArrayAdapter (SDK) → NumberListAdapter (al tău).
 *    -   Layout-ul rândului: android.R.layout.simple_list_item_1 → item_number.xml.
 *    -   Numărul de coloane: 1 → 2.
 *    -   Cine cheamă findViewById: SDK-ul → codul tău, o dată per rând.
 *
 * 3. CE TREBUIE SĂ FACĂ ACTIVITATEA ÎN PLUS
 *    -   Nimic, în afară de a pasa `this` (Context) adapterului propriu.
 *    -   ArrayAdapter lua Context-ul prin constructor; NumberListAdapter la fel.
 *    -   Deci diferența se vede doar în tipul variabilei.
 *
 * 4. CE NU TREBUIE SĂ FACĂ ACTIVITATEA
 *    -   Să cunoască id-urile din rând (tvDecimal, tvBinary).
 *    -   Să știe câte coloane are rândul.
 *    -   Să atingă convertView, ViewHolder sau reciclarea.
 *    Orice astfel de linie ar fi o scurgere de responsabilitate: activitatea ar trebui
 *    schimbată când se schimbă rândul.
 *
 * DIAGRAMA RESPONSABILITĂȚILOR:
 *
 *   TwoColumnActivity                 NumberListAdapter
 *   ├── setContentView(layout)        ├── getCount()   → 100
 *   ├── findViewById(lvNumbers)       ├── getItem(n)
 *   ├── new NumberListAdapter(        ├── getItemId(n)
 *   │       this,                     └── getView(n, convertView, parent)
 *   │       NumberData.getNumbers())        ├── inflate / getTag
 *   └── setAdapter(adapter)                 ├── findViewById × 2
 *                                           └── setText × 2
 *
 * 5. DE CE ID-URILE NU SE CIOCNESC
 *    R.id.lvNumbers e o singură constantă int, generată o dată pentru toate layout-urile.
 *    Valoarea e aceeași, iar findViewById o caută în arborele atașat activității
 *    curente. Dacă ai avea două ListView-uri cu același id ÎN ACELAȘI layout, primul
 *    găsit ar fi returnat — și al doilea ar fi inaccesibil.
 */

/**
 * Step 2: two columns in a ListView.
 * A custom adapter fills each column of the row layout.
 */
public class TwoColumnActivity extends AppCompatActivity {

    // ==================================================================================
    // METODA 1 — onCreate
    // ==================================================================================
    // Teorie:  același ciclu de viață; se schimbă doar clasa adapterului.
    // Logică:  1. super  2. setContentView  3. findViewById  4. new NumberListAdapter
    //          5. setAdapter
    // Risc:    `this` trebuie să fie Context; dacă ai pasa altceva, LayoutInflater.from
    //          aruncă.
    // Ref:     capitolul 12.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);                    // 1. ciclul de viață
        setContentView(R.layout.activity_two_column);          // 2. include antetul + ListView

        ListView lvNumbers = findViewById(R.id.lvNumbers);     // 3. ACELAȘI id ca în treapta 1

        NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
        //                                ↑ Context                  ↑ List<Integer> cu 100
        lvNumbers.setAdapter(adapter);                         // 4. leagă lista de widget
    }

    // Același id, alt layout — lvNumbers apare și în activity_single_column.xml, și în
    // activity_two_column.xml. Nu e o problemă: id-urile sunt unice PER LAYOUT, nu global.
    // findViewById caută doar în arborele layout-ului curent, deci găsește ListView-ul
    // din ecranul curent.
    //
    // `this` ca Context — adapterul are nevoie de el pentru LayoutInflater. Aici e
    // singurul loc în care activitatea atinge detaliul de inflate.
    //
    // Activitatea nu știe ce e într-un rând — nu există findViewById(R.id.tvDecimal)
    // aici. Cele două coloane sunt treaba adapterului. Dacă redenumești tvDecimal în
    // XML, se schimbă doar NumberListAdapter.
    //
    // Comparație cu treapta 1: aceeași structură, patru linii, doar clasa adapterului
    // diferită. Lecția: activitatea aproape nu se schimbă; adapterul e locul unde se
    // întâmplă totul.
    //
    // Ce s-ar întâmpla dacă ai pasa `null` ca Context: LayoutInflater.from(null) aruncă
    // NullPointerException în constructorul adapterului, deci la
    // new NumberListAdapter(null, ...). Erora apare devreme, în onCreate, nu la primul
    // rând — bine pentru depanare.
    //
    // ==================================================================================
    // DE CE ACTIVITATEA NU ARE NEVOIE DE `implements`
    // ==================================================================================
    //
    // Nu e nevoie de nicio interfață pentru că activitatea nu primește evenimente de la
    // adapter. Nu există „onItemBound" sau „onRowCreated". Adapterul e un obiect pasiv:
    // ListView îl întreabă, el răspunde. Activitatea doar îl construiește și îl predă.
    //
    // Dacă ai vrea să reacționezi la un click pe rând, ai avea două variante:
    //   1. lvNumbers.setOnItemClickListener(...)  → în activitate, cu poziția
    //   2. un listener pus pe rând, în getView     → în adapter
    // Aici nu e nevoie de niciuna: rândurile nu sunt clickabile.
    //
    // ==================================================================================
    // CE S-AR ÎNTÂMPLA DACĂ AI PUNE ADAPTERUL ÎNTR-UN CÂMP STATIC
    // ==================================================================================
    //
    //   private static NumberListAdapter adapter;   // ← greșit
    //
    // Adapterul ține lista și, prin holder-e, view-urile. Un câmp static ar ține
    // adapterul în viață după ce activitatea e distrusă, iar view-urile din holder-e ar
    // ține arborele vechi. Rezultatul: o scurgere de memorie care crește la fiecare
    // rotire. Adapterul e întotdeauna un câmp de instanță (sau o variabilă locală, ca
    // aici) — niciodată static.
}
```

**De ce blocul insistă pe „ce nu trebuie să facă activitatea":** pentru că majoritatea greșelilor la `ListView` vin din încercarea de a controla rândul din activitate. `findViewById(R.id.tvDecimal)` într-o activitate returnează `null` — rândurile nu sunt încă în arborele activității, sunt create la cerere de adapter. Dacă ai nevoie de un view dintr-un rând, îl iei din adapter, nu din activitate.

---

## 28.8 `activity_two_column.xml` — antet + listă

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FIȘIER: activity_two_column.xml
     ==================================================================================
     LOCAȚIE:  DMA06/src/main/res/layout/activity_two_column.xml
     ROL:      layout-ul treptei 2: antet fix sus, ListView jos.
     CONȚINE:  1 × include (layout_number_header), 1 × ListView
     ID-URI:   lvNumbers
     ================================================================================== -->

<!-- Coloană verticală: antetul sus (cât conținutul), lista jos (restul ecranului). -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Antetul e un fișier separat, refolosit și de treapta 3.
         Conținutul fișierului inclus e umflat ÎN LOCUL tag-ului: rezultatul e ca și
         cum ai fi scris antetul direct aici, dar definiția există într-un singur loc. -->
    <include layout="@layout/layout_number_header" />

    <!-- ListView-ul ia tot spațiul rămas după antet.
         0dp + weight="1" = „dimensiunea mea de bază e zero; ia din spațiul liber".
         Cu match_parent, lista ar cere toată înălțimea părintelui, ar depăși marginea
         de jos și s-ar tăia. -->
    <ListView
        android:id="@+id/lvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>

<!-- ======================================================================================
     CUM SE ÎMPARTE SPAȚIUL, CONCRET
     ======================================================================================
     Ecran: 800dp înălțime.
       antetul: wrap_content → măsoară textul + padding 12dp × 2 ≈ 60dp
       lista:   0dp + weight 1 → primește 800 − 60 = 740dp

     Dacă lista ar avea match_parent:
       antetul: 60dp
       lista:   cere 800dp → total 860dp → depășește cu 60dp
       rezultat: ultimele rânduri ies sub marginea ecranului și nu pot fi derulate
                 până la capăt, pentru că ListView crede că are loc

     De ce 0dp și nu wrap_content cu weight: weight se aplică pe spațiul RĂMAS după
     dimensiunea de bază. Cu 0dp, baza e zero, deci toată înălțimea disponibilă intră
     în calculul weight-ului. Cu wrap_content, lista ar primi „înălțimea conținutului
     + parte din rest", ceea ce nu e ce vrei.
     ====================================================================================== -->

<!-- ======================================================================================
     CE TREBUIE REȚINUT DIN FIȘIER
     ======================================================================================
     <include>                antetul e definit o singură dată, folosit de 2 ecrane
     0dp + weight="1"         lista ia restul după antet
     match_parent + weight    GREȘIT: lista ar depăși marginea de jos
     antetul în afara listei  rămâne fix la scroll; în listă ar fi derulat cu ea
     ordinea copiilor        antetul primul, lista a doua; weight nu schimbă ordinea
     ====================================================================================== -->
```

**De ce antetul e în afara listei:** rămâne fix când derulezi. Dacă ar fi primul element din listă, ar derula odată cu ea — și ai avea nevoie de un adapter cu două tipuri de rânduri (`getItemViewType`), mult mai complicat pentru un antet static.

**Ce se întâmplă dacă pui `include` după `ListView`:** antetul ar apărea **sub** listă. Ordinea copiilor în `LinearLayout` vertical e ordinea din XML, iar `weight`-ul nu schimbă ordinea, doar împarte spațiul.

**`<include>` și `layout_*`:** poți suprascrie atribute de layout pe tag-ul `<include>` (de exemplu `android:layout_marginTop`). Nu poți suprascrie `android:id`-ul rădăcinii incluse decât dacă îl declari explicit pe `include`. Aici nu e nevoie: antetul nu are id.

---

## 28.9 `layout_number_header.xml` — antetul refolosit

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FIȘIER: layout_number_header.xml
     ==================================================================================
     LOCAȚIE:  DMA06/src/main/res/layout/layout_number_header.xml
     ROL:      antetul cu două coloane, refolosit de treptele 2 și 3.
     CONȚINE:  2 × TextView („Decimal", „Binary")
     ID-URI:   niciunul — nimic din cod nu îl atinge
     ================================================================================== -->

<!-- De ce un fișier fără id-uri are totuși antet: pentru că e refolosit. Un fișier
     folosit de două ecrane se citește de două ori mai des decât unul folosit de unul
     singur. Iar faptul că nu are id-uri e o informație: înseamnă că poți schimba orice
     text din el fără să atingi Java. -->

<!-- Antetul cu două coloane. Nu are id-uri: codul nu îl atinge niciodată. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="?attr/colorSurfaceVariant"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="12dp">

    <!-- Coloana 1: „Decimal", aliniată la stânga (implicit) -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="@string/decimal"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <!-- Coloana 2: „Binary", aliniată la dreapta.
         gravity="end" respectă direcția de citire; "right" ar fi rămas mereu la dreapta. -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:gravity="end"
        android:text="@string/binary"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />
</LinearLayout>

<!-- ======================================================================================
     CE TREBUIE REȚINUT DIN FIȘIER
     ======================================================================================
     background="?attr/colorSurfaceVariant"      nuanță diferită, funcționează în dark mode
     textColor="?attr/colorOnSurfaceVariant"     perechea gândită împreună cu fundalul
     textAppearanceLabelLarge                    etichetă, mai mică decât BodyLarge
     paddingVertical="12dp"                      mai strâns decât rândul (14dp), intenționat
     aliniere identică cu item_number.xml        padding 16dp, weight 1, gravity end
     ====================================================================================== -->
```

**`background="?attr/colorSurfaceVariant"`** — o nuanță diferită de fundal, ca antetul să se distingă de rânduri. Vine din tema Material3, deci funcționează și în dark mode.

**`textColor="?attr/colorOnSurfaceVariant"`** — culoarea de text potrivită pentru acel fundal. Perechea `colorSurfaceVariant` / `colorOnSurfaceVariant` e gândită împreună; dacă pui un `#888` hardcodat, în dark mode textul dispare.

**Alinierea trebuie să coincidă cu `item_number.xml`:** același `paddingHorizontal="16dp"`, același `weight="1"`, aceeași `gravity="end"` pe a doua coloană. Sunt două fișiere separate, deci potrivirea se face manual. Dacă schimbi padding-ul într-unul singur, antetul nu se mai aliniază cu rândurile — și se vede imediat.

**De ce `paddingVertical="12dp"` aici și `14dp` în rând:** antetul e puțin mai strâns, ca să pară o etichetă, nu un rând. Diferența de 2dp e intenționată, nu o scăpare.

---

## 28.10 `NumberRecyclerAdapter.java` — treapta 3, adapterul

Același rând, aceleași date, alt contract. Diferența față de `NumberListAdapter` nu e cosmetică: sunt trei metode obligatorii în loc de patru, iar `getView` a fost tăiat în două.

```java
/*
 * ======================================================================================
 * FIȘIER: NumberRecyclerAdapter.java
 * ======================================================================================
 * LOCAȚIE:  DMA06/src/main/java/ro/ase/ie/dma06/adapters/NumberRecyclerAdapter.java
 * PACHET:   ro.ase.ie.adapters
 * ROL:      adaptează List<Integer> la ACELAȘI rând cu două coloane (item_number.xml),
 *           dar pentru un RecyclerView. ViewHolder-ul e obligatoriu, iar getView e
 *           despărțit în două metode.
 *
 * STRUCTURA FIȘIERULUI (5 părți):
 *   1. ViewHolder            — 10 linii: câmpuri final + constructor cu findViewById
 *   2. câmp + constructor    — 5 linii: doar lista, fără Context
 *   3. onCreateViewHolder    — 6 linii: creează rândul și holder-ul
 *   4. onBindViewHolder      — 6 linii: umple holder-ul
 *   5. getItemCount          — 3 linii: câte elemente sunt
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - Trei metode abstracte obligatorii: onCreateViewHolder, onBindViewHolder,
 *     getItemCount. Nu există getView.
 *   - Parametrul generic <NumberViewHolder> elimină toate cast-urile.
 *   - `super(itemView)` e obligatoriu în constructorul holder-ului.
 *   - Nu există `convertView`: RecyclerView decide singur ce holder refolosește.
 * ======================================================================================
 */

// ======================================================================================
// BLOCUL 1 — PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Față de NumberListAdapter au dispărut Context, BaseAdapter și inflater-ul ca câmp;
// au apărut NonNull și RecyclerView. Importul `android.view.View` rămâne: e tipul
// parametrului din constructorul holder-ului.
// ======================================================================================

package ro.ase.ie.adapters;   // același pachet ca NumberListAdapter

import android.view.LayoutInflater;   // pentru inflate, în onCreateViewHolder
import android.view.View;             // itemView-ul holder-ului
import android.view.ViewGroup;        // parent-ul din onCreateViewHolder
import android.widget.TextView;       // cele două coloane

import androidx.annotation.NonNull;                 // contract: parametru / rezultat care nu e null
import androidx.recyclerview.widget.RecyclerView;  // clasa de bază și ViewHolder-ul ei

import java.util.List;

import ro.ase.ie.dma06.R;

// ======================================================================================
// THEORY BLOCK: RECYCLERVIEW.ADAPTER
// ======================================================================================
/*
 * 1. CE ESTE
 *    -   Clasa abstractă care leagă datele de RecyclerView.
 *    -   Are TREI metode abstracte:
 *          onCreateViewHolder(ViewGroup parent, int viewType) → ViewHolder
 *          onBindViewHolder(ViewHolder holder, int position) → void
 *          getItemCount()                                    → int
 *    -   Toate celelalte au implementări implicite.
 *
 * 2. DE CE NU ARE getView
 *    -   Pentru că RecyclerView nu cere niciodată un View. Cere un ViewHolder.
 *    -   Un ViewHolder e o cutie cu un View înăuntru (itemView) plus referințe la
 *        copiii lui. RecyclerView ține holder-e, nu view-uri.
 *    -   De ce: ca să poată refolosi un holder FĂRĂ să știe ce e în el. Pentru asta
 *        are nevoie de un tip stabil (holder-ul), nu de un View oarecare.
 *
 * 3. DE CE TREI METODE ȘI NU UNA
 *    -   Crearea (inflate + findViewById) e scumpă și rară.
 *    -   Umplerea (setText) e ieftină și frecventă.
 *    -   Separându-le, RecyclerView poate chema doar a doua, de mii de ori, fără să
 *        plătească prima.
 *    -   getItemCount e a treia pentru că RecyclerView trebuie să știe câte poziții
 *        există ÎNAINTE de a cere vreun holder.
 *
 * 4. CE SE ÎNTÂMPLĂ CU CELELALTE METODE
 *    getItemId(int)             → NO_ID (-1) implicit; se activează cu setHasStableIds(true)
 *    getItemViewType(int)       → 0 implicit; pentru rânduri de tipuri diferite
 *    onViewRecycled(holder)     → gol; bun pentru anulat un download de imagine
 *    onViewAttachedToWindow     → gol; holder-ul intră în ecran
 *    onViewDetachedFromWindow   → gol; holder-ul iese din ecran
 *    onAttachedToRecyclerView   → gol; adapterul e legat de un RecyclerView
 *    onDetachedFromRecyclerView → gol; adapterul e dezlegat
 *
 * 5. CINE CHEAMĂ CE
 *    RecyclerView + LayoutManager decid:
 *      - câți holder-e încap pe ecran
 *      - care holder se refolosește pentru ce poziție
 *      - când e nevoie de un holder nou
 *    Adapterul doar răspunde: „iată un holder nou" / „am umplut holder-ul".
 *
 * 6. DE CE E CLASĂ ABSTRACTĂ ȘI NU INTERFAȚĂ
 *    Pentru că are stare: lista de observatori (AdapterDataObservable), referința la
 *    RecyclerView și implementările implicite ale metodelor opționale. O interfață nu
 *    poate ține stare.
 *
 * DIAGRAMA CELOR TREI METODE:
 *
 *   RecyclerView                         Adapter
 *   ── getItemCount() ──────────────────▶ 100
 *   ── „am nevoie de un holder" ────────▶ onCreateViewHolder(parent, 0)
 *                                            └─ inflate + new NumberViewHolder
 *   ── „umple-l pentru poziția 7" ──────▶ onBindViewHolder(holder, 7)
 *                                            └─ setText × 2
 *   ── „holder-ul a ieșit din ecran" ───▶ (îl pune în pool; adapterul nu e întrebat)
 */

/**
 * Step 3: fills the same row for a RecyclerView.
 * The ViewHolder is required here, and getView is split into two methods.
 */
public class NumberRecyclerAdapter
        extends RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder> {
        //                       ↑ tipul holder-ului, ca parametru generic

    // ==================================================================================
    // BLOCUL 2 — CLASA INTERIOARĂ NumberViewHolder
    // ==================================================================================
    // Teorie:  obligatorie; RecyclerView.Adapter e parametrizat cu ea.
    // Logică:  constructorul primește itemView, cheamă super(itemView) și caută copiii.
    // Risc:    fără `super(itemView)`, RecyclerView nu are ce recicla — holder-ul nu are
    //          un View asociat.
    // Ref:     capitolul 12.
    // ==================================================================================
    static class NumberViewHolder extends RecyclerView.ViewHolder {
        final TextView tvDecimal;   // final: atribuit în constructor, nu se mai schimbă
        final TextView tvBinary;    // final: atribuit în constructor, nu se mai schimbă

        NumberViewHolder(@NonNull View itemView) {
            super(itemView);                                        // obligatoriu: salvează rândul
            tvDecimal = itemView.findViewById(R.id.tvDecimal);      // căutare 1, o dată per holder
            tvBinary = itemView.findViewById(R.id.tvBinary);        // căutare 2, o dată per holder
        }
    }

    // Parametrul generic — RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder>
    // declară CE TIP DE HOLDER produce adapterul. De aici încolo, toate metodele
    // lucrează cu NumberViewHolder, nu cu RecyclerView.ViewHolder: onCreateViewHolder
    // îl returnează, onBindViewHolder îl primește. NICIO cast nicăieri — asta e
    // câștigul față de getTag().
    //
    // De ce NumberRecyclerAdapter.NumberViewHolder și nu doar NumberViewHolder: în
    // declarația `extends` nu ești încă în interiorul clasei, deci numele clasei
    // interioare trebuie calificat. În restul fișierului poți scrie doar NumberViewHolder.
    //
    // super(itemView) — obligatoriu. RecyclerView.ViewHolder nu are constructor fără
    // parametri, deci compilatorul te obligă să îl chemi. El salvează rândul în itemView.
    //
    // findViewById în constructorul holder-ului — asta e jumătatea de CREARE. Rulează
    // o singură dată per holder, nu la fiecare afișare.
    //
    // Câmpurile final — pot fi final pentru că sunt atribuite în constructor. La
    // NumberListAdapter nu puteau, pentru că erau atribuite după `new ViewHolder()`.
    // Diferența asta mică e exact motivul pentru care RecyclerView a mutat căutarea
    // în constructor.
    //
    // static class NumberViewHolder — din nou static, din aceleași două motive: fără
    // referință implicită la adapter și fără dependență de o instanță a adapterului.
    // Aici e `static class` fără `private`: tipul apare în semnătura publică a clasei
    // (RecyclerView.Adapter<...NumberViewHolder>), deci nu are rost să fie ascuns.
    // La NumberListAdapter holder-ul e `private static class`, pentru că nu apare în
    // nicio semnătură publică.
    //
    // @NonNull pe itemView — contract: RecyclerView nu îți dă niciodată null. Adnotarea
    // nu schimbă runtime-ul; e citită de lint și de Android Studio.

    // ==================================================================================
    // BLOCUL 3 — CÂMPUL ȘI CONSTRUCTORUL
    // ==================================================================================
    // Teorie:  primește doar lista; Context-ul se ia din `parent` la creare.
    // Logică:  this.numbers = numbers.
    // Risc:    dacă ai cere și Context, ai avea un parametru în plus care nu e folosit
    //          nicăieri în clasă.
    // Ref:     capitolul 12.
    // ==================================================================================
    private final List<Integer> numbers;   // sursa de date, prin referință

    public NumberRecyclerAdapter(List<Integer> numbers) {
        this.numbers = numbers;   // NU copiem lista
    }

    // Constructorul adapterului primește doar lista — spre deosebire de
    // NumberListAdapter, nu are nevoie de Context. Contextul se ia la nevoie din
    // parent.getContext(), în onCreateViewHolder.
    //
    // De ce nu are LayoutInflater ca câmp: pentru că îl poate lua din `parent` la
    // fiecare creare, iar creările sunt rare. Un câmp ar fi o optimizare prematură —
    // și ar cere Context în constructor.

    // ==================================================================================
    // BLOCUL 4 — onCreateViewHolder, JUMĂTATEA DE CREARE
    // ==================================================================================
    // Teorie:  creează un holder NOU: umflă rândul și construiește cutia.
    // Logică:  1. LayoutInflater.from(parent.getContext())
    //          2. inflate(item_number, parent, false)
    //          3. new NumberViewHolder(view)
    // Risc:    dacă uiți `false`, inflate întoarce părintele, nu rândul.
    // Ref:     capitolul 12.
    // ==================================================================================
    @NonNull
    @Override
    public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Runs only when a new row is needed
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_number, parent, false);   // ACELAȘI layout ca treapta 2
        return new NumberViewHolder(view);                       // holder-ul, nu view-ul
    }

    // Când rulează: doar când RecyclerView are nevoie de un holder NOU — pool-ul de
    // reciclare e gol. La pornire, pentru primele rânduri vizibile; apoi din ce în ce
    // mai rar.
    //
    // `parent` — RecyclerView-ul. Din el se ia Context-ul pentru inflater și el
    // furnizează LayoutParams-ul.
    //
    // `viewType` — aici e mereu 0, pentru că nu suprascriem getItemViewType. Dacă ai
    // avea două feluri de rânduri (antet + element), ai returna 0/1 din getItemViewType
    // și ai face switch aici, ca să umfli layout-ul potrivit.
    //
    // LayoutInflater.from(parent.getContext()) — nu mai e nevoie de un câmp
    // layoutInflater, pentru că `parent` cară contextul cu el.
    //
    // .inflate(R.layout.item_number, parent, false) — exact același apel ca la ListView:
    // același layout, aceiași parametri, același false.
    //
    // return new NumberViewHolder(view) — întoarce HOLDER-UL, nu view-ul. RecyclerView
    // are nevoie de holder ca să știe ce a creat și să îl poată recicla.
    //
    // @NonNull — contract: parent nu e null, rezultatul nu e null. Lint-ul verifică.
    //
    // De ce metoda nu întoarce View: pentru că RecyclerView nu lucrează cu View-uri.
    // Lucrează cu holder-e, care știu ce copii au înăuntru. Un View returnat ar trebui
    // re-inspectat la fiecare refolosire — exact ce ViewHolder evită.

    // ==================================================================================
    // BLOCUL 5 — onBindViewHolder ȘI getItemCount
    // ==================================================================================
    // Teorie:  umple un holder existent cu datele de la poziția dată.
    // Logică:  1. numbers.get(position)  2. setText × 2
    // Risc:    dacă faci `findViewById` aici, ai pierdut tot câștigul holder-ului.
    // Ref:     capitolul 12.
    // ==================================================================================
    @Override
    public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
        // Runs each time a row shows a number
        int number = numbers.get(position);                          // Integer → int
        holder.tvDecimal.setText(String.valueOf(number));            // coloana 1
        holder.tvBinary.setText(Integer.toBinaryString(number));     // coloana 2
    }

    // ----------------------------------------------------------------------------------
    // METODA 3 — getItemCount
    // ----------------------------------------------------------------------------------
    // Teorie:  înlocuiește getCount() din BaseAdapter.
    // Logică:  dimensiunea listei.
    // Risc:    dacă minte, onBindViewHolder primește o poziție invalidă.
    // Ref:     capitolul 12.
    // ----------------------------------------------------------------------------------
    @Override
    public int getItemCount() {
        return numbers.size();   // 100
    }

    // Când rulează onBindViewHolder: de fiecare dată când un rând ARATĂ un element —
    // la prima afișare, la fiecare refolosire după scroll, după notifyItemChanged,
    // după o animație.
    //
    // Nu există convertView — holder-ul vine gata creat. Nu există
    // `if (convertView == null)`, pentru că decizia a fost luată deja de RecyclerView.
    //
    // Nu există findViewById — referințele sunt în holder, luate la creare.
    //
    // numbers.get(position) direct — adapterul nu are getItem(position). Dacă ai nevoie
    // de el (de exemplu pentru un click), îl adaugi ca metodă proprie.
    //
    // getItemCount() înlocuiește getCount() — același rol: câte elemente are lista.
    //
    // Dacă getItemCount() minte: dacă întoarce mai mult decât numbers.size(),
    // onBindViewHolder ajunge la numbers.get(position) cu o poziție invalidă →
    // IndexOutOfBoundsException. Dacă întoarce mai puțin, ultimele elemente pur și
    // simplu nu apar.
    //
    // De ce onBindViewHolder întoarce void: pentru că holder-ul e deja la RecyclerView.
    // Nu trebuie returnat nimic — metoda doar modifică un obiect pe care RecyclerView
    // îl are deja. La getView, returnarea era necesară pentru că ListView nu avea altă
    // cale să afle ce view să adauge.
    //
    // Ce se întâmplă dacă apeși pe un rând: nimic. Nu există listener. Într-o aplicație
    // reală, ai pune un OnClickListener pe holder.itemView chiar în onBindViewHolder —
    // și ai avea grijă să folosești holder.getAdapterPosition(), nu `position`, pentru
    // că poziția se poate schimba între bind și click.
    //
    // ==================================================================================
    // GETVIEW()  vs  onCreateViewHolder() + onBindViewHolder() — ACEEAȘI IMAGINE, DESPICATĂ
    // ==================================================================================
    //
    // ┌─────────────────────────────────────────────────────────────────────────────────┐
    // │                          LISTVIEW: O SINGURĂ METODĂ                             │
    // │                                                                                 │
    // │   getView(position, convertView, parent)                                        │
    // │   ├─────────────────────────────────────────────────────────────────────────┐   │
    // │   │ PARTEA A — CREARE                                      doar dacă null   │   │
    // │   │   if (convertView == null) {                                           │   │
    // │   │       convertView = inflate(...)          ← XML → obiecte              │   │
    // │   │       holder = new ViewHolder()            ← cutia goală               │   │
    // │   │       holder.tvDecimal = findViewById(...) ← căutare                   │   │
    // │   │       holder.tvBinary  = findViewById(...) ← căutare                   │   │
    // │   │       convertView.setTag(holder)           ← lipește cutia             │   │
    // │   │   }                                                                    │   │
    // │   ├─────────────────────────────────────────────────────────────────────────┤   │
    // │   │ PARTEA B — UMPLERE                                    la FIECARE apel  │   │
    // │   │   else { holder = getTag() }              ← ia cutia                   │   │
    // │   │   holder.tvDecimal.setText(...)                                        │   │
    // │   │   holder.tvBinary.setText(...)                                         │   │
    // │   │   return convertView                                                   │   │
    // │   └─────────────────────────────────────────────────────────────────────────┘   │
    // │                                                                                 │
    // │   ↑ cele două părți sunt în ACEEAȘI metodă, separate doar de un `if`            │
    // └─────────────────────────────────────────────────────────────────────────────────┘
    //
    //                                     ↓  despicarea  ↓
    //
    // ┌─────────────────────────────────────────────────────────────────────────────────┐
    // │                       RECYCLERVIEW: DOUĂ METODE SEPARATE                        │
    // │                                                                                 │
    // │   onCreateViewHolder(parent, viewType)      onBindViewHolder(holder, position)  │
    // │   ├──────────────────────────────────┐      ├──────────────────────────────────┤
    // │   │ PARTEA A — CREARE                │      │ PARTEA B — UMPLERE               │
    // │   │   View view = inflate(...)       │      │   int number = numbers.get(pos)  │
    // │   │   return new NumberViewHolder(   │      │   holder.tvDecimal.setText(...)  │
    // │   │       view)                      │      │   holder.tvBinary.setText(...)   │
    // │   │       ├─ super(itemView)         │      │   (void — nu returnează nimic)   │
    // │   │       ├─ findViewById × 2        │      │                                  │
    // │   │       └─ câmpuri final           │      │                                  │
    // │   └──────────────────────────────────┘      └──────────────────────────────────┘
    // │                                                                                 │
    // │   CINE DECIDE CARE SE CHEAMĂ:                                                   │
    // │     pool gol            → onCreateViewHolder + onBindViewHolder                 │
    // │     pool are un holder  → doar onBindViewHolder                                 │
    // │                                                                                 │
    // │   CINE ȚINE LOCUL LUI convertView: pool-ul intern (RecycledViewPool)            │
    // │   CINE ȚINE LOCUL LUI setTag/getTag: tipul generic al adapterului               │
    // └─────────────────────────────────────────────────────────────────────────────────┘
    //
    // Citește diagrama de sus în jos, apoi de jos în sus. Sus: o metodă, două ramuri,
    // un `if` care le desparte. Jos: două metode, fiecare cu o singură ramură, iar
    // decizia mutată în framework. ACEEAȘI MUNCĂ, ÎMPĂRȚITĂ ALTFEL.
    //
    // CE SE CÂȘTIGĂ CONCRET:
    //   reumplere fără creare   pool-ul dă un holder gata făcut; doar onBindViewHolder
    //   animații                RecyclerView știe ce holder s-a mutat
    //   actualizări parțiale    notifyItemChanged(5) re-leagă doar poziția 5
    //   cod tipat               holder-ul e parametru, nu Object dintr-un tag
    //   testabilitate           poți testa onBindViewHolder cu un holder construit manual
    //
    // CE SE PIERDE: două metode în loc de una, un parametru generic în plus,
    // super(itemView) obligatoriu. Pentru o listă de 100 de numere, câștigul e mic.
    // Pentru o listă de 10.000 de imagini, e diferența dintre 60fps și 20fps.
    //
    // ==================================================================================
    // CE SE ÎNTÂMPLĂ DACĂ UIȚI super(itemView)
    // ==================================================================================
    //
    //   NumberViewHolder(@NonNull View itemView) {
    //       // super(itemView);   ← scos
    //       tvDecimal = itemView.findViewById(R.id.tvDecimal);
    //   }
    //
    // Nu compilează: RecyclerView.ViewHolder nu are constructor fără parametri, iar
    // compilatorul încearcă să cheme super() implicit. Erora e la compilare, nu la
    // runtime — deci o prinzi imediat:
    //
    //   error: constructor ViewHolder in class ViewHolder cannot be applied to given types;
    //     required: View
    //     found: no arguments
    //
    // Dacă ai chema super(null), ar compila, dar itemView ar fi null și RecyclerView ar
    // crăpa la primul layout, când încearcă să adauge holder-ul în arbore.
    //
    // ==================================================================================
    // RECYCLEDVIEWPOOL — CE ȚINE ȘI CÂND SE GOLEȘTE
    // ==================================================================================
    //
    //   RecycledViewPool
    //     ├── SparseArray<ScrapData> pe viewType
    //     │     ├── viewType 0 → listă de holder-e (max 5 implicit)
    //     │     └── viewType 1 → listă de holder-e
    //     └── fiecare holder ține itemView + referințele din constructor
    //
    // Implicit, pool-ul păstrează maximum 5 holder-e per tip. Restul sunt lăsate să
    // fie colectate. La o listă cu 10 rânduri vizibile, 5 în pool sunt de ajuns.
    //
    // Se golește la setAdapter cu alt adapter, la setRecycledViewPool(null) și la
    // distrugerea RecyclerView-ului. Nu se golește la scroll.
    //
    // ==================================================================================
    // CUM SE ADAUGĂ UN CLICK PE RÂND
    // ==================================================================================
    //
    //   @Override
    //   public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
    //       int number = numbers.get(position);
    //       holder.tvDecimal.setText(String.valueOf(number));
    //       holder.tvBinary.setText(Integer.toBinaryString(number));
    //       holder.itemView.setOnClickListener(v ->
    //               Toast.makeText(v.getContext(),
    //                       "Poziția " + holder.getAdapterPosition(),
    //                       Toast.LENGTH_SHORT).show());
    //   }
    //
    // De ce getAdapterPosition() și nu `position`: între momentul bind-ului și momentul
    // click-ului, lista se poate schimba (un element șters, unul adăugat). `position`
    // e valoarea de la bind, care poate fi veche; getAdapterPosition() întoarce poziția
    // curentă. În codul din repo nu există click, deci nu există nici problema.
    //
    // ==================================================================================
    // DE CE HOLDER-UL NU ARE NEVOIE DE ADAPTER
    // ==================================================================================
    //
    // Un ViewHolder ține itemView și doi copii. Nu are nevoie de listă, de poziție sau
    // de adapter ca să existe. De aceea poate fi `static`: nu depinde de nicio instanță
    // a clasei exterioare. Toată informația vine ca parametru în onBindViewHolder.
    //
    // La NumberListAdapter, holder-ul e construit în getView și umplut imediat, tot
    // acolo. Aici e construit în onCreateViewHolder și umplut în altă metodă, cu date
    // primite ca parametru. Diferența de design se vede în semnătura constructorului.
}
```

**Ce trebuie să reții din fișierul ăsta:** `RecyclerView.Adapter` are exact trei metode abstracte și **nu are `getView`**. Motivul e că `RecyclerView` nu cere niciodată un `View` — cere un `ViewHolder`. Iar holder-ul e tipat prin parametrul generic, deci toate cast-urile dispar.

**De ce `getItemCount()` nu se numește `getCount()`:** pentru că nu e aceeași interfață. `BaseAdapter` implementează `ListAdapter`, care are `getCount()`. `RecyclerView.Adapter` e o clasă independentă, cu numele ei. Asemănarea e funcțională, nu contractuală.

**Ce se întâmplă cu `getItemId`:** în `RecyclerView.Adapter` există, dar întoarce `NO_ID` (`-1`) implicit. Dacă vrei id-uri stabile, suprascrii metoda și chemi `setHasStableIds(true)` pe adapter. Aici nu e nevoie: nu există selecție.

---

## 28.11 `RecyclerViewActivity.java` — treapta 3, ecranul

Aici se vede ce `ListView` ținea înăuntru: `LayoutManager`, `ItemDecoration`, `ItemAnimator`. Fiecare e un obiect separat, setat din cod.

```java
/*
 * ======================================================================================
 * FIȘIER: RecyclerViewActivity.java
 * ======================================================================================
 * LOCAȚIE:  DMA06/src/main/java/ro/ase/ie/dma06/activities/RecyclerViewActivity.java
 * PACHET:   ro.ase.ie.dma06.activities
 * ROL:      treapta 3. Același rând, aceleași date, dar cu RecyclerView. Aici se vede
 *           ce ListView ținea înăuntru: LayoutManager, ItemDecoration, ItemAnimator.
 *
 * STRUCTURA FIȘIERULUI (2 părți):
 *   1. importuri   — 10 linii, dintre care 3 din androidx.recyclerview
 *   2. onCreate    — 12 linii: layout, RecyclerView, LayoutManager, decoration, adapter
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - Fără setLayoutManager, RecyclerView nu afișează NIMIC și nu dă eroare.
 *   - DividerItemDecoration ia orientarea ca `int`, nu ca obiect.
 *   - Adapterul nu primește Context: îl ia din `parent` la creare.
 * ======================================================================================
 */

// ======================================================================================
// BLOCUL 1 — PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Trei importuri noi față de treapta 2, toate din androidx.recyclerview:
//   RecyclerView            widget-ul
//   LinearLayoutManager     aranjarea
//   DividerItemDecoration   separatorul
// ======================================================================================

package ro.ase.ie.dma06.activities;      // pachetul ecranelor

import android.os.Bundle;                // parametrul lui onCreate

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.DividerItemDecoration;   // linia dintre rânduri
import androidx.recyclerview.widget.LinearLayoutManager;    // aranjarea pe verticală
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.adapters.NumberRecyclerAdapter;
import ro.ase.ie.data.NumberData;
import ro.ase.ie.dma06.R;

// ======================================================================================
// THEORY BLOCK: CELE PATRU PIESE ALE UNUI RECYCLERVIEW
// ======================================================================================
/*
 * 1. ADAPTER — CONȚINUTUL
 *    Ce se afișează. Creează holder-e și le umple. Nu știe unde stau pe ecran.
 *
 * 2. LAYOUTMANAGER — ARANJAREA
 *    Unde stau. Câte rânduri încap, cât măsoară fiecare, cum se calculează scroll-ul.
 *    Fără el, RecyclerView nu are cine să îi spună ce să deseneze.
 *
 * 3. ITEMDECORATION — DECORAȚIUNEA
 *    Ce se desenează peste sau sub rânduri: separatori, margini, umbre.
 *    Spre deosebire de ListView, nu există `android:divider` în XML.
 *
 * 4. ITEMANIMATOR — ANIMAȚIA
 *    Cum se mișcă rândurile când datele se schimbă. Vine implicit (DefaultItemAnimator);
 *    nu îl configurezi aici.
 *
 * SEPARAREA:
 *
 *   ┌──────────────────────────────────────────────────────────────────────────────┐
 *   │                            RecyclerView                                      │
 *   │                                                                              │
 *   │   ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐   ┌──────────┐  │
 *   │   │   Adapter    │   │  LayoutManager   │   │ItemDecoration│   │ Animator │  │
 *   │   │  (conținut)  │   │   (aranjare)     │   │ (separatori) │   │(mișcare) │  │
 *   │   └──────┬───────┘   └────────┬─────────┘   └──────┬───────┘   └────┬─────┘  │
 *   │          │                    │                    │                │        │
 *   │   ce se vede            unde se vede          ce se vede        cum se       │
 *   │   în fiecare rând       pe ecran              între rânduri     mișcă       │
 *   └──────────────────────────────────────────────────────────────────────────────┘
 *
 *   ListView avea toate patru înghesuite într-o singură clasă. De aceea nu puteai
 *   schimba aranjarea fără să schimbi widget-ul.
 *
 * CONSECINȚA PRACTICĂ:
 *   -   Schimbi LinearLayoutManager cu GridLayoutManager(2) → grilă, fără nicio
 *       modificare în adapter.
 *   -   Adaugi un ItemDecoration → separatori, fără să atingi adapterul.
 *   -   Schimbi adapterul → alt conținut, fără să atingi aranjarea.
 *
 * DE CE „PATRU” ȘI NU TREI:
 *   ItemAnimator există și lucrează, chiar dacă nu îl configurezi. Un RecyclerView fără
 *   setItemAnimator are DefaultItemAnimator, care animează adăugări, ștergeri și
 *   mutări. Dacă îl scoți cu setItemAnimator(null), animațiile dispar, dar lista
 *   funcționează.
 */

/**
 * Step 3: the same two columns in a RecyclerView.
 * RecyclerView needs a LayoutManager, and dividers are added separately.
 */
public class RecyclerViewActivity extends AppCompatActivity {

    // ==================================================================================
    // METODA 1 — onCreate
    // ==================================================================================
    // Teorie:  ciclul de viață; aici se asamblează cele patru piese.
    // Logică:  1. super  2. setContentView  3. findViewById
    //          4. LayoutManager + setLayoutManager
    //          5. DividerItemDecoration + addItemDecoration
    //          6. adapter + setAdapter
    // Risc:    fără setLayoutManager, ecranul rămâne gol, fără excepție.
    // Ref:     capitolul 12 și capitolul 23 (migrarea ListView → RecyclerView).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);                          // 1. ciclul de viață
        setContentView(R.layout.activity_recycler_view);             // 2. antet + RecyclerView

        RecyclerView rvNumbers = findViewById(R.id.rvNumbers);       // 3. singurul RecyclerView

        LinearLayoutManager layoutManager = new LinearLayoutManager(this);   // 4. aranjare verticală
        rvNumbers.setLayoutManager(layoutManager);                          //    ← OBLIGATORIU
        rvNumbers.addItemDecoration(
                new DividerItemDecoration(this, layoutManager.getOrientation()));  // 5. separator
        //                                ↑ Context   ↑ orientarea, ca int

        NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
        rvNumbers.setAdapter(adapter);                               // 6. conținutul
    }

    // Ordinea celor trei setări: setLayoutManager → addItemDecoration → setAdapter.
    // Ordinea nu e fatală între ele, dar setLayoutManager TREBUIE să fie înainte de
    // orice layout. Dacă îl uiți, RecyclerView nu desenează nimic, indiferent câte
    // decorări și adaptoare ai adăuga.
    //
    // LinearLayoutManager(this) — constructorul cu un singur argument înseamnă vertical.
    // Varianta completă: LinearLayoutManager(context, orientation, reverseLayout).
    // Aici orientation ar fi RecyclerView.VERTICAL (1), iar reverseLayout false.
    //
    // layoutManager.getOrientation() — întoarce RecyclerView.VERTICAL, adică 1.
    // DividerItemDecoration așteaptă propria constantă, DividerItemDecoration.VERTICAL,
    // care e tot 1. Sunt două constante diferite ca semnificație, dar cu aceleași valori
    // (0 = orizontal, 1 = vertical în ambele clase), deci linia funcționează.
    //
    // DANGER! Compilatorul nu poate verifica: ambele sunt int. Dacă ai schimba
    // LayoutManager-ul pe orizontală, getOrientation() ar întoarce 0, care e tot
    // DividerItemDecoration.HORIZONTAL — deci codul rămâne corect. Potrivirea e reală,
    // nu întâmplătoare, dar se bazează pe valori numerice, nu pe un tip comun.
    //
    // addItemDecoration înainte de setAdapter — ordinea dintre ele nu contează.
    // Decorarea se aplică la desenare, nu la setarea datelor.
    //
    // De ce rvNumbers e declarat RecyclerView și nu View: pentru că ai nevoie de
    // setLayoutManager, addItemDecoration și setAdapter — toate metode ale clasei.
    // findViewById e generic, deci deduce tipul din variabilă.
    //
    // De ce nu se cheamă notifyDataSetChanged(): datele sunt fixe, iar setAdapter
    // declanșează singur primul layout. notifyDataSetChanged() ar fi redundant și ar
    // cauza o reumplere inutilă.

    // ==================================================================================
    // CE FACE LAYOUTMANAGER LA FIECARE CADRU
    // ==================================================================================
    //
    //   RecyclerView.onLayout()
    //     └─ LayoutManager.onLayoutChildren(recycler, state)
    //          ├─ calculează câți copii încap în spațiul disponibil
    //          ├─ cere holder-e din pool pentru pozițiile vizibile
    //          ├─ cheamă adapter.onBindViewHolder(holder, position) pentru fiecare
    //          ├─ măsoară și poziționează fiecare rând (layoutDecorated)
    //          └─ aruncă în pool holder-ele care au ieșit din ecran
    //
    // GridLayoutManager — new GridLayoutManager(this, 2) aranjează în două coloane.
    // Adapterul rămâne neschimbat, item_number.xml rămâne neschimbat.
    //
    // StaggeredGridLayoutManager — coloane cu înălțimi diferite, ca un Pinterest.
    // La fel, fără modificări în adapter.
    //
    // setReverseLayout(true) — lista crește de jos în sus, ca un chat. Tot din
    // LayoutManager.
    //
    // ==================================================================================
    // CE SE ÎNTÂMPLĂ FĂRĂ setLayoutManager
    // ==================================================================================
    //
    //   Nimic. Și exact asta e problema.
    //
    //   RecyclerView fără LayoutManager
    //     ├─ setAdapter(adapter)        → succes, fără excepție
    //     ├─ addItemDecoration(...)     → succes, fără excepție
    //     ├─ onMeasure()                → măsoară 0 × 0
    //     ├─ onLayout()                 → Log.e: „No layout manager attached; skipping layout"
    //     └─ ecranul                    → gol
    //
    //   Mesajul exact din Logcat:
    //     E/RecyclerView: No layout manager attached; skipping layout
    //
    //   De ce nu aruncă excepție: pentru că RecyclerView e proiectat să funcționeze și
    //   fără conținut. Un RecyclerView gol e o stare validă (de exemplu înainte de
    //   încărcarea datelor). Framework-ul nu poate ști dacă ai uitat să setezi managerul
    //   sau dacă intenționat nu ai încă date.
    //
    //   De ce e cea mai urâtă eroare din capitol: compilează, rulează, nu crapă, dar
    //   ecranul e gol. Toate celelalte greșeli din capitol se văd imediat; asta se vede
    //   doar dacă știi să te uiți în Logcat.
    //
    //   Ordinea de diagnostic pentru un RecyclerView gol:
    //     1) ai setLayoutManager?
    //     2) ai setAdapter?
    //     3) getItemCount() întoarce mai mult de 0?
    //     4) rădăcina layout-ului are înălțime nenulă?
    //   În 90% din cazuri, răspunsul e la prima întrebare.

    // ==================================================================================
    // DIAGRAMA SEPARĂRII: CONȚINUT vs ARANJARE
    // ==================================================================================
    //
    // ┌─────────────────────────────────────────────────────────────────────────────────┐
    // │              CE SE AFIȘEAZĂ          vs.        CUM SE ARANJEAZĂ                │
    // │                                                                                 │
    // │   ADAPTER (conținut)                      LAYOUTMANAGER (aranjare)               │
    // │   ├── getItemCount() → 100                ├── câte rânduri încap                 │
    // │   ├── onCreateViewHolder → rândul         ├── unde stă fiecare rând               │
    // │   ├── onBindViewHolder → textul           ├── cât măsoară fiecare                 │
    // │   └── getItemViewType → tipul             ├── cum se calculează scroll-ul         │
    // │                                           └── ce holder se refolosește            │
    // │                                                                                 │
    // │   Nu știe:                                Nu știe:                              │
    // │   ├── câte rânduri încap                  ├── ce e într-un rând                   │
    // │   ├── unde stă rândul                     ├── ce date există                      │
    // │   └── cum se derulează                    └── câte elemente sunt                  │
    // │                                                                                 │
    // │   ─────────────────────────────────────────────────────────────────────────     │
    // │                                                                                 │
    // │   ACELEAȘI DATE + ACELAȘI ADAPTER:                                              │
    // │                                                                                 │
    // │   LinearLayoutManager      GridLayoutManager(2)        StaggeredGrid(2)          │
    // │   ┌───┐                    ┌───┬───┐                   ┌───┬───┐                 │
    // │   │ 1 │                    │ 1 │ 2 │                   │ 1 │ 2 │                 │
    // │   ├───┤                    ├───┼───┤                   │   ├───┤                 │
    // │   │ 2 │                    │ 3 │ 4 │                   │ 3 │ 4 │                 │
    // │   ├───┤                    ├───┼───┤                   ├───┼───┤                 │
    // │   │ 3 │                    │ 5 │ 6 │                   │ 5 │ 6 │                 │
    // │   └───┘                    └───┴───┘                   └───┴───┘                 │
    // │                                                                                 │
    // │   zero modificări în adapter, zero modificări în item_number.xml                │
    // └─────────────────────────────────────────────────────────────────────────────────┘
    //
    // De ce separarea e importantă la examen: întrebarea „ce trebuie să setăm la un
    // RecyclerView ca să afișeze ceva” are răspunsul „adapter + LayoutManager”. Dacă
    // răspunzi doar „adapter”, ai pierdut jumătate din punctaj — și, mai important,
    // ai pierdut exact diferența față de ListView.
    //
    // Ce înseamnă „conținut” și „aranjare” în practică: conținutul e ce se vede în
    // fiecare rând (numărul zecimal și cel binar). Aranjarea e unde se vede fiecare
    // rând (unul sub altul, în două coloane, invers). Sunt două întrebări independente,
    // deci două obiecte independente.

    // ==================================================================================
    // DIVIDERITEMDECORATION — SEPARATORUL
    // ==================================================================================
    //
    // ListView are android:divider în XML. RecyclerView nu are așa ceva. Liniile dintre
    // rânduri sunt desenate de un ItemDecoration, iar DividerItemDecoration e decorarea
    // gata făcută din bibliotecă.
    //
    // Cum funcționează, în trei pași:
    //   1. RecyclerView desenează rândurile (prin LayoutManager)
    //   2. ItemDecoration.onDraw()      → desenează SUB conținut (înainte de copii)
    //   3. ItemDecoration.onDrawOver()  → desenează PESTE conținut (după copii)
    //
    // DividerItemDecoration folosește onDraw și desenează o linie la marginea de jos a
    // fiecărui rând, cu excepția ultimului.
    //
    // layoutManager.getOrientation() — îi spune decorării dacă liniile sunt orizontale
    // sau verticale. Pentru o listă verticală, separatorul e o linie orizontală între
    // rânduri. Pentru o listă orizontală, ar fi o linie verticală între coloane.
    //
    // Ce se întâmplă dacă pui orientarea greșită: separatorul e desenat pe cealaltă
    // axă — adică linii verticale peste rânduri, sau linii orizontale suprapuse. Nu
    // crapă, doar arată greșit. E genul de bug care se vede din prima.
    //
    // De ce nu e în XML: pentru că RecyclerView nu are atribute proprii de separator.
    // Tot ce ține de desenare se face din cod, prin ItemDecoration. E prețul separării:
    // mai mult cod, mai mult control.
    //
    // ==================================================================================
    // LISTVIEW vs RECYCLERVIEW — DIFERENȚELE DIN ACEST FIȘIER
    // ==================================================================================
    //
    //   ListView (treptele 1 și 2)          RecyclerView (treapta 3)
    //   ├── aranjare internă, fixă          ├── setLayoutManager(...) explicit
    //   ├── android:divider în temă         ├── addItemDecoration(...) în cod
    //   ├── animații limitate               ├── ItemAnimator implicit
    //   ├── adapter cu getView              ├── adapter cu 3 metode
    //   └── reciclare internă               └── RecycledViewPool, tot intern
    //
    // Trei linii de configurare în plus, trei capabilități în plus. Nimic din fișierul
    // ăsta nu există în treptele 1 și 2 — și exact asta e lecția capitolului.
    //
    // ==================================================================================
    // CE SE ÎNTÂMPLĂ DACĂ PUI DECORAREA DUPĂ setAdapter
    // ==================================================================================
    //
    //   Funcționează. addItemDecoration nu depinde de adapter; decorarea se aplică la
    //   faza de desenare, care are loc oricum după layout. Ordinea recomandată
    //   (manager → decoration → adapter) e o convenție de citire, nu o cerință.
    //
    // Ce ESTE o cerință: setLayoutManager înainte ca RecyclerView să primească primul
    // layout. Dacă îl setezi după ce view-ul a fost deja măsurat, RecyclerView cere
    // un requestLayout() — de aceea, în practică, îl setezi în onCreate, înainte de
    // orice altceva.
    //
    // ==================================================================================
    // DE CE `this` CA PRIM ARGUMENT LA LinearLayoutManager ȘI LA DividerItemDecoration
    // ==================================================================================
    //
    // Ambele au nevoie de Context:
    //   - LinearLayoutManager îl folosește pentru Resources (dimensiuni, densitate);
    //   - DividerItemDecoration îl folosește pentru a obține drawable-ul de separator
    //     din tema curentă.
    //
    // Nu e același Context ca la adapter: adapterul nu primește niciunul, pentru că îl
    // ia din `parent` în onCreateViewHolder. Aici, în onCreate, nu ai încă un `parent`,
    // deci `this` e singura sursă.
}
```

**Ce trebuie să reții din fișierul ăsta:** un `RecyclerView` funcțional are nevoie de **adapter + LayoutManager**. Restul (`ItemDecoration`, `ItemAnimator`) sunt opționale. Iar dacă uiți `setLayoutManager`, nu primești nicio excepție — doar un ecran gol și un rând în Logcat.

**De ce `ListView` nu putea fi descompus:** pentru că aranjarea era în `AbsListView.layoutChildren`, iar separatorul în `android:divider`. Ambele erau private. `RecyclerView` a fost scris de la zero ca să expună aceste puncte ca obiecte schimbabile.

---

## 28.12 `activity_recycler_view.xml` — antet + `RecyclerView`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FIȘIER: activity_recycler_view.xml
     ==================================================================================
     LOCAȚIE:  DMA06/src/main/res/layout/activity_recycler_view.xml
     ROL:      layout-ul treptei 3: ACELAȘI antet, ACEEAȘI structură ca treapta 2,
               doar widget-ul diferă.
     CONȚINE:  1 × include (layout_number_header), 1 × RecyclerView
     ID-URI:   rvNumbers
     ================================================================================== -->

<!-- Aceeași structură ca la treapta 2: antet fix sus, listă jos.
     Diferența dintre cele două fișiere e de exact un tag. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Același antet, din același fișier -->
    <include layout="@layout/layout_number_header" />

    <!-- Numele complet: RecyclerView nu e în android.widget, ci în biblioteca AndroidX.
         XML-ul nu are importuri, deci numele complet e singurul mod de a referi o clasă
         din alt pachet. La fel se întâmplă cu MaterialButton. -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>

<!-- ======================================================================================
     ATRIBUTE PE CARE RECYCLERVIEW LE ARE ȘI FIȘIERUL NU LE FOLOSEȘTE
     ======================================================================================
     android:clipToPadding="false"        rândurile se desenează și sub padding
     android:scrollbars="vertical"        bara de scroll, dacă o vrei explicită
     android:overScrollMode="never"       fără efectul de „elastic" la capete
     app:layoutManager="androidx.recyclerview.widget.LinearLayoutManager"
                                          aranjarea direct din XML, fără cod
     app:spanCount="2"                    numărul de coloane pentru GridLayoutManager
     tools:listitem="@layout/item_number" doar în preview, nu la runtime
     ======================================================================================
     `app:layoutManager` e singurul care chiar poate înlocui o linie de cod. Dar el
     creează managerul cu constructorul fără argumente, deci nu poți configura
     orientarea sau reverseLayout. În practică, se setează din cod.
     ====================================================================================== -->

<!-- ======================================================================================
     CE TREBUIE REȚINUT DIN FIȘIER
     ======================================================================================
     nume complet            androidx.recyclerview.widget.RecyclerView
     rvNumbers               prefix rv = RecyclerView, lv = ListView
     0dp + weight="1"        aceeași logică: antetul wrap_content, lista ia restul
     fără android:divider    separatorul vine din DividerItemDecoration, în cod
     fără dependență directă RecyclerView vine tranzitiv prin biblioteca Material
     ====================================================================================== -->
```

**Numele complet e obligatoriu** — `RecyclerView` nu e o clasă din `android.widget`, deci XML-ul nu o poate prescurta. La fel se întâmplă cu orice view din biblioteci: `com.google.android.material.button.MaterialButton`, `androidx.recyclerview.widget.RecyclerView`.

**Nicio dependență explicită în `build.gradle.kts`** — nu există o linie `implementation(libs.recyclerview)`. Clasa se rezolvă pentru că biblioteca Material (`com.google.android.material:material`) aduce `androidx.recyclerview` tranzitiv. Dacă ai scoate Material, importul ar crăpa.

**De ce `rvNumbers` și nu `lvNumbers`:** id-ul e diferit de cel din treptele 1 și 2, deși ar fi putut fi același (layout-uri diferite). Diferența e intenționată: `rv` = `RecyclerView`, `lv` = `ListView`. Când citești `findViewById(R.id.rvNumbers)`, știi imediat ce tip de widget primești.

**Ce s-ar întâmpla dacă ai pune un `ListView` în loc de `RecyclerView`:** ar compila (dacă ai schimba și `findViewById`), dar `setLayoutManager` nu ar exista pe `ListView`. Deci nu poți înlocui unul cu altul fără să schimbi și codul. Layout-ul e aproape identic; clasa nu.

---

## 28.13 `item_number.xml` — un singur layout pentru două adaptere

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ==================================================================================
     FIȘIER: item_number.xml
     ==================================================================================
     LOCAȚIE:  DMA06/src/main/res/layout/item_number.xml
     ROL:      rândul cu două coloane. Folosit de NumberListAdapter ȘI de
               NumberRecyclerAdapter. Este dovada că diferența dintre trepte nu e în
               layout, ci în adapter.
     CONȚINE:  1 × LinearLayout orizontal, 2 × TextView
     ID-URI:   tvDecimal, tvBinary   ← contractul ambelor adaptoare
     ================================================================================== -->

<!-- De ce antetul e cel mai important din capitol: pentru că fișierul e folosit de
     DOUĂ adaptoare. Dacă schimbi un id aici, trebuie să îl schimbi în două fișiere
     Java. Dacă schimbi un padding, se schimbă în ambele trepte. Un layout partajat
     e un contract partajat. -->

<!-- One row with two columns. Steps 2 and 3 both use this layout. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="14dp">

    <!-- Coloana 1: numărul zecimal, aliniat la stânga.
         0dp + weight="1" = jumătate din lățime. Cu wrap_content, fiecare coloană ar fi
         lată cât textul ei, iar coloanele nu s-ar mai alinia între rânduri. -->
    <TextView
        android:id="@+id/tvDecimal"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:textAppearance="?attr/textAppearanceBodyLarge" />

    <!-- Coloana 2: numărul binar, aliniat la dreapta, cu font monospațiat.
         monospace = cifre de aceeași lățime, deci numerele binare se aliniază frumos.
         gravity="end" respectă direcția de citire (supportsRtl="true" în manifest). -->
    <TextView
        android:id="@+id/tvBinary"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:fontFamily="monospace"
        android:gravity="end"
        android:textAppearance="?attr/textAppearanceBodyLarge" />
</LinearLayout>

<!-- ======================================================================================
     CE TREBUIE REȚINUT DIN FIȘIER
     ======================================================================================
     match_parent × wrap_content      lat cât lista, înalt cât conținutul
     paddingHorizontal 16dp           spațiu interior; există din API 26, minSdk 33
     paddingVertical 14dp             mai generos decât antetul (12dp)
     0dp + weight="1" pe ambele       echivalentul a 50% / 50%
     fontFamily="monospace"           doar pe coloana binară
     gravity="end"                    aliniere care respectă RTL
     fără android:text                rândul e gol până îl umple adapterul
     tvDecimal / tvBinary             contractul ambelor adaptoare
     ======================================================================================
     CUM SE MĂSOARĂ UN RÂND
     ======================================================================================
     LinearLayout orizontal, doi copii cu 0dp + weight 1:
       1. părintele primește lățimea listei (match_parent)
       2. scade padding-ul orizontal: 16dp + 16dp = 32dp
       3. împarte restul la suma weight-urilor: (L − 32) / 2 pentru fiecare
       4. fiecare TextView primește exact jumătate, indiferent cât text are
       5. înălțimea: wrap_content → cea mai înaltă dintre cele două, plus padding 14dp × 2

     De aceea cele două coloane se aliniază perfect între rânduri, deși textele au
     lungimi diferite: lățimea nu depinde de conținut. Cu wrap_content ar depinde, iar
     coloana a doua ar „sări" la fiecare rând.
     ====================================================================================== -->
```

**Comentariul din capul fișierului** — „Steps 2 and 3 both use this layout" — e chiar miezul capitolului. Același fișier XML servește `ListView`-ul din treapta 2 și `RecyclerView`-ul din treapta 3. Diferența dintre cele două **nu e în layout**, ci în adapter.

**`match_parent` × `wrap_content`** — rândul e lat cât lista și înalt cât conținutul. Înălțimea `wrap_content` se adaptează la font mărit; o înălțime fixă ar tăia textul.

**`fontFamily="monospace"`** — cifrele au aceeași lățime, deci numerele binare se aliniază frumos la dreapta. E un font din sistem, nu un fișier adăugat în proiect.

**Fără `android:text`** — rândul e gol în preview și se umple la runtime. Fără adapter, ai vedea 100 de rânduri goale.

**Cele două id-uri sunt contractul** — `tvDecimal` și `tvBinary` sunt căutate de **ambele** adaptoare. Dacă le redenumești, trebuie schimbate în două fișiere Java.

### Același layout, două apeluri `inflate`

```
// NumberListAdapter.getView
convertView = layoutInflater.inflate(R.layout.item_number, parent, false);

// NumberRecyclerAdapter.onCreateViewHolder
View view = LayoutInflater.from(parent.getContext())
        .inflate(R.layout.item_number, parent, false);
```

Același fișier, aceiași parametri, același `false`. Singurul lucru care diferă e metoda din jur: una primește un `convertView` posibil reciclat, cealaltă creează un holder nou.

**Ce înseamnă asta pentru examen:** dacă ți se cere să explici de ce `item_number.xml` e același în ambele trepte, răspunsul e „pentru că layout-ul descrie **rândul**, nu **lista**". Rândul e independent de cine îl aranjează. `ListView` și `RecyclerView` diferă prin modul în care produc și refolosesc rândurile, nu prin ce e într-un rând.

---

## 28.14 Comparația finală, metodă cu metodă

### Corespondența exactă între cele două adaptere

| # | `NumberListAdapter` (ListView) | `NumberRecyclerAdapter` (RecyclerView) | Când rulează |
|---|---|---|---|
| 1 | `public int getCount()` | `public int getItemCount()` | la fiecare măsurare a listei |
| 2 | `public Integer getItem(int position)` | — (se folosește direct `numbers.get(position)`) | la cerere (`getItemAtPosition`), respectiv la bind |
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

**Cum se citește tabelul:** fiecare rând e o singură responsabilitate, nu o linie de cod. Rândurile 1–3 sunt „evidența" (câte, care, ce id). Rândurile 4–9 sunt „crearea". Rândurile 10–12 sunt „umplerea". Împărțirea pe verticală a tabelului e exact împărțirea pe verticală a codului.

**Ce nu are corespondent:** `getItem` și `getItemId` nu au echivalent obligatoriu în `RecyclerView.Adapter`. `getItem` dispare pentru că `onBindViewHolder` primește direct poziția și are lista în câmp. `getItemId` există, dar e opțional și întoarce `NO_ID` implicit.

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
| `Context` în constructor | `parent.getContext()` la creare |

**De ce dispare `Context` din constructor:** pentru că `onCreateViewHolder` primește `parent`, iar `parent.getContext()` e exact contextul de care ai nevoie. Un parametru mai puțin în constructor înseamnă o clasă mai ușor de testat: poți construi adapterul fără o activitate.

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

**Aceeași linie de date, trei costuri:** treapta 1 e cea mai ieftină de scris și cea mai limitată. Treapta 2 e cea mai explicită și cea mai verbosă. Treapta 3 e cea mai flexibilă și cea mai „ceremonioasă" la prima vedere — dar toată ceremonia se plătește o singură dată, la scriere, nu la runtime.

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
Ca aranjarea să fie independentă de conținut. Schimbi lista în grilă fără să atingi adapterul.

**„Ce se întâmplă fără `setLayoutManager`?"**
`RecyclerView` nu afișează nimic și nu dă eroare. Doar mesajul `No layout manager attached; skipping layout` în Logcat.

**„Câte metode are obligatoriu `RecyclerView.Adapter`?"**
Trei: `onCreateViewHolder`, `onBindViewHolder`, `getItemCount`. Nu are `getView`, pentru că nu primește și nu întoarce `View`-uri, ci `ViewHolder`-uri.

**„De ce `NumberData` are constructor privat?"**
Pentru că toate metodele sunt statice și nu există stare. Constructorul privat blochează `new NumberData()`, care nu ar avea sens. E tiparul claselor utilitare din JDK.

---

## 28.15 Fluxul complet

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
  LayoutManager măsoară și decide câte holder-e încap
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
| apeși pe un rând | `OnItemClickListener` → `getItemAtPosition(position)` | listener pus pe view, în `onBindViewHolder` |

**Ultima linie e o diferență de design, nu de API:** `ListView` are un listener global pe listă; `RecyclerView` nu are `OnItemClickListener`. Îl pui pe fiecare rând, în `onBindViewHolder`, de obicei pe `holder.itemView`. Aici nu e nevoie — niciun rând nu e clickabil.

### Ce nu se schimbă deloc

- `NumberData` — aceeași sursă, aceleași 100 de numere.
- `item_number.xml` — același rând, aceleași două coloane.
- `layout_number_header.xml` — același antet.
- Textul afișat — „1 / 1", „2 / 10", …, „100 / 1100100".

Se schimbă doar **cine** produce rândurile și **cum** sunt aranjate.

---

## 28.16 Ce să reții

- **Trei trepte, aceleași date.** `ArrayAdapter` → `BaseAdapter` cu `ViewHolder` manual → `RecyclerView.Adapter`. Diferența nu e în layout, ci în adapter.
- **`convertView`** e rândul reciclat. `null` = rând nou; non-`null` = refolosește-l.
- **`setTag` / `getTag`** lipesc `ViewHolder`-ul de rând. Fără `setTag`, `getTag` întoarce `null` și lista crapă la primul scroll — cu `NullPointerException: Attempt to read from field ... on a null object reference`.
- **`ViewHolder` e `static`** ca să nu țină referință la adapter. La `ListView` e `private static`; la `RecyclerView` e `static` (package-private), pentru că apare în semnătura publică.
- **`getView` s-a despărțit** în `onCreateViewHolder` (creare, rară și scumpă) și `onBindViewHolder` (umplere, frecventă și ieftină).
- **`LayoutManager` e separat** ca aranjarea să fie independentă de conținut. Fără el, `RecyclerView` e gol și tăcut.
- **`RecyclerView` nu are `OnItemClickListener`** global și nu are `android:divider`. Le înlocuiește cu listener pe rând și `ItemDecoration`.
- **`getItemCount()` mincinos** → `IndexOutOfBoundsException` în `onBindViewHolder`.
- **`inflate(layout, parent, false)`** — `parent` pentru `LayoutParams`, `false` ca să nu atașeze acum.
- **Pachetele `data` și `adapters` nu conțin `dma06`** în declarație, deși folderele da. Importurile folosesc pachetul declarat.
- **`NumberData.getNumbers()` întoarce o listă nouă** la fiecare apel. Trei ecrane, trei liste independente.
- **`ArrayAdapter` cheamă `toString()`** pe fiecare element. Funcționează pentru un singur text; se oprește la al doilea `TextView`.

---

## Rezumat capitol 28

- `DMA06` = trei trepte pe aceleași numere 1–100: `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter`.
- `NumberData` e curat: `final`, constructor `private`, metodă `static`, zero importuri `android.*`.
- Treapta 1: trei linii de adapter, un singur `TextView`, nicio reciclare scrisă de tine.
- Treapta 2: `getView` cu `if (convertView == null)`, `ViewHolder` + `setTag`/`getTag`, `findViewById` o singură dată per rând.
- Treapta 3: `onCreateViewHolder` + `onBindViewHolder` + `getItemCount`, holder tipat, fără cast.
- `item_number.xml` e comun treptelor 2 și 3 — dovada că diferența e în adapter.
- `LayoutManager` și `ItemDecoration` sunt piesele pe care `ListView` le ținea înăuntru (aranjare fixă, divider din XML), iar `RecyclerView` le-a scos afară.
- `activity_two_column.xml` și `activity_recycler_view.xml` sunt aproape identice: doar widget-ul diferă.

**Înapoi la** [capitolul 12](12%20-%20DMA06%20-%20ListView%20vs%20RecyclerView.md) **sau la** [cheatsheet](21%20-%20Cheatsheet.md).







