# Capitolul 10 — Reconstruiește de la zero

**Obiectiv:** să reproduci întreaga aplicație `G1097` **fără material**, în 90 de minute, cu doar documentația Android deschisă. Acesta e testul real.

**Timp estimat:** 90 min (prima încercare), 45 min (a doua), 30 min (a treia).

---

## Regulile drill-ului

1. **Proiect nou**, de la zero. Nu copia fișiere din `_progres/` sau `cod-final/`.
2. **Nu deschide capitolele 01–09.** Dacă te blochezi, notează unde, continuă, revino la final.
3. Ai voie să deschizi: documentația Android, Stack Overflow, `cod-final/` **doar la final**, pentru comparație.
4. Cronometrează. Notează timpul.
5. La final, completează tabelul de mai jos.

---

## Ordinea de construcție (fără să te uiți)

Aceasta e ordinea care funcționează. Dacă o urmezi, nu te blochezi.

### Faza 1 — schelet (10 min)

1. Proiect nou, Empty Views Activity, Java, `minSdk 33`, package `ro.ase.ie.g1097`.
2. `MainActivity` mutat în `ro.ase.ie.g1097.activities`.
3. `themes.xml`: `Theme.Material3.DayNight.NoActionBar`.
4. `strings.xml`: `app_name`, `items` (20), `movie_genre` (10).
5. `outline_add_24.xml` (Vector Asset → Add).
6. Rulează: „Hello World”.

### Faza 2 — model (10 min)

7. `ro.ase.ie.g1097.model.Movie` cu 10 câmpuri, `Serializable`.
8. Constructor gol + constructor 10 parametri.
9. Getteri/setteri (Alt+Insert).
10. `toString()` (Alt+Insert).

### Faza 3 — ecranul principal (15 min)

11. `activity_main.xml`: `FrameLayout` + `ListView` + FAB.
12. `MainActivity`: câmpuri, `onCreate`, `EdgeToEdge`, insets.
13. `addSampleMovies()` cu 3 filme.
14. `ArrayAdapter` + `initControls`.
15. Rulează: 3 filme în listă.

### Faza 4 — formularul (25 min)

16. `activity_item.xml`: `ScrollView` + `LinearLayout` + 4 carduri.
17. Card 1: Title, Genre, Release.
18. Card 2: Budget, Duration.
19. Card 3: Rating, Switch, CheckBox, RadioGroup.
20. Card 4: Poster.
21. Buton Save.
22. Rulează (temporar `setContentView(R.layout.activity_item)`).

### Faza 5 — `ItemActivity` (20 min)

23. Clasă nouă + declarare în manifest.
24. Câmpuri + `onCreate` + insets.
25. `initControls` (13 `findViewById`).
26. `initListeners` (date, save, seekbar, switch).
27. `showReleaseDatePicker`.
28. `saveMovie`.
29. Rulează: formularul se deschide, Save nu crăpă.

### Faza 6 — navigare (10 min)

30. `launcher` cu `registerForActivityResult`.
31. `initListeners` complet (FAB + item click).
32. `onActivityResult` cu `add` / `set`.
33. Rulează: adaugi un film, apare în listă.

### Faza 7 — editare (10 min)

34. `getIntent()` + `existing != null`.
35. `fillForm`.
36. `setTitle` + `setText` pe buton.
37. Rulează: editezi un film, se actualizează.

---

## Tabel de cronometrare

| Încercare | Data | Timp total | Unde te-ai blocat | Ce ai căutat |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Ținta:** sub 45 min fără blocaje majore.

---

## Checklist final (fără să te uiți la cod)

Bifează doar dacă ai scris tu, din memorie.

### Structură
- [ ] proiect Gradle cu `minSdk 33`, Java 11
- [ ] `MainActivity` și `ItemActivity` în `ro.ase.ie.g1097.activities`
- [ ] ambele declarate în manifest, `MainActivity` cu `exported="true"`
- [ ] tema `Theme.Material3.DayNight.NoActionBar`

### Model
- [ ] `Movie implements Serializable`
- [ ] 10 câmpuri cu tipurile corecte
- [ ] constructor gol **explicit**
- [ ] constructor 10 parametri
- [ ] `isWatched()` / `isOnWatchlist()`

### `activity_main.xml`
- [ ] `FrameLayout` cu `id=main`
- [ ] `ListView` cu `id=listView`
- [ ] FAB cu `layout_gravity="bottom|end"`
- [ ] ordinea: ListView, apoi FAB

