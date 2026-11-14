# Capitolul 38 — Codul nou adnotat (14.11.2026)

**Obiectiv:** să citești fiecare linie a **versiunii actualizate** a aplicației — cea adusă pe 14.11.2026 — cu explicația lipită de ea: ce face, de ce e acolo, ce se rupe dacă o scoți. Față de versiunea veche (capitolele 22 și 29–31), aplicația are acum `RecyclerView`, un adaptor propriu, un callback de click și un ecran nou.

**Timp estimat:** 90–120 min (citire activă, cu proiectul deschis în paralel).

**Sursa:** versiunea 2 (14.11.2026), pachetul `com.example.group1098` — 8 fișiere adnotate aici: `MainActivity.java`, `MovieAdapter.java`, `IMovieListener.java`, `PlaceCiocanul.java`, `movie_item.xml`, `activity_main.xml`, `activity_place_ciocanul.xml`, `AndroidManifest.xml`. Cele trei fișiere rămase neschimbate (`Movie.java`, `ItemActivity.java`, `activity_item.xml`) sunt trimise la capitolele 22 și 30.

**Regulă:** codul este **nemodificat, byte cu byte**. Tot ce apare cu `//` sau `<!-- -->` în plus față de sursă este adnotare. Nu s-a reformatat nimic, nu s-a șters nicio linie, nu s-a adăugat nicio instrucțiune.

---

## 38.0 Ce e nou, în 10 rânduri

1. **`ListView` → `RecyclerView`.** Câmpul `listView` devine `rvMovies`; clasa vine din `androidx.recyclerview.widget`, nu din framework.
2. **`ArrayAdapter<Movie>` → `MovieAdapter`.** Adaptorul nu mai e gata făcut: are `ViewHolder`, `onCreateViewHolder`, `onBindViewHolder` și `getItemCount` scrise de mână.
3. **Click pe rând → interfață proprie.** `setOnItemClickListener` dispare; apare `IMovieListener`, implementată de activitate și apelată din `ViewHolder`.
4. **`movie_item.xml` este, în sfârșit, folosit.** În capitolul 22 fișierul exista, dar nu-l inflata nimeni. Acum fiecare rând al listei este un card construit din el.
5. **Ecran nou: `PlaceCiocanul`.** Un al doilea FAB (`btnVlad`, jos-stânga) deschide un ecran de test, prin **același** `launcher`.
6. **Codul vechi este păstrat comentat** în `MainActivity`, în trei locuri. Nu e o scăpare: este migrarea arătată pe viu, cu versiunea de dinainte și de după una lângă alta.
7. **Notificarea listei.** `movieAdapter.notifyDataSetChanged()` se apelează după fiecare mutație (`add` la inserare, `set` la editare) — varianta „geamănă", nu `notifyItemInserted`.
8. **Pachetul s-a schimbat:** `com.example.group1098`, cu subpachetele `activities/`, `adapter/` și `model/`. Importurile și `R`-ul urmează pachetul nou.
9. **Trei activități în manifest**, nu două. `PlaceCiocanul` trebuie declarat, altfel `Intent`-ul aruncă `ActivityNotFoundException` la runtime, fără eroare de compilare.
10. **Trei fișiere sunt identice byte cu byte** cu versiunea veche, în afara liniilor de pachet: `Movie.java`, `ItemActivity.java`, `activity_item.xml`. Nu se adnotează din nou aici.

### 38.0.1 Fișierele care nu s-au schimbat

| Fișier | Stare | Unde îl citești |
|---|---|---|
| `Movie.java` | identic cu versiunea veche, diferă doar `package ...model` | capitolul 22, secțiunea 22.1 (și capitolul 30 pentru varianta G1098) |
| `ItemActivity.java` | identic, diferă doar pachetul și cele două importuri | capitolul 22, secțiunea 22.3 |
| `activity_item.xml` | identic **fără nicio diferență** | capitolul 22, secțiunea 22.5 |

**De ce contează că sunt identice:** tot ce ai învățat despre formular rămâne valabil cuvânt cu cuvânt. Ce s-a schimbat este **doar** ecranul cu lista și legăturile lui: widget-ul, adaptorul, click-ul, layout-ul rândului și manifestul. Exact acolo trebuie să te uiți când compari cele două versiuni.

**Unde se vede tot restul:** capitolul 39 ia diferențele una câte una — de la `ListView` la `RecyclerView`, de la adaptorul gata făcut la adaptorul propriu, de la listener-ul de listă la interfața de callback — și le leagă de cerințele de examen. Capitolul de față este **citirea codului**; capitolul 39 este **explicația migrării**.

### 38.0.2 Cum să citești capitolul

- **Citește codul întâi, comentariul al doilea.** Acoperă cu mâna blocul de deasupra, spune ce face linia, apoi verifică.
- **Blocurile `TEORIE`** apar înaintea fiecărei clase și explică *de ce* există structura, nu *cum* funcționează.
- **Pașii numerotați** („1. Verificare", „2. Inflate") descriu ordinea execuției. Ordinea este parte din lecție.
- **Marcajele `RISC:`, `BUG:` și `DANGER!`** arată unde codul se poate rupe, unde se rupe deja și unde greșeala nu produce nicio eroare.
- **Diagramele ASCII** arată ce nu se vede în cod: reciclarea rândurilor, drumul click-ului, arborele de view-uri.
- **Compară cu capitolul 22.** Acolo e versiunea veche a acelorași două ecrane; diferența dintre ele este chiar materia acestei secțiuni.

---

## 38.1 `MainActivity.java` — lista pe RecyclerView

