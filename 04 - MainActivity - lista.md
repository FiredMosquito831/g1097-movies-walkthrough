# Capitolul 04 — `MainActivity`: lista de filme

**Obiectiv:** o `MainActivity` care creează 3 filme demo, le afișează într-un `ListView` prin `ArrayAdapter`, și are FAB-ul legat (încă fără navigare — asta vine în cap. 08).

**Timp estimat:** 30–45 min.

**Fișier final:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` (5455 B, SHA-256 `6c82723f8e099c87…`)

> **Notă:** la acest capitol scriem `MainActivity` **fără** `ActivityResultLauncher` și fără `onItemClick`. Alea vin în cap. 08. Aici doar: date demo + listă + FAB care nu face nimic încă.

---

## Pasul 4.1 — Scheletul clasei

### De ce

O `Activity` e o clasă care are un **ciclu de viață** controlat de Android. Nu tu o creezi cu `new MainActivity()`. Sistemul o instanțiază când e nevoie și cheamă metode:

```
onCreate()   ← se creează
onStart()    ← devine vizibilă
onResume()   ← primește focus
onPause()    ← pierde focus
onStop()     ← nu mai e vizibilă
onDestroy()  ← se distruge
```

Tu suprascrii doar ce ai nevoie. Aici: `onCreate()`.

### Cum

```java
package ro.ase.ie.g1097.activities;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.List;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MainActivity extends AppCompatActivity {

    private FloatingActionButton fabInsert;
    private ListView listView;
    private final List<Movie> movies = new ArrayList<>();
    private ArrayAdapter<Movie> movieAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        addSampleMovies();

        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
        initControls();
        initListeners();
    }

    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        listView = findViewById(R.id.listView);
        listView.setAdapter(movieAdapter);
    }

    private void initListeners() {
        // se completează în capitolul 08
    }

    private void addSampleMovies() {
        // se completează la pasul 4.5
    }
}
```

### De ce câmpurile sunt `private` și nu locale

`fabInsert`, `listView`, `movieAdapter` sunt folosite în **mai multe metode** (`initControls`, `initListeners`, `onCreate`). Dacă ar fi locale în `onCreate`, nu le-ai putea accesa din `initListeners`.

`movies` e `final` pentru că **referința** nu se schimbă niciodată — aceeași listă, doar conținutul i se modifică (`add`, `set`). `final` pe o colecție nu înseamnă „imuabilă”, înseamnă „nu o reasignezi”.

> **De reținut:** `final List<Movie> movies = new ArrayList<>();` — poți face `movies.add(...)`, dar nu `movies = new ArrayList<>();`. E o distincție care apare la test.

---

## Pasul 4.2 — `setContentView` și ordinea apelurilor

### De ce ordinea din `onCreate` contează

```java
super.onCreate(savedInstanceState);   // 1. lansează ciclul de viață al părintelui
setContentView(R.layout.activity_main); // 2. construiește arborele de view-uri
addSampleMovies();                      // 3. umple lista de date (fără UI)
movieAdapter = new ArrayAdapter<>(...); // 4. creează adapterul peste listă
initControls();                         // 5. findViewById + setAdapter
initListeners();                        // 6. leagă butoane
```

**De ce `setContentView` înainte de `findViewById`?** Pentru că `findViewById` caută în arborele de view-uri. Înainte de `setContentView`, arborele nu există → `null`.

**De ce `addSampleMovies` înainte de `new ArrayAdapter`?** Pentru că `ArrayAdapter` primește **referința** la listă. Dacă ai adăuga filme după, ar merge și el (aceeași referință), dar `notifyDataSetChanged()` ar fi necesar. Umplând înainte, adapterul vede lista deja plină la construcție.

**De ce `initControls` după `new ArrayAdapter`?** Pentru că `initControls` apelează `listView.setAdapter(movieAdapter)` — deci `movieAdapter` trebuie să existe.

### Ordinea greșită clasică

```java
initControls();  // NullPointerException la listView.setAdapter(movieAdapter)
movieAdapter = new ArrayAdapter<>(...);
```

`movieAdapter` e `null` când e folosit. **Aceasta e cea mai frecventă eroare la test.**

### Exercițiu 4.2

**Cerință:** mută `initControls()` **înainte** de `movieAdapter = new ArrayAdapter<>(...)`. Rulează. Citește `Logcat`.

<details>
<summary>Indiciu</summary>

Caută `NullPointerException` și uită-te la linia din `MainActivity` care a crăpat.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am inversat ordinea a două linii din `onCreate`.

**Ce se întâmplă:** aplicația crăpă la pornire cu:

```
java.lang.NullPointerException: Attempt to invoke virtual method
'void android.widget.ListView.setAdapter(android.widget.ListAdapter)'
on a null object reference
```

sau, dacă `listView` e găsit dar `movieAdapter` e `null`:

```
java.lang.NullPointerException
    at ro.ase.ie.g1097.activities.MainActivity.initControls(MainActivity.java:...)
