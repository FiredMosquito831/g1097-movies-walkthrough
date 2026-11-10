# Capitolul 01 — Setup și scheletul proiectului

**Obiectiv:** la finalul acestui capitol ai un proiect Android care compilează și afișează un ecran gol, cu tema Material 3, fără ActionBar, și cu `minSdk 33`.

**Timp estimat:** 25–40 min (prima dată).

---

## Pasul 1.1 — Creează proiectul

### De ce

Un proiect Android nu e „un fișier”. E un **proiect Gradle** — un folder cu o rețetă de build. Gradle citește rețeta, descarcă bibliotecile, compilează Java-ul, împachetează resursele XML și produce un `.apk`. Android Studio nu compilează nimic singur; el cheamă Gradle.

De asta, când ceva nu merge, prima întrebare e mereu: *ce a spus Gradle?*

### Cum

1. Android Studio → **File → New → New Project**.
2. Șablon: **Empty Views Activity** (NU „Empty Activity” — acela e pentru Compose).
3. Completează:

| Câmp | Valoare | De ce |
|---|---|---|
| Name | `Movies1097` | numele aplicației, apare sub iconiță |
| Package name | `ro.ase.ie.g1097` | **exact** asta; toate importurile din cod depind de el |
| Save location | `.../Exams and tests/test 1/_progres/` | nu în `cod-final/`, nu în `dma2026/` |
| Language | **Java** | proiectul e în Java, nu Kotlin |
| Minimum SDK | **API 33 ("Tiramisu")** | `minSdk = 33` în repo |
| Build configuration language | **Kotlin DSL** | fișierele sunt `build.gradle.kts` |

4. **Finish**. Așteaptă „Gradle sync finished”.

### Verifică

În `app/build.gradle.kts` trebuie să vezi `minSdk = 33`. Dacă ai pus altceva, schimbă acum — nu mai târziu.

> **Atenție:** dacă `compileSdk` propus de Studio e mai mic decât 33, `minSdk 33` dă eroare. `compileSdk` trebuie să fie ≥ `minSdk`.

---

## Pasul 1.2 — Înțelege structura de foldere

### De ce

Android are **două lumi** care se compilează împreună:

- **cod** (`java/`) — ce *face* aplicația;
- **resurse** (`res/`) — ce *arată* aplicația: layout-uri, texte, culori, imagini.

Resursele nu sunt citite la runtime din fișiere. Sunt **compilate** în `R.java`, o clasă generată automat care dă un `int` fiecărei resurse. De asta scrii `R.layout.activity_main` — e un `int`, nu un string.

### Cum

Structura pe care o vei avea:

```
app/
  src/main/
    AndroidManifest.xml          ← „buletinul” aplicației
    java/ro/ase/ie/g1097/
      MainActivity.java          ← ecranul principal
    res/
      layout/                    ← XML-uri de ecran
      values/                    ← strings, colors, themes
      values-night/              ← tema pentru dark mode
      drawable/                  ← imagini vectoriale
      mipmap-*/                  ← iconițele aplicației
```

### Verifică

Deschide `res/values/strings.xml`. Trebuie să conțină `app_name`. Deschide `MainActivity.java` — trebuie să fie în pachetul `ro.ase.ie.g1097`.

> Dacă pachetul tău e `ro.ase.ie.g1097` dar clasa e în alt subpachet, mută-o: click dreapta pe fișier → **Refactor → Move**.

---

## Pasul 1.3 — `build.gradle.kts` al modulului

### De ce

Acesta e fișierul care spune lui Gradle **ce SDK**, **ce biblioteci** și **ce opțiuni de compilare** folosește modulul `app`. Fiecare linie are un efect direct asupra codului pe care îl scrii.

### Cum

Deschide `app/build.gradle.kts`. Compară cu ce trebuie să ai. **Nu copia orbește** — dacă versiunile tale sunt mai noi, e în regulă; verifică doar că *structura* e aceeași.

