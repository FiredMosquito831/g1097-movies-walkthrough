# Capitolul 22 — Codul G1097 adnotat

**Obiectiv:** să citești codul aplicației cu explicații pe fiecare bloc — ce face, de ce e acolo, ce s-ar întâmpla dacă ai șterge linia.

**Timp estimat:** 60–90 min (citire activă).

**Sursa:** commitul `d719ffc`. Toate cele 6 fișiere care contează.

> **Cum citești:** nu citi pasiv. Pentru fiecare bloc, acoperă explicația și încearcă să spui tu ce face. Dacă nu poți, ai găsit ce trebuie repetat.

---

## 22.1 `Movie.java` — modelul

### Fișierul complet, adnotat

```java
package ro.ase.ie.g1097.model;          // subpachetul `model` — date curate

import java.io.Serializable;            // marker: obiectul poate fi trimis prin Intent
import java.util.Date;                  // tipul datei de lansare

public class Movie implements Serializable {
```

**De ce `implements Serializable`:** `Intent.putExtra(String, Serializable)` e singurul mod simplu de a trimite un obiect întreg între două activități. Fără el, `putExtra(MOVIE_EXTRA, movie)` nu compilează.

**De ce nu are `import android.*`:** modelul trebuie testabil fără emulator. Dacă ar importa `EditText`, ar depinde de UI.

```java
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
```

**Comentariile din dreapta sunt documentația profesorului:** fiecare câmp notează **ce widget** îl produce. Le păstrezi — la test, întrebarea „de unde vine câmpul X?" are răspunsul chiar în cod.

**De ce fiecare tip:**

