from fastapi.testclient import TestClient
from main import app, get_db
import pytest
import sqlite3
import os
import pathlib
from io import BytesIO
import io
from fastapi import UploadFile

#STEP 6-4: uncomment this test setup
test_db = pathlib.Path(__file__).parent.resolve() / "db" / "test_mercari.sqlite3"

def override_get_db():
    conn = sqlite3.connect(test_db, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def db_connection():
    # Before the test is done, create a test database
    conn = sqlite3.connect(test_db, check_same_thread=False)

    cursor = conn.cursor()
    #cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
        )
    ''')
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS items (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category_id INTEGER,
        image_filename TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(id)
	)"""
    )    

    conn.commit()
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries

    yield conn

    conn.close()
    # After the test is done, remove the test database
    if test_db.exists():
        test_db.unlink() # Remove the file

client = TestClient(app)

def get_mock_image_file():
    image_content = b"fake_image_content"
    return UploadFile(
        filename="test_image.jpg",
        file=BytesIO(image_content)
    )

@pytest.mark.parametrize(
    "want_status_code, want_body",
    [
        (200, {"message": "Hello, world!"}),
    ],
)
def test_hello(want_status_code, want_body):
    response = client.get("/") # Used to have .json() but then it won't have status_code
    assert response.status_code == want_status_code
    assert response.json() == want_body


# STEP 6-4: uncomment this test
@pytest.mark.parametrize(
    "args, want_status_code",
    [
        ({"name":"used iPhone 16e", "category":"phone"}, 200),
        ({"name":"", "category":"phone"}, 400),
    ],
)
def test_add_item_e2e(args,want_status_code,db_connection):

    dummy_image = ("dummy.jpg", io.BytesIO(b"dummyimage"), "image/jpeg") # Indicate MIME type in thee third element

    response = client.post("/items/", data=args, files={"image": dummy_image}) # Send a request
    
    assert response.status_code == want_status_code # Check if the response
    
    if want_status_code >= 400:
        return
    
    
    # Check if the response body is correct
    response_data = response.json()
    assert "message" in response_data

    # Check if the data was saved to the database correctly
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM items WHERE name = ?", (args["name"],))
    db_item = cursor.fetchone()
    assert db_item is not None
    assert dict(db_item)["name"] == args["name"]
