# Capitolul 27 — Codul DMA05 adnotat

**Obiectiv:** să citești DMA05 ca pe un laborator de widget-uri — fiecare view din XML, fiecare listener din cod și fiecare linie de `ViewBinding`, cu explicația lângă ele. Nu există logică de business: există doar UI, iar tot ce se poate învăța din el e **legătura dintre XML și cod**.

**Sursa:** `DMA05/` la commitul `d719ffc` — 29 de fișiere, din care 3 contează pentru capitol: `MainActivity.java`, `activity_main.xml`, `AndroidManifest.xml`. Al patrulea fișier care contează indirect este `build.gradle.kts`, pentru că acolo se aprinde `viewBinding`.

**Ce înveți din el:** `ViewBinding` (`ActivityMainBinding`), toate widget-urile de input și listenerii lor, plus fluxul complet `XML → arbore de View-uri → ecran`.

**Timp estimat:** 60–90 min (citire activă, cu fișierul deschis alături).

> **Cum citești:** fiecare fișier este o **singură bucată continuă**, în ordinea din sursă. Comentariile sunt țesute în ea, ca într-un fișier adnotat pe care îl poți citi de sus până jos. Nu sări peste blocurile de teorie: ele explică deciziile care apar imediat după ele. Pentru fiecare porțiune, acoperă comentariul și încearcă să spui tu ce face linia următoare. Dacă nu poți, ai găsit ce trebuie repetat.

**Legendă:** codul din blocurile de mai jos este **identic cu fișierele din repo**. Tot ce apare după `//` sau între `/* */` (respectiv între `<!-- -->` în XML) a fost adăugat pentru explicare. Comentariile nu schimbă comportamentul, dar în XML ele **nu pot sta pe același rând cu un atribut** — de aceea acolo stau pe rânduri separate, deasupra elementului.

---

## 27.0 Harta fișierelor

```
DMA05/
├── build.gradle.kts                          ← viewBinding = true (pornește generatorul)
├── src/main/
│   ├── AndroidManifest.xml                   ← declară activitatea, tema, soft input
│   ├── java/ro/ase/ie/dma05/
│   │   └── MainActivity.java                 ← 88 de linii: inflate + 7 listeneri
│   └── res/
│       ├── layout/activity_main.xml          ← 17 ID-uri, 14 copii direcți
│       ├── drawable/ic_android_black_24dp.xml    ← vectorul din ImageView
│       ├── drawable/ic_launcher_background.xml
│       ├── drawable/ic_launcher_foreground.xml
│       ├── mipmap-anydpi/ic_launcher.xml
│       ├── mipmap-anydpi/ic_launcher_round.xml
│       ├── mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher*.webp
│       ├── values/colors.xml                 ← black, white
│       ├── values/strings.xml                ← doar app_name = "DMA05"
│       ├── values/themes.xml                 ← Theme.DMA05
│       ├── values-night/themes.xml           ← varianta de noapte
│       └── xml/backup_rules.xml, data_extraction_rules.xml
├── src/test/java/ro/ase/ie/dma05/ExampleUnitTest.java
├── src/androidTest/java/ro/ase/ie/dma05/ExampleInstrumentedTest.java
└── src/main/keepRules/rules.keep
```

**29 de fișiere, 3 relevante.** Restul sunt șablonul Android Studio: iconițe, teste goale, reguli de backup. Nu le citim.

**De ce 3 și nu 4:** `build.gradle.kts` nu se citește linie cu linie, dar cele două linii care contează sunt:

```kotlin
android {
    namespace = "ro.ase.ie.dma05"          // pachetul aplicației (înlocuiește `package` din manifest)
    buildFeatures { viewBinding = true }   // ← fără asta, ActivityMainBinding nu există
}
```

**`namespace` și `viewBinding` sunt singurele lucruri din build care se văd în codul Java.** `namespace` explică de ce `import ro.ase.ie.dma05.databinding.ActivityMainBinding;` are exact acel prefix. `viewBinding = true` explică de ce clasa există. Restul fișierului — SDK-uri, dependențe, versiuni — nu schimbă nicio linie din `MainActivity`.

**`minSdk = 33`** — aplicația rulează doar pe Android 13+. Contează pentru `EdgeToEdge`: nu există ramuri de compatibilitate pentru API-uri vechi, iar `WindowInsetsCompat` are implementare nativă pe toate dispozitivele vizate.

---

## 27.1 `MainActivity.java` — fișierul întreg, adnotat

Fișierul are 88 de linii și face un singur lucru: construiește ecranul, îl pune pe display și leagă șapte listeneri. Îl citim ca pe un singur document, de sus până jos.

