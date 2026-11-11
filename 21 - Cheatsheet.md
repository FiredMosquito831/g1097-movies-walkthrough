# Capitolul 21 — Cheatsheet: module, clase și rețete

**Obiectiv:** o referință densă. Fiecare lucru care se poate cere la test, cu codul exact și cu „când îl folosești".

**Timp estimat:** 30 min citit, apoi revii ca la orice cheatsheet.

> **Cum îl folosești:** nu îl citești de la cap la coadă înainte de test. Îl răsfoiești acum o dată, apoi când te blochezi într-un exercițiu cauți secțiunea.

---

## 21.1 Harta fișierelor G1097

```
G1097/
├── build.gradle.kts                  namespace, minSdk 33, viewBinding=true
└── src/main/
    ├── AndroidManifest.xml           declară MainActivity + ItemActivity
    ├── java/ro/ase/ie/g1097/
    │   ├── model/Movie.java          DATELE. Fără importuri android.*
    │   ├── activities/MainActivity.java   LISTA + navigarea
    │   └── activities/ItemActivity.java   FORMULARUL
    └── res/
        ├── layout/activity_main.xml  FrameLayout + ListView + FAB
        ├── layout/activity_item.xml  ScrollView + 4 carduri + buton
        ├── layout/movie_item.xml     cardul de rând (pentru RecyclerView)
        ├── values/strings.xml        app_name, items, movie_genre
        ├── values/themes.xml         Theme.Material3.DayNight.NoActionBar
        └── values-night/themes.xml   varianta dark
```

**Regula de aur:** `model` nu știe ce e un widget. `activities` nu conțin logică de afișare per rând. `adapters` nu știu ce e o `Activity`.

---

## 21.2 Modelul `Movie` — cum adaugi un atribut

### Câmpurile existente și de ce au tipul lor

| Câmp | Tip | Widget sursă | De ce tipul ăsta |
|---|---|---|---|
| `title` | `String` | `TextInputEditText` | text liber |
| `release` | `Date` | `TextInputEditText` + `DatePickerDialog` | o dată, ca să poți calcula |
| `genre` | `String` | `Spinner` | unul din 10 texte |
| `budget` | `double` | `TextInputEditText` (`numberDecimal`) | bani cu zecimale |
| `duration` | `int` | `SeekBar` | progresul e `int` |
| `rating` | `float` | `RatingBar` | `getRating()` întoarce `float` |
| `watched` | `boolean` | `MaterialSwitch` | bifă |
| `approval` | `String` | `RadioGroup` | textul butonului selectat |
| `onWatchlist` | `boolean` | `MaterialCheckBox` | bifă |
| `poster` | `String` | `TextInputEditText` (`textUri`) | URL |

### Rețeta: adaugi un atribut nou (5 pași, în ordinea asta)

```java
// 1. Movie.java
private String writer;
public String getWriter() { return writer; }
public void setWriter(String writer) { this.writer = writer; }
// + adaugă-l în constructorul cu 10 argumente (devine 11)

// 2. activity_item.xml — un TextInputLayout + TextInputEditText cu android:id="@+id/etWriter"

// 3. ItemActivity.java
etWriter = findViewById(R.id.etWriter);          // initControls
etWriter.setText(existing.getWriter());          // fillForm
movie.setWriter(etWriter.getText().toString());  // saveMovie

// 4. movie_item.xml — un TextView cu android:id="@+id/movieWriter"

// 5. MovieAdapter.java (dacă folosești RecyclerView)
movieWriter = itemView.findViewById(R.id.movieWriter);   // ViewHolder
movieWriter.setText(movie.getWriter());                  // bind()
```

**Dacă rămâi pe `ListView` + `ArrayAdapter`:** pasul 4 și 5 dispar. Dar atunci atributul se vede doar prin `toString()`:

```java
@Override
public String toString() {
    return title + " — " + writer + " (" + rating + ")";
}
```

> **De ce ordinea contează:** modelul întâi, UI-ul după. Dacă începi cu XML-ul, codul nu compilează până nu adaugi câmpul.

### Tipuri de atribut și ce widget le produce

| Tip | Widget | Cum citești |
|---|---|---|
| `String` | `EditText` | `getText().toString()` |
| `String` (din listă) | `Spinner` | `getSelectedItem().toString()` |
| `int` | `SeekBar` | `getProgress()` |
| `int` (din text) | `EditText` | `Integer.parseInt(getText().toString())` |
| `double` | `EditText` | `Double.parseDouble(getText().toString())` |
| `float` | `RatingBar` | `getRating()` |
| `boolean` | `Switch` / `CheckBox` | `isChecked()` |
| `ArrayList<String>` | `EditText` | `Arrays.asList(text.split(","))` |
| `String` (alegere unică) | `RadioGroup` | iterezi copiii, `rb.isChecked()` |

