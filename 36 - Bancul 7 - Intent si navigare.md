# Capitolul 36 — Bancul 7: Intent și navigare

**Obiectiv:** să stăpânești ambele sensuri ale unui `Intent` — dus (ce trimiți când deschizi un ecran) și întors (ce raportezi când îl închizi) — încât orice cerință de tip „trimite", „returnează", „deschide" să se rezolve în 10–15 minute, fără să ghicești numele constantei sau al metodei.

**Cum arată cerința la examen:** „Trimiteți filmul selectat în ecranul de detaliu și returnați poziția." Două propoziții, trei lucruri de făcut: un `putExtra` la dus, un `setResult` la întors și o ramură în callback. Restul capitolului e variațiuni pe aceeași temă.

**Cele două sensuri, într-o singură imagine:**

```
MainActivity                              ItemActivity
    |                                          |
    |  Intent explicit                         |
    |  putExtra(MOVIE_EXTRA, movie)   -------> |  getIntent()
    |  putExtra(POSITION_EXTRA, 0)             |  getSerializableExtra(...)
    |  launcher.launch(intent)                 |  getIntExtra(..., -1)
    |                                          |
    |  <------- setResult(RESULT_OK, intent)   |
    |           finish()                       |
    v
callback(ActivityResult)
    getResultCode()  -> CE s-a întâmplat
    getData()        -> CU CE
```

**Trei lucruri pe care le greșește aproape toată lumea:**

| Greșeala | Efectul | Unde apare |
|---|---|---|
| Uiți `setResult` | părintele primește `RESULT_CANCELED` și ignoră tot | 36.3, 36.5 |
| Trimiți `MOVIE_EXTRA` fără `POSITION_EXTRA` la insert | `ItemActivity` intră în modul edit cu un obiect gol → `NullPointerException` în `fillForm` | 36.7 |
| Faci `movies.add(movie)` la editare | filmul apare de două ori, originalul rămâne neschimbat | 36.8 |

**Codurile de rezultat — tabelul pe care îl reții:**

| Constantă | Valoare | Cine o pune | Ce înseamnă |
|---|---|---|---|
| `RESULT_OK` | `-1` | `ItemActivity.saveMovie()` | „am salvat, uită-te la `Intent`" |
| `RESULT_CANCELED` | `0` | sistemul, când apeși Back | „nu s-a întâmplat nimic" |
| `RESULT_FIRST_USER` | `1` | tu | primul cod propriu disponibil |
| `RESULT_DRAFT` | `2` | 36.4 | „am salvat o ciornă" |
| `RESULT_DELETE` | `3` | 36.5 | „șterge rândul de la poziția asta" |

> Regula: orice cod propriu trebuie să fie **≥ 1**. `0` este deja `RESULT_CANCELED`, iar `-1` este `RESULT_OK`. Un cod de `0` ar fi interpretat ca „utilizatorul a apăsat Back".

**Ce este deja în cod la `d719ffc`** — nu inventăm nimic, pornim de aici:

- `MainActivity` are `protected static final String POSITION_EXTRA = "position";` și `MOVIE_EXTRA = "movie";`
- `MainActivity` are `private ActivityResultLauncher<Intent> launcher;`, înregistrat cu `registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), callback)` la **finalul** lui `onCreate`
- `ItemActivity` are `private int position = -1;` și citește filmul cu `IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class)`
- `ItemActivity.saveMovie()` face deja `setResult(RESULT_OK, intent)` + `finish()`

Deci jumătate din lanț există. Exercițiile adaugă bucățile lipsă, una câte una.

**Harta capitolului:**

| # | Ce adaugi | Direcția | Fișiere |
|---|---|---|---|
| 36.1 | un `String` în titlu | dus | `MainActivity`, `ItemActivity` |
| 36.2 | doi parametri într-un subtitlu | dus | + `activity_item.xml` |
| 36.3 | un `boolean` înapoi | întors | `MainActivity`, `ItemActivity` |
| 36.4 | un cod de rezultat propriu | întors | + `activity_item.xml` |
| 36.5 | ștergere cu poziție | întors | + `activity_item.xml` |
| 36.6 | confirmare înainte de ștergere | — | `ItemActivity` |
| 36.7 | insert fără poziție | dus + întors | `MainActivity`, `ItemActivity` |
| 36.8 | edit cu poziție, fără duplicat | dus + întors | `MainActivity`, `ItemActivity` |
| 36.9 | `ACTION_VIEW` către browser | implicit | + `AndroidManifest.xml` |
| 36.10 | atribut nou + Intent | toate | toate |

---

## Exercițiul 36.1 — Trimite un String și afișează-l în titlul ecranului

**Cerință:** Când apeși FAB-ul „+", `MainActivity` trimite în `ItemActivity` un `String` cu titlul ecranului („New movie"). `ItemActivity` îl citește și îl pune în bara de titlu cu `setTitle(...)`. Când intri în editare, titlul rămâne „Edit movie".

**Fișiere atinse:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `activities/MainActivity.java`. Sub `protected static final String MOVIE_EXTRA = "movie";`, adaugă `protected static final String TITLE_EXTRA = "title";`.
2. În `initListeners()`, în listener-ul lui `fabInsert`, după `Intent intent = new Intent(MainActivity.this, ItemActivity.class);`, adaugă `intent.putExtra(TITLE_EXTRA, "New movie");`.
3. Deschide `activities/ItemActivity.java`. În `onCreate`, imediat după `Intent intent = getIntent();`, adaugă `String header = intent.getStringExtra(MainActivity.TITLE_EXTRA);`.
4. La finalul lui `onCreate`, transformă blocul `if (existing != null)` într-un `if / else if`: ramura `else if (header != null)` face `setTitle(header);`.
5. Verifică: Run, apasă FAB-ul. Bara de titlu a ecranului de formular scrie „New movie". Atinge un film din listă: bara scrie „Edit movie".

**Indiciu 1 — dacă te blochezi la pasul 1:** constantele de extra sunt `String`-uri care trăiesc în `MainActivity` și se citesc din `ItemActivity`. Sunt `protected static`, deci accesibile din același pachet `ro.ase.ie.g1097.activities`. Nu le duplica în `ItemActivity` — dacă scrii „title" într-o parte și „Title" în cealaltă, cheia nu se potrivește și primești `null` fără nicio eroare.

**Indiciu 2 — dacă te blochezi la pasul 4:** `setTitle("Edit movie")` este deja apelat în ramura `existing != null`. Dacă pui `setTitle(header)` după bloc, îl suprascrii și ecranul de editare va scrie „New movie". De aceea cele două variante stau în `if / else if`, nu una după alta.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** o constantă nouă în `MainActivity`, un `putExtra` la lansare, o citire în `ItemActivity` și o ramură `else if` care o afișează.

**Cod:**

Pasul 1 — `activities/MainActivity.java`, lângă celelalte constante:

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
protected static final String TITLE_EXTRA = "title";     // linia nouă
```

Pasul 2 — `MainActivity.initListeners()`, listener-ul FAB-ului:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, "New movie");      // linia nouă
        launcher.launch(intent);
    }
});
```

Pasul 3 și 4 — `activities/ItemActivity.java`, `onCreate()`:

```java
Intent intent = getIntent();
String header = intent.getStringExtra(MainActivity.TITLE_EXTRA);   // linia nouă
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
} else if (header != null) {                                        // ramura nouă
    setTitle(header);
}
```

**De ce:** `getStringExtra` întoarce `null` când cheia lipsește, nu o excepție. Asta face din „a venit sau nu extra-ul" o decizie pe care o iei tu, cu `if`. În `MainActivity`, click-ul pe rând nu pune `TITLE_EXTRA`, deci `header` este `null` acolo — exact ce trebuie, pentru că ramura de editare are propriul titlu.

