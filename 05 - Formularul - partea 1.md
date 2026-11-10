# Capitolul 05 — Formularul, partea 1: structură și câmpuri de bază

**Obiectiv:** `activity_item.xml` — un `ScrollView` cu 4 carduri Material. În acest capitol construiești **structura** + **Card 1 (Basics)**: titlu, gen, dată lansare. Restul cardurilor vin în cap. 06.

**Timp estimat:** 45–60 min.

**Fișier final:** `cod-final/res/layout/activity_item.xml` (21505 B, 451 linii, SHA-256 `242620d52ee3be63…`)

> **Sfat:** acest fișier e cel mai mare din proiect. **Nu-l scrie dintr-o bucată.** Construiește-l card cu card, rulează după fiecare, verifică vizual. Un fișier de 451 linii scris orbește are șanse mari să aibă o etichetă neînchisă undeva.

---

## Pasul 5.1 — De ce `ScrollView` ca rădăcină

### De ce

Formularul are 4 carduri + buton, mult mai înalt decât un ecran de telefon. Fără scroll, ultimele câmpuri ar fi inaccesibile.

`ScrollView` face **exact un lucru**: permite derularea verticală a unui singur copil.

### Regula `ScrollView`

> `ScrollView` are voie cu **exact un copil**. Dacă pui doi, build-ul eșuează cu:
> `ScrollView can host only one direct child`

De aceea copilul e un `LinearLayout` vertical, care ține toate cardurile.

### Cum

```xml
<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="?attr/colorSurface"
    android:fillViewport="true"
    tools:context=".activities.ItemActivity">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingHorizontal="16dp"
        android:paddingTop="24dp"
        android:paddingBottom="24dp">

        <!-- cardurile -->

    </LinearLayout>
</ScrollView>
```

### Atributele, explicate

| Atribut | De ce |
|---|---|
| `android:id="@+id/main"` | pentru insets — la fel ca în `activity_main.xml` |
| `android:background="?attr/colorSurface"` | fundal din temă (alb în light, gri închis în dark). `?attr/` = atribut de temă, nu culoare fixă |
| `android:fillViewport="true"` | dacă conținutul e mai scurt decât ecranul, îl întinde să umple. Fără el, ai un fundal alb doar cât conținutul, restul gri |
| `paddingHorizontal="16dp"` | stânga + dreapta, 16dp (standard Material) |
| `paddingTop/Bottom="24dp"` | spațiu sus/jos |

### De ce `?attr/colorSurface` și nu `#FFFFFF`

`?attr/colorSurface` **rezolvă la culoarea din temă**. În light mode = alb, în dark mode = gri închis. Dacă ai scrie `#FFFFFF`, în dark mode ai avea alb pe negru — textul alb ar fi invizibil.

> **De reținut:** `?attr/nume` = „întreabă tema”. `@color/nume` = „folosește culoarea fixă”. Pentru culori de suprafață, text și contur, **întotdeauna** `?attr/`.

### `paddingHorizontal` vs `paddingStart/End`

`paddingHorizontal` e o scurtătură pentru `paddingLeft` + `paddingRight`. Dar în RTL (arabă), `paddingLeft` rămâne stânga fizică, ceea ce e greșit. Varianta corectă RTL-ar fi `paddingStart` + `paddingEnd`.

> **Atenție:** `android:paddingHorizontal` a fost introdus în API 26. Repo-ul are `minSdk 33`, deci e OK. Pe API mai vechi, ar fi trebuit `paddingLeft` + `paddingRight` sau `paddingStart` + `paddingEnd`.

### Exercițiu 5.1

**Cerință:** scoate `android:fillViewport="true"`. Rulează pe un emulator înalt și observă fundalul. Apoi pune-l la loc.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am eliminat `android:fillViewport="true"` din `ScrollView`.

