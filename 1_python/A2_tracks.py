import json
import re
import time
import statistics
from datetime import datetime, date
from collections import Counter
from pathlib import Path
from langdetect import detect, DetectorFactory, LangDetectException

# Imposta il seed per langdetect per risultati riproducibili
DetectorFactory.seed = 0

AUDIO_FEATURES = ['bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness']

RE_PAREN_FEAT = re.compile(r"\((feat\.|ft\.|featuring)\s+([^)]+)\)", re.IGNORECASE)
RE_PLAIN_FEAT = re.compile(r"(feat\.|ft\.|featuring)\s+(.+)$", re.IGNORECASE)
RE_SPLIT_ARTISTS = re.compile(r",|&| x ")

#FUNZIONI GENERALI

def is_missing(value):
    """Controlla se un valore è mancante, nullo o stringa vuota/nan."""
    if value is None:
        return True
    if isinstance(value, str):
        v = value.strip().lower()
        return v == "" or v in {"na", "nan", "null", "none", "0", "0.0", "[]", "unknown"}
    # Gestione NaN per float
    if isinstance(value, float) and value != value:
        return True
    return False

# NORMALIZZAZIONE DATE
def parse_album_date(date_str):
    """Restituisce (year, month, day) da una stringa data."""
    if not isinstance(date_str, str) or not date_str.strip():
        return None, None, None
    
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.year, (dt.month if "%m" in fmt else None), (dt.day if "%d" in fmt else None)
        except ValueError:
            continue
    return None, None, None

# RICAVO STAFIONI DAL MESE
def get_season(month):
    if not isinstance(month, int): return None
    if month in (12, 1, 2): return "winter"
    elif month in (3, 4, 5): return "spring"
    elif month in (6, 7, 8): return "summer"
    elif month in (9, 10, 11): return "autumn"
    return None

# NORMALIZZAZIONE LINGUA
def normalize_lang(value):
    if is_missing(value) or not isinstance(value, str): return None
    v = value.strip().lower()
    mapping = {
        'it': 'it', 'ita': 'it', 'italian': 'it', 'italiano': 'it', 'it-it': 'it',
        'en': 'en', 'eng': 'en', 'english': 'en', 'en-us': 'en', 'en-gb': 'en',
        'es': 'es', 'spa': 'es', 'spanish': 'es',
        'fr': 'fr', 'fra': 'fr', 'french': 'fr',
        'de': 'de', 'ger': 'de', 'german': 'de',
        'pt': 'pt', 'por': 'pt', 'portuguese': 'pt'
    }
    return mapping.get(v, "other" if v not in {"", "nan"} else None)

# FILTRO FEATURED ARTISTS
def extract_featured_from_title(title):
    if not isinstance(title, str): 
        return None

    text = title.strip()
    match = RE_PAREN_FEAT.search(text)
    
    artists_str = ""
    if match:
        artists_str = match.group(2)
    else:
        match2 = RE_PLAIN_FEAT.search(text)
        if match2:
            artists_str = match2.group(2)
    
    if not artists_str: 
        return None

    # Pulizia extra: Rimuoviamo spazi doppi e formattiamo bene
    # Esempio input grezzo: "Guè  , Marracash & Sfera"
    # 1. Splittiamo per pulire ogni nome
    parts = [p.strip() for p in RE_SPLIT_ARTISTS.split(artists_str) if p.strip()]
    
    # 2. Rimettiamo insieme in una stringa unica pulita
    # Output: "Guè, Marracash, Sfera"
    return ", ".join(parts)

# LANGUAGE DETECTION
def detect_lang_safe(lyrics):
    if not isinstance(lyrics, str) or len(lyrics.strip()) < 20:
        return None
    try:
        code = detect(lyrics[:5000])
        return code if code in {"it", "en", "es", "fr", "de", "pt"} else "other"
    except LangDetectException:
        return None