**De reținut:**
1. **`setTitle(...)` este metoda lui `Activity`, nu a `ActionBar`-ului.** `AppCompatActivity` o expune direct și funcționează și când bara e generată de temă. `getSupportActionBar().setTitle(...)` ar cere un `null`-check, pentru că `getSupportActionBar()` poate întoarce `null` când tema nu are `ActionBar`.
2. **Ordinea ramurilor este contractul.** Editarea câștigă întotdeauna în fața titlului primit: dacă ai venit cu `MOVIE_EXTRA`, ești în editare, indiferent ce `TITLE_EXTRA` ai primit.
3. **Cheia este un `String` oarecare.** `"title"` nu are nicio legătură cu `R.string` sau cu `android:label`. E doar o etichetă în `Bundle`; contează să fie identică la ambele capete, de aceea o ții într-o singură constantă.
4. **`getIntent()` întoarce `Intent`-ul cu care a fost creată activitatea.** Nu îl confunda cu `Intent`-ul de rezultat din `saveMovie()` — acela e un obiect nou, construit de tine, și nu are legătură cu cel primit.
5. **Nu pune text vizibil în `putExtra` dacă poți pune o cheie.** Aici textul e chiar ce vrei să afișezi, deci e în regulă; dar dacă ar fi fost „modul" ecranului, ai fi trimis `"insert"` / `"edit"` și ai fi ales textul în `ItemActivity`.

**Unde se aplică:** orice valoare simplă care personalizează un ecran secundar — un titlu, un mod (`"insert"` / `"edit"`), un id de entitate, un nume de utilizator. Modelul e mereu același: constantă în părinte, `putExtra` la lansare, `getXxxExtra` cu gardă de `null` în copil.

</details>

---

## Exercițiul 36.2 — Trimite doi parametri (titlu + an) și afișează-i într-un subtitlu

**Cerință:** FAB-ul trimite **doi** extra-uri: titlul ecranului și anul curent. `ItemActivity` le afișează împreună, într-un singur `TextView` de subtitlu, sub antetul „Movie details", în forma `New movie · 2026`. În editare subtitlul rămâne cel original.

**Fișiere atinse:** `activities/MainActivity.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `MainActivity`, adaugă a doua constantă: `protected static final String YEAR_EXTRA = "year";`.
2. În listener-ul FAB-ului, după `putExtra(TITLE_EXTRA, ...)`, adaugă `intent.putExtra(YEAR_EXTRA, Calendar.getInstance().get(Calendar.YEAR));`. `Calendar` este deja importat în `MainActivity`.
3. În `res/layout/activity_item.xml`, al doilea `TextView` din antet (cel cu textul „Fill in the information below and save.") nu are `android:id`. Adaugă-i `android:id="@+id/tvSubtitle"`.
4. În `ItemActivity`, adaugă câmpul `private TextView tvSubtitle;`, linia `tvSubtitle = findViewById(R.id.tvSubtitle);` în `initControls()`.
5. În `onCreate`, citește anul cu `int year = intent.getIntExtra(MainActivity.YEAR_EXTRA, -1);` și, în ramura `else if (header != null)`, construiește textul.
6. Verifică: Run, FAB — subtitlul scrie „New movie · 2026". Atinge un film — subtitlul rămâne „Fill in the information below and save.".

**Indiciu 1 — dacă te blochezi la pasul 3:** `TextView`-ul de subtitlu este **al doilea** din antetul ecranului, imediat după „Movie details". Are `textAppearanceBodyMedium` și `textColor="?attr/colorOnSurfaceVariant"`. Nu confunda cu etichetele din carduri (`tvTile`, `tvGenre` etc.), care au deja id-uri.

**Indiciu 2 — dacă te blochezi la pasul 5:** `getIntExtra` cere o valoare implicită, pentru că un `int` nu poate fi `null`. Folosește `-1` ca „nu a venit" și tratează cazul: dacă anul lipsește, afișează doar titlul, fără separator. Altfel ajungi cu „New movie · -1" pe ecran.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un al doilea extra numeric, un id pentru `TextView`-ul de subtitlu, un câmp și o linie în `initControls`, plus construcția textului în `onCreate`.

**Cod:**

Pasul 1 și 2 — `activities/MainActivity.java`:

```java
protected static final String TITLE_EXTRA = "title";
protected static final String YEAR_EXTRA = "year";       // linia nouă
```

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, "New movie");
        intent.putExtra(YEAR_EXTRA, Calendar.getInstance().get(Calendar.YEAR));   // linia nouă
        launcher.launch(intent);
    }
});
```

Pasul 3 — `res/layout/activity_item.xml`, al doilea `TextView` din rădăcină:

```xml
<TextView
    android:id="@+id/tvSubtitle"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:layout_marginBottom="20dp"
    android:text="Fill in the information below and save."
    android:textAppearance="?attr/textAppearanceBodyMedium"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

Pasul 4 și 5 — `activities/ItemActivity.java`, trei locuri:

```java
// 4a. câmpul, lângă celelalte TextView-uri
private TextView tvSubtitle;

// 4b. initControls() — la finalul metodei
tvSubtitle = findViewById(R.id.tvSubtitle);

// 5. onCreate() — citirea și construcția textului
Intent intent = getIntent();
String header = intent.getStringExtra(MainActivity.TITLE_EXTRA);
int year = intent.getIntExtra(MainActivity.YEAR_EXTRA, -1);        // linia nouă
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
} else if (header != null) {
    setTitle(header);
    tvSubtitle.setText(year == -1 ? header : header + " · " + year);   // linia nouă
}
```

**De ce:** două extra-uri înseamnă două chei și două citiri, dar un singur `Intent`. Nu există „`putExtra` cu două valori": fiecare valoare are cheia ei. Separatorul `·` (U+00B7) este același caracter folosit deja în `movie_item.xml` pentru subtitlul cardului, deci ecranele arată consecvent.

**De reținut:**
1. **`int` nu poate fi `null`, deci `getIntExtra` are nevoie de o valoare implicită.** Alege o valoare care nu poate fi validă (`-1` pentru un an) și trateaz-o ca „absent". Alternativa `Integer` cu `getSerializableExtra` funcționează, dar e mai greoaie și nu îți cumpără nimic.
2. **Ordinea `putExtra` nu contează, ordinea citirilor nici.** `Bundle`-ul este o hartă; contează doar cheile.
3. **Un `TextView` fără `android:id` nu poate fi găsit din cod.** `findViewById(R.id.tvSubtitle)` întoarce `null` și `setText` aruncă `NullPointerException` — de aceea pasul 3 este obligatoriu, nu opțional.
4. **Separatorul se pune în cod, nu în XML.** Dacă îl pui în `android:text`, îl pierzi la primul `setText`.
5. **Afișarea condiționată e mai bună decât o valoare implicită vizibilă.** `year == -1 ? header : header + " · " + year` evită „New movie · -1", care arată ca un bug.

**Unde se aplică:** orice ecran care are nevoie de context — „Edit movie · Inception", „Detalii · poziția 3", „Adaugă notă · student 123". Regula: un extra per informație, o valoare implicită care nu poate fi confundată cu o valoare reală, o gardă la afișare.

</details>

---

## Exercițiul 36.3 — Returnează un boolean „salvat" și reacționează în MainActivity

**Cerință:** Când `ItemActivity` salvează, pune în `Intent`-ul de rezultat un `boolean` cu cheia `"saved"`, setat pe `true`. `MainActivity` afișează un `Toast` cu „Movie saved" doar când primește `true`. Dacă utilizatorul apasă Back, nu apare nimic.

**Fișiere atinse:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `MainActivity`, adaugă `protected static final String SAVED_EXTRA = "saved";` lângă celelalte constante.
2. În `ItemActivity.saveMovie()`, după `intent.putExtra(MainActivity.MOVIE_EXTRA, movie);`, adaugă `intent.putExtra(MainActivity.SAVED_EXTRA, true);`.
3. În `MainActivity`, în callback-ul launcherului, după `movieAdapter.notifyDataSetChanged();` din ramura `RESULT_OK`, adaugă `if (intent.getBooleanExtra(SAVED_EXTRA, false)) { Toast... }`.
4. Adaugă garda `if (intent == null) return;` imediat după `Intent intent = o.getData();`.
5. Verifică: Run, adaugă un film, Save — apare „Movie saved". Atinge un film, apasă Back — nu apare nimic.

**Indiciu 1 — dacă te blochezi la pasul 2:** `saveMovie()` construiește deja `Intent intent = new Intent();` și pune filmul în el. Boolean-ul se adaugă în **același** `Intent`, înainte de `setResult`. Dacă faci un `Intent` nou după `setResult`, nu mai ajunge nicăieri.

**Indiciu 2 — dacă te blochezi la pasul 3:** `getBooleanExtra` cere și el o valoare implicită — `false`. Nu verifica `== true` cu `getBooleanExtra(SAVED_EXTRA)` fără al doilea argument: metoda nu are acea suprascriere și nu compilează.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un flag boolean în `Intent`-ul de rezultat și o reacție în callback-ul părintelui, condiționată de flag.

**Cod:**

`activities/MainActivity.java`:

```java
protected static final String SAVED_EXTRA = "saved";     // linia nouă
```

`activities/ItemActivity.java`, `saveMovie()` — finalul metodei:

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.SAVED_EXTRA, true);         // linia nouă
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

`activities/MainActivity.java`, callback-ul launcherului:

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    if (intent == null) return;                          // garda nouă
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    movieAdapter.notifyDataSetChanged();
    if (intent.getBooleanExtra(SAVED_EXTRA, false)) {     // reacția nouă
        Toast.makeText(MainActivity.this, "Movie saved", Toast.LENGTH_SHORT).show();
    }
}
```

