import csv
from pprint import pprint
from pathlib import Path

csv.field_size_limit(10**9)  # i testi delle canzoni superano il limite di default

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
DIMENSIONS_DIR = PROJECT_ROOT / 'dimensions'
DIMENSIONS_DIR.mkdir(exist_ok=True)

with open(PROCESSED_DIR / "artisti.csv", "r", encoding='utf-8') as fonte_artisti:
    artisti = list(csv.DictReader(fonte_artisti, delimiter=";"))

with open(PROCESSED_DIR / "tracks_clean.csv","r",encoding= "utf-8") as fonte_tracce:
    tracce = list(csv.DictReader(fonte_tracce, delimiter=","))


def crea_dimensioni(dati, nome_file: str, colonne: list, chiave_primaria: str):
    ids_visti = set()     # Set per tracciare solo gli ID
    tabella_finale = []   # Lista per le righe complete

    for riga in dati:
        # 1. Estrai l'ID corrente e puliscilo
        valore_id = riga.get(chiave_primaria, "").strip()

        # 2. Controlla se l'ID esiste e se non è stato ancora processato
        if valore_id != "" and valore_id not in ids_visti:
            # Aggiungi l'ID al set dei "visti"
            ids_visti.add(valore_id)

            # 3. Crea la tupla con tutte le colonne richieste
            record_tupla = tuple(riga.get(col, "").strip() for col in colonne)
            tabella_finale.append(record_tupla)


    # Scrittura su file
    with open(DIMENSIONS_DIR / nome_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(colonne)        # Header
        writer.writerows(tabella_finale) # Dati

    print(f"Dimensione '{nome_file}' creata con {len(tabella_finale)} record univoci (basati su {chiave_primaria})")
    return tabella_finale



colonne_geo = [
    "geo_id",
    "birth_place",
    "province",
    "region",
    "country",
    "latitude",
    "longitude",
    "geocode"
]



geography_dim = crea_dimensioni(artisti, "geography_dim.csv",colonne_geo, "geo_id")


colonne_artista = [
    'id_author',
    'name',
    'gender',
    'birth_date',
    'active_start',
    'artist_type',
    "geo_id"
]

artist_dim = crea_dimensioni(artisti, "artist_dim.csv",colonne_artista, "id_author")



colonne_album = [
    "album_id",
    "album_name",
    "album_release_date",
    "album_type",
    "disc_number",
    "track_number"
]

album_dim = crea_dimensioni(tracce, "album_dim.csv",colonne_album, "album_id")



colonne_date = [
    "date_id",
    "day",
    "month",
    "year",
    "season",
    "weekday"
]

date_dim = crea_dimensioni(tracce, "date_dim.csv",colonne_date,"date_id" )



colonna_text = [
    "text_id",
    "lyrics",
    "featured_artists",
    "language",
    "explicit",
    "swear_IT",
    "swear_EN",
    "swear_IT_words",
    "swear_EN_words",
    "n_sentences",
    "n_tokens",
    "char_per_tok",
    "avg_token_per_clause"    
]

text_dim = crea_dimensioni(tracce,"text_dim.csv",colonna_text, "text_id")



colonna_symphony = [
    "symp_id",
    "bpm",
    "rolloff",
    "flux",
    "rms",
    "flatness",
    "spectral_complexity",
    "pitch",
    "loudness",
    "duration_ms",
    "popularity",
    "audio_label"
]

symphony_dim = crea_dimensioni(tracce,"symphony_dim.csv",colonna_symphony, "symp_id")



colonna_fact = [
    "id_track",
    "title",
    "streams_1month",
    "symp_id",
    "text_id",
    "id_artist",
    "album_id",
    "date_id"
]

fact_table = crea_dimensioni(tracce, "fact_table.csv", colonna_fact, "id_track")