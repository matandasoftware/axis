# API Specification

**Author:** Pfarelo Channel Mudau  
**Created:** 2026-03-15  
**Purpose:** REST API endpoints for AXIS backend

---

## Overview

This document specifies all API endpoints for the AXIS platform.

**Base URL:** `https://api.axis.app/v1`

**Authentication:** JWT tokens (Bearer authentication)

**Response Format:** JSON

---

## Authentication

### Register

**POST** `/auth/register`

**Request Body:**

```json
{
  "username": "pfarelo",
  "email": "pfarelo@example.com",
  "password": "SecurePassword123!",
  "first_name": "Pfarelo",
  "last_name": "Mudau"
}
```

**Response: 201 Created**

```json
{
  "user": {
    "id": 1,
    "username": "pfarelo",
    "email": "pfarelo@example.com",
    "first_name": "Pfarelo",
    "last_name": "Mudau"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Login

**POST** `/auth/login`

**Request Body:**

```json
{
  "username": "pfarelo",
  "password": "SecurePassword123!"
}
```

**Response: 200 OK**

```json
{
  "user": {
    "id": 1,
    "username": "pfarelo",
    "email": "pfarelo@example.com"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Refresh Token

**POST** `/auth/refresh`

**Request Body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response: 200 OK**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Logout

**POST** `/auth/logout`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 204 No Content**

---

## User Profile

### Get Profile

**GET** `/profile`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 200 OK**

```json
{
  "id": 1,
  "user_id": 1,
  "date_of_birth": "1995-06-15",
  "phone_number": "+27123456789",
  "profile_picture": "https://cdn.axis.app/profiles/1.jpg",
  "timezone": "Africa/Johannesburg",
  "bedtime": "22:00:00",
  "wake_time": "06:00:00",
  "fitness_level": "INTERMEDIATE",
  "max_weekly_workout_volume": 15000,
  "typical_work_hours_per_week": 40,
  "work_start_time": "08:00:00",
  "work_end_time": "17:00:00",
  "avg_task_estimation_error": 12.5,
  "total_completed_tasks": 156,
  "total_completed_workouts": 78
}
```

### Update Profile

**PATCH** `/profile`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "timezone": "Africa/Johannesburg",
  "bedtime": "23:00:00",
  "fitness_level": "ADVANCED"
}
```

**Response: 200 OK**

```json
{
  "id": 1,
  "timezone": "Africa/Johannesburg",
  "bedtime": "23:00:00",
  "fitness_level": "ADVANCED"
}
```

---

## Tasks

### List Tasks

**GET** `/tasks`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `status` (optional): TODO, IN_PROGRESS, COMPLETED
- `category` (optional): Category ID
- `date` (optional): Filter by scheduled date (YYYY-MM-DD)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Results per page (default: 20)

**Response: 200 OK**

```json
{
  "count": 45,
  "next": "https://api.axis.app/v1/tasks?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "title": "XYZ Mine Inspection",
      "description": "Monthly safety inspection",
      "category": {
        "id": 1,
        "name": "WORK",
        "color_hex": "#EF4444"
      },
      "priority": 5,
      "estimated_duration": 120,
      "actual_duration": null,
      "predicted_duration": 135,
      "energy_requirement": "HIGH",
      "due_date": "2026-03-20",
      "scheduled_date": "2026-03-18",
      "scheduled_time": "09:00:00",
      "auto_scheduled": false,
      "status": "TODO",
      "completed": false,
      "location": {
        "id": 456,
        "name": "XYZ Mine",
        "latitude": -26.2041,
        "longitude": 28.0473
      },
      "related_workout_id": null,
      "related_expense_id": null,
      "is_recurring": false,
      "auto_created": true,
      "created_at": "2026-03-15T10:30:00Z",
      "updated_at": "2026-03-15T10:30:00Z"
    }
  ]
}
```

### Get Task

**GET** `/tasks/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 200 OK**

