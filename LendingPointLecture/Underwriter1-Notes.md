# Underwriter Session 1 – Lecture Notes

## Overview

This session covers the **Underwriter's role** at LendingPoint and provides a hands-on walkthrough of the **Salesforce Opportunity** object and all its tabs. The underwriter handles applications where automated processes have failed, performing manual verifications, requesting supporting documents, and overriding validation failures when justified.

---

## 1. The Underwriter's Role

- **When involved:** Automated verification steps (KYC, bank verification, employment, etc.) fail or require manual review.
- **Primary responsibilities:**
  - Review failed validation checks.
  - Request and verify supporting documents from the customer.
  - Override specific tolerance/validation failures with documented justification.
  - Manage offers (deselect/reselect customer offers, create custom offers).
- **Goal:** Move the application from a blocked state to "Ready to Fund" by resolving all failures.

---

## 2. Salesforce Opportunity – Key Concepts

- Every loan application is tracked as an **Opportunity** in Salesforce.
- The opportunity moves through statuses: `Credit Qualified` → `Offer Accepted` → `Ready to Fund` → `Funded`, etc.
- Two types of accounts associated with an opportunity:
  - **Deposit Account:** Where the loan amount is deposited (customer's bank account).
  - **Repayment Account:** The account from which repayments are deducted (can be the same or different from the deposit account).

---

## 3. Opportunity Tabs

### 3.1 Details Tab

- Contains core application information:
  - Customer name, loan amount, interest rate, term, monthly payment.
  - Application status and stage.
  - Source (DTC / Partner).
  - Created date, last modified date.
- **"Ready to Fund" light:** A traffic-light indicator that shows whether all validations have passed.
  - 🟢 Green = All clear, ready for funding.
  - 🔴 Red = Outstanding failures that need resolution.

---

### 3.2 Offers Tab

- Displays all **system-generated loan offers** presented to the customer.
- Each offer includes: loan amount, APR, term (months), monthly payment.
- Shows which offer the customer **selected** (checkbox).
- The **Original Offer** field indicates the original amount offered vs. what the customer chose.
- Underwriters can:
  - **Deselect** the customer's chosen offer.
  - **Reselect** a different offer on behalf of the customer.

---

### 3.3 Underwriter Offers Tab

- Allows underwriters to create **custom offers** not available through the standard system.
- Used when:
  - The customer wants different terms.
  - The underwriter needs to adjust based on additional verification.
- **"Recalculate Offers" button:** Re-runs the offer generation engine with updated parameters (e.g., after income verification adjusts the approved amount).
- Custom offers can have different amounts, rates, or terms than originally generated.

---

### 3.4 Employment Tab

- Displays the customer's employment information:
  - **Employment Type:** Employee, Self-Employed, or Retired.
  - Employer name, job title, work phone, work email.
  - Annual income, employment start date.
- **Employment type determines verification path:**
  - **Employee:** Verified via employer contact and work email (EmailAge API).
  - **Self-Employed:** Requires business documentation (tax returns, business license).
  - **Retired:** Requires proof of retirement income (pension statements, Social Security).
- Underwriters verify this manually when automated checks fail.

---

### 3.5 ACH Information Tab

- Contains the customer's bank account details for both deposit and repayment:
  - Bank name, account number, routing number.
  - Account type (Checking / Savings).
- **Payment methods tracked:**
  - **ACH (Bank Transfer):** Primary method for auto-pay.
  - **Debit Card:** Alternative payment method.
  - **Credit Card:** Another alternative.
- Shows verification status of bank details (via GiACT).
- If GiACT verification fails, the underwriter must manually verify bank information using uploaded bank statements.

---

### 3.6 Documents Tab

- Lists all **required documents** and their statuses:
  - Bank statements, pay stubs, tax returns, ID documents, etc.
- Documents can be uploaded in two ways:
  - **Direct upload:** Customer or underwriter uploads through the portal.
  - **Email upload:** Customer emails documents, which are then attached to the opportunity.
- Underwriters can:
  - Request specific documents from the customer.
  - Review uploaded documents for accuracy.
  - Mark documents as accepted or rejected.

---

### 3.7 Validation Tab (Profile Validation)

- Shows **all validation checks** that were run on the application.
- Displays both **passed** (🟢 green) and **failed** (🔴 red) checks.
- Each validation includes:
  - What was checked (ID, email, phone, bank account, address, etc.).
  - Verification method (IDology, Payfone, GiACT, Plaid, etc.).
  - Pass/Fail status.
- This is a **comprehensive view** of every check, regardless of pass/fail.

> **Key Point:** The Validation tab is the older, more comprehensive view. It was the primary tab before the Tolerance tab was introduced.

---

### 3.8 Tolerance Tab

- A **newer feature** that focuses primarily on **failures only**.
- Only shows checks that have **failed** (🔴 red) — passed checks are hidden.
- Purpose: Quickly identify what needs attention without scrolling through passed checks.
- **Which tab is active depends on the ARN (Analytical Random Number):**
  - Certain ARN values route to the Validation tab.
  - Other ARN values route to the Tolerance tab.
  - This is configured in the backend rules.
- **Override functionality:**
  - Underwriters can **override** individual tolerance failures.
  - Steps to override:
    1. Click the "Override" button on the specific failed tolerance.
    2. Enter an **override reason/note** (e.g., "Reviewed 3 months of bank statements, account is valid").
    3. Select status (e.g., "Approved").
    4. Save the override.
  - Overridden tolerances are displayed separately so other reviewers can see what was manually approved and why.
  - Once **all tolerances become green** (either passed or overridden), the "Ready to Fund" indicator turns green.

---

### 3.9 Profile Tab

- The **backbone of the Tolerance tab** — provides the raw data that feeds tolerance decisions.
- Structured in sections:
  - **ID Details:** Verified using IDology (name, SSN, DOB, address matching).
  - **Contact Information:** Email verification, phone verification (Payfone).
  - **Bank Account Details:** Account/routing number verification (GiACT), balance info (Plaid).
- Each parameter shows:
  - Whether it has been **verified** (checkbox).
  - **Verified using** which service/API.
- **Key relationship:**
  - Profile tab provides data → Tolerance tab evaluates rules against this data → Determines pass/fail.
  - Profile tab reflects **automated process results only**; manual overrides in Tolerance tab are NOT reflected back in Profile.

---

### 3.10 Related Tab

- A critical tab with multiple sections:

#### Attachments
- All files attached to the opportunity:
  - **Plaid statements** (bank statement fetched via Plaid API).
  - **GiACT verification** results.
  - **Signed contracts** (S-Docs copies).
  - **Uploaded documents** (manual uploads from customer/underwriter).

#### Opportunity Additional Details
- Extended information not shown on the main Details tab:
  - ID verification details (IDology results).
  - Phone verification (Payfone).
  - Business-level details.
  - Various verification scores and results.

#### Opportunity Field History
- **Critical for debugging** — tracks all field changes over time.
- For each change, shows:
  - **Field name** (e.g., Status, Amount, Routing Number).
  - **Original value** → **New value**.
  - **Timestamp** of change.
  - **Who made the change.**
- Example: Status changed from "Credit Qualified" to "Offer Accepted" at a specific timestamp.
- Useful for QA and developers to trace what happened during the application lifecycle.

#### Logs (Login Logs / Web Service Logs)
- Salesforce web service logs generated at each step.
- Contains API request/response details.
- Used for **debugging issues** — e.g., checking the "Easy Verify Funding Decision" log to see if contact info was validated, deposit account was validated, etc.
- Every backend service call creates a corresponding log entry.

---

### 3.11 Fraud Summary Tab

- Contains fraud-related checks and alerts:
  - **Verification Statuses:** Flags like `Steps`, `No Steps`, `Special Review`, `Decline`.
  - These flags are calculated based on **backend rules**.
  - Example: For a particular opportunity, "Special Review" flag = true, "No Steps" = true.
- **Fraud Shields:** Rules that have passed or failed for fraud detection.
- **IP Address Verification:** Checks the applicant's IP address.
- **Email Address Verification:** Validates the email.
- **Trust Scores:** Payfone trust score, ID Analytics score, and other scoring details.
- The exact meaning of each flag becomes clearer with hands-on experience.

---

### 3.12 Decisioning Tab

- Shows the **BRMS (Business Rules Management System)** rules evaluation:
  - Contains all rules checked during both **soft pull** and **hard pull** phases.
  - Rules highlighted in **red** = failed.
  - Rules with a **checkmark** = passed.
- **Two layers of credit checks:**
  - **Soft Pull:** Runs automatically when the customer clicks "Check My Options." Used for initial qualification.
  - **Hard Pull:** Runs automatically **after contract signing.** Ensures applicant's financial status hasn't changed. Can only be done **once every 30 days.**
- **"Primary" checkbox:** Indicates which credit pull (soft or hard) was used for application qualification.
- **Three key buttons on the Decisioning tab:**
  1. **Soft Credit Pull:** Manually trigger a soft pull (if not already run).
  2. **Hard Credit Pull:** Manually trigger a hard pull (disabled if already done within 30 days).
  3. **Override Rules:** Re-checks all rules and can change status from "Declined" to "Credit Qualified," potentially generating new offers.
- **Credit Report section:** Shows entries for both soft and hard pulls with their pass/fail statuses.
- **Recommended Actions:** Shows any required actions based on rule failures. If "No action," failures may be non-mandatory.

#### BRMS Rules — Mandatory vs. Non-Mandatory
- **Mandatory rules:** Must pass (e.g., credit score must be above a minimum threshold — cannot give a loan if below).
- **Non-mandatory rules:** Can fail if other compensating factors exist (e.g., low credit score but very high annual income may still qualify).
- The decisioning tab shows which rules failed and whether they are blocking.

#### Override Rules Button
- Used when an application is **declined** due to rule failures but the underwriter wants to re-evaluate.
- Clicking it re-runs all rules and can:
  - Change status from "Declined" → "Credit Qualified."
  - Generate new offers.
- **Important:** Clicking Override Rules does **not always** produce offers — it depends on whether the underlying rules that generate offers are actually overridden/passed.

---

## 4. Validation vs. Tolerance — Quick Comparison

| Feature | Validation Tab | Tolerance Tab |
|---|---|---|
| **Shows** | All checks (pass + fail) | Only failed checks |
| **Color coding** | 🟢 Green (pass), 🔴 Red (fail) | 🔴 Red (fail only) |
| **Override support** | No | Yes — underwriters can override |
| **Tab activation** | Based on ARN value | Based on ARN value |
| **Age** | Older feature | Newer feature |
| **Data source** | Profile tab | Profile tab |

---

## 5. Override Process — Step by Step

1. Open the **Tolerance** tab.
2. Identify the failed check (red indicator).
3. Click the **Override** button on that specific tolerance.
4. Enter a **note/reason** explaining why the override is justified (e.g., "Manually verified bank statements for 3 months").
5. Set the status to **Approved**.
6. **Save** the override.
7. The overridden tolerance now shows as resolved.
8. Other reviewers can see that the tolerance was **manually overridden** and the reason why.
9. Once **all tolerances** are green (passed or overridden), the **"Ready to Fund"** light turns green.

---

## 6. Credit Pulls — Soft vs. Hard

| Aspect | Soft Pull | Hard Pull |
|---|---|---|
| **When triggered** | "Check My Options" click | After contract signing |
| **Impact on credit score** | No impact | May impact credit score |
| **Frequency limit** | Can be re-run | Once every 30 days |
| **Purpose** | Initial qualification | Final verification before funding |
| **Runs automatically** | Yes | Yes (after contract signing) |
| **Can be triggered manually** | Yes (via Decisioning tab) | Yes (if not done in last 30 days) |
| **Button state** | Usually enabled | Disabled if already done |

---

## 7. Key Takeaways

1. **Underwriters are the safety net** — they handle what automation can't.
2. **Profile tab feeds data to Tolerance tab** — automated results flow one way.
3. **ARN determines which tab (Validation vs. Tolerance)** is active for a given opportunity.
4. **Override requires documentation** — every override needs a clear reason.
5. **BRMS rules have two tiers** — mandatory (must pass) and non-mandatory (can be compensated).
6. **Hard pull is limited to once per 30 days** — the button is disabled after execution.
7. **Opportunity Field History is the debugging goldmine** — tracks every change with timestamps.
8. **"Ready to Fund"** only turns green when all validations/tolerances pass or are overridden.

---

## 8. Recommended Next Steps (from the session)

- Get **Salesforce credentials** created as soon as possible.
- Do a **hands-on walkthrough**: Open any opportunity, explore all tabs.
- **Run the E2E flow** from beginning to end while simultaneously checking the Salesforce tabs to see how data populates at each stage.
