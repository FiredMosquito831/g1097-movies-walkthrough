# Capitolul 11 — Extensii: `RecyclerView`, binding, atribute noi

**Obiectiv:** să înlocuiești `ListView` + `ArrayAdapter` cu `RecyclerView` + un adapter propriu, cu `ViewHolder` și `onBindViewHolder`. Apoi să extinzi modelul cu atribute noi și să le legi în listă.

**Timp estimat:** 90–120 min.

**Sursa:** `movie_item.xml` există în repo (`d719ffc`). `MovieAdapter.java` **nu** e în repo — e lucrul tău local din 09.11, necomis. Îl reconstruiești aici ca exercițiu, ca la laboratorul următor.

---

## Partea A — De ce `RecyclerView`

### Pasul 11.1 — Problema cu `ListView`

#### De ce

`ListView` **reciclează** view-urile: creează ~10 rânduri vizibile, iar la scroll le refolosește. Dar are trei probleme:

1. **`findViewById` la fiecare rând** — `ArrayAdapter.getView()` caută view-urile de fiecare dată. E lent.
2. **Layout-uri complexe** — `simple_list_item_1` are un singur `TextView`. Pentru un card cu poster, titlu, rating, chip-uri, ai nevoie de un layout propriu.
3. **Fără animații** — adăugarea/ștergerea unui element nu e animată.

`RecyclerView` rezolvă toate trei:
1. **`ViewHolder`** — ține referințele la view-uri, găsite o singură dată.
2. **Layout propriu** — `movie_item.xml`.
3. **`ItemAnimator`** — animații gratuite.

#### Diferența fundamentală

| | `ListView` | `RecyclerView` |
|---|---|---|
| Adapter | `ArrayAdapter` (gata făcut) | `RecyclerView.Adapter` (scrii tu) |
| View-uri | `getView()` cu `convertView` | `onCreateViewHolder` + `onBindViewHolder` |
| Reciclare | manuală (`convertView`) | automată, prin `ViewHolder` |
| Layout | vertical, mereu | configurabil (`LinearLayoutManager`, `GridLayoutManager`) |
| Animații | nu | da |

---

### Pasul 11.2 — `ViewHolder`: de ce există

#### De ce

Fără `ViewHolder`, `getView()` ar face:

```java
if (convertView == null) {
    convertView = inflater.inflate(R.layout.movie_item, parent, false);
}
TextView title = convertView.findViewById(R.id.movieTitle);  // ← la FIECARE apel
```

`findViewById` parcurge arborele de view-uri. Pe un card cu 10 elemente, e 10 căutări × N rânduri × M scroll-uri.

Cu `ViewHolder`:

```java
if (convertView == null) {
    convertView = inflater.inflate(R.layout.movie_item, parent, false);
    holder = new MovieViewHolder(convertView);   // ← o singură dată
    convertView.setTag(holder);
} else {
    holder = (MovieViewHolder) convertView.getTag();
}
```

Căutarea se face **o singură dată per view reciclat**. Apoi refolosești referințele.

> **De reținut:** `ViewHolder` = cache de referințe. Nu e „un wrapper frumos” — e optimizarea principală.

---

### Pasul 11.3 — `movie_item.xml`: layout-ul unui rând

#### De ce

Cardul unui film are: poster, titlu, subtitlu (gen · an), rating (stele + valoare), fapte (durată · buget), chip-uri de stare.

#### Cum

Fișierul e în `cod-final/res/layout/movie_item.xml` (5821 B, 136 linii). Structura:

```
MaterialCardView (cornerRadius 16dp, elevation 3dp)
└── LinearLayout orizontal (padding 12dp)
    ├── ImageView moviePoster (96×140dp)
    └── LinearLayout vertical (weight 1)
        ├── TextView movieTitle (20sp, bold, maxLines 2)
        ├── TextView movieSubtitle (14sp, gri)
        ├── LinearLayout orizontal
        │   ├── RatingBar movieRating (small, isIndicator)
        │   └── TextView movieRatingValue
        ├── TextView movieFacts (13sp, gri)
        └── ChipGroup movieStatusGroup
            ├── Chip chipApproval
            ├── Chip chipWatched
            └── Chip chipWatchlist
```

#### Atributele cheie

