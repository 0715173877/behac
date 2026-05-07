# Behac International Academy - School Management System

A comprehensive Django-based school management system for **Behac International Academy**. This system manages students, academics, staff, finance, behavior records, and parent communication through role-based dashboards.

---

## Django Apps Overview

### 1. `core` — Academic Calendar Management
**Purpose:** Manages the school's academic calendar — academic years and terms.

- **Models:** `AcademicYear`, `Term`
- **Key Features:**
  - Define academic years (e.g., "2025-2026") with start/end dates
  - Set the current active academic year (only one can be current at a time)
  - Define terms (Term 1, 2, 3) within each academic year
  - Activate/deactivate terms
- **URLs:** `/core/academic-years/`, `/core/terms/`

---

### 2. `students` — Student Registration & Management
**Purpose:** Manages student profiles, parent accounts, and family relationships.

- **Models:** `Student`, `OtherRelative`, `Relationship`, `StudentClassHistory`
- **Key Features:**
  - Auto-generates registration numbers (`BIA-YYYY-NNNN`)
  - Tracks personal info, NIDA, birth certificate, religion, address
  - Links each student to a parent Django user account (auto-created with email credentials)
  - Supports multiple other relatives per student (e.g., aunt, uncle)
  - Tracks class history across academic years
  - Bulk import students via Excel/CSV
  - Age calculation from date of birth
- **URLs:** `/students/`

---

### 3. `academics` — Academics & Curriculum
**Purpose:** Manages classes, subjects, exams, results, attendance, assignments, and timetables.

- **Models:** `ClassLevel`, `Subject`, `Exam`, `Result`, `Attendance`, `Assignment`, `Timetable`
- **Key Features:**
  - Class levels (Pre-primary & Primary) with ordering
  - Subjects with unique codes, assignable to multiple class levels
  - Exam definitions with max/passing marks
  - Result recording with automatic letter grading (A-F)
  - Daily attendance tracking (Present/Absent/Late)
  - Assignments with file uploads and due dates
  - Weekly timetables with periods, subjects, and teacher assignments
  - **Bulk result upload** via Excel with validation
  - Teacher-scoped filtering (teachers only see their assigned classes/subjects)
- **URLs:** `/academics/`

---

### 4. `finance` — Fee Management & Payments
**Purpose:** Manages fee structures, payments, receipts, and outstanding balances.

- **Models:** `FeeCategory`, `FeeStructure`, `Payment`, `FeeReminder`
- **Key Features:**
  - Fee categories (School Fee, Buns & Transport, Sweater, etc.) — recurring or one-time
  - Fee structures linking categories to class levels and academic years
  - Payment recording with auto-generated receipt numbers (UUID-based)
  - Installment month tracking
  - **Bulk payment import** via Excel
  - **PDF receipt generation** using WeasyPrint
  - **Outstanding balance reports** with Excel export
  - **Payment reports** with date range and category filters
  - Accountant dashboard with income summaries and charts
  - Automated fee reminder emails
- **URLs:** `/finance/`

---

### 5. `staff` — Staff & Teacher Management
**Purpose:** Manages teachers, other staff, salary payments, and user accounts.

- **Models:** `Teacher`, `OtherStaff`, `SalaryPayment` (using GenericForeignKey)
- **Key Features:**
  - Teacher profiles with subject and class assignments
  - Other staff profiles with department and role (HR, IT, Finance, Admin, Support)
  - Salary payment tracking per month (with base salary updates)
  - CV and certificate file uploads
  - **User management:** Create, list, search, activate/deactivate users
  - **Password reset** functionality
  - **Group assignment** (Parent, Teacher, Admin, Owner, Accountant)
- **URLs:** `/teachers/`

---

### 6. `behavior` — Behavior & Achievements
**Purpose:** Tracks student behavior records and achievements.

- **Models:** `BehaviorRecord`, `Achievement`
- **Key Features:**
  - Positive and negative behavior records with descriptions
  - Action tracking and resolution status
  - Student achievements/awards with dates
  - Teacher-scoped filtering
  - Academic year filtering
- **URLs:** `/behavior/`

---

### 7. `locations` — Geographic Regions
**Purpose:** Manages geographic location data for student addresses.

- **Models:** `Region`, `District`
- **Key Features:**
  - Regions (e.g., Dar es Salaam, Arusha)
  - Districts linked to regions
  - Used by the Student model for address information
- **URLs:** (No public views — used as a data dependency)

---

### 8. `dashboard` — Role-Based Dashboards
**Purpose:** Provides customized home pages and views for each user role.

- **Models:** (None — uses data from other apps)
- **Key Features:**
  - **Admin/Owner Dashboard:** Key stats (students, teachers, classes, parents), revenue charts (monthly, by category), class distribution, recent payments & results
  - **Teacher Dashboard:** My classes, student count, today's timetable, recent results, upcoming assignments
  - **Parent Dashboard:** Child selector, academic progress, payments, behavior records, attendance, timetable, achievements
  - **Parent Sub-views:** Progress, Payments, Behavior, Attendance, Timetable, Achievements
  - **Blocked Parent View:** Parents with outstanding balances are restricted
  - **Accountant Dashboard:** Income summaries, outstanding students, payment reports
  - Custom login view with role-based redirects
- **URLs:** `/dashboard/`

---

## User Roles & Permissions

| Role | Description | Access |
|------|-------------|--------|
| **Owner** | Full system access | All areas |
| **Admin** | Full system access | All areas |
| **Teacher** | Manages classes, subjects, results, attendance | Academics, Behavior (scoped) |
| **Accountant** | Manages payments, fees, reports | Finance dashboard |
| **Parent** | Views child's progress, payments, behavior | Parent dashboard (scoped) |

---

## Tech Stack

- **Backend:** Django 6.0+
- **Database:** PostgreSQL (configurable via `.env`)
- **Frontend:** Django Templates with Bootstrap
- **PDF Generation:** WeasyPrint
- **Excel Import/Export:** OpenPyXL, Pandas
- **Email:** Console backend (configurable)

## Quick Start

```bash
# Clone and enter the project
cd behac_school

# Install dependencies
pip install -r requirement.txt

# Configure environment
cp .env.example .env  # Edit as needed

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```