---

## 21.3 Layout-uri — ce widget pui și cum îl referi

### ID-uri: cum dai și cum iei

```xml
<!-- în XML -->
<Button
    android:id="@+id/btnClear"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Clear" />
```

```java
// în cod
Button btnClear = findViewById(R.id.btnClear);
```

**Reguli:**
- `@+id/` = „creează ID-ul dacă nu există". Doar la prima apariție.
- Numele din XML devine `R.id.<nume>` exact.
- Fără `android:id` → nu poți referi view-ul din cod.
- ID-ul greșit = **eroare de compilare** (`cannot find symbol variable`).
- ID-ul corect dar view-ul în alt layout = **`null`** la runtime.

### Convenția de prefixe din repo

| Prefix | Widget | Exemplu |
|---|---|---|
| `et` | `EditText` / `TextInputEditText` | `etTitle` |
| `tv` | `TextView` | `tvDurationValue` |
| `sp` | `Spinner` | `spGenre` |
| `sb` | `SeekBar` | `sbDuration` |
| `rb` | `RatingBar` / `RadioButton` | `rbRating`, `rbGeneral` |
| `rg` | `RadioGroup` | `rgApproval` |
| `cb` | `CheckBox` | `cbOnWatchList` |
| `sw` | `Switch` | `swWatched` |
| `btn` / `bt` | `Button` | `btnMovieAction` |
| `fab` | `FloatingActionButton` | `fabInsert` |

> Nu e o regulă a limbajului, e o convenție de citire. Dar în repo există inconsecvențe (`cbonWatchList` vs `cbOnWatchList`, `btMovieAction` vs `btnMovieAction`) — respectă-le exact.

### Extragi textul din layout

```java
String text = etTitle.getText().toString();       // EditText
String text = tvSomeLabel.getText().toString();   // TextView
String genre = spGenre.getSelectedItem().toString(); // Spinner
```

### Cele mai folosite atribute

| Atribut | Valori | Efect |
|---|---|---|
| `layout_width` / `layout_height` | `match_parent`, `wrap_content`, `0dp`+weight | dimensiune |
| `layout_weight` | număr | împarte spațiul rămas |
| `layout_gravity` | `bottom\|end` etc. | poziția **elementului** în părinte |
| `gravity` | `center_vertical` etc. | poziția **conținutului** în element |
| `padding` / `margin` | `16dp` | interior / exterior |
| `textAppearance` | `?attr/textAppearanceBodyLarge` | tipografie din temă |
| `textColor` | `?attr/colorOnSurface` | culoare din temă |
| `inputType` | `textCapWords`, `numberDecimal`, `date`, `textUri` | tastatură + restricție |
| `visibility` | `visible`, `invisible`, `gone` | `GONE` nu ocupă spațiu |

---

## 21.4 `findViewById` vs `ViewBinding`

### `findViewById` (ce folosește repo-ul)

```java
setContentView(R.layout.activity_item);
etTitle = findViewById(R.id.etTitle);   // după setContentView, altfel null
```

**Avantaj:** explicit, vezi legătura `R.id` ↔ XML.
**Dezavantaj:** nu e type-safe, poate întoarce `null`, mult cod repetitiv.

### `ViewBinding` (alternativa modernă)

```java
// build.gradle.kts
buildFeatures { viewBinding = true }

// în Activity
ActivityItemBinding binding = ActivityItemBinding.inflate(getLayoutInflater());
setContentView(binding.getRoot());
binding.etTitle.setText("Dune");   // câmp generat, tip exact, niciodată null
```

**Avantaj:** type-safe, fără `findViewById`, refactor sigur.
**Dezavantaj:** mai puțin explicit pentru învățare.

> **Repo-ul are `viewBinding = true` dar nu îl folosește.** Dacă la test ți se cere să migrezi, știi ce să faci — și știi să explici de ce nu e folosit.

---

## 21.5 Listeneri — tabelul complet

