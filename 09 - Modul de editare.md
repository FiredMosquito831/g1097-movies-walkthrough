# Capitolul 09 — Modul de editare

**Obiectiv:** `ItemActivity` primește un `Movie` existent, umple formularul cu valorile lui, iar la Save trimite înapoi filmul modificat + poziția. `MainActivity` îl înlocuiește în listă.

**Timp estimat:** 30–45 min.

**Fișier final:** `cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java` — versiunea completă, cu `fillForm` și blocul din `onCreate`.

---

## Pasul 9.1 — Citirea `Intent`-ului în `onCreate`

### De ce

`ItemActivity` trebuie să știe **de ce** a fost deschisă:

- din FAB → `Intent` fără extra-uri → insert mode;
- din click pe listă → `Intent` cu `Movie` + `position` → edit mode.

### Cum

Adaugă în `onCreate`, **după** `initListeners()`:

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

### De ce `existing != null` e testul corect

Nu testezi `intent.hasExtra(MOVIE_EXTRA)` — deși ar merge. Testezi **rezultatul** citirii:

- dacă extra-ul lipsește → `null`;
- dacă extra-ul există dar e de alt tip → `null` (sau excepție);
- dacă extra-ul există și e `Movie` → obiectul.

Deci `existing != null` e mai robust.

### De ce `setTitle("Edit movie")`

Schimbă titlul ferestrei (în recents, în bara de sus dacă ar exista). E feedback vizual că ești în modul editare.

> **Atenție:** `setTitle` pe `Activity` setează titlul **ferestrei**, nu al unui `TextView`. Cu tema `NoActionBar`, nu vezi nimic pe ecran — doar în recents.

### De ce `btMovieAction.setText("Update Movie")`

Butonul spune „Save Movie” în insert mode și „Update Movie” în edit mode. Schimbă textul, schimbă și așteptarea utilizatorului.

### Exercițiu 9.1

**Cerință:** adaugă și un schimb de culoare: în edit mode, butonul devine portocaliu. Cum?

<details>
<summary>Indiciu</summary>

`MaterialButton` are `setBackgroundTintList(ColorStateList)`. Sau poți folosi `setBackgroundColor`.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat în blocul `if (existing != null)`:

```java
btMovieAction.setBackgroundTintList(
        android.content.res.ColorStateList.valueOf(
                android.graphics.Color.parseColor("#FF9800")));
```

**Ce se vede:** în edit mode, butonul devine portocaliu.

**De ce `setBackgroundTintList` și nu `setBackgroundColor`:** `MaterialButton` folosește un `MaterialShapeDrawable` ca fundal. `setBackgroundColor` l-ar înlocui și ai pierde colțurile rotunjite + ripple. `setBackgroundTintList` **nuanțează** fundalul existent.

**De reținut:**
1. `MaterialButton` are API-uri speciale: `setBackgroundTintList`, `setIconTint`, `setStrokeColor`.
2. `ColorStateList.valueOf(color)` creează o listă cu o singură culoare pentru toate stările.
3. Pentru culori din temă: `MaterialColors.getColor(btMovieAction, com.google.android.material.R.attr.colorPrimary)`.

**Unde revine:** nu revine, dar e o tehnică utilă pentru a diferenția vizual stările.

</details>

---

## Pasul 9.2 — `fillForm`: umplerea formularului

### De ce

Ai un `Movie` existent. Trebuie să pui fiecare valoare în widget-ul corespunzător. E inversul lui `saveMovie`.

