# Capitolul 12 — DMA06: ListView vs. RecyclerView, în trei trepte

**Obiectiv:** să înțelegi exact ce se schimbă între `ListView` cu `ArrayAdapter`, `ListView` cu adapter propriu și `RecyclerView`. Profesorul a construit trei ecrane pe **aceleași date** (numerele 1–100), ca diferențele să fie vizibile.

**Timp estimat:** 60–75 min.

**Sursa:** `DMA06/` la commitul `d719ffc` — 37 de fișiere, ultima modificare `2d891ef` (2026-11-04).

> **De ce contează pentru tine:** în `G1097` la `d719ffc` ai `ListView` + `ArrayAdapter`. Trecerea pe `RecyclerView` pe care ai făcut-o local în 09.11 urmează **exact** pașii din DMA06. Aici vezi mecanismul curat, pe date simple, fără formular în jur.

---

## Pasul 12.1 — Structura proiectului DMA06

### De ce

Înainte de cod, uită-te la împărțirea pe pachete. E primul exemplu din repo cu separare clară pe responsabilități.

### Cum

```
DMA06/src/main/java/ro/ase/ie/dma06/
├── activities/
│   ├── MainActivity.java            ← meniul cu 3 butoane
│   ├── SingleColumnActivity.java    ← Treapta 1: ListView + ArrayAdapter
│   ├── TwoColumnActivity.java       ← Treapta 2: ListView + adapter propriu
│   └── RecyclerViewActivity.java    ← Treapta 3: RecyclerView
├── adapters/
│   ├── NumberListAdapter.java       ← BaseAdapter pentru ListView
│   └── NumberRecyclerAdapter.java   ← RecyclerView.Adapter
└── data/
    └── NumberData.java              ← sursa: 1..100
```

Și în `res/layout/`:
- `activity_main.xml`, `activity_single_column.xml`, `activity_two_column.xml`, `activity_recycler_view.xml`
- `item_number.xml` — **același rând, folosit de treptele 2 și 3**
- `layout_number_header.xml` — antetul cu două coloane

### De ce contează împărțirea

Fiecare pachet are un singur rol:

| Pachet | Rol | Nu are voie să |
|---|---|---|
| `data` | produce date | cunoască `View`, `Adapter`, `Context` |
| `adapters` | transformă date în rânduri | cunoască `Activity` |
| `activities` | leagă totul și răspunde la input | conțină logică de afișare per rând |

`NumberData` e cel mai curat exemplu:

```java
public final class NumberData {
    private static final int FIRST_NUMBER = 1;
    private static final int LAST_NUMBER = 100;

    private NumberData() {
        // This class only has static methods
    }

    public static List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();
        for (int number = FIRST_NUMBER; number <= LAST_NUMBER; number++) {
            numbers.add(number);
        }
        return numbers;
    }
}
```

Observă: constructor `private` (nu se instanțiază), metodă `static`, zero importuri `android.*`.

> **De reținut:** `private` pe constructor e trucul standard pentru o clasă utilitară. Dacă nu o poți instanția, nimeni nu o va face din greșeală.

---

## Pasul 12.2 — Treapta 1: `ListView` cu `ArrayAdapter`

### De ce

E varianta minimă. Funcționează doar când rândul are **un singur text**.

### Cum

`SingleColumnActivity`:

```java
ListView lvNumbers = findViewById(R.id.lvNumbers);
// ArrayAdapter calls toString() on each number and shows it in a TextView
ArrayAdapter<Integer> adapter = new ArrayAdapter<>(
        this, android.R.layout.simple_list_item_1, NumberData.getNumbers());
lvNumbers.setAdapter(adapter);
```

Trei linii. Atât.

### Ce se vede

O listă cu „1", „2", „3" … „100", pe un singur rând fiecare.

### De ce merge fără niciun layout propriu

`android.R.layout.simple_list_item_1` e un layout **din sistem** care conține un `TextView` cu id-ul `android.R.id.text1`. `ArrayAdapter` îl umple cu `toString()`-ul fiecărui element.

Pentru `Integer`, `toString()` întoarce exact numărul. Deci `1` → `"1"`.

### Limita

Ce faci dacă vrei **două** coloane — zecimal și binar? `ArrayAdapter` are un singur `TextView`. Nu poți.

Aici se termină Treapta 1.

### Exercițiu 12.2

