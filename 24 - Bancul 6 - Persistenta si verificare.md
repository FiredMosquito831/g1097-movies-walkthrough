# Capitolul 24 — Bancul 6: persistență și verificare

**Obiectiv:** să poți demonstra la examen, în mai puțin de un minut, că ceea ce salvezi **chiar** ajunge în listă, cu valorile corecte, o singură dată — și să știi exact ce supraviețuiește unei rotiri, unei ieșiri din aplicație și unei reporniri. Bancul 6 nu cere cod spectaculos: cere **dovada** că lanțul funcționează, plus persistența reală, pe disc.

**Unde stau datele la d719ffc:** `private final List<Movie> movies = new ArrayList<>();` în `MainActivity`. Nimic pe disc.

**Cele trei niveluri de persistență:**

| Nivel | Ce supraviețuiește | Cum |
|---|---|---|
| Starea formularului | rotirea | `onSaveInstanceState` |
| Lista în memorie | cât timp procesul trăiește | `ArrayList` în `MainActivity` |
| Lista pe disc | repornirea aplicației | `SharedPreferences` / fișier / Room |

**Cum arată cerința la examen:** „Datele să se salveze." Patru cuvinte, două cerințe ascunse:

- **(a)** la Save, filmul apare în listă, cu valorile corecte;
- **(b)** la editare, lista se actualizează **pe loc**, fără duplicate.

Restul capitolului e despre cum **demonstrezi** (a) și (b) — și despre ce răspunzi când profesorul întreabă „și după ce închizi aplicația?".

**Trei defecte reale la `d719ffc` pe care le vei întâlni în timpul verificării.** Nu sunt scenarii inventate; sunt în cod:

| Defect | Unde | Simptom |
|---|---|---|
| `Double.parseDouble("")` | `ItemActivity.saveMovie()`, linia 173 | Save cu bugetul gol → `NumberFormatException`, aplicația crapă, nu se întoarce nimic în listă |
| `dateFormat.format(null)` | `ItemActivity.fillForm()`, linia 88 | un `Movie` cu `release == null` → `NullPointerException` la deschiderea în editare |
| `String.valueOf(double)` | `ItemActivity.fillForm()`, linia 89 | bugetul se afișează `1.6E8` în loc de `160000000` |

Primul și al doilea ucid cerința (a) înainte să apuce să ruleze. Al treilea nu crapă nimic, dar arată urât și e cel care te face să crezi că „nu s-a salvat" când de fapt s-a salvat.

**Convenție:** textele din UI rămân în engleză, ca în aplicație (`"Save Movie"`, `"Update Movie"`, `"Yes"`, `"No"`). Proza, comentariile din cod și explicațiile sunt în română. Numerele de linie se referă la `cod-final/` la commitul `d719ffc`.

**Harta exercițiilor:**

| # | Ce verifici | Mecanismul din spate | Nivel |
|---|---|---|---|
| 24.1 | adăugarea ajunge pe ecran | `notifyDataSetChanged()` | listă |
| 24.2 | editarea înlocuiește, nu adaugă | `movies.set(position, ...)` | listă |
| 24.3 | Back anulează | `RESULT_OK` + copia prin `Intent` | navigare |
| 24.4 | numărul de filme e corect | `movies.size()` + `Toast` | listă |
| 24.5 | rotirea | `onSaveInstanceState` | formular |
| 24.6 | repornirea aplicației | `SharedPreferences` + JSON construit manual | disc |
| 24.7 | un atribut nou se salvează și se reîncarcă | checklist în 6 verificări | toate |
| 24.8 | „se salvează, dar nu apare" | triaj: Logcat, breakpoint, `Toast` | debug |
| 24.9 | „apare de două ori" | `add` vs. `set` | debug |
| 24.10 | examenul | (a) + (b), cap-coadă | toate |

---

## Exercițiul 24.1 — Adaugi un film, apare în listă. Ce se întâmplă dacă uiți `notifyDataSetChanged()`?

**Cerință:** Adaugă un film din formular și confirmă că apare în listă. Apoi **scoate** temporar `movieAdapter.notifyDataSetChanged()` din ramura de adăugare și descrie exact ce vezi la prima rulare, la a doua adăugare și în Logcat. La final, spune de ce simptomul nu e „nimic nu se întâmplă", ci „lista rămâne un pas în urmă".

**Fișiere atinse:** `cod-final/java/ro/ase/ie/g1097/activities/MainActivity.java` — callback-ul din `onCreate()` (liniile 63–77), plus o linie de `Log.d` pentru diagnostic.

**Cum abordezi — pașii tăi:**
1. Deschide `MainActivity.java` și citește callback-ul de la liniile 63–77. Notează cele două ramuri: `position == -1` → `movies.add(movie)` (linia 70); altfel → `movies.set(position, movie)` (linia 75). Ambele sunt urmate de `movieAdapter.notifyDataSetChanged()` (liniile 71 și 76).
2. Rulează aplicația. Lista are 3 rânduri: Inception, Toy Story, The Matrix.
3. Apasă FAB-ul, completează titlul „Dune", bugetul `165000000`, alege o dată, apasă „Save Movie". Revino în listă: al 4-lea rând apare. **Asta e comportamentul corect.**
4. Comentează linia 71 (`// movieAdapter.notifyDataSetChanged();`), rulează din nou, adaugă „Dune". Revino în listă: rămân 3 rânduri. Adaugă „Alien". Revino: de regulă apare „Dune", dar nu și „Alien". Notează senzația: **lista e cu un pas în urmă**.
5. Adaugă temporar, imediat după `movies.add(movie)`, un log:
   ```java
   Log.d("G1097", "dupa add: movies=" + movies.size()
           + " adapter=" + movieAdapter.getCount()
           + " listView=" + listView.getCount());
   ```
   Rulează și uită-te în Logcat la filtrul `G1097`. Cei trei parametri trebuie să fie egali. Când nu sunt, ai găsit bug-ul.
6. Pune linia 71 la loc și confirmă că cei trei parametri sunt din nou egali după fiecare operație.

**Indiciu 1 — dacă te blochezi la pasul 4:** `ArrayAdapter` nu copiază lista, o **referință** ține. Deci `movies.add(movie)` modifică exact lista pe care adapterul o citește. Ce lipsește nu e datele, ci **anunțul** că datele s-au schimbat.

**Indiciu 2 — dacă te blochezi la pasul 5:** `adapter.getCount()` întoarce `mObjects.size()`, adică valoarea live. `listView.getCount()` întoarce `mItemCount`, valoarea **cache-uită** la ultimul `onChanged()`. Diferența dintre ele este exact `notifyDataSetChanged()`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** nimic nou în codul final — s-a verificat lanțul și s-a demonstrat ce se strică fără notificare.

**Cod:**

```java
// MainActivity, callback-ul din onCreate(), liniile 63–77 — există la d719ffc
if (o.getResultCode() == RESULT_OK) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);
    if (position == -1) {
        movies.add(movie);
        movieAdapter.notifyDataSetChanged();   // ← singurul semnal către ListView
    } else {
        movies.set(position, movie);
        movieAdapter.notifyDataSetChanged();
    }
}
```

```java
// diagnostic — o linie, în callback, după notify
Log.d("G1097", "movies=" + movies.size()
        + " adapter=" + movieAdapter.getCount()
        + " listView=" + listView.getCount());
```

**De ce:** lanțul are patru verigi și doar ultima redesenează:

1. `movies.add(movie)` mută datele. Lista e aceeași instanță pe care a primit-o adapterul în constructor (`new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`, linia 55).
2. `ArrayAdapter.getCount()` returnează `mObjects.size()` — deci **deja** vede 4 elemente.
3. `ListView` nu întreabă niciodată lista. Întreabă adapterul, dar numai când e anunțat: `notifyDataSetChanged()` → `DataSetObservable.notifyChanged()` → `AdapterView.onChanged()`, care face `mItemCount = getAdapter().getCount()` și `requestLayout()`.
4. Fără pasul 3, `mItemCount` rămâne 3. `ListView` nu are de ce să ceară un al patrulea rând.

De aceea simptomul e „un pas în urmă": `ListView.onMeasure()` recitește `mItemCount` din adapter (`mItemCount = mAdapter == null ? 0 : mAdapter.getCount();`). La următorul pass complet de măsurare — o rotire, o revenire în ecran, o schimbare de layout — rândul lipsă apare „de la sine", iar cel adăugat imediat după el rămâne ascuns. Din exterior arată ca o listă care întârzie, nu ca un bug.

Mai există și un final urât: dacă un pass de layout rulează **fără** măsurare, cu `mItemCount` rămas în urmă, `ListView.layoutChildren()` aruncă:

```
java.lang.IllegalStateException: The content of the adapter has changed but
ListView did not receive a notification. Make sure your adapter calls
notifyDataSetChanged() when its content changes.
```

Mesajul ăsta e cel mai bun profesor: îți spune exact ce ai uitat.

**De reținut:** `ArrayAdapter.add(movie)` apelează singur `notifyDataSetChanged()` la final. Deci `movieAdapter.add(movie)` ar funcționa și fără linia explicită — dovadă că ceea ce contează nu e mutația, ci **notificarea**. `movies.add(movie)` ocolește adapterul și de aceea nu notifică nimeni. Aici e și răspunsul scurt de la examen: „adapterul nu observă lista; îl anunți tu".

