# Capitolul 37 — Conceptele, explicate

**Obiectiv:** să poți răspunde la „de ce?" pentru fiecare mecanism din aplicația Android. Nu „cum se scrie", ci **de ce există**, **ce ar face codul fără el** și **ce se rupe** când îl înțelegi greșit.

**Ce nu este capitolul ăsta:**

- Nu este cheatsheet. Cheatsheet-ul e capitolul 21: acolo ai tabelul cu metode și rețeta pe cinci pași. Aici ai mecanismul din spate.
- Nu este rețetă. Rețetele sunt capitolele 33–35: acolo ai „cum faci X în 10 minute". Aici ai „de ce X funcționează așa".
- Nu este cod adnotat. Codul adnotat e capitolul 22: acolo fiecare linie are explicația lipită de ea. Aici fiecare **concept** are explicația lipită de el.

**Cum se citește:** 24 de concepte, fiecare cu exact șase rubrici, mereu în aceeași ordine:

| Rubrica | Întrebarea la care răspunde |
|---|---|
| **Ce este** | definiția, în 2–4 propoziții, fără jargon nedefinit |
| **De ce există** | ce problemă rezolvă, ce ai face manual fără el |
| **Cum funcționează** | mecanismul, pas cu pas, cu diagramă unde ajută |
| **Ce se rupe fără el** | eroarea concretă, comportamentul greșit concret |
| **Unde îl vezi în G1097** | fișier + metodă + cod real |
| **Confuzia tipică** | ce crede lumea greșit, și de ce e greșit |

**Regula de aur a capitolului:** fiecare afirmație este verificabilă în codul real. Când un concept nu apare în G1097, o spun explicit și arăt unde apare în proiectele de curs — `DMA02`, `DMA05`, `DMA06`.

**Sursa de adevăr:** `D:\tmp\claude\dma-annot\src-G1097\` — cele opt fișiere (`MainActivity.java`, `ItemActivity.java`, `Movie.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`, `strings.xml`), plus `build.gradle.kts` din `cod-final`.

**De ce un capitol întreg de „de ce":** la test, jumătate din puncte se dau pe cod care compilează, iar cealaltă jumătate pe explicații. „Un adapter leagă datele de listă" nu e o explicație — e o tautologie. Explicația e: *cine* apelează metodele adapterului, *când*, și *ce ar face codul dacă adapterul nu ar exista*. Capitolul ăsta e construit exact pe diferența asta.

**Harta capitolului:**

| Grup | Concepte | Ce acoperă |
|---|---|---|
| Fundația | 37.1–37.4 | aplicația, `Context`, resursele, manifestul |
| Desenarea | 37.5–37.7 | arborele de view-uri, cele trei passe, layout-urile |
| Legătura cod–XML | 37.8–37.9 | `findViewById`, ViewBinding |
| Timpul | 37.10–37.13 | `Activity`, ciclul de viață, stare, `Application` |
| Evenimentele | 37.14–37.15 | listeneri, lambda |
| Datele | 37.16–37.20 | model, adapter, ViewHolder, LayoutManager, ListView vs RecyclerView |
| Granițele | 37.21–37.24 | `Intent`, `Bundle`, `ActivityResultLauncher`, Gradle |

---

## Conceptul 37.1 — Ce este o aplicație Android

**Ce este**

O aplicație Android este un **APK** — o arhivă zip cu cod compilat (`classes.dex`), resurse compilate (`resources.arsc` plus folderele `res/`), un manifest în formă binară și o semnătură. La instalare, sistemul îi atribuie un **identificator de utilizator Linux** propriu și un director de date propriu, iar de atunci încolo rulează într-un **proces** izolat, cu permisiuni proprii. Aplicația nu are un `main()` scris de tine: sistemul o pornește și îi cheamă componentele.

**De ce există**

Pentru că un telefon rulează simultan zeci de aplicații scrise de oameni care nu au încredere unul în celălalt, pe un dispozitiv cu memorie limitată și cu un utilizator care poate oricând să apese Home. Fără acest înveliș ai fi responsabil manual de: pornirea procesului, izolarea față de alte aplicații, eliberarea memoriei când sistemul are nevoie de ea, ciclul de viață al ecranelor, încărcarea resurselor potrivite pentru limbă și densitate, și actualizarea codului fără să pierzi datele utilizatorului. Android îți dă toate astea la pachet, iar în schimb îți cere un singur lucru: să declari în manifest ce componente ai, ca sistemul să știe ce poate porni.

**Cum funcționează**

Lanțul complet, de la build până la primul pixel:

```
1. BUILD (pe calculatorul tău)
   surse .java ──javac──> .class ──d8──> classes.dex
   res/ + AndroidManifest.xml ──aapt2──> resurse binare + resources.arsc
                                    |
                                    v
                              app-debug.apk  (zip semnat)

2. INSTALARE (pe telefon)
   PackageManagerService citește manifestul
     -> înregistrează componentele în indexul sistemului
     -> atribuie un UID Linux, ex. u0_a231
     -> creează /data/data/ro.ase.ie.g1097/

3. LANSARE (apeși iconița)
   Launcher trimite Intent(ACTION_MAIN, CATEGORY_LAUNCHER)
     -> system_server rezolvă Intent-ul în MainActivity
     -> nu există proces? Zygote fork-uiește unul nou
     -> ActivityThread.main() pornește bucla de mesaje (Looper)
     -> Application.onCreate()
     -> MainActivity.onCreate() -> onStart() -> onResume()
     -> prima desenare
```

Trei lucruri pe care diagrama le arată și care se uită ușor:

1. **Procesul nu există până nu e nevoie de el.** Iconița din launcher nu ține aplicația în memorie. După ce apeși Home și sistemul are nevoie de RAM, procesul poate fi omorât complet, iar la revenire pornește din nou, cu `onCreate` din nou.
2. **`Application.onCreate()` rulează înaintea oricărei activități.** De aceea inițializările globale stau acolo (vezi 37.13).
3. **UID-ul este granița de securitate.** Două aplicații cu UID-uri diferite nu pot citi fișierele celeilalte. Asta e sandbox-ul, și e motivul pentru care `Context` are sens (vezi 37.2): el știe al cui UID ești.

**Ce se rupe fără el**

- **Fără `applicationId` distinct** (sau cu el schimbat între versiuni): Android tratează build-ul ca pe o aplicație nouă. Se instalează în paralel, cu alt director de date, iar utilizatorul vede două iconițe. Datele vechi rămân orfane.
- **Fără filtrul `MAIN` + `LAUNCHER`**: aplicația se instalează, dar nu are iconiță în launcher. Nu există nicio cale prin care utilizatorul să o pornească — doar `adb shell am start`.
- **Cu `minSdk` mai mare decât versiunea telefonului**: instalarea eșuează cu `INSTALL_FAILED_OLDER_SDK`, înainte să ruleze o linie de cod.
- **Cu un crash în `Application.onCreate()`**: procesul moare înainte să se creeze prima activitate. Vezi crash-ul în logcat fără să fi apărut vreun ecran — un simptom care derutează, pentru că „aplicația mea nici nu s-a deschis".

**Unde îl vezi în G1097**

`build.gradle.kts` fixează identitatea aplicației:

```kotlin
android {
    namespace = "ro.ase.ie.g1097"
    defaultConfig {
        applicationId = "ro.ase.ie.g1097"
        minSdk = 33
        targetSdk = 37
    }
}
```

`AndroidManifest.xml` declară învelișul și cele două componente:

```xml
<application
    android:label="@string/app_name"
    android:theme="@style/Theme.G1097">
    <activity android:name=".activities.MainActivity" android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
    <activity android:name=".activities.ItemActivity" android:exported="false" />
</application>
```

`MainActivity` este singura activitate cu filtrul `LAUNCHER` — deci singura poartă de intrare. `ItemActivity` are `exported="false"`, adică nicio altă aplicație nu o poate porni; doar G1097 o poate deschide, prin `Intent`-ul din `initListeners()`.

**Confuzia tipică**

„Aplicația este `MainActivity`." Nu. Aplicația este pachetul instalat, cu UID-ul și procesul lui; `MainActivity` este doar primul ecran, un obiect care se creează și se distruge de mai multe ori pe durata unei singure rulări. Consecința practică: dacă vrei o valoare care supraviețuiește între ecrane, nu o pui într-o activitate — o pui într-un model, într-un `Application` sau pe disc.

A doua confuzie: „dacă aplicația e în recents, înseamnă că rulează". Nu. Recents ține o **sarcină** (task), adică o listă de activități și starea lor salvată — nu un proces. Procesul poate fi omorât oricând, iar la revenire Android recreează activitățile din starea salvată. Exact de aici vine nevoia de `onSaveInstanceState` (vezi 37.12).

A treia: „un proces = o aplicație". Nu. O aplicație poate rula în mai multe procese (dacă declari `android:process`), iar un proces poate găzdui activități din mai multe aplicații în anumite cazuri. Pentru G1097, cele două activități rulează în același proces — de aceea serializarea din `Intent` pare „instant" și de aceea `serialVersionUID` nu e o problemă reală aici (vezi 37.16).

---

## Conceptul 37.2 — Contextul

**Ce este**

`Context` este o clasă abstractă din Android care reprezintă **legătura dintre codul tău și mediul aplicației**. Prin ea ajungi la resurse (`getResources()`), la pachetul aplicației (`getPackageManager()`), la serviciile de sistem (`getSystemService()`), la folderele de fișiere (`getFilesDir()`), la preferințe (`getSharedPreferences()`) și la pornirea altor ecrane (`startActivity()`). `Activity`, `Service` și `Application` **sunt** `Context`, pentru că moștenesc din el.

**De ce există**

Pentru că o clasă care vrea să afișeze un text tradus are nevoie de tabelul de traduceri, iar acel tabel aparține aplicației, nu clasei. Fără `Context` ai avea două variante, ambele rele: fie un glob static (`App.resources`) care se sparge când aplicația are mai multe configurații, fie transmiterea explicită a zeci de obiecte prin constructori. `Context` rezolvă problema printr-un singur parametru care încapsulează tot mediul.

Are și un rol de securitate: obiectul `Context` știe **al cui** UID ești. Când apelezi `getSharedPreferences("x", MODE_PRIVATE)`, Android nu verifică permisiuni — fișierul e deja în directorul tău privat, pentru că UID-ul din `Context` a decis calea.

**Cum funcționează**

Ierarhia reală, simplificată la ce contează:

```
                Context  (abstract: getResources, startActivity, ...)
                   ^
                   |
            ContextWrapper  (delegate: toate metodele merg la mBase)
             ^          ^
             |          |
  ContextThemeWrapper   Application
        ^                  (are Resources, dar FĂRĂ temă de UI)
        |
   Activity  (are și fereastră, și temă, și WindowManager)
```

`ContextWrapper` nu implementează nimic: ține un câmp `mBase` de tip `Context` și trimite fiecare apel mai departe. `ContextImpl` este implementarea reală, creată de sistem. Când scrii `this` într-o activitate, `this` este un `ContextThemeWrapper` care deleagă la un `ContextImpl` legat de aplicația ta.

Diferența care contează la examen:

| | `Activity` (Context de activitate) | `getApplicationContext()` |
|---|---|---|
| are temă (`?attr/colorPrimary`) | da | nu |
| poate deschide o fereastră (dialog, `startActivity`) | da | doar cu `FLAG_ACTIVITY_NEW_TASK` |
| trăiește cât activitatea | da | cât procesul |
| potrivit pentru un singleton | **nu** (scurgere de memorie) | da |

**Ce se rupe fără el**

- **`Toast.makeText(this, ...)` într-o clasă anonimă**: `this` este obiectul listener, nu activitatea. Eroare de compilare, `incompatible types: <anonymous OnClickListener> cannot be converted to Context`. Fix: `MainActivity.this`.
- **Un `Context` de activitate ținut într-un câmp `static`**: activitatea nu mai poate fi colectată de garbage collector după `onDestroy`, pentru că o referință statică o ține în viață. Simptomul nu e un crash, ci memorie care crește la fiecare rotire.
- **`getApplicationContext()` folosit pentru un dialog**: `WindowManager$BadTokenException: Unable to add window -- token null is not for an application`. Application-ul nu are fereastră.
- **Resurse citite fără `Context`**: `getString(R.string.app_name)` nu există ca metodă statică. Fără un `Context` nu ai de unde lua tabelul de resurse.

**Unde îl vezi în G1097**

Trei locuri, toate instructive:

```java
// MainActivity.onCreate — `this` este MainActivity, deci un Context.
// ArrayAdapter are nevoie de el ca să încarce android.R.layout.simple_list_item_1.
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

```java
// MainActivity.initListeners — aici `this` NU e un Context.
// Suntem într-o clasă anonimă, deci `this` e OnClickListener.
// De aceea se scrie MainActivity.this, nu `this`.
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        launcher.launch(intent);
    }
});
```

```java
// ItemActivity.showReleaseDatePicker — `this` este ItemActivity,
// iar DatePickerDialog are nevoie de un Context cu temă ca să-și construiască fereastra.
new DatePickerDialog(
        this,
        new DatePickerDialog.OnDateSetListener() { ... },
        releaseCal.get(Calendar.YEAR),
        ...
).show();
```

În `DMA06`, `NumberListAdapter` primește `Context` prin constructor și îl folosește doar pentru `LayoutInflater.from(context)` — adapterul nu are nevoie de mai mult, și e un exemplu bun de dependență minimă:

```java
public NumberListAdapter(Context context, List<Integer> numbers) {
    this.layoutInflater = LayoutInflater.from(context);
    this.numbers = numbers;
}
```

**Confuzia tipică**

„`Context` este aplicația." Nu chiar: `Context` este **interfața către** aplicație. Sunt mai multe obiecte `Context` în același proces — unul per activitate, unul per serviciu, unul pentru `Application` — și toate deleagă la același `ContextImpl`. De aceea `this` și `getApplicationContext()` nu sunt interschimbabile.

A doua confuzie: „`getApplicationContext()` e mereu varianta sigură". E varianta sigură pentru **durată de viață**, nu pentru **funcționalitate**. Îți lipsește tema, deci orice widget care citește `?attr/colorPrimary` va arunca `InflateException` sau va lua valorile implicite. Regula practică: în UI folosești `this` (activitatea); într-un singleton sau într-un obiect care trăiește mai mult decât ecranul, folosești `getApplicationContext()`.

A treia: „`Context` se pasează peste tot, ca un parametru în plus". Nu. Un adapter are nevoie de el doar ca să obțină un `LayoutInflater` sau un `Resources`; dacă îl păstrezi doar ca să-l ai, ai cuplat clasa de UI-ul aplicației. `NumberListAdapter` de mai sus e modelul corect: ia `Context`, extrage imediat ce-i trebuie, nu îl ține.

---

## Conceptul 37.3 — Resursele și clasa R

**Ce este**

Resursele sunt tot ce nu este cod: layout-uri XML, texte, culori, dimensiuni, imagini, șiruri de caractere, style-uri. Stau în subfoldere ale lui `res/` (`layout/`, `values/`, `drawable/`, `mipmap/`, `xml/`). La build, instrumentul **aapt2** le compilează în formă binară și generează o clasă Java numită **`R`**, în pachetul declarat de `namespace`, care conține câte o constantă `int` pentru fiecare resursă. `R.layout.activity_main`, `R.id.etTitle`, `R.array.movie_genre` sunt numere, nu obiecte.

**De ce există**

Pentru că același cod trebuie să arate diferit pe ecrane diferite, în limbi diferite, în modul întunecat. Dacă ai scrie `"Movie details"` direct în cod, ai avea o singură variantă; dacă ai scrie calea fișierului, ai avea un string fragil care se sparge la fiecare redenumire. `R` rezolvă ambele: îți dă un **nume stabil la compilare** (`R.string.movie_details`) pentru o resursă care se **rezolvă la runtime** în varianta potrivită configurației curente. Tu scrii numele; sistemul alege fișierul.

**Cum funcționează**

```
res/
├── layout/activity_main.xml ──┐
├── layout/activity_item.xml ──┤
├── values/strings.xml ────────┤   aapt2
├── values/themes.xml ─────────┼──────────> R.java  (generat, NU se editează)
├── drawable/outline_add_24.xml┤            public static final class id {
└── mipmap/ic_launcher.xml ────┘                public static final int etTitle = 0x7f0800a1;
                                                public static final int listView = 0x7f0800f3;
                                            }
                                            public static final class layout {
                                                public static final int activity_main = 0x7f0b001c;
                                            }
                                                     +
                                            resources.arsc  (tabelul nume -> valoare, per configurație)
```

La runtime, `setContentView(R.layout.activity_main)` primește un `int`, îl caută în `resources.arsc`, găsește fișierul XML binar și îl pasează la `LayoutInflater`. `findViewById(R.id.etTitle)` primește tot un `int` și îl compară cu ID-urile atribuite fiecărui view **în timpul inflatului**. Deci: `R.id.etTitle` nu e „numele" view-ului, e un număr care trebuie să fie identic în două locuri — în XML și în cod.

Sintaxa din XML are două forme care se confundă des:

| Formă | Sens |
|---|---|
| `@+id/etTitle` | **creează** ID-ul dacă nu există deja (semnul `+`) |
| `@id/etTitle` | **referă** un ID deja creat |
| `@string/app_name` | referă o resursă din `values/strings.xml` |
| `@array/movie_genre` | referă un `<string-array>` |
| `@drawable/outline_add_24` | referă o imagine vectorială sau bitmap |
| `@style/Theme.G1097` | referă un style |
| `?attr/colorPrimary` | referă un **atribut al temei** curente, nu o resursă fixă |
| `@android:drawable/ic_menu_save` | referă o resursă a **sistemului**, nu a ta |

**Ce se rupe fără el**

- **„Cannot resolve symbol R"**: nu e o problemă de resurse, e un **build eșuat**. `R.java` se generează doar dacă aapt2 a trecut. Fix: Build → Clean Project, apoi Rebuild, și citește primul error din Build Output, nu ultimul.
- **`AAPT: error: resource string/foo not found`**: ai referit o resursă care nu există. Build-ul cade, dar mesajul e clar — spre deosebire de ID-urile lipsă la runtime.
- **`Resources$NotFoundException`**: resursa există la compilare dar nu se poate încărca la runtime — tipic o temă greșită în manifest sau un `@style` care referă alt `@style` inexistent.
- **`findViewById` întoarce `null`**: ID-ul există în `R` (deci compilarea trece), dar view-ul nu e în arborele pe care îl cauți. Cauza nu e resursa, e layout-ul greșit sau ordinea apelurilor (vezi 37.8).

**Unde îl vezi în G1097**

`activity_main.xml` referă trei resurse deodată:

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:contentDescription="Add"
    app:srcCompat="@drawable/outline_add_24" />
```

`activity_item.xml` referă un array definit în `strings.xml`:

```xml
<Spinner
    android:id="@+id/spGenre"
    android:entries="@array/movie_genre" />
```

iar `strings.xml` conține exact array-ul:

```xml
<string-array name="movie_genre">
    <item>Drama</item>
    <item>Action</item>
    ...
    <item>Mystery</item>
</string-array>
```

Consecința: `spGenre` are 10 elemente **fără ca `ItemActivity` să scrie vreo literă de gen**. `fillForm` doar caută textul în listă:

```java
for (int index = 0; index < spGenre.getCount(); index++) {
    if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
        spGenre.setSelection(index);
        break;
    }
}
```

Dacă adaugi „Documentary" în `strings.xml`, codul îl vede automat. Dacă îl adaugi doar în cod, spinner-ul nu îl are.

`MainActivity` folosește și o resursă a **sistemului**, nu a aplicației:

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

`android.R.layout.simple_list_item_1` este un layout livrat de Android, cu un singur `TextView`. Se vede prefixul `android.` — asta îl deosebește de `R.layout.*`, care e al tău.

**Confuzia tipică**

„`R` este o clasă pe care o scriu eu." Nu. `R.java` se generează la fiecare build în `build/generated/`, iar dacă o editezi, modificările dispar. De aceea nu apare în `src/` și de aceea nu o vei găsi niciodată în repo.

A doua: „valorile din `R.id` sunt stabile, le pot salva." Nu. Sunt generate de aapt2 și se pot schimba de la un build la altul când adaugi sau scoți resurse. Nu se persistă niciodată un `R.id` într-un fișier, într-o bază de date sau într-un `SharedPreferences`. Persistă numele (`"etTitle"`) sau, mai bine, o cheie proprie.

A treia: „`@+id/` și `@id/` sunt sinonime". Nu. `@+id/x` **declară**; `@id/x` **referă**. Dacă folosești `@id/x` fără să fi declarat `x` nicăieri, build-ul cade cu `resource id/x not found`. În practică, prima apariție într-un fișier folosește `@+id/`, restul `@id/` — dar în codul de zi cu zi se pune `@+id/` peste tot, pentru că e idempotent.

A patra, cea mai costisitoare la test: „`?attr/colorPrimary` și `@color/purple_500` sunt același lucru". Nu. `@color/...` e o culoare fixă. `?attr/...` e un **rol de temă**: se rezolvă la runtime la culoarea pe care tema o atribuie acelui rol, deci se schimbă automat în dark mode. `activity_item.xml` folosește `?attr/colorSurface`, `?attr/colorOnSurface`, `?attr/colorPrimary` exact din acest motiv.

---

## Conceptul 37.4 — AndroidManifest.xml

**Ce este**

`AndroidManifest.xml` este **contractul dintre aplicația ta și sistemul de operare**. El declară ce componente are aplicația (`activity`, `service`, `broadcast receiver`, `content provider`), ce permisiuni cere, ce temă folosește, ce clasă de `Application` rulează și ce `Intent`-uri poate primi fiecare componentă. Sistemul îl citește **la instalare**, nu la rulare, și construiește din el indexul prin care rezolvă orice `Intent`.

**De ce există**

Pentru că sistemul trebuie să știe ce poate porni **înainte** să încarce codul tău. Când apeși o iconiță, Android nu are încă procesul tău pornit — are doar o bază de date cu pachete instalate. Fără manifest, `startActivity(new Intent(this, ItemActivity.class))` ar fi un apel către o clasă despre care sistemul nu știe nimic: n-ar ști dacă are voie să o creeze, în ce proces, cu ce temă, cu ce mod de tastatură.

Are și un rol de securitate. `android:exported` este granița: o activitate `exported="true"` poate fi pornită de orice aplicație de pe telefon; una `exported="false"` doar de aplicația ta. Fără această declarație, orice aplicație ar putea deschide orice ecran al oricui.

**Cum funcționează**

```
INSTALARE
  APK -> PackageManagerService.parse
       -> pentru fiecare <activity>: înregistrează (nume clasă, intent-filter, exported, temă)
       -> verifică permisiunile cerute
       -> indexul e acum în /data/system/packages.xml

