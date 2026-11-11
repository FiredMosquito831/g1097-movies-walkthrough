# Capitolul 30 — Codul G1098 adnotat

**Obiectiv:** să citești fiecare linie a aplicației G1098 cu explicația lipită de ea — ce face, de ce e acolo, ce se rupe dacă o scoți.

**Timp estimat:** 90–120 min (citire activă, cu proiectul deschis în paralel).

**Sursa:** `cod-final`, commitul `d719ffc` — `Movie.java`, `MainActivity.java`, `ItemActivity.java`, `AndroidManifest.xml`, `activity_main.xml`, `activity_item.xml`.

**Regulă:** codul este **nemodificat, byte cu byte**. Tot ce apare cu `//` sau `<!-- -->` în plus față de sursă este adnotare.

---

## 30.0 Ce diferă față de G1097

Aplicația G1098 este **funcțional identică** cu G1097: aceeași listă, același formular, același flux prin `Intent`. Diferențele sunt de nume, de ordine și de igienă a importurilor. Sunt exact genul de diferență care apare la examen când ți se cere să explici de ce două rezolvări care fac același lucru arată diferit.

| Aspect | G1098 | G1097 (referință) |
|---|---|---|
| Câmpul pentru poster în `Movie.java` | `private String posterUrl;` | `private String poster = null;` |
| Inițializator de câmp | niciunul | `= null` |
| Poziția constructorului fără parametri | **după `toString()`**, înaintea getterilor (linia 47) | ultimul, după setteri (linia 127) |
| `toString()` include posterul? | **DA** — `posterUrl` | da, dar ca `poster` |
| `MainActivity.java` — importuri nefolosite | doar `android.widget.Toast` | `java.util.Date` și `android.widget.Toast` |
| `MainActivity.java` — importă `BigDecimal` sau `Date`? | **niciunul** — cel mai curat import din toate grupele | `Date` (nefolosit) |
| `ItemActivity.java` — importuri nefolosite | **niciunul** | `Switch`, `Toast`, `Snackbar`, `ActivityItemBinding` |
| `ItemActivity.java` — importă `Switch`/`Toast`/`Snackbar`/`ActivityItemBinding`? | **niciunul** | toate patru (toate nefolosite) |
| `activity_main.xml` | FAB-ul folosește `@drawable/outline_add_2_24` | `@drawable/outline_add_24` |
| `activity_item.xml` | identic cu G1097 | — |
| `AndroidManifest.xml` | identic cu G1097 (diferă doar tema: `Theme.G1098`) | `Theme.G1097` |
| `movie_item.xml` | **nu există** | există (pregătit pentru S07, nefolosit de niciun cod) |

### 30.0.1 Câmpul se numește `posterUrl`, nu `poster`

Ambele grupe au în `Movie` un al zecelea câmp de tip `String`, pe aceeași poziție în constructorul cu 10 parametri, cu același rol: adresa afișului filmului. Diferă doar numele.

Numele nu rămâne însă în `Movie.java`. El se propagă în **patru** locuri:

```
Movie.java                          ItemActivity.java
-----------                         ------------------
private String posterUrl;           existing.getPosterUrl()      <- fillForm
public String getPosterUrl()        movie.setPosterUrl(...)      <- saveMovie
public void setPosterUrl(...)
```

**De ce contează:** dacă lipești o linie din codul G1097 într-un fișier G1098, nu compila. `existing.getPoster()` nu există pe un `Movie` G1098, iar `movie.setPoster(...)` la fel. Compilatorul te prinde imediat — și asta este exact ce vrei de la o redenumire.

**Ce înveți:** o redenumire de câmp este un refactor pe care compilatorul îl verifică în toate locurile. De aceea redenumirea se face cu `Shift+F6` (Rename) în Android Studio, nu cu căutare și înlocuire: unealta schimbă și getter-ul, și setter-ul, și toate apelurile.

### 30.0.2 Lipsește inițializatorul `= null`

G1098 scrie `private String posterUrl;`. G1097 scrie `private String poster = null;`.

**La runtime, cele două sunt identice.** În Java, orice câmp de tip referință care nu este inițializat primește automat `null` la construcția obiectului. Nu există „valoare nedefinită" ca în C++.

**De ce contează totuși:** `= null` este **documentație**. Îi spune cititorului: „acest câmp poate lipsi; un film fără poster este valid". Forma fără inițializator nu spune nimic — cititorul trebuie să deducă singur dacă `null` este permis sau este o scăpare.

**RISC:** ambele variante ajung la `null`. Dacă apelezi `.length()` sau `.isEmpty()` pe valoare înainte ca ea să fie setată, iei `NullPointerException`. În aplicație nu se întâmplă: `fillForm` face `etPoster.setText(existing.getPosterUrl())`, iar `setText(null)` este legal și afișează câmp gol.

**Ce înveți:** inițializarea explicită la valoarea implicită este un comentariu, nu un comportament. Nu confunda cele două când citești cod.

### 30.0.3 Constructorul fără parametri stă după `toString()`

În G1098, ordinea membrilor este:

```
linia  6   class Movie
linia  7   cele 10 câmpuri
linia 18   Movie(10 parametri)
linia 32   toString()
linia 47   Movie()                 <- constructorul gol
linia 50   getTitle() ... setPosterUrl()
```

În G1097, `Movie()` este **ultima** metodă din clasă, după cele 20 de getter-e și setter-e.

**Compilatorul nu are nicio preferință.** Ordinea membrilor într-o clasă Java este liberă. Runtime-ul este identic.

**De ce contează pentru cititor:** în G1098 vezi **amândouă** felurile de a crea un `Movie` unul lângă altul — constructorul cu 10 parametri și cel gol — înainte să intri în cele 20 de metode mecanice. În G1097 trebuie să derulezi peste 20 de metode ca să găsești constructorul gol.

**Ce înveți:** ordinea membrilor este un contract de citire. Convenția sănătoasă: câmpuri, constructori, metodă de afișare, restul. G1098 o respectă mai bine decât G1097, deși ambele compilează.

### 30.0.4 `toString()` include posterul

G1098 tipărește `posterUrl='...'`. G1096 și G1099 **omit** posterul complet. G1097 îl tipărește, dar cu numele `poster`. Așadar, dintre cele patru grupe, doar G1097 și G1098 au un `toString()` complet; G1098 este singura care îl numește `posterUrl`.

**De ce contează:** `ArrayAdapter` cu `android.R.layout.simple_list_item_1` umple rândul cu `item.toString()`. Deci URL-ul posterului **apare pe ecran**, în listă. Pentru un URL de 60 de caractere, rândul devine lung și urât — dar titlul și ratingul sunt la început, deci informația utilă rămâne vizibilă.

**De ce merită totuși:** `toString()` este unealta ta de depanare. `Log.d("MOVIE", movie.toString())` îți arată toate cele 10 câmpuri. Un `toString()` incomplet ascunde exact câmpul pe care îl cauți — și atunci pierzi zece minute crezând că valoarea nu s-a setat.

**RISC:** dacă posterul este `null`, rândul conține `posterUrl='null'` — un text, nu o eroare. Confuzia apare când crezi că ai salvat string-ul `"null"`.

**Ce înveți:** `toString()` este un contract de diagnostic. Completitudinea bate frumusețea.

### 30.0.5 `MainActivity` are un singur import mort

G1098 importă `android.widget.Toast` și nu îl folosește niciodată. G1097 are două importuri moarte: `java.util.Date` și `android.widget.Toast`.

**De ce contează:** un import nu ajunge în bytecode. Este o instrucțiune pentru compilator, rezolvată la compilare și apoi dispărută. Nu crește APK-ul, nu încarcă nimic la runtime, nu costă nicio milisecundă.

Costul este **uman**: importul sugerează o dependență care nu există. Cine citește fișierul se întreabă „unde se afișează Toast-ul?" și pierde timp căutând.

**Ce înveți:** un import este o afirmație. O afirmație falsă costă timp de citire, chiar dacă nu costă nimic la runtime.

### 30.0.6 `MainActivity` nu importă nici `BigDecimal`, nici `Date`

G1098 este cea mai curată din toate grupele la capitolul importuri: în afara lui `Toast`, fiecare import este folosit.

**De ce nu are nevoie de `Date`:** datele celor trei filme demo se construiesc așa:

```
new GregorianCalendar(2010, Calendar.JULY, 16).getTime()
```

`getTime()` întoarce un `Date`, dar acel `Date` este **consumat direct** ca argument în constructorul lui `Movie`. Tipul nu este scris nicăieri în fișier, deci nu este nevoie de import. Un import se face pentru un **nume** folosit în cod, nu pentru un tip care trece printr-o expresie.

**De ce nu are nevoie de `BigDecimal`:** bugetul este un `double`, scris ca literal (`160000000`). `BigDecimal` ar apărea doar dacă ai scrie `new BigDecimal("160000000")`.

**Ce înveți:** importurile urmăresc identificatorii scriși efectiv în fișier. „Tipul ăsta apare undeva în lanțul de apeluri" nu este un motiv de import.

### 30.0.7 `ItemActivity` nu are niciun import mort

G1098: toate cele 30 de importuri sunt folosite. G1097: patru importuri moarte — `android.widget.Switch`, `android.widget.Toast`, `com.google.android.material.snackbar.Snackbar` și `ActivityItemBinding`.

**De ce `Switch` este mort peste tot:** toate cele patru grupe declară în `ItemActivity`:

```
private MaterialSwitch swWatched;
```

`MaterialSwitch` este `com.google.android.material.materialswitch.MaterialSwitch`, nu `android.widget.Switch`. Cine importă `android.widget.Switch` și apoi declară `MaterialSwitch` are un import care nu corespunde niciunui nume din fișier. Este capcana clasică de examen: numele seamănă, clasele sunt diferite.

**De ce `ActivityItemBinding` este mort:** este clasa generată de ViewBinding pentru `activity_item.xml`. Ea există în build, dar G1097 nu o folosește în `ItemActivity` — fișierul lucrează cu `findViewById`.

**Ce înveți:** un fișier fără avertismente nu este noroc, este disciplină. Și `Switch` vs `MaterialSwitch` este întrebarea care apare la test.

### 30.0.8 `outline_add_2_24` vs `outline_add_24`

În `res/drawable/` din G1098 fișierul se numește `outline_add_2_24.xml`. În G1097 se numește `outline_add_24.xml`. Ambele sunt iconițe vectoriale „plus" de 24dp, cu același viewport de 960 de unități, dar cu `pathData` diferit: plusul din G1098 este desenat mai mare (de la 120 la 840, adică 720 de unități), cel din G1097 mai mic (de la 200 la 760, adică 560 de unități). `_2_` marchează a doua variantă a aceleiași iconițe.

**De ce contează:** `@drawable/...` se rezolvă **la build**, de către AAPT2. Numele este transformat într-un întreg în `R.java`. Dacă resursa lipsește, build-ul pică cu:

```
error: resource drawable/outline_add_2_24 (aka ro.ase.ie.g1098:drawable/outline_add_2_24) not found.
```

Nu este un crash la runtime. Este o eroare de compilare — aplicația nici nu se instalează.

**Consecința practică:** dacă copiezi `activity_main.xml` în alt proiect fără să copiezi și drawable-ul, build-ul pică. Soluția este să copiezi ambele fișiere, sau să schimbi referința într-un nume care există.

**Ce înveți:** referințele din XML sunt contracte de compilare. Un nume de resursă greșit se vede imediat, nu după două ecrane de test.

### 30.0.9 `activity_item.xml` este identic cu G1097

Cele 452 de linii sunt **identice byte cu byte** cu formularul din G1097. Aceleași patru carduri, aceleași ID-uri, aceleași stiluri, aceleași texte.

**De ce contează:** formularul este partea **stabilă** a aplicației între grupe. Ce variază de la o grupă la alta sunt modelul (numele câmpurilor) și activitățile (importuri, ordine). Layout-ul este același exercițiu copiat de toți.

**Ce înveți:** dacă știi `activity_item.xml` pe de rost dintr-o grupă, îl știi pentru toate. Efortul de memorare se face o singură dată.

### 30.0.10 `AndroidManifest.xml` diferă doar prin tema

Singura linie diferită este:

```
android:theme="@style/Theme.G1098"
```

față de `@style/Theme.G1097`. Numele activităților sunt relative la pachet (`.activities.MainActivity`), deci nu conțin „g1097" sau „g1098" în text.

**De ce contează:** manifestul descrie **componentele** aplicației, nu codul. El nu știe ce câmpuri are `Movie`. De aceea două aplicații cu modele diferite au manifeste identice.

**Ce înveți:** când schimbi grupa la examen, manifestul este ultimul loc în care trebuie să umbli — și doar la temă.

### 30.0.11 G1098 nu are `movie_item.xml`

G1097 are un `movie_item.xml` pregătit pentru laboratorul următor (RecyclerView), dar **nefolosit de niciun cod**. În setul de șase fișiere al acestui capitol, G1098 nu îl are.

**De ce contează:** un layout nefolosit nu schimbă nimic la runtime. Nu este inflate, nu consumă memorie, nu apare în ecran. Este doar un fișier în proiect.

**Ce înveți:** absența lui nu este o regresie. Ambele variante sunt corecte; diferența este că G1097 îți arată din timp ce urmează.

### 30.0.12 Sinteza: ce înveți din toate diferențele

| Diferența | Este despre | Se vede la runtime? | Te prinde compilatorul? |
|---|---|---|---|
| `posterUrl` vs `poster` | nume | nu | **da** |
| `= null` lipsă | documentație | nu | nu |
| poziția constructorului | ordine de citire | nu | nu |
| poster în `toString()` | diagnostic | **da** (în listă) | nu |
| importuri moarte | igienă | nu | nu (doar lint) |
| `outline_add_2_24` | resurse | nu | **da** (build) |
| `movie_item.xml` absent | inventar | nu | nu |

