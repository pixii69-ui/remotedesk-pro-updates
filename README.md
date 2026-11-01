# RemoteDesk PRO — publiczny kanał aktualizacji

To repozytorium służy **wyłącznie do dystrybucji zatwierdzonych wydań** aplikacji RemoteDesk PRO (Android i Windows).

- **Źródła aplikacji** pozostają prywatne w `pixii69-ui/remotedesk-pro`.
- Nie publikujemy tutaj kodu źródłowego, kluczy JKS, haseł, tokenów ani danych użytkowników.
- **Stan: kanał przygotowywany, jeszcze nieaktywny.** Nie ma podpisanego wydania produkcyjnego.

## Gdzie aplikacja będzie sprawdzać aktualizacje?

Po zatwierdzeniu pierwszego wydania w głównej gałęzi pojawi się plik `version.json`:

```text
https://raw.githubusercontent.com/pixii69-ui/remotedesk-pro-updates/main/version.json
```

**Celowo nie tworzymy jeszcze `version.json`**. Nie wolno kierować użytkowników do pobierania fikcyjnej, testowej lub niepodpisanej paczki.

## Procedura pierwszego wydania

1. Zatwierdzić i przetestować kod w prywatnym repozytorium.
2. Utworzyć **jeden stały klucz podpisu Android release**, zabezpieczyć kopię i skonfigurować sekrety GitHub Actions (nigdy nie commitować JKS).
3. Sprawdzić identyfikator pakietu Android, podpis, numer wersji i zachowanie danych przy instalacji aktualizacji.
4. Przygotować podpisany APK i kompletną paczkę Windows ZIP; sprawdzić je na rzeczywistych urządzeniach.
5. Po wyraźnej zgodzie właściciela opublikować paczki w GitHub **Releases** tego repozytorium.
6. Przygotować `version.json` z dokładnymi adresami i prawdziwymi sumami SHA-256 **już opublikowanych** paczek.
7. Zatwierdzić manifest dopiero po sprawdzeniu jego poprawności.

Szczegóły znajdują się w [liście kontrolnej wydania](docs/RELEASE_CHECKLIST.md). Przykładowy manifest jest w `docs/version.example.json` i **nie uruchamia kanału aktualizacji**.

## Ważne ograniczenia

- Aktualizacje Androida wymagają tego samego identyfikatora aplikacji i zgodnego certyfikatu podpisu oraz wyższego `versionCode`. Instalację zatwierdza użytkownik w systemie Android.
- Starsze debug APK mogą być podpisane innymi certyfikatami. Pierwsza migracja na stały podpis release może wymagać jednorazowej reinstalacji.
- Windows: aktualny plan to zweryfikowane pobranie archiwum ZIP i ręczna wymiana plików; automatyczny instalator Windows jeszcze nie istnieje.
- SHA-256 zabezpiecza integralność pobranego pliku względem manifestu, ale nie zastępuje zaufanego podpisu aplikacji ani zabezpieczeń samego manifestu.

**Żadna publikacja APK/ZIP bez wyraźnej zgody właściciela projektu.**
