# Capitolul 02 — Modelul `Movie`

**Obiectiv:** o clasă `ro.ase.ie.g1097.model.Movie` care ține toate datele unui film, e serializabilă (ca să poată călători între activități) și are constructori + getteri/setteri.

**Timp estimat:** 20–30 min.

**Fișier final:** `cod-final/java/ro/ase/ie/g1097/model/Movie.java` (3196 B, SHA-256 `feb7fffc5273fcbf…`)

---

## Pasul 2.1 — De ce un model separat

### De ce

Ai putea să ții datele în `MainActivity`, în 10 variabile separate. De ce nu?

Pentru că un film **călătorește**: din `MainActivity` în `ItemActivity`, înapoi, în listă, eventual în baza de date. Ai nevoie de un **pachet** care să ducă toate câmpurile împreună, într-un singur obiect.

Asta e un **model** (sau POJO — Plain Old Java Object): o clasă fără logică de UI, doar date.

### Regula de aur

> Modelul **nu știe** ce e un `EditText`, un `Spinner` sau un `Intent`. Nu are importuri `android.*`.

Dacă `Movie.java` are `import android.widget.EditText`, ai greșit arhitectura. Modelul e Java curat — poate fi testat fără emulator.

### Cum

Creează pachetul `ro.ase.ie.g1097.model` (click dreapta pe `ro.ase.ie.g1097` → **New → Package**) și în el clasa `Movie`.

---

## Pasul 2.2 — Câmpurile

### De ce fiecare tip

Fiecare câmp corespunde **unui widget** din formular. Tipul nu e ales la întâmplare — e ales ca să se potrivească cu ce poate produce widget-ul.

| Câmp | Tip Java | Widget sursă | De ce tipul ăsta |
|---|---|---|---|
| `title` | `String` | `TextInputEditText` | text liber |
| `release` | `Date` | `TextInputEditText` + `DatePickerDialog` | o **dată**, nu un string; ca să poți face diferențe între date |
| `genre` | `String` | `Spinner` | unul din 10 texte |
| `budget` | `double` | `TextInputEditText` (`numberDecimal`) | bani, cu zecimale |
| `duration` | `int` | `SeekBar` | progresul e `int` între min și max |
| `rating` | `float` | `RatingBar` | `RatingBar.getRating()` întoarce `float` |
| `watched` | `boolean` | `MaterialSwitch` | bifă |
| `approval` | `String` | `RadioGroup` | textul butonului selectat („G”, „PG-13”…) |
| `onWatchlist` | `boolean` | `MaterialCheckBox` | bifă |
| `poster` | `String` | `TextInputEditText` (`textUri`) | un URL |

> **De ce `float` și nu `double` pentru rating?** Pentru că `RatingBar.getRating()` returnează `float`. Dacă ai pune `double`, ar trebui să convertești la fiecare citire. Alegi tipul sursei.

> **De ce `double` și nu `float` pentru budget?** Pentru că banii au nevoie de precizie; `float` pierde cifre la valori mari (160000000 devine 1.6E8 cu erori de rotunjire).

### Cum

```java
package ro.ase.ie.g1097.model;

import java.io.Serializable;
import java.util.Date;

public class Movie implements Serializable {
    private String title;        // EditText
    private Date release;        // EditText date
    private String genre;        // Spinner
    private double budget;       // EditText number
    private int duration;        // SeekBar
    private float rating;        // RatingBar
    private boolean watched;     // Switch
    private String approval;     // RadioGroup | RadioButtons
    private boolean onWatchlist; // Checkbox
    private String poster = null;

    // ... urmează constructorii și getterii
}
```

Observă comentariile din dreapta: professorul a notat **ce widget** produce fiecare câmp. E o documentație excelentă — o păstrezi.

`poster = null` e explicit, deși `String` e oricum `null` implicit. E o formă de documentație: „poate lipsi”.

### De ce `private`