Regula care le leagă: **compilatorul verifică nume și resurse, nu intenții.** Tot ce ține de ordine, de documentație și de igienă rămâne în sarcina ta.

---

## 30.1 Cum să citești acest capitol

Acesta nu este un capitol de exerciții. Este un capitol de **citire cu lupa**: iei fiecare fișier al aplicației și îl parcurgi linie cu linie, cu explicația chiar deasupra.

- **Citește codul întâi, comentariul al doilea.** Acoperă cu mâna blocul de comentarii, spune ce face linia, apoi verifică.
- **Blocurile `TEORIE`** apar înaintea fiecărei clase și explică *de ce* există structura, nu *cum* funcționează.
- **Blocurile numerotate** („1. Validare", „2. Curățare") descriu pașii unei metode în ordinea execuției. Ordinea este parte din lecție.
- **Marcajele `RISC:` și `BUG:`** semnalează locurile unde codul funcționează astăzi, dar se poate rupe, sau unde se rupe deja.
- **Diagramele ASCII** arată ce nu se vede în cod: obiectul care călătorește între activități, ierarhia de view-uri, ciclul de viață.
- **Fiecare fișier are exact un bloc de cod**, întreg. Nu sunt fragmente: poți citi `ItemActivity.java` ca pe un document continuu, de la `package` la ultima acoladă.
- **Nu memora.** Scopul este să poți reconstrui fișierul pornind de la o diagramă.

---

## 30.2 `Movie.java` — modelul de date

Cel mai mic fișier al aplicației și singurul care nu depinde de Android. 129 de linii, dintre care 20 sunt getter-e și setter-e mecanice.

```java
/*
 * ======================================================================================
 * FIȘIER: Movie.java — MODELUL DE DATE AL GRUPEI G1098
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   O clasă POJO (Plain Old Java Object): 10 câmpuri private, un constructor cu 10
 *   parametri, un constructor gol, o metodă toString() și 20 de getter-e/setter-e.
 *   Zero logică de business. Zero import android.*.
 *
 * DE CE EXISTĂ:
 *   Ca să transporte datele unui film dintr-un ecran în altul fără să depindă de UI.
 *   `MainActivity` ține o listă de `Movie`; `ItemActivity` construiește un `Movie`
 *   din valorile formularului și îl trimite înapoi.
 *
 * CINE DEPINDE DE EL:
 *   - MainActivity: creează 3 filme demo și le afișează prin ArrayAdapter
 *   - ItemActivity: citește câmpurile în fillForm, le scrie în saveMovie
 *   - Intent: îl serializează cu putExtra, fiindcă implementează Serializable
 *
 * CE NU FACE:
 *   Nu validează nimic. Nu știe ce este un EditText, un Spinner sau un Intent.
 *   Nu are id: identitatea filmului în listă este POZIȚIA, nu un câmp.
 *   Nu formatează data: formatarea este treaba lui SimpleDateFormat din ItemActivity.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   Tot fluxul de date. `Intent.putExtra` nu ar avea ce serializa, `ArrayAdapter`
 *   nu ar avea ce afișa, iar `ItemActivity` ar trebui să trimită 10 extra-uri
 *   separate și să le recompună manual în MainActivity.
 * ======================================================================================
 */

// ======================================================================================
// PACHETUL
// ======================================================================================
// `model` este pachetul care ține DATELE. `activities` ține ecranele. Separarea nu este
// cosmetică: ea permite ca Movie să fie testat fără emulator, pentru că nu are nicio
// dependență de Android.
// ======================================================================================
package ro.ase.ie.g1098.model;

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
//   formata cu `SimpleDateFormat` și poți compara două date.
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
 * CE SE ÎNTÂMPLĂ EXACT LA SERIALIZARE
 * ======================================================================================
 *
 * 1. `putExtra(String, Serializable)` este verificat la COMPILARE. Dacă `Movie` nu ar
 *    implementa interfața, apelul nu ar găsi nicio metodă potrivită.
 *
 * 2. La runtime, `ObjectOutputStream` scrie în bytes:
 *      - numele clasei și `serialVersionUID`
 *      - fiecare câmp non-static și non-transient, în ordinea declarării
 *      - referințele, ca identificatori (un obiect partajat se scrie o singură dată)
 *
 * 3. `Date` este serializabil, deci `release` trece fără probleme. Dacă `Movie` ar
 *    ține un `View`, un `Context` sau un `Calendar`, serializarea ar arunca
 *    `NotSerializableException`.
 *
 * 4. La destinație, `getSerializableExtra` reconstruiește un graf NOU de obiecte.
 *    `Movie@A` din listă și `Movie@A'` din ItemActivity au același conținut, dar
 *    adrese diferite. `==` între ele este `false`; `.equals` nu este suprascris,
 *    deci tot `false`.
 *
 * 5. `serialVersionUID` lipsește. JVM-ul îl calculează din structura clasei. În
 *    același proces, între `putExtra` și `getSerializableExtra` trec milisecunde,
 *    deci riscul este nul. Între două versiuni ale aplicației, riscul este real.
 * ======================================================================================
 */

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
    // ATENȚIE: comentariul din sursă spune „Switch", dar tipul real este
    //   `MaterialSwitch`. `android.widget.Switch` este o altă clasă.
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
    // DIFERENȚA FAȚĂ DE G1097: aici câmpul se numește `posterUrl` și NU are
    //   inițializator `= null`. Valoarea implicită este tot `null`; diferența este
    //   doar de documentație. Vezi 30.0.1 și 30.0.2.
    // RISC: `null` ajunge în `etPoster.setText(null)` la editare — legal, dar afișează
    //   câmp gol. Dacă ai apela `.length()` pe el, ai lua `NullPointerException`.
    // ==================================================================================
    private String posterUrl;

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

        // Linia care diferă de G1097 doar prin numele câmpului: `posterUrl`, nu `poster`.
        this.posterUrl = posterUrl;
    }

    // ==================================================================================
    // toString() — CONTRACTUL DE AFIȘARE ÎN LISTĂ
    // ==================================================================================
    // DE CE ESTE OBLIGATORIU AICI:
    //   `ArrayAdapter` cu `android.R.layout.simple_list_item_1` primește un `TextView`
    //   și îl umple cu `item.toString()`. Fără suprascriere, `Object.toString()` ar
    //   întoarce `ro.ase.ie.g1098.model.Movie@a1b2c3d` — adresa din memorie.
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
    // DIFERENȚA FAȚĂ DE G1096 ȘI G1099: aici apare și `posterUrl`. Cele două grupe
    //   omit posterul complet. G1097 îl are, dar cu numele `poster`.
    //
    // CE SE VEDE PE ECRAN: toate cele 10 câmpuri, pe un singur rând, inclusiv URL-ul
    //   posterului. Urât, dar corect. Se repară în laboratorul următor cu RecyclerView.
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

                // Ultimul câmp: posterul. Este singurul loc din aplicație unde URL-ul
                // apare pe ecran, în rândul listei. Dacă ar lipsi, `toString()` ar
                // rămâne valid, dar ai pierde câmpul la depanare.
                ", posterUrl='" + posterUrl + '\'' +

                // Acolada de închidere a obiectului, ca text.
                '}';
    }

    // ==================================================================================
    // CONSTRUCTORUL FĂRĂ PARAMETRI — POZIȚIA CARE DIFERĂ DE G1097
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
    // DE CE ESTE AICI ȘI NU LA SFÂRȘIT: poziția nu contează pentru compilator.
    //   În G1098 stă imediat după `toString()`, ca cititorul să vadă amândouă
    //   constructoarele înainte de cele 20 de metode mecanice. În G1097 este ultima.
    // ==================================================================================
    public Movie() {
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
    // NUMELE: `getPosterUrl`, nu `getPoster` — aici se vede diferența față de G1097.
    //   `fillForm` din ItemActivity apelează exact acest nume.
    public String getPosterUrl() {
        return posterUrl;
    }

    // SETTER pentru poster. Acceptă `null` fără să se plângă.
    // `saveMovie` apelează `movie.setPosterUrl(etPoster.getText().toString())`.
    public void setPosterUrl(String posterUrl) {
        this.posterUrl = posterUrl;
    }
}
```

**Tabel de referință — cele 10 câmpuri și perechea lor din UI:**

| # | Câmp | Tip | Getter | Setter | Widget |
|---|---|---|---|---|---|
| 1 | `title` | `String` | `getTitle()` | `setTitle()` | `etTitle` |
| 2 | `release` | `Date` | `getRelease()` | `setRelease()` | `etRelease` + dialog |
| 3 | `genre` | `String` | `getGenre()` | `setGenre()` | `spGenre` |
| 4 | `budget` | `double` | `getBudget()` | `setBudget()` | `etBudget` |
| 5 | `duration` | `int` | `getDuration()` | `setDuration()` | `sbDuration` |
| 6 | `rating` | `float` | `getRating()` | `setRating()` | `rbRating` |
| 7 | `watched` | `boolean` | `isWatched()` | `setWatched()` | `swWatched` |
| 8 | `approval` | `String` | `getApproval()` | `setApproval()` | `rgApproval` |
| 9 | `onWatchlist` | `boolean` | `isOnWatchlist()` | `setOnWatchlist()` | `cbOnWatchList` |
| 10 | `posterUrl` | `String` | `getPosterUrl()` | `setPosterUrl()` | `etPoster` |

**Cele trei lucruri care se pot întreba din acest fișier:**

1. **De ce `implements Serializable`?** Ca să poată fi pus într-un `Intent` cu `putExtra`.
2. **Obiectul primit în `ItemActivity` este originalul?** Nu. Este o copie deserializată.
3. **De ce constructor gol explicit?** Un constructor cu parametri suprimă constructorul implicit, iar `saveMovie` face `new Movie()`.

---

## 30.3 `MainActivity.java` — lista și navigarea

Ecranul de start. 145 de linii, dintre care jumătate sunt importuri și semnături. Fișierul care **deține starea** aplicației: lista `movies`.

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
 * CE NU FACE: nu salvează nimic pe disc. Lista trăiește cât trăiește procesul.
 *   La rotirea ecranului, activitatea este recreată și `addSampleMovies()` rulează
 *   din nou — filmele adăugate se pierd. Persistența vine în laboratorul următor.
 *
 * CE S-AR RUPE FĂRĂ EL: aplicația ar porni direct într-un formular fără listă,
 *   iar rezultatul salvat nu ar avea unde să se întoarcă.
 * ======================================================================================
 */

// ======================================================================================
// PACHETUL
// ======================================================================================
// `activities` ține ecranele. Modelul stă în `model`, iar `R` în rădăcina pachetului.
// ======================================================================================
package ro.ase.ie.g1098.activities;

// ======================================================================================
// IMPORTURI — GRUPATE PE SURSĂ
// ======================================================================================
// android.*        — clase din framework (Intent, Bundle, View, widget-uri)
// androidx.*       — biblioteci Jetpack (AppCompat, EdgeToEdge, insets, activity result)
// com.google.*     — Material Components (FloatingActionButton)
// java.util.*      — colecții și date
// ro.ase.ie.g1098  — modelul și clasa R generată
//
// OBSERVAȚIE DE IGIENĂ: singurul import nefolosit din fișier este `android.widget.Toast`.
//   G1097 mai are unul: `java.util.Date`. Ambele sunt inofensive la runtime — un import
//   nu ajunge în bytecode — dar sugerează o dependență care nu există.
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
//   Este singurul import mort al grupei G1098 în MainActivity.
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

// GregorianCalendar: constructorul de dată folosit în addSampleMovies.
//   `new GregorianCalendar(an, luna, zi).getTime()` produce un `Date` direct.
import java.util.GregorianCalendar;

// List: tipul declarat al câmpului `movies` (interfața, nu implementarea).
import java.util.List;

// R: clasa generată de build care mapăează numele din XML la întregi.
import ro.ase.ie.g1098.R;

// Movie: modelul de date.
import ro.ase.ie.g1098.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: CINE ȚINE STAREA ȘI CINE O AFIȘEAZĂ
 * ======================================================================================
 *
 * 1. **Un singur proprietar al listei.** `movies` este `final` și este singura listă
 *    din aplicație. `ItemActivity` nu are listă; primește un `Movie` și întoarce un
 *    `Movie`. Regula „o singură sursă de adevăr" previne liste care se contrazic.
 *
 * 2. **Adapterul nu copiază lista.** `new ArrayAdapter<>(this, layout, movies)` primește
 *    REFERINȚA la listă. Adapterul citește din ea la fiecare `getView`. De aceea
 *    `movies.add(...)` se vede imediat în adapter — dar ListView-ul nu redesenează
 *    decât după `notifyDataSetChanged()`.
 *
 * 3. **Ordinea din onCreate este contract.** `addSampleMovies()` trebuie să ruleze
 *    înainte de crearea adapterului, ca lista să aibă conținut la primul bind.
 *    `initControls()` trebuie să ruleze înainte de `initListeners()`, ca
 *    `fabInsert` și `listView` să fie deja legate când li se pun listeneri.
 *
 * 4. **Launcher-ul se înregistrează în onCreate, nu în listener.** `registerForActivityResult`
 *    trebuie apelat înainte ca activitatea să ajungă în starea STARTED. Apelat dintr-un
 *    `onClick`, ar arunca `IllegalStateException`.
 *
 * CICLUL DE VIAȚĂ, PE SCURT:
 *
 *   onCreate  -> super, EdgeToEdge, setContentView, insets, date, adapter,
 *                controls, listeners, launcher
 *   onStart   -> activitatea devine vizibilă
 *   onResume  -> primește input
 *   onPause   -> pierde input (ItemActivity apare peste ea)
 *   onStop    -> nu mai este vizibilă
 *   onDestroy -> distrusă (rotire, back, proces omorât)
 *
 *   La întoarcerea din ItemActivity: onStart -> onResume -> callback-ul launcher-ului.
 * ======================================================================================
 */
public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // CHEILE EXTRA — CONTRACTUL DINTRE CELE DOUĂ ACTIVITĂȚI
    // ==================================================================================
    // `protected static final`: `static` pentru că nu depinde de instanță, `protected`
    //   ca să fie vizibil din ItemActivity (același pachet `activities`), `final`
    //   pentru că valoarea nu se schimbă niciodată.
    // VALOAREA este un String oarecare: „position" și „movie". Convenția este să fie
    //   unică în aplicație; altfel două extra-uri cu aceeași cheie se suprascriu.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";

    // Butonul „+". Tipul concret este FloatingActionButton, nu View: avem nevoie
    // doar de setOnClickListener, care există pe orice View, dar tipul concret
    // documentează ce widget este.
    private FloatingActionButton fabInsert;

    // Lista derulantă.
    private ListView listView;

    // Launcher-ul de rezultat. Este atribuit în onCreate, DUPĂ initListeners().
    // `ActivityResultLauncher<Intent>`: pornește un Intent și întoarce un ActivityResult.
    private ActivityResultLauncher<Intent> launcher;

    // LISTA — starea aplicației. `final` înseamnă că referința nu se schimbă;
    // conținutul, da. `List` este interfața; `ArrayList` este implementarea.
    // Inițializarea la declarație garantează că lista există înainte de orice metodă.
    private final List<Movie> movies = new ArrayList<>();

    // Adapterul. Este creat în onCreate, după ce lista are deja cele 3 filme demo.
    private ArrayAdapter<Movie> movieAdapter;

    /*
     * ==============================================================================
     * BLOC DE TEORIE: ACTIVITY RESULT API
     * ==============================================================================
     *
     * 1. Înainte de AndroidX Activity 1.2, rezultatul se lua cu:
     *      startActivityForResult(intent, REQUEST_CODE);
     *      onActivityResult(requestCode, resultCode, data)
     *    Ambele sunt DEPRECATE. Problema: codul de request era un `int` global, ușor
     *    de duplicat, iar metoda `onActivityResult` creștea cu un `switch` pentru
     *    fiecare activitate pornită.
     *
     * 2. API-ul nou leagă un CALLBACK de un CONTRACT, o singură dată:
     *      launcher = registerForActivityResult(contract, callback)
     *      launcher.launch(intent)
     *
     * 3. `StartActivityForResult` este contractul generic: primește un `Intent` și
     *    întoarce un `ActivityResult` (cod + Intent).
     *
     * 4. Înregistrarea trebuie făcută în `onCreate`, înainte de starea STARTED.
     *    Un `launcher` înregistrat prea târziu aruncă `IllegalStateException`.
     *
     * 5. Callback-ul rulează pe UI thread, după `onResume`, când activitatea este
     *    din nou vizibilă. De aceea `notifyDataSetChanged()` este sigur acolo.
     * ==============================================================================
     */

    // ==================================================================================
    // onCreate — LOCUL ÎN CARE SE CONSTRUIEȘTE ECRANUL
    // ==================================================================================
    // CE FACE: leagă layout-ul, populează lista, creează adapterul, leagă widget-urile,
    //   instalează listenerii și înregistrează launcher-ul de rezultat.
    // CUM: în ordinea de mai jos. Ordinea este parte din lecție.
    // RISC: dacă `initListeners()` ar rula înainte de `initControls()`, `fabInsert`
    //   ar fi `null` și `setOnClickListener` ar arunca `NullPointerException`.
    // REF: același schelet în toate grupele; capitolul 22, secțiunea 22.2.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. Lanțul către superclasă. OBLIGATORIU primul: AppCompatActivity își face
        //    inițializările interne (temă, fragment manager, saved state) aici.
        //    Dacă îl muți mai jos, primești excepții greu de diagnosticat.
        super.onCreate(savedInstanceState);

        // 2. Edge-to-edge: conținutul este desenat sub bara de status și sub cea de
        //    navigare. Fără pasul 4, primele rânduri ar sta sub ceas.
        EdgeToEdge.enable(this);

        // 3. Layout-ul. `R.layout.activity_main` este ID-ul generat pentru fișierul
        //    `res/layout/activity_main.xml`. De aici încolo, `findViewById` poate
        //    găsi widget-urile.
        setContentView(R.layout.activity_main);

        // 4. Insets: măsurăm barele de sistem și le transformăm în padding pe rădăcină.
        //    `findViewById(R.id.main)` este FrameLayout-ul din XML — de aceea ID-ul
        //    `main` este obligatoriu acolo.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. Cât ocupă barele de sistem, în pixeli.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Padding pe toate cele patru laturi. Astfel conținutul începe sub
            //     bara de status și se termină deasupra barei de navigare.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. `return insets` = „nu am consumat nimic"; copiii primesc mai departe.
            return insets;
        });

        // 5. Datele de demonstrație. Trebuie să ruleze ÎNAINTE de crearea adapterului,
        //    ca lista să aibă conținut la primul bind.
        addSampleMovies();

        // 6. Adapterul. `android.R.layout.simple_list_item_1` este un layout din
        //    framework: un singur TextView. `this` este Context-ul cerut de constructor.
        //    Al treilea argument este lista — adapterul păstrează REFERINȚA, nu o copie.
        movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);

        // 7. Legarea widget-urilor la câmpuri.
        initControls();

        // 8. Instalarea listener-ilor. Rulează după initControls, ca widget-urile
        //    să fie deja non-null.
        initListeners();

        // 9. Launcher-ul de rezultat. Se înregistrează O SINGURĂ DATĂ, în onCreate.
        //    `StartActivityForResult` este contractul care spune: „pornesc o activitate
        //    și vreau un rezultat înapoi".
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // Callback-ul: o clasă anonimă care implementează o singură metodă.
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // 9a. Verificăm codul. `RESULT_OK` înseamnă că ItemActivity a
                        //     apelat `setResult(RESULT_OK, intent)`. Dacă utilizatorul
                        //     a apăsat Back, codul este `RESULT_CANCELED` și nu facem nimic.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // 9b. Intent-ul rezultat. Poate fi `null` teoretic, dar
                            //     ItemActivity îl trimite mereu când codul este OK.
                            Intent intent = o.getData();

                            // 9c. Scoatem obiectul. `getSerializableExtra` întoarce
                            //     `Serializable`, deci cast-ul la `Movie` este obligatoriu.
                            //     Obiectul este O COPIE deserializată, nu originalul.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // 9d. Poziția. Lipsa extra-ului înseamnă insert, adică -1.
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // 9e. Ramura de INSERT: poziția lipsește.
                            if(position == -1)
                            {
                                // Adăugăm la finalul listei.
                                movies.add(movie);

                                // Anunțăm adapterul. Fără acest apel, ListView-ul nu
                                // știe că lista are un element nou și nu redesenează.
                                movieAdapter.notifyDataSetChanged();
                            }
                            // 9f. Ramura de EDIT: poziția există.
                            else
                            {
                                // ÎNLOCUIRE, nu adăugare. `set` păstrează ordinea.
                                movies.set(position, movie);

                                // Și aici este nevoie de notificare.
                                movieAdapter.notifyDataSetChanged();
                            }
                        }
                    }
                });
    }

    // ==================================================================================
    // initListeners — CE SE ÎNTÂMPLĂ LA APĂSARE
    // ==================================================================================
    // CE FACE: instalează doi listeneri — unul pe FAB (insert), unul pe rândul de listă
    //   (edit).
    // CUM: `setOnClickListener` pe FAB; `setOnItemClickListener` pe ListView.
    // RISC: listener-ii sunt clase anonime. În interiorul lor, `this` NU este
    //   MainActivity, ci obiectul listener. De aceea se scrie `MainActivity.this`.
    // REF: capitolul 22, secțiunea 22.2.
    // ==================================================================================
    private void initListeners() {

        // 1. FAB -> formular gol (insert).
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // Intent EXPLICIT: (Context, Class). Al doilea argument este clasa
                // activității care trebuie pornită. Intent-ul implicit ar căuta
                // o aplicație care știe să facă ceva, nu clasa noastră.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // Pornirea prin launcher, nu prin `startActivityForResult` (deprecat).
                // Launcher-ul știe ce callback să apeleze la întoarcere.
                launcher.launch(intent);
            }
        });

        // 2. Click pe rând -> formular plin (edit).
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                // 2a. Același Intent explicit.
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);

                // 2b. Obiectul care călătorește. `movies.get(position)` este filmul
                //     de pe rândul apăsat. Serializarea se face automat.
                intent.putExtra(MOVIE_EXTRA, movies.get(position));

                // 2c. Poziția, ca ItemActivity să știe ce să înlocuiască la întoarcere.
                intent.putExtra(POSITION_EXTRA, position);

                // 2d. Pornire.
                launcher.launch(intent);
            }
        });
    }

    // ==================================================================================
    // initControls — FINDVIEWBYID
    // ==================================================================================
    // CE FACE: leagă cele două widget-uri de câmpuri și instalează adapterul pe listă.
    // CUM: `findViewById` cu ID-ul din XML; apoi `setAdapter`.
    // RISC: `findViewById` întoarce `null` dacă ID-ul nu există în layout-ul setat.
    //   Un ID greșit nu dă eroare la compilare — dă `NullPointerException` la runtime.
    // REF: `R.id.floatingActionButton` și `R.id.listView` din `activity_main.xml`.
    // ==================================================================================
    private void initControls() {

        // ID-ul din XML este `floatingActionButton`, iar câmpul se numește `fabInsert`.
        // Numele nu trebuie să coincidă; contează doar ID-ul din `R.id`.
        fabInsert = findViewById(R.id.floatingActionButton);

        // Lista.
        listView = findViewById(R.id.listView);

        // Adapterul se instalează pe listă. Din acest moment, ListView-ul întreabă
        // adapterul ce să afișeze pe fiecare rând.
        listView.setAdapter(movieAdapter);
    }

    // ==================================================================================
    // addSampleMovies — DATELE DE DEMONSTRAȚIE
    // ==================================================================================
    // CE FACE: adaugă trei filme în listă, ca ecranul să nu fie gol la prima pornire.
    // CUM: trei apeluri ale constructorului cu 10 parametri.
    // RISC: ordinea argumentelor este POZIȚIONALĂ. Aici sunt 3 String-uri și 2 boolean-uri,
    //   deci inversarea lor compilează. Verifică tabelul din 30.2.
    // REF: constructorul `Movie(...)` din `Movie.java`.
    // ==================================================================================
    private void addSampleMovies() {

        // FILMUL 1 — Inception.
        // `new GregorianCalendar(an, luna, zi)`: luna este 0-based! `Calendar.JULY` = 6,
        // nu 7. `.getTime()` transformă Calendar în Date, tipul cerut de constructor.
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

        // FILMUL 2 — Toy Story.
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

        // FILMUL 3 — The Matrix.
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

### 30.3.1 Ordinea din `onCreate` — de ce nu se poate schimba

```
onCreate
  |
  |-- 1. super.onCreate(savedState)        <- fără el, AppCompat nu e inițializat
  |-- 2. EdgeToEdge.enable(this)           <- conținut sub barele de sistem
  |-- 3. setContentView(activity_main)     <- de aici încolo există view-uri
  |-- 4. insets pe R.id.main               <- padding pe rădăcină
  |-- 5. addSampleMovies()                 <- lista are conținut
  |-- 6. movieAdapter = new ArrayAdapter   <- adapterul primește lista
  |-- 7. initControls()                    <- fabInsert + listView + setAdapter
  |-- 8. initListeners()                   <- listeneri pe obiecte non-null
  +-- 9. launcher = registerForActivityResult(...)
