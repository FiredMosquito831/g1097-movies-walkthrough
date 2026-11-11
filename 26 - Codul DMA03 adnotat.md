# Capitolul 26 — Codul DMA03 adnotat

**Obiectiv:** să citești proiectul `DMA03` linie cu linie — fiecare instrucțiune explicată: ce face, de ce e acolo, ce se strică dacă o scoți. La final trebuie să poți reconstrui din memorie un drawer cu toolbar, un meniu contextual pe rând și un dialog care creează controale.

**Timp estimat:** 90–120 min (citire activă; capitolele adnotate se citesc mai încet decât cele de construcție).

**Sursa:** `DMA03/` la commitul `d719ffc` — 8 fișiere: două activități, manifestul, două layout-uri și trei meniuri.

**Ce înveți din el:** `DrawerLayout`, `NavigationView`, `MaterialToolbar`, `PopupMenu`, `OnBackPressedCallback`, `AlertDialog`, `Snackbar`, view-uri create din cod.

> **Cum citești:** nu citi pasiv. Fiecare fișier e **un singur bloc de cod**, în ordinea din sursă, cu explicațiile țesute în el. Acoperă comentariul, spune ce face linia, apoi verifică. Dacă nu poți, ai găsit ce trebuie repetat.

---

## 26.0 Convențiile de adnotare

Capitolul folosește șase tipuri de marcaje, toate **în interiorul blocului de cod**. Le recunoști după formă, fără să le memorezi.

| Marcaj | Unde apare | Ce conține |
|---|---|---|
| `/* FIȘIER: ... */` | la începutul blocului | rolul fișierului, ce demonstrează, de ce depinde |
| `/* THEORY BLOCK: ... */` | înainte de o secțiune mare | teoria necesară ca să înțelegi codul care urmează |
| `/* METHOD: ... */` | deasupra fiecărei metode | **Theory / Logic / Ref / Risk** — patru rubrici fixe |
| `// 1.`, `// 2.`, `// 3.` | în interiorul metodelor | pașii de execuție, în ordinea în care rulează |
| `// WARNING:` | lângă o linie periculoasă | greșeala care compilează, dar crapă la runtime |
| `// RISK:` | lângă o alegere discutabilă | ce se strică dacă schimbi sau scoți linia |

**De ce patru rubrici la fiecare metodă:**

1. **Theory** — conceptul din spate. Fără el, metoda e o rețetă pe care o uiți după test.
2. **Logic** — pașii concreți, numerotați. Ăsta e răspunsul la „ce face metoda".
3. **Ref** — unde găsești subiectul în materiale. Ca să poți reveni.
4. **Risk** — ce se strică dacă metoda lipsește sau e scrisă altfel. Ăsta e răspunsul la „de ce nu merge".

**Regula de aur a capitolului:** codul propriu-zis e **neatins, caracter cu caracter**. Tot ce e nou e comentariu. Fiecare fișier e un singur bloc continuu, exact ca fișierul sursă: nu vei găsi fragmente separate de proză între linii.

**Densitatea e intenționată.** În fișierul de referință, aproximativ două până la patru linii de comentariu însoțesc fiecare trei până la cinci linii de cod. Capitolul depășește raportul, pentru că toată teoria stă în interiorul blocului: fiecare import, fiecare câmp, fiecare metodă și aproape fiecare linie are explicația ei, scrisă ca `//` sau `/* */` în același bloc.

### Harta fișierelor

| Fișier | Linii | Rol | Secțiunea |
|---|---|---|---|
| `MainActivity.java` | 127 | ecranul principal: drawer, toolbar, două meniuri, Back | 26.1 |
| `SecondActivity.java` | 88 | dialog + Snackbar + butoane create din cod | 26.2 |
| `AndroidManifest.xml` | 29 | declararea celor două activități | 26.3 |
| `activity_main.xml` | 62 | ierarhia de containere a ecranului principal | 26.4 |
| `activity_second.xml` | 17 | un `LinearLayout` cu un buton | 26.5 |
| `drawer_menu.xml` | 28 | conținutul sertarului | 26.6 |
| `list_item_menu.xml` | 12 | meniul contextual de pe rând | 26.6 |
| `top_app_bar.xml` | 22 | meniul barei de sus | 26.6 |

**Observație de ansamblu:** proiectul are 385 de linii de cod (325 fără rândurile goale și comentarii) și aproximativ 2 500 de linii de explicații în capitolul de față. Raportul e intenționat. La examen contează să știi **de ce** fiecare linie e acolo, nu să reproduci sintaxa.

---

## 26.1 `MainActivity.java` — drawer, toolbar, meniuri

Un singur `onCreate`, zece pași. Fișierul nu are metode ajutătoare — totul e inline. E cel mai dens fișier din proiect și, la test, cel mai probabil să-ți ceară o modificare. Blocul de mai jos e fișierul întreg, în ordinea din sursă.

