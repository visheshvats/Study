# Lecture 3 Notes — LendingPoint: Funding, Salesforce CRM & Repayments

## 1. Lecture Overview

Today's topics:
- What happens when an application gets **funded** (loan dispersed)
- How **repayments** work
- A peek inside **Salesforce** — Contact, Opportunity, and LA (Loan Agreement)

---

## 2. Contract Documents — Two Types

| Type | Description |
|------|-------------|
| **S-Docs (Virtual Contract)** | A soft-copy document the user signs virtually on the UI. Contains terms & conditions, LendingPoint policies, selected APR/offer details, and a summary of what the loan will look like. This is a **prerequisite** document. |
| **LA (Loan Agreement)** | The **final, comprehensive agreement** between the bank and the customer — generated only after the application is funded. This is the "bible" of the loan account. |

- Once the user signs the virtual contract (S-Docs) → **hard pull** runs → all calculations are done → customer sees the **Thank You page**.

---

## 3. Salesforce: Contact & Opportunity

### Contact
- When the **Create Lead API** is hit, a **Contact** is created in Salesforce.
- Contains the customer's PII: first name, last name, address, etc.
- Think of it as the preliminary form submitted when applying for a loan.

### Opportunity
- Created after the Contact, when the **PreQual API** is called.
- An Opportunity gets **associated** with the Contact.
- A single Contact can have **multiple Opportunities** (e.g., one declined, one cancelled, one active).
- The Opportunity object has **1,000–1,500+ fields**.

### Partner Account
- Each application is linked to a **partner account** (e.g., "Align Corporate Virtual Card", "Turnkey ATM Solutions").
- Different partners have different partner accounts in Salesforce.

---

## 4. Opportunity Tabs in Salesforce

Each tab in the Opportunity is **synced with the UI pages** — naming conventions are similar, making it easy to find related information in the CRM.

| Tab | Purpose |
|-----|---------|
| **Fraud Summary** | Verification results: address verification, email verification, ID scan, ID questions |
| **Decisioning** | **Backbone tab** — the most critical tab. Contains rules for soft pull and hard pull. Shows checkboxes for each rule (checked = passed, null = not executed). If critical rules fail, the application is declined. |
| **Offers** | Lists all offers returned by the Offer Generator for this application. Shows which offer the customer selected. |
| **Underwriter Offers** | Similar to Offers tab, but **underwriters can create custom offers** here and email them to the customer. |
| **Employment** | Employment type and verification info (employee, self-employed, retired, etc.) |
| **ACH Information** | Bank account information (account number, routing number) |
| **Documents** | Uploaded documents and attachments |
| **Profile** | Customer profile information |
| **Validation** | **Critical tab** — shows green/red flags indicating whether the customer passed all ~7 steps required for funding. All green = ready to fund. |

### Decisioning Tab Deep Dive
- Contains **soft pass** and **hard pass** rule results.
- Rule checked ✅ = **passed**
- Rule is null = **not executed**
- Some rule failures don't stop the application (non-blocking).
- Certain critical rule failures → **application is declined**.
- Credit report **attachments** are stored here — one for hard pull, one for soft pull.
- BRMS attributes from GDS (the rules engine) are visible in this tab.

### Offers vs. Underwriter Offers
- **Offers tab** — read-only list of system-generated offers and the customer's selection.
- **Underwriter Offers tab** — allows underwriters to **create custom offers** when a customer requests a different loan amount than what was auto-generated. The underwriter checks eligibility, creates the custom offer, and emails the customer.

---

## 5. Funding Process

Funding is **manual** — not automated.

### Flow:
1. Customer completes the UI flow → signs virtual contract → sees **Thank You page**.
2. Hard pull runs successfully.
3. **Funding Decision API** is called.
4. Underwriter manually changes the Opportunity status:
   - `Contract Package Sent` / `Approved` → **`Funding`** → **`Funded`**
5. Once status = **Funded**, the **LA (Loan Agreement)** is generated.

> **Key point**: The validation tab's flags are updated **after the hard pull** succeeds and the Funding Decision API is called successfully.

---

## 6. LA — Loan Agreement

- Generated when the application status changes to **Funded**.
- The **final agreement** between the partner bank and the customer.
- Contains a massive amount of information:
  - Loan terms and conditions
  - Repayment schedule (sequence, dates, number of payments)
  - Balance remaining
  - Charges and fees
  - Transaction history (loan disbursement, payments)
  - Customer signatures
- Described as the **"bible of the loan account"** — every detail about the loan lives here.
- Many fields, many tabs, many buttons.

### LA Tabs (Key ones):
| Tab | Content |
|-----|---------|
| **Repayment Schedule** | Sequence number, next repayment date, number of payments, balance remaining |
| **Transactions** | Loan disbursement records, charges, and payment history |
| **LPTI** | Installment records with their own statuses |

> Each tab in the LA is self-descriptive — the tab name indicates what information it holds.

---

## 7. Customer Portal

- LendingPoint has a **Customer Portal** for funded customers.
- Customer creates a **username and password** during the application process.
- **Access is only available after the application is funded** — cannot access the portal before funding.

### Portal Features:
- Make **payments** (future payments)
- Make **part payments**
- Initiate **foreclosure** (early loan payoff)
- View **loan information**

---

## 8. Repayments

- **LPTI (LendingPoint Transaction Installment)** = the repayment records.
- Each LPTI has its own **status**.
- Represents the customer **paying installments back**.

### One-Time Payment Date Change:
- If the customer wants to change their payment date (e.g., from Jan 20 to Jan 25):
  1. Customer calls the **LendingPoint Operations floor**.
  2. Operations team **raises a request**.
  3. The payment date is changed via buttons/actions in the LA within Salesforce.

---

## 9. Key Takeaways

- **Salesforce is the CRM backbone** — Contact stores customer PII, Opportunity tracks the application journey, LA tracks the funded loan.
- **UI pages and Salesforce tabs are synced** — same naming conventions make navigation intuitive.
- **Funding is manual** — underwriter changes the status in Salesforce.
- **LA is generated only after funding** — it's the comprehensive loan document.
- **Customer portal** is accessible only post-funding for payment management.
- **Repayments (LPTI)** are tracked as individual installment records with statuses.
