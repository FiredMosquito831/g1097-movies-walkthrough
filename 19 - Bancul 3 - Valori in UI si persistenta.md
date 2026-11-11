# Capitolul 19 — Bancul de cerințe 3: legarea valorilor de UI și păstrarea stării

**Obiectiv:** să traduci orice cerință de tipul „când se schimbă X, eticheta să arate Y" sau „după modificare, starea să rămână corectă" într-un mecanism concret din Android, pe aplicația G1097 de la commitul `d719ffc`. La test cerința nu spune niciodată „scrie un `TextWatcher`" — spune „când scriu în câmp, eticheta să se actualizeze". Traducerea e treaba ta.

**Cele patru direcții în care circulă o valoare:**
| Direcție | Mecanism |
|---|---|
| widget → etichetă | listener (`onProgressChanged`, `onCheckedChanged`, `afterTextChanged`, ...) |
| widget → model | `saveMovie()` |
| model → widget | `fillForm()` |
| listă → ecran | `notifyDataSetChanged()` / `notifyItemChanged()` |

Toate cele zece exerciții sunt variante ale acestor patru direcții. Trei dintre ele (19.7, 19.8, 19.10) repară defecte **reale** din codul de la `d719ffc`, nu inventează scenarii.

**Convenție:** textele din UI rămân în engleză, ca în aplicație (`"Save Movie"`, `"Yes"`, `"No"`). Proza și explicațiile sunt în română.

---

## Exercițiul 19.1 — `tvWatchedValue` urmărește switch-ul

**Cerință:** `tvWatchedValue` arată `"Yes"` / `"No"` după starea lui `swWatched`. Codul există deja la `d719ffc`. Explică **de ce** eticheta e deja corectă când deschizi un film existent în modul editare și ce se strică exact dacă muți `initListeners()` după blocul care apelează `fillForm(existing)`.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `initListeners()` (liniile 144–149) și `onCreate()` (liniile 73–83).

**Cum abordezi — pașii tăi:**
1. Deschide `ItemActivity.java` și găsește `initListeners()` (linia 131). Confirmă că blocul `swWatched.setOnCheckedChangeListener(...)` există și scrie în `tvWatchedValue`.
2. Deschide `onCreate()` (linia 63) și notează pe hârtie ordinea: `initControls()` → `initListeners()` → blocul `if (existing != null)` → `fillForm(existing)`.
3. Intră în `fillForm` (linia 86) și urmărește linia 92: `swWatched.setChecked(existing.isWatched())`. Întreabă-te ce face `setChecked` când valoarea primită e identică cu cea curentă — default-ul din XML e `false`.
4. Scrie răspunsul în două propoziții: listenerul se apelează la `setChecked` **dacă valoarea se schimbă**; pentru `false` nu se schimbă, dar eticheta din XML e deja `"No"`.
5. Verificare pe emulator: deschide „Inception" (`watched = true`) → eticheta `"Yes"`; deschide „The Matrix" (`watched = false`) → `"No"`. Apoi mută temporar `initListeners()` după blocul `if` și repetă: „Inception" arată `"No"`. Pune ordinea la loc.

**Indiciu 1 — dacă te blochezi la pasul 1:** `CompoundButton.setChecked()` nu e un setter mut. Citește sursa: apelează listenerul, dar numai dacă valoarea se schimbă (`if (mChecked != checked)`).

**Indiciu 2 — dacă te blochezi la pasul 3:** XML-ul are `android:text="No"` pe `tvWatchedValue` (linia 318). Cazul `false` nu declanșează listenerul, dar eticheta e deja corectă — de aceea funcționează „din noroc".

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** nimic nou — blocul există deja. Se explică ordinea și condiția.

**Cod:**

```java
// ItemActivity.initListeners(), liniile 144–149 — există la d719ffc
swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
    @Override
    public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
        tvWatchedValue.setText(isChecked ? "Yes" : "No");
    }
});
```

```java
// ItemActivity.onCreate(), liniile 73–83 — ordinea e tot secretul
initControls();
initListeners();          // 1. listenerul e înregistrat

Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);   // 2. abia acum setChecked() are pe cine să anunțe
    setTitle("Edit movie");
    btMovieAction.setText("Update Movie");
}
```

**De ce:** `CompoundButton.setChecked(boolean)` nu e un simplu `this.checked = checked`. Sursa din `CompoundButton`:

```java
public void setChecked(boolean checked) {
    if (mChecked != checked) {
        mChecked = checked;
        refreshDrawableState();
        // ...
        if (mOnCheckedChangeListener != null) {
            mOnCheckedChangeListener.onCheckedChanged(this, mChecked);
        }
    }
}
```

Două consecințe, ambele contează la test:

1. **Listenerul se apelează și la apel programatic**, nu doar la atingere. `fillForm` face `swWatched.setChecked(existing.isWatched())` (linia 92), iar listenerul e deja înregistrat → eticheta se actualizează singură.
2. **Numai dacă valoarea se schimbă.** `mChecked != checked` e garda. Tabelul complet:

| `existing.isWatched()` | Default din XML | `setChecked()` | Listenerul | Eticheta |
|---|---|---|---|---|
| `true` | `false` | se schimbă | se apelează | `"Yes"` ✔ |
| `false` | `false` | nu se schimbă | **nu** se apelează | `"No"` din XML ✔ |

Cazul `false` merge **din noroc**: XML-ul are `android:text="No"` pe `tvWatchedValue` (linia 318), deci valoarea de start e deja corectă. Dacă cineva ar schimba XML-ul în `"Yes"`, filmul cu `watched = false` ar afișa `"Yes"` și nimeni nu ar vedea de ce.

**De reținut:** dacă muți `initListeners()` după blocul `if (existing != null)`, `setChecked(true)` rulează fără listener → eticheta rămâne `"No"` pentru un film văzut. Nu crapă, nu dă eroare, doar minte. Reparația robustă nu e ordinea, ci o singură metodă care scrie eticheta, apelată din ambele locuri:

```java
private void updateWatchedLabel(boolean isChecked) {
    tvWatchedValue.setText(isChecked ? "Yes" : "No");
}

// în listener:
updateWatchedLabel(isChecked);

// la finalul lui fillForm, după swWatched.setChecked(...):
updateWatchedLabel(existing.isWatched());
```

Așa ești independent de ordine și de garda `mChecked != checked`.

**Unde se aplică:** orice `CompoundButton` — `CheckBox`, `MaterialSwitch`, `RadioButton`. `RadioGroup.check(id)` are exact aceeași gardă (`if (id == mCheckedId) return;`), deci `rgApproval.check(...)` din `fillForm` (linia 108) anunță listenerul doar dacă schimbă selecția. La rotire, framework-ul restaurează starea switch-ului și apelează tot `setChecked()` → eticheta se autorepară.

