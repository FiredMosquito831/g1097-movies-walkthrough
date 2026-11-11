# Capitolul 20 — Bancul de cerințe 4: adăugarea unui control

**Obiectiv:** să execuți „puneți un buton / un switch / un chip / un FAB" la examen în 5–10 minute per control, fără să uiți `findViewById`, fără `NullPointerException` și fără să pui controlul într-un layout pe care nimeni nu îl citește.

**Cum arată cerința la examen:** „Puneți un buton aici sau alt control." Poate fi orice: buton, switch, chip, FAB, spinner, iconiță. Două cerințe, 30 de minute. Profesorul schimbă un cuvânt — „buton" devine „switch", „jos-dreapta" devine „jos-stânga" — și așteaptă același lanț de patru pași.

**Rețeta pentru orice control nou (4 pași):**
1. Îl pui în XML, cu `android:id`
2. Îl iei în cod cu `findViewById`
3. Îi atașezi un listener
4. Îl folosești: citești valoarea, schimbi textul, îl ascunzi

> **Regula:** XML → `findViewById` → listener → acțiune. Patru pași, în ordinea asta, pentru orice control. Dacă sari peste unul, controlul apare dar nu face nimic — și ăsta e singurul mod în care poți pierde puncte la o cerință atât de simplă.

**Tabelul de buzunar:**

| Ce ți se cere | Tag în XML | Listener | Cum citești |
|---|---|---|---|
| Buton | `MaterialButton` / `Button` | `setOnClickListener` | — |
| Switch | `MaterialSwitch` / `Switch` | `setOnCheckedChangeListener` | `isChecked()` |
| Chip | `Chip` | `setOnClickListener` (sau `setOnCheckedChangeListener`, dacă e `checkable`) | `isChecked()` |
| FAB | `FloatingActionButton` | `setOnClickListener` | — |
| Spinner | `Spinner` | `setOnItemSelectedListener` | `getSelectedItemPosition()` |
| Câmp de text | `TextInputLayout` + `TextInputEditText` | `addTextChangedListener` | `getText().toString()` |

**Convenții — citește o dată, înainte de primul exercițiu:**
- Codul de plecare e `cod-final/`, adică `G1097` la commitul `d719ffc`. Toate numele de fișiere și de id-uri din capitol sunt cele reale.
- `activity_main.xml` are rădăcină `FrameLayout`. Un control „deasupra listei" se pune cu `android:layout_gravity="top|start"`, iar `ListView`-ul primește `android:layout_marginTop`, ca să nu stea sub el.
- `movie_item.xml` **există, dar nu e folosit de niciun adapter** la `d719ffc`: `MainActivity` construiește `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, deci rândul e un singur `TextView` cu `toString()`-ul filmului. Orice control pus în `movie_item.xml` nu apare pe ecran până nu faci adapterul — exercițiul 20.5 îl construiește.
- Exercițiile 20.4, 20.5, 20.7 și 20.8 lucrează pe lista afișată `visibleMovies` și pe metoda `refreshList()`, ambele introduse în 20.4. Dacă faci un exercițiu fără 20.4, înlocuiește `visibleMovies` cu `movies` și `refreshList()` cu `movieAdapter.notifyDataSetChanged()`.

---

## Exercițiul 20.1 — Butonul „Clear form" sub „Save Movie"

**Cerință:** Adaugă sub butonul „Save Movie" un buton „Clear form" care golește toate câmpurile formularului, fără să închidă ecranul și fără să atingă filmul din listă.

**Fișiere atinse:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `res/layout/activity_item.xml` și derulează la final. Ultimul copil al `LinearLayout`-ului vertical este `btnMovieAction` (`MaterialButton`, „Save Movie", înălțime 60dp).
2. Imediat după `</com.google.android.material.button.MaterialButton>`-ul lui `btnMovieAction`, dar înainte de `</LinearLayout>`, adaugă un `MaterialButton` cu `android:id="@+id/btnClear"`, `style="@style/Widget.Material3.Button.TextButton"`, `layout_width="match_parent"`, `layout_height="wrap_content"`, `layout_marginTop="8dp"` și `android:text="Clear form"`.
3. Deschide `activities/ItemActivity.java` și adaugă câmpul `private Button btClear;` lângă `private Button btMovieAction;`.
4. În `initControls()`, adaugă `btClear = findViewById(R.id.btnClear);` la finalul metodei.
5. În `initListeners()`, adaugă `btClear.setOnClickListener(v -> clearForm());`.
6. Scrie metoda `clearForm()` la finalul clasei: golește cele trei `EditText`-uri și resetează `spGenre`, `sbDuration`, `rbRating`, `swWatched`, `cbonWatchList`, `rgApproval` — plus, obligatoriu, `releaseCal`.
7. Verifică: Run, completează tot formularul, apasă „Clear form". Toate câmpurile se golesc, eticheta duratei arată „0 min.", cea a switch-ului „No", ratingul cade la zero. Apoi completează doar titlul și salvează: filmul trebuie să aibă data de azi, nu data pe care o aleseseși înainte de clear.

**Indiciu 1 — dacă te blochezi la pasul 2:** butonul se pune ca frate al lui `btnMovieAction`, nu în interiorul lui. Dacă îl pui după `</LinearLayout>`, devine al doilea copil direct al `ScrollView`-ului și primești „ScrollView can host only one direct child".

**Indiciu 2 — dacă te blochezi la pasul 6:** `sbDuration.setProgress(0)` și `swWatched.setChecked(false)` își actualizează singure etichetele, pentru că listenerii din `initListeners()` sunt deja atașați. Nu trebuie să scrii tu `tvDurationValue.setText("0 min.")`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un buton nou în formular, luat cu `findViewById`, cu listener care apelează o metodă `clearForm()` ce readuce fiecare control la valoarea lui implicită.

**Cod (XML + Java):**

`res/layout/activity_item.xml` — după `btnMovieAction`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnClear"
    style="@style/Widget.Material3.Button.TextButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Clear form"
    app:icon="@android:drawable/ic_menu_close_clear_cancel"
    app:iconGravity="textStart" />
```

`activities/ItemActivity.java`:

```java
// câmpul, lângă celelalte
private Button btClear;

// initControls(), la final
btClear = findViewById(R.id.btnClear);

// initListeners(), la final
btClear.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        clearForm();
    }
});

// metoda nouă, la finalul clasei
private void clearForm() {
    etTitle.setText("");
    etRelease.setText("");
    etRelease.setError(null);
    releaseCal = Calendar.getInstance();   // capcana: textul nu ține data
    spGenre.setSelection(0);
    etBudget.setText("");
    sbDuration.setProgress(0);
    rbRating.setRating(0f);
    swWatched.setChecked(false);
    cbonWatchList.setChecked(false);
    rgApproval.check(R.id.rbGeneral);
    etPoster.setText("");
    etTitle.requestFocus();
}
```

**De ce:** fiecare control are o metodă de scriere proprie — `setText`, `setSelection`, `setProgress`, `setRating`, `setChecked`, `check`. `clearForm()` le cheamă pe toate, în ordinea din formular, ca să poți verifica vizual că nu ai sărit niciunul.