```java
/*
 * ======================================================================================
 * FIȘIER: MainActivity.java
 * ======================================================================================
 * ROL:
 *   Ecranul principal al aplicației DMA03. Un singur `onCreate` care leagă cinci
 *   componente: lista, meniul contextual, sertarul, bara de sus și butonul Back.
 *
 * CE DEMONSTREAZĂ:
 *   1. DrawerLayout + NavigationView   — meniu lateral glisant peste conținut.
 *   2. MaterialToolbar                 — titlu, iconiță hamburger, meniu de acțiuni.
 *   3. PopupMenu                       — meniu contextual ancorat pe un rând.
 *   4. OnBackPressedCallback           — interceptarea butonului Back.
 *
 * DEPINDE DE:
 *   - androidx.activity           → EdgeToEdge, OnBackPressedCallback
 *   - com.google.android.material → MaterialToolbar, NavigationView
 *   - androidx.drawerlayout       → DrawerLayout (adus tranzitiv de `material`)
 *
 * CE NU FACE:
 *   - nu pornește SecondActivity (nu există niciun `startActivity` în tot fișierul);
 *   - nu salvează nimic în `savedInstanceState`;
 *   - nu are adapter scris de mână — lista se hrănește din `@array/items`.
 *
 * REF: cap. 14 — DMA03: navigare, meniuri și dialoguri.
 * ======================================================================================
 */

package ro.ase.ie.dma03;

// ======================================================================================
// IMPORT 1: android.content.Intent — IMPORTAT, DAR NEFOLOSIT
// ======================================================================================
// CE ESTE: descrierea unei acțiuni sau a unui ecran de pornit.
// DE CE E AICI: singurul mod de a deschide SecondActivity ar fi
//   `startActivity(new Intent(this, SecondActivity.class))`.
// DE CE E O PROBLEMĂ: în tot fișierul nu există niciun `new Intent(...)`, niciun
//   `startActivity`. Importul e SINGURA urmă a legăturii care lipsește.
// CUM VERIFICI: Ctrl+F după „Intent" în tot proiectul → un singur rezultat, linia asta.
// ======================================================================================
import android.content.Intent;

// ======================================================================================
// IMPORT 2: android.os.Bundle — starea salvată la recreare
// ======================================================================================
// CE ESTE: un dicționar cheie-valoare pe care sistemul îl păstrează între instanțe.
// DE CE E AICI: semnătura lui `onCreate(Bundle)` o cere.
// DE CE E INUTIL AICI: codul nu citește niciodată `savedInstanceState`. La rotire,
//   totul revine la starea inițială: titlu „Inbox", „Inbox" bifat, lista sus.
// ======================================================================================
import android.os.Bundle;

// ======================================================================================
// IMPORT 3: android.widget.ListView — lista de 20 de rânduri
// ======================================================================================
// CE ESTE: un `ViewGroup` care afișează o listă verticală derulabilă.
// DE CE E AICI: ecranul principal e, practic, o listă cu un meniu contextual.
// DE CE NU `RecyclerView`: 20 de rânduri statice, fără animații, fără view-uri
//   reciclate complicate. `ListView` e suficient și cere zero cod de adapter.
// ======================================================================================
import android.widget.ListView;

// ======================================================================================
// IMPORT 4: android.widget.PopupMenu — meniul ancorat pe rând
// ======================================================================================
// CE ESTE: un meniu plutitor, atașat de un view anume (ancora).
// DE CE E AICI: apăsarea lungă pe un rând trebuie să deschidă Open / Rename / Delete
//   lângă rândul respectiv, nu în colțul ecranului.
// DE CE NU `androidx.appcompat.widget.PopupMenu`: ar fi mers, dar varianta de
//   platformă e suficientă. Diferența se vede doar la stilul fundalului și la ripple.
// ======================================================================================
import android.widget.PopupMenu;

// ======================================================================================
// IMPORT 5: android.widget.Toast — mesajul scurt, fără acțiune
// ======================================================================================
// CE ESTE: un text care apare și dispare singur, fără să blocheze ecranul.
// DE CE E AICI: toate ramurile de meniu sunt demonstrații — un `Toast` e suficient.
// DE CE NU `Snackbar`: `Snackbar` are nevoie de un view părinte și de un `.show()`
//   suplimentar. Pentru o confirmare fără acțiune, `Toast` e mai direct.
// ======================================================================================
import android.widget.Toast;

// ======================================================================================
// IMPORT 6-13: androidx.* — infrastructura activității
// ======================================================================================
// EdgeToEdge              → desenare sub barele de sistem (API 21+).
// OnBackPressedCallback   → mecanismul modern pentru butonul Back.
// AppCompatActivity       → activitatea de bază, cu suport AppCompat.
// Insets                  → dreptunghiurile barelor de sistem, în pixeli.
// GravityCompat           → START/END, sigure pentru RTL.
// ViewCompat              → listener-ul de insets, compatibil pe toate API-urile.
// WindowInsetsCompat      → tipurile de insets (systemBars, ime, displayCutout).
// DrawerLayout            → containerul cu sertar (vine tranzitiv prin `material`).
// ======================================================================================
import androidx.activity.EdgeToEdge;
import androidx.activity.OnBackPressedCallback;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.GravityCompat;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.drawerlayout.widget.DrawerLayout;

// ======================================================================================
// IMPORT 14-15: Material — bara și sertarul
// ======================================================================================
// MaterialToolbar  → `Toolbar` cu stilizare Material 3 aplicată automat.
// NavigationView   → conținutul sertarului: meniu, iconițe, bifare, insets proprii.
// ======================================================================================
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.navigation.NavigationView;

/*
 * ======================================================================================
 * THEORY BLOCK: ACTIVITY ȘI CICLUL DE VIAȚĂ
 * ======================================================================================
 *
 * 1. CE E O ACTIVITY
 *    -   O componentă Android cu o fereastră proprie. Sistemul o creează, o afișează,
 *        o ascunde și o distruge după propriile reguli.
 *    -   Nu o instanțiezi tu cu `new MainActivity()`. O pornește sistemul, pe baza
 *        unui `Intent` sau a iconiței din lansator.
 *    -   Are un ciclu de viață cu stări: CREATED → STARTED → RESUMED → PAUSED →
 *        STOPPED → DESTROYED. Între stări, sistemul cheamă metode de callback.
 *
 * 2. `onCreate` — PRIMUL CALLBACK, O SINGURĂ DATĂ PER INSTANȚĂ
 *    -   Aici se construiește interfața: `setContentView`, `findViewById`, listenere.
 *    -   Se cheamă la pornire și la fiecare recreare (rotire, schimbare de temă,
 *        schimbare de limbă). La recreare primește `savedInstanceState` cu datele
 *        salvate anterior — aici e `null` prima dată și e ignorat mereu.
 *    -   Nu e locul pentru operații lungi: blocul rulează pe thread-ul principal,
 *        iar sistemul așteaptă să termine înainte să deseneze primul cadru.
 *
 * 3. ORDINEA OBLIGATORIE ÎN `onCreate`
 *    -   `super.onCreate(...)` PRIMUL. Părintele inițializează infrastructura
 *        (inclusiv `OnBackPressedDispatcher`-ul folosit mai jos).
 *    -   `setContentView(...)` ÎNAINTE de orice `findViewById`. Altfel primești
 *        `null`, nu excepție — și `NullPointerException` apare mai târziu, pe o
 *        linie fără legătură aparentă.
 *    -   `findViewById` și listenere DUPĂ `setContentView`.
 *
 * 4. DE CE UN SINGUR `onCreate` E O PROBLEMĂ DIDACTICĂ, NU UNA TEHNICĂ
 *    -   Funcționează perfect. Dar șapte responsabilități într-o metodă de 100 de
 *        linii se citesc greu și se testează și mai greu.
 *    -   Într-o aplicație reală: metode private `setupToolbar()`, `setupDrawer()`,
 *        `setupList()`. Aici sunt lăsate inline ca să vezi ordinea reală a apelurilor.
 *
 * 5. CE ÎNSEAMNĂ „CONTEXT"
 *    -   `this` dintr-o activitate e un `Context` (mai exact `ContextThemeWrapper`):
 *        dă acces la resurse, la tema aplicației și la serviciile sistemului.
 *    -   Widget-urile cer un context TEMATIZAT. `getApplicationContext()` nu are
 *        tema activității — de aceea `new Button(SecondActivity.this)` și nu
 *        `new Button(getApplicationContext())`.
 *
 * REF: cap. 15 — DMA02: Application și ciclu de viață; documentația
 *      `android.app.Activity` și `androidx.activity.ComponentActivity`.
 * ======================================================================================
 */

public class MainActivity extends AppCompatActivity {

    // ==================================================================================
    // CÂMP 1: drawerLayout
    // ==================================================================================
    // CE ESTE: referința la `DrawerLayout`-ul din XML.
    // UNDE E FOLOSIT: în trei locuri — listener-ul sertarului (`closeDrawer`),
    //   callback-ul Back (`isDrawerOpen` + `closeDrawer`) și hamburger (`openDrawer`).
    // DE CE E CÂMP ȘI NU LOCALĂ: toate cele trei utilizări sunt în `onCreate`, deci
    //   ar fi mers și locală. E câmp din obișnuință, ca să fie la îndemână dacă
    //   adaugi metode noi.
    // `private` — nimic din afară nu are nevoie de el.
    // ==================================================================================
    private DrawerLayout drawerLayout;

    // ==================================================================================
    // CÂMP 2: listView
    // ==================================================================================
    // CE ESTE: referința la lista din XML.
    // UNDE E FOLOSIT: în listener-ul de apăsare lungă, ca să citească textul rândului
    //   apăsat (`getItemAtPosition(position)`).
    // DE CE E CÂMP: lambda de long press se execută DUPĂ ce `onCreate` s-a terminat.
    //   O variabilă locală ar fi prinsă în closure (lambda capturează doar variabile
    //   effectively final), dar un câmp e mai clar și supraviețuiește cât trăiește
    //   activitatea.
    // ==================================================================================
    private ListView listView;

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: onCreate(Bundle savedInstanceState)
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   Callback-ul de creare al activității. Rulează o dată per instanță, pe thread-ul
     *   principal, înainte ca primul cadru să fie desenat. Aici se construiește tot
     *   arborele de view-uri și se leagă toate listenerele.
     *
     * LOGIC (ordinea reală din cod):
     *   1. `super.onCreate`                — inițializează părintele (inclusiv dispatcher-ul Back)
     *   2. `EdgeToEdge.enable`             — fereastra se întinde sub barele de sistem
     *   3. `setContentView`                — umflă `activity_main.xml`
     *   4. insets pe `R.id.main`           — padding ca să nu stai sub ceas
     *   5. `listView` + apăsare lungă      — `PopupMenu` ancorat pe rând
     *   6. `drawerLayout`/`toolbar`/`nav`  — cele trei componente găsite după id
     *   7. listener sertar                 — schimbă titlul, închide sertarul
     *   8. callback Back                   — închide sertarul sau deleagă
     *   9. hamburger                       — deschide sertarul
     *  10. meniu toolbar                   — Search / Share / Settings
     *
     * REF:
     *   cap. 14 (secțiunile 14.1–14.6), documentația `Activity#onCreate`.
     *
     * RISK:
     *   - `findViewById` înainte de `setContentView` → `null`, apoi NPE într-un listener.
     *   - `super.onCreate` omis → `SuperNotCalledException` la runtime.
     *   - listenerii mutați înainte de `setContentView` → primesc view-uri `null`.
     * ----------------------------------------------------------------------------------
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // PASUL 1: super.onCreate — lansează ciclul de viață al părintelui.
        // Fără el, `getOnBackPressedDispatcher()` de mai jos ar primi un dispatcher
        // neconfigurat. `@Override` e și o verificare: dacă semnătura greșește,
        // compilatorul te avertizează.
        super.onCreate(savedInstanceState);

        // PASUL 2: EdgeToEdge — fereastra se întinde sub status bar și sub bara de
        // navigare. Cheamă `WindowCompat.setDecorFitsSystemWindows(window, false)`.
        // Fără el, aplicația ar avea bare de sistem opace și nu ai avea nevoie de
        // blocul de insets de mai jos. Cu el, AI nevoie — altfel primul rând din
        // listă intră sub ceas.
        EdgeToEdge.enable(this);

        // PASUL 3: setContentView — `LayoutInflater` citește XML-ul, creează
        // obiectele Java pentru fiecare tag și le atașează la fereastră.
        // Din acest moment, `findViewById` poate găsi ceva. Înainte, arborele nu există.
        // `R.layout` e resursa de layout (fișierul întreg); `R.id` e un identificator
        // dintr-un view. Două spații de nume diferite, generate în același `R.java`.
        setContentView(R.layout.activity_main);

        // PASUL 4: insets — când sistemul calculează cât ocupă barele, aplică pe
        // view-ul cu `id=main` un padding egal cu ele. Conținutul se mută în zona
        // sigură, fundalul rămâne întins pe tot ecranul.
        //
        // `ViewCompat.setOnApplyWindowInsetsListener` înregistrează un listener
        // compatibil: pe API vechi folosește metodele vechi, pe API nou pe cele noi.
        // Listener-ul rulează imediat după `setContentView` și apoi la fiecare
        // schimbare (rotire, tastatură, bare care apar/dispar). Nu rulează o singură
        // dată — de aceea codul din interior trebuie să fie idempotent.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            // `Type.systemBars()` = status bar + navigation bar + caption bar.
            // Nu include tastatura (`Type.ime()`) și nici decupajul (`Type.displayCutout()`).
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());

            // `setPadding` SUPRASCRIE padding-ul existent. Dacă `CoordinatorLayout`-ul
            // ar avea `android:padding="8dp"` în XML, cele 8dp ar dispărea la primul
            // insets. Corect ar fi `v.setPadding(base + insets.left, ...)`, cu valorile
            // de bază salvate într-un câmp. Aici XML-ul nu are padding, deci nu se vede.
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

            // `return insets` — NU `WindowInsetsCompat.CONSUMED`. Insets-urile merg mai
            // departe, la copii. Dacă le-ai consuma, `AppBarLayout` nu ar mai ști de ele
            // și `liftOnScroll` ar primi valori greșite. Consumi doar când ai tratat tu
            // complet zona și vrei să oprești propagarea.
            return insets;
        });

        // PASUL 5: lista. Metoda e generică (`<T extends View> T findViewById(int)`),
        // deci compilatorul deduce tipul din atribuire; nu e nevoie de cast.
        // Căutarea se face pe activitate, adică în tot arborele ferestrei. Dacă ai avea
        // două view-uri cu același id în layout-uri diferite, ai primi primul găsit —
        // de aceea id-urile trebuie să fie unice într-un layout.
        listView = findViewById(R.id.listView);

        // `setOnItemLongClickListener` înregistrează un listener pentru apăsare lungă
        // pe ORICE rând al listei. Nu există un listener „pe rând": `ListView` are unul
        // singur, pentru toate rândurile, și îți spune în parametri pe care rând s-a apăsat.
        //
        // Lambda cu patru parametri pentru `AdapterView.OnItemLongClickListener`:
        //   parent   : AdapterView<?> — `ListView`-ul însuși (aici nu e folosit)
        //   view     : View           — RÂNDUL apăsat; devine ancora meniului
        //   position : int            — indexul rândului în listă, 0-based
        //   id       : long           — id-ul elementului; pentru `ArrayAdapter` e
        //                               egal cu `position`. Tipul e `long` pentru că
        //                               `AdapterView` poate lucra și cu id-uri din
        //                               baze de date (`SQLite` folosește `long`).
        //
        // NU există `setOnItemClickListener` nicăieri în fișier. Un tap simplu pe rând
        // nu face nimic. Doar apăsarea lungă reacționează. E o alegere didactică:
        // proiectul demonstrează meniul contextual, nu navigarea.
        //
        // Ce se întâmplă la un tap simplu, concret: `ListView` primește `ACTION_DOWN`,
        // pornește un `CheckForLongPress` cu timeout-ul sistemului (~500 ms), iar la
        // `ACTION_UP` fără listener de click nu se întâmplă nimic. Rândul nici măcar
        // nu rămâne evidențiat — `ListView` în modul `CHOICE_MODE_NONE` nu ține selecție.
        //
        // De ce listener-ul e pe listă și nu pe adapter: adapterul produce view-uri,
        // nu evenimente. `ListView` e cel care știe poziția și rândul apăsat.
        //
        // ------------------------------------------------------------------------------
        // METHOD (lambda): onItemLongClick(parent, view, position, id)
        // THEORY: callback pentru apăsarea lungă pe un rând de listă.
        // LOGIC:  1. construiește un `PopupMenu` ancorat pe `view`;
        //         2. umflă `list_item_menu`;
        //         3. înregistrează listener-ul de element;
        //         4. `show()` și `return true`.
        // REF:    26.1.9–26.1.11
        // RISK:   fără `return true`, se declanșează și click-ul normal.
        // ------------------------------------------------------------------------------
        // Long press shows the popup menu
        listView.setOnItemLongClickListener((parent, view, position, id) -> {
            // `new PopupMenu(this, view)` — `this` e contextul (activitatea, pentru
            // temă), `view` e ancora. `PopupWindow` calculează poziția pornind de la
            // dreptunghiul view-ului și îl plasează dedesubt, dacă încape, sau deasupra,
            // dacă nu. De aceea meniul apare lipit de rând, nu în colțul ecranului.
            //
            // De ce NU `listView` ca ancoră: `ListView` e un dreptunghi mare, cât tot
            // ecranul. Meniul ar apărea la marginea lui — adică sus, lângă bară — și ar
            // acoperi rândul apăsat. De ce NU `toolbar`: ar arăta ca un meniu de overflow
            // al barei, nu ca un meniu contextual.
            PopupMenu popup = new PopupMenu(this, view);   // anchored to the pressed row

            // `getMenuInflater()` vine din `Context` (activitatea) și întoarce un
            // `MenuInflater` — un parser pentru `<menu>`, nu pentru layout-uri.
            // `inflate(resursă, meniu)` — al doilea argument e `Menu`-ul DESTINAȚIE,
            // obținut cu `popup.getMenu()`. Nu e ca la `setContentView`, unde dai doar
            // resursa. De ce `R.menu.list_item_menu` și nu `top_app_bar`: sunt două
            // meniuri diferite, pentru două contexte diferite. `list_item_menu` are
            // „Open / Rename / Delete" — acțiuni pe un rând. `top_app_bar` are
            // „Search / Share / Settings" — acțiuni pe ecran.
            //
            // Ce se întâmplă dacă uiți `inflate`: meniul e gol. `popup.show()` afișează
            // un dreptunghi fără elemente, iar listener-ul nu se apelează niciodată.
            popup.getMenuInflater().inflate(R.menu.list_item_menu, popup.getMenu());

            // `setOnMenuItemClickListener` se apelează ÎNAINTE de `popup.show()`;
            // dacă îl înregistrezi după, meniul e deja afișat și click-urile din prima
            // secundă se pierd.
            popup.setOnMenuItemClickListener(menuItem -> {
                // `getItemId()` — id-ul din XML (`R.id.action_open` etc.). Nu poziția:
                // dacă reordonezi elementele în XML, id-urile rămân aceleași, pozițiile nu.
                int itemId = menuItem.getItemId();

                // `position` e capturat din lambda exterioară. E un parametru de metodă,
                // deci effectively final — Java permite capturarea. Dacă ai încerca să-l
                // modifici între timp (`position++`), compilatorul ar refuza.
                //
                // `getItemAtPosition(position)` întoarce un `CharSequence` — textul din
                // `@array/items`, pentru că `ListView` și-a construit singur un
                // `ArrayAdapter` din atributul `android:entries` din XML. Nu ai scris
                // niciun adapter în cod.
                //
                // `.toString()` e redundant pentru un `String`, dar inofensiv. Devine
                // necesar în momentul în care pui obiecte în listă: acolo `toString()`
                // e contractul de afișare.
                String selected = listView.getItemAtPosition(position).toString();

                // `return true` = „am tratat eu click-ul". Meniul se închide și
                // evenimentul nu mai circulă. `return false` = „nu mă interesează" —
                // sistemul încearcă handler-ul implicit.
                //
                // Ce se întâmplă exact cu `return false` pe `PopupMenu`: `PopupMenu`
                // închide meniul oricum, la click. Valoarea se propagă la
                // `MenuBuilder.performItemAction`, care, dacă nu e consumată, continuă
                // cu acțiunea implicită a elementului — de exemplu un `Intent` setat pe
                // item. La noi elementele nu au `Intent`, deci `false` nu schimbă nimic
                // vizibil. Dar contractul rămâne: `true` = tratat.
                if (itemId == R.id.action_open) {
                    // `Toast.makeText(...).show()` — două apeluri. `makeText`
                    // CONSTRUIEȘTE, `show()` AFIȘEAZĂ. Fără `.show()`, nu se întâmplă
                    // nimic, fără eroare. E cea mai frecventă greșeală la început.
                    // `LENGTH_SHORT` ≈ 2 secunde; `LENGTH_LONG` ≈ 3,5 secunde. Valorile
                    // sunt indicii, nu garanții: producătorul poate ajusta durata.
                    Toast.makeText(this, "Open: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_rename) {
                    Toast.makeText(this, "Rename: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_delete) {
                    Toast.makeText(this, "Delete: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                }
                // `return false` la final e cod mort — toate cele trei id-uri sunt
                // acoperite mai sus. Rămâne corect: dacă adaugi un al patrulea element
                // în `list_item_menu.xml` și uiți să-l tratezi, click-ul cade frumos în
                // handler-ul implicit în loc să facă ceva imprevizibil.
                return false;
            });

            // `popup.show()` — până aici doar ai configurat meniul. Abia acum apare pe
            // ecran. Ordinea e: construiești → umfli → înregistrezi listener → afișezi.
            popup.show();

            // `return true` din listener-ul de apăsare lungă — spune listei „apăsarea
            // lungă a fost tratată". Dacă ai întoarce `false`, sistemul ar considera
            // apăsarea lungă netratată și ar putea declanșa și un click normal în urma
            // ei. Rezultatul: meniul apare și, simultan, se execută acțiunea de click.
            //
            // Mecanismul din spate: `AdapterView` ține un flag intern
            // (`mHasPerformedLongPress`). Listener-ul îl setează doar dacă întoarce
            // `true`. La `ACTION_UP`, dacă flagul e setat, click-ul e ignorat. Dacă nu,
            // `performClick()` rulează normal.
            //
            // Ordinea contează: `popup.show()` ÎNAINTE de `return true`. Invers nu se
            // poate — `return` încheie lambda.
            return true;   // true = long press handled, so the normal click doesn't also fire
        });


        // PASUL 6: legarea celor trei componente. Toate trei id-urile trebuie să existe
        // în `activity_main.xml`, altfel primești `null` și un `NullPointerException`
        // la primul apel. Ordinea celor trei linii nu contează — sunt independente.
        // Contează doar să fie după `setContentView`.
        //
        // `toolbar` și `navigationView` sunt LOCALE, `drawerLayout` e CÂMP.
        // Inconsecvență reală în cod: toate trei sunt folosite doar în `onCreate`.
        // Merge și cu toate trei locale; merge și cu toate trei câmpuri. Alege o
        // variantă și ține-te de ea.
        drawerLayout = findViewById(R.id.drawerLayout);
        MaterialToolbar toolbar = findViewById(R.id.topAppBar);
        NavigationView navigationView = findViewById(R.id.navigationView);


        // PASUL 7: listener-ul sertarului.
        //
        // Ce face fiecare ramură: schimbă TITLUL barei de sus. Conținutul listei
        // rămâne același — cele 20 de „Item N". Aplicația e o demonstrație de
        // navigare, nu una de date.
        //
        // `toolbar.setTitle("Inbox")` suprascrie `app:title="Inbox"` din XML.
        // Valoarea din XML e doar cea inițială; după primul click, titlul vine din cod.
        //
        // `nav_settings` e tratat diferit — un `Toast`, nu un titlu. E singurul element
        // din submeniul „Other", deci nu are sens să schimbe titlul ecranului.
        //
        // De ce `item.getItemId()` și nu `item.getTitle()`: titlul e text vizibil,
        // care se poate traduce sau schimba. Id-ul e stabil. Comparația cu `R.id.*`
        // e singura care rezistă la o schimbare de limbă.
        //
        // Ce se întâmplă dacă niciun `if` nu se potrivește: listener-ul continuă,
        // cheamă `item.setChecked(true)` și închide sertarul. Elementul necunoscut
        // rămâne bifat, dar titlul nu se schimbă. Nu e o eroare — e un comportament
        // implicit.
        //
        // ------------------------------------------------------------------------------
        // METHOD (lambda): onMenuItemClick(item) — selecția din sertar
        // THEORY: callback pentru un element din `NavigationView`.
        // LOGIC:  1. citește id-ul; 2. actualizează titlul; 3. setează bifa;
        //         4. închide sertarul; 5. `return true`.
        // REF:    26.1.13
        // RISK:   fără `closeDrawer`, sertarul rămâne peste ecran.
        // ------------------------------------------------------------------------------
        // Drawer item clicks
        navigationView.setNavigationItemSelectedListener(item -> {
            int id = item.getItemId();

            if (id == R.id.nav_inbox) {
                toolbar.setTitle("Inbox");
            } else if (id == R.id.nav_sent) {
                toolbar.setTitle("Sent");
            } else if (id == R.id.nav_trash) {
                toolbar.setTitle("Trash");
            } else if (id == R.id.nav_settings) {
                Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
            }

            // `item.setChecked(true)` — meniul are `android:checkableBehavior="single"`
            // (vezi 26.6), deci se comportă ca un grup de radio butoane: un singur
            // element bifat. Apelul explicit garantează starea după ce sertarul se
            // închide și după redeschidere.
            //
            // De ce e nevoie de `setChecked` explicit dacă meniul e deja „single":
            // `checkableBehavior` face grupul exclusiv, dar nu înseamnă că
            // `NavigationView` marchează automat elementul la click. Codul nu se
            // bazează pe comportamentul implicit — îl setează singur. E o alegere
            // defensivă, bună.
            item.setChecked(true);

            // `closeDrawer(GravityCompat.START)` — închide sertarul din partea `start`.
            // Trebuie să corespundă cu `android:layout_gravity="start"` din XML. Dacă
            // în XML e `start` și în cod `end`, sertarul rămâne deschis.
            //
            // De ce `setNavigationItemSelectedListener` NU închide sertarul singur:
            // `NavigationView` e un container de meniu. Nu are referință la
            // `DrawerLayout` și nu știe că există unul. Sunt vecini în arbore, nu
            // părinte-copil. Listener-ul e doar un callback: „s-a apăsat elementul X".
            // Ce faci cu informația — schimbi titlul, închizi sertarul, pornești un
            // ecran — e decizia ta, în codul tău.
            //
            // Consecința practică: dacă uiți `closeDrawer`, sertarul rămâne peste
            // ecran după selecție. Utilizatorul vede titlul schimbat, dar nu vede
            // conținutul. E primul lucru care lipsește dintr-o implementare grăbită.
            drawerLayout.closeDrawer(GravityCompat.START);

            // `return true` — spune `NavigationView` că click-ul a fost tratat. Dacă
            // întorci `false`, elementul nu se marchează vizual ca selectat. Contractul
            // documentat al variantei vechi (`OnNavigationItemSelectedListener`) e
            // explicit: „true to display the item as the selected item". Varianta nouă
            // (`MenuItem.OnMenuItemClickListener`) propagă valoarea în `MenuBuilder`,
            // iar `NavigationView` o folosește la fel.
            //
            // De ce codul cheamă totuși `setChecked(true)`: pentru că se bazează pe
            // contract, nu pe implementare. Dacă `NavigationView` s-ar schimba, bifarea
            // rămâne corectă.
            return true;
        });

        // PASUL 8: butonul Back. De ce nu `@Override public void onBackPressed()`:
        // metoda a fost marcată deprecated din API 33, iar `OnBackPressedDispatcher`
        // e mecanismul oficial. Pe lângă asta, dispatcher-ul permite MAI MULTE
        // callback-uri în lanț, fiecare cu prioritatea lui — o singură suprascriere
        // nu poate face asta.
        //
        // `new OnBackPressedCallback(true)` — argumentul e starea inițială:
        // `true` = activ. Un callback dezactivat nu primește evenimente.
        //
        // `addCallback(this, ...)` — primul argument e `LifecycleOwner` (activitatea).
        // Dispatcher-ul ține callback-ul doar cât timp activitatea e în `STARTED`.
        // La `onStop`, callback-ul e scos automat; la `onStart`, revine. Nu trebuie
        // să-l elimini manual. Varianta fără `LifecycleOwner` lasă callback-ul în
        // listă până îl scoți tu — dacă uiți, ține o referință la activitate.
        //
        // Logica, pas cu pas:
        //   1. S-a apăsat Back.
        //   2. Sertarul e deschis? → închide-l. Sfârșit. Utilizatorul rămâne pe ecran.
        //   3. Sertarul e închis? → `setEnabled(false)`, apoi re-trimite evenimentul.
        //
        // De ce `setEnabled(false)` înainte de re-trimitere: fără el,
        // `onBackPressed()` ar intra din nou în ACELAȘI callback, care ar vedea
        // sertarul închis și ar re-trimite evenimentul — recursie infinită,
        // `StackOverflowError`. Dezactivându-te pe tine însuți, lași următorul handler
        // din lanț (cel implicit, care închide activitatea) să primească evenimentul.
        //
        // Mecanismul exact: `OnBackPressedDispatcher` ține callback-urile într-o
        // colecție ordonată. `onBackPressed()` o parcurge de la ultimul adăugat spre
        // primul și se oprește la primul callback ACTIV care tratează evenimentul.
        // Dacă callback-ul tău se reapelează fără să se dezactiveze, parcurgerea îl
        // găsește tot pe el. `setEnabled(false)` îl scoate din colecția de callback-uri
        // active, deci parcurgerea trece mai departe.
        //
        // Ce e „handler-ul implicit": `ComponentActivity` înregistrează un fallback
        // care cheamă `super.onBackPressed()` — adică `finish()` pe activitate. Dacă
        // nu ar exista, Back ar fi ignorat.
        //
        // De ce nu `finish()` direct: `finish()` ar închide activitatea, dar ar sări
        // peste orice alt callback din lanț (de exemplu un `NavController` care ar
        // trebui să gestioneze Back întâi). Delegarea păstrează lanțul intact.
        //
        // ------------------------------------------------------------------------------
        // METHOD: handleOnBackPressed()
        // THEORY: callback-ul care interceptează Back înaintea sistemului.
        // LOGIC:  1. dacă sertarul e deschis, închide-l;
        //         2. altfel dezactivează-te și delegă evenimentul.
        // REF:    26.1.14
        // RISK:   fără `setEnabled(false)`, recursie infinită.
        // ------------------------------------------------------------------------------
        // Back button closes the drawer first if it's open
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
                    drawerLayout.closeDrawer(GravityCompat.START);
                } else {
                    setEnabled(false);
                    getOnBackPressedDispatcher().onBackPressed();
                }
            }
        });


        // PASUL 9: hamburger-ul. Iconița din stânga barei (cele trei linii) deschide
        // sertarul. Iconița există deja în XML — `app:navigationIcon="@drawable/ic_menu"`.
        // Fără listener, e doar decorativă: se vede, se apasă, nu se întâmplă nimic.
        // Listener-ul e cel care o transformă în buton.
        //
        // `setNavigationOnClickListener` — un singur listener pentru iconița de
        // navigare a toolbar-ului. Nu primește poziție sau id: e un singur buton.
        //
        // De ce nu `ActionBarDrawerToggle`: varianta clasică leagă automat iconița,
        // sertarul și accesibilitatea, dar cere ca toolbar-ul să fie setat ca
        // `ActionBar` (`setSupportActionBar`). Aici toolbar-ul e folosit ca view
        // obișnuit, deci legătura se face manual. E mai puțin cod, dar și mai puțin
        // automatism — de exemplu, iconița nu se animă în săgeată când sertarul e
        // deschis, iar descrierea de accesibilitate nu se actualizează automat.
        //
        // `GravityCompat.START` — aceeași direcție ca `layout_gravity` din XML.
        // A patra apariție în fișier.
        // Hamburger (navigation) icon
        toolbar.setNavigationOnClickListener(v -> {
            drawerLayout.openDrawer(GravityCompat.START);
        });

        // PASUL 10: meniul din toolbar. Meniul e deja umflat —
        // `app:menu="@menu/top_app_bar"` din XML. Aici doar reacționezi la click.
        // Dacă ai fi folosit `setSupportActionBar(toolbar)`, ai fi suprascris
        // `onCreateOptionsMenu` și `onOptionsItemSelected`; cu toolbar-ul ca view
        // simplu, ăsta e cârligul corect.
        //
        // `action_settings` are `app:showAsAction="never"` — de aceea ajunge în
        // meniul „⋮" (overflow), nu pe bară. `action_search` și `action_share` au
        // `ifRoom` — apar direct pe bară dacă încap.
        //
        // Comentariul `// open settings` marchează un loc gol. Ramura afișează un
        // `Toast`, dar intenția era deschiderea unui ecran de setări. E un TODO
        // deghizat.
        //
        // `return false` la final e cod mort — toate cele trei id-uri sunt acoperite
        // mai sus. Rămâne corect: dacă adaugi un al patrulea element în meniu și uiți
        // să-l tratezi, click-ul cade frumos în handler-ul implicit în loc să arunce
        // excepție.
        //
        // Ce se întâmplă cu `return false` pe un element din overflow: `Toolbar`
        // propagă valoarea la `MenuBuilder`, care încearcă acțiunea implicită a
        // elementului (un `Intent`, un `ActionProvider`). La noi nu există niciuna,
        // deci meniul se închide și atât.
        //
        // ------------------------------------------------------------------------------
        // METHOD (lambda): onMenuItemClick(item) — meniul barei
        // THEORY: callback pentru Search / Share / Settings.
        // LOGIC:  1. citește id-ul; 2. afișează un `Toast`; 3. `return true`.
        // REF:    26.1.16
        // RISK:   `return false` pe un id necunoscut lasă evenimentul să circule.
        // ------------------------------------------------------------------------------
        // Search, share and overflow menu items
        toolbar.setOnMenuItemClickListener(item -> {
            int id = item.getItemId();

            if (id == R.id.action_search) {
                Toast.makeText(this, "Search", Toast.LENGTH_SHORT).show();
                return true;
            } else if (id == R.id.action_share) {
                Toast.makeText(this, "Share", Toast.LENGTH_SHORT).show();
                return true;
            } else if (id == R.id.action_settings) {
                // open settings
                Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
                return true;
            }
            return false;
        });
    }
}
```

**Ce reții din fișierul ăsta:** un singur `onCreate` cu zece pași; ordinea `super` → `EdgeToEdge` → `setContentView` → `findViewById` e obligatorie; `GravityCompat.START` apare de patru ori și trebuie să fie identic cu `layout_gravity` din XML; `NavigationView` nu închide sertarul singur; callback-ul de Back se dezactivează înainte să delege.

---

## 26.2 `SecondActivity.java` — dialog și Snackbar

**Atenție înainte de orice:** `SecondActivity` e declarată în manifest, dar **nu e pornită nicăieri**. Nu există `Intent` în `MainActivity` — doar importul nefolosit. Ecranul e complet funcțional dacă îl lansezi manual (Run → Edit Configurations → Launch: Specified Activity), dar în aplicația livrată e inaccesibil. E un ecran de laborator rămas nelegat, nu un bug de compilare.

```java
/*
 * ======================================================================================
 * FIȘIER: SecondActivity.java
 * ======================================================================================
 * ROL:
 *   Ecran de laborator pentru trei lucruri care nu încap în MainActivity:
 *     1. un dialog de confirmare construit cu `AlertDialog.Builder`;
 *     2. un `Snackbar` cu acțiune de anulare;
 *     3. un view creat din cod (`new Button`) și adăugat în arbore.
 *
 * CE DEMONSTREAZĂ:
 *   1. AlertDialog.Builder   — lanț de settere + `show()`.
 *   2. Snackbar.make(...)    — feedback tranzitoriu cu buton de acțiune.
 *   3. addButton()           — `new Button(ctx)`, `setId`, `LayoutParams`, `addView`.
 *
 * DEPINDE DE:
 *   - android.app.AlertDialog        → varianta de PLATFORMĂ (nu AppCompat)
 *   - com.google.android.material    → Snackbar
 *   - android:onClick="btnClick"     → legătura din XML, prin reflecție
 *
 * CE NU FACE:
 *   - nu e pornită din MainActivity (niciun `Intent` în tot proiectul);
 *   - nu salvează butoanele adăugate la rotire;
 *   - nu validează nimic — orice click pe „Do it!" adaugă un buton.
 *
 * REF: cap. 14 (secțiunea despre dialoguri), documentația `AlertDialog.Builder`,
 *      `Snackbar`, `ViewGroup.LayoutParams`.
 * ======================================================================================
 */

