# Capitolul 25 — Codul DMA02 adnotat

**Obiectiv:** să citești primul proiect al laboratorului linie cu linie — clasa `Application`, ciclul de viață complet, `DynamicColors` și un `Intent` implicit — cu explicații pe fiecare bloc: ce face, de ce e acolo, ce se strică dacă îl ștergi.

**Sursa:** `DMA02/` la commitul `d719ffc` (2026-11-09, „G1097_S07") — 4 fișiere, 199 de linii de cod: `DMA02App.java` (62), `MainActivity.java` (64), `AndroidManifest.xml` (35), `activity_main.xml` (38).

**Cum citești capitolul.** Fiecare fișier are, în ordine:

1. un **antet de fișier** (`/* ... */` la Java, `<!-- ... -->` la XML) — ce este, de ce există, ce se strică fără el;
2. un **THEORY BLOCK** înainte de clasă sau de nodul principal — regula generală din spatele codului;
3. **codul adnotat linie cu linie** — fiecare linie are un motiv, iar fiecare metodă are un bloc `THEORY / LOGIC / REF / RISK`;
4. o secțiune de **capcane** și un **tabel cu ce se strică** dacă ștergi fiecare lucru.

Comentariile adăugate folosesc patru prefixe:

| Prefix | Ce înseamnă |
|---|---|
| `THEORY:` | regula din spatele liniei — ce garantează framework-ul |
| `LOGIC:` | pașii concreți, numerotați, pe care îi execută codul |
| `REF:` | unde se verifică afirmația (sursa Android 36, manifest, layout, `build.gradle.kts`) |
| `RISK:` | ce se strică dacă linia lipsește sau e schimbată |

> **Regula de aur:** tokenii de cod sunt identici cu cei din repo. Tot ce e scris după `//` sau între `<!-- -->` a fost adăugat pentru studiu. Comentariile nu schimbă compilarea și nu schimbă comportamentul.

---

## 25.0 Harta proiectului

```
DMA02/
└── src/main/
    ├── AndroidManifest.xml              ← contractul cu sistemul: 35 de linii
    ├── java/ro/ase/ie/dma02/
    │   ├── DMA02App.java                ← Application + 7 callback-uri: 62 de linii
    │   └── MainActivity.java            ← 6 metode de ciclu de viață + pressMe: 64 de linii
    └── res/
        ├── layout/activity_main.xml     ← toolbar + text + buton: 38 de linii
        ├── values/themes.xml            ← tema în modul light
        └── values-night/themes.xml      ← tema în modul night
```

| Fișier | Rol | Fără el |
|---|---|---|
| `DMA02App.java` | obiectul unic al procesului; abonare la ciclul de viață; Material You | manifestul nu are ce instanția: nicio eroare, doar tăcere |
| `MainActivity.java` | singura activitate; loghează ciclul de viață; lansează share sheet-ul | launcher-ul nu are ce porni: `ActivityNotFoundException` |
| `AndroidManifest.xml` | leagă clasele de sistem; declară filtrele de `Intent` | APK-ul nu se instalează sau aplicația nu apare în launcher |
| `activity_main.xml` | arborele de view-uri al ecranului | `R.layout.activity_main` nu există: build-ul eșuează |

**Cele două lumi ale proiectului:**

```
   COD JAVA                            MANIFEST                         SISTEM
   ─────────                           ────────                         ──────
   DMA02App      ── android:name ────► <application>  ◄── instanțiază ── ActivityThread
   MainActivity  ── android:name ────► <activity>     ◄── pornește ───── launcher
   pressMe       ── ACTION_SEND ─────► <intent-filter> ◄── rezolvă ───── PackageManager
   R.layout.activity_main ◄── nume ─── activitate     ◄── inflatează ── LayoutInflater
```

Fără săgeata din manifest, clasele există doar în cod: compilează, dar nu sunt niciodată create. Este prima capcană a proiectului și cea mai greu de depistat, pentru că nu produce nicio eroare.

---

## 25.1 `DMA02App.java` — clasa `Application`

### 25.1.1 Fișierul complet, adnotat

```java
/*
 * ======================================================================================
 * DMA02App.java — CLASA `Application` A PROIECTULUI DMA02
 * ======================================================================================
 * CE ESTE:
 *   Clasa care devine obiectul unic al procesului Android. Framework-ul o instanțiază
 *   o singură dată, la pornirea procesului, ÎNAINTE de orice activitate.
 *
 * DE CE EXISTĂ:
 *   1. Abonează un observator la ciclul de viață al TUTUROR activităților
 *      (`registerActivityLifecycleCallbacks`).
 *   2. Activează global Material You (`DynamicColors.applyToActivitiesIfAvailable`).
 *   3. Scrie primul mesaj din Logcat, ca dovadă că inițializarea globală a rulat.
 *
 * CE SE STRICĂ FĂRĂ EL:
 *   - fără `android:name=".DMA02App"` în manifest, clasa NU este instanțiată:
 *     nicio eroare, niciun mesaj — doar tăcere în Logcat;
 *   - fără `implements ActivityLifecycleCallbacks`, nu primești niciun eveniment;
 *   - fără `DynamicColors`, aplicația rămâne pe paleta fixă din `themes.xml`.
 *
 * ORDINEA PE SCURT:
 *   proces nou → Application.attachBaseContext() → ContentProvider.onCreate()
 *              → DMA02App.onCreate() → MainActivity.onCreate() → onStart() → onResume()
 *
 * REF: android.app.Application (Android 36), documentația clasei:
 *      „The Application class, or your subclass of the Application class, is
 *       instantiated before any other class when the process for your
 *       application/package is created."
 * ======================================================================================
 */

package ro.ase.ie.dma02;                    // pachetul aplicației; identic cu `namespace` din build.gradle.kts

import android.app.Activity;                // tipul primit de fiecare callback: activitatea observată
import android.app.Application;             // clasa de bază — obiectul unic al procesului
import android.os.Bundle;                   // starea salvată, primită de două dintre callback-uri
import android.util.Log;                    // scrierea în Logcat

import androidx.annotation.NonNull;         // contract pentru lint: parametrul nu are voie să fie null
import androidx.annotation.Nullable;        // contract pentru lint: parametrul poate fi null

import com.google.android.material.color.DynamicColors;   // Material You: culori extrase din wallpaper

/*
 * ======================================================================================
 * THEORY BLOCK: `Application` — obiectul unic al procesului
 * ======================================================================================
 * 1. UN PROCES = UN `Application`
 *    Android pornește aplicația într-un proces nou (implicit). La începutul procesului,
 *    `ActivityThread` creează EXACT UN obiect `Application`. Toate activitățile,
 *    serviciile și receiver-ele din acel proces îl împart.
 *    Consecință: câmpurile din `Application` sunt „globale" pentru proces, nu pentru o
 *    activitate. Nu se resetează la rotire și nu se recreează la navigare.
 *
 * 2. `Application` NU ESTE O ACTIVITATE
 *    Nu are fereastră, nu are layout, nu apare pe ecran. Este doar un punct de
 *    inițializare și un loc de stat global. De aceea `onCreate()` lui nu are
 *    `setContentView` și nu primește `Bundle`: nu are stare de restaurat.
 *
 * 3. `onCreate()` — UN SINGUR APEL, ÎNAINTE DE ORICE ACTIVITATE
 *    Documentația framework-ului: „Called when the application is starting, before any
 *    activity, service, or receiver objects (excluding content providers) have been
 *    created." Deci: providerii de conținut se pot crea înaintea lui, restul nu.
 *
 * 4. `ActivityLifecycleCallbacks` — ȘABLONUL OBSERVATOR
 *    `Application` ține o listă de observatori. Fiecare metodă de ciclu de viață a
 *    unei activități apelează, în interiorul ei, `Application.dispatchActivityX(...)`,
 *    care iterează lista. Înregistrând `this`, `DMA02App` primește evenimente de la
 *    TOATE activitățile, fără să scrie nimic în ele.
 *
 * 5. `DynamicColors` — MATERIAL YOU GLOBAL
 *    `applyToActivitiesIfAvailable(this)` înregistrează propriul observator și aplică
 *    un theme overlay fiecărei activități, înainte de `onCreate`. Un singur apel,
 *    efect în toată aplicația.
 *
 * ASCII: CINE SE CREEAZĂ PRIMUL
 *
 *   Zygote ──fork()──► proces nou
 *                         │
 *                         ├─ 1. Application.attachBaseContext()   (nu apare în cod)
 *                         ├─ 2. ContentProvider.onCreate()        (dacă există)
 *                         ├─ 3. DMA02App.onCreate()               ◄── AICI
 *                         │       ├─ super.onCreate()
 *                         │       ├─ registerActivityLifecycleCallbacks(this)
 *                         │       ├─ DynamicColors.applyToActivitiesIfAvailable(this)
 *                         │       └─ Log.w(TAG, "onCreate")
 *                         └─ 4. MainActivity.onCreate()           ◄── abia acum
 * ======================================================================================
 */
public class DMA02App
        extends Application                                       // (1) DMA02App ESTE un Application
        implements Application.ActivityLifecycleCallbacks {       // (2) și ESTE observatorul de ciclu de viață

    // TAG-ul din Logcat. `getSimpleName()` întoarce "DMA02App", fără pachet.
    // `getName()` ar fi dat "ro.ase.ie.dma02.DMA02App" — prea lung pentru o coloană.
    // Nu e `static`: Application are o singură instanță per proces, deci un câmp de
    // instanță e suficient. În MainActivity e `static final`, pentru că acolo pot
    // exista mai multe instanțe (la rotire) și tag-ul trebuie să fie al clasei.
    private final String TAG = DMA02App.class.getSimpleName();

    // ==================================================================================
    // METODA 1/8: onCreate() — PUNCTUL DE INTRARE AL PROCESULUI
    // ==================================================================================
    // THEORY: `Application.onCreate()` e chemat o singură dată, la pornirea procesului,
    //         înaintea oricărei activități. Este locul corect pentru inițializări
    //         globale: abonări, teme, biblioteci, DI.
    // LOGIC:
    //   1. `super.onCreate()` — contractul clasei de bază.
    //   2. `registerActivityLifecycleCallbacks(this)` — abonarea observatorului.
    //   3. `DynamicColors.applyToActivitiesIfAvailable(this)` — tema globală.
    //   4. `Log.w(...)` — dovada că inițializarea s-a terminat.
    // REF: android.app.Application#onCreate (Android 36); javadoc-ul clasei.
    // RISK: ordinea 2 → 3 → 4 nu e întâmplătoare. Abonarea și tema trebuie făcute
    //       ÎNAINTE ca prima activitate să fie creată; dacă le muți în MainActivity,
    //       rulează prea târziu pentru prima activitate.
    @Override
    public void onCreate() {
        super.onCreate();                                  // pas 0: contractul clasei de bază (aici e gol, dar se păstrează)
        registerActivityLifecycleCallbacks(this);          // pas 1: „this" devine observatorul tuturor activităților
        DynamicColors.applyToActivitiesIfAvailable(this);  // pas 2: Material You, global, dacă e disponibil

        Log.w(TAG, "onCreate");                            // pas 3: primul rând din Logcat — înaintea oricărei activități
    }

    // ==================================================================================
    // CALLBACK 1/7: onActivityCreated(Activity, Bundle)
    // ==================================================================================
    // THEORY: se declanșează când o activitate apelează `super.onCreate(...)`.
    //         `bundle` este exact `savedInstanceState`: `null` la prima creare,
    //         non-null la recreare (rotire, revenire după kill).
    // CÂND: în interiorul lui `Activity.onCreate`, după `mFragments.dispatchCreate()`
    //       și înainte de `mCalled = true`.
    // LOGIC: scrie un singur rând în Logcat, cu numele clasei activității.
    // REF: Activity.java (android-36), linia 1883 — `dispatchActivityCreated(...)`.
    // RISK: în acest moment `setContentView` NU a rulat încă (dacă activitatea apelează
    //       `super` prima, cum face MainActivity). Deci `findViewById` ar întoarce null:
    //       nu atinge view-urile aici.
    @Override
    public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
        Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());   // ex.: "onActivityCreatedMainActivity"
    }                                                                            // lipsește spațiul dintre text și nume

    // ==================================================================================
    // CALLBACK 2/7: onActivityDestroyed(Activity) — poziția 2 în fișier, nu în viață
    // ==================================================================================
    // THEORY: se declanșează când activitatea este distrusă definitiv: Back, rotire,
    //         `finish()`. Este perechea lui `onDestroy`.
    // CÂND: în interiorul lui `Activity.onDestroy`, după curățenia framework-ului.
    // LOGIC: scrie un singur rând în Logcat.
    // REF: Activity.java (android-36), linia 2971 — `dispatchActivityDestroyed()`.
    // RISK: NU e garantat. Dacă sistemul omoară procesul din lipsă de memorie,
    //       `onDestroy` nu rulează și callback-ul nu vine. Nu pune aici salvarea de date.
    @Override
    public void onActivityDestroyed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityDestroyed" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 3/7: onActivityPaused(Activity)
    // ==================================================================================
    // THEORY: se declanșează când activitatea își pierde focusul: altă activitate vine
    //         peste ea, dialog, share sheet, Home. Activitatea poate fi încă vizibilă.
    // CÂND: la începutul lui `Activity.onPause`, ÎNAINTE de restul corpului metodei.
    // LOGIC: scrie un singur rând în Logcat.
    // REF: Activity.java (android-36), linia 2662 — `dispatchActivityPaused()`.
    // RISK: `onPause` blochează tranziția către activitatea următoare. Orice lucrezi
    //       aici întârzie ecranul următor: păstrează metoda scurtă.
    @Override
    public void onActivityPaused(@NonNull Activity activity) {
        Log.w(TAG, "onActivityPaused" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 4/7: onActivityResumed(Activity)
    // ==================================================================================
    // THEORY: se declanșează când activitatea devine interactivă: e în prim-plan și
    //         primește input. Este perechea lui `onResume`.
    // CÂND: la începutul lui `Activity.onResume`, înainte de restul corpului.
    // LOGIC: scrie un singur rând în Logcat.
    // REF: Activity.java (android-36), linia 2228 — `dispatchActivityResumed()`.
    // RISK: aici poți porni animații și listeners; nu face treabă grea, pentru că
    //       întârzie primul frame interactiv.
    @Override
    public void onActivityResumed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityResumed" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 5/7: onActivitySaveInstanceState(Activity, Bundle)
    // ==================================================================================
    // THEORY: se declanșează când sistemul cere activității să-și salveze starea, ca
    //         să o poată reconstrui după ce procesul e omorât. `bundle` este exact
    //         obiectul care va ajunge în `onCreate` la revenire.
    // CÂND: în interiorul lui `Activity.onSaveInstanceState`. Din Android 9 (API 28),
    //       după `onStop`; înainte, putea fi înainte de `onStop`.
    // LOGIC: niciunul — metoda e goală intenționat.
    // REF: Activity.java (android-36), linia 2565 — `dispatchActivitySaveInstanceState(...)`.
    // RISK: Bundle-ul trece prin Binder; datele mari dau `TransactionTooLargeException`.
    //       DMA02 nu are stare de salvat, deci metoda rămâne goală.
    @Override
    public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {

    }

    // ==================================================================================
    // CALLBACK 6/7: onActivityStarted(Activity)
    // ==================================================================================
    // THEORY: se declanșează când activitatea devine vizibilă, dar nu neapărat
    //         interactivă. Este perechea lui `onStart`.
    // CÂND: în interiorul lui `Activity.onStart`, după `mFragments.doLoaderStart()`.
    // LOGIC: scrie un singur rând în Logcat.
    // REF: Activity.java (android-36), linia 2154 — `dispatchActivityStarted()`.
    // RISK: aici activitatea e vizibilă, dar nu primește încă input. Nu porni
    //       animații care depind de focus.
    @Override
    public void onActivityStarted(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStarted" + activity.getClass().getSimpleName());
    }

    // ==================================================================================
    // CALLBACK 7/7: onActivityStopped(Activity)
    // ==================================================================================
    // THEORY: se declanșează când activitatea nu mai este vizibilă: Home, altă
    //         activitate full-screen, ecran stins. Este perechea lui `onStop`.
    // CÂND: în interiorul lui `Activity.onStop`, după `mActivityTransitionState.onStop`.
    // LOGIC: scrie un singur rând în Logcat.
    // REF: Activity.java (android-36), linia 2893 — `dispatchActivityStopped()`.
    // RISK: activitatea poate fi distrusă imediat după, fără `onDestroy` garantat.
    //       Nu păstra aici resurse care trebuie eliberate neapărat.
    @Override
    public void onActivityStopped(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStopped" + activity.getClass().getSimpleName());
    }
}   // închide clasa DMA02App
```

### 25.1.2 De ce `Application` există și de ce rulează înaintea oricărei activități

Android nu pornește „aplicația" ca pe un proces monolitic. Pornește un **proces Linux** și, în el, un **fir principal** (`ActivityThread`). La începutul acelui fir, framework-ul construiește un singur obiect `Application`, apoi, la cererea launcher-ului, construiește prima activitate. Ordinea nu este o convenție de stil: este impusă de `ActivityThread.handleBindApplication()`.

```
ActivityThread.handleBindApplication()
  │
  ├─ 1. makeApplication(...)                 ← creează instanța clasei din android:name
  │       └─ DMA02App()                      ← constructorul (nu-l scriem)
  │
  ├─ 2. app.attachBaseContext(context)       ← Context-ul de bază
  │
  ├─ 3. installContentProviders(...)         ← providerii: ÎNAINTE de Application.onCreate
  │       └─ ContentProvider.onCreate()
  │
  ├─ 4. mInstrumentation.callApplicationOnCreate(app)
  │       └─ DMA02App.onCreate()             ◄── abonare + DynamicColors + primul log
  │
  └─ 5. bucla de mesaje a firului principal  ← abia acum pot veni cereri de activitate
          └─ launchActivity(...) → MainActivity
```

**De ce nu un bloc `static`:** un bloc `static { ... }` rulează la încărcarea clasei, care poate fi declanșată de orice cod, oricând, și nu are un `Context` garantat. `Application.onCreate` rulează exact o dată per proces, înaintea oricărei componente, și primește un `Context` valid. Este singurul loc în care poți înregistra `ActivityLifecycleCallbacks` **înainte** ca prima activitate să existe.

**De ce nu în `MainActivity.onCreate`:** ai pierde exact primul eveniment — `onActivityCreated` pentru `MainActivity` însăși — și ai repeta codul în fiecare activitate. În DMA02 există o singură activitate, deci diferența e mică; în `G1097` (două activități) devine vizibilă.

**`Application` nu are UI:** nu are fereastră, nu are `setContentView`, nu apare în recents. Este doar un obiect de proces. De aceea `onCreate()` lui nu primește `Bundle`: nu are stare de restaurat.

> **Nu pune curățenie în `onTerminate()`.** Metoda există, dar documentația spune că se apelează doar în medii emulate; pe un dispozitiv real, procesul este pur și simplu omorât, fără să ruleze codul tău.

### 25.1.3 Ordinea exactă: `Application.onCreate` → `Activity.onCreate` → `onStart` → `onResume`

```
TIMP ─────────────────────────────────────────────────────────────────────────────►

DMA02App.onCreate()
  │  super.onCreate()
  │  registerActivityLifecycleCallbacks(this)
  │  DynamicColors.applyToActivitiesIfAvailable(this)
  │  Log.w("DMA02App", "onCreate")
  ▼
MainActivity.onCreate(savedInstanceState)
  │  super.onCreate(savedInstanceState)
  │    └─ Application.dispatchActivityCreated(this, savedInstanceState)
  │         └─ DMA02App.onActivityCreated(activity, bundle)      → log „onActivityCreatedMainActivity"
  │  setContentView(R.layout.activity_main)
  │  Log.w("MainActivity", "onCreate")                            → log „onCreate"
  ▼
MainActivity.onStart()
  │  super.onStart()
  │    └─ Application.dispatchActivityStarted(this)
  │         └─ DMA02App.onActivityStarted(activity)               → log „onActivityStartedMainActivity"
  │  Log.w("MainActivity", "onStart")                             → log „onStart"
  ▼
MainActivity.onResume()
  │  super.onResume()
  │    └─ Application.dispatchActivityResumed(this)               ← la ÎNCEPUTUL lui onResume
  │         └─ DMA02App.onActivityResumed(activity)               → log „onActivityResumedMainActivity"
  │  Log.w("MainActivity", "onResume")                            → log „onResume"
  ▼
ECRANUL E VIZIBIL ȘI INTERACTIV
```

**De ce logul din `Application` apare primul:** pentru că `MainActivity` apelează `super.onX()` **primul**, iar dispatch-ul către `Application` se face **în interiorul** lui `super.onX()`. Ordinea din Logcat nu spune „callback-ul rulează înaintea metodei", ci „logul tău rulează după `super`".

> Dacă ai scrie `Log.w(...)` **înainte** de `super.onStart()`, ordinea s-ar inversa: `MainActivity: onStart` ar apărea primul, apoi `DMA02App: onActivityStartedMainActivity`. Aceeași metodă, altă ordine — doar din poziția lui `super`.

**Ce vezi în Logcat la o pornire completă:**

```
DMA02App:      onCreate
DMA02App:      onActivityCreatedMainActivity
MainActivity:  onCreate
DMA02App:      onActivityStartedMainActivity
MainActivity:  onStart
DMA02App:      onActivityResumedMainActivity
MainActivity:  onResume
```

**Ce vezi la ieșire (Home, apoi Back):**

```
DMA02App:      onActivityPausedMainActivity
MainActivity:  onPause
DMA02App:      onActivityStoppedMainActivity
MainActivity:  onStop
DMA02App:      onActivityDestroyedMainActivity
MainActivity:  onDestroy
```

### 25.1.4 Ce observă `registerActivityLifecycleCallbacks`

```
Application
  └─ mActivityLifecycleCallbacks : ArrayList<ActivityLifecycleCallbacks>
        └─ [0] DMA02App          ← înregistrat de `registerActivityLifecycleCallbacks(this)`

Activity.onCreate()
  └─ super.onCreate()
       └─ getApplication().dispatchActivityCreated(this, bundle)
            └─ for (cb : mActivityLifecycleCallbacks)
                   cb.onActivityCreated(this, bundle)
                     └─ DMA02App.onActivityCreated(...) → Log.w(...)
```

Observatorul primește **instanța** activității, nu doar numele ei. De aceea poți face în `Application` lucruri care depind de activitatea curentă — de exemplu, să marchezi în analytics ce ecran a fost deschis — fără ca activitatea să știe că este observată.

**Cele șapte metode, pe scurt:**

| # | Callback | Declanșat din | Când | Ce poți face acolo |
|---|---|---|---|---|
| 1 | `onActivityCreated(activity, bundle)` | `Activity.onCreate` | la creare; `bundle` = `savedInstanceState` | inițializări care depind de activitate, dar **nu** view-uri |
| 2 | `onActivityStarted(activity)` | `Activity.onStart` | activitatea devine vizibilă | pornirea unor resurse vizuale |
| 3 | `onActivityResumed(activity)` | `Activity.onResume` | activitatea devine interactivă | listeners, animații, analytics „screen view" |
| 4 | `onActivityPaused(activity)` | `Activity.onPause` | pierde focusul | oprirea listener-ilor, salvarea rapidă |
| 5 | `onActivityStopped(activity)` | `Activity.onStop` | nu mai e vizibilă | eliberarea resurselor grele |
| 6 | `onActivitySaveInstanceState(activity, bundle)` | `Activity.onSaveInstanceState` | sistemul cere starea | date mici, serializabile |
| 7 | `onActivityDestroyed(activity)` | `Activity.onDestroy` | distrugere definitivă | curățenie finală (dacă apucă) |

**De ce toate șapte:** interfața are șapte metode **abstracte**. Nu poți implementa doar jumătate: dacă ștergi o metodă, proiectul **nu compilează** (`DMA02App is not abstract and does not override abstract method ...`). De aceea `onActivitySaveInstanceState` există chiar dacă nu face nimic.

> Din API 29, interfața are și metode `default` pentru momentele „pre" și „post" (`onActivityPreCreated`, `onActivityPostResumed` etc.). Acelea au implementare implicită goală, deci nu ești obligat să le suprascrii. Cele șapte din tabel sunt singurele abstracte.

**De ce ordinea din fișier nu e ordinea de execuție:** metodele apar alfabetic — `onActivityCreated`, `onActivityDestroyed`, `onActivityPaused`, `onActivityResumed`, `onActivitySaveInstanceState`, `onActivityStarted`, `onActivityStopped`. IntelliJ generează implementările în ordine alfabetică, nu în ordinea ciclului de viață. Ordinea de bază este `Created → Started → Resumed → Paused → Stopped → Destroyed`; `SaveInstanceState` se intercalează înainte de distrugere (după `Stopped` pe API 28+).

### 25.1.5 `android:name=".DMA02App"` — singura linie care leagă clasa de runtime

```
AndroidManifest.xml                         Runtime
───────────────────                         ───────
android:name=".DMA02App"   ─────────────►   ro.ase.ie.dma02.DMA02App
                                            (punctul = relativ la `namespace`)

lipsește                   ─────────────►   android.app.Application
                                            (clasa ta NU e instanțiată: tăcere)

nume greșit                ─────────────►   ClassNotFoundException la pornire
```

**De ce punctul:** în manifest, un nume care începe cu `.` este relativ la pachetul aplicației. Aici `namespace = "ro.ase.ie.dma02"` în `build.gradle.kts`, deci `.DMA02App` înseamnă `ro.ase.ie.dma02.DMA02App`. Poți scrie și numele complet, fără punct; ambele sunt echivalente.

**Ce se întâmplă dacă uiți linia:** Android folosește `android.app.Application` implicit. `DMA02App` nu este niciodată creată, deci `onCreate()` nu rulează, callback-urile nu se înregistrează, `DynamicColors` nu se aplică și primul log nu apare. Aplicația arată și funcționează identic. **Nicio eroare. Doar tăcere.** Este capcana clasică a laboratorului: crezi că ai scris codul, dar codul nu rulează.

**Ce se întâmplă dacă numele e greșit:** la pornire, `ActivityThread` încearcă să instanțieze clasa și eșuează cu `Unable to instantiate application ro.ase.ie.dma02.DMA02App: java.lang.ClassNotFoundException`. Aici eroarea e zgomotoasă, deci e mai ușor de găsit decât lipsa liniei.

### 25.1.6 `DynamicColors.applyToActivitiesIfAvailable` — Material You

**Ce face Material You:** din Android 12 (API 31), sistemul extrage o paletă din wallpaper și o expune ca resurse de sistem: `system_accent1_*`, `system_accent2_*`, `system_neutral1_*`, `system_neutral2_*`. Material Components le mapează pe rolurile temei — `colorPrimary`, `colorOnPrimary`, `colorSurface` etc. — printr-un **theme overlay**. Rezultatul: aplicația preia culorile fundalului, fără să scrii nicio culoare.

```
WALLPAPER
   │  (Android 12+, API 31+)
   ▼
Paleta sistemului: system_accent1_100 ... system_neutral2_900
   │
   ▼
DynamicColors.applyToActivitiesIfAvailable(app)
   │  înregistrează un ActivityLifecycleCallbacks propriu
   ▼
onActivityPreCreated(activity)          ← înainte de Activity.onCreate
   │  activity.getTheme().applyStyle(ThemeOverlay_Material3_DynamicColors_*, true)
   ▼
colorPrimary / colorSurface / ... vin din wallpaper
```

**De ce un singur apel e suficient:** metoda nu aplică tema unei singure activități. Ea înregistrează un observator pe `Application` — exact mecanismul din 25.1.4 — și aplică overlay-ul în `onActivityPreCreated`, adică **înainte** ca fiecare activitate să-și rezolve tema. De aceea apelul stă în `Application.onCreate`: prinde toate activitățile, inclusiv prima.

**De ce e no-op sub API 31:** resursele `system_accent1_*` nu există înainte de Android 12. Biblioteca verifică `Build.VERSION.SDK_INT >= 31` și, dacă nu e îndeplinită, nu înregistrează nimic. Nu crapă, nu loghează o eroare — pur și simplu nu face nimic, iar tema rămâne cea din `themes.xml`.

> **În DMA02, `minSdk = 33`.** Aplicația nu se poate instala pe un dispozitiv sub Android 13, deci orice dispozitiv pe care rulează are API ≥ 33, adică peste pragul de 31. Practic, aici `DynamicColors` se aplică mereu. No-op-ul rămâne o noțiune teoretică utilă pentru întrebarea de examen, nu un caz real al proiectului.

**Condiția suplimentară:** overlay-ul aplicat este unul Material3. Dacă tema activității nu coboară din `Theme.Material3`, nu există overlay potrivit și nu se schimbă nimic. Aici tema este `Theme.DMA02` → `Base.Theme.DMA02` → `Theme.Material3.Dark` / `Theme.Material3.DayNight.NoActionBar`, deci condiția e îndeplinită.

### 25.1.7 `Log.w` vs `Log.d` — de ce warning

Nivelele din `android.util.Log`, în ordine crescătoare:

| Nivel | Metodă | Valoare | Când apare în Logcat |
|---|---|---|---|
| VERBOSE | `Log.v` | 2 | doar cu filtrul „Verbose" |
| DEBUG | `Log.d` | 3 | cu filtrul „Debug" sau mai jos |
| INFO | `Log.i` | 4 | cu filtrul „Info" sau mai jos |
| WARN | `Log.w` | 5 | cu filtrul „Warn" sau mai jos |
| ERROR | `Log.e` | 6 | cu filtrul „Error" sau mai jos |

Logcat afișează mesajele cu nivel **≥** filtrul ales. Deci:

- dacă filtrezi la **Info**, `Log.d` dispare, iar `Log.w` rămâne;
- dacă filtrezi la **Warn**, rămân doar `Log.w` și `Log.e`;
- `Log.w` este afișat convențional în galben, ceea ce îl face ușor de găsit într-o listă lungă.

**De ce `w` în laborator:** pentru vizibilitate, nu pentru că ceva ar fi greșit. Mesajele sunt demonstrații, iar `w` rezistă la filtre mai agresive decât `d`. În plus, `d` este nivelul care se elimină cel mai des în build-urile de release, prin reguli R8 de tip `-assumenosideeffects`; proiectul nu are astfel de reguli, dar convenția rămâne.

> **Nu confunda nivelul cu tag-ul.** `Log.w(TAG, "onCreate")` are două argumente: primul e tag-ul (`DMA02App` sau `MainActivity`), al doilea e mesajul. În Logcat, cele două coloane se văd separat: `DMA02App: onCreate` înseamnă tag `DMA02App`, mesaj `onCreate`.

### 25.1.8 Ce se strică dacă ștergi fiecare linie din `DMA02App`

| Linie ștearsă | Efect |
|---|---|
| `extends Application` | la pornire: `ClassCastException` — manifestul cere o clasă care nu e `Application` |
| `implements Application.ActivityLifecycleCallbacks` | `registerActivityLifecycleCallbacks(this)` nu mai compilează: `this` nu are tipul cerut |
| `private final String TAG = ...` | nu compilează: `TAG` nu mai există în cele 8 metode |
| `super.onCreate()` | la `Application` baza e goală, deci nimic vizibil; încalcă însă contractul și e periculos dacă lanțul se schimbă |
| `registerActivityLifecycleCallbacks(this)` | nicio eroare, niciun mesaj `onActivity*` în Logcat — aplicația arată identic |
| `DynamicColors.applyToActivitiesIfAvailable(this)` | paleta fixă din `themes.xml`; pe Android 12+ aplicația nu mai urmează wallpaper-ul |
| `Log.w(TAG, "onCreate")` | nimic funcțional; dispare doar primul rând din Logcat |
| o metodă de callback | nu compilează: interfața are șapte metode abstracte |
| `@Override` | compilează, dar o greșeală de nume devine o metodă nouă, ignorată de framework |

### 25.1.9 Unde se verifică afirmațiile

Toate afirmațiile despre ordinea callback-urilor se pot verifica în sursa Android instalată local, în `$ANDROID_HOME/sources/android-36/android/app/Activity.java`. Comanda de căutare este `grep -n "dispatchActivity" "$ANDROID_HOME/sources/android-36/android/app/Activity.java"`.

| Afirmație | Linia din `Activity.java` (android-36) |
|---|---|
| `dispatchActivityCreated` e în `onCreate` | 1883 |
| `dispatchActivityStarted` e în `onStart` | 2154 |
| `dispatchActivityResumed` e în `onResume` | 2228 |
| `dispatchActivityPaused` e în `onPause` | 2662 |
| `dispatchActivityStopped` e în `onStop` | 2893 |
| `dispatchActivitySaveInstanceState` e în `onSaveInstanceState` | 2565 |
| `dispatchActivityDestroyed` e în `onDestroy` | 2971 |

> Numerele de linie sunt pentru `android-36`; în alte versiuni ale SDK-ului pot diferi cu câteva linii. Metoda și ordinea rămân aceleași. Ce contează pentru examen: fiecare dispatch este **în interiorul** metodei cu același nume, nu într-un `performX()` separat.

### 25.1.10 `Application` vs `Activity` vs `Service`

| Criteriu | `Application` | `Activity` | `Service` |
|---|---|---|---|
| Instanțe per proces | exact 1 | 0..n | 0..n |
| Are UI | nu | da | nu |
| Ciclu de viață | `onCreate` → `onTerminate` (nerelevant) | 6 metode + `onRestart` | `onCreate` → `onStartCommand` → `onDestroy` |
| Rol în DMA02 | inițializare globală | ecranul | nu există |
| Primește `Bundle` | nu | da, în `onCreate` | nu |

**De ce `Application` nu are `onStart`/`onResume`:** nu are fereastră și nu concurează cu alte aplicații pentru prim-plan. Există cât există procesul.

---

## 25.2 `MainActivity.java` — ciclul de viață

### 25.2.1 Fișierul complet, adnotat

```java
/*
 * ======================================================================================
 * MainActivity.java — SINGURA ACTIVITATE A PROIECTULUI DMA02
 * ======================================================================================
 * CE ESTE:
 *   Activitatea care apare în launcher și care deține ecranul din `activity_main.xml`.
 *   Extinde `AppCompatActivity`, nu `Activity`: are nevoie de tema Material3/AppCompat.
 *
 * DE CE EXISTĂ:
 *   1. Demonstrează ciclul de viață: șase metode suprascrise, fiecare doar loghează.
 *   2. Leagă layout-ul de cod: `setContentView(R.layout.activity_main)`.
 *   3. Demonstrează un `Intent` implicit: `pressMe` deschide share sheet-ul.
 *
 * CE SE STRICĂ FĂRĂ EL:
 *   - fără `setContentView`, ecranul rămâne gol și `findViewById` întoarce null;
 *   - fără `super.onCreate`, framework-ul aruncă `SuperNotCalledException`;
 *   - fără `pressMe`, `android:onClick` crapă la click, nu la compilare.
 *
 * REF: android.app.Activity (Android 36); AppCompatActivity (androidx.appcompat).
 * ======================================================================================
 */

package ro.ase.ie.dma02;                             // același pachet ca DMA02App

import android.content.Intent;                       // folosit doar în pressMe
import android.os.Bundle;                            // parametrul din onCreate
import android.util.Log;                             // scrierea în Logcat
import android.view.View;                            // parametrul din pressMe — cerut de android:onClick

import androidx.appcompat.app.AppCompatActivity;     // varianta AppCompat a lui Activity

/*
 * ======================================================================================
 * THEORY BLOCK: ciclul de viață al unei activități
 * ======================================================================================
 * 1. CE ESTE O ACTIVITATE
 *    O componentă cu fereastră. Sistemul o creează, o afișează, o ascunde și o
 *    distruge după reguli fixe. Tu nu apelezi `onCreate`; îl apelează framework-ul.
 *
 * 2. CELE ȘAPTE STĂRI (șase metode + onRestart)
 *    onCreate → onStart → onResume → onPause → onStop → onDestroy
 *    `onRestart` apare doar la revenirea din `onStop`.
 *
 * 3. `super` ESTE OBLIGATORIU
 *    `ActivityThread` verifică după fiecare metodă dacă ai apelat `super`. Dacă nu,
 *    aruncă `SuperNotCalledException`. Nu e convenție, e verificare la runtime.
 *
 * 4. `AppCompatActivity` vs `Activity`
 *    `AppCompatActivity` aduce backport-ul AppCompat: inflatare compatibilă, teme
 *    Material pe versiuni vechi, `AppCompatDelegate` pentru dark mode. Cere o temă
 *    care coboară din `Theme.AppCompat` (aici: `Theme.Material3.*`).
 *
 * 5. ORDINEA DIN FIȘIER NU E ORDINEA DE EXECUȚIE
 *    Metodele sunt în ordine alfabetică (generate de IntelliJ), nu cronologică.
 *
 * ASCII: CICLUL COMPLET
 *
 *   onCreate ──► onStart ──► onResume ──► [vizibil, interactiv]
 *                                            │
 *                          Home / altă activitate
 *                                            ▼
 *                                        onPause ──► onStop ──► [ascuns]
 *                                                          │
 *                                        revenire ──► onRestart ──► onStart ──► onResume
 *                                                          │
 *                                        Back ──► onDestroy
 * ======================================================================================
 */
public class MainActivity extends AppCompatActivity {   // (1) activitate cu suport AppCompat

    // Tag-ul din Logcat: "MainActivity".
    // `static final` = aparține clasei, nu instanței. La rotire se creează o instanță
    // nouă, dar tag-ul rămâne același — exact ce vrei în Logcat.
    private static final String TAG = MainActivity.class.getSimpleName();

    // ==================================================================================
    // METODA 1/7: onCreate(Bundle) — CONSTRUCȚIA
    // ==================================================================================
    // THEORY: prima metodă a ciclului. Aici se inflatează layout-ul și se leagă
    //         view-urile. `savedInstanceState` e null la prima creare și non-null
    //         la recreare (rotire, revenire după kill).
    // LOGIC:
    //   1. `super.onCreate(...)` — obligatoriu primul.
    //   2. `setContentView(...)` — creează arborele de view-uri.
    //   3. `Log.w(...)` — marchează sfârșitul construcției.
    // REF: Activity.java (android-36), linia 1861 — `onCreate`.
    // RISK: fără `super`, `SuperNotCalledException`. Fără `setContentView`, ecran gol.
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);              // pas 1: framework-ul își face inițializările
        setContentView(R.layout.activity_main);          // pas 2: XML-ul devine arbore de View-uri
        Log.w(TAG, "onCreate");                          // pas 3: primul log al activității
    }

    // ==================================================================================
    // METODA 2/7: onDestroy() — DISTRUGEREA
    // ==================================================================================
    // THEORY: ultima metodă a ciclului. Apare la Back, la `finish()` sau la rotire.
    //         NU este garantată: dacă sistemul omoară procesul, nu rulează.
    // LOGIC: `super` + un rând în Logcat.
    // REF: Activity.java (android-36), linia 2932 — `onDestroy`.
    // RISK: nu pune aici salvarea de date — s-ar putea să nu apuce să ruleze.
    //       Pentru salvare există `onPause` / `onStop` / `onSaveInstanceState`.
    @Override
    protected void onDestroy() {
        super.onDestroy();                              // curățenia framework-ului
        Log.w(TAG, "onDestroy");
    }

    // ==================================================================================
    // METODA 3/7: onStart() — DEVENIREA VIZIBILĂ
    // ==================================================================================
    // THEORY: activitatea devine vizibilă, dar nu primește încă input. Este perechea
    //         lui `onStop`.
    // LOGIC: `super` + un rând în Logcat.
    // REF: Activity.java (android-36), linia 2148 — `onStart`.
    // RISK: aici încă nu poți presupune că utilizatorul poate apăsa ceva.
    @Override
    protected void onStart() {
        super.onStart();                                // framework-ul își face tranziția
        Log.w(TAG, "onStart");
    }

    // ==================================================================================
    // METODA 4/7: onStop() — ASCUNDEREA
    // ==================================================================================
    // THEORY: activitatea nu mai este vizibilă: Home, altă activitate full-screen,
    //         ecran stins. Este perechea lui `onStart`.
    // LOGIC: `super` + un rând în Logcat.
    // REF: Activity.java (android-36), linia 2889 — `onStop`.
    // RISK: după `onStop`, activitatea poate fi distrusă fără `onDestroy` garantat.
    @Override
    protected void onStop() {
        super.onStop();                                 // framework-ul își face tranziția
        Log.w(TAG, "onStop");
    }

    // ==================================================================================
    // METODA 5/7: onPause() — PIERDEREA FOCUSULUI
    // ==================================================================================
    // THEORY: activitatea își pierde focusul: altă activitate vine peste ea, dialog,
    //         share sheet, Home. Poate fi încă vizibilă.
    // LOGIC: `super` + un rând în Logcat.
    // REF: Activity.java (android-36), linia 2660 — `onPause`.
    // RISK: `onPause` blochează tranziția către activitatea următoare. Orice lucrezi
    //       aici întârzie ecranul următor.
    @Override
    protected void onPause() {
        super.onPause();                                // framework-ul își face tranziția
        Log.w(TAG, "onPause");
    }

    // ==================================================================================
    // METODA 6/7: onResume() — DEVENIREA INTERACTIVĂ
    // ==================================================================================
    // THEORY: activitatea este în prim-plan și primește input. Este perechea lui
    //         `onPause`.
    // LOGIC: `super` + un rând în Logcat.
    // REF: Activity.java (android-36), linia 2226 — `onResume`.
    // RISK: aici poți porni animații și listeners; nu face treabă grea, pentru că
    //       întârzie primul frame interactiv.
    @Override
    protected void onResume() {
        super.onResume();                               // framework-ul își face tranziția
        Log.w(TAG, "onResume");
    }

    // ==================================================================================
    // METODA 7/7: pressMe(View) — UN `Intent` IMPLICIT
    // ==================================================================================
    // THEORY: `android:onClick="pressMe"` din layout leagă butonul de această metodă
    //         prin REFLECȚIE, nu la compilare. Framework-ul caută în Context-ul
    //         view-ului o metodă `public void` cu exact un parametru `View`.
    // LOGIC:
    //   1. Varianta 1 (comentată): ACTION_VIEW + https:// → browser.
    //   2. Varianta 2 (comentată): ACTION_DIAL + tel: → tastatură telefonică.
    //   3. Varianta 3 (activă): ACTION_SEND + text/plain → share sheet.
    // REF: Intent.java, Intent.ACTION_SEND, Intent.createChooser.
    // RISK: `Uri` NU e importat. Dacă decomentezi primele două variante, fișierul
    //       nu compilează: `cannot find symbol: class Uri`.
    public void pressMe(View view) {                    // semnătura e dictată de android:onClick="pressMe"
        // --------------------------------------------------------------------------
        // VARIANTA 1 (comentată): deschide un URL în browserul implicit.
        // --------------------------------------------------------------------------
        // `ACTION_VIEW` + `https://` = „arată-mi acest lucru".
        // Ar cere `import android.net.Uri;` — de aceea blocul e comentat.
  /*      Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse("https://developer.android.com"));
        startActivity(web);*/

        // --------------------------------------------------------------------------
        // VARIANTA 2 (comentată): deschide tastatura telefonică, fără să sune.
        // --------------------------------------------------------------------------
        // `ACTION_DIAL` NU cere permisiunea CALL_PHONE. Varianta care sună,
        // `ACTION_CALL`, ar cere-o.
        /*Intent call = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0212345678"));
        startActivity(call);*/

        // --------------------------------------------------------------------------
        // VARIANTA 3 (activă): share sheet.
        // --------------------------------------------------------------------------
        Intent share = new Intent(Intent.ACTION_SEND);                  // acțiunea: „trimite"
        share.setType("text/plain");                                     // MIME: obligatoriu pentru rezolvare
        share.putExtra(Intent.EXTRA_TEXT, "Hello!");                     // payload-ul
        startActivity(Intent.createChooser(share, "Share via DMA"));     // chooser forțat, cu titlu

    }
}   // închide clasa MainActivity
```

### 25.2.2 De ce `AppCompatActivity` și nu `Activity`

`AppCompatActivity` este varianta AndroidX a lui `Activity`. Aduce înapoi (backport) comportamentul AppCompat:

- **inflatare compatibilă** — `AppCompatViewInflater` transformă automat `<TextView>` în `AppCompatTextView` etc., ca să arate la fel pe toate versiunile;
- **teme Material pe versiuni vechi** — `Theme.Material3.*` coboară din `Theme.AppCompat`, deci are nevoie de o activitate AppCompat;
- **`AppCompatDelegate`** — dark mode, locale, vector drawables.

> **Capcana inversă:** dacă păstrezi `AppCompatActivity` dar schimbi tema într-una de platformă (fără AppCompat), aplicația crapă la pornire cu `IllegalStateException: You need to use a Theme.AppCompat theme (or descendant) with this activity.` Aici tema `Theme.DMA02` → `Base.Theme.DMA02` → `Theme.Material3.Dark` / `Theme.Material3.DayNight.NoActionBar` este compatibilă.

**De ce `TAG` e `static final` aici, dar `private final` în `DMA02App`:** `MainActivity` poate avea mai multe instanțe (la rotire, la revenire), dar tag-ul e același pentru toate — deci aparține clasei. `Application` are o singură instanță per proces, deci un câmp de instanță e suficient. Este o inconsecvență de stil, nu un bug.

### 25.2.3 Ordinea din fișier vs ordinea de execuție

Metodele apar în fișier în ordine alfabetică: `onCreate`, `onDestroy`, `onStart`, `onStop`, `onPause`, `onResume`. IntelliJ generează implementările așa. Ordinea reală la rulare este alta:

```
pornire:   onCreate → onStart → onResume
Home:      onPause → onStop
revenire:  onRestart → onStart → onResume
Back:      onPause → onStop → onDestroy
rotire:    onPause → onStop → onDestroy → onCreate → onStart → onResume
```

> La rotire, `onSaveInstanceState` rulează înainte de distrugere, ca să poată fi reconstruită starea. În DMA02 nu salvează nimic, dar mecanismul există.

**De ce toate cele șase metode sunt „goale":** fiecare suprascriere face exact un lucru — scrie un rând în Logcat. Sunt **observatori**, nu cerințe: dacă ștergi o metodă întreagă, aplicația funcționează în continuare, pentru că rulează implementarea din `AppCompatActivity`. Pierzi doar rândul din Logcat.

**De ce `super` e primul peste tot:** pentru un log, ordinea nu contează. Dar convenția pentru `onPause`, `onStop` și `onDestroy` este să faci curățenia **înainte** de `super` (resursele tale încă există), iar pentru `onCreate`, `onStart`, `onResume` — după `super`. Aici toate sunt după, pentru simplitate. Ce contează: `super` **trebuie** apelat. Fără el, `ActivityThread` aruncă `SuperNotCalledException` după fiecare metodă.

### 25.2.4 `pressMe`: cele trei `Intent`-uri

Un `Intent` are două feluri de a fi construit:

- **explicit** — `new Intent(this, MainActivity.class)`: știi exact ce clasă vrei;
- **implicit** — `new Intent(Intent.ACTION_SEND)`: declari doar **ce operație** vrei, iar sistemul caută aplicațiile care o pot face.

Toate cele trei variante din `pressMe` sunt implicite. Diferența dintre ele este acțiunea și datele:

| Variantă | Acțiune | Date | Efect | Stare |
|---|---|---|---|---|
| 1 | `ACTION_VIEW` | `https://developer.android.com` | deschide browserul implicit | comentată: `Uri` nu e importat |
| 2 | `ACTION_DIAL` | `tel:0212345678` | deschide tastatura telefonică, **fără** să sune | comentată: `Uri` nu e importat |
| 3 | `ACTION_SEND` | `text/plain` + `EXTRA_TEXT` | deschide share sheet-ul | activă |