```java
/*
 * ======================================================================================
 * FIȘIER: MainActivity.java — ECRANUL CU LISTA, VERSIUNEA 2
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   Activitatea de start. Ține lista de filme într-un `ArrayList<Movie>`, o afișează
 *   cu un `RecyclerView` printr-un adaptor propriu (`MovieAdapter`) și pornește
 *   `ItemActivity` — pentru inserare, din FAB, și pentru editare, din click pe rând.
 *
 * DE CE EXISTĂ:
 *   Este singurul loc care deține STAREA aplicației: lista `movies`. Toate celelalte
 *   ecrane primesc un `Movie` prin `Intent` și întorc un `Movie` prin rezultat.
 *   Fără această clasă nu există unde să se întoarcă rezultatul.
 *
 * DE CE DEPINDE:
 *   - `Movie` (modelul), `MovieAdapter` și `IMovieListener` (pachetul `adapter`),
 *   - `R.layout.activity_main` și patru ID-uri: `main`, `rvMovies`,
 *     `floatingActionButton`, `btnVlad`,
 *   - clasele `ItemActivity` și `PlaceCiocanul`, pornite prin `Intent`.
 *
 * CINE DEPINDE DE EL:
 *   `ItemActivity` citește `MainActivity.MOVIE_EXTRA` și `MainActivity.POSITION_EXTRA`
 *   (le vede fiindcă sunt `protected static` și fișierul este în ACELAȘI pachet).
 *   `AndroidManifest.xml` îl declară cu intent-filter-ul LAUNCHER.
 *
 * CE NU FACE:
 *   Nu validează date, nu ține o poziție „selectată", nu salvează nimic pe disc.
 *   Lista trăiește în memorie și dispare odată cu procesul.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   Aplicația nu ar avea punct de intrare: fără activitatea din LAUNCHER, iconița
 *   nu pornește nimic. Iar fără `movies` de aici, formularul ar avea unde să trimită
 *   rezultatul, dar nimeni nu l-ar primi.
 * ======================================================================================
 */

// ======================================================================================
// PACHETUL ȘI IMPORTURILE
// ======================================================================================
package com.example.group1098.activities;

// Intent: obiectul care descrie „ce activitate pornești" și ce date duce cu ea.
//   Aici apare de trei ori: la FAB, la al doilea FAB și în callback-ul de rezultat.
import android.content.Intent;

// Bundle: sacul de stare salvat de sistem. Apare doar în semnătura lui `onCreate`.
import android.os.Bundle;

// View: clasa de bază a oricărui element de UI. Tipul parametrului din `onClick`.
import android.view.View;

// AdapterView: clasa de bază pentru ListView/Spinner, folosită de
//   `AdapterView.OnItemClickListener`.
// RISC: IMPORT NEFOLOSIT în versiunea 2. Singura referință a rămas în blocul
//   comentat din `initListeners`. Codul compilează, dar Android Studio îl arată gri.
import android.widget.AdapterView;

// ArrayAdapter: puntea dintre `List<Movie>` și rândurile de ListView.
// RISC: IMPORT NEFOLOSIT — la fel, supraviețuiește doar în comentarii.
import android.widget.ArrayAdapter;

// ListView: widget-ul versiunii vechi. Nici măcar nu mai există în layout.
// RISC: IMPORT NEFOLOSIT — rămășiță a migrării.
import android.widget.ListView;

// Toast: mesaje scurte pe ecran. Nu este folosit nicăieri în acest fișier —
//   nici în versiunea veche nu era (capitolul 22 îl semnala la fel).
import android.widget.Toast;

// EdgeToEdge: desenare sub barele de sistem (status + navigare).
import androidx.activity.EdgeToEdge;

// ActivityResult: rezultatul întors de activitatea secundară: cod + Intent.
import androidx.activity.result.ActivityResult;

// ActivityResultCallback: interfața cu o singură metodă, apelată la întoarcere.
import androidx.activity.result.ActivityResultCallback;

// ActivityResultLauncher: obiectul care pornește activitatea și ține legătura
//   cu callback-ul. Este câmpul `launcher`.
import androidx.activity.result.ActivityResultLauncher;

// ActivityResultContracts: contractele predefinite. Aici `StartActivityForResult`,
//   adică exact vechiul `startActivityForResult`, ambalat modern.
import androidx.activity.result.contract.ActivityResultContracts;

// AppCompatActivity: activitatea de bază, cu temă Material și suport AppCompat.
import androidx.appcompat.app.AppCompatActivity;

// Insets: valorile în pixeli ale barelor care acoperă conținutul.
import androidx.core.graphics.Insets;

// ViewCompat: versiunea compatibilă a API-urilor de View (insets pe orice API).
import androidx.core.view.ViewCompat;

// WindowInsetsCompat: descrierea insets-urilor, independent de versiunea Android.
import androidx.core.view.WindowInsetsCompat;

// LinearLayoutManager: singurul layout manager folosit aici. El decide ARANJAREA
//   rândurilor într-o listă verticală — `RecyclerView` nu are una implicită.
import androidx.recyclerview.widget.LinearLayoutManager;

// RecyclerView: widget-ul care înlocuiește ListView. Containerul, nu adaptorul.
import androidx.recyclerview.widget.RecyclerView;

// IMovieListener: contractul de click. MainActivity îl IMPLEMENTEAZĂ.
import com.example.group1098.adapter.IMovieListener;

// MovieAdapter: adaptorul propriu, scris în pachetul `adapter`.
import com.example.group1098.adapter.MovieAdapter;

// FloatingActionButton: butonul rotund. Sunt DOUĂ în acest ecran.
import com.google.android.material.floatingactionbutton.FloatingActionButton;

// ArrayList: implementarea concretă a listei de filme.
import java.util.ArrayList;

// Calendar: constantele lunilor (`Calendar.JULY`, `NOVEMBER`, `MARCH`).
import java.util.Calendar;

// GregorianCalendar: constructorul rapid „an, lună, zi" din datele demo.
import java.util.GregorianCalendar;

// List: interfața de listă.
// RISC: IMPORT NEFOLOSIT — câmpul este declarat `ArrayList<Movie>`, nu `List<Movie>`.
import java.util.List;

// R: clasa generată din resurse. Aici pentru `R.layout.activity_main` și `R.id.*`.
import com.example.group1098.R;

// Movie: modelul de date. Singura dependență către pachetul `model`.
import com.example.group1098.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: ACTIVITY, RECYCLERVIEW, CALLBACK
 * ======================================================================================
 *
 * 1. **Activity = un ecran cu o stare.** `MainActivity` este `Context` (are acces la
 *    resurse și la sistem) și `LifecycleOwner` (are un ciclu de viață: onCreate ->
 *    onStart -> onResume -> onPause -> onStop -> onDestroy).
 *
 * 2. **RecyclerView = un container fără opinii.** Nu știe ce afișează, nu știe cum
 *    arată un rând și nu știe în ce direcție se derulează. Tot ce știe este să ceară
 *    de la adaptor: „câte rânduri sunt?" și „dă-mi rândul de la poziția N".
 *
 * 3. **Adapter = traducătorul.** Pentru fiecare rând vizibil, creează (o singură dată)
 *    vederea și apoi o umple cu date (de fiecare dată). Cele două momente sunt două
 *    metode diferite: `onCreateViewHolder` și `onBindViewHolder`.
 *
 * 4. **Callback = întoarcerea click-ului.** Un rând este o vedere inertă. Ca să ajungă
 *    la activitate, adaptorul primește un obiect care implementează `IMovieListener`;
 *    aici obiectul acela este CHIAR `MainActivity` (`new MovieAdapter(movies, this)`).
 *
 * 5. **Launcher = contractul cu rezultatul.** `registerForActivityResult` se apelează
 *    O DATĂ, în `onCreate`, înainte ca activitatea să fie vizibilă. Rezultatul vine
 *    în `onActivityResult`, cu un cod (`RESULT_OK` / `RESULT_CANCELED`) și un `Intent`.
 *
 * FLUXUL VIZUAL AL FIECĂRUI RÂND:
 *
 *   movies (ArrayList<Movie>)            <- datele, deținute de activitate
 *        |
 *        v
 *   MovieAdapter                         <- getItemCount() + onBindViewHolder()
 *        |
 *        v
 *   RecyclerView  <--- LinearLayoutManager   <- UNDE stau rândurile
 *        |
 *        v
 *   movie_item.xml  ->  un card per film
 *
 * CINE ȚINE CE:
 *
 *   MainActivity  ---- deține ---->  ArrayList<Movie> movies
 *        |                                  ^
 *        | creează                          | aceeași referință
 *        v                                  |
 *   MovieAdapter  ----------------------> movies
 *        |
 *        +---- listează click-ul către ----> IMovieListener ( = MainActivity )
 *
 * DE CE `implements IMovieListener` ESTE OBLIGATORIU:
 *   `new MovieAdapter(movies, this)` cere ca al doilea argument să fie un
 *   `IMovieListener`. Fără `implements`, linia NU COMPILEAZĂ — și este bine:
 *   compilatorul verifică exact contractul pe care îl vrei.
 * ======================================================================================
 */

// Activitatea de start. `implements IMovieListener` o face destinatarul click-urilor.
public class MainActivity extends AppCompatActivity implements IMovieListener {

    // ==================================================================================
    // CELE DOUĂ CHEI ALE COMUNICĂRII CU ItemActivity
    // ==================================================================================
    // `static final` = constantă de clasă: aceeași valoare pentru toate instanțele,
    //   stabilită o dată, la compilare.
    // `protected` = vizibilă în subclase ȘI în tot pachetul. ItemActivity este în
    //   `com.example.group1098.activities`, deci vede constantele fără import.
    // DE CE NU `private`: ItemActivity le-ar primi ca text literal „movie" / „position";
    //   o greșeală de tastare ar da un extra inexistent, fără nicio eroare.
    // RISC: dacă schimbi valoarea „movie" aici, ItemActivity o vede automat — dar
    //   orice `getStringExtra("movie")` scris de mână în alt fișier s-ar rupe silențios.
    // ==================================================================================
    protected static final String POSITION_EXTRA = "position";

    // A doua cheie: filmul serializat. Aceeași convenție.
    protected static final String MOVIE_EXTRA = "movie";

    // FAB-ul „+", din colțul dreapta-jos. Deschide ItemActivity în modul inserare.
    private FloatingActionButton fabInsert;

    // Codul versiunii vechi, PĂSTRAT INTENȚIONAT:
    // private ListView listView;
    // DE CE A RĂMAS: ca cititorul să vadă exact ce s-a înlocuit și cu ce. În codul
    //   livrat, comentariul nu are efect; îl poți citi ca pe un „înainte".
    // REF: capitolul 22, secțiunea 22.2 — versiunea în care linia era activă.

    // SUCCESORUL lui `listView`: containerul de listă al versiunii 2.
    private RecyclerView rvMovies;

    // Launcher-ul de rezultat. Un singur obiect deservește AMBELE ecrane
    //   (`ItemActivity` și `PlaceCiocanul`), pentru că amândouă se pornesc la fel.
    // RISC: este atribuit ABIA la finalul lui `onCreate`, dar este folosit în
    //   listeneri creați mai devreme. Vezi explicația pasului 8 din `onCreate`.
    private ActivityResultLauncher<Intent> launcher;

    // LISTA — singura sursă de date a ecranului.
    // `final` înseamnă că REFERINȚA nu se schimbă niciodată; conținutul, da.
    //   De aceea `movies.add(...)` este legal, iar `movies = new ArrayList<>()` nu.
    // DE CE `final` ajută aici: adaptorul primește ACEASTĂ referință; dacă ai
    //   înlocui lista cu alta, adaptorul ar rămâne pe cea veche, fără nicio eroare.
    private final ArrayList<Movie> movies = new ArrayList<>();

    // Codul versiunii vechi, păstrat comentat:
    //private ArrayAdapter<Movie> movieAdapter;
    // Observă spațierea: originalul nu avea spațiu după `//`. Este mărturia exactă
    //   a unei linii comentate cu Ctrl+/ în Android Studio, nu rescrisă de mână.
    // REF: capitolul 22 — `ArrayAdapter` cu `simple_list_item_1`.

    // Adaptorul propriu. Tipul este clasa scrisă în pachetul `adapter`, nu una de sistem.
    private MovieAdapter movieAdapter;

    // Al doilea FAB, adăugat în versiunea 2. Jos-stânga; deschide ecranul de test.
    // Numele (`btnVlad`) este cel din XML (`@+id/btnVlad`) — se potrivește exact.
    private FloatingActionButton btnVlad;

    // ==================================================================================
    // METODA: onCreate — CONSTRUCȚIA ECRANULUI
    // ==================================================================================
    // CE FACE: creează ecranul, încarcă datele demo, construiește adaptorul, leagă
    //   view-urile de cod, instalează cei doi listeneri de buton și înregistrează
    //   launcher-ul de rezultat.
    // CUM: în ordinea de mai jos — și ordinea este singura parte greu de reparat.
    // RISC: fiecare pas depinde de cel dinainte. Mută `initControls()` după
    //   `initListeners()` și primești `NullPointerException` pe `fabInsert`,
    //   pentru că listener-ul s-ar lega pe un câmp încă `null`.
    // REF: capitolul 22, 22.2 — aceeași schemă, cu ListView în loc de RecyclerView.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. Lanțul obligatoriu al clasei de bază: fără el, AppCompat nu își
        //    instalează delegate-ul și tema nu se aplică.
        super.onCreate(savedInstanceState);

        // 2. Ferestrele desenează sub barele de sistem (status bar + navigare).
        EdgeToEdge.enable(this);

        // 3. Se umflă arborele de view-uri din XML. Din acest moment,
        //    `findViewById` are ce căuta.
        setContentView(R.layout.activity_main);

        // 4. Compensarea barelor: containerul `R.id.main` primește padding egal cu
        //    înălțimea barelor, ca primul rând să nu stea sub status bar.
        //    Lambda primește `insets` și întoarce exact ce a primit — contractul API.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. Insets-urile „system bars": status bar sus, navigare jos.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Padding pe cele patru laturi. `left/right` acoperă și cazul RTL,
            //     pentru că sunt deja calculate de sistem pe direcția corectă.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. Se întoarce obiectul primit: altfel sistemul ar considera insets-urile
            //     consumate și alte view-uri nu le-ar mai primi.
            return insets;
        });

        // 5. Datele demo: trei filme, adăugate ÎNAINTE ca adaptorul să fie creat.
        //    (Tehnic, ordinea nu ar strica: adaptorul ține referința la listă, nu o copie.)
        addSampleMovies();

        // Codul versiunii vechi, păstrat comentat — adaptorul gata făcut:
        // movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
        // CE FĂCEA: lega lista de un rând standard, care afișa `movie.toString()`,
        //   adică tot obiectul, pe un singur rând de text.
        // CE FACE ÎN LOCUL LUI: linia de mai jos, cu adaptorul propriu.

        // 6. Adaptorul propriu. `this` este al doilea parametru pentru că MainActivity
        //    implementează `IMovieListener` — ea este destinatarul click-urilor.
        //    Se pasează REFERINȚA la listă: adaptorul vede orice modificare ulterioară.
        movieAdapter = new MovieAdapter(movies, this);

        // 7a. Legarea view-urilor: în acest moment `rvMovies`, `fabInsert` și `btnVlad`
        //     primesc obiectele reale. `movieAdapter` este deja construit, deci
        //     `setAdapter` are ce primi.
        initControls();

        // 7b. Listenerii de butoane. Au nevoie de view-urile de la 7a — de aceea
        //     ordinea aceasta și nu invers.
        initListeners();

        // 7c. Al doilea listener, într-o metodă separată: FAB-ul `btnVlad`.
        initSecondListener();

        // 8. Launcher-ul de rezultat. `registerForActivityResult` trebuie apelat
        //    înainte ca activitatea să fie STARTED; `onCreate` este locul canonic.
        //    Contractul `StartActivityForResult` este echivalentul modern al vechiului
        //    `startActivityForResult(intent, REQUEST_CODE)`.
        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),

                // Callback-ul: o clasă anonimă care implementează o singură metodă.
                new ActivityResultCallback<ActivityResult>() {

                    // Se apelează la întoarcerea din ItemActivity sau PlaceCiocanul.
                    @Override
                    public void onActivityResult(ActivityResult o) {

                        // Poarta: se lucrează doar când ecranul secundar a spus
                        //   „am un rezultat". `RESULT_CANCELED` (butonul Back) nu
                        //   schimbă nimic în listă.
                        if(o.getResultCode() == RESULT_OK)
                        {
                            // Intent-ul de rezultat. Poate fi `null` dacă activitatea
                            //   a apelat `setResult(RESULT_OK)` fără Intent.
                            // RISC: aici nu se verifică `null`. Azi este sigur, pentru
                            //   că ItemActivity pune mereu un Intent (capitolul 22, 22.3),
                            //   iar PlaceCiocanul nu apelează niciodată `setResult`.
                            Intent intent = o.getData();

                            // Filmul călător: o COPIE deserializată, nu originalul.
                            //   Cast-ul este necesar: `getSerializableExtra` întoarce
                            //   `Serializable`, tipul comun al tuturor obiectelor puse.
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);

                            // Poziția: -1 = „nu există", adică modul inserare.
                            //   Valoarea implicită -1 este chiar convenția aplicației.
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);

                            // Ramura 1: nu există poziție -> film NOU.
                            if(position == -1)
                            {
                                // Adăugare la finalul listei.
                                movies.add(movie);

                                // Anunțul către RecyclerView. Fără el, lista rămâne
                                //   vizual neschimbată: adaptorul nu observă ArrayList-ul.
                                // REF: capitolul 23 — varianta fină, `notifyItemInserted`.
                                movieAdapter.notifyDataSetChanged();
                            }

                            // Ramura 2: poziție validă -> ÎNLOCUIRE, nu adăugare.
                            else
                            {
                                // `set` suprascrie elementul de la poziția dată.
                                // RISC: dacă lista s-ar fi schimbat între timp (ștergere,
                                //   reordonare), poziția ar putea indica alt film.
                                //   Aici lista nu se schimbă în afara acestor două ramuri.
                                movies.set(position, movie);

                                // Același anunț: un rând s-a schimbat.
                                movieAdapter.notifyDataSetChanged();
                            }
                        }
                    }
                });
    }

    // ==================================================================================
    // METODA: initListeners — FAB-ul de INSERARE (și codul vechi, comentat)
    // ==================================================================================
    // CE FACE: leagă `fabInsert` de pornirea ItemActivity fără extra-uri. Un singur
    //   listener activ; în plus, păstrează comentat listener-ul de listă al versiunii 1.
    // CUM: 1) listener pe FAB; 2) construiește Intent explicit; 3) lansează.
    // RISC: `launcher` este încă `null` în momentul în care se creează listener-ul —
    //   dar este citit abia la click, când `onCreate` s-a terminat de mult.
    // REF: capitolul 22, 22.2 — aceeași metodă, fără blocul comentat.
    // ==================================================================================
    private void initListeners() {

        // Listener pe FAB. Clasa anonimă, nu lambda: stilul proiectului (și al examenului).
        fabInsert.setOnClickListener(new View.OnClickListener() {

            // Se execută la fiecare apăsare.
            @Override
            public void onClick(View v) {

                // Intent EXPLICIT: sursa (`MainActivity.this`) și destinația
                //   (`ItemActivity.class`). Fără extra-uri: ItemActivity vede că nu are
                //   `MOVIE_EXTRA` și intră în modul inserare.
                // OBSERVAȚIE: clasa este scrisă cu numele complet al pachetului, deși
                //   ItemActivity este în ACELAȘI pachet. Este redundant, dar legal.
                Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);

                // Pornirea prin launcher: rezultatul va ajunge în callback-ul de la
                //   pasul 8 din `onCreate`.
                launcher.launch(intent);
            }
        });

        // ==============================================================================
        // CODUL VERSIUNII VECHI — CLICK-UL PE RÂND, PĂSTRAT COMENTAT
        // ==============================================================================
        // Acesta este cel mai valoros bloc didactic din fișier: arată EXACT ce s-a
        // pierdut când ListView a fost înlocuit cu RecyclerView și unde a fost mutat.
        //
        //   ÎNAINTE (ListView):                ACUM (RecyclerView):
        //   listView.setOnItemClickListener    listener în MovieAdapter (pe itemView)
        //   onItemClick(..., position, id)     onMovieClick(Movie, position)
        //   movies.get(position)               movies.get(position)
        //   putExtra(MOVIE_EXTRA, ...)         putExtra(MOVIE_EXTRA, ...)
        //   putExtra(POSITION_EXTRA, ...)      putExtra(POSITION_EXTRA, ...)
        //   launcher.launch(intent)            launcher.launch(intent)
        //
        // Ultimele patru linii sunt IDENTICE cu `onMovieClick` de la finalul fișierului.
        // Diferența este doar CINE le apelează: înainte ListView, acum adaptorul.
        /* listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);
                intent.putExtra(MOVIE_EXTRA, movies.get(position));
                intent.putExtra(POSITION_EXTRA, position);
                launcher.launch(intent);
            }
        });*/
        // DE CE A FOST NECESARĂ MUTAREA: un rând de RecyclerView nu este un element de
        //   listă observat de widget, ci o vedere oarecare. Nu există „onItemClick";
        //   click-ul se leagă manual, pe `itemView`, în `ViewHolder` (38.2).
        // RISC: dacă ai lăsa cele două active (blocul decomentat + `onMovieClick`),
        //   click-ul ar porni ItemActivity de două ori — două activități suprapuse.
    }

    // ==================================================================================
    // METODA: initSecondListener — AL DOILEA FAB
    // ==================================================================================
    // CE FACE: leagă `btnVlad` de pornirea ecranului `PlaceCiocanul`.
    // CUM: 1) listener; 2) Intent explicit; 3) ACELAȘI launcher.
    // RISC: același launcher primește și rezultatul acestui ecran. PlaceCiocanul nu
    //   cheamă `setResult`, deci codul întors este `RESULT_CANCELED` și callback-ul
    //   nu face nimic — exact comportamentul dorit.
    // REF: `initListeners`, cu o singură diferență: clasa destinație.
    // ==================================================================================
    private void initSecondListener() {

        // Listener pe al doilea FAB (jos-stânga, iconița cu ciocan).
        btnVlad.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {

                // Variabila se numește `intent2` — suficient pentru a nu se confunda
                //   cu `intent` din metoda de mai sus, deși sunt în metode diferite.
                Intent intent2 = new Intent(MainActivity.this, com.example.group1098.activities.PlaceCiocanul.class);

                // Același launcher: un singur contract de rezultat pentru două ecrane.
                launcher.launch(intent2);
            }
        });
    }

    // ==================================================================================
    // METODA: initControls — FINDVIEWBYID ȘI CONFIGURAREA LISTEI
    // ==================================================================================
    // CE FACE: leagă câmpurile Java de view-urile din XML și configurează RecyclerView
    //   (layout manager + adaptor).
    // CUM: 1) FAB; 2) RecyclerView; 3) layout manager; 4) adaptor; 5) al doilea FAB.
    // RISC: `setLayoutManager` trebuie apelat ÎNAINTE de `setAdapter`. Fără layout
    //   manager, RecyclerView nu desenează nimic și scrie în Logcat:
    //   „No layout manager attached; skipping layout".
    // REF: capitolul 22, 22.2 — aceeași metodă, cu `ListView.setAdapter` în loc.
    // ==================================================================================
    private void initControls() {

        // 1. FAB-ul de inserare, după ID-ul din `activity_main.xml`.
        fabInsert = findViewById(R.id.floatingActionButton);

        // Codul versiunii vechi, păstrat comentat — legarea ListView-ului:
        // listView = findViewById(R.id.listView);
        // listView.setAdapter(movieAdapter);
        // OBSERVAȚIE: ambele linii sunt comentate, dar `R.id.listView` nici măcar nu
        //   mai există în layout. Dacă le-ai decomenta, fișierul NU AR COMPILA.

        // 2. RecyclerView-ul. ID-ul `rvMovies` există în layout-ul versiunii 2.
        rvMovies = findViewById(R.id.rvMovies);

        // 3. Layout manager: OBLIGATORIU, înainte de adaptor. `this` este Context-ul.
        //    LinearLayoutManager = listă verticală, un rând sub altul.
        //    Alte variante: GridLayoutManager (grilă), StaggeredGridLayoutManager.
        rvMovies.setLayoutManager(new LinearLayoutManager(this));

        // 4. Adaptorul construit în `onCreate`. Din acest moment, RecyclerView știe
        //    câte rânduri are lista și cum să le construiască.
        rvMovies.setAdapter(movieAdapter);

        // 5. Al doilea FAB. Căutat DUPĂ ce adaptorul este legat — ordinea între
        //    view-uri nu contează, toate există de la `setContentView`.
        btnVlad = findViewById(R.id.btnVlad);
    }

    // ==================================================================================
    // METODA: addSampleMovies — DATELE DEMO
    // ==================================================================================
    // CE FACE: adaugă în listă trei filme construite cu constructorul cu 10 parametri.
    // CUM: trei apeluri `new Movie(...)`, fiecare cu aceeași ordine de argumente.
    // RISC: constructorul este POZIȚIONAL. Inversarea a două argumente de ACELAȘI tip
    //   (String cu String, boolean cu boolean) compilează și produce date greșite.
    // REF: capitolul 22, 22.1 — tabelul pozițiilor din constructorul lui `Movie`.
    // ==================================================================================
    private void addSampleMovies() {

        // Filmul 1. Argumentele, pe poziții:
        //   1 title="Inception", 2 release=16 iulie 2010, 3 genre="Sci-Fi",
        //   4 budget=160000000, 5 duration=148, 6 rating=4.5f,
        //   7 watched=true, 8 approval="PG-13", 9 onWatchlist=false, 10 posterUrl=...
        movies.add(new Movie(

                // 1. Titlul.
                "Inception",

                // 2. Data. `GregorianCalendar(an, lună, zi)` — luna este 0-based:
                //    `Calendar.JULY` este 6, nu 7. `.getTime()` transformă calendarul
                //    în `Date`, tipul cerut de model.
                new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),

                // 3. Genul — text liber, nu enum.
                "Sci-Fi",

                // 4. Bugetul — `double`, de aceea fără sufix.
                160000000,

                // 5. Durata în minute — `int`.
                148,

                // 6. Ratingul — `float`: sufixul `f` este OBLIGATORIU. Fără el,
                //    literalul `4.5` este `double` și apelul nu compilează.
                4.5f,

                // 7. „Am văzut filmul" — boolean.
                true,

                // 8. Ghidajul parental — textul butonului radio.
                "PG-13",

                // 9. „Pe lista de revăzut" — al doilea boolean, independent de primul.
                false,

                // 10. URL-ul posterului. Aici este un URL de exemplu: aplicația nu
                //     descarcă nicio imagine, deci valoarea nu ajunge niciodată pe ecran.
                "https://example.com/posters/inception.jpg"));

        // Filmul 2. Aceeași structură, alte valori. `Calendar.NOVEMBER` = 10 (0-based).
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

        // Filmul 3. `Calendar.MARCH` = 2 (0-based); rating 5f — nota maximă;
        //   `watched=false`, `onWatchlist=true`: filmul este pus deoparte, nu văzut.
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
    // METODA: onMovieClick — IMPLEMENTAREA CONTRACTULUI DE CLICK
    // ==================================================================================
    // CE FACE: primește de la adaptor filmul și poziția, apoi pornește ItemActivity
    //   în modul editare, cu ambele extra-uri.
    // CUM: 1) Intent explicit; 2) pune filmul; 3) pune poziția; 4) lansează.
    // RISC: metoda folosește `movies.get(position)`, NU parametrul `movie`. Cele două
    //   sunt consistente aici (adaptorul citește din aceeași listă). Dacă adaptorul ar
    //   primi altă listă, parametrul ar fi sursa corectă.
    // REF: blocul comentat din `initListeners` — acesta este `onItemClick` mutat.
    // ==================================================================================
    @Override
    public void onMovieClick(Movie movie, int position) {

        // 1. Același Intent explicit ca la FAB, dar cu extra-uri.
        Intent intent = new Intent(MainActivity.this, com.example.group1098.activities.ItemActivity.class);

        // 2. Filmul, serializat în Bundle. `putExtra(String, Serializable)`.
        //    Se ia din listă după poziție — sursa de adevăr a ecranului.
        intent.putExtra(MOVIE_EXTRA, movies.get(position));

        // 3. Poziția: prezența ei este semnalul „mod editare" pentru ItemActivity.
        intent.putExtra(POSITION_EXTRA, position);

        // 4. Pornirea. Rezultatul (filmul modificat) vine în callback-ul din `onCreate`
        //    și intră pe ramura `movies.set(position, movie)`.
        launcher.launch(intent);
    }
}
```

**Ce s-a schimbat față de versiunea veche, în trei locuri:**

| Loc | Versiunea veche (cap. 22) | Versiunea 2 (aici) |
|---|---|---|
| câmpul listei | `ListView listView` | `RecyclerView rvMovies` |
| adaptorul | `ArrayAdapter<Movie>` | `MovieAdapter` (clasă proprie) |
| click pe rând | `listView.setOnItemClickListener` | `onMovieClick`, apelat din `ViewHolder` |
| configurare | `listView.setAdapter(...)` | `setLayoutManager(...)` + `setAdapter(...)` |
| al doilea buton | nu există | `btnVlad` -> `PlaceCiocanul` |

**Ordinea din `onCreate`, într-o singură privire:**

```
onCreate
  |-- super.onCreate
  |-- EdgeToEdge.enable          barele devin transparente
  |-- setContentView             arborele de view-uri există
  |-- insets pe R.id.main         padding = status + navigare
  |-- addSampleMovies            movies = [Inception, Toy Story, The Matrix]
  |-- new MovieAdapter(movies, this)    adaptorul ține REFERINȚA la `movies`
  |-- initControls               rvMovies + LayoutManager + setAdapter
  |-- initListeners              fabInsert -> launcher (launcher este încă null)
  |-- initSecondListener         btnVlad  -> launcher (launcher este încă null)
  +-- registerForActivityResult  launcher creat
        |
        v
  ecranul este vizibil; primul click găsește `launcher` DEJA atribuit