| Element | Atribut | De ce |
|---|---|---|
| `MaterialCardView` | `app:cardCornerRadius="16dp"` | colțuri rotunjite |
| | `app:cardElevation="3dp"` | umbră (aici **da**, spre deosebire de cardurile din formular) |
| | `app:cardUseCompatPadding="true"` | padding pentru umbră pe API vechi |
| `ImageView` | `layout_width="96dp"`, `layout_height="140dp"` | raport ~2:3, ca un poster |
| | `scaleType="centerCrop"` | umple, decupează, nu deformează |
| | `src="@android:drawable/ic_menu_gallery"` | placeholder |
| `LinearLayout` info | `layout_width="0dp"` + `layout_weight="1"` | ia tot spațiul rămas |
| `TextView` titlu | `maxLines="2"`, `ellipsize="end"` | titluri lungi se trunchiază cu „…” |
| `RatingBar` | `style="?android:attr/ratingBarStyleSmall"` | variantă mică |
| | `isIndicator="true"` | **doar afișare**, nu se poate modifica |
| `ChipGroup` | `singleLine="false"` | chip-urile pot trece pe rândul următor |
| `Chip` | `clickable="false"` | nu sunt butoane |
| | `ensureMinTouchTargetSize="false"` | înălțime 28dp, nu 48dp |

#### De ce `isIndicator="true"`

Într-o listă, rating-ul e **informație**, nu input. `isIndicator` face stelele neinteractive. Fără el, utilizatorul ar putea modifica rating-ul direct în listă — și ai avea nevoie de un listener pentru a-l salva.

#### De ce `ensureMinTouchTargetSize="false"`

Material impune o zonă de atingere de minim 48dp. Un `Chip` decorativ de 28dp ar fi împins la 48dp, stricând layout-ul. Dezactivarea e corectă pentru chip-uri **neinteractive**.

---

### Pasul 11.4 — Adaugă `RecyclerView` în proiect

#### De ce

`RecyclerView` **nu** e în `appcompat` sau `material`. E o bibliotecă separată: `androidx.recyclerview:recyclerview`.

#### Cum

1. În `gradle/libs.versions.toml`:

```toml
[versions]
recyclerview = "1.4.0"

[libraries]
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

2. În `app/build.gradle.kts`:

```kotlin
dependencies {
    // ... existente ...
    implementation(libs.recyclerview)
}
```

3. **Sync Project with Gradle Files**.

#### Exercițiu 11.4

**Cerință:** ce se întâmplă dacă încerci să folosești `RecyclerView` fără să adaugi dependența?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am încercat să declar `androidx.recyclerview.widget.RecyclerView` fără dependență.

**Ce se întâmplă:** **eroare de compilare**:

```
error: package androidx.recyclerview.widget does not exist
```

**De ce:** `RecyclerView` nu e în SDK-ul Android, nici în `appcompat`. E o bibliotecă AndroidX separată.

**De reținut:**
1. `appcompat` aduce `AppCompatActivity`, `Fragment` etc.
2. `material` aduce `MaterialCardView`, `Chip`, `MaterialButton` etc.
3. `recyclerview` aduce `RecyclerView`, `LinearLayoutManager`, `ViewHolder`.
4. `constraintlayout` aduce `ConstraintLayout`.

Fiecare bibliotecă se adaugă separat.

**Unde revine:** dacă vrei să încarci imagini din URL, ai nevoie de **încă** o bibliotecă (Glide, Coil, Picasso). Nu e inclusă în niciuna de mai sus.

</details>

---

### Pasul 11.5 — Înlocuiește `ListView` cu `RecyclerView`

#### Cum

`activity_main.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".activities.MainActivity">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        tools:listitem="@layout/movie_item" />

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

#### Ce s-a schimbat

| Înainte | Acum | De ce |
|---|---|---|
| `android:orientation="horizontal"` | **șters** | era invalid pe `FrameLayout` |
| `<ListView id=listView>` | `<RecyclerView id=recyclerView>` | widget nou |
| `android:entries="@array/items"` | **șters** | `RecyclerView` nu are `entries` |
| — | `tools:listitem="@layout/movie_item"` | preview cu cardul real |

#### `tools:listitem`

E echivalentul modern al lui `android:entries`, dar **doar pentru preview**. Îi spune lui Android Studio: „desenează un rând folosind acest layout”. La runtime, nu face nimic.

> **De reținut:** `tools:*` = design-time. `android:*` = runtime. `tools:listitem` e cea mai bună soluție pentru preview-ul unui `RecyclerView`.

---

## Partea B — Adapterul

### Pasul 11.6 — Structura `MovieAdapter`

#### De ce

`RecyclerView.Adapter` are **trei** metode abstracte obligatorii:

1. `onCreateViewHolder(parent, viewType)` — creează un rând gol.
2. `onBindViewHolder(holder, position)` — umple rândul cu date.
3. `getItemCount()` — câte rânduri sunt.

Plus opțional: `ViewHolder` ca clasă interioară.

#### Cum

Creează pachetul `ro.ase.ie.g1097.adapters` și clasa `MovieAdapter`.