**De ce:** codul de rezultat spune *clasa* evenimentului („OK"), iar extra-urile spun *detaliile*. Un `boolean` în `Intent` este cel mai ieftin mod de a transmite o informație care nu are valoare proprie — nu trebuie să inventezi un cod de rezultat nou pentru ceva ce se poate exprima ca „da / nu".

**De reținut:**
1. **`RESULT_OK` fără `Intent` este posibil.** `setResult(RESULT_OK)` există ca suprascriere cu un singur argument și lasă `o.getData()` pe `null`. De aceea garda `if (intent == null) return;` nu este decorativă — fără ea, primul `getSerializableExtra` aruncă `NullPointerException`.
2. **Valoarea implicită a lui `getBooleanExtra` este decizia ta.** Cu `false`, absența cheii înseamnă „nu s-a întâmplat nimic" — exact semantică vrei. Cu `true`, orice rezultat `RESULT_OK` ar afișa toast-ul.
3. **Un flag nu înlocuiește datele.** Dacă ai nevoie și de film, îl trimiți separat; flag-ul doar califică rezultatul. Nu împacheta `boolean`-ul în `Movie` — nu are ce căuta în model.
4. **Toast-ul se afișează pe firul UI, din callback.** Callback-ul launcherului rulează pe main thread, deci `Toast.makeText(...).show()` este sigur. Dintr-un `Thread` sau `Executor` ar arunca `RuntimeException`.
5. **Alternativa la flag este un cod de rezultat propriu** (exercițiul 36.4). Alege flag când ai deja `RESULT_OK` și vrei doar să nuanțezi; alege cod propriu când evenimentul este fundamental altul.

**Unde se aplică:** orice „spune-mi dacă s-a întâmplat" — salvare reușită, formular validat, utilizator autentificat, sincronizare terminată. Modelul: `putExtra` cu un `boolean` în `Intent`-ul de rezultat, `getBooleanExtra` cu implicit `false` în părinte.

</details>

---

## Exercițiul 36.4 — Al doilea buton care întoarce un rezultat diferit

**Cerință:** Adaugă în `ItemActivity` un al doilea buton, „Save as draft", sub „Save Movie". Apăsat, închide ecranul cu codul propriu `RESULT_DRAFT` (valoarea `2`) și **fără** să modifice lista. `MainActivity` afișează „Draft saved" când primește acel cod, iar lista rămâne neschimbată.

**Fișiere atinse:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `activity_item.xml`, după `btnMovieAction`, adaugă un `MaterialButton` cu `android:id="@+id/btnDraft"`, stil `@style/Widget.Material3.Button.TonalButton`, text „Save as draft".
2. În `ItemActivity`, adaugă constanta `public static final int RESULT_DRAFT = 2;` imediat sub declarația clasei, înaintea câmpurilor.
3. Adaugă câmpul `private Button btDraft;`, linia din `initControls()` și listener-ul din `initListeners()`.
4. Scrie metoda `saveDraft()`: `setResult(RESULT_DRAFT);` apoi `finish();`. Fără `Intent`.
5. În `MainActivity`, în callback, adaugă ramura `else if (o.getResultCode() == ItemActivity.RESULT_DRAFT)` cu un `Toast`.
6. Verifică: Run, FAB, completează titlul, apasă „Save as draft" — apare „Draft saved", lista are tot 3 rânduri. Apoi Save Movie — lista are 4.

**Indiciu 1 — dacă te blochezi la pasul 2:** `RESULT_OK` este `-1`, `RESULT_CANCELED` este `0`, `RESULT_FIRST_USER` este `1`. Deci `2` este liber. Dacă folosești `0`, sistemul îl tratează ca „utilizatorul a apăsat Back" și ramura ta nu se execută niciodată.

**Indiciu 2 — dacă te blochezi la pasul 5:** pe ramura asta `o.getData()` este `null`, pentru că `setResult(RESULT_DRAFT)` nu are `Intent`. Nu apela `getData().getIntExtra(...)` — verifică doar codul și afișează toast-ul.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un buton nou, o constantă de rezultat propriu, o metodă care închide ecranul fără date și o ramură nouă în callback-ul părintelui.

**Cod:**

`res/layout/activity_item.xml` — după `btnMovieAction`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnDraft"
    style="@style/Widget.Material3.Button.TonalButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Save as draft"
    app:icon="@android:drawable/ic_menu_edit" />
```

`activities/ItemActivity.java`:

```java
public static final int RESULT_DRAFT = 2;      // sub declarația clasei

private Button btDraft;

// initControls()
btDraft = findViewById(R.id.btnDraft);

// initListeners()
btDraft.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveDraft();
    }
});

// metoda nouă
private void saveDraft() {
    setResult(RESULT_DRAFT);
    finish();
}
```

`activities/MainActivity.java` — callback-ul devine:

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    if (intent == null) return;
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    movieAdapter.notifyDataSetChanged();
} else if (o.getResultCode() == ItemActivity.RESULT_DRAFT) {     // ramura nouă
    Toast.makeText(MainActivity.this, "Draft saved", Toast.LENGTH_SHORT).show();
}
```

**De ce:** `setResult(int)` și `setResult(int, Intent)` sunt două metode diferite. Prima închide ecranul cu un cod și atât; a doua adaugă și date. Un draft nu are ce date să transmită — părintele trebuie doar să știe că s-a întâmplat, ca să afișeze mesajul. De aceea butonul nu atinge `movies`.

**De reținut:**
1. **Codurile proprii încep de la `1`.** `RESULT_FIRST_USER` este definit exact pentru asta; `2` este la fel de bun și mai ușor de citit când ai mai multe. `0` și `-1` sunt ocupate de sistem.
2. **Un cod propriu nu are nevoie de `Intent`.** Dacă nu ai date de transmis, `setResult(RESULT_DRAFT)` este suficient. Părintele verifică `getResultCode()` și nu atinge `getData()`.
3. **Ordinea ramurilor în callback este ordinea priorităților.** `RESULT_OK` primul, apoi codurile proprii; un `else if` final fără condiție ar prinde și `RESULT_CANCELED`, ceea ce de obicei nu vrei.
4. **Butonul nu validează nimic.** Un draft poate avea câmpuri goale — asta e ideea. Dacă vrei totuși validare, o pui în `saveDraft()` înainte de `setResult`, nu în părinte.
5. **Cele două butoane trebuie să arate diferit.** `Widget.Material3.Button.TonalButton` are fundal tonal, „Save Movie" este plin. La examen, diferența vizuală e jumătate din punctajul pe UX.