**De reținut:**
1. **`releaseCal` nu se golește cu `etRelease.setText("")`.** `saveMovie()` nu citește textul câmpului, ci `releaseCal.getTime()`. Dacă nu resetezi calendarul, după „Clear form" și „Save Movie" filmul primește înapoi data veche, deși câmpul era gol. E cea mai frecventă greșeală la acest buton.
2. **`setProgress(0)` și `setChecked(false)` declanșează listenerii.** Etichetele `tvDurationValue` și `tvWatchedValue` se actualizează singure. Dacă le setezi și tu, nu strică; dacă le uiți, tot e corect.
3. **Butonul nu salvează.** Nu apelează `saveMovie()`, nu face `setResult`, nu face `finish()`. Golește și atât.
4. **Capcana din spate:** după „Clear form", `etBudget` e gol, iar `saveMovie()` face `Double.parseDouble("")` → `NumberFormatException`. Dacă profesorul apasă Save imediat după Clear, aplicația cade. Apărarea minimă, la începutul lui `saveMovie()`: `if (etBudget.getText().toString().isEmpty()) { etBudget.setError("Budget required"); return; }`.

**Unde se aplică:** orice cerință de tip „buton care resetează formularul", „buton de anulare", „golește câmpurile". Același `clearForm()` se folosește și după un Save reușit, dacă vrei să rămâi pe ecran.

</details>

---

## Exercițiul 20.2 — Al doilea FAB, jos-stânga, care afișează numărul de filme

**Cerință:** Adaugă în `activity_main.xml` un al doilea `FloatingActionButton`, în colțul din stânga jos. La apăsare, afișează un `Toast` cu numărul de filme din listă.

**Fișiere atinse:** `res/layout/activity_main.xml`, `activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `res/layout/activity_main.xml`. Rădăcina e `FrameLayout`; copiii sunt `ListView` (`listView`) și FAB-ul existent (`floatingActionButton`, cu `layout_gravity="bottom|end"`).
2. După FAB-ul existent, adaugă un al doilea `FloatingActionButton` cu `android:id="@+id/fabCount"`, `android:layout_gravity="bottom|start"`, `android:layout_margin="16dp"`, `android:contentDescription="Show movie count"` și `app:srcCompat` către o iconiță.
3. Deschide `activities/MainActivity.java` și adaugă câmpul `private FloatingActionButton fabCount;` lângă `fabInsert`.
4. În `initControls()`, adaugă `fabCount = findViewById(R.id.fabCount);`.
5. În `initListeners()`, adaugă `fabCount.setOnClickListener(...)` care afișează `Toast.makeText(MainActivity.this, movies.size() + " movies", Toast.LENGTH_SHORT).show();`.
6. Verifică: Run. Jos-stânga apare un al doilea buton rotund. Atinge-l: „3 movies". Adaugă un film, atinge-l din nou: „4 movies".

**Indiciu 1 — dacă te blochezi la pasul 2:** `FrameLayout` așază copiii după `android:layout_gravity`. `bottom|end` = dreapta jos, `bottom|start` = stânga jos. Dacă uiți `layout_gravity`, butonul stă în colțul din stânga sus, suprapus peste listă.

**Indiciu 2 — dacă te blochezi la pasul 5:** `Toast.makeText(...)` are nevoie de un `Context`. În clasă anonimă scrii `MainActivity.this`; într-o lambda `this` e deja `MainActivity`. `MainActivity.this` merge în ambele cazuri, deci e alegerea sigură.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un al doilea FAB în același `FrameLayout`, în colțul opus, cu listener care citește dimensiunea listei și o afișează într-un `Toast`.

**Cod (XML + Java):**

`res/layout/activity_main.xml` — după FAB-ul `floatingActionButton`:

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/fabCount"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="bottom|start"
    android:layout_margin="16dp"
    android:contentDescription="Show movie count"
    app:srcCompat="@android:drawable/ic_menu_info_details" />
```

`activities/MainActivity.java`:

```java
private FloatingActionButton fabCount;

// initControls()
fabCount = findViewById(R.id.fabCount);

// initListeners()
fabCount.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Toast.makeText(MainActivity.this,
                movies.size() + " movies",
                Toast.LENGTH_SHORT).show();
    }
});
```

**De ce:** `FrameLayout` nu are rânduri sau coloane — fiecare copil se poziționează singur prin `layout_gravity`. Al doilea FAB e doar încă un copil, în colțul liber. `Toast` e cel mai ieftin mod de a arăta o valoare: o linie, fără layout nou, fără dialog.

**De reținut:**
1. **`movies.size()` e numărul total; `visibleMovies.size()` e numărul afișat.** Dacă ai făcut 20.4 și switch-ul e pornit, cele două diferă. Alege-l pe cel cerut și spune la examen pe care îl folosești.
2. **`Toast` nu blochează aplicația.** Dispare singur după circa două secunde (`LENGTH_SHORT`) sau trei (`LENGTH_LONG`).
3. **`android:contentDescription` nu e decorativ.** Fără el, lint-ul dă warning, iar TalkBack anunță „buton" fără să spună ce face.
4. **Două FAB-uri nu se calcă** dacă unul e `bottom|start` și celălalt `bottom|end`. Dacă le pui amândouă în același colț, ultimul desenat îl acoperă pe primul.
5. **Iconița poate fi orice.** Am folosit `@android:drawable/ic_menu_info_details` ca să se vadă diferența; poți refolosi `@drawable/outline_add_24`, dar atunci butoanele arată identic și profesorul nu vede că ai adăugat ceva.

**Unde se aplică:** orice „încă un buton plutitor", „buton de info", „arată un număr". Același model: copil nou în `FrameLayout`, `layout_gravity` diferit, listener care citește o valoare.

</details>

---

## Exercițiul 20.3 — Butonul „Delete" din `ItemActivity`, cu cod de rezultat propriu

**Cerință:** Adaugă în `ItemActivity` un buton „Delete movie" care închide ecranul cu un cod de rezultat propriu (`RESULT_DELETE`), iar `MainActivity` șterge filmul din listă când primește acel cod. Butonul nu apare când adaugi un film nou.

**Fișiere atinse:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `activity_item.xml`, după `btnMovieAction`, adaugă un `MaterialButton` cu `android:id="@+id/btnDelete"`, stil `@style/Widget.Material3.Button.OutlinedButton`, text „Delete movie" și culoarea `?attr/colorError`.
2. În `ItemActivity.java`, adaugă constanta `public static final int RESULT_DELETE = 2;` imediat sub declarația clasei, lângă câmpuri.
3. Adaugă câmpul `private Button btDelete;`, linia din `initControls()` și listener-ul din `initListeners()`.
4. Scrie metoda `deleteMovie()`: pune `position` în Intent, cheamă `setResult(RESULT_DELETE, intent)` și `finish()`.
5. La finalul lui `onCreate`, după blocul `if (existing != null)`, adaugă `btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);`.
6. În `MainActivity.java`, în callback-ul launcherului, adaugă ramura `else if (o.getResultCode() == ItemActivity.RESULT_DELETE)`.
7. Verifică: Run, atinge un film, apasă Delete — rândul dispare din listă. Atinge FAB-ul „+": butonul Delete nu e vizibil.

