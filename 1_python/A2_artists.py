# data preparation (assignment 2) [artists]

import pygeohash
import xml.etree.ElementTree as et 
import pprint 
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import csv 
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'



def xml_to_dict(nome_file:str):
    artists = et.parse(nome_file)
    artists_root = artists.getroot()

    artists_df = []

    for row in artists_root.findall("row"):
        riga = {}

        for child in row:
            col_name = child.tag

            if child.text is not None:
                valore = child.text.strip()
            else:
                valore = None
            
            riga[col_name] = valore if valore != '' else None
            
        artists_df.append(riga)

    return artists_df


df = xml_to_dict(RAW_DIR / "artists.xml")


# funzione per droppare le colonne 
def column_drop(nome_colonna:str, df:list):
    for row in df:
        row.pop(nome_colonna, None) 

column_drop("active_end",df)

# funzione per droppare le righe 

def row_drop(index_riga:int, df:list):
    del df[index_riga]


# creiamo una nuova colonna "artist_type" per distinguere i solisti dai gruppi:

for riga in df:
    if riga["description"]:
        if "gruppo" in riga["description"]:
            riga["artist_type"] = "gruppo"
        else:
            riga["artist_type"] = "solista"
    else:
        riga["artist_type"] = "solista"

# una volta che abbiamo estratto queste informazioni possiamo droppare la colonna description 

column_drop("description", df)



# vado a ripopolare manualmente il dati mancanti del dataset (ho provato con un API ma non mi è riuscito)

df[2]["birth_date"] = "2000-08-22"
df[2]["birth_place"] = "Genova"
df[2]["active_start"] = "2017-01-15"
df[2]["artist_type"] = "solista"
df[3]["birth_place"] = "La Spezia"
df[4]["birth_place"] = "Milano"
df[8]["birth_place"] = "Torino"
df[9]["birth_place"] = "Avellino"
df[10]["birth_place"] = "Roma"
df[11]["birth_place"] = "La spezia"
df[12]["birth_place"] = "Milano"
df[22]["birth_place"] = "Milano"
df[42]["birth_place"] = "Milano"
df[44]["birth_place"] = "Leonforte"
df[51]["birth_place"] = "Palermo"
df[61]["birth_place"] = "Avellino"
df[62]["birth_place"] = "Milano"
df[65]["birth_place"] = "Milano"
df[70]["birth_place"] = "Milano"
df[75]["birth_place"] = "Napoli"
df[78]["birth_place"] = "Apulia"
df[87]["birth_place"] = "La Spezia"
df[91]["birth_place"] = "Legnano"
df[92]["birth_place"] = "Roma"
df[102]["birth_place"] = "Santo Domingo"
df[102]["country"] = "Dominican Republic"
df[102]["birth_date"] = "1993-07-27"
df[91]["birth_date"] = "1999-08-27"
df[75]["birth_date"] = "1970-11-05"
df[51]["birth_date"] = "1986-08-05"
df[3]["birth_date"] = "2003-08-15"
df[8]["birth_date"] = "1994-01-01"
df[9]["birth_date"] = "2000-03-10"
df[12]["birth_date"] = "1976-09-30"
df[22]["birth_date"] = "1980-11-29"
df[42]["birth_date"] = "1980-12-25"
df[44]["birth_date"] = "1995-01-01"
df[51]["birth_date"] = "1986-08-05"
df[61]["birth_date"] = "1985-08-02"
df[62]["birth_date"] = ""
df[62]["active_start"]= "2013-01-01"
df[65]["birth_date"] = "1985-01-01"
df[70]["birth_date"] = "1991-05-23"
df[75]["birth_date"] = "1970-11-15"
df[78]["birth_date"] = "1996-08-20"
df[87]["birth_date"] = "1991-01-01"
df[92]["birth_date"] = "1992-06-05"
df[102]["birth_date"] = "1993-07-27"
df[3]["active_start"] = "2020-01-31"
df[5]["active_start"] = "1989-01-01"
df[8]["active_start"] = "2015-03-13"
df[10]["active_start"] = "2001-01-01"
df[11]["active_start"] = "2015-03-12"
df[12]["active_start"] = "2006-01-01"
df[14]["active_start"] = "2013-02-26"
df[15]["active_start"] = "2018-04-28"
df[16]["active_start"] = "2006-04-29"
df[17]["active_start"] = "2003-01-01"
df[19]["active_start"] = "1996-01-01"
df[21]["active_start"] = "2016-01-01"
df[22]["active_start"] = "2006-01-01"
df[25]["active_start"] = "2011-06-14"
df[26]["active_start"] = "2016-05-16"
df[29]["active_start"] = "2008-01-01"
df[36]["active_start"] = "2012-11-06"
df[38]["active_start"] = "2018-04-19"
df[42]["active_start"] = "2011-06-14"
df[43]["active_start"] = "2011-01-01"
df[44]["active_start"] = "2019-07-12"
df[48]["active_start"] = "2006-01-01"
df[51]["active_start"] = "2010-01-01"
df[52]["active_start"] = "1995-01-01"
df[54]["active_start"] = "2012-06-19"
df[58]["active_start"] = "2017-02-04"
df[60]["active_start"] = "2019-01-22"
df[61]["active_start"] = "2017-06-27"
df[62]["active_start"] = "2013-10-01"
df[64]["active_start"] = "2005-01-01"
df[65]["active_start"] = "2011-01-01"
df[66]["active_start"] = "2004-05-01"
df[70]["active_start"] = "2014-01-01"
df[72]["active_start"] = "2021-07-23"
df[75]["active_start"] = "1993-01-01"
df[76]["active_start"] = "2021-02-19"
df[82]["active_start"] = "2020-01-16"
df[87]["active_start"] = "2016-01-01"
df[89]["active_start"] = "2008-05-01"
df[91]["active_start"] = "2015-10-06"
df[92]["active_start"] = "2019-06-14"
df[93]["active_start"] = "2012-01-01"
df[94]["active_start"] = "1994-01-01"
df[95]["active_start"] = "2015-10-01"
df[97]["active_start"] = "2019-01-01"
df[98]["active_start"] = "2015-05-19"
df[99]["active_start"] = "2006-06-01"
df[102]["active_start"] = "2019-12-06"
df[103]["active_start"] = "2014-01-01"
df[0]["birth_place"] = "Napoli"
df[4]["birth_place"] = "Milano"
df[11]["birth_place"] = "La Spezia"
df[17]["birth_place"] = "Milano"
df[19]["birth_place"] = "Roma"
df[20]["birth_place"] = "Roma"
df[23]["birth_place"] = "Roma"
df[94]["birth_place"] = "Varese"