```kotlin
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "ro.ase.ie.g1097"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "ro.ase.ie.g1097"
        minSdk = 33
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures { viewBinding = true }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.activity.ktx)
    implementation(libs.appcompat)
    implementation(libs.constraintlayout)
    implementation(libs.material)
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}
```

### Explicație linie cu linie

| Linie | Ce face | De ce contează pentru tine |
|---|---|---|
| `namespace` | pachetul în care se generează `R` | dacă îl schimbi, toate `import ro.ase.ie.g1097.R` se strică |
| `applicationId` | ID-ul din Play Store / din telefon | două aplicații cu același ID se suprascriu |
| `minSdk = 33` | cea mai veche versiune Android pe care rulează | sub 33, unele API-uri folosite aici nu există |
| `targetSdk = 37` | pentru ce versiune e optimizată | influențează comportamentul la runtime |
| `buildFeatures { viewBinding = true }` | generează clase `ActivityMainBinding` etc. | **activat, dar codul nu îl folosește** — vezi cap. 07, pasul 7.2 |
| `optimization { enable = false }` | dezactivează R8 în release | altfel codul ar fi minificat și numele claselor schimbate |
| `VERSION_11` | nivelul de limbaj Java | dacă pui 8, nu poți folosi `var`, lambda-uri noi etc. |
| `implementation(libs.material)` | Material Components | **obligatoriu** pentru `MaterialCardView`, `MaterialSwitch`, `Chip`, `MaterialButton` |

### Verifică

**Build → Make Project** (Ctrl+F9). Trebuie să scrie `BUILD SUCCESSFUL`.

> **Eroare frecventă:** `Unresolved reference: libs`. Înseamnă că `gradle/libs.versions.toml` nu e sincronizat. **File → Sync Project with Gradle Files**.

---

## Pasul 1.4 — `libs.versions.toml`

### De ce

Android Studio modern ține versiunile bibliotecilor într-un **version catalog**: un fișier TOML unde definești o dată versiunea, apoi o referențiezi cu `libs.nume`. Avantajul: o singură sursă de adevăr pentru versiuni, în tot proiectul.

### Cum

Deschide `gradle/libs.versions.toml`. Conținutul din repo:

```toml
[versions]
agp = "9.4.1"
junit = "4.13.2"
junitVersion = "1.3.0"
espressoCore = "3.7.0"
appcompat = "1.8.0"
material = "1.14.0"
activityKtx = "1.13.0"
constraintlayout = "2.2.2"
coordinatorlayout = "1.3.0"

[libraries]
junit = { group = "junit", name = "junit", version.ref = "junit" }
ext-junit = { group = "androidx.test.ext", name = "junit", version.ref = "junitVersion" }
espresso-core = { group = "androidx.test.espresso", name = "espresso-core", version.ref = "espressoCore" }
appcompat = { group = "androidx.appcompat", name = "appcompat", version.ref = "appcompat" }
material = { group = "com.google.android.material", name = "material", version.ref = "material" }
activity-ktx = { group = "androidx.activity", name = "activity-ktx", version.ref = "activityKtx" }
constraintlayout = { group = "androidx.constraintlayout", name = "constraintlayout", version.ref = "constraintlayout" }
coordinatorlayout = { group = "androidx.coordinatorlayout", name = "coordinatorlayout", version.ref = "coordinatorlayout" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
```

### Exercițiu 1.4

**Cerință:** adaugă în catalog o intrare pentru `androidx.recyclerview:recyclerview:1.4.0`, cu numele `recyclerview`. Nu o folosi încă — doar definește-o.

<details>
<summary>Indiciu</summary>

Ai nevoie de două lucruri: o intrare în `[versions]` (ex. `recyclerview = "1.4.0"`) și una în `[libraries]` care o referențiează cu `version.ref`.

</details>

<details>
<summary>Soluție</summary>

**Ce s-a făcut:** ai adăugat o **intrare de catalog** — o declarație de versiune și o referință de bibliotecă. Nu ai adăugat încă biblioteca în build.

