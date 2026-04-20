# MSL Mapa — Arquitectura i Especificacions Tècniques

## Visió general

MSL Mapa és una aplicació d'escriptori Python per gestionar hospitals, doctors i projectes a la Península Ibèrica. L'usuari interactua principalment mitjançant un mapa interactiu i quatre pestanyes de llista amb cerca.

**Tecnologies principals:**
- **Python 3.10+** — llenguatge de programació
- **PyQt6** — interfície gràfica d'escriptori (widgets, finestres, diàlegs)
- **PyQt6-WebEngine** — navegador integrat per mostrar el mapa Leaflet
- **SQLite** — base de dades local, un sol fitxer `.db`
- **openpyxl** — exportació a format Excel (`.xlsx`)
- **requests** — cerca d'adreces via API Nominatim (OpenStreetMap)

---

## Instal·lació i execució

```bash
# 1. Crea un entorn virtual (recomanat)
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

# 2. Instal·la les dependències
pip install -r requirements.txt

# 3. (Primera vegada) Migra les dades del JSON existent
python utils/migrate_json.py

# 4. Llença l'aplicació
python main.py
```

La base de dades es crea automàticament a `msl_data.db` al directori arrel del projecte la primera vegada que s'executa l'app.

---

## Estructura de fitxers

```
msl_mapa/
├── main.py                      ← punt d'entrada
├── requirements.txt
├── msl_data.db                  ← base de dades SQLite (es crea sola)
│
├── database/
│   ├── schema.sql               ← definició de taules (s'executa 1 vegada)
│   └── db.py                    ← DatabaseManager: TOT el codi SQL va aquí
│
├── models/
│   ├── hospital.py              ← dataclass Hospital (dades pures, sense UI)
│   ├── doctor.py                ← dataclass Doctor
│   └── projecte.py              ← dataclass Projecte
│
├── ui/
│   ├── main_window.py           ← finestra principal amb les pestanyes
│   ├── map_widget.py            ← pestanya del mapa (Leaflet integrat)
│   ├── hospital_dialog.py       ← diàleg modal per editar un hospital
│   ├── tab_hospitals.py         ← pestanya llista d'hospitals
│   ├── tab_doctors.py           ← pestanya llista de doctors
│   ├── tab_projectes.py         ← pestanya llista de projectes
│   └── tab_about.py             ← pestanya "Quant a"
│
├── assets/
│   ├── map_template.html        ← pàgina HTML del mapa (Leaflet)
│   └── leaflet/
│       ├── leaflet.js           ← biblioteca de mapes (bundlejada, offline)
│       └── leaflet.css
│
└── utils/
    ├── export.py                ← ExcelExporter amb openpyxl
    ├── geocoder.py              ← cerca d'adreces via Nominatim
    └── migrate_json.py          ← migració única des del JSON original
```

---

## El patró MVC (Model-Vista-Controlador) explicat simplement

Si coneixes R Shiny, la idea és similar: separes les dades de la interfície.

### Analogia amb R

| R / Shiny | Python / PyQt6 |
|-----------|---------------|
| Data frame, tibble | `models/hospital.py` (dataclass) |
| Funcions `reactive()` | Senyals i slots de PyQt6 |
| `renderTable()`, `renderPlot()` | Widgets de la capa `ui/` |
| Connexió a BD amb `DBI` | `database/db.py` (DatabaseManager) |

### Les tres capes

**1. Model — "les dades"** (`database/`, `models/`)

El `DatabaseManager` a `db.py` és l'únic que parla amb SQLite. Les dataclasses (`Hospital`, `Doctor`, `Projecte`) són simples contenidors de dades, com named tuples però millors. Cap d'aquestes classes sap res de botons ni finestres.

```python
# Exemple: obtenir tots els hospitals
db = DatabaseManager("msl_data.db")
hospitals = db.get_all_hospitals()   # retorna List[Hospital]
```

**2. Vista — "la interfície"** (`ui/`)

Cada fitxer de `ui/` conté una classe que hereta d'un widget de PyQt6. Mostren dades però **no fan consultes SQL directament** — reben els dades ja preparades.

**3. Connexió — senyals i slots**

Un **senyal** és com un event d'R: "ha passat quelcom". Un **slot** és la funció que reacciona. Es connecten explícitament amb `.connect()`.

