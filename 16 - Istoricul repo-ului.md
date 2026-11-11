# Capitolul 16 — Istoricul complet al repo-ului

**Obiectiv:** să vezi cum a evoluat repo-ul `dma2026` de la primul commit până la `d719ffc` — 44 de commituri, 9 proiecte, 13 octombrie → 9 noiembrie 2026.

**Timp estimat:** 25–35 min (citire).

**Sursa:** `git log` pe `mihaidoinea/dma2026`, branch `main`, HEAD `d719ffc`.

> **De ce e util:** la test, întrebări de tipul „ce s-a adăugat în S05?" sau „de ce codul arată așa?" se răspund din istoric. Și vezi cum lucrează un profesor care își construiește materialul incremental.

---

## Pasul 16.1 — Privirea de ansamblu

### Cifrele

| | |
|---|---|
| Commituri | **44** |
| Prima dată | **13 octombrie 2026** — `8b04238` „DMA02" |
| Ultima dată | **9 noiembrie 2026** — `d719ffc` „G1097_S07" |
| Proiecte | 9 (DMA02, DMA03, DMA05, DMA06, G1096, G1097, G1098, G1099) |
| Zile cu commituri | 13, 19, 21, 22, 26, 27, 29 oct · 2, 3, 4, 9 nov |
| Merge-uri | 3 (`e2ba1f5`, `9dc5ebc` + primul) |

### Structura pe perioade

| Perioadă | Ce s-a întâmplat |
|---|---|
| **13 oct** | primul commit: `DMA02` — demonstrația de ciclu de viață |
| **19–22 oct** | `DMA03` (navigare) + **S04 la toate cele 4 grupe** |
| **26–29 oct** | **restructurare majoră** + **S05 la toate grupele** |
| **2–4 nov** | **S06 la toate grupele** + `DMA06` (ListView/RecyclerView) |
| **9 nov** | `G1097_S07` — doar `movie_item.xml` |

---

## Pasul 16.2 — Cronologia completă

### 13 octombrie

| Commit | Ce |
|---|---|
| `8b04238` | **DMA02** — primul commit din repo. Clasa `Application` + ciclul de viață |

### 19 octombrie

| Commit | Ce |
|---|---|
| `a08f665` | **G1097_S04** — primul commit al grupei tale. Schelet Gradle + `MainActivity` (24 linii) + `activity_main.xml` (19 linii) |

### 21 octombrie — ziua cea mai aglomerată (13 commituri)

| Commit | Ce |
|---|---|
| `063ceed`, `ba82276`, `42baa90`, `858f7ea` | **DMA03** — navigare, meniuri, dialoguri (4 commituri) |
| `f8f653b` | **G1097_S04** — apare `ItemActivity` (43 linii), `activity_item.xml` (10 linii), `strings.xml` (22 linii). **Aici se naște ListView-ul** |
| `1993e6c` | **G1097_S04** — `gradle-daemon-jvm.properties` (12 linii, configurare) |
| `695bb34`, `a7610f3`, `902e1a0` | **G1098_S04** (3 commituri) |
| `7a5b342`, `680f602` | **G1096_S04** (2 commituri) |
| `919b765`, `11eb644` | **G1099_S04** (2 commituri) |
| `7d43292` | „Add course information to README" — README-ul repo-ului |

**Ce s-a întâmplat practic:** într-o singură zi, profesorul a pus scheletul pentru toate cele 4 grupe și a terminat DMA03. Fiecare grupă a primit 2–3 commituri separate — de aici numărul mare.

### 22 octombrie

| Commit | Ce |
|---|---|
| `b7633cd` | **DMA03** — ultimul commit al proiectului |
| `e2ba1f5` | **Merge** remote-tracking branch 'origin/main' |

### 26 octombrie — restructurarea

| Commit | Ce |
|---|---|
| `51863a3` | **„Project restructured"** — cel mai important commit structural |
| `2e4e176` | **G1097_S05** — pachete `activities/` + `model/`, apare `Movie.java` (14 linii), `outline_add_24.xml`, `activity_item.xml` **+115 linii** |
| `8a91c82` | **G1097_S05** — `ItemActivity` **+62 linii** (logica formularului) |

### Ce a făcut „Project restructured"

Commit-ul mută structura de la **modul per grupă** (`G1097/app/src/main/...`) la **modul la nivel de proiect**:

```
ÎNAINTE                          DUPĂ
G1097/                           G1097/
├── app/                         ├── src/main/         ← src-ul urcă
│   ├── build.gradle.kts         ├── build.gradle.kts
│   ├── src/main/                └── gradle/
│   └── gradle/                      
├── gradlew                      (wrapper-ul dispare)
├── gradlew.bat
└── settings.gradle.kts
```

