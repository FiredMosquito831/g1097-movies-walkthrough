# Capitolul 39 — Ce s-a schimbat față de versiunea veche

**Obiectiv:** să înțelegi exact ce s-a modificat între aplicația cu `ListView` din capitolul 22 și versiunea 2 cu `RecyclerView`, ce a rămas neatins și — cel mai important — ce înseamnă asta pentru ce ți se poate cere la test.

**Ce comparăm:** două instantanee ale aceleiași aplicații, la două momente diferite.

| | Versiunea veche | Versiunea 2 |
|---|---|---|
| Locație | `D:\tmp\claude\site-build\stage\src\G1098\src\main\` | `D:\tmp\claude\dma-annot\src-v2\` |
| Pachet de bază | `ro.ase.ie.g1098` | `com.example.group1098` |
| Listă | `ListView` + `ArrayAdapter<Movie>` | `RecyclerView` + `MovieAdapter` |
| Click pe rând | `setOnItemClickListener` | interfață `IMovieListener` |
| Ecrane | 2 (`MainActivity`, `ItemActivity`) | 3 (+ `PlaceCiocanul`) |
| Fișiere în comparație | 6 (3 Java + 2 XML + manifest) | 11 |

**De ce contează comparația.** La examen, cerința „înlocuiește `ListView` cu `RecyclerView`" **nu se mai dă de la zero** — codul pe care îl primești are deja migrarea făcută. Ce se dă este modificarea peste ea: alt `LayoutManager`, alt rând, alt click, notificare corectă. Iar dacă nu știi ce anume s-a schimbat față de versiunea din capitolul 22, riști să cauți în cod o structură care nu mai există (un `listView`, un `ArrayAdapter`, un `setOnItemClickListener`) și să pierzi minute prețioase.

**Cum am comparat, ca să poți reface și tu verificarea.** Am luat fișierele vechi, am înlocuit doar linia de `package` (și, la `ItemActivity`, cele două importuri `ro.ase.ie.*`), apoi am rulat un `diff` linie cu linie. Rezultatul e în 39.5: trei fișiere ies identice, restul diferă mult. Pentru cifrele din capitol am numărat liniile fiecărui fișier în parte.

> **Regula capitolului:** fiecare afirmație de aici e verificabilă în cele 11 fișiere din `src-v2` sau în cele patru din versiunea veche. Unde o afirmație vine din altă parte (comportament al framework-ului, capitolul 23), o spun explicit. Nimic nu e scris din memorie.

**Harta capitolului:**

| Secțiune | Ce acoperă | Nivel |
|---|---|---|
| 39.1 | XML-ul listei și cele trei linii din `MainActivity` | layout + legătură |
| 39.2 | adaptorul, contractul celor trei metode, reciclarea | arhitectură |
| 39.3 | lanțul de click, de la card până la `launcher` | evenimente |
| 39.4 | ecranul nou `PlaceCiocanul` și bug-ul din el | cod nou |
| 39.5 | cele trei fișiere identice și ce înseamnă 60% | inventar |
| 39.6 | ce e șchiop în codul nou, cu reparații | calitate |
| 39.7 | ce se cere la examen și unde te uiți | strategie |

---

## 39.1 Lista: `ListView` → `RecyclerView`

Aici e singura schimbare care se vede cu ochiul liber în XML. Și e mai mică decât pare: un tag, un ID și un atribut care dispare.

**Vechi** — `activity_main.xml`, versiunea cu `ListView`:

```xml
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />
```

**Nou** — `activity_main.xml`, versiunea 2:

```xml
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvMovies"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
```

Trei diferențe, fiecare cu explicația ei.

| Aspect | Vechi | Nou | De ce |
|---|---|---|---|
| Tag | `<ListView>` | `<androidx.recyclerview.widget.RecyclerView>` | `RecyclerView` nu e clasă de framework |
| ID | `@+id/listView` | `@+id/rvMovies` | `findViewById` caută alt nume; `R.id.listView` dispare |
| Conținut declarativ | `android:entries="@array/items"` | — (atributul nu există) | `RecyclerView` nu-și construiește singur adaptorul |
| Copii ai `FrameLayout` | 2 | 3 | a apărut al doilea FAB (`btnVlad`) |

### Diferența 1 — tag-ul: de ce numele întreg al clasei

`<ListView>` funcționează fără prefix pentru că e un widget din framework: `LayoutInflater` are o scurtătură care încearcă automat `android.widget.ListView`, apoi `android.webkit.ListView` etc. `RecyclerView` **nu stă în `android.widget`** — vine din biblioteca `androidx.recyclerview`, cu pachetul ei. Ca să-l poată instanția, inflater-ul are nevoie de numele complet al clasei, exact cum îl scrii în `import`.

Dacă scrii `<RecyclerView ... />`, inflate-ul nu găsește nicio clasă cu acel nume și aruncă o excepție la `setContentView`. De aici regula pe care o vezi în orice proiect AndroidX: widget-urile de bibliotecă se scriu cu numele complet în XML (`androidx.recyclerview.widget.RecyclerView`, `com.google.android.material.card.MaterialCardView`), cele de framework cu numele scurt (`ListView`, `FrameLayout`, `TextView`).

### Diferența 2 — ID-ul: nu e doar o redenumire

`@+id/listView` → `@+id/rvMovies`. Prefixul `rv` e convenția pentru `RecyclerView`, ca `tv` pentru `TextView` sau `btn` pentru `Button`. Contează pentru cititul codului, nu pentru funcționare.

Dar schimbarea are o consecință pe care compilatorul o prinde imediat: `R.id.listView` **nu mai există** în clasa `R` generată. Orice `findViewById(R.id.listView)` rămas în cod nu compilează — eroare `cannot find symbol`. E unul dintre puținele cazuri în care o schimbare de layout e semnalată de compilator, nu de crash la rulare. Folosește asta: dacă ai schimbat XML-ul și proiectul încă compilează, mai ai undeva un `R.id.listView` de curățat.

### Diferența 3 — `android:entries` dispare

`android:entries` era un atribut al lui `AbsListView`: îi dădeai un `string-array` din `strings.xml` și widget-ul își construia singur un `ArrayAdapter` intern. În versiunea veche, array-ul avea 20 de intrări:

```xml
    <string-array name="items">
        <item>Item 1</item>
        <item>Item 2</item>
        <!-- ... până la ... -->
        <item>Item 20</item>
    </string-array>
```

Un detaliu care merită subliniat, pentru că e o capcană de citire: **acele 20 de rânduri nu se vedeau niciodată pe ecran**. `MainActivity.initControls()` apela `listView.setAdapter(movieAdapter)` imediat după `setContentView`, iar `setAdapter` înlocuiește adaptorul construit din `entries`. Deci `android:entries="@array/items"` era decorativ — o rămășiță de la primul laborator, când lista afișa „Item 1…Item 20" și nu avea model.

`RecyclerView` nu are atribut echivalent. Conținutul vine **exclusiv** din adaptorul setat în cod. Asta are două consecințe practice:

- dacă uiți `setAdapter(...)`, lista e goală, fără eroare;
- dacă uiți `setLayoutManager(...)`, lista e goală, fără eroare — și fără niciun warning în Logcat (capitolul 23, exercițiul 23.10, primul indiciu).

### Ce se întâmplă în `MainActivity`

Aici se vede a doua jumătate a migrării. Vechi:

```java
    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        listView = findViewById(R.id.listView);
        listView.setAdapter(movieAdapter);
    }
