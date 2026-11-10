# Test 1 — G1097: aplicația Movies, de la zero

**Ținta:** să poți reconstrui singur, pornind de la un proiect gol, aplicația `G1097` la starea din commitul **`d719ffc`** (`G1097_S07`, 2026-11-09) — și apoi să o extinzi.

**Sursa de adevăr:** `Android dev/dma2026-sync-2026-11-10/G1097/` (clone curat al repo-ului `mihaidoinea/dma2026`, branch `main`, HEAD `d719ffc`).
**Codul final, copiat aici:** `cod-final/` — 17 fișiere, cu hash-uri SHA-256 în `cod-final/HASH-URI.txt`.

> **Regula de aur:** nu copia. Tastează. Fiecare dată când copiezi, pierzi exact exercițiul pe care îl vei da la test.
> Când greșești — și vei greși — citește eroarea din `Build` înainte să te uiți la soluție. Eroarea îți spune fișierul și linia.

---

## Ce construiești

O aplicație cu **două ecrane**:

| Ecran | Ce face |
|---|---|
| `MainActivity` | Afișează o listă de filme. Buton flotant „+” jos-dreapta. Atingi un film → îl editezi. |
| `ItemActivity` | Formular complet de film: titlu, gen, dată, buget, durată, rating, „recomandat”, „watchlist”, ghidaj parental, poster. Butonul salvează și se întoarce. |

Datele circulă **în memorie**, într-un `ArrayList<Movie>` din `MainActivity`. Nu există bază de date, nu există rețea, nu există fișiere. Totul se pierde la închiderea aplicației — și asta e intenționat.

```
MainActivity
  ├── List<Movie> movies        ← singura sursă de date
  ├── ArrayAdapter<Movie>       ← leagă lista de ListView
  └── ActivityResultLauncher    ← așteaptă răspuns de la ItemActivity
                │
                │  Intent + Movie (Serializable) + position
                ▼
ItemActivity
  ├── citește Movie din Intent (dacă există)
  ├── umple formularul
  └── la Save: construiește Movie nou → setResult(RESULT_OK) → finish()
```

---

## Cum se folosește acest material

Pentru fiecare pas:

1. **Citește „De ce” și „Cum”.** Nu sări peste „De ce” — la test ți se cere să explici, nu doar să scrii.
2. **Închide soluția.** Fă exercițiul singur.
3. **Rulează.** `Run ▶` pe emulator. Dacă nu compilează, citește eroarea.
4. **Abia apoi** deschide indiciul. Dacă tot nu merge, deschide soluția.
5. **Compară** codul tău cu soluția **linie cu linie**. Diferă ceva? Întreabă-te de ce.
6. **Bifează** pasul în tabelul de progres de mai jos.

Un pas e „gata” când: codul compilează, aplicația rulează, și poți explica **fără să te uiți** de ce ai scris ce ai scris.

---

## Ordinea capitolelor

| # | Fișier | Ce înveți | Pași |
|---|---|---|---|
| 01 | [01 - Setup si schelet.md](01%20-%20Setup%20si%20schelet.md) | Proiect, Gradle, manifest, primul ecran care rulează | 1.1–1.10 |
| 02 | [02 - Modelul Movie.md](02%20-%20Modelul%20Movie.md) | Clasă de model, tipuri, `Serializable`, constructori, getteri | 2.1–2.9 |
| 03 | [03 - Ecranul principal - layout.md](03%20-%20Ecranul%20principal%20-%20layout.md) | `FrameLayout`, `ListView`, `FloatingActionButton`, drawable vector | 3.1–3.7 |
| 04 | [04 - MainActivity - lista.md](04%20-%20MainActivity%20-%20lista.md) | `onCreate`, `ArrayAdapter`, date demo, `Calendar`, insets | 4.1–4.10 |
| 05 | [05 - Formularul - partea 1.md](05%20-%20Formularul%20-%20partea%201.md) | `ScrollView`, `MaterialCardView`, `TextInputLayout`, `Spinner` | 5.1–5.11 |
| 06 | [06 - Formularul - partea 2.md](06%20-%20Formularul%20-%20partea%202.md) | `SeekBar`, `RatingBar`, `MaterialSwitch`, `CheckBox`, `RadioGroup`, `MaterialButton` | 6.1–6.12 |
| 07 | [07 - ItemActivity - citire si scriere.md](07%20-%20ItemActivity%20-%20citire%20si%20scriere.md) | `findViewById`, listeneri, `DatePickerDialog`, `saveMovie` | 7.1–7.11 |
| 08 | [08 - Navigarea si rezultatul.md](08%20-%20Navigarea%20si%20rezultatul.md) | `Intent`, `ActivityResultLauncher`, `Serializable`, `RESULT_OK` | 8.1–8.9 |
| 09 | [09 - Modul de editare.md](09%20-%20Modul%20de%20editare.md) | `fillForm`, `position`, adăugare vs. înlocuire | 9.1–9.7 |
| 10 | [10 - Reconstruieste de la zero.md](10%20-%20Reconstruieste%20de%20la%20zero.md) | Drill final, cronometrat, fără material | — |
| 11 | [11 - Extensii.md](11%20-%20Extensii.md) | `RecyclerView`, `ViewHolder`, `onBindViewHolder`, atribute noi | 11.1–11.14 |