**Unde se aplică:** orice pereche listă + adapter — `ArrayAdapter`, `BaseAdapter`, `RecyclerView.Adapter` (unde echivalentul e `notifyItemInserted` / `notifyItemChanged` / `notifyDataSetChanged`). Regula: **o singură metodă care mută datele și notifică**, apelată din toate locurile. Dacă `movies.add` apare în două locuri și `notify` doar într-unul, ai deja bug-ul.

</details>

---

## Exercițiul 24.2 — Editezi un film, lista arată valorile NOI. De ce `set` și nu `add`?

**Cerință:** Deschide „Inception", schimbă titlul în „Inception (2010)" și bugetul în `200000000`, apasă „Update Movie". Lista trebuie să arate valorile noi, iar numărul de rânduri să rămână 3. Explică apoi de ce codul folosește `movies.set(position, movie)` și nu `movies.add(movie)`, și de ce nu ai putea modifica pur și simplu obiectul primit în `ItemActivity`.

**Fișiere atinse:** `MainActivity.java` — ramura `else` din callback (liniile 73–77); `ItemActivity.java` — `saveMovie()` (liniile 168–194), citit, nu modificat.

**Cum abordezi — pașii tăi:**
1. Rulează aplicația și atinge rândul „Inception". Formularul se deschide completat, iar butonul scrie „Update Movie" — semn că `position != -1`.
2. Schimbă titlul și bugetul, apasă „Update Movie". În listă, rândul 0 arată valorile noi; lista are tot 3 rânduri.
3. Deschide `MainActivity.java` la linia 75 și înlocuiește temporar `movies.set(position, movie);` cu `movies.add(movie);`. Rulează din nou și repetă editarea.
4. Privește lista: 4 rânduri. Primul e „Inception" **vechi**, ultimul e „Inception (2010)" **nou**. Aceasta e diferența dintre `set` și `add`, vizibilă pe ecran.
5. Pune `set` la loc. Apoi deschide `ItemActivity.java` la liniile 76–83 și întreabă-te de ce `fillForm(existing)` nu poate „salva" modificările direct în obiectul părinte.
6. Verificare: după Update, atinge din nou rândul → formularul arată valorile noi. Dacă arăta cele vechi, ai adăugat în loc să înlocuiești.

**Indiciu 1 — dacă te blochezi la pasul 5:** obiectul care pleacă prin `Intent` nu e obiectul din listă. `putExtra(String, Serializable)` îl serializează, iar `Intent`-ul trece prin `system_server` (Binder), deci la destinație se reconstruiește o **instanță nouă**. Modifici copia, nu originalul.

**Indiciu 2 — dacă te blochezi la pasul 3:** `set(index, element)` înlocuiește elementul de la index și **păstrează mărimea**. `add(element)` adaugă la final și **crește mărimea**. Niciuna nu te obligă să folosești valoarea întoarsă — `add` întoarce `boolean`, `set` întoarce elementul vechi — deci compilatorul nu te avertizează că ai ales greșit.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-a confirmat că editarea înlocuiește, s-a demonstrat ce se întâmplă cu `add` și s-a explicat de ce obiectul din `ItemActivity` e o copie.

**Cod:**

```java
// MainActivity, liniile 73–77 — varianta corectă (d719ffc)
else {
    movies.set(position, movie);          // înlocuiește la index
    movieAdapter.notifyDataSetChanged();  // și reînnoiește rândurile vizibile
}
```

```java
// greșit — duce la duplicat (vezi și 24.9)
else {
    movies.add(movie);                    // originalul rămâne la position
    movieAdapter.notifyDataSetChanged();  // și copia apare la final
}
```

```java
// ItemActivity, liniile 76–83 — de ce nu poți modifica originalul
Intent intent = getIntent();
Movie existing = IntentCompat.getSerializableExtra(intent, MainActivity.MOVIE_EXTRA, Movie.class);
if (existing != null) {
    position = intent.getIntExtra(MainActivity.POSITION_EXTRA, -1);
    fillForm(existing);                   // citește dintr-o COPIE
    ...
}
```

**De ce:** trei motive independente, toate valabile la examen:

1. **`set` păstrează invarianta listei.** O editare nu schimbă numărul de filme. `add` ar face 4 rânduri din 3, iar cerința (b) din examen — „fără duplicate" — pică imediat.
2. **Obiectul din `ItemActivity` e o copie.** `Movie implements Serializable` (linia 6 din `Movie.java`). `putExtra` îl pune în `Bundle`, `Intent`-ul traversează Binder către `system_server` și înapoi, iar `getSerializableExtra` îl deserializează într-o instanță nouă. Chiar dacă `ItemActivity` ar face `existing.setTitle("X")`, obiectul din `movies` ar rămâne neatins. De aceea părintele trebuie **să primească** obiectul nou și să-l instaleze el.
3. **`saveMovie()` construiește oricum un `Movie` nou.** Prima linie a metodei (168) e `Movie movie = new Movie();`. Nu există nicio cale prin care modificările să ajungă în obiectul vechi — și nici nu trebuie să existe.

De ce se vede schimbarea imediat: `ArrayAdapter.getView()` cheamă `toString()` pe obiectul aflat la poziția respectivă. După `set`, la poziția `position` stă obiectul nou, deci `toString()` întoarce valorile noi. Vechiul obiect nu mai e referit de nimeni și îl ia garbage collector-ul.

`notifyDataSetChanged()` rămâne obligatoriu și după `set`: numărul de rânduri nu se schimbă, dar **conținutul** da, iar `ListView` trebuie să recicleze și să recompună rândurile vizibile.

**De reținut:** `movies.set(position, movie)` aruncă `IndexOutOfBoundsException` dacă `position` e în afara listei. `position` vine dintr-un `Intent`, deci e „date de la altcineva" — nu te încrede în el. Garda minimă, care intră și în codul de la 24.10:

```java
if (position >= 0 && position < movies.size()) {
    movies.set(position, movie);
} else {
    Log.e("G1097", "position invalid: " + position + ", size=" + movies.size());
}
```

**Unde se aplică:** orice „editare" în Android — `set` + `notifyItemChanged` la `RecyclerView`, `UPDATE ... WHERE id = ?` la SQLite, `map.put(key, value)` într-un dicționar. Peste tot: înlocuire la cheie, nu adăugare. Confuzia `add`/`set` e cea mai frecventă sursă de duplicate la test.

</details>

---

## Exercițiul 24.3 — Apeși Back fără Save: nu se schimbă nimic. Ce garantează asta?

