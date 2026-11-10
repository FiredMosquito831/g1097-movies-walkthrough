# Capitolul 06 — Formularul, partea 2: restul câmpurilor

**Obiectiv:** Cardurile 2 (Production), 3 (Your verdict) și 4 (Poster) + butonul Save. La final ai `activity_item.xml` complet, 451 linii.

**Timp estimat:** 45–60 min.

---

## Pasul 6.1 — Card 2: Budget

### De ce

Bugetul e un număr cu zecimale. `TextInputLayout` cu `prefixText` afișează „$ ” în față, fără să fie parte din valoare.

### Cum

```xml
<TextView
    android:id="@+id/tvBudget"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Budget"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

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
```

### `app:prefixText` vs `android:drawableStart`

`prefixText="$ "` e un **text** care apare în câmp, înaintea valorii tastate. Nu e parte din textul returnat de `getText()`.

`drawableStart` ar fi o **imagine** — nu poți scrie „$” ca imagine fără un vector.

> **De reținut:** `prefixText` și `suffixText` sunt doar vizuale. `etBudget.getText().toString()` întoarce **doar** numărul, fără „$”.

### Capcana `Double.parseDouble`

În `saveMovie()`:

```java
movie.setBudget(Double.parseDouble(etBudget.getText().toString()));
```

Dacă câmpul e **gol**, `Double.parseDouble("")` aruncă `NumberFormatException` → aplicația crăpă la Save.

> Aceasta e o **problemă reală** în codul repo-ului la `d719ffc`. Versiunea ta locală de sync (modificarea necomisă) o repară cu un `if (!budgetText.isEmpty())` + `try/catch`. Vezi cap. 07, pasul 7.8.

### Exercițiu 6.1

**Cerință:** ce se întâmplă dacă tastezi `1,5` (cu virgulă) în loc de `1.5`? Testează pe emulator cu tastatură românească.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am testat introducerea unei virgule zecimale.

**Ce se vede:** depinde de tastatură și de `Locale`:
- Pe tastatură cu `,` ca separator zecimal (română), poți tasta `1,5`.
- `Double.parseDouble("1,5")` → **`NumberFormatException`**. `parseDouble` acceptă **doar** punct.

**De ce:** `Double.parseDouble` e independent de `Locale`. Acceptă formatul „invariant” (`1.5`, `1.5E10`). Nu acceptă virgulă.

**De reținut:**
1. `Double.parseDouble` ≠ `NumberFormat` cu `Locale`. Primul e strict, al doilea e localizat.
2. Dacă vrei să accepți virgula, folosești `NumberFormat.getInstance(locale).parse(text)`.
3. `android:inputType="numberDecimal"` afișează tastatura cu separatorul **local** — deci pe română vei vedea virgulă, și parseDouble va crăpa.

**Unde revine:** în cap. 07, `saveMovie` are exact această problemă. E un bug pe care versiunea ta locală îl repară. La test, dacă ți se cere „ce se întâmplă dacă introduc 1,5”, răspunsul e: `NumberFormatException`.

</details>

---

## Pasul 6.2 — Card 2: Duration cu `SeekBar`

### De ce

Durata e un număr între 0 și 300. Un `SeekBar` e mai rapid decât tastarea și arată vizual poziția în interval.

### Cum — rândul cu etichetă + valoare

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:orientation="horizontal">

    <TextView
        android:id="@+id/tvDuration"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="Duration"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorOnSurfaceVariant" />

    <TextView
        android:id="@+id/tvDurationValue"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="0 min"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorPrimary"
        tools:text="148 min" />
