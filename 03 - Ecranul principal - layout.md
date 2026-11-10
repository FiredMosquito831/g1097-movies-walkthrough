# Capitolul 03 — Ecranul principal: layout-ul

**Obiectiv:** `activity_main.xml` — un `FrameLayout` cu un `ListView` pe tot ecranul și un `FloatingActionButton` suprapus jos-dreapta.

**Timp estimat:** 20–30 min.

**Fișier final:** `cod-final/res/layout/activity_main.xml` (1016 B, SHA-256 `230b1a3bf534d36e…`)

---

## Pasul 3.1 — Ce este un layout XML

### De ce

Un layout XML descrie un **arbore de view-uri**. Fiecare element e o clasă Java:

| XML | Clasă Java |
|---|---|
| `<FrameLayout>` | `android.widget.FrameLayout` |
| `<ListView>` | `android.widget.ListView` |
| `<com.google.android.material.floatingactionbutton.FloatingActionButton>` | clasa aia, exact |

Când apelezi `setContentView(R.layout.activity_main)`, Android:

1. citește XML-ul (deja compilat în binar),
2. creează obiectele Java (`new FrameLayout(context)`, `new ListView(context)`...),
3. le leagă în arbore (`parent.addView(child)`),
4. măsoară și desenează.

Deci **XML-ul nu e „configurare”** — e cod care se execută la `setContentView`. Fiecare atribut devine un apel de metodă (`android:textSize="20sp"` → `setTextSize(...)`).

### Consecință practică

Poți face orice în XML și echivalentul în Java. XML-ul e preferat pentru că e declarativ, se vede în preview, și separă „ce arată” de „ce face”.

---

## Pasul 3.2 — `FrameLayout` ca rădăcină

### De ce `FrameLayout` și nu `LinearLayout` sau `ConstraintLayout`

`FrameLayout` stivulește copiii **unul peste altul**, în ordinea din XML:

- primul copil = cel mai de jos (în spate);
- ultimul copil = cel mai de sus (în față).

Asta e exact ce vrei: lista umple ecranul, iar butonul flotant **plutește deasupra ei**, în colț.

Cu `LinearLayout` ar fi trebuit o structură mai complicată. Cu `ConstraintLayout` ar fi mers, dar e overkill pentru 2 copii.

### Capcana din repo

```xml
android:orientation="horizontal"
```

`FrameLayout` **nu are** atribut `orientation`. Linia e ignorată de Android (nu dă eroare, doar un warning de lint). A rămas de la un `LinearLayout` din care s-a transformat layout-ul.

> **De ce o păstrăm?** Pentru fidelitate față de repo. Dar trebuie să **știi** că e inutilă — la test, dacă ți se cere să explici, răspunsul e: „atribut invalid pentru `FrameLayout`, ignorat”.

### Cum

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    tools:context=".activities.MainActivity">
```

### De ce cele trei `xmlns`

| Namespace | Pentru ce | Exemplu de atribut |
|---|---|---|
| `android:` | atribute din framework-ul Android | `android:layout_width` |
| `app:` | atribute din biblioteci (Material, AndroidX) | `app:srcCompat` |
| `tools:` | atribute **doar pentru preview**, eliminate la build | `tools:context` |

`tools:context=".activities.MainActivity"` nu face nimic la runtime. Îi spune lui Android Studio ce clasă să folosească pentru preview (ex. pentru a sugera `findViewById`).

### De ce `android:id="@+id/main"`

`@+id/` înseamnă „creează ID-ul dacă nu există”. ID-ul `main` e folosit în cod:

```java
ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), ...)
```

Dacă lipsește, `findViewById(R.id.main)` întoarce `null` și insets-ul nu se aplică → conținutul intră sub bara de status.

---

## Pasul 3.3 — `ListView`

### De ce

`ListView` e widget-ul clasic pentru liste verticale. Primește un `Adapter` care știe câte elemente sunt și cum arată fiecare.

### Cum

```xml
<ListView
    android:id="@+id/listView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:entries="@array/items" />