```toml
[versions]
# ... existente ...
recyclerview = "1.4.0"

[libraries]
# ... existente ...
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

**Cum funcționează:** `[versions]` ține **numărul** versiunii sub un nume. `[libraries]` ține **coordonatele** Maven (`group:name:version`) și leagă versiunea prin `version.ref`. Când scrii `libs.recyclerview` în `build.gradle.kts`, Gradle rezolvă lanțul: `libs.recyclerview` → `androidx.recyclerview:recyclerview:1.4.0`.

**De ce două intrări și nu una:** dacă ai scrie versiunea direct în `[libraries]`, ai repeta-o la fiecare bibliotecă din același grup. Cu `version.ref`, o schimbi într-un singur loc — toate cele care o referă se actualizează.

**De reținut:**
1. Catalogul e **declarativ**. Nu descarcă nimic. Descărcarea se face când biblioteca apare în `dependencies { }`.
2. `Sync Project with Gradle Files` regenerează accesorii `libs.*`. Fără sync, Android Studio nu vede intrarea nouă.
3. Numele din `[libraries]` cu cratime (`activity-ktx`) devine `libs.activity.ktx` — punct, nu cratimă. TOML normalizează.

**Unde revine:** în capitolul 11 (pasul 11.4), adaugi `implementation(libs.recyclerview)` în `dependencies`. Abia atunci biblioteca e descărcată și `RecyclerView` devine disponibil în cod. Aceeași intrare, dar folosită.

</details>

---

## Pasul 1.5 — `AndroidManifest.xml`

### De ce

Manifestul e **singurul fișier pe care Android îl citește înainte să pornească orice cod**. El spune sistemului:

- ce activități există și care e prima;
- ce permisiuni cere aplicația;
- ce temă are;
- ce iconiță are.

Fără o activitate marcată cu `MAIN` + `LAUNCHER`, aplicația nu apare în launcher.

### Cum

Deschide `app/src/main/AndroidManifest.xml`. Ținta finală:

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

</manifest>
```

> **Nu ai încă `ItemActivity`.** Deocamdată declară doar `MainActivity`. A doua activitate o adaugi la pasul 7.1, când o creezi. Dacă o declari acum, build-ul eșuează cu „class not found”.

### Explicație

| Atribut | Sens |
|---|---|
| `android:name=".activities.MainActivity"` | punctul de la început = pachetul `namespace` + restul. Deci `ro.ase.ie.g1097.activities.MainActivity` |
| `android:exported="true"` | obligatoriu pentru activitatea de launcher; fără el, Android 12+ refuză instalarea |
| `android:exported="false"` | `ItemActivity` e pornită doar din interiorul aplicației |
| `windowSoftInputMode="adjustResize"` | când apare tastatura, layout-ul se micșorează, nu se acoperă |
| `android:theme="@style/Theme.G1097"` | tema se aplică întregii aplicații |

> **Atenție la `.activities.`** — în repo, activitățile stau în subpachetul `activities`. Dacă la pasul 1.1 ai lăsat `MainActivity` în pachetul rădăcină, ai două opțiuni: (a) muți clasa în `activities` (recomandat, e structura repo-ului), sau (b) scrii `android:name=".MainActivity"`. **Alege (a)** — restul materialului presupune `ro.ase.ie.g1097.activities`.

### Exercițiu 1.5

**Cerință:** mută `MainActivity` în subpachetul `activities` și actualizează manifestul. Rulează aplicația — trebuie să pornească în continuare.

<details>
<summary>Indiciu</summary>

Click dreapta pe `MainActivity.java` → **Refactor → Move** → alege `ro.ase.ie.g1097.activities`. Android Studio actualizează singur `package` din fișier și manifestul.

</details>

<details>
<summary>Soluție</summary>

```java
package ro.ase.ie.g1097.activities;
```

și în manifest:

```xml
android:name=".activities.MainActivity"
```

**Ce s-a făcut:** ai mutat clasa `MainActivity` din pachetul rădăcină `ro.ase.ie.g1097` în subpachetul `ro.ase.ie.g1097.activities`, și ai actualizat referința din manifest.