LANSARE
  Intent explicit  -> are componenta (pachet + clasă) -> caută direct
  Intent implicit  -> are acțiune + categorie + data  -> potrivește cu intent-filter-ele
                    -> 0 potriviri:  ActivityNotFoundException
                    -> 2+ potriviri: dialog „Open with"
                    -> verifică exported înainte de a porni
```

Ordinea de prioritate dintre manifest și cod, care se inversează des în mintea oamenilor: **manifestul câștigă** pentru tot ce ține de sistem (poate fi pornită, cu ce temă, în ce proces, cu ce `launchMode`), iar **codul câștigă** pentru tot ce ține de comportament (ce face `onCreate`, ce listeneri are butonul). Nu poți porni o activitate declarată `exported="false"` din altă aplicație, oricât cod ai scrie.

**Ce se rupe fără el**

- **Activitate nedeclarată**: `ActivityNotFoundException: Unable to find explicit activity class {ro.ase.ie.g1097/ro.ase.ie.g1097.activities.ItemActivity}. Have you declared this activity in your AndroidManifest.xml?` — mesajul îți spune exact ce lipsește.
- **`android:name` greșit**: dacă scrii `android:name="ItemActivity"` fără punct și fără pachet, Android caută `ro.ase.ie.g1097.ItemActivity`, nu `.activities.ItemActivity`. Rezultatul e tot `ActivityNotFoundException`, dar cauza e alta.
- **`android:exported` lipsă pe API 31+**: dacă activitatea are `<intent-filter>`, build-ul eșuează cu un mesaj de la manifest merger care cere o valoare explicită pentru `android:exported` pe componenta respectivă. Nu e warning, e eroare de build.
- **Temă inexistentă**: `Resources$NotFoundException` la pornire, înainte de `onCreate` — un crash pe care nu îl poți prinde în cod.
- **Filtru `LAUNCHER` lipsă**: aplicația se instalează, dar nu apare în launcher (vezi 37.1).

**Unde îl vezi în G1097**

Fișierul întreg are 30 de linii și fiecare contează:

```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:supportsRtl="true"
    android:theme="@style/Theme.G1097">
    <activity
        android:name=".activities.MainActivity"
        android:exported="true"
        android:windowSoftInputMode="adjustResize">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
    <activity
        android:name=".activities.ItemActivity"
        android:exported="false"
        android:windowSoftInputMode="adjustResize" />
</application>
```

Patru decizii, fiecare cu o consecință:

1. **`MainActivity` are `exported="true"`** pentru că launcher-ul este o altă aplicație și trebuie să o poată porni. Fără `true`, iconița nu ar funcționa.
2. **`ItemActivity` are `exported="false"`** pentru că e un ecran intern. Nimeni din afară nu are ce căuta în formularul de film.
3. **`android:windowSoftInputMode="adjustResize"` pe ambele** — când apare tastatura, fereastra se micșorează, iar `ScrollView` din `activity_item.xml` poate derula până la câmpul activ. Fără el, tastatura ar acoperi câmpul.
4. **`android:theme="@style/Theme.G1097"` pe `<application>`**, nu pe fiecare activitate — tema se moștenește. De aici vin toate `?attr/colorPrimary` din layout-uri.

Observă ce **nu** este în manifest: niciun layout, niciun `findViewById`, nicio logică. Manifestul nu spune ce face aplicația, spune doar **ce există** în ea.

**Confuzia tipică**

„Manifestul declară layout-ul." Nu. Layout-ul se leagă în cod, prin `setContentView(R.layout.activity_main)`. Manifestul nu știe ce e un layout.

A doua: „`exported="true"` înseamnă că e publică/importantă". Înseamnă doar **pornibilă din altă aplicație**. O activitate `exported="false"` poate fi perfect funcțională și esențială — `ItemActivity` este exact asta.

A treia: „trebuie să declar toate clasele în manifest". Nu, doar **componentele** sistemului: activități, servicii, receiver-e, provider-i. `Movie` nu apare în manifest și nici nu trebuie.

A patra, specifică acestui proiect: „dacă adaug o activitate nouă, o adaug doar în cod". Dacă nu o declari, `startActivity` aruncă `ActivityNotFoundException`. Și invers: dacă o declari dar nu o folosești, nu se rupe nimic — doar indexul sistemului are o intrare inutilă.

---

## Conceptul 37.5 — View și ViewGroup: arborele de view-uri

**Ce este**

`View` este clasa de bază pentru **orice element vizual**: un dreptunghi care știe să se deseneze, să primească atingerea, să aibă un ID, o poziție, o dimensiune și o vizibilitate. `ViewGroup` este o subclasă a lui `View` care **conține alți `View`** și decide unde stau. Un `TextView` este `View`; un `LinearLayout` este `ViewGroup`; un `LinearLayout` care conține un `TextView` este un arbore cu două noduri.

**De ce există**

Pentru că o interfață este o **compunere**, nu o listă plată. Un card de film are o imagine, un titlu, un subtitlu, o bară de rating și trei chip-uri — iar cardul stă într-o listă, care stă într-un `FrameLayout`, care stă într-o fereastră. Arborele nu e o alegere estetică: este singura structură care permite **o singură parcurgere recursivă** pentru măsurare, pentru desenare și pentru distribuirea atingerii. Fără el ai avea nevoie de coordonate absolute pentru fiecare element, iar orice schimbare de dimensiune a ecranului ar strica totul.

**Cum funcționează**

`LayoutInflater` citește XML-ul și, pentru fiecare tag, creează obiectul corespunzător **prin reflecție**, apelând constructorul cu doi parametri `(Context, AttributeSet)`. `<FrameLayout>` devine `new FrameLayout(context, attrs)`, `<TextView>` devine `new TextView(context, attrs)`, iar `<com.google.android.material.card.MaterialCardView>` devine clasa aceea, cu numele complet. Apoi fiecare copil este adăugat în părintele lui, iar părintele îl ține într-o listă internă.

Arborele ecranului principal din G1097 (simplificat — partea de sus a arborelui aparține sistemului și temei, nu layout-ului tău):

```
DecorView                       <- creat de sistem, nu de tine
└── LinearLayout (vertical)
    ├── [bara de titlu / AppBar] <- din temă
    └── FrameLayout  android.R.id.content   <- aici ajunge layout-ul tău
        └── FrameLayout  @id/main           <- rădăcina din activity_main.xml
            ├── ListView  @id/listView
            │   ├── TextView   (rândul 0, inflatat din simple_list_item_1)
            │   ├── TextView   (rândul 1)
            │   └── TextView   (rândul 2)
            └── FloatingActionButton  @id/floatingActionButton
```

Și arborele formularului, care e mai adânc:

```
ScrollView  @id/main
└── LinearLayout (vertical)
    ├── TextView  „Movie details"
    ├── TextView  „Fill in the information below and save."
    ├── MaterialCardView  (Basics)
    │   └── LinearLayout (vertical)
    │       ├── TextView  @id/tvTile
    │       ├── TextInputLayout -> TextInputEditText @id/etTitle
    │       ├── TextView  @id/tvGenre
    │       ├── MaterialCardView -> Spinner @id/spGenre
    │       └── TextInputLayout -> TextInputEditText @id/etRelease
    ├── MaterialCardView  (Production)
    │   └── LinearLayout (vertical)
    │       ├── TextView @id/tvBudget
    │       ├── TextInputLayout -> TextInputEditText @id/etBudget
    │       ├── LinearLayout -> TextView @id/tvDuration + TextView @id/tvDurationValue
    │       ├── SeekBar @id/sbDuration
    │       └── LinearLayout -> două TextView (0 min / 300 min)
    ├── MaterialCardView  (Your verdict)
    │   └── LinearLayout (vertical)
    │       ├── TextView @id/tvRating
    │       ├── RatingBar @id/rbRating
    │       ├── View (separator 1dp)
    │       ├── LinearLayout -> TextView @id/tvWatched + TextView @id/tvWatchedValue
    │       │                    + MaterialSwitch @id/swWatched + MaterialCheckBox @id/cbOnWatchList
    │       ├── View (separator 1dp)
    │       ├── TextView @id/tvGuidance
    │       └── HorizontalScrollView -> RadioGroup @id/rgApproval -> 5 MaterialRadioButton
    ├── MaterialCardView  (Poster)
    │   └── LinearLayout -> TextInputLayout -> TextInputEditText @id/etPoster
    └── MaterialButton @id/btnMovieAction
```

Două consecințe directe ale arborelui, pe care le vei folosi la test:

1. **`findViewById` caută în subarbore**, nu în toată aplicația. Dacă îl apelezi pe `rgApproval`, găsește doar ce e sub el. Dacă îl apelezi pe `Activity`, caută din `DecorView` în jos — deci găsește tot ce e în layout-ul setat cu `setContentView` (vezi 37.8).
2. **Ordinea copiilor este ordinea desenării.** În `FrameLayout`, ultimul copil se desenează deasupra celorlalți. De aceea FAB-ul este după `ListView` în `activity_main.xml` — altfel ar fi acoperit de listă.

**Ce se rupe fără el**

- **`IllegalStateException: ScrollView can host only one direct child`**: `ScrollView` este un `ViewGroup` care acceptă exact un copil, pentru că nu are cum să decidă cum să împartă înălțimea între doi. În `activity_item.xml`, tocmai de aceea tot conținutul stă într-un singur `LinearLayout`.
- **Un view adăugat în cod fără `LayoutParams`**: `addView(view)` fără parametri folosește `LayoutParams`-ul implicit al părintelui, care poate fi `WRAP_CONTENT`/`WRAP_CONTENT` — elementul apare, dar nu unde te aștepți.
- **`findViewById` pe un view care nu e în arbore**: întoarce `null`, fără eroare. Simptomul e `NullPointerException` mai târziu, într-o cu totul altă metodă.
- **Un `ViewGroup` care nu e `View`**: nu există. `ViewGroup extends View`, deci un `LinearLayout` poate fi pus oriunde se acceptă un `View` — inclusiv ca frunză într-un alt `LinearLayout`.

**Unde îl vezi în G1097**

`activity_main.xml` este cel mai simplu arbore din proiect — două frunze într-un `FrameLayout`:

```xml
<FrameLayout
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">
    <ListView android:id="@+id/listView" ... />
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_gravity="bottom|end" ... />
</FrameLayout>
```

`activity_item.xml` arată compunerea pe patru niveluri, cu `MaterialCardView` ca secțiune:

```xml
<ScrollView android:id="@+id/main" android:fillViewport="true">
    <LinearLayout android:orientation="vertical">
        <com.google.android.material.card.MaterialCardView>
            <LinearLayout android:orientation="vertical">
                <TextView android:id="@+id/tvTile" />
                <com.google.android.material.textfield.TextInputLayout>
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle" />
                </com.google.android.material.textfield.TextInputLayout>
```

`movie_item.xml` arată arborele unui **rând**, nu al unui ecran — și e singurul layout din G1097 care nu e folosit încă:

```xml
<com.google.android.material.card.MaterialCardView>
    <LinearLayout android:orientation="horizontal">
        <ImageView android:id="@+id/moviePoster" />
        <LinearLayout android:layout_width="0dp" android:layout_weight="1"
                      android:orientation="vertical">
            <TextView android:id="@+id/movieTitle" />
            <TextView android:id="@+id/movieSubtitle" />
            ...
```

**Confuzia tipică**

„Rădăcina din XML este rădăcina ecranului." Nu. Deasupra ei mai există `android.R.id.content` (un `FrameLayout` pus de `AppCompatActivity`) și `DecorView`, pus de sistem. Consecința practică: `findViewById(R.id.main)` găsește rădăcina ta, dar `getWindow().getDecorView()` întoarce cu totul altceva — și de aceea listener-ul de insets din G1097 se pune pe `R.id.main`, nu pe decor.

A doua: „`ViewGroup` și `View` sunt lucruri diferite". `ViewGroup` **este** un `View`, cu dreptul de a avea copii. De aici vine flexibilitatea: poți pune un `LinearLayout` oriunde încape un `TextView`, și poți trata orice `ViewGroup` ca pe un `View` când nu te interesează copiii lui.

A treia: „dacă un view nu se vede, nu există". Există, doar are `visibility="gone"` (nu ocupă spațiu) sau `"invisible"` (ocupă spațiu, dar nu se desenează). `findViewById` îl găsește în ambele cazuri, iar `getWidth()` poate fi 0 pentru un `GONE`.

---

## Conceptul 37.6 — Cum se desenează un ecran: measure, layout, draw

**Ce este**

Desenarea unui ecran se face în **trei passe** recursive peste arborele de view-uri: **measure** (cât de mare vrea să fie fiecare view), **layout** (unde se așază fiecare, în coordonate absolute față de părinte) și **draw** (desenarea efectivă pe un `Canvas`). Fiecare pas coboară de la rădăcină la frunze, iar rezultatul fiecăruia îl hrănește pe următorul.

**De ce există**

Pentru că dimensiunea ecranului nu se știe la compilare. Un telefon are 1080×2400 pixeli, altul 1440×3120, o tabletă are alt raport, iar utilizatorul poate roti ecranul sau deschide tastatura în orice moment. Dacă ai scrie coordonate fixe, layout-ul s-ar rupe pe orice alt dispozitiv. Cele trei passe sunt mecanismul prin care un layout **declarativ** („pune-l sub titlu, umple lățimea") devine poziții **concrete** („stânga=0, sus=312, dreapta=1080, jos=420").

**Cum funcționează**

Cheia este `MeasureSpec`: un `int` împachetat care conține un **mod** și o **dimensiune**.

| Mod | Sens | Cine îl dă |
|---|---|---|
| `EXACTLY` | „ai exact atâția pixeli" | părintele, când copilul are `match_parent` sau o dimensiune fixă |
| `AT_MOST` | „ai cel mult atâția" | părintele, când copilul are `wrap_content` |
| `UNSPECIFIED` | „fă cum vrei" | un `ScrollView` pe verticală, un `HorizontalScrollView` pe orizontală |

Passele, pe un exemplu real din `movie_item.xml` — coloana de text are `layout_width="0dp"` și `layout_weight="1"`:

```
1. MEASURE  (de sus în jos)
   părintele primește MeasureSpec de la părintele lui
     -> calculează MeasureSpec-ul fiecărui copil
     -> copilul cu wrap_content primește AT_MOST(lățimea părintelui)
     -> copilul cu 0dp + weight primește, în prima trecere, 0 sau AT_MOST
     -> părintele adună înălțimile cerute, apoi împarte RESTUL după weight
     -> a doua trecere: copilul cu weight primește EXACTLY(spațiul rămas)
     -> fiecare view își salvează getMeasuredWidth() / getMeasuredHeight()

2. LAYOUT   (tot de sus în jos)
   părintele știe poziția lui absolută
     -> calculează poziția fiecărui copil față de el
     -> child.layout(left, top, right, bottom)
     -> fiecare view își salvează getLeft(), getTop(), getWidth(), getHeight()

3. DRAW     (tot de sus în jos)
   canvas desenează: background -> conținut propriu (onDraw) -> copii -> scrollbars
     -> un TextView desenează textul, un ImageView desenează bitmap-ul
     -> un ViewGroup nu desenează nimic propriu, doar își cheamă copiii
```

Cine pornește cele trei passe: `Choreographer`, sincronizat cu vsync-ul ecranului (60, 90 sau 120 de ori pe secundă). Când ceva se schimbă, view-ul cere o nouă trecere:

| Apel | Ce invalidează | Când îl folosești |
|---|---|---|
| `requestLayout()` | measure + layout + draw | ai schimbat o dimensiune, un text care schimbă înălțimea, ai adăugat un copil |
| `invalidate()` | doar draw | ai schimbat o culoare, o valoare afișată, fără să se schimbe dimensiunea |

`setText()` pe un `TextView` apelează singur `requestLayout()` dacă textul nou are altă dimensiune — de aceea nu trebuie să o faci tu. `setPadding()` apelează `requestLayout()` — de aici efectul listener-ului de insets din G1097.

**Ce se rupe fără el**

- **`getWidth()` în `onCreate()` întoarce 0**: în `onCreate` arborele există (după `setContentView`), dar nu a fost măsurat încă. Prima măsurare se întâmplă după `onResume`, când fereastra devine vizibilă. Fix: `view.post(() -> ...)` sau `doOnLayout`.
- **`0dp` fără `layout_weight`**: `0dp` înseamnă „zero pixeli", nu „umple". Dacă uiți `weight`, elementul dispare complet — nu primești eroare, primești un spațiu gol.
- **`layout_weight` pe `wrap_content`**: funcționează, dar împarte **spațiul rămas** după ce fiecare copil și-a luat dimensiunea naturală. E o sursă clasică de layout-uri care arată „aproape bine".
- **`ScrollView` cu un copil `match_parent` pe verticală**: `ScrollView` dă `UNSPECIFIED` pe verticală, deci `match_parent` nu are față de ce să se raporteze. De aceea `activity_item.xml` are `android:fillViewport="true"` — forțează copilul să umple viewport-ul când conținutul e mai scurt, fără să spargă derularea când e mai lung.

**Unde îl vezi în G1097**

`movie_item.xml` — `0dp` + `weight` pentru coloana de text, ca să ia tot ce rămâne după poster:

```xml
<ImageView
    android:id="@+id/moviePoster"
    android:layout_width="96dp"
    android:layout_height="140dp" />

<LinearLayout
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    android:layout_weight="1"
    android:orientation="vertical">
```

`activity_recycler_view.xml` din `DMA06` — același mecanism, pe verticală, ca `RecyclerView`-ul să ocupe tot spațiul rămas sub header:

```xml
<include layout="@layout/layout_number_header" />
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/rvNumbers"
    android:layout_width="match_parent"
    android:layout_height="0dp"
    android:layout_weight="1" />
