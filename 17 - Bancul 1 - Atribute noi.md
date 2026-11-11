# Capitolul 17 — Bancul de cerințe 1: adăugarea unui atribut

**Obiectiv:** să execuți „adăugați un atribut” la examen în 10–15 minute per atribut, fără să uiți niciun strat și fără să pierzi puncte pe un `NullPointerException` sau un `NumberFormatException`.

**Cum arată cerința la examen:** „Adăugați filmului atributul `<tip> <nume>`. Afișați-l în formular și în listă.” Două cerințe, 30 de minute, un singur atribut sau două.

**Lanțul de 5 pași:** 1. Model  2. Layout formular  3. ItemActivity  4. Layout card  5. Adapter
> Regula: model → formular → activitate → card → adapter.

---

## Exercițiul 17.1 — `writer` (String): atributul de referință

**Cerință:** Adăugați filmului atributul `writer` (String) — numele scenaristului. Afișați-l în formular, sub data lansării, și în listă.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private String writer;` lângă `private String poster = null;`.
2. În constructorul cu 10 parametri, adaugă `String writer` la finalul listei și `this.writer = writer;` la finalul corpului.
3. În `toString()`, adaugă linia `", writer='" + writer + '\'' +` după linia lui `poster`.
4. Adaugă `getWriter()` și `setWriter()` lângă `getPoster()`/`setPoster()`.
5. Compilează. Vor apărea trei erori în `MainActivity.addSampleMovies()` — adaugă al 11-lea argument la fiecare dintre cele trei apeluri `new Movie(...)`.
6. Deschide `res/layout/activity_item.xml`, găsește `</com.google.android.material.textfield.TextInputLayout>` al lui `etRelease` (Card 1, Basics) și inserează acolo `TextView`-ul etichetei plus `TextInputLayout`-ul cu `etWriter`.
7. Deschide `activities/ItemActivity.java` și fă patru adăugiri: câmpul `private EditText etWriter;`, linia din `initControls()`, linia din `fillForm()`, linia din `saveMovie()`.
8. Deschide `res/layout/movie_item.xml`: adaugă `TextView`-ul `movieWriter` după `movieFacts`. În `MovieAdapter`, trei linii: câmp, `findViewById`, `setText`.
9. Verifică: Run, adaugă un film cu „Christopher Nolan” la Writer. În listă trebuie să apară `writer='Christopher Nolan'` în textul `toString()`. Atinge filmul: câmpul Writer e completat.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 1</summary>

câmpul se declară lângă celelalte câmpuri, sus în clasă, nu în constructor. Dacă îl pui în constructor, compilatorul îl tratează ca parametru și `this.writer` nu mai există.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 3</summary>

`toString()` e chiar sub constructor. Linia nouă se pune între `", poster='" + poster + '\'' +` și `'}'`, cu virgula la început — același stil ca toate celelalte linii.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat câmpul în model, câmpul în formular, citirea/scrierea în `ItemActivity`, `TextView`-ul în card și legarea în adapter.

**Cod:**

Pasul 1 — `model/Movie.java`, patru locuri:

```java
// 1a. câmpul, lângă celelalte
private String writer;

// 1b. constructorul complet — parametru nou, LA FINAL, după poster
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String writer) {
    this.title = title;
    this.release = release;
    this.genre = genre;
    this.budget = budget;
    this.duration = duration;
    this.rating = rating;
    this.watched = watched;
    this.approval = approval;
    this.onWatchlist = onWatchlist;
    this.poster = poster;
    this.writer = writer;          // linia nouă
}

// 1c. toString() — după linia lui poster, înainte de '}'
", writer='" + writer + '\'' +

// 1d. getter/setter, lângă celelalte
public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 1 (Basics), imediat după `TextInputLayout`-ul lui `etRelease`:

```xml
<TextView
    android:id="@+id/tvWriter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Writer"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etWriter"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Writer"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Pasul 3 — `activities/ItemActivity.java`, patru locuri:

```java
// 3a. câmpul, lângă celelalte
private EditText etWriter;

// 3b. initControls() — la finalul metodei
etWriter = findViewById(R.id.etWriter);

// 3c. fillForm() — la finalul metodei
etWriter.setText(existing.getWriter());

// 3d. saveMovie() — înainte de construirea Intent-ului
movie.setWriter(etWriter.getText().toString());
```

Pasul 4 — `res/layout/movie_item.xml`, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Writer"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 5 — `MovieAdapter.java`, trei locuri:

```java
// 5a. câmp în MovieViewHolder
private final TextView movieWriter;

// 5b. în constructorul lui MovieViewHolder
movieWriter = itemView.findViewById(R.id.movieWriter);

// 5c. în bind()
movieWriter.setText(movie.getWriter() != null ? movie.getWriter() : "");
```

Pasul 6, obligatoriu — `activities/MainActivity.java`, `addSampleMovies()`. Toate cele trei apeluri primesc un al 11-lea argument, altfel **nu compilează**:

```java
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
        "https://example.com/posters/inception.jpg",
        "Christopher Nolan"));   // ← argumentul nou
```

**De ce:** fiecare strat are propria reprezentare a aceleiași valori — `String` în model, `EditText` în formular, `setText`/`getText` în activitate, `TextView` în card, `bind` în adapter. Un atribut nou înseamnă cinci reprezentări, nu una.

**De reținut:**
1. **Constructorul se schimbă, nu se supraîncarcă.** Dacă adaugi un al doilea constructor cu 11 parametri și îl lași pe cel cu 10, ai două constructoare aproape identice și `addSampleMovies` continuă să meargă cu cel vechi — filmul demo are `writer = null` și nu observi. Schimbi semnătura și repari cele trei apeluri.
2. **Constructorul gol rămâne neatins.** E declarat la finalul lui `Movie` și e folosit de `saveMovie()` (`Movie movie = new Movie();`). Nu-l atinge.
3. **La `d719ffc` cardul nu e folosit.** Lista din `MainActivity` e un `ListView` cu `ArrayAdapter` pe `android.R.layout.simple_list_item_1`, deci afișează **`toString()`**. Pașii 4 și 5 nu au niciun efect vizibil până când nu faci `RecyclerView` + `MovieAdapter` (capitolul 11, pașii 11.6–11.8). La examen, dacă profesorul cere „în listă”, pasul care contează la `d719ffc` e **1c**.
4. `ItemActivity` folosește `findViewById`, nu ViewBinding (deși e activat în Gradle — vezi capitolul 13). Deci nu trebuie să regenerezi nicio clasă `Binding`.
5. Dacă uiți pasul 3d, atributul se salvează ca `null` la fiecare editare: `saveMovie()` construiește un `Movie` **nou**, nu îl modifică pe cel existent.

**Unde se aplică:** orice atribut `String` — `writer`, `country`, `studio`, `language`. Lanțul e identic.

</details>

---

## Exercițiul 17.2 — `year` (Integer): atributul numeric care poate fi null

**Cerință:** Adăugați filmului atributul `year` (Integer) — anul lansării. Câmp numeric în formular, patru cifre. Afișați-l în listă.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private Integer year;` — cu `I` mare, e clasă, nu primitivă.
2. În constructorul complet, adaugă `Integer year` la final și `this.year = year;`.
3. În `toString()`, adaugă `", year=" + year +`.
4. Adaugă `getYear()` și `setYear()`; tipul returnat și parametrul sunt `Integer`.
5. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument, `2010`, `1995`, `1999`.
6. În `activity_item.xml`, Card 1, după `etRelease`: `TextView` + `TextInputLayout` cu `etYear`, `android:inputType="number"` și `android:maxLength="4"`.
7. În `ItemActivity.java`: câmpul, `initControls()`, `fillForm()` — cu `String.valueOf(...)` — și `saveMovie()` — cu gardă `isEmpty()` înainte de `Integer.parseInt`.
8. Verifică: Run, adaugă un film cu anul 2024. În listă apare `year=2024`. Editează un film, golește anul, salvează — nu trebuie să apară niciun crash, iar în listă apare `year=null`.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 1</summary>