</details>

---

## Exercițiul 19.2 — Contor de caractere sub `etTitle`

**Cerință:** sub câmpul de titlu apare un text viu de forma `"12 / 50"`, care se actualizează la fiecare tastă. Tastarea peste 50 de caractere este **blocată**, nu doar semnalată.

**Fișiere atinse:** `cod-final/res/layout/activity_item.xml` (un `TextView` nou + o margine modificată) și `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` (`initControls`, `initListeners`).

**Cum abordezi — pașii tăi:**
1. Deschide `activity_item.xml` și găsește `TextInputLayout`-ul lui `etTitle` (liniile 70–84). Schimbă `android:layout_marginBottom="16dp"` (linia 74) în `4dp`.
2. Adaugă `TextView`-ul `tvTitleCounter` imediat după `</com.google.android.material.textfield.TextInputLayout>` (linia 84), înainte de comentariul `<!-- Genre -->`.
3. În `ItemActivity.java`, adaugă cele trei importuri (`Editable`, `InputFilter`, `TextWatcher`), câmpul `TITLE_MAX_LENGTH`, câmpul `tvTitleCounter` și `findViewById` în `initControls()`.
4. În `initListeners()`, adaugă cele două bucăți: `etTitle.setFilters(...)` (blocarea) și `etTitle.addTextChangedListener(...)` (contorul).
5. Verificare pe emulator: tastează în titlu — contorul crește la fiecare tastă; la 50 de caractere tastarea nu mai adaugă nimic; butonul X din câmp golește textul și contorul revine la `"0 / 50"`.

**Indiciu 1 — dacă te blochezi la pasul 1:** sunt două mecanisme diferite. Contorul e un `TextWatcher`; blocarea e un `InputFilter.LengthFilter`. Unul nu face treaba celuilalt.

**Indiciu 2 — dacă te blochezi la pasul 4:** `TextWatcher` are trei metode; cea care te interesează e `afterTextChanged(Editable s)`, iar lungimea se ia cu `s.length()`. `LengthFilter` se pune în array: `new InputFilter[]{ new InputFilter.LengthFilter(50) }`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un `TextView` sub `TextInputLayout`-ul titlului, am înregistrat un `InputFilter.LengthFilter(50)` și un `TextWatcher` care scrie `lungime + " / 50"`.

**Cod:**

În `activity_item.xml`, `TextInputLayout`-ul lui `etTitle` are `android:layout_marginBottom="16dp"` (linia 74). Schimbă-l în `4dp`, apoi adaugă imediat după `</com.google.android.material.textfield.TextInputLayout>` (linia 84), înainte de comentariul `<!-- Genre -->`:

```xml
<TextView
    android:id="@+id/tvTitleCounter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="end"
    android:layout_marginBottom="16dp"
    android:text="0 / 50"
    android:textAppearance="?attr/textAppearanceLabelSmall"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

În `ItemActivity.java`:

```java
// importuri noi
import android.text.Editable;
import android.text.InputFilter;
import android.text.TextWatcher;

// câmpuri noi, lângă celelalte
private static final int TITLE_MAX_LENGTH = 50;
private TextView tvTitleCounter;

// initControls(), la final
tvTitleCounter = findViewById(R.id.tvTitleCounter);

// initListeners(), la final
etTitle.setFilters(new InputFilter[]{ new InputFilter.LengthFilter(TITLE_MAX_LENGTH) });
etTitle.addTextChangedListener(new TextWatcher() {
    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

    @Override
    public void onTextChanged(CharSequence s, int start, int before, int count) { }

    @Override
    public void afterTextChanged(Editable s) {
        tvTitleCounter.setText(s.length() + " / " + TITLE_MAX_LENGTH);
    }
});
```

**De ce:**

- `setFilters` **înlocuiește** tot array-ul de filtre, nu adaugă. Dacă mai ai un filtru (de exemplu unul care elimină spațiile duble), pune-l în același array: `new InputFilter[]{ new InputFilter.LengthFilter(50), altFiltru }`.
- `LengthFilter` acționează la **orice** modificare a textului, inclusiv la `setText` programatic. Deci dacă `fillForm` primește un titlu de 60 de caractere, în câmp vor ajunge doar primele 50 — și modelul și UI-ul diverg fără niciun mesaj. E un comportament de care trebuie să fii conștient, nu un bug.
- `afterTextChanged` e callback-ul corect: primește `Editable`-ul final. `onTextChanged` se apelează în timpul modificării, iar dacă scrii în text de acolo intri în re-entranță.
- Contorul e corect și după `fillForm`, pentru că watcher-ul e înregistrat în `initListeners()`, care rulează înaintea blocului `if (existing != null)`.
- `TextInputEditText` extinde `AppCompatEditText` → `EditText` → `TextView`, deci are și `setFilters`, și `addTextChangedListener`.
- Butonul de clear (`app:endIconMode="clear_text"`, linia 76) golește textul → watcher-ul se apelează → `"0 / 50"`.

**De reținut:** Material are contor gata făcut, pe `TextInputLayout`: `app:counterEnabled="true"` și `app:counterMaxLength="50"`. Afișează exact `"12 / 50"` și se face roșu peste limită — dar **nu blochează tastarea**. Dacă cerința spune doar „contor", oricare variantă e acceptată; dacă spune „să nu poți scrie mai mult", ai nevoie de `LengthFilter`. La test scrie ambele, într-o propoziție: „contorul e `LengthFilter` + `TextWatcher`; Material are unul vizual, dar nu blochează".

**Unde se aplică:** `etPoster` (limită de URL), orice câmp cu lungime maximă. Același `TextWatcher` stă la baza exercițiilor 19.3 și 19.10.

</details>

---

## Exercițiul 19.3 — `tvBudgetValue` cu separatori de mii, în timp ce tastezi

**Cerință:** cât timp utilizatorul tastează în `etBudget`, o etichetă `tvBudgetValue` arată bugetul formatat cu separatori de mii: `160000000` în câmp → `$160,000,000` în etichetă.

**Fișiere atinse:** `cod-final/res/layout/activity_item.xml` (un `TextView` nou după `TextInputLayout`-ul bugetului, linia 179) și `ItemActivity.java` (`initControls`, `initListeners`, un câmp `NumberFormat`).

**Cum abordezi — pașii tăi:**
1. Deschide `activity_item.xml` și găsește `TextInputLayout`-ul bugetului (liniile 165–179). Schimbă `android:layout_marginBottom="16dp"` (linia 169) în `4dp`.
2. Adaugă `TextView`-ul `tvBudgetValue` după `</com.google.android.material.textfield.TextInputLayout>` (linia 179), înainte de comentariul `<!-- Duration -->`.
3. În `ItemActivity.java`, adaugă `import java.text.NumberFormat;`, câmpul `tvBudgetValue`, câmpul `budgetFormat` și `findViewById` în `initControls()`.
4. În `initListeners()`, adaugă watcher-ul: citește textul, verifică `isEmpty()`, apoi `try { Double.parseDouble(raw) } catch (NumberFormatException e)`.
5. Verificare pe emulator: tastează `160000000` → eticheta arată `$160,000,000`; șterge tot → `$0`; lipește `12a` → eticheta arată `—`.

**Indiciu 1 — dacă te blochezi la pasul 3:** `NumberFormat.getNumberInstance(Locale.US)` grupează cu `,` și separă zecimalele cu `.` — exact ce acceptă `Double.parseDouble`.

**Indiciu 2 — dacă te blochezi la pasul 4:** `Double.parseDouble("")` aruncă excepție, deci verifică `raw.isEmpty()` **înainte** de `try`. Formatarea propriu-zisă e `budgetFormat.format(value)`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** un `TextWatcher` pe `etBudget` care citește textul, îl parsează și scrie în etichetă valoarea formatată. Câmpul rămâne neformatat.

**Cod:**

În `activity_item.xml`, `TextInputLayout`-ul bugetului are `android:layout_marginBottom="16dp"` (linia 169). Schimbă-l în `4dp` și adaugă după `</com.google.android.material.textfield.TextInputLayout>` (linia 179), înainte de `<!-- Duration -->`:

```xml
<TextView
    android:id="@+id/tvBudgetValue"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="end"
    android:layout_marginBottom="16dp"
    android:text="$0"
    android:textAppearance="?attr/textAppearanceLabelSmall"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

