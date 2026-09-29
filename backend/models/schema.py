from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from database import Base
import enum


class SourceTag(enum.Enum):
    REAL_OFFICIAL = "REAL_OFFICIAL"
    REAL_PUBLIC = "REAL_PUBLIC"
    PROXY = "PROXY"
    SYNTHETIC = "SYNTHETIC"


class Mine(Base):
    __tablename__ = "mines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    location = Column(Geometry('POINT', srid=4326, spatial_index=False))
    boundary = Column(Geometry('POLYGON', srid=4326, spatial_index=False))
    state = Column(String(100))
    district = Column(String(100))
    operational_status = Column(String(50))
    capacity_tonnes_per_year = Column(Float)
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.REAL_PUBLIC)
    created_at = Column(DateTime, server_default='now()')
    updated_at = Column(DateTime, server_default='now()')


class Drillhole(Base):
    __tablename__ = "drillholes"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    hole_id = Column(String(100), nullable=False)
    location = Column(Geometry('POINT', srid=4326, spatial_index=False))
    total_depth_m = Column(Float)
    drill_date = Column(Date)
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="drillholes")


class AssayInterval(Base):
    __tablename__ = "assay_intervals"

    id = Column(Integer, primary_key=True, index=True)
    drillhole_id = Column(Integer, ForeignKey("drillholes.id"), nullable=False)
    from_depth_m = Column(Float, nullable=False)
    to_depth_m = Column(Float, nullable=False)
    mn_percent = Column(Float)
    fe_percent = Column(Float)
    sio2_percent = Column(Float)
    al2o3_percent = Column(Float)
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    drillhole = relationship("Drillhole", backref="assay_intervals")


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    ore_extracted_tonnes = Column(Float)
    mn_content_tonnes = Column(Float)
    grade_percent = Column(Float)
    target_tonnes = Column(Float)
    shortfall_tonnes = Column(Float)
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="production_records")


class EquipmentEvent(Base):
    __tablename__ = "equipment_events"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    equipment_id = Column(String(100), nullable=False)
    event_type = Column(String(50))  # breakdown, maintenance, etc.
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    downtime_hours = Column(Float)
    cause = Column(String(255))
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="equipment_events")


class BlastRecord(Base):
    __tablename__ = "blast_records"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    actual_date = Column(DateTime)
    delay_hours = Column(Float)
    delay_reason = Column(String(255))
    explosives_kg = Column(Float)
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="blast_records")


class EnvObservation(Base):
    __tablename__ = "env_observations"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    observation_date = Column(Date, nullable=False)
    layer_type = Column(String(50), nullable=False)  # rainfall, soil_moisture, ndvi, lst
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    location = Column(Geometry('POINT', srid=4326, spatial_index=False))
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.REAL_PUBLIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="env_observations")


class ReservePrediction(Base):
    __tablename__ = "reserve_predictions"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    predicted_reserve_tonnes = Column(Float)
    confidence_level = Column(Float)
    model_version = Column(String(50))
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="reserve_predictions")


class ShortfallPrediction(Base):
    __tablename__ = "shortfall_predictions"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    target_date = Column(Date, nullable=False)
    predicted_shortfall_tonnes = Column(Float)
    probability = Column(Float)
    contributing_factors = Column(Text)  # JSON string
    model_version = Column(String(50))
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="shortfall_predictions")


class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, nullable=False)
    prediction_type = Column(String(50), nullable=False)  # reserve or shortfall
    feature_name = Column(String(100), nullable=False)
    feature_value = Column(Float)
    importance_score = Column(Float)
    direction = Column(String(10))  # positive or negative
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"))
    recommendation_type = Column(String(50), nullable=False)  # exploration, production, maintenance
    priority = Column(String(20))  # high, medium, low
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action_items = Column(Text)  # JSON string
    expected_impact = Column(Text)
    generated_at = Column(DateTime, server_default='now()')
    status = Column(String(50), default='pending')  # pending, in_progress, completed, dismissed
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    mine = relationship("Mine", backref="recommendations")


class ActionLog(Base):
    __tablename__ = "actions_log"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"))
    action_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    performed_by = Column(String(100))
    performed_at = Column(DateTime, server_default='now()')
    outcome = Column(String(50))
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
    created_at = Column(DateTime, server_default='now()')

    recommendation = relationship("Recommendation", backref="actions")


class DataQuality(Base):
    __tablename__ = "data_quality"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer)
    check_type = Column(String(50), nullable=False)  # schema, range, crs, completeness
    check_description = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False)  # passed, failed, quarantined
    error_message = Column(Text)
    checked_at = Column(DateTime, server_default='now()')
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.SYNTHETIC)
