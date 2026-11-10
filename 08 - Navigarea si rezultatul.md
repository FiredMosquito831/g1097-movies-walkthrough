# Capitolul 08 — Navigarea și rezultatul

**Obiectiv:** FAB-ul deschide `ItemActivity`; `ItemActivity` trimite înapoi un `Movie`; `MainActivity` îl adaugă în listă și redesenează.

**Timp estimat:** 30–45 min.

**Fișiere modificate:** `MainActivity.java` (se adaugă `launcher` + `initListeners` complet)

---

## Pasul 8.1 — De ce nu `startActivity` simplu

### De ce

Ai putea face:

```java
Intent intent = new Intent(this, ItemActivity.class);
startActivity(intent);
```

Funcționează — dar **nu primești nimic înapoi**. `ItemActivity` s-ar închide, iar tu nu ai afla ce a salvat utilizatorul.

Ai nevoie de o **comunicare bidirecțională**:

```
MainActivity --Intent--> ItemActivity
MainActivity <--Intent-- ItemActivity   (rezultat)
```

### Cum se face

| Metodă | Stare | Recomandat? |
|---|---|---|
| `startActivityForResult(intent, REQUEST_CODE)` | **depreciat** din API 30 | nu |
| `registerForActivityResult(...)` | actual | **da** |

Repo-ul folosește varianta modernă.

---

## Pasul 8.2 — `registerForActivityResult`

### De ce

`registerForActivityResult` înregistrează un **callback** care va fi apelat când activitatea copil se închide cu un rezultat. Trebuie apelat **înainte** ca activitatea să fie pornită (ideal în `onCreate`).

### Cum

```java
private ActivityResultLauncher<Intent> launcher;

// în onCreate, după initListeners():
launcher = registerForActivityResult(
        new ActivityResultContracts.StartActivityForResult(),
        new ActivityResultCallback<ActivityResult>() {
            @Override
            public void onActivityResult(ActivityResult result) {
                if (result.getResultCode() == RESULT_OK) {
                    Intent data = result.getData();
                    Movie movie = (Movie) data.getSerializableExtra(MOVIE_EXTRA);
                    int position = data.getIntExtra(POSITION_EXTRA, -1);
                    if (position == -1) {
                        movies.add(movie);
                    } else {
                        movies.set(position, movie);
                    }
                    movieAdapter.notifyDataSetChanged();
                }
            }
        });
```

### Cele două argumente

| Argument | Ce e |
|---|---|
| `new ActivityResultContracts.StartActivityForResult()` | **contractul**: definește tipul de input (`Intent`) și output (`ActivityResult`) |
| `new ActivityResultCallback<ActivityResult>() { ... }` | **callback-ul**: ce faci cu rezultatul |

### De ce `ActivityResult` și nu `Intent`

`ActivityResult` conține **trei** lucruri:

| Metodă | Ce întoarce |
|---|---|
| `getResultCode()` | `RESULT_OK` sau `RESULT_CANCELED` |
| `getData()` | `Intent`-ul cu date (poate fi `null`) |
| `getResultCode()` | codul de rezultat |

Dacă ai primi direct `Intent`, ai pierde `resultCode` — și n-ai ști dacă utilizatorul a salvat sau a apăsat Back.

### Exercițiu 8.2

**Cerință:** ce se întâmplă dacă uiți `if (result.getResultCode() == RESULT_OK)`?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am eliminat verificarea `resultCode`.

**Ce se întâmplă:** când utilizatorul apasă **Back** (fără să salveze), `ItemActivity` se închide cu `RESULT_CANCELED` și `getData()` = `null`. Codul tău ar face:

```java
Movie movie = (Movie) data.getSerializableExtra(MOVIE_EXTRA);  // NPE: data e null
```

→ **crash**.

**De ce:** `getData()` e `null` când nu s-a setat niciun rezultat. `resultCode` e singurul mod de a distinge „a salvat” de „a renunțat”.

**De reținut:**
1. `RESULT_OK` = activitatea a setat un rezultat cu `setResult(RESULT_OK, intent)`.
2. `RESULT_CANCELED` = orice altceva (Back, închidere forțată, `finish()` fără `setResult`).
3. **Întotdeauna** verifică `resultCode` înainte de `getData()`.

**Unde revine:** în cap. 09, când editezi un film și apeși Back, `MainActivity` **nu** trebuie să modifice nimic. Verificarea `RESULT_OK` e ce garantează asta.

</details>

---

## Pasul 8.3 — Constantele pentru extra

### De ce

Cheile din `Intent` sunt **string-uri**. Dacă scrii `"movie"` într-un loc și `"Movie"` în altul, primești `null` fără nicio eroare.