```

**De ce `launcher` este ultimul:** listener-ii instalați la pasul 8 conțin `launcher.launch(...)`. Dacă ai apela `launcher.launch` înainte ca `launcher` să fie atribuit, ai lua `NullPointerException`. În practică nu se poate întâmpla: niciun click nu poate ajunge la listener până când `onCreate` nu s-a terminat și ecranul nu este desenat.

**De ce `registerForActivityResult` nu poate sta într-un listener:** înregistrarea trebuie făcută înainte ca activitatea să atingă starea `STARTED`. Un `onClick` rulează mult după aceea, iar Android aruncă `IllegalStateException: LifecycleOwner is attempting to register while current state is RESUMED`.

### 30.3.2 Ce se întâmplă la întoarcerea din `ItemActivity`

```
ItemActivity: setResult(RESULT_OK, intent) + finish()
      |
      v
MainActivity: onStart -> onResume
      |
      v
ActivityResultRegistry livrează rezultatul
      |
      v
onActivityResult(ActivityResult o)
      |
      |-- o.getResultCode() == RESULT_OK ?
      |        |
      |        +-- NU  -> nimic (utilizatorul a apăsat Back)
      |        |
      |        +-- DA  -> intent = o.getData()
      |                   movie = (Movie) getSerializableExtra("movie")
      |                   position = getIntExtra("position", -1)
      |                        |
      |                        +-- -1  -> movies.add(movie)
      |                        +-- >=0 -> movies.set(position, movie)
      |                        |
      |                        +-- movieAdapter.notifyDataSetChanged()
      v