```

**De ce `launcher` poate fi `null` în listeneri fără să crape:** clasa anonimă nu copiază valoarea câmpului la creare; ea ține referința către obiectul `MainActivity` și citește câmpul **la momentul click-ului**. Între crearea listener-ului și primul click se află tot restul lui `onCreate`, deci atribuirea s-a făcut. Este o dependență de ordine care funcționează, dar merită știută: dacă ai apela `launcher.launch(...)` **direct** în `onCreate`, înainte de linia de înregistrare, ai lua `NullPointerException`.

---

## 38.2 `MovieAdapter.java` — adaptorul, cu ViewHolder

Acesta este fișierul care lipsește din versiunea veche. `ArrayAdapter` era o clasă gata făcută: îi dădeai lista și un layout de rând, iar ea afișa `toString()`-ul fiecărui element. Aici adaptorul este scris de mână, pentru că rândul nu mai este un `TextView`, ci un card întreg, cu poster, titlu, stele și patru etichete — iar cine le umple trebuie decis de tine.

```java
/*
 * ======================================================================================
 * FIȘIER: MovieAdapter.java — ADAPTORUL LISTEI
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   Puntea dintre `ArrayList<Movie>` (date) și `RecyclerView` (UI). Extinde
 *   `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>` și conține două clase:
 *   adaptorul propriu-zis și `ViewHolder`-ul care ține referințele rândului.
 *
 * DE CE EXISTĂ:
 *   `RecyclerView` nu știe să afișeze un `Movie`. El știe doar să ceară:
 *   „câte elemente ai?" (`getItemCount`), „dă-mi o vedere de rând" (`onCreateViewHolder`)
 *   și „umple vederea asta cu elementul de la poziția N" (`onBindViewHolder`).
 *
 * DE CE DEPINDE:
 *   - `Movie` (modelul) și `IMovieListener` (contractul de click),
 *   - `R.layout.movie_item` (layout-ul rândului) și nouă ID-uri din el,
 *   - `Chip` din Material Components, `RatingBar` și `ImageView` din framework.
 *
 * CINE DEPINDE DE EL:
 *   `MainActivity` îl construiește (`new MovieAdapter(movies, this)`) și îl pasează
 *   lui `rvMovies.setAdapter(...)`.
 *
 * CE NU FACE:
 *   Nu deține lista (o primește prin referință), nu decide aranjarea rândurilor
 *   (o face `LayoutManager`-ul), nu știe ce se întâmplă la click — doar anunță
 *   listener-ul.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   `rvMovies.setAdapter(...)` nu ar avea argument; lista ar rămâne goală pe ecran,
 *   deși `movies` ar avea trei elemente.
 * ======================================================================================
 */

// Pachetul `adapter`: separat de `activities` și de `model`. Adaptorul depinde de amândouă,
//   dar niciuna dintre ele nu depinde de adaptor în afară de MainActivity.
package com.example.group1098.adapter;

// LayoutInflater: singurul mod de a transforma un XML într-un arbore de view-uri.
import android.view.LayoutInflater;

// View: tipul rădăcinii unui rând inflate și tipul parametrului din `onClick`.
import android.view.View;

// ViewGroup: părintele în care va sta rândul (RecyclerView-ul însuși).
//   Din el se ia `Context`-ul pentru inflate.
import android.view.ViewGroup;

// ImageView: posterul. Declarat în holder, dar NEUMPLUT în `onBindViewHolder`.
import android.widget.ImageView;

// RatingBar: stelele. Declarat în holder, dar NEUMPLUT — rămâne la valoarea din XML.
import android.widget.RatingBar;

// TextView: cele patru texte ale cardului (titlu, subtitlu, valoare rating, facts).
import android.widget.TextView;

// NonNull: adnotare de contract. Nu schimbă bytecode-ul; îi spune lui lint (și
//   cititorului) că parametrul nu are voie să fie null, iar returul nu este null.
import androidx.annotation.NonNull;

// RecyclerView: clasa de bază. `RecyclerView.Adapter` și `RecyclerView.ViewHolder`
//   sunt clasele interioare pe care le extindem aici.
import androidx.recyclerview.widget.RecyclerView;

// R: `R.layout.movie_item` și cele nouă ID-uri căutate cu `findViewById`.
import com.example.group1098.R;

// Movie: elementul afișat.
import com.example.group1098.model.Movie;

// Chip: eticheta rotunjită din Material Components. Trei bucăți pe card.
import com.google.android.material.chip.Chip;

// SimpleDateFormat: transformă `Date` în an, pentru subtitlul „gen. an".
import java.text.SimpleDateFormat;

// ArrayList: tipul listei primite prin constructor.
import java.util.ArrayList;

/*
 * ======================================================================================
 * BLOC DE TEORIE: CONTRACTUL RecyclerView.Adapter
 * ======================================================================================
 *
 * 1. **Trei metode obligatorii, nimic altceva:**
 *      - `getItemCount()`        -> câte rânduri există în total;
 *      - `onCreateViewHolder()`  -> construiește o vedere de rând GOALĂ;
 *      - `onBindViewHolder()`    -> umple o vedere EXISTENTĂ cu date.
 *
 * 2. **De ce două metode și nu una.** `onCreateViewHolder` este scump: citește XML-ul
 *    și construiește arborele de view-uri. Se apelează o singură dată pentru fiecare
 *    rând care încape pe ecran. `onBindViewHolder` este ieftin: doar `setText`.
 *    Se apelează de fiecare dată când un rând reapare la derulare. Dacă ai 10 000 de
 *    filme și 8 rânduri vizibile, se creează ~10 vederi și se leagă de mii de ori.
 *
 * 3. **Reciclarea.** Când un rând iese din ecran, vederea lui nu se aruncă: intră
 *    într-un bazin. Când e nevoie de un rând nou, se scoate o vedere din bazin și
 *    se re-leagă — fără inflate. De aici numele „RecyclerView".
 *
 *    ecran:  [0][1][2][3][4][5][6][7]      (8 vizibile)
 *    derulezi in jos:
 *       randul 0 iese  ->  vederea lui ajunge in bazin
 *       randul 8 intra <-  primeste vederea reciclata, re-legata cu datele lui 8
 *
 * 4. **ViewHolder = cache-ul de findViewById.** Fără el, fiecare bind ar căuta din nou
 *    opt view-uri prin arbore. `ViewHolder` le ține o dată, în câmpuri `final`.
 *    `RecyclerView` garantează că obiectul `ViewHolder` călătorește împreună cu vederea
 *    lui, deci `holder.title` este mereu TextView-ul rândului curent.
 *
 * 5. **Poziția nu este a ta.** `position` vine ca parametru la bind, dar la click nu
 *    mai există: se cere cu `getAbsoluteAdapterPosition()`. Între timp, lista se poate
 *    schimba, iar poziția salvată într-un câmp ar deveni greșită.
 *
 * 6. **`viewType`.** Aici este ignorat: toate rândurile arată la fel. Dacă ai avea două
 *    tipuri de carduri (film văzut / film nou), `getItemViewType(position)` ar decide,
 *    iar `onCreateViewHolder` ar primi un `viewType` diferit și ar inflata alt XML.
 * ======================================================================================
 */