```java
package ro.ase.ie.g1097.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.RatingBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.chip.Chip;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(int position);
    }

    private final List<Movie> movies;
    private final OnItemClickListener listener;
    private static final SimpleDateFormat dateFormat =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    public MovieAdapter(List<Movie> movies, OnItemClickListener listener) {
        this.movies = movies;
        this.listener = listener;
    }

    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        Movie movie = movies.get(position);
        holder.bind(movie, listener);
    }

    @Override
    public int getItemCount() {
        return movies != null ? movies.size() : 0;
    }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {
        // pasul 11.7
    }
}
```

#### De ce `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`

Parametrul generic e **tipul `ViewHolder`** pe care îl folosești. Asta face `onBindViewHolder` type-safe: `holder` e `MovieViewHolder`, nu `RecyclerView.ViewHolder`.

#### De ce `interface OnItemClickListener` definită în adapter

`RecyclerView` **nu are** `setOnItemClickListener`. E o decizie de design: item-urile pot fi click-abile parțial (doar o parte din card).

Soluția: definești o interfață, o primești în constructor, o apelezi la click.

> **De reținut:** `ListView` are `setOnItemClickListener`; `RecyclerView` **nu**. Trebuie să-l implementezi manual.

#### De ce `static final SimpleDateFormat`

`SimpleDateFormat` e **scump** de creat (parsează pattern-ul). Dacă ai crea unul per rând, la 100 de rânduri ai 100 de obiecte. Static = unul singur pentru toate.

> **Atenție:** `SimpleDateFormat` **nu e thread-safe**. Aici e folosit doar în UI thread. Dacă adapterul ar fi folosit din mai multe thread-uri, ar fi un bug.

#### De ce `movies != null ? movies.size() : 0`

Defensiv. Dacă `movies` ar fi `null`, `getItemCount()` ar arunca NPE, iar `RecyclerView` ar crăpa la layout. Întoarcerea lui 0 e „listă goală”.

---

### Pasul 11.7 — `ViewHolder` cu `bind`

#### De ce

`ViewHolder` ține referințele. `bind()` mută logica de umplere din `onBindViewHolder` în `ViewHolder`, ca să fie reutilizabilă.

#### Cum

```java
public static class MovieViewHolder extends RecyclerView.ViewHolder {
    private final ImageView moviePoster;
    private final TextView movieTitle;
    private final TextView movieSubtitle;
    private final RatingBar movieRating;
    private final TextView movieRatingValue;
    private final TextView movieFacts;
    private final Chip chipApproval;
    private final Chip chipWatched;
    private final Chip chipWatchlist;

    public MovieViewHolder(@NonNull View itemView) {
        super(itemView);
        moviePoster = itemView.findViewById(R.id.moviePoster);
        movieTitle = itemView.findViewById(R.id.movieTitle);
        movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
        movieRating = itemView.findViewById(R.id.movieRating);
        movieRatingValue = itemView.findViewById(R.id.movieRatingValue);
        movieFacts = itemView.findViewById(R.id.movieFacts);
        chipApproval = itemView.findViewById(R.id.chipApproval);
        chipWatched = itemView.findViewById(R.id.chipWatched);
        chipWatchlist = itemView.findViewById(R.id.chipWatchlist);
    }

    public void bind(Movie movie, OnItemClickListener listener) {
        if (movie == null) return;

        movieTitle.setText(movie.getTitle());

        String yearStr = movie.getRelease() != null
                ? dateFormat.format(movie.getRelease()) : "";
        String genreStr = movie.getGenre() != null ? movie.getGenre() : "";
        if (!genreStr.isEmpty() && !yearStr.isEmpty()) {
            movieSubtitle.setText(genreStr + " · " + yearStr);
        } else if (!genreStr.isEmpty()) {
            movieSubtitle.setText(genreStr);
        } else {
            movieSubtitle.setText(yearStr);
        }

        movieRating.setRating(movie.getRating());
        movieRatingValue.setText(String.valueOf(movie.getRating()));

        String durationStr = movie.getDuration() + " min.";
        String budgetStr = "";
        if (movie.getBudget() >= 1_000_000) {
            budgetStr = "$" + (long) (movie.getBudget() / 1_000_000) + "M";
        } else if (movie.getBudget() > 0) {
            budgetStr = "$" + (long) movie.getBudget();
        }
        if (!budgetStr.isEmpty()) {
            movieFacts.setText(durationStr + "  ·  " + budgetStr);
        } else {
            movieFacts.setText(durationStr);
        }

        if (movie.getApproval() != null && !movie.getApproval().isEmpty()) {
            chipApproval.setText(movie.getApproval());
            chipApproval.setVisibility(View.VISIBLE);
        } else {
            chipApproval.setVisibility(View.GONE);
        }

        chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
        chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

        itemView.setOnClickListener(v -> {
            if (listener != null) {
                int pos = getBindingAdapterPosition();
                if (pos != RecyclerView.NO_POSITION) {
                    listener.onItemClick(pos);
                }
            }
        });
    }
}
```

