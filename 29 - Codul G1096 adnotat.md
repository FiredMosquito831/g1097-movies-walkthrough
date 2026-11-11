# Capitolul 29 — Codul G1096 adnotat

**Obiectiv:** să citești fiecare linie a aplicației G1096 cu explicația lipită de ea — ce face, de ce e acolo, ce se rupe dacă o scoți — și să vezi exact prin ce diferă de G1097, ca să nu înveți o variantă și să scrii alta.

**Timp estimat:** 90–120 min (citire activă, cu proiectul deschis în paralel).

**Sursa:** `mihaidoinea/dma2026`, commitul `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`. Grupa G1096 **nu are** `movie_item.xml`.

**Regulă:** codul este **nemodificat, byte cu byte**. Tot ce apare cu `//`, `/* */` sau `<!-- -->` în plus față de sursă este adnotare. Comentariile care existau deja în sursă (`//EditText`, `//Spinner`, `<!-- Header -->`) au fost păstrate exact, iar adnotarea s-a construit în jurul lor.

---

## 29.0 Ce diferă față de G1097

Aplicația este aceeași: `MainActivity` ține `List<Movie>`, un `ArrayAdapter` o afișează într-un `ListView`, FAB-ul deschide `ItemActivity` printr-un `Intent`, rezultatul se întoarce printr-un `ActivityResultLauncher`, iar `ItemActivity` construiește un `Movie` din formular. Aceleași zece câmpuri, aceleași widget-uri, aceleași două layout-uri de ecran.

Diferențele sunt puține și mici. Tocmai de aceea contează: sunt exact locurile în care o întrebare de examen poate primi două răspunsuri corecte, în funcție de grupa pe care ai citit-o.

| Aspect | G1096 | G1097 (referință) |
|---|---|---|
| Câmpul pentru poster în `Movie.java` | `private String posterUrl;` | `private String poster = null;` |
| Inițializator de câmp | niciunul | `= null` |
| Poziția constructorului fără parametri | **primul**, înaintea celui cu parametri (linia 18) | ultimul, după setteri (linia 127) |
| `toString()` include posterul? | **NU** | da (`poster`) |
| `MainActivity.java` — importuri nefolosite | `java.math.BigDecimal` și `android.widget.Toast` | `java.util.Date` și `android.widget.Toast` |
| `MainActivity.java` — importă `java.util.Date`? | **nu** | da (nefolosit) |
| `ItemActivity.java` — importuri nefolosite | `android.widget.Switch` | `Switch`, `Toast`, `Snackbar`, `ActivityItemBinding` |
| `ItemActivity.java` — importă `Toast`/`Snackbar`/`ActivityItemBinding`? | **nu** | da (toate nefolosite) |
| `activity_main.xml` | identic cu G1097 | — |
| `activity_item.xml` | identic cu G1097 | — |
| `AndroidManifest.xml` | identic cu G1097 (diferă doar tema: `Theme.G1096`) | `Theme.G1097` |
| `movie_item.xml` | **nu există** | există (pregătit pentru S07, nefolosit de niciun cod) |

### 29.0.1 Numele câmpului: `posterUrl` vs `poster`

G1096 declară `private String posterUrl;`. G1097 declară `private String poster = null;`. Diferența nu este doar lexicală: ea se propagă în **accesori**.

- G1096 are `getPosterUrl()` și `setPosterUrl(String)`.
- G1097 are `getPoster()` și `setPoster(String)`.

`ItemActivity` din G1096 apelează `movie.setPosterUrl(etPoster.getText().toString())` în `saveMovie()` și `existing.getPosterUrl()` în `fillForm()`. Dacă lipești cod din capitolul 22 într-un proiect G1096, compilatorul se oprește cu `cannot find symbol: method setPoster(java.lang.String)`. Eroarea nu este evidentă pentru cineva care se uită la formular — câmpul se numește `etPoster`, dar modelul se numește `posterUrl`.

**Ce înveți:** numele unui câmp `private` nu este cosmetic. El devine contract public prin numele accesoriilor. Când redenumești câmpul, trebuie să redenumești accesoriile și să actualizezi toate locurile care le apelează — aici două, în `ItemActivity`.

**Nuanță de semantică:** `posterUrl` este mai precis — spune că valoarea este un link, nu o imagine. `poster` este mai general — ar putea fi o cale locală, un nume de fișier sau un `Drawable`. Ambele sunt corecte. Important este să fie consistente în tot proiectul.

### 29.0.2 Inițializatorul `= null`

G1097 scrie `private String poster = null;`. G1096 scrie doar `private String posterUrl;`. La runtime, **comportamentul este identic**: un câmp de tip obiect este oricum inițializat cu `null` de către JVM, înainte ca orice constructor să ruleze.

Deci de ce apare `= null` în G1097? Este **documentație**: linia spune explicit „acest câmp poate lipsi; un film fără poster este valid". Un cititor care vede `= null` nu se întreabă dacă lipsa valorii este un bug.

**Ce înveți:** în Java, `= null` pe un câmp de instanță nu previne nimic și nu schimbă nimic. Nu există „inițializare sigură" prin `= null`; există doar intenție comunicată. Capcana opusă este reală: a scrie `= null` pe un câmp `final` sau a inițializa cu `null` o variabilă pe care apoi o folosești imediat **ascunde** un `NullPointerException` în loc să îl prevină.

**Legătura cu constructorul gol:** `new Movie()` lasă toate cele zece câmpuri pe valorile implicite (`null`, `0`, `0.0`, `false`). Deci `posterUrl` este `null` după `new Movie()`, indiferent dacă în declarație scrie `= null` sau nu.

### 29.0.3 Poziția constructorului fără parametri

În G1096, `public Movie() { }` este **prima metodă din clasă**, la linia 18, imediat după cele zece câmpuri și înaintea constructorului cu parametri. În G1097, același constructor este **ultima metodă**, la linia 127, după toate cele douăzeci de getter-e și setter-e.

Pentru compilator: **zero diferență**. Ordinea metodelor într-o clasă nu are nicio semnificație semantică în Java. Pentru cititor: G1096 îți arată mai întâi „cum se creează un obiect gol", apoi „cum se creează un obiect plin" — exact ordinea în care apar în aplicație: `saveMovie()` face `new Movie()` (gol, umplut cu setter-e), iar `addSampleMovies()` face `new Movie(10 argumente)` (plin, dintr-o expresie).

**Ce înveți:** poziția este o decizie de stil, nu o regulă. IntelliJ generează constructorii acolo unde îi pui. Ce **nu** este stil este existența lui: dacă definești orice constructor cu parametri, compilatorul nu mai generează automat constructorul fără parametri. `new Movie()` din `saveMovie()` ar înceta să compileze. Ambele grupe îl scriu explicit — doar în locuri diferite.

**Detaliu de formatare, vizibil în sursă:** în G1096 lista de parametri a constructorului plin este ruptă pe două linii (linia 21 se termină cu `onWatchlist,`, linia 22 începe cu `String posterUrl)`), aliniată sub primul parametru. În G1097 este pe o singură linie. Nu schimbă nimic semantic; arată doar că fișierul a trecut prin alt formator sau prin altă lățime de fereastră.

### 29.0.4 `toString()` fără poster

`toString()` din G1096 se oprește la `onWatchlist`. `posterUrl` **nu apare** în textul returnat. În G1097, ultimul fragment este `", poster='" + poster + '\''`.

**Consecința vizibilă:** în listă, rândul G1096 nu afișează URL-ul posterului. Pentru un rând de `ListView` cu `simple_list_item_1`, acesta este chiar un avantaj — rândul este mai scurt și mai lizibil.

**Consecința ascunsă, și aceasta este lecția:** `toString()` este scris de mână. Adăugarea unui câmp în clasă **nu** îl adaugă automat în `toString()`. Dacă adaugi un câmp și uiți să îl pui în `toString()`, **nimic nu se rupe**: codul compilează, aplicația rulează, doar că valoarea nu se vede nicăieri. Este un bug tăcut, opusul unui crash.

**Ce înveți:** `toString()` este un contract de afișare, nu o oglindă a clasei. Îl actualizezi conștient, când vrei să vezi câmpul. La examen, dacă ți se cere „afișați toate atributele", numără-le pe degete — zece câmpuri, zece fragmente.

**Nuanță:** `Date` nu este încadrat în apostrofuri, pentru că `Date.toString()` produce deja un format lizibil (`Sat Jul 16 00:00:00 GMT+03:00 2010`). Acel format depinde de timezone și de locale, deci nu este stabil între dispozitive.

### 29.0.5 Importurile nefolosite din `MainActivity.java`

G1096 importă `java.math.BigDecimal` și `android.widget.Toast`, ambele nefolosite. G1097 importă `java.util.Date` și `android.widget.Toast`, ambele nefolosite. Intersecția este `Toast`; diferența este `BigDecimal` față de `Date`.

Ce sugerează fiecare despre istoria fișierului (ipoteze plauzibile, nu fapte din sursă):

- **`BigDecimal`** — probabil cineva a luat în calcul să parseze bugetul cu precizie zecimală exactă (`new BigDecimal(text)`), apoi a renunțat în favoarea lui `Double.parseDouble` din `ItemActivity`. Importul a rămas.
- **`Date`** (doar în G1097) — probabil cineva a lucrat cu date direct în `MainActivity`, apoi a mutat logica în model.
- **`Toast`** (în ambele) — probabil un mesaj de confirmare la salvare, scos la un moment dat. `Toast` este importul „care rămâne" în aproape orice proiect Android.

**Detaliu important, verificabil:** G1096 **nu** importă `java.util.Date`, deși `Movie` are un câmp `Date` și `MainActivity` construiește date cu `GregorianCalendar`. Nu are nevoie: `new GregorianCalendar(...).getTime()` întoarce un `Date`, dar tipul nu este **numit** niciodată în fișier. Importul este necesar doar când scrii numele tipului, nu când îl pasezi mai departe.

**Ce înveți:** un import nefolosit nu strică build-ul — `javac` nu dă eroare, doar `-Xlint:all` dă warning. Dar el **minte despre dependențe**: cine citește fișierul crede că `MainActivity` lucrează cu bani exacți sau cu date, iar el nu face niciuna.

### 29.0.6 Importurile nefolosite din `ItemActivity.java`

G1096 importă un singur nume mort: `android.widget.Switch`. G1097 importă patru: `Switch`, `Toast`, `Snackbar` și `ActivityItemBinding`.

**De ce `Switch` este mort în toate cele patru grupe:** toate declară `private MaterialSwitch swWatched;`, iar `MaterialSwitch` este `com.google.android.material.materialswitch.MaterialSwitch`. Niciun nume `Switch` nu apare în corpul fișierului.

**Și de ce este bine că este mort:** `MaterialSwitch` extinde `SwitchCompat`, care extinde `CompoundButton`. **Nu** extinde `android.widget.Switch`. Dacă cineva ar „repara" importul folosindu-l — `private Switch swWatched;` — atunci `findViewById(R.id.swWatched)` ar întoarce un `MaterialSwitch` și atribuirea ar arunca `ClassCastException` la runtime. Importul mort este, în acest caz, o capcană **dezamorsată**.

**`ActivityItemBinding`** (doar în G1097) este clasa generată de View Binding. Dacă View Binding ar fi activat, ai scrie `ActivityItemBinding binding = ActivityItemBinding.inflate(getLayoutInflater());` și ai renunța la cei 13 `findViewById`. G1096 nu o face — folosește `findViewById` clasic, iar importul nu există deloc.

**`Toast` și `Snackbar`** (doar în G1097) sunt moarte pentru că `saveMovie()` nu afișează nicio confirmare: apelează `setResult` și `finish()`, iar utilizatorul vede lista actualizată. În G1096 autorul nu le-a importat niciodată.

**Ce înveți:** numărul de importuri moarte nu măsoară calitatea codului, dar **spune o poveste** despre ce a încercat autorul și a abandonat. La examen, dacă ți se cere să identifici importurile nefolosite, metoda este mecanică: pentru fiecare import, caută numele clasei în restul fișierului.

### 29.0.7 `movie_item.xml` lipsește

G1097 are un al șaselea fișier: `movie_item.xml`, un layout de rând cu card, poster și chips-uri de stare. G1096 nu îl are deloc.

**Diferența funcțională este zero.** `MainActivity` din ambele grupe folosește `android.R.layout.simple_list_item_1`, nu `R.layout.movie_item`. Nicio linie de cod nu referă fișierul. El există în G1097 doar ca pregătire pentru S07, unde lista trece pe `RecyclerView`.

**Ce înveți:** un fișier de resurse pe care niciun cod nu îl referă este greutate moartă. `R.layout.movie_item` apare în `R.java` doar dacă fișierul există, dar nimeni nu îl citește. Ștergerea lui nu schimbă comportamentul aplicației — doar câteva sute de bytes din APK.

**Legătura cu laboratorul următor:** în G1096, trecerea la `RecyclerView` cere crearea lui `movie_item.xml` de la zero. În G1097, fișierul este deja acolo și trebuie doar legat.

### 29.0.8 Ce rămâne identic — și de ce contează

Trei fișiere sunt identice sau aproape identice: `activity_main.xml`, `activity_item.xml` și `AndroidManifest.xml`. Ultimul diferă doar prin referința la temă (`@style/Theme.G1096` față de `@style/Theme.G1097`).

Asta înseamnă că **tot ce înveți despre layout-uri din capitolul 22 se aplică aici cuvânt cu cuvânt**. Diferențele sunt în codul Java și în model, nu în XML. Dacă la examen ți se cere să explici un atribut din `activity_item.xml`, răspunsul este același pentru ambele grupe.

---

## 29.1 Cum să citești acest capitol

Acesta nu este un capitol de exerciții. Este un capitol de **citire cu lupa**: iei fiecare fișier al aplicației și îl parcurgi linie cu linie, cu explicația chiar deasupra.

