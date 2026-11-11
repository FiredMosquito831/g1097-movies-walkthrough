# Capitolul 23 — Bancul 5: migrarea completă ListView → RecyclerView

**Obiectiv:** să execuți migrarea `ListView` → `RecyclerView` în zece cerințe separate, fiecare cu propriul punct de verificare, astfel încât să poți opri oriunde și să ai un proiect care compilează și rulează.

**De ce în 10 pași:** la examen cerința vine bucată cu bucată („adaugă dependența", „fă adapterul", „leagă rating-ul", „repară notificarea"), nu dintr-o suflare. Fiecare exercițiu de aici e o astfel de bucată, cu starea intermediară descrisă explicit: după pasul N proiectul compilează, iar tu știi exact ce vezi pe ecran. Varianta dintr-o singură bucată e exercițiul 18.5; aici e aceeași migrare, tăiată în felii.

**Starea de plecare** (commit `d719ffc`, folderul `cod-final`):
- `activities/MainActivity.java` — `ListView` + `ArrayAdapter<Movie>` + `setOnItemClickListener`, trei filme de probă în `addSampleMovies()`.
- `res/layout/activity_main.xml` — `<ListView android:id="@+id/listView" ... android:entries="@array/items" />` într-un `FrameLayout`, plus FAB-ul.
- `res/layout/movie_item.xml` — **există, e complet, dar nu e referențiat de nimic** în tot proiectul.
- `gradle/libs.versions.toml` și `build.gradle.kts` — **nu conțin `recyclerview`**, nici în `[versions]`, nici în `[libraries]`, nici în `dependencies`.
- `model/Movie.java` — `Serializable`, cu `title`, `release` (`Date`), `genre`, `budget` (`double`), `duration` (`int`), `rating` (`float`), `watched`, `approval`, `onWatchlist`, `poster`.

**Starea finală:** `RecyclerView` cu `LinearLayoutManager`, `MovieAdapter` cu `MovieViewHolder` care leagă tot cardul din `movie_item.xml` (titlu, subtitlu gen · an, rating, durată + buget, trei chips-uri), click prin interfață proprie către `launcher`, inserare și editare notificate cu `notifyItemInserted` / `notifyItemChanged`.

**Tabel: ce se schimbă**

| | ListView | RecyclerView |
|---|---|---|
| Dependență | vine cu `appcompat` | `androidx.recyclerview:recyclerview`, declarată separat |
| Widget în XML | `<ListView>` | `<androidx.recyclerview.widget.RecyclerView>` |
| Atribut de listă | `android:entries="@array/items"` | nu există; `tools:listitem` doar pentru preview |
| Adapter | `ArrayAdapter<Movie>` (gata făcut) | `RecyclerView.Adapter<MovieViewHolder>` (scris de tine) |
| Rând | `android.R.layout.simple_list_item_1` + `toString()` | `movie_item.xml` + `ViewHolder` |
| Reciclare | manuală (`convertView` + `setTag`) | automată, prin `ViewHolder` |
| Aranjare | proprie lui `AbsListView` | `LayoutManager` separat, obligatoriu |
| Click pe rând | `setOnItemClickListener` | interfață proprie, legată pe `itemView` |
| Notificare | `notifyDataSetChanged()` | `notifyItemInserted` / `notifyItemChanged` / `notifyItemRemoved` |
| Animații | nu are | `ItemAnimator` implicit |
| Metode obligatorii | `getView`, `getCount`, `getItem` | `onCreateViewHolder`, `onBindViewHolder`, `getItemCount` |

> **Regula celor 10 pași:** dependență → XML → clasă goală → `ViewHolder` → `onCreateViewHolder` → text → rating → facts + chips → click → activitate. Ordinea nu e întâmplătoare: fiecare pas are nevoie de tipul creat la pasul anterior, iar activitatea se atinge ultima, ca să nu ai niciodată două erori deodată.

---

## Exercițiul 23.1 — Dependența `androidx.recyclerview`

**Cerință:** adaugă biblioteca `androidx.recyclerview:recyclerview` în catalogul de versiuni și în lista de dependențe a modulului, apoi sincronizează Gradle. Nu se scrie nicio linie de cod Java și nu se atinge niciun layout.

**Fișiere atinse:** `gradle/libs.versions.toml`, `build.gradle.kts`

**Cum abordezi — pașii tăi:**
1. Deschide `gradle/libs.versions.toml`. Găsește secțiunea `[versions]` — începe cu `agp = "9.4.1"` și se termină cu `coordinatorlayout = "1.3.0"`. Adaugă o linie nouă la finalul secțiunii: `recyclerview = "1.4.0"`.
2. În același fișier, coboară la `[libraries]`. Ultima linie e cea a lui `coordinatorlayout`. Adaugă sub ea linia pentru `recyclerview`, cu aceeași formă `group` / `name` / `version.ref`.
3. Deschide `build.gradle.kts` din rădăcina modulului. În blocul `dependencies { }`, adaugă `implementation(libs.recyclerview)` imediat după `implementation(libs.material)`.
4. Apasă **Sync Now** pe banner-ul care apare sus în Android Studio (sau `File → Sync Project with Gradle Files`). Așteaptă să se termine bara de progres.
5. Verifică: `Build → Make Project` trebuie să dea `BUILD SUCCESSFUL`. Deschide panoul **External Libraries** din Project view — trebuie să apară `Gradle: androidx.recyclerview:recyclerview:1.4.0`. Pe ecranul telefonului nu se schimbă absolut nimic, pentru că încă nu folosește nimeni clasa.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 2</summary>

numele din `[libraries]` devine numele folosit în `build.gradle.kts`, cu cratimele transformate în puncte. Aliasul `recyclerview` (un singur cuvânt) se accesează `libs.recyclerview`. Dacă ai scrie `androidx-recyclerview`, ai accesa `libs.androidx.recyclerview`. Aici folosim forma scurtă, ca la `appcompat` și `material`.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 3</summary>

`implementation(...)` cere **accesorul generat**, nu coordonatele Maven. `implementation("androidx.recyclerview:recyclerview:1.4.0")` ar merge și așa, dar în proiectul ăsta toate dependențele trec prin catalog — dacă scrii coordonatele direct, pierzi punctul pe cerință. Dacă `libs.recyclerview` apare roșu, sync-ul de la pasul 4 nu s-a făcut încă.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat o versiune și o intrare de librărie în catalog, apoi am legat-o în lista de dependențe a modulului. Zero cod Java.

**Cod:**

`gradle/libs.versions.toml` — secțiunea `[versions]`, la final:

```toml
[versions]
agp = "9.4.1"
junit = "4.13.2"
junitVersion = "1.3.0"
espressoCore = "3.7.0"
appcompat = "1.8.0"
material = "1.14.0"
activityKtx = "1.13.0"
constraintlayout = "2.2.2"
coordinatorlayout = "1.3.0"
recyclerview = "1.4.0"
```

`gradle/libs.versions.toml` — secțiunea `[libraries]`, la final:

```toml
[libraries]
# ... cele existente ...
coordinatorlayout = { group = "androidx.coordinatorlayout", name = "coordinatorlayout", version.ref = "coordinatorlayout" }
recyclerview = { group = "androidx.recyclerview", name = "recyclerview", version.ref = "recyclerview" }
```