| Câmp | Tip | De ce |
|---|---|---|
| `title` | `String` | text liber din `EditText` |
| `release` | `Date` | o dată, ca să poți calcula diferențe |
| `genre` | `String` | textul selectat din `Spinner` |
| `budget` | `double` | are zecimale; `float` pierde precizie la 160 000 000 |
| `duration` | `int` | `SeekBar.getProgress()` întoarce `int` |
| `rating` | `float` | `RatingBar.getRating()` întoarce `float` |
| `watched` | `boolean` | `isChecked()` |
| `approval` | `String` | textul butonului radio selectat („PG-13") |
| `onWatchlist` | `boolean` | `isChecked()` |
| `poster` | `String` | un URL |

**`poster = null` explicit** — deși `String` e `null` implicit, linia documentează: „poate lipsi".

```java
    public Movie(String title, Date release, String genre, double budget, int duration,
                 float rating, boolean watched, String approval,
                 boolean onWatchlist, String poster) {
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

**De ce `this.title = title`:** parametrul are același nume cu câmpul. Fără `this`, ai face `title = title` — auto-atribuire, câmpul rămâne `null`.

**Ordinea parametrilor e pozițională** și trebuie respectată exact:

```
1. String title      6. float rating
2. Date release      7. boolean watched
3. String genre      8. String approval
4. double budget     9. boolean onWatchlist
5. int duration     10. String poster
```

> Dacă inversezi doi parametri de **același tip**, compilatorul nu te prinde. Filmul se creează, dar cu date greșite.

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

**De ce contează `toString()`:** `ArrayAdapter` îl cheamă pe fiecare element ca să afișeze rândul. Fără suprascriere, lista ar arăta `ro.ase.ie.g1097.model.Movie@a1b2c3d`.

**Formatul** e generat de IntelliJ (**Alt+Insert → toString()**). `'\''` e un apostrof escapate.

**Ce se vede în listă la `d719ffc`:** toate cele 10 câmpuri pe un rând, inclusiv URL-ul posterului. Urât, dar corect. Se repară în capitolul 11 cu `RecyclerView`.

```java
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    // ... la fel pentru toate cele 10

    public boolean isWatched() { return watched; }
    public void setWatched(boolean watched) { this.watched = watched; }

    public boolean isOnWatchlist() { return onWatchlist; }
    public void setOnWatchlist(boolean onWatchlist) { this.onWatchlist = onWatchlist; }

    public Movie() {
    }
}
```

**`isWatched()` și nu `getWatched()`** — convenția JavaBeans pentru `boolean`. În capitolul 11, `MovieAdapter` apelează `movie.isWatched()`. Dacă ai scris `getWatched()`, nu compilează.

**Constructorul gol e la sfârșit** — poziția nu contează pentru compilator, dar **existența lui e obligatorie**:

> Dacă definești un constructor cu parametri, Java **nu mai generează** automat constructorul fără parametri. Iar `ItemActivity.saveMovie()` face `new Movie();`. Fără el, nu compilează.

---

## 22.2 `MainActivity.java` — lista și navigarea

### Constantele și câmpurile

```java
public class MainActivity extends AppCompatActivity {

    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";
```

**De ce constante și nu `"movie"` scris de mână:** cheia e folosită în două activități. Dacă scrii `"movie"` într-un loc și `"Movie"` în altul, primești `null` **fără nicio eroare**.

**De ce `protected static final`:**
- `protected` — accesibil din `ItemActivity` (sunt în același pachet `activities`)
- `static` — aparține clasei, nu instanței
- `final` — nu se schimbă

```java
    private FloatingActionButton fabInsert;
    private ListView listView;
    private ActivityResultLauncher<Intent> launcher;
    private final List<Movie> movies = new ArrayList<>();
    private ArrayAdapter<Movie> movieAdapter;
```

**De ce câmpuri și nu variabile locale:** sunt folosite în mai multe metode (`onCreate`, `initControls`, `initListeners`).

**De ce `final` pe `movies`:** referința nu se schimbă niciodată — aceeași listă, doar conținutul i se modifică. Poți face `movies.add(...)`, dar nu `movies = ...`.

**De ce `List<Movie>` și nu `ArrayList<Movie>`:** `List` e interfața. Poți schimba implementarea oricând fără să modifici restul codului.

### `onCreate` — ordinea contează

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);      // 1. ciclul de viață al părintelui
        EdgeToEdge.enable(this);                 // 2. permite desenarea sub barele de sistem
        setContentView(R.layout.activity_main);  // 3. construiește arborele de view-uri
```

**Ordinea e obligatorie.** `findViewById` apelat înainte de `setContentView` întoarce `null`.

```java
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
```

**Ce face:** aplică padding egal cu barele de sistem pe **rădăcină** (`R.id.main`). Fără el, primul rând din listă intră sub ceas, iar FAB-ul sub bara de navigare.

**De ce pe rădăcină:** padding-ul pe rădăcină împinge **toți** copiii în zona sigură. Pe un copil, ceilalți ar rămâne sub bare.

**`return insets`** (nu `CONSUMED`) lasă insets-urile să circule mai departe.

```java
        addSampleMovies();                                          // 4. umple lista (fără UI)

        movieAdapter = new ArrayAdapter<>(this,                     // 5. creează adapterul
                android.R.layout.simple_list_item_1, movies);
        initControls();                                             // 6. findViewById + setAdapter
        initListeners();                                            // 7. leagă butoanele
```

**De ce `addSampleMovies` înainte de `new ArrayAdapter`:** adapterul primește **referința** la listă. Umplând-o înainte, adapterul vede lista deja plină la construcție — nu ai nevoie de `notifyDataSetChanged()`.

**De ce `initControls` după `new ArrayAdapter`:** `initControls` face `listView.setAdapter(movieAdapter)`. Dacă `movieAdapter` ar fi `null`, ai `NullPointerException`.

```java
        launcher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {
                        if (o.getResultCode() == RESULT_OK) {
                            Intent intent = o.getData();
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);
                            if (position == -1) {
                                movies.add(movie);                 // insert
                            } else {
                                movies.set(position, movie);       // edit
                            }
                            movieAdapter.notifyDataSetChanged();   // ← obligatoriu
                        }
                    }
                });
    }
```

**`launcher` e inițializat DUPĂ `initListeners()`** — o capcană reală a repo-ului. Funcționează doar pentru că listener-ul **nu se execută la înregistrare**, ci la click. La click, `launcher` e deja inițializat.

> Dacă ai apela `fabInsert.performClick()` imediat după `initListeners()`, ai avea `NullPointerException`.

**`getResultCode() == RESULT_OK`** — obligatoriu. Fără verificare, când utilizatorul apasă Back, `getData()` e `null` → NPE.

**`position == -1`** = insert (FAB), `position >= 0` = edit (click pe rând).

**`notifyDataSetChanged()`** — fără el, lista nu se redesenează. Filmul se salvează, dar nu apare.

### `initControls` — legătura XML ↔ cod

```java
    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        listView = findViewById(R.id.listView);
        listView.setAdapter(movieAdapter);
    }
```

**`findViewById` e generic** în Java modern: `ListView listView = findViewById(R.id.listView);` funcționează fără cast.

**`setAdapter` e ultima linie** — leagă sursa de date de widget.

### `initListeners` — cele două acțiuni

```java
    private void initListeners() {
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);
                launcher.launch(intent);
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

**`MainActivity.this` și nu `this`:** în interiorul clasei anonime, `this` e clasa anonimă — care nu e `Context`. `new Intent(this, ...)` ar da eroare.

**`launcher.launch(intent)` și nu `startActivity(intent)`:** al doilea pornește activitatea, dar **nu primești nimic înapoi**.

**FAB → `Intent` fără extra-uri** → `ItemActivity` intră în insert mode.
**Click pe rând → `Intent` cu `MOVIE_EXTRA` + `POSITION_EXTRA`** → `ItemActivity` intră în edit mode.

### `addSampleMovies` — datele demo

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
        // ... Toy Story, The Matrix
    }
```

**`GregorianCalendar(2010, Calendar.JULY, 16)`** — lunile sunt indexate **de la 0**: `JULY` = 6, nu 7. De aceea se folosesc constantele.

**`.getTime()`** — `GregorianCalendar` **este** un `Calendar`, nu un `Date`. `getTime()` extrage milisecundele.

**`4.5f`** — literal `float`. `4.5` ar fi `double` și nu s-ar potrivi la parametrul `float` fără cast.

---

## 22.3 `ItemActivity.java` — formularul

### Câmpurile și starea

```java
public class ItemActivity extends AppCompatActivity {

    private EditText etTitle;
    private EditText etRelease;
    private Spinner spGenre;
    private EditText etBudget;
    private SeekBar sbDuration;
    private RatingBar rbRating;
    private RadioGroup rgApproval;
    private CheckBox cbonWatchList;
    private MaterialSwitch swWatched;
    private EditText etPoster;
    private Button btMovieAction;
    private TextView tvDurationValue;
    private TextView tvWatchedValue;
```

**13 referințe la view-uri.** Cele 7 `TextView`-uri de etichetă (`tvTile`, `tvGenre` etc.) nu apar aici — nu sunt folosite în cod, doar în XML.

**Atenție la nume:** `cbonWatchList` (câmp) ↔ `cbOnWatchList` (ID), `btMovieAction` (câmp) ↔ `btnMovieAction` (ID). Inconsecvențe ale repo-ului — respectă-le exact.

```java
    private int position = -1;   // -1 = insert mode
    private Calendar releaseCal = Calendar.getInstance();
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());
```

**`position = -1`** — sentinel. Orice valoare ≥ 0 = „editez filmul de la poziția asta".

**`releaseCal = Calendar.getInstance()`** — data implicită e **acum**. Alternativa `null` ar crăpa în `saveMovie`.

**`SimpleDateFormat` e mutabil și nu e thread-safe.** Aici e folosit doar pe UI thread, deci e OK. `final` garantează că nu e reasignat.

### `onCreate` și citirea modului

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_item);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            // ... identic cu MainActivity, dar pe ScrollView-ul din activity_item
        });

        initControls();
        initListeners();
    }