**Ce se vede:** dacă formularul e mai scurt decât ecranul (nu e cazul aici, dar imaginează-ți), `LinearLayout`-ul copil se întinde doar cât conținutul. Restul ecranului rămâne cu fundalul **ferestrei** (care poate fi altă culoare), nu cu `colorSurface`.

**De ce:** `ScrollView` măsoară copilul cu `wrap_content` (înălțimea conținutului). `fillViewport="true"` îi spune: „dacă e mai mic decât viewport-ul, întinde-l la înălțimea viewport-ului”.

**De reținut:**
1. `fillViewport` e util când vrei ca fundalul să acopere tot ecranul, indiferent de conținut.
2. În `activity_item.xml` conținutul e oricum mai înalt decât ecranul, deci efectul e vizibil doar pe tablete sau landscape.
3. E o bună practică să-l pui mereu pe `ScrollView` cu un singur copil `LinearLayout`.

**Unde revine:** nu revine explicit, dar e relevant la cap. 11 dacă adaugi un `RecyclerView` într-un `ScrollView` — acolo `fillViewport` nu ajută, pentru că `RecyclerView` are scroll propriu. Se rezolvă cu `nestedScrollingEnabled="false"` sau, mai bine, cu un singur `RecyclerView` cu headere.

</details>

---

## Pasul 5.2 — Header-ul formularului

### De ce

Primele două `TextView`-uri nu sunt într-un card. Sunt titlul ecranului („Movie details”) și un subtitlu („Fill in the information below and save.”). Rol: orientare.

### Cum

```xml
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Movie details"
    android:textAppearance="?attr/textAppearanceHeadlineMedium"
    android:textColor="?attr/colorOnSurface"
    android:textStyle="bold" />

<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:layout_marginBottom="20dp"
    android:text="Fill in the information below and save."
    android:textAppearance="?attr/textAppearanceBodyMedium"
    android:textColor="?attr/colorOnSurfaceVariant" />
```

### De ce `textAppearance` și nu `textSize`

`?attr/textAppearanceHeadlineMedium` e un **stil complet** din tema Material 3: dimensiune, greutate, spațiere, înălțime de linie. `textSize="28sp"` ar da doar dimensiunea, fără restul.

> **De reținut:** în Material 3 folosești **tipografia temei** (`textAppearance*`), nu valori hardcodate. Așa arată consecvent pe toate ecranele.

### Ierarhia de culori

| Atribut | Rol | Unde se folosește |
|---|---|---|
| `?attr/colorOnSurface` | text principal | titluri, valori |
| `?attr/colorOnSurfaceVariant` | text secundar | subtitluri, etichete |
| `?attr/colorPrimary` | accent | titluri de secțiune, valori active |
| `?attr/colorOutline` | contur | borduri de câmpuri |
| `?attr/colorOutlineVariant` | contur slab | separatoare |

Această ierarhie e **întreaga filozofie Material 3**: nu alegi culori, alegi **roluri**. Tema le rezolvă.

### Exercițiu 5.2

**Cerință:** schimbă `?attr/textAppearanceHeadlineMedium` cu `?attr/textAppearanceDisplayLarge`. Rulează. Ce observi? Revino.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat stilul de tipografie al titlului.

**Ce se vede:** „Movie details” devine **uriaș** (Display Large e ~57sp în Material 3, față de Headline Medium ~28sp). Probabil se rupe pe două rânduri.

**De ce:** `textAppearance*` sunt **scări** definite de Material 3. Fiecare are dimensiune, greutate, letter-spacing și line-height proprii.

**De reținut:**
1. Scara Material 3: `DisplayLarge/Medium/Small`, `HeadlineLarge/Medium/Small`, `TitleLarge/Medium/Small`, `BodyLarge/Medium/Small`, `LabelLarge/Medium/Small`.
2. Regula de aur: **un singur `Display`** per ecran (dacă e nevoie), `Headline` pentru titluri de ecran, `Title` pentru titluri de secțiune, `Body` pentru text, `Label` pentru etichete de câmp.
3. Nu amesteca `textSize` cu `textAppearance` — al doilea îl suprascrie pe primul.

