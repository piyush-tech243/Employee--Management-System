from fastapi import FastAPI
from pydantic import BaseModel,Field
from mysql.connector import connect
from dotenv import load_dotenv
import os
app = FastAPI()  # FASTAPI() = fastapi application ka ek object bnata h or app ye variable h
load_dotenv(dotenv_path=".env")
print("DB HOST:", os.getenv("DB_HOST"))
print("DB USER:", os.getenv("DB_USER"))
print("DB NAME:", os.getenv("DB_NAME"))
class Employee(BaseModel):
    name:str
    email:str
    department:str
    salary:float = Field(...,ge=0)   

db = connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)    
@app.post("/employees")
def create_employee(employee:Employee) :
    cursor=db.cursor()
    cursor.execute("INSERT into employees(name,email,department,salary)values(%s,%s,%s,%s)", (employee.name, employee.email, employee.department, employee.salary))
    db.commit()
    print("Employee created successfully")
    return{
           "message": "Employee created successfully",
           "employee": employee
    }
@app.get("/employees")     #ye ek decorator h jo ki get request ko handle krta h 
def get_employees(page: int = 1, limit: int = 10):
    cursor=db.cursor()
    cursor.execute("SELECT COUNT(*) FROM employees")  # total employee count krne ke liye jisse page gin ske
    total_employees = cursor.fetchone()[0]
    offset = (page - 1) * limit
    cursor.execute("select*from employees LIMIT %s OFFSET %s",(limit,offset))
    employees=cursor.fetchall()
    result=[]
    for employee in employees:
        result.append({
            "id":employee[0],
            "name":employee[1],
            "email":employee[2],
            "department":employee[3],
            "salary":employee[4]
        })
    return {
    "employees": result,
    "total_employees": total_employees
}

## employees ko naam ya id se search krne ke liye 

@app.get("/employees/search")
def search_employee(search: str):

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM employees
        WHERE name LIKE %s
        OR email LIKE %s
        OR id = %s
        """,
        (f"%{search}%", f"%{search}%", search)
    )

    employees = cursor.fetchall()

    result = []

    for employee in employees:
        result.append({
            "id": employee[0],
            "name": employee[1],
            "email": employee[2],
            "department": employee[3],
            "salary": employee[4]
        })

    return {"employees": result}


@app.get("/employees/{employee_id}")     #existing data ko retrieve krna 
def get_employee(employee_id: int):

    cursor = db.cursor()

    cursor.execute(
        "select * from employees where id=%s",
        (employee_id,)
    )

    employee = cursor.fetchone()

    return {
        "id": employee[0],
        "name": employee[1],
        "email": employee[2],
        "department": employee[3],
        "salary": employee[4]
    }


@app.put("/employees/{employee_id}")                      #ye update krne ke liye h existing data ko 
def update_employee(employee_id:int,employee:Employee):
    cursor=db.cursor()
    cursor.execute("update employees set name=%s,email=%s,department=%s,salary=%s where id=%s",(employee.name,employee.email,employee.department,employee.salary,employee_id))
    db.commit()
    return{
        "message": "Employee updated successfully"
    }
@app.delete("/employees/{employee_id}")           #employee ke data ko delete krne ke liye use hota h  ye decorator
def delete_employee(employee_id:int):
    cursor=db.cursor()
    cursor.execute("delete from employees where id=%s",(employee_id,))
    db.commit()
    return{
        "message": "Employee deleted successfully"
    }
@app.get("/")   # ye ek decorator h jo ki get request ko handle krta h 
def home():
    return({"message": "Employee Management API is Running"})
