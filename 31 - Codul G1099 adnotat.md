# Capitolul 31 — Codul G1099 adnotat

**Obiectiv:** să citești fiecare linie a aplicației G1099 cu explicația lipită de ea — ce face, de ce e acolo, ce se rupe dacă o scoți.

**Timp estimat:** 90–120 min (citire activă, cu proiectul deschis în paralel).

**Sursa:** `cod-final`, commitul `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`.

**Regulă:** codul este **nemodificat, byte cu byte**. Tot ce apare cu `//` sau `<!-- -->` în plus față de sursă este adnotare.

---

## 31.0 Ce diferă față de G1097

Aplicația G1099 este **aceeași aplicație** ca G1097: aceleași două activități, același model, aceleași două layout-uri, același flux. Am comparat fișierele linie cu linie, iar diferențele sunt puține. Nu sunt însă întâmplătoare: fiecare arată o decizie de cod pe care o poți primi ca întrebare.

| Aspect | G1099 | G1097 (referință) |
|---|---|---|
| Câmpul pentru poster în `Movie.java` | `private String posterUrl;` | `private String poster = null;` |
| Inițializator de câmp | niciunul | `= null` |
| Poziția constructorului fără parametri | **primul**, înaintea celui cu parametri (linia 18) | ultimul, după setteri (linia 127) |
| `toString()` include posterul? | **NU** | da (`poster`) |
| `MainActivity.java` — importuri nefolosite | `android.widget.Toast` și `java.util.Date` | aceleași două |
| `ItemActivity.java` — importuri nefolosite | `android.media.Rating`, `android.widget.Switch`, `com.google.android.material.snackbar.Snackbar` | `Switch`, `Toast`, `Snackbar`, `ActivityItemBinding` |
| `ItemActivity.java` — import `android.media.Rating` | **prezent, nefolosit** | absent |
| `ItemActivity.java` — importă `Toast`/`ActivityItemBinding`? | **nu** | da (nefolosite) |
| `activity_main.xml` | identic cu G1097 | — |
| `activity_item.xml` | identic cu G1097 | — |
| `AndroidManifest.xml` | identic cu G1097 (diferă doar tema: `Theme.G1099`) | `Theme.G1097` |
| `movie_item.xml` | **nu există** | există (pregătit pentru S07, nefolosit de niciun cod) |

### 31.0.1 `posterUrl` în loc de `poster`

Câmpul se numește altfel, deci **și getter-ul și setter-ul se numesc altfel**: `getPosterUrl()` / `setPosterUrl()`. Nu este o diferență cosmetică — este singura diferență care se vede din afara clasei.

`ItemActivity` apelează exact aceste nume, în două locuri:

- `etPoster.setText(existing.getPosterUrl());` — în `fillForm`
- `movie.setPosterUrl(etPoster.getText().toString());` — în `saveMovie`

**Ce înveți:** numele unui câmp `private` nu este vizibil din exterior, dar numele getter-ului **este** contractul. Poți redenumi câmpul fără să strici nimic, atâta timp cât getter-ul rămâne la fel. Dacă redenumești getter-ul fără să actualizezi apelurile, codul **nu mai compilează** — și aceasta este varianta bună: compilatorul te prinde.

**De ce `Url`:** sufixul spune ce fel de text este. Un poster ar putea fi și o cale locală, un `byte[]` sau un `Drawable`. Aici este un link, iar numele o declară.

### 31.0.2 Fără `= null`

În G1097, câmpul se termina cu `= null`. În G1099 se termină cu `;`. Pentru compilator, cele două variante sunt **identice**: un câmp de tip referință, neinițializat explicit, primește `null`.

**Ce înveți:** inițializatorul explicit nu schimbă comportamentul, schimbă **ce citește următorul programator**. `= null` este un comentariu scris în cod: „acest câmp poate lipsi". Absența lui nu înseamnă că câmpul este obligatoriu — înseamnă doar că autorul nu a simțit nevoia să spună asta.

**RISC, identic în ambele variante:** `null` ajunge în `etPoster.setText(null)`. Apelul este legal și afișează un câmp gol. Dacă însă ai apela `posterUrl.length()` pe el, ai lua `NullPointerException`. Modelul nu te protejează în niciuna dintre cele două grupe.

### 31.0.3 Constructorul fără parametri este primul

În G1097, constructorul gol stă la **linia 127**, după toate getter-ele și setter-ele. În G1099 stă la **linia 18**, imediat după câmpuri și înaintea constructorului cu 10 parametri.

Pentru compilator, poziția nu contează deloc. Pentru cititor, contează mult:

- vezi imediat că există un constructor gol, deci `new Movie()` este legal;
- vezi imediat perechea de constructori, unul lângă altul;
- nu ajungi la finalul fișierului ca să afli dacă `saveMovie()` are cu ce construi obiectul.

**Ce înveți:** ordinea membrilor într-o clasă este o **decizie de citire**, nu de semantică. Java nu are „ordine obligatorie a membrilor" — dar are o ordine utilă: câmpuri, constructori, metode.

**De ce contează la examen:** dacă ți se cere „scrie constructorul fără parametri", îl poți pune oriunde. Dacă ți se cere „explică de ce există", răspunsul este același indiferent de poziție: un constructor cu parametri **suprimă** constructorul implicit generat de compilator.

### 31.0.4 `toString()` nu include posterul

`toString()` este contractul de afișare în listă. `ArrayAdapter` cu `android.R.layout.simple_list_item_1` umple un `TextView` cu `item.toString()`. Tot ce nu apare în `toString()` este **invizibil pe ecran**.

În G1099, posterul lipsește din `toString()`. În G1097, apare ca `", poster='" + poster + '\''`.

**Ce înveți:** `toString()` nu se actualizează singur. A fost generat o dată de IntelliJ, iar câmpul adăugat ulterior lipsește. Este cel mai frecvent loc în care un câmp „dispare" din interfață fără ca cineva să fi șters ceva.

**Consecința practică:** două filme care diferă **doar** prin URL-ul posterului arată identic în `ListView`. Rândul este mai scurt și mai lizibil, dar lista nu mai distinge cele două intrări.

### 31.0.5 `android.media.Rating` — importul care arată ca altceva

Acesta este diferența cea mai interesantă din capitol și merită citită încet.

`import android.media.Rating;` este **prezent în G1099 și absent în G1097**. Și este **nefolosit**.

Ce este `android.media.Rating`: o clasă reală din framework, disponibilă din **API 21**, care descrie ratingul unui conținut media. Are metode ca `newStarRating(int maxStars, float starRating)`, `getStarRating()` sau `isRated()`. Este un **obiect de valoare**, nu un widget: nu se desenează, nu se atașează la un layout, nu are `OnRatingBarChangeListener`.

Ce este widget-ul din formular: `RatingBar`, adică `android.widget.RatingBar`. O bară de stele desenată pe ecran, cu `getRating()` care întoarce `float` și `setRating(float)`.

Cele două clase:

- au nume care începe la fel;
- nu au nicio relație de moștenire între ele;
- trăiesc în pachete diferite (`android.media` vs `android.widget`);
- nu se pot înlocui una pe alta.

**RISC:** un student care citește doar blocul de importuri poate crede că formularul folosește API-ul de rating media. Nu îl folosește. `rbRating` este declarat `RatingBar`, iar `getRating()` este metoda lui `RatingBar`.

**Ce înveți:** un import **nu dovedește** că tipul este folosit. Dovada este o apariție a numelui în afara liniei de import. Aici, `Rating` apare exact o dată în tot fișierul — chiar în import.

### 31.0.6 Importurile moarte, pe fișiere

| Fișier | Import mort | De ce este mort |
|---|---|---|
| `MainActivity.java` | `android.widget.Toast` | nu există niciun `Toast.makeText(...)` în fișier |
| `MainActivity.java` | `java.util.Date` | tipul `Date` nu este scris nicăieri; `getTime()` întoarce un `Date`, dar tipul este inferat |
| `ItemActivity.java` | `android.media.Rating` | vezi 31.0.5 |
| `ItemActivity.java` | `android.widget.Switch` | câmpul `swWatched` este `MaterialSwitch`, nu `Switch` |
| `ItemActivity.java` | `com.google.android.material.snackbar.Snackbar` | nu există niciun `Snackbar.make(...)` în fișier |

`android.widget.Switch` este un caz special: **toate grupele** declară `private MaterialSwitch swWatched;`, iar `MaterialSwitch` extinde `SwitchCompat`, nu `Switch`. Deci, oriunde apare importul `android.widget.Switch`, el este mort. În G1099 apare.

**Ce înveți:** compilatorul **nu** se plânge de importurile nefolosite. Doar lint-ul din Android Studio le marchează, cu un avertisment galben, iar avertismentul nu blochează build-ul. De aceea rămân în fișier ani întregi.

**De ce contează la examen:** „care importuri sunt nefolosite?" este o întrebare cu răspuns exact, verificabil. Trebuie să poți număra aparițiile numelui, nu să ghicești după nume.

### 31.0.7 `movie_item.xml` nu există

G1097 are un al șaptelea fișier, `movie_item.xml` — un card de listă pregătit pentru laboratorul următor (RecyclerView), dar **nefolosit de niciun cod**. G1099 nu îl are deloc.

**Ce înveți:** aplicația nu depinde de el. Absența lui nu schimbă nimic la runtime, pentru că niciun `findViewById`, niciun adapter și niciun `LayoutInflater` nu îl referă. Este un fișier „pregătit", nu un fișier „folosit".

**Consecință pentru capitol:** G1099 are **șase** fișiere de adnotat, nu șapte. Secțiunile 31.2–31.7 acoperă tot codul care rulează.

### 31.0.8 Layout-urile și manifestul sunt identice

`activity_main.xml` și `activity_item.xml` sunt identice cu cele din G1097. `AndroidManifest.xml` diferă doar prin numele temei: `@style/Theme.G1099` în loc de `@style/Theme.G1097`. Numele complet al pachetului nu apare în manifest — el vine din `namespace`-ul declarat în `build.gradle`, iar aici toate numele de clase sunt relative (`.activities.MainActivity`).

**Ce înveți:** diferențele dintre grupe sunt în **cod**, nu în layout. Interfața este comună; logica este cea care variază. Este exact ce trebuie să compari când ai două variante ale aceleiași teme.

---

## 31.1 Cum să citești acest capitol

Acesta nu este un capitol de exerciții. Este un capitol de **citire cu lupa**: iei fiecare fișier al aplicației și îl parcurgi linie cu linie, cu explicația chiar deasupra.

- **Citește codul întâi, comentariul al doilea.** Acoperă cu mâna blocul de comentarii, spune ce face linia, apoi verifică. Dacă ai citit comentariul primul, ai impresia că știai — dar ai recunoscut, nu ai reconstruit.
- **Blocurile `TEORIE`** apar înaintea fiecărei clase și explică *de ce* există structura, nu *cum* funcționează. Sunt partea care se uită cel mai repede; sunt și partea care se cere la examen.
- **Blocurile numerotate** („1. Validare", „2. Curățare") descriu pașii unei metode în ordinea execuției. Ordinea este parte din lecție: inversate, metoda se comportă altfel.
- **Marcajele `RISC:`, `BUG:` și `DANGER!`** semnalează locurile unde codul funcționează astăzi, dar se poate rupe, sau unde se rupe deja. Sunt singurele locuri din capitol în care nu descriu, ci avertizez.
- **Diagramele ASCII** arată ce nu se vede în cod: obiectul care călătorește între activități, arborele de view-uri, ordinea de execuție din `onCreate`.
- **Compară cu capitolul 22.** Fiecare secțiune are un corespondent în codul G1097. Diferențele sunt în 31.0; restul este comun. Dacă ai citit deja capitolul 22, citește acest capitol ca pe o **verificare**: unde crezi că știi deja, oprește-te și spune cu voce tare de ce linia este acolo.
- **Nu memora.** Scopul este să poți reconstrui fișierul pornind de la o diagramă. Dacă poți desena fluxul FAB → `ItemActivity` → `Intent` → listă, codul îl scrii singur.

---

## 31.2 `Movie.java` — modelul de date