| Widget | Metodă | Metode de implementat | Lambda? |
|---|---|---|---|
| `Button` | `setOnClickListener` | 1 (`onClick`) | **da** |
| `ListView` | `setOnItemClickListener` | 1 (`onItemClick`) | **da** |
| `ListView` | `setOnItemLongClickListener` | 1 (`onItemLongClick`) → `boolean` | **da** |
| `Switch`, `CheckBox`, `ToggleButton`, `RadioButton` | `setOnCheckedChangeListener` | 1 (`onCheckedChanged`) | **da** |
| `RadioGroup` | `setOnCheckedChangeListener` | 1 (`onCheckedChanged(group, checkedId)`) | **da** |
| `SeekBar` | `setOnSeekBarChangeListener` | **3** | **nu** |
| `RatingBar` | `setOnRatingBarChangeListener` | 1 | **da** |
| `EditText` | `addTextChangedListener` | 3 (`beforeTextChanged`, `onTextChanged`, `afterTextChanged`) | **nu** |
| `Toolbar` | `setOnMenuItemClickListener` | 1 → `boolean` | **da** |

**Regula:** o singură metodă abstractă = interfață funcțională = lambda permisă.

### Cele două stiluri

```java
// clasă anonimă (repo)
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});

// lambda (echivalent)
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

> **`this` într-o clasă anonimă** = clasa anonimă → ai nevoie de `MainActivity.this`. **`this` într-o lambda** = clasa exterioară → `this` e suficient.

---

## 21.6 Adaptoare — care, când, cum

### Arborele de decizie

```
Ai o listă de obiecte?
├── da
│   ├── Rândul are UN singur text?
│   │   └── ArrayAdapter  →  new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, list)
│   ├── Rândul are mai multe view-uri?
│   │   └── ai nevoie de un adapter propriu
│   │       ├── pe ListView  →  BaseAdapter cu getView() + ViewHolder + setTag
│   │       └── pe RecyclerView → RecyclerView.Adapter + ViewHolder + onCreate/onBind
│   └── ...
└── nu → nu ai nevoie de adapter
```

### `ArrayAdapter` (ce folosește repo-ul)

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
listView.setAdapter(movieAdapter);
```

- Cheamă `toString()` pe fiecare element.
- **Un singur** `TextView` per rând.
- După orice modificare a listei: `movieAdapter.notifyDataSetChanged();`

### `BaseAdapter` pentru `ListView` (două coloane)

```java
public class MovieListAdapter extends BaseAdapter {
    private static class ViewHolder {
        TextView tvTitle;
        TextView tvSubtitle;
    }

    private final List<Movie> movies;
    private final LayoutInflater inflater;

    public MovieListAdapter(Context context, List<Movie> movies) {
        this.inflater = LayoutInflater.from(context);
        this.movies = movies;
    }

    @Override public int getCount() { return movies.size(); }
    @Override public Movie getItem(int position) { return movies.get(position); }
    @Override public long getItemId(int position) { return position; }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = inflater.inflate(R.layout.movie_item, parent, false);
            holder = new ViewHolder();
            holder.tvTitle = convertView.findViewById(R.id.movieTitle);
            holder.tvSubtitle = convertView.findViewById(R.id.movieSubtitle);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }
        Movie movie = getItem(position);
        holder.tvTitle.setText(movie.getTitle());
        holder.tvSubtitle.setText(movie.getGenre());
        return convertView;
    }
}
```

> **`convertView` + `ViewHolder` + `setTag`/`getTag`** = reciclarea. Fără ele, `findViewById` la fiecare scroll.

### `RecyclerView.Adapter` (când vrei animații și flexibilitate)

```java
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) { this.movies = movies; }

    @NonNull @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position));
    }

    @Override public int getItemCount() { return movies.size(); }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {
        private final TextView movieTitle;

        public MovieViewHolder(@NonNull View itemView) {
            super(itemView);
            movieTitle = itemView.findViewById(R.id.movieTitle);
        }

        public void bind(Movie movie) {
            movieTitle.setText(movie.getTitle());
        }
    }
}
```

Plus în `MainActivity`:

```java
RecyclerView recyclerView = findViewById(R.id.recyclerView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));   // OBLIGATORIU
recyclerView.setAdapter(movieAdapter);
```

### Corespondența `BaseAdapter` ↔ `RecyclerView.Adapter`

| `BaseAdapter` | `RecyclerView.Adapter` | Când rulează |
|---|---|---|
| `getCount()` | `getItemCount()` | la nevoie |
| `getView()`, partea `if (convertView == null)` | `onCreateViewHolder()` | o dată per rând creat |
| `getView()`, partea de `setText` | `onBindViewHolder()` | la fiecare afișare |
| `ViewHolder` + `setTag`/`getTag` manual | `RecyclerView.ViewHolder` automat | — |

### Notificări

| Metodă | Când | Efect |
|---|---|---|
| `notifyDataSetChanged()` | orice modificare | reconstruiește tot (fără animații) |
| `notifyItemInserted(pos)` | ai adăugat la `pos` | animă inserarea |
| `notifyItemChanged(pos)` | ai modificat la `pos` | animă modificarea |
| `notifyItemRemoved(pos)` | ai șters de la `pos` | animă ștergerea |

