# Intelligence Hub

**Author:** Pfarelo Channel Mudau  
**Created:** 2026-03-15  
**Purpose:** Central intelligence system for cross-module analysis and smart recommendations

---

## Overview

The Intelligence Hub is AXIS's central brain that connects all modules together.

**Without Intelligence Hub:**
- Tasks module only knows about tasks
- Workouts module only knows about workouts
- Finance module only knows about expenses
- Location module only knows about places
- **No communication = No intelligence**

**With Intelligence Hub:**
- All modules report to the Hub
- Hub analyzes data from all modules
- Hub makes intelligent decisions
- Hub coordinates automated actions
- **Result: The app understands your life holistically**

---

## What It Does

### 1. Analyzes Your Current State

The Hub constantly tracks:
- Where you are (location)
- How tired you are (energy level)
- What you've done today (work hours, workouts, tasks)
- How much you've spent (budget status)
- Your patterns over time (work days, workout streaks)

### 2. Makes Intelligent Predictions

When you create a task:
- Hub checks: Did you workout today? (adds fatigue penalty)
- Hub checks: How many hours worked? (adds mental fatigue)
- Hub checks: What time is it? (considers productivity curve)
- **Result:** "This will take 78 minutes, not 60"

### 3. Automates Repetitive Actions

When you arrive at XYZ Mine:
- Hub detects: GPS coordinates match work location
- Hub checks: Last inspection was 28 days ago
- Hub creates: "XYZ Mine Inspection" task automatically
- **Result:** You don't have to remember to create the task

### 4. Provides Proactive Recommendations

The Hub warns you before problems:
- "You've worked out 6 days straight - rest recommended"
- "You've spent 80% of budget - review expenses"
- "You work 10+ hours on Mondays - schedule breaks"

### 5. Continuously Learns

Every task completed, every workout finished, every trip taken:
- Hub records actual vs predicted data
- Hub identifies patterns
- Hub retrains ML models
- **Result:** Predictions improve over time

---

## Architecture

Displayed in [Intelligence Hub Architecture](diagrams/intelligence-hub-architecture.drawio.png)

---

## Core Components

### 1. Context Engine

**What it does:** Maintains your current state in real-time

**Data tracked:**

| Field | Description | Example |
|-------|-------------|---------|
| `current_location_id` | Where you are now | XYZ Mine |
| `current_energy_level` | Energy (1-10 scale) | 6/10 |
| `work_hours_today` | Hours worked today | 7 hours |
| `workout_today` | Did you workout? | Yes |
| `tasks_completed_today` | Tasks finished | 5 |
| `spent_today` | Money spent | R450.00 |
| `workouts_this_week` | Weekly workout count | 5 |
| `consecutive_workout_days` | Workout streak | 5 days |
| `over_budget` | Budget exceeded? | No |

**When it updates:**
- Task completed → Increment task count, add work hours
- Workout finished → Set workout_today = true, update energy
- Expense logged → Add to spent_today, check budget
- Location changed → Update current_location_id
- Midnight → Reset daily counters

**Database table:** `user_context_state`

---

### 2. Duration Predictor

**What it does:** Predicts how long tasks will actually take (not what you estimate)

**Factors considered:**

1. **Your estimation history:** Do you usually underestimate or overestimate?
2. **Workout fatigue:** Recent workout = tasks take longer
3. **Mental fatigue:** Many work hours = slower thinking
4. **Time of day:** Morning = faster, evening = slower
5. **Task category:** Work tasks vs personal tasks have different patterns
6. **Location:** Home = focused, public place = distractions

**Calculation flow:**

Displayed in [Duration Prediction Flow](diagrams/duration-prediction-flow.drawio.png)

---

### 3. Smart Scheduler

**What it does:** Finds the optimal time to do tasks

**Criteria considered:**

1. **Energy requirements:** High-energy tasks during peak hours (morning)
2. **Due dates:** Urgent tasks get priority slots
3. **Available time:** Only schedule in free blocks
4. **Location:** Schedule mine inspections when you're near mines
5. **Fatigue:** Don't schedule heavy tasks after workouts
6. **Preferences:** Respect your work hours and sleep schedule

**Scheduling flow:**

Displayed in [Smart Scheduling Flow](diagrams/smart-scheduling-flow.drawio.png)

---

### 4. ML Model Manager

**What it does:** Trains and manages machine learning models

**Models managed:**

| Model | Purpose | Training Data |
|-------|---------|---------------|
| Task Duration Model | Predict task completion time | Task completion history |
| Travel Time Model | Predict ETA (see Hybrid ETA Algorithm) | Travel history |
| Workout Duration Model | Predict workout session length | Workout sessions |
| Budget Prediction Model | Predict monthly spending | Expense history |

**Training schedule:**

- **Immediate:** After 10+ new data points collected
- **Daily (02:00):** Lightweight updates using yesterday's data
- **Weekly (Sunday 03:00):** Full model retraining
- **On-demand:** When prediction accuracy drops below 70%

---

### 5. Recommendation Engine

**What it does:** Provides proactive suggestions before problems occur

**Recommendation types:**

**Health & Wellness:**
- "You've worked out 6 days straight. Rest day recommended."
- "Low energy detected (3/10). Consider light workout instead of planned HIIT."

**Productivity:**
- "You've worked 50 hours this week. Schedule rest this weekend."
- "Your focus drops after 18:00. Reschedule complex tasks to morning."

**Financial:**
- "You've spent 80% of monthly budget with 10 days remaining."
- "Work expenses this month: R3,200. Remember to claim reimbursement."

**Location & Travel:**
- "You haven't inspected XYZ Mine in 28 days. Schedule visit?"
- "Traffic to [location] peaks at 08:00. Leave by 07:30 to arrive on time."

---

## Summary

The Intelligence Hub is what makes AXIS truly intelligent:

1. ✅ **Cross-Module Awareness:** All modules communicate through the Hub
2. ✅ **Context-Based Decisions:** Every action considers your current state
3. ✅ **Proactive Recommendations:** Warns before problems occur
4. ✅ **Continuous Learning:** ML models improve with every data point
5. ✅ **Automation:** Auto-creates tasks, links expenses, adjusts schedules

**Without Intelligence Hub:** AXIS is just 4 separate apps

**With Intelligence Hub:** AXIS understands your life holistically and adapts to help you

---

**Next:** See [API Specification](api-specification.md) for endpoint details