#!/usr/bin/env python3
"""
update_returns_data.py
Usage: python3 update_returns_data.py "path/to/new Morningstar Returns.xlsx"

Reads the Master sheet from a new Morningstar KiwiSaver Report spreadsheet,
extracts fund returns, and updates the data inside kiwisaver-fund-comparison.html.
Run this every quarter when the new Morningstar report is released.
"""

import sys, re, json
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Installing pandas..."); import subprocess; subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl", "-q"])
    import pandas as pd

HTML_FILE = Path(__file__).parent / "kiwisaver-fund-comparison.html"

def v(x):
    try:
        f = float(x)
        return None if str(x).strip() == 'nan' else f
    except:
        return None

def extract_data(xlsx_path):
    df = pd.read_excel(xlsx_path, sheet_name='Master', header=None)

    # Category averages (rows 2–6)
    cat_order = ['Conservative', 'Moderate', 'Balanced', 'Growth', 'Aggressive']
    cat_avgs = {}
    for i in range(2, 7):
        row = df.iloc[i]
        cat = str(row[0]).strip()
        if cat in cat_order:
            cat_avgs[cat] = {'yr3': v(row[7]), 'yr5': v(row[9]), 'yr10': v(row[11])}

    # Individual funds (rows 7+)
    funds = []
    for i in range(7, len(df)):
        row = df.iloc[i]
        cat  = str(row[0]).strip()
        name = str(row[1]).strip()
        if cat == 'nan' or name == 'nan' or cat not in cat_order:
            continue
        funds.append({
            'cat': cat, 'name': name,
            'yr3':  v(row[7]),  'rank3':  v(row[8]),
            'yr5':  v(row[9]),  'rank5':  v(row[10]),
            'yr10': v(row[11]), 'rank10': v(row[12]),
        })

    # Also grab row 1 (Booster Geared Growth / any special top entry)
    row1 = df.iloc[1]
    cat1 = str(row1[0]).strip()
    name1 = str(row1[1]).strip()
    if cat1 in cat_order and name1 != 'nan':
        funds.append({'cat': cat1, 'name': name1,
                      'yr3': v(row1[7]), 'rank3': None,
                      'yr5': v(row1[9]), 'rank5': None,
                      'yr10': v(row1[11]), 'rank10': None})

    return cat_avgs, funds

def format_js_data(cat_avgs, funds):
    lines = []

    # Category averages
    lines.append("const CATEGORY_AVERAGES = {")
    for cat, vals in cat_avgs.items():
        yr3  = f"{vals['yr3']}"  if vals['yr3']  is not None else 'null'
        yr5  = f"{vals['yr5']}"  if vals['yr5']  is not None else 'null'
        yr10 = f"{vals['yr10']}" if vals['yr10'] is not None else 'null'
        lines.append(f"  '{cat}': {{ yr3: {yr3}, yr5: {yr5}, yr10: {yr10} }},")
    lines.append("};")
    lines.append("")

    # Funds array
    lines.append("const FUNDS = [")
    for f in funds:
        def fv(x): return 'null' if x is None else str(x)
        name_escaped = f['name'].replace("'", "\\'")
        lines.append(
            f"  {{cat:'{f['cat']}', name:'{name_escaped}', "
            f"yr3:{fv(f['yr3'])}, rank3:{fv(f['rank3'])}, "
            f"yr5:{fv(f['yr5'])}, rank5:{fv(f['rank5'])}, "
            f"yr10:{fv(f['yr10'])}, rank10:{fv(f['rank10'])}}},"
        )
    lines.append("];")
    return "\n".join(lines)

def update_html(new_js):
    html = HTML_FILE.read_text(encoding='utf-8')

    # Replace the block between the two markers
    pattern = r'(// ── Data ─+\n)(.*?)(const CATEGORIES = )'
    replacement = r'\g<1>' + new_js + '\n\n' + r'\g<3>'

    new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)
    if n != 1:
        print("ERROR: Could not find data block in HTML. Check the markers.")
        sys.exit(1)
    HTML_FILE.write_text(new_html, encoding='utf-8')
    print(f"✓ Updated {HTML_FILE.name}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update_returns_data.py \"path/to/Morningstar Returns.xlsx\"")
        sys.exit(1)

    xlsx_path = sys.argv[1]
    print(f"Reading: {xlsx_path}")
    cat_avgs, funds = extract_data(xlsx_path)
    print(f"  Found {len(funds)} funds across {len(cat_avgs)} categories")

    new_js = format_js_data(cat_avgs, funds)
    update_html(new_js)

    # Also update the data source note in the HTML
    html = HTML_FILE.read_text(encoding='utf-8')
    # Try to extract report date from filename
    fname = Path(xlsx_path).stem
    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', fname, re.IGNORECASE)
    if date_match:
        report_date = date_match.group(0)
        html = re.sub(
            r'Morningstar KiwiSaver Report,? [A-Za-z]+ \d{4}',
            f'Morningstar KiwiSaver Report, {report_date}',
            html
        )
        HTML_FILE.write_text(html, encoding='utf-8')
        print(f"  Updated report date to: {report_date}")

    # Copy updated files to netlify-deploy folder
    deploy_dir = Path(__file__).parent / "netlify-deploy"
    deploy_dir.mkdir(exist_ok=True)
    import shutil
    shutil.copy(HTML_FILE, deploy_dir / "index.html")
    shutil.copy(Path(__file__).parent / "ssksa-logo.webp", deploy_dir / "ssksa-logo.webp")
    print(f"✓ Copied to netlify-deploy/")

    print("\nDone! Drag the netlify-deploy folder to https://morningstarreturns.netlify.app to redeploy.")
    print("  Site: https://kiwisaver-morningstar-returns-latest.solidsteeleadvice.co.nz")

if __name__ == '__main__':
    main()