`Integer` e o clasă din `java.lang`, ca `String`. Nu are nevoie de import, se declară cu majusculă și acceptă `null`. `int` e primitiva, cu valoarea implicită `0`.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 7</summary>

`etYear.setText(existing.getYear())` compilează, dar la runtime aruncă `Resources$NotFoundException`. `Integer`-ul se unboxează la `int` și ajunge la suprascrierea `setText(int resid)`, care caută un id de resursă. Forțează `String` cu `String.valueOf(...)`.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat atributul ca `Integer` (încadrare, nu primitivă), l-am citit cu `parseInt` protejat și l-am afișat cu `String.valueOf`.

**Cod:**

Pasul 1 — `model/Movie.java`:

```java
// 1a. câmpul — Integer, nu int
private Integer year;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, Integer year) {
    // ... celelalte atribuiri ...
    this.year = year;
}

// 1c. toString()
", year=" + year +

// 1d. getter/setter
public Integer getYear() {
    return year;
}

public void setYear(Integer year) {
    this.year = year;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 1 (Basics), după `etRelease`:

```xml
<TextView
    android:id="@+id/tvYear"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Year"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etYear"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Year"
        android:inputType="number"
        android:maxLength="4" />
</com.google.android.material.textfield.TextInputLayout>
```

Pasul 3 — `activities/ItemActivity.java`:

```java
// 3a. câmpul
private EditText etYear;

// 3b. initControls()
etYear = findViewById(R.id.etYear);

// 3c. fillForm() — String.valueOf, NU getYear() direct
etYear.setText(existing.getYear() != null
        ? String.valueOf(existing.getYear())
        : "");

// 3d. saveMovie() — parsare protejată
String yearText = etYear.getText().toString().trim();
movie.setYear(yearText.isEmpty() ? null : Integer.parseInt(yearText));
```

Pasul 4 — `res/layout/movie_item.xml`, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieYear"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Year"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 5 — `MovieAdapter.java`:

```java
private final TextView movieYear;

movieYear = itemView.findViewById(R.id.movieYear);

movieYear.setText(movie.getYear() != null ? String.valueOf(movie.getYear()) : "");
```

Pasul 6 — `MainActivity.addSampleMovies()`: al 11-lea argument la toate trei:

```java
        "https://example.com/posters/inception.jpg",
        2010));
```

**De ce:** `Integer` și nu `int` pentru că „an necunoscut” e o informație reală. Cu `int`, toate cele trei filme demo ar avea `year = 0` până le setezi, iar cardul ar afișa „0” — o minciună. Cu `Integer`, valoarea implicită e `null` și poți afișa gol.

**De reținut:**
1. **Capcana `setText(Integer)`.** `TextView` are două metode: `setText(CharSequence)` și `setText(int resid)`. Dacă scrii `etYear.setText(existing.getYear())`, compilatorul **unboxează** `Integer`-ul la `int` și alege a doua variantă — adică tratează anul 2010 ca **id de resursă**. Rezultat: `Resources$NotFoundException` la runtime. Soluția e `String.valueOf(...)`, care forțează `String`.
2. `Integer.parseInt("")` aruncă `NumberFormatException`. De aici `isEmpty() ? null : ...`. `trim()` înainte, ca un câmp cu un spațiu să nu treacă drept număr.
3. `android:inputType="number"` afișează tastatura numerică și blochează minusul și virgula. `maxLength="4"` limitează la patru cifre — dar nu validează că e un an plauzibil („0000” trece).
4. `toString()` tipărește `year=null` pentru valoarea lipsă. La `d719ffc` asta e tot ce se vede în listă — acceptabil pentru test.
5. Bug-ul din `etBudget` e vecin: `Double.parseDouble(etBudget.getText().toString())` aruncă dacă utilizatorul scrie virgulă zecimală. Nu e treaba ta să-l repari la examen, dar recunoaște-l dacă îl vezi.

**Unde se aplică:** orice atribut numeric care poate lipsi — `year`, `oscarsWon`, `seasonCount`.

</details>

---

## Exercițiul 17.3 — `popular` (boolean): steagul cu valoare implicită

**Cerință:** Adăugați filmului atributul `popular` (boolean) — filmul e popular în rândul publicului. În formular, un `Switch`. În listă, un chip „Popular”.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private boolean popular;` lângă `private boolean watched;`.
2. În constructorul complet, adaugă `boolean popular` la final și `this.popular = popular;`.
3. În `toString()`, adaugă `", popular=" + popular +`.
4. Adaugă `isPopular()` — nu `getPopular()` — și `setPopular(boolean)`.
5. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument, `true` sau `false`.
6. În `activity_item.xml`, Card 3 (Your verdict), după `RadioGroup`-ul `rgApproval`: un rând cu `TextView` „Popular” și `MaterialSwitch` cu id `swPopular`. Importul pentru `MaterialSwitch` există deja în `ItemActivity`.
7. În `ItemActivity.java`: câmpul `private MaterialSwitch swPopular;`, `initControls()`, `fillForm()` cu `setChecked(existing.isPopular())`, `saveMovie()` cu `movie.setPopular(swPopular.isChecked())`.
8. În `movie_item.xml`, în `movieStatusGroup`, după `chipWatchlist`: un `Chip` cu id `chipPopular`. În adapter: câmp, `findViewById`, `setVisibility`.
9. Verifică: Run, adaugă un film cu switch-ul pornit. În listă apare `popular=true`. Deschide un film cu switch-ul oprit: switch-ul trebuie să fie stins, nu pornit.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 2</summary>

`boolean`, nu `Boolean`. Primitiva are deja valoarea `false`, deci nu are nevoie de inițializare în declarație — și nu poate fi `null`.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 7</summary>

dacă uiți `swPopular.setChecked(...)` din `fillForm`, nu apare nicio eroare. Dar `saveMovie()` construiește un `Movie` nou, deci la prima editare filmul devine nepopular — fără ca utilizatorul să atingă switch-ul.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat câmpul `boolean`, un `MaterialSwitch` în formular, un chip în card și `setVisibility` în adapter.

**Cod:**

Pasul 1 — `model/Movie.java`:

```java
// 1a. câmpul
private boolean popular;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, boolean popular) {
    // ... celelalte atribuiri ...
    this.popular = popular;
}

// 1c. toString()
", popular=" + popular +

// 1d. getter/setter — convenția isX() pentru boolean
public boolean isPopular() {
    return popular;
}

public void setPopular(boolean popular) {
    this.popular = popular;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 3 (Your verdict), după `RadioGroup`-ul `rgApproval`, înainte de `</LinearLayout>`:

```xml
<View
    android:layout_width="match_parent"
    android:layout_height="1dp"
    android:layout_marginVertical="12dp"
    android:background="?attr/colorOutlineVariant" />

<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:minHeight="48dp"
    android:orientation="horizontal">

    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="Popular"
        android:textAppearance="?attr/textAppearanceBodyLarge"
        android:textColor="?attr/colorOnSurface" />

    <com.google.android.material.materialswitch.MaterialSwitch
        android:id="@+id/swPopular"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
</LinearLayout>
```

Pasul 3 — `activities/ItemActivity.java`:

```java
// 3a. câmpul — MaterialSwitch e deja importat
private MaterialSwitch swPopular;

// 3b. initControls()
swPopular = findViewById(R.id.swPopular);

// 3c. fillForm()
swPopular.setChecked(existing.isPopular());

// 3d. saveMovie()
movie.setPopular(swPopular.isChecked());
```

Pasul 4 — `res/layout/movie_item.xml`, în `movieStatusGroup`, după `chipWatchlist`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipPopular"
    style="@style/Widget.Material3.Chip.Suggestion"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Popular"
    android:clickable="false"
    app:chipMinHeight="28dp"
    app:ensureMinTouchTargetSize="false" />
```