În `ItemActivity.java`:

```java
// import nou
import java.text.NumberFormat;

// câmp nou
private TextView tvBudgetValue;
private final NumberFormat budgetFormat = NumberFormat.getNumberInstance(Locale.US);

// initControls(), la final
tvBudgetValue = findViewById(R.id.tvBudgetValue);

// initListeners(), la final
etBudget.addTextChangedListener(new TextWatcher() {
    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

    @Override
    public void onTextChanged(CharSequence s, int start, int before, int count) { }

    @Override
    public void afterTextChanged(Editable s) {
        String raw = s.toString().trim();
        if (raw.isEmpty()) {
            tvBudgetValue.setText("$0");
            return;
        }
        try {
            double value = Double.parseDouble(raw);
            tvBudgetValue.setText("$" + budgetFormat.format(value));
        } catch (NumberFormatException e) {
            tvBudgetValue.setText("—");
        }
    }
});
```

**De ce:**

- **Eticheta formatează, câmpul rămâne brut.** Dacă ai formata și câmpul, ai avea nevoie de o gardă de re-entranță (scrii în text → watcher-ul se apelează din nou → scrii din nou) și de repoziționarea cursorului. Aici nu e nevoie de niciuna: câmpul nu se atinge.
- `NumberFormat.getNumberInstance(Locale.US)` grupează cu `,` și separă zecimalele cu `.` — exact ce acceptă `Double.parseDouble`. Cu `Locale.getDefault()` pe un telefon românesc ai obține `160.000.000`, iar dacă ai copia valoarea în câmp, `parseDouble` ar arunca. Locale fix = comportament previzibil.
- `Double.parseDouble("")` aruncă `NumberFormatException` — de aceea `isEmpty()` e verificat **înainte** de `try`. Aceasta e exact linia 173 din `saveMovie`, unde lipsa verificării produce crash (vezi 19.10).
- Tastezi `1` → `$1`; `16` → `$16`; `160` → `$160`; `1600` → `$1,600`; `160000000` → `$160,000,000`. Fiecare tastă returnează o etichetă nouă, fără nicio stare păstrată între apeluri.
- `NumberFormat.format(double)` păstrează implicit până la 3 zecimale. Pentru bani, adaugă `budgetFormat.setMaximumFractionDigits(2);` o singură dată, în `initControls`.
- Eticheta e corectă și după `fillForm`, pentru că `setText` din `fillForm` declanșează watcher-ul.

**De reținut:** forma curată a direcției „widget → etichetă" e o **funcție pură**: citește widget-ul, calculează, scrie eticheta. Nu ține valoarea parsată într-un câmp al activității și nu spera că rămâne sincronă — la prima editare a textului ai două surse de adevăr.

**Unde se aplică:** orice etichetă de tip „preview" — durată (19.4), rating, preț. În 19.10 același watcher primește și validarea.

</details>

---

## Exercițiul 19.4 — `tvDurationValue` arată „1 h 22 min"

**Cerință:** `tvDurationValue` afișează `"1 h 22 min"` când progresul `SeekBar`-ului e cel puțin 60, și `"22 min"` când e sub 60. La 148 → `"2 h 28 min"`, la 60 → `"1 h"`.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `onProgressChanged` (liniile 150–165) plus o metodă nouă.

**Cum abordezi — pașii tăi:**
1. Deschide `ItemActivity.java` și citește `onProgressChanged` (liniile 151–154). Observă ce afișează acum: `progress + " min."`.
2. Scrie metoda `formatDuration(int totalMinutes)` lângă `saveMovie()`, cu două ramuri: sub 60 și peste 60 (împărțire întreagă + modulo).
3. Înlocuiește corpul lui `onProgressChanged` cu un singur apel: `tvDurationValue.setText(formatDuration(progress));`.
4. Verificare pe emulator: trage slider-ul la 82 → `"1 h 22 min"`; la 60 → `"1 h"`; la 59 → `"59 min"`. Apoi deschide „Inception" (148) → `"2 h 28 min"` imediat, fără să atingi slider-ul.

**Indiciu 1 — dacă te blochezi la pasul 2:** orele sunt `totalMinutes / 60`, minutele rămase sunt `totalMinutes % 60`. Cazul `minutes == 0` trebuie tratat separat, altfel obții `"1 h 0 min"`.

**Indiciu 2 — dacă te blochezi la pasul 4:** `onProgressChanged` se apelează și când `fillForm` face `sbDuration.setProgress(...)`, cu `fromUser == false`. De aceea eticheta e corectă la deschiderea unui film — nu muta actualizarea în `onStopTrackingTouch`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am scos formatarea din listener într-o metodă separată și am înlocuit `progress + " min."` cu apelul ei.

**Cod:**

```java
// ItemActivity — metodă nouă, lângă saveMovie()
private String formatDuration(int totalMinutes) {
    if (totalMinutes < 60) {
        return totalMinutes + " min";
    }
    int hours = totalMinutes / 60;
    int minutes = totalMinutes % 60;
    return minutes == 0 ? hours + " h" : hours + " h " + minutes + " min";
}
```

