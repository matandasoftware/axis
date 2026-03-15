-- AXIS DATABASE SCHEMA
-- PostgreSQL 15
-- Author: Pfarelo Channel Mudau
-- Created: 2026-03-15

-- This schema implements a tightly integrated design where all modules
-- (Tasks, Workouts, Finance, Location) share data through foreign keys.


-- ACCOUNTS MODULE

CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    date_of_birth DATE,
    phone_number VARCHAR(20),
    profile_picture VARCHAR(255),
    
    timezone VARCHAR(50) DEFAULT 'Africa/Johannesburg',
    bedtime TIME DEFAULT '22:00:00',
    wake_time TIME DEFAULT '06:00:00',
    
    fitness_level VARCHAR(20) DEFAULT 'INTERMEDIATE',
    max_weekly_workout_volume INTEGER DEFAULT 15000,
    
    typical_work_hours_per_week INTEGER DEFAULT 40,
    work_start_time TIME DEFAULT '08:00:00',
    work_end_time TIME DEFAULT '17:00:00',
    
    avg_task_estimation_error DECIMAL(5,2) DEFAULT 0.00,
    total_completed_tasks INTEGER DEFAULT 0,
    total_completed_workouts INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_user ON user_profiles(user_id);


-- LOCATIONS MODULE