```

`activity_item.xml` — `fillViewport`, care schimbă MeasureSpec-ul copilului:

```xml
<ScrollView
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true">
```

Și listener-ul de insets din ambele activități, care provoacă **intenționat** o nouă trecere de layout:

```java
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
    return insets;
});
```

`setPadding` schimbă dimensiunea utilă a rădăcinii, deci cere `requestLayout()`. Fără acest apel, conținutul ar sta sub bara de stare — `EdgeToEdge.enable(this)` face fereastra să deseneze sub bare, iar padding-ul este compensația.

**Confuzia tipică**

„`match_parent` și `0dp` + `weight` sunt echivalente." Nu. `match_parent` cere **toată** dimensiunea părintelui, indiferent de frați — deci într-un `LinearLayout` orizontal, doi copii cu `match_parent` se calcă unul pe altul. `0dp` + `weight` cere **o parte** din spațiul rămas, proporțional cu `weight`. `match_parent` = „tot", `0dp`+`weight` = „partea mea".

A doua: „`onCreate` știe cât de mare e ecranul". Nu. `onCreate` construiește arborele; măsurarea se face după, în prima trecere de layout. Orice cod care depinde de dimensiuni trebuie amânat.

A treia: „`invalidate()` și `requestLayout()` sunt sinonime". Nu. `invalidate()` doar redesenează, păstrând pozițiile; `requestLayout()` remăsoară tot subarborele. Dacă schimbi textul unui `TextView` și apelezi doar `invalidate()`, textul nou poate fi tăiat, pentru că înălțimea nu a fost recalculată.

A patra: „cele trei passe sunt separate în timp". Sunt separate **logic**, dar rulează în aceeași trecere de desenare, una după alta, sincronizate cu vsync-ul. De aceea o schimbare de layout în `onCreate` nu produce flicker: totul se rezolvă înainte de primul cadru afișat.

---
## Conceptul 37.7 — Layout-urile: FrameLayout, LinearLayout, ConstraintLayout, ScrollView

**Ce este**

Un layout este un `ViewGroup` care implementează o **regulă de aranjare** pentru copiii lui. `FrameLayout` îi stivuiește unul peste altul, în colțul din stânga sus. `LinearLayout` îi pune într-un singur rând sau o singură coloană, în ordinea din XML. `ConstraintLayout` îi poziționează prin relații față de părinte și față de frați. `ScrollView` este un `FrameLayout` special care acceptă **un singur copil** și îl lasă să fie mai înalt decât ecranul, permițând derularea.

**De ce există**

Pentru că „unde stă fiecare element" nu are un singur răspuns corect. Un ecran cu un singur conținut vrea un `FrameLayout`; un formular vrea o coloană; un ecran care trebuie să arate bine pe telefon și pe tabletă vrea constrângeri relative. Dacă ar exista un singur layout, ar trebui să fie suficient de general pentru toate — și ar fi greu de folosit pentru oricare. Android a ales **layout-uri specializate**, fiecare cu un algoritm simplu, iar tu alegi algoritmul potrivit. Este exact inversul unui framework cu poziționare absolută: nu spui unde, spui după ce regulă.

**Cum funcționează**

Fiecare layout își implementează propriul `onMeasure` și `onLayout`. Diferența dintre ele este **algoritmul**, nu API-ul.

**`FrameLayout`** — stivă, toți copiii în colțul din stânga sus, ultimul desenat deasupra:

```
+---------------------------+
| [copil 1]                 |
| [copil 2]  <- peste el    |
| [copil 3]                 |
+---------------------------+
```

Copiii se pot muta cu `android:layout_gravity` (`bottom|end`, `center`). Nu are `weight`, nu are orientare. Ordinea din XML este ordinea z-order.

**`LinearLayout`** — un singur ax, `orientation="horizontal"` sau `"vertical"`:

```
vertical:                     horizontal:
+-------------------+         +--------+--------+--------+
| [copil 1]         |         | copil1 | copil2 | copil3 |
| [copil 2]         |         +--------+--------+--------+
| [copil 3]         |
+-------------------+
```

Matematica lui `weight`, care se cere la test:

```
spațiu total al părintelui:            360dp
copiii fără weight cer:                 96dp + 12dp (margin) = 108dp
spațiu rămas:                          360 - 108 = 252dp
suma weight-urilor:                    1
fiecare copil cu weight:               252 * (weight / suma) = 252dp
```

Deci `weight` **nu** împarte tot spațiul, împarte **restul**. Dacă toți copiii au `0dp` + `weight`, atunci restul este tot spațiul, și pare că împarte totul — de aici confuzia.

**`ConstraintLayout`** — fiecare copil are cel puțin o constrângere pe orizontală și una pe verticală:

```
        parent top
            |
   +--------+--------+
   |  [TextView]     |  <- start -> parent start, top -> parent top
   +--------+--------+
            |
        parent bottom
```

Are `app:layout_constraintStart_toStartOf`, `..._toEndOf`, `app:layout_constraintHorizontal_bias` (0 = stânga, 0.5 = centru, 1 = dreapta), chains și `Guideline`. Avantajul lui real: **un singur nivel de adâncime** pentru layout-uri complexe, deci measure-ul nu se repetă de N ori.

**`ScrollView`** — un `FrameLayout` care dă copilului `UNSPECIFIED` pe verticală:

```
+-------------------+  <- viewport (înălțimea ecranului)
| conținut vizibil  |
| ...               |
+-------------------+
| conținut ascuns   |  <- există, se ajunge prin derulare
| ...               |
+-------------------+
```

`android:fillViewport="true"` schimbă comportamentul când conținutul e **mai scurt** decât viewport-ul: îl întinde să umple ecranul. Fără el, un formular scurt ar lăsa o zonă goală dedesubt, iar fundalul ar fi al ferestrei, nu al conținutului.

**Ce se rupe fără el**

- **`FrameLayout` cu `android:orientation`**: atributul este **ignorat**, fără warning în build. Exact asta se întâmplă în `activity_main.xml` din G1097 — are `android:orientation="horizontal"` pe un `FrameLayout`. Nu strică nimic, dar trădează o neînțelegere: orientarea nu are sens într-o stivă.
- **`ScrollView` cu doi copii**: `IllegalStateException: ScrollView can host only one direct child`. Nu e o limitare arbitrară — `ScrollView` nu are cum să decidă cum să împartă derularea între doi copii independenți.
- **`ConstraintLayout` cu un copil fără constrângeri**: view-ul „sare" în colțul din stânga sus, fără eroare. Android Studio avertizează în editor („This view is not constrained"), dar build-ul trece.
- **`LinearLayout` orizontal cu prea mulți copii**: se înghesuie și ultimii ies din ecran, fără scroll. Simptomul e conținut tăiat, nu crash.
- **`weight` uitat pe `0dp`**: elementul are dimensiune zero și dispare. Vezi 37.6.

**Unde îl vezi în G1097**

`activity_main.xml` — `FrameLayout` cu două frunze, FAB-ul poziționat cu `layout_gravity`:

```xml
<FrameLayout
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">          <!-- ignorat: FrameLayout nu are orientare -->

    <ListView android:id="@+id/listView" ... />

    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp" ... />
</FrameLayout>
```

`activity_item.xml` — `ScrollView` cu **un singur** copil `LinearLayout` vertical, care conține patru `MaterialCardView`:

```xml
<ScrollView android:id="@+id/main" android:fillViewport="true">
    <LinearLayout android:orientation="vertical" android:paddingHorizontal="16dp">
        <MaterialCardView> ... Basics ... </MaterialCardView>
        <MaterialCardView> ... Production ... </MaterialCardView>
        <MaterialCardView> ... Your verdict ... </MaterialCardView>
        <MaterialCardView> ... Poster ... </MaterialCardView>
        <MaterialButton android:id="@+id/btnMovieAction" />
    </LinearLayout>
</ScrollView>
```

`movie_item.xml` — `LinearLayout` orizontal cu `weight` pe coloana de text, și un `LinearLayout` orizontal interior pentru rândul de rating:

```xml
<LinearLayout android:orientation="horizontal" android:padding="12dp">
    <ImageView android:layout_width="96dp" android:layout_height="140dp" />
    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">
        ...
        <LinearLayout android:orientation="horizontal" android:gravity="center_vertical">
            <RatingBar android:id="@+id/movieRating" ... />
            <TextView android:id="@+id/movieRatingValue" ... />
        </LinearLayout>
```

`DMA02/activity_main.xml` — `ConstraintLayout`, singurul din proiectele de curs care îl folosește:

```xml
<androidx.constraintlayout.widget.ConstraintLayout android:id="@+id/main">
    <com.google.android.material.appbar.MaterialToolbar
        android:id="@+id/toolbar"
        android:layout_height="?attr/actionBarSize" />
    <TextView
        android:id="@+id/textView"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    <Button
        android:id="@+id/button"
        app:layout_constraintBottom_toTopOf="@+id/textView"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

**Confuzia tipică**

„`FrameLayout` este pentru fragmente, `LinearLayout` pentru restul." Nu există o asemenea regulă. `FrameLayout` este alegerea corectă oricând ai **elemente suprapuse** — un conținut și un buton plutitor peste el, exact ca în `activity_main.xml`.

A doua: „`weight` împarte lățimea totală". Împarte **restul**, după ce fiecare copil și-a luat dimensiunea proprie. Dacă un copil are `100dp` fix, acel `100dp` iese din calcul înainte de împărțire.

A treia: „`ConstraintLayout` este mereu mai bun". Este mai bun când ai multe relații între elemente; este **mai rău** când ai o coloană simplă, pentru că adaugi constrângeri degeaba. `activity_item.xml` folosește `LinearLayout` pentru o coloană — alegerea corectă.

A patra: „`ScrollView` face orice conținut derulabil". Nu: doar pe verticală, doar un copil, și doar dacă copilul acela e mai înalt decât viewport-ul. Pentru orizontală ai `HorizontalScrollView` — folosit în `activity_item.xml` pentru rândul de cinci radio-butone, care nu încap pe un ecran îngust.

---

## Conceptul 37.8 — findViewById și de ce e fragil

**Ce este**

`findViewById(int id)` este metoda prin care ceri unui view — sau unei activități — să caute în arborele lui un view cu ID-ul dat și să îl întoarcă. Semnătura este generică: `<T extends View> T findViewById(int id)`, ceea ce înseamnă că **tipul îl deduci din atribuire**. Nu verifică nimic la runtime: face un cast, iar dacă tipul nu se potrivește, primești `ClassCastException`.

**De ce există**

Pentru că XML-ul și Java sunt două limbaje separate, iar legătura dintre ele se face la runtime. În XML ai declarat `<TextInputEditText android:id="@+id/etTitle" />`; în Java ai nevoie de o referință la obiectul acela pentru a-l citi. `findViewById` este puntea: un `int` generat de aapt2, căutat într-un arbore de obiecte create de `LayoutInflater`.

**Cum funcționează**

Sunt **două** metode cu același nume, și diferența lor se cere la test:

| Apel | Unde caută |
|---|---|
| `activity.findViewById(id)` | din `DecorView` în jos — adică tot ecranul, inclusiv bara de titlu |
| `view.findViewById(id)` | doar în subarborele acelui view |

Implementarea din `View` este o căutare în adâncime cu verificare de ID:

```
View.findViewById(id)
  ├── dacă this.mID == id -> return this
  └── dacă this e ViewGroup -> pentru fiecare copil:
        └── copil.findViewById(id)   (recursiv)
  └── dacă nu s-a găsit nimic -> return null
```

Costul este proporțional cu numărul de view-uri din subarbore. Pentru un formular cu 30 de view-uri și 13 apeluri, costul e neglijabil — deci **motivul pentru care `findViewById` e considerat fragil nu este performanța**. Motivele reale sunt trei:

1. **Poate întoarce `null`** și compilatorul nu te avertizează. `etTitle.setText(...)` pe `null` aruncă `NullPointerException` la runtime, într-o metodă care poate fi departe de apel.
2. **Nu este type-safe.** `TextView tv = findViewById(R.id.listView)` compilează, dar aruncă `ClassCastException: android.widget.ListView cannot be cast to android.widget.TextView` la runtime.
3. **Nu este refactor-safe.** Redenumești `etTitle` în `etMovieTitle` în XML: build-ul cade cu `cannot find symbol`, ceea ce e bine. Dar dacă **muți** view-ul în alt layout și uiți să actualizezi `setContentView`, build-ul trece și primești `null`. A doua situație e cea care costă.

**Ce se rupe fără el**

- **`findViewById` înainte de `setContentView`**: arborele nu există încă, deci întoarce `null` pentru orice ID. Simptomul e `NullPointerException` în `initControls()`. Regula: `setContentView` primul, `findViewById` după.
- **ID corect, layout greșit**: `findViewById(R.id.etTitle)` într-o activitate care a făcut `setContentView(R.layout.activity_main)` → `null`, fără eroare de compilare. ID-ul există în `R`, dar nu în arborele curent.
- **Tip greșit**: `ClassCastException` la runtime, cu mesajul exact al celor două clase.
- **ID inexistent**: `cannot find symbol: variable etTitl` — eroare de compilare, cea mai bună variantă posibilă.

**Unde îl vezi în G1097**

`ItemActivity.initControls()` — 13 apeluri, unul după altul, fiecare cu tipul declarat în câmp:

```java
private void initControls() {
    etTitle = findViewById(R.id.etTitle);
    etRelease = findViewById(R.id.etRelease);
    spGenre = findViewById(R.id.spGenre);
    etBudget = findViewById(R.id.etBudget);
    sbDuration = findViewById(R.id.sbDuration);
    rbRating = findViewById(R.id.rbRating);
    rgApproval = findViewById(R.id.rgApproval);
    cbonWatchList = findViewById(R.id.cbOnWatchList);
    swWatched = findViewById(R.id.swWatched);
    etPoster = findViewById(R.id.etPoster);
    btMovieAction = findViewById(R.id.btnMovieAction);
    tvDurationValue = findViewById(R.id.tvDurationValue);
    tvWatchedValue = findViewById(R.id.tvWatchedValue);
}
```

`MainActivity.initControls()` — doar două, dar ordinea lor față de `setAdapter` contează:

```java
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    listView = findViewById(R.id.listView);
    listView.setAdapter(movieAdapter);
}
```

`ItemActivity.onCreate()` — ordinea obligatorie, vizibilă în primele șapte linii:

```java
super.onCreate(savedInstanceState);
EdgeToEdge.enable(this);
setContentView(R.layout.activity_item);          // 1. arborele există
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...);  // 2. primul findViewById
initControls();                                   // 3. restul
initListeners();
```

Dacă ai muta `initControls()` înainte de `setContentView`, toate cele 13 referințe ar fi `null` și prima care ar fi folosită ar arunca `NullPointerException`.

**Confuzia tipică**

„`findViewById` este lent, de aceea se folosește ViewBinding." Nu performanța e problema. Un `findViewById` pe un arbore de 50 de view-uri durează microsecunde, iar în `onCreate` se execută o singură dată. Problema este **siguranța la compilare**: `null`-ul posibil și cast-ul neverificat. ViewBinding rezolvă exact aceste două lucruri (vezi 37.9).

A doua: „`findViewById` caută în toată aplicația". Nu. Caută în subarborele obiectului pe care îl apelezi. Dacă îl apelezi pe `Activity`, ajunge la tot ecranul pentru că `Activity` deleagă la fereastră; dacă îl apelezi pe un `View`, caută doar sub el. Consecința practică: într-un adapter, `findViewById` se apelează pe `convertView`, nu pe `Activity` — altfel ai căuta în tot ecranul pentru fiecare rând (vezi 37.18).

A treia: „dacă ID-ul există în `R`, `findViewById` îl găsește". Nu. `R.id.etTitle` există pentru că aapt2 l-a generat din XML, dar view-ul există **în arbore** doar dacă layout-ul care îl conține a fost inflatat. Două lucruri diferite, care coincid doar când totul e în regulă.

---

## Conceptul 37.9 — ViewBinding

**Ce este**

ViewBinding este o funcționalitate a plugin-ului Android Gradle care **generează o clasă Java pentru fiecare layout XML**. Clasa se numește după fișier (`activity_main.xml` → `ActivityMainBinding`), are un câmp public pentru fiecare view cu `android:id`, de tipul corect, și se obține printr-un `inflate`. Nu mai scrii `findViewById` deloc.

**De ce există**

Pentru a elimina cele trei fragilități din 37.8 printr-o singură schimbare: **legătura dintre XML și cod se verifică la compilare**. Clasa generată are exact câmpurile pentru ID-urile care există în acel layout, cu tipul din XML. Dacă ștergi un ID, build-ul cade. Dacă îl redenumești, build-ul cade. Nu poate să întoarcă `null` pentru un câmp declarat, pentru că `inflate` a construit deja tot arborele.

**Cum funcționează**

Se activează cu o singură linie în `build.gradle.kts`:

```kotlin
android {
    buildFeatures { viewBinding = true }
}
```

La următorul build, AGP generează pentru fiecare layout o clasă în pachetul `namespace`:

```
res/layout/activity_main.xml  ──build──>  ro.ase.ie.dma05.databinding.ActivityMainBinding
res/layout/activity_item.xml  ──build──>  ro.ase.ie.g1097.databinding.ActivityItemBinding
```

Clasa generată, simplificată la ce folosești:

```java
public final class ActivityMainBinding {
    public final LinearLayout main;
    public final Button button;
    public final Switch switch1;
    public final EditText editTextText;
    // ... câte un câmp pentru fiecare android:id din layout

    public static ActivityMainBinding inflate(LayoutInflater inflater) { ... }
    public LinearLayout getRoot() { ... }   // rădăcina layout-ului, cu tipul din XML
}
```

Ciclul de viață al unui binding într-o activitate:

```
1. binding = ActivityMainBinding.inflate(getLayoutInflater());
      -> LayoutInflater citește XML-ul
      -> construiește arborele
      -> umple câmpurile cu findViewById, O SINGURĂ DATĂ, în cod generat

2. setContentView(binding.getRoot());
      -> arborele construit devine conținutul ferestrei

3. binding.button.setOnClickListener(...)
      -> acces direct la câmp, fără căutare, fără cast, fără null
```

Diferența față de `findViewById` nu este „mai puțin cod" — deși și asta. Este că **`binding.buton` nu compilează dacă butonul nu există**. Greșeala se mută din runtime în compilare, iar asta e întotdeauna o îmbunătățire.

**Ce se rupe fără el**

- **Fără `buildFeatures { viewBinding = true }`**: `Cannot resolve symbol 'ActivityMainBinding'`. Clasa nu există, pentru că nu a fost generată. Nu e o problemă de import — e o problemă de configurare.
- **Binding-ul layout-ului greșit**: `ActivityItemBinding.inflate(...)` într-o activitate care trebuia să încarce `activity_main.xml` compilează, dar afișează alt ecran. Nu primești eroare, pentru că ambele clase există.
- **Un view fără `android:id`**: nu apare în binding. Nu poți ajunge la el din cod — ceea ce e corect, dar surprinde când ai uitat ID-ul.
- **`binding` folosit după `onDestroy`**: nu aruncă nimic, pentru că binding-ul e doar un obiect Java care ține referințe la view-uri. Problema e memoria: dacă ții binding-ul într-un câmp `static`, ții tot arborele în viață.

**Unde îl vezi în G1097**

**G1097 are `viewBinding = true` în `build.gradle.kts`, dar nu îl folosește.** `ItemActivity.initControls()` face 13 `findViewById`, iar `MainActivity.initControls()` două — plus câte unul în `onCreate`, pentru `R.id.main` în listener-ul de insets. Este o alegere didactică: la test ți se poate cere fie să explici de ce nu e folosit, fie să migrezi.

```kotlin
// cod-final/build.gradle.kts — flagul există
android {
    namespace = "ro.ase.ie.g1097"
    buildFeatures { viewBinding = true }
}
```

Contrastul e în `DMA05`, care îl folosește complet:

```java
import ro.ase.ie.dma05.databinding.ActivityMainBinding;

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

        binding.button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Button clicked", Toast.LENGTH_SHORT).show();
            }
        });

        binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
            Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
        });
```

Observă cele trei diferențe față de G1097: nu există `initControls()`, nu există niciun `findViewById`, iar `binding.getRoot()` înlocuiește `findViewById(R.id.main)` în listener-ul de insets.

**Confuzia tipică**

„ViewBinding este DataBinding." Nu. DataBinding este un sistem mult mai greu: permite expresii în XML (`android:text="@{movie.title}"`), variabile, observare de date. ViewBinding este doar **generarea de referințe tipate**. În practică, ViewBinding e suficient pentru 95% din cazuri și nu are costul de build al DataBinding.

A doua: „ViewBinding înlocuiește layout-ul". Nu. XML-ul rămâne exact la fel; se generează doar o clasă Java care îl înfășoară. `activity_item.xml` nu se schimbă cu nimic dacă activezi ViewBinding.

A treia: „ViewBinding face `findViewById` intern, deci e la fel de fragil". Face `findViewById` intern, dar **o singură dată**, în cod generat, cu ID-urile citite din același XML. Fragilitatea dispare pentru că generatorul și XML-ul sunt sincronizate la build, nu pentru că mecanismul de căutare ar fi altul.

A patra, importantă la examen: „dacă am `viewBinding = true`, trebuie să îl folosesc". Nu. Flagul doar generează clasele; `findViewById` continuă să funcționeze. G1097 este dovada: flagul e activ, codul folosește `findViewById`.

---

## Conceptul 37.10 — Activity: ce este și cine o creează

**Ce este**

O `Activity` este un **ecran cu ciclu de viață**, declarat în manifest, pornit de un `Intent` și găzduit de o fereastră. Nu este un obiect pe care îl construiești tu: sistemul o instanțiază prin reflecție, îi cheamă metodele în ordine și o distruge când nu mai e nevoie. `MainActivity` și `ItemActivity` sunt cele două activități ale lui G1097.

**De ce există**

Pentru că un ecran trebuie să aibă un **punct de intrare pe care sistemul îl cunoaște**. Dacă ai construi ecranele cu `new`, sistemul nu ar ști când să le dea memorie, când să le ia, cum să le salveze starea la rotire sau cum să le readucă după ce procesul a fost omorât. `Activity` este contractul: tu spui ce să faci în `onCreate`, sistemul decide **când** să o facă.

**Cum funcționează**

Lanțul complet, de la `launcher.launch(intent)` până la primul `onResume`:

```
MainActivity: launcher.launch(intent)
    |
    v
system_server: ActivityTaskManager
    |-- rezolvă Intent-ul în ItemActivity (din manifest)
    |-- verifică exported, permisiuni
    |-- procesul există deja (G1097 rulează) -> refolosește
    |
    v
ActivityThread (firul principal al aplicației)
    |-- Instrumentation.newActivity(ItemActivity.class)
    |     -> reflecție: constructor FĂRĂ parametri
    |     -> dacă lipsește: InstantiationException
    |-- activity.attach(context, window, ...)
    |     -> primește fereastra, resursele, tema
    |-- activity.onCreate(savedInstanceState)
    |     -> setContentView -> arborele de view-uri
    |-- activity.onStart()
    |-- activity.onResume()
    |-- fereastra devine vizibilă -> measure -> layout -> draw
```

