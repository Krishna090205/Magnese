"""
FastAPI main application with base API endpoints
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime, timedelta
import json

from database import get_db
from models.schema import (
    Mine, DataQuality, EnvObservation, SourceTag,
    ReservePrediction, ShortfallPrediction, PredictionExplanation,
    Recommendation, ActionLog, ProductionRecord, Drillhole, AssayInterval
)

app = FastAPI(
    title="Manganese Exploration System API",
    description="API for manganese reserve identification and production shortfall prediction",
    version="1.0.0"
)


# Pydantic models for API responses
class MineResponse(BaseModel):
    id: int
    name: str
    state: Optional[str] = None
    district: Optional[str] = None
    operational_status: Optional[str] = None
    capacity_tonnes_per_year: Optional[float] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class DataQualityResponse(BaseModel):
    id: int
    table_name: str
    record_id: Optional[int] = None
    check_type: str
    check_description: str
    status: str
    error_message: Optional[str] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class EnvObservationResponse(BaseModel):
    id: int
    mine_id: int
    observation_date: date
    layer_type: str
    value: float
    unit: Optional[str] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: str


class ReservePredictionResponse(BaseModel):
    id: int
    mine_id: int
    prediction_date: datetime
    predicted_reserve_tonnes: Optional[float] = None
    confidence_level: Optional[float] = None
    model_version: Optional[str] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class ShortfallPredictionResponse(BaseModel):
    id: int
    mine_id: int
    prediction_date: datetime
    target_date: date
    predicted_shortfall_tonnes: Optional[float] = None
    probability: Optional[float] = None
    contributing_factors: Optional[str] = None
    model_version: Optional[str] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class PredictionExplanationResponse(BaseModel):
    id: int
    prediction_id: int
    prediction_type: str
    feature_name: str
    feature_value: Optional[float] = None
    importance_score: Optional[float] = None
    direction: Optional[str] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class RecommendationResponse(BaseModel):
    id: int
    mine_id: Optional[int] = None
    recommendation_type: str
    priority: Optional[str] = None
    title: str
    description: str
    action_items: Optional[str] = None
    expected_impact: Optional[str] = None
    status: Optional[str] = None
    generated_at: Optional[datetime] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class ActionLogResponse(BaseModel):
    id: int
    recommendation_id: Optional[int] = None
    action_type: str
    description: str
    performed_by: Optional[str] = None
    performed_at: Optional[datetime] = None
    outcome: Optional[str] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class DrillholeResponse(BaseModel):
    id: int
    mine_id: int
    hole_id: str
    total_depth_m: Optional[float] = None
    drill_date: Optional[date] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


class AssayIntervalResponse(BaseModel):
    id: int
    drillhole_id: int
    from_depth_m: float
    to_depth_m: float
    mn_percent: Optional[float] = None
    fe_percent: Optional[float] = None
    sio2_percent: Optional[float] = None
    al2o3_percent: Optional[float] = None
    source_tag: str
    
    class Config:
        from_attributes = True
        use_enum_values = True


@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        database=db_status,
        timestamp=str(datetime.now())
    )


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Manganese Exploration System API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "mines": "/api/mines",
            "mines_production": "/api/mines/{mine_id}/production",
            "mines_drillholes": "/api/mines/{mine_id}/drillholes",
            "drillhole_assays": "/api/drillholes/{drillhole_id}/assays",
            "data_quality": "/api/data-quality",
            "environment": "/api/environment/{layer}",
            "reserve_targets": "/api/reserve-targets",
            "gis_layers": "/api/gis-layers/{layer}",
            "shortfall_forecast": "/api/shortfall-forecast",
            "explanations": "/api/explain/{prediction_id}",
            "recommendations": "/api/recommendations",
            "actions": "/api/actions (POST)",
            "history": "/api/history",
            "recommendation_history": "/api/history/{recommendation_id}",
            "overview": "/api/overview",
            "alerts": "/api/alerts"
        },
        "documentation": "/docs"
    }


@app.get("/api/mines", response_model=List[MineResponse])
def get_mines(
    state: Optional[str] = None,
    operational_status: Optional[str] = None,
    source_tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all mines with optional filters
    
    Filters:
    - state: Filter by state (e.g., Maharashtra, Madhya Pradesh)
    - operational_status: Filter by operational status
    - source_tag: Filter by data source tag
    """
    query = db.query(Mine)
    
    if state:
        query = query.filter(Mine.state == state)
    if operational_status:
        query = query.filter(Mine.operational_status == operational_status)
    if source_tag:
        try:
            source_tag_enum = SourceTag(source_tag.upper())
            query = query.filter(Mine.source_tag == source_tag_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source_tag: {source_tag}")
    
    mines = query.all()
    return mines


@app.get("/api/mines/{mine_id}", response_model=MineResponse)
def get_mine(mine_id: int, db: Session = Depends(get_db)):
    """Get a specific mine by ID"""
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    return mine


@app.get("/api/mines/{mine_id}/production")
def get_mine_production(mine_id: int, db: Session = Depends(get_db)):
    """Get production records for a specific mine"""
    production = db.query(ProductionRecord).filter(
        ProductionRecord.mine_id == mine_id
    ).order_by(ProductionRecord.record_date.desc()).limit(365).all()
    
    return [
        {
            "id": p.id,
            "record_date": p.record_date.isoformat() if p.record_date else None,
            "ore_extracted_tonnes": p.ore_extracted_tonnes,
            "target_tonnes": p.target_tonnes,
            "shortfall_tonnes": p.shortfall_tonnes,
            "source_tag": p.source_tag.value if p.source_tag else None
        }
        for p in production
    ]


@app.get("/api/mines/{mine_id}/drillholes", response_model=List[DrillholeResponse])
def get_mine_drillholes(mine_id: int, db: Session = Depends(get_db)):
    """Get drillhole data for a specific mine"""
    drillholes = db.query(Drillhole).filter(
        Drillhole.mine_id == mine_id
    ).all()
    
    return drillholes


@app.get("/api/drillholes/{drillhole_id}/assays", response_model=List[AssayIntervalResponse])
def get_drillhole_assays(drillhole_id: int, db: Session = Depends(get_db)):
    """Get assay intervals for a specific drillhole"""
    assays = db.query(AssayInterval).filter(
        AssayInterval.drillhole_id == drillhole_id
    ).order_by(AssayInterval.from_depth_m).all()
    
    return assays


@app.get("/api/data-quality", response_model=List[DataQualityResponse])
def get_data_quality(
    table_name: Optional[str] = None,
    check_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get data quality records with optional filters
    
    Filters:
    - table_name: Filter by table name
    - check_type: Filter by check type (schema, range, crs, completeness)
    - status: Filter by status (passed, failed, quarantined)
    - limit: Maximum number of records to return
    """
    query = db.query(DataQuality)
    
    if table_name:
        query = query.filter(DataQuality.table_name == table_name)
    if check_type:
        query = query.filter(DataQuality.check_type == check_type)
    if status:
        query = query.filter(DataQuality.status == status)
    
    query = query.order_by(DataQuality.checked_at.desc()).limit(limit)
    
    quality_records = query.all()
    return quality_records


@app.get("/api/data-quality/summary")
def get_data_quality_summary(db: Session = Depends(get_db)):
    """Get summary statistics of data quality checks"""
    try:
        # Total checks by status
        status_query = text("""
            SELECT status, COUNT(*) as count
            FROM data_quality
            GROUP BY status
        """)
        status_results = db.execute(status_query).fetchall()
        
        status_summary = {row.status: row.count for row in status_results}
        
        # Total checks by table
        table_query = text("""
            SELECT table_name, COUNT(*) as count
            FROM data_quality
            GROUP BY table_name
        """)
        table_results = db.execute(table_query).fetchall()
        
        table_summary = {row.table_name: row.count for row in table_results}
        
        # Total checks by type
        type_query = text("""
            SELECT check_type, COUNT(*) as count
            FROM data_quality
            GROUP BY check_type
        """)
        type_results = db.execute(type_query).fetchall()
        
        type_summary = {row.check_type: row.count for row in type_results}
        
        return {
            "by_status": status_summary,
            "by_table": table_summary,
            "by_check_type": type_summary,
            "total_checks": sum(status_summary.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@app.get("/api/environment/{layer}", response_model=List[EnvObservationResponse])
def get_environment_data(
    layer: str,
    mine_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source_tag: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """
    Get environmental observation data for a specific layer
    
    Layers: rainfall, soil_moisture, ndvi, lst
    
    Filters:
    - mine_id: Filter by mine ID
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - source_tag: Filter by data source tag
    - limit: Maximum number of records to return
    """
    # Validate layer type
    valid_layers = ['rainfall', 'soil_moisture', 'ndvi', 'lst']
    if layer not in valid_layers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid layer. Valid layers: {', '.join(valid_layers)}"
        )
    
    query = db.query(EnvObservation).filter(EnvObservation.layer_type == layer)
    
    if mine_id:
        query = query.filter(EnvObservation.mine_id == mine_id)
    if start_date:
        try:
            start = date.fromisoformat(start_date)
            query = query.filter(EnvObservation.observation_date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    if end_date:
        try:
            end = date.fromisoformat(end_date)
            query = query.filter(EnvObservation.observation_date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    if source_tag:
        try:
            source_tag_enum = SourceTag(source_tag.upper())
            query = query.filter(EnvObservation.source_tag == source_tag_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source_tag: {source_tag}")
    
    query = query.order_by(EnvObservation.observation_date.desc()).limit(limit)
    
    observations = query.all()
    return observations


@app.get("/api/environment/{layer}/summary")
def get_environment_summary(
    layer: str,
    mine_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get summary statistics for environmental data"""
    # Validate layer type
    valid_layers = ['rainfall', 'soil_moisture', 'ndvi', 'lst']
    if layer not in valid_layers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid layer. Valid layers: {', '.join(valid_layers)}"
        )
    
    try:
        query = text("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT mine_id) as num_mines,
                MIN(observation_date) as earliest_date,
                MAX(observation_date) as latest_date,
                AVG(value) as mean_value,
                MIN(value) as min_value,
                MAX(value) as max_value
            FROM env_observations
            WHERE layer_type = :layer
        """)
        
        params = {'layer': layer}
        
        if mine_id:
            query = text(query.text + " AND mine_id = :mine_id")
            params['mine_id'] = mine_id
        if start_date:
            query = text(query.text + " AND observation_date >= :start_date")
            params['start_date'] = start_date
        if end_date:
            query = text(query.text + " AND observation_date <= :end_date")
            params['end_date'] = end_date
        
        results = db.execute(query, params).fetchall()
        
        if not results:
            return {"message": "No data found for the specified parameters"}
        
        summary = {
            "layer": layer,
            "total_records": results[0].total_records,
            "num_mines": results[0].num_mines,
            "date_range": {
                "earliest": str(results[0].earliest_date) if results[0].earliest_date else None,
                "latest": str(results[0].latest_date) if results[0].latest_date else None
            },
            "statistics": {
                "mean": float(results[0].mean_value) if results[0].mean_value else None,
                "min": float(results[0].min_value) if results[0].min_value else None,
                "max": float(results[0].max_value) if results[0].max_value else None
            }
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


# ===== Stage 2: Reserve Targeting Endpoints =====

@app.get("/api/reserve-targets", response_model=List[ReservePredictionResponse])
def get_reserve_targets(
    mine_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source_tag: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get reserve targeting predictions
    
    Filters:
    - mine_id: Filter by mine ID
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - source_tag: Filter by data source tag
    - limit: Maximum number of records to return
    """
    query = db.query(ReservePrediction)
    
    if mine_id:
        query = query.filter(ReservePrediction.mine_id == mine_id)
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(ReservePrediction.prediction_date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(ReservePrediction.prediction_date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    if source_tag:
        try:
            source_tag_enum = SourceTag(source_tag.upper())
            query = query.filter(ReservePrediction.source_tag == source_tag_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source_tag: {source_tag}")
    
    query = query.order_by(ReservePrediction.prediction_date.desc()).limit(limit)
    
    predictions = query.all()
    return predictions


@app.get("/api/gis-layers/{layer}")
def get_gis_layer(
    layer: str,
    mine_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get GIS layer data for visualization
    
    Layers: reserve_predictions, shortfall_predictions, environmental
    
    Returns GeoJSON-compatible format with source_tag provenance
    """
    valid_layers = ['reserve_predictions', 'shortfall_predictions', 'environmental']
    if layer not in valid_layers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid layer. Valid layers: {', '.join(valid_layers)}"
        )
    
    try:
        if layer == 'reserve_predictions':
            # Get reserve predictions with mine locations
            query = text("""
                SELECT 
                    rp.id,
                    rp.mine_id,
                    m.name as mine_name,
                    m.location,
                    rp.predicted_reserve_tonnes,
                    rp.confidence_level,
                    rp.model_version,
                    rp.source_tag,
                    rp.prediction_date
                FROM reserve_predictions rp
                JOIN mines m ON rp.mine_id = m.id
            """)
            
            params = {}
            if mine_id:
                query = text(query.text + " WHERE rp.mine_id = :mine_id")
                params['mine_id'] = mine_id
            
            results = db.execute(query, params).fetchall()
            
            features = []
            for row in results:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]  # Would extract from PostGIS geometry
                    },
                    "properties": {
                        "id": row.id,
                        "mine_id": row.mine_id,
                        "mine_name": row.mine_name,
                        "predicted_reserve_tonnes": row.predicted_reserve_tonnes,
                        "confidence_level": row.confidence_level,
                        "model_version": row.model_version,
                        "source_tag": row.source_tag.value if row.source_tag else None,
                        "prediction_date": row.prediction_date.isoformat() if row.prediction_date else None
                    }
                })
            
            return {
                "type": "FeatureCollection",
                "layer": layer,
                "features": features,
                "source_tag_provenance": "All records include source_tag for data provenance"
            }
        
        elif layer == 'shortfall_predictions':
            query = text("""
                SELECT 
                    sp.id,
                    sp.mine_id,
                    m.name as mine_name,
                    m.location,
                    sp.target_date,
                    sp.predicted_shortfall_tonnes,
                    sp.probability,
                    sp.model_version,
                    sp.source_tag,
                    sp.prediction_date
                FROM shortfall_predictions sp
                JOIN mines m ON sp.mine_id = m.id
            """)
            
            params = {}
            if mine_id:
                query = text(query.text + " WHERE sp.mine_id = :mine_id")
                params['mine_id'] = mine_id
            
            results = db.execute(query, params).fetchall()
            
            features = []
            for row in results:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]
                    },
                    "properties": {
                        "id": row.id,
                        "mine_id": row.mine_id,
                        "mine_name": row.mine_name,
                        "target_date": row.target_date.isoformat() if row.target_date else None,
                        "predicted_shortfall_tonnes": row.predicted_shortfall_tonnes,
                        "probability": row.probability,
                        "model_version": row.model_version,
                        "source_tag": row.source_tag.value if row.source_tag else None,
                        "prediction_date": row.prediction_date.isoformat() if row.prediction_date else None
                    }
                })
            
            return {
                "type": "FeatureCollection",
                "layer": layer,
                "features": features,
                "source_tag_provenance": "All records include source_tag for data provenance"
            }
        
        elif layer == 'environmental':
            # Get environmental observations
            query = text("""
                SELECT 
                    eo.id,
                    eo.mine_id,
                    m.name as mine_name,
                    eo.observation_date,
                    eo.layer_type,
                    eo.value,
                    eo.unit,
                    eo.location,
                    eo.source_tag
                FROM env_observations eo
                JOIN mines m ON eo.mine_id = m.id
            """)
            
            params = {}
            if mine_id:
                query = text(query.text + " WHERE eo.mine_id = :mine_id")
                params['mine_id'] = mine_id
            
            results = db.execute(query, params).fetchall()
            
            features = []
            for row in results:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]
                    },
                    "properties": {
                        "id": row.id,
                        "mine_id": row.mine_id,
                        "mine_name": row.mine_name,
                        "observation_date": row.observation_date.isoformat() if row.observation_date else None,
                        "layer_type": row.layer_type,
                        "value": row.value,
                        "unit": row.unit,
                        "source_tag": row.source_tag.value if row.source_tag else None
                    }
                })
            
            return {
                "type": "FeatureCollection",
                "layer": layer,
                "features": features,
                "source_tag_provenance": "All records include source_tag for data provenance"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting GIS layer: {str(e)}")


# ===== Stage 2: Shortfall Forecast Endpoints =====

@app.get("/api/shortfall-forecast", response_model=List[ShortfallPredictionResponse])
def get_shortfall_forecast(
    mine_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source_tag: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get shortfall forecast predictions
    
    Filters:
    - mine_id: Filter by mine ID
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - source_tag: Filter by data source tag
    - limit: Maximum number of records to return
    """
    query = db.query(ShortfallPrediction)
    
    if mine_id:
        query = query.filter(ShortfallPrediction.mine_id == mine_id)
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(ShortfallPrediction.prediction_date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(ShortfallPrediction.prediction_date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    if source_tag:
        try:
            source_tag_enum = SourceTag(source_tag.upper())
            query = query.filter(ShortfallPrediction.source_tag == source_tag_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source_tag: {source_tag}")
    
    query = query.order_by(ShortfallPrediction.prediction_date.desc()).limit(limit)
    
    predictions = query.all()
    return predictions


@app.get("/api/explain/{prediction_id}", response_model=List[PredictionExplanationResponse])
def get_prediction_explanation(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get feature contribution explanations for a prediction
    
    Args:
        prediction_id: ID of the prediction to explain
    """
    explanations = db.query(PredictionExplanation).filter(
        PredictionExplanation.prediction_id == prediction_id
    ).all()
    
    if not explanations:
        raise HTTPException(status_code=404, detail="No explanations found for this prediction")
    
    return explanations


@app.get("/api/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(
    mine_id: Optional[int] = None,
    status: Optional[str] = None,
    recommendation_type: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get recommendations with optional filters
    
    Filters:
    - mine_id: Filter by mine ID
    - status: Filter by status (pending, in_progress, completed, dismissed)
    - recommendation_type: Filter by type (maintenance, production, exploration)
    - priority: Filter by priority (high, medium, low)
    - limit: Maximum number of records to return
    """
    query = db.query(Recommendation)
    
    if mine_id:
        query = query.filter(Recommendation.mine_id == mine_id)
    if status:
        query = query.filter(Recommendation.status == status)
    if recommendation_type:
        query = query.filter(Recommendation.recommendation_type == recommendation_type)
    if priority:
        query = query.filter(Recommendation.priority == priority)
    
    query = query.order_by(Recommendation.generated_at.desc()).limit(limit)
    
    recommendations = query.all()
    return recommendations


@app.post("/api/actions")
def create_action(
    recommendation_id: int,
    action_type: str,
    description: str,
    performed_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create an action log entry for a recommendation
    
    Args:
        recommendation_id: ID of the recommendation
        action_type: Type of action (status_update, action_taken, etc.)
        description: Description of the action
        performed_by: User or system performing the action
    """
    # Verify recommendation exists
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Create action log
    action_log = ActionLog(
        recommendation_id=recommendation_id,
        action_type=action_type,
        description=description,
        performed_by=performed_by or 'system',
        outcome='pending',
        source_tag=SourceTag.SYNTHETIC
    )
    
    db.add(action_log)
    db.commit()
    db.refresh(action_log)
    
    return {
        "message": "Action logged successfully",
        "action_id": action_log.id,
        "source_tag": action_log.source_tag.value
    }


@app.get("/api/history/{recommendation_id}", response_model=List[ActionLogResponse])
def get_action_history(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get action history for a recommendation
    
    Args:
        recommendation_id: ID of the recommendation
    """
    actions = db.query(ActionLog).filter(
        ActionLog.recommendation_id == recommendation_id
    ).order_by(ActionLog.performed_at.desc()).all()
    
    return actions


@app.get("/api/history")
def get_all_history(
    mine_id: Optional[int] = None,
    action_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all action history with optional filters
    
    Filters:
    - mine_id: Filter by mine ID (via recommendations)
    - action_type: Filter by action type
    - limit: Maximum number of records to return
    """
    query = db.query(ActionLog).join(Recommendation)
    
    if mine_id:
        query = query.filter(Recommendation.mine_id == mine_id)
    if action_type:
        query = query.filter(ActionLog.action_type == action_type)
    
    query = query.order_by(ActionLog.performed_at.desc()).limit(limit)
    
    actions = query.all()
    
    return {
        "actions": [
            {
                "id": action.id,
                "recommendation_id": action.recommendation_id,
                "action_type": action.action_type,
                "description": action.description,
                "performed_by": action.performed_by,
                "performed_at": action.performed_at.isoformat() if action.performed_at else None,
                "outcome": action.outcome,
                "source_tag": action.source_tag.value if action.source_tag else None
            }
            for action in actions
        ],
        "source_tag_provenance": "All records include source_tag for data provenance"
    }


# ===== Stage 3: Overview and Aggregation Endpoints =====

@app.get("/api/overview")
def get_overview(db: Session = Depends(get_db)):
    """
    Get overview dashboard statistics
    
    Returns portfolio summary with source_tag provenance
    """
    try:
        # Count mines
        total_mines = db.query(Mine).count()
        
        # Count active shortfall alerts (predictions with probability >= 0.05)
        active_alerts = db.query(ShortfallPrediction).filter(
            ShortfallPrediction.probability >= 0.05,
            ShortfallPrediction.target_date >= datetime.now().date()
        ).count()
        
        # Count active exploration targets (reserve predictions with high confidence)
        active_targets = db.query(ReservePrediction).filter(
            ReservePrediction.confidence_level >= 0.7,
            ReservePrediction.prediction_date >= datetime.now() - timedelta(days=30)
        ).count()
        
        # Data freshness (latest prediction dates)
        latest_reserve = db.query(
            func.max(ReservePrediction.prediction_date)
        ).scalar()
        
        latest_shortfall = db.query(
            func.max(ShortfallPrediction.prediction_date)
        ).scalar()
        
        # Production summary
        total_production = db.query(
            func.sum(ProductionRecord.ore_extracted_tonnes)
        ).scalar()
        
        total_shortfall = db.query(
            func.sum(ProductionRecord.shortfall_tonnes)
        ).scalar()
        
        return {
            "mines_monitored": total_mines,
            "active_shortfall_alerts": active_alerts,
            "active_exploration_targets": active_targets,
            "data_freshness": {
                "latest_reserve_prediction": latest_reserve.isoformat() if latest_reserve else None,
                "latest_shortfall_prediction": latest_shortfall.isoformat() if latest_shortfall else None
            },
            "production_summary": {
                "total_production_tonnes": float(total_production) if total_production else 0,
                "total_shortfall_tonnes": float(total_shortfall) if total_shortfall else 0
            },
            "source_tag_provenance": "Aggregated from tables with individual source_tags"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating overview: {str(e)}")


@app.get("/api/alerts")
def get_alerts(
    alert_type: Optional[str] = None,
    mine_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get active alerts (shortfall predictions above threshold)
    
    Filters:
    - alert_type: Filter by type (shortfall, reserve)
    - mine_id: Filter by mine ID
    - limit: Maximum number of records to return
    """
    try:
        alerts = []
        
        # Shortfall alerts
        if not alert_type or alert_type == 'shortfall':
            shortfall_alerts = db.query(ShortfallPrediction).join(Mine).filter(
                ShortfallPrediction.probability >= 0.05,
                ShortfallPrediction.target_date >= datetime.now().date()
            )
            
            if mine_id:
                shortfall_alerts = shortfall_alerts.filter(ShortfallPrediction.mine_id == mine_id)
            
            shortfall_alerts = shortfall_alerts.order_by(
                ShortfallPrediction.probability.desc()
            ).limit(limit).all()
            
            for alert in shortfall_alerts:
                alerts.append({
                    "id": alert.id,
                    "type": "shortfall",
                    "mine_id": alert.mine_id,
                    "mine_name": alert.mine.name if alert.mine else "Unknown",
                    "severity": "high" if alert.probability >= 0.15 else "medium",
                    "probability": alert.probability,
                    "predicted_shortfall_tonnes": alert.predicted_shortfall_tonnes,
                    "target_date": alert.target_date.isoformat() if alert.target_date else None,
                    "source_tag": alert.source_tag.value if alert.source_tag else None
                })
        
        # Reserve alerts (high-value targets)
        if not alert_type or alert_type == 'reserve':
            reserve_alerts = db.query(ReservePrediction).join(Mine).filter(
                ReservePrediction.confidence_level >= 0.7,
                ReservePrediction.prediction_date >= datetime.now() - timedelta(days=30)
            )
            
            if mine_id:
                reserve_alerts = reserve_alerts.filter(ReservePrediction.mine_id == mine_id)
            
            reserve_alerts = reserve_alerts.order_by(
                ReservePrediction.predicted_reserve_tonnes.desc()
            ).limit(limit).all()
            
            for alert in reserve_alerts:
                alerts.append({
                    "id": alert.id,
                    "type": "reserve",
                    "mine_id": alert.mine_id,
                    "mine_name": alert.mine.name if alert.mine else "Unknown",
                    "severity": "high" if alert.confidence_level >= 0.9 else "medium",
                    "predicted_reserve_tonnes": alert.predicted_reserve_tonnes,
                    "confidence_level": alert.confidence_level,
                    "prediction_date": alert.prediction_date.isoformat() if alert.prediction_date else None,
                    "source_tag": alert.source_tag.value if alert.source_tag else None
                })
        
        # Sort by severity (high first)
        alerts.sort(key=lambda x: (x['severity'] == 'high', x.get('probability', x.get('confidence_level', 0))), reverse=True)
        
        return {
            "alerts": alerts[:limit],
            "total_count": len(alerts),
            "source_tag_provenance": "All alerts include source_tag for data provenance"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alerts: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
