# Capitolul 14 — DMA03: navigare, meniuri și dialoguri

**Obiectiv:** să înțelegi structura `DrawerLayout` + `NavigationView` + `MaterialToolbar`, meniurile (`PopupMenu` pe rând, meniu în toolbar), gestionarea butonului Back și dialogurile cu `AlertDialog` / `Snackbar`.

**Timp estimat:** 50–65 min.

**Sursa:** `DMA03/` la commitul `d719ffc` — 40 de fișiere, primele commituri `42baa90`, `858f7ea`, `b7633cd` (2026-10-21).

> **De ce contează:** `G1097` nu are meniuri și nici drawer. Dar la test, întrebări de tipul „cum faci un meniu lateral", „ce diferență e între `PopupMenu` și `NavigationView`" sau „cum interceptezi Back" sunt frecvente. Aici ai implementarea completă.

---

## Pasul 14.1 — Structura layout-ului cu drawer

### De ce

Un meniu lateral nu e un widget peste conținut. E o **ierarhie de containere** cu roluri precise.

### Cum

`activity_main.xml`:

```xml
<androidx.drawerlayout.widget.DrawerLayout
    android:id="@+id/drawerLayout"
    ...>

    <androidx.coordinatorlayout.widget.CoordinatorLayout
        android:id="@+id/main"
        ...>

        <com.google.android.material.appbar.AppBarLayout ...>
            <com.google.android.material.appbar.MaterialToolbar
                android:id="@+id/topAppBar" ... />
        </com.google.android.material.appbar.AppBarLayout>

        <FrameLayout ...>
            <ListView
                android:id="@+id/listView" ... />
        </FrameLayout>

    </androidx.coordinatorlayout.widget.CoordinatorLayout>

    <com.google.android.material.navigation.NavigationView
        android:id="@+id/navigationView" ... />

</androidx.drawerlayout.widget.DrawerLayout>
```

### Arborele, pe niveluri

```
DrawerLayout                      ← containerul care știe de drawer
├── CoordinatorLayout  (id=main)  ← conținutul principal (primul copil = ecranul)
│   ├── AppBarLayout
│   │   └── MaterialToolbar       ← bara de sus cu titlu, hamburger, meniu
│   └── FrameLayout
│       └── ListView              ← conținutul
└── NavigationView                ← sertarul (al doilea copil = drawer)
```

### Regula `DrawerLayout`

> `DrawerLayout` are **maximum două** copii direcți:
> 1. **conținutul** (primul copil) — orice `ViewGroup`;
> 2. **sertarul** (al doilea copil) — de obicei `NavigationView`.
>
> Sertarul trebuie să declare `android:layout_gravity="start"` (sau `end`).

Dacă pui un al treilea copil, build-ul nu pică, dar comportamentul devine imprevizibil.

### De ce `CoordinatorLayout` și nu direct `FrameLayout`

`CoordinatorLayout` e containerul care știe să coordoneze `AppBarLayout` cu conținutul: la scroll, bara se poate ascunde sau plia. Dacă pui `LinearLayout`, bara rămâne fixă și pierzi comportamentul Material.

### De ce `FrameLayout` între `CoordinatorLayout` și `ListView`

`CoordinatorLayout` are nevoie de un `Behavior` pe copil ca să știe cum să reacționeze la scroll. `ListView` nu are unul implicit, dar îmbrăcat într-un `FrameLayout` cu `app:layout_behavior` funcționează.

### Exercițiu 14.1

**Cerință:** ce se întâmplă dacă muți `NavigationView` **înaintea** `CoordinatorLayout` în XML?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai inversat ordinea celor doi copii ai `DrawerLayout`.

**Ce se întâmplă:** `DrawerLayout` tratează **primul** copil ca fiind conținutul. Deci `NavigationView` devine „ecranul", iar `CoordinatorLayout` devine sertarul. Rezultat: vezi meniul ca pagină principală, iar la swipe apare lista.

**De ce:** `DrawerLayout` nu distinge după tip, ci după poziție. Primul copil = conținut, ceilalți = drawere.