**Unde se aplică:** orice „al doilea mod de a închide ecranul" — salvează ca draft, anulează cu motive, trimite spre aprobare, marchează ca văzut. Fiecare primește un cod propriu și, dacă are nevoie, un `Intent` cu date.

</details>

---
## Exercițiul 36.5 — Șterge un film din ItemActivity și trimite poziția înapoi

**Cerință:** Adaugă în `ItemActivity` un buton „Delete movie", vizibil doar când editezi un film existent. Apăsat, închide ecranul cu codul propriu `RESULT_DELETE` și trimite înapoi poziția rândului. `MainActivity` scoate filmul din listă la acea poziție și redesenează.

**Fișiere atinse:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `activity_item.xml`, după `btnDraft` (sau după `btnMovieAction`, dacă nu ai făcut 36.4), adaugă un `MaterialButton` cu `android:id="@+id/btnDelete"`, stil `@style/Widget.Material3.Button.OutlinedButton`, text „Delete movie" și culoarea `?attr/colorError`.
2. În `ItemActivity`, adaugă constanta `public static final int RESULT_DELETE = 3;` lângă `RESULT_DRAFT`.
3. Adaugă câmpul `private Button btDelete;`, linia din `initControls()` și listener-ul din `initListeners()`.
4. Scrie metoda `deleteMovie()`: pune `position` în `Intent`, apoi `setResult(RESULT_DELETE, intent)` și `finish()`.
5. La finalul lui `onCreate`, după blocul `if / else if`, adaugă `btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);`.
6. În `MainActivity`, în callback, adaugă ramura `else if (o.getResultCode() == ItemActivity.RESULT_DELETE)` care citește poziția și face `movies.remove(position)`.
7. Verifică: Run, atinge „Toy Story", apasă Delete — rândul dispare, lista are 2. Apasă FAB-ul: butonul Delete nu se vede.

**Indiciu 1 — dacă te blochezi la pasul 4:** `position` este câmpul din `ItemActivity`, setat în `onCreate` doar când ai venit cu `MOVIE_EXTRA`. În modul insert rămâne `-1`, deci butonul e ascuns și nu ai ce poziție trimite. Nu citi poziția din `getIntent()` în `deleteMovie()` — câmpul o are deja.

**Indiciu 2 — dacă te blochezi la pasul 6:** `movies.remove(position)` are două suprascrieri: `remove(int index)` și `remove(Object o)`. Cu un `int`, Java alege prima — bine. Dar dacă poziția vine greșită (de exemplu `-1`), `remove(-1)` aruncă `IndexOutOfBoundsException`. Verifică intervalul înainte.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un buton care se vede doar în editare, un cod de rezultat propriu, un `Intent` care transportă poziția și o ramură de ștergere în părinte.

**Cod:**

`res/layout/activity_item.xml` — după `btnDraft`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnDelete"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Delete movie"
    android:textColor="?attr/colorError"
    app:icon="@android:drawable/ic_menu_delete"
    app:iconTint="?attr/colorError"
    app:strokeColor="?attr/colorError" />
```

`activities/ItemActivity.java`:

```java
public static final int RESULT_DRAFT = 2;
public static final int RESULT_DELETE = 3;      // linia nouă

private Button btDelete;

// initControls()
btDelete = findViewById(R.id.btnDelete);

// initListeners()
btDelete.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        deleteMovie();
    }
});

// metoda nouă
private void deleteMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_DELETE, intent);
    finish();
}