```java
/*
 * ======================================================================================
 * FIȘIER: MainActivity.java
 * ======================================================================================
 * LOCAȚIE:  DMA05/src/main/java/ro/ase/ie/dma05/MainActivity.java
 * PACHET:   ro.ase.ie.dma05
 * ROL:      singura activitate a aplicației. Nu are model, nu are date, nu are rețea.
 *           Construiește arborele de view-uri din activity_main.xml și înregistrează
 *           șapte listeneri, fiecare cu un Toast ca efect.
 *
 * STRUCTURA FIȘIERULUI (4 părți):
 *   1. importuri                  — 15 linii, dintre care unul generat
 *   2. câmpul `binding`           — 1 linie
 *   3. onCreate                   — 64 de linii, tot comportamentul
 *   4. închiderea clasei          — 2 linii
 *
 * CE TREBUIE SĂ ȘTII ÎNAINTE:
 *   - `ActivityMainBinding` NU există în sursă. O generează Gradle la build.
 *   - `inflate` construiește arborele; `setContentView` îl pune pe ecran. Doi pași.
 *   - Fiecare `binding.<nume>` este o citire de câmp, nu o căutare în arbore.
 *   - Șapte listeneri, cinci interfețe, două stiluri (lambda / clasă anonimă).
 * ======================================================================================
 */

/*
 * ======================================================================================
 * THEORY BLOCK 1: VIEW BINDING
 * ======================================================================================
 *
 * 1. CE ESTE
 *    O clasă Java generată de Android Gradle Plugin, câte una pentru fiecare fișier
 *    de layout din res/layout/. Nu o scrii tu, nu o modifici, nu o versionezi.
 *
 * 2. CÂND SE GENEREAZĂ
 *    La BUILD, nu la runtime. AGP rulează un task de generare înainte de compilarea
 *    Java, scrie fișierele în build/generated/... și le pune pe classpath.
 *    Consecința 1: dacă adaugi un android:id și nu rulezi build-ul, câmpul nu există.
 *    Consecința 2: clasa nu apare în src/, deci nu o vei găsi căutând în proiect.
 *
 * 3. DIN CE SE GENEREAZĂ
 *    Din res/layout/activity_main.xml. Fiecare android:id="@+id/..." devine un câmp
 *    public final cu tipul tag-ului:
 *      <Button android:id="@+id/button">    ->  public final Button button;
 *      <SeekBar android:id="@+id/seekBar">  ->  public final SeekBar seekBar;
 *
 * 4. REGULA DE NUME
 *    activity_main.xml  ->  ActivityMainBinding
 *    activity_item.xml  ->  ActivityItemBinding
 *    item_movie.xml     ->  ItemMovieBinding
 *    underscore + literă mică -> CamelCase; sufixul Binding se adaugă mereu.
 *
 * 5. CONDIȚIA DE ACTIVARE
 *    build.gradle.kts:
 *      android { buildFeatures { viewBinding = true } }
 *    Fără ea, clasa nu se generează și importul nu compilează.
 *
 * 6. CE CONȚINE
 *    - un câmp public final per android:id
 *    - un câmp privat rootView + metoda getRoot()
 *    - două metode statice inflate(...)
 *    - o metodă statică bind(View)
 *
 * 7. CE NU FACE
 *    - nu e DataBinding: fără expresii @{...} în XML
 *    - nu înlocuiește findViewById pentru ID-uri primite la runtime
 *    - nu generează câmpuri pentru view-uri fără android:id
 *
 * PIPELINE-UL DE GENERARE:
 *
 *   activity_main.xml
 *        │
 *        ├── aapt2 ──────────────▶ R.java (R.id.button, R.layout.activity_main)
 *        │
 *        └── AGP ViewBinding ────▶ ActivityMainBinding.java
 *                                      │
 *                                      ▼
 *                                  javac (compilează ambele)
 *                                      │
 *                                      ▼
 *                                  APK (clasa e în dex, ca orice clasă)
 */

/*
 * ======================================================================================
 * THEORY BLOCK 2: CICLUL DE VIAȚĂ AL UNEI ACTIVITĂȚI
 * ======================================================================================
 *
 * 1. STĂRILE, ÎN ORDINE
 *    onCreate()   → instanța e construită; aici se umflă layout-ul și se leagă listenerii
 *    onStart()    → activitatea devine vizibilă, dar nu neapărat interactivă
 *    onResume()   → activitatea e în prim-plan și primește input
 *    onPause()    → pierde focusul; salvezi ce e ieftin, oprești animații
 *    onStop()     → nu mai e vizibilă; eliberezi resurse grele
 *    onDestroy()  → instanța moare; aici s-ar anula listeneri globali
 *    onRestart()  → după onStop, înainte de onStart, când revii în activitate
 *
 * 2. CE GARANTEAZĂ onCreate
 *    - Window-ul există deja (creat de ActivityThread înainte de apel).
 *    - `setContentView` poate fi chemat după `super.onCreate`, fără să arunce.
 *    - `findViewById` întoarce null până după `setContentView`.
 *    - `savedInstanceState` e `null` la prima pornire și un Bundle la recreare.
 *
 * 3. DE CE `super.onCreate` PRIMUL
 *    AppCompatActivity delegă ciclul de viață către AppCompatDelegate. Dacă apelezi
 *    `setContentView` înainte de `super.onCreate`, delegate-ul nu are încă `Context`-ul
 *    și tema, iar inflate-ul aruncă. Regula e mecanică: super primul, restul după.
 *
 * 4. RECREAREA LA ROTIRE
 *    ROTIRE → onPause → onStop → onSaveInstanceState → onDestroy
 *           → onCreate(savedInstanceState ≠ null) → onStart → onResume
 *    Instanța e NOUĂ. Câmpul `binding` e reasignat. Listener-ii se reînregistrează.
 *    Starea widget-urilor cu `android:id` se restaurează automat de către framework.
 *
 * 5. CE SE ÎNTÂMPLĂ CU `binding` LA RECREARE
 *    Vechiul binding rămâne atașat de arborele vechi, care e distrus. Ambele devin
 *    eligibile pentru garbage collection. Nu există scurgere pentru că nu păstrezi
 *    o referință statică și nu asculti nimic global.
 *
 * DIAGRAMA STĂRILOR:
 *
 *   PORNIRE
 *     │
 *     ▼
 *   onCreate ──▶ onStart ──▶ onResume ──▶ [RUNNING]
 *                                            │
 *                                            ▼
 *                                         onPause
 *                                            │
 *                                            ▼
 *                                         onStop ──▶ onDestroy   (dacă nu revine)
 *                                            │
 *                                            ▼
 *                                        onRestart ──▶ onStart ──▶ onResume
 */

/*
 * ======================================================================================
 * THEORY BLOCK 3: WINDOW INSETS ȘI EDGE-TO-EDGE
 * ======================================================================================
 *
 * 1. IERARHIA FERESTREI
 *    Activity
 *      └── Window (PhoneWindow)
 *            └── DecorView (FrameLayout)
 *                  ├── (opțional) action bar
 *                  └── android.R.id.content (FrameLayout)
 *                        └── ce ai pus tu cu setContentView
 *
 *    Barele de sistem (status, navigare) NU sunt copii ale DecorView: sunt ferestre
 *    separate, desenate de sistem deasupra lui. De aceea conținutul poate ajunge
 *    „sub" ele când fereastra e edge-to-edge.
 *
 *    `setContentView(view)` nu pune view-ul direct în fereastră: îl adaugă în
 *    `android.R.id.content`, un FrameLayout care umple tot spațiul rămas.
 *
 * 2. CE SUNT INSETS
 *    Patru valori (left, top, right, bottom), în pixeli, care spun cât din marginea
 *    ecranului e acoperită de ceva ce nu trebuie să acoperi cu conținut:
 *      - statusBars()      → bara de sus (ceas, baterie, notificări)
 *      - navigationBars()  → bara de jos (butoane sau gest bar)
 *      - captionBar()      → bara de titlu în multi-window
 *      - ime()             → tastatura
 *      - displayCutout()   → notch / gaură în ecran
 *      - systemGestures()  → zonele gesturilor de sistem
 *    `Type.systemBars()` = statusBars | navigationBars | captionBar.
 *
 * 3. EDGE-TO-EDGE
 *    Implicit, `decorFitsSystemWindows = true`: sistemul micșorează fereastra ca să
 *    încapă între bare. Conținutul nu ajunge niciodată sub bară.
 *    `EdgeToEdge.enable(this)` setează `decorFitsSystemWindows = false`: fereastra
 *    se întinde pe tot ecranul, iar tu primești insets-urile și decizi ce faci cu ele.
 *    Avantaj: conținutul poate desena sub bară (imagini, hărți, video).
 *    Cost: trebuie să aplici tu padding-ul, altfel primul widget stă sub ceas.
 *
 * 4. CUM CIRCULĂ INSETS-URILE
 *    Sistem → DecorView → content → rădăcină → copii
 *    Fiecare view poate:
 *      - să ignore (returnează insets-urile primite)
 *      - să consume (returnează CONSUMED) → dispatch-ul se oprește
 *      - să modifice (returnează insets-uri noi) → copiii primesc valorile modificate
 *    Listener-ul din DMA05 returnează `insets`, deci nu consumă nimic.
 *
 * 5. DE CE PADDING PE RĂDĂCINĂ
 *    Padding-ul pe rădăcină mută TOȚI copiii în zona sigură, cu o singură operație.
 *    Padding-ul pe un copil mută doar acel copil. Iar dacă rădăcina nu are padding,
 *    primul copil stă sub bara de status, indiferent ce padding are al doilea.
 *
 * 6. CE NU ACOPERĂ `Type.systemBars()`
 *    Tastatura. Pentru IME ai nevoie de `Type.ime()` și, de obicei, de un al doilea
 *    listener sau de o combinație în același listener. DMA05 nu o face, pentru că
 *    toate câmpurile sunt în jumătatea de sus a ecranului.
 *
 * DIAGRAMA DISPATCH-ULUI:
 *
 *   WindowInsets { systemBars: (0, 24, 0, 48), ime: (0, 0, 0, 0) }
 *        │
 *        ▼
 *   DecorView ──▶ content ──▶ LinearLayout (root)
 *                                  │  listener: setPadding(0, 24, 0, 48)
 *                                  │  return insets  ← nu consumă
 *                                  ▼
 *                            Button, Switch, … primesc aceleași insets,
 *                            dar nu au listener, deci le ignoră
 */

// ======================================================================================
// PACHETUL ȘI IMPORTURILE
// ======================================================================================
// Primul rând al oricărui fișier Java: pachetul. Aici nu e doar organizare — e și
// sursa prefixului pentru clasa generată: `ro.ase.ie.dma05` + `.databinding`.
// ======================================================================================

package ro.ase.ie.dma05;                              // pachetul modulului; vine din `namespace` în build.gradle.kts

// --------------------------------------------------------------------------------------
// GRUPUL 1 — API-ul Android clasic (android.*)
// Sunt clase din framework-ul care există pe dispozitiv, nu din biblioteci împachetate.
// --------------------------------------------------------------------------------------

import android.os.Bundle;                             // parametrul lui onCreate: starea salvată la rotire
import android.view.View;                             // tipul parametrului din onClick(View v) și al lui v din lambda de insets
import android.widget.RadioButton;                    // tipul returnat de group.findViewById(checkedId)
import android.widget.RadioGroup;                     // tipul parametrului `group` din OnCheckedChangeListener
import android.widget.SeekBar;                        // interfața cu TREI metode — singura care cere clasă anonimă
import android.widget.Toast;                          // feedback-ul tuturor celor șapte listeneri

// --------------------------------------------------------------------------------------
// GRUPUL 2 — AndroidX (androidx.*)
// Biblioteci împachetate în APK, cu versiune fixată în build.gradle.kts.
// --------------------------------------------------------------------------------------

import androidx.activity.EdgeToEdge;                  // desenare sub barele de sistem (activity-ktx 1.8+)
import androidx.annotation.NonNull;                   // adnotare de contract, nu schimbă runtime-ul
import androidx.appcompat.app.AppCompatActivity;      // clasa de bază: Activity + AppCompat + delegate
import androidx.core.graphics.Insets;                 // cele patru valori de padding, în pixeli
import androidx.core.view.ViewCompat;                 // înregistrarea listener-ului de insets, compatibil pe orice API
import androidx.core.view.WindowInsetsCompat;         // Type.systemBars() și obiectul `insets`

// --------------------------------------------------------------------------------------
// GRUPUL 3 — codul GENERAT (ro.ase.ie.dma05.databinding)
// Acesta e singurul import care nu are un fișier corespondent în src/.
// --------------------------------------------------------------------------------------

import ro.ase.ie.dma05.databinding.ActivityMainBinding;   // ← clasa GENERATĂ la build din activity_main.xml

// --------------------------------------------------------------------------------------
// DE CE LIPSESC Button, Switch, CheckBox, ToggleButton, RatingBar, EditText, ImageView
// --------------------------------------------------------------------------------------
// În fișier nu apare niciodată numele acestor tipuri. Le accesezi doar ca `binding.button`,
// `binding.switch1` etc. — compilatorul știe tipul din câmpul generat, tu nu îl mai scrii.
// ViewBinding elimină și importurile, nu doar findViewById.
//
// `View` e importat deși nu instanțiezi unul: e tipul parametrului din onClick(View v)
// și al parametrului `v` din lambda de insets. `RadioButton` e importat pentru că îl
// declari ca tip al variabilei locale `selected`. `SeekBar` e importat pentru că numele
// apare explicit în `new SeekBar.OnSeekBarChangeListener()`.

// ======================================================================================
// CLASA ȘI CÂMPUL
// ======================================================================================
// O singură clasă, un singur câmp. Câmpul e cheia întregului fișier: el ține arborele
// viu după ce onCreate se termină.
// ======================================================================================

public class MainActivity extends AppCompatActivity {   // AppCompatActivity = Activity + AppCompat + delegate

    ActivityMainBinding binding;                         // câmp, nu variabilă locală; null până la inflate

    // ----------------------------------------------------------------------------------
    // DE CE CÂMP ȘI NU VARIABILĂ LOCALĂ
    // ----------------------------------------------------------------------------------
    // În DMA05 ar funcționa și local, pentru că totul se întâmplă în onCreate. Dar tiparul
    // e câmp pentru că în orice aplicație reală binding-ul e atins și din onSaveInstanceState,
    // și din metode ajutătoare, și din listeneri. `ActivityMainBinding binding;` fără
    // `private` e package-private — funcționează, dar `private` ar fi stilul corect.
    //
    // Înainte de `inflate`, câmpul e `null`. Nu e „gol", e referință nulă. Orice
    // `binding.button` înainte de linia cu `inflate` dă NullPointerException.
    //
    // De ce nu e `static`: binding-ul aparține instanței de activitate. La rotire,
    // onCreate rulează din nou pe o instanță nouă și reasignează câmpul. Un câmp static
    // ar ține arborele vechi în viață și ar scurge memoria activității distruse.
    //
    // De ce nu e `final`: pentru că `inflate` se apelează în onCreate, nu în constructor.
    // ----------------------------------------------------------------------------------

    // ----------------------------------------------------------------------------------
    // METODA: onCreate
    // ----------------------------------------------------------------------------------
    // CÂND SE APELEAZĂ: o singură dată per instanță de activitate, după ce Window-ul
    //   a fost creat și înainte ca arborele să fie desenat.
    // CE PRIMEȘTE: `savedInstanceState` — un Bundle cu starea salvată la rotire, sau
    //   `null` la prima pornire. În DMA05 nu e citit niciodată: starea widget-urilor
    //   se restaurează automat, pentru că toate au `android:id`.
    // CE TREBUIE SĂ FACĂ: să apeleze `super.onCreate` PRIMUL. Altfel, delegate-ul
    //   AppCompat nu e inițializat și `setContentView` aruncă.
    // ----------------------------------------------------------------------------------
    @Override                                             // suprascriem metoda din AppCompatActivity
    protected void onCreate(Bundle savedInstanceState) {  // `protected`, ca în clasa de bază
        super.onCreate(savedInstanceState);               // 1. ciclul de viață al părintelui — obligatoriu primul

        // ------------------------------------------------------------------------------
        // PASUL 2 — CONSTRUIREA ARBORELUI
        // ------------------------------------------------------------------------------
        // `ActivityMainBinding.inflate(...)` face TREI lucruri, într-o singură expresie:
        //   a. cere LayoutInflater-ului să parseze res/layout/activity_main.xml
        //   b. creează obiectele Java pentru fiecare tag (LinearLayout, Button, …)
        //   c. parcurge arborele și umple câmpurile clasei generate, după `android:id`
        // Rezultatul e un obiect ActivityMainBinding pe care îl păstrăm în câmp.
        //
        // getLayoutInflater() întoarce LayoutInflater-ul activității, deja legat de
        // Context-ul și de tema ei. De aceea nu scrii LayoutInflater.from(this) — e
        // același obiect, doar obținut pe altă cale.
        //
        // Varianta cu un argument apelează intern `inflate(inflater, null, false)`:
        // arborele se construiește complet, dar rămâne NEATAȘAT. Nu are încă un părinte
        // și nu e desenat. Asta permite `setContentView(binding.getRoot())` să îl
        // atașeze exact o dată, la locul potrivit. Dacă `inflate` l-ar atașa singur,
        // `setContentView` ar arunca IllegalStateException: The specified child already
        // has a parent.
        // ------------------------------------------------------------------------------
        binding = ActivityMainBinding.inflate(getLayoutInflater());   // 2. XML → obiecte Java + câmpuri umplute

        /*
         * DIAGRAMA 1 — cum se construiește arborele și cum se umplu câmpurile:
         *
         * activity_main.xml (text)                          obiecte Java (heap)
         * ┌────────────────────────────────┐
         * │ <LinearLayout id="@+id/main">  │
         * │   ├─ <Button id="@+id/button"> │   LayoutInflater
         * │   ├─ <ImageView id="…">        │   ───────────────▶   creează câte un obiect
         * │   ├─ <Switch id="@+id/switch1">│                      per tag, cu atributele
         * │   ├─ <EditText id="…"> × 5     │                      citite din XML
         * │   ├─ <CheckBox id="…">         │
         * │   ├─ <RadioGroup id="…">       │
         * │   │    ├─ <RadioButton id="…"> │
         * │   │    └─ <RadioButton id="…"> │
         * │   ├─ <ToggleButton id="…">     │
         * │   ├─ <ProgressBar id="…">      │
         * │   ├─ <SeekBar id="…">          │
         * │   └─ <RatingBar id="…">        │
         * └────────────────────────────────┘
         *                                              ┌──────────────────────────────────┐
         *                                              │ LinearLayout        (id = main)  │
         *                                              │   ├─ Button         (id = button)│
         *                                              │   ├─ ImageView                   │
         *                                              │   ├─ Switch         (id = switch1)│
         *                                              │   ├─ EditText × 5                │
         *                                              │   ├─ CheckBox                    │
         *                                              │   ├─ RadioGroup                  │
         *                                              │   │    ├─ RadioButton            │
         *                                              │   │    └─ RadioButton            │
         *                                              │   ├─ ToggleButton                │
         *                                              │   ├─ ProgressBar                 │
         *                                              │   ├─ SeekBar                     │
         *                                              │   └─ RatingBar                   │
         *                                              └────────────────┬─────────────────┘
         *                                                               │
         *                                             bind(root) parcurge arborele
         *                                             și, pentru fiecare android:id,
         *                                             scrie referința în câmpul corespunzător
         *                                                               │
         *                                              ┌────────────────▼─────────────────┐
         *                                              │ ActivityMainBinding              │
         *                                              │   rootView : LinearLayout        │
         *                                              │   main     : LinearLayout ───────┼──▶ același obiect
         *                                              │   button   : Button ─────────────┼──▶ același obiect
         *                                              │   switch1  : Switch ─────────────┼──▶ același obiect
         *                                              │   … 17 câmpuri                   │
         *                                              └──────────────────────────────────┘
         *
         * DIAGRAMA 2 — cum se rezolvă `binding.button` până la view-ul cu id="button":
         *
         * XML:   android:id="@+id/button"
         *               │
         *               ├──────────────────────────────┬─────────────────────────────────────┐
         *               │ aapt2 (BUILD)                │ AGP ViewBinding (BUILD)             │
         *               ▼                              ▼                                     │
         *       R.id.button = 0x7f0800a3       public final Button button;                 │
         *       (int ilustrativ, stabil în APK) (un câmp în clasa generată)                │
         *               │                              │                                     │
         *               └──────────────┬───────────────┘                                     │
         *                              ▼                                                     │
         *               bind(root) la inflate:                                               │
         *                 button = ViewBindings.findChildViewById(root, R.id.button)         │
         *                 if (button == null) throw NullPointerException("Missing …")        │
         *                              │                                                     │
         *                              ▼                                                     │
         *               binding.button ───────────────────────────────────────────────────────┘
         *                 = getfield, O(1), fără nicio căutare în arbore
         */

        // ------------------------------------------------------------------------------
        // PASUL 3 — EDGE-TO-EDGE ȘI ATAȘAREA
        // ------------------------------------------------------------------------------
        // Ordinea contează: întâi edge-to-edge, apoi atașarea, apoi listener-ul de insets.
        //
        // EdgeToEdge.enable(this) setează decorFitsSystemWindows = false, face barele
        // de sistem transparente și aplică scrim-uri (SystemBarStyle.auto) pentru contrast.
        // Rezultatul: conținutul se desenează sub bară, iar tu ești responsabil să îl
        // împingi în zona sigură — exact ce face listener-ul de mai jos.
        //
        // setContentView(binding.getRoot()) înlocuiește setContentView(R.layout.activity_main).
        // getRoot() întoarce LinearLayout-ul rădăcină — exact view-ul care are
        // android:id="@+id/main" în XML.
        //
        // CAPCANA NR. 1: dacă lași și setContentView(R.layout.activity_main) după linia
        // cu binding-ul, Android construiește UN AL DOILEA ARBORE, complet separat. Pe
        // ecran ajunge al doilea; `binding` arată spre primul. Cei șapte listeneri se
        // leagă pe view-uri pe care nu le vede nimeni, iar aplicația pare „moartă" —
        // niciun Toast nu apare. Se întâmplă des la migrarea de la findViewById.
        // ------------------------------------------------------------------------------
        EdgeToEdge.enable(this);                      // 3. fereastra se întinde SUB barele de sistem
        setContentView(binding.getRoot());            // 4. arborele construit ajunge pe ecran

        /*
         * DIAGRAMA 3 — fluxul în doi pași, inflate vs setContentView:
         *
         * PASUL 1 — CONSTRUIREA                         PASUL 2 — ATAȘAREA
         * binding = ActivityMainBinding                 setContentView(binding.getRoot())
         *           .inflate(getLayoutInflater())
         *         │                                             │
         *         ▼                                             ▼
         *   activity_main.xml                            DecorView (fereastra)
         *         │                                             │
         *         ▼                                             ├─ android.R.id.content (FrameLayout)
         *   arbore de View-uri                                  │     │
         *   (neatașat, invizibil,                               │     ▼
         *    fără părinte)                                      │  LinearLayout (root)
         *         │                                             │     ├─ Button
         *         ▼                                             │     ├─ ImageView
         *   ActivityMainBinding                                 │     └─ … copiii
         *   (câmpuri umplute)                                   │
         *                                                       ▼
         *                                              arborele e pe ecran,
         *                                              pregătit pentru measure/layout
         *
         * Între cele două linii: arborele există în heap, cu toate atributele citite,
         * dar nu are părinte și nu e desenat. Un findViewById pe activitate ar returna
         * null, iar binding.button.getWidth() ar returna 0.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: View.OnApplyWindowInsetsListener
        // ------------------------------------------------------------------------------
        // CE OBSERVĂ: insets-urile ferestrei — cât de mult din marginea ecranului e
        //   acoperită de barele de sistem (status, navigare, caption).
        // CÂND SE DECLANȘEAZĂ: la fiecare dispatch de insets, adică la prima așezare
        //   în pagină, la rotire, la schimbarea dimensiunii ferestrei, la deschiderea
        //   tastaturii (dacă ai cere Type.ime()) și la intrarea/ieșirea din multi-window.
        // STIL: lambda — interfața are O SINGURĂ metodă: onApplyWindowInsets(View, WindowInsetsCompat).
        // PARAMETRI: `v` = view-ul pe care e înregistrat listener-ul (rădăcina);
        //            `insets` = WindowInsetsCompat, obiectul cu toate tipurile de insets.
        // RETUR: insets-urile care merg mai departe la copii. `return insets` = nu consuma.
        // ------------------------------------------------------------------------------
        ViewCompat.setOnApplyWindowInsetsListener(binding.getRoot(), (v, insets) -> {
            // a. scoate cele patru dimensiuni ale barelor de sistem, în pixeli
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            // b. aplică-le ca padding pe RĂDĂCINĂ: toți copiii se mută în zona sigură
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            // c. lasă insets-urile să circule mai departe, la copii
            return insets;
        });

        /*
         * DIAGRAMA 4 — padding pe rădăcină vs padding pe copil:
         *
         * VARIANTA CORECTĂ: padding pe rădăcină
         * ┌───────────────────────────────────────────────┐
         * │ ███ status bar ███████████████████████████████ │  ← se desenează PESTE conținut
         * │ ┌───────────────────────────────────────────┐ │
         * │ │ LinearLayout (root)                       │ │
         * │ │   paddingTop    = systemBars.top          │ │
         * │ │   paddingBottom = systemBars.bottom       │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Button                              │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Switch                              │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ … toți copiii, împinși împreună     │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ └───────────────────────────────────────────┘ │
         * │ ███ navigation bar ██████████████████████████ │
         * └───────────────────────────────────────────────┘
         *
         * VARIANTA GREȘITĂ: padding pe un copil
         * ┌───────────────────────────────────────────────┐
         * │ ███ status bar ███████████████████████████████ │
         * │ ┌───────────────────────────────────────────┐ │
         * │ │ LinearLayout (root) — fără padding        │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Button  ← doar el e împins în jos   │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ Switch  ← rămâne sub bară           │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ │   ┌─────────────────────────────────────┐ │ │
         * │ │   │ RatingBar ← rămâne sub bară         │ │ │
         * │ │   └─────────────────────────────────────┘ │ │
         * │ └───────────────────────────────────────────┘ │
         * │ ███ navigation bar ██████████████████████████ │
         * └───────────────────────────────────────────────┘
         *
         * CE FACE FIECARE LINIE DIN LAMBDA:
         *   insets.getInsets(Type.systemBars())  → cele 4 dimensiuni (status + navigare + caption)
         *   v.setPadding(left, top, right, bottom) → le aplică drept padding pe rădăcină
         *   return insets                        → lasă insets-urile să circule la copii
         *
         * return insets, nu CONSUMED: dacă ai întoarce CONSUMED, dispatch-ul s-ar opri
         * la rădăcină și niciun copil nu ar mai primi insets-urile. Aici nu contează,
         * pentru că niciun copil nu le cere, dar e regula generală.
         *
         * CAPCANA NR. 2: setPadding SUPRASCRIE padding-ul din XML, nu îl adună.
         * Rădăcina din DMA05 nu are android:padding, deci nu se pierde nimic. Dacă ar
         * avea 16dp, corect ar fi v.setPadding(16dp + left, 16dp + top, ...).
         *
         * Ce nu acoperă Type.systemBars(): tastatura. Când se deschide un EditText,
         * IME-ul nu e compensat — ar trebui Type.ime() într-un al doilea listener sau
         * în același. În DMA05 câmpurile sunt în partea de sus, deci nu se vede.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: View.OnClickListener
        // ------------------------------------------------------------------------------
        // CE OBSERVĂ: un click — adică un down + up în interiorul limitelor view-ului,
        //   fără ca degetul să fi ieșit din view între timp.
        // CÂND SE DECLANȘEAZĂ: la up, dacă view-ul e clickable și nu e dezactivat.
        //   Se mai declanșează și la performClick() din cod.
        // STIL: clasă anonimă — interfața are o singură metodă, deci lambda ar fi mers.
        //   Alegerea e didactică: vezi mai jos echivalentul lambda.
        // ------------------------------------------------------------------------------
        binding.button.setOnClickListener(new View.OnClickListener() {
            // --------------------------------------------------------------------------
            // METODA: onClick
            // --------------------------------------------------------------------------
            // `v` este view-ul care a primit click-ul — aici, același binding.button.
            // Parametrul există pentru că aceeași instanță de listener poate fi
            // înregistrată pe mai multe view-uri; atunci `v` spune care a fost atins.
            // --------------------------------------------------------------------------
            @Override                                     // suprascriem metoda din interfață
            public void onClick(View v) {                 // `View`, nu `Button`: interfața e declarată pe View
                Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show();
            }
        });

        // ------------------------------------------------------------------------------
        // DE CE MainActivity.this ȘI NU this
        // ------------------------------------------------------------------------------
        // În interiorul clasei anonime, `this` e obiectul listener-ului, nu activitatea.
        // Iar Toast.makeText cere un Context. MainActivity.this e sintaxa prin care ieși
        // din clasa anonimă și ajungi la instanța exterioară. Într-o lambda, `this` se
        // referă la instanța care înconjoară lambda — adică MainActivity — deci
        // MainActivity.this ar fi redundant, dar legal.
        //
        // Echivalentul lambda al blocului întreg (NU există în fișierul real):
        //   binding.button.setOnClickListener(v ->
        //           Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show());
        //
        // ANATOMIA Toast.makeText(...).show():
        //   Toast.makeText(...)   → fabrică statică: construiește obiectul, nu îl afișează
        //   MainActivity.this     → Context-ul: de unde se iau resursele și pachetul
        //   "Button clicked"      → textul, un CharSequence
        //   Toast.LENGTH_SHORT    → durata: ~2 secunde (LENGTH_LONG ≈ 3,5 s)
        //   .show()               → atașează Toast-ul la coada de afișare
        //
        // .show() E OBLIGATORIU: fără el construiești obiectul Toast și îl arunci — pe
        // ecran nu apare nimic. Nu primești excepție, nu primești warning de compilare,
        // nu primești eroare la runtime. Linia
        //   Toast.makeText(this, "x", Toast.LENGTH_SHORT);
        // e perfect validă sintactic și complet inutilă. E cea mai frecventă greșeală
        // „invizibilă" din Android: codul rulează, aplicația nu crapă, feedback-ul lipsește.
        //
        // Ce se întâmplă în spate, când apelezi .show():
        //   Toast.makeText(context, text, duration)
        //      ├── creează un obiect Toast (nu e încă vizibil)
        //      └── .show()
        //            ├── cere serviciului de notificări al sistemului să îl afișeze
        //            ├── sistemul îl pune într-o COADĂ globală (un singur Toast o dată)
        //            ├── fereastra Toast apare deasupra aplicației, fără să blocheze input-ul
        //            └── după durată, dispare singură — nu trebuie să o închizi tu
        //
        // De ce Toast și nu TextView: Toast-ul nu are nevoie de un părinte în layout.
        // Apare într-o fereastră separată (WindowManager, TYPE_TOAST), deasupra
        // aplicației, și dispare singur. Zece Toaste declanșate rapid se afișează
        // secvențial, unul după altul, fiecare ~2 secunde — de aceea un Toast pe fiecare
        // pas de SeekBar produce o coadă de zeci de secunde.
        // ------------------------------------------------------------------------------

        // ------------------------------------------------------------------------------
        // LISTENER: CompoundButton.OnCheckedChangeListener (pe Switch)
        // ------------------------------------------------------------------------------
        // CE OBSERVĂ: starea `checked` a unui CompoundButton — bifat / nebifat.
        // CÂND SE DECLANȘEAZĂ: la atingere ȘI la setChecked(...) din cod.
        // STIL: lambda — interfața are o singură metodă:
        //   onCheckedChanged(CompoundButton buttonView, boolean isChecked)
        // ------------------------------------------------------------------------------
        binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
            // `buttonView` = widget-ul care a produs schimbarea; aici e ignorat.
            // `isChecked`  = NOUA stare, nu cea veche.
            Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        // ------------------------------------------------------------------------------
        // LISTENER: CompoundButton.OnCheckedChangeListener (pe CheckBox)
        // ------------------------------------------------------------------------------
        // Aceeași interfață, alt widget. Semnătura lambda e identică pentru că
        // CheckBox extinde tot CompoundButton.
        // ------------------------------------------------------------------------------
        binding.checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "CheckBox clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        /*
         * DE CE ACEEAȘI INTERFAȚĂ PENTRU DOUĂ WIDGET-URI DIFERITE
         *
         * Switch și CheckBox extind amândouă CompoundButton, care declară
         * setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener). De aceea
         * semnătura lambda e identică: (CompoundButton buttonView, boolean isChecked).
         * Nu tipul widget-ului decide listener-ul, ci CLASA DE BAZĂ.
         *
         * IERARHIA:
         *   View
         *    └── TextView
         *         └── Button
         *              └── CompoundButton          ← declară OnCheckedChangeListener
         *                   ├── CheckBox
         *                   ├── RadioButton
         *                   ├── Switch
         *                   └── ToggleButton
         *
         * "Switch clicked to " + isChecked → concatenarea apelează String.valueOf(boolean),
         * deci textul e ...true sau ...false. Nu ai nevoie de `if`.
         *
         * Listener-ul se declanșează și la schimbări din cod: un setChecked(true) ar
         * produce și el Toast. Consecința practică: dacă într-un onCreate restaurezi
         * starea cu setChecked(...), listener-ul înregistrat ÎNAINTE de restaurare va
         * produce efecte secundare.
         *
         * De ce Switch și nu SwitchCompat: layout-ul folosește <Switch>, clasa din
         * android.widget. SwitchCompat ar fi androidx.appcompat.widget.SwitchCompat.
         * Ambele extind CompoundButton, deci listener-ul e același.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: SeekBar.OnSeekBarChangeListener
        // ------------------------------------------------------------------------------
        // CE OBSERVĂ: trei momente diferite ale interacțiunii cu bara:
        //   1. începutul atingerii
        //   2. fiecare schimbare de valoare
        //   3. sfârșitul atingerii
        // CÂND SE DECLANȘEAZĂ: la fiecare dintre cele trei momente; onProgressChanged
        //   se declanșează și la setProgress(...) din cod, cu fromUser = false.
        // STIL: clasă anonimă — TREI metode abstracte, deci interfața NU e funcțională.
        // ------------------------------------------------------------------------------
        binding.seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            // --------------------------------------------------------------------------
            // METODA 1: onProgressChanged — valoarea s-a schimbat
            // --------------------------------------------------------------------------
            // `seekBar`  = bara care a produs evenimentul
            // `progress` = valoarea NOUĂ, între 0 și android:max (implicit 100)
            // `fromUser` = true dacă schimbarea vine de la deget, false dacă vine din cod
            // --------------------------------------------------------------------------
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                Toast.makeText(MainActivity.this, "Progress changed to " + progress, Toast.LENGTH_SHORT).show();
            }

            // --------------------------------------------------------------------------
            // METODA 2: onStartTrackingTouch — degetul a atins bara
            // --------------------------------------------------------------------------
            // Se apelează O SINGURĂ DATĂ, la începutul tragerii, înainte de prima
            // schimbare de valoare. Corp gol: nu avem ce face la început.
            // --------------------------------------------------------------------------
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            // --------------------------------------------------------------------------
            // METODA 3: onStopTrackingTouch — degetul s-a ridicat
            // --------------------------------------------------------------------------
            // Se apelează O SINGURĂ DATĂ, la sfârșitul tragerii. Aici s-ar salva
            // valoarea finală într-o bază de date sau într-un ViewModel — nu la fiecare
            // pas. Corp gol: DMA05 nu salvează nimic.
            // --------------------------------------------------------------------------
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });

        /*
         * DE CE AICI NU MERGE LAMBDA
         *
         * SeekBar.OnSeekBarChangeListener are TREI metode abstracte. O interfață
         * funcțională are exact una. Cu trei, ești obligat la clasă anonimă care să le
         * implementeze pe toate. Compilatorul nu are cum să ghicească ce să pună în
         * celelalte două metode.
         *
         * CELE TREI MOMENTE:
         *   onProgressChanged     → la fiecare schimbare de valoare
         *   onStartTrackingTouch  → când degetul atinge bara
         *   onStopTrackingTouch   → când degetul se ridică
         *
         * De ce trei și nu una: „valoarea s-a schimbat" nu e același lucru cu
         * „utilizatorul interacționează". onProgressChanged poate veni din cod
         * (setProgress), din animație sau din deget. Celelalte două izolează gestul.
         *
         * `fromUser` e true când schimbarea vine de la utilizator și false când vine
         * din setProgress(...). Aici e ignorat — Toast-ul apare în ambele cazuri.
         * Corect ar fi `if (fromUser) { ... }`.
         *
         * Corpurile goale sunt legale și obligatorii. Trebuie să implementezi toate
         * cele trei metode; dacă nu ai ce face într-una, o lași goală. Dacă uiți una,
         * fișierul nu compilează: clasa anonimă ar fi abstractă.
         *
         * progress merge de la 0 la android:max. În XML nu există android:max, deci
         * valoarea implicită e 100. Fără android:progress, valoarea inițială e 0.
         *
         * DEFECTUL DIDACTIC: un Toast pentru fiecare pas înseamnă zeci de Toaste la o
         * singură tragere, puse în coadă. În ItemActivity (G1097) același listener scrie
         * într-un TextView — comportamentul corect.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: RadioGroup.OnCheckedChangeListener
        // ------------------------------------------------------------------------------
        // CE OBSERVĂ: selecția grupului — care RadioButton e bifat.
        // CÂND SE DECLANȘEAZĂ: când un copil devine bifat, fie la atingere, fie la
        //   check(...) din cod. Se declanșează și cu checkedId = -1 după clearCheck().
        // STIL: clasă anonimă — interfața are o singură metodă, deci lambda ar fi mers.
        //   Din nou, alegere didactică: repo-ul alternează stilurile.
        // ------------------------------------------------------------------------------
        binding.radioGroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {

            // --------------------------------------------------------------------------
            // METODA: onCheckedChanged
            // --------------------------------------------------------------------------
            // `group`     = grupul care a produs evenimentul
            // `checkedId` = ID-ul de RESURSĂ al butonului bifat (R.id.radioButton1 sau
            //               R.id.radioButton2), NU indexul lui (0 / 1) și NU obiectul.
            //               Poate fi -1 dacă nu e bifat nimic.
            // --------------------------------------------------------------------------
            @Override
            public void onCheckedChanged(@NonNull RadioGroup group, int checkedId) {
                // transformă ID-ul primit la runtime în obiectul RadioButton
                RadioButton selected = group.findViewById(checkedId);
                Toast.makeText(MainActivity.this, "Radio button clicked " + selected.getText(), Toast.LENGTH_SHORT).show();
            }
        });

        /*
         * checkedId E UN ID DE RESURSĂ, NU UN INDEX ȘI NU OBIECTUL
         *
         * Valoarea e R.id.radioButton1 sau R.id.radioButton2 — un int generat de aapt2,
         * stabil în APK. Confuzia „e poziția" e frecventă și duce la findViewById(0),
         * care întoarce null.
         *
         * De ce group.findViewById(checkedId) și nu findViewById(checkedId): căutarea
         * se face în subarborele grupului. Aici ar funcționa și varianta pe activitate,
         * pentru că ID-urile sunt unice în layout — dar forma cu `group` e cea corectă
         * conceptual: cauți în containerul care știe de butoane.
         *
         * Acesta e singurul findViewById care supraviețuiește cu ViewBinding. Binding-ul
         * îți dă binding.radioButton1 și binding.radioButton2, dar nu are cum să
         * transforme un int primit la runtime într-un câmp. Alternativa:
         *   RadioButton selected = checkedId == R.id.radioButton1
         *           ? binding.radioButton1
         *           : binding.radioButton2;
         *
         * De ce RadioGroup.OnCheckedChangeListener are o singură metodă, dar tot clasă
         * anonimă: din nou, stil alternat. Lambda ar fi perfect validă.
         *
         * ATENȚIE LA NUMELE METODEI: și CompoundButton, și RadioGroup au
         * setOnCheckedChangeListener, dar cu interfețe diferite. Nu e nici suprascriere,
         * nici supraîncărcare: sunt două metode declarate în două clase fără relație de
         * moștenire (RadioGroup extinde LinearLayout, nu CompoundButton). Se alege după
         * tipul receptorului.
         *
         * @NonNull vine din androidx.annotation. Nu schimbă comportamentul la runtime —
         * e contract pentru lint și pentru cititor: „grupul nu e niciodată null".
         *
         * CAPCANA NR. 3: dacă checkedId ar fi -1 (se întâmplă după clearCheck()),
         * findViewById(-1) întoarce null și selected.getText() aruncă NPE. În DMA05 nu
         * se apelează clearCheck(), deci nu se întâmplă. În G1097, primul buton are
         * android:checked="true" tocmai ca să nu existe niciodată „niciunul selectat".
         *
         * De ce selected.getText() și nu selected: RadioButton e un View; concatenarea
         * unui View ar apela toString(), care întoarce numele clasei plus hash.
         */

        // ------------------------------------------------------------------------------
        // LISTENER: CompoundButton.OnCheckedChangeListener (pe ToggleButton)
        // ------------------------------------------------------------------------------
        // Al treilea widget cu aceeași interfață. Dovada că listener-ul vine din
        // clasa de bază, nu din tipul concret al widget-ului.
        // ------------------------------------------------------------------------------
        binding.toggleButton.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "Toggle button clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });

        // ------------------------------------------------------------------------------
        // LISTENER: RatingBar.OnRatingBarChangeListener
        // ------------------------------------------------------------------------------
        // CE OBSERVĂ: valoarea stelelor — un `float`, nu un `int`.
        // CÂND SE DECLANȘEAZĂ: la atingere ȘI la setRating(...) din cod.
        // STIL: lambda — interfața are o singură metodă:
        //   onRatingChanged(RatingBar ratingBar, float rating, boolean fromUser)
        // ------------------------------------------------------------------------------
        binding.ratingBar.setOnRatingBarChangeListener((ratingBar, rating, fromUser) -> {
            // `rating` e float pentru că android:stepSize="0.5" → 0.0, 0.5, 1.0, …
            // `fromUser` are același sens ca la SeekBar.
            Toast.makeText(MainActivity.this, "Rating changed to " + rating, Toast.LENGTH_SHORT).show();
        });


    }                                                     // sfârșitul lui onCreate
}                                                         // sfârșitul clasei MainActivity

/*
 * ======================================================================================
 * FAMILIILE DE LISTENERI — REGULA CARE DECIDE STILUL
 * ======================================================================================
 *
 *                 interfața are o singură metodă abstractă?
 *                               │
 *               ┌───────────────┴────────────────┐
 *              DA                                NU
 *               │                                 │
 *               ▼                                 ▼
 *       LAMBDA PERMISĂ                  CLASĂ ANONIMĂ OBLIGATORIE
 *       ─────────────                   ─────────────────────────
 *       View.OnClickListener            SeekBar.OnSeekBarChangeListener
 *         onClick(View)                   onProgressChanged(SeekBar, int, boolean)
 *                                         onStartTrackingTouch(SeekBar)
 *       CompoundButton.OnChecked...       onStopTrackingTouch(SeekBar)
 *         onCheckedChanged(CompoundButton, boolean)
 *                                       TextWatcher (nefolosit în DMA05)
 *       RadioGroup.OnChecked...           beforeTextChanged(CharSequence, int, int, int)
 *         onCheckedChanged(RadioGroup, int) onTextChanged(CharSequence, int, int, int)
 *                                         afterTextChanged(Editable)
 *       RatingBar.OnRatingBar...
 *         onRatingChanged(RatingBar, float, boolean)
 *
 *       View.OnApplyWindowInsets...
 *         onApplyWindowInsets(View, WindowInsetsCompat)
 *
 * REGULA, ÎNTR-O PROPOZIȚIE: o singură metodă abstractă → lambda permisă; două sau
 * mai multe → clasă anonimă obligatorie. Stilul din repo alternează deliberat, ca să
 * vezi ambele forme pe aceeași interfață (button e clasă anonimă, deși ar fi putut
 * fi lambda).
 *
 * CRONOLOGIA DECLANȘĂRII:
 *
 *   BUTTON (click)
 *     ACTION_DOWN ──▶ ACTION_UP ──▶ performClick() ──▶ onClick(v)
 *     (dacă degetul iese din view între down și up, click-ul NU se declanșează)
 *
 *   SWITCH / CHECKBOX / TOGGLEBUTTON (checked)
 *     atingere ──▶ toggle() ──▶ setChecked(!checked) ──▶ onCheckedChanged(view, isChecked)
 *     SAU setChecked(true) din cod ──▶ onCheckedChanged(view, true)
 *
 *   SEEKBAR (3 momente)
 *     ACTION_DOWN ──▶ onStartTrackingTouch(bar)
 *     ACTION_MOVE ──▶ onProgressChanged(bar, val, true)   ← de multe ori
 *     ACTION_UP   ──▶ onStopTrackingTouch(bar)
 *     SAU setProgress(50) din cod ──▶ onProgressChanged(bar, 50, false)
 *
 *   RADIOGROUP (selecție)
 *     atingere pe un RadioButton
 *       └── copilul se bifează
 *             └── grupul debifează ceilalți copii
 *                   └── onCheckedChanged(group, R.id.radioButtonN)   ← o singură dată
 *     SAU clearCheck() ──▶ onCheckedChanged(group, -1)   ← capcana nr. 3
 *
 *   RATINGBAR (valoare float)
 *     atingere pe stele ──▶ onRatingChanged(bar, rating, true)
 *     SAU setRating(3.5f) ──▶ onRatingChanged(bar, 3.5f, false)
 *
 * CE AU TOATE ÎN COMUN: listener-ul se declanșează DUPĂ ce starea s-a schimbat, nu
 * înainte. Când intri în onCheckedChanged, isChecked e deja noua valoare; când intri
 * în onProgressChanged, progress e deja noua valoare. Nu trebuie să citești starea
 * din widget — o primești ca parametru.
 *
 * CE DIFERĂ: numărul de evenimente per gest. Un click = un eveniment. O tragere de
 * SeekBar = un start, N progress, un stop. O bifă = un eveniment. De aceea SeekBar
 * are nevoie de trei metode, iar CheckBox de una.
 *
 * CE ÎNSEAMNĂ „INTERFAȚĂ FUNCȚIONALĂ" ÎN JAVA: o interfață cu exact o metodă
 * abstractă. Poate avea oricâte metode default și static, dar o singură metodă fără
 * implementare. View.OnClickListener are onClick abstractă și nimic altceva.
 * SeekBar.OnSeekBarChangeListener are trei metode abstracte, deci nu e funcțională.
 *
 * DE CE LAMBDA NU ARE NEVOIE DE new: expresia lambda ESTE implementarea metodei
 * abstracte. Compilatorul generează o clasă (sau un invokedynamic) și știe ce metodă
 * să lege pentru că există doar una. Când sunt trei, nu are cum să ghicească.
 *
 * LA RUNTIME: lambda care nu capturează variabile e un singleton. Lambda care
 * capturează (MainActivity.this e capturat implicit) alocă o instanță o singură dată,
 * la înregistrare. Costul e neglijabil, dar există.
 */
```