### Cum

```java
protected static final String POSITION_EXTRA = "position";
protected static final String MOVIE_EXTRA = "movie";
```

### De ce `protected static final`

| Modificator | De ce |
|---|---|
| `protected` | accesibil din `ItemActivity` (subclasă? nu — dar în **același pachet** `activities`, deci `protected` e suficient) |
| `static` | aparține clasei, nu instanței |
| `final` | nu se schimbă niciodată |

> **Atenție:** `protected` în Java înseamnă „accesibil din subclase **și** din același pachet”. `ItemActivity` e în `ro.ase.ie.g1097.activities`, la fel ca `MainActivity` — deci merge. Dacă ar fi în alt pachet, `protected` nu ar fi suficient (ar trebui `public`).

### Exercițiu 8.3

**Cerință:** mută `ItemActivity` în pachetul `ro.ase.ie.g1097` (nu `activities`). Ce se întâmplă cu `MainActivity.MOVIE_EXTRA`?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am mutat clasa în alt pachet.

**Ce se întâmplă:** **eroare de compilare**:

```
error: MOVIE_EXTRA has protected access in MainActivity
```

**De ce:** `protected` permite accesul din subclase și din **același pachet**. `ItemActivity` nu e subclasă a `MainActivity` și nu mai e în același pachet → nu are acces.

**De reținut:**
1. Ierarhia de acces: `private` < `package-private` (fără modificator) < `protected` < `public`.
2. `protected` e **mai larg** decât package-private doar prin subclase, nu prin pachete.
3. Dacă vrei acces din orice pachet, folosești `public`.

**Unde revine:** nu revine, dar e o întrebare clasică de test despre modificatori de acces.

</details>

---

## Pasul 8.4 — `initListeners` complet

### De ce

Acum ai `launcher`, deci poți lega FAB-ul și click-ul pe listă.

### Cum

```java
private void initListeners() {
    fabInsert.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            launcher.launch(intent);
        }
    });

    listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
        @Override
        public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            intent.putExtra(MOVIE_EXTRA, movies.get(position));
            intent.putExtra(POSITION_EXTRA, position);
            launcher.launch(intent);
        }
    });
}
```

### `MainActivity.this` vs `this`

În interiorul clasei anonime `new View.OnClickListener() { ... }`, `this` se referă la **clasa anonimă**, nu la `MainActivity`. Deci `new Intent(this, ...)` ar da eroare (tipul `View.OnClickListener` nu e `Context`).

Soluția: `MainActivity.this` — referință explicită la instanța exterioară.

> **De reținut:** în lambda, `this` se referă la clasa **exterioară**. Deci `new Intent(this, ItemActivity.class)` ar merge într-o lambda, dar nu într-o clasă anonimă. E o diferență importantă.

### `launcher.launch(intent)` vs `startActivity(intent)`

`launcher.launch(intent)`:
1. pornește activitatea,
2. garantează că `onActivityResult` va fi apelat la închidere.

`startActivity(intent)`:
1. pornește activitatea,
2. **nu** primești nimic înapoi.

### Exercițiu 8.4

**Cerință:** rescrie ambii listeneri cu lambda. Ce se întâmplă cu `MainActivity.this`?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit clasele anonime cu lambda.

```java
private void initListeners() {
    fabInsert.setOnClickListener(v -> {
        Intent intent = new Intent(this, ItemActivity.class);
        launcher.launch(intent);
    });

    listView.setOnItemClickListener((parent, view, position, id) -> {
        Intent intent = new Intent(this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    });
}
```

**Ce se întâmplă cu `MainActivity.this`:** **nu mai e nevoie.** Într-o lambda, `this` se referă la instanța **exterioară** (`MainActivity`). Deci `new Intent(this, ...)` merge direct.

**De ce:** lambda nu creează o clasă anonimă „reală” cu propriul `this` — e o funcție care captează contextul. `this` rămâne cel al clasei care o definește.

**De reținut:**
1. **Clasă anonimă**: `this` = clasa anonimă → ai nevoie de `MainActivity.this`.
2. **Lambda**: `this` = clasa exterioară → `this` e suficient.
3. `OnItemClickListener` are **patru** parametri, dar e tot funcțională (o singură metodă `onItemClick`). Lambda merge.

**Unde revine:** în cap. 11, `MovieAdapter` folosește lambda pentru `setOnClickListener` — acolo `this` e `MovieViewHolder`, iar `MainActivity` nu e accesibilă direct. De aceea se folosește un **callback** (`OnItemClickListener` definit în adapter).

</details>

---

## Pasul 8.5 — Fluxul complet, urmărit

### Cum