ListView redesenează rândurile vizibile
```

**RISC:** dacă uiți `notifyDataSetChanged()`, lista din memorie se modifică, dar ecranul rămâne neschimbat până la următoarea redesenează (rotire, derulare). Este cel mai frecvent bug „invizibil" din aplicațiile cu `ListView`.

### 30.3.3 `MainActivity.this` vs `this`

```
În afara clasei anonime:        În interiorul `new View.OnClickListener() { ... }`:
-----------------------------   ------------------------------------------------
this          = MainActivity     this          = OnClickListener
MainActivity.this = MainActivity MainActivity.this = MainActivity
```

Constructorul `Intent(Context, Class)` cere un `Context`. `MainActivity` **este** un `Context` (extinde `AppCompatActivity` -> `Context`), dar `OnClickListener` nu este. De aceea se scrie `MainActivity.this`.

---

## 30.4 `ItemActivity.java` — formularul

Cel mai mare fișier Java al aplicației: 218 linii, 13 widget-uri, 4 listeneri și două metode care fac toată munca (`fillForm`, `saveMovie`). Este și fișierul cu **zero importuri moarte** — cel mai curat din toate grupele.

```java
/*
 * ======================================================================================
 * FIȘIER: ItemActivity.java — FORMULARUL DE INSERT ȘI EDIT
 * ======================================================================================
 * CE ESTE: a doua activitate. Afișează un formular cu 13 controale, citește valorile
 *   și le împachetează într-un `Movie`, pe care îl trimite înapoi în MainActivity.
 *
 * DE CE EXISTĂ: MainActivity ține lista, dar nu are loc pe ecran pentru un formular.
 *   Separarea în două activități este modelul clasic „listă + detaliu".
 *
 * CE ȘTIE: cele 13 widget-uri, un `Calendar` care este sursa de adevăr pentru dată,
 *   un `SimpleDateFormat`, poziția din listă (-1 = insert) și cheile extra.
 *
 * CE NU FACE: nu ține lista, nu știe ce este înainte sau după filmul editat, nu
 *   salvează nimic pe disc. Produce un `Movie` și îl predă.
 *
 * CE S-AR RUPE FĂRĂ EL: butonul „+" ar deschide o activitate inexistentă, iar
 *   click-ul pe un rând ar arunca `ActivityNotFoundException`.
 * ======================================================================================
 */

// ======================================================================================
// PACHETUL
// ======================================================================================
// Același pachet ca MainActivity: `activities`. De aceea `MainActivity.MOVIE_EXTRA`
// este vizibil aici fără import — `protected` + același pachet.
// ======================================================================================
package ro.ase.ie.g1098.activities;

// ======================================================================================
// IMPORTURI — TOATE FOLOSITE
// ======================================================================================
// Diferența față de G1097: acolo existau patru importuri moarte (`Switch`, `Toast`,
// `Snackbar`, `ActivityItemBinding`). Aici fiecare import corespunde unui nume scris
// în fișier. Verificarea este mecanică: caută numele în corpul clasei.
// ======================================================================================

// DatePickerDialog: dialogul de alegere a datei.
import android.app.DatePickerDialog;

// Intent: obiectul în care punem rezultatul.
import android.content.Intent;

// Bundle: doar în semnătura lui onCreate.
import android.os.Bundle;

// View: tipul parametrului din onClick și clasa de bază a widget-urilor.
import android.view.View;

// Button: butonul „Save Movie" / „Update Movie".
import android.widget.Button;

// CheckBox: bifa „Watchlist". Tipul declarat este CheckBox, deși widget-ul din XML
//   este MaterialCheckBox — care extinde CheckBox.
import android.widget.CheckBox;

// CompoundButton: interfața pentru switch/checkbox; `OnCheckedChangeListener` stă aici.
import android.widget.CompoundButton;

// DatePicker: parametrul din onDateSet.
import android.widget.DatePicker;

// EditText: titlu, dată, buget, poster.
import android.widget.EditText;

// RadioButton: butoanele din grupul de ghidaj.
import android.widget.RadioButton;

// RadioGroup: containerul care garantează selecția unică.
import android.widget.RadioGroup;

// RatingBar: stelele.
import android.widget.RatingBar;

// SeekBar: slider-ul de durată.
import android.widget.SeekBar;

// Spinner: lista de genuri.
import android.widget.Spinner;

// TextView: cele două etichete dinamice (durata și valoarea switch-ului).
import android.widget.TextView;

// EdgeToEdge: desenare sub barele de sistem.
import androidx.activity.EdgeToEdge;

// NonNull: adnotare pe parametrul lui onCheckedChanged. Nu schimbă comportamentul;
//   documentează că Android garantează un obiect non-null.
import androidx.annotation.NonNull;

// AppCompatActivity: clasa de bază.
import androidx.appcompat.app.AppCompatActivity;

// IntentCompat: variantă compatibilă a `getSerializableExtra`, cu tip explicit.
import androidx.core.content.IntentCompat;

// Insets / ViewCompat / WindowInsetsCompat: aceleași ca în MainActivity.
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

// MaterialSwitch: switch-ul Material. NU `android.widget.Switch` — aceea este altă clasă.
import com.google.android.material.materialswitch.MaterialSwitch;

// ParseException: excepția aruncată de `SimpleDateFormat.parse`.
import java.text.ParseException;

// SimpleDateFormat: conversia Date <-> String.
import java.text.SimpleDateFormat;

// Calendar: câmpurile de dată și sursa de adevăr pentru release.
import java.util.Calendar;

// Date: tipul întors de `releaseCal.getTime()` și de `dateFormat.parse(...)`.
import java.util.Date;

// Locale: formatul regional pentru date.
import java.util.Locale;

// R și Movie.
import ro.ase.ie.g1098.R;
import ro.ase.ie.g1098.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: FORMULARUL CA MAȘINĂ DE STARE
 * ======================================================================================
 *
 * 1. **Două moduri, o singură activitate.** `position == -1` înseamnă INSERT;
 *    `position >= 0` înseamnă EDIT. Nu există două activități separate, pentru că
 *    formularul este identic; diferă doar valorile inițiale și eticheta butonului.
 *
 * 2. **Widget-urile sunt sursa de adevăr pentru 9 câmpuri, Calendar pentru unul.**
 *    Titlul se citește din `etTitle`, bugetul din `etBudget` etc. Data NU se citește
 *    din `etRelease`: textul este doar o AFIȘARE, valoarea reală stă în `releaseCal`.
 *
 *        [etRelease]  --(afișare)-->  "16/07/2010"
 *        [releaseCal] --(valoare)-->  Date  --> saveMovie() --> Movie
 *
 * 3. **Rezultatul se întoarce prin Intent.** `setResult(RESULT_OK, intent)` +
 *    `finish()` este perechea obligatorie. Fără `finish()`, activitatea rămâne
 *    deschisă; fără `setResult`, MainActivity primește `RESULT_CANCELED`.
 *
 * 4. **Validarea lipsește.** Formularul nu verifică nimic: bugetul gol crapă,
 *    data null crapă, ghidajul nemarcat lasă `approval` null. Sunt bug-uri reale,
 *    marcate mai jos cu `BUG:`.
 *
 * CE SE ÎNTÂMPLĂ LA FIECARE APĂSARE:
 *
 *   etRelease click      -> showReleaseDatePicker() -> dialog -> releaseCal + text
 *   btnMovieAction click -> saveMovie() -> Intent -> setResult -> finish
 *   swWatched toggle     -> tvWatchedValue.setText("Yes"/"No")
 *   sbDuration drag      -> tvDurationValue.setText(progress + " min.")
 * ======================================================================================
 */
public class ItemActivity extends AppCompatActivity {

    // ==================================================================================
    // CELE 13 WIDGET-URI — câmpuri, legate în initControls()
    // ==================================================================================
    // Toate sunt `private`: nimeni din afară nu are voie să le atingă. Toate sunt
    //   legate cu `findViewById` în aceeași metodă, ca o greșeală de ID să fie
    //   vizibilă într-un singur loc.
    // ==================================================================================

    // 1. Titlul — TextInputEditText.
    private EditText etTitle;

    // 2. Data — TextInputEditText, dar NU se citește din el (vezi releaseCal).
    private EditText etRelease;

    // 3. Genul — Spinner cu `@array/movie_genre`.
    private Spinner spGenre;

    // 4. Bugetul — TextInputEditText cu inputType=numberDecimal.
    private EditText etBudget;

    // 5. Durata — SeekBar 0..300.
    private SeekBar sbDuration;

    // 6. Rating — RatingBar cu 5 stele și pas 0.5.
    private RatingBar rbRating;

    // 7. Ghidajul — RadioGroup cu 5 butoane.
    private RadioGroup rgApproval;

    // 8. Bifa Watchlist — ID `cbOnWatchList`, câmp `cbonWatchList`.
    private CheckBox cbonWatchList;

    // 9. Switch-ul — MaterialSwitch, NU android.widget.Switch.
    private MaterialSwitch swWatched;

    // 10. Posterul — TextInputEditText cu inputType=textUri.
    private EditText etPoster;

    // 11. Butonul de acțiune — „Save Movie" sau „Update Movie".
    private Button btMovieAction;

    // 12. Eticheta care arată durata curentă.
    private TextView tvDurationValue;