### După cod: cele șapte familii, într-un tabel

| # | Linia | Widget | Metodă de înregistrare | Interfață | Metode | Stil |
|---|---|---|---|---|---|---|
| 1 | 38 | `button` | `setOnClickListener` | `View.OnClickListener` | 1 | clasă anonimă |
| 2 | 45 | `switch1` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 3 | 49 | `checkBox` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 4 | 53 | `seekBar` | `setOnSeekBarChangeListener` | `SeekBar.OnSeekBarChangeListener` | **3** | clasă anonimă |
| 5 | 70 | `radioGroup` | `setOnCheckedChangeListener` | `RadioGroup.OnCheckedChangeListener` | 1 | clasă anonimă |
| 6 | 78 | `toggleButton` | `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | lambda |
| 7 | 82 | `ratingBar` | `setOnRatingBarChangeListener` | `RatingBar.OnRatingBarChangeListener` | 1 | lambda |

### Harta liniilor din fișier

| Linii | Ce conține |
|---|---|
| 1–17 | `package` + cele 15 importuri (3 grupuri) |
| 19–21 | clasa `MainActivity` + câmpul `binding` |
| 23–24 | antetul lui `onCreate` |
| 25 | `super.onCreate(savedInstanceState)` |
| 27 | `ActivityMainBinding.inflate(getLayoutInflater())` |
| 29–30 | `EdgeToEdge.enable(this)` + `setContentView(binding.getRoot())` |
| 31–35 | listener-ul de insets (lambda) |
| 38–43 | `button` — `View.OnClickListener` (clasă anonimă) |
| 45–47 | `switch1` — `CompoundButton.OnCheckedChangeListener` (lambda) |
| 49–51 | `checkBox` — aceeași interfață (lambda) |
| 53–68 | `seekBar` — `SeekBar.OnSeekBarChangeListener` (3 metode, clasă anonimă) |
| 70–76 | `radioGroup` — `RadioGroup.OnCheckedChangeListener` (clasă anonimă) |
| 78–80 | `toggleButton` — `CompoundButton.OnCheckedChangeListener` (lambda) |
| 82–84 | `ratingBar` — `RatingBar.OnRatingBarChangeListener` (lambda) |
| 87–88 | închiderea lui `onCreate` și a clasei |

**Cum se folosește harta:** dacă vrei să modifici un singur comportament, sari direct la liniile lui. Dacă vrei să înțelegi fluxul, citește 23–35 (construcție + insets), apoi 38–84 (listenerii, în ordinea din fișier). Restul sunt importuri și acolade.

### Ce nu are listener — și de ce

Șapte widget-uri au listener. Restul nu:

| View | De ce nu | Ce s-ar folosi dacă ai vrea |
|---|---|---|
| `imageView` | doar afișare | `setOnClickListener` (orice `View` îl are) |
| cele 5 `EditText` | se citesc la nevoie, nu la tastare | `addTextChangedListener(new TextWatcher(){...})` — **3 metode**, deci clasă anonimă |
| `progressBar` | e demonstrativ, rămâne la 0 | `setProgress(int)` din cod |
| `radioButton1/2` | grupul le acoperă | listener pe fiecare buton, rar util |

**`TextWatcher` e celălalt exemplu de interfață cu trei metode** pe care îl întâlnești des, lângă `SeekBar.OnSeekBarChangeListener`. Dacă la test ți se cere „reacționează când utilizatorul tastează", răspunsul e `TextWatcher` cu `beforeTextChanged`, `onTextChanged`, `afterTextChanged`.

**De ce `EditText`-urile nu au listener aici:** DMA05 nu are unde să ducă valoarea. Nu există buton de salvare, nu există model, nu există bază de date. Un `TextWatcher` ar produce Toaste la fiecare tastă — și mai rău decât la `SeekBar`.

---

## 27.2 `activity_main.xml` — fișierul întreg, adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FIȘIER: activity_main.xml
  ======================================================================================
  LOCAȚIE: DMA05/src/main/res/layout/activity_main.xml
  ROL:     singurul layout al aplicației. Un LinearLayout vertical cu 14 copii direcți,
           care acoperă toate widget-urile de input uzuale.
  ID-URI:  17 (rădăcina + 16 copii sau descendenți)
  FOLOSITE ÎN COD: 7 (button, switch1, checkBox, seekBar, radioGroup, toggleButton, ratingBar)
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: INFLATE → MEASURE → LAYOUT → DRAW
  ======================================================================================
  1. INFLATE (build + runtime)
     La build: aapt2 compilează XML-ul într-un format binar și generează R.id.*.
     La runtime: LayoutInflater parsează XML-ul binar și creează obiectele Java.
     Fiecare tag devine un obiect; fiecare atribut android:* devine o valoare în
     AttributeSet, citită de constructor.

  2. MEASURE
     Părintele întreabă fiecare copil: „cât de mare vrei să fii?"
     Răspunsul depinde de MeasureSpec, care are două componente: mod + dimensiune.
       EXACTLY   → dimensiunea e impusă (match_parent sau valoare fixă)
       AT_MOST   → copilul poate fi oricât, dar nu mai mult decât atât (wrap_content)
       UNSPECIFIED → fără constrângeri (ScrollView pe verticală)
     Rezultatul: getMeasuredWidth() / getMeasuredHeight().

  3. LAYOUT
     Părintele decide poziția fiecărui copil: left, top, right, bottom.
     LinearLayout vertical: fiecare copil primește top = bottom-ul copilului anterior.
     Rezultatul: getLeft(), getTop(), getWidth(), getHeight().

  4. DRAW
     Fiecare view își desenează conținutul: fundal, text, imagini, copii.
     Aici apare primul pixel pe ecran.

  DE CE CONTEAZĂ:
     - match_parent pe lățime + wrap_content pe înălțime = rând de formular.
     - Un LinearLayout fără ScrollView nu poate fi derulat pe verticală: măsoară
       copiii cu AT_MOST pe înălțimea ecranului, iar ce nu încape e tăiat.
     - setPadding în listener-ul de insets se aplică ÎNAINTE de measure, deci
       schimbă măsurătoarea, nu doar desenarea.
  ======================================================================================
-->

<!--
  RĂDĂCINA — LinearLayout vertical.
  DE CE LinearLayout și nu ConstraintLayout: pentru 14 copii stivuiți vertical,
    LinearLayout e suficient și mai simplu. ConstraintLayout ar fi adăugat constrângeri
    pentru fiecare copil, fără beneficiu.
  DE CE vertical: copiii se stivuiesc de sus în jos, unul sub altul.
  DE CE nu ScrollView: pe un ecran mic, ultimele widget-uri (SeekBar, RatingBar) pot
    ieși din zona vizibilă. G1097 învelește formularul într-un ScrollView exact din
    acest motiv.

  ATRIBUTE, PE RÂND:
    xmlns:android   → atributele framework-ului
    xmlns:app       → atributele bibliotecilor (aici, app:srcCompat de pe ImageView)
    xmlns:tools     → atribute care există DOAR în preview și sunt eliminate la build
    android:id      → @+id/main; rădăcina are ID, deci binding.main există, dar codul
                      folosește binding.getRoot()
    layout_width    → match_parent: umple fereastra
    layout_height   → match_parent: umple fereastra
    orientation     → vertical
    tools:context   → doar pentru preview; îi spune lui Android Studio ce activitate
                      să simuleze. Eliminat la build.

  Spațiul de dinaintea lui `>` (tools:context=".MainActivity" >) e în fișierul real.
  XML-ul îl ignoră. Nu îl „repara" — codul trebuie să rămână byte-identic.
-->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity" >

    <!--
      BUTTON — primul copil; singurul cu click listener.
        android:id="@+id/button"              → câmpul binding.button (tip Button)
        android:layout_width="match_parent"   → lat cât părintele (toată coloana)
        android:layout_height="wrap_content"  → înalt cât textul + padding-ul implicit
        android:text="Button"                 → eticheta; hardcodată, nu din strings.xml

      match_parent pe lățime + wrap_content pe înălțime = rând de formular.
      android:text e hardcodat; lint dă warning HardcodedText. strings.xml conține doar
      app_name — DMA05 e laborator, nu produs.
    -->
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Button" />

    <!--
      IMAGEVIEW — al doilea copil; fără listener, doar afișare.
        android:id="@+id/imageView"           → câmpul binding.imageView
        app:srcCompat="@drawable/…"           → vectorul, prin AppCompat (nu android:src)
        layout_height="wrap_content"          → înălțimea intrinsică a drawable-ului

      app:srcCompat și nu android:src: varianta AppCompat, necesară pentru VectorDrawable
      pe API-uri vechi și pentru app:tint. Fișierul ic_android_black_24dp.xml e un vector.
      ImageView nu are listener — e contraexemplul care arată că „fiecare widget are
      listener" e fals.
    -->
    <ImageView
        android:id="@+id/imageView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        app:srcCompat="@drawable/ic_android_black_24dp" />

    <!--
      SWITCH — al treilea copil; CompoundButton, listener de bifă.
        android:id="@+id/switch1"             → câmpul binding.switch1 (nu `switch`)
        android:text="Switch"                 → eticheta din stânga, nu starea
        fără android:checked                  → pornește oprit

      De ce ID-ul e switch1 și nu switch: generatorul de layout din Android Studio
      construiește ID-ul din numele widget-ului și adaugă un număr când numele simplu
      nu e disponibil. Codul îl folosește exact așa: binding.switch1.
    -->
    <Switch
        android:id="@+id/switch1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Switch" />

    <!--
      EDITTEXT #1 — text liber.
        android:id="@+id/editTextText"        → câmpul binding.editTextText
        android:ems="10"                      → lățime minimă de 10 em-uri (ignorată de match_parent)
        android:inputType="text"              → TYPE_CLASS_TEXT: QWERTY, fără filtrare
        android:hint="Text"                   → placeholder, dispare la prima tastă

      android:ems="10" — „lățimea a 10 caractere M". Cu layout_width="match_parent",
      MeasureSpec-ul e EXACTLY pe lățime, deci ems e ignorat. Rămâne ca rămășiță.
      android:hint NU e valoare: getText() întoarce "", nu hint-ul. Hint-ul e desenat
      de TextView-ul însuși, doar cât timp textul e gol.
    -->
    <EditText
        android:id="@+id/editTextText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:inputType="text"
        android:hint="Text" />

    <!--
      EDITTEXT #2 — parolă.
        android:id="@+id/editTextTextPassword" → câmpul binding.editTextTextPassword
        android:inputType="textPassword"       → mascare cu puncte + sugestii oprite
        android:hint="Password"                → placeholder; NU e valoare

      Mascarea e doar vizuală: textul real rămâne în getText() și ajunge în Bundle la
      rotire dacă nu dezactivezi salvarea stării. Pentru un laborator e suficient.
    -->
    <EditText
        android:id="@+id/editTextTextPassword"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Password"
        android:inputType="textPassword" />

    <!--
      EDITTEXT #3 — email.
        android:id="@+id/editTextTextEmailAddress" → câmpul binding.editTextTextEmailAddress
        android:inputType="textEmailAddress"       → tastatură cu @ și ., fără validare
        android:hint="Email"                       → placeholder

      inputType nu validează: poți tasta abc fără @. IME-ul poate oferi sugestii de
      adrese, dar câmpul acceptă orice.
    -->
    <EditText
        android:id="@+id/editTextTextEmailAddress"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Email"
        android:inputType="textEmailAddress" />

    <!--
      EDITTEXT #4 — oră.
        android:id="@+id/editTextTime"        → câmpul binding.editTextTime
        android:inputType="time"              → tastatură numerică + separator oră
        android:hint="Time"                   → placeholder

      Tastatura e numerică cu `:`; filtrul acceptă cifre și separatori, dar acceptă
      și 99:99. Validarea formatului rămâne treaba codului.
    -->
    <EditText
        android:id="@+id/editTextTime"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Time"
        android:inputType="time" />

    <!--
      EDITTEXT #5 — dată.
        android:id="@+id/editTextDate"        → câmpul binding.editTextDate
        android:inputType="date"              → tastatură numerică + separator dată
        android:hint="Date"                   → placeholder

      Tastatura e numerică cu `/`; acceptă și 99/99/9999. inputType e un contract cu
      tastatura, nu cu datele.
    -->
    <EditText
        android:id="@+id/editTextDate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ems="10"
        android:hint="Date"
        android:inputType="date" />

    <!--
      CHECKBOX — 0..n alegeri independente.
        android:id="@+id/checkBox"            → câmpul binding.checkBox
        android:text="CheckBox"               → eticheta din dreapta
        fără android:checked                  → pornește nebifat
    -->
    <CheckBox
        android:id="@+id/checkBox"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="CheckBox" />

    <!--
      RADIOGROUP — containerul impune excluderea reciprocă între copii.
        android:id="@+id/radioGroup"          → câmpul binding.radioGroup
        fără android:orientation              → implicit vertical
        fără android:checkedButton            → niciun buton bifat la pornire

      CheckBox = 0..n alegeri independente. RadioGroup = exact 0 sau 1. Doi RadioButton
      fără un RadioGroup în jur s-ar comporta ca niște checkbox-uri — asta e tot rolul
      containerului. RadioGroup extinde LinearLayout, deci are orientation, gravity și
      layout_weight pentru copii.
    -->
    <RadioGroup
        android:id="@+id/radioGroup"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" >

        <!--
          OPȚIUNEA 1.
            android:id="@+id/radioButton1"    → R.id.radioButton1, valoarea din checkedId
            android:text="First Option"       → textul returnat de getText()
        -->
        <RadioButton
            android:id="@+id/radioButton1"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="First Option" />

        <!--
          OPȚIUNEA 2.
            android:id="@+id/radioButton2"    → R.id.radioButton2, valoarea din checkedId
            android:text="Second Option"      → textul returnat de getText()

          Copiii au ID-uri, deci binding.radioButton1 și binding.radioButton2 există.
          Codul nu le folosește — trece prin group.findViewById(checkedId). Ambele căi
          sunt valide.
        -->
        <RadioButton
            android:id="@+id/radioButton2"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Second Option" />

    </RadioGroup>

    <!--
      TOGGLEBUTTON — buton cu două stări.
        android:id="@+id/toggleButton"        → câmpul binding.toggleButton
        android:text="ToggleButton"           → eticheta stării ON; OFF e implicit "OFF"
        fără android:textOn / textOff         → de unde inconsecvența ON/OFF
    -->
    <ToggleButton
        android:id="@+id/toggleButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="ToggleButton" />

    <!--
      PROGRESSBAR — demonstrativ, rămâne la 0.
        android:id="@+id/progressBar"         → câmpul binding.progressBar
        style="?android:attr/progressBarStyleHorizontal" → bară, nu cerc
        fără android:progress                 → valoarea implicită 0

      Fără style, ar fi cercul care se învârte la infinit. ?android:attr/... înseamnă
      „atributul din tema platformei", nu din tema aplicației.
    -->
    <ProgressBar
        android:id="@+id/progressBar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <!--
      SEEKBAR — bară glisantă.
        android:id="@+id/seekBar"             → câmpul binding.seekBar
        fără android:max                      → maximul implicit 100
        fără android:progress                 → valoarea inițială 0

      SeekBar extinde ProgressBar (prin AbsSeekBar), de aceea are getProgress() și
      setProgress(int). Diferența: adaugă degetul și cele trei evenimente de atingere.
    -->
    <SeekBar
        android:id="@+id/seekBar"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <!--
      RATINGBAR — 5 stele, pas de 0.5.
        android:id="@+id/ratingBar"           → câmpul binding.ratingBar
        android:numStars="5"                  → 5 stele
        android:stepSize="0.5"                → jumătăți de stea → valoare float
        android:layout_gravity="center_horizontal" → centrat pe orizontală
        layout_width="wrap_content"           → lată cât stelele, nu cât ecranul

      RatingBar extinde AbsSeekBar, deci e și ea un ProgressBar cu getProgress().
      Valoarea implicită e 0, deci nicio stea aprinsă la pornire.
    -->
    <RatingBar
        android:id="@+id/ratingBar"
        android:numStars="5"
        android:layout_gravity="center_horizontal"
        android:stepSize="0.5"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
</LinearLayout>
```

