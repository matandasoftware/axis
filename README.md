# AXIS

Intelligent life management system with adaptive scheduling, workout tracking, financial management, and location-based intelligence.

## Overview

AXIS is a tightly integrated system that learns from your behavior to intelligently manage tasks, workouts, finances, and location tracking.

### Key Features

- **Adaptive Task Scheduling**: Auto-schedule based on energy, workload, and context
- **Real-Time Workout Tracking**: Live session monitoring with intelligent suggestions
- **Financial Intelligence**: Location-based expense tracking and auto-tagging
- **Work Travel Optimization**: Learns inspection routes and predicts travel times
- **Cross-Module Awareness**: Workout fatigue affects task scheduling, expenses link to locations

## System Architecture

![System Overview](docs/diagrams/system-overview.png)

See [System Architecture](docs/system-architecture.md) for detailed diagrams.

## Project Structure

<table>
<tr>
<td width="50%" valign="top">

<pre>
axis/
│
├── backend/
│   └── .gitkeep
│
├── frontend-web/
│   └── .gitkeep
│
├── frontend-mobile/
│   └── .gitkeep
│
├── docs/
│   │
│   ├── diagrams/                    ← Place your draw.io exports here
│   │   ├── create-task-flow.drawio.png
│   │   ├── database-erd.drawio.png
│   │   ├── module-integration.drawio.png
│   │   ├── system-overview.drawio.png
│   │   ├── tech-stack.drawio.png
│   │   ├── work-travel-flow.drawio.png
│   │   └── workout-session-flow.drawio.png
│   │
│   ├── system-architecture.md
│   ├── database-schema.sql
│   ├── hybrid-eta-algorithm.md
│   ├── intelligence-hub.md
│   ├── api-specification.md
│   └── implementation-plan.md
│
├── README.md
└── .gitignore
</pre>

</td>
<td width="50%" valign="top">

**Directory Descriptions:**

**`backend/`**  
Django backend application (to be implemented)

**`frontend-web/`**  
React web application with TypeScript

**`frontend-mobile/`**  
React Native mobile app with Expo

**`docs/`**  
Complete project documentation

**`docs/diagrams/`**  
Architecture and flow diagrams (Draw.io exports)

**Key Documentation:**
- `system-architecture.md` - Architecture overview
- `database-schema.sql` - PostgreSQL schema
- `hybrid-eta-algorithm.md` - ETA prediction algorithm
- `intelligence-hub.md` - Central intelligence system
- `api-specification.md` - REST API endpoints
- `implementation-plan.md` - Build roadmap

</td>
</tr>
</table>


## Technology Stack

**Backend**
- Django 5.0 with Django REST Framework
- PostgreSQL 15 for relational data
- Redis 7 for caching and queues
- Celery for background tasks
- Django Channels for WebSockets

**Frontend Web**
- React 19 with TypeScript
- Redux Toolkit for state management
- Tailwind CSS 4 for styling
- Vite 7 for build tooling

**Frontend Mobile**
- React Native with Expo
- Native device APIs for GPS tracking

**Machine Learning**
- scikit-learn for prediction models
- pandas for data processing
- numpy for numerical operations

## Getting Started

1. Review [System Architecture](docs/system-architecture.md)
2. Study [Database Schema](docs/database-schema.sql)
3. Understand [Hybrid ETA Algorithm](docs/hybrid-eta-algorithm.md)
4. Follow [Implementation Plan](docs/implementation-plan.md)

## Module Integration

![Module Integration](docs/diagrams/module-integration.png)

All modules are tightly integrated:
- Tasks check workout fatigue before scheduling
- Workouts create tasks automatically
- Expenses auto-link to tasks and locations
- Location detection triggers task creation

## Use Case: Work Travel Intelligence

Designed for monthly mine/station inspections:

1. System detects arrival at known work location
2. Auto-creates inspection task
3. Tracks time spent on-site
4. Prompts for related expenses
5. Links expenses to inspection task
6. Learns travel times for future predictions

See [Work Travel Flow](docs/diagrams/work-travel-flow.png)

## Author

Pfarelo Channel Mudau

GitHub: [@matandasoftware](https://github.com/matandasoftware)

## Status

**Current Phase**: Planning & Documentation

Next: Backend implementation