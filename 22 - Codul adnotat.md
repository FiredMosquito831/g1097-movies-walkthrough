# Capitolul 22 — Codul G1097 adnotat

**Obiectiv:** să citești fiecare linie a aplicației G1097 cu explicația lipită de ea — ce face, de ce e acolo, ce se rupe dacă o scoți.

**Timp estimat:** 90–120 min (citire activă, cu proiectul deschis în paralel).

**Sursa:** `cod-final`, commitul `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `activity_main.xml`, `activity_item.xml`, `movie_item.xml`.

**Regulă:** codul este **nemodificat, byte cu byte**. Tot ce apare cu `//` sau `<!-- -->` în plus față de sursă este adnotare.

---

## 22.0 Cum să citești acest capitol

Acesta nu este un capitol de exerciții. Este un capitol de **citire cu lupa**: iei fiecare fișier al aplicației și îl parcurgi linie cu linie, cu explicația chiar deasupra.

- **Citește codul întâi, comentariul al doilea.** Acoperă cu mâna blocul de comentarii, spune ce face linia, apoi verifică.
- **Blocurile `TEORIE`** apar înaintea fiecărei clase și explică *de ce* există structura, nu *cum* funcționează.
- **Blocurile numerotate** („1. Validare", „2. Curățare") descriu pașii unei metode în ordinea execuției. Ordinea este parte din lecție.
- **Marcajele `RISC:` și `BUG:`** semnalează locurile unde codul funcționează astăzi, dar se poate rupe, sau unde se rupe deja.
- **Diagramele ASCII** arată ce nu se vede în cod: obiectul care călătorește între activități, zona sigură a ecranului, reciclarea rândurilor în listă.
- **Nu memora.** Scopul este să poți reconstrui fișierul pornind de la o diagramă.

---

## 22.1 `Movie.java` — modelul de date

```java
/*
 * ======================================================================================
 * FIȘIER: Movie.java — MODELUL DE DATE
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   O clasă POJO (Plain Old Java Object): 10 câmpuri private, un constructor cu 10
 *   parametri, un constructor gol și 20 de getter-e/setter-e. Zero logică de business.
 *
 * DE CE EXISTĂ:
 *   Ca să transporte datele unui film dintr-un ecran în altul fără să depindă de UI.
 *   `MainActivity` ține o listă de `Movie`; `ItemActivity` construiește un `Movie`.
 *
 * CE ȘTIE:
 *   Doar valorile: titlu, dată, gen, buget, durată, rating, watched, approval,
 *   onWatchlist, poster. Nu știe ce este un `EditText`, un `Intent` sau un `ListView`.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   Tot fluxul de date. `Intent.putExtra` nu ar avea ce serializa, `ArrayAdapter`
 *   nu ar avea ce afișa, iar `ItemActivity` ar trebui să trimită 10 extra-uri separate
 *   și să le recompună manual în `MainActivity`.
 * ======================================================================================
 */

package ro.ase.ie.g1097.model;

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
//   `Serializable` din fabrică și este tipul cerut de enunțul temei.
// RISC: `Date` este MUTABIL. `getRelease()` întoarce referința internă, nu o copie,
//   deci un apelant neatent poate modifica data din obiect fără să treacă prin setter.
// ======================================================================================
import java.util.Date;

/*
 * ======================================================================================
 * BLOC DE TEORIE: DE CE UN MODEL SEPARAT (POJO)
 * ======================================================================================
 *
 * 1. **Single Responsibility** — clasa are un singur motiv să se schimbe: se modifică
 *    structura datelor unui film. Nu se schimbă când se schimbă un layout, un buton
 *    sau o culoare. Dacă ai pune `getText().toString()` aici, clasa ar depinde de
 *    `android.widget.EditText` și ar avea două motive să se schimbe.
 *
 * 2. **Serializability** — fiind `Serializable` și fără referințe către `Context`,
 *    obiectul poate traversa granița dintre două activități. Un `Movie` care ar ține
 *    un `EditText` nu ar putea fi serializat: `View` nu este `Serializable`.
 *
 * 3. **Testability** — poți scrie un test JVM simplu care creează un `Movie` și
 *    verifică `getTitle()`. Fără emulator, fără Android. Asta se întâmplă pentru că
 *    în fișier nu există niciun `import android.*`.
 *
 * 4. **Fără câmp `id`** — identitatea filmului în listă este POZIȚIA, nu un ID.
 *    De aici vine tot mecanismul `POSITION_EXTRA` din celelalte două fișiere.
 *    Este o simplificare didactică: o bază de date reală ar avea un `id` stabil.
 *
 * VIZUAL: cum călătorește obiectul între activități
 *
 *   [MainActivity]                      [Intent]                     [ItemActivity]
 *   movies.get(position)                                                  |
 *         |                                                               |
 *         +-- putExtra("movie", obj) --+                                  |
 *                                      |                                  |
 *                          serialize (JVM -> bytes)                      |
 *                                      |                                  |
 *                                      +-- Bundle -- startActivity --> --+
 *                                                                         |
 *                                                       getSerializableExtra(...)
 *                                                                         |
 *                                                          O COPIE, nu originalul
 *
 *   Originalul rămâne în lista din MainActivity. Modificarea copiei NU se vede
 *   în listă. De aceea MainActivity face `movies.set(position, movie)` la final.
 * ======================================================================================
 */
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
    //   din `arrays.xml` ar schimba retroactiv genul tuturor filmelor salvate.
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
    //   nu mai găsește potrivirea și nu bifează nimic — silențios.
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
    //   controale s-ar contrazice la salvare.
    // ==================================================================================
    private boolean onWatchlist; //Checkbox

    // ==================================================================================
    // CÂMPUL 10: poster
    // ==================================================================================
    // TIP: String — un URL (sau orice text) către afișul filmului.
    // WIDGET SURSĂ: `etPoster` (inputType=textUri) -> `getText().toString()`.
    // DE CE `= null` explicit: `String` este oricum `null` implicit. Linia este
    //   DOCUMENTAȚIE: „acest câmp poate lipsi". Un film fără poster este valid.
    // RISC: `null` ajunge în `etPoster.setText(null)` la editare — legal, dar afișează
    //   câmp gol. Dacă ai apela `.length()` pe el, ai lua `NullPointerException`.
    // ==================================================================================
    private String poster = null;

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
    //     10      String    poster         etPoster (textUri)
    //
    //   Dacă inversezi pozițiile 1 și 3 (ambele String) sau 7 și 9 (ambele boolean),
    //   codul COMPILEAZĂ. Filmul se creează. Doar că `title` primește genul și
    //   `genre` primește titlul. Compilatorul nu te poate ajuta aici.
    // ==================================================================================
    public Movie(String title, Date release, String genre, double budget, int duration, float rating, boolean watched, String approval, boolean onWatchlist, String poster) {

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
        this.poster = poster;
    }

    // ==================================================================================
    // toString() — CONTRACTUL DE AFIȘARE ÎN LISTĂ
    // ==================================================================================
    // DE CE ESTE OBLIGATORIU AICI:
    //   `ArrayAdapter` cu `android.R.layout.simple_list_item_1` primește un `TextView`
    //   și îl umple cu `item.toString()`. Fără suprascriere, `Object.toString()` ar
    //   întoarce `ro.ase.ie.g1097.model.Movie@a1b2c3d` — adresa din memorie.
    //
    // FLUXUL EXACT:
    //   ListView.getView(position) -> ArrayAdapter.getView(...) -> TextView.setText(
    //   movies.get(position).toString())
    //
    // DE CE `@Override`: compilatorul verifică semnătura. Dacă scrii `tostring()`
    //   cu literă mică, fără adnotare nu primești nicio eroare — doar metoda ta
    //   nu este apelată niciodată.
    //
    // FORMATUL: generat de IntelliJ cu Alt+Insert -> toString(). `'\''` este un
    //   apostrof escapate, ca să nu închidă literalul de caracter.
    //
    // CE SE VEDE PE ECRAN: toate cele 10 câmpuri, pe un singur rând, inclusiv URL-ul
    //   posterului. Urât, dar corect. Se repară în capitolul următor cu RecyclerView
    //   și `movie_item.xml`.
    // ==================================================================================
    @Override
    public String toString() {

        // Concatenare de String-uri cu `+`. Fiecare `+` creează un obiect nou în memorie.
        // Pentru 10 câmpuri, diferența este neglijabilă; pentru bucle mari s-ar folosi
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
                ", onWatchlist=" + onWatchlist +
                ", poster='" + poster + '\'' +

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
    // de model și crapă abia în `fillForm` (vezi BUG 2).
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

    // GETTER pentru URL-ul posterului. Poate întoarce `null`.
    public String getPoster() {
        return poster;
    }

    // SETTER pentru poster. Acceptă `null` fără să se plângă.
    public void setPoster(String poster) {
        this.poster = poster;
    }

    // ==================================================================================
    // CONSTRUCTORUL FĂRĂ PARAMETRI — ULTIMA LINIE A FIȘIERULUI
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
    // DE CE ESTE LA SFÂRȘIT: poziția nu contează pentru compilator. Este la sfârșit
    //   pentru că așa l-a generat IntelliJ și pentru că cititorul îl vede după
    //   toate metodele de care depinde.
    // ==================================================================================
    public Movie() {
    }
}
```

---

## 22.2 `MainActivity.java` — lista și navigarea

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
 *
 * CE ȘTIE: lista, adapterul, cele două extra-uri, launcher-ul de rezultat.
 *   Nu știe cum arată formularul și nu validează date.
 *
 * CE S-AR RUPE FĂRĂ EL: aplicația ar porni direct într-un formular fără listă,
 *   iar rezultatul salvat nu ar avea unde să se întoarcă.
 * ======================================================================================
 */

package ro.ase.ie.g1097.activities;

// ======================================================================================
// IMPORTURI — GRUPATE PE SURSĂ
// ======================================================================================
// android.*        — clase din framework (Intent, Bundle, View, widget-uri)
// androidx.*       — biblioteci Jetpack (AppCompat, EdgeToEdge, insets, activity result)
// com.google.*     — Material Components (FloatingActionButton)
// java.util.*      — colecții și date
// ro.ase.ie.g1097  — modelul și clasa R generată
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

// ArrayList: implementarea concretă a listei.
import java.util.ArrayList;

// Calendar: câmpurile de dată (YEAR, MONTH, DAY_OF_MONTH) și constantele lunilor.
import java.util.Calendar;

// Date: tipul stocat în model pentru data de lansare.
import java.util.Date;

// GregorianCalendar: constructorul rapid „an, lună, zi" folosit în datele demo.
import java.util.GregorianCalendar;

// List: interfața de listă. Câmpul este declarat `List`, nu `ArrayList`.
import java.util.List;

// Modelul de date — singura dependență către `model`.
import ro.ase.ie.g1097.model.Movie;

// R: clasa generată din resurse. Aici pentru `R.layout.activity_main` și `R.id.*`.
import ro.ase.ie.g1097.R;

/*
 * ======================================================================================
 * BLOC DE TEORIE: ACTIVITY, INTENT, ADAPTER
 * ======================================================================================
 *
 * 1. **Activity = un ecran cu o stare.** `MainActivity` este un `Context` (are acces la
 *    resurse, temă, sistem) și un `LifecycleOwner` (are un ciclu de viață: onCreate ->
 *    onStart -> onResume -> onPause -> onStop -> onDestroy).
 *
 * 2. **Intent = un mesaj.** Un `Intent` explicit conține clasa destinatar și un `Bundle`
 *    de extra-uri. Pornirea se face cu `startActivity` (fără rezultat) sau cu un
 *    `ActivityResultLauncher` (cu rezultat).
 *
 * 3. **Adapter = traducătorul.** `ListView` nu știe ce este un `Movie`. `ArrayAdapter`
 *    știe: pentru fiecare poziție, ia `movies.get(position)` și îl transformă într-un
 *    rând de UI. Fără adapter, `ListView` ar afișa o listă de obiecte goale.
 *
 * 4. **Ordinea în onCreate este contract, nu stil.** Fiecare pas depinde de cel dinainte:
 *    fără `super`, AppCompat nu are delegate; fără `setContentView`, `findViewById`
 *    întoarce null; fără adapter, `setAdapter` primește null.
 *
 * VIZUAL: ciclul de viață în timpul unui insert
 *
 *   MainActivity:  onCreate -> onStart -> onResume -> onPause
 *                                                        |
 *                                                        v
 *   ItemActivity:                                   onCreate -> onStart -> onResume
 *                                                        |
 *                                                   (utilizatorul salvează)
 *                                                        |
 *                                                   setResult + finish
 *                                                        |
 *   MainActivity:  onStart -> onResume -> [callback launcher] -> listă redesenată
 *
 *   MainActivity NU este distrusă cât timp ItemActivity este deasupra. Este doar
 *   oprită. De aceea lista `movies` supraviețuiește și de aceea callback-ul o poate
 *   modifica direct.
 * ======================================================================================
 */