```

> **În repo, blocul care citește `Intent`-ul e adăugat tot aici** (capitolul 09). La `d719ffc` `fillForm` există și e apelat din `onCreate` când `existing != null`.

### `initControls` — cele 13 `findViewById`

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

**De ce toate într-o metodă:** dacă un ID e greșit, `findViewById` întoarce `null` și eroarea apare mai târziu, la primul acces. Grupându-le, vezi imediat dacă vreunul lipsește.

### `initListeners` — patru listeneri

```java
    private void initListeners() {
        etRelease.setOnClickListener(v -> showReleaseDatePicker());
        btMovieAction.setOnClickListener(v -> saveMovie());

        swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
                tvWatchedValue.setText(isChecked ? "Yes" : "No"));

        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                tvDurationValue.setText(progress + " min.");
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) { }
            @Override public void onStopTrackingTouch(SeekBar seekBar) { }
        });
    }
```

**`setOnClickListener` pe un `EditText`** — un `EditText` primește focus la atingere, nu click. Dar `setOnClickListener` funcționează: la prima atingere primește focus **și** declanșează click-ul.

**`SeekBar` are clasă anonimă** (3 metode), **`Switch` are lambda** (1 metodă).

**`fromUser` e ignorat** — textul se actualizează și când valoarea vine din cod (`setProgress` în `fillForm`). E corect: vrei ca eticheta să reflecte mereu valoarea.

### `showReleaseDatePicker`

```java
    private void showReleaseDatePicker() {
        String current = etRelease.getText().toString();
        if (!current.isEmpty()) {
            try {
                Date parsed = dateFormat.parse(current);
                if (parsed != null)
                    releaseCal.setTime(parsed);
            } catch (ParseException ignored) { }
        }

        new DatePickerDialog(this,
                (view, year, month, day) -> {
                    releaseCal.set(year, month, day);
                    etRelease.setError(null);
                    etRelease.setText(dateFormat.format(releaseCal.getTime()));
                },
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)
        ).show();
    }