- **Citește codul întâi, comentariul al doilea.** Acoperă cu mâna blocul de comentarii, spune ce face linia, apoi verifică. Dacă ai citit doar comentariul, ai impresia că știi; dacă ai încercat să prezici linia, chiar știi.
- **Blocurile `BLOC DE TEORIE`** apar înaintea fiecărei clase și a fiecărei secțiuni mari de XML. Ele explică *de ce* există structura, nu *cum* funcționează. Citeste-le primele, apoi intră în cod.
- **Blocurile de deasupra metodelor** au patru etichete fixe: `CE FACE`, `CUM`, `RISC`, `REF`. `REF` trimite la alt loc din aplicație sau la alt capitol unde apare același pattern.
- **Pașii numerotați** („1. Validare", „2. Curățare stare veche", „3. Actualizare") descriu ordinea execuției. Ordinea este parte din lecție: aceiași pași în altă ordine produc alt rezultat.
- **Marcajele `RISC:`, `BUG:` și `DANGER!`** semnalează locurile unde codul funcționează astăzi dar se poate rupe, sau unde se rupe deja. Sunt cele mai valoroase linii din capitol — la examen se cer exact acestea.
- **Diagramele ASCII** arată ce nu se vede în cod: arborele de view-uri, obiectul care călătorește între activități, ordinea din `onCreate`, ciclul de viață.
- **Compară cu capitolul 22.** Fiecare diferență din 29.0 are un corespondent exact acolo. Dacă înveți o singură variantă, înveți jumătate din răspuns.
- **Nu memora.** Scopul este să poți reconstrui fișierul pornind de la o diagramă. Dacă poți desena fluxul, codul vine singur.

---

## 29.2 `Movie.java` — modelul de date

```java
/*
 * ======================================================================================
 * FIȘIER: Movie.java — MODELUL DE DATE AL APLICAȚIEI
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   O clasă POJO (Plain Old Java Object): 10 câmpuri private, un constructor fără
 *   parametri, un constructor cu 10 parametri și 20 de getter-e/setter-e.
 *   Zero logică de business, zero referințe la Android.
 *
 * DE CE EXISTĂ:
 *   Este singurul tip care traversează granița dintre cele două activități.
 *   `MainActivity` ține `List<Movie>`; `ItemActivity` construiește un `Movie` din
 *   formular și îl trimite înapoi. Modelul este liantul dintre cele două ecrane.
 *
 * DE CE DEPINDE:
 *   - `java.io.Serializable` — ca obiectul să poată fi pus într-un `Intent`.
 *   - `java.util.Date` — tipul datei de lansare.
 *   Nimic din `android.*`. Aceasta este proprietatea care îl face testabil pe JVM.
 *
 * CINE DEPINDE DE EL:
 *   `MainActivity` (lista, adapterul, extra-urile), `ItemActivity` (`fillForm`,
 *   `saveMovie`), `ArrayAdapter` (prin `toString()`).
 *
 * CE NU FACE:
 *   - Nu validează nimic: acceptă titlu gol, buget negativ, dată null.
 *   - Nu are `id`: identitatea în listă este POZIȚIA.
 *   - Nu are `equals()` / `hashCode()`: două filme cu aceleași valori nu sunt
 *     „egale" pentru `List.remove()` sau `List.contains()`.
 *   - Nu știe ce este un `EditText`, un `Spinner` sau un `Intent`.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   `Intent.putExtra(MOVIE_EXTRA, movie)` nu ar avea tip; `ArrayAdapter` nu ar
 *   avea ce afișa; `ItemActivity` ar trebui să trimită 10 extra-uri separate, iar
 *   `MainActivity` le-ar recompune manual — 10 chei de sincronizat în două locuri.
 * ======================================================================================
 */

// Pachetul = calea din `src/main/java`. Aici `ro.ase.ie.g1096.model`.
// `model` este subpachetul care ține tipurile de date; `activities` ține ecranele.
// Separarea nu este cosmetică: `model` nu importă nimic din `activities`, deci
// poate fi testat și refolosit fără Android.
package ro.ase.ie.g1096.model;

// ======================================================================================
// IMPORT 1: java.io.Serializable
// ======================================================================================
// CE ESTE: o interfață MARKER — nu are nicio metodă de implementat.
// DE CE AICI: `Intent.putExtra(String, Serializable)` este cea mai simplă cale de a
//   trimite un obiect întreg către altă activitate. Fără `implements Serializable`,
//   apelul `intent.putExtra(MOVIE_EXTRA, movie)` nu găsește nicio suprascriere
//   potrivită și NU COMPILEAZĂ.
// CE SE ÎNTÂMPLĂ LA RUNTIME: JVM-ul serializează graful de obiecte în bytes, îl pune
//   în `Bundle`, iar activitatea destinatară primește o COPIE deserializată.
// RISC: fără `serialVersionUID` declarat, JVM-ul calculează unul din structura clasei.
//   Dacă adaugi un câmp între scriere și citire (procese diferite), primești
//   `InvalidClassException`. Aici scrierea și citirea se întâmplă în ACELAȘI proces,
//   la câteva milisecunde distanță, deci riscul este teoretic.
// ======================================================================================
import java.io.Serializable;

// ======================================================================================
// IMPORT 2: java.util.Date
// ======================================================================================
// CE ESTE: un moment în timp, stocat intern ca număr de milisecunde din 1 ianuarie 1970.
// DE CE AICI: data de lansare trebuie să fie o DATĂ, nu un text. Ca `Date` poți
//   sorta, compara și formata cu `SimpleDateFormat`.
// DE CE NU `String`: ai stoca „16/07/2010" și ai pierde capacitatea de a calcula.
//   `fillForm` ar trebui să parseze la fiecare afișare, iar `saveMovie` ar trebui
//   să formateze la fiecare salvare — două locuri în care poți greși formatul.
// DE CE NU `java.time.LocalDate`: este mai nou și mai curat, dar `Date` este
//   `Serializable` din fabrică și este tipul folosit de restul aplicației.
// RISC: `Date` este MUTABIL. `getRelease()` întoarce referința internă, nu o copie,
//   deci un apelant neatent poate modifica data din obiect fără să treacă prin setter.
// ======================================================================================
import java.util.Date;

/*
 * ======================================================================================
 * BLOC DE TEORIE: DE CE UN MODEL SEPARAT (POJO) ȘI DE CE `Serializable`
 * ======================================================================================
 *
 * 1. SINGLE RESPONSIBILITY
 *    Clasa are un singur motiv să se schimbe: se modifică structura datelor unui film.
 *    Nu se schimbă când se schimbă un layout, un buton sau o culoare. Dacă ai pune
 *    `getText().toString()` aici, clasa ar depinde de `android.widget.EditText` și ar
 *    avea două motive să se schimbe.
 *
 * 2. SERIALIZABILITY
 *    `Intent.putExtra(String, Serializable)` este cea mai simplă cale de a trimite un
 *    obiect întreg către altă activitate. Fără `implements Serializable`, apelul
 *    `intent.putExtra(MOVIE_EXTRA, movie)` nu găsește nicio suprascriere potrivită și
 *    NU COMPILEAZĂ. Interfața nu are metode: schimbă doar ce poate face JVM-ul cu
 *    obiectul — îl poate transforma în bytes și înapoi.
 *
 * 3. CE SE ÎNTÂMPLĂ LA RUNTIME
 *    JVM-ul serializează graful de obiecte în bytes, îl pune în `Bundle`, iar
 *    activitatea destinatară primește o COPIE deserializată. Originalul rămâne în
 *    lista din `MainActivity`.
 *
 *    [MainActivity]                      [Intent]                     [ItemActivity]
 *    movies.get(position)                                                  |
 *          |                                                               |
 *          +-- putExtra("movie", obj) --+                                  |
 *                                       |                                  |
 *                           serialize (JVM -> bytes)                      |
 *                                       |                                  |
 *                                       +-- Bundle -- startActivity --> --+
 *                                                                          |
 *                                                        getSerializableExtra(...)
 *                                                                          |
 *                                                           O COPIE, nu originalul
 *
 *    Consecința practică: modificarea copiei NU se vede în listă. De aceea
 *    `MainActivity` face `movies.set(position, movie)` la întoarcere.
 *
 * 4. DE CE FĂRĂ CÂMP `id`
 *    Identitatea filmului în listă este POZIȚIA, nu un ID. De aici vine tot mecanismul
 *    `POSITION_EXTRA` din celelalte două fișiere. Este o simplificare didactică: o bază
 *    de date reală ar avea un `id` stabil, iar ștergerea unui rând nu ar mai muta
 *    identitatea celorlalte.
 *
 * 5. TESTABILITY
 *    În fișier nu există niciun `import android.*`. Poți scrie un test JVM care creează
 *    un `Movie` și verifică `getTitle()`. Fără emulator, fără Android, fără Robolectric.
 *
 * 6. CONVENȚIA DE NUME PENTRU BOOLEENI
 *    `isWatched()` și `isOnWatchlist()`, nu `getWatched()` și `getOnWatchlist()`.
 *    Este convenția JavaBeans: framework-urile care citesc proprietăți prin reflecție
 *    caută prefixul `is` pentru `boolean`. `fillForm` apelează exact aceste nume.
 * ======================================================================================
 */

// `implements Serializable` = interfață marker, fără nicio metodă de implementat.
// Ea schimbă doar ce poate face JVM-ul cu obiectul: îl poate transforma în bytes.
public class Movie implements Serializable {

    // ==================================================================================
    // CÂMPUL 1: title
    // ==================================================================================
    // TIP: String — text liber, de lungime arbitrară.
    // WIDGET SURSĂ: `etTitle` (TextInputEditText) -> `getText().toString()`.
    // DE CE String: titlul este text, nu are operații numerice sau de dată.
    // CE SE RUPE DACĂ E GREȘIT: dacă ar fi `int`, „Inception" nu ar încăpea;
    //   dacă ar fi `char[]`, `ArrayAdapter` ar afișa adresa array-ului.
    // ==================================================================================
    private String title; //EditText

    // ==================================================================================
    // CÂMPUL 2: release
    // ==================================================================================
    // TIP: Date — un moment în timp (aici, doar ziua contează).
    // WIDGET SURSĂ: `etRelease` + `DatePickerDialog`; în model ajunge din
    //   `releaseCal.getTime()`, NU din textul din EditText.
    // DE CE Date: permite formatare cu `SimpleDateFormat` și comparare.
    // CE SE RUPE DACĂ E GREȘIT: dacă ar fi `String`, `fillForm` ar trebui să parseze
    //   la fiecare afișare, iar un text tastat greșit ar ajunge în model ca atare.
    // ==================================================================================
    private Date release; //EditText date

    // ==================================================================================
    // CÂMPUL 3: genre
    // ==================================================================================
    // TIP: String — textul selectat din listă („Sci-Fi", „Animation", „Action").
    // WIDGET SURSĂ: `spGenre` (Spinner) -> `getSelectedItem().toString()`.
    // DE CE String și nu `enum`: genurile vin din `@array/movie_genre`, adică din XML.
    //   Cu `enum`, adăugarea unui gen ar cere modificarea codului Java.
    // CE SE RUPE DACĂ E GREȘIT: dacă ai stoca poziția (`int`), schimbarea ordinii
    //   din lista de resurse `@array/movie_genre` ar schimba retroactiv genul
    //   tuturor filmelor salvate.
    // ==================================================================================
    private String genre; //Spinner

    // ==================================================================================
    // CÂMPUL 4: budget
    // ==================================================================================
    // TIP: double — număr cu zecimale, precizie de ~15–16 cifre semnificative.
    // WIDGET SURSĂ: `etBudget` (inputType=numberDecimal) -> `Double.parseDouble(...)`.
    // DE CE double și nu float: `float` are ~7 cifre semnificative. Pentru 160 000 000
    //   ambele sunt exacte, dar 160 000 001 nu ar fi reprezentabil exact în `float`.
    //   În plus, `Double.parseDouble` întoarce `double` — un câmp `float` ar cere cast.
    // CE SE RUPE DACĂ E GREȘIT: dacă ar fi `int`, zecimalele ar fi trunchiate;
    //   dacă ar fi `String`, nu ai putea compara bugete.
    // ==================================================================================
    private double budget; //EditText number

    // ==================================================================================
    // CÂMPUL 5: duration
    // ==================================================================================
    // TIP: int — număr întreg de minute, 0..300.
    // WIDGET SURSĂ: `sbDuration` (SeekBar) -> `getProgress()`.
    // DE CE int: `SeekBar.getProgress()` întoarce `int`. Orice alt tip ar cere cast.
    // CE SE RUPE DACĂ E GREȘIT: dacă ar fi `String`, `setProgress` ar cere parsare
    //   și ai putea salva „abc" ca durată.
    // ==================================================================================
    private int duration; //SeekBar

    // ==================================================================================
    // CÂMPUL 6: rating
    // ==================================================================================
    // TIP: float — nota cu jumătăți de stea (0.0, 0.5, ..., 5.0).
    // WIDGET SURSĂ: `rbRating` (RatingBar) -> `getRating()`.
    // DE CE float: `RatingBar.getRating()` și `setRating(float)` lucrează cu `float`.
    //   Un câmp `double` ar face `setRating(existing.getRating())` să NU compileze
    //   fără cast explicit.
    // CE SE RUPE DACĂ E GREȘIT: dacă ar fi `int`, ai pierde jumătățile de stea;
    //   dacă ar fi `String` („4.5"), comparațiile ar fi lexicografice.
    // ==================================================================================
    private float rating; //RatingBar

    // ==================================================================================
    // CÂMPUL 7: watched
    // ==================================================================================
    // TIP: boolean — true/false.
    // WIDGET SURSĂ: `swWatched` (MaterialSwitch) -> `isChecked()`.
    // DE CE boolean: starea unui switch este binară. `isChecked()` întoarce exact asta.
    // CE SE RUPE DACĂ E GREȘIT: dacă ar fi `String` („Yes"/„No"), orice `if` ar cere
    //   comparație de text, iar „yes" minuscul ar fi tratat ca false.
    // ATENȚIE LA ETICHETĂ: în `activity_item.xml`, switch-ul este etichetat
    //   „Recommended", nu „Watched". Câmpul spune `watched`, ecranul spune altceva.
    // ==================================================================================
    private boolean watched; //Switch

    // ==================================================================================
    // CÂMPUL 8: approval
    // ==================================================================================
    // TIP: String — TEXTUL butonului radio selectat („G", „PG", „PG-13", „R", „NC-17").
    // WIDGET SURSĂ: `rgApproval` (RadioGroup) -> buclă peste copii + `getText()`.
    // DE CE text și nu ID-ul resursei: textul supraviețuiește reordonării butoanelor
    //   în XML. ID-ul este o valoare generată în `R.java`, stabilă doar cât timp
    //   nu redenumești butonul.
    // RISC: dacă schimbi eticheta în XML („PG13" în loc de „PG-13"), `fillForm`
    //   nu mai găsește potrivirea și nu bifează nimic — silențios, fără eroare.
    // CE SE RUPE DACĂ E GREȘIT: dacă ai stoca indexul (0..4), adăugarea unui buton
    //   la începutul grupului ar schimba sensul tuturor valorilor salvate.
    // ==================================================================================
    private String approval; //RadioGroup | RadioButtons

    // ==================================================================================
    // CÂMPUL 9: onWatchlist
    // ==================================================================================
    // TIP: boolean — true/false.
    // WIDGET SURSĂ: `cbonWatchList` (MaterialCheckBox) -> `isChecked()`.
    // DE CE boolean: o bifă este binară. Independentă de `watched`: poți să fi văzut
    //   filmul ȘI să îl ții pe lista de revăzut.
    // CE SE RUPE DACĂ E GREȘIT: dacă ai refolosi `watched` pentru amândouă, cele două
    //   controale s-ar contrazice la salvare — ultimul citit ar câștiga.
    // ==================================================================================
    private boolean onWatchlist; //Checkbox

    // ==================================================================================
    // CÂMPUL 10: posterUrl — SINGURA DIFERENȚĂ DE NUME FAȚĂ DE G1097
    // ==================================================================================
    // TIP: String — un URL (sau orice text) către afișul filmului.
    // WIDGET SURSĂ: `etPoster` (inputType=textUri) -> `getText().toString()`.
    // DE CE `posterUrl` și nu `poster`: numele spune că valoarea este un LINK, nu o
    //   imagine încărcată. În G1097 câmpul se numește `poster` și are `= null` explicit.
    // DE CE FĂRĂ `= null`: în Java un câmp obiect este oricum `null` implicit. G1096
    //   nu scrie inițializatorul; comportamentul este identic, doar documentația diferă.
    // RISC: `null` ajunge în `etPoster.setText(null)` la editare — legal, dar afișează
    //   câmp gol. Dacă ai apela `.length()` pe el, ai lua `NullPointerException`.
    // OBSERVAȚIE: aplicația NU încarcă niciodată imaginea. Nu există `ImageView`,
    //   nu există bibliotecă de rețea, nu există permisiune `INTERNET` în manifest.
    //   URL-ul este stocat ca text și atât.
    // ==================================================================================
    private String posterUrl;

    // ==================================================================================
    // CONSTRUCTORUL FĂRĂ PARAMETRI — PRIMUL DIN CLASĂ ÎN G1096
    // ==================================================================================
    // DE CE ESTE OBLIGATORIU SĂ FIE SCRIS EXPLICIT:
    //   Regula Java: dacă definești ORICE constructor cu parametri, compilatorul
    //   NU mai generează automat constructorul fără parametri.
    //   `saveMovie()` din ItemActivity face `Movie movie = new Movie();`.
    //   Fără acest constructor, fișierul NU COMPILEAZĂ.
    //
    // DE CE CORPUL ESTE GOL: toate câmpurile primesc valorile implicite
    //   (null / 0 / 0.0 / false). Obiectul este umplut imediat cu setter-e.
    //
    // DE CE ESTE PRIMUL AICI: poziția nu contează pentru compilator. În G1096 stă
    //   imediat după câmpuri, ca cititorul să vadă mai întâi „obiectul gol", apoi
    //   „obiectul plin". În G1097 același constructor este ULTIMA metodă a fișierului.
    //   Ambele variante sunt corecte; este o decizie de stil, nu o regulă.
    // ==================================================================================
    public Movie() {
    }

    // ==================================================================================
    // CONSTRUCTORUL CU 10 PARAMETRI
    // ==================================================================================
    // DE CE EXISTĂ: `addSampleMovies()` din MainActivity creează cele 3 filme demo
    //   într-o singură expresie. Fără el, ar fi 10 apeluri de setter pe fiecare film.
    //
    // CAPCANA: ordinea parametrilor este POZIȚIONALĂ. Numele din semnătură nu ajută
    //   la apel — compilatorul se uită doar la tipuri și la poziție.
    //
    //   POZIȚIA   TIP       NUME           WIDGET CARE PRODUCE VALOAREA
    //   ---------------------------------------------------------------------------
    //      1      String    title          TextInputEditText etTitle
    //      2      Date      release        etRelease + DatePickerDialog
    //      3      String    genre          Spinner spGenre
    //      4      double    budget         etBudget (numberDecimal)
    //      5      int       duration       SeekBar sbDuration
    //      6      float     rating         RatingBar rbRating
    //      7      boolean   watched        MaterialSwitch swWatched
    //      8      String    approval       RadioGroup rgApproval
    //      9      boolean   onWatchlist    MaterialCheckBox cbOnWatchList
    //     10      String    posterUrl      etPoster (textUri)
    //
    //   Dacă inversezi pozițiile 1 și 3 (ambele String) sau 7 și 9 (ambele boolean),
    //   codul COMPILEAZĂ. Filmul se creează. Doar că `title` primește genul și
    //   `genre` primește titlul. Compilatorul nu te poate ajuta aici.
    //
    // FORMATARE: în G1096 lista de parametri este ruptă pe două linii, a doua aliniată
    //   sub primul parametru. În G1097 este pe o singură linie. Semantic: identic.
    // ==================================================================================
    public Movie(String title, Date release, String genre, double budget, int duration, float rating, boolean watched, String approval, boolean onWatchlist,
                 String posterUrl) {

        // `this.title` = câmpul clasei; `title` = parametrul.
        // Fără `this.`, linia ar fi `title = title` — auto-atribuire, câmpul rămâne null.
        this.title = title;

        // Același model pentru fiecare dintre cele 10 câmpuri. Toate cele 10 linii
        // sunt identice structural; dacă una lipsește, câmpul rămâne cu valoarea
        // implicită (null / 0 / 0.0 / false) și bug-ul apare abia la afișare.
        this.release = release;
        this.genre = genre;
        this.budget = budget;
        this.duration = duration;
        this.rating = rating;
        this.watched = watched;
        this.approval = approval;
        this.onWatchlist = onWatchlist;
        this.posterUrl = posterUrl;
    }

    // ==================================================================================
    // toString() — CONTRACTUL DE AFIȘARE ÎN LISTĂ
    // ==================================================================================
    // DE CE ESTE OBLIGATORIU AICI:
    //   `ArrayAdapter` cu `android.R.layout.simple_list_item_1` primește un `TextView`
    //   și îl umple cu `item.toString()`. Fără suprascriere, `Object.toString()` ar
    //   întoarce `ro.ase.ie.g1096.model.Movie@a1b2c3d` — adresa din memorie.
    //
    // FLUXUL EXACT:
    //   ListView.getView(position) -> ArrayAdapter.getView(...) -> TextView.setText(
    //   movies.get(position).toString())
    //
    // DE CE `@Override`: compilatorul verifică semnătura. Dacă scrii `tostring()`
    //   cu literă mică, fără adnotare nu primești nicio eroare — doar metoda ta
    //   nu este apelată niciodată.
    //
    // DIFERENȚA FAȚĂ DE G1097: aici `posterUrl` NU apare în textul returnat.
    //   G1097 se termină cu `", poster='" + poster + '\''`. Aici se termină cu
    //   `onWatchlist`. Adăugarea unui câmp în clasă nu îl adaugă automat aici.
    //
    // FORMATUL: generat de IntelliJ cu Alt+Insert -> toString(). `'\''` este un
    //   apostrof escapate, ca să nu închidă literalul de caracter.
    //
    // CE SE VEDE PE ECRAN: nouă câmpuri, pe un singur rând. Urât, dar corect.
    //   Se repară în laboratorul următor cu RecyclerView și un layout de rând.
    // ==================================================================================
    @Override
    public String toString() {

        // Concatenare de String-uri cu `+`. Fiecare `+` creează un obiect nou în memorie.
        // Pentru 9 câmpuri, diferența este neglijabilă; pentru bucle mari s-ar folosi
        // `StringBuilder`.
        return "Movie{" +

                // Câmpurile text sunt încadrate în apostrofuri, ca să se vadă limitele
                // valorii: `title='Inception'`. Fără ele, `title=''` și `genre=''`
                // ar fi indistinguibile de un câmp gol.
                "title='" + title + '\'' +

                // `Date` nu este încadrat în apostrofuri: `toString()`-ul lui produce
                // deja un format lizibil (`Sat Jul 16 00:00:00 GMT+03:00 2010`).
                ", release=" + release +

                // Virgula de la început, nu de la sfârșit: ultimul câmp nu are nevoie
                // de separator, iar `}` se lipește corect.
                ", genre='" + genre + '\'' +
                ", budget=" + budget +
                ", duration=" + duration +
                ", rating=" + rating +
                ", watched=" + watched +
                ", approval='" + approval + '\'' +

                // ULTIMUL CÂMP DIN TEXT — și ultimul din clasă care apare aici.
                // `posterUrl` lipsește. Vezi diferența 29.0.4.
                ", onWatchlist=" + onWatchlist +

                // Acolada de închidere a obiectului, ca text.
                '}';
    }

    // ==================================================================================
    // GETTERI ȘI SETTERI — 20 DE METODE, TOATE MECANICE
    // ==================================================================================
    // DE CE EXISTĂ: câmpurile sunt `private`. Codul din alte pachete (și chiar din
    //   `activities`) nu le poate citi sau scrie direct. Getter-ele și setter-ele
    //   sunt singura interfață.
    //
    // DE CE ATÂT DE MULTE: 10 câmpuri x 2 = 20. Sunt generate automat de IntelliJ
    //   (Alt+Insert -> Getter and Setter). Nu se scriu de mână la examen.
    //
    // CONVENȚIA DE NUME:
    //   - `getX()` pentru obiecte și primitive, CU EXCEPȚIA lui boolean;
    //   - `isX()` pentru boolean — convenția JavaBeans.
    //
    // ORDINEA: câmpurile apar în aceeași ordine ca declarațiile, cu excepția lui
    //   `watched`, care sare peste `approval` și `onWatchlist` — getter-ul lui vine
    //   imediat după `rating`, apoi `approval`, apoi `onWatchlist`, apoi `posterUrl`.
    // ==================================================================================

    // GETTER: întoarce referința la String. String este imutabil, deci nu există
    // risc de modificare din exterior.
    public String getTitle() {
        return title;
    }

    // SETTER: `this.title` = câmpul, `title` = parametrul. Aceeași capcană ca în
    // constructorul cu 10 parametri.
    public void setTitle(String title) {
        this.title = title;
    }

    // GETTER pentru Date. ATENȚIE: întoarce REFERINȚA, nu o copie.
    // RISC: `movie.getRelease().setTime(0)` ar modifica data din obiect fără setter.
    //   O variantă corectă ar fi `return new Date(release.getTime());`.
    public Date getRelease() {
        return release;
    }

    // SETTER pentru Date. Nu validează `null` — un `Movie` cu dată null este acceptat
    // de model și crapă abia în `fillForm`, la `dateFormat.format(null)`.
    public void setRelease(Date release) {
        this.release = release;
    }

    // GETTER pentru gen. Valoarea provine din Spinner, dar modelul nu știe asta.
    public String getGenre() {
        return genre;
    }

    // SETTER pentru gen. Nu verifică dacă valoarea există în `@array/movie_genre`.
    // Validarea este responsabilitatea UI-ului, nu a modelului.
    public void setGenre(String genre) {
        this.genre = genre;
    }

    // GETTER pentru buget. `double` se copiază prin valoare — nu există probleme
    // de aliasing ca la Date.
    public double getBudget() {
        return budget;
    }

    // SETTER pentru buget. Nu respinge valori negative: un buget -5 ar fi acceptat.
    // Validarea ar trebui făcută în `saveMovie`, înainte de apel.
    public void setBudget(double budget) {
        this.budget = budget;
    }

    // GETTER pentru durată, în minute.
    public int getDuration() {
        return duration;
    }

    // SETTER pentru durată. Nu limitează la 0..300 — limita există doar în XML
    // (`android:max="300"`), adică doar în UI.
    public void setDuration(int duration) {
        this.duration = duration;
    }

    // GETTER pentru rating. `float` — nota cu jumătăți de stea.
    public float getRating() {
        return rating;
    }

    // SETTER pentru rating. Parametrul este `float`, exact tipul cerut de
    // `RatingBar.setRating(float)`.
    public void setRating(float rating) {
        this.rating = rating;
    }

    // ==================================================================================
    // DE CE `isWatched()` ȘI NU `getWatched()`
    // ==================================================================================
    // 1. CONVENȚIA JAVABEANS: pentru `boolean`, getter-ul se numește `isX()`, nu `getX()`.
    //    Reflectarea (și framework-urile care citesc proprietăți) caută prefixul `is`.
    // 2. CONSISTENȚA: `isOnWatchlist()` respectă aceeași regulă. Dacă unul ar fi
    //    `getWatched()` și celălalt `isOnWatchlist()`, codul ar fi greu de citit.
    // 3. CODUL DEPINDE DE NUME: `fillForm` apelează `existing.isWatched()`. Dacă ai
    //    scris `getWatched()`, apelul nu compilează — și trebuie schimbat în două locuri.
    // ==================================================================================
    public boolean isWatched() {
        return watched;
    }

    // Setter-ul rămâne `setWatched` — prefixul `set` este același pentru toate tipurile.
    public void setWatched(boolean watched) {
        this.watched = watched;
    }

    // GETTER pentru ghidajul parental („PG-13" etc.).
    public String getApproval() {
        return approval;
    }

    // SETTER pentru ghidaj. Valoarea este textul butonului radio, nu ID-ul lui.
    public void setApproval(String approval) {
        this.approval = approval;
    }

    // GETTER pentru bifa „Watchlist". Prefix `is` — din nou convenția JavaBeans.
    public boolean isOnWatchlist() {
        return onWatchlist;
    }

    // SETTER pentru bifă.
    public void setOnWatchlist(boolean onWatchlist) {
        this.onWatchlist = onWatchlist;
    }

    // ==================================================================================
    // GETTER ȘI SETTER PENTRU POSTER — NUMELE CARE TRĂDEAZĂ GRUPA
    // ==================================================================================
    // Aici se vede diferența 29.0.1 în forma ei cea mai concretă: metodele se numesc
    // `getPosterUrl` / `setPosterUrl`, nu `getPoster` / `setPoster`.
    // `ItemActivity` din G1096 le apelează pe acestea două. Copierea codului din
    // capitolul 22 (scris pentru G1097) produce `cannot find symbol`.
    // ==================================================================================
    public String getPosterUrl() {
        return posterUrl;
    }

    // SETTER pentru poster. Acceptă `null` fără să se plângă.
    public void setPosterUrl(String posterUrl) {
        this.posterUrl = posterUrl;
    }

    // Acolada de închidere a clasei. După ea nu mai există nimic în fișier:
    // nicio clasă internă, niciun `enum`, nicio constantă.
}
```