```

### Atributele, explicate

| Atribut | Efect |
|---|---|
| `layout_width="match_parent"` | la fel de lat ca părintele (FrameLayout-ul) |
| `layout_height="match_parent"` | la fel de înalt ca părintele |
| `android:entries="@array/items"` | **umple lista direct din XML** cu cele 20 de „Item 1..20” |

### Capcana `android:entries`

`android:entries` e o **scurtătură** care creează automat un `ArrayAdapter<String>` din resursa dată. E utilă pentru demo, dar **intră în conflict** cu `setAdapter()` din cod.

În `MainActivity.initControls()` ai:

```java
listView.setAdapter(movieAdapter);
```

Asta **înlocuiește** adapterul creat de `entries`. Deci `android:entries` devine inutil la runtime.

> **De ce e păstrat totuși?** Pentru că în preview-ul Android Studio vezi lista populată, nu un dreptunghi gol. E o tehnică de design-time. La runtime, codul câștigă.

**De reținut:** `android:entries` și `setAdapter()` sunt alternative. Dacă le ai pe amândouă, ultima apelare câștigă.

### Exercițiu 3.3

**Cerință:** elimină `android:entries="@array/items"` și verifică: (a) preview-ul din Android Studio, (b) aplicația pe emulator. Ce diferă?

<details>
<summary>Indiciu</summary>

Preview-ul se uită la `tools:` și la `android:` pentru design-time. `setAdapter()` rulează doar pe device.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am scos `android:entries="@array/items"` din `ListView`.

**Cum se vede:** în preview-ul Android Studio, lista apare **goală** (un dreptunghi alb). Pe emulator, lista apare **populată** cu Inception, Toy Story, The Matrix — pentru că `setAdapter(movieAdapter)` din `MainActivity` o umple.

**De ce:** `android:entries` e citit **doar la inflate**, adică atunci când Android construiește view-urile. `setAdapter()` e apelat după `setContentView()`, deci **după** inflate. Al doilea îl înlocuiește pe primul.

**De reținut:**
1. Preview-ul Android Studio **nu rulează cod Java**. Deci orice depinde de `setAdapter()`, `notifyDataSetChanged()` etc. nu apare în preview.
2. `android:entries` e o scurtătură de design-time, nu o soluție reală.
3. Pentru un preview realist, se folosește `tools:listitem="@layout/movie_item"` (vezi cap. 11).

**Unde revine:** la capitolul 11, când treci pe `RecyclerView`, `android:entries` dispare complet și e înlocuit de `tools:listitem`, care e **doar** pentru preview. Vei vedea exact aceeași distincție design-time vs runtime.

</details>

---

## Pasul 3.4 — `FloatingActionButton`

### De ce

Un FAB e butonul rotund care plutește peste conținut. În Material Design e rezervat pentru **acțiunea principală** a ecranului. Aici: „adaugă un film”.

### Cum

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="bottom|end"
    android:layout_margin="16dp"
    android:contentDescription="Add"
    app:srcCompat="@drawable/outline_add_24" />
```

### Atributele, explicate

| Atribut | De ce exact așa |
|---|---|
| `layout_width/height="wrap_content"` | FAB-ul are dimensiune fixă internă (56dp implicit); `wrap_content` o respectă |
| `android:layout_gravity="bottom|end"` | **cheia**: în `FrameLayout`, `layout_gravity` poziționează copilul. `bottom\|end` = jos, dreapta (sau stânga în RTL, datorită `supportsRtl`) |
| `android:layout_margin="16dp"` | distanță de margini, ca să nu atingă muchia |
| `android:contentDescription="Add"` | text pentru TalkBack (accesibilitate). **Obligatoriu** pentru imagini — lint-ul dă eroare altfel |
| `app:srcCompat="@drawable/outline_add_24"` | iconița. `srcCompat` (nu `android:src`) pentru compatibilitate vectorială |

### De ce `app:srcCompat` și nu `android:src`

`android:src` pe un `ImageView` (și FAB-ul e un `ImageView` specializat) nu suportă vectori pe versiuni vechi de Android fără AppCompat. `app:srcCompat` e varianta sigură, procesată de AppCompat.

> **De reținut:** `app:` = atribut din bibliotecă. `android:` = atribut din framework. Când un atribut nu există în `android:`, îl cauți în `app:`.