</LinearLayout>
```

### `0dp` + `layout_weight="1"` — mecanismul

Într-un `LinearLayout` orizontal:

1. Copiii cu `wrap_content` / `match_parent` își iau spațiul.
2. **Spațiul rămas** se împarte între copiii cu `layout_weight`.
3. Un copil cu `layout_width="0dp"` + `layout_weight="1"` primește **tot** spațiul rămas.

Aici: `tvDuration` (0dp, weight 1) ia tot spațiul rămas după ce `tvDurationValue` (wrap_content) își ia cât are nevoie. Efectul: valoarea e împinsă în dreapta.

> **Regula:** `0dp` + `weight` e echivalentul a „umple ce rămâne”. `match_parent` + `weight` ar da rezultate neintuitive.

### `tools:text` vs `android:text`

- `android:text="0 min"` — valoarea **reală** la runtime.
- `tools:text="148 min"` — valoarea din **preview**, ignorată la build.

De ce ambele? Ca să vezi în preview cum arată cu o valoare realistă, dar la runtime să pornească de la 0.

### Cum

```xml
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
```

### Atributele `SeekBar`

| Atribut | Sens |
|---|---|
| `android:max="300"` | valoarea maximă |
| `android:min="0"` | valoarea minimă (**API 26+**) |
| `progressTint` | culoarea părții umplute |
| `thumbTint` | culoarea mânerului |
| `tools:progress="148"` | poziția în preview |

> **Atenție:** `android:min` pe `SeekBar` e disponibil **doar din API 26**. Repo-ul are `minSdk 33`, deci merge. Pe API mai vechi, `min` e mereu 0.

### De ce rândul cu „0 min” / „300 min”

E o etichetă de interval. Utilizatorul știe ce înseamnă capetele barei. Fără ea, ar ghici.

### Exercițiu 6.2

**Cerință:** schimbă `android:max` la `600`. Rulează. Ce se întâmplă cu textul „300 min” de sub bară? De ce e o problemă?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat doar `android:max="600"`, lăsând textul „300 min”.

**Ce se vede:** bara merge până la 600, dar eticheta de sub ea spune în continuare „300 min”. **Inconsecvență vizuală.**

**De ce:** cele două sunt **independente**. `android:max` e proprietatea barei; „300 min” e un `TextView` scris de mână. Nimic nu le sincronizează.

**De reținut:**
1. Într-un layout, valorile numerice apar adesea în **două locuri**: în atribut și în text. Dacă schimbi una, trebuie să o schimbi și pe cealaltă.
2. Soluția corectă: textul din dreapta să fie generat din `android:max` la runtime, sau folosit un `string` cu format (`%1$d min`).
3. Aici e o **datorie tehnică** asumată: valorile sunt hardcodate în două locuri.

**Unde revine:** în cap. 07, `tvDurationValue` e actualizat la runtime din `seekBar.getProgress()`. Dar eticheta „300 min” rămâne hardcodată. Dacă schimbi `max`, trebuie să schimbi și textul.

</details>

---

## Pasul 6.3 — Card 3: RatingBar

### De ce

Rating-ul e o notă de la 0 la 5, cu jumătăți de stea. `RatingBar` e widget-ul dedicat: arată stele, permite atingere.

### Cum

```xml
<TextView
    android:id="@+id/tvRating"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Rating"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

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
```

### Atributele, explicate

| Atribut | Sens |
|---|---|
| `android:numStars="5"` | câte stele |
| `android:stepSize="0.5"` | pasul: jumătate de stea |
| `progressTint="#FFC107"` | culoarea stelelor pline — **galben Material** |
| `secondaryProgressTint` | culoarea stelelor parțiale |
| `progressBackgroundTint` | culoarea stelelor goale |
| `layout_gravity="center_horizontal"` | centrează bara în card |
| `tools:rating="3.5"` | valoarea din preview |

### De ce `#FFC107` hardcodat

E o excepție asumată: galbenul de stele nu e în tema Material 3 ca rol. Puteai defini un `color` în `colors.xml`, dar repo-ul l-a pus direct.

> **De reținut:** culorile hardcodate sunt acceptabile pentru **semnificații fixe** (stele = galben, indiferent de temă). Pentru tot restul, `?attr/`.

### De ce `layout_gravity` și nu `gravity`

`RatingBar` nu are conținut intern de aliniat. Vrei să-l centrezi **pe el** în card → `layout_gravity`.

### Exercițiu 6.3

**Cerință:** schimbă `stepSize` la `1`. Rulează. Poți da 3.5 stele?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat `android:stepSize="0.5"` în `android:stepSize="1"`.

**Ce se vede:** poți da doar valori întregi: 1, 2, 3, 4, 5. Nu poți selecta 3.5.

**De ce:** `stepSize` definește **granularitatea**. Cu 1, fiecare atingere sare la următoarea stea întreagă. Cu 0.5, poți selecta jumătăți.

**De reținut:**
1. `stepSize` e independent de `numStars`. Poți avea 5 stele cu pas 0.1 (50 de valori posibile).
2. `getRating()` întoarce `float` — deci poate returna 3.5, 2.0, etc.
3. Dacă `stepSize` nu împarte exact `numStars`, ultima stea poate fi inaccesibilă.