**Cum funcționează:** `package` din fișierul `.java` **este** poziția clasei în ierarhia de pachete — nu e doar o etichetă. Când mutat fișierul în folderul `activities/`, trebuie să declari și `package ro.ase.ie.g1097.activities;` ca să corespundă. Manifestul folosește **calea relativă** la `namespace`: `.activities.MainActivity` = `ro.ase.ie.g1097` + `.activities.MainActivity`.

**De ce contează:** `android:name` din manifest e rezolvat de `PackageManager` la instalare. Dacă numele nu corespunde unei clase reale, aplicația crăpă la pornire cu `ClassNotFoundException` — nu la compilare.

**De reținut:**
1. **Pachetul și folderul trebuie să corespundă.** Java permite să nu corespundă (compilatorul nu verifică), dar uneltele (Android Studio, Gradle, manifestul) se bazează pe corespondență.
2. `Refactor → Move` face **trei** lucruri deodată: mută fișierul, schimbă `package`, actualizează toate referințele (inclusiv manifestul).
3. Dacă muți manual (drag & drop), trebuie să faci tu toate trei.

**Unde revine:** în capitolul 07 (pasul 7.1), `ItemActivity` se creează direct în `activities`. Și în capitolul 08 (pasul 8.3), discuția despre `protected` depinde de faptul că ambele activități sunt în **același pachet**.

</details>

---

## Pasul 1.6 — Tema Material 3, fără ActionBar

### De ce

Tema decide **tot** aspectul: culori, tipografie, forme, umbre. Repo-ul folosește `Theme.Material3.DayNight.NoActionBar`:

- **Material3** → componentele Material pe care le vei folosi au stilul corect;
- **DayNight** → comută automat între light și dark după setarea telefonului;
- **NoActionBar** → fără bara de titlu implicită; ecranele își desenează singure conținutul de sus.

`NoActionBar` e important: `activity_item.xml` începe direct cu un `ScrollView` care are `android:id="@+id/main"` și padding din insets. Dacă ar exista ActionBar, conținutul ar fi împins în jos și padding-ul ar ieși greșit.

### Cum

`res/values/themes.xml`:

```xml
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Base.Theme.G1097" parent="Theme.Material3.DayNight.NoActionBar">
        <!-- Customize your light theme here. -->
    </style>

    <style name="Theme.G1097" parent="Base.Theme.G1097" />
</resources>
```

`res/values-night/themes.xml`:

```xml
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Base.Theme.G1097" parent="Theme.Material3.DayNight.NoActionBar">
        <!-- Customize your dark theme here. -->
    </style>
</resources>
```

### De ce două fișiere?

`values-night/` e citit **doar** când telefonul e pe dark mode. Android suprapune resursele: întâi ia `values/`, apoi, dacă există și e night mode, suprascrie cu `values-night/`.

De asta `Base.Theme.G1097` e definit în **ambele** — poți personaliza separat culorile light și dark. `Theme.G1097` e definit doar în `values/`, pentru că moștenește din `Base.Theme.G1097` și va lua automat versiunea corectă.

> Dacă ai numele altfel (ex. `Theme.Movies1097`), folosește-l consecvent: în `themes.xml` **și** în `AndroidManifest.xml`. Un nume greșit = `Resources$NotFoundException` la pornire.

### Exercițiu 1.6

**Cerință:** schimbă `colorPrimary` în tema light la un albastru închis (`#1565C0`) și verifică pe emulator că butoanele viitoare îl folosesc. Apoi comută telefonul pe dark mode și observă ce se întâmplă.

<details>
<summary>Indiciu</summary>

Adaugă `<item name="colorPrimary">#1565C0</item>` în `Base.Theme.G1097` din `values/themes.xml`. Pentru a vedea efectul ai nevoie de o componentă care folosește `colorPrimary` — deocamdată nu ai. **Revino la acest exercițiu după capitolul 03.**

</details>

<details>
<summary>Soluție</summary>

```xml
<style name="Base.Theme.G1097" parent="Theme.Material3.DayNight.NoActionBar">
    <item name="colorPrimary">#1565C0</item>
</style>
```