    // 13. Eticheta care arată „Yes"/„No" pentru switch.
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
    // `Locale.getDefault()` = formatul limbii dispozitivului.
    // `final`: referința nu se schimbă. Obiectul, însă, este MUTABIL.
    // RISC: `SimpleDateFormat` nu este thread-safe. Aici este folosit exclusiv pe
    //   UI thread, deci nu există concurență.
    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());

    // ==================================================================================
    // onCreate — CONSTRUIREA FORMULARULUI
    // ==================================================================================
    // CE FACE: leagă layout-ul, leagă widget-urile, instalează listenerii și apoi
    //   verifică dacă a fost pornită pentru edit.
    // CUM: initControls -> initListeners -> citirea Intent-ului -> fillForm.
    // RISC: ordinea contează. `fillForm` atinge widget-uri, deci trebuie să ruleze
    //   după `initControls`. Listenerii trebuie instalați înainte de `fillForm`,
    //   altfel `setChecked` ar declanșa listener-ul? Nu: listener-ul se instalează
    //   înainte, iar `setChecked` ÎL DECLANȘEAZĂ — de aceea eticheta „Yes"/„No"
    //   se actualizează corect la editare.
    // REF: capitolul 22, secțiunea 22.3.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. Lanțul către superclasă, obligatoriu primul.
        super.onCreate(savedInstanceState);

        // 2. Edge-to-edge.
        EdgeToEdge.enable(this);

        // 3. Layout-ul formularului.
        setContentView(R.layout.activity_item);

        // 4. Insets pe rădăcină. `R.id.main` este ScrollView-ul din XML.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // 5. Widget-urile, înainte de orice le atinge.
        initControls();

        // 6. Listenerii, înainte de fillForm (ca setChecked să actualizeze eticheta).
        initListeners();

        // 7. Intent-ul care a pornit activitatea. Poate conține un film (edit)
        //    sau poate fi gol (insert).
        Intent intent = getIntent();

        // 8. Citirea filmului. `IntentCompat.getSerializableExtra` este varianta
        //    tipată: al treilea argument este clasa, deci nu mai este nevoie de cast.
        //    Rezultatul este O COPIE deserializată, nu originalul din listă.
        Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);

        // 9. Dacă există un film, suntem în modul EDIT.
        if (existing != null) {

            // 9a. Poziția din listă. Dacă extra-ul lipsește, rămâne -1 — dar
            //     în modul edit el este mereu trimis de MainActivity.
            position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);

            // 9b. Umplem formularul cu valorile filmului.
            fillForm(existing);

            // 9c. Titlul ecranului (bara de sus).
            setTitle("Edit movie");

            // 9d. Eticheta butonului.
            btMovieAction.setText("Update Movie");
        }
    }

    // ==================================================================================
    // fillForm — MODEL -> WIDGET-URI
    // ==================================================================================
    // CE FACE: copiază cele 10 câmpuri ale unui `Movie` în cele 13 controale.
    // CUM: 9 setări directe + 2 bucle de potrivire (Spinner, RadioGroup).
    // RISC: `existing.getRelease()` poate fi `null` -> `dateFormat.format(null)`
    //   aruncă NPE. `getPosterUrl()` poate fi `null` -> `setText(null)` este legal.
    // REF: perechea acestei metode este `saveMovie` — fiecare setare de aici are
    //   un echivalent invers acolo.
    // ==================================================================================
    private void fillForm(Movie existing) {

        // 1. Titlul: String -> EditText.
        etTitle.setText(existing.getTitle());

        // 2. Data: Date -> String formatat. ATENȚIE: `releaseCal` NU este actualizat
        //    aici. Vezi BUG 3 mai jos.
        etRelease.setText(dateFormat.format(existing.getRelease()));

        // 3. Bugetul: double -> String. `String.valueOf` evita `"" + budget`.
        etBudget.setText(String.valueOf(existing.getBudget()));

        // 4. Durata: int -> progres pe SeekBar.
        sbDuration.setProgress(existing.getDuration());

        // 5. Bifa Watchlist.
        cbonWatchList.setChecked(existing.isOnWatchlist());

        // 6. Switch-ul. `setChecked` declanșează listener-ul instalat în onCreate,
        //    deci `tvWatchedValue` primește „Yes"/„No" fără cod suplimentar.
        swWatched.setChecked(existing.isWatched());

        // 7. Rating-ul: float -> stele.
        rbRating.setRating(existing.getRating());

        // 8. Posterul: String -> EditText. Poate fi `null`; `setText(null)` afișează gol.
        etPoster.setText(existing.getPosterUrl());

        // 9. Genul: căutare în Spinner după TEXT.
        //    `getCount()` = numărul de elemente din `@array/movie_genre`.
        for(int index=0; index<spGenre.getCount(); index++)
        {
            // `getItemAtPosition(index)` întoarce `Object`; `.equals` compară textele.
            if(spGenre.getItemAtPosition(index).equals(existing.getGenre()))
            {
                // Am găsit genul: îl selectăm și ieșim din buclă.
                spGenre.setSelection(index);

                // Fără `break`, am continua să căutăm și am putea selecta alt element
                // dacă lista ar conține duplicate.
                break;
            }
        }

        // 10. Ghidajul: căutare în RadioGroup după TEXTUL butonului.
        //     `getChildCount()` = 5. `getChildAt(index)` întoarce `View`.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            // Cast la RadioButton pentru a putea citi textul.
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // Potrivire pe text: „PG-13" din model == „PG-13" din XML.
            if(rb.getText().toString().equals(existing.getApproval()))
            {
                // `check` vrea ID-ul, nu indexul. `check` debifează automat restul.
                rgApproval.check(rgApproval.getChildAt(index).getId());

                // Un singur buton poate fi selectat; ieșim.
                break;
            }
        }
    }

    /*
     * ==============================================================================
     * BLOC DE TEORIE: findViewById vs ViewBinding
     * ==============================================================================
     *
     * 1. `findViewById(R.id.x)` caută în arborele de view-uri la RUNTIME și întoarce
     *    `View`. Cast-ul la tipul concret este implicit prin generică, dar nu este
     *    verificat de compilator: un ID greșit sau un tip greșit dă eroare abia la
     *    runtime.
     *
     * 2. ViewBinding generează o clasă `ActivityItemBinding` cu un câmp pentru fiecare
     *    ID. `binding.etTitle` este verificat la COMPILARE. În plus, nu mai e nevoie
     *    de 13 linii de `findViewById`.
     *
     * 3. De ce nu este folosit aici: la acest laborator se predă metoda clasică.
     *    ViewBinding apare în DMA05, iar cursul îl tratează separat.
     *
     * 4. Amestecul este permis, dar costă: dacă folosești binding pentru 12 câmpuri
     *    și findViewById pentru al 13-lea, ai două mecanisme de întreținut.
     * ==============================================================================
     */

    // ==================================================================================
    // initControls — CELE 13 findViewById
    // ==================================================================================
    // CE FACE: leagă fiecare câmp de widget-ul cu ID-ul corespunzător.
    // CUM: `findViewById(R.id.x)` pentru fiecare.
    // RISC: un ID greșit întoarce `null` FĂRĂ eroare de compilare. NPE-ul apare la
    //   primul acces, undeva departe. De aceea toate sunt grupate aici.
    // REF: ID-urile din `activity_item.xml`.
    // ==================================================================================
    private void initControls() {

        // 1. Titlu.
        etTitle = findViewById(R.id.etTitle);

        // 2. Data.
        etRelease = findViewById(R.id.etRelease);

        // 3. Genul.
        spGenre = findViewById(R.id.spGenre);

        // 4. Bugetul.
        etBudget = findViewById(R.id.etBudget);

        // 5. Durata.
        sbDuration = findViewById(R.id.sbDuration);

        // 6. Rating-ul.
        rbRating = findViewById(R.id.rbRating);

        // 7. Ghidajul.
        rgApproval = findViewById(R.id.rgApproval);

        // 8. Bifa. ID-ul are „On" mare, câmpul are „on" mic: `cbOnWatchList` vs
        //    `cbonWatchList`. O greșeală de tastare aici dă NPE la fillForm.
        cbonWatchList = findViewById(R.id.cbOnWatchList);

        // 9. Switch-ul.
        swWatched = findViewById(R.id.swWatched);

        // 10. Posterul.
        etPoster = findViewById(R.id.etPoster);

        // 11. Butonul. ID-ul este `btnMovieAction`, câmpul `btMovieAction`.
        btMovieAction = findViewById(R.id.btnMovieAction);

        // 12. Eticheta de durată.
        tvDurationValue = findViewById(R.id.tvDurationValue);

        // 13. Eticheta de switch.
        tvWatchedValue = findViewById(R.id.tvWatchedValue);
    }

    // ==================================================================================
    // initListeners — CEI 4 LISTENERI
    // ==================================================================================
    // CE FACE: leagă evenimentele de metode.
    // CUM: click pe dată, click pe buton, schimbare switch, mișcare slider.
    // RISC: listener-ii sunt clase anonime; `this` din interior NU este activitatea.
    // REF: `saveMovie()` și `showReleaseDatePicker()` sunt metodele apelate.
    // ==================================================================================
    private void initListeners() {

        // 1. Click pe câmpul de dată -> dialog.
        //    `EditText` nu are eveniment „click" dedicat; `OnClickListener` funcționează
        //    pentru că EditText este un View.
        etRelease.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showReleaseDatePicker();
            }
        });

        // 2. Click pe buton -> salvare.
        btMovieAction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveMovie();
            }
        });

        // 3. Switch -> eticheta „Yes"/„No".
        //    `OnCheckedChangeListener` este apelat și când schimbarea vine din COD
        //    (`setChecked` în fillForm), nu doar de la utilizator.
        swWatched.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(@NonNull CompoundButton buttonView, boolean isChecked) {
                // Ternary: o singură expresie pentru ambele stări.
                tvWatchedValue.setText(isChecked ? "Yes" : "No");
            }
        });

        // 4. Slider -> eticheta de durată.
        sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            // 4a. La fiecare schimbare de progres — inclusiv când vine din cod.
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // `progress` este int; concatenarea cu String îl convertește automat.
                tvDurationValue.setText(progress + " min.");
            }

            // 4b. La atingerea sliderului. Nu avem nevoie de nimic aici.
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            // 4c. La ridicarea degetului. Nu avem nevoie de nimic aici.
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });
    }

    // ==================================================================================
    // saveMovie — WIDGET-URI -> MODEL -> INTENT
    // ==================================================================================
    // CE FACE: construiește un `Movie` din valorile formularului, îl pune într-un
    //   Intent și îl trimite înapoi în MainActivity.
    // CUM: 1) new Movie(); 2) 9 setter-e; 3) buclă pentru ghidaj; 4) putExtra;
    //   5) setResult + finish.
    // RISC: `Double.parseDouble("")` aruncă `NumberFormatException`; `releaseCal`
    //   poate conține o dată veche (vezi BUG 3).
    // REF: perechea inversă a lui `fillForm`.
    // ==================================================================================
    private void saveMovie() {

        // 1. Obiect gol. Aici se vede de ce constructorul fără parametri este obligatoriu.
        Movie movie = new Movie();

        // 2. Titlul, direct din text.
        movie.setTitle(etTitle.getText().toString());

        // 3. Data — din CALENDAR, nu din text.
        movie.setRelease(releaseCal.getTime());

        // 4. Genul — textul selectat în Spinner.
        movie.setGenre(spGenre.getSelectedItem().toString());

        // 5. Bugetul — parsare. BUG 1: dacă utilizatorul lasă câmpul gol,
        //    `Double.parseDouble("")` aruncă `NumberFormatException` și aplicația se închide.
        movie.setBudget(Double.parseDouble(etBudget.getText().toString()));

        // 6. Durata — direct din progres.
        movie.setDuration(sbDuration.getProgress());

        // 7. Rating-ul.
        movie.setRating(rbRating.getRating());

        // 8. Switch-ul.
        movie.setWatched(swWatched.isChecked());

        // 9. Bifa.
        movie.setOnWatchlist(cbonWatchList.isChecked());

        // 10. Posterul. Poate fi un string gol dacă utilizatorul nu a scris nimic.
        movie.setPosterUrl(etPoster.getText().toString());

        // 11. Ghidajul: parcurgem grupul și luăm textul butonului bifat.
        for(int index=0; index<rgApproval.getChildCount(); index++)
        {
            RadioButton rb = (RadioButton) rgApproval.getChildAt(index);

            // `isChecked()` — un singur buton poate fi bifat în RadioGroup.
            if(rb.isChecked())
            {
                movie.setApproval(rb.getText().toString());

                // Am găsit butonul; nu mai căutăm.
                break;
            }
        }

        // 12. Intent FĂRĂ target. Nu pornim o activitate; doar transportăm date
        //     înapoi. `new Intent()` este suficient pentru `setResult`.
        Intent intent = new Intent();

        // 13. Obiectul, serializat automat.
        intent.putExtra(MainActivity.MOVIE_EXTRA, movie);

        // 14. Poziția, DOAR în modul edit. În insert, cheia lipsește, iar
        //     `getIntExtra(..., -1)` din MainActivity întoarce -1.
        if (position != -1)
            intent.putExtra(MainActivity.POSITION_EXTRA, position);

        // 15. Rezultatul. Fără acest apel, MainActivity ar primi RESULT_CANCELED.
        setResult(RESULT_OK, intent);

        // 16. Închiderea activității. Fără ea, formularul rămâne pe ecran.
        finish();
    }

    // ==================================================================================
    // showReleaseDatePicker — DIALOGUL DE DATĂ
    // ==================================================================================
    // CE FACE: deschide un `DatePickerDialog` poziționat pe data din `releaseCal`.
    // CUM: 1) încearcă să parseze textul curent; 2) deschide dialogul; 3) la confirmare,
    //   scrie în calendar și în text.
    // RISC: textul tastat manual nu ajunge în calendar decât dacă dialogul este deschis.
    // REF: singurul loc care scrie în `releaseCal` după inițializare.
    // ==================================================================================
    private void showReleaseDatePicker() {

        // 1. Textul curent din câmp.
        String current = etRelease.getText().toString();

        // 2. Dacă nu este gol, încearcă să îl transforme în Date.
        if (!current.isEmpty()) {
            try {
                // `parse` întoarce `null` dacă textul nu poate fi interpretat.
                Date parsed = dateFormat.parse(current);

                // Dacă avem o dată validă, o punem în calendar.
                if (parsed != null)
                    releaseCal.setTime(parsed);

            // 3. Text invalid: ignorăm. Dialogul se deschide pe data veche.
            } catch (ParseException ignored) { }
        }

        // 4. Dialogul. Constructorul cere: Context, listener, an, lună, zi.
        new DatePickerDialog(
                this,

                // 4a. Listener-ul de confirmare.
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {

                        // Scriem în calendar. `month` este 0-based, exact cum îl vrea Calendar.
                        releaseCal.set(year, month, day);

                        // Curățăm o eventuală eroare afișată pe câmp.
                        etRelease.setError(null);

                        // Actualizăm textul afișat din calendar.
                        etRelease.setText(dateFormat.format(releaseCal.getTime()));
                    }
                },

                // 4b. Valorile inițiale: din calendar, nu din text.
                releaseCal.get(Calendar.YEAR),
                releaseCal.get(Calendar.MONTH),
                releaseCal.get(Calendar.DAY_OF_MONTH)

        // 5. `show()` — fără el, dialogul este construit dar nu apare.
        ).show();
    }
}
```

### 30.4.1 Cele trei bug-uri reale

**BUG 1 — buget gol.**

```
etBudget gol  ->  getText().toString() = ""
              ->  Double.parseDouble("")  ->  NumberFormatException
              ->  aplicația se închide (dacă excepția nu este prinsă)
```

Utilizatorul apasă „Save Movie" fără să completeze bugetul. Formularul nu validează nimic. Soluția corectă ar fi o verificare înainte de `parseDouble`, plus `etBudget.setError(...)`.

**BUG 2 — dată `null` la editare.**

```
Movie cu release == null  ->  fillForm  ->  dateFormat.format(null)
                          ->  NullPointerException
```

Se poate întâmpla dacă un film a fost creat cu `setRelease(null)` sau dacă datele vin dintr-o sursă externă. În aplicația de față nu se întâmplă, pentru că `saveMovie` scrie mereu `releaseCal.getTime()`.

**BUG 3 — data se pierde la editare fără atingerea câmpului.**

Acesta este cel mai subtil și merită urmărit pas cu pas:

```
1. Click pe rândul „Inception" (release = 16/07/2010)
2. ItemActivity.onCreate -> fillForm(existing)
      etRelease.setText("16/07/2010")     <- doar TEXTUL
      releaseCal rămâne data de AZI       <- din Calendar.getInstance()
3. Utilizatorul schimbă doar titlul și apasă „Update Movie"
4. saveMovie -> movie.setRelease(releaseCal.getTime())  -> data de AZI
```

Filmul își pierde data de lansare fără ca utilizatorul să atingă câmpul. Corect ar fi ca `fillForm` să facă și `releaseCal.setTime(existing.getRelease())`. Metoda `showReleaseDatePicker` repară problema **doar** dacă utilizatorul deschide dialogul, pentru că acolo textul este parsat în calendar.

### 30.4.2 Fluxul formularului, în două moduri

```
INSERT                                  EDIT
------                                  ----
Intent fără MOVIE_EXTRA                 Intent cu MOVIE_EXTRA + POSITION_EXTRA
      |                                       |
existing == null                        existing != null
      |                                       |
position = -1                           position = 0 (sau alt index)
formular gol                            fillForm(existing)
buton: "Save Movie"                     buton: "Update Movie"
      |                                       |
saveMovie()                             saveMovie()
      |                                       |
Intent: doar MOVIE_EXTRA                Intent: MOVIE_EXTRA + POSITION_EXTRA
      |                                       |
MainActivity: position == -1            MainActivity: position == 0
movies.add(movie)                       movies.set(0, movie)
```

### 30.4.3 De ce `releaseCal` și nu textul din `EditText`

```
Utilizatorul poate:
  A. alege data din dialog        -> releaseCal este actualizat, textul este actualizat
  B. tasta manual în câmp        -> textul se schimbă, releaseCal NU
  C. nu atinge câmpul            -> textul rămâne ce era, releaseCal rămâne ce era

saveMovie citește mereu releaseCal.
  A -> corect
  B -> data tastată este IGNORATĂ (se salvează ce era în calendar)
  C -> corect în insert, GREȘIT în edit (vezi BUG 3)