Consecințe:
- `gradlew`, `gradlew.bat`, wrapper-ul Gradle **dispar** din fiecare modul
- `libs.versions.toml` se mută la nivel de rădăcină
- `settings.gradle.kts` rămâne doar la rădăcină

> **De reținut:** înainte de 26 oct, fiecare grupă era un proiect independent. După, toate sunt module ale unui singur proiect. De aceea `build.gradle.kts` din `G1097` la `d719ffc` are doar `plugins { alias(libs.plugins.android.application) }` — versiunile vin din catalogul de la rădăcină.

### 27 octombrie — S05 la toate grupele

| Commit | Ce |
|---|---|
| `a1c6b74`, `e65cc20` | **G1096_S05** |
| `f7c12dc` | **G1097_S05** — rescriere `ItemActivity`, `Movie` +37 linii, `activity_item` +29, `strings` +12 |
| `8fbcf29` | **G1097_S05** — o singură linie modificată (fix) |
| `71da3c8` | **G1098_S05** |
| `de8a681`, `be7f6b8` | **G1099_S05** |

### 29 octombrie

| Commit | Ce |
|---|---|
| `4a60b5d` | **G1098_S05** — ultimul S05, cu 2 zile întârziere față de celelalte grupe |

### 2 noiembrie

| Commit | Ce |
|---|---|
| `2efafdb` | **G1097_S06** — `activity_item.xml` **+306 linii** (formularul mare), `MainActivity` +52, `Movie` +19. **Cel mai mare commit din istoricul G1097** |

### 3 noiembrie

| Commit | Ce |
|---|---|
| `99740e7` | **G1096_S06** |
| `c14a1f2` | **G1099_S06** |
| `2a1ae9a` | **G1099** — „Add fields and methods for movie details management" (`ItemActivity` +85) |
| `02499dc` | **G1099** — „Add getters and setters for Movie class attributes" (`Movie` +80) |
| `8c878b6` | **G1099** — „Initialize movie adapter and add sample movies" (`MainActivity` +12) |

