# Customer 360 — Data Integration & Master Data Management

A data integration and customer master-data platform that consolidates fragmented customer records from multiple banking systems into a unified **Customer 360** view.

The system ingests data from Core Banking, Credit Card, and Loan systems, identifies records belonging to the same real-world customer, resolves conflicting attributes using a defined **trust hierarchy**, and provides a consolidated customer profile with data-quality visibility.

---

## Overview

Large financial institutions typically have customer information distributed across multiple systems.

A single customer may appear as:

* `C0001` in Core Banking
* `CC_243` in Credit Card
* `L_817` in the Loan System

These identifiers do not necessarily identify different people.

The core problem is therefore:

> **How do we determine which records represent the same real-world customer and construct one trusted customer profile from them?**

This project addresses that problem through:

1. **Data ingestion**
2. **Data normalization**
3. **Entity resolution / customer matching**
4. **Master ID creation**
5. **Survivorship and conflict resolution**
6. **Data-quality analysis**
7. **Customer 360 visualization**
8. **Transaction and financial relationship aggregation**

---

# Problem Statement

Banking data is often fragmented across independent systems.

Different systems may contain:

* Different customer IDs
* Different spellings of names
* Different address formats
* Different phone numbers
* Different email addresses
* Duplicate records
* Missing attributes
* Conflicting attributes

For example:

```text
Core Banking
--------------------------------
Customer_ID : C0001
Name        : Kara Randy Clark
Email       : karac@gmail.com
Phone       : 9971674338
DOB         : 1959-03-22


Credit Card
--------------------------------
Cust_Ref    : CC_243
Name        : Kara R. Clark
Email       : karac@gmail.com
Phone       : 9971674338


Loan System
--------------------------------
Loan_Cust_ID: L_817
Name        : Kara Randy Clark
Phone       : 9971674338
```

These records may belong to the same person even though their source-system identifiers are different.

The platform converts these fragmented records into a unified master representation:

```text
                    ┌──────────────────┐
                    │   MASTER CUSTOMER │
                    │      M00475       │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   Core Banking        Credit Card        Loan System
      C0001              CC_243              L_817
```

---

# Goals

The system is designed to:

* Consolidate customer records from multiple banking systems.
* Detect duplicate or matching customer records.
* Assign a unique Master Customer ID.
* Resolve conflicting attributes.
* Apply source-specific trust rules.
* Preserve source-system identifiers.
* Provide a unified Customer 360 profile.
* Track financial relationships and transactions.
* Measure data quality.
* Make the matching and survivorship process explainable.

---

# Architecture

The system follows a pipeline architecture:

```text
                    SOURCE SYSTEMS
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
 Core Banking       Credit Card       Loan System
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                  DATA INGESTION
                         │
                         ▼
                  NORMALIZATION
                         │
                         ▼
                 ENTITY RESOLUTION
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
        Exact Matching        Fuzzy Matching
        Email / Phone             Name
             │                       │
             └───────────┬───────────┘
                         ▼
                 MASTER CUSTOMER ID
                         │
                         ▼
                  SURVIVORSHIP
                         │
                         ▼
              CUSTOMER 360 DATABASE
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
          Customer     Quality   Transactions
            360        Dashboard
```

---

# Data Sources

The supplied dataset contains five primary data files and supporting metadata.

## 1. Core Banking

File:

```text
core_banking.csv
```

Columns:

| Column        | Description                      |
| ------------- | -------------------------------- |
| `Customer_ID` | Core Banking customer identifier |
| `Name`        | Customer name                    |
| `Email`       | Customer email                   |
| `Phone`       | Customer phone number            |
| `DOB`         | Date of birth                    |
| `Address`     | Customer address                 |

Dataset size:

```text
1,560 records
```

---

## 2. Credit Card

File:

```text
credit_card.csv
```

Columns:

| Column         | Description                     |
| -------------- | ------------------------------- |
| `Cust_Ref`     | Credit-card customer identifier |
| `Name`         | Customer name                   |
| `Email`        | Customer email                  |
| `Phone`        | Customer phone number           |
| `Credit_Limit` | Credit-card credit limit        |
| `Address`      | Customer address                |

Dataset size:

```text
975 records
```

---

## 3. Loan System

File:

```text
loan_system.csv
```

Columns:

