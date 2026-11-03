from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List

from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


OUT_DIR = Path(__file__).resolve().parent
INTERNAL_PATH = OUT_DIR / "AMAKids_Internal_Financial_Calculator.xlsx"
DEMO_PATH = OUT_DIR / "AMAKids_Demo_One_Center.xlsx"

NAVY = "17365D"
BLUE = "2F75B5"
LIGHT_BLUE = "D9EAF7"
PALE_BLUE = "EAF3F8"
YELLOW = "FFF2CC"
GREEN = "70AD47"
LIGHT_GREEN = "E2F0D9"
RED = "C00000"
LIGHT_RED = "FCE4D6"
GRAY = "D9E1F2"
LIGHT_GRAY = "F2F2F2"
WHITE = "FFFFFF"
ORANGE = "ED7D31"

thin_gray = Side(style="thin", color="B7C9D6")
border = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=thin_gray)


@dataclass
class Product:
    enabled: int
    name: str
    gross_price: float
    vat_applicable: int
    lessons_month: int
    groups: int
    target_group: int
    max_group: int
    teacher_cost_class: float
    materials_revenue: float
    materials_cost: float
    lead_share: float
    churn: float
    retention: float
    course_months: int
    note: str = ""


@dataclass
class StaffRole:
    role: str
    fte: float
    gross_salary: float
    employer_load: float
    start_month: int
    note: str = ""


PRODUCTS = [
    Product(1, "Mental Arithmetic", 110, 0, 4, 2, 10, 12, 25, 35, 18, 0.50, 0.04, 0.65, 10,
            "Two groups; one 90-minute lesson per week"),
    Product(1, "English", 100, 0, 4, 2, 10, 12, 28, 25, 12, 0.50, 0.04, 0.65, 10,
            "Two groups; one 90-minute lesson per week"),
    Product(0, "Memorica", 90, 1, 4, 0, 8, 10, 25, 30, 15, 0.00, 0.05, 0.60, 9),
    Product(0, "Programming", 110, 1, 4, 0, 8, 10, 30, 20, 10, 0.00, 0.05, 0.60, 9),
    Product(0, "Online course", 70, 1, 4, 0, 10, 12, 20, 10, 5, 0.00, 0.06, 0.55, 9),
    Product(0, "Summer camp", 180, 1, 1, 0, 12, 16, 90, 0, 40, 0.00, 0.00, 0.00, 1),
]

STAFF = [
    StaffRole("Administrator", 0.50, 800, 0.00, 1, "Part-time at launch"),
    StaffRole("Additional administrator", 0.50, 800, 0.00, 13, "Added when the center grows to six groups"),
    StaffRole("Sales manager", 0.00, 1000, 0.00, 1, "Enable when lead flow requires it"),
    StaffRole("Center manager", 0.50, 1300, 0.00, 25, "Half-time management role from the third year"),
    StaffRole("SMM / local content", 0.20, 700, 0.00, 1, "Part-time; media budget is separate"),
    StaffRole("Cleaner", 0.20, 350, 0.00, 1, "Part-time / contractor equivalent"),
    StaffRole("Substitute / coordinator", 0.00, 900, 0.00, 13, "Optional after scale-up"),
]

FIXED_COSTS = [
    ("Rent", 700, "Regional city, approximately 70–90 sqm"),
    ("Utilities and service charge", 120, "Electricity, heating, water, building service"),
    ("Software / CRM / communication", 50, "Recurring subscriptions"),
    ("Accounting and payroll", 80, "Local outsourced provider"),
    ("Insurance", 25, "Business and public liability"),
    ("Cleaning supplies and consumables", 45, "Excludes cleaner salary"),
    ("Repairs and maintenance", 40, "Monthly reserve"),
    ("Bank fees", 30, "Excludes card acquiring fee"),
    ("Other fixed costs", 50, "Contingency for recurring small costs"),
]

CAPEX = [
    ("Franchise / territory fee", 4000, 0, 1, 1, "One-time contractual payment"),
    ("Rental deposit", 1400, 0, 1, 1, "Recoverable at exit; included in funding need"),
    ("Renovation and fit-out", 4500, 1, 60, 1, "Light renovation for a leased premise"),
    ("Furniture and classroom equipment", 3000, 1, 60, 1, "Desks, chairs, storage, boards"),
    ("Laptops, screens and devices", 1200, 1, 36, 1, "Teaching equipment"),
    ("Inside and outside branding", 900, 1, 36, 1, "Signs and visual materials"),
    ("Pre-opening marketing", 800, 0, 1, 1, "Separate from monthly acquisition budget"),
    ("Registration, legal and permits", 300, 0, 1, 1, "Country-specific"),
    ("Initial teaching materials", 600, 0, 1, 1, "Opening stock"),
]


def style_title(ws, title: str, end_col: int = 8) -> None:
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    c = ws.cell(1, 1, title)
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.font = Font(color=WHITE, bold=True, size=16)
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 28


def section(ws, row: int, title: str, end_col: int) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=end_col)
    c = ws.cell(row, 1, title)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.font = Font(color=WHITE, bold=True)
    c.alignment = Alignment(horizontal="left")


def header_row(ws, row: int, start_col: int, end_col: int) -> None:
    for col in range(start_col, end_col + 1):
        c = ws.cell(row, col)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.font = Font(color=WHITE, bold=True)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border


def input_cell(cell, number_format: str | None = None) -> None:
    cell.fill = PatternFill("solid", fgColor=YELLOW)
    cell.font = Font(color="1F4E78")
    cell.border = border
    if number_format:
        cell.number_format = number_format


def formula_cell(cell, number_format: str | None = None) -> None:
    cell.fill = PatternFill("solid", fgColor=PALE_BLUE)
    cell.border = border
    if number_format:
        cell.number_format = number_format


def label_cell(cell) -> None:
    cell.border = border
    cell.alignment = Alignment(vertical="top", wrap_text=True)


def setup_sheet(ws, freeze: str = "A2") -> None:
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = freeze
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0


def build_readme(wb: Workbook, demo: bool = False) -> None:
    ws = wb.create_sheet("00_README")
    style_title(ws, "AMAKids financial model — user guide", 8)
    setup_sheet(ws, "A4")
    ws.column_dimensions["A"].width = 23
    ws.column_dimensions["B"].width = 95
    ws.column_dimensions["C"].width = 24
    rows = [
        ("Purpose", "Presentation example for one center" if demo else
         "Internal 60-month calculator for assessing a specific center request"),
        ("How to use", "Change only yellow cells. Blue cells contain formulas. Select a scenario on 01_INPUTS."),
        ("Revenue logic", "Students are carried month to month. New students come from the funnel and are capped by planned group capacity. July and August are non-billing months in the base school-year pattern."),
        ("Tax logic", "Customer prices are entered gross. VAT is removed only for products marked taxable. Corporate income tax is applied to positive EBIT. Replace both rates and taxability with local professional advice."),
        ("Capacity", "Planned capacity = planned groups × target group size. Maximum capacity is shown separately and should not be used as the normal operating target."),
        ("Cash flow", "The model includes opening investment, operating cash flow and cumulative project cash flow. It does not assume debt financing."),
        ("Important", "This is a decision-support model, not accounting or tax advice. Validate price, rent, payroll burden, VAT treatment and conversion metrics for each location."),
        ("Demo basis", "Generic regional European city; assumptions are broadly consistent with a Romanian regional-city price level. No city name is used in presentation output."),
        ("Color legend", "Yellow = input; pale blue = formula; green = positive status; red = warning."),
    ]
    start = 4
    for i, (a, b) in enumerate(rows, start):
        ws.cell(i, 1, a).font = Font(bold=True, color=NAVY)
        ws.cell(i, 2, b).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(i, 1).border = ws.cell(i, 2).border = border
        ws.row_dimensions[i].height = 38 if i not in (start + 6,) else 52
    ws.cell(start + len(rows) + 2, 1, "Workbook sheets").font = Font(bold=True, color=WHITE)
    ws.cell(start + len(rows) + 2, 1).fill = PatternFill("solid", fgColor=BLUE)
    sheet_notes = [
        ("01_INPUTS", "Global assumptions, market, funnel, seasonality and fixed costs"),
        ("02_PRODUCTS", "Product economics, group sizes, prices and teacher cost"),
        ("02A_GROUP_PLAN", "Planned number of groups by product and model year"),
        ("03_STAFF", "Fixed monthly staff and employer cost"),
        ("04_CAPEX", "Opening investment and depreciation lives"),
        ("05_SCENARIOS", "Base, conservative and optimistic multipliers"),
        ("06_MODEL", "Monthly operating model"),
        ("07_ANNUAL", "Annual P&L and cash-flow summary"),
        ("08_DASHBOARD", "Decision metrics and charts"),
        ("09_CHECKS", "Structural and input quality checks"),
    ]
    rr = start + len(rows) + 3
    for name, desc in sheet_notes:
        ws.cell(rr, 1, name).font = Font(bold=True, color=NAVY)
        ws.cell(rr, 2, desc)
        ws.cell(rr, 1).border = ws.cell(rr, 2).border = border
        rr += 1