```

**De ce:** `movieAdapter` e un câmp `private` care nu a fost încă inițializat. În Java, un câmp de tip obiect nedeclarat are valoarea `null`. `setAdapter(null)` nu aruncă imediat, dar `ListView` nu poate afișa nimic; dacă `listView` însuși e `null`, `listView.setAdapter(...)` aruncă NPE instant.

**De reținut:**
1. **Ordinea inițializărilor e critică.** Regula: *definește înainte să folosești*.
2. `findViewById` întoarce `null` dacă ID-ul nu există sau nu e încă în arbore.
3. NPE-ul îți spune **fișierul și linia** — citește-l, nu ghici.

**Unde revine:** în cap. 07, `ItemActivity.initControls()` trebuie apelat **după** `setContentView`, altfel **toate** cele 13 `findViewById` întorc `null`. Și în cap. 08, `launcher` trebuie inițializat **înainte** ca `initListeners` să-l folosească în `onClick`.

</details>

---

## Pasul 4.3 — `ArrayAdapter`

### De ce

`ListView` nu știe să afișeze `Movie`. Are nevoie de un **adapter** care să răspundă la două întrebări:

- câte elemente sunt? (`getCount()`)
- cum arată elementul de la poziția `i`? (`getView(i, ...)`)

`ArrayAdapter` e implementarea gata făcută pentru liste de obiecte. El cheamă `toString()` pe fiecare element și îl pune într-un `TextView`.

### Cum

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

Trei argumente:

| Argument | Ce e | De ce |
|---|---|---|
| `this` | `Context` | adapterul are nevoie de context ca să creeze view-uri |
| `android.R.layout.simple_list_item_1` | un layout **din Android**, nu din proiect | conține un singur `TextView` cu id-ul `android.R.id.text1` |
| `movies` | `List<Movie>` | sursa de date — **referință**, nu copie |

### `android.R` vs `R`

- `android.R.layout.simple_list_item_1` → resursă din **sistemul Android** (există pe orice telefon)
- `R.layout.activity_main` → resursă din **proiectul tău**

De asta nu ai nevoie de un fișier `simple_list_item_1.xml` — e deja în Android.

### Capcana `notifyDataSetChanged`

`ArrayAdapter` ține referința la listă, dar **nu observă** modificările ei automat. Dacă faci `movies.add(movie)`, lista se schimbă, dar `ListView`-ul **nu se redesenează** până nu apelezi:

```java
movieAdapter.notifyDataSetChanged();
```

> **De reținut:** `notifyDataSetChanged()` e obligatoriu după orice modificare a listei. În cap. 08 îl vei vedea de două ori, în `onActivityResult`.

### Exercițiu 4.3

**Cerință:** adaugă în `onCreate`, după `initListeners()`, linia `movies.add(new Movie("Test", null, "Drama", 0, 0, 0f, false, "G", false, null));` — **fără** `notifyDataSetChanged()`. Rulează. Apare „Test” în listă?

<details>
<summary>Indiciu</summary>

Gândește-te când își citește `ListView`-ul datele: la `setAdapter` sau la fiecare frame?

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un film după ce adapterul a fost deja setat pe listă, fără să notific.

**Ce se vede:** „Test” **nu apare**. Lista rămâne cu cele 3 filme demo.

**De ce:** `ListView` își construiește view-urile o singură dată, când primește adapterul (`setAdapter`), și le refolosește la scroll. Nu are un mecanism de „observare” a listei. `notifyDataSetChanged()` e semnalul explicit: „datele s-au schimbat, reconstruiește”.

**De reținut:**
1. `ArrayAdapter` + `ListView` = model „push”: tu trebuie să anunți.
2. `RecyclerView.Adapter` (cap. 11) e la fel — tot `notifyDataSetChanged()` sau variante mai fine (`notifyItemInserted`, `notifyItemChanged`).
3. Dacă ai adăuga filmul **înainte** de `new ArrayAdapter<>(...)`, ar apărea fără notificare, pentru că adapterul ar fi construit cu lista deja plină.

**Unde revine:** în cap. 08, `onActivityResult` face exact `movies.add(movie); movieAdapter.notifyDataSetChanged();`. Dacă uiți a doua linie, filmul se salvează în listă dar **nu apare** — și vei crede că salvarea nu merge.

</details>

---

## Pasul 4.4 — `findViewById`

### De ce

`findViewById(R.id.x)` caută în arborele de view-uri un element cu ID-ul `x`. E ca un `document.getElementById()`.

### Cum

```java
fabInsert = findViewById(R.id.floatingActionButton);
listView = findViewById(R.id.listView);
```

### De ce `R.id.floatingActionButton`

În XML ai `android:id="@+id/floatingActionButton"`. `@+id/` creează ID-ul în `R.id`. Deci în cod: `R.id.floatingActionButton`.

### De ce nu e nevoie de cast

În Java modern (și cu `compileSdk` recent), `findViewById` e **generic**:

```java
public <T extends View> T findViewById(int id)
```

Compilatorul deduce tipul din atribuire. Deci `ListView listView = findViewById(R.id.listView);` merge fără `(ListView)`.

> **Istoric:** în cod vechi vedeai `(ListView) findViewById(R.id.listView)`. Cast-ul explicit nu mai e necesar, dar îl vei întâlni în exemple.

### Capcana: `findViewById` după `setContentView`

Dacă apelezi `findViewById` înainte de `setContentView`, întoarce `null`. De asta `initControls()` e apelat **după** `setContentView`.

### Exercițiu 4.4

**Cerință:** mută `initControls();` **înainte** de `setContentView(R.layout.activity_main);`. Ce se întâmplă?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am mutat apelul `initControls()` înainte de `setContentView`.

**Ce se întâmplă:** `fabInsert` și `listView` primesc `null`. Apoi `listView.setAdapter(movieAdapter)` aruncă:

```
NullPointerException: Attempt to invoke virtual method 'void android.widget.ListView.setAdapter(...)' on a null object reference
```

**De ce:** `setContentView` e cel care **construiește** arborele de view-uri din XML. Înainte de el, `findViewById` nu are unde să caute.

**De reținut:**
1. Ordinea obligatorie în `onCreate`: `super.onCreate` → `setContentView` → `findViewById`.
2. `findViewById` returnează `null`, **nu** aruncă excepție când nu găsește — deci eroarea apare mai târziu, la primul apel pe obiectul `null`. Asta face debugging-ul mai greu.
3. Dacă ai un `findViewById` care întoarce `null` și ID-ul **există** în XML, verifică: (a) ai apelat `setContentView` cu layout-ul corect? (b) elementul e în **acel** layout sau într-unul inclus?

**Unde revine:** în cap. 07, `ItemActivity` are 13 `findViewById`. Dacă unul întoarce `null`, vei avea NPE la `fillForm` sau `saveMovie`, nu la `initControls`. Aceeași cauză, alt loc de manifestare.

</details>

---

## Pasul 4.5 — Datele demo: `GregorianCalendar`

### De ce

Ai nevoie de 3 filme ca să vezi lista populată. Fiecare are o **dată de lansare**. Cum construiești un `Date` dintr-o zi, lună, an?

`java.util.Date` e doar un `long` (milisecunde din 1970). Nu are constructori prietenoși. `GregorianCalendar` e clasa care știe să construiască o dată din componente.

### Cum

```java
private void addSampleMovies() {
    movies.add(new Movie(
            "Inception",
            new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),
            "Sci-Fi",
            160000000,
            148,
            4.5f,
            true,
            "PG-13",
            false,
            "https://example.com/posters/inception.jpg"));

    movies.add(new Movie(
            "Toy Story",
            new GregorianCalendar(1995, Calendar.NOVEMBER, 22).getTime(),
            "Animation",
            30000000,
            81,
            4f,
            true,
            "G",
            false,
            "https://example.com/posters/toy-story.jpg"));

    movies.add(new Movie(
            "The Matrix",
            new GregorianCalendar(1999, Calendar.MARCH, 31).getTime(),
            "Action",
            63000000,
            136,
            5f,
            false,
            "R",
            true,
            "https://example.com/posters/the-matrix.jpg"));
}
```

### Capcana lunii

`Calendar.JULY` = **6**, nu 7! Lunile sunt indexate de la 0:

| Constantă | Valoare reală | Index |
|---|---|---|
| `Calendar.JANUARY` | ianuarie | 0 |
| `Calendar.FEBRUARY` | februarie | 1 |
| … | … | … |
| `Calendar.JULY` | iulie | 6 |
| `Calendar.DECEMBER` | decembrie | 11 |

De asta se folosesc constantele, nu numere. `new GregorianCalendar(2010, 7, 16)` ar fi **16 august 2010**, nu 16 iulie.

> **Aceasta e cea mai frecventă greșeală cu `Calendar`.** La test, dacă ți se cere „16 iulie 2010”, scrii `Calendar.JULY`, nu `7`.

### De ce `.getTime()`

`GregorianCalendar` **este** un `Calendar`, nu un `Date`. `getTime()` îl convertește într-un `Date` (extrage milisecundele).

```
GregorianCalendar(2010, JULY, 16)  --getTime()-->  Date(millis)
```

### De ce `4f` și nu `4.0`

`4f` e literal `float`. `4.0` ar fi `double` și nu s-ar potrivi la parametrul `float rating` fără cast. `4.5f`, `5f` — la fel.

### De ce `160000000` și nu `160_000_000`

Ambele sunt valide în Java 7+. Repo-ul folosește forma fără underscore. `160_000_000` e mai lizibil, dar fii consecvent.

### Exercițiu 4.5

**Cerință:** adaugă un al patrulea film demo: „Interstellar”, 7 noiembrie 2014, „Sci-Fi”, buget 165000000, 169 minute, rating 4.5, watched `true`, approval „PG-13”, watchlist `false`, poster `https://example.com/posters/interstellar.jpg`.

