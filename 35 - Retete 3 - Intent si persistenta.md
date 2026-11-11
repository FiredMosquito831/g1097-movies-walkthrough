# Capitolul 35 — Rețete 3: Intent, persistență, ciclu de viață

**Obiectiv:** să poți rezolva, în 10–15 minute fiecare, cerințele de examen care nu țin de layout și nici de adaptoare, ci de **circulația datelor**: cum pleacă un obiect dintr-un ecran, cum se întoarce modificat, ce se întâmplă când apeși Back, ce supraviețuiește unei rotiri și ce supraviețuiește închiderii aplicației. Aici se pierd cei mai mulți puncte pentru că nimic nu crapă: datele pur și simplu nu ajung unde trebuie.

**Aplicația de referință:** G1097 (Movies), commit `d719ffc`. Două activități — `MainActivity` (lista) și `ItemActivity` (formularul) — un model serializabil (`Movie`, 10 câmpuri) și o listă ținută în memorie: `private final List<Movie> movies = new ArrayList<>();`.

**Cele trei familii de cerințe ale capitolului:**

| Familia | Rețetele | Întrebarea la care răspunde |
|---|---|---|
| Navigare și date între ecrane | 35.1 – 35.8 | „Cum ajunge filmul în celălalt ecran și cum se întoarce?" |
| Persistență | 35.9 – 35.11 | „Ce se pierde la rotire? Ce se pierde la închidere? Cum dovedesc?" |
| Ciclu de viață și debug | 35.12 – 35.13 | „În ce ordine se apelează metodele și de ce nu ajunge rezultatul?" |

**Cum e construită fiecare rețetă.** Toate au exact aceleași șapte secțiuni, în aceeași ordine: cerința cum sună la test, fișierele atinse (cu ce e obligatoriu și ce e „doar dacă"), pașii numerotați cu cod complet, explicația mecanismului, greșeala care costă puncte, verificarea pe emulator și exercițiile de exersat. Poți citi orice rețetă de sine stătător — contextul se repetă scurt acolo unde e nevoie.

**Regula de aur a capitolului:** în Android, datele nu „se văd" dintr-un ecran în altul. Fiecare trecere este o **copie serializată** pusă într-un `Bundle`, iar fiecare întoarcere este un **cod + un `Intent`** pe care ecranul apelant trebuie să le citească explicit. Nu există memorie partajată între activități, iar când procesul moare nu există nimic. Toate cele 13 rețete sunt variațiuni pe această temă.

**Starea de la care pornești** — lanțul complet, așa cum există în cod:

```text
MainActivity                          ItemActivity
------------                          ------------
fabInsert.onClick
  new Intent(MainActivity.this, ItemActivity.class)
  launcher.launch(intent)  --------->  onCreate
                                         intent fără MOVIE_EXTRA
                                         existing == null -> position = -1
                                       saveMovie()
                                         new Movie() din widget-uri
                                         setResult(RESULT_OK, intent)
                                         finish()
  callback  <-------------------------  { MOVIE_EXTRA, fără POSITION_EXTRA }
  position == -1 -> movies.add(...)

listView.onItemClick(position)
  putExtra(MOVIE_EXTRA, movies.get(position))
  putExtra(POSITION_EXTRA, position)
  launcher.launch(intent)  --------->  onCreate
                                         existing != null
                                         position = position
                                         fillForm(existing)
                                       saveMovie()
                                         setResult(RESULT_OK, intent)
                                         finish()
  callback  <-------------------------  { MOVIE_EXTRA, POSITION_EXTRA }
  position != -1 -> movies.set(position, movie)
```

**Convenții.** Textele din interfață rămân în engleză, ca în aplicație (`"Save Movie"`, `"Update Movie"`, `"Edit movie"`). Proza, comentariile din cod și explicațiile sunt în română. Numele câmpurilor și ale identificatorilor sunt exact cele din `src-G1097` — inclusiv asimetriile: câmpul se numește `cbonWatchList`, dar id-ul este `cbOnWatchList`; câmpul este `btMovieAction`, dar id-ul este `btnMovieAction`. La examen, o literă greșită într-un `findViewById` nu dă eroare de compilare, dă `null` la runtime.

---

## Rețeta 35.1 — Pornește o altă activitate

**Cerința, cum sună la test:** „Când utilizatorul atinge un rând din listă, deschide ecranul de detalii al filmului."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `AndroidManifest.xml` | verifici că `ItemActivity` e declarată cu `android:name=".activities.ItemActivity"` | da — verificare, nu modificare |
| 2 | `activities/MainActivity.java` | construiești `Intent`-ul explicit și apeși `startActivity` / `launcher.launch` în `initListeners()` | da |
| 3 | `activities/ItemActivity.java` | doar dacă adaugi un ecran nou: `onCreate` + `setContentView` | doar dacă ecranul nu există |
| 4 | `res/layout/activity_item.xml` | doar dacă adaugi un ecran nou: layout-ul lui | doar dacă ecranul nu există |

**Pașii, în ordine:**

**Pasul 1 — verifică manifestul.** O activitate care nu e declarată în `AndroidManifest.xml` nu poate fi pornită, oricât de corect ar fi `Intent`-ul. În G1097, cele două activități sunt deja acolo:

```xml
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
```

`android:exported="false"` înseamnă: doar aplicația ta poate porni `ItemActivity`. E exact ce vrei pentru un ecran intern. `android:exported="true"` este obligatoriu doar pentru activitatea cu `MAIN`/`LAUNCHER`, cea care apare în launcher.

**Pasul 2 — construiește `Intent`-ul în `MainActivity.initListeners()`.** Locul exact este listener-ul care există deja pe listă:

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        startActivity(intent);
    }
});
```

Trei lucruri contează în cele două linii:

- `MainActivity.this`, nu `this`. Suntem într-o clasă anonimă (`new AdapterView.OnItemClickListener() { ... }`), deci `this` ar însemna listener-ul, nu activitatea. `new Intent(this, ItemActivity.class)` nu compilează acolo — constructorul cere un `Context`, iar `OnItemClickListener` nu este unul. Dacă folosești lambda, `this` redevine activitatea și confuzia dispare.
- `ItemActivity.class` — al doilea parametru este clasa **țintă**, nu un string cu numele ei. Android o transformă în `ComponentName` la pornire.
- `startActivity(intent)` — fără rezultat. Ecranul nou apare deasupra, `MainActivity` rămâne vie în back stack.

**Pasul 3 — varianta din aplicație, cu rezultat.** G1097 nu folosește `startActivity` pentru `ItemActivity`, ci un `ActivityResultLauncher`, pentru că are nevoie de filmul întors:

```java
Intent intent = new Intent(MainActivity.this, ItemActivity.class);
intent.putExtra(MOVIE_EXTRA, movies.get(position));
intent.putExtra(POSITION_EXTRA, position);
launcher.launch(intent);
```

Diferența la runtime este doar cine primește răspunsul: `startActivity` îl aruncă, `launcher.launch` îl trimite callback-ului înregistrat. Pornirea în sine e identică. Rețeta 35.4 arată înregistrarea launcher-ului; aici reține doar că **același `Intent`** merge în ambele cazuri.

**Pasul 4 — dacă adaugi un ecran nou.** În `ItemActivity`, scheletul minim care se vede pe ecran este:

```java
public class ItemActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_item);
    }
}
```

Plus intrarea din manifest de la pasul 1, cu numele corect al pachetului: `.activities.ItemActivity` înseamnă `ro.ase.ie.g1097.activities.ItemActivity`.

**Ce se întâmplă la runtime, în ordine:**

```text
apasă rândul
  MainActivity.onPause
  ItemActivity.onCreate -> onStart -> onResume
  MainActivity.onStop            (rămâne în back stack, nu e distrusă)

apeși Back în ItemActivity
  ItemActivity.onPause -> onStop -> onDestroy
  MainActivity.onRestart -> onStart -> onResume
```

**De ce merge așa:** `Intent`-ul explicit nu e „un link", e o **cerere către sistem**. `startActivity` trimite cererea la `ActivityManager`, care verifică în manifest că `ItemActivity` există și că ai voie să o pornești, apoi creează o instanță nouă a clasei. Cele două activități nu se cunosc direct: nu împart câmpuri, nu împart memorie, nu împart nicio referință. `MainActivity` nu este distrusă când pleacă — rămâne în back stack, în starea `stopped`, iar la `Back` este doar repornită (`onRestart`), nu recreată. De aceea lista rămâne intactă când te întorci: obiectul `MainActivity` a existat tot timpul.

**Greșeala care costă puncte:**

1. **Uiți intrarea din manifest.** Simptom: aplicația crapă la atingerea rândului, cu `android.content.ActivityNotFoundException: Unable to find explicit activity class {ro.ase.ie.g1097/ro.ase.ie.g1097.activities.ItemActivity}; have you declared this activity in your AndroidManifest.xml?`. Cauza: ai creat clasa, dar nu ai declarat-o.
2. **Scrii `new Intent(this, ...)` într-o clasă anonimă.** Simptom: eroare de compilare, `Intent(android.content.Context, java.lang.Class<?>)` nu se aplică. Cauza: `this` este listener-ul. Soluția: `MainActivity.this`.
3. **Folosești `startActivity` unde cerința spune „returnează".** Simptom: ecranul se deschide, salvezi, te întorci și lista nu se schimbă — fără nicio eroare. Cauza: `startActivity` nu are callback; rezultatul se pierde. Trebuie `launcher.launch` (35.4).

**Verificarea:** rulezi aplicația, apeși pe „Inception" în listă. Trebuie să apară ecranul cu formularul, iar în bara de sus să scrie „Edit movie". Apeși Back: revii la listă, cele trei rânduri sunt tot acolo, în aceeași ordine. Apoi apeși FAB-ul „+": același ecran, dar cu „Movie details" în bara de sus și formularul gol — dovada că ecranul e același, doar extra-urile diferă.

**Exersează:** [20.7](cap-20.html#ex-20-7) (buton „Edit" în card, în locul atingerii rândului), [23.9](cap-23.html#ex-23-9) (click pe rând cu poziția și callback, în varianta `RecyclerView`).

---

## Rețeta 35.2 — Trimite valori simple prin Intent

**Cerința, cum sună la test:** „Trimite titlul filmului atins către ecranul de detalii și afișează-l în bara de titlu."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | adaugi constanta cheii și `putExtra` în `initListeners()` | da |
| 2 | `activities/ItemActivity.java` | citești valoarea în `onCreate()` și o afișezi | da |
| 3 | `res/values/strings.xml` | doar dacă vrei textul într-un string resource | nu |

**Pașii, în ordine:**

**Pasul 1 — pune cheia într-o constantă, în `MainActivity`.** Lângă cele două care există deja:

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
protected static final String TITLE_EXTRA = "title";
```

`protected static final` nu e decor: `ItemActivity` este în același pachet (`ro.ase.ie.g1097.activities`), deci vede constanta fără import și fără să o mai declare încă o dată. O singură sursă pentru un string care trebuie să fie identic în două fișiere.