for e in df:
    
    e["country"] = "Italia"
    e["nationality"] = "Italia"

# essendo che entrambe le colonne "country" e "nationality" hanno gli stessi valori (Italia) andrò a droppare la colonna nationality 

column_drop("nationality",df)

# cerchiamo di popolare le province [sta cosa è servita praticamente ad un cazzo]
città_capitali = []
for riga in df:
    if riga["birth_place"] in città_capitali:
        if riga["province"] is None:
            riga["province"] = riga["birth_place"]


# Mappa il luogo di nascita (birth_place) alla sua Provincia (Province)
città_provincia = {
    "Verona": "Verona",
    "Rho": "Milano",
    "Milano": "Milano",
    "Sternatia": "Lecce",
    "Salerno": "Salerno",
    "Avellino": "Avellino",
    "Nocera Inferiore": "Salerno",
    "La Spezia": "La Spezia",
    "Bologna": "Bologna",
    "Vimercate": "Monza e della Brianza",
    "Alpignano": "Torino",
    "Senigallia": "Ancona",
    "Brescia": "Brescia",
    "Torino": "Torino",
    "Roma": "Roma",
    "Napoli": "Napoli",
    "Olbia": "Gallura", 
    "Firenze": "Firenze",
    "Scampia": "Napoli",
    "Vicenza": "Vicenza",
    "Grottaglie": "Taranto",
    "Nicosia": "Enna",
    "Gallarate": "Varese",
    "Treviso": "Treviso",
    "Desenzano del Garda": "Brescia",
    "San Benedetto del Tronto": "Ascoli Piceno",
    "Scafati": "Salerno",
    "Pieve Emanuele": "Milano",
    "Grugliasco": "Torino",
    "Lodi": "Lodi",
    "Cagliari": "Cagliari",
    "Reggio Calabria": "Reggio Calabria",
    "Fiumicino": "Roma",
    "Padova": "Padova",
   
}