<details>
<summary>Indiciu</summary>

Noiembrie = `Calendar.NOVEMBER`. Ordinea parametrilor: title, release, genre, budget, duration, rating, watched, approval, onWatchlist, poster.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un al patrulea `movies.add(new Movie(...))` la finalul lui `addSampleMovies()`.

```java
movies.add(new Movie(
        "Interstellar",
        new GregorianCalendar(2014, Calendar.NOVEMBER, 7).getTime(),
        "Sci-Fi",
        165000000,
        169,
        4.5f,
        true,
        "PG-13",
        false,
        "https://example.com/posters/interstellar.jpg"));
```

**Cum verifici:** rulezi. În listă apare un al patrulea rând: `Movie{title='Interstellar', release=..., ...}`.

**De ce merge fără alte modificări:** `addSampleMovies()` e apelat **înainte** de `new ArrayAdapter<>(...)`. Adapterul e construit cu lista deja completă, deci nu ai nevoie de `notifyDataSetChanged()`.

**De reținut:**
1. Ordinea parametrilor constructorului e **pozițională**. `169` (int) la poziția 5, `4.5f` (float) la 6. Dacă inversezi, compilatorul **nu** te prinde (ambele sunt numerice, cu conversie implicită `int`→`float`), dar datele vor fi greșite.
2. `Calendar.NOVEMBER` = 10, nu 11.
3. Dacă uiți `.getTime()`, ai `GregorianCalendar`, nu `Date` → eroare de compilare (tip incompatibil).