```

De aceea `EditText`-ul are `inputType="date"` și un listener de click: intenția este să fie folosit doar prin dialog, nu prin tastare.

---

## 30.5 `AndroidManifest.xml` — harta componentelor

30 de linii. Nu conține cod, nu conține date: declară **ce componente are aplicația** și cu ce temă pornește. Este singurul fișier care trebuie să știe de existența ambelor activități.

```xml
<!-- ====================================================================================== -->
<!-- FIȘIER: AndroidManifest.xml — Harta componentelor -->
<!-- ====================================================================================== -->
<!-- CE ESTE: declarația aplicației către sistemul Android. Spune ce activități există, -->
<!-- care este cea de start, cu ce temă pornește și ce iconiță are. -->
<!-- DE CE EXISTĂ: fără manifest, Android nu știe că aplicația are o activitate de lansat. -->
<!-- `startActivity(new Intent(this, ItemActivity.class))` ar arunca -->
<!-- `ActivityNotFoundException` dacă ItemActivity nu ar fi declarată aici. -->
<!-- CE NU FACE: nu conține cod, nu conține date, nu știe ce câmpuri are `Movie`. -->
<!-- Nu declară permisiuni — aplicația nu are nevoie de niciuna. -->
<!-- DIFERENȚA FAȚĂ DE G1097: o singură linie, `android:theme`. Restul este identic. -->
<!-- ====================================================================================== -->

<!-- Declarația XML. Trebuie să fie primul lucru din fișier în varianta reală. -->
<?xml version="1.0" encoding="utf-8"?>

<!-- MANIFEST — rădăcina. -->
<!-- xmlns:android  -> namespace-ul atributelor de framework. -->
<!-- xmlns:tools    -> namespace-ul atributelor pentru Android Studio. -->
<!-- AICI este declarat, dar NEUTILIZAT: niciun atribut `tools:` nu -->
<!-- apare în fișier. Este inofensiv, dar este un import mort la nivel -->
<!-- de XML. În `activity_main.xml` şi `activity_item.xml` este folosit -->
<!-- pentru `tools:context`. -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- APPLICATION — aplicația în ansamblu. Un singur element per APK. -->
    <!-- Nu are `android:name`: nu există o clasă Application personalizată. -->
    <application

        <!-- Backup automat al datelor aplicației. Aici nu există date de salvat, -->
        <!-- dar atributul rămâne din șablonul de proiect. -->
        android:allowBackup="true"

        <!-- Regulile de extragere a datelor pentru Android 12+. Fișierul este în -->
        <!-- res/xml/data_extraction_rules.xml. -->
        android:dataExtractionRules="@xml/data_extraction_rules"

        <!-- Regulile de backup pentru versiunile anterioare Android 12. -->
        android:fullBackupContent="@xml/backup_rules"

        <!-- Iconița aplicației, din res/mipmap. -->
        android:icon="@mipmap/ic_launcher"

        <!-- Numele afișat sub iconiță, din res/values/strings.xml. -->
        android:label="@string/app_name"

        <!-- Iconița rotundă, pentru launcher-ele care o cer. -->
        android:roundIcon="@mipmap/ic_launcher_round"

        <!-- Suport pentru layout oglindit în limbile RTL. -->
        android:supportsRtl="true"

        <!-- TEMA. Singura diferență față de G1097: acolo `Theme.G1097`. -->
        <!-- Tema este definită în res/values/themes.xml și res/values-night/themes.xml. -->
        android:theme="@style/Theme.G1098">

        <!-- ACTIVITATEA 1: MainActivity — ecranul de start. -->
        <!-- `android:name=".activities.MainActivity"` este un nume RELATIV la pachetul -->
        <!-- aplicației (namespace-ul din build.gradle.kts). Punctul de la început -->
        <!-- înseamnă „pachetul aplicației". -->
        <!-- `android:exported="true"` — OBLIGATORIU pentru activitatea cu intent-filter -->
        <!-- de la Android 12 încoace. `true` înseamnă că alte aplicații (launcher-ul) -->
        <!-- o pot porni. Fără atribut, build-ul pică. -->
        <!-- `android:windowSoftInputMode="adjustResize"` — când apare tastatura, fereastra -->
        <!-- se micșorează, ca ScrollView-ul să poată derula până la câmpul activ. -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!-- INTENT FILTER — ce fel de intent-uri poate primi activitatea. -->
            <!-- MAIN + LAUNCHER = „aceasta este aplicația care apare în launcher". -->
            <!-- O singură activitate din aplicație are acest filtru. -->
            <intent-filter>

                <!-- Acțiunea principală. -->
                <action android:name="android.intent.action.MAIN" />

                <!-- Categoria care o face vizibilă în launcher. -->
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ACTIVITATEA 2: ItemActivity — formularul. -->
        <!-- `android:exported="false"` — este pornită DOAR din interiorul aplicației, -->
        <!-- prin Intent explicit. Nicio altă aplicație nu o poate lansa. -->
        <!-- Nu are intent-filter: nu are sens să fie descoperită din exterior. -->
        <!-- Are același `windowSoftInputMode`, pentru că are și ea câmpuri de text. -->
        <activity
            android:name=".activities.ItemActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**Tabel de referință — atributele din manifest:**

| Atribut | Valoare | Efect |
|---|---|---|
| `android:allowBackup` | `true` | permite backup-ul datelor aplicației |
| `android:theme` | `@style/Theme.G1098` | tema Material, definită în `themes.xml` |
| `android:exported` (Main) | `true` | launcher-ul o poate porni |
| `android:exported` (Item) | `false` | doar aplicația o poate porni |
| `android:windowSoftInputMode` | `adjustResize` | tastatura micșorează fereastra |
| `android:name` | `.activities.X` | nume relativ la pachetul aplicației |

**De ce nu există `package=`:** în versiunile moderne de Android Gradle Plugin, numele pachetului se declară în `build.gradle.kts` (`namespace = "ro.ase.ie.g1098"`), nu în manifest. Atributul `package` a fost eliminat din șablon.

---

## 30.6 `activity_main.xml` — ecranul listei

26 de linii. Un `FrameLayout` cu exact doi copii: lista (dedesubt) și FAB-ul (deasupra).

```xml
<!-- ====================================================================================== -->
<!-- FIȘIER: activity_main.xml — ECRANUL CU LISTA -->
<!-- ====================================================================================== -->
<!-- CE ESTE: un FrameLayout cu exact doi copii: ListView (umple tot) și FAB (peste el). -->
<!-- DE CE ATÂT DE PUȚIN: toată complexitatea este în `activity_item.xml` (formularul). -->
<!-- Aici doar scheletul listei. -->
<!-- STRUCTURA: -->
<!-- FrameLayout (id=main) -->
<!-- |== ListView (id=listView)            <- primul copil = desenat primul = dedesubt -->
<!-- +== FloatingActionButton (id=...)     <- al doilea copil = desenat peste listă -->
<!-- ORDINEA COPIILOR ESTE SEMNIFICAȚIE, NU STIL: în FrameLayout, fiecare copil este -->
<!-- desenat peste cel anterior. Inversate, lista ar acoperi butonul. -->
<!-- DIFERENȚA FAȚĂ DE G1097: un singur atribut — `app:srcCompat` al FAB-ului folosește -->
<!-- `@drawable/outline_add_2_24` în loc de `@drawable/outline_add_24`. -->
<!-- ====================================================================================== -->

<!-- Declarația XML. -->
<?xml version="1.0" encoding="utf-8"?>

<!-- FRAMELAYOUT — containerul rădăcină. -->
<!-- DE CE FrameLayout și nu LinearLayout: copiii trebuie să se SUPRApună. Un LinearLayout -->
<!-- i-ar pune unul lângă altul (sau unul sub altul), iar FAB-ul nu ar mai pluti peste listă. -->
<!-- DE CE nu ConstraintLayout: pentru doi copii, un FrameLayout este mai simplu și mai ieftin. -->
<!-- ATRIBUTE, PE RÂND: -->
<!-- xmlns:android   -> atributele framework-ului (layout_width, text, id...) -->
<!-- xmlns:app       -> atributele bibliotecilor (Material, AndroidX) -->
<!-- xmlns:tools     -> atribute care există DOAR în preview-ul Android Studio -->
<!-- și sunt ELIMINATE la build. Nu ajung niciodată în APK. -->
<!-- android:id      -> @+id/main; `@+id/` CREEAZĂ ID-ul, `@id/` îl REFERĂ pe unul existent -->
<!-- layout_width    -> match_parent: ocupă toată lățimea părintelui -->
<!-- layout_height   -> match_parent: ocupă toată înălțimea -->
<!-- orientation     -> ATRIBUT INVALID pe FrameLayout; există doar pe LinearLayout. -->
<!-- Este IGNORAT de Android și produce un warning de lint -->
<!-- („Unknown attribute"). Rămășiță de la un LinearLayout anterior. -->
<!-- tools:context   -> doar pentru preview; îi spune lui Android Studio ce activitate -->
<!-- să folosească pentru temă. Eliminat la build. -->
<!-- DE CE `android:id="@+id/main"` ESTE OBLIGATORIU: codul face `findViewById(R.id.main)` -->
<!-- pentru listener-ul de insets. Fără acest ID, apelul ar întoarce `null` și -->
<!-- `setOnApplyWindowInsetsListener(null, ...)` ar arunca NPE. -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!-- LISTVIEW — lista derulantă. -->
    <!-- DE CE ListView și nu RecyclerView: la acest commit se predă ListView-ul clasic. -->
    <!-- RecyclerView apare în laboratorul următor. -->
    <!-- ATRIBUTE: -->
    <!-- android:id              -> listView; folosit de `findViewById` în initControls -->
    <!-- layout_width/height     -> match_parent pe ambele axe: lista ocupă tot ecranul, -->
    <!-- inclusiv zona de sub FAB. FAB-ul este desenat PESTE -->
    <!-- listă, nu listă pe lângă el. -->
    <!-- android:entries         -> umple lista din XML cu elementele din `@array/items`. -->
    <!-- LA RUNTIME, `listView.setAdapter(movieAdapter)` -->
    <!-- ÎNLOCUIEȘTE complet acest adapter. `entries` rămâne -->
    <!-- doar pentru ca preview-ul să arate o listă plină. -->
    <!-- Costul la runtime este zero după `setAdapter`. -->
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/items" />

    <!-- FLOATING ACTION BUTTON — butonul „+". -->
    <!-- Numele complet este necesar pentru că este o clasă din biblioteca Material, -->
    <!-- nu una din framework. Prefixul `com.google.android.material...` este calea clasei. -->
    <!-- ATRIBUTE: -->
    <!-- android:id          -> floatingActionButton; căutat în initControls -->
    <!-- layout_width/height -> wrap_content: FAB-ul are o dimensiune fixă impusă de stil -->
    <!-- (56dp implicit). `match_parent` l-ar întinde pe tot ecranul. -->
    <!-- android:layout_gravity -> poziția ACESTUI COPIL în PĂRINTELE lui (FrameLayout). -->
    <!-- android:layout_margin  -> 16dp pe toate laturile. Împreună cu padding-ul de insets -->
    <!-- aplicat pe `R.id.main`, butonul stă la 16dp de zona -->
    <!-- sigură, nu de marginea fizică. -->
    <!-- android:contentDescription -> textul citit de TalkBack. OBLIGATORIU pentru -->
    <!-- elementele fără text vizibil; fără el, lint-ul dă -->
    <!-- eroare („ContentDescription"), iar utilizatorii cu -->
    <!-- cititor de ecran aud doar „buton". -->
    <!-- app:srcCompat       -> varianta compatibilă pentru imagini vectoriale. -->
    <!-- `android:src` ar funcționa pe API 21+, dar `srcCompat` -->
    <!-- este recomandarea AndroidX și singura care suportă -->
    <!-- vectori pe toate versiunile. -->
    <!-- DIFERENȚA FAȚĂ DE G1097: `@drawable/outline_add_2_24` vs `@drawable/outline_add_24`. -->
    <!-- Ambele fișiere există, dar în proiecte diferite. Dacă muți XML-ul fără drawable, -->
    <!-- build-ul pică cu „resource drawable/outline_add_2_24 not found". -->
    <!-- ================================================================================== -->
    <!-- layout_gravity  vs  gravity -->
    <!-- ================================================================================== -->
    <!-- gravity         = cum își aranjează ELEMENTUL copiii lui în interior -->
    <!-- layout_gravity  = cum este aranjat ELEMENTUL în părintele lui -->
    <!-- Exemplu: un TextView cu `gravity="center"` își centrează TEXTUL. -->
    <!-- Un TextView cu `layout_gravity="center"` este centrat ÎN PĂRINTE. -->
    <!-- `bottom|end` = jos, dreapta. `end` respectă direcția de citire: în RTL devine -->
    <!-- stânga. `right` ar fi fost fix și ar fi greșit în RTL. -->
    <!-- DE CE funcționează aici: FrameLayout respectă `layout_gravity` pe copii. -->
    <!-- ================================================================================== -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_2_24" />

</FrameLayout>
```

**Tabel de referință pentru atributele din acest fișier:**

| Atribut | Valoare | Efect |
|---|---|---|
| `android:id` | `@+id/main` | creează ID-ul folosit de insets |
| `android:layout_width/height` | `match_parent` | umple părintele |
| `android:orientation` | `horizontal` | **invalid** pe FrameLayout, ignorat |
| `android:entries` | `@array/items` | listă de preview, înlocuită la runtime |
| `android:layout_gravity` | `bottom\|end` | poziționează FAB-ul în FrameLayout |
| `android:contentDescription` | `"Add"` | accesibilitate + lint |
| `app:srcCompat` | `@drawable/outline_add_2_24` | imagine vectorială compatibilă |
| `tools:context` | `.activities.MainActivity` | doar preview |

