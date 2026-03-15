# Hybrid ETA Algorithm

**Author:** Pfarelo Channel Mudau  
**Created:** 2026-03-15  
**Purpose:** Travel time prediction combining distance-based and ML-based approaches

---

## Overview

The Hybrid ETA Algorithm predicts travel time between two locations by combining:

1. **Distance-based estimation** (Haversine formula + average speed)
2. **Machine Learning prediction** (trained on historical travel data)

The algorithm intelligently selects the best method based on available data.

---

## Why Hybrid?

**Problem:**
- Pure distance-based: Ignores traffic, time of day, personal driving patterns
- Pure ML: Requires training data (fails for new locations)

**Solution:**
- Start with distance-based (always works)
- Gradually incorporate ML as data accumulates
- Maintain confidence scores to decide which method to trust

---

## Algorithm Flow
 
 displayed in [ETA Algorithm Flow](diagrams/eta-algorithm-flow.drawio.png)

---

## Method 1: Distance-Based Estimation

### Formula

**Step 1: Calculate distance using Haversine formula**

a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2) c = 2 × atan2(√a, √(1−a)) distance = R × c

Where:

R = Earth's radius (6371 km)
Δlat = lat2 - lat1 (in radians)
Δlon = lon2 - lon1 (in radians)


**Step 2: Estimate time**

time = distance / average_speed


### Average Speed Selection

Speed depends on distance (proxy for road type):

- **< 5 km:** Urban (30 km/h) - Stop signs, traffic lights
- **5-20 km:** Suburban (50 km/h) - Secondary roads
- **20-50 km:** Rural (70 km/h) - Main roads
- **> 50 km:** Highway (90 km/h) - Open roads

### Python Implementation