**Indiciu 1 — dacă te blochezi la pasul 2:** codurile de rezultat sunt `int`-uri. `RESULT_OK` = -1, `RESULT_CANCELED` = 0, `RESULT_FIRST_USER` = 1. Orice cod propriu trebuie să fie ≥ 1; folosește 2 sau `RESULT_FIRST_USER`.

**Indiciu 2 — dacă te blochezi la pasul 6:** `o.getData()` poate fi `null` când rezultatul nu are Intent. Verifică `data != null` înainte de `getIntExtra`, altfel `NullPointerException` exact pe ramura nouă.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un buton nou în formular, o constantă de rezultat, un `Intent` care transportă poziția și o ramură nouă în callback-ul din `MainActivity`.

**Cod (XML + Java):**

`res/layout/activity_item.xml` — după `btnMovieAction`:

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
public static final int RESULT_DELETE = 2;

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

// onCreate(), după blocul if (existing != null)
btDelete.setVisibility(position == -1 ? View.GONE : View.VISIBLE);
```

`activities/MainActivity.java` — callback-ul launcherului devine:

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
    refreshList();   // sau movieAdapter.notifyDataSetChanged()
} else if (o.getResultCode() == ItemActivity.RESULT_DELETE) {
    Intent data = o.getData();
    if (data != null) {
        int position = data.getIntExtra(POSITION_EXTRA, -1);
        if (position >= 0 && position < movies.size()) {
            movies.remove(position);
            refreshList();   // sau movieAdapter.notifyDataSetChanged()
        }
    }
}
```

**De ce:** `setResult` transportă două lucruri — un cod și un `Intent` opțional. Codul spune *ce s-a întâmplat*, Intent-ul spune *cu ce*. `RESULT_OK` înseamnă salvare, `RESULT_DELETE` înseamnă ștergere; `MainActivity` are nevoie de poziție ca să știe ce rând să scoată.

**De reținut:**
1. **Codul propriu trebuie să fie ≥ 1.** 0 e `RESULT_CANCELED`, -1 e `RESULT_OK`. Un cod de 0 ar fi tratat ca „utilizatorul a apăsat Back".
2. **`position` e câmpul din `ItemActivity`,** setat în `onCreate` doar când ai venit cu `MOVIE_EXTRA`. În modul insert rămâne -1, deci butonul se ascunde.
3. **Ascunde butonul cu `View.GONE`, nu `INVISIBLE`.** GONE scoate și spațiul ocupat; altfel formularul are o gaură de 60dp sub butonul de salvare.
4. **Fără `refreshList()` (sau `notifyDataSetChanged()`), filmul dispare din `movies` dar rămâne pe ecran** până la următoarea redesenezare. Lista și modelul se țin sincron manual — asta e tema întregului capitol.
5. **Ștergerea nu cere confirmare aici.** Dacă ai 30 de secunde libere, înfășoară `deleteMovie()` într-un `AlertDialog`; dar întâi termină lanțul de rezultat, că acela e punctul.

**Unde se aplică:** orice „închide cu un rezultat care nu e OK" — delete, anulare, „adaugă la favorite" dintr-un ecran secundar. Modelul e mereu același: constantă proprie, `setResult`, ramură nouă în callback.

</details>

---

## Exercițiul 20.4 — `Switch` deasupra listei care filtrează filmele văzute

**Cerință:** Adaugă în `MainActivity`, deasupra listei, un `Switch` cu textul „Only watched". Când e pornit, lista arată doar filmele cu `watched == true`; când e oprit, le arată pe toate. Lista se redesenează imediat, iar filmele nu se pierd.

**Fișiere atinse:** `res/layout/activity_main.xml`, `activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `activity_main.xml`, adaugă un `MaterialSwitch` cu `android:id="@+id/swOnlyWatched"`, `android:layout_gravity="top|start"`, `android:layout_margin="16dp"` și `android:text="Only watched"`, ca ultim copil al `FrameLayout`-ului.
2. Dă `ListView`-ului `android:layout_marginTop="72dp"`, ca primul rând să nu stea sub switch.
3. În `MainActivity.java`, adaugă câmpurile `private MaterialSwitch swOnlyWatched;` și `private final List<Movie> visibleMovies = new ArrayList<>();`.
4. Schimbă adapterul să lucreze pe `visibleMovies`, nu pe `movies`.
5. Adaugă linia din `initControls()` și listener-ul din `initListeners()`.
6. Scrie `refreshList()`: golește `visibleMovies`, o umple din `movies` după starea switch-ului și cheamă `notifyDataSetChanged()`.
7. Înlocuiește `movies.get(position)` din click cu `visibleMovies.get(position)` și trimite `movies.indexOf(movie)` ca poziție.
8. Verifică: Run. Pornește switch-ul: rămân doar Inception și Toy Story (ambele au `watched = true`). Adaugă un film nou cu switch-ul pornit: nu apare până nu oprești switch-ul.

**Indiciu 1 — dacă te blochezi la pasul 6:** nu filtra `movies` direct. `movies` e sursa de date; dacă o golești, filmele sunt pierdute definitiv. Filtrarea se face într-o a doua listă, `visibleMovies`, pe care o citește adapterul.

**Indiciu 2 — dacă te blochezi la pasul 4:** `ArrayAdapter` ține referința la lista primită în constructor. Dacă schimbi conținutul listei (`clear()` + `add()`), adapterul vede modificarea după `notifyDataSetChanged()`. Dacă înlocuiești referința (`visibleMovies = new ArrayList<>()`), adapterul rămâne pe lista veche și nu mai vezi nimic.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** o listă afișată separat de lista sursă, un switch care o reconstruiește și un punct unic de redesenezare (`refreshList()`).

**Cod (XML + Java):**

`res/layout/activity_main.xml`:

```xml
<com.google.android.material.materialswitch.MaterialSwitch
    android:id="@+id/swOnlyWatched"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="top|start"
    android:layout_margin="16dp"
    android:text="Only watched" />
```

și, pe `ListView`:

```xml
android:layout_marginTop="72dp"
```

`activities/MainActivity.java`:

```java
private MaterialSwitch swOnlyWatched;
private final List<Movie> visibleMovies = new ArrayList<>();

// onCreate — adapterul se leagă de lista afișată
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, visibleMovies);
initControls();
initListeners();
// ... launcher ...
refreshList();   // la finalul lui onCreate

// initControls()
swOnlyWatched = findViewById(R.id.swOnlyWatched);

// initListeners()
swOnlyWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        refreshList();
    }
});