```

Nou:

```java
    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        // listView = findViewById(R.id.listView);
        // listView.setAdapter(movieAdapter);
        rvMovies = findViewById(R.id.rvMovies);
        rvMovies.setLayoutManager(new LinearLayoutManager(this));
        rvMovies.setAdapter(movieAdapter);
        btnVlad = findViewById(R.id.btnVlad);
    }
```

Rând cu rând: `findViewById(R.id.listView)` devine `findViewById(R.id.rvMovies)`, `setAdapter` rămâne `setAdapter`, iar între ele apare o linie fără corespondent în versiunea veche — `setLayoutManager`.

Linia nouă are un singur rol: să spună unde și cum se așază rândurile. `new LinearLayoutManager(this)` înseamnă „o coloană verticală, un rând sub altul". Alternativele pe care le poți primi la examen:

| Cerință | Obiectul |
|---|---|
| listă verticală (implicit) | `new LinearLayoutManager(this)` |
| listă orizontală | `new LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)` |
| grilă pe două coloane | `new GridLayoutManager(this, 2)` |
| grilă cu înălțimi diferite | `new StaggeredGridLayoutManager(2, StaggeredGridLayoutManager.VERTICAL)` |

`RecyclerView` nu are nicio preferință proprie: fără `LayoutManager` nu desenează nimic. De aceea linia asta e obligatorie, nu opțională.

### Arborele, vechi și nou

```
VECHI — activity_main.xml                NOU — activity_main.xml
FrameLayout (id=main)                    FrameLayout (id=main)
│  orientation="horizontal"              │  orientation="horizontal"
│  (ignorat de FrameLayout)              │  (ignorat, tot acolo)
│                                        │
├── ListView (id=listView)               ├── RecyclerView (id=rvMovies)
│     entries=@array/items               │     (fără entries, fără layoutManager
│     adaptor: ArrayAdapter<Movie>       │      în XML — amândouă în cod)
│     rând: simple_list_item_1           │     adaptor: MovieAdapter
│                                        │     rând: movie_item.xml
│                                        │
└── FAB (id=floatingActionButton)        ├── FAB (id=floatingActionButton)
      bottom|end → ItemActivity          │     bottom|end → ItemActivity
                                         │
      (2 copii)                          └── FAB (id=btnVlad)
                                               bottom|start → PlaceCiocanul
                                         (3 copii)
```

La rulare, fiecare rând al `RecyclerView`-ului este un copac propriu, construit din `movie_item.xml`: un `MaterialCardView` care conține un `LinearLayout`, un `ImageView` și încă un `LinearLayout` cu titlu, subtitlu, rating, facts și patru chips-uri. Despre ce se umple din el și ce rămâne static — 39.2 și 39.6.

Un detaliu de preview, nu de funcționare: XML-ul nou nu are `tools:listitem="@layout/movie_item"`, deci în Android Studio `RecyclerView`-ul apare ca un dreptunghi gol. Atributul e `tools:`, deci dispare la build și nu schimbă nimic în aplicație.

---

## 39.2 Adaptorul: `ArrayAdapter` → `MovieAdapter`

Dacă 39.1 a fost schimbarea de suprafață, aici e schimbarea de fond. În versiunea veche adaptorul era **o linie**; în versiunea 2 este **un fișier întreg**, plus o interfață.

**Vechi** — câmpul și construirea:

```java
    private ArrayAdapter<Movie> movieAdapter;
    // ...
    private final List<Movie> movies = new ArrayList<>();
    // ...
    movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

**Nou** — aceleași trei locuri:

```java
    private MovieAdapter movieAdapter;
    // ...
    private final ArrayList<Movie> movies = new ArrayList<>();
    // ...
    movieAdapter = new MovieAdapter(movies, this);
```

Trei observații imediate, toate vizibile în diff:

- Tipul câmpului se schimbă din `ArrayAdapter<Movie>` în `MovieAdapter` — clasa ta, nu una din framework.
- Tipul listei se schimbă din `List<Movie>` în `ArrayList<Movie>`, pentru că **asta cere constructorul** lui `MovieAdapter` (`public MovieAdapter(ArrayList<Movie> movies, IMovieListener listener)`). Nu e o preferință de stil; dacă lași `List<Movie>`, nu compilează.
- Al doilea argument nu mai e un layout, ci `this` — activitatea însăși, în rolul de listener. Despre asta, 39.3.

Linia veche rămâne în fișier, comentată:

```java
        // movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

### De ce `ArrayAdapter` nu mai are ce căuta aici

`ArrayAdapter` e un adaptor **gata făcut**, construit pentru un singur caz: o listă de obiecte afișate ca text. El primește la construcție trei lucruri — un `Context`, un ID de layout de rând și lista de date — și știe să facă singur restul. Prețul e că știe **un singur fel de rând**.

Trei motive concrete, în ordinea în care te lovesc:

**1. Rândul are un singur `TextView`.** `android.R.layout.simple_list_item_1` este un layout care vine cu Android (de aici `android.R`, nu `R`) și conține exact un `TextView`, cu ID-ul `android.R.id.text1`. `ArrayAdapter` umple acel singur `TextView`. `movie_item.xml` nu are un `TextView` rădăcină: rădăcina e un `MaterialCardView`, iar înăuntru sunt 10 widgeturi cu ID-uri proprii. `ArrayAdapter` nu are niciun mecanism prin care să pună o valoare în `movieRating` sau în `chipWatched`.

**2. Singura valoare pe care o știe afișa e `toString()`.** `ArrayAdapter` nu te întreabă „ce câmp vrei"; ia obiectul și-i cheamă `toString()`. Iar `Movie.toString()` din proiect e dump-ul complet:

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
                ", posterUrl='" + posterUrl + '\'' +
                '}';
    }
```

Cu `simple_list_item_1` + `toString()` (perechea din tabelul de la începutul capitolului 23), rândul vechi afișa exact șirul acesta — toate cele 10 câmpuri, pe un singur rând, cu acolade cu tot. Nu era o listă de filme, era o listă de `toString()`-uri.

**3. Nu există contract de poziție.** `ArrayAdapter` expune `getView(position, convertView, parent)`, unde reciclarea se face manual, prin `convertView`. `RecyclerView` cere altă triadă de metode și alte tipuri. Nu poți „adapta" un `ArrayAdapter` la `RecyclerView` fără să-l înlocuiești complet.

### Contractul celor trei metode

`MovieAdapter` extinde `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`. Clasa de bază are trei metode abstracte; dacă nu le scrii pe toate trei, clasa nu compilează. Iată-le, cu cine le cheamă și când:

| Metodă | Cine o cheamă | Când | De câte ori | Ce trebuie să facă |
|---|---|---|---|---|
| `onCreateViewHolder(parent, viewType)` | `RecyclerView` | când are nevoie de un rând nou, adică la început și când reciclarea nu mai ajunge | o dată per rând „fizic" (cele care încap pe ecran + câteva de rezervă) | să inflateze `movie_item.xml` și să întoarcă un `MovieViewHolder` nou |
| `onBindViewHolder(holder, position)` | `RecyclerView` | înainte de fiecare afișare a unui rând | de fiecare dată când rândul apare pe ecran, **inclusiv** când același `ViewHolder` e refolosit pentru alt film | să scrie datele din `movies.get(position)` în widgeturile din `holder` |
| `getItemCount()` | `RecyclerView` | la pornire și după fiecare notificare | des | să întoarcă numărul de elemente, adică `movies.size()` |

