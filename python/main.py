import os
import logging
import pathlib
import hashlib
from fastapi import FastAPI, Form, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import logging
from pydantic import BaseModel
from contextlib import asynccontextmanager


# Define the path to the images & sqlite3 database
images = pathlib.Path(__file__).parent.resolve() / "images"
db = pathlib.Path(__file__).parent.resolve() / "db" / "mercari.sqlite3"


def get_db():
    if not db.exists():
        yield

    conn = sqlite3.connect(db, check_same_thread=False)  # Try to use single thread
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


# STEP 5-1: set up the database connection
def setup_database():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    with open(pathlib.Path(__file__).parent.resolve() / "db" / "items.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    yield


app = FastAPI(lifespan=lifespan)

logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class HelloResponse(BaseModel):
    message: str


@app.get("/", response_model=HelloResponse)
def hello():
    return HelloResponse(**{"message": "Hello, world!"})


json_file = "items.json"
# Declare as variable to use in multile methods
SELECT_ITEMS_QUERY = """
                    SELECT items.id, items.name, categories.name AS category, items.image_filename
                    FROM items
                    JOIN categories ON items.category_id = categories.id
                    """


@app.get("/items")
def get_items(db: sqlite3.Connection = Depends(get_db)):
    logger.info("Getting items indatabase")
    cursor = db.cursor()
    cursor.execute(SELECT_ITEMS_QUERY)
    items = cursor.fetchall()

    items_list = [{"id": id_, "name": name, "category": category, "image_filename": image_filename} for id_, name, category, image_filename in items]
    
    return {"items": items_list}
"""
# Step 4-3 - Getting data from json file
def get_items():
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("Fetching all items from items.json")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to open json file: {e}")
            return {"items": []}
    else:
        return {"items": []}
"""

# Step 5-1: 
@app.get("/items/{item_id}")
def get_chosen_id_item(item_id:int, db: sqlite3.Connection = Depends(get_db)):
    logger.info(f"Searching item with id {item_id}")
    cursor = db.cursor()

    cursor.execute(SELECT_ITEMS_QUERY)

    item = cursor.fetchone()

    if not item:
        logger.warning("No item is found in the selected id")
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_dict = dict(item)

    if not item_dict.get("image_filename"):
        item_dict["image_filename"] = "dummy.jpg"

    logger.info("Found item in the id")

    return item_dict
    
"""
# Step 4-5: Get item data from chosen index
def get_chosen_id_item(item_id:int):

    logger.info(f"Fetching item with ID: {item_id}")

    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                logger.info("Fetching all items from items.json")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to open json file: {e}")
            items = {"items": []}
    else:
        return {"items": []}
    
    if item_id <= 0 or item_id > len(items["items"]):
        logger.warning(f"Item ID out of range: {item_id}")
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = items["items"][item_id - 1]
    if "image_filename" not in item:
        item["image_filename"] = "dummy.jpg"

    return item
"""
# Step 5-2: Get items containing specified keyword in name
@app.get("/search")
def get_chosen_items(keyword: str, db: sqlite3.Connection = Depends(get_db)):
    logger.info(f"Search keyword received: {keyword}")

    cursor = db.cursor()

    try:
        cursor.execute("""
                        SELECT items.name, categories.name AS category, items.image_filename
                        FROM items
                        JOIN categories ON items.category_id = categories.id
                        WHERE items.name LIKE ?                        
                        """, (f"%{keyword}%",))
        items = cursor.fetchall()

    except sqlite3.OperationalError as e:
        # If the table 'items' does not exist
        if "no such table: items" in str(e):
            logger.error("The 'items' table does not exist.")
            raise HTTPException(status_code=500, detail="The 'items' table does not exist.")
        else:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    if not items:
        logger.warning(f"No item is found with the keyword: {keyword}")
        raise HTTPException(status_code=404, detail="Item not found")
    
    items_list = []
    for item in items:
        item_dict = dict(item)
        if not item_dict.get("image_filename"):
            item_dict["image_filename"] = "dummy.jpg"
        items_list.append(item_dict)

    logger.info(f"Found {len(items_list)} items matching keyword.")

    return {"items": items_list}



class AddItemResponse(BaseModel):
    message: str


# add_item is a handler to add a new item for POST /items .
@app.post("/items", response_model=AddItemResponse)
async def add_item(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db),
):
    logger.info(f"Adding new item: name={name}, category={category}, image_filename={image.filename}")

    # Reject if name or category is empty or whitespace  only 
    # (Accept name with numbers only since it could exist...)
    if not name.strip() or not category.strip():
        logger.warning("Empty name or category received.")
        raise HTTPException(status_code=400, detail="name and category cannot be empty")
    
    if not image.filename.endswith(".jpg"):
        logger.warning(f"Invalid image file extension: {image.filename}")
        raise HTTPException(status_code=400, detail="image name must be end with .jpg")
    
     # ハッシュ化
    image_data = await image.read()
    image_hash = hashlib.sha256(image_data).hexdigest()
    image_filename = f"{image_hash}.jpg"

    image_path = images / image_filename

    with open(image_path, "wb") as f:
        f.write(image_data)

    insert_item(Item(name=name, category=category, image_filename=image_filename), db)
    logger.info(f"Item added to database: {name} in category {category} with image {image_filename}")

    return AddItemResponse(**{"message": f"item received: {name}, Category: {category}, image_name: {image_filename}"})


# get_image is a handler to return an image for GET /images/{filename} .
@app.get("/image/{image_name}")
async def get_image(image_name):
    # Create image path
    image = images / image_name

    if not image_name.endswith(".jpg"):
        logger.warning("Invalid image file extension")
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "dummy.jpg"

    return FileResponse(image)


class Item(BaseModel):
    name: str
    category: str
    image_filename: str = None


# STEP 5-1: Insert item into database
def insert_item(item: Item, db: sqlite3.Connection):
    cursor = db.cursor()

    logger.info("Inserting items to database...")

    cursor.execute("SELECT id FROM categories WHERE name = ?", (item.category,))
    category_row = cursor.fetchone()

    if category_row is None:
        logger.info(f"Adding newe category: {category_row}")
        cursor.execute("INSERT INTO categories(name) VALUES (?);", (item.category,))
        db.commit()

        cursor.execute("SELECT id FROM categories WHERE name = ?", (item.category,))
        category_row = cursor.fetchone()

    category_id = category_row[0]

    cursor.execute("INSERT INTO items(name, category_id, image_filename) VALUES (?,?,?);", (item.name, category_id, item.image_filename))
    
    db.commit()
    cursor.close()

    logger.info("Inserting items to database --Succeeded!")
    
    """
    #  STEP 4-2: add an implementation to store an item

    # Load file if it exists and can be open, otherwise create file data (list)
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                logger.info("Fetching all items from items.json")
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to open json file: {e}")
            data = {"items": []}
    else:
        data = {"items": []}

    data["items"].append(item.dict())

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)   
    """
