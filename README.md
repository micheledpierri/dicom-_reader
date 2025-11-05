# DICOM Reader

Un lettore DICOM completo con funzionalità avanzate per la visualizzazione, manipolazione e gestione di immagini mediche DICOM.

## Caratteristiche Principali

### 🖼️ Visualizzazione Immagini
- **Interfaccia grafica intuitiva** basata su PyQt5
- **Caricamento rapido** di file DICOM da directory o file individuali
- **Organizzazione automatica** in studi e serie
- **Navigazione semplice** tra immagini multiple
- **Window/Level regolabile** per ottimizzare la visualizzazione
- **Modalità Cine** per riproduzione continua delle serie di immagini
  - FPS regolabile (1-60 fps)
  - Modalità loop attivabile
  - Controlli play/pause

### 🔧 Elaborazione Immagini
Modulo completo di filtri per l'elaborazione delle immagini:

**Filtri Base:**
- Regolazione luminosità e contrasto
- Sharpening (nitidezza)
- Gaussian blur
- Median filter per riduzione rumore
- Inversione immagine
- Correzione gamma

**Equalizzazione Istogramma:**
- Equalizzazione standard
- CLAHE (Contrast Limited Adaptive Histogram Equalization)

**Edge Detection:**
- Sobel operator
- Canny edge detector

**Thresholding:**
- Soglia binaria
- Soglia automatica di Otsu

**Morfologia:**
- Erosione e dilatazione
- Apertura e chiusura morfologica

**Denoising:**
- Bilateral filter (preserva i bordi)
- Non-local means denoising

**Preset Medici:**
- Miglioramento visualizzazione ossa
- Miglioramento tessuti molli
- Riduzione rumore
- Enfatizzazione bordi

### 🎲 Ricostruzione 3D
- **Volume rendering** usando VTK
- **Preset di rendering**:
  - Visualizzazione ossa
  - Visualizzazione tessuti molli
  - Maximum Intensity Projection (MIP)
- **Multi-Planar Reconstruction (MPR)**:
  - Viste assiali, coronali e sagittali
  - Slicing obliquo

### 💾 Database Locale
- **Database SQLite** per archiviazione locale
- **Organizzazione gerarchica**: Paziente → Studio → Serie → Istanza
- **Ricerca rapida** per paziente, studio o serie
- **Gestione completa** con funzioni CRUD
- **Metadati DICOM** completi salvati nel database

## Installazione

### Requisiti
- Python 3.8 o superiore
- Sistema operativo: Windows, Linux, o macOS

### Installazione Dipendenze

```bash
# Clone del repository
git clone https://github.com/yourusername/dicom-_reader.git
cd dicom-_reader

# Installazione delle dipendenze
pip install -r requirements.txt
```

### Dipendenze Principali
- `pydicom` - Lettura e parsing file DICOM
- `PyQt5` - Interfaccia grafica
- `numpy` - Elaborazione array numerici
- `vtk` - Ricostruzione e rendering 3D
- `opencv-python` - Elaborazione immagini
- `scikit-image` - Algoritmi di image processing
- `scipy` - Funzioni scientifiche
- `sqlalchemy` - ORM per database

## Utilizzo

### Avvio Applicazione

```bash
python main.py
```

### Caricamento File DICOM

**Opzione 1 - Carica Directory:**
1. Clicca su "Open Directory" o usa `Ctrl+O`
2. Seleziona la directory contenente i file DICOM
3. L'applicazione caricherà automaticamente tutti i file DICOM trovati

**Opzione 2 - Carica File Individuali:**
1. Clicca su "Open Files" o usa `Ctrl+Shift+O`
2. Seleziona uno o più file DICOM
3. I file saranno organizzati in studi e serie

### Navigazione Immagini

**Controlli Base:**
- **First/Previous/Next/Last** - Pulsanti di navigazione
- **Slider** - Scorri velocemente tra le immagini
- **Mouse wheel** - Scorrimento rapido (se abilitato)

**Window/Level:**
- Usa gli slider per regolare Window Center e Window Width
- Clicca "Reset Window/Level" per tornare ai valori predefiniti DICOM

**Modalità Cine:**
1. Imposta il FPS desiderato (1-60)
2. Attiva/disattiva "Loop" per ripetizione continua
3. Clicca "Play" per avviare la riproduzione
4. Clicca "Stop" per fermare

### Filtri Immagine

1. Seleziona un'immagine
2. Menu: `Tools → Image Filters`
3. Scegli il filtro desiderato
4. Regola i parametri
5. Applica il filtro

### Ricostruzione 3D

1. Carica una serie con almeno 2 immagini
2. Menu: `Tools → 3D Reconstruction`
3. Scegli il preset di rendering:
   - Bone (ossa)
   - Soft Tissue (tessuti molli)
   - MIP (Maximum Intensity Projection)
4. Interagisci con il volume usando mouse e tastiera

### Database Locale

**Aggiungere File al Database:**
1. Carica i file DICOM
2. Menu: `Database → Add to Database`
3. Conferma l'aggiunta

**Gestire il Database:**
1. Menu: `Database → Manage Database`
2. Visualizza, cerca ed elimina record
3. Usa la ricerca per trovare rapidamente pazienti o studi

