# Synthetic Documents Guide for Testing and Validation

This guide provides templates and examples for creating synthetic documents to test the Social Support Application system.

## Document Types Required

1. **Application Form** (Required)
2. **Bank Statement** (Optional but recommended)
3. **Emirates ID** (Optional but recommended)
4. **Resume/CV** (Optional)
5. **Assets/Liabilities Excel** (Optional)
6. **Credit Report** (Optional)

---

## 1. Application Form

### Format: PDF or Image (scanned form)

### Required Fields:
```
Name: [Full Name]
Address: [Complete Address]
Income: [Monthly Income in AED]
Family Size: [Number of dependents]
Employment Status: [Employed/Unemployed/Self-Employed/Student]
Phone: [Contact Number]
Email: [Email Address]
```

### Example Template:
```
SOCIAL SUPPORT APPLICATION FORM

Personal Information:
Name: Ahmed Mohammed Al-Mansoori
Address: Villa 123, Al Barsha, Dubai, UAE
Phone: +971-50-123-4567
Email: ahmed.almansoori@email.com

Financial Information:
Monthly Income: 3,500 AED
Employment Status: Unemployed
Family Size: 4

Additional Information:
Reason for Application: Job loss due to company closure
Date: 15/01/2024
```

### Test Scenarios:

**Scenario 1: Low Income (Eligible)**
- Income: 2,000-5,000 AED
- Family Size: 4-6
- Employment: Unemployed

**Scenario 2: Medium Income (Conditional)**
- Income: 8,000-12,000 AED
- Family Size: 2-3
- Employment: Part-time

**Scenario 3: High Income (May Decline)**
- Income: 20,000+ AED
- Family Size: 1-2
- Employment: Full-time

**Scenario 4: Inconsistent Data (For Validation)**
- Different name spelling across documents
- Address mismatch with Emirates ID
- Income mismatch with bank statement

---

## 2. Bank Statement

### Format: PDF or Image (scanned statement)

### Required Information:
```
Account Number: [Account Number]
Account Holder: [Name matching application]
Balance: [Current Balance]
Statement Period: [Date Range]
Transactions: [List of transactions]
```

### Example Template:
```
EMIRATES NBD BANK
Account Statement

Account No: 1234567890123456
Account Holder: Ahmed Mohammed Al-Mansoori
Statement Period: 01/12/2023 - 31/12/2023

Opening Balance: 5,000.00 AED
Closing Balance: 3,200.50 AED

Transactions:
Date        Description              Debit      Credit     Balance
01/12/2023  Salary Credit            -          3,500.00  8,500.00
05/12/2023  Grocery Store           1,200.00   -          7,300.00
10/12/2023  Rent Payment            2,500.00   -          4,800.00
15/12/2023  Utility Bill            350.00     -          4,450.00
20/12/2023  ATM Withdrawal          800.00     -          3,650.00
25/12/2023  School Fees              450.00     -          3,200.50
```

### Test Scenarios:

**Scenario 1: Low Balance (Eligible)**
- Balance: 500-2,000 AED
- Regular small transactions
- No large deposits

**Scenario 2: Moderate Balance**
- Balance: 5,000-15,000 AED
- Regular income deposits
- Normal expenses

**Scenario 3: High Balance (May Affect Eligibility)**
- Balance: 50,000+ AED
- Large deposits
- Investment transactions

**Scenario 4: Inconsistent Data**
- Account holder name doesn't match application
- Statement period doesn't align with application date

---

## 3. Emirates ID

### Format: Image (JPG/PNG) - Front and Back

### Required Information:
```
ID Number: [15-digit number]
Name: [Full Name in English and Arabic]
Nationality: [Nationality]
Date of Birth: [DD/MM/YYYY]
Expiry Date: [DD/MM/YYYY]
Address: [Optional - if visible]
```

### Example Template (Text representation for OCR):
```
UNITED ARAB EMIRATES
IDENTITY CARD

ID Number: 784-1985-1234567-1
Name: Ahmed Mohammed Al-Mansoori
Name (Arabic): أحمد محمد المنصوري
Nationality: Emirati
Date of Birth: 15/03/1985
Expiry Date: 15/03/2029

[QR Code]
[Photo]
```

### Test Scenarios:

**Scenario 1: Valid ID**
- Valid 15-digit ID number
- Name matches application form
- Not expired

**Scenario 2: Expired ID**
- Expiry date in the past
- Should trigger validation warning

**Scenario 3: Name Mismatch**
- Different name spelling
- Tests validation agent

