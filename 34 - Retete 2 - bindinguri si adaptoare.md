# Capitolul 34 — Rețete 2: bindinguri și adaptoare

**Obiectiv:** să rezolvi în 10–15 minute orice cerință de tip „leagă valoarea X de widget-ul Y" sau „fă un adapter", pe aplicația **G1097 (Movies)**, commit `d719ffc`. Fiecare rețetă are pașii exacți, codul minim care compilează, mecanismul din spate și greșeala care costă puncte.

**Sursa:** `cod-final` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`, `strings.xml`. Toate ID-urile, metodele și câmpurile din capitol există exact așa în fișierele astea.

**Convenția de căi:** toate căile sunt relative la `src/main/`. Deci `java/ro/ase/ie/g1097/activities/ItemActivity.java` înseamnă `app/src/main/java/ro/ase/ie/g1097/activities/ItemActivity.java`, iar `res/layout/movie_item.xml` înseamnă `app/src/main/res/layout/movie_item.xml`.

---

## Ce este un „binding" în sensul examenului

Cuvântul acoperă trei lucruri diferite, care se rezolvă diferit:

| Situația | Mecanismul | Rețetele |
|---|---|---|
| Widget → etichetă, cât timp utilizatorul lucrează | listener pe widget, `setText` în callback | 34.1, 34.2, 34.4, 34.6 |
| Widget → model, la salvare | `getText()` / `getProgress()` / `isChecked()` + setter | 34.3, 34.5 |
| Model → rând de listă | adapter: `ArrayAdapter`, `BaseAdapter` sau `RecyclerView.Adapter` | 34.7–34.14 |

Primele două se fac în `ItemActivity` și nu pot strica build-ul: dacă le greșești, aplicația compilează și doar nu face ce trebuie. Al treilea se face într-o clasă nouă și, scris pe jumătate, **nu compilează deloc**. De aceea, la examen, ordinea e: întâi cerința de formular, apoi adapterul.

**Detaliu verificat în sursă:** `ItemActivity` folosește `findViewById`, deși `build.gradle.kts` are `buildFeatures { viewBinding = true }` și fișierul importă `ro.ase.ie.g1097.databinding.ActivityItemBinding`. Importul e mort — nu se folosește nicăieri. La examen scrii `findViewById`, ca în repo.

**Regula celor 30 de minute:** un binding simplu = 5 minute, unul cu validare = 10, un adapter = 15–20, migrarea completă = 25. Dacă ți se dau două cerințe, începe cu cea care nu poate rupe build-ul.

**Trei verificări înainte de orice rețetă:**

1. `setContentView(R.layout.activity_item)` rulează **înainte** de orice `findViewById`. Altfel primești `NullPointerException`.
2. `initControls()` rulează **înainte** de `initListeners()` și **înainte** de `fillForm(existing)`. Ordinea asta apare explicit în `onCreate`.
3. Fiecare ID pe care îl scrii în Java trebuie să existe în XML. Un ID care nu există în niciun layout dă eroare de compilare (`cannot find symbol`). Un ID care există, dar aparține altui view, compilează și întoarce `null` la `findViewById` — crapă la prima atingere. Verifică în XML, nu în autocomplete.

---

## Rețeta 34.1 — Leagă o valoare de o etichetă, în timp real

**Cerința, cum sună la test**

„Leagă eticheta `tvDurationValue` de slider-ul `sbDuration`, astfel încât valoarea să se actualizeze în timp real, în forma `148 min.`"

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `java/ro/ase/ie/g1097/activities/ItemActivity.java` | adaugi listener-ul pe `sbDuration`, în `initListeners()` | **da** |
| 2 | `res/layout/activity_item.xml` | nimic — `sbDuration` și `tvDurationValue` există deja | nu, doar verifici |

**Pașii, în ordine**

**Pasul 1 — verifică widget-urile în XML.** În `activity_item.xml`, cardul „Production" conține:

```xml
<SeekBar
    android:id="@+id/sbDuration"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:max="300"
    android:min="0"
    android:progressTint="?attr/colorPrimary"
    android:thumbTint="?attr/colorPrimary"
    tools:progress="148" />
```

și, deasupra lui, eticheta:

```xml
<TextView
    android:id="@+id/tvDurationValue"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="0 min"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorPrimary"
    tools:text="148 min" />
```

Observă: `android:text="0 min"` este textul **de design**, scris de mână. `tools:text="148 min"` se vede doar în preview-ul din Android Studio, nu pe telefon.

**Pasul 2 — câmpurile există deja.** În `ItemActivity.java`:

```java
private SeekBar sbDuration;
private TextView tvDurationValue;
```

**Pasul 3 — `findViewById` există deja.** În `initControls()`:

```java
sbDuration = findViewById(R.id.sbDuration);
tvDurationValue = findViewById(R.id.tvDurationValue);
```

**Pasul 4 — adaugi legătura.** În `initListeners()`, la finalul metodei:

```java
sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {

    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {

    }
});
```

Cele două metode goale sunt obligatorii: `SeekBar.OnSeekBarChangeListener` are **trei** metode abstracte, deci clasa anonimă trebuie să le implementeze pe toate. Nu poți folosi lambda aici — o lambda are nevoie de o interfață cu **o singură** metodă abstractă.

**Pasul 5 — verifică ordinea din `onCreate`.** Trebuie să fie exact așa:

```java
initControls();
initListeners();

Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

`initListeners()` rulează **înainte** de `fillForm(existing)`. Asta face ca legătura să fie activă în momentul în care `fillForm` apelează `sbDuration.setProgress(148)`.

**De ce merge așa**

`SeekBar` nu are o proprietate „valoare" care să se actualizeze singură în etichetă. Are un listener cu trei metode, iar `onProgressChanged` se apelează la **orice** schimbare a progresului — fie că vine din degetul utilizatorului (`fromUser = true`), fie din cod (`fromUser = false`). De aceea, când `fillForm` face `sbDuration.setProgress(148)`, eticheta se actualizează fără ca `fillForm` să știe de ea. Ordinea din `onCreate` garantează că listener-ul e înregistrat înainte de prima schimbare programatică.

**Greșeala care costă puncte**

1. **Scrii doar `onStopTrackingTouch`.** Simptom: eticheta se actualizează doar când ridici degetul, iar în timpul mișcării rămâne în urmă. Cauza: ai pus `setText` în metoda care anunță **sfârșitul** atingerii, nu schimbarea valorii.
2. **Legi eticheta greșită.** Simptom: dispare textul „Duration" din formular. Cauza: ai scris `tvDuration` (eticheta statică de lângă slider) în loc de `tvDurationValue` (valoarea). Ambele încep la fel.
3. **Muți `initListeners()` după `fillForm`.** Simptom: formularul gol merge, dar la editarea unui film eticheta rămâne „0 min". Cauza: `setProgress(148)` a rulat înainte ca listener-ul să existe.

**Verificarea**

Rulezi aplicația și deschizi formularul gol. Eticheta Duration scrie `0 min.` — **cu punct**, deși XML-ul are `0 min` fără punct. Punctul e dovada că a rulat codul tău, nu textul din XML. Miști slider-ul: cifra urmează degetul, fără întârziere. Apeși pe „Inception" în listă (durata 148): eticheta arată `148 min.` imediat, fără să atingi slider-ul.

**Exersează**