**Cerință:** de ce `ArrayAdapter<Integer>` și nu `ArrayAdapter<String>`? Ce s-ar întâmpla cu al doilea?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai comparat cele două variante de tip generic.

**Răspunsul:** `ArrayAdapter<Integer>` ține `List<Integer>`. `ArrayAdapter<String>` ar cere `List<String>`, deci ai fi convertit fiecare număr în string **înainte** de a-l pune în listă.

**Ce se pierde:** tipul. Dacă ai `List<String>`, nu mai poți face `Integer.toBinaryString(...)` fără să parsezi înapoi. Ai arunca informația și ai recupera-o.

**De reținut:**
1. Generic-ul trebuie să coincidă cu tipul listei sursă.
2. `ArrayAdapter` nu are nevoie de `Integer` — ar fi mers și `Object`. Dar atunci ai pierde verificarea la compilare.
3. `toString()` e apelat pe element, indiferent de tip.

**Unde revine:** la Treapta 2, adapterul propriu primește tot `List<Integer>` — și abia acolo tipul chiar contează, pentru că îl folosești în `Integer.toBinaryString()`.

</details>

---

## Pasul 12.3 — Treapta 2: `ListView` cu adapter propriu (`BaseAdapter`)

### De ce

Ai nevoie de **două coloane** într-un rând. `ArrayAdapter` nu știe decât un `TextView`. Deci scrii tu adapterul.

### Cum — layout-ul rândului

`res/layout/item_number.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- One row with two columns. Steps 2 and 3 both use this layout. -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:paddingHorizontal="16dp"
    android:paddingVertical="14dp">

    <TextView
        android:id="@+id/tvDecimal"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:textAppearance="?attr/textAppearanceBodyLarge" />

    <TextView
        android:id="@+id/tvBinary"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:fontFamily="monospace"
        android:gravity="end"
        android:textAppearance="?attr/textAppearanceBodyLarge" />
</LinearLayout>
```

Două `TextView` cu `0dp` + `layout_weight="1"` → fiecare ia jumătate din lățime.

> **Observă comentariul din XML:** „Steps 2 and 3 both use this layout." Același fișier servește ambele adaptere. Asta e dovada că diferența dintre `ListView` și `RecyclerView` **nu e în layout**, ci în adapter.

### Cum — adapterul

`adapters/NumberListAdapter.java`:

```java
public class NumberListAdapter extends BaseAdapter {

    private static class ViewHolder {
        TextView tvDecimal;
        TextView tvBinary;
    }

    private final List<Integer> numbers;
    private final LayoutInflater layoutInflater;

    public NumberListAdapter(Context context, List<Integer> numbers) {
        this.layoutInflater = LayoutInflater.from(context);
        this.numbers = numbers;
    }

    @Override
    public int getCount() {
        return numbers.size();
    }

    @Override
    public Integer getItem(int position) {
        return numbers.get(position);
    }

    @Override
    public long getItemId(int position) {
        // Each number is unique, so the number itself can be the ID
        return numbers.get(position);
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;

        if (convertView == null) {
            // New row: inflate it and store its views
            convertView = layoutInflater.inflate(R.layout.item_number, parent, false);
            holder = new ViewHolder();
            holder.tvDecimal = convertView.findViewById(R.id.tvDecimal);
            holder.tvBinary = convertView.findViewById(R.id.tvBinary);
            convertView.setTag(holder);
        } else {
            // Reused row: get its stored views
            holder = (ViewHolder) convertView.getTag();
        }

        int number = getItem(position);
        holder.tvDecimal.setText(String.valueOf(number));
        holder.tvBinary.setText(Integer.toBinaryString(number));

        return convertView;
    }
}
```

### Cele patru metode ale lui `BaseAdapter`

| Metodă | Întrebarea la care răspunde | Cine o cheamă |
|---|---|---|
| `getCount()` | câte rânduri sunt? | `ListView` |
| `getItem(position)` | ce obiect e la poziția i? | `ListView` (la click) |
| `getItemId(position)` | ce ID stabil are? | `ListView` (`OnItemClickListener` primește `id`) |
| `getView(...)` | cum arată rândul i? | `ListView`, la fiecare rând vizibil |

### Mecanismul `convertView` + `ViewHolder` — esența

Aici e tot secretul performanței. `ListView` **nu creează 100 de rânduri** pentru 100 de elemente. Creează ~10 (câte încap pe ecran) și le **refolosește** la scroll.