1. Utilizatorul apasă FAB.
2. `fabInsert.setOnClickListener` → `launcher.launch(intent)`.
3. `ItemActivity.onCreate` → `initControls`, `initListeners`.
4. Utilizatorul completează formularul, apasă Save.
5. `saveMovie()` → `setResult(RESULT_OK, intent)` → `finish()`.
6. `ItemActivity` se închide.
7. `MainActivity.onActivityResult` e apelat cu `ActivityResult`.
8. `resultCode == RESULT_OK` → extrage `Movie` și `position`.
9. `position == -1` → `movies.add(movie)`.
10. `movieAdapter.notifyDataSetChanged()` → `ListView` redesenează.
11. Filmul apare în listă.

### Diagrama

```
MainActivity                    ItemActivity
    |                                |
    |-- launcher.launch(intent) ---->|
    |                                | onCreate
    |                                | initControls
    |                                | initListeners
    |                                | (utilizator completează)
    |                                | saveMovie()
    |                                | setResult(RESULT_OK, intent)
    |                                | finish()
    |<---- onActivityResult ---------|
    |  resultCode = RESULT_OK        |
    |  data = intent cu Movie        |
    |                                |
    | movies.add(movie)              |
    | notifyDataSetChanged()         |
    | ListView redesenează           |
```

### Exercițiu 8.5

**Cerință:** adaugă un `Toast` în `onActivityResult` care afișează titlul filmului primit. Rulează, salvează un film, vezi toast-ul.

<details>
<summary>Indiciu</summary>

`Toast.makeText(context, text, Toast.LENGTH_SHORT).show();`

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un `Toast` după extragerea filmului.

```java
if (result.getResultCode() == RESULT_OK) {
    Intent data = result.getData();
    Movie movie = (Movie) data.getSerializableExtra(MOVIE_EXTRA);
    int position = data.getIntExtra(POSITION_EXTRA, -1);
    Toast.makeText(this, "Saved: " + movie.getTitle(), Toast.LENGTH_SHORT).show();
    // ... restul
}
```

**Ce se vede:** la salvare, apare un toast jos cu „Saved: Interstellar”.

**De ce merge:** `Toast` e un mesaj non-blocant, afișat 2 secunde. Nu oprește execuția.

**De reținut:**
1. `Toast.makeText(context, text, duration)` — `context` e `this` (MainActivity).
2. `LENGTH_SHORT` = 2s, `LENGTH_LONG` = 3.5s.
3. `show()` e obligatoriu — fără el, toast-ul nu apare.
4. `Toast` e util pentru debugging rapid, dar **nu** înlocuiește `Log.d`.

**Unde revine:** nu revine, dar e o unealtă de debugging pe care o vei folosi des.

</details>

---

## Pasul 8.6 — `getSerializableExtra` vs `IntentCompat`

### De ce

Repo-ul folosește două variante diferite:

- `MainActivity`: `(Movie) intent.getSerializableExtra(MOVIE_EXTRA)`
- `ItemActivity`: `IntentCompat.getSerializableExtra(intent, MOVIE_EXTRA, Movie.class)`

### De ce diferă

`getSerializableExtra(String)` e **depreciat** în API 33+. `IntentCompat` e varianta modernă, care cere tipul clasei.

Repo-ul a actualizat doar `ItemActivity`, nu și `MainActivity`. E o inconsecvență — ambele funcționează, dar cea din `MainActivity` dă un warning de compilare.

> **De reținut:** dacă vezi un warning galben pe `getSerializableExtra`, nu e o eroare. Codul merge. Dar varianta modernă e `IntentCompat`.

### Exercițiu 8.6

**Cerință:** actualizează `MainActivity` să folosească `IntentCompat.getSerializableExtra(data, MOVIE_EXTRA, Movie.class)`. Verifică că merge.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit linia din `onActivityResult`.

```java
import androidx.core.content.IntentCompat;
// ...
Movie movie = IntentCompat.getSerializableExtra(data, MOVIE_EXTRA, Movie.class);
```

**De ce merge:** `IntentCompat` e o clasă de compatibilitate care apelează metoda corectă în funcție de versiunea Android.

**De reținut:**
1. `IntentCompat.getSerializableExtra` **nu** întoarce `Serializable`, ci direct `Movie` — fără cast.
2. Dacă tipul nu se potrivește, întoarce `null` (sau aruncă, depinde de versiune).
3. E varianta recomandată pentru cod nou.

**Unde revine:** nu revine.

</details>

---

## Pasul 8.7 — Ordinea de inițializare (capcana repo-ului)

### De ce

În `onCreate` din repo:

```java
initControls();
initListeners();     // ← înregistrează listeneri care folosesc `launcher`
launcher = registerForActivityResult(...);   // ← launcher inițializat DUPĂ
```