```

**Fluxul:**
1. citește textul curent;
2. dacă nu e gol, îl parsează în `releaseCal`;
3. deschide dialogul poziționat pe `releaseCal`;
4. la confirmare, actualizează `releaseCal` și textul.

**`month` e 0-indexat și aici** — `DatePickerDialog` întoarce direct valoarea corectă pentru `Calendar.set`. Fără `-1`.

**`catch (ParseException ignored) { }`** — dacă utilizatorul a tastat „abc", ignorăm și pornim de la data anterioară. Un `catch` gol e acceptabil **doar** când eroarea nu schimbă comportamentul dorit.

### `saveMovie` — construirea modelului

```java
    private void saveMovie() {
        Movie movie = new Movie();
        movie.setTitle(etTitle.getText().toString());
        movie.setRelease(releaseCal.getTime());
        movie.setGenre(spGenre.getSelectedItem().toString());
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));
        movie.setDuration(sbDuration.getProgress());
        movie.setRating(rbRating.getRating());
        movie.setWatched(swWatched.isChecked());
        movie.setOnWatchlist(cbonWatchList.isChecked());
        movie.setPoster(etPoster.getText().toString());

        for (int index = 0; index < rgApproval.getChildCount(); index++) {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
            if (rb.isChecked()) {
                movie.setApproval(rb.getText().toString());
                break;
            }
        }

        Intent intent = new Intent();
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);
        setResult(RESULT_OK, intent);
        finish();
    }