package ro.ase.ie.dma03;

// ======================================================================================
// IMPORT 1: android.app.AlertDialog — ATENȚIE, varianta de PLATFORMĂ
// ======================================================================================
// CE ESTE: dialogul standard al sistemului Android.
// DE CE E O ALEGERE DISCUTABILĂ: există și `androidx.appcompat.app.AlertDialog`.
//   Varianta de platformă folosește `android.R.attr.alertDialogTheme` al temei
//   curente; varianta AppCompat forțează tema și stilul bibliotecii. Cu
//   `Theme.Material3.DayNight.NoActionBar`, diferența vizuală poate fi mică sau
//   nulă, dar varianta AppCompat e cea care respectă tema aplicației în toate
//   cazurile. Funcțional sunt identice.
// DE CE CONTEAZĂ TOTUȘI: dacă tema aplicației ar fi una AppCompat pură (fără
//   Material3), `android.app.AlertDialog` ar cădea pe stilul de sistem — butoane
//   altfel colorate, alt font, altă umbră.
// ======================================================================================
import android.app.AlertDialog;

// ======================================================================================
// IMPORT 2: android.content.DialogInterface — interfața butoanelor dialogului
// ======================================================================================
// CE ESTE: interfața care conține `OnClickListener`-ul dialogului.
// DE CE E IMPORTATĂ SEPARAT: `OnClickListener` e o interfață IMBRICATĂ în ea:
//   `DialogInterface.OnClickListener`. Fără import, ar trebui scris numele complet.
// ======================================================================================
import android.content.DialogInterface;

// ======================================================================================
// IMPORT 3: android.os.Bundle — starea salvată la recreare
// ======================================================================================
// Semnătura lui `onCreate(Bundle)` o cere. Codul nu îl citește niciodată.
// ======================================================================================
import android.os.Bundle;

// ======================================================================================
// IMPORT 4-5: android.util.DisplayMetrics + android.util.TypedValue
// ======================================================================================
// FOLOSITE DOAR ÎN `addButton`, pentru conversia 50dp → pixeli.
// `DisplayMetrics` = densitatea ecranului (câți pixeli are un dp).
// `TypedValue.applyDimension` = conversia propriu-zisă, pentru orice unitate.
// REZULTATUL E COD MORT (vezi 26.2.7). Importurile rămân pentru că linia care le
// folosește există.
// ======================================================================================
import android.util.DisplayMetrics;
import android.util.TypedValue;

// ======================================================================================
// IMPORT 6-7: android.view.View + android.view.ViewGroup
// ======================================================================================
// `View` — tipul parametrului din `btnClick(View view)`. Semnătura e impusă de
//   `android:onClick` din XML.
// `ViewGroup` — clasa de bază pentru `LayoutParams`. `ViewGroup.LayoutParams` e
//   tipul cerut de `setLayoutParams`; `LinearLayout.LayoutParams` ar fi subtipul
//   cu `weight`.
// ======================================================================================
import android.view.View;
import android.view.ViewGroup;

// ======================================================================================
// IMPORT 8-10: android.widget.Button + LinearLayout + Toast
// ======================================================================================
// `Button`        — widget-ul creat din cod.
// `LinearLayout`  — containerul în care se adaugă butoanele.
// `Toast`         — mesajul de anulare din butonul negativ.
// ======================================================================================
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;

// ======================================================================================
// IMPORT 11-15: androidx.* — infrastructura activității
// ======================================================================================
// Identice cu cele din MainActivity: EdgeToEdge, AppCompatActivity, Insets,
// ViewCompat, WindowInsetsCompat. Blocul de insets e copiat cuvânt cu cuvânt.
// ======================================================================================
import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

// ======================================================================================
// IMPORT 16: com.google.android.material.snackbar.Snackbar
// ======================================================================================
// CE ESTE: bara de feedback de la baza ecranului, cu text + acțiune opțională.
// DE CE VINE DIN MATERIAL: `Snackbar` nu face parte din platformă. De aceea
//   `SecondActivity` are nevoie de `libs.material` în dependențe — la fel ca
//   `MainActivity` pentru toolbar.
// CE S-AR ÎNTÂMPLA CU `Toast`: ai pierde butonul de acțiune. `Toast` nu are
//   `setAction`, nu poate fi închis de utilizator și nu are durată indefinită.
//   Pentru „anulează ultima acțiune", `Snackbar` e singura variantă din platformă.
// ======================================================================================
import com.google.android.material.snackbar.Snackbar;

/*
 * ======================================================================================
 * THEORY BLOCK: TREI MODALITĂȚI DE FEEDBACK ȘI UN VIEW CONSTRUIT DIN COD
 * ======================================================================================
 *
 * 1. DIALOG — BLOCHEAZĂ, CERE O DECIZIE
 *    -   `AlertDialog` apare peste ecran, într-o fereastră separată. Utilizatorul
 *        trebuie să răspundă înainte să continue.
 *    -   Se construiește cu `AlertDialog.Builder`: un obiect care adună configurația
 *        (titlu, mesaj, butoane) și abia la `show()` creează dialogul.
 *    -   Fiecare setter întoarce ACELAȘI builder → lanț de apeluri.
 *
 * 2. TOAST — TREACE, NU CERE NIMIC
 *    -   Text scurt, fără acțiune, fără layout. Apare și dispare singur.
 *    -   Nu are nevoie de un view părinte: e desenat într-o fereastră proprie.
 *
 * 3. SNACKBAR — TREACE, DAR POATE FI ANULAT
 *    -   Bară la baza ecranului, cu text + un buton de acțiune opțional.
 *    -   SPRE DEOSEBIRE DE TOAST, are nevoie de un VIEW: se inserează în arborele
 *        de view-uri, nu într-o fereastră separată. De aici al doilea argument
 *        din `make(...)`.
 *    -   Cu un `CoordinatorLayout` părinte, poate fi glisat pentru închidere și
 *        poate împinge un FAB în sus. Cu un `LinearLayout`, funcționează, dar
 *        fără aceste bonusuri.
 *
 * 4. VIEW CONSTRUIT DIN COD
 *    -   Orice widget are un constructor care cere un `Context` TEMATIZAT.
 *    -   Un view creat din cod nu are id, nu are `LayoutParams` și nu e în arbore.
 *        Trei operații separate:
 *          a) `setId(...)`            → ca să poată fi găsit cu `findViewById`;
 *          b) `setLayoutParams(...)`  → ca părintele să știe cum să-l măsoare;
 *          c) `parent.addView(...)`   → ca să intre în arbore și să fie desenat.
 *    -   Ordinea contează: `addView` fără `LayoutParams` funcționează (părintele
 *        generează unele implicite), dar `findViewById` fără `setId` nu găsește nimic.
 *
 * 5. DE CE UN VIEW ADĂUGAT DIN COD DISPARE LA ROTIRE
 *    -   Arborele de view-uri se reconstruiește din XML la fiecare recreare.
 *    -   Butonul adăugat trăiește doar în instanța veche a activității.
 *    -   Ca să supraviețuiască, ar trebui salvat în `savedInstanceState` (o listă de
 *        id-uri/text) și reconstruit în `onCreate`.
 *
 * REF: cap. 14 (dialoguri și Snackbar), documentația `AlertDialog.Builder`,
 *      `Snackbar`, `ViewGroup.addView`.
 * ======================================================================================
 */

public class SecondActivity extends AppCompatActivity {