**Unde revine:** în cap. 09, `fillForm` va formata `existing.getRelease()` cu `SimpleDateFormat("dd/MM/yyyy")`. Dacă `release` e `null` (film creat cu constructorul gol și fără setRelease), vei avea NPE. De asta versiunea ta locală de sync adaugă un `if (existing.getRelease() != null)`.

</details>

---

## Pasul 4.6 — `EdgeToEdge` și insets

### De ce

Din Android 15, aplicațiile sunt afișate **edge-to-edge** implicit: conținutul se întinde sub bara de status și sub bara de navigare. Frumos, dar textul de sus se suprapune cu ceasul.

Soluția: aplici **padding** egal cu înălțimea barelor de sistem.

### Cum

```java
EdgeToEdge.enable(this);
setContentView(R.layout.activity_main);
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
    return insets;
});
```

### Linie cu linie

| Linie | Ce face |
|---|---|
| `EdgeToEdge.enable(this)` | permite desenarea sub barele de sistem |
| `findViewById(R.id.main)` | rădăcina layout-ului — de aceea are `android:id="@+id/main"` |
| `insets.getInsets(Type.systemBars())` | înălțimile barelor (status sus, navigare jos, eventual laterale) |
| `v.setPadding(...)` | împinge conținutul în interiorul zonei sigure |
| `return insets` | lasă insets-urile să circule mai departe (dacă nu le consumi) |