```

**Sursa fiecărui câmp:**

| Model | Sursă | Metodă |
|---|---|---|
| `title` | `etTitle` | `getText().toString()` |
| `release` | `releaseCal` | `getTime()` — **nu** `etRelease` |
| `genre` | `spGenre` | `getSelectedItem().toString()` |
| `budget` | `etBudget` | `Double.parseDouble(...)` |
| `duration` | `sbDuration` | `getProgress()` |
| `rating` | `rbRating` | `getRating()` |
| `watched` | `swWatched` | `isChecked()` |
| `onWatchlist` | `cbonWatchList` | `isChecked()` |
| `poster` | `etPoster` | `getText().toString()` |
| `approval` | `rgApproval` | iterezi copiii |

**De ce `releaseCal` și nu `etRelease`:** calendarul e sursa de adevăr. Textul poate fi gol sau invalid.

**Bucla radio e generică** — adaugi un buton în XML, codul îl vede fără modificări.

**`if (position != -1)`** — în insert mode nu trimiți poziția; `MainActivity` interpretează absența ca „adaugă la final".

**`setResult(RESULT_OK, intent)` + `finish()`** — perechea obligatorie. Fără `setResult`, `MainActivity` primește `RESULT_CANCELED` și nu face nimic.

### Bug-urile reale din acest fișier

| Linie | Bug | Ce se întâmplă |
|---|---|---|
| `Double.parseDouble(etBudget.getText().toString())` | câmp gol → `""` | `NumberFormatException` → crash |
| `dateFormat.format(existing.getRelease())` în `fillForm` | `release` e `null` | `NullPointerException` → crash |
| `String.valueOf(existing.getBudget())` în `fillForm` | 160000000.0 | afișează `1.6E8` |

**Toate trei sunt reale la `d719ffc`** și documentate în capitolele 07 și 09. Dacă la test ți se cere să le repari, știi exact ce să faci.

---

## 22.4 `activity_main.xml` — ecranul listei

```xml
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">
```

**`FrameLayout`** — stivulește copiii unul peste altul. Ordinea în XML = ordinea de desenare.

**`android:id="@+id/main"`** — folosit de insets în cod. Fără el, `findViewById(R.id.main)` întoarce `null`.

**`android:orientation="horizontal"`** — **atribut invalid** pe `FrameLayout`. Ignorat de Android, warning de lint. Rămășiță de la un `LinearLayout` anterior.

**`tools:context`** — doar pentru preview, eliminat la build.

```xml
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />
```

**`android:entries`** — umple lista din XML cu 20 de „Item 1..20". La runtime, `listView.setAdapter(movieAdapter)` **îl înlocuiește**. Rămâne pentru preview.

```xml
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_24" />
</FrameLayout>
```

**`layout_gravity="bottom|end"`** — poziția **elementului** în părinte. `end` respectă direcția de citire (RTL).

**`contentDescription`** — obligatoriu pentru imagini, altfel lint-ul dă eroare. Textul e citit de TalkBack.

**`app:srcCompat`** — variantă compatibilă pentru `VectorDrawable`.

**Ordinea:** `ListView` primul, FAB al doilea → FAB-ul e **peste** listă. Invers, lista l-ar acoperi.

---

## 22.5 `activity_item.xml` — formularul

### Structura

```
ScrollView (id=main)                     ← un singur copil
└── LinearLayout vertical (padding 16/24/24)
    ├── TextView "Movie details"         ← titlu
    ├── TextView "Fill in the information below..."
    ├── MaterialCardView [Basics]
    │   └── LinearLayout vertical (padding 16dp)
    │       ├── TextView "Basics" (colorPrimary)
    │       ├── TextView tvTile + TextInputLayout(hintEnabled=false) + etTitle
    │       ├── TextView tvGenre + MaterialCardView(outlined) + Spinner spGenre
    │       └── TextInputLayout(startIcon=calendar) + etRelease
    ├── MaterialCardView [Production]
    │   ├── TextView "Production"
    │   ├── TextView tvBudget + TextInputLayout(prefixText="$ ") + etBudget
    │   ├── LinearLayout (tvDuration + tvDurationValue)
    │   ├── SeekBar sbDuration (max=300, min=0)
    │   └── LinearLayout ("0 min" / "300 min")
    ├── MaterialCardView [Your verdict]
    │   ├── TextView "Your verdict"
    │   ├── TextView tvRating + RatingBar rbRating (5 stele, step 0.5)
    │   ├── View (separator 1dp)
    │   ├── LinearLayout (tvWatched + tvWatchedValue | swWatched | cbOnWatchList)
    │   ├── View (separator 1dp)
    │   ├── TextView tvGuidance
    │   └── HorizontalScrollView + RadioGroup rgApproval (5 butoane)
    ├── MaterialCardView [Poster]
    │   ├── TextView "Poster"
    │   └── TextInputLayout(startIcon=gallery) + etPoster
    └── MaterialButton btnMovieAction (60dp, cornerRadius 30dp)
```

### Blocurile care merită explicate

**`ScrollView` cu un singur copil:**

```xml
<ScrollView ...
    android:id="@+id/main"
    android:background="?attr/colorSurface"
    android:fillViewport="true">
```

> `ScrollView` are voie cu **exact un copil**. Doi → `ScrollView can host only one direct child`.

**`?attr/colorSurface`** — culoarea din temă (alb în light, gri închis în dark). `#FFFFFF` ar rupe dark mode-ul.

**`fillViewport="true"`** — întinde conținutul să umple ecranul dacă e mai scurt.

**`TextInputLayout` cu etichetă fixă:**

```xml
<TextView android:id="@+id/tvTile" android:text="Title" ... />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    app:hintEnabled="false"
    app:endIconMode="clear_text">
    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etTitle"
        android:hint="Movie title"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

**`hintEnabled="false"`** — dezactivează hint-ul plutitor. Altfel ai **două** etichete: `TextView`-ul de deasupra și hint-ul din contur.

**`endIconMode="clear_text"`** — un „X" în dreapta care șterge textul. **Nu** resetează modelul — doar `EditText`-ul.

**`tvTile`** — typo în repo pentru „tvTitle". Nu e folosit în cod.

**`Spinner` în `MaterialCardView` outlined:**

```xml
<com.google.android.material.card.MaterialCardView
    style="?attr/materialCardViewOutlinedStyle"
    android:layout_height="56dp"
    app:cardBackgroundColor="@android:color/transparent"
    app:cardCornerRadius="4dp"
    app:strokeColor="?attr/colorOutline">

    <Spinner android:id="@+id/spGenre"
        android:entries="@array/movie_genre"
        android:spinnerMode="dropdown" />