def build_inputs(wb: Workbook, horizon: int) -> Dict[str, int]:
    ws = wb.create_sheet("01_INPUTS")
    style_title(ws, "01 — Global assumptions", 14)
    setup_sheet(ws, "A5")
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 64
    for col in range(4, 15):
        ws.column_dimensions[chr(64 + col)].width = 12

    section(ws, 3, "Model control", 3)
    data = [
        (4, "Selected scenario", "Base", "Choose Base, Conservative or Optimistic"),
        (5, "Currency", "EUR", "Presentation and model currency"),
        (6, "Start date", date(2027, 9, 1), "First operating month"),
        (7, "Model horizon, months", horizon, "Fixed model length"),
        (8, "Corporate income tax", 0.20, "Applied to positive EBIT"),
        (9, "Standard VAT", 0.20, "Products can be marked VAT-exempt separately"),
        (10, "Royalty on net revenue", 0.10, "Franchise royalty"),
        (11, "Marketing fund on net revenue", 0.02, "Central brand contribution"),
        (12, "Card / collection fee on gross revenue", 0.02, "Acquiring and payment cost"),
        (13, "Annual price inflation", 0.03, "Automatic annual increase"),
        (14, "Annual non-payroll cost inflation", 0.03, "Rent and other recurring costs"),
        (15, "Annual salary inflation", 0.05, "Staff and teaching rates"),
        (16, "Target minimum cash buffer", 5000, "Management reserve, not an expense"),
    ]
    for r, label, value, note in data:
        ws.cell(r, 1, label); label_cell(ws.cell(r, 1))
        ws.cell(r, 2, value); input_cell(ws.cell(r, 2))
        ws.cell(r, 3, note); label_cell(ws.cell(r, 3))
    for r in range(8, 16):
        ws.cell(r, 2).number_format = "0.0%"
    ws.cell(16, 2).number_format = '€#,##0'
    ws.cell(6, 2).number_format = "mmm yyyy"
    dv = DataValidation(type="list", formula1='"Base,Conservative,Optimistic"', allow_blank=False)
    ws.add_data_validation(dv); dv.add(ws["B4"])

    section(ws, 18, "Market and commercial assumptions", 3)
    market = [
        (19, "City population", 150000, "Reference size for a medium regional city"),
        (20, "Target-age children as % population", 0.11, "Replace with local demographic data"),
        (21, "Share affordable / relevant", 0.25, "Households realistically able and willing to buy"),
        (22, "Catchment reach", 0.60, "Travel time and location accessibility"),
        (23, "Target share of addressable market", 0.015, "Long-term center penetration"),
        (24, "Addressable children", "=B19*B20*B21*B22", "Formula"),
        (25, "Target unique students", "=B24*B23", "Sanity check, not a capacity input"),
    ]
    for r, label, value, note in market:
        ws.cell(r, 1, label); label_cell(ws.cell(r, 1))
        ws.cell(r, 2, value)
        (formula_cell if isinstance(value, str) and value.startswith("=") else input_cell)(ws.cell(r, 2))
        ws.cell(r, 3, note); label_cell(ws.cell(r, 3))
    for r in (20, 21, 22, 23): ws.cell(r, 2).number_format = "0.0%"
    for r in (19, 24, 25): ws.cell(r, 2).number_format = "#,##0"

    section(ws, 27, "Acquisition funnel", 3)
    funnel = [
        (28, "Base monthly paid-media budget", 300, "Normal operating month"),
        (29, "Launch monthly paid-media budget", 600, "Used during launch period"),
        (30, "Launch period, months", 3, "From model start"),
        (31, "Cost per lead", 5, "Validate from local campaigns"),
        (32, "Organic leads per month", 10, "Referrals, walk-ins and existing audience"),
        (33, "Lead → demo booking", 0.45, "Stage conversion"),
        (34, "Demo booking → attendance", 0.70, "Show rate"),
        (35, "Demo attendance → paid", 0.35, "Close rate"),
        (36, "Direct/referral students per month", 1, "Additional non-funnel sales before seasonality"),
        (37, "Default annual re-enrollment", 0.65, "Applied in September; product can override"),
    ]
    for r, label, value, note in funnel:
        ws.cell(r, 1, label); label_cell(ws.cell(r, 1))
        ws.cell(r, 2, value); input_cell(ws.cell(r, 2))
        ws.cell(r, 3, note); label_cell(ws.cell(r, 3))
    for r in (33, 34, 35, 37): ws.cell(r, 2).number_format = "0.0%"
    for r in (28, 29, 31): ws.cell(r, 2).number_format = '€#,##0.00'

    section(ws, 39, "Seasonality by calendar month", 14)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, m in enumerate(months, 2):
        ws.cell(40, i, m)
    header_row(ws, 40, 1, 13)
    ws.cell(40, 1, "Factor")
    season_rows = [
        (41, "New-sales factor", [1.0, 1.0, 1.05, 1.0, 0.9, 0.7, 0.0, 0.2, 1.6, 1.3, 1.0, 0.7]),
        (42, "Billing / teaching factor", [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1]),
        (43, "Marketing budget factor", [1, 1, 1, 1, 0.9, 0.7, 0.4, 0.8, 1.5, 1.2, 1, 0.8]),
    ]
    for r, label, vals in season_rows:
        ws.cell(r, 1, label); label_cell(ws.cell(r, 1))
        for c, value in enumerate(vals, 2):
            ws.cell(r, c, value); input_cell(ws.cell(r, c), "0.00x")

    section(ws, 45, "Other fixed monthly costs", 3)
    ws.append([])
    ws.cell(46, 1, "Cost item"); ws.cell(46, 2, "Monthly amount"); ws.cell(46, 3, "Comment")
    header_row(ws, 46, 1, 3)
    start_fixed = 47
    for idx, (name, amount, note) in enumerate(FIXED_COSTS, start_fixed):
        ws.cell(idx, 1, name); label_cell(ws.cell(idx, 1))
        ws.cell(idx, 2, amount); input_cell(ws.cell(idx, 2), '€#,##0.00')
        ws.cell(idx, 3, note); label_cell(ws.cell(idx, 3))
    fixed_end = start_fixed + len(FIXED_COSTS) - 1
    ws.cell(fixed_end + 1, 1, "Total other fixed costs").font = Font(bold=True)
    ws.cell(fixed_end + 1, 2, f"=SUM(B{start_fixed}:B{fixed_end})")
    formula_cell(ws.cell(fixed_end + 1, 2), '€#,##0.00')

    section(ws, fixed_end + 3, "Scenario multipliers used by the model", 3)
    mult_names = ["Price", "New-student demand", "CPL", "Churn", "Fixed costs", "Salary / teacher cost"]
    scenario_rows = {}
    for i, name in enumerate(mult_names, fixed_end + 4):
        scenario_rows[name] = i
        ws.cell(i, 1, name + " multiplier"); label_cell(ws.cell(i, 1))
        column = 2 + mult_names.index(name)
        ws.cell(i, 2, f'=INDEX(\'05_SCENARIOS\'!${chr(66+mult_names.index(name))}$5:${chr(66+mult_names.index(name))}$7,MATCH($B$4,\'05_SCENARIOS\'!$A$5:$A$7,0))')
        formula_cell(ws.cell(i, 2), "0.00x")
        ws.cell(i, 3, "Calculated from selected scenario"); label_cell(ws.cell(i, 3))

    return {
        "fixed_start": start_fixed,
        "fixed_end": fixed_end,
        "fixed_total": fixed_end + 1,
        "mult_start": fixed_end + 4,
        "price_mult": scenario_rows["Price"],
        "demand_mult": scenario_rows["New-student demand"],
        "cpl_mult": scenario_rows["CPL"],
        "churn_mult": scenario_rows["Churn"],
        "fixed_mult": scenario_rows["Fixed costs"],
        "salary_mult": scenario_rows["Salary / teacher cost"],
    }


def build_products(wb: Workbook) -> Dict[str, int]:
    ws = wb.create_sheet("02_PRODUCTS")
    style_title(ws, "02 — Products and group economics", 18)
    setup_sheet(ws, "A5")
    headers = ["Enabled", "Product", "Gross monthly price", "VAT applies", "Net price today", "Lessons / month",
               "Reference Year 1 groups", "Target group", "Max group", "Reference target capacity", "Reference max capacity",
               "Teacher cost / class", "Materials revenue / new student", "Materials cost / new student",
               "Lead share", "Monthly churn", "Annual retention", "Course months", "Comment"]
    for c, h in enumerate(headers, 1): ws.cell(4, c, h)
    header_row(ws, 4, 1, len(headers))
    widths = [10, 24, 18, 12, 17, 14, 14, 13, 12, 15, 14, 18, 20, 18, 12, 14, 15, 13, 46]
    for c, width in enumerate(widths, 1): ws.column_dimensions[ws.cell(4, c).column_letter].width = width
    start = 5
    for r, p in enumerate(PRODUCTS, start):
        values = [p.enabled, p.name, p.gross_price, p.vat_applicable, None, p.lessons_month, p.groups, p.target_group,
                  p.max_group, None, None, p.teacher_cost_class, p.materials_revenue, p.materials_cost,
                  p.lead_share, p.churn, p.retention, p.course_months, p.note]
        for c, value in enumerate(values, 1):
            ws.cell(r, c, value)
            if c in (5, 10, 11): formula_cell(ws.cell(r, c))
            else: input_cell(ws.cell(r, c))
            ws.cell(r, c).alignment = Alignment(vertical="top", wrap_text=True)
        ws.cell(r, 5, f'=IF(D{r}=1,C{r}/(1+\'01_INPUTS\'!$B$9),C{r})')
        ws.cell(r, 10, f"=A{r}*G{r}*H{r}")
        ws.cell(r, 11, f"=A{r}*G{r}*I{r}")
        for c in (3, 5, 12, 13, 14): ws.cell(r, c).number_format = '€#,##0.00'
        for c in (15, 16, 17): ws.cell(r, c).number_format = "0.0%"
    end = start + len(PRODUCTS) - 1
    total_row = end + 2
    ws.cell(total_row, 2, "Enabled-product totals").font = Font(bold=True, color=NAVY)
    ws.cell(total_row, 10, f"=SUM(J{start}:J{end})"); formula_cell(ws.cell(total_row, 10), "#,##0")
    ws.cell(total_row, 11, f"=SUM(K{start}:K{end})"); formula_cell(ws.cell(total_row, 11), "#,##0")
    ws.cell(total_row, 15, f"=SUM(O{start}:O{end})"); formula_cell(ws.cell(total_row, 15), "0.0%")
    ws.conditional_formatting.add(f"O{total_row}", CellIsRule(operator="notEqual", formula=["1"], fill=PatternFill("solid", fgColor=LIGHT_RED)))
    return {"start": start, "end": end, "total": total_row}


