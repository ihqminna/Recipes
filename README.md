# Reseptikirjasto

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnukseen, kirjautumaan sisään sovellukseen ja kirjautumaan ulos.
* Käyttäjä näkee kaikki reseptit, sekä erikseen itse lisäämänsä reseptit.

## Tulevat toiminnot (työn alla)

* Kuvan lisääminen reseptiin.
* Kullakin reseptillä oma sivu
* Reseptin sivulla sitä voi muokata
* Reseptisivulla sitä voi kommentoida.
* Reseptin voi poistaa.
* Käyttäjäsivu, jossa näkee oman aktiivisuutensa.
* Käyttäjä pystyy etsimään reseptejä hakusanalla.
* Reseptiin voi lisätä avainsanoja (kuten "salaatti", "punajuuri", "vegaaninen").
* Avainsanat on listattu erikseen ja niiden perusteella voi selata reseptejä.
* Sovellus on responsiivinen mobiilikäyttöön.

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut:

```
$ sqlite3 database.db < schema.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```