### `MainActivity`
- [ ] `EdgeToEdge` + insets pe `R.id.main`
- [ ] `addSampleMovies` cu 3 filme
- [ ] `ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`
- [ ] `initControls` cu `setAdapter`
- [ ] `launcher` cu `StartActivityForResult`
- [ ] `onActivityResult`: `RESULT_OK` → `add` sau `set` → `notifyDataSetChanged`
- [ ] `initListeners`: FAB + `setOnItemClickListener`

### `activity_item.xml`
- [ ] `ScrollView` cu `id=main`, `fillViewport`
- [ ] 4 `MaterialCardView`
- [ ] `TextInputLayout` + `TextInputEditText` pentru Title, Release, Budget, Poster
- [ ] `Spinner` cu `entries`
- [ ] `SeekBar` cu `max=300`
- [ ] `RatingBar` cu `numStars=5`, `stepSize=0.5`
- [ ] `MaterialSwitch` + `MaterialCheckBox`
- [ ] `RadioGroup` cu 5 `MaterialRadioButton`
- [ ] `MaterialButton` cu `id=btnMovieAction`

### `ItemActivity`
- [ ] 13 câmpuri + `position = -1` + `releaseCal` + `dateFormat`
- [ ] `initControls`: 13 `findViewById`
- [ ] `initListeners`: `etRelease`, `btMovieAction`, `sbDuration`, `swWatched`
- [ ] `showReleaseDatePicker` cu `DatePickerDialog`
- [ ] `saveMovie`: 10 setteri + iterație radio + `setResult` + `finish`
- [ ] `getIntent()` + `fillForm` + `setTitle` + buton

---

## Teste funcționale (pe emulator)

Rulează-le pe toate. Dacă una eșuează, ai un bug.

| # | Test | Rezultat așteptat |
|---|---|---|
| 1 | Pornește aplicația | 3 filme în listă |
| 2 | Apasă FAB | formular gol, buton „Save Movie” |
| 3 | Completează + Save | 4 filme, ultimul e cel nou |
| 4 | Apasă Back fără Save | lista rămâne cu 3 |
| 5 | Atinge un film | formular populat, buton „Update Movie” |
| 6 | Modifică titlul + Update | lista are tot 3, titlul e schimbat |
| 7 | Click pe Release | se deschide calendarul |
| 8 | Alege o dată | câmpul se actualizează `dd/MM/yyyy` |
| 9 | Mișcă SeekBar | `tvDurationValue` se actualizează |
| 10 | Comută switch | `tvWatchedValue` devine „Yes” |
| 11 | Save cu buget gol | **crash** (bug cunoscut) |
| 12 | Editează film cu data | data apare corect |
| 13 | Rotire ecran | **formularul se golește** (stare pierdută) |

### Despre testul 13

Rotirea ecranului **recreează** activitatea (`onCreate` se apelează din nou). Câmpurile se pierd pentru că nu salvezi starea în `onSaveInstanceState`.

E un **comportament cunoscut** al repo-ului, nu un bug de reparat acum. Dar trebuie să știi de ce se întâmplă — e o întrebare clasică de test.

---

## Ce faci dacă te blochezi

| Simptom | Cauză probabilă | Verifică |
|---|---|---|
| `ClassNotFoundException` la pornire | activitatea nu e în manifest | `AndroidManifest.xml` |
| `NullPointerException` în `initControls` | `setContentView` lipsește sau e după | ordinea din `onCreate` |
| Lista e goală | `setAdapter` lipsește | `initControls` |
| Filmul nu apare după Save | `notifyDataSetChanged` lipsește | `onActivityResult` |
| Formularul se deschide gol la editare | `getIntent` nu citește extra-ul | cheia `MOVIE_EXTRA` |
| `NumberFormatException` la Save | buget gol | `Double.parseDouble` |
| `NullPointerException` la editare | `release` e `null` | `fillForm` |
| Butonul nu face nimic | listener-ul nu e legat | `initListeners` |
| Spinner-ul arată prima opțiune greșită | genul nu e în listă | bucla din `fillForm` |

---

## După drill

Dacă ai reușit sub 45 min fără să deschizi materialul: **ai stăpânit aplicația**. Treci la capitolul 11.

Dacă ai avut blocaje: notează-le în tabel, recitește capitolul relevant, repetă peste 2 zile.

---

**Următorul capitol:** [11 - Extensii.md](11%20-%20Extensii.md)
