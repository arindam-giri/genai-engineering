import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_excels(user_query: str, excel_folder: str):
    """
    Analyze Excel files in a folder based on user query using Claude Agent.
    
    Args:
        user_query: The user's question about the Excel data
        excel_folder: Path to folder containing Excel files
    """
    
    # AWS Bedrock Configuration
    os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["ANTHROPIC_MODEL"] = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    os.environ["ANTHROPIC_SMALL_FAST_MODEL"] = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    os.environ["DISABLE_PROMPT_CACHING"] = "1"
    os.environ["AWS_PROFILE"] = "arindam_linux"
    
    # Verify folder exists
    if not os.path.exists(excel_folder):
        print(f"Error: Folder '{excel_folder}' does not exist!")
        return
    
    # Create analysis workspace
    workspace = os.path.join(excel_folder, ".analysis_workspace")
    os.makedirs(workspace, exist_ok=True)
    
    print("=" * 80)
    print("EXCEL ANALYZER - Interactive Query System")
    print("=" * 80)
    print(f"Analyzing folder: {os.path.abspath(excel_folder)}")
    print(f"User Query: {user_query}")
    print("=" * 80 + "\n")
    
    # Configure agent with Read, Grep, Task, and Glob tools
    options = ClaudeAgentOptions(
        system_prompt=f"""You are an expert Excel data analyst with access to multiple tools.

Your task is to analyze Excel files and answer user queries about the data.

Available tools:
- Glob: Find Excel files (*.xlsx, *.xls) in the directory
- Read: Read file contents (you'll need to convert Excel to readable format first)
- Grep: Search for specific patterns in converted files
- Task: Break down complex analysis into steps
- Bash: Execute Python scripts to read Excel files

IMPORTANT INSTRUCTIONS:
1. First, use Glob to find all Excel files in the folder
2. Create a Python script to read Excel files using pandas or openpyxl
3. Convert Excel data to CSV or text format for easier analysis
4. Use the converted data to answer the user's query
5. Provide clear, accurate answers with specific data points
6. If you need to perform calculations, write and execute Python code
7. Save your analysis results to a report file

Working directory: {excel_folder}
Analysis workspace: {workspace}

User Query: {user_query}

Start by finding all Excel files, then analyze them to answer the query.""",
        cwd=excel_folder,
        max_turns=25  # Allow multiple tool uses for complex analysis
    )
    
    # Main analysis prompt
    analysis_prompt = f"""Please analyze the Excel files in this directory and answer the following query:

"{user_query}"

Follow these steps:
1. Use Glob to find all Excel files (*.xlsx, *.xls)
2. Create a Python script that:
   - Reads all Excel files using pandas
   - Extracts relevant data
   - Performs necessary analysis
   - Answers the user's query
3. Execute the script and capture results
4. Provide a clear, detailed answer with:
   - Summary of findings
   - Specific data points and numbers
   - Any trends or patterns discovered
   - Source files for the data

Save your analysis to '{workspace}/analysis_report.txt' for reference."""
    
    print("Starting analysis...\n")
    
    async for message in query(
        prompt=analysis_prompt,
        options=options
    ):
        print(message)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    # Check if report was generated
    report_path = os.path.join(workspace, "analysis_report.txt")
    if os.path.exists(report_path):
        print(f"\nDetailed report saved to: {report_path}")
    
    print(f"\nYou can find any generated analysis files in: {workspace}")


async def interactive_mode(excel_folder: str):
    """
    Interactive mode for multiple queries on the same Excel dataset.
    """
    print("=" * 80)
    print("EXCEL ANALYZER - Interactive Mode")
    print("=" * 80)
    print(f"Analyzing Excel files in: {os.path.abspath(excel_folder)}")
    print("\nType 'exit' or 'quit' to stop")
    print("=" * 80 + "\n")
    
    while True:
        user_query = input("\nEnter your query: ").strip()
        
        if user_query.lower() in ['exit', 'quit', 'q']:
            print("\nExiting analyzer. Goodbye!")
            break
        
        if not user_query:
            print("Please enter a valid query.")
            continue
        
        print("\n" + "-" * 80)
        await analyze_excels(user_query, excel_folder)
        print("-" * 80)


