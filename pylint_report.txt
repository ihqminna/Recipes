# Pylint-raportti

Pylint antaa seuraavan raportin sovelluksesta:

```
************* Module app
app.py:390:17: E1136: Value 'old_recipe' is unsubscriptable (unsubscriptable-object)
************* Module db
db.py:12:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:24:0: W0102: Dangerous default value [] as argument (dangerous-default-value)

------------------------------------------------------------------
Your code has been rated at 9.86/10
```

Muutama huomio jäi raportille:

## Muuttuja on "unsubscriptable"

Muuttuja old_recipe

```
app.py:390:17: E1136: Value 'old_recipe' is unsubscriptable (unsubscriptable-object)
```

Tämä on kuitenkin sanakirja listan sisällä, joten viittaukset onnistuvat seuraavasti:

```
old_recipe = [{'name': nimi, 'instructions': ohje, 'slug': slug, 'id': id, 'user_id': käyttäjä-id, 'image': kuva}]

```

Näin ollen sen sisältämiin arvoihin viitataan seuraavasti, jonka Pylint jostain syystä tulkitsee vääräksi, vaikka koodi toimii.

```
name = old_recipe[0]["name"]
```

## Vaarallinen oletusarvo

Raportissa on seuraavat ilmoitukset liittyen vaaralliseen oletusarvoon:

```
db.py:12:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:24:0: W0102: Dangerous default value [] as argument (dangerous-default-value)

```

Esimerkiksi ensimmäinen ilmoitus koskee seuraavaa funktiota: 

```
def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()
```
Tässä parametrin oletusarvo `[]` on tyhjä lista. Tässä ongelmaksi voisi tulla, että sama oletusarvona oleva tyhjä listaolio on jaettu kaikkien funktion kutsujen kesken ja jos jossain kutsussa listan sisältöä muutettaisiin, tämä muutos näkyisi myös muihin kutsuihin. Käytännössä tässä tapauksessa tämä ei kuitenkaan haittaa, koska koodi ei muuta listaoliota.