De aceea `getView` primește `convertView`:

```
convertView == null   →  rând NOU: umflă-l din XML, caută view-urile, salvează-le în ViewHolder
convertView != null   →  rând REFOLOSIT: ia ViewHolder-ul salvat, NU mai caută nimic
```

`convertView.setTag(holder)` lipește `ViewHolder`-ul de rând. La refolosire, `convertView.getTag()` îl recuperează.

**Fără `ViewHolder`:** la fiecare scroll, `findViewById` ar căuta prin arbore de două ori per rând. Cu 100 de rânduri și scroll mult, e vizibil lent.

**Cu `ViewHolder`:** căutarea se face o singură dată per rând creat.

### De ce `getItemId` întoarce chiar numărul

```java
return numbers.get(position);
```

Pentru că numerele sunt unice. Într-o listă cu duplicate (ex. filme cu același titlu), ai avea nevoie de un `id` separat.

> **De reținut:** `getItemId` e folosit de `ListView` doar dacă ai `setHasStableIds(true)`. Implicit e ignorat. Dar e bine să-l implementezi corect.

### Exercițiu 12.3

**Cerință:** ce se întâmplă dacă uiți `convertView.setTag(holder)`?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai eliminat linia care lipește `ViewHolder`-ul de rând.

**Ce se întâmplă:** la scroll, `convertView != null`, deci se intră pe ramura `else`:

```java
holder = (ViewHolder) convertView.getTag();   // getTag() întoarce null
```

Apoi `holder.tvDecimal.setText(...)` → **`NullPointerException`**. Lista crăpă la prima refolosire de rând, adică imediat ce derulezi.

**De ce:** `setTag` și `getTag` sunt o pereche. Fără prima, a doua întoarce `null`.

**De reținut:**
1. `View.setTag(Object)` / `getTag()` e un câmp liber pe orice `View` — îl folosești ca să atașezi date.
2. Dacă uiți `setTag`, nu ai eroare la compilare. Abia la scroll apare.
3. Alternativa modernă e `RecyclerView.ViewHolder`, care face asta automat (vezi Treapta 3).

**Unde revine:** în Treapta 3, `RecyclerView` **îți impune** `ViewHolder` — nu poți uita `setTag` pentru că nu îl mai scrii tu.

</details>

---

## Pasul 12.4 — Treapta 3: `RecyclerView`

### De ce

`RecyclerView` face același lucru ca Treapta 2, dar:

- **`ViewHolder` e obligatoriu** — nu opțional, ca la `ListView`;
- **`getView` e împărțit în două metode** — creare și umplere;
- **`LayoutManager` e separat** — poți schimba vertical/grilă/orizontal fără să atingi adapterul;
- **animații gratuite** la inserare/ștergere.

### Cum — activitatea

`RecyclerViewActivity`:

```java
RecyclerView rvNumbers = findViewById(R.id.rvNumbers);
LinearLayoutManager layoutManager = new LinearLayoutManager(this);
rvNumbers.setLayoutManager(layoutManager);
NumberRecyclerAdapter adapter = new NumberRecyclerAdapter(NumberData.getNumbers());
rvNumbers.setAdapter(adapter);
```

### Cum — layout-ul

`activity_recycler_view.xml`:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <include layout="@layout/layout_number_header" />

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvNumbers"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

`layout_height="0dp"` + `layout_weight="1"` → `RecyclerView`-ul ia tot spațiul rămas după antet.

> **Atenție:** `RecyclerView` cu `wrap_content` într-un `LinearLayout` vertical funcționează, dar pierzi reciclarea eficientă (măsoară tot conținutul). `0dp` + `weight` sau `match_parent` e varianta corectă.

### Cum — adapterul

`adapters/NumberRecyclerAdapter.java`:

```java
public class NumberRecyclerAdapter
        extends RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder> {

    static class NumberViewHolder extends RecyclerView.ViewHolder {
        final TextView tvDecimal;
        final TextView tvBinary;

        NumberViewHolder(@NonNull View itemView) {
            super(itemView);
            tvDecimal = itemView.findViewById(R.id.tvDecimal);
            tvBinary = itemView.findViewById(R.id.tvBinary);
        }
    }

    private final List<Integer> numbers;

    public NumberRecyclerAdapter(List<Integer> numbers) {
        this.numbers = numbers;
    }

    @NonNull
    @Override
    public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Runs only when a new row is needed
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_number, parent, false);
        return new NumberViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull NumberViewHolder holder, int position) {
        // Runs each time a row shows a number
        int number = numbers.get(position);
        holder.tvDecimal.setText(String.valueOf(number));
        holder.tvBinary.setText(Integer.toBinaryString(number));
    }

    @Override
    public int getItemCount() {
        return numbers.size();
    }
}
```

