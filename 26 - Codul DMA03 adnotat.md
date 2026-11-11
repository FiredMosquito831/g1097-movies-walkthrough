# Capitolul 26 — Codul DMA03 adnotat

**Obiectiv:** să citești proiectul `DMA03` bloc cu bloc — fiecare linie explicată: ce face, de ce e acolo, ce se strică dacă o scoți. La final trebuie să poți reconstrui din memorie un drawer cu toolbar, un meniu contextual pe rând și un dialog care creează controale.

**Timp estimat:** 60–90 min (citire activă).

**Sursa:** `DMA03/` la commitul `d719ffc` — 8 fișiere: două activități, manifestul, două layout-uri și trei meniuri.

**Ce înveți din el:** `DrawerLayout`, `NavigationView`, `MaterialToolbar`, `PopupMenu`, `OnBackPressedCallback`, `AlertDialog`, `Snackbar`, view-uri create din cod.

> **Cum citești:** nu citi pasiv. Pentru fiecare bloc, acoperă explicația și încearcă să spui tu ce face. Dacă nu poți, ai găsit ce trebuie repetat.
>
> **Despre comentarii:** fișierele au deja câteva comentarii scrise de autor (`// Long press shows the popup menu`, `// anchored to the pressed row`). Le-am păstrat. Comentariile adăugate pentru capitol arată la fel — tot cu `//` — dar sunt mai lungi și explică **de ce**, nu **ce**. Codul propriu-zis e neatins.

---

## 26.1 `MainActivity.java` — drawer, toolbar, meniuri

Un singur `onCreate`, șapte responsabilități. Fișierul nu are metode ajutătoare — totul e inline. E cel mai dens fișier din proiect și, la test, cel mai probabil să-ți ceară o modificare.

### Importurile — și un import mort

```java
package ro.ase.ie.dma03;

import android.content.Intent;          // ← IMPORTAT, DAR NEFOLOSIT. Nu există niciun Intent în tot fișierul.
import android.os.Bundle;               // starea salvată la recreare (aici nu e folosită)
import android.widget.ListView;         // lista de 20 de rânduri
import android.widget.PopupMenu;        // meniul ancorat pe rând (long press)
import android.widget.Toast;            // mesajul scurt, fără acțiune
```

**`import android.content.Intent` fără nicio utilizare** nu e o scăpare de stil — e dovada că `SecondActivity` nu e pornită nicăieri. Un `Intent` ar fi singurul mod de a deschide al doilea ecran, iar în tot proiectul apare o singură dată: pe linia asta. Detaliul e reluat în 26.2 și 26.3.

**De ce `android.widget.*` și nu `androidx.appcompat.widget.AppCompatListView`:** `ListView` nu are variantă AppCompat. `PopupMenu` are (`androidx.appcompat.widget.PopupMenu`), dar aici e folosită cea de platformă — funcționează, doar că nu moștenește stilul Material.

```java
import androidx.activity.EdgeToEdge;              // desenare sub barele de sistem
import androidx.activity.OnBackPressedCallback;   // butonul Back modern
import androidx.appcompat.app.AppCompatActivity;  // activitatea de bază
import androidx.core.graphics.Insets;             // dreptunghiurile barelor de sistem
import androidx.core.view.GravityCompat;          // START/END, sigure pentru RTL
import androidx.core.view.ViewCompat;             // listener-ul de insets
import androidx.core.view.WindowInsetsCompat;     // tipurile de insets
import androidx.drawerlayout.widget.DrawerLayout; // containerul cu sertar
```

**`GravityCompat` și nu `Gravity`:** `Gravity.LEFT` e „stânga fizică". `GravityCompat.START` e „începutul direcției de citire" — stânga în română, dreapta în arabă. În fișier apare de patru ori: `closeDrawer` de două ori, `isDrawerOpen` și `openDrawer`. Toate trebuie să fie aceeași direcție ca `layout_gravity` din XML. Amestecul `START`/`LEFT` produce un sertar care se deschide dintr-o parte și nu se închide din aceeași parte.

**`androidx.drawerlayout` nu apare în `build.gradle.kts`.** Vine tranzitiv, prin `libs.material`. Dacă vreodată scoți Material din dependențe, `DrawerLayout` dispare și el — deși pare o componentă de bază.

```java
import com.google.android.material.appbar.MaterialToolbar;   // bara de sus, varianta Material 3
import com.google.android.material.navigation.NavigationView; // conținutul sertarului
```

**`MaterialToolbar` și nu `androidx.appcompat.widget.Toolbar`:** aceeași clasă de bază, dar cu stilizare Material 3 aplicată automat — înălțime, tipografie, ripple. Ambele ar funcționa; `MaterialToolbar` cere mai puțină configurare ca să arate corect.

### Câmpurile

```java
public class MainActivity extends AppCompatActivity {

    private DrawerLayout drawerLayout;   // folosit în 3 locuri: listener drawer, Back, hamburger
    private ListView listView;           // folosit în listenerul de long press
```

**De ce câmpuri și nu variabile locale:** ambele sunt citite din interiorul unor listeneri lambda, care se execută **după** ce `onCreate` s-a terminat. O variabilă locală ar fi prinsă în closure (lambda capturează doar variabile effectively final), dar un câmp e mai clar și supraviețuiește cât trăiește activitatea.

**`private`** — nimic din afară nu are nevoie de ele. `drawerLayout` ar fi putut fi și locală (toate cele trei utilizări sunt în `onCreate`); e câmp din obișnuință, ca să fie la îndemână dacă adaugi metode noi.

### Începutul lui `onCreate` — ordinea e obligatorie

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);       // 1. lansează ciclul de viață al părintelui
        EdgeToEdge.enable(this);                  // 2. permite desenarea sub status bar și sub bara de navigare
        setContentView(R.layout.activity_main);   // 3. umflă XML-ul și construiește arborele de view-uri