`build.gradle.kts` — blocul `dependencies`, linia nouă e ultima `implementation`:

```kotlin
dependencies {
    implementation(libs.activity.ktx)
    implementation(libs.appcompat)
    implementation(libs.constraintlayout)
    implementation(libs.material)
    implementation(libs.recyclerview)
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}
```

**De ce:**
- `RecyclerView` nu face parte din SDK-ul Android și nu e în `appcompat`. E un artefact AndroidX separat, cu ciclu de versiuni propriu — de aceea are intrare proprie în catalog.
- Catalogul are două secțiuni pentru că sunt două lucruri diferite: `[versions]` ține **numerele**, `[libraries]` ține **coordonatele**. O librărie poate împrumuta versiunea alteia prin `version.ref`, dar aici are versiune proprie.
- `implementation` înseamnă „o folosesc în interiorul modulului, nu o expun consumatorilor". Pentru o aplicație (nu o librărie) e varianta corectă; `api` ar avea sens doar într-un modul de librărie.

**De reținut:**
- Versiunea `1.4.0` e cea folosită în tot cursul (cap. 11, cap. 18). Dacă Android Studio îți propune una mai nouă la sync, accept-o — contează structura, nu numărul.
- `material` aduce `recyclerview` tranzitiv, deci e posibil ca proiectul să compileze și fără pasul ăsta. Nu te baza pe asta: declari explicit fiecare bibliotecă din care folosești clase direct. Altfel, o actualizare a lui `material` îți poate strica build-ul fără să fi atins tu nimic.
- Sync-ul nu e opțional. Fără el, Android Studio nu regenerează accesorii `libs.*` și tot ce urmează apare roșu, deși fișierele sunt corecte.

**Unde se aplică:** orice cerință de forma „adaugă biblioteca X". Aceeași mecanică (versiune → librărie → `implementation` → sync) se folosește și pentru Glide, Retrofit, Room. Dacă examenul cere „adaugă dependența", ăsta e răspunsul complet, în trei fișiere-logice și un sync.

</details>

---

## Exercițiul 23.2 — `ListView` → `RecyclerView` în layout

**Cerință:** înlocuiește widget-ul din `activity_main.xml` cu `RecyclerView` și repară strictul necesar în `MainActivity` ca proiectul să compileze și aplicația să nu crape. Nu se creează încă niciun adapter.

**Fișiere atinse:** `res/layout/activity_main.xml`, `java/ro/ase/ie/g1097/activities/MainActivity.java`

**Cum abordezi — pașii tăi:**
1. Deschide `res/layout/activity_main.xml`. Găsește blocul `<ListView ... />` — e primul copil al lui `FrameLayout`, are `android:id="@+id/listView"` și `android:entries="@array/items"`.
2. Înlocuiește-l cu `<androidx.recyclerview.widget.RecyclerView ... />`, cu `android:id="@+id/recyclerView"`, `layout_width`/`layout_height` `match_parent`, `tools:itemCount="3"` și `tools:listitem="@layout/movie_item"`. Șterge `android:entries`.
3. Șterge și `android:orientation="horizontal"` de pe `FrameLayout` — `FrameLayout` nu are orientare, atributul era ignorat.
4. Deschide `MainActivity.java`. Șterge `import android.widget.ListView;` și `import android.widget.AdapterView;`, adaugă `import androidx.recyclerview.widget.RecyclerView;`.
5. Schimbă câmpul `private ListView listView;` în `private RecyclerView recyclerView;`.
6. În `initControls()`: `listView = findViewById(R.id.listView);` devine `recyclerView = findViewById(R.id.recyclerView);`, iar linia `listView.setAdapter(movieAdapter);` se **șterge** (nu ai ce adapter să pui încă).
7. În `initListeners()`: șterge integral blocul `listView.setOnItemClickListener(new AdapterView.OnItemClickListener() { ... })`. `RecyclerView` nu are metoda asta — dacă o lași, nu compilează.
8. Rulează. Trebuie să vezi un ecran gol cu FAB-ul în colț. Apasă FAB-ul, completează formularul, salvează: aplicația **nu** crapă, dar lista rămâne goală.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 2</summary>

`RecyclerView` nu acceptă `android:entries`. Atributul aparține de `AbsListView` (clasa-părinte a lui `ListView`), nu de `RecyclerView`, care e un `ViewGroup` simplu. Dacă îl lași, build-ul trece, dar atributul e ignorat complet — și e o greșeală pe care corectorul o vede din prima.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 5</summary>

dacă păstrezi id-ul `listView` ca să nu atingi `MainActivity`, codul **compilează**, dar la runtime primești `ClassCastException: androidx.recyclerview.widget.RecyclerView cannot be cast to android.widget.ListView`. `findViewById` e generic și face cast la tipul cerut; compilatorul nu poate verifica ce obiect găsește efectiv în XML. Redenumirea id-ului e ce te forțează să schimbi tipul.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am schimbat widget-ul în XML, am schimbat tipul câmpului și cele două apeluri care nu mai au sens pe `RecyclerView`. Lista e acum goală pentru că nu are adapter — starea e corectă pentru pasul ăsta.

**Cod:**

`res/layout/activity_main.xml` — fișierul complet după modificare:

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/main"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".activities.MainActivity">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        tools:itemCount="3"
        tools:listitem="@layout/movie_item" />

    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/floatingActionButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:contentDescription="Add"
        app:srcCompat="@drawable/outline_add_24" />

</FrameLayout>
```

`MainActivity.java` — exact cele patru locuri atinse:

```java
// 1. importuri
import androidx.recyclerview.widget.RecyclerView;   // nou
// ȘTERSE: import android.widget.AdapterView;
// ȘTERSE: import android.widget.ListView;

// 2. câmpul
private RecyclerView recyclerView;                  // era: private ListView listView;

// 3. initControls()
private void initControls() {
    fabInsert = findViewById(R.id.floatingActionButton);
    recyclerView = findViewById(R.id.recyclerView);
    // ȘTERSĂ: listView.setAdapter(movieAdapter);
}