### Cum

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
}
```

### Maparea inversă

| Câmp model | Widget | Metodă de scriere |
|---|---|---|
| `title` | `etTitle` | `setText(String)` |
| `release` | `etRelease` | `setText(dateFormat.format(Date))` |
| `genre` | `spGenre` | `setSelection(index)` — **caută indexul** |
| `budget` | `etBudget` | `setText(String.valueOf(double))` |
| `duration` | `sbDuration` | `setProgress(int)` |
| `rating` | `rbRating` | `setRating(float)` |
| `watched` | `swWatched` | `setChecked(boolean)` |
| `onWatchlist` | `cbonWatchList` | `setChecked(boolean)` |
| `poster` | `etPoster` | `setText(String)` |
| `approval` | `rgApproval` | `check(id)` — **caută butonul** |

### De ce `String.valueOf(existing.getBudget())`

`EditText.setText` acceptă `CharSequence`, nu `double`. `String.valueOf(double)` convertește.

> **Atenție:** `String.valueOf(160000000.0)` întoarce `"1.6E8"`! Nu `"160000000"`. Vei vedea în câmp `1.6E8`. E o **problemă reală** în repo.

Verifică: `Double.toString(160000000.0)` → `"1.6E8"`. Da.

**Soluția corectă** ar fi `String.format(Locale.US, "%.0f", existing.getBudget())` sau `new BigDecimal(...).toPlainString()`.

### De ce `spGenre.setSelection(index)` și nu `setSelection(text)`

`Spinner` **nu are** `setSelectionByText`. Are doar `setSelection(int position)`.

Deci trebuie să cauți manual indexul:

```java
for (int index = 0; index < spGenre.getCount(); index++) {
    if (spGenre.getItemAtPosition(index).equals(existing.getGenre())) {
        spGenre.setSelection(index);
        break;
    }
}
```

`getItemAtPosition(index)` întoarce `Object` — aici `String`, pentru că `entries` creează un `ArrayAdapter<String>`.

### De ce `.equals()` și nu `==`

`==` compară **referințe**. `String`-urile din `entries` și cel din `Movie` sunt obiecte diferite, chiar dacă au același text. `.equals()` compară **conținutul**.

> **Aceasta e o greșeală clasică la test:** `==` pe `String` compară referințe, nu valori.

### De ce `rgApproval.check(id)` și nu `rb.setChecked(true)`

Ambele ar merge. Dar `rgApproval.check(id)` e metoda **grupului**: garantează că celelalte butoane se deselectează. `rb.setChecked(true)` ar putea lăsa două butoane bifate dacă grupul nu e sincronizat.

### Exercițiu 9.2

**Cerință:** ce se întâmplă dacă `existing.getGenre()` e `"Documentary"` și nu e în `movie_genre`? Rulează mental.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am urmărit bucla când genul nu e găsit.

**Ce se întâmplă:** bucla se termină fără `break`. `spGenre.setSelection(...)` **nu e apelat**. Deci spinner-ul rămâne pe **prima** opțiune (`Drama`).

**Ce se vede:** formularul arată genul `Drama`, deși filmul are `Documentary`. La Save, filmul va primi `Drama` — **date corupte silențios**.

**De ce:** nu există un `else` care să semnaleze „genul nu există”. Bucla e pur optimistă.

**De reținut:**
1. **Buclele de căutare fără `else`** pot ascunde date invalide.
2. Soluția: după buclă, verifică dacă ai găsit ceva. Dacă nu, adaugă opțiunea lipsă sau setează o valoare implicită.
3. Aici e un **risc real**: dacă profesorul adaugă un gen nou în `movie_genre` și utilizatorul salvează un film cu el, apoi îl editează, genul se pierde.

**Unde revine:** în cap. 11, `MovieAdapter` afișează `movie.getGenre()` direct — deci genul corect apare în listă, dar formularul îl arată greșit. Inconsecvență.

</details>

---

## Pasul 9.3 — Capcana `release == null`

### De ce

`dateFormat.format(null)` aruncă `NullPointerException`.

### Când se întâmplă

Dacă un film a fost creat cu constructorul gol și **fără** `setRelease`:

```java
Movie movie = new Movie();
movie.setTitle("Test");
// release rămâne null
```

Apoi `fillForm` apelează `dateFormat.format(existing.getRelease())` → **NPE**.

### Versiunea din repo (`d719ffc`)

```java
etRelease.setText(dateFormat.format(existing.getRelease()));
```

**Crăpă** dacă `release` e `null`.

### Versiunea ta locală (modificare necomisă)

```java
if (existing.getRelease() != null) {
    releaseCal.setTime(existing.getRelease());
    etRelease.setText(dateFormat.format(existing.getRelease()));
}
```

**Nu crăpă** — sare peste.

### Exercițiu 9.3

**Cerință:** creează un film cu `release = null` (adaugă-l manual în `addSampleMovies`), apoi încearcă să-l editezi. Ce se întâmplă cu versiunea din repo?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat în `addSampleMovies`:

```java
Movie broken = new Movie();
broken.setTitle("No date");
broken.setGenre("Drama");
movies.add(broken);
```

**Ce se întâmplă:** la click pe „No date”, `ItemActivity` crăpă:

```
java.lang.NullPointerException: Attempt to invoke virtual method
'java.lang.String java.text.SimpleDateFormat.format(java.util.Date)'
on a null object reference
```

**De ce:** `SimpleDateFormat.format(null)` nu are ce formata. Aruncă NPE.

**De reținut:**
1. **Orice metodă care primește un obiect poate arunca NPE dacă primește `null`.**
2. `String.valueOf(null)` **nu** aruncă — întoarce `"null"`. Dar `dateFormat.format(null)` aruncă.
3. Diferența: `String.valueOf` e static și acceptă `Object`; `format` e instanță și cere `Date` non-null.

**Reparația:** adaugă verificarea `if (existing.getRelease() != null)`. E exact ce face versiunea ta locală.

**Unde revine:** în cap. 11, `MovieAdapter` are deja verificarea:

```java
String yearStr = movie.getRelease() != null ? dateFormat.format(movie.getRelease()) : "";
```

Acolo e tratat corect.

</details>

---

## Pasul 9.4 — Fluxul complet de editare

### Cum

1. Utilizatorul atinge un film în listă.
2. `onItemClick` → `intent.putExtra(MOVIE_EXTRA, movies.get(position))` + `putExtra(POSITION_EXTRA, position)`.
3. `launcher.launch(intent)`.
4. `ItemActivity.onCreate` → citește `existing` → `position = ...` → `fillForm(existing)`.
5. Formularul e populat.
6. Utilizatorul modifică, apasă „Update Movie”.
7. `saveMovie()` → construiește `Movie` nou → `putExtra(MOVIE_EXTRA, movie)` + `putExtra(POSITION_EXTRA, position)` → `setResult(RESULT_OK)`.
8. `MainActivity.onActivityResult` → `position != -1` → `movies.set(position, movie)`.
9. `notifyDataSetChanged()` → lista se actualizează.

### De ce `movies.set(position, movie)` și nu `movies.add`

`set` **înlocuiește** elementul de la poziția dată. `add` ar adăuga un duplicat la final.

### Exercițiu 9.4

**Cerință:** schimbă `movies.set(position, movie)` cu `movies.add(movie)`. Rulează, editează un film. Ce se întâmplă?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit `set` cu `add` în `onActivityResult`.

**Ce se vede:** după editare, filmul apare **de două ori** în listă: versiunea veche la poziția originală, versiunea nouă la final.

**De ce:** `add` adaugă la coadă. Nu șterge nimic.

**De reținut:**
1. `List.set(index, element)` = înlocuiește, dimensiunea rămâne aceeași.
2. `List.add(element)` = adaugă la final, dimensiunea crește.
3. `position` e singura informație care îți spune **unde** să înlocuiești.

**Unde revine:** nu revine, dar e o întrebare de test: „ce diferență e între `add` și `set`?”.

</details>

---

## Pasul 9.5 — Verificare completă

### Cum

1. Rulează.
2. Vezi 3 filme.
3. Atinge „Inception” → formularul se deschide cu toate câmpurile completate.
4. Butonul spune „Update Movie”.
5. Schimbă titlul în „Inception (2010)”.
6. Apasă Update.
7. **Verifică:** lista are tot 3 filme, primul e acum „Inception (2010)”.

### Ce verifici

- [ ] `fillForm` umple toate cele 10 câmpuri
- [ ] `position` e setat corect
- [ ] butonul spune „Update Movie”
- [ ] `movies.set(position, movie)` înlocuiește, nu adaugă
- [ ] lista rămâne cu 3 elemente

### Teste de margine

- [ ] editezi, apoi apeși **Back** → lista rămâne neschimbată
- [ ] editezi, salvezi, apoi editezi din nou → valorile sunt cele noi
- [ ] adaugi un film nou, apoi îl editezi → merge

---

## Pasul 9.6 — Exercițiu de reflecție: de ce `position` și nu `id`

**Cerință:** de ce `position` (index în listă) și nu un `id` unic per film?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** repo-ul folosește poziția în listă ca identificator.

**De ce e problematic:**
1. **Poziția se schimbă** dacă adaugi/ștergi elemente. Dacă ai trimite `position = 2` și între timp s-ar adăuga un element la început, ai edita filmul greșit.
2. **Nu e stabilă** între sesiuni. La repornire, lista se reconstruiește de la 0.
3. **Nu e unică** în sens semantic — doi pași pot avea aceeași poziție în momente diferite.

**De ce merge aici:** lista nu se modifică în timp ce ești în `ItemActivity`. Deci poziția e stabilă pe durata editării.

**Cum ar fi corect:** fiecare `Movie` ar avea un `long id` generat la creare (ex. `System.currentTimeMillis()` sau un contor). La editare, trimiți `id`-ul, iar `MainActivity` caută filmul cu acel `id`.

**De reținut:**
1. **Indexul nu e identitate.** E o poziție într-o structură care se poate schimba.
2. Pentru liste mici și statice, indexul e acceptabil. Pentru liste dinamice, ai nevoie de `id`.
3. În baze de date (Room, SQLite), `id` e obligatoriu.

**Unde revine:** în cap. 11, `RecyclerView.Adapter` folosește `getBindingAdapterPosition()` — tot un index. Dar acolo e sigur, pentru că lista nu se schimbe în timpul unui bind.

</details>

---

## Pasul 9.7 — Compară cu originalul

```bash
diff "cod-final/java/ro/ase/ie/g1097/activities/ItemActivity.java" \
     "_progres/Movies1097/app/src/main/java/ro/ase/ie/g1097/activities/ItemActivity.java"
```

La acest stadiu, fișierul tău ar trebui să fie **identic** cu `cod-final` (mai puțin eventualele exerciții pe care le-ai făcut).

---

## Rezumat capitol 09

- `getIntent()` + `IntentCompat.getSerializableExtra` → detectezi modul.
- `fillForm` = inversul lui `saveMovie`.
- `Spinner` nu are `setSelection(text)` → cauți indexul.
- `RadioGroup.check(id)` garantează exclusivitatea.
- `String.valueOf(double)` poate da notație științifică (`1.6E8`).
- `dateFormat.format(null)` = NPE — bug real în repo.
- `movies.set(position, movie)` înlocuiește; `add` ar duplica.

**Următorul capitol:** [10 - Reconstruieste de la zero.md](10%20-%20Reconstruieste%20de%20la%20zero.md)