**De ce primele două sunt comentate:** sunt demonstrații păstrate în cod ca material didactic. Ambele folosesc `Uri.parse(...)`, iar `android.net.Uri` **nu** apare în lista de importuri. Dacă decomentezi primul bloc, compilatorul dă `cannot find symbol: class Uri`. Adaugă `import android.net.Uri;` și compilează.

**De ce `ACTION_DIAL` și nu `ACTION_CALL`:** `ACTION_DIAL` deschide tastatura cu numărul completat, iar utilizatorul apasă butonul de apel. Nu are nevoie de permisiunea `CALL_PHONE`. `ACTION_CALL` ar suna direct și ar cere permisiunea în manifest și la runtime.

**De ce `ACTION_SEND` + `setType("text/plain")`:** un `Intent` implicit declară doar **ce operație** vrei, nu și clasa care o execută. Sistemul caută aplicațiile care au un `<intent-filter>` potrivit. `setType` este filtrul principal: fără el, sistemul nu știe ce aplicații pot primi `Intent`-ul.

| Linie ștearsă | Efect |
|---|---|
| `share.setType("text/plain")` | nicio aplicație nu se potrivește; chooser-ul apare gol („No apps can perform this action"), iar `startActivity` direct ar da `ActivityNotFoundException` |
| `share.putExtra(Intent.EXTRA_TEXT, "Hello!")` | share sheet-ul se deschide, dar textul trimis e gol |
| `Intent.createChooser(...)` | Android poate deschide direct aplicația implicită de share, fără dialog |
| `startActivity(...)` | `Intent`-ul e construit și aruncat; nu se întâmplă nimic |

**De ce `Intent.EXTRA_TEXT` și nu `"android.intent.extra.TEXT"`:** constanta are exact aceeași valoare, dar numele e verificat de compilator. Un string scris de mână greșit nu dă eroare — doar textul nu ajunge nicăieri.

**De ce `createChooser`:** `ACTION_SEND` singur respectă aplicația implicită de share. `createChooser(intent, title)` forțează **mereu** dialogul de alegere, cu titlul dat („Share via DMA"). E util când vrei ca utilizatorul să decidă conștient. Intern, `createChooser` construiește un `Intent` cu acțiunea `ACTION_CHOOSER`, pune `Intent`-ul original în `EXTRA_INTENT` și titlul în `EXTRA_TITLE`.

### 25.2.5 Fluxul share sheet-ului

```
pressMe(view)
  │
  ├─ 1. new Intent(Intent.ACTION_SEND)          acțiune = „trimite"
  ├─ 2. share.setType("text/plain")             MIME = ce fel de conținut
  ├─ 3. share.putExtra(EXTRA_TEXT, "Hello!")    payload-ul
  └─ 4. Intent.createChooser(share, "Share via DMA")
        │
        ▼
   PackageManager.queryIntentActivities(intent, MATCH_DEFAULT_ONLY)
        │  caută TOATE aplicațiile cu <intent-filter> care acceptă
        │  ACTION_SEND + text/plain + category DEFAULT
        ▼
   ┌─────────────────────────────────────────────┐
   │  Share via DMA                              │
   │  ┌───────────┐ ┌───────────┐ ┌───────────┐  │
   │  │ Gmail     │ │ Messages  │ │ DMA02     │  │  ← DMA02 apare datorită
   │  └───────────┘ └───────────┘ └───────────┘  │    filtrului din manifest
   └─────────────────────────────────────────────┘
        │
        ▼
   aplicația aleasă primește Intent-ul cu EXTRA_TEXT = "Hello!"
```

**Bucla care se închide:** manifestul declară un `<intent-filter>` pentru `ACTION_SEND` + `text/plain` (secțiunea 25.3). Deci **DMA02 apare în propriul share sheet**. Dacă o alegi, pornește o **a doua** instanță de `MainActivity` (launch mode standard), iar prima trece prin `onPause` → `onStop`. Și, pentru că `MainActivity` nu citește niciodată `getIntent().getStringExtra(Intent.EXTRA_TEXT)`, textul primit e ignorat: vezi doar un ecran nou, identic.

**De ce `startActivity` și nu `startActivityForResult`:** nu ai nevoie de niciun rezultat înapoi. `startActivityForResult` (sau `registerForActivityResult`) se folosește când aștepți date — ca în `G1097`, la formular.

### 25.2.6 Ce se strică dacă ștergi fiecare lucru din `MainActivity`

| Element șters | Efect |
|---|---|
| `extends AppCompatActivity` | nu mai compilează: `super.onCreate`, `setContentView` și `onCreate` nu există în `Object` |
| `super.onCreate(savedInstanceState)` | `SuperNotCalledException` la pornire |
| `setContentView(...)` | ecran alb; orice `findViewById` ar întoarce `null` |
| o metodă de ciclu de viață | nimic funcțional; dispare doar rândul din Logcat |
| `super.onX()` dintr-o metodă | `SuperNotCalledException` după acea metodă |
| `public` din `pressMe` | reflecția nu găsește metoda: `IllegalStateException` la click |
| `pressMe` întreagă | `android:onClick` nu are ce chema: `IllegalStateException` la click |
| `share.setType(...)` | chooser gol: nicio aplicație nu se potrivește |
| `Intent.createChooser(...)` | se poate deschide direct aplicația implicită, fără dialog |

### 25.2.7 Ce nu face proiectul (și de ce contează)

DMA02 este un schelet didactic. Lipsesc intenționat câteva lucruri pe care le vei vedea în proiectele următoare:

| Lipsește | Unde apare | Ce înseamnă |
|---|---|---|
| `EdgeToEdge` + listener de insets | `G1097` | pe Android 15+ conținutul intră sub bara de stare |
| View Binding | `DMA05` | `findViewById` întoarce `View` generic, cu cast manual |
| `onSaveInstanceState` | `G1097` | starea se pierde la rotire |
| meniu de opțiuni | `DMA03` | nu există `onCreateOptionsMenu` |
| a doua activitate | `G1097` | nu există navigare, doar un ecran |

**De ce contează:** fiecare lipsă este un concept care apare într-un capitol următor. Dacă înțelegi ce **nu** face DMA02, înțelegi mai bine ce adaugă celelalte proiecte. De exemplu, `EdgeToEdge` nu este o funcție estetică: este consecința faptului că, din Android 15, aplicațiile cu `targetSdk ≥ 35` desenează implicit sub barele sistemului.

> DMA02 are `targetSdk = 37`, deci pe un dispozitiv Android 15+ rulează deja edge-to-edge, doar că fără să trateze insets-urile. Toolbar-ul poate intra sub ceas. Este prima „datorie tehnică" pe care o rezolvă `G1097`.

---

## 25.3 `AndroidManifest.xml`

### 25.3.1 Fișierul complet, adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ↑ declarația XML: prima linie obligatorie. Un comentariu ÎNAINTEA ei ar face
     documentul invalid, de aceea antetul stă după ea. -->

<!--
  ======================================================================================
  AndroidManifest.xml — CONTRACTUL APLICAȚIEI CU SISTEMUL ANDROID
  ======================================================================================
  CE ESTE:
    Fișierul care spune sistemului ce componente are aplicația, ce permisiuni cere și
    ce `Intent`-uri acceptă. Fără el, APK-ul nu se poate instala.

  DE CE EXISTĂ:
    1. leagă `DMA02App` de runtime (`android:name=".DMA02App"`);
    2. declară `MainActivity` și filtrul care o face vizibilă în launcher;
    3. declară filtrul care face aplicația vizibilă în share sheet.

  CE SE STRICĂ FĂRĂ EL:
    - fără `<application android:name>`, `DMA02App` nu e instanțiat: tăcere;
    - fără `MAIN` + `LAUNCHER`, aplicația nu apare în launcher;
    - fără `exported="true"`, build-ul eșuează pe targetSdk ≥ 31.

  REF: AndroidManifest.xml (Android 36); build.gradle.kts, `namespace`.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: manifestul ca registru de componente
  ======================================================================================
  1. `<manifest>` — rădăcina. Conține `package` (sau `namespace` în build.gradle.kts)
     și namespace-urile XML.
  2. `<application>` — un singur nod per APK. Atributele lui se aplică întregii
     aplicații: nume, icon, temă, backup.
  3. `<activity>` — o componentă cu fereastră. Fiecare are `android:name` și, dacă
     are `<intent-filter>`, `android:exported`.
  4. `<intent-filter>` — ce `Intent`-uri acceptă componenta. `MAIN` + `LAUNCHER` =
     punct de intrare; `SEND` + `DEFAULT` + `text/plain` = receptor de share.
  ======================================================================================
-->

<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
    <!-- ↑ xmlns:android = prefixul tuturor atributelor android:.
         xmlns:tools = prefixul tools:; aici e declarat, dar niciun atribut tools:
         nu apare în fișier — rămășiță din șablon. -->

    <!--
      ==================================================================================
      NODUL <application> — atributele globale ale aplicației
      ==================================================================================
      android:name=".DMA02App"              ← LEGĂTURA cu DMA02App.java
      android:allowBackup="true"            ← backup automat al datelor
      android:dataExtractionRules="..."     ← reguli de backup pentru Android 12+
      android:fullBackupContent="..."       ← reguli de backup pentru Android 11 și mai jos
      android:icon / roundIcon              ← iconul din launcher
      android:label="@string/app_name"      ← numele afișat: „DMA02"
      android:supportsRtl="true"            ← oglindire pentru limbi RTL
      android:theme="@style/Theme.DMA02"    ← tema aplicației
      ==================================================================================
    -->
    <application
        android:name=".DMA02App"
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA02">
        <!-- ↑ după `>` putem pune comentarii: sunt între elemente, nu în interiorul
             tag-ului. În interiorul unui tag XML, între atribute, un comentariu ar
             face documentul invalid. -->

        <!--
          ==================================================================================
          ACTIVITATEA PRINCIPALĂ
          ==================================================================================
          android:name=".MainActivity"        ← clasa care se instanțiază
          android:exported="true"             ← obligatoriu: launcher-ul e altă aplicație
          android:windowSoftInputMode="..."   ← comportamentul la tastatură (inert aici)
          ==================================================================================
        -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <!-- ↑ activitatea care apare în launcher și care are layout-ul din 25.4. -->

            <!--
              FILTRUL 1: MAIN + LAUNCHER
              MAIN      = „acesta e punctul de intrare"
              LAUNCHER  = „arată-mă în launcher"
            -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <!-- ↑ fără acest filtru, aplicația nu apare în launcher. -->

            <!--
              FILTRUL 2: SEND + DEFAULT + text/plain
              SEND       = „primesc conținut trimis de alte aplicații"
              DEFAULT    = obligatoriu pentru rezolvarea implicită
              text/plain = doar text simplu
              → aplicația apare în share sheet-ul propriu și al altora.
            -->
                <intent-filter>
                    <action android:name="android.intent.action.SEND" />
                    <category android:name="android.intent.category.DEFAULT" />
                    <data android:mimeType="text/plain" />
                </intent-filter>
            <!-- ↑ indentarea inconsistentă (16 spații) e în repo; nu schimbă nimic. -->


        </activity>
    </application>

</manifest>
```

### 25.3.2 `android:name=".DMA02App"` — legătura cu codul

Aceasta este cea mai importantă linie din fișier, pentru că este singura legătură dintre clasa din 25.1 și runtime.

```
AndroidManifest.xml                         Runtime
───────────────────                         ───────
android:name=".DMA02App"   ─────────────►   ro.ase.ie.dma02.DMA02App
                                            (punctul = relativ la `namespace`)

lipsește                   ─────────────►   android.app.Application
                                            (clasa ta NU e instanțiată: tăcere)

nume greșit                ─────────────►   ClassNotFoundException la pornire
```

**De ce punctul:** în manifest, un nume care începe cu `.` este relativ la pachetul aplicației. Aici `namespace = "ro.ase.ie.dma02"` în `build.gradle.kts`, deci `.DMA02App` înseamnă `ro.ase.ie.dma02.DMA02App`. Poți scrie și numele complet, fără punct; ambele sunt echivalente.

**Ce se întâmplă dacă uiți linia:** Android folosește `android.app.Application` implicit. `DMA02App` nu este niciodată creată, deci `onCreate()` nu rulează, callback-urile nu se înregistrează, `DynamicColors` nu se aplică și primul log nu apare. Aplicația arată și funcționează identic. **Nicio eroare. Doar tăcere.** Este capcana clasică a laboratorului: crezi că ai scris codul, dar codul nu rulează.

**Ce se întâmplă dacă numele e greșit:** la pornire, `ActivityThread` încearcă să instanțieze clasa și eșuează cu `Unable to instantiate application ro.ase.ie.dma02.DMA02App: java.lang.ClassNotFoundException`. Aici eroarea e zgomotoasă, deci e mai ușor de găsit decât lipsa liniei.

### 25.3.3 `android:exported="true"` — obligatoriu, nu opțional

Din Android 12 (API 31), orice componentă cu `<intent-filter>` trebuie să declare explicit `android:exported`. Fără atribut, build-ul eșuează:

```
Apps targeting Android 12 and higher are required to specify an explicit value
for `android:exported` when the corresponding component has an intent filter defined.
```

**De ce `true` aici:** launcher-ul este **altă** aplicație. Ca să poată porni `MainActivity`, componenta trebuie să fie exportată. Dacă ai pune `false`, launcher-ul (alt UID) nu ar mai vedea activitatea: aplicația nu ar mai apărea în launcher.

**De ce nu e o problemă de securitate:** activitatea nu face nimic sensibil: afișează un text și un buton. Dacă ar citi date private, ai limita accesul cu permisiuni sau ai verifica apelantul.

### 25.3.4 Cele două `<intent-filter>`-uri

| Filtru | Acțiune | Categorie | Date | Efect |
|---|---|---|---|---|
| 1 | `android.intent.action.MAIN` | `android.intent.category.LAUNCHER` | — | aplicația apare în launcher |
| 2 | `android.intent.action.SEND` | `android.intent.category.DEFAULT` | `text/plain` | aplicația apare în share sheet |

**Filtrul 1 — `MAIN` + `LAUNCHER`:** `MAIN` spune „acesta e punctul de intrare"; `LAUNCHER` spune „arată-mă în launcher". Fără el, aplicația se poate porni doar din altă aplicație sau din `adb`, nu din iconiță.

**Filtrul 2 — `SEND` + `DEFAULT` + `text/plain`:** filtrează ce `Intent`-uri implicite acceptă activitatea.

- `SEND` = acțiunea „trimite conținut";
- `DEFAULT` = obligatoriu pentru `startActivity`: sistemul rezolvă cu `MATCH_DEFAULT_ONLY`, deci un filtru fără `DEFAULT` nu se potrivește niciodată;
- `text/plain` = limitează la text simplu. Fără el, aplicația ar apărea la share pentru orice tip de conținut.

> Filtrul e **doar receptor**. Codul nu citește textul primit, deci aplicația apare în share sheet și îl ignoră. E jumătatea a doua a demonstrației din 25.2.5.

**De ce `DEFAULT` și nu `LAUNCHER` la al doilea filtru:** `LAUNCHER` ar însemna „arată-mă în launcher" — nu are sens aici. `DEFAULT` este categoria cerută de rezolvarea implicită; fără ea, filtrul nu este luat în calcul de `PackageManager`.

### 25.3.5 Atributele din `<application>`

| Atribut | Ce face | Dacă îl ștergi |
|---|---|---|
| `android:name` | leagă clasa `Application` | clasa nu rulează; fără eroare, doar tăcere |
| `android:allowBackup` | permite backup automat al datelor aplicației | se aplică default-ul (`true` pe majoritatea dispozitivelor) |
| `android:dataExtractionRules` | regulile de backup/transfer pentru **Android 12+** | se aplică regulile implicite |
| `android:fullBackupContent` | regulile de backup pentru **Android 11 și mai jos** | se aplică regulile implicite |
| `android:icon` | iconul din launcher | iconul implicit al sistemului |
| `android:label` | numele afișat sub icon și în recents | numele aplicației devine numele pachetului |
| `android:roundIcon` | varianta rotundă pentru launcere care o cer | se folosește `android:icon` |
| `android:supportsRtl` | oglindește layout-urile pentru limbi RTL | interfața nu se mai oglindește |
| `android:theme` | tema aplicației | tema de platformă: componentele Material nu mai arată corect |

**De ce două fișiere de backup:** `fullBackupContent` e citit de Android 11 și mai jos; `dataExtractionRules` de Android 12+. Ambele sunt generate de șablon și acoperă două intervale de API. Dacă ștergi fișierele `res/xml/backup_rules.xml` și `data_extraction_rules.xml` dar lași atributele, build-ul eșuează cu „resource not found".

**De ce `android:label="@string/app_name"`:** numele „DMA02" stă în `res/values/strings.xml`, nu hardcodat în manifest. Așa poate fi tradus, iar lint-ul nu dă `HardcodedText`.

### 25.3.6 Tema: `Theme.DMA02`

`Theme.DMA02` e definit în `res/values/themes.xml` ca `parent="Base.Theme.DMA02"`, iar `Base.Theme.DMA02` are **doi** părinți, în funcție de modul sistemului:

| Fișier | Părinte | Efect |
|---|---|---|
| `values/themes.xml` (mod light) | `Theme.Material3.Dark` | aplicația e **întunecată** și are ActionBar |
| `values-night/themes.xml` (mod night) | `Theme.Material3.DayNight.NoActionBar` | aplicația e întunecată și **nu** are ActionBar |

Rezultatul e o inconsecvență reală a repo-ului: aplicația e mereu dark, iar bara de titlu a ferestrei apare doar în modul light — acolo unde, peste ea, mai există și `MaterialToolbar`-ul din layout. Nu crapă nimic, dar explică de ce ecranul arată diferit cu tema sistemului pe light față de night.

> `Theme.Material3.Dark` nu este o temă `DayNight`: în modul light rămâne dark. De aceea aplicația nu urmează setarea sistemului, ci doar o ignoră. `Theme.Material3.DayNight.NoActionBar` din `values-night` ar fi urmat-o, dar e folosită doar noaptea.

### 25.3.7 Ce se strică dacă ștergi fiecare lucru din manifest

| Element șters | Efect |
|---|---|
| `android:name=".DMA02App"` | `DMA02App` nu rulează: nicio eroare, doar tăcere |
| `android:name=".MainActivity"` | build-ul eșuează: activitatea nu are nume |
| `android:exported="true"` | build-ul eșuează pe targetSdk ≥ 31 |
| filtrul `MAIN` + `LAUNCHER` | aplicația nu apare în launcher |
| filtrul `SEND` + `DEFAULT` + `text/plain` | aplicația nu mai apare în share sheet |
| `android:theme` | tema de platformă: `AppCompatActivity` crapă la pornire |
| `android:icon` / `roundIcon` | iconul implicit al sistemului |
| `android:label` | numele aplicației devine numele pachetului |
| `xmlns:android` | toate atributele `android:` devin invalide: build eșuează |
| `xmlns:tools` | nimic: e declarat, dar nefolosit în manifest |

### 25.3.8 De ce nu există `<uses-permission>`

Manifestul nu declară nicio permisiune. Nu e o omisiune: acțiunile folosite nu cer una.

| Acțiune | Permisiune necesară | De ce |
|---|---|---|
| `ACTION_SEND` | niciuna | trimite prin alte aplicații; ele au grijă de permisiuni |
| `ACTION_VIEW` + `https://` | niciuna | browserul are deja `INTERNET` |
| `ACTION_DIAL` | niciuna | deschide tastatura, nu sună |
| `ACTION_CALL` | `CALL_PHONE` | ar suna direct — nu e folosit |

> Dacă ai adăuga `ACTION_CALL`, ar trebui `<uses-permission android:name="android.permission.CALL_PHONE" />` în manifest **și** o cerere la runtime (Android 6+). DMA02 nu are nevoie de nimic din toate astea.

---

## 25.4 `activity_main.xml`

### 25.4.1 Fișierul complet, adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ↑ declarația XML: prima linie obligatorie. -->

<!--
  ======================================================================================
  activity_main.xml — ARBORELE DE VIEW-URI AL ECRANULUI
  ======================================================================================
  CE ESTE:
    Layout-ul inflat de `setContentView(R.layout.activity_main)` în MainActivity.onCreate.
    Un ConstraintLayout cu trei copii: un toolbar, un text centrat și un buton.

  DE CE EXISTĂ:
    1. definește ce se vede pe ecran;
    2. leagă butonul de metoda `pressMe` prin `android:onClick`;
    3. dă id-urile folosite de cod (`main`, `toolbar`, `textView`, `button`).

  CE SE STRICĂ FĂRĂ EL:
    - `R.layout.activity_main` nu mai există: build-ul eșuează;
    - fără `Button`, `pressMe` nu poate fi chemat;
    - fără `android:onClick`, click-ul nu face nimic.

  REF: activity_main.xml; R.layout.activity_main; MainActivity.onCreate.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: ConstraintLayout și legăturile XML → cod
  ======================================================================================
  1. CONSTRAINTS, NU ORDINE
     Fiecare copil e poziționat prin relații față de părinte sau față de frați, nu
     prin ordinea din fișier. Un view fără constraints e plasat la (0,0).

  2. `@+id/...` vs `@id/...`
     `@+id/textView` creează id-ul dacă nu există; `@id/textView` îl referă.
     În practică, `@+id` funcționează și când id-ul există deja.

  3. `android:onClick` — REFLECȚIE
     Nu e o legătură de compilare. La click, framework-ul caută în Context-ul
     view-ului o metodă `public void` cu exact un parametru `View`.

  4. `?attr/...` — valori din temă
     `?attr/actionBarSize` și `?attr/textAppearanceBodyLarge` se rezolvă la runtime
     din tema activității, nu sunt valori fixe.
  ======================================================================================
-->

<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">
    <!-- ↑ rădăcina: ConstraintLayout, id `main` (nefolosit în DMA02, folosit în G1097
         pentru insets). `tools:context` e doar pentru previzualizarea din IDE și
         dispare la build. -->

    <!--
      ==================================================================================
      MATERIALTOOLBAR — bara de titlu desenată de aplicație
      ==================================================================================
      android:id="@+id/toolbar"                    ← id-ul view-ului (nefolosit în cod)
      android:layout_width="match_parent"          ← ocupă toată lățimea
      android:layout_height="?attr/actionBarSize"  ← înălțimea standard a barei (56dp)
      app:title="@string/app_name"                 ← titlul: „DMA02"
      Fără constraints → plasat la (0,0) de ConstraintLayout.
      ==================================================================================
    -->
    <com.google.android.material.appbar.MaterialToolbar
        android:id="@+id/toolbar"
        android:layout_width="match_parent"
        android:layout_height="?attr/actionBarSize"
        app:title="@string/app_name"/>
    <!-- ↑ NU e setat ca ActionBar: nu există `setSupportActionBar(toolbar)`. -->

    <!--
      ==================================================================================
      TEXTVIEW — textul centrat
      ==================================================================================
      android:text="Hello World!"                             ← text hardcodat
      android:textAppearance="?attr/textAppearanceBodyLarge"  ← stilul tipografic din temă
      patru constraints față de parent                        ← centrat pe ambele axe
      ==================================================================================
    -->
    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        android:textAppearance="?attr/textAppearanceBodyLarge"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    <!-- ↑ `wrap_content` + patru constraints = centrat, cu dimensiunea textului. -->

    <!--
      ==================================================================================
      BUTTON — singura legătură XML → cod din proiect
      ==================================================================================
      android:onClick="pressMe"                             ← numele metodei din MainActivity
      app:layout_constraintBottom_toTopOf="@+id/textView"   ← se așază deasupra textului
      app:layout_constraintTop_toTopOf="parent"             ← pornește de sus
      ==================================================================================
    -->
    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Button"
        app:layout_constraintBottom_toTopOf="@+id/textView"
        app:layout_constraintEnd_toEndOf="parent"
        android:onClick="pressMe"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    <!-- ↑ click → reflecție → MainActivity.pressMe(view). -->

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 25.4.2 De ce `ConstraintLayout`

Fiecare copil e poziționat prin **relații** față de părinte sau față de frați, nu prin ordine. E layout-ul generat de șablonul „Empty Views Activity" și e potrivit pentru ecrane simple: un text centrat, un buton deasupra lui.

**De ce `android:id="@+id/main"`:** în DMA02 nu e folosit nicăieri — nicio linie de cod nu face `findViewById(R.id.main)`. În `G1097` devine esențial: `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` are nevoie de el. Dacă îl ștergi aici, DMA02 merge în continuare; dacă îl ștergi în `G1097`, codul care face `findViewById(R.id.main)` nu mai compilează.

**De ce `tools:context=".MainActivity"`:** îi spune IDE-ului ce activitate să folosească pentru previzualizare (temă, rezolvarea `android:onClick`). La build, atributul e eliminat — nu ajunge în APK.

### 25.4.3 `MaterialToolbar`

Atributele care contează sunt `android:layout_height="?attr/actionBarSize"` și `app:title="@string/app_name"`. `?attr/actionBarSize` ia înălțimea standard a barei (56dp) din temă. `app:title` e atributul Material, nu `android:title`. Toolbar-ul are `match_parent` pe lățime și **niciun constraint** — în `ConstraintLayout`, un view fără constraints e plasat la colțul (0,0) cu dimensiunea măsurată. Funcționează, dar „din întâmplare": dacă adaugi alt view deasupra, toolbar-ul nu se mișcă.

> Niciun cod nu apelează `setSupportActionBar(toolbar)`. Deci toolbar-ul e doar un view stilizat cu un titlu, nu ActionBar-ul activității: nu primește meniu de opțiuni, nu primește buton de navigare înapoi.

### 25.4.4 `TextView`

Atributele care contează sunt `android:text="Hello World!"` și `android:textAppearance="?attr/textAppearanceBodyLarge"`. Patru constraints (sus, jos, start, end) față de părinte = centrat pe ambele axe. `?attr/textAppearanceBodyLarge` ia stilul tipografic „body large" din tema Material 3 (16sp), în loc să hardcodezi `textSize`.

> `"Hello World!"` e text hardcodat: lint-ul dă avertisment `HardcodedText`, iar textul nu poate fi tradus. Corect ar fi `@string/hello_world` în `strings.xml`.

### 25.4.5 `Button` și `android:onClick`

Atributele care contează sunt `android:onClick="pressMe"` și `app:layout_constraintBottom_toTopOf="@+id/textView"`. Butonul e legat de `TextView` prin `bottom_toTopOf`: se așază deasupra textului, centrat orizontal. Împreună cu `top_toTopOf="parent"`, ocupă jumătatea de sus a ecranului. `@+id/textView` funcționează și fără `+` (id-ul e deja declarat mai sus), dar e inofensiv.

**Cum se leagă `android:onClick` de cod:** la click, `View`-ul caută în lanțul de `Context`-uri (activitate, aplicație) o metodă `public`, cu return `void`, cu exact un parametru `View`, al cărei nume este `pressMe`. Dacă nu o găsește, aruncă:

```
IllegalStateException: Could not find method pressMe(View) in a parent or ancestor Context
for android:onClick attribute defined on view class android.widget.Button ...
```

> `android:onClick` este **singura** legătură dintre XML și cod din tot proiectul. Numele din XML trebuie să fie identic cu metoda din `MainActivity` — altfel `IllegalStateException` la click, nu la compilare.

### 25.4.6 Ce se strică dacă ștergi fiecare bloc din layout

| Bloc șters | Efect |
|---|---|
| `Button`-ul | `pressMe` nu mai poate fi chemat; aplicația afișează doar textul |
| `android:onClick="pressMe"` | click-ul nu face nimic; nicio eroare, nicio urmă în Logcat |
| `TextView`-ul | referința `bottom_toTopOf` rămâne fără țintă: constraint-ul e ignorat, iar butonul se lipește de marginea de sus |
| `MaterialToolbar` | ecranul rămâne fără titlu; restul merge |
| `android:id="@+id/main"` | nimic în DMA02; `G1097` nu ar mai compila |
| `xmlns:app` | toate atributele `app:` devin invalide → build eșuează |
| `xmlns:tools` | `tools:context` devine invalid → build eșuează |
| `tools:context` | doar previzualizarea din IDE pierde tema; build-ul merge |

### 25.4.7 Ordinea atributelor nu contează

În XML, ordinea atributelor dintr-un tag este irelevantă pentru runtime. `android:id` poate fi primul sau ultimul; `android:onClick` poate sta oriunde. Ordinea din fișier este o convenție de lizibilitate (și, uneori, ordinea în care le-a scris șablonul).

> Ce **contează** este ordinea **elementelor**: `ConstraintLayout` nu depinde de ea, dar un `LinearLayout` da. În DMA02 totul e `ConstraintLayout`, deci ordinea copiilor nu schimbă pozițiile — doar ordinea de desenare (z-order), iar aici nu se suprapun.

---

## 25.5 Fluxul complet

### 25.5.1 Pornirea procesului și prima activitate

```
PORNIREA PROCESULUI
  Zygote → fork → ActivityThread.main
    ├── Application.attachBaseContext()                 (nu apare în cod)
    ├── ContentProvider.onCreate()                      (dacă există; nu e cazul aici)
    └── DMA02App.onCreate()
          ├── super.onCreate()
          ├── registerActivityLifecycleCallbacks(this)
          ├── DynamicColors.applyToActivitiesIfAvailable(this)
          └── Log.w("DMA02App", "onCreate")
                ↓
  MainActivity (instanță nouă)
    ├── DMA02App.onActivityCreated(MainActivity, null)  ← din interiorul super.onCreate
    ├── MainActivity.onCreate
    │     ├── super.onCreate(...)          → dispatch-ul de mai sus
    │     ├── setContentView(activity_main)
    │     └── Log.w("MainActivity", "onCreate")
    ├── DMA02App.onActivityStarted   → MainActivity.onStart   → Log
    ├── DMA02App.onActivityResumed   → MainActivity.onResume  → Log
    └── ecranul e vizibil
```

**Ce se citește din diagramă:**

1. `Application.onCreate` rulează **înaintea** oricărei activități — de aceea abonarea și tema stau acolo.
2. Fiecare metodă a activității are un callback pereche, declanșat din interiorul lui `super`.
3. `setContentView` rulează **după** `onActivityCreated`, deci callback-ul nu poate atinge view-urile.
4. La rotire, lanțul complet de distrugere și creare rulează din nou — de aceea `onCreate` apare de două ori în Logcat.

### 25.5.2 Apăsarea butonului și share sheet-ul

```
APĂSARE BUTON
  Button.onClick → reflecție → MainActivity.pressMe(view)
    ├── new Intent(ACTION_SEND)
    ├── setType("text/plain")
    ├── putExtra(EXTRA_TEXT, "Hello!")
    └── startActivity(createChooser(share, "Share via DMA"))
          ↓
  MainActivity.onPause → onStop          (chooser-ul e altă activitate, peste ea)
  ChooserActivity se deschide
    ├── în listă apare și DMA02 (filtrul SEND din manifest)
    └── alegi o aplicație
          ↓
  MainActivity.onStart → onResume        (la revenire)
```

**De ce `onPause` → `onStop` și nu `onDestroy`:** chooser-ul este o activitate a sistemului, deschisă **peste** `MainActivity`. Activitatea ta nu este distrusă, doar ascunsă. La revenire, `onStart` → `onResume`, fără `onCreate`.

**Dacă alegi DMA02 din chooser:** se creează o instanță **nouă** de `MainActivity`, iar cea veche rămâne în spate. Textul `"Hello!"` este ignorat, pentru că `MainActivity` nu citește `getIntent()`. Este demonstrația completă a unui `Intent` implicit: emițătorul și receptorul sunt aceeași aplicație.

### 25.5.3 Back, Home și rotire

```
APĂSARE BACK (din MainActivity)
  onPause → onStop → onDestroy
    └── DMA02App.onActivityDestroyed

APĂSARE HOME
  onPause → onStop
    └── procesul poate fi omorât oricând de sistem

REVENIRE DIN HOME
  onRestart → onStart → onResume
    └── `onRestart` NU e suprascris în MainActivity, deci nu apare în Logcat

ROTIRE
  onPause → onStop → onSaveInstanceState → onDestroy
  → onActivityCreated → onCreate → onStart → onResume    (instanță nouă!)
```

**De ce rotirea e cel mai bun test:** parcurge aproape tot ciclul, de două ori, și demonstrează că `onCreate` nu rulează o singură dată per aplicație, ci o dată per instanță de activitate. În Logcat vezi:

```
DMA02App:      onActivityPausedMainActivity
MainActivity:  onPause
DMA02App:      onActivityStoppedMainActivity
MainActivity:  onStop
DMA02App:      onActivityDestroyedMainActivity
MainActivity:  onDestroy
DMA02App:      onActivityCreatedMainActivity
MainActivity:  onCreate
DMA02App:      onActivityStartedMainActivity
MainActivity:  onStart
DMA02App:      onActivityResumedMainActivity
MainActivity:  onResume
```

**De ce `Application.onCreate` nu apare a doua oară:** procesul nu a murit. `Application` trăiește cât trăiește procesul, nu cât trăiește activitatea. La rotire se recreează doar activitatea.

### 25.5.4 Tabel de scenarii

| Scenariu | Secvența metodelor | Ce apare în Logcat |
|---|---|---|
| Pornire din launcher | `onCreate → onStart → onResume` | `onActivityCreatedMainActivity`, `onCreate`, `onActivityStartedMainActivity`, `onStart`, `onActivityResumedMainActivity`, `onResume` |
| Home | `onPause → onStop` | `onActivityPausedMainActivity`, `onPause`, `onActivityStoppedMainActivity`, `onStop` |
| Revenire din Home | `onRestart → onStart → onResume` | `onActivityStartedMainActivity`, `onStart`, `onActivityResumedMainActivity`, `onResume` |
| Back | `onPause → onStop → onDestroy` | `onActivityPausedMainActivity`, `onPause`, `onActivityStoppedMainActivity`, `onStop`, `onActivityDestroyedMainActivity`, `onDestroy` |
| Rotire | `onPause → onStop → onSaveInstanceState → onDestroy → onCreate → onStart → onResume` | cele două lanțuri, unul după altul |
| Share sheet | `onPause → onStop`, apoi `onStart → onResume` la revenire | `onActivityPausedMainActivity`, `onPause`, `onActivityStoppedMainActivity`, `onStop`, apoi `onActivityStartedMainActivity`, `onStart`, `onActivityResumedMainActivity`, `onResume` |

**De ce `onRestart` nu apare în coloana din dreapta:** `MainActivity` nu îl suprascrie, deci nu scrie nimic în Logcat. Framework-ul îl apelează, dar nu ai un rând pentru el. Este singurul „gol" al demonstrației: șase metode sunt logate, a șaptea nu.

> Dacă vrei să-l vezi, adaugi în `MainActivity` o metodă `onRestart()` care apelează `super.onRestart()` și scrie `Log.w(TAG, "onRestart")`. Nu e în proiect, dar mecanismul este identic cu celelalte șase.

---

## 25.6 Capcane reale în DMA02

| Loc | Capcană | Efect |
|---|---|---|
| `MainActivity` | `Uri` nu e importat | decomentezi blocul `ACTION_VIEW` → nu compilează |
| `MainActivity` | metodele sunt în ordine alfabetică | ordinea din fișier ≠ ordinea de execuție |
| `MainActivity` | fără `EdgeToEdge` + insets | pe Android 15+ conținutul intră sub bara de stare |
| `MainActivity` | `pressMe` fără `public` | reflecția nu găsește metoda: crash la click |
| `AndroidManifest.xml` | filtrul `SEND` nu e citit în cod | aplicația apare în share sheet, dar ignoră textul |
| `AndroidManifest.xml` | `adjustResize` fără câmpuri de text | atribut inert |
| `AndroidManifest.xml` | `xmlns:tools` declarat, dar nefolosit | zgomot, nu bug |
| `AndroidManifest.xml` | `android:name` absent | `DMA02App` nu rulează: tăcere |
| `themes.xml` | `Theme.Material3.Dark` în `values`, `DayNight.NoActionBar` în `values-night` | aplicația e mereu dark; ActionBar doar în modul light |
| `activity_main.xml` | toolbar fără constraints | plasat la (0,0) „din întâmplare" |
| `activity_main.xml` | `"Hello World!"` și `"Button"` hardcodate | lint `HardcodedText`, fără traducere |
| `activity_main.xml` | `android:id="@+id/main"` nefolosit | cod mort în DMA02; util în `G1097` |

**Capcana 1 — `Uri` neimportat.** Este singura capcană din codul Java care se manifestă la **compilare**, nu la runtime. De aceea blocurile sunt comentate: codul demonstrativ nu poate rula fără un import suplimentar.

**Capcana 2 — ordinea alfabetică.** Cine citește fișierul de sus în jos crede că `onCreate` este urmat de `onDestroy`. În realitate, `onDestroy` este ultima metodă din ciclu. Ordinea din fișier este o alegere a IDE-ului, nu o afirmație despre runtime.

**Capcana 3 — `EdgeToEdge`.** Proiectul are `targetSdk = 37`. Pe Android 15+ (API 35+), aplicațiile cu `targetSdk ≥ 35` rulează implicit edge-to-edge. Fără un listener de insets, conținutul se desenează **sub** bara de stare, iar toolbar-ul intră sub ceas. În `G1097`, `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` rezolvă exact asta.

**Capcana 4 — `android:name` absent.** Nu produce nicio eroare. Este capcana „tăcută" a laboratorului: aplicația arată identic, dar `DMA02App` nu rulează. Singura dovadă este lipsa rândului `DMA02App: onCreate` din Logcat.

**Capcana 5 — tema.** `Theme.Material3.Dark` în `values` și `Theme.Material3.DayNight.NoActionBar` în `values-night` produc o aplicație mereu dark, cu ActionBar doar în modul light. Nu crapă, dar arată inconsistent.

### 25.6.1 Trei capcane de citire

**1. `Log.w` nu înseamnă „eroare".** Nivelul `w` este warning, nu error. Mesajele din DMA02 sunt demonstrații, nu probleme. Dacă filtrezi Logcat la `Error`, nu vezi niciunul.

**2. `onCreate` nu înseamnă „o dată per aplicație".** Înseamnă „o dată per instanță de activitate". La rotire, `MainActivity.onCreate` rulează din nou; `DMA02App.onCreate` nu.

**3. `Application` nu înseamnă „pornirea aplicației".** Procesul poate exista și fără o activitate vizibilă (de exemplu, un `ContentProvider` sau un `Service`). `Application.onCreate` rulează la pornirea procesului, nu la deschiderea ecranului.

---

## 25.7 Ce să reții

| Fișier | Esența |
|---|---|
| `DMA02App.java` | `Application` + `ActivityLifecycleCallbacks`; `onCreate` rulează înaintea oricărei activități; `DynamicColors` se aplică global, o singură dată |
| `MainActivity.java` | șase metode de ciclu de viață, toate cu `super` primul; `pressMe` = `Intent` implicit cu `ACTION_SEND` |
| `AndroidManifest.xml` | `android:name=".DMA02App"` leagă clasa; `exported="true"` obligatoriu; două filtre: `LAUNCHER` și `SEND` |
| `activity_main.xml` | `ConstraintLayout`; `android:onClick="pressMe"` e singura legătură XML → cod |

**Zece afirmații de reținut:**

1. `Application` este **unul per proces**, creat înaintea oricărei activități. Nu are UI și nu are `Bundle`.
2. `Application.onCreate` este locul pentru inițializări globale: abonări, teme, biblioteci.
3. `ActivityLifecycleCallbacks` are **șapte** metode abstracte. Le implementezi pe toate sau nu compilează.
4. Callback-urile se declanșează **din interiorul** metodei de bază (`super.onX()`), nu înaintea ei.
5. Dacă `MainActivity` apelează `super` primul, logul din `Application` apare primul în Logcat.
6. `MainActivity` suprascrie șase metode doar ca să logheze. Ștergerea unei suprascrieri nu strică nimic; ștergerea lui `super` dă `SuperNotCalledException`.
7. Ordinea metodelor în fișier e alfabetică, nu cronologică: `onCreate → onStart → onResume → onPause → onStop → onDestroy`.
8. `android:onClick="pressMe"` cere exact `public void pressMe(View)`; altfel crash la click, nu la build.
9. `ACTION_SEND` fără `setType` nu are țintă; `createChooser` forțează dialogul de alegere.
10. Aplicația apare în propriul share sheet (filtrul `SEND`), dar nu citește textul primit.

### 25.7.1 Corespondența cod ↔ concept

| Construct din cod | Conceptul | Secțiunea |
|---|---|---|
| `extends Application` | obiect unic per proces | 25.1.2 |
| `implements Application.ActivityLifecycleCallbacks` | șablonul observator | 25.1.4 |
| `registerActivityLifecycleCallbacks(this)` | abonarea la toate activitățile | 25.1.4 |
| `DynamicColors.applyToActivitiesIfAvailable(this)` | Material You global | 25.1.6 |
| `Log.w(TAG, ...)` | nivelul de log și vizibilitatea | 25.1.7 |
| `android:name=".DMA02App"` | legătura manifest ↔ clasă | 25.1.5, 25.3.2 |
| `super.onCreate(savedInstanceState)` | contractul `super` | 25.2.3 |
| `setContentView(R.layout.activity_main)` | inflatarea layout-ului | 25.2.1 |
| `android:onClick="pressMe"` | reflecția XML → cod | 25.4.5 |
| `Intent.ACTION_SEND` + `setType` | `Intent` implicit | 25.2.4 |
| `Intent.createChooser(...)` | chooser forțat | 25.2.4 |
| `<intent-filter>` `SEND` + `DEFAULT` | receptorul de share | 25.3.4 |

**Trei lucruri care nu se văd din cod:**

- **Manifestul este jumătate din aplicație.** Fără `android:name`, clasa `Application` este cod mort; fără `MAIN` + `LAUNCHER`, activitatea nu apare în launcher; fără `SEND`, nu apare în share sheet.
- **`DynamicColors` este un no-op sub API 31.** Nu crapă, nu loghează: pur și simplu nu face nimic. În DMA02, `minSdk = 33`, deci nu se întâmplă niciodată.
- **`Log.w` nu înseamnă „eroare".** Înseamnă doar „nivel warning": suficient de sus ca să rămână vizibil când filtrezi Logcat la Info.

---

## Rezumat capitol 25

- `Application` = obiect unic per proces, creat înaintea oricărei activități. Fără `android:name` în manifest, clasa nu există la runtime — nicio eroare, doar tăcere.
- `Application.onCreate` e locul pentru inițializări globale: înregistrarea callback-urilor și `DynamicColors`. Ambele trebuie făcute înainte de prima activitate.
- `ActivityLifecycleCallbacks` are șapte metode abstracte: le implementezi pe toate sau nu compilează. `onActivitySaveInstanceState` e singura goală.
- Callback-urile se declanșează din interiorul metodei de bază (`super.onX()`); pentru că `MainActivity` apelează `super` primul, logul din `Application` apare primul în Logcat.
- `MainActivity` suprascrie șase metode doar ca să logheze. Ștergerea unei suprascrieri nu strică nimic; ștergerea lui `super` dă `SuperNotCalledException`.
- Ordinea metodelor în fișier e alfabetică, nu cronologică: `onCreate → onStart → onResume → onPause → onStop → onDestroy`.
- `android:onClick="pressMe"` cere exact `public void pressMe(View)`; altfel crash la click, nu la build.
- `ACTION_SEND` fără `setType` nu are țintă; `createChooser` forțează dialogul de alegere.
- Aplicația apare în propriul share sheet (filtrul `SEND`), dar nu citește textul primit.
- `Uri` nu e importat: blocurile comentate din `pressMe` nu compilează dacă le decomentezi.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [prezentarea generală](index.html).