public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // CONSTANTELE DE EXTRA
    // ==================================================================================
    // DE CE CONSTANTE ȘI NU LITERALI: cheia „movie" este scrisă în două fișiere.
    //   Dacă într-un loc scrii "movie" și în altul "Movie", `getSerializableExtra`
    //   întoarce `null` FĂRĂ NICIO EROARE. Compilatorul nu te ajută cu String-uri.
    //
    // DE CE `protected`: `ItemActivity` este în același pachet, deci ar funcționa și
    //   `package-private`. `protected` documentează intenția: „se folosește din
    //   subclase / din cod apropiat".
    //
    // DE CE `static`: valoarea aparține clasei, nu instanței. `MainActivity.MOVIE_EXTRA`
    //   se poate scrie fără să existe un obiect MainActivity.
    //
    // DE CE `final`: cheia nu trebuie schimbată niciodată la runtime.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";

    // ==================================================================================
    // CÂMPUL 1: fabInsert
    // ==================================================================================
    // TIP: FloatingActionButton — butonul „+".
    // DE CE CÂMP: este legat în `initControls` și folosit în `initListeners`.
    //   O variabilă locală în `initControls` ar muri la sfârșitul metodei.
    // ==================================================================================
    private FloatingActionButton fabInsert;

    // ==================================================================================
    // CÂMPUL 2: listView
    // ==================================================================================
    // TIP: ListView — widget-ul care afișează rândurile.
    // DE CE CÂMP: legat în `initControls`, i se atașează listener în `initListeners`.
    // ==================================================================================
    private ListView listView;

    // ==================================================================================
    // CÂMPUL 3: launcher
    // ==================================================================================
    // TIP: ActivityResultLauncher<Intent> — obiectul returnat de `registerForActivityResult`.
    // DE CE CÂMP: este creat în `onCreate` și folosit în `initListeners`, în două
    //   locuri (FAB și click pe rând).
    // RISC DE ORDINE: `initListeners()` rulează ÎNAINTE de atribuirea acestui câmp.
    //   Funcționează doar pentru că listener-ii se execută la CLICK, nu la înregistrare.
    // ==================================================================================
    private ActivityResultLauncher<Intent> launcher;

    // ==================================================================================
    // CÂMPUL 4: movies
    // ==================================================================================
    // TIP: `final List<Movie>` inițializat cu `ArrayList`.
    // DE CE `List` și nu `ArrayList`: tipul declarat este interfața. Implementarea
    //   poate fi schimbată (ex. `LinkedList`) fără să modifici restul codului.
    // DE CE `final`: REFERINȚA nu se schimbă niciodată. Poți face `movies.add(...)`,
    //   `movies.set(...)`, dar nu `movies = new ArrayList<>()`.
    // DE CE `new ArrayList<>()` aici: lista trebuie să existe înainte de `onCreate`,
    //   pentru că `ArrayAdapter` primește referința la ea.
    // ==================================================================================
    private final List<Movie> movies = new ArrayList<>();

    // ==================================================================================
    // CÂMPUL 5: movieAdapter
    // ==================================================================================
    // TIP: ArrayAdapter<Movie> — adapterul care leagă lista de ListView.
    // DE CE NU este `final`: este atribuit în `onCreate`, după `addSampleMovies()`.
    // DE CE CÂMP: `notifyDataSetChanged()` este apelat din interiorul callback-ului,
    //   unde ai nevoie de aceeași instanță.
    // ==================================================================================
    private ArrayAdapter<Movie> movieAdapter;

    // ==================================================================================
    // onCreate — CONSTRUCTORUL DE FAPT AL ECRANULUI
    // ==================================================================================
    // Semnătura este impusă de framework: `protected void onCreate(Bundle)`.
    // `savedInstanceState` este `null` la prima creare și un `Bundle` la recreare
    //   (rotire de ecran, schimbare de temă). Aici NU este folosit: lista se pierde
    //   la rotire. Este o limitare cunoscută a acestui commit.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // PASUL 1: lansează lanțul de inițializare al clasei părinte.
        // CE FACE: AppCompat își instalează delegate-ul, încarcă tema, creează
        //   ActionBar-ul și pregătește `FragmentManager`-ul.
        // CE SE RUPE DACĂ LIPSEȘTE: `SuperNotCalledException` la `onStart`, sau
        //   `NullPointerException` în `setContentView` pentru că delegate-ul nu există.
        // CE SE RUPE DACĂ E PREA TÂRZIU (după setContentView): AppCompat nu mai poate
        //   aplica tema pe fereastră; poți vedea un flash de culoare greșită.
        super.onCreate(savedInstanceState);

        // PASUL 2: activează modul edge-to-edge.
        // CE FACE: setează ferestrele să deseneze și sub barele de sistem, astfel
        //   încât conținutul să poată ocupa tot ecranul. Barele devin transparente.
        // DE CE ÎNAINTE DE setContentView: configurarea ferestrei trebuie făcută
        //   înainte ca prima vedere să fie atașată, altfel poți vedea o recolorare.
        // CONSECINȚĂ: conținutul intră SUB ceas și sub bara de navigare. De aceea
        //   pasul 4 aplică padding.
        EdgeToEdge.enable(this);

        // PASUL 3: umple fereastra cu arborele de view-uri din XML.
        // CE FACE: inflatează `res/layout/activity_main.xml` și îl atașează la fereastră.
        // DE CE ÎNAINTE DE findViewById: înainte de acest apel, `findViewById` nu are
        //   unde să caute și întoarce `null` pentru orice ID.
        // CE SE RUPE DACĂ LIPSEȘTE: ecran alb; orice `findViewById` -> null -> NPE.
        setContentView(R.layout.activity_main);

        // PASUL 4: aplică padding egal cu barele de sistem pe rădăcină.
        // ==============================================================================
        // VIZUAL: zona sigură (safe area)
        //
        //   +--------------------------------------------------+  ^
        //   |  ceas   baterie   notificări                     |  | status bar (~24dp)
        //   +--------------------------------------------------+  v
        //   |                                                  |  ^
        //   |                                                  |  |
        //   |            CONȚINUT (padding aplicat)            |  | ecran
        //   |                                                  |  |
        //   |                                                  |  |
        //   +--------------------------------------------------+  v
        //   |  back   home   recente                           |  ^  navigation bar (~48dp)
        //   +--------------------------------------------------+  v
        //
        //   Fără padding: primul rând din listă intră sub ceas, iar FAB-ul intră
        //   sub bara de navigare și devine imposibil de apăsat.
        //   Cu padding pe R.id.main: TOȚI copiii sunt împinși în zona sigură.
        // ==============================================================================
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // Extrage insets-urile pentru „systemBars": status bar + navigation bar
            // + caption bar. Nu include tastatura (IME), care ar fi `Type.ime()`.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // Aplică padding pe toate cele patru laturi, în pixeli.
            // DE CE pe rădăcină: padding-ul pe un copil ar împinge doar acel copil;
            //   ceilalți ar rămâne sub bare.
            // EFECT SECUNDAR: padding-ul se REAPLICĂ la fiecare schimbare de insets
            //   (rotire, bară de navigare care apare/dispare). `setPadding` nu adună,
            //   ci înlocuiește — deci nu se acumulează.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // `return insets` (nu `CONSUMED`): insets-urile continuă să circule către
            // copii. Dacă ai returna `WindowInsetsCompat.CONSUMED`, niciun copil nu
            // ar mai primi informația și ar trebui să își aplice singur padding.
            return insets;
        });

        // PASUL 5: umple lista cu 3 filme demo.
        // DE CE ÎNAINTE de crearea adapterului: adapterul primește REFERINȚA la listă.
        //   Umplând lista înainte, adapterul vede deja 3 elemente la construcție și
        //   nu ai nevoie de `notifyDataSetChanged()`.
        // Dacă ai apela `addSampleMovies()` după `new ArrayAdapter(...)`, ar funcționa
        //   și atunci (aceeași referință), dar ar trebui un `notifyDataSetChanged()`
        //   ca ListView-ul să redeseneze.
        addSampleMovies();

        // PASUL 6: creează adapterul.
        // Parametri:
        //   1. `this` — Context-ul (MainActivity este un Context).
        //   2. `android.R.layout.simple_list_item_1` — un layout care conține UN TextView.
        //   3. `movies` — lista de date, ținută prin REFERINȚĂ, nu copiată.
        // DE CE `android.R.layout` și nu `R.layout`: este un layout din framework,
        //   nu din proiect.
        // DE CE `<>` (diamond): compilatorul deduce `ArrayAdapter<Movie>` din `movies`.
        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

        // PASUL 7: leagă view-urile de câmpuri și atașează adapterul.
        // DE CE DUPĂ crearea adapterului: `initControls` face `listView.setAdapter(movieAdapter)`.
        //   Dacă `movieAdapter` ar fi null, `setAdapter(null)` ar lăsa lista goală.
        initControls();

        // PASUL 8: atașează listener-ii.
        // DE CE DUPĂ `initControls`: listener-ii au nevoie de `fabInsert` și `listView`,
        //   care sunt atribuite acolo. Înainte, ar fi null -> NPE la înregistrare.
        // OBSERVAȚIE: `launcher` este încă null în acest moment. Vezi pasul 9.
        initListeners();

        // PASUL 9: înregistrează callback-ul pentru rezultat.
        // ==============================================================================
        // DE CE AICI ȘI NU ÎNTR-UN LISTENER:
        //   `registerForActivityResult` trebuie apelat ÎNAINTE ca activitatea să
        //   ajungă în starea STARTED. Altfel primești:
        //   "LifecycleOwner ... is attempting to register while current state is RESUMED.
        //    LifecycleOwners must call register before they are STARTED."
        //   De aceea înregistrarea stă în `onCreate`, nu în `onClick`.
        //
        // FLUXUL:
        //   [onCreate] registerForActivityResult(contract, callback)
        //        |
        //        v
        //   [click FAB] launcher.launch(intent)
        //        |
        //        v
        //   ItemActivity se deschide; MainActivity -> onPause
        //        |
        //        v
        //   ItemActivity: setResult(RESULT_OK, intent) + finish()
        //        |
        //        v
        //   MainActivity revine: onStart -> onResume
        //        |
        //        v
        //   callback.onActivityResult(result)   <-- aici se modifică lista
        // ==============================================================================
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // Callback-ul este o clasă anonimă. Se poate scrie și cu lambda, dar
                // sursa folosește forma explicită — utilă la examen pentru claritate.
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // VERIFICARE OBLIGATORIE: a venit un rezultat bun?
                        // Dacă utilizatorul apasă Back, `ItemActivity` se închide cu
                        // RESULT_CANCELED, iar `o.getData()` este null.
                        // Fără acest `if`, următorul `intent.getSerializableExtra`
                        // ar arunca NullPointerException.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // Extrage Intent-ul de rezultat. Poate fi null dacă
                            // activitatea a apelat `setResult(RESULT_OK)` fără Intent —
                            // aici nu se întâmplă, dar este un risc teoretic.
                            Intent intent = o.getData();

                            // Citește obiectul serializat. Cast-ul este necesar pentru
                            // că `getSerializableExtra` întoarce `Serializable`.
                            // RISC: dacă obiectul nu ar fi `Movie`, cast-ul ar arunca
                            //   `ClassCastException` la runtime.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // Citește poziția. Valoarea implicită `-1` este CHEIA
                            // întregului protocol: -1 înseamnă „nu există poziție",
                            // adică insert.
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // MOD INSERT: ItemActivity nu a trimis poziție.
                            if(position == -1)
                            {
                                // Adaugă la finalul listei.
                                movies.add(movie);

                                // Anunță adapterul că datele s-au schimbat.
                                // FĂRĂ ACEASTĂ LINIE: filmul este în listă, dar
                                // ListView-ul nu se redesenează și utilizatorul
                                // nu vede nimic până la următoarea recreare.
                                movieAdapter.notifyDataSetChanged();
                            }
                            // MOD EDIT: ItemActivity a trimis poziția.
                            else
                            {
                                // Înlocuiește elementul de la poziția respectivă.
                                // `set` nu schimbă dimensiunea listei.
                                movies.set(position, movie);

                                // Și aici este obligatoriu: `set` nu notifică nimeni.
                                movieAdapter.notifyDataSetChanged();
                            }
                        }

                        // Dacă resultCode != RESULT_OK, nu facem nimic. Lista rămâne
                        // neatinsă, exact ca înainte de deschiderea formularului.
                    }
                });
    }

    // ==================================================================================
    // initListeners — CE SE ÎNTÂMPLĂ LA INTERACȚIUNE
    // ==================================================================================
    // Două acțiuni: FAB (insert) și click pe rând (edit).
    // Ambele pornesc ACEEAȘI activitate, cu extra-uri diferite.
    // ==================================================================================
    private void initListeners() {

        // FAB -> INSERT
        // Clasă anonimă `View.OnClickListener` cu o singură metodă `onClick`.
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // `MainActivity.this` și NU `this`.
                // ==========================================================================
                // DE CE: în interiorul clasei anonime, `this` este INSTANȚA LISTENER-ULUI,
                //   nu activitatea. `new Intent(this, ItemActivity.class)` ar căuta un
                //   constructor `Intent(View.OnClickListener, Class)` — inexistent —
                //   și NU ar compila.
                // `MainActivity.this` este referința calificată către instanța exterioară,
                //   care ESTE un `Context`.
                // ==========================================================================
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // Pornește activitatea PRIN LAUNCHER, nu prin `startActivity`.
                // DE CE: `startActivity` pornește ecranul, dar nu are unde să întoarcă
                //   rezultatul. `launcher.launch` știe cine primește răspunsul.
                // FĂRĂ EXTRA-URI: ItemActivity vede `existing == null` -> insert mode.
                launcher.launch(intent);
            }
        });

        // CLICK PE RÂND -> EDIT
        // `AdapterView.OnItemClickListener` are o singură metodă cu 4 parametri.
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                // Parametrii:
                //   `parent`   — ListView-ul (aici nu e folosit)
                //   `view`     — rândul apăsat (aici nu e folosit)
                //   `position` — indexul din adapter; ASTA ne interesează
                //   `id`       — id-ul rândului; pentru ArrayAdapter este egal cu poziția

                // Același tip de Intent: aceeași activitate, alt conținut.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // Trimite filmul selectat. `putExtra(String, Serializable)` este
                // suprascrierea aleasă pentru că `Movie implements Serializable`.
                // OBIECTUL ESTE SERIALIZAT — în ItemActivity ajunge o COPIE.
                intent.putExtra(MOVIE_EXTRA, movies.get(position));

                // Trimite și poziția. Ea este singurul lucru care distinge edit de insert.
                // `int` -> `putExtra(String, int)`.
                intent.putExtra(POSITION_EXTRA, position);

                // Pornește pentru rezultat, exact ca la insert.
                launcher.launch(intent);
            }
        });
    }

    // ==================================================================================
    // initControls — LEGĂTURA XML <-> COD
    // ==================================================================================
    // Trei linii, trei responsabilități: două `findViewById` și o atașare de adapter.
    // ==================================================================================
    private void initControls() {

        // `findViewById` caută în arborele inflat la `setContentView`.
        // În Java modern, metoda este generică: tipul se deduce din variabila din stânga.
        //   Echivalentul vechi: `(FloatingActionButton) findViewById(R.id.floatingActionButton)`.
        // Dacă ID-ul nu există în layout, întoarce `null` FĂRĂ eroare — NPE la primul acces.
        fabInsert = findViewById(R.id.floatingActionButton);

        // Același lucru pentru listă. ID-ul `listView` există în `activity_main.xml`.
        listView = findViewById(R.id.listView);

        // Atașează adapterul. Din acest moment, ListView-ul știe ce să afișeze.
        // DE CE ULTIMA LINIE: are nevoie de `listView` (deja atribuit) și de
        //   `movieAdapter` (atribuit în onCreate înainte de apelul acestei metode).
        listView.setAdapter(movieAdapter);
    }

    // ==================================================================================
    // addSampleMovies — DATELE DEMO
    // ==================================================================================
    // Trei filme construite cu constructorul cu 10 parametri. Aici se vede, în practică,
    // capcana pozițională descrisă în 22.1: fiecare apel are exact 10 argumente, în
    // ordinea din semnătură.
    //
    // DE CE EXISTĂ: ca să ai ce vedea la prima pornire, fără să introduci date manual.
    // DE CE ÎN COD ȘI NU ÎN RESURSE: sunt obiecte, nu texte; un array XML ar cere
    //   parsare și conversii de tip.
    // ==================================================================================
    private void addSampleMovies() {

        // FILMUL 1: Inception
        // Argumentele, în ordine:
        //   1. "Inception"                                          -> String title
        //   2. new GregorianCalendar(2010, Calendar.JULY, 16).getTime() -> Date release
        //   3. "Sci-Fi"                                             -> String genre
        //   4. 160000000                                            -> double budget
        //   5. 148                                                  -> int duration
        //   6. 4.5f                                                 -> float rating
        //   7. true                                                 -> boolean watched
        //   8. "PG-13"                                              -> String approval
        //   9. false                                                -> boolean onWatchlist
        //  10. "https://example.com/posters/inception.jpg"          -> String poster
        movies.add(new Movie(
                "Inception",

                // `GregorianCalendar(an, lună, zi)`:
                //   - anul este ABSOLUT (2010), nu relativ;
                //   - luna este 0-INDEXATĂ: `Calendar.JULY` = 6, nu 7. De aceea se
                //     folosesc constantele, nu numerele — `new GregorianCalendar(2010, 7, 16)`
                //     ar însemna 16 AUGUST;
                //   - ziua este 1-indexată, ca în viața reală.
                // `.getTime()` transformă Calendar-ul într-un `Date` (milisecunde).
                //   `GregorianCalendar` ESTE un `Calendar`, dar NU este un `Date`.
                new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),

                // Genul — text simplu, nu trebuie să existe în `@array/movie_genre`.
                "Sci-Fi",

                // Bugetul: literal `int` (160 000 000) lărgit automat la `double`.
                // Nu are nevoie de sufix; `160000000.0` ar fi echivalent.
                160000000,

                // Durata: literal `int`, în minute.
                148,

                // Rating: literal `float`. Sufixul `f` este OBLIGATORIU.
                // Fără el, `4.5` ar fi `double` și nu s-ar potrivi la parametrul `float`
                // fără cast explicit.
                4.5f,

                // `watched` — film văzut.
                true,

                // `approval` — textul butonului radio, nu ID-ul.
                "PG-13",

                // `onWatchlist` — nu este pe lista de revăzut.
                false,

                // `poster` — URL fictiv. Nu este descărcat nicăieri în acest commit.
                "https://example.com/posters/inception.jpg"));

        // FILMUL 2: Toy Story
        // Aceeași structură, alte valori. `Calendar.NOVEMBER` = 10 (0-indexat).
        // `4f` este tot un literal `float`, doar fără zecimale.
        // ATENȚIE: genul „Animation" NU există în `@array/movie_genre` (Drama, Action,
        //   Comedy, Horror, Romance, Thriller, Sci-Fi, Adventure, Fantasy, Mystery).
        //   Consecința apare la editare: `fillForm` nu găsește potrivirea, spinner-ul
        //   rămâne pe „Drama", iar salvarea schimbă genul filmului. Vezi 22.3.
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

        // FILMUL 3: The Matrix
        // `Calendar.MARCH` = 2 (0-indexat). `5f` = rating maxim.
        // `watched = false` și `onWatchlist = true` — combinația „nu l-am văzut,
        // dar vreau să-l văd". Este singurul film din cele trei cu această combinație,
        // utilă pentru verificarea celor două controale independente.
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
}
```

**Ce trebuie reținut din acest fișier:**

| Element | De ce contează |
|---|---|
| Ordinea din `onCreate` | fiecare pas depinde de cel dinainte; `launcher` este ultimul |
| `EdgeToEdge` + insets | fără padding pe `R.id.main`, conținutul intră sub bare |
| `new ArrayAdapter(..., movies)` | ține REFERINȚA la listă, nu o copie |
| `notifyDataSetChanged()` | singurul mod prin care ListView află de schimbare |
| `registerForActivityResult` | obligatoriu înainte de `STARTED`, deci în `onCreate` |
| `MainActivity.this` | în clasa anonimă, `this` nu este `Context` |

---

## 22.3 `ItemActivity.java` — formularul

```java
/*
 * ======================================================================================
 * FIȘIER: ItemActivity.java — FORMULARUL DE INSERT / EDIT
 * ======================================================================================
 * CE ESTE: o activitate cu 13 view-uri, un Calendar și un formatter de dată.
 *   Construiește un `Movie` din valorile din formular și îl trimite înapoi.
 *
 * DE CE EXISTĂ: `MainActivity` nu are voie să creeze obiecte de model dintr-un formular.
 *   Separarea înseamnă că formularul poate fi schimbat (alt layout, alte câmpuri) fără
 *   să atingi lista.
 *
 * CE ȘTIE: valorile curente ale celor 10 câmpuri, modul (insert sau edit) și poziția.
 *   Nu știe ce se întâmplă cu filmul după `finish()`.
 *
 * CE S-AR RUPE FĂRĂ EL: aplicația ar avea doar lista demo, fără posibilitatea de a
 *   adăuga sau modifica un film.
 * ======================================================================================
 */

