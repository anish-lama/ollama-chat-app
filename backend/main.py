from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from db_service import run_sql
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"   
MODEL = "deepseek-llm" 

messages = []

class ChatRequest(BaseModel):
    message: str

def call_llm(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

""" Normal chat post request 
@app.post("/chat")
def chat(request: ChatRequest):

    try:
        user_message = request.message

        messages.append({
            "role": "user",
            "content": user_message
        })

        response = ollama.chat(
            model="llama3",
            messages=messages
        )

        assistant_reply = response["message"]["content"]

        messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

        return {
            "response": assistant_reply
        }
    except Exception as e:
        return {"error": str(e)}

"""
@app.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message

    schema = """
Table: users
Columns:
- id
- name
- hire_date
- department
"""

    #step 1 - Generate SQL
    sql_prompt = f"""
You are a PostgreSQL expert.

Convert the user's question into a SQL query ONLY if it is related to the database.

Rules:
- Only generate SQL if the question is about employees/users
- If the question is NOT related to the database including Hi, Hello, return EXACTLY: NONE
- Only use SELECT queries
- Use the schema provided
- [Strict] Do NOT explain anything
- Do NOT include markdown
- [Srtict] Start directly with SELECT
- Select ONLY relevant columns (do NOT always select all)
- Add WHERE, groupby, partition conditions when needed
- Use ILIKE as an operator: column_name ILIKE '%value%'
- Never use ILIKE as a function
- Example: WHERE department ILIKE '%finance%'

Schema:
{schema}

Question:
{user_message}
"""

    sql_query = call_llm(sql_prompt).strip()
    print("Generated SQL:", sql_query)

    #Safety check
    if sql_query.upper() == "NONE":
        return {"response": "Ask me about employees..."}

    if not sql_query.lower().startswith("select"):
        return {"response": "Something went wrong..."}

    # Step 2 - Execure SQL
    columns, rows = run_sql(sql_query)


    formatted_result = {
        "columns": columns,
        "rows": [
            [str(cell) for cell in row]
            for row in rows
        ]
    }

    formatted_result_json = json.dumps(formatted_result, indent=2)
    print("Return result: ", formatted_result_json)

    # Step 3 - Generate Answer

    final_prompt = f"""
You are a data assistant.

The SQL result is the ONLY source of truth.

User question:
{user_message}

SQL result: {formatted_result_json}

You must ONLY use the provided rows.

Rules:
- Never filter rows
- Never add rows
- Never remove rows
- Never infer anything
- Never re-evaluate the question
- The rows already satisfy the query
- If "rows" : [[0]] → answer MUST say 0.
- If rows has one number → use that exact number.
- If rows has multiple rows → describe them clearly.
- Answer should start with based on database.

Your job is ONLY to convert the rows into a readable answer.

If the rows list is empty respond exactly:
"No employees found in the database."
"""
    
 
    final_response = call_llm(final_prompt)

    return {"response": final_response}


#app.mount("/static", StaticFiles(directory="static"), name="static")

"""@app.get("/")
def read_index():
    return FileResponse("static/index.html")"""