Pasul 5 — `MovieAdapter.java`:

```java
private final Chip chipPopular;

chipPopular = itemView.findViewById(R.id.chipPopular);

chipPopular.setVisibility(movie.isPopular() ? View.VISIBLE : View.GONE);
```

Pasul 6 — `MainActivity.addSampleMovies()`: al 11-lea argument, `true` sau `false`, la toate trei.

**De ce:** `setVisibility` și nu `setText("")`. Un chip e o etichetă care există sau nu; dacă îl lași mereu vizibil și doar îi schimbi textul, cardul are un dreptunghi gol pentru filmele nepopulare.

**De reținut:**
1. **`fillForm` nu e opțional.** `saveMovie()` construiește un `Movie` nou. Dacă uiți `swPopular.setChecked(...)`, editezi un film popular, nu atingi switch-ul, salvezi — și filmul devine nepopular. Valoarea implicită `false` e cea care te înșelă: nu dă eroare, doar pierde date.
2. **Convenția `isPopular()`.** Pentru `boolean`, getterul e `isX()`, nu `getX()` — la fel ca `isWatched()` și `isOnWatchlist()` din model. `getPopular()` ar compila, dar ar fi inconsistent.
3. **`View.GONE` în `ChipGroup`.** `GONE` scoate chip-ul din aranjament, deci celelalte chips se strâng. `INVISIBLE` păstrează spațiul și lasă o gaură.
4. **La `d719ffc` chip-ul nu se vede.** `movie_item.xml` nu e folosit de `ListView` (vezi 17.1, punctul 3). Efectul vizibil la commit e doar `popular=true` în `toString()`. Pașii 4–5 devin reali după mutarea pe `RecyclerView` (capitolul 11).
5. `MaterialSwitch` în loc de `Switch` simplu — fișierul folosește deja `com.google.android.material.materialswitch.MaterialSwitch` pentru `swWatched`, iar importul există.

**Unde se aplică:** orice steag boolean — `popular`, `awarded`, `remastered`, `availableIn4K`.

</details>

---

## Exercițiul 17.4 — `imdbScore` (float): zecimala cu virgulă

**Cerință:** Adăugați filmului atributul `imdbScore` (float) — nota IMDb, între 0 și 10, cu o zecimală. Câmp decimal în formular, afișat în listă.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private float imdbScore;` lângă `private float rating;`.
2. În constructorul complet, adaugă `float imdbScore` la final și `this.imdbScore = imdbScore;`.
3. În `toString()`, adaugă `", imdbScore=" + imdbScore +`.
4. Adaugă `getImdbScore()` și `setImdbScore(float)`.
5. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument cu sufixul `f`, de exemplu `8.8f`.
6. În `activity_item.xml`, Card 2 (Production), după `etBudget`: `TextView` etichetă + `TextInputLayout` cu `app:suffixText="/ 10"` și `etImdbScore`, `inputType="numberDecimal"`, `maxLength="4"`.
7. În `ItemActivity.java`: câmpul, `initControls()`, `fillForm()` cu `String.valueOf(...)`, `saveMovie()` cu `replace(',', '.')` înainte de `Float.parseFloat` și gardă `isEmpty()`.
8. În `movie_item.xml` și adapter: `TextView`-ul `movieImdbScore`, legat cu `"IMDb " + movie.getImdbScore()`.
9. Verifică: Run, scrie `8,5` cu virgulă în câmp și salvează. Nu trebuie să apară niciun crash, iar în listă apare `imdbScore=8.5`.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 5</summary>

literalul `float` are nevoie de sufixul `f`. `8.8` fără sufix e `double` și nu se potrivește pe un parametru `float` — eroarea e „incompatible types: possible lossy conversion from double to float”.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 7</summary>

`Float.parseFloat("8,5")` aruncă `NumberFormatException`, pentru că parserul acceptă doar punct. Normalizezi întâi — `text.replace(',', '.')` — și parsezi rezultatul, nu textul original.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat atributul `float`, câmpul decimal și am normalizat separatorul înainte de parsare.

**Cod:**

Pasul 1 — `model/Movie.java`:

```java
// 1a. câmpul
private float imdbScore;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, float imdbScore) {
    // ... celelalte atribuiri ...
    this.imdbScore = imdbScore;
}

// 1c. toString()
", imdbScore=" + imdbScore +

// 1d. getter/setter
public float getImdbScore() {
    return imdbScore;
}

