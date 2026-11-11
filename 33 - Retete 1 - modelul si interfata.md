# Capitolul 33 — Rețete 1: modelul și interfața

**Obiectiv:** pentru fiecare cerință care atinge modelul (`Movie`) sau interfața (formularul, lista, un ecran nou), să ai pașii exacți, în ordine, cu codul minim care compilează, cu explicația mecanismului și cu greșeala care costă puncte.

**Timp estimat:** 150–180 min pentru toate cele 16 rețete; 10–15 min pentru una singură, cât îți rămâne la test pentru o cerință.

**Sursa:** aplicația G1097 (Movies), commit `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`, `strings.xml`.

**Regula de aur:** la test ai **2 cerințe în 30 de minute**. O rețetă de aici trebuie să încapă în 10–15 minute, cu timp pentru verificare. Dacă îți ia mai mult, ai sărit un pas sau ai rescris un fișier întreg în loc să adaugi o linie.

---

## 33.0 Ce ai în mână

### Fișierele aplicației

| Fișier | Rol | Ce modifici cel mai des |
|---|---|---|
| `Movie.java` | modelul: 10 câmpuri private, constructor cu 10 parametri, constructor gol, getteri/setteri, `toString()` | câmp nou, getter/setter, constructor, `toString()` |
| `activity_item.xml` | formularul din `ItemActivity`: `ScrollView` → `LinearLayout` → 4 carduri | widget nou, tip nou de input |
| `ItemActivity.java` | citește formularul și construiește `Movie`; `findViewById`, `fillForm`, `saveMovie` | câmp, `findViewById`, `fillForm`, `saveMovie` |
| `activity_main.xml` | ecranul principal: `FrameLayout` cu `ListView` și `FloatingActionButton` | control deasupra listei |
| `MainActivity.java` | ține `List<Movie> movies`, `ArrayAdapter<Movie> movieAdapter`, `ActivityResultLauncher<Intent> launcher` | date demo, adapter, listeneri |
| `movie_item.xml` | rândul de `RecyclerView` — **există, dar nu e folosit de niciun cod** | doar când migrezi la `RecyclerView` |
| `AndroidManifest.xml` | declară cele două activități | ecran nou |
| `strings.xml` | `app_name`, `items` (20 de texte demo), `movie_genre` (10 genuri) | array nou pentru un `Spinner` |

> **Atenție la `movie_item.xml`:** fișierul este pregătit pentru `RecyclerView`, dar în G1097 **nu este inflate nicăieri**. `MainActivity` folosește `ArrayAdapter` cu `android.R.layout.simple_list_item_1`. Orice widget adaugi în `movie_item.xml` nu se vede până nu faci migrarea din capitolul 23. Spun asta explicit la rețeta 33.12.

`ItemActivity` folosește `findViewById`, **nu** ViewBinding: cele 13 view-uri sunt câmpuri declarate la nivelul clasei (`etTitle`, `etRelease`, `spGenre`, `etBudget`, `sbDuration`, `rbRating`, `rgApproval`, `cbonWatchList`, `swWatched`, `etPoster`, `btMovieAction`, `tvDurationValue`, `tvWatchedValue`) și sunt inițializate în `initControls()`, după `setContentView`. `Movie implements Serializable`, de aceea poate fi trimis prin `Intent.putExtra` și citit cu `IntentCompat.getSerializableExtra`.

### Modelul `Movie` — cele 10 câmpuri

| Câmp | Tip | Widget care îl produce | Getter |
|---|---|---|---|
| `title` | `String` | `etTitle` (`TextInputEditText`) | `getTitle()` |
| `release` | `Date` | `etRelease` + `DatePickerDialog` | `getRelease()` |
| `genre` | `String` | `spGenre` (`Spinner`) | `getGenre()` |
| `budget` | `double` | `etBudget` (`TextInputEditText`, `numberDecimal`) | `getBudget()` |
| `duration` | `int` | `sbDuration` (`SeekBar`) | `getDuration()` |
| `rating` | `float` | `rbRating` (`RatingBar`) | `getRating()` |
| `watched` | `boolean` | `swWatched` (`MaterialSwitch`) | `isWatched()` |
| `approval` | `String` | `rgApproval` (`RadioGroup`) | `getApproval()` |
| `onWatchlist` | `boolean` | `cbonWatchList` (`MaterialCheckBox`) | `isOnWatchlist()` |
| `poster` | `String` | `etPoster` (`TextInputEditText`, `textUri`) | `getPoster()` |

Constructorul cu parametri are **exact 10 parametri, în ordinea din tabel**. Există și `public Movie() {}` — constructorul gol, folosit de `saveMovie()`.

### Fluxul de date

```
MainActivity                          ItemActivity
  movies: List<Movie>                   formular (13 view-uri)
  movieAdapter: ArrayAdapter<Movie>     releaseCal: Calendar
  launcher: ActivityResultLauncher      position: int (-1 = insert)
        |                                     ^
        |  Intent + MOVIE_EXTRA (Movie)       |
        +-------------------------------------+
        |  Intent + MOVIE_EXTRA + POSITION_EXTRA
        v                                     |
  onActivityResult: add() sau set()           |
  movieAdapter.notifyDataSetChanged()         |
```

### Regula celor patru straturi

Orice cerință care atinge un atribut nou trece prin **aceleași patru straturi, în ordinea asta**:

1. **Modelul** — `Movie.java`: câmp, getter, setter, constructor, `toString()`.
2. **Formularul** — `activity_item.xml`: widget cu `android:id`.
3. **Legătura** — `ItemActivity.java`: câmp, `findViewById`, `fillForm`, `saveMovie`.
4. **Afișarea** — `toString()` (pentru `ListView`) sau `movie_item.xml` + adapter (pentru `RecyclerView`).

> **De ce ordinea contează:** dacă începi cu XML-ul, codul nu compilează până nu există câmpul în model. Dacă începi cu `ItemActivity`, `findViewById` întoarce `null` până nu există ID-ul în XML. Modelul este singurul strat care nu depinde de niciun altul — deci primul.

### Convenția de nume

| Prefix | Widget | Exemplu în G1097 |
|---|---|---|
| `et` | `EditText` / `TextInputEditText` | `etTitle`, `etBudget`, `etPoster` |
| `tv` | `TextView` | `tvDurationValue`, `tvWatchedValue` |
| `sp` | `Spinner` | `spGenre` |
| `sb` | `SeekBar` | `sbDuration` |
| `rb` | `RatingBar` / `RadioButton` | `rbRating`, `rbPG13` |
| `rg` | `RadioGroup` | `rgApproval` |
| `cb` | `CheckBox` | `cbonWatchList` |
| `sw` | `Switch` | `swWatched` |
| `btn` | `Button` | `btnMovieAction` |
| `fab` | `FloatingActionButton` | `floatingActionButton` |

> În repo există și inconsecvențe: câmpul Java se numește `cbonWatchList`, dar ID-ul este `cbOnWatchList`; câmpul este `btMovieAction`, dar ID-ul este `btnMovieAction`. **Numele câmpului și ID-ul nu trebuie să coincidă** — `findViewById(R.id.cbOnWatchList)` leagă cele două nume. Respectă exact ce este în fișier.

### Cum se citește o rețetă

Fiecare rețetă are șapte secțiuni: cerința, fișierele atinse, pașii, de ce merge, greșeala care costă puncte, verificarea, exercițiile. Pașii sunt în ordinea în care îi faci la test.

**ID-urile noi.** Rețetele care adaugă un widget creează un ID care nu există încă în aplicație — `etWriter`, `etYear`, `movieWriter`. Îl scrii exact așa cum apare în cod: `@+id/etWriter` în XML, `R.id.etWriter` în Java. Numele trebuie să fie unic în proiect și să respecte prefixul din tabelul de mai sus. Restul codului este identic cu ce trebuie să scrii: nu lipsesc linii, nu sunt prescurtări.

---

## Rețeta 33.1 — Adaugă un atribut String

### **Cerința, cum sună la test**

„Adaugă filmului numele regizorului (`writer`) și afișează-l în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmp `writer`, getter, setter, al 11-lea parametru în constructor, linie în `toString()` | da |
| 2 | `activity_item.xml` | `TextInputLayout` + `TextInputEditText` cu ID nou, în cardul „Basics" | da, dacă vrei să introduci valoarea din formular |
| 3 | `ItemActivity.java` | câmp, `findViewById`, `fillForm`, `saveMovie` | da, împreună cu pasul 2 |
| 4 | `MainActivity.java` | al 11-lea argument în cele trei `new Movie(...)` din `addSampleMovies()` | da, după ce schimbi constructorul |
| 5 | `movie_item.xml` | `TextView` pentru rând | doar dacă treci la `RecyclerView` |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, la sfârșitul listei de câmpuri.** Adaugi câmpul lângă `poster`:

```java
private String title;
private Date release;
private String genre;
private double budget;
private int duration;
private float rating;
private boolean watched;
private String approval;
private boolean onWatchlist;
private String poster = null;
private String writer;
```

**Pasul 2 — `Movie.java`, după `setPoster()`.** Getter-ul și setter-ul, în aceeași formă ca ale celorlalte câmpuri:

```java
public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}
```

**Pasul 3 — `Movie.java`, constructorul cu parametri.** Adaugi al 11-lea parametru **la sfârșit**, ca să nu miști ordinea celor existente, și îl atribui:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, String writer) {
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
    this.writer = writer;
}
```

**Pasul 4 — `Movie.java`, `toString()`.** Adaugi linia înainte de acolada de închidere a șirului:

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
            ", writer='" + writer + '\'' +
            '}';
}
```

**Pasul 5 — `activity_item.xml`, în cardul „Basics", după blocul lui `etRelease`.** Adaugi un câmp text nou. ID-ul ales aici este `etWriter`:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
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

**Pasul 6 — `ItemActivity.java`, la câmpurile clasei.** Adaugi referința, lângă `etPoster`:

```java
private EditText etPoster;
private EditText etWriter;
```

**Pasul 7 — `ItemActivity.java`, în `initControls()`.** Legătura cu XML-ul:

```java
etPoster = findViewById(R.id.etPoster);
etWriter = findViewById(R.id.etWriter);
```

**Pasul 8 — `ItemActivity.java`, în `fillForm()`.** Umpli câmpul când intri pe un film existent:

```java
etPoster.setText(existing.getPoster());
etWriter.setText(existing.getWriter());
```

**Pasul 9 — `ItemActivity.java`, în `saveMovie()`.** Citești valoarea în obiectul care pleacă spre listă:

```java
movie.setPoster(etPoster.getText().toString());
movie.setWriter(etWriter.getText().toString());
```

**Pasul 10 — `MainActivity.java`, în `addSampleMovies()`.** Constructorul are acum 11 parametri, deci toate cele trei apeluri primesc încă un argument. Primul:

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
        "Christopher Nolan"));