---

## 30.7 `activity_item.xml` — formularul

452 de linii, identice cu G1097. Patru carduri, un antet, un buton. Este cel mai lung fișier al aplicației și singurul care se memorează greu — de aceea structura contează mai mult decât fiecare atribut.

### 30.7.0 Trei reguli care se aplică în tot fișierul

**1. `?attr/` vs `@color/` vs `#RRGGBB`**

| Formă | Când se rezolvă | Se schimbă cu tema? | Când se folosește |
|---|---|---|---|
| `?attr/colorPrimary` | la runtime, din tema curentă | **da** | orice culoare semantică |
| `@color/my_color` | la build, din `colors.xml` | nu | culori fixe ale brandului |
| `#FFC107` | la build, literal | nu | excepții asumate (stelele) |
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

### 30.7.1 Fișierul adnotat

```xml
<!-- ====================================================================================== -->
<!-- FIȘIER: activity_item.xml — FORMULARUL DE INSERT / EDIT -->
<!-- ====================================================================================== -->
<!-- CE ESTE: un ScrollView cu un singur copil (LinearLayout vertical), care conține -->
<!-- un antet, patru carduri și un buton. -->
<!-- DE CE EXISTĂ: este ecranul în care utilizatorul introduce datele unui film. -->
<!-- CINE ÎL FOLOSEȘTE: ItemActivity, prin `setContentView(R.layout.activity_item)`. -->
<!-- CE NU FACE: nu validează, nu salvează, nu știe ce este un `Movie`. -->
<!-- STRUCTURA (4 carduri + antet + buton): -->
<!-- ScrollView (id=main) -->
<!-- +== LinearLayout vertical -->
<!-- |== TextView  "Movie details"               <- titlu -->
<!-- |== TextView  "Fill in the information..."  <- subtitlu -->
<!-- |== MaterialCardView  [Basics]              <- titlu, gen, dată -->
<!-- |== MaterialCardView  [Production]          <- buget, durată -->
<!-- |== MaterialCardView  [Your verdict]        <- rating, switch, bifă, ghidaj -->
<!-- |== MaterialCardView  [Poster]              <- URL -->
<!-- +== MaterialButton    "Save Movie"          <- acțiunea -->
<!-- DE CE CARDURI: împart un formular lung în secțiuni vizuale. Fiecare card are -->
<!-- aceeași rețetă: fundal de suprafață, colțuri 20dp, padding intern 16dp. -->
<!-- ====================================================================================== -->

<!-- Declarația XML. -->
<?xml version="1.0" encoding="utf-8"?>

<!-- SCROLLVIEW — rădăcina. -->
<!-- DE CE ScrollView: formularul este mai înalt decât ecranul. Fără el, ultimele -->
<!-- câmpuri ar fi inaccesibile. -->
<!-- REGULA: ScrollView are EXACT UN copil. Dacă pui doi, primești eroare la inflate -->
<!-- („ScrollView can host only one direct child"). -->
<!-- ATRIBUTE: -->
<!-- android:id="@+id/main"        -> căutat de listener-ul de insets din ItemActivity -->
<!-- android:fillViewport="true"   -> copilul este întins cel puțin la înălțimea -->
<!-- viewport-ului, chiar dacă conținutul e mai scurt -->
<!-- android:background="?attr/colorSurface" -> fundalul temei, nu alb fix -->
<!-- tools:context                 -> doar preview -->
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <!-- LINEARLAYOUT VERTICAL — singurul copil al ScrollView. -->
    <!-- Aici stau toate secțiunile, una sub alta. -->
    <!-- `paddingHorizontal` + `paddingTop/Bottom` = 16dp lateral, 24dp sus/jos. -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- Header -->
        <!-- TITLUL ECRANULUI, varianta din interiorul paginii. -->
        <!-- `textAppearanceHeadlineMedium` este un rol de tipografie Material: -->
        <!-- mărime, greutate și spațiere consecvente cu restul aplicației. -->
        <!-- `?attr/colorOnSurface` = culoarea de text potrivită pentru suprafața curentă. -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Movie details"
            android:textAppearance="?attr/textAppearanceHeadlineMedium"
            android:textColor="?attr/colorOnSurface"
            android:textStyle="bold" />

        <!-- SUBTITLUL. `colorOnSurfaceVariant` este o nuanță mai slabă, pentru text -->
        <!-- secundar. `layout_marginBottom="20dp"` desparte antetul de primul card. -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"
            android:layout_marginBottom="20dp"
            android:text="Fill in the information below and save."
            android:textAppearance="?attr/textAppearanceBodyMedium"
            android:textColor="?attr/colorOnSurfaceVariant" />

        <!-- ============================================================================ -->
        <!-- BLOC: MaterialCardView — cele trei stiluri folosite în acest fișier          -->
        <!-- ============================================================================ -->
        <!-- `?attr/materialCardViewFilledStyle`  = fundal umplut, fără contur.           -->
        <!-- `?attr/materialCardViewOutlinedStyle` = fundal transparent, cu contur.       -->
        <!-- `?attr/materialCardViewElevatedStyle` = fundal ridicat, cu umbră.            -->
        <!-- Aici: primele trei carduri sunt FILLED, cardul Spinner-ului este OUTLINED.   -->
        <!-- `app:cardCornerRadius` suprascrie colțul din stil.                           -->
        <!-- `app:strokeColor` are sens doar pe stilul outlined.                          -->
        <!-- ============================================================================ -->
        <!-- ============ CARD 1: Basics ============ -->
        <!-- CARDUL 1 — titlu, gen, dată. -->
        <!-- `style="?attr/materialCardViewFilledStyle"` = fundal umplut, fără contur. -->
        <!-- `app:cardCornerRadius="20dp"` suprascrie colțul implicit al stilului. -->
        <!-- `layout_marginBottom="16dp"` = spațiul dintre carduri. -->
        <com.google.android.material.card.MaterialCardView
            style="?attr/materialCardViewFilledStyle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="20dp">

            <!-- Conținutul cardului: un LinearLayout vertical cu padding 16dp. -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <!-- Titlul secțiunii. `colorPrimary` îl face vizibil ca titlu de card. -->
                <!-- `textAppearanceTitleMedium` = mai mic decât titlul ecranului. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Basics"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Title -->
                <!-- ETICHETA CÂMPULUI. Are ID (`tvTile`), dar codul NU o folosește: -->
                <!-- este doar pentru lizibilitate și pentru eventuale teste. -->
                <!-- `textAppearanceLabelLarge` = etichetă mică, majuscule în temă. -->
                <TextView
                    android:id="@+id/tvTile"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Title"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- TEXTINPUTLAYOUT — învelișul câmpului de titlu. -->
                <!-- `OutlinedBox` = contur vizibil în jurul câmpului. -->
                <!-- `app:hintEnabled="false"` = fără etichetă plutitoare; eticheta este -->
                <!-- TextView-ul de deasupra. -->
                <!-- `app:endIconMode="clear_text"` = adaugă un X care golește câmpul. -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="16dp"
                    app:hintEnabled="false"
                    app:endIconMode="clear_text">

                    <!-- CÂMPUL PROPRIU-ZIS. ID-ul `etTitle` este căutat în initControls. -->
                    <!-- `inputType="textCapWords"` = tastatura pornește cu majusculă -->
                    <!-- la fiecare cuvânt. Nu este validare, doar confort. -->
                    <com.google.android.material.textfield.TextInputEditText
                        android:id="@+id/etTitle"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:hint="Movie title"
                        android:inputType="textCapWords" />
                </com.google.android.material.textfield.TextInputLayout>

                <!-- Genre -->
                <!-- Eticheta pentru Spinner. ID `tvGenre`, nefolosit în cod. -->
                <TextView
                    android:id="@+id/tvGenre"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Genre"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- SPINNER-UL ESTE ÎNVELIT ÎNTR-UN CARD. -->
                <!-- DE CE: Spinner-ul nu are contur propriu. Cardul îi dă bordura -->
                <!-- și colțurile, ca să arate ca un câmp TextInput. -->
                <!-- `cardBackgroundColor="@android:color/transparent"` = fără fundal, -->
                <!-- doar contur. -->
                <!-- `strokeColor="?attr/colorOutline"` = culoarea de contur a temei. -->
                <!-- `layout_height="56dp"` = înălțimea standard a unui câmp Material. -->
                <com.google.android.material.card.MaterialCardView
                    style="?attr/materialCardViewOutlinedStyle"
                    android:layout_width="match_parent"
                    android:layout_height="56dp"
                    android:layout_marginBottom="16dp"
                    app:cardBackgroundColor="@android:color/transparent"
                    app:cardCornerRadius="4dp"
                    app:strokeColor="?attr/colorOutline">

                    <!-- SPINNER-UL. `entries="@array/movie_genre"` umple lista din XML. -->
                    <!-- `spinnerMode="dropdown"` = lista se deschide ca un popup, -->
                    <!-- nu ca un dialog modal. -->
                    <!-- ID-ul `spGenre` este căutat în initControls și folosit în -->
                    <!-- fillForm (setSelection) și saveMovie (getSelectedItem). -->
                    <Spinner
                        android:id="@+id/spGenre"
                        android:layout_width="match_parent"
                        android:layout_height="match_parent"
                        android:entries="@array/movie_genre"
                        android:paddingStart="4dp"
                        android:spinnerMode="dropdown" />
                </com.google.android.material.card.MaterialCardView>

                <!-- Release date -->
                <!-- CÂMPUL DE DATĂ. -->
                <!-- `hintEnabled="true"` = eticheta „Release date" plutește deasupra -->
                <!-- când câmpul are text. -->
                <!-- `startIconDrawable="@android:drawable/ic_menu_my_calendar"` = iconița -->
                <!-- de calendar din framework, în stânga. -->
                <!-- `startIconContentDescription` = textul citit de TalkBack pentru iconiță. -->
                <!-- ATENȚIE: `etRelease` NU este citit în saveMovie. Valoarea reală stă -->
                <!-- în `releaseCal`. Vezi BUG 3 din 30.4. -->
                <com.google.android.material.textfield.TextInputLayout
                    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:hintEnabled="true"
                    app:startIconContentDescription="Release date"
                    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

                    <!-- CÂMPUL. `inputType="date"` = tastatură numerică cu separatori. -->
                    <!-- Click-ul pe el deschide DatePickerDialog (listener în ItemActivity). -->
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
        <!-- CARDUL 2 — buget și durată. -->
        <!-- Aceeași rețetă ca primul card: stil filled, colț 20dp, padding 16dp. -->
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

                <!-- Budget -->
                <!-- Eticheta câmpului de buget. ID `tvBudget`, nefolosit în cod. -->
                <TextView
                    android:id="@+id/tvBudget"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Budget"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- CÂMPUL DE BUGET. -->
                <!-- `app:prefixText="$ "` = prefix afișat în interiorul câmpului, dar -->
                <!-- NU face parte din textul citit de `getText()`. -->
                <!-- `inputType="numberDecimal"` = tastatură numerică cu virgulă zecimală. -->
                <!-- BUG 1: dacă utilizatorul lasă câmpul gol, `Double.parseDouble("")` -->
                <!-- aruncă NumberFormatException în saveMovie. -->
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
                <!-- RÂNDUL DE DURATĂ: etichetă în stânga, valoare în dreapta. -->
                <!-- `gravity="center_vertical"` = aliniere pe verticala centrului. -->
                <!-- `orientation="horizontal"` = copiii stau unul lângă altul. -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:orientation="horizontal">

                    <!-- ETICHETA „Duration". -->
                    <!-- `layout_width="0dp"` + `layout_weight="1"` = ia tot spațiul rămas, -->
                    <!-- împingând valoarea în dreapta. -->
                    <TextView
                        android:id="@+id/tvDuration"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="Duration"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!-- VALOAREA DURATEI. Este actualizată din cod, în -->
                    <!-- `onProgressChanged`, cu `progress + " min."`. -->
                    <!-- `tools:text="148 min"` = valoare DOAR pentru preview; la runtime -->
                    <!-- textul pornește de la „0 min". -->
                    <TextView
                        android:id="@+id/tvDurationValue"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelLarge"
                        android:textColor="?attr/colorPrimary"
                        tools:text="148 min" />
                </LinearLayout>

                <!-- SEEKBAR-UL. -->
                <!-- `max="300"` și `min="0"` = intervalul. `min` este disponibil din API 26; -->
                <!-- pe versiuni mai vechi ar fi ignorat. -->
                <!-- `progressTint` și `thumbTint` = culoarea barei și a mânerului, din temă. -->
                <!-- `tools:progress="148"` = doar preview. -->
                <!-- ID-ul `sbDuration` este folosit în initControls, fillForm, saveMovie -->
                <!-- și în listener-ul de progres. -->
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

                <!-- RÂNDUL CU MIN/MAX: două etichete, „0 min" în stânga și „300 min" -->
                <!-- în dreapta. `paddingHorizontal="16dp"` le aliniază cu marginile -->
                <!-- barei, care are padding intern. -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal"
                    android:paddingHorizontal="16dp">

                    <!-- Minimul. `0dp` + `weight=1` îl împinge pe celălalt în dreapta. -->
                    <TextView
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="0 min"
                        android:textAppearance="?attr/textAppearanceLabelSmall"
                        android:textColor="?attr/colorOnSurfaceVariant" />

                    <!-- Maximul. -->
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
        <!-- CARDUL 3 — rating, switch, bifă, ghidaj. Cel mai complex card: -->
        <!-- conține două separatoare și un RadioGroup derulabil orizontal. -->
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
                    android:text="Your verdict"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- Rating -->
                <!-- Eticheta rating-ului. ID `tvRating`, nefolosit în cod. -->
                <TextView
                    android:id="@+id/tvRating"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Rating"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- RATINGBAR — stelele. -->
                <!-- `numStars="5"` = cinci stele. -->
                <!-- `stepSize="0.5"` = jumătăți de stea. Fără el, doar stele întregi. -->
                <!-- `progressTint="#FFC107"` = galben literal, nu din temă. Este o -->
                <!-- excepție asumată: culoarea stelelor nu trebuie să se schimbe cu tema. -->
                <!-- `layout_gravity="center_horizontal"` = centrat în card. -->
                <!-- ID-ul `rbRating` este folosit în initControls, fillForm, saveMovie. -->
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

                <!-- SEPARATOR — o linie de 1dp. -->
                <!-- `View` gol, folosit doar pentru linie. `colorOutlineVariant` este -->
                <!-- culoarea de separare a temei. -->
                <!-- `layout_marginVertical="12dp"` = spațiu sus și jos. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Recommended -->
                <!-- RÂNDUL „Recommended": text în stânga, switch și bifă în dreapta. -->
                <!-- `minHeight="48dp"` = ținta minimă de atingere recomandată de Material. -->
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:gravity="center_vertical"
                    android:minHeight="48dp"
                    android:orientation="horizontal">

                    <!-- COLOANA DE TEXT: două TextView-uri verticale. -->
                    <!-- `0dp` + `weight=1` = ocupă tot spațiul liber, împingând -->
                    <!-- controalele în dreapta. -->
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:orientation="vertical">

                        <!-- Eticheta principală. -->
                        <TextView
                            android:id="@+id/tvWatched"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Recommended"
                            android:textAppearance="?attr/textAppearanceBodyLarge"
                            android:textColor="?attr/colorOnSurface" />

                        <!-- VALOAREA SWITCH-ULUI, ca text. Este actualizată din listener-ul -->
                        <!-- `onCheckedChanged` cu „Yes"/„No". Pornește de la „No". -->
                        <TextView
                            android:id="@+id/tvWatchedValue"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="No"
                            android:textAppearance="?attr/textAppearanceLabelLarge"
                            android:textColor="?attr/colorPrimary" />
                    </LinearLayout>

                    <!-- SWITCH-UL MATERIAL. ID `swWatched`, câmp `MaterialSwitch swWatched`. -->
                    <!-- ATENȚIE: nu este `android.widget.Switch`. De aceea importul -->
                    <!-- `android.widget.Switch` ar fi mort. -->
                    <com.google.android.material.materialswitch.MaterialSwitch
                        android:id="@+id/swWatched"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="12dp" />

                    <!-- BIFA „Watchlist". ID `cbOnWatchList` (cu „On" mare). -->
                    <!-- Tipul din XML este MaterialCheckBox; câmpul din cod este -->
                    <!-- declarat `CheckBox` — MaterialCheckBox extinde CheckBox. -->
                    <com.google.android.material.checkbox.MaterialCheckBox
                        android:id="@+id/cbOnWatchList"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Watchlist" />
                </LinearLayout>

                <!-- Al doilea separator, identic cu primul. -->
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:layout_marginVertical="12dp"
                    android:background="?attr/colorOutlineVariant" />

                <!-- Guidance -->
                <!-- Eticheta grupului de ghidaj. ID `tvGuidance`, nefolosit în cod. -->
                <TextView
                    android:id="@+id/tvGuidance"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="4dp"
                    android:text="Guidance"
                    android:textAppearance="?attr/textAppearanceLabelLarge"
                    android:textColor="?attr/colorOnSurfaceVariant" />

                <!-- HORIZONTALSCROLLVIEW — permite derulare orizontală. -->
                <!-- DE CE: cinci butoane radio nu încap pe un ecran îngust. -->
                <!-- `scrollbars="none"` = fără bara de derulare vizibilă. -->
                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none">

                    <!-- ==================================================================== -->
                    <!-- BLOC: RadioGroup — de ce garantează selecția unică                   -->
                    <!-- ==================================================================== -->
                    <!-- Un RadioGroup urmărește ce buton este bifat și, când unul primește   -->
                    <!-- `android:checked="true"`, îl debifează automat pe celălalt.          -->
                    <!-- `check(id)` din cod face aceeași operație, programatic.              -->
                    <!-- De aceea fillForm poate face o singură potrivire și `break`.         -->
                    <!-- `getChildCount()` numără COPIII direcți, adică cei 5 radio-butoane.  -->
                    <!-- ==================================================================== -->
                    <!-- RADIOGROUP — garantează selecția unică. -->
                    <!-- `orientation="horizontal"` = butoanele stau pe un rând. -->
                    <!-- ID-ul `rgApproval` este folosit în initControls, fillForm, -->
                    <!-- saveMovie și în buclele de potrivire pe text. -->
                    <RadioGroup
                        android:id="@+id/rgApproval"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <!-- BUTONUL 1: „G". `android:checked="true"` = selectat implicit. -->
                        <!-- Acesta este motivul pentru care un formular gol are totuși -->
                        <!-- un ghidaj valid la salvare. -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbGeneral"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:checked="true"
                            android:text="G" />

                        <!-- BUTONUL 2: „PG". -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbParentGuidance"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG" />

                        <!-- BUTONUL 3: „PG-13". Textul este cheia de potrivire din fillForm. -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbPG13"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="PG-13" />

                        <!-- BUTONUL 4: „R". -->
                        <com.google.android.material.radiobutton.MaterialRadioButton
                            android:id="@+id/rbRestricted"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="R" />

                        <!-- BUTONUL 5: „NC-17". -->
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
        <!-- CARDUL 4 — URL-ul posterului. Singurul card cu un singur câmp. -->
        <!-- `layout_marginBottom="24dp"` = mai mult spațiu înainte de buton. -->
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

                <!-- Titlul secțiunii. -->
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="12dp"
                    android:text="Poster"
                    android:textAppearance="?attr/textAppearanceTitleMedium"
                    android:textColor="?attr/colorPrimary" />

                <!-- CÂMPUL DE POSTER. -->
                <!-- `endIconMode="clear_text"` = X de golire. -->
                <!-- `startIconDrawable="@android:drawable/ic_menu_gallery"` = iconiță -->
                <!-- de galerie din framework. -->
                <!-- `inputType="textUri"` = tastatură cu `/` și `.com`, potrivită pentru URL. -->
                <!-- ID-ul `etPoster` este folosit în initControls, fillForm, saveMovie. -->
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
        <!-- BUTONUL DE ACȚIUNE. -->
        <!-- `style="@style/Widget.Material3.Button"` = buton umplut, cu colțuri. -->
        <!-- `layout_height="60dp"` = mai înalt decât implicit, pentru atingere ușoară. -->
        <!-- `app:cornerRadius="30dp"` = colțuri complet rotunjite (jumătate din înălțime). -->
        <!-- `app:icon="@android:drawable/ic_menu_save"` = iconița de salvare. -->
        <!-- `app:iconGravity="textStart"` = iconița înaintea textului. -->
        <!-- ID-ul `btnMovieAction` este căutat în initControls; textul este schimbat -->
        <!-- în onCreate la „Update Movie" pentru modul edit. -->
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

### 30.7.2 Ierarhia de view-uri, pe scurt

```
ScrollView (main)
 |
 +-- LinearLayout (vertical)
      |
      +-- TextView "Movie details"
      +-- TextView "Fill in the information below and save."
      |
      +-- MaterialCardView [Basics]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Basics"
      |         +-- TextView "Title"  (tvTile)
      |         +-- TextInputLayout
      |         |    +-- TextInputEditText etTitle
      |         +-- TextView "Genre"  (tvGenre)
      |         +-- MaterialCardView
      |         |    +-- Spinner spGenre
      |         +-- TextInputLayout
      |              +-- TextInputEditText etRelease
      |
      +-- MaterialCardView [Production]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Production"
      |         +-- TextView "Budget"  (tvBudget)
      |         +-- TextInputLayout
      |         |    +-- TextInputEditText etBudget
      |         +-- LinearLayout (horizontal)
      |         |    +-- TextView "Duration" (0dp, weight=1)
      |         |    +-- TextView tvDurationValue
      |         +-- SeekBar sbDuration
      |         +-- LinearLayout (horizontal)
      |              +-- TextView "0 min" (0dp, weight=1)
      |              +-- TextView "300 min"
      |
      +-- MaterialCardView [Your verdict]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Your verdict"
      |         +-- TextView "Rating"  (tvRating)
      |         +-- RatingBar rbRating
      |         +-- View (separator)
      |         +-- LinearLayout (horizontal)
      |         |    +-- LinearLayout (vertical, 0dp, weight=1)
      |         |    |    +-- TextView "Recommended" (tvWatched)
      |         |    |    +-- TextView tvWatchedValue
      |         |    +-- MaterialSwitch swWatched
      |         |    +-- MaterialCheckBox cbOnWatchList
      |         +-- View (separator)
      |         +-- TextView "Guidance" (tvGuidance)
      |         +-- HorizontalScrollView
      |              +-- RadioGroup rgApproval
      |                   +-- MaterialRadioButton rbGeneral   "G"
      |                   +-- MaterialRadioButton rbParentGuidance "PG"
      |                   +-- MaterialRadioButton rbPG13      "PG-13"
      |                   +-- MaterialRadioButton rbRestricted "R"
      |                   +-- MaterialRadioButton rbNC17      "NC-17"
      |
      +-- MaterialCardView [Poster]
      |    +-- LinearLayout (vertical)
      |         +-- TextView "Poster"
      |         +-- TextInputLayout
      |              +-- TextInputEditText etPoster
      |
      +-- MaterialButton btnMovieAction "Save Movie"