**Scenario 4: Invalid Format**
- Missing digits in ID number
- Unclear image (tests OCR)

---

## 4. Resume/CV

### Format: PDF or DOCX

### Required Sections:
```
Name: [Full Name]
Email: [Email Address]
Phone: [Phone Number]
Education: [Degree, Institution, Year]
Experience: [Job Title, Company, Duration, Description]
Skills: [List of skills]
```

### Example Template:
```
AHMED MOHAMMED AL-MANSOORI
Email: ahmed.almansoori@email.com
Phone: +971-50-123-4567

EDUCATION
Bachelor of Business Administration
Dubai University, 2010-2014

EXPERIENCE
Sales Associate
ABC Retail Store, Dubai
2015-2023
- Customer service
- Inventory management
- Sales reporting

SKILLS
- Communication
- Customer Service
- Microsoft Office
- Arabic and English
```

### Test Scenarios:

**Scenario 1: Recent Employment**
- Current or recent job
- Relevant experience
- Good skills match

**Scenario 2: Long-term Unemployed**
- Last job 2+ years ago
- Limited recent experience
- May need upskilling

**Scenario 3: Career Change**
- Different field experience
- Transferable skills
- Education mismatch

**Scenario 4: Minimal Experience**
- Recent graduate
- Limited work history
- Strong education

---

## 5. Assets/Liabilities Excel File

### Format: Excel (.xlsx or .xls)

### Required Columns:
```
Item | Description | Category | Value
```

### Example Template:

| Item | Description | Category | Value (AED) |
|------|-------------|----------|------------|
| 1 | Savings Account | Asset | 15,000 |
| 2 | Car | Asset | 25,000 |
| 3 | Personal Loan | Liability | 8,000 |
| 4 | Credit Card Debt | Liability | 2,500 |
| 5 | Furniture | Asset | 5,000 |
| 6 | Student Loan | Liability | 12,000 |

**Total Assets:** 45,000 AED
**Total Liabilities:** 22,500 AED
**Net Worth:** 22,500 AED

### Test Scenarios:

**Scenario 1: Low Net Worth (Eligible)**
- Assets: 10,000-20,000 AED
- Liabilities: 5,000-15,000 AED
- Net Worth: 5,000-10,000 AED

**Scenario 2: Negative Net Worth (High Priority)**
- Assets: 10,000 AED
- Liabilities: 25,000 AED
- Net Worth: -15,000 AED

**Scenario 3: High Net Worth (May Affect Eligibility)**
- Assets: 200,000+ AED
- Liabilities: 50,000 AED
- Net Worth: 150,000+ AED

**Scenario 4: Minimal Assets**
- Only essential items
- No significant savings
- High debt-to-asset ratio

---

## 6. Credit Report

### Format: PDF

### Required Information:
```
Credit Score: [300-850]
Outstanding Debt: [Total amount]
Payment History: [On-time vs Late payments]
Active Loans: [Number and details]
```

### Example Template:
```
CREDIT BUREAU REPORT
Report Date: 15/01/2024

Applicant: Ahmed Mohammed Al-Mansoori
ID: 784-1985-1234567-1

CREDIT SCORE: 650

OUTSTANDING DEBT: 22,500 AED
- Personal Loan: 8,000 AED
- Credit Card: 2,500 AED
- Student Loan: 12,000 AED

PAYMENT HISTORY (Last 12 months):
On-time Payments: 10
Late Payments: 2
Missed Payments: 0

ACTIVE LOANS: 3
- Personal Loan (Bank ABC)
- Credit Card (Bank XYZ)
- Student Loan (Education Finance)

ACCOUNT STATUS: Active
```

### Test Scenarios:

**Scenario 1: Good Credit (650-750)**
- Regular payments
- Manageable debt
- Good payment history

**Scenario 2: Poor Credit (300-550)**
- Multiple late payments
- High debt
- Defaults or collections

**Scenario 3: Excellent Credit (750+)**
- Perfect payment history
- Low debt utilization
- Long credit history

**Scenario 4: Limited Credit History**
- New to credit
- Few accounts
- Short history

---

## Validation Testing Scenarios

### Cross-Document Consistency Tests:

**Test 1: Name Consistency**
- Application Form: "Ahmed Mohammed Al-Mansoori"
- Emirates ID: "Ahmed M. Al-Mansoori" (Minor variation - should pass)
- Bank Statement: "Ahmed Al-Mansoori" (Major variation - should flag)

