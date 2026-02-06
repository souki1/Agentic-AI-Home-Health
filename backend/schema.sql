-- PostgreSQL schema for Health Analytics.
-- Tables are also created by the app on startup via SQLAlchemy create_all.
-- Run this manually in Cloud SQL if you want the schema before the app starts.
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patients (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    condition VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS check_ins (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL REFERENCES patients(id),
    date TIMESTAMPTZ NOT NULL,
    fatigue FLOAT DEFAULT 0,
    breathlessness FLOAT DEFAULT 0,
    cough FLOAT DEFAULT 0,
    pain FLOAT DEFAULT 0,
    nausea FLOAT DEFAULT 0,
    dizziness FLOAT DEFAULT 0,
    swelling FLOAT DEFAULT 0,
    anxiety FLOAT DEFAULT 0,
    headache FLOAT DEFAULT 0,
    chest_tightness FLOAT DEFAULT 0,
    joint_stiffness FLOAT DEFAULT 0,
    skin_issues FLOAT DEFAULT 0,
    constipation FLOAT DEFAULT 0,
    bloating FLOAT DEFAULT 0,
    sleep_hours FLOAT DEFAULT 0,
    meds_taken BOOLEAN DEFAULT TRUE,
    appetite VARCHAR(20) DEFAULT 'Normal',
    mobility VARCHAR(20) DEFAULT 'Normal',
    devices TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS ix_check_ins_patient_id ON check_ins(patient_id);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