public void setImdbScore(float imdbScore) {
    this.imdbScore = imdbScore;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 2 (Production), după `etBudget`:

```xml
<TextView
    android:id="@+id/tvImdbScore"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="IMDb score"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:suffixText="/ 10">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etImdbScore"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="IMDb score"
        android:inputType="numberDecimal"
        android:maxLength="4" />
</com.google.android.material.textfield.TextInputLayout>
```

Pasul 3 — `activities/ItemActivity.java`:

```java
// 3a. câmpul
private EditText etImdbScore;

// 3b. initControls()
etImdbScore = findViewById(R.id.etImdbScore);

// 3c. fillForm() — String.valueOf dă mereu punct
etImdbScore.setText(String.valueOf(existing.getImdbScore()));

// 3d. saveMovie() — virgula devine punct ÎNAINTE de parseFloat
String scoreText = etImdbScore.getText().toString().trim().replace(',', '.');
movie.setImdbScore(scoreText.isEmpty() ? 0f : Float.parseFloat(scoreText));
```

Pasul 4 — `res/layout/movie_item.xml`, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieImdbScore"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="IMDb 0.0"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 5 — `MovieAdapter.java`:

```java
private final TextView movieImdbScore;

movieImdbScore = itemView.findViewById(R.id.movieImdbScore);

movieImdbScore.setText("IMDb " + movie.getImdbScore());
```

Pasul 6 — `MainActivity.addSampleMovies()`: al 11-lea argument, de tip `float` — scrie `8.8f`, cu `f`, altfel e `double` și nu compilează:

```java
        "https://example.com/posters/inception.jpg",
        8.8f));
```

**De ce:** `Float.parseFloat` folosește `Locale`-independent punctul. Un utilizator cu tastatură românească scrie `8,5`, iar `Float.parseFloat("8,5")` aruncă `NumberFormatException` — aplicația se închide la Save. `replace(',', '.')` costă un apel și elimină tot bug-ul.

**De reținut:**
1. **Virgula zecimală e capcana standard la orice câmp decimal.** `Double.parseDouble` și `Float.parseFloat` acceptă doar punct. Dacă vrei să accepți ambele, normalizezi înainte de parsare.
2. `String.valueOf(float)` produce mereu punct, deci `fillForm` e sigur — nu trebuie să faci conversia inversă.
3. `Float.parseFloat("")` aruncă. De aici garda `isEmpty()`. `Float.parseFloat("8,")` aruncă la fel, deci `replace` trebuie aplicat înainte, nu după.
4. **`float` vs `double`.** `Movie` are deja `double budget` (bani, precizie) și `float rating` (notă, o zecimală). `imdbScore` e tot o notă → `float`, ca `rating`. Literalul din `addSampleMovies` are nevoie de sufixul `f`.
5. Variantă: în loc de `EditText`, un `RatingBar` cu `android:numStars="10"` și `android:stepSize="0.5"`; atunci `saveMovie` e `movie.setImdbScore(rbImdb.getRating())`, fără nicio parsare. Mai puțin cod, mai puține erori — dar profesorul a cerut câmp, nu stele.

**Unde se aplică:** orice atribut zecimal — `imdbScore`, `price`, `latitude`.

</details>

---

## Exercițiul 17.5 — `actors` (ArrayList\<String\>): listă într-un singur câmp

**Cerință:** Adăugați filmului atributul `actors` (ArrayList\<String\>) — numele actorilor. În formular, un singur câmp text, numele separate prin virgulă. În listă, afișați-i despărțiți prin virgulă.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `import java.util.ArrayList;` sus și câmpul `private ArrayList<String> actors = new ArrayList<>();`.
2. În constructorul complet, adaugă `ArrayList<String> actors` la final și `this.actors = actors;`.
3. În `toString()`, adaugă `", actors=" + actors +` — `List.toString()` pune singur parantezele pătrate.
4. Adaugă `getActors()` și `setActors(ArrayList<String>)`.
5. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument e o listă, `new ArrayList<>(Arrays.asList("Leonardo DiCaprio", "Joseph Gordon-Levitt"))`. Adaugă `import java.util.Arrays;` în `MainActivity`.
6. În `activity_item.xml`, Card 1, după `etRelease`: `TextView` etichetă + `TextInputLayout` cu `etActors` și hint-ul `"Actor 1, Actor 2, Actor 3"`.
7. În `ItemActivity.java`: câmpul, `initControls()`, `fillForm()` cu `String.join(", ", existing.getActors())` și gardă `null`.
8. În `saveMovie()`: o listă nouă, o buclă pe `etActors.getText().toString().split(",")`, `trim()` pe fiecare element, `isEmpty()` înainte de `add`.
9. În `movie_item.xml` și adapter: `TextView`-ul `movieActors`, legat cu `String.join(", ", movie.getActors())`.
10. Verifică: Run, scrie `A, B, C` și salvează — în listă apare `actors=[A, B, C]`. Apoi golește câmpul și salvează: trebuie să apară `actors=[]`, nu `actors=[]` cu un element vid înăuntru.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 1</summary>

inițializează câmpul pe loc, `= new ArrayList<>()`. Altfel e `null` până îl setează cineva, iar `toString()` și cardul trebuie să verifice `null` la fiecare afișare.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 8</summary>

`"".split(",")` nu întoarce un tablou gol, ci `[""]` — un tablou cu un singur element vid. Fără `if (!trimmed.isEmpty())`, un câmp lăsat gol produce o listă cu un `String` vid, iar cardul afișează o virgulă singuratică.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat `ArrayList<String>` în model, un `EditText` în care utilizatorul scrie lista separată prin virgulă, `split` la salvare și `String.join` la afișare.

**Cod:**

Pasul 1 — `model/Movie.java`:

```java
import java.util.ArrayList;   // import nou, sus

// 1a. câmpul — inițializat, ca să nu fie null
private ArrayList<String> actors = new ArrayList<>();

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, ArrayList<String> actors) {
    // ... celelalte atribuiri ...
    this.actors = actors;
}

// 1c. toString() — List.toString() dă deja "[a, b]"
", actors=" + actors +

// 1d. getter/setter
public ArrayList<String> getActors() {
    return actors;
}

public void setActors(ArrayList<String> actors) {
    this.actors = actors;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 1 (Basics), după `etRelease`:

```xml
<TextView
    android:id="@+id/tvActors"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Actors"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etActors"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Actor 1, Actor 2, Actor 3"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Pasul 3 — `activities/ItemActivity.java`:

```java
import java.util.ArrayList;   // import nou, sus

// 3a. câmpul
private EditText etActors;

// 3b. initControls()
etActors = findViewById(R.id.etActors);

// 3c. fillForm() — lista devine text
etActors.setText(existing.getActors() != null
        ? String.join(", ", existing.getActors())
        : "");

// 3d. saveMovie() — textul devine listă
ArrayList<String> actors = new ArrayList<>();
for (String name : etActors.getText().toString().split(",")) {
    String trimmed = name.trim();
    if (!trimmed.isEmpty()) {
        actors.add(trimmed);
    }
}
movie.setActors(actors);
```

Pasul 4 — `res/layout/movie_item.xml`, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieActors"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Actors"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 5 — `MovieAdapter.java`:

```java
private final TextView movieActors;

movieActors = itemView.findViewById(R.id.movieActors);

movieActors.setText(movie.getActors() != null
        ? String.join(", ", movie.getActors())
        : "");
```

Pasul 6 — `MainActivity.addSampleMovies()`: al 11-lea argument e o listă, nu un `String`:

```java
        "https://example.com/posters/inception.jpg",
        new ArrayList<>(Arrays.asList("Leonardo DiCaprio", "Joseph Gordon-Levitt"))));
```

**De ce:** un singur `EditText` cu separator e cel mai ieftin mod de a introduce o listă pe telefon. `split` la salvare, `join` la afișare — două conversii, ambele într-o linie.

**De reținut:**
1. **`"".split(",")` returnează `[""]`**, un tablou cu un singur element vid — nu un tablou gol. Fără garda `if (!trimmed.isEmpty())`, un câmp lăsat gol produce o listă cu un `String` vid, iar cardul afișează o virgulă singuratică.
2. **`"a,,b".split(",")` returnează `["a", "", "b"]`.** Virgula dublă nu dispare, produce un element vid în mijloc. De aceea `trim()` + `isEmpty()` se fac pe fiecare element, nu pe tot textul.
3. `String.join` e disponibil din API 26; `minSdk` e 33, deci e în regulă. Alternativa fără import nou: `android.text.TextUtils.join(", ", list)`.
4. **`ArrayList<String>` e `Serializable`**, deci `Intent.putExtra(MOVIE_EXTRA, movie)` funcționează neschimbat. `List<String>` ar funcționa și el la runtime (obiectul real e tot `ArrayList`), dar cerința spune `ArrayList` — declară `ArrayList`.
5. `List.toString()` dă `[Inception, ...]` cu paranteze pătrate. La `d719ffc` asta e ce se vede în listă, pentru că `ArrayAdapter` afișează `toString()`. Urât, dar vizibil — suficient pentru test.
6. `new ArrayList<>(Arrays.asList(...))` are nevoie de `import java.util.Arrays;` în `MainActivity`. Alternativa fără import: `new ArrayList<>(List.of(...))` — tot cu import.

**Unde se aplică:** orice listă simplă — `actors`, `tags`, `languages`, `awards`.

</details>

---

## Exercițiul 17.6 — `ageRestriction` (int): slider-ul cu valoare afișată

**Cerință:** Adăugați filmului atributul `ageRestriction` (int) — vârsta minimă recomandată, între 0 și 21. În formular, un `SeekBar` cu valoarea afișată deasupra. În listă, „+18” sau „Toate vârstele”.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private int ageRestriction;` lângă `private int duration;`.
2. În constructorul complet, adaugă `int ageRestriction` la final și `this.ageRestriction = ageRestriction;`.
3. În `toString()`, adaugă `", ageRestriction=" + ageRestriction +`.
4. Adaugă `getAgeRestriction()` și `setAgeRestriction(int)`.
5. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument, un `int` simplu, de exemplu `13`.
6. În `activity_item.xml`, Card 2, după blocul `sbDuration` + `tvDurationValue`: separatorul `View`, un rând cu eticheta „Minimum age” și `TextView`-ul `tvAgeRestrictionValue`, apoi `SeekBar`-ul `sbAgeRestriction` cu `android:min="0"` și `android:max="21"`.
7. În `ItemActivity.java`: cele două câmpuri, `initControls()`, apoi listener-ul în `initListeners()` — care rulează înainte de `fillForm()` —, `setProgress` în `fillForm()`, `getProgress()` în `saveMovie()`.
8. În `movie_item.xml` și adapter: `TextView`-ul `movieAgeRestriction`, legat cu `"+" + movie.getAgeRestriction()` sau „All ages” pentru 0.
9. Verifică: Run, trage slider-ul — eticheta se schimbă în timp real. Salvează cu 18, apoi redeschide filmul: slider-ul e la 18 **și** eticheta arată „18+”, nu „0+”.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 6</summary>

copiază blocul `sbDuration` + `tvDurationValue` din același card și schimbă doar `android:max` din `300` în `21`. Structura e identică, inclusiv separatorul `View` de deasupra.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 7</summary>

listener-ul trebuie atașat în `initListeners()`, nu în `fillForm()`. `onCreate` rulează `initControls()` → `initListeners()` → `fillForm()`, deci `setProgress` din `fillForm` declanșează `onProgressChanged` și eticheta se actualizează singură. Dacă atașezi listener-ul după `fillForm`, eticheta rămâne „0+” lângă un slider la 18.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat atributul `int`, un `SeekBar` cu `max="21"`, un `TextView` pentru valoare și un listener care ține eticheta sincronizată.

**Cod:**

Pasul 1 — `model/Movie.java`:

```java
// 1a. câmpul
private int ageRestriction;

// 1b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, int ageRestriction) {
    // ... celelalte atribuiri ...
    this.ageRestriction = ageRestriction;
}