</com.google.android.material.card.MaterialCardView>
```

**Trucul:** `Spinner`-ul nativ nu are contur. Îl învelești într-un card outlined ca să arate ca celelalte câmpuri `OutlinedBox` (contur 1dp, colțuri 4dp, înălțime 56dp).

**Aici `entries` rămâne** — `ItemActivity` nu apelează `spGenre.setAdapter(...)`.

**`SeekBar`:**

```xml
<SeekBar
    android:id="@+id/sbDuration"
    android:max="300"
    android:min="0"
    android:progressTint="?attr/colorPrimary"
    android:thumbTint="?attr/colorPrimary" />
```

**`android:min` e disponibil din API 26.** `minSdk 33`, deci merge.

**Cele două etichete „0 min" / „300 min" sunt hardcodate** — dacă schimbi `max`, trebuie să le schimbi și pe ele.

**`RatingBar`:**

```xml
<RatingBar
    android:id="@+id/rbRating"
    android:numStars="5"
    android:stepSize="0.5"
    android:progressTint="#FFC107"
    android:secondaryProgressTint="#FFC107"
    android:progressBackgroundTint="?attr/colorOutlineVariant" />
```

**`#FFC107` hardcodat** — galben de stele, semnificație fixă, nu rol de temă. Excepție asumată.

**`stepSize="0.5"`** — jumătăți de stea. `getRating()` întoarce `float`.

**`RadioGroup` în `HorizontalScrollView`:**

```xml
<HorizontalScrollView android:scrollbars="none">
    <RadioGroup android:id="@+id/rgApproval"
        android:orientation="horizontal">
        <com.google.android.material.radiobutton.MaterialRadioButton
            android:id="@+id/rbGeneral"
            android:checked="true"
            android:text="G" />
        <!-- PG, PG-13, R, NC-17 -->
    </RadioGroup>
</HorizontalScrollView>
```

**`HorizontalScrollView`** — 5 butoane nu încap pe un ecran de 360dp.

**`android:checked="true"` pe primul** — `rgApproval` are **mereu** o valoare. Nu poți salva un film fără ghidaj.

**`MaterialButton`:**

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnMovieAction"
    style="@style/Widget.Material3.Button"
    android:layout_height="60dp"
    app:cornerRadius="30dp"
    app:icon="@android:drawable/ic_menu_save"
    app:iconGravity="textStart" />
```

**`cornerRadius = height / 2`** = pill. `Widget.Material3.Button` **este** varianta filled.

---

## 22.6 `movie_item.xml` — cardul pentru RecyclerView

**Nu e folosit la `d719ffc`.** `git grep movie_item` întoarce 0 rezultate. E pregătirea pentru laboratorul următor.

```xml
<com.google.android.material.card.MaterialCardView
    android:layout_marginHorizontal="12dp"
    android:layout_marginVertical="6dp"
    app:cardCornerRadius="16dp"
    app:cardElevation="3dp"
    app:cardUseCompatPadding="true">

    <LinearLayout android:orientation="horizontal" android:padding="12dp">

        <ImageView
            android:id="@+id/moviePoster"
            android:layout_width="96dp"
            android:layout_height="140dp"
            android:scaleType="centerCrop" />

        <LinearLayout android:layout_width="0dp" android:layout_weight="1"
            android:orientation="vertical" android:layout_marginStart="12dp">

            <TextView android:id="@+id/movieTitle" android:textSize="20sp"
                android:textStyle="bold" android:maxLines="2" android:ellipsize="end" />

            <TextView android:id="@+id/movieSubtitle" android:textSize="14sp" />

            <LinearLayout android:orientation="horizontal">
                <RatingBar android:id="@+id/movieRating"
                    style="?android:attr/ratingBarStyleSmall"
                    android:isIndicator="true" />
                <TextView android:id="@+id/movieRatingValue" />
            </LinearLayout>

            <TextView android:id="@+id/movieFacts" android:textSize="13sp" />

            <com.google.android.material.chip.ChipGroup android:id="@+id/movieStatusGroup">
                <Chip android:id="@+id/chipApproval" android:clickable="false" />
                <Chip android:id="@+id/chipWatched" android:clickable="false" />
                <Chip android:id="@+id/chipWatchlist" android:clickable="false" />
            </ChipGroup>
        </LinearLayout>
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