// onCreate(), la final, după blocul if / else if
btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);
```

`activities/MainActivity.java` — callback-ul:

```java
} else if (o.getResultCode() == ItemActivity.RESULT_DELETE) {
    Intent data = o.getData();
    if (data == null) return;
    int position = data.getIntExtra(POSITION_EXTRA, -1);
    if (position >= 0 && position < movies.size()) {
        movies.remove(position);
        movieAdapter.notifyDataSetChanged();
    }
}
```

**De ce:** ștergerea are nevoie de un singur lucru: **care** rând. Poziția este singura informație care leagă ecranul de detaliu de lista din părinte, pentru că `ItemActivity` nu ține referința la listă. Codul `RESULT_DELETE` spune *ce* să faci cu poziția; fără el, părintele ar crede că trebuie să înlocuiască rândul.

**De reținut:**
1. **`View.GONE`, nu `View.INVISIBLE`.** `INVISIBLE` ascunde butonul dar păstrează spațiul; formularul rămâne cu o gaură de 60dp sub butonul de salvare. `GONE` scoate și spațiul.
2. **Butonul se ascunde după ce `position` a fost setat.** Dacă pui linia înainte de blocul `if (existing != null)`, `position` este încă `-1` și butonul rămâne ascuns chiar și în editare.
3. **Garda de interval nu este opțională.** `movies.remove(-1)` aruncă `IndexOutOfBoundsException`; `movies.remove(99)` la fel. Poziția vine dintr-un alt proces de UI și trebuie tratată ca input extern.
4. **`notifyDataSetChanged()` după `remove`.** Fără el, filmul dispare din `ArrayList` dar rămâne pe ecran până la următoarea redesenezare — și la examen arată ca și cum ștergerea nu a funcționat.
5. **Poziția se strică dacă lista se schimbă între timp.** Dacă între deschiderea ecranului și Delete s-ar adăuga un film în față, poziția ar indica alt rând. În aplicația asta nu se poate întâmpla (un singur ecran activ), dar în aplicații reale se rezolvă cu un id stabil, nu cu indexul.

**Unde se aplică:** orice „șterge din ecranul de detaliu" — film, student, produs, notă. Modelul: cod propriu `RESULT_DELETE`, `Intent` cu poziția (sau cu id-ul), ramură nouă în callback, gardă de interval, `notify`.

</details>

---

## Exercițiul 36.6 — Confirmare cu AlertDialog înainte de ștergere

**Cerință:** Butonul „Delete movie" nu mai șterge direct: deschide un `AlertDialog` cu titlul „Delete movie", mesajul `Delete "Toy Story"?` și două butoane, „Delete" și „Cancel". Doar „Delete" apelează `deleteMovie()`; „Cancel" închide dialogul și nu se întâmplă nimic.

**Fișiere atinse:** `activities/ItemActivity.java` (și, dacă nu ai făcut 36.5, `res/layout/activity_item.xml`).

**Cum abordezi — pașii tăi:**
1. În `ItemActivity`, adaugă importurile `androidx.appcompat.app.AlertDialog` și `android.content.DialogInterface`.
2. Scrie o metodă nouă `confirmDelete()` care construiește dialogul cu `new AlertDialog.Builder(this)`.
3. Lansează înlănțuit: `.setTitle(...)`, `.setMessage(...)`, `.setPositiveButton("Delete", listener)`, `.setNegativeButton("Cancel", null)`, `.show()`.
4. În listener-ul butonului `btnDelete`, înlocuiește `deleteMovie();` cu `confirmDelete();`.
5. Verifică: Run, atinge un film, apasă Delete — apare dialogul cu titlul filmului. „Cancel" nu face nimic, „Delete" șterge rândul.

**Indiciu 1 — dacă te blochezi la pasul 1:** există două clase cu același nume: `android.app.AlertDialog` (platforma) și `androidx.appcompat.app.AlertDialog` (AppCompat). Aplicația folosește tema Material 3 prin AppCompat, deci importă varianta `androidx.appcompat.app.AlertDialog`. Cea din `android.app` compilează și rulează, dar folosește stilul platformei și nu respectă tema aplicației — culori, colțuri și tipografie diferite.

**Indiciu 2 — dacă te blochezi la pasul 3:** `setNegativeButton("Cancel", null)` este legal: al doilea argument este `DialogInterface.OnClickListener` și poate fi `null`, caz în care butonul doar închide dialogul. Nu ai nevoie de o clasă goală.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un `AlertDialog` construit cu builder, două butoane și un singur loc în care se apelează efectiv ștergerea.

**Cod:**

`activities/ItemActivity.java` — importuri noi, în blocul `androidx`:

```java
import androidx.appcompat.app.AlertDialog;
```

și în blocul `android`:

```java
import android.content.DialogInterface;
```

Metoda nouă și listener-ul modificat:

```java
private void confirmDelete() {
    new AlertDialog.Builder(this)
            .setTitle("Delete movie")
            .setMessage("Delete \"" + etTitle.getText().toString() + "\"?")
            .setPositiveButton("Delete", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    deleteMovie();
                }
            })
            .setNegativeButton("Cancel", null)
            .show();
}
```

```java
// initListeners() — listener-ul lui btDelete
btDelete.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        confirmDelete();          // în loc de deleteMovie();
    }
});
```

**De ce:** dialogul este un al doilea punct de decizie între utilizator și o operație ireversibilă. `deleteMovie()` rămâne neschimbat — el face treaba; `confirmDelete()` doar cere permisiunea. Separarea asta contează: dacă ai pune dialogul în `deleteMovie()`, ai avea nevoie de un al doilea dialog dacă vreodată apelezi ștergerea din alt loc.

**De reținut:**
1. **`this` din `new AlertDialog.Builder(this)` este `ItemActivity`.** Suntem într-o metodă de instanță, nu într-o clasă interioară anonimă, deci `this` este activitatea. În interiorul unui `OnClickListener`, `this` ar fi listener-ul — de aceea acolo se scrie `ItemActivity.this` dacă ai nevoie de context.
2. **Dialogul se închide singur la click pe buton; `finish()` închide ecranul.** Ordinea reală: click pe „Delete" → listener → `deleteMovie()` → `setResult` → `finish()` → activitatea se închide, iar dialogul dispare odată cu ea.
3. **`setNegativeButton("Cancel", null)`** — listener-ul `null` înseamnă „doar închide". Alternativa cu un listener gol face același lucru, cu trei linii în plus.
4. **Mesajul folosește titlul din formular, nu din model.** `etTitle.getText()` reflectă ce vede utilizatorul acum, inclusiv modificările nesalvate. Dacă ai folosi `existing.getTitle()`, ai arăta un titlu care nu mai e pe ecran.
5. **Nu bloca firul UI.** `AlertDialog.show()` este non-blocant: metoda se termină imediat, iar răspunsul vine în listener. De aceea `deleteMovie()` nu poate fi apelat „după" `show()` în aceeași metodă — ar șterge înainte ca utilizatorul să apese ceva.

**Unde se aplică:** orice acțiune ireversibilă — ștergere, ieșire fără salvare, resetare formular, trimitere în rețea. Modelul: metodă separată pentru acțiune, metodă de confirmare care o învelește, listener-ul butonului apelează confirmarea.

</details>

---

## Exercițiul 36.7 — Trimite un Movie nou, fără poziție (insert)

**Cerință:** Trasează și verifică drumul complet al unui film **nou**: FAB → `ItemActivity` fără `MOVIE_EXTRA` și fără `POSITION_EXTRA` → Save → `MainActivity` primește `RESULT_OK`, citește poziția ca `-1` și face `movies.add(movie)`. Adaugă un `Toast` cu `movies.size()` după fiecare insert, ca dovadă.

**Fișiere atinse:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `MainActivity.initListeners()` și uită-te la listener-ul FAB-ului: `new Intent(MainActivity.this, ItemActivity.class)` plus `TITLE_EXTRA` și `YEAR_EXTRA`. **Nimic altceva.**
2. Deschide `ItemActivity.onCreate()`: `existing` este `null`, deci blocul `if` nu rulează, `position` rămâne `-1`, formularul e gol.
3. Deschide `ItemActivity.saveMovie()`: `intent.putExtra(MainActivity.POSITION_EXTRA, position)` este în interiorul `if (position != -1)`, deci **nu se execută**.
4. Deschide callback-ul din `MainActivity`: `intent.getIntExtra(POSITION_EXTRA, -1)` întoarce `-1` pentru că cheia lipsește, deci ramura este `movies.add(movie)`.
5. Adaugă dovada: după `movieAdapter.notifyDataSetChanged();` din ramura de insert, un `Toast` cu `movies.size()`.
6. Verifică: Run, FAB, completează, Save — lista are 4 rânduri, toast-ul scrie „4 movies". Repetă — 5 rânduri, „5 movies".

**Indiciu 1 — dacă te blochezi la pasul 1:** ispita este să trimiți și un `Movie` gol, ca să nu fie `null` în `ItemActivity`. Nu o face: `existing != null` ar declanșa `fillForm(emptyMovie)`, iar `dateFormat.format(null)` aruncă `NullPointerException` imediat. Absența extra-ului este chiar semnalul de „mod insert".

**Indiciu 2 — dacă te blochezi la pasul 3:** nu adăuga `intent.putExtra(POSITION_EXTRA, -1)` „ca să fie". Funcționează, dar transformă un contract clar („cheia lipsește = insert") într-unul fragil („valoarea e -1 = insert"). Lasă cheia afară.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am confirmat cele patru puncte ale traseului de insert și am adăugat o dovadă vizibilă a numărului de elemente.

**Cod:**

`activities/MainActivity.java` — listener-ul FAB-ului, forma finală:

```java
fabInsert.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(TITLE_EXTRA, "New movie");
        intent.putExtra(YEAR_EXTRA, Calendar.getInstance().get(Calendar.YEAR));
        launcher.launch(intent);
        // fără MOVIE_EXTRA  -> ItemActivity intră în modul insert
        // fără POSITION_EXTRA -> nimic de înlocuit
    }
});
```

`activities/ItemActivity.java` — `onCreate()`, ramura de insert:

```java
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    // ... modul edit
}
// aici: existing == null, position == -1, formular gol
```

`activities/ItemActivity.java` — `saveMovie()`, finalul:

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.SAVED_EXTRA, true);
if (position != -1)                                   // în insert: false
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

`activities/MainActivity.java` — callback-ul, ramura de insert cu dovada:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
    Toast.makeText(MainActivity.this, movies.size() + " movies", Toast.LENGTH_SHORT).show();
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

**De ce:** insertul nu are nevoie de nicio informație despre rând, pentru că rândul nu există încă. Tot ce trebuie să știe părintele este „adaugă la final". `position == -1` este modul în care cele două ecrane cad de acord asupra acestui lucru, fără un al doilea cod de rezultat.

**De reținut:**
1. **`getIntExtra(key, -1)` întoarce `-1` și când cheia lipsește, și când valoarea este chiar `-1`.** Din perspectiva părintelui, cele două cazuri sunt identice — și asta e în regulă, pentru că ambele înseamnă „insert".
2. **Nu trimite `MOVIE_EXTRA` cu un obiect gol.** `existing != null` ar fi `true`, `fillForm` ar rula pe un `Movie` fără dată, iar `dateFormat.format(null)` ar arunca `NullPointerException`. Este cea mai frecventă greșeală la examen.
3. **`movies.add(movie)` adaugă la final.** Poziția noului rând este `movies.size() - 1` după apel. Dacă vrei să inserezi la început, folosești `movies.add(0, movie)` — dar atunci toate pozițiile trimise ulterior se mută cu unul.
4. **Toast-ul cu `movies.size()` este cea mai ieftină dovadă.** La examen, profesorul vede imediat că lista crește cu exact unul, nu cu doi și nu cu zero.
5. **`notifyDataSetChanged()` este obligatoriu și aici.** `add` mută datele, `notify` le face vizibile. Ordinea dintre ele nu contează, dar ambele trebuie să existe.

**Unde se aplică:** orice creare de entitate nouă dintr-un ecran secundar — film, student, produs, comandă. Traseul: părinte fără extra-uri de identitate → copil cu `position == -1` → rezultat fără poziție → `add` + `notify`.

</details>

---
## Exercițiul 36.8 — Editează și trimite înapoi fără să duplici (poziție)

**Cerință:** Atinge un film din listă, modifică titlul în formular, apasă „Update Movie". Lista trebuie să aibă **același număr** de rânduri, iar rândul atins să arate valorile noi. Filmul nu are voie să apară de două ori.

**Fișiere atinse:** `activities/MainActivity.java`, `activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `MainActivity.initListeners()`, verifică listener-ul de click pe rând: pune `MOVIE_EXTRA` **și** `POSITION_EXTRA`, apoi `launcher.launch(intent)`.
2. În `ItemActivity.onCreate()`, verifică faptul că `position` este **câmp**, nu variabilă locală, și că se setează din `intent.getIntExtra(MainActivity.POSITION_EXTRA, -1)`.
3. În `ItemActivity.saveMovie()`, verifică faptul că `POSITION_EXTRA` se pune înapoi doar când `position != -1`.
4. În `MainActivity`, în callback, verifică ramura `else`: `movies.set(position, movie)`, nu `movies.add(movie)`.
5. Adaugă garda de interval înainte de `set`, ca poziția să nu poată ieși din listă.
6. Verifică: Run, atinge „Inception", schimbă titlul în „Inception (2010)", Update — lista are tot 3 rânduri, primul are titlul nou.