Trei consecințe care se cer la test:

1. **Constructorul trebuie să fie fără parametri.** Sistemul nu are ce argumente să îți dea. De aceea `MainActivity` și `ItemActivity` nu au niciun constructor scris — compilatorul le dă pe cel implicit.
2. **`onCreate` nu este constructorul.** Constructorul creează obiectul gol; `onCreate` primește `Bundle`-ul cu starea salvată și fereastra deja atașată. Orice inițializare care atinge UI-ul trebuie să stea în `onCreate`.
3. **O activitate nu se creează cu `new`.** `new MainActivity()` compilează, dar obiectul rezultat nu are fereastră, nu are resurse atașate, nu are ciclu de viață. Orice `setContentView` pe el aruncă.

**Ce se rupe fără el**

- **`new MainActivity()`**: compilează, dar primul acces la `getWindow()` sau `getResources()` aruncă `NullPointerException`. Nu există avertisment de compilare — de aceea e o capcană.
- **Activitate nedeclarată în manifest**: `ActivityNotFoundException` la `launch`, cu mesajul care îți spune exact ce lipsește (vezi 37.4).
- **Clasă `static` sau `private`**: `InstantiationException: can't instantiate class ...; no empty constructor`. O activitate trebuie să fie `public` și să aibă constructor public fără parametri.
- **Muncă grea în `onCreate`**: ecranul apare alb sau înghețat, pentru că `onCreate` rulează pe firul principal, iar desenarea așteaptă să se termine.

**Unde îl vezi în G1097**

Cele două activități, cu tot ce le trebuie ca să fie activități:

```java
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ...
    }
}

public class ItemActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_item);
        ...
    }
}
```

Pornirea, din `MainActivity.initListeners()`:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        launcher.launch(intent);
    }
});
```

`MainActivity.this` este `Context`-ul necesar pentru `Intent`; `ItemActivity.class` este **componenta** — un obiect `Class`, nu o instanță. Nicăieri în G1097 nu apare `new ItemActivity()`.

**Confuzia tipică**

„Activitatea este aplicația." Nu — este un ecran. Aplicația poate avea zeci; G1097 are două. Vezi 37.1 pentru diferență.

A doua: „creez activitatea cu `new`". Nu. O creează sistemul, prin reflecție, când un `Intent` o cere. Tu ceri **pornirea**, nu construiești obiectul.

A treia: „`onCreate` este constructorul". Nu. Constructorul creează obiectul; `onCreate` este primul callback al ciclului de viață, cu `Bundle`-ul de stare și cu fereastra deja pregătită. Diferența practică: în constructor nu ai `Context` complet atașat, deci nu poți apela `getResources()` sau `setContentView`.

A patra: „o activitate poate fi distrusă oricând, deci `onDestroy` e garantat". Nu. La rotire, da. La apăsarea Back, da. Când sistemul omoară procesul pentru memorie, **nu** — `onDestroy` nu rulează, iar `onSaveInstanceState` a rulat deja înainte. Vezi 37.11 și 37.12.

---

## Conceptul 37.11 — Ciclul de viață

**Ce este**

Ciclul de viață este **șirul de metode pe care sistemul le cheamă pe o activitate** de la creare până la distrugere: `onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`, plus `onRestart` la revenire. Fiecare metodă corespunde unei stări în care activitatea poate sau nu să fie vizibilă, să aibă focus, să primească input.

**De ce există**

Pentru că sistemul are nevoie să **ia memorie** de la aplicațiile care nu sunt folosite, iar tu ai nevoie să **eliberezi resurse** (cameră, senzori, animații, listeneri) exact atunci când ecranul nu mai e relevant. Fără un ciclu de viață ai avea două variante: să ții totul pornit (baterie și memorie pierdute) sau să ghicești singur când ecranul e vizibil (imposibil — doar sistemul știe cine are focus). Ciclul de viață este contractul prin care sistemul îți spune ce se întâmplă, iar tu decizi ce faci.

**Cum funcționează**

Stările și tranzițiile:

```
                     onCreate()
                        |
                        v
                    [CREATED]
                        |  onStart()
                        v
                    [STARTED]  <----------- onRestart() <-----+
                        |  onResume()                          |
                        v                                      |
                    [RESUMED]  <- activitatea are focus        |
                        |                                      |
        +---------------+----------------+                     |
        |               |                |                     |
   utilizatorul    altă aplicație    apasă Home          revine în prim-plan
   apasă Back      în prim-plan      sau ecran stins      (din onStop)
        |               |                |                     |
        v               v                v                     |
     onPause()      onPause()        onPause()                 |
        |               |                |                     |
     onStop()        onStop()         onStop() ---------------+
        |               |                |
     onDestroy()    (procesul poate fi omorât oricând, fără onDestroy)
```

Ordinea la **rotire** — cea care produce cele mai multe bug-uri:

```
onPause -> onStop -> onSaveInstanceState -> onDestroy
   -> onCreate(savedInstanceState != null) -> onStart -> onResume
```

Ordinea la **apăsarea Back**:

```
onPause -> onStop -> onDestroy          (fără recreare)
```

Ce pui în fiecare metodă, și de ce:

| Metodă | Ce faci | De ce acolo |
|---|---|---|
| `onCreate` | `setContentView`, `findViewById`, inițializări de structură | rulează o dată per instanță |
| `onStart` | înregistrezi listeneri de sistem (senzori, broadcast) | activitatea devine vizibilă |
| `onResume` | pornești animații, camera, actualizezi datele afișate | activitatea are focus |
| `onPause` | oprești animații, salvezi rapid ce se poate pierde | urmează să pierzi focus-ul |
| `onStop` | eliberezi resurse grele, deregistrezi listeneri | nu mai e vizibilă |
| `onDestroy` | anulezi callback-uri, oprești thread-uri | instanța moare definitiv |

**Ce se rupe fără el**

- **Listener înregistrat în `onResume` fără deregistrare în `onPause`**: după fiecare revenire ai încă unul. Simptomul e un eveniment care se procesează de 3 ori după 3 reveniri — fără nicio eroare.
- **Camera ținută în `onStart` fără eliberare în `onStop`**: altă aplicație nu poate deschide camera, iar pe unele dispozitive aplicația ta crapă la `open()`.
- **Muncă în `onCreate` care trebuia în `onResume`**: datele afișate rămân cele de la creare, pentru că la revenire `onCreate` **nu** rulează din nou.
- **Socoteală pe `onDestroy`**: la omorârea procesului de către sistem, `onDestroy` nu rulează. Orice salvare pusă acolo se pierde exact în cazul în care conta.

**Unde îl vezi în G1097**

G1097 suprascrie **doar `onCreate`**, în ambele activități. Nu are `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`, `onSaveInstanceState`. Este suficient pentru o aplicație didactică, dar înseamnă și că nu ai unde să vezi ciclul în acțiune.

`DMA02` îl arată complet — `MainActivity` suprascrie toate cele șase metode, fiecare cu un `Log`:

```java
@Override protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    Log.w(TAG, "onCreate");
}

@Override protected void onStart()   { super.onStart();   Log.w(TAG, "onStart"); }
@Override protected void onResume()  { super.onResume();  Log.w(TAG, "onResume"); }
@Override protected void onPause()   { super.onPause();   Log.w(TAG, "onPause"); }
@Override protected void onStop()    { super.onStop();    Log.w(TAG, "onStop"); }
@Override protected void onDestroy() { super.onDestroy(); Log.w(TAG, "onDestroy"); }
```

Iar `DMA02App` vede **aceleași tranziții din exterior**, prin `Application.ActivityLifecycleCallbacks`:

```java
public class DMA02App extends Application implements Application.ActivityLifecycleCallbacks {

    @Override
    public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
        DynamicColors.applyToActivitiesIfAvailable(this);
        Log.w(TAG, "onCreate");
    }

    @Override
    public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
        Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());
    }
    // ... onActivityStarted, onActivityResumed, onActivityPaused,
    //     onActivityStopped, onActivitySaveInstanceState, onActivityDestroyed
}
```

Diferența dintre cele două surse de log este exact ce trebuie să reții: metodele activității sunt chemate **pe activitate**, iar callback-urile din `Application` sunt chemate **pe aplicație, pentru orice activitate**. Al doilea mod îți permite să vezi ciclul fără să modifici activitatea — și e felul în care îl poți demonstra la test.

**Confuzia tipică**

„`onDestroy` rulează mereu." Nu. Rulează când activitatea este distrusă **intenționat** (Back, `finish()`, rotire, `configChanges`). Când sistemul omoară procesul pentru memorie, `onDestroy` nu rulează — procesul dispare. De aceea salvarea nu se pune în `onDestroy`.

A doua: „`onPause` înseamnă că activitatea e terminată". Nu. `onPause` înseamnă că a pierdut focus-ul — poate fi acoperită parțial de un dialog sau de altă activitate. Poate reveni direct în `onResume`, fără `onStop`.

A treia: „`onCreate` rulează la fiecare revenire". Nu. Rulează o dată per instanță. La revenirea din Home rulează `onRestart` → `onStart` → `onResume`. Dacă vrei să reîmprospătezi datele la fiecare revenire, locul este `onResume`.

A patra: „`onStart` și `onResume` sunt aproape identice". Nu. `onStart` = vizibilă; `onResume` = vizibilă **și** cu focus, adică primește input. Între ele poate exista un dialog care acoperă activitatea: `onPause` fără `onStop`.

---

## Conceptul 37.12 — Starea: onSaveInstanceState vs SharedPreferences

**Ce este**

Sunt **două mecanisme diferite** pentru a nu pierde date, cu durate de viață diferite. `onSaveInstanceState(Bundle)` salvează stare **efemeră** într-un `Bundle` ținut de sistem în memorie: supraviețuiește rotirii și recreării activității, dar nu supraviețuiește închiderii aplicației. `SharedPreferences` salvează date **durabile** într-un fișier XML din directorul privat al aplicației: supraviețuiește opririi, repornirii și actualizării, dar nu dezinstalării.

**De ce există**

Pentru că sunt două probleme diferite, care se confundă constant. Prima: „utilizatorul a rotit telefonul și a pierdut ce tastase" — o problemă de **configurație**, rezolvată cu `Bundle`. A doua: „utilizatorul vrea să regăsească filmele după ce închide aplicația" — o problemă de **persistență**, rezolvată cu fișier, bază de date sau `SharedPreferences`. Un singur mecanism nu le poate rezolva pe amândouă: `Bundle`-ul e prea efemer pentru persistență, iar fișierul e prea scump pentru o valoare care trăiește 2 secunde.

**Cum funcționează**

Cele două durate de viață, pe aceeași axă:

```
                    rotire          Home            omorâre proces      repornire
                       |              |                    |                |
Bundle:            supraviețuiește    da (dacă task-ul   NU               NU
                   (recreare)         e restaurat)
                       |              |                    |                |
SharedPreferences: supraviețuiește  supraviețuiește   supraviețuiește  supraviețuiește
```

Mecanismul `Bundle`-ului:

```
1. Utilizatorul rotește telefonul
2. Sistemul: onPause -> onStop -> onSaveInstanceState(outState)
      -> activitatea ta pune în outState ce vrea să păstreze
3. onDestroy
4. Sistemul creează o instanță NOUĂ a aceleiași clase
5. onCreate(savedInstanceState)   <- bundle-ul de la pasul 2
      -> citești din el și repui starea în widget-uri
```

Forma canonică, pe care o știi din capitolul 21:

```java
@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putString("title", etTitle.getText().toString());
    outState.putInt("duration", sbDuration.getProgress());
}

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_item);
    initControls();
    if (savedInstanceState != null) {
        etTitle.setText(savedInstanceState.getString("title"));
        sbDuration.setProgress(savedInstanceState.getInt("duration"));
    }
}
```

Mecanismul `SharedPreferences`-ului, în schimb, nu are legătură cu ciclul de viață: scrii când vrei, citești când vrei, iar fișierul stă în `/data/data/ro.ase.ie.g1097/shared_prefs/`. Nu se șterge la rotire, nu se șterge la Home, nu se șterge la repornire.

Criteriul de alegere, într-un tabel:

| Întrebare | `Bundle` | `SharedPreferences` |
|---|---|---|
| Trebuie să supraviețuiască rotirii? | da | da (dar e exagerat) |
| Trebuie să supraviețuiască închiderii aplicației? | **nu** | da |
| Cât de mari sunt datele? | mici (KB) | mici (KB) — nu pentru liste mari |
| Ce fel de date? | orice e `Serializable`/`Parcelable` | primitive, `String`, `Set<String>` |
| Cine o șterge? | sistemul, la distrugere | utilizatorul, la dezinstalare/clear data |

**Ce se rupe fără el**

- **Fără `onSaveInstanceState`**: la rotire, formularul se golește. Exact asta se întâmplă în G1097 — vezi mai jos. Simptomul e spectaculos: completezi cinci câmpuri, rotești telefonul, totul dispare.
- **Fără verificarea `savedInstanceState != null`**: la prima creare bundle-ul este `null`, iar `savedInstanceState.getString(...)` aruncă `NullPointerException` în `onCreate`. Aplicația crapă la prima pornire, nu la rotire.
- **Un obiect care nu e `Serializable` pus în `Bundle`**: `RuntimeException: Parcelable encountered IOException writing serializable object`. Se întâmplă la runtime, nu la compilare.
- **`SharedPreferences` folosit pentru stare de UI**: la fiecare rotire scrii pe disc, iar la următoarea pornire aplicația „ține minte" un formular pe care utilizatorul îl abandonase. Comportament greșit, fără eroare.
- **`SharedPreferences` pentru liste mari**: fișierul se citește integral în memorie la prima accesare. Pentru 10.000 de filme ai nevoie de o bază de date, nu de preferințe.

**Unde îl vezi în G1097**

**G1097 nu suprascrie `onSaveInstanceState`.** Parametrul `savedInstanceState` există în semnătura ambelor `onCreate`, dar nu este citit nicăieri:

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);   // savedInstanceState este ignorat
    EdgeToEdge.enable(this);
    setContentView(R.layout.activity_item);
    ...
}
```

Consecința, verificabilă pe emulator: completezi formularul în `ItemActivity`, rotești telefonul, iar toate cele zece valori introduse se pierd. `releaseCal` revine la `Calendar.getInstance()`, spinner-ul revine la „Drama", rating-ul la 0, iar `swWatched` și `cbonWatchList` revin la `false`. Este un **gol real** al codului, nu o alegere — și un exercițiu probabil la test.

Al doilea gol: `MainActivity` ține lista în `private final List<Movie> movies = new ArrayList<>();` și o umple cu `addSampleMovies()` la fiecare `onCreate`. La rotire, lista se reconstruiește de la cele trei filme de start, iar filmele adăugate de utilizator dispar. Aici `Bundle`-ul ar fi potrivit, pentru că `Movie implements Serializable` — deci `outState.putSerializable("movies", new ArrayList<>(movies))` ar funcționa.

`SharedPreferences` **nu apare deloc în G1097**. Apare în capitolul 35 ca rețetă și este mecanismul corect pentru „filmele să rămână după închiderea aplicației" — o cerință pe care G1097 nu o are.

**Confuzia tipică**

„`SharedPreferences` este pentru stare." Nu — este pentru **preferințe durabile**: ultimul mod de sortare, tema aleasă, dacă tutorialul a fost văzut. Starea unui formular netrimis nu e o preferință; e ceva ce trebuie să dispară când utilizatorul închide ecranul.

A doua: „`Bundle`-ul supraviețuiește repornirii aplicației". Nu. Trăiește cât **task-ul** din recents, în memoria sistemului. Dacă utilizatorul închide aplicația din recents, bundle-ul dispare.

A treia: „dacă salvez în `onSaveInstanceState`, nu mai am nevoie de nimic". Ai nevoie, pentru că `onSaveInstanceState` **nu** se apelează când utilizatorul apasă Back sau când apeși tu `finish()`. În acele cazuri activitatea moare definitiv și starea se pierde intenționat.

A patra: „pot pune orice obiect în `Bundle`". Doar `Serializable`, `Parcelable` și primitive. Un `Context`, un `Drawable`, un `View` nu sunt — iar eroarea apare la runtime, când bundle-ul este scris, nu când îl construiești. Vezi 37.16 și 37.22.

---
## Conceptul 37.13 — Application

**Ce este**

`Application` este clasa care reprezintă **aplicația ca întreg, în timpul unei rulări**. Există o singură instanță per proces, este creată de sistem **înaintea oricărei activități** și trăiește până când procesul moare. Dacă vrei o clasă proprie, o scrii și o declari în manifest cu `android:name=".NumeleClasei"`; altfel Android folosește clasa implicită `android.app.Application`.

**De ce există**

Pentru că există inițializări care trebuie făcute **o singură dată per proces**, nu o dată per ecran: configurarea unei librării de logging, înregistrarea unui handler de crash-uri, inițializarea unei baze de date, aplicarea culorilor dinamice. Dacă le-ai pune în `onCreate`-ul fiecărei activități, s-ar executa de N ori, iar la rotire s-ar executa din nou. `Application` este singurul loc din aplicație despre care sistemul garantează că rulează exact o dată, înainte de orice altceva.

**Cum funcționează**

```
1. Sistemul pornește procesul (fork din Zygote)
2. ActivityThread.main()
3. ActivityThread găsește clasa declarată în manifest:
      <application android:name=".DMA02App">
4. Instrumentation.newApplication(DMA02App.class, context)
      -> reflecție: constructor fără parametri
5. application.attachBaseContext(context)
6. application.onCreate()          <-- aici îți faci inițializările
7. abia acum se creează prima activitate: onCreate -> onStart -> onResume
```

Ordinea este garantată și este motivul pentru care `Application` funcționează ca loc de inițializare: nu există nicio cale prin care o activitate să ruleze înainte de `Application.onCreate()`.

Ce poți face în `Application` și ce nu:

| Poți | Nu poți (sau nu ar trebui) |
|---|---|
| inițializezi librării, logger, crash handler | afișa un dialog (nu ai fereastră) |
| înregistrezi `ActivityLifecycleCallbacks` | presupune că există o activitate curentă |
| aplici tema / culorile dinamice | face muncă grea (blochezi pornirea) |
| ții stare globală per proces | ții stare per utilizator (nu ai UI) |

**Ce se rupe fără el**