```java
// onProgressChanged, înlocuiește linia 153
@Override
public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
    tvDurationValue.setText(formatDuration(progress));
}
```

**De ce:**

- Folosește parametrul `progress`, nu `seekBar.getProgress()`. Sunt aceeași valoare, dar parametrul e contractul callback-ului.
- `fromUser` e `false` când `fillForm` face `sbDuration.setProgress(existing.getDuration())` (linia 90). Listenerul se apelează oricum → eticheta e corectă imediat după `fillForm`, fără cod suplimentar. Dacă ai pune actualizarea doar în `onStopTrackingTouch`, ecranul de editare ar arăta `"0 min"` pentru un film de 148 de minute, fiindcă nimeni nu a tras de slider.
- `ProgressBar.setProgressInternal` are garda `if (progress == mProgress) return false;` — deci pentru un film cu durata 0 listenerul nu se apelează deloc. Eticheta din XML e deja `"0 min"` (linia 201), deci iarăși merge din noroc. Dacă schimbi textul din XML, pune `updateDurationLabel(0)` la finalul lui `initControls`.
- `android:max="300"` (linia 212) → valoarea maximă afișată e `"5 h"`. Limitele de sub slider sunt hardcodate `"0 min"` / `"300 min"` (liniile 228, 235) — dacă schimbi `max`, trebuie schimbate și ele.
- 82 → `"1 h 22 min"`, 148 → `"2 h 28 min"`, 60 → `"1 h"`, 59 → `"59 min"`.

**De reținut:** varianta de la `d719ffc`, `progress + " min."`, are un punct final care nu apare nicăieri în cerință și nu are formă de ore. La test, dacă cerința dă un exemplu exact (`"1 h 22 min"`), formatul e parte din notă — nu-l „îmbunătăți".

**Unde se aplică:** orice `SeekBar`/`ProgressBar` cu etichetă derivată. La `RatingBar` există exact același tipar: `onRatingChanged(RatingBar ratingBar, float rating, boolean fromUser)` — și acolo `fromUser` e `false` la `setRating` din `fillForm`.

</details>

---

## Exercițiul 19.5 — Toast cu numărul de filme după Save

**Cerință:** după ce utilizatorul salvează (indiferent dacă a adăugat sau a editat), `MainActivity` afișează un `Toast` cu câte filme există în listă. Numărul trebuie să fie corect în ambele cazuri.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` — `onActivityResult` (liniile 62–79).

**Cum abordezi — pașii tăi:**
1. Deschide `MainActivity.java` și citește `onActivityResult` (liniile 62–79). Identifică cele două ramuri: `position == -1` (inserare) și `else` (editare).
2. Confirmă că ambele ramuri se termină cu `movieAdapter.notifyDataSetChanged()` — Toast-ul vine după ele, nu înăuntru.
3. Adaugă `Toast.makeText(MainActivity.this, movies.size() + " movies in the list", Toast.LENGTH_SHORT).show();` la finalul blocului `if (o.getResultCode() == RESULT_OK)`, după `if/else`.
4. Verificare pe emulator: pornești cu 3 filme demo; apeși `+`, completezi, Save → `"4 movies in the list"`; apoi atingi „Inception", schimbi titlul, Update → `"3 movies in the list"`.

**Indiciu 1 — dacă te blochezi la pasul 3:** în interiorul clasei anonime `ActivityResultCallback`, `this` e callback-ul, nu activitatea. Scrie `MainActivity.this`, altfel nu compilează (nu există `Context`).

**Indiciu 2 — dacă te blochezi la pasul 4:** numărul trebuie citit **după** mutație. Dacă pui Toast-ul înainte de `movies.add(movie)`, afișezi 3 în loc de 4. `Toast` e deja importat la linia 9.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un `Toast` la finalul callback-ului, după ce lista a fost modificată și adapterul notificat.

**Cod:**

```java
// MainActivity.onCreate(), în interiorul lui ActivityResultCallback
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
        Toast.makeText(MainActivity.this,
                movies.size() + " movies in the list",
                Toast.LENGTH_SHORT).show();
    }
}
```

**De ce:**

- **După ambele ramuri.** Inserarea schimbă dimensiunea (3 → 4), editarea nu (rămâne 3). Ambele sunt corecte — condiția e ca `movies.size()` să fie citit **după** mutație.
- Dacă pui `Toast`-ul înainte de `movies.add(movie)`, afișezi 3 în loc de 4. E classicul off-by-one care se vede imediat pe emulator.
- `MainActivity.this`, nu `this`: în interiorul clasei anonime `ActivityResultCallback`, `this` e callback-ul, nu activitatea. `Toast.makeText(this, ...)` nu compilează — nu există `Context`.
- `Toast` e deja importat la linia 9 și e nefolosit la `d719ffc` — semn că exercițiul era prevăzut.
- `o.getData()` poate fi `null` teoretic. Aici e sigur, pentru că `ItemActivity.saveMovie()` cheamă întotdeauna `setResult(RESULT_OK, intent)` cu un `Intent` non-null. Un `if (intent == null) return;` costă o linie și nu strică nimic.

**De reținut:** numărul e o proprietate a **modelului** (`movies`), nu a adapterului. `movieAdapter.getCount()` ar da același rezultat și ar fi chiar mai aproape de ce se vede pe ecran — dar numai pentru că adapterul înfășoară exact aceeași listă. În `MainActivity`, sursa de adevăr e `movies`.

**Unde se aplică:** orice etichetă de tip „N elemente". Dacă vrei un `TextView` permanent în loc de `Toast`, actualizează-l în același loc în care notifici adapterul — niciodată într-un singur ramură.

</details>

---

## Exercițiul 19.6 — Rotirea nu pierde formularul

**Cerință:** întoarce telefonul în `ItemActivity` și formularul păstrează titlul, bugetul, durata și ratingul. Implementează `onSaveInstanceState` și explică ce se pierde de fapt fără el.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — două metode noi și cinci constante.

**Cum abordezi — pașii tăi:**
1. Deschide `ItemActivity.java` și fă lista câmpurilor care **nu** sunt `View`: `position` (linia 57), `releaseCal` (linia 58), `dateFormat` (linia 59).
2. Întreabă-te, pentru fiecare, ce se întâmplă la rotire: `position` e recitit din `Intent`; `releaseCal` e reinițializat cu `Calendar.getInstance()`; `dateFormat` e doar un formatter, nu ține stare.
3. Adaugă cele cinci constante `KEY_*` lângă `position`.
4. Scrie `onSaveInstanceState` (cele patru valori + `releaseCal.getTimeInMillis()`) și `onRestoreInstanceState` (simetric, cu `setTimeInMillis`).
5. Verificare pe emulator: deschide „Inception", schimbă titlul, bugetul, durata și ratingul, rotește telefonul → valorile rămân. Apoi alege o dată din picker, rotește, apasă Update, redeschide filmul → data e cea aleasă, nu cea de azi.

**Indiciu 1 — dacă te blochezi la pasul 1:** cele patru câmpuri din cerință (`etTitle`, `etBudget`, `sbDuration`, `rbRating`) se salvează deja singure — `EditText.getFreezesText()` returnează `true`, iar `ProgressBar` își salvează progresul. Câmpul care **nu** se salvează e `releaseCal`.

**Indiciu 2 — dacă te blochezi la pasul 4:** `onRestoreInstanceState` rulează după `onStart`, deci după `fillForm(existing)` din `onCreate` — restaurarea ta câștigă în fața modelului. Dacă ai restaura la începutul lui `onCreate`, `fillForm` ți-ar suprascrie valorile.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat `onSaveInstanceState` / `onRestoreInstanceState` cu cele patru valori din cerință plus `releaseCal` — ultimul fiind singurul care conta cu adevărat.

**Cod:**

```java
// câmpuri noi, lângă position
private static final String KEY_TITLE = "key_title";
private static final String KEY_BUDGET = "key_budget";
private static final String KEY_DURATION = "key_duration";
private static final String KEY_RATING = "key_rating";
private static final String KEY_RELEASE = "key_release";
```

```java
// ItemActivity — după onCreate()
@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putString(KEY_TITLE, etTitle.getText().toString());
    outState.putString(KEY_BUDGET, etBudget.getText().toString());
    outState.putInt(KEY_DURATION, sbDuration.getProgress());
    outState.putFloat(KEY_RATING, rbRating.getRating());
    outState.putLong(KEY_RELEASE, releaseCal.getTimeInMillis());
}

