PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS hospitals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'actiu'
                            CHECK(status IN ('actiu','inactiu','potencial')),
    color           TEXT    NOT NULL DEFAULT '#2563d4',
    contacte        TEXT    NOT NULL DEFAULT '',
    observacions    TEXT    NOT NULL DEFAULT '',
    lat             REAL    NOT NULL,
    lng             REAL    NOT NULL,
    creat_el        TEXT    NOT NULL DEFAULT (datetime('now')),
    actualitzat_el  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS doctors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT    NOT NULL,
    especialitat    TEXT    NOT NULL DEFAULT '',
    email           TEXT    NOT NULL DEFAULT '',
    telefon         TEXT    NOT NULL DEFAULT '',
    institucio      TEXT    NOT NULL DEFAULT '',
    linkedin        TEXT    NOT NULL DEFAULT '',
    observacions    TEXT    NOT NULL DEFAULT '',
    hospital_id     INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    creat_el        TEXT    NOT NULL DEFAULT (datetime('now')),
    actualitzat_el  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS projectes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT    NOT NULL,
    tema            TEXT    NOT NULL DEFAULT '',
    status          TEXT    NOT NULL DEFAULT 'actiu'
                            CHECK(status IN ('actiu','inactiu','completat')),
    observacions    TEXT    NOT NULL DEFAULT '',
    hospital_id     INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    creat_el        TEXT    NOT NULL DEFAULT (datetime('now')),
    actualitzat_el  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS doctor_projecte (
    doctor_id   INTEGER NOT NULL REFERENCES doctors(id)   ON DELETE CASCADE,
    projecte_id INTEGER NOT NULL REFERENCES projectes(id) ON DELETE CASCADE,
    PRIMARY KEY (doctor_id, projecte_id)
);

CREATE INDEX IF NOT EXISTS idx_doctors_hospital   ON doctors(hospital_id);
CREATE INDEX IF NOT EXISTS idx_projectes_hospital ON projectes(hospital_id);
CREATE INDEX IF NOT EXISTS idx_dp_doctor          ON doctor_projecte(doctor_id);
CREATE INDEX IF NOT EXISTS idx_dp_projecte        ON doctor_projecte(projecte_id);
