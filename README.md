# HabitFlow

HabitFlow is a Django-based habit tracker designed to help users build and maintain positive habits. This application is a practical tool, demonstrating skills in Django, Bootstrap, and modern web application design.

## Features

### **User Authentication**
- Secure user registration and login with custom forms.
- Authentication features provided using Django's built-in tools.

### **Habit Management**
- Create, edit, and delete habits with detailed attributes:
  - **Name:** A unique name for each habit.
  - **Description:** A brief overview of the habit.
  - **Frequency:** Specify habit recurrence (daily, weekly, monthly, custom).
  - **Difficulty:** Classify habits as easy, medium, or hard.

### **Progress Tracking**
- Intuitive dashboard to:
  - View active habits.
  - Mark daily progress with statuses:
    - **Missed**
    - **Skipped**
    - **Complete**
  - Add notes and log time spent on habits.

### **Responsive Design**
- Built with Bootstrap for a professional, mobile-friendly user interface.

## Technology Stack

### **Backend**
- Python (Django framework)

### **Frontend**
- HTML5, CSS3, Bootstrap 5
- JavaScript for interactivity

### **Database**
- SQLite (default database for Django development)

### **Containerization**
- Fully containerized using Docker and available on [DockerHub](https://hub.docker.com/repository/docker/yudheerrm/habit-flow/).

## Folder Structure

```
habit_tracker/
├── habit_tracker/         # Project settings and configuration
├── tracker/               # Custom Django app for HabitFlow
│   ├── migrations/        # Database migration files
│   ├── templates/         # HTML templates
|     ├── authentication/  # Authentication templates
│   ├── static/            # Static files (CSS, JS, images)
│   ├── forms.py           # Form classes for user input
│   ├── models.py          # Database models
│   ├── views.py           # Logic for rendering templates
│   ├── urls.py            # App-specific routes
├── manage.py              # Django management script
├── Dockerfile             # Docker configuration file
```

## Setup and Installation

### Using Docker(Recommended)
1. Clone the repository:
   ```bash
   git clone https://github.com/YudheerRM/Habit-Flow.git
   cd Habit-Flow
   ```

2. Build the Docker image:
   ```bash
   docker build -t habitflow .
   ```

3. Run the Docker container:
   ```bash
   docker run -p 8000:8000 habitflow
   ```

4. Access the application at `http://127.0.0.1:8000/`.

### Manual Setup (Without Docker)
1. Clone the repository:
   ```bash
   git clone https://github.com/YudheerRM/Habit-Flow.git
   cd Habit-Flow
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations to set up the database:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000/`.

## Future Plans

- **Gamification:** Add streak tracking and reward systems for habit consistency.
- **Visualization:** Incorporate charts and graphs to display habit progress.
- **Notifications:** Email or in-app reminders for habits.