**De reținut:**
1. Ordinea în XML **contează** la `DrawerLayout`, exact ca la `FrameLayout` (capitolul 03).
2. `android:layout_gravity="start"` pe `NavigationView` spune unde apare sertarul.
3. Un singur conținut, unul sau două drawere (start + end).

**Unde revine:** în `G1097`, `FrameLayout` din `activity_main.xml` are aceeași regulă de ordine: `ListView` primul, FAB al doilea (capitolul 03, pasul 3.5).

</details>

---

## Pasul 14.2 — `MaterialToolbar`: hamburger și meniu

### De ce

`MaterialToolbar` e bara de sus. Are trei zone: navigare (stânga), titlu (centru/stânga), acțiuni (dreapta).

### Cum — meniul din toolbar

`res/menu/top_app_bar.xml`:

```xml
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

### `app:showAsAction` — cele trei valori

| Valoare | Efect |
|---|---|
| `ifRoom` | apare ca iconiță **dacă încape**; altfel intră în `⋮` |
| `never` | intră **mereu** în `⋮` |
| `always` | apare mereu ca iconiță (rău — umple bara) |

În DMA03: `search` și `share` sunt `ifRoom` (iconițe), `settings` e `never` (în overflow).

### Cum — legarea în cod

```java
MaterialToolbar toolbar = findViewById(R.id.topAppBar);

// Hamburger (navigation) icon
toolbar.setNavigationOnClickListener(v -> {
    drawerLayout.openDrawer(GravityCompat.START);
});

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
        Toast.makeText(this, "Settings", Toast.LENGTH_SHORT).show();
        return true;
    }
    return false;
});
```

### Două metode diferite pentru două zone

| Zonă | Metodă | Ce primești |
|---|---|---|
| Iconița de navigare (stânga) | `setNavigationOnClickListener` | `View` |
| Acțiunile (dreapta) | `setOnMenuItemClickListener` | `MenuItem` |

> **De reținut:** `return true` în `setOnMenuItemClickListener` înseamnă „am tratat click-ul". `return false` lasă evenimentul să se propage (și închide meniul fără acțiune).

### Cum apare hamburger-ul

`MaterialToolbar` afișează automat iconița de hamburger dacă:
1. ai setat un `DrawerLayout` ca `ActionBarDrawerToggle`, **sau**
2. ai pus `app:navigationIcon="@drawable/ic_menu"` în XML.

În DMA03, iconița vine din temă (`NoActionBar` + toolbar custom). Verifică `activity_main.xml` pentru `app:navigationIcon`.

### Exercițiu 14.2

**Cerință:** schimbă `action_settings` din `showAsAction="never"` în `"ifRoom"`. Rulează. Ce se vede?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai schimbat modul de afișare al unui item de meniu.

**Ce se vede:** „Settings" apare ca a treia iconiță în bară — dar numai dacă are `android:icon` și încape. În DMA03, `action_settings` **nu are** `android:icon`, deci apare ca **text** „Settings" în bară. Dacă nu încape, intră tot în `⋮`.

**De ce:** `showAsAction="ifRoom"` cere „arată-mă direct dacă am loc". Fără iconiță, se arată ca text — și ocupă mult.

**De reținut:**
1. `showAsAction` afectează doar **prezența în bară**, nu funcționalitatea. `setOnMenuItemClickListener` primește click-ul în ambele cazuri.
2. Un item fără iconiță și `ifRoom` arată prost. Regula: iconiță pentru `ifRoom`, fără iconiță pentru `never`.
3. `always` e o capcană: pe ecrane mici, itemele se suprapun.

**Unde revine:** nu revine, dar e o întrebare clasică: „unde apare un item de meniu?" Răspuns: depinde de `showAsAction` **și** de spațiul disponibil.

</details>

---

## Pasul 14.3 — `NavigationView`: sertarul

### De ce

`NavigationView` e componenta Material pentru meniul lateral. Ia un meniu XML și îl afișează ca listă de rânduri cu iconițe.

### Cum — meniul sertarului

`res/menu/drawer_menu.xml` conține itemele: `nav_inbox`, `nav_sent`, `nav_trash`, `nav_settings`.

### Cum — legarea

```java
NavigationView navigationView = findViewById(R.id.navigationView);

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

    item.setChecked(true);
    drawerLayout.closeDrawer(GravityCompat.START);
    return true;
});
```

### Cele două linii care contează

```java
item.setChecked(true);
drawerLayout.closeDrawer(GravityCompat.START);
```

1. **`item.setChecked(true)`** — marchează vizual itemul selectat. Fără el, utilizatorul nu știe unde e.
2. **`closeDrawer`** — închide sertarul după selecție. Fără el, sertarul rămâne deschis peste conținut.

> **De reținut:** `setNavigationItemSelectedListener` **nu** închide sertarul automat. Trebuie să o faci tu.

### `GravityCompat.START` vs `Gravity.LEFT`

`START` respectă direcția de citire: în RTL, `START` = dreapta. `LEFT` ar fi mereu stânga — greșit în RTL. Același principiu ca `layout_gravity="bottom|end"` din capitolul 03.

### Exercițiu 14.3

**Cerință:** elimină `drawerLayout.closeDrawer(...)`. Rulează, apasă un item din sertar. Ce se întâmplă?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai scos linia care închide sertarul.

**Ce se vede:** titlul din toolbar se schimbă („Inbox", „Sent"…), dar **sertarul rămâne deschis** peste listă. Utilizatorul trebuie să facă swipe manual ca să-l închidă.

**De ce:** listener-ul de selecție e doar un callback. Nu are comportament implicit de închidere — fiecare aplicație decide (unele au submeniuri și rămân deschise).

**De reținut:**
1. `closeDrawer(GravityCompat.START)` închide sertarul din stânga. Pentru dreapta: `GravityCompat.END`.
2. `item.setChecked(true)` e separat — îl poți face și înainte de închidere.
3. `return true` spune că ai tratat selecția.

**Unde revine:** nu revine.

</details>

---

## Pasul 14.4 — `PopupMenu`: meniu ancorat pe un rând

### De ce

Un meniu contextual pentru un element de listă. Nu e același lucru cu meniul din toolbar: apare **lângă rândul atins**, nu în bară.

### Cum

```java
listView = findViewById(R.id.listView);