# POP ALBUM, FILTRO DATE E FILL TRAMITE ALBUM_RELEASE_DATE
def filter_dates_and_clean(tracks):
    """
    Rimuove album, riempie le date mancanti e filtra le righe che rimangono incomplete.
    """
    clean_tracks = []

    for track in tracks:
        # 1. Elimina album
        track.pop('album', None)

        # 2. Fill date
        album_date = track.get("album_release_date")
        if album_date:
            y, m, d = parse_album_date(album_date)
            if is_missing(track.get("year")) and y: track["year"] = int(y)
            if is_missing(track.get("month")) and m: track["month"] = int(m)
            if is_missing(track.get("day")) and d: track["day"] = int(d)

        # 3. Check completezza
        if not (is_missing(track.get("year")) or is_missing(track.get("month")) or is_missing(track.get("day"))):
            clean_tracks.append(track)
    return clean_tracks


def pipeline(tracks):
    """
    SINGLE PASS LOOP: Esegue feat artists, language, season, lyrics stats ed explicit su ogni riga.
    """
    
    for track in tracks:
        # A. Featured Artists
        current_feat = track.get("featured_artists")
        
        # 1. Se manca featured_artist lo cerco nel titolo
        if is_missing(current_feat):
            track["featured_artists"] = extract_featured_from_title(track.get("title"))
            
        # 2. Se c'è già: lo puliamo (togliamo parentesi se è un residuo di lista)
        elif isinstance(current_feat, str):
            clean = current_feat.replace("[", "").replace("]", "").replace("'", "").strip()
            track["featured_artists"] = clean if clean else None
            
        else:
            track["featured_artists"] = None

        # B. Language Detection
        curr_lang = normalize_lang(track.get("language"))
        lyrics = track.get("lyrics")
        detected = detect_lang_safe(lyrics)

        if curr_lang is None:
            track["language"] = detected
        elif curr_lang == "other" and detected in {"it", "en", "es", "fr", "de", "pt"}:
             track["language"] = detected
        elif curr_lang in {"it", "en"} and detected in {"it", "en"} and detected != curr_lang:
            track["language"] = detected
        else:
            track["language"] = curr_lang

        # C. Season & Weekday
        try:
            y = int(float(track["year"]))
            m = int(float(track["month"]))
            d = int(float(track["day"]))
            
            # Year, month e day come interi
            track["year"], track["month"], track["day"] = y, m, d
            
            dt = date(y, m, d)
            track["weekday"] = dt.strftime("%A")
            track["season"] = get_season(m)
        except (ValueError, TypeError):
            track["weekday"] = None
            track["season"] = None

        # D. Lyrics Stats
        has_lyrics = lyrics and isinstance(lyrics, str) and len(lyrics.strip()) > 0
        words = lyrics.split() if has_lyrics else []
        sentences = [r for r in lyrics.split('\n') if r.strip() != ''] if has_lyrics else []
        
        # Gestione n_tokens / n_sentences
        track['n_tokens'] = int(track.get('n_tokens') or len(words))
        track['n_sentences'] = int(track.get('n_sentences') or len(sentences))

        # Char per tok
        cpt = track.get('char_per_tok')
        if (cpt is None or cpt == 0) and track['n_tokens'] > 0:
            val_cpt = sum(len(w) for w in words) / track['n_tokens']
        elif cpt is not None:
            val_cpt = cpt
        else:
            val_cpt = 0
        track['char_per_tok'] = round(float(val_cpt), 4)

        # Avg token per clause
        atpc = track.get('avg_token_per_clause')
        if (atpc is None or atpc == 0) and track['n_sentences'] > 0:
            val_atpc = track['n_tokens'] / track['n_sentences']
        elif atpc is not None:
            val_atpc = atpc
        else:
            val_atpc = 0
        track['avg_token_per_clause'] = round(float(val_atpc), 4)

        # E. Explicit
        exp = track.get('explicit')
        if is_missing(exp):
            s_en = track.get('swear_EN') or 0
            s_it = track.get('swear_IT') or 0
            track['explicit'] = True if (s_en > 0 or s_it > 0) else False
        else:
            track['explicit'] = bool(exp)
    return tracks