    // ==================================================================================
    // CÂMP: inflatedLayout
    // ==================================================================================
    // CE ESTE: rădăcina din `activity_second.xml` — un `LinearLayout` vertical.
    // DE CE E CÂMP ȘI NU LOCALĂ: e folosit în TREI metode — `onCreate` (inițializare),
    //   `btnClick` (Snackbar) și `addButton` (`addView`).
    // FĂRĂ `private` — inconsecvență față de `MainActivity`, unde câmpurile sunt
    //   `private`. Nu strică nimic (suntem în același pachet), dar convenția e `private`.
    // NUMELE E ÎNȘELĂTOR: nu e un layout „umflat" la runtime, e layout-ul din XML.
    //   Umflarea a făcut-o `setContentView`. Numele sugerează intenția — un container
    //   în care se adaugă view-uri — nu mecanismul.
    // ==================================================================================
    LinearLayout inflatedLayout;

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: onCreate(Bundle savedInstanceState)
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   Callback-ul de creare. Aici se umflă `activity_second.xml` și se obține
     *   referința la containerul în care vor fi adăugate butoanele.
     *
     * LOGIC:
     *   1. `super.onCreate` — părintele.
     *   2. `EdgeToEdge.enable` — desenare sub bare.
     *   3. `setContentView` — umflă layout-ul.
     *   4. insets pe `R.id.main` — padding pentru barele de sistem.
     *   5. `inflatedLayout = findViewById(R.id.main)` — referința la container.
     *
     * REF: cap. 14, documentația `Activity#onCreate`.
     *
     * RISK:
     *   - `inflatedLayout` inițializat înainte de `setContentView` → `null`, apoi
     *     `NullPointerException` la primul `addView`.
     * ----------------------------------------------------------------------------------
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_second);

        // Blocul de insets e IDENTIC cu cel din MainActivity — copiat. Aici
        // `R.id.main` e pe `LinearLayout`-ul rădăcină, nu pe un `CoordinatorLayout`.
        // Funcționează la fel: padding pe rădăcină, copiii se mută în zona sigură.
        //
        // De ce e copiat și nu extras într-o funcție utilitară: într-un proiect de
        // laborator, copierea e acceptabilă. Într-o aplicație reală, ai avea o funcție
        // `applyInsets(View root)` într-o clasă de utilitare — sau ai folosi
        // `ViewCompat.setOnApplyWindowInsetsListener` o singură dată, într-o clasă
        // de bază.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // ULTIMA linie — după `setContentView`. Dacă ar fi înainte, ar primi `null`
        // și primul `addView` ar arunca `NullPointerException`.
        //
        // Ce face `findViewById(R.id.main)` aici: caută în arborele
        // `activity_second.xml`. Id-ul `main` există și în `activity_main.xml`, dar
        // cele două layout-uri nu coexistă niciodată în același arbore — fiecare
        // activitate are fereastra ei. Nu e o coliziune.
        inflatedLayout = findViewById(R.id.main);
    }

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: btnClick(View view)
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   Metodă publică, cu semnătură fixă, chemată prin REFLECȚIE de platformă atunci
     *   când se apasă butonul cu `android:onClick="btnClick"` din XML. Nu există
     *   `setOnClickListener` nicăieri în cod — toată legătura e în XML.
     *
     * LOGIC:
     *   1. Creează un `AlertDialog.Builder` cu contextul activității.
     *   2. Înlănțuie: titlu → mesaj → cancelable → buton pozitiv → buton negativ.
     *   3. În butonul pozitiv: `addButton()` întoarce id-ul noului buton.
     *   4. Afișează un `Snackbar` cu acțiunea „Cancel", care șterge butonul după id.
     *   5. În butonul negativ: doar un `Toast`.
     *   6. `builder.show()` — abia aici dialogul apare pe ecran.
     *
     * REF:
     *   cap. 14 (secțiunea despre dialoguri), documentația `android:onClick`,
     *   `AlertDialog.Builder`, `Snackbar.make`.
     *
     * RISK:
     *   - metoda făcută `private` → compilează, dar la click:
     *     `IllegalStateException: Could not find method btnClick(View) ...`
     *   - parametrul schimbat din `View` în alt tip → aceeași excepție, la runtime.
     *   - `builder.show()` uitat → dialogul e construit și niciodată afișat.
     * ----------------------------------------------------------------------------------
     */
    public void btnClick(View view) {
        // Semnătura e IMPUSĂ de XML. În `activity_second.xml`, butonul are
        // `android:onClick="btnClick"`. Android caută la runtime, prin reflecție, o
        // metodă `public void btnClick(View)` în contextul activității.
        //
        // CONSECINȚA: dacă o faci `private`, sau îi schimbi parametrul în `Object`,
        // sau o redenumești fără să modifici XML-ul, COMPILAREA TRECE. Eroarea apare
        // la click: `IllegalStateException: Could not find method btnClick(View) in a
        // parent or ancestor Context`. Unul dintre puținele locuri din Android unde
        // greșeala nu se vede la build.
        //
        // `view` e butonul apăsat. Aici nu e folosit — codul nu are nevoie să știe
        // care buton a fost. Dar parametrul e obligatoriu: reflecția caută exact
        // semnătura cu un `View`.
        //
        // De ce `public` și nu `protected`: reflecția caută metode publice.
        // `protected` sau package-private nu sunt găsite din `View`-ul care face
        // apelul (alt pachet).
        //
        // ALTERNATIVA MODERNĂ: `setOnClickListener` în `onCreate`. E mai sigur
        // (compilatorul verifică), dar mai verbose. `android:onClick` e acceptat
        // pentru demonstrații; Google îl consideră depășit pentru cod nou.

        // `AlertDialog.Builder` — construiește dialogul bucată cu bucată. Fiecare
        // setter întoarce ACELAȘI builder, de aceea se pot înlănțui. Lanțul se
        // încheie cu `setNegativeButton`, iar `builder.show()` de la finalul metodei
        // afișează dialogul.
        //
        // De ce funcționează lanțul: `setTitle`, `setMessage`, `setCancelable`,
        // `setPositiveButton`, `setNegativeButton` au toate `return this;` în
        // implementare. Nu e magie — e convenția „fluent builder".
        //
        // `SecondActivity.this` și nu `this`: în interiorul unui listener, `this` ar
        // însemna listener-ul. `SecondActivity.this` e sintaxa pentru instanța clasei
        // exterioare. Aici suntem încă în corpul metodei, deci `this` ar fi mers —
        // dar forma explicită e o obișnuință bună, pentru că în doi pași vei fi în
        // `onClick`.
        AlertDialog.Builder builder = new AlertDialog.Builder(SecondActivity.this);
        builder.setTitle("Add new control ...")
                .setMessage("Are you sure you want to add a new control?")

                // `setCancelable(true)` e valoarea implicită. Scrisă explicit,
                // documentează comportamentul: se poate închide cu Back sau cu tap în
                // afară. Consecința: dacă utilizatorul închide așa, NICIUN buton nu se
                // execută — nici „Do it!", nici „Cancel". Dacă ai nevoie de o acțiune
                // garantată, ai nevoie de `setOnCancelListener`.
                //
                // Cu `setCancelable(false)`, dialogul nu se mai poate închide decât
                // prin cele două butoane. Pentru o confirmare critică e alegerea
                // corectă; pentru una obișnuită, enervează utilizatorul.
                .setCancelable(true)

                // Butonul pozitiv e acțiunea principală — apare în dreapta, colorat.
                // Textul „Do it!" e explicit; „OK" ar fi vag.
                //
                // `which` e `DialogInterface.BUTTON_POSITIVE` aici. Nu e folosit —
                // fiecare buton are listener-ul lui. Dacă ai avea un singur listener
                // pentru toate butoanele, `which` ar fi singura modalitate de a distinge.
                //
                // De ce listener-ul e o clasă anonimă și nu un lambda:
                // `DialogInterface.OnClickListener` are o singură metodă abstractă,
                // deci ar merge și un lambda (`(dialog, which) -> { ... }`). Codul
                // alege forma veche, din generația Java 7. Ambele compilează; lambda
                // e mai scurt.
                .setPositiveButton("Do it!", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        // Creează butonul ÎNAINTE de Snackbar, ca să ai ce șterge.
                        // Id-ul returnat e SINGURA legătură cu butonul nou: nu ai o
                        // referință la obiect, doar un număr.
                        int id = addButton();

                        // `Snackbar.make(context, view, text, duration)` — patru argumente:
                        //   context  : SecondActivity.this — pentru temă și resurse
                        //   view     : inflatedLayout — view-ul de referință
                        //   text     : "Cancel previous action."
                        //   duration : Snackbar.LENGTH_LONG ≈ 2,75 s
                        //
                        // DE CE al doilea argument trebuie să fie un VIEW: `Snackbar`
                        // nu e o fereastră separată ca `Toast`-ul. E un view obișnuit,
                        // adăugat în arborele existent. Ca să știe unde să-l adauge,
                        // are nevoie de un punct de plecare: pornește de la view-ul dat
                        // și urcă prin părinți până găsește un `CoordinatorLayout` sau
                        // `android.R.id.content`. Fără un `View`, nu are de unde să
                        // pornească — de aceea nu există o suprascriere
                        // `make(Context, String, int)`.
                        //
                        // Ce se întâmplă exact cu `inflatedLayout`: e un `LinearLayout`
                        // simplu. `Snackbar` urcă de la el la `android.R.id.content`
                        // (containerul ferestrei) și își adaugă bara acolo. Rezultatul:
                        // bara apare jos, peste conținut.
                        //
                        // Ce ai câștiga cu un `CoordinatorLayout`: `SwipeDismissBehavior`
                        // (glisezi ca să închizi) și coordonarea cu un
                        // `FloatingActionButton` (FAB-ul se mută în sus cât timp
                        // Snackbar-ul e vizibil). Aici nu există FAB, deci diferența e
                        // doar glisarea.
                        Snackbar.make(SecondActivity.this, inflatedLayout, "Cancel previous action.", Snackbar.LENGTH_LONG)

                                // `setAction("Cancel", listener)` — adaugă butonul din
                                // dreapta. Textul e scurt cu intenție: un „Undo last
                                // action" ar înghesui mesajul pe ecrane mici.
                                //
                                // Textul și eticheta sunt ambele „Cancel" — o alegere
                                // nefericită de nume. Mesajul „Cancel previous action."
                                // spune ce s-a întâmplat; butonul „Cancel" ar trebui să
                                // fie „Undo", pentru că ANULEAZĂ adăugarea, nu anulează
                                // Snackbar-ul. Funcțional, butonul șterge butonul adăugat.
                                .setAction("Cancel", new View.OnClickListener() {
                                    @Override
                                    public void onClick(View v) {
                                        // `id` e capturat din lambda exterioară. E o
                                        // variabilă locală `int`, atribuită o singură
                                        // dată → effectively final → poate fi prinsă.
                                        // Dacă ai scrie `id++` între declarație și
                                        // folosire, compilatorul ar refuza captura.
                                        //
                                        // `inflatedLayout.findViewById(id)` — funcționează
                                        // pentru că butonul a primit un id explicit cu
                                        // `setId(counter)`. Fără `setId`, `findViewById`
                                        // ar returna `null` și `removeView(null)` ar
                                        // arunca `NullPointerException`.
                                        Button viewById = inflatedLayout.findViewById(id);

                                        // `removeView(viewById)` — scoate view-ul din
                                        // container. Butonul dispare de pe ecran; obiectul
                                        // rămâne în memorie până la următoarea colectare
                                        // de gunoi.
                                        inflatedLayout.removeView(viewById);
                                    }
                                }).show();
                        // `.show()` la final — fără el, Snackbar-ul e construit și
                        // niciodată afișat. Aceeași capcană ca la `Toast`.
                        //
                        // Momentul afișării: Snackbar-ul e creat ÎN `onClick`-ul
                        // butonului pozitiv, deci apare după ce dialogul s-a închis.
                        // Dacă l-ai crea înainte de `builder.show()`, ar apărea sub
                        // dialog.
                        //
                        // Durata `LENGTH_LONG`: ~2,75 secunde (valorile din
                        // `SnackbarManager`: 1 500 ms pentru `SHORT`, 2 750 ms pentru
                        // `LONG`). Suficient ca utilizatorul să apese „Cancel".
                        // `LENGTH_INDEFINITE` ar ține bara până la o acțiune sau un
                        // swipe — prea agresiv pentru o confirmare.

                    }
                })

                // Butonul negativ — anulare. Doar un `Toast`, nicio modificare de stare.
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        Toast.makeText(SecondActivity.this, "Object creation cancelled", Toast.LENGTH_LONG).show();
                    }
                });

        // `builder.show()` — creează dialogul și îl afișează. Echivalent cu
        // `builder.create().show()`. Se apelează O SINGURĂ DATĂ, după ce lanțul de
        // settere s-a încheiat.
        //
        // De ce `show()` e separat și nu în lanț: pentru că lanțul se termină cu `;`
        // după `setNegativeButton`, iar `show()` e o metodă a builder-ului, nu un
        // setter. Ar fi mers și `builder.setTitle(...).show()`, dar codul alege forma
        // explicită.
        //
        // Ce se întâmplă dacă apelezi `show()` de două ori: se creează două dialoguri,
        // ambele afișate. Al doilea apare peste primul. Nu e o excepție — doar un bug
        // vizual.
        //
        // Ce se întâmplă dacă apelezi un setter după `show()`: nu are efect asupra
        // dialogului afișat. Builder-ul copiază valorile în dialog la `create()`;
        // după aceea, setterele modifică doar builder-ul, nu dialogul viu.
        builder.show();
    }


    // ==================================================================================
    // CÂMP: counter
    // ==================================================================================
    // DECLARAT ÎNTRE METODE — legal în Java, neobișnuit ca stil.
    // DOUĂ ROLURI SIMULTAN: generator de id-uri și sursă pentru etichetă.
    // DE CE NU `static`: ar fi împărțit între instanțe. La recreare, activitatea nouă
    //   ar continua de la valoarea veche — id-uri care nu se repetă, dar și un contor
    //   care crește la infinit. Aici `counter` e per instanță, deci se resetează la
    //   rotire.
    // ==================================================================================
    int counter = 0;

    /*
     * ----------------------------------------------------------------------------------
     * METHOD: addButton()
     * ----------------------------------------------------------------------------------
     * THEORY:
     *   Un view construit din cod e un obiect Java obișnuit până când îl adaugi într-un
     *   părinte. Are nevoie de trei lucruri ca să fie util:
     *     1. un CONTEXT TEMATIZAT (constructorul);
     *     2. un ID (ca să poată fi regăsit);
     *     3. LayoutParams (ca părintele să știe cum să-l măsoare).
     *
     * LOGIC:
     *   1. Calculează 50dp în pixeli (rezultatul e ignorat — cod mort).
     *   2. Creează `new Button(SecondActivity.this)`.
     *   3. Setează textul cu pre-increment: „Button_1", „Button_2", ...
     *   4. Setează id-ul = counter (1, 2, 3, ...).
     *   5. Creează `ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)`.
     *   6. `addView(newBtn)` — îl adaugă la sfârșitul `LinearLayout`-ului.
     *   7. Întoarce id-ul, ca apelantul să poată șterge butonul.
     *
     * REF:
     *   cap. 14 (secțiunea despre view-uri dinamice), documentația `View#setId`,
     *   `ViewGroup.LayoutParams`, `ViewGroup#addView`.
     *
     * RISK:
     *   - context de aplicație în loc de activitate → pierzi tema;
     *   - `setId` uitat → butonul nu poate fi găsit și șters;
     *   - `counter` nu se salvează → la rotire butoanele dispar și id-urile se repetă.
     * ----------------------------------------------------------------------------------
     */
    public int addButton()
    {
        // COD MORT. `hPixels` e calculat și NICIODATĂ folosit. Intenția era probabil
        // `newBtn.setHeight(hPixels)` sau un `LayoutParams` cu înălțime de 50dp.
        // Compilatorul dă un warning (`variable hPixels is never used`), nu o eroare.
        //
        // Ce face totuși, util de știut: `TypedValue.applyDimension(COMPLEX_UNIT_DIP,
        // 50, metrics)` convertește 50dp în pixeli fizici, folosind densitatea
        // ecranului. La 3x, întoarce 150. E conversia corectă atunci când ai nevoie de
        // pixeli într-un calcul — de exemplu pentru animații sau pentru `setPadding`.
        //
        // De ce nu `50 * getResources().getDisplayMetrics().density`: e echivalent,
        // dar `applyDimension` tratează și `SP`, `PT`, `MM`, `IN` cu aceeași
        // semnătură. O funcție, toate unitățile.
        //
        // De ce `DisplayMetrics` se obține o singură dată:
        // `getResources().getDisplayMetrics()` întoarce obiectul configurației
        // curente. Apelat de mai multe ori, întoarce același obiect. Nu e o operație
        // scumpă, dar e inutil să o repeți.
        DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
        int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50,
                displayMetrics);

        // `new Button(Context)` — constructorul cere un CONTEXT TEMATIZAT.
        // `SecondActivity.this` are tema `Theme.DMA03`. Dacă ai pasa
        // `getApplicationContext()`, butonul ar pierde tema și, pe unele atribute
        // Material, ar arunca excepție la inflate.
        //
        // De ce `new Button(ctx)` și nu `LayoutInflater.from(ctx).inflate(...)`:
        // pentru un buton simplu, constructorul e mai direct. Inflater-ul are sens
        // când vrei un layout XML întreg, cu stiluri și copii.
        Button newBtn = new Button(SecondActivity.this);

        // `++counter` (pre-increment) — întâi incrementează, apoi folosește. Primul
        // buton e `Button_1`, iar `counter` devine 1. Cu `counter++` (post-increment),
        // primul ar fi `Button_0` și ai avea un buton cu id 0.
        newBtn.setText("Button_" + (++counter));

        // `setId(counter)` — id-uri 1, 2, 3... Id-urile de resursă sunt în zona
        // `0x7f......`, deci nu se ciocnesc. `View.NO_ID` e `-1`, deci 0 ar fi fost
        // o valoare nefericită — încă un motiv pentru pre-increment.
        //
        // FĂRĂ `setId`, butonul există dar e imposibil de găsit cu `findViewById`.
        // Ar apărea pe ecran și nu l-ai mai putea șterge.
        //
        // De ce id-urile mici sunt sigure: `findViewById` caută după valoarea
        // întreagă. Un id de 1 nu se ciocnește cu `R.id.button` (care e `0x7f0b....`).
        // Singura cerință e să fie unic în subarborele în care cauți.
        //
        // ALTERNATIVA MODERNĂ: `View.generateViewId()` întoarce un id unic, garantat.
        // Ar fi mai sigur dacă ai avea mai multe surse de id-uri. Aici `counter` e
        // suficient.
        newBtn.setId(counter);

        // `ViewGroup.LayoutParams` — clasa de bază. `LinearLayout` o acceptă. Dacă ai
        // nevoie de `layout_weight`, trebuie `LinearLayout.LayoutParams` — clasa de
        // bază nu are acel câmp.
        //
        // `MATCH_PARENT` pe lățime — butonul umple containerul, ca butonul original
        // din XML. `WRAP_CONTENT` pe înălțime — cât are nevoie textul.
        //
        // Ce înseamnă cele două constante: `MATCH_PARENT` = `-1` (umple părintele),
        // `WRAP_CONTENT` = `-2` (cât conținutul). Sunt valori negative intenționat,
        // ca să nu se confunde cu dimensiuni reale în pixeli.
        //
        // FĂRĂ `setLayoutParams`, `addView` aplică valorile implicite ale
        // containerului — tot `MATCH_PARENT`/`WRAP_CONTENT` pentru `LinearLayout`,
        // deci practic același rezultat. Explicit e mai sigur când containerul se
        // schimbă.
        //
        // Ce se întâmplă dacă pasezi `LinearLayout.LayoutParams`: funcționează și mai
        // bine — părintele nu mai trebuie să convertească.
        // `ViewGroup.LayoutParams` e acceptat pentru că
        // `LinearLayout.generateLayoutParams(ViewGroup.LayoutParams)` știe să-l
        // împacheteze.
        ViewGroup.LayoutParams layoutParams =
                new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT);
        newBtn.setLayoutParams(layoutParams);

        // `addView` — adaugă la sfârșitul `LinearLayout`-ului vertical, deci sub
        // butonul existent. Al doilea buton apare sub primul, al treilea sub al doilea.
        //
        // `addView` are două efecte: atașează view-ul la arbore și declanșează o
        // cerere de layout (`requestLayout`). Butonul apare imediat, fără să mai faci
        // nimic.
        inflatedLayout.addView(newBtn);

        // `return counter` — id-ul tocmai atribuit. Apelantul îl păstrează în `id` și
        // îl folosește în acțiunea Snackbar-ului.
        //
        // Ce se întâmplă la rotire: `counter` se resetează la 0, iar butoanele
        // adăugate dispar — nu sunt salvate în `savedInstanceState`. La rotire,
        // activitatea e recreată, `onCreate` rulează din nou, iar
        // `activity_second.xml` are din nou un singur buton.
        //
        // De ce se resetează și id-urile: dacă ai adăuga din nou butoane după rotire,
        // primul ar primi iar id-ul 1. Nu se ciocnește cu nimic, pentru că butoanele
        // vechi au dispărut odată cu arborele.
        return counter;
    }
}
```

**Ce reții din fișierul ăsta:** `android:onClick` cere `public void btnClick(View)`; `AlertDialog.Builder` se înlănțuie, iar `show()` e obligatoriu; `Snackbar.make` cere un `View` pentru că se inserează în arbore; un view creat din cod are nevoie de context tematizat, `setId` și `LayoutParams`; `SecondActivity` nu e pornită nicăieri.

---

## 26.3 `AndroidManifest.xml`

Fișierul care declară aplicația și cele două activități. Fără intrarea din manifest, o activitate nu există pentru sistem — chiar dacă fișierul `.java` compilează.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FIȘIER: AndroidManifest.xml
  ======================================================================================
  ROL:
    Declară aplicația și cele două activități. Fără intrarea din manifest, o
    activitate nu există pentru sistem — chiar dacă fișierul .java compilează.

  CE DEMONSTREAZĂ:
    1. `android:exported` — cine poate porni activitatea.
    2. `intent-filter` MAIN + LAUNCHER — cine apare în lansator.
    3. `android:supportsRtl` — de ce `layout_gravity="start"` se oglindește.

  REF: cap. 01 (setup și schelet), documentația `<manifest>`, `<activity>`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <manifest>
  ======================================================================================
  `xmlns:android` — namespace-ul atributelor de platformă. Fără el, `android:name`
    nu e recunoscut.
  `xmlns:tools` — namespace-ul atributelor de design-time. DECLARAT, DAR NEFOLOSIT:
    niciun atribut `tools:*` în fișier. Rămășiță din șablon. Nu strică, dar lint-ul
    îl semnalează.
  FĂRĂ `<uses-permission>` — aplicația nu are nevoie de nimic. Nici internet, nici
    stocare. Toate datele sunt în memorie.
  ======================================================================================
-->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!--
      ==================================================================================
      ELEMENT: <application>
      ==================================================================================
      Un singur element per aplicație. Toate activitățile, serviciile și receiver-ele
      sunt copii ai lui.

      ATRIBUTE:
      `allowBackup="true"` — aplicația participă la backup-ul automat al sistemului.
        Pentru o aplicație fără date persistente, e irelevant.
      `dataExtractionRules` (API 31+) și `fullBackupContent` (sub API 31) — fișiere
        care spun ce se salvează. Ambele trimit la `res/xml/`. Dacă lipsește unul,
        build-ul trece, dar lint-ul avertizează.
      `icon` și `roundIcon` — două resurse diferite pentru lansator: iconița pătrată
        și cea rotundă. Unele lansatoare folosesc forma rotundă, altele o maschează
        pe cea pătrată.
      `label="@string/app_name"` — numele aplicației, din `strings.xml` (`DMA03`).
        Nu e text literal, deci se poate traduce.
      `supportsRtl="true"` — interfața se oglindește în limbile RTL. De aici
        importanța `GravityCompat.START` în loc de `Gravity.LEFT`. Fără acest
        atribut, `start` s-ar comporta ca `left` chiar și în arabă.
      `theme="@style/Theme.DMA03"` — tema se aplică TUTUROR activităților care nu au
        `android:theme` propriu. Ambele o moștenesc. Lanțul e `Theme.DMA03` →
        `Base.Theme.DMA03` → `Theme.Material3.DayNight.NoActionBar`.

      DE CE `NoActionBar` ÎN NUMELE TEMEI: aplicația își desenează singură bara, cu
        `MaterialToolbar`. Dacă tema ar avea `ActionBar`, ai vedea două bare
        suprapuse — una a sistemului, una a ta.
      ==================================================================================
    -->
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA03">

        <!--
          ==============================================================================
          ELEMENT: <activity> MainActivity
          ==============================================================================
          `.MainActivity` — punctul de la început înseamnă „în pachetul aplicației",
            adică `ro.ase.ie.dma03.MainActivity`. Forma completă ar fi identică.
          `exported="true"` — obligatoriu pentru componenta cu `intent-filter` de la
            API 31 încoace. Fără el, build-ul EȘUEAZĂ. E singura activitate care
            poate fi pornită din afară — de lansator.
          `windowSoftInputMode="adjustResize"` — când apare tastatura, fereastra se
            micșorează, nu se panoramează. Aici nu există niciun `EditText`, deci
            atributul e inutil — dar e inofensiv și pregătește terenul pentru un
            ecran cu câmpuri.
          `adjustResize` vs `adjustPan`: `adjustResize` micșorează fereastra și lasă
            conținutul să se rearanjeze; `adjustPan` mută fereastra în sus ca să țină
            câmpul vizibil. Pentru formulare, `adjustResize` e aproape mereu alegerea
            corectă.
          ==============================================================================
        -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">

            <!--
              ==========================================================================
              ELEMENT: <intent-filter> MAIN + LAUNCHER
              ==========================================================================
              Perechea care creează iconița în lansator.
              `MAIN` = punctul de intrare; `LAUNCHER` = apare în lista de aplicații.
              Ambele sunt necesare.
              Doar `MAIN`: aplicația nu apare în lansator, dar poate fi pornită
                explicit cu `Intent`.
              Doar `LAUNCHER`: nu e recunoscută ca punct de intrare, deci tot nu apare.
              ==========================================================================
            -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!--
          ==============================================================================
          ELEMENT: <activity> SecondActivity
          ==============================================================================
          `exported="false"` — nicio aplicație din afară nu o poate porni. Corect: e
            un ecran intern.
          FĂRĂ `intent-filter` — nu are punct de intrare. Nu apare în lansator.

          AICI E DOVADA FINALĂ: `SecondActivity` e declarată, dar NIMIC nu o pornește.
            `MainActivity` nu conține niciun `Intent`. Ecranul e un laborator lăsat
            nelegat — cod complet, accesibil doar dacă îl lansezi manual din Android
            Studio.

          CE AR FI TREBUIT PENTRU A O LEGA: în `MainActivity`, un
            `startActivity(new Intent(this, SecondActivity.class))` — de exemplu în
            ramura `nav_settings` sau pe `action_open` din meniul contextual.
            Importul `android.content.Intent` există deja, semn că intenția a fost
            acolo.

          DE CE `exported="false"` NU ÎMPIEDICĂ LANSAREA MANUALĂ DIN IDE: Android
            Studio instalează aplicația în modul debug și pornește activitatea cu
            privilegiile de debug ale aplicației, nu ca o aplicație străină.
            Restricția `exported` se aplică altor aplicații, nu propriei aplicații.
          ==============================================================================
        -->
        <activity
            android:name=".SecondActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**Ce reții din fișierul ăsta:** `exported="true"` + `MAIN`/`LAUNCHER` = ecranul de start; `SecondActivity` e declarată, dar nelegată; `supportsRtl="true"` e motivul pentru care `start` se oglindește.

---

## 26.4 `activity_main.xml` — ierarhia de containere

Șase containere imbricate, fiecare cu o singură responsabilitate. Blocul de mai jos e fișierul întreg, în ordinea din sursă.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FIȘIER: activity_main.xml
  ======================================================================================
  ROL:
    Construiește ecranul principal din șase containere imbricate. Fiecare are o
    singură responsabilitate; împreună produc efectul de drawer + app bar + listă.

  CE DEMONSTREAZĂ:
    1. DrawerLayout cu exact doi copii: conținut + sertar.
    2. CoordinatorLayout care coordonează AppBarLayout cu lista.
    3. MaterialToolbar cu titlu, hamburger și meniu.
    4. NavigationView cu `layout_gravity="start"` (RTL-safe).

  REF: cap. 14 (secțiunea 14.1), documentația `DrawerLayout`, `CoordinatorLayout`,
       `AppBarLayout`, `NavigationView`.
  ======================================================================================
-->

<!--
  ======================================================================================
  THEORY BLOCK: CUM SE DESENEAZĂ UN ECRAN ANDROID
  ======================================================================================
  1. ARBORELE DE VIEW-URI
     Fiecare ecran e un arbore: un `ViewGroup` rădăcină cu copii, care pot fi la
     rândul lor `ViewGroup`-uri.
     `View` = ceva ce se desenează (text, imagine, buton).
     `ViewGroup` = ceva ce conține alte view-uri și le poziționează.

  2. CELE TREI FAZE
     MEASURE: fiecare view își calculează dimensiunea dorită, în funcție de
       `LayoutParams` și de spațiul oferit de părinte.
     LAYOUT: părintele decide poziția (left, top) fiecărui copil.
     DRAW: fiecare view se desenează pe canvas.
     Cele trei faze se repetă la fiecare `requestLayout()` — de exemplu când adaugi
     un buton cu `addView`.

  3. `match_parent` vs `wrap_content`
     `match_parent` (`-1`): „umple tot spațiul părintelui".
     `wrap_content` (`-2`): „cât am nevoie ca să-mi arăt conținutul".
     Sunt valori speciale, nu dimensiuni în pixeli.

  4. DE CE CONTAINERELE SUNT IMBRICATE
     Fiecare `ViewGroup` adaugă O SINGURĂ comportare:
       DrawerLayout      → glisare laterală;
       CoordinatorLayout → coordonare între copii (app bar + scroll);
       AppBarLayout      → colaps la scroll;
       FrameLayout       → suprapunere simplă, fără poziționare;
       LinearLayout      → stivuire.
     Un singur container nu poate face toate comportamentele. Le compui.

  5. DE CE `FrameLayout` ÎNTRE `CoordinatorLayout` ȘI `ListView`
     `CoordinatorLayout` aplică un `Behavior` pe COPILUL DIRECT.
     `ListView` ar putea fi el însuși copilul direct, dar `FrameLayout`-ul izolează
     comportamentul și lasă loc pentru un FAB sau un `TextView` de „listă goală" în
     viitor.

  REF: documentația `View`, `ViewGroup`, `View.MeasureSpec`, `CoordinatorLayout`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ARBORELE, PE NIVELURI — ȘI RESPONSABILITATEA FIECĂRUIA
  ======================================================================================
  DrawerLayout (id=drawerLayout)          ← știe să gliseze un panou peste conținut;
  │                                          NU desenează nimic propriu-zis;
  │                                          ține evidența stării „deschis/închis"
  ├── CoordinatorLayout (id=main)         ← panoul de conținut (primul copil);
  │   │                                      coordonează comportamentele copiilor
  │   ├── AppBarLayout                    ← ține bara; știe să se ridice la scroll
  │   │   └── MaterialToolbar (topAppBar) ← titlu, hamburger, meniu, click-uri
  │   │
  │   └── FrameLayout                     ← suport pentru `layout_behavior`;
  │       │                                  izolează lista de CoordinatorLayout
  │       └── ListView (listView)         ← 20 rânduri din @array/items;
  │                                          primește apăsarea lungă
  │
  └── NavigationView (navigationView)     ← sertarul: meniu + iconițe + insets
                                             proprii; glisează din `start`

  TABELUL RESPONSABILITĂȚILOR:
  Nivel 1  DrawerLayout        glisează sertarul peste conținut
  Nivel 2  CoordinatorLayout   coordonează AppBarLayout cu lista
  Nivel 3  AppBarLayout        ține bara și aplică liftOnScroll
  Nivel 4  MaterialToolbar     titlu, hamburger, meniu
  Nivel 5  FrameLayout         aplică layout_behavior pe listă
  Nivel 6  ListView            afișează rândurile

  CE SE STRICĂ DACĂ LIPSEȘTE UN NIVEL:
  DrawerLayout     → nu există sertar;
  CoordinatorLayout → bara nu reacționează la scroll;
  AppBarLayout     → bara nu se ridică, nu se colapsează;
  MaterialToolbar  → ecranul nu are bară;
  FrameLayout      → lista se desenează sub bară;
  ListView         → ecranul e gol.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: DrawerLayout (rădăcina)
  ======================================================================================
  `@+id/drawerLayout` — semnul `+` înseamnă „creează id-ul dacă nu există". Prima
    apariție într-un fișier XML trebuie să aibă `+`; în cod se folosește
    `R.id.drawerLayout` fără.
  `match_parent` x 2 — containerul acoperă tot ecranul, inclusiv zonele de sub bare.
    `EdgeToEdge` are sens doar așa: conținutul se întinde, iar padding-ul de insets
    îl ține în zona sigură.
  `xmlns:app` — namespace-ul pentru atributele definite de biblioteci (`app:menu`,
    `app:title`). Fără el, `app:menu` nu e recunoscut.

  DE CE `DrawerLayout` E RĂDĂCINA ȘI NU `CoordinatorLayout`: pentru că sertarul
    trebuie să acopere TOT ecranul, inclusiv bara. Dacă `DrawerLayout` ar fi copil
    al `CoordinatorLayout`, sertarul ar fi împins de bară și ar porni de sub ea.
  ======================================================================================
-->
<androidx.drawerlayout.widget.DrawerLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/drawerLayout"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

<!--
  ======================================================================================
  REGULA `DrawerLayout`: EXACT DOI COPII
  ======================================================================================
  REGULA CANONICĂ: exact DOI copii direcți.
    1. PRIMUL copil — conținutul. Orice `ViewGroup`; aici `CoordinatorLayout`.
       Umple tot spațiul.
    2. AL DOILEA copil — sertarul. Aici `NavigationView`. Trebuie să aibă
       `android:layout_gravity="start"` (sau `end`).

  CE ÎNSEAMNĂ „EXACT" TEHNIC: `DrawerLayout` acceptă mai mulți copii, dar
    contractul e: UN conținut + CEL MULT un sertar pe fiecare margine. Poți avea un
    sertar `start` și unul `end` simultan. Nu poți avea doi pe aceeași margine —
    `IllegalStateException` la inflate: „Child drawer has absolute gravity ... but
    this DrawerLayout already has a drawer view along that edge".

  CUM DECIDE `DrawerLayout` CINE E SERTAR: după `android:layout_gravity`. Un copil
    fără gravity (sau cu `top`/`bottom`) e tratat ca CONȚINUT și desenat peste
    ceilalți, pe tot ecranul. De aceea `NavigationView` fără `layout_gravity` ar
    acoperi ecranul și nu s-ar deschide niciodată.

  DE CE ORDINEA CONTEAZĂ: primul copil e conținutul prin contract și prin ordinea
    de desenare. Copiii se desenează în ordinea din XML, deci sertarul (al doilea)
    se desenează peste conținut. Dacă ai pune sertarul primul, ar fi desenat primul
    și conținutul l-ar acoperi — deși `DrawerLayout` l-ar trata tot ca sertar,
    pentru că are gravity.

  CE SE ÎNTÂMPLĂ DACĂ PUI UN AL TREILEA COPIL FĂRĂ GRAVITY: e tratat ca al doilea
    panou de conținut, desenat peste primul, pe tot ecranul. Build-ul trece; ecranul
    arată ca și cum conținutul ar fi fost înlocuit. Un bug greu de diagnosticat,
    pentru că XML-ul e valid.

  DE CE `DrawerLayout` NU E UN `ViewGroup` OBIȘNUIT: are logică proprie de
    interceptare a gesturilor (`onInterceptTouchEvent`), de măsurare a sertarului și
    de animație. De aceea nu poate fi înlocuit cu un `FrameLayout` + `TranslationX`
    scris de mână fără mult cod.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: CoordinatorLayout (panoul de conținut)
  ======================================================================================
  `xmlns:android` și `xmlns:app` sunt declarate DIN NOU — deși sunt deja pe
    `DrawerLayout`. Redundant, dar legal: namespace-urile se moștenesc, iar
    redeclararea e ignorată. Nu strică nimic; unii editori le adaugă automat.
  `@+id/main` — de aici vine `findViewById(R.id.main)` din cod, pentru insets.
    Id-ul e pe CONȚINUT, nu pe `DrawerLayout` — deci padding-ul de insets nu atinge
    sertarul.
  `match_parent` x 2 — conținutul umple spațiul rămas după ce `DrawerLayout` îl
    măsoară. Practic, tot ecranul.

  DE CE `CoordinatorLayout` ȘI NU DIRECT `FrameLayout`: coordonează `AppBarLayout`
    cu lista — efectul de `liftOnScroll` are nevoie de el. Fără `CoordinatorLayout`,
    bara nu știe când lista se derulează.

  CE FACE CONCRET: ține un `Behavior` pentru fiecare copil direct. `AppBarLayout`
    are un `Behavior` care ascultă scroll-ul; `FrameLayout`-ul cu
    `app:layout_behavior="@string/appbar_scrolling_view_behavior"` are unul care se
    împinge în jos cu înălțimea barei. Fără coordinator, cele două nu comunică.
  ======================================================================================
-->
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!--
      ================================================================================
      ELEMENT: AppBarLayout (bara de sus)
      ================================================================================
      Un `LinearLayout` vertical cu un singur scop: să țină bara și să-i aplice
      comportamentele de scroll. Nu e obligatoriu să conțină doar un toolbar; poate
      conține și un `TabLayout`.

      ATRIBUTE:
      `wrap_content` pe înălțime — bara are înălțimea copilului
        (`?attr/actionBarSize`). `match_parent` ar întinde-o pe tot ecranul.
      `#6750A4` — movul de bază Material 3, HARDCODAT. Nu se adaptează la dark mode:
        în întuneric bara rămâne mov deschis. Corect ar fi `?attr/colorPrimary`.
      `liftOnScroll="true"` — când lista se derulează, bara își schimbă culoarea în
        `liftOnScrollColor` (#4F378B, tot hardcodat) și primește o umbră. E efectul
        „app bar care se ridică".
      `liftOnScrollColor` — culoarea de destinație a tranziției. Fără ea, tranziția
        ar folosi o culoare derivată din temă.
      `liftOnScrollTargetViewId="@id/listView"` — îi spune lui `AppBarLayout` CARE
        view derulează. Fără el, `AppBarLayout` încearcă să detecteze singur view-ul
        derulabil; când view-ul e imbricat (aici `ListView`-ul e în `FrameLayout`),
        detectarea poate alege alt view sau poate produce flicker. Id-ul explicit
        elimină ambiguitatea — e recomandarea din documentația Material pentru
        view-uri derulabile imbricate.
      `@id/listView` și nu `@+id/listView`: id-ul e deja creat de `ListView`, care
        apare mai jos în același fișier. `@+id` ar crea un id nou, iar referința ar
        arăta spre altceva (sau ar da eroare de duplicat).

      CUM FUNCȚIONEAZĂ „LIFT ON SCROLL" PE SCURT: `AppBarLayout` ascultă evenimentele
        de scroll ale view-ului țintă. Când primește un scroll în jos, animă fundalul
        spre `liftOnScrollColor` și adaugă o umbră; când ajunge sus, revine. E o
        tranziție de culoare, nu o schimbare de înălțime.
      ================================================================================
    -->
    <com.google.android.material.appbar.AppBarLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#6750A4"
        app:liftOnScroll="true"
        app:liftOnScrollColor="#4F378B"
        app:liftOnScrollTargetViewId="@id/listView">

        <!--
          ==============================================================================
          ELEMENT: MaterialToolbar
          ==============================================================================
          `?attr/actionBarSize` — înălțimea standard a barei (56dp). Nu hardcoda
            `56dp`: pe unele teme și orientări diferă.
          `android:background="@android:color/transparent"` — toolbar-ul e
            transparent, culoarea vine de la `AppBarLayout`. Altfel ai două straturi
            de mov, iar `liftOnScroll` ar schimba doar unul.
          `app:title="Inbox"` — titlul inițial. Codul îl suprascrie cu
            `toolbar.setTitle(...)` la click pe sertar.
          `app:titleTextColor` și `app:navigationIconTint` — alb. Fără ele, textul ar
            fi negru pe mov în light theme. `navigationIconTint` e necesar separat
            pentru că iconița vectorială are culoarea proprie (#000000 în
            `ic_menu.xml`).
          `app:navigationIcon="@drawable/ic_menu"` — cele trei linii. Desenul e un
            `VectorDrawable` de 24dp; culoarea reală o dă `navigationIconTint`.
          `app:menu="@menu/top_app_bar"` — umflă meniul direct din XML. De aceea
            `onCreate` nu are `onCreateOptionsMenu`.
          `app:theme="@style/ThemeOverlay.Material3.Dark.ActionBar"` — aplică o temă
            întunecată DOAR pe toolbar, ca textul și iconițele să fie deschise.
            Alternativa ar fi fost să setezi fiecare culoare în parte.
          `app:theme` și nu `android:theme`: `app:theme` e citit de `Toolbar` și
            aplicat doar subarborelui lui. `android:theme` ar schimba tema întregii
            ferestre.
          `app:` peste tot și nu `android:`: atributele `title`, `titleTextColor`,
            `navigationIcon`, `menu`, `layout_scrollFlags` sunt definite de biblioteci
            (AppCompat/Material), nu de platformă. Cu `android:` ar fi ignorate sau ar
            avea altă semnificație.

          `app:layout_scrollFlags="scroll|enterAlways|snap"` — comportamentul la
            derulare:
              scroll       → bara iese din ecran când derulezi în jos;
              enterAlways  → revine imediat ce derulezi în sus, oriunde ai fi în listă;
              snap         → se oprește complet vizibilă sau complet ascunsă, niciodată
                             pe jumătate.

          CE SE ÎNTÂMPLĂ DACĂ SCOȚI `app:menu`: bara rămâne fără
            Search/Share/Settings, iar `toolbar.setOnMenuItemClickListener` nu se mai
            apelează niciodată. Nu e eroare — doar un listener mort.
          CE SE ÎNTÂMPLĂ DACĂ SCOȚI `app:navigationIcon`: hamburger-ul dispare, iar
            `setNavigationOnClickListener` nu mai are ce apăsa. Sertarul rămâne
            accesibil doar prin gestul de glisare de la marginea ecranului.
          ==============================================================================
        -->
        <com.google.android.material.appbar.MaterialToolbar
            android:id="@+id/topAppBar"
            android:layout_width="match_parent"
            android:layout_height="?attr/actionBarSize"
            android:background="@android:color/transparent"
            app:title="Inbox"
            app:titleTextColor="@android:color/white"
            app:navigationIcon="@drawable/ic_menu"
            app:navigationIconTint="@android:color/white"
            app:menu="@menu/top_app_bar"
            app:layout_scrollFlags="scroll|enterAlways|snap"
            app:theme="@style/ThemeOverlay.Material3.Dark.ActionBar" />

    </com.google.android.material.appbar.AppBarLayout>

    <!--
      ================================================================================
      ELEMENT: FrameLayout + ListView
      ================================================================================
      `app:layout_behavior="@string/appbar_scrolling_view_behavior"` — fără el,
        `FrameLayout`-ul ar fi desenat de la `y=0`, adică SUB bară, iar primele
        rânduri ar fi acoperite. Comportamentul îl împinge în jos exact cu înălțimea
        barei.
      De ce e un string și nu o clasă: `app:layout_behavior` acceptă numele complet
        al clasei `Behavior`. `@string/appbar_scrolling_view_behavior` e un alias
        definit de Material pentru
        `com.google.android.material.appbar.AppBarLayout$ScrollingViewBehavior`. Așa
        nu depinzi de numele intern al clasei.

      `android:entries="@array/items"` — `ListView` își construiește singur un
        `ArrayAdapter` din cele 20 de șiruri din `strings.xml`. NU există niciun
        adapter în cod — de aceea `listView.getItemAtPosition(position)` întoarce
        direct un `String`.
      Ce face exact: în constructorul `ListView`, se citește atributul și se cheamă
        `setAdapter(new ArrayAdapter<>(context, android.R.layout.simple_list_item_1,
        entries))`. Layout-ul rândului e cel standard de platformă — un `TextView`.
      `android:nestedScrollingEnabled="true"` — permite listei să transmită
        evenimentele de derulare părintelui (`CoordinatorLayout`), ca `liftOnScroll`
        să funcționeze. Fără el, lista „înghite" derularea și bara nu reacționează.
      `match_parent` pe înălțime — lista umple tot spațiul rămas după bară.
        `wrap_content` ar fi lăsat-o să crească la infinit.

      DE CE `ListView` ȘI NU `RecyclerView` AICI: 20 de rânduri statice, fără
        animații, fără view-uri reciclate complicate. `ListView` e suficient și cere
        zero cod. `RecyclerView` ar fi cerut un adapter, un `ViewHolder` și un
        `LayoutManager` — subiectul capitolului 12.
      CE SE ÎNTÂMPLĂ DACĂ SCOȚI `FrameLayout`-UL: `ListView` ar primi
        `app:layout_behavior` și ar funcționa, dar ai pierde locul pentru un FAB sau
        un `TextView` de „listă goală". `FrameLayout`-ul e un strat de extensie, nu o
        necesitate tehnică.
      ================================================================================
    -->
    <!-- layout_behavior: spune CoordinatorLayout că acest view stă SUB app bar -->
    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_behavior="@string/appbar_scrolling_view_behavior">

        <ListView
            android:id="@+id/listView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:entries="@array/items"
            android:nestedScrollingEnabled="true" />
    </FrameLayout>

</androidx.coordinatorlayout.widget.CoordinatorLayout>

    <!--
      ================================================================================
      ELEMENT: NavigationView (sertarul)
      ================================================================================
      `layout_width="wrap_content"` — sertarul are lățimea conținutului, nu a
        ecranului. `match_parent` ar acoperi tot și nu ar mai părea sertar. Material
        recomandă ~280dp; `wrap_content` se apropie.
      `layout_height="match_parent"` — pe toată înălțimea.
      `android:layout_gravity="start"` — ATRIBUTUL CARE FACE DIFERENȚA. Fără el,
        `NavigationView` e tratat ca al doilea panou de conținut și nu se deschide
        niciodată. Trebuie să fie identic cu `GravityCompat.START` din cod.
      `app:menu="@menu/drawer_menu"` — conținutul sertarului vine din XML.
        `NavigationView` îl umflă singur; codul doar ascultă click-urile.
      `NavigationView` își aplică singură insets-urile — extinde
        `ScrimInsetsFrameLayout`, care adaugă padding pentru status bar. De aceea nu
        are nevoie de blocul de insets din cod.
      ================================================================================
    -->
    <com.google.android.material.navigation.NavigationView
        android:id="@+id/navigationView"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        app:menu="@menu/drawer_menu" />

</androidx.drawerlayout.widget.DrawerLayout>

<!--
  ======================================================================================
  `layout_gravity="start"` ȘI RTL
  ======================================================================================
  CE ÎNSEAMNĂ `start`: „începutul direcției de citire". În română, engleză, germană
  — stânga. În arabă, ebraică, persană — dreapta.

  CUM SE REZOLVĂ: `DrawerLayout` cheamă `Gravity.getAbsoluteGravity(gravity,
  layoutDirection)` și transformă `START` în `LEFT` sau `RIGHT`, în funcție de
  direcția de layout a view-ului. Rezultatul e folosit la măsurare și la poziționare.

  DE CE E NEVOIE DE `android:supportsRtl="true"` ÎN MANIFEST: fără el, aplicația nu
  primește direcție RTL de la sistem, iar `start` se comportă ca `left` chiar și în
  arabă. Cu el, întreaga interfață se oglindește: toolbar-ul, textul, sertarul.

  CE SE ÎNTÂMPLĂ ÎN COD DACĂ AMESTECI `START` ȘI `LEFT`:

  LTR (română):
    XML: layout_gravity="start"  → sertarul e în STÂNGA
    Cod: openDrawer(GravityCompat.START) → caută sertarul din START = STÂNGA → OK

  RTL (arabă):
    XML: layout_gravity="start"  → sertarul e în DREAPTA
    Cod: openDrawer(GravityCompat.START) → caută sertarul din START = DREAPTA → OK

  RTL cu cod greșit:
    XML: layout_gravity="start"  → sertarul e în DREAPTA
    Cod: openDrawer(Gravity.LEFT) → caută sertarul din STÂNGA → nu există → nimic

  REGULA: `layout_gravity` din XML și `GravityCompat.*` din cod trebuie să folosească
  aceeași constantă relativă (`start`/`end`). Niciodată `left`/`right` amestecat cu
  `start`/`end`.

  DE CE `GravityCompat` ȘI NU `Gravity`: `GravityCompat.START` e definit în
  biblioteca de compatibilitate și e egal cu `Gravity.START` pe API-urile care îl au.
  Pe API-uri vechi, `GravityCompat` face conversia. În practică, cu `minSdk 33`, ai
  putea folosi și `Gravity.START` — dar `GravityCompat` e convenția și nu costă nimic.

  CE SE ÎNTÂMPLĂ CU `layout_gravity="end"`: sertarul vine din dreapta în LTR și din
  stânga în RTL. Util pentru un al doilea sertar (de exemplu setări). Codul ar trebui
  să folosească `GravityCompat.END` pentru el.

  DE CE `NavigationView` NU ARE `layout_gravity` IMPLICIT: pentru că `DrawerLayout`
  nu poate ghici ce margine vrei. Fără gravity, copilul e tratat ca conținut — și
  ecranul arată ca și cum sertarul ar fi fost lipit peste listă.
  ======================================================================================
-->
```

**Ce reții din fișierul ăsta:** `DrawerLayout` are exact doi copii, iar rolul fiecăruia e dat de `layout_gravity`; `id=main` e pe conținut, nu pe drawer; `CoordinatorLayout` + `AppBarLayout` + `layout_behavior` produc efectul de bară care se ridică; `NavigationView` își aplică singură insets-urile.

---

## 26.5 `activity_second.xml`

Layout-ul ecranului de laborator: un singur `LinearLayout` vertical cu un singur `Button`, legat de cod prin `android:onClick`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FIȘIER: activity_second.xml
  ======================================================================================
  ROL:
    Layout-ul ecranului de laborator. Un singur `LinearLayout` vertical cu un
    singur `Button`, legat de cod prin `android:onClick`.

  CE DEMONSTREAZĂ:
    1. `android:onClick` — legătura XML → metodă, prin reflecție.
    2. `LinearLayout` vertical — containerul în care se adaugă butoane din cod.
    3. `tools:context` — atribut care există doar pentru preview-ul din IDE.

  REF: cap. 14 (secțiunea despre dialoguri), documentația `android:onClick`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: LinearLayout (rădăcina)
  ======================================================================================
  `LinearLayout` vertical — copiii se stivuiesc de sus în jos. De asta butoanele
    adăugate din cod apar unul sub altul, nu peste.
  `android:orientation="vertical"` — obligatoriu pentru stivuirea pe verticală.
    Valoarea implicită este `horizontal`, deci fără atribut butoanele ar sta unul
    lângă altul.
  `android:id="@+id/main"` — folosit de două ori în cod: pentru insets și pentru
    `inflatedLayout`. Id-ul se repetă față de `activity_main.xml`, dar nu e o
    problemă: cele două layout-uri nu coexistă niciodată în același arbore.
  `xmlns:app` e declarat, dar NEFOLOSIT — niciun atribut `app:*` în fișier.
    Rămășiță din șablon, semnalată de lint.
  `xmlns:tools` — namespace-ul atributelor de design-time. Folosit o singură dată,
    pentru `tools:context`.
  `tools:context=".SecondActivity"` — doar pentru preview-ul din Android Studio: îi
    spune editorului ce temă și ce clasă să folosească. Eliminat la build, nu ajunge
    în APK. Fără el, preview-ul folosește tema aplicației și nu știe ce activitate
    să simuleze.
  ======================================================================================
-->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".SecondActivity">

    <!--
      ================================================================================
      ELEMENT: Button
      ================================================================================
      `android:onClick="btnClick"` — leagă butonul de metoda `btnClick(View)` din
        activitate, prin reflecție. NU există `setOnClickListener` în cod — toată
        legătura e aici.
      De ce funcționează fără cod: la click, Android caută metoda în contextul
        activității. Dacă nu o găsește, excepția apare LA RUNTIME, nu la compilare.
      Cum caută exact: `View.performClick()` cheamă `onClick`-ul setat; dacă nu
        există, `View` are un `DeclaredOnClickListener` creat la inflate, care ține
        numele metodei și contextul. La click, caută metoda cu reflecție, în context
        și în părinții lui.

      `android:id="@+id/button"` NU e folosit nicăieri — nici în cod, nici în alt
        XML. E util doar dacă vrei să-l referențiezi mai târziu. Butoanele create
        din cod primesc id-uri numerice (1, 2, 3...), nu id-uri de resursă.
      `match_parent` pe lățime — butonul umple ecranul. Butoanele adăugate din cod
        primesc același `MATCH_PARENT`, deci arată identic.
      `wrap_content` pe înălțime — cât are nevoie textul, plus padding-ul implicit
        al butonului Material.
      FĂRĂ `padding` pe `LinearLayout` — butoanele ating marginile ecranului.
        Cosmetic, nu funcțional.
      DE CE `Button` ȘI NU `MaterialButton`: `Button` e stilizat automat de tema
        Material3 (prin `buttonStyle` din temă), deci arată ca un `MaterialButton`.
        Diferența apare doar dacă vrei atribute specifice (`app:icon`,
        `app:cornerRadius`).
      CE SE ÎNTÂMPLĂ DACĂ ADAUGI `android:enabled="false"`: butonul nu mai primește
        click-uri, deci `btnClick` nu se mai apelează. Util pentru a bloca o acțiune
        până la o condiție.
      ================================================================================
    -->
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:onClick="btnClick"
        android:text="Button" />
</LinearLayout>
```

**Ce reții:** `android:onClick` e singura legătură dintre XML și `btnClick`; `LinearLayout` vertical e motivul pentru care butoanele adăugate apar unul sub altul.

---

## 26.6 Meniurile (`res/menu/*.xml`)

Trei fișiere, trei scopuri diferite. Toate sunt umflate din XML — niciunul nu e construit în cod. Fiecare fișier are propriul bloc, în ordinea din sursă.

### 26.6.1 `drawer_menu.xml` — conținutul sertarului

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FIȘIER: drawer_menu.xml
  ======================================================================================
  ROL:
    Conținutul sertarului: trei destinații de navigare + o setare separată.
    `NavigationView` îl umflă singur, prin `app:menu="@menu/drawer_menu"`.

  CE DEMONSTREAZĂ:
    1. `checkableBehavior="single"` — grup exclusiv, ca un radio group.
    2. `item` fără id, cu `menu` imbricat — subtitlu de secțiune.
    3. Id-urile `nav_*` — exact cele verificate în `MainActivity`.

  REF: cap. 14 (secțiunea despre meniuri), documentația `Menu`, `MenuItem`, `SubMenu`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <menu>
  ======================================================================================
  Rădăcina oricărui fișier de meniu. Conține `<group>` și `<item>`.
  ======================================================================================
-->
<menu xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- checkableBehavior="single" = radio group: un singur element bifat -->
    <!--
      ================================================================================
      ELEMENT: <group android:checkableBehavior="single">
      ================================================================================
      Grupul se comportă ca un radio group: când selectezi „Sent", „Inbox" se
      debifează automat. Valorile posibile:

        single → un singur element bifat per grup (radio);
        all    → fiecare element se poate bifa independent (checkbox);
        none   → niciun element nu e bifabil.

      `android:checked="true"` pe `nav_inbox` — starea inițială. Fără ea, la prima
      deschidere niciun element nu e bifat, deși toolbar-ul afișează „Inbox".
      `android:icon` — fiecare element are o iconiță vectorială din `res/drawable/`.
      `NavigationView` le afișează la stânga titlului.
      `android:title` e text literal, nu `@string/...` — funcționează, dar nu se
      traduce. Pentru o aplicație reală, toate titlurile ar trebui să fie în
      `strings.xml`.
      ================================================================================
    -->
    <group android:checkableBehavior="single">
        <item
            android:id="@+id/nav_inbox"
            android:icon="@drawable/ic_inbox"
            android:title="Inbox"
            android:checked="true" />
        <item
            android:id="@+id/nav_sent"
            android:icon="@drawable/ic_send"
            android:title="Sent" />
        <item
            android:id="@+id/nav_trash"
            android:icon="@drawable/ic_delete"
            android:title="Trash" />
    </group>

    <!--
      ================================================================================
      ELEMENT: <item android:title="Other"> cu <menu> imbricat
      ================================================================================
      Un `<item>` FĂRĂ id, care conține un `<menu>` — trucul pentru un SUBTITLU DE
      SECȚIUNE. „Other" apare ca etichetă gri, iar „Settings" dedesubt, separat de
      grupul principal.

      DE CE `nav_settings` E ÎN AFARA GRUPULUI: nu face parte din navigarea
      principală (Inbox/Sent/Trash), ci e o setare. Separarea vizuală sugerează
      diferența.
      CONSECINȚA ÎN COD: `nav_settings` nu e checkable, deci `item.setChecked(true)`
      nu are efect vizual pe el. Ramura lui afișează un `Toast`.
      CE SE ÎNTÂMPLĂ DACĂ PUI `nav_settings` ÎN ACELAȘI GRUP: ar deveni al patrulea
      radio button. La click, „Inbox" s-ar debifa și „Settings" ar rămâne bifat —
      deși nu e o destinație de navigare. Separarea nu e doar vizuală, e semantică.
      ================================================================================
    -->
    <item android:title="Other">
        <menu>
            <item
                android:id="@+id/nav_settings"
                android:icon="@drawable/ic_settings"
                android:title="Settings" />
        </menu>
    </item>
</menu>
```

### 26.6.2 `list_item_menu.xml` — meniul contextual

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FIȘIER: list_item_menu.xml
  ======================================================================================
  ROL:
    Meniul contextual de pe un rând: Open / Rename / Delete. Umflat de `PopupMenu`
    în `MainActivity`, la apăsarea lungă.

  CE DEMONSTREAZĂ:
    1. Un meniu minimal, fără iconițe și fără `showAsAction`.
    2. Id-urile `action_*` — exact cele verificate în cod.

  REF: cap. 14 (secțiunea despre meniuri), documentația `PopupMenu`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <menu> cu trei <item>
  ======================================================================================
  MINIMALISM DELIBERAT: fără iconițe, fără `showAsAction`. Un `PopupMenu` nu are
    bară — toate elementele apar în listă, deci `showAsAction` ar fi ignorat.

  CELE TREI ID-URI SUNT EXACT CELE VERIFICATE ÎN `MainActivity`: `action_open`,
    `action_rename`, `action_delete`. Dacă redenumești unul în XML fără să modifici
    codul, ramura respectivă nu se mai execută — și nu primești eroare de compilare,
    doar un `if` care nu mai intră niciodată.

  FĂRĂ `android:icon` — un meniu contextual scurt se citește mai repede fără
    iconițe. Cu iconițe, `PopupMenu` le afișează, dar ocupă mai mult spațiu.

  ORDINEA ELEMENTELOR = ORDINEA DIN MENIU. `Open`, `Rename`, `Delete` apar de sus în
    jos. Dacă vrei `Delete` ultimul (ca acțiune distructivă), ordinea asta e deja
    corectă.

  DE CE `Delete` NU ARE UN STIL ROȘU: meniurile Android nu au un atribut standard
    pentru „element periculos". Ai putea seta un `SpannableString` cu culoare în cod,
    dar nu e o practică răspândită.
  ======================================================================================
-->
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/action_open"
        android:title="Open" />
    <item
        android:id="@+id/action_rename"
        android:title="Rename" />
    <item
        android:id="@+id/action_delete"
        android:title="Delete" />
</menu>
```

### 26.6.3 `top_app_bar.xml` — meniul barei

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--
  ======================================================================================
  FIȘIER: top_app_bar.xml
  ======================================================================================
  ROL:
    Meniul barei de sus: Search, Share și Settings. Umflat de `MaterialToolbar`
    prin `app:menu="@menu/top_app_bar"`.

  CE DEMONSTREAZĂ:
    1. `app:showAsAction` — toate valorile și efectul lor la runtime.
    2. `app:` vs `android:` — de ce namespace-ul contează.
    3. Overflow-ul — unde ajung elementele care nu încap.

  REF: cap. 14 (secțiunea despre meniuri), documentația `Menu`, `MenuItem`,
       `android:showAsAction`.
  ======================================================================================
-->

<!--
  ======================================================================================
  ELEMENT: <menu> cu xmlns:app
  ======================================================================================
  `xmlns:app` e OBLIGATORIU aici: `showAsAction` e un atribut definit de biblioteca
    AppCompat, nu de platformă. Fără namespace-ul `app`, atributul nu ar fi recunoscut.

  `app:showAsAction` ȘI NU `android:showAsAction` — atributul e definit de biblioteca
    AppCompat, nu de platformă. Cu `android:` ar fi ignorat silențios pe versiunile
    noi. De ce e ignorat: `android:showAsAction` e citit doar de `ActionBar`-ul de
    framework (API 11+). Aplicația folosește `Theme.Material3.DayNight.NoActionBar`
    și un `MaterialToolbar` ca view simplu — nu există `ActionBar` de framework care
    să citească atributul.

  TOATE VALORILE `showAsAction` ȘI CE SE ÎNTÂMPLĂ LA RUNTIME:

    never                (0) → elementul stă MEREU în overflow (meniul „⋮"),
                               indiferent de spațiu;
    ifRoom               (1) → elementul apare pe bară DACĂ ÎNCAPE; altfel în overflow;
    always               (2) → elementul apare MEREU pe bară, chiar dacă înghesuie
                               titlul;
    withText             (4) → MODIFICATOR: afișează și titlul, nu doar iconița
                               (se combină cu `ifRoom`/`always`);
    collapseActionView   (8) → elementul are un `ActionView` care se strânge la
                               iconiță și se extinde la click (ex. `SearchView`).

  CUM SE COMBINĂ: `withText` și `collapseActionView` sunt FLAG-URI, nu stări. Se
    scriu cu `|`:
      app:showAsAction="ifRoom|withText"          → pe bară, cu iconiță ȘI text
      app:showAsAction="always|collapseActionView" → mereu pe bară, cu ActionView
                                                     colapsabil

  CE FACE TOOLBAR-UL CONCRET, ÎN ORDINE:
    1. Măsoară lățimea disponibilă (ecranul minus iconița de navigare minus titlul).
    2. Parcurge elementele în ordinea din XML.
    3. Pentru fiecare `always`: îl pune pe bară, indiferent de spațiu.
    4. Pentru fiecare `ifRoom`: îl pune pe bară dacă mai încape; altfel în overflow.
    5. Pentru fiecare `never`: îl pune direct în overflow.
    6. Overflow-ul apare doar dacă are cel puțin un element.

  ORDINEA ÎN XML = ORDINEA PE BARĂ, de la stânga la dreapta (după iconița de
    navigare). În overflow, ordinea se păstrează.

  TITLURILE SUNT LITERALE, nu resurse — aceeași observație ca la `drawer_menu.xml`.
  ======================================================================================
-->
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">

    <!--
      ================================================================================
      ELEMENT: action_search — ifRoom
      ================================================================================
      `ifRoom` — apare pe bară dacă încape; altfel în overflow. Pe un telefon îngust,
      unul dintre Search și Share poate cădea în overflow. Pe tabletă apar amândouă.
      Comportamentul depinde de lățimea ecranului, de orientare și de lungimea
      titlului.
      `android:icon="@drawable/ic_search"` — iconița vectorială din `res/drawable/`.
      ================================================================================
    -->
    <item
        android:id="@+id/action_search"
        android:icon="@drawable/ic_search"
        android:title="Search"
        app:showAsAction="ifRoom" />

    <!--
      ================================================================================
      ELEMENT: action_share — ifRoom
      ================================================================================
      A doua acțiune `ifRoom`. Dacă bara nu are loc pentru amândouă, cea de-a doua
      (în ordinea din XML) cade prima în overflow.
      ================================================================================
    -->
    <item
        android:id="@+id/action_share"
        android:icon="@drawable/ic_share"
        android:title="Share"
        app:showAsAction="ifRoom" />

    <!--
      ================================================================================
      ELEMENT: action_settings — never
      ================================================================================
      `never` — stă MEREU în overflow, indiferent de spațiu. Nu are iconiță: în
      overflow, textul e suficient. Elementele cu iconiță în overflow își afișează
      iconița; cele fără, doar textul.

      CE SE ÎNTÂMPLĂ DACĂ PUI `always` PE TOATE TREI: bara devine aglomerată, titlul
      „Inbox" se trunchiază, iar pe ecrane mici elementele se suprapun peste titlu.
      `always` se folosește doar pentru acțiuni critice, maximum una-două.
      CE SE ÎNTÂMPLĂ DACĂ PUI `withText` FĂRĂ `ifRoom`: `withText` singur nu spune
      unde să stea elementul. În practică, se combină mereu cu `ifRoom` sau `always`.
      ================================================================================
    -->
    <!-- Items with "never" go into the ⋮ overflow menu -->
    <item
        android:id="@+id/action_settings"
        android:title="Settings"
        app:showAsAction="never" />
</menu>
```

**Ce reții din meniuri:** `showAsAction` are cinci valori, dar numai trei sunt stări (`never`, `ifRoom`, `always`); `withText` și `collapseActionView` sunt flag-uri. `app:` e obligatoriu; `android:` e ignorat de AppCompat.

---

## 26.7 Fluxuri complete

Secțiunea adună, într-un singur loc, cele patru fluxuri pe care le poți primi la test ca scenariu: pornirea, deschiderea sertarului, meniul contextual și Back. Fiecare are o diagramă și o listă de efecte.

### 26.7.1 Pornirea — de la iconiță la primul cadru

```
┌──────────────┐
│ LANSATOR     │  utilizatorul apasă iconița
└──────┬───────┘
       │ Intent MAIN + LAUNCHER
       ▼
┌──────────────────────────────────────────────────────────────┐
│ ActivityManagerService                                       │
│  - citește AndroidManifest.xml                               │
│  - găsește `.MainActivity` pentru filtrul MAIN/LAUNCHER      │
│  - creează procesul aplicației (dacă nu există)              │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ MainActivity                                                 │
│  constructor → onCreate → onStart → onResume                 │
│                                                              │
│  onCreate:                                                   │
│    1. super.onCreate                                         │
│    2. EdgeToEdge.enable                                      │
│    3. setContentView(activity_main)                          │
│         └── arborele de view-uri se construiește             │
│    4. insets pe R.id.main                                    │
│    5. listView + listener apăsare lungă                      │
│    6. drawerLayout / toolbar / navigationView                │
│    7. listener sertar                                        │
│    8. callback Back                                          │
│    9. listener hamburger                                     │
│   10. listener meniu toolbar                                 │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ MEASURE → LAYOUT → DRAW                                      │
│  - DrawerLayout măsoară conținutul și sertarul               │
│  - CoordinatorLayout măsoară AppBar-ul și FrameLayout-ul     │
│  - ListView creează primele rânduri vizibile                 │
│  - primul cadru apare pe ecran                               │
└──────────────────────────────────────────────────────────────┘
```

**Ce poți spune la test în trei propoziții:** lansatorul trimite un `Intent` cu `MAIN` + `LAUNCHER`; sistemul găsește activitatea în manifest și o creează; `onCreate` construiește arborele, leagă listenerii, iar sistemul desenează primul cadru.

**Ce nu se întâmplă:** nicio citire din `savedInstanceState`, nicio cerere de rețea, nicio bază de date. Ecranul e complet static.

### 26.7.2 Starea sertarului — mașină de stări

```
                    openDrawer(START)
   ┌────────────┐ ──────────────────────► ┌────────────┐
   │   ÎNCHIS   │                         │  DESCHIS   │
   │            │ ◄────────────────────── │            │
   └────────────┘   closeDrawer(START)    └────────────┘
         ▲                sau Back                │
         │                                        │
         │  click pe un element din               │
         │  NavigationView                        │
         └────────────────────────────────────────┘
                  (closeDrawer din listener)

   Glisare de la margine: ÎNCHIS → DESCHIS (gest nativ DrawerLayout)
   Glisare spre margine:  DESCHIS → ÎNCHIS  (gest nativ DrawerLayout)
   Click pe scrim:        DESCHIS → ÎNCHIS  (comportament implicit)
```

**Tranzițiile și cine le declanșează:**

| Tranziție | Declanșator | Cod |
|---|---|---|
| ÎNCHIS → DESCHIS | hamburger | `toolbar.setNavigationOnClickListener` → `openDrawer(START)` |
| ÎNCHIS → DESCHIS | glisare de la margine | `DrawerLayout` nativ |
| DESCHIS → ÎNCHIS | click pe element | `navigationView.setNavigationItemSelectedListener` → `closeDrawer(START)` |
| DESCHIS → ÎNCHIS | Back | `OnBackPressedCallback` → `closeDrawer(START)` |
| DESCHIS → ÎNCHIS | click pe scrim | `DrawerLayout` nativ |
| DESCHIS → ÎNCHIS | glisare spre margine | `DrawerLayout` nativ |

**De ce `DrawerLayout` are nevoie de `closeDrawer` explicit dacă gestul nativ închide:** gestul nativ există, dar nu e suficient. Utilizatorul care apasă un element din meniu se așteaptă ca sertarul să se închidă imediat — nu să gliseze el. `closeDrawer` face tranziția programatic, cu animație.

**Ce se întâmplă dacă apelezi `closeDrawer` când sertarul e deja închis:** nimic. Metoda verifică starea și nu face nimic dacă e deja închis. Nu aruncă excepție. La fel `openDrawer` când e deja deschis.

### 26.7.3 Selectarea unui element din sertar — secvență

```
Utilizator                NavigationView            MainActivity              DrawerLayout
    │                          │                         │                         │
    │  click „Sent"            │                         │                         │
    ├─────────────────────────►│                         │                         │
    │                          │  onMenuItemClick(item)  │                         │
    │                          ├────────────────────────►│                         │
    │                          │                         │                         │
    │                          │                         │  id == nav_sent?        │
    │                          │                         │  → toolbar.setTitle     │
    │                          │                         │    ("Sent")             │
    │                          │                         │                         │
    │                          │                         │  item.setChecked(true)  │
    │                          │◄────────────────────────┤                         │
    │                          │  (bifează „Sent",       │                         │
    │                          │   debifează „Inbox")    │                         │
    │                          │                         │                         │
    │                          │                         │  closeDrawer(START)     │
    │                          │                         ├────────────────────────►│
    │                          │                         │                         │
    │                          │                         │  return true            │
    │                          │◄────────────────────────┤                         │
    │                          │                         │                         │
    │  sertarul se retrage     │                         │                         │
    │◄─────────────────────────┴─────────────────────────┴─────────────────────────┤
```

**Ordinea exactă din cod:** întâi se schimbă titlul, apoi `setChecked`, apoi `closeDrawer`, apoi `return true`. Dacă ai muta `closeDrawer` înainte de `setChecked`, bifarea s-ar face pe un meniu deja ascuns — funcționează, dar nu se vede.

**Ce vede utilizatorul:** sertarul se retrage, titlul barei devine „Sent", iar la redeschidere „Sent" e bifat și „Inbox" nu. Lista nu se schimbă — rămân cele 20 de „Item N".

### 26.7.4 Meniul contextual — secvență

```
Utilizator                ListView                 PopupMenu              MainActivity
    │                        │                         │                        │
    │  apăsare lungă         │                         │                        │
    │  pe rândul 5           │                         │                        │
    ├───────────────────────►│                         │                        │
    │                        │  onItemLongClick(       │                        │
    │                        │    parent, view, 5, 5)  │                        │
    │                        ├────────────────────────►│                        │
    │                        │                         │                        │
    │                        │                         │  new PopupMenu(this,   │
    │                        │                         │      view)             │
    │                        │                         │  inflate(list_item_    │
    │                        │                         │      menu)             │
    │                        │                         │  setOnMenuItemClick... │
    │                        │                         │  show()                │
    │                        │                         │                        │
    │  meniul apare lângă    │                         │                        │
    │  rândul 5              │                         │                        │
    │◄───────────────────────┴─────────────────────────┤                        │
    │                        │                         │                        │
    │  click „Delete"        │                         │                        │
    ├────────────────────────┼────────────────────────►│                        │
    │                        │                         │  itemId == action_     │
    │                        │                         │      delete            │
    │                        │                         │  selected = "Item 6"   │
    │                        │◄────────────────────────┤  Toast "Delete:        │
    │                        │  getItemAtPosition(5)   │      Item 6"           │
    │                        │                         │  return true           │
    │                        │                         │                        │
    │  meniul se închide     │                         │                        │
    │◄───────────────────────┴─────────────────────────┘                        │
```

**Atenție la index:** `position` e 0-based, deci rândul 5 afișează „Item 6". Nu e un bug — e convenția Java.

**De ce `selected` se calculează în listener-ul de meniu și nu în cel de apăsare lungă:** pentru că `position` e capturat și rămâne valid. Ai putea să-l calculezi mai devreme și să-l captezi, dar ai avea o variabilă în plus. Calculul la click e mai direct.

### 26.7.5 Back — cele două ramuri

```
                         ┌─────────────────────┐
                         │  Back apăsat        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ dispatcher.onBackPressed()    │
                    │ parcurge callback-urile       │
                    │ de la ultimul spre primul     │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ callback-ul nostru e activ?   │
                    └───────┬───────────────┬───────┘
                            │ DA            │ NU
                            ▼               ▼
              ┌─────────────────────┐   ┌──────────────────────┐
              │ isDrawerOpen(START) │   │ următorul callback  │
              └──────┬───────┬──────┘   │ sau fallback         │
                     │ DA    │ NU       │   └─ finish()        │
                     ▼       ▼          └──────────────────────┘
        ┌────────────────┐  ┌──────────────────────────────┐
        │ closeDrawer    │  │ setEnabled(false)            │
        │                │  │ onBackPressed()              │
        │ rămâi pe ecran │  │   └─ fallback → finish()     │
        └────────────────┘  └──────────────────────────────┘
```

**Cele două ramuri, într-o propoziție fiecare:** sertar deschis → îl închizi și rămâi; sertar închis → te dezactivezi și lași sistemul să închidă activitatea.

**De ce nu `finish()` direct în ramura a doua:** ai sări peste orice alt callback din lanț. Dacă ai adăuga un `NavController` sau un al doilea callback, Back ar trebui să ajungă la ele întâi.

### 26.7.6 `SecondActivity` — fluxul complet

```
LANSARE MANUALĂ
  onCreate
    ├── super.onCreate
    ├── EdgeToEdge.enable
    ├── setContentView(activity_second)
    ├── insets pe R.id.main
    └── inflatedLayout = findViewById(R.id.main)

CLICK „Button"
  android:onClick → reflecție → btnClick(View)
    ├── AlertDialog.Builder(SecondActivity.this)
    ├── setTitle / setMessage / setCancelable
    ├── setPositiveButton("Do it!", listener)
    ├── setNegativeButton("Cancel", listener)
    └── builder.show()

CLICK „Do it!"
  ├── id = addButton()
  │     ├── new Button(SecondActivity.this)
  │     ├── setText("Button_1")
  │     ├── setId(1)
  │     ├── setLayoutParams(MATCH_PARENT, WRAP_CONTENT)
  │     └── inflatedLayout.addView(newBtn)
  └── Snackbar.make(..., inflatedLayout, "Cancel previous action.", LENGTH_LONG)
        ├── setAction("Cancel", listener)
        └── show()
              └── CLICK „Cancel"
                    ├── findViewById(1)
                    └── removeView(butonul)

CLICK „Cancel" (în dialog)
  └── Toast "Object creation cancelled"
```

**Ce se vede pe ecran, în ordine:** dialogul, apoi butonul nou sub butonul original, apoi Snackbar-ul de jos. Dacă apeși „Cancel" pe Snackbar, butonul dispare; Snackbar-ul se închide oricum.

**Ce se întâmplă dacă apeși „Do it!" de trei ori:** dialogul se închide după fiecare click, deci trebuie să redeschizi. Fiecare „Do it!" adaugă un buton și un Snackbar. Snackbar-urile se înlocuiesc unul pe altul (un singur Snackbar vizibil per părinte).

### 26.7.7 Ce se întâmplă în memorie

```
ActivityManagerService
    └── MainActivity (instanță)
          ├── mDecorView (fereastra)
          │     └── DrawerLayout
          │           ├── CoordinatorLayout (id=main)
          │           │     ├── AppBarLayout
          │           │     │     └── MaterialToolbar
          │           │     │           ├── navigationIcon view
          │           │     │           └── menu items
          │           │     └── FrameLayout
          │           │           └── ListView
          │           │                 └── adapter (ArrayAdapter)
          │           │                       └── 20 String-uri
          │           └── NavigationView
          │                 └── Menu (din drawer_menu.xml)
          └── câmpuri:
                ├── drawerLayout  → referință la view
                └── listView      → referință la view
```

**Listenerii și ciclul de viață:** fiecare listener e un obiect atașat unui view (`ListView.mOnItemLongClickListener`, `Toolbar.mOnMenuItemClickListener`, `Toolbar.mNavigationOnClickListener`, `NavigationView.mListener`, `OnBackPressedDispatcher.callbacks`). Toți țin o referință la `MainActivity` (prin captură sau prin câmp) și sunt deținuți de view-uri deținute de activitate. Ciclul Activity → View → Listener → Activity se rupe când activitatea e distrusă. Nu e scurgere.

**La rotire:** sistemul cheamă `onSaveInstanceState` (dacă e implementat), apoi `onPause` → `onStop` → `onDestroy` pe instanța veche. Creează o instanță NOUĂ și cheamă din nou `onCreate`. Toate view-urile vechi sunt colectate de gunoi; toți listenerii mor cu ele. Starea care nu e salvată se pierde: titlul, bifarea, poziția listei.

**Ce ar trebui salvat pentru o aplicație reală:** titlul curent (String), id-ul elementului bifat, poziția listei (`ListView` salvează singur, dacă are id), butoanele adăugate în `SecondActivity` (listă de id-uri + texte).

**De ce `counter` se resetează:** e un câmp de instanță, nu `static`. Instanța nouă pornește cu `counter = 0`. Dacă ar fi `static`, ar supraviețui rotirii, dar ar trăi cât procesul și ar crește la infinit.

**Când ar apărea o scurgere:** dacă ai pune un listener într-un `static` (de exemplu `private static List<View.OnClickListener> listeners`) sau într-un singleton la nivel de aplicație. Atunci referința ar supraviețui activității și ar ține-o în viață.

---

## 26.8 Capcane — simptom, cauză, remediu

Secțiunea e scrisă ca un tabel de diagnostic. La test, întrebarea „ce se întâmplă dacă…" se răspunde din coloana „Simptom".

### 26.8.1 Capcane în `MainActivity`

| # | Ce faci greșit | Simptom | Cauză | Remediu |
|---|---|---|---|---|
| 1 | Uiți `closeDrawer` în listener-ul sertarului | titlul se schimbă, dar sertarul rămâne peste ecran | `NavigationView` nu știe de `DrawerLayout` | `drawerLayout.closeDrawer(GravityCompat.START)` |
| 2 | Uiți `setEnabled(false)` în callback-ul Back | `StackOverflowError` la Back cu sertarul închis | callback-ul se reapelează pe el însuși | dezactivează-te înainte de `onBackPressed()` |
| 3 | Folosești `Gravity.LEFT` într-un loc și `START` în altul | merge în română, se strică în RTL | constante diferite | folosește `GravityCompat.START` peste tot |
| 4 | Uiți `return true` la apăsarea lungă | meniul apare și se declanșează și click-ul | `mHasPerformedLongPress` rămâne `false` | `return true` după `popup.show()` |
| 5 | Uiți `popup.show()` | nimic nu apare la apăsare lungă | meniul e construit, dar nu afișat | cheamă `show()` |
| 6 | Uiți `popup.getMenuInflater().inflate(...)` | meniu gol, fără elemente | nu s-a umplut `Menu`-ul | umfle cu `R.menu.list_item_menu` |
| 7 | Pui `toolbar` ca ancoră a `PopupMenu` | meniul apare sub bară, nu lângă rând | ancora greșită | folosește `view` (rândul) |
| 8 | Pui `listView` ca ancoră | meniul apare la marginea listei | ancora e prea mare | folosește `view` |
| 9 | Uiți `app:menu` din toolbar | bara nu are Search/Share/Settings | meniul nu e umflat | adaugă `app:menu="@menu/top_app_bar"` |
| 10 | Uiți `app:navigationIcon` | nu există hamburger | iconița nu e setată | adaugă `app:navigationIcon="@drawable/ic_menu"` |
| 11 | Uiți `setNavigationOnClickListener` | hamburger-ul e decorativ | nimeni nu ascultă click-ul | înregistrează listener-ul |
| 12 | Uiți `setOnMenuItemClickListener` | elementele din meniu nu fac nimic | nimeni nu ascultă click-ul | înregistrează listener-ul |
| 13 | Pui `android:showAsAction` | atributul e ignorat | AppCompat citește `app:` | folosește `app:showAsAction` |
| 14 | Pui `always` pe toate elementele | titlul se trunchiază, bara e aglomerată | `always` nu ține cont de spațiu | folosește `ifRoom` |

**De ce capcana 2 e cea mai gravă:** `StackOverflowError` nu poate fi prinsă elegant și crapă aplicația imediat. Nu există mesaj util în log — doar o urmă de stivă uriașă, cu `handleOnBackPressed` repetat de mii de ori.

**De ce capcana 1 e cea mai frecventă:** pare că `NavigationView` ar trebui să închidă sertarul singur. Nu o face, pentru că nu are referință la el. E o separare de responsabilități, nu o scăpare.

### 26.8.2 Capcane în `SecondActivity`

| # | Ce faci greșit | Simptom | Cauză | Remediu |
|---|---|---|---|---|
| 1 | Faci `btnClick` `private` | compilează, crapă la click cu `IllegalStateException` | reflecția caută metode publice | `public void btnClick(View)` |
| 2 | Schimbi parametrul în `Object` | aceeași excepție la click | semnătura nu se potrivește | păstrează `View` |
| 3 | Uiți `builder.show()` | dialogul nu apare | builder-ul e construit, dar nu afișat | cheamă `show()` |
| 4 | Uiți `.show()` la Snackbar | Snackbar-ul nu apare | construit, dar nu afișat | adaugă `.show()` |
| 5 | Uiți `setId` în `addButton` | butonul apare, dar nu poate fi șters | `findViewById` întoarce `null` | `newBtn.setId(counter)` |
| 6 | Folosești `getApplicationContext()` | butonul pierde tema / crapă la inflate | context netematizat | `SecondActivity.this` |
| 7 | Pui `counter++` în loc de `++counter` | primul buton are id 0 | post-increment | `++counter` |
| 8 | Nu salvezi butoanele în `savedInstanceState` | la rotire dispar | arborele se reconstruiește din XML | salvează id-urile și reconstruiește |
| 9 | Pui `Snackbar.make` cu un `Context` în loc de `View` | nu compilează | nu există suprascrierea | al doilea argument e `View` |
| 10 | Uiți `setLayoutParams` | butonul are dimensiuni implicite | părintele generează `LayoutParams` | setează explicit |

**De ce capcana 6 e subtilă:** `getApplicationContext()` compilează și, pe unele teme, funcționează. Eroarea apare doar când widget-ul are nevoie de un atribut de temă care există doar în tema activității. Atunci primești `InflateException` sau un widget complet nestilizat.

**De ce capcana 8 nu e un bug, ci o limitare:** un view adăugat din cod nu face parte din XML, deci nu poate fi reconstruit automat. Salvarea în `Bundle` e responsabilitatea ta.

### 26.8.3 Capcane în XML

| # | Ce faci greșit | Simptom | Cauză | Remediu |
|---|---|---|---|---|
| 1 | Pui `NavigationView` fără `layout_gravity` | sertarul acoperă ecranul și nu se deschide | e tratat ca al doilea conținut | `android:layout_gravity="start"` |
| 2 | Pui al treilea copil în `DrawerLayout` | conținutul e acoperit | copilul fără gravity e tratat ca conținut | doar conținut + sertar |
| 3 | Pui doi copii cu `start` | `IllegalStateException` la inflate | un singur sertar per margine | unul `start`, unul `end` |
| 4 | Scoți `app:layout_behavior` | lista se desenează sub bară | `CoordinatorLayout` nu știe să o împingă | adaugă comportamentul |
| 5 | Scoți `liftOnScrollTargetViewId` | lift-ul poate fi sacadat sau aplicat pe alt view | detectarea automată e nesigură când view-ul e imbricat | adaugă id-ul |
| 6 | Scoți `android:nestedScrollingEnabled` | scroll-ul nu ajunge la `CoordinatorLayout` | lista înghite evenimentele | setează `true` |
| 7 | Pui `match_parent` pe `NavigationView` | sertarul acoperă tot ecranul | lățime greșită | `wrap_content` |
| 8 | Pui `id=main` pe `DrawerLayout` | padding peste padding-ul sertarului | insets aplicate pe rădăcină | pune id-ul pe conținut |
| 9 | Pui `android:background` pe toolbar | două straturi de mov | culoarea vine din `AppBarLayout` | `@android:color/transparent` |
| 10 | Pui `56dp` hardcodat | bara arată greșit pe alte teme | înălțime fixă | `?attr/actionBarSize` |

**De ce capcana 1 e cea mai înșelătoare:** XML-ul e valid, build-ul trece, aplicația pornește. Doar că sertarul nu se deschide — și niciun log nu spune de ce. Trebuie să știi regula ca să o diagnostichezi.

**De ce capcana 8 e greu de văzut:** padding-ul suplimentar e mic (înălțimea status bar) și arată ca o margine de design. Pe un telefon cu notch, diferența e mai vizibilă.

### 26.8.4 Cum verifici manual fiecare comportament

| # | Ce verifici | Cum | Rezultatul corect |
|---|---|---|---|
| 1 | Sertarul se deschide | apasă hamburger-ul | `NavigationView` glisează din stânga peste conținut |
| 2 | Sertarul se închide la selecție | deschide sertarul, apasă „Sent" | sertarul se retrage, titlul devine „Sent" |
| 3 | Bifarea e exclusivă | deschide sertarul din nou | „Sent" e bifat, „Inbox" nu |
| 4 | Meniul contextual e ancorat | apăsare lungă pe „Item 7" | meniul apare lângă rândul 7, nu sub toolbar |
| 5 | Back închide sertarul | deschide sertarul, apasă Back | sertarul se închide, aplicația rămâne deschisă |
| 6 | Back închide aplicația | cu sertarul închis, apasă Back | aplicația se închide, fără crash |
| 7 | Meniul barei funcționează | apasă Search, Share, apoi Settings din „⋮" | trei `Toast`-uri diferite |
| 8 | `SecondActivity` e inaccesibilă | parcurge toate ecranele aplicației | nu există nicio cale către ea |
| 9 | Dialogul și Snackbar-ul | lansează manual `SecondActivity`, apasă butonul, „Do it!", apoi „Cancel" pe Snackbar | buton nou, apoi dispare |

**Cum verifici 8 fără să lansezi manual:** caută `SecondActivity` în tot codul. Singurele apariții sunt în manifest, în propriul fișier și în `tools:context`. Niciun `Intent`, niciun `startActivity`.

**Cum verifici 4 cu precizie:** apasă lung pe primul rând și pe ultimul. Meniul trebuie să apară dedesubt pe primul și deasupra pe ultimul — `PopupWindow` îl mută ca să încapă.

**Cum verifici 6 fără să închizi aplicația din greșeală:** deschide sertarul, apasă Back (se închide), apasă din nou Back (se închide aplicația). Dacă ai `StackOverflowError`, aplicația crapă la al doilea Back — exact simptomul capcanei 2.

**Ce nu poți verifica fără un dispozitiv RTL:** comportamentul `start`/`end`. Poți schimba limba sistemului în arabă sau ebraică, ori poți forța direcția din opțiunile de dezvoltator („Force RTL layout direction").

---

## 26.9 Legăturile XML ↔ cod

Aproape fiecare bug din proiecte Android mici e o legătură ruptă între un nume din XML și un nume din cod. Tabelul le adună pe toate.

| În XML | În cod | Ce se strică dacă diferă |
|---|---|---|
| `android:layout_gravity="start"` | `GravityCompat.START` | sertarul nu se deschide / nu se închide |
| `@+id/drawerLayout` | `R.id.drawerLayout` | `NullPointerException` |
| `@+id/topAppBar` | `R.id.topAppBar` | `NullPointerException` |
| `@+id/navigationView` | `R.id.navigationView` | `NullPointerException` |
| `@+id/listView` | `R.id.listView` | `NullPointerException` |
| `@+id/main` | `R.id.main` (insets) | fără padding, conținut sub bare |
| `android:onClick="btnClick"` | `public void btnClick(View)` | `IllegalStateException` la click |
| `app:menu="@menu/top_app_bar"` | `toolbar.setOnMenuItemClickListener` | listener mort |
| `app:menu="@menu/drawer_menu"` | `navigationView.setNavigationItemSelectedListener` | listener mort |
| `@+id/action_open` etc. | `R.id.action_open` etc. | ramura nu se mai execută |
| `@+id/nav_inbox` etc. | `R.id.nav_inbox` etc. | ramura nu se mai execută |
| `android:entries="@array/items"` | `listView.getItemAtPosition(...)` | listă goală |
| `app:liftOnScrollTargetViewId="@id/listView"` | `@+id/listView` | lift-ul poate fi sacadat sau aplicat pe alt view |

**Regula generală:** fiecare `R.id.*` din cod trebuie să aibă un `@+id/*` în XML. Fiecare `@+id/*` din XML care e folosit în cod trebuie să aibă un `R.id.*`. Un id fără pereche nu dă eroare de compilare — doar un `null` sau un `if` mort.

**Cum verifici rapid:** `Ctrl+Click` pe `R.id.nume` în Android Studio. Dacă te duce la XML, legătura există. Dacă nu, ai un id greșit sau lipsă.

**De ce `@+id` are `+` doar prima dată:** `+` înseamnă „creează id-ul". A doua apariție într-un alt fișier XML poate folosi `@id/...` (fără `+`), pentru că id-ul există deja în `R`. În practică, `@+id` funcționează și a doua oară — doar că nu mai creează nimic.

### 26.9.1 Cum citești un stack trace pentru cele cinci excepții ale proiectului

**1. `NullPointerException` la un `findViewById`**

```
java.lang.NullPointerException: Attempt to invoke virtual method
    'void android.widget.ListView.setOnItemLongClickListener(...)'
    on a null object reference
    at ro.ase.ie.dma03.MainActivity.onCreate(MainActivity.java:40)
```

**Cum îl citești:** ultima linie din trace e locul exact. „on a null object reference" înseamnă că `listView` e `null`. Cauza: `findViewById` a fost apelat înainte de `setContentView` sau id-ul nu există în XML.

**2. `IllegalStateException: Could not find method btnClick(View)`**

```
java.lang.IllegalStateException: Could not find method btnClick(View) in a
    parent or ancestor Context for android:onClick attribute defined on view
    class android.widget.Button with id 'button'
    at android.view.View$DeclaredOnClickListener.resolveMethod(...)
```

**Cum îl citești:** mesajul spune exact ce metodă lipsește și pe ce view. Cauze: metoda e `private`, are alt parametru, sau a fost redenumită fără să modifici XML-ul.

**3. `StackOverflowError` la Back**

```
java.lang.StackOverflowError:
    at ro.ase.ie.dma03.MainActivity$1.handleOnBackPressed(MainActivity.java:94)
    at androidx.activity.OnBackPressedDispatcher.onBackPressed(...)
    at ro.ase.ie.dma03.MainActivity$1.handleOnBackPressed(MainActivity.java:98)
    at androidx.activity.OnBackPressedDispatcher.onBackPressed(...)
    ... (mii de linii identice)
```

**Cum îl citești:** două linii care se repetă la infinit. Cauza: `onBackPressed()` e chemat din callback-ul care ar trebui să-l gestioneze, fără `setEnabled(false)`.

**4. `IllegalStateException: Child drawer has absolute gravity`**

```
java.lang.IllegalStateException: Child drawer has absolute gravity LEFT but
    this DrawerLayout already has a drawer view along that edge
    at androidx.drawerlayout.widget.DrawerLayout.addDrawerChild(...)
```

**Cum îl citești:** ai doi copii cu `layout_gravity` pe aceeași margine. Cauza: un al doilea `NavigationView` cu `start`, sau un `FrameLayout` cu `layout_gravity="left"` accidental.

**5. `InflateException` la `setContentView`**

```
android.view.InflateException: Binary XML file line #17: Error inflating class
    com.google.android.material.appbar.MaterialToolbar
    Caused by: java.lang.IllegalArgumentException: The style on this component
    requires your app theme to be Theme.MaterialComponents (or a descendant).
```

**Cum îl citești:** ultima linie „Caused by" e cauza reală. Aici: tema aplicației nu e Material. Cauza: `Theme.DMA03` a fost schimbată sau `setContentView` rulează într-un context cu altă temă.

**Regula generală de citire:** de sus în jos, ultima linie „Caused by" e cauza; prima linie din trace care conține `ro.ase.ie.dma03` e locul din codul tău. Restul sunt apeluri din bibliotecă — utile doar dacă vrei să înțelegi mecanismul.

**Ce nu trebuie să faci:** să citești tot trace-ul de sus în jos și să te oprești la prima linie din Android. Cauza e aproape mereu în ultimul „Caused by" și în prima linie a codului tău.

---

## 26.10 Ce să reții

| Fișier | Esența |
|---|---|
| `MainActivity.java` | `onCreate` face tot: insets, listă, drawer, Back, hamburger, meniu. `GravityCompat.START` de patru ori, identic cu XML-ul. |
| `SecondActivity.java` | `android:onClick` cere `public void nume(View)`. `setId` e ce face butonul găsibil. `hPixels` e cod mort. |
| `AndroidManifest.xml` | `exported="true"` + `MAIN`/`LAUNCHER` = ecranul de start. `SecondActivity` e declarată, dar nelegată. |
| `activity_main.xml` | `DrawerLayout` cu exact 2 copii; al doilea are `layout_gravity="start"`. `id=main` e pe conținut, nu pe drawer. |
| `activity_second.xml` | `LinearLayout` vertical cu un buton legat prin `android:onClick`. |
| `drawer_menu.xml` | `checkableBehavior="single"` = radio group. `item` fără id + `menu` imbricat = subtitlu de secțiune. |
| `list_item_menu.xml` | Trei acțiuni, fără iconițe. Id-urile trebuie să coincidă cu cele din cod. |
| `top_app_bar.xml` | `app:showAsAction`: `ifRoom` pe bară, `never` în overflow. |

### Cele șase legături care trebuie să fie identice

| În XML | În cod | Ce se strică dacă diferă |
|---|---|---|
| `android:layout_gravity="start"` | `GravityCompat.START` | sertarul nu se deschide / nu se închide |
| `@+id/drawerLayout` | `R.id.drawerLayout` | `NullPointerException` |
| `@+id/topAppBar` | `R.id.topAppBar` | `NullPointerException` |
| `@+id/navigationView` | `R.id.navigationView` | `NullPointerException` |
| `@+id/main` | `R.id.main` (insets) | fără padding, conținut sub bare |
| `android:onClick="btnClick"` | `public void btnClick(View)` | `IllegalStateException` la click |

### Greșelile pe care le-ar prinde un test

1. **Uiți `closeDrawer`** — sertarul rămâne peste ecran după selecție.
2. **Uiți `setEnabled(false)` în callback-ul de Back** — `StackOverflowError` la Back cu sertarul închis.
3. **Pui `Gravity.LEFT` într-un loc și `START` în altul** — merge în română, se strică în RTL.
4. **Scoți `app:layout_behavior`** — lista se desenează sub bară.
5. **Scoți `liftOnScrollTargetViewId`** — lift-ul poate fi sacadat sau aplicat pe alt view.
6. **Scoți `setId` din `addButton`** — Snackbar-ul nu mai găsește butonul de șters.
7. **Faci `btnClick` privată** — compilează, crapă la click.

### Cele cinci întrebări de examen la care răspunde capitolul

| Întrebare | Răspunsul scurt | Secțiunea |
|---|---|---|
| De ce `DrawerLayout` are exact doi copii? | primul = conținut, al doilea = sertar; rolul e dat de `layout_gravity` | 26.4.4 |
| De ce `setNavigationItemSelectedListener` nu închide sertarul? | `NavigationView` nu are referință la `DrawerLayout` | 26.1.13 |
| De ce `setEnabled(false)` înainte de `onBackPressed()`? | altfel callback-ul se reapelează pe el însuși, recursie infinită | 26.1.14 |
| De ce `Snackbar.make` cere un `View`? | Snackbar-ul se inserează în arbore, nu într-o fereastră separată | 26.2.6 |
| De ce `SecondActivity` nu apare niciodată? | e declarată în manifest, dar niciun `Intent` nu o pornește | 26.3 |

---

## 26.11 Glosar

Termenii care apar în capitol și pe care un test îi poate cere fără să-i definească. Definițiile sunt scurte intenționat: un termen, o propoziție, un exemplu din proiect.

| Termen | Definiție | Unde apare |
|---|---|---|
| **Activity** | componentă cu o fereastră proprie, pornită de sistem | `MainActivity`, `SecondActivity` |
| **Context** | acces la resurse, temă și servicii de sistem | `this` în `new PopupMenu(this, view)` |
| **Context tematizat** | context care are o temă aplicată | `SecondActivity.this` la `new Button(...)` |
| **View** | orice element desenabil | `ListView`, `Button`, `Toolbar` |
| **ViewGroup** | view care conține alți copii și îi poziționează | `DrawerLayout`, `LinearLayout` |
| **LayoutParams** | contractul dintre copil și părinte despre dimensiuni | `ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)` |
| **Inflater** | parser care transformă XML în obiecte | `LayoutInflater`, `MenuInflater` |
| **Listener** | obiect care așteaptă un eveniment | `setOnItemLongClickListener` |
| **Lambda** | implementare concisă a unei interfețe funcționale | toți listenerii din proiect |
| **Insets** | zonele ocupate de barele de sistem | blocul din `onCreate` |
| **Drawer** | panou glisant peste conținut | `NavigationView` |
| **Scrim** | stratul semi-transparent din spatele sertarului | desenat de `DrawerLayout` |
| **Overflow** | meniul „⋮" pentru elementele care nu încap pe bară | `action_settings` |
| **ActionView** | view care înlocuiește iconița unui element de meniu | `SearchView` (nu e folosit aici) |
| **RTL** | right-to-left; direcție de citire pentru arabă/ebraică | `layout_gravity="start"` |
| **dp** | pixel independent de densitate | `?attr/actionBarSize` (56dp) |
| **Manifest** | fișierul care declară componentele aplicației | `AndroidManifest.xml` |
| **exported** | dacă o componentă poate fi pornită din altă aplicație | `MainActivity` = `true` |
| **Intent** | descrierea unei acțiuni sau a unui ecran de pornit | importul nefolosit |
| **Reflecție** | căutarea unei metode după nume, la runtime | `android:onClick` |
| **Snackbar** | bară de feedback cu acțiune opțională | `SecondActivity` |
| **Dialog** | fereastră modală care cere o decizie | `AlertDialog` |
| **Toast** | mesaj scurt, fără acțiune | toate ramurile de meniu |
| **Stare** | datele care ar trebui să supraviețuiască recreării | `savedInstanceState` |

### Cinci perechi de termeni care se confundă

**1. `View` vs `ViewGroup`** — `ViewGroup` **este** un `View` (moștenește din el), dar are copii. Un `Button` e `View`, un `LinearLayout` e `ViewGroup`. În XML, ambele sunt tag-uri; în cod, ambele sunt `View`.

**2. `LayoutInflater` vs `MenuInflater`** — primul citește layout-uri (`<LinearLayout>`, `<Button>`), al doilea citește meniuri (`<menu>`, `<item>`). Nu se înlocuiesc unul pe altul.

**3. `Toast` vs `Snackbar`** — `Toast` nu are nevoie de un view și nu poate fi anulat; `Snackbar` are nevoie de un view și poate avea o acțiune. `Toast` apare într-o fereastră separată, `Snackbar` în arborele ecranului.

**4. `PopupMenu` vs `ContextMenu`** — `PopupMenu` e ancorat pe un view și apare lângă el; `ContextMenu` apare centrat, ca un dialog, după `registerForContextMenu`. Aici e folosit `PopupMenu`.

**5. `Gravity.LEFT` vs `GravityCompat.START`** — primul e stânga fizică, al doilea e începutul direcției de citire. În LTR sunt egale ca efect; în RTL diferă. Codul folosește exclusiv `START`.

**De ce glosarul e la final și nu la început:** termenii se învață mai bine după ce i-ai văzut în context. Dacă l-ai citi întâi, ai memora definiții fără exemple. Acum, fiecare definiție îți amintește de o linie din proiect.

**Cum îl folosești înainte de test:** acoperă coloana „Definiție" și încearcă să explici termenul în două propoziții, cu un exemplu din `DMA03`. Dacă nu poți, ai o secțiune de recitit.

---

## Rezumat capitol 26

- `MainActivity` are un singur `onCreate` cu zece pași; ordinea `super` → `EdgeToEdge` → `setContentView` → `findViewById` e obligatorie.
- `DrawerLayout` are exact doi copii: conținutul și sertarul. Sertarul se recunoaște după `layout_gravity="start"`.
- `id=main` e pe `CoordinatorLayout`, nu pe `DrawerLayout` — insets-urile se aplică doar pe conținut, iar `NavigationView` se ocupă singură de ale ei.
- `MaterialToolbar` are două zone de click, cu două listenere diferite: `setNavigationOnClickListener` (hamburger) și `setOnMenuItemClickListener` (Search/Share/Settings).
- `PopupMenu` e ancorat pe rândul apăsat și are nevoie de `return true` ca să nu declanșeze și click-ul normal.
- `OnBackPressedCallback` rezolvă Back în doi pași: închide sertarul, apoi se dezactivează și re-trimite evenimentul. Fără `setEnabled(false)`, recursie infinită.
- `AlertDialog.Builder` se înlănțuie; `show()` e obligatoriu. Aici e varianta de platformă, nu AppCompat.
- `Snackbar` are nevoie de `.show()` și de un view de referință; acțiunea lui poate șterge un view adăugat din cod.
- View-urile create din cod au nevoie de trei lucruri: context tematizat, `LayoutParams`, `setId` dacă vrei să le regăsești.
- `SecondActivity` e declarată în manifest, dar **nu e pornită nicăieri** — importul `Intent` din `MainActivity` e singura urmă a legăturii care lipsește.

**Înapoi la** [cheatsheet](21%20-%20Cheatsheet.md), la [capitolul DMA03 de construcție](14%20-%20DMA03%20-%20Navigare%20si%20meniuri.md) **sau la** [prezentarea generală](index.html).

