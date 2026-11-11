# Capitolul 18 — Bancul de cerințe 2: bindinguri, view-uri, adaptoare

**Obiectiv:** să poți rezolva, în 30 de minute și fără să te uiți la nimic, orice combinație de două cerințe din cele trei care se dau la test: **leagă o valoare de un widget**, **schimbă un widget cu altul**, **fă un adapter**. Toate exemplele sunt pe aplicația `G1097` la commitul `d719ffc` — exact codul din `cod-final/`, nu o variantă aproximativă.

**Cele trei lucruri care se cer la examen:**

| Ce ți se cere | Ce atingi |
|---|---|
| „leagă valoarea X de widget-ul Y" | `findViewById` + setterul potrivit (`setText`, `setProgress`, `setRating`, `setChecked`, `setSelection`) |
| „schimbă un `TextView` într-un `EditText`" | XML (widgetul nou) + `findViewById` (tipul câmpului) + citirea valorii în `saveMovie` |
| „fă un adapter" | `RecyclerView.Adapter` + `ViewHolder` + `onBindViewHolder` (+ `LayoutManager` în activitate) |

**Convenția de căi:** toate căile din capitol sunt relative la `src/main/` din modulul `app`. Deci `res/layout/movie_item.xml` înseamnă `app/src/main/res/layout/movie_item.xml`, iar `java/ro/ase/ie/g1097/model/Movie.java` înseamnă `app/src/main/java/ro/ase/ie/g1097/model/Movie.java`.

**Regula celor 30 de minute:** un binding = 5–10 minute, un schimb de widget = 10–15, un adapter = 20. Dacă ți se dau două cerințe, începe cu cea care nu poate strica build-ul. Un adapter scris pe jumătate nu compilează deloc; un binding scris pe jumătate compilează și doar nu face nimic.

**Un detaliu care economisește timp:** cele trei cerințe nu sunt independente. „Schimbă un widget" e tot un binding, doar că are cinci puncte de atins în loc de două. Iar „fă un adapter" conține binding-ul rândului — `bind()` din `ViewHolder` e exact „leagă valoarea X de widget-ul Y", repetat pentru fiecare câmp.

---

## Exercițiul 18.1 — `tvDurationValue` legat de `SeekBar`