// Adaptorul. Generic-ul din `<...>` este TIPUL HOLDER-ULUI, nu tipul elementului.
//   De aceea `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`: clasa interioară
//   este referită cu numele complet, pentru că apare în semnătura clasei care o conține.
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    // ==================================================================================
    // CELE DOUĂ REFERINȚE
    // ==================================================================================
    // Lista NU se copiază: adaptorul ține referința primită de la activitate.
    //   Consecința bună: `movies.add(...)` din MainActivity se vede aici imediat,
    //   fără să trebuiască reconstruit adaptorul.
    // Consecința periculoasă: dacă MainActivity ar înlocui lista cu alta
    //   (`movies = new ArrayList<>()`), adaptorul ar rămâne pe cea veche.
    // `final` = referința nu se reasignează. Conținutul se poate schimba liber.
    // Fără modificator de acces = vizibil în pachetul `adapter`.
    final ArrayList<Movie> movies;

    // Listener-ul de click: cine primește evenimentul. Aici, MainActivity.
    // RISC: nu se verifică `null`. Dacă ai construi adaptorul cu `null`, totul ar
    //   funcționa până la primul click, când ai lua NullPointerException.
    final IMovieListener listener;

    // ==================================================================================
    // CONSTRUCTORUL — DOAR DOUĂ ATRIBUIRI
    // ==================================================================================
    // CE FACE: primește lista și listener-ul și le ține pentru toată viața adaptorului.
    // CUM: două atribuiri, fără logică.
    // RISC: nu se clonează lista. Dacă ai vrea o copie, ar trebui `new ArrayList<>(movies)`
    //   — dar atunci modificările din activitate nu s-ar mai vedea în listă.
    // REF: `new MovieAdapter(movies, this)` în MainActivity, 38.1.
    // ==================================================================================
    public MovieAdapter(ArrayList<Movie> movies, IMovieListener listener) {

        // `this.movies` = câmpul; `movies` = parametrul. Aceeași capcană ca la `Movie`.
        this.movies = movies;

        // Același model pentru listener.
        this.listener = listener;
    }

    // ==================================================================================
    // METODA: onCreateViewHolder — CONSTRUCȚIA UNUI RÂND GOL
    // ==================================================================================
    // CE FACE: umflă `movie_item.xml` într-o vedere nouă și o învelește într-un holder.
    // CUM: 1) ia inflater-ul din contextul părintelui; 2) umflă layout-ul cu `false`;
    //   3) întoarce un `MovieViewHolder` nou.
    // RISC: al treilea argument trebuie să fie `false`. Cu `true`, vederea ar fi lipită
    //   imediat de părinte, iar RecyclerView ar încerca să o adauge din nou -> crash.
    // REF: capitolul 23, exercițiul despre `ViewHolder` — același cod, pas cu pas.
    // ==================================================================================
    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {

        // 1. Inflater-ul se ia DIN CONTEXTUL PĂRINTELUI, nu din activitate: adaptorul
        //    nu are și nu trebuie să aibă o referință către Activity. `parent.getContext()`
        //    este activitatea care găzduiește RecyclerView-ul, deci tema este cea corectă.
        // 2. `inflate(R.layout.movie_item, parent, false)`:
        //      - primul argument: XML-ul rândului;
        //      - al doilea: părintele, din care se iau `LayoutParams`-ul corect;
        //      - al treilea `false`: NU atașa acum. RecyclerView decide când.
        //    „Nu atașa" este răspunsul corect în 99% din cazurile de adaptor.
        // 3. Rezultatul este o vedere de card, încă fără nicio dată în ea.
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.movie_item, parent, false);

        // 4. Se învelește în holder. Din acest moment, `holder.title` etc. sunt valide:
        //    constructorul holder-ului face toate `findViewById`-urile.
        return new MovieViewHolder(view);
    }

    // ==================================================================================
    // METODA: onBindViewHolder — UMPLEREA RÂNDULUI CU DATE
    // ==================================================================================
    // CE FACE: ia filmul de la poziția dată și scrie în holder titlul și subtitlul.
    // CUM: 1) un formatator de an; 2) filmul; 3) titlul; 4) „gen. an".
    // RISC: doar DOUĂ câmpuri sunt umplute din nouă. Restul rămân cu valorile din XML
    //   — vezi BUG-ul de mai jos.
    // REF: capitolul 22, 22.6 — `movie_item.xml`, cardul care se vede acum.
    // ==================================================================================
    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {

        // 1. Formatator pentru an. Se creează LA FIECARE BIND — un obiect nou pentru
        //    fiecare rând, de fiecare dată când rândul reapare la derulare.
        // RISC: `SimpleDateFormat` este scump de construit. Corect ar fi un câmp
        //   `private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy");`
        //   construit o singură dată. Aici, cu trei filme, nu se observă.
        // ATENȚIE: `"yyyy"` este an calendaristic. `"YYYY"` ar fi an de săptămână
        //   (ISO week-year) și ar da 2027 pentru câteva zile din decembrie 2026.
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy");

        // 2. Filmul de la poziția cerută. `position` este dat de RecyclerView și este
        //    garantat în intervalul 0..getItemCount()-1 în timpul unui bind.
        Movie movie = movies.get(position);

        // 3. Titlul. `setText` acceptă CharSequence; `getTitle()` întoarce String.
        holder.title.setText(movie.getTitle());

        // 4. Subtitlul: „gen. an". Trei observații, toate verificabile:
        //    - `movie.getGenre()` este deja `String`; `.toString()` pe un String
        //      întoarce ACELAȘI obiect — este redundant, dar inofensiv.
        //      RISC: dacă `genre` ar fi null, apelul ar arunca NullPointerException.
        //      DANGER!: excepția izbucnește în onBindViewHolder, în timpul derulării,
        //        nu la pornire — un crash care apare abia când lista ajunge la filmul
        //        respectiv. Aici `addSampleMovies` și formularul pun mereu gen, deci nu
        //        se întâmplă; dar modelul permite `null` prin constructorul gol.
        //    - separatorul este „. " (punct și spațiu), nu „ · " cum sugerează
        //      comentariul din `movie_item.xml`. Rezultatul vizibil: „Sci-Fi. 2010".
        //    - `sdf.format(movie.getRelease())` cere un `Date` nenull. Dacă filmul
        //      ar avea data null (posibil prin constructorul gol), ar arunca NPE.
        holder.subtitle.setText(movie.getGenre().toString() + ". " + sdf.format(movie.getRelease()));

        // OBSERVAȚIE: metoda se termină aici. Nu există apel `super.onBindViewHolder`.
        //   Nu este obligatoriu — clasa de bază nu face nimic în el.
    }

    // ==================================================================================
    // METODA: getItemCount — CÂTE RÂNDURI EXISTĂ
    // ==================================================================================
    // CE FACE: întoarce numărul de elemente din listă.
    // CUM: `movies.size()`, citit la fiecare apel — deci mereu la zi.
    // RISC: dacă ai returna o valoare constantă sau un câmp actualizat manual,
    //   RecyclerView ar cere bind-uri pentru poziții inexistente -> IndexOutOfBounds.
    // REF: `notifyDataSetChanged()` din MainActivity — anunțul care face RecyclerView
    //   să întrebe din nou această metodă.
    // ==================================================================================
    @Override
    public int getItemCount() {

        // Sursa de adevăr este lista, nu un contor paralel.
        return movies.size();
    }

    /*
     * ==================================================================================
     * BUG: CARDUL AFIȘEAZĂ DATE STATICE PENTRU TOATE FILMELE
     * ==================================================================================
     * `MovieViewHolder` caută nouă view-uri, dar `onBindViewHolder` scrie doar în două:
     * `title` și `subtitle`. Celelalte șapte rămân exact cum au fost inflate din XML:
     *
     *   din XML (aceeași valoare pe FIECARE rând)     din model (ignorat)
     *   --------------------------------------------  ------------------------
     *   movieFacts      = "142 min  ·  $160M"          duration, budget
     *   movieRatingValue= "4.5"                        rating
     *   movieRating     = 0 stele (fără `rating=` in XML)  rating
     *   chipApproval    = "Approved"                   approval
     *   chipWatched     = "Watched"                    watched
     *   chipWatchlist   = "Watchlist"                  onWatchlist
     *   moviePoster     = iconița galeriei             posterUrl
     *
     * Consecința: Inception (148 min, $160M, PG-13) și Toy Story (81 min, $30M, G)
     * apar cu ACELEAȘI facts-uri și ACELEAȘI etichete. Datele sunt în model, dar nu
     * ajung niciodată pe ecran. Nu este o eroare de sintaxă: compilează și rulează.
     * ==================================================================================
     */

    // ==================================================================================
    // CLASA INTERIOARĂ: MovieViewHolder
    // ==================================================================================
    // CE FACE: ține referințele celor nouă view-uri ale cardului și leagă click-ul.
    // CUM: `findViewById` o singură dată, în constructor; click pe `itemView`.
    // RISC: este o clasă interioară NEstatică — ține o referință implicită către adaptor.
    //   Aici este convenabil (vede `movies` și `listener` direct), dar înseamnă că
    //   holder-ul nu poate trăi fără adaptor.
    // REF: `RecyclerView.ViewHolder`, care ține `itemView` — vederea rândului întreg.
    // ==================================================================================
    class MovieViewHolder extends RecyclerView.ViewHolder {

        // ==============================================================================
        // CELE NOUĂ CÂMPURI — CACHE-UL DE findViewById
        // ==============================================================================
        // Toate `final`: se atribuie o dată, în constructor, și nu se mai schimbă.
        //   Un rând nou = un holder nou = un set nou de referințe.
        // Cele nouă corespund celor nouă ID-uri din `movie_item.xml` pe care le folosește
        //   codul. În layout mai există două ID-uri pe care holder-ul NU le caută:
        //   `movieStatusGroup` (ChipGroup-ul) și `chipCiocan` (al patrulea chip).
        // ==============================================================================

        // Posterul. Căutat, dar niciodată umplut — vezi BUG-ul de mai sus.
        final ImageView poster;

        // Titlul — UMPLUT în `onBindViewHolder`.
        final TextView title;

        // Subtitlul „gen. an" — UMPLUT în `onBindViewHolder`.
        final TextView subtitle;

        // Stelele. Niciodată setate: `android:rating` nu există în XML, deci 0 stele.
        final RatingBar rating;

        // Valoarea numerică a ratingului. Rămâne „4.5" din XML pentru orice film.
        final TextView ratingValue;

        // „durata · bugetul". Rămâne „142 min · $160M" din XML.
        final TextView facts;

        // Cele trei etichete de stare. Raman textele din XML.
        final Chip chipApproval;
        final Chip chipWatched;
        final Chip chipWatchList;

        // ==============================================================================
        // CONSTRUCTORUL HOLDER-ULUI
        // ==============================================================================
        // CE FACE: leagă fiecare câmp de view-ul lui din rândul primit și instalează
        //   listener-ul de click pe rândul întreg.
        // CUM: `super(itemView)` obligatoriu, apoi nouă `findViewById`, apoi un listener.
        // RISC: `findViewById` pe `itemView`, NU pe activitate. Dacă ai căuta în
        //   activitate, ai găsi primul view cu acel ID din tot ecranul — nu neapărat
        //   din rândul curent.
        // REF: capitolul 22, 22.6 — ID-urile căutate aici sunt exact cele din layout.
        // ==============================================================================
        public MovieViewHolder(@NonNull View itemView) {

            // `super(itemView)` este obligatoriu: clasa de bază păstrează vederea
            //   rândului și o folosește pentru poziționare și pentru animații.
            super(itemView);

            // Fiecare `findViewById` întoarce `View`; atribuirea într-un câmp de tip
            //   concret face cast-ul automat (generics), fără `(TextView)` scris de mână.
            //   Dacă ID-ul ar lipsi din layout, s-ar întoarce `null` — fără eroare la
            //   compilare, doar un NPE la primul bind.
            poster = itemView.findViewById(R.id.moviePoster);
            title = itemView.findViewById(R.id.movieTitle);
            subtitle = itemView.findViewById(R.id.movieSubtitle);
            rating = itemView.findViewById(R.id.movieRating);
            ratingValue = itemView.findViewById(R.id.movieRatingValue);
            facts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchList = itemView.findViewById(R.id.chipWatchlist);

            // ==========================================================================
            // CLICK-UL PE RÂND
            // ==========================================================================
            // Aici este întregul mecanism care înlocuiește `setOnItemClickListener`.
            // Se leagă pe `itemView` — cardul întreg, nu pe un text anume.
            // DE CE în constructor și nu în bind: listener-ul este același pentru toată
            //   viața vederii; legarea lui la fiecare bind ar aloca un obiect degeaba.
            // ==========================================================================
            itemView.setOnClickListener(new View.OnClickListener() {

                // Se execută la apăsare. `v` este cardul.
                @Override
                public void onClick(View v) {

                    // Poziția se cere ACUM, nu se ține într-un câmp.
                    // `getAbsoluteAdapterPosition()` întoarce poziția în lista
                    //   adaptorului, sau `NO_POSITION` (-1) dacă rândul a fost scos
                    //   din listă între timp (animație de ștergere, listă schimbată).
                    int pos = getAbsoluteAdapterPosition();

                    // Garda: poziție validă? Fără ea, `movies.get(-1)` ar arunca
                    //   IndexOutOfBoundsException. Aici nu se șterg elemente, dar
                    //   garda este obligatorie ca tipar.
                    if (pos != RecyclerView.NO_POSITION) {

                        // Filmul de la poziția respectivă.
                        Movie movie = movies.get(pos);

                        // Anunțul către activitate. `listener` este MainActivity.
                        //   Din acest apel se ajunge în `onMovieClick`, care pornește
                        //   ItemActivity cu două extra-uri (38.1).
                        listener.onMovieClick(movie, pos);
                    }
                }
            });
        }
    }
}
```

**Ordinea în care RecyclerView apelează adaptorul:**

```
RecyclerView vrea să afișeze lista
   |
   |-- getItemCount() .............................. 3
   |
   |-- pentru fiecare rând vizibil (0, 1, 2):
   |     |-- onCreateViewHolder(parent, 0) ....... un card NOU, gol
   |     +-- onBindViewHolder(holder, pozitie) .... title + subtitle scrise
   |
   +-- la derulare:
         |-- vederea care iese -> în bazinul de reciclare
         +-- vederea care intra:
               onBindViewHolder(holder RECICLAT, poziție nouă)
               (fără onCreateViewHolder, fără inflate)
