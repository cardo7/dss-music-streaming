import pyodbc
from db_config import get_conn_str

# --- CONFIGURAZIONE ---
# Le credenziali sono lette dal file .env nella root del progetto (vedi db_config.py)
conn_str = get_conn_str()

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connessione riuscita (Assignment 4).")
except Exception as e:
    print(f"Errore: {e}")
    exit()

# --- Funzione per droppare le tabelle ---
cursor.execute("""
    IF OBJECT_ID('FactSong', 'U') IS NOT NULL DROP TABLE FactSong;
    IF OBJECT_ID('SymphonyDim', 'U') IS NOT NULL DROP TABLE SymphonyDim;
    IF OBJECT_ID('TextDim', 'U') IS NOT NULL DROP TABLE TextDim;
    IF OBJECT_ID('DateDim', 'U') IS NOT NULL DROP TABLE DateDim;
    IF OBJECT_ID('AlbumDim', 'U') IS NOT NULL DROP TABLE AlbumDim;
    IF OBJECT_ID('ArtistDim', 'U') IS NOT NULL DROP TABLE ArtistDim;
    IF OBJECT_ID('GeographyDim', 'U') IS NOT NULL DROP TABLE GeographyDim;
""")
conn.commit()
print("Vecchie tabelle eliminate.")

# --- Creazione tabelle ---

cursor.execute("""
               
    -- 1. Dimensione Geografia (Legata all'artista)
    CREATE TABLE GeographyDim (
        geo_id VARCHAR(20) PRIMARY KEY,
        birth_place VARCHAR(100),
        province VARCHAR(100),
        region VARCHAR(100),
        country VARCHAR(100),
        latitude FLOAT,
        longitude FLOAT,
        geocode VARCHAR(100)
    );
               
    -- 2. Dimensione Artista
    CREATE TABLE ArtistDim (
        id_author VARCHAR(20) PRIMARY KEY,
        name VARCHAR(255),
        gender VARCHAR(50),
        birth_date DATE,
        active_start DATE,
        artist_type VARCHAR(50),
        geo_id VARCHAR(20),
        FOREIGN KEY (geo_id) REFERENCES GeographyDim(geo_id)
    );



    -- 3. Dimensione Album
    CREATE TABLE AlbumDim (
        album_id VARCHAR(20) PRIMARY KEY,
        album_name VARCHAR(500),
        album_release_date DATE,
        album_type VARCHAR(50),
        disc_number INT,
        track_number INT
    );

    -- 4. Dimensione Tempo (Date)
    CREATE TABLE DateDim (
        date_id INT PRIMARY KEY,
        day INT,
        month INT,
        year INT,
        season VARCHAR(7),
        weekday VARCHAR(10)
    );

    -- 5. Dimensione Audio Features (Symphony)
    CREATE TABLE SymphonyDim (
        symp_id VARCHAR(20) PRIMARY KEY,
        bpm FLOAT,
        rolloff FLOAT,
        flux FLOAT,
        rms FLOAT,
        flatness FLOAT,
        spectral_complexity FLOAT,
        pitch FLOAT,
        loudness FLOAT, 
        duration_ms INT,
        popularity INT,
        audio_label VARCHAR(25)
    );

    -- 6. Dimensione Testo (Text)
    CREATE TABLE TextDim (
        text_id VARCHAR(20) PRIMARY KEY,
        lyrics NVARCHAR(MAX),
        featured_artists NVARCHAR(MAX),
        language VARCHAR(5),
        explicit BIT,
        swear_IT           INT,
        swear_EN           INT,
        swear_IT_words     NVARCHAR(MAX),
        swear_EN_words     NVARCHAR(MAX),
        n_sentences INT,
        n_tokens INT,
        char_per_tok FLOAT,
        avg_token_per_clause FLOAT
    );

    -- 7. Fact Table (Al centro)
    CREATE TABLE FactSong (
        id_track VARCHAR(20) PRIMARY KEY,
        title VARCHAR(500),
        streams_1month INT,
        symp_id VARCHAR(20),
        text_id VARCHAR(20),
        id_author VARCHAR(20),
        album_id VARCHAR(20),
        date_id INT,
        FOREIGN KEY (id_author) REFERENCES ArtistDim(id_author),
        FOREIGN KEY (album_id) REFERENCES AlbumDim(album_id),
        FOREIGN KEY (date_id) REFERENCES DateDim(date_id),
        FOREIGN KEY (symp_id) REFERENCES SymphonyDim(symp_id),
        FOREIGN KEY (text_id) REFERENCES TextDim(text_id)
    );
""")
conn.commit()
print("Tabelle create con successo.")
conn.close()