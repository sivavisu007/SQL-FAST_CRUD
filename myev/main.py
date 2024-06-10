from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Connect to MySQL database
mysql_connection = mysql.connector.connect(
    user="root",
    password="admin",
    database="sqldb"
)
mysql_cursor = mysql_connection.cursor()

# Pydantic model for the data
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

# Model to interact with MySQL
class MySQLModel:
    @classmethod
    def get_items(cls):
        mysql_cursor.execute("SELECT * FROM items")
        return mysql_cursor.fetchall()

    @classmethod
    def get_item(cls, item_id: int):
        mysql_cursor.execute("SELECT * FROM items WHERE id=%s", (item_id,))
        return mysql_cursor.fetchone()

    @classmethod
    def create_item(cls, item: Item):
        query = "INSERT INTO items (name, description, price, tax) VALUES (%s, %s, %s, %s)"
        mysql_cursor.execute(query, (item.name, item.description, item.price, item.tax))
        mysql_connection.commit()
        return {"id": mysql_cursor.lastrowid, **item.dict()}

    @classmethod
    def update_item(cls, item_id: int, item: Item):
        query = "UPDATE items SET name=%s, description=%s, price=%s, tax=%s WHERE id=%s"
        mysql_cursor.execute(query, (item.name, item.description, item.price, item.tax, item_id))
        mysql_connection.commit()
        if mysql_cursor.rowcount == 0:
            return None
        return {"id": item_id, **item.dict()}

    @classmethod
    def delete_item(cls, item_id: int):
        query = "DELETE FROM items WHERE id=%s"
        mysql_cursor.execute(query, (item_id,))
        mysql_connection.commit()
        if mysql_cursor.rowcount == 0:
            return None
        return {"id": item_id}

# Routes
@app.get("/items/")
def read_items():
    return MySQLModel.get_items()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = MySQLModel.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items/")
def create_item(item: Item):
    return MySQLModel.create_item(item)

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    updated_item = MySQLModel.update_item(item_id, item)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    deleted_item = MySQLModel.delete_item(item_id)
    if deleted_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted_item