Primul fișier și singurul care nu atinge Android. Tot ce urmează în capitol depinde de el.

```java
/*
 * ======================================================================================
 * FIȘIER: Movie.java — MODELUL DE DATE AL APLICAȚIEI
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   O clasă POJO (Plain Old Java Object): 10 câmpuri private, un constructor fără
 *   parametri, un constructor cu 10 parametri, o suprascriere de `toString()` și
 *   20 de getter-e/setter-e. Zero logică de business, zero referințe la Android.
 *
 * DE CE EXISTĂ:
 *   Ca să transporte datele unui film dintr-un ecran în altul fără să depindă de UI.
 *   `MainActivity` ține `List<Movie>`; `ItemActivity` construiește un `Movie`.
 *
 * DE CE DEPINDE:
 *   Doar de `java.io.Serializable` și `java.util.Date`. Nimic din `android.*`.
 *   De aceea clasa poate fi testată pe JVM, fără emulator.
 *
 * CINE DEPINDE DE EL:
 *   `MainActivity` (lista, adapterul, cele 3 filme demo), `ItemActivity`
 *   (`fillForm` citește, `saveMovie` scrie), `ArrayAdapter` (apelează `toString()`).
 *
 * CE NU FACE:
 *   Nu validează nimic. Nu știe ce este un `EditText`, un `Intent` sau un `ListView`.
 *   Nu are `id`: identitatea filmului în listă este POZIȚIA, nu un câmp.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   Tot fluxul de date. `Intent.putExtra` nu ar avea ce serializa, `ArrayAdapter`
 *   nu ar avea ce afișa, iar `ItemActivity` ar trebui să trimită 10 extra-uri
 *   separate și să le recompună manual în `MainActivity`.
 * ======================================================================================
 */

// PACHETUL: `model` — stratul de date, separat de `activities`.
// DE CE CONTEAZĂ: `ItemActivity` importă `ro.ase.ie.g1099.model.Movie`, niciodată invers.
//   Modelul nu știe cine îl folosește. Este singura regulă de arhitectură din aplicație.
package ro.ase.ie.g1099.model;

// ======================================================================================
// IMPORT 1: java.io.Serializable
// ======================================================================================
// CE ESTE: o interfață MARKER — nu are nicio metodă de implementat.
// DE CE AICI: `Intent.putExtra(String, Serializable)` este cea mai simplă cale de a
//   trimite un obiect întreg către altă activitate. Fără `implements Serializable`,
//   apelul `intent.putExtra(MOVIE_EXTRA, movie)` nu găsește nicio suprascriere
//   potrivită și fișierul NU COMPILEAZĂ.
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
//   `Serializable` din fabrică și este tipul folosit în tot proiectul.
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
 * 5. **Zece câmpuri, nu nouă** — posterul este al zecelea. El nu apare în `toString()`
 *    (vezi 31.0.4), dar există în model, are getter și setter, și este citit de
 *    `ItemActivity` la editare. Un câmp poate exista fără să fie afișat.
 *
 * VIZUAL: obiectul care traversează granița dintre activități
 *
 *   [MainActivity]                    [Intent / Bundle]                [ItemActivity]
 *   movies: List<Movie>
 *     [0] Movie@A  ------------------+
 *                                    |
 *                      putExtra("movie", Movie@A)
 *                                    |
 *                          serialize -> bytes
 *                                    |
 *                          Bundle { "movie" -> bytes }
 *                                    |
 *                          startActivityForResult
 *                                    |
 *                          deserialize -> Movie@A'
 *                                    |
 *                          (obiect NOU, adresă nouă)
 *
 *   Movie@A rămâne în lista din MainActivity. Modificarea lui Movie@A' nu se vede
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
    // ATENȚIE: tipul este `float`, nu `android.media.Rating`. Vezi 31.0.5 — importul
    //   acela este mort, iar widget-ul este `RatingBar`.
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
    // OBSERVAȚIE: comentariul din sursă spune „Switch", dar tipul real al widget-ului
    //   este `MaterialSwitch`. Comentariile nu se actualizează singure.
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
    // CÂMPUL 10: posterUrl
    // ==================================================================================
    // TIP: String — un URL (sau orice text) către afișul filmului.
    // WIDGET SURSĂ: `etPoster` (inputType=textUri) -> `getText().toString()`.
    // DE CE NU are `= null` explicit (diferența față de G1097): `String` este oricum
    //   `null` implicit. Absența inițializatorului nu schimbă comportamentul, doar
    //   nota de documentație. Vezi 31.0.2.
    // DE CE se numește `posterUrl` și nu `poster`: sufixul declară că valoarea este
    //   un LINK, nu o imagine. Getter-ul se numește, în consecință, `getPosterUrl()`.
    // RISC: `null` ajunge în `etPoster.setText(null)` la editare — legal, dar afișează
    //   câmp gol. Dacă ai apela `.length()` pe el, ai lua `NullPointerException`.
    // ==================================================================================
    private String posterUrl;

    // ==================================================================================
    // CONSTRUCTORUL FĂRĂ PARAMETRI — PRIMUL ÎN FIȘIER
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
    // DE CE ESTE PRIMUL (diferența față de G1097, unde este ultimul):
    //   poziția nu contează pentru compilator, dar aici cititorul vede imediat că
    //   `new Movie()` este legal. Vezi 31.0.3.
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
    // ==================================================================================
    public Movie(String title, Date release, String genre, double budget, int duration, float rating, boolean watched, String approval, boolean onWatchlist, String posterUrl) {

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

        // Ultimul câmp: aici se vede și diferența de nume față de G1097.
        // `this.posterUrl` este câmpul; `posterUrl` este parametrul. Ambele au același nume.
        this.posterUrl = posterUrl;
    }

    // ==================================================================================
    // toString() — CONTRACTUL DE AFIȘARE ÎN LISTĂ
    // ==================================================================================
    // DE CE ESTE OBLIGATORIU AICI:
    //   `ArrayAdapter` cu `android.R.layout.simple_list_item_1` primește un `TextView`
    //   și îl umple cu `item.toString()`. Fără suprascriere, `Object.toString()` ar
    //   întoarce `ro.ase.ie.g1099.model.Movie@a1b2c3d` — adresa din memorie.
    //
    // FLUXUL EXACT:
    //   ListView.getView(position) -> ArrayAdapter.getView(...) -> TextView.setText(
    //   movies.get(position).toString())
    //
    // DE CE `@Override`: compilatorul verifică semnătura. Dacă scrii `tostring()`
    //   cu literă mică, fără adnotare nu primești nicio eroare — doar metoda ta
    //   nu este apelată niciodată.
    //
    // DIFERENȚA FAȚĂ DE G1097: posterul NU apare aici. Nouă câmpuri, nu zece.
    //   Vezi 31.0.4 — un câmp poate exista în model fără să fie afișat.
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
                ", onWatchlist=" + onWatchlist +

                // Acolada de închidere a obiectului, ca text.
                // AICI S-AR FI AFIȘAT POSTERUL, în G1097: ", poster='" + poster + '\''.
                // În G1099 lipsește, iar rândul din listă se termină după onWatchlist.
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

    // GETTER pentru URL-ul posterului. Poate întoarce `null`.
    // NUMELE: `getPosterUrl`, nu `getPoster` — diferența față de G1097.
    //   `ItemActivity.fillForm` apelează exact acest nume.
    public String getPosterUrl() {
        return posterUrl;
    }

    // SETTER pentru poster. Acceptă `null` fără să se plângă.
    // `ItemActivity.saveMovie` apelează exact acest nume.
    public void setPosterUrl(String posterUrl) {
        this.posterUrl = posterUrl;
    }
}
```

**Tabel de referință pentru câmpurile din `Movie.java`:**

| # | Câmp | Tip | Widget sursă | Apare în `toString()`? |
|---|---|---|---|---|
| 1 | `title` | `String` | `etTitle` | da |
| 2 | `release` | `Date` | `etRelease` + dialog | da |
| 3 | `genre` | `String` | `spGenre` | da |
| 4 | `budget` | `double` | `etBudget` | da |
| 5 | `duration` | `int` | `sbDuration` | da |
| 6 | `rating` | `float` | `rbRating` | da |
| 7 | `watched` | `boolean` | `swWatched` | da |
| 8 | `approval` | `String` | `rgApproval` | da |
| 9 | `onWatchlist` | `boolean` | `cbonWatchList` | da |
| 10 | `posterUrl` | `String` | `etPoster` | **nu** |

---
## 31.3 `MainActivity.java` — lista și navigarea

Al doilea fișier și singurul care ține **starea** aplicației. Tot ce se vede pe ecranul de start trece prin el.

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
 * DE CE DEPINDE: de `ListView`, `ArrayAdapter`, `Intent`, de Activity Result API
 *   și de modelul `Movie`. Nu depinde de niciun widget de formular.
 *
 * CINE DEPINDE DE EL: `ItemActivity`, care citește `MainActivity.MOVIE_EXTRA` și
 *   `MainActivity.POSITION_EXTRA` — cele două constante sunt contractul dintre ecrane.
 *
 * CE NU FACE: nu validează date, nu desenează rânduri personalizate, nu salvează
 *   nimic pe disc. Lista trăiește cât trăiește procesul.
 *
 * CE S-AR RUPE FĂRĂ EL: aplicația ar porni direct într-un formular fără listă,
 *   iar rezultatul salvat nu ar avea unde să se întoarcă.
 * ======================================================================================
 */

// PACHETUL: `activities` — stratul de UI. Modelul stă în `model`, nu aici.
package ro.ase.ie.g1099.activities;

// ======================================================================================
// IMPORTURI — GRUPATE PE SURSĂ
// ======================================================================================
// android.*        — clase din framework (Intent, Bundle, View, widget-uri)
// androidx.*       — biblioteci Jetpack (AppCompat, EdgeToEdge, insets, activity result)
// com.google.*     — Material Components (FloatingActionButton)
// java.util.*      — colecții și date
// ro.ase.ie.g1099  — modelul și clasa R generată
//
// REGULĂ DE CITIRE: fiecare import trebuie să aibă un consumator în fișier.
//   Două nu îl au — `Toast` și `Date`. Sunt marcate mai jos. Vezi 31.0.6.
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
//   Nu există niciun `Toast.makeText(...)` în tot fișierul. Import mort.
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
//   ATENȚIE: numele `Date` nu este scris nicăieri în corpul fișierului. `getTime()`
//   întoarce un `Date`, dar tipul este inferat, nu declarat. Import mort.
import java.util.Date;

// GregorianCalendar: constructorul cu (an, lună, zi) folosit pentru filmele demo.
import java.util.GregorianCalendar;

// List: tipul DECLARAT al listei. Interfața, nu implementarea.
import java.util.List;

// R: clasa generată din resurse. Fără ea, `R.layout.activity_main` nu există.
import ro.ase.ie.g1099.R;

// Movie: modelul de date.
import ro.ase.ie.g1099.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: CINE DEȚINE STAREA
 * ======================================================================================
 *
 * 1. **O singură sursă de adevăr.** `movies` este `final` și trăiește cât activitatea.
 *    `ItemActivity` nu are voie să modifice lista direct: primește o COPIE a unui
 *    film și trimite înapoi un `Movie` NOU. MainActivity decide ce face cu el.
 *
 * 2. **Adapterul ține REFERINȚA, nu o copie.** `new ArrayAdapter<>(..., movies)`
 *    primește lista, nu conținutul ei. De aceea `movies.add(...)` se vede în adapter
 *    imediat ce apelezi `notifyDataSetChanged()`. Dacă ai scrie
 *    `new ArrayList<>(movies)`, modificările nu s-ar mai vedea.
 *
 * 3. **Activity Result API înlocuiește `startActivityForResult`.** Nu mai există
 *    `onActivityResult` suprascris în activitate. Există un `launcher` cu un
 *    callback înregistrat o singură dată, în `onCreate`.
 *
 * 4. **Ordinea din `onCreate` este semantică.** `initListeners()` se apelează ÎNAINTE
 *    ca `launcher` să fie atribuit. Funcționează pentru că listener-ul citește
 *    CÂMPUL `launcher` la momentul click-ului, nu la momentul atașării.
 *
 * VIZUAL: două intrări, o singură ieșire
 *
 *   FAB apăsat  ----------------------+
 *                                     |
 *   rând apăsat ---+                  |
 *                  |                  v
 *                  |        new Intent(MainActivity.this, ItemActivity.class)
 *                  |                  |
 *                  |        (FAB: fără extra-uri  -> insert)
 *                  |        (rând: MOVIE + POSITION -> edit)
 *                  |                  |
 *                  +------------------+--> launcher.launch(intent)
 *                                             |
 *                                             v
 *                                     ItemActivity
 *                                             |
 *                                   setResult(RESULT_OK, intent)
 *                                             |
 *                                             v
 *                              callback: RESULT_OK?
 *                                  position == -1 -> movies.add(movie)
 *                                  position >= 0  -> movies.set(position, movie)
 *                                             |
 *                                             v
 *                                  movieAdapter.notifyDataSetChanged()
 * ======================================================================================
 */