// 4. initListeners() — rămâne doar blocul FAB-ului
private void initListeners() {
    fabInsert.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, ItemActivity.class);
            launcher.launch(intent);
        }
    });
    // ȘTERS integral: listView.setOnItemClickListener(new AdapterView.OnItemClickListener() { ... });
}
```

**De ce:**
- `android:entries="@array/items"` era deja mort înainte de migrare: `initControls()` chema `listView.setAdapter(movieAdapter)`, care înlocuia adapterul construit din `entries`. Cu `RecyclerView` atributul dispare cu totul, pentru că nu există pe `AbsListView`.
- `tools:listitem="@layout/movie_item"` e înlocuitorul modern: îi spune **doar editorului** să deseneze un rând de probă folosind cardul real. La runtime nu face nimic. `tools:itemCount="3"` îi spune câte rânduri de probă să deseneze. E primul loc din proiect care referențiază `movie_item.xml` — până acum fișierul era complet nefolosit.
- `tools:` = design-time, `android:` = runtime. Regula ține pentru toate atributele `tools:*`.
- `RecyclerView` nu are `setOnItemClickListener` din design: un rând poate avea zone click-abile diferite (card, poster, buton). Click-ul se leagă manual, pe `itemView`, în adapter — pasul 23.9.

**De reținut:**
- După 23.2 aplicația **rulează**, dar lista e goală. Nu e un bug: `RecyclerView` fără adapter nu afișează nimic, iar `RecyclerView` fără `LayoutManager` nu afișează nimic **fără nicio eroare în Logcat**. A doua e capcana clasică de examen.
- `ArrayAdapter`-ul e încă construit în `onCreate` și `notifyDataSetChanged()` e încă apelat din callback-ul lui `launcher`. Nu deranjează cu nimic — un adapter neatașat nu are ce să redeseneze. Se curăță abia la 23.10, când îl înlocuim cu `MovieAdapter`.
- `@array/items` din `strings.xml` rămâne acum fără niciun consumator. Poți să-l ștergi, dar nu e obligatoriu și nu aduce puncte.

**Unde se aplică:** orice cerință „înlocuiește widget-ul X cu Y". Șablonul e mereu același: XML → tipul câmpului → `findViewById` → apelurile care nu mai există pe tipul nou. Când schimbi tipul, compilatorul îți spune exact ce apeluri au murit; nu trebuie să le ghicești.

</details>

---

## Exercițiul 23.3 — `MovieAdapter` cu cele trei metode obligatorii

**Cerință:** creează clasa `MovieAdapter` în pachetul `adapters`, care extinde `RecyclerView.Adapter`, cu cele trei metode abstracte implementate. Clasa compilează, dar nu e folosită de nicio activitate — pe ecran nu se schimbă nimic.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java` (fișier nou)

**Cum abordezi — pașii tăi:**
1. În Project view, click dreapta pe pachetul `ro.ase.ie.g1097` → `New → Package`, nume `adapters`. (Sau `New → Java Class` și scrii numele complet `ro.ase.ie.g1097.adapters.MovieAdapter` — Android Studio creează și pachetul.)
2. `New → Java Class` în pachetul nou, nume `MovieAdapter`, tip `Class`.
3. Scrie declarația: `public class MovieAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder>`. Observă că parametrul generic e încă `RecyclerView.ViewHolder`, nu o clasă a ta — clasa ta de `ViewHolder` apare la 23.4.
4. Adaugă câmpul `private final List<Movie> movies;` și un constructor care îl primește.
5. Implementează `getItemCount()`: `return movies.size();`.
6. Implementează `onCreateViewHolder(...)` returnând un `ViewHolder` minimal — `RecyclerView.ViewHolder` e **abstract**, deci ai nevoie de o subclasă anonimă: `new RecyclerView.ViewHolder(new View(parent.getContext())) { }`.
7. Implementează `onBindViewHolder(...)` cu corp gol și un comentariu `// 23.6`.
8. `Build → Make Project`. Trebuie `BUILD SUCCESSFUL`. Pe ecran: neschimbat.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 3</summary>

`RecyclerView.Adapter` cere un singur parametru generic — tipul `ViewHolder`-ului. Dacă îl lași fără (`extends RecyclerView.Adapter`), primești `raw use of parameterized class` și `onCreateViewHolder` nu mai are ce returna type-safe. Dacă pui `RecyclerView.Adapter<Movie>` (tipul modelului), primești eroare pentru că `Movie` nu extinde `ViewHolder`.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 6</summary>

`new RecyclerView.ViewHolder(view)` nu compilează — clasa e `abstract`. Nu e o problemă de sintaxă, e prin design: `ViewHolder` e făcut să fie subclasat. Trucul `{ }` la final creează o subclasă anonimă, suficientă pentru un schelet care nu afișează nimic. La 23.4 o înlocuim cu clasa noastră.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am creat scheletul adapterului. Are datele, știe câte rânduri sunt, dar nu știe să construiască și nici să umple un rând. Nu e legat nicăieri.

**Cod:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`, fișier complet:

```java
package ro.ase.ie.g1097.adapters;

import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

import ro.ase.ie.g1097.model.Movie;

public class MovieAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) {
        this.movies = movies;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View randGol = new View(parent.getContext());
        return new RecyclerView.ViewHolder(randGol) { };
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        // 23.6
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }
}
```

**De ce:**
- Cele trei metode sunt singurele abstracte din `RecyclerView.Adapter`. `onCreateViewHolder` construiește un rând gol, `onBindViewHolder` umple un rând existent, `getItemCount` spune câte rânduri există. Dacă lipsește una, clasa nu compilează.
- `movies` e `final` și e **aceeași listă** pe care o ține și `MainActivity`. Adapterul nu copiază datele, doar le citește. De aceea `movies.add(...)` din activitate se vede în listă fără să reasignezi nimic.
- `@NonNull` pe parametri și pe valoarea returnată e contract, nu decor: `RecyclerView` nu acceptă un `ViewHolder` null din `onCreateViewHolder`.
- `RecyclerView.ViewHolder` e `abstract`, deci subclasa anonimă `{ }` e singura variantă de a returna ceva fără să scrii o clasă separată.

**De reținut:**
- Un `Adapter` nu afișează nimic prin el însuși. Are nevoie de `setAdapter` **și** `setLayoutManager` pe un `RecyclerView` (23.10). De aceea pașii 23.3–23.9 nu schimbă ecranul.
- `getItemCount()` trebuie să fie sincron cu lista reală. Dacă întorci o valoare mai mare decât `movies.size()`, `onBindViewHolder` ajunge la `movies.get(poziție_inexistentă)` și primești `IndexOutOfBoundsException` la derulare, nu la pornire.
- Pachetul `adapters` e unul dintre cele trei pachete ale proiectului (`model`, `activities`, `adapters`). Adapterul nu are voie să cunoască `MainActivity` — comunică înapoi doar prin interfața de la 23.9.

**Unde se aplică:** orice cerință „creează un adapter pentru `RecyclerView`". Scheletul e identic indiferent de model: trei metode, un câmp cu lista, un constructor. Diferența dintre adaptoare e doar ce se scrie în `onCreateViewHolder` și `onBindViewHolder`.

</details>

---

## Exercițiul 23.4 — `MovieViewHolder` cu câmpurile din `movie_item.xml`

**Cerință:** adaugă în `MovieAdapter` o clasă interioară statică `MovieViewHolder` care ține referințe la toate view-urile din card și le caută o singură dată, în constructor. Adapterul rămâne parametrizat pe `RecyclerView.ViewHolder` — clasa nouă nu e încă folosită.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**Cum abordezi — pașii tăi:**
1. Deschide `res/layout/movie_item.xml` și notează toate `android:id`-urile: `moviePoster`, `movieTitle`, `movieSubtitle`, `movieRating`, `movieRatingValue`, `movieFacts`, `movieStatusGroup`, `chipApproval`, `chipWatched`, `chipWatchlist`.
2. Deschide `MovieAdapter.java`. La finalul clasei, înainte de acolada de închidere, scrie `public static class MovieViewHolder extends RecyclerView.ViewHolder { }`.
3. Declară câte un câmp `private final` pentru fiecare view pe care îl legi: `TextView` pentru titlu, subtitlu, valoarea rating-ului și facts; `RatingBar` pentru rating; `Chip` pentru cele trei chips-uri. `moviePoster` și `movieStatusGroup` rămân nelegate.
4. Scrie constructorul `public MovieViewHolder(@NonNull View itemView)`, cu `super(itemView);` pe prima linie.
5. În constructor, câte o linie `câmp = itemView.findViewById(R.id.xxx);` pentru fiecare.
6. Adaugă importurile: `android.widget.RatingBar`, `android.widget.TextView`, `com.google.android.material.chip.Chip`, `ro.ase.ie.g1097.R`.
7. `Build → Make Project`. `BUILD SUCCESSFUL`. Pe ecran: neschimbat — clasa e declarată, dar nimeni nu o instanțiază încă.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 2</summary>

clasa interioară se pune **în interiorul** lui `MovieAdapter`, nu ca fișier separat. `static` nu e opțional: fără el, fiecare `ViewHolder` ține o referință la adapter, iar la reciclare rămâi cu obiecte care se țin reciproc în viață.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 5</summary>

`findViewById` se apelează pe `itemView`, nu pe `this` și nu pe `parent`. `ViewHolder` nu e un `View` — e doar un obiect care ține unul. Dacă scrii `findViewById(...)` simplu, compilatorul îți spune că metoda nu există în `ViewHolder`.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat clasa care ține referințele rândului. Căutarea cu `findViewById` se face o singură dată, la crearea rândului, nu la fiecare afișare.

**Cod:** adaugă în `MovieAdapter.java`, înainte de acolada finală a clasei:

```java
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
    }