| Column         | Description                     |
| -------------- | ------------------------------- |
| `Loan_Cust_ID` | Loan-system customer identifier |
| `Name`         | Customer name                   |
| `Phone`        | Customer phone number           |
| `Loan_Amt`     | Loan amount                     |
| `Address`      | Customer address                |

Dataset size:

```text
580 records
```

The same loan data is also supplied in:

```text
loan_system.jsonl
```

with 580 records.

---

## 4. Transaction Data

File:

```text
transaction_data.csv
```

Columns:

| Column       | Description                       |
| ------------ | --------------------------------- |
| `Txn_ID`     | Transaction identifier            |
| `Account_ID` | Source account/customer reference |
| `Amount`     | Transaction amount                |
| `Date`       | Transaction date                  |
| `Type`       | Credit or Debit                   |

Dataset size:

```text
6,841 transactions
```

`Account_ID` can reference identifiers from the source systems.

---

## 5. Reference Data

File:

```text
reference_data.csv
```

This file provides normalization mappings such as:

```text
Short_Form    Long_Form
St.           Street
Rd.           Road
```

It can be used during address normalization.

---

# Ground Truth

File:

```text
ground_truth_mapping.csv
```

The ground-truth dataset contains known relationships between source-system records.

Dataset size:

```text
63 master-customer mappings
```

It contains:

```text
Master_ID
Core_Banking_Customer_ID
Core_Banking_Duplicate_IDs
Credit_Card_Cust_Ref
Loan_Cust_ID
Email_Exact_Match_CC_vs_Core
True_Name
True_DOB
True_Phone
```

Ground truth is useful for evaluating the entity-resolution algorithm.

For example:

```text
Master_ID: M00475

Core Banking : C0001
Credit Card  : CC_243
Loan         : L_817
```

This establishes that these source records correspond to the same master customer.

---

# Customer Identity Resolution

The most important part of the system is determining whether two records represent the same real-world customer.

The matching process uses two categories of signals.

## Exact Matching

The supplied trust hierarchy defines:

```json
"exact_match_fields": [
  "Email",
  "Phone"
]
```

Therefore, normalized email and phone values can provide strong identity signals.

Example:

```text
Record A
Email = person@example.com

Record B
Email = person@example.com
```

This is an exact email match.

Similarly:

```text
Record A
Phone = 9876543210

Record B
Phone = 9876543210
```

is an exact phone match.

---

# Fuzzy Matching

Names are handled differently.

The trust hierarchy defines:

```json
"fuzzy_match_fields": [
  "Name"
]
```

with:

```json
"fuzzy_threshold": 0.85
```

Therefore, names should not simply be compared using exact string equality.

Examples of potentially equivalent names:

```text
Kara Randy Clark
Kara R. Clark
KARA RANDY CLARK
```

A normalized/fuzzy comparison can determine whether two names are sufficiently similar.

The configured threshold is:

```text
0.85
```

---

# Matching Strategy

A practical matching pipeline is:

```text
Raw Record
     │
     ▼
Normalize Fields
     │
     ├── Email normalization
     ├── Phone normalization
     ├── Name normalization
     └── Address normalization
     │
     ▼
Exact Match?
     │
   ┌─┴─┐
  YES  NO
   │    │
   │    ▼
   │  Fuzzy Name Match
   │    │
   │    ▼
   │  Score >= 0.85?
   │    │
   └────┤
        ▼
   Same Customer?
        │
        ▼
   Master Customer
```

The exact implementation may combine multiple signals rather than relying on a single field.

---

# Normalization

Matching raw strings directly is unreliable.

The system should normalize values before comparison.

## Name Normalization

Typical operations include:

```text
"Kara Randy Clark"
"KARA RANDY CLARK"
"Kara  Randy   Clark"
```

→

```text
kara randy clark
```

Normalization can include:

* Lowercasing
* Whitespace normalization
* Punctuation handling
* Removal of unnecessary formatting

---

## Email Normalization

Example:

```text
"KaraC@gmail.com"
```

can be normalized to a consistent representation before matching.

The objective is to compare equivalent values rather than formatting differences.

---

## Phone Normalization

Phone numbers should be reduced to a consistent comparable representation.

Example:

```text
+91 98765 43210
919876543210
9876543210
```

may require country-code and formatting normalization depending on the source data.

---

## Address Normalization

The supplied reference data provides mappings such as:

```text
St. → Street
Rd. → Road
```

