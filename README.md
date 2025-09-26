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

## Tulevat toiminnot

* Reseptiin voi lisätä ainesosia.
* Reseptisivulla sitä voi kommentoida.
* Käyttäjäsivu, jossa näkee oman aktiivisuutensa.
* Reseptiin voi lisätä valmiita avainsanoja (kuten "salaatti", "kevyt", "vegaaninen").
* Avainsanat on listattu erikseen ja niiden perusteella voi selata reseptejä.

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