#### De ce `static class`

Un `ViewHolder` e **instanță per rând vizibil** (~10). Dacă ar fi non-static, fiecare ar ține o referință la `MovieAdapter` — și la 100 de rânduri ai 100 de referințe inutile. `static` elimină asta.

#### De ce `findViewById` în constructor

Se execută **o singură dată per view creat**, nu la fiecare bind. Aici e optimizarea.

#### De ce `getBindingAdapterPosition()` și nu `getAdapterPosition()`

`getAdapterPosition()` e **depreciat**. `getBindingAdapterPosition()` e varianta modernă, care ține cont de `ConcatAdapter` (mai mulți adaptori într-un `RecyclerView`).

#### De ce `NO_POSITION`

În timpul unei animații de ștergere, un view poate fi încă vizibil dar fără poziție validă. `getBindingAdapterPosition()` întoarce `NO_POSITION` (-1). Dacă ai apela `listener.onItemClick(-1)`, ai avea `IndexOutOfBoundsException`.

#### De ce `itemView.setOnClickListener` în `bind` și nu în constructor

Dacă ai pune listener-ul în constructor, ar captura poziția **la creare** — care se schimbă la reciclare. Punându-l în `bind`, `getBindingAdapterPosition()` e evaluat **la click**, deci e mereu corect.

> **Aceasta e capcana clasică a `RecyclerView`:** poziția se schimbă, view-urile se reciclează. Orice referință la poziție trebuie evaluată la momentul click-ului, nu la bind.

#### Formatarea bugetului

```java
if (movie.getBudget() >= 1_000_000) {
    budgetStr = "$" + (long) (movie.getBudget() / 1_000_000) + "M";
}
```

`160000000 / 1000000 = 160.0` → `(long) 160.0 = 160` → `"$160M"`. Frumos, compact.

`1_000_000` cu underscore e doar lizibilitate — Java îl ignoră.

#### `View.GONE` vs `View.INVISIBLE`

| Valoare | Efect |
|---|---|
| `VISIBLE` | se vede, ocupă spațiu |
| `INVISIBLE` | nu se vede, **ocupă spațiu** |
| `GONE` | nu se vede, **nu ocupă spațiu** |

Pentru chip-uri, vrei `GONE`: dacă nu e „watched”, chip-ul dispare complet și celelalte se rearanjează.

---

### Pasul 11.8 — Actualizează `MainActivity`

#### Cum

```java
private RecyclerView recyclerView;
private MovieAdapter movieAdapter;

// în onCreate, înlocuiește:
// movieAdapter = new ArrayAdapter<>(...);
movieAdapter = new MovieAdapter(movies, position -> {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
});

// în initControls:
recyclerView = findViewById(R.id.recyclerView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));
recyclerView.setAdapter(movieAdapter);

// în initListeners: șterge listView.setOnItemClickListener(...)
```

#### `LayoutManager`

`RecyclerView` **nu știe** cum să aranjeze elementele. Are nevoie de un `LayoutManager`:

| Manager | Aranjare |
|---|---|
| `LinearLayoutManager(this)` | vertical (implicit) |
| `LinearLayoutManager(this, HORIZONTAL, false)` | orizontal |
| `GridLayoutManager(this, 2)` | grilă 2 coloane |
| `StaggeredGridLayoutManager(2, VERTICAL)` | grilă cu înălțimi diferite |

> **De reținut:** fără `setLayoutManager`, `RecyclerView` nu afișează nimic. Nu dă eroare — doar listă goală.

#### De ce `notifyDataSetChanged()` rămâne

`RecyclerView.Adapter` are și el `notifyDataSetChanged()`. Funcționează la fel. Dar are și variante mai fine:

| Metodă | Efect |
|---|---|
| `notifyDataSetChanged()` | reconstruiește tot |
| `notifyItemInserted(pos)` | animă inserarea |
| `notifyItemChanged(pos)` | animă modificarea |
| `notifyItemRemoved(pos)` | animă ștergerea |
| `notifyItemMoved(from, to)` | animă mutarea |

Pentru adăugare/editare, varianta fină e mai frumoasă. Dar `notifyDataSetChanged()` e corectă.

#### Exercițiu 11.8