```

**Trei lucruri pe care le vei fi întrebat despre acest fișier:**

1. **„De ce două metode, `onCreateViewHolder` și `onBindViewHolder`?"** Pentru că inflate-ul este scump și se face o singură dată per rând vizibil, iar legarea datelor este ieftină și se face la fiecare reapariție. Reciclarea este tot rostul widget-ului.
2. **„Cum ajunge click-ul la activitate?"** Prin `IMovieListener`: adaptorul nu cunoaște `MainActivity`, doar interfața. Activitatea se pasează pe sine în constructor.
3. **„De ce `getAbsoluteAdapterPosition()` și nu câmpul `position` din bind?"** Pentru că poziția se poate schimba între bind și click. Metoda o cere la momentul evenimentului și întoarce `NO_POSITION` când nu mai este validă.

---

## 38.3 `IMovieListener.java` — contractul de click

Cel mai mic fișier din aplicație: șapte linii, o singură metodă. Este însă piesa care face diferența dintre versiunea veche și cea nouă: înlocuiește `AdapterView.OnItemClickListener`, pe care `ListView` îl oferea gata făcut, cu un contract scris de tine.

```java
/*
 * ======================================================================================
 * FIȘIER: IMovieListener.java — CONTRACTUL DE CLICK PE RÂND
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   O interfață cu o singură metodă. Spune ce trebuie să știe să facă cineva care
 *   vrea să fie anunțat când utilizatorul atinge un rând din listă.
 *
 * DE CE EXISTĂ:
 *   `RecyclerView` nu are `setOnItemClickListener`. Click-ul se leagă manual, pe
 *   `itemView`, în `ViewHolder` (38.2) — iar de acolo trebuie să ajungă undeva.
 *   Interfața este acel „undeva", fără ca adaptorul să știe cine este destinatarul.
 *
 * DE CE DEPINDE:
 *   Doar de `Movie` (tipul parametrului). Nu depinde de Android, de `View`,
 *   de `Context` și de nicio clasă din aplicație.
 *
 * CINE DEPINDE DE EL:
 *   - `MovieAdapter` — are un câmp `IMovieListener` și îl apelează la click;
 *   - `MainActivity` — îl implementează și se pasează pe sine adaptorului.
 *
 * CE NU FACE:
 *   Nu știe ce se întâmplă după click, nu pornește activități, nu ține poziția.
 *   Este doar o semnătură.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   Adaptorul ar trebui să primească direct un `MainActivity` — adică exact cuplarea
 *   pe care interfața o evită. Iar dacă ai schimba semnătura metodei, cele două
 *   locuri care depind de ea (adaptorul și activitatea) ar refuza să compileze.
 * ======================================================================================
 */

// Pachetul `adapter`, nu `activities`: contractul aparține adaptorului, care îl cere.
//   MainActivity îl importă de aici. Direcția dependenței: activities -> adapter -> model.
package com.example.group1098.adapter;

// `Movie` este tipul transportat de eveniment — nu `Object`, nu `View`.
import com.example.group1098.model.Movie;

/*
 * ======================================================================================
 * BLOC DE TEORIE: INTERFAȚA CA CALLBACK (INVERSION OF CONTROL)
 * ======================================================================================
 *
 * 1. **Problema.** Un rând de listă este o vedere inertă: știe să se deseneze, nu știe
 *    ce înseamnă „atingerea mea". Cineva trebuie să decidă ce se întâmplă la click —
 *    iar acel cineva este ACTIVITATEA, nu adaptorul.
 *
 * 2. **Soluția naivă.** Adaptorul ar putea primi direct `MainActivity` și ar putea
 *    construi el `Intent`-ul. Ar funcționa, dar adaptorul ar depinde de trei lucruri
 *    care nu au legătură cu desenatul unui card: clasa `ItemActivity`, constantele
 *    `MOVIE_EXTRA` / `POSITION_EXTRA` și un `Context` pentru `startActivity`.
 *
 * 3. **Soluția cu interfață.** Adaptorul depinde de UN SINGUR nume: `IMovieListener`.
 *    Nu știe cine îl implementează și nici ce se întâmplă după apel. Activitatea se
 *    pasează pe sine (`this`) și își asumă comportamentul.
 *
 * 4. **Inversion of control.** Nu adaptorul cheamă activitatea „pe nume"; el cheamă o
 *    metodă dintr-un contract, iar activitatea a decis să răspundă la el. Controlul
 *    asupra a „ce se întâmplă" este inversat față de fluxul normal de apeluri.
 *
 * 5. **Consecința practică la examen.** Pentru cerința „leagă click-ul pe rând de
 *    pornirea altei activități", răspunsul are exact trei piese:
 *      1) interfața (acest fișier),
 *      2) apelul din ViewHolder (`listener.onMovieClick(...)`),
 *      3) `implements` pe activitate + `new MovieAdapter(movies, this)`.
 * ======================================================================================
 */
// `public interface`: public = vizibil din orice pachet; interface = contract fără
//   implementare. Metodele sunt implicit `public abstract`.
public interface IMovieListener {

    // ==================================================================================
    // METODA: onMovieClick — SINGURA CERINȚĂ A CONTRACTULUI
    // ==================================================================================
    // CE FACE: definește ce primește cineva care vrea să afle de un click pe rând.
    // CUM: nu are corp — fiecare implementare decide ce face (aici: pornește ecranul).
    // RISC: `Movie` poate fi null dacă lista ar conține un element null; `position`
    //   este poziția în listă, valabilă doar dacă lista nu s-a schimbat între timp.
    // REF: apelul din `MovieAdapter.MovieViewHolder` și implementarea din MainActivity.
    // ==================================================================================
    void onMovieClick(Movie movie, int position);
}
```

**De ce o interfață și nu un `Intent` trimis direct din adaptor.** Adaptorul ar putea, tehnic, să construiască el `Intent`-ul și să pornească `ItemActivity`. Atunci ar depinde de `ItemActivity`, de constantele `MOVIE_EXTRA` și `POSITION_EXTRA` și de un `Context` — trei dependențe în plus. Cu interfața, adaptorul depinde de un nume de metodă, iar activitatea rămâne singurul loc care știe ce se întâmplă la click.

```
   FARA interfata                      CU interfata
   -------------                       ------------
   MovieAdapter                        MovieAdapter
     |  știe ItemActivity               |  știe doar IMovieListener
     |  știe MOVIE_EXTRA                |
     |  știe Context                    v
     +--> Intent                     MainActivity (implementează)
          către ItemActivity           |  știe ItemActivity
                                        +--> Intent către ItemActivity
```

**Aceeași funcționalitate, scrisă cu lambda.** Interfața are o singură metodă abstractă, deci este o interfață funcțională: `IMovieListener` poate fi scrisă și ca `(movie, position) -> { ... }`. Aici s-a ales clasa anonimă / implementarea pe activitate, pentru că la examen se cere forma explicită, cu `implements` în declarația clasei.

---

## 38.4 `PlaceCiocanul.java` — ecranul nou

Al treilea ecran al aplicației și cel mai simplu: un singur buton, un singur mesaj. Este interesant nu prin ce face, ci prin cele două tipare pe care le arată — varianta `Window` a lui edge-to-edge și un `RISC` clasic despre `String.valueOf(int)`.

```java
/*
 * ======================================================================================
 * FIȘIER: PlaceCiocanul.java — ECRANUL DE TEST
 * ======================================================================================
 * CE ESTE ACEST FIȘIER:
 *   O activitate minimă, deschisă de al doilea FAB din ecranul principal. Are un
 *   singur buton, care afișează un `Toast`. Nu citește și nu scrie niciun `Movie`.
 *
 * DE CE EXISTĂ:
 *   Este un ecran de probă adăugat în versiunea 2: verifică faptul că al doilea FAB
 *   pornește o activitate și că manifestul o declară. Nu are rol în fluxul de date.
 *
 * DE CE DEPINDE:
 *   - `R.layout.activity_place_ciocanul` și două ID-uri: `main`, `floatingActionButton2`;
 *   - `R.string.app_name` (folosit greșit — vezi RISC-ul din `onCreate`);
 *   - intrarea din `AndroidManifest.xml`, fără care nu poate fi pornită.
 *
 * CINE DEPINDE DE EL:
 *   Doar `MainActivity.initSecondListener()`, care îl lansează prin `launcher`.
 *
 * CE NU FACE:
 *   Nu întoarce niciun rezultat: nu apelează `setResult`, deci la întoarcere codul
 *   este `RESULT_CANCELED` și callback-ul din MainActivity nu face nimic.
 *
 * CE S-AR RUPE FĂRĂ EL:
 *   `btnVlad` ar porni o clasă inexistentă -> `ActivityNotFoundException` la runtime.
 * ======================================================================================
 */

// Pachetul ecranelor. Aici se află și MainActivity și ItemActivity.
package com.example.group1098.activities;

// Bundle: doar în semnătura lui `onCreate`, ca peste tot.
import android.os.Bundle;

// View: tipul parametrului din `onClick`.
import android.view.View;

// Toast: mesajul scurt afișat la apăsarea butonului.
import android.widget.Toast;

// AppCompatActivity: aceeași bază ca celelalte două activități.
import androidx.appcompat.app.AppCompatActivity;

// Insets: valorile barelor de sistem.
import androidx.core.graphics.Insets;

// ViewCompat: listener-ul de insets, compatibil pe orice versiune.
import androidx.core.view.ViewCompat;

// WindowCompat: varianta de edge-to-edge care primește un `Window`, nu o activitate.
//   MainActivity folosește `EdgeToEdge.enable(this)`; aici se folosește această formă.
import androidx.core.view.WindowCompat;

// WindowInsetsCompat: descrierea insets-urilor.
import androidx.core.view.WindowInsetsCompat;

// R: layout-ul și ID-urile.
import com.example.group1098.R;

// FloatingActionButton: butonul singur al ecranului.
import com.google.android.material.floatingactionbutton.FloatingActionButton;

// (două linii goale în sursă — păstrate ca atare)

/*
 * ======================================================================================
 * BLOC DE TEORIE: UN AL TREILEA ECRAN, ȘI DOUĂ API-URI PENTRU ACELAȘI LUCRU
 * ======================================================================================
 *
 * 1. **O activitate = un ecran.** `PlaceCiocanul` este a treia activitate a aplicației.
 *    Se declară în manifest (38.8), se pornește cu `Intent` explicit și se închide cu
 *    butonul Back al sistemului. Atât este necesar ca să existe.
 *
 * 2. **Două variante de edge-to-edge.** `MainActivity` folosește `EdgeToEdge.enable(this)`,
 *    care primește activitatea; aici se folosește `WindowCompat.enableEdgeToEdge(getWindow())`,
 *    care primește fereastra. Efectul este același: conținutul este desenat sub barele
 *    de sistem, iar padding-ul se aplică manual, din insets. Cele două rețete coexistă
 *    în același proiect: un detaliu de igienă, nu o eroare.
 *
 * 3. **Toast vs Snackbar.** `Toast` apare peste orice ecran, nu are nevoie de un părinte
 *    și dispare singur. `Snackbar` are nevoie de un `CoordinatorLayout` și stă în partea
 *    de jos a ecranului. Pentru un mesaj de test, `Toast` este alegerea minimală.
 *
 * 4. **Ce lipsește ca să fie un ecran real:** un `RecyclerView` cu ID și cu adaptor, un
 *    `ProgressBar` dimensionat corect, un mesaj din `strings.xml` în locul textului
 *    hardcodat și un `setResult` dacă ecranul ar trebui să întoarcă date.
 * ======================================================================================
 */
// Activitatea. Fără `implements`: acest ecran nu primește click-uri din nicio listă.
public class PlaceCiocanul extends AppCompatActivity {

    // Butonul ecranului. Numele `btn2` este ales de autor; ID-ul din XML este
    //   `floatingActionButton2`. Cele două nu trebuie să coincidă — legătura se face
    //   prin `findViewById`, nu prin nume.
    private FloatingActionButton btn2;

    // ==================================================================================
    // CÂMPUL `string` — DECLARAT, ATRIBUIT, NICIODATĂ CITIT
    // ==================================================================================
    // RISC: câmpul nu este folosit nicăieri. Este „cod mort": niciun `getText`, niciun
    //   `Toast`, niciun `Log` nu îl citește. Compilatorul nu se plânge, pentru că
    //   atribuirea este un efect secundar valid.
    // Numele `string` este și el o alegere slabă: descrie TIPUL, nu conținutul.
    // ==================================================================================
    private String string;

    // ==================================================================================
    // METODA: onCreate — TOT ECRANUL, ÎNTR-O SINGURĂ METODĂ
    // ==================================================================================
    // CE FACE: umflă layout-ul, aplică insets-urile, leagă butonul de un Toast și
    //   atribuie (inutil) câmpul `string`.
    // CUM: 1) super; 2) edge-to-edge; 3) setContentView; 4) insets; 5) findViewById;
    //   6) listener; 7) atribuirea greșită a lui `string`.
    // RISC: spre deosebire de MainActivity, aici nu există `initControls()` și
    //   `initListeners()`. Cu un singur buton, separarea nu merită — dar ordinea
    //   rămâne importantă: `findViewById` trebuie după `setContentView`.
    // REF: MainActivity (38.1) — aceeași schemă, cu metode separate.
    // ==================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // 1. Lanțul clasei de bază.
        super.onCreate(savedInstanceState);

        // 2. Edge-to-edge, varianta cu `Window`. `getWindow()` întoarce fereastra
        //    activității; metoda o configurează să deseneze sub bare.
        // OBSERVAȚIE: este echivalentul lui `EdgeToEdge.enable(this)` din MainActivity,
        //    scris cu altă API. Ambele fac același lucru; proiectul le amestecă.
        WindowCompat.enableEdgeToEdge(getWindow());

        // 3. Arborele de view-uri din layout-ul ecranului nou.
        setContentView(R.layout.activity_place_ciocanul);