def build_group_plan(wb: Workbook, products: Dict[str, int], demo: bool = False) -> Dict[str, int]:
    ws = wb.create_sheet("02A_GROUP_PLAN")
    style_title(ws, "02A — Group expansion plan", 8)
    setup_sheet(ws, "A5")
    headers = ["Product", "Months 1–6", "Months 7–12", "Months 13–24", "Months 25–60", "Expected opening students", "Year 1 target students", "Comment"]
    for c, h in enumerate(headers, 1):
        ws.cell(4, c, h)
    header_row(ws, 4, 1, len(headers))
    for c, width in enumerate([25, 15, 15, 15, 15, 24, 22, 58], 1):
        ws.column_dimensions[get_column_letter(c)].width = width
    if demo:
        plans = [
            (2, 2, 3, 4, 9, 18, "Mental Arithmetic: two groups at launch"),
            (3, 3, 4, 5, 12, 24, "English: three groups at launch"),
            (1, 2, 2, 2, 3, 6, "Memorica: one opening cohort; two concurrent groups from month 7"),
            (0, 0, 0, 0, 0, 0, "Enable the product first on 02_PRODUCTS"),
            (0, 0, 0, 0, 0, 0, "Enable the product first on 02_PRODUCTS"),
            (0, 0, 0, 0, 0, 0, "Enable the product first on 02_PRODUCTS"),
        ]
    else:
        plans = [
            (2, 2, 3, 4, 0, 0, "Group expansion follows operating demand and available teachers"),
            (2, 2, 3, 4, 0, 0, "Group expansion follows operating demand and available teachers"),
            (0, 0, 0, 0, 0, 0, "Enable the product first on 02_PRODUCTS"),
            (0, 0, 0, 0, 0, 0, "Enable the product first on 02_PRODUCTS"),
            (0, 0, 0, 0, 0, 0, "Enable the product first on 02_PRODUCTS"),
            (0, 0, 0, 0, 0, 0, "Enable the product first on 02_PRODUCTS"),
        ]
    start = 5
    for idx, product_row in enumerate(range(products["start"], products["end"] + 1)):
        r = start + idx
        ws.cell(r, 1, f"='02_PRODUCTS'!B{product_row}"); formula_cell(ws.cell(r, 1))
        for c, value in enumerate(plans[idx][:4], 2):
            ws.cell(r, c, value); input_cell(ws.cell(r, c), "0")
        ws.cell(r, 6, plans[idx][4]); input_cell(ws.cell(r, 6), "0")
        ws.cell(r, 7, plans[idx][5]); input_cell(ws.cell(r, 7), "0")
        ws.cell(r, 8, plans[idx][6]); input_cell(ws.cell(r, 8))
        ws.cell(r, 8).alignment = Alignment(wrap_text=True, vertical="top")
    end = start + len(plans) - 1
    total = end + 2
    ws.cell(total, 1, "Total groups by year").font = Font(bold=True, color=NAVY)
    for c in range(2, 6):
        ws.cell(total, c, f"=SUM({get_column_letter(c)}{start}:{get_column_letter(c)}{end})")
        formula_cell(ws.cell(total, c), "0")
    ws.cell(total, 6, f"=SUM(F{start}:F{end})")
    formula_cell(ws.cell(total, 6), "0")
    ws.cell(total, 7, f"=SUM(G{start}:G{end})")
    formula_cell(ws.cell(total, 7), "0")
    ws.cell(total + 2, 1, "How it works").font = Font(bold=True, color=NAVY)
    ws.cell(total + 2, 2, "The monthly model uses the group count for the current model year. New students cannot exceed target capacity: groups × target students per group. Churn and non-renewal free places for new intake.")
    ws.merge_cells(start_row=total + 2, start_column=2, end_row=total + 3, end_column=8)
    ws.cell(total + 2, 2).alignment = Alignment(wrap_text=True, vertical="top")
    return {"start": start, "end": end, "total": total}


def build_staff(wb: Workbook) -> Dict[str, int]:
    ws = wb.create_sheet("03_STAFF")
    style_title(ws, "03 — Fixed staff", 8)
    setup_sheet(ws, "A5")
    headers = ["Role", "FTE", "Gross / contractor monthly rate", "Employer load", "Monthly employer cost", "Start month", "Comment"]
    for c, h in enumerate(headers, 1): ws.cell(4, c, h)
    header_row(ws, 4, 1, len(headers))
    widths = [27, 10, 24, 15, 22, 13, 48]
    for c, width in enumerate(widths, 1): ws.column_dimensions[ws.cell(4, c).column_letter].width = width
    start = 5
    for r, role in enumerate(STAFF, start):
        vals = [role.role, role.fte, role.gross_salary, role.employer_load, None, role.start_month, role.note]
        for c, value in enumerate(vals, 1):
            ws.cell(r, c, value)
            (formula_cell if c == 5 else input_cell)(ws.cell(r, c))
            ws.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(r, 5, f"=B{r}*C{r}*(1+D{r})")
        ws.cell(r, 3).number_format = ws.cell(r, 5).number_format = '€#,##0.00'
        ws.cell(r, 4).number_format = "0.0%"
    end = start + len(STAFF) - 1
    total = end + 2
    ws.cell(total, 1, "Total monthly staff at current structure").font = Font(bold=True)
    ws.cell(total, 5, f"=SUM(E{start}:E{end})"); formula_cell(ws.cell(total, 5), '€#,##0.00')
    return {"start": start, "end": end, "total": total}


def build_capex(wb: Workbook) -> Dict[str, int]:
    ws = wb.create_sheet("04_CAPEX")
    style_title(ws, "04 — Opening investment", 7)
    setup_sheet(ws, "A5")
    headers = ["Item", "Cash amount", "Depreciable", "Life, months", "Cash month", "Monthly depreciation", "Comment"]
    for c, h in enumerate(headers, 1): ws.cell(4, c, h)
    header_row(ws, 4, 1, 7)
    widths = [34, 17, 14, 14, 12, 20, 50]
    for c, width in enumerate(widths, 1): ws.column_dimensions[ws.cell(4, c).column_letter].width = width
    start = 5
    for r, item in enumerate(CAPEX, start):
        name, amount, dep, life, month, note = item
        vals = [name, amount, dep, life, month, None, note]
        for c, value in enumerate(vals, 1):
            ws.cell(r, c, value)
            (formula_cell if c == 6 else input_cell)(ws.cell(r, c))
            ws.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(r, 6, f"=IF(C{r}=1,B{r}/D{r},0)")
        ws.cell(r, 2).number_format = ws.cell(r, 6).number_format = '€#,##0.00'
    end = start + len(CAPEX) - 1
    total = end + 2
    ws.cell(total, 1, "Total opening cash investment").font = Font(bold=True)
    ws.cell(total, 2, f"=SUM(B{start}:B{end})"); formula_cell(ws.cell(total, 2), '€#,##0.00')
    ws.cell(total + 1, 1, "Monthly depreciation after all assets are active").font = Font(bold=True)
    ws.cell(total + 1, 6, f"=SUM(F{start}:F{end})"); formula_cell(ws.cell(total + 1, 6), '€#,##0.00')
    return {"start": start, "end": end, "total": total}


def build_scenarios(wb: Workbook) -> None:
    ws = wb.create_sheet("05_SCENARIOS")
    style_title(ws, "05 — Scenario assumptions", 8)
    setup_sheet(ws, "A5")
    headers = ["Scenario", "Price", "New-student demand", "CPL", "Churn", "Fixed costs", "Salary / teacher cost", "Interpretation"]
    for c, h in enumerate(headers, 1): ws.cell(4, c, h)
    header_row(ws, 4, 1, 8)
    rows = [
        ("Base", 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, "Reference operating case"),
        ("Conservative", 0.95, 0.75, 1.40, 1.30, 1.10, 1.10, "Lower demand and price, more expensive acquisition and delivery"),
        ("Optimistic", 1.05, 1.20, 0.85, 0.80, 0.95, 1.00, "Stronger demand and retention with efficient local operation"),
    ]
    for r, values in enumerate(rows, 5):
        for c, value in enumerate(values, 1):
            ws.cell(r, c, value); input_cell(ws.cell(r, c))
            if 2 <= c <= 7: ws.cell(r, c).number_format = "0.00x"
    for c, width in enumerate([18, 12, 20, 12, 12, 15, 20, 66], 1):
        ws.column_dimensions[ws.cell(4, c).column_letter].width = width