- **Fără `android:name` în manifest**: clasa ta nu este instanțiată niciodată. Nu primești eroare — `Application.onCreate()` pur și simplu nu rulează, iar inițializările tale lipsesc. Simptomul e o librărie care „nu funcționează" fără niciun mesaj.
- **Muncă grea în `Application.onCreate()`**: fiecare pornire a aplicației așteaptă. Ecranul alb de la lansare devine mai lung, iar pe dispozitive lente poți ajunge la ANR („Application Not Responding").
- **Stare mutabilă ținută în `Application`**: funcționează cât timp procesul trăiește, dar dispare când sistemul îl omoară. Dacă o folosești ca „bază de date în memorie", utilizatorul pierde date fără să închidă aplicația.
- **Presupunerea că `Application` e unică în lume**: este unică **per proces**. Dacă aplicația rulează în două procese, ai două instanțe `Application`, fiecare cu starea ei.

**Unde îl vezi în G1097**

**G1097 nu are clasă `Application`.** Manifestul nu conține `android:name` pe `<application>`, deci rulează `android.app.Application` implicit, care nu face nimic în plus. Este o absență deliberată de simplitate: aplicația nu are nevoie de inițializări globale.

`DMA02` o are, și o folosește pentru două lucruri simultan — tema dinamică și observarea ciclului de viață:

```java
public class DMA02App
        extends Application
        implements Application.ActivityLifecycleCallbacks {

    private final String TAG = DMA02App.class.getSimpleName();

    @Override
    public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
        DynamicColors.applyToActivitiesIfAvailable(this);

        Log.w(TAG, "onCreate");
    }
```

Declararea în manifest, singura linie care face diferența:

```xml
<application
    android:name=".DMA02App"
    android:label="@string/app_name"
    android:theme="@style/Theme.DMA02">
```

`registerActivityLifecycleCallbacks(this)` este partea cea mai utilă la examen: din `Application` poți primi toate cele șapte callback-uri de ciclu de viață **pentru orice activitate**, fără să modifici vreo activitate. `DMA02App` le implementează pe toate, iar `onActivitySaveInstanceState` este lăsat gol — un detaliu care arată că interfața cere toate metodele, chiar dacă nu le folosești.

`DynamicColors.applyToActivitiesIfAvailable(this)` este un exemplu perfect de inițializare globală: aplică paleta Material You tuturor activităților, o singură dată, dintr-un singur loc. Făcută în fiecare activitate, ar fi cod duplicat.

**Confuzia tipică**

„`Application` este un singleton global pe care îl pot folosi oriunde." Este un singleton **per proces**, nu per aplicație-instalată. Și nu este un loc bun pentru date de business: dacă procesul moare, datele dispar. Pentru date care trebuie să rămână, ai nevoie de fișier, `SharedPreferences` sau bază de date.

A doua: „`Application.onCreate()` rulează la fiecare activitate". Nu — rulează o singură dată, la pornirea procesului. Când revii în aplicație după Home, dacă procesul a supraviețuit, `Application.onCreate()` **nu** rulează din nou.

A treia: „dacă am `Application`, pot renunța la `Context` în activități". Nu. `Application` este un `Context`, dar fără temă și fără fereastră (vezi 37.2). Widget-urile au nevoie de contextul activității.

A patra: „`Application` este locul pentru `SharedPreferences`". Poate fi — dar nu pentru că e `Application`. `SharedPreferences` se obține din orice `Context`, iar fișierul e același. Diferența e doar cine ține referința.

---

## Conceptul 37.14 — Listeneri: ce sunt și cine îi apelează

**Ce este**

Un listener este **un obiect care implementează o interfață pe care widget-ul o cunoaște**, iar widget-ul îl apelează când se întâmplă ceva. `View.OnClickListener` are o singură metodă, `onClick(View)`. Tu îi dai un obiect care o implementează prin `setOnClickListener(...)`, iar widget-ul îl ține într-un câmp și îl apelează când utilizatorul atinge view-ul.

**De ce există**

Pentru că widget-ul nu poate ști ce vrei să faci. Un `Button` știe să se deseneze și să detecteze atingerea, dar nu știe că în aplicația ta înseamnă „deschide formularul". Fără listeneri ai avea două variante, ambele rele: să extinzi `Button` pentru fiecare buton (o clasă per comportament) sau să verifici periodic dacă a fost apăsat (polling, imposibil de făcut corect). Listenerul este **inversarea controlului**: nu tu întrebi widget-ul, widget-ul te anunță pe tine.

**Cum funcționează**

Lanțul complet, de la deget până la codul tău:

```
1. Degetul atinge ecranul
2. Kernel -> InputDispatcher -> aplicația ta
3. ViewRootImpl.dispatchInputEvent()
4. DecorView.dispatchTouchEvent()      <- coboară în arbore
5. fiecare ViewGroup decide cărui copil îi pasă (hit test pe coordonate)
6. Button.dispatchTouchEvent()
7. Button.onTouchEvent(MotionEvent)
      -> ACTION_DOWN: se marchează „pressed", se redesenează
      -> ACTION_UP:   dacă degetul e încă pe buton -> performClick()
8. View.performClick()
      -> dacă mOnClickListener != null -> mOnClickListener.onClick(this)
9. codul tău rulează, PE FIRUL PRINCIPAL
```

Trei lucruri care se deduc din lanț:

1. **Listenerul rulează pe firul principal (UI thread).** Orice operație lungă în `onClick` blochează desenarea. De aici vine regula: în listener nu faci I/O, nu dormi, nu aștepți rețea.
2. **`setOnClickListener` stochează referința, nu o copiază.** Un singur listener per widget pentru un anumit tip de eveniment — dacă îl setezi de două ori, al doilea îl înlocuiește pe primul, fără warning.
3. **Listenerul se apelează doar dacă view-ul e `clickable`.** `setOnClickListener` face view-ul clickable automat; dacă îl scoți din `clickable`, listener-ul rămâne setat dar nu se mai apelează.

Cele șase tipuri de listeneri din G1097, cu ce primește fiecare:

| Metodă de setare | Interfață | Metode | Ce primești |
|---|---|---|---|
| `setOnClickListener` | `View.OnClickListener` | 1 | `View v` |
| `setOnItemClickListener` | `AdapterView.OnItemClickListener` | 1 | `parent, view, position, id` |
| `setOnCheckedChangeListener` | `CompoundButton.OnCheckedChangeListener` | 1 | `buttonView, isChecked` |
| `setOnSeekBarChangeListener` | `SeekBar.OnSeekBarChangeListener` | **3** | vezi mai jos |
| `setOnDateSetListener` | `DatePickerDialog.OnDateSetListener` | 1 | `view, year, month, day` |
| `setOnApplyWindowInsetsListener` | `androidx.core.view.OnApplyWindowInsetsListener` | 1 | `v, insets` |

**Ce se rupe fără el**

- **Listener nesetat**: butonul se apasă, se animă (ripple), dar nu se întâmplă nimic. Zero erori, zero log-uri. Cel mai greu de depanat simptom, pentru că totul pare în regulă.
- **Listener setat pe view-ul greșit**: apeși butonul, se întâmplă acțiunea altui buton. Se întâmplă când copiezi un bloc de cod și uiți să schimbi variabila.
- **`NullPointerException` în listener**: un câmp folosit în `onClick` este `null`, de obicei pentru că listener-ul a fost setat înainte ca acel câmp să fie inițializat. Exact aceasta este capcana din G1097 cu `launcher` (vezi mai jos).
- **Muncă grea în listener**: interfața îngheață la apăsare. Nu crapă, doar nu răspunde — iar utilizatorul apasă din nou, de trei ori.

**Unde îl vezi în G1097**

`MainActivity.initListeners()` — doi listeneri, amândoi folosesc `launcher`, care este inițializat **după** această metodă:

```java
private void initListeners() {
    fabInsert.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            launcher.launch(intent);      // launcher este încă null ÎN ACEST MOMENT
        }
    });

    listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
        @Override
        public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            intent.putExtra(MOVIE_EXTRA, movies.get(position));
            intent.putExtra(POSITION_EXTRA, position);
            launcher.launch(intent);
        }
    });
}
```

Ordinea din `onCreate` este:

```java
initControls();                                    // 1
initListeners();                                   // 2  <- listenerii sunt SETAȚI aici
launcher = registerForActivityResult(...);         // 3  <- launcher devine non-null aici
```

Aici nu se rupe nimic, și merită înțeles de ce: la pasul 2 nu se apelează `onClick`, doar se **stochează** un obiect. `onClick` rulează abia când utilizatorul atinge butonul, mult după ce `onCreate` s-a terminat. Dacă ai muta `launcher.launch(intent)` în afara lui `onClick` — de exemplu direct în `initListeners()` — ai avea `NullPointerException`.

`ItemActivity.initListeners()` — patru listeneri, inclusiv unul cu **trei** metode:

```java
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveMovie();
    }
});

swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});

sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) { }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) { }
});
```

`onProgressChanged` este apelat **și** când schimbi progresul din cod (`setProgress`), nu doar la atingere. Parametrul `fromUser` spune care dintre cazuri e — G1097 îl ignoră intenționat, pentru că eticheta trebuie să reflecte valoarea în ambele situații. Dacă l-ai filtra cu `if (fromUser)`, `fillForm` ar seta progresul fără să actualizeze eticheta, iar la editare ai vedea „0 min" pentru un film de 148 de minute.

**Confuzia tipică**

„Listenerul rulează pe alt fir, deci pot face ce vreau în el." Nu. Rulează pe firul principal. Pentru operații lungi ai nevoie de un fir secundar, iar rezultatul îl revii pe firul principal.

A doua: „`setOnClickListener` întoarce ceva". Nu, întoarce `void`. Nu poți înlănțui apeluri și nu poți verifica dacă s-a setat.

A treia: „dacă setez doi listeneri, se apelează amândoi". Nu. Al doilea îl înlocuiește pe primul, pentru că widget-ul ține **o singură** referință. Dacă ai nevoie de două comportamente, le pui în aceeași metodă.

A patra: „listenerul este apelat când se schimbă valoarea din cod". Depinde de widget. `SeekBar.onProgressChanged` **da** (de aceea `fromUser`); `CompoundButton.onCheckedChanged` **da**; `RadioGroup.onCheckedChanged` **da**. Dar `ListView.onItemClick` nu — acela e doar pentru atingere. Regula generală: dacă metoda se numește `onXChanged`, se apelează și la schimbarea programatică; dacă se numește `onXClick`, doar la interacțiune.

---

## Conceptul 37.15 — Lambda și interfețe funcționale

**Ce este**

O **interfață funcțională** este o interfață cu **exact o metodă abstractă**. O **lambda** este o formă scurtă de a scrie implementarea acelei metode, fără clasă, fără nume, fără `new`. `(a, b) -> a + b` este echivalentul lui `new FunctionalInterface() { public int apply(int a, int b) { return a + b; } }`, doar că fără tot ambalajul.

**De ce există**

Pentru că un listener cu o singură metodă cere șase linii de ceremonial pentru o singură expresie. În `MainActivity`:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        launcher.launch(intent);
    }
});
```

șase linii, dintre care **una** contează. Lambda reduce la:

```java
fabInsert.setOnClickListener(v -> launcher.launch(intent));
```

Câștigul nu e estetic. Câștigul e că **intenția devine vizibilă**: vezi dintr-o privire ce se întâmplă la click, fără să citești prin tipuri și adnotări.

**Cum funcționează**

Regula este mecanică: **o singură metodă abstractă = lambda permisă**. Două sau mai multe = clasă anonimă obligatorie.

| Interfață | Metode abstracte | Lambda? |
|---|---|---|
| `View.OnClickListener` | 1 (`onClick`) | **da** |
| `AdapterView.OnItemClickListener` | 1 (`onItemClick`) | **da** |
| `CompoundButton.OnCheckedChangeListener` | 1 (`onCheckedChanged`) | **da** |
| `View.OnLongClickListener` | 1 (`onLongClick`) | **da** |
| `SeekBar.OnSeekBarChangeListener` | **3** | **nu** |
| `TextWatcher` | **3** | **nu** |
| `androidx.core.view.OnApplyWindowInsetsListener` | 1 (`onApplyWindowInsets`) | **da** |

Sintaxa, pe cele trei forme pe care le vei folosi:

```java
// 1. un parametru, o expresie
view.setOnClickListener(v -> doSomething());

// 2. un parametru, bloc (cu acolade, dacă ai nevoie de mai multe instrucțiuni)
view.setOnClickListener(v -> {
    Intent intent = new Intent(this, ItemActivity.class);
    launcher.launch(intent);
});

// 3. doi parametri
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

Trei reguli care produc erori de compilare dacă le încalci:

1. **Parametrii se pot scurta, nu lungi.** Poți scrie `v ->` în loc de `(View v) ->`, dar nu poți adăuga parametri pe care interfața nu îi are.
2. **Variabilele locale capturate trebuie să fie efectiv finale.** Nu le poți modifica în lambda. Un câmp al clasei, în schimb, se poate — pentru că nu e capturat prin valoare, ci prin `this`.
3. **`this` într-o lambda este instanța exterioară.** Într-o clasă anonimă, `this` este clasa anonimă. Diferența e crucială în G1097.

**Ce se rupe fără el**

- **Lambda pe o interfață cu trei metode**: `SeekBar.OnSeekBarChangeListener is not a functional interface` — eroare de compilare, mesaj clar. Nu poți „rezolva" cu lambda; trebuie clasă anonimă.
- **Modificarea unei variabile locale în lambda**: `Variable used in lambda expression should be final or effectively final`. Se întâmplă când încerci să acumulezi un total într-un `for`.
- **`this` greșit**: într-o lambda, `this` este activitatea — deci `Toast.makeText(this, ...)` funcționează. Într-o clasă anonimă, `this` este listener-ul — deci ai nevoie de `MainActivity.this`. Confuzia produce erori de compilare greu de citit („cannot be converted to Context").
- **Captura unui câmp care se schimbă**: lambda vede valoarea **la momentul execuției**, nu la momentul creării, pentru câmpuri. Pentru variabile locale, vede valoarea de la creare. Două comportamente diferite, aceeași sintaxă.

**Unde îl vezi în G1097**

G1097 folosește **o singură lambda**, în ambele activități, și este cea mai interesantă din tot codul:

```java
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
    return insets;
});
```

De ce aici și nu în altă parte: `OnApplyWindowInsetsListener` are **o singură** metodă (`onApplyWindowInsets`), deci lambda e permisă. Restul listenerilor din G1097 sunt scrise ca **clase anonime**, deși majoritatea ar fi putut fi lambda:

```java
// G1097 — clasă anonimă (6 linii pentru o instrucțiune)
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});

// echivalent lambda (2 linii)
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

Singurul care **nu** poate fi lambda este `SeekBar.OnSeekBarChangeListener`, pentru că are trei metode — și exact așa apare în cod, cu două metode goale:

```java
sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }
    @Override public void onStartTrackingTouch(SeekBar seekBar) { }
    @Override public void onStopTrackingTouch(SeekBar seekBar) { }
});
```

`DMA05` arată contrastul — aceleași widget-uri, scrise cu lambda:

```java
binding.switch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
    Toast.makeText(MainActivity.this, "Switch clicked to " + isChecked, Toast.LENGTH_SHORT).show();
});

binding.checkBox.setOnCheckedChangeListener((buttonView, isChecked) -> {
    Toast.makeText(MainActivity.this, "CheckBox clicked to " + isChecked, Toast.LENGTH_SHORT).show();
});

binding.ratingBar.setOnRatingBarChangeListener((ratingBar, rating, fromUser) -> {
    Toast.makeText(MainActivity.this, "Rating changed to " + rating, Toast.LENGTH_SHORT).show();
});
```

Observă că `DMA05` scrie `MainActivity.this` chiar și în lambda. Aici nu e obligatoriu — `this` ar fi fost tot `MainActivity` — dar este corect și lizibil. În `binding.radioGroup.setOnCheckedChangeListener(...)`, `DMA05` folosește tot o clasă anonimă, deși `RadioGroup.OnCheckedChangeListener` are **una** singură metodă (`onCheckedChanged(group, checkedId)`) și ar fi permis o lambda; codul din interior are nevoie de `group.findViewById(checkedId)`.

**Confuzia tipică**

„Lambda este mereu mai bună." Nu. Pentru `SeekBar` și `TextWatcher` nu este posibilă. Și pentru un listener care are nevoie de `this` ca obiect (nu ca `Context`), clasa anonimă poate fi mai clară.

A doua: „lambda creează un obiect nou la fiecare apel". Nu neapărat. Compilatorul poate refolosi o instanță dacă lambda nu capturează nimic. Oricum, costul este neglijabil — nu este un criteriu de alegere.

A treia: „`this` în lambda este lambda". Nu — este exact invers față de clasa anonimă. În lambda, `this` este **instanța în care e scrisă lambda**. De aceea `Toast.makeText(this, ...)` funcționează într-o lambda dintr-o activitate, dar nu într-o clasă anonimă din aceeași activitate.

A patra: „pot modifica o variabilă locală într-o lambda". Nu, dacă e locală. Poți modifica un **câmp** al clasei. Diferența se vede la compilare: `Variable used in lambda expression should be final or effectively final`.

---

## Conceptul 37.16 — Modelul (POJO) și Serializable

**Ce este**

Un **POJO** (*Plain Old Java Object*) este o clasă care conține doar date: câmpuri private, getteri, setteri, constructori, eventual `toString()` și `equals()`. Nu are logică de business, nu depinde de Android, nu știe ce e un `EditText`. `Serializable` este o **interfață marker** — nu are nicio metodă — care îi spune JVM-ului că obiectele clasei pot fi transformate într-un flux de bytes și reconstruite.

**De ce există**

POJO-ul există din trei motive care se văd direct în cod. **Separare**: clasa `Movie` are un singur motiv să se schimbe — structura datelor unui film. **Testabilitate**: poți testa `Movie` fără emulator, pentru că fișierul nu are niciun `import android.*`. **Transportabilitate**: un obiect fără `Context` și fără `View` poate traversa granița dintre două activități.

`Serializable` există pentru că acea graniță **nu permite referințe**. Când `MainActivity` trimite un `Movie` către `ItemActivity`, cele două activități rulează în același proces, dar comunică prin `Binder`, adică prin bytes. Nu poți trimite o referință; trebuie să trimiți o **copie serializată**.

**Cum funcționează**

Serializarea, pas cu pas:

```
MainActivity                          Binder                    ItemActivity
------------                          ------                    ------------
movies.get(0)  ->  Movie@A
                        |
                        | putExtra("movie", Movie@A)
                        v
              ObjectOutputStream
                 scrive în bytes:
                   - numele clasei + serialVersionUID
                   - fiecare câmp ne-static, ne-transient
                        |
                        v
                  Bundle { "movie" -> byte[] }
                        |
                        | (Binder transaction, ~1MB limită)
                        v
              ObjectInputStream
                 citește bytes, creează Movie@A'
                 (constructor NU se apelează!)
                        |
                        v
                                          existing = Movie@A'   <- obiect NOU
```

Trei consecințe, toate vizibile în cod:

1. **Obiectul primit este o copie.** `Movie@A'` are aceleași valori, dar altă adresă. Modificarea lui nu atinge lista din `MainActivity`. De aceea `saveMovie()` construiește un `Movie` **nou** și îl trimite înapoi, iar `MainActivity` face `movies.set(position, movie)`.
2. **Constructorul nu rulează la deserializare.** JVM-ul creează obiectul fără să îl apeleze. De aceea `Movie` are un constructor gol explicit — nu pentru serializare, ci pentru `new Movie()` din `saveMovie()`.
3. **`serialVersionUID` este calculat automat** din structura clasei dacă nu îl declari. Dacă adaugi un câmp între scriere și citire, cele două valori nu se mai potrivesc și primești `InvalidClassException`. În G1097 riscul e teoretic: scrierea și citirea se întâmplă în același proces, la milisecunde distanță.

Ce este și ce nu este serializabil:

| Serializabil | Nu este serializabil |
|---|---|
| primitivele și wrapper-ele lor | `Context`, `Activity`, `Application` |
| `String` | `View`, `Drawable`, `Bitmap` |
| `Date`, `Calendar` | `Thread`, `Socket`, `InputStream` |
| `ArrayList`, `HashMap` (dacă elementele sunt) | orice clasă fără `implements Serializable` |
| orice clasă care implementează `Serializable` | un câmp `transient` (se sare la scriere) |

**Ce se rupe fără el**

- **Fără `implements Serializable`**: `intent.putExtra(MOVIE_EXTRA, movie)` nu găsește nicio suprascriere potrivită. **Eroare de compilare**, nu de runtime: `no suitable method found for putExtra(String,Movie)`.
- **Cu un câmp neserializabil**: `NotSerializableException: ro.ase.ie.g1097.model.Movie` la runtime, când bundle-ul este scris. Se întâmplă dacă adaugi un câmp de tip `Drawable` sau `Context`.
- **Fără constructor gol**: `saveMovie()` face `new Movie()` — dacă ai doar constructorul cu 10 parametri, nu compilează. În Java, un constructor cu parametri **suprimă** constructorul implicit.
- **Cu `release` null**: `fillForm` apelează `dateFormat.format(existing.getRelease())`, iar `SimpleDateFormat.format(null)` aruncă `NullPointerException`. Se întâmplă dacă un film e construit fără dată — de exemplu dacă trimiți `MOVIE_EXTRA` fără ca utilizatorul să fi ales o dată.
- **Cu `budget` gol**: `Double.parseDouble("")` aruncă `NumberFormatException` în `saveMovie()`. Un câmp numeric gol este cea mai frecventă sursă de crash din formular.

**Unde îl vezi în G1097**

`Movie.java` — 10 câmpuri, două constructoare, 20 de getteri/setteri, `toString()`:

```java
public class Movie implements Serializable {
    private String title;        // EditText
    private Date release;        // EditText date
    private String genre;        // Spinner
    private double budget;       // EditText number
    private int duration;        // SeekBar
    private float rating;        // RatingBar
    private boolean watched;     // Switch
    private String approval;     // RadioGroup | RadioButtons
    private boolean onWatchlist; // Checkbox
    private String poster = null;

    public Movie(String title, Date release, String genre, double budget, int duration,
                 float rating, boolean watched, String approval, boolean onWatchlist, String poster) { ... }

    public Movie() { }           // necesar pentru new Movie() din saveMovie()
```

Comentariile din dreapta fiecărui câmp nu sunt decorative: ele documentează **de unde vine valoarea**. Modelul nu știe ce e un `SeekBar`, dar cineva care citește clasa știe că `duration` se populează dintr-unul.

`toString()` este contractul de afișare pentru `ArrayAdapter`:

```java
@Override
public String toString() {
    return "Movie{" +
            "title='" + title + '\'' +
            ", release=" + release +
            ", genre='" + genre + '\'' +
            ", budget=" + budget +
            ", duration=" + duration +
            ", rating=" + rating +
            ", watched=" + watched +
            ", approval='" + approval + '\'' +
            ", onWatchlist=" + onWatchlist +
            ", poster='" + poster + '\'' +
            '}';
}
```

De aceea lista din `MainActivity` arată rânduri de forma `Movie{title='Inception', release=..., genre='Sci-Fi', ...}` — `ArrayAdapter` cheamă `toString()` pe fiecare element (vezi 37.17). Dacă ai schimba `toString()` să întoarcă doar titlul, lista ar arăta curat, fără nicio altă modificare.

Transportul, în două locuri:

```java
// MainActivity — trimitere
intent.putExtra(MOVIE_EXTRA, movies.get(position));

// ItemActivity — primire (varianta modernă, tipată)
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
```

