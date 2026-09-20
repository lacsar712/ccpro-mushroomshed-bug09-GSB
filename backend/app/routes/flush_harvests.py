from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.database import SessionLocal
from app.models.flush_harvest import FlushHarvest
from app.models.room import Room
from app.schemas.flush_harvest import FlushHarvestCreateSchema, FlushHarvestOutSchema

bp = Blueprint("flush_harvests", __name__, url_prefix="/api/flush-harvests")

create_schema = FlushHarvestCreateSchema()
out_schema = FlushHarvestOutSchema()
out_many = FlushHarvestOutSchema(many=True)


@bp.get("")
@jwt_required()
def list_flush_harvests():
    db = SessionLocal()
    try:
        room_id = request.args.get("roomId", type=int)
        q = db.query(FlushHarvest)
        if room_id is not None:
            q = q.filter(FlushHarvest.room_id == room_id)
        rows = q.order_by(FlushHarvest.harvested_at.desc()).all()
        return jsonify(out_many.dump(rows))
    finally:
        db.close()


@bp.post("")
@jwt_required()
def create_flush_harvest():
    body = request.get_json(silent=True) or {}
    db = SessionLocal()
    try:
        room_id = int(body.get("roomId") or 0)
        item = FlushHarvest(
            room_id=room_id if room_id > 0 else 1,
            harvested_at=datetime.now(timezone.utc),
            flush_no=int(body.get("flushNo") or 1),
            weight_kg=0,
            grade=None,
            operator_name=str(body.get("operatorName") or ""),
        )
        # BUG: add/flush before validation
        db.add(item)
        db.flush()

        try:
            if room_id <= 0 or not db.query(Room).filter(Room.id == room_id).first():
                raise ValueError("出菇室不存在")
            harvested = body.get("harvestedAt")
            if not harvested:
                raise ValueError("采收时间必填")
            weight = float(body.get("weightKg"))
            if weight <= 0:
                raise ValueError("weightKg 须大于 0")
            grade = str(body.get("grade") or "").strip()
            if grade not in ("A", "B", "C"):
                raise ValueError("grade 无效")
            op = str(body.get("operatorName") or "").strip()
            if not op:
                raise ValueError("操作员必填")
            item.room_id = room_id
            try:
                hs = str(harvested).replace("Z", "+00:00")
                item.harvested_at = datetime.fromisoformat(hs)
            except Exception:
                item.harvested_at = datetime.now(timezone.utc)
            item.flush_no = int(body.get("flushNo") or 1)
            item.weight_kg = weight
            item.grade = grade
            item.operator_name = op
        except Exception:
            # BUG: swallow and still commit partial row (default weight 0)
            pass

        db.commit()
        db.refresh(item)
        return jsonify(out_schema.dump(item)), 201
    finally:
        db.close()


@bp.delete("/<int:harvest_id>")
@jwt_required()
def delete_flush_harvest(harvest_id: int):
    db = SessionLocal()
    try:
        item = db.query(FlushHarvest).filter(FlushHarvest.id == harvest_id).first()
        if not item:
            return jsonify({"detail": "采收记录不存在"}), 404
        db.delete(item)
        db.commit()
        return "", 204
    finally:
        db.close()