**Pasul 2 — pune valoarea în `Intent`, în `MainActivity.initListeners()`:**

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, movies.get(position).getTitle());
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }
});
```

Un `Intent` poate duce oricâte extra-uri; nu se suprascriu între ele atâta timp cât cheile diferă. Ordinea în care le pui nu contează.

**Pasul 3 — citește valoarea în `ItemActivity.onCreate()`, după `initControls()`:**

```java
Intent intent = getIntent();
String title = intent.getStringExtra(MainActivity.TITLE_EXTRA);
if (title != null) {
    setTitle(title);
}
```

`getIntent()` întoarce `Intent`-ul cu care a fost pornită activitatea. El rămâne valabil toată viața activității, inclusiv după rotire — de aceea nu trebuie salvat în `Bundle`.

**Pasul 4 — tabelul metodelor, după tip.** Perechile sunt fixe; nu există conversie automată între tipuri:

| Ce trimiți | Ce scrii în expeditor | Ce citești în destinatar | Valoare dacă lipsește |
|---|---|---|---|
| `String` | `putExtra(KEY, "Inception")` | `getStringExtra(KEY)` | `null` |
| `int` | `putExtra(KEY, 148)` | `getIntExtra(KEY, -1)` | default-ul dat de tine |
| `long` | `putExtra(KEY, 160000000L)` | `getLongExtra(KEY, 0L)` | default-ul dat de tine |
| `float` | `putExtra(KEY, 4.5f)` | `getFloatExtra(KEY, 0f)` | default-ul dat de tine |
| `boolean` | `putExtra(KEY, true)` | `getBooleanExtra(KEY, false)` | default-ul dat de tine |
| orice obiect | `putExtra(KEY, movie)` | `IntentCompat.getSerializableExtra(...)` | `null` (35.3) |

Observă asimetria: `getStringExtra` nu are parametru de default, pentru că `null` este un răspuns valid pentru un string. Restul au obligatoriu un default, pentru că primitivele nu pot fi `null`.

**Pasul 5 — verifică existența cheii, dacă default-ul nu e suficient:**

```java
if (intent.hasExtra(MainActivity.TITLE_EXTRA)) {
    setTitle(intent.getStringExtra(MainActivity.TITLE_EXTRA));
}
```

`hasExtra` întoarce `true` și dacă valoarea pusă este `null`, deci nu înlocuiește verificarea `!= null`; o completează atunci când vrei să distingi „cheia lipsește" de „cheia există cu valoare goală".

**De ce merge așa:** un `Intent` este, la bază, un `Bundle` — o mapă `String -> valoare` care știe să se serializeze. Când apeși `launcher.launch`, sistemul copiază bundle-ul, îl pasează în alt proces sau în același proces, și îl reconstruiește înainte de `ItemActivity.onCreate`. De aceea cheia trebuie să fie **identică** la ambele capete: nu există verificare la compilare între `putExtra("title", ...)` și `getStringExtra("Title")`, iar rezultatul este `null`, nu o excepție. Constanta elimină exact această clasă de bug-uri. Default-ul din `getIntExtra` este mecanismul prin care codul din aplicație distinge cele două moduri: `position` lipsește la insert, deci devine `-1`, iar `-1` este exact convenția „mod insert" din `ItemActivity`.

**Greșeala care costă puncte:**

1. **Cheie scrisă diferit la cele două capete.** Simptom: `title` este `null`, `setTitle` nu se apelează, bara de sus rămâne „G1097" — fără nicio eroare în Logcat. Cauza: `"Title"` într-un fișier, `"title"` în celălalt. Soluția: constanta din pasul 1.
2. **Citești cu metoda altui tip.** Simptom: `getIntExtra` pe un extra `String` întoarce `0` și în Logcat apare un `W/Bundle: Key ... expected Integer but value was a java.lang.String`; invers, `getStringExtra` pe un `int` întoarce `null`. Nu crapă, doar nu funcționează. Cauza: ai schimbat tipul într-o parte și ai uitat cealaltă parte.
3. **Uiți default-ul potrivit.** Simptom: poziția citită este `0` în loc de `-1`, iar salvarea face `set(0, movie)` în loc de `add(movie)` — primul film este înlocuit. Cauza: `getIntExtra(POSITION_EXTRA, 0)` în loc de `-1`.

**Verificarea:** apeși pe „Inception" — bara de sus arată „Inception"; apeși Back, apoi pe „Toy Story" — bara arată „Toy Story". Apeși FAB-ul „+": bara rămâne „Movie details", pentru că `TITLE_EXTRA` lipsește și `title` este `null`. Dacă vezi „null" scris în bară, ai pus valoarea în `Intent` fără să verifici `!= null`.

**Exersează:** [17.1](cap-17.html#ex-17-1) (atributul `String` care trebuie să ajungă din formular în listă), [19.5](cap-19.html#ex-19-5) (o valoare calculată într-un ecran și afișată imediat după Save).

---

## Rețeta 35.3 — Trimite un obiect întreg (Serializable)

**Cerința, cum sună la test:** „Trimite filmul atins, întreg, ca să se umple formularul de editare cu valorile lui."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `model/Movie.java` | verifici `implements Serializable` și că toate cele 10 câmpuri sunt serializabile | da — verificare |
| 2 | `activities/MainActivity.java` | `putExtra(MOVIE_EXTRA, movies.get(position))` + `putExtra(POSITION_EXTRA, position)` | da |
| 3 | `activities/ItemActivity.java` | `IntentCompat.getSerializableExtra(...)` + garda `!= null` | da |
| 4 | `activities/MainActivity.java` | `import androidx.core.content.IntentCompat;` | da, dacă folosești varianta modernă |

**Pașii, în ordine:**

**Pasul 1 — verifică modelul.** Clasa trebuie să implementeze `Serializable` și să aibă constructor fără parametri:

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;
import java.util.Date;

public class Movie implements Serializable {
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

    public Movie() {
    }

    public Movie(String title, Date release, String genre, double budget, int duration,
                 float rating, boolean watched, String approval, boolean onWatchlist, String poster) {
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

    // getteri și setteri
}
```

Toate cele 10 tipuri sunt serializabile: `String` și primitivele sunt prin definiție, iar `java.util.Date` implementează `Serializable`. Constructorul fără parametri este necesar pentru codul care reconstruiește obiectul (și pentru `moviesFromJson` din 35.10).

**Pasul 2 — pune obiectul în `Intent`, în `MainActivity.initListeners()`:**

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

`putExtra(String, Serializable)` este supraîncărcarea care se alege automat pentru un `Movie`. Nu trebuie să faci nimic special: dacă obiectul implementează `Serializable`, compilează.

**Pasul 3 — citește obiectul în `ItemActivity.onCreate()`:**

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

`IntentCompat.getSerializableExtra(Intent, String, Class<T>)` este varianta tipată din `androidx.core`. Ea întoarce direct `Movie`, fără cast, și funcționează identic pe toate versiunile de Android. Varianta veche, `(Movie) intent.getSerializableExtra(MOVIE_EXTRA)`, încă merge, dar este marcată depreciată din API 33 — iar în `MainActivity` exact așa apare în callback:

```java
Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
```

Diferența dintre cele două fișiere nu e un bug, e o inconsecvență a codului original. La examen scrie varianta cu `IntentCompat` în ambele locuri și spune de ce.

**Pasul 4 — importă ce trebuie.** În `ItemActivity` există deja:

```java
import androidx.core.content.IntentCompat;
```

Dacă folosești varianta modernă și în `MainActivity`, adaugă același import acolo.

**Pasul 5 — înțelege ce călătorește.** Nu referința, ci o **copie**:

```text
MainActivity                          Intent / Bundle                ItemActivity
------------                          ---------------                ------------
movies: List<Movie>
  [0] Movie@A  ---------------------+
  [1] Movie@B                       |
  [2] Movie@C                       |
                                    |  putExtra("movie", Movie@A)
                                    v
                          serialize(Movie@A) -> bytes
                                    |
                                    v
                          Bundle { "movie" -> bytes,
                                   "position" -> 0 }
                                    |
                                    v
                          deserialize(bytes) -> Movie@A'
                                    |
                                    v
                                                       existing = Movie@A'
                                                       (obiect NOU, adresă nouă)
```

**De ce merge așa:** `Intent`-ul nu poate ține referințe către obiecte din heap-ul unei activități, pentru că poate traversa granița dintre procese. De aceea `putExtra` serializează obiectul în bytes, iar `getSerializableExtra` îl deserializează într-un obiect nou. `Serializable` este mecanismul Java clasic: reflexie peste câmpuri, scriere recursivă a fiecăruia. Costul este real — pentru un `Movie` cu 10 câmpuri e neglijabil, pentru o listă de mii de obiecte ar fi o problemă. Consecința cea mai importantă nu e performanța, ci **identitatea**: `Movie@A` și `Movie@A'` sunt două obiecte diferite. Modificarea formularului nu se vede în listă până când nu trimiți rezultatul înapoi și faci `movies.set(...)`.

**Greșeala care costă puncte:**

1. **Uiți `implements Serializable`.** Simptom: la `putExtra`, aplicația crapă cu `java.lang.RuntimeException: Parcelable encountered IOException writing serializable object` și, în cauză, `java.io.NotSerializableException: ro.ase.ie.g1097.model.Movie`. Cauza: clasa nu implementează interfața. Nu există verificare la compilare — `putExtra(String, Serializable)` cere doar tipul, iar eroarea apare la runtime.
2. **Adaugi în `Movie` un câmp care nu e serializabil.** Simptom: același crash, dar numai după ce completezi acel câmp. Cauza: ai pus un `Context`, un `Drawable`, un `Bitmap` sau un listener în model. Regula: modelul ține **date**, nu resurse și nu referințe către UI.
3. **Crezi că modifici obiectul din listă.** Simptom: schimbi titlul în formular, apeși Back fără Save, iar lista arată tot titlul vechi — și e corect. Cauza: ai uitat că `existing` este o copie. Dacă vrei să se schimbe, trebuie `setResult` + `movies.set(...)` (35.5).

**Verificarea:** apeși pe „Inception" — formularul se deschide plin: titlu, dată, gen „Sci-Fi", buget, durată, rating, „PG-13", poster. Modifici titlul în „Inception 2" și apeși Back fără Save: lista arată tot „Inception". Asta dovedește două lucruri deodată — copia a funcționat, iar editarea nu e „live". Apoi repeți și apeși „Update Movie": lista arată „Inception 2".