### După cod: inventarul widget-urilor

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

**17 ID-uri, 7 folosite în cod.** Celelalte 10 produc câmpuri în `ActivityMainBinding` pe care nimeni nu le atinge — și e perfect normal: binding-ul le generează pe toate, indiferent dacă le folosești. ID-urile în plus costă doar câte o referință per câmp, umplută o dată la `inflate`. În plus, ID-urile sunt necesare pentru **restaurarea stării** la rotire: fără ID, un widget nu își salvează starea.

### Cele 14 copii direcți, pe rând

| # | Widget | Ce este, într-o propoziție |
|---|---|---|
| 1 | `Button` | buton cu text; singurul view din layout care primește `setOnClickListener` |
| 2 | `ImageView` | afișează un vector; nu reacționează la nimic, e decor |
| 3 | `Switch` | comutator glisant on/off; `CompoundButton`, ca `CheckBox` |
| 4 | `EditText` (`text`) | câmp liber, tastatură QWERTY, fără filtrare |
| 5 | `EditText` (`textPassword`) | câmp mascat cu puncte, fără sugestii |
| 6 | `EditText` (`textEmailAddress`) | tastatură cu `@` și `.`, dar acceptă orice text |
| 7 | `EditText` (`time`) | tastatură numerică cu `:`; acceptă și „99:99" |
| 8 | `EditText` (`date`) | tastatură numerică cu `/`; acceptă și „99/99/9999" |
| 9 | `CheckBox` | bifă independentă; 0..n astfel de bife |
| 10 | `RadioGroup` | container cu doi `RadioButton`; impune exact 0 sau 1 selecție |
| 11 | `ToggleButton` | buton cu două stări; textul din XML e eticheta ON |
| 12 | `ProgressBar` | bară orizontală demonstrativă; rămâne la 0 |
| 13 | `SeekBar` | bară glisantă 0..100; singura cu trei evenimente |
| 14 | `RatingBar` | cinci stele cu pas de 0.5; valoare `float` |

