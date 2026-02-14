-- Banking Database Schema for Warehouse SQL Assistant
-- Comprehensive banking data for analysis

-- Drop existing tables if they exist
DROP TABLE IF EXISTS loan_payments CASCADE;
DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS credit_card_transactions CASCADE;
DROP TABLE IF EXISTS credit_cards CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS branches CASCADE;

-- Branches table
CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    branch_code VARCHAR(10) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE NOT NULL,
    ssn VARCHAR(20) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    employment_status VARCHAR(20) CHECK (employment_status IN ('employed','unemployed','retired','student','self_employed')),
    annual_income DECIMAL(12,2),
    credit_score INTEGER CHECK (credit_score BETWEEN 300 AND 850),
    customer_segment VARCHAR(20) CHECK (customer_segment IN ('retail','premium','private_banking','business')),
    risk_category VARCHAR(10) CHECK (risk_category IN ('low','medium','high')),
    kyc_status VARCHAR(20) CHECK (kyc_status IN ('pending','approved','rejected','under_review')),
    branch_id INTEGER REFERENCES branches(branch_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type VARCHAR(30) CHECK (account_type IN ('checking','savings','money_market','certificate_deposit','business_checking','business_savings')),
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    interest_rate DECIMAL(5,4) DEFAULT 0.0000,
    minimum_balance DECIMAL(10,2) DEFAULT 0.00,
    account_status VARCHAR(20) CHECK (account_status IN ('active','inactive','closed','frozen','suspended')),
    overdraft_limit DECIMAL(10,2) DEFAULT 0.00,
    branch_id INTEGER REFERENCES branches(branch_id),
    opened_date DATE NOT NULL,
    closed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(account_id),
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('deposit','withdrawal','transfer_in','transfer_out','fee','interest','dividend','check','atm','online','mobile')),
    amount DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    description TEXT,
    transaction_date TIMESTAMP NOT NULL,
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(50),
    location VARCHAR(100),
    channel VARCHAR(20) CHECK (channel IN ('branch','atm','online','mobile','phone','check')),
    reference_number VARCHAR(50),
    status VARCHAR(20) CHECK (status IN ('pending','completed','failed','cancelled','reversed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit Cards table
CREATE TABLE credit_cards (
    card_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    card_number VARCHAR(16) UNIQUE NOT NULL,
    card_type VARCHAR(20) CHECK (card_type IN ('visa','mastercard','amex','discover')),
    card_category VARCHAR(30) CHECK (card_category IN ('basic','gold','platinum','rewards','cashback','business')),
    credit_limit DECIMAL(12,2) NOT NULL,
    current_balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    available_credit DECIMAL(12,2) NOT NULL,
    apr DECIMAL(5,2) NOT NULL,
    annual_fee DECIMAL(8,2) DEFAULT 0.00,
    card_status VARCHAR(20) CHECK (card_status IN ('active','inactive','blocked','expired','cancelled')),
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit Card Transactions table
CREATE TABLE credit_card_transactions (
    cc_transaction_id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES credit_cards(card_id),
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('purchase','cash_advance','payment','fee','interest','refund')),
    amount DECIMAL(12,2) NOT NULL,
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(50),
    transaction_date TIMESTAMP NOT NULL,
    location VARCHAR(100),
    reference_number VARCHAR(50),
    status VARCHAR(20) CHECK (status IN ('pending','completed','failed','disputed')),
    rewards_earned DECIMAL(8,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loans table
CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    loan_number VARCHAR(20) UNIQUE NOT NULL,
    loan_type VARCHAR(30) CHECK (loan_type IN ('personal','mortgage','auto','business','student','line_of_credit')),
    loan_amount DECIMAL(15,2) NOT NULL,
    outstanding_balance DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,4) NOT NULL,
    term_months INTEGER NOT NULL,
    monthly_payment DECIMAL(10,2) NOT NULL,
    loan_status VARCHAR(20) CHECK (loan_status IN ('active','paid_off','default','delinquent','restructured')),
    origination_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    next_payment_date DATE,
    payments_made INTEGER DEFAULT 0,
    last_payment_date DATE,
    collateral_value DECIMAL(15,2),
    ltv_ratio DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loan Payments table
CREATE TABLE loan_payments (
    payment_id SERIAL PRIMARY KEY,
    loan_id INTEGER REFERENCES loans(loan_id),
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    principal_amount DECIMAL(10,2) NOT NULL,
    interest_amount DECIMAL(10,2) NOT NULL,
    fee_amount DECIMAL(8,2) DEFAULT 0.00,
    payment_method VARCHAR(20) CHECK (payment_method IN ('auto_debit','online','branch','phone','check','mobile')),
    payment_status VARCHAR(20) CHECK (payment_status IN ('completed','pending','failed','returned')),
    late_fee DECIMAL(8,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_customers_segment ON customers(customer_segment);
CREATE INDEX idx_customers_risk ON customers(risk_category);
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_status ON accounts(account_status);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_cc_trans_date ON credit_card_transactions(transaction_date);
CREATE INDEX idx_loans_type ON loans(loan_type);
CREATE INDEX idx_loans_status ON loans(loan_status);