**Exersează:** [24.2](cap-24.html#ex-24-2) (de ce `set` și nu `add`), [19.9](cap-19.html#ex-19-9) (lista nu are voie să arate date vechi după editare).

---

## Rețeta 35.4 — Primește un rezultat (ActivityResultLauncher)

**Cerința, cum sună la test:** „Ecranul de detalii trebuie să întoarcă filmul în listă, iar lista să se actualizeze imediat."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | câmpul `ActivityResultLauncher<Intent>` + `registerForActivityResult` în `onCreate()` | da |
| 2 | `activities/MainActivity.java` | `launcher.launch(intent)` în loc de `startActivity` | da |
| 3 | `activities/MainActivity.java` | importurile `androidx.activity.result.*` | da |
| 4 | `activities/ItemActivity.java` | `setResult(RESULT_OK, intent)` înainte de `finish()` | da, altfel nu vine nimic |

**Pașii, în ordine:**

**Pasul 1 — declară câmpul.** Nu o variabilă locală, nu un câmp al listener-ului: un câmp al activității, lângă celelalte view-uri:

```java
private FloatingActionButton fabInsert;
private ListView listView;
private ActivityResultLauncher<Intent> launcher;
private final List<Movie> movies = new ArrayList<>();
private ArrayAdapter<Movie> movieAdapter;
```

Tipul este `ActivityResultLauncher<Intent>`: un launcher care primește un `Intent` la lansare. Există și `ActivityResultLauncher<Void>` pentru contracte care nu au nevoie de input.

**Pasul 2 — înregistrează launcher-ul în `onCreate()`.** Locul exact în codul original este **după** `initControls()` și `initListeners()`:

```java
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
initControls();
initListeners();

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

Ordinea cu `initListeners()` nu este întâmplătoare, dar nici periculoasă: listener-ul FAB-ului este doar **creat** acolo, nu executat. `launcher` este citit abia când utilizatorul apasă butonul, iar până atunci `onCreate` s-a terminat și câmpul este atribuit. Periculos ar fi fost dacă `initListeners()` ar fi apelat direct `launcher.launch(...)` — ar fi dat `NullPointerException`.

**Pasul 3 — lansează prin launcher, nu prin `startActivity`.** Ambele locuri din `initListeners()`:

```java
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
```

**Pasul 4 — importurile.** Fără ele nu compilează:

```java
import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
```

**Pasul 5 — înțelege ce primești în callback.** `ActivityResult` are exact două lucruri:

```java
o.getResultCode()   // int: RESULT_OK (-1), RESULT_CANCELED (0) sau un cod propriu
o.getData()         // Intent: extra-urile puse de celălalt ecran, sau null
```

`getData()` poate fi `null` — de exemplu când utilizatorul apasă Back, caz în care nici nu intri pe ramura `RESULT_OK`. Dar poate fi `null` și când cineva apelează `setResult(RESULT_OK)` fără `Intent`. Codul original nu verifică, pentru că `ItemActivity` pune mereu un `Intent`; dacă adaugi tu ramuri noi, verifică (35.6).

**De ce merge așa:** `registerForActivityResult` nu înregistrează un „request code", ci o **intrare într-un registry ținut de `ComponentActivity`**. Registry-ul este legat de ciclul de viață: când activitatea ajunge în `STARTED`, sistemul îi livrează rezultatele care au sosit cât timp era oprită. De aceea înregistrarea trebuie făcută **înainte ca `onCreate` să se termine** — după aceea activitatea a trecut deja de starea necesară și registry-ul nu mai acceptă intrări. Când `ItemActivity` cheamă `setResult` și `finish()`, `ActivityManager` reține codul și `Intent`-ul, iar când `MainActivity` revine în prim-plan, registry-ul găsește intrarea potrivită și cheamă callback-ul. Nu există „așteptare" în `MainActivity`: între `launch` și callback, `MainActivity` este oprită, nu blocată.

**Greșeala care costă puncte:**

1. **Înregistrezi launcher-ul în listener.** Simptom: la primul click pe FAB, crash cu `java.lang.IllegalStateException: LifecycleOwner ro.ase.ie.g1097.activities.MainActivity@... is attempting to register while current state is RESUMED. LifecycleOwners must call register before they are STARTED.` Cauza: `registerForActivityResult` trebuie apelat în `onCreate` (sau într-un field initializer), nu la momentul click-ului.
2. **Declari câmpul, dar uiți să-l atribui.** Simptom: `NullPointerException` pe `launcher.launch(intent)`. Cauza: ai declarat `private ActivityResultLauncher<Intent> launcher;` și ai sărit peste linia cu `registerForActivityResult`.
3. **Amesteci `startActivity` cu `launcher.launch`.** Simptom: un drum funcționează (editarea), celălalt nu (FAB-ul), deși codul arată aproape la fel. Cauza: unul dintre cele două locuri încă folosește `startActivity`, deci rezultatul nu are unde să ajungă.

**Verificarea:** pune un `Log.d("G1097", "callback code=" + o.getResultCode())` în prima linie a callback-ului. Apeși FAB → completezi titlul → „Save Movie" → în Logcat apare `callback code=-1`. Apeși FAB → Back fără Save → nu apare nimic, pentru că `RESULT_CANCELED` nu intră pe ramură. Dacă nu apare nici la Save, verificați pasul 1 și pasul 3.

**Exersează:** [20.3](cap-20.html#ex-20-3) (același launcher, folosit pentru un cod de rezultat propriu), [24.1](cap-24.html#ex-24-1) (ce se întâmplă dacă uiți `notifyDataSetChanged()` după callback).

---

## Rețeta 35.5 — Returnează un obiect modificat

**Cerința, cum sună la test:** „La apăsarea butonului de salvare, filmul modificat înlocuiește rândul din listă, fără să apară un duplicat."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `saveMovie()`: construiești `Movie`, pui extra-urile, `setResult`, `finish()` | da |
| 2 | `activities/MainActivity.java` | în callback: `movies.set(position, movie)` + `notifyDataSetChanged()` | da |
| 3 | `activities/ItemActivity.java` | `position` citit din `POSITION_EXTRA` în `onCreate()` | da — altfel nu știi ce înlocuiești |

**Pașii, în ordine:**

**Pasul 1 — construiește obiectul din widget-uri, în `ItemActivity.saveMovie()`:**

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
    // pasul 2
}
```

Două detalii care se uită: `movie.setRelease(releaseCal.getTime())` — data vine din `Calendar`, **nu** din textul din `etRelease`; și `setApproval` se citește dintr-o buclă pe `RadioGroup`, pentru că `RadioGroup` nu are `getText()`, are copii.

**Pasul 2 — pune obiectul și poziția în `Intent`-ul de rezultat:**

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1) {
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
}
setResult(RESULT_OK, intent);
finish();
```

`new Intent()` fără parametri — nu e un `Intent` care pornește ceva, e doar un transport pentru extra-uri. Condiția `if (position != -1)` este exact ce distinge insertul de editare: la insert nu ai ce poziție să trimiți, iar lipsa cheii face ca `getIntExtra(POSITION_EXTRA, -1)` din callback să întoarcă `-1`, adică tot insert.

**Pasul 3 — citește poziția la deschidere, în `ItemActivity.onCreate()`:**

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

Câmpul este declarat cu valoarea de insert, ca să nu depinzi de nicio ramură:

```java
private int position = -1;   // -1 = insert mode
```

**Pasul 4 — în callback-ul din `MainActivity`, înlocuiește, nu adăuga:**

```java
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
```

`List.set(int index, E element)` înlocuiește elementul de pe poziția dată și întoarce elementul vechi. Nu schimbă dimensiunea listei. `List.add(E element)` adaugă la final și crește dimensiunea. Sunt două operații diferite, iar confuzia dintre ele este cel mai frecvent bug din aplicație.

**Pasul 5 — anunță adapterul.** `movieAdapter.notifyDataSetChanged()` după fiecare mutație. `ArrayAdapter` ține **referința** la lista `movies`, deci vede imediat conținutul nou; dar `ListView` nu observă lista, observă doar ce i-a spus adapterul la ultimul bind. Fără `notifyDataSetChanged()`, rândul rămâne desenat cu valorile vechi până la următoarea redesenezare (derulare, rotire, revenire din alt ecran).

**De ce merge așa:** rezultatul unei activități are două componente — un cod și un `Intent`. `setResult(RESULT_OK, intent)` scrie ambele într-un câmp al activității, iar `finish()` le trimite apelantului. `MainActivity` primește un `Movie` **deserializat**, adică un obiect nou, construit din bytes; singurul lucru care îl leagă de rândul din listă este `position`, pe care l-ai trimis separat tocmai pentru că obiectul nu știe unde stă. De aceea lanțul are trei verigi obligatorii: poziția trimisă la dus, poziția trimisă la întors, și `set` în loc de `add`. Dacă oricare lipsește, filmul apare de două ori sau dispare.

**Greșeala care costă puncte:**

1. **`add` în loc de `set` pe ramura de editare.** Simptom: editezi „Inception", apeși „Update Movie", iar lista are 4 rânduri — „Inception" vechi și „Inception" nou. Cauza: ramura `else` face `movies.add(movie)` sau lipsește cu totul, iar totul cade pe `add`.
2. **Uiți `setResult` înainte de `finish()`.** Simptom: formularul se închide, dar lista nu se schimbă deloc; în callback `o.getResultCode()` este `0` (`RESULT_CANCELED`). Cauza: ai apelat `finish()` singur. `finish()` trimite codul curent, care implicit este `RESULT_CANCELED`.
3. **Nu trimiți `POSITION_EXTRA`.** Simptom: același duplicat ca la punctul 1, deși codul din callback este corect. Cauza: ai uitat `intent.putExtra(POSITION_EXTRA, position)` în `saveMovie()`, deci `getIntExtra(..., -1)` întoarce `-1` și ramura aleasă este `add`.

**Verificarea:** lista are 3 filme. Atingi „Toy Story", schimbi titlul în „Toy Story 2", apeși „Update Movie". Lista trebuie să aibă tot **3** rânduri, iar rândul 2 să fie „Toy Story 2". Apoi apeși FAB, completezi titlul „Dune", „Save Movie": lista are **4** rânduri. Dacă are 5, ai `add` pe ramura de editare. Dacă are tot 3 după insert, ai uitat `notifyDataSetChanged()`.

**Exersează:** [24.2](cap-24.html#ex-24-2) (de ce `set` și nu `add`), [24.9](cap-24.html#ex-24-9) (debug: după editare filmul apare de două ori).

---
## Rețeta 35.6 — Returnează un cod de rezultat (ștergere)

**Cerința, cum sună la test:** „Adaugă posibilitatea de a șterge un film: ecranul de detalii închide cu un cod propriu, iar lista scoate rândul când primește acel cod."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | constanta `RESULT_DELETE`, câmpul `deleteMode`, metoda `deleteMovie()` | da |
| 2 | `activities/MainActivity.java` | constanta `DELETE_MODE_EXTRA` + `setOnItemLongClickListener` pe listă | da |
| 3 | `activities/MainActivity.java` | ramura `else if` din callback-ul launcher-ului | da |
| 4 | `res/layout/activity_item.xml` | **nimic** — refolosim butonul care există deja | nu |

**Pașii, în ordine:**

**Pasul 1 — pune cheia modului de ștergere în `MainActivity`, lângă celelalte două:**

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
protected static final String DELETE_MODE_EXTRA = "delete_mode";
```

**Pasul 2 — adaugă long press pe rând, în `MainActivity.initListeners()`.** Click-ul normal deschide editarea; ținerea apăsată deschide același ecran, dar în modul de ștergere:

```java
listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
    @Override
    public boolean onItemLongClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        intent.putExtra(DELETE_MODE_EXTRA, true);
        launcher.launch(intent);
        return true;
    }
});
```

`return true` înseamnă „am consumat evenimentul". Dacă întorci `false`, la ridicarea degetului se declanșează și click-ul normal, deci ecranul s-ar deschide de două ori.

**Pasul 3 — declară codul propriu în `ItemActivity`.** Orice cod propriu trebuie să fie **cel puțin 1**, pentru că 0 este `RESULT_CANCELED` și -1 este `RESULT_OK`:

```java
public static final int RESULT_DELETE = 2;
```

**Pasul 4 — citește modul în `ItemActivity.onCreate()`.** După blocul care umple formularul:

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}

deleteMode = intent.getBooleanExtra(MainActivity.DELETE_MODE_EXTRA, false);
if (deleteMode) {
    setTitle("Delete movie");
    btMovieAction.setText("Delete movie");
}
```

Câmpul nou, lângă `position`:

```java
private boolean deleteMode = false;
```

Ordinea contează: `deleteMode` se citește **după** blocul `if (existing != null)`, altfel textul „Update Movie" pus de acel bloc ar rescrie „Delete movie".

**Pasul 5 — leagă butonul de două acțiuni.** Listener-ul existent din `initListeners()` devine:

```java
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        if (deleteMode) {
            deleteMovie();
        } else {
            saveMovie();
        }
    }
});
```

Listener-ul citește câmpul `deleteMode` abia la click, deci nu contează că `initListeners()` rulează înainte de citirea extra-ului din `onCreate`.

**Pasul 6 — scrie `deleteMovie()`:**

```java
private void deleteMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_DELETE, intent);
    finish();
}
```

**Pasul 7 — adaugă ramura în callback-ul din `MainActivity`:**

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    movieAdapter.notifyDataSetChanged();
} else if (o.getResultCode() == ItemActivity.RESULT_DELETE) {
    Intent data = o.getData();
    if (data != null) {
        int position = data.getIntExtra(POSITION_EXTRA, -1);
        if (position >= 0 && position < movies.size()) {
            movies.remove(position);
            movieAdapter.notifyDataSetChanged();
        }
    }
}
```

`movies.remove(position)` cu `int` înseamnă „scoate elementul de la indexul `position`" (`List.remove(int)`), nu „scoate obiectul `position`". A doua variantă ar fi `movies.remove(movies.get(position))` și ar căuta după `equals`.