**Cerință:** înlocuiește `notifyDataSetChanged()` cu variantele fine, în funcție de `position`.

<details>
<summary>Indiciu</summary>

În `onActivityResult`: dacă `position == -1`, e inserare la final (`movies.size() - 1`). Altfel, e modificare la `position`.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit notificarea globală cu una specifică.

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyItemInserted(movies.size() - 1);
} else {
    movies.set(position, movie);
    movieAdapter.notifyItemChanged(position);
}
```

**Ce se vede:** filmul nou **alunecă** în listă, cu o animație scurtă. Filmul editat își schimbă conținutul cu un fade.

**De ce:** `RecyclerView` are un `ItemAnimator` implicit care animă `notifyItemInserted`, `notifyItemChanged` etc. `notifyDataSetChanged()` **nu** declanșează animații, pentru că anunță „totul s-a schimbat”.

**De reținut:**
1. `movies.size() - 1` = poziția elementului abia adăugat (indexul e 0-based).
2. Ordinea: **întâi** modifici lista, **apoi** notifici. Dacă notifici înainte, `RecyclerView` citește o listă inconsistentă → `IndexOutOfBoundsException`.
3. `notifyItemChanged(position)` e după `movies.set(position, movie)`.

**Unde revine:** dacă adaugi ștergere (swipe-to-delete), folosești `notifyItemRemoved(position)`.

</details>

---

## Partea C — Extinderea modelului

### Pasul 11.9 — Adaugă un atribut nou: `country`

#### De ce

Vrei să adaugi „țara de producție” — un `String` care apare în card. Trebuie să modifici **patru** locuri, în ordine.

#### Ordinea corectă (importantă!)

1. **Modelul** (`Movie.java`) — câmp + getter/setter + constructor.
2. **Layout-ul formularului** (`activity_item.xml`) — un câmp nou.
3. **`ItemActivity`** — `findViewById`, `fillForm`, `saveMovie`.
4. **Layout-ul cardului** (`movie_item.xml`) — un `TextView` nou.
5. **`MovieAdapter`** — `findViewById` în `ViewHolder`, `setText` în `bind`.

> **Regula:** modelul întâi, UI-ul după. Dacă începi cu UI-ul, ai erori de compilare până termini modelul.

#### Cum — pasul 1: modelul

```java
private String country;

// în constructorul complet, adaugă la final:
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String country) {
    // ...
    this.country = country;
}

public String getCountry() { return country; }
public void setCountry(String country) { this.country = country; }
```

> **Atenție:** ai schimbat semnătura constructorului. Toate apelurile `new Movie(...)` cu 10 argumente **nu mai compilează**. Va trebui să actualizezi `addSampleMovies` din `MainActivity`.

**Alternativă mai sigură:** păstrezi constructorul vechi și adaugi unul nou cu 11 parametri. Dar ai două constructoare aproape identice — confuzie.

**Recomandare:** schimbi constructorul și actualizezi toate apelurile. E mai curat.

#### Cum — pasul 2: formularul

În `activity_item.xml`, în Card 1 (Basics), după Release:

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

#### Cum — pasul 3: `ItemActivity`

```java
private EditText etCountry;

// initControls:
etCountry = findViewById(R.id.etCountry);

// fillForm:
etCountry.setText(existing.getCountry());

// saveMovie:
movie.setCountry(etCountry.getText().toString());
```

#### Cum — pasul 4: cardul

În `movie_item.xml`, după `movieFacts`:

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

#### Cum — pasul 5: adapterul

```java
// în ViewHolder:
private final TextView movieCountry;

// în constructor:
movieCountry = itemView.findViewById(R.id.movieCountry);