```

Importurile care se adaugă la începutul fișierului:

```java
import android.widget.RatingBar;
import android.widget.TextView;

import com.google.android.material.chip.Chip;

import ro.ase.ie.g1097.R;
```

**De ce:**
- `ViewHolder` există exact pentru asta: `findViewById` e o căutare în arborele de view-uri, iar fără `ViewHolder` s-ar face la fiecare afișare a fiecărui rând, la fiecare derulare. Cu el, se face o dată per rând creat, apoi referințele se refolosesc.
- `static` e obligatoriu din punct de vedere practic: o clasă interioară non-statică păstrează o referință implicită la instanța exterioară (`MovieAdapter`). Cu 10 rânduri vizibile ai 10 referințe inutile, iar dacă adapterul moare, rândurile îl țin în viață.
- `moviePoster` rămâne nelegat intenționat: proiectul nu are nicio bibliotecă de încărcat imagini (Glide, Coil, Picasso), iar `poster` e un URL text. Cardul afișează iconița din XML. Legarea unei imagini reale e altă cerință.
- `movieStatusGroup` (ChipGroup-ul) nu are nevoie de referință: ascundem chips-urile individual, iar grupul se rearanjează singur.

**De reținut:**
- Câmpurile sunt `final`: se scriu o dată în constructor și nu se mai ating. Dacă le faci mutabile, nimic nu te oprește să le reasignezi din greșeală în `bind`.
- Tipul câmpului trebuie să fie tipul real din XML. `movieRating` e `RatingBar`, nu `TextView`; `chipApproval` e `Chip` (din Material), nu `TextView`. Un `findViewById` cu tip greșit compilează și crapă la runtime cu `ClassCastException`.
- Clasa e `public static`, nu `private`: apare ca parametru generic în semnătura publică a adapterului. Dacă o faci `private`, tot compilează intern, dar nu mai poți scrie `RecyclerView.Adapter<MovieAdapter.MovieViewHolder>` din alt fișier.

**Unde se aplică:** orice `ViewHolder`, pentru orice model. Regula: un câmp per view pe care îl modifici din cod, câte un `findViewById` în constructor, `final` peste tot. View-urile pe care doar le lași așa cum sunt în XML nu primesc câmp.

</details>

---

## Exercițiul 23.5 — `onCreateViewHolder`: inflate `movie_item`

**Cerință:** leagă `MovieViewHolder` de adapter — schimbă parametrul generic și fă `onCreateViewHolder` să umfle `R.layout.movie_item` și să returneze un `MovieViewHolder` construit pe view-ul umflat.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**Cum abordezi — pașii tăi:**
1. Deschide `MovieAdapter.java`.
2. Schimbă declarația clasei: `extends RecyclerView.Adapter<RecyclerView.ViewHolder>` devine `extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder>`.
3. Schimbă semnătura lui `onCreateViewHolder` să returneze `MovieViewHolder` în loc de `RecyclerView.ViewHolder`.
4. Înlocuiește corpul: șterge cele două linii cu `randGol` și subclasa anonimă; scrie `View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.movie_item, parent, false);` și `return new MovieViewHolder(view);`.
5. Schimbă și semnătura lui `onBindViewHolder` să primească `MovieViewHolder`.
6. Adaugă `import android.view.LayoutInflater;`.
7. `Build → Make Project`. `BUILD SUCCESSFUL`. Pe ecran: neschimbat — adapterul nu e încă atașat la `RecyclerView`.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 4</summary>

al treilea argument al lui `inflate` trebuie să fie `false`. Cu `true`, `inflate` atașează imediat rândul la `parent`, iar `RecyclerView` aruncă `IllegalStateException` pentru că el însuși vrea să controleze atașarea. `false` înseamnă „construiește-l, dar lasă-mă pe mine să-l pun".

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 5</summary>

dacă ai schimbat generic-ul dar ai uitat semnăturile, primești `name clash: onBindViewHolder(RecyclerView.ViewHolder,int) and onBindViewHolder(MovieViewHolder,int) have the same erasure`. Nu e o eroare de sintaxă — e semnul că ai amestecat vechiul tip cu noul. Schimbă ambele semnături în același pas.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** adapterul știe acum să construiască un rând real, din `movie_item.xml`. Încă nu știe să-l umple cu date.

**Cod:** `MovieAdapter.java` — declarația și cele două metode:

```java
public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    private final List<Movie> movies;

    public MovieAdapter(List<Movie> movies) {
        this.movies = movies;
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
        // 23.6
    }

    @Override
    public int getItemCount() {
        return movies.size();
    }

    // ... MovieViewHolder din 23.4 ...
}
```

Import nou:

```java
import android.view.LayoutInflater;
```

**De ce:**
- `LayoutInflater.from(parent.getContext())` — `inflate` are nevoie de un `Context`, iar `ViewHolder`-ul nu are unul. `parent` (RecyclerView-ul) îl are, prin `getContext()`.
- `parent` la `inflate` nu e decorativ: îi dă inflater-ului `LayoutParams`-ul corect al părintelui. Fără el, cardul cu `layout_width="match_parent"` ar primi parametri impliciți și ar ieși îngust.
- `false` la `attachToRoot` — `RecyclerView` își atașează singur rândurile, la momentul lui. Dacă `inflate` le-ar atașa, ai avea un rând în plus, nemanevat de `LayoutManager`.
- Parametrul generic face `onBindViewHolder` type-safe: `holder` e `MovieViewHolder`, deci ai acces direct la `movieTitle` fără cast.

**De reținut:**
- `onCreateViewHolder` rulează **o dată per rând creat**, nu o dată per element din listă. `RecyclerView` creează doar câte rânduri încap pe ecran plus o rezervă, apoi le refolosește. La 3 filme vezi 3 rânduri; la 300 tot atâtea câte încap.
- `viewType` e parametrul care permite rânduri de tipuri diferite în aceeași listă. Aici e ignorat, pentru că avem un singur tip de rând.
- `@NonNull` pe `parent` și pe return: `RecyclerView` nu tolerează nici `parent` null, nici `ViewHolder` null.

**De reținut — verificare vizuală înainte de termen:** dacă vrei să vezi cardul acum, fără să aștepți 23.10, adaugă temporar în `MainActivity.initControls()`, după `findViewById`:

```java
recyclerView.setLayoutManager(new androidx.recyclerview.widget.LinearLayoutManager(this));
recyclerView.setAdapter(new ro.ase.ie.g1097.adapters.MovieAdapter(movies));
```

Rulează: vezi trei carduri goale (fără text, pentru că `bind` nu există încă). **Șterge cele două linii imediat** — la 23.10 le scriem corect, cu listener. Nu lăsa varianta temporară în soluția de examen.

**Unde se aplică:** orice adapter cu un singur tip de rând. Șablonul `inflate(R.layout.item_x, parent, false)` + `new XViewHolder(view)` e identic pentru toate; se schimbă doar numele layout-ului și al clasei.

</details>

---

## Exercițiul 23.6 — `onBindViewHolder`: titlu și subtitlu (gen · an)

**Cerință:** umple rândul cu date. `movieTitle` primește titlul filmului, `movieSubtitle` primește `gen · an`, anul format cu `SimpleDateFormat`.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**Cum abordezi — pașii tăi:**
1. Deschide `MovieAdapter.java`.
2. Adaugă în `MovieAdapter`, lângă câmpul `movies`, un formator static: `private static final SimpleDateFormat YEAR_FORMAT = new SimpleDateFormat("yyyy", Locale.getDefault());`.
3. Adaugă importurile `java.text.SimpleDateFormat` și `java.util.Locale`.
4. În `MovieViewHolder`, adaugă metoda `public void bind(Movie movie)`, cu `movieTitle.setText(movie.getTitle());` pe prima linie.
5. Sub ea, formatează anul: `String year = movie.getRelease() != null ? YEAR_FORMAT.format(movie.getRelease()) : "";`.
6. Adaugă `movieSubtitle.setText(movie.getGenre() + " · " + year);`. Atenție: separatorul e `·` (U+00B7), cu spații în jur, exact ca în comentariul din `movie_item.xml`.
7. În `onBindViewHolder`, înlocuiește comentariul cu `holder.bind(movies.get(position));`.
8. `Build → Make Project`. `BUILD SUCCESSFUL`. Pe ecran: neschimbat (sau, dacă ai lăsat verificarea temporară din 23.5, cardurile au acum titlu și subtitlu).

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 2</summary>

`SimpleDateFormat` se creează **o dată**, ca `static final`, nu în `bind`. Dacă îl creezi în `bind`, construiești un obiect nou la fiecare afișare a fiecărui rând — exact munca pe care `ViewHolder`-ul o evită. Pattern-ul `"yyyy"` dă anul cu patru cifre; `"yy"` ar da `10` în loc de `2010`.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 6</summary>

separatorul nu e `-` și nu e `|`. E `·` (middle dot), caracterul din comentariul `<!-- genre · release year, e.g. "Sci-Fi · 2021" -->`. Dacă îl scrii din tastatură greșit, se vede în listă ca un pătrat. Copiază-l din comentariul din XML.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** rândul are acum text. `bind` e metoda care traduce un `Movie` în widget-uri; restul pașilor doar o completează.

**Cod:** `MovieAdapter.java` — câmpul nou, importurile și metoda `bind`:

```java
import java.text.SimpleDateFormat;
import java.util.Locale;