**De ce merge așa:** `setResult` are două argumente tocmai pentru că rezultatul are două dimensiuni: **codul** spune *ce s-a întâmplat* (`OK` = salvare, `RESULT_DELETE` = ștergere, `CANCELED` = nimic), iar **`Intent`-ul** spune *cu ce*. Callback-ul din `MainActivity` nu poate ghici ce a vrut utilizatorul, deci codul este singurul semnal. `Activity` ține codul într-un câmp intern, inițial `RESULT_CANCELED`; `setResult` doar îl scrie, iar `finish()` îl trimite apelantului. De aceea ordinea `setResult` → `finish()` este obligatorie, iar un cod propriu trebuie să fie pozitiv: valorile negative și zero sunt rezervate de sistem. Faptul că refolosim `btMovieAction` nu este un compromis estetic — este exact ce ai face dacă nu ai timp să atingi layout-ul, iar la examen economisește un pas întreg (XML + `findViewById` + listener nou).

**Greșeala care costă puncte:**

1. **Cod propriu egal cu 0.** Simptom: apeși „Delete movie", ecranul se închide, lista nu se schimbă, iar în callback `getResultCode()` este `0`. Cauza: ai declarat `RESULT_DELETE = 0` sau ai uitat `setResult` cu totul. Zero este `RESULT_CANCELED`, adică exact „utilizatorul a renunțat".
2. **`o.getData()` folosit fără verificare.** Simptom: `NullPointerException` pe ramura nouă, deși ramura `RESULT_OK` merge. Cauza: un rezultat poate veni cu cod valid și fără `Intent`; `getData()` întoarce `null`, iar `getIntExtra` pe `null` crapă.
3. **Ștergi din listă fără `notifyDataSetChanged()`.** Simptom: filmul dispare din model, dar rândul rămâne pe ecran până la următoarea redesenezare; dacă apeși din nou pe el, poziția nu mai corespunde. Cauza: ai uitat anunțul adapterului.

**Verificarea:** ții apăsat pe „The Matrix". Ecranul de detalii se deschide cu „Delete movie" pe buton și „Delete movie" în bara de sus. Apeși butonul: revii în listă, iar lista are **2** rânduri. Apoi ții apăsat pe un rând și apeși Back: lista are tot 2 rânduri — dovada că Back trimite `RESULT_CANCELED`, nu `RESULT_DELETE`. În final apeși FAB-ul: butonul scrie „Save Movie", nu „Delete movie", pentru că în modul insert `deleteMode` este `false`.

**Exersează:** [20.3](cap-20.html#ex-20-3) (exact acest lanț, cu buton separat în layout), [24.4](cap-24.html#ex-24-4) (verificarea numărului de filme cu `Toast`).

---

## Rețeta 35.7 — Intent implicit

**Cerința, cum sună la test:** „Utilizatorul ține apăsat pe câmpul cu linkul posterului și aplicația deschide linkul în browser."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `setOnLongClickListener` pe `etPoster` + `Intent(ACTION_VIEW, Uri)` | da |
| 2 | `activities/ItemActivity.java` | importurile `android.net.Uri` și `android.content.ActivityNotFoundException` | da |
| 3 | `AndroidManifest.xml` | `<queries>` pentru `ACTION_VIEW` — doar dacă folosești `resolveActivity` | doar dacă |

**Pașii, în ordine:**

**Pasul 1 — pune listener-ul în `ItemActivity.initListeners()`.** Nu pe click, ci pe **long click**: un `EditText` are nevoie de click ca să primească focus și tastatură, deci un `OnClickListener` ar fura exact gestul de editare.

```java
etPoster.setOnLongClickListener(new View.OnLongClickListener() {
    @Override
    public boolean onLongClick(View v) {
        String url = etPoster.getText().toString().trim();
        if (url.isEmpty()) {
            etPoster.setError("Poster URL is empty");
            return true;
        }
        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
        try {
            startActivity(intent);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(ItemActivity.this, "No app can open this link", Toast.LENGTH_SHORT).show();
        }
        return true;
    }
});
```

**Pasul 2 — adaugă importurile.** `Toast` există deja în fișier; lipsesc cele două:

```java
import android.content.ActivityNotFoundException;
import android.net.Uri;
```

**Pasul 3 — varianta cu verificare înainte de lansare.** Dacă vrei să nu prinzi excepția, întrebi întâi cine poate răspunde:

```java
Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
if (intent.resolveActivity(getPackageManager()) != null) {
    startActivity(intent);
} else {
    Toast.makeText(ItemActivity.this, "No app can open this link", Toast.LENGTH_SHORT).show();
}
```

Atenție însă: din Android 11, `resolveActivity` este filtrat de **package visibility**. Fără o declarație `<queries>` în manifest, metoda poate întoarce `null` chiar și când un browser există. Declarația arată așa:

```xml
<queries>
    <intent>
        <action android:name="android.intent.action.VIEW" />
        <data android:scheme="https" />
    </intent>
</queries>
```

De aceea varianta cu `try`/`catch` este mai sigură la examen: nu depinde de manifest.

**Pasul 4 — alte acțiuni implicite, aceeași mecanică.** Schimbi doar acțiunea și `Uri`-ul:

```java
// browser
new Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com/posters/inception.jpg"));

// telefon
new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0744000000"));

// e-mail
new Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:test@example.com"));

// partajare text — aici ai nevoie și de tip
Intent share = new Intent(Intent.ACTION_SEND);
share.setType("text/plain");
share.putExtra(Intent.EXTRA_TEXT, etTitle.getText().toString());
startActivity(Intent.createChooser(share, "Share movie"));
```

`Intent.createChooser` afișează un dialog cu toate aplicațiile care pot răspunde, în loc să aleagă una singură. Pentru `ACTION_SEND` este aproape obligatoriu: altfel sistemul poate alege automat o aplicație pe care utilizatorul nu o aștepta.

**Pasul 5 — ce se întâmplă cu activitatea ta.** Când browserul se deschide, `ItemActivity` primește `onPause`, apoi `onStop`. Nu primești niciun rezultat, pentru că ai folosit `startActivity`, nu un launcher. Când revii cu Back, `ItemActivity` este doar repornită (`onRestart` → `onStart` → `onResume`), iar formularul este intact.

**De ce merge așa:** un `Intent` implicit nu numește o clasă, ci descrie **ce vrei să se întâmple**: o acțiune (`ACTION_VIEW`) și o dată (`Uri`). Sistemul interoghează `PackageManager`-ul, care știe ce activități din ce aplicații au declarat `intent-filter`-uri compatibile, și pornește pe cea potrivită — sau afișează un chooser dacă sunt mai multe. Tu nu afli niciodată ce aplicație a răspuns, iar aplicația ta nu are nevoie de permisiuni pentru asta. Diferența față de `Intent`-ul explicit din 35.1 este exact aceasta: explicit înseamnă „clasa X", implicit înseamnă „oricine știe să facă Y cu datele Z". Dacă nimeni nu știe, `startActivity` aruncă `ActivityNotFoundException` — singurul caz în care un `Intent` implicit crapă.

**Greșeala care costă puncte:**

1. **`Uri.parse` fără schemă.** Simptom: `ActivityNotFoundException` la orice link scris fără `https://`, deși linkul pare valid. Cauza: `Uri.parse("www.example.com")` produce un `Uri` cu schemă `null`, pe care niciun browser nu îl acceptă. Soluția: validează sau completează schema înainte.
2. **Listener pe click în loc de long click.** Simptom: apeși pe câmp, se deschide browserul și nu mai poți scrie în el. Cauza: `setOnClickListener` pe un `EditText` înlocuiește comportamentul normal de focus.
3. **`startActivity` fără `try`/`catch` și fără verificare.** Simptom: crash cu `ActivityNotFoundException` pe emulatorul fără browser. Cauza: ai presupus că aplicația țintă există.

**Verificarea:** completezi `etPoster` cu `https://example.com/posters/inception.jpg`, ții apăsat pe câmp: se deschide browserul pe acel link. Revii cu Back: formularul este intact, cu toate valorile. Golești câmpul și ții apăsat din nou: apare eroarea „Poster URL is empty" pe câmp, fără să se deschidă nimic.

**Exersează:** [18.6](cap-18.html#ex-18-6) (URL-ul posterului afișat într-un `TextView`), [17.7](cap-17.html#ex-17-7) (validarea unui câmp obligatoriu înainte de a face ceva cu valoarea lui).

---

## Rețeta 35.8 — Back vs finish() vs setResult

**Cerința, cum sună la test:** „Explică ce se întoarce în listă când apeși Back, când apeși Save și când apeși Save urmat imediat de Back."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `setResult(RESULT_OK, intent)` înainte de `finish()` în `saveMovie()` | da — deja există |
| 2 | `activities/MainActivity.java` | garda `if (o.getResultCode() == RESULT_OK)` | da — deja există |
| 3 | `activities/ItemActivity.java` | `OnBackPressedCallback` — doar dacă vrei să schimbi comportamentul lui Back | doar dacă |

**Pașii, în ordine:**

**Pasul 1 — înțelege cele trei noțiuni, care nu sunt sinonime:**

| Noțiune | Ce este | Cine o produce |
|---|---|---|
| **Back** | un gest al utilizatorului, care închide activitatea curentă | sistemul, prin `OnBackPressedDispatcher` |
| **`finish()`** | metoda care cere închiderea activității | codul tău (sau Back, indirect) |
| **`setResult(cod, intent)`** | scrie rezultatul care va fi trimis apelantului | codul tău |

Back **nu** este `finish()` apelat de tine: Back este un eveniment care, dacă nu e interceptat, duce la `finish()`. Iar `finish()` **nu** implică un rezultat `OK`: trimite ce e în câmpul intern, adică `RESULT_CANCELED` dacă nu ai scris altceva.

**Pasul 2 — scrie corect finalul lui `saveMovie()`:**

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1) {
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
}
setResult(RESULT_OK, intent);
finish();
```

Ordinea este singura care funcționează: `setResult` **scrie**, `finish()` **trimite**. Invers, rezultatul se pierde.

**Pasul 3 — cunoaște toate scenariile.** Tabelul de mai jos este răspunsul complet la cerință:

| Ce face utilizatorul | Ce se execută | Cod trimis | Ce face `MainActivity` |
|---|---|---|---|
| Back fără Save | `finish()` implicit | `RESULT_CANCELED` (0) | nimic — garda `== RESULT_OK` nu trece |
| Save | `setResult(RESULT_OK)` + `finish()` | `RESULT_OK` (-1) | `add` sau `set`, apoi `notifyDataSetChanged()` |
| Save, apoi Back imediat | primul `finish()` închide; al doilea Back nu mai ajunge la `ItemActivity` | `RESULT_OK` | la fel ca la Save |
| `finish()` fără `setResult` | `finish()` | `RESULT_CANCELED` | nimic |
| `setResult(RESULT_OK)` fără `finish()` | nimic, deocamdată | — | nimic până la închidere |
| `setResult(RESULT_OK)`, apoi Back | Back → `finish()` → trimite rezultatul scris | `RESULT_OK` | `add` sau `set` |
| `finish()`, apoi `setResult(...)` | al doilea apel este ignorat | `RESULT_CANCELED` | nimic |

Ultimele două rânduri sunt capcanele reale. `setResult` nu trimite nimic; doar memorează. Deci dacă îl apelezi prea devreme — de exemplu în `onCreate`, ca să „fii sigur" — și utilizatorul apasă Back, lista primește `RESULT_OK` cu un `Intent` care poate nici nu conține filmul. Iar dacă apelezi `finish()` înainte de `setResult`, al doilea apel nu mai are efect.

**Pasul 4 — varianta corectă dacă vrei să schimbi comportamentul lui Back.** Nu suprascrii `onBackPressed()` (depreciat din API 33), înregistrezi un callback:

```java
getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
    @Override
    public void handleOnBackPressed() {
        setResult(RESULT_CANCELED);
        finish();
    }
});
```

Importul este `androidx.activity.OnBackPressedCallback`. În practică, pentru aplicația asta nu ai nevoie: comportamentul implicit este exact ce trebuie.

**Pasul 5 — verifică ordinea cu `Log`.** Pune un log înainte de `setResult` și unul în callback:

```java
// ItemActivity.saveMovie()
Log.d("G1097", "saveMovie: setResult OK, position=" + position);
setResult(RESULT_OK, intent);
finish();