// 1c. toString()
", ageRestriction=" + ageRestriction +

// 1d. getter/setter
public int getAgeRestriction() {
    return ageRestriction;
}

public void setAgeRestriction(int ageRestriction) {
    this.ageRestriction = ageRestriction;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 2 (Production), după blocul `sbDuration`:

```xml
<View
    android:layout_width="match_parent"
    android:layout_height="1dp"
    android:layout_marginVertical="12dp"
    android:background="?attr/colorOutlineVariant" />

<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:orientation="horizontal">

    <TextView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="Minimum age"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <TextView
        android:id="@+id/tvAgeRestrictionValue"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="0+"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorPrimary" />
</LinearLayout>

<SeekBar
    android:id="@+id/sbAgeRestriction"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:min="0"
    android:max="21"
    android:progressTint="?attr/colorPrimary"
    android:thumbTint="?attr/colorPrimary" />
```

Pasul 3 — `activities/ItemActivity.java`, patru locuri:

```java
// 3a. câmpurile
private SeekBar sbAgeRestriction;
private TextView tvAgeRestrictionValue;

// 3b. initControls()
sbAgeRestriction = findViewById(R.id.sbAgeRestriction);
tvAgeRestrictionValue = findViewById(R.id.tvAgeRestrictionValue);

// 3c. initListeners() — înainte de fillForm, ca eticheta să se actualizeze singură
sbAgeRestriction.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvAgeRestrictionValue.setText(progress + "+");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) { }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) { }
});

// 3d. fillForm() — un singur apel; listener-ul face restul
sbAgeRestriction.setProgress(existing.getAgeRestriction());

// 3e. saveMovie() — getProgress() întoarce direct int
movie.setAgeRestriction(sbAgeRestriction.getProgress());
```

Pasul 4 — `res/layout/movie_item.xml`, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieAgeRestriction"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Age"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 5 — `MovieAdapter.java`:

```java
private final TextView movieAgeRestriction;

movieAgeRestriction = itemView.findViewById(R.id.movieAgeRestriction);

movieAgeRestriction.setText(movie.getAgeRestriction() == 0
        ? "All ages"
        : "+" + movie.getAgeRestriction());
```

Pasul 6 — `MainActivity.addSampleMovies()`: al 11-lea argument, un `int` simplu:

```java
        "https://example.com/posters/inception.jpg",
        13));
```

**De ce:** `SeekBar` nu are nevoie de parsare — `getProgress()` întoarce exact `int`-ul de care ai nevoie. E singurul widget din fișier care dă direct tipul corect, fără conversie.

**De reținut:**
1. **Ordinea din `onCreate` face magia.** `initControls()` → `initListeners()` → `fillForm()`. Pentru că listener-ul e atașat **înainte** de `fillForm`, `setProgress(...)` din `fillForm` declanșează `onProgressChanged` și eticheta se actualizează singură. Dacă ai atașa listener-ul după `fillForm`, ar trebui să scrii `tvAgeRestrictionValue.setText(...)` și în `fillForm` — altfel la editare slider-ul arată 13, iar eticheta arată „0+”.
2. `SeekBar` nu are „step”. Toate cele 22 de valori întregi sunt selectabile. Dacă vrei doar 0, 6, 12, 16, 18, 21, folosești un `Spinner` cu `android:entries="@array/age_restriction"` și `Integer.parseInt(spAge.getSelectedItem().toString())`.
3. `android:min` e disponibil din API 26; `minSdk` 33, deci e în regulă. `sbDuration` îl folosește deja.
4. `progress + "+"` e concatenare `int` + `String` → `String`. Nu ai nevoie de `String.valueOf`.
5. `SeekBar.OnSeekBarChangeListener` are trei metode; două rămân goale. Nu e greșeală — sunt obligatorii prin interfață.

**Unde se aplică:** orice atribut întreg mărginit — `ageRestriction`, `discount`, `quantity`.

</details>

---

## Exercițiul 17.7 — `country` (String) cu validare: câmpul obligatoriu

**Cerință:** Adăugați filmului atributul `country` (String). Câmpul e obligatoriu: dacă e gol, salvarea se blochează, apare o eroare pe câmp și formularul rămâne deschis.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private String country;` lângă `poster`.
2. În constructorul complet, adaugă `String country` la final și `this.country = country;`.
3. În `toString()`, adaugă `", country='" + country + '\'' +`.
4. Adaugă `getCountry()` și `setCountry(String)`.
5. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument, `"USA"`, `"SUA"`, `"UK"`.
6. În `activity_item.xml`, Card 1, după `etRelease`: `TextView` etichetă + `TextInputLayout` cu `etCountry`.
7. În `ItemActivity.java`: câmpul, `initControls()`, `fillForm()` cu `etCountry.setText(existing.getCountry())`.
8. În `saveMovie()`, ca **primă** instrucțiune: citește textul, `trim()`, iar dacă e gol — `setError`, `requestFocus`, `return`.
9. În `movie_item.xml` și adapter: `TextView`-ul `movieCountry`, cu gardă `null`.
10. Verifică: Run, lasă țara goală și apasă Save. Formularul trebuie să rămână deschis, cu mesajul roșu pe câmp. Scrie „Romania” și apasă din nou: se salvează și apare în listă.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 8</summary>

garda se pune la începutul lui `saveMovie()`, înainte de `Movie movie = new Movie();`. Dacă o pui după construirea obiectului, ai muncit degeaba și e ușor să uiți `return`.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 8</summary>

fără `return` după `setError`, metoda continuă, salvează filmul cu țara goală, apelează `setResult(RESULT_OK)` și `finish()` — adică exact ce voiai să împiedici, doar cu un mesaj roșu afișat o clipă.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** lanțul complet de la 17.1 pentru `country`, plus o gardă la începutul lui `saveMovie`.

**Cod:**

Pasul 1 — `model/Movie.java`:

```java
private String country;

public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String country) {
    // ... celelalte atribuiri ...
    this.country = country;
}

", country='" + country + '\'' +

public String getCountry() {
    return country;
}