---

## 29.3 `MainActivity.java` — lista și navigarea

```java
/*
 * ======================================================================================
 * FIȘIER: MainActivity.java — ECRANUL CU LISTA
 * ======================================================================================
 * CE ESTE: activitatea de start. Ține lista de filme, o afișează cu un `ArrayAdapter`
 *   într-un `ListView` și pornește `ItemActivity` pentru insert sau edit.
 *
 * DE CE EXISTĂ: este singurul loc care deține STAREA aplicației (lista `movies`).
 *   `ItemActivity` este doar un formular care produce un `Movie` și îl trimite înapoi.
 *   Fără `MainActivity`, rezultatul salvat nu ar avea unde să se întoarcă.
 *
 * DE CE DEPINDE:
 *   - `activity_main.xml` — pentru `R.id.main`, `R.id.listView`, `R.id.floatingActionButton`.
 *   - `ItemActivity` — clasa pe care o pornește prin `Intent`.
 *   - `Movie` — tipul elementelor din listă.
 *   - `androidx.activity.result.*` — pentru `registerForActivityResult`.
 *
 * CINE DEPINDE DE EL:
 *   `AndroidManifest.xml` îl declară ca LAUNCHER. `ItemActivity` îi citește
 *   constantele `MOVIE_EXTRA` și `POSITION_EXTRA`.
 *
 * CE NU FACE:
 *   - Nu validează nimic: acceptă orice `Movie` întors de formular.
 *   - Nu persistă lista: la rotire sau la moartea procesului, lista se pierde.
 *   - Nu are layout de rând propriu: folosește `android.R.layout.simple_list_item_1`.
 *   - Nu încarcă postere: URL-ul rămâne text în model.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   Aplicația ar porni direct într-un formular fără listă. `MOVIE_EXTRA` și
 *   `POSITION_EXTRA` nu ar exista, deci `ItemActivity` nu ar compila.
 * ======================================================================================
 */

// Pachetul `activities` — ecranele. Separat de `model`, ca să nu amestece
// tipurile de date cu cele de UI.
package ro.ase.ie.g1096.activities;

// ======================================================================================
// IMPORTURI — GRUPATE PE SURSĂ
// ======================================================================================
// android.*        — clase din framework (Intent, Bundle, View, widget-uri)
// androidx.*       — biblioteci Jetpack (AppCompat, EdgeToEdge, insets, activity result)
// com.google.*     — Material Components (FloatingActionButton)
// java.util.*      — colecții și date
// ro.ase.ie.g1096  — modelul și clasa R generată
//
// ÎN G1096, DOUĂ IMPORTURI SUNT MOARTE: `java.math.BigDecimal` și
// `android.widget.Toast`. În G1097 moarte sunt `java.util.Date` și `Toast`.
// Vezi diferența 29.0.5.
// ======================================================================================

// Intent: obiectul care descrie „ce activitate pornești" și ce date duce cu ea.
import android.content.Intent;

// Bundle: sacul de stare salvat de sistem (folosit aici doar în semnătura lui onCreate).
import android.os.Bundle;

// View: clasa de bază pentru orice element de UI. Apare în semnăturile listener-ilor.
import android.view.View;

// AdapterView: clasa de bază pentru ListView/Spinner. Aici doar pentru OnItemClickListener.
import android.widget.AdapterView;

// ArrayAdapter: puntea dintre `List<Movie>` și rândurile din ListView.
import android.widget.ArrayAdapter;

// ListView: widget-ul care afișează lista derulabilă.
import android.widget.ListView;

// Toast: mesaje scurte. Importat în sursă, dar NEUTILIZAT în acest fișier.
// Face parte din diferența 29.0.5 — apare mort în ambele grupe.
import android.widget.Toast;

// EdgeToEdge: activează desenarea sub barele de sistem (status + navigare).
import androidx.activity.EdgeToEdge;

// ActivityResult: rezultatul întors de activitatea secundară (cod + Intent).
import androidx.activity.result.ActivityResult;

// ActivityResultCallback: interfața cu o singură metodă, apelată la întoarcere.
import androidx.activity.result.ActivityResultCallback;

// ActivityResultLauncher: obiectul care pornește activitatea și ține legătura cu callback-ul.
import androidx.activity.result.ActivityResultLauncher;

// ActivityResultContracts: contractele predefinite (aici, StartActivityForResult).
import androidx.activity.result.contract.ActivityResultContracts;

// AppCompatActivity: activitatea de bază cu suport pentru teme Material și ActionBar.
import androidx.appcompat.app.AppCompatActivity;

// Insets: valorile în pixeli ale barelor care acoperă conținutul.
import androidx.core.graphics.Insets;

// ViewCompat: versiunea compatibilă a API-urilor de View (insets pe orice API).
import androidx.core.view.ViewCompat;

// WindowInsetsCompat: descrierea insets-urilor, independent de versiunea Android.
import androidx.core.view.WindowInsetsCompat;

// FloatingActionButton: butonul rotund din colțul dreapta-jos.
import com.google.android.material.floatingactionbutton.FloatingActionButton;

// BigDecimal: numere zecimale cu precizie EXACTĂ. Importat în sursă, dar NEUTILIZAT.
// DIFERENȚA FAȚĂ DE G1097: acolo acest import nu există; în schimb există `java.util.Date`,
//   și el nefolosit. Aici `Date` nici nu este importat — și nu este nevoie, pentru că
//   numele `Date` nu apare niciodată în fișier; `getTime()` este pasat direct mai departe.
import java.math.BigDecimal;

// ArrayList: implementarea concretă a listei.
import java.util.ArrayList;

// Calendar: câmpurile de dată (YEAR, MONTH, DAY_OF_MONTH) și constantele lunilor.
import java.util.Calendar;

// GregorianCalendar: constructorul rapid „an, lună, zi" folosit în datele demo.
import java.util.GregorianCalendar;

// List: interfața de listă. Câmpul este declarat `List`, nu `ArrayList`.
import java.util.List;

// Clasa R, generată la build din toate fișierele din `res/`. Fără ea, `R.id.listView`
// nu ar exista ca simbol.
import ro.ase.ie.g1096.R;

// Modelul de date — singura dependență către `model`.
import ro.ase.ie.g1096.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: CINE DEȚINE STAREA ȘI CINE O AFIȘEAZĂ
 * ======================================================================================
 *
 * 1. UN SINGUR PROPRIETAR AL LISTEI
 *    `movies` este câmp de instanță în `MainActivity`. `ItemActivity` nu are nicio
 *    referință la ea. Formularul produce un `Movie` și îl trimite înapoi prin
 *    `setResult`; abia `MainActivity` decide ce face cu el (`add` sau `set`).
 *    Aceasta este separarea care face fluxul ușor de urmărit.
 *
 * 2. `final` NU ÎNSEAMNĂ IMUTABIL
 *    `private final List<Movie> movies = new ArrayList<>();`
 *    `final` blochează REATRIBUIREA referinței (`movies = new ArrayList<>()` nu
 *    compilează), dar NU blochează modificarea conținutului. `movies.add(...)` și
 *    `movies.set(...)` sunt perfect legale. Este exact ce vrem: aceeași listă,
 *    mereu, cu conținut care se schimbă.
 *
 * 3. ADAPTERUL ȚINE REFERINȚA, NU O COPIE
 *    `new ArrayAdapter<>(this, ..., movies)` primește lista prin referință. De aceea
 *    `movies.add(movie)` este vizibil pentru adapter — dar numai după
 *    `notifyDataSetChanged()`. ListView nu observă lista singur.
 *
 * 4. DOUĂ MODURI, UN SINGUR FORMULAR
 *    - FAB  -> `Intent` FĂRĂ extra-uri -> `ItemActivity` în modul INSERT.
 *    - Rând -> `Intent` CU `MOVIE_EXTRA` și `POSITION_EXTRA` -> modul EDIT.
 *    `ItemActivity` decide modul după `existing != null`, nu după un flag separat.
 *
 * 5. CICLUL DE VIAȚĂ AL LISTEI
 *    Lista trăiește cât activitatea. La rotire, Android distruge și recreează
 *    activitatea, iar `movies` se reinițializează cu cele 3 filme demo. Nu există
 *    `onSaveInstanceState`, deci filmele adăugate se pierd. Vezi RISC mai jos.
 * ======================================================================================
 */

// `extends AppCompatActivity` — activitatea de bază AndroidX. Oferă `setContentView`,
// `findViewById`, `getIntent`, `setResult`, `finish`, `RESULT_OK`.
public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // CONSTANTELE DE PROTOCOL DINTRE CELE DOUĂ ACTIVITĂȚI
    // ==================================================================================
    // `protected static final` = constantă de clasă, vizibilă în subclase și în pachet.
    // `ItemActivity` este în ACELAȘI pachet (`ro.ase.ie.g1096.activities`), deci ar
    // funcționa și fără `protected`. Este declarat așa din obișnuință.
    //
    // ATENȚIE — CAPCANĂ FINĂ: `static final String` cu valoare literală este o
    // CONSTANTĂ DE COMPILARE. Compilatorul o INLINUIEȘTE în fiecare clasă care o
    // folosește. Dacă schimbi „movie" în „film" și recompilezi doar MainActivity,
    // ItemActivity compilat anterior păstrează „movie" în bytecode. Se rezolvă cu
    // un clean build. La examen nu se cere, dar explică de ce constantele publice
    // se schimbă rar.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";

    // Butonul rotund „+". Tipul este clasa Material, nu `ImageButton`.
    private FloatingActionButton fabInsert;

    // Lista derulantă. Umple tot ecranul; FAB-ul plutește peste ea.
    private ListView listView;

    // Launcher-ul de rezultat. NU este inițializat aici — primește valoare în `onCreate`,
    // DUPĂ `initListeners()`. Vezi explicația de la `initListeners`.
    private ActivityResultLauncher<Intent> launcher;

    // Lista de filme — singura stare a aplicației.
    // `final` = referința nu se schimbă niciodată; conținutul, da.
    // `new ArrayList<>()` = diamond operator; tipul se deduce din declarație.
    private final List<Movie> movies = new ArrayList<>();

    // Adapterul care leagă lista de ListView. Tipul generic este `Movie`, deci
    // `getItem(position)` întoarce `Movie`, nu `Object`.
    private ArrayAdapter<Movie> movieAdapter;

    // ==================================================================================
    // onCreate — ORDINEA CONTEAZĂ
    // ==================================================================================
    // CE FACE: construiește ecranul, populează lista demo, creează adapterul, leagă
    //   controalele de cod, atașează listenerii și înregistrează launcher-ul.
    // CUM: 1. super 2. EdgeToEdge 3. setContentView 4. insets 5. date demo
    //   6. adapter 7. findViewById 8. listeneri 9. launcher.
    // RISC: fiecare pas depinde de cel dinainte. `findViewById` înainte de
    //   `setContentView` întoarce null; `setAdapter` înainte de `new ArrayAdapter`
    //   ar da NullPointerException.
    // REF: exact aceeași ordine în G1097 (capitolul 22, secțiunea 22.2).
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. Lansează lanțul de inițializare al clasei de bază. OBLIGATORIU primul.
        //    Fără el, `AppCompat` nu își instalează delegate-ul și tema nu se aplică.
        super.onCreate(savedInstanceState);

        // 2. Activează desenarea edge-to-edge: conținutul intră sub status bar și
        //    sub bara de navigare. Consecința: trebuie să ne ocupăm noi de padding,
        //    altfel primul rând de text stă sub ceas.
        EdgeToEdge.enable(this);

        // 3. Umflă arborele de view-uri din `activity_main.xml`. Din acest moment
        //    `findViewById` poate găsi ceva. Înainte de acest apel, întoarce null.
        setContentView(R.layout.activity_main);

        // 4. Corectează padding-ul pentru barele de sistem.
        //    `findViewById(R.id.main)` = FrameLayout-ul rădăcină din XML.
        //    Lambda-ul este `View.OnApplyWindowInsetsListener` (interfață funcțională).
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. Extrage dimensiunile barelor de sistem: status bar + navigation bar.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Aplică-le ca padding pe containerul rădăcină. Copiii se înghesuie
            //     automat înăuntru; nu trebuie să îi atingem pe fiecare.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. Întoarce `insets` NEconsumat, ca să ajungă și la copii.
            //     Dacă ai returna `WindowInsetsCompat.CONSUMED`, nimeni altcineva
            //     nu ar mai primi informația.
            return insets;
        });

        // 5. Pune în listă cele 3 filme demo. Se face ÎNAINTE de crearea adapterului,
        //    ca adapterul să numere de la început 3 elemente. Dacă ai face-o după,
        //    ar funcționa la fel (adapterul ține referința), dar ar fi nevoie de
        //    `notifyDataSetChanged()` ca să redeseneze.
        addSampleMovies();

        // 6. Creează adapterul.
        //    `this` = Context (activitatea).
        //    `android.R.layout.simple_list_item_1` = layout-ul de rând din FRAMEWORK,
        //      nu din aplicație. Conține un singur TextView cu id `android.R.id.text1`.
        //      De aceea rândul afișează `toString()`-ul modelului.
        //    `movies` = sursa de date, prin referință.
        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

        // 7. Leagă câmpurile Java de view-urile din XML.
        initControls();

        // 8. Atașează listenerii. Aici `launcher` este încă `null`, dar este OK:
        //    listenerii citesc câmpul abia la CLICK, iar până atunci pasul 9 l-a setat.
        initListeners();

        // 9. Înregistrează contractul de rezultat. TREBUIE apelat înainte ca
        //    activitatea să ajungă în starea STARTED, deci în `onCreate` este locul
        //    corect. Întoarce un `ActivityResultLauncher<Intent>`.
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // Callback-ul: o clasă anonimă care implementează interfața cu o metodă.
                // Se execută pe thread-ul principal, după ce activitatea secundară
                // s-a închis și aceasta a revenit în prim-plan.
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // FILTRUL 1: a întors ceva util? `RESULT_OK` este -1.
                        // Dacă utilizatorul a apăsat Back, codul este RESULT_CANCELED (0)
                        // și nu facem nimic — lista rămâne neatinsă.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // `getData()` = Intent-ul construit de ItemActivity în `saveMovie()`.
                            // Poate fi null teoretic; aici RESULT_OK garantează că nu este.
                            Intent intent = o.getData();

                            // Scoate obiectul serializat. ATENȚIE: este O COPIE.
                            // `getSerializableExtra(String)` este DEPRECAT din API 33;
                            // varianta modernă este `IntentCompat.getSerializableExtra(...)`,
                            // folosită deja în ItemActivity. Aici a rămas varianta veche —
                            // inconsistență reală între cele două fișiere.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // A doua informație din Intent: poziția. Default -1 = „nu există".
                            // -1 este convenția aplicației pentru „mod insert".
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // RAMURA 1: poziția lipsește -> film NOU.
                            if(position == -1)
                            {
                                // Adaugă la sfârșitul listei.
                                movies.add(movie);

                                // Anunță adapterul. Fără acest apel, ListView nu știe
                                // că lista are un element mai mult și nu redesenează.
                                movieAdapter.notifyDataSetChanged();
                            }
                            // RAMURA 2: poziția există -> ÎNLOCUIRE, nu adăugare.
                            else
                            {
                                // `set` suprascrie elementul de pe poziția dată.
                                // Dacă ai folosi `add`, ai avea un duplicat.
                                movies.set(position, movie);
                                movieAdapter.notifyDataSetChanged();
                            }
                        }
                    }
                });
    }

    // ==================================================================================
    // initListeners — CE SE ÎNTÂMPLĂ LA APĂSARE
    // ==================================================================================
    // CE FACE: atașează două comportamente — FAB-ul pornește formularul gol, click-ul
    //   pe rând pornește formularul plin.
    // CUM: 1. `fabInsert.setOnClickListener` 2. `listView.setOnItemClickListener`.
    // RISC: `launcher` este încă null când rulează această metodă. Este sigur pentru
    //   că listenerii sunt executate abia după `onCreate`, când `launcher` are valoare.
    // REF: același pattern de clase anonime ca în `ItemActivity.initListeners()`.
    // ==================================================================================
    private void initListeners() {

        // Clasă anonimă care implementează `View.OnClickListener`.
        // `new View.OnClickListener() { ... }` = „un obiect care știe doar să reacționeze
        // la click". Nu are nume, nu se refolosește.
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // `MainActivity.this` = Context-ul activității.
                // `this` singur ar fi listener-ul (clasa anonimă), nu o activitate —
                // iar constructorul `Intent(Context, Class)` ar primi tipul greșit.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // FĂRĂ extra-uri! Absența lui `MOVIE_EXTRA` este exact semnalul
                // pe care `ItemActivity` îl citește ca „mod insert".
                launcher.launch(intent);
            }
        });

        // Listener pentru click pe un rând. Interfața are 4 parametri:
        //   parent   = ListView-ul
        //   view     = rândul apăsat (un TextView, aici)
        //   position = indexul în listă (0-based)
        //   id       = id-ul rândului; pentru ArrayAdapter este egal cu position
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                // Același target ca la FAB — dar de data asta ducem și date.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // Obiectul de pe rândul apăsat. Este serializat automat la `launch`.
                // `movies.get(position)` întoarce REFERINȚA din listă; `putExtra`
                // o serializează într-o copie. Originalul rămâne neatins.
                intent.putExtra(MOVIE_EXTRA, movies.get(position));

                // Poziția, ca `ItemActivity` să știe ce rând să înlocuiască la salvare.
                intent.putExtra(POSITION_EXTRA, position);

                // Pornește activitatea prin launcher, nu prin `startActivity`.
                // Diferența: launcher-ul garantează că rezultatul ajunge în callback.
                launcher.launch(intent);
            }
        });
    }

    // ==================================================================================
    // initControls — FINDVIEWBYID, PUR ȘI SIMPLU
    // ==================================================================================
    // CE FACE: leagă cele două view-uri de câmpurile Java și instalează adapterul.
    // CUM: 1. FAB 2. ListView 3. setAdapter.
    // RISC: `findViewById` întoarce null dacă ID-ul nu există în layout-ul curent.
    //   Aici toate cele trei ID-uri există în `activity_main.xml`.
    // REF: în `ItemActivity`, aceeași metodă are 13 linii, nu 3.
    // ==================================================================================
    private void initControls() {

        // ID-ul din XML este `@+id/floatingActionButton`; câmpul se numește `fabInsert`.
        // Numele diferă, ID-ul contează.
        fabInsert = findViewById(R.id.floatingActionButton);

        // ID-ul din XML este `@+id/listView`.
        listView = findViewById(R.id.listView);

        // Instalează adapterul. Din acest moment ListView are ce desena.
        // `android:entries="@array/items"` din XML este IGNORAT de acum înainte.
        listView.setAdapter(movieAdapter);
    }

    // ==================================================================================
    // addSampleMovies — DATELE DEMO
    // ==================================================================================
    // CE FACE: adaugă 3 filme în listă, ca ecranul să nu pornească gol.
    // CUM: 3 apeluri ale constructorului cu 10 parametri, fiecare cu `new GregorianCalendar`.
    // RISC: ordinea argumentelor este POZIȚIONALĂ. Inversarea a două argumente de
    //   același tip (String/String sau boolean/boolean) compilează și produce date greșite.
    // REF: constructorul este documentat în 29.2; aici se vede SINGURUL lui consumator.
    // ==================================================================================
    private void addSampleMovies() {

        // FILMUL 1 — „Inception".
        // `new Movie(` deschide apelul; fiecare argument este pe linia lui, ca să se
        // vadă poziția. Ordinea este cea din semnătură: title, release, genre, budget,
        // duration, rating, watched, approval, onWatchlist, posterUrl.
        movies.add(new Movie(
                "Inception",                                              // 1. title
                // 2. release: `GregorianCalendar(an, lună, zi)` — LUNA ESTE 0-BASED!
                //    `Calendar.JULY` = 6, nu 7. Dacă ai scrie `new GregorianCalendar(2010, 7, 16)`
                //    ai obține 16 AUGUST. `getTime()` transformă Calendar în Date.
                new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),
                "Sci-Fi",                                                 // 3. genre
                160000000,                                                // 4. budget (int -> double)
                148,                                                      // 5. duration (minute)
                4.5f,                                                     // 6. rating (float!)
                true,                                                     // 7. watched
                "PG-13",                                                  // 8. approval
                false,                                                    // 9. onWatchlist
                "https://example.com/posters/inception.jpg"));            // 10. posterUrl

        // FILMUL 2 — „Toy Story".
        // Aceeași structură. `4f` este un `float` literal; fără `f` ar fi `double`
        // și constructorul nu ar găsi potrivirea pentru parametrul `float rating`.
        movies.add(new Movie(
                "Toy Story",
                new GregorianCalendar(1995, Calendar.NOVEMBER, 22).getTime(),
                "Animation",
                30000000,
                81,
                4f,
                true,
                "G",
                false,
                "https://example.com/posters/toy-story.jpg"));

        // FILMUL 3 — „The Matrix".
        // Singurul cu `watched = false` și `onWatchlist = true`: cele două booleene
        // sunt independente, iar acest film demonstrează exact asta.
        movies.add(new Movie(
                "The Matrix",
                new GregorianCalendar(1999, Calendar.MARCH, 31).getTime(),
                "Action",
                63000000,
                136,
                5f,
                false,
                "R",
                true,
                "https://example.com/posters/the-matrix.jpg"));
    }

    // ==================================================================================
    // CE LIPSEȘTE DIN ACEST FIȘIER — ȘI SE CERE LA EXAMEN
    // ==================================================================================
    // - `onSaveInstanceState(Bundle)`: nu există. La rotire, activitatea este
    //   recreată, `movies` se reinițializează, iar filmele adăugate DISPAR.
    //   RISC REAL, nu teoretic: întoarce telefonul după ce ai adăugat un film.
    // - `onResume()` / `onStart()`: nu există. Nu e nevoie; totul se face în `onCreate`.
    // - `onDestroy()`: nu există. Nu există resurse de eliberat.
    // - Meniu, `OptionsMenu`, `Toolbar`: nu există. Ecranul este doar listă + FAB.
    // ==================================================================================
}
```

---

## 29.4 `ItemActivity.java` — formularul

```java
/*
 * ======================================================================================
 * FIȘIER: ItemActivity.java — FORMULARUL DE ADAUGĂ / EDITEZĂ
 * ======================================================================================
 * CE ESTE: un ecran cu 13 controale, care citește valorile din ele, construiește un
 *   `Movie` și îl trimite înapoi în `MainActivity` printr-un `Intent` de rezultat.
 *
 * DE CE EXISTĂ: este SINGURUL loc care știe să transforme widget-uri în model.
 *   `MainActivity` nu atinge niciun `EditText`; primește un `Movie` gata făcut.
 *
 * DE CE DEPINDE:
 *   - `activity_item.xml` — pentru cele 13 ID-uri (`etTitle` ... `btnMovieAction`).
 *   - `MainActivity` — pentru constantele `MOVIE_EXTRA` și `POSITION_EXTRA`.
 *   - `Movie` — tipul pe care îl construiește.
 *   - `IntentCompat` — pentru citirea tipată a extra-ului serializabil.
 *
 * CINE DEPINDE DE EL:
 *   `MainActivity` (îl pornește prin `launcher`), `AndroidManifest.xml` (îl declară).
 *
 * CE NU FACE:
 *   - Nu validează nimic: un buget gol produce `NumberFormatException`, nu un mesaj.
 *   - Nu persistă nimic: nu scrie în fișier, în `SharedPreferences` sau în bază de date.
 *   - Nu încarcă posterul: `etPoster` este doar text.
 *   - Nu știe ce se întâmplă cu `Movie`-ul după `finish()`.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   Aplicația ar avea listă, dar niciun mod de a adăuga sau modifica un film.
 *   FAB-ul ar porni o activitate inexistentă -> `ActivityNotFoundException`.
 * ======================================================================================
 */

// Același pachet ca `MainActivity` — de aceea poate folosi constantele ei
// fără import și fără calificare completă.
package ro.ase.ie.g1096.activities;

// ======================================================================================
// IMPORTURI — 24 DE NUME, DINTRE CARE UNUL MORT
// ======================================================================================
// android.widget.*   — cele 13 tipuri de widget-uri + interfețele lor de listener
// androidx.*         — AppCompat, EdgeToEdge, insets, IntentCompat, @NonNull
// com.google.*       — MaterialSwitch (singurul widget Material din cod)
// java.text.*        — SimpleDateFormat și excepția ei
// java.util.*        — Calendar, Date, Locale
//
// MORT: `android.widget.Switch`. Câmpul este `MaterialSwitch`, care extinde
//   `SwitchCompat`, NU `android.widget.Switch`. Vezi diferența 29.0.6.
// ======================================================================================

// DatePickerDialog: dialogul de calendar care apare la click pe câmpul de dată.
import android.app.DatePickerDialog;

// Intent: obiectul de rezultat, construit în `saveMovie()`.
import android.content.Intent;

// Bundle: doar în semnătura lui onCreate.
import android.os.Bundle;

// View: tipul parametrului din OnClickListener.
import android.view.View;

// Button: tipul câmpului `btMovieAction`.
import android.widget.Button;

// CheckBox: tipul câmpului `cbonWatchList`.
import android.widget.CheckBox;

// CompoundButton: clasa de bază pentru Switch/CheckBox; interfața de listener este aici.
import android.widget.CompoundButton;

// DatePicker: primul parametru al lui `onDateSet`.
import android.widget.DatePicker;

// EditText: tipul câmpurilor `etTitle`, `etRelease`, `etBudget`, `etPoster`.
import android.widget.EditText;

// RadioButton: tipul în care se face CAST fiecare copil al lui `rgApproval`.
import android.widget.RadioButton;

// RadioGroup: containerul care garantează selecție unică între butoanele radio.
import android.widget.RadioGroup;

// RatingBar: tipul câmpului `rbRating`.
import android.widget.RatingBar;

// SeekBar: tipul câmpului `sbDuration`.
import android.widget.SeekBar;

// Spinner: tipul câmpului `spGenre`.
import android.widget.Spinner;

// Switch: IMPORT MORT. Niciun nume `Switch` nu apare în fișier.
// DANGER! Dacă ai „repara" importul folosindu-l — `private Switch swWatched;` —
//   `findViewById(R.id.swWatched)` ar întoarce un `MaterialSwitch`, care NU este
//   subclasă a lui `android.widget.Switch`, și ai lua `ClassCastException` la runtime.
import android.widget.Switch;

// TextView: tipul câmpurilor `tvDurationValue` și `tvWatchedValue`.
import android.widget.TextView;

// EdgeToEdge: desenare sub barele de sistem.
import androidx.activity.EdgeToEdge;

// NonNull: adnotare pe parametrul lui `onCheckedChanged`. Doar documentație pentru
//   compilator și pentru lint; nu schimbă bytecode-ul.
import androidx.annotation.NonNull;

// AppCompatActivity: clasa de bază.
import androidx.appcompat.app.AppCompatActivity;

// IntentCompat: variantă compatibilă a citirii extra-urilor. `getSerializableExtra(
//   Intent, String, Class<T>)` este varianta tipată, care nu mai aruncă
//   ClassCastException și funcționează pe toate API-urile.
import androidx.core.content.IntentCompat;

// Insets / ViewCompat / WindowInsetsCompat: aceleași trei clase ca în MainActivity,
// pentru același listener de padding.
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

// MaterialSwitch: widget-ul Material pentru comutator. Extinde SwitchCompat,
// care extinde CompoundButton — de aceea listener-ul este `CompoundButton.OnCheckedChangeListener`.
import com.google.android.material.materialswitch.MaterialSwitch;

// ParseException: excepția aruncată de `SimpleDateFormat.parse` pe text invalid.
import java.text.ParseException;

// SimpleDateFormat: formatează și parsează „dd/MM/yyyy".
import java.text.SimpleDateFormat;

// Calendar: tipul lui `releaseCal` și constantele YEAR / MONTH / DAY_OF_MONTH.
import java.util.Calendar;

// Date: tipul returnat de `dateFormat.parse(...)`.
import java.util.Date;

// Locale: formatarea depinde de localizare (nume de luni, separatori).
import java.util.Locale;

// Clasa R — pentru cele 13 ID-uri.
import ro.ase.ie.g1096.R;

// Modelul construit de formular.
import ro.ase.ie.g1096.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: FORMULARUL CA FABRICĂ ȘI CELE DOUĂ MODURI
 * ======================================================================================
 *
 * 1. UN SINGUR ECRAN, DOUĂ MODURI
 *    Nu există `AddActivity` și `EditActivity`. Există un `ItemActivity` care se
 *    comportă diferit în funcție de ce primește în `Intent`:
 *
 *      Intent FĂRĂ MOVIE_EXTRA   -> mod INSERT: formular gol, buton „Save Movie"
 *      Intent CU    MOVIE_EXTRA  -> mod EDIT:   formular plin, buton „Update Movie"
 *
 *    Discriminantul este `existing != null`, nu un flag boolean separat. Mai puțin
 *    cod, mai puține locuri în care flag-ul poate fi greșit.
 *
 * 2. DIRECȚIA DATELOR
 *    MainActivity --(Intent cu Movie)--> ItemActivity --(formular)--> Movie nou
 *    ItemActivity --(setResult cu Movie nou)--> MainActivity
 *    Datele curg într-un singur sens, o singură dată. Nu există observatori,
 *    nu există callback-uri intermediare.
 *
 * 3. `Intent`-UL DE REZULTAT NU ESTE PORNIT NICĂIODATĂ
 *    `new Intent()` fără target nu descrie o navigație. Este doar un container
 *    pentru `putExtra`, pe care `setResult` îl trimite înapoi apelantului.
 *    Confuzia clasică: „de ce nu are `IntentActivity.class`?" — pentru că nu
 *    pornește nimic.
 *
 * 4. CINE ESTE SURSA DE ADEVĂR PENTRU DATĂ
 *    NU textul din `etRelease`. Ci `releaseCal`, un `Calendar`. Textul este doar
 *    o reprezentare; calendarul este valoarea. `saveMovie()` citește din calendar.
 *    Consecința: dacă uiți să sincronizezi calendarul cu textul, salvezi altă dată.
 *    Aici EXISTĂ această uitare — vezi BUG 2.
 *
 * 5. CICLUL DE VIAȚĂ AL UNUI FORMULAR
 *    onCreate -> (utilizatorul completează) -> saveMovie -> setResult -> finish
 *    -> onPause -> onStop -> onDestroy. Nu există salvare automată, nu există
 *    „draft". Dacă apeși Back, tot ce ai tastat se pierde, fără avertisment.
 * ======================================================================================
 */

// Aceeași clasă de bază ca MainActivity.
public class ItemActivity extends AppCompatActivity {

    // ==================================================================================
    // CELE 13 CÂMPURI DE WIDGET — ORDINEA URMEAZĂ FORMULARUL, NU XML-UL
    // ==================================================================================
    // Sunt declarate în ordinea în care apar pe ecran: titlu, dată, gen, buget,
    // durată, rating, ghidaj, watchlist, switch, poster, buton, două etichete.
    // Tipul fiecăruia este exact clasa din XML — `EditText`, nu `TextInputEditText`,
    // pentru că `TextInputEditText` este subclasă a lui `EditText`.
    // ==================================================================================

    // Titlul filmului. `TextInputEditText` din XML este un `EditText`, deci merge.
    private EditText etTitle;

    // Data lansării. NU se tastează: click-ul deschide `DatePickerDialog`.
    private EditText etRelease;

    // Genul, ales din `@array/movie_genre`.
    private Spinner spGenre;

    // Bugetul, tastat pe tastatură numerică cu zecimale.
    private EditText etBudget;

    // Durata, aleasă cu slider-ul 0..300.
    private SeekBar sbDuration;

    // Nota, 0..5 stele cu pas de 0.5.
    private RatingBar rbRating;

    // Grupul de butoane radio pentru ghidajul parental.
    private RadioGroup rgApproval;

    // Bifa „Watchlist". Numele câmpului are un `b` în plus față de ID: `cbonWatchList`.
    private CheckBox cbonWatchList;

    // Comutatorul „Recommended". TIPUL ESTE MATERIAL, nu `android.widget.Switch`.
    private MaterialSwitch swWatched;

    // URL-ul posterului, tastat cu tastatură de tip URI.
    private EditText etPoster;

    // Butonul de salvare. Textul lui se schimbă în modul edit.
    private Button btMovieAction;

    // Eticheta „148 min." de lângă slider — se actualizează la fiecare mișcare.
    private TextView tvDurationValue;

    // Eticheta „Yes"/„No" de lângă switch — se actualizează la fiecare comutare.
    private TextView tvWatchedValue;

    // ==================================================================================
    // STARE INTERNĂ — TREI CÂMPURI CARE NU SUNT WIDGET-URI
    // ==================================================================================
    // `position` = modul. -1 înseamnă insert; orice altă valoare înseamnă edit.
    //   Este SINGURUL flag de mod din clasă. Nu există `boolean isEdit`.
    //
    // `releaseCal` = sursa de adevăr pentru dată. Inițializat cu „acum", ca dialogul
    //   să pornească de undeva chiar dacă utilizatorul nu a ales nimic.
    //
    // `dateFormat` = formatatorul comun pentru afișare și parsare. `final` pentru că
    //   referința nu se schimbă; `SimpleDateFormat` este mutabilă intern, dar aici
    //   este folosită doar pe thread-ul principal.
    // ==================================================================================
    private int position = -1;   // -1 = insert mode
    private Calendar releaseCal = Calendar.getInstance();
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    // ==================================================================================
    // onCreate — CONSTRUIEȘTE FORMULARUL, APOI ÎL UMPLE DACĂ E CAZUL
    // ==================================================================================
    // CE FACE: umflă layout-ul, leagă cele 13 view-uri, atașează cei 4 listeneri,
    //   apoi citește `Intent`-ul și decide dacă formularul pornește gol sau plin.
    // CUM: 1. super 2. EdgeToEdge 3. setContentView 4. insets 5. initControls
    //   6. initListeners 7. getIntent 8. citire extra 9. dacă există, fillForm + texte.
    // RISC: ordinea 5-6-9 este esențială. `fillForm` apelează `setChecked` și
    //   `setProgress`, care declanșează listenerii. Dacă listenerii nu ar fi atașați
    //   înainte, etichetele `tvWatchedValue` și `tvDurationValue` ar rămâne pe
    //   valorile din XML („No", „0 min").
    // REF: aceeași ordine ca în MainActivity.onCreate, plus pasul de citire a Intent-ului.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. Lanțul clasei de bază. Obligatoriu primul.
        super.onCreate(savedInstanceState);

        // 2. Desenare sub barele de sistem.
        EdgeToEdge.enable(this);

        // 3. Umflă `activity_item.xml`. Din acest moment `findViewById` găsește view-urile.
        setContentView(R.layout.activity_item);

        // 4. Padding pentru barele de sistem, pe rădăcina `R.id.main` (ScrollView-ul).
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // 5. Leagă cele 13 câmpuri de view-uri.
        initControls();

        // 6. Atașează cei 4 listeneri. TREBUIE înainte de `fillForm`, pentru că
        //    `fillForm` va declanșa `onCheckedChanged` și `onProgressChanged`.
        initListeners();

        // 7. Ia Intent-ul care a pornit activitatea.
        //    - La insert: Intent gol, construit de FAB.
        //    - La edit: Intent cu MOVIE_EXTRA și POSITION_EXTRA, construit de click-ul pe rând.
        Intent intent = getIntent();

        // 8. Citește obiectul serializat, în varianta TIPATĂ.
        //    `IntentCompat.getSerializableExtra(intent, key, Movie.class)` întoarce
        //    direct `Movie` sau `null`, fără cast manual și fără metoda deprecată.
        //    ATENȚIE: obiectul primit este O COPIE deserializată, nu originalul din listă.
        Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);

        // 9. Discriminantul de mod: există obiect sau nu.
        if (existing != null) {

            // 9a. Reține poziția pentru `saveMovie`. Dacă lipsește, rămâne -1 și
            //     `saveMovie` ar trimite un film nou în loc să înlocuiască.
            position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);

            // 9b. Umple cele 13 controale cu valorile filmului.
            fillForm(existing);

            // 9c. `setTitle` este metoda ACTIVITĂȚII (schimbă titlul din ActionBar),
            //     NU `Movie.setTitle`. Aceeași nume, altă clasă — capcană de citire.
            setTitle("Edit movie");

            // 9d. Schimbă textul butonului. Utilizatorul vede că salvează o modificare.
            btMovieAction.setText("Update Movie");
        }
        // Dacă `existing` este null, nu se face nimic: formularul rămâne gol,
        // butonul rămâne „Save Movie" din XML, iar `position` rămâne -1.
    }

    // ==================================================================================
    // fillForm — MODEL -> WIDGET-URI
    // ==================================================================================
    // CE FACE: copiază cele 10 valori ale unui `Movie` în cele 13 controale.
    // CUM: 8 setter-e directe, apoi 2 bucle — una pe Spinner (după TEXT), una pe
    //   RadioGroup (după TEXT).
    // RISC: cele două bucle eșuează SILENȚIOS dacă textul nu se potrivește. Spinner-ul
    //   rămâne pe prima poziție, grupul radio rămâne pe butonul bifat implicit.
    // REF: perechea acestei metode este `saveMovie()` — acolo merge invers, widget -> model.
    // ==================================================================================
    private void fillForm(Movie existing) {

        // Text simplu. `setText` acceptă `null` și afișează câmp gol.
        etTitle.setText(existing.getTitle());

        // Data: `Date` -> text cu `SimpleDateFormat`. ATENȚIE: această linie NU
        // actualizează `releaseCal`. Vezi BUG 2 mai jos.
        etRelease.setText(dateFormat.format(existing.getRelease()));

        // Buget: `double` -> text. `String.valueOf(double)` produce „1.6E8" pentru
        // 160 000 000, nu „160000000". Vezi BUG 3.
        etBudget.setText(String.valueOf(existing.getBudget()));

        // Durata: `int` -> progres pe slider. Valoarea este limitată automat la 0..300.
        // Această linie DECLANȘEAZĂ `onProgressChanged`, care actualizează eticheta.
        sbDuration.setProgress(existing.getDuration());

        // Bifa: `boolean` -> `setChecked`. Declanșează listener-ul doar dacă valoarea
        // se SCHIMBĂ față de starea curentă.
        cbonWatchList.setChecked(existing.isOnWatchlist());

        // Switch-ul: `boolean` -> `setChecked`. Declanșează `onCheckedChanged`,
        // care scrie „Yes"/„No" în `tvWatchedValue`.
        swWatched.setChecked(existing.isWatched());

        // Nota: `float` -> `setRating(float)`. Tipurile se potrivesc exact.
        rbRating.setRating(existing.getRating());

        // Posterul: `String` -> text. Poate fi `null`; `setText(null)` este legal.
        etPoster.setText(existing.getPosterUrl());

        // BUCLA 1 — Spinner-ul nu are „setValue(String)". Are doar „setSelection(index)".
        // Deci căutăm indexul după text, comparând fiecare element cu genul filmului.
        for(int index=0; index<spGenre.getCount(); index++)
        {
            // `getItemAtPosition` întoarce elementul din `@array/movie_genre`.
            // `.equals` pe obiectul din adapter; dacă ar fi null, ar arunca NPE.
            if(spGenre.getItemAtPosition(index).equals(existing.getGenre()))
            {
                // Am găsit genul — selectează-l.
                spGenre.setSelection(index);

                // Ieși din buclă: prima potrivire este suficientă.
                break;
            }
            // Dacă nu se găsește nicio potrivire, spinner-ul rămâne pe poziția 0.
            // RISC: niciun mesaj, nicio eroare. Doar genul afișat este altul.
        }

        // BUCLA 2 — RadioGroup-ul nu are „select by text" nici el.
        // Iterăm peste COPIII grupului, nu peste un array separat.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            // CAST la RadioButton. Funcționează pentru că toți copiii din XML sunt
            // `MaterialRadioButton`, care extinde `RadioButton`.
            // RISC: dacă cineva adaugă un `View` separator în RadioGroup, acest cast
            //   aruncă `ClassCastException` la editare.
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // Compară TEXTUL butonului („G", „PG", „PG-13", „R", „NC-17") cu valoarea.
            if(rb.getText().toString().equals(existing.getApproval()))
            {
                // `check(id)` bifează butonul și îl debifează automat pe celălalt —
                // aceasta este garanția pe care o dă RadioGroup.
                rgApproval.check(rgApproval.getChildAt(index).getId());

                // Ieși din buclă.
                break;
            }
        }
    }

    // ==================================================================================
    // initControls — 13 FINDVIEWBYID, UNUL PENTRU FIECARE ID DIN XML
    // ==================================================================================
    // CE FACE: leagă fiecare câmp Java de view-ul cu ID-ul corespunzător.
    // CUM: 13 atribuiri mecanice. Ordinea urmează ordinea câmpurilor.
    // RISC: un ID greșit -> `findViewById` întoarce null -> `NullPointerException`
    //   la prima utilizare, nu aici. Cea mai greu de depanat clasă de bug-uri.
    // REF: `MainActivity.initControls()` are doar 3 linii; aici sunt 13.
    // ==================================================================================
    private void initControls() {

        // Fiecare linie are aceeași formă: `câmp = findViewById(R.id.id_din_xml);`
        // `findViewById` este generic din API 26: tipul se deduce din câmpul din stânga.
        etTitle = findViewById(R.id.etTitle);
        etRelease = findViewById(R.id.etRelease);
        spGenre = findViewById(R.id.spGenre);
        etBudget = findViewById(R.id.etBudget);
        sbDuration = findViewById(R.id.sbDuration);
        rbRating = findViewById(R.id.rbRating);
        rgApproval = findViewById(R.id.rgApproval);

        // ATENȚIE LA NUME: câmpul este `cbonWatchList`, ID-ul este `cbOnWatchList`.
        // Un `b` în plus în câmp, un `O` mare în ID. Ambele sunt corecte.
        cbonWatchList = findViewById(R.id.cbOnWatchList);

        swWatched = findViewById(R.id.swWatched);
        etPoster = findViewById(R.id.etPoster);

        // Butonul: câmpul `btMovieAction`, ID-ul `btnMovieAction`.
        btMovieAction = findViewById(R.id.btnMovieAction);

        // Cele două etichete care se actualizează din listeneri.
        tvDurationValue = findViewById(R.id.tvDurationValue);
        tvWatchedValue = findViewById(R.id.tvWatchedValue);
    }

    // ==================================================================================
    // initListeners — PATRU COMPORTAMENTE
    // ==================================================================================
    // CE FACE: atașează: click pe dată -> dialog; click pe buton -> salvare;
    //   schimbare switch -> etichetă; mișcare slider -> etichetă.
    // CUM: 4 clase anonime, dintre care una implementează o interfață cu 3 metode.
    // RISC: ordinea contează față de `fillForm` — vezi onCreate, pasul 6.
    // REF: `MainActivity.initListeners()` are 2 listeneri; aici sunt 4.
    // ==================================================================================
    private void initListeners() {

        // LISTENER 1 — click pe câmpul de dată.
        // Un `EditText` nu are „onDateClick"; folosim click-ul generic.
        etRelease.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Deschide dialogul de calendar. Metoda este mai jos.
                showReleaseDatePicker();
            }
        });

        // LISTENER 2 — click pe butonul de salvare.
        btMovieAction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Construiește Movie-ul, îl pune în Intent, setează rezultatul, închide.
                saveMovie();
            }
        });

        // LISTENER 3 — schimbarea switch-ului.
        // Interfața este `CompoundButton.OnCheckedChangeListener`, nu una proprie
        // lui MaterialSwitch: MaterialSwitch este un CompoundButton.
        swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                // Operator ternar: o singură expresie pentru ambele cazuri.
                // `isChecked` este valoarea NOUĂ, nu cea veche.
                tvWatchedValue.setText(isChecked ? "Yes" : "No");
            }
        });

        // LISTENER 4 — slider-ul de durată.
        // Interfața are TREI metode. Toate trebuie implementate; două rămân goale.
        // Nu există metode default într-o interfață Java clasică.
        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // `progress` = valoarea nouă, 0..300.
                // `fromUser` = true dacă vine din degetul utilizatorului, false dacă
                //   vine din `setProgress(...)`. Aici este IGNORAT intenționat:
                //   vrem ca eticheta să fie corectă și când `fillForm` apelează
                //   `setProgress`, nu doar când trage utilizatorul.
                tvDurationValue.setText(progress + " min.");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
                // Gol: nu ne interesează momentul în care începe tragerea.
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                // Gol: nu ne interesează momentul în care se termină tragerea.
                // Aici s-ar putea salva valoarea sau afișa un mesaj, dacă ar fi nevoie.
            }
        });
    }

    // ==================================================================================
    // saveMovie — WIDGET-URI -> MODEL -> INTENT -> REZULTAT
    // ==================================================================================
    // CE FACE: citește cele 13 controale, construiește un `Movie`, îl pune într-un
    //   `Intent` de rezultat împreună cu poziția (dacă există) și închide ecranul.
    // CUM: 1. new Movie() 2. nouă setter-e 3. buclă pe RadioGroup 4. Intent
    //   5. putExtra 6. poziție condiționată 7. setResult 8. finish.
    // RISC: `Double.parseDouble` pe text gol aruncă `NumberFormatException`.
    //   Vezi BUG 1 — este singurul crash reproductibil din aplicație.
    // REF: perechea lui `fillForm`; consumatorul este callback-ul din MainActivity.
    // ==================================================================================
    private void saveMovie() {

        // 1. Obiect gol, umplut imediat cu setter-e. De aceea constructorul fără
        //    parametri este obligatoriu în model.
        Movie movie = new Movie();

        // 2. Cele nouă setter-e care corespund unui widget fiecare.
        //    Ordinea nu contează; doar perechile widget -> setter contează.
        movie.setTitle(etTitle.getText().toString());

        // DATA NU VINE DIN TEXT, ci din calendar. Textul poate fi invalid; calendarul nu.
        // `getTime()` transformă Calendar -> Date.
        movie.setRelease(releaseCal.getTime());

        // Genul: textul selectat în Spinner. `getSelectedItem()` nu este null cât timp
        // spinner-ul are cel puțin un element (valorile din `@array/movie_genre`).
        movie.setGenre(spGenre.getSelectedItem().toString());

        // BUG 1: dacă `etBudget` este gol, `Double.parseDouble("")` aruncă
        // `NumberFormatException`, iar aplicația se închide. Nu există try/catch
        // și nu există verificare `isEmpty()`.
        // Aceeași linie refuză și „1,5" (virgulă zecimală, locale românesc), dar
        // acceptă „1.6E8" (notație științifică).
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));

        // Durata: direct din progres, fără conversie.
        movie.setDuration(sbDuration.getProgress());

        // Nota: `getRating()` întoarce `float`, exact tipul câmpului.
        movie.setRating(rbRating.getRating());

        // Switch-ul: `isChecked()` -> boolean.
        movie.setWatched(swWatched.isChecked());

        // Bifa: `isChecked()` -> boolean. Independentă de switch.
        movie.setOnWatchlist(cbonWatchList.isChecked());

        // Posterul: text liber. Poate fi gol — modelul acceptă.
        movie.setPosterUrl(etPoster.getText().toString());

        // 3. Ghidajul parental: nu are getter direct pe RadioGroup, deci căutăm
        //    butonul bifat. Aceeași buclă ca în `fillForm`, dar cu `isChecked()`.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // Exact un buton este bifat (garanție RadioGroup). Dacă niciunul nu ar fi
            // bifat, `approval` ar rămâne null — dar XML-ul bifează `rbGeneral` implicit.
            if(rb.isChecked())
            {
                // Valoarea salvată este TEXTUL butonului, nu ID-ul.
                movie.setApproval(rb.getText().toString());
                break;
            }
        }

        // 4. Intent FĂRĂ target. Nu pornește nicio activitate: este containerul
        //    rezultatului, citit de callback-ul din MainActivity.
        Intent intent = new Intent();

        // 5. Pune filmul. `putExtra(String, Serializable)` serializează obiectul.
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);

        // 6. Poziția se pune DOAR în modul edit. În modul insert, absența ei este
        //    exact semnalul pe care `MainActivity` îl citește ca „adaugă la sfârșit".
        //    Fără acolade: `if`-ul controlează o singură instrucțiune.
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);

        // 7. Setează codul de rezultat. `RESULT_OK` este -1 — aceeași valoare ca
        //    „poziția lipsește", dar complet nelegată. Aici este cod de rezultat,
        //    acolo este index de listă. Coincidență numerică, nu conflict.
        setResult(RESULT_OK, intent);

        // 8. Închide activitatea. Fără `finish()`, `setResult` nu ajunge niciodată
        //    la apelant, pentru că activitatea ar rămâne deschisă.
        finish();
    }

    // ==================================================================================
    // showReleaseDatePicker — DIALOGUL DE CALENDAR
    // ==================================================================================
    // CE FACE: deschide un `DatePickerDialog` poziționat pe data curentă din
    //   `releaseCal`, iar la confirmare scrie data în calendar ȘI în text.
    // CUM: 1. parsează textul existent (dacă e valid) 2. construiește dialogul
    //   3. la confirmare, actualizează calendarul 4. formatează înapoi în EditText.
    // RISC: dacă textul din câmp a fost tastat manual și este invalid, parse-ul
    //   eșuează silențios și dialogul pornește de la data veche din calendar.
    // REF: `SimpleDateFormat` este folosit și în `fillForm`; aici în direcția inversă.
    // ==================================================================================
    private void showReleaseDatePicker() {

        // Textul curent din câmp. Poate fi gol (formular nou) sau o dată formatată
        // de `fillForm` (mod edit) sau text tastat manual de utilizator.
        String current = etRelease.getText().toString();

        // Parsăm doar dacă există ceva de parsat.
        if (!current.isEmpty()) {
            try {
                // `parse` întoarce `Date` sau aruncă `ParseException`.
                Date parsed = dateFormat.parse(current);

                // `parse` poate întoarce null teoretic; verificăm înainte de folosire.
                if (parsed != null)
                    // Sincronizează calendarul cu textul. Aici se întâmplă legătura
                    // text -> Calendar, care lipsește din `fillForm` (BUG 2).
                    releaseCal.setTime(parsed);
            } catch (ParseException ignored) { }
            // Excepția este IGNORATĂ intenționat: text invalid nu trebuie să blocheze
            // dialogul. Se pornește de la data veche din calendar.
            // RISC: utilizatorul nu află niciodată că textul lui a fost ignorat.
        }

        // Construiește dialogul. Parametrii:
        //   1. `this` = Context
        //   2. listener-ul de confirmare (clasă anonimă)
        //   3-5. anul, luna, ziua de start — LUNA ESTE 0-BASED (`Calendar.MONTH`)
        // `.show()` la final: dialogul nu apare până nu este apelată.
        new DatePickerDialog(
                this,
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {

                        // `month` vine tot 0-based din DatePicker, deci se potrivește
                        // direct cu `Calendar.set(year, month, day)`. Fără conversie.
                        releaseCal.set(year, month, day);

                        // Curăță orice eroare afișată anterior pe câmp. Aici nimic nu
                        // setează vreodată o eroare, dar apelul este defensiv.
                        etRelease.setError(null);

                        // Scrie data înapoi în câmp, în același format „dd/MM/yyyy".
                        etRelease.setText(dateFormat.format(releaseCal.getTime()));
                    }
                },
                // Valorile de start: exact starea curentă a calendarului.
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)
        ).show();
    }

    // ==================================================================================
    // CELE TREI BUG-URI REALE DIN ACEST FIȘIER
    // ==================================================================================
    // BUG 1 — BUGET GOL -> CRASH
    //   `Double.parseDouble("")` aruncă `NumberFormatException`. Utilizatorul apasă
    //   „Save Movie" fără să completeze bugetul, aplicația se închide.
    //   Reproducibil 100%. Nu există validare, nu există try/catch.
    //
    // BUG 2 — DATA SE PIERDE LA EDITARE
    //   `fillForm` scrie data în `etRelease`, dar NU o scrie în `releaseCal`.
    //   `releaseCal` rămâne pe `Calendar.getInstance()`, adică „acum", din momentul
    //   creării activității. Dacă utilizatorul editează un film și NU atinge câmpul
    //   de dată, `saveMovie` salvează `releaseCal.getTime()` = data de AZI.
    //   Filmul „Inception" (2010) devine „azi", fără nicio eroare.
    //   Corect ar fi ca `fillForm` să facă și `releaseCal.setTime(existing.getRelease())`.
    //
    // BUG 3 — NOTAȚIE ȘTIINȚIFICĂ ÎN CÂMPUL DE BUGET
    //   `String.valueOf(160000000.0)` produce „1.6E8", nu „160000000".
    //   La editare, câmpul afișează „1.6E8". Parsarea înapoi funcționează, deci
    //   datele sunt corecte — doar afișarea este urâtă. Cosmetic, dar vizibil.
    //
    // RISC SUPLIMENTAR — GENUL CARE NU SE GĂSEȘTE
    //   Dacă `@array/movie_genre` se schimbă și valoarea salvată nu mai există,
    //   `fillForm` lasă spinner-ul pe poziția 0, fără mesaj. La salvare, genul
    //   filmului se schimbă în primul element din listă.
    // ==================================================================================
}
```

---

## 29.5 `AndroidManifest.xml` — harta aplicației

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- ================================================================================== -->
<!-- FIȘIER: AndroidManifest.xml — CONTRACTUL APLICAȚIEI CU SISTEMUL                    -->
<!-- ================================================================================== -->
<!-- CE ESTE: fișierul pe care Android îl citește ÎNAINTE să execute orice cod Java.     -->
<!--   El declară ce componente are aplicația, care este cea de start, ce temă          -->
<!--   folosește și ce permisiuni cere.                                                 -->
<!-- DE CE EXISTĂ: fără el, sistemul nu știe că `MainActivity` există. O clasă Java      -->
<!--   nu este „o activitate" prin simpla moștenire din AppCompatActivity; devine       -->
<!--   activitate doar când este declarată aici.                                        -->
<!-- CINE DEPINDE DE EL: procesul de build (îl fuzionează în APK), launcher-ul           -->
<!--   sistemului, `PackageManager`.                                                    -->
<!-- CE NU FACE: nu conține cod, nu conține layout-uri, nu conține logica de navigare.   -->
<!-- CE S-AR RUPE FĂRĂ EL: aplicația nu s-ar instala deloc.                             -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- MANIFESTUL RĂDĂCINĂ                                                                -->
<!-- ================================================================================== -->
<!-- ATRIBUTE:                                                                          -->
<!--   xmlns:android -> namespace-ul atributelor de framework                          -->
<!--   xmlns:tools   -> namespace-ul atributelor pentru Android Studio                  -->
<!--                                                                                    -->
<!-- OBSERVAȚIE: NU există atribut `package`. În AGP 7+ pachetul se declară în          -->
<!--   `build.gradle` prin `namespace = "ro.ase.ie.g1096"`. Tutorialele vechi arată     -->
<!--   `package="ro.ase.ie.g1096"` aici; sintaxa a fost mutată.                         -->
<!--                                                                                    -->
<!-- `xmlns:tools` este DECLARAT, dar în acest fișier NU este folosit: nu apare          -->
<!--   niciun atribut `tools:...`. Declarația este inofensivă, dar inutilă.             -->
<!-- ================================================================================== -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- ============================================================================== -->
    <!-- ELEMENTUL <application> — tot ce ține de aplicație în ansamblu                  -->
    <!-- ============================================================================== -->
    <!-- ATRIBUTE, PE RÂND:                                                              -->
    <!--   allowBackup="true"            -> sistemul poate salva datele aplicației       -->
    <!--                                    (Android Auto Backup).                       -->
    <!--   dataExtractionRules           -> regulile de backup pentru API 31+; trimite    -->
    <!--                                    la `res/xml/data_extraction_rules.xml`.      -->
    <!--   fullBackupContent             -> regulile de backup pentru API 30 și mai jos; -->
    <!--                                    trimite la `res/xml/backup_rules.xml`.       -->
    <!--   icon / roundIcon              -> iconițele din `res/mipmap`; cele două variante -->
    <!--                                    acoperă lansatoarele care taie colțurile.     -->
    <!--   label                         -> numele afișat sub iconiță, din `strings.xml`. -->
    <!--   supportsRtl="true"            -> layout-urile se oglindesc în limbile RTL.     -->
    <!--   theme                         -> tema aplicației. AICI este SINGURA valoare    -->
    <!--                                    specifică grupei: `Theme.G1096`. În G1097      -->
    <!--                                    este `Theme.G1097`. În rest, fișierul este    -->
    <!--                                    identic.                                      -->
    <!--                                                                                 -->
    <!-- CE NU EXISTĂ AICI — și este important: NICIO permisiune. Nu există              -->
    <!--   `<uses-permission android:name="android.permission.INTERNET" />`.             -->
    <!--   Aplicația nu face nicio cerere de rețea: posterul este stocat ca text și       -->
    <!--   nu este descărcat niciodată.                                                   -->
    <!-- ============================================================================== -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.G1096">

        <!-- ========================================================================== -->
        <!-- ACTIVITATEA 1: MainActivity — ECRANUL DE START                              -->
        <!-- ========================================================================== -->
        <!-- android:name=".activities.MainActivity"                                     -->
        <!--   Punctul de la început este RELATIV la namespace-ul aplicației.            -->
        <!--   Forma completă ar fi `ro.ase.ie.g1096.activities.MainActivity`.           -->
        <!--                                                                             -->
        <!-- android:exported="true"                                                     -->
        <!--   OBLIGATORIU din API 31 pentru orice componentă cu intent-filter.          -->
        <!--   `true` = alte aplicații pot porni această activitate. Este necesar        -->
        <!--   pentru launcher: sistemul trebuie să o poată porni.                       -->
        <!--   Fără atribut, build-ul eșuează cu „Apps targeting Android 12 and higher   -->
        <!--   are required to specify an explicit value for android:exported".          -->
        <!--                                                                             -->
        <!-- android:windowSoftInputMode="adjustResize"                                  -->
        <!--   Când apare tastatura, fereastra se MICȘOREZĂ, nu se acoperă. Lista         -->
        <!--   rămâne vizibilă deasupra tastaturii.                                      -->
        <!-- ========================================================================== -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!-- INTENT-FILTER-UL DE LAUNCHER                                          -->
            <!-- Perechea MAIN + LAUNCHER este ce face iconița din meniu să pornească -->
            <!-- aplicația. Fără ea, activitatea ar exista, dar nu ar avea intrare.    -->
            <!--                                                                       -->
            <!-- `MAIN`     = punctul de intrare al aplicației.                        -->
            <!-- `LAUNCHER` = apare în lista de aplicații a sistemului.                -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <!-- Categoria: „arată-mă în launcher". -->
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ========================================================================== -->
        <!-- ACTIVITATEA 2: ItemActivity — FORMULARUL                                    -->
        <!-- ========================================================================== -->
        <!-- android:exported="false"                                                    -->
        <!--   `false` = DOAR aplicația noastră o poate porni. Nicio altă aplicație      -->
        <!--   nu poate deschide formularul direct. Este valoarea corectă pentru o       -->
        <!--   activitate internă.                                                       -->
        <!--                                                                             -->
        <!-- NU are intent-filter: nu este punct de intrare, este deschisă din cod      -->
        <!-- prin `launcher.launch(new Intent(this, ItemActivity.class))`.               -->
        <!--                                                                             -->
        <!-- `windowSoftInputMode="adjustResize"` din nou: formularul are câmpuri text   -->
        <!-- în partea de jos a unui ScrollView, iar tastatura trebuie să micșoreze      -->
        <!-- fereastra ca scroll-ul să funcționeze.                                      -->
        <!--                                                                             -->
        <!-- ATENȚIE: elementul se închide cu `/>` pentru că nu are copii.               -->
        <!-- ========================================================================== -->
        <activity
            android:name=".activities.ItemActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**Harta celor două activități:**

```
                    AndroidManifest.xml
                           |
        +------------------+-------------------+
        |                                      |
  MainActivity                          ItemActivity
  exported = true                       exported = false
  intent-filter MAIN+LAUNCHER           fără intent-filter
  windowSoftInputMode = adjustResize    windowSoftInputMode = adjustResize
        |                                      ^
        |                                      |
        +---- launcher.launch(Intent) ---------+
              (doar din interiorul aplicației)
