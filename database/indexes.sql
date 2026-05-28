USE risksaarthi;

-- USERS
CREATE INDEX idx_users_email ON users(email);

-- LOAN APPLICATIONS
CREATE INDEX idx_loan_user ON loan_applications(user_id);
CREATE INDEX idx_loan_cibil ON loan_applications(cibil_score);
CREATE INDEX idx_application_time ON loan_applications(application_time);

-- NEW INDEXES (IDENTITY SYSTEM)
CREATE INDEX idx_identity_hash ON loan_applications(identity_hash);
CREATE INDEX idx_identity_type ON loan_applications(identity_type);
CREATE INDEX idx_applicant_id ON loan_applications(applicant_id);

-- MODEL METADATA
CREATE INDEX idx_model_name ON model_metadata(model_name);
CREATE INDEX idx_model_version ON model_metadata(version);

-- PREDICTION RESULTS
CREATE INDEX idx_prediction_application ON prediction_results(application_id);
CREATE INDEX idx_prediction_model ON prediction_results(model_id);
CREATE INDEX idx_risk_category ON prediction_results(risk_category);
CREATE INDEX idx_loan_decision ON prediction_results(loan_decision);
CREATE INDEX idx_prediction_time ON prediction_results(prediction_time);
CREATE INDEX idx_foir ON prediction_results(foir);
CREATE INDEX idx_emi ON prediction_results(emi);

-- Composite Index
CREATE INDEX idx_risk_decision_time
ON prediction_results(risk_category, loan_decision, prediction_time);

-- ML DATASET
CREATE INDEX idx_loan_data_cibil ON loan_data(cibil_score);
CREATE INDEX idx_loan_data_income ON loan_data(annual_income);
CREATE INDEX idx_loan_data_default ON loan_data(`default`);

-- CONTACT
CREATE INDEX idx_contact_user_id ON contact_messages(user_id);
CREATE INDEX idx_contact_created_at ON contact_messages(created_at);
CREATE INDEX idx_contact_email ON contact_messages(email);