def build_model(wb: Workbook, horizon: int, meta: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    ws = wb.create_sheet("06_MODEL")
    style_title(ws, "06 — Monthly operating model", horizon + 1)
    setup_sheet(ws, "B4")
    ws.column_dimensions["A"].width = 38
    for c in range(2, horizon + 2):
        ws.column_dimensions[get_column_letter(c)].width = 13

    rows: Dict[str, int] = {}
    labels = [
        (2, "Month number", "month_no"), (3, "Month", "date"), (4, "Model year", "year"),
        (5, "Calendar month", "cal_month"), (6, "Billing factor", "billing_factor"),
        (7, "New-sales factor", "sales_factor"), (8, "Marketing factor", "marketing_factor"),
        (9, "Cost inflation factor", "cost_infl"), (10, "Price inflation factor", "price_infl"),
        (11, "Salary inflation factor", "salary_infl"), (12, "Paid-media spend", "marketing_spend"),
        (13, "Paid leads", "paid_leads"), (14, "Organic leads", "organic_leads"),
        (15, "Total leads", "total_leads"),
    ]
    for r, label, key in labels:
        rows[key] = r; ws.cell(r, 1, label); label_cell(ws.cell(r, 1))
    header_row(ws, 2, 1, horizon + 1)
    ws.cell(2, 1, "Metric")

    mult = meta["inputs"]
    product_meta = meta["products"]
    staff_meta = meta["staff"]
    capex_meta = meta["capex"]

    product_blocks: List[Dict[str, int]] = []
    current_row = 18
    for idx, product_row in enumerate(range(product_meta["start"], product_meta["end"] + 1), 1):
        section(ws, current_row, f"Product {idx}", horizon + 1)
        ws.cell(current_row, 1, f'="Product {idx}: "&\'02_PRODUCTS\'!B{product_row}')
        block = {"product_row": product_row, "section": current_row}
        block_labels = [
            ("Beginning enrolled students", "begin"),
            ("Annual non-renewals", "annual_nonrenewal"),
            ("Course completion / non-continuation", "course_noncontinuation"),
            ("Monthly churn", "monthly_churn"),
            ("Retained students", "retained"),
            ("Allocated leads", "allocated_leads"), ("Demo bookings", "bookings"),
            ("Demo attendance", "attendance"), ("New-student demand", "demand"),
            ("New paid students", "new_students"), ("Ending enrolled students", "ending"),
            ("Billed students", "billed"), ("Groups taught", "groups"),
            ("Classes delivered", "classes"), ("Gross customer revenue", "gross_revenue"),
            ("Net tuition revenue", "net_revenue"), ("Materials revenue", "materials_revenue"),
            ("Teacher cost", "teacher_cost"), ("Materials cost", "materials_cost"),
        ]
        for offset, (label, key) in enumerate(block_labels, 1):
            rr = current_row + offset
            block[key] = rr
            ws.cell(rr, 1, label); label_cell(ws.cell(rr, 1))
        product_blocks.append(block)
        current_row += len(block_labels) + 3

    section(ws, current_row, "Consolidated center P&L and cash flow", horizon + 1)
    summary_labels = [
        ("Total ending enrolled students", "total_students"), ("Total billed students", "total_billed"),
        ("New paid students", "total_new"), ("Student outflow: churn + non-renewal", "total_outflow"),
        ("Total leads", "summary_leads"),
        ("Gross customer revenue", "gross_revenue"), ("Net tuition revenue", "net_tuition"),
        ("Materials revenue", "materials_revenue"), ("Total net revenue", "net_revenue"),
        ("Teacher cost", "teacher_cost"), ("Materials cost", "materials_cost"),
        ("Paid-media spend", "paid_media"), ("Fixed staff cost", "staff_cost"),
        ("Other fixed costs", "fixed_costs"), ("Royalty", "royalty"),
        ("Central marketing fund", "marketing_fund"), ("Payment fees", "payment_fees"),
        ("EBITDA", "ebitda"), ("Depreciation", "depreciation"), ("EBIT", "ebit"),
        ("Corporate income tax", "income_tax"), ("Net income", "net_income"),
        ("Operating cash flow", "operating_cf"), ("Opening investment cash outflow", "capex_outflow"),
        ("Net project cash flow", "net_cf"), ("Cumulative project cash flow", "cumulative_cf"),
        ("Capacity utilization", "capacity_utilization"), ("EBITDA margin", "ebitda_margin"),
        ("CAC per new student", "cac"),
    ]
    for offset, (label, key) in enumerate(summary_labels, 1):
        rr = current_row + offset; rows[key] = rr
        ws.cell(rr, 1, label); label_cell(ws.cell(rr, 1))

    for c in range(2, horizon + 2):
        letter = ws.cell(2, c).column_letter
        prev_letter = ws.cell(2, c - 1).column_letter if c > 2 else None
        ws.cell(rows["month_no"], c, c - 1)
        ws.cell(rows["date"], c, "='01_INPUTS'!$B$6" if c == 2 else f"=EDATE({prev_letter}{rows['date']},1)")
        ws.cell(rows["year"], c, f"=ROUNDUP({letter}{rows['month_no']}/12,0)")
        ws.cell(rows["cal_month"], c, f'=TEXT({letter}{rows["date"]},"mmm")')
        ws.cell(rows["billing_factor"], c, f"=INDEX('01_INPUTS'!$B$42:$M$42,1,MONTH({letter}{rows['date']}))")
        ws.cell(rows["sales_factor"], c, f"=INDEX('01_INPUTS'!$B$41:$M$41,1,MONTH({letter}{rows['date']}))")
        ws.cell(rows["marketing_factor"], c, f"=INDEX('01_INPUTS'!$B$43:$M$43,1,MONTH({letter}{rows['date']}))")
        ws.cell(rows["cost_infl"], c, f"=(1+'01_INPUTS'!$B$14)^(({letter}{rows['month_no']}-1)/12)")
        ws.cell(rows["price_infl"], c, f"=(1+'01_INPUTS'!$B$13)^(({letter}{rows['month_no']}-1)/12)")
        ws.cell(rows["salary_infl"], c, f"=(1+'01_INPUTS'!$B$15)^(({letter}{rows['month_no']}-1)/12)")
        ws.cell(rows["marketing_spend"], c, f"=IF({letter}{rows['month_no']}<='01_INPUTS'!$B$30,'01_INPUTS'!$B$29,'01_INPUTS'!$B$28)*{letter}{rows['marketing_factor']}*{letter}{rows['cost_infl']}")
        ws.cell(rows["paid_leads"], c, f"={letter}{rows['marketing_spend']}/('01_INPUTS'!$B$31*'01_INPUTS'!$B${mult['cpl_mult']})")
        ws.cell(rows["organic_leads"], c, f"='01_INPUTS'!$B$32*{letter}{rows['sales_factor']}")
        ws.cell(rows["total_leads"], c, f"={letter}{rows['paid_leads']}+{letter}{rows['organic_leads']}")

        for block in product_blocks:
            pr = block["product_row"]
            enabled = f"'02_PRODUCTS'!$A${pr}"
            if c == 2:
                ws.cell(block["begin"], c, 0)
            else:
                ws.cell(block["begin"], c, f"={prev_letter}{block['ending']}")
            retention = f"IF('02_PRODUCTS'!$Q${pr}>0,'02_PRODUCTS'!$Q${pr},'01_INPUTS'!$B$37)"
            ws.cell(block["annual_nonrenewal"], c,
                    f"=IF(AND('02_PRODUCTS'!$R${pr}>=9,MONTH({letter}{rows['date']})=9),{letter}{block['begin']}*(1-{retention}),0)")
            ws.cell(block["course_noncontinuation"], c,
                    f"=IF(AND('02_PRODUCTS'!$R${pr}<9,{letter}{rows['month_no']}>1,MOD({letter}{rows['month_no']}-1,'02_PRODUCTS'!$R${pr})=0),{letter}{block['begin']}*(1-{retention}),0)")
            ws.cell(block["monthly_churn"], c,
                    f"=IF(OR({letter}{block['annual_nonrenewal']}>0,{letter}{block['course_noncontinuation']}>0),0,{letter}{block['begin']}*'02_PRODUCTS'!$P${pr}*'01_INPUTS'!$B${mult['churn_mult']}*{letter}{rows['billing_factor']})")
            ws.cell(block["retained"], c,
                    f"={letter}{block['begin']}-{letter}{block['annual_nonrenewal']}-{letter}{block['course_noncontinuation']}-{letter}{block['monthly_churn']}")
            ws.cell(block["allocated_leads"], c, f"={letter}{rows['total_leads']}*'02_PRODUCTS'!$O${pr}*{enabled}")
            ws.cell(block["bookings"], c, f"={letter}{block['allocated_leads']}*'01_INPUTS'!$B$33")
            ws.cell(block["attendance"], c, f"={letter}{block['bookings']}*'01_INPUTS'!$B$34")
            ws.cell(block["demand"], c,
                    f"=({letter}{block['attendance']}*'01_INPUTS'!$B$35+'01_INPUTS'!$B$36*'02_PRODUCTS'!$O${pr})*'01_INPUTS'!$B${mult['demand_mult']}*{letter}{rows['sales_factor']}")
            group_plan_row = meta["group_plan"]["start"] + (pr - product_meta["start"])
            planned_groups = (
                f"IF({letter}{rows['month_no']}<=6,'02A_GROUP_PLAN'!$B${group_plan_row},"
                f"IF({letter}{rows['month_no']}<=12,'02A_GROUP_PLAN'!$C${group_plan_row},"
                f"IF({letter}{rows['month_no']}<=24,'02A_GROUP_PLAN'!$D${group_plan_row},'02A_GROUP_PLAN'!$E${group_plan_row})))"
            )
            ws.cell(block["new_students"], c,
                    f"=IF(AND({letter}{rows['month_no']}=1,'02A_GROUP_PLAN'!$F${group_plan_row}>0),MIN('02A_GROUP_PLAN'!$F${group_plan_row},{enabled}*{planned_groups}*'02_PRODUCTS'!$H${pr}),MIN({letter}{block['demand']},MAX(0,{enabled}*{planned_groups}*'02_PRODUCTS'!$H${pr}-{letter}{block['retained']})))")
            ws.cell(block["ending"], c, f"={letter}{block['retained']}+{letter}{block['new_students']}")
            ws.cell(block["billed"], c, f"={letter}{block['ending']}*{letter}{rows['billing_factor']}")
            ws.cell(block["groups"], c,
                    f"=IF({letter}{block['billed']}>0,MIN({planned_groups},ROUNDUP({letter}{block['billed']}/'02_PRODUCTS'!$H${pr},0)),0)")
            ws.cell(block["classes"], c, f"={letter}{block['groups']}*'02_PRODUCTS'!$F${pr}*{letter}{rows['billing_factor']}")
            ws.cell(block["gross_revenue"], c,
                    f"={letter}{block['billed']}*'02_PRODUCTS'!$C${pr}*{letter}{rows['price_infl']}*'01_INPUTS'!$B${mult['price_mult']}")
            ws.cell(block["net_revenue"], c,
                    f"={letter}{block['gross_revenue']}/(1+'01_INPUTS'!$B$9*'02_PRODUCTS'!$D${pr})")
            ws.cell(block["materials_revenue"], c,
                    f"={letter}{block['new_students']}*'02_PRODUCTS'!$M${pr}*{letter}{rows['price_infl']}")
            ws.cell(block["teacher_cost"], c,
                    f"={letter}{block['classes']}*'02_PRODUCTS'!$L${pr}*{letter}{rows['salary_infl']}*'01_INPUTS'!$B${mult['salary_mult']}")
            ws.cell(block["materials_cost"], c,
                    f"={letter}{block['new_students']}*'02_PRODUCTS'!$N${pr}*{letter}{rows['cost_infl']}")

        def sum_blocks(key: str) -> str:
            return "+".join(f"{letter}{b[key]}" for b in product_blocks)

        ws.cell(rows["total_students"], c, f"={sum_blocks('ending')}")
        ws.cell(rows["total_billed"], c, f"={sum_blocks('billed')}")
        ws.cell(rows["total_new"], c, f"={sum_blocks('new_students')}")
        ws.cell(rows["total_outflow"], c, f"={sum_blocks('annual_nonrenewal')}+{sum_blocks('course_noncontinuation')}+{sum_blocks('monthly_churn')}")
        ws.cell(rows["summary_leads"], c, f"={letter}{rows['total_leads']}")
        ws.cell(rows["gross_revenue"], c, f"={sum_blocks('gross_revenue')}")
        ws.cell(rows["net_tuition"], c, f"={sum_blocks('net_revenue')}")
        ws.cell(rows["materials_revenue"], c, f"={sum_blocks('materials_revenue')}")
        ws.cell(rows["net_revenue"], c, f"={letter}{rows['net_tuition']}+{letter}{rows['materials_revenue']}")
        ws.cell(rows["teacher_cost"], c, f"={sum_blocks('teacher_cost')}")
        ws.cell(rows["materials_cost"], c, f"={sum_blocks('materials_cost')}")
        ws.cell(rows["paid_media"], c, f"={letter}{rows['marketing_spend']}")
        ws.cell(rows["staff_cost"], c,
                f"=SUMPRODUCT(--('03_STAFF'!$F${staff_meta['start']}:$F${staff_meta['end']}<={letter}{rows['month_no']}),'03_STAFF'!$E${staff_meta['start']}:$E${staff_meta['end']})*{letter}{rows['salary_infl']}*'01_INPUTS'!$B${mult['salary_mult']}")
        ws.cell(rows["fixed_costs"], c,
                f"='01_INPUTS'!$B${mult['fixed_total']}*{letter}{rows['cost_infl']}*'01_INPUTS'!$B${mult['fixed_mult']}")
        ws.cell(rows["royalty"], c, f"={letter}{rows['net_revenue']}*'01_INPUTS'!$B$10")
        ws.cell(rows["marketing_fund"], c, f"={letter}{rows['net_revenue']}*'01_INPUTS'!$B$11")
        ws.cell(rows["payment_fees"], c, f"={letter}{rows['gross_revenue']}*'01_INPUTS'!$B$12")
        ws.cell(rows["ebitda"], c,
                f"={letter}{rows['net_revenue']}-SUM({letter}{rows['teacher_cost']}:{letter}{rows['payment_fees']})")
        ws.cell(rows["depreciation"], c,
                f"=SUMPRODUCT(--('04_CAPEX'!$C${capex_meta['start']}:$C${capex_meta['end']}=1),--('04_CAPEX'!$E${capex_meta['start']}:$E${capex_meta['end']}<={letter}{rows['month_no']}),--(('04_CAPEX'!$E${capex_meta['start']}:$E${capex_meta['end']}+'04_CAPEX'!$D${capex_meta['start']}:$D${capex_meta['end']})>{letter}{rows['month_no']}),'04_CAPEX'!$F${capex_meta['start']}:$F${capex_meta['end']})")
        ws.cell(rows["ebit"], c, f"={letter}{rows['ebitda']}-{letter}{rows['depreciation']}")
        ws.cell(rows["income_tax"], c, f"=MAX(0,{letter}{rows['ebit']}*'01_INPUTS'!$B$8)")
        ws.cell(rows["net_income"], c, f"={letter}{rows['ebit']}-{letter}{rows['income_tax']}")
        ws.cell(rows["operating_cf"], c, f"={letter}{rows['net_income']}+{letter}{rows['depreciation']}")
        ws.cell(rows["capex_outflow"], c,
                f"=SUMIFS('04_CAPEX'!$B${capex_meta['start']}:$B${capex_meta['end']},'04_CAPEX'!$E${capex_meta['start']}:$E${capex_meta['end']},{letter}{rows['month_no']})")
        ws.cell(rows["net_cf"], c, f"={letter}{rows['operating_cf']}-{letter}{rows['capex_outflow']}")
        ws.cell(rows["cumulative_cf"], c,
                f"={letter}{rows['net_cf']}" if c == 2 else f"={prev_letter}{rows['cumulative_cf']}+{letter}{rows['net_cf']}")
        capacity_terms = []
        for block in product_blocks:
            pr = block["product_row"]
            gp_row = meta["group_plan"]["start"] + (pr - product_meta["start"])
            planned_capacity_groups = (
                f"IF({letter}{rows['month_no']}<=6,'02A_GROUP_PLAN'!$B${gp_row},"
                f"IF({letter}{rows['month_no']}<=12,'02A_GROUP_PLAN'!$C${gp_row},"
                f"IF({letter}{rows['month_no']}<=24,'02A_GROUP_PLAN'!$D${gp_row},'02A_GROUP_PLAN'!$E${gp_row})))"
            )
            capacity_terms.append(f"'02_PRODUCTS'!$A${pr}*'02_PRODUCTS'!$H${pr}*({planned_capacity_groups})")
        ws.cell(rows["capacity_utilization"], c,
                f"=IFERROR({letter}{rows['total_billed']}/({'+'.join(capacity_terms)}),0)")
        ws.cell(rows["ebitda_margin"], c, f"=IFERROR({letter}{rows['ebitda']}/{letter}{rows['net_revenue']},0)")
        ws.cell(rows["cac"], c, f"=IFERROR({letter}{rows['paid_media']}/{letter}{rows['total_new']},0)")

    for row in range(2, rows["cac"] + 1):
        for col in range(2, horizon + 2):
            formula_cell(ws.cell(row, col))
    for col in range(2, horizon + 2):
        ws.cell(rows["date"], col).number_format = "mmm-yy"
        for r in (rows["billing_factor"], rows["sales_factor"], rows["marketing_factor"], rows["cost_infl"], rows["price_infl"], rows["salary_infl"]):
            ws.cell(r, col).number_format = "0.00x"
        for r in (rows["marketing_spend"], rows["gross_revenue"], rows["net_tuition"], rows["materials_revenue"], rows["net_revenue"], rows["teacher_cost"], rows["materials_cost"], rows["paid_media"], rows["staff_cost"], rows["fixed_costs"], rows["royalty"], rows["marketing_fund"], rows["payment_fees"], rows["ebitda"], rows["depreciation"], rows["ebit"], rows["income_tax"], rows["net_income"], rows["operating_cf"], rows["capex_outflow"], rows["net_cf"], rows["cumulative_cf"], rows["cac"]):
            ws.cell(r, col).number_format = '€#,##0;[Red]-€#,##0'
        for r in (rows["capacity_utilization"], rows["ebitda_margin"]): ws.cell(r, col).number_format = "0.0%"
    for block in product_blocks:
        for col in range(2, horizon + 2):
            for key in ("gross_revenue", "net_revenue", "materials_revenue", "teacher_cost", "materials_cost"):
                ws.cell(block[key], col).number_format = '€#,##0;[Red]-€#,##0'
    ws.conditional_formatting.add(f"B{rows['cumulative_cf']}:{ws.cell(rows['cumulative_cf'], horizon+1).coordinate}",
                                  CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=LIGHT_RED)))
    return {**rows, "product_blocks": product_blocks, "last_col": horizon + 1, "last_row": rows["cac"]}