```

---

## 29.6 `activity_main.xml` — ecranul listei

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- ================================================================================== -->
<!-- FIȘIER: activity_main.xml — ECRANUL CU LISTA                                       -->
<!-- ================================================================================== -->
<!-- CE ESTE: un FrameLayout cu exact doi copii: ListView (umple tot) și FAB (peste el). -->
<!-- DE CE ATÂT DE PUȚIN: toată complexitatea este în `activity_item.xml` (formularul). -->
<!--   Aici doar scheletul.                                                             -->
<!-- STRUCTURA:                                                                         -->
<!--                                                                                    -->
<!--   FrameLayout (id=main)                                                            -->
<!--   |== ListView (id=listView)            <- primul copil = desenat primul = dedesubt -->
<!--   +== FloatingActionButton (id=...)     <- al doilea copil = desenat peste listă    -->
<!--                                                                                    -->
<!-- ORDINEA COPIILOR ESTE SEMNIFICAȚIE, NU STIL: în FrameLayout, fiecare copil este     -->
<!--   desenat peste cel anterior. Inversate, lista ar acoperi butonul.                 -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- FRAMELAYOUT — containerul rădăcină                                                  -->
<!-- ================================================================================== -->
<!-- DE CE FrameLayout și nu LinearLayout: copiii trebuie să se SUPRApună. Un           -->
<!--   LinearLayout i-ar pune unul lângă altul, iar FAB-ul nu ar mai pluti peste listă. -->
<!-- DE CE nu ConstraintLayout: pentru doi copii, un FrameLayout este mai simplu.       -->
<!--                                                                                    -->
<!-- ATRIBUTE:                                                                          -->
<!--   xmlns:android   -> atributele framework-ului                                     -->
<!--   xmlns:app       -> atributele bibliotecilor (Material, AndroidX)                 -->
<!--   xmlns:tools     -> atribute care există DOAR în preview și sunt eliminate la     -->
<!--                      build. Nu ajung niciodată în APK.                             -->
<!--   android:id      -> @+id/main; `@+id/` CREEAZĂ ID-ul, `@id/` îl REFERĂ            -->
<!--   layout_width    -> match_parent: ocupă toată lățimea părintelui                  -->
<!--   layout_height   -> match_parent: ocupă toată înălțimea                          -->
<!--   orientation     -> ATRIBUT INVALID pe FrameLayout; există doar pe LinearLayout.  -->
<!--                      Este IGNORAT de Android și produce un warning de lint         -->
<!--                      („Unknown attribute"). Rămășiță de la un LinearLayout anterior. -->
<!--   tools:context   -> doar pentru preview; îi spune lui Android Studio ce           -->
<!--                      activitate să folosească pentru temă.                         -->
<!--                                                                                    -->
<!-- DE CE `android:id="@+id/main"` ESTE OBLIGATORIU: codul face                        -->
<!--   `findViewById(R.id.main)` pentru listener-ul de insets. Fără acest ID, apelul    -->
<!--   ar întoarce null și `setOnApplyWindowInsetsListener(null, ...)` ar arunca NPE.   -->
<!-- ================================================================================== -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!-- ============================================================================== -->
    <!-- LISTVIEW — lista derulantă                                                      -->
    <!-- ============================================================================== -->
    <!-- DE CE ListView și nu RecyclerView: la acest commit se predă ListView-ul clasic. -->
    <!--   RecyclerView apare în laboratorul următor, împreună cu un layout de rând      -->
    <!--   propriu. G1096 nu are nici măcar `movie_item.xml`.                            -->
    <!--                                                                                 -->
    <!-- ATRIBUTE:                                                                       -->
    <!--   android:id            -> listView; folosit de `findViewById` în initControls   -->
    <!--   layout_width/height   -> match_parent pe ambele axe: lista ocupă tot ecranul, -->
    <!--                            inclusiv zona de sub FAB. FAB-ul este desenat PESTE   -->
    <!--                            listă, nu listă pe lângă el.                         -->
    <!--   android:entries       -> umple lista din XML cu elementele din `@array/items`. -->
    <!--                            LA RUNTIME, `listView.setAdapter(movieAdapter)`      -->
    <!--                            ÎNLOCUIEȘTE complet acest adapter. `entries` rămâne  -->
    <!--                            doar pentru ca preview-ul să arate o listă plină.     -->
    <!--                            Costul la runtime este zero după `setAdapter`.        -->
    <!--                                                                                 -->
    <!-- RISC: ultimul rând din listă poate sta sub FAB. Lista nu are padding de jos,     -->
    <!--   iar butonul este desenat peste ea. Cu 3 filme nu se observă; cu 30, da.        -->
    <!-- ============================================================================== -->
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />

    <!-- ============================================================================== -->
    <!-- FLOATING ACTION BUTTON — butonul „+"                                            -->
    <!-- ============================================================================== -->
    <!-- Numele complet este necesar pentru că este o clasă din biblioteca Material,     -->
    <!--   nu una din framework. Prefixul `com.google.android.material...` este calea.   -->
    <!--                                                                                 -->
    <!-- ATRIBUTE:                                                                       -->
    <!--   android:id          -> floatingActionButton; căutat în initControls            -->
    <!--   layout_width/height -> wrap_content: FAB-ul are o dimensiune fixă impusă de   -->
    <!--                          stil (56dp implicit). `match_parent` l-ar întinde.      -->
    <!--   android:layout_gravity -> poziția ACESTUI COPIL în PĂRINTELE lui (FrameLayout).-->
    <!--   android:layout_margin  -> 16dp pe toate laturile. Împreună cu padding-ul de    -->
    <!--                          insets aplicat pe `R.id.main`, butonul stă la 16dp de   -->
    <!--                          zona sigură, nu de marginea fizică.                     -->
    <!--   android:contentDescription -> textul citit de TalkBack. OBLIGATORIU pentru     -->
    <!--                          elementele fără text vizibil; fără el, lint-ul          -->
    <!--                          semnalează („ContentDescription"), iar utilizatorii cu  -->
    <!--                          cititor de ecran aud doar „buton".                     -->
    <!--   app:srcCompat       -> varianta compatibilă pentru imagini vectoriale.         -->
    <!--                          `android:src` ar funcționa pe API 21+, dar `srcCompat`  -->
    <!--                          este recomandarea AndroidX.                             -->
    <!--                                                                                 -->
    <!-- layout_gravity  vs  gravity:                                                    -->
    <!--   gravity         = cum își aranjează ELEMENTUL copiii lui în interior          -->
    <!--   layout_gravity  = cum este aranjat ELEMENTUL în părintele lui                 -->
    <!--                                                                                 -->
    <!-- `bottom|end` = jos, dreapta. `end` respectă direcția de citire: în RTL devine    -->
    <!--   stânga. `right` ar fi fost fix și ar fi greșit în RTL.                        -->
    <!-- ============================================================================== -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_24" />

</FrameLayout>
```