Închidere (encapsulation). Dacă câmpurile ar fi `public`, oricine ar putea scrie `movie.budget = -5`. Cu `private` + setter, poți valida mai târziu fără să schimbi toți callerii.

---

## Pasul 2.3 — `implements Serializable`

### De ce

`Intent.putExtra(String, Serializable)` e **singurul mod simplu** prin care trimiți un obiect întreg între două activități.

`Serializable` e o interfață **marker**: nu are nicio metodă de implementat. E doar o etichetă care spune JVM-ului: „poți transforma obiectul ăsta într-un flux de bytes”.

### Cum funcționează, de fapt

Când apelezi `intent.putExtra("movie", movie)`:

1. Android serializează obiectul (scrie câmpurile într-un `byte[]`).
2. `byte[]` e pus în `Intent` (care e el însuși serializat ca `Parcel`).
3. `Intent` trece granița dintre procese (dacă e nevoie) sau rămâne în memorie.
4. În `ItemActivity`, `getSerializableExtra("movie")` deserializează — **creează un obiect nou**, cu aceleași valori.

> **Capcană majoră:** obiectul primit e o **copie**, nu aceeași referință. Dacă îl modifici în `ItemActivity`, obiectul din `MainActivity` **nu se schimbă**. De asta, la editare, `ItemActivity` trimite înapoi poziția și filmul nou, iar `MainActivity` face `movies.set(position, movie)`.

### Ce trebuie să fie serializabil

Toate câmpurile trebuie să fie serializabile. `String`, `Date`, primitivele — da. Dacă ai avea un câmp de tip `Drawable` sau `Context`, ar crăpa cu `NotSerializableException`.

### Exercițiu 2.3

**Cerință:** ce se întâmplă dacă adaugi în `Movie` un câmp `private java.util.Calendar releaseCalendar;`? Testează mental, apoi verifică.

<details>
<summary>Indiciu</summary>

`Calendar` implementează `Serializable`? Verifică documentația: `java.util.Calendar implements Serializable, Cloneable, Comparable<Calendar>`.

</details>

<details>
<summary>Soluție</summary>

**Ce s-a făcut:** ai adăugat ipotetic un câmp `private java.util.Calendar releaseCalendar;` în `Movie` și te-ai întrebat dacă serializează.

**Răspunsul:** **funcționează** — `java.util.Calendar` implementează `Serializable`, deci nu aruncă `NotSerializableException`.

**De ce e totuși o idee proastă:** ai avea **două surse de adevăr** pentru aceeași informație — `release` (un `Date`) și `releaseCalendar` (un `Calendar`). Ele pot diverge: setezi `release` dar uiți `releaseCalendar`, și ai un film care „s-a lansat în 2010” dar al cărui calendar spune 2011.

**De reținut:**
1. **Serializabilitatea e o condiție necesară, nu suficientă.** Un model bun e și **normalizat** — fiecare informație are o singură reprezentare.
2. Dacă ai nevoie de ambele forme (Date pentru UI, Calendar pentru calcule), convertești la nevoie: `Calendar c = Calendar.getInstance(); c.setTime(release);` — nu stochezi ambele.
3. Câmpurile `transient` **nu** se serializează. Dacă ai un câmp derivat care nu trebuie trimis între activități, îl marchezi `transient`.

**Unde revine:** în capitolul 07 (pasul 7.2), `ItemActivity` are un câmp `Calendar releaseCal` — dar acela e **starea UI-ului**, nu parte din model. Modelul are doar `Date release`. Separarea e corectă: modelul ține datele, activitatea ține starea temporară a formularului.

</details>

---

## Pasul 2.4 — Constructorul fără argumente

### De ce

În `ItemActivity.saveMovie()` apare:

```java
Movie movie = new Movie();
movie.setTitle(...);
movie.setRelease(...);
// ...
```

Se creează un obiect **gol**, apoi se umple câmp cu câmp. Ai nevoie de `new Movie()` — adică de un constructor fără parametri.