// metoda nouă
private void refreshList() {
    visibleMovies.clear();
    for (Movie movie : movies) {
        if (!swOnlyWatched.isChecked() || movie.isWatched()) {
            visibleMovies.add(movie);
        }
    }
    movieAdapter.notifyDataSetChanged();
}
```

Click-ul pe rând devine:

```java
listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        Movie movie = visibleMovies.get(position);
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movie);
        intent.putExtra(POSITION_EXTRA, movies.indexOf(movie));
        launcher.launch(intent);
    }
});
```

Iar în callback-ul launcherului, ambele `movieAdapter.notifyDataSetChanged()` se înlocuiesc cu `refreshList()`.

**De ce:** două liste, două roluri. `movies` = adevărul; `visibleMovies` = ce vezi. `refreshList()` reconstruiește a doua din prima, de fiecare dată când se schimbă filtrul sau datele. Adapterul nu știe de filtru — el vede doar lista pe care o are.

**De reținut:**
1. **Importurile noi:** `import android.widget.CompoundButton;` și `import com.google.android.material.materialswitch.MaterialSwitch;` în `MainActivity.java`. Fără ele codul nu compilează; Android Studio le adaugă automat doar dacă apeși pe sugestie.
2. **`movies.indexOf(movie)` merge pentru că `Movie` nu are `equals()`.** `indexOf` compară referințe, iar în ambele liste sunt aceleași obiecte. Dacă ai adăuga `equals()` după titlu, două filme cu același titlu ar deveni indistinctibile.
3. **`refreshList()` se cheamă în trei locuri:** la finalul lui `onCreate`, în listener-ul switch-ului și după fiecare rezultat din `ItemActivity`. Dacă uiți unul, lista rămâne desincronizată exact în cazul pe care îl testează profesorul.
4. **`MaterialSwitch` are nevoie de tema Material3.** Tema aplicației e `Theme.G1097`, cu părinte `Theme.Material3.DayNight.NoActionBar`, deci merge fără nicio modificare.
5. **`layout_marginTop="72dp"` pe `ListView` nu e cosmetic.** Fără el, primul rând stă sub switch și nu poți apăsa pe el.
6. **Filtrul nu modifică `watched`.** Un film scos din listă rămâne cu valoarea lui; se schimbă doar ce vezi, nu ce e în model.

**Unde se aplică:** orice filtru — „doar watchlist", „doar rating ≥ 4", „doar genul ales". Se schimbă doar condiția din `if`; restul rămâne identic.

</details>

---

## Exercițiul 20.5 — `Chip` „New" în card, pentru filmele lansate în ultimii 5 ani

**Cerință:** Adaugă în `movie_item.xml` un `Chip` cu textul „New", vizibil doar când filmul a fost lansat în ultimii 5 ani.

**Fișiere atinse:** `res/layout/movie_item.xml`, `adapters/MovieAdapter.java` (nou), `activities/MainActivity.java`.

**Atenție — capcana exercițiului:** la `d719ffc`, `movie_item.xml` nu e folosit de niciun adapter. `MainActivity` are `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, deci rândul e un singur `TextView` cu `toString()`-ul filmului. Dacă pui chip-ul în `movie_item.xml` și rulezi, nu se întâmplă nimic. Ca să apară, ai nevoie de un adapter care umflă `movie_item.xml` — îl construiești aici, în circa 70 de linii cu tot cu importuri.

**Cum abordezi — pașii tăi:**
1. În `movie_item.xml`, găsește `ChipGroup`-ul `movieStatusGroup` și ultimul lui copil, `chipWatchlist`. Adaugă după el un `Chip` cu `android:id="@+id/chipNew"`, text „New" și `android:visibility="gone"`.
2. Creează pachetul `ro.ase.ie.g1097.adapters` și clasa `MovieAdapter extends ArrayAdapter<Movie>`.
3. Scrie constructorul `(Context, List<Movie>)`, care cheamă `super(context, 0, movies)`.
4. Suprascrie `getView()`: umflă `R.layout.movie_item` dacă `convertView` e null, ia filmul cu `getItem(position)` și leagă titlul, subtitlul, ratingul, faptele și chip-urile existente.
5. Calculează „new": `Calendar fiveYearsAgo = Calendar.getInstance(); fiveYearsAgo.add(Calendar.YEAR, -5);` și compară cu `movie.getRelease()`.
6. Setează `chipNew.setVisibility(isNew ? View.VISIBLE : View.GONE);`.
7. În `MainActivity`, schimbă `new ArrayAdapter<>(...)` cu `new MovieAdapter(this, visibleMovies)`.
8. Verifică: Run. Inception (2010) și Toy Story (1995) nu au chip; adaugă un film cu data de azi — apare cu „New". Adaugă unul din 2015 — fără chip.

**Indiciu 1 — dacă te blochezi la pasul 3:** `ArrayAdapter` cere un layout în constructor, dar dacă suprascrii `getView()` poți da `0`. Nu se umflă nimic cu el; îl folosești doar ca să ai `getItem()` și `getCount()` gata făcute.

**Indiciu 2 — dacă te blochezi la pasul 6:** `convertView` se refolosește. Dacă setezi `chipNew` vizibil pentru un film nou și nu îl ascunzi pentru următorul, chip-ul rămâne lipit pe rândul reciclat. De aceea `setVisibility` se face la fiecare `getView`, în ambele ramuri — `VISIBLE` și `GONE`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un chip nou în card, un adapter propriu pentru `ListView` și regula de 5 ani în `getView()`.

**Cod (XML + Java):**

`res/layout/movie_item.xml` — în `ChipGroup`-ul `movieStatusGroup`, după `chipWatchlist`:

```xml
<com.google.android.material.chip.Chip
    android:id="@+id/chipNew"
    style="@style/Widget.Material3.Chip.Suggestion"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="New"
    android:clickable="false"
    android:visibility="gone"
    app:chipMinHeight="28dp"
    app:ensureMinTouchTargetSize="false" />
```

`java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (fișier nou):

```java
package ro.ase.ie.g1097.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.RatingBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.google.android.material.chip.Chip;