**Tabel de referință pentru atributele din acest fișier:**

| Atribut | Valoare | Efect |
|---|---|---|
| `android:id` | `@+id/main` | creează ID-ul folosit de insets |
| `android:layout_width/height` | `match_parent` | umple părintele |
| `android:layout_gravity` | `bottom\|end` | poziționează FAB-ul în FrameLayout |
| `android:contentDescription` | `"Add"` | accesibilitate + lint |
| `app:srcCompat` | `@drawable/outline_add_24` | imagine vectorială compatibilă |
| `tools:context` | `.activities.MainActivity` | doar preview |
| `android:orientation` | `horizontal` | **invalid** pe FrameLayout, ignorat |

---

## 29.7 `activity_item.xml` — formularul

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- ================================================================================== -->
<!-- FIȘIER: activity_item.xml — FORMULARUL DE ADAUGĂ / EDITEZĂ                          -->
<!-- ================================================================================== -->
<!-- CE ESTE: un ScrollView cu un singur copil LinearLayout vertical, împărțit în       -->
<!--   patru carduri (Basics, Production, Your verdict, Poster) plus butonul de salvare. -->
<!-- DE CE EXISTĂ: este singurul layout cu care `ItemActivity` lucrează. Cele 13 ID-uri -->
<!--   căutate în `initControls()` sunt toate aici.                                     -->
<!-- CINE DEPINDE DE EL: `ItemActivity` (prin `setContentView(R.layout.activity_item)`). -->
<!-- CE NU FACE: nu validează, nu afișează erori, nu are text de ajutor pentru câmpuri -->
<!--   invalide. Este strict structură.                                                 -->
<!-- CE S-AR RUPE FĂRĂ EL: `setContentView` ar arunca `Resources.NotFoundException`,   -->
<!--   iar fiecare `findViewById` ar întoarce null.                                     -->
<!--                                                                                    -->
<!-- IDENTIC CU G1097. Toate observațiile din capitolul 22, secțiunea 22.5, se aplică   -->
<!--   aici cuvânt cu cuvânt.                                                           -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- REGULA 1: `?attr/` vs `@color/` vs `#RRGGBB`                                       -->
<!-- ================================================================================== -->
<!--   ?attr/colorPrimary   -> se rezolvă la RUNTIME, din tema curentă; se schimbă      -->
<!--                           în dark mode. Este un ROL, nu o valoare.                 -->
<!--   @color/my_color      -> se rezolvă la BUILD, din `colors.xml`; nu se schimbă.    -->
<!--   #FFC107              -> literal, la build; excepție asumată (stelele).           -->
<!--   @android:color/...   -> constantă de framework.                                  -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- REGULA 2: `0dp` + `layout_weight`                                                  -->
<!-- ================================================================================== -->
<!--   LinearLayout orizontal, lățime totală 360dp:                                     -->
<!--   +--------------------------------------------------------------+                 -->
<!--   | TextView A        | TextView B                               |                 -->
<!--   | width=0dp         | width=wrap_content                       |                 -->
<!--   | weight=1          | (fără weight)                            |                 -->
<!--   +-------------------+------------------------------------------+                 -->
<!--   |<=== restul =====>|<====== cât cere textul =================>|                 -->
<!--                                                                                    -->
<!--   `0dp` + `weight` = „nu mă interesează lățimea mea, dă-mi ce rămâne".             -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- REGULA 3: `style=` vs atribute explicite                                           -->
<!-- ================================================================================== -->
<!--   `style="@style/Widget.Material3.TextInputLayout.OutlinedBox"` aplică un PACHET   -->
<!--   de atribute. Un atribut scris explicit lângă `style` îl SUPRASCRIE pe cel din    -->
<!--   stil. De aceea `app:cardCornerRadius="20dp"` funcționează peste stilul cardului. -->
<!-- ================================================================================== -->