```json
{
  "id": 123,
  "title": "XYZ Mine Inspection",
  "description": "Monthly safety inspection",
  "category": {
    "id": 1,
    "name": "WORK"
  },
  "priority": 5,
  "estimated_duration": 120,
  "predicted_duration": 135,
  "prediction_reasoning": "Adjusted for: No recent workout (+0%), Normal workload (+0%), Morning time (-5%)",
  "status": "TODO",
  "location": {
    "id": 456,
    "name": "XYZ Mine"
  }
}
```

### Create Task

**POST** `/tasks`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "title": "Write inspection report",
  "description": "Summarize findings from XYZ Mine",
  "category_id": 1,
  "priority": 4,
  "estimated_duration": 90,
  "energy_requirement": "MEDIUM",
  "due_date": "2026-03-20",
  "location_id": null
}
```

**Response: 201 Created**

```json
{
  "id": 124,
  "title": "Write inspection report",
  "estimated_duration": 90,
  "predicted_duration": 108,
  "prediction_reasoning": "Adjusted for: Workout fatigue (+15%), High workload (+5%)",
  "ai_suggestion": "Consider scheduling for tomorrow morning (30% faster when well-rested)",
  "created_at": "2026-03-15T14:30:00Z"
}
```

### Update Task

**PATCH** `/tasks/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "status": "IN_PROGRESS",
  "started_at": "2026-03-15T15:00:00Z"
}
```

**Response: 200 OK**

```json
{
  "id": 124,
  "status": "IN_PROGRESS",
  "started_at": "2026-03-15T15:00:00Z"
}
```

### Complete Task

**POST** `/tasks/{id}/complete`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "actual_duration": 95,
  "completed_at": "2026-03-15T16:35:00Z"
}
```

**Response: 200 OK**

```json
{
  "id": 124,
  "status": "COMPLETED",
  "completed": true,
  "estimated_duration": 90,
  "predicted_duration": 108,
  "actual_duration": 95,
  "estimation_accuracy": "Your estimate was 5% under, AI was 13% over",
  "context_recorded": true
}
```

### Delete Task

**DELETE** `/tasks/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 204 No Content**

### Request AI Schedule

**POST** `/tasks/{id}/schedule`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 200 OK**

```json
{
  "suggested_date": "2026-03-17",
  "suggested_time": "09:30:00",
  "reasoning": "Peak morning energy, 3 days before deadline, no conflicting tasks",
  "confidence": 0.88,
  "alternative_slots": [
    {
      "date": "2026-03-17",
      "time": "14:00:00",
      "reasoning": "Post-lunch, lower energy but still available"
    }
  ]
}
```

---

## Locations

### List Locations

**GET** `/locations`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `zone_type` (optional): Filter by zone type
- `is_work_location` (optional): true or false

**Response: 200 OK**

```json
{
  "count": 8,
  "results": [
    {
      "id": 456,
      "name": "XYZ Mine",
      "address": "123 Mining Road, Johannesburg",
      "latitude": -26.2041,
      "longitude": 28.0473,
      "radius_meters": 150,
      "zone_type": "WORK",
      "is_work_location": true,
      "work_location_type": "MINE",
      "inspection_frequency": "MONTHLY",
      "last_inspection_date": "2026-02-15",
      "next_inspection_due": "2026-03-15",
      "visit_count": 12,
      "total_time_spent_minutes": 1440,
      "is_frequent": true
    }
  ]
}
```

### Create Location

**POST** `/locations`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "name": "ABC Police Station",
  "address": "456 Law Street, Pretoria",
  "latitude": -25.7479,
  "longitude": 28.2293,
  "radius_meters": 100,
  "zone_type": "WORK",
  "is_work_location": true,
  "work_location_type": "POLICE_STATION",
  "inspection_frequency": "QUARTERLY"
}
```

**Response: 201 Created**

```json
{
  "id": 457,
  "name": "ABC Police Station",
  "latitude": -25.7479,
  "longitude": 28.2293,
  "inspection_frequency": "QUARTERLY",
  "next_inspection_due": "2026-06-15"
}
```

### Update Location

**PATCH** `/locations/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "inspection_frequency": "MONTHLY"
}
```

**Response: 200 OK**

### Delete Location

**DELETE** `/locations/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 204 No Content**

### Record Location Visit

**POST** `/locations/{id}/visit`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "arrived_at": "2026-03-15T09:28:00Z",
  "visit_type_id": 1,
  "purpose": "Monthly safety inspection",
  "from_location_id": 5
}
```