```

**Ordinea nu e negociabilă.** `findViewById` apelat înainte de `setContentView` întoarce `null` — nu aruncă excepție, doar îți dă un `NullPointerException` mai târziu, pe o linie fără legătură aparentă.

**`EdgeToEdge.enable(this)`** face fereastra să ocupe tot ecranul, inclusiv zonele de sub ceas și sub bara de gesturi. Fără ea, aplicația ar avea bare de sistem opace și nu ai avea nevoie de blocul următor. Cu ea, **ai** nevoie — altfel primul rând din listă intră sub ceas.

### Insets — padding pe rădăcină

```java
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
```

**Ce face:** când sistemul calculează cât ocupă barele, aplică pe view-ul cu `id=main` un padding egal cu ele. Conținutul se mută în zona sigură, fundalul rămâne întins pe tot ecranul.

**`R.id.main` e pe `CoordinatorLayout`, nu pe `DrawerLayout`.** Contează: padding-ul se aplică pe **panoul de conținut**, nu pe sertar. `NavigationView` își aplică singură insets-urile (extinde `ScrimInsetsFrameLayout`), deci nu are nevoie de ajutor. Dacă ai fi pus `id=main` pe `DrawerLayout`, ai fi adăugat padding peste padding-ul sertarului.

**`return insets`** — nu `WindowInsetsCompat.CONSUMED`. Insets-urile merg mai departe, la copii. Dacă le-ai consuma, `AppBarLayout` nu ar mai ști de ele și `liftOnScroll` ar primi valori greșite.

**De ce pe rădăcină și nu pe fiecare copil:** padding-ul pe părinte împinge **toți** copiii deodată. Aplicat pe fiecare copil în parte, ai repeta codul și ai rata orice view adăugat ulterior.

### Lista și meniul contextual

```java
        listView = findViewById(R.id.listView);

        // Long press shows the popup menu
        listView.setOnItemLongClickListener((parent, view, position, id) -> {
```

**Lambda cu patru parametri** pentru `AdapterView.OnItemLongClickListener`:

| Parametru | Ce e |
|---|---|
| `parent` | `ListView`-ul însuși (aici nu e folosit) |
| `view` | **rândul** apăsat — devine ancora meniului |
| `position` | indexul rândului în listă |
| `id` | id-ul elementului; pentru `ArrayAdapter` e egal cu `position` |

**Nu există `setOnItemClickListener` nicăieri în fișier.** Un tap simplu pe rând nu face nimic. Doar apăsarea lungă reacționează. E o alegere didactică: proiectul demonstrează meniul contextual, nu navigarea.

```java
            PopupMenu popup = new PopupMenu(this, view);   // anchored to the pressed row
            popup.getMenuInflater().inflate(R.menu.list_item_menu, popup.getMenu());
```

**`new PopupMenu(context, anchorView)`** — al doilea argument e ancora. Meniul apare lipit de rândul apăsat, nu în colțul ecranului. Dacă ai pasa `listView` în loc de `view`, ar apărea lângă listă, adică nicăieri util.

**`getMenuInflater()`** vine din `Context` (activitatea). **`inflate(resursă, meniu)`** — al doilea argument e `Menu`-ul **destinație**, obținut cu `popup.getMenu()`. Nu e ca la `setContentView`, unde dai doar resursa.

**De ce `R.menu.list_item_menu` și nu `R.menu.top_app_bar`:** sunt două meniuri diferite, pentru două contexte diferite. `list_item_menu` are „Open / Rename / Delete" — acțiuni pe un rând. `top_app_bar` are „Search / Share / Settings" — acțiuni pe ecran.

```java
            popup.setOnMenuItemClickListener(menuItem -> {
                int itemId = menuItem.getItemId();
                String selected = listView.getItemAtPosition(position).toString();
```

**`position` e capturat din lambda exterioară.** E un parametru de metodă, deci effectively final — Java permite capturarea. Dacă ai încerca să-l modifici între timp (`position++`), compilatorul ar refuza.

**`getItemAtPosition(position)` întoarce un `CharSequence`** — textul din `@array/items`, pentru că `ListView` și-a construit singur un `ArrayAdapter` din atributul `android:entries` din XML. Nu ai scris niciun adapter în cod.

**`.toString()` e redundant** pentru un `String`, dar inofensiv. Devine necesar în momentul în care pui obiecte în listă: acolo `toString()` e contractul de afișare.

```java
                if (itemId == R.id.action_open) {
                    Toast.makeText(this, "Open: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_rename) {
                    Toast.makeText(this, "Rename: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                } else if (itemId == R.id.action_delete) {
                    Toast.makeText(this, "Delete: " + selected, Toast.LENGTH_SHORT).show();
                    return true;
                }
                return false;
```

**`return true` = „am tratat eu click-ul".** Meniul se închide și evenimentul nu mai circulă. **`return false`** = „nu mă interesează" — sistemul încearcă handler-ul implicit.

**Cele trei ramuri sunt identice în afară de text.** La un exercițiu, aici se schimbă ceva: `action_delete` ar scoate elementul din listă, `action_rename` ar deschide un dialog. Structura e pregătită pentru asta — doar `Toast`-ul trebuie înlocuit.

**`Toast.makeText(...).show()`** — două apeluri. `makeText` **construiește**, `show()` **afișează**. Fără `.show()`, nu se întâmplă nimic, fără eroare. E cea mai frecventă greșeală la început.

```java
            popup.show();
            return true;   // true = long press handled, so the normal click doesn't also fire
        });
```

**`popup.show()`** — până aici doar ai configurat meniul. Abia acum apare pe ecran.

**`return true` din listener-ul de long press** — spune listei „apăsarea lungă a fost tratată". Dacă ai întoarce `false`, sistemul ar considera apăsarea lungă netratată și ar putea declanșa și un click normal în urma ei. Rezultatul: meniul apare și, simultan, se execută acțiunea de click.

**Ordinea contează:** `popup.show()` **înainte** de `return true`. Invers nu se poate — `return` încheie lambda.

### Legarea celor trei componente

```java
        drawerLayout = findViewById(R.id.drawerLayout);
        MaterialToolbar toolbar = findViewById(R.id.topAppBar);
        NavigationView navigationView = findViewById(R.id.navigationView);
```

**Trei `findViewById` pentru trei view-uri din XML.** Toate cele trei id-uri trebuie să existe în `activity_main.xml`, altfel primești `null` și un `NullPointerException` la primul apel.

**`toolbar` și `navigationView` sunt locale, `drawerLayout` e câmp.** Inconsecvență reală în cod: toate trei sunt folosite doar în `onCreate`. Merge și cu toate trei locale; merge și cu toate trei câmpuri. Alege o variantă și ține-te de ea.

### Listener-ul sertarului

```java
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
```

**Ce face fiecare ramură:** schimbă **titlul** barei de sus. Conținutul listei rămâne același — cele 20 de „Item N". Aplicația e o demonstrație de navigare, nu una de date.

**`toolbar.setTitle("Inbox")`** suprascrie `app:title="Inbox"` din XML. Valoarea din XML e doar cea inițială; după primul click, titlul vine din cod.

**`nav_settings` e tratat diferit** — un `Toast`, nu un titlu. E singurul element din submeniul „Other", deci nu are sens să schimbe titlul ecranului.

```java
            item.setChecked(true);
            drawerLayout.closeDrawer(GravityCompat.START);
            return true;
        });
```

**`item.setChecked(true)`** — meniul are `android:checkableBehavior="single"` (vezi 26.6), deci se comportă ca un grup de radio butoane: un singur element bifat. Apelul explicit garantează starea după ce sertarul se închide și după redeschidere.

**`closeDrawer(GravityCompat.START)`** — închide sertarul din partea `start`. Trebuie să corespundă cu `android:layout_gravity="start"` din XML. Dacă în XML e `start` și în cod `end`, sertarul rămâne deschis.

**`return true`** — spune `NavigationView` că click-ul a fost tratat. Dacă întorci `false`, elementul nu se marchează vizual ca selectat.

**Fără `closeDrawer`, sertarul rămâne peste ecran** după ce ai ales o opțiune. E primul lucru care lipsește dintr-o implementare grăbită.

### Butonul Back — `OnBackPressedCallback`

```java
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
```

**De ce nu `@Override public void onBackPressed()`:** metoda a fost marcată deprecated din API 33, iar `OnBackPressedDispatcher` e mecanismul oficial. Pe lângă asta, dispatcher-ul permite **mai multe** callback-uri în lanț, fiecare cu prioritatea lui — o singură suprascriere nu poate face asta.

**`new OnBackPressedCallback(true)`** — argumentul e starea inițială: `true` = activ. Un callback dezactivat nu primește evenimente.

**`addCallback(this, ...)`** — primul argument e `LifecycleOwner` (activitatea). Dispatcher-ul ține callback-ul doar cât timp activitatea e în `STARTED`. La `onStop`, callback-ul e scos automat; la `onStart`, revine. Nu trebuie să-l elimini manual.

**Logica, pas cu pas:**

1. S-a apăsat Back.
2. Sertarul e deschis? → închide-l. Sfârșit. Utilizatorul rămâne pe ecran.
3. Sertarul e închis? → `setEnabled(false)`, apoi re-trimite evenimentul.

**De ce `setEnabled(false)` înainte de re-trimitere:** fără el, `onBackPressed()` ar intra din nou în **același** callback, care ar vedea sertarul închis și ar re-trimite evenimentul — recursie infinită, `StackOverflowError`. Dezactivându-te pe tine însuți, lași următorul handler din lanț (cel implicit, care închide activitatea) să primească evenimentul.

**`GravityCompat.START` de trei ori** — `isDrawerOpen`, `closeDrawer`, și în listener-ul de mai jos. Toate trei trebuie să fie identice cu `layout_gravity` din XML.

### Hamburger-ul

```java
        // Hamburger (navigation) icon
        toolbar.setNavigationOnClickListener(v -> {
            drawerLayout.openDrawer(GravityCompat.START);
        });
```

**Ce face:** iconița din stânga barei (cele trei linii) deschide sertarul.

**Iconița există deja în XML** — `app:navigationIcon="@drawable/ic_menu"`. Fără listener, e doar decorativă: se vede, se apasă, nu se întâmplă nimic. Listener-ul e cel care o transformă în buton.

**De ce nu `ActionBarDrawerToggle`:** varianta clasică leagă automat iconița, sertarul și accesibilitatea, dar cere ca toolbar-ul să fie setat ca `ActionBar` (`setSupportActionBar`). Aici toolbar-ul e folosit ca view obișnuit, deci legătura se face manual. E mai puțin cod, dar și mai puțin automatism — de exemplu, iconița nu se animă în săgeată când sertarul e deschis.

### Meniul din toolbar

```java
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
```

**Meniul e deja umflat** — `app:menu="@menu/top_app_bar"` din XML. Aici doar reacționezi la click. Dacă ai fi folosit `setSupportActionBar(toolbar)`, ai fi suprascris `onCreateOptionsMenu` și `onOptionsItemSelected`; cu toolbar-ul ca view simplu, ăsta e cârligul corect.

**`action_settings` are `app:showAsAction="never"`** — de aceea ajunge în meniul „⋮" (overflow), nu pe bară. `action_search` și `action_share` au `ifRoom` — apar direct pe bară dacă încap.

**Comentariul `// open settings` marchează un loc gol.** Ramura afișează un `Toast`, dar intenția era deschiderea unui ecran de setări. E un TODO deghizat.

**`return false` la final e cod mort** — toate cele trei id-uri sunt acoperite mai sus. Rămâne corect: dacă adaugi un al patrulea element în meniu și uiți să-l tratezi, click-ul cade frumos în handler-ul implicit în loc să arunce excepție.

---

## 26.2 `SecondActivity.java` — dialog și Snackbar

**Atenție înainte de orice:** `SecondActivity` e declarată în manifest, dar **nu e pornită nicăieri**. Nu există `Intent` în `MainActivity` — doar importul nefolosit. Ecranul e complet funcțional dacă îl lansezi manual (Run → Edit Configurations → Launch: Specified Activity), dar în aplicația livrată e inaccesibil. E un ecran de laborator rămas nelegat, nu un bug de compilare.

### Importurile

```java
package ro.ase.ie.dma03;

import android.app.AlertDialog;          // ← ATENȚIE: versiunea de PLATFORMĂ, nu androidx.appcompat.app.AlertDialog
import android.content.DialogInterface;  // interfața pentru butoanele dialogului
import android.os.Bundle;
import android.util.DisplayMetrics;      // densitatea ecranului (pentru conversia dp→px)
import android.util.TypedValue;          // applyDimension: dp → pixeli
import android.view.View;                // tipul parametrului din btnClick
import android.view.ViewGroup;           // clasa de bază pentru LayoutParams
import android.widget.Button;
import android.widget.LinearLayout;      // containerul în care adaugi butoane
import android.widget.Toast;
```

**`android.app.AlertDialog` vs `androidx.appcompat.app.AlertDialog`** — diferența se vede pe ecran. Varianta de platformă folosește tema de dialog a sistemului; varianta AppCompat folosește tema aplicației. Cu `Theme.Material3.DayNight`, dialogul din acest fișier va arăta ca un dialog de sistem, nu ca unul Material 3. Funcțional e identic; vizual e inconsistent.

**`DialogInterface`** e importat separat pentru că `OnClickListener`-ul dialogului e o interfață imbricată în ea: `DialogInterface.OnClickListener`.

```java
import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.snackbar.Snackbar;   // bara de jos cu acțiune
```

**`Snackbar` vine din Material**, nu din platformă. De aceea `SecondActivity` are nevoie de `libs.material` în dependențe — la fel ca `MainActivity` pentru toolbar.

### Câmpul și `onCreate`

```java
public class SecondActivity extends AppCompatActivity {

    LinearLayout inflatedLayout;   // fără modificator = package-private; e rădăcina din activity_second.xml
```

**Fără `private`** — inconsecvență față de `MainActivity`, unde câmpurile sunt `private`. Nu strică nimic (suntem în același pachet), dar convenția e `private`.

**De ce câmp și nu local:** e folosit în `btnClick`, în acțiunea Snackbar-ului și în `addButton`. Trei metode, un singur câmp.

```java
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_second);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        inflatedLayout = findViewById(R.id.main);
    }
```

**Blocul de insets e identic cu cel din `MainActivity`** — copiat. Aici `R.id.main` e pe `LinearLayout`-ul rădăcină, nu pe un `CoordinatorLayout`. Funcționează la fel: padding pe rădăcină, copiii se mută în zona sigură.

**`inflatedLayout = findViewById(R.id.main)` e ultima linie** — după `setContentView`. Dacă ar fi înainte, ar primi `null` și primul `addView` ar arunca `NullPointerException`.

**Numele `inflatedLayout` e înșelător:** nu e un layout „umflat" la runtime, e layout-ul din XML. Umflarea a făcut-o `setContentView`. Numele sugerează intenția — un container în care se adaugă view-uri — nu mecanismul.

### `btnClick` — contractul cu `android:onClick`

```java
    public void btnClick(View view) {
```

**Semnătura e impusă de XML.** În `activity_second.xml`, butonul are `android:onClick="btnClick"`. Android caută la runtime, prin reflecție, o metodă `public void btnClick(View)` în contextul activității.

**Consecința:** dacă o faci `private`, sau îi schimbi parametrul în `Object`, sau o redenumești fără să modifici XML-ul, **compilarea trece**. Eroarea apare la click: `IllegalStateException: Could not find method btnClick(View) in a parent or ancestor Context`. Unul dintre puținele locuri din Android unde greșeala nu se vede la build.

**`view` e butonul apăsat.** Aici nu e folosit — codul nu are nevoie să știe care buton a fost.

### Dialogul

```java
        AlertDialog.Builder builder = new AlertDialog.Builder(SecondActivity.this);
        builder.setTitle("Add new control ...")
                .setMessage("Are you sure you want to add a new control?")
                .setCancelable(true)
```

**`AlertDialog.Builder`** — construiește dialogul bucată cu bucată. Fiecare setter întoarce **același** builder, de aceea se pot înlănțui. Lanțul se încheie cu `setNegativeButton`, iar `builder.show()` de la finalul metodei afișează dialogul.

**`SecondActivity.this` și nu `this`:** în interiorul unui listener, `this` ar însemna listener-ul. `SecondActivity.this` e sintaxa pentru instanța clasei exterioare. Aici suntem încă în corpul metodei, deci `this` ar fi mers — dar forma explicită e o obișnuință bună, pentru că în doi pași vei fi în `onClick`.

**`setCancelable(true)` e valoarea implicită.** Scrisă explicit, documentează comportamentul: se poate închide cu Back sau cu tap în afară. Consecința: dacă utilizatorul închide așa, **niciun** buton nu se execută — nici „Do it!", nici „Cancel". Dacă ai nevoie de o acțiune garantată, ai nevoie de `setOnCancelListener`.

```java
                .setPositiveButton("Do it!", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        int id = addButton();
```

**Butonul pozitiv** e acțiunea principală — apare în dreapta, colorat. Textul „Do it!" e explicit; „OK" ar fi vag.

**`int id = addButton();`** — creează butonul **înainte** de Snackbar, ca să ai ce șterge. Id-ul returnat e singura legătură cu butonul nou: nu ai o referință la obiect, doar un număr.

**`which`** e `DialogInterface.BUTTON_POSITIVE` aici. Nu e folosit — fiecare buton are listener-ul lui.

```java
                        Snackbar.make(SecondActivity.this, inflatedLayout, "Cancel previous action.", Snackbar.LENGTH_LONG)
                                .setAction("Cancel", new View.OnClickListener() {
                                    @Override
                                    public void onClick(View v) {
                                        Button viewById = inflatedLayout.findViewById(id);
                                        inflatedLayout.removeView(viewById);
                                    }
                                }).show();
```

**`Snackbar.make(context, view, text, duration)`** — patru argumente:

| Argument | Rol |
|---|---|
| `SecondActivity.this` | contextul, pentru temă și resurse |
| `inflatedLayout` | view-ul de referință; Snackbar-ul caută un părinte potrivit și apare jos |
| `"Cancel previous action."` | textul |
| `Snackbar.LENGTH_LONG` | ~10 secunde (`LENGTH_SHORT` = ~4 s) |

**`inflatedLayout` e un `LinearLayout` simplu, nu un `CoordinatorLayout`.** Snackbar-ul funcționează, dar fără beneficiile CoordinatorLayout: nu se poate glisa pentru a-l închide și nu împinge automat un FAB în sus. Pentru un ecran de demonstrație e suficient.

**`setAction("Cancel", listener)`** — adaugă butonul din dreapta. Textul e scurt cu intenție: un „Undo last action" ar înghesui mesajul pe ecrane mici.

**`id` e capturat din lambda exterioară.** E o variabilă locală `int`, atribuită o singură dată → effectively final → poate fi prinsă. Dacă ai scrie `id++` între declarație și folosire, compilatorul ar refuza captura.

**`inflatedLayout.findViewById(id)`** — funcționează pentru că butonul a primit un id explicit cu `setId(counter)`. Fără `setId`, `findViewById` ar returna `null` și `removeView(null)` ar arunca `NullPointerException`.

**`removeView(viewById)`** — scoate view-ul din container. Butonul dispare de pe ecran; obiectul rămâne în memorie până la următoarea colectare de gunoi.

**`.show()` la final** — fără el, Snackbar-ul e construit și niciodată afișat. Aceeași capcană ca la `Toast`.

**Momentul afișării:** Snackbar-ul e creat **în** `onClick`-ul butonului pozitiv, deci apare după ce dialogul s-a închis. Dacă l-ai crea înainte de `builder.show()`, ar apărea sub dialog.

```java
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        Toast.makeText(SecondActivity.this, "Object creation cancelled", Toast.LENGTH_LONG).show();
                    }
                });
        builder.show();
```

**Butonul negativ** — anulare. Doar un `Toast`, nicio modificare de stare.

**`builder.show()`** — creează dialogul și îl afișează. Echivalent cu `builder.create().show()`. Se apelează **o singură dată**, după ce lanțul de settere s-a încheiat.

**De ce `show()` e separat și nu în lanț:** pentru că lanțul se termină cu `;` după `setNegativeButton`, iar `show()` e o metodă a builder-ului, nu un setter. Ar fi mers și `builder.setTitle(...).show()`, dar codul alege forma explicită.

### `addButton` — crearea unui view din cod

```java
    int counter = 0;
    public int addButton()
    {
```

**Câmpul `counter` e declarat între metode** — legal în Java, neobișnuit ca stil. Are două roluri simultan: generator de id-uri și sursă pentru etichetă.

**`public int addButton()`** — public pentru că e apelată din `onClick`, dar și pentru că ar putea fi apelată din XML. Returnează id-ul, ca apelantul să poată găsi butonul mai târziu.

**Brace pe linia următoare** — stil diferit de restul fișierului (K&R). Cosmetic, fără efect.

```java
        DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
        int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50,
                displayMetrics);
```

**Cod mort.** `hPixels` e calculat și **niciodată folosit**. Intenția era probabil `newBtn.setHeight(hPixels)` sau un `LayoutParams` cu înălțime de 50dp. Compilatorul dă un warning (`variable hPixels is never used`), nu o eroare.

**Ce face totuși, util de știut:** `TypedValue.applyDimension(COMPLEX_UNIT_DIP, 50, metrics)` convertește 50dp în pixeli fizici, folosind densitatea ecranului. La 3x, întoarce 150. E conversia corectă atunci când ai nevoie de pixeli într-un calcul — de exemplu pentru animații sau pentru `setPadding`.

**De ce nu `50 * getResources().getDisplayMetrics().density`:** e echivalent, dar `applyDimension` tratează și `SP`, `PT`, `MM`, `IN` cu aceeași semnătură. O funcție, toate unitățile.

```java
        Button newBtn = new Button(SecondActivity.this);
        newBtn.setText("Button_" + (++counter));
        newBtn.setId(counter);
```

**`new Button(Context)`** — constructorul cere un **context tematizat**. `SecondActivity.this` are tema `Theme.DMA03`. Dacă ai pasa `getApplicationContext()`, butonul ar pierde tema și, pe unele atribute Material, ar arunca excepție la inflate.

**`++counter` (pre-increment)** — întâi incrementează, apoi folosește. Primul buton e `Button_1`, iar `counter` devine 1. Cu `counter++` (post-increment), primul ar fi `Button_0` și ai avea un buton cu id 0.

**`setId(counter)`** — id-uri 1, 2, 3... Id-urile de resursă sunt în zona `0x7f......`, deci nu se ciocnesc. `View.NO_ID` e `-1`, deci 0 ar fi fost o valoare nefericită — încă un motiv pentru pre-increment.

**Fără `setId`, butonul există dar e imposibil de găsit** cu `findViewById`. Ar apărea pe ecran și nu l-ai mai putea șterge.

```java
        ViewGroup.LayoutParams layoutParams =
                new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT);
        newBtn.setLayoutParams(layoutParams);
```

**`ViewGroup.LayoutParams`** — clasa de bază. `LinearLayout` o acceptă. Dacă ai nevoie de `layout_weight`, trebuie `LinearLayout.LayoutParams` — clasa de bază nu are acel câmp.

**`MATCH_PARENT` pe lățime** — butonul umple containerul, ca butonul original din XML. **`WRAP_CONTENT` pe înălțime** — cât are nevoie textul.

**Fără `setLayoutParams`**, `addView` aplică valorile implicite ale containerului — tot `MATCH_PARENT`/`WRAP_CONTENT` pentru `LinearLayout`, deci practic același rezultat. Explicit e mai sigur când containerul se schimbă.

```java
        inflatedLayout.addView(newBtn);
        return counter;
    }
}
```

**`addView`** — adaugă la sfârșitul `LinearLayout`-ului vertical, deci sub butonul existent. Al doilea buton apare sub primul, al treilea sub al doilea.

**`return counter`** — id-ul tocmai atribuit. Apelantul îl păstrează în `id` și îl folosește în acțiunea Snackbar-ului.

**Ce se întâmplă la rotire:** `counter` se resetează la 0, iar butoanele adăugate dispar — nu sunt salvate în `savedInstanceState`. La rotire, activitatea e recreată, `onCreate` rulează din nou, iar `activity_second.xml` are din nou un singur buton.

---

## 26.3 `AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
```

**`xmlns:tools` e declarat, dar nefolosit** — niciun atribut `tools:*` în fișier. Rămășiță din șablon. Nu strică, dar lint-ul îl semnalează.

**Fără `<uses-permission>`** — aplicația nu are nevoie de nimic. Nici internet, nici stocare. Toate datele sunt în memorie.

```xml
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DMA03">
```

**`allowBackup="true"`** — aplicația participă la backup-ul automat al sistemului. Pentru o aplicație fără date persistente, e irelevant.

**`dataExtractionRules`** (API 31+) și **`fullBackupContent`** (sub API 31) — fișiere care spun ce se salvează. Ambele trimit la `res/xml/`. Dacă lipsește unul, build-ul trece, dar lint-ul avertizează.

**`supportsRtl="true"`** — interfața se oglindește în limbile RTL. De aici importanța `GravityCompat.START` în loc de `Gravity.LEFT`.

**`android:theme="@style/Theme.DMA03"`** — tema se aplică **tuturor** activităților care nu au `android:theme` propriu. Ambele o moștenesc.

```xml
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
```

**`.MainActivity`** — punctul de la început înseamnă „în pachetul aplicației", adică `ro.ase.ie.dma03.MainActivity`. Forma completă ar fi identică.

**`android:exported="true"`** — obligatoriu pentru componenta cu `intent-filter` de la API 31 încoace. Fără el, build-ul **eșuează**. E singura activitate care poate fi pornită din afară — de lansator.

**`intent-filter` cu `MAIN` + `LAUNCHER`** — perechea care creează iconița în lansator. `MAIN` = punctul de intrare, `LAUNCHER` = apare în lista de aplicații. Ambele sunt necesare.

**`windowSoftInputMode="adjustResize"`** — când apare tastatura, fereastra se micșorează, nu se panoramează. Aici nu există niciun `EditText`, deci atributul e inutil — dar e inofensiv și pregătește terenul pentru un ecran cu câmpuri.

```xml
        <activity
            android:name=".SecondActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
    </application>

</manifest>
```

**`android:exported="false"`** — nicio aplicație din afară nu o poate porni. Corect: e un ecran intern.

**Fără `intent-filter`** — nu are punct de intrare. Nu apare în lansator.

**Aici e dovada finală:** `SecondActivity` e declarată, dar **nimic nu o pornește**. `MainActivity` nu conține niciun `Intent`. Ecranul e un laborator lăsat nelegat — cod complet, accesibil doar dacă îl lansezi manual din Android Studio.

**Ce ar fi trebuit pentru a o lega:** în `MainActivity`, un `startActivity(new Intent(this, SecondActivity.class))` — de exemplu în ramura `nav_settings` sau pe `action_open` din meniul contextual. Importul `android.content.Intent` există deja, semn că intenția a fost acolo.

---

## 26.4 `activity_main.xml` — ierarhia de containere

### Arborele, pe niveluri

```
DrawerLayout (id=drawerLayout)                    ← rădăcina; exact 2 copii
├── CoordinatorLayout (id=main)                   ← panoul de conținut (primul copil)
│   ├── AppBarLayout
│   │   └── MaterialToolbar (id=topAppBar)
│   └── FrameLayout
│       └── ListView (id=listView)
└── NavigationView (id=navigationView)            ← sertarul (al doilea copil)
```

**Regula `DrawerLayout`:** exact **doi** copii direcți. Primul e conținutul, al doilea e sertarul. Al doilea **trebuie** să aibă `android:layout_gravity="start"` (sau `end`) — altfel e tratat ca al doilea panou de conținut și nu se deschide niciodată.

**De ce `CoordinatorLayout` și nu direct `FrameLayout`:** coordonează `AppBarLayout` cu lista — efectul de `liftOnScroll` are nevoie de el. Fără `CoordinatorLayout`, bara nu știe când lista se derulează.

**De ce încă un `FrameLayout` între `CoordinatorLayout` și `ListView`:** `CoordinatorLayout` are nevoie de un copil căruia să-i aplice `layout_behavior`. `ListView` ar putea fi el însuși acel copil, dar `FrameLayout`-ul izolează comportamentul și lasă loc pentru un FAB sau un `TextView` de „listă goală" în viitor.

### Rădăcina

```xml
<?xml version="1.0" encoding="utf-8"?>

<!-- DrawerLayout: exact 2 copii direcți — conținutul și sertarul -->
<androidx.drawerlayout.widget.DrawerLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/drawerLayout"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
```

**`@+id/drawerLayout`** — semnul `+` înseamnă „creează id-ul dacă nu există". Prima apariție într-un fișier XML trebuie să aibă `+`; în cod se folosește `R.id.drawerLayout` fără.

**`match_parent` × 2** — containerul acoperă tot ecranul, inclusiv zonele de sub bare. `EdgeToEdge` are sens doar așa: conținutul se întinde, iar padding-ul de insets îl ține în zona sigură.

**`xmlns:app`** — namespace-ul pentru atributele definite de biblioteci (`app:menu`, `app:title`). Fără el, `app:menu` nu e recunoscut.

### Panoul de conținut

```xml
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
```

**`xmlns:android` și `xmlns:app` sunt declarate din nou** — deși sunt deja pe `DrawerLayout`. Redundant, dar legal: namespace-urile se moștenesc, iar redeclararea e ignorată. Nu strică nimic; unii editori le adaugă automat.

**`@+id/main`** — de aici vine `findViewById(R.id.main)` din cod, pentru insets. Id-ul e pe **conținut**, nu pe `DrawerLayout` — deci padding-ul de insets nu atinge sertarul.

### Bara de sus

```xml
    <com.google.android.material.appbar.AppBarLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#6750A4"
        app:liftOnScroll="true"
        app:liftOnScrollColor="#4F378B"
        app:liftOnScrollTargetViewId="@id/listView">
```

**`#6750A4`** — movul de bază Material 3, **hardcodat**. Nu se adaptează la dark mode: în întuneric bara rămâne mov deschis. Corect ar fi `?attr/colorPrimary`.

**`liftOnScroll="true"`** — când lista se derulează, bara își schimbă culoarea în `liftOnScrollColor` (`#4F378B`, tot hardcodat) și primește o umbră. E efectul „app bar care se ridică".

**`liftOnScrollTargetViewId="@id/listView"`** — îi spune lui `AppBarLayout` **care** view derulează. Fără el, `AppBarLayout` caută automat un view derulabil printre frați; cum `ListView`-ul e ascuns în `FrameLayout`, nu-l găsește și efectul nu se declanșează.

```xml
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
```

**`?attr/actionBarSize`** — înălțimea standard a barei (56dp). Nu hardcoda `56dp`: pe unele teme și orientări diferă.

**`android:background="@android:color/transparent"`** — toolbar-ul e transparent, culoarea vine de la `AppBarLayout`. Altfel ai două straturi de mov, iar `liftOnScroll` ar schimba doar unul.

**`app:title="Inbox"`** — titlul inițial. Codul îl suprascrie cu `toolbar.setTitle(...)` la click pe sertar.

**`app:titleTextColor` și `app:navigationIconTint`** — alb. Fără ele, textul ar fi negru pe mov în light theme. `navigationIconTint` e necesar separat pentru că iconița vectorială are culoarea proprie (`#000000` în `ic_menu.xml`).

**`app:navigationIcon="@drawable/ic_menu"`** — cele trei linii. Desenul e un `VectorDrawable` de 24dp; culoarea reală o dă `navigationIconTint`.

**`app:menu="@menu/top_app_bar"`** — umflă meniul direct din XML. De aceea `onCreate` nu are `onCreateOptionsMenu`.

**`app:layout_scrollFlags="scroll|enterAlways|snap"`** — comportamentul la derulare:

| Flag | Efect |
|---|---|
| `scroll` | bara iese din ecran când derulezi în jos |
| `enterAlways` | revine imediat ce derulezi în sus, oriunde ai fi în listă |
| `snap` | se oprește complet vizibilă sau complet ascunsă, niciodată pe jumătate |

**`app:theme="@style/ThemeOverlay.Material3.Dark.ActionBar"`** — aplică o temă întunecată **doar** pe toolbar, ca textul și iconițele să fie deschise. Alternativa ar fi fost să setezi fiecare culoare în parte.

### Lista

```xml
    </com.google.android.material.appbar.AppBarLayout>

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
```

**`app:layout_behavior="@string/appbar_scrolling_view_behavior"`** — fără el, `FrameLayout`-ul ar fi desenat de la `y=0`, adică **sub** bară, iar primele rânduri ar fi acoperite. Comportamentul îl împinge în jos exact cu înălțimea barei.

**`android:entries="@array/items"`** — `ListView` își construiește singur un `ArrayAdapter` din cele 20 de șiruri din `strings.xml`. **Nu există niciun adapter în cod** — de aceea `listView.getItemAtPosition(position)` întoarce direct un `String`.

**`android:nestedScrollingEnabled="true"`** — permite listei să transmită evenimentele de derulare părintelui (`CoordinatorLayout`), ca `liftOnScroll` să funcționeze. Fără el, lista „înghite" derularea și bara nu reacționează.

**`match_parent` pe înălțime** — lista umple tot spațiul rămas după bară. `wrap_content` ar fi lăsat-o să crească la infinit.

### Sertarul

```xml
</androidx.coordinatorlayout.widget.CoordinatorLayout>

    <com.google.android.material.navigation.NavigationView
        android:id="@+id/navigationView"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        app:menu="@menu/drawer_menu" />

</androidx.drawerlayout.widget.DrawerLayout>
```

**`layout_width="wrap_content"`** — sertarul are lățimea conținutului, nu a ecranului. `match_parent` ar acoperi tot și nu ar mai părea sertar. Material recomandă ~280dp; `wrap_content` se apropie.

**`layout_height="match_parent"`** — pe toată înălțimea.

**`android:layout_gravity="start"`** — **atributul care face diferența.** Fără el, `NavigationView` e tratat ca al doilea panou de conținut și nu se deschide niciodată. Trebuie să fie identic cu `GravityCompat.START` din cod.

**`app:menu="@menu/drawer_menu"`** — conținutul sertarului vine din XML. `NavigationView` îl umflă singur; codul doar ascultă click-urile.

**`NavigationView` își aplică singură insets-urile** — extinde `ScrimInsetsFrameLayout`, care adaugă padding pentru status bar. De aceea nu are nevoie de blocul de insets din cod.

---

## 26.5 `activity_second.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".SecondActivity">
```

**`LinearLayout` vertical** — copiii se stivuiesc de sus în jos. De asta butoanele adăugate din cod apar unul sub altul, nu peste.

**`android:id="@+id/main"`** — folosit de două ori în cod: pentru insets și pentru `inflatedLayout`. Id-ul se repetă față de `activity_main.xml`, dar nu e o problemă: cele două layout-uri nu coexistă niciodată în același arbore.

**`xmlns:app` e declarat, dar nefolosit** — niciun atribut `app:*` în fișier. Rămășiță din șablon, semnalată de lint.

**`tools:context=".SecondActivity"`** — doar pentru preview-ul din Android Studio: îi spune editorului ce temă și ce clasă să folosească. Eliminat la build, nu ajunge în APK.

```xml
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:onClick="btnClick"
        android:text="Button" />
</LinearLayout>
```

**`android:onClick="btnClick"`** — leagă butonul de metoda `btnClick(View)` din activitate, prin reflecție. **Nu există `setOnClickListener` în cod** — toată legătura e aici.

**De ce funcționează fără cod:** la click, Android caută metoda în contextul activității. Dacă nu o găsește, excepția apare **la runtime**, nu la compilare.

**`android:id="@+id/button"` nu e folosit nicăieri** — nici în cod, nici în alt XML. E util doar dacă vrei să-l referențiezi mai târziu. Butoanele create din cod primesc id-uri numerice (1, 2, 3...), nu id-uri de resursă.

**`match_parent` pe lățime** — butonul umple ecranul. Butoanele adăugate din cod primesc același `MATCH_PARENT`, deci arată identic.

**Fără `padding` pe `LinearLayout`** — butoanele ating marginile ecranului. Cosmetic, nu funcțional.

---

## 26.6 Meniurile (`res/menu/*.xml`)

Trei fișiere, trei scopuri diferite. Toate sunt umflate din XML — niciunul nu e construit în cod.

### `drawer_menu.xml` — conținutul sertarului

```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- checkableBehavior="single" = radio group: un singur element bifat -->
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
```

**`android:checkableBehavior="single"`** — grupul se comportă ca un radio group: când selectezi „Sent", „Inbox" se debifează automat. Valorile posibile: `single`, `all`, `none`.

**`android:checked="true"` pe `nav_inbox`** — starea inițială. Fără ea, la prima deschidere niciun element nu e bifat, deși toolbar-ul afișează „Inbox".

**`android:icon`** — fiecare element are o iconiță vectorială din `res/drawable/`. `NavigationView` le afișează la stânga titlului.

**`android:title` e text literal, nu `@string/...`** — funcționează, dar nu se traduce. Pentru o aplicație reală, toate titlurile ar trebui să fie în `strings.xml`.

```xml
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

**Un `<item>` fără id, care conține un `<menu>`** — trucul pentru un **subtitlu de secțiune**. „Other" apare ca etichetă gri, iar „Settings" dedesubt, separat de grupul principal.

**De ce `nav_settings` e în afara grupului** — nu face parte din navigarea principală (Inbox/Sent/Trash), ci e o setare. Separarea vizuală sugerează diferența.

**Consecința în cod:** `nav_settings` nu e checkable, deci `item.setChecked(true)` nu are efect vizual pe el. Ramura lui afișează un `Toast`.

### `list_item_menu.xml` — meniul contextual

```xml
<?xml version="1.0" encoding="utf-8"?>
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

**Minimalism deliberat:** fără iconițe, fără `showAsAction`. Un `PopupMenu` nu are bară — toate elementele apar în listă, deci `showAsAction` ar fi ignorat.

**Cele trei id-uri sunt exact cele verificate în `MainActivity`:** `action_open`, `action_rename`, `action_delete`. Dacă redenumești unul în XML fără să modifici codul, ramura respectivă nu se mai execută — și nu primești eroare de compilare, doar un `if` care nu mai intră niciodată.

**Fără `android:icon`** — un meniu contextual scurt se citește mai repede fără iconițe. Cu iconițe, `PopupMenu` le afișează, dar ocupă mai mult spațiu.

### `top_app_bar.xml` — meniul barei

```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">

    <item
        android:id="@+id/action_search"
        android:icon="@drawable/ic_search"
        android:title="Search"
        app:showAsAction="ifRoom" />

    <item
        android:id="@+id/action_share"
        android:icon="@drawable/ic_share"
        android:title="Share"
        app:showAsAction="ifRoom" />

    <!-- Items with "never" go into the ⋮ overflow menu -->
    <item
        android:id="@+id/action_settings"
        android:title="Settings"
        app:showAsAction="never" />
</menu>
```

**`app:showAsAction` și nu `android:showAsAction`** — atributul e definit de biblioteca AppCompat, nu de platformă. Cu `android:` ar fi ignorat silențios pe versiunile noi.

**Cele trei valori care contează:**

| Valoare | Efect |
|---|---|
| `ifRoom` | apare pe bară dacă încape; altfel în overflow |
| `never` | mereu în meniul „⋮" |
| `always` | mereu pe bară, chiar dacă înghesuie titlul |

**`action_search` și `action_share` au `ifRoom`** — pe un telefon îngust, unul dintre ele poate cădea în overflow. Pe tabletă apar amândouă.

**`action_settings` are `never` și nu are iconiță** — în overflow, textul e suficient. Elementele cu iconiță în overflow își afișează iconița; cele fără, doar textul.

**Ordinea în XML = ordinea pe bară**, de la stânga la dreapta (după iconița de navigare). În overflow, ordinea se păstrează.

**Titlurile sunt literale**, nu resurse — aceeași observație ca la `drawer_menu.xml`.

---

## 26.7 Fluxul complet

### Pornirea

```
LANSATOR → MainActivity
  onCreate
    ├── super.onCreate
    ├── EdgeToEdge.enable
    ├── setContentView(activity_main)
    │     └── DrawerLayout
    │           ├── CoordinatorLayout (id=main)
    │           │     ├── AppBarLayout → MaterialToolbar (id=topAppBar)
    │           │     └── FrameLayout → ListView (id=listView)
    │           │           └── adapter automat din @array/items → 20 rânduri
    │           └── NavigationView (id=navigationView, gravity=start)
    ├── insets pe R.id.main        → padding pentru barele de sistem
    ├── listView = findViewById
    ├── listView.setOnItemLongClickListener   → PopupMenu
    ├── drawerLayout / toolbar / navigationView = findViewById
    ├── navigationView.setNavigationItemSelectedListener
    ├── getOnBackPressedDispatcher().addCallback
    ├── toolbar.setNavigationOnClickListener
    └── toolbar.setOnMenuItemClickListener
```

**Nicio instrucțiune de stare** — nu se citește nimic din `savedInstanceState`, nu se salvează nimic. La rotire, totul revine la starea inițială.

### Deschiderea sertarului

```
APASĂ HAMBURGER
  toolbar.setNavigationOnClickListener
    └── drawerLayout.openDrawer(GravityCompat.START)
          └── NavigationView glisează din stânga peste conținut

ALEGE „Sent"
  navigationView.setNavigationItemSelectedListener(item)
    ├── id == R.id.nav_sent → toolbar.setTitle("Sent")
    ├── item.setChecked(true)              → „Inbox" se debifează (checkableBehavior=single)
    ├── drawerLayout.closeDrawer(START)    → sertarul se retrage
    └── return true                        → click tratat

EFECT: titlul barei se schimbă. Lista rămâne aceeași — 20 de „Item N".
```

### Meniul contextual

```
APĂSARE LUNGĂ PE RÂNDUL 5
  listView.setOnItemLongClickListener(parent, view, position=5, id=5)
    ├── new PopupMenu(this, view)          → ancorat pe rândul apăsat
    ├── inflate(R.menu.list_item_menu)     → Open / Rename / Delete
    ├── popup.show()
    └── return true                        → fără click normal după

ALEGE „Delete"
  popup.setOnMenuItemClickListener(menuItem)
    ├── selected = listView.getItemAtPosition(5).toString()   → "Item 6"
    ├── id == R.id.action_delete
    ├── Toast "Delete: Item 6"
    └── return true                        → meniul se închide
```

**Atenție la index:** `position` e 0-based, deci rândul 5 afișează „Item 6". Nu e un bug — e convenția Java.

### Butonul Back

```
SERTAR DESCHIS + BACK
  OnBackPressedCallback.handleOnBackPressed()
    ├── isDrawerOpen(START) == true
    └── closeDrawer(START)                 → rămâi pe ecran

SERTAR ÎNCHIS + BACK
  OnBackPressedCallback.handleOnBackPressed()
    ├── isDrawerOpen(START) == false
    ├── setEnabled(false)                  → te dezactivezi, ca să nu te reapelezi
    └── getOnBackPressedDispatcher().onBackPressed()
          └── handler-ul implicit → finish() → aplicația se închide
```

### Ecranul nelegat

```
MainActivity ──X──> SecondActivity
                    (niciun Intent nicăieri)

Dacă îl lansezi manual:
  SecondActivity.onCreate
    ├── setContentView(activity_second)    → LinearLayout vertical + un Button
    ├── insets pe R.id.main
    └── inflatedLayout = findViewById(R.id.main)

  CLICK pe „Button"
    └── android:onClick → btnClick(View)
          └── AlertDialog.Builder
                ├── Title: "Add new control ..."
                ├── Message: "Are you sure you want to add a new control?"
                ├── Cancelable: true
                ├── Positive „Do it!"
                │     ├── id = addButton()          → Button_1, id=1, adăugat în layout
                │     └── Snackbar LENGTH_LONG „Cancel previous action."
                │           └── action „Cancel"
                │                 ├── findViewById(id)
                │                 └── removeView(...)   → butonul dispare
                ├── Negative „Cancel"
                │     └── Toast "Object creation cancelled"
                └── builder.show()
```

**Tabloul de ansamblu:** `MainActivity` demonstrează navigarea (drawer + toolbar + meniu contextual + Back). `SecondActivity` demonstrează dialogul și manipularea dinamică a arborelui de view-uri. Sunt două laboratoare separate, lipite în același proiect.

---

## 26.8 Ce să reții

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
5. **Scoți `liftOnScrollTargetViewId`** — bara nu mai reacționează la derulare.
6. **Scoți `setId` din `addButton`** — Snackbar-ul nu mai găsește butonul de șters.
7. **Faci `btnClick` privată** — compilează, crapă la click.

---

## Rezumat capitol 26

- `MainActivity` are un singur `onCreate` cu șapte responsabilități; ordinea `super` → `EdgeToEdge` → `setContentView` → `findViewById` e obligatorie.
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