**Ce s-a făcut:** ai adăugat un `<item>` în stilul de bază, care **suprascrie** `colorPrimary` moștenit din `Theme.Material3.DayNight.NoActionBar`.

**Cum funcționează:** un `<style>` cu `parent` **moștenește** toate atributele părintelui, apoi le poate suprascrie pe cele declarate. Deci `Base.Theme.G1097` are toate culorile Material 3, mai puțin `colorPrimary`, care e albastru închis.

**De ce nu se vede încă nimic:** nicio componentă din ecranul „Hello World” nu folosește `colorPrimary`. `TextView`-ul folosește `textColor` (care e `colorOnSurface`), nu `colorPrimary`. Deci schimbarea e **inertă** până apare un FAB, un `MaterialButton`, un titlu de card etc.

**De reținut:**
1. **Moștenirea de stiluri** e lanțul: `Theme.G1097` → `Base.Theme.G1097` → `Theme.Material3.DayNight.NoActionBar` → … → `Theme.MaterialComponents`.
2. `values-night/themes.xml` **suprascrie** `Base.Theme.G1097` doar când e dark mode. Dacă nu pui `<item>` acolo, culoarea din `values/` rămâne.
3. Un atribut de temă se referă cu `?attr/nume` în layout, `?attr/` în XML, `MaterialColors.getColor(view, R.attr.nume)` în cod.

**Unde revine:** în capitolul 03, FAB-ul folosește `colorPrimaryContainer` ca fundal. În capitolul 06, `MaterialButton` filled folosește `colorPrimary`. Abia acolo vezi albastrul.

</details>

---

## Pasul 1.7 — `strings.xml`

### De ce

Textele nu se scriu direct în layout. Se pun în `strings.xml` și se referă cu `@string/nume`. Trei motive:

1. **Traducere** — adaugi `values-ro/strings.xml` și ai aplicația în română, fără să atingi layout-ul.
2. **Un singur loc de schimbat** — redenumești aplicația dintr-un loc.
3. **Erori de lint evitate** — Android Studio te avertizează dacă hardcodezi texte.

> **Excepție asumată în repo:** multe texte din `activity_item.xml` sunt scrise direct (`android:text="Movie details"`). E o alegere a profesorului pentru lizibilitate la laborator. În codul tău poți face la fel, dar **știi de ce** o faci.

### Cum

`res/values/strings.xml`:

```xml
<resources>
    <string name="app_name">G1097</string>

    <string-array name="items">
        <item>Item 1</item>
        <item>Item 2</item>
        <!-- ... până la Item 20 ... -->
    </string-array>

    <string-array name="movie_genre">
        <item>Drama</item>
        <item>Action</item>
        <item>Comedy</item>
        <item>Horror</item>
        <item>Romance</item>
        <item>Thriller</item>
        <item>Sci-Fi</item>
        <item>Adventure</item>
        <item>Fantasy</item>
        <item>Mystery</item>
    </string-array>
</resources>
```

### Ce sunt cele două array-uri

- **`items`** — 20 de rânduri „Item 1” … „Item 20”. Sunt **demo**, folosite de `ListView` prin `android:entries="@array/items"` în `activity_main.xml`. Nu vin din cod. Le vei înlocui cu filmele reale la capitolul 04.
- **`movie_genre`** — cele 10 genuri, folosite de `Spinner` prin `android:entries="@array/movie_genre"`. Acestea **rămân** — sunt lista reală de genuri din formular.

### Exercițiu 1.7

**Cerință:** adaugă în `movie_genre` genul `Documentary`, pe poziția a 3-a (adică între `Action` și `Comedy`). Ce se întâmplă cu un film care avea genul `Comedy` salvat înainte?

<details>
<summary>Indiciu</summary>

Gândește-te cum găsește `fillForm` genul: compară **textul**, nu indexul. Vezi `ItemActivity.fillForm`, bucla `for(int index=0; index<spGenre.getCount(); index++)`.

</details>

<details>
<summary>Soluție</summary>

