import pandas as pd
import openpyxl
import sys
from datetime import datetime

# File to analyze
excel_file = "/Users/arindam/Documents/playground/git-repos/genai-engineering/basic_model_calls/claude/excel_data/COIN_Tool_v1_LITE_exampledata.xlsm"

print("=" * 80)
print("EXCEL FILE ANALYSIS")
print("=" * 80)
print(f"File: {excel_file}")
print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

try:
    # Load the Excel file to see all sheets
    xl_file = pd.ExcelFile(excel_file, engine='openpyxl')
    print(f"\n📊 SHEETS FOUND: {len(xl_file.sheet_names)}")
    print(f"Sheet Names: {', '.join(xl_file.sheet_names)}")
    print("\n" + "=" * 80)

    # Dictionary to store all dataframes
    all_sheets = {}

    # Analyze each sheet
    for sheet_name in xl_file.sheet_names:
        print(f"\n\n📄 SHEET: '{sheet_name}'")
        print("-" * 80)

        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
            all_sheets[sheet_name] = df

            print(f"   Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")

            if df.shape[0] > 0 and df.shape[1] > 0:
                print(f"\n   Columns ({len(df.columns)}):")
                for i, col in enumerate(df.columns, 1):
                    print(f"      {i}. {col}")

                # Show first few rows
                print(f"\n   First 5 rows preview:")
                print(df.head().to_string(max_colwidth=50))

                # Basic statistics for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    print(f"\n   Numeric columns summary:")
                    print(df[numeric_cols].describe().to_string())

                # Count non-null values
                print(f"\n   Data completeness:")
                non_null_counts = df.count()
                for col in df.columns[:10]:  # Show first 10 columns
                    null_count = df[col].isnull().sum()
                    total = len(df)
                    pct = ((total - null_count) / total * 100) if total > 0 else 0
                    print(f"      {col}: {total - null_count}/{total} ({pct:.1f}% complete)")

                if len(df.columns) > 10:
                    print(f"      ... and {len(df.columns) - 10} more columns")

            else:
                print("   ⚠️  Sheet is empty or has no data")

        except Exception as e:
            print(f"   ❌ Error reading sheet: {str(e)}")

    # Generate summary
    print("\n\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)

    total_rows = sum(df.shape[0] for df in all_sheets.values() if df is not None)
    total_cols = sum(df.shape[1] for df in all_sheets.values() if df is not None)

    print(f"✓ Total sheets analyzed: {len(all_sheets)}")
    print(f"✓ Total rows across all sheets: {total_rows}")
    print(f"✓ Total columns across all sheets: {total_cols}")

    # Identify key sheets
    if all_sheets:
        largest_sheet = max(all_sheets.items(), key=lambda x: x[1].shape[0] if x[1] is not None else 0)
        print(f"✓ Largest sheet: '{largest_sheet[0]}' with {largest_sheet[1].shape[0]} rows")

    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