**Unde revine:** în tot restul formularului. Vei vedea `TitleMedium` pe titlurile cardurilor („Basics”, „Production”), `LabelLarge` pe etichetele câmpurilor („Title”, „Genre”), `LabelSmall` pe valorile min/max ale `SeekBar`-ului.

</details>

---

## Pasul 5.3 — `MaterialCardView` ca container de secțiune

### De ce

Formularul e împărțit în 4 secțiuni vizuale: **Basics**, **Production**, **Your verdict**, **Poster**. Fiecare e un card cu colțuri rotunjite și fundal ușor diferit.

`MaterialCardView` e containerul. Nu e doar „o cutie cu umbră” — e o componentă Material cu stiluri predefinite.

### Cum

```xml
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

        <!-- conținutul cardului -->

    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

### Atributele, explicate

| Atribut | De ce |
|---|---|
| `style="?attr/materialCardViewFilledStyle"` | stil Material 3: fundal `surfaceContainerHighest`, fără umbră. Alternativa: `materialCardViewOutlinedStyle` (fundal transparent, contur) |
| `layout_marginBottom="16dp"` | spațiu între carduri |
| `app:cardCornerRadius="20dp"` | colțuri rotunjite (Material 3 folosește 12–28dp) |
| `LinearLayout` vertical + `padding="16dp"` | conținutul e stivuit vertical, cu padding interior |

### De ce `style` și nu atribute individuale

`style="?attr/materialCardViewFilledStyle"` aduce **un set întreg** de atribute (fundal, umbră, contur, ripple). Dacă le-ai scrie individual, ai rata unele și ai pierde consistența cu tema.

> **De reținut:** `style` = set de atribute reutilizabile. În Material 3, stilurile sunt expuse ca `?attr/...` ca să poată fi suprascrise de temă.

### De ce `wrap_content` la înălțime

Cardul trebuie să crească după conținut. `match_parent` ar face fiecare card să umple tot ecranul.

### Exercițiu 5.3

**Cerință:** schimbă `materialCardViewFilledStyle` cu `materialCardViewOutlinedStyle` pe primul card. Rulează. Ce diferență vezi?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat stilul primului card.

**Ce se vede:**
- **Filled**: fundal gri-deschis (în light mode), fără umbră, fără contur. Cardul „iese” prin culoare.
- **Outlined**: fundal transparent (sau `surface`), cu un contur subțire de 1dp în `colorOutline`. Cardul „iese” prin linie.

**De ce:** Material 3 are două stiluri de card pentru două contexte. `Filled` pentru conținut care trebuie să iasă în evidență; `Outlined` pentru liste dense sau când vrei mai puțină greutate vizuală.

**De reținut:**
1. Ambele stiluri respectă tema (light/dark) automat.
2. `Outlined` are `cardElevation=0`; `Filled` are și el 0 în M3 (umbrele au fost înlocuite de tonuri).
3. Nu amesteca stilurile în același ecran fără motiv — aici toate 4 cardurile sunt `Filled`.

**Unde revine:** `movie_item.xml` (cap. 11) folosește `MaterialCardView` **fără** `style`, cu `app:cardElevation="3dp"` explicit — pentru că acolo cardul e un element de listă, nu o secțiune de formular. Vei vedea diferența de abordare.

</details>

---

## Pasul 5.4 — `TextInputLayout` + `TextInputEditText`

### De ce

Un `EditText` simplu arată ca o linie. `TextInputLayout` e **containerul** care adaugă:

- hint plutitor (label care se ridică când tastezi);
- contur (outlined) sau fundal (filled);
- iconițe start/end;
- mesaje de eroare;
- prefix/sufix.

`TextInputEditText` e `EditText`-ul specializat care funcționează corect în interiorul lui `TextInputLayout`.

> **Regula:** `TextInputLayout` are **exact un** copil, care trebuie să fie `TextInputEditText` (sau `TextInputLayout` imbricat, dar rar).

### Cum — câmpul „Title”

```xml
<TextView
    android:id="@+id/tvTile"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Title"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginBottom="16dp"
    app:hintEnabled="false"
    app:endIconMode="clear_text">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Movie title"
        android:inputType="textCapWords" />
