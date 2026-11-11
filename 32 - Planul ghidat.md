# Capitolul 32 — Planul ghidat: de la zero la „pot da testul"

Ai citit capitolele. Ai făcut exerciții. Acum problema nu mai e „ce învăț", ci „în ce ordine, cât timp pe fiecare și cum știu că sunt gata".

Capitolul ăsta e răspunsul: **zece sesiuni, 18 ore, un singur fir**. Fiecare sesiune are un obiectiv, un timp, ce citești, ce exersezi și un test de ieșire. Nu treci mai departe până nu treci testul.

**Ce nu e capitolul ăsta:** nu e o a doua teorie. Nu explică `RecyclerView` și nu repetă rețetele. Trimite la ele și îți spune doar ce să iei din fiecare, în ce ordine și cât timp.

**Cum îl folosești:**

1. O sesiune pe rând, cu cronometrul pornit. Sesiunile au timpi diferiți pentru că au greutăți diferite — nu le egaliza.
2. Citește rubrica „Ești gata când" **înainte** să începi. Pare un detaliu; în realitate e singurul lucru care îți spune dacă ai terminat sau doar ai stat.
3. Dacă nu treci testul de ieșire, nu avansezi. Repeți sesiunea a doua zi. O sesiune repetată costă 2 ore; o fundație lipsă costă tot testul.
4. Bifezi în tabelul de mai jos. Progresul se vede, nu se simte.

**Ce trebuie să existe înainte de sesiunea 1:** proiectul `Movies1097` care compilează și rulează, construit în capitolele [01](cap-01.html)–[11](cap-11.html). Dacă nu îl ai, planul nu are pe ce să se sprijine — întâi aplicația, apoi planul.

**Harta celor zece sesiuni:**

| # | Sesiune | Timp | Ce rămâne după ea | Capitole |
|---|---|---|---|---|
| 1 | Harta | 2 h | știi ce fișier atingi pentru orice cerință | 21, 22 |
| 2 | Modelul | 1,5 h | adaugi un atribut în 8 minute | 33.1–33.6, 17 |
| 3 | Interfața | 1,5 h | pui un widget și un buton cu listener | 33.11–33.16, 20 |
| 4 | Bindingurile | 2 h | legi un widget de o etichetă | 34.1–34.6, 18, 19 |
| 5 | Adaptoarele | 2 h | scrii un adapter de la zero | 34.7–34.9, 18 |
| 6 | RecyclerView | 2,5 h | migrezi lista în 25 de minute | 23, 34.10 |
| 7 | Intent | 2 h | trimiți și primești date între ecrane | 35.1–35.8, 36 |
| 8 | Persistența | 2 h | datele supraviețuiesc rotirii și închiderii | 35.9–35.13, 24 |
| 9 | Simularea | 1,5 h | dai testul în 30 de minute | 17.10, 20.10 |
| 10 | Ziua testului | 1 h | ai planul de 30 de minute | 32.10 |

**Cum arată o sesiune.** Toate au aceleași cinci rubrici, în aceeași ordine:

| Rubrica | Ce îți cere |
|---|---|
| **Obiectiv** | o propoziție: ce trebuie să știi la final |
| **Timp** | cât durează, împărțit pe activități |
| **Citești** | exact ce capitole și secțiuni, nu „materialul" |
| **Exersezi** | exercițiile care fixează lucrul din sesiune |
| **Ești gata când** | un test verificabil, nu o impresie |

> **Regula celor 18 ore:** dacă o sesiune îți ia dublu, nu ești lent — sesiunea dinainte nu s-a lipit. Întoarce-te la ea. Planul e secvențial dinadins: fiecare sesiune folosește ceva construit în precedenta.

---

## 32.0 Cum arată testul

Două cerințe. Treizeci de minute. Aplicația `G1097` la starea din commitul `d719ffc` — exact cea pe care ai construit-o în capitolele 01–11.

Fiecare cerință e o propoziție de forma „Adaugă filmului numele regizorului și afișează-l în listă" sau „Trimite filmul selectat în ecranul de detaliu și returnează poziția". Nu e un proiect: e o modificare localizată, în 2–5 fișiere, care trebuie să compileze și să ruleze la final.

**Anatomia unei cerințe.** „Adaugă filmului `writer` (String) și afișează-l în listă" atinge cinci fișiere: `Movie.java`, `activity_item.xml`, `ItemActivity.java`, `MainActivity.java` (constructorul) și — dacă lista e pe `RecyclerView` — `movie_item.xml` plus adapterul. Sunt șapte editări obligatorii. Dacă știi ordinea, durează 8 minute. Dacă o improvizezi, durează 25 și probabil ratezi una.

**Familiile de cerințe care pot pica:**

| Familia | Cum sună | Unde o înveți | Exerciții |
|---|---|---|---|
| Atribut nou | „adaugă `writer` și afișează-l" | [33.1](cap-33.html#reteta-33-1)–[33.6](cap-33.html#reteta-33-6) | 17.1–17.10 |
| Widget nou | „adaugă un buton / switch / spinner" | [33.11](cap-33.html#reteta-33-11)–[33.16](cap-33.html#reteta-33-16) | 20.1–20.10 |
| Binding | „valoarea din slider să apară în etichetă" | [34.1](cap-34.html#reteta-34-1)–[34.6](cap-34.html#reteta-34-6) | 18.1–18.3, 19.1–19.4 |
| Adapter | „rândul să arate două linii" | [34.7](cap-34.html#reteta-34-7)–[34.9](cap-34.html#reteta-34-9) | 18.4, 18.8 |
| Migrare | „treci lista pe `RecyclerView`" | [23](cap-23.html), [34.10](cap-34.html#reteta-34-10) | 23.1–23.10, 18.5 |
| Intent | „trimite / returnează" | [35.1](cap-35.html#reteta-35-1)–[35.8](cap-35.html#reteta-35-8) | 36.1–36.10 |
| Persistență | „datele să nu se piardă" | [35.9](cap-35.html#reteta-35-9)–[35.13](cap-35.html#reteta-35-13) | 24.5–24.10 |