**`cardElevation="3dp"`** — aici umbra e **prezentă**, spre deosebire de cardurile din formular. E un element de listă, nu o secțiune.

**`ImageView` 96×140dp** — raport ~2:3, ca un poster. `scaleType="centerCrop"` umple fără să deformeze.

**`layout_width="0dp"` + `layout_weight="1"`** pe coloana de text — ia tot spațiul rămas după poster.

**`maxLines="2"` + `ellipsize="end"`** — titlurile lungi se trunchiază cu „…".

**`isIndicator="true"`** — stelele sunt doar afișare, nu input. Fără listener necesar.

**`clickable="false"` pe chips** — sunt etichete, nu butoane.

**`ensureMinTouchTargetSize="false"`** — altfel Material le împinge la 48dp și strică layout-ul.

---

## 22.7 Cum se leagă totul — fluxul complet

```
PORNIRE
  MainActivity.onCreate
    ├── setContentView(activity_main)
    ├── insets pe R.id.main
    ├── addSampleMovies()            → 3 filme în `movies`
    ├── new ArrayAdapter(movies)     → movieAdapter
    ├── initControls()               → findViewById + setAdapter
    ├── initListeners()              → FAB + item click
    └── registerForActivityResult    → launcher

APASĂ FAB
  onClick → Intent(MainActivity → ItemActivity)
          → launcher.launch(intent)
            ↓
  ItemActivity.onCreate
    ├── setContentView(activity_item)
    ├── initControls()               → 13 × findViewById
    ├── initListeners()              → date picker, save, switch, seekbar
    └── existing == null             → insert mode (formular gol)

COMPLETEAZĂ + SAVE
  saveMovie()
    ├── new Movie()
    ├── 10 × setter din widget-uri
    ├── buclă pe rgApproval
    ├── Intent cu MOVIE_EXTRA (fără POSITION_EXTRA)
    ├── setResult(RESULT_OK, intent)
    └── finish()
          ↓
  MainActivity.onActivityResult
    ├── resultCode == RESULT_OK ?
    ├── position == -1  → movies.add(movie)
    └── movieAdapter.notifyDataSetChanged()
          ↓
  ListView redesenează → filmul apare

CLICK PE RÂND
  onItemClick(position)
    ├── Intent cu MOVIE_EXTRA + POSITION_EXTRA
    └── launcher.launch(intent)
          ↓
  ItemActivity.onCreate
    ├── existing != null
    ├── position = ...
    ├── fillForm(existing)          → umple cele 10 câmpuri
    └── setTitle + buton „Update Movie"

EDITEZI + UPDATE
  saveMovie()
    ├── Intent cu MOVIE_EXTRA + POSITION_EXTRA
    └── setResult + finish()
          ↓
  MainActivity.onActivityResult
    ├── position != -1 → movies.set(position, movie)
    └── notifyDataSetChanged()
```

---

## 22.8 Ce să reții din fiecare fișier

| Fișier | Esența |
|---|---|
| `Movie.java` | POJO serializabil, 10 câmpuri, constructor gol explicit, `isX()` pentru booleeni, `toString()` = contract de afișare |
| `MainActivity.java` | ordinea din `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` |
| `ItemActivity.java` | 13 `findViewById`, `releaseCal` ca sursă de adevăr, buclă generică pe `RadioGroup`, `setResult` + `finish` |
| `activity_main.xml` | `FrameLayout` + ordinea copiilor + `layout_gravity` pe FAB |
| `activity_item.xml` | `ScrollView` cu un copil, `MaterialCardView` ca secțiune, `TextInputLayout`, `Spinner` învelit |
| `movie_item.xml` | card de listă, `weight` pentru coloana de text, chips pentru stare |

---

## Rezumat capitol 22

- Modelul nu atinge UI-ul; activitățile nu conțin logică de rând.
- `onCreate`: `super` → `setContentView` → `findViewById` → restul.
- `releaseCal` e sursa de adevăr, nu textul din `EditText`.
- Bucla pe `RadioGroup` face codul generic — adaugi butoane, codul le vede.
- `setResult(RESULT_OK)` + `finish()` e perechea obligatorie.
- `notifyDataSetChanged()` după orice modificare a listei.
- `movie_item.xml` există dar nu e legat — pregătire pentru laboratorul următor.
- Trei bug-uri reale: buget gol, `release` null, notație științifică.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [prezentarea generală](index.html).
