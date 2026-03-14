from flask import Flask
# Import your actual logic from the app folder
# If your main logic is in app/main.py, use:
from app.main import app as application

# This tells Vercel to use 'app'
app = application 

if __name__ == "__main__":
    app.run()