**Test 2: Address Consistency**
- Application Form: "Villa 123, Al Barsha, Dubai"
- Emirates ID: "Villa 123, Al Barsha, Dubai" (Match - should pass)
- Bank Statement: "P.O. Box 12345, Dubai" (Different - should flag)

**Test 3: Income Consistency**
- Application Form: "3,500 AED monthly"
- Bank Statement: Average deposits 3,200 AED (Close - should pass)
- Bank Statement: Average deposits 8,000 AED (Mismatch - should flag)

**Test 4: Family Size Validation**
- Application Form: "Family Size: 4"
- Resume: Mentions "wife and 2 children" (Matches - should pass)
- No cross-reference available (Should note missing validation)

---

## Document Quality Tests

### Test 1: Clear Documents
- High resolution
- Good contrast
- Proper formatting
- Expected: High extraction accuracy

### Test 2: Poor Quality Documents
- Low resolution images
- Blurry text
- Poor lighting
- Expected: Lower extraction, may need manual review

### Test 3: Handwritten Documents
- Handwritten application forms
- Scanned handwritten notes
- Expected: OCR challenges, may need LLM enhancement

### Test 4: Multi-language Documents
- Arabic text mixed with English
- Bilingual forms
- Expected: Should handle both languages

---

## Edge Cases for Testing

### Case 1: Missing Documents
- Only application form provided
- Missing bank statement
- Missing credit report
- Expected: System should work with available documents, flag missing ones

### Case 2: Incomplete Information
- Application form with blank fields
- Bank statement with missing transactions
- Expected: Validation agent should flag incomplete data

### Case 3: Unusual Formats
- Bank statement from non-UAE bank
- Resume in non-standard format
- Expected: System should handle gracefully or flag for review

### Case 4: Data Anomalies
- Negative bank balance
- Income higher than expenses suggest
- Family size doesn't match dependents
- Expected: Validation agent should identify inconsistencies

---

## Sample Data Sets

### Dataset 1: Highly Eligible Applicant
- Income: 2,500 AED/month
- Family Size: 5
- Employment: Unemployed
- Net Worth: -5,000 AED
- Credit Score: 580
- Expected: **Approve**

### Dataset 2: Conditionally Eligible
- Income: 8,000 AED/month
- Family Size: 3
- Employment: Part-time
- Net Worth: 15,000 AED
- Credit Score: 680
- Expected: **Conditional Approve**

### Dataset 3: Soft Decline
- Income: 15,000 AED/month
- Family Size: 2
- Employment: Full-time
- Net Worth: 50,000 AED
- Credit Score: 720
- Expected: **Soft Decline** (may need enablement support)

### Dataset 4: Decline
- Income: 25,000 AED/month
- Family Size: 1
- Employment: Full-time professional
- Net Worth: 200,000 AED
- Credit Score: 780
- Expected: **Decline**

---

## Tools for Creating Synthetic Documents

### 1. PDF Generation
- Use Python libraries: `reportlab`, `fpdf`, `weasyprint`
- Online tools: PDFtk, Adobe Acrobat
- Word/Google Docs → Export as PDF

### 2. Image Generation (for IDs)
- Use image editing tools: GIMP, Photoshop
- Python: `Pillow` for image manipulation
- Online ID generators (for testing only)

### 3. Excel Generation
- Python: `pandas`, `openpyxl`
- Excel/Google Sheets
- CSV → Excel conversion

### 4. OCR Testing Images
- Create clear, high-resolution images
- Add noise/blur for quality testing
- Test with different fonts and layouts

---

## Best Practices

1. **Use Realistic Data**: Make synthetic data look realistic but clearly fake
2. **Vary Formats**: Test different document layouts and formats
3. **Include Edge Cases**: Test boundary conditions and unusual scenarios
4. **Maintain Consistency**: For cross-validation tests, ensure some documents match
5. **Document Scenarios**: Keep track of what each test case validates
6. **Privacy**: Never use real personal data, even for testing

---

## Quick Start: Minimal Test Set

For quick testing, create these 3 documents:

1. **Application Form** (PDF)
   - Name: "Test Applicant"
   - Income: 3,000 AED
   - Family Size: 3
   - Employment: Unemployed

2. **Bank Statement** (PDF)
   - Account: 1234567890
   - Balance: 2,500 AED
   - Account Holder: "Test Applicant"

3. **Assets/Liabilities** (Excel)
   - Assets: 10,000 AED
   - Liabilities: 8,000 AED
   - Net Worth: 2,000 AED

This minimal set will test the core functionality without requiring all document types.