</com.google.android.material.textfield.TextInputLayout>
```

### De ce un `TextView` separat deasupra

Ai putea folosi `hint`-ul lui `TextInputLayout` ca etichetă. Dar repo-ul alege altă abordare: un `TextView` **deasupra** („Title”), plus `app:hintEnabled="false"` care dezactivează hint-ul plutitor, plus `android:hint` pe `TextInputEditText` ca placeholder.

**De ce?** Pentru că eticheta deasupra rămâne **vizibilă mereu**, inclusiv când câmpul e completat. Hint-ul plutitor se mută în contur și devine mic. Pentru un formular lung, eticheta fixă e mai lizibilă.

> **Capcană de nume:** `android:id="@+id/tvTile"` — „Tile”, nu „Title”. E o **typo în repo**. Nu o corecta dacă vrei fidelitate, dar știi că e typo. În cod nu e folosită (nu apare în `initControls`), deci nu strică nimic.

### `app:hintEnabled="false"`

Dezactivează hint-ul plutitor al lui `TextInputLayout`. Dacă ar fi `true` (implicit), ai avea **două** etichete: `TextView`-ul de deasupra și hint-ul plutitor din contur. Redundant.

### `app:endIconMode="clear_text"`

Adaugă un „X” în dreapta câmpului, care șterge textul. Util la câmpuri lungi.

Valori posibile: `none`, `clear_text`, `password_toggle`, `dropdown_menu`, `custom`.

### `android:inputType`

| Valoare | Efect |
|---|---|
| `textCapWords` | tastatură text, fiecare cuvânt cu majusculă |
| `numberDecimal` | tastatură numerică cu zecimale |
| `date` | tastatură cu cifre și `/` |
| `textUri` | tastatură cu `/` și `.com` |

`inputType` face **două** lucruri: alege tastatura și **restricționează** caracterele acceptate.

### Exercițiu 5.4

**Cerință:** schimbă `inputType` din `textCapWords` în `textPassword` pe câmpul Title. Rulează, scrie ceva. Ce se întâmplă? De ce nu ai face asta niciodată aici?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat `android:inputType="textCapWords"` în `android:inputType="textPassword"`.

**Ce se vede:** textul tastat apare ca **puncte** (••••). Tastatura e text normal, dar caracterele sunt mascate.

**De ce:** `textPassword` e un flag care spune `EditText`-ului să mascheze textul și să nu-l salveze în sugestii. E pentru parole, evident.

**De reținut:**
1. `inputType` combină **trei** dimensiuni: clasă (text/number/phone), variație (capWords, password) și flags (noSuggestions, visiblePassword).
2. `textPassword` pe un titlu de film ar face aplicația inutilizabilă — dar e o demonstrație bună că `inputType` **schimbă comportamentul**, nu doar tastatura.
3. Pentru URL-uri, `textUri` e alegerea corectă (cap. 06, poster).

**Unde revine:** la câmpul Budget (`numberDecimal`) și Poster (`textUri`). Vei vedea că `numberDecimal` **respinge literele** — dacă încerci să tastezi „abc”, nu se întâmplă nimic.

</details>

---

## Pasul 5.5 — `Spinner` cu `android:entries`

### De ce

Genul e o alegere din 10 opțiuni fixe. Un `Spinner` (dropdown) e widget-ul potrivit: ocupă puțin spațiu, arată opțiunile la cerere.

### Cum

Repo-ul învelește `Spinner`-ul într-un `MaterialCardView` ca să-i dea un contur care arată ca al celorlalte câmpuri `OutlinedBox`:

```xml
<TextView
    android:id="@+id/tvGenre"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Genre"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.card.MaterialCardView
    style="?attr/materialCardViewOutlinedStyle"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:layout_marginBottom="16dp"
    app:cardBackgroundColor="@android:color/transparent"
    app:cardCornerRadius="4dp"
    app:strokeColor="?attr/colorOutline">

    <Spinner
        android:id="@+id/spGenre"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/movie_genre"
        android:paddingStart="4dp"
        android:spinnerMode="dropdown" />