public void setCountry(String country) {
    this.country = country;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 1 (Basics), după `etRelease`:

```xml
<TextView
    android:id="@+id/tvCountry"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Country"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etCountry"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Country"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Pasul 3 — `activities/ItemActivity.java`, cu validarea în `saveMovie`:

```java
// 3a. câmpul
private EditText etCountry;

// 3b. initControls()
etCountry = findViewById(R.id.etCountry);

// 3c. fillForm()
etCountry.setText(existing.getCountry());

// 3d. saveMovie() — PRIMA instrucțiune din metodă
private void saveMovie() {
    String country = etCountry.getText().toString().trim();
    if (country.isEmpty()) {
        etCountry.setError("Country is required");
        etCountry.requestFocus();
        return;                       // ← fără el, salvarea continuă
    }

    Movie movie = new Movie();
    // ... restul metodei, neschimbat ...
    movie.setCountry(country);        // folosești variabila deja curățată
    // ...
}
```

Pasul 4 — `res/layout/movie_item.xml`, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieCountry"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Country"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 5 — `MovieAdapter.java`:

```java
private final TextView movieCountry;

movieCountry = itemView.findViewById(R.id.movieCountry);

movieCountry.setText(movie.getCountry() != null ? movie.getCountry() : "");
```

Pasul 6 — `MainActivity.addSampleMovies()`: al 11-lea argument, `"USA"`, `"SUA"`, etc.

**De ce:** `return` după eroare. Fără el, metoda continuă, construiește `Movie`-ul cu țara goală, apelează `setResult(RESULT_OK)` și `finish()` — adică exact ce voiai să împiedici, doar cu un mesaj roșu afișat o clipă.

**De reținut:**
1. **Validezi înainte de a construi obiectul.** Dacă validezi la final, după `new Movie()`, ai muncit degeaba și riscă să uiți `return`.
2. **`trim()` înainte de `isEmpty()`.** Un câmp cu un singur spațiu nu e „gol” pentru `String.isEmpty()`, dar e gol pentru un om. `"   ".trim().isEmpty()` → `true`.
3. **Eroarea nu dispare singură.** `setError(...)` rămâne pe câmp până o ștergi cu `setError(null)`. Fișierul face deja asta pentru `etRelease` în callback-ul datei — același pattern.
4. **`etCountry.setError` vs `TextInputLayout.setError`.** Prima variantă e cea folosită deja în fișier și afișează un popup cu iconiță. A doua afișează mesajul sub chenar, fără popup — dar îți trebuie o referință la `TextInputLayout`, nu la `EditText`. Ambele funcționează cu `app:hintEnabled="false"`.
5. **Nu valida în `fillForm`.** La editare, un film vechi fără țară trebuie să se poată deschide; eroarea apare doar când apeși Save.
6. `requestFocus()` mută cursorul pe câmpul greșit. Fără el, utilizatorul vede eroarea dar trebuie să caute câmpul.

**Unde se aplică:** orice câmp obligatoriu — `country`, `title`, `email`. Pentru mai multe câmpuri, repeți garda pentru fiecare, în ordinea din formular, și faci un singur `return` după toate.

</details>

---

## Exercițiul 17.8 — `awarded` (boolean) cu chip condiționat

**Cerință:** Adăugați filmului atributul `awarded` (boolean) — filmul a câștigat un premiu. În formular, o bifă. În card, un chip „Awarded” care apare **doar** dacă atributul e `true`.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private boolean awarded;` lângă `watched`.
2. În constructorul complet, adaugă `boolean awarded` la final și `this.awarded = awarded;`.
3. În `toString()`, adaugă `", awarded=" + awarded +`.
4. Adaugă `isAwarded()` și `setAwarded(boolean)`.
5. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument, `true` sau `false`.
6. În `activity_item.xml`, Card 3, după `RadioGroup`-ul `rgApproval`: un `MaterialCheckBox` cu id `cbAwarded` și text „Awarded”.
7. În `ItemActivity.java`: câmpul `private CheckBox cbAwarded;`, `initControls()`, `fillForm()` cu `setChecked(existing.isAwarded())`, `saveMovie()` cu `movie.setAwarded(cbAwarded.isChecked())`.
8. În `movie_item.xml`, în `movieStatusGroup`, după `chipWatchlist`: un `Chip` cu id `chipAwarded`.
9. În adapter: câmpul, `findViewById`, apoi în `bind()` — `chipAwarded.setVisibility(movie.isAwarded() ? View.VISIBLE : View.GONE)`, cu ambele ramuri.
10. Verifică: Run, adaugă un film bifat — în listă apare `awarded=true`. După ce faci `RecyclerView` (capitolul 11), derulează lista până la un film nebifat: chip-ul „Awarded” nu trebuie să apară.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 6</summary>

`MaterialCheckBox` extinde `CheckBox`, deci îl poți ține într-un câmp `CheckBox` — exact cum face fișierul cu `cbOnWatchList`: declarat `CheckBox` în Java, construit ca `MaterialCheckBox` în XML.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 9</summary>

scrie `setVisibility(movie.isAwarded() ? View.VISIBLE : View.GONE)`, nu un `if` fără `else`. `ViewHolder`-urile sunt reciclate: un rând care a afișat un film premiat e refolosit pentru unul nepremiat și păstrează chip-ul.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat atributul, o bifă în formular și un chip în `movieStatusGroup`, cu vizibilitate setată la fiecare `bind`.

**Cod:**

Pasul 1 — `model/Movie.java`:

```java
private boolean awarded;

public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, boolean awarded) {
    // ... celelalte atribuiri ...
    this.awarded = awarded;
}

", awarded=" + awarded +

public boolean isAwarded() {
    return awarded;
}

public void setAwarded(boolean awarded) {
    this.awarded = awarded;
}
```

Pasul 2 — `res/layout/activity_item.xml`, în Card 3 (Your verdict), după `RadioGroup`:

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/cbAwarded"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Awarded" />
```

Pasul 3 — `activities/ItemActivity.java`:

```java
// 3a. câmpul — CheckBox simplu, deja importat
private CheckBox cbAwarded;

// 3b. initControls()
cbAwarded = findViewById(R.id.cbAwarded);

// 3c. fillForm()
cbAwarded.setChecked(existing.isAwarded());

// 3d. saveMovie()
movie.setAwarded(cbAwarded.isChecked());
```

Pasul 4 — `res/layout/movie_item.xml`, în `movieStatusGroup`, după `chipWatchlist`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipAwarded"
    style="@style/Widget.Material3.Chip.Suggestion"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Awarded"
    android:clickable="false"
    app:chipMinHeight="28dp"
    app:chipIcon="@android:drawable/star_on"
    app:ensureMinTouchTargetSize="false" />
```

Pasul 5 — `MovieAdapter.java`:

```java
private final Chip chipAwarded;

chipAwarded = itemView.findViewById(R.id.chipAwarded);

// în bind() — OBLIGATORIU la fiecare rând, nu doar când e true
chipAwarded.setVisibility(movie.isAwarded() ? View.VISIBLE : View.GONE);
```

Pasul 6 — `MainActivity.addSampleMovies()`: al 11-lea argument, `true` sau `false`, la toate trei.

**De ce:** `setVisibility` cu ambele ramuri. Un `if (movie.isAwarded()) chipAwarded.setVisibility(View.VISIBLE);` fără `else` e bug-ul clasic de `RecyclerView`: rândul reciclat păstrează starea filmului precedent, iar un film fără premiu apare cu chip-ul „Awarded” de la vecinul de dinainte.

**De reținut:**
1. **`bind()` trebuie să seteze vizibilitatea de fiecare dată.** `ViewHolder`-urile sunt reciclate — un rând care a afișat un film premiat e refolosit pentru unul nepremiat. Dacă nu resetezi, chip-ul rămâne. Regula: orice proprietate care depinde de date se setează în `bind`, nu în constructor.
2. **`View.GONE` în `ChipGroup`.** `GONE` scoate chip-ul din aranjament, deci celelalte chips se strâng. `INVISIBLE` păstrează spațiul și lasă o gaură între chips.
3. **`isAwarded()`, nu `getAwarded()`.** Convenția pentru `boolean` e `isX()`.
4. **La `d719ffc` chip-ul nu se vede deloc.** `movie_item.xml` nu e folosit de `ListView` (vezi 17.1, punctul 3). Efectul vizibil la commit e doar `awarded=true` în `toString()`. Pașii 4–5 devin reali după mutarea pe `RecyclerView` (capitolul 11).
5. Bifa e `MaterialCheckBox`, dar câmpul Java e `CheckBox` — `MaterialCheckBox` extinde `CheckBox`, deci `findViewById` într-un `CheckBox` funcționează. La fel face și fișierul cu `cbOnWatchList`.

**Unde se aplică:** orice element de UI condiționat — chip-uri, iconițe, badge-uri, secțiuni întregi.

</details>

---

## Exercițiul 17.9 — `cast` (ArrayList\<Actor\>): atributul compus

**Cerință:** Adăugați o clasă `Actor` cu două câmpuri, `name` și `role`, și atributul `cast` (ArrayList\<Actor\>) în `Movie`. În formular, actorii se scriu ca `Nume:Rol`, separați prin virgulă. În listă, apar ca `Nume (Rol)`.

**Fișiere atinse:** `model/Actor.java` (fișier nou), `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Creează `model/Actor.java` **înainte** de orice altceva: pachet `ro.ase.ie.g1097.model`, `implements Serializable`, câmpurile `name` și `role`, constructor gol, constructor cu doi parametri, getteri/setteri, `toString()` care întoarce `name + " (" + role + ")"`.
2. Deschide `model/Movie.java`. Adaugă `import java.util.ArrayList;` și câmpul `private ArrayList<Actor> cast = new ArrayList<>();`.
3. În constructorul complet, adaugă `ArrayList<Actor> cast` la final și `this.cast = cast;`.
4. În `toString()`, adaugă `", cast=" + cast +`.
5. Adaugă `getCast()` și `setCast(ArrayList<Actor>)`.
6. Compilează și repară cele trei apeluri din `addSampleMovies()`: al 11-lea argument e o listă de `Actor`, `new ArrayList<>(Arrays.asList(new Actor("...", "..."), ...))`.
7. În `activity_item.xml`, Card 1, după `etRelease`: `TextView` etichetă + `TextInputLayout` cu `etCast` și `app:helperText="Name:Role, Name:Role"`.
8. În `ItemActivity.java`: câmpul, `initControls()`, `fillForm()` cu `castToText(...)`, `saveMovie()` cu `parseCast(...)`. Scrie cele două metode private la finalul clasei.
9. În `movie_item.xml` și adapter: `TextView`-ul `movieCast`, legat cu `TextUtils.join(", ", movie.getCast())` — cu `import android.text.TextUtils;`.
10. Verifică: Run, scrie `Tom Hanks:Forrest, Robin Wright:Jenny` și salvează. Nu trebuie să apară `NotSerializableException`. În listă apare `cast=[Tom Hanks (Forrest), Robin Wright (Jenny)]`. Redeschide filmul: câmpul arată din nou `Tom Hanks:Forrest, Robin Wright:Jenny`, nu formatul cu paranteze.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 1</summary>

`implements Serializable` pe `Actor` nu e opțional. `Movie` pleacă prin `Intent.putExtra(String, Serializable)` și serializarea parcurge tot graful de obiecte — un `Actor` ne-serializabil dă `NotSerializableException` la Save, nu la compilare.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 8</summary>

folosește `entry.split(":", 2)`, cu limita 2. Fără limită, un rol care conține `:` produce trei elemente, `parts.length == 2` devine fals și intrarea e aruncată fără niciun mesaj.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am creat clasa `Actor`, am adăugat lista în `Movie`, am scris două metode de conversie în `ItemActivity` (text → listă și listă → text) și am afișat lista în card.

**Cod:**

Pasul 1 — `model/Actor.java`, fișier nou:

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;

public class Actor implements Serializable {   // ← obligatoriu

    private String name;
    private String role;

    public Actor() {
    }

    public Actor(String name, String role) {
        this.name = name;
        this.role = role;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    // formatul pentru CARD, nu pentru formular
    @Override
    public String toString() {
        return name + " (" + role + ")";
    }
}
```

Pasul 2 — `model/Movie.java`:

```java
import java.util.ArrayList;   // import nou

// 2a. câmpul
private ArrayList<Actor> cast = new ArrayList<>();

// 2b. constructor
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, ArrayList<Actor> cast) {
    // ... celelalte atribuiri ...
    this.cast = cast;
}

// 2c. toString() — folosește Actor.toString()
", cast=" + cast +

// 2d. getter/setter
public ArrayList<Actor> getCast() {
    return cast;
}

public void setCast(ArrayList<Actor> cast) {
    this.cast = cast;
}
```

Pasul 3 — `res/layout/activity_item.xml`, în Card 1 (Basics), după `etRelease`:

```xml
<TextView
    android:id="@+id/tvCast"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:layout_marginBottom="4dp"
    android:text="Cast"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text"
    app:helperText="Name:Role, Name:Role">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etCast"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Cast"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

Pasul 4 — `activities/ItemActivity.java`, cu două metode noi:

```java
import java.util.ArrayList;   // import nou

// 4a. câmpul
private EditText etCast;

// 4b. initControls()
etCast = findViewById(R.id.etCast);

// 4c. fillForm() — listă → text
etCast.setText(existing.getCast() != null ? castToText(existing.getCast()) : "");

// 4d. saveMovie() — text → listă
movie.setCast(parseCast(etCast.getText().toString()));

// 4e. cele două metode, la finalul clasei
private ArrayList<Actor> parseCast(String text) {
    ArrayList<Actor> cast = new ArrayList<>();
    for (String entry : text.split(",")) {
        String[] parts = entry.split(":", 2);      // limit 2 — vezi mai jos
        if (parts.length == 2) {
            String name = parts[0].trim();
            String role = parts[1].trim();
            if (!name.isEmpty()) {
                cast.add(new Actor(name, role));
            }
        }
    }
    return cast;
}

private String castToText(ArrayList<Actor> cast) {
    StringBuilder sb = new StringBuilder();
    for (Actor actor : cast) {
        if (sb.length() > 0) {
            sb.append(", ");
        }
        sb.append(actor.getName()).append(":").append(actor.getRole());
    }
    return sb.toString();
}
```

Pasul 5 — `res/layout/movie_item.xml`, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieCast"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Cast"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 6 — `MovieAdapter.java`:

```java
import android.text.TextUtils;   // import nou

private final TextView movieCast;

movieCast = itemView.findViewById(R.id.movieCast);

// TextUtils.join apelează toString() pe fiecare element
movieCast.setText(movie.getCast() != null
        ? TextUtils.join(", ", movie.getCast())
        : "");
```

Pasul 7 — `MainActivity.addSampleMovies()`: al 11-lea argument e o listă de `Actor`:

```java
        "https://example.com/posters/inception.jpg",
        new ArrayList<>(Arrays.asList(
                new Actor("Leonardo DiCaprio", "Cobb"),
                new Actor("Joseph Gordon-Levitt", "Arthur")))));