CREATE TABLE locations (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    address TEXT,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    radius_meters INTEGER DEFAULT 100,
    
    zone_type VARCHAR(50) NOT NULL,
    
    is_work_location BOOLEAN DEFAULT FALSE,
    work_location_type VARCHAR(50),
    inspection_frequency VARCHAR(20),
    last_inspection_date DATE,
    
    visit_count INTEGER DEFAULT 0,
    total_time_spent_minutes INTEGER DEFAULT 0,
    is_frequent BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_locations_user ON locations(user_id);
CREATE INDEX idx_locations_coordinates ON locations(latitude, longitude);
CREATE INDEX idx_locations_zone_type ON locations(zone_type);


CREATE TABLE location_visits (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,

    arrived_at TIMESTAMP NOT NULL,
    departed_at TIMESTAMP,
    duration_minutes INTEGER,

    visit_type_id INTEGER REFERENCES visit_types(id),
    purpose TEXT,
    notes TEXT,
    inspection_report_url VARCHAR(255),

    from_location_id INTEGER REFERENCES locations(id),
    travel_time_minutes INTEGER,
    avg_speed_kmh DECIMAL(5,2),

    weather_condition VARCHAR(50),
    time_of_day VARCHAR(20),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_location_visits_user ON location_visits(user_id);
CREATE INDEX idx_location_visits_location ON location_visits(location_id);
CREATE INDEX idx_location_visits_date ON location_visits(arrived_at);


CREATE TABLE travel_history (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    from_location_id INTEGER NOT NULL REFERENCES locations(id),
    to_location_id INTEGER NOT NULL REFERENCES locations(id),
    
    departed_at TIMESTAMP NOT NULL,
    arrived_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL,
    
    distance_km DECIMAL(10,2),
    
    avg_speed_kmh DECIMAL(5,2),
    max_speed_kmh DECIMAL(5,2),
    
    day_of_week INTEGER,
    hour_of_day INTEGER,
    is_rush_hour BOOLEAN,
    weather_condition VARCHAR(50),
    
    was_predicted BOOLEAN DEFAULT FALSE,
    predicted_duration INTEGER,
    prediction_error INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_travel_history_user ON travel_history(user_id);
CREATE INDEX idx_travel_history_route ON travel_history(from_location_id, to_location_id);


CREATE TABLE visit_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(50),
    icon VARCHAR(50),
    description TEXT
);

INSERT INTO visit_types (name, category, icon, description) VALUES
('MINE_INSPECTION', 'WORK', 'hard-hat', 'Mine safety and compliance inspection'),
('POLICE_STATION_INSPECTION', 'WORK', 'shield', 'Police station facility inspection'),
('SCHOOL_INSPECTION', 'WORK', 'school', 'Educational facility inspection'),
('HOSPITAL_INSPECTION', 'WORK', 'hospital', 'Medical facility inspection'),
('DELIVERY', 'WORK', 'truck', 'Package or equipment delivery'),
('MEETING', 'WORK', 'users', 'Business meeting or consultation'),
('SHOPPING', 'PERSONAL', 'shopping-cart', 'Shopping trip'),
('SOCIAL_VISIT', 'PERSONAL', 'heart', 'Visiting friends or family'),
('GYM_SESSION', 'FITNESS', 'dumbbell', 'Workout at gym'),
('OTHER', 'GENERAL', 'star', 'Other visit purpose');


-- TASKS MODULE

CREATE TABLE task_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color_hex VARCHAR(7) DEFAULT '#3B82F6',
    icon VARCHAR(50),
    description TEXT
);

INSERT INTO task_categories (name, color_hex, icon, description) VALUES
('WORK', '#EF4444', 'briefcase', 'Work-related tasks'),
('PERSONAL', '#10B981', 'user', 'Personal errands and activities'),
('WORKOUT', '#F59E0B', 'dumbbell', 'Exercise and fitness'),
('STUDY', '#8B5CF6', 'book', 'Learning and education'),
('SOCIAL', '#EC4899', 'users', 'Social activities'),
('REST', '#06B6D4', 'moon', 'Rest and recovery'),
('BIBLE_STUDY', '#6366F1', 'bible', 'Bible reading and study'),
('OTHER', '#6B7280', 'star', 'Miscellaneous tasks');


CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL REFERENCES task_categories(id),
    
    priority INTEGER DEFAULT 3,
    
    estimated_duration INTEGER NOT NULL,
    actual_duration INTEGER,
    
    energy_requirement VARCHAR(20) DEFAULT 'MEDIUM',
    
    due_date DATE,
    scheduled_date DATE,
    scheduled_time TIME,
    auto_scheduled BOOLEAN DEFAULT FALSE,
    
    status VARCHAR(20) DEFAULT 'TODO',
    completed BOOLEAN DEFAULT FALSE,
    
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    location_id INTEGER REFERENCES locations(id),
    related_workout_id INTEGER,
    related_expense_id INTEGER,
    
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(50),
    recurrence_data JSONB,
    parent_task_id INTEGER REFERENCES tasks(id),
    
    auto_created BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_category ON tasks(category_id);
CREATE INDEX idx_tasks_status ON tasks(status, completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_scheduled ON tasks(scheduled_date, scheduled_time);
CREATE INDEX idx_tasks_location ON tasks(location_id);


CREATE TABLE task_completion_history (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    
    estimated_duration INTEGER NOT NULL,
    actual_duration INTEGER NOT NULL,
    duration_error INTEGER,
    duration_error_percentage DECIMAL(5,2),
    
    completed_at TIMESTAMP NOT NULL,
    day_of_week INTEGER,
    hour_of_day INTEGER,
    location_id INTEGER REFERENCES locations(id),
    
    energy_level_before INTEGER,
    work_hours_today INTEGER,
    workout_today BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_task_history_user ON task_completion_history(user_id);
CREATE INDEX idx_task_history_task ON task_completion_history(task_id);


-- WORKOUTS MODULE

CREATE TABLE training_disciplines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE equipment_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE muscle_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    anatomical_name VARCHAR(100),
    description TEXT
);


CREATE TABLE difficulty_levels (
    id SERIAL PRIMARY KEY,
    level VARCHAR(50) UNIQUE NOT NULL,
    numeric_value INTEGER,
    description TEXT
);


CREATE TABLE exercises (
    id BIGSERIAL PRIMARY KEY,
    
    name VARCHAR(200) NOT NULL,
    alternate_names TEXT[],
    slug VARCHAR(200) UNIQUE NOT NULL,
    
    discipline_id INTEGER REFERENCES training_disciplines(id),
    difficulty_level_id INTEGER REFERENCES difficulty_levels(id),
    
    primary_equipment_id INTEGER REFERENCES equipment_types(id),
    secondary_equipment_ids INTEGER[],
    
    description TEXT,
    instructions TEXT,
    tips TEXT,
    
    primary_muscle_group_id INTEGER REFERENCES muscle_groups(id),
    secondary_muscle_groups INTEGER[],
    
    demo_video_url VARCHAR(255),
    image_urls TEXT[],
    
    measurement_type VARCHAR(50),
    typical_rep_range VARCHAR(50),
    typical_rest_seconds INTEGER,
    
    easier_variation_id INTEGER REFERENCES exercises(id),
    harder_variation_id INTEGER REFERENCES exercises(id),
    
    tags TEXT[],
    
    is_custom BOOLEAN DEFAULT FALSE,
    created_by_user_id INTEGER REFERENCES auth_user(id),
    is_approved BOOLEAN DEFAULT FALSE,
    
    times_performed INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_exercises_discipline ON exercises(discipline_id);
CREATE INDEX idx_exercises_difficulty ON exercises(difficulty_level_id);
CREATE INDEX idx_exercises_equipment ON exercises(primary_equipment_id);
CREATE INDEX idx_exercises_muscle ON exercises(primary_muscle_group_id);
CREATE INDEX idx_exercises_tags ON exercises USING GIN(tags);


CREATE TABLE workout_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    title VARCHAR(200),
    date DATE NOT NULL,
    
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    planned_duration INTEGER,
    actual_duration INTEGER,
    
    status VARCHAR(20) DEFAULT 'PLANNED',
    
    total_planned_reps INTEGER,
    total_actual_reps INTEGER,
    completion_percentage DECIMAL(5,2),
    
    location_id INTEGER REFERENCES locations(id),
    related_task_id INTEGER REFERENCES tasks(id),
    
    notes TEXT,
    energy_level_before INTEGER,
    energy_level_after INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_workout_sessions_user ON workout_sessions(user_id);
CREATE INDEX idx_workout_sessions_date ON workout_sessions(date);
CREATE INDEX idx_workout_sessions_status ON workout_sessions(status);


CREATE TABLE workout_session_exercises (
    id BIGSERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    
    exercise_order INTEGER NOT NULL,
    
    planned_sets INTEGER NOT NULL,
    planned_reps_per_set INTEGER,
    planned_duration_seconds INTEGER,
    planned_rest_seconds INTEGER,
    
    completed_sets INTEGER DEFAULT 0,
    actual_reps JSONB,
    actual_durations JSONB,
    actual_rest_times JSONB,
    
    sets_completion_percentage DECIMAL(5,2),
    reps_completion_percentage DECIMAL(5,2),
    
    skipped_sets JSONB,
    
    status VARCHAR(20) DEFAULT 'PENDING',
    
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    performance_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_session_exercises_session ON workout_session_exercises(session_id);


CREATE TABLE workout_goals (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    
    goal_type VARCHAR(20) NOT NULL,
    
    baseline_value DECIMAL(10,2) NOT NULL,
    baseline_date DATE NOT NULL,
    
    target_value DECIMAL(10,2) NOT NULL,
    target_date DATE NOT NULL,
    
    current_value DECIMAL(10,2),
    last_updated DATE,
    progress_percentage DECIMAL(5,2),
    
    status VARCHAR(20) DEFAULT 'IN_PROGRESS',
    
    achieved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_workout_goals_user ON workout_goals(user_id);
CREATE INDEX idx_workout_goals_exercise ON workout_goals(exercise_id);
CREATE INDEX idx_workout_goals_status ON workout_goals(status);


-- FINANCE MODULE

CREATE TABLE expense_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color_hex VARCHAR(7) DEFAULT '#3B82F6',
    icon VARCHAR(50),
    is_default BOOLEAN DEFAULT TRUE
);

INSERT INTO expense_categories (name, color_hex, icon) VALUES
('FOOD', '#10B981', 'utensils'),
('TRANSPORT', '#3B82F6', 'car'),
('ENTERTAINMENT', '#F59E0B', 'film'),
('SHOPPING', '#EC4899', 'shopping-bag'),
('HEALTH', '#EF4444', 'heart'),
('EDUCATION', '#8B5CF6', 'book'),
('BILLS', '#6B7280', 'file-text'),
('WORK', '#06B6D4', 'briefcase'),
('GYM', '#F59E0B', 'dumbbell'),
('OTHER', '#9CA3AF', 'star');


CREATE TABLE budgets (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    budget_type VARCHAR(20) DEFAULT 'MONTHLY',
    month DATE NOT NULL,
    
    allocated_amount DECIMAL(10,2) NOT NULL,
    spent_amount DECIMAL(10,2) DEFAULT 0.00,
    
    category_allocations JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, month)
);

CREATE INDEX idx_budgets_user ON budgets(user_id);
CREATE INDEX idx_budgets_month ON budgets(month);


CREATE TABLE expenses (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    amount DECIMAL(10,2) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES expense_categories(id),
    description TEXT,
    notes TEXT,
    
    payment_method VARCHAR(50),
    
    location_id INTEGER REFERENCES locations(id),
    related_task_id INTEGER REFERENCES tasks(id),
    auto_tagged BOOLEAN DEFAULT FALSE,
    
    expense_date DATE NOT NULL,
    expense_time TIME,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_location ON expenses(location_id);


-- INTELLIGENCE HUB

CREATE TABLE user_context_state (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    current_location_id INTEGER REFERENCES locations(id),
    current_energy_level INTEGER,
    
    work_hours_today INTEGER DEFAULT 0,
    workout_today BOOLEAN DEFAULT FALSE,
    tasks_completed_today INTEGER DEFAULT 0,
    spent_today DECIMAL(10,2) DEFAULT 0.00,
    
    work_hours_this_week INTEGER DEFAULT 0,
    workouts_this_week INTEGER DEFAULT 0,
    spent_this_week DECIMAL(10,2) DEFAULT 0.00,
    
    consecutive_work_days INTEGER DEFAULT 0,
    consecutive_workout_days INTEGER DEFAULT 0,
    over_budget BOOLEAN DEFAULT FALSE,
    
    last_location_update TIMESTAMP,
    last_activity TIMESTAMP,
    
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_context_user ON user_context_state(user_id);


CREATE TABLE ml_prediction_models (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    model_type VARCHAR(50) NOT NULL,
    
    model_version VARCHAR(20),
    model_data BYTEA,
    
    training_samples INTEGER,
    accuracy_score DECIMAL(5,4),
    mae DECIMAL(10,2),
    rmse DECIMAL(10,2),
    
    feature_names TEXT[],
    feature_importance JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    trained_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ml_models_user ON ml_prediction_models(user_id);
CREATE INDEX idx_ml_models_type ON ml_prediction_models(model_type, is_active);


CREATE TABLE prediction_history (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    model_id INTEGER NOT NULL REFERENCES ml_prediction_models(id),
    
    prediction_type VARCHAR(50) NOT NULL,
    predicted_value DECIMAL(10,2) NOT NULL,
    confidence_score DECIMAL(3,2),
    
    actual_value DECIMAL(10,2),
    prediction_error DECIMAL(10,2),
    
    features_used JSONB,
    
    predicted_at TIMESTAMP NOT NULL,
    actual_recorded_at TIMESTAMP
);

CREATE INDEX idx_prediction_history_user ON prediction_history(user_id);
CREATE INDEX idx_prediction_history_model ON prediction_history(model_id);


-- NOTIFICATIONS

CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    
    action_url VARCHAR(255),
    action_type VARCHAR(50),
    
    is_read BOOLEAN DEFAULT FALSE,
    is_pushed BOOLEAN DEFAULT FALSE,
    
    priority INTEGER DEFAULT 3,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);