**De ce tocmai aceste 14:** sunt inventarul widget-urilor de input pe care le cer exercițiile de test. Fiecare apare o singură dată, ca să poți compara comportamentele: trei `CompoundButton` (`Switch`, `CheckBox`, `ToggleButton`), două bare (`ProgressBar`, `SeekBar`), o singură familie de selecție exclusivă (`RadioGroup` + `RadioButton`), cinci variații de `EditText`.

### `inputType` — tabelul complet

| Valoare | Constanta Android | Tastatura afișată | Restricționează? | Validează? |
|---|---|---|---|---|
| `text` | `TYPE_CLASS_TEXT` | QWERTY normală | nu | nu |
| `textPassword` | `TYPE_CLASS_TEXT \| TYPE_TEXT_VARIATION_PASSWORD` | QWERTY, fără sugestii | **da** — mascare cu puncte, fără auto-correct | nu |
| `textEmailAddress` | `TYPE_CLASS_TEXT \| TYPE_TEXT_VARIATION_EMAIL_ADDRESS` | QWERTY cu `@` și `.` | **nu** — doar optimizează tastatura | nu |
| `time` | `TYPE_CLASS_DATETIME \| TYPE_DATETIME_VARIATION_TIME` | cifre și `:` | parțial — filtrează la cifre și separatori | nu |
| `date` | `TYPE_CLASS_DATETIME \| TYPE_DATETIME_VARIATION_DATE` | cifre și `/` | parțial — filtrează la cifre și separatori | nu |

