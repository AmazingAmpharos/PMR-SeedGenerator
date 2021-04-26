import json
import sqlite3

from db.item import Item


# Creates/overwrites ./debug/requirements.json by parsing the default database
def create_requirements_json():
    connection = sqlite3.connect("default_db.sqlite")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM item INNER JOIN maparea ON item.map_area_id = maparea.id WHERE maparea.name != 'Options'")
    with open("./debug/requirements.json", "w") as file:
        json_data = {}
        for data in cursor.fetchall():
            map_name = data[15]
            key_name = data[6]
            item_name = data[9]
            area_id = data[1]
            map_id = data[2]
            index = data[3]
            key = (0xA1 << 24) | (area_id << 16) | (map_id << 8) | index

            item = Item.get(Item.area_id==area_id, Item.map_id==map_id, Item.index==index)
            if map_name not in json_data:
                json_data[map_name] = {}
            json_data[map_name][item.key_name] = {
                "item": item.item_name,
                "value": item.value,
                "item_type": item.item_type,
                "area_id": item.area_id,
                "map_id": item.map_id,
                "index": item.index,
                "map_name": map_name,
                "requirements": {
                    "partners": [],
                    "items": [],
                    "boots": 0,
                    "hammer": 0,
                    "flip_panels": True if item.key_name == "HiddenPanel" else False,
                }
            }

        json.dump(json_data, file, indent=4)

# Update default_db.sqlite from requirements.json
def update_db_requirements():
    connection = sqlite3.connect("default_db.sqlite")
    cursor = connection.cursor()

    with open("requirements.json", "r") as file:
        json_data = json.load(file)
        for map_name,data in json_data.items():
            for item,item_data in data.items():
                query = f"""
                    UPDATE item
                    SET logic='{str(item_data["requirements"]).replace("'", '"')}'
                    WHERE area_id={item_data['area_id']} AND map_id={item_data['map_id']} AND `index`={item_data['index']};
                """
                result = cursor.execute(query)
            connection.commit()