`IntentCompat.getSerializableExtra(intent, key, Class)` este varianta din `androidx.core` care întoarce tipul corect fără cast. Varianta veche, `intent.getSerializableExtra(key)`, întoarce `Serializable` și cere un cast explicit.

**Confuzia tipică**

„`Serializable` și `Parcelable` sunt același lucru." Nu. `Serializable` este mecanismul Java, bazat pe reflecție — simplu de folosit, dar lent. `Parcelable` este mecanismul Android, scris manual — mult mai rapid, dar cu ~30 de linii de cod per clasă. Pentru un obiect mic trimis între două ecrane, `Serializable` este alegerea rezonabilă; pentru liste mari sau `Bundle`-uri frecvente, `Parcelable`.

A doua: „obiectul primit este originalul". Nu. Este o copie deserializată. Consecința practică e întreaga arhitectură a editării din G1097: `ItemActivity` nu poate modifica filmul din listă, pentru că nu are filmul din listă. De aceea trimite înapoi un obiect nou, iar `MainActivity` îl pune la poziția primită.

A treia: „`Serializable` face obiectul persistent". Nu. Produce un flux de bytes, atât. Persistența pe disc este o altă problemă (fișier, `SharedPreferences`, bază de date).

A patra: „`isWatched()` este o greșeală, ar trebui `getWatched()`". Nu. Convenția JavaBeans cere `isX()` pentru `boolean` primitiv. Ambele funcționează, dar `isX()` este forma idiomatică — și e cea pe care o așteaptă unele librării de serializare.

---

## Conceptul 37.17 — Adapter: ce este și de ce există

**Ce este**

Un adapter este **puntea dintre o sursă de date și un widget de listă**. Widget-ul nu știe ce e un `Movie`; adapterul știe, și îi traduce: „am atâtea elemente", „dă-mi view-ul pentru elementul de la poziția 3". `ArrayAdapter` este implementarea generică pentru o listă de obiecte afișate printr-un singur text; `BaseAdapter` și `RecyclerView.Adapter` sunt clasele de bază pentru adaptoare proprii.

**De ce există**

Pentru că `ListView` are nevoie de un răspuns la două întrebări pe care nu le poate deduce: **câte rânduri sunt** și **cum arată rândul i**. Fără adapter ai avea două variante, ambele imposibile la scară. Prima: creezi tu toate view-urile și le adaugi într-un `LinearLayout` — pentru 1000 de filme ai 1000 de view-uri în memorie, indiferent câte se văd. A doua: înveți `ListView` despre `Movie` — dar atunci `ListView` ar depinde de modelul tău, iar un al doilea model ar cere un al doilea `ListView`.

Adapterul rezolvă ambele: `ListView` rămâne generic, iar tu îi dai un obiect care știe să răspundă. Și, crucial, adapterul este chemat **doar pentru rândurile vizibile** — de aici vine eficiența (vezi 37.18).

**Cum funcționează**

Cine apelează metodele adapterului: **`ListView`**, nu tu. Tu doar setezi adapterul o dată.

```
MainActivity                          ListView                       ArrayAdapter
------------                          --------                       ------------
movies: List<Movie>
    |
    | new ArrayAdapter<>(this,
    |     simple_list_item_1, movies)
    +---------------------------->  setAdapter(adapter)
                                         |
                                         | 1. getCount()  -> 3
                                         |    „am nevoie de 3 rânduri"
                                         |
                                         | 2. getView(0, null, parent)
                                         |       -> inflate simplu TextView
                                         |       -> setText(movies.get(0).toString())
                                         | 3. getView(1, null, parent)
                                         | 4. getView(2, null, parent)
                                         v
                                    afișează 3 rânduri

utilizatorul derulează (dacă ar fi 100 de filme):
    rândul 0 iese -> convertView = rândul 0
    ListView cheamă getView(7, convertView, parent)
      -> adapterul refolosește vederea și schimbă doar textul
```

Patru momente în care `ListView` întreabă adapterul:

| Moment | Metodă | Ce se întâmplă |
|---|---|---|
| la `setAdapter` | `getCount()` | află câte rânduri are |
| la desenare | `getView(position, convertView, parent)` | cere view-ul pentru fiecare rând vizibil |
| la derulare | `getView(...)` cu `convertView` | cere un rând nou, oferind unul reciclat |
| la `notifyDataSetChanged()` | `getCount()` + `getView(...)` | reinteroghează tot ce e vizibil |

`ArrayAdapter` are o particularitate care explică tot ce vezi în listă: **cheamă `toString()` pe fiecare element** și pune rezultatul într-un singur `TextView`. De aceea rândurile din G1097 arată ca niște obiecte Java tipărite, nu ca niște titluri de film.

**Ce se rupe fără el**

- **Fără `setAdapter`**: lista e goală, fără nicio eroare. `ListView` fără adapter nu are ce întreba, deci nu desenează nimic. Simptomul e identic cu „lista mea e goală", deși datele există.
- **Fără `notifyDataSetChanged()`**: lista arată datele de la ultimul bind. Adaugi un film, lista rămâne cu trei rânduri, deși `movies.size()` este 4. `ListView` **nu observă** lista — nu are cum, e un `ArrayList` obișnuit.
- **Adapter creat cu altă listă**: `new ArrayAdapter<>(this, layout, new ArrayList<>())` în loc de `movies` → lista e veșnic goală, pentru că modifici o listă, iar adapterul citește alta.
- **`notifyDataSetChanged()` înainte de modificare**: `IndexOutOfBoundsException`, pentru că adapterul reinteroghează `getCount()` și apoi cere rânduri care încă nu există în listă.

**Unde îl vezi în G1097**

Trei linii, în trei locuri diferite, și fiecare contează:

```java
// MainActivity.onCreate — adapterul ține REFERINȚA la `movies`, nu o copie
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

// MainActivity.initControls — legarea de widget
listView.setAdapter(movieAdapter);

// MainActivity — callback-ul rezultatului, DUPĂ fiecare modificare a listei
movies.add(movie);
movieAdapter.notifyDataSetChanged();
```

Ordinea din callback este contractul:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();      // întâi modifici, apoi notifici
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

`android.R.layout.simple_list_item_1` este layout-ul de rând: un singur `TextView` cu ID-ul `android.R.id.text1`. `ArrayAdapter` îl umple cu `toString()`. Dacă vrei un rând cu mai multe view-uri, ai nevoie de un adapter propriu — exact ce arată `DMA06`.

`DMA06/TwoColumnActivity` — un `BaseAdapter` propriu, pentru două coloane:

```java
ListView lvNumbers = findViewById(R.id.lvNumbers);
NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
lvNumbers.setAdapter(adapter);
```

`DMA06/NumberListAdapter` — cele patru metode pe care `BaseAdapter` le cere:

```java
@Override public int getCount()  { return numbers.size(); }
@Override public Integer getItem(int position) { return numbers.get(position); }
@Override public long getItemId(int position) { return numbers.get(position); }
@Override public View getView(int position, View convertView, ViewGroup parent) { ... }
```

`getItemId` este interesant: întoarce **numărul însuși**, nu poziția, pentru că numerele sunt unice. În G1097, `Movie` nu are ID, deci identitatea este poziția — de aici tot mecanismul `POSITION_EXTRA`.

**Confuzia tipică**

„Adapterul este lista." Nu. Adapterul **citește** lista. `ArrayAdapter` primește o referință la `movies` și o citește la fiecare `getView`. De aceea `movies.add(...)` se vede imediat în adapter — dar numai după `notifyDataSetChanged()`.

A doua: „adapterul observă lista și se actualizează singur." Nu. `ArrayList` nu are mecanism de notificare. De aceea există `notifyDataSetChanged()`, `notifyItemInserted()`, `notifyItemRemoved()`. Fără ele, `ListView` crede că lista e neschimbată.

A treia: „`notifyDataSetChanged()` redesenează lista." Nu redesen­ează — **anunță** că datele s-au schimbat, iar `ListView` decide ce reinteroghează. Efectul e reconstruirea rândurilor vizibile, fără animații.

A patra: „un adapter per rând". Nu — un adapter per **listă**. El produce toate rândurile, unul câte unul, și e chemat de atâtea ori câte rânduri are nevoie widget-ul.

---

## Conceptul 37.18 — ViewHolder și reciclarea rândurilor

**Ce este**

`ViewHolder` este un obiect mic care **păstrează referințele la view-urile unui rând**, ca să nu fie căutate din nou la fiecare afișare. Reciclarea este mecanismul prin care widget-ul de listă **refolosește view-urile care ies din ecran** pentru rândurile care intră, în loc să creeze altele noi.

**De ce există**

Pentru că `findViewById` și `inflate` sunt scumpe, iar o listă se derulează. Fără reciclare, o listă de 1000 de elemente ar avea 1000 de arbori de view-uri în memorie — indiferent că se văd 8. Fără `ViewHolder`, fiecare derulare ar face `findViewById` pentru fiecare view din rând, de zeci de ori pe secundă. Împreună, cele două transformă o operație O(n) în memorie și O(n) căutări într-una O(1) în memorie și O(1) căutări per rând afișat.

**Cum funcționează**

Reciclarea, pas cu pas, pe o listă de 100 de elemente cu 7 rânduri vizibile:

```
Starea inițială — 7 view-uri create, 7 rânduri vizibile:

  ecran:  [0][1][2][3][4][5][6]
  pool:   (gol)

Derulezi în jos cu un rând:

  rândul 0 iese în sus
     -> ListView îl ia și îl pune în pool ca `convertView`
  rândul 7 intră în jos
     -> ListView cheamă getView(7, convertView = rândul 0, parent)

  getView(7, convertView, parent):
     convertView != null?
       DA  -> NU mai inflatezi. Refosești vederea existentă.
              holder = (ViewHolder) convertView.getTag()
       NU  -> inflatezi rândul o dată, creezi holder-ul,
              findViewById pentru fiecare view,
              convertView.setTag(holder)

     apoi, în ambele cazuri:
       holder.tvDecimal.setText(String.valueOf(numbers.get(7)))
       holder.tvBinary.setText(Integer.toBinaryString(numbers.get(7)))
       return convertView

Rezultat: pentru 100 de elemente există ~8 view-uri, create o singură dată.
```

Costul, comparat:

| | Fără reciclare | Cu reciclare, fără ViewHolder | Cu ambele |
|---|---|---|---|
| `inflate` per rând | 1 | 1 (prima dată) | 1 (prima dată) |
| `findViewById` per rând afișat | N | N | **0** |
| view-uri în memorie pentru 1000 | 1000 | ~8 | ~8 |

`ViewHolder` nu economisește `inflate` — asta face reciclarea. `ViewHolder` economisește **căutările**. Sunt două optimizări independente, care se combină.

În `RecyclerView`, `ViewHolder` nu mai este opțional: `RecyclerView.Adapter` are `ViewHolder` în semnătura generică, iar `onCreateViewHolder` / `onBindViewHolder` sunt separate tocmai ca să fie imposibil să ratezi separarea.

**Ce se rupe fără el**

- **Fără reciclare** (ignori `convertView` și inflatezi de fiecare dată): lista funcționează, dar derularea devine sacadată pe liste lungi, iar memoria crește proporțional cu numărul de rânduri vizitate. Nu e crash, e jank.
- **Fără `setTag`**: `holder = (ViewHolder) convertView.getTag()` întoarce `null`, apoi `holder.tvDecimal` aruncă `NullPointerException` la prima derulare. Se întâmplă dacă uiți `convertView.setTag(holder)` în ramura `if`.
- **Cu `setTag` dar fără `getTag`**: `findViewById` la fiecare rând — funcționează, dar pierzi optimizarea.
- **Cu un câmp nesetat în `bind`**: rândul reciclat păstrează valoarea de la elementul anterior. Simptomul clasic: derulezi și vezi un titlu de film peste posterul altuia. Cauza: ai setat textul doar condiționat, iar pe ramura `else` ai lăsat valoarea veche.
- **`ViewHolder` care ține datele**: dacă pui `Movie movie` în `ViewHolder` și uiți să îl actualizezi în `bind`, ai exact același simptom, dar mai greu de găsit.

**Unde îl vezi în G1097**

G1097 folosește `ArrayAdapter`, care are reciclare **internă** — de aceea codul nu arată niciun `convertView`. Reciclarea se întâmplă, doar că nu o vezi:

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

`ArrayAdapter.getView(position, convertView, parent)` refolosește `convertView` dacă există și face `setText(movies.get(position).toString())`. Pentru un singur `TextView`, asta e suficient.

`DMA06` arată mecanismul explicit, în două variante. `NumberListAdapter` — `ListView` cu `ViewHolder` manual:

```java
@Override
public View getView(int position, View convertView, ViewGroup parent) {
    ViewHolder holder;

    if (convertView == null) {
        // rând nou: inflate + cache de referințe
        convertView = layoutInflater.inflate(R.layout.item_number, parent, false);
        holder = new ViewHolder();
        holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);
        holder.tvBinary = convertView.findViewById(R.id.tvBinary);
        convertView.setTag(holder);
    } else {
        // rând reciclat: ia referințele din tag
        holder = (ViewHolder) convertView.getTag();
    }

    int number = getItem(position);
    holder.tvDecimal.setText(String.valueOf(number));
    holder.tvBinary.setText(Integer.toBinaryString(number));

    return convertView;
}

private static class ViewHolder {
    TextView tvDecimal;
    TextView tvBinary;
}
```

`NumberRecyclerAdapter` — aceeași idee, dar `ViewHolder` este obligatoriu și `getView` este împărțit în două:

```java
static class NumberViewHolder extends RecyclerView.ViewHolder {
    final TextView tvDecimal;
    final TextView tvBinary;

    NumberViewHolder(@NonNull View itemView) {
        super(itemView);
        tvDecimal = itemView.findViewById(R.id.tvDecimal);
        tvBinary = itemView.findViewById(R.id.tvBinary);
    }
}

@NonNull
@Override
public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
    // rulează doar când e nevoie de un rând NOU
    View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.item_number, parent, false);
    return new NumberViewHolder(view);
}

@Override
public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
    // rulează de fiecare dată când rândul afișează un număr
    int number = numbers.get(position);
    holder.tvDecimal.setText(String.valueOf(number));
    holder.tvBinary.setText(Integer.toBinaryString(number));
}
```

Împărțirea este exact `if (convertView == null)` / `else` din `ListView`, dar făcută de framework: `onCreateViewHolder` este ramura „rând nou", `onBindViewHolder` este partea care rulează mereu.

**Confuzia tipică**

„`ViewHolder` ține datele rândului." Nu — ține **view-urile** rândului. Datele se pun la fiecare `bind`, pentru că rândul este refolosit pentru alt element. Dacă pui date în `ViewHolder` și uiți să le actualizezi, rândul arată datele elementului precedent.

A doua: „reciclarea înseamnă că se creează mai puține rânduri". Nu — înseamnă că se creează mai puține **view-uri**. Rândurile logice sunt tot atâtea câte elemente are lista; view-urile fizice sunt doar câte încap pe ecran plus câteva.

A treia: „`RecyclerView` reciclează mai bine decât `ListView`". Reciclează **mai explicit** și cu un pool configurabil, dar mecanismul de bază este același. Diferența reală este că `RecyclerView` te obligă să separi crearea de legare (vezi 37.20).

A patra: „dacă lista are 3 elemente, reciclarea nu contează". Corect — și de aceea G1097 poate folosi `ArrayAdapter` fără nicio grijă. Reciclarea contează de la câteva zeci de elemente în sus.

---
## Conceptul 37.19 — LayoutManager

**Ce este**

`LayoutManager` este obiectul care decide, pentru un `RecyclerView`, **unde stă fiecare rând** și **când trebuie reciclat**. El este cel care știe dacă lista se aranjează vertical, orizontal, în grilă sau în grilă eșalonată. Vine în trei implementări gata făcute: `LinearLayoutManager`, `GridLayoutManager`, `StaggeredGridLayoutManager`.

**De ce există**

Pentru că `RecyclerView` a fost proiectat ca un **motor de reciclare**, nu ca o listă. El știe să țină un pool de view-uri, să le dea și să le ia înapoi, să ruleze animații. Nu știe însă — și nu ar trebui să știe — cum se aranjează elementele. Separarea aceasta permite schimbarea aranjării fără atingerea adapterului: același `NumberRecyclerAdapter` funcționează cu `LinearLayoutManager` vertical, orizontal sau cu `GridLayoutManager` pe 3 coloane, fără o linie schimbată.

**Cum funcționează**

Relația dintre cele patru componente:

```
RecyclerView
├── LayoutManager        <- unde stă fiecare rând, care e fereastra vizibilă
├── Adapter              <- ce date are fiecare rând, cum arată
├── ItemAnimator         <- ce animație rulează la inserare/ștergere
└── ItemDecoration       <- ce se desenează ÎNTRE rânduri (separatoare, margini)
```

Ciclul, la fiecare derulare:

```
1. RecyclerView primește un eveniment de scroll
2. LayoutManager calculează ce poziții ar trebui să fie vizibile acum
      -> „rândurile 5..12"
3. pentru fiecare poziție care intră:
      -> cere adapterului un ViewHolder
         -> din pool, dacă există (onBindViewHolder)
         -> nou, dacă nu (onCreateViewHolder)
4. LayoutManager poziționează fiecare view: layout(left, top, right, bottom)
5. pentru fiecare poziție care iese:
      -> ViewHolder se întoarce în pool
```

`LinearLayoutManager` — un singur ax, cu `getOrientation()` care întoarce `VERTICAL` sau `HORIZONTAL`. Această metodă este folosită în `DMA06` ca să configureze separatorul:

```java
LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
rvNumbers.addItemDecoration(
        new DividerItemDecoration(this, layoutManager.getOrientation()));
```

`GridLayoutManager` — primește numărul de coloane în constructor: `new GridLayoutManager(this, 3)`. `StaggeredGridLayoutManager` — primește numărul de coloane și orientarea, și permite înălțimi diferite per element.

**Ce se rupe fără el**

- **Fără `setLayoutManager`**: `RecyclerView` nu afișează **nimic**. Nu crapă, nu aruncă excepție — doar rămâne gol, iar în logcat apare `RecyclerView: No layout manager attached; skipping layout`. Este cea mai frecventă greșeală la prima folosire, pentru că `ListView` nu avea nevoie de așa ceva.
- **`LinearLayoutManager` cu `context` greșit**: compilează și funcționează, dar tema și resursele vin din alt context. Simptomul poate fi un separator cu culoarea greșită.
- **`GridLayoutManager` cu 0 coloane**: `IllegalArgumentException: spanCount should be at least 1`.
- **Schimbarea `LayoutManager` după `setAdapter`**: funcționează, dar provoacă un re-layout complet. Nu e o eroare, e o operație scumpă.

**Unde îl vezi în G1097**

**G1097 nu are `RecyclerView`**, deci nici `LayoutManager`. `activity_main.xml` folosește `ListView`, care își are aranjarea implementată intern — verticală, fără alternativă.

`DMA06/RecyclerViewActivity` este exemplul complet, în șapte linii:

```java
RecyclerView rvNumbers = findViewById(R.id.rvNumbers);

LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
rvNumbers.addItemDecoration(
        new DividerItemDecoration(this, layoutManager.getOrientation()));

NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

Ordinea contează și merită observată: `LayoutManager` **înainte** de adapter. `RecyclerView` poate primi adapterul fără layout manager, dar nu va desena nimic până nu primește și layout manager-ul. De ce: adapterul spune *câte* elemente sunt, layout manager-ul spune *care* dintre ele se văd.

`activity_recycler_view.xml` arată de ce `RecyclerView` are nevoie de `0dp` + `weight` ca să ocupe restul ecranului sub header:

```xml
<include layout="@layout/layout_number_header" />
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/rvNumbers"
    android:layout_width="match_parent"
    android:layout_height="0dp"
    android:layout_weight="1" />
```

**Confuzia tipică**

„`RecyclerView` este un `ListView` cu animații." Nu. `RecyclerView` este un container gol care deleagă **totul**: aranjarea la `LayoutManager`, datele la `Adapter`, reciclarea la `RecycledViewPool`, animațiile la `ItemAnimator`, separatoarele la `ItemDecoration`. `ListView` avea toate acestea încorporat, într-o singură clasă greu de extins.

A doua: „`LayoutManager` desenează rândurile". Nu — el calculează poziții și cheamă `layout(...)` pe fiecare view. Desenarea o face `RecyclerView` prin `draw()`, iar conținutul fiecărui rând îl desenează view-urile din el.

A treia: „`ListView` nu are layout manager". Are — este implicit și fix (vertical). De aceea nu îl poți schimba. `RecyclerView` a scos decizia din clasă și a făcut-o parametru.

A patra: „`DividerItemDecoration` este parte din `RecyclerView`". Nu — este o `ItemDecoration`, adică un obiect separat pe care îl adaugi. `ListView` avea `android:divider` ca atribut XML; `RecyclerView` a scos și asta în afară.

---

## Conceptul 37.20 — ListView vs RecyclerView

**Ce este**

Sunt **două widget-uri de listă** cu aceeași misiune și cu filosofii diferite. `ListView` este varianta veche: face totul singur — reciclare, aranjare, separatoare — și îți dă un singur punct de extensie, `getView()`. `RecyclerView` este varianta nouă: un container gol care împarte responsabilitățile între `Adapter`, `LayoutManager`, `ItemAnimator` și `ItemDecoration`.

**De ce există amândouă**

`ListView` există din primele versiuni de Android și funcționează. `RecyclerView` a apărut în `androidx` pentru că `ListView` avea trei limitări structurale pe care nu le puteai repara fără să spargi compatibilitatea: reciclarea era **implicită** și ușor de ratat, aranjarea era **fixă** (verticală), iar notificările erau **globale** (`notifyDataSetChanged()` reconstruia tot, fără animații). `RecyclerView` a rezolvat toate trei prin separare: reciclarea e obligatorie prin `ViewHolder`, aranjarea e un parametru, notificările sunt granulare.

`ListView` nu a fost scos din Android — este încă acolo, încă funcționează, și este alegerea corectă pentru o listă simplă. G1097 îl folosește exact așa.

**Cum funcționează**

Comparația pipeline-urilor, pas cu pas:

```
ListView                                RecyclerView
--------                                ------------
setAdapter(adapter)                     setLayoutManager(lm)
                                        setAdapter(adapter)