provincia_regione = {
    # Lombardia
    "Milano": "Lombardia",
    "Varese": "Lombardia",
    "Brescia": "Lombardia",
    "Lodi": "Lombardia",
    "Monza e della Brianza": "Lombardia", 
    
    # Lazio
    "Roma": "Lazio",
    
    # Campania
    "Napoli": "Campania",
    "Salerno": "Campania",
    "Avellino": "Campania",
    
    # Veneto
    "Verona": "Veneto",
    "Vicenza": "Veneto",
    "Treviso": "Veneto",
    "Padova": "Veneto",

    # Piemonte
    "Torino": "Piemonte",

    # Puglia
    "Taranto": "Puglia",
    "Lecce": "Puglia",

    # Liguria
    "Genova": "Liguria",
    "La Spezia": "Liguria",
    
    # Marche
    "Ascoli Piceno": "Marche",
    
    # Toscana
    "Firenze": "Toscana",
    
    # Sicilia
    "Enna": "Sicilia",
    
    # Calabria
    "Reggio Calabria": "Calabria",
    
    # Sardegna
    "Gallura": "Sardegna",
    "Cagliari": "Sardegna",
    
    # Emilia-Romagna
    "Bologna": "Emilia-Romagna",
    
    # Ancona
    "Ancona": "Marche", 
}

# riempiamo la colonna "region"
for riga in df:
    if riga["province"] is None and riga["birth_place"] is not None:
        if riga["birth_place"] in città_provincia:
            riga["province"] = città_provincia[riga["birth_place"]]





for riga in df:
    if riga["province"]:
        riga["region"] = provincia_regione[riga["province"]]
    else:
        continue


# tramite il birth_place ripopoliamo anche latitudine e longitudine 

geolocator = Nominatim(user_agent="Geo_ETL_Script") 

def fill_lat_long(df : list):
    
    for riga in df:
        citta = riga.get('birth_place')
        lat_esistente = riga.get('latitude')
        
        # Se la latitudine è vuota (None o stringa vuota) E la città è presente
        if (lat_esistente is None or lat_esistente == '') and citta is not None:
            
            try:
                # Componi la query e cercala
                query = citta + ", Italia"
                location = geolocator.geocode(query) # Chiama l'API
                
                if location:
                    # Se il risultato è valido, aggiorna la riga
                    riga['latitude'] = str(location.latitude)
                    riga['longitude'] = str(location.longitude)
                
                # Pausa obbligatoria per non sovraccaricare l'API di Nominatim
                time.sleep(1.5) 
                
            except GeocoderServiceError:
                # Se l'API restituisce un errore di servizio (es. rate limit), aspetta di più e continua
                time.sleep(5) 
                continue 
                
    return df 


fill_lat_long(df)

# creazione della colonna "geo_code" tramite latitude e longitude 

for riga in df:
    long = riga.get("longitude")
    lati = riga.get("latitude")

# di base xml etree transforma tutte le variabili in stringhe, quindi devo riportare i valori a dei flaot 

    if long and lati:
        long_float = float(long)
        lati_float = float(lati)

        geocode = pygeohash.encode(lati_float,long_float, precision= 5 ) # precisione = 5 indica un'area di 5 km quadrati quindi ottima per analizzare quartieri e città 
        riga["geocode"] = geocode
    else:
        riga["geocode"] = None




place_to_id_map = {}
current_id = 1  

for row in df:
    place = row.get("birth_place")
   
    if place not in place_to_id_map:
        place_to_id_map[place] = current_id
        current_id += 1
    
    row["geo_id"] = place_to_id_map[place]


import csv

def save_to_csv(data_list, filename):
    
    keys = data_list[0].keys()
 
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            
            
        lettore = csv.DictWriter(output_file, fieldnames=keys, delimiter=';') # Uso ; come separatore (più sicuro per Excel italiano)    
        lettore.writeheader()
        lettore.writerows(data_list)
            
    print(" File salvato con successo")
        
save_to_csv(df, PROCESSED_DIR / "artisti.csv")