Codul real din `MovieAdapter.java`:

```java
    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy");
        Movie movie = movies.get(position);
        holder.title.setText(movie.getTitle());
        holder.subtitle.setText(movie.getGenre().toString() + ". " + sdf.format(movie.getRelease()));

    }

    @Override
    public int getItemCount() {
        return movies.size();
    }
```

Citește-le în ordinea în care le cheamă `RecyclerView`, nu în ordinea din fișier: întâi `getItemCount()` (câte rânduri sunt), apoi `onCreateViewHolder` pentru fiecare rând de care are nevoie, apoi `onBindViewHolder` pentru fiecare rând pe care urmează să-l arate.

### Mecanismul reciclării, într-o imagine

```
RecyclerView (cu LinearLayoutManager)
│
├─ 1. „câte elemente am?"          → getItemCount()            → 3
│
├─ 2. „am nevoie de rânduri"       → onCreateViewHolder() × 4  → 4 × inflate(movie_item)
│        (câte încap pe ecran + 1-2 în rezervă)
│
├─ 3. „umple rândurile"            → onBindViewHolder(holder, 0..3)
│        holder.title    ← movies.get(0).getTitle()
│        holder.subtitle ← movies.get(0).getGenre() + anul
│
├─ 4. derulare: rândul 0 iese din ecran
│        ViewHolder-ul lui NU se aruncă — intră în piscina de reciclare
│
└─ 5. derulare: rândul 4 trebuie afișat
         → NU se cheamă onCreateViewHolder
         → se cheamă onBindViewHolder(același holder, 4)
         → aceleași widgeturi, alt conținut
```

Pasul 5 e tot sensul lui `ViewHolder`: `findViewById` se face **o singură dată**, în constructorul `ViewHolder`, nu la fiecare derulare. La o listă de 1000 de filme, versiunea cu `RecyclerView` face `findViewById` de câteva ori; un adaptor care ar căuta widgeturile în `onBindViewHolder` ar face-o de mii de ori. De aici regula: `findViewById` stă în constructorul `ViewHolder`, scrierea valorilor stă în `onBindViewHolder`.

### Tabelul comparației

| Aspect | `ArrayAdapter<Movie>` (vechi) | `MovieAdapter` (nou) |
|---|---|---|
| Cine ține rândurile | `ArrayAdapter`, cu lista primită la construcție | `MovieAdapter`, cu referința `final ArrayList<Movie> movies` |
| Cine umple rândul | `ArrayAdapter`, cu `toString()` | `onBindViewHolder`, câmp cu câmp |
| Layout-ul rândului | `android.R.layout.simple_list_item_1` (un `TextView`) | `R.layout.movie_item` (`MaterialCardView`, 10 widgeturi) |
| Reciclare | `convertView` + `if (convertView == null) inflate` | `ViewHolder` reciclat de `RecyclerView` |
| Metode obligatorii | niciuna — e gata făcut | trei: `onCreateViewHolder`, `onBindViewHolder`, `getItemCount` |
| Cine știe poziția | parametrul `position` din `getView` | parametrul `position` din `onBindViewHolder` |
| Click | pe listă, în activitate | pe rând, în adaptor (39.3) |
| Notificare | `notifyDataSetChanged()` | `notifyDataSetChanged()` sau `notifyItem*` |

### Trei detalii din cod pe care merită să le vezi

**1. Adapterul nu copiază lista.** Constructorul face `this.movies = movies;` — aceeași referință pe care o ține `MainActivity`. De aceea `movies.add(movie)` din callback se vede în listă după `notifyDataSetChanged()`: nu se sincronizează nimic, e același obiect. `getItemCount()` întoarce deja `movies.size()` actualizat; notificarea e ce-i spune lui `RecyclerView` să întrebe din nou.

**2. `MovieViewHolder` e clasă interioară ne-statică.** În capitolul 12 regula era „`ViewHolder` se face `static`". Aici e `class MovieViewHolder extends RecyclerView.ViewHolder` — fără `static`, pentru că are nevoie de `movies` și `listener` din instanța exterioară și le vede direct. Varianta `static` ar fi cerut ca amândouă să fie transmise ca parametri. Ambele sunt corecte; prima e mai scurtă, a doua mai explicită.

**3. Câmpurile adaptorului sunt package-private.** `final ArrayList<Movie> movies;` și `final IMovieListener listener;` nu au `private`. Nu e o scăpare, dar nici o decizie grozavă: clasa interioară le-ar fi văzut oricum, iar fără modificator ele devin vizibile pentru tot pachetul `com.example.group1098.adapter`. `private` ar fi fost suficient și mai sigur.

**Ce încă mai folosește vechea cale.** `MainActivity` păstrează `movieAdapter.notifyDataSetChanged()` în ambele ramuri ale callback-ului. Funcționează — `RecyclerView` are și el metoda — dar pierde animația de inserare și re-leagă toate rândurile vizibile. Varianta modernă e exercițiul 23.10 din capitolul 23.

---

## 39.3 Click-ul: `setOnItemClickListener` → interfață `IMovieListener`

Aici e diferența cea mai neintuitivă pentru cineva care vine de pe `ListView`, pentru că nu e o schimbare de API, ci o schimbare de **arhitectură**.

**Vechi** — click-ul stătea pe listă, într-o singură bucată, în `initListeners()`:

```java
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);
                intent.putExtra(MOVIE_EXTRA, movies.get(position));
                intent.putExtra(POSITION_EXTRA, position);
                launcher.launch(intent);
            }
        });
```

**Nou** — același cod există, dar comentat:

```java
        /* listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);
                intent.putExtra(MOVIE_EXTRA, movies.get(position));
                intent.putExtra(POSITION_EXTRA, position);
                launcher.launch(intent);
            }
        });*/
```

Click-ul propriu-zis s-a mutat în două locuri: în adaptor (care prinde evenimentul) și într-o metodă a activității (care face navigarea). Între ele stă o interfață de 7 linii.

### Interfața

Fișier nou, `IMovieListener.java`, integral:

```java
package com.example.group1098.adapter;

import com.example.group1098.model.Movie;

public interface IMovieListener {
    void onMovieClick(Movie movie, int position);
}
```

O singură metodă, două argumente: obiectul pe care s-a dat click și poziția lui. Atât.

### Cine implementează

`MainActivity` își schimbă declarația clasei:

```java
public class MainActivity extends AppCompatActivity implements IMovieListener {
```

și primește metoda la finalul fișierului:

```java
    @Override
    public void onMovieClick(Movie movie, int position) {
        Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }
```

Corpul e identic cu cel din listener-ul vechi, cu o singură diferență de formă: `ItemActivity.class` a devenit numele complet `com.example.group1098.activities.ItemActivity.class`. `MainActivity` nu mai are `ItemActivity` în import, deci are nevoie de numele calificat.

Iar adaptorul primește activitatea ca listener, în chiar linia de construcție:

```java
        movieAdapter = new MovieAdapter(movies, this);
```

`this` e `MainActivity`, care tocmai a promis prin `implements` că știe `onMovieClick`.

### Lanțul complet

```
 1. utilizatorul atinge cardul
          │
          ▼
 2. itemView.setOnClickListener           ← în constructorul MovieViewHolder
    (MovieAdapter.java)
          │  onClick(View v)
          ▼
 3. int pos = getAbsoluteAdapterPosition();
    if (pos != RecyclerView.NO_POSITION) {
        Movie movie = movies.get(pos);
        listener.onMovieClick(movie, pos);   ← apelul prin interfață
    }
          │
          ▼
 4. IMovieListener.onMovieClick(Movie, int)  ← contractul (fișier separat)
          │
          ▼
 5. MainActivity.onMovieClick(...)          ← implementarea
        Intent intent = new Intent(...)
        intent.putExtra(MOVIE_EXTRA, ...)
        intent.putExtra(POSITION_EXTRA, ...)
        launcher.launch(intent)
          │
          ▼
 6. ItemActivity (formularul, la fel ca înainte)
```

Codul verigii 2–3, exact cum e în fișier:

```java
            itemView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    int pos = getAbsoluteAdapterPosition();
                    if (pos != RecyclerView.NO_POSITION) {
                        Movie movie = movies.get(pos);
                        listener.onMovieClick(movie, pos);
                    }
                }
            });
```

### De ce `RecyclerView` nu are `setOnItemClickListener`

Pentru că nu are sens să aibă. Un rând de `RecyclerView` poate conține oricâte zone interactive — un card, un chip, un buton de ștergere, un poster. Un listener unic pe listă ar fi trebuit să ghicească ce anume a fost atins. Soluția aleasă de AndroidX: fiecare rând își pune singur listener-ii pe zonele lui, iar cine vrea să afle rezultatul îl primește printr-un callback pe care îl definește el.

De aici încă o consecință practică: **adapterul nu știe ce se întâmplă cu click-ul**. `MovieAdapter` nu importă `Intent`, nu importă `ItemActivity`, nu cunoaște `MainActivity`. Știe doar că există cineva care a promis `onMovieClick(Movie, int)`. Poți schimba destinația click-ului fără să atingi adaptorul.

### Tabelul celor două mecanisme

| | Vechi (`ListView`) | Nou (`RecyclerView`) |
|---|---|---|
| Unde se înregistrează | `listView.setOnItemClickListener(...)` | `itemView.setOnClickListener(...)` în `ViewHolder` |
| Cine ține listener-ul | widget-ul listei | fiecare rând, individual |
| Tipul callback-ului | `AdapterView.OnItemClickListener` (framework) | `IMovieListener` (al tău) |
| Semnătura | `onItemClick(parent, view, position, id)` | `onMovieClick(Movie, int)` |
| Ce primești | poziția și id-ul rândului | obiectul întreg și poziția |
| Cine implementează | o clasă anonimă, în activitate | activitatea însăși |
| Unde stă codul de navigare | în `initListeners()` | în `onMovieClick(...)`, metodă publică |

### Patru nuanțe care se văd în cod

**1. Poziția se calculează la click, nu la legare.** `getAbsoluteAdapterPosition()` se evaluează în momentul atingerii. Dacă ai fi capturat `position` în constructorul `ViewHolder` sau în `onBindViewHolder`, după prima reciclare ai fi deschis filmul greșit — exact capcana din capitolul 23, exercițiul 23.9.

**2. `getAbsoluteAdapterPosition()` vs `getBindingAdapterPosition()`.** Versiunea 2 folosește prima formă; capitolul 23 folosește a doua. Pentru un singur adaptor atașat la `RecyclerView`, rezultatul e identic. Diferența apare la `ConcatAdapter`: poziția absolută e în lista completă, cea „binding" e în adaptorul care a produs rândul.

**3. Listener-ul e legat în constructorul `ViewHolder`, nu în `bind`.** Ambele variante sunt corecte, atâta timp cât poziția se rezolvă la click. Aici legarea în constructor se face o singură dată per rând, nu la fiecare re-legare; în capitolul 23 legarea în `bind` e aleasă pentru lizibilitate, fiindcă `bind` primește deja `movie` și `listener`.

**4. Nu există verificare de `null` pe listener.** `MovieAdapter` presupune că a primit un listener valid. `new MovieAdapter(movies, null)` compilează, iar primul click aruncă `NullPointerException`. Varianta din capitolul 23 verifică `listener != null`; e o diferență de robustețe, nu de funcționare.

**Un detaliu de citit cu atenție:** metoda `onMovieClick(Movie movie, int position)` primește filmul, dar nu-l folosește — scrie `movies.get(position)` în `putExtra`. Funcționează, pentru că ambele vin din aceeași listă și aceeași poziție. Dar dacă adaptorul ar primi vreodată o listă filtrată sau sortată, cele două ar diverge, iar codul ar deschide alt film decât cel atins. Corect ar fi `intent.putExtra(MOVIE_EXTRA, movie);`. E genul de dedublare pe care un examen cu „explică ce face linia asta" o poate scoate la iveală.

---

## 39.4 Ecranul nou: `PlaceCiocanul`

A treia diferență de structură față de versiunea veche nu ține de listă: e un ecran care pur și simplu **nu exista**. În vechea versiune, manifestul declara două activități; în versiunea 2, trei.

### Ce este