> **Ordinea:** întâi modifici lista, **apoi** notifici. Altfel `IndexOutOfBoundsException`.

---

## 21.7 Intents și rezultate

### Pornire simplă (fără rezultat)

```java
Intent intent = new Intent(this, ItemActivity.class);
startActivity(intent);
```

### Pornire cu rezultat (ce folosește repo-ul)

```java
// MainActivity
private ActivityResultLauncher<Intent> launcher;

launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
        result -> {
            if (result.getResultCode() == RESULT_OK) {
                Intent data = result.getData();
                Movie movie = IntentCompat.getSerializableExtra(data, MOVIE_EXTRA, Movie.class);
                int position = data.getIntExtra(POSITION_EXTRA, -1);
                if (position == -1) movies.add(movie);
                else movies.set(position, movie);
                movieAdapter.notifyDataSetChanged();
            }
        });

// trimitere
Intent intent = new Intent(this, ItemActivity.class);
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);
launcher.launch(intent);
```

```java
// ItemActivity — trimiterea rezultatului
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

### Cheile și constantele

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
```

> **Greșeala clasică:** scrii `"movie"` într-un loc și `"Movie"` în altul → primești `null` fără eroare. De aceea constante.

### Ce trebuie să fie serializabil

```java
public class Movie implements Serializable { ... }
```

`String`, `Date`, primitivele — da. `Context`, `Drawable` — nu.

> **Obiectul primit e o COPIE**, nu aceeași referință. De aceea ediția trimite înapoi rezultat, nu modifică direct.

---

## 21.8 Ciclul de viață

```
PORNIRE:   onCreate → onStart → onResume
HOME:      onPause → onStop
REVENIRE:  onRestart → onStart → onResume
BACK:      onPause → onStop → onDestroy
ROTIRE:    onPause → onStop → onDestroy → onCreate → onStart → onResume
```

| Metodă | Ce faci |
|---|---|
| `onCreate` | `setContentView`, `findViewById`, inițializări |
| `onStart` | înregistrare listeneri de sistem |
| `onResume` | pornire animații, cameră |
| `onPause` | oprire animații, salvare rapidă |
| `onStop` | eliberare resurse |
| `onDestroy` | anulare callback-uri |

### Păstrarea stării la rotire

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

---

## 21.9 Widget-uri: citire și scriere

| Widget | Citești | Scrii | Listener |
|---|---|---|---|
| `EditText` | `getText().toString()` | `setText(String)` | `addTextChangedListener` |
| `TextView` | `getText().toString()` | `setText(CharSequence)` | — |
| `Spinner` | `getSelectedItem().toString()` | `setSelection(int)` | `setOnItemSelectedListener` |
| `SeekBar` | `getProgress()` | `setProgress(int)` | `setOnSeekBarChangeListener` |
| `RatingBar` | `getRating()` | `setRating(float)` | `setOnRatingBarChangeListener` |
| `Switch` / `CheckBox` | `isChecked()` | `setChecked(boolean)` | `setOnCheckedChangeListener` |
| `RadioGroup` | `getCheckedRadioButtonId()` sau iterezi copiii | `check(int id)` | `setOnCheckedChangeListener` |
| `Button` | — | `setText(...)`, `setEnabled(bool)` | `setOnClickListener` |
| orice `View` | — | `setVisibility(View.GONE)` | — |

### `RadioGroup` — cele două moduri de a citi

```java
// modul 1: cu checkedId (direct)
int checkedId = rgApproval.getCheckedRadioButtonId();
RadioButton rb = findViewById(checkedId);
String approval = rb.getText().toString();

// modul 2: iterând copiii (ce folosește repo-ul — merge și dacă adaugi butoane)
for (int i = 0; i < rgApproval.getChildCount(); i++) {
    RadioButton rb = (RadioButton) rgApproval.getChildAt(i);
    if (rb.isChecked()) {
        movie.setApproval(rb.getText().toString());
        break;
    }
}
```

> Modul 2 e mai robust: adaugi un buton în XML, codul îl vede fără modificări.

---

## 21.10 Erori frecvente și cauza lor