@Override
protected void onRestoreInstanceState(@NonNull Bundle savedInstanceState) {
    super.onRestoreInstanceState(savedInstanceState);
    etTitle.setText(savedInstanceState.getString(KEY_TITLE, ""));
    etBudget.setText(savedInstanceState.getString(KEY_BUDGET, ""));
    sbDuration.setProgress(savedInstanceState.getInt(KEY_DURATION, 0));
    rbRating.setRating(savedInstanceState.getFloat(KEY_RATING, 0f));
    releaseCal.setTimeInMillis(
            savedInstanceState.getLong(KEY_RELEASE, System.currentTimeMillis()));
}
```

**De ce:**

- `onSaveInstanceState` se apelează înainte ca activitatea să fie distrusă de rotire, de „Don't keep activities" sau de moartea procesului cu stare. **Nu** se apelează la Back — acolo utilizatorul chiar a renunțat.
- `onRestoreInstanceState` se apelează **după** `onStart`, deci după `onCreate`. Asta e esențial: în `onCreate` a rulat deja `fillForm(existing)`, care a pus valorile din model. Restaurarea ta vine după și câștigă. Dacă ai restaura la începutul lui `onCreate`, `fillForm` ți-ar suprascrie valorile.
- **Cele patru câmpuri din cerință se salvează deja singure.** `EditText.getFreezesText()` returnează `true`, iar `ProgressBar` (din care derivă `SeekBar` și `RatingBar`) își salvează progresul în `ProgressBar.SavedState`. Toate au `android:id`, iar `android:saveEnabled` e `true` implicit. Deci rotirea le păstrează și fără codul de mai sus — scrierea lor explicită e corectă, dar redundantă. La test spune-o: arată că știi ce face framework-ul.
- **Ce se pierde cu adevărat e `releaseCal`.** E un câmp al activității, inițializat cu `Calendar.getInstance()` la fiecare recreare. Textul din `etRelease` supraviețuiește (e `EditText`), dar `saveMovie()` citește `releaseCal.getTime()` (linia 171), nu textul câmpului. Deci după rotire apeși Update și salvezi **data de azi**, în timp ce pe ecran se vede data veche. Linia care contează din tot exercițiul e `outState.putLong(KEY_RELEASE, ...)`.
- `position` supraviețuiește fără nimic: e recitit din `Intent`, iar sistemul re-livrează același `Intent` la recreare.
- `Bundle` are o limită practică de ~1 MB (`TransactionTooLargeException`). Nu pune bitmap-uri, liste mari sau imagini acolo. Un `Movie` e mic și `Serializable`, dar nu ai nevoie de el: formularul nu e încă un `Movie` valid (bugetul poate fi gol).

**De reținut:** `android:configChanges="orientation|screenSize"` **nu** e soluția. Ascunde problema la rotire, dar nu la moartea procesului, și în plus sari peste reîncărcarea resurselor (layout-ul de landscape nu s-ar mai aplica).

**Unde se aplică:** orice câmp de activitate care nu e `View` și nu vine din `Intent` — `releaseCal`, un filtru de căutare, un index de pagină, un obiect editat.

</details>

---

## Exercițiul 19.7 — `1.6E8` în loc de `160000000`

**Cerință:** deschide „Inception" în modul editare. `etBudget` arată `1.6E8`. E un defect real la `d719ffc`. Repară `fillForm` și explică de ce nu crapă nimic, deși afișajul e greșit.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `fillForm`, linia 89.

**Cum abordezi — pașii tăi:**
1. Deschide `ItemActivity.java` la linia 89 și citește `etBudget.setText(String.valueOf(existing.getBudget()));`.
2. Rulează aplicația și deschide pe rând cele trei filme demo: „Inception" arată `1.6E8`, „Toy Story" arată `3.0E7`, „The Matrix" arată `6.3E7`.
3. Înlocuiește linia cu un format explicit: `String.format(Locale.US, "%.0f", existing.getBudget())` sau `BigDecimal.valueOf(...).toPlainString()`.
4. Verificare pe emulator: redeschide toate trei → `160000000`, `30000000`, `63000000`. Apasă Update pe „Inception" fără să atingi bugetul și redeschide-l → valoarea a rămas `160000000`.

**Indiciu 1 — dacă te blochezi la pasul 2:** `String.valueOf(double)` apelează `Double.toString(double)`, care trece la notație științifică de la 10^7 în sus. Toate cele trei valori demo sunt peste prag.

**Indiciu 2 — dacă te blochezi la pasul 3:** `%.0f` = fără zecimale, fără exponent, fără separatori. `Locale.US` e obligatoriu, altfel `Locale.getDefault()` ar pune `,` ca separator zecimal și `Double.parseDouble` ar refuza textul la Save.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit `String.valueOf(...)` cu un format explicit, fără exponent.

**Cod:**

```java
// înainte (d719ffc, linia 89)
etBudget.setText(String.valueOf(existing.getBudget()));

// după — varianta 1
etBudget.setText(String.format(Locale.US, "%.0f", existing.getBudget()));