Un ecran de test. Nu are listă, nu are formular, nu salvează nimic: are un fundal, un buton și un mesaj scurt. Numele („pune ciocanul") și textul mesajului arată că a fost scris ca verificare rapidă — un loc unde apeși și vezi imediat dacă legătura dintre al doilea buton din ecranul principal și o a doua activitate funcționează.

Fișierul întreg, 42 de linii:

```java
package com.example.group1098.activities;

import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.group1098.R;
import com.google.android.material.floatingactionbutton.FloatingActionButton;


public class PlaceCiocanul extends AppCompatActivity {

    private FloatingActionButton btn2;
    private String string;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WindowCompat.enableEdgeToEdge(getWindow());
        setContentView(R.layout.activity_place_ciocanul);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        btn2 = findViewById(R.id.floatingActionButton2);

        btn2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(PlaceCiocanul.this, "Caca", Toast.LENGTH_LONG).show();
            }
        });

        string = String.valueOf(R.string.app_name);
    }
}
```

### Ce face

Trei lucruri, în ordinea din `onCreate`:

1. **Activează edge-to-edge** și aplică padding-ul pentru barele de sistem — exact ca `MainActivity` și `ItemActivity`, doar cu altă metodă de intrare (vezi mai jos).
2. **Leagă butonul** `floatingActionButton2` de un `Toast` care afișează textul `"Caca"` timp de `Toast.LENGTH_LONG` (3,5 secunde).
3. **Atribuie un câmp** `string` cu rezultatul lui `String.valueOf(R.string.app_name)`. Câmpul nu e citit nicăieri.

Layout-ul, pe scurt: un `RelativeLayout` cu id-ul `main` (de care are nevoie listener-ul de insets), un `RecyclerView` fără id, un `FloatingActionButton` cu id-ul `floatingActionButton2` și un `ProgressBar` lat de 6dp. Ce nu merge în el — 39.6.

### Cum se ajunge la el

Două piese: un al doilea FAB în `activity_main.xml` și un listener în `MainActivity`.

Butonul, adăugat ca al treilea copil al `FrameLayout`-ului:

```xml
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/btnVlad"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:clickable="true"
        android:layout_margin="16dp"
        android:contentDescription="Ciocan"
        android:layout_gravity="bottom|start"
        app:srcCompat="@drawable/buton_ciocan"/>
```

`bottom|start` îl pune în colțul opus FAB-ului de adăugare, care are `bottom|end`. Iconița vine din `@drawable/buton_ciocan` — un fișier care nu există în versiunea veche și nici în `cod-final`; trebuie adăugat în proiect, altfel build-ul pică la resurse.

Legătura, într-o metodă separată:

```java
    private void initSecondListener() {
        btnVlad.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent2 = new Intent(MainActivity.this, com.example.group1098.activities.PlaceCiocanul.class);
                launcher.launch(intent2);
            }
        });
    }
```

Apelată în `onCreate`, imediat după `initListeners()`:

```java
        movieAdapter = new MovieAdapter(movies, this);
        initControls();
        initListeners();
        initSecondListener();
```

Ordinea contează: `btnVlad` e găsit în `initControls()`, iar `initSecondListener()` are nevoie de el. Dacă ai inversa cele două, `btnVlad` ar fi `null` și ai lua `NullPointerException` la `setOnClickListener`.

În manifest, a treia activitate:

```xml
        <activity
            android:name=".activities.PlaceCiocanul"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
```

`exported="false"` e corect: ecranul se deschide doar din aplicație, nu din exterior. `windowSoftInputMode="adjustResize"` e inutil aici — ecranul nu are niciun câmp de text — dar a fost copiat după celelalte două intrări.

### Semnalul de alarmă: `String.valueOf(R.string.app_name)`

Linia de la finalul lui `onCreate` e singurul loc din tot codul versiunii 2 care e **greșit**, nu doar neterminat.

```java
        string = String.valueOf(R.string.app_name);
```

`R.string.app_name` **nu este un text**. Este un câmp `int` generat de AAPT, care ține ID-ul numeric al resursei — ceva de forma `2131689600`. `String.valueOf` are o suprascriere pentru `int`, deci rezultatul e șirul de cifre al ID-ului, nu numele aplicației.

```java
// ce face linia
String.valueOf(R.string.app_name)   →  "2131689600"     // ID-ul, ca text

// ce ar trebui să facă
getString(R.string.app_name)        →  "G1098"          // textul resursei
```

Diferența dintre `R.string.x` și `getString(R.string.x)` e exact diferența dintre „numărul de la casa de marcat" și „produsul". `R.string.app_name` e cheia; `getString(...)` e metoda care întoarce valoarea din `strings.xml`, cu tot cu formatare dacă resursa are parametri.

Practic, bug-ul nu are efect vizibil: câmpul `string` nu e folosit nicăieri. E o linie care nu face nimic rău și nimic bun — dar e exact genul de linie pe care un test cu „ce afișează?" o poate transforma în puncte pierdute.

### O inconsecvență de stil: două API-uri pentru același lucru

`MainActivity` și `ItemActivity` pornesc edge-to-edge cu `EdgeToEdge.enable(this)` (din `androidx.activity`); `PlaceCiocanul` pornește cu `WindowCompat.enableEdgeToEdge(getWindow())` (din `androidx.core`). Ambele fac același lucru — permit desenarea sub barele de sistem. Nu e o eroare, e o inconsecvență de stil, vizibilă în `import`-uri.

### Ce se întâmplă cu rezultatul

`PlaceCiocanul` e lansat cu **același** `launcher` ca `ItemActivity`. La întoarcere se execută același callback `onActivityResult`, dar cum ecranul nu apelează niciodată `setResult`, codul întors e `RESULT_CANCELED` și ramura `if (o.getResultCode() == RESULT_OK)` nu se execută. Lista rămâne neatinsă — corect funcțional, dar ecranul de test e legat de mecanismul de rezultat al formularului fără să aibă nevoie de el.

### Locul lui în arborele aplicației

```
MainActivity (launcher)
├── FAB "add"    (floatingActionButton, bottom|end)   → ItemActivity   (duce/întoarce Movie)
└── FAB "ciocan" (btnVlad, bottom|start)              → PlaceCiocanul  (nu duce, nu întoarce)
                                                              │
                                            FAB floatingActionButton2 → Toast
                                            RecyclerView fără id      → gol
                                            ProgressBar 6dp           → decor
```

Trei ecrane, două legături, un singur flux de date real (cel către `ItemActivity`). `PlaceCiocanul` e o fundătură intenționată.

---

## 39.5 Ce a rămas identic

Aici e partea care contează cel mai mult pentru examen, și e cea care se vede cel mai puțin.

### Cele trei fișiere

| Fișier | Linii | Ce diferă față de versiunea veche |
|---|---|---|
| `Movie.java` | 130 | doar linia de `package` |
| `ItemActivity.java` | 217 | linia de `package` + cele două importuri `ro.ase.ie.*` |
| `activity_item.xml` | 451 | nimic — text identic caracter cu caracter |
| **Total** | **798** | |

Verificarea, ca să o poți reface: am înlocuit în fișierul vechi `package ro.ase.ie.g1098.model;` cu `package com.example.group1098.model;` și am comparat cu `diff`. Rezultatul: zero diferențe. La `ItemActivity`, la fel, după ce am înlocuit și `import ro.ase.ie.g1098.R;` cu `import com.example.group1098.R;` și `import ro.ase.ie.g1098.model.Movie;` cu varianta `com.example.group1098.*`.

O precizare de onestitate: fișierele vechi au terminatori de linie CRLF, cele noi au LF în unele cazuri. Diferența e invizibilă în editor și nu schimbă niciun caracter din cod. Textul propriu-zis este identic — cu excepția liniei de pachet, care e singura schimbare reală.

### Ce înseamnă cifra

```
Total linii în cele 11 fișiere din src-v2 .......... 1.350
din care manifest ..................................    33
cod + layout (baza procentelor) .................... 1.317

Identice cu versiunea veche ........................   798   (60,6% din 1.317)
Modificate sau noi .................................   519   (39,4% din 1.317)
```

Aproximativ **60% din aplicație nu a fost atinsă**. Și nu e o parte oarecare: sunt exact cele trei fișiere care definesc examenul.

| Fișier | Ce conține | Capitolele care îl acoperă |
|---|---|---|
| `Movie.java` | 10 câmpuri, constructor cu 10 parametri, constructor gol, 20 getter-e/setter-e, `toString()` | 02, 22.1, 17, 33 |
| `ItemActivity.java` | citirea celor 10 câmpuri din formular, `fillForm`, `saveMovie`, `DatePickerDialog` | 07, 09, 22.3 |
| `activity_item.xml` | 4 carduri Material: Basics, Details, Approval, Poster; toate cele 10 controale | 05, 06, 20, 22.5 |

Ce înseamnă concret: **orice cerință care atinge modelul sau formularul se rezolvă cu codul pe care îl știai deja**. Adaugi un câmp în `Movie` — aceleași trei locuri (câmp, constructor, getter/setter). Adaugi un control în formular — același `findViewById`, aceeași citire în `saveMovie`, aceeași scriere în `fillForm`. Nicio rețetă din capitolele 33–35 nu s-a schimbat din cauza `RecyclerView`-ului, atâta timp cât cerința nu atinge lista.

### Ce s-a schimbat, de fapt, în `MainActivity`

Chiar și în fișierul care s-a modificat cel mai mult, jumătate e la fel. Verificat prin comparație pe blocuri:

| Bloc | Stare |
|---|---|
| `POSITION_EXTRA`, `MOVIE_EXTRA` | identice |
| `addSampleMovies()` — cele trei filme de probă | identic, linie cu linie |
| Callback-ul lui `launcher` (`onActivityResult`) | identic |
| `fabInsert.setOnClickListener` | identic, în afară de `ItemActivity.class` scris cu numele complet |
| Câmpurile | `ListView` → `RecyclerView`, `ArrayAdapter` → `MovieAdapter`, `List` → `ArrayList`, plus `btnVlad` |
| `initControls()` | + `setLayoutManager`, + `btnVlad` |
| `initListeners()` | listener-ul de listă scos (comentat) |
| `onMovieClick(...)` | metodă nouă, corpul vechiului listener |

Deci nici `MainActivity` nu e „rescrisă": are trei modificări reale (tipurile, `initControls`, click-ul) și două adăugiri (al doilea FAB, metoda nouă).

### Ce nu mai e la fel, deși nu pare

Trei lucruri mici, care nu țin de listă:

1. **Pachetul de bază**: `ro.ase.ie.g1098` → `com.example.group1098`. Toate importurile `ro.ase.ie...R` devin `com.example.group1098.R`.
2. **Tema din manifest**: `@style/Theme.G1098` → `@style/Theme.Group1098`. Dacă numele nu există în `themes.xml`, aplicația nu pornește.
3. **Resurse noi**: `@string/chip_ciocan_name` și `@drawable/buton_ciocan` nu există în versiunea veche sau în `cod-final`. Au fost adăugate în proiectul versiunii 2; nu sunt între cele 11 fișiere, deci nu le pot verifica aici — dar XML-ul le cere, iar build-ul nu trece fără ele.

### Concluzia secțiunii

Aplicația nu a fost rescrisă. A fost **retrofitată**: s-a schimbat mecanismul de afișare a listei (4 fișiere: `activity_main.xml`, `MainActivity`, `MovieAdapter` + `IMovieListener`) și s-a adăugat un ecran de test (2 fișiere), în timp ce modelul și formularul au rămas cuvânt cu cuvânt la locul lor.

Asta e și vestea bună pentru examen: 60% din codul pe care îl știai e încă acolo, neschimbat, iar cele 40% care s-au schimbat sunt concentrate în trei mecanisme pe care le poți număra pe degete — lista, adaptorul, click-ul.

---

## 39.6 Ce mai e de făcut în cod (ce e șchiop)

Codul versiunii 2 compilează și rulează. Nu e însă curat: are rămășițe de la versiunea veche, un ecran neterminat și un rând de listă umplut pe sfert. Toate cele de mai jos sunt verificabile în fișiere.

### 1. `android:orientation` pe un container care nu-l are

`activity_main.xml`, pe `FrameLayout`:

```xml
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">
```

`FrameLayout` nu are atribut `orientation`. Atributul e **ignorat** de Android și produce cel mult un warning de lint („Unknown attribute"). Vine din versiunea veche, unde era la fel de inutil — l-am moștenit, nu l-am adăugat.

Aceeași problemă, în oglindă, în `activity_place_ciocanul.xml`, pe un `RelativeLayout`:

```xml
    tools:context=".activities.PlaceCiocanul"
    android:orientation="vertical">
```

**De ce contează.** Nu pentru că deranjează acum, ci pentru că devine funcțional exact când nu te aștepți. Dacă o cerință de examen sună „schimbă `FrameLayout` în `LinearLayout` ca să pui un titlu deasupra listei", atributul `orientation="horizontal"` începe brusc să conteze: lista și titlul se așază **unul lângă altul**, nu unul sub altul, iar FAB-ul nu mai plutește peste nimic. Rezultatul arată ca un bug scris de tine, deși linia era acolo de la început.

**Reparația:** șterge atributul din ambele fișiere. Dacă ai nevoie de `LinearLayout`, scrie `orientation` explicit, cu valoarea pe care o vrei.

### 2. `activity_place_ciocanul.xml`: un `RecyclerView` care nu va afișa nimic

```xml
    <androidx.recyclerview.widget.RecyclerView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
```

Trei probleme — două în XML, una în cod:

| Problemă | Unde | Efect |
|---|---|---|
| fără `android:id` | XML | `findViewById` nu are ce căuta; codul nu poate ajunge la el |
| `wrap_content` pe ambele axe | XML | chiar cu adapter, s-ar dimensiona după conținut, nu după ecran |
| fără `LayoutManager` și fără `setAdapter` | cod | `RecyclerView` nu știe cum să aranjeze rândurile și nu are ce aranja |

Iar în `PlaceCiocanul.java` nu există **nicio** referință la el: `initControls`-ul ecranului e o singură linie, `btn2 = findViewById(R.id.floatingActionButton2);`. Deci widget-ul e inert: ocupă un dreptunghi de 0×0 în colțul din stânga-sus și atât.

**Reparația**, dacă vrei să-l folosești: `android:id="@+id/rvCiocane"`, `layout_width="match_parent"`, `layout_height="match_parent"`, apoi în `onCreate`: `findViewById`, `setLayoutManager(new LinearLayoutManager(this))`, `setAdapter(...)`. Dacă nu, șterge-l — un widget mort într-un layout e o invitație la confuzie.

**Tot în același fișier**, două lucruri care se văd doar pe telefon, nu în editor. Butonul are `tools:layout_editor_absoluteX="334dp"` și `tools:layout_editor_absoluteY="655dp"` — atribute **de editor**, care îi spun lui Android Studio unde să-l deseneze în preview și sunt eliminate la build. Iar `ProgressBar`-ul are `android:layout_width="6dp"`. Într-un `RelativeLayout` fără nicio regulă (`layout_below`, `layout_alignParentBottom` etc.), toți copiii se așază în colțul din stânga-sus. Deci pe telefon butonul și `ProgressBar`-ul se suprapun, iar bara are 6 pixeli lățime — nu un indicator vizibil.

### 3. `movie_item.xml`: 10 widgeturi, 2 umplute

Numărul exact, din fișier: **10 widgeturi cu `android:id`** (un `ImageView`, patru `TextView`-uri, un `RatingBar`, patru `Chip`-uri), plus un `ChipGroup` care le grupează pe ultimele — 11 ID-uri în total.

`MovieViewHolder` leagă **9** dintre ele, prin `findViewById`:

```java
            poster = itemView.findViewById(R.id.moviePoster);
            title = itemView.findViewById(R.id.movieTitle);
            subtitle = itemView.findViewById(R.id.movieSubtitle);
            rating = itemView.findViewById(R.id.movieRating);
            ratingValue = itemView.findViewById(R.id.movieRatingValue);
            facts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchList = itemView.findViewById(R.id.chipWatchlist);
```

`onBindViewHolder` scrie în **două**: `title` și `subtitle`.

```java
        holder.title.setText(movie.getTitle());
        holder.subtitle.setText(movie.getGenre().toString() + ". " + sdf.format(movie.getRelease()));
```

Restul rămân cu valorile statice din XML:

| Widget | Valoarea din `movie_item.xml` | Se schimbă? |
|---|---|---|
| `movieTitle` | `"Movie title"` | da, din `movie.getTitle()` |
| `movieSubtitle` | `"Genre · Year"` | da, din gen + anul lansării |
| `moviePoster` | `@android:drawable/ic_menu_gallery` | nu — `posterUrl` nu e folosit |
| `movieRating` | `numStars=5`, `stepSize=0.5`, fără progres | nu — rămâne gol |
| `movieRatingValue` | `"4.5"` | nu |
| `movieFacts` | `"142 min  ·  $160M"` | nu |
| `chipApproval` | `"Approved"` | nu |
| `chipWatched` | `"Watched"` | nu |
| `chipWatchlist` | `"Watchlist"` | nu |
| `chipCiocan` | `@string/chip_ciocan_name` | nu — nici măcar nu e declarat în `ViewHolder` |
| `movieStatusGroup` | — (grup) | nu e referit nicăieri |

**Efectul pe ecran:** fiecare card arată titlul și subtitlul corect, dar **toate** au aceeași valoare „4.5", aceleași „142 min · $160M" și aceleași patru chips-uri — inclusiv chip-ul „ciocan", pe fiecare film. Un film de 81 de minute arată „142 min". Un film cu rating 5 arată „4.5".

Nu e un bug care crapă: e un bug care **minte**. Și e greu de observat, pentru că la primul rând arată plauzibil.

**Reparația** e exercițiul 23.7 și 23.8 din capitolul 23: în `onBindViewHolder`, scrie și `holder.rating.setRating(movie.getRating())`, `holder.ratingValue.setText(String.format("%.1f", movie.getRating()))`, compune `facts` din durată și buget, apoi setează vizibilitatea chips-urilor în funcție de `approval`, `watched` și `onWatchlist` — fără să uiți ramura `else` (`View.GONE`), altfel rândurile reciclate păstrează chip-urile filmului anterior.

### 4. `Toast`-ul din `PlaceCiocanul` are text de test

```java
                Toast.makeText(PlaceCiocanul.this, "Caca", Toast.LENGTH_LONG).show();
```

Textul nu are legătură cu aplicația. Ecranul e un test, iar mesajul a rămas de la prima rulare.

**Reparația:** un text neutru („PlaceCiocanul funcționează") sau, mai bine, `getString(R.string.app_name)` — care e și demonstrația corectă a diferenței explicate în 39.4.

### Și încă trei lucruri mai mici

**5. `notifyDataSetChanged()` în loc de `notifyItem*`.** În callback-ul lui `launcher`, ambele ramuri — `movies.add(movie)` și `movies.set(position, movie)` — sunt urmate de `movieAdapter.notifyDataSetChanged();`. Funcționează, dar re-leagă toate rândurile vizibile și pierde animația. Varianta corectă: `notifyItemInserted(movies.size() - 1)` la inserare, `notifyItemChanged(position)` la editare (capitolul 23, exercițiul 23.10).

**6. Cod mort din versiunea veche, lăsat pe loc.** În `MainActivity`:

```java
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;
// ...
import java.util.List;
```

Niciunul nu mai e folosit: `AdapterView`, `ArrayAdapter`, `ListView` și `Toast` apar doar în comentarii, iar `List` a fost înlocuit de `ArrayList`. În plus, două blocuri comentate: linia cu `new ArrayAdapter<>(...)` și tot listener-ul `setOnItemClickListener`. Java nu dă eroare pentru importuri nefolosite, doar un warning — deci codul compilează.

Costul nu e tehnic, e de citire: la examen, un `import android.widget.ListView;` într-un fișier care nu mai are `ListView` te face să cauți o structură care nu există. Șterge-le.

**7. `MainActivity.onMovieClick` ignoră parametrul `movie`.** Metoda primește filmul și apoi scrie `movies.get(position)` în extra. Funcționează cât timp poziția și obiectul vin din aceeași listă, dar e o dedublare inutilă. `intent.putExtra(MOVIE_EXTRA, movie);` e mai scurt și mai corect.

### Tabelul reparațiilor, pe scurt

| # | Unde | Reparație | Efect |
|---|---|---|---|
| 1 | ambele layout-uri | șters `android:orientation` de pe containerele care nu-l au | dispare warning-ul și capcana la schimbarea containerului |
| 2 | `activity_place_ciocanul.xml` | id + `LinearLayoutManager` + adapter, sau ștergere; reguli de poziționare pentru FAB și `ProgressBar` | ecranul chiar afișează ceva, fără suprapuneri |
| 3 | `MovieAdapter` | `onBindViewHolder` completat cu rating, facts, chips | fiecare card arată datele filmului lui |
| 4 | `PlaceCiocanul` | `Toast` cu mesaj real | ecranul nu mai arată a test neterminat |
| 5 | `MainActivity` | `notifyItemInserted` / `notifyItemChanged` | animație + muncă mai puțină |
| 6 | `MainActivity` | importuri și blocuri comentate șterse | cod mai ușor de citit la examen |
| 7 | `MainActivity.onMovieClick` | `putExtra(MOVIE_EXTRA, movie)` | o singură sursă de adevăr |

Niciuna dintre cele șapte nu blochează examenul. Toate șapte sunt exact ce ai putea primi ca cerință suplimentară.

---

## 39.7 Ce înseamnă pentru examen

Două lucruri, ambele schimbă felul în care abordezi cerința.

### 1. Cerința „schimbă `ListView` în `RecyclerView`" e deja făcută

Dacă la test primești proiectul versiunii 2 și cerința sună „înlocuiți `ListView` cu `RecyclerView`", e o capcană sau o verificare de citire: codul **este deja migrat**. Ce ți se poate cere, realist, e să **modifici** peste migrare. Iată corespondența dintre o cerință și locul exact pe care îl atingi:

| Cerința care sună așa | Ce atingi | Unde e explicat |
|---|---|---|
| „Aranjează lista pe două coloane" | `new GridLayoutManager(this, 2)` în `initControls` | 39.1 |
| „Fă lista orizontală" | `new LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)` | 39.1 |
| „Schimbă ce se vede în fiecare rând" | `movie_item.xml` + `onBindViewHolder` | 39.2, 39.6 |
| „Umple rating-ul / durata / chips-urile" | `onBindViewHolder` + ramuri `View.GONE` | 39.2, cap. 23 (23.7, 23.8) |
| „Click pe un chip, nu pe tot cardul" | `chipX.setOnClickListener` în `ViewHolder` | 39.3 |
| „Click lung pentru ștergere" | `setOnLongClickListener` + `notifyItemRemoved(position)` | 39.3 |
| „Anunță lista după salvare, cu animație" | `notifyItemInserted` / `notifyItemChanged` | 39.2, 39.6 |
| „Adaugă un câmp nou în rând" | `movie_item.xml` + câmp în `ViewHolder` + linie în `onBindViewHolder` | 39.2 |
| „Schimbă destinația click-ului" | doar `MainActivity.onMovieClick` | 39.3 |

Observă modelul: **toate** trec prin unul din fișierele atinse de migrare. Nicio cerință nouă nu te trimite în `Movie` sau în `ItemActivity`, pentru că acelea n-au legătură cu lista.

Diferența de atitudine față de capitolul 23: acolo **construiești** adaptorul de la zero, cu zece pași și puncte de verificare intermediare; aici **modifici** un adaptor care există. La examen, a doua e varianta probabilă — deci citește `MovieAdapter` până îl poți rescrie din memorie, dar nu porni de la fișier gol.

### 2. Ce rămâne la fel

Toate rețetele din capitolele 33–35 rămân valabile. Dar cu o precizare care se vede abia când le aplici: **lista de la capătul lor e acum `RecyclerView`**.

| Tip de cerință | Ce se schimbă față de rețetă | Ce rămâne identic |
|---|---|---|
| adaugă un atribut în model | nimic | cele trei locuri din `Movie`: câmp, constructor, getter/setter |
| leagă un control nou în formular | nimic | `findViewById`, citirea în `saveMovie`, scrierea în `fillForm` |
| trimite date între ecrane | nimic | `putExtra` / `setResult` / callback-ul lui `launcher` |
| salvează persistent | nimic | tot fișierul `ItemActivity` (39.5) |
| **afișează atributul nou în listă** | **da** — se adaugă în `movie_item.xml`, în `ViewHolder` și în `onBindViewHolder` | restul |
| **anunță lista după modificare** | **da** — `MovieAdapter`, nu `ArrayAdapter`; `notifyItem*` e varianta corectă | ramurile din callback |

Ultimele două rânduri sunt singurele locuri unde `RecyclerView`-ul intră în joc. Ele sunt și singurele unde se pierd puncte, pentru că acolo se întâlnesc două lucruri pe care le știai separat: modelul (capitolele 02, 17) și adaptorul (capitolele 18, 23).

**Concret, ce înseamnă „`notifyDataSetChanged()` și `MovieAdapter` intră în joc":** dacă cerința e „adaugă un câmp `country` și afișează-l în listă", lanțul complet e:

```
Movie.java          → câmp + constructor + getter/setter        (neschimbat față de rețetă)
activity_item.xml   → un EditText în plus                        (neschimbat)
ItemActivity.java   → findViewById + citire în saveMovie        (neschimbat)
movie_item.xml      → un TextView în plus                        (nou: rândul)
MovieAdapter.java   → câmp în ViewHolder + o linie în bind       (nou: adaptorul)
MainActivity.java   → nimic, dacă lista e deja notificată        (neschimbat)
```

Primele trei linii sunt rețeta pe care o știai. Ultimele două sunt noutatea. Aici se duce timpul la examen.

### Cele patru greșeli care costă puncte în versiunea 2

1. **Uiți `setLayoutManager`.** Listă goală, fără nicio eroare în Logcat. E singura greșeală din tot capitolul care nu se plânge deloc (capitolul 23, primul indiciu de la 23.10).
2. **Umpleți doar o parte din rând.** Codul versiunii 2 face exact asta: 2 câmpuri din 10. Arată plauzibil la primul rând, dar datele sunt statice (39.6, punctul 3).
3. **Chips-uri fără ramura `else`.** Rândurile reciclate păstrează statusul filmului anterior — „bug-ul de reciclare" clasic.
4. **`notifyItemInserted(movies.size())`** în loc de `movies.size() - 1`. `Inconsistency detected`, doar la inserare.

### Cum arată un răspuns complet

Dacă la test primești „schimbați lista astfel încât să afișeze și rating-ul", răspunsul are trei părți, toate în afara modelului și a formularului: widgetul în `movie_item.xml` (dacă lipsește), câmpul și `findViewById` în `ViewHolder`, linia din `onBindViewHolder` plus `notifyDataSetChanged()` dacă datele se schimbă din altă parte. Trei locuri — exact cele 40% care s-au schimbat în versiunea 2.

---

## Rezumat capitol 39

**Ce s-a schimbat, în patru rânduri:**

| Zona | Vechi | Nou | Secțiunea |
|---|---|---|---|
| Widget-ul listei | `<ListView id=listView entries=@array/items>` | `<RecyclerView id=rvMovies>`, fără `entries` | 39.1 |
| Adaptorul | `ArrayAdapter<Movie>` + `simple_list_item_1` + `toString()` | `MovieAdapter` + `movie_item.xml` + 3 metode | 39.2 |
| Click-ul | `setOnItemClickListener`, pe listă | interfață `IMovieListener`, pe fiecare rând | 39.3 |
| Ecrane | 2 | 3 (+ `PlaceCiocanul`) | 39.4 |

**Ce a rămas identic:**

| Fișier | Linii | Diferență |
|---|---|---|
| `Movie.java` | 130 | doar `package` |
| `ItemActivity.java` | 217 | `package` + 2 importuri |
| `activity_item.xml` | 451 | niciuna |

798 din 1.317 linii de cod și layout — aproximativ 60% din aplicație — nu s-a atins. Modelul și formularul se comportă exact ca în capitolele 22, 33–35.

**Cele trei mecanisme noi pe care trebuie să le poți scrie din memorie:**

```java
// 1. legarea listei — MainActivity.initControls(), copiat din sursă
rvMovies = findViewById(R.id.rvMovies);
rvMovies.setLayoutManager(new LinearLayoutManager(this));
rvMovies.setAdapter(movieAdapter);

// 2. contractul adaptorului — MovieAdapter, semnăturile prescurtate
onCreateViewHolder(parent, viewType) → inflate(R.layout.movie_item) + new MovieViewHolder(view)
onBindViewHolder(holder, position)   → holder.title.setText(...); holder.subtitle.setText(...)
getItemCount()                       → movies.size()

// 3. click-ul — MovieAdapter.MovieViewHolder, copiat din sursă
itemView.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        int pos = getAbsoluteAdapterPosition();
        if (pos != RecyclerView.NO_POSITION) {
            Movie movie = movies.get(pos);
            listener.onMovieClick(movie, pos);
        }
    }
});
```

**Ce e șchiop în codul versiunii 2** — șapte lucruri, toate reale: `orientation` pe `FrameLayout`; `RecyclerView` fără id și fără `LayoutManager` în `PlaceCiocanul`; `onBindViewHolder` care umple 2 din 10 widgeturi; `Toast` cu text de test; `notifyDataSetChanged()` în loc de `notifyItem*`; importuri și blocuri comentate rămase din versiunea veche; parametrul `movie` ignorat în `onMovieClick`.

**Trei propoziții de reținut:**

1. Migrarea nu s-a făcut de la zero, s-a făcut **peste** codul existent — și se vede: 60% din linii sunt neatinse.
2. `RecyclerView` nu are click pe listă; click-ul se pune pe rând, iar adapterul îl raportează prin interfață — lanțul e mereu același și se învață o dată.
3. La examen, cerința atinge aproape sigur unul din cele trei locuri: `setLayoutManager`, `onBindViewHolder`, sau lanțul de click. Restul e cod pe care îl știai deja.

**Pentru codul adnotat linie cu linie**, vezi capitolul 38. **Pentru migrarea pas cu pas, cu puncte de verificare intermediare**, vezi capitolul 23. Capitolul acesta a fost despre **de ce** și despre **ce înseamnă** — cele două capitole sunt despre **cum**.