</com.google.android.material.card.MaterialCardView>
```

### De ce trucul cu `MaterialCardView`

`Spinner`-ul nativ nu are contur. Ca să arate consecvent cu `TextInputLayout`-urile `OutlinedBox` (care au contur de 1dp, colțuri 4dp), îl învelești într-un card `Outlined` cu:

- `cardBackgroundColor="@android:color/transparent"` — ca să nu acopere fundalul cardului părinte;
- `cardCornerRadius="4dp"` — același ca `TextInputLayout`;
- `strokeColor="?attr/colorOutline"` — aceeași culoare de contur;
- `layout_height="56dp"` — înălțimea standard a unui câmp Material.

Rezultatul: vizual, arată ca un câmp `OutlinedBox` cu dropdown.

### `android:entries` vs adapter

Ca și la `ListView`, `android:entries="@array/movie_genre"` creează automat un `ArrayAdapter<String>` din resursă. Aici **nu** e înlocuit de cod — `ItemActivity` nu apelează `spGenre.setAdapter(...)`. Deci `entries` e sursa reală.

> **De reținut:** la `ListView` din `MainActivity`, `entries` era înlocuit de `setAdapter`. La `Spinner`, `entries` rămâne. Aceeași sintaxă, comportamente diferite în funcție de ce face codul.

### `spinnerMode="dropdown"`

Două moduri:
- `dropdown` — un popup sub spinner (implicit pe Android modern);
- `dialog` — un dialog modal.

`dropdown` e mai rapid pentru liste scurte.

### Exercițiu 5.5

**Cerință:** adaugă un al doilea `Spinner` sub gen, pentru „Limba” (Română, Engleză, Franceză), cu `android:id="@+id/spLanguage"`. Nu-l folosi în cod. Verifică vizual.

<details>
<summary>Indiciu</summary>

Cel mai simplu: adaugi un `string-array` nou în `strings.xml` și copiezi structura `TextView` + `MaterialCardView` + `Spinner`.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat în `strings.xml`:

```xml
<string-array name="movie_language">
    <item>Română</item>
    <item>Engleză</item>
    <item>Franceză</item>
</string-array>
```

și în layout, după blocul Genre:

```xml
<TextView
    android:id="@+id/tvLanguage"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Language"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<com.google.android.material.card.MaterialCardView
    style="?attr/materialCardViewOutlinedStyle"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:layout_marginBottom="16dp"
    app:cardBackgroundColor="@android:color/transparent"
    app:cardCornerRadius="4dp"
    app:strokeColor="?attr/colorOutline">

    <Spinner
        android:id="@+id/spLanguage"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:entries="@array/movie_language"
        android:paddingStart="4dp"
        android:spinnerMode="dropdown" />