// după — varianta 2 (fără dependență de locale)
etBudget.setText(BigDecimal.valueOf(existing.getBudget()).toPlainString());
```

Varianta 2 cere `import java.math.BigDecimal;`. `Locale` e deja importat (linia 36).

**De ce:**

- Specificația `Double.toString` e explicită: forma zecimală se folosește doar pentru `10^-3 ≤ |x| < 10^7`. `160000000.0` e peste → `"1.6E8"`. Datele demo lovesc toate trei bug-ul: `160000000` → `"1.6E8"`, `30000000` → `"3.0E7"`, `63000000` → `"6.3E7"`.
- **De ce nu crapă:** `Double.parseDouble("1.6E8")` returnează `160000000.0`. Deci `saveMovie()` (linia 173) citește înapoi exact valoarea corectă și o salvează corect. Defectul e silențios: datele sunt bune, UI-ul minte.
- **De ce nu poate utilizatorul să repare din tastatură:** `android:inputType="numberDecimal"` (linia 178) dă o tastatură fără `E`. Iar `setText` **nu** trece prin key listener — trece doar prin filtrele din `setFilters`. Exact de aceea `E`-ul ajunge în câmp: `fillForm` îl scrie programatic, ocolind restricția de tastare.
- `String.format(Locale.US, "%.0f", x)`: fără zecimale, fără exponent, fără separatori de mii. `Locale.US` e obligatoriu: fără el se folosește `Locale.getDefault()`, iar pe un telefon românesc `%.2f` ar produce `"160000000,00"` — pe care `Double.parseDouble` îl refuză.
- `BigDecimal.valueOf(double)` trece și el prin `Double.toString`, dar `toPlainString()` nu folosește niciodată exponentul. Rezultat identic, fără locale. Pentru bani e varianta mai corectă, fiindcă afișează exact valoarea zecimală a lui `double`, fără rotunjire de format.
- `app:prefixText="$ "` (linia 171) pune deja `$` în fața câmpului — nu adăuga încă unul.

**De reținut:** nu construi niciodată textul unui număr cu `String.valueOf` sau `"" + număr` când numărul poate fi mare sau e `float`. Același capcană la rating: `String.valueOf(0.1f + 0.2f)` dă `"0.30000001"`. Și dacă vrei separatori de mii, nu-i pune în câmp — `Double.parseDouble("160,000,000")` aruncă. Separatorii stau în etichetă (19.3), nu în input.

**Unde se aplică:** orice `setText` dintr-un câmp numeric al modelului — buget, rating, durată. Și `Movie.toString()` are exact aceeași problemă: rândul din listă afișează `budget=1.6E8` (vezi 19.9).

</details>

---

## Exercițiul 19.8 — `fillForm` crapă când `release` e `null`

**Cerință:** `fillForm` aruncă `NullPointerException` pentru un `Movie` fără dată de lansare. Pune o gardă și explică de unde vine `null`-ul și de ce stack trace-ul arată altă linie decât a ta. Apoi verifică al doilea defect din aceeași metodă: editarea unui film îi schimbă data de lansare fără să atingi câmpul.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `fillForm`, linia 88.

**Cum abordezi — pașii tăi:**
1. Deschide `ItemActivity.java` la linia 88 și citește `etRelease.setText(dateFormat.format(existing.getRelease()));`.
2. Reproduce mental cazul: `Movie` are constructor fără argumente (linia 127), deci `new Movie()` lasă `release` pe `null`. Un astfel de obiect ajuns în `fillForm` ajunge la `dateFormat.format(null)`.
3. Înlocuiește linia cu un `if (existing.getRelease() != null) { ... } else { etRelease.setText(""); }`, iar în ramura `if` adaugă și `releaseCal.setTime(existing.getRelease());`.
4. Verifică al doilea defect: rulează aplicația, deschide „Inception", apasă Update **fără** să atingi câmpul de dată, redeschide filmul → data a devenit azi.
5. Verificare după reparație: aceeași secvență → data rămâne `16/07/2010`.

**Indiciu 1 — dacă te blochezi la pasul 2:** `dateFormat` nu e `null` — NPE-ul vine din interiorul lui `SimpleDateFormat.format`, care face `calendar.setTime(null)`. Citește stack trace-ul până la frame-ul `ItemActivity.fillForm`.

**Indiciu 2 — dacă te blochezi la pasul 4:** `releaseCal` e actualizat doar în `showReleaseDatePicker` (liniile 199–204). Dacă nu deschizi picker-ul, rămâne pe „acum", iar `saveMovie()` scrie `releaseCal.getTime()` — nu textul din câmp.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat garda de `null` **și** am sincronizat `releaseCal` cu data din model.

**Cod:**

```java
// înainte (d719ffc, linia 88)
etRelease.setText(dateFormat.format(existing.getRelease()));