### Corespondența exactă cu Treapta 2

| `BaseAdapter` (ListView) | `RecyclerView.Adapter` | Când rulează |
|---|---|---|
| `getCount()` | `getItemCount()` | la nevoie |
| `getView(...)` **prima parte**: `if (convertView == null) { inflate; findViewById; setTag }` | `onCreateViewHolder(...)` | **o singură dată** per rând creat |
| `getView(...)` **a doua parte**: `setText(...)` | `onBindViewHolder(...)` | la **fiecare** afișare a rândului |
| `ViewHolder` + `setTag`/`getTag` manual | `RecyclerView.ViewHolder` — automat | — |

Comentariile profesorului din cod spun exact asta:

```
// Runs only when a new row is needed      → onCreateViewHolder
// Runs each time a row shows a number     → onBindViewHolder
```

> **De reținut:** `RecyclerView` nu are `getView` pentru că a **despărțit** cele două responsabilități care la `ListView` erau amestecate într-o singură metodă cu `if (convertView == null)`.

### De ce `ViewHolder` e `static`

```java
static class NumberViewHolder extends RecyclerView.ViewHolder {
```

Dacă ar fi non-static, fiecare `ViewHolder` ar ține o referință implicită la instanța `NumberRecyclerAdapter`. Cu ~10 rânduri vizibile, ai ~10 referințe inutile. `static` le elimină.

> **Aceeași regulă** se aplică și la `MovieAdapter` din G1097 (capitolul 11).

### De ce `@NonNull`

```java
@NonNull
@Override
public NumberViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType)
```

Sunt adnotări de contract. `RecyclerView` garantează că nu trimite `null` ca `parent`, iar tu garantezi că nu întorci `null`. Lint-ul verifică.

### Exercițiu 12.4

**Cerință:** înlocuiește `LinearLayoutManager` cu `GridLayoutManager(this, 2)`. Rulează. Ce se schimbă? Trebuie să modifici adapterul?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai schimbat doar `LayoutManager`-ul:

```java
rvNumbers.setLayoutManager(new GridLayoutManager(this, 2));
```

**Ce se vede:** rândurile se aranjează în **două coloane**, ca o grilă. Fiecare celulă e în continuare `item_number.xml` (care are deja două coloane în interior).

**Trebuie modificat adapterul?** **Nu.** Absolut nicio linie.

**De ce:** `RecyclerView` separă **ce afișezi** (adapter) de **cum aranjezi** (LayoutManager). La `ListView` aranjarea era fixă — verticală, mereu.

**De reținut:**
1. `LinearLayoutManager(context)` — vertical (implicit).
2. `LinearLayoutManager(context, RecyclerView.HORIZONTAL, false)` — orizontal.
3. `GridLayoutManager(context, spanCount)` — grilă cu N coloane.
4. `StaggeredGridLayoutManager(spanCount, orientation)` — grilă cu înălțimi diferite.
5. Fără `setLayoutManager`, `RecyclerView` **nu afișează nimic** — și nu dă eroare.

**Unde revine:** în G1097 (capitolul 11), `MainActivity` folosește `LinearLayoutManager(this)`. Dacă ai vrea listă orizontală de postere, schimbi un rând.

</details>

---

## Pasul 12.5 — Comparația finală, pe aceleași date

### De ce

Trei ecrane, aceleași numere 1–100, același `item_number.xml` la treptele 2 și 3. Doar adapterul diferă.

### Tabelul care trebuie știut la test

| | Treapta 1 | Treapta 2 | Treapta 3 |
|---|---|---|---|
| Widget | `ListView` | `ListView` | `RecyclerView` |
| Adapter | `ArrayAdapter` | `BaseAdapter` propriu | `RecyclerView.Adapter` |
| Layout rând | `simple_list_item_1` (sistem) | `item_number.xml` | `item_number.xml` |
| Coloane per rând | 1 | 2 | 2 |
| `ViewHolder` | implicit, ascuns | **manual** (`setTag`/`getTag`) | **obligatoriu**, automat |
| Metoda de umplere | `getView()` | `getView()` | `onBindViewHolder()` |
| Metoda de creare | — | în `getView`, `if (convertView == null)` | `onCreateViewHolder()` |
| Aranjare | verticală fixă | verticală fixă | `LayoutManager` — configurabil |
| Animații | nu | nu | da |