## Struttura del Progetto

```
dicom-_reader/
├── main.py                          # Entry point applicazione
├── requirements.txt                 # Dipendenze Python
├── README.md                        # Questo file
└── dicom_reader/                    # Package principale
    ├── __init__.py
    ├── dicom/                       # Moduli DICOM
    │   ├── __init__.py
    │   ├── loader.py                # Caricamento file DICOM
    │   ├── parser.py                # Parsing metadati DICOM
    │   └── series_organizer.py      # Organizzazione serie
    ├── gui/                         # Interfaccia grafica
    │   ├── __init__.py
    │   ├── main_window.py           # Finestra principale
    │   ├── viewer_widget.py         # Widget visualizzazione
    │   └── series_navigator.py      # Navigatore serie
    ├── processing/                  # Elaborazione immagini
    │   ├── __init__.py
    │   ├── filters.py               # Filtri immagine
    │   └── reconstruction_3d.py     # Ricostruzione 3D
    ├── database/                    # Gestione database
    │   ├── __init__.py
    │   ├── db_manager.py            # Manager database
    │   └── models.py                # Modelli SQLAlchemy
    └── utils/                       # Utilities
        ├── __init__.py
        └── config.py                # Configurazione
```

## Utilizzo Programmatico

### Esempio: Caricamento e Visualizzazione

```python
from dicom_reader.dicom import DICOMLoader, SeriesOrganizer
from dicom_reader.dicom import DICOMParser

# Carica file DICOM
loader = DICOMLoader()
file_paths = loader.load_from_directory("/path/to/dicom/files")
datasets = loader.load_files(file_paths)

# Organizza in serie
organizer = SeriesOrganizer()
organizer.add_datasets(datasets)
organizer.sort_all_series()

# Ottieni informazioni
studies = organizer.get_studies_list()
for study in studies:
    print(f"Study: {study.study_description}")
    for series in study.get_series_list():
        print(f"  Series: {series.series_description} ({series.get_instance_count()} images)")
```

### Esempio: Applicazione Filtri

```python
from dicom_reader.processing import ImageFilters
import numpy as np

# Carica immagine (assume image_array sia un numpy array)
image_array = ...

# Applica filtri
sharpened = ImageFilters.sharpen(image_array, amount=1.5)
denoised = ImageFilters.denoise_bilateral(sharpened)
enhanced = ImageFilters.adaptive_histogram_equalization(denoised)
```

### Esempio: Database

```python
from dicom_reader.database import DatabaseManager

# Inizializza database
db = DatabaseManager()

# Aggiungi file DICOM
db.add_dicom_file("/path/to/file.dcm")

# Cerca pazienti
patients = db.search_patients("John Doe")

# Ottieni statistiche
stats = db.get_database_stats()
print(f"Database: {stats['patients']} patients, {stats['studies']} studies")
```

## Configurazione

Le configurazioni si trovano in `dicom_reader/utils/config.py`:

- Percorsi directory applicazione
- Impostazioni default window/level
- Parametri modalità cine
- Livello di logging
- Dimensioni finestra

## Log e Debug

I log dell'applicazione sono salvati in:
- Linux/Mac: `~/.dicom_reader/logs/dicom_reader.log`
- Windows: `%USERPROFILE%\.dicom_reader\logs\dicom_reader.log`

Per debug dettagliato, modifica `LOG_LEVEL` in `config.py`:
```python
LOG_LEVEL = "DEBUG"
```

## Troubleshooting

### L'applicazione non si avvia
- Verifica che tutte le dipendenze siano installate: `pip install -r requirements.txt`
- Controlla i log in `~/.dicom_reader/logs/`

### I file DICOM non vengono caricati
- Verifica che i file siano validi DICOM
- Controlla i permessi di lettura sui file
- Alcuni file DICOM compressi potrebbero richiedere dipendenze aggiuntive

### Problemi con il rendering 3D
- Assicurati che VTK sia installato correttamente
- Su alcuni sistemi potrebbe essere necessario installare driver OpenGL

### Database non funziona
- Verifica i permessi di scrittura in `~/.dicom_reader/`
- Elimina il database corrotto: `rm ~/.dicom_reader/dicom_database.db`

## Sviluppi Futuri

- [ ] Supporto DICOM-RT (Radiotherapy)
- [ ] Misurazione distanze e aree
- [ ] Annotazioni e ROI
- [ ] Export immagini in formati standard (PNG, JPEG)
- [ ] Supporto DICOM Query/Retrieve (PACS)
- [ ] Plugin system per estensioni
- [ ] Report automatici
- [ ] Multi-language support

## Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file LICENSE per dettagli.

## Contributi

I contributi sono benvenuti! Per favore:
1. Fork il repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## Supporto

Per bug report e richieste di funzionalità, apri un issue su GitHub.

## Credits

Sviluppato con:
- [pydicom](https://github.com/pydicom/pydicom) - DICOM file handling
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [VTK](https://vtk.org/) - 3D visualization
- [OpenCV](https://opencv.org/) - Image processing

---

**DICOM Reader** - Visualizzazione e gestione professionale di immagini mediche DICOM
