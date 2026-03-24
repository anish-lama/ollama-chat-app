from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from db_service import run_sql
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from auth import verify_password, create_access_token, SECRET_KEY, ALGORITHM, hash_password, create_refresh_token

import requests
import json
import os


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str


# login route
@app.post("/login")
def login(request: LoginRequest):
    
    result = run_sql(f"""
        SELECT username, password FROM auth_users
        WHERE username = '{request.username}'
    """)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = result[0]
    
    if not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})
    refresh_token = create_refresh_token({"sub": user["username"]})

    return {
            "access_token": token,
            "refresh_token": refresh_token
            }

# auth dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# register users
@app.post("/register")
def register(request: LoginRequest):
    hashed = hash_password(request.password)

    try:
        run_sql(f"""
            INSERT INTO auth_users (username, password)
            VALUES ('{request.username}', '{hashed}')
        """)

        return {"message": "User created"}
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
@app.post("/refresh")
def refresh_token(refresh_token: str):

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms = [ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        new_access_token = create_access_token({"sub": username})

        return {"access_token": new_access_token}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")



# protected route test
#@app.get("/protected")
#def protected(user = Depends(get_current_user)):
 #   return {"message": f"Hello {user}"}



messages = []

class ChatRequest(BaseModel):
    message: str

def call_llm(prompt: str):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/auto",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    data = response.json()

     # Handle errors safely
    if "choices" not in data:
        return f"LLM Error: {data}"

    return data["choices"][0]["message"]["content"]

@app.post("/chat")
def chat(request: ChatRequest, user: str = Depends(get_current_user)):
    
    print("Authenticated user:", user)

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