**Response: 201 Created**

```json
{
  "id": 789,
  "location_id": 456,
  "arrived_at": "2026-03-15T09:28:00Z",
  "visit_type": "MINE_INSPECTION",
  "travel_time_minutes": 88,
  "travel_prediction_accuracy": "Predicted 90 min, actual 88 min (98% accurate)",
  "auto_created_task": {
    "id": 125,
    "title": "XYZ Mine Inspection"
  }
}
```

### End Location Visit

**PATCH** `/locations/visits/{visit_id}/end`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "departed_at": "2026-03-15T12:15:00Z",
  "notes": "All safety checks passed. Equipment operational."
}
```

**Response: 200 OK**

```json
{
  "id": 789,
  "duration_minutes": 167,
  "notes": "All safety checks passed. Equipment operational."
}
```

---

## Travel & ETA

### Predict ETA

**POST** `/travel/predict-eta`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "from_location_id": 5,
  "to_location_id": 456,
  "departure_time": "2026-03-17T08:00:00Z"
}
```

**Response: 200 OK**

```json
{
  "duration_minutes": 92,
  "confidence": 0.88,
  "method": "Hybrid",
  "distance_km": 64.2,
  "distance_estimate": 55,
  "ml_estimate": 95,
  "weight_distance": 0.2,
  "weight_ml": 0.8,
  "trips_count": 8,
  "reasoning": "Based on 8 previous trips. Monday morning traffic typically adds 15 minutes.",
  "suggested_departure": "2026-03-17T07:28:00Z",
  "arrival_time": "2026-03-17T09:00:00Z"
}
```

### Get Travel History

**GET** `/travel/history`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `from_location_id` (optional)
- `to_location_id` (optional)
- `limit` (optional): Default 20

**Response: 200 OK**

```json
{
  "count": 8,
  "results": [
    {
      "id": 234,
      "from_location": {
        "id": 5,
        "name": "Home"
      },
      "to_location": {
        "id": 456,
        "name": "XYZ Mine"
      },
      "departed_at": "2026-03-15T08:00:00Z",
      "arrived_at": "2026-03-15T09:28:00Z",
      "duration_minutes": 88,
      "distance_km": 64.2,
      "avg_speed_kmh": 43.7,
      "was_predicted": true,
      "predicted_duration": 90,
      "prediction_error": -2
    }
  ]
}
```

---

## Workouts

### List Workout Sessions

**GET** `/workouts/sessions`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `status` (optional): PLANNED, IN_PROGRESS, COMPLETED
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Response: 200 OK**

```json
{
  "count": 15,
  "results": [
    {
      "id": 567,
      "title": "Leg Day",
      "date": "2026-03-15",
      "start_time": "2026-03-15T16:00:00Z",
      "end_time": "2026-03-15T17:15:00Z",
      "planned_duration": 60,
      "actual_duration": 75,
      "status": "COMPLETED",
      "total_planned_reps": 120,
      "total_actual_reps": 114,
      "completion_percentage": 95.0,
      "location": {
        "id": 10,
        "name": "Gym"
      },
      "energy_level_before": 8,
      "energy_level_after": 5
    }
  ]
}
```

### Create Workout Session

**POST** `/workouts/sessions`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "title": "Push Day",
  "date": "2026-03-16",
  "planned_duration": 60,
  "location_id": 10,
  "exercises": [
    {
      "exercise_id": 45,
      "planned_sets": 3,
      "planned_reps_per_set": 25,
      "planned_rest_seconds": 120
    }
  ]
}
```

**Response: 201 Created**

```json
{
  "id": 568,
  "title": "Push Day",
  "date": "2026-03-16",
  "status": "PLANNED",
  "exercises_count": 1
}
```

### Start Workout

**POST** `/workouts/sessions/{id}/start`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "energy_level_before": 7
}
```

**Response: 200 OK**

```json
{
  "id": 568,
  "status": "IN_PROGRESS",
  "start_time": "2026-03-16T17:00:00Z"
}
```

### Log Exercise Set

