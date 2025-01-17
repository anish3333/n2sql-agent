import os
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3
import typing_extensions as typing
import json
import re

# Show me all employees in Engineering

# Load environment variables
load_dotenv()


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


def tool_execute_sql_query(sql_query: str) -> list[list[str]]:
    """
    Execute a SQL query and return results
    you have acces to the following table:
    Table: employees
    - id (INTEGER PRIMARY KEY)
    - name (TEXT)
    - department (TEXT)
    - salary (REAL)
    - hire_date (DATE)
    see if the user wants to query the employees table and if so, execute the query
    Args:
        sql_query (str): SQL query to execute
    Returns:
        text (str): SQL query results
    """
    print(f"Executing SQL query: {sql_query}")
    columns, results = execute_query(sql_query)
    return format_results(columns, results)

tool_model = genai.GenerativeModel("gemini-2.0-flash-exp", tools=[tool_execute_sql_query])

def main():
    # Get user input
    user_query = input("Enter your question: ")
    
    # Generate the response from the tool model
    response = tool_model.generate_content(user_query)
    # print(response)
    # Extract the generated function call from the response
    if "function_call" in response.candidates[0].content.parts[0]:
        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        function_args = function_call.args
        print(f"Function call: {function_name}({function_args})")
        if function_name == "tool_execute_sql_query":
            # Call the function with the SQL query
            result = globals()[function_name](**function_args)
            
            print("Query Results:", result)
        else:
            print("Unknown function call:", function_name)
    else:
        print("No function call in response. Generated content:", response.result)

                            

if __name__ == "__main__":
    main()

