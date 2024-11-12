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
    
class Status(enum.Enum):
    PENDING='pending'
    FAILED='failed'
    COMPLETED='completed'

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(Enum(Role), default=Role.USER)
    created_at = db.Column(db.DateTime, default=datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default = datetime.now())
     # Product relationship: One user can have many products
    products = db.relationship('Product', backref='owner', lazy=True)
    #relationship for ScrapingTasks
    scraping_tasks = db.relationship('ScrapingTask', backref='created_by_user', lazy=True)
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
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    reviews = db.relationship('Review', backref='product', lazy=True)
    sentiment_summary = db.relationship('SentimentSummary', backref='product', uselist=False)
    platforms = db.relationship('ProductPlatform', back_populates='product', lazy=True)  # Updated to back_populates for bidirectional relationship

    
# ProductPlatform to associate a product with one or more platforms
class ProductPlatform(db.Model):
    __tablename__ = 'product_platforms'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    platform = db.Column(Enum(ReviewSource), nullable=False)
    platform_id = db.Column(db.String(16), unique=True, nullable=False)  # ASIN or FSN
    
    # Define the relationship to Product with back_populates
    product = db.relationship('Product', back_populates='platforms')

class RawReview(db.Model):
    __tablename__='raw_reviews'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), db.ForeignKey('scraping_tasks.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.String(10), nullable=True)
    body = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(100), nullable=True)
    date = db.Column(db.String(50), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    platform = db.Column(Enum(ReviewSource), nullable=False)  
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    source = db.Column(Enum(ReviewSource), nullable=False)
    sentiment = db.Column(Enum(Sentiment))
    relevance_score = db.Column(db.Float)
    review_date = db.Column(db.String(50), nullable=True)
    author = db.Column(db.String(100), nullable=True)

# SentimentSummary model
class SentimentSummary(db.Model):
    __tablename__ = 'sentiment_summaries'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    platform_id = db.Column(db.String(16), db.ForeignKey('product_platforms.platform_id'), nullable=False)
    platform = db.Column(Enum(ReviewSource), nullable=False)
    positive_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default = 0)
    most_rating = db.Column(db.Float, default = 0)
    word_cloud = db.Column(db.Text)
    words = db.Column(db.JSON, nullable=False, default=list)
    frequency = db.Column(db.JSON, nullable=False, default=list)
    
    
    
    # Helper method to get reviews by sentiment
    def get_reviews_by_sentiment(self, sentiment_value):
        return Review.query.filter_by(product_id=self.product_id, sentiment=sentiment_value).all()



class ScrapingTask(db.Model):
    __tablename__='scraping_tasks'
    id = db.Column(db.String(36), primary_key=True)
    fsn_asin = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    platform = db.Column(Enum(ReviewSource), nullable=False)  # "flipkart" or "amazon"
    status = db.Column(Enum(Status), nullable=False, default=Status.PENDING)  # "pending", "completed", "failed"
    created_at = db.Column(db.DateTime, default=datetime.now())
    message = db.Column(db.String(200), nullable=True)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    

    
    