> **`inputType` nu validează.** Poți tasta un email fără `@` într-un câmp `textEmailAddress` și o oră „99:99" într-un câmp `time`. Validarea e treaba ta, în cod. `inputType` e un **contract cu tastatura**, nu cu datele.

### Cele trei canale prin care XML-ul ajunge în cod

```
activity_main.xml
      │
      ├── CANALUL 1: android:id ──────────────▶ ViewBinding (BUILD)
      │     @+id/button                         → public final Button button;
      │                                         → binding.button
      │     legătură verificată la compilare
      │
      ├── CANALUL 2: atribute de comportament ─▶ widget-ul (RUNTIME)
      │     android:inputType="time"            → setInputType(...) în constructor
      │     android:max="100"                   → setMax(100)
      │     android:checked="true"              → setChecked(true)
      │     android:hint="Time"                 → setHint("Time")
      │     legătură citită la inflate, nu verificată de tine
      │
      └── CANALUL 3: stil și temă ─────────────▶ aspectul (RUNTIME)
            ?android:attr/progressBarStyleHorizontal → stilul barei
            Theme.DMA05                        → culori, tipografie, forme
            legătură prin atribute ?attr/... și style=
```

**Canalul 1 e singurul verificat de compilator.** Dacă schimbi `android:id` în XML și uiți să schimbi codul, build-ul pică la `binding.vechiulId`. De aceea `ViewBinding` e considerat „type-safe": legătura e mecanică, nu textuală.