```

---

## 30.8 Fluxul complet

### 30.8.1 Pornirea aplicației

```
LAUNCHER
  |
  |== Android citește AndroidManifest.xml
  |== găsește activitatea cu MAIN + LAUNCHER
  |== pornește .activities.MainActivity
        |
        v
  MainActivity.onCreate
    |== super.onCreate
    |== EdgeToEdge.enable
    |== setContentView(activity_main)
    |== insets pe R.id.main
    |== addSampleMovies()        -> 3 filme în listă
    |== movieAdapter = ArrayAdapter(simple_list_item_1, movies)
    |== initControls()           -> fabInsert, listView, setAdapter
    |== initListeners()          -> FAB + item click
    +== launcher = registerForActivityResult(...)
        |
        v
  onStart -> onResume
        |
        v
  ListView cere adapterului 3 rânduri
        |
        v
  ArrayAdapter.getView -> TextView.setText(movie.toString())
        |
        v
  ECRANUL ARATĂ 3 RÂNDURI
```

### 30.8.2 Insert — FAB

```
APASĂ „+"
  |
  |== fabInsert.onClick
  |== new Intent(MainActivity.this, ItemActivity.class)
  |== launcher.launch(intent)
        |
        v
  ItemActivity.onCreate
    |== setContentView(activity_item)
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

### 30.8.3 Edit — click pe rând

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

### 30.8.4 Obiectul care călătorește

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

### 30.8.5 Reciclarea rândurilor în ListView

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

## 30.9 Ce să reții din fiecare fișier

| Fișier | Esența | Capcana |
|---|---|---|
| `Movie.java` | POJO serializabil, 10 câmpuri, constructor gol explicit, `isX()` pentru booleeni, `toString()` complet | constructorul cu 10 parametri este POZIȚIONAL |
| `MainActivity.java` | ordinea din `onCreate`, `ArrayAdapter`, `registerForActivityResult`, `notifyDataSetChanged` | `launcher` este atribuit DUPĂ `initListeners` |
| `ItemActivity.java` | 13 `findViewById`, `releaseCal` ca sursă de adevăr, buclă generică pe `RadioGroup`, `setResult` + `finish` | buget gol -> crash; data se pierde la editare |
| `AndroidManifest.xml` | două activități, `exported` corect, tema | `exported="true"` obligatoriu pe activitatea cu intent-filter |
| `activity_main.xml` | `FrameLayout` + ordinea copiilor + `layout_gravity` pe FAB | `android:orientation` este invalid pe FrameLayout |
| `activity_item.xml` | `ScrollView` cu un copil, `MaterialCardView` ca secțiune, `TextInputLayout`, `Spinner` învelit | `hintEnabled` trebuie corelat cu existența etichetei |

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

### Cele 5 diferențe față de G1097 pe care trebuie să le poți spune

1. **`posterUrl` vs `poster`** — numele se propagă în getter, setter și în cele două apeluri din `ItemActivity`.
2. **Fără `= null`** — comportament identic, documentație mai săracă.
3. **Constructorul gol după `toString()`** — ordine de citire, nu de compilare.
4. **`toString()` cu `posterUrl`** — `toString()` complet; G1096 și G1099 îl omit.
5. **`outline_add_2_24`** — referință de resursă validă doar dacă drawable-ul există în proiect.

---

## Rezumat capitol 30

- Modelul nu atinge UI-ul; activitățile nu conțin logică de rând.
- `onCreate`: `super` -> `EdgeToEdge` -> `setContentView` -> insets -> date -> adapter -> controls -> listeners -> launcher.
- `releaseCal` este sursa de adevăr pentru dată, nu textul din `EditText`.
- Bucla pe `RadioGroup` face codul generic — adaugi butoane în XML, codul le vede.
- `setResult(RESULT_OK, intent)` + `finish()` este perechea obligatorie.
- `notifyDataSetChanged()` după orice modificare a listei.
- G1098 este cel mai curat la importuri: un singur import mort (`Toast` în `MainActivity`) și zero în `ItemActivity`.
- Trei bug-uri reale: buget gol, `release` null, data pierdută la editare fără atingerea câmpului.
- Diferențele față de G1097 sunt de nume, ordine și igienă — aplicația face exact același lucru.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [prezentarea generală](index.html).
