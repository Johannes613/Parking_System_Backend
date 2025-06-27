from flask import request, jsonify
from config.db import mysql


# Route to list all parking slots
def get_slots():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM slots")
    slots = cur.fetchall()
    cur.close()
    slot_list = []
    for slot in slots:
        slot_dict = {
            "slotId": slot[0],
            "slotName": slot[1],
            "isOccupied": slot[2],
        }
        slot_list.append(slot_dict)

    return jsonify(slot_list)


# route to add slots to the parking system
def add_slot():
    data = request.get_json()
    slot_name = data.get("slotName")
    is_occupied = data.get("isOccupied", False)

    if not slot_name:
        return jsonify({"error": "slotName is required"}), 400

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO slots (slotName, isOccupied) VALUES (%s, %s)",
        (slot_name, is_occupied),
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Slot created successfully"}), 201


# route to update the status of parking slots
def update_slot(slot_id):
    data = request.get_json()
    is_occupied = data.get("isOccupied", False)

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE slots SET isOccupied = %s WHERE slotId = %s", (is_occupied, slot_id)
    )
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "slot updated successfully"})


# a route to delete slots from the parking system
def delete_slot(slot_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM slots WHERE slotId = %s", (slot_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "slot deleted successfully"})