**Indiciu 1 — dacă te blochezi la pasul 2:** `position` este citit în `onCreate`, dar folosit în `saveMovie()`, care rulează mult mai târziu, dintr-un listener. O variabilă locală declarată în `onCreate` ar fi vizibilă doar acolo; `saveMovie()` nu ar compila. Trebuie să fie câmp al clasei, exact ca `private int position = -1;` din codul actual.

**Indiciu 2 — dacă te blochezi la pasul 4:** `movies.set(position, movie)` înlocuiește elementul de la index și **păstrează** dimensiunea listei. `movies.add(movie)` crește lista cu unul. Ambele compilează, ambele rulează fără excepție — doar unul este corect.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am verificat lanțul complet al editării: doi extra-uri la dus, un câmp care supraviețuiește până la Save, un extra la întors și un `set` în părinte.

**Cod:**

`activities/MainActivity.java` — click pe rând:

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));      // obiectul, serializat
        intent.putExtra(POSITION_EXTRA, position);               // indexul rândului
        launcher.launch(intent);
    }
});
```

`activities/ItemActivity.java` — câmpul și citirea:

```java
private int position = -1;   // CÂMP, nu local

// onCreate()
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

`activities/ItemActivity.java` — `saveMovie()`, finalul:

```java
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
intent.putExtra(MainActivity.SAVED_EXTRA, true);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);   // dus-întors
setResult(RESULT_OK, intent);
finish();
```

`activities/MainActivity.java` — callback-ul, cu gardă:

```java
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    if (intent == null) return;
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
    } else if (position >= 0 && position < movies.size()) {
        movies.set(position, movie);          // ÎNLOCUIRE
    } else {
        return;                               // poziție invalidă: nu facem nimic
    }
    movieAdapter.notifyDataSetChanged();
}
```

**De ce:** poziția este singura legătură dintre rândul din listă și ecranul de detaliu. Ea face turul complet: `MainActivity` o pune la dus, `ItemActivity` o ține într-un câmp, o pune la întors, `MainActivity` o folosește la `set`. Dacă lipsește oriunde pe traseu, `getIntExtra` întoarce `-1` și filmul editat devine un film nou adăugat la final.

**De reținut:**
1. **Obiectul primit în `ItemActivity` este o copie.** `Intent` serializează `Movie` la `putExtra` și îl deserializează la citire. Modificarea câmpurilor din `existing` nu se vede în lista părintelui. De aceea `saveMovie()` construiește un `Movie` nou și îl trimite înapoi — asta este singura cale prin care modificarea ajunge în listă.
2. **`position` trebuie să fie câmp.** Este citit în `onCreate` și folosit în `saveMovie()`, apelat dintr-un listener. O variabilă locală nu supraviețuiește.
3. **`Movie` trebuie să rămână `Serializable`.** Dacă scoți `implements Serializable`, `putExtra(String, Serializable)` nu mai compilează, iar o variantă `Parcelable` ar cere `writeToParcel` și `CREATOR`. Pentru examen, `Serializable` este suficient.
4. **`IntentCompat.getSerializableExtra(intent, key, Movie.class)` este varianta modernă.** `intent.getSerializableExtra(key)` este deprecat din API 33 și întoarce `Serializable`, deci ai nevoie de un cast. Varianta cu `Class<T>` face cast-ul în siguranță.
5. **Garda de interval prinde și cazul `position == -1` trimis accidental.** Dacă ai pus `POSITION_EXTRA` cu `-1` la insert, ramura `position == -1` îl tratează oricum ca adăugare — dar dacă cineva trimite `99`, fără gardă ai `IndexOutOfBoundsException`.

**Unde se aplică:** orice editare care trebuie să actualizeze o listă — film, student, produs, notă. Regula celor trei `position`: îl trimiți la dus, îl ții într-un câmp, îl trimiți la întors.

</details>

---

## Exercițiul 36.9 — Intent implicit: deschide un link în browser

**Cerință:** Adaugă în `ItemActivity`, în cardul „Poster", un buton „Open poster in browser". Apăsat, ia URL-ul din `etPoster` și îl deschide într-o aplicație externă cu `Intent.ACTION_VIEW`. Dacă câmpul e gol, arată o eroare pe câmp; dacă nu există nicio aplicație care poate deschide link-ul, arată un `Toast`.

**Fișiere atinse:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `AndroidManifest.xml`.

**Cum abordezi — pașii tăi:**
1. În `activity_item.xml`, în Card 4 (Poster), după `TextInputLayout`-ul lui `etPoster`, adaugă un `MaterialButton` cu `android:id="@+id/btnOpenPoster"`, stil `@style/Widget.Material3.Button.TextButton`.
2. În `ItemActivity`, adaugă importul `android.net.Uri`.
3. Adaugă câmpul `private Button btOpenPoster;`, linia din `initControls()` și listener-ul din `initListeners()`.
4. Scrie metoda `openInBrowser(String url)`: gardă pentru gol, prefix `https://` dacă lipsește schema, `Uri.parse`, `new Intent(Intent.ACTION_VIEW, uri)`.
5. Verifică disponibilitatea cu `intent.resolveActivity(getPackageManager()) != null` înainte de `startActivity`.
6. În `AndroidManifest.xml`, adaugă blocul `<queries>` cu acțiunea `VIEW` și schema `https`, ca fișierul să fie copil direct al lui `<manifest>`.
7. Verifică: Run, scrie `https://developer.android.com` în Poster, apasă butonul — se deschide browserul. Golește câmpul și apasă — apare eroarea pe câmp, fără crash.

**Indiciu 1 — dacă te blochezi la pasul 4:** `Uri.parse("example.com")` produce un URI **fără schemă**. Un astfel de URI nu are cum să fie deschis de un browser, iar `resolveActivity` întoarce `null`. De aceea prefixul `https://` se adaugă înainte de `Uri.parse`, nu după.

**Indiciu 2 — dacă te blochezi la pasul 6:** pe Android 11+ (API 30), aplicațiile nu mai văd toate celelalte aplicații instalate. `resolveActivity` filtrează după vizibilitate, deci fără `<queries>` întoarce `null` chiar și când Chrome este instalat. `startActivity` ar funcționa — doar verificarea eșuează, iar tu afișezi „no app" pe nedrept.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un buton nou, o metodă care construiește un `Intent` implicit, o verificare de disponibilitate și declarația `<queries>` din manifest.

**Cod:**

`res/layout/activity_item.xml` — în Card 4, după `TextInputLayout`-ul lui `etPoster`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnOpenPoster"
    style="@style/Widget.Material3.Button.TextButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Open poster in browser"
    app:icon="@android:drawable/ic_menu_view" />
```

`activities/ItemActivity.java` — import și metodă:

```java
import android.net.Uri;
```

```java
private Button btOpenPoster;

// initControls()
btOpenPoster = findViewById(R.id.btnOpenPoster);

// initListeners()
btOpenPoster.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        openInBrowser(etPoster.getText().toString().trim());
    }
});