import java.util.Calendar;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends ArrayAdapter<Movie> {

    public MovieAdapter(@NonNull Context context, @NonNull List<Movie> movies) {
        super(context, 0, movies);
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext())
                    .inflate(R.layout.movie_item, parent, false);
        }

        Movie movie = getItem(position);
        if (movie == null) {
            return convertView;
        }

        TextView tvTitle = convertView.findViewById(R.id.movieTitle);
        TextView tvSubtitle = convertView.findViewById(R.id.movieSubtitle);
        RatingBar rbRating = convertView.findViewById(R.id.movieRating);
        TextView tvRatingValue = convertView.findViewById(R.id.movieRatingValue);
        TextView tvFacts = convertView.findViewById(R.id.movieFacts);
        Chip chipApproval = convertView.findViewById(R.id.chipApproval);
        Chip chipWatched = convertView.findViewById(R.id.chipWatched);
        Chip chipWatchlist = convertView.findViewById(R.id.chipWatchlist);
        Chip chipNew = convertView.findViewById(R.id.chipNew);

        tvTitle.setText(movie.getTitle());

        if (movie.getRelease() != null) {
            Calendar release = Calendar.getInstance();
            release.setTime(movie.getRelease());
            tvSubtitle.setText(movie.getGenre() + " · " + release.get(Calendar.YEAR));
        } else {
            tvSubtitle.setText(movie.getGenre());
        }

        rbRating.setRating(movie.getRating());
        tvRatingValue.setText(String.valueOf(movie.getRating()));
        tvFacts.setText(String.format(Locale.getDefault(), "%d min  ·  $%,.0f",
                movie.getDuration(), movie.getBudget()));

        chipApproval.setText(movie.getApproval());
        chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
        chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

        Calendar fiveYearsAgo = Calendar.getInstance();
        fiveYearsAgo.add(Calendar.YEAR, -5);
        boolean isNew = movie.getRelease() != null
                && movie.getRelease().after(fiveYearsAgo.getTime());
        chipNew.setVisibility(isNew ? View.VISIBLE : View.GONE);

        return convertView;
    }
}
```

`activities/MainActivity.java` — o singură linie:

```java
movieAdapter = new MovieAdapter(this, visibleMovies);   // înainte: new ArrayAdapter<>(...)
```

**De ce:** `ListView` nu știe să umple un layout complex. `ArrayAdapter`-ul implicit umflă `simple_list_item_1`, adică un `TextView`. Ca să apară cardul din `movie_item.xml`, ai nevoie de un adapter care îl umflă el și care leagă fiecare view de câmpul lui.

**De reținut:**
1. **`movie_item.xml` exista, dar era mort.** Asta e capcana: fișierul e în repo, arată bine în preview, dar niciun cod nu îl încarcă. Un control pus acolo nu apare până nu există adapter.
2. **`convertView` se reciclează.** Toate `setVisibility` se fac la fiecare `getView`, nu doar când creezi rândul. Altfel, un chip de la rândul 3 apare pe rândul 10 după scroll.
3. **Regula de 5 ani:** `Calendar.add(Calendar.YEAR, -5)` ține cont de ani bisecți; `Date.after` e comparație strictă. Un film lansat exact acum 5 ani și o zi nu e „New".
4. **`ListView` ignoră marginea de pe rădăcina rândului.** `AbsListView` folosește `AbsListView.LayoutParams`, care nu păstrează margini; spațiul dintre carduri vine din `app:cardUseCompatPadding="true"`, deja pus în layout.
5. **`getView` rulează la fiecare scroll.** Nu face muncă grea acolo; două `Calendar.getInstance()` per rând sunt acceptabile, dar dacă vrei, scoate-le într-un câmp al adapterului.

**Unde se aplică:** orice „arată un chip / un badge / o etichetă în funcție de o condiție". Condiția se schimbă, restul lanțului rămâne: câmp în XML, `findViewById` în `getView`, `setVisibility`.

</details>

---

## Exercițiul 20.6 — Înlocuiește iconița FAB-ului cu un `VectorDrawable` nou

**Cerință:** Schimbă iconița FAB-ului din `activity_main.xml` cu alta, creată de tine ca `VectorDrawable` (File → New → Vector Asset). Iconița veche rămâne în proiect.

**Fișiere atinse:** `res/drawable/ic_star_24.xml` (nou), `res/layout/activity_main.xml`.

**Cum abordezi — pașii tăi:**
1. În Android Studio, click dreapta pe folderul `res` → New → Vector Asset.
2. Asset Type: **Clip Art**. Click pe butonul „Clip Art", caută „star", alege iconița, OK.
3. Name: `ic_star_24`. Size: 24dp x 24dp. Next → Finish. Apare `res/drawable/ic_star_24.xml`.
4. Deschide `activity_main.xml`, găsește FAB-ul `floatingActionButton` și schimbă `app:srcCompat="@drawable/outline_add_24"` în `app:srcCompat="@drawable/ic_star_24"`.
5. Schimbă și `android:contentDescription` din „Add" în ceva ce descrie noua acțiune.
6. Verifică: Run. Butonul rotund are acum o stea. Dacă apare neagră pe fundal colorat, adaugă `app:tint="?attr/colorOnPrimaryContainer"` pe FAB sau șterge `android:tint` din vector.

**Indiciu 1 — dacă te blochezi la pasul 1:** dialogul are două ecrane. Primul alege tipul și iconița; al doilea alege numele și culoarea. Dacă închizi la primul, nu s-a creat nimic.

**Indiciu 2 — dacă te blochezi la pasul 4:** numele contează. `ic_star_24` devine `R.drawable.ic_star_24`. Resursele vor litere mici, cifre și underscore — fără majuscule, fără cratime, fără spații.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un fișier vector nou în `res/drawable/` și o singură referință schimbată în layout.

**Cod (XML + Java):**

`res/drawable/ic_star_24.xml` — generat de wizard, arată așa:

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF000000"
        android:pathData="M12,17.27L18.18,21l-1.64,-7.03L22,9.24l-7.19,-0.61L12,2 9.19,8.63 2,9.24l5.46,4.73L5.82,21z" />
</vector>
```

`res/layout/activity_main.xml` — FAB-ul devine:

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="bottom|end"
    android:layout_margin="16dp"
    android:contentDescription="Add to favorites"
    app:srcCompat="@drawable/ic_star_24" />
```

**De ce:** un `VectorDrawable` e un desen descris prin coordonate (`pathData`), nu prin pixeli. Un fișier de câteva sute de bytes arată bine la orice densitate, pentru că sistemul îl randează la dimensiunea cerută.

**De reținut:**
1. **`app:srcCompat`, nu `android:src`.** FAB-ul folosește `srcCompat`; `android:src` funcționează pe API nou, dar nu pe toate versiunile, iar lint-ul te avertizează.
2. **`android:tint="#000000"` din vector e o capcană.** Dacă îl lași, iconița e neagră oriunde o pui. În FAB, `app:tint` (implicit `?attr/colorOnPrimaryContainer` în Material3) acoperă tint-ul vectorului; într-un `ImageView` simplu, nu.
3. **`android:contentDescription` descrie acțiunea, nu desenul:** „Add to favorites", nu „star".
4. **Vectorul vechi rămâne în proiect.** Nu îl șterge dacă nu ți se cere; dacă îl ștergi și îl mai referă cineva, build-ul cade cu „resource not found".
5. **Varianta de 10 secunde, dacă nu ai timp de dialog:** `app:srcCompat="@android:drawable/btn_star_big_on"`. Merge, dar cerința „create a vector asset" nu e îndeplinită.

**Unde se aplică:** orice „schimbă iconița", „pune o săgeată", „adaugă un icon în buton". `app:icon` pe `MaterialButton` funcționează exact la fel.

</details>

---

## Exercițiul 20.7 — Buton „Edit" în card, în locul atingerii întregului rând

**Cerință:** Adaugă în cardul din `movie_item.xml` un `MaterialButton` „Edit" care deschide `ItemActivity` în modul de editare. Atingerea oricărei alte zone din card nu mai face nimic.

**Fișiere atinse:** `res/layout/movie_item.xml`, `adapters/MovieAdapter.java`, `activities/MainActivity.java`.

**Presupune:** adapterul din 20.5.

**Cum abordezi — pașii tăi:**
1. În coloana de informații din `movie_item.xml`, după `ChipGroup`-ul `movieStatusGroup`, adaugă un `MaterialButton` cu `android:id="@+id/btnEdit"`, stil `@style/Widget.Material3.Button.TextButton`, text „Edit" și `android:layout_gravity="end"`.
2. În adapter, adaugă interfața `OnEditClickListener` cu metoda `onEditClick(int position)`.
3. Adaugă câmpul `private final OnEditClickListener listener;` și parametrul corespunzător în constructor.
4. În `getView`, ia butonul și atașează `btnEdit.setOnClickListener(v -> listener.onEditClick(position));`.
5. În `MainActivity`, șterge (sau comentează) blocul `listView.setOnItemClickListener(...)` din `initListeners()`.
6. Adaugă metoda `openForEdit(int listPosition)`: ia filmul din `visibleMovies`, pune `movies.indexOf(movie)` ca poziție și lansează `ItemActivity`.
7. Schimbă construirea adapterului în `new MovieAdapter(this, visibleMovies, this::openForEdit)`.
8. Verifică: Run. Atinge cardul în afara butonului — nimic. Atinge „Edit" — se deschide formularul completat, titlul ecranului e „Edit movie", iar butonul de salvare scrie „Update Movie".

**Indiciu 1 — dacă te blochezi la pasul 6:** `position` din `getView` e poziția în lista afișată, nu în `movies`. Când filtrezi (20.4), cele două diferă. De aceea `MainActivity` primește poziția din listă și o traduce cu `movies.indexOf(movie)`.

**Indiciu 2 — dacă te blochezi la pasul 4:** listener-ul se atașează la fiecare `getView`, nu o singură dată. Dacă îl pui doar în ramura `convertView == null`, butonul rândului reciclat va deschide filmul care era acolo la prima umflare.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un buton în card, o interfață de callback în adapter și o metodă publică de deschidere în `MainActivity`.

**Cod (XML + Java):**

`res/layout/movie_item.xml` — în coloana de informații, după `ChipGroup`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnEdit"
    style="@style/Widget.Material3.Button.TextButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="end"
    android:minWidth="0dp"
    android:minHeight="0dp"
    android:text="Edit"
    app:icon="@android:drawable/ic_menu_edit"
    app:iconGravity="textStart" />
```