</com.google.android.material.card.MaterialCardView>
```

**Cum verifici:** rulează, apeși spinner-ul, vezi cele 3 limbi. Nu se salvează nicăieri — e doar vizual.

**De ce funcționează fără cod:** `android:entries` e suficient pentru populare. `Spinner` își creează singur adapterul.

**De reținut:**
1. `Spinner` **fără** `entries` și **fără** `setAdapter` = gol.
2. `Spinner` cu `entries` = populat, fără nicio linie de cod.
3. Ca să citești selecția: `spGenre.getSelectedItem().toString()`.

**Unde revine:** în cap. 07, `saveMovie()` face exact `movie.setGenre(spGenre.getSelectedItem().toString())`. Iar `fillForm` caută textul în listă ca să seteze selecția — pentru că `Spinner` nu are `setSelectionByText`, doar `setSelection(index)`.

</details>

---

## Pasul 5.6 — Câmpul dată: `TextInputLayout` cu iconiță

### De ce

Data lansării nu se tastează — se alege dintr-un calendar. Dar câmpul trebuie să arate ca un câmp normal, cu iconiță de calendar.

### Cum

```xml
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:hintEnabled="true"
    app:startIconContentDescription="Release date"
    app:startIconDrawable="@android:drawable/ic_menu_my_calendar">

    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/etRelease"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Release date"
        android:inputType="date" />
