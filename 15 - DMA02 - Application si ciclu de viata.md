# Capitolul 15 — DMA02: clasa `Application` și ciclul de viață

**Obiectiv:** să înțelegi ciclul de viață al unei `Activity` (toate cele șapte metode), ce e clasa `Application`, cum funcționează `ActivityLifecycleCallbacks` și cum trimiți un `Intent` implicit.

**Timp estimat:** 40–50 min.

**Sursa:** `DMA02/` — primul commit din repo, `8b04238` (2026-10-13), 29 de fișiere.

> **De ce contează:** ciclul de viață e **cea mai frecventă întrebare de teorie** la examen. `G1097` folosește doar `onCreate`, dar trebuie să știi ce se întâmplă în restul și în ce ordine.

---

## Pasul 15.1 — Cele șapte metode ale ciclului de viață

### De ce

Android nu îți cheamă codul când vrea el. Îl cheamă în **momente bine definite**, iar tu suprascrii ce ai nevoie.

### Cum — lista completă

`DMA02/MainActivity` le suprascrie pe toate și scrie în Logcat:

```java
private static final String TAG = MainActivity.class.getSimpleName();

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    Log.w(TAG, "onCreate");
}

@Override
protected void onStart() {
    super.onStart();
    Log.w(TAG, "onStart");
}

@Override
protected void onResume() {
    super.onResume();
    Log.w(TAG, "onResume");
}

@Override
protected void onPause() {
    super.onPause();
    Log.w(TAG, "onPause");
}

@Override
protected void onStop() {
    super.onStop();
    Log.w(TAG, "onStop");
}

@Override
protected void onDestroy() {
    super.onDestroy();
    Log.w(TAG, "onDestroy");
}
```

### Ordinea și sensul

| Metodă | Când se apelează | Ce faci de obicei acolo |
|---|---|---|
| `onCreate()` | la creare, **o singură dată** per instanță | `setContentView`, `findViewById`, inițializări |
| `onStart()` | când devine vizibilă | înregistrare de listeneri de sistem |
| `onResume()` | când primește focus (poate primi input) | pornire animații, cameră, senzori |
| `onPause()` | când pierde focus (altă activitate vine deasupra) | oprire animații, salvare rapidă |
| `onStop()` | când nu mai e vizibilă | eliberare resurse grele |
| `onDestroy()` | când se distruge | anulare de callback-uri, eliberare |
| `onRestart()` | între `onStop` și `onStart`, la revenire | rar folosită |

### Ordinea la pornire și la închidere

```
PORNIRE:   onCreate → onStart → onResume
ÎNCHIDERE: onPause → onStop → onDestroy
```

### Ce se întâmplă la fiecare scenariu

| Scenariu | Metode apelate |
|---|---|
| Pornești aplicația | `onCreate` → `onStart` → `onResume` |
| Apeși Home | `onPause` → `onStop` |
| Revii din Home | `onRestart` → `onStart` → `onResume` |
| Altă activitate vine deasupra (dialog) | `onPause` (și `onStop` dacă acoperă tot) |
| Apeși Back | `onPause` → `onStop` → `onDestroy` |
| Rotești ecranul | `onPause` → `onStop` → `onDestroy` → `onCreate` → `onStart` → `onResume` |

> **Atenție la rotire:** activitatea e **distrusă și recreată**. De aceea câmpurile se pierd dacă nu le salvezi în `onSaveInstanceState`. Vezi capitolul 10, testul 13.

### De ce `Log.w` și nu `Log.d`

`Log.w` (warning) e vizibil implicit în Logcat fără să schimbi filtrul de nivel. `Log.d` (debug) poate fi ascuns. Pentru demonstrație, `w` e alegerea practică.

### Exercițiu 15.1

**Cerință:** fără să rulezi, scrie în ordine ce metode se apelează când: (a) pornești aplicația, (b) apeși Home, (c) revii, (d) apeși Back.

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai reconstruit secvențele din tabel.

**Răspunsul:**

| | Secvența |
|---|---|
| (a) pornire | `onCreate` → `onStart` → `onResume` |
| (b) Home | `onPause` → `onStop` |
| (c) revenire | `onRestart` → `onStart` → `onResume` |
| (d) Back | `onPause` → `onStop` → `onDestroy` |

**De ce (c) are `onRestart`:** activitatea nu a fost distrusă, doar oprită. `onRestart` marchează „revin dintr-o oprire", distinct de prima pornire.