package ro.ase.ie.g1097.activities;

// ======================================================================================
// IMPORTURI — CE ADUCE FIECARE
// ======================================================================================
// android.app.DatePickerDialog   — dialogul de alegere a datei
// android.content.Intent         — citirea extra-urilor la intrare și construirea
//                                  Intent-ului de rezultat
// android.os.Bundle              — semnătura lui onCreate
// android.view.View              — parametrul din listener-ii de click
// android.widget.*               — cele 13 widget-uri ale formularului
// androidx.activity.EdgeToEdge   — desenare sub barele de sistem
// androidx.annotation.NonNull    — contractul lui OnCheckedChangeListener
// androidx.core.content.IntentCompat — citirea tipată a unui Serializable (API 33+)
// androidx.core.view.*           — insets
// com.google.android.material.*  — MaterialSwitch, Snackbar
// java.text.*                    — parsare și formatare de dată
// java.util.*                    — Calendar, Date, Locale
// ro.ase.ie.g1097.*              — R, binding, model
// ======================================================================================

// Dialogul nativ cu calendar. Se deschide la click pe câmpul de dată.
import android.app.DatePickerDialog;

// Intent: la intrare, aduce filmul de editat; la ieșire, duce filmul salvat.
import android.content.Intent;

// Bundle: starea salvată de sistem. Neutilizat în corp, doar în semnătură.
import android.os.Bundle;

// View: tipul parametrului din `OnClickListener`.
import android.view.View;

// Button: tipul butonului de salvare. În XML este `MaterialButton`, care extinde Button.
import android.widget.Button;

// CheckBox: tipul declarat al câmpului, deși obiectul real este `MaterialCheckBox`.
import android.widget.CheckBox;

// CompoundButton: interfața comună pentru Switch și CheckBox; apare în listener.
import android.widget.CompoundButton;

// DatePicker: primul parametru al callback-ului `OnDateSetListener`.
import android.widget.DatePicker;

// EditText: tipul declarat pentru cele 4 câmpuri text.
import android.widget.EditText;

// RadioButton: folosit la bucla peste copiii lui RadioGroup.
import android.widget.RadioButton;

// RadioGroup: containerul celor 5 butoane de ghidaj.
import android.widget.RadioGroup;

// RatingBar: stelele.
import android.widget.RatingBar;

// SeekBar: slider-ul de durată.
import android.widget.SeekBar;

// Spinner: lista derulantă de genuri.
import android.widget.Spinner;

// Switch: importat, dar câmpul este declarat `MaterialSwitch`.
import android.widget.Switch;

// TextView: etichetele dinamice pentru durată și watched.
import android.widget.TextView;

// Toast: importat în sursă, dar NEUTILIZAT în acest fișier.
import android.widget.Toast;

// EdgeToEdge: conținut sub barele de sistem.
import androidx.activity.EdgeToEdge;

// NonNull: adnotarea din semnătura lui onCheckedChanged.
import androidx.annotation.NonNull;

// AppCompatActivity: clasa de bază.
import androidx.appcompat.app.AppCompatActivity;

// IntentCompat: variantă compatibilă cu API 33 pentru citirea unui Serializable tipat.
import androidx.core.content.IntentCompat;

// Insets: valorile barelor de sistem.
import androidx.core.graphics.Insets;

// ViewCompat: listener-ul de insets compatibil.
import androidx.core.view.ViewCompat;

// WindowInsetsCompat: tipurile de insets.
import androidx.core.view.WindowInsetsCompat;

// MaterialSwitch: switch-ul Material (nu cel din framework).
import com.google.android.material.materialswitch.MaterialSwitch;

// Snackbar: importat, dar NEUTILIZAT. Rămășiță de la o versiune anterioară.
import com.google.android.material.snackbar.Snackbar;

// ParseException: excepția aruncată de `SimpleDateFormat.parse`.
import java.text.ParseException;

// SimpleDateFormat: formatarea și parsarea „dd/MM/yyyy".
import java.text.SimpleDateFormat;

// Calendar: sursa de adevăr pentru dată.
import java.util.Calendar;

// Date: tipul din model.
import java.util.Date;

// Locale: formatul de dată depinde de limba dispozitivului.
import java.util.Locale;

// R: ID-urile din layout.
import ro.ase.ie.g1097.R;

// ActivityItemBinding: generat de View Binding. Importat, dar NEUTILIZAT —
//   sursa folosește `findViewById`. Rămășiță de la o variantă cu binding.
import ro.ase.ie.g1097.databinding.ActivityItemBinding;

// Modelul.
import ro.ase.ie.g1097.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: FORMULARUL CA MAȘINĂ DE STARE
 * ======================================================================================
 *
 * 1. **Două moduri, o singură activitate.** `ItemActivity` nu are două layout-uri și
 *    două clase. Are un câmp `position` care este `-1` (insert) sau `>= 0` (edit).
 *    Tot comportamentul diferit derivă din acest câmp.
 *
 * 2. **Sursa de adevăr nu este întotdeauna widget-ul.** Pentru 9 câmpuri, widget-ul
 *    este sursa (citești direct din el la salvare). Pentru dată, sursa este
 *    `releaseCal`, iar `EditText`-ul este doar o AFIȘARE.
 *
 * 3. **Listener-ii sunt și ei sursă de adevăr pentru etichete.** `tvDurationValue`
 *    și `tvWatchedValue` nu sunt citite la salvare; sunt actualizate de listener-ii
 *    widget-urilor. Dacă un listener nu se declanșează, eticheta rămâne în urmă.
 *
 * 4. **Rezultatul este un Intent.** Activitatea nu întoarce un obiect prin return;
 *    îl pune într-un `Intent` și îl predă prin `setResult`.
 *
 * VIZUAL: fluxul de date în formular
 *
 *   [etTitle] -------------------------+
 *   [etRelease] --(doar afișare)--+    |
 *                                 |    |
 *   [releaseCal] -----------------+----+---> saveMovie() ---> Movie ---> Intent
 *   [spGenre] -------------------------+                                    |
 *   [etBudget] ------------------------+                                    v
 *   [sbDuration] ----------------------+                            setResult(RESULT_OK)
 *   [rbRating] ------------------------+                                    |
 *   [swWatched] -----------------------+                                    v
 *   [cbonWatchList] -------------------+                                  finish()
 *   [rgApproval] --(buclă)--+----------+
 *   [etPoster] ------------------------+
 * ======================================================================================
 */
public class ItemActivity extends AppCompatActivity {

    // ==================================================================================
    // CELE 13 REFERINȚE LA VIEW-URI
    // ==================================================================================
    // DE CE 13: formularul are 10 câmpuri de date + 2 etichete dinamice + 1 buton.
    //   Cele 7 `TextView`-uri de etichetă fixă (`tvTile`, `tvGenre`, `tvBudget`,
    //   `tvDuration`, `tvRating`, `tvWatched`, `tvGuidance`) NU apar aici: nu sunt
    //   citite și nu sunt modificate din cod, deci nu au nevoie de referință.
    //
    // DE CE TOATE SUNT `private`: sunt detalii de implementare ale ecranului.
    // ==================================================================================

    // Câmpul 1: titlul. Obiectul real din XML este `TextInputEditText`, dar tipul
    // declarat este `EditText` — clasa părinte. Este suficient pentru `getText()`.
    private EditText etTitle;

    // Câmpul 2: data, ca TEXT. Valoarea reală este în `releaseCal` (vezi mai jos).
    private EditText etRelease;

    // Câmpul 3: genul. `Spinner` — lista derulantă din `@array/movie_genre`.
    private Spinner spGenre;

    // Câmpul 4: bugetul. `inputType="numberDecimal"` în XML.
    private EditText etBudget;

    // Câmpul 5: durata. `SeekBar` cu max 300.
    private SeekBar sbDuration;

    // Câmpul 6: rating-ul. `RatingBar` cu 5 stele și pas 0.5.
    private RatingBar rbRating;

    // Câmpul 7: ghidajul parental. `RadioGroup` cu 5 butoane.
    private RadioGroup rgApproval;

    // Câmpul 8: bifa „Watchlist".
    // ATENȚIE LA NUME: câmpul este `cbonWatchList`, ID-ul este `cbOnWatchList`.
    //   Un `o` lipsă într-o parte, un `O` în plus în cealaltă. Nu este typo de corectat:
    //   așa este sursa. `findViewById(R.id.cbonWatchList)` NU ar compila.
    private CheckBox cbonWatchList;

    // Câmpul 9: switch-ul „Recommended". Tipul real este `MaterialSwitch`, care
    // extinde `SwitchCompat` -> `CompoundButton`. Declarat `MaterialSwitch` pentru
    // a avea acces la toate metodele lui.
    private MaterialSwitch swWatched;

    // Câmpul 10: URL-ul posterului.
    private EditText etPoster;

    // Câmpul 11: butonul de salvare.
    // ATENȚIE LA NUME: câmpul este `btMovieAction`, ID-ul este `btnMovieAction`.
    private Button btMovieAction;

    // Câmpul 12: eticheta care afișează durata („148 min."). NU este citită la
    // salvare — este doar afișare, actualizată de listener-ul SeekBar-ului.
    private TextView tvDurationValue;

    // Câmpul 13: eticheta care afișează „Yes"/„No" pentru switch.
    private TextView tvWatchedValue;

    // ==================================================================================
    // STAREA FORMULARULUI
    // ==================================================================================

    // MODUL: -1 = insert, >= 0 = edit.
    // DE CE `-1` și nu `0`: `0` este o poziție validă în listă. Sentinel-ul trebuie
    //   să fie o valoare IMPOSIBILĂ ca poziție.
    // CINE ÎL SCHIMBĂ: doar `onCreate`, când găsește un film în Intent.
    private int position = -1;   // -1 = insert mode

    // SURSA DE ADEVĂR PENTRU DATĂ.
    // `Calendar.getInstance()` = data și ora CURENTĂ. De aceea formularul pornește
    //   cu data de azi, nu cu o dată goală.
    // DE CE NU `null`: `saveMovie` apelează `releaseCal.getTime()` necondiționat.
    //   Un `null` ar arunca NPE la prima salvare.
    // DE CE `Calendar` și nu `Date`: `Calendar` are câmpuri (YEAR, MONTH, DAY_OF_MONTH)
    //   pe care `DatePickerDialog` le citește și le scrie direct.
    private Calendar releaseCal = Calendar.getInstance();

    // FORMATTER-UL DE DATĂ.
    // „dd/MM/yyyy" = zi cu 2 cifre / lună cu 2 cifre / an cu 4 cifre.
    //   ATENȚIE: `MM` = lună, `mm` = minute. Inversarea este o greșeală clasică.
    // `Locale.getDefault()` = formatul limbii dispozitivului. Aici pattern-ul este
    //   explicit, deci Locale influențează doar simbolurile și ordinea internă.
    // `final`: referința nu se schimbă. Obiectul, însă, este MUTABIL.
    // RISC: `SimpleDateFormat` nu este thread-safe. Aici este folosit exclusiv pe
    //   UI thread, deci nu există concurență.
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    // ==================================================================================
    // onCreate — TREI FAZE: INFRASTRUCTURĂ, CONTROALE, MOD
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // Faza 0: lanțul AppCompat. Fără el, tema și delegate-ul nu există.
        super.onCreate(savedInstanceState);

        // Edge-to-edge: conținutul poate ocupa tot ecranul, inclusiv sub bare.
        // Aici rădăcina este un `ScrollView` cu `android:id="@+id/main"`.
        EdgeToEdge.enable(this);

        // Inflatează `activity_item.xml`. Toate cele 13 `findViewById` depind de el.
        setContentView(R.layout.activity_item);