        // 4. Insets-urile, pe containerul `R.id.main` din acest layout (un RelativeLayout).
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {

            // 4a. Barele de sistem.
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // 4b. Padding egal cu barele.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // 4c. Se întoarce obiectul primit.
            return insets;
        });

        // 5. Butonul, după ID-ul din `activity_place_ciocanul.xml`.
        btn2 = findViewById(R.id.floatingActionButton2);

        // 6. Listener-ul butonului: un Toast. Tot comportamentul ecranului.
        btn2.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {

                // `PlaceCiocanul.this` = Context-ul (în clasa anonimă, `this` ar fi
                //   listener-ul). `Toast.LENGTH_LONG` = ~3,5 secunde.
                // RISC: textul este hardcodat în cod, nu în `strings.xml`. Lint dă
                //   avertismentul „HardcodedText", iar textul nu poate fi tradus.
                //   Înainte de orice predare, el trebuie înlocuit cu un mesaj real.
                Toast.makeText(PlaceCiocanul.this, "Caca", Toast.LENGTH_LONG).show();
            }
        });

        // 7. ULTIMA LINIE A METODEI — și cea mai instructivă.
        // ==================================================================================
        // RISC: `String.valueOf(R.string.app_name)` NU întoarce numele aplicației.
        // ==================================================================================
        // `R.string.app_name` este un `int`: ID-ul numeric al resursei, generat în `R.java`.
        // `String.valueOf` are mai multe suprascrieri; cu un `int` o alege pe cea care
        //   transformă numărul în cifre. Rezultatul este un text de forma „2131689472",
        //   nu „Group1098".
        //
        //   GRESIT:  String.valueOf(R.string.app_name)      -> "2131689472"
        //   CORECT:  getString(R.string.app_name)           -> "Group1098"
        //   CORECT:  String.valueOf(getString(R.string.app_name))
        //
        // DE CE NU SE VEDE: valoarea nu este afișată nicăieri. Câmpul `string` este
        //   mort, deci bug-ul nu are efect vizibil — deocamdată. Prima încercare de
        //   a-l pune într-un `TextView` ar afișa un număr.
        // DE REȚINUT: `R.<tip>.<nume>` este MEREU un `int`. Textul se obține doar prin
        //   `getString(...)` / `getText(...)` / `getDrawable(...)`, adică prin `Resources`.
        string = String.valueOf(R.string.app_name);
    }
}
```

**Fluxul acestui ecran, cap-coadă:**

```
MainActivity                         PlaceCiocanul                     sistem
------------                         -------------                     ------
btnVlad.onClick
  |
  |-- Intent(MainActivity.this, PlaceCiocanul.class)
  +-- launcher.launch(intent)
            |
            v
                                     onCreate
                                       |-- WindowCompat.enableEdgeToEdge
                                       |-- setContentView(activity_place_ciocanul)
                                       |-- insets pe R.id.main
                                       |-- btn2 = findViewById(...)
                                       |-- btn2.setOnClickListener
                                       +-- string = String.valueOf(R.string.app_name)  <- RISC
            |
            v
                                     apasă FAB -> Toast "Caca" (3,5 s)
            |
            v
                                     buton Back
                                       |
                                       +-- fără setResult -> RESULT_CANCELED
            |
            v
MainActivity.onActivityResult(o)
  +-- o.getResultCode() == RESULT_OK ? NU -> nu se întâmplă nimic
```

**De ce ecranul nu strică nimic, deși are un bug.** `MainActivity` filtrează pe `RESULT_OK`. `PlaceCiocanul` nu apelează niciodată `setResult`, deci la întoarcere codul este `RESULT_CANCELED` și callback-ul nu atinge nici lista, nici adaptorul. Un ecran de test care nu trimite rezultat este inofensiv prin construcție — dar numai atât timp cât rămâne de test.

---

## 38.5 `movie_item.xml` — cardul, în sfârșit folosit

În capitolul 22 fișierul acesta exista și era complet, dar **nu-l inflata nimeni**: `MainActivity` folosea `android.R.layout.simple_list_item_1`, adică un singur `TextView` cu `toString()`-ul filmului. Acum este layout-ul fiecărui rând: `MovieAdapter.onCreateViewHolder` îl umflă, iar `MovieViewHolder` îi caută ID-urile.

Diferența se vede imediat pe ecran: în loc de o linie de text de 300 de caractere, fiecare film are un card cu poster, titlu, subtitlu, stele și etichete.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FIȘIER: movie_item.xml — CARDUL UNUI SINGUR FILM                                       -->
<!-- ====================================================================================== -->
<!-- CE ESTE: layout-ul unui rând de listă. Se umflă o dată pentru fiecare rând vizibil   -->
<!--   și se re-leagă cu date la fiecare reapariție (reciclare — vezi 38.2).               -->
<!-- DE CE EXISTĂ: RecyclerView are nevoie de un XML pe care să îl repete. Acesta este el. -->
<!-- DE CE DEPINDE: de tema Material (MaterialCardView, stilurile Chip.Suggestion) și de  -->
<!--   resursa @string/chip_ciocan_name. Nu depinde de nicio clasă Java.                   -->
<!-- CINE DEPINDE DE EL: MovieAdapter — prin R.layout.movie_item și nouă ID-uri de aici.   -->
<!-- CE NU FACE: nu afișează date reale prin el însuși. Valorile android:text de mai jos  -->
<!--   sunt PLACEHOLDER-E care se văd la runtime dacă adaptorul nu le suprascrie.          -->
<!-- CE S-AR RUPE FĂRĂ EL: inflate(R.layout.movie_item, ...) nu ar compila; lista ar      -->
<!--   rămâne fără rânduri, deși adaptorul ar avea ce afișa.                                -->
<!-- ====================================================================================== -->
<!-- STRUCTURA ARBORELUI (11 ID-uri declarate, 9 folosite de cod):                         -->
<!--   MaterialCardView                          rădăcina = itemView (cardul întreg)       -->
<!--     +- LinearLayout orizontal, padding 12dp                                           -->
<!--         +- ImageView    moviePoster         96 x 140dp                                -->
<!--         +- LinearLayout vertical, 0dp + weight 1                                      -->
<!--             +- TextView   movieTitle        20sp, bold, maxim 2 rânduri               -->
<!--             +- TextView   movieSubtitle     14sp, gri                                 -->
<!--             +- LinearLayout orizontal                                                 -->
<!--             |    +- RatingBar  movieRating      5 stele, indicator                    -->
<!--             |    +- TextView   movieRatingValue „4.5"                                 -->
<!--             +- TextView   movieFacts        „142 min · $160M"                         -->
<!--             +- ChipGroup  movieStatusGroup                                            -->
<!--                 +- Chip   chipApproval      „Approved"                                -->
<!--                 +- Chip   chipWatched       „Watched" + iconiță                       -->
<!--                 +- Chip   chipWatchlist     „Watchlist"                               -->
<!--                 +- Chip   chipCiocan        @string/chip_ciocan_name                  -->
<!-- ====================================================================================== -->
<!-- MATERIALCARDVIEW — rădăcina rândului.                                                 -->
<!-- DE CE CARD și nu LinearLayout: fiecare rând este o unitate vizuală independentă, cu   -->
<!--   colțuri și umbră proprii. Un LinearLayout simplu ar arăta ca un tabel.              -->
<!-- layout_width="match_parent" — rândul ocupă toată lățimea listei.                      -->
<!-- layout_height="wrap_content" — înălțimea o dă conținutul (posterul de 140dp).         -->
<!-- layout_marginHorizontal="12dp" / layout_marginVertical="6dp" — aer în jurul cardului. -->
<!-- RISC: marginHorizontal și marginVertical au fost introduse în API 26. Cu minSdk 24    -->
<!--   (din build.gradle.kts), pe Android 7.0–7.1 sunt ignorate: cardul atinge marginile.  -->
<!-- cardCornerRadius="16dp" — colțuri rotunjite; cardElevation="3dp" — umbră.             -->
<!-- cardUseCompatPadding="true" — padding intern ca umbra să nu fie tăiată pe API vechi.  -->
<!-- OBSERVAȚIE: rădăcina NU are android:id. Nu are nevoie: itemView din ViewHolder este   -->
<!--   chiar acest card, iar adaptorul nu îl caută cu findViewById.                        -->
<!-- ====================================================================================== -->
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

    <!-- LINEARLAYOUT ORIZONTAL — poster în stânga, informații în dreapta. -->
    <!-- padding="12dp" — conținutul nu atinge marginea cardului. -->
    <!-- DE CE orizontal: posterul și coloana de text stau alăturate, ca într-un afiș. -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="12dp">

        <!-- Poster -->
        <!-- IMAGEVIEW — posterul filmului. -->
        <!-- 96 x 140dp — raport ~2:3, ca un afiș. Dimensiuni FIXE: posterul nu își -->
        <!--   schimbă mărimea după textul din dreapta. -->
        <!-- background="#11000000" — negru cu alfa 0x11 (~7% opacitate). Formatul este -->
        <!--   #AARRGGBB: alfa primul, apoi roșu, verde, albastru. -->
        <!-- scaleType="centerCrop" — umple cele 96x140dp decupând marginile, fără să -->
        <!--   deformeze. fitXY ar întinde imaginea; centerInside ar lăsa benzi goale. -->
        <!-- contentDescription="Movie poster" — textul citit de TalkBack. -->
        <!-- src="@android:drawable/ic_menu_gallery" — imagine provizorie, din resursele -->
        <!--   de sistem, nu din proiect. -->
        <!-- RISC: adaptorul caută acest view în holder (câmpul `poster`) dar NU îl umple -->
        <!--   niciodată. Pe ecran apare mereu iconița de galerie, pentru orice film. -->
        <ImageView
            android:id="@+id/moviePoster"
            android:layout_width="96dp"
            android:layout_height="140dp"
            android:background="#11000000"
            android:scaleType="centerCrop"
            android:contentDescription="Movie poster"
            android:src="@android:drawable/ic_menu_gallery" />

        <!-- Info column -->
        <!-- COLOANA DE INFORMAȚII — 0dp + weight 1. -->
        <!-- DE CE 0dp: lățimea nu este fixată; o ia pe tot restul rămas după poster. -->
        <!-- DE CE weight="1": singurul copil cu weight primește tot spațiul liber. Fără -->
        <!--   el, 0dp ar însemna lățime zero și textul ar dispărea. -->
        <!-- marginStart="12dp" — separă textul de poster; `start` respectă RTL. -->
        <!-- orientation="vertical" — elementele curg de sus în jos. -->
        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:layout_marginStart="12dp"
            android:orientation="vertical">

            <!-- TITLUL — movieTitle. -->
            <!-- textSize="20sp" + textStyle="bold" — ierarhie puternică; titlul este -->
            <!--   elementul principal al rândului. -->
            <!-- maxLines="2" — maximum două rânduri. -->
            <!-- ellipsize="end" — dacă nu încape, se taie cu „..." la final. Fără el, -->
            <!--   textul ar fi tăiat brutal la margine. -->
            <!-- android:text="Movie title" — PLACEHOLDER. Aici adaptorul scrie -->
            <!--   movie.getTitle(), deci valoarea din XML nu se vede la runtime. -->
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
            <!-- SUBTITLUL — movieSubtitle. -->
            <!-- textSize="14sp" — secundar față de titlu; marginTop="2dp" — lipit de el. -->
            <!-- textColor="#757575" — gri hardcodat. Corect ar fi ?attr/colorOnSurfaceVariant, -->
            <!--   ca să se adapteze la dark mode. Aici este o culoare fixă. -->
            <!-- PLACEHOLDER: adaptorul scrie „gen. an" — cu punct, nu cu „·" ca în XML. -->
            <TextView
                android:id="@+id/movieSubtitle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Genre · Year"
                android:textSize="14sp"
                android:textColor="#757575" />

            <!-- Rating -->
            <!-- RÂNDUL DE RATING — orizontal, centrat pe verticală. -->
            <!-- gravity="center_vertical" — stelele și cifra se aliniază pe mijlocul -->
            <!--   înălțimii, nu pe sus. -->
            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <!-- RATINGBAR — stelele. -->
                <!-- style="?android:attr/ratingBarStyleSmall" — varianta mică, cu stele -->
                <!--   de ~14dp; stil de sistem, nu Material. -->
                <!-- numStars="5" — cinci stele; stepSize="0.5" — jumătăți de stea. -->
                <!-- isIndicator="true" — doar afișează, nu se poate modifica prin -->
                <!--   atingere. Fără el, utilizatorul ar schimba nota fiecărui rând. -->
                <!-- RISC: nu există android:rating și adaptorul nu setează nimic, deci -->
                <!--   TOATE rândurile arată zero stele, oricât ar fi nota din model. -->
                <RatingBar
                    android:id="@+id/movieRating"
                    style="?android:attr/ratingBarStyleSmall"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:numStars="5"
                    android:stepSize="0.5"
                    android:isIndicator="true" />

                <!-- VALOAREA NUMERICĂ — movieRatingValue, cifra din dreapta stelelor. -->
                <!-- textSize="13sp", gri; marginStart="6dp" — separă de stele. -->
                <!-- BUG: valoarea este statică „4.5" din XML și nu este scrisă de -->
                <!--   adaptor. Toate rândurile arată 4.5, indiferent de film. -->
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
            <!-- „FACTS" — durata și bugetul, pe un singur rând de text. -->
            <!-- Exemplul din XML: „142 min  ·  $160M" (două spații înainte de separator). -->
            <!-- textSize="13sp", gri deschis (#9E9E9E) — informația cea mai secundară. -->
            <!-- BUG: și acest text este static. Adaptorul nu îl scrie, deci toate cele -->
            <!--   trei filme afișează aceeași durată și același buget. -->
            <TextView
                android:id="@+id/movieFacts"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="142 min  ·  $160M"
                android:textSize="13sp"
                android:textColor="#9E9E9E" />

            <!-- Status chips: approval, watched, watchlist -->
            <!-- CHIPGROUP — containerul etichetelor. -->
            <!-- match_parent — are toată lățimea coloanei; marginTop="8dp" — separă de -->
            <!--   textul de deasupra. -->
            <!-- chipSpacingHorizontal="6dp" — 6dp între etichete. -->
            <!-- singleLine="false" — dacă nu încap pe un rând, trec pe rândul următor. -->
            <!-- OBSERVAȚIE: grupul are ID (movieStatusGroup) dar adaptorul NU îl caută. -->
            <com.google.android.material.chip.ChipGroup
                android:id="@+id/movieStatusGroup"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                app:chipSpacingHorizontal="6dp"
                app:singleLine="false">

                <!-- CHIP 1 — ghidajul parental („Approved"). -->
                <!-- style="@style/Widget.Material3.Chip.Suggestion" — stilul Material 3 -->
                <!--   pentru etichete de sugestie: fundal discret, fără contur. -->
                <!-- android:text="Approved" — text static. Aici ar trebui să apară -->
                <!--   movie.getApproval(): „PG-13", „R", „G". -->
                <!-- android:clickable="false" — eticheta nu se apasă. DE CE CONTEAZĂ: -->
                <!--   fără el, Chip-ul ar consuma atingerea, iar click-ul pe rând (legat -->
                <!--   pe itemView) nu s-ar mai declanșa când apeși exact pe etichetă. -->
                <!-- chipMinHeight="28dp" — mai scurtă decât standardul (32dp implicit). -->
                <!-- ensureMinTouchTargetSize="false" — acceptă zonă de atingere sub 48dp. -->
                <!--   Aici este în regulă: eticheta nu se apasă oricum. -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipApproval"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Approved"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />

                <!-- CHIP 2 — „Watched". -->
                <!-- Singura diferență față de primul: app:chipIcon, o bifă din resursele -->
                <!--   de sistem (@android:drawable/checkbox_on_background). -->
                <!-- Text static: ar trebui să depindă de movie.isWatched(). -->
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

                <!-- CHIP 3 — „Watchlist". -->
                <!-- Text static: ar trebui să depindă de movie.isOnWatchlist(). -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipWatchlist"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Watchlist"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false" />

                <!-- CHIP 4 — chipCiocan. -->
                <!-- Textul vine din @string/chip_ciocan_name — o resursă de text, nu un -->
                <!--   literal. Este singurul chip fără text scris direct în layout. -->
                <!-- OBSERVAȚIE: ID-ul nu apare în MovieViewHolder, deci acest chip nu este -->
                <!--   niciodată modificat din cod. Este o a patra etichetă decorativă. -->
                <!-- ATENȚIE la spațiere: „false"/> — fără spațiu înainte de />. Este -->
                <!--   singurul chip scris așa; fișierul este exact cum a fost salvat. -->
                <com.google.android.material.chip.Chip
                    android:id="@+id/chipCiocan"
                    style="@style/Widget.Material3.Chip.Suggestion"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="@string/chip_ciocan_name"
                    android:clickable="false"
                    app:chipMinHeight="28dp"
                    app:ensureMinTouchTargetSize="false"/>
            </com.google.android.material.chip.ChipGroup>
        </LinearLayout>
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

**Ce se vede pe ecran și de ce.** Rezultatul fidel al acestui layout, cu adaptorul din 38.2, este următorul — merită citit ca o diagnoză, nu ca o schiță:

| Element | Valoarea afișată | Vine din |
|---|---|---|
| titlu | „Inception" / „Toy Story" / „The Matrix" | **model** (`getTitle()`) |
| subtitlu | „Sci-Fi. 2010", „Animation. 1995", „Action. 1999" | **model** (`getGenre()`, `getRelease()`) |
| stele | 0 stele, pentru toate | XML (lipsește `android:rating`) |
| valoare rating | „4.5", pentru toate | XML (placeholder) |
| facts | „142 min · $160M", pentru toate | XML (placeholder) |
| chip 1 | „Approved", pentru toate | XML |
| chip 2 | „Watched", pentru toate | XML |
| chip 3 | „Watchlist", pentru toate | XML |
| chip 4 | textul din `@string/chip_ciocan_name` | XML (resursă) |
| poster | iconița galeriei, pentru toate | XML (`@android:drawable/...`) |

Două elemente sunt corecte, nouă sunt identice pe fiecare card. Este exact genul de defect pe care îl descoperi citind `onBindViewHolder` **și** layoutul împreună — niciunul singur nu îl arată.

---

## 38.6 `activity_main.xml` — RecyclerView și al doilea FAB

Față de versiunea veche, două schimbări: `ListView` a devenit `RecyclerView`, iar FAB-ul singur a devenit doi. Restul scheletului — `FrameLayout` cu `id=main` pentru insets — este identic.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FIȘIER: activity_main.xml — ECRANUL CU LISTA                                           -->
<!-- ====================================================================================== -->
<!-- CE ESTE: un FrameLayout cu trei copii: RecyclerView (umple tot), FAB-ul de inserare   -->
<!--   (jos-dreapta) și FAB-ul spre ecranul de test (jos-stânga).                          -->
<!-- DE CE EXISTĂ: este singurul layout care conține lista. Complexitatea unui rând este   -->
<!--   în movie_item.xml; aici este doar scheletul.                                         -->
<!-- CINE DEPINDE DE EL: MainActivity — prin R.layout.activity_main și trei ID-uri:         -->
<!--   main, rvMovies, floatingActionButton.                                                -->
<!-- CE NU FACE: nu definește cum arată un rând (acesta vine din movie_item.xml) și nu     -->
<!--   stabilește ordinea (o face LinearLayoutManager).                                     -->
<!-- CE S-AR RUPE FĂRĂ EL: setContentView nu ar avea ce încărca; findViewById(R.id.main)   -->
<!--   ar întoarce null și listener-ul de insets ar arunca NullPointerException.            -->
<!-- ====================================================================================== -->
<!-- FRAMELAYOUT — containerul rădăcină. -->
<!-- DE CE FrameLayout și nu LinearLayout: copiii trebuie să se SUPRApună. Butoanele       -->
<!--   plutesc peste listă; un LinearLayout le-ar pune unul lângă altul (sau unul sub       -->
<!--   altul), iar FAB-urile nu ar mai pluti.                                               -->
<!-- DE CE nu ConstraintLayout: pentru trei copii, FrameLayout este suficient și mai       -->
<!--   ieftin de citit.                                                                     -->
<!-- ORDINEA COPIILOR ESTE SEMNIFICAȚIE: fiecare copil este desenat peste cel anterior.     -->
<!--   RecyclerView este PRIMUL, deci stă dedesubt; FAB-urile vin peste el.                -->
<!-- ATRIBUTE: xmlns:android = framework; xmlns:app = biblioteci (Material); xmlns:tools   -->
<!--   = doar preview, eliminate la build.                                                  -->
<!-- android:id="@+id/main" — containerul pe care se aplică padding-ul de insets.           -->
<!--   @+id/ CREEAZĂ ID-ul; @id/ l-ar REFERI pe unul existent.                              -->
<!-- android:orientation="horizontal" — ATRIBUT INVALID pe FrameLayout: `orientation`      -->
<!--   există doar pe LinearLayout. Este IGNORAT de Android și produce un warning de lint   -->
<!--   („Unknown attribute"). Zgomot inofensiv, rămas de la un LinearLayout anterior. Nu    -->
<!--   schimbă nimic la runtime și nu merită „reparat" decât dacă ți se cere explicit.      -->
<!-- tools:context — doar pentru preview: ce activitate împrumută tema în editor.           -->
<!-- DE CE android:id="@+id/main" ESTE OBLIGATORIU: codul face findViewById(R.id.main)      -->
<!--   pentru listener-ul de insets. Fără ID, apelul ar întoarce null și                   -->
<!--   setOnApplyWindowInsetsListener(null, ...) ar arunca NullPointerException.            -->
<!-- ====================================================================================== -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">

    <!-- RECYCLERVIEW — lista. -->
    <!-- Numele complet al clasei este obligatoriu: RecyclerView nu face parte din -->
    <!--   widget-urile framework-ului, ci din biblioteca AndroidX. În XML se scrie -->
    <!--   calea completă a clasei. -->
    <!-- android:id="@+id/rvMovies" — căutat în initControls, unde primește -->
    <!--   LayoutManager și adaptor. -->
    <!-- layout_width/height = match_parent — lista umple ecranul, inclusiv zona de sub -->
    <!--   butoane. Butoanele sunt desenate PESTE ea, nu lângă ea. -->
    <!-- CE NU ARE, SPRE DEOSEBIRE DE LISTVIEW: -->
    <!--   - nu are android:entries: RecyclerView nu știe să își construiască singur -->
    <!--     rândurile din resurse; are nevoie de un adaptor; -->
    <!--   - nu are tools:listitem: atributul de preview care ar arăta în editor cum arată -->
    <!--     un rând. Fără el, preview-ul apare gol. Nu afectează runtime-ul. -->
    <!-- RISC: pentru că lista se întinde pe tot ecranul, iar butoanele sunt desenate peste -->
    <!--   ea, ultimul rând poate sta sub FAB-uri. Remediul corect este paddingBottom pe -->
    <!--   listă + clipToPadding="false". -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvMovies"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

    <!-- FAB 1 — inserarea. -->
    <!-- layout_gravity="bottom|end" — jos, dreapta. `end` respectă direcția de citire; -->
    <!--   în RTL devine stânga. `right` ar fi fix și greșit în RTL. -->
    <!-- layout_margin="16dp" — 16dp față de zona sigură (padding-ul de insets se aplică -->
    <!--   pe R.id.main, nu pe FAB). -->
    <!-- contentDescription="Add" — textul citit de TalkBack. Obligatoriu pentru un buton -->
    <!--   fără text vizibil; fără el, lint-ul dă eroare „ContentDescription". -->
    <!-- app:srcCompat — varianta compatibilă pentru imagini vectoriale; suportă vectori -->
    <!--   pe toate versiunile, spre deosebire de android:src. -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_24" />

    <!-- FAB 2 — btnVlad, butonul către ecranul de test. -->
    <!-- Este NOU față de versiunea veche. Stă în partea opusă față de primul: -->
    <!--   bottom|start — jos, stânga. -->
    <!-- android:clickable="true" — redundant: FloatingActionButton este clickable din -->
    <!--   construcție. Pe primul FAB nu apare; aici a fost adăugat explicit. -->
    <!-- contentDescription="Ciocan" — din nou, pentru TalkBack. -->
    <!-- app:srcCompat="@drawable/buton_ciocan" — iconiță proprie proiectului. -->
    <!-- DE CE există: deschide PlaceCiocanul, ecranul de test (38.4). Legarea se face -->
    <!--   în initSecondListener, prin același launcher. -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/btnVlad"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:clickable="true"
        android:layout_margin="16dp"
        android:contentDescription="Ciocan"
        android:layout_gravity="bottom|start"
        app:srcCompat="@drawable/buton_ciocan"/>
</FrameLayout>
```

