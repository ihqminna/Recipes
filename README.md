# Reseptikirjasto

**Hallinnoi reseptejäsi helposti ja inspiroidu muiden resepteistä Reseptikirjasto-sovelluksessa!**

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnukseen, kirjautumaan sisään sovellukseen ja kirjautumaan ulos.
* Käyttäjä näkee kaikki reseptit, sekä erikseen itse lisäämänsä reseptit.
* Kullakin reseptillä on oma sivu.
* Käyttäjä pystyy etsimään reseptejä hakusanalla.
* Reseptin voi poistaa.
* Reseptiä voi muokata.
* Kuvan lisääminen reseptiin.
* Reseptiin voi lisätä ainesosia.
* Avainsanat on listattu erikseen ja niiden perusteella voi selata reseptejä.
* Reseptisivulla sitä voi kommentoida.
* Käyttäjäsivu, jossa näkee käyttäjän aktiivisuuden.
* Reseptiin voi lisätä valmiita avainsanoja (kuten "salaatti" ja "vegaaninen").

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja reseptien avainsanat:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```

## Suuri tietomäärä
Kun reseptejä luotiin 10 000, käyttäjiä 10 000 ja kommentteja 1 000 000, etusivusta tuli aivan valtavan pitkä ja sen latauksessa alkoi olemaan ongelmia.

Sivutuksella (24 reseptiä per sivu) tilanne parani huomattavasti ja 10 000 reseptillä sivut ladattiin todella nopeasti:
elapsed time: 0.05 s
127.0.0.1 - - [19/Oct/2025 23:25:47] "GET /4 HTTP/1.1" 200 -
elapsed time: 0.37 s
127.0.0.1 - - [19/Oct/2025 23:25:48] "GET /static/default.jpg HTTP/1.1" 304 -
elapsed time: 0.39 s
127.0.0.1 - - [19/Oct/2025 23:25:48] "GET /static/eggplant.png HTTP/1.1" 304 -
elapsed time: 0.4 s
127.0.0.1 - - [19/Oct/2025 23:25:48] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.02 s
127.0.0.1 - - [19/Oct/2025 23:25:49] "GET /5 HTTP/1.1" 200 -

Kun testidataa kasvatetaan 1 000 000 reseptiin, alkaa latauskin hidastumaan:
elapsed time: 0.15 s
127.0.0.1 - - [19/Oct/2025 23:30:21] "GET /1 HTTP/1.1" 200 -
elapsed time: 0.22 s
127.0.0.1 - - [19/Oct/2025 23:30:21] "GET /static/default.jpg HTTP/1.1" 304 -
elapsed time: 0.29 s
127.0.0.1 - - [19/Oct/2025 23:30:22] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.31 s
127.0.0.1 - - [19/Oct/2025 23:30:22] "GET /static/eggplant.png HTTP/1.1" 304 -
elapsed time: 0.11 s
127.0.0.1 - - [19/Oct/2025 23:30:31] "GET /2 HTTP/1.1" 200 -

Koska etusivulle ei ladata dataa muista tauluista kuin Recipes-taulusta, päädyin testaamaan indeksointia avainsanojen avulla. Lisätään kullekin reseptille jokin avainsanoista ja testataan reseptilistauksen latautumista avainsanasivulla:
elapsed time: 1.98 s
127.0.0.1 - - [19/Oct/2025 23:42:20] "GET /avainsanat/vegaaninen HTTP/1.1" 200 -
elapsed time: 0.34 s
127.0.0.1 - - [19/Oct/2025 23:42:21] "GET /static/eggplant.png HTTP/1.1" 304 -
elapsed time: 0.35 s
127.0.0.1 - - [19/Oct/2025 23:42:21] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.36 s
127.0.0.1 - - [19/Oct/2025 23:42:21] "GET /static/default.jpg HTTP/1.1" 304 -

Tämäkin on suhteellisen nopeaa, tässäkin sivutus auttaa jo suuresti:
elapsed time: 0.11 s
127.0.0.1 - - [19/Oct/2025 23:45:31] "GET /1 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [19/Oct/2025 23:45:31] "GET /static/main.css HTTP/1.1" 304 -
elapsed time: 0.01 s
127.0.0.1 - - [19/Oct/2025 23:45:31] "GET /static/eggplant.png HTTP/1.1" 304 -
elapsed time: 0.0 s
127.0.0.1 - - [19/Oct/2025 23:45:31] "GET /static/default.jpg HTTP/1.1" 304 -