        // Insets pe rădăcina ScrollView. Identic cu MainActivity, dar aici padding-ul
        // este aplicat pe un container care DERULEAZĂ: conținutul se derulează în
        // interiorul zonei sigure, nu sub ea.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Faza 1: leagă cele 13 view-uri de câmpuri.
        // DE CE PRIMA: `fillForm` are nevoie de ele, iar `initListeners` la fel.
        initControls();

        // Faza 2: atașează listener-ii.
        // DE CE ÎNAINTE DE `fillForm`: `fillForm` apelează `setChecked` și `setProgress`.
        //   Aceste apeluri DECLANȘEAZĂ listener-ii, care actualizează etichetele
        //   `tvWatchedValue` și `tvDurationValue`. Dacă listener-ii ar fi atașați după
        //   `fillForm`, etichetele ar rămâne cu valorile implicite din XML.
        initListeners();

        // Faza 3: citește Intent-ul de intrare.
        Intent intent = getIntent();

        // Citire TIPATĂ a serializable-ului.
        // ==============================================================================
        // DE CE `IntentCompat` ȘI NU `intent.getSerializableExtra(...)`:
        //   Metoda veche este depreciată din API 33. `IntentCompat.getSerializableExtra`
        //   primește și clasa așteptată, deci face verificarea tipului înainte de cast
        //   și funcționează identic pe toate versiunile.
        // DE CE `MainActivity.MOVIE_EXTRA`: aceeași constantă ca la trimitere. O greșeală
        //   de literă aici ar produce `null` fără nicio eroare.
        // VALOAREA: `null` în modul insert (FAB-ul nu pune niciun extra).
        // ==============================================================================
        Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);

        // MOD EDIT: există un film în Intent.
        if (existing != null) {

            // Citește poziția. Aici `-1` ar însemna „film trimis fără poziție" —
            // un caz care nu se întâmplă în fluxul normal, dar ar transforma salvarea
            // într-un insert (duplicat).
            position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);

            // Umple formularul cu valorile filmului primit.
            // OBIECTUL ESTE O COPIE: modificările din formular NU ajung în lista din
            // MainActivity decât prin Intent-ul de rezultat.
            fillForm(existing);

            // Schimbă titlul ecranului. `setTitle` este metoda Activity-ului,
            //   NU setter-ul modelului — nu există conflict, destinatarul diferă.
            // ATENȚIE: tema aplicației este `Theme.Material3.DayNight.NoActionBar`
            //   (vezi `themes.xml`), iar layout-ul nu conține niciun `Toolbar`.
            //   Fără ActionBar, titlul nu se vede nicăieri pe ecran — schimbarea
            //   este reală, dar invizibilă. Feedback-ul vizibil pentru utilizator
            //   este textul butonului, setat pe linia următoare.
            setTitle("Edit movie");

            // Schimbă textul butonului. Același buton face insert sau update;
            //   eticheta este singura diferență vizibilă pentru utilizator.
            btMovieAction.setText("Update Movie");
        }

        // MOD INSERT: `existing == null`. Nu se întâmplă nimic.
        //   `position` rămâne -1, formularul rămâne cu valorile implicite din XML:
        //   titlu gol, dată = azi, gen = primul din listă, buget gol, durată 0,
        //   rating 0, switch oprit, bifă oprită, „G" bifat, poster gol.
    }

    // ==================================================================================
    // fillForm — MODEL -> WIDGET-URI
    // ==================================================================================
    // 10 câmpuri, în ordinea din model. Fiecare linie este inversul unei linii din
    // `saveMovie`.
    // ==================================================================================
    private void fillForm(Movie existing) {

        // Text: `getText().toString()` la salvare, `setText(...)` la umplere.
        // `setText` așteaptă `CharSequence`; `String` este un `CharSequence`.
        etTitle.setText(existing.getTitle());

        // BUG 2: `existing.getRelease()` poate fi `null`.
        // ==============================================================================
        // `SimpleDateFormat.format(null)` aruncă `NullPointerException`.
        // CÂND SE ÎNTÂMPLĂ: când filmul editat are `release == null`. În fluxul demo
        //   toate cele 3 filme au dată, deci bug-ul nu se vede. Devine real dacă un
        //   `Movie` este construit cu constructorul gol și salvat fără dată, sau dacă
        //   datele vin dintr-o sursă externă.
        // REPARAȚIE: `if (existing.getRelease() != null) { ... } else { etRelease.setText(""); }`
        // ==============================================================================
        etRelease.setText(dateFormat.format(existing.getRelease()));

        // BUG 3: `String.valueOf(double)` produce notație științifică pentru valori mari.
        // ==============================================================================
        // `String.valueOf(160000000.0)` -> "1.6E8".
        // Utilizatorul vede „1.6E8" în câmpul de buget. `Double.parseDouble("1.6E8")`
        //   funcționează, deci valoarea se salvează corect — dar afișarea este urâtă
        //   și pare o eroare.
        // REPARAȚIE: `String.format(Locale.getDefault(), "%.0f", existing.getBudget())`
        //   sau un `DecimalFormat`.
        // ==============================================================================
        etBudget.setText(String.valueOf(existing.getBudget()));

        // `SeekBar.setProgress(int)` — valoarea este limitată automat la 0..max.
        // Dacă durata din model ar fi 500, bara s-ar opri la 300.
        // EFECT SECUNDAR: dacă valoarea se SCHIMBĂ, se declanșează `onProgressChanged`
        //   și eticheta `tvDurationValue` se actualizează. Dacă valoarea este deja 0
        //   (implicită), listener-ul NU se declanșează — dar eticheta din XML este
        //   deja „0 min", deci rezultatul este corect.
        sbDuration.setProgress(existing.getDuration());

        // `CheckBox.setChecked(boolean)` — nu are listener, deci nicio reacție în lanț.
        cbonWatchList.setChecked(existing.isOnWatchlist());

        // `setChecked` pe switch DECLANȘEAZĂ `OnCheckedChangeListener`.
        // Efectul: `tvWatchedValue` primește „Yes" sau „No".
        // DE ACEASTA linie depinde ordinea din `onCreate`: listener-ul trebuie să
        //   fie deja atașat când `fillForm` rulează.
        swWatched.setChecked(existing.isWatched());

        // `RatingBar.setRating(float)` — parametrul este `float`, exact tipul din model.
        // Fără listener: stelele se desenează direct.
        rbRating.setRating(existing.getRating());

        // `setText(null)` este legal: câmpul devine gol. Nu aruncă excepție.
        etPoster.setText(existing.getPoster());

        // ==============================================================================
        // BUCLA PENTRU SPINNER — potrivire pe TEXT
        // ==============================================================================
        // `Spinner` nu are `setSelectionByValue`. Are doar `setSelection(int)`.
        //   Deci trebuie să cauți indexul corespunzător valorii din model.
        // `getCount()` = numărul de elemente din `@array/movie_genre`.
        // `getItemAtPosition(index)` întoarce `Object`; aici, un `String`.
        // `equals` (nu `==`): compară conținutul, nu referințele.
        // RISC CONCRET: „Animation" (genul lui Toy Story) nu există în
        //   `@array/movie_genre`. Bucla nu găsește nimic, spinner-ul rămâne pe
        //   poziția 0 („Drama"), iar la salvare filmul își schimbă genul FĂRĂ
        //   să anunțe nimeni. Este cel mai probabil loc în care vei pierde puncte
        //   la o demonstrație live, pentru că nu apare nicio eroare.
        // ==============================================================================
        for(int index=0; index<spGenre.getCount(); index++)
        {
            if(spGenre.getItemAtPosition(index).equals(existing.getGenre()))
            {
                // Setează selecția și oprește bucla. Fără `break`, ar continua
                //   degeaba — dar rezultatul ar fi identic.
                spGenre.setSelection(index);
                break;
            }
        }

        // ==============================================================================
        // BUCLA PENTRU RADIOGROUP — potrivire pe TEXTUL BUTONULUI
        // ==============================================================================
        // `getChildCount()` = 5 (butoanele din XML).
        // `getChildAt(index)` întoarce `View`; cast la `RadioButton` pentru `getText()`.
        // `check(id)` — RadioGroup vrea ID-ul, nu indexul. De aceea `getChildAt(index).getId()`.
        // DE CE este generică: adaugi un al 6-lea buton în XML și codul îl vede
        //   fără nicio modificare.
        // RISC: potrivirea se face pe text. Redenumirea „PG-13" -> „PG13" în XML rupe
        //   editarea pentru filmele salvate cu vechea etichetă.
        // ==============================================================================
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
            if(rb.getText().toString().equals(existing.getApproval()))
            {
                // `check` dezactivează automat orice alt buton din grup.
                rgApproval.check(rgApproval.getChildAt(index).getId());
                break;
            }
        }
    }

    // ==================================================================================
    // initControls — CELE 13 findViewById
    // ==================================================================================
    // DE CE TOATE ÎNTR-O METODĂ: dacă un ID este greșit, `findViewById` întoarce
    //   `null` fără eroare, iar NPE-ul apare abia la primul acces — undeva departe.
    //   Grupate aici, poți verifica vizual că fiecare linie are un ID existent.
    //
    // ORDINEA: nu contează pentru compilator. Este ordinea câmpurilor din clasă,
    //   adică ordinea din formular, de sus în jos.
    // ==================================================================================
    private void initControls() {

        // 1. Titlu — TextInputEditText etTitle (cardul „Basics").
        etTitle = findViewById(R.id.etTitle);

        // 2. Data — TextInputEditText etRelease (cardul „Basics").
        etRelease = findViewById(R.id.etRelease);

        // 3. Gen — Spinner spGenre (cardul „Basics").
        spGenre = findViewById(R.id.spGenre);

        // 4. Buget — TextInputEditText etBudget (cardul „Production").
        etBudget = findViewById(R.id.etBudget);

        // 5. Durată — SeekBar sbDuration (cardul „Production").
        sbDuration = findViewById(R.id.sbDuration);

        // 6. Rating — RatingBar rbRating (cardul „Your verdict").
        rbRating = findViewById(R.id.rbRating);

        // 7. Ghidaj — RadioGroup rgApproval (cardul „Your verdict").
        rgApproval = findViewById(R.id.rgApproval);

        // 8. Watchlist — ID `cbOnWatchList` (cu „On"), câmp `cbonWatchList` (fără „O").
        cbonWatchList = findViewById(R.id.cbOnWatchList);

        // 9. Switch — MaterialSwitch swWatched.
        swWatched = findViewById(R.id.swWatched);

        // 10. Poster — TextInputEditText etPoster (cardul „Poster").
        etPoster = findViewById(R.id.etPoster);

        // 11. Buton — ID `btnMovieAction`, câmp `btMovieAction`.
        btMovieAction = findViewById(R.id.btnMovieAction);

        // 12. Eticheta de durată — TextView tvDurationValue.
        tvDurationValue = findViewById(R.id.tvDurationValue);

        // 13. Eticheta de switch — TextView tvWatchedValue.
        tvWatchedValue = findViewById(R.id.tvWatchedValue);
    }

    // ==================================================================================
    // initListeners — PATRU LISTENERI
    // ==================================================================================
    // 1. click pe etRelease   -> deschide dialogul de dată
    // 2. click pe buton       -> saveMovie()
    // 3. switch schimbat      -> actualizează „Yes"/„No"
    // 4. seekbar mișcat       -> actualizează „NNN min."
    // ==================================================================================
    private void initListeners() {

        // LISTENER 1: click pe câmpul de dată.
        // ==============================================================================
        // DE CE `setOnClickListener` PE UN `EditText`: un EditText primește focus la
        //   atingere, nu click. Totuși, `setOnClickListener` funcționează: la prima
        //   atingere primește focus ȘI declanșează click-ul.
        // RISC: dacă utilizatorul apasă a doua oară (câmpul are deja focus), click-ul
        //   se declanșează din nou — dialogul se redeschide. Este comportamentul dorit.
        // RISC MAI MARE: câmpul are `inputType="date"`, deci utilizatorul POATE tasta.
        //   Textul tastat nu este citit în `releaseCal` decât la deschiderea dialogului.
        //   Dacă tastează și apasă direct Save, se salvează data veche din `releaseCal`.
        // ==============================================================================
        etRelease.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showReleaseDatePicker();
            }
        });

        // LISTENER 2: click pe butonul de salvare.
        // Nu există validare înainte de `saveMovie()`. Vezi BUG 1.
        btMovieAction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveMovie();
            }
        });

        // LISTENER 3: switch-ul „Recommended".
        // ==============================================================================
        // `CompoundButton.OnCheckedChangeListener` are o singură metodă, cu doi parametri:
        //   `buttonView` — switch-ul care s-a schimbat (nefolosit aici)
        //   `isChecked`  — noua stare
        // `@NonNull` este adnotarea din semnătura interfeței; o copiem.
        // Operatorul ternar alege textul într-o singură expresie.
        // SE DECLANȘEAZĂ ȘI PROGRAMATIC: `fillForm` -> `swWatched.setChecked(...)`
        //   -> listener -> eticheta se actualizează. De aceea ordinea din onCreate contează.
        // ==============================================================================
        swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                tvWatchedValue.setText(isChecked ? "Yes" : "No");
            }
        });

        // LISTENER 4: slider-ul de durată.
        // ==============================================================================
        // `SeekBar.OnSeekBarChangeListener` are TREI metode. Toate trebuie implementate,
        //   chiar dacă două sunt goale — altfel clasa anonimă nu compilează.
        //
        // `onProgressChanged(seekBar, progress, fromUser)`:
        //   `progress`  — noua valoare (0..300)
        //   `fromUser`  — `true` dacă utilizatorul a tras de slider, `false` dacă
        //                 valoarea a fost setată din cod (`setProgress` în `fillForm`)
        //
        // DE CE `fromUser` ESTE IGNORAT AICI: vrem ca eticheta să reflecte MEREU
        //   valoarea reală, indiferent de cine a schimbat-o. Dacă ai filtra pe
        //   `fromUser`, la editare eticheta ar rămâne „0 min" până la prima atingere.
        // ==============================================================================
        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {

                // Concatenare: `int + String` -> String. Rezultat: „148 min.".
                // Punctul este în text, nu în valoare.
                tvDurationValue.setText(progress + " min.");
            }

            // Metoda 2: de la atingere la mișcare. Nu avem nevoie de ea.
            // Corp gol = intenționat, nu uitat. Interfața o cere.
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            // Metoda 3: la ridicarea degetului. Nu avem nevoie de ea.
            // Aici s-ar putea face un „commit" al valorii sau o haptică.
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });
    }

    // ==================================================================================
    // saveMovie — WIDGET-URI -> MODEL -> INTENT
    // ==================================================================================
    // Cinci pași, în ordine:
    //   1. creează obiectul gol
    //   2. citește 9 câmpuri direct din widget-uri
    //   3. citește al 10-lea câmp (approval) prin buclă
    //   4. pune obiectul în Intent, plus poziția dacă există
    //   5. setResult + finish
    // ==================================================================================
    private void saveMovie() {

        // PASUL 1: obiect gol. Funcționează doar pentru că `Movie` are constructor
        // fără parametri scris explicit (vezi 22.1).
        Movie movie = new Movie();

        // PASUL 2: cele 9 câmpuri simple.
        // Fiecare linie este inversul unei linii din `fillForm`.
        // `getText()` întoarce `Editable`; `toString()` îl face `String`.
        movie.setTitle(etTitle.getText().toString());

        // `releaseCal.getTime()` — NU `etRelease.getText()`.
        // ==============================================================================
        // DE CE: calendarul este sursa de adevăr. Textul poate fi gol, poate fi tastat
        //   greșit, poate fi în alt format. Calendarul a fost actualizat doar de
        //   dialog, cu valori garantat valide.
        // `getTime()` construiește un `Date` NOU la fiecare apel, dar cu aceleași
        //   milisecunde.
        // ==============================================================================
        movie.setRelease(releaseCal.getTime());

        // `getSelectedItem()` întoarce `Object`; `toString()` îl face `String`.
        // RISC: dacă spinner-ul ar fi gol, ar fi `null` -> NPE. Aici `entries` din XML
        //   garantează cel puțin un element.
        movie.setGenre(spGenre.getSelectedItem().toString());

        // BUG 1: `Double.parseDouble("")` aruncă `NumberFormatException`.
        // ==============================================================================
        // CÂND SE ÎNTÂMPLĂ: la insert, câmpul de buget este gol. Utilizatorul apasă
        //   „Save Movie" fără să completeze bugetul -> aplicația se închide.
        // DE CE NU SE VEDE ÎN DEMO: cele 3 filme au buget completat, iar la editare
        //   câmpul este umplut de `fillForm`.
        // REPARAȚIE: `String budgetText = etBudget.getText().toString();
        //              double budget = budgetText.isEmpty() ? 0 : Double.parseDouble(budgetText);`
        // RISC SUPLIMENTAR: pe tastaturi care produc virgulă zecimală („1,5"),
        //   `parseDouble` aruncă aceeași excepție — `Double.parseDouble` acceptă doar
        //   punctul, indiferent de `Locale`.
        // ==============================================================================
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));

        // `getProgress()` întoarce `int`, exact tipul câmpului.
        movie.setDuration(sbDuration.getProgress());

        // `getRating()` întoarce `float`, exact tipul câmpului.
        movie.setRating(rbRating.getRating());

        // `isChecked()` întoarce `boolean`.
        movie.setWatched(swWatched.isChecked());

        // A doua bifă, independentă de prima.
        movie.setOnWatchlist(cbonWatchList.isChecked());

        // Posterul poate fi gol — `""`, nu `null`. Modelul acceptă ambele.
        movie.setPoster(etPoster.getText().toString());

        // PASUL 3: al 10-lea câmp — ghidajul.
        // ==============================================================================
        // RadioGroup nu are „getSelectedItem". Are „getCheckedRadioButtonId()", dar
        //   sursa preferă bucla, ca să poată lua TEXTUL, nu ID-ul.
        // `getChildCount()` = 5. `getChildAt` -> `View` -> cast la `RadioButton`.
        // `isChecked()` — exact un buton este bifat (RadioGroup garantează asta).
        // `break` după primul găsit: restul sunt oricum nebifate.
        // Dacă niciun buton nu ar fi bifat, `approval` ar rămâne `null` — dar XML-ul
        //   are `android:checked="true"` pe primul, deci nu se întâmplă.
        // ==============================================================================
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
            if(rb.isChecked())
            {
                movie.setApproval(rb.getText().toString());
                break;
            }
        }

        // PASUL 4: construiește Intent-ul de REZULTAT.
        // ==============================================================================
        // `new Intent()` FĂRĂ parametri: nu este un Intent de navigare, ci un
        //   container de date. Nu are componentă țintă; este citit de launcher-ul
        //   din MainActivity.
        // ==============================================================================
        Intent intent = new Intent();

        // `putExtra(String, Serializable)` — `Movie` implementează interfața, deci
        //   suprascrierea este găsită. Obiectul este serializat aici.
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);

        // Poziția se trimite DOAR în modul edit.
        // ==============================================================================
        // În insert, cheia lipsește. MainActivity citește cu `getIntExtra(..., -1)`
        //   și primește exact sentinel-ul. Absența cheii ESTE informația „insert".
        // Dacă ai trimite mereu poziția (cu -1), ar funcționa identic — dar protocolul
        //   ar fi mai puțin clar.
        // ==============================================================================
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);

        // PASUL 5a: predă rezultatul.
        // `RESULT_OK` este constanta `Activity.RESULT_OK` (-1). Fără acest apel,
        //   activitatea s-ar închide cu `RESULT_CANCELED` și MainActivity ar ignora-o.
        setResult(RESULT_OK, intent);

        // PASUL 5b: închide activitatea.
        // DE CE DUPĂ `setResult`: `finish()` programează închiderea și predarea
        //   rezultatului. Invers, rezultatul ar putea pleca înainte să fie setat.
        // `finish()` NU distruge imediat activitatea: ea trece prin onPause -> onStop
        //   -> onDestroy, iar MainActivity revine în prim-plan.
        finish();
    }

    // ==================================================================================
    // showReleaseDatePicker — DIALOGUL DE DATĂ
    // ==================================================================================
    // Fluxul:
    //   1. citește textul curent din câmp
    //   2. dacă nu e gol, îl parsează și actualizează `releaseCal`
    //   3. deschide dialogul poziționat pe valorile din `releaseCal`
    //   4. la confirmare, scrie în `releaseCal` și în text
    // ==================================================================================
    private void showReleaseDatePicker() {

        // Textul curent, ca String. Poate fi „" (câmp gol) sau „16/07/2010".
        String current = etRelease.getText().toString();

        // Doar dacă există text încercăm parsarea. Un string gol ar arunca
        // `ParseException` și ar fi prins mai jos — dar verificarea este mai ieftină.
        if (!current.isEmpty()) {
            try {

                // `parse` întoarce `Date` sau aruncă `ParseException`.
                // Poate întoarce și `null` dacă textul este gol — de aici verificarea.
                Date parsed = dateFormat.parse(current);

                // `setTime(Date)` copiază milisecundele în Calendar.
                if (parsed != null)
                    releaseCal.setTime(parsed);
            }

            // `catch` GOL, cu nume `ignored`.
            // ==========================================================================
            // DE CE ESTE ACCEPTABIL: dacă textul nu este o dată validă, comportamentul
            //   dorit este „pornim de la data anterioară". Nu există nimic de raportat
            //   și nimic de reparat — dialogul se deschide oricum.
            // CÂND NU ar fi acceptabil: dacă eroarea ar trebui arătată utilizatorului
            //   sau dacă ar ascunde o problemă de logică.
            // ==========================================================================
            } catch (ParseException ignored) { }
        }

        // Construiește dialogul. Parametri:
        //   1. `this` — Context-ul
        //   2. listener-ul de confirmare (clasă anonimă)
        //   3. anul inițial
        //   4. luna inițială — 0-INDEXATĂ, exact ce așteaptă `Calendar`
        //   5. ziua inițială — 1-indexată
        // `.show()` — fără el, dialogul este construit dar nu apare.
        new DatePickerDialog(
                this,
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {

                        // Scrie în Calendar. ATENȚIE: `set(an, lună, zi)` NU resetează
                        // ora. Ora rămâne cea din `Calendar.getInstance()` — adică
                        // momentul în care a fost creat formularul.
                        // Consecință: două filme salvate în aceeași zi au Date-uri
                        // diferite la nivel de milisecunde. Pentru afișare (dd/MM/yyyy)
                        // nu contează.
                        releaseCal.set(year, month, day);

                        // Șterge un eventual mesaj de eroare de pe câmp.
                        // `setError` nu este apelat nicăieri în acest fișier, deci
                        // linia este defensivă — utilă dacă mai târziu se adaugă validare.
                        etRelease.setError(null);

                        // Scrie textul formatat în câmp. Aici se vede legătura:
                        // Calendar -> String -> EditText. La salvare, drumul este invers:
                        // EditText -> (ignorat) ; Calendar -> Date -> model.
                        etRelease.setText(dateFormat.format(releaseCal.getTime()));
                    }
                },
                // Valorile inițiale ale dialogului, citite din Calendar.
                // `Calendar.MONTH` este deja 0-indexat, deci se passează direct.
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)
        ).show();
    }
}
```

### Cele trei bug-uri reale din `ItemActivity`

| # | Linia din sursă | Declanșator | Efect |
|---|---|---|---|
| **BUG 1** | `Double.parseDouble(etBudget.getText().toString())` | câmpul de buget este gol | `NumberFormatException` -> crash |
| **BUG 2** | `dateFormat.format(existing.getRelease())` | filmul editat are `release == null` | `NullPointerException` -> crash |
| **BUG 3** | `String.valueOf(existing.getBudget())` | buget ≥ 10 000 000 | afișează `1.6E8` în loc de `160000000` |

**Care se vede în demo:** BUG 1 apare imediat dacă apeși „Save Movie" fără să completezi bugetul — este primul lucru pe care îl vei întâlni dacă rulezi aplicația. BUG 2 și BUG 3 nu se văd, pentru că toate cele 3 filme demo au dată și buget completate.

**Alte riscuri (nu sunt bug-uri, dar pot deveni):**

- Tastarea manuală a datei în `etRelease` nu actualizează `releaseCal` — se salvează data veche.
- Genul „Animation" al lui Toy Story nu există în `@array/movie_genre`: la editare, spinner-ul rămâne pe „Drama" și salvarea schimbă genul fără nicio eroare.
- `position` rămâne `-1` dacă `MOVIE_EXTRA` există dar `POSITION_EXTRA` lipsește — salvarea devine insert, adică duplicat.

---

## 22.4 `activity_main.xml` — ecranul listei

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FIȘIER: activity_main.xml — ECRANUL CU LISTA
  ======================================================================================
  CE ESTE: un FrameLayout cu exact doi copii: ListView (umple tot) și FAB (peste el).
  DE CE ATÂT DE PUȚIN: toată complexitatea este în `movie_item.xml` (viitorul rând)
    și în `activity_item.xml` (formularul). Aici doar scheletul.
  STRUCTURA:

    FrameLayout (id=main)
    |== ListView (id=listView)            <- primul copil = desenat primul = dedesubt
    +== FloatingActionButton (id=...)     <- al doilea copil = desenat peste listă

  ORDINEA COPIILOR ESTE SEMNIFICAȚIE, NU STIL: în FrameLayout, fiecare copil este
    desenat peste cel anterior. Inversate, lista ar acoperi butonul.
  ======================================================================================
-->

<!--
  FRAMELAYOUT — containerul rădăcină.
  DE CE FrameLayout și nu LinearLayout: copiii trebuie să se SUPRApună. Un LinearLayout
    i-ar pune unul lângă altul (sau unul sub altul), iar FAB-ul nu ar mai pluti peste listă.
  DE CE nu ConstraintLayout: pentru doi copii, un FrameLayout este mai simplu și mai ieftin.

  ATRIBUTE, PE RÂND:
    xmlns:android   -> atributele framework-ului (layout_width, text, id...)
    xmlns:app       -> atributele bibliotecilor (Material, AndroidX)
    xmlns:tools     -> atribute care există DOAR în preview-ul Android Studio
                       și sunt ELIMINATE la build. Nu ajung niciodată în APK.
    android:id      -> @+id/main; `@+id/` CREEAZĂ ID-ul, `@id/` îl REFERĂ pe unul existent
    layout_width    -> match_parent: ocupă toată lățimea părintelui
    layout_height   -> match_parent: ocupă toată înălțimea
    orientation     -> ATRIBUT INVALID pe FrameLayout; există doar pe LinearLayout.
                       Este IGNORAT de Android și produce un warning de lint
                       („Unknown attribute"). Rămășiță de la un LinearLayout anterior.
    tools:context   -> doar pentru preview; îi spune lui Android Studio ce activitate
                       să folosească pentru temă. Eliminat la build.

  DE CE `android:id="@+id/main"` ESTE OBLIGATORIU: codul face `findViewById(R.id.main)`
    pentru listener-ul de insets. Fără acest ID, apelul ar întoarce `null` și
    `setOnApplyWindowInsetsListener(null, ...)` ar arunca NPE.
-->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!--
      LISTVIEW — lista derulantă.
      DE CE ListView și nu RecyclerView: la acest commit se predă ListView-ul clasic.
        RecyclerView apare în laboratorul următor, împreună cu `movie_item.xml`.

      ATRIBUTE:
        android:id              -> listView; folosit de `findViewById` în initControls
        layout_width/height     -> match_parent pe ambele axe: lista ocupă tot ecranul,
                                   inclusiv zona de sub FAB. FAB-ul este desenat PESTE
                                   listă, nu listă pe lângă el.
        android:entries         -> umple lista din XML cu elementele din `@array/items`
                                   (20 de „Item 1"..„Item 20").
                                   LA RUNTIME, `listView.setAdapter(movieAdapter)`
                                   ÎNLOCUIEȘTE complet acest adapter. `entries` rămâne
                                   doar pentru ca preview-ul să arate o listă plină.
                                   Costul la runtime este zero după `setAdapter`.
    -->
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />

    <!--
      FLOATING ACTION BUTTON — butonul „+".
      Numele complet este necesar pentru că este o clasă din biblioteca Material,
        nu una din framework. Prefixul `com.google.android.material...` este calea clasei.

      ATRIBUTE:
        android:id          -> floatingActionButton; căutat în initControls
        layout_width/height -> wrap_content: FAB-ul are o dimensiune fixă impusă de stil
                               (56dp implicit). `match_parent` l-ar întinde pe tot ecranul.
        android:layout_gravity -> poziția ACESTUI COPIL în PĂRINTELE lui (FrameLayout).
        android:layout_margin  -> 16dp pe toate laturile. Împreună cu padding-ul de insets
                                  aplicat pe `R.id.main`, butonul stă la 16dp de zona
                                  sigură, nu de marginea fizică.
        android:contentDescription -> textul citit de TalkBack. OBLIGATORIU pentru
                                  elementele fără text vizibil; fără el, lint-ul dă
                                  eroare („ContentDescription"), iar utilizatorii cu
                                  cititor de ecran aud doar „buton".
        app:srcCompat       -> varianta compatibilă pentru imagini vectoriale.
                               `android:src` ar funcționa pe API 21+, dar `srcCompat`
                               este recomandarea AndroidX și singura care suportă
                               vectori pe toate versiunile.

      ==================================================================================
      layout_gravity  vs  gravity
      ==================================================================================
        gravity         = cum își aranjează ELEMENTUL copiii lui în interior
        layout_gravity  = cum este aranjat ELEMENTUL în părintele lui

        Exemplu: un TextView cu `gravity="center"` își centrează TEXTUL.
                 Un TextView cu `layout_gravity="center"` este centrat ÎN PĂRINTE.

      `bottom|end` = jos, dreapta. `end` respectă direcția de citire: în RTL devine
        stânga. `right` ar fi fost fix și ar fi greșit în RTL.
      DE CE funcționează aici: FrameLayout respectă `layout_gravity` pe copii.
      ==================================================================================
    -->
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
| `app:srcCompat` | `@drawable/...` | imagine vectorială compatibilă |
| `tools:context` | `.activities.MainActivity` | doar preview |

---

## 22.5 `activity_item.xml` — formularul

### 22.5.0 Trei reguli care se aplică în tot fișierul

**1. `?attr/` vs `@color/` vs `#RRGGBB`**