def build_annual(wb: Workbook, horizon: int, model: Dict[str, int]) -> None:
    ws = wb.create_sheet("07_ANNUAL")
    years = horizon // 12
    style_title(ws, "07 — Annual summary", years + 1)
    setup_sheet(ws, "B4")
    ws.column_dimensions["A"].width = 38
    for y in range(1, years + 1):
        ws.cell(3, y + 1, f"Year {y}")
    header_row(ws, 3, 1, years + 1); ws.cell(3, 1, "Metric")
    metrics = [
        ("Net revenue", "net_revenue", "sum"), ("Gross customer revenue", "gross_revenue", "sum"),
        ("EBITDA", "ebitda", "sum"), ("EBITDA margin", "ebitda", "margin"),
        ("Net income", "net_income", "sum"), ("Operating cash flow", "operating_cf", "sum"),
        ("Opening investment", "capex_outflow", "sum"), ("Net project cash flow", "net_cf", "sum"),
        ("Average billed students per calendar month", "total_billed", "avg"), ("End-of-year enrolled students", "total_students", "end"),
        ("New paid students", "total_new", "sum"), ("Paid leads", "summary_leads", "sum"),
        ("Student outflow", "total_outflow", "sum"),
        ("Average CAC", "cac", "weighted_cac"), ("Average capacity utilization", "capacity_utilization", "avg"),
        ("Average billed students per teaching month", "total_billed", "avg_teaching"),
    ]
    start = 4
    first_model_col = 2
    for r, (label, key, calc) in enumerate(metrics, start):
        ws.cell(r, 1, label); label_cell(ws.cell(r, 1))
        for y in range(1, years + 1):
            c = y + 1
            start_col = first_model_col + (y - 1) * 12
            end_col = start_col + 11
            left = f"'06_MODEL'!{wb['06_MODEL'].cell(model[key], start_col).coordinate}"
            right = f"'06_MODEL'!{wb['06_MODEL'].cell(model[key], end_col).coordinate}"
            if calc == "sum": formula = f"=SUM({left}:{right})"
            elif calc == "avg": formula = f"=AVERAGE({left}:{right})"
            elif calc == "end": formula = f"={right}"
            elif calc == "avg_teaching":
                billing_left = f"'06_MODEL'!{wb['06_MODEL'].cell(model['billing_factor'], start_col).coordinate}"
                billing_right = f"'06_MODEL'!{wb['06_MODEL'].cell(model['billing_factor'], end_col).coordinate}"
                formula = f'=IFERROR(SUM({left}:{right})/COUNTIF({billing_left}:{billing_right},">0"),0)'
            elif calc == "margin":
                rev_left = f"'06_MODEL'!{wb['06_MODEL'].cell(model['net_revenue'], start_col).coordinate}"
                rev_right = f"'06_MODEL'!{wb['06_MODEL'].cell(model['net_revenue'], end_col).coordinate}"
                formula = f"=IFERROR(SUM({left}:{right})/SUM({rev_left}:{rev_right}),0)"
            else:
                spend_left = f"'06_MODEL'!{wb['06_MODEL'].cell(model['paid_media'], start_col).coordinate}"
                spend_right = f"'06_MODEL'!{wb['06_MODEL'].cell(model['paid_media'], end_col).coordinate}"
                new_left = f"'06_MODEL'!{wb['06_MODEL'].cell(model['total_new'], start_col).coordinate}"
                new_right = f"'06_MODEL'!{wb['06_MODEL'].cell(model['total_new'], end_col).coordinate}"
                formula = f"=IFERROR(SUM({spend_left}:{spend_right})/SUM({new_left}:{new_right}),0)"
            ws.cell(r, c, formula); formula_cell(ws.cell(r, c))
            if key in ("net_revenue", "gross_revenue", "ebitda", "net_income", "operating_cf", "capex_outflow", "net_cf", "cac"):
                ws.cell(r, c).number_format = '€#,##0;[Red]-€#,##0'
            elif calc == "margin" or key == "capacity_utilization": ws.cell(r, c).number_format = "0.0%"
            else: ws.cell(r, c).number_format = "#,##0.0"
    ws.auto_filter.ref = f"A3:{ws.cell(start+len(metrics)-1, years+1).coordinate}"