// MainActivity, prima linie din onActivityResult
Log.d("G1097", "callback: code=" + o.getResultCode() + " data=" + o.getData());
```

**De ce merge așa:** fiecare `Activity` are un câmp intern pentru codul de rezultat, inițializat cu `RESULT_CANCELED`. `setResult` îl suprascrie. `finish()` cere `ActivityManager`-ului închiderea activității și, în același timp, îi spune ce cod și ce `Intent` să livreze apelantului. `ActivityManager` păstrează rezultatul până când apelantul revine în `STARTED`, apoi îl predă registry-ului de rezultate, care cheamă callback-ul. Back este doar un eveniment care ajunge la același `finish()` dacă nu îl interceptezi — de aceea Back „anulează" în mod implicit: nu pentru că cineva a decis asta, ci pentru că valoarea inițială a câmpului este `RESULT_CANCELED`.

**Greșeala care costă puncte:**

1. **`setResult` după `finish()`.** Simptom: formularul se închide, lista nu se schimbă, iar în Logcat callback-ul vede `code=0`. Cauza: ordinea inversă. `finish()` a trimis deja `RESULT_CANCELED`.
2. **`setResult` în `onCreate`, ca să fie „gata".** Simptom: apeși Back fără să salvezi și, uneori, lista se schimbă sau crapă cu `NullPointerException` pe `getSerializableExtra`. Cauza: rezultatul memorat este trimis și la Back, iar `Intent`-ul nu conține filmul.
3. **Așteptarea ca Back să păstreze modificările.** Simptom: editezi cinci câmpuri, apeși Back, lista arată valorile vechi — și e comportamentul corect. Cauza: modificările trăiesc doar în widget-uri; ele ajung în listă numai prin `saveMovie()`.

**Verificarea:** trei teste, fiecare cu Logcat-ul deschis. (1) Deschizi un film, apeși Back: nu apare nicio linie `callback`. (2) Deschizi, apeși „Update Movie": apare `callback: code=-1`. (3) Deschizi, apeși „Update Movie", apoi Back imediat: apare o singură linie `callback: code=-1`, nu două — a doua apăsare nu mai are ce închide.

**Exersează:** [24.3](cap-24.html#ex-24-3) (apeși Back fără Save: nu se schimbă nimic — ce garantează asta), [24.2](cap-24.html#ex-24-2) (de ce editarea înseamnă `set`).

---

## Rețeta 35.9 — Formularul supraviețuiește rotirii

**Cerința, cum sună la test:** „Rotește ecranul în timp ce completezi formularul: valorile introduse nu trebuie să se piardă, iar la salvare data să rămână cea afișată."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `onSaveInstanceState` cu `releaseCal` | da |
| 2 | `activities/ItemActivity.java` | restaurarea în `onCreate()`, după `fillForm()` | da |
| 3 | `activities/ItemActivity.java` | `fillForm()`: sincronizezi `releaseCal` cu filmul editat | da — capcana reală |
| 4 | `activities/MainActivity.java` | `onSaveInstanceState` cu lista — doar dacă cerința vorbește despre listă | doar dacă |

**Pașii, în ordine:**

**Pasul 1 — știi ce se salvează singur.** La rotire, Android distruge activitatea și o recreează. Înainte de distrugere, fiecare **view cu `android:id`** își salvează starea internă, iar după `onCreate` i-o restaurează. În `ItemActivity`, asta înseamnă:

| Widget | Ce se salvează automat | De ce |
|---|---|---|
| `etTitle`, `etRelease`, `etBudget`, `etPoster` | textul | `EditText.getFreezesText()` întoarce `true` |
| `sbDuration` | progresul | `ProgressBar` își salvează `mProgress` |
| `rbRating` | progresul (deci rating-ul) | moștenește `ProgressBar` |
| `cbonWatchList`, `swWatched` | bifa | `CompoundButton` își salvează `mChecked` |
| `rgApproval` | id-ul butonului bifat | `RadioGroup` salvează `mCheckedId` |
| `spGenre` | poziția selectată | `AbsSpinner` salvează poziția |

Ce **nu** se salvează: câmpurile tale (`position`, `releaseCal`), plus textele din `tvDurationValue` și `tvWatchedValue` — un `TextView` simplu nu își salvează textul dacă nu are `android:freezesText="true"`.

**Pasul 2 — observă de ce etichetele se refac totuși.** `tvDurationValue` și `tvWatchedValue` par pierdute, dar nu sunt: la restaurare, `sbDuration` primește progresul salvat prin `setProgress(...)`, ceea ce declanșează `onProgressChanged`, iar listener-ul rescrie eticheta. La fel, `swWatched` este restaurat prin `setChecked(...)`, care declanșează `onCheckedChanged`. Etichetele sunt **derivate**, iar listener-ul le re-derivă. Lecția: un `TextView` care arată o valoare derivată nu are nevoie de salvare proprie atâta timp cât sursa lui se restaurează și listener-ul există.

**Pasul 3 — salvează `releaseCal`.** Aici este capcana reală. `releaseCal` este un `Calendar`, nu un view, deci nu se salvează singur. Adaugă în `ItemActivity`:

```java
private static final String KEY_RELEASE_MILLIS = "release_millis";

@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putLong(KEY_RELEASE_MILLIS, releaseCal.getTimeInMillis());
}
```

**Pasul 4 — restaurează-l în `onCreate()`, după blocul care umple formularul.** Ordinea nu e opțională:

```java
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}

if (savedInstanceState != null) {
    releaseCal.setTimeInMillis(
            savedInstanceState.getLong(KEY_RELEASE_MILLIS, releaseCal.getTimeInMillis()));
}
```

De ce după: la rotire, `getIntent()` întoarce același `Intent`, deci `fillForm(existing)` rulează din nou și ar rescrie `releaseCal` cu data filmului. Valoarea utilizatorului, salvată în `Bundle`, trebuie aplicată **ultima**.

**Pasul 5 — repară și sincronizarea din `fillForm()`.** Fără pasul acesta, rețeta nu se termină: în codul original, `fillForm` scrie data în `etRelease`, dar **nu** în `releaseCal`. Iar `saveMovie()` citește `releaseCal.getTime()`. Consecința: deschizi un film în editare, nu atingi câmpul de dată, apeși „Update Movie" — și filmul primește data de **azi**.

```java
private void fillForm(Movie existing) {
    etTitle.setText(existing.getTitle());
    etRelease.setText(dateFormat.format(existing.getRelease()));
    if (existing.getRelease() != null) {
        releaseCal.setTime(existing.getRelease());
    }
    etBudget.setText(String.valueOf(existing.getBudget()));
    sbDuration.setProgress(existing.getDuration());
    cbonWatchList.setChecked(existing.isOnWatchlist());
    swWatched.setChecked(existing.isWatched());
    rbRating.setRating(existing.getRating());
    etPoster.setText(existing.getPoster());
    for (int index = 0; index < spGenre.getCount(); index++) {
        if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
            spGenre.setSelection(index);
            break;
        }
    }
    for (int index = 0; index < rgApproval.getChildCount(); index++) {
        RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
        if (rb.getText().toString().equals(existing.getApproval())) {
            rgApproval.check(rgApproval.getChildAt(index).getId());
            break;
        }
    }
}
```

Garda `!= null` este necesară pentru că `dateFormat.format(null)` aruncă `NullPointerException` pe linia de deasupra — un film cu `release == null` crapă înainte să ajungă la `releaseCal`.

**Pasul 6 — lista din `MainActivity`, dacă cerința o cere.** Rotirea distruge și `MainActivity`. La recreare, `addSampleMovies()` rulează din nou pe o listă goală, deci filmele adăugate de utilizator dispar. Soluția minimă este `Bundle`:

```java
private static final String KEY_MOVIES = "movies";

@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putSerializable(KEY_MOVIES, new ArrayList<>(movies));
}
```

iar în `onCreate()`, imediat după `addSampleMovies()`:

```java
if (savedInstanceState != null) {
    Object saved = savedInstanceState.getSerializable(KEY_MOVIES);
    if (saved instanceof ArrayList) {
        movies.clear();
        movies.addAll((ArrayList<Movie>) saved);
    }
}
```

Necesită `import androidx.annotation.NonNull;` în `MainActivity`. `ArrayList<Movie>` este serializabil pentru că `Movie` este serializabil. Atenție: `getSerializable(String)` este depreciat din API 33; la examen funcționează, iar varianta modernă este `BundleCompat`. Această soluție ține lista doar la rotire — pentru repornirea aplicației vezi 35.10.

**De ce merge așa:** rotirea este o **schimbare de configurație**. În loc să rearanjeze view-urile existente, Android alege soluția simplă și sigură: distruge activitatea (`onPause` → `onStop` → `onDestroy`) și o recreează (`onCreate` → `onStart` → `onResume`). Înainte de distrugere, `onSaveInstanceState` este chemat pe fiecare view din arbore, iar starea se strânge într-un `Bundle` pe care sistemul îl păstrează. La recreare, `onCreate` rulează **înaintea** restaurării view-urilor: de aceea `fillForm(existing)` poate scrie liniștit în `EditText`, iar apoi framework-ul pune peste textul salvat al utilizatorului. Câmpurile tale nu fac parte din arbore, deci pentru ele `Bundle`-ul trebuie completat manual. Iar `releaseCal` este cazul perfect: valoarea lui nu se vede nicăieri în UI, dar este cea care ajunge în model la salvare.

**Greșeala care costă puncte:**

1. **Nu sincronizezi `releaseCal` în `fillForm`.** Simptom: editezi un film, nu atingi data, salvezi — data devine ziua de azi, fără nicio eroare. Cauza: `etRelease` arată data corectă, dar `saveMovie()` citește `releaseCal`, care a rămas `Calendar.getInstance()`.
2. **Restaurezi `releaseCal` înainte de `fillForm`.** Simptom: rotirea pare că funcționează, dar dacă rotești în timpul editării și salvezi, data revine la cea din film — modificarea utilizatorului este ignorată. Cauza: ordinea inversă în `onCreate`; `fillForm` a rescris valoarea restaurată.
3. **Crezi că `tvDurationValue` are nevoie de salvare proprie.** Simptom: adaugi cod inutil și, uneori, introduci un bug de sincronizare. Cauza: ai uitat că listener-ul `sbDuration` rescrie eticheta la restaurare.

**Verificarea:** deschizi „Inception", schimbi titlul în „Test", duci durata la 200, pornești switch-ul, alegi „R", deschizi date picker-ul și alegi 01/01/2020. Rotești ecranul: toate cele cinci valori sunt acolo, iar etichetele arată „200 min." și „Yes". Apeși „Update Movie": în listă, filmul are data 01/01/2020, nu data de azi. Apoi rotești lista: cele trei filme plus cele adăugate de tine sunt încă acolo.

**Exersează:** [24.5](cap-24.html#ex-24-5) (ce se pierde de fapt din formular la rotire), [19.6](cap-19.html#ex-19-6) (rotirea nu pierde formularul).

---

## Rețeta 35.10 — Lista supraviețuiește închiderii aplicației (SharedPreferences + JSON)

**Cerința, cum sună la test:** „Datele să se salveze: adaugi un film, închizi aplicația din Recents, o redeschizi, iar filmul este încă în listă."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | două constante: numele fișierului de preferințe și cheia JSON | da |
| 2 | `activities/MainActivity.java` | înlocuiești `addSampleMovies();` cu încărcare + populare la prima rulare | da |
| 3 | `activities/MainActivity.java` | `onPause()` care salvează | da |
| 4 | `activities/MainActivity.java` | cinci metode: `saveMovies`, `loadMovies`, `moviesToJson`, `moviesFromJson`, `escape` | da |
| 5 | `activities/MainActivity.java` | șase importuri | da |
| 6 | `build.gradle.kts` | **nimic** — `org.json` vine cu Android, nu e dependență | nu |

**Pașii, în ordine:**

**Pasul 1 — declară constantele, lângă cheile de extra:**

```java
private static final String PREFS_NAME = "g1097_movies";
private static final String KEY_MOVIES_JSON = "movies_json";
```

**Pasul 2 — înlocuiește `addSampleMovies();` din `onCreate()`.** Linia există singură, între blocul de insets și crearea adapterului:

```java
movies.addAll(loadMovies());
if (movies.isEmpty()) {
    addSampleMovies();
    saveMovies();               // prima rulare: demo-urile ajung pe disc
}

movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
initControls();
initListeners();
```

`movies` este declarat `private final List<Movie> movies = new ArrayList<>();`. De aceea **nu** scrii `movies = loadMovies();` — nu compilează. Adapterul ține referința la listă, nu la conținut, deci lista nu se reasignează niciodată; se modifică doar prin `addAll` / `clear` / `add` / `set` / `remove`.

**Pasul 3 — salvează la fiecare ieșire din ecran:**

```java
@Override
protected void onPause() {
    super.onPause();
    saveMovies();
}
```

`onPause`, nu `onDestroy`: `onDestroy` nu este garantat — dacă procesul este omorât, nu se cheamă. `onPause` se cheamă la fiecare ieșire din ecran, inclusiv când deschizi `ItemActivity` sau când apeși Home.

**Pasul 4 — scrie și citește:**

```java
private boolean saveMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = moviesToJson();
    boolean ok = prefs.edit().putString(KEY_MOVIES_JSON, json).commit();
    Log.d("G1097", "saveMovies: " + movies.size() + " filme, "
            + json.length() + " caractere, ok=" + ok);
    return ok;
}

private List<Movie> loadMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = prefs.getString(KEY_MOVIES_JSON, null);
    List<Movie> loaded = moviesFromJson(json);
    Log.d("G1097", "loadMovies: " + loaded.size() + " filme din " + PREFS_NAME);
    return loaded;
}
```

**Pasul 5 — construiește JSON-ul manual, cu `StringBuilder`.** Fără Gson, fără Moshi, fără nicio dependență nouă. Toate cele 10 câmpuri, în aceeași ordine:

```java
private String moviesToJson() {
    StringBuilder sb = new StringBuilder("[");
    for (int i = 0; i < movies.size(); i++) {
        Movie m = movies.get(i);
        if (i > 0) sb.append(',');
        sb.append('{')
          .append("\"title\":\"").append(escape(m.getTitle())).append("\",")
          .append("\"release\":").append(m.getRelease() == null ? 0L : m.getRelease().getTime()).append(',')
          .append("\"genre\":\"").append(escape(m.getGenre())).append("\",")
          .append("\"budget\":").append(BigDecimal.valueOf(m.getBudget()).toPlainString()).append(',')
          .append("\"duration\":").append(m.getDuration()).append(',')
          .append("\"rating\":").append(m.getRating()).append(',')
          .append("\"watched\":").append(m.isWatched()).append(',')
          .append("\"approval\":\"").append(escape(m.getApproval())).append("\",")
          .append("\"onWatchlist\":").append(m.isOnWatchlist()).append(',')
          .append("\"poster\":\"").append(escape(m.getPoster())).append("\"")
          .append('}');
    }
    return sb.append(']').toString();
}

private static String escape(String value) {
    if (value == null) return "";
    return value.replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t");
}
```

Ordinea din `escape` contează: întâi backslash, apoi ghilimele. Invers, `\"` ar deveni `\\"` și JSON-ul s-ar strica.

**Pasul 6 — citește JSON-ul cu `org.json`:**

```java
private List<Movie> moviesFromJson(String json) {
    List<Movie> result = new ArrayList<>();
    if (json == null || json.isEmpty()) return result;
    try {
        JSONArray array = new JSONArray(json);
        for (int i = 0; i < array.length(); i++) {
            JSONObject o = array.getJSONObject(i);
            Movie m = new Movie();
            m.setTitle(o.optString("title", ""));
            m.setRelease(new Date(o.optLong("release", 0L)));
            m.setGenre(o.optString("genre", ""));
            m.setBudget(o.optDouble("budget", 0));
            m.setDuration(o.optInt("duration", 0));
            m.setRating((float) o.optDouble("rating", 0));
            m.setWatched(o.optBoolean("watched", false));
            m.setApproval(o.optString("approval", ""));
            m.setOnWatchlist(o.optBoolean("onWatchlist", false));
            m.setPoster(o.optString("poster", ""));
            result.add(m);
        }
    } catch (JSONException e) {
        Log.e("G1097", "JSON invalid — pornesc cu lista goală", e);
    }
    return result;
}
```

`optString` / `optInt` / `optLong` / `optDouble` / `optBoolean` întorc o valoare implicită în loc să arunce. `getString` ar arunca `JSONException` dacă cheia lipsește — util când vrei să afli că fișierul e corupt, dăunător când vrei ca aplicația să pornească.

**Pasul 7 — adaugă importurile:**

```java
import android.content.SharedPreferences;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.math.BigDecimal;
```

**Pasul 8 — salvează și după fiecare rezultat primit.** `onPause` acoperă ieșirea din ecran, dar dacă procesul este omorât imediat după un insert, filmul nu a apucat să fie scris. O linie în callback închide golul:

```java
movies.add(movie);
movieAdapter.notifyDataSetChanged();
saveMovies();
```

**De ce merge așa:** la închiderea aplicației din Recents, procesul este omorât, iar odată cu el dispare tot heap-ul: `movies`, adapterul, activitățile. RAM-ul nu este persistență. `SharedPreferences` scrie un fișier XML în `/data/data/ro.ase.ie.g1097/shared_prefs/g1097_movies.xml`, pe care sistemul îl păstrează până la dezinstalare sau „Clear data". La prima citire, tot fișierul este încărcat în memorie; `edit()` construiește o copie modificabilă, iar `commit()` o scrie sincron și întoarce `boolean` — de aceea poți verifica în Logcat dacă scrierea a reușit. `apply()` ar scrie asincron și nu ar întoarce nimic. Pentru o listă de câteva filme, diferența de timp este neglijabilă, iar `commit()` îți dă dovada.

Trei decizii care merită explicate la examen:

- **`BigDecimal.valueOf(...).toPlainString()`** în loc de `String.valueOf(double)`. `String.valueOf(160000000.0)` produce `1.6E8`. JSON acceptă notația științifică, deci s-ar reîncărca corect, dar fișierul devine ilizibil. `toPlainString()` scrie `160000000`.
- **`release` ca `long`** (`Date.getTime()`), nu ca text. Un `Date` formatat depinde de `Locale` și de fus orar; un `long` este fără ambiguitate. `0` este sentința pentru „fără dată" și devine `new Date(0)` la citire, ca să nu introduci `null` — `fillForm` crapă pe `release == null`.
- **JSON construit manual**, nu Gson. Gson nu este în dependențele proiectului, iar `org.json` vine cu Android SDK. La examen, „fără dependențe noi" este adesea o cerință explicită.

**Greșeala care costă puncte:**

1. **`movies = loadMovies();`** Simptom: eroare de compilare `cannot assign a value to final variable movies`. Cauza: lista este `final` pentru că adapterul ține referința la ea. Soluția: `movies.addAll(loadMovies());`.
2. **Fără `escape()`.** Simptom: adaugi un film cu titlul `He said "hi"`, închizi aplicația, o redeschizi — lista este goală, deși fișierul există. Cauza: ghilimelele au închis stringul JSON mai devreme, iar `new JSONArray(...)` a aruncat `JSONException`; codul pornește cu lista goală.
3. **Populare cu demo-uri necondiționată.** Simptom: după fiecare repornire, cele trei filme demo apar din nou, pe lângă cele salvate. Cauza: ai lăsat `addSampleMovies();` fără garda `if (movies.isEmpty())`.
4. **Salvare în `onDestroy()`.** Simptom: funcționează când apeși Back, nu funcționează când închizi din Recents. Cauza: `onDestroy` nu se cheamă când procesul este omorât.

**Verificarea:** adaugi filmul „Dune", închizi aplicația din Recents (swipe), o redeschizi: lista are **4** rânduri, iar demo-urile nu s-au dublat. Apoi adaugi un film cu titlul `He said "hi"`, repornești: titlul este intact. În Logcat, `saveMovies: 4 filme, ... caractere, ok=true` apare la fiecare ieșire din ecran. Verificarea pe disc este subiectul rețetei 35.11.

**Exersează:** [24.6](cap-24.html#ex-24-6) (implementarea de referință, cu aceeași abordare), [24.10](cap-24.html#ex-24-10) (examenul: „datele să se salveze").

---
## Rețeta 35.11 — Verifică persistența

**Cerința, cum sună la test:** „Demonstrează că datele chiar se salvează: arată fișierul de pe disc și dovedește că lista se reîncarcă după o repornire completă."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/MainActivity.java` | `Log.d` în `saveMovies()` și `loadMovies()` | da — dovezile |
| 2 | terminal / Android Studio | `adb shell run-as ... cat shared_prefs/g1097_movies.xml` | da |
| 3 | terminal / Android Studio | `adb shell am force-stop` și `adb shell pm clear` | da |
| 4 | `activities/MainActivity.java` | `Toast` cu numărul de filme — alternativă la Logcat | nu |

**Pașii, în ordine:**

**Pasul 1 — pune dovezi în cod, nu în ochi.** Fără loguri, „se salvează" este o impresie. Cele două linii din 35.10 sunt suficiente:

```java
Log.d("G1097", "saveMovies: " + movies.size() + " filme, "
        + json.length() + " caractere, ok=" + ok);
Log.d("G1097", "loadMovies: " + loaded.size() + " filme din " + PREFS_NAME);
```

`ok` este rezultatul lui `commit()`. Dacă este `false`, fișierul nu s-a scris — și afli asta imediat, nu după ce pierzi filmul.

**Pasul 2 — citește fișierul de pe disc.** Aplicația este în build `debug` (implicit în Android Studio), deci `run-as` funcționează:

```bash
adb shell run-as ro.ase.ie.g1097 cat shared_prefs/g1097_movies.xml
```

Trebuie să vezi ceva de forma:

```xml
<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
    <string name="movies_json">[{&quot;title&quot;:&quot;Inception&quot;,&quot;release&quot;:1279231200000,&quot;genre&quot;:&quot;Sci-Fi&quot;,...}]</string>
</map>
```

Trei lucruri se verifică aici: că fișierul există, că are cheia `movies_json` și că înăuntru se văd cele 10 câmpuri. `&quot;` este doar modul în care serializatorul XML escapează ghilimelele — JSON-ul din interior este corect.

**Pasul 3 — testează cele trei morți diferite.** Nu sunt echivalente:

| Test | Comandă / gest | Ce dovedește |
|---|---|---|
| Rotire | Ctrl+Left / Ctrl+Right în emulator | `onSaveInstanceState` (35.9), **nu** persistența |
| Închidere din Recents | swipe pe card | procesul moare, `onPause` a salvat |
| Oprire forțată | `adb shell am force-stop ro.ase.ie.g1097` | procesul moare fără `onDestroy` |
| Repornire emulator | cold boot | fișierul supraviețuiește reboot-ului |

```bash
adb shell am force-stop ro.ase.ie.g1097
adb shell monkey -p ro.ase.ie.g1097 -c android.intent.category.LAUNCHER 1
```