> **Atenție Java:** dacă **definiți** un constructor cu parametri, compilatorul **nu mai generează** automat constructorul fără parametri. Deci trebuie să-l scrii explicit. Ăsta e motivul pentru care îl găsești la **sfârșitul** clasei în repo — și e o capcană clasică la test.

### Cum

```java
public Movie() {
}
```

Gata. (În repo e pus la finalul fișierului, după getteri. Poziția în fișier nu contează pentru compilator.)

---

## Pasul 2.5 — Constructorul cu toate argumentele

### De ce

În `MainActivity.addSampleMovies()` se creează filmele demo **dintr-o singură expresie**:

```java
movies.add(new Movie(
        "Inception",
        new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),
        "Sci-Fi",
        160000000,
        148,
        4.5f,
        true,
        "PG-13",
        false,
        "https://example.com/posters/inception.jpg"));
```

Un constructor cu 10 parametri ține codul compact. Alternativa — 10 linii de setteri pentru fiecare film — ar umple `MainActivity` de zgomot.

### Capcana ordinii

Cei 10 parametri sunt **poziționali**. Nimic nu te oprește să scrii `"PG-13"` în locul lui `true`. Compilatorul nu te prinde dacă tipurile se potrivesc (ex. `String` vs `String`).

Ordinea din repo, pe care o respecți **exact**:

```
1. String title
2. Date release
3. String genre
4. double budget
5. int duration
6. float rating
7. boolean watched
8. String approval
9. boolean onWatchlist
10. String poster
```

### Cum

```java
public Movie(String title, Date release, String genre, double budget,
             int duration, float rating, boolean watched, String approval,
             boolean onWatchlist, String poster) {
    this.title = title;
    this.release = release;
    this.genre = genre;
    this.budget = budget;
    this.duration = duration;
    this.rating = rating;
    this.watched = watched;
    this.approval = approval;
    this.onWatchlist = onWatchlist;
    this.poster = poster;
}
```

`this.title = title;` — `this` e obligatoriu când parametrul are același nume cu câmpul. Fără `this`, ai face `title = title;` (auto-atribuire, câmpul rămâne `null`).

### Exercițiu 2.5

**Cerință:** scrie un al doilea constructor care primește doar `title` și `genre` și lasă restul valorilor implicite. Ce valori vor avea `budget`, `duration`, `rating`?

<details>
<summary>Indiciu</summary>

Un `double` nedeclarat = `0.0`, un `int` = `0`, un `float` = `0.0f`, un `boolean` = `false`, un `String` = `null`, un `Date` = `null`.

</details>

<details>
<summary>Soluție</summary>

```java
public Movie(String title, String genre) {
    this.title = title;
    this.genre = genre;
    // restul rămân valorile implicite Java
}
```

`budget = 0.0`, `duration = 0`, `rating = 0.0f`, `watched = false`, `approval = null`, `onWatchlist = false`, `poster = null`, `release = null`.

**Ce s-a făcut:** ai adăugat un constructor **supraîncărcat** — al doilea, cu doi parametri, lângă cel cu zece.

**Cum funcționează supraîncărcarea:** Java alege constructorul după **semnătură** (numărul și tipurile parametrilor), nu după nume. `new Movie("Dune", "Sci-Fi")` găsește constructorul cu `(String, String)`. `new Movie()` găsește cel gol. `new Movie("Dune", date, "Sci-Fi", ...)` găsește cel cu zece.

**De ce valorile implicite contează:** în Java, câmpurile de instanță se inițializează automat cu valorile lor default (`0`, `false`, `null`). **Nu** trebuie să le scrii. Dar trebuie să știi ce sunt, pentru că UI-ul le va afișa.

**De reținut:**
1. **Valorile implicite Java:** `int`/`long`/`short`/`byte` = 0, `float`/`double` = 0.0, `boolean` = false, **orice obiect = `null`**.
2. `release = null` e periculos: `dateFormat.format(null)` aruncă `NullPointerException`.
3. Un constructor care lasă câmpuri `null` mută responsabilitatea validării la **consumator** (UI-ul). E o decizie de design, nu neapărat o greșeală.