```

La fel pentru `"Toy Story"` și `"The Matrix"` — dacă uiți unul, exact acolo vei lua eroarea de compilare.

**Pasul 11 — doar dacă afișezi atributul într-un rând de `RecyclerView`.** În `movie_item.xml` adaugi un `TextView` în coloana de informații, iar în adapter îl legi în `ViewHolder` și îl umpli în `bind()`. În G1097 acest pas **nu are efect** pentru că `movie_item.xml` nu e folosit — vezi rețeta 33.12.

### **De ce merge așa**

`ArrayAdapter<Movie>` nu știe ce este un `Movie`: pentru fiecare rând apelează `toString()`. De aceea atributul apare în listă doar dacă îl adaugi în `toString()`. Constructorul cu parametri este singurul loc în care un `Movie` primește valori la creare; dacă adaugi câmpul și uiți parametrul, câmpul rămâne `null` pentru toate filmele demo. `findViewById` caută în arborele de view-uri construit de `setContentView`, de aceea se apelează după el, în `initControls()`, nu în declarația câmpului.

> **Atenție la copy-paste între grupe:** în G1097, `toString()` include și `poster`; în G1099, `toString()` nu îl include. Dacă lucrezi pe altă grupă, verifică fișierul înainte să adaugi linia — altfel adaugi un atribut într-un `toString()` care arată altfel decât credeai.

### **Greșeala care costă puncte**

1. **Adaugi câmpul și getter-ul, dar nu parametrul în constructor.** Simptom: codul compilează, aplicația rulează, dar toate filmele au `writer = null` și rândul se termină cu `writer='null'`. Cauza: constructorul cu 10 parametri nu are unde să primească valoarea, iar `new Movie(...)` din `addSampleMovies()` nu o trimite.
2. **Adaugi parametrul, dar nu actualizezi toate cele trei apeluri `new Movie(...)`.** Simptom: `error: constructor Movie in class Movie cannot be applied to given types; required: 11, found: 10`. Cauza: ai schimbat semnătura, dar nu apelanții. Compilatorul îți spune exact linia — citește-o înainte să te uiți la cod.
3. **Uiți `toString()`.** Simptom: completezi câmpul, apeși Save, rândul nou apare, dar arată exact ca înainte. Cauza: `ArrayAdapter` afișează `toString()`, nu câmpurile obiectului. Atributul este salvat în model, doar că nu ajunge niciodată pe ecran.

### **Verificarea**

Rulează aplicația. Lista are trei rânduri, iar fiecare se termină cu `writer='...'`. Apasă FAB-ul, completează formularul, scrie un nume la „Writer" și apasă „Save Movie": al patrulea rând conține numele. Atinge rândul: câmpul „Writer" este deja completat. Modifică numele și apasă „Update Movie": rândul se schimbă pe loc, fără să apară un al cincilea.

### **Exersează**

[17.1 — `writer` (String): atributul de referință](cap-17.html#ex-17-1) · [17.10 — `writer` + `popular`: cele două cerințe, în 30 de minute](cap-17.html#ex-17-10) · [24.7 — checklist-ul de după fiecare „adaugă un atribut"](cap-24.html#ex-24-7)

---

## Rețeta 33.2 — Adaugă un atribut numeric întreg (int)

### **Cerința, cum sună la test**

„Adaugă filmului anul în care a fost produs (`year`, `int`) și afișează-l în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmp `int year`, getter, setter, al 11-lea parametru, linie în `toString()` | da |
| 2 | `activity_item.xml` | `TextInputEditText` cu `inputType="number"` și ID nou | da, dacă îl introduci din formular |
| 3 | `ItemActivity.java` | câmp, `findViewById`, `fillForm`, `saveMovie` cu `Integer.parseInt` | da, împreună cu pasul 2 |
| 4 | `MainActivity.java` | al 11-lea argument în cele trei `new Movie(...)` | da, după ce schimbi constructorul |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, la câmpuri.** Un `int` este o valoare primitivă: nu poate fi `null`, iar valoarea implicită este `0`.

```java
private String poster = null;
private int year;
```

**Pasul 2 — `Movie.java`, getter și setter.** Pentru `int` se folosește `get`, nu `is`:

```java
public int getYear() {
    return year;
}

public void setYear(int year) {
    this.year = year;
}
```

**Pasul 3 — `Movie.java`, constructorul.** Al 11-lea parametru, la sfârșit:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, int year) {
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
    this.year = year;
}
```

**Pasul 4 — `Movie.java`, `toString()`.** Adaugi linia:

```java
", year=" + year +
```

**Pasul 5 — `activity_item.xml`, în cardul „Production", după blocul bugetului.** Câmpul numeric:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etYear"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Year"
        android:inputType="number" />
</com.google.android.material.textfield.TextInputLayout>
```

**Pasul 6 — `ItemActivity.java`, la câmpuri.**

```java
private EditText etYear;
```

**Pasul 7 — `ItemActivity.java`, în `initControls()`.**

```java
etYear = findViewById(R.id.etYear);
```

**Pasul 8 — `ItemActivity.java`, în `fillForm()`.** Aici este capcana de tip: `setText` are două variante utile — `setText(CharSequence)` și `setText(int)`. Dacă îi dai un `int`, Java alege `setText(int)`, care îl tratează ca **ID de resursă**, nu ca text:

```java
etYear.setText(String.valueOf(existing.getYear()));
```

**Pasul 9 — `ItemActivity.java`, în `saveMovie()`.** `getText()` întoarce un `Editable`, nu un număr; conversia o faci tu, cu protecție pentru câmpul gol:

```java
String rawYear = etYear.getText().toString().trim();
movie.setYear(rawYear.isEmpty() ? 0 : Integer.parseInt(rawYear));
```

**Pasul 10 — `MainActivity.java`, în `addSampleMovies()`.** Al 11-lea argument, un `int` fără ghilimele:

```java
"https://example.com/posters/inception.jpg",
2010));
```

### **De ce merge așa**

`int` este primitiv: nu are `null`, iar dacă nu îl inițializezi, valoarea lui este `0`. `Integer.parseInt` transformă un șir în `int` și aruncă `NumberFormatException` dacă șirul nu este un număr întreg — de aceea câmpul gol trebuie prins înainte. `String.valueOf(int)` face conversia inversă și este obligatoriu la `setText`, pentru că altfel se apelează supraîncărcarea `setText(int)`, care caută o resursă cu acel număr.

### **Greșeala care costă puncte**

1. **`Integer.parseInt` pe câmp gol.** Simptom: apeși Save fără să completezi anul și aplicația se închide cu `NumberFormatException: For input string: ""`. Cauza: ai sărit verificarea `isEmpty()`. Aceeași eroare apare și pentru `"2010 "` cu spațiu — de aceea `.trim()`.
2. **`etYear.setText(existing.getYear())`.** Simptom: `Resources.NotFoundException` când intri în editare pe un film existent. Cauza: `setText(int)` tratează numărul ca ID de resursă. Corect este `String.valueOf(...)`.
3. **Uiți al 11-lea argument într-un singur `new Movie(...)`.** Simptom: eroare de compilare în `addSampleMovies()`, cu numărul de argumente cerute și găsite. Cauza: constructorul s-a schimbat, apelurile nu.

### **Verificarea**

Rulează aplicația: fiecare rând conține `year=...`. Adaugă un film cu anul `2024` și verifică al patrulea rând. Atinge rândul: câmpul „Year" arată `2024`, nu un număr de resursă și nu `0`. Lasă câmpul gol la un film nou și apasă Save: aplicația rămâne deschisă, iar rândul arată `year=0`.

### **Exersează**

[17.2 — `year` (Integer): atributul numeric care poate fi null](cap-17.html#ex-17-2) · [17.6 — `ageRestriction` (int): slider-ul cu valoare afișată](cap-17.html#ex-17-6) · [19.10 — combo de examen: valoare în etichetă + eroare de validare](cap-19.html#ex-19-10)

---

## Rețeta 33.3 — Adaugă un atribut Integer care poate fi null

### **Cerința, cum sună la test**

„Adaugă filmului numărul de premii Oscar (`oscars`), care poate să lipsească, și afișează-l în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmp `Integer oscars`, getter, setter, al 11-lea parametru, linie în `toString()` | da |
| 2 | `activity_item.xml` | `TextInputEditText` cu `inputType="number"` și ID nou | da, dacă îl introduci din formular |
| 3 | `ItemActivity.java` | câmp, `findViewById`, `fillForm` cu verificare de `null`, `saveMovie` cu valoare sau `null` | da, împreună cu pasul 2 |
| 4 | `MainActivity.java` | al 11-lea argument: un număr sau `null` | da, după ce schimbi constructorul |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, la câmpuri.** `Integer` este clasa-ambalaj a lui `int`: este o referință, deci poate fi `null`.

```java
private String poster = null;
private Integer oscars;
```

**Pasul 2 — `Movie.java`, getter și setter.**

```java
public Integer getOscars() {
    return oscars;
}

public void setOscars(Integer oscars) {
    this.oscars = oscars;
}
```

**Pasul 3 — `Movie.java`, constructorul.** Al 11-lea parametru este `Integer`, nu `int`:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, Integer oscars) {
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
    this.oscars = oscars;
}
```

**Pasul 4 — `Movie.java`, `toString()`.** `null` se afișează ca textul `null`, nu crapă:

```java
", oscars=" + oscars +
```

**Pasul 5 — `activity_item.xml`, în cardul „Production".**

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etOscars"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Oscars (optional)"
        android:inputType="number" />