// după
if (existing.getRelease() != null) {
    releaseCal.setTime(existing.getRelease());
    etRelease.setText(dateFormat.format(existing.getRelease()));
} else {
    etRelease.setText("");
}
```

**De ce:**

- **NPE-ul nu e al tău, e al framework-ului.** `dateFormat` nu e `null`. `SimpleDateFormat.format(Date)` delegă la `format(date, new StringBuffer(), new FieldPosition(0))`, care face `calendar.setTime(date)`, iar `Calendar.setTime(null)` aruncă `NullPointerException`. De aceea stack trace-ul arată `java.text.SimpleDateFormat.format` și nu linia 88 — trebuie să cobori în trace până la frame-ul `ItemActivity.fillForm` ca să înțelegi ce s-a întâmplat. La test, asta e răspunsul care contează: nu „am pus un `if`", ci „NPE-ul vine din interiorul formatter-ului".
- **De unde vine `null`-ul:** `Movie` are constructor fără argumente (linia 127) și implementează `Serializable`. Orice cod care face `new Movie()` și uită să apeleze `setRelease(...)` lasă câmpul `null`. Fluxul aplicației nu produce așa ceva — `saveMovie()` setează mereu data (linia 171) — dar `fillForm` e un punct de intrare care nu are voie să presupună.
- `etRelease.setText("")` în ramura `else`: utilizatorul vede un câmp gol și poate alege o dată. `setText(null)` ar merge și el (`TextView` tratează `null` ca text gol), dar `""` e explicit.
- **Al doilea defect, mai grav:** `fillForm` nu a sincronizat niciodată `releaseCal`. Câmpul e inițializat cu „acum" și e actualizat doar în `showReleaseDatePicker` (liniile 199–204). Deci la `d719ffc`, dacă deschizi un film și apeși Update **fără** să atingi câmpul de dată, `saveMovie()` scrie `releaseCal.getTime()` = data de azi. Data de lansare se schimbă silențios, fără nicio eroare. E cel mai periculos dintre cele trei defecte ale capitolului, fiindcă e pierdere de date, nu crash. Linia `releaseCal.setTime(existing.getRelease());` din ramura `if` îl repară.
- Ramura `else` lasă `releaseCal` pe „acum" — exact ce ar propune și `DatePickerDialog` implicit. E acceptabil.

**De reținut:** orice `format(...)` pe o valoare care poate fi `null` are nevoie de gardă — `SimpleDateFormat` și `NumberFormat` aruncă amândouă NPE. Atenție la contrastul periculos: `String.valueOf(null)` **nu** aruncă, returnează `"null"`. Adică un tip de cod ascunde `null`-ul, altul crapă. Trebuie să știi care face ce.

**Unde se aplică:** `dateFormat.format` din `showReleaseDatePicker` (deja protejat de `parsed != null`, linia 201), orice formatter din `fillForm`, orice `NumberFormat.format` pe un `Double` despre care nu ești sigur că e setat. `Movie.toString()` e sigur — concatenarea de string-uri transformă `null` în `"null"`.

</details>

---

## Exercițiul 19.9 — Lista nu are voie să arate date vechi după editare

**Cerință:** după ce editezi un film, rândul din listă arată valorile noi. Explică diferența dintre `notifyDataSetChanged()` și `notifyItemChanged(int)` și spune exact când e corect fiecare.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` — `onActivityResult` (liniile 68–77). Dacă ai construit `MovieAdapter` în capitolul 11, și `adapters/MovieAdapter.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `MainActivity.java` și citește `onActivityResult` (liniile 62–79). Notează că ambele ramuri cheamă deja `notifyDataSetChanged()` — deci întrebarea e „de ce e nevoie de el", nu „ce lipsește".
2. Verifică ce înfășoară adapterul: linia 55, `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)` — aceeași referință la listă, nu o copie.
3. Scrie lanțul de la `notifyDataSetChanged()` la redesenare: `BaseAdapter` → `DataSetObservable.notifyChanged()` → observer-ul din `AbsListView` → `mDataChanged = true` + `requestLayout()`.
4. Scrie varianta pentru `RecyclerView`: `notifyItemInserted(movies.size() - 1)` la inserare, `notifyItemChanged(position)` la editare.
5. Verificare pe emulator: comentează `notifyDataSetChanged()` doar pe ramura `else`, editează un film → rândul rămâne cu valorile vechi. Pune-l la loc → rândul se actualizează.

**Indiciu 1 — dacă te blochezi la pasul 4:** `ArrayAdapter` nu are `notifyItemChanged`. Metoda aia există doar pe `RecyclerView.Adapter`, deci pe `ListView` singura variantă corectă e `notifyDataSetChanged()`.

**Indiciu 2 — dacă te blochezi la pasul 5:** ordinea e „mută, apoi notifică". Iar obiectul din `Intent` e o instanță nouă (deserializată), deci fără `movies.set(position, movie)` editarea se pierde chiar și cu notify corect.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-a păstrat varianta corectă pentru `ListView` și s-a scris varianta fină pentru `RecyclerView`.

**Cod:**

```java
// MainActivity — ListView + ArrayAdapter (starea de la d719ffc, corectă)
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

```java
// MainActivity — dacă ai trecut pe RecyclerView (MovieAdapter, capitolul 11)
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyItemInserted(movies.size() - 1);
} else {
    movies.set(position, movie);
    movieAdapter.notifyItemChanged(position);
}
```

**De ce:**

- **Adapterul nu copiază lista.** `new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)` (linia 55) păstrează o referință la **același** `ArrayList`. Deci `movies.set(position, movie)` schimbă ce ar returna adapterul la `getItem(position)` — dar nimeni nu-i spune `ListView`-ului să recitească. `notifyDataSetChanged()` e semnalul: `BaseAdapter` → `DataSetObservable.notifyChanged()` → observer-ul din `AbsListView` marchează `mDataChanged = true` și cere un layout.
- **`notifyItemChanged(int)` nu există pe `ArrayAdapter`.** E declarată pe `RecyclerView.Adapter`. Apelul pe un adapter de `ListView` e eroare de compilare, nu de runtime — deci nu poți „greși discret".
- **Cu `ListView`**, `notifyDataSetChanged()` e singura variantă corectă. Reconstruiește toate rândurile vizibile. Pentru 3–4 filme, costul e zero.
- **Cu `RecyclerView`**, variantele fine sunt corecte **și** animate: `notifyItemChanged(position)` rebindează un singur rând, `notifyItemInserted(index)` animă inserarea. `notifyDataSetChanged()` merge și el, dar rebindează tot și anulează animațiile.
- **Ordinea: întâi muți, apoi notifici.** `notifyItemChanged(position)` înainte de `movies.set(...)` e o cerere de rebind care se execută la următorul layout — de obicei prinde totuși obiectul nou, fiindcă `set` rulează sincron imediat după. Dar `notifyItemInserted(size)` înainte de `add` e garantat greșit: `RecyclerView` validează numărul de elemente și aruncă `IndexOutOfBoundsException: Inconsistency detected`. Habitul „mută, apoi notifică" e singurul care e mereu corect.
- **De ce obiectul trebuie înlocuit:** `getSerializableExtra` **deserializează**. `Movie`-ul care se întoarce din `ItemActivity` e o instanță nouă, nu cea din listă. Fără `movies.set(position, movie)`, editarea se pierde chiar cu un notify perfect.
- La `d719ffc`, textul rândului e `Movie.toString()`: `ArrayAdapter` cu `simple_list_item_1` are `mFieldId == 0` și face `text.setText(item.toString())`. Deci orice câmp schimbat schimbă rândul — de aceea un notify lipsă se vede imediat, cu tot dump-ul de câmpuri.

**De reținut:** `notifyDataSetChanged` = „s-ar putea să se fi schimbat orice, rebindează tot". `notifyItem*` = „exact asta s-a schimbat". Prima e mereu corectă; a doua e corectă doar dacă indexul și datele sunt de acord. Ambele trebuie apelate de pe thread-ul principal.

**Unde se aplică:** orice actualizare de listă — inserare, editare, ștergere. Același raționament stă la baza `DiffUtil` (capitolul 11): el calculează pentru tine seria de `notifyItem*`.

</details>

---

## Exercițiul 19.10 — Combo de examen: valoare în etichetă + eroare de validare

**Cerință:** cât timp utilizatorul tastează în `etBudget`, eticheta `tvBudgetValue` arată valoarea imediat, iar dacă textul nu e un număr pe câmp apare o eroare. Apăsarea pe Save cu bugetul gol **nu** are voie să crapă aplicația.

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — `initListeners` (watcher-ul) și `saveMovie` (linia 173).