This allows different textual representations to be normalized before comparison.

---

# Survivorship Rules

Finding that records belong to the same customer is only half of the problem.

The next question is:

> When multiple systems contain different values for the same customer, which value should become the master value?

The supplied `trust_hierarchy.json` defines the survivorship rules.

The configured priorities are:

### Phone

```text
SourceA > SourceB > SourceC
```

### Email

```text
SourceB > SourceA > SourceC
```

### Name

```text
SourceA > SourceB > SourceC
```

### Address

```text
SourceB > SourceA > SourceC
```

### DOB

```text
SourceA > SourceB > SourceC
```

The important point is that **trust is field-specific**.

The system should not assume that one source is universally authoritative.

For example:

```text
Email:
SourceB > SourceA > SourceC
```

while:

```text
Name:
SourceA > SourceB > SourceC
```

This allows the master record to select the most trusted value independently for each attribute.

---

# Source Mapping

The three source systems are conceptually mapped to:

```text
SourceA → Core Banking
SourceB → Credit Card
SourceC → Loan System
```

This mapping allows the supplied trust hierarchy to be applied consistently across the source systems.

---

# Master Customer Record

After matching and survivorship, each real-world customer receives a stable master identifier.

Example:

```text
Master_ID
---------
M00475
```

The master customer can then maintain relationships with all source records:

```text
Master Customer
M00475

├── Core Banking
│   └── C0001
│
├── Credit Card
│   └── CC_243
│
└── Loan System
    └── L_817
```

This creates a cross-system identity layer.

---

# Customer 360

The Customer 360 page combines information from all available systems.

A conceptual customer profile can contain:

```text
Customer
────────────────────────────
Master ID       M00475
Name            Kara Randy Clark
DOB             22/03/1959
Phone           9971674338
Email           karac@gmail.com
Address         ...

Relationships
────────────────────────────
Core Banking    C0001
Credit Card     CC_243
Loan            L_817

Financial Data
────────────────────────────
Credit Limit    ...
Loan Amount     ...
Transactions    ...
```

The objective is to provide one place where an institution can understand a customer's relationships across systems.

---

# Data Quality

The platform also exposes data-quality information.

Important dimensions include:

### Completeness

Are required fields populated?

```text
Email present?
Phone present?
DOB present?
Address present?
```

### Consistency

Do different systems contain conflicting information?

```text
Core Banking:
Phone = A

Credit Card:
Phone = B
```

### Uniqueness

Are multiple source records potentially representing the same customer?

### Validity

Do values follow expected formats?

Examples:

```text
Valid email
Valid phone
Valid date
```

### Accuracy

Where ground truth exists, matching results can be compared against the known mapping.

---

# Quality Evaluation

The ground-truth mapping can be used to evaluate entity resolution.

Conceptually:

```text
Predicted Mapping
        │
        ▼
Compare
        │
        ▼
Ground Truth Mapping
        │
        ▼
Performance Metrics
```

Useful metrics include:

* True positives
* False positives
* False negatives
* Precision
* Recall
* F1 score

For example:

```text
Precision =
Correctly identified matches
----------------------------
All predicted matches
```

```text
Recall =
Correctly identified matches
----------------------------
All actual matches
```

These metrics help determine whether the matching system is incorrectly merging customers or failing to identify valid relationships.

---

# Application Structure

The frontend is organized around the major workflows of the platform.

A conceptual structure is:

```text
src/
│
├── components/
│   └── Sidebar
│
├── pages/
│   ├── Customer360
│   ├── Ingestion
│   └── Quality
│
├── App
└── main
```

The primary application sections are:

### Customer 360

Provides the consolidated customer view.

### Ingestion

Provides visibility into source data and ingestion.

### Quality

Provides visibility into data-quality and entity-resolution results.

---

# Frontend

The frontend uses:

* React
* Vite
* React Router
* JavaScript/JSX
* CSS

React Router is used to separate the major application views.

Conceptually:

```text
/
├── Customer 360
├── Ingestion
└── Quality
```

---

# Backend

The backend is responsible for the data-processing layer.

Its responsibilities include:

```text
Receive Source Data
        ↓
Validate
        ↓
Normalize
        ↓
Match
        ↓
Create / Resolve Master ID
        ↓
Apply Survivorship
        ↓
Store / Return Master Data
```