</com.google.android.material.textfield.TextInputLayout>
```

**Pasul 6 — `ItemActivity.java`, la câmpuri.**

```java
private EditText etOscars;
```

**Pasul 7 — `ItemActivity.java`, în `initControls()`.**

```java
etOscars = findViewById(R.id.etOscars);
```

**Pasul 8 — `ItemActivity.java`, în `fillForm()`.** Aici sunt două capcane într-o linie. `existing.getOscars()` poate fi `null`, iar `setText` cu un `Integer` se rezolvă la `setText(int)` prin unboxing:

```java
etOscars.setText(existing.getOscars() == null ? "" : String.valueOf(existing.getOscars()));
```

**Pasul 9 — `ItemActivity.java`, în `saveMovie()`.** Câmpul gol înseamnă „nu există valoare", adică `null`, nu `0`:

```java
String rawOscars = etOscars.getText().toString().trim();
movie.setOscars(rawOscars.isEmpty() ? null : Integer.parseInt(rawOscars));
```

**Pasul 10 — `MainActivity.java`, în `addSampleMovies()`.** Poți trimite un număr sau `null`:

```java
"https://example.com/posters/inception.jpg",
4));
```

La un film fără premii, al 11-lea argument este `null`.

### **De ce merge așa**

`Integer` este o referință, deci are două stări pe care `int` nu le are: o valoare și `null`. `null` este exact răspunsul corect la „nu știu" — dacă ai folosi `0`, ai afirma că filmul are zero premii. La citire, `Integer.parseInt` întoarce `int`, iar atribuirea îl împachetează automat în `Integer` (autoboxing). La scriere, `String.valueOf(Object)` acceptă și `null` și întoarce textul `"null"`, de aceea în `fillForm` verifici întâi și pui șir gol.

### **Greșeala care costă puncte**

1. **`etOscars.setText(existing.getOscars())`.** Simptom: `Resources.NotFoundException` la editare, sau un număr afișat ca resursă. Cauza: `Integer` se unboxează la `int`, iar Java alege `setText(int)`, varianta care primește un ID de resursă. `String.valueOf(...)` este obligatoriu.
2. **`existing.getOscars().intValue()` fără verificare de `null`.** Simptom: `NullPointerException` în `fillForm` pe filmele fără premii. Cauza: ai presupus că valoarea există. Verifici `== null` înainte de orice operație.
3. **Trimiți `0` în loc de `null` pentru „lipsește".** Simptom: nu crapă nimic, dar lista arată `oscars=0` pentru filme despre care nu știi nimic. Cauza: ai folosit `int` sau ai pus `0` ca valoare implicită. Diferența dintre „zero" și „necunoscut" este exact motivul pentru care cerința cere `Integer`.

### **Verificarea**

Adaugă un film cu `3` la Oscars: rândul arată `oscars=3`. Atinge rândul: câmpul arată `3`. Șterge valoarea, apasă Update: rândul arată `oscars=null`, iar aplicația nu se închide. Adaugă un film nou cu câmpul gol: `oscars=null`, fără excepție.

### **Exersează**

[17.2 — `year` (Integer): atributul numeric care poate fi null](cap-17.html#ex-17-2) · [19.8 — `fillForm` crapă când `release` e `null`](cap-19.html#ex-19-8)

---

## Rețeta 33.4 — Adaugă un atribut zecimal (float / double)

### **Cerința, cum sună la test**

„Adaugă filmului nota IMDb (`imdbScore`, `float`) și afișează-l în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmp `float imdbScore`, getter, setter, al 11-lea parametru, linie în `toString()` | da |
| 2 | `activity_item.xml` | `TextInputEditText` cu `inputType="numberDecimal"` și ID nou | da, dacă îl introduci din formular |
| 3 | `ItemActivity.java` | câmp, `findViewById`, `fillForm`, `saveMovie` cu `Float.parseFloat` | da, împreună cu pasul 2 |
| 4 | `MainActivity.java` | al 11-lea argument, cu sufixul `f` | da, după ce schimbi constructorul |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, la câmpuri.** `float` este zecimala pe 32 de biți; `double` este tot o zecimală, pe 64 de biți. Aici cerința spune `float`.

```java
private String poster = null;
private float imdbScore;
```

**Pasul 2 — `Movie.java`, getter și setter.**

```java
public float getImdbScore() {
    return imdbScore;
}

public void setImdbScore(float imdbScore) {
    this.imdbScore = imdbScore;
}
```

**Pasul 3 — `Movie.java`, constructorul.** Al 11-lea parametru:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, float imdbScore) {
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
    this.imdbScore = imdbScore;
}
```

**Pasul 4 — `Movie.java`, `toString()`.**

```java
", imdbScore=" + imdbScore +
```

**Pasul 5 — `activity_item.xml`, în cardul „Your verdict", sub rating.**

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etImdbScore"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="IMDb score"
        android:inputType="numberDecimal" />
</com.google.android.material.textfield.TextInputLayout>
```

**Pasul 6 — `ItemActivity.java`, la câmpuri.**

```java
private EditText etImdbScore;
```

**Pasul 7 — `ItemActivity.java`, în `initControls()`.**

```java
etImdbScore = findViewById(R.id.etImdbScore);
```

**Pasul 8 — `ItemActivity.java`, în `fillForm()`.** `setText` nu are variantă pentru `float`; conversia este explicită:

```java
etImdbScore.setText(String.valueOf(existing.getImdbScore()));
```

**Pasul 9 — `ItemActivity.java`, în `saveMovie()`.** Tastatura poate produce virgulă zecimală în funcție de limbă; o normalizezi înainte de parse:

```java
String rawScore = etImdbScore.getText().toString().trim().replace(',', '.');
movie.setImdbScore(rawScore.isEmpty() ? 0f : Float.parseFloat(rawScore));
```

**Pasul 10 — `MainActivity.java`, în `addSampleMovies()`.** Un literal `float` are sufixul `f`; fără el, Java îl tratează ca `double` și nu îl acceptă acolo unde se cere `float`:

```java
"https://example.com/posters/inception.jpg",
8.8f));
```

### **De ce merge așa**

`float` și `double` sunt ambele zecimale, dar `float` are mai puțină precizie și este tipul cerut de widget-uri precum `RatingBar` (`getRating()` întoarce `float`). `Float.parseFloat` acceptă și notație științifică (`1.6E8`), dar nu acceptă virgula zecimală, indiferent de limba telefonului — de aceea `replace(',', '.')`. La `setText`, nu există supraîncărcare pentru `float`, deci fără `String.valueOf` codul nici măcar nu compilează.

### **Greșeala care costă puncte**

1. **`Float.parseFloat` pe câmp gol.** Simptom: `NumberFormatException: empty String` la Save. Cauza: ai sărit verificarea `isEmpty()`. La fel pentru `"8,5"` dacă nu normalizezi virgula. Aceeași capcană există deja în cod la `budget`: `Double.parseDouble(etBudget.getText().toString())` din `saveMovie()` crapă identic dacă lași bugetul gol.
2. **Literal fără `f` în constructor.** Simptom: `error: incompatible types: possible lossy conversion from double to float` la `8.8` în `addSampleMovies()`. Cauza: `8.8` este `double`; pentru `float` se scrie `8.8f`.
3. **`String.valueOf` pe un `double` mare.** Simptom: în formular apare `1.6E8` în loc de `160000000` (se întâmplă la `budget`). Cauza: `String.valueOf(double)` alege reprezentarea științifică pentru valori mari. Pentru bani se formatează cu `String.format("%.0f", value)` sau `DecimalFormat`.

### **Verificarea**

Adaugă un film cu `8.5` la IMDb: rândul conține `imdbScore=8.5`. Atinge rândul: câmpul arată `8.5`, nu `8.5f` și nu o excepție. Tastează `8,5` cu virgulă și salvează: valoarea ajunge `8.5`. Lasă câmpul gol: `imdbScore=0.0`, fără crash.

### **Exersează**

[17.4 — `imdbScore` (float): zecimala cu virgulă](cap-17.html#ex-17-4) · [19.7 — `1.6E8` în loc de `160000000`](cap-19.html#ex-19-7)

---

## Rețeta 33.5 — Adaugă un atribut boolean

### **Cerința, cum sună la test**

„Adaugă filmului un câmp `classic` (`boolean`), bifabil din formular, și afișează-l în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmp `boolean classic`, getter `isClassic()`, setter, al 11-lea parametru, linie în `toString()` | da |
| 2 | `activity_item.xml` | `MaterialCheckBox` cu ID nou | da, dacă îl introduci din formular |
| 3 | `ItemActivity.java` | câmp, `findViewById`, `fillForm` cu `setChecked`, `saveMovie` cu `isChecked` | da, împreună cu pasul 2 |
| 4 | `MainActivity.java` | al 11-lea argument: `true` sau `false` | da, după ce schimbi constructorul |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, la câmpuri.** Un `boolean` primitiv are valoarea implicită `false`:

```java
private String poster = null;
private boolean classic;
```

**Pasul 2 — `Movie.java`, getter și setter.** Pentru `boolean`, convenția JavaBeans cere `is`, nu `get`:

```java
public boolean isClassic() {
    return classic;
}

public void setClassic(boolean classic) {
    this.classic = classic;
}
```

**Pasul 3 — `Movie.java`, constructorul.** Al 11-lea parametru:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, boolean classic) {
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
    this.classic = classic;
}
```

**Pasul 4 — `Movie.java`, `toString()`.**

```java
", classic=" + classic +
```

**Pasul 5 — `activity_item.xml`, în cardul „Your verdict", sub rândul cu `swWatched` și `cbOnWatchList`.** Bifa:

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/cbClassic"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Classic" />
```

**Pasul 6 — `ItemActivity.java`, la câmpuri.** Tipul este `CheckBox`; `MaterialCheckBox` este o subclasă a lui, deci merge și `CheckBox`:

```java
private CheckBox cbClassic;
```

**Pasul 7 — `ItemActivity.java`, în `initControls()`.**

```java
cbClassic = findViewById(R.id.cbClassic);
```

**Pasul 8 — `ItemActivity.java`, în `fillForm()`.** Fără linia asta, la editare bifa pornește mereu debifată și Save rescrie `false`:

```java
cbClassic.setChecked(existing.isClassic());
```

**Pasul 9 — `ItemActivity.java`, în `saveMovie()`.** `isChecked()` întoarce exact `boolean`:

```java
movie.setClassic(cbClassic.isChecked());
```

**Pasul 10 — `MainActivity.java`, în `addSampleMovies()`.** Al 11-lea argument:

```java
"https://example.com/posters/inception.jpg",
true));
```

### **De ce merge așa**

`boolean` are doar două valori și o valoare implicită `false`, deci nu are nevoie de verificări de `null`. `CheckBox` și `Switch` sunt amândouă `CompoundButton`, iar metoda care spune starea este `isChecked()`; listener-ul `setOnCheckedChangeListener` primește `(CompoundButton, boolean)` și funcționează identic pentru amândouă. `fillForm` este obligatoriu: fără el, obiectul restaurat în formular nu reflectă valoarea din model, iar primul Save o pierde.

### **Greșeala care costă puncte**

1. **Uiți `cbClassic.setChecked(existing.isClassic())` în `fillForm`.** Simptom: editezi un film clasic, formularul arată bifa debifată, apeși Update și filmul devine neclasic. Cauza: widget-ul nu a fost sincronizat cu modelul la intrarea în ecran.
2. **Scrii `getClassic()` în loc de `isClassic()`.** Simptom: compilează, dar nu respectă convenția JavaBeans și se vede în cod ca o inconsistență. Cauza: ai copiat modelul de la un câmp ne-`boolean`. Pentru `boolean`, perechea este `isX()` / `setX()`.
3. **Pui `setChecked(true)` în `onCreate` ca „valoare implicită".** Simptom: la editare, bifa apare mereu pornită, indiferent de film. Cauza: ai confundat valoarea implicită a câmpului cu starea din model; `fillForm` trebuie să fie singurul loc care scrie în widget după `initControls()`.

### **Verificarea**

Adaugă un film cu bifa pornită: rândul arată `classic=true`. Atinge rândul: bifa este pornită. Debifeaz-o, apasă Update: rândul arată `classic=false`, iar filmul nu se dublează. Adaugă un film nou fără să atingi bifa: `classic=false`.

### **Exersează**

[17.3 — `popular` (boolean): steagul cu valoare implicită](cap-17.html#ex-17-3) · [17.8 — `awarded` (boolean) cu chip condiționat](cap-17.html#ex-17-8) · [19.1 — `tvWatchedValue` urmărește switch-ul](cap-19.html#ex-19-1)

---

## Rețeta 33.6 — Adaugă un atribut listă (ArrayList<String>)

### **Cerința, cum sună la test**

„Adaugă filmului lista actorilor (`actors`, `ArrayList<String>`), scrie-i despărțiți prin virgulă în formular și afișează-i în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmp `ArrayList<String> actors`, getter, setter, al 11-lea parametru, linie în `toString()` | da |
| 2 | `activity_item.xml` | un singur `TextInputEditText` cu ID nou, pentru textul cu virgule | da, dacă îi introduci din formular |
| 3 | `ItemActivity.java` | câmp, `findViewById`, `fillForm` cu `String.join`, `saveMovie` cu `split` | da, împreună cu pasul 2 |
| 4 | `MainActivity.java` | al 11-lea argument: un `ArrayList<String>` | da, după ce schimbi constructorul |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, la câmpuri.** Lista este o referință; o inițializezi ca să nu fie `null`:

```java
private String poster = null;
private ArrayList<String> actors = new ArrayList<>();
```

**Pasul 2 — `Movie.java`, getter și setter.** Getter-ul întoarce lista întreagă, nu un element:

```java
public ArrayList<String> getActors() {
    return actors;
}