```xml
<string-array name="movie_genre">
    <item>Drama</item>
    <item>Action</item>
    <item>Documentary</item>
    <item>Comedy</item>
    <!-- ... -->
</string-array>
```

Filmul cu genul `Comedy` **rămâne corect**: `fillForm` caută după text (`spGenre.getItemAtPosition(index).equals(existing.getGenre())`), nu după poziție. Deci inserezi oriunde, fără să strici datele.

**Ce s-a făcut:** ai adăugat un element în `movie_genre` **în mijlocul** array-ului, nu la final. Toate genurile de după își schimbă indexul cu +1.

**Cum se vede:** în `Spinner`, ordinea opțiunilor se schimbă. `Documentary` apare pe poziția 3. Dar un film salvat cu `genre = "Comedy"` continuă să se găsească corect la editare.

**De ce:** `Movie.genre` e un `String` („Comedy”), nu un index. `fillForm` **caută** textul în listă și abia apoi calculează indexul:

```java
for (int index = 0; index < spGenre.getCount(); index++) {
    if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
        spGenre.setSelection(index);
        break;
    }
}
```

Deci indexul e **derivat** din text, nu stocat.

**De reținut:**
1. **Salvează valoarea, nu poziția.** O poziție într-o listă care se poate schimba e o referință fragilă.
2. Dacă `Movie` ar fi avut `int genreIndex`, inserarea ar fi stricat toate filmele de după poziția 2.
3. Același principiu la `RadioGroup`: se salvează **textul** butonului („PG-13”), nu indexul lui.

**Unde revine:** în capitolul 09 (pasul 9.2), bucla de căutare din `fillForm` e exact mecanismul care face posibilă inserarea. Și în capitolul 11 (pasul 11.13), `DiffUtil.areItemsTheSame` are aceeași problemă: fără un `id` stabil, se bazează pe titlu.

</details>

---

## Pasul 1.8 — `colors.xml` și drawable-ul vectorial

### De ce

`colors.xml` din repo conține doar negru și alb — restul culorilor vin din tema Material. Le păstrezi pentru că șablonul le referă.

`outline_add_24.xml` e o **iconiță vectorială** (un `VectorDrawable`): un plus, desenat cu un `pathData` SVG. Se folosește ca iconiță a butonului flotant. Avantajul față de un PNG: se scalează perfect la orice densitate, fără fișiere multiple.

### Cum

`res/values/colors.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
```

`res/drawable/outline_add_24.xml`:

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:height="24dp"
    android:tint="#000000"
    android:viewportHeight="960"
    android:viewportWidth="960"
    android:width="24dp">

    <path android:fillColor="@android:color/white"
        android:pathData="M440,520L200,520L200,440L440,440L440,200L520,200L520,440L760,440L760,520L520,520L520,760L440,760L440,520Z" />
</vector>
```

### Cum citești `pathData`

`M440,520` = **M**ove to (440, 520). `L200,520` = **L**ine to (200, 520). Literele mari înseamnă coordonate absolute, cele mici relative.

Desenează un plus: pornești din (440,520), mergi la stânga la (200,520), în sus la (200,440), la dreapta la (440,440)... și tot așa, până închizi forma. Sistemul de coordonate e 960×960 (`viewport`), dar iconița se afișează la 24dp (`width`/`height`).

> **Nu trebuie să desenezi tu path-uri.** Android Studio are **File → New → Vector Asset** cu iconițe Material gata făcute. Dar trebuie să știi ce e un `VectorDrawable`, pentru că la test poate fi întrebare.

### Exercițiu 1.8

**Cerință:** creează un `VectorDrawable` numit `ic_delete_24.xml` care desenează o linie diagonală (un „X” simplificat). Folosește `File → New → Vector Asset → Clip Art → Delete`.

<details>
<summary>Indiciu</summary>

Dacă folosești Vector Asset, Android Studio scrie path-ul singur. Verifică apoi că fișierul e în `res/drawable/` și că poți referi `@drawable/ic_delete_24` dintr-un layout.

</details>

<details>
<summary>Soluție</summary>

Fișierul generat arată similar cu:

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal">
    <path android:fillColor="@android:color/white"
        android:pathData="M6,19c0,1.1 0.9,2 2,2h8c1.1,0 2,-0.9 2,-2V7H6v12zM19,4h-3.5l-1,-1h-5l-1,1H5v2h14V4z" />
</vector>
```