**De reținut:**
1. `onCreate` rulează **o singură dată** per instanță. La rotire, e o instanță nouă, deci rulează din nou.
2. `onResume`/`onPause` sunt perechi; `onStart`/`onStop` sunt perechi.
3. `onDestroy` **nu** e garantat — dacă procesul e omorât de sistem, nu se apelează.

**Unde revine:** în capitolul 04, `MainActivity` are doar `onCreate`. Restul metodelor lipsesc pentru că nu ai nevoie de ele — dar ele **se apelează** oricum (versiunile din `AppCompatActivity`).

</details>

---

## Pasul 15.2 — Clasa `Application`

### De ce

`Application` e un obiect **unic per proces**, creat **înaintea oricărei activități**. E locul pentru inițializări globale: biblioteci, DI, logging, teme.

### Cum

`DMA02/DMA02App.java`:

```java
public class DMA02App
        extends Application
        implements Application.ActivityLifecycleCallbacks {

    private final String TAG = DMA02App.class.getSimpleName();

    @Override
    public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
        DynamicColors.applyToActivitiesIfAvailable(this);

        Log.w(TAG, "onCreate");
    }
    // ...
}
```

### Trei lucruri esențiale

1. **`extends Application`** — clasa ta devine obiectul global.
2. **`registerActivityLifecycleCallbacks(this)`** — te abonezi la ciclul de viață al **tuturor** activităților.
3. **`DynamicColors.applyToActivitiesIfAvailable(this)`** — activează Material You (culori extrase din wallpaper) pe Android 12+.

### De ce trebuie declarată în manifest

`AndroidManifest.xml`:

```xml
<application
    android:name=".DMA02App"
    ...>
```

Fără `android:name`, Android folosește `android.app.Application` implicit — și clasa ta nu e instanțiată niciodată.

> **Atenție:** numele complet e `.DMA02App` (cu punct la început), relativ la `namespace`. Dacă scrii doar `DMA02App`, manifestul nu găsește clasa.

### Când rulează `Application.onCreate`

**Înainte** de `Activity.onCreate`. Ordinea la pornirea aplicației:

```
Application.onCreate
  → Activity.onCreate
    → Activity.onStart
      → Activity.onResume
```

### Exercițiu 15.2

**Cerință:** ce se întâmplă dacă uiți `android:name=".DMA02App"` din manifest? Codul din `DMA02App` mai rulează?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai comparat manifestul cu și fără atribut.

**Răspunsul:** **nu.** Fără `android:name`, Android instanțiază `android.app.Application` — clasa ta nu e niciodată creată. `Log.w(TAG, "onCreate")` din `DMA02App` nu apare în Logcat. Nicio eroare, doar tăcere.

**De ce:** manifestul e singura sursă pentru „ce clasă de `Application` folosesc". Fără ea, se ia default-ul.

**De reținut:**
1. `android:name` în `<application>` = clasa ta de `Application`.
2. `android:name` în `<activity>` = clasa activității.
3. Ambele folosesc calea relativă la `namespace`, cu punct la început.

**Unde revine:** în capitolul 01, pasul 1.5 — același mecanism pentru `MainActivity`.

</details>

---

## Pasul 15.3 — `ActivityLifecycleCallbacks`

### De ce

Vrei să loghezi ciclul de viață al **tuturor** activităților dintr-un singur loc, fără să suprascrii metodele în fiecare.

### Cum

`DMA02App` implementează șapte metode:

```java
@Override
public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {
    Log.w(TAG, "onActivityCreated" + activity.getClass().getSimpleName());
}

@Override
public void onActivityStarted(@NonNull Activity activity) {
    Log.w(TAG, "onActivityStarted" + activity.getClass().getSimpleName());
}

@Override
public void onActivityResumed(@NonNull Activity activity) {
    Log.w(TAG, "onActivityResumed" + activity.getClass().getSimpleName());
}

@Override
public void onActivityPaused(@NonNull Activity activity) {
    Log.w(TAG, "onActivityPaused" + activity.getClass().getSimpleName());
}

@Override
public void onActivityStopped(@NonNull Activity activity) {
    Log.w(TAG, "onActivityStopped" + activity.getClass().getSimpleName());
}

@Override
public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {
}

@Override
public void onActivityDestroyed(@NonNull Activity activity) {
    Log.w(TAG, "onActivityDestroyed" + activity.getClass().getSimpleName());
}
```

### Corespondența cu metodele activității