public void setActors(ArrayList<String> actors) {
    this.actors = actors;
}
```

**Pasul 3 — `Movie.java`, constructorul.** Al 11-lea parametru:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, ArrayList<String> actors) {
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
    this.actors = actors;
}
```

**Pasul 4 — `Movie.java`, `toString()`.** O listă se afișează cu paranteze pătrate și virgule, prin `toString()`-ul ei:

```java
", actors=" + actors +
```

**Pasul 5 — `activity_item.xml`, în cardul „Basics", sub câmpul regizorului.** Un singur câmp text ține toată lista:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etActors"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Actors, separated by commas"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

**Pasul 6 — `ItemActivity.java`, la câmpuri.**

```java
private EditText etActors;
```

**Pasul 7 — `ItemActivity.java`, în `initControls()`.**

```java
etActors = findViewById(R.id.etActors);
```

**Pasul 8 — `ItemActivity.java`, în `fillForm()`.** Transformi lista înapoi în text, cu separatorul pe care îl așteaptă utilizatorul:

```java
etActors.setText(String.join(", ", existing.getActors()));
```

**Pasul 9 — `ItemActivity.java`, în `saveMovie()`.** Tai textul după virgulă, elimini spațiile și sari peste bucățile goale:

```java
ArrayList<String> actors = new ArrayList<>();
for (String name : etActors.getText().toString().split(",")) {
    String trimmed = name.trim();
    if (!trimmed.isEmpty()) {
        actors.add(trimmed);
    }
}
movie.setActors(actors);
```

**Pasul 10 — `MainActivity.java`, în `addSampleMovies()`.** Construiești lista înainte de apel sau direct în argument:

```java
"https://example.com/posters/inception.jpg",
new ArrayList<>(Arrays.asList("Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"))));
```

Adaugă importul `java.util.Arrays` în `MainActivity`.

### **De ce merge așa**

Un `EditText` ține un singur șir, așa că lista este codificată într-un text cu separator. `String.split(",")` întoarce un tablou de șiruri, iar `new ArrayList<>(...)` îl face modificabil. `String.join(", ", list)` face drumul invers și este disponibil pe API 26+, iar `minSdk`-ul proiectului este 33. `ArrayList` și `String` sunt amândouă `Serializable`, deci lista călătorește prin `Intent` fără nicio configurare suplimentară.

### **Greșeala care costă puncte**

1. **`Arrays.asList(text.split(","))` și apoi `add(...)`.** Simptom: `UnsupportedOperationException` când încerci să mai adaugi un actor. Cauza: `Arrays.asList` întoarce o listă de dimensiune fixă, nu un `ArrayList`. Înfășoară-o: `new ArrayList<>(Arrays.asList(...))`.
2. **Câmp gol tratat ca listă cu un element.** Simptom: după Save fără actori, rândul arată `actors=[""]` sau `actors=[]` în funcție de implementare. Cauza: `"".split(",")` întoarce un tablou cu un singur șir gol. Verifică `trimmed.isEmpty()` înainte de `add`.
3. **Uiți `trim()`.** Simptom: lista arată `["Leonardo DiCaprio", " Joseph Gordon-Levitt"]`, cu spațiu în față, iar căutarea după nume nu mai găsește actorul. Cauza: separatorul este `", "`, nu `","`; spațiul rămâne în șir.

### **Verificarea**

Adaugă un film cu `A, B, C` la actori: rândul arată `actors=[A, B, C]`. Atinge rândul: câmpul arată `A, B, C`, cu spații după virgule. Șterge un nume și salvează: lista are două elemente. Lasă câmpul gol: `actors=[]`, fără excepție.

### **Exersează**

[17.5 — `actors` (ArrayList\<String\>): listă într-un singur câmp](cap-17.html#ex-17-5) · [17.9 — `cast` (ArrayList\<Actor\>): atributul compus](cap-17.html#ex-17-9)

## Rețeta 33.7 — Adaugă un atribut compus (o clasă nouă)

### **Cerința, cum sună la test**

„Adaugă filmului un regizor (`director`) cu nume și naționalitate, ca obiect separat, și afișează-l în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Director.java` | clasă nouă în `ro.ase.ie.g1097.model`, cu `implements Serializable` | da |
| 2 | `Movie.java` | câmp `Director director`, getter, setter, al 11-lea parametru, linie în `toString()` | da |
| 3 | `activity_item.xml` | două `TextInputEditText` cu ID-uri noi (nume, naționalitate) | da, dacă îl introduci din formular |
| 4 | `ItemActivity.java` | două câmpuri, `findViewById`, `fillForm` cu verificare de `null`, `saveMovie` cu `new Director(...)` | da, împreună cu pasul 3 |
| 5 | `MainActivity.java` | al 11-lea argument: `new Director(...)` | da, după ce schimbi constructorul |

### **Pașii, în ordine**

**Pasul 1 — fișier nou `Director.java`, în pachetul `ro.ase.ie.g1097.model`.** Clasa este un POJO ca `Movie`, cu un detaliu care nu este opțional: `implements Serializable`.

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;

public class Director implements Serializable {

    private String name;
    private String nationality;

    public Director(String name, String nationality) {
        this.name = name;
        this.nationality = nationality;
    }

    public Director() {
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getNationality() {
        return nationality;
    }

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }

    @Override
    public String toString() {
        return "Director{name='" + name + "', nationality='" + nationality + "'}";
    }
}
```

**Pasul 2 — `Movie.java`, la câmpuri.** Câmpul este o referință la un obiect, nu un text:

```java
private String poster = null;
private Director director;
```

**Pasul 3 — `Movie.java`, getter și setter.**

```java
public Director getDirector() {
    return director;
}

public void setDirector(Director director) {
    this.director = director;
}
```

**Pasul 4 — `Movie.java`, constructorul.** Al 11-lea parametru este `Director`:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, Director director) {
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
    this.director = director;
}
```

**Pasul 5 — `Movie.java`, `toString()`.** Nu concatenzi câmpurile regizorului: apelezi `toString()`-ul lui `Director`, care trebuie să existe:

```java
", director=" + director +
```

**Pasul 6 — `activity_item.xml`, în cardul „Basics", sub câmpul regizorului text.** Două câmpuri, unul sub altul:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etDirectorName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Director name"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    app:hintEnabled="false">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etDirectorNationality"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Director nationality"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

**Pasul 7 — `ItemActivity.java`, la câmpuri.**

```java
private EditText etDirectorName;
private EditText etDirectorNationality;
```

**Pasul 8 — `ItemActivity.java`, în `initControls()`.**

```java
etDirectorName = findViewById(R.id.etDirectorName);
etDirectorNationality = findViewById(R.id.etDirectorNationality);
```

**Pasul 9 — `ItemActivity.java`, în `fillForm()`.** `director` poate fi `null` la filmele demo sau la un film salvat înainte de modificare; verifici înainte să ceri `getName()`:

```java
if (existing.getDirector() != null) {
    etDirectorName.setText(existing.getDirector().getName());
    etDirectorNationality.setText(existing.getDirector().getNationality());
} else {
    etDirectorName.setText("");
    etDirectorNationality.setText("");
}
```

**Pasul 10 — `ItemActivity.java`, în `saveMovie()`.** Construiești obiectul compus din cele două câmpuri:

```java
movie.setDirector(new Director(
        etDirectorName.getText().toString(),
        etDirectorNationality.getText().toString()));