def audio_metrics(tracks, features):
    """
    Imputa i valori audio mancanti usando la mediana dell'artista.
    """
    # 1. Raccolta dati per artista
    art_col = {}
    for track in tracks:
        artist = track.get('primary_artist')
        if not artist: continue
        if artist not in art_col: art_col[artist] = {f: [] for f in features}
        
        for f in features:
            val = track.get(f)
            if isinstance(val, (int, float)) and val != 0:
                art_col[artist][f].append(val)

    # 2. Calcolo mediane
    artist_medians = {}
    for artist, feats in art_col.items():
        artist_medians[artist] = {}
        for f, vals in feats.items():
            if vals:
                artist_medians[artist][f] = round(statistics.median(vals), 4)

    # 3. Applicazione fix
    fixed_count = 0
    for track in tracks:
        artist = track.get('primary_artist')
        medians = artist_medians.get(artist)
        modified = False
        
        for f in features:
            val = track.get(f)
            if val is None or val == 0:
                if medians and medians.get(f) is not None:
                    track[f] = medians[f]
                    modified = True
            elif isinstance(val, float):
                track[f] = round(val, 4)
        
        if modified: fixed_count += 1
    return tracks

def regenerate_ids(tracks):
    
    # --- REGISTRI ---
    artist_map = {}          # Nome Artista -> ID (es. "guè" -> 1)
    next_artist_id = 1
    
    album_map = {}           # (ID_Artista, Nome Album) -> Sequenza Album (es. 1)
    artist_album_counts = {} # ID_Artista -> Quanti album ha finora
    
    album_track_counts = {}  # (ID_Artista, Sequenza Album) -> Quante tracce ha finora

    # --- FORMATTAZIONE ---
    # Puoi cambiare questi numeri se hai più dati
    # :03d significa "3 cifre con zeri davanti" (es. 005)
    FMT_ART = "{:03d}" 
    FMT_ALB = "{:02d}"
    FMT_TRK = "{:02d}"

    for track in tracks:
        # --- A. GESTIONE ARTISTA ---
        raw_artist = track.get('primary_artist')
        # Se manca l'artista, lo chiamiamo "unknown", ma avrà comunque un numero
        artist_name = str(raw_artist).strip().lower() if raw_artist else "unknown_artist"
        
        if artist_name not in artist_map:
            artist_map[artist_name] = next_artist_id
            next_artist_id += 1
        
        curr_art_id = artist_map[artist_name]

        # --- B. GESTIONE ALBUM ---
        raw_album = track.get('album_name')
        # Se manca l'album, usiamo un placeholder. 
        # Riceverà un ID valido (es. Album 99) che conterrà tutte le tracce sparse.
        album_name = str(raw_album).strip().lower() if raw_album else "no_album_placeholder"
        
        # La chiave unica è (Chi è l'artista + Come si chiama l'album)
        album_key = (curr_art_id, album_name)
        
        if album_key not in album_map:
            current_count = artist_album_counts.get(curr_art_id, 0)
            new_seq = current_count + 1
            
            artist_album_counts[curr_art_id] = new_seq
            album_map[album_key] = new_seq
        
        curr_alb_seq = album_map[album_key]

        # --- C. GESTIONE TRACCIA ---
        # Identifichiamo l'album specifico con (Artista + Numero Album)
        full_album_id_tuple = (curr_art_id, curr_alb_seq)
        
        curr_track_seq = album_track_counts.get(full_album_id_tuple, 0) + 1
        album_track_counts[full_album_id_tuple] = curr_track_seq

        # --- D. CREAZIONE ID ---
        # 1. Parte Artista (es. "001")
        part_art = FMT_ART.format(curr_art_id)
        # 2. Parte Album (es. "02")
        part_alb = FMT_ALB.format(curr_alb_seq)
        # 3. Parte Traccia (es. "05")
        part_trk = FMT_TRK.format(curr_track_seq)

        # Costruiamo gli ID finali
        # ID ALBUM: ALB + Artista + Album (es. ALB00102)
        new_album_id = f"ALB{part_art}{part_alb}"
        
        # ID TRACCIA: TR + Artista + Album + Traccia (es. TR0010205)
        new_track_id = f"TR{part_art}{part_alb}{part_trk}"
        
        # NUOVI ID per Symphony e Text (1-a-1 con la traccia)
        new_symp_id   = f"SYM{part_art}{part_alb}{part_trk}" # Es. SYM0010101
        new_text_id   = f"TXT{part_art}{part_alb}{part_trk}" # Es. TXT0010101
        # --- E. GESTIONE DATE_ID (INT YYYYMMDD) ---
        # Recuperiamo i valori puliti (assumiamo siano già int o None da enrich_metadata)
        y = track.get('year')
        m = track.get('month')
        d = track.get('day')
        
        # --- RINOMINA STREAMS ---
        # Se esiste la chiave vecchia con la chiocciola, la spostiamo su quella nuova e cancelliamo la vecchia
        if 'streams@1month' in track:
            track['streams_1month'] = track.pop('streams@1month')
        # --- E. PULIZIA E SALVATAGGIO ---
        # Rimuoviamo TUTTI i vecchi ID che potrebbero confondere
        track.pop('id', None)
        track.pop('source_id', None) # Se non ti serve il vecchio ID sporco, via
        track.pop('id_album', None)  # Via eventuali vecchi ID album

        if y is not None and m is not None and d is not None:
            # Formula matematica per creare l'intero: 2021 * 10000 + 4 * 100 + 5 = 20210405
            date_id = int(y) * 10000 + int(m) * 100 + int(d)
            track['date_id'] = date_id
        else:
            track['date_id'] = None
        track['id_track'] = new_track_id
        track['album_id'] = new_album_id
        track['symp_id']   = new_symp_id
        track['text_id']   = new_text_id
    print(f"Generati Smart IDs per {len(artist_map)} Artisti.")
    return tracks