### Ce răspunsuri dai la test

**„Ce diferență e între ListView și RecyclerView?"**
`RecyclerView` obligă `ViewHolder`, separă crearea de umplere (`onCreateViewHolder` / `onBindViewHolder`), delegă aranjarea unui `LayoutManager` și oferă animații. `ListView` are un singur `getView()` cu `if (convertView == null)` și aranjare fixă.

**„De ce ArrayAdapter nu ajunge?"**
Pentru că știe un singur `TextView` per rând. Pentru două coloane ai nevoie de un layout propriu și de un adapter care să-l umple.

**„Ce face convertView?"**
Refolosește rândurile care ies din ecran. Fără el, s-ar umfla 100 de rânduri pentru 100 de elemente.

---

## Pasul 12.6 — Verificare

### Cum

1. Deschide `DMA06` în Android Studio.
2. Rulează. Din meniu, apasă pe rând cele trei butoane.
3. Treapta 1: listă cu un număr pe rând.
4. Treapta 2: listă cu două coloane (zecimal | binar).
5. Treapta 3: aceleași două coloane, dar cu `RecyclerView`.
6. Derulează rapid prin toate trei. Treapta 3 ar trebui să fie cea mai fluidă.

### Ce verifici în cod

- [ ] `NumberData` nu are importuri `android.*`
- [ ] `item_number.xml` e folosit de **ambele** adaptere
- [ ] `NumberListAdapter extends BaseAdapter` cu 4 metode
- [ ] `NumberListAdapter` are `ViewHolder` + `setTag`/`getTag`
- [ ] `NumberRecyclerAdapter extends RecyclerView.Adapter<NumberRecyclerAdapter.NumberViewHolder>`
- [ ] `NumberViewHolder` e `static`
- [ ] `RecyclerViewActivity` cheamă `setLayoutManager` **înainte** de `setAdapter`

---

## Pasul 12.7 — Exercițiu de sinteză

**Cerință:** scrie din memorie `NumberRecyclerAdapter` complet, fără să te uiți. Ce trei metode are obligatoriu?

<details>
<summary>Răspuns — explicativ</summary>

**Trei metode obligatorii:**
1. `onCreateViewHolder(parent, viewType)` → `@NonNull NumberViewHolder`
2. `onBindViewHolder(holder, position)` → `void`
3. `getItemCount()` → `int`

Plus clasa `ViewHolder` interioară, `static`, care extinde `RecyclerView.ViewHolder`.

**De ce exact trei:** `RecyclerView.Adapter` le declară `abstract`. Dacă nu le implementezi, clasa nu compilează.

**Ce e opțional:** `getItemViewType`, `getItemId`, `onViewRecycled`, `onAttachedToRecyclerView` — toate au implementări implicite.

**De reținut:**
1. **Trei metode**, nu patru ca la `BaseAdapter` (`getCount`, `getItem`, `getItemId`, `getView`).
2. `getItemCount()` înlocuiește `getCount()`.
3. Nu există `getItem(position)` — îl scrii tu dacă ai nevoie, ca metodă proprie.

**Unde revine:** în capitolul 11, `MovieAdapter` are exact aceleași trei metode, doar că lucrează cu `Movie` în loc de `Integer`.

</details>

---

## Rezumat capitol 12

- `DMA06` = trei trepte pe aceleași date: `ArrayAdapter` → `BaseAdapter` → `RecyclerView.Adapter`.
- `item_number.xml` e comun treptelor 2 și 3 — diferența e doar în adapter.
- `convertView` + `ViewHolder` + `setTag`/`getTag` = reciclarea la `ListView`.
- `onCreateViewHolder` / `onBindViewHolder` = `getView` despărțit în două la `RecyclerView`.
- `LayoutManager` separă aranjarea de conținut.
- Fără `setLayoutManager`, `RecyclerView` e gol — fără eroare.

**Următorul capitol:** [13 - DMA05 - ViewBinding.md](13%20-%20DMA05%20-%20ViewBinding.md)