**Cum abordezi — pașii tăi:**
1. Pornește de la watcher-ul construit la 19.3. Nu scrie altul — îl extinzi pe acela.
2. Împarte `afterTextChanged` în trei ramuri: gol (șterge eroarea, afișează `$0`), valid (formatează, șterge eroarea), invalid (afișează `—`, pune eroarea).
3. Deschide `saveMovie()` la linia 173 și înlocuiește `movie.setBudget(Double.parseDouble(...))` cu varianta cu gardă: `isEmpty()` → `setError` + `requestFocus` + `return`; apoi `try/catch` în jurul parsării.
4. Verificare pe emulator: golește bugetul și apasă Save → aplicația **nu** crapă, eroarea apare pe câmp, activitatea rămâne deschisă. Scrie `abc` → eroare. Șterge și scrie `100` → eroarea dispare. Save → te întorci în listă cu 4 filme.

**Indiciu 1 — dacă te blochezi la pasul 2:** folosește `afterTextChanged`, nu `onTextChanged` — doar acolo ai `Editable`-ul final. `setError(null)` pe ramurile gol și valid e la fel de important ca `setError("...")` pe cea invalidă.

**Indiciu 2 — dacă te blochezi la pasul 3:** `Double.parseDouble("")` aruncă `NumberFormatException`. `return` trebuie să vină **înainte** de `setResult`/`finish()`, altfel trimiți în `MainActivity` un film incomplet.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** watcher-ul de la 19.3 a primit validare, iar `saveMovie` a primit gardă de parsare.

**Cod:**

```java
// initListeners() — înlocuiește watcher-ul din 19.3
etBudget.addTextChangedListener(new TextWatcher() {
    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

    @Override
    public void onTextChanged(CharSequence s, int start, int before, int count) { }

    @Override
    public void afterTextChanged(Editable s) {
        String raw = s.toString().trim();
        if (raw.isEmpty()) {
            tvBudgetValue.setText("$0");
            etBudget.setError(null);
            return;
        }
        try {
            double value = Double.parseDouble(raw);
            tvBudgetValue.setText("$" + budgetFormat.format(value));
            etBudget.setError(null);
        } catch (NumberFormatException e) {
            tvBudgetValue.setText("—");
            etBudget.setError("Not a valid number");
        }
    }
});
```

```java
// saveMovie() — înlocuiește linia 173
String budgetText = etBudget.getText().toString().trim();
if (budgetText.isEmpty()) {
    etBudget.setError("Budget is required");
    etBudget.requestFocus();
    return;
}
double budget;
try {
    budget = Double.parseDouble(budgetText);
} catch (NumberFormatException e) {
    etBudget.setError("Not a valid number");
    etBudget.requestFocus();
    return;
}
movie.setBudget(budget);
```

**De ce:**

- **`afterTextChanged`, nu `onTextChanged`.** `onTextChanged` se apelează în timpul modificării; dacă scrii în text de acolo, intri în re-entranță. `afterTextChanged` primește `Editable`-ul final și e singurul callback în care modificarea textului e legală (cu gardă).
- **Gol nu înseamnă invalid.** Un câmp gol înseamnă „utilizatorul nu a tastat încă" — să-i pui eroare roșie pe un formular virgin e greșit. Gol → șterge eroarea, afișează `$0`.
- **`setError(null)` pe ramura validă.** Fără el, iconița roșie rămâne după ce utilizatorul corectează valoarea. Asta e jumătatea de „păstrare corectă a stării" din cerință: eroarea e și ea stare.
- **`Double.parseDouble("")` aruncă** `NumberFormatException: empty String`. La `d719ffc`, linia 173 o cheamă necondiționat, deci Save cu bugetul gol **crapă aplicația**. Garda din `saveMovie` e obligatorie chiar și cu watcher-ul, pentru că watcher-ul doar afișează eroarea — nu oprește butonul.
- **`return` înainte de `setResult`/`finish()`.** Activitatea rămâne deschisă, utilizatorul vede eroarea, nimic nu pleacă înapoi în `MainActivity`. Dacă ai chema `setResult` întâi și ai ieși după, `MainActivity` ar primi un film incomplet.
- `Double.parseDouble` acceptă și `"NaN"`, `"Infinity"` și hex float (`"0x1p3"`). Dacă examenul e strict, adaugă după parsare: `if (!Double.isFinite(value)) { ... }`.
- Tastatura `numberDecimal` restricționează tastarea, dar nu paste-ul, nu tastaturile hardware și nu `setText`. Validarea rămâne obligatorie.
- `etBudget.setError(...)` e varianta simplă. Cu `TextInputLayout` în jur, poți folosi `TextInputLayout.setError(...)` — dar atunci ai nevoie de un `android:id` pe layout (acum nu are, linia 165).

**De reținut:** cerința „leagă valoarea de UI" înseamnă aproape întotdeauna: un listener, o etichetă și eroarea ștearsă pe **toate** ramurile. Ramurile sunt trei: gol, valid, invalid. Dacă ratezi una, starea rămâne greșită — exact ce se notează la test.

**Unde se aplică:** `etTitle` (obligatoriu, nu gol), `etPoster` (verificare de URL), `etRelease` (parsare cu `SimpleDateFormat`, care aruncă `ParseException` în loc de `NumberFormatException` — aceeași structură, alt tip de excepție).

</details>

---

## Recapitulare — ce verifici la test

| Cerința din examen | Mecanismul | Exercițiu |
|---|---|---|
| „când schimb X, eticheta să arate Y" | listener pe widget | 19.1, 19.2, 19.3, 19.4 |
| „câmpul să nu accepte mai mult de N" | `InputFilter.LengthFilter` | 19.2 |
| „după Save, arată câte sunt" | `movies.size()` după mutație | 19.5 |
| „rotația nu pierde datele" | `onSaveInstanceState` + câmpurile care nu sunt `View` | 19.6 |
| „arată `1.6E8`" | `String.format("%.0f")` / `BigDecimal.toPlainString()` | 19.7 |
| „crapă când lipsește data" | gardă `null`; NPE-ul vine din framework | 19.8 |
| „lista arată date vechi" | `notifyDataSetChanged` vs. `notifyItemChanged` | 19.9 |
| „arată valoarea + eroare" | `TextWatcher` + `setError` pe toate ramurile | 19.10 |

Trei propoziții de memorat:

1. **Listenerul se apelează și la apel programatic**, dar numai dacă valoarea se schimbă — de aceea `fillForm` funcționează, și de aceea uneori funcționează „din noroc".
2. **Framework-ul salvează singur `View`-urile cu `id`.** Ce nu salvează sunt câmpurile tale — `releaseCal` e exemplul canonic.
3. **`String.valueOf(număr)` minte la valori mari sau `float`.** Format explicit, mereu.
