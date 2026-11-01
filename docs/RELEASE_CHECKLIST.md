# RemoteDesk PRO — kontrola przed publicznym OTA

## Gotowe (1 listopada 2026)

- [x] Prywatne repo źródłowe i osobne publiczne repo aktualizacji.
- [x] Wygenerowany **jeden stały certyfikat Android** (bootstrap #3: PASS).
- [x] Właściciel pobrał zaszyfrowaną kopię zapasową, hasło zachowane osobno.
- [x] Stałe Android applicationId: `pl.remotedesk.remotedesk_pro`.
- [x] Podpisane APK 0.3.1+4: apksigner, aapt i kompilacja PASS.
- [x] Android 0.3.1: instalacja i uruchomienie na telefonie PASS.
- [x] Publiczny walidator manifestu oraz ręczny workflow aktywacji OTA.

## Pierwsza aktualizacja 0.3.1 → 0.3.2

- [x] Przygotować 0.3.2+5 i podpisać **tym samym** certyfikatem — PASS, workflow kandydata #2.
- [ ] Przetestować działanie Androida 0.3.2 oraz aktualizację 0.3.1 → 0.3.2
      bez usuwania aplikacji i danych.
- [ ] Sprawdzić ZIP i uruchamianie Windows na rzeczywistym komputerze.
- [x] Uzyskać **osobną, jednoznaczną zgodę właściciela** na publiczną
      publikację APK i ZIP.
- [x] Opublikować w tym repo GitHub Release `v0.3.2` z
      `RemoteDeskPRO.apk` oraz `RemoteDeskPRO-Windows.zip`.
- [x] Aktywować pierwszy publiczny manifest przez PR #2 (właściciel zatwierdził publikację); CI #5 sprawdził rzeczywiste publiczne pliki i ich SHA-256. Ręczny workflow aktywacyjny pozostaje dla kolejnych wydań.
- [x] Zweryfikować PASS oraz dostępność `version.json` w `main` — CI #5 i #6 PASS.
- [ ] Na zainstalowanej 0.3.1 sprawdzić wykrycie, pobranie, SHA-256,
      otwarcie instalatora i aktualizację za zgodą użytkownika.

## Mechanizm ochronny

- Workflow nie tworzy ani nie zmienia publicznego Release — wymaga
  jego wcześniejszego zatwierdzenia i opublikowania.
- Nie dopuszcza APK z obcym certyfikatem, innym package ID ani
  błędnym numerem wersji.
- Sprawdza, że nowe `version_code` oraz wersja semantyczna są wyższe
  od obecnego manifestu. Pierwsza aktywacja wymaga co najmniej 0.3.2+5.
- Waliduje SHA-256 rzeczywistych, publicznie pobieranych plików.
- Nie wpisywać haseł, tokenów ani prywatnych kluczy do GitHub Releases.

Windows: pobranie ZIP jest automatyzowane; wymiana aplikacji nadal ręczna.
