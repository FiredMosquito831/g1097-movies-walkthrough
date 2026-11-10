# Capitolul 07 — `ItemActivity`: citirea și scrierea formularului

**Obiectiv:** `ItemActivity` completă — leagă cele 13 câmpuri, afișează `DatePickerDialog`, actualizează valorile live (durată, switch) și construiește un `Movie` la Save.

**Timp estimat:** 45–60 min.

**Fișier final:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` (8306 B, SHA-256 `5d48a48e8bcb460d…`)

> **Atenție:** la acest capitol `ItemActivity` **nu are încă** `fillForm` (modul editare) — asta vine în cap. 09. Aici doar **insert mode**: câmpuri goale → completezi → Save.

---

## Pasul 7.1 — Creează clasa și declară-o în manifest

### De ce

`ItemActivity` e al doilea ecran. Trebuie să existe ca fișier **și** să fie declarată în manifest, altfel `startActivity` aruncă `ActivityNotFoundException`.

### Cum

1. Click dreapta pe pachetul `ro.ase.ie.g1097.activities` → **New → Java Class** → `ItemActivity`.
2. În `AndroidManifest.xml`, adaugă în `<application>`:

```xml
<activity
    android:name=".activities.ItemActivity"
    android:exported="false"
    android:windowSoftInputMode="adjustResize" />
```

### De ce `exported="false"`

`ItemActivity` nu se pornește din launcher. Doar din `MainActivity`, prin `Intent`. Dacă ar fi `true`, orice aplicație de pe telefon ar putea-o deschide — risc de securitate.

> **De reținut:** `exported="true"` doar pentru activitatea de launcher (și pentru cele care primesc `intent-filter` extern). Toate celelalte: `false`.

---

## Pasul 7.2 — Scheletul și câmpurile

### De ce

`ItemActivity` are nevoie de referințe la 13 view-uri, plus 3 câmpuri de stare (`position`, `releaseCal`, `dateFormat`).

### Cum

```java
package ro.ase.ie.g1097.activities;

