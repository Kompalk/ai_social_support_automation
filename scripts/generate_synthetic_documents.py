"""Script to generate synthetic documents for testing."""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. Install with: pip install reportlab")
    print("Falling back to text file generation.")

def generate_assets_liabilities_excel(output_path: str, scenario: str = "low_income"):
    """Generate synthetic assets/liabilities Excel file."""
    
    scenarios = {
        "low_income": {
            "assets": [
                {"Item": "Savings Account", "Description": "Bank savings", "Category": "Asset", "Value": 5000},
                {"Item": "Car", "Description": "2015 Toyota", "Category": "Asset", "Value": 15000},
                {"Item": "Furniture", "Description": "Household items", "Category": "Asset", "Value": 3000},
            ],
            "liabilities": [
                {"Item": "Personal Loan", "Description": "Bank loan", "Category": "Liability", "Value": 8000},
                {"Item": "Credit Card", "Description": "Credit card debt", "Category": "Liability", "Value": 2500},
            ]
        },
        "medium_income": {
            "assets": [
                {"Item": "Savings Account", "Description": "Bank savings", "Category": "Asset", "Value": 20000},
                {"Item": "Car", "Description": "2018 Honda", "Category": "Asset", "Value": 35000},
                {"Item": "Furniture", "Description": "Household items", "Category": "Asset", "Value": 8000},
            ],
            "liabilities": [
                {"Item": "Personal Loan", "Description": "Bank loan", "Category": "Liability", "Value": 15000},
                {"Item": "Credit Card", "Description": "Credit card debt", "Category": "Liability", "Value": 5000},
            ]
        },
        "high_income": {
            "assets": [
                {"Item": "Savings Account", "Description": "Bank savings", "Category": "Asset", "Value": 100000},
                {"Item": "Car", "Description": "2022 BMW", "Category": "Asset", "Value": 150000},
                {"Item": "Property", "Description": "Apartment", "Category": "Asset", "Value": 500000},
            ],
            "liabilities": [
                {"Item": "Mortgage", "Description": "Property loan", "Category": "Liability", "Value": 300000},
                {"Item": "Car Loan", "Description": "Vehicle financing", "Category": "Liability", "Value": 80000},
            ]
        },
        "wealthy": {
            "assets": [
                {"Item": "Savings Account", "Description": "Premium banking account", "Category": "Asset", "Value": 2500000},
                {"Item": "Investment Portfolio", "Description": "Stocks and bonds", "Category": "Asset", "Value": 5000000},
                {"Item": "Primary Residence", "Description": "Luxury villa in Emirates Hills", "Category": "Asset", "Value": 8000000},
                {"Item": "Investment Property 1", "Description": "Apartment in Downtown Dubai", "Category": "Asset", "Value": 3500000},
                {"Item": "Investment Property 2", "Description": "Commercial property", "Category": "Asset", "Value": 6000000},
                {"Item": "Luxury Car 1", "Description": "2024 Rolls-Royce Phantom", "Category": "Asset", "Value": 1200000},
                {"Item": "Luxury Car 2", "Description": "2024 Lamborghini Urus", "Category": "Asset", "Value": 800000},
                {"Item": "Yacht", "Description": "Private yacht", "Category": "Asset", "Value": 15000000},
                {"Item": "Art Collection", "Description": "Fine art and collectibles", "Category": "Asset", "Value": 3000000},
                {"Item": "Jewelry & Watches", "Description": "Luxury items", "Category": "Asset", "Value": 500000},
            ],
            "liabilities": [
                {"Item": "Primary Residence Mortgage", "Description": "Property loan (low LTV)", "Category": "Liability", "Value": 2000000},
                {"Item": "Investment Property Loan", "Description": "Commercial property financing", "Category": "Liability", "Value": 1500000},
            ]
        }
    }
    
    data = scenarios.get(scenario, scenarios["low_income"])
    all_items = data["assets"] + data["liabilities"]
    
    df = pd.DataFrame(all_items)
    
    # Create output directory if it doesn't exist
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_excel(output_path, index=False)
    print(f"Generated assets/liabilities Excel: {output_path}")
    return output_path


