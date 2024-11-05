:: Activate virtual environment
call minorvenv\Scripts\activate

:: Function to deactivate venv on exit
set "deactivated=0"
setlocal

:: Check if the database exists, and initialize it if it doesn't
if not exist "sentimentScout.db" (
    python init_db.py
)

:: Run the application
python run.py

:: Deactivate virtual environment when exiting
call minorvenv\Scripts\deactivate
echo Deactivated virtual environment.