ListView:                               RecyclerView + LayoutManager:
  getCount()                              getItemCount()
  getView(0, null, parent)                onCreateViewHolder(parent, viewType)  <- o dată
     -> inflate                            onBindViewHolder(holder, 0)         <- mereu
     -> findViewById
     -> setText
  getView(1, null, parent)
     -> inflate
     ...
                                        la derulare:
la derulare:                              LayoutManager decide ce poziții intră
  getView(7, convertView, parent)         pool de ViewHolder (nu de View)
     -> convertView != null?              onCreateViewHolder doar dacă pool-ul e gol
     -> getTag / setTag                   onBindViewHolder pentru fiecare
     -> setText
```

Tabelul de corespondență, care se cere la test:

| `ListView` / `BaseAdapter` | `RecyclerView.Adapter` | Când rulează |
|---|---|---|
| `getCount()` | `getItemCount()` | la nevoie |
| `getView()`, ramura `convertView == null` | `onCreateViewHolder()` | o dată per rând creat |
| `getView()`, partea de `setText` | `onBindViewHolder()` | la fiecare afișare |
| `ViewHolder` + `setTag`/`getTag` manual | `RecyclerView.ViewHolder` obligatoriu | — |
| `android:divider` în XML | `DividerItemDecoration` adăugat în cod | — |
| `notifyDataSetChanged()` | `notifyItemInserted/Changed/Removed` | după fiecare mutație |

Diferențele care contează în practică:

| Criteriu | `ListView` | `RecyclerView` |
|---|---|---|
| reciclare | implicită, ușor de ratat | obligatorie prin `ViewHolder` |
| aranjare | doar verticală | orice `LayoutManager` |
| animații la schimbare | nu | da, prin `ItemAnimator` |
| notificare granulară | nu | da (`notifyItem*`) |
| separatoare | atribut XML | `ItemDecoration` |
| cod pentru o listă simplă | 3 linii | 5–6 linii + o clasă de adapter |

**Ce se rupe fără el**

- **Migrare `ListView` → `RecyclerView` fără `setLayoutManager`**: lista apare goală, cu warning în logcat. Vezi 37.19.
- **`getView` care nu refolosește `convertView`**: lista funcționează, dar derularea e sacadată. Nu e eroare.
- **`notifyDataSetChanged()` în `RecyclerView`**: funcționează, dar pierzi animațiile și reconstruiești tot. Nu e greșit, e doar mai puțin eficient decât `notifyItemInserted`.
- **`RecyclerView` fără `layout_height` determinat** (de exemplu `wrap_content` într-un `ScrollView`): înălțimea se calculează greșit, iar lista se vede tăiată sau complet goală. `RecyclerView` are nevoie de o înălțime cunoscută ca să știe câte rânduri să creeze.

**Unde îl vezi în G1097**

G1097 folosește **`ListView` + `ArrayAdapter`**, alegerea minimă pentru trei rânduri:

```java
// activity_main.xml
<ListView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:entries="@array/items" />
```

```java
// MainActivity.onCreate
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

Observă `android:entries="@array/items"` din XML: este o legătură statică la array-ul de 20 de elemente din `strings.xml`. Ea este **înlocuită** la runtime de `listView.setAdapter(movieAdapter)` din `initControls()`. Cele două mecanisme nu se combină — `setAdapter` câștigă.

`DMA06` are toate trei variantele, în trei activități, exact ca să le poți compara:

| Activitate | Widget | Adapter | Rând |
|---|---|---|---|
| `SingleColumnActivity` | `ListView` | `ArrayAdapter<Integer>` | un `TextView` |
| `TwoColumnActivity` | `ListView` | `NumberListAdapter extends BaseAdapter` | două `TextView` |
| `RecyclerViewActivity` | `RecyclerView` | `NumberRecyclerAdapter` | două `TextView` |

Aceeași listă de numere de la 1 la 100, același layout de rând (`item_number.xml`), trei implementări. Diferența dintre `TwoColumnActivity` și `RecyclerViewActivity` este exact ce trebuie să poți explica:

```java
// TwoColumnActivity — 2 linii
NumberListAdapter adapter = new NumberListAdapter(this, NumberData.getNumbers());
lvNumbers.setAdapter(adapter);

// RecyclerViewActivity — 6 linii
LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
rvNumbers.addItemDecoration(new DividerItemDecoration(this, layoutManager.getOrientation()));
NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

**Confuzia tipică**

„`RecyclerView` este mereu mai rapid." Nu. Pentru 3 elemente, `ListView` + `ArrayAdapter` este mai rapid **și** mai puțin cod. `RecyclerView` câștigă la liste lungi, la animații și la aranjamente variate.

A doua: „`ListView` este depreciat, nu se mai folosește". Nu este marcat `@Deprecated` și funcționează. Google recomandă `RecyclerView` pentru cod nou, dar `ListView` rămâne valid — iar la examen poate fi cerut explicit.

A treia: „`RecyclerView` nu are nevoie de `ViewHolder`". Are — este parte din semnătura generică `RecyclerView.Adapter<VH extends ViewHolder>`. Nu poți scrie un adapter fără el.

A patra: „`ArrayAdapter` funcționează și cu `RecyclerView`". Nu. `ArrayAdapter` extinde `BaseAdapter`, deci este un `ListAdapter` — interfața cerută de `ListView` — nu un `RecyclerView.Adapter`. Pentru `RecyclerView` ai nevoie de un adapter propriu.

---

## Conceptul 37.21 — Intent

**Ce este**

Un `Intent` este **un mesaj prin care ceri sistemului să facă ceva**. Conține o **acțiune** (`ACTION_VIEW`, `ACTION_SEND`, `ACTION_MAIN`), o **componentă** țintă (opțional), **date** (un `Uri`), o **categorie** și **extra-uri** (un `Bundle`). Când are componentă, se numește **explicit** și merge exact acolo. Când nu are, se numește **implicit** și sistemul caută cine îl poate trata.

**De ce există**

Pentru că o aplicație nu trebuie să știe ce alte aplicații are telefonul. Dacă vrei să trimiți un text, nu vrei să cunoști clasa internă a aplicației de mesagerie — vrei să spui „am un text de partajat, cine poate?". `Intent` este această declarație. Pentru navigarea internă, `Intent`-ul explicit rezolvă o problemă mai simplă: dă sistemului o componentă pe care o poate instanția, fără ca tu să o construiești (vezi 37.10).

**Cum funcționează**

Cele două feluri, cu drumul lor prin sistem:

```
EXPLICIT
  new Intent(MainActivity.this, ItemActivity.class)
     |
     |-- component = { ro.ase.ie.g1097, .activities.ItemActivity }
     v
  system_server: caută componenta în manifest
     -> există?  nu -> ActivityNotFoundException
     -> exported? nu și vin din altă aplicație -> SecurityException
     -> pornește

IMPLICIT
  new Intent(Intent.ACTION_SEND).setType("text/plain")
     |
     |-- action = ACTION_SEND, type = text/plain, fără componentă
     v
  system_server: PackageManager.queryIntentActivities()
     -> 0 potriviri   -> ActivityNotFoundException
     -> 1 potrivire   -> pornește direct
     -> 2+ potriviri  -> Intent.createChooser() sau dialog de sistem
```

Anatomia unui `Intent`:

| Câmp | Metodă | Exemplu |
|---|---|---|
| componentă | `new Intent(context, Clasa.class)` | `ItemActivity.class` |
| acțiune | `setAction(...)` | `Intent.ACTION_SEND` |
| date | `setData(Uri)` | `Uri.parse("https://...")` |
| tip MIME | `setType(...)` | `"text/plain"` |
| categorie | `addCategory(...)` | `Intent.CATEGORY_LAUNCHER` |
| extra-uri | `putExtra(...)` | `putExtra("movie", movie)` |
| flag-uri | `setFlags(...)` | `FLAG_ACTIVITY_NEW_TASK` |

**Ce se rupe fără el**

- **Componentă inexistentă**: `ActivityNotFoundException: Unable to find explicit activity class {...}`. Cauza e fie clasa greșită, fie manifestul (vezi 37.4).
- **`Intent` implicit fără handler**: `ActivityNotFoundException: No Activity found to handle Intent { act=android.intent.action.SEND ... }`. Se întâmplă pe emulatoarele fără aplicații de mesagerie.
- **`Intent` implicit cu handler, dar fără `setType`**: multe aplicații se filtrează după tip MIME, deci fără el nu se găsește niciun handler.
- **Un `Intent` fără țintă folosit cu `startActivity`**: `ActivityNotFoundException`, pentru că nu are componentă și nici acțiune. Este exact cazul în care `Intent`-ul este corect construit — dar pentru `setResult`, nu pentru `startActivity` (vezi mai jos).

**Unde îl vezi în G1097**

Trei `Intent`-uri, fiecare cu alt rol:

```java
// 1. MainActivity.initListeners — explicit, către ItemActivity, fără extra-uri (insert)
Intent intent = new Intent(MainActivity.this, ItemActivity.class);
launcher.launch(intent);

// 2. MainActivity.initListeners — explicit, cu două extra-uri (edit)
Intent intent = new Intent(MainActivity.this, ItemActivity.class);
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);
launcher.launch(intent);

// 3. ItemActivity.saveMovie — FĂRĂ țintă, pentru rezultat
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

Al treilea este cel care derutează. `new Intent()` fără parametri nu este o greșeală: un `Intent` de rezultat nu pornește nimic, ci **călătorește înapoi** către activitatea care a lansat-o. Are nevoie doar de extra-uri. Dacă ai pune o componentă în el, ar fi ignorată.

`DMA02` arată un `Intent` **implicit**, singurul din proiectele de curs:

```java
public void pressMe(View view) {
    Intent share = new Intent(Intent.ACTION_SEND);
    share.setType("text/plain");
    share.putExtra(Intent.EXTRA_TEXT, "Hello!");
    startActivity(Intent.createChooser(share, "Share via DMA"));
}
```

`Intent.createChooser(...)` este necesar când există mai mulți handleri: în loc să lași sistemul să aleagă, afișează un dialog. Fără el, Android ar alege ultima aplicație folosită sau ar afișa propriul dialog — `createChooser` îți dă control asupra titlului.

Metoda este legată de XML prin `android:onClick="pressMe"`:

```xml
<Button
    android:id="@+id/button"
    android:onClick="pressMe" />
```

Aceasta este o legătură **declarativă** de listener: sistemul caută metoda `pressMe(View)` în activitate și o apelează. Funcționează, dar nu e recomandată — nu apare nicăieri în cod, deci e greu de găsit, iar o redenumire a metodei rupe legătura la runtime, nu la compilare.

**Confuzia tipică**

„`Intent` este datele." Nu — este **plicul**. Datele stau în `Bundle`-ul de extra-uri (vezi 37.22). `Intent`-ul are și destinație, și acțiune, și flag-uri.

A doua: „un `Intent` fără componentă este inutil". Dimpotrivă — este singurul mod de a cere unui `Intent` de rezultat să existe, și singurul mod de a lansa o aplicație pe care nu o cunoști (implicit).

A treia: „`Intent` explicit și implicit sunt sinonime când există un singur handler". Nu. Un `Intent` explicit ocolește rezolvarea și merge direct la componentă; unul implicit trece prin `PackageManager` și poate găsi **altă** aplicație decât cea la care te gândeai. Pentru navigarea internă, explicit este singura variantă corectă.

A patra: „`putExtra` poate primi orice obiect". Doar primitive, `String`, `Serializable`, `Parcelable` și array-uri din ele. Un `View` sau un `Context` nu trece — iar eroarea apare la runtime, când bundle-ul este scris.

---

## Conceptul 37.22 — Bundle și ce călătorește între activități

**Ce este**

Un `Bundle` este **o colecție cheie-valoare** în care cheile sunt `String`, iar valorile sunt primitive, `String`, `Serializable`, `Parcelable` sau array-uri din ele. Extra-urile unui `Intent` **sunt** un `Bundle`: `putExtra(key, value)` scrie în el, `getXxxExtra(key)` citește din el. `Bundle`-ul este și mecanismul prin care sistemul îți dă înapoi starea salvată (vezi 37.12).

**De ce există**

Pentru că granița dintre două componente Android este o graniță de **proces**, nu de obiecte. Chiar dacă `MainActivity` și `ItemActivity` rulează în același proces, comunicarea trece prin `Binder`, care transportă doar bytes. Un `Bundle` este structura care știe să transforme valori Java în bytes și înapoi, într-un mod pe care sistemul îl poate transporta și stoca.

**Cum funcționează**

Ce se întâmplă cu fiecare valoare, pe drum:

```
MainActivity                                  ItemActivity
------------                                  ------------
intent.putExtra("position", 0)
   -> Bundle.putInt("position", 0)
   -> stocat ca int (nu ca obiect)

intent.putExtra("movie", movie)
   -> Bundle.putSerializable("movie", movie)
   -> la nevoie: ObjectOutputStream -> byte[]

   Bundle { "position" -> 0,
            "movie"    -> byte[] }

        |  Binder transaction
        |  (buffer partajat, ~1 MB per proces)
        v

ItemActivity.getIntent()
   -> același Bundle, dar valori deserializate la cerere
   -> getIntExtra("position", -1)            -> 0
   -> getSerializableExtra("movie")          -> Movie@A'  (COPIE)
```

Trei consecințe practice:

1. **Cheia este un contract.** `"movie"` într-o parte și `"Movie"` în cealaltă → `null`, fără nicio eroare. De aceea G1097 ține cheile în constante: `protected static final String MOVIE_EXTRA = "movie";`.
2. **Valoarea implicită este obligatorie la citire.** `getIntExtra(key, -1)` are nevoie de o valoare de întoarcere când cheia lipsește. G1097 folosește `-1` ca **santinelă** pentru „nu există poziție", adică modul insert.
3. **Există o limită de dimensiune.** `Binder` are un buffer de ~1 MB per proces. Un `Bitmap` mare sau o listă de mii de obiecte produce `TransactionTooLargeException` — o excepție care apare la `launch`, nu la `putExtra`.

Tipurile de citire, cu valoarea implicită:

| Metodă | Tip returnat | Implicit în G1097 |
|---|---|---|
| `getIntExtra(key, def)` | `int` | `-1` |
| `getStringExtra(key)` | `String` sau `null` | — |
| `getBooleanExtra(key, def)` | `boolean` | — |
| `getSerializableExtra(key)` | `Serializable` (cere cast) | — |
| `IntentCompat.getSerializableExtra(intent, key, Class)` | tipat | — |

**Ce se rupe fără el**

- **Cheie greșită**: `null` sau valoarea implicită, fără eroare. Cel mai frecvent bug de `Intent`, și motivul pentru care cheile stau în constante.
- **Tip greșit la citire**: `getIntExtra` pe o cheie care ține un `String` întoarce valoarea implicită, nu o excepție. `getSerializableExtra` cu cast greșit aruncă `ClassCastException`.
- **`TransactionTooLargeException`**: la trimiterea unui obiect mare. Simptomul e un crash în `launcher.launch(intent)`, cu mesaj despre `Binder transaction`.
- **Valoare implicită nepotrivită**: `getIntExtra(POSITION_EXTRA, 0)` în loc de `-1` ar face ca orice insert să fie tratat ca editare a primului film. Atenție la sentinelă.
- **Obiect mutabil modificat după `putExtra`**: nu se vede în cealaltă activitate, pentru că serializarea s-a făcut la `putExtra`. Comportamentul e corect, dar contraintuitiv.

**Unde îl vezi în G1097**

Trei locuri, care formează un circuit complet:

```java
// MainActivity — scriere (două extra-uri)
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);

// ItemActivity — citire, cu sentinelă
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    ...
}

// ItemActivity — scriere înapoi
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);

// MainActivity — citire în callback
Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
int position = intent.getIntExtra(POSITION_EXTRA, -1);
if (position == -1) {
    movies.add(movie);
} else {
    movies.set(position, movie);
}
```

Observă asimetria din `saveMovie()`: `POSITION_EXTRA` se pune **doar** dacă `position != -1`. La insert, `position` este `-1`, deci extra-ul lipsește, iar `MainActivity` primește valoarea implicită `-1` și intră pe ramura `add`. La editare, `position` este `0` sau mai mare, extra-ul există, iar `MainActivity` intră pe ramura `set`. Un singur `int` codifică două moduri de operare.

**Confuzia tipică**

„`Bundle`-ul este același obiect la ambele capete." Nu. Este serializat la scriere și deserializat la citire. Consecința: obiectul `Movie` din `ItemActivity` este o copie, iar modificarea lui nu atinge lista (vezi 37.16).

A doua: „`putExtra` acceptă orice". Doar tipuri pe care `Bundle` le poate scrie. Un `Context`, un `View`, un `Drawable` nu sunt acceptate — iar eroarea apare la runtime.

A treia: „`Bundle`-ul este pentru date permanente". Nu. Trăiește cât `Intent`-ul sau cât task-ul. Pentru persistență ai nevoie de fișier, `SharedPreferences` sau bază de date (vezi 37.12).

A patra: „dacă trimit o listă mare, merge". Până la ~1 MB. Peste, `TransactionTooLargeException`. Pentru liste mari, trimite un ID și citește din bază de date în cealaltă activitate.

---

## Conceptul 37.23 — ActivityResultLauncher

**Ce este**

`ActivityResultLauncher<Intent>` este obiectul prin care **porni o activitate și primești un rezultat înapoi**. Se obține din `registerForActivityResult(contract, callback)`, iar lansarea se face cu `launcher.launch(intent)`. Înlocuiește vechea pereche `startActivityForResult()` + `onActivityResult()`, care a fost deprecată.

**De ce există**

Pentru că vechiul mecanism avea trei probleme structurale. Prima: **coduri de cerere** (`REQUEST_CODE = 1`) pe care trebuia să le gestionezi manual, cu risc de coliziune. A doua: **un singur callback pentru toate rezultatele** — `onActivityResult(requestCode, resultCode, data)` — un `switch` care creștea cu fiecare ecran. A treia, cea mai gravă: dacă activitatea era **recreată** (la rotire) în timp ce ecranul copil era deschis, rezultatul se pierdea sau ajungea la altă instanță.

`ActivityResultLauncher` rezolvă toate trei: fiecare lansare are propriul callback, nu există coduri de cerere, iar înregistrarea supraviețuiește recreării pentru că este ținută de `ActivityResultRegistry`, nu de instanța activității.

**Cum funcționează**

Ciclul complet:

```
1. onCreate()
     launcher = registerForActivityResult(
                    new ActivityResultContracts.StartActivityForResult(),
                    callback)
        |
        |-- înregistrează callback-ul într-un registry ținut de ComponentActivity
        |-- cheia este generată automat, nu de tine
        v

2. launcher.launch(intent)
        |
        |-- pornește ItemActivity (ca orice startActivity)
        |-- reține că această lansare așteaptă un rezultat
        v

3. ItemActivity: setResult(RESULT_OK, intent) + finish()
        |
        v

4. MainActivity revine în prim-plan
        |
        |-- ActivityResultRegistry găsește callback-ul pentru lansarea asta
        v
   callback.onActivityResult(ActivityResult o)
        |-- o.getResultCode()  -> RESULT_OK / RESULT_CANCELED
        |-- o.getData()        -> Intent-ul cu extra-uri (poate fi null)
```

Regula de înregistrare, care produce cea mai frecventă excepție: **`registerForActivityResult` trebuie apelat înainte ca activitatea să fie `STARTED`.** În practică, în `onCreate`. Dacă îl muți într-un listener, primești:

```
IllegalStateException: LifecycleOwner ... is attempting to register while
current state is RESUMED. LifecycleOwners must call register before they are STARTED.
```

Motivul: registry-ul trebuie să știe ce callback-uri există **înainte** de a primi un rezultat, iar rezultatul poate sosi oricând după `onStart`.

**Ce se rupe fără el**