async def main():
    """
    Main function with example usage scenarios.
    """
    
    # Example 1: Create sample Excel files for testing
    print("Setting up test environment...\n")
    
    test_folder = "./excel_data"
    os.makedirs(test_folder, exist_ok=True)
    
    # Create sample Excel files using pandas
    setup_script = f"""
import pandas as pd
import os

folder = "{test_folder}"

# Sample 1: Sales Data
sales_data = {{
    'Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
    'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Laptop'],
    'Quantity': [2, 15, 8, 3, 1],
    'Price': [1200, 25, 75, 300, 1200],
    'Total': [2400, 375, 600, 900, 1200]
}}
df_sales = pd.DataFrame(sales_data)
df_sales.to_excel(os.path.join(folder, 'sales_2025.xlsx'), index=False)

# Sample 2: Employee Data
employee_data = {{
    'Employee_ID': [101, 102, 103, 104, 105],
    'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Charlie Brown'],
    'Department': ['Sales', 'IT', 'Sales', 'HR', 'IT'],
    'Salary': [60000, 75000, 55000, 65000, 80000],
    'Years_Experience': [3, 5, 2, 4, 7]
}}
df_employees = pd.DataFrame(employee_data)
df_employees.to_excel(os.path.join(folder, 'employees.xlsx'), index=False)

# Sample 3: Inventory Data
inventory_data = {{
    'SKU': ['LP001', 'MS001', 'KB001', 'MN001', 'HD001'],
    'Item': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Hard Drive'],
    'Stock': [45, 150, 89, 34, 120],
    'Reorder_Level': [20, 50, 30, 15, 40],
    'Supplier': ['TechCorp', 'AccessoriesInc', 'AccessoriesInc', 'DisplayTech', 'StoragePro']
}}
df_inventory = pd.DataFrame(inventory_data)
df_inventory.to_excel(os.path.join(folder, 'inventory.xlsx'), index=False)

print("Sample Excel files created successfully!")
"""
    
    # Write and execute setup script
    with open(f"{test_folder}/setup_samples.py", "w") as f:
        f.write(setup_script)
    
    try:
        import subprocess
        result = subprocess.run(
            ["python", f"{test_folder}/setup_samples.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"Warning: {result.stderr}")
    except Exception as e:
        print(f"Note: Could not create sample files automatically: {e}")
        print("You can create your own Excel files in the folder.")
    
    print("\n" + "=" * 80)
    print("EXAMPLE QUERIES")
    print("=" * 80)
    
    # Example queries to demonstrate
    example_queries = [
        "What is the total sales revenue across all products?",
        "How many employees work in each department?",
        "Which items in inventory are below their reorder level?",
        "What is the average salary by department?",
        "List all products sold and their total quantities",
        "Show me the employee with the highest salary",
        "What is the total value of inventory (Stock * Price from sales data)?",
    ]
    
    print("\nExample queries you can ask:")
    for i, q in enumerate(example_queries, 1):
        print(f"{i}. {q}")
    
    print("\n" + "=" * 80)
    print("Choose mode:")
    print("1. Single query mode")
    print("2. Interactive mode (multiple queries)")
    print("3. Run example query")
    print("=" * 80)
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        # Single query mode
        user_query = input("\nEnter your query: ").strip()
        if user_query:
            await analyze_excels(user_query, test_folder)
        else:
            print("No query provided.")
    
    elif choice == "2":
        # Interactive mode
        await interactive_mode(test_folder)
    
    elif choice == "3":
        # Run example query
        print("\nRunning example query: 'What is the total sales revenue across all products?'")
        await analyze_excels(
            "What is the total sales revenue across all products?",
            test_folder
        )
    
    else:
        print("Invalid choice. Running example query...")
        await analyze_excels(
            "What is the total sales revenue across all products?",
            test_folder
        )
    
    print("\n" + "=" * 80)
    print(f"Excel files location: {os.path.abspath(test_folder)}")
    print(f"Analysis workspace: {os.path.abspath(test_folder)}/.analysis_workspace")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())