**Unde revine:** în `movie_item.xml` (cap. 11), `RatingBar`-ul e `isIndicator="true"` — doar afișare, nu interactiv. Deci `stepSize` contează doar pentru **afișare** acolo, nu pentru input.

</details>

---

## Pasul 6.4 — Card 3: rândul cu `MaterialSwitch` și `MaterialCheckBox`

### De ce

Două opțiuni booleene **independente**:
- „Recommended” (switch) — filmul e recomandat?
- „Watchlist” (checkbox) — e pe lista de urmărit?

### Cum

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:minHeight="48dp"
    android:orientation="horizontal">

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">

        <TextView
            android:id="@+id/tvWatched"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Recommended"
            android:textAppearance="?attr/textAppearanceBodyLarge"
            android:textColor="?attr/colorOnSurface" />

        <TextView
            android:id="@+id/tvWatchedValue"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="No"
            android:textAppearance="?attr/textAppearanceLabelLarge"
            android:textColor="?attr/colorPrimary" />
    </LinearLayout>

    <com.google.android.material.materialswitch.MaterialSwitch
        android:id="@+id/swWatched"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginEnd="12dp" />

    <com.google.android.material.checkbox.MaterialCheckBox
        android:id="@+id/cbOnWatchList"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Watchlist" />
</LinearLayout>
```

### Structura, explicată

```
LinearLayout orizontal (minHeight 48dp)
├── LinearLayout vertical (weight 1)        ← textul, ia spațiu rămas
│   ├── TextView "Recommended"
│   └── TextView "No"                        ← valoarea, actualizată din cod
├── MaterialSwitch                            ← bifă glisantă
└── MaterialCheckBox "Watchlist"              ← bifă pătrată
```

### De ce două widget-uri diferite pentru același tip de date

Ambele sunt `boolean`, dar au **semnificații UI diferite**:

- **Switch** = „pornit/oprit” — o stare a întregului ecran sau a unei acțiuni.
- **Checkbox** = „bifez un element dintr-o listă de opțiuni” — o selecție.

Aici: „Recommended” e o **stare** (filmul e recomandat sau nu), „Watchlist” e o **selecție** (îl adaug pe listă). E o distincție subtilă de design, nu tehnică.

### `minHeight="48dp"`

Înălțimea minimă pentru un element **atingibil**. Ghidul Material: orice element interactiv trebuie să aibă cel puțin 48×48dp. Altfel, utilizatorul ratează.

### `tvWatchedValue`

Un `TextView` care arată „Yes” / „No” **în plus** față de switch. Redundant vizual, dar util: utilizatorul vede starea și în text, nu doar prin poziția mânerului.

Actualizat în cod (cap. 07):

```java
swWatched.setOnCheckedChangeListener((buttonView, isChecked) ->
    tvWatchedValue.setText(isChecked ? "Yes" : "No"));
```

### Exercițiu 6.4

**Cerință:** înlocuiește `MaterialSwitch` cu un al doilea `MaterialCheckBox` (id `cbWatched`). Ce se schimbă vizual? Ce se schimbă în cod?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat widget-ul.

```xml
<com.google.android.material.checkbox.MaterialCheckBox
    android:id="@+id/cbWatched"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginEnd="12dp" />
