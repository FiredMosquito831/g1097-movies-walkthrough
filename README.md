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

### Versiunea 2 — codul de la 14.11.2026

Versiunea **actualizată** a aplicației: `RecyclerView`, adaptor propriu cu `ViewHolder`, callback de click prin interfață `IMovieListener` și un ecran nou. Ea înlocuiește varianta veche la examen.

| # | Fișier | Ce conține | Bife |
|---|---|---|---|
| 38 | [38 - Codul nou adnotat.md](38%20-%20Codul%20nou%20adnotat.md) | Cele 8 fișiere noi sau modificate, adnotate linie cu linie: `MainActivity`, `MovieAdapter`, `IMovieListener`, `PlaceCiocanul`, `movie_item.xml`, `activity_main.xml`, `activity_place_ciocanul.xml`, manifestul | 1 |
| 39 | [39 - Ce s-a schimbat.md](39%20-%20Ce%20s-a%20schimbat.md) | Ce s-a schimbat față de versiunea veche și de ce: lista, adaptorul, click-ul, ecranul nou, ce a rămas identic, ce mai e șchiop, ce înseamnă pentru examen | 1 |

### Calea 1 — Rescrie de la 0

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

### Anexe — celelalte grupe, proiectele de curs și istoricul repo-ului

| # | Fișier | Ce înveți | Pași |
|---|---|---|---|
| 29 | [29 - Codul G1096 adnotat.md](29%20-%20Codul%20G1096%20adnotat.md) | Codul G1096 bloc cu bloc, plus diferențele față de G1097 (`posterUrl`, importuri moarte, constructorul gol) | 29.1–29.9 |
| 30 | [30 - Codul G1098 adnotat.md](30%20-%20Codul%20G1098%20adnotat.md) | Codul G1098 bloc cu bloc — singura grupă cu `toString()` complet și cu alt drawable la FAB | 30.1–30.9 |
| 31 | [31 - Codul G1099 adnotat.md](31%20-%20Codul%20G1099%20adnotat.md) | Codul G1099 bloc cu bloc, inclusiv importul-mort `android.media.Rating` | 31.1–31.9 |
| 12 | [12 - DMA06 - ListView vs RecyclerView.md](12%20-%20DMA06%20-%20ListView%20vs%20RecyclerView.md) | Cele 3 trepte pe aceleași date: `ArrayAdapter` → `BaseAdapter` → `RecyclerView` | 12.1–12.7 |
| 13 | [13 - DMA05 - ViewBinding.md](13%20-%20DMA05%20-%20ViewBinding.md) | `ViewBinding` vs `findViewById`, toate widget-urile de input | 13.1–13.6 |
| 14 | [14 - DMA03 - Navigare si meniuri.md](14%20-%20DMA03%20-%20Navigare%20si%20meniuri.md) | `DrawerLayout`, `NavigationView`, `PopupMenu`, Back, `AlertDialog`, `Snackbar` | 14.1–14.8 |
| 15 | [15 - DMA02 - Application si ciclu de viata.md](15%20-%20DMA02%20-%20Application%20si%20ciclu%20de%20viata.md) | Ciclul de viață complet, clasa `Application`, `Intent` implicit | 15.1–15.6 |
| 16 | [16 - Istoricul repo-ului.md](16%20-%20Istoricul%20repo-ului.md) | Toate cele 44 de commituri, evoluția pe sesiuni, comparația între grupe | 16.1–16.6 |
| 25 | [25 - Codul DMA02 adnotat.md](25%20-%20Codul%20DMA02%20adnotat.md) | Codul DMA02 bloc cu bloc: `Application`, ciclu de viață, `Intent` implicit | 25.1–25.6 |
| 26 | [26 - Codul DMA03 adnotat.md](26%20-%20Codul%20DMA03%20adnotat.md) | Codul DMA03 bloc cu bloc: drawer, toolbar, meniuri, dialoguri | 26.1–26.8 |
| 27 | [27 - Codul DMA05 adnotat.md](27%20-%20Codul%20DMA05%20adnotat.md) | Codul DMA05 bloc cu bloc: `ViewBinding`, toate widget-urile | 27.1–27.6 |
| 28 | [28 - Codul DMA06 adnotat.md](28%20-%20Codul%20DMA06%20adnotat.md) | Codul DMA06 bloc cu bloc: cele trei trepte de listă | 28.1–28.10 |