```python
# Exemple: quan l'usuari fa clic a un pin del mapa,
# MainWindow obre el diàleg d'edició
map_widget.hospital_clicked.connect(main_window.obrir_hospital)
```

La diferència clau amb R: en PyQt6, tu defineixes els senyals manualment i els connectes tu. No és reactiu automàticament.

---

## Model de dades

### Diagrama de relacions

```
hospitals (1) ─────── (N) doctors
    │                      │
    │                      │ (N:M via doctor_projecte)
    │                      │
    └──────── (N) projectes
```

- Un **hospital** pot tenir molts doctors i molts projectes.
- Un **doctor** pertany a un únic hospital (restricció de disseny).
- Un **projecte** pertany a un únic hospital.
- Un doctor pot participar en múltiples projectes del seu hospital.
- Un projecte pot tenir múltiples doctors (tots del mateix hospital).

### Taules SQLite

#### `hospitals`
| Camp | Tipus | Descripció |
|------|-------|-----------|
| id | INTEGER PK | Identificador únic (autoincrement) |
| nom | TEXT | Nom de l'hospital |
| status | TEXT | `actiu` / `inactiu` / `potencial` |
| color | TEXT | Color del pin al mapa (hex, e.g. `#2563d4`) |
| contacte | TEXT | Informació de contacte (text lliure) |
| observacions | TEXT | Notes addicionals |
| lat | REAL | Latitud geogràfica |
| lng | REAL | Longitud geogràfica |
| creat_el | TEXT | Data de creació (ISO 8601) |
| actualitzat_el | TEXT | Data de darrera modificació |

#### `doctors`
| Camp | Tipus | Descripció |
|------|-------|-----------|
| id | INTEGER PK | Identificador únic |
| nom | TEXT | Nom complet |
| especialitat | TEXT | Especialitat mèdica |
| email | TEXT | Correu electrònic |
| telefon | TEXT | Telèfon |
| institucio | TEXT | Institució / centre |
| linkedin | TEXT | URL de LinkedIn |
| observacions | TEXT | Notes |
| hospital_id | INTEGER FK | Hospital al qual pertany |
| creat_el | TEXT | Data de creació |
| actualitzat_el | TEXT | Data de darrera modificació |

#### `projectes`
| Camp | Tipus | Descripció |
|------|-------|-----------|
| id | INTEGER PK | Identificador únic |
| nom | TEXT | Nom del projecte |
| tema | TEXT | Àrea temàtica |
| status | TEXT | `actiu` / `inactiu` / `completat` |
| observacions | TEXT | Notes |
| hospital_id | INTEGER FK | Hospital al qual pertany |
| creat_el | TEXT | Data de creació |
| actualitzat_el | TEXT | Data de darrera modificació |

#### `doctor_projecte` (taula de relació N:M)
| Camp | Tipus | Descripció |
|------|-------|-----------|
| doctor_id | INTEGER FK | Referència a `doctors.id` |
| projecte_id | INTEGER FK | Referència a `projectes.id` |

---

## Integració del mapa

### Per què QWebEngineView?

PyQt6 no té un widget de mapes natiu. La solució estàndard és embeddar un navegador Chromium (`QWebEngineView`) que carrega una pàgina HTML amb Leaflet.js — la mateixa biblioteca que usa l'aplicació original.

### Comunicació bidireccional Python ↔ JavaScript

El mecanisme s'anomena **QWebChannel**. Funciona com un pont:

```
Python (MapWidget)  ←──────────────→  JavaScript (map_template.html)
                       QWebChannel
```

**Python → JavaScript** (actualitzar pins):
```python
# Enviar la llista d'hospitals al mapa
data = json.dumps([{"id": h.id, "lat": h.lat, ...} for h in hospitals])
self.web_view.page().runJavaScript(f"setHospitals({data})")
```