A doua comandă pornește aplicația din launcher. Dacă lista revine, persistența funcționează independent de ciclul de viață al activității.

**Pasul 4 — verifică începutul curat.** `pm clear` șterge toate datele aplicației, inclusiv preferințele:

```bash
adb shell pm clear ro.ase.ie.g1097
```

La următoarea pornire trebuie să vezi exact **3** filme — cele demo. Asta dovedește că ramura `if (movies.isEmpty())` funcționează și că popularea nu se repetă peste datele existente.

**Pasul 5 — verifică escape-ul cu date ostile.** Adaugă pe rând:

- un titlu cu ghilimele: `He said "hi"`;
- un titlu cu diacritice: `Ștrumfii`;
- un titlu cu backslash: `C:\Movies`;
- un buget mare: `160000000`.

După fiecare, închide din Recents și redeschide. Toate cele patru trebuie să revină identice. Dacă lista devine goală după unul dintre ele, `escape()` lipsește sau are ordinea greșită.

**Pasul 6 — citește Logcat-ul filtrat.** Nu căuta prin mii de linii:

```bash
adb logcat -s G1097
```

Vezi doar logurile tale, în ordine: `loadMovies: 3 filme din g1097_movies`, apoi, la fiecare ieșire din ecran, `saveMovies: 3 filme, ... ok=true`.

**De ce merge așa:** `SharedPreferences` este un fișier XML scris de `FastXmlSerializer` în directorul privat al aplicației. El nu depinde de proces, de activitate sau de ciclul de viață: odată ce `commit()` a întors `true`, datele sunt pe disc. De aceea verificarea corectă nu este „închid și deschid ecranul", ci „omor procesul și repornesc". `force-stop` este testul cel mai dur disponibil fără reboot: sistemul nu mai cheamă nimic din aplicație, exact ca atunci când utilizatorul face swipe din Recents. `run-as` funcționează pentru că build-ul `debug` este `debuggable`, iar `run-as` rulează procesul cu UID-ul aplicației — de aceea poate citi `/data/data/ro.ase.ie.g1097/`, unde altfel nu ai acces.

**Greșeala care costă puncte:**

1. **Verifici doar prin rotire.** Simptom: „merge" la rotire, dar filmul dispare la închidere. Cauza: rotirea este acoperită de `onSaveInstanceState` (35.9), nu de `SharedPreferences`. Sunt două mecanisme diferite, cu durate de viață diferite.
2. **`pm clear` înainte de a nota rezultatul așteptat.** Simptom: „s-au pierdut toate datele" — și chiar s-au pierdut, pentru că tu le-ai șters. Cauza: `pm clear` este resetare completă, nu test de persistență.
3. **Te uiți la fișier cu altă aplicație sau pe alt UID.** Simptom: `Permission denied` la `cat`. Cauza: ai uitat `run-as` sau rulezi pe un build `release`.

**Verificarea:** protocolul complet, în ordine: (1) `pm clear`, pornești, vezi 3 filme; (2) adaugi „Dune", vezi 4; (3) `adb shell run-as ro.ase.ie.g1097 cat shared_prefs/g1097_movies.xml` și găsești `Dune` în JSON; (4) `am force-stop`, pornești din launcher, vezi tot 4; (5) închizi din Recents, redeschizi, vezi tot 4; (6) adaugi un titlu cu ghilimele, repeti pașii 4–5, titlul este intact. Dacă toate șase trec, persistența este dovedită.