public class MovieAdapter extends RecyclerView.Adapter<MovieAdapter.MovieViewHolder> {

    private static final SimpleDateFormat YEAR_FORMAT =
            new SimpleDateFormat("yyyy", Locale.getDefault());

    private final List<Movie> movies;

    // ... constructor, onCreateViewHolder ...

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position));
    }

    // ... getItemCount ...

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

        // ... câmpurile și constructorul din 23.4 ...

        public void bind(Movie movie) {
            movieTitle.setText(movie.getTitle());

            String year = movie.getRelease() != null
                    ? YEAR_FORMAT.format(movie.getRelease())
                    : "";
            movieSubtitle.setText(movie.getGenre() + " · " + year);
        }
    }
}
```

**De ce:**
- `bind` primește `Movie`, nu poziția: `ViewHolder`-ul nu trebuie să știe unde stă în listă. Poziția e treaba adapterului, obiectul e treaba rândului.
- `YEAR_FORMAT` e `static final` în clasa exterioară, nu în `ViewHolder`. E un singur obiect pentru toate rândurile, iar clasa interioară statică are acces la câmpurile statice private ale clasei care o conține.
- Verificarea `movie.getRelease() != null` e defensivă: modelul are constructor fără argumente și setter, deci un `Movie` poate exista cu `release` null. `YEAR_FORMAT.format(null)` ar arunca `NullPointerException` chiar în timpul derulării.
- `Locale.getDefault()` la formator: pentru `"yyyy"` nu schimbă cifrele la noi, dar e forma corectă. Un formator fără `Locale` explicit e semnalat de lint.

**De reținut:**
- `SimpleDateFormat` **nu e thread-safe**. Aici e folosit doar pe UI thread, deci e în regulă. Dacă adapterul ar rula și din alt thread, ai avea nevoie de un formator per thread sau de `java.time` (`DateTimeFormatter`, care e imutabil).
- `bind` se apelează la **fiecare** afișare, nu o dată per rând. Un rând reciclat primește alt film, deci `bind` trebuie să suprascrie **toate** câmpurile, nu doar pe cele care se schimbă. Regula asta devine critică la chips-uri (23.8).
- `movie.getRelease()` e `Date`, nu `String`. Nu ai nevoie de `toString()` — formatorul îl acceptă direct.

**Unde se aplică:** orice câmp text derivat din model. Dacă valoarea se calculează (an din dată, preț formatat, plural), calculul stă în `bind`, nu în model — modelul rămâne date pure.

</details>

---

## Exercițiul 23.7 — Rating: `movieRating` + `movieRatingValue`

**Cerință:** leagă rating-ul. `movieRating` (RatingBar) primește valoarea ca stele, `movieRatingValue` (TextView) primește valoarea scrisă cu un decimal.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**Cum abordezi — pașii tăi:**
1. Deschide `MovieAdapter.java` și găsește metoda `bind` din `MovieViewHolder`.
2. Adaugă `movieRating.setRating(movie.getRating());` după linia subtitlului.
3. Adaugă `movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));`.
4. Verifică în `movie_item.xml` că `movieRating` are `android:stepSize="0.5"` și `android:isIndicator="true"` — altfel `setRating(4.5f)` ar rotunji la 4 sau 5 stele.
5. `Build → Make Project`. `BUILD SUCCESSFUL`. Pe ecran: neschimbat (sau, cu verificarea temporară, stelele apar pe card).

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 3</summary>

`String.valueOf(movie.getRating())` ar merge și el, dar dă `4.5` pentru 4.5f și `4.0` pentru 4f — acceptabil. `String.format` îți dă control exact pe numărul de zecimale, ceea ce contează dacă rating-ul vine cu mai multe. Nu folosi `String.format` fără `Locale`: pe un telefon configurat în română ai primi `4,5`, iar designul cardului are `4.5`.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 4</summary>

dacă stelele arată toate pline sau toate goale, nu e de la cod — e de la `stepSize`. Cu `stepSize="1"`, `setRating(4.5f)` afișează 4 sau 5 stele, după cum rotunjește intern. `stepSize="0.5"` permite jumătăți de stea.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat două linii în `bind`. RatingBar-ul primește `float`, TextView-ul primește text formatat.

**Cod:** în `MovieViewHolder.bind(Movie movie)`, după linia subtitlului:

```java
movieRating.setRating(movie.getRating());
movieRatingValue.setText(String.format(Locale.US, "%.1f", movie.getRating()));
```

**De ce:**
- `RatingBar.setRating(float)` așteaptă exact tipul din model (`float rating`). Nu ai nevoie de cast.
- `%.1f` = un decimal, rotunjit. `4.5f` → `4.5`, `4f` → `4.0`, `5f` → `5.0`. Consecvent pe toate cardurile.
- `Locale.US` fixează separatorul zecimal la punct, indiferent de limba telefonului. E o alegere de design: cardul are `android:text="4.5"` ca exemplu, deci punctul e convenția vizuală a ecranului.
- `isIndicator="true"` din XML face stelele neinteractive. Fără el, utilizatorul ar putea modifica rating-ul direct în listă, iar valoarea s-ar pierde la reciclare.

**De reținut:**
- `RatingBar` e o subclasă de `ProgressBar`; `setRating` e metoda lui, nu `setProgress`. `setProgress` ar merge și ea (scara e 0..numStars*100 intern), dar e greșit semantic.
- Cele două view-uri sunt legate separat intenționat: bara e vizuală, textul e precis. Dacă ai lega doar bara, un rating de 4.3 ar arăta identic cu 4.5.
- `movieRatingValue` are `android:text="4.5"` în XML ca text de design. Dacă `bind` nu îl suprascrie, toate cardurile ar arăta `4.5` — exact genul de bug care trece neobservat la prima vedere.

**Unde se aplică:** orice pereche valoare-vizual + valoare-text. La fel se leagă `SeekBar` + `TextView` cu durata în `ItemActivity` (`tvDurationValue`), doar că acolo valoarea vine din control, nu din model.

</details>

---

## Exercițiul 23.8 — `movieFacts` și chips-urile cu `setVisibility`

**Cerință:** leagă linia de facts (durată + buget formatat ca `$160M`) și cele trei chips-uri de status. Fiecare chip apare doar dacă filmul are proprietatea respectivă, și **dispare** dacă nu o are.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**Cum abordezi — pașii tăi:**
1. Deschide `MovieAdapter.java`, metoda `bind`.
2. Adaugă `movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM", movie.getDuration(), movie.getBudget() / 1_000_000));`.
3. Pentru `chipApproval`: ia `String approval = movie.getApproval();`. Dacă e nenul și nevide, `chipApproval.setText(approval);` și `setVisibility(View.VISIBLE);`. Altfel doar `setVisibility(View.GONE);`.
4. Pentru `chipWatched`: `chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);`.
5. Pentru `chipWatchlist`: `chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);`.
6. Verifică importul `android.view.View` — e deja acolo din 23.3.
7. `Build → Make Project`. `BUILD SUCCESSFUL`. Pe ecran: neschimbat (sau, cu verificarea temporară, cardurile sunt complete).

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 3</summary>