**Ce înseamnă „rezolvat".** Patru condiții, în ordinea asta:

1. **Compilează.** O eroare de compilare anulează tot restul — la test nu există „aproape".
2. **Rulează.** Aplicația pornește și nu crapă la primul click.
3. **Se vede.** Comportamentul cerut e pe ecran: rândul nou apare, eticheta se schimbă, ecranul se întoarce cu date.
4. **Poți explica.** De ce ai pus linia acolo și nu în altă parte. Fără explicație, cerința e pe jumătate.

**Ce nu se cere.** Aplicația nu are bază de date, rețea, fișiere sau teste automate. Cerințele rămân în interiorul codului pe care îl ai: model, layout-uri, activități, adaptoare, `Intent`.

**Cele două ceasuri.** Din 30 de minute, 5 se duc pe citit și planificat, 22 pe cele două cerințe, 3 pe compilat și rulat. Împărțirea minut cu minut e în secțiunea 32.10. Aici reține un singur lucru: **nicio cerință nu are voie să consume mai mult de 12 minute**. Dacă la minutul 12 nu ai compilat-o, o lași și treci la a doua — altfel pierzi amândouă.

---

## Pasul 32.1 — Sesiunea 1 — Harta

**Obiectiv:** la finalul sesiunii știi, fără să deschizi nimic, ce fișier trebuie atins pentru fiecare tip de cerință.

**Timp:** 2 h — 60 min citit, 30 min scris `Movie.java` pe hârtie, 30 min comparație și corectare.

**Citești:**
- [21](cap-21.html) integral, 30 de minute. Nu îl înveți, îl răsfoiești: 21.1 (harta fișierelor), 21.2 (cum adaugi un atribut), 21.5 (tabelul de listeneri), 21.6 (adaptoare), 21.7 (intents). Restul îl lași pentru sesiunile care au nevoie de el.
- [22](cap-22.html) — doar secțiunile 22.1 (`Movie.java`) și 22.3 (`ItemActivity.java`). Sunt cele două fișiere pe care le atingi în aproape orice cerință.

**Exersezi:**
- Închizi tot: editor, capitole, cheatsheet, telefon. Iei o coală A4 și scrii `Movie.java` din memorie, în 30 de minute: `package`, `implements Serializable`, cele 10 câmpuri cu tipurile lor, constructorul cu 10 parametri, `toString()`.
- Apoi deschizi `cod-final/java/ro/ase/ie/g1097/model/Movie.java` și compari **linie cu linie**. Nu numeri greșelile — notezi care dintre ele te-ar fi costat la test: un tip greșit (`int` în loc de `float`), un câmp uitat, `getWatched()` în loc de `isWatched()`.

**Ești gata când:** poți numi din memorie cele 6 fișiere ale aplicației și ce face fiecare, în mai puțin de 2 minute, fără să te uiți la tabel.

**Cele 6 fișiere și granițele lor:**

| Fișier | Rolul | Ce conține | Ce nu are voie să conțină |
|---|---|---|---|
| `model/Movie.java` | datele | 10 câmpuri, constructor, getteri/setteri, `toString()` | importuri `android.*`, `findViewById` |
| `activities/MainActivity.java` | lista | `List<Movie>`, `ArrayAdapter`, `launcher`, `addSampleMovies()` | logică de formular |
| `activities/ItemActivity.java` | formularul | câmpuri widget, `initControls`, `initListeners`, `fillForm`, `saveMovie` | acces direct la lista din `MainActivity` |
| `res/layout/activity_main.xml` | ecranul listei | `FrameLayout` + `ListView` + FAB | logică |
| `res/layout/activity_item.xml` | formularul | `ScrollView` + 4 carduri + buton | logică |
| `res/layout/movie_item.xml` | rândul de listă | cardul cu `movieTitle`, `movieSubtitle` etc. | — (la `d719ffc` nu e folosit) |

Mai există patru fișiere de context — `AndroidManifest.xml`, `strings.xml`, `themes.xml`, `build.gradle.kts` — dar pe ele le atingi doar la setup, nu în cerințele de test.

> **Capcana sesiunii:** `movie_item.xml` există în proiect, dar `ArrayAdapter` nu îl folosește. Dacă te întrebi „unde se afișează rândul", răspunsul la `d719ffc` e `toString()`, nu XML-ul. Confuzia asta costă puncte la orice cerință care zice „afișează-l în listă": depinde pe ce adapter ești.

---

## Pasul 32.2 — Sesiunea 2 — Modelul

**Obiectiv:** adaugi orice atribut simplu în model — câmp, getter, setter, parametru în constructor, linie în `toString()` — fără să te uiți la vreun exemplu.

**Timp:** 1,5 h — 40 min rețete, 50 min exerciții.