// în bind:
movieCountry.setText(movie.getCountry() != null ? movie.getCountry() : "");
```

#### Exercițiu 11.9

**Cerință:** fă toți cei 5 pași. Rulează. Verifică: adaugi un film cu țara „USA”, apare în card.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un atribut `country` în tot lanțul.

**Ce trebuie să verifici:**
1. `addSampleMovies` — toate cele 3 apeluri `new Movie(...)` au acum un al 11-lea argument.
2. `MovieAdapter` — `movieCountry.setText(...)` nu aruncă NPE.
3. Formularul — câmpul apare în Card 1.
4. Cardul — țara apare sub „142 min · $160M”.

**De ce 5 pași:** fiecare strat are propria reprezentare a datelor:
- modelul: câmp Java
- formularul: `EditText`
- `ItemActivity`: citire/scriere
- cardul: `TextView`
- adapterul: legarea

**De reținut:**
1. **Ordinea contează.** Model → formular → activitate → card → adapter.
2. Dacă uiți un pas, ai fie date care nu se salvează, fie câmp care nu apare.
3. La test, dacă ți se cere „adaugă un atribut”, enumeră cei 5 pași.

**Unde revine:** orice atribut nou urmează exact același lanț.

</details>

---

### Pasul 11.10 — Adaugă un atribut derivat: `isRecent`

#### De ce

Un atribut **derivat** nu se salvează — se calculează. „Film recent” = lansat în ultimii 5 ani.

#### Cum

```java
// în Movie.java:
public boolean isRecent() {
    if (release == null) return false;
    Calendar fiveYearsAgo = Calendar.getInstance();
    fiveYearsAgo.add(Calendar.YEAR, -5);
    return release.after(fiveYearsAgo.getTime());
}
```

#### De ce nu e un câmp

Dacă ai salva `isRecent` ca `boolean`, ar deveni învechit: un film recent azi nu va fi recent peste 5 ani. **Derivatul se calculează din datele sursă**, nu se stochează.

> **De reținut:** `isRecent()` e o metodă, nu un getter de câmp. Nu are setter. Nu apare în constructor.

#### Cum îl afișezi

În `movie_item.xml`, adaugi un `Chip`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipRecent"
    style="@style/Widget.Material3.Chip.Assist"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Recent"
    android:clickable="false"
    app:chipMinHeight="28dp"
    app:ensureMinTouchTargetSize="false" />
```

În adapter:

```java
chipRecent.setVisibility(movie.isRecent() ? View.VISIBLE : View.GONE);
```

#### Exercițiu 11.10

**Cerință:** adaugă `isRecent` și afișează-l. Ce se întâmplă cu „Inception” (2010)? Dar cu „Dune” (2021)?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat metoda `isRecent()` și chip-ul.

**Ce se vede (în 2026):**
- „Inception” (2010) → **nu** e recent (16 ani)
- „Dune” (2021) → **nu** e recent (5 ani, la limită — depinde de lună)
- Un film din 2024 → **da**, e recent

**De ce:** `fiveYearsAgo.add(Calendar.YEAR, -5)` scade 5 ani din data curentă. `release.after(fiveYearsAgo)` e `true` dacă filmul e mai nou.

**De reținut:**
1. **Atributele derivate** se calculează, nu se stochează.
2. `Calendar.add` modifică obiectul **în loc** (nu returnează unul nou).
3. `Date.after(Date)` compară momente în timp.
4. Rezultatul depinde de **data curentă** — testul nu e determinist. Pentru teste, ai nevoie de o dată injectabilă.

**Unde revine:** orice atribut care depinde de „acum” (vârstă, zile până la lansare, „nou”) e derivat și are aceeași problemă de testare.

</details>

---

### Pasul 11.11 — Adaugă o acțiune: ștergerea unui film

#### De ce

Lista crește, dar nu poți șterge nimic. Adaugi un buton de ștergere per card.

#### Cum — pasul 1: interfața

În `MovieAdapter`:

```java
public interface OnItemClickListener {
    void onItemClick(int position);
    void onDeleteClick(int position);
}
```

Sau, mai curat, două interfețe separate. Aici extindem pe cea existentă.

#### Cum — pasul 2: cardul

În `movie_item.xml`, adaugi un `ImageButton`:

```xml
<ImageButton
    android:id="@+id/btnDelete"
    android:layout_width="40dp"
    android:layout_height="40dp"
    android:layout_gravity="top|end"
    android:background="?attr/selectableItemBackgroundBorderless"
    android:contentDescription="Delete"
    android:src="@android:drawable/ic_menu_delete" />
```

#### Cum — pasul 3: adapterul

```java
// în ViewHolder:
private final ImageButton btnDelete;

// constructor:
btnDelete = itemView.findViewById(R.id.btnDelete);

// bind:
btnDelete.setOnClickListener(v -> {
    int pos = getBindingAdapterPosition();
    if (pos != RecyclerView.NO_POSITION && listener != null) {
        listener.onDeleteClick(pos);
    }
});
```

#### Cum — pasul 4: `MainActivity`

```java
movieAdapter = new MovieAdapter(movies, new MovieAdapter.OnItemClickListener() {
    @Override
    public void onItemClick(int position) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }

    @Override
    public void onDeleteClick(int position) {
        movies.remove(position);
        movieAdapter.notifyItemRemoved(position);
    }
});
```

#### Exercițiu 11.11

**Cerință:** implementează ștergerea. Testează: șterge primul film, apoi editează al doilea. Ce se întâmplă?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat butonul de ștergere și fluxul complet.

**Ce se vede:** filmul dispare cu o animație.