import android.app.DatePickerDialog;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.RatingBar;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.IntentCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.materialswitch.MaterialSwitch;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

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

    private int position = -1;   // -1 = insert mode
    private Calendar releaseCal = Calendar.getInstance();
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_item);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        initControls();
        initListeners();
    }

    private void initControls() {
        // pasul 7.3
    }

    private void initListeners() {
        // pasul 7.4
    }

    private void saveMovie() {
        // pasul 7.8
    }

    private void showReleaseDatePicker() {
        // pasul 7.7
    }
}
```

### De ce `position = -1`

E un **sentinel** (valoare specială). `-1` înseamnă „nu editez nimic, creez un film nou”. Orice valoare ≥ 0 înseamnă „editez filmul de la poziția asta”. Vezi cap. 09.

### De ce `releaseCal = Calendar.getInstance()`

Data implicită = **acum**. Dacă utilizatorul nu alege o dată, filmul primește data curentă. Alternativa ar fi `null`, dar atunci `saveMovie` ar pune `null` în model și `fillForm` ar crăpa.

### De ce `dateFormat` e `final`

`SimpleDateFormat` e **mutabil** și **nu e thread-safe**. Aici e folosit doar în UI thread, deci e OK. `final` garantează că nu e reasignat.

> **De reținut:** `SimpleDateFormat` cu `Locale.getDefault()` respectă limba telefonului. Pentru un format fix indiferent de limbă, folosești `Locale.US`.

### De ce `IntentCompat` și nu direct

`getSerializableExtra(String)` e **depreciat** în API 33+. `IntentCompat.getSerializableExtra(intent, key, Class)` e varianta modernă, care cere explicit tipul clasei. Vezi cap. 09.

---

## Pasul 7.3 — `initControls`: cele 13 `findViewById`

### De ce

Fiecare câmp din cod trebuie legat de view-ul din XML. Fără asta, ai `null` și NPE la primul acces.

### Cum

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

### Capcana numelor diferite

Observă:

| Câmp Java | ID din XML | De ce diferă |
|---|---|---|
| `cbonWatchList` | `cbOnWatchList` | nume ales de profesor; nu urmează convenția |
| `btMovieAction` | `btnMovieAction` | `bt` vs `btn` |
| `etTitle` | `etTitle` | la fel |

**Nu e o greșeală** — e o inconsecvență de numire. Dar trebuie să le respecți **exact**, altfel `findViewById` întoarce `null`.

> **De reținut:** ID-ul din XML și numele câmpului Java sunt **independente**. Convenția `et`/`sp`/`sb`/`rb`/`rg`/`cb`/`sw`/`tv`/`btn` e doar o convenție de citire, nu o regulă a limbajului.

### Exercițiu 7.3

**Cerință:** ce se întâmplă dacă scrii `findViewById(R.id.etTitl)` (typo)? Când apare eroarea?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am introdus un typo în ID.

**Ce se întâmplă:** **eroare de compilare**, imediat:

```
error: cannot find symbol
variable etTitl
location: class R.id
```

**De ce:** `R.id.etTitl` nu există în clasa `R` generată. Compilatorul știe toate ID-urile din XML — dacă nu-l găsește, nu compilează.

**De reținut:**
1. `R.id.*` e **verificat la compilare**. Un ID greșit nu ajunge niciodată la runtime.
2. Dacă în schimb **ID-ul din XML lipsește** (ai uitat `android:id`), compilarea trece, dar `findViewById` întoarce `null` → NPE la runtime.
3. Deci: eroare de compilare = ID inexistent; NPE = ID existent dar view-ul nu e în layout-ul curent.

**Unde revine:** în cap. 09, `fillForm` folosește toate cele 13 câmpuri. Un `null` acolo dă NPE la `etTitle.setText(...)`.

</details>

---

## Pasul 7.4 — `initListeners`: click pe dată și pe buton

### De ce

Două acțiuni:
- click pe câmpul Release → deschide calendarul;
- click pe Save → salvează și închide.

### Cum

```java
private void initListeners() {
    etRelease.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            showReleaseDatePicker();
        }
    });
    btMovieAction.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            saveMovie();
        }
    });
}
```

### De ce `setOnClickListener` pe un `EditText`

Un `EditText` primește focus la atingere, **nu** click. Dar `setOnClickListener` funcționează: la prima atingere, primește focus **și** declanșează click-ul.

> **Capcană:** dacă `EditText`-ul are `android:focusable="false"`, click-ul nu mai ajunge. Aici nu e cazul.

### Sintaxa veche vs lambda

Repo-ul folosește `new View.OnClickListener() { ... }` — sintaxa **anonimă clasică**. Echivalentul modern:

```java
etRelease.setOnClickListener(v -> showReleaseDatePicker());
btMovieAction.setOnClickListener(v -> saveMovie());
```

Ambele compilează. Repo-ul păstrează stilul vechi pentru claritate didactică (se vede tipul).

> **De reținut:** lambda e disponibilă din Java 8. Proiectul are `VERSION_11`, deci merge. Dar la test, dacă ți se cere „scrie listener-ul”, ambele forme sunt acceptate.

### Exercițiu 7.4

**Cerință:** rescrie ambii listeneri cu lambda. Verifică că merge.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit clasele anonime cu expresii lambda.

```java
private void initListeners() {
    etRelease.setOnClickListener(v -> showReleaseDatePicker());
    btMovieAction.setOnClickListener(v -> saveMovie());
}
```

**De ce merge:** `View.OnClickListener` e o **interfață funcțională** — are o singură metodă abstractă (`onClick(View)`). Lambda e permisa oriunde e o interfață funcțională.

**De reținut:**
1. Lambda = formă scurtă pentru o clasă anonimă cu **o singură metodă**.
2. Parametrul `v` e `View`-ul care a declanșat click-ul. Nu-l folosim aici.
3. `this` într-o clasă anonimă se referă la clasa anonimă; într-o lambda, la **clasa exterioară**. E o diferență importantă: dacă ai avea nevoie de `ItemActivity.this`, lambda e mai sigură.

**Unde revine:** în cap. 11, `MovieAdapter` folosește lambda pentru `itemView.setOnClickListener(v -> ...)`. Acolo `this` ar fi fost ambiguu.

</details>

---

## Pasul 7.5 — Listener pe `SeekBar`

### De ce

Când miști bara, textul `tvDurationValue` trebuie să arate valoarea curentă. Fără listener, rămâne „0 min”.

### Cum

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

### De ce trei metode

`OnSeekBarChangeListener` are **trei** metode abstracte — nu e interfață funcțională, deci **nu poți folosi lambda**. Trebuie să implementezi toate trei, chiar dacă două rămân goale.

| Metodă | Când se apelează |
|---|---|
| `onProgressChanged` | la fiecare schimbare de valoare |
| `onStartTrackingTouch` | când pui degetul pe mâner |
| `onStopTrackingTouch` | când ridici degetul |

### Parametrul `fromUser`

`true` = schimbarea vine de la utilizator (a tras de bară).
`false` = schimbarea vine din cod (`setProgress(...)`).

Repo-ul **ignoră** parametrul — actualizează textul în ambele cazuri. Asta e de fapt **corect**: vrei ca textul să reflecte valoarea indiferent de sursă. Vezi cap. 09, unde `setProgress` din `fillForm` declanșează și el actualizarea.

### Exercițiu 7.5

**Cerință:** modifică listener-ul să afișeze „0 min” când progress e 0, și „N min.” altfel. De ce e o idee bună?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat o condiție pe `progress`.

```java
@Override
public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
    if (progress == 0) {
        tvDurationValue.setText("0 min");
    } else {
        tvDurationValue.setText(progress + " min.");
    }
}
```

**De ce e o idee bună:** consistență cu layout-ul. În XML, `tvDurationValue` are `android:text="0 min"` (fără punct). Dacă listener-ul ar scrie mereu „N min.”, la prima atingere ai avea „0 min.” — o schimbare vizuală fără sens.

**De reținut:**
1. Textul inițial din XML și textul generat de cod trebuie să fie **consistente**.
2. `progress + " min."` face **concatenare** `int` + `String` → `String`. Nu e adunare.
3. Pentru plural corect („1 min” vs „2 min”), ai nevoie de `getResources().getQuantityString(...)`.

**Unde revine:** în `movie_item.xml` (cap. 11), `movieFacts` afișează `duration + " min."` — aceeași convenție.

</details>

---

## Pasul 7.6 — Listener pe `MaterialSwitch`

### De ce

Când comuți switch-ul, textul `tvWatchedValue` trebuie să arate „Yes” / „No”.

### Cum

```java
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});
```

### De ce `CompoundButton.OnCheckedChangeListener`

`MaterialSwitch` extinde `SwitchCompat` → `CompoundButton`. Listener-ul e definit pe `CompoundButton`, deci merge pe **orice** subclasă: `Switch`, `CheckBox`, `RadioButton`, `ToggleButton`.

> **De reținut:** `setOnCheckedChangeListener` e definit pe `CompoundButton`. De aceea funcționează identic pe switch și pe checkbox.

### Operatorul ternar

`isChecked ? "Yes" : "No"` = formă scurtă pentru `if/else` care returnează o valoare.

### Exercițiu 7.6

**Cerință:** adaugă un listener similar pe `cbonWatchList` care schimbă textul unui `TextView` nou (`tvWatchlistValue`) între „On list” și „Not on list”. Trebuie să adaugi și `TextView`-ul în layout.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat în `activity_item.xml`, lângă checkbox:

```xml
<TextView
    android:id="@+id/tvWatchlistValue"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Not on list"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorPrimary" />
