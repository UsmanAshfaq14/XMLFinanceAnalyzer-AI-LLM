import xml.etree.ElementTree as ET
import re
from datetime import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def validate_date_format(date_str):
    """Validate that the date is in YYYY-MM-DD format"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_positive_number(value):
    """Validate that a value is a positive number"""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_xml_data(xml_data):
    """Validate the XML data structure and content"""
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return False, "ERROR: Invalid XML format. Please check your XML structure."
    
    reports = root.findall('./report')
    if not reports:
        return False, "ERROR: No report elements found in the XML."
    
    validation_summary = {
        "num_reports": len(reports),
        "reports_validation": []
    }
    
    required_fields = ['company_name', 'report_date', 'revenue', 'expenses', 'net_income', 'assets', 'liabilities']
    numeric_fields = ['revenue', 'expenses', 'net_income', 'assets', 'liabilities']
    
    all_valid = True
    
    for i, report in enumerate(reports):
        report_validation = {
            "index": i + 1,
            "missing_fields": [],
            "invalid_fields": [],
            "data": {}
        }
        
        # Check for missing fields
        for field in required_fields:
            field_elem = report.find(field)
            if field_elem is None or field_elem.text is None or field_elem.text.strip() == '':
                report_validation["missing_fields"].append(field)
                all_valid = False
            else:
                report_validation["data"][field] = field_elem.text.strip()
        
        # Check data types and values
        if 'report_date' in report_validation["data"] and not validate_date_format(report_validation["data"]["report_date"]):
            report_validation["invalid_fields"].append("report_date")
            all_valid = False
        
        for field in numeric_fields:
            if field in report_validation["data"] and not validate_positive_number(report_validation["data"][field]):
                report_validation["invalid_fields"].append(field)
                all_valid = False
        
        validation_summary["reports_validation"].append(report_validation)
    
    return all_valid, validation_summary

def calculate_metrics(report_data):
    """Calculate financial metrics based on the report data"""
    # Convert string values to float for calculations
    revenue = float(report_data["revenue"])
    expenses = float(report_data["expenses"])
    net_income = float(report_data["net_income"])
    assets = float(report_data["assets"])
    liabilities = float(report_data["liabilities"])
    
    # Calculate metrics
    profit_margin_step = net_income / revenue
    profit_margin = profit_margin_step * 100
    
    debt_to_asset_ratio = liabilities / assets
    
    operating_expense_ratio_step = expenses / revenue
    operating_expense_ratio = operating_expense_ratio_step * 100
    
    liquidity_ratio_diff = assets - liabilities
    liquidity_ratio = liquidity_ratio_diff / assets
    
    # Generate recommendation
    if profit_margin >= 20 and debt_to_asset_ratio <= 0.5 and liquidity_ratio >= 0.2:
        recommendation = f"The financial health of {report_data['company_name']} appears strong. No immediate corrective actions are necessary."
    else:
        recommendation = f"Financial warning for {report_data['company_name']}: Consider reducing expenses, improving revenue generation, or restructuring liabilities."
    
    return {
        "profit_margin": round(profit_margin, 2),
        "profit_margin_step": round(profit_margin_step, 4),
        "debt_to_asset_ratio": round(debt_to_asset_ratio, 2),
        "operating_expense_ratio": round(operating_expense_ratio, 2),
        "operating_expense_ratio_step": round(operating_expense_ratio_step, 4),
        "liquidity_ratio": round(liquidity_ratio, 2),
        "liquidity_ratio_diff": round(liquidity_ratio_diff, 2),
        "recommendation": recommendation
    }

def generate_validation_report(validation_summary):
    """Generate markdown validation report"""
    report = "# Data Validation Report\n"
    report += "## Data Structure Check:\n"
    report += f"- Number of reports: {validation_summary['num_reports']}\n"
    
    report += "\n## Reports Validation:\n"
    
    for report_val in validation_summary["reports_validation"]:
        report += f"\n### Report {report_val['index']}:\n"
        
        report += "#### Required Fields Check:\n"
        all_fields_present = True
        for field in ['company_name', 'report_date', 'revenue', 'expenses', 'net_income', 'assets', 'liabilities']:
            status = "missing" if field in report_val["missing_fields"] else "present"
            report += f"- {field}: {status}\n"
            if status == "missing":
                all_fields_present = False
        
        report += "\n#### Data Validation Check:\n"
        all_data_valid = True
        for field in report_val["invalid_fields"]:
            report += f"- {field}: invalid\n"
            all_data_valid = False
        
        if not report_val["invalid_fields"]:
            report += "- All present fields are valid\n"
        
        report += "\n#### Validation Result:\n"
        if all_fields_present and all_data_valid:
            report += "- ✓ Validation successful\n"
        else:
            report += "- ✗ Validation failed\n"
    
    report += "\n## Validation Summary\n"
    if all(len(r["missing_fields"]) == 0 and len(r["invalid_fields"]) == 0 for r in validation_summary["reports_validation"]):
        report += "Data validation is successful! Proceeding with analysis.\n"
    else:
        report += "Data validation failed. Please correct the errors and submit again.\n"
    
    return report

def generate_financial_analysis(report_data, metrics):
    """Generate markdown financial analysis report with LaTeX formulas"""
    report = f"# Financial Analysis Summary\n"
    report += f"Total Reports Analyzed: 1\n\n"
    
    report += f"## Detailed Analysis for {report_data['company_name']}\n\n"
    
    # Input Data
    report += f"### Input Data:\n"
    report += f"- **Report Date:** {report_data['report_date']}\n"
    report += f"- **Revenue:** ${report_data['revenue']}\n"
    report += f"- **Expenses:** ${report_data['expenses']}\n"
    report += f"- **Net Income:** ${report_data['net_income']}\n"
    report += f"- **Assets:** ${report_data['assets']}\n"
    report += f"- **Liabilities:** ${report_data['liabilities']}\n\n"
    
    # Step-by-Step Calculations
    report += f"### Step-by-Step Calculations:\n\n"
    
    # 1. Profit Margin
    report += f"#### 1. Profit Margin Calculation:\n"
    report += f"- **Formula:**  \n"
    report += f"  $$ \\text{{Profit Margin}} = \\left(\\frac{{\\text{{Net Income}}}}{{\\text{{Revenue}}}}\\right) \\times 100 $$\n"
    report += f"- **Calculation Steps:**\n"
    report += f"  1. **Division:** Divide Net Income by Revenue:  \n"
    report += f"     $$ Step = \\frac{{{report_data['net_income']}}}{{{report_data['revenue']}}} = {metrics['profit_margin_step']} $$\n"
    report += f"  2. **Conversion to Percentage:** Multiply the result by 100:  \n"
    report += f"     $$ \\text{{Profit Margin}} = {metrics['profit_margin_step']} \\times 100 = {metrics['profit_margin']}\\% $$\n"
    report += f"- **Final Profit Margin:** {metrics['profit_margin']}%\n\n"
    
    # 2. Debt-to-Asset Ratio
    report += f"#### 2. Debt-to-Asset Ratio Calculation:\n"
    report += f"- **Formula:**  \n"
    report += f"  $$ \\text{{Debt-to-Asset Ratio}} = \\frac{{\\text{{Liabilities}}}}{{\\text{{Assets}}}} $$\n"
    report += f"- **Calculation Steps:**\n"
    report += f"  1. **Division:** Divide Liabilities by Assets:  \n"
    report += f"     $$ \\text{{Debt-to-Asset Ratio}} = \\frac{{{report_data['liabilities']}}}{{{report_data['assets']}}} = {metrics['debt_to_asset_ratio']} $$\n"
    report += f"- **Final Debt-to-Asset Ratio:** {metrics['debt_to_asset_ratio']}\n\n"
    
    # 3. Operating Expense Ratio
    report += f"#### 3. Operating Expense Ratio Calculation:\n"
    report += f"- **Formula:**  \n"
    report += f"  $$ \\text{{Operating Expense Ratio}} = \\left(\\frac{{\\text{{Expenses}}}}{{\\text{{Revenue}}}}\\right) \\times 100 $$\n"
    report += f"- **Calculation Steps:**\n"
    report += f"  1. **Division:** Divide Expenses by Revenue:  \n"
    report += f"     $$ Step = \\frac{{{report_data['expenses']}}}{{{report_data['revenue']}}} = {metrics['operating_expense_ratio_step']} $$\n"
    report += f"  2. **Conversion to Percentage:** Multiply the result by 100:  \n"
    report += f"     $$ \\text{{Operating Expense Ratio}} = {metrics['operating_expense_ratio_step']} \\times 100 = {metrics['operating_expense_ratio']}\\% $$\n"
    report += f"- **Final Operating Expense Ratio:** {metrics['operating_expense_ratio']}%\n\n"
    
    # 4. Liquidity Ratio
    report += f"#### 4. Liquidity Ratio Calculation:\n"
    report += f"- **Formula:**  \n"
    report += f"  $$ \\text{{Liquidity Ratio}} = \\frac{{\\text{{Assets}} - \\text{{Liabilities}}}}{{\\text{{Assets}}}} $$\n"
    report += f"- **Calculation Steps:**\n"
    report += f"  1. **Subtraction:** Calculate the difference between Assets and Liabilities:  \n"
    report += f"     $$ Difference = {report_data['assets']} - {report_data['liabilities']} = {metrics['liquidity_ratio_diff']} $$\n"
    report += f"  2. **Division:** Divide the difference by Assets:  \n"
    report += f"     $$ \\text{{Liquidity Ratio}} = \\frac{{{metrics['liquidity_ratio_diff']}}}{{{report_data['assets']}}} = {metrics['liquidity_ratio']} $$\n"
    report += f"- **Final Liquidity Ratio:** {metrics['liquidity_ratio']}\n\n"
    
    # Final Recommendation
    report += f"### Final Financial Recommendation:\n\n"
    report += f"- **Thresholds for Evaluation:**\n"
    report += f"  - Profit Margin should be **greater than or equal to 20%**.\n"
    report += f"  - Debt-to-Asset Ratio should be **less than or equal to 0.5**.\n"
    report += f"  - Liquidity Ratio should be **greater than or equal to 0.2**.\n\n"
    
    report += f"- **Decision Logic:**\n"
    report += f"  - **IF** Profit Margin ≥ 20% **AND** Debt-to-Asset Ratio ≤ 0.5 **AND** Liquidity Ratio ≥ 0.2,  \n"
    report += f"    **THEN**:  \n"
    report += f"    \"The financial health of {report_data['company_name']} appears strong. No immediate corrective actions are necessary.\"\n"
    report += f"  - **ELSE**:  \n"
    report += f"    \"Financial warning for {report_data['company_name']}: Consider reducing expenses, improving revenue generation, or restructuring liabilities.\"\n\n"
    
    report += f"**Final Recommendation for {report_data['company_name']}:**  \n"
    report += f"{metrics['recommendation']}\n"
    
    return report

def process_xml_data(xml_data):
    """Main function to process XML data and generate reports"""
    valid, validation_result = validate_xml_data(xml_data)
    validation_report = generate_validation_report(validation_result)
    
    if not valid:
        return validation_report
    
    reports_analysis = []
    for report_val in validation_result["reports_validation"]:
        if report_val["missing_fields"] or report_val["invalid_fields"]:
            continue
        
        metrics = calculate_metrics(report_val["data"])
        analysis_report = generate_financial_analysis(report_val["data"], metrics)
        reports_analysis.append(analysis_report)
    
    # Combine validation report and analysis reports
    final_report = validation_report + "\n\n" + "\n\n".join(reports_analysis)
    return final_report

# Sample XML data - Replace this with your actual data
xml_data = """
<financial_reports>
<report>
<company_name>Theta Fusion</company_name>
<report_date>2023-12-15</report_date>
<revenue>5500000</revenue>
<expenses>3300000</expenses>
<net_income>2200000</net_income>
<assets>10000000</assets>
<liabilities>4000000</liabilities>
</report>
<report>
<company_name>Omicron Energy</company_name>
<report_date>2023-12-18</report_date>
<revenue>6000000</revenue>
<expenses>3600000</expenses>
<net_income>2400000</net_income>
<assets>11000000</assets>
<liabilities>4500000</liabilities>
</report>
<report>
<company_name>Psi Solutions</company_name>
<report_date>2023-12-20</report_date>
<revenue>7000000</revenue>
<expenses>4200000</expenses>
<net_income>2800000</net_income>
<assets>12000000</assets>
<liabilities>5000000</liabilities>
</report>
<report>
<company_name>Sigma Innovations</company_name>
<report_date>2023-12-22</report_date>
<revenue>8000000</revenue>
<expenses>4800000</expenses>
<net_income>3200000</net_income>
<assets>13000000</assets>
<liabilities>5500000</liabilities>
</report>
<report>
<company_name>Alpha Quantum</company_name>
<report_date>2023-12-25</report_date>
<revenue>9000000</revenue>
<expenses>5400000</expenses>
<net_income>3600000</net_income>
<assets>14000000</assets>
<liabilities>6000000</liabilities>
</report>
</financial_reports>
"""

# Process the data and print the report
report = process_xml_data(xml_data)
print(report)