### De ce `ViewCompat` și nu direct

`ViewCompat.setOnApplyWindowInsetsListener` e varianta compatibilă cu toate versiunile Android. API-ul nativ (`View.setOnApplyWindowInsetsListener`) are semnături diferite între versiuni.

### De ce se aplică pe `R.id.main`

Pentru că `main` e **rădăcina** (`FrameLayout`). Dacă ai aplica padding pe `ListView`, FAB-ul ar rămâne sub bara de navigare. Aplicând pe rădăcină, **toți** copiii sunt împinși înăuntru.

### Exercițiu 4.6

**Cerință:** elimină blocul `ViewCompat.setOnApplyWindowInsetsListener(...)`. Rulează. Ce se întâmplă cu textul din listă și cu FAB-ul?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am scos listener-ul de insets, păstrând `EdgeToEdge.enable(this)`.

**Ce se vede:** primul rând din listă intră **sub bara de status** (ceasul, bateria se suprapun peste „Inception”). FAB-ul intră **sub bara de navigare** (butoanele gestuale îl acoperă parțial).

**De ce:** `EdgeToEdge.enable()` spune sistemului „lasă-mă să desenez sub bare”. Fără padding compensator, conținutul chiar ajunge sub ele.

**De reținut:**
1. `EdgeToEdge` + insets = pereche. Una fără alta dă suprapuneri.
2. Padding-ul se aplică pe **rădăcină**, nu pe copii.
3. `return insets` (nu `WindowInsetsCompat.CONSUMED`) lasă insets-urile să circule — dacă ai un `BottomNavigationView`, are nevoie de ele.

**Unde revine:** `ItemActivity` face exact același lucru, dar pe `R.id.main` din `activity_item.xml` — care e un `ScrollView`. Diferență: acolo `ScrollView` are `android:fillViewport="true"`, deci padding-ul se aplică pe conținutul scrollabil. Vei vedea că funcționează la fel.

</details>

---

## Pasul 4.7 — `initListeners` gol (deocamdată)

### De ce

În repo, `initListeners()` conține doi listeneri:

```java
fabInsert.setOnClickListener(...)   // deschide ItemActivity
listView.setOnItemClickListener(...) // deschide ItemActivity cu filmul
```

Dar ambii folosesc `launcher`, care e inițializat **după** `initListeners()` în `onCreate`. Deci la acest capitol, `initListeners()` e gol — îl completezi în cap. 08.

### Cum

```java
private void initListeners() {
    // se completează în capitolul 08
}
```

### De ce nu-l lași complet de la început

Pentru că ai avea `launcher` `null` când apeși butonul → NPE. Ordinea din repo e:

```java
initControls();
initListeners();     // ← aici launcher e încă null!
launcher = registerForActivityResult(...);
```

> **Atenție:** aceasta e o **capcană reală în codul repo-ului**. `initListeners` înregistrează listeneri care **capturează** câmpul `launcher` — dar listener-ul nu se execută la înregistrare, ci la click. La click, `launcher` e deja inițializat. Deci merge **din întâmplare**, datorită execuției amânate.
>
> Dacă ai apela `fabInsert.performClick()` imediat după `initListeners()`, ai avea NPE. E o lecție despre **ordinea de inițializare vs. momentul execuției**.

---

## Pasul 4.8 — Verificare

### Cum

1. Rulează aplicația.
2. Vezi 3 rânduri în listă.
3. Textul fiecărui rând arată ca `Movie{title='Inception', release=..., ...}` — lung, urât, dar complet.
4. FAB-ul e vizibil jos-dreapta. Dacă îl apeși, **nu se întâmplă nimic** (listener gol).

### Ce verifici în cod

- [ ] `movies` e `final List<Movie>` inițializat cu `new ArrayList<>()`
- [ ] `onCreate` cheamă în ordine: `super`, `EdgeToEdge`, `setContentView`, insets, `addSampleMovies`, `new ArrayAdapter`, `initControls`, `initListeners`
- [ ] `initControls` face `findViewById` + `listView.setAdapter(movieAdapter)`
- [ ] `addSampleMovies` adaugă 3 filme cu `GregorianCalendar`
- [ ] `initListeners` e gol