```

**Ce se vede:** în loc de o bifă glisantă, ai o bifă pătrată fără text. Funcțional, la fel.

**Ce se schimbă în cod:** **tot.** `swWatched` nu mai există, deci:
- `findViewById(R.id.swWatched)` → `null` (sau eroare de compilare dacă ai șters ID-ul)
- `swWatched.setChecked(...)` → NPE
- `swWatched.isChecked()` → NPE
- listener-ul `setOnCheckedChangeListener` nu se mai poate atașa

**De ce:** `MaterialSwitch` și `MaterialCheckBox` sunt **clase diferite** (`com.google.android.material.materialswitch.MaterialSwitch` vs `com.google.android.material.checkbox.MaterialCheckBox`), deși ambele extind `CompoundButton`. Câmpul din cod e declarat `MaterialSwitch swWatched;` — trebuie schimbat tipul.

**De reținut:**
1. **ID-ul leagă XML de cod.** Dacă schimbi ID-ul, trebuie să schimbi și `findViewById`.
2. Ambele sunt `CompoundButton`, deci `setOnCheckedChangeListener` merge pe amândouă.
3. `MaterialCheckBox` are `text="Watchlist"` — textul e lângă bifă. `MaterialSwitch` nu are text.

**Unde revine:** în cap. 11, `movie_item.xml` folosește `Chip`-uri pentru a arăta starea („Watched”, „Watchlist”) — o a treia reprezentare vizuală a acelorași date. Vei vedea că **același model** se poate afișa în multe feluri.

</details>

---

## Pasul 6.5 — Card 3: `RadioGroup` cu `MaterialRadioButton`

### De ce

Ghidajul parental e **o singură alegere din 5**. `RadioGroup` garantează că doar un buton e selectat.

### Cum

```xml
<TextView
    android:id="@+id/tvGuidance"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginBottom="4dp"
    android:text="Guidance"
    android:textAppearance="?attr/textAppearanceLabelLarge"
    android:textColor="?attr/colorOnSurfaceVariant" />

<HorizontalScrollView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:scrollbars="none">

    <RadioGroup
        android:id="@+id/rgApproval"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="horizontal">

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
```

### De ce `HorizontalScrollView`

5 butoane pe orizontală nu încap pe un ecran îngust (ex. 360dp). `HorizontalScrollView` permite derulare orizontală dacă nu încap.

`scrollbars="none"` ascunde bara de scroll (inutilă pe ecrane touch).

### De ce `RadioGroup` și nu 5 `RadioButton` independenți

`RadioGroup` **grupează** butoanele: când selectezi unul, celelalte se deselectează automat. Fără grup, ai putea selecta toate 5.

### `android:checked="true"` pe `rbGeneral`

Primul buton e selectat implicit. Astfel, `rgApproval` are **mereu** o valoare — nu poți salva un film fără ghidaj.

### De ce `MaterialRadioButton` și nu `RadioButton`

`MaterialRadioButton` are stilul Material 3 (animat, cu ripple). `RadioButton` ar arăta ca Android 4.

### Exercițiu 6.5

**Cerință:** adaugă un al 6-lea buton, „Unrated”, cu id `rbUnrated`, text „NR”. Ce trebuie să faci în cod ca să funcționeze?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat în `RadioGroup`:

```xml
<com.google.android.material.radiobutton.MaterialRadioButton
    android:id="@+id/rbUnrated"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="NR" />