<!-- ================================================================================== -->
<!-- SCROLLVIEW — rădăcina                                                              -->
<!-- ================================================================================== -->
<!-- DE CE ScrollView: formularul este mai înalt decât ecranul unui telefon. Fără el,   -->
<!--   butonul de salvare ar fi inaccesibil pe ecrane mici.                             -->
<!-- REGULA: ScrollView acceptă EXACT UN copil. Al doilea ar produce o excepție la      -->
<!--   inflate („ScrollView can host only one direct child").                           -->
<!--                                                                                    -->
<!-- ATRIBUTE:                                                                          -->
<!--   android:id="@+id/main"     -> folosit de listener-ul de insets din ItemActivity. -->
<!--   layout_width/height        -> match_parent pe ambele axe.                        -->
<!--   android:background         -> `?attr/colorSurface`, culoarea de fundal a temei.  -->
<!--                                 Fără ea, fundalul ar fi implicit și ar putea diferi -->
<!--                                 de restul aplicației.                              -->
<!--   android:fillViewport="true"-> copilul este întins să acopere cel puțin ecranul, -->
<!--                                 chiar dacă are mai puțin conținut.                 -->
<!--   tools:context              -> doar preview.                                      -->
<!-- ================================================================================== -->
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <!-- ============================================================================== -->
    <!-- CONȚINUTUL — un singur LinearLayout vertical                                    -->
    <!-- ============================================================================== -->
    <!-- `paddingHorizontal` și `paddingTop/Bottom` există din API 26. Pe versiuni mai   -->
    <!--   vechi ar fi ignorate; proiectul folosește EdgeToEdge, deci API-ul este oricum -->
    <!--   modern.                                                                       -->
    <!-- ============================================================================== -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- ========================================================================== -->
        <!-- ANTETUL ECRANULUI                                                          -->
        <!-- ========================================================================== -->
        <!-- Două TextView-uri statice, FĂRĂ id: nu sunt citite niciodată din cod.       -->
        <!-- Primul: titlul mare, cu stilul de headline al temei.                       -->
        <!-- Header -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Movie details"
            android:textAppearance="?attr/textAppearanceHeadlineMedium"
            android:textColor="?attr/colorOnSurface"
            android:textStyle="bold" />

        <!-- Al doilea: subtitlul, mai mic, cu culoarea secundară. -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="20dp"
            android:text="Fill in the information below and save."
            android:textAppearance="?attr/textAppearanceBodyMedium"
            android:textColor="?attr/colorOnSurfaceVariant" />

        <!-- ========================================================================== -->
        <!-- CARD 1 — „Basics": titlu, gen, dată                                        -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 1: Basics ============ -->
        <!-- MaterialCardView cu stilul „filled": fundal colorat, fără contur.           -->
        <!-- `cardCornerRadius="20dp"` este scris explicit și SUPRASCRIE valoarea din   -->
        <!--   stil.                                                                     -->
        <!-- ========================================================================== -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <!-- Container vertical interior, cu padding de 16dp pe toate laturile. -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!-- Titlul secțiunii. `?attr/colorPrimary` îl face colorat. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Basics"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- ETICHETA „Title" — id `tvTile`, nu `tvTitle`.                   -->
                <!--   Typo real în sursă. Nu este folosită nicăieri în Java, deci   -->
                <!--   typo-ul nu are efect. Dar dacă ai vrea să o folosești,        -->
                <!--   `findViewById(R.id.tvTitle)` ar întoarce null.                -->
                <!-- Title -->
                <TextView
                    android:id="@+id/tvTile"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Title"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- CÂMPUL DE TITLU, învelit în TextInputLayout.                     -->
                <!--   `hintEnabled="false"` -> fără etichetă plutitoare; hint-ul din -->
                <!--     EditText se comportă ca un placeholder obișnuit.             -->
                <!--   `endIconMode="clear_text"` -> adaugă un X care golește câmpul. -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text">

                    <!-- `TextInputEditText` este subclasă a lui `EditText`, deci se  -->
                    <!--   leagă de câmpul `private EditText etTitle`.                -->
                    <!-- `textCapWords` -> tastatura capitalizează fiecare cuvânt.    -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Movie title"
                        android:inputType="textCapWords" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- ETICHETA „Genre". -->
                <!-- Genre -->
                <TextView
                    android:id="@+id/tvGenre"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Genre"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- SPINNER-UL, ÎNVELIT ÎNTR-UN CARD.                                -->
                <!--   DE CE: `Spinner` nu are un stil Material „outlined". Trucul    -->
                <!--   este un MaterialCardView cu contur, înalt de 56dp (înălțimea  -->
                <!--   standard a unui câmp Material), în care spinner-ul umple tot.  -->
                <!--   `cardBackgroundColor="@android:color/transparent"` -> fără      -->
                <!--   fundal propriu, ca să se vadă fundalul cardului părinte.       -->
                <com.google.android.material.card.MaterialCardView
                    style="?attr/materialCardViewOutlinedStyle"
                    android:layout_width="match_parent"
                    android:layout_height="56dp"
                    android:layout_marginBottom="16dp"
                    app:cardBackgroundColor="@android:color/transparent"
                    app:cardCornerRadius="4dp"
                    app:strokeColor="?attr/colorOutline">

                    <!-- `entries` umple spinner-ul din `@array/movie_genre` — valorile -->
                    <!--   definite într-un fișier din `res/values/`, nu în acesta.      -->
                    <!-- `spinnerMode="dropdown"` -> lista se deschide ca un popup,     -->
                    <!--   nu ca un dialog modal.                                       -->
                    <Spinner
                        android:id="@+id/spGenre"
                        android:layout_width="match_parent"
                        android:layout_height="match_parent"
                        android:entries="@array/movie_genre"
                        android:paddingStart="4dp"
                        android:spinnerMode="dropdown" />
                </com.google.android.material.card.MaterialCardView>

                <!-- CÂMPUL DE DATĂ.                                                  -->
                <!--   `hintEnabled="true"` (valoarea implicită, scrisă explicit) ->  -->
                <!--   eticheta „Release date" PLUTeșTE deasupra când câmpul are text. -->
                <!--   `startIconDrawable` -> iconița de calendar în stânga.          -->
                <!--   `startIconContentDescription` -> textul citit de TalkBack      -->
                <!--   pentru iconiță.                                                -->
                <!-- Release date -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="true"
                    app:startIconContentDescription="Release date"
                    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

                    <!-- `inputType="date"` -> tastatură numerică cu `/` și `-`.     -->
                    <!--   Câmpul rămâne EDITABIL: utilizatorul poate tasta text     -->
                    <!--   invalid, iar `showReleaseDatePicker` îl ignoră silențios. -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etRelease"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Release date"
                        android:inputType="date" />
                </com.google.android.material.textfield.TextInputLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ========================================================================== -->
        <!-- CARD 2 — „Production": buget și durată                                     -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 2: Production ============ -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!-- Titlul secțiunii. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Production"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- ETICHETA „Budget". -->
                <!-- Budget -->
                <TextView
                    android:id="@+id/tvBudget"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Budget"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- CÂMPUL DE BUGET.                                                 -->
                <!--   `prefixText="$ "` -> afișează „$ " în fața valorii, fără să o  -->
                <!--   adauge la text. Este doar vizual.                              -->
                <!--   `inputType="numberDecimal"` -> tastatură numerică cu punct     -->
                <!--   zecimal. Virgula nu este disponibilă pe toate tastaturile.     -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:prefixText="$ ">

                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etBudget"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Budget"
                        android:inputType="numberDecimal" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- RÂNDUL DE DURATĂ: etichetă + valoare curentă.                    -->
                <!--   `layout_weight="1"` pe etichetă -> ea ia tot spațiul rămas,    -->
                <!--   iar valoarea stă în dreapta, lipită de margine.                -->
                <!-- Duration -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">

                    <!-- `width="0dp"` + `weight="1"` = „ia ce rămâne". -->
                    <TextView
                        android:id="@+id/tvDuration"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Duration"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!-- VALOAREA CURENTĂ. Textul inițial este „0 min" (FĂRĂ punct), -->
                    <!--   dar Java scrie „0 min." (CU punct) la prima actualizare.  -->
                    <!--   Inconsistență cosmetică reală între XML și cod.           -->
                    <!--   `tools:text` este doar pentru preview; nu ajunge în APK.   -->
                    <TextView
                        android:id="@+id/tvDurationValue"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorPrimary"
                        tools:text="148 min" />
                </LinearLayout>

                <!-- SLIDER-UL DE DURATĂ.                                             -->
                <!--   `android:max="300"` -> valoarea maximă.                        -->
                <!--   `android:min="0"` -> atribut disponibil din API 26; pe versiuni -->
                <!--     mai vechi este ignorat și minimul rămâne 0 oricum.           -->
                <!--   `progressTint` / `thumbTint` -> culoarea barei și a mânerului, -->
                <!--     luată din tema curentă.                                      -->
                <!--   `tools:progress="148"` -> doar preview.                        -->
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

                <!-- Legenda sub slider: 0 în stânga, 300 în dreapta. -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal"
                    android:paddingHorizontal="16dp">

                    <TextView
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelSmall"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="300 min"
                        android:textAppearance="?attr/textAppearanceLabelSmall"
                        android:textColor="?attr/colorOnSurfaceVariant" />
                </LinearLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ========================================================================== -->
        <!-- CARD 3 — „Your verdict": rating, switch, bifă, ghidaj                      -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 3: Your verdict ============ -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Your verdict"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- ETICHETA „Rating". -->
                <!-- Rating -->
                <TextView
                    android:id="@+id/tvRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Rating"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- RATINGBAR-UL.                                                    -->
                <!--   `numStars="5"` -> cinci stele.                                 -->
                <!--   `stepSize="0.5"` -> jumătăți de stea.                          -->
                <!--   `#FFC107` -> chihlimbar HARDCODAT, nu din temă. În dark mode   -->
                <!--     rămâne la fel. Este o excepție asumată, nu un rol de temă.   -->
                <!--   `layout_gravity="center_horizontal"` -> centrat în părintele   -->
                <!--     vertical.                                                    -->
                <RatingBar
                    android:id="@+id/rbRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_gravity="center_horizontal"
                    android:layout_marginTop="4dp"
                    android:numStars="5"
                    android:stepSize="0.5"
                    android:progressTint="#FFC107"
                    android:secondaryProgressTint="#FFC107"
                    android:progressBackgroundTint="?attr/colorOutlineVariant"
                    tools:rating="3.5" />

                <!-- Separator: o linie de 1dp, colorată din temă. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- RÂNDUL „Recommended" + switch + bifă.                            -->
                <!--   `minHeight="48dp"` -> ținta minimă de atingere recomandată de  -->
                <!--   Material.                                                      -->
                <!-- Recommended -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:minHeight="48dp"
                    android:orientation="horizontal">

                    <!-- Coloana de text: etichetă + valoare. -->
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">

                        <!-- ATENȚIE LA SEMANTICĂ: eticheta spune „Recommended", -->
                        <!--   dar câmpul din model se numește `watched`. Cele două -->
                        <!--   nu înseamnă același lucru. Este o inconsecvență între -->
                        <!--   UI și model, nu un bug funcțional: switch-ul salvează -->
                        <!--   exact ce arată.                                    -->
                        <TextView
                            android:id="@+id/tvWatched"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Recommended"
                            android:textAppearance="?attr/textAppearanceBodyLarge"
                            android:textColor="?attr/colorOnSurface" />

                        <!-- Valoarea textuală a switch-ului. Pornește pe „No" și este -->
                        <!--   rescrisă de listener cu „Yes"/„No".                       -->
                        <TextView
                            android:id="@+id/tvWatchedValue"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="No"
                            android:textAppearance="?attr/textAppearanceLabelLarge"
                            android:textColor="?attr/colorPrimary" />
                    </LinearLayout>

                    <!-- COMUTATORUL. Tipul complet Material, exact tipul câmpului -->
                    <!--   `private MaterialSwitch swWatched;`.                     -->
                    <com.google.android.material.materialswitch.MaterialSwitch
                        android:id="@+id/swWatched"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="12dp" />

                    <!-- BIFA „Watchlist". Tip Material, dar câmpul Java este     -->
                    <!--   `CheckBox` — MaterialCheckBox este subclasă, deci merge. -->
                    <com.google.android.material.checkbox.MaterialCheckBox
                        android:id="@+id/cbOnWatchList"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Watchlist" />
                </LinearLayout>

                <!-- Al doilea separator. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- ETICHETA „Guidance". -->
                <!-- Guidance -->
                <TextView
                    android:id="@+id/tvGuidance"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Guidance"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- CINCI BUTOANE RADIO NU ÎNCAP pe un ecran îngust. De aceea sunt -->
                <!--   puse într-un HorizontalScrollView: se pot derula lateral.     -->
                <!--   `scrollbars="none"` -> fără bara de derulare vizibilă.        -->
                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none">

                    <!-- RADIOGROUP-ul. `orientation="horizontal"` -> butoanele stau  -->
                    <!--   pe un rând. Garanția grupului: exact UNUL bifat.            -->
                    <RadioGroup
                        android:id="@+id/rgApproval"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <!-- `android:checked="true"` -> selecția implicită. Fără ea, -->
                        <!--   niciun buton nu ar fi bifat și `approval` ar rămâne    -->
                        <!--   null la salvare.                                       -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbGeneral"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:checked="true"
                            android:text="G" />

                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbParentGuidance"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG" />

                        <!-- Textul „PG-13" este EXACT valoarea salvată în model. -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbPG13"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG-13" />

                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbRestricted"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="R" />

                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbNC17"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="NC-17" />
                    </RadioGroup>
                </HorizontalScrollView>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ========================================================================== -->
        <!-- CARD 4 — „Poster"                                                          -->
        <!-- ========================================================================== -->
        <!-- ============ CARD 4: Poster ============ -->
        <!-- Singurul card cu UN SINGUR câmp. Eticheta „Poster" nu are id, spre deosebire -->
        <!--   de celelalte etichete de secțiune.                                       -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="24dp"
            app:cardCornerRadius="20dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Poster"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- CÂMPUL DE URL.                                                    -->
                <!--   `inputType="textUri"` -> tastatură cu `/`, `.` și `.com`.       -->
                <!--   `startIconDrawable` -> iconița de galerie.                      -->
                <!--   `endIconMode="clear_text"` -> X-ul de golire.                   -->
                <!--   NICIO previzualizare: nu există ImageView, nu există încărcare. -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text"
                    app:startIconContentDescription="Poster link"
                    app:startIconDrawable="@android:drawable/ic_menu_gallery">

                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etPoster"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Poster URL"
                        android:inputType="textUri" />
                </com.google.android.material.textfield.TextInputLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ========================================================================== -->
        <!-- BUTONUL DE SALVARE                                                          -->
        <!-- ========================================================================== -->
        <!--   `layout_height="60dp"` + `cornerRadius="30dp"` -> formă de pastilă.      -->
        <!--   `app:icon` -> iconița de salvare, din framework.                         -->
        <!--   `iconGravity="textStart"` -> iconița stă înaintea textului.              -->
        <!--   Textul este „Save Movie"; în modul edit, `ItemActivity` îl schimbă în    -->
        <!--   „Update Movie" prin `btMovieAction.setText(...)`.                        -->
        <!-- ========================================================================== -->
        <!-- Save -->
        <com.google.android.material.button.MaterialButton
            android:id="@+id/btnMovieAction"
            style="@style/Widget.Material3.Button"
            android:layout_width="match_parent"
            android:layout_height="60dp"
            android:text="Save Movie"
            android:textAppearance="?attr/textAppearanceLabelLarge"
            app:cornerRadius="30dp"
            app:icon="@android:drawable/ic_menu_save"
            app:iconGravity="textStart" />

    </LinearLayout>
</ScrollView>
```

**Harta widget-urilor din formular — ce citește fiecare setter:**

| Câmp `Movie` | Widget | ID | Metodă de citire |
|---|---|---|---|
| `title` | TextInputEditText | `etTitle` | `getText().toString()` |
| `release` | TextInputEditText + dialog | `etRelease` | `releaseCal.getTime()` |
| `genre` | Spinner | `spGenre` | `getSelectedItem().toString()` |
| `budget` | TextInputEditText | `etBudget` | `Double.parseDouble(...)` |
| `duration` | SeekBar | `sbDuration` | `getProgress()` |
| `rating` | RatingBar | `rbRating` | `getRating()` |
| `watched` | MaterialSwitch | `swWatched` | `isChecked()` |
| `approval` | RadioGroup | `rgApproval` | buclă + `isChecked()` |
| `onWatchlist` | MaterialCheckBox | `cbOnWatchList` | `isChecked()` |
| `posterUrl` | TextInputEditText | `etPoster` | `getText().toString()` |

---

## 29.8 Fluxul complet

### 29.8.1 Pornirea aplicației

```
PORNIRE
  AndroidManifest: intent-filter MAIN + LAUNCHER
    |
    v
  MainActivity.onCreate(savedInstanceState = null)
    |
    |== super.onCreate                 -> AppCompat își instalează delegate-ul
    |== EdgeToEdge.enable(this)         -> ferestrele desenează sub bare
    |== setContentView(activity_main)   -> arborele de view-uri există
    |== insets pe R.id.main             -> padding = status bar + nav bar
    |== addSampleMovies()               -> movies = [Inception, Toy Story, The Matrix]
    |== new ArrayAdapter(this,
    |       android.R.layout.simple_list_item_1, movies)
    |                                   -> movieAdapter ține REFERINȚA la `movies`
    |== initControls()                  -> fabInsert, listView, setAdapter
    |== initListeners()                 -> FAB + item click (launcher este încă null)
    +== registerForActivityResult(...)  -> launcher creat
          |
          v
  ListView afișează 3 rânduri:
    „Movie{title='Inception', release=..., genre='Sci-Fi', ..., onWatchlist=false}"
    „Movie{title='Toy Story', ...}"
    „Movie{title='The Matrix', ...}"
```

Observă că rândul **nu** conține URL-ul posterului: `toString()` din G1096 se oprește la `onWatchlist`.

### 29.8.2 Insert — FAB

```
APASĂ FAB
  fabInsert.onClick
    |
    |== new Intent(MainActivity.this, ItemActivity.class)   (FĂRĂ extra-uri)
    +== launcher.launch(intent)
          |
          v
  MainActivity: onPause
  ItemActivity: onCreate
    |
    |== setContentView(activity_item)
    |== insets pe R.id.main
    |== initControls()          -> 13 findViewById
    |== initListeners()         -> 4 listeneri (înainte de fillForm!)
    |== getIntent()             -> Intent fără MOVIE_EXTRA
    +== existing == null        -> position rămâne -1, formular gol
          |
          v
  UTILIZATORUL COMPLETEAZĂ ȘI APASĂ „Save Movie"
    |
    |== saveMovie()
    |     |== new Movie()
    |     |== 9 setter-e din widget-uri
    |     |== buclă pe rgApproval -> al 10-lea setter
    |     |== Intent fără target
    |     |== putExtra(MOVIE_EXTRA, movie)
    |     |== (position == -1, deci POSITION_EXTRA NU se pune)
    |     |== setResult(RESULT_OK, intent)
    |     +== finish()
    |
    v
  ItemActivity: onPause -> onStop -> onDestroy
  MainActivity: onStart -> onResume -> callback
    |
    |== resultCode == RESULT_OK ?
    |== intent = o.getData()
    |== movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA)   <- O COPIE
    |== position = intent.getIntExtra(POSITION_EXTRA, -1)           -> -1
    |== movies.add(movie)
    +== movieAdapter.notifyDataSetChanged()
          |
          v
  ListView redesenează -> al 4-lea rând apare
