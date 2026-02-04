-- Users (and patients: role = 'patient')
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    name VARCHAR(255),
    age INTEGER,
    condition VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- Check-ins (symptom and device readings per day per patient)
CREATE TABLE IF NOT EXISTS check_ins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    date VARCHAR(10) NOT NULL,
    fatigue DOUBLE PRECISION NOT NULL DEFAULT 0,
    breathlessness DOUBLE PRECISION NOT NULL DEFAULT 0,
    cough DOUBLE PRECISION NOT NULL DEFAULT 0,
    pain DOUBLE PRECISION NOT NULL DEFAULT 0,
    nausea DOUBLE PRECISION NOT NULL DEFAULT 0,
    dizziness DOUBLE PRECISION NOT NULL DEFAULT 0,
    swelling DOUBLE PRECISION NOT NULL DEFAULT 0,
    anxiety DOUBLE PRECISION NOT NULL DEFAULT 0,
    headache DOUBLE PRECISION NOT NULL DEFAULT 0,
    chest_tightness DOUBLE PRECISION NOT NULL DEFAULT 0,
    joint_stiffness DOUBLE PRECISION NOT NULL DEFAULT 0,
    skin_issues DOUBLE PRECISION NOT NULL DEFAULT 0,
    constipation DOUBLE PRECISION NOT NULL DEFAULT 0,
    bloating DOUBLE PRECISION NOT NULL DEFAULT 0,
    sleep_hours DOUBLE PRECISION NOT NULL DEFAULT 7,
    meds_taken BOOLEAN NOT NULL DEFAULT TRUE,
    appetite VARCHAR(20) NOT NULL DEFAULT 'Normal',
    mobility VARCHAR(20) NOT NULL DEFAULT 'Normal',
    devices JSONB,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS ix_check_ins_patient_id ON check_ins (patient_id);
CREATE INDEX IF NOT EXISTS ix_check_ins_date ON check_ins (date);