```

**Pasul 11 — `MainActivity.java`, în `addSampleMovies()`.** Al 11-lea argument este un obiect:

```java
"https://example.com/posters/inception.jpg",
new Director("Christopher Nolan", "British")));
```

Adaugă importul `ro.ase.ie.g1097.model.Director`.

### **De ce merge așa**

`Movie implements Serializable`, iar serializarea este **recursivă**: la `putExtra`, Java scrie în bytes obiectul și tot ce atinge prin câmpurile lui. Dacă `Director` nu este și el `Serializable`, lanțul se rupe exact la câmpul `director`, chiar dacă `Movie` este serializabil. La citire, `IntentCompat.getSerializableExtra` reconstruiește întregul graf — de aceea obiectul primit în `ItemActivity` este o copie completă, cu regizor cu tot.

### **Greșeala care costă puncte**

1. **`Director` fără `implements Serializable`.** Simptom: aplicația se închide când atingi un rând din listă, cu `Parcelable encountered IOException writing serializable object` și `Caused by: NotSerializableException: ro.ase.ie.g1097.model.Director`. Cauza: serializarea lui `Movie` ajunge la câmpul `director` și nu știe să-l scrie. Compilatorul nu te avertizează — eroarea este doar la runtime.
2. **`fillForm` fără verificarea de `null`.** Simptom: `NullPointerException` în `fillForm` pe filmele demo, care au `director = null`. Cauza: ai apelat `existing.getDirector().getName()` fără să verifici.
3. **Uiți `toString()` în `Director`.** Simptom: rândul arată `director=ro.ase.ie.g1097.model.Director@1a2b3c` în loc de nume. Cauza: `Movie.toString()` concatenă obiectul, iar fără `toString()` se folosește varianta implicită din `Object`, care afișează numele clasei și hash-ul.

### **Verificarea**

Adaugă un film cu regizorul „Christopher Nolan", naționalitate „British": rândul conține `director=Director{name='Christopher Nolan', nationality='British'}`. Atinge rândul: ambele câmpuri sunt completate. Modifică naționalitatea și apasă Update: rândul se schimbă, fără crash. Atinge un film demo: câmpurile sunt goale, nu apare excepție.

### **Exersează**

[17.9 — `cast` (ArrayList\<Actor\>): atributul compus](cap-17.html#ex-17-9) · [18.10 — combo: atributul `writer`, în XML și în `bind()`](cap-18.html#ex-18-10)

---

## Rețeta 33.8 — Adaugă un atribut derivat (calculat)

### **Cerința, cum sună la test**

„Adaugă filmului deceniul în care a apărut (`decade`), calculat din data lansării, și afișează-l în listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | getter `getDecade()` care calculează din `release`; linie în `toString()` | da |
| 2 | `activity_item.xml` | nimic | nu |
| 3 | `ItemActivity.java` | nimic | nu |
| 4 | `MainActivity.java` | nimic | nu |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, după `getRelease()`.** Nu adaugi câmp, nu adaugi setter, nu adaugi parametru în constructor. Adaugi doar metoda care calculează:

```java
public int getDecade() {
    if (release == null) {
        return 0;
    }
    Calendar calendar = Calendar.getInstance();
    calendar.setTime(release);
    int year = calendar.get(Calendar.YEAR);
    return (year / 10) * 10;
}
```

**Pasul 2 — `Movie.java`, importul.** `Calendar` trebuie importat dacă nu este deja:

```java
import java.util.Calendar;
```

**Pasul 3 — `Movie.java`, `toString()`.** Apelezi metoda, nu un câmp:

```java
", decade=" + getDecade() +
```

Atât. Nu atingi XML-ul, nu atingi `ItemActivity`, nu atingi `MainActivity`.

### **De ce merge așa**

Un atribut derivat nu are stocare: valoarea lui este o funcție de alte câmpuri, calculată la fiecare citire. Dacă l-ai stoca într-un câmp, ar trebui să îl actualizezi manual la fiecare schimbare a datei — iar `fillForm` și `saveMovie` ar putea produce valori contradictorii. `Calendar` este necesar pentru că `Date` este doar un moment în timp; `Date.getYear()` este depreciat și întoarce anul **scăzut cu 1900**, deci nu îl folosi.

### **Greșeala care costă puncte**

1. **Adaugi câmp și setter pentru un atribut derivat.** Simptom: codul compilează, dar după ce editezi data, `decade` rămâne vechi. Cauza: ai stocat o valoare care trebuia calculată; două surse de adevăr se contrazic.
2. **Nu verifici `release == null`.** Simptom: `NullPointerException` în `toString()` la un film fără dată, adică exact când lista se redesenează. Cauza: `calendar.setTime(null)` aruncă excepție.
3. **Folosești `release.getYear()`.** Simptom: pentru 2010 obții `110`. Cauza: metoda este depreciată și numără anii de la 1900. `Calendar.get(Calendar.YEAR)` întoarce anul calendaristic corect.

### **Verificarea**

Lista arată `decade=2010` pentru Inception, `decade=1990` pentru Toy Story și The Matrix. Editează data unui film la 1985 și salvează: rândul arată `decade=1980`, fără să fi atins vreun câmp nou. Un film cu data lipsă arată `decade=0`, fără crash.

### **Exersează**

[17.8 — `awarded` (boolean) cu chip condiționat](cap-17.html#ex-17-8) · [19.4 — `tvDurationValue` arată „1 h 22 min"](cap-19.html#ex-19-4)

---

## Rețeta 33.9 — Schimbă tipul unui atribut existent

### **Cerința, cum sună la test**

„Schimbă tipul ratingului din `float` în `double`, fără să strici formularul și lista."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmpul, getter-ul, setter-ul și parametrul din constructor devin `double` | da |
| 2 | `ItemActivity.java` | `fillForm` are nevoie de un cast la `setRating(float)` | da |
| 3 | `activity_item.xml` | nimic | nu |
| 4 | `MainActivity.java` | literalii `4.5f`, `4f`, `5f` rămân valizi | nu |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, câmpul.**

```java
private double rating;
```

**Pasul 2 — `Movie.java`, getter și setter.** Ambele se schimbă împreună cu câmpul:

```java
public double getRating() {
    return rating;
}

public void setRating(double rating) {
    this.rating = rating;
}
```

**Pasul 3 — `Movie.java`, constructorul.** Parametrul devine `double`:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             double rating, boolean watched, String approval, boolean onWatchlist,
             String poster) {
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
}
```

**Pasul 4 — `Movie.java`, `toString()`.** Nu se schimbă nimic: concatenarea cu `+` acceptă orice tip primitiv.

**Pasul 5 — `ItemActivity.java`, în `fillForm()`.** `RatingBar.setRating` cere `float`, iar `getRating()` întoarce acum `double`. Conversia de la `double` la `float` este **îngustă** și are nevoie de cast explicit:

```java
rbRating.setRating((float) existing.getRating());
```

**Pasul 6 — `ItemActivity.java`, în `saveMovie()`.** Aici nu este nevoie de cast: `rbRating.getRating()` întoarce `float`, iar `float` se lărgește automat la `double`:

```java
movie.setRating(rbRating.getRating());
```

**Pasul 7 — `MainActivity.java`, în `addSampleMovies()`.** Literalii `4.5f`, `4f`, `5f` rămân valizi: un `float` se lărgește automat la `double`. Poți să îi lași așa sau să îi scrii `4.5`, `4.0`, `5.0`.

### **De ce merge așa**

Java face conversii automate doar când **nu se pierde informație**: `float` → `double` este o lărgire, deci merge fără cast; `double` → `float` este o îngustare, deci cere cast explicit și poate pierde precizie. `RatingBar` a fost proiectat cu `float`, deci la granița dintre model (`double`) și widget (`float`) trebuie să convertești tu. Restul lanțului — `toString()`, `Intent`, `ArrayAdapter` — nu depinde de tipul exact al zecimalei.

### **Greșeala care costă puncte**

1. **Uiți castul din `fillForm`.** Simptom: `error: incompatible types: possible lossy conversion from double to float` la `rbRating.setRating(existing.getRating())`. Cauza: ai schimbat modelul, dar widget-ul are în continuare `setRating(float)`.
2. **Schimbi câmpul, dar nu getter-ul și setter-ul.** Simptom: erori în lanț la `setRating(double)` și `getRating()` — semnătura nu mai corespunde cu câmpul. Cauza: tipul atributului este contractul format din câmp + getter + setter + parametru; toate patru se schimbă împreună.
3. **Faci schimbarea inversă, la `budget` (`double` → `float`), și uiți `String.valueOf`.** Simptom: în formular apare `1.6E8` în loc de `160000000`. Cauza: reprezentarea științifică a lui `double`; pentru bani formatezi cu `String.format("%.0f", value)`.

### **Verificarea**

Lista arată `rating=4.5`, `rating=4.0`, `rating=5.0`. Atinge un rând: stelele arată exact valoarea din model, iar câmpul nu crapă. Modifică ratingul la 3.5 și salvează: rândul arată `rating=3.5`. Compilarea trece fără avertismente de conversie.

### **Exersează**

[18.2 — `etBudget` devine `SeekBar` (0–500 milioane, pas 1 milion)](cap-18.html#ex-18-2) · [18.3 — `rbRating` (`RatingBar`) devine `Spinner` cu 1–5 stele](cap-18.html#ex-18-3) · [19.7 — `1.6E8` în loc de `160000000`](cap-19.html#ex-19-7)

---

## Rețeta 33.10 — Redenumește un atribut și propagă în tot codul

### **Cerința, cum sună la test**

„Redenumește câmpul `poster` în `posterUrl` și actualizează tot codul care îl folosește."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `Movie.java` | câmpul, getter-ul, setter-ul, parametrul din constructor, linia din `toString()` | da |
| 2 | `ItemActivity.java` | `getPoster()` → `getPosterUrl()`, `setPoster()` → `setPosterUrl()` | da |
| 3 | `MainActivity.java` | nimic: constructorul este pozițional, numele parametrului nu se vede la apel | nu |
| 4 | `activity_item.xml` | nimic: ID-ul `etPoster` este independent de numele câmpului | nu |

### **Pașii, în ordine**

**Pasul 1 — `Movie.java`, câmpul.** Schimbi numele, nu tipul:

```java
private String posterUrl = null;
```

**Pasul 2 — `Movie.java`, getter-ul și setter-ul.** Numele lor este contractul public al clasei; se schimbă obligatoriu împreună cu câmpul:

```java
public String getPosterUrl() {
    return posterUrl;
}

public void setPosterUrl(String posterUrl) {
    this.posterUrl = posterUrl;
}
```

**Pasul 3 — `Movie.java`, constructorul.** Parametrul se redenumește și atribuirea folosește noul nume:

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String posterUrl) {
    this.title = title;
    this.release = release;
    this.genre = genre;
    this.budget = budget;
    this.duration = duration;
    this.rating = rating;
    this.watched = watched;
    this.approval = approval;
    this.onWatchlist = onWatchlist;
    this.posterUrl = posterUrl;
}
```

**Pasul 4 — `Movie.java`, `toString()`.** Linia folosește câmpul, deci se schimbă:

```java
", posterUrl='" + posterUrl + '\'' +
```

Eticheta din text (`posterUrl=`) este cosmetică, dar o schimbi ca să nu inducă în eroare.

**Pasul 5 — `ItemActivity.java`, în `fillForm()`.** Apelul vechi nu mai compilează:

```java
etPoster.setText(existing.getPosterUrl());
```

**Pasul 6 — `ItemActivity.java`, în `saveMovie()`.** La fel:

```java
movie.setPosterUrl(etPoster.getText().toString());
```

**Pasul 7 — verifici dacă mai există apeluri.** Caută în tot proiectul `getPoster` și `setPoster`. În G1097 nu mai există altul; dacă ai adăugat tu unul într-o rețetă anterioară, îl actualizezi și pe acela.

### **De ce merge așa**

Câmpul este `private`, deci numele lui nu se vede din afara clasei; getter-ul și setter-ul sunt singurul contract. Când redenumești getter-ul, toate apelurile care îl folosesc devin erori de compilare — și aceasta este varianta bună: compilatorul îți dă lista completă a locurilor de schimbat. `MainActivity` nu este atins pentru că acolo constructorul este apelat pozițional: `new Movie(..., "https://...")` nu conține numele parametrului.

### **Greșeala care costă puncte**

1. **Redenumești câmpul, dar lași getter-ul `getPoster()`.** Simptom: codul compilează, dar clasa are un câmp `posterUrl` și un getter `getPoster()` care întoarce `posterUrl`. Cauza: ai schimbat doar jumătate din contract; este legal, dar inconsistent și greu de citit.
2. **Redenumești getter-ul și uiți un apel.** Simptom: `error: cannot find symbol method getPoster()` în `ItemActivity`. Cauza: ai schimbat contractul, dar nu toți apelanții. Nu este o greșeală de logică — o rezolvi citind eroarea.
3. **Redenumești și ID-ul `etPoster` „ca să fie la fel".** Simptom: eroare de compilare la `findViewById(R.id.etPoster)` după ce ai schimbat XML-ul. Cauza: ai confundat numele câmpului Java cu ID-ul din XML. Sunt independente: poți avea câmpul `etPoster` și ID-ul `etPosterUrl`, atâta timp cât `findViewById` folosește ID-ul corect.

### **Verificarea**

Proiectul compilează fără nicio referință la `getPoster` sau `setPoster`. Lista arată `posterUrl='https://...'`. Atinge un rând: câmpul „Poster URL" este completat. Modifică URL-ul și salvează: rândul se actualizează.

### **Exersează**

[17.10 — `writer` + `popular`: cele două cerințe, în 30 de minute](cap-17.html#ex-17-10) · [24.7 — checklist-ul de după fiecare „adaugă un atribut"](cap-24.html#ex-24-7)

---

## Rețeta 33.11 — Adaugă un widget în formular

### **Cerința, cum sună la test**

„Adaugă sub data lansării o etichetă care arată anul ales, actualizată când schimbi data."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activity_item.xml` | `TextView` cu ID nou, sub blocul `etRelease` | da |
| 2 | `ItemActivity.java` | câmp, `findViewById`, actualizare în `onDateSet` și în `fillForm` | da |
| 3 | `Movie.java` | nimic | nu |