`View.GONE`, nu `View.INVISIBLE`. `INVISIBLE` ascunde view-ul dar îi păstrează spațiul, deci cardul rămâne cu o dungă goală sub facts. `GONE` îl scoate din layout complet, iar `ChipGroup` rearanjează chips-urile rămase.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la formatarea bugetului</summary>

`movie.getBudget()` e `double` în unități întregi (`160000000`), nu în milioane. Împarți la `1_000_000` ca să ajungi la `160`, apoi formatezi cu `%.0f` ca să tai zecimalele. Dacă uiți împărțirea, obții `$160000000M`.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** am adăugat linia de facts și cele trei chips-uri, fiecare cu ambele ramuri — vizibil **și** ascuns.

**Cod:** în `MovieViewHolder.bind(Movie movie)`, după liniile de rating:

```java
movieFacts.setText(String.format(Locale.US, "%d min  ·  $%.0fM",
        movie.getDuration(), movie.getBudget() / 1_000_000));

String approval = movie.getApproval();
if (approval != null && !approval.isEmpty()) {
    chipApproval.setText(approval);
    chipApproval.setVisibility(View.VISIBLE);
} else {
    chipApproval.setVisibility(View.GONE);
}
chipWatched.setVisibility(movie.isWatched() ? View.VISIBLE : View.GONE);
chipWatchlist.setVisibility(movie.isOnWatchlist() ? View.VISIBLE : View.GONE);
```

**De ce:**
- `%d min  ·  $%.0fM` — `%d` pentru `int duration`, `%.0f` pentru `double budget / 1_000_000`. Două spații în jurul lui `·`, ca să corespundă cu `android:text="142 min  ·  $160M"` din XML.
- `Locale.US` la buget: dacă ai folosi `Locale.getDefault()` într-o limbă care grupează miile, ai putea primi separatori nedoriți. Aici `%.0f` nu grupează, dar fixarea locale-ului e obiceiul corect pentru valori afișate cu simbol valutar.
- `chipApproval` are nevoie de **text** pe lângă vizibilitate: XML-ul are `android:text="Approved"` ca text de design, iar valoarea reală vine din `movie.getApproval()` (`"PG-13"`, `"G"`, `"R"`).
- Cele trei chips-uri sunt independente: un film poate fi și aprobat, și urmărit, și pe watchlist.

**De reținut:**
- **Capcana reciclării:** fiecare chip trebuie să primească **ambele** ramuri, `VISIBLE` și `GONE`. Dacă scrii doar `if (movie.isWatched()) chipWatched.setVisibility(View.VISIBLE);` fără `else`, un rând reciclat care a fost „Watched" rămâne cu chip-ul aprins și pentru următorul film. E bug-ul clasic al `RecyclerView`-ului și singurul loc din exercițiile astea unde nu se vede în cod că lipsește ceva.
- `View.INVISIBLE` vs `View.GONE`: primul păstrează spațiul, al doilea îl eliberează. Pentru chips-uri vrei `GONE`.
- `movieStatusGroup` nu se atinge. `ChipGroup` își recalculează singur aranjarea când un copil devine `GONE`.

**Unde se aplică:** orice element condiționat într-un rând de `RecyclerView` — badge-uri, iconițe de status, butoane care apar doar pentru anumite elemente. Regula e mereu aceeași: `if` cu ambele ramuri, niciodată doar ramura „arată".

</details>

---

## Exercițiul 23.9 — Click pe rând cu `getBindingAdapterPosition()` și callback

**Cerință:** fă rândul click-abil. Adapterul primește în constructor un listener; la click, îl apelează cu poziția **curentă** a rândului, nu cu cea de la creare. `MainActivity` nu se atinge încă.

**Fișiere atinse:** `java/ro/ase/ie/g1097/adapters/MovieAdapter.java`