| Metoda activității | Metoda callback-ului |
|---|---|
| `onCreate` | `onActivityCreated(activity, savedInstanceState)` |
| `onStart` | `onActivityStarted(activity)` |
| `onResume` | `onActivityResumed(activity)` |
| `onPause` | `onActivityPaused(activity)` |
| `onStop` | `onActivityStopped(activity)` |
| `onSaveInstanceState` | `onActivitySaveInstanceState(activity, bundle)` |
| `onDestroy` | `onActivityDestroyed(activity)` |

### Ordinea de apel

Callback-ul din `Application` primește evenimentul **înainte** ca metoda activității să ruleze. Deci în Logcat vezi:

```
DMA02App: onActivityCreatedMainActivity
MainActivity: onCreate
DMA02App: onActivityStartedMainActivity
MainActivity: onStart
...
```

> **De reținut:** `ActivityLifecycleCallbacks` e util pentru: logging centralizat, analytics („câte ecrane a văzut utilizatorul"), eliberare de resurse globale. Nu înlocuiește metodele activității — le **observă**.

### Exercițiu 15.3

**Cerință:** de ce `onActivitySaveInstanceState` are `Bundle` ca al doilea parametru, iar celelalte nu?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai comparat semnăturile.

**Răspunsul:** pentru că `Activity.onSaveInstanceState(Bundle outState)` are nevoie de `Bundle` ca să primească starea. Callback-ul primește **același** `Bundle`, ca să poată adăuga sau citi.

**De ce celelalte nu au:** `onStart`, `onResume` etc. nu au parametri — nu au nevoie de date.

**De reținut:**
1. `ActivityLifecycleCallbacks` s-a adăugat în API 14.
2. `onActivityCreated` primește `savedInstanceState` — util ca să știi dacă e recreare (rotire) sau pornire nouă.
3. `Bundle` e `null` la prima creare, non-null la recreare.

**Unde revine:** în capitolul 10, testul 13 (rotirea) — `savedInstanceState` e ce ți-ar fi trebuit ca să nu pierzi datele formularului.

</details>

---

## Pasul 15.4 — `DynamicColors` (Material You)

### De ce

De la Android 12, sistemul poate extrage o paletă de culori din wallpaper. `DynamicColors` activează asta pentru aplicația ta.

### Cum

```java
@Override
public void onCreate() {
    super.onCreate();
    registerActivityLifecycleCallbacks(this);
    DynamicColors.applyToActivitiesIfAvailable(this);
    // ...
}
```

### Ce face

Dacă rulezi pe Android 12+, tema Material 3 primește culorile dinamice. Pe versiuni mai vechi, apelul e ignorat — nicio eroare.

### De ce în `Application` și nu în fiecare activitate

`applyToActivitiesIfAvailable(this)` se aplică **tuturor** activităților create după acel moment. Un singur apel, o singură dată.

> **De reținut:** `DynamicColors` face parte din `com.google.android.material`. Nu ai nevoie de altă dependență — `libs.material` e deja acolo.

### Exercițiu 15.4

**Cerință:** ce se întâmplă dacă schimbi wallpaper-ul pe Android 12+ cu aplicația deschisă?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai testat comportamentul dinamic.

**Răspunsul:** culorile aplicației **se schimbă** după ce aplicația e recreată (sau repornită). Pe unele dispozitive se actualizează și live.

**De ce:** `DynamicColors` citește paleta la `Application.onCreate`. La schimbarea wallpaper-ului, sistemul poate recrea procesul.

**De reținut:**
1. `DynamicColors.applyToActivitiesIfAvailable(this)` — `this` e `Application`, nu `Activity`.
2. Pe Android < 12, apelul nu face nimic (grație `IfAvailable`).
3. Culorile tale explicite din `themes.xml` au prioritate.

**Unde revine:** în `G1097`, tema `Theme.Material3.DayNight.NoActionBar` suportă culori dinamice, dar aplicația **nu** apelează `DynamicColors` — deci folosește paleta fixă Material 3.

</details>

---

## Pasul 15.5 — `Intent` implicit

### De ce

Toate `Intent`-urile din `G1097` sunt **explicite** — spun exact ce clasă să pornească. Un `Intent` **implicit** spune doar *ce operație* vrei, iar sistemul alege aplicația.

### Cum

`MainActivity.pressMe(View)`:

```java
public void pressMe(View view) {
/*        Intent web = new Intent(Intent.ACTION_VIEW, Uri.parse("https://developer.android.com"));
    startActivity(web);*/

/*    Intent call = new Intent(Intent.ACTION_DIAL, Uri.parse("tel:0212345678"));
    startActivity(call);*/

    Intent share = new Intent(Intent.ACTION_SEND);
    share.setType("text/plain");
    share.putExtra(Intent.EXTRA_TEXT, "Hello!");
    startActivity(Intent.createChooser(share, "Share via DMA"));
}
```

### Cele trei acțiuni, comentate pe rând

| Acțiune | Ce deschide | De ce e comentată |
|---|---|---|
| `ACTION_VIEW` + `https://...` | browserul | demonstrativ |
| `ACTION_DIAL` + `tel:...` | tastatura telefonică | demonstrativ |
| `ACTION_SEND` + `text/plain` | **share sheet**-ul | **activă** |

### De ce `createChooser`

`ACTION_SEND` fără `createChooser` ar deschide aplicația implicită de share (sau ar arăta un dialog dacă nu există default). `createChooser(intent, title)` forțează **mereu** dialogul de alegere, cu titlul dat.

> **De reținut:** `createChooser` e util când vrei ca utilizatorul să aleagă explicit, nu să meargă pe default.

### `setType` e obligatoriu pentru `ACTION_SEND`

Fără `setType("text/plain")`, Android nu știe ce aplicații pot primi `Intent`-ul → `ActivityNotFoundException`.

### `G1097` are și un `intent-filter` de recepție

În `DMA02/AndroidManifest.xml` există:

```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <category android:name="android.intent.category.DEFAULT" />
</intent-filter>
```

Asta înseamnă că aplicația **apare în share sheet** — poți trimite text din altă aplicație către ea.

### Exercițiu 15.5

**Cerință:** de ce `new Intent(this, ItemActivity.class)` e explicit, iar `new Intent(Intent.ACTION_SEND)` e implicit?

<details>
<summary>Răspuns — explicativ</summary>

**Ce s-a făcut:** ai comparat cele două forme.

**Răspunsul:**
- **Explicit:** ai `ComponentName` — pachet + clasă. Sistemul știe exact ce să pornească. `new Intent(context, ItemActivity.class)`.
- **Implicit:** ai doar acțiune + date. Sistemul caută în toate aplicațiile instalate cea care declară un `intent-filter` potrivit.

**De ce contează:**
1. Explicit = **intern aplicației**, mereu aceeași clasă.
2. Implicit = **între aplicații**, poate fi orice app care acceptă.

**De reținut:**
1. `Intent(Context, Class)` → explicit.
2. `Intent(String action)` sau `Intent(String action, Uri)` → implicit.
3. Un `Intent` implicit poate eșua cu `ActivityNotFoundException` dacă nicio aplicație nu-l acceptă.

**Unde revine:** în capitolul 08, `launcher.launch(intent)` primește un `Intent` explicit — de aceea merge mereu.

</details>

---

## Pasul 15.6 — Verificare

### Cum

1. Deschide `DMA02` în Android Studio.
2. Rulează cu **Logcat** deschis, filtrat pe `package:mine`.
3. Vezi în ordine: `DMA02App: onCreate`, apoi `onActivityCreatedMainActivity`, apoi `MainActivity: onCreate`, etc.
4. Apasă Home, revino, apasă butonul. Urmărește secvențele.

### Ce verifici în cod

- [ ] `DMA02App extends Application implements Application.ActivityLifecycleCallbacks`
- [ ] manifestul are `android:name=".DMA02App"`
- [ ] `registerActivityLifecycleCallbacks(this)` în `Application.onCreate`
- [ ] toate cele 7 metode implementate
- [ ] `MainActivity` suprascrie toate cele 6 metode de ciclu de viață
- [ ] `pressMe` folosește `ACTION_SEND` + `createChooser`

---

## Rezumat capitol 15

- Ciclu de viață: `onCreate` → `onStart` → `onResume` → `onPause` → `onStop` → `onDestroy`, plus `onRestart`.
- Rotirea = `onDestroy` + `onCreate` → starea se pierde fără `onSaveInstanceState`.
- `Application` = obiect unic per proces, creat înaintea oricărei activități.
- Se declară în manifest cu `android:name=".ClasaMea"`.
- `ActivityLifecycleCallbacks` = observator central pentru toate activitățile.
- `DynamicColors` = Material You, doar Android 12+.
- `Intent` explicit = clasă exactă. `Intent` implicit = acțiune, sistemul alege.

**Următorul capitol:** [16 - Istoricul repo-ului.md](16%20-%20Istoricul%20repo-ului.md)