**Ordinea de desenare în `FrameLayout`:**

```
        +--------------------------------------+
        |  RecyclerView  (primul copil)        |   <- desenat PRIMUL, dedesubt
        |  [card Inception]                    |
        |  [card Toy Story]                    |
        |  [card The Matrix]                   |
        |                                      |
        |  (FAB)                       (FAB)   |   <- desenate PESTE lista
        +---[btnVlad]--------[+]--------------+
             bottom|start   bottom|end

  Copil 1 = RecyclerView   -> fundalul
  Copil 2 = FAB „+"        -> peste lista
  Copil 3 = FAB „ciocan"   -> peste listă, în stânga
```

**Tabel de referință pentru cele două FAB-uri:**

| | `floatingActionButton` | `btnVlad` |
|---|---|---|
| poziție | `bottom\|end` (dreapta) | `bottom\|start` (stânga) |
| iconiță | `@drawable/outline_add_24` | `@drawable/buton_ciocan` |
| `contentDescription` | „Add" | „Ciocan" |
| `clickable` | implicit | `"true"` explicit (redundant) |
| deschide | `ItemActivity` (inserare) | `PlaceCiocanul` |
| listener | `initListeners()` | `initSecondListener()` |
| launcher | același | același |

---

## 38.7 `activity_place_ciocanul.xml` — layout-ul ecranului nou

Acesta este un **schelet**, nu un ecran funcțional: `PlaceCiocanul.java` folosește doar două dintre cele patru view-uri, iar `RecyclerView`-ul de aici nu are nici măcar ID. Merită citit pentru cele trei semnale pe care le dă un layout neterminat.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FIȘIER: activity_place_ciocanul.xml — ECRANUL DE TEST                                  -->
<!-- ====================================================================================== -->
<!-- CE ESTE: layout-ul ecranului PlaceCiocanul. Conține un RecyclerView fără ID, un FAB,   -->
<!--   un ProgressBar îngust și nimic altceva.                                              -->
<!-- DE CE EXISTĂ: este scheletul ecranului nou adus în versiunea 2. Din el se folosesc     -->
<!--   două view-uri: containerul main (pentru insets) și FAB-ul (pentru Toast).            -->
<!-- CINE DEPINDE DE EL: PlaceCiocanul.java — prin R.layout.activity_place_ciocanul,        -->
<!--   R.id.main și R.id.floatingActionButton2.                                             -->
<!-- CE NU FACE: nu afișează nicio listă (RecyclerView-ul nu are ID, deci nu poate fi        -->
<!--   configurat din cod) și nu afișează niciun progres (ProgressBar-ul nu e legat de      -->
<!--   nimic).                                                                              -->
<!-- CE S-AR RUPE FĂRĂ EL: setContentView(R.layout.activity_place_ciocanul) nu ar compila.  -->
<!-- ====================================================================================== -->
<!-- RELATIVELAYOUT — containerul rădăcină. -->
<!-- DE CE RelativeLayout: poziționarea copiilor se face prin reguli relative („deasupra    -->
<!--   lui X", „în dreapta părintelui"). Aici însă NU este folosită nicio regulă, deci      -->
<!--   este un container fără rost — un FrameLayout ar fi echivalent.                       -->
<!-- android:id="@+id/main" — folosit de findViewById(R.id.main) pentru insets.             -->
<!-- android:orientation="vertical" — ATRIBUT INVALID pe RelativeLayout: există doar pe     -->
<!--   LinearLayout. Ignorat la runtime; zgomot, exact ca în activity_main.xml.             -->
<!-- tools:context — doar pentru preview.                                                   -->
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".activities.PlaceCiocanul"
    android:orientation="vertical">

    <!-- RECYCLERVIEW FĂRĂ ID — schelet. -->
    <!-- wrap_content / wrap_content — dacă ar avea conținut, s-ar dimensiona după el; -->
    <!--   așa, cu zero rânduri, are 0x0. -->
    <!-- PROBLEMA 1: nu are android:id. Fără ID nu poate fi găsit cu findViewById, deci -->
    <!--   niciun cod nu îi poate da un LayoutManager sau un adaptor. -->
    <!-- PROBLEMA 2: fără LayoutManager, un RecyclerView nu desenează nimic și scrie în -->
    <!--   Logcat „No layout manager attached; skipping layout". -->
    <!-- Concluzie: este un rezervor de spațiu pentru un ecran viitor, nu o listă. -->
    <androidx.recyclerview.widget.RecyclerView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />

    <!-- FAB — singurul view funcțional. -->
    <!-- android:id="@+id/floatingActionButton2" — căutat în onCreate ca btn2. -->
    <!-- android:clickable="true" — redundant, ca la btnVlad din ecranul principal. -->
    <!-- app:srcCompat="@drawable/outline_add_24" — aceeași iconiță ca FAB-ul de -->
    <!--   inserare. Aici nu adaugă nimic; este moștenită. -->
    <!-- tools:layout_editor_absoluteX / absoluteY — atribute DOAR de editor: canalele -->
    <!--   folosite de layout editor ca să așeze view-ul pe plansă. NU există la runtime -->
    <!--   și se elimină la build. -->
    <!-- RISC: pentru că nu există layout_alignParent* / layout_center* și nici -->
    <!--   layout_gravity, copilul este așezat implicit în colțul stânga-sus (0,0) — nu -->
    <!--   unde arată preview-ul (334dp, 655dp). -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:clickable="true"
        app:srcCompat="@drawable/outline_add_24"
        tools:layout_editor_absoluteX="334dp"
        tools:layout_editor_absoluteY="655dp" />

    <!-- PROGRESSBAR — schelet. -->
    <!-- style="?android:attr/progressBarStyle" — stilul implicit de sistem: cerc animat, -->
    <!--   nedeterminat. -->
    <!-- layout_width="6dp" — lățimea este 6dp, în timp ce înălțimea este wrap_content. -->
    <!--   Rezultatul: un cerc strivit, aproape invizibil. Corect ar fi wrap_content pe -->
    <!--   ambele axe. -->
    <!-- Nu este legat de niciun cod: nu are ID și nu este pornit/oprit de nicăieri. -->
    <ProgressBar
        style="?android:attr/progressBarStyle"
        android:layout_width="6dp"
        android:layout_height="wrap_content" />