public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // CELE DOUĂ CONSTANTE — CONTRACTUL DINTRE CELE DOUĂ ECRANE
    // ==================================================================================
    // CHEIA sub care călătorește filmul în Intent. `"movie"` este un String arbitrar;
    //   important este să fie ACEEAȘI valoare la trimitere și la citire.
    // DE CE `protected` și nu `private`: `ItemActivity` este în același pachet
    //   (`ro.ase.ie.g1099.activities`) și le citește ca `MainActivity.MOVIE_EXTRA`.
    //   `protected` acoperă și subclasele, dar aici pachetul este motivul real.
    // DE CE `static final`: sunt constante de CLASĂ, nu de instanță. Nu depind de
    //   niciun obiect MainActivity.
    // RISC: o greșeală de literă într-una din cele două locuri produce `null`
    //   la citire, fără nicio excepție și fără nicio eroare de compilare.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";

    // Butonul „+". Tipul este clasa Material, nu `ImageButton`.
    //   Este căutat în `initControls` și folosit în `initListeners`.
    private FloatingActionButton fabInsert;

    // Lista derulantă. Căutată în `initControls`, primește adapterul tot acolo.
    private ListView listView;

    // Launcher-ul de rezultat. NU este inițializat aici: primește valoarea abia
    //   la finalul lui `onCreate`, după `registerForActivityResult`.
    // DE CE un câmp și nu o variabilă locală: listener-ii din `initListeners`
    //   trebuie să îl poată citi la momentul click-ului, adică mult după `onCreate`.
    private ActivityResultLauncher<Intent> launcher;

    // LISTA — singura stare reală a aplicației.
    // `final` înseamnă că REFERINȚA nu se schimbă: nu poți scrie `movies = ...`.
    //   Conținutul, însă, se schimbă liber: `add`, `set`, `clear` sunt permise.
    // DE CE `List` și nu `ArrayList` la declarare: tipul declarat este interfața,
    //   implementarea este ascunsă. Schimbi `ArrayList` cu `LinkedList` fără să
    //   atingi restul fișierului.
    // DE CE `new ArrayList<>()` aici: lista există înainte de `onCreate`, deci
    //   `addSampleMovies()` o poate umple fără verificări de `null`.
    private final List<Movie> movies = new ArrayList<>();

    // ADAPTERUL. Ține REFERINȚA la `movies`, nu o copie.
    // Nu este inițializat aici pentru că are nevoie de `Context` (`this`), iar
    //   `this` este utilizabil abia după `super.onCreate`.
    private ArrayAdapter<Movie> movieAdapter;

    // ==================================================================================
    // onCreate — NOUĂ PAȘI, ÎN ORDINE
    // ==================================================================================
    // CE FACE: construiește ecranul, încarcă datele demo, creează adapterul, leagă
    //   listener-ii și înregistrează launcher-ul de rezultat.
    // CUM: 1. infrastructură (super, edge-to-edge, layout, insets)
    //      2. date (addSampleMovies)
    //      3. adapter
    //      4. controale (findViewById + setAdapter)
    //      5. listener-i
    //      6. launcher
    // RISC: `registerForActivityResult` trebuie apelat ÎNAINTE ca activitatea să
    //   fie STARTED. Aici este în `onCreate`, deci este legal. Mutat în `onResume`,
    //   ar arunca `IllegalStateException`.
    // REF: același șablon de insets apare și în `ItemActivity.onCreate`.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Edge-to-edge: conținutul este desenat și sub bara de status și sub cea de
        // navigare. Fără el, aplicația ar avea o bandă proprie în partea de sus.
        EdgeToEdge.enable(this);

        // Umflă `activity_main.xml` în arborele de view-uri. Din acest moment,
        //   `findViewById` poate găsi `R.id.main`, `R.id.listView` și FAB-ul.
        setContentView(R.layout.activity_main);

        // Insets: măsoară barele de sistem și le transformă în padding pe container.
        // `(v, insets) -> { ... }` este o expresie lambda pentru
        //   `OnApplyWindowInsetsListener` — interfața are o singură metodă.
        // DE CE `R.id.main`: FrameLayout-ul rădăcină din `activity_main.xml`.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            // `systemBars()` = bara de status + bara de navigare, împreună.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            // Padding în loc de margin: margin-ul ar fi ignorat de părintele FrameLayout.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            // `return insets` = „nu am consumat nimic"; evenimentul poate merge mai departe.
            return insets;
        });

        // Pasul 2: umple lista cu cele 3 filme demo.
        // DE CE ÎNAINTE de crearea adapterului: ca adapterul să pornească deja cu 3
        //   elemente. Dacă ar fi după, ar funcționa la fel, dar ar cere un
        //   `notifyDataSetChanged()` suplimentar.
        addSampleMovies();

        // Pasul 3: creează adapterul.
        // `android.R.layout.simple_list_item_1` = un singur TextView pe rând, din
        //   framework. Nu este un layout al proiectului — de aceea prefixul `android.`.
        // Al treilea argument este LISTA, nu o copie a ei. Vezi blocul de teorie.
        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

        // Pasul 4: leagă referințele la view-uri și instalează adapterul.
        initControls();

        // Pasul 5: atașează listener-ii.
        // ATENȚIE: `launcher` este încă `null` în acest moment. Este în regulă —
        //   listener-ii îl citesc abia la click, iar până atunci `onCreate` s-a terminat.
        initListeners();

        // Pasul 6: înregistrează launcher-ul.
        // `StartActivityForResult` este contractul care pornește o activitate și
        //   așteaptă un rezultat — echivalentul modern al lui `startActivityForResult`.
        // Callback-ul este o clasă anonimă, nu o expresie lambda, pentru că are
        //   două niveluri de indentare și un singur metodă cu corp lung.
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // FILTRUL: rezultatul contează doar dacă activitatea secundară
                        //   a apelat `setResult(RESULT_OK, ...)`. `RESULT_CANCELED`
                        //   (butonul Back) intră pe ramura falsă și nu face nimic.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // `getData()` = Intent-ul construit în `ItemActivity.saveMovie`.
                            // RISC: dacă o activitate ar întoarce RESULT_OK fără date,
                            //   `intent` ar fi `null` și linia următoare ar arunca NPE.
                            //   Aici nu se întâmplă: `saveMovie` pune mereu un Intent.
                            Intent intent = o.getData();

                            // Citește filmul. Metoda este cea VECHE, cu cast explicit —
                            //   nu `IntentCompat`, cum folosește `ItemActivity`.
                            //   Este depreciată din API 33, dar funcționează.
                            // OBIECTUL ESTE O COPIE deserializată, nu originalul.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // Citește poziția. `-1` este valoarea implicită atunci când
                            //   extra-ul lipsește — adică exact în modul insert.
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // RAMURA INSERT: nu există poziție.
                            if(position == -1)
                            {
                                // Adaugă la finalul listei.
                                movies.add(movie);

                                // Anunță adapterul. Fără acest apel, ListView-ul NU
                                //   știe că lista s-a schimbat și nu redesenează nimic.
                                movieAdapter.notifyDataSetChanged();
                            }
                            // RAMURA EDIT: există poziție.
                            else
                            {
                                // ÎNLOCUIEȘTE elementul de pe poziție. Nu `add` — ar
                                //   duplica filmul. Nu `remove` + `add` — ar schimba ordinea.
                                movies.set(position, movie);

                                // Același anunț. Ambele ramuri au nevoie de el.
                                movieAdapter.notifyDataSetChanged();
                            }
                        }
                    }
                });
    }

    // ==================================================================================
    // initListeners — CE SE ÎNTÂMPLĂ LA APĂSARE
    // ==================================================================================
    // CE FACE: atașează doi listener-i — unul pe FAB, unul pe rândurile listei.
    // CUM: 1. FAB -> Intent fără extra-uri -> insert
    //      2. rând -> Intent cu MOVIE + POSITION -> edit
    // RISC: metoda este apelată înainte ca `launcher` să fie atribuit. Funcționează
    //   doar pentru că listener-ii citesc câmpul la click, nu la atașare.
    // REF: același model de listener anonim apare de patru ori în `ItemActivity`.
    // ==================================================================================
    private void initListeners() {

        // Listener pe FAB. Clasa anonimă implementează `View.OnClickListener`.
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // `MainActivity.this` — NU `this`. În interiorul clasei anonime,
                //   `this` este listener-ul, nu activitatea. `Context`-ul cerut de
                //   constructorul lui Intent este activitatea.
                // Al doilea argument este clasa activității de pornit.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // FĂRĂ extra-uri. Absența lui MOVIE_EXTRA este exact semnalul de
                //   „mod insert" pe care îl citește `ItemActivity.onCreate`.
                launcher.launch(intent);
            }
        });

        // Listener pe rândurile listei. `AdapterView.OnItemClickListener` are patru
        //   parametri: părintele, view-ul rândului, poziția și id-ul.
        // `id` este al patrulea și este IGNORAT aici: identitatea este poziția.
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                // Același Intent către aceeași activitate.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // AICI este diferența față de FAB: filmul pleacă spre formular.
                //   `movies.get(position)` este obiectul din listă; `putExtra` îl
                //   SERIALIZEAZĂ. Formularul va primi o copie.
                intent.putExtra(MOVIE_EXTRA, movies.get(position));

                // Poziția pleacă separat, ca `int`. Ea nu face parte din model.
                intent.putExtra(POSITION_EXTRA, position);

                // Pornește activitatea prin launcher, ca rezultatul să ajungă în callback.
                launcher.launch(intent);
            }
        });
    }

    // ==================================================================================
    // initControls — FINDVIEWBYID ȘI SETADAPTER
    // ==================================================================================
    // CE FACE: leagă cele două câmpuri de view-urile din XML și instalează adapterul.
    // CUM: 1. FAB după id  2. ListView după id  3. setAdapter
    // RISC: dacă un id nu există în layout, `findViewById` întoarce `null` și
    //   apelul următor aruncă NPE. Aici ambele id-uri există în `activity_main.xml`.
    // REF: `ItemActivity.initControls` face același lucru pentru 13 view-uri.
    // ==================================================================================
    private void initControls() {

        // `R.id.floatingActionButton` — id-ul din XML, nu numele câmpului.
        fabInsert = findViewById(R.id.floatingActionButton);

        // `R.id.listView` — id-ul din XML.
        listView = findViewById(R.id.listView);

        // Instalează adapterul. Din acest moment, `android:entries="@array/items"`
        //   din XML este IGNORAT: `setAdapter` îl înlocuiește complet.
        listView.setAdapter(movieAdapter);
    }

    // ==================================================================================
    // addSampleMovies — CELE TREI FILME DEMO
    // ==================================================================================
    // CE FACE: adaugă trei `Movie` în listă, folosind constructorul cu 10 parametri.
    // CUM: trei apeluri `movies.add(new Movie(...))`, fiecare cu 10 argumente
    //   poziționale, în ordinea din semnătură.
    // RISC: ordinea argumentelor este POZIȚIONALĂ. `"Sci-Fi"` trebuie să fie al
    //   treilea, nu al doilea — altfel ajunge în `release` și nu compilează, sau
    //   ajunge în `genre` când tipurile coincid și compilează greșit.
    // REF: constructorul este adnotat în 31.2; tabelul de poziții este acolo.
    // ==================================================================================
    private void addSampleMovies() {

        // FILMUL 1 — Inception.
        // `new GregorianCalendar(an, lună, zi)` — ATENȚIE: luna este 0-based.
        //   `Calendar.JULY` este 6, nu 7. `getTime()` transformă calendarul în `Date`.
        // Argumentele 4..10: buget (int lărgit la double), durată, rating (`4.5f`),
        //   watched, approval, onWatchlist, posterUrl.
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

        // FILMUL 2 — Toy Story. `4f` este un float literal: fără `f`, ar fi double
        //   și nu ar încăpea în parametrul `float rating`.
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

        // FILMUL 3 — The Matrix. `Calendar.MARCH` este 2 (0-based).
        //   `watched = false`, `onWatchlist = true` — jedința combinație care diferă
        //   de primele două și care arată că cele două booleene sunt independente.
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

**Tabel de referință pentru `onCreate`:**

| # | Linie | Ce construiește | Depinde de |
|---|---|---|---|
| 1 | `super.onCreate` | lanțul AppCompat | — |
| 2 | `EdgeToEdge.enable` | desenare sub bare | — |
| 3 | `setContentView` | arborele de view-uri | `activity_main.xml` |
| 4 | listener de insets | padding pe `R.id.main` | id-ul `main` |
| 5 | `addSampleMovies` | 3 `Movie` în listă | `Movie` |
| 6 | `new ArrayAdapter` | adapterul | lista, `this` |
| 7 | `initControls` | FAB, ListView, `setAdapter` | `R.id.*` |
| 8 | `initListeners` | 2 listener-i | `launcher` (încă `null`) |
| 9 | `registerForActivityResult` | `launcher` | contractul |

---
## 31.4 `ItemActivity.java` — formularul

Al treilea fișier și cel mai lung dintre cele trei clase Java. Aici se construiește un `Movie` din 10 widget-uri și se trimite înapoi.

```java
/*
 * ======================================================================================
 * FIȘIER: ItemActivity.java — FORMULARUL DE INSERT ȘI EDIT
 * ======================================================================================
 * CE ESTE: o singură activitate care servește DOUĂ moduri. Dacă primește un `Movie`
 *   în Intent, este editare; dacă nu primește nimic, este inserare.
 *
 * DE CE EXISTĂ: este ecranul care transformă widget-uri în model. Toate cele 10
 *   câmpuri ale lui `Movie` sunt produse aici, din `getText()`, `getProgress()`,
 *   `getRating()`, `isChecked()` și `getSelectedItem()`.
 *
 * DE CE DEPINDE: de `activity_item.xml` (13 view-uri), de `Movie`, de constantele
 *   `MainActivity.MOVIE_EXTRA` / `POSITION_EXTRA` și de Activity Result API
 *   (prin `setResult`).
 *
 * CINE DEPINDE DE EL: `MainActivity`, care primește Intent-ul de rezultat în callback.
 *
 * CE NU FACE: nu ține lista, nu știe ce poziție are filmul în listă (o primește),
 *   nu salvează nimic pe disc. Nu validează câmpurile înainte de salvare.
 *
 * CE S-AR RUPE FĂRĂ EL: aplicația ar avea listă, dar niciun mod de a adăuga sau
 *   modifica un film. FAB-ul ar porni o activitate inexistentă.
 *
 * ATENȚIE LA IMPORTURI: trei dintre ele sunt MOARTE — `android.media.Rating`,
 *   `android.widget.Switch` și `Snackbar`. Sunt marcate pe rând mai jos. Vezi 31.0.5.
 * ======================================================================================
 */

// PACHETUL: același `activities` ca MainActivity — de aceea constantele `protected`
//   ale lui MainActivity sunt vizibile aici fără import.
package ro.ase.ie.g1099.activities;

// DatePickerDialog: dialogul cu roți pentru an/lună/zi.
import android.app.DatePickerDialog;

// Intent: obiectul de rezultat, construit la salvare.
import android.content.Intent;

// Rating: clasa de rating pentru conținut MEDIA, din API 21.
//   IMPORT MORT. Nu este folosită nicăieri în fișier — apare exact o dată, aici.
//   Widget-ul din formular este `RatingBar`, cu totul altă clasă. Vezi 31.0.5.
import android.media.Rating;

// Bundle: doar în semnătura lui onCreate.
import android.os.Bundle;

// View: tipul parametrului din OnClickListener.
import android.view.View;

// Button: butonul de salvare (`btMovieAction`).
import android.widget.Button;

// CheckBox: bifa „Watchlist" (`cbonWatchList`).
import android.widget.CheckBox;

// CompoundButton: interfața comună pentru Switch și CheckBox; apare în semnătura
//   listener-ului de switch.
import android.widget.CompoundButton;

// DatePicker: tipul view-ului din callback-ul dialogului de dată.
import android.widget.DatePicker;

// EditText: titlul, data, bugetul și posterul.
import android.widget.EditText;

// RadioButton: cele 5 butoane de ghidaj parental.
import android.widget.RadioButton;

// RadioGroup: containerul celor 5 butoane.
import android.widget.RadioGroup;

// RatingBar: bara de stele. ACESTA este widget-ul de rating, nu `android.media.Rating`.
import android.widget.RatingBar;

// SeekBar: bara de durată.
import android.widget.SeekBar;

// Spinner: lista derulantă de genuri.
import android.widget.Spinner;

// Switch: widget-ul clasic de comutare.
//   IMPORT MORT. Câmpul `swWatched` este declarat `MaterialSwitch`, iar
//   `MaterialSwitch` extinde `SwitchCompat`, nu `Switch`. Numele `Switch` nu apare
//   nicăieri în afara acestei linii. Vezi 31.0.6.
import android.widget.Switch;

// TextView: cele două etichete dinamice (`tvDurationValue`, `tvWatchedValue`).
import android.widget.TextView;

// EdgeToEdge: desenare sub barele de sistem.
import androidx.activity.EdgeToEdge;

// NonNull: adnotare pe parametrul `buttonView` din listener-ul de switch.
//   Este o promisiune că parametrul nu este null; compilatorul nu o verifică,
//   dar lint-ul o folosește.
import androidx.annotation.NonNull;

// AppCompatActivity: clasa de bază a activității.
import androidx.appcompat.app.AppCompatActivity;

// IntentCompat: varianta tipată a lui `getSerializableExtra`, cu `Class<T>`.
//   Spre deosebire de MainActivity, care folosește metoda veche cu cast,
//   aici se folosește varianta modernă.
import androidx.core.content.IntentCompat;

// Insets / ViewCompat / WindowInsetsCompat: aceleași trei clase ca în MainActivity,
//   pentru padding-ul de sub barele de sistem.
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

// MaterialSwitch: switch-ul Material 3. Extinde SwitchCompat -> CompoundButton.
import com.google.android.material.materialswitch.MaterialSwitch;

// Snackbar: bară scurtă de mesaj, în partea de jos a ecranului.
//   IMPORT MORT. Nu există niciun `Snackbar.make(...)` în fișier.
import com.google.android.material.snackbar.Snackbar;

// ParseException: excepția aruncată de `SimpleDateFormat.parse` pe text invalid.
import java.text.ParseException;

// SimpleDateFormat: formatter-ul „dd/MM/yyyy" pentru câmpul de dată.
import java.text.SimpleDateFormat;

// Calendar: sursa de adevăr pentru dată.
import java.util.Calendar;

// Date: tipul întors de `dateFormat.parse(...)`.
import java.util.Date;

// Locale: formatul regional pentru formatter.
import java.util.Locale;

// R: resursele generate.
import ro.ase.ie.g1099.R;

// Movie: modelul construit la salvare și citit la umplere.
import ro.ase.ie.g1099.model.Movie;

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
 * 4. **Rezultatul este un Intent.** Activitatea nu întoarce un obiect prin `return`;
 *    îl pune într-un `Intent` și îl predă prin `setResult`.
 *
 * 5. **Ordinea din `onCreate` este critică.** `initListeners()` rulează ÎNAINTE de
 *    `fillForm()`. Motivul: `setChecked` și `setProgress` declanșează listener-ii,
 *    care actualizează etichetele. Invers, etichetele ar rămâne cu valorile din XML.
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
 *
 * VIZUAL: cele două moduri
 *
 *   Intent FĂRĂ MOVIE_EXTRA          Intent CU MOVIE_EXTRA
 *          |                                  |
 *          v                                  v
 *   existing == null                   existing != null
 *          |                                  |
 *   position rămâne -1                 position = getIntExtra(..., -1)
 *   formular gol                       fillForm(existing)
 *   buton: "Save Movie"                buton: "Update Movie"
 *          |                                  |
 *          +---------------+------------------+
 *                          v
 *                     saveMovie()
 *                          |
 *          position == -1 -> Intent FĂRĂ POSITION_EXTRA
 *          position >= 0  -> Intent CU POSITION_EXTRA
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
    // ATENȚIE: tipul este `RatingBar`, NU `android.media.Rating`. Importul acela
    //   este mort — vezi 31.0.5.
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
    // DE ACEA importul `android.widget.Switch` este mort: nu este tipul acestui câmp.
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
    // RISC: în modul edit, `fillForm` NU actualizează acest calendar — vezi BUG 4.
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
    // onCreate — INFRASTRUCTURĂ, CONTROALE, LISTENER-I, MOD
    // ==================================================================================
    // CE FACE: construiește ecranul, atașează listener-ii, apoi decide dacă umple
    //   formularul cu un film existent sau îl lasă gol.
    // CUM: 1. infrastructură (super, edge-to-edge, layout, insets)
    //      2. initControls
    //      3. initListeners
    //      4. citește Intent-ul
    //      5. dacă există film -> position, fillForm, titlu, text buton
    // RISC: ordinea 2-3-5 este obligatorie. `fillForm` are nevoie de view-uri (2)
    //   și trebuie să declanșeze listener-ii (3) pentru etichete.
    // REF: `MainActivity.onCreate` are aceeași primă fază de infrastructură.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Edge-to-edge: același apel ca în MainActivity.
        EdgeToEdge.enable(this);

        // Umflă `activity_item.xml`. Arborele are un ScrollView rădăcină cu id `main`.
        setContentView(R.layout.activity_item);

        // Insets pe containerul rădăcină. Identic cu MainActivity, cu o singură
        //   diferență de context: aici `R.id.main` este ScrollView-ul, nu FrameLayout-ul.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Faza 1: leagă cele 13 câmpuri de view-urile din XML.
        // DE CE PRIMA: `fillForm` are nevoie de ele, iar `initListeners` la fel.
        initControls();

        // Faza 2: atașează listener-ii.
        // DE CE ÎNAINTE DE `fillForm`: `fillForm` apelează `setChecked` și `setProgress`.
        //   Aceste apeluri DECLANȘEAZĂ listener-ii, care actualizează etichetele
        //   `tvWatchedValue` și `tvDurationValue`. Dacă listener-ii ar fi atașați după
        //   `fillForm`, etichetele ar rămâne cu valorile implicite din XML.
        initListeners();

        // Faza 3: citește Intent-ul de intrare.
        // `getIntent()` întoarce Intent-ul care a pornit activitatea. Nu este null:
        //   orice activitate este pornită cu un Intent, chiar și unul gol.
        Intent intent = getIntent();

        // Citire TIPATĂ a serializable-ului.
        // DE CE `IntentCompat` ȘI NU `intent.getSerializableExtra(...)`:
        //   Metoda veche este depreciată din API 33. `IntentCompat.getSerializableExtra`
        //   primește și clasa așteptată, deci face verificarea tipului înainte de cast
        //   și funcționează identic pe toate versiunile.
        // DE CE `MainActivity.MOVIE_EXTRA`: aceeași constantă ca la trimitere. O greșeală
        //   de literă aici ar produce `null` fără nicio eroare.
        // VALOAREA: `null` în modul insert (FAB-ul nu pune niciun extra).
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
            // Dacă tema nu are ActionBar, titlul nu se vede nicăieri pe ecran;
            //   feedback-ul vizibil pentru utilizator este textul butonului, mai jos.
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
    // CE FACE: copiază cele 10 valori din `Movie` în cele 10 widget-uri.
    // CUM: 1. câmpurile simple, în ordinea din model
    //      2. Spinner: buclă peste poziții, potrivire pe text
    //      3. RadioGroup: buclă peste copii, potrivire pe text
    // RISC: nu actualizează `releaseCal`. Vezi BUG 4 — data se pierde la update.
    // REF: fiecare linie este inversul unei linii din `saveMovie`.
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
        //   `Movie` este construit cu constructorul gol și salvat fără dată.
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

        // `MaterialSwitch.setChecked(boolean)` — DECLANȘEAZĂ listener-ul de switch,
        //   care scrie „Yes"/„No" în `tvWatchedValue`. De aceea listener-ii trebuie
        //   atașați înainte de `fillForm`.
        swWatched.setChecked(existing.isWatched());

        // `RatingBar.setRating(float)` — parametrul este `float`, exact tipul câmpului
        //   din model. O valoare de 4.5 aprinde 4 stele și jumătate.
        rbRating.setRating(existing.getRating());

        // `setText(null)` este legal: câmpul devine gol. Nu aruncă excepție.
        // Aici se vede diferența de nume față de G1097: `getPosterUrl()`, nu `getPoster()`.
        etPoster.setText(existing.getPosterUrl());

        // SPINNER — nu are `setValue`, are `setSelection(index)`.
        // De aceea este nevoie de o buclă: caută INDEXUL valorii care corespunde.
        // `getCount()` = numărul de elemente din `@array/movie_genre`.
        // `getItemAtPosition(index)` întoarce un `Object` (în practică, `String`).
        // `break` la prima potrivire: dacă array-ul ar avea duplicate, câștigă primul.
        // Dacă nu se găsește nicio potrivire, spinner-ul rămâne pe poziția 0 —
        //   silențios, fără eroare.
        for(int index=0; index<spGenre.getCount(); index++)
        {
            if(spGenre.getItemAtPosition(index).equals(existing.getGenre()))
            {
                // `setSelection` mută selecția. Nu declanșează niciun listener aici,
                //   pentru că nu am atașat niciunul pe Spinner.
                spGenre.setSelection(index);
                break;
            }
        }

        // RADIOGROUP — nici aici nu există `setValue`. `check(id)` primește un ID.
        // `getChildCount()` = 5 (cele 5 MaterialRadioButton).
        // `getChildAt(index)` întoarce `View`; cast la `RadioButton` pentru `getText()`.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
            if(rb.getText().toString().equals(existing.getApproval()))
            {
                // `check(...)` primește ID-ul copilului, nu indexul. De aceea se
                //   citește `getChildAt(index).getId()`.
                // Efect secundar: `check` dezbină automat butonul bifat anterior.
                rgApproval.check(rgApproval.getChildAt(index).getId());
                break;
            }
        }

        // CE NU FACE ACEASTĂ METODĂ: nu scrie în `releaseCal`.
        //   Textul este afișat corect, dar calendarul rămâne pe data de AZI.
        //   Vezi BUG 4, imediat după listă.
    }

    // ==================================================================================
    // initControls — 13 FINDVIEWBYID, ÎN ORDINEA DIN FORMULAR
    // ==================================================================================
    // CE FACE: leagă fiecare câmp Java de view-ul cu id-ul corespunzător din XML.
    // CUM: 13 apeluri `findViewById`, în ordinea vizuală a formularului.
    // RISC: fiecare id trebuie să existe în `activity_item.xml`. Un id greșit
    //   întoarce `null` și crapă la primul acces, nu aici.
    // REF: `MainActivity.initControls` are același rol, cu 2 view-uri.
    // ==================================================================================
    private void initControls() {

        // Cardul „Basics": titlul și data.
        etTitle = findViewById(R.id.etTitle);
        etRelease = findViewById(R.id.etRelease);

        // Genul — Spinner învelit într-un MaterialCardView în XML.
        spGenre = findViewById(R.id.spGenre);

        // Cardul „Production": bugetul și durata.
        etBudget = findViewById(R.id.etBudget);
        sbDuration = findViewById(R.id.sbDuration);

        // Cardul „Your verdict": rating, ghidaj, switch, bifă.
        rbRating = findViewById(R.id.rbRating);
        rgApproval = findViewById(R.id.rgApproval);

        // ATENȚIE: id-ul este `cbOnWatchList` (cu `O` mare), câmpul este
        //   `cbonWatchList` (cu `o` mic). Diferă doar prin majusculă.
        cbonWatchList = findViewById(R.id.cbOnWatchList);

        swWatched = findViewById(R.id.swWatched);

        // Cardul „Poster".
        etPoster = findViewById(R.id.etPoster);

        // Butonul de salvare. Id-ul este `btnMovieAction`, câmpul `btMovieAction`.
        btMovieAction = findViewById(R.id.btnMovieAction);

        // Cele două etichete dinamice. Sunt citite doar de listener-ii de mai jos.
        tvDurationValue = findViewById(R.id.tvDurationValue);
        tvWatchedValue = findViewById(R.id.tvWatchedValue);
    }

    // ==================================================================================
    // initListeners — PATRU LISTENER-I
    // ==================================================================================
    // CE FACE: atașează comportamentul celor patru widget-uri interactive.
    // CUM: 1. etRelease -> deschide dialogul de dată
    //      2. btMovieAction -> saveMovie
    //      3. swWatched -> actualizează eticheta „Yes"/„No"
    //      4. sbDuration -> actualizează eticheta „N min."
    // RISC: listener-ul de switch și cel de SeekBar sunt esențiale pentru `fillForm`;
    //   fără ele, etichetele ar rămâne desincronizate la editare.
    // REF: aceleași clase anonime ca în `MainActivity.initListeners`.
    // ==================================================================================
    private void initListeners() {

        // 1. CLICK PE CÂMPUL DE DATĂ -> dialog.
        // `EditText` este și editabil, dar aici click-ul este interceptat și înlocuit
        //   cu un dialog. Utilizatorul nu tastează data, o alege.
        etRelease.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showReleaseDatePicker();
            }
        });

        // 2. CLICK PE BUTON -> salvare.
        // Același listener face insert sau update; diferența este câmpul `position`.
        btMovieAction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveMovie();
            }
        });

        // 3. SWITCH -> etichetă.
        // `CompoundButton.OnCheckedChangeListener` are un singur metodă, cu două
        //   argumente: butonul și noua stare.
        // `@NonNull` pe `buttonView` este o adnotare de contract, nu o verificare
        //   la runtime.
        swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                // Operator ternar: „Yes" dacă este bifat, „No" altfel.
                // `setText` așteaptă `CharSequence`; ambii literali sunt `String`.
                tvWatchedValue.setText(isChecked ? "Yes" : "No");
            }
        });

        // 4. SEEKBAR -> etichetă.
        // Interfața are TREI metode; două rămân goale, dar TREBUIE scrise:
        //   altfel clasa anonimă nu compilează.
        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            // Apelat la fiecare schimbare de valoare.
            // `progress` = noua valoare (0..300).
            // `fromUser` = true dacă schimbarea vine de la deget, false dacă vine
            //   din cod (`setProgress`). Aici este IGNORAT intenționat: eticheta
            //   trebuie să reflecte valoarea în ambele cazuri.
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // `progress + " min."` — concatenare int cu String. Java convertește
                //   automat int-ul în text. Rezultat: „148 min.".
                tvDurationValue.setText(progress + " min.");
            }

            // Apelat când degetul atinge bara. Nu avem nevoie de el.
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            // Apelat când degetul ridică. Nu avem nevoie de el.
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });
    }

    // ==================================================================================
    // saveMovie — WIDGET-URI -> MODEL -> INTENT -> REZULTAT
    // ==================================================================================
    // CE FACE: construiește un `Movie` nou din valorile curente ale formularului,
    //   îl pune într-un Intent și îl trimite înapoi lui MainActivity.
    // CUM: 1. `new Movie()` — constructorul gol
    //      2. 9 setter-e directe din widget-uri
    //      3. buclă pe RadioGroup pentru al 10-lea câmp
    //      4. Intent fără target, cu MOVIE_EXTRA și, condiționat, POSITION_EXTRA
    //      5. setResult + finish
    // RISC: `Double.parseDouble` pe text gol aruncă `NumberFormatException` — BUG 1.
    // REF: fiecare linie este inversul unei linii din `fillForm`.
    // ==================================================================================
    private void saveMovie() {

        // Obiect NOU, nu obiectul primit. Chiar și în modul edit, filmul din listă
        //   nu este modificat direct: este înlocuit cu acesta, prin `movies.set`.
        Movie movie = new Movie();

        // `getText()` întoarce un `Editable`, nu un `String`. `toString()` face conversia.
        movie.setTitle(etTitle.getText().toString());

        // DATA: din `releaseCal`, NU din textul din `etRelease`.
        // `getTime()` transformă calendarul într-un `Date` nou.
        // Aici se vede BUG 4: în modul edit, `releaseCal` nu a fost sincronizat.
        movie.setRelease(releaseCal.getTime());

        // GENUL: `getSelectedItem()` întoarce `Object`; `toString()` îl face text.
        // Dacă spinner-ul ar fi gol, ar arunca NPE — aici lista vine din
        //   `@array/movie_genre` și nu este goală.
        movie.setGenre(spGenre.getSelectedItem().toString());

        // BUG 1: `Double.parseDouble("")` aruncă `NumberFormatException`.
        // ==============================================================================
        // `etBudget` pornește GOL în modul insert. Dacă utilizatorul apasă „Save Movie"
        //   fără să scrie un buget, aplicația CRAPĂ. Nu există nicio validare înainte.
        // REPARAȚIE: `String text = etBudget.getText().toString();`
        //             `double value = text.isEmpty() ? 0 : Double.parseDouble(text);`
        // ==============================================================================
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));

        // DURATA: direct din progresul barei. `int`, fără conversie.
        movie.setDuration(sbDuration.getProgress());

        // RATING: `float`, exact tipul câmpului.
        movie.setRating(rbRating.getRating());

        // SWITCH: `isChecked()` întoarce `boolean`.
        movie.setWatched(swWatched.isChecked());

        // BIFĂ: `isChecked()` întoarce `boolean`.
        movie.setOnWatchlist(cbonWatchList.isChecked());

        // POSTER: textul brut, fără validare de URL. Poate fi și gol.
        // Aici se vede a doua diferență de nume: `setPosterUrl`, nu `setPoster`.
        movie.setPosterUrl(etPoster.getText().toString());

        // GHIDAJUL: singurul câmp care nu are un getter direct pe widget.
        // `RadioGroup` nu are `getSelectedItem`; are doar `getCheckedRadioButtonId()`,
        //   care ar cere o căutare suplimentară. Bucla este mai simplă.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
            if(rb.isChecked())
            {
                // Textul butonului, nu ID-ul lui. Vezi câmpul 8 din `Movie.java`.
                movie.setApproval(rb.getText().toString());
                break;
            }
        }

        // INTENT DE REZULTAT — fără target.
        // `new Intent()` nu pornește nimic. Este doar un container pentru `setResult`.
        Intent intent = new Intent();

        // Filmul, sub aceeași cheie folosită de MainActivity la citire.
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);

        // POZIȚIA — DOAR în modul edit.
        // În modul insert, extra-ul lipsește, iar MainActivity citește `-1` ca implicit.
        // Astfel, absența poziției este chiar semnalul de „adaugă".
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);

        // Predă rezultatul. `RESULT_OK` este constanta moștenită din `Activity` (= -1).
        // Fără acest apel, MainActivity ar primi `RESULT_CANCELED` și ar ignora filmul.
        setResult(RESULT_OK, intent);

        // Închide activitatea. Fără `finish()`, formularul ar rămâne pe ecran,
        //   iar rezultatul ar fi livrat abia la apăsarea butonului Back.
        finish();
    }

    // ==================================================================================
    // showReleaseDatePicker — DIALOGUL DE DATĂ
    // ==================================================================================
    // CE FACE: deschide un `DatePickerDialog` poziționat pe data curentă din
    //   `releaseCal` și scrie rezultatul în calendar și în text.
    // CUM: 1. dacă textul există, încearcă să îl parseze în `releaseCal`
    //      2. deschide dialogul cu anul/luna/ziua din `releaseCal`
    //      3. la confirmare, scrie în `releaseCal` și formatează textul
    // RISC: `parse` poate arunca `ParseException`; este prinsă și IGNORATĂ.
    // REF: singurul loc din aplicație care folosește `DatePickerDialog`.
    // ==================================================================================
    private void showReleaseDatePicker() {

        // Textul curent din câmp. Poate fi gol (insert) sau o dată formatată (edit).
        String current = etRelease.getText().toString();

        // Dacă există text, încearcă să îl transformi în dată.
        if (!current.isEmpty()) {
            try {
                // `parse` întoarce `null` dacă textul nu poate fi interpretat complet.
                Date parsed = dateFormat.parse(current);
                if (parsed != null)
                    // Sincronizează calendarul cu textul. Acesta este SINGURUL loc
                    //   în care `releaseCal` primește data din formular — de aici BUG 4.
                    releaseCal.setTime(parsed);
            } catch (ParseException ignored) { }
            // `catch` gol, intenționat: un text invalid nu blochează dialogul.
            //   Calendarul rămâne pe valoarea anterioară, iar dialogul se deschide
            //   pe ea. Utilizatorul corectează din dialog.
        }

        // Construiește dialogul.
        // `this` = Context-ul (activitatea).
        // Al doilea argument este listener-ul de confirmare, ca clasă anonimă.
        // Următoarele trei sunt valorile inițiale: an, lună, zi.
        new DatePickerDialog(
                this,
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {

                        // `month` este deja 0-based, exact cum îl așteaptă `Calendar.set`.
                        //   NU se scade 1. Confuzia apare la `GregorianCalendar`, unde
                        //   constantele `Calendar.JULY` ascund aceeași convenție.
                        releaseCal.set(year, month, day);

                        // Șterge eventuala eroare afișată pe câmp. `setError(null)`
                        //   ascunde iconița și mesajul de sub `TextInputLayout`.
                        etRelease.setError(null);

                        // Scrie textul formatat. Aici `releaseCal` este deja actualizat,
                        //   deci textul și calendarul sunt sincronizate.
                        etRelease.setText(dateFormat.format(releaseCal.getTime()));
                    }
                },

                // Valorile inițiale ale roților dialogului: din calendar, nu din text.
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)

        // `show()` este obligatoriu. Constructorul creează dialogul, dar nu îl afișează.
        ).show();
    }
}
```

**Cele patru bug-uri reale, într-un singur loc:**

| # | Unde | Ce se întâmplă | Când se vede |
|---|---|---|---|
| 1 | `saveMovie` → `Double.parseDouble` | `NumberFormatException` pe câmp gol | primul „Save Movie" fără buget |
| 2 | `fillForm` → `dateFormat.format(null)` | `NullPointerException` | editarea unui `Movie` cu `release == null` |
| 3 | `fillForm` → `String.valueOf(double)` | „1.6E8" în loc de „160000000" | orice buget ≥ 10^7 |
| 4 | `fillForm` nu scrie în `releaseCal` | data filmului devine data de AZI | editare fără atingerea câmpului de dată |

**BUG 4, în detaliu** — este singurul care nu apare în capitolul 22, pentru că nici acolo nu a fost semnalat:

```
MOD EDIT, utilizatorul schimbă DOAR titlul:

  onCreate
    releaseCal = Calendar.getInstance()        -> data de AZI
    fillForm(existing)
      etRelease.setText("16/07/2010")          -> doar TEXTUL
      (releaseCal rămâne pe data de AZI)

  utilizatorul apasă "Update Movie"
    saveMovie()
      movie.setRelease(releaseCal.getTime())   -> data de AZI, nu 16/07/2010

  MainActivity
    movies.set(position, movie)                -> data originală este PIERDUTĂ
```

Dacă utilizatorul deschide dialogul de dată măcar o dată, `showReleaseDatePicker` parsează textul și repară calendarul. Bug-ul se manifestă doar când câmpul este lăsat neatins.

---
## 31.5 `AndroidManifest.xml` — harta aplicației

Al patrulea fișier și singurul care nu este nici cod, nici layout. Este **declarația** pe care sistemul o citește înainte să încarce o singură clasă.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ================================================================================== -->
<!-- FIȘIER: AndroidManifest.xml — DECLARAȚIA APLICAȚIEI                                 -->
<!-- ================================================================================== -->
<!-- CE ESTE: fișierul care spune sistemului de operare ce componente are aplicația,     -->
<!--   care dintre ele poate fi pornită din exterior și ce temă folosește.               -->
<!-- DE CE EXISTĂ: fără el, Android nu știe că `MainActivity` este punctul de pornire.   -->
<!-- CE NU FACE: nu conține cod, nu conține layout, nu declară permisiuni (aplicația     -->
<!--   nu are nevoie de niciuna).                                                        -->
<!-- CE S-AR RUPE FĂRĂ EL: aplicația nu ar apărea în launcher.                          -->
<!-- DIFERENȚA FAȚĂ DE G1097: doar `Theme.G1099` în loc de `Theme.G1097`.               -->
<!--   Numele pachetului nu apare aici: vine din `namespace`-ul din `build.gradle`.      -->
<!-- ================================================================================== -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- ============================================================================== -->
    <!-- ELEMENTUL APPLICATION — configurația globală a aplicației.                      -->
    <!-- ATRIBUTE, PE RÂND:                                                              -->
    <!--   allowBackup         = permite sistemului să copieze datele aplicației.        -->
    <!--   dataExtractionRules = regulile de backup pentru Android 12+.                  -->
    <!--   fullBackupContent   = regulile de backup pentru Android 11 și mai vechi.      -->
    <!--   icon / roundIcon    = iconițele din launcher; `mipmap` = mai multe densități. -->
    <!--   label               = numele aplicației, din `strings.xml`. Niciodată text    -->
    <!--                         literal aici.                                           -->
    <!--   supportsRtl         = suport pentru limbile scrise de la dreapta la stânga.   -->
    <!--   theme               = tema aplicației. Singura diferență față de G1097.       -->
    <!--                                                                                 -->
    <!-- `xmlns:tools` este declarat mai sus, dar în acest fișier NU este folosit:       -->
    <!--   niciun atribut `tools:` nu apare. Declarație moartă, ca importurile moarte.   -->
    <!-- ============================================================================== -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.G1099">

        <!-- ========================================================================== -->
        <!-- ACTIVITATEA 1: MainActivity — ecranul cu lista.                            -->
        <!-- `android:name` este RELATIV: `.activities.MainActivity` se compune cu      -->
        <!--   numele pachetului din `build.gradle`.                                    -->
        <!-- `android:exported="true"` este OBLIGATORIU din API 31 pentru orice         -->
        <!--   componentă cu intent-filter. Fără el, build-ul eșuează.                  -->
        <!-- `adjustResize`: când apare tastatura, fereastra se micșorează, iar         -->
        <!--   conținutul rămâne vizibil. Alternativa `adjustPan` ar împinge ecranul.   -->
        <!-- ========================================================================== -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!-- FILTRUL DE INTENȚII — ce face activitatea pornibilă din launcher. -->
            <intent-filter>
                <!-- `MAIN` = punctul de intrare al aplicației. -->
                <action android:name="android.intent.action.MAIN" />

                <!-- `LAUNCHER` = apare în lista de aplicații a telefonului. -->
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ========================================================================== -->
        <!-- ACTIVITATEA 2: ItemActivity — formularul.                                  -->
        <!-- `android:exported="false"`: NU poate fi pornită de altă aplicație.         -->
        <!--   Este corect: formularul se deschide doar din MainActivity, prin Intent.  -->
        <!-- Fără intent-filter, pentru că nu răspunde la nicio acțiune globală.        -->
        <!-- `adjustResize` din nou: formularul are câmpuri text, deci tastatura apare. -->
        <!-- ========================================================================== -->
        <activity
            android:name=".activities.ItemActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**Tabel de referință pentru manifest:**

| Atribut | Valoare | Efect | Obligatoriu? |
|---|---|---|---|
| `android:exported` pe `MainActivity` | `true` | poate fi pornită din launcher | **da**, din API 31 |
| `android:exported` pe `ItemActivity` | `false` | doar din aplicație | **da**, din API 31 |
| `android:windowSoftInputMode` | `adjustResize` | fereastra se micșorează la tastatură | nu, dar recomandat |
| `android:theme` | `@style/Theme.G1099` | tema Material 3 | nu, dar fără ea arată implicit |
| `android:allowBackup` | `true` | backup automat | nu |
| `android:supportsRtl` | `true` | layout oglindit în RTL | nu |

---

## 31.6 `activity_main.xml` — ecranul listei

Al cincilea fișier. Douăzeci și șase de linii, doi copii. Este cel mai simplu layout din aplicație și, totuși, conține o capcană.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ================================================================================== -->
<!-- FIȘIER: activity_main.xml — ECRANUL CU LISTA                                        -->
<!-- ================================================================================== -->
<!-- CE ESTE: un FrameLayout cu exact doi copii: ListView (umple tot) și FAB (peste el). -->
<!-- DE CE ATÂT DE PUȚIN: toată complexitatea este în `activity_item.xml` (formularul).  -->
<!--   Aici doar scheletul.                                                              -->
<!-- STRUCTURA:                                                                          -->
<!--                                                                                     -->
<!--   FrameLayout (id=main)                                                             -->
<!--   |== ListView (id=listView)          -> primul copil = desenat primul = dedesubt   -->
<!--   +== FloatingActionButton (id=...)   -> al doilea copil = desenat peste listă      -->
<!--                                                                                     -->
<!-- ORDINEA COPIILOR ESTE SEMNIFICAȚIE, NU STIL: în FrameLayout, fiecare copil este      -->
<!--   desenat peste cel anterior. Inversate, lista ar acoperi butonul.                  -->
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
    <!-- LISTVIEW — lista derulantă.                                                    -->
    <!-- `android:id="@+id/listView"` -> căutat în `initControls`.                      -->
    <!-- `match_parent` pe ambele axe: lista ocupă tot ecranul, inclusiv zona de sub    -->
    <!--   FAB. Butonul este desenat PESTE listă, nu listă pe lângă el.                 -->
    <!-- `android:entries="@array/items"` -> umple lista din XML cu elementele din      -->
    <!--   array-ul de demonstrație. LA RUNTIME, `listView.setAdapter(movieAdapter)`    -->
    <!--   ÎNLOCUIEȘTE complet acest adapter. `entries` rămâne doar pentru preview.     -->
    <!--   Costul la runtime este zero după `setAdapter`.                               -->
    <!-- ============================================================================== -->
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />

    <!-- ============================================================================== -->
    <!-- FLOATING ACTION BUTTON — butonul „+".                                          -->
    <!-- Numele complet este necesar: este o clasă din biblioteca Material, nu din      -->
    <!--   framework. Prefixul `com.google.android.material...` este calea clasei.      -->
    <!-- `wrap_content` pe ambele axe: FAB-ul are dimensiune fixă din stil (56dp).      -->
    <!--   `match_parent` l-ar întinde pe tot ecranul.                                  -->
    <!-- `android:layout_gravity="bottom|end"` = poziția ACESTUI COPIL în părintele lui. -->
    <!--   `end` respectă direcția de citire: în RTL devine stânga.                     -->
    <!-- `android:layout_margin="16dp"` = 16dp față de marginea zonei de conținut.       -->
    <!-- `android:contentDescription="Add"` = textul citit de TalkBack. Text literal,   -->
    <!--   deci lint-ul dă avertisment (ar trebui `@string/...`).                       -->
    <!-- `app:srcCompat` = varianta compatibilă pentru imagini vectoriale.              -->
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

**Capcana fișierului:** `android:orientation="horizontal"` pe un `FrameLayout`. Atributul **nu există** pe `FrameLayout` — există doar pe `LinearLayout`. Android îl ignoră la runtime și emite un avertisment de lint („Unknown attribute"). Este o rămășiță de la un `LinearLayout` anterior, păstrată de la o versiune la alta. Nu strică nimic, dar arată că fișierul a fost editat.

**`layout_gravity` vs `gravity`:**

```
gravity         = cum își aranjează ELEMENTUL copiii lui în interior
layout_gravity  = cum este aranjat ELEMENTUL în părintele lui

TextView cu gravity="center"         -> textul este centrat în TextView
TextView cu layout_gravity="center"  -> TextView-ul este centrat în părinte
```

---

## 31.7 `activity_item.xml` — formularul

Al șaselea și ultimul fișier. Patru sute cincizeci și două de linii, patru carduri, 26 de id-uri. Este layout-ul care produce toate cele 10 valori ale modelului.

### 31.7.1 Trei reguli care se aplică în tot fișierul

**1. `?attr/` vs `@color/` vs `#RRGGBB`**

| Formă | Când se rezolvă | Se schimbă cu tema? | Când se folosește |
|---|---|---|---|
| `?attr/colorPrimary` | la runtime, din tema curentă | **da** | orice culoare semantică |
| `@color/my_color` | la build, din `colors.xml` | nu | culori fixe ale brandului |
| `#FFC107` | la build, literal | nu | excepții asumate (stelele) |

Diferența esențială: `?attr/` este un **rol**, `@color/` este o **valoare**. `?attr/colorPrimary` înseamnă „culoarea primară a temei" și devine altă nuanță în dark mode. `#FFC107` rămâne chihlimbar în ambele teme.

**2. `0dp` + `layout_weight`**

```
LinearLayout orizontal, lățime totală 360dp

  +-----------------------------+------------+
  | TextView                    | TextView   |
  | layout_width="0dp"          | wrap_content
  | layout_weight="1"           |            |
  +-----------------------------+------------+
  |<------ tot spațiul rămas --------------->|

  `0dp` + weight = „ia tot spațiul rămas după ce ceilalți copii și-au luat partea".
  `wrap_content` + weight = „ia mărimea ta naturală, apoi împarte restul".
```

**3. `tools:` nu ajunge în APK**

`tools:text`, `tools:rating` și `tools:progress` există **doar** în preview-ul Android Studio. Sunt eliminate la build. Le poți folosi ca să vezi formularul plin fără să scrii cod.

### 31.7.2 Fișierul adnotat

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ================================================================================== -->
<!-- FIȘIER: activity_item.xml — FORMULARUL DE INSERT ȘI EDIT                            -->
<!-- ================================================================================== -->
<!-- CE ESTE: un ScrollView cu un singur copil LinearLayout vertical, care conține       -->
<!--   patru MaterialCardView-uri (Basics, Production, Your verdict, Poster) și butonul  -->
<!--   de salvare. 26 de id-uri, dintre care 13 sunt căutate în cod.                      -->
<!-- DE CE EXISTĂ: este singurul layout care colectează date de la utilizator.           -->
<!-- CE NU FACE: nu validează nimic. Un câmp gol este perfect valid pentru XML.          -->
<!-- CE S-AR RUPE FĂRĂ EL: `ItemActivity` ar apela `setContentView` pe o resursă         -->
<!--   inexistentă și ar crăpa la pornire.                                               -->
<!-- DIFERENȚA FAȚĂ DE G1097: niciuna. Fișierul este identic.                            -->
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
    <!-- SCROLLVIEW — rădăcina.                                                          -->
    <!-- `android:id="@+id/main"` -> folosit de listener-ul de insets din `onCreate`.    -->
    <!-- DE CE ScrollView: formularul este mai înalt decât ecranul, mai ales cu           -->
    <!--   tastatura deschisă.                                                           -->
    <!-- REGULA: ScrollView are EXACT UN copil. Doi copii ar arunca                     -->
    <!--   `IllegalStateException` la inflate.                                           -->
    <!-- `android:fillViewport="true"`: dacă unicul copil este mai scund decât ecranul,  -->
    <!--   este întins să umple viewport-ul. Fără el, fundalul rămâne gol dedesubt.      -->
    <!-- `android:background="?attr/colorSurface"` = culoarea de suprafață a temei.      -->
    <!-- ============================================================================== -->

    <!-- ============================================================================== -->
    <!-- CONTAINERUL VERTICAL — unicul copil al ScrollView-ului.                         -->
    <!-- `wrap_content` pe înălțime: crește cât conținutul, ca ScrollView-ul să aibă     -->
    <!--   ce derula.                                                                    -->
    <!-- `paddingHorizontal` și `paddingTop/Bottom` = 16dp lateral, 24dp sus/jos.        -->
    <!--   `paddingHorizontal` este API 26+; pe versiuni mai vechi este ignorat.         -->
    <!-- ============================================================================== -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- Header -->
        <!-- TITLUL ECRANULUI, ca text în layout. Nu este `setTitle` — este un TextView. -->
        <!-- `textAppearanceHeadlineMedium` = scara tipografică Material 3.              -->
        <!-- `?attr/colorOnSurface` = culoarea de text potrivită pentru suprafață.       -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Movie details"
            android:textAppearance="?attr/textAppearanceHeadlineMedium"
            android:textColor="?attr/colorOnSurface"
            android:textStyle="bold" />

        <!-- SUBTITLUL. `colorOnSurfaceVariant` = text secundar, mai șters.              -->
        <!-- `layout_marginBottom="20dp"` = spațiu până la primul card.                  -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="20dp"
            android:text="Fill in the information below and save."
            android:textAppearance="?attr/textAppearanceBodyMedium"
            android:textColor="?attr/colorOnSurfaceVariant" />

        <!-- ============ CARD 1: Basics ============ -->
        <!-- CARDUL 1 — titlul, genul și data.                                           -->
        <!-- `?attr/materialCardViewFilledStyle` = stilul Material 3 de card umplut.     -->
        <!-- `cardCornerRadius="20dp"` = colțuri rotunjite, peste valoarea din stil.     -->
        <!-- `layout_marginBottom="16dp"` = spațiu între carduri.                        -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <!-- CONȚINUTUL CARDULUI. `padding="16dp"` pe toate laturile.                 -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!-- TITLUL SECȚIUNII. `colorPrimary` = accentul temei.                  -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Basics"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Title -->
                <!-- ETICHETA CÂMPULUI. `tvTile` este o GREȘEALĂ DE TIPAR („Tile" în     -->
                <!--   loc de „Title"), dar este inofensivă: id-ul nu este folosit        -->
                <!--   nicăieri în cod. Un id cu typo nu strică nimic atâta timp cât      -->
                <!--   nimeni nu îl caută.                                                -->
                <TextView
                    android:id="@+id/tvTile"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Title"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- CÂMPUL DE TITLU — TextInputLayout + TextInputEditText.               -->
                <!-- `OutlinedBox` = stilul cu contur.                                    -->
                <!-- `app:hintEnabled="false"` = fără etichetă flotantă, pentru că         -->
                <!--   eticheta există deja ca TextView deasupra.                         -->
                <!-- `app:endIconMode="clear_text"` = butonul „X" de golire, la focus.    -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text">

                    <!-- `etTitle` — sursa lui `movie.setTitle(...)`.                      -->
                    <!-- `inputType="textCapWords"` = tastatura scrie cu majusculă la     -->
                    <!--   începutul fiecărui cuvânt.                                     -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Movie title"
                        android:inputType="textCapWords" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- Genre -->
                <!-- ETICHETA GENULUI. `tvGenre` nu este folosit în cod.                  -->
                <TextView
                    android:id="@+id/tvGenre"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Genre"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- SPINNER-UL, ÎNVELIT ÎNTR-UN CARD.                                    -->
                <!-- DE CE învelit: Spinner-ul nu are contur propriu. Cardul îi dă        -->
                <!--   aspectul de câmp, ca să se potrivească cu TextInputLayout-urile.   -->
                <!-- `cardBackgroundColor="@android:color/transparent"` = fără umplere.   -->
                <!-- `strokeColor="?attr/colorOutline"` = conturul.                       -->
                <!-- `layout_height="56dp"` = înălțimea standard a unui câmp Material.    -->
                <com.google.android.material.card.MaterialCardView
                    style="?attr/materialCardViewOutlinedStyle"
                    android:layout_width="match_parent"
                    android:layout_height="56dp"
                    android:layout_marginBottom="16dp"
                    app:cardBackgroundColor="@android:color/transparent"
                    app:cardCornerRadius="4dp"
                    app:strokeColor="?attr/colorOutline">

                    <!-- `spGenre` — sursa lui `movie.setGenre(...)`.                      -->
                    <!-- `android:entries="@array/movie_genre"` = valorile vin din XML,   -->
                    <!--   nu din cod. Adăugarea unui gen = o linie în arrays.xml.        -->
                    <!-- `spinnerMode="dropdown"` = listă derulantă, nu dialog.           -->
                    <Spinner
                        android:id="@+id/spGenre"
                        android:layout_width="match_parent"
                        android:layout_height="match_parent"
                        android:entries="@array/movie_genre"
                        android:paddingStart="4dp"
                        android:spinnerMode="dropdown" />
                </com.google.android.material.card.MaterialCardView>

                <!-- Release date -->
                <!-- CÂMPUL DE DATĂ.                                                      -->
                <!-- `hintEnabled="true"` AICI, spre deosebire de titlu: eticheta          -->
                <!--   „Release date" este hint-ul flotant, nu un TextView separat.       -->
                <!-- `startIconDrawable` = iconița de calendar din framework.             -->
                <!-- ATENȚIE: câmpul este EDITABIL, dar click-ul este interceptat de      -->
                <!--   `etRelease.setOnClickListener` și înlocuit cu un dialog.           -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="true"
                    app:startIconContentDescription="Release date"
                    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

                    <!-- `etRelease` — doar AFIȘARE. Sursa de adevăr este `releaseCal`.   -->
                    <!-- `inputType="date"` = tastatură numerică cu separatori.           -->
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
        <!-- CARDUL 2 — bugetul și durata.                                               -->
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
                    android:text="Production"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Budget -->
                <!-- ETICHETA BUGETULUI. `tvBudget` nu este folosit în cod.               -->
                <TextView
                    android:id="@+id/tvBudget"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Budget"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- CÂMPUL DE BUGET.                                                     -->
                <!-- `app:prefixText="$ "` = prefixul afișat în câmp, nu în text.         -->
                <!-- `inputType="numberDecimal"` = tastatură numerică cu virgulă.         -->
                <!-- RISC: tastatura permite și câmp gol. `Double.parseDouble("")`        -->
                <!--   aruncă `NumberFormatException` — BUG 1 din 31.4.                   -->
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
                <!-- RÂNDUL CU ETICHETA ȘI VALOAREA DURATEI.                              -->
                <!-- `layout_weight="1"` pe etichetă = împinge valoarea în dreapta.       -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">

                    <!-- `tvDuration` — etichetă fixă, nefolosită în cod.                 -->
                    <TextView
                        android:id="@+id/tvDuration"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Duration"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!-- `tvDurationValue` — SINGURUL TextView de aici care este        -->
                    <!--   căutat în cod. Este actualizat de listener-ul SeekBar-ului.  -->
                    <!-- `tools:text="148 min"` = valoare doar pentru preview.          -->
                    <TextView
                        android:id="@+id/tvDurationValue"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorPrimary"
                        tools:text="148 min" />
                </LinearLayout>

                <!-- SEEKBAR-UL DE DURATĂ.                                                -->
                <!-- `android:max="300"` = valoarea maximă. `android:min="0"` = minima.   -->
                <!--   `android:min` este API 26+; pe versiuni mai vechi este ignorat.    -->
                <!-- `progressTint` și `thumbTint` = culoarea barei și a mânerului.       -->
                <!-- `tools:progress="148"` = poziția în preview.                         -->
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

                <!-- LEGENDA BAREI: „0 min" în stânga, „300 min" în dreapta.              -->
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
        <!-- CARDUL 3 — rating, switch, bifă și ghidaj parental.                         -->
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
                <!-- ETICHETA RATING-ULUI. `tvRating` nu este folosit în cod.             -->
                <TextView
                    android:id="@+id/tvRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Rating"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- RATINGBAR — widget-ul de stele.                                      -->
                <!-- `numStars="5"` = 5 stele. `stepSize="0.5"` = jumătăți de stea.       -->
                <!-- `#FFC107` = chihlimbar, singura culoare literală din fișier.         -->
                <!-- `progressBackgroundTint` = culoarea stelelor neumplute.              -->
                <!-- ATENȚIE: acesta este `android.widget.RatingBar`, NU                  -->
                <!--   `android.media.Rating` din importul mort. Vezi 31.0.5.             -->
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

                <!-- LINIE DE SEPARARE. `1dp` înălțime, culoare de contur.                -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Recommended -->
                <!-- RÂNDUL CU SWITCH ȘI BIFĂ. `minHeight="48dp"` = ținta minimă de       -->
                <!--   atingere recomandată de Material.                                  -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:minHeight="48dp"
                    android:orientation="horizontal">

                    <!-- COLOANA DE TEXT, cu `weight="1"` ca să împingă controalele       -->
                    <!--   în dreapta.                                                    -->
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">

                        <!-- `tvWatched` — etichetă fixă „Recommended".                   -->
                        <TextView
                            android:id="@+id/tvWatched"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Recommended"
                            android:textAppearance="?attr/textAppearanceBodyLarge"
                            android:textColor="?attr/colorOnSurface" />

                        <!-- `tvWatchedValue` — eticheta dinamică „Yes"/„No",             -->
                        <!--   actualizată de listener-ul switch-ului.                    -->
                        <TextView
                            android:id="@+id/tvWatchedValue"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="No"
                            android:textAppearance="?attr/textAppearanceLabelLarge"
                            android:textColor="?attr/colorPrimary" />
                    </LinearLayout>

                    <!-- MATERIALSWITCH — widget-ul „Recommended".                        -->
                    <!-- Numele complet este obligatoriu: clasa este din biblioteca       -->
                    <!--   Material, nu din framework. De aceea importul                   -->
                    <!--   `android.widget.Switch` este mort. Vezi 31.0.6.                -->
                    <com.google.android.material.materialswitch.MaterialSwitch
                        android:id="@+id/swWatched"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="12dp" />

                    <!-- MATERIALCHECKBOX — bifa „Watchlist".                             -->
                    <!-- ID-ul este `cbOnWatchList`, câmpul Java este `cbonWatchList`.    -->
                    <!--   Diferă printr-o singură majusculă.                             -->
                    <com.google.android.material.checkbox.MaterialCheckBox
                        android:id="@+id/cbOnWatchList"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Watchlist" />
                </LinearLayout>

                <!-- A doua linie de separare. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Guidance -->
                <!-- ETICHETA GHIDAJULUI. `tvGuidance` nu este folosit în cod.            -->
                <TextView
                    android:id="@+id/tvGuidance"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Guidance"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- HORIZONTAL SCROLL: cele 5 butoane radio nu încap pe un ecran       -->
                <!--   îngust, deci pot fi trase lateral. `scrollbars="none"` = fără    -->
                <!--   indicator vizibil.                                               -->
                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none">

                    <!-- RADIOGROUP — containerul care garantează selecția UNICĂ.         -->
                    <!-- `orientation="horizontal"` = butoanele stau pe un rând.          -->
                    <!-- Codul iterează `getChildAt(index)` și citește `getText()`.       -->
                    <RadioGroup
                        android:id="@+id/rgApproval"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <!-- `android:checked="true"` = „G" este selectat implicit.       -->
                        <!--   De aceea `saveMovie` găsește mereu un buton bifat.         -->
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

        <!-- ============ CARD 4: Poster ============ -->
        <!-- CARDUL 4 — URL-ul posterului.                                            -->
        <!-- `layout_marginBottom="24dp"` = ultimul card, spațiu mai mare până la buton. -->
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

                <!-- CÂMPUL DE POSTER.                                                    -->
                <!-- `inputType="textUri"` = tastatură cu `/` și `.com`.                  -->
                <!-- `startIconDrawable` = iconița de galerie din framework.              -->
                <!-- `etPoster` — sursa lui `movie.setPosterUrl(...)`.                    -->
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
        <!-- BUTONUL DE SALVARE.                                                          -->
        <!-- `layout_height="60dp"` = mai înalt decât standardul, ca acțiune principală.  -->
        <!-- `app:cornerRadius="30dp"` = colțuri complet rotunjite (jumătate din 60).      -->
        <!-- `app:icon` + `app:iconGravity="textStart"` = iconiță înaintea textului.      -->
        <!-- Textul este schimbat din cod în modul edit: „Update Movie".                  -->
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

**Tabel de referință pentru cele 13 view-uri cu id:**

| # | id în XML | Tip | Câmp Java | Rol |
|---|---|---|---|---|
| 1 | `etTitle` | `TextInputEditText` | `etTitle` | `setTitle` / `getTitle` |
| 2 | `etRelease` | `TextInputEditText` | `etRelease` | afișare dată |
| 3 | `spGenre` | `Spinner` | `spGenre` | `setGenre` |
| 4 | `etBudget` | `TextInputEditText` | `etBudget` | `setBudget` |
| 5 | `sbDuration` | `SeekBar` | `sbDuration` | `setDuration` |
| 6 | `rbRating` | `RatingBar` | `rbRating` | `setRating` |
| 7 | `rgApproval` | `RadioGroup` | `rgApproval` | `setApproval` |
| 8 | `cbOnWatchList` | `MaterialCheckBox` | `cbonWatchList` | `setOnWatchlist` |
| 9 | `swWatched` | `MaterialSwitch` | `swWatched` | `setWatched` |
| 10 | `etPoster` | `TextInputEditText` | `etPoster` | `setPosterUrl` |
| 11 | `btnMovieAction` | `MaterialButton` | `btMovieAction` | declanșează `saveMovie` |
| 12 | `tvDurationValue` | `TextView` | `tvDurationValue` | etichetă dinamică |
| 13 | `tvWatchedValue` | `TextView` | `tvWatchedValue` | etichetă dinamică |

**Cele șapte etichete fixe care nu sunt căutate în cod:** `tvTile`, `tvGenre`, `tvBudget`, `tvDuration`, `tvRating`, `tvWatched`, `tvGuidance`. Sunt etichete fixe. Au id pentru că așa le-a generat Android Studio, dar nimeni nu le caută. Nici cele cinci butoane radio nu sunt căutate după id: `fillForm` și `saveMovie` le parcurg cu `getChildAt(index)`.

---

## 31.8 Fluxul complet

Patru diagrame. Fiecare urmărește un singur fir, de la eveniment până la pixel.

### 31.8.1 Pornirea aplicației

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

  OBSERVAȚIE: posterul NU apare în niciun rând. `toString()` nu îl include.
```

### 31.8.2 Insert — FAB

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
    |== movie = (Movie) getSerializableExtra(MOVIE_EXTRA)   <- O COPIE
    |== position = getIntExtra(POSITION_EXTRA, -1)           -> -1
    |== movies.add(movie)
    +== movieAdapter.notifyDataSetChanged()
          |
          v
  ListView redesenează -> al 4-lea rând apare
```

### 31.8.3 Edit — click pe rând

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
    |     |     |   (releaseCal NU se actualizează -> BUG 4)
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

### 31.8.4 Obiectul care călătorește

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

**Consecința practică:** modificarea formularului nu se vede în listă până la `movies.set(...)`. Nu există nicio „legătură" între obiectul din listă și cel din formular — sunt două obiecte distincte, cu adrese distincte.

### 31.8.5 Ciclul de viață — ce se întâmplă cu starea

```
MainActivity                          ItemActivity
------------                          ------------

onCreate
onStart
onResume   <-- ecranul este vizibil
   |
   |  launcher.launch(...)
   v
onPause    ------------------------>  onCreate
                                      onStart
                                      onResume   <-- formularul este vizibil
                                         |
                                         |  saveMovie() -> setResult -> finish()
                                         v
onResume   <-- callback-ul rulează  onPause
   |                                onStop
   |                                onDestroy
   v
(ecranul de listă, actualizat)

DACĂ UTILIZATORUL APASĂ BACK ÎN FORMULAR:
  ItemActivity: onPause -> onStop -> onDestroy
  MainActivity: onResume
  callback-ul NU rulează cu RESULT_OK -> lista rămâne neschimbată

DACĂ SISTEMUL UCIDE PROCESUL ÎN TIMP CE FORMULARUL ESTE DESCHIS:
  starea formularului se pierde, pentru că nu este salvată în `onSaveInstanceState`
  `movies` se pierde și ea, pentru că nu este persistentă
  (aplicația didactică nu are `SharedPreferences`, bază de date sau fișier)
```

### 31.8.6 Reciclarea rândurilor în ListView

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

## 31.9 Ce să reții din fiecare fișier

| Fișier | Esența | Capcana |
|---|---|---|
| `Movie.java` | POJO serializabil, 10 câmpuri, constructor gol explicit, `isX()` pentru booleeni, `toString()` = contract de afișare | constructorul cu 10 parametri este POZIȚIONAL; posterul lipsește din `toString()` |
| `MainActivity.java` | ordinea din `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` | `launcher` este atribuit DUPĂ `initListeners`; două importuri moarte |
| `ItemActivity.java` | 13 `findViewById`, `releaseCal` ca sursă de adevăr, buclă generică pe `RadioGroup`, `setResult` + `finish` | buget gol -> crash; dată null -> crash; `releaseCal` nesincronizat în edit; trei importuri moarte |
| `AndroidManifest.xml` | două activități, `exported`, `windowSoftInputMode`, tema | `android:exported` este obligatoriu din API 31 |
| `activity_main.xml` | `FrameLayout` + ordinea copiilor + `layout_gravity` pe FAB | `android:orientation` este invalid pe FrameLayout |
| `activity_item.xml` | `ScrollView` cu un copil, `MaterialCardView` ca secțiune, `TextInputLayout`, `Spinner` învelit | `hintEnabled` trebuie corelat cu existența etichetei; 7 etichete fixe nefolosite |

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
10. **Ce importuri sunt moarte în G1099?** `Toast` și `Date` în `MainActivity`; `Rating`, `Switch` și `Snackbar` în `ItemActivity`.

### Diferențele care pot fi întrebări

| Întrebare posibilă | Răspuns scurt |
|---|---|
| Ce tip are câmpul pentru poster în G1099? | `String posterUrl`, fără `= null` |
| Cum se numește getter-ul posterului? | `getPosterUrl()` — nu `getPoster()` |
| Apare posterul în listă? | Nu — `toString()` nu îl include |
| Unde este constructorul fără parametri? | Primul, la linia 18, înaintea celui cu parametri |
| Ce este `android.media.Rating`? | O clasă de rating media, API 21+, nefolosită aici |
| Ce widget produce rating-ul? | `RatingBar`, din `android.widget` |
| Există `movie_item.xml`? | Nu, în G1099 nu există |

---

## Rezumat capitol 31

- Modelul nu atinge UI-ul; activitățile nu conțin logică de rând.
- `onCreate`: `super` -> `EdgeToEdge` -> `setContentView` -> insets -> date -> adapter -> controls -> listeners -> launcher.
- `releaseCal` este sursa de adevăr pentru dată, nu textul din `EditText`.
- Bucla pe `RadioGroup` face codul generic — adaugi butoane în XML, codul le vede.
- `setResult(RESULT_OK, intent)` + `finish()` este perechea obligatorie.
- `notifyDataSetChanged()` după orice modificare a listei.
- Posterul există în model, are getter și setter, dar nu apare în `toString()` și nu are `= null`.
- `android.media.Rating` este un import mort care arată ca `RatingBar` — cea mai bună capcană de citire din capitol.
- Patru bug-uri reale: buget gol, `release` null, notație științifică, `releaseCal` nesincronizat la editare.
- G1099 are șase fișiere, nu șapte: `movie_item.xml` lipsește.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [prezentarea generală](index.html).