```

**Ce trebuie făcut în cod:** **nimic.** `saveMovie()` și `fillForm()` iterează peste `rgApproval.getChildCount()` și citesc `rb.getText()`. Al 6-lea buton e automat inclus.

```java
for(int index=0; index<rgApproval.getChildCount(); index++) {
    RadioButton rb = (RadioButton) rgApproval.getChildAt(index);
    if(rb.isChecked()) {
        movie.setApproval(rb.getText().toString());
        break;
    }
}
```

**De ce merge:** codul e scris **generic**, peste copiii grupului, nu peste ID-uri individuale. E o dovadă de design bun: adaugi un buton în XML, codul îl vede.

**De reținut:**
1. `rgApproval.getChildCount()` = numărul de copii direcți.
2. `rgApproval.getChildAt(i)` = copilul de la poziția i.
3. `RadioButton` (clasa părinte) e suficient pentru `getText()` și `isChecked()`; nu ai nevoie de `MaterialRadioButton` în cod.
4. Dacă ai fi scris `if (rbGeneral.isChecked()) ... else if (rbPG13.isChecked()) ...`, ar fi trebuit să adaugi un `else if` pentru fiecare buton nou.

**Unde revine:** în cap. 07, `fillForm` face același lucru invers: caută butonul al cărui text e egal cu `existing.getApproval()` și îl selectează. Adaugi „NR”, merge și acolo, fără modificări.

</details>

---

## Pasul 6.6 — Card 4: Poster URL

### De ce

Posterul e un URL. Câmpul e un `TextInputEditText` cu `inputType="textUri"` și iconiță de galerie.

### Cum

```xml
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
```

### De ce `layout_marginBottom="24dp"` (nu 16dp)

E ultimul card înainte de buton. 24dp = spațiu mai mare între „conținut” și „acțiune finală”.

### `inputType="textUri"`

Tastatură cu `/`, `.com`, `.ro`. Nu restricționează caracterele — poți tasta orice, dar tastatura e optimizată.

### Exercițiu 6.6

**Cerință:** ce se întâmplă dacă lași câmpul Poster gol și apeși Save? Urmează lanțul până la afișare.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am urmărit fluxul unui poster gol.

**Lanțul:**
1. `saveMovie()`: `movie.setPoster(etPoster.getText().toString())` → `""` (string gol, nu `null`).
2. `Intent.putExtra(MOVIE_EXTRA, movie)` → filmul e serializat cu `poster=""`.
3. `MainActivity.onActivityResult`: `movies.add(movie)` → lista are un film cu poster gol.
4. `movieAdapter.notifyDataSetChanged()` → `ListView` redesenează.
5. `ArrayAdapter.getView()` → cheamă `movie.toString()` → afișează `poster=''`.

**Ce se vede:** în listă, rândul arată `... poster=''}`. Nu se întâmplă nimic rău — pentru că `ListView` nu încarcă imagini.

**De ce e relevant:** în cap. 11, `MovieAdapter` va încerca să încarce posterul într-un `ImageView`. Un URL gol sau invalid va da o imagine goală (sau o eroare de rețea, dacă folosești o bibliotecă de loading). Deci validarea posterului devine importantă **abia atunci**.

**De reținut:**
1. `getText().toString()` întoarce `""` pentru câmp gol, **nu** `null`.
2. `""` și `null` sunt diferite: `"".isEmpty()` e `true`, `null.isEmpty()` aruncă NPE.
3. Modelul are `poster = null` ca valoare implicită, dar UI-ul produce `""`. Inconsecvență minoră.

**Unde revine:** în cap. 11, `MovieAdapter` nu încarcă imagini (nu are bibliotecă de loading) — deci posterul rămâne doar text. Dacă vrei să încarci imagini, ai nevoie de Glide/Coil, care e o extensie.

</details>

---

## Pasul 6.7 — Butonul Save

### De ce

Un `MaterialButton` lat cât ecranul, înalt de 60dp, cu colțuri de 30dp (pill shape), cu iconiță de salvare.

### Cum

```xml
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
```

### Atributele

| Atribut | Sens |
|---|---|
| `style="@style/Widget.Material3.Button"` | stil Material 3: fundal `colorPrimary`, text `colorOnPrimary` |
| `layout_height="60dp"` | înălțime generoasă (implicit e 40dp) |
| `app:cornerRadius="30dp"` | colțuri complet rotunjite (60/2 = 30 → pill) |
| `app:icon="@android:drawable/ic_menu_save"` | iconiță de salvare din sistem |
| `app:iconGravity="textStart"` | iconița înaintea textului |

### De ce 30dp la colțuri

Ca să fie **pill**: `cornerRadius = height / 2`. Dacă ar fi 60, ar fi prea mult (Android îl limitează la height/2 oricum). Dacă ar fi 8, ar fi un buton normal cu colțuri mici.

### De ce `Widget.Material3.Button` și nu `Widget.Material3.Button.Filled`

`Widget.Material3.Button` **este** varianta filled (implicită). Variantele sunt:
- `Widget.Material3.Button` = filled
- `Widget.Material3.Button.TonalButton` = tonal (fundal secundar)
- `Widget.Material3.Button.OutlinedButton` = contur
- `Widget.Material3.Button.TextButton` = doar text

### Exercițiu 6.7

**Cerință:** schimbă stilul la `Widget.Material3.Button.OutlinedButton`. Rulează. Ce diferență vezi? Care e mai potrivită pentru „Save”?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat stilul butonului.

**Ce se vede:**
- **Filled** (original): fundal plin în `colorPrimary` (albastru), text alb. Butonul e **principal**.
- **Outlined**: fundal transparent, contur de 1dp, text în `colorPrimary`. Butonul e **secundar**.

**Care e mai potrivită:** **Filled**, pentru că „Save” e acțiunea principală a ecranului. Outlined ar fi potrivit pentru „Cancel”, dacă ar exista.

**De reținut:**
1. Ierarhia Material: **filled** = acțiune principală, **tonal** = secundară, **outlined** = alternativă, **text** = terțiară.
2. Un ecran ar trebui să aibă **un singur** buton filled (acțiunea principală).
3. `cornerRadius` funcționează pe toate stilurile.

**Unde revine:** nu revine, dar e relevant pentru test: dacă ți se cere „cum faci un buton secundar”, răspunsul e `.OutlinedButton` sau `.TextButton`.

</details>

---

## Pasul 6.8 — Separatoarele `<View>`

### De ce

Între Rating și rândul switch/checkbox, și între acel rând și RadioGroup, sunt linii subțiri de separare.

### Cum

```xml
<View
    android:layout_width="match_parent"
    android:layout_height="1dp"
    android:layout_marginVertical="12dp"
    android:background="?attr/colorOutlineVariant" />