// Long press shows the popup menu
listView.setOnItemLongClickListener((parent, view, position, id) -> {
    PopupMenu popup = new PopupMenu(this, view);   // anchored to the pressed row
    popup.getMenuInflater().inflate(R.menu.list_item_menu, popup.getMenu());

    popup.setOnMenuItemClickListener(menuItem -> {
        int itemId = menuItem.getItemId();
        String selected = listView.getItemAtPosition(position).toString();

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
    });

    popup.show();
    return true;   // true = long press handled
});
```

### Cele patru lucruri care trebuie reținute

| Linie | De ce |
|---|---|
| `new PopupMenu(this, view)` | al doilea argument e **ancora** — rândul atins. De aceea `view` din `onItemLongClick` |
| `popup.getMenuInflater().inflate(...)` | popup-ul pornește gol; îi umpli meniul dintr-un XML |
| `popup.show()` | fără el, nimic nu apare. `setOnMenuItemClickListener` nu afișează |
| `return true` | **consumă** long press-ul, ca să nu se declanșeze și click-ul normal |

> **Capcană:** dacă `return false`, long press-ul nu e consumat și `ListView` poate declanșa și `OnItemClick` — deci se deschide și acțiunea normală.

### `setOnItemLongClickListener` vs `setOnItemClickListener`

| | Declanșare | Tipic pentru |
|---|---|---|
| `setOnItemClickListener` | atingere simplă | deschide detaliul |
| `setOnItemLongClickListener` | apăsare lungă | meniu contextual, ștergere |

Ambele primesc `(parent, view, position, id)`.

### Exercițiu 14.4

**Cerință:** schimbă `return true` în `return false` la finalul `setOnItemLongClickListener`. Ce se întâmplă la long press?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai schimbat valoarea returnată.

**Ce se vede:** popup-ul apare, dar după ce selectezi o acțiune, se poate declanșa și acțiunea de click normal (dacă există un `setOnItemClickListener` legat). În DMA03 nu există, deci efectul vizibil e mic — dar principiul e important.

**De ce:** `return true` = „am consumat evenimentul". `return false` = „nu l-am consumat, du-l mai departe".

**De reținut:**
1. Regula se aplică la **toți** listenerii care întorc `boolean`: `onItemLongClick`, `onMenuItemClick`, `onTouch`.
2. `onItemClick` întoarce `void` — nu poate consuma nimic.
3. Dacă vrei ca long press să anuleze click-ul, `return true` e obligatoriu.

**Unde revine:** în `ItemActivity` (capitolul 07), `onDateSet` întoarce `void` — la fel, nu consumă nimic. Doar `boolean` poate consuma.

</details>

---

## Pasul 14.5 — Butonul Back: `OnBackPressedCallback`

### De ce

Când sertarul e deschis și apeși Back, comportamentul corect e să închizi sertarul, nu să închizi aplicația. Android modern cere `OnBackPressedCallback` (metoda `onBackPressed()` e depreciată).

### Cum

```java
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

