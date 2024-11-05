from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db
import enum
from sqlalchemy import Enum
from flask_login import UserMixin

    
class Role(enum.Enum):
    USER='user'
    ADMIN='admin'

class ReviewSource(enum.Enum):
    AMAZON='amazon'
    FLIPKART='flipkart'
    
class Sentiment(enum.Enum):
    POSITIVE='positive'
    NEGATIVE='negative'
    NEUTRAL='neutral'

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(Enum(Role), default=Role.USER)
    created_at = db.Column(db.DateTime, default=datetime.now(), index=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    # Flask-Login required properties
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    @property
    def role_name(self):
        return self.role.name if self.role else None

# Product model with ASIN
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(), index=True)
    
    reviews = db.relationship('Review', backref='product', lazy=True)
    sentiment_summary = db.relationship('SentimentSummary', backref='product', uselist=False)
    platforms = db.relationship('ProductPlatform', backref='product', lazy=True)
    # dashboard_data = db.relationship('DashboardData', backref='product', lazy=True)
    
# ProductPlatform to associate a product with one or more platforms
class ProductPlatform(db.Model):
    __tablename__ = 'product_platforms'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    platform = db.Column(Enum(ReviewSource), nullable=False)
    platform_id = db.Column(db.String(16), unique=True, nullable=False)  # ASIN or FSN


# Review model
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    source = db.Column(Enum(ReviewSource), nullable=False)
    sentiment = db.Column(Enum(Sentiment))
    relevance_score = db.Column(db.Float)
    fetched_at = db.Column(db.DateTime, default=datetime.now(), index=True)

# SentimentSummary model
class SentimentSummary(db.Model):
    __tablename__ = 'sentiment_summaries'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    positive_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    word_cloud = db.Column(db.Text)
    
    
    # Helper method to get reviews by sentiment
    def get_reviews_by_sentiment(self, sentiment_value):
        return Review.query.filter_by(product_id=self.product_id, sentiment=sentiment_value).all()



# Notification model for asynchronous notifications
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(), index=True)
    
    
    # # DashboardData model for product and generic dashboard data
# class DashboardData(db.Model):
#     __tablename__ = 'dashboard_data'
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.now(), index=True)
#     avg_sentiment = db.Column(db.Float)
#     review_count = db.Column(db.Integer)
#     positive_ratio = db.Column(db.Float)
#     top_keywords = db.Column(db.String(255))  # Keywords for word cloud representation


# class DashboardData(db.Model):
#     __tablename__ = 'dashboard_data'
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.now())
#     avg_sentiment = db.Column(db.Float)
#     review_count = db.Column(db.Integer)
#     positive_ratio = db.Column(db.Float)
#     top_keywords = db.Column(db.String(255))  # Product-specific keywords for word cloud
    
#     # Fields to support aggregation for overall dashboard
#     global_positive_count = db.Column(db.Integer)
#     global_neutral_count = db.Column(db.Integer)
#     global_negative_count = db.Column(db.Integer)