**Unde revine:** în capitolul 09 (pasul 9.3), vezi exact NPE-ul cauzat de `release = null`. Versiunea ta locală de sync îl repară cu `if (existing.getRelease() != null)`. **Modelul permite null; UI-ul trebuie să se apere.**

</details>

---

## Pasul 2.6 — Getteri și setteri

### De ce

Codul din ambele activități citește și scrie câmpuri prin metode:

```java
movie.setTitle(etTitle.getText().toString());
// ...
existing.getRelease()
```

Nu ai voie să faci `movie.title` direct — e `private`.

### Convenția JavaBeans

| Tip câmp | Getter | Setter |
|---|---|---|
| `String`, `Date` | `getTitle()` | `setTitle(String)` |
| `double` | `getBudget()` | `setBudget(double)` |
| `int` | `getDuration()` | `setDuration(int)` |
| `float` | `getRating()` | `setRating(float)` |
| `boolean` | **`isWatched()`** | `setWatched(boolean)` |

> **Atenție la `boolean`:** getter-ul e `isWatched()`, nu `getWatched()`. Aici intervine o capcană: în `MovieAdapter` (capitolul 11) se apelează `movie.isWatched()` și `movie.isOnWatchlist()`. Dacă ai scris `getWatched()`, codul nu compilează.

### Cum

```java
public String getTitle() { return title; }
public void setTitle(String title) { this.title = title; }

public Date getRelease() { return release; }
public void setRelease(Date release) { this.release = release; }

public String getGenre() { return genre; }
public void setGenre(String genre) { this.genre = genre; }

public double getBudget() { return budget; }
public void setBudget(double budget) { this.budget = budget; }

public int getDuration() { return duration; }
public void setDuration(int duration) { this.duration = duration; }

public float getRating() { return rating; }
public void setRating(float rating) { this.rating = rating; }

public boolean isWatched() { return watched; }
public void setWatched(boolean watched) { this.watched = watched; }

public String getApproval() { return approval; }
public void setApproval(String approval) { this.approval = approval; }

public boolean isOnWatchlist() { return onWatchlist; }
public void setOnWatchlist(boolean onWatchlist) { this.onWatchlist = onWatchlist; }

public String getPoster() { return poster; }
public void setPoster(String poster) { this.poster = poster; }
```

### Scurtătură Android Studio

**Alt+Insert** (sau click dreapta → **Generate**) → **Getter and Setter** → selectezi toate câmpurile → OK. Generează toate cele 20 de metode. **Scrie-le totuși o dată manual**, ca să știi ce generezi.

### Exercițiu 2.6

**Cerință:** de ce `getDuration()` returnează `int` dar `getBudget()` returnează `double`, deși ambele sunt numere? Răspunde fără să te uiți la tabel.

<details>
<summary>Răspuns</summary>

**Ce s-a făcut:** ai răspuns la o întrebare de tip „de ce tipul e ăsta”, fără să scrii cod.

**Răspunsul:** pentru că **sursa** lor diferă. `SeekBar.getProgress()` întoarce `int` — progresul e un întreg între `min` și `max`. Bugetul vine dintr-un text cu zecimale (`numberDecimal`) și e citit cu `Double.parseDouble`, care întoarce `double`.

**Regula generală:** **tipul câmpului = tipul sursei**. Dacă sursa e `int`, câmpul e `int`. Dacă sursa e `double`, câmpul e `double`. Astfel eviți conversii la fiecare citire/scriere.

**De reținut:**
1. Conversia `int` → `double` e **implicită** (nu pierzi date). Conversia `double` → `int` e **explicită** (pierzi zecimale).
2. Dacă ai fi pus `int budget`, ai fi pierdut zecimalele la fiecare salvare.
3. Dacă ai fi pus `double duration`, ai fi avut `148.0` în loc de `148` — inutil.