Observă `viewportWidth="24"` — alt sistem de coordonate decât la plus (960). Ambele sunt valide; viewport-ul e doar spațiul în care sunt exprimate coordonatele.

**Ce s-a făcut:** ai generat un `VectorDrawable` cu un path SVG care desenează forma „Delete” (un coș de gunoi), folosind Vector Asset Studio.

**Cum funcționează un `VectorDrawable`:** path-ul e o **secvență de comenzi** într-un sistem de coordonate propriu (`viewportWidth` × `viewportHeight`). Comenzile sunt litere:

| Litera | Sens |
|---|---|
| `M x,y` | **M**ove to — mută „penița” la (x, y) fără să deseneze |
| `L x,y` | **L**ine to — desenează o linie la (x, y) |
| `H x` | **H**orizontal line to — linie orizontală la x |
| `V y` | **V**ertical line to — linie verticală la y |
| `C` / `S` | **C**ubic / **S**mooth curve — curbe Bézier |
| `Z` | **Z** — închide forma (linie înapoi la punctul de start) |

Literele mari = coordonate **absolute**; literele mici = **relative** la poziția curentă.

**De ce `24` la Vector Asset și `960` la plus:** `viewport` e doar spațiul de coordonate, nu dimensiunea finală. `android:width="24dp"` e dimensiunea afișată. Un path exprimat în 960×960 se scalează la 24dp la fel de bine ca unul în 24×24 — doar coordonatele diferă.

**De reținut:**
1. **`VectorDrawable` = imagine vectorială**, nu bitmap. Se scalează fără pierdere, un singur fișier pentru toate densitățile.
2. `android:tint="?attr/colorControlNormal"` permite **recolorarea** din temă — de aceea iconița se adaptează la dark mode.
3. Nu trebuie să scrii path-uri de mână. Vector Asset Studio are mii de iconițe Material.

**Unde revine:** în capitolul 11 (pasul 11.11), adaugi un `ImageButton` cu `@android:drawable/ic_menu_delete` — o iconiță **din sistem**, nu un vector propriu. Diferența: `@android:drawable/` = resursă Android, `@drawable/` = resursă a proiectului tău.

</details>

---

## Pasul 1.9 — `.gitignore`

### De ce

Folderul `build/` conține output-ul compilării: sute de MB, regenerabile, diferite la fiecare mașină. Nu se pune în git.

### Cum

`app/.gitignore`:

```
/build
```

Simplu. În repo, modulul G1097 are exact atât. Rădăcina are un `.gitignore` mai mare (cu `.gradle`, `.idea`, `local.properties`), dar pentru tine, în `_progres/`, nu contează — nu faci commit.

---

## Pasul 1.10 — Primul run

### De ce

Până nu rulează, nu ai dovada că setup-ul e corect. Nu trece la capitolul 02 până nu vezi aplicația pe emulator.

### Cum

1. **Device Manager** → creează un emulator dacă nu ai: **Pixel 7, API 34 sau 35** (orice ≥ 33).
2. Apasă **Run ▶** (Shift+F10).
3. Așteaptă: prima compilare poate dura 2–5 minute.

### Verifică

- Aplicația apare în launcher cu numele `G1097` (sau `Movies1097`).
- La deschidere vezi „Hello World!” centrat.
- În `Logcat` nu sunt linii roșii `FATAL EXCEPTION`.

### Exercițiu 1.10 — capcană

**Cerință:** deschide `Logcat`, filtrează după `package:mine`, închide aplicația din recents și redeschide-o. Găsește linia care confirmă că `MainActivity` a fost creată.

<details>
<summary>Indiciu</summary>