- [18.1](cap-18.html#ex-18-1) — exact legătura asta, rescrisă din memorie.
- [19.1](cap-19.html#ex-19-1) — același mecanism pe `swWatched`.
- [19.4](cap-19.html#ex-19-4) — aceeași etichetă, formatată „1 h 22 min".

---

## Rețeta 34.2 — Leagă o valoare la inițializare

**Cerința, cum sună la test**

„La deschiderea formularului, etichetele `tvDurationValue` și `tvWatchedValue` să pornească de la starea reală a widget-urilor, nu de la textul scris în XML."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `ItemActivity.java` | adaugi metoda `syncLabels()` și o apelezi în `initControls()` | **da** |
| 2 | `ItemActivity.java` | o apelezi și la finalul lui `fillForm(...)` | **da**, dacă vrei să fie corectă și în modul de editare |
| 3 | `activity_item.xml` | nimic | nu |

**Pașii, în ordine**

**Pasul 1 — scrii metoda.** La finalul clasei `ItemActivity`, după `showReleaseDatePicker()`:

```java
private void syncLabels() {
    tvDurationValue.setText(sbDuration.getProgress() + " min.");
    tvWatchedValue.setText(swWatched.isChecked() ? "Yes" : "No");
}
```

**Pasul 2 — o apelezi la inițializare.** În `initControls()`, după ultimul `findViewById`:

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

    syncLabels();
}
```

**Pasul 3 — o apelezi și după `fillForm`.** În modul de editare, `fillForm` schimbă starea widget-urilor **după** ce `initControls` a rulat deja. Adaugă apelul la finalul metodei:

```java
private void fillForm(Movie existing) {
    etTitle.setText(existing.getTitle());
    etRelease.setText(dateFormat.format(existing.getRelease()));
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

    syncLabels();
}
```

**De ce merge așa**

Textul din XML (`android:text="0 min"`, `android:text="No"`) este o valoare **statică**, copiată în fiecare instanță a layout-ului. Widget-ul, în schimb, are o stare proprie: `getProgress()` și `isChecked()`. La pornire, cele două coincid din întâmplare; după `fillForm`, nu mai coincid. O singură metodă care citește widget-ul și scrie eticheta, apelată în ambele momente, garantează că eticheta nu minte niciodată. Nu ai nevoie de listener pentru asta — ai nevoie de un singur punct de adevăr.

**Greșeala care costă puncte**

1. **Apelezi `syncLabels()` înainte de `findViewById`.** Simptom: `NullPointerException` la pornire, în `initControls`. Cauza: ai pus apelul la începutul metodei, nu la final.
2. **O apelezi doar în `initControls()`.** Simptom: formularul gol e corect, dar la editarea „Inception" eticheta arată `0 min.` și `No`, deși slider-ul e la 148 și switch-ul e pornit. Cauza: `fillForm` a schimbat widget-urile după ce etichetele fuseseră deja scrise.
3. **Te bazezi pe `android:text` din XML.** Simptom: eticheta arată corect până la prima schimbare făcută din cod. Cauza: ai confundat textul de design cu valoarea.

**Verificarea**

Formular gol: `0 min.` și `No`. Apeși pe „Inception" (148 minute, văzut): `148 min.` și `Yes`. Apeși pe „The Matrix" (136 minute, nevăzut): `136 min.` și `No`. Între cele două deschideri, etichetele se schimbă **fără** să miști nimic — asta arată că `syncLabels()` rulează la fiecare deschidere.

**Exersează**

- [18.1](cap-18.html#ex-18-1) — varianta cu listener, pentru comparație.
- [19.6](cap-19.html#ex-19-6) — ce se întâmplă cu aceleași valori la rotirea ecranului.

---

## Rețeta 34.3 — Citește un widget în model, la salvare

**Cerința, cum sună la test**

„La apăsarea butonului Save, construiește obiectul `Movie` citind toate widget-urile din formular și trimite-l înapoi în `MainActivity`."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `ItemActivity.java` | completezi `saveMovie()` cu câte o linie de citire pentru fiecare widget | **da** |
| 2 | `ItemActivity.java` | verifici că `btMovieAction` are listener care cheamă `saveMovie()` | **da** |
| 3 | `Movie.java` | nimic — toate setter-ele există | nu |

**Pașii, în ordine**

**Pasul 1 — verifică intrarea în metodă.** În `initListeners()`:

```java
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveMovie();
    }
});
```

**Pasul 2 — scrie corpul lui `saveMovie()`.** Metoda completă, în `ItemActivity.java`:

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

**Pasul 3 — verifică tabelul de citire.** Fiecare widget are exact o metodă de citire, iar tipul se potrivește cu setter-ul:

| Widget | Citire | Tip în `Movie` | Setter |
|---|---|---|---|
| `etTitle` | `getText().toString()` | `String` | `setTitle` |
| `etRelease` | `releaseCal.getTime()` | `Date` | `setRelease` |
| `spGenre` | `getSelectedItem().toString()` | `String` | `setGenre` |
| `etBudget` | `Double.parseDouble(getText().toString())` | `double` | `setBudget` |
| `sbDuration` | `getProgress()` | `int` | `setDuration` |
| `rbRating` | `getRating()` | `float` | `setRating` |
| `swWatched` | `isChecked()` | `boolean` | `setWatched` |
| `cbonWatchList` | `isChecked()` | `boolean` | `setOnWatchlist` |
| `etPoster` | `getText().toString()` | `String` | `setPoster` |
| `rgApproval` | iterezi copiii până la `isChecked()` | `String` | `setApproval` |

**De ce merge așa**

Formularul este singura sursă de date în momentul salvării: nu există un obiect `Movie` „pe jumătate" care să fie actualizat. Metoda creează un obiect nou cu constructorul fără parametri și îl umple prin setteri, într-o ordine care nu contează pentru compilator, dar care urmează ordinea din formular. Apoi obiectul pleacă prin `Intent`, iar `MainActivity` îl primește în callback-ul lui `launcher` și îl pune în listă (`add`) sau îl înlocuiește (`set`), după cum `position` este `-1` sau nu.

**Greșeala care costă puncte**

1. **Câmp numeric gol.** Simptom: aplicația se închide la Save, cu `NumberFormatException: For input string: ""`. Cauza: `Double.parseDouble("")` aruncă excepție, iar tu nu ai validat înainte. Rezolvarea e rețeta 34.5.
2. **Data citită din text.** Simptom: codul nu compilează, sau data se pierde. Cauza: ai încercat `new Date(etRelease.getText().toString())` — `Date` nu are constructor din `String`. Data trăiește în `releaseCal`, iar `etRelease` doar o afișează.
3. **Uiți `setResult(RESULT_OK, intent)`.** Simptom: formularul se închide, dar lista nu se schimbă. Cauza: callback-ul din `MainActivity` verifică `o.getResultCode() == RESULT_OK` și ignoră orice altceva.

**Verificarea**

Completezi formularul și apeși Save Movie. Revii în listă, iar filmul apare. În modul de editare, butonul scrie „Update Movie", iar la salvare rândul își schimbă valorile, fără să apară un rând nou. Închizi formularul cu Back, fără Save: lista rămâne neschimbată.

**Exersează**

- [17.1](cap-17.html#ex-17-1) — același traseu, pentru un atribut nou.
- [19.7](cap-19.html#ex-19-7) — ce se întâmplă cu bugetul afișat ca `1.6E8`.
- [19.8](cap-19.html#ex-19-8) — `fillForm` care crapă când `release` e `null`.

---

## Rețeta 34.4 — Arată sau ascunde un widget condiționat

**Cerința, cum sună la test**

„Eticheta `tvWatchedValue` să fie vizibilă doar cât timp switch-ul `swWatched` este pornit; când switch-ul este oprit, eticheta dispare complet."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `ItemActivity.java` | adaugi `setVisibility` în listener-ul switch-ului | **da** |
| 2 | `ItemActivity.java` | setezi vizibilitatea și la inițializare, în `initControls()` | **da** |
| 3 | `activity_item.xml` | nimic | nu |

**Pașii, în ordine**

**Pasul 1 — listener-ul, cu ambele ramuri.** În `initListeners()`, înlocuiești listener-ul existent cu:

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
        tvWatchedValue.setVisibility(isChecked ? View.VISIBLE : View.GONE);
    }
});
```

**Pasul 2 — starea inițială.** Listener-ul se apelează doar când valoarea **se schimbă**. La deschidere, switch-ul e oprit și nu se schimbă nimic, deci eticheta ar rămâne vizibilă cu textul „No". Adaugă la finalul lui `initControls()`, după `findViewById`-uri:

```java
tvWatchedValue.setVisibility(swWatched.isChecked() ? View.VISIBLE : View.GONE);
```

**Pasul 3 — verifică importul.** `ItemActivity.java` are deja `import android.view.View;` (îl folosește în `onClick(View v)`). Nu trebuie adăugat nimic.

**Un detaliu de tip, verificat în sursă:** `swWatched` este declarat în XML ca `com.google.android.material.materialswitch.MaterialSwitch`, iar câmpul din `ItemActivity` are exact tipul `MaterialSwitch`. Fișierul importă și `android.widget.Switch`, dar importul e mort — în aplicație nu există niciun `Switch` simplu. Listener-ul funcționează pentru că `MaterialSwitch` extinde `SwitchCompat`, care extinde `CompoundButton`; de aceea tipul parametrului din `onCheckedChanged` este `CompoundButton`, nu `MaterialSwitch`.

**De ce merge așa**

`setVisibility(int)` schimbă felul în care view-ul participă la layout. `View.VISIBLE` îl arată, `View.INVISIBLE` îl ascunde dar îi păstrează spațiul, `View.GONE` îl scoate din calcul complet — rândul se strânge, iar view-urile de sub el urcă. Listener-ul prinde doar **schimbările**, nu și starea de la pornire, de aceea e nevoie de al doilea apel, făcut o singură dată, în `initControls()`. Cele două apeluri sunt independente: unul e pentru utilizator, celălalt pentru prima afișare.

**Greșeala care costă puncte**

1. **Doar ramura `VISIBLE`.** Simptom: eticheta apare când pornești switch-ul, dar nu mai dispare când îl oprești. Cauza: ai scris `if (isChecked) { setVisibility(View.VISIBLE); }` fără `else`. E aceeași greșeală care, într-un adapter, face rândurile reciclate să păstreze statusul filmului anterior.
2. **`View.INVISIBLE` în loc de `View.GONE`.** Simptom: eticheta nu se vede, dar sub „Recommended" rămâne un gol de o linie, iar cardul nu se strânge. Cauza: `INVISIBLE` păstrează spațiul.
3. **Fără pasul 2.** Simptom: la deschidere, eticheta „No" se vede deși switch-ul e oprit; abia după ce apeși switch-ul de două ori dispare. Cauza: ai crezut că listener-ul rulează și la inițializare.

**Verificarea**

Deschizi formularul gol: sub „Recommended" nu apare niciun „No" — rândul are doar eticheta și switch-ul. Pornești switch-ul: apare „Yes", iar rândul crește. Oprești: „Yes" dispare și rândul se strânge la loc. Deschizi „Inception" (văzut): eticheta e vizibilă din prima, pentru că `fillForm` a pornit switch-ul.

**Exersează**

