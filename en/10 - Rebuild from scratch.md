# Chapter 10 — Rebuild from Scratch

**Objective:** Recreate the entire `G1097` application **without the material**, in 90 minutes, with only the Android documentation open. This is the real test.

**Estimated time:** 90 min (first attempt), 45 min (second), 30 min (third).

---

## Drill rules

1. **Create a new project** from scratch. Do not copy files from `_progres/` or `cod-final/`.
2. **Do not open chapters 01–09.** If you get stuck, note where, keep going, and come back at the end.
3. You may open: the Android documentation, Stack Overflow, and `cod-final/` **only at the end**, for comparison.
4. Time yourself. Write down the time.
5. At the end, fill in the table below.

---

## Build order (without looking)

This is the order that works. Follow it and you won't get stuck.

### Phase 1 — skeleton (10 min)

1. New project, Empty Views Activity, Java, `minSdk 33`, package `ro.ase.ie.g1097`.
2. Move `MainActivity` to `ro.ase.ie.g1097.activities`.
3. `themes.xml`: `Theme.Material3.DayNight.NoActionBar`.
4. `strings.xml`: `app_name`, `items` (20), `movie_genre` (10).
5. `outline_add_24.xml` (Vector Asset → Add).
6. Run: “Hello World”.

### Phase 2 — model (10 min)

7. `ro.ase.ie.g1097.model.Movie` with 10 fields, `Serializable`.
8. Empty constructor + 10-parameter constructor.
9. Getters/setters (Alt+Insert).
10. `toString()` (Alt+Insert).

### Phase 3 — main screen (15 min)

11. `activity_main.xml`: `FrameLayout` + `ListView` + FAB.
12. `MainActivity`: fields, `onCreate`, `EdgeToEdge`, insets.
13. `addSampleMovies()` with 3 movies.
14. `ArrayAdapter` + `initControls`.
15. Run: 3 movies in the list.

### Phase 4 — form (25 min)

16. `activity_item.xml`: `ScrollView` + `LinearLayout` + 4 cards.
17. Card 1: Title, Genre, Release.
18. Card 2: Budget, Duration.
19. Card 3: Rating, Switch, CheckBox, RadioGroup.
20. Card 4: Poster.
21. Save button.
22. Run (temporarily use `setContentView(R.layout.activity_item)`).

### Phase 5 — `ItemActivity` (20 min)

23. New class + declare it in the manifest.
24. Fields + `onCreate` + insets.
25. `initControls` (13 `findViewById` calls).
26. `initListeners` (date, save, seekbar, switch).
27. `showReleaseDatePicker`.
28. `saveMovie`.
29. Run: the form opens, Save does not crash.

### Phase 6 — navigation (10 min)

30. `launcher` with `registerForActivityResult`.
31. Complete `initListeners` (FAB + item click).
32. `onActivityResult` with `add` / `set`.
33. Run: add a movie; it appears in the list.

### Phase 7 — editing (10 min)

34. `getIntent()` + `existing != null`.
35. `fillForm`.
36. `setTitle` + `setText` on the button.
37. Run: edit a movie; it updates.

---

## Timing table

| Attempt | Date | Total time | Where you got stuck | What you looked up |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Target:** under 45 min without major blockers.

---

## Final checklist (without looking at the code)

Check an item only if you wrote it yourself from memory.

### Structure
- [ ] Gradle project with `minSdk 33`, Java 11
- [ ] `MainActivity` and `ItemActivity` in `ro.ase.ie.g1097.activities`
- [ ] both declared in the manifest, `MainActivity` with `exported="true"`
- [ ] theme `Theme.Material3.DayNight.NoActionBar`

### Model
- [ ] `Movie implements Serializable`
- [ ] 10 fields with the correct types
- [ ] **explicit** empty constructor
- [ ] 10-parameter constructor
- [ ] `isWatched()` / `isOnWatchlist()`

### `activity_main.xml`
- [ ] `FrameLayout` with `id=main`
- [ ] `ListView` with `id=listView`
- [ ] FAB with `layout_gravity="bottom|end"`
- [ ] order: ListView, then FAB