| Formă | Când se rezolvă | Se schimbă cu tema? | Când se folosește |
|---|---|---|---|
| `?attr/colorPrimary` | la runtime, din tema curentă | **da** | orice culoare semantică |
| `@color/my_color` | la build, din `colors.xml` | nu | culori fixe ale brandului |
| `#FFC107` | la build, literal | nu | excepții asumate (stele) |
| `@android:color/transparent` | constantă de framework | nu | „fără fundal" |

Diferența esențială: `?attr/` este un **rol**, `@color/` este o **valoare**. `?attr/colorPrimary` înseamnă „culoarea primară a temei" și devine altă nuanță în dark mode. `@color/purple_500` rămâne mov în ambele teme.

**2. `0dp` + `layout_weight`**

```
LinearLayout orizontal, lățime totală 360dp
+--------------------------------------------------------------+
| TextView A        | TextView B                               |
| width=0dp         | width=wrap_content                       |
| weight=1          | (fără weight)                            |
+-------------------+------------------------------------------+
|<---- restul ---->|<------ cât cere textul ------------------>|

Regula: `0dp` + `weight` = „nu mă interesează lățimea mea, dă-mi ce rămâne".
Fără `0dp` (cu `wrap_content`), weight-ul distribuie spațiul DUPĂ ce fiecare
copil și-a luat dimensiunea naturală — rezultatul este greu de prevăzut.
```