The frontend should primarily consume processed data rather than implementing the core identity-resolution logic itself.

---

# Data Flow

A complete data flow looks like this:

```text
                 ┌─────────────────┐
                 │  Core Banking   │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │  Credit Card    │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │   Loan System   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │    Ingestion    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Normalization  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Entity Matching │
                 └────────┬────────┘
                          │
               ┌──────────┴──────────┐
               │                     │
               ▼                     ▼
        Exact Matching        Fuzzy Matching
        Email / Phone              Name
               │                     │
               └──────────┬──────────┘
                          ▼
                 ┌─────────────────┐
                 │  Master Entity  │
                 │    Resolution   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Survivorship   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Customer 360    │
                 └─────────────────┘
```

---

# Repository Dataset

The repository uses the following supplied files:

```text
.
├── core_banking.csv
├── credit_card.csv
├── loan_system.csv
├── loan_system.jsonl
├── transaction_data.csv
├── reference_data.csv
├── ground_truth_mapping.csv
└── trust_hierarchy.json
```

---

# Dataset Summary

| Dataset         | Records | Purpose                                 |
| --------------- | ------: | --------------------------------------- |
| Core Banking    |   1,560 | Primary banking customer records        |
| Credit Card     |     975 | Credit-card customer records            |
| Loan System     |     580 | Loan customer records                   |
| Loan JSONL      |     580 | JSONL representation of loan data       |
| Transactions    |   6,841 | Financial transactions                  |
| Ground Truth    |      63 | Known master-customer relationships     |
| Reference Data  |       — | Normalization mappings                  |
| Trust Hierarchy |       — | Matching and survivorship configuration |

---

# Trust Hierarchy Configuration

The system's matching and survivorship behavior is configuration-driven.

Current configuration:

```json
{
  "field_priorities": {
    "Phone": ["SourceA", "SourceB", "SourceC"],
    "Email": ["SourceB", "SourceA", "SourceC"],
    "Name": ["SourceA", "SourceB", "SourceC"],
    "Address": ["SourceB", "SourceA", "SourceC"],
    "DOB": ["SourceA", "SourceB", "SourceC"]
  },
  "matching_rules": {
    "exact_match_fields": ["Email", "Phone"],
    "fuzzy_match_fields": ["Name"],
    "fuzzy_threshold": 0.85
  }
}
```

Keeping these rules outside the application logic makes the matching system easier to modify and audit.

---

# Example Resolution

Consider:

```text
Core Banking
--------------------------------
ID      : C0001
Name    : Kara Randy Clark
Email   : karac@gmail.com
Phone   : 9971674338
DOB     : 1959-03-22


Credit Card
--------------------------------
ID      : CC_243
Name    : Kara Randy Clark
Email   : karac@gmail.com
Phone   : 9971674338


Loan System
--------------------------------
ID      : L_817
Name    : Kara Randy Clark
Phone   : 9971674338
```

The matching engine can identify shared identity signals:

```text
Email → exact match
Phone → exact match
Name  → high similarity
```

The records can therefore be associated with:

```text
Master_ID = M00475
```

The master record then retains the relationship:

```text
M00475
│
├── C0001
├── CC_243
└── L_817
```

The final values are selected according to the configured field-level trust hierarchy.

---

# Why Master Data Management?

Without a master identity layer, applications have to repeatedly answer:

```text
Is C0001 the same person as CC_243?
```

This causes:

* Duplicate customer profiles
* Inconsistent reporting
* Incorrect customer segmentation
* Incomplete financial exposure
* Poor analytics
* Repeated data-cleaning work

With a master customer layer:

```text
Source IDs
   ↓
Master ID
   ↓
Unified Customer
```

downstream systems can work with a consistent representation.

---

# Design Principles

## 1. Separate Identity From Source Identity

Source-system IDs are not necessarily global customer IDs.

```text
C0001
CC_243
L_817
```

are source identifiers.

```text
M00475
```

represents the master entity.

---

## 2. Matching and Survivorship Are Different Problems

Matching answers:

> Are these records the same person?

Survivorship answers:

> Which attribute value should represent that person?

They should therefore be treated as separate stages.

```text
Matching
   ↓
Identity Resolution
   ↓
Survivorship
```

---

## 3. Field-Level Trust

A source should not automatically be considered authoritative for every field.

Instead:

```text
Field
  ↓
Priority Order
  ↓
Surviving Value
```

