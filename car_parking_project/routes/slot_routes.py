from flask import Blueprint
from controllers.slot_controller import get_slots, add_slot, update_slot, delete_slot

slot_bp = Blueprint("slot_bp", __name__)

slot_bp.route("/api/slots", methods=["GET"])(get_slots)
slot_bp.route("/api/slots/add", methods=["POST"])(add_slot)
slot_bp.route("/api/slots/updateSlotStatus/<int:slot_id>", methods=["PUT"])(update_slot)
slot_bp.route("/api/slots/deleteSlots/<int:slot_id>", methods=["DELETE"])(delete_slot)