`adapters/MovieAdapter.java` — trei adăugiri:

```java
public interface OnEditClickListener {
    void onEditClick(int position);
}

private final OnEditClickListener listener;

public MovieAdapter(@NonNull Context context, @NonNull List<Movie> movies,
                    @NonNull OnEditClickListener listener) {
    super(context, 0, movies);
    this.listener = listener;
}

// în getView, după celelalte findViewById
MaterialButton btnEdit = convertView.findViewById(R.id.btnEdit);
btnEdit.setOnClickListener(v -> listener.onEditClick(position));
```

`activities/MainActivity.java`:

```java
// initListeners() — blocul listView.setOnItemClickListener(...) se șterge complet

// metoda nouă
private void openForEdit(int listPosition) {
    if (listPosition < 0 || listPosition >= visibleMovies.size()) {
        return;
    }
    Movie movie = visibleMovies.get(listPosition);
    Intent intent = new Intent(this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movie);
    intent.putExtra(POSITION_EXTRA, movies.indexOf(movie));
    launcher.launch(intent);
}

// onCreate
movieAdapter = new MovieAdapter(this, visibleMovies, this::openForEdit);
```

**De ce:** butonul are nevoie de o cale înapoi la `MainActivity`. Interfața e acea cale: adapterul nu știe ce e `MainActivity`, știe doar că cineva vrea să afle poziția atinsă. `this::openForEdit` e metoda care primește poziția.

**De reținut:**
1. **Import nou în adapter:** `import com.google.android.material.button.MaterialButton;`. Fără el, `findViewById(R.id.btnEdit)` întoarce `View`, nu `MaterialButton`.
2. **`this::openForEdit`** e echivalentul lambda al lui `new OnEditClickListener() { public void onEditClick(int p) { openForEdit(p); } }`. Merge pentru că interfața are o singură metodă.
3. **Varianta rapidă, fără interfață:** `((MainActivity) getContext()).openForEdit(position)` direct în adapter. Compilează și merge la examen, dar creează o dependență de la `adapters` la `activities` — exact ce capitolul 12 spune să eviți.
4. **Listener-ul se pune în afara blocului `if (convertView == null)`.** `convertView` se refolosește, dar listener-ul trebuie să știe poziția nouă.
5. **Butonul consumă doar click-urile lui.** Restul cardului nu mai reacționează pentru că ai șters `setOnItemClickListener`; dacă vrei tot cardul click-abil, pui `setOnClickListener` pe `convertView` și atunci butonul e de prisos.
6. **`android:minWidth="0dp"` și `android:minHeight="0dp"`** reduc butonul la textul lui; altfel `MaterialButton` impune 48dp și umflă cardul.

**Unde se aplică:** orice „buton în rândul listei" — delete per rând, favorite, share. Același lanț: interfață în adapter, metodă în activitate, poziție tradusă.

</details>

---

## Exercițiul 20.8 — `Spinner` deasupra listei pentru sortare

**Cerință:** Adaugă în `MainActivity`, deasupra listei, un `Spinner` cu trei opțiuni — „As added", „Title A-Z", „Rating (best first)". La schimbarea opțiunii, lista se reordonează.

**Fișiere atinse:** `res/values/strings.xml`, `res/layout/activity_main.xml`, `activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `strings.xml`, adaugă un `<string-array name="sort_options">` cu cele trei texte, lângă `movie_genre`.
2. În `activity_main.xml`, adaugă un `Spinner` cu `android:id="@+id/spSort"`, `android:layout_gravity="top|end"`, `android:layout_margin="16dp"`, `android:entries="@array/sort_options"` și `android:spinnerMode="dropdown"`.
3. `ListView` are deja `android:layout_marginTop="72dp"` dacă ai făcut 20.4; dacă nu, pune-l acum.
4. În `MainActivity.java`, adaugă câmpul `private Spinner spSort;` și linia din `initControls()`.
5. În `initListeners()`, atașează `setOnItemSelectedListener` cu ambele metode — `onItemSelected` cheamă `sortMovies(position)`, `onNothingSelected` rămâne gol.
6. Scrie `sortMovies(int mode)`: 0 → `refreshList()`, 1 → sortare după titlu, 2 → sortare după rating descrescător, apoi `notifyDataSetChanged()`.
7. Verifică: Run. Alege „Title A-Z": Inception, The Matrix, Toy Story. Alege „Rating (best first)": The Matrix (5), Inception (4.5), Toy Story (4). Alege „As added": ordinea inițială.

**Indiciu 1 — dacă te blochezi la pasul 5:** `Spinner` are nevoie de **două** metode în listener, chiar dacă `onNothingSelected` nu face nimic. Dacă încerci cu lambda, nu compilează — interfața nu e funcțională.

**Indiciu 2 — dacă te blochezi la pasul 6:** sortarea se face pe `visibleMovies`, nu pe `movies`. `movies` păstrează ordinea de inserare, iar „As added" o restaurează prin `refreshList()`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un string-array cu opțiuni, un spinner în colțul de sus, un listener cu două metode și o metodă de sortare cu trei ramuri.

**Cod (XML + Java):**

`res/values/strings.xml` — lângă `movie_genre`:

```xml
<string-array name="sort_options">
    <item>As added</item>
    <item>Title A-Z</item>
    <item>Rating (best first)</item>