</com.google.android.material.textfield.TextInputLayout>
```

### Diferența față de câmpul Title

| | Title | Release |
|---|---|---|
| `hintEnabled` | `false` | **`true`** |
| etichetă separată deasupra | da (`tvTile`) | **nu** |
| iconiță start | nu | **da** (`ic_menu_my_calendar`) |
| `inputType` | `textCapWords` | `date` |

Aici se folosește hint-ul plutitor: „Release date” urcă în contur când scrii. Nu ai `TextView` deasupra.

**De ce abordări diferite?** Inconsecvență de design în repo. Ambele funcționează. La test, dacă ți se cere să explici, spui: „câmpul Title are etichetă fixă; câmpul Release folosește hint plutitor”. Nu e o greșeală, e o alegere.

### `app:startIconDrawable`

Iconița din stânga. `@android:drawable/ic_menu_my_calendar` e o iconiță **din sistem** (Android o are de la API 1). Nu ai nevoie de un fișier propriu.

### `app:startIconContentDescription`

Text pentru TalkBack. Obligatoriu când ai `startIconDrawable`, altfel lint-ul dă eroare.

### De ce `inputType="date"` deși câmpul e read-only în practică

Utilizatorul **nu tastează** data — o alege din `DatePickerDialog` (cap. 07). Dar `inputType="date"` face tastatura să fie numerică cu `/`, în caz că vrea să scrie manual. Iar `SimpleDateFormat` din cod poate parsa „16/07/2010”.

> **Atenție:** câmpul **nu e** `editable=false`. Utilizatorul poate tasta. Dar `showReleaseDatePicker()` parsează textul existent, deci dacă tastează ceva invalid, `ParseException` e **ignorată** (`catch (ParseException ignored) { }`) și calendarul pornește de la data curentă. Vezi cap. 07.

### Exercițiu 5.6

**Cerință:** adaugă `app:endIconMode="clear_text"` la câmpul Release. Rulează, scrie o dată, apasă X. Ce se întâmplă cu `releaseCal`?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat `app:endIconMode="clear_text"` la `TextInputLayout`-ul datei.

**Ce se vede:** apare un X în dreapta. Îl apeși, textul dispare.

**Ce se întâmplă cu `releaseCal`:** **nimic.** `releaseCal` rămâne la valoarea ei anterioară (sau la `Calendar.getInstance()` dacă n-ai ales niciodată o dată).

**De ce:** `clear_text` șterge **doar textul din `EditText`**. Nu are nicio legătură cu `releaseCal`, care e un câmp Java separat. La `saveMovie()`, `movie.setRelease(releaseCal.getTime())` — deci filmul va primi **data veche**, nu `null`, deși câmpul e gol.

**De reținut:**
1. **Sursa de adevăr** e `releaseCal`, nu textul din `EditText`. Textul e doar o reprezentare.
2. Dacă vrei ca ștergerea să reseteze data, trebuie să adaugi un listener pe `endIconMode` sau să verifici în `saveMovie` dacă textul e gol.
3. E un **bug real** în repo: poți salva un film cu data pe care ai ales-o anterior, deși câmpul pare gol.

**Unde revine:** în cap. 07, `showReleaseDatePicker()` **parsează textul** ca să inițializeze calendarul. Dacă textul e gol, `releaseCal` rămâne cum era. Deci ștergerea textului nu resetează nimic — și e o capcană pe care o vei vedea la test.

</details>

---

## Pasul 5.7 — Verificare vizuală a Cardului 1

### Cum

1. Rulează. Deschide `ItemActivity` — dar **nu ai încă navigare**. Deci temporar, ca să vezi layout-ul:
   - Deschide `activity_item.xml` → tab **Design**.
   - Sau schimbă temporar `setContentView(R.layout.activity_main)` în `MainActivity` cu `setContentView(R.layout.activity_item)`. **Revino imediat după.**
2. Verifică:
   - Titlul „Movie details” sus.
   - Cardul „Basics” cu eticheta „Basics” în `colorPrimary`.
   - Câmpul Title cu etichetă deasupra și X în dreapta.
   - Spinner-ul Genre cu contur, înălțime 56dp.
   - Câmpul Release cu iconiță de calendar în stânga.

### Checklist

- [ ] `ScrollView` cu `android:id="@+id/main"`, `fillViewport="true"`, `background="?attr/colorSurface"`
- [ ] copil unic `LinearLayout` vertical, padding 16/24/24
- [ ] header: 2 `TextView`
- [ ] Card 1 `MaterialCardView` cu `materialCardViewFilledStyle`, `cardCornerRadius="20dp"`
- [ ] în card: `LinearLayout` vertical, padding 16dp
- [ ] etichetă „Basics” cu `TitleMedium` + `colorPrimary`
- [ ] `tvTile` + `TextInputLayout` (hintEnabled=false, endIconMode=clear_text) + `etTitle`
- [ ] `tvGenre` + `MaterialCardView` outlined + `Spinner` cu `entries`
- [ ] `TextInputLayout` cu `startIconDrawable` + `etRelease`

---

## Pasul 5.8 — Exercițiu de reflecție

**Cerință:** de ce `TextInputLayout` are `layout_width="match_parent"` dar `TextView`-ul etichetă are `wrap_content`?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** etichetele (`tvTile`, `tvGenre`) sunt `wrap_content`; câmpurile (`TextInputLayout`, `MaterialCardView` cu spinner) sunt `match_parent`.

**De ce:** o etichetă trebuie să ocupe **doar cât textul**. Dacă ar fi `match_parent`, ar fi o cutie invizibilă lată de tot ecranul — fără efect vizual, dar fără sens. Un câmp trebuie să ocupe **toată lățimea** disponibilă, ca să ai loc să tastezi.

**De reținut:**
1. `wrap_content` = cât conținutul.
2. `match_parent` = cât părintele.
3. `0dp` + `layout_weight` = împarte spațiul rămas (vezi cap. 06, la rândul Duration).

**Unde revine:** în cap. 06, rândul cu `tvDuration` + `tvDurationValue` folosește `0dp` + `layout_weight="1"` pe primul, ca să împingă valoarea în dreapta. Trei moduri de dimensionare, trei scopuri.

</details>

---

## Rezumat capitol 05

- `ScrollView` = un singur copil, `fillViewport` pentru fundal complet.
- `MaterialCardView` cu `style="?attr/materialCardViewFilledStyle"` = secțiune.
- `TextInputLayout` + `TextInputEditText` = câmp cu contur, iconițe, hint.
- `hintEnabled="false"` + `TextView` deasupra = etichetă fixă.
- `Spinner` în `MaterialCardView` outlined = dropdown cu aspect de câmp.
- `?attr/color*` = roluri de culoare, nu culori fixe.

**Următorul capitol:** [06 - Formularul - partea 2.md](06%20-%20Formularul%20-%20partea%202.md)