def generate_application_form_pdf(output_path: str, name: str, income: float, 
                                 family_size: int, employment_status: str, address: str):
    """Generate application form as PDF."""
    if not REPORTLAB_AVAILABLE:
        # Fallback to text file
        generate_application_form_text(name, income, family_size, employment_status, address)
        return
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("SOCIAL SUPPORT APPLICATION FORM", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Personal Information Section
    story.append(Paragraph("<b>Personal Information:</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    data = [
        ['Name:', name],
        ['Address:', address],
        ['Phone:', f"+971-50-{random.randint(1000000, 9999999)}"],
        ['Email:', f"{name.lower().replace(' ', '.')}@email.com"],
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Financial Information Section
    story.append(Paragraph("<b>Financial Information:</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    data = [
        ['Monthly Income:', f"{income:,.0f} AED"],
        ['Employment Status:', employment_status],
        ['Family Size:', str(family_size)],
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Additional Information
    story.append(Paragraph("<b>Additional Information:</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Reason for Application: Financial assistance required", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Signature: ________________", styles['Normal']))
    
    doc.build(story)
    print(f"Generated application form PDF: {output_path}")


def generate_application_form_text(name: str, income: float, family_size: int, 
                                  employment_status: str, address: str) -> str:
    """Generate application form text content (fallback)."""
    form_text = f"""
SOCIAL SUPPORT APPLICATION FORM

Personal Information:
Name: {name}
Address: {address}
Phone: +971-50-{random.randint(1000000, 9999999)}
Email: {name.lower().replace(' ', '.')}@email.com

Financial Information:
Monthly Income: {income:,.0f} AED
Employment Status: {employment_status}
Family Size: {family_size}

Additional Information:
Reason for Application: Financial assistance required
Date: {datetime.now().strftime('%d/%m/%Y')}

Signature: ________________
"""
    return form_text


def generate_bank_statement_pdf(output_path: str, account_holder: str, account_number: str, 
                                balance: float, monthly_income: float, is_wealthy: bool = False):
    """Generate bank statement as PDF.
    
    Args:
        output_path: Path to save the PDF
        account_holder: Account holder name
        account_number: Account number
        balance: Closing balance
        monthly_income: Monthly income
        is_wealthy: If True, shows luxury/investment transactions instead of regular expenses
    """
    if not REPORTLAB_AVAILABLE:
        # Fallback to text file
        text = generate_bank_statement_text(account_holder, account_number, balance, monthly_income, is_wealthy)
        Path(output_path.replace('.pdf', '.txt')).write_text(text)
        return
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Header
    story.append(Paragraph("EMIRATES NBD BANK", styles['Heading1']))
    story.append(Paragraph("Account Statement", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    statement_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    # Account Information
    data = [
        ['Account No:', account_number],
        ['Account Holder:', account_holder],
        ['Statement Period:', f"{statement_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"],
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Balance Summary
    opening_balance = balance + (monthly_income * 0.1) if is_wealthy else balance + 2000
    story.append(Paragraph(f"Opening Balance: {opening_balance:,.2f} AED", styles['Normal']))
    story.append(Paragraph(f"Closing Balance: {balance:,.2f} AED", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Transactions Table
    transactions_data = [['Date', 'Description', 'Debit', 'Credit', 'Balance']]
    
    current_balance = opening_balance
    if is_wealthy:
        # Wealthy transactions: investment returns, luxury purchases, etc.
        transactions = []
        transactions.append((statement_date, "Opening Balance", 0, 0, current_balance))
        current_balance += monthly_income
        transactions.append((statement_date + timedelta(days=3), "Salary Credit", 0, monthly_income, current_balance))
        current_balance += monthly_income * 0.5
        transactions.append((statement_date + timedelta(days=5), "Investment Return", 0, monthly_income * 0.5, current_balance))
        current_balance -= monthly_income * 0.15
        transactions.append((statement_date + timedelta(days=8), "Luxury Retail Purchase", monthly_income * 0.15, 0, current_balance))
        current_balance -= monthly_income * 0.2
        transactions.append((statement_date + timedelta(days=12), "Private School Fees", monthly_income * 0.2, 0, current_balance))
        current_balance -= monthly_income * 0.3
        transactions.append((statement_date + timedelta(days=18), "Investment Transfer", monthly_income * 0.3, 0, current_balance))
        current_balance -= monthly_income * 0.1
        transactions.append((statement_date + timedelta(days=22), "Yacht Maintenance", monthly_income * 0.1, 0, current_balance))
        current_balance -= monthly_income * 0.05
        transactions.append((statement_date + timedelta(days=26), "Charitable Donation", monthly_income * 0.05, 0, current_balance))
        current_balance -= monthly_income * 0.2
        transactions.append((end_date, "Miscellaneous Expenses", monthly_income * 0.2, 0, balance))
    else:
        # Regular transactions
        transactions = []
        transactions.append((statement_date, "Opening Balance", 0, 0, current_balance))
        current_balance += monthly_income
        transactions.append((statement_date + timedelta(days=5), "Salary Credit", 0, monthly_income, current_balance))
        current_balance -= monthly_income * 0.3
        transactions.append((statement_date + timedelta(days=10), "Grocery Store", monthly_income * 0.3, 0, current_balance))
        current_balance -= monthly_income * 0.5
        transactions.append((statement_date + timedelta(days=15), "Rent Payment", monthly_income * 0.5, 0, current_balance))
        current_balance -= monthly_income * 0.1
        transactions.append((statement_date + timedelta(days=20), "Utility Bill", monthly_income * 0.1, 0, current_balance))
        current_balance -= monthly_income * 0.05
        transactions.append((statement_date + timedelta(days=25), "ATM Withdrawal", monthly_income * 0.05, 0, current_balance))
        current_balance -= monthly_income * 0.05
        transactions.append((end_date, "Miscellaneous", monthly_income * 0.05, 0, balance))
    
    for date, desc, debit, credit, bal in transactions:
        transactions_data.append([
            date.strftime('%d/%m/%Y'),
            desc,
            f"{debit:,.2f}" if debit > 0 else "-",
            f"{credit:,.2f}" if credit > 0 else "-",
            f"{bal:,.2f}"
        ])
    
    table = Table(transactions_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    
    doc.build(story)
    print(f"Generated bank statement PDF: {output_path}")


def generate_bank_statement_text(account_holder: str, account_number: str, 
                                 balance: float, monthly_income: float, is_wealthy: bool = False) -> str:
    """Generate bank statement text content."""
    statement_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    opening_balance = balance + (monthly_income * 0.1) if is_wealthy else balance + 2000
    
    # Calculate transactions with proper balances
    current_balance = opening_balance
    transactions_list = []
    
    if is_wealthy:
        transactions_list.append((statement_date, "Opening Balance", 0, 0, current_balance))
        current_balance += monthly_income
        transactions_list.append((statement_date + timedelta(days=3), "Salary Credit", 0, monthly_income, current_balance))
        current_balance += monthly_income * 0.5
        transactions_list.append((statement_date + timedelta(days=5), "Investment Return", 0, monthly_income * 0.5, current_balance))
        current_balance -= monthly_income * 0.15
        transactions_list.append((statement_date + timedelta(days=8), "Luxury Retail Purchase", monthly_income * 0.15, 0, current_balance))
        current_balance -= monthly_income * 0.2
        transactions_list.append((statement_date + timedelta(days=12), "Private School Fees", monthly_income * 0.2, 0, current_balance))
        current_balance -= monthly_income * 0.3
        transactions_list.append((statement_date + timedelta(days=18), "Investment Transfer", monthly_income * 0.3, 0, current_balance))
        current_balance -= monthly_income * 0.1
        transactions_list.append((statement_date + timedelta(days=22), "Yacht Maintenance", monthly_income * 0.1, 0, current_balance))
        current_balance -= monthly_income * 0.05
        transactions_list.append((statement_date + timedelta(days=26), "Charitable Donation", monthly_income * 0.05, 0, current_balance))
        current_balance -= monthly_income * 0.2
        transactions_list.append((end_date, "Miscellaneous Expenses", monthly_income * 0.2, 0, balance))
    else:
        transactions_list.append((statement_date, "Opening Balance", 0, 0, current_balance))
        current_balance += monthly_income
        transactions_list.append((statement_date + timedelta(days=5), "Salary Credit", 0, monthly_income, current_balance))
        current_balance -= monthly_income * 0.3
        transactions_list.append((statement_date + timedelta(days=10), "Grocery Store", monthly_income * 0.3, 0, current_balance))
        current_balance -= monthly_income * 0.5
        transactions_list.append((statement_date + timedelta(days=15), "Rent Payment", monthly_income * 0.5, 0, current_balance))
        current_balance -= monthly_income * 0.1
        transactions_list.append((statement_date + timedelta(days=20), "Utility Bill", monthly_income * 0.1, 0, current_balance))
        current_balance -= monthly_income * 0.05
        transactions_list.append((statement_date + timedelta(days=25), "ATM Withdrawal", monthly_income * 0.05, 0, current_balance))
        current_balance -= monthly_income * 0.05
        transactions_list.append((end_date, "Miscellaneous", monthly_income * 0.05, 0, balance))
    
    transactions_text = "Transactions:\nDate        Description              Debit      Credit     Balance\n"
    for date, desc, debit, credit, bal in transactions_list:
        debit_str = f"{debit:,.2f}" if debit > 0 else "-"
        credit_str = f"{credit:,.2f}" if credit > 0 else "-"
        transactions_text += f"{date.strftime('%d/%m/%Y')}  {desc:<25} {debit_str:>10}   {credit_str:>10}   {bal:>12,.2f}\n"
    
    statement_text = f"""
EMIRATES NBD BANK
Account Statement

Account No: {account_number}
Account Holder: {account_holder}
Statement Period: {statement_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}

Opening Balance: {opening_balance:,.2f} AED
Closing Balance: {balance:,.2f} AED

{transactions_text}
"""
    return statement_text


def generate_credit_report_pdf(output_path: str, name: str, id_number: str, 
                               credit_score: int, outstanding_debt: float, is_wealthy: bool = False):
    """Generate credit report as PDF.
    
    Args:
        output_path: Path to save the PDF
        name: Applicant name
        id_number: ID number
        credit_score: Credit score
        outstanding_debt: Total outstanding debt
        is_wealthy: If True, shows investment/commercial loans instead of personal loans
    """
    if not REPORTLAB_AVAILABLE:
        # Fallback to text file
        text = generate_credit_report_text(name, id_number, credit_score, outstanding_debt, is_wealthy)
        Path(output_path.replace('.pdf', '.txt')).write_text(text)
        return
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Header
    story.append(Paragraph("CREDIT BUREAU REPORT", styles['Heading1']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Applicant Information
    data = [
        ['Applicant:', name],
        ['ID:', id_number],
    ]
    table = Table(data, colWidths=[1.5*inch, 4.5*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Credit Score
    story.append(Paragraph(f"<b>CREDIT SCORE: {credit_score}</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Outstanding Debt
    story.append(Paragraph(f"<b>OUTSTANDING DEBT: {outstanding_debt:,.2f} AED</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    if is_wealthy:
        debt_data = [
            ['Investment Property Mortgage:', f"{outstanding_debt * 0.6:,.2f} AED"],
            ['Commercial Property Loan:', f"{outstanding_debt * 0.3:,.2f} AED"],
            ['Other Investment Financing:', f"{outstanding_debt * 0.1:,.2f} AED"],
        ]
    else:
        debt_data = [
            ['Personal Loan:', f"{outstanding_debt * 0.6:,.2f} AED"],
            ['Credit Card:', f"{outstanding_debt * 0.3:,.2f} AED"],
            ['Other:', f"{outstanding_debt * 0.1:,.2f} AED"],
        ]
    table = Table(debt_data, colWidths=[2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Payment History
    story.append(Paragraph("<b>PAYMENT HISTORY (Last 12 months):</b>", styles['Heading2']))
    on_time = 12 if credit_score > 650 else 8
    late = 0 if credit_score > 650 else 4
    missed = 0 if credit_score > 600 else 2
    
    payment_data = [
        ['On-time Payments:', str(on_time)],
        ['Late Payments:', str(late)],
        ['Missed Payments:', str(missed)],
    ]
    table = Table(payment_data, colWidths=[2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Account Status
    active_loans = 3 if is_wealthy and outstanding_debt > 0 else (2 if outstanding_debt > 0 else 0)
    story.append(Paragraph(f"<b>ACTIVE LOANS:</b> {active_loans}", styles['Normal']))
    story.append(Paragraph("<b>ACCOUNT STATUS:</b> Active", styles['Normal']))
    
    doc.build(story)
    print(f"Generated credit report PDF: {output_path}")


def generate_credit_report_text(name: str, id_number: str, credit_score: int, 
                               outstanding_debt: float, is_wealthy: bool = False) -> str:
    """Generate credit report text content."""
    if is_wealthy:
        debt_breakdown = f"""
OUTSTANDING DEBT: {outstanding_debt:,.2f} AED
- Investment Property Mortgage: {outstanding_debt * 0.6:,.2f} AED
- Commercial Property Loan: {outstanding_debt * 0.3:,.2f} AED
- Other Investment Financing: {outstanding_debt * 0.1:,.2f} AED
"""
        active_loans = 3 if outstanding_debt > 0 else 0
    else:
        debt_breakdown = f"""
OUTSTANDING DEBT: {outstanding_debt:,.2f} AED
- Personal Loan: {outstanding_debt * 0.6:,.2f} AED
- Credit Card: {outstanding_debt * 0.3:,.2f} AED
- Other: {outstanding_debt * 0.1:,.2f} AED
"""
        active_loans = 2 if outstanding_debt > 0 else 0
    
    report_text = f"""
CREDIT BUREAU REPORT
Report Date: {datetime.now().strftime('%d/%m/%Y')}

Applicant: {name}
ID: {id_number}

CREDIT SCORE: {credit_score}

{debt_breakdown}
PAYMENT HISTORY (Last 12 months):
On-time Payments: {12 if credit_score > 650 else 8}
Late Payments: {0 if credit_score > 650 else 4}
Missed Payments: {0 if credit_score > 600 else 2}

ACTIVE LOANS: {active_loans}
ACCOUNT STATUS: Active
"""
    return report_text


def generate_resume_pdf(output_path: str, name: str, email: str, phone: str, 
                       has_experience: bool = True, experience_type: str = "standard"):
    """Generate resume as PDF.
    
    Args:
        output_path: Path to save the PDF
        name: Applicant name
        email: Email address
        phone: Phone number
        has_experience: Whether applicant has work experience
        experience_type: "standard" for regular jobs, "executive" for high-level positions
    """
    if not REPORTLAB_AVAILABLE:
        # Fallback to text file
        text = generate_resume_text(name, email, phone, has_experience, experience_type)
        Path(output_path.replace('.pdf', '.txt')).write_text(text)
        return
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Name (Title)
    title_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=10,
    )
    story.append(Paragraph(name.upper(), title_style))
    story.append(Paragraph(f"Email: {email}", styles['Normal']))
    story.append(Paragraph(f"Phone: {phone}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Education
    story.append(Paragraph("EDUCATION", styles['Heading2']))
    if experience_type == "executive":
        story.append(Paragraph("Master of Business Administration (MBA)", styles['Normal']))
        story.append(Paragraph("INSEAD Business School, 2000-2002", styles['Normal']))
        story.append(Paragraph("Bachelor of Engineering, Computer Science", styles['Normal']))
        story.append(Paragraph("MIT, 1996-2000", styles['Normal']))
    else:
        story.append(Paragraph("Bachelor of Business Administration", styles['Normal']))
        story.append(Paragraph("Dubai University, 2010-2014", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Experience
    story.append(Paragraph("EXPERIENCE", styles['Heading2']))
    if has_experience:
        if experience_type == "executive":
            story.append(Paragraph("<b>Chief Executive Officer</b>", styles['Normal']))
            story.append(Paragraph("Gulf Technology Ventures, Dubai", styles['Normal']))
            story.append(Paragraph("2018-Present", styles['Normal']))
            story.append(Paragraph("• Lead strategic direction and oversee portfolio of technology investments", styles['Normal']))
            story.append(Paragraph("• Manage assets worth over 500 million AED", styles['Normal']))
            story.append(Paragraph("• Direct executive team of 50+ professionals", styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph("<b>Investment Director</b>", styles['Normal']))
            story.append(Paragraph("Dubai Investment Group, Dubai", styles['Normal']))
            story.append(Paragraph("2010-2018", styles['Normal']))
            story.append(Paragraph("• Managed private equity and real estate investment portfolios", styles['Normal']))
            story.append(Paragraph("• Achieved average annual returns of 25%+", styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph("<b>Senior Financial Analyst</b>", styles['Normal']))
            story.append(Paragraph("Goldman Sachs, London", styles['Normal']))
            story.append(Paragraph("2005-2010", styles['Normal']))
            story.append(Paragraph("• Analyzed investment opportunities in MENA region", styles['Normal']))
            story.append(Paragraph("• Structured complex financial transactions", styles['Normal']))
        else:
            story.append(Paragraph("<b>Sales Associate</b>", styles['Normal']))
            story.append(Paragraph("ABC Retail Store, Dubai", styles['Normal']))
            story.append(Paragraph("2015-2023", styles['Normal']))
            story.append(Paragraph("• Customer service and sales", styles['Normal']))
            story.append(Paragraph("• Inventory management", styles['Normal']))
            story.append(Paragraph("• Sales reporting and analysis", styles['Normal']))
    else:
        story.append(Paragraph("No previous work experience", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Skills
    story.append(Paragraph("SKILLS", styles['Heading2']))
    if experience_type == "executive":
        story.append(Paragraph("• Strategic Planning & Leadership", styles['Normal']))
        story.append(Paragraph("• Investment Management & Portfolio Analysis", styles['Normal']))
        story.append(Paragraph("• Financial Modeling & Risk Assessment", styles['Normal']))
        story.append(Paragraph("• Arabic, English, and French", styles['Normal']))
    else:
        story.append(Paragraph("• Communication", styles['Normal']))
        story.append(Paragraph("• Customer Service", styles['Normal']))
        story.append(Paragraph("• Microsoft Office", styles['Normal']))
        story.append(Paragraph("• Arabic and English", styles['Normal']))
    
    doc.build(story)
    print(f"Generated resume PDF: {output_path}")


def generate_resume_text(name: str, email: str, phone: str, 
                        has_experience: bool = True, experience_type: str = "standard") -> str:
    """Generate resume text content."""
    if has_experience:
        if experience_type == "executive":
            experience_section = """
EXPERIENCE
Chief Executive Officer
Gulf Technology Ventures, Dubai
2018-Present
- Lead strategic direction and oversee portfolio of technology investments
- Manage assets worth over 500 million AED
- Direct executive team of 50+ professionals

Investment Director
Dubai Investment Group, Dubai
2010-2018
- Managed private equity and real estate investment portfolios
- Achieved average annual returns of 25%+

Senior Financial Analyst
Goldman Sachs, London
2005-2010
- Analyzed investment opportunities in MENA region
- Structured complex financial transactions
"""
            education_section = """
EDUCATION
Master of Business Administration (MBA)
INSEAD Business School, 2000-2002
Bachelor of Engineering, Computer Science
MIT, 1996-2000
"""
            skills_section = """
SKILLS
- Strategic Planning & Leadership
- Investment Management & Portfolio Analysis
- Financial Modeling & Risk Assessment
- Arabic, English, and French
"""
        else:
            experience_section = """
EXPERIENCE
Sales Associate
ABC Retail Store, Dubai
2015-2023
- Customer service and sales
- Inventory management
- Sales reporting and analysis
"""
            education_section = """
EDUCATION
Bachelor of Business Administration
Dubai University, 2010-2014
"""
            skills_section = """
SKILLS
- Communication
- Customer Service
- Microsoft Office
- Arabic and English
"""
    else:
        experience_section = """
EXPERIENCE
No previous work experience
"""
        education_section = """
EDUCATION
Bachelor of Business Administration
Dubai University, 2010-2014
"""
        skills_section = """
SKILLS
- Communication
- Customer Service
- Microsoft Office
- Arabic and English
"""
    
    resume_text = f"""
{name.upper()}
Email: {email}
Phone: {phone}

{education_section}

{experience_section}

{skills_section}
"""
    return resume_text


def generate_eligible_applicant_documents(output_dir: str = "test_documents/eligible_applicant"):
    """Generate complete set of documents for an eligible applicant."""
    test_dir = Path(output_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Eligible applicant profile: Low income, large family, unemployed, financial need
    applicant_name = "Fatima Ali Al-Hashimi"
    applicant_id = "784-1990-2345678-2"
    monthly_income = 2800  # Low income
    family_size = 5  # Large family
    employment_status = "Unemployed"
    address = "Apartment 45, Building 12, Al Qusais, Dubai, UAE"
    account_number = "9876543210987654"
    bank_balance = 1200  # Low balance
    credit_score = 580  # Moderate credit score
    outstanding_debt = 15000  # Significant debt relative to income
    
    print("=" * 60)
    print("Generating ELIGIBLE APPLICANT documents...")
    print("=" * 60)
    print(f"Applicant: {applicant_name}")
    print(f"Income: {monthly_income:,} AED/month")
    print(f"Family Size: {family_size}")
    print(f"Employment: {employment_status}")
    print(f"Expected Outcome: APPROVE")
    print(f"Output directory: {test_dir.absolute()}")
    print()
    
    # Generate Assets/Liabilities Excel (low net worth)
    excel_path = test_dir / "assets_liabilities.xlsx"
    generate_assets_liabilities_excel(str(excel_path), "low_income")
    print(f"✓ Generated: {excel_path.name}")
    
    # Generate Application Form
    app_form = test_dir / "application_form.pdf"
    generate_application_form_pdf(
        str(app_form), applicant_name, monthly_income, family_size, 
        employment_status, address
    )
    print(f"✓ Generated: {app_form.name}")
    
    # Generate Bank Statement (low balance, minimal transactions)
    bank_stmt = test_dir / "bank_statement.pdf"
    generate_bank_statement_pdf(
        str(bank_stmt), applicant_name, account_number, bank_balance, monthly_income
    )
    print(f"✓ Generated: {bank_stmt.name}")
    
    # Generate Credit Report (moderate score, manageable debt)
    credit_rpt = test_dir / "credit_report.pdf"
    generate_credit_report_pdf(
        str(credit_rpt), applicant_name, applicant_id, credit_score, outstanding_debt
    )
    print(f"✓ Generated: {credit_rpt.name}")
    
    # Generate Resume (limited recent experience, unemployed)
    resume = test_dir / "resume.pdf"
    generate_resume_pdf(
        str(resume), applicant_name, 
        f"{applicant_name.lower().replace(' ', '.')}@email.com",
        "+971-50-987-6543", has_experience=False  # Limited experience
    )
    print(f"✓ Generated: {resume.name}")
    
    print()
    print("=" * 60)
    print("✅ All documents generated successfully!")
    print("=" * 60)
    print()
    print("📋 Document Summary:")
    print(f"  • Application Form: {app_form.name}")
    print(f"  • Bank Statement: {bank_stmt.name}")
    print(f"  • Credit Report: {credit_rpt.name}")
    print(f"  • Resume: {resume.name}")
    print(f"  • Assets/Liabilities: {excel_path.name}")
    print()
    print("💡 Note: For Emirates ID, create an image file (JPG/PNG)")
    print("   with ID information visible.")
    print()
    print("📊 Eligibility Profile:")
    print(f"   - Income Level: Very Low ({monthly_income:,} AED/month)")
    print(f"   - Family Size: Large ({family_size} members)")
    print(f"   - Employment: {employment_status}")
    print(f"   - Financial Need: High")
    print(f"   - Expected Recommendation: APPROVE")
    print()
    
    return test_dir


def generate_wealthy_applicant_documents(output_dir: str = "test_documents/wealthy_applicant"):
    """Generate complete set of documents for a highly wealthy applicant."""
    test_dir = Path(output_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Wealthy applicant profile: Very high income, high net worth, executive position
    applicant_name = "Ahmed Hassan Al-Zahra"
    applicant_id = "784-1978-8765432-1"
    monthly_income = 450000  # Very high income (executive/CEO level)
    family_size = 6  # Large family but with high income
    employment_status = "CEO - Technology Investments"
    address = "Villa 15, Emirates Hills, Dubai, UAE"
    account_number = "4444444444444444"
    bank_balance = 8500000  # Very high balance
    credit_score = 850  # Excellent credit score
    outstanding_debt = 3500000  # High absolute debt but low relative to assets
    
    print("=" * 60)
    print("Generating WEALTHY APPLICANT documents...")
    print("=" * 60)
    print(f"Applicant: {applicant_name}")
    print(f"Income: {monthly_income:,} AED/month")
    print(f"Family Size: {family_size}")
    print(f"Employment: {employment_status}")
    print(f"Expected Outcome: REJECT (Not eligible for social support)")
    print(f"Output directory: {test_dir.absolute()}")
    print()
    
    # Generate Assets/Liabilities Excel (high net worth)
    excel_path = test_dir / "assets_liabilities.xlsx"
    generate_assets_liabilities_excel(str(excel_path), "wealthy")
    print(f"✓ Generated: {excel_path.name}")
    
    # Generate Application Form
    app_form = test_dir / "application_form.pdf"
    generate_application_form_pdf(
        str(app_form), applicant_name, monthly_income, family_size, 
        employment_status, address
    )
    print(f"✓ Generated: {app_form.name}")
    
    # Generate Bank Statement (high balance, large transactions)
    bank_stmt = test_dir / "bank_statement.pdf"
    generate_bank_statement_pdf(
        str(bank_stmt), applicant_name, account_number, bank_balance, monthly_income, is_wealthy=True
    )
    print(f"✓ Generated: {bank_stmt.name}")
    
    # Generate Credit Report (excellent score, manageable debt relative to assets)
    credit_rpt = test_dir / "credit_report.pdf"
    generate_credit_report_pdf(
        str(credit_rpt), applicant_name, applicant_id, credit_score, outstanding_debt, is_wealthy=True
    )
    print(f"✓ Generated: {credit_rpt.name}")
    
    # Generate Resume (extensive executive experience)
    resume = test_dir / "resume.pdf"
    generate_resume_pdf(
        str(resume), applicant_name, 
        f"{applicant_name.lower().replace(' ', '.')}@email.com",
        "+971-50-888-7777", has_experience=True, experience_type="executive"
    )
    print(f"✓ Generated: {resume.name}")
    
    print()
    print("=" * 60)
    print("✅ All documents generated successfully!")
    print("=" * 60)
    print()
    print("📋 Document Summary:")
    print(f"  • Application Form: {app_form.name}")
    print(f"  • Bank Statement: {bank_stmt.name}")
    print(f"  • Credit Report: {credit_rpt.name}")
    print(f"  • Resume: {resume.name}")
    print(f"  • Assets/Liabilities: {excel_path.name}")
    print()
    print("💡 Note: For Emirates ID, create an image file (JPG/PNG)")
    print("   with ID information visible.")
    print()
    print("📊 Wealth Profile:")
    print(f"   - Income Level: Very High ({monthly_income:,} AED/month)")
    print(f"   - Net Worth: Extremely High (Multi-million AED)")
    print(f"   - Employment: {employment_status}")
    print(f"   - Financial Need: None (Self-sufficient)")
    print(f"   - Expected Recommendation: REJECT (Not eligible)")
    print()
    
    return test_dir


if __name__ == "__main__":
    import sys
    
    # Check if user wants eligible or wealthy applicant
    if len(sys.argv) > 1 and sys.argv[1] == "eligible":
        generate_eligible_applicant_documents()
    elif len(sys.argv) > 1 and sys.argv[1] == "wealthy":
        generate_wealthy_applicant_documents()
    else:
        # Default: Generate standard test documents
        test_dir = Path("test_documents")
        test_dir.mkdir(exist_ok=True)
        
        # Example applicant data
        applicant_name = "Mohammed Uzair"
        applicant_id = "784-1985-1234567-1"
        monthly_income = 25000
        family_size = 4
        employment_status = "Employed"
        address = "Villa 123, Palm Jumeriah, Dubai, UAE"
        account_number = "1234567890123456"
        bank_balance = 3000000
        credit_score = 720
        outstanding_debt = 0
        
        print("Generating synthetic documents...")
        print(f"Output directory: {test_dir.absolute()}")
        print()
        print("💡 Tip: Run with arguments to generate specific applicant types:")
        print("   python3 scripts/generate_synthetic_documents.py eligible  # Low-income eligible applicant")
        print("   python3 scripts/generate_synthetic_documents.py wealthy   # High-wealth applicant")
        print()
        
        # Generate Assets/Liabilities Excel
        excel_path = test_dir / "assets_liabilities_low_income.xlsx"
        generate_assets_liabilities_excel(str(excel_path), "low_income")
        
        # Generate PDF files
        app_form = test_dir / "application_form.pdf"
        generate_application_form_pdf(
            str(app_form), applicant_name, monthly_income, family_size, 
            employment_status, address
        )
        
        bank_stmt = test_dir / "bank_statement.pdf"
        generate_bank_statement_pdf(
            str(bank_stmt), applicant_name, account_number, bank_balance, monthly_income
        )
        
        credit_rpt = test_dir / "credit_report.pdf"
        generate_credit_report_pdf(
            str(credit_rpt), applicant_name, applicant_id, credit_score, outstanding_debt
        )
        
        resume = test_dir / "resume.pdf"
        generate_resume_pdf(
            str(resume), applicant_name, 
            f"{applicant_name.lower().replace(' ', '.')}@email.com",
            "+971-50-123-4567", has_experience=True
        )
        
        print()
        print("Note: For Emirates ID, create an image file (JPG/PNG) with the ID information visible.")
        print("See docs/SYNTHETIC_DOCUMENTS_GUIDE.md for detailed templates.")