**Ce se întâmplă la editare după ștergere:** **funcționează corect**, pentru că `position` e recalculat la click pe poziția **actuală** din listă.

**Dar** dacă ai fi ținut o referință la poziție (ex. într-un câmp `selectedPosition`), ai fi editat filmul greșit.

**De reținut:**
1. `movies.remove(position)` **înainte** de `notifyItemRemoved(position)`.
2. După ștergere, toate pozițiile de după se **deplasează** cu -1.
3. `getBindingAdapterPosition()` e evaluat la click → mereu corect.
4. Dacă ai vrea „undo”, ai avea nevoie de `Snackbar` cu acțiune și de păstrarea filmului șters.

**Unde revine:** pattern-ul „șterge + undo” e standard în Material Design. `Snackbar.make(view, "Deleted", LENGTH_LONG).setAction("Undo", ...)`.

</details>

---

### Pasul 11.12 — Extensie: căutare în listă

#### De ce

Cu 3 filme nu ai nevoie de căutare. Cu 50, da. Adaugi un `SearchView` sau un `EditText` care filtrează.

#### Cum — varianta simplă

În `activity_main.xml`, deasupra `RecyclerView`-ului... dar `FrameLayout` nu stivuiește vertical. Trebuie schimbat în `LinearLayout` vertical sau `CoordinatorLayout`.

**Soluția minimă:** înlocuiești `FrameLayout` cu un `LinearLayout` vertical:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <com.google.android.material.textfield.TextInputLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_margin="8dp"
        app:startIconDrawable="@android:drawable/ic_menu_search">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/etSearch"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:hint="Search movies" />
    </com.google.android.material.textfield.TextInputLayout>

    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <androidx.recyclerview.widget.RecyclerView
            android:id="@+id/recyclerView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            tools:listitem="@layout/movie_item" />

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

#### De ce `layout_weight="1"` pe `FrameLayout`

`LinearLayout` vertical cu un `TextInputLayout` (wrap_content) și un `FrameLayout` (0dp, weight 1): al doilea ia tot spațiul rămas. Deci lista umple ecranul sub căutare.

#### Cum filtrezi

```java
private final List<Movie> allMovies = new ArrayList<>();  // lista completă
private final List<Movie> movies = new ArrayList<>();     // lista filtrată

// în onCreate, după addSampleMovies:
allMovies.addAll(movies);

// în initListeners:
etSearch.addTextChangedListener(new TextWatcher() {
    @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
    @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}

    @Override
    public void afterTextChanged(Editable s) {
        String query = s.toString().toLowerCase().trim();
        movies.clear();
        if (query.isEmpty()) {
            movies.addAll(allMovies);
        } else {
            for (Movie m : allMovies) {
                if (m.getTitle() != null && m.getTitle().toLowerCase().contains(query)) {
                    movies.add(m);
                }
            }
        }
        movieAdapter.notifyDataSetChanged();
    }
});
```

#### Exercițiu 11.12

**Cerință:** implementează căutarea. Testează: scrie „in”, vezi Inception și Interstellar. Șterge, vezi toate.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am separat lista completă (`allMovies`) de lista afișată (`movies`).

**De ce două liste:** dacă filtrezi `movies` **în loc**, pierzi elementele eliminate. Trebuie o listă sursă neatinsă.

**De reținut:**
1. **Lista afișată** e o proiecție a listei sursă.
2. `movies.clear()` + `movies.addAll(...)` — nu reasignezi `movies`, pentru că adapterul ține referința.
3. `toLowerCase()` pe ambele părți — căutare case-insensitive.
4. `contains(query)` — căutare parțială.
5. `notifyDataSetChanged()` după fiecare modificare.

**Capcana:** dacă ai face `movies = filteredList;`, adapterul ar ține referința la **vechea** listă → nu s-ar actualiza nimic.

**Unde revine:** același pattern pentru sortare, filtrare după gen, după rating.

</details>

---

### Pasul 11.13 — Extensie: `DiffUtil` (nivel avansat)

#### De ce

`notifyDataSetChanged()` reconstruiește **tot**. Pentru liste mari, e lent și pierde animațiile. `DiffUtil` calculează diferențele și notifică doar ce s-a schimbat.

#### Cum

```java
public void updateMovies(List<Movie> newMovies) {
    DiffUtil.DiffResult diff = DiffUtil.calculateDiff(new DiffUtil.Callback() {
        @Override public int getOldListSize() { return movies.size(); }
        @Override public int getNewListSize() { return newMovies.size(); }

        @Override
        public boolean areItemsTheSame(int oldPos, int newPos) {
            return movies.get(oldPos).getTitle().equals(newMovies.get(newPos).getTitle());
        }

        @Override
        public boolean areContentsTheSame(int oldPos, int newPos) {
            Movie a = movies.get(oldPos);
            Movie b = newMovies.get(newPos);
            return a.getTitle().equals(b.getTitle())
                    && a.getRating() == b.getRating()
                    && a.getBudget() == b.getBudget()
                    && a.getDuration() == b.getDuration();
        }
    });
    movies.clear();
    movies.addAll(newMovies);
    diff.dispatchUpdatesTo(this);
}
```