### Mecanismul, pas cu pas

1. `addCallback(this, callback)` — înregistrezi un callback legat de ciclul de viață al activității.
2. `new OnBackPressedCallback(true)` — `true` = activ imediat.
3. În `handleOnBackPressed`:
   - dacă sertarul e deschis → închide-l și **oprește-te**;
   - altfel → `setEnabled(false)` (dezactivezi callback-ul ca să nu te reapelezi) și apelezi comportamentul implicit.

> **De ce `setEnabled(false)` înainte de `onBackPressed()`:** dacă lași callback-ul activ și apelezi `onBackPressed()`, te reapelezi pe tine însuți → buclă infinită. Dezactivarea îl scoate din lanț pentru acel apel.

### Exercițiu 14.5

**Cerință:** elimină `setEnabled(false)` din ramura `else`. Rulează, deschide sertarul, închide-l, apasă Back.

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai scos dezactivarea callback-ului.

**Ce se întâmplă:** la Back cu sertarul închis, `handleOnBackPressed` se apelează, intră pe `else`, apelează `getOnBackPressedDispatcher().onBackPressed()` — care **te reapelează** pe tine. Recursie infinită → `StackOverflowError`, sau aplicația îngheață.

**De ce:** dispatcher-ul cheamă callback-urile active în ordine. Dacă al tău e activ și tu îl apelezi, te chemi pe tine.

**De reținut:**
1. `setEnabled(false)` = scoate callback-ul din lanț.
2. Alternativa: `removeCallback` — dar atunci nu-l mai poți reactiva ușor.
3. `getOnBackPressedDispatcher().onBackPressed()` e echivalentul vechiului `super.onBackPressed()`.

**Unde revine:** nu revine, dar e o întrebare de test: „cum gestionezi Back cu un drawer deschis?"

</details>

---

## Pasul 14.6 — `AlertDialog` și `Snackbar`

### De ce

`DMA03` are un al doilea ecran (`SecondActivity`) care demonstrează două componente de feedback: un dialog de confirmare și un `Snackbar` cu acțiune.

> **Observație onestă:** `SecondActivity` e declarată în manifest dar **nu e pornită de nicăieri**. `MainActivity` importă `Intent` dar nu îl folosește. E un ecran de laborator, lăsat nelegat. Îl poți deschide doar temporar, adăugând un `startActivity` în `MainActivity`.

### Cum — `AlertDialog`

```java
public void btnClick(View view) {
    AlertDialog.Builder builder = new AlertDialog.Builder(SecondActivity.this);
    builder.setTitle("Add new control ...")
            .setMessage("Are you sure you want to add a new control?")
            .setCancelable(true)
            .setPositiveButton("Do it!", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    int id = addButton();
                    // Snackbar...
                }
            })
            .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    Toast.makeText(SecondActivity.this, "Object creation cancelled", Toast.LENGTH_LONG).show();
                }
            });
    builder.show();
}
```

