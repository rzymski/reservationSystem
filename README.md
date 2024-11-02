___
**Aplikacja webowa stworzona w Django 4.2.6 i pythonie 3.11.1**
___

## Zawartość REDME
1. :calendar: [Opis aplikacji](#opis-aplikacji)
2. :scroll: [Funkcjonalność](#funkcjonalność)
3. :computer: [Uruchomienie aplikacji lokalnie](#Instrukcja-uruchomienia-aplikacji-lokalnie)
4. :wrench: [Konfiguracja](#konfiguracja)
5. :satellite: [Wdrożenie na serwer pythonanywhere](#wdrożenie-na-serwer-pythonanywhere)
6. :globe_with_meridians: [Działanie aplikacji](#działanie-aplikacji)

# Opis aplikacji
Aplikacja stworzona jako temat pracy inżynierskiej.</br>
Celem pracy było stworzenie aplikacji, która umożliwiałaby użytkownikom ustalenie terminów spotkań bez osoby pośredniczącej.</br></br>
Przyjmuje się, że w aplikacji są 4 rodzaje użytkowników: `administrator`, `usługodawcy`, `klienci` i `niezalogowani użytkownicy`.</br>
Terminy spotkań mają 4 stany: `propozycja terminu`, `dostępny termin`, `termin z propozycją spotkania` i `zatwierdzony termin`.</br>
**Niezalogowani użytkownicy** mogą tylko przeglądać kalendarz i tabele z terminami.</br>
**Klienci** mogą dodawać własne `propozycje terminów` oraz proponować spotkania w dostepnych terminach usługodawców. (tworzyć niepotwierdzone rezerwacje)</br>
**Usługodawcy** mogą akceptować/odrzucać propozycje klientów oraz ustalać własne `dostępne terminy`.</br>
**Administrator** ma możliwość zmiany wszystkich terminów, zmiany powiadomień i zarządza wszystkimi użytkownikami.</br>
Wszelkie zmiany w terminach automatycznie wysyłają powiadomienia do wszystkich stron związanych z danym terminem.

# Funkcjonalność
1) [x] Kalendarz
2) [x] Dodawanie, edytowanie, usuwanie dostępnych terminów
3) [x] Dodawanie, edytowanie, usuwanie rezerwacji
4) [x] Dodawanie, edytowanie, usuwanie propozycji terminów
5) [x] Zatwierdzanie i odrzucanie rezerwacji/propozycji terminów
6) [x] Filtr kalendarza (wybrani usługodawcy lub klienci)
7) [x] Tabela z dostępnymi terminami
8)[x] Tabela z  rezerwacjami
9) [x] Wyszukiwarka do tabel
10)[x] Filtry do tabel (zakres dat, użytkownik)
11) [x] Profil użytkownika
12) [x] Powiadomienia na stronie i przez email-a
13) [x] Rejestracja i Logowanie
14) [x] Panel administracyjny
15) [x] Dwa motywy (jasny i ciemny)
16) [ ] Statystyki

# Instrukcja uruchomienia aplikacji lokalnie:
Tworzymy wirtualne środowisko
```sh
python -m venv venv
```

Aktywujemy wirtualne środowisko
```sh
.\venv\Scripts\activate
```
Instalujemy wszystkie potrzebne biblioteki z pliku `requirements.txt`
```sh
pip install -r .\requirements.txt
```

Uruchomienie projektu Django
```sh
python manage.py runserver 'nrPortu opcjonalnie'
```

# Konfiguracja:
<h3>Przydatne polecenia:</h3>

Tworzenie migracji po zmianie modelów
```sh
python manage.py makemigrations appName --name changeName
```

Zatwierdzenie migracji
```sh
python manage.py migrate  
```

Tworzenie super użytkownika
```sh
python manage.py createsuperuser
```

# Wdrożenie na serwer pythonanywhere:
<details>
    <summary><h3>Uruchomienie konsoli w pythonanywhere:</h3></summary>
        W sekcji <code>Consoles</code><br/>
        Uruchamiamy konsole:        
        <img src="readmeImages/launchConsole.png?raw=true" alt="uruchomienie konsoli w pythonanywhere">