**JavaScript → Python** (l'usuari ha clicat un pin):
```javascript
// A map_template.html
pyBridge.on_js_message(JSON.stringify({type: "pin_click", hospital_id: 3}))
```

```python
# A map_widget.py — el mètode que rep el missatge
@pyqtSlot(str)
def on_js_message(self, message: str):
    data = json.loads(message)
    if data["type"] == "pin_click":
        self.hospital_clicked.emit(data["hospital_id"])
```

### Per què Leaflet bundlejat?

Els fitxers `leaflet.js` i `leaflet.css` es copien localment a `assets/leaflet/`. Això permet que l'app funcioni sense connexió a internet. Les tessel·les del mapa (imatge de fons) sí requereixen internet perquè vénen de CARTO.

---

## Flux d'interacció principal

### Clic en un pin del mapa (editar hospital)

```
Usuari clica pin
  → JavaScript emet event al pont QWebChannel
  → MapWidget.on_js_message() rep el missatge
  → MapWidget emet el senyal hospital_clicked(id)
  → MainWindow.on_hospital_selected(id) s'activa
  → Consulta db.get_hospital(id) → objecte Hospital
  → Obre HospitalDialog(hospital) com a modal
  → Usuari edita i prem "Guardar"
  → HospitalDialog crida db.save_hospital(hospital)
  → MainWindow.refresh_all() s'executa
  → Tots els tabs i el mapa es recarreguen
```

### Clic al mapa buit (afegir hospital)

```
Usuari clica en zona buida del mapa
  → JavaScript envia {type: "map_click", lat: X, lng: Y}
  → MapWidget emet map_clicked_empty(lat, lng)
  → MainWindow obre HospitalDialog(None, lat=X, lng=Y)
  → Usuari omple el formulari i prem "Guardar"
  → db.save_hospital() → nou hospital creat
  → refresh_all() → nou pin apareix al mapa
```

---

## DatabaseManager — referència ràpida

Totes les operacions de dades passen per `DatabaseManager` a `database/db.py`:

```python
db = DatabaseManager("msl_data.db")

# Hospitals
db.get_all_hospitals() → List[Hospital]
db.get_hospital(id) → Hospital
db.save_hospital(hospital) → int (id)    # INSERT o UPDATE automàtic
db.delete_hospital(id) → None

# Doctors
db.get_doctors_for_hospital(hospital_id) → List[Doctor]
db.save_doctor(doctor) → int
db.delete_doctor(id) → None

# Projectes
db.get_projectes_for_hospital(hospital_id) → List[Projecte]
db.save_projecte(projecte) → int
db.delete_projecte(id) → None

# Relacions doctor-projecte
db.link_doctor_projecte(doctor_id, projecte_id) → None
db.unlink_doctor_projecte(doctor_id, projecte_id) → None
db.get_projectes_for_doctor(doctor_id) → List[int]  # llista d'ids

# Cerca creuada (per als tabs de llista)
db.search_hospitals(query: str) → List[dict]
db.search_doctors(query: str) → List[dict]
db.search_projectes(query: str) → List[dict]
```

---

## Senyals i slots — referència ràpida

| Classe | Senyal | Connectat a |
|--------|--------|------------|
| `MapWidget` | `hospital_clicked(int)` | `MainWindow.on_hospital_selected` |
| `MapWidget` | `map_clicked_empty(float, float)` | `MainWindow.on_map_clicked_empty` |
| `HospitalsTab` | `hospital_selected(int)` | `MapWidget.pan_to_hospital` |
| `HospitalDialog` | (modal exec) | `MainWindow.refresh_all` (post-tancament) |

---

## Preguntes freqüents

**Q: On s'emmagatzema la base de dades?**
A: A `msl_data.db` al directori arrel del projecte. És un fitxer portàtil que pots copiar, fer còpia de seguretat o compartir.

**Q: Com faig una còpia de seguretat?**
A: Simplement copia `msl_data.db`. És un fitxer SQLite estàndard, llegible amb [DB Browser for SQLite](https://sqlitebrowser.org/) (gratuït).

**Q: El mapa necessita internet?**
A: Les tessel·les de fons (la imatge cartogràfica) requereixen internet. La lògica de pins i interacció funciona offline. Si no hi ha internet, el mapa apareixerà en gris però els pins i les funcions funcionaran.

**Q: Com afegeixo nous camps a una taula?**
A: Modifica `schema.sql`, actualitza la dataclass corresponent a `models/`, actualitza els mètodes de `db.py`, i actualitza els formularis de `ui/`. SQLite permet fer `ALTER TABLE ... ADD COLUMN` per migrar dades existents sense recrear la taula.

**Q: Puc importar dades del JSON original?**
A: Sí. Executa `python utils/migrate_json.py` i segueix les instruccions. Aquest script és segur d'executar més d'una vegada (comprova si les dades ja existeixen).
