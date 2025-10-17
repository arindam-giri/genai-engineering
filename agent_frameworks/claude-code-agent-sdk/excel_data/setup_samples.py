
import pandas as pd
import os

folder = "./excel_data"

# Sample 1: Sales Data
sales_data = {
    'Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
    'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Laptop'],
    'Quantity': [2, 15, 8, 3, 1],
    'Price': [1200, 25, 75, 300, 1200],
    'Total': [2400, 375, 600, 900, 1200]
}
df_sales = pd.DataFrame(sales_data)
df_sales.to_excel(os.path.join(folder, 'sales_2025.xlsx'), index=False)

# Sample 2: Employee Data
employee_data = {
    'Employee_ID': [101, 102, 103, 104, 105],
    'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Charlie Brown'],
    'Department': ['Sales', 'IT', 'Sales', 'HR', 'IT'],
    'Salary': [60000, 75000, 55000, 65000, 80000],
    'Years_Experience': [3, 5, 2, 4, 7]
}
df_employees = pd.DataFrame(employee_data)
df_employees.to_excel(os.path.join(folder, 'employees.xlsx'), index=False)

# Sample 3: Inventory Data
inventory_data = {
    'SKU': ['LP001', 'MS001', 'KB001', 'MN001', 'HD001'],
    'Item': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Hard Drive'],
    'Stock': [45, 150, 89, 34, 120],
    'Reorder_Level': [20, 50, 30, 15, 40],
    'Supplier': ['TechCorp', 'AccessoriesInc', 'AccessoriesInc', 'DisplayTech', 'StoragePro']
}
df_inventory = pd.DataFrame(inventory_data)
df_inventory.to_excel(os.path.join(folder, 'inventory.xlsx'), index=False)

print("Sample Excel files created successfully!")