```

### 29.8.3 Edit — click pe rând

```
CLICK PE RÂNDUL 1
  listView.onItemClick(parent, view, position = 0, id = 0)
    |
    |== new Intent(MainActivity.this, ItemActivity.class)
    |== putExtra(MOVIE_EXTRA, movies.get(0))    <- SERIALIZARE
    |== putExtra(POSITION_EXTRA, 0)
    +== launcher.launch(intent)
          |
          v
  ItemActivity.onCreate
    |
    |== initControls() + initListeners()
    |== existing = IntentCompat.getSerializableExtra(intent, MOVIE_EXTRA, Movie.class)
    |                                                        <- COPIE, tipată
    |== existing != null
    |     |== position = 0
    |     |== fillForm(existing)     -> 8 setter-e + 2 bucle
    |     |     |== sbDuration.setProgress(...)  -> declanșează onProgressChanged
    |     |     |== swWatched.setChecked(...)    -> declanșează onCheckedChanged
    |     |     +== (de aceea listenerii trebuie atașați ÎNAINTE)
    |     |== setTitle("Edit movie")            <- metoda ACTIVITĂȚII
    |     +== btMovieAction.setText("Update Movie")
    +== (formularul arată filmul existent)
          |
          v
  UTILIZATORUL MODIFICĂ ȘI APASĂ „Update Movie"
    |
    |== saveMovie()
    |     |== new Movie() + 10 setter-e
    |     |== putExtra(MOVIE_EXTRA, movie)
    |     |== position != -1 -> putExtra(POSITION_EXTRA, 0)
    |     +== setResult + finish()
    |
    v
  MainActivity callback
    |== position = 0 (nu -1)
    |== movies.set(0, movie)        <- ÎNLOCUIRE, nu adăugare
    +== notifyDataSetChanged()
          |
          v
  Rândul 1 se redesenează cu datele noi
