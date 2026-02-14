#!/usr/bin/env python3
"""Seed schema embeddings into Qdrant for the RAG pipeline."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.embedding_service import EmbeddingService

SCHEMAS = [
    {
        "table_name": "branches",
        "ddl_statement": """CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    branch_code VARCHAR(10) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "Bank branch locations and contact information",
    },
    {
        "table_name": "customers",
        "ddl_statement": """CREATE TABLE customers (
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
    employment_status VARCHAR(20),
    annual_income DECIMAL(12,2),
    credit_score INTEGER,
    customer_segment VARCHAR(20),
    risk_category VARCHAR(10),
    kyc_status VARCHAR(20),
    branch_id INTEGER REFERENCES branches(branch_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "Customer demographics, employment, income, credit score, and risk data",
    },
    {
        "table_name": "accounts",
        "ddl_statement": """CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type VARCHAR(30),
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    interest_rate DECIMAL(5,4) DEFAULT 0.0000,
    minimum_balance DECIMAL(10,2) DEFAULT 0.00,
    account_status VARCHAR(20),
    overdraft_limit DECIMAL(10,2) DEFAULT 0.00,
    branch_id INTEGER REFERENCES branches(branch_id),
    opened_date DATE NOT NULL,
    closed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "Bank accounts (checking, savings, money market) with balances and types",
    },
    {
        "table_name": "transactions",
        "ddl_statement": """CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(account_id),
    transaction_type VARCHAR(20),
    amount DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    description TEXT,
    transaction_date TIMESTAMP NOT NULL,
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(50),
    location VARCHAR(100),
    channel VARCHAR(20),
    reference_number VARCHAR(50),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "All account transactions including deposits, withdrawals, transfers, and purchases",
    },
    {
        "table_name": "credit_cards",
        "ddl_statement": """CREATE TABLE credit_cards (
    card_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    card_number VARCHAR(16) UNIQUE NOT NULL,
    card_type VARCHAR(20),
    card_category VARCHAR(30),
    credit_limit DECIMAL(12,2) NOT NULL,
    current_balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    available_credit DECIMAL(12,2) NOT NULL,
    apr DECIMAL(5,2) NOT NULL,
    annual_fee DECIMAL(8,2) DEFAULT 0.00,
    card_status VARCHAR(20),
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "Credit card information including type, limit, balance, and APR",
    },
    {
        "table_name": "credit_card_transactions",
        "ddl_statement": """CREATE TABLE credit_card_transactions (
    cc_transaction_id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES credit_cards(card_id),
    transaction_type VARCHAR(20),
    amount DECIMAL(12,2) NOT NULL,
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(50),
    transaction_date TIMESTAMP NOT NULL,
    location VARCHAR(100),
    reference_number VARCHAR(50),
    status VARCHAR(20),
    rewards_earned DECIMAL(8,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "Credit card transaction history including purchases, payments, and rewards",
    },
    {
        "table_name": "loans",
        "ddl_statement": """CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    loan_number VARCHAR(20) UNIQUE NOT NULL,
    loan_type VARCHAR(30),
    loan_amount DECIMAL(15,2) NOT NULL,
    outstanding_balance DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,4) NOT NULL,
    term_months INTEGER NOT NULL,
    monthly_payment DECIMAL(10,2) NOT NULL,
    loan_status VARCHAR(20),
    origination_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    next_payment_date DATE,
    payments_made INTEGER DEFAULT 0,
    last_payment_date DATE,
    collateral_value DECIMAL(15,2),
    ltv_ratio DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "Loans including mortgage, personal, auto, and business with terms and status",
    },
    {
        "table_name": "loan_payments",
        "ddl_statement": """CREATE TABLE loan_payments (
    payment_id SERIAL PRIMARY KEY,
    loan_id INTEGER REFERENCES loans(loan_id),
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    principal_amount DECIMAL(10,2) NOT NULL,
    interest_amount DECIMAL(10,2) NOT NULL,
    fee_amount DECIMAL(8,2) DEFAULT 0.00,
    payment_method VARCHAR(20),
    payment_status VARCHAR(20),
    late_fee DECIMAL(8,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        "description": "Loan payment records with principal/interest breakdown and payment method",
    },
]


def main():
    print("🔄 Seeding schema embeddings into Qdrant...")
    svc = EmbeddingService()
    svc.embed_all_schemas(SCHEMAS)
    print(f"✅ Embedded {len(SCHEMAS)} table schemas successfully!")
    stored = svc.get_all_schemas()
    print(f"📊 Verified {len(stored)} schemas in Qdrant")


if __name__ == "__main__":
    main()