### `MainActivity`
- [ ] `EdgeToEdge` + insets on `R.id.main`
- [ ] `addSampleMovies` with 3 movies
- [ ] `ArrayAdapter<>(this, android.R.layout.simple_list_item_1, movies)`
- [ ] `initControls` with `setAdapter`
- [ ] `launcher` with `StartActivityForResult`
- [ ] `onActivityResult`: `RESULT_OK` → `add` or `set` → `notifyDataSetChanged`
- [ ] `initListeners`: FAB + `setOnItemClickListener`

### `activity_item.xml`
- [ ] `ScrollView` with `id=main`, `fillViewport`
- [ ] 4 `MaterialCardView`
- [ ] `TextInputLayout` + `TextInputEditText` for Title, Release, Budget, Poster
- [ ] `Spinner` with `entries`
- [ ] `SeekBar` with `max=300`
- [ ] `RatingBar` with `numStars=5`, `stepSize=0.5`
- [ ] `MaterialSwitch` + `MaterialCheckBox`
- [ ] `RadioGroup` with 5 `MaterialRadioButton`
- [ ] `MaterialButton` with `id=btnMovieAction`

### `ItemActivity`
- [ ] 13 fields + `position = -1` + `releaseCal` + `dateFormat`
- [ ] `initControls`: 13 `findViewById` calls
- [ ] `initListeners`: `etRelease`, `btMovieAction`, `sbDuration`, `swWatched`
- [ ] `showReleaseDatePicker` with `DatePickerDialog`
- [ ] `saveMovie`: 10 setters + radio iteration + `setResult` + `finish`
- [ ] `getIntent()` + `fillForm` + `setTitle` + button

---

## Functional tests (on the emulator)

Run all of them. If one fails, you have a bug.

| # | Test | Expected result |
|---|---|---|
| 1 | Launch the app | 3 movies in the list |
| 2 | Tap the FAB | empty form, “Save Movie” button |
| 3 | Fill in the form + Save | 4 movies; the last one is the new movie |
| 4 | Press Back without saving | the list still has 3 movies |
| 5 | Tap a movie | populated form, “Update Movie” button |
| 6 | Change the title + Update | the list still has 3 movies; the title has changed |
| 7 | Tap Release | the calendar opens |
| 8 | Choose a date | the field updates to `dd/MM/yyyy` |
| 9 | Move the SeekBar | `tvDurationValue` updates |
| 10 | Toggle the switch | `tvWatchedValue` becomes “Yes” |
| 11 | Save with an empty budget | **crash** (known bug) |
| 12 | Edit a movie with a date | the date appears correctly |
| 13 | Rotate the screen | **the form is cleared** (state is lost) |

### About test 13

Rotating the screen **recreates** the activity (`onCreate` is called again). The fields are lost because you do not save the state in `onSaveInstanceState`.

This is a **known behavior** of the repo, not a bug to fix now. But you need to know why it happens — it's a classic test question.

---

## What to do if you get stuck

| Symptom | Likely cause | Check |
|---|---|---|
| `ClassNotFoundException` on launch | the activity is not in the manifest | `AndroidManifest.xml` |
| `NullPointerException` in `initControls` | `setContentView` is missing or comes later | the order in `onCreate` |
| The list is empty | `setAdapter` is missing | `initControls` |
| The movie does not appear after Save | `notifyDataSetChanged` is missing | `onActivityResult` |
| The form opens empty when editing | `getIntent` does not read the extra | the `MOVIE_EXTRA` key |
| `NumberFormatException` on Save | empty budget | `Double.parseDouble` |
| `NullPointerException` when editing | `release` is `null` | `fillForm` |
| The button does nothing | the listener is not attached | `initListeners` |
| The Spinner shows the wrong first option | the genre is not in the list | the loop in `fillForm` |

---

## After the drill

If you finished in under 45 min without opening the material: **you've mastered the app**. Move on to chapter 11.

If you got stuck: note it in the table, reread the relevant chapter, and repeat in 2 days.

---

**Next chapter:** [11 - Extensii.md](11%20-%20Extensii.md)