```

și în `ItemActivity`:

```java
private TextView tvWatchlistValue;
// în initControls:
tvWatchlistValue = findViewById(R.id.tvWatchlistValue);
// în initListeners:
cbonWatchList.setOnCheckedChangeListener((buttonView, isChecked) ->
        tvWatchlistValue.setText(isChecked ? "On list" : "Not on list"));
```

**De ce merge:** `CompoundButton.OnCheckedChangeListener` e comun pentru switch și checkbox.

**De reținut:**
1. Aici ai folosit **lambda** — `OnCheckedChangeListener` are o singură metodă, deci e funcțională.
2. La `SeekBar` nu ai putut, pentru că are trei metode.
3. Regula: **o metodă abstractă = lambda permisă**.

**Unde revine:** în cap. 11, `MovieAdapter` nu mai are nevoie de listeneri pe switch/checkbox — starea e doar afișată prin `Chip`-uri.

</details>

---

## Pasul 7.7 — `DatePickerDialog`

### De ce

Data se alege dintr-un calendar, nu se tastează. `DatePickerDialog` e dialogul standard Android.

### Cum

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

    new DatePickerDialog(
            this,
            new DatePickerDialog.OnDateSetListener() {
                @Override
                public void onDateSet(DatePicker view, int year, int month, int day) {
                    releaseCal.set(year, month, day);
                    etRelease.setError(null);
                    etRelease.setText(dateFormat.format(releaseCal.getTime()));
                }
            },
            releaseCal.get(Calendar.YEAR),
            releaseCal.get(Calendar.MONTH),
            releaseCal.get(Calendar.DAY_OF_MONTH)
    ).show();
}
```