```

### De ce `<View>`

`View` e clasa de bază pentru orice element vizual. Un `View` gol, cu înălțime 1dp și fundal, e o **linie**.

### `layout_marginVertical="12dp"`

Spațiu sus și jos (echivalent cu `marginTop` + `marginBottom`).

### De ce `colorOutlineVariant` și nu `colorOutline`

`colorOutlineVariant` e mai **slabă** decât `colorOutline`. Separatoarele trebuie să fie subtile, nu să concureze cu contururile câmpurilor.

### Exercițiu 6.8

**Cerință:** înlocuiește un separator cu un `TextView` care conține „—” repetat. Merită? De ce nu?

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit `<View .../>` cu un `TextView` cu text de liniuțe.

**Ce se vede:** o linie punctată, nu continuă. Și ocupă mai mult spațiu vertical (înălțimea textului, nu 1dp).

**De ce nu merită:**
1. **Performanță**: un `TextView` e mai scump decât un `View` gol (măsurare text, layout text, desenare text).
2. **Aspect**: liniuțele nu se întind uniform; depinde de font.
3. **Accesibilitate**: TalkBack ar citi „liniuță liniuță liniuță”.
4. **Semantică**: un separator nu e text.

**De reținut:** `<View>` e cel mai ieftin mod de a desena o formă simplă. Pentru linii, dreptunghiuri, cercuri mici — `View` cu `background`.

**Unde revine:** în `movie_item.xml` (cap. 11), nu sunt separatoare — cardul are deja umbră și margini. Separatoarele sunt specifice formularelor lungi.

</details>

---

## Pasul 6.9 — Verificare vizuală completă

### Cum

1. Rulează. Deschide `activity_item.xml` în **Design**.
2. Derulează. Verifică:
   - Card 1: Title, Genre, Release.
   - Card 2: Budget (cu „$ ” în față), Duration (bară + valoare), etichete 0/300 min.
   - Card 3: Rating (5 stele), separator, Recommended + switch + Watchlist checkbox, separator, Guidance cu 5 radio butoane.
   - Card 4: Poster URL.
   - Buton „Save Movie” pill, cu iconiță.

### Checklist final

- [ ] toate cele 4 `MaterialCardView` cu `materialCardViewFilledStyle`
- [ ] toate cele 13 ID-uri: `tvTile`, `etTitle`, `tvGenre`, `spGenre`, `etRelease`, `tvBudget`, `etBudget`, `tvDuration`, `tvDurationValue`, `sbDuration`, `tvRating`, `rbRating`, `tvWatched`, `tvWatchedValue`, `swWatched`, `cbOnWatchList`, `tvGuidance`, `rgApproval`, `etPoster`, `btnMovieAction`
- [ ] `ScrollView` cu `android:id="@+id/main"`
- [ ] niciun `TextView` fără `layout_width`/`layout_height`
- [ ] toate etichetele închise corect

> **Numără ID-urile:** sunt 20, dar doar 13 sunt folosite în cod. Cele nefolosite: `tvTile`, `tvGenre`, `tvBudget`, `tvDuration`, `tvRating`, `tvWatched`, `tvGuidance`, plus cele 5 radio butoane. Sunt pentru **accesibilitate** și pentru viitoare funcționalități.

---

## Pasul 6.10 — Exercițiu de sinteză: citește fișierul

**Cerință:** deschide `cod-final/res/layout/activity_item.xml` și parcurge-l de sus în jos. Pentru fiecare bloc, spune în minte: *ce widget e, ce ID are, ce rol are*.

### Harta fișierului

```
ScrollView (id=main)
└── LinearLayout vertical
    ├── TextView "Movie details"
    ├── TextView "Fill in the information below..."
    ├── MaterialCardView [Basics]
    │   └── LinearLayout
    │       ├── TextView "Basics"
    │       ├── TextView tvTile + TextInputLayout + etTitle
    │       ├── TextView tvGenre + MaterialCardView + Spinner spGenre
    │       └── TextInputLayout + etRelease
    ├── MaterialCardView [Production]
    │   └── LinearLayout
    │       ├── TextView "Production"
    │       ├── TextView tvBudget + TextInputLayout + etBudget
    │       ├── LinearLayout (tvDuration + tvDurationValue)
    │       ├── SeekBar sbDuration
    │       └── LinearLayout (0 min / 300 min)
    ├── MaterialCardView [Your verdict]
    │   └── LinearLayout
    │       ├── TextView "Your verdict"
    │       ├── TextView tvRating + RatingBar rbRating
    │       ├── View (separator)
    │       ├── LinearLayout (tvWatched + tvWatchedValue | swWatched | cbOnWatchList)
    │       ├── View (separator)
    │       ├── TextView tvGuidance
    │       └── HorizontalScrollView + RadioGroup rgApproval (5 butoane)
    ├── MaterialCardView [Poster]
    │   └── LinearLayout
    │       ├── TextView "Poster"
    │       └── TextInputLayout + etPoster
    └── MaterialButton btnMovieAction
