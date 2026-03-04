# Lecture 1 Notes — LendingPoint: Intro & Core Loan Origination

## 1. About LendingPoint

- **Low-risk credit provider** — acts as a **mediator** between customers and partner banks.
- Serves customers who are **declined by big banks** (e.g., Bank of America) due to high risk profile scoring.
- LendingPoint has a **lower risk threshold**, so more customers get approved.
- The loan origination process is **almost fully automated** (AI-driven), unlike traditional banks which rely heavily on manual processes (sales reps, paperwork, etc.).
- **"Funded"** = the approved loan amount is transferred to the customer's bank account.

## 2. Partner Banks

- LendingPoint works with **two partner banks**:
  1. **FEB (First Electronic Bank)**
  2. **FinWise**
- More banks are expected to join in the future.
- LendingPoint calculates customer risk, then notifies partner banks.

## 3. Loan Types / Flows

| Abbreviation | Full Name            | Description                                                                 |
|--------------|----------------------|-----------------------------------------------------------------------------|
| **DTC**      | Direct to Customer   | Loan amount is credited directly into the customer's bank account.          |
| **PON / P1** | Point of Need        | Merchant-based loans (similar to Bajaj Finserv in India). Money goes to the merchant, not the customer. |

- Initially, LendingPoint dealt only with **consumer loans (DTC)**.
- Over the past ~3 years, they've also started targeting **merchants (PON)**.
- The two main flows are **DTC** and **P1**.

## 4. Credit System

- Equivalent of India's **CIBIL score** in the US.
- Credit score is maintained based on **credit history**.
- **Three major credit bureaus worldwide**: TransUnion, Experian, Equifax.
- LendingPoint uses **two bureaus**:
  1. **TransUnion**
  2. **Experian**

## 5. PII Page (Personal Identifiable Information)

When a customer clicks "Apply" on `lendingpoint.com`, they fill out:

- First name, Last name, DOB
- Phone number, Email
- Address
- Annual income (CTC / business revenue)
- Income source (Employee / Self-employed / Retired / Other)
- **SSN (Social Security Number)** — unique identifier for US individuals (like Aadhaar in India)

### Third-Party APIs on PII Page

| API             | Purpose                                           |
|-----------------|---------------------------------------------------|
| Email Verify    | Checks if the email is legitimate (not spam)      |
| Zip Code (USPS) | Validates the entered zip code                    |
| SSN Verify      | Validates whether the SSN is a valid number       |
| Location Check  | First operation on "Check My Options" — verifies the customer is in the US |

> **Key Rule**: LendingPoint only operates in the **United States**. Non-US applicants are blocked.

## 6. "Check My Options" — Soft Pull

After filling the PII page, clicking **"Check My Options"** triggers:

1. **Location check** — verifies customer is in the US (via IP/device).
2. **Soft pull (soft inquiry)** — hits the credit bureau to fetch the customer's credit report in real time.
   - This does **not** affect the customer's credit score.
   - Always a soft inquiry at this stage.
   - Verifies credit history and background.

### BRMS & GDS

- **BRMS** = **Business Rules Management System** — defines rules to evaluate the application.
- **GDS** = the **company providing the tool** (third-party rules engine).
- They are **not the same thing**: GDS provides the platform; BRMS is the set of business rules running on it.
- Based on BRMS rules and attributes, the application is **graded**.

### Customer Grading System

- Grades: **A1, A2, B1, B2, C1, C2, C3**, etc.
- Like student grading — categorizes customer risk level.
- Grade determines what **offers** are generated.

## 7. Offer Generation

- Once graded, an **Offer Generator** (separate system/database) produces loan offers.
- Customer sees an **Offer Catalog** with multiple options, e.g.:
  - $4,000 for 48 months at 28.95% APR → monthly payment $132.19
  - $5,000, etc.
- Customer **selects one offer**.
- The application is updated in **Salesforce** with the selected offer.

> **Note**: The offer amount doesn't equal the disbursed amount — **processing fees** are deducted. For example, a $5,000 offer might disburse ~$4,800.

## 8. KYC — Verify Identity (Know Your Customer)