// metoda nouă
private void openInBrowser(String url) {
    if (url.isEmpty()) {
        etPoster.setError("Add a poster link first");
        return;
    }
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        url = "https://" + url;
    }
    Uri uri = Uri.parse(url);
    Intent intent = new Intent(Intent.ACTION_VIEW, uri);
    if (intent.resolveActivity(getPackageManager()) != null) {
        startActivity(intent);
    } else {
        Toast.makeText(this, "No app can open this link", Toast.LENGTH_SHORT).show();
    }
}
```

`AndroidManifest.xml` — copil direct al lui `<manifest>`, înaintea lui `<application>`:

```xml
<queries>
    <intent>
        <action android:name="android.intent.action.VIEW" />
        <data android:scheme="https" />
    </intent>
</queries>
```

**De ce:** un `Intent` explicit numește clasa care trebuie pornită (`new Intent(this, ItemActivity.class)`); unul implicit descrie **ce vrei să se întâmple** și lasă sistemul să aleagă aplicația. `ACTION_VIEW` + un URI `https` înseamnă „arată-mi adresa asta", iar sistemul o dă browserului sau aplicației care s-a declarat capabilă să o deschidă. Tu nu ai nevoie de permisiuni și nu ai nevoie să știi ce browser are utilizatorul.

**De reținut:**
1. **`<queries>` este despre *vizibilitate*, nu despre permisiuni.** Din Android 11, `PackageManager` ascunde aplicațiile nedeclarate. `resolveActivity` întoarce `null` fără `<queries>`, deși `startActivity` ar fi funcționat. Două soluții corecte: declari `<queries>` (verifici înainte) sau prinzi `ActivityNotFoundException` (încerci și te aperi).
2. **`Uri.parse(null)` aruncă `NullPointerException`.** Nu `IllegalArgumentException`, nu `null` — excepție. De aceea garda `url.isEmpty()` este prima linie a metodei, nu o formalitate.
3. **Un URI fără schemă nu este deschis de nimeni.** `"example.com"` nu are `scheme`, iar filtrele din manifest se uită exact la schemă. Prefixul `https://` este obligatoriu dacă permiți utilizatorului să scrie o adresă „goală".
4. **`ACTION_VIEW` nu cere permisiunea `INTERNET`.** Permisiunea o cere aplicația care descarcă efectiv pagina — browserul. Aplicația ta doar pornește un `Intent`.
5. **Nu folosi `ACTION_VIEW` pentru fișiere proprii.** Pentru un fișier din aplicația ta ai nevoie de `FileProvider` și de `content://`; `file://` aruncă `FileUriExposedException` din API 24.

**Unde se aplică:** orice „deschide în altă aplicație" — link în browser, hartă cu `geo:`, telefon cu `tel:`, e-mail cu `mailto:`, share cu `ACTION_SEND`. Modelul: construiește URI-ul, construiește `Intent`-ul cu acțiunea potrivită, verifică sau prinde excepția, pornește.

</details>

---

## Exercițiul 36.10 — Combo de examen: atribut nou + trimis prin Intent

**Cerință:** Adaugă filmului atributul `trailer` (String) — linkul către trailer. Afișează-l în formular, în cardul „Poster", sub linkul posterului. În listă, un **apăsare lungă** pe un rând deschide trailerul în browser. Atributul trebuie să supraviețuiască turului complet prin `Intent`: salvat în `ItemActivity`, ajuns în `MainActivity`, citit la apăsarea lungă.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`, `util/IntentUtils.java` (nou), `AndroidManifest.xml`.

**Cum abordezi — pașii tăi:**
1. Deschide `model/Movie.java`. Adaugă `private String trailer;` lângă `private String poster = null;`.
2. În constructorul cu 10 parametri, adaugă `String trailer` la finalul listei și `this.trailer = trailer;` la finalul corpului.
3. În `toString()`, adaugă `", trailer='" + trailer + '\'' +` după linia lui `poster`.
4. Adaugă `getTrailer()` și `setTrailer()` lângă `getPoster()`/`setPoster()`.
5. Compilează: apar trei erori în `MainActivity.addSampleMovies()`. Adaugă al 11-lea argument la fiecare dintre cele trei apeluri `new Movie(...)`.
6. În `activity_item.xml`, în Card 4, după `TextInputLayout`-ul lui `etPoster`, adaugă `TextInputLayout` + `TextInputEditText` cu `android:id="@+id/etTrailer"`.
7. În `ItemActivity`: câmpul `private EditText etTrailer;`, linia din `initControls()`, linia din `fillForm()`, linia din `saveMovie()`.
8. Creează `util/IntentUtils.java` cu metoda statică `openInBrowser(Activity, String)`.
9. În `MainActivity.initListeners()`, adaugă `setOnItemLongClickListener` care citește `movies.get(position).getTrailer()` și apelează helper-ul. **Returnează `true`.**
10. Verifică: Run, adaugă un film cu trailer `https://www.youtube.com/watch?v=dQw4w9WgXcQ`, ține apăsat pe rând — se deschide browserul. Ține apăsat pe „Inception" — se deschide trailerul demo.

**Indiciu 1 — dacă te blochezi la pasul 5:** constructorul este **pozițional**. Al 11-lea argument trebuie să fie exact `String`, iar dacă îl pui în altă poziție decât în declarație, compilatorul se plânge de tipuri sau, mai rău, trece și amestecă valorile. Ordinea parametrilor și ordinea argumentelor trebuie să fie identice.

**Indiciu 2 — dacă te blochezi la pasul 9:** `setOnItemLongClickListener` are un `boolean` ca valoare de retur. Dacă întorci `false`, evenimentul nu este consumat și se declanșează și click-ul normal — adică, după ce se deschide browserul, se deschide și ecranul de editare peste el. `return true;` în ambele ramuri.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un atribut nou în model, câmpul lui în formular, citirea și scrierea în `ItemActivity`, argumentele noi în datele demo, un helper de navigare implicită și un listener de apăsare lungă în `MainActivity`.

**Cod:**

Pasul 1–4 — `model/Movie.java`:

```java
private String poster = null;
private String trailer;                       // câmpul nou

public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster, String trailer) {
    // ... aceleași atribuiri
    this.poster = poster;
    this.trailer = trailer;                   // linia nouă
}

// toString(), după linia lui poster
", trailer='" + trailer + '\'' +

public String getTrailer() {
    return trailer;
}

public void setTrailer(String trailer) {
    this.trailer = trailer;
}
```

Pasul 5 — `MainActivity.addSampleMovies()`, toate cele trei apeluri:

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
        "https://www.youtube.com/watch?v=YoHD9XEInc0"));   // ← al 11-lea argument
```

```java
// Toy Story
"https://example.com/posters/toy-story.jpg",
"https://www.youtube.com/watch?v=xNWSGRD5CzU"));

// The Matrix
"https://example.com/posters/the-matrix.jpg",
"https://www.youtube.com/watch?v=vKQi3bBA1y8"));
```

Pasul 6 — `res/layout/activity_item.xml`, în Card 4, după `TextInputLayout`-ul lui `etPoster`:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="12dp"
    app:hintEnabled="false"
    app:endIconMode="clear_text"
    app:startIconContentDescription="Trailer link"
    app:startIconDrawable="@android:drawable/ic_media_play">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etTrailer"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Trailer URL"
        android:inputType="textUri" />
</com.google.android.material.textfield.TextInputLayout>
```

Pasul 7 — `activities/ItemActivity.java`, patru locuri:

```java
private EditText etTrailer;

// initControls()
etTrailer = findViewById(R.id.etTrailer);

// fillForm()
etTrailer.setText(existing.getTrailer() != null ? existing.getTrailer() : "");

// saveMovie()
movie.setTrailer(etTrailer.getText().toString());
```

Pasul 8 — `util/IntentUtils.java`, fișier nou:

```java
package ro.ase.ie.g1097.util;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;

public final class IntentUtils {

    private IntentUtils() {
    }

    public static void openInBrowser(Activity activity, String url) {
        if (url == null || url.trim().isEmpty()) {
            Toast.makeText(activity, "No link to open", Toast.LENGTH_SHORT).show();
            return;
        }
        String fixed = url.trim();
        if (!fixed.startsWith("http://") && !fixed.startsWith("https://")) {
            fixed = "https://" + fixed;
        }
        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(fixed));
        try {
            activity.startActivity(intent);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(activity, "No app can open this link", Toast.LENGTH_SHORT).show();
        }
    }
}
```

Pasul 9 — `activities/MainActivity.java`, în `initListeners()`:

```java
import ro.ase.ie.g1097.util.IntentUtils;
```

```java
listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
    @Override
    public boolean onItemLongClick(AdapterView<?> parent, View view, int position, long id) {
        IntentUtils.openInBrowser(MainActivity.this, movies.get(position).getTrailer());
        return true;      // consumă evenimentul
    }
});
```

**De ce:** exercițiul leagă cele două jumătăți ale capitolului. Atributul nou trebuie să treacă prin cinci reprezentări până la ecran (model → formular → activitate → `Intent` → listă), iar la final este folosit de un `Intent` implicit. Dacă oricare verigă lipsește, lanțul se rupe tăcut: `getTrailer()` întoarce `null`, iar helper-ul afișează „No link to open" în loc să deschidă browserul.

**De reținut:**
1. **`return true` în `onItemLongClick` este obligatoriu.** Altfel evenimentul se propagă și la `OnItemClickListener`, deci după browser se deschide și ecranul de editare. Două acțiuni dintr-o singură atingere.
2. **Helper-ul folosește `try / catch`, nu `resolveActivity`.** Este varianta care nu are nevoie de `<queries>`: nu întrebi dacă există o aplicație, încerci și te aperi dacă nu există. Pentru un link extern este suficientă și mai puțin fragilă.
3. **`url == null` trebuie verificat înainte de `Uri.parse`.** `Uri.parse(null)` aruncă `NullPointerException`, iar un `Movie` demo fără trailer (sau unul construit înainte de atribut) are exact `null`.
4. **`fillForm` are nevoie de gardă.** `etTrailer.setText(null)` afișează câmp gol, dar dacă adaugi un `TextWatcher` sau un `setError`, `null` devine o problemă. `existing.getTrailer() != null ? ... : ""` costă trei cuvinte.
5. **Ordinea parametrilor din constructor este contractul.** `trailer` după `poster`, în declarație și în toate cele trei apeluri. Dacă îl pui între `approval` și `onWatchlist`, compilatorul nu te oprește — `String` lângă `String` trece, iar datele se amestecă.

**Unde se aplică:** exact formatul „adaugă un atribut și folosește-l într-un `Intent`" — link de trailer, adresă de site, număr de telefon, coordonate. Lanțul din capitolul 17 (cinci straturi) plus cele două sensuri din capitolul 36 (dus și întors) acoperă majoritatea cerințelor de examen care combină modelul cu navigarea.

</details>

---

## Recapitulare — ce verifici la test

| Cerința din examen | Mecanismul | Exercițiu |
|---|---|---|
| „trimite un text în ecranul următor" | `putExtra(TITLE_EXTRA, ...)` + `getStringExtra` | 36.1 |
| „trimite două valori" | două chei, două citiri, o singură gardă de `null` | 36.2 |
| „spune-mi dacă s-a salvat" | `putExtra(SAVED_EXTRA, true)` + `getBooleanExtra(..., false)` | 36.3 |
| „al doilea buton închide altfel" | `RESULT_DRAFT = 2` + ramură nouă în callback | 36.4 |
| „șterge filmul din ecranul de detaliu" | `RESULT_DELETE` + poziție + `movies.remove` | 36.5 |
| „cere confirmare înainte" | `AlertDialog.Builder` în jurul lui `deleteMovie()` | 36.6 |
| „adaugă un film nou" | fără `MOVIE_EXTRA`, fără `POSITION_EXTRA` → `add` | 36.7 |
| „editează fără să duplici" | `POSITION_EXTRA` dus-întors → `set` | 36.8 |
| „deschide un link" | `ACTION_VIEW` + `Uri.parse` + `<queries>` sau `try/catch` | 36.9 |
| „atribut nou + navigare" | lanțul din capitolul 17 + `ACTION_VIEW` pe apăsare lungă | 36.10 |

**Checklist-ul de dinainte de Run — șase verificări, în ordinea în care se strică:**

| # | Verifică | Simptomul dacă lipsește |
|---|---|---|
| 1 | Constanta de extra are aceeași valoare în ambele activități | `null` la citire, fără nicio eroare |
| 2 | `position` este **câmp** în `ItemActivity`, nu local | nu compilează în `saveMovie()` |
| 3 | `setResult(...)` este apelat înainte de `finish()` | părintele primește `RESULT_CANCELED` |
| 4 | `o.getData()` este verificat de `null` | `NullPointerException` pe ramura fără `Intent` |
| 5 | `add` la insert, `set` la editare | duplicat sau film pierdut |
| 6 | `notifyDataSetChanged()` după fiecare mutație | lista arată date vechi |

**Trei propoziții de memorat:**

1. **Un `Intent` duce date; un cod de rezultat spune ce s-a întâmplat.** `putExtra` la dus, `setResult(cod, intent)` la întors, `getResultCode()` + `getData()` în callback. Patru metode, două sensuri.
2. **Obiectul care călătorește este o copie.** Serializarea la `putExtra` și deserializarea la citire produc un obiect nou. Modificarea lui nu atinge lista; doar `movies.set(position, movieNou)` o atinge.
3. **`registerForActivityResult` se apelează în `onCreate`, nu într-un listener.** La `d719ffc` este chiar ultima instrucțiune din `onCreate`, după `initListeners()`. Mutat într-un `onClick`, aruncă `IllegalStateException: LifecycleOwner is attempting to register while current state is RESUMED`.

---

## Rezumat capitol 36

**Ce ai construit:** un traseu complet de navigare între două activități — date la dus, date la întors, coduri proprii de rezultat, confirmare, ștergere, insert, edit și un `Intent` implicit către browser.

**Tabelul metodelor, pe sensuri:**

| Direcție | Metodă | Unde | Cine o citește |
|---|---|---|---|
| dus | `putExtra(String, String)` | `MainActivity`, la `launch` | `getStringExtra` |
| dus | `putExtra(String, int)` | `MainActivity`, la `launch` | `getIntExtra(key, -1)` |
| dus | `putExtra(String, Serializable)` | `MainActivity`, click pe rând | `IntentCompat.getSerializableExtra` |
| întors | `setResult(int, Intent)` | `ItemActivity.saveMovie()` | `getResultCode()` + `getData()` |
| întors | `setResult(int)` | `ItemActivity.saveDraft()` | doar `getResultCode()` |
| lansare | `launcher.launch(intent)` | `MainActivity` | — |
| înregistrare | `registerForActivityResult(...)` | `MainActivity.onCreate()` | — |

**Cele patru capcane care costă puncte:**

1. **Uiți `setResult`.** Ecranul se închide cu `RESULT_CANCELED` și părintele ignoră tot. Se întâmplă când apeși Back „ca să testezi" și crezi că ai salvat.
2. **Trimiți `MOVIE_EXTRA` fără `POSITION_EXTRA`.** `ItemActivity` intră în modul edit cu un obiect gol, `fillForm` ajunge la `dateFormat.format(null)` și aruncă `NullPointerException`.
3. **Faci `add` în loc de `set`.** Filmul editat apare de două ori, originalul rămâne neschimbat, iar lista crește la fiecare Update.
4. **Muți `registerForActivityResult` într-un listener.** `IllegalStateException` la primul click, pentru că înregistrarea trebuie făcută în timpul construcției activității, când starea este `CREATED`.

**Ce urmează:** dacă examenul cere „trimite date între ecrane", ai 36.1–36.8. Dacă cere „deschide ceva în afara aplicației", ai 36.9. Dacă le cere pe amândouă plus un atribut nou, ai 36.10 — și, în spate, lanțul din capitolul 17.