```

**De ce:** `Actor` trebuie să fie `Serializable` pentru că `Movie` călătorește prin `Intent.putExtra(String, Serializable)`, iar serializarea Java parcurge **tot graful de obiecte**. Un `Actor` ne-serializabil nu dă eroare la compilare — dă `NotSerializableException` la runtime, exact când apeși Save, adică în fața profesorului.

**De reținut:**
1. **`implements Serializable` pe `Actor` e obligatoriu.** `ArrayList` e serializabil, dar asta nu ajută: fiecare element trebuie să fie și el. Simptomul e clar — formularul funcționează, iar la Save aplicația se închide cu `NotSerializableException: ro.ase.ie.g1097.model.Actor`.
2. **`split(":", 2)` și nu `split(":")`.** Cu limita 2, tot ce e după primul `:` rămâne în al doilea element: `"Robert Downey Jr.:Tony Stark:Iron Man"` → rol `"Tony Stark:Iron Man"`. Fără limită → trei elemente, `parts.length == 2` e fals, iar intrarea e aruncată tacit.
3. **Două formate, două metode.** `Actor.toString()` dă `"Tom Hanks (Forrest)"` — format de **afișare**. Câmpul text cere `"Tom Hanks:Forrest"` — format de **intrare**. Dacă încerci să faci round-trip prin `toString()`, parsezi paranteze și te spargi la primul nume cu paranteză. De aceea `castToText` construiește explicit `Nume:Rol`.
4. **`String.join` nu merge pe `List<Actor>`.** Semnătura e `String.join(CharSequence, Iterable<? extends CharSequence>)`, iar `Actor` nu e `CharSequence` — eroare de compilare. `TextUtils.join(CharSequence, Iterable<?>)` acceptă orice și apelează `toString()` pe fiecare element. De aici importul.
5. **`parts.length == 2` aruncă intrările fără `:`.** E o decizie: `"Tom Hanks"` singur nu are rol, deci nu devine `Actor`. Alternativa e să accepți rol gol — dar atunci cardul afișează `Tom Hanks ()`.
6. **Constructorul gol din `Actor`** nu e folosit de cod, dar îl păstrezi: orice clasă de model care va ajunge în `Gson`, `Room` sau `Parcelable` are nevoie de el. Costă două linii.
7. **Ordinea pașilor contează mai mult ca la 17.1.** Dacă faci `Movie` înainte de `Actor`, nu compilează nimic. Fișierul nou întâi, apoi modelul care îl folosește.

**Unde se aplică:** orice atribut compus — `cast`, `awards` (listă de obiecte), `screenings` (listă de ore + sală).

</details>

---

## Exercițiul 17.10 — `writer` + `popular`: cele două cerințe, în 30 de minute

**Cerință:** Adăugați filmului două atribute: `writer` (String) și `popular` (boolean). Ambele trebuie să apară în formular și în listă. Timp: 30 de minute.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `res/layout/movie_item.xml`, `activities/MainActivity.java`, `MovieAdapter.java` (opțional).

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java` și fă **ambele** atribute într-o singură trecere: cele două câmpuri, ambii parametri în constructor, ambele linii din `toString()`, toți patru getteri/setteri.
2. Compilează imediat. Repară cele trei apeluri din `addSampleMovies()` — două argumente noi fiecare, în ordinea `writer`, `popular`.
3. Deschide `activity_item.xml` o singură dată: `etWriter` în Card 1 după `etRelease`, `swPopular` în Card 3 după `rgApproval`.
4. Deschide `ItemActivity.java` o singură dată: ambele câmpuri, ambele `findViewById` în `initControls()`, ambele linii în `fillForm()`, ambele în `saveMovie()`.
5. Deschide `movie_item.xml` o singură dată: `movieWriter` și `moviePopular`, lipite, după `movieFacts`.
6. În adapter: două câmpuri, două `findViewById`, două `setText`.
7. Verifică în trei atingeri: adaugă un film cu ambele completate → apare în listă; editează și schimbă doar `writer` → `popular` rămâne cum era; golește `writer` → câmpul devine gol, nu păstrează valoarea veche.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 1</summary>