### Fluxul, pas cu pas

1. **Citește textul curent** din `etRelease`.
2. **Dacă nu e gol**, încearcă să-l parseze cu `dateFormat`. Dacă reușește, actualizează `releaseCal`.
3. **Deschide dialogul**, poziționat pe data din `releaseCal`.
4. **La confirmare**, `onDateSet` primește `year`, `month`, `day`.
5. **Actualizează** `releaseCal` și textul câmpului.

### De ce `month` e 0-indexat și aici

`DatePickerDialog` întoarce `month` de la 0 (ianuarie = 0), la fel ca `Calendar`. Deci `releaseCal.set(year, month, day)` funcționează direct, fără `-1`.

> **Atenție:** `DatePicker` (widget-ul) are `getMonth()` 0-indexat, dar `DatePickerDialog` îți dă direct valoarea corectă pentru `Calendar.set`. Nu confunda.

### De ce `catch (ParseException ignored) { }`

Dacă utilizatorul a tastat ceva invalid („abc”), `parse` aruncă. Ignorăm și continuăm cu data din `releaseCal` — calendarul se deschide pe data anterioară sau pe azi.

> **De reținut:** un `catch` gol e acceptabil **doar** când eroarea nu schimbă comportamentul dorit. Aici: „dacă textul e invalid, ignoră-l”.

### De ce `etRelease.setError(null)`

Curăță o eventuală eroare afișată anterior. În repo, `setError` nu e apelat niciodată cu o valoare non-null — deci linia e defensivă, fără efect practic.

### Exercițiu 7.7

**Cerință:** adaugă o validare: dacă data aleasă e în viitor, afișează `etRelease.setError("Release date cannot be in the future")` și nu actualiza câmpul.

<details>
<summary>Indiciu</summary>

Compară `releaseCal.getTime()` cu `new Date()` (acum). `Date.after(other)` întoarce `true` dacă e după.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat o condiție în `onDateSet`.