**Cum abordezi — pașii tăi:**
1. Deschide `MovieAdapter.java`.
2. Declară interfața în interiorul lui `MovieAdapter`, sus, înainte de câmpuri: `public interface OnItemClickListener { void onItemClick(int position); }`.
3. Adaugă câmpul `private final OnItemClickListener listener;`.
4. Schimbă constructorul: `public MovieAdapter(List<Movie> movies, OnItemClickListener listener)`, cu `this.listener = listener;`.
5. Schimbă `onBindViewHolder` să apeleze `holder.bind(movies.get(position), listener);`.
6. Schimbă semnătura lui `bind` în `public void bind(Movie movie, OnItemClickListener listener)`.
7. La finalul lui `bind`, adaugă blocul de click pe `itemView`, cu verificarea `getBindingAdapterPosition() != RecyclerView.NO_POSITION`.
8. `Build → Make Project`. `BUILD SUCCESSFUL`. Pe ecran: neschimbat — `MainActivity` încă nu construiește `MovieAdapter`, deci schimbarea de constructor nu strică nimic.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 7</summary>

listener-ul se leagă în `bind`, **nu** în constructorul `ViewHolder`. În constructor, `getBindingAdapterPosition()` ar fi evaluat o singură dată, la crearea rândului, și ar rămâne în urmă la reciclare — ai deschide filmul greșit după prima derulare.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la verificarea poziției</summary>

`getBindingAdapterPosition()` poate întoarce `RecyclerView.NO_POSITION` (adică `-1`) când rândul e în curs de scoatere sau în timpul unei animații. Fără `if`, ajungi la `movies.get(-1)` și primești `IndexOutOfBoundsException`. Verifică **și** listener-ul null, dacă permiți construirea adapterului fără el.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** adapterul are acum un canal de comunicare către activitate. Nu cunoaște `MainActivity`, `Intent` sau `ItemActivity` — doar o interfață cu o metodă.

**Cod:** `MovieAdapter.java` — părțile atinse:

```java
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

    @Override
    public void onBindViewHolder(@NonNull MovieViewHolder holder, int position) {
        holder.bind(movies.get(position), listener);
    }

    // ... onCreateViewHolder, getItemCount ...

    public static class MovieViewHolder extends RecyclerView.ViewHolder {

        // ... câmpurile și constructorul ...

        public void bind(Movie movie, OnItemClickListener listener) {
            // ... liniile din 23.6, 23.7, 23.8 ...

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

**De ce:**
- `RecyclerView` **nu are** `setOnItemClickListener`. E o decizie de design: un rând poate avea mai multe zone click-abile, iar un listener global ar fi ambiguu. Soluția e interfața proprie.
- `itemView` e câmpul public al lui `ViewHolder` care ține rădăcina rândului — aici `MaterialCardView`-ul din `movie_item.xml`. Click-ul pe orice punct al cardului declanșează listener-ul.
- `getBindingAdapterPosition()` se evaluează **la momentul click-ului**, nu la `bind`. De aceea e corectă chiar și după inserări, ștergeri sau reciclări.
- Interfața e declarată în adapter, nu în `MainActivity`: adapterul își definește contractul, activitatea îl implementează. Invers ar însemna ca adapterul să depindă de activitate.

**De reținut:**
- `getBindingAdapterPosition()` e varianta modernă a lui `getAdapterPosition()` (depreciat). Diferența: cea nouă ține cont de `ConcatAdapter` și de poziția în adapterul care a produs rândul.
- `NO_POSITION` e constanta `-1`. Verificarea nu e decorativă — fără ea, un click în timpul unei animații de inserare crapă aplicația.
- Lambda `v -> { ... }` implementează `View.OnClickListener`. Echivalentul lung e `new View.OnClickListener() { public void onClick(View v) { ... } }`.
- Listener-ul se poate transmite și ca metodă-referință din activitate (`this::openItem`), dar numai după 23.10, când activitatea construiește adapterul.

**Unde se aplică:** orice eveniment dintr-un rând de listă — click, click lung, click pe un chip, click pe poster. Toate se leagă în `bind`, toate folosesc `getBindingAdapterPosition()`, toate verifică `NO_POSITION`.

</details>

---

## Exercițiul 23.10 — `MainActivity`: `LayoutManager`, `setAdapter`, `notifyItem*`

**Cerință:** leagă adapterul de `RecyclerView`, șterge tot ce ținea de `ListView` și `ArrayAdapter`, mută click-ul în callback-ul adapterului și înlocuiește `notifyDataSetChanged()` cu `notifyItemInserted` / `notifyItemChanged`.

**Fișiere atinse:** `java/ro/ase/ie/g1097/activities/MainActivity.java`

**Cum abordezi — pașii tăi:**
1. Deschide `MainActivity.java`. Șterge `import android.widget.ArrayAdapter;`.
2. Adaugă importurile `androidx.recyclerview.widget.LinearLayoutManager`, `androidx.recyclerview.widget.RecyclerView` (dacă lipsește) și `ro.ase.ie.g1097.adapters.MovieAdapter`.
3. Schimbă câmpul `private ArrayAdapter<Movie> movieAdapter;` în `private MovieAdapter movieAdapter;`.
4. În `onCreate`, înlocuiește `movieAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies);` cu `movieAdapter = new MovieAdapter(movies, this::openItem);`.
5. În `initControls()`, după `recyclerView = findViewById(R.id.recyclerView);`, adaugă `recyclerView.setLayoutManager(new LinearLayoutManager(this));` și `recyclerView.setAdapter(movieAdapter);`.
6. În callback-ul lui `launcher`: `movieAdapter.notifyDataSetChanged();` din ramura de inserare devine `movieAdapter.notifyItemInserted(movies.size() - 1);`; cel din ramura de editare devine `movieAdapter.notifyItemChanged(position);`.
7. Adaugă metoda `private void openItem(int position)` care construiește `Intent`-ul către `ItemActivity` cu `MOVIE_EXTRA` și `POSITION_EXTRA` și apelează `launcher.launch(intent);`.
8. Rulează. Trebuie să vezi trei carduri: **Inception** (Sci-Fi · 2010, 4.5, `148 min · $160M`, chips PG-13 + Watched), **Toy Story** (Animation · 1995, 4.0, `81 min · $30M`, chips G + Watched), **The Matrix** (Action · 1999, 5.0, `136 min · $63M`, chips R + Watchlist). Click pe un card → formularul se deschide completat. Salvează modificări → rândul se actualizează cu animație. FAB → formular gol → salvează → rând nou apare în listă cu animație.

<details markdown="1">
<summary>Indiciu 1 — dacă te blochezi la pasul 8 și lista e goală, fără nicio eroare în Logcat</summary>

ai uitat `setLayoutManager`. E singura greșeală din tot capitolul care nu se plânge deloc: `RecyclerView` fără `LayoutManager` nu știe cum să aranjeze rândurile și nu afișează nimic, fără excepție, fără warning.

</details>

<details markdown="1">
<summary>Indiciu 2 — dacă te blochezi la pasul 6</summary>

`notifyItemInserted` cere **indexul elementului nou**, nu dimensiunea listei. După `movies.add(movie)`, elementul nou e la `movies.size() - 1`. Dacă scrii `notifyItemInserted(movies.size())`, primești `IndexOutOfBoundsException: Inconsistency detected. Invalid item position ... itemCount is ...`.

</details>

<details>
<summary>Soluție — explicativ</summary>

**Ce s-a făcut:** activitatea nu mai știe ce e `ListView` sau `ArrayAdapter`. Are un `RecyclerView`, un `MovieAdapter` construit cu un callback, un `LayoutManager` și notificări fine.

**Cod:** `MainActivity.java` — fișierul complet după migrare:

```java
package ro.ase.ie.g1097.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.List;