### **Pașii, în ordine**

**Pasul 1 — `activity_item.xml`, în cardul „Basics", imediat după `TextInputLayout`-ul lui `etRelease`.** Eticheta:

```xml
<TextView
    android:id="@+id/tvReleaseYear"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:text="Year: —"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorPrimary" />
```

**Pasul 2 — `ItemActivity.java`, la câmpuri.**

```java
private TextView tvReleaseYear;
```

**Pasul 3 — `ItemActivity.java`, în `initControls()`.**

```java
tvReleaseYear = findViewById(R.id.tvReleaseYear);
```

**Pasul 4 — `ItemActivity.java`, în `onDateSet` din `showReleaseDatePicker()`.** Aici ai deja anul ca parametru, deci nu mai parsezi textul:

```java
public void onDateSet(DatePicker view, int year, int month, int day) {
    releaseCal.set(year, month, day);
    etRelease.setError(null);
    etRelease.setText(dateFormat.format(releaseCal.getTime()));
    tvReleaseYear.setText("Year: " + year);
}
```

**Pasul 5 — `ItemActivity.java`, în `fillForm()`.** Aici este capcana reală a aplicației: `fillForm` scrie în `etRelease`, dar **nu sincronizează `releaseCal`**. Dacă adaugi eticheta fără să repari asta, la editare eticheta arată anul de azi, iar Save scrie data de azi. Sincronizezi ambele:

```java
etRelease.setText(dateFormat.format(existing.getRelease()));
releaseCal.setTime(existing.getRelease());
tvReleaseYear.setText("Year: " + releaseCal.get(Calendar.YEAR));
```

**Pasul 6 — `ItemActivity.java`, în `clearForm()` dacă ai adăugat butonul de la rețeta 33.13.** Resetezi și eticheta:

```java
tvReleaseYear.setText("Year: —");
```

### **De ce merge așa**

Eticheta este o **oglindă** a stării, nu o a doua sursă de adevăr: o actualizezi din `releaseCal`, exact în locurile în care `releaseCal` se schimbă. `onDateSet` este singurul loc în care utilizatorul alege o dată, iar `fillForm` este singurul loc în care formularul primește o dată existentă. Dacă actualizezi eticheta din `etRelease.getText()`, parsezi un text pe care tocmai l-ai formatat — o operație inutilă și fragilă.

### **Greșeala care costă puncte**

1. **Uiți `fillForm`.** Simptom: editezi un film, eticheta arată „Year: —" sau anul de azi, deși câmpul de dată arată data filmului. Cauza: ai actualizat eticheta doar în `onDateSet`, care nu este apelat la intrarea în ecran.
2. **Nu sincronizezi `releaseCal` în `fillForm`.** Simptom: editezi un film din 2010, nu atingi data, apeși Update și filmul devine „lansat azi". Cauza: `releaseCal` a rămas `Calendar.getInstance()` din inițializarea câmpului; `saveMovie` scrie `releaseCal.getTime()`, nu textul din `etRelease`. Este un bug real al aplicației, nu doar al rețetei.
3. **Actualizezi eticheta din `etRelease.getText()` în `onDateSet`.** Simptom: funcționează, dar după ce utilizatorul tastează manual o dată și apoi deschide picker-ul, eticheta poate rămâne în urmă. Cauza: ai două surse de adevăr; folosește `releaseCal`.

### **Verificarea**

Deschide formularul: eticheta arată „Year: —". Apasă pe dată, alege 16 iulie 2010: câmpul arată `16/07/2010`, eticheta arată „Year: 2010". Salvează: rândul conține `release=...2010`. Atinge rândul: eticheta arată „Year: 2010" din prima, fără să deschizi picker-ul. Apasă Update fără să atingi data: anul rămâne 2010.

### **Exersează**

[18.1 — `tvDurationValue` legat de `SeekBar`](cap-18.html#ex-18-1) · [19.2 — contor de caractere sub `etTitle`](cap-19.html#ex-19-2) · [19.4 — `tvDurationValue` arată „1 h 22 min"](cap-19.html#ex-19-4) · [19.8 — `fillForm` crapă când `release` e `null`](cap-19.html#ex-19-8)

## Rețeta 33.12 — Adaugă un widget în rândul listei

### **Cerința, cum sună la test**

„Adaugă în rândul listei un `TextView` care arată regizorul filmului."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `movie_item.xml` | `TextView` cu ID nou, în coloana de informații | da, dar **fără efect** în aplicația actuală |
| 2 | `Movie.java` | atributul `writer` (rețeta 33.1) și linia lui din `toString()` | da, pentru `ListView` |
| 3 | `MovieAdapter.java` | câmp în `ViewHolder`, `findViewById`, `setText` în `bind()` | doar dacă ai făcut migrarea la `RecyclerView` |
| 4 | `MainActivity.java` | nimic, cât timp rămâi pe `ArrayAdapter` | nu |

### **Pașii, în ordine**

**Pasul 0 — ce trebuie să știi înainte de primul pas.** `movie_item.xml` **există în G1097, dar nu este folosit de niciun cod**. `MainActivity` creează `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, iar `simple_list_item_1` este un layout de sistem cu **un singur `TextView`**. Niciun `inflate` nu atinge `movie_item.xml`. Fișierul este pregătit pentru `RecyclerView` și devine activ abia la migrarea din capitolul 23. Rețeta presupune că `writer` există deja în `Movie` (rețeta 33.1); dacă nu, adaugi întâi câmpul, getter-ul, setter-ul și linia din `toString()`.

**Pasul 1 — `movie_item.xml`, în coloana de informații, după `movieSubtitle`.** Adaugi `TextView`-ul:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:text="Writer"
    android:textSize="13sp"
    android:textColor="#616161"
    android:maxLines="1"
    android:ellipsize="end" />
```

**Pasul 2 — dacă rămâi pe `ListView`.** Nu se vede nimic nou: rândul este desenat de `simple_list_item_1`, care nu știe de `movieWriter`. Singura cale ca atributul să apară este `toString()` din `Movie`. Extinzi metoda existentă cu `writer` (sau o rescrii compact, dacă vrei un rând mai scurt):

```java
@Override
public String toString() {
    return title + " — " + writer + " (" + rating + ")";
}
```

Aceasta este varianta corectă pentru `ListView` și este cea care se punctează la test dacă nu ți se cere explicit `RecyclerView`.

**Pasul 3 — dacă ai migrat la `RecyclerView`.** În `MovieAdapter`, în `ViewHolder`, adaugi câmpul și îl legi:

```java
private final TextView movieWriter;

public MovieViewHolder(@NonNull View itemView) {
    super(itemView);
    movieTitle = itemView.findViewById(R.id.movieTitle);
    movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
    movieWriter = itemView.findViewById(R.id.movieWriter);
}
```

**Pasul 4 — `MovieAdapter`, în `bind()`.** Umpli câmpul din model:

```java
movieWriter.setText(movie.getWriter());
```

**Pasul 5 — `MainActivity`, după orice modificare a listei.** Adapterul nu observă singur schimbarea:

```java
movieAdapter.notifyDataSetChanged();
```

### **De ce merge așa**

`ArrayAdapter` are un singur contract cu rândul: ia obiectul din listă și îl transformă în text prin `toString()`. Nu citește `movie_item.xml` și nu caută view-uri după ID. `RecyclerView` este cel care are nevoie de un layout de rând și de un adapter propriu, cu `ViewHolder`; abia atunci `findViewById` are ce găsi. De aceea, în G1097, adăugarea în `movie_item.xml` este o modificare **pregătitoare**, nu una vizibilă.

### **Greșeala care costă puncte**

1. **Adaugi widget-ul în `movie_item.xml` și aștepți să apară.** Simptom: rulezi aplicația, adaugi un film, rândul arată exact ca înainte. Cauza: fișierul nu este inflate nicăieri; `ArrayAdapter` folosește `simple_list_item_1`.
2. **Adaugi atributul în model, dar nu în `toString()`.** Simptom: la fel, rândul nu se schimbă, deși valoarea este salvată. Cauza: pentru `ListView`, `toString()` este singura fereastră spre ecran.
3. **Modifici lista, dar uiți `notifyDataSetChanged()`.** Simptom: după Save, datele sunt în `movies`, dar lista arată vechiul conținut până derulezi sau rotesti ecranul. Cauza: adapterul ține o referință la listă, dar nu este notificat să redeseneze.

### **Verificarea**

Cu `ListView`: adaugă un film cu regizor și verifică faptul că rândul conține numele regizorului prin `toString()`. Cu `RecyclerView`: după migrare, rândul are un `TextView` suplimentar, iar la scroll textul rămâne corect (nu se amestecă între rânduri). În ambele cazuri, după editare rândul se actualizează fără duplicat.

### **Exersează**

[18.4 — a doua linie în rândul de `ListView` (`BaseAdapter` propriu)](cap-18.html#ex-18-4) · [18.6 — URL-ul posterului într-un `TextView`](cap-18.html#ex-18-6) · [18.8 — rândul arată `Inception (2010)`: `toString()` sau adapter propriu?](cap-18.html#ex-18-8) · [23.4 — `MovieViewHolder` cu câmpurile din `movie_item.xml`](cap-23.html#ex-23-4) · [23.6 — `onBindViewHolder`: titlu și subtitlu](cap-23.html#ex-23-6)

---

## Rețeta 33.13 — Adaugă un buton

### **Cerința, cum sună la test**

„Adaugă în formular un buton «Clear form» care golește toate câmpurile, fără să închidă ecranul."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activity_item.xml` | `MaterialButton` cu ID nou, sub butonul de Save | da |
| 2 | `ItemActivity.java` | câmp, `findViewById`, listener, metoda `clearForm()` | da |
| 3 | `Movie.java` | nimic | nu |

### **Pașii, în ordine**

**Pasul 1 — `activity_item.xml`, după `btnMovieAction`.** Butonul, cu aceeași lățime și cu un stil secundar:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnClear"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:layout_marginTop="12dp"
    android:text="Clear form" />
```

**Pasul 2 — `ItemActivity.java`, la câmpuri.**

```java
private Button btnClear;
```

**Pasul 3 — `ItemActivity.java`, în `initControls()`.**

```java
btnClear = findViewById(R.id.btnClear);
```

**Pasul 4 — `ItemActivity.java`, în `initListeners()`.** Listener-ul apelează metoda, nu conține logica:

```java
btnClear.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        clearForm();
    }
});
```

**Pasul 5 — `ItemActivity.java`, metoda nouă `clearForm()`.** Golește fiecare widget și, obligatoriu, resetează `releaseCal`:

```java
private void clearForm() {
    etTitle.setText("");
    etRelease.setText("");
    releaseCal = Calendar.getInstance();
    spGenre.setSelection(0);
    etBudget.setText("");
    sbDuration.setProgress(0);
    rbRating.setRating(0);
    swWatched.setChecked(false);
    cbonWatchList.setChecked(false);
    rgApproval.check(R.id.rbGeneral);
    etPoster.setText("");
    tvDurationValue.setText("0 min.");
    tvWatchedValue.setText("No");
}
```

**Pasul 6 — `ItemActivity.java`, verifică importurile.** `Calendar` este deja importat; `Button` este deja importat. Nu adaugi nimic.

### **De ce merge așa**

Butonul este doar un declanșator: `setOnClickListener` rulează metoda ta. `clearForm()` trebuie să atingă **toate** sursele de date ale formularului, nu doar cele vizibile. `releaseCal` este o sursă invizibilă: `saveMovie()` scrie `releaseCal.getTime()`, deci dacă îl lași neatins, butonul golește câmpul de dată, dar Save scrie în continuare data veche. `rgApproval.check(R.id.rbGeneral)` este necesar pentru că un `RadioGroup` nu are „stare goală": are mereu un buton selectat.

### **Greșeala care costă puncte**

1. **Golești `etRelease`, dar nu `releaseCal`.** Simptom: apeși Clear, câmpul de dată este gol, apeși Save și filmul are data veche. Cauza: ai curățat textul, nu starea. `releaseCal = Calendar.getInstance()` este linia care contează.
2. **Uiți `rgApproval.check(R.id.rbGeneral)`.** Simptom: după Clear, rămâne selectat `PG-13` sau `R`. Cauza: `RadioGroup` nu se golește prin `setChecked(false)` pe copii; se selectează explicit un buton.
3. **Pui logica de golire direct în listener.** Simptom: funcționează, dar codul devine greu de citit și nu poți reutiliza golirea după Save. Cauza: ai amestecat declanșatorul cu acțiunea; metoda separată `clearForm()` este răspunsul curat.

### **Verificarea**

Completează formularul, apasă „Clear form": toate câmpurile sunt goale, slider-ul este la 0, stelele la 0, aprobarea este pe `G`, iar etichetele arată „0 min." și „No". Apasă Save: filmul se salvează cu valorile goale, fără crash și fără data veche. Butonul „Save Movie" rămâne funcțional.

### **Exersează**

[20.1 — butonul „Clear form" sub „Save Movie"](cap-20.html#ex-20-1) · [20.3 — butonul „Delete" din `ItemActivity`, cu cod de rezultat propriu](cap-20.html#ex-20-3) · [20.10 — combinația de examen: butonul „Duplicate movie"](cap-20.html#ex-20-10)

---

## Rețeta 33.14 — Adaugă un control deasupra listei

### **Cerința, cum sună la test**

„Adaugă deasupra listei un buton care sortează filmele după titlu."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activity_main.xml` | schimbi rădăcina din `FrameLayout` în `LinearLayout` vertical și înfășori lista + FAB-ul într-un `FrameLayout` | da |
| 2 | `MainActivity.java` | câmp, `findViewById`, listener care sortează lista și notifică adapterul | da |
| 3 | `Movie.java` | nimic | nu |