| Simptom | Cauză | Fix |
|---|---|---|
| `NullPointerException` în `initControls` | `findViewById` înainte de `setContentView` | mută apelul după |
| `NullPointerException` la `setAdapter` | `movieAdapter` neinițializat | creează adapterul înainte |
| Lista goală, fără eroare | ai uitat `setAdapter` | adaugă-l |
| Filmul nu apare după Save | ai uitat `notifyDataSetChanged()` | adaugă-l |
| `NumberFormatException` la Save | câmp numeric gol | `if (!text.isEmpty())` + `try/catch` |
| `NullPointerException` la editare | `release` e `null` | `if (existing.getRelease() != null)` |
| `ClassNotFoundException` la pornire | activitatea nu e în manifest | declară-o |
| `ActivityNotFoundException` | clasa nu există sau numele e greșit | verifică `android:name` |
| Spinner pe prima opțiune greșită | textul nu e în listă | verifică `movie_genre` |
| `Resources$NotFoundException` | numele temei greșit | verifică `themes.xml` + manifest |
| `ScrollView can host only one direct child` | doi copii | pune un `LinearLayout` |
| „Cannot resolve symbol R" | build eșuat | Build → Clean + Rebuild |

---

## 21.11 Rețete rapide pentru examen

### „Adaugă un atribut X și afișează-l în listă"

1. `Movie.java`: câmp + getter + setter + în constructor
2. `activity_item.xml`: widget cu `android:id`
3. `ItemActivity`: `findViewById` + `fillForm` + `saveMovie`
4. `movie_item.xml`: `TextView` cu id (dacă e RecyclerView) **sau** `toString()` (dacă e ListView)
5. Adapter: `findViewById` în `ViewHolder` + `setText` în `bind`

### „Schimbă un widget cu altul"

1. XML: înlocuiește tag-ul, păstrează `android:id` (sau schimbă-l și în cod)
2. Cod: schimbă tipul câmpului (`EditText` → `SeekBar`)
3. Cod: schimbă citirea (`getText()` → `getProgress()`)
4. Cod: schimbă scrierea (`setText()` → `setProgress()`)
5. Cod: schimbă listener-ul dacă e nevoie

### „Fă un adapter"

1. Creează `adapters/MovieAdapter.java`
2. `onCreateViewHolder` → inflate layout + `ViewHolder`
3. `onBindViewHolder` → `holder.bind(movie)`
4. `getItemCount` → `movies.size()`
5. În `MainActivity`: `setLayoutManager` + `setAdapter`

### „Adaugă un buton"

1. XML: `<Button android:id="@+id/btnX" ... />`
2. `findViewById`
3. `setOnClickListener`
4. În listener: ce trebuie să facă

### „Valoarea din widget să apară într-o etichetă"

1. Ia widget-ul și eticheta cu `findViewById`
2. Atașează listener-ul potrivit pe widget
3. În listener: `label.setText(...)`
4. Dacă vrei și la inițializare: apelează aceeași logică în `onCreate` sau setează în XML

---

## 21.12 Ce să spui la test când ți se cere „explică"

| Întrebare | Răspunsul scurt |
|---|---|
| De ce `Movie implements Serializable`? | ca să poată fi trimis prin `Intent.putExtra` între activități |
| De ce obiectul primit e o copie? | `Intent` serializează/deserializează |
| De ce `isWatched()` și nu `getWatched()`? | convenția JavaBeans pentru `boolean` |
| De ce `Arrays.asList()` într-un `EditText`? | un câmp text ține un singur șir; lista se separă prin virgulă |
| De ce `View.GONE` și nu `INVISIBLE`? | `GONE` nu ocupă spațiu |
| De ce `notifyDataSetChanged()`? | adapterul nu observă lista singur |
| De ce `setLayoutManager` la `RecyclerView`? | altfel nu știe cum să aranjeze rândurile |
| De ce `ViewHolder`? | cache de referințe, ca să nu cauți view-urile la fiecare scroll |
| De ce `calendar` pentru dată? | `Date` e doar un `long`, `Calendar` știe să construiască din zi/lună/an |
| De ce `Calendar.JULY` = 6? | lunile sunt indexate de la 0 |

---

## Rezumat capitol 21

- Model → formular → activitate → card → adapter. Mereu în ordinea asta.
- `findViewById` după `setContentView`. Un ID greșit = eroare de compilare; un ID lipsă = `null` la runtime.
- O metodă abstractă = lambda. Trei metode (`SeekBar`, `TextWatcher`) = clasă anonimă.
- `ArrayAdapter` pentru un text; adapter propriu pentru mai multe view-uri.
- `notifyDataSetChanged()` după orice modificare a listei.
- `Intent` cu rezultat: `registerForActivityResult` + `setResult(RESULT_OK)`.
- Rotirea distruge activitatea — salvează în `onSaveInstanceState`.

**Următorul capitol:** [22 - Codul adnotat.md](22%20-%20Codul%20adnotat.md)
