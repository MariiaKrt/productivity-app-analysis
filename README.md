# Productivity App — Product Analytics Case Study

This project investigates why a subscription-based productivity app was losing paid users despite growing registrations.

## Objective

Identify where the decline occurs after registration and determine whether it is driven by:

* lower conversion
* higher churn
* a specific platform or customer segment
* combination of the factors

## Customer Journey

Users follow this path within the app:


## Approach

### 1. Data Validation

Validated:

* primary and foreign keys
* duplicates and missing values
* date consistency
* trial and subscription logic
* payment and plan values

### 2. Product Health Analysis

Measured:

* registrations
* trial users
* 15-day and 30-day registration-to-paid conversion
* new and active subscriptions
* subscription churn
* successful payments and revenue

### 3. Root-Cause Analysis

Compared conversion across:

* platform
* acquisition channel
* region
* age group
* trial and non-trial paths
* payment outcomes

## Key Findings

* Registrations increased by approximately **35%**.
* Paid users decreased by approximately **42%**.
* The main issue was a decline in **registration-to-paid conversion**.
* The decline was concentrated on **iOS**.
* iOS conversion fell from **42.72% to 10.28%**.
* Android conversion remained relatively stable.
* No single channel, region, age group, or payment issue explained the decline.

The evidence points to an iOS-specific problem in the path from registration to paid subscription.

## Recommended Next Steps

* Verify the data is recorded completely and consistently in the sources
* Compare analytics data with backend subscription records
* Compare the decline with iOS releases and product changes 
* Analyse the iOS funnel at a more granular level
* Analyse abandoned checkout and subscription activation

## Repository Structure

```text
productivity-app-analysis/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 0. Data validation and cleaning
│   ├── 1. Product health overview
│   └── 2. Business decline root-cause analysis
├── src/
│   ├── preprocessing.py
│   ├── conversions.py
│   └── visualizing.py
└── README.md
```

## Tech Stack

Python, pandas, NumPy, SciPy, Matplotlib, Jupyter