- After selecting an offer, a **Verified Identity** screen appears.
- Purpose: Ensure the applicant is a **real person** (not a bot).
- Uses **AI-generated questions** from a database, e.g.:
  - "What are the first two digits of your SSN?"
  - "What is the approximate square footage of your property?"
- Questions are based on data the system has collected/recorded about customer interactions.
- Once answered correctly → proceed to Bank Information page.

> **Note**: KYC failure does **not** stop the flow — documents are requested manually instead.

## 9. Bank Information

### Plaid Integration

- Customer selects their bank → **Plaid API** (third-party) is triggered.
- Plaid presents an **iframe** (secure layer) where the customer enters bank portal credentials.
- Plaid **fetches bank statements** automatically in the backend.
- If successful: *"John, your bank statements have been received."*
- If failed: *"Your bank statements have not been received."*

### Skip Option

- Customers can **skip Plaid** and upload bank statements **manually** (if skeptical about sharing credentials).

### Account Verification

- Bank name and account number are populated from Plaid.
- Currently, LendingPoint supports **one bank account per application** (no multiple accounts).
- On clicking "Next", another API (**GiACT**) runs in the background to verify:
  - Account number and routing number **belong to the customer**.
  - No **credit fraud history** associated with the account.

## 10. Employment Verification

Customer selects income source:

| Type           | Verification                                                                 |
|----------------|-----------------------------------------------------------------------------|
| **Employee**   | Enter company name, work phone, work email → APIs verify authenticity        |
| **Self-employed** | Enter company name, phone → verified that company/phone actually exist    |
| **Retired**    | No verification needed. Treated as "ex-army/navy". Documents collected at end of flow. |
| **Other**      | No verification. Documents collected manually at end of flow.                |

> For employees, work phone and work email are verified via backend APIs to confirm they are **associated with the customer**.

## 11. Payment Setup

LendingPoint needs to know the **repayment account** — where installments will be deducted from.

### Four Options

| Option                   | Details                                                              |
|--------------------------|----------------------------------------------------------------------|
| **Auto-pay with Bank**   | Bank account number + routing number verified via API                |
| **Auto-pay with Debit**  | Debit card number, expiration, CVV → API verifies authenticity       |
| **Auto-pay with Credit** | Credit card number, expiration, CVV → API verifies authenticity      |
| **Other**                | Manual — upload a voided check at end of flow (rare)                 |

- Most customers choose **bank, debit, or credit card**.
- "Other" is very rare.

## 12. Terms / TILA Page

- After payment setup, customer sees a **TILA (Truth in Lending Act) page**.
- Shows all loan details, disbursement amount, fees.
- Customer must agree to loan details and acknowledge that a **credit inquiry (hard pull) is required** for final approval.

## 13. Contract Signing

- **DocuSign** was previously used — now replaced by **S-Docs** (virtual contracts).
- S-Docs doesn't verify the actual signature — it's just a **soft consent** ("I am ready for this application").
- Once signed, a **hard pull (hard inquiry)** runs in the backend.

> **Hard pull** — unlike soft pull, this **affects the customer's credit score**.

## 14. Decline Points

A customer's application gets **declined** at only **two points**:

1. **Soft pull fails** — based on BRMS rules, the customer is declined immediately (*"Sorry, we can't give you a loan"*).
2. **Hard pull fails** — after contract signing, if the hard inquiry fails, the application is declined.

### Non-blocking Failures

- **KYC failure** — doesn't stop the flow; documents are requested manually.
- **Employment verification failure** — doesn't stop the flow; documents are requested manually.
- **Any other verification failure** — the customer continues, but is asked to **upload documents manually** at the end.

> **Key Principle**: LendingPoint tries to **never stop the customer flow**. If automated verification fails, they fall back to **manual document upload → manual underwriter review**.

## 15. Manual Processing

- If a customer fails any automated verification, at the end of the flow they see a **document upload page**.
- Message: *"We got it from here. We have received your documents and we'll review them shortly."*
- **Underwriters** manually process the loan application.
- Customer is notified via **email** upon completion.

## 16. Wrap-up

- This lecture covered the **intro** and **core business** of LendingPoint — how loan origination works.
- **Next session** will cover:
  - Funding & repayments
  - How Salesforce looks
  - Manual loan processing in Salesforce
  - Customer portal
  - Resumption flow