- [17.8](cap-17.html#ex-17-8) — un chip care apare doar la o condiție.
- [18.9](cap-18.html#ex-18-9) — chip-ul de aprobare, legat și ascuns cu `View.GONE`.

---

## Rețeta 34.5 — Validare cu mesaj de eroare

**Cerința, cum sună la test**

„La Save, dacă titlul este gol sau bugetul nu este un număr, salvarea se oprește și câmpul vinovat afișează un mesaj de eroare."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `ItemActivity.java` | adaugi metoda `validateForm()` | **da** |
| 2 | `ItemActivity.java` | apelezi `validateForm()` la începutul lui `saveMovie()` | **da** |
| 3 | `activity_item.xml` | nimic — `etTitle` și `etBudget` au deja ID | nu |

**Pașii, în ordine**

**Pasul 1 — scrii validarea.** În `ItemActivity.java`, deasupra lui `saveMovie()`:

```java
private boolean validateForm() {
    etTitle.setError(null);
    etBudget.setError(null);

    String title = etTitle.getText().toString().trim();
    if (title.isEmpty()) {
        etTitle.setError("Titlul este obligatoriu");
        etTitle.requestFocus();
        return false;
    }

    String budget = etBudget.getText().toString().trim();
    if (budget.isEmpty()) {
        etBudget.setError("Bugetul este obligatoriu");
        etBudget.requestFocus();
        return false;
    }

    try {
        Double.parseDouble(budget);
    } catch (NumberFormatException e) {
        etBudget.setError("Bugetul trebuie să fie un număr");
        etBudget.requestFocus();
        return false;
    }

    return true;
}
```

Primele două linii șterg erorile de la apăsarea anterioară: `setError(null)` ascunde iconița. Fără ele, mesajul rămâne pe câmp și după ce utilizatorul l-a corectat. În `showReleaseDatePicker()` există deja același model, pe `etRelease`.

**Pasul 2 — o apelezi prima.** `saveMovie()`, metoda completă:

```java
private void saveMovie() {
    if (!validateForm()) {
        return;
    }

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

**Pasul 3 — verifică ordinea.** Garda trebuie să fie **prima** instrucțiune din `saveMovie()`, înainte de `Double.parseDouble(...)`. Dacă ai muta validarea mai jos — de exemplu imediat după `movie.setBudget(...)` — excepția ar fi aruncată înainte ca mesajul să ajungă pe ecran, iar aplicația s-ar închide.

**De ce merge așa**

`setError(CharSequence)` este o metodă a lui `TextView`: atașează un mesaj de eroare view-ului, iar Android afișează o iconiță roșie în dreapta și un popup cu textul. Nu oprește nimic singură — de aceea `validateForm()` întoarce `boolean` și `saveMovie()` iese imediat cu `return`. `requestFocus()` mută focusul pe câmpul vinovat, iar `ScrollView`-ul din `activity_item.xml` derulează de obicei până la el. Ordinea contează: validarea rulează **înainte** de `Double.parseDouble`, altfel excepția aruncată de parsare ajunge înaintea mesajului tău.

**Greșeala care costă puncte**

1. **Validezi după ce parsezi.** Simptom: aplicația se închide cu `NumberFormatException` înainte să apuci să vezi mesajul. Cauza: `Double.parseDouble` e apelat mai sus în metodă decât `validateForm()`.
2. **Afișezi eroarea, dar salvezi mai departe.** Simptom: apare iconița roșie, dar filmul se salvează oricum și ecranul se închide. Cauza: ai uitat `return` după `setError`.
3. **Nu folosești `trim()`.** Simptom: un câmp cu un singur spațiu trece validarea, iar în listă apare un film cu titlul „ ". Cauza: `" ".isEmpty()` este `false`.

**Verificarea**

Ștergi titlul și apeși Save: rămâi pe formular, câmpul Title are iconiță roșie și mesajul „Titlul este obligatoriu". Scrii un titlu, ștergi bugetul, apeși Save: eroarea se mută pe Budget. Completezi ambele și apeși Save: revii în listă și filmul apare. Mesajul dispare de la sine când apeși din nou Save după ce ai corectat.

**Exersează**

- [17.7](cap-17.html#ex-17-7) — câmpul obligatoriu, varianta completă.
- [19.10](cap-19.html#ex-19-10) — combo de examen: valoare în etichetă plus eroare de validare.

---

## Rețeta 34.6 — Sincronizează două widget-uri

**Cerința, cum sună la test**

„Când switch-ul `swWatched` este pornit, bifează automat `cbOnWatchList`; când este oprit, debifează-l."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `ItemActivity.java` | adaugi `cbonWatchList.setChecked(isChecked)` în listener-ul switch-ului | **da** |
| 2 | `ItemActivity.java` | inversi ordinea a două linii în `fillForm(...)` | **da**, altfel editarea strică datele |
| 3 | `activity_item.xml` | nimic | nu |

**Pașii, în ordine**

**Pasul 1 — sincronizarea, într-o singură direcție.** În `initListeners()`:

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
        cbonWatchList.setChecked(isChecked);
    }
});
```

Un singur sens: switch-ul comandă, checkbox-ul ascultă. Nu pui și listener pe checkbox care să pornească switch-ul.

**Pasul 2 — repari ordinea din `fillForm`.** Codul actual are, în această ordine:

```java
cbonWatchList.setChecked(existing.isOnWatchlist());
swWatched.setChecked(existing.isWatched());
```

După pasul 1, `swWatched.setChecked(...)` declanșează listener-ul, care scrie în checkbox — deci valoarea din model este suprascrisă. Inversați-le:

```java
swWatched.setChecked(existing.isWatched());
cbonWatchList.setChecked(existing.isOnWatchlist());
```

Acum switch-ul se setează primul (și eventual suprascrie checkbox-ul), iar checkbox-ul primește la final valoarea din model. Ultimul care scrie câștigă, iar ultimul este modelul.

**De ce merge așa**

Spre deosebire de `SeekBar`, unde listener-ul primește `fromUser`, `CompoundButton.OnCheckedChangeListener` **nu** are un astfel de parametru: `setChecked(...)` din cod declanșează listener-ul exact ca o atingere a utilizatorului. De aceea sincronizarea se propagă și din `fillForm`. Android nu reapelează listener-ul dacă valoarea cerută este identică cu cea curentă (`setChecked` verifică întâi), ceea ce face ca lanțul să se oprească singur după un pas — cu condiția să existe un singur sens.

**Greșeala care costă puncte**

1. **Sincronizare în ambele sensuri.** Simptom: apeși switch-ul, checkbox-ul se bifează, dar switch-ul sare înapoi pe oprit — sau cele două rămân în stări diferite. Cauza: ai pus un listener și pe checkbox, care îl comandă pe switch. Android blochează re-intrarea pe **același** buton, dar nu între două butoane diferite, așa că rezultatul depinde de ordinea în care se propagă apelurile. Regula simplă: un singur sens, iar al doilea widget doar ascultă.
2. **Nu repari ordinea din `fillForm`.** Simptom: editezi „Inception" (văzut, dar nu pe watchlist), apeși Save fără să atingi nimic, iar filmul apare acum și pe watchlist. Cauza: `swWatched.setChecked(true)` a rulat după `cbonWatchList.setChecked(false)` și a bifat checkbox-ul prin listener.
3. **Pui sincronizarea în `saveMovie()`.** Simptom: în listă valorile sunt corecte, dar în formular checkbox-ul nu se mișcă atunci când apeși switch-ul. Cauza: sincronizarea trebuie să fie în listener, nu la salvare.

**Verificarea**

Deschizi formularul gol: pornești switch-ul → checkbox-ul Watchlist se bifează singur. Oprești → se debifează. Deschizi „Inception" (văzut, nu e pe watchlist): switch-ul e pornit, checkbox-ul rămâne nebifat — modelul nu a fost alterat. Deschizi „The Matrix" (nevăzut, pe watchlist): switch-ul e oprit, checkbox-ul rămâne bifat. Apeși Save fără modificări: în listă, chips-urile rămân aceleași.

**Exersează**

- [19.1](cap-19.html#ex-19-1) — eticheta care urmărește switch-ul.
- [18.1](cap-18.html#ex-18-1) — același tip de legătură, pe `SeekBar`.

---

## Rețeta 34.7 — ArrayAdapter cu toString()

**Cerința, cum sună la test**

„Afișează lista de filme într-un `ListView` folosind `ArrayAdapter` și explică de ce fiecare rând arată `Movie{title='Inception', ...}`."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `MainActivity.java` | câmpul `ArrayAdapter<Movie>`, construirea lui, `setAdapter` | **da** |
| 2 | `MainActivity.java` | `notifyDataSetChanged()` după `add` / `set` | **da** |
| 3 | `activity_main.xml` | nimic — `listView` există deja | nu |
| 4 | `movie_item.xml` | nimic — **nu se folosește** în varianta asta | nu |

**Pașii, în ordine**

**Pasul 1 — câmpul.** În `MainActivity.java`, lângă celelalte câmpuri:

```java
private ListView listView;
private final List<Movie> movies = new ArrayList<>();
private ArrayAdapter<Movie> movieAdapter;
```

**Pasul 2 — construiești adapterul, după ce lista are date.** În `onCreate`, imediat după `addSampleMovies()`:

```java
addSampleMovies();

movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
initControls();
initListeners();
```

Ordinea din repo este: întâi datele, apoi adaptorul. Nu pentru că altfel ar crăpa ceva, ci pentru că așa se citește corect lanțul. Adapterul primește **referința** la listă, nu o copie, iar `ListView` întreabă `getCount()` abia la primul layout, după ce `onCreate` s-a terminat — deci și varianta inversă ar afișa lista completă. Diferența apare doar dacă ai modifica lista după primul layout: atunci ai avea nevoie de `notifyDataSetChanged()`.

**Pasul 3 — îl atașezi pe listă.** În `initControls()`:

```java
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    listView = findViewById(R.id.listView);
    listView.setAdapter(movieAdapter);
}
```

**Pasul 4 — notifici după fiecare modificare.** În callback-ul lui `launcher`:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

**De ce merge așa**

`ArrayAdapter` este un adaptor gata făcut pentru cazul cel mai simplu: o listă de obiecte și un rând cu **un singur `TextView`**. Layout-ul `android.R.layout.simple_list_item_1` are ca rădăcină exact un `TextView`, iar când nu i se dă un ID de câmp, `ArrayAdapter` folosește chiar rădăcina rândului ca text. Fiindcă elementele sunt de tip `Movie`, nu `String`, adaptorul nu are ce text să pună direct — așa că apelează `toString()` pe fiecare element. `Movie.toString()` este generat de IntelliJ și tipărește toate cele zece câmpuri, de unde rândul lung pe care îl vezi. Lista `movies` este aceeași instanță pe care o ține și activitatea, dar `ListView` nu observă modificările din ea: de aceea `notifyDataSetChanged()` este obligatoriu după `add` și `set`.

**Greșeala care costă puncte**

1. **Uiți `notifyDataSetChanged()`.** Simptom: salvezi un film, revii în listă și nu s-a schimbat nimic; închizi și redeschizi aplicația și filmul apare. Cauza: lista s-a modificat, dar `ListView` nu a fost anunțat.
2. **Uiți `setAdapter`.** Simptom: lista arată `Item 1` … `Item 20`, nu filmele. Cauza: `activity_main.xml` are `android:entries="@array/items"`, iar `ListView` își construiește singur un adaptor din acel array când nu i se dă altul. Cele 20 de intrări sunt exact `string-array`-ul `items` din `strings.xml`.
3. **Pui `R.layout.movie_item` în loc de `android.R.layout.simple_list_item_1`.** Simptom: `IllegalStateException: ArrayAdapter requires the resource ID to be a TextView`, la prima afișare. Cauza: rădăcina lui `movie_item.xml` este un `MaterialCardView`, nu un `TextView`, iar `ArrayAdapter` încearcă să trateze tot rândul ca pe un `TextView`. Pentru acel layout ai nevoie de un adaptor propriu — rețeta 34.8.

**Verificarea**

Rulezi aplicația: trei rânduri, fiecare un șir lung care începe cu `Movie{title='Inception'` și continuă cu `release=…, genre='Sci-Fi', budget=1.6E8, …`. Apeși FAB, completezi, salvezi: al patrulea rând apare la final. Apeși pe un rând: formularul se deschide cu datele filmului, iar la salvare rândul își schimbă textul, fără să apară unul nou.

**Exersează**

- [18.8](cap-18.html#ex-18-8) — `Inception (2010)`: `toString()` sau adaptor propriu?
- [24.1](cap-24.html#ex-24-1) — ce se întâmplă exact dacă uiți `notifyDataSetChanged()`.
- [24.2](cap-24.html#ex-24-2) — de ce `set` și nu `add` la editare.

---

## Rețeta 34.8 — BaseAdapter cu ViewHolder

**Cerința, cum sună la test**

„Înlocuiește `ArrayAdapter` cu un `BaseAdapter` propriu, care umple cardul din `movie_item.xml`: titlu, subtitlu, rating, facts și cele trei chips-uri."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` | fișier nou: clasa completă | **da** |
| 2 | `MainActivity.java` | schimbi tipul câmpului și construirea adapterului | **da** |
| 3 | `res/layout/movie_item.xml` | nimic — e complet, doar îl folosești | nu |

**Pașii, în ordine**

**Pasul 1 — creezi pachetul și fișierul.** Click dreapta pe `ro.ase.ie.g1097` → `New → Package`, nume `adapters`. În el, `New → Java Class`, nume `MovieListAdapter`.

**Pasul 2 — scrii clasa completă.** `MovieListAdapter.java`:

```java
package ro.ase.ie.g1097.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.RatingBar;
import android.widget.TextView;

import com.google.android.material.chip.Chip;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieListAdapter extends BaseAdapter {

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private static class ViewHolder {
        TextView movieTitle;
        TextView movieSubtitle;
        RatingBar movieRating;
        TextView movieRatingValue;
        TextView movieFacts;
        Chip chipApproval;
        Chip chipWatched;
        Chip chipWatchlist;
    }

    private final List<Movie> movies;
    private final LayoutInflater layoutInflater;

    public MovieListAdapter(Context context, List<Movie> movies) {
        this.layoutInflater = LayoutInflater.from(context);
        this.movies = movies;
    }

    @Override
    public int getCount() {
        return movies.size();
    }

    @Override
    public Movie getItem(int position) {
        return movies.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;

        if (convertView == null) {
            convertView = layoutInflater.inflate(R.layout.movie_item, parent, false);
            holder = new ViewHolder();
            holder.movieTitle = convertView.findViewById(R.id.movieTitle);
            holder.movieSubtitle = convertView.findViewById(R.id.movieSubtitle);
            holder.movieRating = convertView.findViewById(R.id.movieRating);
            holder.movieRatingValue = convertView.findViewById(R.id.movieRatingValue);
            holder.movieFacts = convertView.findViewById(R.id.movieFacts);
            holder.chipApproval = convertView.findViewById(R.id.chipApproval);
            holder.chipWatched = convertView.findViewById(R.id.chipWatched);
            holder.chipWatchlist = convertView.findViewById(R.id.chipWatchlist);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        bind(holder, getItem(position));
        return convertView;
    }

    private void bind(ViewHolder holder, Movie movie) {
        holder.movieTitle.setText(movie.getTitle());

        String year = movie.getRelease() != null
                ? YEAR_FORMAT.format(movie.getRelease())
                : "";
        holder.movieSubtitle.setText(movie.getGenre() + " · " + year);

        holder.movieRating.setRating(movie.getRating());
        holder.movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

        holder.movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
                movie.getDuration(), movie.getBudget() / 1_000_000));

        String approval = movie.getApproval();
        if (approval != null && !approval.isEmpty()) {
            holder.chipApproval.setText(approval);
            holder.chipApproval.setVisibility(View.VISIBLE);
        } else {
            holder.chipApproval.setVisibility(View.GONE);
        }
        holder.chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
        holder.chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
    }
}
```

**Pasul 3 — schimbi adaptorul în activitate.** În `MainActivity.java`:

```java
import ro.ase.ie.g1097.adapters.MovieListAdapter;

private MovieListAdapter movieAdapter;
```

În `onCreate`:

```java
movieAdapter = new MovieListAdapter(this, movies);
```

În `initControls()`, linia rămâne aceeași:

```java
listView.setAdapter(movieAdapter);
```

Notificările rămân `movieAdapter.notifyDataSetChanged();` — `BaseAdapter` are metoda, ca orice adaptor.

**Pasul 4 — ștergi importul devenit inutil.** `import android.widget.ArrayAdapter;` nu mai e folosit. Nu blochează build-ul, dar lasă avertisment.

**De ce merge așa**

`BaseAdapter` este clasa de bază pentru orice adaptor de `ListView`. Are o singură metodă cu adevărat obligatorie — `getView` — plus `getCount`, pe care trebuie să o implementezi ca să spună câte rânduri există. `ListView` nu creează un rând pentru fiecare element: creează doar câte încap pe ecran și le **reciclează** la derulare, trimițându-le înapoi în `getView` prin parametrul `convertView`. Dacă `convertView` este `null`, rândul trebuie umflat din XML; dacă nu, îl refolosești. Ca să nu cauți cele opt view-uri cu `findViewById` la fiecare refolosire, le pui într-un obiect `ViewHolder` și îl atașezi rândului cu `setTag`. La refolosire, `getTag()` îți dă exact obiectul de data trecută.

**Greșeala care costă puncte**

1. **Uiți `convertView.setTag(holder)`.** Simptom: `NullPointerException` în `getView`, la prima derulare, pe linia `holder.movieTitle`. Cauza: ramura `else` primește un rând reciclat, dar `getTag()` întoarce `null`.
2. **Umflați cu `null` în loc de `parent`.** Simptom: cardul nu se întinde pe toată lățimea, iar `layout_marginHorizontal` pare ignorat. Cauza: `inflate(R.layout.movie_item, null)` nu are de unde lua `LayoutParams`-ul părintelui. Corect este `inflate(R.layout.movie_item, parent, false)`.
3. **Chips-uri fără ramura `else`.** Simptom: derulezi lista, iar un film care nu e pe watchlist apare cu chip-ul „Watchlist" aprins. Cauza: rândul reciclat păstrează vizibilitatea de la filmul anterior. Fiecare chip are nevoie de **ambele** ramuri, `VISIBLE` și `GONE`.

**Verificarea**

Rulezi: trei carduri. Primul: „Inception", „Sci-Fi · 2010", 4.5 stele, „148 min  ·  $160M", chips-urile `PG-13` și `Watched`. Al doilea: „Toy Story", „Animation · 1995", 4.0, „81 min  ·  $30M", `G` și `Watched`. Al treilea: „The Matrix", „Action · 1999", 5.0, „136 min  ·  $63M", `R` și `Watchlist`. Adaugi un film: al patrulea card apare la final, cu datele lui.

**Exersează**

- [18.4](cap-18.html#ex-18-4) — a doua linie în rândul de `ListView`.
- [18.6](cap-18.html#ex-18-6) — URL-ul posterului într-un `TextView` din același card.

---

## Rețeta 34.9 — RecyclerView.Adapter de la zero

**Cerința, cum sună la test**

„Scrie de la zero un `RecyclerView.Adapter` care afișează filmele în `movie_item.xml`, cu `ViewHolder`, `onCreateViewHolder`, `onBindViewHolder` și `getItemCount`."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `adapters/MovieAdapter.java` | fișier nou: clasa completă | **da** |
| 2 | `activity_main.xml` | înlocuiești `<ListView>` cu `<androidx.recyclerview.widget.RecyclerView>` | **da** |
| 3 | `MainActivity.java` | `setLayoutManager` + `setAdapter` | **da** |
| 4 | `gradle/libs.versions.toml`, `build.gradle.kts` | dependența `androidx.recyclerview` | **da**, dacă nu e deja adăugată |

**Pașii, în ordine**

**Pasul 1 — dependența.** `RecyclerView` nu vine cu `appcompat`, spre deosebire de `ListView`. În `gradle/libs.versions.toml`:

```toml
[versions]
recyclerview = "1.4.0"

[libraries]
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

În `build.gradle.kts`, în `dependencies { }`:

```kotlin
implementation(libs.recyclerview)
```

Apoi `Sync Now`.

**Pasul 2 — widget-ul în layout.** În `activity_main.xml`, `<ListView>` devine:

```xml
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

ID-ul rămâne `listView`. Un ID este doar un nume: îl poți păstra ca să nu atingi `findViewById`. Câmpul Java, în schimb, se redenumește în `recyclerView`, pentru că acum ține alt tip de obiect.

**Pasul 3 — clasa adapterului.** `MovieAdapter.java`:

```java
package ro.ase.ie.g1097.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
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

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) {
        this.movies = movies;
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
        holder.bind(movies.get(position));
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

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
            movieTitle = itemView.findViewById(R.id.movieTitle);
            movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
            movieRating = itemView.findViewById(R.id.movieRating);
            movieRatingValue = itemView.findViewById(R.id.movieRatingValue);
            movieFacts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchlist = itemView.findViewById(R.id.chipWatchlist);
        }

        public void bind(Movie movie) {
            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);

            movieRating.setRating(movie.getRating());
            movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

            movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
                    movie.getDuration(), movie.getBudget() / 1_000_000));

            String approval = movie.getApproval();
            if (approval != null && !approval.isEmpty()) {
                chipApproval.setText(approval);
                chipApproval.setVisibility(View.VISIBLE);
            } else {
                chipApproval.setVisibility(View.GONE);
            }
            chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
            chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
        }
    }
}
```

**Pasul 4 — atașarea, în `MainActivity`.** Trei linii, toate obligatorii:

```java
private RecyclerView recyclerView;
private MovieAdapter movieAdapter;

// în onCreate, după addSampleMovies()
movieAdapter = new MovieAdapter(movies);

// în initControls()
recyclerView = findViewById(R.id.listView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));
recyclerView.setAdapter(movieAdapter);
```

Importurile: `androidx.recyclerview.widget.LinearLayoutManager`, `androidx.recyclerview.widget.RecyclerView`, `ro.ase.ie.g1097.adapters.MovieAdapter`.

**Pasul 5 — notificarea.** După `movies.add(movie)` sau `movies.set(position, movie)`:

```java
movieAdapter.notifyDataSetChanged();
```

Merge și `notifyItemInserted`, dar despre diferență e vorba în rețeta 34.14.

**De ce merge așa**

`RecyclerView.Adapter` rupe `getView` în două, ca să separe munca scumpă de munca ieftină. `onCreateViewHolder` rulează o singură dată per rând construit: umflă XML-ul și caută view-urile. `onBindViewHolder` rulează la fiecare afișare a unui rând, inclusiv după reciclare: doar scrie valorile. `getItemCount` spune câte rânduri există. `ViewHolder` nu mai e opțional și nu mai are nevoie de `setTag` — `RecyclerView` îl ține singur. În schimb, `RecyclerView` nu știe **cum** să aranjeze rândurile: de aceea are nevoie de un `LayoutManager`, care se setează separat și obligatoriu.

**Greșeala care costă puncte**

1. **Uiți `setLayoutManager`.** Simptom: ecran alb, fără nicio eroare în Logcat. Cauza: `RecyclerView` are adapter, dar nu are cine să măsoare și să plaseze rândurile. E cea mai scumpă greșeală din capitol, pentru că nu lasă nicio urmă.
2. **`getItemCount()` nu corespunde listei.** Simptom: `IndexOutOfBoundsException` la derulare, nu la pornire. Cauza: ai returnat `movies.size() + 1` sau ai uitat să actualizezi metoda după ce ai schimbat sursa de date.
3. **`onCreateViewHolder` întoarce `null`.** Simptom: `NullPointerException` în `RecyclerView`, imediat după pornire. Cauza: ai scris metoda ca să compileze, fără să returnezi un `ViewHolder`.

**Verificarea**

Rulezi: trei carduri, identice cu cele din rețeta 34.8. Derulezi (dacă ai mai multe filme): rândurile se refolosesc, fără să clipească. Apeși FAB, salvezi: al patrulea card apare. Click pe un card: deocamdată nu se întâmplă nimic — click-ul se leagă în rețeta 34.13.

**Exersează**

- [23.3](cap-23.html#ex-23-3) — scheletul adapterului, pas cu pas.
- [23.4](cap-23.html#ex-23-4) — `MovieViewHolder` cu câmpurile din `movie_item.xml`.
- [23.5](cap-23.html#ex-23-5) — `onCreateViewHolder` cu `inflate`.
- [18.5](cap-18.html#ex-18-5) — migrarea completă, într-un singur răspuns de examen.

---

## Rețeta 34.10 — Migrare completă ListView → RecyclerView

**Cerința, cum sună la test**

„Migrează lista din `ListView` în `RecyclerView`: adaugă dependența, schimbă layout-ul, scrie adapterul și leagă-l în activitate."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `gradle/libs.versions.toml` | versiunea și librăria `recyclerview` | **da** |
| 2 | `build.gradle.kts` | `implementation(libs.recyclerview)` | **da** |
| 3 | `res/layout/activity_main.xml` | `<ListView>` → `<androidx.recyclerview.widget.RecyclerView>` | **da** |
| 4 | `adapters/MovieAdapter.java` | fișier nou, cu `ViewHolder` și callback de click | **da** |
| 5 | `MainActivity.java` | tipul câmpului, `LayoutManager`, `setAdapter`, `notifyItem*` | **da** |
| 6 | `movie_item.xml` | nimic — devine, în sfârșit, folosit | nu |

**Pașii, în ordine**

**Pasul 1 — dependența.** `gradle/libs.versions.toml`, la finalul secțiunii `[versions]`:

```toml
recyclerview = "1.4.0"
```

În `[libraries]`, sub `coordinatorlayout`:

```toml
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

`build.gradle.kts`, în `dependencies { }`, după `implementation(libs.material)`:

```kotlin
implementation(libs.recyclerview)
```

`Sync Now`, apoi `Build → Make Project`. Trebuie `BUILD SUCCESSFUL`, iar în `External Libraries` apare `androidx.recyclerview:recyclerview:1.4.0`.

**Pasul 2 — layout-ul.** În `activity_main.xml`, înlocuiești blocul `<ListView … />` cu:

```xml
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

Două lucruri se schimbă și două rămân:

- se schimbă **tag-ul** — `<ListView>` devine `<androidx.recyclerview.widget.RecyclerView>`;
- dispare `android:entries="@array/items"` — este un atribut de `ListView`; pe `RecyclerView` nu are niciun efect, iar rândurile vin oricum din adapter;
- rămâne `layout_width` / `layout_height` pe `match_parent`;
- rămâne **ID-ul** `listView`. Un ID este doar un nume, iar păstrarea lui înseamnă că `findViewById(R.id.listView)` nu trebuie atins. Câmpul Java se redenumește în `recyclerView`, pentru că acum ține un `RecyclerView` — numele câmpului și ID-ul din XML sunt independente. Dacă vrei totuși să redenumești și ID-ul, folosește `Refactor → Rename`: o redenumire manuală doar în XML lasă `R.id.listView` în Java și build-ul cade.

**Pasul 3 — adapterul.** `adapters/MovieAdapter.java`, fișier complet:

```java
package ro.ase.ie.g1097.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
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

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;
    private final OnItemClickListener listener;

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
        holder.bind(movies.get(position), listener);
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

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
            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);

            movieRating.setRating(movie.getRating());
            movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

            movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
                    movie.getDuration(), movie.getBudget() / 1_000_000));

            String approval = movie.getApproval();
            if (approval != null && !approval.isEmpty()) {
                chipApproval.setText(approval);
                chipApproval.setVisibility(View.VISIBLE);
            } else {
                chipApproval.setVisibility(View.GONE);
            }
            chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
            chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

            itemView.setOnClickListener(v -> {
                int pos = getBindingAdapterPosition();
                if (listener != null && pos != RecyclerView.NO_POSITION) {
                    listener.onItemClick(pos);
                }
            });
        }
    }
}
```

**Pasul 4 — `MainActivity`, câmpurile și importurile.** Scoți `android.widget.AdapterView`, `android.widget.ArrayAdapter` și `android.widget.ListView`; adaugi:

```java
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.g1097.adapters.MovieAdapter;
```

Câmpurile devin:

```java
private FloatingActionButton fabInsert;
private RecyclerView recyclerView;
private ActivityResultLauncher<Intent> launcher;
private final List<Movie> movies = new ArrayList<>();
private MovieAdapter movieAdapter;
```

**Pasul 5 — `onCreate`.** Construirea adapterului și callback-ul:

```java
addSampleMovies();

movieAdapter = new MovieAdapter(movies, this::openItem);
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
                        movieAdapter.notifyItemInserted(movies.size() - 1);
                    } else {
                        movies.set(position, movie);
                        movieAdapter.notifyItemChanged(position);
                    }
                }
            }
        });
```

**Pasul 6 — `initControls`.** Cele trei linii obligatorii:

```java
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    recyclerView = findViewById(R.id.listView);
    recyclerView.setLayoutManager(new LinearLayoutManager(this));
    recyclerView.setAdapter(movieAdapter);
}
```

**Pasul 7 — `initListeners`.** Blocul `listView.setOnItemClickListener(...)` dispare complet: `RecyclerView` nu are așa ceva, iar dacă îl lași, nici măcar nu compilează, pentru că `recyclerView` este alt tip. Rămâne doar FAB-ul:

```java
private void initListeners() {
    fabInsert.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            launcher.launch(intent);
        }
    });
}
```

**Pasul 8 — metoda de click.** O adaugi în `MainActivity`:

```java
private void openItem(int position) {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
}
```

**De ce merge așa**

Migrarea mută trei responsabilități din `ListView` în trei locuri separate. Aranjarea rândurilor trece în `LayoutManager`; construirea și umplerea rândului trec în adapter; click-ul trece dintr-un listener al listei într-un callback al adapterului, pentru că `RecyclerView` nu are `setOnItemClickListener`. `movie_item.xml` era pregătit exact pentru asta: exista în proiect, dar niciun `findViewById`, niciun `LayoutInflater` și niciun adaptor nu îl referea. Acum devine rândul listei, iar `ArrayAdapter` dispare cu tot cu `toString()`.

**Greșeala care costă puncte**

1. **Uiți `setLayoutManager`.** Simptom: ecran alb, FAB vizibil, zero erori. Cauza: `RecyclerView` fără `LayoutManager` nu are cine să aranjeze rândurile. Nu se vede în Logcat, nu se vede în build — doar pe ecran.
2. **`notifyItemInserted(movies.size())`.** Simptom: `IndexOutOfBoundsException: Inconsistency detected`, doar când inserezi, nu la pornire. Cauza: după `add`, ultimul index valid este `movies.size() - 1`.
3. **Rămâne `listView.setOnItemClickListener(...)` în `initListeners`.** Simptom: `cannot find symbol: method setOnItemClickListener`. Cauza: ai schimbat tipul câmpului în `RecyclerView`, dar ai lăsat codul vechi. Șterge blocul întreg, nu doar linia din el.

**Verificarea**

Rulezi: lista arată exact ca înainte de migrare, dar cu carduri, nu cu text lung. Click pe „Inception": formularul se deschide cu datele lui, butonul scrie „Update Movie". Modifici rating-ul, salvezi: doar acel card se schimbă, cu o scurtă animație. FAB, film nou, Save: cardul nou apare la final, cu animație de inserare. Derulezi în jos și în sus: poziția se păstrează.

**Exersează**

- [23.1](cap-23.html#ex-23-1) — dependența, izolat.
- [23.2](cap-23.html#ex-23-2) — `ListView` → `RecyclerView` în layout.
- [23.10](cap-23.html#ex-23-10) — `LayoutManager`, `setAdapter`, `notifyItem*`.
- [18.5](cap-18.html#ex-18-5) — aceeași migrare, într-o singură bucată.

---

## Rețeta 34.11 — GridLayoutManager, două coloane

**Cerința, cum sună la test**

„Afișează filmele pe două coloane, fără să modifici adapterul și fără să atingi layout-ul rândului."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `MainActivity.java` | înlocuiești `LinearLayoutManager` cu `GridLayoutManager` | **da** |
| 2 | `adapters/MovieAdapter.java` | nimic | nu |
| 3 | `res/layout/movie_item.xml` | nimic | nu |

**Pașii, în ordine**

**Pasul 1 — importul.** În `MainActivity.java`:

```java
import androidx.recyclerview.widget.GridLayoutManager;
```

**Pasul 2 — o singură linie.** În `initControls()`, înlocuiești:

```java
recyclerView.setLayoutManager(new LinearLayoutManager(this));
```

cu:

```java
recyclerView.setLayoutManager(new GridLayoutManager(this, 2));
```

**Pasul 3 — verifici că nu ai atins nimic altceva.** Adapterul rămâne `MovieAdapter`, rândul rămâne `movie_item.xml`, `setAdapter` rămâne la fel. Dacă ai simțit nevoia să schimbi ceva în `bind`, ai ieșit din cerință.

**De ce merge așa**

`LayoutManager`-ul este singurul responsabil pentru aranjarea rândurilor. `GridLayoutManager` extinde `LinearLayoutManager` și împarte lățimea disponibilă în `spanCount` coloane; fiecare rând primește lățimea unei coloane, iar `RecyclerView` calculează singur câte rânduri încap. Adapterul nu știe și nu trebuie să știe câte coloane există — el primește în continuare poziții de la 0 la `getItemCount() - 1` și umple același card. De aceea schimbarea e o linie, nu o rescriere.

**Greșeala care costă puncte**

1. **`new GridLayoutManager(this, 0)`.** Simptom: `IllegalArgumentException: spanCount should be at least 1`, la deschiderea ecranului. Cauza: numărul de coloane trebuie să fie cel puțin 1.
2. **Construiești managerul, dar uiți să îl atașezi.** Simptom: ecran alb, fără eroare. Cauza: ai scris `new GridLayoutManager(this, 2);` ca instrucțiune de sine stătătoare, în loc de `recyclerView.setLayoutManager(new GridLayoutManager(this, 2));`.
3. **Pui `GridLayoutManager` pe `ListView`.** Simptom: nu compilează. Cauza: `ListView` are alt sistem de aranjare; rețeta presupune că ai făcut deja migrarea din 34.10.

**Verificarea**

Rulezi: cele trei filme apar câte două pe rând — „Inception" și „Toy Story" sus, „The Matrix" singur pe al doilea rând, în stânga. Fiecare card are jumătate din lățime, iar posterul de 96dp rămâne vizibil. Adaugi un film: se completează a doua coloană a ultimului rând. Întorci telefonul pe orizontală: se văd tot două coloane, mai late.

**Exersează**

- [18.7](cap-18.html#ex-18-7) — `LinearLayoutManager` → `GridLayoutManager`, cu verificarea pe ecran.

---

## Rețeta 34.12 — Antet în listă (două tipuri de rând)

**Cerința, cum sună la test**

„Primul rând al listei să fie un antet care afișează numărul de filme; restul rândurilor rămân cardurile obișnuite."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `adapters/MovieAdapter.java` | constantele de tip, `getItemViewType`, `getItemCount`, `onCreateViewHolder`, `onBindViewHolder`, `HeaderViewHolder` | **da** |
| 2 | `adapters/MovieAdapter.java` | offsetul `- 1` în `bind` și în callback-ul de click | **da** |
| 3 | `MainActivity.java` | nimic — `openItem` primește tot indexul din listă | nu |

**Pașii, în ordine**

**Pasul 1 — două constante și tipul generic.** Sus în `MovieAdapter`, lângă câmpuri:

```java
private static final int TYPE_HEADER = 0;
private static final int TYPE_MOVIE = 1;
```

Declarația clasei se schimbă din `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>` în:

```java
public class MovieAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {
```

Motivul: acum adapterul produce **două** tipuri de `ViewHolder`, deci tipul generic trebuie să fie strămoșul comun.

**Pasul 2 — numărul de rânduri include antetul.** `getItemCount()`:

```java
@Override
public int getItemCount() {
    return movies.size() + 1;
}
```

**Pasul 3 — spui ce tip are fiecare poziție.** Metoda nouă:

```java
@Override
public int getItemViewType(int position) {
    return position == 0 ? TYPE_HEADER : TYPE_MOVIE;
}
```

**Pasul 4 — construiești rândul potrivit.** `onCreateViewHolder`:

```java
@NonNull
@Override
public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
    if (viewType == TYPE_HEADER) {
        TextView header = new TextView(parent.getContext());
        header.setTextSize(16f);
        header.setPadding(32, 32, 32, 16);
        return new HeaderViewHolder(header);
    }

    View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.movie_item, parent, false);
    return new MovieViewHolder(view);
}
```

Antetul e construit direct în cod, ca să nu adaugi un fișier XML întreg pentru un singur `TextView`. Într-un proiect real ai face un `header_item.xml` separat; aici diferența e doar de unde vine view-ul.

**Pasul 5 — umpli rândul potrivit, cu offset.** `onBindViewHolder`:

```java
@Override
public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
    if (holder instanceof HeaderViewHolder) {
        ((HeaderViewHolder) holder).bind(movies.size());
    } else {
        ((MovieViewHolder) holder).bind(movies.get(position - 1), listener);
    }
}
```

`position - 1` este esențial: poziția 0 este antetul, deci primul film stă la poziția 1 din adapter și la indexul 0 din listă.

**Pasul 6 — clasa antetului.** În `MovieAdapter`, lângă `MovieViewHolder`:

```java
static class HeaderViewHolder extends RecyclerView.ViewHolder {

    private final TextView text;

    HeaderViewHolder(@NonNull View itemView) {
        super(itemView);
        text = (TextView) itemView;
    }

    void bind(int count) {
        text.setText("Filme salvate: " + count);
    }
}
```

**Pasul 7 — același offset în callback-ul de click.** În `MovieViewHolder.bind(...)`, ultimul bloc devine:

```java
itemView.setOnClickListener(v -> {
    int pos = getBindingAdapterPosition();
    if (listener != null && pos != RecyclerView.NO_POSITION) {
        listener.onItemClick(pos - 1);
    }
});
```

Fără `- 1`, click-ul pe primul card ar deschide al doilea film, iar click-ul pe ultimul card ar arunca `IndexOutOfBoundsException` în `openItem`.

**De ce merge așa**

`RecyclerView` tratează fiecare tip de rând separat: întreabă `getItemViewType` înainte de a crea un rând, ține un bazin de rânduri reciclate pentru fiecare tip și cheamă `onCreateViewHolder` doar când nu are ce recicla. De aceea antetul și cardurile nu se amestecă niciodată, deși sunt în aceeași listă. Prețul e că toate pozițiile de după antet sunt deplasate cu unu, iar deplasarea trebuie aplicată în două locuri: la citirea filmului și la raportarea poziției către activitate. `getItemCount` trebuie să includă antetul, altfel ultimul film nu se mai afișează.

**Greșeala care costă puncte**

1. **Uiți `position - 1`.** Simptom: click pe „Inception" deschide „Toy Story"; click pe ultimul card închide aplicația cu `IndexOutOfBoundsException`. Cauza: poziția din adapter include antetul, indexul din listă nu.
2. **Uiți `getItemViewType`.** Simptom: lista arată patru rânduri identice cu „Filme salvate: 3" și niciun card. Cauza: implementarea implicită întoarce 0 pentru orice poziție, iar 0 este exact `TYPE_HEADER` — deci toate rândurile sunt tratate ca antet.
3. **Uiți să actualizezi `getItemCount`.** Simptom: antetul nu apare deloc, sau ultimul film lipsește din listă. Cauza: ai schimbat `onCreateViewHolder`, dar numărul de rânduri a rămas `movies.size()`.

**Verificarea**

Rulezi: primul rând scrie „Filme salvate: 3", dedesubt sunt cele trei carduri. Adaugi un film: antetul devine „Filme salvate: 4", iar cardul nou apare la final. Click pe primul card: se deschide „Inception", nu „Toy Story". Click pe ultimul card: se deschide „The Matrix", fără să crape.

**Exersează**

- [23.4](cap-23.html#ex-23-4) — `ViewHolder`-ul cu câmpurile din card.
- [23.8](cap-23.html#ex-23-8) — elemente condiționate în rând, aceeași logică de tipuri.

---

## Rețeta 34.13 — Click în adaptor, cu callback către activitate

**Cerința, cum sună la test**

„La click pe un card, deschide filmul în `ItemActivity`, în modul de editare. Adapterul nu are voie să cunoască activitatea."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `adapters/MovieAdapter.java` | interfața `OnItemClickListener`, câmpul, parametrul din constructor, click-ul din `bind` | **da** |
| 2 | `MainActivity.java` | `new MovieAdapter(movies, this::openItem)` + metoda `openItem(int)` | **da** |
| 3 | `MainActivity.java` | ștergi `listView.setOnItemClickListener(...)` | **da** |

**Pașii, în ordine**

**Pasul 1 — contractul, declarat în adapter.** Sus în `MovieAdapter`:

```java
public interface OnItemClickListener {
    void onItemClick(int position);
}
```

**Pasul 2 — câmpul și constructorul.** Adapterul primește listener-ul o singură dată, la construire:

```java
private final List<Movie> movies;
private final OnItemClickListener listener;

public MovieAdapter(List<Movie> movies, OnItemClickListener listener) {
    this.movies = movies;
    this.listener = listener;
}
```

**Pasul 3 — îl transmiți mai departe.** `onBindViewHolder`:

```java
@Override
public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
    holder.bind(movies.get(position), listener);
}
```

**Pasul 4 — legi click-ul în `bind`, nu în constructor.** Metoda `bind` din `MovieViewHolder`, completă:

```java
public void bind(Movie movie, OnItemClickListener listener) {
    movieTitle.setText(movie.getTitle());

    String year = movie.getRelease() != null
            ? YEAR_FORMAT.format(movie.getRelease())
            : "";
    movieSubtitle.setText(movie.getGenre() + " · " + year);

    movieRating.setRating(movie.getRating());
    movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));

    movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
            movie.getDuration(), movie.getBudget() / 1_000_000));

    String approval = movie.getApproval();
    if (approval != null && !approval.isEmpty()) {
        chipApproval.setText(approval);
        chipApproval.setVisibility(View.VISIBLE);
    } else {
        chipApproval.setVisibility(View.GONE);
    }
    chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
    chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

    itemView.setOnClickListener(v -> {
        int pos = getBindingAdapterPosition();
        if (listener != null && pos != RecyclerView.NO_POSITION) {
            listener.onItemClick(pos);
        }
    });
}
```

`onCreateViewHolder`, `getItemCount` și constructorul `MovieViewHolder` rămân cele din rețeta 34.9.

**Pasul 5 — activitatea implementează contractul.** În `MainActivity.onCreate`:

```java
movieAdapter = new MovieAdapter(movies, this::openItem);
```

Metoda `openItem`, adăugată în `MainActivity`:

```java
private void openItem(int position) {
    Intent intent = new Intent(MainActivity.this, ItemActivity.class);
    intent.putExtra(MOVIE_EXTRA, movies.get(position));
    intent.putExtra(POSITION_EXTRA, position);
    launcher.launch(intent);
}
```

`this::openItem` este o metodă-referință: are aceeași semnătură ca metoda din interfață (`int` → `void`), deci compilatorul o acceptă în locul unei clase anonime.

**Pasul 6 — ștergi click-ul vechi.** În `initListeners()`, blocul `listView.setOnItemClickListener(...)` dispare. `RecyclerView` nu are metoda, iar dacă ai făcut migrarea din 34.10, nici nu compilează.

**De ce merge așa**

`RecyclerView` nu are `setOnItemClickListener` — decizie de design, pentru că un rând poate avea mai multe zone click-abile, iar un listener global ar fi ambiguu. Soluția este ca adapterul să își declare propria interfață, iar activitatea să o implementeze. Adapterul nu cunoaște `MainActivity`, `Intent` sau `ItemActivity`: știe doar să anunțe „s-a apăsat poziția N". Poziția se citește **la momentul click-ului**, cu `getBindingAdapterPosition()`, nu la `bind`, pentru că între timp lista se poate schimba. `NO_POSITION` (`-1`) apare în timpul animațiilor de inserare sau ștergere, când rândul nu mai are o poziție validă.

**Greșeala care costă puncte**

1. **Legi click-ul în constructorul `ViewHolder`.** Simptom: după prima derulare, click pe un card deschide alt film. Cauza: `getBindingAdapterPosition()` ar fi evaluat o singură dată, la crearea rândului, și rămâne în urmă la reciclare.
2. **Folosești parametrul `position` din `onBindViewHolder` în lambda.** Simptom: după ce inserezi un film, click-urile deschid filmul vecin. Cauza: poziția a fost capturată la legare, iar inserarea a deplasat toate pozițiile de după ea.
3. **Nu verifici `NO_POSITION`.** Simptom: `IndexOutOfBoundsException` dacă apeși un card exact în timpul animației de inserare. Cauza: `movies.get(-1)`.

**Verificarea**

Rulezi: click pe fiecare card, în ordine — se deschide filmul corect, cu datele lui, iar butonul scrie „Update Movie". Derulezi până jos și înapoi, apeși din nou: tot corect. Adaugi un film, apoi apeși imediat pe el: se deschide filmul nou, nu vecinul.

**Exersează**

- [23.9](cap-23.html#ex-23-9) — click cu `getBindingAdapterPosition()` și callback.
- [20.7](cap-20.html#ex-20-7) — buton „Edit" în card, în locul atingerii întregului rând.

---

## Rețeta 34.14 — notifyItem* vs notifyDataSetChanged

**Cerința, cum sună la test**

„După Save, lista să se actualizeze corect, cu animație, fără să-și piardă poziția de derulare."

**Fișierele atinse**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `MainActivity.java` | în callback-ul lui `launcher`, înlocuiești `notifyDataSetChanged()` cu `notifyItemInserted` / `notifyItemChanged` | **da** |
| 2 | `adapters/MovieAdapter.java` | nimic — metodele vin din `RecyclerView.Adapter` | nu |

**Pașii, în ordine**

**Pasul 1 — ramura de inserare.** În callback-ul lui `launcher`:

```java
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyItemInserted(movies.size() - 1);
} else {
    movies.set(position, movie);
    movieAdapter.notifyItemChanged(position);
}
```

**Pasul 2 — ștergerea, dacă cerința o cere.** Pentru un film scos din listă, ordinea este aceeași — întâi modifici lista, apoi notifici:

```java
movies.remove(position);
movieAdapter.notifyItemRemoved(position);
```

**Pasul 3 — verifici că nu a rămas niciun `notifyDataSetChanged()`** în callback. Un singur apel rămas anulează beneficiul celorlalte: `RecyclerView` rebindează tot și pierde animațiile.

**Tabelul de corespondență:**

| Ce faci cu lista | Metoda | Ce index primește |
|---|---|---|
| adaugi la final | `notifyItemInserted(index)` | indexul elementului nou, adică `movies.size() - 1` după `add` |
| modifici un element | `notifyItemChanged(index)` | indexul elementului modificat |
| ștergi un element | `notifyItemRemoved(index)` | indexul **vechi** al elementului șters |
| muți un element | `notifyItemMoved(from, to)` | ambele poziții |
| înlocuiești tot conținutul | `notifyDataSetChanged()` | niciunul |

**De ce merge așa**

`notifyDataSetChanged()` nu spune **ce** s-a schimbat, doar că ceva s-a schimbat: `RecyclerView` consideră toate rândurile invalide, le rebindează pe toate, anulează animațiile în curs și poate pierde poziția de derulare. `notifyItemInserted(index)` spune exact unde a apărut un element nou: `RecyclerView` inserează un singur rând, rulează animația de inserare, păstrează celelalte rânduri neatinse și păstrează derularea. Toate metodele `notifyItem*` presupun că lista a fost **deja** modificată — ele anunță o schimbare petrecută, nu o produc.

**Greșeala care costă puncte**

1. **`notifyItemInserted(movies.size())` după `add`.** Simptom: `IndexOutOfBoundsException: Inconsistency detected. Invalid item position`, doar la inserare. Cauza: după `add`, ultimul index valid este `movies.size() - 1`; ai notificat un index care nu există.
2. **Notifici înainte să modifici lista.** Simptom: aceeași excepție de inconsistență, sau un rând gol care apare și dispare. Cauza: `RecyclerView` validează numărul de elemente în momentul notificării; dacă lista nu s-a schimbat încă, numărul nu corespunde.
3. **Apeși `notifyDataSetChanged()` „ca să fie sigur".** Simptom: totul funcționează, dar fără animații, iar derularea poate sări la începutul listei la fiecare salvare. Cauza: notificarea globală invalidează toate rândurile, deci `RecyclerView` nu mai are ce poziție să păstreze.

**Verificarea**

Derulezi lista până la ultimul film, apeși FAB, salvezi: cardul nou apare la final cu o animație scurtă, iar lista rămâne derulată aproape de unde erai. Editezi un film din mijloc: doar cardul acela își schimbă valorile, cu o scurtă evidențiere, iar celelalte nu clipesc. Ștergi un film (dacă ai implementat ștergerea): cardul dispare cu animație, iar lista se strânge.

**Exersează**

- [24.1](cap-24.html#ex-24-1) — ce se întâmplă dacă uiți notificarea.
- [24.2](cap-24.html#ex-24-2) — de ce `set` și nu `add` la editare.
- [24.9](cap-24.html#ex-24-9) — filmul care apare de două ori după editare.
- [19.9](cap-19.html#ex-19-9) — lista nu are voie să arate date vechi după editare.

---

## Rețeta 34.15 — Atașează un eveniment pe orice widget

**Cerința, cum sună la test:** „Când apeși butonul X, să se întâmple Y" sau „când miști slider-ul, eticheta să se actualizeze."

**Fișierele atinse:**

| # | Fișier | Ce faci | Obligatoriu? |
|---|---|---|---|
| 1 | `res/layout/activity_item.xml` | widgetul, cu `android:id` | doar dacă e widget nou |
| 2 | `activities/ItemActivity.java` | câmpul, linia din `initControls()`, listener-ul în `initListeners()` | **da** |

**Pașii, în ordine:**

**Pasul 1 — alege listener-ul după tipul widgetului.** Nu există un singur listener; fiecare widget are al lui. Tabelul de mai jos e tot ce ai nevoie.

| Widget | Metoda de atașare | Ce primești în callback |
|---|---|---|
| `Button`, `MaterialButton`, orice `View` | `setOnClickListener` | `View v` — view-ul apăsat |
| `EditText` | `addTextChangedListener` | `s`, `start`, `before`, `count` |
| `SeekBar` | `setOnSeekBarChangeListener` | `progress`, `fromUser` |
| `RatingBar` | `setOnRatingBarChangeListener` | `rating`, `fromUser` |
| `Switch`, `MaterialSwitch`, `CheckBox` | `setOnCheckedChangeListener` | `buttonView`, `isChecked` |
| `RadioGroup` | `setOnCheckedChangeListener` | `group`, `checkedId` |
| `Spinner` | `setOnItemSelectedListener` | `parent`, `view`, `position`, `id` |
| `ListView` | `setOnItemClickListener` | `parent`, `view`, `position`, `id` |
| `ListView` (apăsare lungă) | `setOnItemLongClickListener` | la fel, dar întoarce `boolean` |

**Pasul 2 — atașează listener-ul în `initListeners()`, nu în `onCreate()`.** În `G1097`, `onCreate()` cheamă `initControls()` apoi `initListeners()`. Ordinea contează: în `initListeners()` widgeturile sunt deja legate prin `findViewById`, deci nu riști `NullPointerException`.

```java
private void initListeners() {
    btMovieAction.setOnClickListener(v -> saveMovie());
    sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
        @Override
        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
            tvDurationValue.setText(progress + " min");
        }
        @Override public void onStartTrackingTouch(SeekBar seekBar) { }
        @Override public void onStopTrackingTouch(SeekBar seekBar) { }
    });
}
```

**Pasul 3 — scrie corpul evenimentului.** Trei forme, toate corecte; alege-o pe cea care se citește mai bine:

```java
// 1. clasă anonimă — explicită, merge pentru orice interfață
btMovieAction.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        saveMovie();
    }
});

// 2. lambda — doar pentru interfețe cu O SINGURĂ metodă (interfețe funcționale)
btMovieAction.setOnClickListener(v -> saveMovie());

// 3. referință la metodă — când metoda are exact semnătura cerută
btMovieAction.setOnClickListener(this::onSaveClicked);
```

`View.OnClickListener` are o singură metodă (`onClick`), deci merge lambda. `SeekBar.OnSeekBarChangeListener` are trei, deci **nu** merge lambda — ai nevoie de clasa anonimă cu toate trei, chiar dacă două rămân goale.

**Pasul 4 — dacă evenimentul trebuie să citească valoarea altui widget**, citește-o în interiorul callback-ului, nu în afara lui:

```java
// CORECT: citești la momentul click-ului
btMovieAction.setOnClickListener(v ->
        Toast.makeText(this, etTitle.getText().toString(), Toast.LENGTH_SHORT).show());

// GREȘIT: citești o singură dată, la atașare — valoarea rămâne cea de atunci
String title = etTitle.getText().toString();
btMovieAction.setOnClickListener(v ->
        Toast.makeText(this, title, Toast.LENGTH_SHORT).show());
```

**De ce merge așa:** un listener nu este „un eveniment" — este **un obiect pe care îl dai unui widget**, iar widgetul îl cheamă când se întâmplă ceva. Tu nu apeși niciodată `onClick()`; îl apelează Android-ul, din firul principal, după ce a primit evenimentul de la sistem. De aceea codul din callback rulează *mai târziu*, nu la atașare — și de aceea trebuie să citești starea acolo, nu înainte.

**Greșeala care costă puncte:**

- **Listener pus înainte de `setContentView`** → `findViewById` întoarce `null` → `NullPointerException` la prima atingere. În `G1097` ordinea e corectă; dacă adaugi cod în `onCreate`, pune-l după `initControls()`.
- **Lambda pe o interfață cu mai multe metode** → nu compilează. `SeekBar.OnSeekBarChangeListener` are trei metode; folosește clasa anonimă.
- **Valoare citită în afara callback-ului** → evenimentul folosește valoarea veche. Citește în interior.
- **Listener care se auto-declanșează** → `setChecked(true)` din cod apelează `onCheckedChanged` exact ca o atingere. Dacă în callback faci iar `setChecked`, intri în buclă. Verifică `fromUser` sau un steag `boolean isBinding`.

**Verificarea:** rulezi, apeși widgetul, vezi efectul. Apoi schimbi valoarea **din cod** (în `fillForm`) și verifici că listener-ul nu strică ce a pus `fillForm`.

**Exersează:** [20.1](cap-20.html#ex-20-1), [18.1](cap-18.html#ex-18-1), [19.1](cap-19.html#ex-19-1)

---

## Tabelul celor 15 rețete

| # | Rețeta | Cerința tipică | Fișiere atinse | Minute |
|---|---|---|---|---|
| 34.1 | Leagă o valoare de o etichetă, în timp real | slider → etichetă, la fiecare mișcare | `ItemActivity.java` | 5 |
| 34.2 | Leagă o valoare la inițializare | eticheta pornește de la starea widget-ului | `ItemActivity.java` | 5 |
| 34.3 | Citește un widget în model, la salvare | Save → obiect `Movie` complet | `ItemActivity.java` | 10 |
| 34.4 | Arată sau ascunde un widget condiționat | etichetă vizibilă doar când switch-ul e pornit | `ItemActivity.java` | 5 |
| 34.5 | Validare cu mesaj de eroare | titlu gol / buget nevalid → `setError` | `ItemActivity.java` | 10 |
| 34.6 | Sincronizează două widget-uri | switch → checkbox | `ItemActivity.java` | 5 |
| 34.7 | ArrayAdapter cu `toString()` | listă simplă, un text per rând | `MainActivity.java` | 5 |
| 34.8 | BaseAdapter cu ViewHolder | card complet pe `ListView` | `adapters/MovieListAdapter.java`, `MainActivity.java` | 20 |
| 34.9 | RecyclerView.Adapter de la zero | card complet pe `RecyclerView` | `adapters/MovieAdapter.java`, `activity_main.xml`, `MainActivity.java` | 20 |
| 34.10 | Migrare completă ListView → RecyclerView | dependență + layout + adapter + activitate | 5 fișiere | 25 |
| 34.11 | GridLayoutManager, două coloane | listă pe două coloane | `MainActivity.java` | 3 |
| 34.12 | Antet în listă | două tipuri de rând | `adapters/MovieAdapter.java` | 15 |
| 34.13 | Click în adaptor, cu callback | card → `ItemActivity` | `adapters/MovieAdapter.java`, `MainActivity.java` | 10 |
| 34.14 | notifyItem* vs notifyDataSetChanged | actualizare cu animație | `MainActivity.java` | 5 |
| 34.15 | Atașează un eveniment pe orice widget | „când apeși X, să se întâmple Y" | `ItemActivity.java` | 5 |

---

## Rezumat capitol 34

**Lanțul de care depinde totul.** Un binding are trei verigi: view-ul din XML (cu ID), referința din Java (`findViewById`, după `setContentView`) și momentul în care legătura se activează (listener sau apel explicit). Dacă lipsește oricare, codul compilează și nu face nimic.

**Ordinea care nu se negociază.** `setContentView` → `initControls` → `initListeners` → `fillForm`. `initListeners` înainte de `fillForm` face ca legăturile să prindă și valorile puse din cod. După ce adaugi sincronizări între widget-uri, ordinea liniilor din `fillForm` devine parte din logică: ultimul care scrie câștigă.

**Adaptorul, pe scurt.** `ArrayAdapter` pentru un singur `TextView` și `toString()`. `BaseAdapter` pentru mai multe view-uri pe `ListView`: `getView` + `convertView` + `ViewHolder` + `setTag`. `RecyclerView.Adapter` pentru mai multe view-uri pe `RecyclerView`: `onCreateViewHolder` + `onBindViewHolder` + `getItemCount` + `ViewHolder` obligatoriu.

**Trei lucruri pe care `RecyclerView` nu le iartă:**

1. Fără `setLayoutManager` — listă goală, fără eroare.
2. Fără `notifyItem*` după modificarea listei — lista nu se actualizează.
3. `getItemCount()` care nu corespunde listei — `IndexOutOfBoundsException` la derulare, nu la pornire.

**Ce spui când ți se cere să explici**

| Întrebare | Răspunsul scurt |
|---|---|
| De ce eticheta se actualizează fără să o ating? | listener-ul se apelează la orice schimbare, inclusiv `setProgress` / `setChecked` din cod |
| De ce `View.GONE` și nu `INVISIBLE`? | `GONE` scoate view-ul din layout, `INVISIBLE` îi păstrează spațiul |
| De ce `setError` nu oprește salvarea singur? | atașează un mesaj view-ului; oprirea o face `return`-ul tău |
| De ce `fillForm` trebuie să țină cont de listener? | `setChecked` din cod declanșează listener-ul exact ca o atingere |
| De ce rândul de `ArrayAdapter` arată `Movie{...}`? | adaptorul cheamă `toString()` pe fiecare element |
| De ce `ViewHolder`? | cache de referințe, ca să nu cauți view-urile la fiecare derulare |
| De ce `setLayoutManager`? | `RecyclerView` nu știe singur cum să aranjeze rândurile |
| De ce click-ul e în `bind`, nu în constructor? | poziția se schimbă la reciclare; în `bind` e citită la momentul click-ului |
| De ce `getBindingAdapterPosition()` poate da `-1`? | rândul nu are poziție validă în timpul unei animații |
| De ce `notifyItemInserted` și nu `notifyDataSetChanged`? | notificarea fină rebindează un singur rând și păstrează animațiile |

**Checklist final, înainte să închizi examenul**

- [ ] Am rulat aplicația: formular gol, formular editat, salvare, listă.
- [ ] Fiecare `findViewById` are un ID care există în XML.
- [ ] Fiecare ramură `if` care schimbă vizibilitatea are și `else`.
- [ ] `setLayoutManager` e apelat înainte de `setAdapter`.
- [ ] După fiecare `add` / `set` / `remove` există o notificare.
- [ ] Nu a rămas niciun `notifyDataSetChanged()` acolo unde cerința cere animație.
- [ ] `ItemActivity` folosește `findViewById`, nu `ActivityItemBinding` — importul acela e mort în repo.