**Cerință:** Deschide un film, modifică titlul, apasă Back (fără „Update Movie"). Lista trebuie să rămână neschimbată, iar redeschiderea filmului trebuie să arate titlul original. Explică **ce anume** din cod garantează asta — sunt trei mecanisme independente — și ce s-ar întâmpla dacă ai apela `setResult(RESULT_OK, ...)` prea devreme.

**Fișiere atinse:** `ItemActivity.java` — `saveMovie()` (liniile 188–193); `MainActivity.java` — callback-ul (liniile 63–77). Ambele citite; eventual o linie de log pentru demonstrație.

**Cum abordezi — pașii tăi:**
1. Rulează aplicația, deschide „Toy Story", schimbă titlul în „Toy Story 2", apasă Back (gest sau butonul de sistem).
2. Lista: neschimbată. Redeschide „Toy Story": titlul e tot „Toy Story". Nimic nu s-a pierdut și nimic nu s-a stricat.
3. Deschide `ItemActivity.java` și caută toate aparițiile lui `setResult`. E o singură linie (192), urmată imediat de `finish()` (193), ambele în `saveMovie()`.
4. Deschide `MainActivity.java` la linia 63: `if (o.getResultCode() == RESULT_OK)`. Întreabă-te ce valoare are `resultCode` când utilizatorul apasă Back.
5. Adaugă temporar un `Toast` în callback, **înainte** de `if`, care afișează `o.getResultCode()` și dacă `o.getData()` e `null`. Repetă ambii pași: Save → `-1` (RESULT_OK) și un `Intent`; Back → `0` (RESULT_CANCELED) și `null`.
6. Scoate `Toast`-ul. Opțional, experimentul periculos de la „De ce": pune `setResult(RESULT_OK);` la finalul lui `onCreate()` și apasă Back.

**Indiciu 1 — dacă te blochezi la pasul 4:** `RESULT_OK` este `-1`, `RESULT_CANCELED` este `0`. O activitate care se închide fără să cheme `setResult` raportează `RESULT_CANCELED`. Back-ul nu cheamă `saveMovie()`, deci nu are cine să seteze altceva.

**Indiciu 2 — dacă te blochezi la pasul 6:** `setResult` nu se „resetează" la Back. Codul rămas setat e folosit de `finish()`. De aceea `setResult` se cheamă **ultima** instrucțiune înainte de `finish()`, niciodată preventiv.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-au identificat cele trei garanții care fac Back-ul inofensiv și s-a demonstrat capcana lui `setResult` lipicios.

**Cod:**

```java
// ItemActivity.saveMovie(), liniile 188–193 — singurul loc cu setResult
Intent intent = new Intent();
intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
if (position != -1)
    intent.putExtra(MainActivity.POSITION_EXTRA, position);
setResult(RESULT_OK, intent);
finish();
```

```java
// MainActivity, linia 63 — poarta de intrare
if (o.getResultCode() == RESULT_OK) {
    ...
}
```

**De ce:** trei mecanisme independente, fiecare ar fi suficient singur:

1. **`setResult` se cheamă doar în `saveMovie()`.** Iar `saveMovie()` e legată numai de butonul `btMovieAction` (`initListeners()`, liniile 138–143). Back nu trece pe acolo. Fără `setResult`, `resultCode` rămâne `RESULT_CANCELED` (0).
2. **Callback-ul filtrează.** Chiar dacă rezultatul ar veni cu alt cod, `if (o.getResultCode() == RESULT_OK)` blochează orice altceva. Poarta e în părinte, nu în copil — bine, pentru că părintele e cel care deține datele.
3. **Copiem, nu partajăm.** Chiar dacă `ItemActivity` ar modifica obiectul primit (ar face `existing.setTitle(...)`), acesta e o instanță deserializată, separată de cea din `movies`. Părintele nu vede modificarea. (Detaliul e explicat în 24.2.)

Ordinea din `saveMovie()` contează: `setResult(...)` **înainte** de `finish()`. Invers, rezultatul nu mai ajunge niciodată — `finish()` distruge activitatea, iar `setResult` apelat după nu mai are cine să-l citească.

**Capcana:** `setResult` e lipicios. Dacă îl chemi la finalul lui `onCreate()` „ca să fie", atunci Back va raporta `RESULT_OK`, iar `MainActivity` va intra pe ramura de salvare cu un `Intent` fără `MOVIE_EXTRA`. Rezultatul e `NullPointerException` la `intent.getSerializableExtra(...)` sau, cu gardă, un film `null` adăugat în listă. Demonstrează o dată, apoi scoate linia. Lecția: **rezultatul se construiește când utilizatorul confirmă, nu când se deschide ecranul.**

**De reținut:** `o.getData()` poate fi `null` chiar și cu `RESULT_OK` (dacă cineva a chemat `setResult(RESULT_OK)` fără `Intent`). Garda de la 24.10 — `if (o.getResultCode() == RESULT_OK && o.getData() != null)` — nu e paranoia, e exact scenariul de mai sus.

**Unde se aplică:** orice pereche „formular → listă": dialog de confirmare (`AlertDialog` cu OK/Cancel), ecran de setări, wizard cu pași. Regula universală: **Back = anulare, butonul explicit = confirmare**, iar părintele verifică codul, nu se încrede în copil.

</details>

---

## Exercițiul 24.4 — 3 adăugări + 1 editare: numărul de filme e corect. Verificare cu `Toast`

**Cerință:** Pornește de la cele 3 filme demo, adaugă 3 filme noi și editează unul existent. La fiecare operație, un `Toast` afișează `movies.size()`. La final, lista trebuie să aibă **6** rânduri, iar cele trei numere — `movies.size()`, `movieAdapter.getCount()`, `listView.getCount()` — trebuie să fie egale după fiecare operație.

**Fișiere atinse:** `MainActivity.java` — o metodă nouă `showCount(String)` și două apeluri în callback.

**Cum abordezi — pașii tăi:**
1. Deschide `MainActivity.java` și adaugă metoda de mai jos, lângă `addSampleMovies()`.
2. Cheam-o la finalul fiecărei ramuri din callback, după `notifyDataSetChanged()`.
3. Rulează și notează pe hârtie, în ordine: `3` (start), `4`, `5`, `6` (cele trei adăugări), `6` (editarea).
4. Verifică tabelul de mai jos. Dacă un rând diferă, oprește-te și caută de ce înainte să continui — un număr greșit la pasul 2 va produce un duplicat la pasul 5.
5. Adaugă și verificarea de duplicate (metoda `hasDuplicateTitles()`), apelată în același loc. La un test corect trebuie să afișeze mereu `false`.
6. Verificare finală pe emulator: după cele patru operații, numără rândurile cu ochiul. Șase. Atinge ultimul film adăugat: formularul se deschide cu valorile lui.

**Indiciu 1 — dacă te blochezi la pasul 3:** `movies.size()` crește doar la `add`. `set` nu schimbă mărimea. Deci 3 + 3 = 6, iar editarea lasă 6. Dacă obții 7, ai folosit `add` și pe ramura de editare (24.9). Dacă obții 5, ai folosit `set` și pe ramura de adăugare — ai suprascris un film.

**Indiciu 2 — dacă te blochezi la pasul 5:** `Toast.makeText(...)` are nevoie de un `Context`; în activitate e `this`. `Toast.LENGTH_SHORT` e constanta de durată. Nu uita `.show()` — fără el, obiectul se construiește și nu apare nimic.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-a adăugat o verificare ieftină, care transformă o presupunere într-o dovadă: numărul de elemente din listă, din adapter și din `ListView`, afișat după fiecare operație.

**Cod:**

```java
// MainActivity — metoda de verificare
private void showCount(String step) {
    String message = step + ": " + movies.size() + " filme";
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    Log.d("G1097", message
            + " | adapter=" + movieAdapter.getCount()
            + " | listView=" + listView.getCount()
            + " | duplicate=" + hasDuplicateTitles());
}

private boolean hasDuplicateTitles() {
    for (int i = 0; i < movies.size(); i++) {
        for (int j = i + 1; j < movies.size(); j++) {
            if (Objects.equals(movies.get(i).getTitle(), movies.get(j).getTitle())) {
                return true;
            }
        }
    }
    return false;
}
```

```java
// apelurile, în callback
if (position == -1) {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
    showCount("dupa adaugare");
} else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
    showCount("dupa editare");
}
```

```java
// import nou în MainActivity
import java.util.Objects;
```

**De ce:** tabelul de așteptare, scris înainte de rulare, e cea mai bună unealtă de debug. Fără el, „parcă erau șase" e o impresie; cu el, 5 sau 7 e un fapt.

| Pas | Acțiune | `movies.size()` | `adapter.getCount()` | `listView.getCount()` | `duplicate` |
|---|---|---|---|---|---|
| 0 | pornire | 3 | 3 | 3 | `false` |
| 1 | adaugă „Dune" | 4 | 4 | 4 | `false` |
| 2 | adaugă „Alien" | 5 | 5 | 5 | `false` |
| 3 | adaugă „Arrival" | 6 | 6 | 6 | `false` |
| 4 | editează „Inception" | 6 | 6 | 6 | `false` |

Trei numere, trei surse diferite: `movies.size()` e adevărul din model, `adapter.getCount()` e ce vede adapterul, `listView.getCount()` e ce a apucat să afișeze `ListView`. Când primul diferă de al doilea, ai două liste (sau două adaptoare). Când al doilea diferă de al treilea, ai uitat `notifyDataSetChanged()` (24.1).

`hasDuplicateTitles()` e verificarea care prinde exact defectul din 24.9 înainte să ajungă la profesor. Comparația pe titlu e suficientă pentru examen; varianta corectă, pe `equals`/`hashCode`, e discutată în 24.9.

**De reținut:** `Toast` e pentru tine, nu pentru utilizator — la examen e acceptat ca dovadă, dar într-o aplicație reală se folosește `Log.d` sau un `TextView` de status. `Toast`-ul se afișează pe firul principal; callback-ul rulează pe firul principal, deci e sigur. Dacă ai apela `showCount` dintr-un fir de fundal, ai avea nevoie de `runOnUiThread`.

**Unde se aplică:** orice cerință de tip „arată câte sunt" sau „verifică numărul". La test, dacă profesorul cere „afișează numărul de filme", `Toast`-ul din 24.4 e răspunsul; dacă cere „permanent pe ecran", mută textul într-un `TextView` și actualizează-l în aceeași metodă — nu în două locuri diferite.

</details>

---

## Exercițiul 24.5 — Rotirea: ce se pierde de fapt din formular. `onSaveInstanceState`

**Cerință:** Completează formularul în `ItemActivity`, întoarce telefonul și notează, pentru fiecare control, dacă valoarea s-a păstrat. Apoi salvează explicit tot formularul cu `onSaveInstanceState` / `onRestoreInstanceState`, ca să nu depinzi de ce face framework-ul. La final, explică de ce lista din `MainActivity` se comportă complet altfel la aceeași rotire.

**Fișiere atinse:** `ItemActivity.java` — șase constante noi, `onSaveInstanceState`, `onRestoreInstanceState`; `MainActivity.java` — opțional, varianta cu `Bundle` de la final.

**Cum abordezi — pașii tăi:**
1. Rulează aplicația, apasă FAB-ul (mod inserare), scrie „Test rotire", alege o dată din picker, mișcă `SeekBar`-ul la 120, pune 4 stele, activează switch-ul. Rotește emulatorul (`Ctrl+Left` / `Ctrl+Right`).
2. Notează ce s-a păstrat: titlul, data afișată, durata, ratingul, switch-ul. Aproape tot. Acum apasă „Save Movie" și uită-te la filmul din listă: **data e cea de azi**, nu cea aleasă. Aici e pierderea reală.
3. Deschide `ItemActivity.java` și fă lista câmpurilor care **nu** sunt `View`: `position` (57), `releaseCal` (58), `dateFormat` (59). Pentru fiecare, întreabă-te cine îl reinițializează la recreare.
4. Adaugă cele șase constante `KEY_*` lângă `position` și cele două metode, după `onCreate()`.
5. Rulează din nou testul de la pasul 1, apoi apasă „Save Movie". Data din listă trebuie să fie cea aleasă.
6. Deschide „Inception" (mod editare), schimbă titlul, rotește, apasă „Update Movie". Apoi revino în `MainActivity`, adaugă un film și rotește acolo.

**Indiciu 1 — dacă te blochezi la pasul 2:** framework-ul salvează singur `View`-urile care au `android:id` și `android:saveEnabled="true"` (default). `EditText.getFreezesText()` returnează `true`; `ProgressBar` (baza pentru `SeekBar` și `RatingBar`) își salvează progresul; `CompoundButton` își salvează bifa; `AbsSpinner` își salvează poziția. Ce **nu** e `View` nu se salvează.

**Indiciu 2 — dacă te blochezi la pasul 6:** în `MainActivity`, `movies` e un câmp al activității, inițializat inline cu `new ArrayList<>()`. La rotire se creează o activitate nouă, deci o listă nouă, goală. `addSampleMovies()` o umple iar cu cele trei demo. `ListView` salvează doar poziția de derulare, nu datele.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-a măsurat ce supraviețuiește fără cod, apoi s-a adăugat salvarea explicită a stării formularului — cu accent pe `releaseCal`, singurul câmp care conta cu adevărat.

**Cod:**

```java
// ItemActivity — câmpuri noi, lângă position (linia 57)
private static final String KEY_TITLE = "key_title";
private static final String KEY_BUDGET = "key_budget";
private static final String KEY_DURATION = "key_duration";
private static final String KEY_RATING = "key_rating";
private static final String KEY_RELEASE = "key_release";
private static final String KEY_RELEASE_TEXT = "key_release_text";
```

```java
// ItemActivity — după onCreate()
@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putString(KEY_TITLE, etTitle.getText().toString());
    outState.putString(KEY_BUDGET, etBudget.getText().toString());
    outState.putInt(KEY_DURATION, sbDuration.getProgress());
    outState.putFloat(KEY_RATING, rbRating.getRating());
    outState.putLong(KEY_RELEASE, releaseCal.getTimeInMillis());
    outState.putString(KEY_RELEASE_TEXT, etRelease.getText().toString());
}

@Override
protected void onRestoreInstanceState(@NonNull Bundle savedInstanceState) {
    super.onRestoreInstanceState(savedInstanceState);
    etTitle.setText(savedInstanceState.getString(KEY_TITLE, ""));
    etBudget.setText(savedInstanceState.getString(KEY_BUDGET, ""));
    sbDuration.setProgress(savedInstanceState.getInt(KEY_DURATION, 0));
    rbRating.setRating(savedInstanceState.getFloat(KEY_RATING, 0f));
    releaseCal.setTimeInMillis(
            savedInstanceState.getLong(KEY_RELEASE, System.currentTimeMillis()));
    etRelease.setText(savedInstanceState.getString(KEY_RELEASE_TEXT, ""));
}
```

```java
// MainActivity — varianta cu Bundle, dacă vrei lista să supraviețuiască rotirii
private static final String KEY_MOVIES = "key_movies";

@Override
protected void onSaveInstanceState(@NonNull Bundle outState) {
    super.onSaveInstanceState(outState);
    outState.putSerializable(KEY_MOVIES, new ArrayList<>(movies));
}
```

```java
// MainActivity.onCreate() — restaurarea, înainte de crearea adapterului
if (savedInstanceState != null) {
    ArrayList<?> saved = savedInstanceState.getSerializable(KEY_MOVIES, ArrayList.class);
    if (saved != null) {
        for (Object item : saved) {
            if (item instanceof Movie) {
                movies.add((Movie) item);
            }
        }
    }
}
if (movies.isEmpty()) {
    addSampleMovies();
}
```

**De ce:** la rotire, activitatea e distrusă și recreată. Ce se întâmplă cu fiecare lucru:

| Ce | Supraviețuiește? | De ce |
|---|---|---|
| `etTitle`, `etRelease`, `etBudget`, `etPoster` | da | `EditText.getFreezesText()` întoarce `true`, deci textul intră în `SavedState` |
| `sbDuration`, `rbRating` | da | `ProgressBar.onSaveInstanceState()` salvează `progress` |
| `swWatched`, `cbonWatchList`, fiecare `RadioButton` | da | `CompoundButton` salvează bifa |
| `spGenre` | da | `AbsSpinner` salvează poziția selectată |
| `tvDurationValue`, `tvWatchedValue` | aparent da | `TextView` **nu** își salvează textul (`freezesText` e `false`), dar listenerii îl recalculează: `setProgress` și `setChecked` îi apelează la restaurare |
| `releaseCal` | **nu** | e câmp al activității, reinițializat cu `Calendar.getInstance()` |
| `position` | da | e recitit din `Intent`, iar sistemul re-livrează același `Intent` |
| `movies` (MainActivity) | **nu** | câmp al activității, recreat gol; `ListView` salvează doar poziția de derulare |

Două detalii de ordine, ambele esențiale:

- **`onRestoreInstanceState` rulează după `onStart`**, deci după `fillForm(existing)` din `onCreate`. Restaurarea ta câștigă în fața modelului. Dacă ai restaura la începutul lui `onCreate`, `fillForm` ți-ar suprascrie valorile.
- **Restaurarea framework-ului rulează tot după `onCreate`**, în `Activity.onRestoreInstanceState` → `mWindow.restoreHierarchyState(...)`. De aceea, în modul editare, după rotire formularul arată ce ai tastat tu, nu ce e în model — comportamentul dorit.

Pierderea reală e `releaseCal`. Textul din `etRelease` supraviețuiește (e `EditText`), dar `saveMovie()` citește `releaseCal.getTime()` (linia 171), nu textul câmpului. Deci după rotire apeși Update și salvezi **data de azi**, în timp ce pe ecran se vede data veche. Nu crapă, nu avertizează — doar minte. Linia care contează din tot exercițiul e `outState.putLong(KEY_RELEASE, ...)`.

De ce lista din `MainActivity` se comportă altfel: nu există niciun `View` care să o țină. `ListView` salvează în `AbsListView.SavedState` doar poziții și selecții (`selectedId`, `firstId`, `position`, `viewTop`, `checkState`) — **niciodată date**. `ArrayAdapter` nu e `View`, deci nu e în ierarhie. Iar `movies` e `final` și inițializat inline: fiecare instanță nouă de `MainActivity` primește un `ArrayList` nou, iar `addSampleMovies()` îl umple cu exact cele trei demo. Filmul adăugat nu „dispare" — nu a fost niciodată altundeva decât în heap-ul activității vechi. Filmul adăugat nu „dispare" — nu a fost niciodată altundeva decât în heap-ul activității vechi.

**De reținut:** `android:configChanges="orientation|screenSize"` **nu** e soluția. Ascunde problema la rotire, dar nu la moartea procesului și nici la „Don't keep activities" (Developer options), și în plus sari peste reîncărcarea resurselor — layout-ul de landscape nu s-ar mai aplica niciodată.

`Bundle` are o limită practică de ~1 MB (`TransactionTooLargeException`). Trei-șase filme sunt nimic; o listă de mii de obiecte sau un bitmap nu au ce căuta acolo. Pentru liste mari, `ViewModel` (supraviețuiește rotirii, nu și morții procesului) sau discul (24.6).

**Unde se aplică:** orice câmp de activitate care nu e `View` și nu vine din `Intent` — `releaseCal`, un filtru de căutare, un index de pagină, un obiect editat. Și orice listă care trebuie să arate la fel după rotire: `Bundle` pentru liste mici, `ViewModel` pentru liste medii, disc pentru tot ce trebuie să rămână.

</details>

---

## Exercițiul 24.6 — Persistență reală: lista se pierde la închiderea aplicației. `SharedPreferences` + JSON construit manual

**Cerință:** Adaugă un film, închide aplicația din Recents (swipe), redeschide-o. Filmul a dispărut. Explică de ce, apoi salvează lista în `SharedPreferences` ca JSON — **construit manual**, cu `StringBuilder`, fără Gson, fără Moshi, fără nicio dependență nouă în `build.gradle.kts`. La pornire, lista se încarcă din preferințe; dacă e goală (prima rulare), se pun cele trei demo și se scriu pe disc.

**Fișiere atinse:** `MainActivity.java` — `onCreate()` (liniile 53–55), `onPause()`, cinci metode noi (`saveMovies`, `loadMovies`, `moviesToJson`, `moviesFromJson`, `escape`) și șase importuri.

**Cum abordezi — pașii tăi:**
1. Rulează aplicația, adaugă „Dune", închide-o din Recents, redeschide-o. Lista are 3 rânduri. Confirmă simptomul înainte să scrii cod.
2. În `MainActivity`, înlocuiește apelul `addSampleMovies();` (linia 53) cu încărcarea din preferințe plus „seed" la prima rulare.
3. Scrie `moviesToJson()` cu `StringBuilder`. Pentru fiecare film, un obiect cu cele 10 câmpuri. Nu uita `escape()` pentru stringuri — altfel un titlu cu ghilimele strică tot fișierul.
4. Scrie `moviesFromJson()` cu `JSONArray` / `JSONObject` din `org.json` (vin cu Android, nu sunt biblioteci externe) și tratează `JSONException`.
5. Cheamă `saveMovies()` în `onPause()`. Verifică pe disc cu `adb`.
6. Testează cu un titlu care conține ghilimele și cu unul care conține diacritice.

**Indiciu 1 — dacă te blochezi la pasul 2:** `movies` e `final`, deci `movies = loadMovies();` **nu compilează**. Folosește `movies.addAll(loadMovies());` sau `movies.clear(); movies.addAll(...);`. Adapterul ține referința la listă, nu la conținut — de aceea nu reasignezi niciodată, doar modifici.

**Indiciu 2 — dacă te blochezi la pasul 4:** `new JSONArray(json)` aruncă `JSONException` dacă șirul e invalid. Prinde-o și pornește cu lista goală — aplicația se auto-repară la prima rulare următoare. Pentru citirea câmpurilor folosește `optString` / `optInt` / `optDouble` / `optBoolean`, care întorc o valoare implicită în loc să arunce.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** lista a fost serializată manual în JSON și scrisă în `SharedPreferences` la fiecare `onPause`, apoi reîncărcată la `onCreate`, cu populare cu demo-uri doar la prima rulare.

**Cod:**

```java
// MainActivity — câmpuri noi, lângă POSITION_EXTRA / MOVIE_EXTRA
private static final String PREFS_NAME = "g1097_movies";
private static final String KEY_MOVIES_JSON = "movies_json";
```

```java
// MainActivity.onCreate() — înlocuiește addSampleMovies() de la linia 53
movies.addAll(loadMovies());
if (movies.isEmpty()) {
    addSampleMovies();
    saveMovies();               // prima rulare: demo-urile ajung pe disc
}

movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
initControls();
initListeners();
```

```java
// MainActivity — scrierea și citirea
@Override
protected void onPause() {
    super.onPause();
    saveMovies();               // fiecare ieșire din ecran scrie lista
}

private boolean saveMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = moviesToJson();
    boolean ok = prefs.edit().putString(KEY_MOVIES_JSON, json).commit();
    Log.d("G1097", "saveMovies: " + movies.size() + " filme, "
            + json.length() + " caractere, ok=" + ok);
    return ok;
}

private List<Movie> loadMovies() {
    SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
    String json = prefs.getString(KEY_MOVIES_JSON, null);
    List<Movie> loaded = moviesFromJson(json);
    Log.d("G1097", "loadMovies: " + loaded.size() + " filme din " + PREFS_NAME);
    return loaded;
}
```

```java
// JSON construit manual — fără Gson, fără Moshi
private String moviesToJson() {
    StringBuilder sb = new StringBuilder("[");
    for (int i = 0; i < movies.size(); i++) {
        Movie m = movies.get(i);
        if (i > 0) sb.append(',');
        sb.append('{')
          .append("\"title\":\"").append(escape(m.getTitle())).append("\",")
          .append("\"release\":").append(m.getRelease() == null ? 0L : m.getRelease().getTime()).append(',')
          .append("\"genre\":\"").append(escape(m.getGenre())).append("\",")
          .append("\"budget\":").append(BigDecimal.valueOf(m.getBudget()).toPlainString()).append(',')
          .append("\"duration\":").append(m.getDuration()).append(',')
          .append("\"rating\":").append(m.getRating()).append(',')
          .append("\"watched\":").append(m.isWatched()).append(',')
          .append("\"approval\":\"").append(escape(m.getApproval())).append("\",")
          .append("\"onWatchlist\":").append(m.isOnWatchlist()).append(',')
          .append("\"poster\":\"").append(escape(m.getPoster())).append("\"")
          .append('}');
    }
    return sb.append(']').toString();
}

private static String escape(String value) {
    if (value == null) return "";
    return value.replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t");
}
```

```java
// citirea — org.json vine cu Android, nu e bibliotecă externă
private List<Movie> moviesFromJson(String json) {
    List<Movie> result = new ArrayList<>();
    if (json == null || json.isEmpty()) return result;
    try {
        JSONArray array = new JSONArray(json);
        for (int i = 0; i < array.length(); i++) {
            JSONObject o = array.getJSONObject(i);
            Movie m = new Movie();
            m.setTitle(o.optString("title", ""));
            m.setRelease(new Date(o.optLong("release", 0L)));
            m.setGenre(o.optString("genre", ""));
            m.setBudget(o.optDouble("budget", 0));
            m.setDuration(o.optInt("duration", 0));
            m.setRating((float) o.optDouble("rating", 0));
            m.setWatched(o.optBoolean("watched", false));
            m.setApproval(o.optString("approval", ""));
            m.setOnWatchlist(o.optBoolean("onWatchlist", false));
            m.setPoster(o.optString("poster", ""));
            result.add(m);
        }
    } catch (JSONException e) {
        Log.e("G1097", "JSON invalid — pornesc cu lista goală", e);
    }
    return result;
}
```

```java
// importuri noi în MainActivity
import android.content.SharedPreferences;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.math.BigDecimal;
```

**De ce:** la închiderea aplicației, procesul moare și odată cu el tot heap-ul: `movies`, adapterul, activitățile. RAM-ul nu e persistență. `SharedPreferences` scrie un fișier XML în `/data/data/ro.ase.ie.g1097/shared_prefs/g1097_movies.xml`, pe care sistemul îl păstrează până la dezinstalare sau „Clear data". La prima citire, tot fișierul e încărcat în memorie; `edit()` construiește o copie modificabilă, iar `commit()` / `apply()` o scrie înapoi.

Alegerea `SharedPreferences` + JSON în locul altor variante:

| Variantă | Când o folosești | Cost |
|---|---|---|
| `SharedPreferences` + JSON | liste mici, examen, prototip | tot fișierul rescris la fiecare salvare; fără interogări |
| fișier în `filesDir` | date mai mari, export | gestionezi tu citirea/scrierea și erorile |
| `Room` / SQLite | liste mari, căutare, relații | entitate, DAO, bază de date, migrări |

Trei decizii din cod care merită explicate:

- **`BigDecimal.valueOf(...).toPlainString()`** în loc de `String.valueOf(double)`. Exact lecția din tabelul de la începutul capitolului: `String.valueOf(160000000.0)` dă `1.6E8`. JSON acceptă notația științifică, deci s-ar reîncărca corect — dar fișierul devine ilizibil, iar dacă îl citești cu altă unealtă (sau cu ochiul) pari să fi salvat altceva. `toPlainString()` scrie `160000000`.
- **`commit()` în loc de `apply()`.** `commit()` scrie sincron și întoarce `boolean` — deci **poți verifica**. `apply()` scrie asincron și nu întoarce nimic. Pentru șase filme, diferența de timp e neglijabilă; pentru o listă mare, folosește `apply()` în producție și `commit()` doar în teste.
- **`onPause()`, nu `onDestroy()`.** `onDestroy()` nu e garantat: dacă procesul e omorât, nu se cheamă. `onPause()` se cheamă la fiecare ieșire din ecran. Salvezi puțin mai des decât e nevoie — corect și sigur.

**De reținut:** `escape()` e obligatoriu și ordinea contează: întâi backslash, apoi ghilimele. Dacă inversezi, `\"` devine `\\"` și JSON-ul se strică. Un titlu ca `He said "hi"` fără escape produce un fișier invalid, iar la pornire `new JSONArray(...)` aruncă — aplicația pornește cu lista goală și pare că „s-a pierdut tot".

`release` e salvat ca `long` (`Date.getTime()`), nu ca string. Un `Date` formatat ca text depinde de `Locale` și de fus orar; un `long` e fără ambiguitate. `0` e sentința pentru „fără dată" și e transformat în `new Date(0)` la citire, ca să nu introducem `null` — `fillForm` de la `d719ffc` crapă pe `release == null` (linia 88).

**Unde se aplică:** orice dată care trebuie să supraviețuiască procesului. La examen, dacă cerința spune „datele să se salveze" și nu spune „în bază de date", `SharedPreferences` + JSON e răspunsul cel mai rapid și mai ușor de explicat. Dacă profesorul cere explicit „la repornirea aplicației", aceasta e demonstrația: închizi din Recents, redeschizi, filmul e acolo.

**Verificare pe emulator:**

1. Adaugă „Dune", închide din Recents, redeschide → „Dune" e în listă, iar demo-urile nu s-au dublat.
2. Fișierul de pe disc:
   ```
   adb shell run-as ro.ase.ie.g1097 cat shared_prefs/g1097_movies.xml
   ```
   Trebuie să vezi `&quot;title&quot;` și restul câmpurilor. `run-as` merge doar pe build `debug` (implicit în Android Studio).
3. Adaugă un film cu titlul `He said "hi"` → repornește → titlul e intact, iar în XML secvența apare ca `\&quot;hi\&quot;` (`FastXmlSerializer` escapează ghilimelele ca `&quot;` chiar și în text).
4. Resetează: `adb shell pm clear ro.ase.ie.g1097` (sau Settings → Apps → Storage → Clear data) → la următoarea pornire revin cele trei demo.

</details>

---

## Exercițiul 24.7 — Checklist-ul de după fiecare „adaugă un atribut": 6 verificări

**Cerință:** Adaugă filmului un atribut nou (alege `writer`, String, sau `language`, String) și parcurge **șase** verificări care dovedesc că atributul se salvează **și** se reîncarcă corect. Scrie checklist-ul ca pe o procedură pe care o repeți la fiecare atribut, nu ca pe o poveste pentru acest atribut.

**Fișiere atinse:** `model/Movie.java`, `res/layout/activity_item.xml`, `activities/ItemActivity.java`, `activities/MainActivity.java` (și `movie_item.xml` + adapter, dacă afișezi atributul în rând).

**Cum abordezi — pașii tăi:**
1. Fă lanțul clasic din capitolul 17: câmp + getter/setter + `toString()` + constructor în `Movie`, control în XML, `findViewById`, `fillForm`, `saveMovie`. Compilează.
2. Parcurge verificările 1–6 de mai jos, în ordine, notând rezultatul fiecăreia. Nu sări peste niciuna „pentru că se vede".
3. La fiecare verificare care pică, notează stratul: model, formular, activitate, listă sau disc. Aproape întotdeauna un atribut „care nu se salvează" e de fapt un atribut care se salvează, dar nu se **reîncarcă** — lipsa din `fillForm`.
4. Rulează din nou checklist-ul după ce ai reparat. Un checklist care nu e rulat de două ori nu e checklist, e încercare.
5. Verificare finală: adaugă un film cu atributul completat, închide aplicația, redeschide, deschide filmul în editare. Valoarea trebuie să fie acolo, în listă și în formular.

**Indiciu 1 — dacă te blochezi la verificarea 3:** pune un `Toast` cu `movie.toString()` în `saveMovie()`, imediat înainte de `setResult`. Dacă atributul apare acolo, `saveMovie` e corect și problema e mai departe. Dacă apare `null` sau `0`, problema e în citirea din widget.

**Indiciu 2 — dacă te blochezi la verificarea 6:** dacă ai făcut 24.6, JSON-ul are exact 10 câmpuri scrise de mână. Un atribut nou nu se salvează pe disc până nu adaugi și linia din `moviesToJson()` **și** linia din `moviesFromJson()`. E cel mai frecvent loc în care un atribut „dispare la repornire".

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-a transformat „adaugă un atribut" într-o procedură verificabilă în șase pași, fiecare cu un simptom clar dacă e sărit.

**Cod:** checklist-ul propriu-zis, cu ce verifici, cum verifici și ce se vede dacă ai sărit pasul.

| # | Verificare | Cum | Dacă lipsește |
|---|---|---|---|
| 1 | **Modelul** are câmp, getter, setter, `toString()` și e în constructor | compilează; `movie.toString()` conține atributul | erori de compilare în `addSampleMovies()`, dacă ai schimbat constructorul |
| 2 | **Formularul** are controlul în XML, cu `android:id`, legat prin `findViewById` | deschide ecranul; nu crapă | `NullPointerException` la `onCreate`, sau câmpul nu există pe ecran |
| 3 | **`saveMovie()`** scrie atributul în `Movie` | `Toast` cu `movie.toString()` înainte de `setResult` | valoarea rămâne default (`null`, `0`, `false`) |
| 4 | **`fillForm()`** citește atributul din `Movie` | deschide filmul în editare | câmpul e gol, deși în listă se vede valoarea |
| 5 | **Lista** afișează atributul | privește rândul; dacă folosești adapter, și `TextView`-ul lui | salvat, dar invizibil — cel mai puțin grav |
| 6 | **Supraviețuirea**: rotire + repornire | rotește în formular; închide din Recents și redeschide | valoarea se pierde la rotire (`onSaveInstanceState`) sau la repornire (JSON-ul de la 24.6) |

```java
// verificarea 3 — Toast-ul care dovedește ce pleacă spre listă
Log.d("G1097", "saveMovie: " + movie.toString());
Toast.makeText(this, movie.getTitle() + " / " + movie.getWriter(),
        Toast.LENGTH_SHORT).show();
```

```java
// verificarea 4 — linia care lipsește cel mai des din fillForm()
etWriter.setText(existing.getWriter() == null ? "" : existing.getWriter());
```

```java
// verificarea 6 — cele două linii din persistarea de la 24.6
sb.append("\"writer\":\"").append(escape(m.getWriter())).append("\",");  // moviesToJson
m.setWriter(o.optString("writer", ""));                                 // moviesFromJson
```

**De ce:** lanțul are șase straturi și fiecare are propriul mod de a eșua tăcut:

```
Movie  →  XML  →  findViewById  →  saveMovie  →  fillForm  →  listă  →  disc
  1        2          2                3             4          5        6
```

Un atribut poate fi corect în cinci straturi și greșit în al șaselea. Simptomele sunt diferite și te trimit direct la strat:

- **Se vede în listă, dar nu în formular** → lipsește `fillForm` (verificarea 4). Lista citește `toString()`, formularul citește `fillForm`.
- **Se vede în formular, dar nu în listă** → lipsește `toString()` sau adapterul (verificarea 5).
- **Se vede peste tot, dar dispare la repornire** → lipsește din JSON (verificarea 6).
- **Se vede peste tot, dar dispare la rotire** → lipsește din `onSaveInstanceState` (verificarea 6, partea întâi).
- **E `null` în `saveMovie`** → lipsește citirea din widget (verificarea 3).

Ordinea verificărilor nu e întâmplătoare: de la model spre disc, de la cel mai ieftin de reparat la cel mai scump. O eroare de compilare la pasul 1 face inutile verificările 2–6.

**De reținut:** verificarea 6 e cea pe care Bancul 6 o adaugă peste lanțul din capitolul 17. Fără ea, atributul tău trăiește cât timp trăiește procesul — exact ca toată lista la `d719ffc`. La examen, dacă ai timp de o singură verificare în plus, fă-o pe asta: rotirea și repornirea sunt singurele care prind `releaseCal`-ul ascuns.

**Unde se aplică:** orice atribut nou, indiferent de tip. Pentru un `Date`, verificarea 4 are o capcană în plus: `fillForm` trebuie să formateze cu `dateFormat` și să nu primească `null` (altfel NPE, linia 88). Pentru un `double`, verificarea 4 trebuie să folosească `BigDecimal.toPlainString()`, nu `String.valueOf` (altfel `1.6E8`). Checklist-ul rămâne același; se schimbă doar codul din fiecare căsuță.

</details>

---

## Exercițiul 24.8 — Debug: filmul se salvează, dar nu apare în listă. 5 cauze, 5 verificări

**Cerință:** Ai adăugat un film, ai apăsat Save, dar în listă nu apare nimic. Enumeră **cinci** cauze posibile, în ordinea în care le verifici, și pentru fiecare spune ce instrument folosești (Logcat, breakpoint, `Toast`) și ce anume te face să o elimini. Nu ghici — triază.

**Fișiere atinse:** `MainActivity.java` (callback-ul, `showCount`), `ItemActivity.java` (`saveMovie`). Doar diagnostic; codul rămâne neschimbat la final.

**Cum abordezi — pașii tăi:**
1. Reproduce bug-ul intenționat: comentează `notifyDataSetChanged()` din ramura de adăugare. Rulează, adaugă un film. Confirmă simptomul.
2. Pune un `Toast` în `saveMovie()`, imediat înainte de `setResult`, cu `movie.getTitle()`. Dacă apare, salvarea a rulat; dacă nu, excepția e înainte.
3. Pune un `Toast` în callback, înainte de `if`, cu `o.getResultCode()`, `o.getData() != null` și `position`. Așa afli dacă rezultatul a ajuns și pe ce ramură intri.
4. Pune un breakpoint pe linia `movies.add(movie)` și rulează în debug. Inspectează `movies.size()` înainte și după, apoi `movieAdapter.getCount()` și `listView.getCount()`.
5. Parcurge tabelul de triaj de mai jos și notează, pentru fiecare cauză, ce valoare ai obținut.

**Indiciu 1 — dacă te blochezi la pasul 2:** un `Toast` care nu apare nu înseamnă neapărat că metoda nu a rulat — poate însemna că activitatea a crăpat înainte. Verifică Logcat după `FATAL EXCEPTION` înainte să tragi concluzia.

**Indiciu 2 — dacă te blochezi la pasul 4:** breakpoint-ul se pune pe linia din callback, nu în `ItemActivity`. Acolo vezi simultan `movies`, `movie` și `position` — exact cele trei variabile care decid ce se întâmplă.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-a construit un triaj în cinci ramuri, fiecare cu un semn distinct în cei trei parametri (`movies.size()`, `adapter.getCount()`, `listView.getCount()`) și cu instrumentul potrivit.

**Cod:** instrumentele de diagnostic, în ordinea în care le pui.

```java
// 1. în ItemActivity.saveMovie(), înainte de setResult
Log.d("G1097", "saveMovie: " + movie);

// 2. în MainActivity, în callback, înainte de if
Log.d("G1097", "result: code=" + o.getResultCode()
        + " data=" + (o.getData() != null)
        + " position=" + (o.getData() == null ? "?" : o.getData().getIntExtra(POSITION_EXTRA, -1)));

// 3. după fiecare ramură
Log.d("G1097", "dupa: movies=" + movies.size()
        + " adapter=" + movieAdapter.getCount()
        + " listView=" + listView.getCount());
```

```bash
# filtrarea Logcat-ului pe tag-ul nostru
adb logcat -s G1097:D
```

**De ce:** cele cinci cauze, cu semnătura lor:

| # | Cauză | Semnătura | Cum confirmi | Reparația |
|---|---|---|---|---|
| 1 | lipsește `notifyDataSetChanged()` | `movies=4`, `adapter=4`, `listView=3` | log-ul de la pasul 3 | adaugă linia (24.1) |
| 2 | rezultatul nu ajunge: `setResult` neapelat, cod greșit, sau excepție înainte | `Toast`-ul din `saveMovie` nu apare, sau `code=0` | `Toast` în `saveMovie` + log în callback | verifică ordinea `setResult` → `finish()`; prinde excepția (buget gol — vezi 24.10) |
| 3 | ramura greșită: `position != -1` la adăugare | `movies=3`, dar un titlu s-a schimbat | log cu `position` în callback | `position` se pune în `Intent` doar la editare (24.9) |
| 4 | adapterul privește altă listă | `movies=4`, `adapter=3` | log-ul de la pasul 3 | un singur `ArrayList`, o singură referință; nu reasignezi `movies` |
| 5 | rândul există, dar nu se vede | `movies=adapter=listView=4`, dar rândul nu e pe ecran | `listView.getLastVisiblePosition()`; `movies.get(size-1).toString()` | titlu gol, listă derulată, sau `toString()` fără atribut |

Cauza 2 merită subliniată, pentru că e singura care nu lasă urme în listă: dacă `saveMovie()` aruncă înainte de `setResult` — și la `d719ffc` o face la buget gol (`Double.parseDouble("")`, linia 173) — activitatea crapă, `MainActivity` revine pe ecran cu lista neatinsă și pare că „Save nu face nimic". Logcat-ul are `FATAL EXCEPTION` și stack-ul complet; ăsta e primul lucru pe care îl citești, nu ultimul.

Cauza 3 e cea care înșală cel mai des: lista **s-a schimbat**, doar că nu crește. Un `position` rămas de la o editare anterioară (sau trimis greșit ca `0`) face `movies.set(0, movie)` și suprascrie primul film. Semnul distinctiv: `movies.size()` rămâne constant, dar conținutul de la un index se schimbă.

Cauza 5 e singura în care datele sunt corecte și vizualul minte. Trei variante: titlul e `""` (rândul are înălțime, dar e gol), lista e derulată și noul rând e sub marginea de jos (`ListView` nu derulează automat la adăugare), sau `toString()` nu conține atributul căutat.

Ordinea de triaj, de la ieftin la scump: **Logcat → `Toast` → breakpoint**. Logcat e gratis și îți spune dacă a crăpat; `Toast`-ul îți spune dacă metoda a rulat; breakpoint-ul îți arată starea exactă. Nu începe cu breakpoint-ul — pierzi zece minute ca să afli ce scria în log.

**De reținut:** cele trei numere (`movies`, `adapter`, `listView`) sunt un triaj complet în două secunde. Fiecare combinație trimite la o cauză diferită:

- `movies == adapter > listView` → notificare lipsă (cauza 1).
- `movies > adapter` → două liste / două adaptoare (cauza 4).
- `movies == adapter == listView` dar rândul nu se vede → cauza 5.
- `movies` nu crește deloc → cauzele 2 sau 3.

**Unde se aplică:** orice „s-a salvat, dar nu se vede". La `RecyclerView` triajul e identic, doar al treilea număr devine `adapter.getItemCount()` după `notifyItemInserted`. La o bază de date, primul număr devine rezultatul unui `SELECT COUNT(*)`.

</details>

---

## Exercițiul 24.9 — Debug: după editare, filmul apare de două ori. `add` vs. `set`

**Cerință:** Editezi „The Matrix" și, după Update, în listă apar două rânduri „The Matrix": cel vechi și cel nou. Explică de ce, arată linia care produce duplicatul, repar-o — și spune ce faci dacă ai folosit deja `set` în locul greșit, astfel încât un film a fost suprascris.

**Fișiere atinse:** `MainActivity.java` — callback-ul (liniile 63–77), plus opțional o metodă de curățare.

**Cum abordezi — pașii tăi:**
1. Reprodu: în callback, înlocuiește `movies.set(position, movie);` cu `movies.add(movie);`. Editează „The Matrix" și schimbă ratingul.
2. Privește lista: 4 rânduri, două cu „The Matrix". Primul e cel vechi, ultimul e cel nou. Numărul a crescut — deci nu e o problemă de afișare, e o problemă de date.
3. Deschide din nou primul „The Matrix": are valorile vechi. Al doilea: valorile noi. Confirmă că sunt două obiecte distincte.
4. Pune `set` la loc și confirmă că lista revine la 3 rânduri, cu valorile noi la poziția corectă.
5. Experimentează și invers: în ramura de adăugare, înlocuiește `movies.add(movie);` cu `movies.set(0, movie);`. Adaugă un film. Lista are tot 3 rânduri, iar „Inception" a dispărut. Acesta e celălalt simptom al aceleiași confuzii.
6. Scrie `removeDuplicates()` și ruleaz-o pe lista deja coruptă de la pasul 2.

**Indiciu 1 — dacă te blochezi la pasul 5:** `set(0, movie)` nu aruncă nicio excepție — indexul 0 e valid. Pur și simplu înlocuiește primul element. De aceea bug-ul e periculos: nu se semnalează, doar pierde date.

**Indiciu 2 — dacă te blochezi la pasul 6:** `Movie` nu are `equals` și `hashCode`, deci `movies.remove(movie)` compară prin identitate și nu va găsi niciodată „același" film. Fie deduplici manual, pe titlu + dată, fie adaugi `equals`/`hashCode` în `Movie` — a doua variantă e cea corectă.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-a identificat confuzia `add`/`set` în ambele ei forme, s-a reparat ramura corectă și s-a scris o curățare pentru datele deja corupte.

**Cod:**

```java
// GREȘIT — duplicat: originalul rămâne la position, copia se adaugă la final
else {
    movies.add(movie);
    movieAdapter.notifyDataSetChanged();
}

// CORECT — înlocuire pe loc, mărimea nu se schimbă
else {
    movies.set(position, movie);
    movieAdapter.notifyDataSetChanged();
}
```

```java
// curățarea unei liste deja corupte — O(n²), suficient pentru examen
private void removeDuplicates() {
    for (int i = movies.size() - 1; i >= 0; i--) {
        for (int j = 0; j < i; j++) {
            if (sameMovie(movies.get(i), movies.get(j))) {
                movies.remove(i);
                break;
            }
        }
    }
    movieAdapter.notifyDataSetChanged();
}

private boolean sameMovie(Movie a, Movie b) {
    if (a.getTitle() == null || b.getTitle() == null) return false;
    if (!a.getTitle().equals(b.getTitle())) return false;
    if (a.getRelease() == null || b.getRelease() == null) return false;
    return a.getRelease().getTime() == b.getRelease().getTime();
}
```

```java
// varianta corectă, pe termen lung — în Movie.java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Movie)) return false;
    Movie other = (Movie) o;
    return Objects.equals(title, other.title)
            && Objects.equals(release, other.release);
}

@Override
public int hashCode() {
    return Objects.hash(title, release);
}
```

```java
// import nou în Movie.java
import java.util.Objects;
```

**De ce:** `add` și `set` răspund la două întrebări diferite:

| Metodă | Întrebarea | Efect | Mărime |
|---|---|---|---|
| `add(element)` | „adaugă un film nou" | inserează la final | +1 |
| `set(index, element)` | „înlocuiește filmul de la index" | înlocuiește, restul rămân | neschimbată |

O editare e a doua întrebare. Butonul se numește „Update Movie", `position` vine din `Intent`, iar utilizatorul a modificat un film existent — nu a creat unul. `add` e răspunsul la altă întrebare.

De ce ajunge duplicatul în listă și nu se rezolvă singur: `movies` e o listă simplă, fără constrângeri de unicitate. Nimic nu împiedică două obiecte cu același titlu. `ArrayAdapter` le afișează pe amândouă, pentru că pentru el sunt două elemente.

**A doua formă a aceleiași confuzii:** `set` folosit la adăugare. Dacă `position` nu e `-1` când adaugi (de exemplu ai trimis `POSITION_EXTRA` cu `0`, sau ai uitat să-l scoți dintr-un `Intent` refolosit), `movies.set(position, movie)` **suprascrie** filmul de la acel index. Lista nu crește, nu apare nicio eroare, dar un film a dispărut. Reparația nu se poate face din cod — filmul vechi nu mai există în memorie. Ce poți face:

1. **Oprește pierderea:** `position` se pune în `Intent` **doar** în modul editare (`if (position != -1)`), exact ca la linia 190 din `ItemActivity`.
2. **Validează indexul** înainte de `set`: `if (position >= 0 && position < movies.size())`.
3. **Refă datele pierdute** manual (reintrodu filmul) sau repornește de la demo-uri cu „Clear data" — dacă ai persistență (24.6), șterge și fișierul de preferințe.

**De reținut:** `Movie` nu are `equals`/`hashCode` la `d719ffc`, deci `List.remove(Object)`, `List.contains(...)` și `Set<Movie>` se comportă pe identitate, nu pe conținut. Două filme cu același titlu sunt „diferite" pentru colecții. Dacă adaugi `equals`/`hashCode`, `removeDuplicates()` se simplifică la:

```java
Set<Movie> unique = new LinkedHashSet<>(movies);
movies.clear();          // movies e final — nu se poate reasigna
movies.addAll(unique);
movieAdapter.notifyDataSetChanged();
```

**Unde se aplică:** orice listă editabilă. În `RecyclerView`, echivalentele sunt `notifyItemInserted` (add) și `notifyItemChanged` (set) — aceeași confuzie, alt API. Într-o bază de date, `INSERT` vs. `UPDATE ... WHERE id = ?`; acolo baza te salvează parțial, pentru că un `INSERT` fără cheie primară duplicată e respins.

</details>

---

## Exercițiul 24.10 — Examenul: „datele să se salveze"

**Cerință:** Cerința de examen are două părți: **(a)** la Save, filmul apare în listă cu valorile corecte; **(b)** la editare, lista se actualizează pe loc, fără duplicate. Implementează ambele, apoi demonstrează-le cu un scenariu de șase pași, cronometrat, în care fiecare pas are un rezultat așteptat. Include gărzile care fac cerința (a) să nu cadă pe buget gol sau pe dată lipsă.

**Fișiere atinse:** `MainActivity.java` — callback-ul; `ItemActivity.java` — `saveMovie()` și `fillForm()`.

**Cum abordezi — pașii tăi:**
1. Scrie întâi scenariul de acceptare (tabelul de mai jos), cu valorile exacte pe care le vei introduce. Nu improviza în timpul demonstrației.
2. Repară cele trei defecte reale: buget gol (`NumberFormatException`), `release` null (`NullPointerException`), buget afișat `1.6E8`.
3. Adaugă garda de `Intent` în callback: `o.getData() != null` și `position` valid.
4. Rulează scenariul o dată, cronometrat. Notează unde pierzi timp.
5. Rulează din nou, cu „Don't keep activities" activat (Developer options) — simularea morții activității. Apoi închide din Recents și redeschide, dacă ai făcut 24.6.
6. Verificare finală: toate rândurile din tabel trec, iar `hasDuplicateTitles()` întoarce `false` la final.

**Indiciu 1 — dacă te blochezi la pasul 2:** `Double.parseDouble("")` aruncă `NumberFormatException`, iar `dateFormat.format(null)` aruncă `NullPointerException` în `calendar.setTime(null)`. Ambele sunt înainte de `setResult`, deci aplicația crapă și părintele nu primește nimic. Nu sunt „îmbunătățiri" — sunt condiții ca cerința (a) să poată fi demonstrată.

**Indiciu 2 — dacă te blochezi la pasul 3:** `o.getData()` poate fi `null` chiar și cu `RESULT_OK` (dacă cineva a chemat `setResult(RESULT_OK)` fără `Intent`). Iar `position` poate fi orice număr întreg — un `Intent` nu e un contract tipat. Ambele gărzi sunt două linii.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** s-au reparat cele trei defecte reale, s-au adăugat gărzile de rezultat și de index, și s-a scris scenariul de acceptare care demonstrează (a) și (b) în mai puțin de cinci minute.

**Cod:**

```java
// ItemActivity.saveMovie() — varianta cu validare
private void saveMovie() {
    String title = etTitle.getText().toString().trim();
    if (title.isEmpty()) {
        etTitle.setError("Title is required");
        etTitle.requestFocus();
        return;
    }

    String budgetText = etBudget.getText().toString().trim().replace(',', '.');
    if (budgetText.isEmpty()) {
        etBudget.setError("Budget is required");
        etBudget.requestFocus();
        return;
    }
    double budget;
    try {
        budget = Double.parseDouble(budgetText);
    } catch (NumberFormatException e) {
        etBudget.setError("Not a valid number");
        etBudget.requestFocus();
        return;
    }

    Movie movie = new Movie();
    movie.setTitle(title);
    movie.setRelease(releaseCal.getTime());
    movie.setGenre(spGenre.getSelectedItem().toString());
    movie.setBudget(budget);
    movie.setDuration(sbDuration.getProgress());
    movie.setRating(rbRating.getRating());
    movie.setWatched(swWatched.isChecked());
    movie.setOnWatchlist(cbonWatchList.isChecked());
    movie.setPoster(etPoster.getText().toString());
    for (int index = 0; index < rgApproval.getChildCount(); index++) {
        RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
        if (rb.isChecked()) {
            movie.setApproval(rb.getText().toString());
            break;
        }
    }

    Intent intent = new Intent();
    intent.putExtra(MainActivity.MOVIE_EXTRA, movie);
    if (position != -1)
        intent.putExtra(MainActivity.POSITION_EXTRA, position);
    setResult(RESULT_OK, intent);
    finish();
}
```

```java
// ItemActivity.fillForm() — cele două linii reparate
// import nou în ItemActivity: java.math.BigDecimal
etRelease.setText(existing.getRelease() == null
        ? ""
        : dateFormat.format(existing.getRelease()));
etBudget.setText(BigDecimal.valueOf(existing.getBudget()).toPlainString());
```

```java
// MainActivity — callback-ul final, cu toate gărzile
if (o.getResultCode() == RESULT_OK && o.getData() != null) {
    Intent intent = o.getData();
    Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
    int position = intent.getIntExtra(POSITION_EXTRA, -1);

    if (movie == null) {
        Log.e("G1097", "rezultat OK, dar fara Movie in Intent");
        return;
    }
    if (position == -1) {
        movies.add(movie);
    } else if (position >= 0 && position < movies.size()) {
        movies.set(position, movie);
    } else {
        Log.e("G1097", "position invalid: " + position + ", size=" + movies.size());
        return;
    }
    movieAdapter.notifyDataSetChanged();
    showCount(position == -1 ? "dupa adaugare" : "dupa editare");  // showCount vine din 24.4
}
```

**De ce:** cerința (a) are trei condiții, toate necesare: formularul produce un `Movie` complet (validare), rezultatul ajunge în părinte (`RESULT_OK` + `Intent`), iar părintele îl adaugă și notifică. Cerința (b) are două: ramura corectă (`set`, nu `add`) și index valid.

Scenariul de acceptare — îl rulezi exact așa, cu valorile astea:

| Pas | Acțiune | Rezultat așteptat | Ce demonstrează |
|---|---|---|---|
| 0 | pornire | 3 rânduri | starea inițială |
| 1 | adaugă „Dune", buget `165000000`, dată `01/10/2021` | 4 rânduri, „Dune" cu valorile introduse | (a) |
| 2 | atinge „Dune", schimbă titlul în „Dune: Part One", Update | 4 rânduri, titlul nou, **fără** al doilea „Dune" | (b) |
| 3 | atinge „Inception", Update fără nicio modificare | 4 rânduri, „Inception" neschimbat | (b) — `set` pe aceeași valoare nu strică nimic |
| 4 | adaugă „Alien" cu bugetul **gol** | apare eroarea pe câmp, aplicația **nu** crapă, lista rămâne 4 | (a) — garda |
| 5 | completează bugetul lui „Alien" cu `100000000` și salvează | 5 rânduri | (a) |
| 6 | închide din Recents, redeschide | tot 5 rânduri (cele 3 demo + Dune + Alien) | persistența (24.6) |

Tabelul e și răspunsul la întrebarea „cum verifici?". Fiecare rând are un rezultat observabil pe ecran, nu o impresie.

Cele trei defecte reparate, și de ce fiecare contează pentru (a):

- **Buget gol** → `NumberFormatException` în `saveMovie`, înainte de `setResult`. Aplicația crapă, părintele nu primește nimic, utilizatorul vede lista neatinsă. Fără gardă, cerința (a) nu poate fi demonstrată cu un formular incomplet — iar la examen formularul e aproape mereu incomplet la primul Save.
- **`release` null** → `NullPointerException` în `fillForm`, la `dateFormat.format(null)` (linia 88). Nu se întâmplă la `d719ffc` cu datele demo, dar se întâmplă cu un `Movie` construit manual sau încărcat din JSON fără dată. O gardă de trei linii.
- **`1.6E8`** → nu crapă, dar arată ca un bug și te face să crezi că valoarea s-a stricat. `BigDecimal.valueOf(...).toPlainString()` scrie `160000000`. Bonus: `Double.parseDouble("160000000")` funcționează, deci turul complet e corect.

**De reținut:** ordinea din `saveMovie()` e contractul: validează → construiește `Movie` → `setResult` → `finish()`. Orice `return` înainte de `setResult` înseamnă „nu s-a întâmplat nimic", iar asta e exact comportamentul dorit pentru un formular invalid. Orice `setResult` înainte de validare înseamnă că trimiți un film incomplet.

`position` e singura variabilă care decide între (a) și (b). Default `-1` în `getIntExtra`, pus în `Intent` doar la editare, validat înainte de `set`. Trei reguli, trei linii.

**Unde se aplică:** orice cerință de tip „salvează" la examen. Indiferent de entitate — film, student, produs, notă — lanțul e același: formular validat → `Movie`/`Student`/`Product` nou → `setResult` → părinte care `add` sau `set` → `notify`. Ce se schimbă sunt doar numele câmpurilor.

</details>

---

## Recapitulare — ce verifici la test

| Cerința din examen | Mecanismul | Exercițiu |
|---|---|---|
| „adaugi un film și apare în listă" | `notifyDataSetChanged()` după fiecare mutație | 24.1 |
| „editezi și lista arată valorile noi" | `movies.set(position, movie)` | 24.2 |
| „apeși Back și nu se schimbă nimic" | `setResult` doar la Save + garda `RESULT_OK` | 24.3 |
| „arată câte filme sunt" | `movies.size()` în `Toast` / `TextView` | 24.4 |
| „rotația nu pierde datele" | `onSaveInstanceState` + câmpurile care nu sunt `View` | 24.5 |
| „datele rămân după repornire" | `SharedPreferences` + JSON construit manual | 24.6 |
| „adaugă un atribut" | checklist în 6 verificări | 24.7 |
| „se salvează, dar nu apare" | triaj pe trei numere: `movies` / `adapter` / `listView` | 24.8 |
| „apare de două ori" | `add` vs. `set` | 24.9 |
| „datele să se salveze" | (a) + (b), cu validare și index validat | 24.10 |

Trei propoziții de memorat:

1. **Adapterul nu observă lista; îl anunți tu.** `movies.add(...)` mută datele, `notifyDataSetChanged()` le face vizibile. Fără al doilea, primul e invizibil.
2. **Editarea înseamnă `set`, adăugarea înseamnă `add`.** Aceeași confuzie produce fie un duplicat, fie un film pierdut — și niciuna nu aruncă excepție.
3. **RAM-ul nu e persistență.** `ArrayList` trăiește cât procesul; rotirea pierde lista, repornirea pierde tot. `onSaveInstanceState` ține formularul, `SharedPreferences` ține lista.