```java
@Override
public void onDateSet(DatePicker view, int year, int month, int day) {
    Calendar chosen = Calendar.getInstance();
    chosen.set(year, month, day);
    if (chosen.after(Calendar.getInstance())) {
        etRelease.setError("Release date cannot be in the future");
        return;
    }
    releaseCal.set(year, month, day);
    etRelease.setError(null);
    etRelease.setText(dateFormat.format(releaseCal.getTime()));
}
```

**De ce `chosen.after(Calendar.getInstance())`:** `Calendar` are `after(Calendar)`. Pentru `Date`, ai `date.after(new Date())`.

**De reținut:**
1. `setError` afișează un mesaj roșu sub câmp și o iconiță. E mecanismul standard de validare.
2. `return` timpuriu = nu actualizezi `releaseCal` și nu schimbi textul.
3. `setError(null)` curăță eroarea anterioară — aici devine **util**, nu doar defensiv.

**Unde revine:** în `saveMovie` (pasul 7.8), ai putea valida similar înainte de a construi `Movie`.

</details>

---

## Pasul 7.8 — `saveMovie`: construirea modelului

### De ce

La Save, trebuie să citești **toate** cele 10 câmpuri din UI și să construiești un `Movie`. Apoi să-l trimiți înapoi.

### Cum

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

### Sursa fiecărui câmp

| Câmp model | Sursă | Metodă |
|---|---|---|
| `title` | `etTitle` | `getText().toString()` |
| `release` | `releaseCal` | `getTime()` |
| `genre` | `spGenre` | `getSelectedItem().toString()` |
| `budget` | `etBudget` | `Double.parseDouble(getText().toString())` |
| `duration` | `sbDuration` | `getProgress()` |
| `rating` | `rbRating` | `getRating()` |
| `watched` | `swWatched` | `isChecked()` |
| `onWatchlist` | `cbonWatchList` | `isChecked()` |
| `poster` | `etPoster` | `getText().toString()` |
| `approval` | `rgApproval` | iterație peste copii |

### De ce `releaseCal` și nu `etRelease`

Pentru că `releaseCal` e sursa de adevăr. Textul poate fi gol sau invalid; calendarul are mereu o valoare validă. Vezi pasul 5.6.

### Capcana `Double.parseDouble` pe câmp gol

Dacă `etBudget` e gol, `Double.parseDouble("")` aruncă `NumberFormatException` → **aplicația crăpă**.

Aceasta e o problemă **reală** în `d719ffc`. Versiunea ta locală de sync o repară astfel:

```java
String budgetText = etBudget.getText().toString().trim();
if (!budgetText.isEmpty()) {
    try {
        movie.setBudget(Double.parseDouble(budgetText));
    } catch (NumberFormatException e) {
        movie.setBudget(0);
    }
} else {
    movie.setBudget(0);
}
```

> **Decizie:** în materialul de bază păstrăm versiunea din repo (fidelitate). Dar **știi** că e un bug. Dacă vrei să-l repari, folosește varianta de mai sus — e o îmbunătățire, nu o abatere.

### De ce `break` în bucla radio

După ce ai găsit butonul bifat, nu mai are rost să continui. `break` iese din buclă.

### De ce `if (position != -1)` la `putExtra`

Dacă e insert mode (`position == -1`), nu trimiți poziția. `MainActivity` va interpreta absența ei ca „adaugă la final”. Vezi cap. 08.

### Exercițiul 7.8 — capcana

**Cerință:** rulează aplicația, deschide formularul, **lasă bugetul gol**, apasă Save. Citește `Logcat`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am testat salvarea cu buget gol.

**Ce se întâmplă:** aplicația **crăpă**:

```
java.lang.NumberFormatException: For input string: ""
    at java.lang.Double.parseDouble(Double.java:...)
    at ro.ase.ie.g1097.activities.ItemActivity.saveMovie(ItemActivity.java:173)
```

**De ce:** `Double.parseDouble("")` nu poate converti un string gol într-un număr. Aruncă `NumberFormatException`, care nu e prinsă → propagată → aplicația se închide.

