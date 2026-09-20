from marshmallow import Schema, fields, validate


class FlushHarvestCreateSchema(Schema):
    room_id = fields.Int(required=True, data_key="roomId")
    harvested_at = fields.DateTime(required=True, data_key="harvestedAt")
    flush_no = fields.Int(required=True, data_key="flushNo", validate=validate.Range(min=1))
    weight_kg = fields.Float(required=False, data_key="weightKg", allow_none=True)
    grade = fields.Str(required=False, allow_none=True)
    operator_name = fields.Str(required=True, data_key="operatorName", validate=validate.Length(min=1, max=64))


class FlushHarvestOutSchema(Schema):
    id = fields.Int(dump_only=True)
    room_id = fields.Int(data_key="roomId")
    harvested_at = fields.DateTime(data_key="harvestedAt")
    flush_no = fields.Int(data_key="flushNo")
    weight_kg = fields.Method("dump_weight", data_key="weightKg")
    grade = fields.Str(allow_none=True)
    operator_name = fields.Str(data_key="operatorName")

    def dump_weight(self, obj):
        v = obj.weight_kg if hasattr(obj, "weight_kg") else obj.get("weight_kg")
        raw = float(v) if v is not None else 0.0
        # BUG: dump or 0 mask
        return raw or 0