```

---

## Pasul 6.11 — Întrebări de test

1. De ce `SeekBar` are `android:min="0"` explicit, deși 0 e implicit?
2. Ce face `app:prefixText` și de ce nu apare în `getText()`?
3. De ce `RadioGroup` și nu 5 `RadioButton` independenți?
4. Ce diferență e între `MaterialSwitch` și `MaterialCheckBox`, funcțional?
5. De ce `layout_marginBottom="24dp"` la ultimul card, dar `16dp` la celelalte?

<details>
<summary>Răspunsuri — explicativ</summary>

**1. De ce `android:min="0"` explicit?**
E **documentație**: arată cititorului că intervalul e [0, 300]. Tehnic e redundant (0 e implicit), dar face intenția clară. Și e necesar dacă vrei să schimbi minimul mai târziu — vezi imediat unde e.

**2. Ce face `app:prefixText`?**
Afișează un text fix înaintea valorii tastate, **în interiorul** câmpului. `getText()` întoarce doar ce a tastat utilizatorul, fără prefix. E pur vizual.

**3. De ce `RadioGroup`?**
Pentru că garantează **exclusivitate**: selectarea unui buton îl deselectează pe celălalt. Fără grup, ai putea selecta toate 5 simultan. Și îți dă `getChildCount()` / `getChildAt()` pentru iterare generică.

**4. `MaterialSwitch` vs `MaterialCheckBox`?**
Funcțional: **identice**. Ambele extind `CompoundButton`, ambele au `isChecked()`, `setChecked()`, `setOnCheckedChangeListener()`. Diferă doar **aspectul** (glisant vs pătrat) și **semantica** (stare vs selecție).

**5. De ce 24dp la ultimul card?**
Spațiu mai mare între „conținut” și „acțiune finală”. E o regulă de design: acțiunea principală trebuie să fie vizibil separată de formular.

</details>

---

## Pasul 6.12 — Compară cu originalul

```bash
diff "cod-final/res/layout/activity_item.xml" \
     "_progres/Movies1097/app/src/main/res/layout/activity_item.xml"
```

Dacă `diff` nu afișează nimic — ai fișierul identic cu `d719ffc`. Dacă afișează diferențe, verifică dacă sunt:
- **intenționate** (ai schimbat ceva la exerciții) → OK
- **accidentale** (ai uitat un atribut) → corectează

---

## Rezumat capitol 06

- `prefixText` = text vizual, nu parte din valoare.
- `SeekBar` cu `min`/`max` + etichete hardcodate = datorie tehnică.
- `RatingBar` cu `stepSize` controlează granularitatea.
- `MaterialSwitch` și `MaterialCheckBox` sunt identice funcțional, diferă vizual.
- `RadioGroup` garantează exclusivitate; iterația peste copii face codul generic.
- `MaterialButton` filled = acțiune principală, `cornerRadius = height/2` = pill.

**Următorul capitol:** [07 - ItemActivity - citire si scriere.md](07%20-%20ItemActivity%20-%20citire%20si%20scriere.md)
