
import os
from dotenv import load_dotenv
import google.generativeai as genai
import sqlite3
from pydantic import BaseModel
from typing import List, Optional

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

class SQLResponse(BaseModel):
    thought: str
    sql_query: str

class QueryResult(BaseModel):
    columns: List[str]
    rows: List[List]

SCHEMA_DESCRIPTION = """
Database Schema:
Table: employees
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- department (TEXT)
- salary (REAL)
- hire_date (DATE)
"""

def generate_structured_response(prompt: str, model_class, llm_instance) -> Optional[BaseModel]:
    """Generate a structured response using the LLM"""
    try:
        prompt_template = f"""Based on this database schema:
{SCHEMA_DESCRIPTION}

Question: {prompt}

Respond with a JSON object containing:
- thought: Your reasoning about how to answer the query
- sql_query: The SQL query to execute

Ensure the response is valid JSON."""

        response = llm_instance.generate_content(prompt_template)
        return model_class.model_validate_json(response.text)
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return None

def execute_query(query: str) -> QueryResult:
    """Execute SQL query and return results in a structured format"""
    try:
        conn = sqlite3.connect('company.db')
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return QueryResult(columns=columns, rows=[list(row) for row in rows])
    except Exception as e:
        print(f"Database error: {str(e)}")
        return QueryResult(columns=[], rows=[])

def format_results(result: QueryResult) -> str:
    """Format query results as a table"""
    if not result.columns:
        return "No results found"
    
    # Create header
    output = []
    header = " | ".join(result.columns)
    separator = "-" * len(header)
    output.append(header)
    output.append(separator)
    
    # Add rows
    for row in result.rows:
        output.append(" | ".join(str(item) for item in row))
    
    return "\n".join(output)

def main():
    # Initialize Gemini model
    model = genai.GenerativeModel('gemini-pro')
    
    while True:
        # Get user input
        user_query = input("\nEnter your question (or 'quit' to exit): ")
        if user_query.lower() == 'quit':
            break
            
        # Generate SQL query with structured output
        print("\nAnalyzing query...")
        response = generate_structured_response(user_query, SQLResponse, model)
        
        if response:
            print(f"\nThought process: {response.thought}")
            print(f"SQL Query: {response.sql_query}\n")
            
            # Execute query and display results
            print("Results:")
            results = execute_query(response.sql_query)
            print(format_results(results))
        else:
            print("Failed to generate SQL query")

if __name__ == "__main__":
    main()