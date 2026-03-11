# The Travelling Therapist

## Quick Overview

The application will need the following:
- **Backend:** Python 3.9> <3.12 , Django 4.0.4
- **Database:** MySQL (Production)
- **Frontend:** Django Templates with Bootstrap 4


## Installation and Setup Process

To run this project locally, follow these steps:

### 1. Clone the repository
Clone the codebase and navigate into the project directory:
```bash
git clone <repository-url>
cd The_Travelling_Therapist
```

### 2. Set up the Virtual Environment

```bash
# Create the virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```
### 4. Now, make the migrations for the database:
```bash
py manage.py makemigrations
```

### 5. And commit them using:

```bash
py manage.py migrate
```
​The project should be working now, but there are still some missing things.


### 6. Create a Superuser
To access the Django Admin panel:
```bash
python manage.py createsuperuser
```

### 7. Seed Admin Settings
Initial admin settings (like email sending and auction limits) must be set for the site to function correctly. Run the provided script:
```bash
python seed_admin_settings.py
```
This initializes:
- **Send Emails:** Enabled (TRUE)
- **Max Active Listings:** 1
- **Default Listing Length:** 3600 seconds (1 hour)

### 8. Run the Development Server
Start the local server:
```bash
python manage.py runserver
```
Alternatively, on Windows, you can use the provided batch file (ensure the virtual environment path inside the `.bat` file aligns with your structure):
```bash
runserver.bat
```

Access the site at `http://127.0.0.1:8000/`.