**Exersează:** [24.7](cap-24.html#ex-24-7) (checklist-ul în 6 verificări după fiecare atribut nou), [24.6](cap-24.html#ex-24-6) (implementarea pe care o verifici aici).

---

## Rețeta 35.12 — Application și ciclul de viață

**Cerința, cum sună la test:** „Explică ordinea metodelor de ciclu de viață pentru cele două ecrane și adaugă o clasă `Application` care loghează fiecare tranziție."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `MovieApp.java` (nou, în `ro.ase.ie.g1097`) | `extends Application`, `onCreate`, `registerActivityLifecycleCallbacks` | da |
| 2 | `AndroidManifest.xml` | `android:name=".MovieApp"` pe `<application>` | da |
| 3 | `activities/MainActivity.java` | `Log.d` în `onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy` | doar dacă nu folosești callback-urile |
| 4 | `activities/ItemActivity.java` | la fel | doar dacă nu folosești callback-urile |

**Pașii, în ordine:**

**Pasul 1 — reține ordinea, pentru fiecare tranziție:**

```text
PORNIRE:   Application.onCreate
           MainActivity.onCreate -> onStart -> onResume

DESCHIDE ItemActivity:
           MainActivity.onPause
           ItemActivity.onCreate -> onStart -> onResume
           MainActivity.onStop

BACK din ItemActivity:
           ItemActivity.onPause -> onStop -> onDestroy
           MainActivity.onRestart -> onStart -> onResume

HOME:
           MainActivity.onPause -> onStop            (rămâne în memorie)

ROTIRE:
           onPause -> onStop -> onSaveInstanceState -> onDestroy
           onCreate -> onStart -> onRestoreInstanceState -> onResume

ÎNCHIDERE DIN RECENTS:
           onPause -> onStop
           procesul moare; onDestroy NU este garantat
```

Regula de memorat: **`onCreate` → `onStart` → `onResume` la intrare, `onPause` → `onStop` → `onDestroy` la ieșire**, iar `onRestart` apare doar când activitatea revine din `stopped`, nu din `destroyed`.

**Pasul 2 — creează `MovieApp.java` în pachetul rădăcină.** Fișierul stă lângă `MainActivity` și `ItemActivity`, dar în `ro.ase.ie.g1097`, nu în `ro.ase.ie.g1097.activities`:

```java
package ro.ase.ie.g1097;

import android.app.Activity;
import android.app.Application;
import android.os.Bundle;
import android.util.Log;

public class MovieApp extends Application {

    private static final String TAG = "G1097";

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "MovieApp.onCreate");

        registerActivityLifecycleCallbacks(new ActivityLifecycleCallbacks() {
            @Override
            public void onActivityCreated(Activity activity, Bundle savedInstanceState) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onCreate");
            }

            @Override
            public void onActivityStarted(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onStart");
            }

            @Override
            public void onActivityResumed(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onResume");
            }

            @Override
            public void onActivityPaused(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onPause");
            }

            @Override
            public void onActivityStopped(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onStop");
            }

            @Override
            public void onActivitySaveInstanceState(Activity activity, Bundle outState) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onSaveInstanceState");
            }

            @Override
            public void onActivityDestroyed(Activity activity) {
                Log.d(TAG, activity.getClass().getSimpleName() + ".onDestroy");
            }
        });
    }
}
```

Interfața are exact șapte metode și trebuie implementate toate. Un singur loc în care pui loguri — nu mai atingi fiecare activitate.

**Pasul 3 — înregistrează clasa în manifest.** Fără linia asta, `MovieApp` nu este instanțiată niciodată și nu vezi niciun log:

```xml
<application
    android:name=".MovieApp"
    android:allowBackup="true"
    android:dataExtractionRules="@xml/data_extraction_rules"
    android:fullBackupContent="@xml/backup_rules"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:supportsRtl="true"
    android:theme="@style/Theme.G1097">
```

Punctul de la început înseamnă „în pachetul aplicației": `.MovieApp` este `ro.ase.ie.g1097.MovieApp`. Pentru activități, punctul se combină cu numele complet: `.activities.MainActivity`.

**Pasul 4 — folosește `Application` ca loc comun pentru listă, dacă cerința cere asta.** `Application` trăiește cât procesul, deci o listă ținută acolo supraviețuiește rotirii ambelor activități:

```java
// în MovieApp, lângă TAG
private final List<Movie> movies = new ArrayList<>();

public List<Movie> getMovies() {
    return movies;
}
```

Plus cele trei importuri care lipsesc din `MovieApp`:

```java
import java.util.ArrayList;
import java.util.List;
import ro.ase.ie.g1097.model.Movie;
```

În `MainActivity`, lista nu mai este creată local (și ai nevoie de `import ro.ase.ie.g1097.MovieApp;`, pentru că activitatea este în alt pachet):

```java
private List<Movie> movies;   // fără `final`, fără `new ArrayList<>()`

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

    movies = ((MovieApp) getApplication()).getMovies();
    if (movies.isEmpty()) {
        addSampleMovies();
    }
    movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
    initControls();
    initListeners();

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
                        } else {
                            movies.set(position, movie);
                        }
                        movieAdapter.notifyDataSetChanged();
                    }
                }
            });
}
```

Două capcane de ordine: atribuirea trebuie făcută **înainte** de crearea adapterului (adapterul primește referința), și **nu** în inițializatorul câmpului. `getApplication()` întoarce `null` acolo, pentru că inițializatoarele de câmp rulează în constructor, iar `attach()` — care leagă activitatea de aplicație — este chemat după constructor.

**Pasul 5 — știi ce NU rezolvă `Application`.** Lista din `Application` supraviețuiește rotirii și navigării, dar **nu** supraviețuiește morții procesului. Pentru repornire ai nevoie de 35.10. `onTerminate()` există în API, dar pe dispozitive reale nu este chemat niciodată — nu pune salvare acolo.

**De ce merge așa:** `Application` este un obiect creat de sistem înainte de orice activitate și distrus odată cu procesul. El nu are interfață și nu apare în back stack; este doar un punct de referință comun. `registerActivityLifecycleCallbacks` înregistrează un observator pe care `ActivityThread` îl cheamă pentru **fiecare** activitate a aplicației, în aceeași ordine în care ar chema metodele activității. De aceea logurile ies în ordinea corectă fără să modifici `MainActivity` sau `ItemActivity`. Rotirea este cea care produce confuzia: pare o „repornire", dar este o distrugere și o recreare a activității, nu a procesului — de aceea `Application.onCreate` apare o singură dată, iar `MainActivity.onCreate` apare de fiecare dată.

**Greșeala care costă puncte:**

1. **Uiți `android:name` în manifest.** Simptom: `MovieApp.onCreate` nu apare niciodată în Logcat, deși clasa există și compilează. Cauza: sistemul nu știe să o instanțieze.
2. **Puneți salvarea în `onTerminate()`.** Simptom: datele se pierd la închidere, deși ai scris codul „corect". Cauza: `onTerminate` nu este chemat pe dispozitive reale, doar în emulatorul vechi.
3. **`getApplication()` în inițializatorul câmpului.** Simptom: `NullPointerException` la pornire, pe linia care ia lista din aplicație. Cauza: câmpurile se inițializează în constructor, înainte de `attach()`.

**Verificarea:** deschizi Logcat filtrat pe `G1097`, pornești aplicația. Ordinea trebuie să fie: `MovieApp.onCreate`, `MainActivity.onCreate`, `MainActivity.onStart`, `MainActivity.onResume`. Atingi un rând: `MainActivity.onPause`, `ItemActivity.onCreate`, `ItemActivity.onStart`, `ItemActivity.onResume`, `MainActivity.onStop`. apeși Back: `ItemActivity.onPause`, `onStop`, `onDestroy`, apoi `MainActivity.onRestart`, `onStart`, `onResume`. Rotești în `ItemActivity`: `onPause`, `onStop`, `onSaveInstanceState`, `onDestroy`, `onCreate`, `onStart`, `onResume` — și **niciun** `MovieApp.onCreate` în plus.

**Exersează:** [24.5](cap-24.html#ex-24-5) (rotirea, pas cu pas), [19.6](cap-19.html#ex-19-6) (rotirea nu pierde formularul).

---

## Rețeta 35.13 — Debug: datele nu ajung unde trebuie

**Cerința, cum sună la test:** „Filmul se salvează, dar nu apare în listă. Găsește cauza și explică în ce ordine verifici."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `activities/ItemActivity.java` | `Log.d` înainte de `setResult` | da |
| 2 | `activities/MainActivity.java` | `Log.d` în prima linie a callback-ului | da |
| 3 | `activities/MainActivity.java` | `Log.d` după `add` / `set` cu `movies.size()` | da |
| 4 | orice fișier suspect | **nu** modifici nimic până nu ai cele trei numere | da — disciplină |

**Pașii, în ordine:**

**Pasul 1 — pune trei loguri, în trei locuri.** Nu ghici; măsoară unde se rupe lanțul:

```java
// ItemActivity.saveMovie(), înainte de setResult
Log.d("G1097", "1 saveMovie: position=" + position
        + " title=" + movie.getTitle()
        + " extras=" + intent.getExtras());

// MainActivity.onActivityResult(), prima linie
Log.d("G1097", "2 callback: code=" + o.getResultCode() + " data=" + o.getData());

// MainActivity, după add / set
Log.d("G1097", "3 list: size=" + movies.size());
```

Trei numere, trei întrebări: (1) a plecat ceva din formular? (2) a ajuns ceva în callback? (3) a intrat în listă?

**Pasul 2 — citește rezultatul ca pe un triaj.** Fiecare combinație are o singură cauză plauzibilă:

| Ce vezi în Logcat | Unde s-a rupt | Cauza probabilă |
|---|---|---|
| niciun log `1` | în `ItemActivity` | butonul nu e legat de `saveMovie()`, sau aplicația a crăpat înainte |
| `1` apare, `2` nu | între activități | ai folosit `startActivity` în loc de `launcher.launch`, sau ai uitat `setResult` |
| `2` apare cu `code=0` | rezultatul | `finish()` fără `setResult`, sau `setResult` după `finish` |
| `2` apare cu `code=-1`, `data=null` | `Intent`-ul de rezultat | `setResult(RESULT_OK)` fără `Intent` |
| `2` apare cu `code=-1`, dar `title=null` în `1` | în formular | câmpul era gol; `movie.getTitle()` este `""` |
| `2` apare corect, `3` nu | în callback | excepție înainte de `add`, sau garda `== RESULT_OK` nu trece |
| `3` crește, ecranul nu | adapter | lipsește `notifyDataSetChanged()` |
| `3` crește cu 1, dar lista are un duplicat | poziția | `position` a ajuns `-1` și s-a executat `add` pe ramura de editare |

**Pasul 3 — verifică cele șase cauze reale, în ordinea costului.** Toate apar în codul acestei aplicații:

1. **Cheie diferită.** `"movie"` într-un fișier, `"Movie"` în celălalt. Simptom: `getSerializableExtra` întoarce `null`, fără excepție. Verificare: loghează `intent.getExtras()` și compară cheile cu constantele.
2. **`RESULT_CANCELED` din lipsă de `setResult`.** Simptom: `code=0` în callback. Verificare: `saveMovie()` se termină cu `setResult` **înainte** de `finish()`.
3. **`data == null`.** Simptom: `NullPointerException` pe `o.getData().getSerializableExtra(...)`. Verificare: `if (o.getData() != null)`.
4. **`position == -1` pe editare.** Simptom: duplicat. Cauza: `POSITION_EXTRA` nu a fost pus la dus sau la întors. Verificare: loghează `position` în ambele capete.
5. **Obiectul este o copie.** Simptom: modifici în formular, lista nu se schimbă. Nu este bug — este mecanismul. Verificare: dacă `movies.get(position) != movie` (identitate de referință), ești pe drumul corect.
6. **`notifyDataSetChanged()` lipsă.** Simptom: `movies.size()` crește, ecranul stă pe loc. Verificare: după fiecare mutație a listei, un singur anunț.

**Pasul 4 — izolează cu `Toast`, dacă nu ai Logcat.** Aceeași informație, vizibilă pe ecran:

```java
Toast.makeText(MainActivity.this,
        "code=" + o.getResultCode() + " size=" + movies.size(),
        Toast.LENGTH_LONG).show();
```

La examen, `Toast` este mai rapid decât Logcat-ul, pentru că demonstrezi pe loc, în fața profesorului.

**Pasul 5 — verifică ordinea, nu doar valorile.** Un lanț poate fi corect bucată cu bucată și greșit în ansamblu. Ordinea din `MainActivity.onCreate` este: `addSampleMovies()` → `movieAdapter` → `initControls()` → `initListeners()` → `registerForActivityResult`. Dacă muți `registerForActivityResult` într-un listener, primești `IllegalStateException`; dacă muți `initControls()` după `initListeners()`, listener-ele se leagă de câmpuri `null` și crapă la primul click.

**De ce merge așa:** rezultatul unei activități traversează patru hopuri — `ItemActivity` → `ActivityManager` → registry-ul de rezultate al lui `MainActivity` → callback — iar fiecare hop poate pierde ceva: un cod nesetat, un `Intent` fără cheie, o cheie cu alt nume, o gardă care nu trece. Un singur `Log` la fiecare hop transformă „nu merge" într-o întrebare cu răspuns binar: primul log care lipsește este hopul defect. De aceea triajul începe întotdeauna cu cele trei numere, nu cu cititul codului: codul arată corect chiar și când un string diferă printr-o literă.

**Greșeala care costă puncte:**

1. **Modifici codul înainte să măsori.** Simptom: după trei „reparații" consecutive, bug-ul persistă și ai introdus încă unul. Cauza: ai sărit peste pasul 1. Trei loguri costă un minut; ghicitul costă zece.
2. **Te uiți la `movies.size()` în loc de `movieAdapter.getCount()`.** Simptom: numerele par corecte, dar ecranul e gol. Cauza: adapterul poate să nu fie legat de listă (`setAdapter` lipsă) sau să fie legat de altă instanță. Verifică ambele numere.
3. **Concluzionezi „nu s-a salvat" când de fapt nu s-a reîncărcat.** Simptom: la repornire lista e goală, deși logul `saveMovies: ok=true` apare. Cauza: `loadMovies()` citește alt nume de fișier sau altă cheie decât `saveMovies()`. Verifică perechea `PREFS_NAME` / `KEY_MOVIES_JSON`.

**Verificarea:** provoci intenționat fiecare cauză și confirmi că triajul o prinde. (1) Schimbi cheia la citire, doar în `ItemActivity`: formularul se deschide gol, în mod insert, deși ai atins un rând existent — `existing` este `null`, deci `position` rămâne `-1`. (2) Comentezi `setResult`: logul `2` arată `code=0`. (3) Comentezi `notifyDataSetChanged()`: logul `3` crește, ecranul nu. (4) Comentezi `putExtra(POSITION_EXTRA, position)` din `saveMovie()`: logul `1` arată `position=0`, logul `2` arată `position=-1`, lista face `add` și apare duplicatul. După fiecare, revii la codul corect.

**Exersează:** [24.8](cap-24.html#ex-24-8) (filmul se salvează, dar nu apare în listă — 5 cauze, 5 verificări), [24.9](cap-24.html#ex-24-9) (după editare, filmul apare de două ori).

---

## Tabelul celor 13 rețete

| # | Rețeta | Când o folosești | Mecanismul | Fișiere |
|---|---|---|---|---|
| 35.1 | Pornește o altă activitate | „deschide ecranul de detalii" | `Intent` explicit + `startActivity` | `MainActivity`, manifest |
| 35.2 | Trimite valori simple | „trimite titlul / poziția" | `putExtra` + `getStringExtra` / `getIntExtra` | `MainActivity`, `ItemActivity` |
| 35.3 | Trimite un obiect întreg | „umple formularul cu filmul atins" | `Serializable` + `IntentCompat` | `Movie`, ambele activități |
| 35.4 | Primește un rezultat | „lista se actualizează după Save" | `ActivityResultLauncher` + `registerForActivityResult` | `MainActivity` |
| 35.5 | Returnează un obiect modificat | „editarea înlocuiește rândul" | `setResult(RESULT_OK)` + `movies.set` | `ItemActivity`, `MainActivity` |
| 35.6 | Returnează un cod de rezultat | „șterge filmul" | cod propriu ≥ 1 + ramură în callback | `ItemActivity`, `MainActivity` |
| 35.7 | Intent implicit | „deschide linkul în browser" | `ACTION_VIEW` + `Uri` | `ItemActivity` |
| 35.8 | Back vs `finish()` vs `setResult` | „ce se întoarce când apeși Back" | codul intern, inițial `RESULT_CANCELED` | `ItemActivity` |
| 35.9 | Formularul supraviețuiește rotirii | „rotesc și nu pierd nimic" | `onSaveInstanceState` + `releaseCal` | `ItemActivity` |
| 35.10 | Lista supraviețuiește închiderii | „datele să se salveze" | `SharedPreferences` + JSON manual | `MainActivity` |
| 35.11 | Verifică persistența | „demonstrează că s-a salvat" | `run-as`, `force-stop`, `pm clear` | terminal, `MainActivity` |
| 35.12 | `Application` și ciclul de viață | „explică ordinea metodelor" | `Application` + `ActivityLifecycleCallbacks` | `MovieApp`, manifest |
| 35.13 | Debug: datele nu ajung | „se salvează, dar nu apare" | trei loguri, triaj pe hopuri | ambele activități |

**Cum alegi în 30 de secunde:** dacă cerința spune „trimite" → 35.2 sau 35.3; „returnează" → 35.4, 35.5 sau 35.6; „șterge" → 35.6; „deschide în altă aplicație" → 35.7; „rotire" → 35.9; „repornire" sau „salvează" → 35.10; „explică" → 35.8 sau 35.12; „nu merge" → 35.13.

## Rezumat capitol 35

- **Un `Intent` duce o copie, nu o referință.** `putExtra` serializează, `getSerializableExtra` deserializează. Modificarea formularului nu se vede în listă până la `movies.set(position, movie)`.
- **Cheile sunt contracte.** `MOVIE_EXTRA` și `POSITION_EXTRA` sunt `protected static final` în `MainActivity` tocmai ca să nu difere între fișiere. O literă schimbată dă `null`, nu eroare.
- **Rezultatul are cod și `Intent`.** `setResult` scrie, `finish()` trimite. Codul implicit este `RESULT_CANCELED`; orice cod propriu trebuie să fie cel puțin 1.
- **`position == -1` înseamnă insert, orice altceva înseamnă edit.** `add` crește lista, `set` înlocuiește. Confuzia produce fie un duplicat, fie un film pierdut, fără nicio excepție.
- **Launcher-ul se înregistrează în `onCreate`, într-un câmp.** Nu în listener, nu într-o variabilă locală. `startActivityForResult` este istorie.
- **Rotirea distruge activitatea, nu procesul.** View-urile cu `id` se salvează singure; câmpurile tale nu. `releaseCal` trebuie salvat manual și sincronizat în `fillForm`.
- **Închiderea aplicației distruge procesul.** Doar `SharedPreferences` (sau un fișier, sau Room) supraviețuiește. `onPause` salvează, `onDestroy` nu este garantat.
- **JSON-ul se construiește manual, cu `escape()`.** Fără escape, un titlu cu ghilimele golește lista la următoarea pornire, fără nicio eroare vizibilă.
- **Trei loguri bat orice ghicit.** Ce pleacă din formular, ce ajunge în callback, ce intră în listă — primul care lipsește este hopul defect.

Trei propoziții de memorat:

1. **Datele nu se văd dintr-un ecran în altul; se trimit și se întorc.** Fiecare trecere este o copie, fiecare întoarcere este un cod plus un `Intent`.
2. **RAM-ul nu este persistență, iar rotirea nu este repornire.** `onSaveInstanceState` ține formularul peste o rotire; `SharedPreferences` ține lista peste o repornire. Nu se înlocuiesc una pe alta.
3. **Când ceva nu ajunge unde trebuie, măsoară, nu citi.** Trei `Log.d` în trei locuri arată exact unde s-a rupt lanțul — și de cele mai multe ori locul nu este cel în care te uitai.
