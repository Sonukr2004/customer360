# BNP-BLR-Team-24

backend/
│
├── ingestion/
│   ├── file_validator.py
│   ├── schema_validator.py
│   └── loader.py
│
├── cleaning/
│   ├── name_cleaner.py
│   ├── email_cleaner.py
│   ├── phone_cleaner.py
│   └── null_handler.py
│
├── standardization/
│   └── address_standardizer.py
│
├── matching/
│   ├── exact_matcher.py
│   ├── fuzzy_matcher.py
│   └── scorer.py
│
├── resolution/
│   └── entity_resolver.py
│
├── survivorship/
│   ├── hierarchy_loader.py
│   └── survivor_engine.py
│
├── golden_record/
│   └── golden_record_service.py
│
├── linking/
│   ├── product_linker.py
│   └── transaction_linker.py
│
├── lineage/
│   └── lineage_service.py
│
├── quality/
│   └── quality_score.py
│
├── api/
│   ├── customer_routes.py
│   ├── product_routes.py
│   └── transaction_routes.py
│
├── models/
├── schemas/
├── database/
└── tests/


frontend/
│
├── pages/
│   ├── Dashboard
│   └── Customer360
│
├── components/
│   ├── CustomerTable
│   ├── CustomerSearch
│   ├── GoldenRecord
│   ├── ProductPortfolio
│   ├── TransactionTimeline
│   ├── SourceTrace
│   └── EditCustomerModal
│
├── services/
│   └── api.js
│
└── hooks/

PostgreSQL
│
├── raw_records
├── cleaned_records
├── master_customers
├── identity_map
├── customer_products
├── transactions
├── field_lineage
└── audit_log