**Citești:**
- [33.1](cap-33.html#reteta-33-1) integral — atributul `String`, rețeta de referință. Toate celelalte sunt variațiuni pe ea.
- [33.2](cap-33.html#reteta-33-2)–[33.6](cap-33.html#reteta-33-6) — doar diferențele: tipul, widget-ul, metoda de citire, ce se întâmplă când valoarea poate fi `null`.

**Exersezi:**
- [17.1](cap-17.html#ex-17-1) — `writer` (String), atributul de referință.
- [17.3](cap-17.html#ex-17-3) — `popular` (boolean), steagul cu valoare implicită.
- [17.5](cap-17.html#ex-17-5) — `actors` (`ArrayList<String>`), lista într-un singur câmp.

**Ești gata când:** adaugi un atribut `String` de la zero, în formular și în listă, în mai puțin de 8 minute, fără să te uiți la niciun capitol.

**Cele 7 puncte — ordinea pe care o repeți până o știi din memorie:**

| # | Unde | Ce pui |
|---|---|---|
| 1 | `Movie.java` | câmpul + getter + setter |
| 2 | `Movie.java` | parametrul în constructor **și** cele 3 apeluri `new Movie(...)` din `addSampleMovies()` |
| 3 | `Movie.java` | linia din `toString()` |
| 4 | `activity_item.xml` | widgetul, cu `android:id` |
| 5 | `ItemActivity.java` | câmpul + `findViewById` în `initControls()` |
| 6 | `ItemActivity.java` | `fillForm()` + `saveMovie()` |
| 7 | `movie_item.xml` + adapter | doar dacă afișezi în rând de `RecyclerView` |

**Tipul dictează widget-ul și metoda de citire:**

| Tip | Widget | Cum citești | Rețeta |
|---|---|---|---|
| `String` | `TextInputEditText` | `getText().toString()` | [33.1](cap-33.html#reteta-33-1) |
| `int` | `SeekBar` | `getProgress()` | [33.2](cap-33.html#reteta-33-2) |
| `Integer` | `EditText` | `Integer.parseInt(...)`, doar după `isEmpty()` | [33.3](cap-33.html#reteta-33-3) |
| `float` / `double` | `RatingBar` / `EditText` | `getRating()` / `Double.parseDouble(...)` | [33.4](cap-33.html#reteta-33-4) |
| `boolean` | `MaterialSwitch` / `CheckBox` | `isChecked()` | [33.5](cap-33.html#reteta-33-5) |
| `ArrayList<String>` | `EditText` | `Arrays.asList(text.split(","))` | [33.6](cap-33.html#reteta-33-6) |

> **Capcana sesiunii:** constructorul are 10 parametri. Când adaugi al 11-lea, cele trei apeluri din `addSampleMovies()` devin invalide simultan. Compilatorul îți dă trei erori pe aceeași linie de semnătură — nu e o eroare, sunt trei. Rezolvi semnătura, apoi toate cele trei apeluri, într-o singură trecere prin fișier.

---

## Pasul 32.3 — Sesiunea 3 — Interfața

**Obiectiv:** pui orice widget într-un layout existent, îi dai un ID, îl legi din cod și îi atașezi un listener, în ordinea corectă.

**Timp:** 1,5 h — 35 min rețete, 45 min exerciții, 10 min recitire.

**Citești:**
- [33.11](cap-33.html#reteta-33-11)–[33.16](cap-33.html#reteta-33-16): widget în formular, widget în rând, buton, control deasupra listei, schimbarea unui widget cu altul, ecran nou.
- [21](cap-21.html), secțiunea 21.3, doar dacă ai uitat convenția de prefixe (`et`, `tv`, `sp`, `sb`, `rb`, `rg`, `cb`, `sw`, `btn`, `fab`).

**Exersezi:**
- [20.1](cap-20.html#ex-20-1) — butonul „Clear form" sub „Save Movie".
- [20.3](cap-20.html#ex-20-3) — butonul „Delete" din `ItemActivity`, cu cod de rezultat propriu.

**Ești gata când:** adaugi un buton cu listener în 5 minute, cronometrat, de la tag-ul din XML până la `setOnClickListener`.

**Rețeta butonului, în 4 pași — o știi din memorie sau o recitești:**

```xml
<!-- 1. activity_item.xml, după btnMovieAction -->
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnClear"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:text="Clear form" />
```

```java
// 2. câmpul clasei
private Button btnClear;

// 3. initControls()
btnClear = findViewById(R.id.btnClear);

// 4. initListeners()
btnClear.setOnClickListener(v -> { /* ce face butonul */ });
```

**Unde se pune fiecare control:**

| Cerința zice | Unde intri | Ce atingi |
|---|---|---|
| „în formular" | `activity_item.xml` | un card existent, la sfârșitul lui |
| „deasupra listei" | `activity_main.xml` | între `FrameLayout` și `ListView`, sau în `FrameLayout` cu `layout_gravity="top"` |
| „în rândul listei" | `movie_item.xml` | cardul rândului + adapterul |
| „un ecran nou" | fișier nou `activity_*.xml` + clasă + manifest | trei locuri, nu unul |

> **Capcana sesiunii:** `findViewById` întoarce `null` dacă e chemat înainte de `setContentView`, dar și dacă ID-ul există în alt layout. Prima variantă dă `NullPointerException` la primul click; a doua, la fel, dar numai pe ecranul greșit. Ambele se rezolvă la fel: verifici că ID-ul e în layout-ul pe care l-ai setat.

---

## Pasul 32.4 — Sesiunea 4 — Bindingurile

**Obiectiv:** legi orice widget de orice etichetă — în timp real, la inițializare — și citești widget-ul în model la salvare.

**Timp:** 2 h — 50 min rețete, 60 min exerciții, 10 min recitire.

**Citești:**
- [34.1](cap-34.html#reteta-34-1)–[34.6](cap-34.html#reteta-34-6): valoare în etichetă live, valoare la inițializare, citire în model, vizibilitate condiționată, validare, sincronizare între două widget-uri.

**Exersezi:**
- [18.1](cap-18.html#ex-18-1) — `tvDurationValue` legat de `SeekBar`.
- [18.2](cap-18.html#ex-18-2) — `etBudget` devine `SeekBar` (0–500 milioane, pas 1 milion).
- [19.1](cap-19.html#ex-19-1) — `tvWatchedValue` urmărește switch-ul.

**Ești gata când:** legi un `SeekBar` de un `TextView` fără să te uiți la nimic — cele trei metode, în ordine, în 4 minute.

**Câte metode are listener-ul — asta decide stilul:**

| Widget | Metode de implementat | Stil |
|---|---|---|
| `Button` | 1 (`onClick`) | lambda |
| `Switch`, `CheckBox`, `RadioButton` | 1 (`onCheckedChanged`) | lambda |
| `RatingBar` | 1 (`onRatingChanged`) | lambda |
| `RadioGroup` | 1 (`onCheckedChanged(group, checkedId)`) | lambda |
| `SeekBar` | **3** | clasă anonimă |
| `EditText` | **3** (`before` / `on` / `after`) | clasă anonimă |

**Regula:** o singură metodă abstractă = interfață funcțională = lambda permisă. Trei metode = clasă anonimă, fără discuție.

```java
// SeekBar: trei metode, două goale
sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }
    @Override public void onStartTrackingTouch(SeekBar seekBar) { }
    @Override public void onStopTrackingTouch(SeekBar seekBar) { }
});
```

> **Capcana sesiunii:** listener-ul nu se declanșează când setezi valoarea din cod. `sbDuration.setProgress(148)` nu cheamă `onProgressChanged`, deci eticheta rămâne goală până când utilizatorul atinge slider-ul. Soluția e rețeta [34.2](cap-34.html#reteta-34-2): apelezi aceeași logică și în `onCreate`, după `initControls()`.

---

## Pasul 32.5 — Sesiunea 5 — Adaptoarele

**Obiectiv:** alegi adapterul potrivit pentru cerință și îl scrii de la zero, cu `ViewHolder`, fără să copiezi din capitol.

**Timp:** 2 h — 50 min rețete, 60 min exerciții, 10 min recitire.

**Citești:**
- [34.7](cap-34.html#reteta-34-7) — `ArrayAdapter` cu `toString()`.
- [34.8](cap-34.html#reteta-34-8) — `BaseAdapter` cu `ViewHolder` pentru `ListView`.
- [34.9](cap-34.html#reteta-34-9) — `RecyclerView.Adapter` de la zero.

**Exersezi:**
- [18.4](cap-18.html#ex-18-4) — a doua linie în rândul de `ListView`, cu `BaseAdapter` propriu.
- [18.8](cap-18.html#ex-18-8) — rândul arată `Inception (2010)`: `toString()` sau adapter propriu?

**Ești gata când:** scrii cele trei metode ale unui `RecyclerView.Adapter` din memorie, în 6 minute, cu `ViewHolder` inclus și fără compiler.

**Arborele de decizie:**

```
Rândul are UN singur text?
├── da  → ArrayAdapter + toString()            (34.7)
└── nu  → adapter propriu
          ├── pe ListView      → BaseAdapter + getView() + ViewHolder + setTag   (34.8)
          └── pe RecyclerView  → onCreateViewHolder / onBindViewHolder / getItemCount  (34.9)
```

**Corespondența dintre cele două adaptoare proprii:**

| `BaseAdapter` | `RecyclerView.Adapter` | Când rulează |
|---|---|---|
| `getCount()` | `getItemCount()` | la nevoie |
| `getView()`, partea `if (convertView == null)` | `onCreateViewHolder()` | o dată per rând creat |
| `getView()`, partea de `setText` | `onBindViewHolder()` | la fiecare afișare |
| `ViewHolder` + `setTag` / `getTag` manual | `RecyclerView.ViewHolder` automat | — |

**Cele trei metode, scheletul pe care îl scrii din memorie:**

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
}
```

> **Capcana sesiunii:** `notifyDataSetChanged()` se cheamă **după** ce ai modificat lista, niciodată înainte. Invers, adapterul numără vechea dimensiune și fie nu afișează rândul nou, fie aruncă `IndexOutOfBoundsException` la scroll. Ordinea e: `movies.add(...)`, apoi `notifyDataSetChanged()`.
## Pasul 32.6 — Sesiunea 6 — RecyclerView

**Obiectiv:** migrezi lista din `ListView` în `RecyclerView` în 25 de minute, fără să citești nimic în timpul migrării.

**Timp:** 2,5 h — 60 min capitolul 23, 30 min rețeta 34.10, 60 min migrarea cronometrată plus refacerea.

**Citești:**
- [23](cap-23.html) integral. Cele 10 exerciții **sunt** cei 10 pași ai migrării, în ordinea în care fiecare pas compilează.
- [34.10](cap-34.html#reteta-34-10) după capitol, ca recapitulare condensată a aceleiași migrări.

**Exersezi:**
- [18.5](cap-18.html#ex-18-5) — `ListView` → `RecyclerView`, răspunsul complet de examen.

**Ești gata când:** faci migrarea completă, de la `ListView` la `RecyclerView`, în 25 de minute, cu aplicația care rulează la final.

**Cei 10 pași, cu fișierul fiecăruia:**

| # | Pasul | Fișier | Ce se schimbă |
|---|---|---|---|
| 1 | dependența | `build.gradle.kts` | `androidx.recyclerview:recyclerview` |
| 2 | layout-ul | `activity_main.xml` | `ListView` → `RecyclerView`, cu ID nou |
| 3 | adapterul | `MovieAdapter.java` (nou) | cele trei metode obligatorii |
| 4 | `ViewHolder` | `MovieAdapter.java` | câmpurile din `movie_item.xml` |
| 5 | `onCreateViewHolder` | `MovieAdapter.java` | `inflate` + `new MovieViewHolder(view)` |
| 6 | `onBindViewHolder` | `MovieAdapter.java` | titlu + subtitlu (gen · an) |
| 7 | rating | `MovieAdapter.java` | `movieRating` + `movieRatingValue` |
| 8 | chips-uri | `MovieAdapter.java` | `movieFacts` + `setVisibility` |
| 9 | click pe rând | `MovieAdapter.java` | `getBindingAdapterPosition()` + callback |
| 10 | `MainActivity` | `MainActivity.java` | `LayoutManager`, `setAdapter`, `notifyItem*` |

**Planul celor 25 de minute:**

| Minut | Ce faci |
|---|---|
| 0–5 | `activity_main.xml`: înlocuiești `ListView` cu `RecyclerView` |
| 5–15 | `MovieAdapter`: clasa, `ViewHolder`, `onCreateViewHolder`, `getItemCount` |
| 15–20 | `onBindViewHolder`: legi câmpurile reale din `movie_item.xml` |
| 20–25 | `MainActivity`: `setLayoutManager`, `setAdapter`, `notifyItemInserted` / `notifyItemChanged` |

> **Capcana sesiunii:** un `RecyclerView` gol, fără nicio eroare în Logcat, are aproape întotdeauna aceeași cauză — ai uitat `setLayoutManager(...)`. Fără el, `RecyclerView` nu știe cum să aranjeze rândurile și nu desenează nimic. A doua cauză, la fel de tăcută: `getItemCount()` întoarce `0` pentru că ai legat adapterul de altă listă decât cea în care adaugi.

---

## Pasul 32.7 — Sesiunea 7 — Intent

**Obiectiv:** trimiți și primești date între cele două ecrane, în ambele sensuri, cu cod de rezultat, fără să ghicești numele constantei sau al metodei.

**Timp:** 2 h — 50 min rețete, 60 min exerciții, 10 min recitire.

**Citești:**
- [35.1](cap-35.html#reteta-35-1)–[35.8](cap-35.html#reteta-35-8): pornirea unei activități, extra simple, obiect întreg, primirea rezultatului, returnarea unui obiect modificat, cod de rezultat propriu, `Intent` implicit, Back vs. `finish()`.

**Exersezi — bancul 7:**
- [36.1](cap-36.html#ex-36-1) — un `String` trimis și afișat în titlul ecranului.
- [36.3](cap-36.html#ex-36-3) — un `boolean` „salvat" întors în `MainActivity`.
- [36.5](cap-36.html#ex-36-5) — ștergerea unui film, cu poziția trimisă înapoi.
- [36.7](cap-36.html#ex-36-7) — un `Movie` nou, fără poziție (insert).

**Ești gata când:** explici, în două propoziții fiecare, de ce obiectul primit în `ItemActivity` e o copie și de ce `setResult` trebuie chemat înainte de `finish()`.

**Cele două sensuri, într-o singură imagine:**

```
MainActivity                                  ItemActivity
    |  Intent explicit                          |
    |  putExtra(MOVIE_EXTRA, movie)  -------->  |  getIntent()
    |  putExtra(POSITION_EXTRA, 0)              |  IntentCompat.getSerializableExtra(...)
    |  launcher.launch(intent)                  |  fillForm(existing)
    |                                           |
    |  <------- setResult(RESULT_OK, intent)    |
    |           finish()                        |
    v
callback: getResultCode()  →  CE s-a întâmplat
          getData()        →  CU CE
```

**Tabelul metodelor, pe sensuri:**

| Direcție | Metodă | Unde | Cine o citește |
|---|---|---|---|
| dus | `putExtra(CHEIE, "text")` | `MainActivity`, la `launch` | `getStringExtra(CHEIE)` |
| dus | `putExtra(CHEIE, 3)` | `MainActivity`, la `launch` | `getIntExtra(CHEIE, -1)` |
| dus | `putExtra(CHEIE, movie)` | `MainActivity`, click pe rând | `IntentCompat.getSerializableExtra(...)` |
| întors | `setResult(RESULT_OK, intent)` | `ItemActivity.saveMovie()` | `getResultCode()` + `getData()` |
| lansare | `launcher.launch(intent)` | `MainActivity` | — |
| înregistrare | `registerForActivityResult(...)` | `MainActivity.onCreate()` | — |

**Cele patru capcane, în ordinea în care te lovesc:**

1. **Obiectul primit e o copie.** `Intent` serializează obiectul la dus și îl deserializează la întors. Modifici copia, nu originalul — de aceea editarea nu se face direct pe lista din `MainActivity`, ci prin `setResult`.
2. **`setResult` înainte de `finish()`.** Invers, `finish()` închide activitatea și `setResult` nu mai ajunge nicăieri; părintele primește `RESULT_CANCELED`.
3. **Cheia scrisă de două ori.** `"movie"` într-un loc și `"Movie"` în altul → `null`, fără nicio eroare. De aceea `MOVIE_EXTRA` și `POSITION_EXTRA` sunt constante în `MainActivity`.
4. **Poziția trimisă la insert.** `POSITION_EXTRA` lipsă înseamnă `-1` la `getIntExtra`, adică „adaugă". Dacă trimiți `0` la un film nou, `MainActivity` intră pe ramura de editare și înlocuiește primul film din listă.

> **Capcana sesiunii:** `registerForActivityResult` se cheamă în `onCreate`, nu într-un listener. Mutat într-un `onClick`, aruncă `IllegalStateException` la primul click, pentru că înregistrarea trebuie făcută în timpul construirii activității.

---

## Pasul 32.8 — Sesiunea 8 — Persistența

**Obiectiv:** datele supraviețuiesc rotirii ecranului și închiderii aplicației, iar tu știi exact care mecanism acoperă care caz.

**Timp:** 2 h — 50 min rețete, 60 min exerciții, 10 min recitire.

**Citești:**
- [35.9](cap-35.html#reteta-35-9)–[35.13](cap-35.html#reteta-35-13): rotirea, `SharedPreferences` cu JSON construit manual, verificarea că s-a salvat, clasa `Application`, debug-ul pierderii de date.

**Exersezi:**
- [24.6](cap-24.html#ex-24-6) — persistență reală: lista se pierde la închidere, `SharedPreferences` + JSON.
- [24.7](cap-24.html#ex-24-7) — checklist-ul de după fiecare „adaugă un atribut": 6 verificări.

**Ești gata când:** salvezi lista în `SharedPreferences` la fiecare modificare și o citești la pornire, iar după rotire formularul e intact.

**Ce supraviețuiește la ce:**

| Eveniment | `onSaveInstanceState` | `SharedPreferences` | `Application` |
|---|---|---|---|
| rotirea ecranului | da | da | da |
| Home, apoi revenire | da | da | da |
| sistemul omoară procesul în fundal | da, prin `Bundle` | da | **nu** |
| utilizatorul închide aplicația | **nu** | da | **nu** |

**JSON construit manual — ce trebuie să știi să scrii:**

```java
// salvare, în MainActivity, după fiecare add / set
JSONArray array = new JSONArray();
for (Movie movie : movies) {
    JSONObject obj = new JSONObject();
    try {
        obj.put("title", movie.getTitle());
        obj.put("genre", movie.getGenre());
        obj.put("duration", movie.getDuration());
        obj.put("rating", movie.getRating());
        array.put(obj);
    } catch (JSONException e) {
        e.printStackTrace();
    }
}
getSharedPreferences("movies", MODE_PRIVATE).edit()
        .putString("list", array.toString())
        .apply();
```

La citire faci drumul invers: `getString("list", "[]")` → `new JSONArray(json)` → pentru fiecare element `new Movie()` + setteri + `movies.add(...)`.

**Cele 6 verificări din 24.7, pe scurt:** câmpul există în model · apare în formular · se umple la editare · se salvează · se vede în listă · se vede și după rotire.

> **Capcana sesiunii:** `onSaveInstanceState` salvează **starea widget-urilor**, nu lista de filme. Dacă vrei ca filmele adăugate să nu dispară la închidere, ai nevoie de `SharedPreferences`. Sunt două probleme diferite și se rezolvă în două locuri diferite.

---

## Pasul 32.9 — Sesiunea 9 — Simularea

**Obiectiv:** să lucrezi 30 de minute în condiții de test și să știi exact unde pierzi timp, nu unde crezi că pierzi.

**Timp:** 1,5 h — 30 min simulare, 15 min corectare, 45 min refacere.

**Citești:**
- Nimic. Doar enunțurile celor două exerciții, o singură dată, la început. Dacă deschizi un capitol, simularea nu mai valorează nimic.

**Exersezi:**
- [17.10](cap-17.html#ex-17-10) — `writer` + `popular`: cele două cerințe, în 30 de minute.
- [20.10](cap-20.html#ex-20-10) — combinația de examen: butonul „Duplicate movie".

**Ești gata când:** termini ambele cerințe în 30 de minute, cu aplicația care rulează, fără să deschizi niciun capitol și fără să te uiți la soluție.

**Protocolul, exact așa:**

1. Pornești cronometrul pe 30 de minute. Nu îl oprești, nu îl dai înapoi.
2. Citești ambele enunțuri integral, o dată, fără să scrii nimic.
3. Lucrezi. Soluțiile sunt pliate în fișiere — nu le deschizi sub nicio formă.
4. La minutul 30 te oprești, indiferent unde ești. Notezi unde erai.
5. Abia acum deschizi soluțiile și corectezi.

**Grila de punctaj — o aplici singur:**

| Criteriu | Puncte |
|---|---|
| compilează | 1 |
| rulează | 1 |
| cerința 1 se vede pe ecran | 2 |
| cerința 2 se vede pe ecran | 2 |
| poți explica fiecare linie adăugată | 2 |
| ai terminat în 30 de minute | 2 |

Sub 7 din 10: nu ești gata. Notează **ce** te-a încetinit — nu „am fost lent", ci „am pierdut 6 minute căutând `fillForm`" sau „am uitat al treilea apel din `addSampleMovies()`". Fiecare întârziere concretă are o rețetă în tabelul din 32.12.

**Apoi recitești ce ai greșit:** deschizi rețeta exactă a lucrului care te-a blocat, o citești o dată, apoi refaci exercițiul de la zero, cronometrat. A doua oară trebuie să intri sub 20 de minute.

> **Capcana sesiunii:** tentația de a „verifica o secundă" soluția. O secundă costă toată simularea — pentru că de la ea încolo nu mai știi dacă ai rezolvat singur sau ai recunoscut răspunsul.

---

## Pasul 32.10 — Sesiunea 10 — Ziua testului

**Obiectiv:** ai un plan de 30 de minute și știi exact ce recitești în ora dinainte, ca să nu intri în test cu capul în material.

**Timp:** 1 h — 40 min recitire, 20 min repetat cu voce tare.

**Citești:**
- Cele 7 puncte și cei 10 pași de mai jos. Nimic altceva. Nu deschizi capitole, nu deschizi exerciții rezolvate.

**Exersezi:**
- Spui cu voce tare, fără să te uiți: cele 7 puncte, cei 10 pași ai migrării, tabelul de erori din 32.12.

**Ești gata când:** spui cele 7 puncte în ordine în 90 de secunde și cei 10 pași în 3 minute, fără să te oprești.

**Ce recitești — cele 7 puncte ale adăugării unui atribut:**

| # | Unde | Ce pui |
|---|---|---|
| 1 | `Movie.java` | câmp + getter + setter |
| 2 | `Movie.java` | parametru în constructor + cele 3 apeluri din `addSampleMovies()` |
| 3 | `Movie.java` | linia din `toString()` |
| 4 | `activity_item.xml` | widgetul, cu ID |
| 5 | `ItemActivity.java` | câmp + `findViewById` în `initControls()` |
| 6 | `ItemActivity.java` | `fillForm()` + `saveMovie()` |
| 7 | `movie_item.xml` + adapter | doar pe `RecyclerView` |

**Ce recitești — cei 10 pași ai migrării:** dependența · layout-ul · adapterul · `ViewHolder` · `onCreateViewHolder` · `onBindViewHolder` · rating · chips-uri · click · `MainActivity`.

**Ce NU recitești:**

- Cod cuvânt cu cuvânt. `toString()` nu se memorează — se generează cu Alt+Insert în 5 secunde.
- Capitolele 01–16. Setup, layout-uri, istoricul repo-ului — nu pică la test.
- Teoria ciclului de viață. Reții doar patru lucruri: `onCreate` construiește, `onSaveInstanceState` salvează, `setResult` raportează, `finish()` închide.
- Exercițiile rezolvate. Recitirea soluțiilor înainte de test îți dă senzația de siguranță fără să îți dea și capacitatea.

**Primele 5 minute din test:**

| Minut | Ce faci |
|---|---|
| 0–1 | citești ambele cerințe integral, fără să scrii nimic |
| 1–2 | notezi pe colț fișierele atinse de fiecare cerință |
| 2–3 | decizi ordinea: prima e cerința care atinge `Movie.java`, pentru că schimbă constructorul |
| 3–5 | deschizi fișierele în ordinea stabilită și nu le mai închizi |

**Cum împarți cele 30 de minute:**

| Minut | Ce faci |
|---|---|
| 0–5 | citit + plan |
| 5–17 | cerința 1, completă, până la compilare |
| 17–27 | cerința 2 |
| 27–30 | compilezi, rulezi, repari ce se vede pe ecran |

> **Regula de la minutul 27:** dacă nu compilează, comentezi ultima modificare — nu toată cerința. O cerință care compilează pe jumătate ia mai multe puncte decât una care nu compilează deloc. Și niciodată nu pleci din test cu un fișier în care ai lăsat o eroare de sintaxă: aceea anulează și partea care funcționa.

---

## 32.11 Dacă ai mai puțin timp

Trei variante, de la „am un weekend" la „am două ore înainte de test". Fiecare spune și ce riști.

**3 zile (~9 h):** faci sesiunile **2, 4, 6, 7, 9** — sari peste 1, 3, 5, 8, 10.

| Ce tai | Ce riști |
|---|---|
| harta (1), interfața (3), adaptoarele proprii (5), persistența (8), ziua testului (10) | dacă pică un `BaseAdapter` propriu sau `SharedPreferences`, improvizezi; fără sesiunea 1 pierzi timp la test căutând fișierul |

Acoperă: atribut nou, binding, migrare `RecyclerView`, `Intent`, simulare. E exact miezul testului.

**1 zi (~5 h):** rețetele [33.1](cap-33.html#reteta-33-1)–[33.5](cap-33.html#reteta-33-5), [34.1](cap-34.html#reteta-34-1), [34.10](cap-34.html#reteta-34-10), [35.1](cap-35.html#reteta-35-1)–[35.5](cap-35.html#reteta-35-5), apoi simularea [17.10](cap-17.html#ex-17-10).

| Ce tai | Ce riști |
|---|---|
| adaptoarele proprii (34.8, 34.9), persistența (35.9–35.13), widget-urile noi (33.11–33.16) | o cerință cu `SharedPreferences` sau cu al doilea `TextView` în rând rămâne nerezolvată |

**2 ore:** doar rețetele [33.1](cap-33.html#reteta-33-1), [34.10](cap-34.html#reteta-34-10), [35.1](cap-35.html#reteta-35-1) și simularea [17.10](cap-17.html#ex-17-10).

| Ce tai | Ce riști |
|---|---|
| tot restul | acoperi doar atributul simplu, migrarea și un `Intent` de bază — dar acoperi bine exact trei lucruri care pică des |

> **Alegerea care contează:** dacă ai timp doar pentru o singură rețetă, e [33.1](cap-33.html#reteta-33-1). Atinge cinci fișiere și apare în aproape orice cerință compusă.

---

## 32.12 Dacă ai greșit ceva

Tabelul de diagnostic. Te uiți la simptom, nu la cod — codul îl citești după.

| Simptom | Cauza probabilă | Rețeta |
|---|---|---|
| Am adăugat atributul, dar nu apare în listă | nu ai atins `movie_item.xml` + adapterul | [33.12](cap-33.html#reteta-33-12) |
| La editare valoarea se pierde | ai uitat `fillForm` (sau linia câmpului din el) | [34.2](cap-34.html#reteta-34-2)–[34.3](cap-34.html#reteta-34-3) |
| Lista nu se actualizează după salvare | ai uitat `notifyDataSetChanged()` | [34.14](cap-34.html#reteta-34-14) |
| `RecyclerView` apare gol, fără eroare | ai uitat `setLayoutManager` | [34.10](cap-34.html#reteta-34-10) |
| Aplicația crapă la Save | `Double.parseDouble` pe câmp gol | [33.4](cap-33.html#reteta-33-4) |
| Se întoarce `RESULT_CANCELED` | ai uitat `setResult` înainte de `finish()` | [35.5](cap-35.html#reteta-35-5) |
| Datele dispar la rotire | ai uitat `onSaveInstanceState` | [35.9](cap-35.html#reteta-35-9) |
| Filmul editat apare de două ori | `movies.add(...)` în loc de `movies.set(position, ...)` | [35.5](cap-35.html#reteta-35-5) |
| Câmpul nou e `null` în toate rândurile demo | ai uitat parametrul în constructor sau unul din cele 3 apeluri | [33.1](cap-33.html#reteta-33-1) |
| Eticheta se actualizează doar când miști widget-ul | listener-ul nu se declanșează la valoarea setată din cod | [34.2](cap-34.html#reteta-34-2) |
| După rotire, `Spinner` revine la prima opțiune | `onSaveInstanceState` nu salvează selecția | [35.9](cap-35.html#reteta-35-9) |
| Butonul nou nu reacționează la click | `findViewById` pe alt ID sau listener pus înainte de `setContentView` | [33.13](cap-33.html#reteta-33-13) |

**Cum îl folosești:** nu cauți simptomul „apropiat". Cauți exact ce vezi pe ecran sau în Logcat. Dacă simptomul nu e în tabel, regula generală e: întâi compilarea, apoi legătura dintre XML și cod (`findViewById`), apoi legătura dintre cod și model (`saveMovie` / `fillForm`), apoi notificarea listei.

---

## 32.13 Cele 10 operații de bază

La test nu ți se cere „adaugă un atribut" în abstract. Ți se cere o **operație concretă**: „adaugă regizorul", „pune un buton de ștergere", „fă ca durata să se vadă sub slider". Toate se reduc însă la zece operații. Dacă le știi pe acestea, știi tot ce poate pica.

| # | Operația | Cum sună la test | Rețeta | Sesiunea | Exersează |
|---|---|---|---|---|---|
| 1 | **Adaugă un câmp filmului** | „adaugă regizorul / anul / genul / o listă de actori" | [33.1](cap-33.html#reteta-33-1)–[33.6](cap-33.html#reteta-33-6) | 2 | [17.1](cap-17.html#ex-17-1), [17.3](cap-17.html#ex-17-3), [17.5](cap-17.html#ex-17-5) |
| 2 | **Adaugă un câmp compus** | „adaugă o listă de actori, fiecare cu nume și rol" | [33.7](cap-33.html#reteta-33-7) | 2 | [17.9](cap-17.html#ex-17-9) |
| 3 | **Adaugă un buton** | „pune un buton Clear form sub Save" | [33.13](cap-33.html#reteta-33-13) | 3 | [20.1](cap-20.html#ex-20-1) |
| 4 | **Atașează un eveniment** | „când apeși butonul, să se întâmple X" | [34.15](cap-34.html#reteta-34-15) | 3–4 | [20.1](cap-20.html#ex-20-1), [18.1](cap-18.html#ex-18-1) |
| 5 | **Șterge un film** | „buton Delete în ecranul de detalii" | [35.6](cap-35.html#reteta-35-6) | 7 | [36.5](cap-36.html#ex-36-5) |
| 6 | **Leagă o valoare de o etichetă** | „durata să apară sub slider, în timp real" | [34.1](cap-34.html#reteta-34-1) | 4 | [18.1](cap-18.html#ex-18-1), [19.1](cap-19.html#ex-19-1) |
| 7 | **Schimbă un widget** | „bugetul din EditText în SeekBar" | [33.15](cap-33.html#reteta-33-15) | 3 | [18.2](cap-18.html#ex-18-2) |
| 8 | **Migrează la RecyclerView** | „lista din ListView în RecyclerView" | [34.10](cap-34.html#reteta-34-10) | 6 | [18.5](cap-18.html#ex-18-5) |
| 9 | **Trimite date prin Intent** | „trimite filmul în ecranul de detalii" | [35.2](cap-35.html#reteta-35-2), [35.3](cap-35.html#reteta-35-3) | 7 | [36.1](cap-36.html#ex-36-1), [36.7](cap-36.html#ex-36-7) |
| 10 | **Persistă lista** | „datele să se salveze după închidere" | [35.10](cap-35.html#reteta-35-10) | 8 | [24.6](cap-24.html#ex-24-6) |

### Cum le exersezi: pe perechi, cum vin la test

Testul dă **două** cerințe. De aceea nu exersezi operațiile separat, ci în perechi — exact combinațiile care apar:

1. **Câmp + afișare** — operațiile 1 și 6. „Adaugă regizorul și arată-l în listă."
2. **Buton + eveniment** — 3 și 4. „Pune un buton care golește formularul."
3. **Buton + ștergere** — 3 și 5. „Pune un buton care șterge filmul."
4. **Câmp + Intent** — 1 și 9. „Adaugă un câmp și trimite-l în ecranul de detalii."
5. **Migrare + afișare** — 8 și 6. „Treci pe RecyclerView și arată durata în rând."

Fiecare pereche se face în **30 de minute, cu cronometru, fără soluție**. Cinci perechi, cinci simulări — și ai acoperit tot ce poate pica.

### Ce faci în primele 5 minute din test

1. Citește ambele cerințe o dată, complet, înainte să deschizi vreun fișier.
2. Notează pe hârtie **fișierele** atinse de fiecare cerință. Dacă îți ies mai mult de trei pe cerință, n-ai înțeles cerința — recitește.
3. Începe cu cerința care atinge **modelul** (`Movie.java`), pentru că a doua o poate folosi.
4. Dacă una dintre cerințe e „migrare la RecyclerView", începe cu **cealaltă**: migrarea mănâncă 20 din cele 30 de minute.
5. Lasă 3 minute la final pentru: rulat aplicația, adăugat un film, editat un film.

---

## Rezumat capitol 32

**Ce ai parcurs:** zece sesiuni, 18 ore, de la „știu ce fișiere are aplicația" la „dau testul în 30 de minute".

| # | Sesiune | Timp | Testul de ieșire |
|---|---|---|---|
| 1 | Harta | 2 h | numeri cele 6 fișiere și rolul lor în 2 minute |
| 2 | Modelul | 1,5 h | atribut `String` complet în sub 8 minute |
| 3 | Interfața | 1,5 h | buton cu listener în 5 minute |
| 4 | Bindingurile | 2 h | `SeekBar` → `TextView` fără să te uiți |
| 5 | Adaptoarele | 2 h | cele trei metode ale `RecyclerView.Adapter` din memorie |
| 6 | RecyclerView | 2,5 h | migrarea completă în 25 de minute |
| 7 | Intent | 2 h | explici copia și ordinea `setResult` / `finish()` |
| 8 | Persistența | 2 h | listă salvată în `SharedPreferences` și citită la pornire |
| 9 | Simularea | 1,5 h | două cerințe în 30 de minute, fără material |
| 10 | Ziua testului | 1 h | cele 7 puncte în 90 de secunde |

**Trei lucruri pe care le iei cu tine:**

1. **Ordinea, nu memoria.** Nu trebuie să știi codul pe de rost; trebuie să știi în ce fișier intri primul. Modelul întâi, apoi XML-ul, apoi `findViewById`, apoi `fillForm` / `saveMovie`, apoi notificarea.
2. **Testul de ieșire, nu sentimentul.** „Am înțeles" nu e un criteriu. „Pot scrie din memorie în 8 minute" este.
3. **Tabelul de diagnostic.** Când ceva nu merge, simptomul îți spune rețeta. Nu citești tot capitolul ca să găsești o linie.

**Ce urmează:** dacă ai trecut toate cele zece teste de ieșire, nu mai ai ce citi — ai de făcut. Reia [17.10](cap-17.html#ex-17-10) și [20.10](cap-20.html#ex-20-10) până intri sub 25 de minute, apoi oprește-te. Odihna dinaintea testului face mai mult decât a douăzeci și unulea exercițiu.