#### De ce `areItemsTheSame` vs `areContentsTheSame`

| Metodă | Întrebarea |
|---|---|
| `areItemsTheSame` | „e același element?” (identitate) |
| `areContentsTheSame` | „arată la fel?” (conținut) |

Dacă e același element dar conținut diferit → animație de modificare.
Dacă e element diferit → animație de inserare/ștergere.

> **De reținut:** fără un `id` real, `areItemsTheSame` se bazează pe titlu — care poate fi duplicat. E o soluție de compromis. Cu un `long id`, ar fi corect.

---

### Pasul 11.14 — Exercițiu final: adaugă 3 atribute

**Cerință:** adaugă `director` (String), `language` (String) și `sequel` (boolean) în model, formular, card și adapter. Apoi afișează-le.

#### Checklist

- [ ] `Movie`: 3 câmpuri, getteri/setteri, constructor actualizat
- [ ] `activity_item.xml`: 2 `TextInputLayout` + 1 `MaterialSwitch`
- [ ] `ItemActivity`: 3 `findViewById`, 3 în `fillForm`, 3 în `saveMovie`
- [ ] `movie_item.xml`: 2 `TextView` + 1 `Chip`
- [ ] `MovieAdapter`: 3 referințe în `ViewHolder`, 3 `setText`/`setVisibility` în `bind`
- [ ] `MainActivity.addSampleMovies`: 3 argumente noi per film

#### Întrebări de test

1. De ce modelul se modifică **înainte** de UI?
2. Ce se întâmplă dacă adaugi câmpul în model dar uiți în `saveMovie`?
3. Ce se întâmplă dacă adaugi `TextView` în card dar uiți `findViewById` în `ViewHolder`?
4. De ce `isRecent` nu are setter?

<details>
<summary>Răspunsuri — explicativ</summary>

**1. De ce modelul întâi?**
Pentru că UI-ul **depinde** de model. Dacă începi cu UI-ul, codul nu compilează până nu adaugi câmpul. Ordinea model → UI = compilare la fiecare pas.

**2. Dacă adaugi câmpul dar uiți în `saveMovie`?**
Câmpul rămâne `null` (sau `false`) pentru orice film salvat. Nu e eroare — doar date lipsă. **Bug tăcut**, cel mai greu de prins.

**3. Dacă adaugi `TextView` dar uiți `findViewById`?**
`movieDirector` rămâne `null` în `ViewHolder`. La `bind`, `movieDirector.setText(...)` → **NPE la scroll**, nu la pornire. Deci bug-ul apare târziu.

**4. De ce `isRecent` nu are setter?**
Pentru că e **derivat**. Dacă ai putea să-l setezi, ai avea două surse de adevăr: `release` și `isRecent`, care pot diverge. Derivatul se calculează mereu din sursă.

</details>

---

## Rezumat capitol 11

- `RecyclerView` = `ViewHolder` (cache de referințe) + `onBindViewHolder` (umplere) + `LayoutManager`.
- `ViewHolder` trebuie `static`; `findViewById` în constructor, o singură dată.
- `getBindingAdapterPosition()` evaluat **la click**, nu la bind.
- `notifyItemInserted/Changed/Removed` = animații; `notifyDataSetChanged` = reconstruire totală.
- Atribut nou = 5 pași: model → formular → activitate → card → adapter.
- Atribut derivat = metodă, nu câmp.
- Filtrare = listă sursă + listă afișată, niciodată reasignare.

---

## Ce urmează după acest material

Ai reconstruit aplicația și ai extins-o. Direcții naturale:

| Extensie | Ce înveți |
|---|---|
| Persistență cu `Room` | bază de date, `@Entity`, `@Dao`, `LiveData` |
| Încărcare imagini cu Glide/Coil | rețea, cache, placeholder |
| `ViewModel` + `LiveData` | supraviețuire la rotire, arhitectură MVVM |
| Navigare cu `Navigation Component` | graf de navigare, `Safe Args` |
| `Fragment`-uri | ecrane reutilizabile, `FragmentManager` |
| Testare cu JUnit + Espresso | teste unitare, teste UI |

Fiecare e un capitol separat de învățat. Aplicația actuală e fundația.