> **Partea I** construiește aplicația ta. **Partea II** acoperă restul repo-ului: codul adnotat al celorlalte trei grupe (29–31 — aceeași aplicație, altă variantă, cu diferențele față de 1097 explicate), cele patru proiecte de curs (care conțin exact lucrurile care lipsesc din G1097 — RecyclerView, ViewBinding, meniuri, ciclu de viață) și istoricul complet.

### Calea 2 — Exerciții tip test: 60 de cerințe de examen

Fiecare cerință are: enunț, fișiere atinse, **„Cum abordezi — pașii tăi"** (4–6 acțiuni concrete), **două indicii gradate**, apoi soluția pliabilă cu explicație.

| # | Fișier | Tipul de cerință | Exerciții |
|---|---|---|---|
| 17 | [17 - Bancul 1 - Atribute noi.md](17%20-%20Bancul%201%20-%20Atribute%20noi.md) | Adaugă un atribut (`String`, `Integer`, `boolean`, `float`, `ArrayList`, clasă nouă) | 17.1–17.10 |
| 18 | [18 - Bancul 2 - Bindinguri si adaptoare.md](18%20-%20Bancul%202%20-%20Bindinguri%20si%20adaptoare.md) | Leagă valori, schimbă un widget, fă un adapter | 18.1–18.10 |
| 19 | [19 - Bancul 3 - Valori in UI si persistenta.md](19%20-%20Bancul%203%20-%20Valori%20in%20UI%20si%20persistenta.md) | Valoare → etichetă, widget → model, listă → ecran, rotire | 19.1–19.10 |
| 20 | [20 - Bancul 4 - Controale noi.md](20%20-%20Bancul%204%20-%20Controale%20noi.md) | Adaugă buton, switch, chip, FAB, spinner | 20.1–20.10 |
| 23 | [23 - Bancul 5 - Migrare ListView la RecyclerView.md](23%20-%20Bancul%205%20-%20Migrare%20ListView%20la%20RecyclerView.md) | Migrarea completă, în 10 pași care compilează fiecare | 23.1–23.10 |
| 24 | [24 - Bancul 6 - Persistenta si verificare.md](24%20-%20Bancul%206%20-%20Persistenta%20si%20verificare.md) | Se salvează datele? Verificare, debug, `SharedPreferences` | 24.1–24.10 |

### Calea 3 — Codul explicat + cheatsheet

| # | Fișier | Ce conține |
|---|---|---|
| 21 | [21 - Cheatsheet.md](21%20-%20Cheatsheet.md) | Harta fișierelor, model, ID-uri, ViewBinding, tabelul de listeneri, arborele de decizie pentru adaptoare, intents, ciclu de viață, erori frecvente, rețete pentru examen |
| 22 | [22 - Codul adnotat.md](22%20-%20Codul%20adnotat.md) | Toate cele 6 fișiere G1097 explicate bloc cu bloc, plus fluxul complet |

### Calea 4 — Rețete de examen

Fiecare tip de cerință care poate pica, pe o pagină: pașii exacți, fișierele atinse, codul minim care compilează, de ce merge așa și greșeala care costă puncte. Începe cu planul.

| # | Fișier | Ce conține | Bife |
|---|---|---|---|
| 32 | [32 - Planul ghidat.md](32%20-%20Planul%20ghidat.md) | 10 sesiuni, ~18 h, cu trimiteri exacte la ce citești și ce exersezi din tot site-ul | 10 |
| 33 | [33 - Retete 1 - modelul si interfata.md](33%20-%20Retete%201%20-%20modelul%20si%20interfata.md) | 16 rețete: atribute (String, int, Integer, float, boolean, listă, compus, derivat), schimbare de tip, redenumire, widget-uri, butoane, ecran nou | 16 |
| 34 | [34 - Retete 2 - bindinguri si adaptoare.md](34%20-%20Retete%202%20-%20bindinguri%20si%20adaptoare.md) | 14 rețete: valori legate de etichete, vizibilitate condiționată, validare, `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter`, migrarea completă, grid, antet, click cu callback | 14 |
| 35 | [35 - Retete 3 - Intent si persistenta.md](35%20-%20Retete%203%20-%20Intent%20si%20persistenta.md) | 13 rețete: pornire activitate, extra simple, obiect `Serializable`, rezultat, cod de rezultat, `Intent` implicit, rotire, `SharedPreferences` + JSON, `Application` | 13 |
| 36 | [36 - Bancul 7 - Intent si navigare.md](36%20-%20Bancul%207%20-%20Intent%20si%20navigare.md) | 10 exerciții de tip examen, cu indicii gradate și soluție explicată | 10 |

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