</details>

Klonujemy repozytorium:
```sh
git clone https://github.com/rzymski/reservationSystem.git
```

Tworzymy wirtaulne środowisko:
```sh
mkvirtualenv --python=/usr/bin/python3.10 venv
```

Pobieramy wszystkie potrzebne pakiety z requirements.txt:
```sh
pip install -r ./reservationSystem/requirements.txt
```

<h3><details>
    <summary>Dodanie aplikacji do serwera:</summary>
        Add a new web app --> ... --> Manual Configuration --> Python 3.10 --> ...<br/>
        <img src="readmeImages/addApplication.png?raw=true" alt="Dodanie aplikacji do serwera">
</details></h3>

<details>
<summary><h3>Ustawienia w sekcji Web:</h3></summary>
  <br/>Source code: /home/<b>nazwaUzytkownika</b>/reservationSystem (nazwa głównego folderu projektu i nazwa repozytorium na github-ie) <br/>
  <br/>Working directory: /home/<b>nazwaUzytkownika</b> <br/>
  <br/>Virtualenv: /home/<b>nazwaUzytkownika</b>/.virtualenvs/venv <br/>
  <br/>Static files: <br/>
  &emsp; URL: /static/ <br/>
  &emsp; DIRECTORY: /home/<b>nazwaUzytkownika</b>/reservationSystem/staticfiles <br/><br/>
  &emsp; URL: /media/ <br/>
  &emsp; DIRECTORY: /home/<b>nazwaUzytkownika</b>/reservationSystem/media <br/><br/>
    
WSGI configuration file:
```python
import os
import sys
path = os.path.expanduser('~/reservationSystem')  # nazwa głównego folderu projektu i nazwa repozytorium na github-ie
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'reservationSystem.settings'  # nazwa głównej aplikacji z settings.py
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
application = StaticFilesHandler(get_wsgi_application())
```
<img src="readmeImages/webSettings.png?raw=true" alt="Ustawienia aplikacji na serwerze">
</details>

Po skonfigurowaniu warto również dla pewności jeszcze raz upewnić się, że pliki statyczne są załadowane.<br/>
**Polecenie do przeładowania plików statycznych:**
```sh
python manage.py collectstatic
```

<h3><details>
    <summary>Przeładowanie aplikacji na serwerze:</summary>
        <img src="readmeImages/reloadSide.png?raw=true" alt="Przeladowanie aplikacji na serwerze">
</details></h3>

# Działanie aplikacji
**Można sprawdzić działanie aplikacji w:**
 - https://pracainzynierskapiotrszumowski.pythonanywhere.com/

**Kalendarz:**
- https://pracainzynierskapiotrszumowski.pythonanywhere.com/
<img src="readmeImages/calendar.png?raw=true" alt="Kalendarz">

**Tabele z dostepnymi terminami i rezerwacjamai:**
- https://pracainzynierskapiotrszumowski.pythonanywhere.com/eventTable/
<img src="readmeImages/eventTable.png?raw=true" alt="Tabele z dostepnymi terminami i rezerwacjamai">

**Panel rejestracyjny:**
- https://pracainzynierskapiotrszumowski.pythonanywhere.com/register/
<img src="readmeImages/registerPanel.png?raw=true" alt="Profil użytkownika">

**Panel logowania:**
- https://pracainzynierskapiotrszumowski.pythonanywhere.com/login/
<img src="readmeImages/loginPanel.png?raw=true" alt="Panel logowania">

**Profil użytkownika:**
- https://pracainzynierskapiotrszumowski.pythonanywhere.com/userProfile/1/ *id użytkownika*
<img src="readmeImages/userProfile.png?raw=true" alt="Profil użytkownika">

**Panel administracyjny:**
- https://pracainzynierskapiotrszumowski.pythonanywhere.com/admin/
<img src="readmeImages/adminPanel.png?raw=true" alt="Panel administracyjny">