</string-array>
```

`res/layout/activity_main.xml`:

```xml
<Spinner
    android:id="@+id/spSort"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="top|end"
    android:layout_margin="16dp"
    android:entries="@array/sort_options"
    android:spinnerMode="dropdown" />
```

`activities/MainActivity.java`:

```java
private Spinner spSort;

// initControls()
spSort = findViewById(R.id.spSort);

// initListeners()
spSort.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
    @Override
    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        sortMovies(position);
    }

    @Override
    public void onNothingSelected(AdapterView<?> parent) {
    }
});

// metoda nouă
private void sortMovies(int mode) {
    if (mode == 0) {
        refreshList();
        return;
    }
    if (mode == 1) {
        visibleMovies.sort((a, b) -> a.getTitle().compareToIgnoreCase(b.getTitle()));
    } else if (mode == 2) {
        visibleMovies.sort((a, b) -> Float.compare(b.getRating(), a.getRating()));
    }
    movieAdapter.notifyDataSetChanged();
}
```

**De ce:** `List.sort(Comparator)` reordonează lista în loc. Comparatorul primește două filme și întoarce negativ dacă primul vine înainte. Pentru rating descrescător, inversăm argumentele: `Float.compare(b, a)`.

**De reținut:**
1. **`onItemSelected` se apelează și la pornire, cu poziția 0.** `sortMovies(0)` rulează imediat după atașarea listener-ului, fără ca utilizatorul să atingă nimic. E normal.
2. **`compareToIgnoreCase` vs. `compareTo`:** primul pune „inception" și „Inception" la fel; al doilea le separă după codul ASCII, cu majusculele înainte.
3. **`Float.compare(b.getRating(), a.getRating())`** — dacă scrii `(int)(b - a)`, ratingurile 4.5 și 4.2 devin amândouă 0 și ordinea e arbitrară. Nu trunchia float-uri într-un comparator.
4. **Sortarea nu se păstrează după filtrare:** `refreshList()` reconstruiește lista în ordinea din `movies`. Dacă vrei să rămână, cheamă `sortMovies(spSort.getSelectedItemPosition())` la finalul lui `refreshList()`.
5. **`android:entries` e suficient pentru un spinner static.** Pentru opțiuni care se schimbă din cod, ai nevoie de un `ArrayAdapter<String>` și de `setAdapter`.

**Unde se aplică:** orice „sortează după", „filtrează după", „alege o categorie". Se schimbă doar comparatorul.

</details>

---

## Exercițiul 20.9 — `TextInputLayout` cu `endIconMode="clear_text"` și ce NU face ștergerea

**Cerință:** Profesorul cere un buton de ștergere rapidă pe câmpul Titlu. **Verifică întâi codul:** la `d719ffc`, `etTitle` are deja `app:endIconMode="clear_text"` pe `TextInputLayout`-ul lui. Deci cerința reală la examen e să știi să pui atributul pe orice câmp — fă-o pe `etBudget`, care nu îl are — și să explici ce nu rezolvă el.

**Fișiere atinse:** `res/layout/activity_item.xml` (și, pentru explicație, `activities/ItemActivity.java`).

**Cum abordezi — pașii tăi:**
1. Deschide `activity_item.xml` și caută `etTitle`. Deasupra lui e un `TextInputLayout` cu `app:endIconMode="clear_text"` ca ultim atribut. Confirmă: butonul X apare când câmpul are text.
2. Caută `etBudget` (Card 2, Production). `TextInputLayout`-ul lui are `app:hintEnabled="false"` și `app:prefixText="$ "`, dar nu are `endIconMode`.
3. Adaugă `app:endIconMode="clear_text"` pe `TextInputLayout`-ul bugetului — nu pe `TextInputEditText`.
4. Verifică: Run, deschide formularul, scrie ceva în Budget. Apare un X la capătul drept; atinge-l și textul dispare.
5. Apasă Save imediat după ce ai golit Budget: aplicația cade cu `NumberFormatException`. Notează de ce — asta e întrebarea de teorie.
6. Deschide `ItemActivity.java` și urmărește `saveMovie()`: `Double.parseDouble(etBudget.getText().toString())`. Confirmă că ștergerea n-a atins nimic altceva.

**Indiciu 1 — dacă te blochezi la pasul 3:** atributul stă pe `TextInputLayout`, nu pe `TextInputEditText`. Dacă îl pui pe edit text, e ignorat fără eroare — și butonul nu apare.

**Indiciu 2 — dacă te blochezi la pasul 5:** `endIconMode` are valori fixe: `clear_text`, `password_toggle`, `dropdown_menu`, `custom`, `none`. Orice altceva dă eroare la build, cu numele atributului.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** atributul `endIconMode="clear_text"` pe `TextInputLayout`-ul bugetului; titlul îl avea deja. Zero linii de Java.

**Cod (XML + Java):**

`res/layout/activity_item.xml` — blocul bugetului, cu atributul nou marcat:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:prefixText="$ "
    app:endIconMode="clear_text">   <!-- linia nouă -->

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etBudget"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Budget"
        android:inputType="numberDecimal" />
</com.google.android.material.textfield.TextInputLayout>
```

Blocul titlului, deja existent în cod, pentru comparație:

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Movie title"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

**De ce:** `clear_text` e un mod al `TextInputLayout`-ului: el adaugă automat un `ImageButton` cu X și, la apăsare, cheamă `editText.setText("")`. Nu scrii niciun listener și nu ții nicio referință la buton.

**De reținut — ce NU face ștergerea:**
1. **Nu resetează modelul.** `Movie` din `movies` rămâne neatins. Textul din câmp e doar o copie de lucru; modelul se schimbă abia la `saveMovie()`.
2. **Nu resetează `releaseCal`.** Pentru `etRelease`, `saveMovie()` folosește `releaseCal.getTime()`, nu textul. Dacă ștergi textul datei și apeși Save, filmul primește tot data veche.
3. **Nu resetează celelalte controale.** SeekBar-ul, RatingBar-ul, switch-ul, checkbox-ul, radiogroup-ul și spinnerul rămân exact cum erau. Fiecare are propria resetare: `setProgress`, `setRating`, `setChecked`, `check`, `setSelection`.
4. **Nu validează.** Un câmp gol e perfect valid pentru `TextInputLayout`; `Double.parseDouble("")` aruncă `NumberFormatException` abia la Save.
5. **Nu salvează și nu închide ecranul.** Nu atinge `setResult` și nu cheamă `finish()`.
6. **Nu golește alt câmp.** Fiecare `TextInputLayout` are propriul end icon; X-ul de la Titlu nu știe de Budget.

**Unde se aplică:** orice câmp de text. E cel mai ieftin punct din examen — un atribut, zero linii de Java — dar și cel mai ușor de explicat greșit.

</details>

---

## Exercițiul 20.10 — Combinația de examen: butonul „Duplicate movie"

**Cerință:** Adaugă în `ItemActivity` un buton „Duplicate movie" care salvează filmul din formular de două ori: o dată normal și încă o dată ca intrare nouă în listă. Butonul funcționează și când editezi un film existent.