import ro.ase.ie.g1097.adapters.MovieAdapter;
import ro.ase.ie.g1097.model.Movie;
import ro.ase.ie.g1097.R;

public class MainActivity extends AppCompatActivity {

    protected static final String POSITION_EXTRA = "position";
    protected static final String MOVIE_EXTRA = "movie";
    private FloatingActionButton fabInsert;
    private RecyclerView recyclerView;
    private ActivityResultLauncher<Intent> launcher;
    private final List<Movie> movies = new ArrayList<>();
    private MovieAdapter movieAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        addSampleMovies();

        movieAdapter = new MovieAdapter(movies, this::openItem);
        initControls();
        initListeners();

        launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult o) {
                        if (o.getResultCode() == RESULT_OK) {
                            Intent intent = o.getData();
                            Movie movie = (Movie) intent.getSerializableExtra(MOVIE_EXTRA);
                            int position = intent.getIntExtra(POSITION_EXTRA, -1);
                            if (position == -1) {
                                movies.add(movie);
                                movieAdapter.notifyItemInserted(movies.size() - 1);
                            } else {
                                movies.set(position, movie);
                                movieAdapter.notifyItemChanged(position);
                            }
                        }
                    }
                });
    }

    private void openItem(int position) {
        Intent intent = new Intent(MainActivity.this, ItemActivity.class);
        intent.putExtra(MOVIE_EXTRA, movies.get(position));
        intent.putExtra(POSITION_EXTRA, position);
        launcher.launch(intent);
    }

    private void initListeners() {
        fabInsert.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, ItemActivity.class);
                launcher.launch(intent);
            }
        });
    }

    private void initControls() {
        fabInsert = findViewById(R.id.floatingActionButton);
        recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(movieAdapter);
    }

    private void addSampleMovies() {
        // neschimbat față de d719ffc — cele trei filme de probă
        movies.add(new Movie(
                "Inception",
                new GregorianCalendar(2010, Calendar.JULY, 16).getTime(),
                "Sci-Fi",
                160000000,
                148,
                4.5f,
                true,
                "PG-13",
                false,
                "https://example.com/posters/inception.jpg"));

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
}
```

**De ce:**
- `setLayoutManager(new LinearLayoutManager(this))` — `RecyclerView` nu știe să aranjeze nimic singur. `LinearLayoutManager` = listă verticală, echivalentul vizual al lui `ListView`. Pentru grilă ai pune `GridLayoutManager(this, 2)`.
- `this::openItem` e o metodă-referință care implementează `MovieAdapter.OnItemClickListener`. Echivalentul lung: `new MovieAdapter.OnItemClickListener() { public void onItemClick(int position) { openItem(position); } }`.
- `openItem` poate folosi `launcher` deși e declarat mai jos în `onCreate`: metoda rulează la click, mult după ce `onCreate` s-a terminat. Aceeași logică era și în varianta cu `ListView`.
- `notifyItemInserted(movies.size() - 1)` — după `add`, ultimul index e `size() - 1`. `RecyclerView` animează doar rândul nou, nu reconstruiește lista.
- `notifyItemChanged(position)` — un singur rând se rebindează, cu animație de tranziție. `movies.set(...)` se face **înainte** de notificare.

**De reținut:**
- Ordinea „mută, apoi notifică" nu e stilistică. `notifyItemInserted` înainte de `add` face `RecyclerView` să valideze un număr de elemente care nu corespunde și aruncă `Inconsistency detected`.
- `notifyDataSetChanged()` ar funcționa și el, dar reconstruiește tot și anulează animațiile. La examen, dacă cerința spune „animați inserarea", răspunsul e `notifyItemInserted`.
- `ArrayAdapter` dispare complet din activitate: câmp, construire, import. Nu mai există `android.R.layout.simple_list_item_1` nicăieri — rândul e `movie_item.xml`, prin `MovieAdapter`.
- Ordinea `movieAdapter = ...` **înainte** de `initControls()` contează: `initControls` cheamă `setAdapter(movieAdapter)`, deci câmpul trebuie să fie deja construit.

**Verificare finală — ce trebuie să vezi pe ecran:**

| Film | Subtitlu | Rating | Facts | Chips-uri |
|---|---|---|---|---|
| Inception | Sci-Fi · 2010 | 4.5 | 148 min · $160M | PG-13, Watched |
| Toy Story | Animation · 1995 | 4.0 | 81 min · $30M | G, Watched |
| The Matrix | Action · 1999 | 5.0 | 136 min · $63M | R, Watchlist |

Plus: click pe card → formularul se deschide cu datele filmului și butonul scrie „Update Movie"; salvare → rândul se schimbă cu animație; FAB → formular gol → salvare → rând nou la finalul listei, cu animație de inserare.

**Unde se aplică:** orice listă dintr-o aplicație Android modernă. Șablonul `setLayoutManager` + `setAdapter` + notificări fine e identic pentru orice model; se schimbă doar adapterul și layout-ul rândului. Dacă examenul cere și `ItemTouchHelper` (swipe-to-delete), el se atașează exact pe `recyclerView`, după `setAdapter`.

</details>

---

## Recapitulare — ce s-a atins, în ordine

| Pas | Fișier | Ce s-a adăugat | Compilează | Se vede pe ecran |
|---|---|---|---|---|
| 23.1 | `libs.versions.toml`, `build.gradle.kts` | dependența `recyclerview` | da | nimic |
| 23.2 | `activity_main.xml`, `MainActivity` | widget-ul + tipul câmpului | da | ecran gol + FAB |
| 23.3 | `MovieAdapter.java` (nou) | clasa + 3 metode | da | nimic |
| 23.4 | `MovieAdapter.java` | `MovieViewHolder` + `findViewById` | da | nimic |
| 23.5 | `MovieAdapter.java` | `inflate(movie_item)` | da | nimic |
| 23.6 | `MovieAdapter.java` | titlu + subtitlu | da | nimic |
| 23.7 | `MovieAdapter.java` | rating + valoare | da | nimic |
| 23.8 | `MovieAdapter.java` | facts + 3 chips-uri | da | nimic |
| 23.9 | `MovieAdapter.java` | interfața de click | da | nimic |
| 23.10 | `MainActivity.java` | `LayoutManager` + `setAdapter` + `notifyItem*` | da | **lista completă** |

**Trei greșeli care costă puncte la examen:**
1. `RecyclerView` fără `setLayoutManager` — listă goală, zero erori. Nu ai cum să o depanezi din Logcat.
2. Chips-uri fără ramura `else` din `bind` — rândurile reciclate păstrează statusul filmului anterior.
3. `notifyItemInserted(movies.size())` în loc de `movies.size() - 1` — `Inconsistency detected`, doar când inserezi, nu la pornire.