**POST** `/workouts/sessions/{session_id}/exercises/{exercise_id}/log-set`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "set_number": 1,
  "reps": 23,
  "duration_seconds": null,
  "rest_seconds": 135
}
```

**Response: 200 OK**

```json
{
  "set_logged": true,
  "sets_completed": 1,
  "sets_remaining": 2
}
```

### Complete Workout

**POST** `/workouts/sessions/{id}/complete`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "energy_level_after": 5,
  "notes": "Felt strong. Increased reps on set 2."
}
```

**Response: 200 OK**

```json
{
  "id": 568,
  "status": "COMPLETED",
  "actual_duration": 68,
  "completion_percentage": 98.5,
  "total_volume_kg": 11500,
  "fatigue_calculated": 32,
  "context_updated": true,
  "recommendation": "High intensity workout. Rest day recommended tomorrow."
}
```

### Search Exercises

**GET** `/workouts/exercises`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `search` (optional): Search by name
- `discipline_id` (optional): Filter by discipline
- `equipment_id` (optional): Filter by equipment
- `muscle_group_id` (optional): Filter by muscle group

**Response: 200 OK**

```json
{
  "count": 450,
  "results": [
    {
      "id": 45,
      "name": "Push-ups",
      "slug": "push-ups",
      "discipline": {
        "id": 1,
        "name": "Calisthenics"
      },
      "difficulty_level": "BEGINNER",
      "primary_equipment": {
        "id": 1,
        "name": "Bodyweight"
      },
      "primary_muscle_group": {
        "id": 5,
        "name": "Chest"
      },
      "measurement_type": "REPS",
      "typical_rep_range": "15-25",
      "demo_video_url": "https://cdn.axis.app/videos/push-ups.mp4"
    }
  ]
}
```

---

## Finance

### List Expenses

**GET** `/expenses`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `category_id` (optional)
- `date_from` (optional)
- `date_to` (optional)
- `location_id` (optional)

**Response: 200 OK**

```json
{
  "count": 67,
  "results": [
    {
      "id": 890,
      "amount": "500.00",
      "category": {
        "id": 8,
        "name": "WORK",
        "color_hex": "#06B6D4"
      },
      "description": "Fuel",
      "notes": null,
      "payment_method": "CARD",
      "location": {
        "id": 456,
        "name": "XYZ Mine"
      },
      "related_task": {
        "id": 123,
        "title": "XYZ Mine Inspection"
      },
      "auto_tagged": true,
      "expense_date": "2026-03-15",
      "expense_time": "10:45:00",
      "created_at": "2026-03-15T10:45:30Z"
    }
  ]
}
```

### Create Expense

**POST** `/expenses`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "amount": 500.00,
  "category_id": 8,
  "description": "Fuel",
  "payment_method": "CARD",
  "expense_date": "2026-03-15",
  "expense_time": "10:45:00"
}
```

**Response: 201 Created**

```json
{
  "id": 890,
  "amount": "500.00",
  "category": {
    "id": 8,
    "name": "WORK"
  },
  "auto_linked": true,
  "linked_to_task": {
    "id": 123,
    "title": "XYZ Mine Inspection"
  },
  "linked_to_location": {
    "id": 456,
    "name": "XYZ Mine"
  },
  "budget_impact": {
    "spent_today": 500.00,
    "spent_this_month": 2950.00,
    "budget_limit": 3000.00,
    "percentage_used": 98.3,
    "warning": "Budget 98% exhausted"
  }
}
```

### Update Expense

**PATCH** `/expenses/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "category_id": 10,
  "notes": "Reimbursable"
}
```

**Response: 200 OK**

### Delete Expense

**DELETE** `/expenses/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 204 No Content**

### Get Budget

**GET** `/budget`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `month` (optional): YYYY-MM format (default: current month)

**Response: 200 OK**

```json
{
  "id": 12,
  "budget_type": "MONTHLY",
  "month": "2026-03",
  "allocated_amount": "3000.00",
  "spent_amount": "2950.00",
  "remaining_amount": "50.00",
  "percentage_used": 98.3,
  "category_allocations": {
    "WORK": 1500.00,
    "FOOD": 800.00,
    "TRANSPORT": 400.00,
    "OTHER": 300.00
  },
  "category_spent": {
    "WORK": 1480.00,
    "FOOD": 720.00,
    "TRANSPORT": 450.00,
    "OTHER": 300.00
  },
  "days_remaining": 16,
  "projection": "At current rate, you'll exceed budget by R200"
}
```

