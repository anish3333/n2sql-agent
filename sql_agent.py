import os
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3
import typing_extensions as typing
import json
import re

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

class SQLResponse(typing.TypedDict):
    thought: str
    sql_query: str

SCHEMA_DESCRIPTION = """
Database Schema:
Table: employees
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- department (TEXT)
- salary (REAL)
- hire_date (DATE)
"""

def execute_query(query):
    """Execute a SQL query and return results"""
    try:
        conn = sqlite3.connect('company.db')
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        conn.close()
        return columns, results
    except Exception as e:
        return None, f"Error: {str(e)}"

def format_results(columns, results):
    """Format query results as a simple table"""
    if not columns:
        return results  # Return error message if no columns
    
    # Create header
    output = []
    header = " | ".join(columns)
    separator = "-" * len(header)
    output.append(header)
    output.append(separator)
    
    # Add rows
    for row in results:
        output.append(" | ".join(str(item) for item in row))
    
    return "\n".join(output)

def get_sql_query(user_query):
    """Get structured SQL query response from Gemini"""
    prompt = f"""You are a SQL expert. Based on the following schema, convert the user's question into a SQL query.
    
{SCHEMA_DESCRIPTION}

User question: {user_query}

Use this JSON schema:


SQLResponse = {{
    "thought": str,
    "sql_query": str
}}
Return: SQLResponse """

    try:
        response = model.generate_content(prompt)
        
        # Check if the response text is empty
        if not response.text.strip():
            return "No response from model", None
          
        pattern = r'\{[^{}]*\}'
        matches = re.finditer(pattern, response.text)
        result = ""
        for match in matches:
          json_str = match.group(0)
          result = json.loads(json_str)
          
        return result.get("thought", ""), result.get("sql_query", None)
    except json.JSONDecodeError as e:
        return f"Error parsing response: {str(e)}", None
    except Exception as e:
        return f"Error generating query: {str(e)}", None

def main():
    # Get user input
    user_query = input("Enter your question: ")
    
    # Generate SQL query
    print("\nAnalyzing query...")
    thought, sql_query = get_sql_query(user_query)
    
    if not sql_query:
        print(f"Thought process: {thought}")
        print("\nFailed to generate SQL query")
        return
    
    print(f"Thought process: {thought}\n")
    print(f"SQL Query: {sql_query}\n")
    
    # Execute query and show results
    print("Results:")
    columns, results = execute_query(sql_query)
    if isinstance(results, str) and results.startswith("Error:"):
        print(results)  # Print error message
    else:
        print(format_results(columns, results))

if __name__ == "__main__":
    main()