- **`registerForActivityResult` într-un listener**: `IllegalStateException` la primul click. Este capcana clasică a migrării de la API-ul vechi.
- **Fără `setResult` în copil**: părintele primește `RESULT_CANCELED` și ignoră tot. Se întâmplă când apeși Back „ca să testezi" și crezi că ai salvat.
- **`o.getData()` folosit fără verificare**: `NullPointerException` când rezultatul vine fără `Intent` (de exemplu `RESULT_CANCELED`). G1097 verifică `getResultCode() == RESULT_OK` înainte, dar nu verifică `getData()` — un risc real dacă cineva apelează `setResult(RESULT_OK)` fără `Intent`.
- **Două lansări simultane cu același launcher**: funcționează, dar callback-ul nu poate distinge care a revenit prima. Pentru cazuri simultane ai nevoie de lansări separate.

**Unde îl vezi în G1097**

Declararea câmpului și înregistrarea, la **finalul** lui `onCreate`:

```java
private ActivityResultLauncher<Intent> launcher;

// ... în onCreate, după initControls() și initListeners():
launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
        new ActivityResultCallback<ActivityResult>() {
            @Override
            public void onActivityResult(ActivityResult o) {
                if (o.getResultCode() == RESULT_OK) {
                    Intent intent = o.getData();
                    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
                    int position = intent.getIntExtra(POSITION_EXTRA, -1);
                    if (position == -1) {
                        movies.add(movie);
                        movieAdapter.notifyDataSetChanged();
                    } else {
                        movies.set(position, movie);
                        movieAdapter.notifyDataSetChanged();
                    }
                }
            }
        });
```

Poziția în `onCreate` este semnificativă: `initListeners()` rulează **înainte**, iar listenerii folosesc `launcher`. Nu se rupe nimic pentru că `onClick` nu se execută în `onCreate` — dar dacă cineva ar muta `launcher.launch(...)` direct în `initListeners()`, ar avea `NullPointerException`. Ordinea corectă ar fi inversă, dar codul funcționează prin întârzierea execuției.

Callback-ul este o **clasă anonimă**, nu o lambda, deși `ActivityResultCallback` are o singură metodă. O lambda ar fi fost echivalentă:

```java
launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
        result -> {
            if (result.getResultCode() == RESULT_OK) {
                Intent data = result.getData();
                ...
            }
        });
```

Lansarea, în doi listeneri:

```java
// FAB — insert
fabInsert.setOnClickListener(v -> launcher.launch(new Intent(MainActivity.this, ItemActivity.class)));

// rând — edit
listView.setOnItemClickListener((parent, view, position, id) -> {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
});
```

**Confuzia tipică**

„`registerForActivityResult` poate fi apelat oriunde". Nu — doar înainte de `STARTED`. În practică, în `onCreate`. Într-un listener, aruncă.

A doua: „callback-ul rulează imediat după `launch`". Nu. Rulează când activitatea copil se închide și părintele revine în prim-plan. Între `launch` și callback pot trece secunde sau minute.

A treia: „`ActivityResultLauncher` este doar un wrapper peste `startActivityForResult`". Nu. Este un mecanism nou, cu registry propriu, care supraviețuiește recreării activității. Vechea pereche era bazată pe coduri de cerere și pe un callback unic.

A patra: „un launcher per lansare". Nu — un launcher per **tip de contract**. G1097 are un singur launcher, folosit pentru ambele lansări (insert și edit), pentru că ambele folosesc același contract: `StartActivityForResult`.

---

## Conceptul 37.24 — Gradle: ce face și de ce ai nevoie de dependențe

**Ce este**

Gradle este **sistemul de build** al proiectului Android. El citește fișierele `build.gradle.kts`, descarcă dependențele, compilează codul Java, compilează resursele cu aapt2, transformă bytecode-ul în `classes.dex` cu d8, împachetează totul într-un APK și îl semnează. Fără el ai avea de rulat manual șapte instrumente, în ordinea corectă, cu parametrii corecți.

**De ce există**

Pentru că un build Android are **mult mai multe etape** decât un `javac`. Trebuie să compilezi resurse, să generezi `R.java`, să mergi manifestele din librării cu al tău, să convertești bytecode Java în formatul Dalvik, să împachetezi totul într-o arhivă, să o semnezi. Și trebuie să o faci la fel pe mașina ta și pe cea a colegului. Gradle face asta **declarativ**: tu descrii ce vrei, el decide cum.

Al doilea rol, la fel de important: **dependențele**. `AppCompatActivity`, `MaterialCardView`, `RecyclerView` nu sunt în Android SDK — sunt librării `androidx` și Material, descărcate de Gradle din depozite Maven și puse pe classpath-ul compilării și în APK.

**Cum funcționează**

Pipeline-ul complet, declanșat de un singur buton:

```
build.gradle.kts + settings.gradle.kts + gradle/libs.versions.toml
        |
        v
1. CONFIGURARE
     - citește plugin-urile (com.android.application, versiunea din catalog)
     - citește blocul `android { }`: namespace, sdk-uri, buildFeatures
     - rezolvă dependențele din `dependencies { }` (descarcă .aar / .jar)

2. COMPILARE RESURSE
     res/ + AndroidManifest.xml --aapt2--> resurse binare + R.java + resources.arsc

3. COMPILARE COD
     .java --javac--> .class --d8--> classes.dex

4. ÎMPACHETARE
     classes.dex + res/ + resources.arsc + manifest binar --zip--> APK

5. SEMNARE
     APK --apksigner--> APK semnat (debug sau release)

6. INSTALARE (opțional, din Android Studio)
     adb install app-debug.apk
```

Structura fișierelor dintr-un proiect Android, cu rolul fiecăruia:

| Fișier | Rol |
|---|---|
| `settings.gradle.kts` | ce module are proiectul și din ce depozite se descarcă |
| `build.gradle.kts` (rădăcină) | plugin-uri comune, aplicate cu `apply false` |
| `build.gradle.kts` (modul) | configurația modulului: `namespace`, SDK-uri, dependențe |
| `gradle/libs.versions.toml` | catalogul de versiuni — un singur loc pentru toate numerele |
| `gradle.properties` | setări Gradle (memorie JVM, configuration cache) |

Tipurile de dependență, care se confundă:

| Configurație | Ajunge în APK? | Vizibilă la compilare? | Pentru ce |
|---|---|---|---|
| `implementation` | da | da, doar în modul | librării de runtime |
| `api` | da | da, și în modulele care depind de tine | doar în librării |
| `compileOnly` | nu | da | adnotări, API-uri furnizate de platformă |
| `testImplementation` | nu | doar în testele JVM | JUnit |
| `androidTestImplementation` | nu (APK separat) | doar în testele instrumentate | Espresso |

**Ce se rupe fără el**

- **Dependență lipsă**: la compilare, `cannot find symbol: class RecyclerView`. La runtime, dacă ai reușit să compilezi cu `compileOnly`, `NoClassDefFoundError`.
- **Versiune incompatibilă**: `Manifest merger failed` sau, mai rău, un crash la runtime din cauza unei metode care nu există în versiunea încărcată.
- **`minSdk` prea mic pentru o librărie**: `uses-sdk:minSdkVersion 21 cannot be smaller than version 24 declared in library`. Build-ul cade, cu mesaj clar.
- **Sync eșuat**: `R` nu se generează, deci `Cannot resolve symbol R` peste tot. Simptomul e înșelător — pare o problemă de cod, de fapt e o problemă de build.
- **`namespace` diferit de pachetul din `AndroidManifest.xml`**: build-ul cade cu `Namespace not specified` sau, în versiuni mai vechi, `R` se generează în alt pachet decât îl importi.

**Unde îl vezi în G1097**

`cod-final/build.gradle.kts` — tot ce contează, în 44 de linii:

```kotlin
plugins {
    alias(libs.plugins.android.application)     // plugin-ul, cu versiunea din catalog
}

android {
    namespace = "ro.ase.ie.g1097"
    compileSdk {
        version = release(37)                    // sintaxa nouă AGP
    }

    defaultConfig {
        applicationId = "ro.ase.ie.g1097"
        minSdk = 33
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures { viewBinding = true }         // generează clasele de binding (vezi 37.9)

    buildTypes {
        release {
            optimization { enable = false }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.activity.ktx)            // EdgeToEdge, registerForActivityResult
    implementation(libs.appcompat)               // AppCompatActivity
    implementation(libs.constraintlayout)        // ConstraintLayout
    implementation(libs.material)                // MaterialCardView, Chip, MaterialSwitch
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}
```

Fiecare dependență are un motiv verificabil în cod:

| Dependență | De unde vine importul | Ce ar lipsi |
|---|---|---|
| `activity-ktx` | `androidx.activity.EdgeToEdge`, `androidx.activity.result.*` | `EdgeToEdge.enable(this)`, `ActivityResultLauncher` |
| `appcompat` | `androidx.appcompat.app.AppCompatActivity` | clasa de bază a ambelor activități |
| `constraintlayout` | `androidx.constraintlayout.widget.ConstraintLayout` | folosit în `DMA02`, nu în G1097 |
| `material` | `com.google.android.material.*` | FAB, `MaterialCardView`, `TextInputLayout`, `Chip`, `MaterialSwitch` |

Ultimul rând este cel mai instructiv: `constraintlayout` este declarat dar **nefolosit** în G1097. Dependența nu strică nimic, doar adaugă mărime APK-ului. Este un exemplu de „dependență moștenită din șablon".

`settings.gradle.kts` — un proiect cu opt module:

```kotlin
rootProject.name = "DMA2026"
include(":G1096")
include(":G1097")
include(":G1098")
include(":G1099")
include(":DMA02")
include(":DMA03")
include(":DMA05")
include(":DMA06")
```

Fiecare modul are propriul `build.gradle.kts`, cu propriul `namespace` și propriul `applicationId`. De aceea G1097 și G1098 sunt aplicații separate, deși sunt în același proiect — au `applicationId` diferite.

`gradle/libs.versions.toml` — catalogul de versiuni, care ține toate numerele într-un singur loc:

```toml
[versions]
agp = "9.4.1"
appcompat = "1.8.0"
material = "1.14.0"
activityKtx = "1.13.0"
constraintlayout = "2.2.2"

[libraries]
appcompat = { group = "androidx.appcompat", name = "appcompat", version.ref = "appcompat" }
material = { group = "com.google.android.material", name = "material", version.ref = "material" }
activity-ktx = { group = "androidx.activity", name = "activity-ktx", version.ref = "activityKtx" }
constraintlayout = { group = "androidx.constraintlayout", name = "constraintlayout", version.ref = "constraintlayout" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
```

De aici vin `libs.appcompat`, `libs.material`, `libs.plugins.android.application`. Avantajul: o singură versiune pentru toate cele opt module. Dacă actualizezi `material` la `1.15.0`, o faci într-un singur loc.

**Confuzia tipică**

„Gradle descarcă cod în aplicația mea." Nu — descarcă librării pe calculatorul tău, le pune pe classpath la compilare și **împachetează** în APK ce este marcat `implementation`. Nu există cod care „se instalează separat".

A doua: „Sync înseamnă build". Nu. **Sync** citește configurația și rezolvă dependențele — de aceea după sync apar clasele din librării în autocomplete. **Build** compilează și produce APK-ul. Poți avea sync reușit și build eșuat.

A treia: „`namespace` și `applicationId` sunt același lucru". Nu. `namespace` este pachetul în care se generează `R` și `BuildConfig`; `applicationId` este identitatea aplicației pe telefon. Pot fi diferite, și uneori trebuie să fie — de exemplu când ai două variante (demo și plătită) cu același cod.

A patra: „dacă adaug o dependență, trebuie să o și import". Nu — adaugi dependența în `build.gradle.kts`, dai sync, apoi scrii `import`. Dacă uiți sync-ul, importul nu se rezolvă, deși linia din Gradle e corectă.

---

## Harta conceptelor

Tabelul care leagă cele 24 de concepte. Coloana „depinde de" arată ce trebuie să înțelegi înainte; coloana „este folosit de" arată unde se duce ideea mai departe.

| # | Concept | Depinde de | Este folosit de | Întrebarea la care răspunde |
|---|---|---|---|---|
| 37.1 | Aplicația Android | — | toate | „ce se instalează și ce pornește?" |
| 37.2 | `Context` | 37.1 | 37.3, 37.9, 37.13, 37.17 | „de unde iau resursele și serviciile?" |
| 37.3 | Resursele și `R` | 37.2 | 37.4, 37.5, 37.8 | „de unde vine `R.id.etTitle`?" |
| 37.4 | `AndroidManifest.xml` | 37.1 | 37.10, 37.21 | „cine știe că activitatea mea există?" |
| 37.5 | `View` / `ViewGroup` | 37.3 | 37.6, 37.7, 37.8 | „de ce ecranul e un arbore?" |
| 37.6 | measure / layout / draw | 37.5 | 37.7 | „când știu cât de mare e un view?" |
| 37.7 | Layout-urile | 37.5, 37.6 | 37.19 | „de ce arată așa și nu altfel?" |
| 37.8 | `findViewById` | 37.3, 37.5 | 37.9, 37.18 | „cum ajung de la XML la obiect?" |
| 37.9 | ViewBinding | 37.8, 37.24 | 37.14 | „de ce nu `findViewById`?" |
| 37.10 | `Activity` | 37.1, 37.4 | 37.11, 37.21 | „cine creează ecranul?" |
| 37.11 | Ciclul de viață | 37.10 | 37.12, 37.13 | „când rulează codul meu?" |
| 37.12 | Starea | 37.11, 37.22 | 37.16 | „unde salvez ca să nu pierd?" |
| 37.13 | `Application` | 37.2, 37.11 | 37.24 | „unde pun inițializarea globală?" |
| 37.14 | Listeneri | 37.5 | 37.15, 37.23 | „cine îmi cheamă codul la click?" |
| 37.15 | Lambda | 37.14 | 37.23 | „de ce șase linii pentru una?" |
| 37.16 | Modelul / `Serializable` | — | 37.17, 37.22 | „cum trec datele dintr-un ecran în altul?" |
| 37.17 | Adapter | 37.16 | 37.18, 37.20 | „cine spune listei ce să afișeze?" |
| 37.18 | `ViewHolder` / reciclare | 37.17 | 37.19, 37.20 | „de ce nu se creează 1000 de rânduri?" |
| 37.19 | `LayoutManager` | 37.7, 37.18 | 37.20 | „cine decide unde stă fiecare rând?" |
| 37.20 | `ListView` vs `RecyclerView` | 37.17, 37.18, 37.19 | — | „pe care îl aleg?" |
| 37.21 | `Intent` | 37.4, 37.10 | 37.22, 37.23 | „cum cer să se întâmple ceva?" |
| 37.22 | `Bundle` | 37.16, 37.21 | 37.12, 37.23 | „ce poate călători?" |
| 37.23 | `ActivityResultLauncher` | 37.14, 37.21, 37.22 | — | „cum primesc răspuns înapoi?" |
| 37.24 | Gradle | 37.1, 37.9 | toate | „de unde vin clasele care nu sunt în SDK?" |

**Trei lanțuri pe care le poți urmări ca să verifici că ai înțeles capitolul:**

```
Lanțul 1 — de la XML la obiect
  37.3 (aapt2 generează R.id.etTitle)
    -> 37.5 (LayoutInflater construiește arborele)
      -> 37.8 (findViewById caută în arbore)
        -> 37.9 (ViewBinding face căutarea o singură dată, generat)

Lanțul 2 — de la date la ecran
  37.16 (Movie, POJO serializabil)
    -> 37.17 (adapterul citește lista)
      -> 37.18 (ViewHolder cachează view-urile rândului)
        -> 37.19 (LayoutManager decide ce rânduri se văd)
          -> 37.20 (ListView vs RecyclerView: cine face ce)

Lanțul 3 — de la un click la alt ecran
  37.14 (listenerul e apelat de widget)
    -> 37.21 (Intent-ul descrie ce vrei)
      -> 37.22 (Bundle-ul transportă datele)
        -> 37.10 (sistemul creează ItemActivity)
          -> 37.23 (launcher-ul primește rezultatul)
            -> 37.12 (dacă nu salvezi, rotirea pierde tot)
```

**Harta inversă — de la simptom la concept:**

| Simptom | Concepte de citit |
|---|---|
| `NullPointerException` în `initControls` | 37.8, 37.10 |
| Lista e goală, fără eroare | 37.17, 37.18 |
| Filmul nu apare după Save | 37.17, 37.23 |
| Formularul se golește la rotire | 37.11, 37.12 |
| `ActivityNotFoundException` | 37.4, 37.21 |
| `Cannot resolve symbol R` | 37.3, 37.24 |
| `ScrollView can host only one direct child` | 37.5, 37.7 |
| Elementul cu `0dp` a dispărut | 37.6, 37.7 |
| `IllegalStateException` la `registerForActivityResult` | 37.23 |
| `TransactionTooLargeException` | 37.22 |
| `ClassCastException` la `findViewById` | 37.8, 37.9 |
| Rândul arată datele altui element | 37.18 |
| `RecyclerView` nu afișează nimic | 37.19, 37.20 |
| `NotSerializableException` | 37.16, 37.22 |
| Aplicația crapă înainte de primul ecran | 37.1, 37.13 |

---

## Rezumat capitol 37

**Cele șase rubrici, într-o propoziție fiecare:**

1. **Ce este** — definiția, fără jargon.
2. **De ce există** — problema pe care o rezolvă, ce ai face manual fără el.
3. **Cum funcționează** — mecanismul, cu cine pe cine apelează.
4. **Ce se rupe fără el** — eroarea concretă sau comportamentul greșit concret.
5. **Unde îl vezi în G1097** — fișier, metodă, cod real.
6. **Confuzia tipică** — ce se crede greșit, și de ce e greșit.

**Cele 24 de concepte, într-un tabel de memorat:**

| Grup | Concepte | Ideea centrală |
|---|---|---|
| Fundația | 37.1–37.4 | aplicația e un pachet cu UID; `Context` e legătura cu mediul; `R` e un index de resurse; manifestul e contractul cu sistemul |
| Desenarea | 37.5–37.7 | ecranul e un arbore; desenarea are trei passe; fiecare layout are un algoritm |
| Legătura cod–XML | 37.8–37.9 | `findViewById` caută și poate da `null`; ViewBinding leagă la compilare |
| Timpul | 37.10–37.13 | sistemul creează activități; ciclul de viață spune când rulezi; starea are două durate; `Application` rulează o dată |
| Evenimentele | 37.14–37.15 | widget-ul te apelează; o metodă abstractă = lambda |
| Datele | 37.16–37.20 | modelul nu știe UI; adapterul traduce; ViewHolder cachează; LayoutManager aranjează; ListView vs RecyclerView e o alegere |
| Granițele | 37.21–37.24 | `Intent` e mesajul; `Bundle` e plicul; launcher-ul așteaptă răspunsul; Gradle construiește totul |

**Zece propoziții care se cer la test, în forma în care trebuie spuse:**

1. **Aplicația nu are `main()`.** Sistemul o pornește când un `Intent` cere o componentă declarată în manifest, iar procesul poate fi omorât oricând fără ca utilizatorul să închidă nimic.
2. **`Context` este interfața către mediul aplicației, nu aplicația.** Sunt mai multe instanțe în același proces, iar cea de tip `Activity` are temă și fereastră, cea de tip `Application` nu.
3. **`R` conține numere generate la build, nu date.** `R.id.etTitle` există doar dacă aapt2 a rulat, iar valoarea lui nu se persistă niciodată.
4. **Manifestul spune ce există, nu ce face.** Fără `<activity>` nu poți porni ecranul, oricât cod ai scrie.
5. **Ecranul este un arbore, iar desenarea îl parcurge de trei ori:** measure, layout, draw. De aceea `getWidth()` în `onCreate` este 0.
6. **`findViewById` poate întoarce `null` și nu verifică tipul.** ViewBinding mută ambele verificări la compilare, pentru că generează câmpuri din același XML.
7. **Activitatea o creează sistemul, prin reflecție, cu constructor fără parametri.** `new MainActivity()` compilează și este complet nefuncțional.
8. **`onDestroy` nu rulează când sistemul omoară procesul.** De aceea salvarea se face în `onSaveInstanceState`, nu în `onDestroy`.
9. **Adapterul este chemat de widget, nu de tine.** Tu îl setezi o dată; `ListView` îl întreabă `getCount()` și `getView()` pentru fiecare rând vizibil.
10. **Obiectul care călătorește prin `Intent` este o copie.** De aceea editarea trimite înapoi un obiect nou și părintele face `movies.set(position, movie)`.

**Trei lucruri pe care G1097 nu le are, și de ce contează:**

| Lipsește | Consecința | Unde e exemplul |
|---|---|---|
| `onSaveInstanceState` | formularul se golește la rotire; lista se resetează la cele trei filme de start | 37.12 |
| clasă `Application` | nu există loc pentru inițializare globală; manifestul nu are `android:name` | `DMA02` |
| `RecyclerView` | lista e limitată la `ArrayAdapter` cu un singur text per rând | `DMA06` |

**Ce urmează:** dacă vrei să aplici ce ai înțeles aici, capitolul 33–35 îți dă rețetele, capitolul 21 îți dă memento-ul, iar capitolul 36 îți dă exercițiile de tip examen. Capitolul acesta rămâne cel la care te întorci când întrebarea începe cu „de ce".