def build_dashboard(wb: Workbook, horizon: int, model: Dict[str, int], meta: Dict[str, Dict[str, int]], demo: bool) -> None:
    ws = wb.create_sheet("08_DASHBOARD")
    style_title(ws, "ONE CENTER — ILLUSTRATIVE FINANCIAL CASE" if demo else "08 — Investment dashboard", 14)
    setup_sheet(ws, "A4")
    for col, width in {"A": 3, "B": 28, "C": 20, "D": 4, "E": 28, "F": 20, "G": 4, "H": 18, "I": 18, "J": 18, "K": 18, "L": 18, "M": 18, "N": 18}.items():
        ws.column_dimensions[col].width = width
    ws.merge_cells("B3:F3")
    ws["B3"] = "Generic medium-sized European city | 2 courses | 2 groups per course"
    ws["B3"].font = Font(bold=True, color=NAVY, size=12)

    metrics = [
        ("B5", "Opening investment", "C5", f"='04_CAPEX'!$B${meta['capex']['total']}", '€#,##0'),
        ("B7", "Year 1 net revenue", "C7", "='07_ANNUAL'!B4", '€#,##0'),
        ("B9", "Year 1 EBITDA", "C9", "='07_ANNUAL'!B6", '€#,##0'),
        ("B11", "Year 1 EBITDA margin", "C11", "='07_ANNUAL'!B7", '0.0%'),
        ("E5", "Opening planned capacity", "F5", "=SUMPRODUCT('02A_GROUP_PLAN'!B5:B10,'02_PRODUCTS'!H5:H10,'02_PRODUCTS'!A5:A10)", '#,##0'),
        ("E7", "Year 1 avg billed / calendar month", "F7", "='07_ANNUAL'!B12", '#,##0.0'),
        ("E9", "Year 2 avg billed / calendar month", "F9", "='07_ANNUAL'!C12", '#,##0.0'),
        ("E11", "Year 2 EBITDA margin", "F11", "='07_ANNUAL'!C7", '0.0%'),
        ("E13", "Year 1 avg / teaching month", "F13", "='07_ANNUAL'!B19", '#,##0.0'),
        ("E15", "Year 2 avg / teaching month", "F15", "='07_ANNUAL'!C19", '#,##0.0'),
    ]
    for label_addr, label, value_addr, formula, fmt in metrics:
        ws[label_addr] = label; ws[label_addr].font = Font(bold=True, color=NAVY)
        ws[value_addr] = formula; ws[value_addr].number_format = fmt
        ws[value_addr].font = Font(bold=True, size=15, color=GREEN)
        ws[label_addr].fill = PatternFill("solid", fgColor=LIGHT_BLUE)
        ws[value_addr].fill = PatternFill("solid", fgColor=LIGHT_GREEN)
        ws[label_addr].border = ws[value_addr].border = border

    last_col_letter = wb["06_MODEL"].cell(2, model["last_col"]).column_letter
    ws["B13"] = "Project payback, month"
    ws["C13"] = f'=IFERROR(MATCH(1,INDEX(--(\'06_MODEL\'!B{model["cumulative_cf"]}:{last_col_letter}{model["cumulative_cf"]}>=0),0),0),"Beyond model horizon")'
    ws["B15"] = "Minimum funding need incl. buffer"
    ws["C15"] = f"=ABS(MIN('06_MODEL'!B{model['cumulative_cf']}:{last_col_letter}{model['cumulative_cf']}))+'01_INPUTS'!$B$16"
    for a in ("B13", "B15"):
        ws[a].font = Font(bold=True, color=NAVY); ws[a].fill = PatternFill("solid", fgColor=LIGHT_BLUE); ws[a].border = border
    for a in ("C13", "C15"):
        ws[a].font = Font(bold=True, size=15, color=ORANGE); ws[a].fill = PatternFill("solid", fgColor=YELLOW); ws[a].border = border
    ws["C15"].number_format = '€#,##0'
    extra_capacity = [
        ("B17", "Month 7 planned capacity", "C17", "=SUMPRODUCT('02A_GROUP_PLAN'!C5:C10,'02_PRODUCTS'!H5:H10,'02_PRODUCTS'!A5:A10)"),
        ("E17", "Year 2 planned capacity", "F17", "=SUMPRODUCT('02A_GROUP_PLAN'!D5:D10,'02_PRODUCTS'!H5:H10,'02_PRODUCTS'!A5:A10)"),
    ]
    for label_addr, label, value_addr, formula in extra_capacity:
        ws[label_addr] = label; ws[value_addr] = formula
        ws[label_addr].font = Font(bold=True, color=NAVY); ws[value_addr].font = Font(bold=True, size=15, color=GREEN)
        ws[label_addr].fill = PatternFill("solid", fgColor=LIGHT_BLUE); ws[value_addr].fill = PatternFill("solid", fgColor=LIGHT_GREEN)
        ws[label_addr].border = ws[value_addr].border = border
        ws[value_addr].number_format = "#,##0"

    section(ws, 18, "Annual outlook", 6)
    for c in range(2, min(horizon // 12, 5) + 2):
        ws.cell(19, c, f"='07_ANNUAL'!{wb['07_ANNUAL'].cell(3, c).coordinate}")
        ws.cell(20, c, f"='07_ANNUAL'!{wb['07_ANNUAL'].cell(4, c).coordinate}")
        ws.cell(21, c, f"='07_ANNUAL'!{wb['07_ANNUAL'].cell(6, c).coordinate}")
        ws.cell(22, c, f"='07_ANNUAL'!{wb['07_ANNUAL'].cell(7, c).coordinate}")
        ws.cell(20, c).number_format = ws.cell(21, c).number_format = '€#,##0;[Red]-€#,##0'
        ws.cell(22, c).number_format = "0.0%"
    ws["A19"] = "Metric"; ws["A20"] = "Net revenue"; ws["A21"] = "EBITDA"; ws["A22"] = "EBITDA margin"
    header_row(ws, 19, 1, min(horizon // 12, 5) + 1)

    chart = BarChart()
    chart.type = "col"; chart.style = 10; chart.title = "Revenue and EBITDA by year"; chart.y_axis.title = "EUR"; chart.height = 7; chart.width = 13
    data = Reference(ws, min_col=2, max_col=min(horizon // 12, 5) + 1, min_row=20, max_row=21)
    cats = Reference(ws, min_col=2, max_col=min(horizon // 12, 5) + 1, min_row=19)
    chart.add_data(data, titles_from_data=False, from_rows=True); chart.set_categories(cats)
    chart.series[0].graphicalProperties.solidFill = BLUE
    chart.series[1].graphicalProperties.solidFill = GREEN
    ws.add_chart(chart, "H4")

    line = LineChart(); line.style = 13; line.title = "Students and capacity utilization"; line.height = 7; line.width = 13
    students = Reference(wb["06_MODEL"], min_col=2, max_col=model["last_col"], min_row=model["total_billed"], max_row=model["total_billed"])
    dates = Reference(wb["06_MODEL"], min_col=2, max_col=model["last_col"], min_row=model["date"], max_row=model["date"])
    line.add_data(students, titles_from_data=False, from_rows=True); line.set_categories(dates); line.y_axis.title = "Billed students"
    ws.add_chart(line, "H19")

    section(ws, 25, "Key assumptions shown to the reader", 6)
    assumptions = [
        ("Customer monthly price — Mental Arithmetic", "='02_PRODUCTS'!C5", "gross if taxable; final price if exempt"),
        ("Customer monthly price — English", "='02_PRODUCTS'!C6", "gross if taxable; final price if exempt"),
        ("VAT", "='01_INPUTS'!B9", "editable / product-level exemption possible"),
        ("Course VAT treatment in demo", '=IF(SUM(\'02_PRODUCTS\'!D5:D6)=0,"Exempt","Taxable")', "validate local authorization and legislation"),
        ("Corporate income tax", "='01_INPUTS'!B8", "on positive EBIT"),
        ("Royalty", "='01_INPUTS'!B10", "on net revenue"),
        ("Planned groups — launch", "='02A_GROUP_PLAN'!B12", "2 per course"),
        ("Planned groups — month 7", "='02A_GROUP_PLAN'!C12", "3 per course in the demo"),
        ("Planned groups — Year 2", "='02A_GROUP_PLAN'!D12", "4 per course in the demo"),
        ("Target students per group", "=AVERAGE('02_PRODUCTS'!H5:H6)", "normal target, below maximum"),
    ]
    for i, (label, formula, note) in enumerate(assumptions, 26):
        ws.cell(i, 2, label); ws.cell(i, 3, formula); ws.cell(i, 5, note)
        ws.cell(i, 2).border = ws.cell(i, 3).border = ws.cell(i, 5).border = border
        if i in (26, 27): ws.cell(i, 3).number_format = '€#,##0.00'
        if i in (28, 30, 31): ws.cell(i, 3).number_format = "0.0%"

    ws["B35"] = "Illustrative only — replace tax, VAT treatment, price, rent, payroll and funnel assumptions for each location."
    ws.merge_cells("B35:F36")
    ws["B35"].alignment = Alignment(wrap_text=True, vertical="center")
    ws["B35"].fill = PatternFill("solid", fgColor=LIGHT_RED)
    ws["B35"].font = Font(color=RED, bold=True)


def build_demo_presentation(wb: Workbook, model: Dict[str, int], meta: Dict[str, Dict[str, int]]) -> None:
    ws = wb.create_sheet("08_DASHBOARD")
    style_title(ws, "ONE CENTER — 3-YEAR FINANCIAL SNAPSHOT", 9)
    setup_sheet(ws, "B5")
    ws.sheet_view.showGridLines = False
    widths = {"A": 25, "B": 14, "C": 14, "D": 14, "E": 14, "F": 14, "G": 14, "H": 14, "I": 14}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    ws.merge_cells("A3:I3")
    ws["A3"] = "Expected opening: 24 students | 12-month target: 48 students | 3 learning products"
    ws["A3"].font = Font(color=NAVY, bold=True, size=12)
    ws["A3"].alignment = Alignment(horizontal="left")

    cards = [("B", "C", "EXPECTED OPENING"), ("D", "E", "YEAR 1"), ("F", "G", "YEAR 2"), ("H", "I", "YEAR 3")]
    for left, right, title in cards:
        ws.merge_cells(f"{left}5:{right}5")
        cell = ws[f"{left}5"]
        cell.value = title; cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.font = Font(color=WHITE, bold=True, size=12)
        cell.alignment = Alignment(horizontal="center")

    labels = ["Groups", "Students: opening / year-end", "Net revenue", "EBITDA", "EBITDA margin"]
    for r, label in enumerate(labels, 6):
        ws.cell(r, 1, label); ws.cell(r, 1).font = Font(bold=True, color=NAVY)
        ws.cell(r, 1).fill = PatternFill("solid", fgColor=LIGHT_BLUE)
        ws.cell(r, 1).border = border

    annual_cols = [None, "B", "C", "D"]
    group_cols = ["B", "C", "D", "E"]
    card_lefts = ["B", "D", "F", "H"]
    for idx, left in enumerate(card_lefts):
        right = get_column_letter(ord(left) - 64 + 1)
        values = []
        if idx == 0:
            values = ["='02A_GROUP_PLAN'!B12", "='02A_GROUP_PLAN'!F12", '="—"', '="—"', '="—"']
        else:
            ac = annual_cols[idx]
            values = [
                f"='02A_GROUP_PLAN'!{group_cols[idx]}12",
                f"='07_ANNUAL'!{ac}13",
                f"='07_ANNUAL'!{ac}4",
                f"='07_ANNUAL'!{ac}6",
                f"='07_ANNUAL'!{ac}7",
            ]
        for row, formula in enumerate(values, 6):
            ws.merge_cells(start_row=row, start_column=ord(left)-64, end_row=row, end_column=ord(left)-63)
            c = ws.cell(row, ord(left)-64, formula)
            c.fill = PatternFill("solid", fgColor=PALE_BLUE if idx else YELLOW)
            c.border = border; c.alignment = Alignment(horizontal="center")
            c.font = Font(bold=True, size=13, color=GREEN if idx else NAVY)
            if row in (8, 9): c.number_format = '€#,##0;[Red]-€#,##0'
            elif row == 10: c.number_format = "0.0%"

    last_col = wb["06_MODEL"].cell(2, model["last_col"]).column_letter
    section(ws, 13, "KEY INVESTMENT INDICATORS", 9)
    indicators = [
        ("A14:C14", "A15:C16", "OPENING INVESTMENT", f"='04_CAPEX'!B{meta['capex']['total']}", '€#,##0'),
        ("D14:F14", "D15:F16", "OPERATING BREAK-EVEN", f'=IFERROR("MONTH "&MATCH(1,INDEX(--(\'06_MODEL\'!B{model["ebitda"]}:{last_col}{model["ebitda"]}>0),0),0),"N/A")', '@'),
        ("G14:I14", "G15:I16", "INVESTMENT PAYBACK", f'=IFERROR(MATCH(1,INDEX(--(\'06_MODEL\'!B{model["cumulative_cf"]}:{last_col}{model["cumulative_cf"]}>=0),0),0)&" MONTHS","BEYOND HORIZON")', '@'),
    ]
    for label_range, value_range, label, formula, fmt in indicators:
        ws.merge_cells(label_range); ws.merge_cells(value_range)
        lc = ws[label_range.split(":")[0]]; vc = ws[value_range.split(":")[0]]
        lc.value = label; lc.font = Font(bold=True, color=NAVY); lc.alignment = Alignment(horizontal="center")
        lc.fill = PatternFill("solid", fgColor=LIGHT_BLUE); lc.border = border
        vc.value = formula; vc.font = Font(bold=True, size=17, color=GREEN); vc.alignment = Alignment(horizontal="center", vertical="center")
        vc.fill = PatternFill("solid", fgColor=LIGHT_GREEN); vc.border = border; vc.number_format = fmt

    ws.merge_cells("A18:I18")
    ws["A18"] = "Staffing included: administrator from launch, full administrator capacity from month 7, and 0.5 FTE center director from Year 2."
    ws["A18"].alignment = Alignment(horizontal="center", wrap_text=True)
    ws["A18"].font = Font(italic=True, color="44546A")
    ws.merge_cells("A20:I21")
    ws["A20"] = "Illustrative model. Results depend on actual enrollment, retention, local taxation and operating costs."
    ws["A20"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws["A20"].fill = PatternFill("solid", fgColor=LIGHT_RED)
    ws["A20"].font = Font(color=RED, bold=True)


def build_checks(wb: Workbook, meta: Dict[str, Dict[str, int]], model: Dict[str, int]) -> None:
    ws = wb.create_sheet("09_CHECKS")
    style_title(ws, "09 — Model checks", 5)
    setup_sheet(ws, "A5")
    ws.column_dimensions["A"].width = 38; ws.column_dimensions["B"].width = 18; ws.column_dimensions["C"].width = 72
    headers = ["Check", "Status", "Interpretation"]
    for c, h in enumerate(headers, 1): ws.cell(4, c, h)
    header_row(ws, 4, 1, 3)
    p = meta["products"]
    last_col = wb["06_MODEL"].cell(2, model["last_col"]).column_letter
    checks = [
        ("Enabled-product lead shares equal 100%", f'=IF(ABS(\'02_PRODUCTS\'!O{p["total"]}-1)<0.0001,"OK","CHECK")', "Otherwise some leads disappear or are double-counted."),
        ("Long-term planned capacity does not exceed target market", '=IF(SUMPRODUCT(\'02A_GROUP_PLAN\'!E5:E10,\'02_PRODUCTS\'!H5:H10,\'02_PRODUCTS\'!A5:A10)<=\'01_INPUTS\'!B25,"OK","REVIEW")', "A capacity above target market may still be valid but needs evidence."),
        ("Corporate tax is between 0% and 40%", '=IF(AND(\'01_INPUTS\'!B8>=0,\'01_INPUTS\'!B8<=0.4),"OK","CHECK")', "Tax should be a decimal percentage."),
        ("VAT is between 0% and 30%", '=IF(AND(\'01_INPUTS\'!B9>=0,\'01_INPUTS\'!B9<=0.3),"OK","CHECK")', "VAT should be a decimal percentage."),
        ("No negative ending students", f'=IF(MIN(\'06_MODEL\'!B{model["total_students"]}:{last_col}{model["total_students"]})>=0,"OK","ERROR")', "Student stock must never be negative."),
        ("Capacity utilization stays below 110%", f'=IF(MAX(\'06_MODEL\'!B{model["capacity_utilization"]}:{last_col}{model["capacity_utilization"]})<=1.1,"OK","ERROR")', "Above 100% means planned group capacity is exceeded."),
        ("Opening investment is positive", f'=IF(\'04_CAPEX\'!B{meta["capex"]["total"]}>0,"OK","CHECK")', "A zero opening investment usually signals missing setup costs."),
        ("At least one product enabled", f'=IF(SUM(\'02_PRODUCTS\'!A{p["start"]}:A{p["end"]})>0,"OK","ERROR")', "Enable at least one product."),
    ]
    for r, (name, formula, note) in enumerate(checks, 5):
        ws.cell(r, 1, name); ws.cell(r, 2, formula); ws.cell(r, 3, note)
        for c in range(1, 4): ws.cell(r, c).border = border; ws.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top")
    ws.conditional_formatting.add(f"B5:B{4+len(checks)}", CellIsRule(operator="equal", formula=['"OK"'], fill=PatternFill("solid", fgColor=LIGHT_GREEN)))


def build_workbook(path: Path, horizon: int, demo: bool) -> None:
    wb = Workbook()
    wb.remove(wb.active)
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"
    build_readme(wb, demo)
    inputs = build_inputs(wb, horizon)
    products = build_products(wb)
    if demo:
        wb["01_INPUTS"]["B4"] = "Base"
        wb["01_INPUTS"]["B29"] = 450  # launch paid-media budget
        wb["01_INPUTS"]["B31"] = 7    # CPL
        pws = wb["02_PRODUCTS"]
        mental, english, memorica = products["start"], products["start"] + 1, products["start"] + 2
        for row, values in {
            mental:   {1: 1, 3: 110, 4: 0, 7: 2, 8: 9, 9: 12, 15: 0.35, 16: 0.03, 17: 0.70, 18: 10},
            english:  {1: 1, 3: 100, 4: 0, 7: 3, 8: 8, 9: 10, 15: 0.45, 16: 0.03, 17: 0.70, 18: 10},
            memorica: {1: 1, 3: 100, 4: 0, 7: 1, 8: 6, 9: 8, 12: 25, 13: 25, 14: 12, 15: 0.20, 16: 0.03, 17: 0.70, 18: 3},
        }.items():
            for col, value in values.items():
                pws.cell(row, col, value)
    group_plan = build_group_plan(wb, products, demo=demo)
    staff = build_staff(wb)
    if demo:
        wb["03_STAFF"].cell(staff["start"] + 1, 6, 7)   # Additional administrator from month 7
        wb["03_STAFF"].cell(staff["start"] + 3, 6, 13)  # Center manager from month 13
    capex = build_capex(wb)
    build_scenarios(wb)
    meta = {"inputs": inputs, "products": products, "group_plan": group_plan, "staff": staff, "capex": capex}
    model = build_model(wb, horizon, meta)
    build_annual(wb, horizon, model)
    if demo:
        build_demo_presentation(wb, model, meta)
    else:
        build_dashboard(wb, horizon, model, meta, demo)
    build_checks(wb, meta, model)
    if demo:
        # Keep all formula support sheets available but place the presentation first.
        wb._sheets.insert(0, wb._sheets.pop(wb.sheetnames.index("08_DASHBOARD")))
        wb["08_DASHBOARD"].title = "PRESENTATION"
        wb["00_README"].sheet_state = "hidden"
        wb["03_STAFF"].sheet_state = "hidden"
        wb["04_CAPEX"].sheet_state = "hidden"
        wb["05_SCENARIOS"].sheet_state = "hidden"
        wb["09_CHECKS"].sheet_state = "hidden"
    wb.save(path)


def validate_workbook(path: Path, expected_horizon: int) -> None:
    wb = load_workbook(path, data_only=False, read_only=False)
    assert "06_MODEL" in wb.sheetnames
    assert wb["06_MODEL"].max_column == expected_horizon + 1
    assert wb["02_PRODUCTS"]["E5"].data_type == "f"
    assert wb["06_MODEL"]["B3"].data_type == "f"
    assert path.stat().st_size > 25_000


def simulate_demo(months: int = 60) -> Dict[str, float]:
    # Independent numerical mirror used only for build-time sanity checks and summary output.
    start_month = 9
    vat = 0.20; cit = 0.20; royalty = 0.10; fund = 0.02; card = 0.02
    price_infl = 0.03; cost_infl = 0.03; salary_infl = 0.05
    season_sales = [1.0, 1.0, 1.05, 1.0, 0.9, 0.7, 0.0, 0.2, 1.6, 1.3, 1.0, 0.7]
    season_bill = [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
    season_mkt = [1, 1, 1, 1, 0.9, 0.7, 0.4, 0.8, 1.5, 1.2, 1, 0.8]
    products = PRODUCTS[:2]
    group_plans = [[2, 3, 4, 4, 4], [2, 3, 4, 4, 4]]
    enrolled = [0.0, 0.0]
    annual = {y: {"rev": 0.0, "ebitda": 0.0, "net": 0.0, "students": 0.0} for y in range(1, months // 12 + 1)}
    cumulative = 0.0; minimum = 0.0; payback = 0
    fixed_base = sum(x[1] for x in FIXED_COSTS)
    capex_total = sum(x[1] for x in CAPEX)
    depreciation = sum(x[1] / x[3] for x in CAPEX if x[2])
    for m in range(1, months + 1):
        cal_month = ((start_month - 1 + m - 1) % 12) + 1
        year = (m - 1) // 12 + 1
        ci = (1 + cost_infl) ** ((m - 1) / 12)
        pi = (1 + price_infl) ** ((m - 1) / 12)
        si = (1 + salary_infl) ** ((m - 1) / 12)
        marketing = (600 if m <= 3 else 300) * season_mkt[cal_month - 1] * ci
        leads = marketing / 5 + 10 * season_sales[cal_month - 1]
        gross = net_tuition = mat_rev = teacher = mat_cost = billed_total = 0.0
        for i, p in enumerate(products):
            planned_groups = group_plans[i][min(year, 5) - 1]
            retained = enrolled[i] * (p.retention if cal_month == 9 else 1 - p.churn * season_bill[cal_month - 1])
            demand = (leads * p.lead_share * .45 * .70 * .35 + 1 * p.lead_share) * season_sales[cal_month - 1]
            new = min(demand, max(0, planned_groups * p.target_group - retained))
            enrolled[i] = retained + new
            billed = enrolled[i] * season_bill[cal_month - 1]
            groups = min(planned_groups, 0 if billed <= 0 else int((billed + p.target_group - 1) // p.target_group))
            gr = billed * p.gross_price * pi
            gross += gr; net_tuition += gr / (1 + vat * p.vat_applicable); mat_rev += new * p.materials_revenue * pi
            teacher += groups * p.lessons_month * season_bill[cal_month - 1] * p.teacher_cost_class * si
            mat_cost += new * p.materials_cost * ci; billed_total += billed
        revenue = net_tuition + mat_rev
        staff_base = sum(r.fte * r.gross_salary * (1 + r.employer_load) for r in STAFF if r.start_month <= m)
        staff = staff_base * si; fixed = fixed_base * ci
        ebitda = revenue - teacher - mat_cost - marketing - staff - fixed - revenue * royalty - revenue * fund - gross * card
        ebit = ebitda - depreciation
        tax = max(0, ebit * cit); net = ebit - tax
        ocf = net + depreciation
        capex = capex_total if m == 1 else 0
        cumulative += ocf - capex; minimum = min(minimum, cumulative)
        if not payback and cumulative >= 0 and m > 1: payback = m
        annual[year]["rev"] += revenue; annual[year]["ebitda"] += ebitda; annual[year]["net"] += net; annual[year]["students"] += billed_total
    return {
        "capex": capex_total,
        "year1_revenue": annual[1]["rev"],
        "year1_ebitda": annual[1]["ebitda"],
        "year1_margin": annual[1]["ebitda"] / annual[1]["rev"],
        "year2_revenue": annual[2]["rev"],
        "year2_ebitda": annual[2]["ebitda"],
        "year2_margin": annual[2]["ebitda"] / annual[2]["rev"],
        "year3_revenue": annual[3]["rev"],
        "year3_ebitda": annual[3]["ebitda"],
        "year3_margin": annual[3]["ebitda"] / annual[3]["rev"],
        "year1_avg_students": annual[1]["students"] / 12,
        "year2_avg_students": annual[2]["students"] / 12,
        "year3_avg_students": annual[3]["students"] / 12,
        "minimum_funding_before_buffer": abs(minimum),
        "payback_month": payback,
    }


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_workbook(INTERNAL_PATH, 60, demo=False)
    build_workbook(DEMO_PATH, 36, demo=True)
    validate_workbook(INTERNAL_PATH, 60)
    validate_workbook(DEMO_PATH, 36)
    print(f"Created: {INTERNAL_PATH}")
    print(f"Created: {DEMO_PATH}")
    print("Both workbooks passed structural validation.")