### De ce merge totuși

Pentru că `initListeners` **nu apelează** `launcher.launch(...)` imediat. Doar **înregistrează** un listener care, **la click**, va apela `launcher.launch(...)`.

La momentul click-ului, `launcher` e deja inițializat. Deci merge.

### Când ar crăpa

Dacă ai apela `fabInsert.performClick()` imediat după `initListeners()`:

```
NullPointerException: Attempt to invoke virtual method
'void ActivityResultLauncher.launch(Object)' on a null object reference
```

### Exercițiu 8.7

**Cerință:** adaugă `fabInsert.performClick();` imediat după `initListeners();`. Rulează. Ce se întâmplă?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am forțat un click programatic înainte ca `launcher` să fie inițializat.

**Ce se întâmplă:** **crash** cu NPE:

```
java.lang.NullPointerException: Attempt to invoke virtual method
'void androidx.activity.result.ActivityResultLauncher.launch(java.lang.Object)'
on a null object reference
    at ro.ase.ie.g1097.activities.MainActivity$1.onClick(MainActivity.java:...)
```

**De ce:** `performClick()` execută listener-ul **imediat**. În acel moment, `launcher` e încă `null` (linia de inițializare nu s-a executat).

**De reținut:**
1. **Ordinea de inițializare** contează când codul se execută **imediat**.
2. **Nu contează** când codul se execută **amânat** (la click, la un callback).
3. Cel mai sigur: inițializezi `launcher` **înainte** de `initListeners()`. Repo-ul nu o face, dar funcționează din întâmplare.

**Recomandare:** mută `launcher = registerForActivityResult(...)` **înainte** de `initListeners()`. E o îmbunătățire sigură.

</details>

---

## Pasul 8.8 — Verificare completă

### Cum

1. Rulează.
2. Vezi 3 filme în listă.
3. Apasă FAB → se deschide formularul gol.
4. Completează: titlu „Dune”, gen „Sci-Fi”, dată 22/10/2021, buget 165000000, durată 155, rating 4, switch ON, watchlist OFF, ghidaj „PG-13”, poster gol.
5. Apasă Save.
6. **Verifică:** lista are acum 4 filme, ultimul e Dune.

### Ce verifici

- [ ] FAB deschide formularul
- [ ] Save adaugă filmul în listă
- [ ] Back (fără Save) **nu** adaugă nimic
- [ ] `notifyDataSetChanged()` e apelat (filmul apare imediat)
- [ ] `resultCode` verificat înainte de `getData()`

---

## Pasul 8.9 — Întrebări de test

1. De ce `launcher.launch()` și nu `startActivity()`?
2. Ce conține `ActivityResult`?
3. De ce `MainActivity.this` în clasa anonimă, dar `this` în lambda?
4. Ce se întâmplă dacă uiți `setResult(RESULT_OK, intent)` în `saveMovie`?
5. De ce `notifyDataSetChanged()` după `movies.add()`?

<details>
<summary>Răspunsuri — explicativ</summary>

**1. De ce `launcher.launch()`?**
`startActivity()` pornește activitatea fără a aștepta un rezultat. `launcher.launch()` pornește activitatea **și** înregistrează callback-ul care va fi apelat la închidere.

**2. Ce conține `ActivityResult`?**
`getResultCode()` (`RESULT_OK` / `RESULT_CANCELED`) și `getData()` (`Intent`-ul cu extra-uri, poate fi `null`).

**3. `MainActivity.this` vs `this`?**
În clasa anonimă, `this` = instanța clasei anonime (care nu e `Context`). În lambda, `this` = instanța clasei exterioare (`MainActivity`, care e `Context`).

**4. Ce se întâmplă dacă uiți `setResult`?**
`ItemActivity` se închide cu `RESULT_CANCELED` (implicit). `MainActivity` vede `resultCode != RESULT_OK` și **nu face nimic**. Filmul se pierde fără nicio eroare.

**5. De ce `notifyDataSetChanged()`?**
`ArrayAdapter` nu observă modificările listei. Fără notificare, `ListView` rămâne cu view-urile vechi.

</details>

---

## Rezumat capitol 08

- `registerForActivityResult` + `launcher.launch()` = comunicare bidirecțională.
- `ActivityResult` conține `resultCode` + `data`; verifici întotdeauna `resultCode`.
- Constante `static final` pentru cheile din `Intent`.
- `MainActivity.this` în clase anonime, `this` în lambda.
- `notifyDataSetChanged()` obligatoriu după modificarea listei.

**Următorul capitol:** [09 - Modul de editare.md](09%20-%20Modul%20de%20editare.md)