**Cerință:** `tvDurationValue` (TextView, cardul „Production" din `activity_item.xml`) trebuie să arate mereu valoarea `SeekBar`-ului `sbDuration`, în forma `"148 min."`. Leagă-le. Apoi explică de ce, la deschiderea formularului în modul de editare, eticheta se actualizează **fără** ca `fillForm` să o atingă.

> Codul din `d719ffc` conține deja legătura (`ItemActivity.java`, `initListeners`). Exercițiul e să o rescrii din memorie și să explici mecanismul — pentru că exact mecanismul se întreabă la test.

**Fișiere atinse:** `java/ro/ase/ie/g1097/activities/ItemActivity.java` (câmpul, `initControls`, `initListeners`). XML-ul are deja ambele view-uri.

**Cum abordezi — pașii tăi:**
1. Deschide `ItemActivity.java` și găsește `initControls()`. Acolo e deja linia `tvDurationValue = findViewById(R.id.tvDurationValue);` — câmpul există, dar nimeni nu îl actualizează.
2. Găsește `initListeners()`. Adaugă `sbDuration.setOnSeekBarChangeListener(...)`. Scrie întâi doar `onProgressChanged`, cu `tvDurationValue.setText(progress + " min.")`. Celelalte două metode rămân goale — interfața le cere, chiar dacă nu fac nimic.
3. Deschide `fillForm(...)` și caută `tvDurationValue`. Nu apare. Rulează aplicația, deschide un film existent și uită-te la eticheta Duration: arată 148, deși `fillForm` nu a scris nimic acolo.
4. Explică de ce: `sbDuration.setProgress(148)` din `fillForm` a declanșat `onProgressChanged`. Verifică apoi ordinea din `onCreate`: `initControls(); initListeners();` rulează **înainte** de `fillForm(existing)`.

**Indiciu 1 — dacă te blochezi la pasul 1:** `SeekBar` nu are `setOnProgressChangedListener`. Metoda se numește `setOnSeekBarChangeListener` și primește un `SeekBar.OnSeekBarChangeListener` cu trei metode: `onProgressChanged`, `onStartTrackingTouch`, `onStopTrackingTouch`. Doar prima te interesează.

**Indiciu 2 — dacă te blochezi la pasul 3:** dacă eticheta rămâne „0 min" când editezi un film, listener-ul nu era înregistrat la momentul `setProgress`. Verifică ordinea din `onCreate`: `initListeners()` trebuie să ruleze înainte de `fillForm(existing)`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am legat `tvDurationValue` de `sbDuration` printr-un listener, nu printr-un apel manual. Eticheta nu se actualizează „la salvare" sau „la deschidere" — se actualizează la fiecare schimbare de progres, indiferent cine o produce.

**Cod:**

```java
// ItemActivity.java — câmpul există deja
private TextView tvDurationValue;

// initControls() — există deja
tvDurationValue = findViewById(R.id.tvDurationValue);

// initListeners() — legătura
sbDuration.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvDurationValue.setText(progress + " min.");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {

    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {

    }
});
```

**De ce:** `onProgressChanged` nu înseamnă „utilizatorul a mișcat degetul". Înseamnă „valoarea progresului s-a schimbat". `SeekBar` anunță listener-ul în două situații:

```
fillForm()                          ItemActivity.onCreate()
  sbDuration.setProgress(148)
        │
        ▼
  ProgressBar.setProgressInternal(148, fromUser = false, animate = false)
        │  (dacă valoarea diferă de cea curentă)
        ▼
  refreshProgress(...) → onProgressRefresh(scale, fromUser = false, ...)
        │
        ▼
  SeekBar.onProgressRefresh(...) → mOnSeekBarChangeListener.onProgressChanged(seekBar, 148, false)
        │
        ▼
  tvDurationValue.setText("148 min.")
```

Al treilea parametru, `fromUser`, e singurul mod de a distinge drag-ul de cod: `true` = degetul utilizatorului, `false` = `setProgress` din cod.

Consecințe directe, toate verificabile în codul din `d719ffc`:

1. `fillForm` **nu** are nevoie de `tvDurationValue.setText(...)`. Dacă ai adăuga-o, ar fi cod mort — listener-ul o face deja.
2. Ordinea din `onCreate` contează. `initControls(); initListeners();` rulează înainte de `fillForm(existing)` (care e apelat după `getIntent()`). Dacă ai muta `initListeners()` după `fillForm`, listener-ul nu ar fi înregistrat la momentul `setProgress` și eticheta ar rămâne „0 min" din XML.
3. Dacă în `onProgressChanged` ai avea un efect secundar — salvare în bază, `Toast`, cerere de rețea — s-ar declanșa și la `fillForm`, fără ca utilizatorul să atingă nimic. Soluția e `if (fromUser) { ... }`.
4. Dacă valoarea e identică cu cea curentă, `setProgress` nu anunță nimic (`ProgressBar` iese devreme din `setProgressInternal`). Deci pentru un film cu durata 0 — valoarea implicită a unui `int` — `fillForm` nu declanșează nimic, iar eticheta rămâne „0 min" din XML. Nimerește corect, dar din noroc, nu din design.

**De reținut:**
- `onProgressChanged(seekBar, progress, fromUser)` — `fromUser` e câmpul care contează, nu `progress`.
- `onStartTrackingTouch` / `onStopTrackingTouch` se declanșează **doar** la atingere reală. Dacă ai nevoie de „a terminat de tras", folosești `onStopTrackingTouch`.
- `progress` e `int`. Pentru un `SeekBar` cu `max="300"`, valorile sunt 0..300.
- Listener-ul se înregistrează o singură dată, în `initListeners()`. Nu în `onCreate` direct, nu în `fillForm`.

**Unde se aplică:** `swWatched` are exact aceeași problemă, cu `CompoundButton`. `fillForm` face `swWatched.setChecked(existing.isWatched())`, iar `initListeners` are `setOnCheckedChangeListener` care scrie în `tvWatchedValue`. `fillForm` **nu** atinge `tvWatchedValue` — și totuși eticheta se actualizează la editare. Același mecanism, alt widget. Dacă la test ți se cere să explici „de ce merge fără să scriu nimic", ăsta e răspunsul.

</details>

---

## Exercițiul 18.2 — `etBudget` devine `SeekBar` (0–500 milioane, pas 1 milion)

**Cerință:** înlocuiește câmpul `etBudget` (`TextInputEditText`) cu un `SeekBar` `sbBudget` care merge de la 0 la 500 de milioane, în pași de 1 milion. O etichetă `tvBudgetValue` arată valoarea curentă în forma `"$160M"`.

**Fișiere atinse:** `res/layout/activity_item.xml` (cardul „Production"), `java/ro/ase/ie/g1097/activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `activity_item.xml` și du-te la cardul „Production". Găsește `tvBudget` (eticheta „Budget") și, imediat sub ea, `TextInputLayout`-ul care conține `etBudget` — cel cu `app:prefixText="$ "` și `android:inputType="numberDecimal"`.
2. Șterge tot `TextInputLayout`-ul, cu tot cu `TextInputEditText`-ul din el. În locul lui pune un `LinearLayout` orizontal cu `tvBudgetValue` (weight 1, aliniat stânga) și un text mic „max $500M" (dreapta), apoi un `SeekBar` cu `id=sbBudget`, `max=500`, `min=0`.
3. Deschide `ItemActivity.java`. Schimbă tipul câmpului: `private EditText etBudget;` devine `private SeekBar sbBudget;`. Adaugă `private TextView tvBudgetValue;`.
4. Atinge toate locurile în care apare `etBudget`: `initControls()` (`findViewById`), `fillForm()` (setProgress), `saveMovie()` (getProgress × 1.000.000). În `initListeners()` adaugi listener-ul care scrie „$160M".
5. Rulează: deschide Inception → slider-ul stă la 160, eticheta arată „$160M". Mișcă slider-ul → eticheta se schimbă din 1 în 1 milion. Salvează → în listă bugetul e cel nou.

**Indiciu 1 — dacă te blochezi la pasul 2:** `SeekBar` nu are „pas". Are `max`. Pașii îi faci tu, prin interpretarea valorii: progres 0..500 înmulțit cu `1_000_000`. Nu există `android:stepSize` pe `SeekBar` (există pe `Slider`-ul Material, alt widget).

**Indiciu 2 — dacă te blochezi la pasul 4:** dacă build-ul zice „cannot find symbol: variable etBudget", ai uitat unul din cele patru locuri (câmpul plus cele trei utilizări). Caută `etBudget` în fișier cu Ctrl+F — trebuie să găsești zero rezultate înainte să rulezi.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am scos `TextInputLayout`-ul cu totul (nu doar `EditText`-ul din el) și am pus în loc un slider plus o etichetă de valoare. Apoi am mutat conversia în două locuri: la citire (`fillForm`) și la scriere (`saveMovie`).

**Cod:**

`res/layout/activity_item.xml` — înlocuiește blocul `TextInputLayout` care conține `etBudget`:

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center_vertical"
    android:orientation="horizontal">

    <TextView
        android:id="@+id/tvBudgetValue"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:text="$0M"
        android:textAppearance="?attr/textAppearanceLabelLarge"
        android:textColor="?attr/colorPrimary" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="max $500M"
        android:textAppearance="?attr/textAppearanceLabelSmall"
        android:textColor="?attr/colorOnSurfaceVariant" />
</LinearLayout>

<SeekBar
    android:id="@+id/sbBudget"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="8dp"
    android:layout_marginBottom="16dp"
    android:max="500"
    android:min="0"
    android:progressTint="?attr/colorPrimary"
    android:thumbTint="?attr/colorPrimary" />
```

Eticheta `tvBudget` („Budget") rămâne neatinsă deasupra — o folosești în continuare.

`ItemActivity.java` — cinci modificări:

```java
// 1. câmpurile
private SeekBar sbBudget;        // înlocuiește: private EditText etBudget;
private TextView tvBudgetValue;  // nou

// 2. initControls()
sbBudget = findViewById(R.id.sbBudget);   // înlocuiește: etBudget = findViewById(R.id.etBudget);
tvBudgetValue = findViewById(R.id.tvBudgetValue);

// 3. initListeners() — adaugă
sbBudget.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        tvBudgetValue.setText("$" + progress + "M");
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {

    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {

    }
});

// 4. fillForm() — înlocuiește etBudget.setText(String.valueOf(existing.getBudget()));
sbBudget.setProgress((int) Math.round(existing.getBudget() / 1_000_000));

// 5. saveMovie() — înlocuiește Double.parseDouble(etBudget.getText().toString())
movie.setBudget(sbBudget.getProgress() * 1_000_000.0);
```

**De ce:**
- `SeekBar` nu are pași: are un interval întreg 0..500. „Pas de 1 milion" e o convenție a ta, nu o setare a widget-ului. `max="500"` + `× 1_000_000` = 0..500.000.000.
- `Math.round` la citire inversă: `160_000_000 / 1_000_000 = 160.0` → 160. Dacă bugetul ar fi 160.400.000, rotunjirea îl aduce la 160 — pierzi precizie, dar pasul e 1M prin definiție.
- `fillForm` nu atinge `tvBudgetValue`: listener-ul o face, pentru că `setProgress` declanșează `onProgressChanged` (exercițiul 18.1).
- `saveMovie` nu mai poate arunca `NumberFormatException`. În codul actual, `Double.parseDouble("")` crăpa dacă apăsai Save cu bugetul gol. Cu `SeekBar`, valoarea e mereu un `int` valid.
- `TextInputLayout` se scoate întreg, nu doar copilul. E construit pentru un singur copil de tip `EditText` și îi aplică hint, counter, error, prefix — un `SeekBar` înăuntru nu are comportamentul așteptat.

**De reținut:**
- `android:min` pe `SeekBar` există din API 26. `minSdk`-ul proiectului e 33, deci merge. Pe API mai vechi `min` e ignorat și rămâne 0.
- `max` e **progresul maxim**, nu valoarea. 500 înseamnă 500 de milioane doar pentru că tu înmulțești.
- Dacă cerința ar zice „pași de 5 milioane", ai `max="100"` și `× 5_000_000`. Aceeași structură, alt număr.
- `progressTint` / `thumbTint` sunt opționale; le pui doar ca slider-ul să arate ca restul temei.

**Unde se aplică:** orice „schimbă X în Y" la examen are aceleași cinci puncte de atins: câmpul, `initControls`, `initListeners` (dacă widgetul nou are listener), `fillForm` (citirea din model), `saveMovie` (scrierea în model). Dacă sari unul, fie nu compilează, fie compilează și se comportă greșit — și a doua variantă e mai rea, pentru că nu te prinde nimeni până la rulare.

</details>

---

## Exercițiul 18.3 — `rbRating` (`RatingBar`) devine `Spinner` cu 1–5 stele

**Cerință:** înlocuiește `RatingBar`-ul `rbRating` (5 stele, pas 0.5) cu un `Spinner` `spRating` cu cinci valori: „1 star" … „5 stars". Valoarea se salvează în `Movie.rating` ca `float`.

**Fișiere atinse:** `res/values/strings.xml` (array nou), `res/layout/activity_item.xml` (cardul „Your verdict"), `java/ro/ase/ie/g1097/activities/ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `res/values/strings.xml` și adaugă un `<string-array name="movie_rating">` cu 5 elemente, lângă `movie_genre`, în același `<resources>`. Fără el, `android:entries` nu compilează.
2. Deschide `activity_item.xml`, cardul „Your verdict". Șterge `RatingBar`-ul `rbRating` (cel cu `numStars="5"`, `stepSize="0.5"`) și pune un `Spinner` cu `id=spRating` și `android:entries="@array/movie_rating"`.
3. Deschide `ItemActivity.java` și atinge cele patru locuri: câmpul (`RatingBar rbRating` → `Spinner spRating`), `initControls()`, `fillForm()` și `saveMovie()`.
4. Scrie conversia în ambele sensuri: la citire `setSelection((int) rating - 1)`, cu limitare în 0..4; la scriere `setRating(position + 1)`.
5. Rulează: editează un film cu rating 4.5 → spinner-ul arată „4 stars" (jumătatea se pierde). Salvează → în listă rating-ul e 4.

**Indiciu 1 — dacă te blochezi la pasul 4:** `Spinner` întoarce o **poziție** (0..4), nu o valoare (1..5). `getSelectedItemPosition()` e indexul, `getSelectedItem()` e textul („3 stars"). Pentru rating vrei indexul.

**Indiciu 2 — dacă tot nu merge la pasul 4:** dacă ratingul e 0 (film nou, câmp `float` neselectat), `(int) 0 - 1 = -1` — index invalid. Limitează: `Math.max(0, Math.min(4, ...))`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am înlocuit un widget cu valoare continuă (0.0–5.0, pas 0.5) cu unul cu valori discrete (5 poziții). Diferența nu e doar vizuală: trebuie o conversie explicită în ambele sensuri, iar precizia se pierde.

**Cod:**

`res/values/strings.xml` — adaugă lângă `movie_genre`:

```xml
<string-array name="movie_rating">
    <item>1 star</item>
    <item>2 stars</item>
    <item>3 stars</item>
    <item>4 stars</item>
    <item>5 stars</item>
</string-array>
```

`res/layout/activity_item.xml` — înlocuiește blocul `<RatingBar ... />`:

```xml
<Spinner
    android:id="@+id/spRating"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:entries="@array/movie_rating"
    android:spinnerMode="dropdown" />
```

`ItemActivity.java`:

```java
// 1. câmpul
private Spinner spRating;   // înlocuiește: private RatingBar rbRating;

// 2. initControls()
spRating = findViewById(R.id.spRating);

// 3. fillForm() — înlocuiește rbRating.setRating(existing.getRating());
int stars = Math.max(0, Math.min(4, (int) existing.getRating() - 1));
spRating.setSelection(stars);

// 4. saveMovie() — înlocuiește movie.setRating(rbRating.getRating());
movie.setRating(spRating.getSelectedItemPosition() + 1);
```

**De ce:**
- `setRating(float)` → `setSelection(int)`: `RatingBar` are valoare continuă, `Spinner` are index. `-1` la citire și `+1` la scriere sunt conversia.
- `Math.max(0, Math.min(4, ...))`: un film nou are `rating = 0f` (valoarea implicită a unui `float`), deci `(int) 0 - 1 = -1`. Un index negativ nu are sens pentru `Spinner`. Limitarea îl aduce la 0, adică „1 star".
- `setRating(spRating.getSelectedItemPosition() + 1)`: `int` se lărgește automat la `float`, deci se potrivește cu semnătura `setRating(float)`.
- `android:entries` leagă array-ul direct din XML, fără `ArrayAdapter` în cod — exact tiparul deja folosit de `spGenre` cu `@array/movie_genre`.

**De reținut:**
- Pierzi jumătățile de stea. `stepSize="0.5"` permitea 4.5; `Spinner`-ul are doar 1..5. Dacă cerința zice „1–5 stele", e acceptabil; dacă zice „păstrează 0.5", trebuie alt widget — `Slider` Material cu `android:stepSize="0.5"`.
- `RatingBar` avea `progressTint="#FFC107"`. Un `Spinner` nu are așa ceva. Nu încerca să reproduci stilul; cerința e funcțională.
- `RatingBar.setRating()` declanșează și el `onRatingChanged(..., fromUser = false)` dacă ai un listener — același mecanism ca la 18.1. Aici nu ai listener, deci nu se vede.
- Varianta fără array în XML: `ArrayAdapter.createFromResource(this, R.array.movie_rating, android.R.layout.simple_spinner_item)` plus `setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)`. Mai lungă, dar necesară când lista se construiește în cod.

**Unde se aplică:** `spGenre` e exact același tipar — uită-te la el ca model. Și tot acolo vezi diferența: în `saveMovie`, `spGenre.getSelectedItem().toString()` ia **textul** („Sci-Fi"), nu indexul. Pentru rating vrei indexul, pentru gen vrei textul. Alege în funcție de ce tip are câmpul din model.

</details>

---

## Exercițiul 18.4 — a doua linie în rândul de `ListView` (`BaseAdapter` propriu)

**Cerință:** rândul din `ListView` trebuie să aibă **două linii**: titlul filmului și, sub el, genul cu anul. Pornind de la `android.R.layout.simple_list_item_1`, adaugă a doua linie.

**Fișiere atinse:** `res/layout/movie_row.xml` (nou), `java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` (nou), `java/ro/ase/ie/g1097/activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. Încearcă întâi ce e imposibil: caută `simple_list_item_1` în proiect (Ctrl+Shift+F). Nu există — e în SDK, nu în proiectul tău. Notează asta: nu ai ce fișier să editezi.
2. Creează `res/layout/movie_row.xml` cu un `LinearLayout` vertical și două `TextView`-uri: `rowTitle` și `rowSubtitle`.
3. Creează pachetul `ro.ase.ie.g1097.adapters` și clasa `MovieListAdapter extends BaseAdapter`. Scrie întâi scheletul: `getCount`, `getItem`, `getItemId`, `getView` (goală).
4. Umple `getView`: `if (convertView == null) { inflate; findViewById; setTag } else { getTag }`, apoi `setText` pe cele două view-uri.
5. În `MainActivity`: schimbă tipul câmpului și linia din `onCreate`. Rulează: două linii per rând, click-ul merge neschimbat.

**Indiciu 1 — dacă te blochezi la pasul 1:** `android.R.layout.simple_list_item_2` **există** și are două `TextView`-uri (`android.R.id.text1`, `android.R.id.text2`). Dar `ArrayAdapter` umple doar `text1`; `text2` rămâne gol. Deci tot la adapter propriu ajungi.

**Indiciu 2 — dacă te blochezi la pasul 4:** dacă rândurile se repetă greșit la scroll (primul film apare de trei ori), ai uitat `convertView.setTag(holder)` sau ai pus `findViewById` în afara blocului `if (convertView == null)`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am renunțat la `simple_list_item_1` și am scris un rând propriu plus un `BaseAdapter` care îl umple.

Partea care trebuie spusă la examen: `android.R.layout.simple_list_item_1` e un fișier din `platforms/android-XX/data/res/layout/`, împachetat în SDK. Nu e în proiectul tău, deci nu poate fi editat. Nu poți „adăuga o linie" într-un layout pe care nu îl deții.

**Cod:**

`res/layout/movie_row.xml` (nou):

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:paddingHorizontal="16dp"
    android:paddingVertical="12dp">

    <TextView
        android:id="@+id/rowTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ellipsize="end"
        android:maxLines="1"
        android:textSize="18sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/rowSubtitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="2dp"
        android:textColor="#757575"
        android:textSize="14sp" />
</LinearLayout>
```

`java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` (nou — creează pachetul `adapters`):

```java
package ro.ase.ie.g1097.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieListAdapter extends BaseAdapter {

    private static class ViewHolder {
        TextView rowTitle;
        TextView rowSubtitle;
    }

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;
    private final LayoutInflater inflater;

    public MovieListAdapter(Context context, List<Movie> movies) {
        this.inflater = LayoutInflater.from(context);
        this.movies = movies;
    }

    @Override
    public int getCount() {
        return movies.size();
    }

    @Override
    public Movie getItem(int position) {
        return movies.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = inflater.inflate(R.layout.movie_row, parent, false);
            holder = new ViewHolder();
            holder.rowTitle = convertView.findViewById(R.id.rowTitle);
            holder.rowSubtitle = convertView.findViewById(R.id.rowSubtitle);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        Movie movie = getItem(position);
        holder.rowTitle.setText(movie.getTitle());

        String year = movie.getRelease() != null
                ? YEAR_FORMAT.format(movie.getRelease())
                : "";
        holder.rowSubtitle.setText(movie.getGenre() + " · " + year);

        return convertView;
    }
}
```

`MainActivity.java` — trei modificări:

```java
// 1. import nou
import ro.ase.ie.g1097.adapters.MovieListAdapter;

// 2. câmpul — schimbă tipul
private MovieListAdapter movieAdapter;   // era: private ArrayAdapter<Movie> movieAdapter;

// 3. onCreate — schimbă construcția
movieAdapter = new MovieListAdapter(this, movies);
// era: movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);
```

Nimic altceva. `listView.setAdapter(movieAdapter)` și `movieAdapter.notifyDataSetChanged()` rămân neschimbate — `BaseAdapter` are `notifyDataSetChanged()`.

**De ce:**
- `getCount()` → câte rânduri sunt.
- `getItem(position)` → obiectul de pe poziția respectivă; `getItemId` → id-ul (poziția e suficientă aici).
- `getView` → prima jumătate creează rândul (o singură dată), a doua îl umple (la fiecare afișare).
- `convertView == null` = rând nou; altfel e un rând reciclat, adus de `ListView` din afara ecranului. De aceea `setTag`/`getTag`: `findViewById` se face o dată per rând creat, nu la fiecare scroll.

**De reținut:**
- `android:entries="@array/items"` din `activity_main.xml` e ignorat când apelezi `setAdapter`. Șterge-l — altfel, dacă uiți `setAdapter`, vezi „Item 1…20" și te întrebi de ce.
- `setOnItemClickListener` din `MainActivity` funcționează neschimbat cu `BaseAdapter` — `ListView` știe poziția, nu adapterul.
- `getItem` întoarce `Movie`, nu `Object`: `listView.getItemAtPosition(position)` îți dă direct un `Movie`, fără cast.
- `LayoutInflater.from(context)` se creează o dată, în constructor — nu în `getView`.
- `ViewHolder` e `private static class`, nu clasă publică: e detaliu intern al adapterului.

**Unde se aplică:** exact același schelet se folosește și pentru `RecyclerView`, dar acolo `ViewHolder` e obligatoriu și metodele sunt împărțite în două (18.5). Dacă știi 18.4, 18.5 e aceeași idee cu altă semnătură.

</details>

---

## Exercițiul 18.5 — `ListView` → `RecyclerView`, răspunsul complet de examen

**Cerință:** înlocuiește `ListView` + `ArrayAdapter` cu `RecyclerView` + `MovieAdapter`. Rândul e `movie_item.xml` (există deja în repo). Click-ul pe rând trebuie să deschidă în continuare `ItemActivity` în modul de editare.

> Ăsta e exercițiul „fă un adapter" în forma lui completă. Scrie-l ca la examen: fișiere în ordine, fiecare cu ce trebuie să conțină. Dacă îl știi pe ăsta, 18.6, 18.9 și 18.10 sunt doar diferențe față de el.

**Fișiere atinse:** `gradle/libs.versions.toml`, `build.gradle.kts` (modulul `app`), `res/layout/activity_main.xml`, `java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (nou), `java/ro/ase/ie/g1097/activities/MainActivity.java`.

**Cum abordezi — pașii tăi:**
1. Adaugă dependența: `gradle/libs.versions.toml` (o versiune + o librărie) și `build.gradle.kts` (`implementation(libs.recyclerview)`). Sync Gradle. Fără ea, pasul 3 nu compilează.
2. `activity_main.xml`: înlocuiește `<ListView android:id="@+id/listView" .../>` cu `<androidx.recyclerview.widget.RecyclerView android:id="@+id/recyclerView" .../>`. Șterge `android:entries`.
3. Creează `MovieAdapter.java` în pachetul `adapters`. Scrie întâi scheletul celor trei metode abstracte (`onCreateViewHolder`, `onBindViewHolder`, `getItemCount`), apoi `ViewHolder`-ul cu `findViewById`, apoi `bind()`.
4. `MainActivity`: schimbă câmpurile (`ListView` → `RecyclerView`), construiește adapterul cu listener-ul de click, pune `setLayoutManager` + `setAdapter` în `initControls()`, șterge blocul `listView.setOnItemClickListener` din `initListeners()`.
5. Rulează: lista arată ca înainte, click-ul deschide formularul, salvarea actualizează rândul. Dacă lista e goală fără eroare, vezi Indiciul 2.

**Indiciu 1 — dacă te blochezi la pasul 1:** `RecyclerView` nu e în `appcompat` și nici în `material`. E `androidx.recyclerview:recyclerview`, o bibliotecă separată. Fără ea: „cannot find symbol class RecyclerView".

**Indiciu 2 — dacă te blochezi la pasul 5:** dacă lista e goală și nu apare nicio eroare în Logcat, ai uitat `setLayoutManager`. E singura greșeală care nu se plânge: `RecyclerView` fără `LayoutManager` nu afișează nimic.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat dependența, am schimbat widget-ul în XML, am scris un adapter cu `ViewHolder` și am mutat click-ul din `ListView` în adapter. Cinci fișiere, în ordinea de mai jos.

**Cod:** patru fișiere, în ordinea în care le scrii.

### Pas 0 — dependența

`gradle/libs.versions.toml`:

```toml
[versions]
recyclerview = "1.4.0"

[libraries]
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

`build.gradle.kts` (modulul `app`), în `dependencies { }`:

```kotlin
implementation(libs.recyclerview)
```

Dacă Android Studio îți propune o versiune mai nouă, acceptă-o — contează structura, nu numărul.

### Pas 1 — `activity_main.xml`

```xml
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/recyclerView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:listitem="@layout/movie_item" />
```

`tools:listitem` e doar pentru preview-ul din Android Studio: îi arată cum va arăta un rând. La runtime nu face nimic. `android:entries` dispare — `RecyclerView` nu are așa atribut, iar dacă îl lași e ignorat și încurcă.

### Pas 2 — `MovieAdapter.java` (fișier nou)

```java
package ro.ase.ie.g1097.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RatingBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.chip.Chip;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

import ro.ase.ie.g1097.R;
import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(int position);
    }

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;
    private final OnItemClickListener listener;

    public MovieAdapter(List<Movie> movies, OnItemClickListener listener) {
        this.movies = movies;
        this.listener = listener;
    }

    @NonNull
    @Override
    public MovieViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.movie_item, parent, false);
        return new MovieViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position), listener);
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

        private final TextView movieTitle;
        private final TextView movieSubtitle;
        private final RatingBar movieRating;
        private final TextView movieRatingValue;
        private final TextView movieFacts;
        private final Chip chipApproval;
        private final Chip chipWatched;
        private final Chip chipWatchlist;

        public MovieViewHolder(@NonNull View itemView) {
            super(itemView);
            movieTitle = itemView.findViewById(R.id.movieTitle);
            movieSubtitle = itemView.findViewById(R.id.movieSubtitle);
            movieRating = itemView.findViewById(R.id.movieRating);
            movieRatingValue = itemView.findViewById(R.id.movieRatingValue);
            movieFacts = itemView.findViewById(R.id.movieFacts);
            chipApproval = itemView.findViewById(R.id.chipApproval);
            chipWatched = itemView.findViewById(R.id.chipWatched);
            chipWatchlist = itemView.findViewById(R.id.chipWatchlist);
        }

        public void bind(Movie movie, OnItemClickListener listener) {
            if (movie == null) return;

            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);

            movieRating.setRating(movie.getRating());
            movieRatingValue.setText(String.valueOf(movie.getRating()));

            movieFacts.setText(movie.getDuration() + " min.  ·  $"
                    + (long) (movie.getBudget() / 1_000_000) + "M");

            String approval = movie.getApproval();
            if (approval != null && !approval.isEmpty()) {
                chipApproval.setText(approval);
                chipApproval.setVisibility(View.VISIBLE);
            } else {
                chipApproval.setVisibility(View.GONE);
            }
            chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
            chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);

            itemView.setOnClickListener(v -> {
                int pos = getBindingAdapterPosition();
                if (listener != null && pos != RecyclerView.NO_POSITION) {
                    listener.onItemClick(pos);
                }
            });
        }
    }
}
```

`moviePoster` rămâne nelegat — imaginea arată în continuare iconița din XML. Încărcarea reală a imaginii e altă cerință; aici doar textul (vezi 18.6 pentru URL).

### Pas 3 — `MainActivity.java`

```java
// importuri noi
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import ro.ase.ie.g1097.adapters.MovieAdapter;

// câmpuri — ListView dispare
private RecyclerView recyclerView;
private MovieAdapter movieAdapter;

// onCreate — înlocuiește linia cu ArrayAdapter
movieAdapter = new MovieAdapter(movies, new MovieAdapter.OnItemClickListener() {
    @Override
    public void onItemClick(int position) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }
});

// initControls() — înlocuiește listView = findViewById(...) și setAdapter
recyclerView = findViewById(R.id.recyclerView);
recyclerView.setLayoutManager(new LinearLayoutManager(this));
recyclerView.setAdapter(movieAdapter);

// initListeners() — ȘTERGE tot blocul listView.setOnItemClickListener
```

`notifyDataSetChanged()` din callback-ul lui `launcher` rămâne neschimbat — `RecyclerView.Adapter` are aceeași metodă.

**De ce:**
- `RecyclerView.Adapter` are **trei** metode abstracte obligatorii: `onCreateViewHolder` (creează un rând gol), `onBindViewHolder` (umple un rând existent), `getItemCount` (câte rânduri). Dacă lipsește una, clasa nu compilează.
- `ViewHolder` e **obligatoriu**, nu opțional ca la `ListView`. `RecyclerView` îl folosește ca să țină referințele și să nu mai caute cu `findViewById` la fiecare afișare.
- `ViewHolder` e `static` pentru că altfel fiecare instanță ar ține o referință la adapter. Cu ~10 rânduri vizibile ai ~10 referințe inutile.
- `onCreateViewHolder` rulează **o dată per rând creat**; `onBindViewHolder` rulează **la fiecare afișare**. Exact ca cele două jumătăți ale lui `getView` din 18.4.
- Click-ul e în `bind`, nu în constructor: dacă l-ai pune în constructor, ar captura poziția de la creare, care se schimbă la reciclare. În `bind`, `getBindingAdapterPosition()` e evaluat la click.
- `getBindingAdapterPosition()` poate întoarce `RecyclerView.NO_POSITION` (-1) în timpul unei animații. Fără verificare, ai `IndexOutOfBoundsException` la `movies.get(-1)`.
- `launcher` e declarat **după** `movieAdapter` în `onCreate`, dar listener-ul rulează la click, mult mai târziu. Nu e o problemă — dar trebuie să poți explica de ce.

**De reținut:**
- Ordinea de la examen: dependență → XML → adapter → activitate. Dacă începi cu adapterul, nu compilează și nu știi dacă e de la adapter sau de la dependență.
- `setLayoutManager` e obligatoriu. Fără el: listă goală, zero erori.
- `getItemCount()` întoarce `movies.size()`. Dacă întorci altceva, ai `IndexOutOfBoundsException` în `bind`.
- `RecyclerView` **nu are** `setOnItemClickListener`. De asta ai nevoie de interfața proprie.
- `notifyDataSetChanged()` reconstruiește tot, fără animații. Pentru animații: `notifyItemInserted`, `notifyItemChanged`, `notifyItemRemoved`.

**Unde se aplică:** capitolul 11 are aceeași clasă desfășurată pas cu pas, iar capitolul 12 are mecanismul pe date simple (numere 1–100), ca să vezi diferența dintre `ListView` și `RecyclerView` fără formular în jur. Aici ai varianta de examen: compactă, în ordinea în care o scrii.

</details>

---

## Exercițiul 18.6 — URL-ul posterului într-un `TextView`

**Cerință:** în `MovieAdapter.bind()`, afișează URL-ul posterului într-un `TextView` din rând. Fără încărcare de imagine — doar textul.

**Fișiere atinse:** `res/layout/movie_item.xml`, `java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (clasa din 18.5).

**Cum abordezi — pașii tăi:**
1. Deschide `movie_item.xml` și du-te la coloana de info (cea cu `layout_weight="1"`). Găsește `movieFacts` și pune sub el un `TextView` cu `id=moviePosterUrl`, un rând, `ellipsize="middle"`.
2. Deschide `MovieAdapter.java`. Adaugă `private final TextView moviePosterUrl;` în `MovieViewHolder` și `moviePosterUrl = itemView.findViewById(R.id.moviePosterUrl);` în constructor.
3. În `bind()`, după `movieFacts`, citește `movie.getPoster()` și tratează trei cazuri: `null`, `""`, valoare validă.
4. Rulează: Inception arată URL-ul, un film adăugat fără poster nu arată nimic (rândul nu crește cu o linie goală).

**Indiciu 1 — dacă te blochezi la pasul 3:** `poster` are `= null` în model, dar formularul scrie `""` când câmpul e gol (`etPoster.getText().toString()`). Ai nevoie de ambele verificări: `poster != null && !poster.isEmpty()`.

**Indiciu 2 — dacă te blochezi la pasul 4:** dacă rândul fără poster are totuși un spațiu gol sub `movieFacts`, ai folosit `View.INVISIBLE`. Trebuie `View.GONE`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un `TextView` în rând și l-am legat de `Movie.poster`. Nu încărcăm imaginea — afișăm adresa ca text, ceea ce e suficient pentru cerință și nu aduce nicio bibliotecă nouă.

**Cod:**

`res/layout/movie_item.xml` — după `movieFacts`, înainte de `ChipGroup`:

```xml
<TextView
    android:id="@+id/moviePosterUrl"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="4dp"
    android:ellipsize="middle"
    android:maxLines="1"
    android:textColor="#9E9E9E"
    android:textSize="12sp" />
```

`MovieAdapter.java` — trei adăugiri:

```java
// 1. câmp în MovieViewHolder
private final TextView moviePosterUrl;

// 2. în constructor, după movieFacts
moviePosterUrl = itemView.findViewById(R.id.moviePosterUrl);

// 3. în bind(), după movieFacts.setText(...)
String poster = movie.getPoster();
if (poster != null && !poster.isEmpty()) {
    moviePosterUrl.setText(poster);
    moviePosterUrl.setVisibility(View.VISIBLE);
} else {
    moviePosterUrl.setVisibility(View.GONE);
}
```

**De ce:**
- `movie.getPoster()` are două stări „fără valoare": `null` (câmpul e inițializat `= null` în model, iar `new Movie()` nu îl atinge) și `""` (formularul salvează textul gol). Ambele trebuie tratate la fel.
- `ellipsize="middle"` taie mijlocul unui URL lung, păstrând începutul și extensia — mai util decât `end` pentru un link.
- `maxLines="1"` e obligatoriu împreună cu `ellipsize`; altfel `TextView`-ul crește pe două-trei rânduri și cardul se deformează.
- `View.GONE` scoate view-ul din layout, deci nici `layout_marginTop="4dp"` nu mai contează. `View.INVISIBLE` l-ar păstra și ai vedea un gol.

**De reținut:**
- `setText(null)` nu aruncă excepție, dar lasă un `TextView` gol care ocupă totuși rândul. Verificarea explicită e pentru `GONE`, nu pentru `setText`.
- Verificarea se face la **fiecare** `bind`, în ambele ramuri. Un rând reciclat care a avut poster și acum nu are trebuie să revină la `GONE`.
- Dacă ai vrea imaginea reală, ai avea nevoie de o bibliotecă (Glide, Coil) și de o permisiune de rețea. Pentru examen, textul e răspunsul corect la „afișează posterul".

**Unde se aplică:** exact același tipar îl vei folosi la orice câmp opțional — `writer` (18.10), `approval` (18.9), `poster`. Diferența e doar tipul: `String` cu două stări goale, `boolean` fără niciuna.

</details>

---

## Exercițiul 18.7 — `LinearLayoutManager` → `GridLayoutManager` pe 2 coloane

**Cerință:** schimbă lista verticală într-o grilă cu 2 coloane. Apoi explică ce **nu** trebuie modificat și de ce.

**Fișiere atinse:** `java/ro/ase/ie/g1097/activities/MainActivity.java` — o singură linie (plus importul).

**Cum abordezi — pașii tăi:**
1. Deschide `MainActivity.java` și du-te în `initControls()`. Găsește `new LinearLayoutManager(this)`.
2. Schimbă în `new GridLayoutManager(this, 2)`. Schimbă importul: `androidx.recyclerview.widget.GridLayoutManager` în locul lui `LinearLayoutManager`.
3. Rulează. Nu atinge nimic altceva — nici adapterul, nici `movie_item.xml`, nici `getItemCount`.
4. Notează ce s-a schimbat vizual (margini, titluri tăiate, înălțimi) și ce a rămas identic (conținutul rândului, click-ul, salvarea).

**Indiciu 1 — dacă te blochezi la pasul 2:** `GridLayoutManager` e în același pachet cu `LinearLayoutManager` (`androidx.recyclerview.widget`). Al doilea parametru e numărul de coloane, nu înălțimea.

**Indiciu 2 — dacă te blochezi la pasul 4:** răspunsul „de ce nu se schimbă adapterul" e că `LayoutManager`-ul primește view-uri gata umplute de la adapter și doar le așază. Nu știe ce e în ele, deci nu are ce să modifice.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat un obiect. Adapterul, XML-ul rândului și restul activității au rămas neatinse.

**Cod:**

```java
// înainte
recyclerView.setLayoutManager(new LinearLayoutManager(this));

// după
recyclerView.setLayoutManager(new GridLayoutManager(this, 2));
```

Import: `androidx.recyclerview.widget.GridLayoutManager`. Importul lui `LinearLayoutManager` devine inutil — șterge-l (warning, nu eroare, dar codul curat se punctează).

**Ce NU se schimbă — răspunsul care se cere la examen:**
- `MovieAdapter` — zero linii.
- `movie_item.xml` — zero linii.
- `onCreateViewHolder`, `onBindViewHolder`, `getItemCount` — neschimbate.
- Click-ul pe rând, `notifyDataSetChanged()`, fluxul către `ItemActivity` — neschimbate.

**De ce:** `RecyclerView` separă **ce afișezi** (adapter) de **cum aranjezi** (LayoutManager). La `ListView` aranjarea era fixă, verticală, mereu — de aceea acolo schimbarea ar fi însemnat alt widget. La `RecyclerView` e un obiect schimbabil.

**Ce se schimbă vizual (și trebuie observat):**
- fiecare card are jumătate din lățime;
- `layout_marginHorizontal="12dp"` din `movie_item.xml` se aplică **per celulă**, deci între coloane sunt 24dp și la marginea ecranului tot 24dp;
- `app:cardUseCompatPadding="true"` adaugă padding suplimentar — cardurile par mai înguste decât ai crede;
- `movieTitle` are `maxLines="2"`: la jumătate de lățime, titlurile se taie mai des;
- `movieFacts` („148 min. · $160M") poate să nu încapă pe un rând.

**De reținut:**
- Fără `setLayoutManager`, `RecyclerView` nu afișează nimic și nu dă eroare. E cea mai frecventă greșeală la examen.
- `LinearLayoutManager(context)` — vertical (implicit).
- `LinearLayoutManager(context, RecyclerView.HORIZONTAL, false)` — orizontal.
- `GridLayoutManager(context, spanCount)` — grilă cu N coloane.
- `StaggeredGridLayoutManager(2, RecyclerView.VERTICAL)` — grilă cu înălțimi diferite.
- Pentru un rând care să ocupe toată lățimea într-o grilă (un antet, de exemplu): `gridLayoutManager.setSpanSizeLookup(new GridLayoutManager.SpanSizeLookup() { @Override public int getSpanSize(int position) { return position == 0 ? 2 : 1; } });`

**Unde se aplică:** dacă la examen ți se cere „listă orizontală", e `new LinearLayoutManager(this, RecyclerView.HORIZONTAL, false)` — tot o linie, tot fără atingerea adapterului. Orice cerință despre *aranjare* se rezolvă în `MainActivity`, nu în adapter.

</details>

---

## Exercițiul 18.8 — rândul arată `Inception (2010)`: `toString()` sau adapter propriu?

**Cerință:** rândul din `ListView` (încă `ArrayAdapter`, adică înainte de 18.5) trebuie să arate `Inception (2010)`. Dă **două** soluții și compară-le.

**Fișiere atinse:** soluția A → `java/ro/ase/ie/g1097/model/Movie.java`; soluția B → `res/layout/movie_row.xml` + `java/ro/ase/ie/g1097/adapters/MovieListAdapter.java` (din 18.4).

**Cum abordezi — pașii tăi:**
1. Deschide `Movie.java` și găsește `toString()`. Există deja, în format de debug (`Movie{title='...', release=...}`).
2. Soluția A: înlocuiește-l cu `title + " (" + year + ")"`. Anul îl iei cu `SimpleDateFormat("yyyy")`, nu cu `getYear()`.
3. Rulează. Lista arată „Inception (2010)". Nu ai atins niciun alt fișier.
4. Soluția B: dă undo la `toString()` (revino la formatul de debug) și modifică `MovieListAdapter.getView` din 18.4.
5. Scrie comparația: fișiere, linii, timp, efecte secundare, ce poți face în plus.

**Indiciu 1 — dacă te blochezi la pasul 2:** `ArrayAdapter` nu știe ce e un `Movie`. Cheamă `toString()` pe fiecare element — e singurul punct de control asupra textului.

**Indiciu 2 — dacă tot nu merge la pasul 2:** `Date.getYear()` întoarce anul minus 1900 și e depreciat. 2010 devine 110. Folosește `SimpleDateFormat("yyyy", Locale.getDefault())`.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** două răspunsuri corecte la aceeași cerință, cu costuri foarte diferite.

### Soluția A — `toString()`

`Movie.java`:

```java
import java.text.SimpleDateFormat;
import java.util.Locale;

// ...

private static final SimpleDateFormat YEAR_FORMAT =
        new SimpleDateFormat("yyyy", Locale.getDefault());

@Override
public String toString() {
    String year = release != null ? YEAR_FORMAT.format(release) : "?";
    return title + " (" + year + ")";
}
```

Asta **înlocuiește** `toString()`-ul de debug care există acum în `Movie.java`. `ArrayAdapter` îl cheamă pentru fiecare rând, deci lista arată exact ce întoarce metoda. Zero modificări în `MainActivity`.

### Soluția B — adapter propriu

Din 18.4, schimbi doar linia de umplere din `getView`:

```java
holder.rowTitle.setText(movie.getTitle() + " (" + year + ")");
holder.rowSubtitle.setVisibility(View.GONE);
```

(sau elimini de tot `rowSubtitle` din `movie_row.xml`, dacă rândul are o singură linie).

### Comparația

| | A: `toString()` | B: adapter propriu |
|---|---|---|
| Fișiere | 1 (`Movie.java`) | 2–3 |
| Linii scrise | ~8 | ~45 |
| Timp | 2 minute | 15 minute |
| Format | unul singur, global | oricâte, per ecran |
| Stil (bold, gri, două linii, iconițe) | nu | da |
| Efecte secundare | schimbă **orice** `toString()`: log-uri, debugger, `Toast`, alte adaptoare | niciunul |
| Când îl alegi | cerința e doar „rândul să arate X" | cerința cere două linii, culori, mai multe view-uri |

**De ce:** merge A pentru că `ArrayAdapter` cheamă `mObjects.get(position).toString()` și pune rezultatul în `android.R.id.text1`. Nu există alt câmp. Deci singurul punct de control asupra textului e `toString()`.

**De reținut:**
- Capcana anului: `movie.getRelease().getYear()` întoarce **anul − 1900** și e depreciat. 2010 devine 110. Folosește `SimpleDateFormat("yyyy")` sau `Calendar`.
- `SimpleDateFormat` e scump de construit; `static final` = unul singur pentru toate rândurile. Nu e thread-safe, dar aici ești pe UI thread.
- `toString()` nu e „doar pentru debug" în Java — orice cod care îl cheamă îl folosește. `ArrayAdapter` e exact un astfel de cod.
- Dacă examenul cere **și** formatul scurt **și** două linii, răspunsul e B. A nu poate face două linii.
- Dacă ai deja un adapter propriu (18.4), A nu are sens: ai deja locul unde să schimbi textul, fără să atingi modelul.

**Unde se aplică:** dacă la examen vezi `ArrayAdapter` în cod și cerința e despre textul rândului, primul reflex e `toString()`. Dacă vezi `BaseAdapter` sau `RecyclerView.Adapter`, modifici `getView` / `bind`. Regula: **nu schimbi modelul ca să rezolvi o problemă de afișare** dacă ai deja un adapter propriu.

</details>

---

## Exercițiul 18.9 — `Chip`-ul de aprobare, legat și ascuns cu `View.GONE`

**Cerință:** leagă `chipApproval` din `movie_item.xml` de `movie.getApproval()` și ascunde-l cu `View.GONE` când aprobarea e goală.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`. XML-ul are deja chip-ul, cu `android:text="Approved"` hardcodat.

**Cum abordezi — pașii tăi:**
1. Deschide `movie_item.xml` și găsește `chipApproval` — există, în `ChipGroup`-ul `movieStatusGroup`, cu `android:text="Approved"` și `android:clickable="false"`.
2. Deschide `MovieAdapter.java`. Adaugă `private final Chip chipApproval;` în `MovieViewHolder` și `chipApproval = itemView.findViewById(R.id.chipApproval);` în constructor.
3. În `bind()`, scrie ramura dublă: valoare validă → `setText` + `VISIBLE`; altfel → `GONE`.
4. Rulează: Inception arată „PG-13", Toy Story „G", The Matrix „R". Un film fără aprobare nu arată niciun chip.

**Indiciu 1 — dacă te blochezi la pasul 2:** `Chip` extinde `TextView` (prin `AppCompatCheckBox`), deci are `setText`. Importul e `com.google.android.material.chip.Chip`, nu `android.widget.*`.

**Indiciu 2 — dacă te blochezi la pasul 4:** dacă un rând reciclat păstrează chip-ul filmului anterior, ai pus `setVisibility(VISIBLE)` doar pe ramura pozitivă. Ambele ramuri trebuie să seteze vizibilitatea.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am legat un `Chip` de un câmp `String` care poate fi gol, cu ascundere completă când nu are valoare.

**Cod:**

```java
// 1. câmp în MovieViewHolder
private final Chip chipApproval;

// 2. în constructor
chipApproval = itemView.findViewById(R.id.chipApproval);

// 3. în bind(), după movieFacts
String approval = movie.getApproval();
if (approval != null && !approval.trim().isEmpty()) {
    chipApproval.setText(approval);
    chipApproval.setVisibility(View.VISIBLE);
} else {
    chipApproval.setVisibility(View.GONE);
}
```

Import: `com.google.android.material.chip.Chip`.

**De ce:**
- `Chip` extinde `AppCompatCheckBox`, care extinde `TextView` — deci `setText()` există și funcționează normal.
- `View.GONE` = scos din layout, nu ocupă spațiu. `View.INVISIBLE` = ocupă spațiu, dar nu se vede. Într-un `ChipGroup`, `INVISIBLE` lasă o gaură între chip-uri.
- `trim()`: formularul poate produce `" "` dacă utilizatorul tastează un spațiu. `isEmpty()` singur nu prinde cazul.
- `null`: `new Movie()` fără argumente lasă `approval = null`. `approval.isEmpty()` ar arunca `NullPointerException` — de aici verificarea `!= null` **înainte** de orice altceva.

**De reținut:**
- `setVisibility` se face la **fiecare** `bind`, în ambele ramuri. Dacă îl pui doar pe `VISIBLE`, un rând reciclat rămâne cu chip-ul de la filmul anterior. Ăsta e bug-ul clasic de reciclare și se vede imediat la scroll.
- Dacă toate cele trei chip-uri sunt `GONE`, `ChipGroup`-ul rămâne cu `layout_marginTop="8dp"` și înălțime 0 — adică 8dp de spațiu mort sub `movieFacts`. Refinare: ține și `movieStatusGroup` în `ViewHolder` și ascunde-l când toate trei sunt goale.
- `chipApproval` are `android:clickable="false"` — e etichetă, nu buton. Nu adăuga listener.
- `app:chipMinHeight="28dp"` și `app:ensureMinTouchTargetSize="false"` sunt deja în XML; nu le atinge, sunt acolo ca chip-ul să nu fie uriaș.
- Textul `"Approved"` din XML e doar pentru preview. Dacă uiți să îl legi, toate rândurile arată „Approved" — și pare că merge.

**Unde se aplică:** `chipWatched` și `chipWatchlist` sunt exact același tipar, dar cu `boolean`:

```java
chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
```

Aici nu există „gol": `boolean` e mereu `true` sau `false`. De aceea nu au nevoie de verificare de `null` — doar de ambele ramuri ale ternarului.

</details>

---

## Exercițiul 18.10 — combo: atributul `writer`, în XML și în `bind()`

**Cerință:** adaugă în `movie_item.xml` un `TextView` pentru `writer` și leagă-l în `MovieAdapter.bind()`. Filmul trebuie să aibă câmpul — altfel cerința nu se poate scrie.

**Fișiere atinse:** `java/ro/ase/ie/g1097/model/Movie.java`, `res/layout/movie_item.xml`, `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`. Opțional, dacă examenul cere și introducerea valorii: `res/layout/activity_item.xml` + `ItemActivity.java`.

**Cum abordezi — pașii tăi:**
1. Deschide `Movie.java`. Nu are `writer`. Adaugă câmpul, getter-ul și setter-ul. Decizi apoi: îl pui și în constructor sau doar ca setter?
2. Dacă îl pui în constructor, actualizează cele 3 apeluri `new Movie(...)` din `addSampleMovies()` — altfel nu compilează. Dacă nu, adaugă o valoare cu setter-ul, ca să ai ce vedea.
3. Deschide `movie_item.xml` și pune `TextView`-ul `movieWriter` sub `movieFacts` (sau sub `movieSubtitle`, dacă vrei lângă titlu).
4. Deschide `MovieAdapter.java`: câmp în `ViewHolder`, `findViewById` în constructor, ramura din `bind()`.
5. Rulează: Inception arată „Written by Christopher Nolan". Un film fără writer nu arată linia deloc.

**Indiciu 1 — dacă te blochezi la pasul 1:** ordinea e model → layout → adapter. Dacă începi cu XML-ul, ajungi să scrii `movie.getWriter()` într-un adapter unde metoda nu există încă și nu înțelegi eroarea.

**Indiciu 2 — dacă te blochezi la pasul 5:** dacă totul compilează dar nu vezi nimic pe ecran, toate cele 3 filme demo au `writer == null` și `TextView`-ul e `GONE`. Pune o valoare într-un sample — altfel pari că nu ai făcut nimic.

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat un atribut nou în model, un view nou în rând și legătura dintre ele. Ăsta e exercițiul care apare cel mai des la examen: „adaugă atributul X și afișează-l în listă".

### Pas 1 — `Movie.java`

```java
private String writer;

public String getWriter() {
    return writer;
}

public void setWriter(String writer) {
    this.writer = writer;
}
```

Apoi decizi constructorul. Varianta recomandată: adaugi parametrul **la finalul** constructorului cu 10 argumente.

```java
public Movie(String title, Date release, String genre, double budget, int duration,
             float rating, boolean watched, String approval, boolean onWatchlist,
             String poster, String writer) {
    this.title = title;
    this.release = release;
    this.genre = genre;
    this.budget = budget;
    this.duration = duration;
    this.rating = rating;
    this.watched = watched;
    this.approval = approval;
    this.onWatchlist = onWatchlist;
    this.poster = poster;
    this.writer = writer;
}
```

`MainActivity.addSampleMovies()` — cele 3 apeluri primesc încă un argument la final:

```java
"https://example.com/posters/inception.jpg",
"Christopher Nolan"));
```

**De ce la final:** dacă ai pune `writer` după `title`, ar trebui să muți toate argumentele la toate cele 3 apeluri — mai multe șanse de greșeală, mai mult timp. La final, adaugi o linie per apel.

Alternativa fără constructor: lași constructorul neatins și faci `movies.get(0).setWriter("Christopher Nolan");` în `addSampleMovies()`. Merge, dar e mai puțin curat — modelul are un câmp pe care constructorul nu îl acoperă.

### Pas 2 — `movie_item.xml`

După `movieFacts`, înainte de `ChipGroup`:

```xml
<TextView
    android:id="@+id/movieWriter"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="2dp"
    android:ellipsize="end"
    android:maxLines="1"
    android:textColor="#616161"
    android:textSize="13sp" />
```

### Pas 3 — `MovieAdapter.java`

```java
// 1. câmp în MovieViewHolder
private final TextView movieWriter;

// 2. în constructor
movieWriter = itemView.findViewById(R.id.movieWriter);

// 3. în bind(), după movieFacts
String writer = movie.getWriter();
if (writer != null && !writer.isEmpty()) {
    movieWriter.setText("Written by " + writer);
    movieWriter.setVisibility(View.VISIBLE);
} else {
    movieWriter.setVisibility(View.GONE);
}
```

**De ce:**
- Ordinea model → layout → adapter nu e o preferință: dacă adaugi `TextView`-ul în XML dar uiți `findViewById`, compilatorul nu se plânge — `bind()` pur și simplu nu îl atinge, iar rândul arată gol. Dacă uiți câmpul în model, **nu compilează** (`getWriter()` nu există). Compilatorul te prinde doar într-o direcție.
- `Movie` e `Serializable`: un `String` nou nu cere nimic special. `Date` era deja serializabil, `String` la fel. Nu trebuie `serialVersionUID`.
- Prefixul „Written by " se pune în `bind`, nu în model. Modelul ține date, nu text de afișare. Dacă mâine vrei altă limbă, schimbi un singur loc.

**De reținut:**
- Dacă examenul cere **și** formularul, sunt exact cei cinci pași din 18.2, pe un câmp text: `activity_item.xml` (`TextInputLayout` + `etWriter`), câmp în `ItemActivity`, `initControls`, `fillForm` → `etWriter.setText(existing.getWriter())`, `saveMovie` → `movie.setWriter(etWriter.getText().toString())`.
- Verifică vizual. Un atribut legat corect dar mereu `GONE` arată exact ca un atribut nelegat.
- Dacă adaugi câmpul în constructor, numărul de argumente se schimbă — orice alt `new Movie(...)` din proiect trebuie actualizat. În `d719ffc` sunt exact 3, toate în `addSampleMovies()`. `saveMovie()` folosește `new Movie()` fără argumente, deci nu e afectat.
- `toString()` nu trebuie atins. Dacă îl lași în formatul de debug, nu strică nimic.

**Unde se aplică:** ăsta e tiparul general pentru „adaugă atributul X". Trei fișiere obligatorii (model, layout, adapter) plus două opționale dacă se cere și formularul (layout formular, `ItemActivity`). Numără-le la început, ca să știi când ai terminat.

</details>

---

## Rezumat capitol 18

### Cele trei rețete, în formă minimă

**1. Leagă valoarea X de widget-ul Y** (5 minute)

```
findViewById(R.id.widgetY)  →  câmp
listener (dacă widgetul se schimbă)  →  widgetY.setX(valoare)
```

Dacă widgetul se schimbă singur (SeekBar, Switch, CheckBox, RatingBar), ai nevoie de listener. Dacă valoarea vine din model și se afișează o dată, ai nevoie doar de setter.

**2. Schimbă un widget cu altul** (10–15 minute)

Cinci puncte, în ordinea asta:

| # | Unde | Ce faci |
|---|---|---|
| 1 | XML | scoți widgetul vechi (cu tot cu `TextInputLayout`, dacă are) și pui widgetul nou, cu `id` |
| 2 | câmpul | schimbi tipul: `private EditText etBudget;` → `private SeekBar sbBudget;` |
| 3 | `initControls` | `findViewById` pe noul id |
| 4 | `fillForm` | citești din model și scrii în widget (conversia, dacă tipurile diferă) |
| 5 | `saveMovie` | citești din widget și scrii în model (conversia inversă) |

**3. Fă un adapter** (20 de minute)

```
dependență (dacă e RecyclerView)
  → XML: widget nou + șterge android:entries
  → Adapter: onCreateViewHolder / onBindViewHolder / getItemCount + ViewHolder
  → Activitate: setLayoutManager + setAdapter (+ click)
```

### Ce spui când ți se cere să explici

| Întrebare | Răspunsul scurt |
|---|---|
| De ce se actualizează eticheta fără să o ating? | `setProgress` / `setChecked` declanșează listener-ul cu `fromUser = false` |
| De ce `ViewHolder` e `static`? | altfel fiecare instanță ține o referință la adapter |
| De ce click-ul e în `bind`, nu în constructor? | poziția se schimbă la reciclare; în `bind` e evaluată la click |
| De ce `View.GONE` și nu `INVISIBLE`? | `GONE` scoate view-ul din layout, nu lasă gol |
| De ce nu merge `ArrayAdapter` pentru două linii? | știe un singur `TextView` (`android.R.id.text1`) |
| Ce nu se schimbă când treci pe grilă? | adapterul și XML-ul rândului — doar `LayoutManager`-ul |
| De ce `toString()` e o soluție validă? | `ArrayAdapter` îl cheamă pe fiecare element |

### Planul celor 30 de minute

| Minute | Ce faci |
|---|---|
| 0–2 | Citești cerințele și notezi fișierele atinse pentru fiecare |
| 2–10 | Rezolvi cerința de binding sau de widget (compilează repede, riști puțin) |
| 10–12 | Rulezi. Dacă nu merge, repari **înainte** să începi adapterul |
| 12–28 | Adapterul: dependență → XML → clasă → activitate |
| 28–30 | Rulezi din nou, verifici click-ul și salvarea, ștergi importurile inutile |

### Checklist final

- [ ] Am atins toate fișierele din „Fișiere atinse" la fiecare exercițiu.
- [ ] `etBudget` / `rbRating` / `listView` nu mai apar nicăieri în cod după înlocuire (Ctrl+F).
- [ ] `setLayoutManager` e apelat înainte de `setAdapter`.
- [ ] Fiecare ramură `if` din `bind()` setează vizibilitatea, nu doar cea pozitivă.
- [ ] Am rulat aplicația: adaug un film, editez un film, salvez, văd rezultatul în listă.