# --- MAIN ---

def main():
    project_root = Path(__file__).resolve().parent.parent
    input_file = project_root / 'data' / 'raw' / 'tracks.json'
    # Output intermedio (separatore ';'): viene letto da A3_clustering, che aggiunge
    # audio_label e salva data/processed/tracks_clean.csv (usato da A5)
    output_file = project_root / 'data' / 'processed' / 'tracks_cleaned_A2.csv'

    # 1. Caricamento
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Errore: File {input_file} non trovato.")
        return

    # 2. Pipeline di elaborazione
    data = filter_dates_and_clean(data)
    data = pipeline(data) 
    
    data = audio_metrics(data, AUDIO_FEATURES)
    data = regenerate_ids(data)



    # 3. Report finale
    print("-" * 30)
    print(f"Totale tracce processate: {len(data)}")
    if data:
        print(f"Esempio (feat): {data[0].get('featured_artists')}")
        print(f"Esempio (lang): {data[0].get('language')}")
        print(f"Esempio (ID): {data[0].get('id_track')}")

    # 4. Salvataggio CSV Sicuro
    import csv
    
    if data:
        # Raccogliamo TUTTE le chiavi uniche da TUTTE le righe
        all_keys = set()
        for row in data:
            all_keys.update(row.keys())
        
        # Ordiniamo le chiavi per avere le colonne sempre nello stesso ordine
        keys = list(all_keys)

        with open(output_file, 'w', newline='', encoding='utf-8') as output_f:

            dict_writer = csv.DictWriter(output_f, fieldnames=keys, delimiter=';') 
            dict_writer.writeheader()
            dict_writer.writerows(data)
            
        print(f"File salvato correttamente: {output_file}")
    else:
        print("Nessun dato da salvare.")

if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print(f"Tempo totale: {end - start:.2f} secondi")