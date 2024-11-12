from app import app, db
from app.models import User, Product, ProductPlatform, Review, SentimentSummary

with app.app_context():
    db.create_all()
print("Database initialized.")