**Canalul 2 nu e verificat de nimeni.** `android:inputType="time"` produce un comportament la runtime, dar nimeni nu te oprește să citești valoarea ca `int` și să crapi la parsare. Atributele sunt citite de constructorul widget-ului din `AttributeSet`, la inflate.

**Canalul 3 e cel mai invizibil.** `?android:attr/progressBarStyleHorizontal` rezolvă un atribut din tema platformei. Dacă tema s-ar schimba, bara ar arăta altfel, fără nicio modificare în XML sau Java.

---

## 27.3 `AndroidManifest.xml` — fișierul întreg, adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FIȘIER: AndroidManifest.xml
  ======================================================================================
  LOCAȚIE: DMA05/src/main/AndroidManifest.xml
  ROL:     declară aplicația, tema și singura activitate. Fără el, iconița nu pornește.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: MANIFESTUL
  ======================================================================================
  1. CE ESTE
     Un fișier XML care declară aplicația către sistemul de operare, ÎNAINTE de a rula
     vreo linie de Java. Sistemul îl citește la instalare și la pornirea unei componente.

  2. CINE ÎL FOLOSEȘTE
     - la instalare: ce permisiuni cere aplicația, ce componente are
     - la lansare: care e activitatea de start (intent-filter MAIN + LAUNCHER)
     - la navigare: ce activități pot fi pornite din alte aplicații (exported)
     - la runtime: ce temă are aplicația, ce mod de soft input are activitatea

  3. MANIFEST MERGER
     La build, AGP combină manifestul tău cu manifestele bibliotecilor (AppCompat,
     Material, activity-ktx). Fiecare bibliotecă își declară componentele și
     permisiunile. Rezultatul e un singur manifest, în APK.
     Atributele tools: rezolvă conflictele:
       tools:node="merge"     → combină
       tools:node="replace"   → înlocuiește
       tools:node="remove"    → elimină
     DMA05 nu are conflicte, deci nu folosește tools: în manifest.

  4. ATRIBUTELE DIN <application>
     android:allowBackup="true"          → sistemul poate salva datele aplicației
     android:dataExtractionRules         → regulile de backup pentru Android 12+
     android:fullBackupContent           → regulile de backup pentru versiunile vechi
     android:icon / roundIcon            → iconițele
     android:label="@string/app_name"    → numele din launcher
     android:supportsRtl="true"          → suport pentru scriere de la dreapta la stânga
     android:theme="@style/Theme.DMA05"  → tema aplicației

  5. ATRIBUTELE DIN <activity>
     android:name=".MainActivity"        → clasa; punctul înseamnă namespace-ul aplicației
     android:exported="true"             → poate fi pornită din exterior (necesar launcher)
     android:windowSoftInputMode="adjustResize" → modul de reacție la tastatură

  6. INTENT-FILTER
     <action android:name="android.intent.action.MAIN" />
     <category android:name="android.intent.category.LAUNCHER" />
     Combinația MAIN + LAUNCHER e ce face activitatea să apară în launcher.
     Fără ea, activitatea există, dar nu e pornită de nimeni.

  7. CE NU ARE DMA05
     - niciun <uses-permission>          → nu accesează nimic protejat
     - niciun <service>, <receiver>      → o singură activitate
     - niciun atribut package            → vine din namespace (AGP 8+)
  ======================================================================================
-->

<!--
  Nu există atribut `package`: din AGP 8, pachetul vine din
  namespace = "ro.ase.ie.dma05" în build.gradle.kts. Dacă ai lăsa package, build-ul
  ar eșua cu un mesaj care spune că atributul nu mai e suportat în manifestul sursă.
  namespace e folosit și pentru R și pentru clasa generată databinding.
-->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!--
      <application> — tot ce ține de aplicație în ansamblu.
        allowBackup + dataExtractionRules + fullBackupContent → șablonul Android Studio;
          fișierele res/xml/backup_rules.xml și data_extraction_rules.xml există în proiect
        icon / roundIcon      → iconițele (roundIcon pentru Android 7.1+)
        label                 → numele din launcher, din strings.xml (singura intrare de acolo)
        supportsRtl           → interfața se oglindește în limbile RTL
        theme                 → Theme.DMA05, definit în values/themes.xml
    -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA05">

        <!--
          SINGURA ACTIVITATE.
            android:name=".MainActivity"   → punctul în față înseamnă „namespace-ul
                                             aplicației"; deci ro.ase.ie.dma05.MainActivity
            android:exported="true"        → obligatoriu din API 31 pentru orice componentă
                                             cu intent-filter; fără el, build-ul eșuează.
                                             Înseamnă „alte aplicații au voie să pornească
                                             asta" — necesar pentru iconița din launcher.
            windowSoftInputMode="adjustResize" → cere sistemului să micșoreze fereastra
                                             când apare tastatura. Cu edge-to-edge pe
                                             API 30+, fereastra NU mai e redimensionată
                                             de sistem: aplicația trebuie să consume
                                             WindowInsetsCompat.Type.ime(). DMA05 tratează
                                             doar systemBars(), deci tastatura acoperă
                                             widget-urile de jos. Nu se vede, pentru că
                                             EditText-urile sunt sus.
        -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!--
              INTENT-FILTER — ce face activitatea vizibilă în launcher.
              Fără el, activitatea există, dar nu e pornită de nimeni; o poți porni doar
              cu adb shell am start, dacă știi numele complet.
            -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