### **Pașii, în ordine**

**Pasul 1 — `activity_main.xml`, rădăcina.** `FrameLayout` suprapune copiii: un control pus primul este acoperit de `ListView`, care are `match_parent`. Ca să ai un rând deasupra listei, rădăcina devine `LinearLayout` vertical, iar lista și FAB-ul rămân împreună într-un `FrameLayout` cu `layout_weight="1"`:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".activities.MainActivity">

    <com.google.android.material.button.MaterialButton
        android:id="@+id/btnSort"
        style="@style/Widget.Material3.Button.TonalButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginHorizontal="16dp"
        android:layout_marginTop="8dp"
        android:text="Sort by title" />

    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <ListView
            android:id="@+id/listView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:entries="@array/items" />

        <com.google.android.material.floatingactionbutton.FloatingActionButton
            android:id="@+id/floatingActionButton"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="bottom|end"
            android:layout_margin="16dp"
            android:contentDescription="Add"
            app:srcCompat="@drawable/outline_add_24" />
    </FrameLayout>
</LinearLayout>
```

> Păstrează `android:id="@+id/main"` pe rădăcină: listener-ul de insets din `onCreate` îl caută. `android:entries="@array/items"` de pe `ListView` este ignorat la runtime, pentru că `initControls()` apelează `listView.setAdapter(movieAdapter)`.

**Pasul 2 — `MainActivity.java`, la câmpuri.**

```java
private Button btnSort;
```

**Pasul 3 — `MainActivity.java`, în `initControls()`.**

```java
btnSort = findViewById(R.id.btnSort);
```

**Pasul 4 — `MainActivity.java`, în `initListeners()`.** Sortezi lista **pe loc** și notifici adapterul:

```java
btnSort.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Collections.sort(movies, new Comparator<Movie>() {
            @Override
            public int compare(Movie m1, Movie m2) {
                return m1.getTitle().compareToIgnoreCase(m2.getTitle());
            }
        });
        movieAdapter.notifyDataSetChanged();
    }
});
```

**Pasul 5 — `MainActivity.java`, importurile.** Adaugi:

```java
import java.util.Collections;
import java.util.Comparator;
```

### **De ce merge așa**

`movieAdapter` a fost construit cu `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)` și ține **referința** la lista `movies`. Dacă sortezi aceeași listă, adapterul vede noua ordine; dacă ai înlocui referința cu o listă nouă, adapterul ar rămâne pe cea veche. `Collections.sort` sortează in-place, iar `notifyDataSetChanged()` este semnalul către `ListView` să redeseneze rândurile. `compareToIgnoreCase` face sortarea insensibilă la majuscule, ca „toy story" să nu ajungă după „The Matrix" din cauza codului ASCII.

### **Greșeala care costă puncte**

1. **Pui butonul direct în `FrameLayout`, deasupra `ListView`.** Simptom: butonul nu se vede deloc, deși există în XML. Cauza: `FrameLayout` suprapune copiii, iar `ListView` cu `match_parent` îl acoperă. Soluția este părintele vertical + `layout_weight`.
2. **Înlocuiești lista în loc să o sortezi.** Simptom: `error: cannot assign a value to final variable movies` sau, dacă ai scos `final`, lista se sortează, dar ecranul nu se schimbă. Cauza: `movies` este `final` și, mai important, adapterul ține referința la ea; trebuie sortată in-place.
3. **Uiți `notifyDataSetChanged()`.** Simptom: apeși butonul, ordinea din memorie se schimbă, dar lista arată la fel până la următoarea adăugare. Cauza: adapterul nu observă singur modificările din listă.

### **Verificarea**

Lista inițială este Inception, Toy Story, The Matrix. Apasă „Sort by title": ordinea devine Inception, The Matrix, Toy Story. Adaugă un film cu titlul „Alien" și apasă din nou: Alien urcă primul. Butonul FAB rămâne vizibil jos-dreapta, iar lista derulează corect.

### **Exersează**

[20.2 — al doilea FAB, jos-stânga, care afișează numărul de filme](cap-20.html#ex-20-2) · [20.4 — `Switch` deasupra listei care filtrează filmele văzute](cap-20.html#ex-20-4) · [20.8 — `Spinner` deasupra listei pentru sortare](cap-20.html#ex-20-8) · [24.1 — ce se întâmplă dacă uiți `notifyDataSetChanged()`](cap-24.html#ex-24-1)

---

## Rețeta 33.15 — Schimbă un widget cu altul

### **Cerința, cum sună la test**

„Înlocuiește `Switch`-ul `swWatched` cu un `CheckBox`, fără să strici salvarea și fără să schimbi ID-ul."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activity_item.xml` | înlocuiești tag-ul `MaterialSwitch` cu `MaterialCheckBox`, păstrezi `android:id="@+id/swWatched"` | da |
| 2 | `ItemActivity.java` | schimbi tipul câmpului din `MaterialSwitch` în `CheckBox`; restul rămâne | da |
| 3 | `ItemActivity.java` | schimbi importul `MaterialSwitch` cu `CheckBox` | da |
| 4 | `Movie.java` | nimic: `isWatched()` și `setWatched()` nu se schimbă | nu |

### **Pașii, în ordine**

**Pasul 1 — `activity_item.xml`, în cardul „Your verdict".** Înlocuiești tag-ul, dar **păstrezi ID-ul**:

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/swWatched"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginEnd="12dp"
    android:text="Watched" />
```

**Pasul 2 — `ItemActivity.java`, câmpul.** Tipul se schimbă, numele rămâne:

```java
private CheckBox swWatched;
```

**Pasul 3 — `ItemActivity.java`, importurile.** Scoți `com.google.android.material.materialswitch.MaterialSwitch` și adaugi:

```java
import android.widget.CheckBox;
```

**Pasul 4 — `ItemActivity.java`, `initControls()`.** Linia rămâne aproape identică; `findViewById` întoarce noul tip, pentru că ID-ul este același:

```java
swWatched = findViewById(R.id.swWatched);
```

**Pasul 5 — `ItemActivity.java`, `fillForm()`.** `CheckBox` este un `CompoundButton`, deci metoda există neschimbată:

```java
swWatched.setChecked(existing.isWatched());
```

**Pasul 6 — `ItemActivity.java`, `saveMovie()`.** La fel:

```java
movie.setWatched(swWatched.isChecked());
```

**Pasul 7 — `ItemActivity.java`, `initListeners()`.** Listener-ul rămâne pe `CompoundButton`, tipul comun al ambelor widget-uri:

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});
```

### **De ce merge așa**

ID-ul este contractul dintre XML și cod: `findViewById(R.id.swWatched)` caută în arborele de view-uri un view cu acel ID și îl întoarce cu tipul real din XML. `CheckBox` și `MaterialSwitch` sunt amândouă subclase de `CompoundButton`, care definește `isChecked()`, `setChecked()` și `setOnCheckedChangeListener()`. De aceea, dacă păstrezi ID-ul, singurele schimbări sunt tag-ul din XML, tipul câmpului și importul. Modelul nu se atinge deloc.