---

## Pasul 4.9 — Exercițiu de reflecție

**Cerință:** de ce `List<Movie>` și nu `ArrayList<Movie>` ca tip al câmpului?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** câmpul e declarat `private final List<Movie> movies = new ArrayList<>();`.

**De ce `List` și nu `ArrayList`:** `List` e **interfața**, `ArrayList` e o **implementare**. Declarând tipul ca interfață, poți schimba implementarea oricând (`LinkedList`, `CopyOnWriteArrayList`) fără să modifici restul codului. Codul care folosește `movies` știe doar că e o listă ordonată cu `add`, `get`, `set`, `size` — nu-l interesează cum e implementată.

**De reținut:**
1. **Programează la interfață, nu la implementare.** E un principiu SOLID (Dependency Inversion).
2. `new ArrayList<>()` cu diamond operator — compilatorul deduce `<Movie>` din tipul câmpului.
3. `final` + interfață = referință fixă, conținut mutabil.

**Unde revine:** în cap. 11, `MovieAdapter` primește `List<Movie> movies` în constructor — tot interfață. Dacă ar primi `ArrayList`, ar fi inutil de restrictiv.

</details>

---

## Pasul 4.10 — Sinteză: `MainActivity` la acest stadiu

```java
package ro.ase.ie.g1097.activities;

import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.List;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MainActivity extends AppCompatActivity {

    private FloatingActionButton fabInsert;
    private ListView listView;
    private final List<Movie> movies = new ArrayList<>();
    private ArrayAdapter<Movie> movieAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        addSampleMovies();

        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
        initControls();
        initListeners();
    }

    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        listView = findViewById(R.id.listView);
        listView.setAdapter(movieAdapter);
    }

    private void initListeners() {
        // capitolul 08
    }

    private void addSampleMovies() {
        // cele 3 filme
    }
}
```

### Întrebări de test

1. De ce `ArrayAdapter` are nevoie de `this`?
2. Ce se întâmplă dacă uiți `listView.setAdapter(movieAdapter)`?
3. De ce `Calendar.JULY` e 6?
4. De ce insets-urile se aplică pe `R.id.main`?
5. Ce face `final` pe `movies`?

<details>
<summary>Răspunsuri — explicativ</summary>

**1. De ce `ArrayAdapter` are nevoie de `this`?**
Primul parametru e `Context`. Adapterul are nevoie de el ca să **creeze view-uri** (`LayoutInflater.from(context)`) și să acceseze resurse. `Activity` **este** un `Context`.

**2. Ce se întâmplă dacă uiți `setAdapter`?**
`ListView` rămâne cu adapterul din `android:entries` (Item 1..20) sau, dacă ai scos `entries`, e gol. Filmele sunt în `movies` dar nu se afișează nicăieri. **Fără eroare** — doar listă goală. E un bug tăcut, greu de prins.

**3. De ce `Calendar.JULY` e 6?**
`Calendar` indexează lunile de la 0 (`JANUARY = 0`). E o decizie istorică din Java 1.1, păstrată pentru compatibilitate. Folosește **constantele**, niciodată numere.

**4. De ce insets pe `R.id.main`?**
`main` e rădăcina arborelui. Padding-ul pe rădăcină împinge **toți** copiii în zona sigură. Pe un copil, ceilalți ar rămâne sub bare.

**5. Ce face `final` pe `movies`?**
Împiedică **reasignarea** referinței (`movies = ...` nu compilează). Conținutul rămâne mutabil (`add`, `set`, `clear` funcționează). E o garanție că lista e aceeași pe toată durata vieții activității.

</details>

---

## Rezumat capitol 04

- `onCreate`: `super` → `EdgeToEdge` → `setContentView` → insets → date → adapter → controls → listeners.
- `ArrayAdapter` + `ListView` = model push; `notifyDataSetChanged()` obligatoriu după modificări.
- `findViewById` după `setContentView`, altfel `null`.
- `GregorianCalendar` cu `Calendar.MONTH` (0-indexat) + `.getTime()`.
- Insets pe rădăcină, cu `ViewCompat`.

**Următorul capitol:** [05 - Formularul - partea 1.md](05%20-%20Formularul%20-%20partea%201.md)