**Observație:** cele trei commituri descriptive ating **G1099**, nu G1098. Și sunt scrise în alt stil: propoziții în engleză („Add getters and setters…") în loc de `G1099_S06`.

> **De ce e interesant:** sugerează că o parte din codul G1099 a fost pus de altcineva (probabil un student care a contribuit la repo, sau profesorul lucrând în alt stil). Restul istoricului e uniform: `G<grupa>_S<sesiune>`.

### 4 noiembrie — ziua cea mai mare după 21 oct

| Commit | Ce |
|---|---|
| `43e4c85`, `e58023a` | **G1098_S06** (două commituri cu același mesaj) |
| `9dc5ebc` | **Merge** remote-tracking branch 'origin/main' |
| `4e6b729`, `2d891ef` | **DMA06** — proiectul cu ListView/RecyclerView |
| `2c4fc99` | **G1096_S06** |
| `f7fb315` | **G1097_S06** — `ItemActivity` **+125 linii** (validare, date picker), `Movie` **+83**, `build.gradle.kts` +2 |
| `e58023a` → `44139d7` | **G1099_S06** |

### 9 noiembrie

| Commit | Ce |
|---|---|
| `d719ffc` | **G1097_S07** — **doar `movie_item.xml`, +136 linii.** Niciun cod Java |

---

## Pasul 16.3 — Evoluția lui `G1097`, sesiune cu sesiune

### Tabelul care trebuie știut

| Sesiune | Data | Ce s-a adăugat | Linii de cod Java |
|---|---|---|---|
| **S04** | 19 + 21 oct | schelet, `MainActivity`, `ItemActivity`, `activity_item` minimal, `strings` | ~90 |
| **S05** | 26–27 oct | pachete `activities`/`model`, `Movie`, FAB, formularul mijlociu | ~250 |
| **S06** | 2 + 4 nov | formularul mare (`+306` linii XML), validare, date picker | ~300 |
| **S07** | 9 nov | **doar layout-ul cardului** pentru viitorul `RecyclerView` | **0** |

### Ce înseamnă concret

**S04** — aplicația are două ecrane goale care se pot deschide. Butoanele nu fac nimic util.

**S05** — apare modelul `Movie`. Formularul are câmpuri. Lista afișează ceva.

**S06** — formularul e complet: toate cele 10 câmpuri, `DatePickerDialog`, validare, `SeekBar` cu valoare live.

**S07** — profesorul pregătește **următorul laborator**: pune `movie_item.xml`, cardul frumos cu poster, titlu, stele, chip-uri. Dar nu scrie adapterul.

### Dovada că S07 e pregătire, nu livrare

```bash
git show --stat d719ffc
# G1097/src/main/res/layout/movie_item.xml | 136 +++++++++++++++++++
# 1 file changed, 136 insertions(+)

git grep "movie_item" HEAD
# (gol)
```

Fișierul e comis, dar **niciun cod nu îl referă**. Nu există `MovieAdapter`, nu există `setAdapter` cu el, nu există `tools:listitem`.

> **Concluzie:** la `d719ffc`, aplicația G1097 e **funcțională pe `ListView`** și are un layout de card **pregătit dar nelegat**. Trecerea pe `RecyclerView` e tema laboratorului următor — pe care ai făcut-o local în 09.11.

---

## Pasul 16.4 — Comparația între grupe

### Ce diferă

| Grupa | Commituri | Ultimul commit | Are S07? | Are `movie_item.xml`? |
|---|---|---|---|---|
| **G1096** | 6 | `2c4fc99` 4 nov (S06) | nu | nu |
| **G1097** | 11 | `d719ffc` 9 nov (S07) | **da** | **da** |
| **G1098** | 8 | `e58023a` 4 nov (S06) | nu | nu |
| **G1099** | 8 | `44139d7` 4 nov (S06) | nu | nu |

### Ce e identic

La `d719ffc`, **toate patru** au:

```java
import android.widget.ArrayAdapter;
import android.widget.ListView;

private ListView listView;
private ArrayAdapter<Movie> movieAdapter;
movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

Aplicația e aceeași. Diferă doar:
- **G1097** are `movie_item.xml` în plus (pregătirea pentru RecyclerView)
- **G1099** are 3 commituri scrise în alt stil (03.11)

### De ce G1097 e „cea mai recentă variantă"

Pentru că are **11 commituri** față de 6–8, și pentru că e **singura cu S07**. Când utilizatorul a spus „strict pe grupa 1097", asta a fost criteriul.

---

## Pasul 16.5 — Ce poți afla din istoric

### Trei întrebări de test

**„În ce sesiune a apărut `Movie.java`?"**
S05, commitul `2e4e176` (26 oct). Are 14 linii — doar câmpurile.

**„Când s-a adăugat `DatePickerDialog`?"**
S06, commitul `f7fb315` (4 nov), `ItemActivity` +125 linii. (`2efafdb` din 2 nov e formularul XML.)

**„De ce `activity_item.xml` are 451 de linii?"**
Pentru că s-a construit în trei valuri: 10 linii în S04, +115 în S05, +306 în S06.

### Comanda care îți dă tot

```bash
git log --reverse --format='%h %ad %s' --date=short -- G1097
```

Și pentru un commit anume:

```bash
git show --stat f7fb315     # ce fișiere a atins
git show f7fb315 -- G1097/src/main/java/ro/ase/ie/g1097/model/Movie.java   # diff-ul exact
```

---

## Pasul 16.6 — Lecțiile de proces

### Cum lucrează profesorul

1. **Commituri mici și dese.** 13 commituri într-o zi. Fiecare grupă primește ce trebuie, separat.
2. **Mesaje uniforme:** `G<grupa>_S<sesiune>`. Poți reconstrui totul din `git log`.
3. **Un commit per grupă per sesiune.** Dacă s-ar fi făcut un singur commit „S06 toate grupele", istoricul ar fi fost ilegibil.
4. **Restructurări rare dar mari.** `51863a3` a atins tot repo-ul. Un commit, o schimbare arhitecturală.
5. **Pregătește următorul laborator în avans.** `movie_item.xml` e comis cu o săptămână înainte de a fi folosit.

### Ce înveți pentru propriul tău cod

- Un commit = o schimbare cu sens propriu. Nu amesteca „adaug formular" cu „mut foldere".
- Mesajele trebuie să spună **ce**, nu „update" sau „fix".
- Când restructurezi, fă-o într-un commit separat, ca să poți reveni.
- Dacă adaugi ceva ce nu e încă folosit, spune-o în mesaj („prepare layout for RecyclerView").

---

## Rezumat capitol 16

- **44 de commituri**, 13 oct → 9 nov, 9 proiecte.
- **21 oct** = ziua cu cele mai multe commituri (13) — scheletul tuturor grupelor + DMA03.
- **26 oct** = „Project restructured" — de la module independente la module ale unui proiect.
- **G1097**: S04 (90 linii) → S05 (250) → S06 (300) → **S07 (0 linii de Java)**.
- **S07** = doar `movie_item.xml`, nelegat de nimic. Pregătire pentru laboratorul următor.
- Toate grupele au `ListView` la `d719ffc`. RecyclerView nu e în repo — doar în `DMA06` (ca demonstrație) și în lucrul tău local.
- G1099 are 3 commituri în alt stil (03.11) — posibil contribuție externă.

**Sfârșitul părții a doua.** Înapoi la [prezentarea generală](index.html).