```

### După cod: ce declară manifestul

**`android:theme="@style/Theme.DMA05"`** — definit în `values/themes.xml`, cu părintele `Theme.Material3.DayNight.NoActionBar`. `NoActionBar` explică de ce aplicația nu are bară de titlu: primul widget începe imediat sub bara de status, împins în jos doar de padding-ul de insets.

**`xmlns:tools` e declarat, dar nefolosit** — niciun atribut `tools:` nu apare în manifest. Rămășiță de șablon, inofensivă.

**Nu există permisiuni.** Aplicația nu accesează nimic protejat: nici internet, nici stocare, nici cameră. Un manifest fără `<uses-permission>` e normal pentru un laborator de widget-uri.

**De ce `.MainActivity` cu punct:** punctul în față înseamnă „numele complet se formează prin concatenarea cu `namespace`". Deci `.MainActivity` devine `ro.ase.ie.dma05.MainActivity`. Fără punct, ar fi interpretat ca nume complet și ar trebui scris tot.

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
| Verificare | runtime | build |

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

### Ce costă fiecare, la runtime

```
findViewById(R.id.button)                    binding.button
        │                                          │
        ▼                                          ▼
View.findViewById(int id)                    getfield
  ├─ this.mID == id ?                          ActivityMainBinding.button
  │     return this                                 │
  ├─ for (copil : copii)                            │
  │     copil.findViewById(id)  ← recursiv         │
  └─ return null                                     ▼
        │                                       O(1)
        ▼                                       zero alocări
  O(n) în subarbore                             zero căutări
  + alocare int[] temporar în ViewGroup
```

**Ce înseamnă concret:** `findViewById` pe un arbore cu 17 view-uri face până la 17 comparații de `int` și, dacă view-ul e ultimul, parcurge tot arborele. Pentru un singur apel e neglijabil. Problema apare când îl apelezi în `onBindViewHolder` al unei liste cu 1000 de rânduri: 1000 × O(n) la fiecare derulare. `ViewBinding` mută toată căutarea într-un singur `bind`, la `inflate`.

**De ce `findViewById` are nevoie de cast:** metoda e declarată `public final <T extends View> T findViewById(int id)` în API-ul modern, deci cast-ul e implicit prin inferență. În codul vechi, semnătura returna `View` și cast-ul era explicit: `(Button) findViewById(...)`. `ViewBinding` nu are nevoie de niciun cast, pentru că tipul câmpului e deja cel corect.

**De ce `findViewById` poate returna `null`:** căutarea se face la runtime, iar compilatorul nu știe ce ID-uri există în layout. Un ID greșit sau un view care nu e în arborele curent întoarce `null`, iar primul acces aruncă `NullPointerException`. `ViewBinding` verifică la `bind` și aruncă imediat, cu mesajul `Missing required view with ID: …` — mai devreme și mai clar.

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

**De ce câmpurile sunt `public final`:** `public` ca să le citești direct, `final` ca să nu le poți reasigna. Sunt umplute o singură dată, în constructorul generat, și nu se mai schimbă. Un `binding.button = null` nu compilează.

### Un exemplu mic, complet

DMA05 are 17 câmpuri, prea multe pentru a vedea forma clasei. Un layout imaginar cu trei ID-uri arată așa:

```java
// RECONSTRUCȚIE pentru un layout imaginar `activity_demo.xml`:
//   <LinearLayout android:id="@+id/main">
//       <Button   android:id="@+id/btnOk" />
//       <TextView android:id="@+id/tvResult" />
//   </LinearLayout>
// Nu există în repo; e aici ca să vezi forma minimă a clasei generate.

public final class ActivityDemoBinding implements ViewBinding {

    private final LinearLayout rootView;      // rădăcina, pentru getRoot()
    public final LinearLayout main;           // câmp pentru @+id/main
    public final Button btnOk;                // câmp pentru @+id/btnOk
    public final TextView tvResult;           // câmp pentru @+id/tvResult

    private ActivityDemoBinding(LinearLayout rootView, LinearLayout main,
                                Button btnOk, TextView tvResult) {
        this.rootView = rootView;             // constructor privat: doar fabricile îl cheamă
        this.main = main;
        this.btnOk = btnOk;
        this.tvResult = tvResult;
    }

    @Override
    public LinearLayout getRoot() { return rootView; }   // contractul ViewBinding

    public static ActivityDemoBinding inflate(LayoutInflater inflater) {
        return inflate(inflater, null, false);           // varianta cu un argument
    }

    public static ActivityDemoBinding inflate(LayoutInflater inflater,
                                              ViewGroup parent, boolean attachToRoot) {
        View root = inflater.inflate(R.layout.activity_demo, parent, attachToRoot);
        return bind(root);                               // după inflate, umple câmpurile
    }

    public static ActivityDemoBinding bind(View rootView) {
        int id;
        id = R.id.main;
        LinearLayout main = ViewBindings.findChildViewById(rootView, id);
        if (main == null) {
            throw new NullPointerException("Missing required view with ID: "
                    + rootView.getResources().getResourceName(id));
        }
        id = R.id.btnOk;
        Button btnOk = ViewBindings.findChildViewById(rootView, id);
        if (btnOk == null) {
            throw new NullPointerException("Missing required view with ID: "
                    + rootView.getResources().getResourceName(id));
        }
        id = R.id.tvResult;
        TextView tvResult = ViewBindings.findChildViewById(rootView, id);
        if (tvResult == null) {
            throw new NullPointerException("Missing required view with ID: "
                    + rootView.getResources().getResourceName(id));
        }
        return new ActivityDemoBinding((LinearLayout) rootView, main, btnOk, tvResult);
    }
}
```

**Ce se vede în exemplu și se aplică și la DMA05:**

1. **Un câmp per ID, plus `rootView`.** Rădăcina are două referințe: `rootView` (privată, pentru `getRoot()`) și `main` (publică, pentru ID). Sunt același obiect.
2. **Constructorul e privat.** Nu poți face `new ActivityDemoBinding(...)` din codul tău. Singurele căi de a obține un binding sunt `inflate` și `bind`.
3. **`bind` e singurul loc cu căutări.** Trei ID-uri → trei `findChildViewById`. După `bind`, nicio căutare.
4. **Eșecul e imediat și explicit.** Dacă un ID lipsește din arbore, `bind` aruncă `NullPointerException` cu numele resursei, nu întoarce `null` mai departe.
5. **Cast-ul e o singură dată, pe rădăcină.** `(LinearLayout) rootView` — pentru că `inflate` întoarce `View`, iar câmpul e `LinearLayout`. Restul câmpurilor primesc tipul exact din `findChildViewById`, fără cast.

**De ce `bind` e public:** îl poți folosi când ai deja un view inflat pe altă cale — de exemplu într-un `RecyclerView.Adapter`, unde `inflate`-ul îl face părintele. `bind(view)` îți dă câmpurile fără să mai umfli încă o dată.

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
- **Nu generează cod pentru `include`-uri** decât dacă include-ul are ID; atunci câmpul e de tipul binding-ului inclus.
- **Nu validează XML-ul semantic.** Un `TextView` cu `android:text="123"` și `inputType` greșit compilează; binding-ul doar leagă referințe.

**De ce există totuși `findViewById` în fișier:** pentru `checkedId`. E singurul caz în care ID-ul nu e cunoscut la compilare. Toate celelalte 16 ID-uri sunt cunoscute, deci au câmp.

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
  adjustResize nu mai redimensionează fereastra (edge-to-edge, API 30+)
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

**De ce listener-ii se reînregistrează:** la rotire, arborele vechi e distrus și se construiește unul nou. Listener-ii erau atașați de view-urile vechi, care nu mai există. `onCreate` rulează din nou și îi atașează de view-urile noi.

**Ce se întâmplă cu `binding` la rotire:** câmpul e reasignat. Vechiul binding devine eligibil pentru garbage collection împreună cu arborele vechi. Nu rămâne nicio referință către el, pentru că activitatea veche e distrusă.

---

## 27.6 Ce să reții

### Tabelul fișierelor

| Fișier | Esența |
|---|---|
| `MainActivity.java` | `inflate` → `getRoot` → insets → 7 listeneri; un singur `findViewById`, pe grup, pentru `checkedId` |
| `activity_main.xml` | `LinearLayout` vertical, 14 copii, 17 ID-uri, fiecare widget de input o dată |
| `AndroidManifest.xml` | fără `package` (vine din `namespace`), `exported="true"`, `adjustResize`, temă `NoActionBar` |
| `build.gradle.kts` | `namespace` + `buildFeatures { viewBinding = true }` — singurele linii care se văd în cod |

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
8. **`Toast.makeText(...)` fără `.show()`** nu afișează nimic și nu dă eroare — cea mai tăcută greșeală din fișier.
9. **`ViewBinding` se generează la build**, nu la runtime: dacă adaugi un ID și nu rulezi build-ul, câmpul nu există.
10. **`binding` e câmp**, ca să supraviețuiască între metode și să fie reasignat la rotire.

### Diagramele, într-o propoziție fiecare

| Diagrama | Ce spune |
|---|---|
| 1. arborele + câmpurile | `inflate` transformă XML în obiecte și, în același pas, umple câmpurile după `android:id` |
| 2. `binding.button` | rezolvarea unui ID trece prin `R.id` la build și devine o citire de câmp la runtime |
| 3. fluxul în doi pași | `inflate` construiește arborele, `setContentView` îl atașează la fereastră |
| 4. padding pe rădăcină vs copil | padding-ul pe rădăcină mută toți copiii; pe un copil, doar acel copil |
| 5. lambda vs clasă anonimă | numărul de metode abstracte decide stilul, nu preferința |
| 6. `findViewById` vs `binding.button` | căutare O(n) în arbore vs citire O(1) de câmp |

---

## Rezumat capitol 27

- `ViewBinding` generează `ActivityMainBinding` din `activity_main.xml`: 17 câmpuri, unul per `android:id`.
- `inflate(getLayoutInflater())` → `setContentView(binding.getRoot())` înlocuiește `setContentView(R.layout...)` + `findViewById`.
- Insets-urile se aplică pe `binding.getRoot()`, niciodată pe un copil.
- Șapte listeneri de widget, cinci interfețe: `View.OnClickListener`, `CompoundButton.OnCheckedChangeListener` (×3), `RadioGroup.OnCheckedChangeListener`, `SeekBar.OnSeekBarChangeListener`, `RatingBar.OnRatingBarChangeListener` — plus listener-ul de insets, care nu e pe un widget.
- Lambda pentru interfețe cu o metodă; clasă anonimă pentru `SeekBar`, care are trei.
- `RadioGroup` impune excluderea reciprocă; `checkedId` e un ID de resursă, nu o poziție.
- `inputType` schimbă tastatura și filtrează, dar nu validează nimic.
- `progressBar` și `imageView` sunt în layout, dar neatinse în cod — inventar, nu funcționalitate.
- `Toast.makeText(...).show()` — fără `.show()`, nimic nu apare și nicio eroare nu te anunță.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [capitolul 13 — DMA05: ViewBinding](13%20-%20DMA05%20-%20ViewBinding.md).