```python
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates.
    
    Args:
        lat1: Latitude of point 1 (degrees)
        lon1: Longitude of point 1 (degrees)
        lat2: Latitude of point 2 (degrees)
        lon2: Longitude of point 2 (degrees)
        
    Returns:
        float: Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return distance


def estimate_average_speed(distance_km):
    """
    Estimate average speed based on distance.
    
    Args:
        distance_km: Distance in kilometers
        
    Returns:
        float: Average speed in km/h
    """
    if distance_km < 5:
        return 30  # Urban
    elif distance_km < 20:
        return 50  # Suburban
    elif distance_km < 50:
        return 70  # Rural
    else:
        return 90  # Highway


def distance_based_eta(lat1, lon1, lat2, lon2):
    """
    Predict travel time using distance-based method.
    
    Args:
        lat1, lon1: Origin coordinates
        lat2, lon2: Destination coordinates
        
    Returns:
        dict: {
            'duration_minutes': int,
            'distance_km': float,
            'avg_speed_kmh': float,
            'confidence': float
        }
    """
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    avg_speed = estimate_average_speed(distance)
    
    # Time = Distance / Speed (convert hours to minutes)
    duration_hours = distance / avg_speed
    duration_minutes = int(duration_hours * 60)
    
    # Confidence: Lower for first-time routes
    confidence = 0.60  # 60% confidence (no historical data)
    
    return {
        'duration_minutes': duration_minutes,
        'distance_km': round(distance, 2),
        'avg_speed_kmh': avg_speed,
        'confidence': confidence
    }

Method 2: Machine Learning Prediction
Approach
Train a Random Forest Regressor on historical travel data.

Features (Input)
What information helps predict travel time?

distance_km: Physical distance
day_of_week: 0 (Monday) to 6 (Sunday)
hour_of_day: 0-23
is_rush_hour: Boolean (07:00-09:00 or 16:00-18:00)
historical_avg_duration: Average of past trips on this route
historical_std_duration: Standard deviation (variability)
trips_count: How many times traveled this route
Target (Output)
duration_minutes: Actual travel time

Training Process
Step 1: Collect data from travel_history table

SELECT 
    distance_km,
    day_of_week,
    hour_of_day,
    CASE 
        WHEN hour_of_day BETWEEN 7 AND 9 THEN TRUE
        WHEN hour_of_day BETWEEN 16 AND 18 THEN TRUE
        ELSE FALSE
    END as is_rush_hour,
    duration_minutes
FROM travel_history
WHERE user_id = 1
  AND from_location_id = 5
  AND to_location_id = 12
ORDER BY departed_at DESC
LIMIT 100;

Step 2: Calculate historical statistics

import pandas as pd
import numpy as np

# Historical trips
trips = [85, 92, 88, 90, 95]

historical_avg = np.mean(trips)  # 90 minutes
historical_std = np.std(trips)   # 3.74 minutes
trips_count = len(trips)         # 5 trips

Step 3: Train model

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle


def train_eta_model(user_id, from_location_id, to_location_id):
    """
    Train ML model for specific route.
    
    Args:
        user_id: User ID
        from_location_id: Origin location ID
        to_location_id: Destination location ID
        
    Returns:
        RandomForestRegressor: Trained model
    """
    # Fetch historical data from database
    query = """
        SELECT 
            distance_km,
            day_of_week,
            hour_of_day,
            CASE 
                WHEN hour_of_day BETWEEN 7 AND 9 THEN 1
                WHEN hour_of_day BETWEEN 16 AND 18 THEN 1
                ELSE 0
            END as is_rush_hour,
            duration_minutes
        FROM travel_history
        WHERE user_id = %s
          AND from_location_id = %s
          AND to_location_id = %s
    """
    
    df = pd.read_sql(query, connection, params=[user_id, from_location_id, to_location_id])
    
    # Minimum 3 trips required
    if len(df) < 3:
        return None
    
    # Calculate historical statistics
    historical_avg = df['duration_minutes'].mean()
    historical_std = df['duration_minutes'].std()
    trips_count = len(df)
    
    # Add statistical features
    df['historical_avg_duration'] = historical_avg
    df['historical_std_duration'] = historical_std
    df['trips_count'] = trips_count
    
    # Features and target
    X = df[['distance_km', 'day_of_week', 'hour_of_day', 'is_rush_hour', 
            'historical_avg_duration', 'historical_std_duration', 'trips_count']]
    y = df['duration_minutes']
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X, y)
    
    # Calculate accuracy (Mean Absolute Error)
    predictions = model.predict(X)
    mae = np.mean(np.abs(predictions - y))
    
    # Save model to database
    model_data = pickle.dumps(model)
    
    save_query = """
        INSERT INTO ml_prediction_models (user_id, model_type, model_data, training_samples, mae, trained_at)
        VALUES (%s, 'TRAVEL_TIME', %s, %s, %s, NOW())
    """
    execute(save_query, [user_id, model_data, len(df), mae])
    
    return model

Step 4: Make prediction

def ml_based_eta(user_id, from_location_id, to_location_id, departure_time):
    """
    Predict travel time using trained ML model.
    
    Args:
        user_id: User ID
        from_location_id: Origin location ID
        to_location_id: Destination location ID
        departure_time: datetime object
        
    Returns:
        dict: Prediction result
    """
    # Load trained model from database
    query = """
        SELECT model_data, mae, training_samples
        FROM ml_prediction_models
        WHERE user_id = %s
          AND model_type = 'TRAVEL_TIME'
          AND is_active = TRUE
        ORDER BY trained_at DESC
        LIMIT 1
    """
    
    result = fetch_one(query, [user_id])
    
    if not result:
        return None  # No trained model
    
    model = pickle.loads(result['model_data'])
    mae = result['mae']
    training_samples = result['training_samples']
    
    # Prepare features
    distance = haversine_distance(from_loc.lat, from_loc.lon, to_loc.lat, to_loc.lon)
    day_of_week = departure_time.weekday()
    hour_of_day = departure_time.hour
    is_rush_hour = 1 if (7 <= hour_of_day <= 9 or 16 <= hour_of_day <= 18) else 0
    
    # Historical statistics
    historical_avg = get_avg_duration(user_id, from_location_id, to_location_id)
    historical_std = get_std_duration(user_id, from_location_id, to_location_id)
    trips_count = get_trips_count(user_id, from_location_id, to_location_id)
    
    # Create feature vector
    features = np.array([[distance, day_of_week, hour_of_day, is_rush_hour, 
                          historical_avg, historical_std, trips_count]])
    
    # Predict
    predicted_duration = model.predict(features)[0]
    
    # Confidence based on training samples and MAE
    if training_samples >= 10:
        confidence = 0.95
    elif training_samples >= 5:
        confidence = 0.85
    else:
        confidence = 0.75
    
    # Reduce confidence if MAE is high
    if mae > 10:
        confidence *= 0.9
    
    return {
        'duration_minutes': int(predicted_duration),
        'confidence': confidence,
        'method': 'ML',
        'training_samples': training_samples,
        'mae': mae
    }

Hybrid Decision Logic
Confidence-Weighted Combination

def hybrid_eta(user_id, from_location_id, to_location_id, departure_time):
    """
    Combine distance-based and ML-based predictions.
    
    Args:
        user_id: User ID
        from_location_id: Origin location ID
        to_location_id: Destination location ID
        departure_time: datetime object
        
    Returns:
        dict: Final prediction
    """
    # Get locations
    from_loc = get_location(from_location_id)
    to_loc = get_location(to_location_id)
    
    # Method 1: Distance-based
    distance_result = distance_based_eta(
        from_loc.latitude, from_loc.longitude,
        to_loc.latitude, to_loc.longitude
    )
    
    # Method 2: ML-based
    ml_result = ml_based_eta(user_id, from_location_id, to_location_id, departure_time)
    
    # Decision logic
    if ml_result is None:
        # No ML model trained yet - use distance-based only
        return {
            **distance_result,
            'method': 'Distance-Based',
            'reason': 'No historical data'
        }
    
    # Weighted combination
    trips_count = get_trips_count(user_id, from_location_id, to_location_id)
    
    if trips_count < 3:
        # Few trips: Favor distance-based
        weight_distance = 0.6
        weight_ml = 0.4
    else:
        # Many trips: Favor ML
        weight_distance = 0.2
        weight_ml = 0.8
    
    # Weighted average
    final_duration = int(
        weight_distance * distance_result['duration_minutes'] +
        weight_ml * ml_result['duration_minutes']
    )
    
    final_confidence = (
        weight_distance * distance_result['confidence'] +
        weight_ml * ml_result['confidence']
    )
    
    return {
        'duration_minutes': final_duration,
        'confidence': round(final_confidence, 2),
        'method': 'Hybrid',
        'distance_estimate': distance_result['duration_minutes'],
        'ml_estimate': ml_result['duration_minutes'],
        'weight_distance': weight_distance,
        'weight_ml': weight_ml,
        'trips_count': trips_count
    }

Real-Time Speed Tracking
During Travel
Mobile app tracks GPS every 10 seconds:

def track_live_travel(user_id, from_location_id, to_location_id):
    """
    Track live travel and update ETA dynamically.
    
    This function is called repeatedly during travel.
    """
    # Get current GPS position
    current_lat, current_lon = get_current_gps()
    
    # Calculate remaining distance
    to_loc = get_location(to_location_id)
    remaining_distance = haversine_distance(current_lat, current_lon, to_loc.latitude, to_loc.longitude)
    
    # Calculate current speed (last 10 seconds)
    current_speed = calculate_speed_from_gps_history()
    
    # Calculate time elapsed
    start_time = get_travel_start_time()
    elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
    
    # Predict remaining time
    if current_speed > 0:
        remaining_minutes = (remaining_distance / current_speed) * 60
    else:
        remaining_minutes = 0
    
    # Total ETA
    total_eta = elapsed_minutes + remaining_minutes
    
    return {
        'elapsed_minutes': int(elapsed_minutes),
        'remaining_minutes': int(remaining_minutes),
        'total_eta_minutes': int(total_eta),
        'current_speed_kmh': current_speed,
        'remaining_distance_km': round(remaining_distance, 2)
    }

Performance Tracking
Store Prediction Accuracy

def record_prediction_accuracy(user_id, from_location_id, to_location_id, predicted_duration, actual_duration):
    """
    Store prediction vs actual for model improvement.
    """
    error = actual_duration - predicted_duration
    error_percentage = (error / actual_duration) * 100
    
    query = """
        INSERT INTO prediction_history (user_id, model_id, prediction_type, predicted_value, actual_value, prediction_error)
        VALUES (%s, %s, 'TRAVEL_TIME', %s, %s, %s)
    """
    
    execute(query, [user_id, model_id, predicted_duration, actual_duration, error])
    
    # If error > 20%, retrain model
    if abs(error_percentage) > 20:
        trigger_model_retraining(user_id, from_location_id, to_location_id)

