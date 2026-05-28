-- ==========================================
-- RISKSAARTHI DATABASE SCHEMA
-- ==========================================

CREATE DATABASE IF NOT EXISTS risksaarthi;
USE risksaarthi;

-- ==========================================
-- 1. ML TRAINING DATASET
-- ==========================================

CREATE TABLE IF NOT EXISTS loan_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    age INT NOT NULL,
    annual_income INT NOT NULL,
    cibil_score INT NOT NULL,
    employment_type VARCHAR(50),
    loan_amount INT NOT NULL,
    loan_tenure INT NOT NULL,
    emi INT NOT NULL,
    existing_loans INT NOT NULL,
    `default` TINYINT(1)
);

-- ==========================================
-- 2. USERS
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 3. LOAN APPLICATIONS
-- ==========================================

CREATE TABLE IF NOT EXISTS loan_applications (
    application_id VARCHAR(50) PRIMARY KEY,

    applicant_id VARCHAR(256) NOT NULL,   -- hashed-based unique ID
    identity_type ENUM('AADHAAR','PAN') NOT NULL,
    identity_hash VARCHAR(256) NOT NULL,

    user_id VARCHAR(50),

    age INT NOT NULL,
    annual_income DECIMAL(12,2) NOT NULL,
    cibil_score INT NOT NULL,
    employment_type VARCHAR(50),

    loan_amount DECIMAL(12,2) NOT NULL,
    emi DECIMAL(12,2),
    loan_tenure INT NOT NULL,
    interest_rate DECIMAL(5,2),

    application_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);

-- ==========================================
-- 4. MODEL METADATA
-- ==========================================

CREATE TABLE IF NOT EXISTS model_metadata (
    model_id VARCHAR(50) PRIMARY KEY,

    model_name VARCHAR(100) NOT NULL,
    algorithm_type VARCHAR(50),

    accuracy DECIMAL(6,4),
    f1_score DECIMAL(6,4),
    roc_auc DECIMAL(6,4),

    version VARCHAR(20),

    training_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 5. PREDICTION RESULTS
-- ==========================================

CREATE TABLE IF NOT EXISTS prediction_results (

    prediction_id VARCHAR(50) PRIMARY KEY,
    application_id VARCHAR(50) NOT NULL,
    model_id VARCHAR(50) NOT NULL,

    default_probability DECIMAL(6,4),
    risk_category VARCHAR(20),
    credit_score INT,
    loan_decision VARCHAR(20),

    foir DECIMAL(6,2),
    emi DECIMAL(10,2),

    explanation_text TEXT,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prediction_application
        FOREIGN KEY (application_id)
        REFERENCES loan_applications(application_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_prediction_model
        FOREIGN KEY (model_id)
        REFERENCES model_metadata(model_id)
);

-- ==========================================
-- 6. CONTACT US MESSAGES
-- ==========================================

CREATE TABLE contact_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    name VARCHAR(100),
    email VARCHAR(150),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);