### De ce `bottom|end` și nu `bottom|right`

`end` respectă direcția de citire. În arabă (RTL), `end` = stânga. `right` ar fi mereu dreapta, ceea ce ar arăta greșit. Aplicația are `android:supportsRtl="true"` în manifest — deci `end` contează.

### Exercițiu 3.4

**Cerință:** mută FAB-ul în colțul **stânga-sus** și mărește marginea la 32dp. Verifică pe emulator.

<details>
<summary>Indiciu</summary>

`layout_gravity` acceptă combinații: `top|start`, `bottom|end`, `center`, etc.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat `layout_gravity` din `bottom|end` în `top|start` și `layout_margin` din `16dp` în `32dp`.

```xml
<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/floatingActionButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="top|start"
    android:layout_margin="32dp"
    android:contentDescription="Add"
    app:srcCompat="@drawable/outline_add_24" />
```

**Cum se vede:** butonul sare în colțul stânga-sus, mai departe de margini.

**De ce funcționează:** în `FrameLayout`, `layout_gravity` e atributul care controlează poziția unui copil în interiorul părintelui. Fără el, copilul e plasat în `top|start` implicit.

**De reținut:**
1. `layout_gravity` = poziția **copilului în părinte**.
2. `gravity` (fără `layout_`) = poziția **conținutului în copil** (ex. textul într-un `TextView`).
3. Confuzia între ele e o greșeală clasică la test.

**Unde revine:** în `activity_item.xml` (cap. 05–06) vei vedea `android:gravity="center_vertical"` pe `LinearLayout`-uri — acela centrează **copiii** pe verticală. Și vei vedea `android:layout_gravity="center_horizontal"` pe `RatingBar` — acela centrează bara în părinte. Același cuvânt, două sensuri.

</details>

---

## Pasul 3.5 — Ordinea copiilor în `FrameLayout`

### De ce

În `FrameLayout`, **ordinea din XML = ordinea de stivuire**. Primul copil e dedesubt, ultimul e deasupra.

În `activity_main.xml`, `ListView` e primul, FAB-ul e al doilea. Deci FAB-ul e **peste** listă.

### Ce s-ar întâmpla invers

Dacă ai pune FAB-ul primul, lista ar fi desenată peste el. Butonul ar fi invizibil (sau parțial, dacă lista are fundal transparent — dar `ListView` are fundal opac).

### Exercițiu 3.5

**Cerință:** inversează ordinea celor doi copii. Rulează. Ce observi? Apoi pune-le la loc.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am mutat blocul `<FloatingActionButton .../>` **înaintea** blocului `<ListView .../>`.

**Cum se vede:** FAB-ul **dispare** de pe ecran. Lista îl acoperă complet.

**De ce:** `FrameLayout` desenează copiii în ordinea din XML. Primul desenat e primul „lipit” pe fundal; fiecare următor se desenează peste. Dacă lista (opacă, `match_parent`) e desenată după FAB, o acoperă.

**De reținut:**
1. **Ordinea în XML contează** la `FrameLayout` (și la `RelativeLayout`, dar acolo se pot folosi și reguli explicite).
2. La `LinearLayout`, ordinea e pe orizontală/verticală, nu pe adâncime.
3. Dacă vrei un element „deasupra” în `FrameLayout`, îl pui **ultimul**.

**Unde revine:** în `movie_item.xml` (cap. 11), `MaterialCardView` conține un `LinearLayout` orizontal cu `ImageView` + coloană de text. Acolo ordinea e stânga-dreapta, pentru că e `LinearLayout`, nu `FrameLayout`. Vei vedea diferența imediat.

</details>

---

## Pasul 3.6 — Verificare vizuală

### De ce

Un layout care compilează poate arăta complet greșit. Verifici **vizual**, nu doar cu `BUILD SUCCESSFUL`.

### Cum

1. Deschide `activity_main.xml` → tab **Design** (dreapta sus).
2. Verifică:
   - Lista umple tot ecranul.
   - FAB-ul e în colțul jos-dreapta, la 16dp de margini.
   - În listă apar „Item 1” … „Item 20” (din `entries`).