**Unde revine:** în capitolul 07 (pasul 7.8), `saveMovie` face exact conversiile inverse: `sbDuration.getProgress()` (int) → `setDuration(int)`, `Double.parseDouble(...)` (double) → `setBudget(double)`. Tipurile se potrivesc, fără cast.

</details>

---

## Pasul 2.7 — `toString()`

### De ce

`ArrayAdapter` — cel folosit în `MainActivity` — **nu știe** să afișeze un `Movie`. El primește o listă de obiecte și, pentru fiecare, cheamă `toString()`. Dacă nu suprascrii `toString()`, `ListView`-ul va afișa:

```
ro.ase.ie.g1097.model.Movie@a1b2c3d
```

ceea ce e inutil. Deci `toString()` e **mecanismul de afișare** pentru lista din capitolul 04.

> Important: în capitolul 11, când treci pe `RecyclerView`, `toString()` **nu mai e folosit** — adapterul citește câmpurile individual cu getteri. Dar până atunci, e singurul mod în care lista arată ceva.

### Cum

```java
@Override
public String toString() {
    return "Movie{" +
            "title='" + title + '\'' +
            ", release=" + release +
            ", genre='" + genre + '\'' +
            ", budget=" + budget +
            ", duration=" + duration +
            ", rating=" + rating +
            ", watched=" + watched +
            ", approval='" + approval + '\'' +
            ", onWatchlist=" + onWatchlist +
            ", poster='" + poster + '\'' +
            '}';
}
```

### De ce arată așa

`'\''` e un `'` escapate. Formatul `Cheie{cheie='valoare', ...}` e generat de IntelliJ/Android Studio (**Alt+Insert → toString()**), nu inventat de profesor.

### Avertisment

Dacă lași `toString()` așa, `ListView`-ul va afișa **tot** — inclusiv URL-ul posterului și toate cele 10 câmpuri, pe un singur rând. Va arăta îngrozitor.

Dar **așa e în repo** la commitul `d719ffc`. Lista arată urât până la capitolul 11, când `RecyclerView` + `movie_item.xml` o fac frumoasă. E o dovadă că aplicația e în evoluție, nu finisată.

### Exercițiu 2.7

**Cerință:** modifică temporar `toString()` să returneze doar `title + " (" + rating + ")"`. Rulează aplicația din capitolul 04 (după ce îl termini) și observă diferența. Apoi **revino** la versiunea din repo.

<details>
<summary>Indiciu</summary>

Nu uita că `ListView` folosește `android.R.layout.simple_list_item_1`, care are un singur `TextView`. Tot ce returnezi apare pe un rând.

</details>

<details>
<summary>Soluție</summary>

```java
@Override
public String toString() {
    return title + " (" + rating + ")";
}
```

**Ce s-a făcut:** ai suprascris `toString()` cu o formă compactă, care returnează doar titlul și rating-ul.

**Cum se vede:** în listă, `Inception (4.5)`, `Toy Story (4.0)`, `The Matrix (5.0)` — mult mai lizibil decât `Movie{title='Inception', release=Mon Jul 16...}`.

**De ce funcționează:** `ArrayAdapter.getView()` cheamă `toString()` pe fiecare element și pune rezultatul într-un `TextView`. Deci **orice** returnezi apare pe rândul listei. E un contract implicit: dacă vrei ca lista să arate bine cu `ArrayAdapter`, `toString()` trebuie să fie prietenos.

**De reținut:**
1. **`toString()` e contractul de afișare** pentru `ArrayAdapter`. Nu e doar pentru debugging.
2. `rating` e `float`; `" (" + rating + ")"` face conversie automată la `String`.
3. Revino la versiunea completă după exercițiu — fidelitatea față de repo contează la test.

**Unde revine:** în capitolul 11, `RecyclerView` **nu mai folosește** `toString()`. `MovieAdapter.bind()` citește câmpurile individual cu getteri. Deci `toString()` devine irelevant pentru afișare — dar rămâne util pentru debugging.

