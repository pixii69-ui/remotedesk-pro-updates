# RemoteDesk PRO — lista kontrolna pierwszego wydania

## Przed przygotowaniem paczek

- [ ] Kod klienta Android / Windows przeszedł testy Flutter i kontrolę wizualną.
- [ ] Publiczny kanał `pixii69-ui/remotedesk-pro-updates` jest oddzielony od prywatnego kodu.
- [ ] Sprawdzono i utrwalono **applicationId Androida** oraz numer `versionCode`; wersja jest wyższa od poprzedniej.
- [ ] Utworzono **jedyny, trwały klucz podpisu release dedykowany RemoteDesk PRO**.
- [ ] Kopia zapasowa klucza jest poza GitHubem, bezpieczna i możliwa do odzyskania.
- [ ] Sekrety `ANDROID_KEYSTORE_B64`, `ANDROID_STORE_PASSWORD`, `ANDROID_KEY_PASSWORD`, `ANDROID_KEY_ALIAS` ustawiono w **prywatnym** repozytorium źródłowym, nie tutaj.
- [ ] Sprawdzono, czy aktualizacja z tej samej serii podpisów zachowuje dane aplikacji.
- [ ] Zaplanowano migrację istniejących debug APK. Jeśli podpis jest niezgodny, nie obiecywać aktualizacji bez reinstalacji.

## Budowanie i weryfikacja

1. W prywatnym repo uruchomić ręcznie `RemoteDesk PRO — prepare signed candidate (manual)` dla wersji zgodnej z `pubspec.yaml`. Workflow nie publikuje wydania.
2. Pobrać i zainstalować podpisane APK na rzeczywistym telefonie/tablecie oraz sprawdzić certyfikat podpisu i `versionCode`.
3. Sprawdzić ZIP Windows: komplet plików aplikacji, uruchomienie programu, skan antywirusowy i instrukcję podmiany.
4. Po **wyraźnym zatwierdzeniu właściciela** utworzyć **publiczny Release** w tym repozytorium, z tagiem `vX.Y.Z`.
5. Dodać w Release dwa pliki o dokładnych nazwach: `RemoteDeskPRO.apk` i `RemoteDeskPRO-Windows.zip`.
6. Wyliczyć SHA-256 plików **faktycznie opublikowanych** i porównać z paczkami testowanymi wcześniej.

## Aktywacja kanału

7. Przygotować plik `version.json` na podstawie `docs/version.example.json`, z prawdziwymi numerami, URL i 64-znakowymi SHA-256.
8. Zweryfikować manifest lokalnie: `python scripts/validate_manifest.py version.json`. Plik musi wskazywać wyłącznie publiczne pliki z tego repo.
9. Dopiero gdy oba URL działają, ich SHA-256 są prawidłowe, a zgoda na publikację została udzielona, scalić `version.json` do głównej gałęzi `main`.
10. Sprawdzić odczyt manifestu przez HTTPS oraz wykrycie nowej wersji z zainstalowanej starszej aplikacji.
11. Na Androidzie systemowy instalator musi poprosić użytkownika o zgodę. Zweryfikować działanie bez utraty danych **na dwóch kolejnych wersjach podpisanych tym samym kluczem**.
12. Na Windows obecna funkcja to sprawdzenie i pobranie ZIP; wymiana plików jest ręczna. Nie oznaczać jej jako automatycznej aktualizacji Windows.

## Zasady bezpieczeństwa

- Nigdy nie commitować JKS, haseł, tokenów, plików prywatnych ani kodu źródłowego aplikacji.
- Nie publikować paczek debug jako release; testowy APK z GitHub Actions nie zastępuje podpisanego wydania.
- Wymagać **stałego certyfikatu podpisu** i wyższego `versionCode` dla kolejnych aktualizacji Androida.
- Nie publikować `version.json`, gdy pliki Release nie istnieją lub nie są zatwierdzone.
- SHA-256 względem manifestu sprawdza integralność, ale bez podpisanego/trusted manifestu nie daje silnej gwarancji autentyczności wydawcy; należy zachować bezpieczeństwo konta GitHub i kluczy, a przed wydaniami produkcyjnymi rozważyć podpisanie manifestu.

**Status obecny:** tylko infrastruktura i dokumentacja. Nie ma zatwierdzonego, podpisanego wydania.