3. Rulează pe emulator: lista apare cu **filme** (Inception, Toy Story, The Matrix) — pentru că `setAdapter` a înlocuit adapterul din XML.

### Diferența design vs runtime

| | Preview | Emulator |
|---|---|---|
| Sursa listei | `android:entries` | `setAdapter(movieAdapter)` |
| Ce vezi | Item 1..20 | Inception, Toy Story, The Matrix |
| Text pe rând | `Item N` | `Movie{title='...', ...}` (pentru că `toString()`) |

Asta e dovada că `setAdapter` câștigă.

---

## Pasul 3.7 — Exercițiu de sinteză

**Cerință:** fără să te uiți la soluție, scrie din memorie `activity_main.xml` complet. Apoi compară cu `cod-final/res/layout/activity_main.xml`.

### Ce verifici

- [ ] `FrameLayout` rădăcină cu `android:id="@+id/main"`
- [ ] cei trei `xmlns` (`android`, `app`, `tools`)
- [ ] `tools:context=".activities.MainActivity"`
- [ ] `ListView` cu `android:id="@+id/listView"`, `match_parent`/`match_parent`, `entries`
- [ ] `FloatingActionButton` cu `android:id="@+id/floatingActionButton"`, `layout_gravity="bottom|end"`, `layout_margin="16dp"`, `contentDescription`, `app:srcCompat`
- [ ] **ordinea**: ListView primul, FAB al doilea

### Întrebări de test

1. De ce `FrameLayout` și nu `LinearLayout`?
2. Ce face `android:orientation="horizontal"` pe un `FrameLayout`?
3. De ce `app:srcCompat` și nu `android:src`?
4. Ce se întâmplă dacă pui FAB-ul înaintea listei?
5. Ce diferență e între `android:gravity` și `android:layout_gravity`?

<details>
<summary>Răspunsuri — explicativ</summary>

**1. De ce `FrameLayout` și nu `LinearLayout`?**
`FrameLayout` stivulește copiii unul peste altul — exact ce trebuie pentru un buton care „plutește” peste listă. `LinearLayout` i-ar pune **unul lângă altul** (orizontal) sau **unul sub altul** (vertical), deci lista și butonul ar împărți ecranul, nu s-ar suprapune.

**2. Ce face `android:orientation="horizontal"` pe un `FrameLayout`?**
**Nimic.** `FrameLayout` nu are atributul `orientation`. Android ignoră atributele necunoscute la inflate (nu aruncă excepție), dar lint-ul dă un warning. Linia a rămas de la un `LinearLayout` anterior.

**3. De ce `app:srcCompat` și nu `android:src`?**
`app:srcCompat` e procesat de AppCompat și știe să încarce `VectorDrawable` pe orice versiune de Android. `android:src` pe un `ImageView` normal nu suportă vectori nativ pe API < 21 (aici `minSdk=33`, deci tehnic ar merge, dar convenția rămâne `srcCompat` pentru portabilitate).

**4. Ce se întâmplă dacă pui FAB-ul înaintea listei?**
Lista, fiind `match_parent` și opacă, e desenată **peste** FAB. Butonul devine invizibil și ne-atingibil.

**5. `android:gravity` vs `android:layout_gravity`?**
- `gravity` = cum se aliniază **conținutul propriu** (textul într-un `TextView`, copiii într-un `LinearLayout`).
- `layout_gravity` = cum se aliniază **elementul însuși** în părintele lui.

Exemplu: `TextView` cu `android:gravity="center"` → textul se centrează în `TextView`. `TextView` cu `android:layout_gravity="center"` → `TextView`-ul se centrează în părinte.

</details>

---

## Rezumat capitol 03

- `FrameLayout` = stivuire; ordinea în XML = ordinea de desenare.
- `ListView` umple tot; `android:entries` e doar pentru preview, `setAdapter` câștigă la runtime.
- FAB poziționat cu `layout_gravity="bottom|end"`, iconiță cu `app:srcCompat`.
- `android:orientation` pe `FrameLayout` e inutil (rămășiță).
- `android:id="@+id/main"` e folosit de insets în cod.

**Următorul capitol:** [04 - MainActivity - lista.md](04%20-%20MainActivity%20-%20lista.md)