```

### 29.8.4 Obiectul care călătorește

```
MainActivity                          Intent / Bundle                ItemActivity
------------                          ---------------                ------------

movies: List<Movie>
  [0] Movie@A  ---------------------+
  [1] Movie@B                       |
  [2] Movie@C                       |
                                    |  putExtra("movie", Movie@A)
                                    v
                          serialize(Movie@A) -> bytes
                                    |
                                    v
                          Bundle { "movie" -> bytes,
                                   "position" -> 0 }
                                    |
                                    v
                          deserialize(bytes) -> Movie@A'
                                    |
                                    v
                                                       existing = Movie@A'
                                                       (obiect NOU, adresă nouă)
                                    |
                        fillForm(existing) citește
                        saveMovie() creează Movie@D
                                    |
                                    v
                          Intent rezultat { "movie" -> Movie@D,
                                            "position" -> 0 }
                                    |
                                    v
                          movies.set(0, Movie@D)
                                    |
                                    v
                          Movie@A rămâne în heap până la GC
```

**Consecința practică:** modificarea formularului nu se vede în listă până la `movies.set(...)`. Nu există „legătură" între obiectul din listă și cel din formular — sunt două obiecte distincte. Dacă ai modifica `Movie@A'` și ai închide activitatea cu Back, `Movie@A` ar rămâne neschimbat.

### 29.8.5 Posterul: stocat, niciodată afișat

```
  etPoster (textUri)
      |
      | getText().toString()
      v
  Movie.posterUrl  (String)
      |
      | putExtra -> serialize -> Bundle -> deserialize
      v
  Movie.posterUrl'  (String)
      |
      | toString()  -- NU îl include
      | ImageView   -- NU există
      | rețea       -- NU există
      v
  (rămâne în model, invizibil)
```

Trei dovezi că posterul nu este folosit niciodată ca imagine:

1. `Movie.toString()` nu îl include — rândul din listă nu îl arată.
2. `activity_item.xml` nu conține niciun `ImageView`.
3. `AndroidManifest.xml` nu conține `<uses-permission android:name="android.permission.INTERNET" />`, iar niciun fișier Java nu importă o bibliotecă de rețea.

Deci `posterUrl` este, în această etapă, **un câmp de text ca oricare altul**.

### 29.8.6 Ce se întâmplă la rotire

```
  Telefon rotit 90°
    |
    v
  MainActivity: onPause -> onStop -> onDestroy   (instanța este ARUNCATĂ)
    |
    v
  MainActivity: onCreate(savedInstanceState != null)
    |
    |== addSampleMovies()   -> movies = [Inception, Toy Story, The Matrix]
    |== ...                 -> lista revine la cele 3 filme demo
    v
  Filmele adăugate de utilizator AU DISPĂRUT.
```

Nu există `onSaveInstanceState(Bundle)` în `MainActivity`, deci `movies` nu este salvată. Este o limitare reală a aplicației, nu o teorie: adaugă un film, rotește telefonul, filmul dispare.

Formularul are aceeași problemă: `ItemActivity` nu salvează starea câmpurilor, deci la rotire formularul se golește (sau se reumple din `Intent`, în modul edit).

---

## 29.9 Ce să reții din fiecare fișier

| Fișier | Esența | Capcana |
|---|---|---|
| `Movie.java` | POJO serializabil, 10 câmpuri, constructor gol explicit **primul**, `isX()` pentru booleeni, `toString()` fără poster | constructorul cu 10 parametri este POZIȚIONAL; `posterUrl` nu `poster` |
| `MainActivity.java` | ordinea din `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` | `launcher` este atribuit DUPĂ `initListeners`; lista se pierde la rotire |
| `ItemActivity.java` | 13 `findViewById`, `releaseCal` ca sursă de adevăr, buclă generică pe `RadioGroup`, `setResult` + `finish` | buget gol -> crash; data se pierde la editare; notație științifică |
| `AndroidManifest.xml` | două activități, `exported` corect, fără permisiuni | `exported` obligatoriu din API 31; `Theme.G1096` este singura diferență de grupă |
| `activity_main.xml` | `FrameLayout` + ordinea copiilor + `layout_gravity` pe FAB | `android:orientation` este invalid pe FrameLayout |
| `activity_item.xml` | `ScrollView` cu un copil, `MaterialCardView` ca secțiune, `TextInputLayout`, `Spinner` învelit | `hintEnabled` trebuie corelat cu existența etichetei; `tvTile` este typo |

### Cele 10 lucruri pe care le vei fi întrebat

1. **De ce `implements Serializable`?** Ca obiectul să poată fi pus într-un `Intent` cu `putExtra`.
2. **Obiectul primit este originalul?** Nu. Este o copie deserializată; de aceea `MainActivity` face `movies.set(...)`.
3. **De ce constructor gol explicit?** Un constructor cu parametri suprimă constructorul implicit, iar `saveMovie` face `new Movie()`. În G1096 este primul din clasă; în G1097, ultimul.
4. **De ce `isWatched()`?** Convenția JavaBeans pentru `boolean`.
5. **De ce `notifyDataSetChanged()`?** ListView nu observă lista; adapterul trebuie să anunțe.
6. **De ce `MainActivity.this`?** În clasa anonimă, `this` este listener-ul, nu `Context`-ul.
7. **De ce `releaseCal` și nu `etRelease`?** Calendarul este sursa de adevăr; textul poate fi invalid. **Dar** `fillForm` nu îl actualizează — BUG 2.
8. **De ce `fromUser` este ignorat?** Eticheta trebuie să reflecte valoarea și când vine din `fillForm`, nu doar când trage utilizatorul.
9. **De ce `0dp` + `weight`?** „Ia tot spațiul rămas", nu „ia mărimea naturală".
10. **De ce `?attr/` și nu `@color/`?** `?attr/` este un rol de temă și se adaptează la dark mode.

### Diferențele pe care le vei fi întrebat la G1096

1. **Cum se numește câmpul posterului?** `posterUrl`, cu accesoriile `getPosterUrl()` / `setPosterUrl(...)`.
2. **Ce importuri sunt moarte în `MainActivity`?** `java.math.BigDecimal` și `android.widget.Toast`.
3. **Ce import este mort în `ItemActivity`?** `android.widget.Switch` — și ar fi periculos dacă ar fi folosit, pentru că `MaterialSwitch` nu este subclasă a lui `Switch`.
4. **Unde este constructorul fără parametri?** Primul, la linia 18, imediat după câmpuri.
5. **Ce lipsește din `toString()`?** `posterUrl`.
6. **Ce fișier lipsește față de G1097?** `movie_item.xml` — și nu îl folosea niciun cod.

---

## Rezumat capitol 29

- Modelul nu atinge UI-ul; activitățile nu conțin logică de rând.
- `onCreate`: `super` -> `EdgeToEdge` -> `setContentView` -> insets -> date -> adapter -> controls -> listeners -> launcher.
- `releaseCal` este sursa de adevăr pentru dată, **dar `fillForm` nu o actualizează** — data se pierde la editare.
- Bucla pe `RadioGroup` face codul generic — adaugi butoane în XML, codul le vede.
- `setResult(RESULT_OK, intent)` + `finish()` este perechea obligatorie.
- `notifyDataSetChanged()` după orice modificare a listei.
- `posterUrl` este stocat ca text și nu este afișat niciodată: nu există `ImageView`, nu există rețea, nu există permisiune `INTERNET`.
- Lista nu supraviețuiește rotirii: nu există `onSaveInstanceState`.
- Trei bug-uri reale: buget gol, data pierdută la editare, notație științifică.
- Față de G1097: `posterUrl` în loc de `poster`, constructor gol primul, `toString()` fără poster, alte importuri moarte, fără `movie_item.xml`.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [prezentarea generală](index.html).