**3. `style=` vs atribute explicite**

`style="@style/Widget.Material3.TextInputLayout.OutlinedBox"` aplică un **pachet** de atribute (contur, padding, culori, colțuri). Un atribut scris explicit lângă `style` îl **suprascrie** pe cel din stil. De aceea `app:cardCornerRadius="20dp"` funcționează peste stilul cardului.

### 22.5.1 Rădăcina și antetul

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FIȘIER: activity_item.xml — FORMULARUL DE INSERT / EDIT
  ======================================================================================
  STRUCTURA (4 carduri + antet + buton):

    ScrollView (id=main)
    +== LinearLayout vertical
        |== TextView  "Movie details"               <- titlu
        |== TextView  "Fill in the information..."  <- subtitlu
        |== MaterialCardView  [Basics]              <- titlu, gen, dată
        |== MaterialCardView  [Production]          <- buget, durată
        |== MaterialCardView  [Your verdict]        <- rating, switch, bifă, ghidaj
        |== MaterialCardView  [Poster]              <- URL
        +== MaterialButton    "Save Movie"          <- acțiunea

  DE CE CARDURI: împart un formular lung în secțiuni vizuale. Fiecare card are
    aceeași rețetă: fundal de suprafață, colțuri 20dp, padding intern 16dp.
  ======================================================================================
-->

<!--
  SCROLLVIEW — containerul care permite derularea.
  REGULA ABSOLUTĂ: ScrollView are voie cu EXACT UN copil direct. Doi copii ->
    `IllegalStateException: ScrollView can host only one direct child`.
  De aceea tot conținutul stă într-un singur LinearLayout vertical.

  ATRIBUTE:
    android:id          -> `main`, ACELAȘI nume ca în activity_main. Nu este global:
                           listener-ul de insets din ItemActivity caută `R.id.main`,
                           iar ID-ul trebuie să existe în FIECARE layout care îl folosește.
    layout_width/height -> match_parent pe ambele axe
    android:background  -> ?attr/colorSurface, culoarea de „suprafață" a temei Material 3.
                           În light mode este aproape alb; în dark mode este un gri
                           foarte închis. DE CE NU #FFFFFF: ar rupe dark mode-ul —
                           textul deschis ar fi invizibil pe fundal alb.
    android:fillViewport -> true: întinde copilul să umple înălțimea viewport-ului
                           dacă conținutul este mai scurt decât ecranul. Fără el,
                           conținutul s-ar lipi de sus și ar rămâne spațiu gol dedesubt.
    tools:context       -> doar pentru preview