</RelativeLayout>
```

**Cele trei semnale ale unui layout neterminat:**

| Semnal | Aici | Ce înseamnă |
|---|---|---|
| view fără ID | `RecyclerView`-ul | codul nu îl poate configura niciodată |
| dimensiune degenerată | `ProgressBar` 6dp lățime | vizual nu se vede; nu are sens funcțional |
| atribut de alt container | `android:orientation` pe `RelativeLayout` | rămășiță de la un `LinearLayout` anterior |

**De ce nu este o greșeală de compilare.** Toate cele trei sunt perfect legale pentru `aapt2`: XML-ul este valid, resursele se generează, aplicația pornește, FAB-ul funcționează. Defectele sunt de **intenție**, nu de sintaxă — exact categoria care trece de build și se vede abia când cineva deschide ecranul.

---

## 38.8 `AndroidManifest.xml` — trei activități

Singurul fișier care nu este nici cod, nici layout: este **contractul cu sistemul de operare**. Aici se declară ce componente are aplicația, care este punctul de intrare, ce temă folosește și ce backup are voie să facă.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- ====================================================================================== -->
<!-- FIȘIER: AndroidManifest.xml — CONTRACTUL CU SISTEMUL                                   -->
<!-- ====================================================================================== -->
<!-- CE ESTE: declarația de componente a aplicației: trei activități, tema, iconițele,      -->
<!--   regulile de backup. Nu conține cod executabil.                                       -->
<!-- DE CE EXISTĂ: Android nu „descoperă" clasele. O activitate care nu este declarată      -->
<!--   aici pur și simplu nu poate fi pornită — nici de launcher, nici cu Intent.           -->
<!-- CE NU FACE: nu conține `package`. Începând cu AGP 8, identitatea aplicației vine din   -->
<!--   namespace + applicationId din build.gradle.kts. Numele relative de aici              -->
<!--   (.activities.MainActivity) se rezolvă față de acel namespace.                        -->
<!-- CE S-AR RUPE FĂRĂ EL: aplicația nu s-ar instala. Iar fără exported="true" pe           -->
<!--   activitatea din LAUNCHER, iconița ar exista, dar nu ar porni nimic.                  -->
<!-- ====================================================================================== -->
<!-- RADĂCINA. xmlns:tools este necesar pentru atributele tools: (aici nu apare niciunul,   -->
<!--   dar namespace-ul este păstrat din șablonul generat de Android Studio).               -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- APLICAȚIA — atributele globale. -->
    <!--   allowBackup="true"                      sistemul poate salva datele aplicației -->
    <!--   dataExtractionRules="@xml/data_extraction_rules"   reguli pentru Android 12+ -->
    <!--   fullBackupContent="@xml/backup_rules"   reguli pentru Android 11 și mai vechi -->
    <!--   icon / roundIcon                        iconițele din mipmap -->
    <!--   label="@string/app_name"                numele afișat sub iconiță -->
    <!--   supportsRtl="true"                      acceptă layout oglindit pentru RTL -->
    <!--   theme="@style/Theme.Group1098"          tema globală, moștenită de activitățile -->
    <!--     care nu își pun alta -->
    <!-- OBSERVAȚIE: nu există nicio permisiune declarată. Aplicația nu folosește rețeaua, -->
    <!--   camera sau stocarea — deci nu are nevoie de <uses-permission>. -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.Group1098">

        <!-- ACTIVITATEA 1 — MainActivity, PUNCTUL DE INTRARE. -->
        <!-- android:name=".activities.MainActivity" — punctul de la început este o -->
        <!--   prescurtare: clasa completă devine com.example.group1098.activities. -->
        <!--   MainActivity, unde prefixul vine din namespace.                     -->
        <!-- android:exported="true" — OBLIGATORIU aici. Din Android 12 (API 31), orice -->
        <!--   componentă cu intent-filter trebuie să declare explicit exported; altfel -->
        <!--   aplicația NU SE INSTALEAZĂ. `true` = poate fi pornită din afara -->
        <!--   aplicației, exact ce face launcher-ul.                              -->
        <!-- android:windowSoftInputMode="adjustResize" — când apare tastatura, fereastra -->
        <!--   se micșorează în loc să fie acoperită. Aici nu există câmpuri de text, -->
        <!--   dar atributul este păstrat uniform.                                -->
        <!-- INTENT-FILTER — rețeta prin care sistemul recunoaște ecranul de start: -->
        <!--   action MAIN = „pornește aplicația"; category LAUNCHER = „arată-o în -->
        <!--   launcher". Fără acest bloc, aplicația s-ar instala și nu ar putea fi -->
        <!--   pornită din iconiță.                                               -->
        <activity
            android:name=".activities.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ACTIVITATEA 2 — ItemActivity, formularul. -->
        <!-- exported="false" — poate fi pornită DOAR din interiorul aplicației. Este -->
        <!--   corect: nimeni din afară nu are ce căuta într-un formular care primește -->
        <!--   un Movie. Contrar aparenței, `false` nu împiedică Intent-ul explicit din -->
        <!--   MainActivity: acela funcționează pentru că vine din același pachet. -->
        <!-- windowSoftInputMode="adjustResize" — AICI contează: formularul are patru -->
        <!--   EditText-uri, un spinner, un SeekBar, un RatingBar, un RadioGroup, două -->
        <!--   bife și un switch. Fără atribut, tastatura ar acoperi câmpurile de jos. -->
        <!-- Nedeclarată, launcher.launch(intent) ar arunca ActivityNotFoundException la -->
        <!--   runtime — fără nicio eroare la compilare. -->
        <activity
            android:name=".activities.ItemActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />

        <!-- ACTIVITATEA 3 — PlaceCiocanul, ecranul de test. -->
        <!-- Este ADAUGAREA versiunii 2. Fără această intrare, FAB-ul btnVlad ar arunca -->
        <!--   ActivityNotFoundException la primul click. -->
        <!-- exported="false" — la fel ca ItemActivity: se pornește doar din aplicație. -->
        <!-- windowSoftInputMode="adjustResize" — uniform, deși ecranul nu are câmpuri. -->
        <activity
            android:name=".activities.PlaceCiocanul"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**Cele trei activități, într-o singură privire:**

```
AndroidManifest.xml
 |
 |-- MainActivity      exported = true    LAUNCHER (MAIN)     <- intrare din iconiță
 |-- ItemActivity      exported = false   fără intent-filter  <- doar Intent intern
 +-- PlaceCiocanul     exported = false   fără intent-filter  <- doar Intent intern

  Cine poate porni ce:
     launcher-ul sistemului  ->  MainActivity  (singura exportată)
     MainActivity            ->  ItemActivity  (Intent explicit, același pachet)
     MainActivity            ->  PlaceCiocanul (Intent explicit, același pachet)
     orice altă aplicație    ->  NIMIC
```

**Trei lucruri care nu se văd în fișier și se întreabă la examen:**

1. **De ce nu există `package="..."`?** Pentru că AGP 8 a mutat identitatea aplicației în `build.gradle.kts`: `namespace` dă numele clasei `R`, iar `applicationId` dă identificatorul din sistem. Manifestul folosește nume relative, care se rezolvă față de `namespace`.
2. **De ce `exported` este obligatoriu?** Din API 31, o componentă cu `intent-filter` fără `exported` explicit blochează instalarea. Este una dintre puținele erori care se văd la instalare, nu la compilare.
3. **De ce `adjustResize` pe toate trei?** Pentru uniformitate. Contează real doar la `ItemActivity`, singurul cu câmpuri de text; dar un atribut consecvent este mai ușor de citit decât unul pus „unde trebuie".

---

## 38.9 Ce să reții din fiecare fișier

| Fișier | Esența | Capcana |
|---|---|---|
| `MainActivity.java` | ordinea din `onCreate`; `RecyclerView` + `LayoutManager` + `setAdapter`; callback-ul de rezultat; `notifyDataSetChanged` după `add`/`set` | `launcher` este atribuit după listeneri; `getData()` nu este verificat pentru `null` |
| `MovieAdapter.java` | contractul cu trei metode; `ViewHolder` ca cache de `findViewById`; click pe `itemView` cu `NO_POSITION` | doar 2 din 9 view-uri sunt umplute — cardul afișează date statice |
| `IMovieListener.java` | contractul de click; adaptorul nu cunoaște activitatea | dacă schimbi semnătura, pică în două locuri (adaptor + activitate) |
| `PlaceCiocanul.java` | al treilea ecran; `WindowCompat.enableEdgeToEdge`; `Toast` | `String.valueOf(R.string.app_name)` întoarce ID-ul numeric, nu textul |
| `movie_item.xml` | cardul rândului; 11 ID-uri, 9 folosite; chips neclickabile ca să treacă click-ul la card | placeholder-ele din XML ajung pe ecran dacă adaptorul nu le scrie |
| `activity_main.xml` | `FrameLayout` cu lista dedesubt și două FAB-uri deasupra | `android:orientation` invalid; ultimul rând poate sta sub FAB-uri |
| `activity_place_ciocanul.xml` | schelet: `RecyclerView` fără ID, `ProgressBar` de 6dp | `tools:layout_editor_absoluteX/Y` nu au efect la runtime |
| `AndroidManifest.xml` | trei activități; doar `MainActivity` exportată, cu LAUNCHER | o activitate nedeclarată = `ActivityNotFoundException` la runtime |

### Cele 10 lucruri pe care le vei fi întrebat

1. **De ce `RecyclerView` și nu `ListView`?** Reciclare automată prin `ViewHolder`, layout manager separat, animații implicite, notificări fine pe poziții.
2. **De ce `setLayoutManager` înainte de `setAdapter`?** Fără layout manager, `RecyclerView` nu știe cum să aranjeze rândurile și nu desenează nimic.
3. **De ce două metode, `onCreateViewHolder` și `onBindViewHolder`?** Inflate-ul este scump și se face o singură dată; legarea datelor este ieftină și se face la fiecare reapariție.
4. **Cum ajunge click-ul la activitate?** Prin `IMovieListener`: adaptorul cheamă interfața, `MainActivity` o implementează. Adaptorul nu știe cine este destinatarul.
5. **De ce `this` în `new MovieAdapter(movies, this)`?** Pentru că `MainActivity` implementează `IMovieListener`; `this` este chiar callback-ul.
6. **De ce `getAbsoluteAdapterPosition()` la click?** Poziția se poate schimba între bind și click; metoda o cere la momentul evenimentului și poate întoarce `NO_POSITION`.
7. **De ce `inflate(..., parent, false)`?** Al treilea argument `false` = nu atașa acum; `RecyclerView` atașează singur. Cu `true`, vederea ar fi adăugată de două ori.
8. **De ce `notifyDataSetChanged()` după fiecare modificare?** Pentru că adaptorul nu observă `ArrayList`-ul; trebuie anunțat. Varianta fină este `notifyItemInserted` / `notifyItemChanged`.
9. **De ce `android:clickable="false"` pe chips?** Ca să nu consume atingerea; altfel click-ul pe rând nu s-ar declanșa când apeși exact pe etichetă.
10. **De ce `String.valueOf(R.string.app_name)` este greșit?** `R.string.*` este un `int` (ID de resursă); `String.valueOf` îl transformă în cifre. Corect este `getString(...)`.

---

## Rezumat capitol 38

- Versiunea 2 schimbă **doar ecranul cu lista** și legăturile ei: widget, adaptor, click, layout de rând, manifest. `Movie.java` și `ItemActivity.java` sunt identice cu versiunea veche în afara liniilor de pachet, iar `activity_item.xml` este identic fără nicio diferență.
- `RecyclerView` cere trei lucruri pe care `ListView` nu le cerea: un **layout manager**, un **adaptor propriu** și, pentru click, un **callback scris de tine**.
- Adaptorul are exact trei metode obligatorii; `ViewHolder` este cache-ul de `findViewById`, iar `onBindViewHolder` este singurul loc unde datele ajung în UI.
- `MainActivity implements IMovieListener` și se pasează pe sine adaptorului: activitatea este destinatarul click-ului.
- Ordinea din `onCreate` nu este cosmetică: `addSampleMovies` -> adaptor -> `initControls` -> listeneri -> `registerForActivityResult`.
- Codul vechi păstrat comentat arată migrarea pe viu: `ListView`, `ArrayAdapter` și `setOnItemClickListener` sunt exact cele trei lucruri pe care `RecyclerView` le scoate.
- Trei defecte reale, toate fără eroare de compilare: cardul afișează date statice pentru șapte din nouă view-uri, `PlaceCiocanul` transformă un ID de resursă în cifre, iar `activity_place_ciocanul.xml` este un schelet cu un `RecyclerView` fără ID.
- Două zgomote inofensive, de semnalat și de lăsat în pace: `android:orientation` pe `FrameLayout` (38.6) și pe `RelativeLayout` (38.7).

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md) **sau la** [prezentarea generală](index.html).