### Părțile unui `AlertDialog`

| Metodă | Ce face |
|---|---|
| `setTitle` | titlul dialogului |
| `setMessage` | textul |
| `setCancelable(true)` | Back și click în afară îl închid |
| `setPositiveButton` | butonul din dreapta (acțiunea) |
| `setNegativeButton` | butonul din stânga (renunțare) |
| `show()` | **obligatoriu** — fără el, nimic nu apare |

Metodele se pot înlănțui (`builder` returnează `builder`) — de aceea `.setTitle(...).setMessage(...)` merge.

### Cum — `Snackbar` cu acțiune

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

> **Capcană:** `Snackbar.make(context, view, text, duration)` — al doilea argument trebuie să fie un `View` **din** arborele curent. Aici e `inflatedLayout`, nu `SecondActivity.this` (care nu e `View`).

### `Snackbar` vs `Toast`

| | `Toast` | `Snackbar` |
|---|---|---|
| Poziție | jos, peste orice | jos, în containerul indicat |
| Buton de acțiune | nu | **da** (`setAction`) |
| Durată | `LENGTH_SHORT` / `LENGTH_LONG` | `LENGTH_SHORT` / `LENGTH_LONG` / `LENGTH_INDEFINITE` |
| Anulabil | nu | da (swipe) |
| Necesită `View` ancora | nu | **da** |

