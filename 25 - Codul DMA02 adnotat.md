# Capitolul 25 — Codul DMA02 adnotat

**Obiectiv:** să citești primul proiect al laboratorului linie cu linie — clasa `Application`, ciclul de viață complet, `DynamicColors` și un `Intent` implicit — cu explicații pe fiecare bloc: ce face, de ce e acolo, ce se strică dacă îl ștergi.

**Sursa:** `DMA02/` la commitul `d719ffc` (2026-11-09, „G1097_S07") — 4 fișiere: `DMA02App.java`, `MainActivity.java`, `AndroidManifest.xml`, `activity_main.xml`.

**Ce înveți din el:**
- cum arată ciclul de viață **complet** — cele șase metode suprascrise de `MainActivity` și cele șapte callback-uri care le observă;
- ce face o clasă `Application` și de ce, fără o linie din manifest, nu rulează niciodată;
- cum se activează Material You cu **un singur apel**, global;
- cum se construiește un `Intent` implicit și de ce `setType` nu e opțional.

> **Cum citești:** nu citi pasiv. Pentru fiecare bloc, acoperă explicația și încearcă să spui tu ce face. Dacă nu poți, ai găsit ce trebuie repetat. Proiectul e mic (125 de linii de Java), dar fiecare linie are un motiv — iar la examen întrebările vin exact pe aceste motive.

---

## 25.1 `DMA02App.java` — clasa `Application`

### Fișierul complet, adnotat

```java
package ro.ase.ie.dma02;                    // pachetul aplicației; identic cu `namespace` din build.gradle.kts

import android.app.Activity;                // tipul primit de fiecare callback: activitatea observată
import android.app.Application;             // clasa de bază — obiectul unic al procesului
import android.os.Bundle;                   // starea salvată, primită de două dintre callbacks
import android.util.Log;                    // scrierea în Logcat

import androidx.annotation.NonNull;         // contract pentru lint: parametrul nu are voie să fie null
import androidx.annotation.Nullable;        // contract pentru lint: parametrul poate fi null

import com.google.android.material.color.DynamicColors;   // Material You: culori extrase din wallpaper

public class DMA02App
        extends Application                               // (1) clasa devine Application-ul aplicației
        implements Application.ActivityLifecycleCallbacks {   // (2) se abonează la ciclul de viață al tuturor activităților

    private final String TAG = DMA02App.class.getSimpleName();   // "DMA02App" — eticheta din coloana Tag

    @Override
    public void onCreate() {
        super.onCreate();                                  // lanțul de moștenire; Application.onCreate e gol, dar se apelează
        registerActivityLifecycleCallbacks(this);          // "this" = observatorul; de acum primește toate evenimentele
        DynamicColors.applyToActivitiesIfAvailable(this);  // Material You, dacă dispozitivul îl suportă

        Log.w(TAG, "onCreate");                            // primul mesaj din Logcat — înaintea oricărei activități
    }
```

**De ce `extends Application`:** `Application` e obiectul **unic per proces**, creat de framework înaintea oricărei activități. Extinzându-l, clasa ta devine acel obiect: un loc sigur pentru inițializări globale care trebuie să ruleze o singură dată. Alternativa — să pui `registerActivityLifecycleCallbacks` și `DynamicColors` în `MainActivity.onCreate` — ar însemna să le repeți în fiecare activitate și, mai grav, să ruleze **după** ce prima activitate e deja construită.

**De ce nu e suficientă clasa:** legătura cu framework-ul se face **doar** din manifest, prin `android:name=".DMA02App"` (secțiunea 25.3). Fără acea linie, Android instanțiază `android.app.Application` implicit, iar `DMA02App` rămâne cod mort: compilează, dar nu e niciodată creat. Nicio eroare, doar tăcere în Logcat.

**De ce `implements Application.ActivityLifecycleCallbacks`:** e șablonul **observator**. În loc să suprascrii șapte metode în fiecare activitate, le suprascrii o dată aici și primești evenimente de la **toate** activitățile. În DMA02 există o singură activitate, deci câștigul e mic — dar mecanismul e cel care contează, iar în `G1097` (două activități) devine imediat util.

**De ce `TAG`:** în Logcat, mesajele sunt grupate pe tag. `getSimpleName()` întoarce `"DMA02App"`, fără pachet; `getName()` ar fi dat `ro.ase.ie.dma02.DMA02App`. E `private final`, nu `static final` ca în `MainActivity` — inconsecvență de stil, nu bug: `Application` are o singură instanță per proces, deci un câmp de instanță e suficient.

**De ce `onCreate` are exact această ordine:**

1. `super.onCreate()` — contractul clasei de bază. La `Application`, metoda din părinte e goală, dar lanțul poate conține altă clasă care face ceva; se păstrează mereu.
2. `registerActivityLifecycleCallbacks(this)` — abonarea. Trebuie făcută **înainte** ca prima activitate să fie creată, altfel primul eveniment se pierde.
3. `DynamicColors.applyToActivitiesIfAvailable(this)` — tema. Trebuie aplicată **înainte** ca prima activitate să-și rezolve tema, altfel primul ecran rămâne cu paleta fixă.
4. `Log.w(...)` — ultima, ca să marcheze „inițializarea globală s-a terminat".

**De ce `Log.w` și nu `Log.d`:** `w` (warning) e vizibil implicit în Logcat fără să schimbi filtrul de nivel; `d` (debug) poate fi ascuns. Pentru demonstrație, `w` e alegerea practică.

**Ce se întâmplă dacă ștergi fiecare linie:**

| Linie ștearsă | Efect |
|---|---|
| `registerActivityLifecycleCallbacks(this)` | nicio eroare, niciun mesaj `onActivity*` în Logcat — aplicația arată identic |
| `DynamicColors.applyToActivitiesIfAvailable(this)` | paleta fixă din `themes.xml`; pe Android 12+ aplicația nu mai urmează wallpaper-ul |
| `Log.w(TAG, "onCreate")` | nimic funcțional; dispare doar primul rând din Logcat |
| `super.onCreate()` | nimic la `Application` (baza e goală), dar încalcă contractul și e periculos dacă lanțul se schimbă |
| `extends Application` | la pornire: `ClassCastException` — manifestul cere o clasă care nu e `Application` |

```java
    @Override
    public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
        Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());   // ex.: "onActivityCreatedMainActivity"
    }                                                                             // fără spațiu între text și numele clasei

    @Override
    public void onActivityDestroyed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityDestroyed" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityPaused(@NonNull Activity activity) {
        Log.w(TAG, "onActivityPaused" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityResumed(@NonNull Activity activity) {
        Log.w(TAG, "onActivityResumed" + activity.getClass().getSimpleName());
    }

    // singura metodă lăsată goală: interfața o cere, dar aici nu avem nimic de salvat și nu logăm
    @Override
    public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {

    }

    @Override
    public void onActivityStarted(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStarted" + activity.getClass().getSimpleName());
    }

    @Override
    public void onActivityStopped(@NonNull Activity activity) {
        Log.w(TAG, "onActivityStopped" + activity.getClass().getSimpleName());
    }
}
```

**De ce toate șapte:** `ActivityLifecycleCallbacks` e o interfață cu șapte metode **abstracte**. Nu poți implementa doar jumătate: dacă ștergi o metodă, proiectul **nu compilează** (`DMA02App is not abstract and does not override abstract method ...`). De aceea `onActivitySaveInstanceState` există chiar dacă nu face nimic.

**Corespondența cu metodele activității:**

| Metoda activității | Callback-ul din `Application` |
|---|---|
| `onCreate` | `onActivityCreated(activity, savedInstanceState)` |
| `onStart` | `onActivityStarted(activity)` |
| `onResume` | `onActivityResumed(activity)` |
| `onPause` | `onActivityPaused(activity)` |
| `onStop` | `onActivityStopped(activity)` |
| `onSaveInstanceState` | `onActivitySaveInstanceState(activity, bundle)` |
| `onDestroy` | `onActivityDestroyed(activity)` |

**Cine se execută primul:** callback-ul e declanșat **din interiorul** metodei de bază. În sursa Android 36, `Activity.onCreate` apelează `dispatchActivityCreated(...)` spre finalul lui, `Activity.onStart` apelează `dispatchActivityStarted()`, `Activity.onResume` apelează `dispatchActivityResumed()` etc. Pentru că `MainActivity` scrie `super.onX()` **primul** și loghează după, în Logcat ordinea este:

```
DMA02App:    onActivityCreatedMainActivity
MainActivity: onCreate
DMA02App:    onActivityStartedMainActivity
MainActivity: onStart
...
```

> Dacă ai loga **înainte** de `super.onStart()`, ordinea s-ar inversa. Ordinea din Logcat nu e „callback-ul e înainte de metodă", ci „logul tău e după `super`".

**De ce `@Nullable Bundle bundle`:** la prima creare, `savedInstanceState` e `null`; la recreare (rotire, revenire după ce procesul a fost omorât), e `Bundle`-ul salvat. Adnotarea documentează asta pentru lint și pentru cititor. `activity` nu e niciodată `null`, de aceea `@NonNull`.

**De ce concatenarea arată urât:** `"onActivityCreated" + activity.getClass().getSimpleName()` produce `onActivityCreatedMainActivity`, fără spațiu. Nu e bug, dar e o capcană de citire: în Logcat pare un singur cuvânt. Dacă vrei lizibilitate, pui `"onActivityCreated "` cu spațiu.

**De ce metodele sunt în ordine alfabetică:** `onActivityCreated`, `onActivityDestroyed`, `onActivityPaused`, `onActivityResumed`, `onActivitySaveInstanceState`, `onActivityStarted`, `onActivityStopped`. IntelliJ generează implementările în ordine alfabetică, nu în ordinea ciclului de viață. Ordinea din fișier **nu** e ordinea de execuție — confuzie clasică la citirea pe fugă.

**Ce se întâmplă dacă ștergi `implements Application.ActivityLifecycleCallbacks`:** `registerActivityLifecycleCallbacks(this)` nu mai compilează, pentru că `this` nu mai e de tipul cerut. Dacă ștergi și apelul, aplicația compilează și rulează, dar fără niciun log de ciclu de viață.

---

## 25.2 `MainActivity.java` — ciclul de viață

### Fișierul complet, adnotat

```java
package ro.ase.ie.dma02;

import android.content.Intent;              // folosit doar în pressMe
import android.os.Bundle;                   // parametrul din onCreate
import android.util.Log;                    // scrierea în Logcat
import android.view.View;                   // parametrul din pressMe — cerut de android:onClick

import androidx.appcompat.app.AppCompatActivity;   // varianta AppCompat a lui Activity

public class MainActivity extends AppCompatActivity {

    private static final String TAG = MainActivity.class.getSimpleName();   // "MainActivity"

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);              // obligatoriu primul; altfel SuperNotCalledException
        setContentView(R.layout.activity_main);          // umple fereastra cu arborele din XML
        Log.w(TAG, "onCreate");                          // primul log al activității
    }
```

**De ce `extends AppCompatActivity` și nu `Activity`:** `AppCompatActivity` aduce înapoi (backport) comportamentul AppCompat: inflatarea view-urilor compatibile, suport pentru teme Material pe versiuni vechi, `AppCompatDelegate` pentru dark mode. În plus, tema `Theme.DMA02` coboară din `Theme.Material3`, care coboară din `Theme.AppCompat` — exact ce cere `AppCompatActivity`.

> Inversul e capcana: dacă păstrezi `AppCompatActivity` dar schimbi tema într-una de platformă (fără AppCompat), aplicația crapă la pornire cu `IllegalStateException: You need to use a Theme.AppCompat theme (or descendant) with this activity.`

**De ce `TAG` e `static final`:** `MainActivity` poate avea mai multe instanțe (la rotire, la revenire), dar tag-ul e același pentru toate. `static` = aparține clasei, nu instanței.

**De ce `onCreate` are exact această ordine:**

1. `super.onCreate(savedInstanceState)` — fără el, framework-ul aruncă `SuperNotCalledException: Activity ... did not call through to super.onCreate()`. Nu e o convenție, e o verificare reală făcută de `ActivityThread` după ce metoda se întoarce.
2. `setContentView(R.layout.activity_main)` — creează arborele de view-uri din XML și îl atașează ferestrei. Fără el, ecranul rămâne gol (alb), iar orice `findViewById` ar întoarce `null`.
3. `Log.w(TAG, "onCreate")` — ultima, ca să marcheze „activitatea e construită".

**De ce `R.layout.activity_main`:** `R` e clasa generată la build din folderul `res/`. Numele fișierului `activity_main.xml` devine constanta `R.layout.activity_main`. Dacă redenumești XML-ul, linia nu mai compilează — legătura dintre cele două fișiere e **prin nume**.

**De ce `savedInstanceState` e ignorat:** DMA02 nu are stare de salvat (niciun câmp, niciun formular). Parametrul e `null` la prima creare și non-`null` la recreare. La rotire, activitatea e distrusă și recreată, iar `onCreate` rulează din nou — în Logcat vezi din nou `MainActivity: onCreate`.

**Ce lipsește față de `G1097`:** blocul `EdgeToEdge.enable(this)` și listener-ul de insets. DMA02 nu le are. Consecința e vizibilă pe Android 15+: aplicațiile cu `targetSdk ≥ 35` rulează implicit edge-to-edge, iar fără listener conținutul se desenează **sub** bara de stare — toolbar-ul intră sub ceas. În `G1097`, `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` rezolvă exact asta.

```java
    @Override
    protected void onDestroy() {
        super.onDestroy();                  // curățenia framework-ului
        Log.w(TAG, "onDestroy");
    }

    @Override
    protected void onStart() {
        super.onStart();
        Log.w(TAG, "onStart");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.w(TAG, "onStop");
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.w(TAG, "onPause");
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.w(TAG, "onResume");
    }
```

**De ce sunt toate șase:** fiecare suprascriere face exact un lucru — scrie un rând în Logcat. Sunt **observatori**, nu cerințe: dacă ștergi o metodă întreagă, aplicația funcționează în continuare, pentru că rulează implementarea din `AppCompatActivity`. Pierzi doar rândul din Logcat.

**De ce `super` e primul peste tot:** pentru un log, ordinea nu contează. Dar convenția pentru `onPause`, `onStop` și `onDestroy` e să faci curățenia **înainte** de `super` (resursele tale încă există), iar pentru `onCreate`, `onStart`, `onResume` — după `super`. Aici toate sunt după, pentru simplitate. Ce contează: `super` **trebuie** apelat. Fără el, `ActivityThread` aruncă `SuperNotCalledException` după fiecare metodă.

**Ordinea din fișier nu e ordinea de execuție:** `onCreate`, `onDestroy`, `onStart`, `onStop`, `onPause`, `onResume` — tot ordine alfabetică, generată de IntelliJ. Ordinea reală la rulare:

```
pornire:   onCreate → onStart → onResume
Home:      onPause → onStop
revenire:  onRestart → onStart → onResume
Back:      onPause → onStop → onDestroy
rotire:    onPause → onStop → onDestroy → onCreate → onStart → onResume
```

**De ce `onDestroy` nu e garantat:** dacă sistemul omoară procesul (memorie puțină), `onDestroy` nu se apelează. De aceea nu pui salvarea de date acolo — pentru salvare există `onPause`/`onStop` și `onSaveInstanceState`.

**De ce mesajul e doar `"onCreate"`:** în Logcat, coloana Tag spune deja `MainActivity`, iar coloana Message spune `onCreate`. Împreună: `MainActivity: onCreate`. Mesajul nu repetă tag-ul.

```java
    public void pressMe(View view) {          // semnătura e dictată de android:onClick="pressMe" din XML
        // Varianta 1, comentată: deschide un URL în browserul implicit.
  /*      Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse("https://developer.android.com"));
        startActivity(web);*/
        // ↑ `Uri` NU e importat în fișier: dacă decomentezi blocul, nu compilează.

        // Varianta 2, comentată: deschide tastatura telefonică, fără să sune.
        /*Intent call = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0212345678"));
        startActivity(call);*/

        // Varianta 3, activă: share sheet.
        Intent share = new Intent(Intent.ACTION_SEND);                  // Intent implicit: acțiune, fără clasă țintă
        share.setType("text/plain");                                     // MIME — obligatoriu pentru ACTION_SEND
        share.putExtra(Intent.EXTRA_TEXT, "Hello!");                     // textul care se trimite
        startActivity(Intent.createChooser(share, "Share via DMA"));     // chooser forțat, cu titlu

    }
}                                            // închide clasa MainActivity
```

**De ce semnătura e exact `public void pressMe(View view)`:** `android:onClick="pressMe"` din layout nu e o legătură de compilare, ci o căutare **prin reflecție** la runtime. Framework-ul caută în Context-ul view-ului (adică în activitate) o metodă `public`, cu return `void`, cu exact un parametru `View`. Dacă numele diferă, click-ul crapă cu:

```
IllegalStateException: Could not find method pressMe(View) in a parent or ancestor Context
for android:onClick attribute defined on view class android.widget.Button ...
```

**De ce parametrul `view` nu e folosit:** metoda e chemată pentru un singur buton, deci nu ai nevoie să distingi sursa. Parametrul e obligatoriu prin contract, chiar dacă îl ignori.

**De ce primele două variante sunt comentate:** sunt demonstrații păstrate în cod ca material didactic. `ACTION_VIEW` + `https://` deschide browserul; `ACTION_DIAL` + `tel:` deschide tastatura telefonică **fără** să sune — de aceea nu cere permisiunea `CALL_PHONE`. Varianta care sună efectiv, `ACTION_CALL`, ar cere-o.

> Capcana reală: `Uri` **nu** e importat (nu apare în lista de importuri). Blocurile sunt comentate exact ca să compileze. Dacă decomentezi primul bloc, primești `cannot find symbol: class Uri` — trebuie adăugat `import android.net.Uri;`.

**De ce `ACTION_SEND` + `setType("text/plain")`:** un `Intent` implicit declară doar **ce operație** vrei, nu și clasa care o execută. Sistemul caută aplicațiile care au un `intent-filter` potrivit. `setType` e filtrul principal: fără el, sistemul nu știe ce aplicații pot primi `Intent`-ul.

| Linie ștearsă | Efect |
|---|---|
| `share.setType("text/plain")` | nicio aplicație nu se potrivește; chooser-ul apare gol („No apps can perform this action"), iar `startActivity` direct ar da `ActivityNotFoundException` |
| `share.putExtra(Intent.EXTRA_TEXT, "Hello!")` | share sheet-ul se deschide, dar textul trimis e gol |
| `Intent.createChooser(...)` | Android poate deschide direct aplicația implicită de share, fără dialog |
| `startActivity(...)` | `Intent`-ul e construit și aruncat; nu se întâmplă nimic |

**De ce `createChooser`:** `ACTION_SEND` singur respectă aplicația implicită de share. `createChooser(intent, title)` forțează **mereu** dialogul de alegere, cu titlul dat („Share via DMA"). E util când vrei ca utilizatorul să decidă conștient.

**De ce `Intent.EXTRA_TEXT` și nu `"android.intent.extra.TEXT"`:** constanta are exact aceeași valoare, dar numele e verificat de compilator. Un string scris de mână greșit nu dă eroare — doar textul nu ajunge nicăieri.

**Bucla care se închide:** manifestul declară un `intent-filter` pentru `ACTION_SEND` + `text/plain` (secțiunea 25.3). Deci **DMA02 apare în propriul share sheet**. Dacă o alegi, pornește o **a doua** instanță de `MainActivity` (launch mode standard), prima trece prin `onPause` → `onStop`. Și, pentru că `MainActivity` nu citește niciodată `getIntent().getStringExtra(Intent.EXTRA_TEXT)`, textul primit e ignorat: vezi doar un ecran nou, identic.

**De ce `startActivity` și nu `startActivityForResult`:** nu ai nevoie de niciun rezultat înapoi. `startActivityForResult` (sau `registerForActivityResult`) se folosește când aștepți date — ca în `G1097`, la formular.

---

## 25.3 `AndroidManifest.xml`

### Fișierul complet, adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ↑ declarația XML: prima linie obligatorie; fără ea, build-ul respinge fișierul. -->

<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
<!-- ↑ xmlns:android = prefixul tuturor atributelor android:. xmlns:tools = prefixul tools:;
     la d719ffc e declarat, dar niciun atribut tools: nu apare în fișier — rămășiță din șablon. -->

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
        <!-- ↑ fiecare atribut, explicat în tabelul de mai jos. -->

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <!-- ↑ activitatea principală: singura din aplicație. -->

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <!-- ↑ filtrul 1: MAIN + LAUNCHER = aplicația apare în launcher. -->

                <intent-filter>
                    <action android:name="android.intent.action.SEND" />
                    <category android:name="android.intent.category.DEFAULT" />
                    <data android:mimeType="text/plain" />
                </intent-filter>
            <!-- ↑ filtrul 2: primește text din share sheet. Indentarea lui e inconsistentă în repo. -->


        </activity>
    </application>

</manifest>
```

**De ce `android:name=".DMA02App"` e cea mai importantă linie din fișier:** e singura legătură dintre codul din 25.1 și runtime. Punctul de la început înseamnă „relativ la `namespace`" — adică `ro.ase.ie.dma02.DMA02App`. Fără linie, Android folosește `android.app.Application` și clasa ta nu e instanțiată. Cu numele scris greșit (`DMA02App` fără punct, sau alt pachet), aplicația crapă la pornire cu `ClassNotFoundException`.

**Atributele din `<application>`:**

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

**De ce `android:theme="@style/Theme.DMA02"`:** `Theme.DMA02` e definit în `res/values/themes.xml` ca `parent="Base.Theme.DMA02"`, iar `Base.Theme.DMA02` are **doi** părinți, în funcție de modul sistemului:

| Fișier | Părinte | Efect |
|---|---|---|
| `values/themes.xml` (mod light) | `Theme.Material3.Dark` | aplicația e **întunecată** și are ActionBar |
| `values-night/themes.xml` (mod night) | `Theme.Material3.DayNight.NoActionBar` | aplicația e întunecată și **nu** are ActionBar |

Rezultatul e o inconsecvență reală a repo-ului: aplicația e mereu dark, iar bara de titlu a ferestrei apare doar în modul light — acolo unde, peste ea, mai există și `MaterialToolbar`-ul din layout. Nu crapă nimic, dar explică de ce ecranul arată diferit cu tema sistemului pe light față de night.

**De ce `android:exported="true"`:** din Android 12 (API 31), orice componentă cu `intent-filter` trebuie să declare explicit `exported`. Fără atribut, build-ul eșuează: „Apps targeting Android 12 and higher are required to specify an explicit value for `android:exported`". Valoarea `true` e obligatorie aici: launcher-ul e **altă** aplicație, deci trebuie să poată porni `MainActivity`.

**De ce `android:windowSoftInputMode="adjustResize"`:** când apare tastatura, fereastra se redimensionează ca să nu acopere câmpul activ. DMA02 nu are niciun câmp de text, deci atributul e inert — rămășiță din șablon. Pe Android 15+, cu edge-to-edge, `adjustResize` e oricum ignorat în favoarea insets-urilor.

**De ce filtrul `MAIN` + `LAUNCHER`:** `MAIN` spune „acesta e punctul de intrare"; `LAUNCHER` spune „arată-mă în launcher". Fără el, aplicația se poate porni doar din altă aplicație sau din `adb`, nu din iconiță.

**De ce filtrul `SEND` + `DEFAULT` + `text/plain`:** filtrează ce `Intent`-uri implicite acceptă activitatea. `DEFAULT` e obligatoriu pentru `startActivity`: sistemul rezolvă cu `MATCH_DEFAULT_ONLY`, deci un filtru fără `DEFAULT` nu se potrivește niciodată. `text/plain` limitează la text — fără el, aplicația ar apărea la share pentru orice tip de conținut.

> Filtrul e **doar receptor**. Codul nu citește textul primit, deci aplicația apare în share sheet și îl ignoră. E jumătatea a doua a demonstrației din 25.2.

---

## 25.4 `activity_main.xml`

### Fișierul complet, adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">
    <!-- ↑ rădăcina: ConstraintLayout, id `main` (nefolosit în DMA02, folosit în G1097 pentru insets). -->

    <com.google.android.material.appbar.MaterialToolbar
        android:id="@+id/toolbar"
        android:layout_width="match_parent"
        android:layout_height="?attr/actionBarSize"
        app:title="@string/app_name"/>
    <!-- ↑ bara de titlu: fără constraints, deci plasată la (0,0) de ConstraintLayout. -->

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
    <!-- ↑ textul central: patru constraints = centrat pe orizontală și pe verticală. -->

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
    <!-- ↑ butonul: `android:onClick="pressMe"` e singura legătură XML → cod din tot proiectul. -->

</androidx.constraintlayout.widget.ConstraintLayout>
```

**De ce `ConstraintLayout`:** fiecare copil e poziționat prin **relații** față de părinte sau față de frați, nu prin ordine. E layout-ul generat de șablonul „Empty Views Activity" și e potrivit pentru ecrane simple: un text centrat, un buton deasupra lui.

**De ce `android:id="@+id/main"`:** în DMA02 nu e folosit nicăieri — nicio linie de cod nu face `findViewById(R.id.main)`. În `G1097` devine esențial: `ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)` are nevoie de el. Dacă îl ștergi aici, DMA02 merge în continuare; dacă îl ștergi în `G1097`, aplicația crapă cu `NullPointerException` la pornire.

**De ce `tools:context=".MainActivity"`:** îi spune IDE-ului ce activitate să folosească pentru previzualizare (temă, rezolvarea `android:onClick`). La build, atributul e eliminat — nu ajunge în APK.

**`MaterialToolbar`:**

```xml
android:layout_height="?attr/actionBarSize"
app:title="@string/app_name"
```

`?attr/actionBarSize` ia înălțimea standard a barei (56dp) din temă. `app:title` e atributul Material, nu `android:title`. Toolbar-ul are `match_parent` pe lățime și **niciun constraint** — în `ConstraintLayout`, un view fără constraints e plasat la colțul (0,0) cu dimensiunea măsurată. Funcționează, dar „din întâmplare": dacă adaugi alt view deasupra, toolbar-ul nu se mișcă.

> Niciun cod nu apelează `setSupportActionBar(toolbar)`. Deci toolbar-ul e doar un view stilizat cu un titlu, nu ActionBar-ul activității: nu primește meniu de opțiuni, nu primește buton de navigare înapoi.

**`TextView`:**

```xml
android:text="Hello World!"
android:textAppearance="?attr/textAppearanceBodyLarge"
```

Patru constraints (sus, jos, start, end) față de părinte = centrat pe ambele axe. `?attr/textAppearanceBodyLarge` ia stilul tipografic „body large" din tema Material 3 (16sp), în loc să hardcodezi `textSize`.

> `"Hello World!"` e text hardcodat: lint-ul dă avertisment `HardcodedText`, iar textul nu poate fi tradus. Corect ar fi `@string/hello_world` în `strings.xml`.

**`Button`:**

```xml
android:onClick="pressMe"
app:layout_constraintBottom_toTopOf="@+id/textView"
```

Butonul e legat de `TextView` prin `bottom_toTopOf`: se așază deasupra textului, centrat orizontal. Împreună cu `top_toTopOf="parent"`, ocupă jumătatea de sus a ecranului. `@+id/textView` funcționează și fără `+` (id-ul e deja declarat mai sus), dar e inofensiv.

> `android:onClick` e **singura** legătură dintre XML și cod din tot proiectul. Numele din XML trebuie să fie identic cu metoda din `MainActivity` — altfel `IllegalStateException` la click, nu la compilare.

**Ce se întâmplă dacă ștergi fiecare bloc:**

| Bloc șters | Efect |
|---|---|
| `Button`-ul | `pressMe` nu mai poate fi chemat; aplicația afișează doar textul |
| `android:onClick="pressMe"` | click-ul nu face nimic; nicio eroare, nicio urmă în Logcat |
| `TextView`-ul | referința `bottom_toTopOf` rămâne fără țintă: constraint-ul e ignorat, iar butonul se lipește de marginea de sus |
| `MaterialToolbar` | ecranul rămâne fără titlu; restul merge |
| `android:id="@+id/main"` | nimic în DMA02; `G1097` ar crăpa la insets |
| `xmlns:app` | toate atributele `app:` devin invalide → build eșuează |

### Capcane reale în DMA02

| Loc | Capcană | Efect |
|---|---|---|
| `MainActivity` | `Uri` nu e importat | decomentezi blocul `ACTION_VIEW` → nu compilează |
| `MainActivity` | metodele sunt în ordine alfabetică | ordinea din fișier ≠ ordinea de execuție |
| `MainActivity` | fără `EdgeToEdge` + insets | pe Android 15+ conținutul intră sub bara de stare |
| `AndroidManifest.xml` | filtrul `SEND` nu e citit în cod | aplicația apare în share sheet, dar ignoră textul |
| `AndroidManifest.xml` | `adjustResize` fără câmpuri de text | atribut inert |
| `themes.xml` | `Theme.Material3.Dark` în `values`, `DayNight.NoActionBar` în `values-night` | aplicația e mereu dark; ActionBar doar în modul light |
| `activity_main.xml` | toolbar fără constraints | plasat la (0,0) „din întâmplare" |
| `activity_main.xml` | `"Hello World!"` și `"Button"` hardcodate | lint `HardcodedText`, fără traducere |

---

## 25.5 Fluxul complet

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

APĂSARE BACK (din MainActivity)
  onPause → onStop → onDestroy
    └── DMA02App.onActivityDestroyed

ROTIRE
  onPause → onStop → onDestroy
  → onActivityCreated → onCreate → onStart → onResume    (instanță nouă!)
```

**Ce se citește din diagramă:**

1. `Application.onCreate` rulează **înaintea** oricărei activități — de aceea abonarea și tema stau acolo.
2. Fiecare metodă a activității are un callback pereche, declanșat din interiorul lui `super`.
3. `pressMe` nu schimbă nicio stare: doar construiește un `Intent` și predă controlul sistemului.
4. La rotire, lanțul complet de distrugere și creare rulează din nou — de aceea `onCreate` apare de două ori în Logcat.

---

## 25.6 Ce să reții

| Fișier | Esența |
|---|---|
| `DMA02App.java` | `Application` + `ActivityLifecycleCallbacks`; `onCreate` rulează înaintea oricărei activități; `DynamicColors` se aplică global, o singură dată |
| `MainActivity.java` | șase metode de ciclu de viață, toate cu `super` primul; `pressMe` = `Intent` implicit cu `ACTION_SEND` |
| `AndroidManifest.xml` | `android:name=".DMA02App"` leagă clasa; `exported="true"` obligatoriu; două filtre: `LAUNCHER` și `SEND` |
| `activity_main.xml` | `ConstraintLayout`; `android:onClick="pressMe"` e singura legătură XML → cod |

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