**Lecția:** `toString()` nu e doar pentru debugging; la `ArrayAdapter` e **contractul de afișare**.

</details>

---

## Pasul 2.8 — Verificarea modelului

### De ce

Înainte să construiești UI-ul, verifici că modelul e corect. Un model greșit se propagă în tot restul aplicației.

### Cum

Fișierul final trebuie să arate exact ca `cod-final/java/ro/ase/ie/g1097/model/Movie.java`. Compară cu:

```bash
# în Git Bash, din folderul test 1
diff <(cat cod-final/java/ro/ase/ie/g1097/model/Movie.java) <(cat "_progres/Movies1097/app/src/main/java/ro/ase/ie/g1097/model/Movie.java")
```

Sau pur și simplu deschide ambele fișiere alături în Android Studio și compară vizual.

### Checklist

- [ ] pachetul e `ro.ase.ie.g1097.model`
- [ ] `implements Serializable`
- [ ] 10 câmpuri `private`, exact tipurile din tabel
- [ ] comentariile cu widget-ul sursă
- [ ] constructor fără argumente **explicit**
- [ ] constructor cu 10 argumente, în ordinea corectă
- [ ] 20 de getteri/setteri, `isWatched`/`isOnWatchlist` pentru booleeni
- [ ] `toString()` suprascris

> **Numele fișierului trebuie să fie `Movie.java`** și clasa `public class Movie`. Dacă nu, Java nu compilează.

---

## Pasul 2.9 — Exercițiu de reflecție

**Cerință:** fără să te uiți în cod, scrie pe hârtie cum arată `new Movie("Dune", 2021, "Sci-Fi")`. Compilează? De ce da / de ce nu?

<details>
<summary>Răspuns</summary>

**Nu compilează.** Nu ai un constructor `Movie(String, int, String)`. Ai doar `Movie()` și `Movie(String, Date, String, double, int, float, boolean, String, boolean, String)`.

Java nu face conversii implicite de la `int` la `Date`. Trebuie:

```java
new Movie("Dune", new GregorianCalendar(2021, Calendar.OCTOBER, 22).getTime(),
          "Sci-Fi", /* ... restul */);
```

sau, mai simplu, constructorul gol + setteri.

**Lecția:** constructorii sunt **supraîncărcați** după semnătură (tipurile și numărul parametrilor), nu după nume. Dacă vrei comoditate, adaugi un constructor `Movie(String title, String genre)`.

</details>

---

## Rezumat capitol 02

- `Movie` e un POJO serializabil, fără importuri Android.
- 10 câmpuri, fiecare cu tipul dictat de widget-ul sursă.
- Constructor gol **explicit** + constructor complet cu 10 parametri.
- Getteri/setteri, cu `isX()` pentru booleeni.
- `toString()` e contractul de afișare pentru `ArrayAdapter`.

### Autoverificare

1. De ce `Movie` nu are `import android.*`?
2. Ce se întâmplă dacă uiți constructorul gol?
3. De ce obiectul primit în `ItemActivity` nu e „același” obiect?
4. De ce `toString()` contează pentru `ListView` dar nu pentru `RecyclerView`?

<details>
<summary>Răspunsuri</summary>

1. Pentru că modelul trebuie să fie testabil și refolosibil fără Android. Dacă ar importa `EditText`, ar depinde de UI.
2. `new Movie()` nu compilează — compilatorul a văzut un constructor custom și nu mai generează cel implicit.
3. `Intent` serializează/deserializează — copie de valoare, nu de referință. De aceea editarea trimite înapoi rezultat, nu modifică direct.
4. `ArrayAdapter` apelează implicit `toString()` pe elemente; `RecyclerView.Adapter` apelează metodele pe care le scrii tu în `onBindViewHolder`.

</details>

---

**Următorul capitol:** [03 - Ecranul principal - layout.md](03%20-%20Ecranul%20principal%20-%20layout.md)
