import pyodbc
import csv
import os
import time

from db_config import get_conn_str, PROJECT_ROOT

# --- 1. CONFIGURAZIONE ---
# Le credenziali sono lette dal file .env nella root del progetto (vedi db_config.py)
INPUT_DIR = str(PROJECT_ROOT / 'dimensions')

conn_str = get_conn_str()

# --- Pulizia finale ---
def clean_val(v):
    """
    Gestisce solo problemi tecnici:
    1. Stringhe vuote -> None (NULL)
    2. Numeri float che dovrebbero essere int (1.0 -> 1)
    """
    if v is None: return None
    s = str(v).strip()
    if s == '' or s.lower() == 'nan': return None
    
    # Fix per i numeri "1.0" 
    if '.' in s:
        try:
            f = float(s)
            if f.is_integer(): return int(f)
            return f
        except:
            pass
    return s


def load_table(cursor, table_name, file_name, columns, pk_index=0):
    file_path = os.path.join(INPUT_DIR, file_name)
    
    if not os.path.exists(file_path):
        print(f"FILE MANCANTE: '{file_name}'. Salto {table_name}.")
        return

    print(f"Caricamento {table_name}...")
    
    placeholders = ', '.join(['?'] * len(columns))
    col_names = ', '.join(columns)
    query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

    batch = []
    seen_ids = set()
    total = 0
    skipped_dup = 0
    skipped_col = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Salta Header
            
            for row in reader:
                # 1. Pulizia Tecnica (None e Numeri)
                clean_row = [clean_val(x) for x in row]
                
                # 2. Controllo Coerenza Colonne
                if len(clean_row) != len(columns): 
                    # Se il CSV ha colonne diverse dal DB, saltiamo
                    skipped_col += 1
                    continue

                # 3. Controllo Duplicati PK (Sicurezza)
                pk = clean_row[pk_index]
                if pk in seen_ids: 
                    skipped_dup += 1
                    continue
                seen_ids.add(pk)

                batch.append(clean_row)
                
                # 4. Invio Batch
                if len(batch) >= 1000:
                    cursor.executemany(query, batch)
                    total += len(batch)
                    batch = []
                    print(f"   ...inserite {total} righe", end='\r')

            # Invio residui
            if batch:
                cursor.executemany(query, batch)
                total += len(batch)

        print(f"{table_name}: Fatto. {total} inserite. (Scartati: {skipped_dup} doppi, {skipped_col} colonne errate)")

    except Exception as e:
        print(f"ERRORE su {table_name}: {e}")
        conn.rollback()


if __name__ == "__main__":
    t0 = time.perf_counter()
    conn = pyodbc.connect(conn_str)
    cur = conn.cursor()

    # Ripopolamento tabelle
    try:

        cols_geo = [
        "geo_id",
        "birth_place",
        "province",
        "region",
        "country",
        "latitude",
        "longitude",
        "geocode"
        ]
        load_table(cur, 'GeographyDim', 'geography_dim.csv', cols_geo, pk_index=0)

        cols_alb = [
        "album_id",
        "album_name",
        "album_release_date",
        "album_type",
        "disc_number",
        "track_number"
        ]
        load_table(cur, 'AlbumDim', 'album_dim.csv', cols_alb, pk_index=0)

        cols_date = [
        "date_id",
        "day",
        "month",
        "year",
        "season",
        "weekday"
        ]
        load_table(cur, 'DateDim', 'date_dim.csv', cols_date, pk_index=0)

        cols_sym = [
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
        load_table(cur, 'SymphonyDim', 'symphony_dim.csv', cols_sym, pk_index=0)

        cols_txt = [
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
        load_table(cur, 'TextDim', 'text_dim.csv', cols_txt, pk_index=0)

        conn.commit()

        cols_art = [
        'id_author', 
        'name', 
        'gender', 
        'birth_date',
        'active_start', 
        'artist_type',
        "geo_id"
        ]
        load_table(cur, 'ArtistDim', 'artist_dim.csv', cols_art, pk_index=0)
        
        conn.commit()

        cols_fact = [
        "id_track",
        "title",
        "streams_1month",
        "symp_id",
        "text_id",
        "id_author",
        "album_id",
        "date_id"
        ]
        load_table(cur, 'FactSong', 'fact_table.csv', cols_fact, pk_index=0)

        conn.commit()
        print("\n CARICAMENTO COMPLETATO CON SUCCESSO!")

    except Exception as e:
        print(f"Errore generale: {e}")
        conn.rollback()
    finally:
        conn.close()
        print(f"Tempo: {time.perf_counter()-t0:.2f}s")