# LendingPoint Lecture 2 — APIs, Partner Flow & Resumption

## 1. PII Page — APIs Running on the First Page

When a user enters personal information (PII page), several **backend APIs** run in real-time:

| API | Type | Purpose |
|-----|------|---------|
| **Email Verification** | 3rd-party | Validates the email address provided |
| **Phone Number Verification** | 3rd-party | Checks the phone number is a valid **US number** (does **not** verify identity — just authenticity) |
| **USPS API** | 3rd-party | US Postal Service — verifies the **zip code** belongs to the correct **state and city** |
| **Resolve 360** | 3rd-party | Resolves the full SSN from the **last 4 digits**. If it can't resolve, the customer must manually enter all 9 digits |
| **Count API** | 3rd-party | Verifies the user's **IP and location**. If IP is outside the US → user is shown a decline/thank-you page ("Unable to generate loan offer") |

> [!IMPORTANT]
> Only **US citizens residing in the US** can apply for a loan on LendingPoint.

---

## 2. "Check My Options" — Create Lead API

When the customer clicks **"Check My Options"**:

- **Create Lead API** (Internal, `POST`) is called
  - Creates a **Contact** and an **Opportunity** in **Salesforce** (CRM)
  - This is essentially the **application creation** in the system
  - Also triggers the **soft pull** (credit check software) to verify credit/grade queries

### 30-Day Rule (Soft Pull Window)
- Once a soft pull is done, the customer **cannot reapply for 30 days**
- This applies whether the customer was **approved or declined**
- Prevents repeated applications and unnecessary credit inquiries

### Duplicate Detection Logic
- If a customer tries to apply again within 30 days, the system detects duplicates using a combination of: **first name, last name, address, zip code, SSN**
- Prevents **data duplicacy** in the system — avoids storing 10x records for the same person

---

## 3. PreQual API

- **PreQual API** (Internal, `GET`) — runs after Create Lead returns `200`
- **Fetches the loan offers** generated for the customer
- Displays offers with: **payment amount, term, and APR**

---

## 4. Save Offer API

- **Save Offer API** (Internal) — called when customer clicks **"Choose"** on an offer
- Saves the selected offer details (amount, term, APR) in the system

---

## 5. Track Progress API

- Fires on **every page** of the application flow
- Tracks which page/step the customer is on
- Helps power the **Resumption Flow** (covered below)

---

## 6. KYC Page — Identity Verification APIs

Two **third-party APIs** perform KYC:

| API | Purpose |
|-----|---------|
| **Payfone** | Verifies customer identity using their **phone number** — cross-checks first name, last name, address, city against the phone number owner |
| **IDology** | Runs KYC and returns **verification questions** based on the customer's information |

> [!NOTE]
> If a customer **fails KYC**, the flow **does NOT stop**. The application continues. Only two points cause a decline: **failing the soft pull** or **failing the hard pull**.

---

## 7. Bank Information Page

| API | Type | Purpose |
|-----|------|---------|
| **Plaid** | 3rd-party | Connects to the customer's bank to **fetch statements** (automated bank verification) |
| **GiACT** | 3rd-party | Verifies **account number + routing number** belong to the customer (cross-checks with name, SSN, etc.) |

- Customers can also **manually upload** bank statements if they don't want to use Plaid
- On the **Payment Setup page**, bank info (name, account #, routing #) is **auto-populated and non-editable** — LendingPoint uses this account for loan recovery

---

## 8. Income/Employment Page

| API | Type | Purpose |
|-----|------|---------|
| **EmailAge** | 3rd-party | Verifies the **work email** domain is legitimate (e.g., `@company.com` is a real domain) |

- Only triggered when the user selects **"Employed"**
- For **self-employed, retired**, etc. — no API is called; verification is **manual** by underwriters via document uploads

---

## 9. Payment Setup Page

- **Auto-pay with Bank**: GiACT verification runs again
- **Auto-pay with Debit Card**: Card number, CVV, expiry verified
- **Credit Card**: Validated for authenticity
- **Other (Void Check)**: No automated verification — manual upload

---

## 10. Contract Signing — S-Docs

- Previously used **DocuSign** (3rd-party) for contract signing
- Partnership with DocuSign **expired**
- Now using **S-Docs** as the new vendor for contract signing

---

## 11. Partner Flow

> [!IMPORTANT]
> **Core Flow** ≠ **Partner Flow** — don't confuse them!

| | Core Flow | Partner Flow |
|--|-----------|--------------|
| **Entry** | Customer applies directly on `lendingpoint.com/apply` | Partner sends application to LendingPoint |
| **Trigger** | Customer-initiated | Partner-initiated (customer was rejected by partner) |

### How Partner Flow Works
1. A partner (e.g., Renovate America, eBay, Invisalign) has their own lending system
2. When they **can't approve** a customer, they send the application to LendingPoint
3. LendingPoint runs its own credit model — and **often approves** those rejected customers
4. There are **1,000+ partners** with LendingPoint
5. In partner flow, the customer still goes through the same pages (offers, KYC, bank, etc.)

---

## 12. Resumption Flow

### Purpose
Allows an **approved** customer who **dropped off mid-application** to **resume from where they left off**.

### How It Works
- Customer creates a **username and password** on the first page
- If they close the browser at any point (offers page, KYC page, bank page, etc.) and come back within 30 days:
  - System detects the existing application
  - **Does NOT run the soft pull again**
  - Redirects the customer to the **exact page they left off** on

### Key Points
- Works only for **approved** applications (declined customers are blocked by the 30-day rule)
- Prevents **duplicate data** and avoids re-running credit checks
- **Track Progress API** is what tracks which page the customer was on

---

## API Summary — Quick Reference

| API | Type | Stage | What It Does |
|-----|------|-------|-------------|
| Email Verification | 3rd-party | PII Page | Validates email |
| Phone Verification | 3rd-party | PII Page | Validates US phone number |
| USPS | 3rd-party | PII Page | Validates zip → state/city |
| Resolve 360 | 3rd-party | PII Page | Resolves full SSN from last 4 |
| Count API | 3rd-party | PII Page | IP/location check (US only) |
| Create Lead | **Internal** (POST) | Check My Options | Creates Contact + Opportunity in Salesforce; triggers soft pull |
| PreQual | **Internal** (GET) | After Create Lead | Fetches generated offers |
| Save Offer | **Internal** | Offer Selection | Saves chosen offer |
| Track Progress | **Internal** | Every Page | Tracks customer's current page |
| Payfone | 3rd-party | KYC | Phone-based identity verification |
| IDology | 3rd-party | KYC | KYC questions based on provided info |
| Plaid | 3rd-party | Bank Page | Connects to bank, fetches statements |
| GiACT | 3rd-party | Bank/Payment Page | Verifies account + routing number |
| EmailAge | 3rd-party | Employment Page | Validates work email domain |
| S-Docs | 3rd-party | Contract | E-signature (replaced DocuSign) |
