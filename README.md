# RemoteDesk PRO — publiczny kanał aktualizacji OTA

Repozytorium służy wyłącznie do dystrybucji **jawnie zatwierdzonych** wydań
RemoteDesk PRO dla Androida i Windows. Kod źródłowy, certyfikat prywatny i
sekrety pozostają w osobnym, prywatnym repozytorium `pixii69-ui/remotedesk-pro`.

## Status

**Kanał OTA jeszcze nieaktywny**: brak publicznego Release i brak `version.json`.
To zamierzone; zainstalowana aplikacja 0.3.1+4 nie ma na razie nowszego wydania.

- APK 0.3.1+4 podpisane stałym kluczem: PASS, test instalacji/uruchomienia
  na telefonie: PASS.
- Docelowy pakiet Android: `pl.remotedesk.remotedesk_pro`.
- Pierwsza prawdziwa aktualizacja OTA: **minimum 0.3.2+5**.
- Windows sprawdza i pobiera ZIP z SHA-256, ale **nie aktualizuje EXE automatycznie**.

## Proces pierwszego publicznego wydania

1. Przetestować podpisanego kandydata 0.3.2+5 z prywatnego workflow
   `prepare signed candidate (manual)`, Android oraz Windows. Nie usuwać
   istniejącej 0.3.1.
2. Właściciel osobno zatwierdza publiczną publikację obydwu paczek.
3. Utworzyć w tym repozytorium **publiczny Release** z tagiem `v0.3.2` i
   dokładnie dwoma plikami:
   `RemoteDeskPRO.apk` oraz `RemoteDeskPRO-Windows.zip`.
4. Po sprawdzeniu Release właściciel uruchamia **ręcznie** workflow
   `RemoteDesk PRO — activate owner-approved OTA (manual)`,
   podając `version=0.3.2`, `version_code=5`, notatki wydania
   i wybierając `I_APPROVE_PUBLIC_OTA`.
5. Workflow sprawdza opublikowany Release, **stały SHA-256 certyfikatu
   podpisu Androida**, `applicationId`, `versionName`, `versionCode`,
   strukturę ZIP Windows, rzeczywiste SHA-256 obu plików i monotoniczny
   wzrost numeru wersji. Weryfikuje również pliki pobrane przez HTTPS.
6. Dopiero po PASS zapisuje **`version.json` na `main`**. Od tej chwili
   klienci starszej wersji wykryją aktualizację po kliknięciu przycisku
   `Sprawdź aktualizacje`.

Ważne: drugi workflow **nie tworzy Release** i sam nie publikuje plików
APK/ZIP. To osobna decyzja właściciela. Nie należy aktywować manifestu, jeśli
publikacja plików nie została już zatwierdzona.

## Adres manifestu

`https://raw.githubusercontent.com/pixii69-ui/remotedesk-pro-updates/main/version.json`

Brak tego pliku oznacza, że kanał jest nieaktywny.

## Bezpieczeństwo i ograniczenia

- Podpis Androida jest porównywany z publicznym odciskiem certyfikatu
  wygenerowanego w prywatnym workflow #3. **Nie ma tutaj klucza prywatnego.**
- Pobierane APK Androida wymaga tego samego identyfikatora i podpisu oraz
  wyższego `versionCode`. Instalację zatwierdza użytkownik w systemie.
- Windows ZIP nie jest podpisanym instalatorem Windows; jego wymiana
  nadal wymaga ręcznych czynności, dlatego nie nazywamy tego Windows OTA.
- SHA-256 sprawdza integralność względem manifestu; do ochrony przed
  kompromitacją konta GitHub można później dodać niezależny podpis manifestu.
- Nie publikować sekretów, kluczy, źródeł prywatnych ani debug APK.

Pełna lista kontrolna: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md).