**De reținut:**
1. **Orice** `parseXxx` aruncă pe input invalid: `Integer.parseInt`, `Double.parseDouble`, `SimpleDateFormat.parse`.
2. `getText().toString()` întoarce `""` pentru câmp gol, **nu** `null`. Deci verificarea `!= null` nu ajută — trebuie `!isEmpty()`.
3. `try/catch` e obligatoriu când parsezi input de la utilizator.

**Unde revine:** în cap. 09, `fillForm` are problema inversă: `dateFormat.format(existing.getRelease())` aruncă NPE dacă `release` e `null`. Aceeași categorie de bug: **input nesigur folosit fără verificare**.

</details>

---

## Pasul 7.9 — Verificare

### Cum

1. Rulează aplicația.
2. Din `MainActivity`, apeși FAB-ul → **nu se întâmplă nimic** (încă nu ai navigare, cap. 08).
3. Ca să testezi `ItemActivity` izolat, adaugă temporar în `MainActivity.onCreate`:

```java
startActivity(new Intent(this, ItemActivity.class));
```

4. Completează formularul, apasă Save. Aplicația se închide (finish), dar nu vezi rezultatul — pentru că nu ai `launcher` încă.

### Ce verifici

- [ ] 13 `findViewById` fără NPE
- [ ] click pe Release deschide calendarul
- [ ] mișcarea barei actualizează `tvDurationValue`
- [ ] comutarea switch-ului actualizează `tvWatchedValue`
- [ ] Save nu crăpă (cu buget completat)
- [ ] Save **crăpă** cu buget gol → confirmi că ai înțeles bug-ul

---

## Pasul 7.10 — Exercițiu de reflecție

**Cerință:** de ce `ItemActivity` construiește un `Movie` **nou** la Save, în loc să modifice unul existent?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** la Save se face `Movie movie = new Movie();` — un obiect nou, indiferent dacă e insert sau edit.

**De ce:** modelul e **imuabil din perspectiva activității**. `ItemActivity` nu are referință la obiectul din `MainActivity` (a primit o **copie** prin serializare). Deci nu poate modifica originalul.

Soluția: construiește un obiect nou, îl trimite înapoi, iar `MainActivity` decide ce face cu el:
- insert → `movies.add(movie)`
- edit → `movies.set(position, movie)`

**De reținut:**
1. **Serializarea creează copii.** Nu poți modifica obiectul părinte prin referință.
2. Pattern-ul „trimite înapoi rezultatul” e standard în Android pentru editare.
3. Alternativa ar fi `startActivityForResult` cu un `Parcelable` mutabil sau un `ViewModel` partajat — dar aici e overkill.

**Unde revine:** cap. 08 (`onActivityResult`) și cap. 09 (`position`).

</details>

---

## Pasul 7.11 — Compară cu originalul

```bash
diff "cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java" \
     "_progres/Movies1097/app/src/main/java/ro/ase/ie/g1097/activities/ItemActivity.java"
```

La acest stadiu vei avea **diferențe intenționate**: `fillForm` și blocul din `onCreate` care citește `Intent`-ul lipsesc (vin în cap. 09). Restul trebuie să fie identic.

---

## Rezumat capitol 07

- `initControls` = 13 `findViewById`, după `setContentView`.
- `OnSeekBarChangeListener` are 3 metode → fără lambda.
- `OnCheckedChangeListener` are 1 metodă → lambda OK.
- `DatePickerDialog` cu `month` 0-indexat, `releaseCal` ca sursă de adevăr.
- `saveMovie` construiește un `Movie` nou din UI.
- `Double.parseDouble("")` = `NumberFormatException` — bug real în repo.

**Următorul capitol:** [08 - Navigarea si rezultatul.md](08%20-%20Navigarea%20si%20rezultatul.md)