### **Greșeala care costă puncte**

1. **Schimbi și ID-ul, dar uiți `findViewById`.** Simptom: `error: cannot find symbol variable swWatched` sau, dacă ai schimbat doar XML-ul, `NullPointerException` la `swWatched.setChecked(...)`. Cauza: ID-ul din XML și cel din `R.id` trebuie să fie identice. Dacă redenumești ID-ul, îl schimbi în **toate** locurile.
2. **Schimbi tipul câmpului, dar lași importul `MaterialSwitch`.** Simptom: `error: cannot find symbol class MaterialSwitch` după ce ai șters tag-ul, sau `incompatible types` la atribuire. Cauza: importul vechi a rămas, iar cel nou lipsește.
3. **Folosești `Switch.OnCheckedChangeListener`.** Simptom: `error: cannot find symbol` — nu există o asemenea interfață. Cauza: listener-ul este definit în `CompoundButton`, clasa-părinte comună.

### **Verificarea**

Formularul arată o bifă pătrată în locul switch-ului. Adaugă un film cu bifa pornită: rândul arată `watched=true`. Atinge rândul: bifa este pornită, iar eticheta „Yes" este afișată. Debifează: eticheta devine „No" imediat. Salvează: rândul arată `watched=false`.

### **Exersează**

[18.2 — `etBudget` devine `SeekBar` (0–500 milioane, pas 1 milion)](cap-18.html#ex-18-2) · [18.3 — `rbRating` (`RatingBar`) devine `Spinner` cu 1–5 stele](cap-18.html#ex-18-3) · [20.9 — `TextInputLayout` cu `endIconMode="clear_text"` și ce NU face ștergerea](cap-20.html#ex-20-9)

---

## Rețeta 33.16 — Adaugă un ecran nou (Activity + layout + manifest)

### **Cerința, cum sună la test**

„Adaugă un ecran nou care arată titlul și genul filmului, deschis cu o apăsare lungă pe rândul din listă."

### **Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activity_detail.xml` | layout nou, cu `TextView`-uri cu ID-uri noi | da |
| 2 | `DetailActivity.java` | clasă nouă în `ro.ase.ie.g1097.activities` | da |
| 3 | `AndroidManifest.xml` | `<activity android:name=".activities.DetailActivity" android:exported="false" />` | da |
| 4 | `MainActivity.java` | `setOnItemLongClickListener` care pornește ecranul cu `startActivity` | da |

### **Pașii, în ordine**

**Pasul 1 — `res/layout/activity_detail.xml`, fișier nou.** Un layout simplu, cu rădăcina `LinearLayout`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp">

    <TextView
        android:id="@+id/tvDetailTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Movie title"
        android:textAppearance="?attr/textAppearanceHeadlineMedium"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/tvDetailGenre"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:text="Genre"
        android:textAppearance="?attr/textAppearanceBodyLarge" />
</LinearLayout>
```

**Pasul 2 — `DetailActivity.java`, fișier nou în `ro.ase.ie.g1097.activities`.** Citește filmul din `Intent` cu `IntentCompat`, exact ca `ItemActivity`:

```java
package ro.ase.ie.g1097.activities;

import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.IntentCompat;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class DetailActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);

        TextView tvDetailTitle = findViewById(R.id.tvDetailTitle);
        TextView tvDetailGenre = findViewById(R.id.tvDetailGenre);

        Movie movie = IntentCompat.getSerializableExtra(
                getIntent(), MainActivity.MOVIE_EXTRA, Movie.class);

        if (movie != null) {
            tvDetailTitle.setText(movie.getTitle());
            tvDetailGenre.setText(movie.getGenre());
        }
    }
}
```

**Pasul 3 — `AndroidManifest.xml`, în `<application>`, după `ItemActivity`.** Fără intrarea asta, ecranul nu poate fi pornit:

```xml
<activity
    android:name=".activities.DetailActivity"
    android:exported="false" />
```

**Pasul 4 — `MainActivity.java`, în `initListeners()`.** Adaugi apăsarea lungă, lângă `setOnItemClickListener`:

```java
listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
    @Override
    public boolean onItemLongClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, DetailActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        startActivity(intent);
        return true;
    }
});
```

**Pasul 5 — `MainActivity.java`, importurile.** `Intent` și `AdapterView` sunt deja importate; `DetailActivity` este în același pachet, deci nu are nevoie de import.

### **De ce merge așa**

Fiecare `Activity` trebuie declarată în `AndroidManifest.xml`, altfel sistemul nu o cunoaște și `startActivity` aruncă `ActivityNotFoundException`. `android:exported="false"` este corect pentru un ecran intern: numai aplicația ta îl poate porni. `setContentView` trebuie apelat înainte de `findViewById`, pentru că abia el construiește arborele de view-uri. `IntentCompat.getSerializableExtra` este varianta folosită de aplicație pentru `Serializable` pe API 33+, unde metoda veche este depreciată. Spre deosebire de `ItemActivity`, ecranul acesta este pornit cu `startActivity`, nu cu `launcher`, pentru că nu are ce rezultat să întoarcă.

### **Greșeala care costă puncte**

1. **Uiți intrarea din manifest.** Simptom: aplicația se închide la apăsarea lungă, cu `ActivityNotFoundException: Unable to find explicit activity class ... DetailActivity; have you declared this activity in your AndroidManifest.xml?`. Cauza: clasa există, dar sistemul nu o cunoaște.
2. **Uiți `setContentView`.** Simptom: `NullPointerException` la `tvDetailTitle.setText(...)`, pentru că `findViewById` nu găsește nimic într-un arbore inexistent. Cauza: ai sărit linia care încarcă layout-ul.
3. **Returnezi `false` din `onItemLongClick`.** Simptom: apăsarea lungă deschide ecranul nou, dar imediat după ea se deschide și ecranul de editare. Cauza: `false` înseamnă „evenimentul nu a fost consumat", deci `ListView` trimite și click-ul normal. `return true` îl consumă.

### **Verificarea**

Apasă lung pe „Inception": se deschide ecranul nou, cu titlul „Inception" și genul „Sci-Fi". Butonul Back te întoarce în listă, fără să modifice nimic. Apasă scurt pe același rând: se deschide formularul de editare, nu ecranul nou. Adaugă un film și apasă lung pe el: ecranul nou arată titlul lui.

### **Exersează**

[23.9 — click pe rând cu `getBindingAdapterPosition()` și callback](cap-23.html#ex-23-9) · [24.2 — editezi un film, lista arată valorile NOI. De ce `set` și nu `add`?](cap-24.html#ex-24-2) · [24.4 — 3 adăugări + 1 editare: numărul de filme e corect](cap-24.html#ex-24-4)

---

## Tabelul celor 16 rețete

| Rețeta | Ce adaugi | Fișiere atinse | Timp | Exercițiu |
|---|---|---|---|---|
| 33.1 | atribut `String` | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.1](cap-17.html#ex-17-1) |
| 33.2 | atribut `int` | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.6](cap-17.html#ex-17-6) |
| 33.3 | atribut `Integer` (nullable) | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.2](cap-17.html#ex-17-2) |
| 33.4 | atribut `float` / `double` | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.4](cap-17.html#ex-17-4) |
| 33.5 | atribut `boolean` | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 10 min | [17.3](cap-17.html#ex-17-3) |
| 33.6 | atribut `ArrayList<String>` | `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 12 min | [17.5](cap-17.html#ex-17-5) |
| 33.7 | atribut compus (clasă nouă) | `Director`, `Movie`, `activity_item`, `ItemActivity`, `MainActivity` | 15 min | [17.9](cap-17.html#ex-17-9) |
| 33.8 | atribut derivat | `Movie` | 5 min | [19.4](cap-19.html#ex-19-4) |
| 33.9 | schimbi tipul unui atribut | `Movie`, `ItemActivity` | 8 min | [18.3](cap-18.html#ex-18-3) |
| 33.10 | redenumești un atribut | `Movie`, `ItemActivity` | 8 min | [17.10](cap-17.html#ex-17-10) |
| 33.11 | widget nou în formular | `activity_item`, `ItemActivity` | 10 min | [18.1](cap-18.html#ex-18-1) |
| 33.12 | widget nou în rând | `movie_item`, adapter (dacă există) | 10 min | [23.6](cap-23.html#ex-23-6) |
| 33.13 | buton nou | `activity_item`, `ItemActivity` | 10 min | [20.1](cap-20.html#ex-20-1) |
| 33.14 | control deasupra listei | `activity_main`, `MainActivity` | 12 min | [20.8](cap-20.html#ex-20-8) |
| 33.15 | schimbi un widget cu altul | `activity_item`, `ItemActivity` | 8 min | [18.2](cap-18.html#ex-18-2) |
| 33.16 | ecran nou | layout nou, `DetailActivity`, manifest, `MainActivity` | 15 min | [23.9](cap-23.html#ex-23-9) |

---

## Rezumat capitol 33

- **Ordinea este mereu aceeași:** model → XML → `ItemActivity` → afișare. Modelul întâi, pentru că nu depinde de nimic; XML-ul al doilea, pentru că `findViewById` are nevoie de ID; legătura a treia; afișarea ultima.
- **Un atribut nou are patru locuri în model:** câmp, getter, setter, parametru în constructor — plus `toString()` dacă vrei să se vadă în `ListView`. Toate cinci se schimbă împreună.
- **Constructorul este pozițional.** Când îi adaugi un parametru, actualizezi toate apelurile `new Movie(...)`. Compilatorul îți spune exact câte argumente lipsesc.
- **`setText` are două fețe.** `setText(CharSequence)` scrie text; `setText(int)` caută o resursă. Pentru numere, `String.valueOf(...)` este obligatoriu — altfel `int`-ul devine ID de resursă și iei `Resources.NotFoundException`.
- **Parsezi cu protecție.** `Integer.parseInt`, `Float.parseFloat` și `Double.parseDouble` aruncă `NumberFormatException` pe șir gol. Verifici `isEmpty()` și faci `trim()`; la zecimale normalizezi virgula.
- **`fillForm` este oglinda lui `saveMovie`.** Fiecare widget citit la salvare trebuie scris la încărcare. Capcana reală a aplicației: `fillForm` nu sincronizează `releaseCal`, deci o editare fără atingerea datei salvează data de azi.
- **`ListView` afișează `toString()`.** `movie_item.xml` există, dar nu este folosit de niciun cod; devine activ doar la migrarea la `RecyclerView`.
- **ID-ul este contractul.** Poți schimba tipul widget-ului fără să atingi modelul, dacă păstrezi ID-ul; dacă îl redenumești, îl schimbi în XML și în toate `findViewById`.
- **Un ecran nou are trei piese obligatorii:** layout, clasă care apelează `setContentView` înainte de `findViewById`, și intrare în `AndroidManifest.xml`. Fără manifest, `ActivityNotFoundException`.