---

## Tabel de progres

Bifează pe măsură ce termini. Un capitol e gata doar când aplicația **rulează** la finalul lui.

| Capitol | Citit | Exerciții făcute | Rulează | Pot explica |
|---|---|---|---|---|
| 01 Setup | ☐ | ☐ | ☐ | ☐ |
| 02 Model | ☐ | ☐ | ☐ | ☐ |
| 03 Layout Main | ☐ | ☐ | ☐ | ☐ |
| 04 MainActivity | ☐ | ☐ | ☐ | ☐ |
| 05 Formular 1 | ☐ | ☐ | ☐ | ☐ |
| 06 Formular 2 | ☐ | ☐ | ☐ | ☐ |
| 07 ItemActivity | ☐ | ☐ | ☐ | ☐ |
| 08 Navigare | ☐ | ☐ | ☐ | ☐ |
| 09 Editare | ☐ | ☐ | ☐ | ☐ |
| 10 Reconstruire | ☐ | ☐ | ☐ | ☐ |
| 11 Extensii | ☐ | ☐ | ☐ | ☐ |

---

## Structura folderului

```
Exams and tests/test 1/
  README.md                          ← acest fișier
  01 ... 11                          ← capitolele
  cod-final/                         ← codul exact la commitul d719ffc
    AndroidManifest.xml
    build.gradle.kts                 ← build.gradle.kts al modulului G1097
    build-root.gradle.kts            ← build.gradle.kts de la rădăcină
    settings.gradle.kts
    gradle.properties
    gradle/libs.versions.toml
    java/ro/ase/ie/g1097/model/Movie.java
    java/ro/ase/ie/g1097/activities/MainActivity.java
    java/ro/ase/ie/g1097/activities/ItemActivity.java
    res/layout/activity_main.xml
    res/layout/activity_item.xml
    res/layout/movie_item.xml
    res/values/strings.xml
    res/values/colors.xml
    res/values/themes.xml
    res/values-night/themes.xml
    res/drawable/outline_add_24.xml
    HASH-URI.txt
  _progres/                          ← aici lucrezi tu (vezi mai jos)
```

---

## Versiunea Word (recomandată pentru citit)

**`Test 1 - G1097 Movies.docx`** — tot materialul într-un singur document, **128 pagini**.

| | |
|---|---|
| Pagină | A4, margini **1,5 cm** pe toate laturile |
| Font corp | Segoe UI 10,5 pt, spațiere 1,1 |
| Font cod | Consolas 8,5 pt, cu **syntax highlighting** (temă tango) |
| Cuprins | generat automat, 124 titluri pe 3 niveluri |
| Footer | număr pagină + total, pe fiecare pagină |
| Formatare | titluri colorate pe niveluri (albastru → verde → violet), carduri de cod cu contur, tabele cu antet albastru și rânduri alternate, citate cu bară galbenă |

> **Atenție:** în Word, blocurile `<details>` (Indiciu / Soluție) **nu se pot plia** — sunt transformate în secțiuni vizibile, cu titluri de nivel 5. Deci vezi soluția imediat sub exercițiu. Dacă vrei să lucrezi fără să vezi răspunsul, folosește fișierele `.md` (care se pliază în orice vizualizator Markdown) sau acoperă partea de jos a paginii.

---

## Unde lucrezi

**Nu** lucra în `cod-final/` și **nu** lucra în `Android dev/dma2026/` (clone-ul tău de lucru).
Creează-ți proiectul în `Exams and tests/test 1/_progres/` (folderul există, e gol) sau oriunde vrei tu, dar nu în cele două de mai sus.

Numele proiectului la creare: **`Movies1097`** (sau `G1097` — cum vrei; namespace-ul îl lași `ro.ase.ie.g1097`).

---

## Ce NU e în acest material

- **Nu** conține codul grupelor 1096/1098/1099. Aplicația e aceeași la toate; 1097 are varianta cea mai recentă. Ne bazăm strict pe 1097.
- **Nu** conține `DMA02`, `DMA03`, `DMA05`, `DMA06` (proiectele de curs).
- **Nu** conține `MovieAdapter.java` din `cod-final/`, pentru că **nu e în repo** la `d719ffc`. Adapterul există doar ca modificare locală necommisă în folderul vechi de sync. Îl construiești în capitolul 11, ca extensie — exact ca la laboratorul următor.

---

## Note despre versiuni (citite din repo, nu din memorie)

| | |
|---|---|
| AGP | `9.4.1` |
| `compileSdk` | `37` (sintaxă nouă: `compileSdk { version = release(37) }`) |
| `minSdk` | `33` |
| `targetSdk` | `37` |
| Java | `VERSION_11` (source + target) |
| Material | `1.14.0` |
| AppCompat | `1.8.0` |
| activity-ktx | `1.13.0` |
| viewBinding | `true` (activat, dar nefolosit în cod — vezi cap. 07) |

Dacă Android Studio îți propune versiuni mai noi la crearea proiectului, **acceptă-le** — nu e o problemă. Ce contează e să înțelegi structura, nu numerele.