### Update Budget

**PATCH** `/budget/{month}`

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**

```json
{
  "allocated_amount": 3500.00,
  "category_allocations": {
    "WORK": 1800.00,
    "FOOD": 900.00
  }
}
```

**Response: 200 OK**

---

## Intelligence Hub

### Get User Context

**GET** `/intelligence/context`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 200 OK**

```json
{
  "current_location": {
    "id": 5,
    "name": "Home"
  },
  "current_energy_level": 7,
  "work_hours_today": 4,
  "workout_today": false,
  "tasks_completed_today": 3,
  "spent_today": "125.00",
  "work_hours_this_week": 22,
  "workouts_this_week": 4,
  "spent_this_week": "1450.00",
  "consecutive_work_days": 4,
  "consecutive_workout_days": 4,
  "over_budget": false,
  "last_updated": "2026-03-15T14:30:00Z"
}
```

### Get Recommendations

**GET** `/intelligence/recommendations`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 200 OK**

```json
{
  "count": 3,
  "recommendations": [
    {
      "id": 1,
      "type": "HEALTH",
      "priority": "HIGH",
      "message": "Rest day recommended",
      "reason": "You've worked out 4 consecutive days",
      "action": "Skip tomorrow's planned workout",
      "created_at": "2026-03-15T14:00:00Z"
    },
    {
      "id": 2,
      "type": "FINANCIAL",
      "priority": "MEDIUM",
      "message": "Budget 98% exhausted",
      "reason": "Spent R2,950 of R3,000 with 16 days remaining",
      "action": "Review non-essential expenses",
      "created_at": "2026-03-15T10:45:35Z"
    },
    {
      "id": 3,
      "type": "LOCATION",
      "priority": "LOW",
      "message": "Inspection due soon",
      "reason": "ABC Police Station last inspected 85 days ago (quarterly due)",
      "action": "Schedule inspection within 5 days",
      "created_at": "2026-03-15T06:00:00Z"
    }
  ]
}
```

### Dismiss Recommendation

**DELETE** `/intelligence/recommendations/{id}`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 204 No Content**

---

## Notifications

### List Notifications

**GET** `/notifications`

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**

- `is_read` (optional): true or false

**Response: 200 OK**

```json
{
  "count": 8,
  "unread_count": 3,
  "results": [
    {
      "id": 456,
      "title": "Task Auto-Created",
      "message": "XYZ Mine Inspection task created on arrival",
      "notification_type": "TASK_AUTO_CREATED",
      "action_url": "/tasks/123",
      "action_type": "VIEW_TASK",
      "is_read": false,
      "is_pushed": true,
      "priority": 3,
      "created_at": "2026-03-15T09:28:30Z"
    }
  ]
}
```

### Mark as Read

**PATCH** `/notifications/{id}/read`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 200 OK**

### Mark All as Read

**POST** `/notifications/read-all`

**Headers:** `Authorization: Bearer {access_token}`

**Response: 200 OK**

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request

```json
{
  "error": "Validation error",
  "details": {
    "estimated_duration": ["This field is required"]
  }
}
```

### 401 Unauthorized

```json
{
  "error": "Authentication credentials were not provided"
}
```

### 403 Forbidden

```json
{
  "error": "You do not have permission to perform this action"
}
```

### 404 Not Found

```json
{
  "error": "Task not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred",
  "request_id": "req_abc123"
}
```

---

## Pagination

List endpoints return paginated results:

```json
{
  "count": 156,
  "next": "https://api.axis.app/v1/tasks?page=3",
  "previous": "https://api.axis.app/v1/tasks?page=1",
  "results": []
}
```

**Query Parameters:**

- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

---

## Rate Limiting

**Limits:**

- Authenticated: 1000 requests/hour
- Unauthenticated: 100 requests/hour

**Headers:**

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1710511200