nu face lanțul de cinci pași de două ori. Deschizi fiecare fișier o singură dată și pui ambele atribute în aceeași editare — cinci treceri, nu zece. La examen diferența e între a termina în 20 de minute și a nu termina.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 2</summary>

ordinea argumentelor din constructor trebuie respectată la toate trei apelurile: `..., poster, writer, popular`. Aici compilatorul te prinde, pentru că `String` și `boolean` nu se pot confunda. Dacă ambele atribute noi ar fi fost `String`, o inversare ar fi compilat și ar fi salvat scenaristul în câmpul de țară, fără nicio eroare.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am tratat cele două atribute ca un singur val de modificări — cinci fișiere, cinci treceri, ambele atribute în fiecare.

**Cod:**

Pasul 1 — `model/Movie.java`, ambele câmpuri într-o singură editare:

```java
// 1a. câmpurile
private String writer;
private boolean popular;

// 1b. constructorul — două argumente noi, în ordinea writer, popular
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String writer, boolean popular) {
    // ... celelalte atribuiri ...
    this.writer = writer;
    this.popular = popular;
}

// 1c. toString() — două linii
", writer='" + writer + '\'' +
", popular=" + popular +

// 1d. getteri/setteri — patru metode
public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}

public boolean isPopular() {
    return popular;
}

public void setPopular(boolean popular) {
    this.popular = popular;
}
```

Pasul 2 — `res/layout/activity_item.xml`, ambele câmpuri în aceeași vizită:

```xml
<!-- Card 1 (Basics), după etRelease: etWriter -->
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etWriter"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Writer"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>

<!-- Card 3 (Your verdict), după rgApproval: swPopular -->
<com.google.android.material.materialswitch.MaterialSwitch
    android:id="@+id/swPopular"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Popular" />
```

Pasul 3 — `activities/ItemActivity.java`, șase locuri, o singură trecere:

```java
// 3a. câmpurile
private EditText etWriter;
private MaterialSwitch swPopular;

// 3b. initControls()
etWriter = findViewById(R.id.etWriter);
swPopular = findViewById(R.id.swPopular);

// 3c. fillForm()
etWriter.setText(existing.getWriter());
swPopular.setChecked(existing.isPopular());

// 3d. saveMovie()
movie.setWriter(etWriter.getText().toString());
movie.setPopular(swPopular.isChecked());
```

Pasul 4 — `res/layout/movie_item.xml`, două `TextView`-uri lipite, după `movieFacts`:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Writer"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />

<TextView
    android:id="@+id/moviePopular"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Popular"
    android:textSize="13sp"
    android:textColor="#9E9E9E" />
```

Pasul 5 — `MovieAdapter.java`, două câmpuri, două `findViewById`, două `setText`:

```java
private final TextView movieWriter;
private final TextView moviePopular;

movieWriter = itemView.findViewById(R.id.movieWriter);
moviePopular = itemView.findViewById(R.id.moviePopular);

movieWriter.setText(movie.getWriter() != null ? movie.getWriter() : "");
moviePopular.setText(movie.isPopular() ? "Popular" : "");
```

Pasul 6 — `MainActivity.addSampleMovies()`: **două** argumente noi la **fiecare** dintre cele trei apeluri:

```java
        "https://example.com/posters/inception.jpg",
        "Christopher Nolan",   // writer
        true));                // popular
```

**De ce:** două atribute înseamnă două valori, nu două lanțuri. Modelul se editează o dată pentru ambele câmpuri, formularul o dată pentru ambele widget-uri, activitatea o dată pentru ambele perechi citire/scriere. Zece treceri devin cinci, iar la examen diferența e între a termina în 20 de minute și a nu termina.

**De reținut:**
1. **Ordinea parametrilor din constructor trebuie respectată la toate cele trei apeluri.** Aici compilatorul te ajută: `String` și `boolean` nu se pot confunda. Dar dacă cele două atribute noi ar fi fost amândouă `String`, o inversare ar fi compilat și ar fi salvat scenaristul în câmpul de țară — fără nicio eroare. Compilatorul te prinde doar când tipurile diferă.
2. **Compilează după pasul 1, înainte de XML.** Imediat ce schimbi semnătura constructorului, `addSampleMovies` are trei erori. Le vezi în `Build`, le repari, apoi treci la UI. Dacă lași totul pentru final, nu mai știi care eroare vine de la ce.
3. **`fillForm` și `saveMovie` se fac împreună, per atribut.** Un atribut cu `fillForm` dar fără `saveMovie` nu se salvează niciodată; unul cu `saveMovie` dar fără `fillForm` se resetează la fiecare editare. Ambele se compilează.
4. **Bugetul de timp, realist:** 2 min model + 8 min formular + 8 min activitate + 4 min card + 4 min adapter + 4 min build și verificare pe emulator = 30.
5. **Verificarea finală, în trei atingeri:** adaugi un film nou cu ambele completate → apare în listă; îl editezi și schimbi doar `writer` → `popular` rămâne cum era; îl editezi și golești `writer` → câmpul devine gol, nu rămâne valoarea veche.
6. Dacă profesorul cere „în listă” și ești pe `d719ffc`, pasul care contează e `toString()`: fără cele două linii din 1c, valorile se salvează dar nu se văd (vezi 17.1, punctul 3).

**Unde se aplică:** exact formatul de examen. Orice combinație de două atribute — `writer` + `popular`, `country` + `year`, `awarded` + `imdbScore` — se rezolvă cu aceleași cinci treceri.

</details>