This allows different systems to be trusted for different attributes.

---

## 4. Explainability

A production financial system should be able to explain why records were linked.

A useful resolution record should conceptually contain:

```text
Master ID
Source Record A
Source Record B

Match Signals:
    Email exact match
    Phone exact match
    Name similarity = 0.94

Decision:
    MATCH
```

This is preferable to an unexplained binary decision.

---

## 5. Configuration Over Hardcoding

Matching thresholds and survivorship priorities are represented as configuration wherever possible.

This allows business rules to change without rewriting the entire matching engine.

---

# Running the Project

## Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

---

## Frontend

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at the local development URL displayed by Vite.

---

## Backend

Create a Python environment:

```bash
python -m venv .venv
```

Activate it.

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend according to the project's FastAPI entry point.

For example:

```bash
uvicorn main:app --reload
```

---

# Recommended Development Workflow

When extending the project, keep the layers separated:

```text
Frontend
   │
   │ API
   ▼
Backend
   │
   ├── Ingestion
   ├── Normalization
   ├── Matching
   ├── Survivorship
   └── Aggregation
   │
   ▼
Database
```

Avoid putting entity-resolution logic directly inside React components.

The frontend should display the result of the data-processing pipeline.

---

# Future Improvements

Potential extensions include:

### Better Entity Resolution

Combine multiple signals into a weighted matching score:

```text
Email Match
Phone Match
Name Similarity
Address Similarity
DOB Match
```

---

### Confidence Scores

Instead of returning only:

```text
MATCH / NO MATCH
```

the system could return:

```text
MATCH
Confidence: 0.96
```

with an explanation of the contributing signals.

---

### Human Review Queue

Ambiguous records can be separated from high-confidence matches:

```text
High confidence
      ↓
Automatic merge

Medium confidence
      ↓
Human review

Low confidence
      ↓
No merge
```

---

### Data Lineage

Track where every master attribute originated:

```text
Master Email
     ↓
Credit Card
     ↓
CC_243
```

This makes the Customer 360 record auditable.

---

### Incremental Ingestion

Instead of processing the entire dataset repeatedly:

```text
New Record
    ↓
Normalize
    ↓
Match against Master Data
    ↓
Update Master
```

This would allow the system to operate continuously.

---

### Production Database

The prototype can be extended with a relational database containing entities such as:

```text
master_customer
source_customer
customer_identity_link
customer_attribute
transaction
data_quality_issue
```

This separates the master entity from the source records and preserves lineage.

---

# Security Considerations

Customer data is sensitive financial information.

A production implementation should include:

* Authentication
* Authorization
* Encryption in transit
* Encryption at rest
* Audit logging
* Role-based access control
* Data masking
* Input validation
* Secure secrets management
* Appropriate retention policies

The dataset used in this repository should be treated as controlled project data.

---

# Project Outcome

The resulting system provides a foundation for a banking **Customer 360 / Master Data Management** platform.

The core transformation is:

```text
Fragmented Banking Records
            │
            ▼
      Data Integration
            │
            ▼
      Entity Resolution
            │
            ▼
       Master Customer
            │
            ▼
        Survivorship
            │
            ▼
       Customer 360
```

Instead of treating each banking system as an isolated source of truth, the platform creates a unified customer identity while preserving the relationship back to each source system.

---

# Key Concepts

This project demonstrates the following engineering concepts:

* Data integration
* Master Data Management
* Customer 360
* Entity resolution
* Record linkage
* Exact matching
* Fuzzy matching
* Data normalization
* Survivorship rules
* Data quality
* Data lineage
* Source-system reconciliation
* Transaction aggregation
* Configuration-driven business rules

---

# Project Status

Current core workflow:

```text
[✓] Source datasets available
[✓] Trust hierarchy defined
[✓] Ground-truth mapping available
[✓] Customer 360 frontend
[✓] Ingestion view
[✓] Data-quality view
[ ] Production-grade entity-resolution engine
[ ] Persistent master-data database
[ ] Automated evaluation pipeline
[ ] Human review workflow
[ ] Production authentication / authorization
```

The unchecked items represent extensions beyond the current prototype and should only be marked complete when implemented.

---

## License

Add the project's applicable license here.

If this repository is being submitted as part of a hackathon or hiring challenge, follow the organizer's requirements regarding redistribution of the supplied datasets.