Caută `Displayed ro.ase.ie.g1097/.activities.MainActivity` sau `START u0 {act=android.intent.action.MAIN ...}`.

</details>

<details>
<summary>Soluție</summary>

În Logcat vei vedea ceva de forma:

```
ActivityTaskManager: START u0 {act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] flg=0x10200000 cmp=ro.ase.ie.g1097/.activities.MainActivity} 
ActivityTaskManager: Displayed ro.ase.ie.g1097/.activities.MainActivity: +412ms
```

Asta îți spune două lucruri: (1) manifestul e corect, (2) cât a durat pornirea. Dacă vezi `Unable to instantiate activity`, manifestul are numele greșit.

**Ce s-a făcut:** ai filtrat Logcat după `package:mine` și ai găsit linia care confirmă crearea activității.

**Cum funcționează filtrul:** `package:mine` e un filtru Logcat care arată doar mesajele de la procesele aplicației tale. Fără el, Logcat e un flux de mii de linii de la tot sistemul.

**De ce `START u0 {cmp=ro.ase.ie.g1097/.activities.MainActivity}` e dovada:** `cmp` = component. Formatul e `package/clasă-relativă-la-package`. Deci `ro.ase.ie.g1097` + `.activities.MainActivity` = exact ce ai declarat în manifest. Dacă ar fi greșit, ai vedea `ActivityNotFoundException` sau `Unable to instantiate`.

**De reținut:**
1. **Logcat e unealta principală de debugging.** `package:mine` e primul filtru pe care îl pui.
2. `Displayed ... +412ms` îți spune timpul de pornire — util pentru performanță.
3. Nivelurile: `V` (verbose), `D` (debug), `I` (info), `W` (warning), `E` (error), `F` (fatal). `FATAL EXCEPTION` = crash.
4. Un crash nu se vede „pe ecran” — se vede **doar** în Logcat.

**Unde revine:** la fiecare pas din capitolele următoare, când ceva nu merge. `NullPointerException` și `NumberFormatException` se citesc în Logcat, nu se ghicesc.

</details>

---

## Rezumat capitol 01

Ai acum:

- un proiect Gradle care compilează;
- `minSdk 33`, Java 11, Material 3, `NoActionBar`;
- un `MainActivity` în `ro.ase.ie.g1097.activities`, declarat în manifest;
- `strings.xml` cu `items` (20) și `movie_genre` (10);
- `outline_add_24.xml`;
- tema `Theme.G1097` cu variantă de noapte.

**Nu ai încă:** nicio clasă `Movie`, niciun layout propriu, nicio logică.

### Autoverificare (fără să te uiți)

1. De ce `android:exported="true"` e obligatoriu pe `MainActivity`?
2. Ce se întâmplă dacă `namespace` diferă de `applicationId`?
3. De ce `values-night/themes.xml` nu conține și `Theme.G1097`?
4. Ce face `buildFeatures { viewBinding = true }` și de ce codul actual nu-l folosește?

<details>
<summary>Răspunsuri</summary>

1. Din Android 12 (API 31), orice activitate cu `intent-filter` trebuie să declare explicit `exported`. Fără el, instalarea eșuează. `true` = poate fi pornită din afară (launcher-ul e „afară”).
2. `namespace` decide pachetul clasei `R`; `applicationId` decide identitatea aplicației în sistem. Pot fi diferite. Dacă schimbi `namespace`, trebuie să actualizezi toate `import ...R`.
3. Pentru că `Theme.G1097` moștenește `Base.Theme.G1097`, iar Android rezolvă moștenirea la runtime, luând `Base` din folderul de configurare potrivit (values sau values-night). Definiția din `values/` e suficientă.
4. Generează clase de tip `ActivityMainBinding` care înlocuiesc `findViewById` cu acces direct la câmpuri, type-safe. Codul din repo folosește `findViewById` — deci feature-ul e activat dar nefolosit. Îl vei folosi opțional în capitolul 11.

</details>

---

**Următorul capitol:** [02 - Modelul Movie.md](02%20-%20Modelul%20Movie.md)