> **De reținut:** `Snackbar` e preferat când oferi o acțiune de anulare („Undo"). `Toast` rămâne pentru confirmări simple.

### Exercițiu 14.6

**Cerință:** înlocuiește `Toast.makeText(...)` din `setNegativeButton` cu un `Snackbar`. Ce trebuie schimbat?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai schimbat metoda de feedback.

```java
.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
    @Override
    public void onClick(DialogInterface dialog, int which) {
        Snackbar.make(SecondActivity.this, inflatedLayout,
                "Object creation cancelled", Snackbar.LENGTH_LONG).show();
    }
})
```

**Ce trebuie schimbat:** al doilea argument al lui `Snackbar.make` — un `View` din arbore. Ai deja `inflatedLayout`. `SecondActivity.this` e `Context`, nu `View`.

**De reținut:**
1. `Snackbar.make(Context, View, CharSequence, int)` — semnătura completă.
2. Recipient: `Snackbar` e o clasă **abstractă**; `make(...)` întoarce o instanță concretă.
3. Nu uita `.show()`.

**Unde revine:** nu revine.

</details>

---

## Pasul 14.7 — Crearea de view-uri din cod

### De ce

`addButton()` creează un `Button` **fără XML**. E opusul a tot ce ai făcut până acum — și e util să știi că se poate.

### Cum

```java
int counter = 0;

public int addButton() {
    DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
    int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50,
            displayMetrics);

    Button newBtn = new Button(SecondActivity.this);
    newBtn.setText("Button_" + (++counter));
    newBtn.setId(counter);

    ViewGroup.LayoutParams layoutParams =
            new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT);
    newBtn.setLayoutParams(layoutParams);

    inflatedLayout.addView(newBtn);
    return counter;
}
```

### Ce se întâmplă, pas cu pas

1. `new Button(context)` — creează widget-ul direct, fără inflate.
2. `setText(...)` — textul.
3. `setId(counter)` — **un ID propriu**. Fără el, view-ul nu poate fi găsit mai târziu cu `findViewById`.
4. `new ViewGroup.LayoutParams(...)` — dimensiunile. Fără ele, view-ul apare cu `0×0`.
5. `inflatedLayout.addView(newBtn)` — îl adaugă în containerul existent.

### De ce `setId` e esențial

La `removeView`, codul face:

```java
Button viewById = inflatedLayout.findViewById(id);
inflatedLayout.removeView(viewById);
```

`findViewById(id)` are nevoie de un ID. De aceea `setId(counter)` salvează ID-ul, iar `addButton()` îl returnează ca să fie folosit de `Snackbar`.

> **Atenție:** `setId(counter)` folosește valori 1, 2, 3… Care pot intra în conflict cu ID-urile generate din `R.id` (care sunt numere mari, dar nu garantat). Practic merge; corect ar fi `View.generateViewId()`.

### `DisplayMetrics` și `TypedValue`

```java
DisplayMetrics displayMetrics = getResources().getDisplayMetrics();
int hPixels = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 50, displayMetrics);
```

Convertește 50dp în pixeli. **Dar**: `hPixels` nu e folosit nicăieri în cod! Linia e demonstrativă — arată cum se face conversia dp → px.

> **De reținut:** în XML, `50dp` e deja convertit de Android. Din cod, trebuie să faci tu conversia cu `TypedValue.applyDimension`.

### Exercițiu 14.7

**Cerință:** de ce `new ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)` și nu `setWidth`/`setHeight` direct pe `Button`?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai comparat cele două abordări.

**Răspunsul:** `View` **nu are** `setWidth`/`setHeight`. Dimensiunile se dau prin `LayoutParams`, pe care părintele le citește la măsurare.

**De ce:** un view nu știe cât spațiu are — știe doar ce cere. Părintele decide. De aceea `LayoutParams` aparține de relația copil–părinte, nu de view.

**De reținut:**
1. `ViewGroup.LayoutParams.MATCH_PARENT` = -1, `WRAP_CONTENT` = -2. Sunt constante speciale, nu valori de pixeli.
2. Tipul corect de `LayoutParams` depinde de părinte: `LinearLayout.LayoutParams` pentru `LinearLayout`, `FrameLayout.LayoutParams` pentru `FrameLayout`.
3. Pentru `LinearLayout`, poți seta și `weight` prin `LinearLayout.LayoutParams`.

**Unde revine:** în capitolul 06, `layout_weight="1"` din XML e exact `LinearLayout.LayoutParams.weight = 1` din cod.

</details>

---

## Pasul 14.8 — Verificare

### Cum

1. Deschide `DMA03` în Android Studio.
2. Rulează. Verifică pe rând:
   - iconița de hamburger deschide sertarul;
   - un item din sertar schimbă titlul și închide sertarul;
   - long press pe un rând deschide popup-ul;
   - Back cu sertarul deschis îl închide, nu închide aplicația;
   - Search / Share / Settings din toolbar dau `Toast`.

### Ce verifici în cod

- [ ] `DrawerLayout` are exact 2 copii: `CoordinatorLayout` + `NavigationView`
- [ ] `NavigationView` are `layout_gravity="start"`
- [ ] `toolbar.setNavigationOnClickListener` deschide drawer-ul
- [ ] `toolbar.setOnMenuItemClickListener` tratează cele 3 acțiuni
- [ ] `navigationView.setNavigationItemSelectedListener` face `setChecked(true)` + `closeDrawer`
- [ ] `PopupMenu` ancorat pe `view` (rândul), nu pe activitate
- [ ] `OnBackPressedCallback` face `setEnabled(false)` înainte de `onBackPressed()`

---

## Rezumat capitol 14

- `DrawerLayout` = 2 copii: conținut (primul) + sertar (al doilea), cu `layout_gravity="start"`.
- `MaterialToolbar` = `setNavigationOnClickListener` (stânga) + `setOnMenuItemClickListener` (dreapta).
- `showAsAction`: `ifRoom` / `never` / `always`.
- `NavigationView` nu închide sertarul singur — `closeDrawer` explicit.
- `PopupMenu` ancorat pe rând, `return true` ca să consume long press-ul.
- `OnBackPressedCallback` cu `setEnabled(false)` înainte de re-apel, altfel recursie.
- `AlertDialog` = `Builder` + `show()`. `Snackbar` = `make(context, view, text, duration)` + acțiune opțională.
- View-uri din cod: `new Button(ctx)`, `setId`, `setLayoutParams`, `addView`.

**Următorul capitol:** [15 - DMA02 - Application si ciclu de viata.md](15%20-%20DMA02%20-%20Application%20si%20ciclu%20de%20viata.md)