-->
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <!--
      LINEARLAYOUT VERTICAL — singurul copil al ScrollView.
      DE CE vertical: formularul curge de sus în jos.
      PADDING:
        paddingHorizontal="16dp" — 16dp stânga + dreapta (scurtătură pentru
          paddingLeft + paddingRight, disponibilă din API 26)
        paddingTop="24dp" / paddingBottom="24dp" — respiro față de marginile ecranului
      DE CE 16dp: unitatea de bază a Material Design pentru margini laterale.
      DE CE wrap_content pe înălțime: conținutul își ia înălțimea naturală, iar
        ScrollView se ocupă de derulare.
    -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- Header -->

        <!--
          TITLUL ECRANULUI — „Movie details".
          textAppearance="?attr/textAppearanceHeadlineMedium" — stilul tipografic
            complet (dimensiune, greutate, spațiere) din tema Material 3, nu doar
            o dimensiune. `?attr/` pentru că stilul depinde de temă.
          textColor="?attr/colorOnSurface" — culoarea de text potrivită pentru
            suprafața pe care stă. În dark mode devine alb.
          textStyle="bold" — suprascrie greutatea din textAppearance.
          DE CE wrap_content pe ambele axe: textul își ia exact spațiul necesar.
        -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Movie details"
            android:textAppearance="?attr/textAppearanceHeadlineMedium"
            android:textColor="?attr/colorOnSurface"
            android:textStyle="bold" />

        <!--
          SUBTITLUL — „Fill in the information below and save."
          textAppearanceBodyMedium — mai mic decât titlul.
          colorOnSurfaceVariant — o nuanță mai estompată decât colorOnSurface,
            exact rolul pentru text secundar.
          marginTop 4dp + marginBottom 20dp — apropierea de titlu și distanța
            față de primul card.
        -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="20dp"
            android:text="Fill in the information below and save."
            android:textAppearance="?attr/textAppearanceBodyMedium"
            android:textColor="?attr/colorOnSurfaceVariant" />

        <!-- ============ CARD 1: Basics ============ -->

        <!--
          MATERIALCARDVIEW — containerul secțiunii „Basics".
          style="?attr/materialCardViewFilledStyle" — stilul de card „umplut" din
            tema Material 3: fundal colorat, fără contur, umbră minimă.
          app:cardCornerRadius="20dp" — colțuri rotunjite, peste valoarea din stil.
          android:layout_marginBottom="16dp" — distanța până la cardul următor.
          DE CE `?attr/` la stil: în Material 3, stilul de card depinde de temă
            (filled vs elevated vs outlined). Referința prin atribut permite
            schimbarea globală a aspectului.

          DE CE UN SINGUR COPIL: MaterialCardView este proiectat pentru un singur
            copil direct (este un FrameLayout specializat, nu un container de listă).
            Toate elementele secțiunii sunt grupate într-un LinearLayout vertical.
        -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <!--
              LinearLayout vertical INTERN — conținutul cardului.
              padding="16dp" pe toate laturile: conținutul nu atinge marginea cardului.
            -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!--
                  TITLUL SECȚIUNII — „Basics".
                  textAppearanceTitleMedium — mai mic decât titlul ecranului,
                    mai mare decât etichetele.
                  textColor="?attr/colorPrimary" — culoarea de accent a temei.
                    Aici este singurul loc din card unde apare culoarea primară,
                    ca să marcheze ierarhia.
                  marginBottom 12dp — separă titlul de primul câmp.
                -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Basics"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Title -->

                <!--
                  ETICHETA CÂMPULUI — „Title".
                  ATENȚIE: ID-ul este `tvTile`, nu `tvTitle`. Typo în sursă.
                    Nu este folosit în cod, deci nu produce eroare — dar dacă îl cauți
                    după `tvTitle`, nu îl găsești.
                  textAppearanceLabelLarge + colorOnSurfaceVariant — stilul standard
                    pentru eticheta de deasupra unui câmp.
                  marginBottom 4dp — apropierea de câmpul pe care îl descrie.
                -->
                <TextView
                    android:id="@+id/tvTile"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Title"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  TEXTINPUTLAYOUT — învelișul câmpului de text.
                  DE CE există: un `EditText` simplu nu are contur, etichetă plutitoare,
                    iconițe sau mesaj de eroare. `TextInputLayout` le adaugă pe toate.
                  style OutlinedBox — contur vizibil, colțuri mici. Alternativa
                    „FilledBox" are fundal umplut.
                  app:hintEnabled="false" — DEZACTIVEAZĂ eticheta plutitoare.
                    DE CE: eticheta este deja un `TextView` separat deasupra (tvTile).
                    Cu hint-ul activ, ai avea DOUĂ etichete pentru același câmp.
                  app:endIconMode="clear_text" — adaugă un „X" în dreapta care șterge
                    textul. ATENȚIE: șterge doar textul din `EditText`, NU valoarea
                    din model.
                  marginBottom 16dp — distanța până la câmpul următor.
                -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text">

                    <!--
                      CÂMPUL DE TEXT — `etTitle`.
                      Tipul real este `TextInputEditText`, o subclasă de `EditText`
                        care colaborează cu `TextInputLayout` (știe să afișeze hint-ul
                        în interiorul conturului).
                      android:hint="Movie title" — textul afișat când câmpul este gol.
                        Rămâne vizibil pentru că `hintEnabled=false` dezactivează doar
                        eticheta PLUTITOARE, nu hint-ul de conținut.
                      android:inputType="textCapWords" — tastatura capitalizează automat
                        prima literă a fiecărui cuvânt. Potrivit pentru titluri.
                    -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Movie title"
                        android:inputType="textCapWords" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- Genre -->

                <!--
                  ETICHETA „Genre" — `tvGenre`.
                  Același stil ca eticheta de titlu: LabelLarge + colorOnSurfaceVariant.
                  Nu este folosită în cod; există doar pentru cititorul uman.
                -->
                <TextView
                    android:id="@+id/tvGenre"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Genre"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  TRUCUL SPINNER-ULUI: un card outlined în jurul lui.
                  DE CE: `Spinner`-ul nativ nu are contur. Celelalte câmpuri sunt
                    `TextInputLayout.OutlinedBox` (contur 1dp, colțuri 4dp). Ca să
                    arate la fel, spinner-ul este învelit într-un card cu:
                      - stil outlined (contur)
                      - înălțime FIXĂ 56dp (aceeași ca a unui câmp OutlinedBox)
                      - colțuri 4dp
                      - fundal TRANSPARENT, ca să se vadă doar conturul
                      - strokeColor din temă
                  app:cardBackgroundColor="@android:color/transparent" — `@android:color`
                    este o constantă de framework, nu o resursă din proiect.
                  app:strokeColor="?attr/colorOutline" — culoarea de contur a temei.
                  DE CE 56dp: înălțimea standard a unui câmp de text Material.
                    Dacă ai pune wrap_content, spinner-ul ar fi mai scund și ar
                    strica alinierea verticală a formularului.
                -->
                <com.google.android.material.card.MaterialCardView
                    style="?attr/materialCardViewOutlinedStyle"
                    android:layout_width="match_parent"
                    android:layout_height="56dp"
                    android:layout_marginBottom="16dp"
                    app:cardBackgroundColor="@android:color/transparent"
                    app:cardCornerRadius="4dp"
                    app:strokeColor="?attr/colorOutline">

                    <!--
                      SPINNER-UL — `spGenre`.
                      android:entries="@array/movie_genre" — valorile vin din XML.
                        DE CE AICI `entries` RĂMÂNE: ItemActivity nu apelează niciodată
                        `spGenre.setAdapter(...)`. Lista este complet statică.
                      android:paddingStart="4dp" — aliniază textul cu cel din câmpurile
                        TextInputLayout (care au padding intern).
                      android:spinnerMode="dropdown" — lista se deschide ca un popup,
                        nu ca un dialog modal. `dialog` ar fi varianta cu fereastră.
                      layout_height="match_parent" — umple cei 56dp ai cardului.
                    -->
                    <Spinner
                        android:id="@+id/spGenre"
                        android:layout_width="match_parent"
                        android:layout_height="match_parent"
                        android:entries="@array/movie_genre"
                        android:paddingStart="4dp"
                        android:spinnerMode="dropdown" />
                </com.google.android.material.card.MaterialCardView>

                <!-- Release date -->

                <!--
                  CÂMPUL DE DATĂ — `etRelease`.
                  DE CE `hintEnabled="true"` AICI și `false` la titlu: aici NU există
                    un TextView separat deasupra. Eticheta este hint-ul plutitor al
                    TextInputLayout-ului, care se ridică atunci când câmpul are text.
                  app:startIconDrawable="@android:drawable/ic_menu_my_calendar" —
                    iconița de calendar din stânga, care sugerează vizual că este
                    un câmp de dată. `@android:drawable` = resursă din framework.
                  app:startIconContentDescription="Release date" — textul pentru TalkBack
                    al iconiței. Fără el, lint-ul semnalează lipsa descrierii.
                  android:inputType="date" — tastatura numerică cu caractere de dată.
                    ATENȚIE: nu împiedică tastarea unui text invalid; doar schimbă
                    tastatura afișată.
                  NU există `android:layout_marginBottom` aici: cardul se termină
                    imediat după acest câmp, iar padding-ul intern al cardului
                    asigură spațiul.
                -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="true"
                    app:startIconContentDescription="Release date"
                    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

                    <!--
                      CÂMPUL PROPRIU-ZIS — `etRelease`.
                      Textul este „dd/MM/yyyy" și este SCRIS de `showReleaseDatePicker`.
                      Utilizatorul poate tasta, dar textul tastat nu ajunge în
                      `releaseCal` decât la redeschiderea dialogului (vezi RISC în 22.3).
                    -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etRelease"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Release date"
                        android:inputType="date" />
                </com.google.android.material.textfield.TextInputLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ============ CARD 2: Production ============ -->

        <!--
          CARDUL „Production" — buget și durată.
          Aceeași rețetă ca primul card: filled style, colțuri 20dp, marginBottom 16dp.
          Diferența este conținutul, nu stilul. Uniformitatea este intenționată:
            utilizatorul recunoaște tiparul după primul card.
        -->
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

                <!--
                  TITLUL SECȚIUNII — „Production". Aceleași atribute ca „Basics".
                -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Production"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Budget -->

                <!--
                  ETICHETA „Budget" — `tvBudget`. Nu este folosită în cod.
                -->
                <TextView
                    android:id="@+id/tvBudget"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Budget"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  CÂMPUL DE BUGET — `etBudget`.
                  app:prefixText="$ " — text FIX afișat în stânga valorii, în interiorul
                    conturului. NU face parte din textul câmpului: `getText()` întoarce
                    doar cifrele. De aceea `Double.parseDouble` funcționează.
                  app:hintEnabled="false" — eticheta este `tvBudget` de deasupra.
                  android:inputType="numberDecimal" — tastatură numerică cu punct zecimal.
                    Nu garantează că textul este un număr valid: utilizatorul poate
                    lăsa câmpul gol (vezi BUG 1).
                  marginBottom 16dp — distanța până la rândul de durată.
                -->
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

                <!-- Duration -->

                <!--
                  RÂNDUL DE DURATĂ — etichetă în stânga, valoare în dreapta.
                  android:gravity="center_vertical" — centrează copiii PE VERTICALĂ
                    în interiorul rândului. DE CE: eticheta și valoarea au înălțimi
                    diferite; fără centrare ar sta aliniate sus.
                  ATENȚIE: `gravity` aici este pe LinearLayout, deci se aplică
                    COPIILOR lui. Nu se confundă cu `layout_gravity`.
                  android:orientation="horizontal" — copiii stau unul lângă altul.
                -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">

                    <!--
                      ETICHETA „Duration" — `tvDuration`.
                      android:layout_width="0dp" + android:layout_weight="1" —
                        ia tot spațiul rămas după ce valoarea din dreapta își ia
                        lățimea naturală. Efectul: valoarea este împinsă în dreapta.
                      Fără `0dp`, cele două texte ar sta lipite în stânga.
                    -->
                    <TextView
                        android:id="@+id/tvDuration"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Duration"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!--
                      VALOAREA DURATEI — `tvDurationValue`, actualizată de listener-ul
                        SeekBar-ului.
                      android:text="0 min" — valoarea inițială, potrivită cu progresul 0.
                      textColor="?attr/colorPrimary" — culoarea de accent, ca să iasă
                        în evidență față de etichetă.
                      tools:text="148 min" — DOAR în preview: arată cum va arăta textul
                        când are o valoare reală. Nu ajunge în APK.
                    -->
                    <TextView
                        android:id="@+id/tvDurationValue"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorPrimary"
                        tools:text="148 min" />
                </LinearLayout>

                <!--
                  SEEKBAR-UL — `sbDuration`.
                  android:max="300" — valoarea maximă. Implicit ar fi 100.
                  android:min="0" — disponibil din API 26. `minSdk 33`, deci merge.
                    Fără el, minimul ar fi tot 0, dar explicit este mai clar.
                  android:progressTint="?attr/colorPrimary" — culoarea părții parcurse.
                  android:thumbTint="?attr/colorPrimary" — culoarea mânerului.
                  tools:progress="148" — doar preview.
                  marginTop 8dp — separă bara de rândul de etichetă.
                  ATENȚIE: `getProgress()` întoarce `int`, exact tipul din model.
                -->
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

                <!--
                  RÂNDUL DE MIN/MAX — „0 min" în stânga, „300 min" în dreapta.
                  paddingHorizontal="16dp" — aliniază etichetele cu începutul și
                    sfârșitul barei, nu cu marginile cardului.
                  Cele două valori sunt HARDCODATE. RISC: dacă schimbi `android:max`
                    al SeekBar-ului, trebuie să schimbi și textul „300 min".
                  `0dp` + `weight=1` pe primul text împinge al doilea în dreapta.
                -->
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

        <!-- ============ CARD 3: Your verdict ============ -->

        <!--
          CARDUL „Your verdict" — rating, switch, bifă, ghidaj.
          Este cel mai dens card: trei controale diferite și două separatoare.
        -->
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

                <!-- Rating -->

                <!--
                  ETICHETA „Rating" — `tvRating`. Nu este folosită în cod.
                  ATENȚIE: nu are `marginBottom`, spre deosebire de celelalte etichete.
                    Stelele au ele `marginTop="4dp"`, deci spațiul este asigurat
                    din partea cealaltă.
                -->
                <TextView
                    android:id="@+id/tvRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Rating"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  RATINGBAR — `rbRating`.
                  android:numStars="5" — 5 stele.
                  android:stepSize="0.5" — jumătăți de stea. `getRating()` întoarce
                    `float` (ex. 3.5), exact tipul din model.
                  android:layout_gravity="center_horizontal" — centrează BARA în
                    părintele vertical. `gravity` ar fi centrat copiii barei, nu bara.
                  Culori:
                    progressTint="#FFC107" — galben de stele, HARDCODAT. Excepție
                      asumată: semnificația „stea galbenă" nu depinde de temă.
                    secondaryProgressTint="#FFC107" — aceeași culoare pentru partea
                      secundară (jumătatea de stea).
                    progressBackgroundTint="?attr/colorOutlineVariant" — stelele goale,
                      din temă.
                  tools:rating="3.5" — doar preview.
                  DE CE nu are listener: rating-ul este citit direct la salvare cu
                    `getRating()`. Nu există etichetă care să se actualizeze.
                -->
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

                <!--
                  SEPARATOR — o linie de 1dp.
                  DE CE un `View` gol: nu există un widget „divider" în XML.
                    Un View cu înălțime 1dp și fundal colorat este soluția standard.
                  marginVertical="12dp" — spațiu egal sus și jos.
                  background="?attr/colorOutlineVariant" — culoarea de contur,
                    suficient de discretă pentru o linie.
                -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Recommended -->

                <!--
                  RÂNDUL CU SWITCH ȘI BIFĂ.
                  gravity="center_vertical" — aliniază cele trei coloane pe verticală.
                  minHeight="48dp" — ținta minimă de atingere recomandată de Material.
                    Fără ea, rândul ar fi mai scund decât degetul.
                -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:minHeight="48dp"
                    android:orientation="horizontal">

                    <!--
                      COLOANA DE TEXT — 0dp + weight 1, deci ia tot spațiul rămas
                      după switch și bifă.
                      vertical — cele două texte stau unul sub altul.
                    -->
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">

                        <!--
                          ETICHETA „Recommended" — `tvWatched`. Nu este folosită în cod.
                          textAppearanceBodyLarge — mai mare decât o etichetă obișnuită,
                            pentru că este textul principal al rândului.
                        -->
                        <TextView
                            android:id="@+id/tvWatched"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Recommended"
                            android:textAppearance="?attr/textAppearanceBodyLarge"
                            android:textColor="?attr/colorOnSurface" />

                        <!--
                          VALOAREA „No" — `tvWatchedValue`, actualizată de listener-ul
                            switch-ului: `isChecked ? "Yes" : "No"`.
                          Valoarea inițială „No" corespunde switch-ului oprit.
                          textColor colorPrimary — evidențiază valoarea.
                        -->
                        <TextView
                            android:id="@+id/tvWatchedValue"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="No"
                            android:textAppearance="?attr/textAppearanceLabelLarge"
                            android:textColor="?attr/colorPrimary" />
                    </LinearLayout>

                    <!--
                      MATERIALSWITCH — `swWatched`.
                      DE CE `MaterialSwitch` și nu `Switch`: varianta Material are
                        animații și culori din temă, plus thumb-ul cu iconiță.
                      marginEnd="12dp" — separă switch-ul de bifă. `end` respectă RTL.
                      NU are text: eticheta este în coloana din stânga.
                      Listener-ul este atașat în cod, nu în XML.
                    -->
                    <com.google.android.material.materialswitch.MaterialSwitch
                        android:id="@+id/swWatched"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="12dp" />

                    <!--
                      MATERIALCHECKBOX — `cbOnWatchList`.
                      ID-ul are „On" cu majusculă; câmpul din cod este `cbonWatchList`.
                      android:text="Watchlist" — eticheta este ÎN INTERIORUL
                        controlului, deci se atinge împreună cu bifa.
                      Este independent de switch: poți bifa amândouă.
                    -->
                    <com.google.android.material.checkbox.MaterialCheckBox
                        android:id="@+id/cbOnWatchList"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Watchlist" />
                </LinearLayout>

                <!--
                  Al doilea separator, identic cu primul.
                -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Guidance -->

                <!--
                  ETICHETA „Guidance" — `tvGuidance`. Nu este folosită în cod.
                -->
                <TextView
                    android:id="@+id/tvGuidance"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Guidance"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!--
                  HORIZONTALSCROLLVIEW — permite derularea orizontală a grupului.
                  DE CE: 5 butoane radio („G", „PG", „PG-13", „R", „NC-17") nu încap
                    pe un ecran de 360dp. Fără derulare, ultimele ar fi tăiate.
                  android:scrollbars="none" — ascunde bara de derulare; pe un rând
                    de butoane ar arăta ca un defect.
                  ATENȚIE: și HorizontalScrollView acceptă un singur copil direct.
                -->
                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none">

                    <!--
                      RADIOGROUP — `rgApproval`.
                      android:orientation="horizontal" — butoanele stau pe un rând.
                        Implicit ar fi vertical.
                      DE CE RadioGroup și nu 5 butoane separate: grupul garantează
                        că EXACT UNUL este bifat. `check(id)` dezactivează automat
                        pe ceilalți.
                      Cele 5 butoane sunt copii direcți; codul le parcurge cu
                        `getChildCount()` / `getChildAt()`.
                    -->
                    <RadioGroup
                        android:id="@+id/rgApproval"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <!--
                          BUTONUL 1 — „G".
                          android:checked="true" — ESTE BIFAT IMPLICIT.
                          DE CE: grupul trebuie să aibă MEREU o valoare. Fără el,
                            `saveMovie` ar putea lăsa `approval` null dacă utilizatorul
                            nu atinge niciun buton.
                          `MaterialRadioButton` — varianta Material, cu animație
                            și culori din temă.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbGeneral"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:checked="true"
                            android:text="G" />

                        <!--
                          BUTONUL 2 — „PG". `rbParentGuidance`.
                          Textul este valoarea care ajunge în model.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbParentGuidance"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG" />

                        <!--
                          BUTONUL 3 — „PG-13". `rbPG13`.
                          ATENȚIE: cratima face parte din text și din valoarea salvată.
                            Redenumirea în „PG13" ar rupe potrivirea din `fillForm`.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbPG13"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG-13" />

                        <!--
                          BUTONUL 4 — „R". `rbRestricted`.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbRestricted"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="R" />

                        <!--
                          BUTONUL 5 — „NC-17". `rbNC17`.
                          Ultimul buton; dacă ai adăuga un al 6-lea, codul l-ar citi
                            fără nicio modificare — bucla este generică.
                        -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbNC17"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="NC-17" />
                    </RadioGroup>
                </HorizontalScrollView>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- ============ CARD 4: Poster ============ -->

        <!--
          CARDUL „Poster" — un singur câmp.
          marginBottom="24dp" — mai mare decât la celelalte carduri, pentru că
            urmează butonul de salvare și trebuie să existe respiro.
        -->
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

                <!--
                  CÂMPUL DE URL — `etPoster`.
                  app:endIconMode="clear_text" — „X"-ul de ștergere.
                  app:startIconDrawable="@android:drawable/ic_menu_gallery" — iconița
                    de galerie, sugestie vizuală pentru „imagine".
                  app:startIconContentDescription="Poster link" — descriere pentru TalkBack.
                  app:hintEnabled="false" — nu există etichetă separată deasupra,
                    dar hint-ul de conținut rămâne vizibil.
                  android:inputType="textUri" — tastatură optimizată pentru URL-uri
                    (are „/", „.", „:"). Nu validează URL-ul.
                -->
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

        <!-- Save -->

        <!--
          BUTONUL DE SALVARE — `btnMovieAction`.
          style="@style/Widget.Material3.Button" — varianta FILLED (fundal plin,
            text alb). Este stilul implicit, dar scris explicit ca să fie clar.
          android:layout_height="60dp" — mai înalt decât standardul (48dp), pentru
            că este acțiunea principală a ecranului.
          app:cornerRadius="30dp" — EXACT jumătate din înălțime, deci butonul devine
            o pastilă (pill). Regula: cornerRadius = height / 2.
          app:icon="@android:drawable/ic_menu_save" — iconița de salvare din framework.
          app:iconGravity="textStart" — iconița stă înaintea textului.
          android:text="Save Movie" — în modul edit, codul îl schimbă în „Update Movie".
          android:textAppearance="?attr/textAppearanceLabelLarge" — stilul de etichetă
            pentru butoane Material.
          DE CE NU are `layout_marginTop`: cardul de deasupra are marginBottom 24dp.
        -->
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

### 22.5.2 Harta widget-urilor din formular

| # | ID în XML | Tip | Câmp în `ItemActivity` | Metodă de citire |
|---|---|---|---|---|
| 1 | `etTitle` | `TextInputEditText` | `etTitle` | `getText().toString()` |
| 2 | `etRelease` | `TextInputEditText` | `etRelease` | (nu se citește — `releaseCal`) |
| 3 | `spGenre` | `Spinner` | `spGenre` | `getSelectedItem().toString()` |
| 4 | `etBudget` | `TextInputEditText` | `etBudget` | `Double.parseDouble(...)` |
| 5 | `sbDuration` | `SeekBar` | `sbDuration` | `getProgress()` |
| 6 | `rbRating` | `RatingBar` | `rbRating` | `getRating()` |
| 7 | `rgApproval` | `RadioGroup` | `rgApproval` | buclă + `isChecked()` |
| 8 | `cbOnWatchList` | `MaterialCheckBox` | `cbonWatchList` | `isChecked()` |
| 9 | `swWatched` | `MaterialSwitch` | `swWatched` | `isChecked()` |
| 10 | `etPoster` | `TextInputEditText` | `etPoster` | `getText().toString()` |
| 11 | `btnMovieAction` | `MaterialButton` | `btMovieAction` | `setOnClickListener` |
| 12 | `tvDurationValue` | `TextView` | `tvDurationValue` | `setText(...)` |
| 13 | `tvWatchedValue` | `TextView` | `tvWatchedValue` | `setText(...)` |

**Trei observații care se văd doar comparând coloanele:**

1. `etRelease` este SINGURUL câmp citit din altă sursă decât widget-ul.
2. Două ID-uri nu se potrivesc cu numele câmpului: `cbOnWatchList` / `cbonWatchList` și `btnMovieAction` / `btMovieAction`.
3. Șapte `TextView`-uri de etichetă (`tvTile`, `tvGenre`, `tvBudget`, `tvDuration`, `tvRating`, `tvWatched`, `tvGuidance`) apar în XML, dar nu în cod — nu au nevoie de referință.

---

## 22.6 `movie_item.xml` — cardul de listă

**Nu este folosit la acest commit.** `MainActivity` nu îl referențiază nicăieri: nu există un `MovieAdapter` și niciun `inflate(R.layout.movie_item, ...)`. Este pregătirea pentru laboratorul următor, unde `ListView` + `ArrayAdapter` sunt înlocuite cu `RecyclerView` + `MovieAdapter` + acest layout.

De ce merită citit acum: este singurul fișier care arată cum ar trebui să arate un rând **bun**, în contrast cu `simple_list_item_1` (un singur `TextView` cu `toString()`-ul întreg).

```xml
<?xml version="1.0" encoding="utf-8"?>

<!--
  ======================================================================================
  FIȘIER: movie_item.xml — RÂNDUL DE LISTĂ (pentru RecyclerView, laboratorul următor)
  ======================================================================================
  STRUCTURA:

    MaterialCardView (rădăcină)
    +== LinearLayout orizontal
        |== ImageView  96x140dp          <- poster
        +== LinearLayout vertical, 0dp+weight=1
            |== TextView  movieTitle     <- 20sp, bold, max 2 rânduri
            |== TextView  movieSubtitle  <- „gen · an"
            |== LinearLayout orizontal
            |   |== RatingBar (small, indicator)
            |   +== TextView movieRatingValue
            |== TextView  movieFacts     <- „142 min · $160M"
            +== ChipGroup
                |== Chip chipApproval
                |== Chip chipWatched
                +== Chip chipWatchlist

  DE CE CARDUL ESTE RĂDĂCINA: fiecare rând este o unitate vizuală independentă,
    cu umbră și colțuri proprii. Un `LinearLayout` simplu ar arăta ca un tabel.
  ======================================================================================
-->

<!--
  MATERIALCARDVIEW — rădăcina rândului.
  ATRIBUTE:
    layout_width="match_parent"  — rândul ocupă toată lățimea listei
    layout_height="wrap_content" — înălțimea dată de conținut (posterul de 140dp)
    layout_marginHorizontal="12dp" — 12dp stânga/dreapta; cardul nu atinge marginile
    layout_marginVertical="6dp"   — 6dp sus/jos; separă rândurile între ele
    app:cardCornerRadius="16dp"   — colțuri rotunjite
    app:cardElevation="3dp"       — umbră. AICI umbra este PREZENTĂ, spre deosebire
                                    de cardurile din formular (care sunt „filled",
                                    fără umbră). Un rând de listă trebuie să se
                                    distingue de fundal.
    app:cardUseCompatPadding="true" — adaugă padding intern pentru ca umbra să nu
                                    fie tăiată de limitele cardului pe API-urile vechi.
                                    Pe API 21+ are ca efect păstrarea umbrei vizibile.
-->
<com.google.android.material.card.MaterialCardView
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginHorizontal="12dp"
    android:layout_marginVertical="6dp"
    app:cardCornerRadius="16dp"
    app:cardElevation="3dp"
    app:cardUseCompatPadding="true">

    <!--
      LINEARLAYOUT ORIZONTAL — poster în stânga, informații în dreapta.
      padding="12dp" — conținutul nu atinge marginea cardului.
      DE CE orizontal: posterul și coloana de text stau alăturate.
    -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="12dp">

        <!-- Poster -->

        <!--
          IMAGEVIEW — posterul.
          layout_width="96dp" / layout_height="140dp" — raport ~2:3, ca un poster
            de film. Dimensiuni FIXE: imaginea nu își schimbă mărimea în funcție
            de textul din dreapta.
          android:background="#11000000" — negru cu alfa 0x11 (~7% opacitate).
            Este un PLACEHOLDER vizibil cât timp nu există imagine.
          android:scaleType="centerCrop" — umple cele 96x140dp decupând marginile,
            fără să deformeze. `fitXY` ar întinde imaginea; `centerInside` ar lăsa
            benzi goale.
          android:contentDescription="Movie poster" — obligatoriu pentru TalkBack.
          android:src="@android:drawable/ic_menu_gallery" — imagine provizorie.
            La runtime, adapterul ar înlocui-o cu posterul real.
        -->
        <ImageView
            android:id="@+id/moviePoster"
            android:layout_width="96dp"
            android:layout_height="140dp"
            android:background="#11000000"
            android:scaleType="centerCrop"
            android:contentDescription="Movie poster"
            android:src="@android:drawable/ic_menu_gallery" />

        <!-- Info column -->

        <!--
          COLOANA DE INFORMAȚII — 0dp + weight 1.
          DE CE: posterul are 96dp fix; restul lățimii (360 - 96 - margini) trebuie
            să o ia coloana de text. Cu `wrap_content`, textul lung ar împinge
            cardul dincolo de ecran.
          marginStart="12dp" — separă textul de poster. `start` respectă RTL.
          orientation="vertical" — elementele curg de sus în jos.
        -->
        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:layout_marginStart="12dp"
            android:orientation="vertical">

            <!--
              TITLUL — `movieTitle`.
              textSize="20sp" + textStyle="bold" — ierarhie puternică; titlul este
                elementul principal al rândului.
              maxLines="2" — maximum două rânduri. Fără el, un titlu lung ar împinge
                restul conținutului în jos și ar strica alinierea rândurilor.
              ellipsize="end" — textul tăiat se termină cu „…".
              DE CE ambele: `maxLines` limitează, `ellipsize` semnalează că există
                mai mult text. Doar `maxLines` ar tăia brusc, fără indiciu.
            -->
            <TextView
                android:id="@+id/movieTitle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Movie title"
                android:textSize="20sp"
                android:textStyle="bold"
                android:maxLines="2"
                android:ellipsize="end" />

            <!-- genre · release year, e.g. "Sci-Fi · 2021" -->

            <!--
              SUBTITLUL — „gen · an".
              textSize="14sp" — mai mic decât titlul.
              textColor="#757575" — gri hardcodat.
              RISC: în dark mode, #757575 pe un fundal închis are contrast mic.
                Ar trebui `?attr/colorOnSurfaceVariant`.
              marginTop="2dp" — lipit de titlu, ca o continuare a lui.
            -->
            <TextView
                android:id="@+id/movieSubtitle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Genre · Year"
                android:textSize="14sp"
                android:textColor="#757575" />

            <!-- Rating -->

            <!--
              RÂNDUL DE RATING — stele + valoare numerică.
              gravity="center_vertical" — aliniază stelele cu textul.
              marginTop="6dp" — separă de subtitlu.
            -->
            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <!--
                  RATINGBAR MIC — `movieRating`.
                  style="?android:attr/ratingBarStyleSmall" — stilul mic din framework
                    (stele de ~12dp). `?android:attr/` = atribut din tema framework-ului,
                    nu din tema aplicației.
                  android:isIndicator="true" — stelele sunt DOAR AFIȘARE. Nu pot fi
                    atinse și nu au listener. Fără el, utilizatorul ar putea modifica
                    rating-ul dintr-un rând de listă.
                  numStars=5, stepSize=0.5 — aceleași valori ca în formular, ca să
                    arate identic.
                -->
                <RatingBar
                    android:id="@+id/movieRating"
                    style="?android:attr/ratingBarStyleSmall"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:numStars="5"
                    android:stepSize="0.5"
                    android:isIndicator="true" />

                <!--
                  VALOAREA NUMERICĂ — „4.5".
                  marginStart="6dp" — separă de stele.
                  textSize="13sp", gri — text secundar.
                  DE CE există: stelele mici sunt greu de citit exact; cifra dă
                    valoarea precisă.
                -->
                <TextView
                    android:id="@+id/movieRatingValue"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:text="4.5"
                    android:textSize="13sp"
                    android:textColor="#757575" />
            </LinearLayout>

            <!-- Facts: duration + budget -->

            <!--
              FAPTE — „142 min · $160M".
              Un singur TextView cu două valori separate prin „·".
              textSize="13sp", gri mai deschis (#9E9E9E) — informație terță.
              DE CE un singur TextView și nu două: sunt informații de același rang,
                pe un rând, fără nevoie de aliniere separată.
            -->
            <TextView
                android:id="@+id/movieFacts"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="142 min  ·  $160M"
                android:textSize="13sp"
                android:textColor="#9E9E9E" />

            <!-- Status chips: approval, watched, watchlist -->

            <!--
              CHIPGROUP — containerul celor trei etichete de stare.
              app:chipSpacingHorizontal="6dp" — 6dp între chip-uri.
              app:singleLine="false" — permite trecerea pe al doilea rând dacă
                nu încap toate. `true` le-ar tăia.
              marginTop="8dp" — separă de rândul de fapte.
              DE CE ChipGroup și nu trei TextView-uri: chip-urile au fundal, colțuri
                și padding standardizate; arată ca niște etichete, nu ca text.
            -->
            <com.google.android.material.chip.ChipGroup
                android:id="@+id/movieStatusGroup"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                app:chipSpacingHorizontal="6dp"
                app:singleLine="false">

                <!--
                  CHIP 1 — ghidajul parental („Approved").
                  style="@style/Widget.Material3.Chip.Suggestion" — stilul de chip
                    sugestie: fundal discret, contur.
                  android:clickable="false" — NU este buton. Fără el, chip-ul ar
                    primi ripple la atingere și ar sugera o acțiune inexistentă.
                  app:chipMinHeight="28dp" — înălțime mică, de etichetă.
                  app:ensureMinTouchTargetSize="false" — DE CE: Material forțează
                    implicit o țintă de atingere de 48dp, care ar umfla rândul.
                    Pentru un element neclickabil, forțarea este inutilă.
                -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipApproval"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Approved"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />

                <!--
                  CHIP 2 — „Watched".
                  app:chipIcon="@android:drawable/checkbox_on_background" — o bifă
                    în interiorul chip-ului, ca să se distingă de celelalte două
                    fără să citești textul.
                -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipWatched"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Watched"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:chipIcon="@android:drawable/checkbox_on_background"
                    app:ensureMinTouchTargetSize="false" />

                <!--
                  CHIP 3 — „Watchlist".
                  Același stil, fără iconiță. Toate trei sunt etichete de stare,
                    nu filtre.
                -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipWatchlist"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Watchlist"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />
            </com.google.android.material.chip.ChipGroup>
        </LinearLayout>
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

**Ce se vede doar comparând cu `activity_item.xml`:**

| Aspect | `activity_item.xml` (formular) | `movie_item.xml` (rând) |
|---|---|---|
| Card | `filled`, fără umbră, colțuri 20dp | `elevation 3dp`, colțuri 16dp |
| Culori | toate din temă (`?attr/`) | trei gri-uri hardcodate |
| Text | stiluri `textAppearance` | `textSize` explicit |
| Rating | editabil | `isIndicator="true"` |
| Controale | interactive | toate `clickable="false"` |

Rândul este intenționat mai „fizic" (umbră, dimensiuni fixe) și mai puțin legat de temă. Este o decizie de design, nu o greșeală — dar hardcodarea culorilor rămâne un risc pentru dark mode.

---

## 22.7 Cum se leagă totul — fluxul complet

### 22.7.1 Pornirea aplicației

```
PORNIRE
  MainActivity.onCreate(savedInstanceState = null)
    |
    |== super.onCreate                 -> AppCompat își instalează delegate-ul
    |== EdgeToEdge.enable(this)         -> ferestrele desenează sub bare
    |== setContentView(activity_main)   -> arborele de view-uri există
    |== insets pe R.id.main             -> padding = status bar + nav bar
    |== addSampleMovies()               -> movies = [Inception, Toy Story, The Matrix]
    |== new ArrayAdapter(this,
    |       simple_list_item_1, movies) -> movieAdapter ține REFERINȚA la `movies`
    |== initControls()                  -> fabInsert, listView, setAdapter
    |== initListeners()                 -> FAB + item click (launcher este încă null)
    +== registerForActivityResult(...)  -> launcher creat
          |
          v
  ListView afișează 3 rânduri:
    „Movie{title='Inception', release=..., genre='Sci-Fi', ...}"
    „Movie{title='Toy Story', ...}"
    „Movie{title='The Matrix', ...}"
```

### 22.7.2 Insert — FAB

```
APASĂ FAB
  fabInsert.onClick
    |
    |== new Intent(MainActivity.this, ItemActivity.class)   (fără extra-uri)
    +== launcher.launch(intent)
          |
          v
  MainActivity: onPause
  ItemActivity: onCreate
    |
    |== setContentView(activity_item)
    |== insets pe R.id.main
    |== initControls()          -> 13 findViewById
    |== initListeners()         -> 4 listeneri
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
    |== movie = getSerializableExtra(MOVIE_EXTRA)     <- O COPIE
    |== position = getIntExtra(POSITION_EXTRA, -1)    -> -1
    |== movies.add(movie)
    +== movieAdapter.notifyDataSetChanged()
          |
          v
  ListView redesenează -> al 4-lea rând apare
```

### 22.7.3 Edit — click pe rând

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
    |== existing = IntentCompat.getSerializableExtra(...)   <- COPIE
    |== existing != null
    |     |== position = 0
    |     |== fillForm(existing)     -> 10 câmpuri umplute
    |     |== setTitle("Edit movie")
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

### 22.7.4 Obiectul care călătorește

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
                        fillForm(existing) citeste
                        saveMovie() creeaza Movie@D
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

**Consecința practică:** modificarea formularului nu se vede în listă până la `movies.set(...)`. Nu există „legătură" între obiectul din listă și cel din formular — sunt două obiecte distincte.

### 22.7.5 Reciclarea rândurilor în ListView

```
ListView are 7 rânduri vizibile, lista are 100 de elemente.

  ecran: [0][1][2][3][4][5][6]

  derulezi în jos:
    rândul 0 iese în sus  ->  convertView = rândul 0
    rândul 7 intră în jos <-  ArrayAdapter.getView(7, convertView, parent)

  ArrayAdapter:
    dacă convertView != null:
        refolosește vederea (nu mai inflatează XML-ul)
    TextView.setText(movies.get(7).toString())

  DE CE contează: fără reciclare, 100 de rânduri ar însemna 100 de inflate-uri.
    Cu reciclare, există ~8 vedieri pentru oricât de multe elemente.

  DE CE `notifyDataSetChanged()` este necesar:
    ListView NU observă lista. El știe doar ce i-a spus adapterul la ultimul bind.
    `notifyDataSetChanged()` -> adapter.notifyChanged() -> ListView re-bindează
    rândurile vizibile.
```

---

## 22.8 Ce să reții din fiecare fișier

| Fișier | Esența | Capcana |
|---|---|---|
| `Movie.java` | POJO serializabil, 10 câmpuri, constructor gol explicit, `isX()` pentru booleeni, `toString()` = contract de afișare | constructorul cu 10 parametri este POZIȚIONAL |
| `MainActivity.java` | ordinea din `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` | `launcher` este atribuit DUPĂ `initListeners` |
| `ItemActivity.java` | 13 `findViewById`, `releaseCal` ca sursă de adevăr, buclă generică pe `RadioGroup`, `setResult` + `finish` | buget gol -> crash; dată null -> crash |
| `activity_main.xml` | `FrameLayout` + ordinea copiilor + `layout_gravity` pe FAB | `android:orientation` este invalid pe FrameLayout |
| `activity_item.xml` | `ScrollView` cu un copil, `MaterialCardView` ca secțiune, `TextInputLayout`, `Spinner` învelit | `hintEnabled` trebuie corelat cu existența etichetei |
| `movie_item.xml` | card de listă, `weight` pentru coloana de text, chips pentru stare | nu este folosit încă; culori hardcodate |

### Cele 10 lucruri pe care le vei fi întrebat

1. **De ce `implements Serializable`?** Ca să poată fi pus într-un `Intent` cu `putExtra`.
2. **Obiectul primit este originalul?** Nu. Este o copie deserializată.
3. **De ce constructor gol explicit?** Un constructor cu parametri suprimă constructorul implicit, iar `saveMovie` face `new Movie()`.
4. **De ce `isWatched()`?** Convenția JavaBeans pentru `boolean`.
5. **De ce `notifyDataSetChanged()`?** ListView nu observă lista; adapterul trebuie să anunțe.
6. **De ce `MainActivity.this`?** În clasa anonimă, `this` este listener-ul, nu `Context`-ul.
7. **De ce `releaseCal` și nu `etRelease`?** Calendarul este sursa de adevăr; textul poate fi invalid.
8. **De ce `fromUser` este ignorat?** Eticheta trebuie să reflecte valoarea și când vine din cod.
9. **De ce `0dp` + `weight`?** „Ia tot spațiul rămas", nu „ia mărimea naturală".
10. **De ce `?attr/` și nu `@color/`?** `?attr/` este un rol de temă și se adaptează la dark mode.

---

## Rezumat capitol 22

- Modelul nu atinge UI-ul; activitățile nu conțin logică de rând.
- `onCreate`: `super` -> `EdgeToEdge` -> `setContentView` -> insets -> date -> adapter -> controls -> listeners -> launcher.
- `releaseCal` este sursa de adevăr pentru dată, nu textul din `EditText`.
- Bucla pe `RadioGroup` face codul generic — adaugi butoane în XML, codul le vede.
- `setResult(RESULT_OK, intent)` + `finish()` este perechea obligatorie.
- `notifyDataSetChanged()` după orice modificare a listei.
- `movie_item.xml` există, dar nu este legat — pregătire pentru laboratorul următor.
- Trei bug-uri reale: buget gol, `release` null, notație științifică.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [prezentarea generală](index.html).