**Fișiere atinse:** `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. În `activity_item.xml`, după `btnMovieAction` (și după `btnDelete`, dacă ai făcut 20.3), adaugă un `MaterialButton` cu `android:id="@+id/btnDuplicate"`, stil `OutlinedButton`, text „Duplicate movie".
2. În `ItemActivity`, extrage construirea filmului din `saveMovie()` într-o metodă `buildMovie()` care întoarce `Movie`.
3. `saveMovie()` devine scurt: `Movie movie = buildMovie();` + Intent + `setResult`.
4. Adaugă câmpul `btDuplicate`, linia din `initControls()` și listener-ul din `initListeners()`.
5. Scrie `duplicateMovie()`: pune filmul în Intent, pune `DUPLICATE_EXTRA = true`, **fără** `POSITION_EXTRA`, apoi `setResult(RESULT_OK, intent)` și `finish()`.
6. În `MainActivity`, adaugă constanta `public static final String DUPLICATE_EXTRA = "duplicate";` lângă celelalte.
7. În callback, dacă `getBooleanExtra(DUPLICATE_EXTRA, false)` e true, adaugă filmul de două ori.
8. Verifică: Run, completează formularul, apasă „Duplicate movie". În listă apar două rânduri identice. Editează un film existent și apasă „Duplicate movie": lista crește cu o copie, filmul original rămâne.

**Indiciu 1 — dacă te blochezi la pasul 5:** `RESULT_OK` singur nu poate spune „adaugă de două ori". Ai nevoie de un al doilea canal de informație în același Intent — un `boolean` extra. Codul de rezultat rămâne `RESULT_OK`, pentru că operația e tot o salvare.

**Indiciu 2 — dacă te blochezi la pasul 7:** dacă trimiți `POSITION_EXTRA`, `MainActivity` intră pe ramura de editare și înlocuiește filmul existent, nu adaugă. Pentru duplicat, poziția trebuie să lipsească — atunci `getIntExtra(POSITION_EXTRA, -1)` întoarce -1, adică „insert".

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** citirea formularului scoasă într-o metodă `buildMovie()`, un buton nou care trimite un flag în loc de poziție și o ramură nouă în callback.

**Cod (XML + Java):**

`res/layout/activity_item.xml` — după `btnMovieAction`:

```xml
<com.google.android.material.button.MaterialButton
    android:id="@+id/btnDuplicate"
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:text="Duplicate movie"
    app:icon="@android:drawable/ic_menu_add"
    app:iconGravity="textStart" />
```

`activities/ItemActivity.java`:

```java
private Button btDuplicate;

// initControls()
btDuplicate = findViewById(R.id.btnDuplicate);

// initListeners()
btDuplicate.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        duplicateMovie();
    }
});

// buildMovie() — corpul vechiului saveMovie(), fără Intent
private Movie buildMovie() {
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
    return movie;
}

// saveMovie() devine
private void saveMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, buildMovie());
    if (position != -1) {
        intent.putExtra(MainActivity.POSITION_EXTRA, position);
    }
    setResult(RESULT_OK, intent);
    finish();
}

// metoda nouă
private void duplicateMovie() {
    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, buildMovie());
    intent.putExtra(MainActivity.DUPLICATE_EXTRA, true);
    setResult(RESULT_OK, intent);
    finish();
}
```

`activities/MainActivity.java`:

```java
public static final String DUPLICATE_EXTRA = "duplicate";

// în callback-ul launcherului
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (intent.getBooleanExtra(DUPLICATE_EXTRA, false)) {
        movies.add(movie);
        movies.add(movie);
    } else if (position == -1) {
        movies.add(movie);
    } else {
        movies.set(position, movie);
    }
    refreshList();   // sau movieAdapter.notifyDataSetChanged()
}
```

**De ce:** `buildMovie()` separă „citește formularul" de „ce faci cu rezultatul". `saveMovie()` și `duplicateMovie()` folosesc aceeași citire, dar trimit rezultate diferite: unul cu poziție (înlocuiește), unul cu flag (adaugă de două ori).

**De reținut:**
1. **Cele două rânduri sunt același obiect.** `movies.add(movie)` de două ori pune aceeași referință. La editarea unuia, celălalt rămâne pe obiectul vechi, pentru că `movies.set(position, movieNou)` înlocuiește doar indexul editat. Pentru copii independente, adaugă un constructor de copiere în `Movie`:

```java
public Movie(Movie other) {
    this(other.title, other.release, other.genre, other.budget, other.duration,
         other.rating, other.watched, other.approval, other.onWatchlist, other.poster);
}
```

și în `MainActivity`: `movies.add(new Movie(movie)); movies.add(movie);`

2. **Fără `POSITION_EXTRA`, rezultatul e tratat ca insert.** `getIntExtra(POSITION_EXTRA, -1)` întoarce -1, iar ramura `position == -1` adaugă. Nu trebuie să trimiți nimic special pentru „nu edita".
3. **Ordinea ramurilor contează.** `DUPLICATE_EXTRA` se verifică înaintea lui `position == -1`; altfel duplicatul ar intra o singură dată.
4. **`buildMovie()` poate arunca `NumberFormatException`** dacă Budget e gol — la fel ca `saveMovie()`. Dacă ai timp, pune verificarea în `buildMovie()`, o singură dată pentru ambele butoane.
5. **Butonul e util și în edit mode:** duplici filmul editat, cu valorile din formular, fără să modifici originalul.

**Unde se aplică:** exact formatul „încă un buton care face ceva cu filmul" — duplicat, salvează ca draft, salvează și adaugă la watchlist. Refactorul `buildMovie()` e ce te salvează când profesorul cere al doilea buton care salvează.

</details>

---

## Recapitulare — cele 10 cerințe într-un tabel

| # | Control | Fișier | Listener | Ce trece între ecrane |
|---|---|---|---|---|
| 20.1 | `MaterialButton` | `activity_item.xml` | `setOnClickListener` | — |
| 20.2 | `FloatingActionButton` | `activity_main.xml` | `setOnClickListener` | — |
| 20.3 | `MaterialButton` | `activity_item.xml` | `setOnClickListener` | `RESULT_DELETE` + poziție |
| 20.4 | `MaterialSwitch` | `activity_main.xml` | `setOnCheckedChangeListener` | — |
| 20.5 | `Chip` | `movie_item.xml` | — (se calculează în `getView`) | — |
| 20.6 | `VectorDrawable` | `res/drawable/` | — | — |
| 20.7 | `MaterialButton` | `movie_item.xml` | `setOnClickListener` | poziție (prin interfață) |
| 20.8 | `Spinner` | `activity_main.xml` | `setOnItemSelectedListener` | — |
| 20.9 | `TextInputLayout` | `activity_item.xml` | intern (`clear_text`) | — |
| 20.10 | `MaterialButton` | `activity_item.xml` | `setOnClickListener` | `RESULT_OK` + `DUPLICATE_EXTRA` |

> **Trucul de timp:** șapte din zece exerciții sunt „XML → `findViewById` → listener → acțiune". Doar 20.5 și 20.7 cer adapter, iar 20.6 nu are deloc Java. Dacă la examen primești „pune un buton", e 20.1 sau 20.2. Dacă primești „pune un buton care șterge", e 20.3. Dacă primești „pune un control care schimbă ce se vede în listă", e 20.4 sau 20.8.
