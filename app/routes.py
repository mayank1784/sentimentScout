from flask import jsonify, request, abort
from app import app,db, login_manager, bcrypt
from app.models import User, Product, ProductPlatform, Review, SentimentSummary, Notification, ReviewSource
from flask_login import login_user, logout_user, login_required, current_user
from errorHandler import handle_errors

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def get():
    return jsonify({'message':'hello'})

# USER & AUTHENTICATION ROUTES
@app.route('/register', methods=['POST'])
@handle_errors
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Username or email already exists'}), 409
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password_hash=hashed_password, email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
@handle_errors
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    # Check if user exists and verify password
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        remember = data.get('remember', False)
        login_user(user, remember=remember)
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# LOGOUT ROUTE
@app.route('/logout', methods=['POST'])
@login_required
@handle_errors
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


# PRODUCT MANAGEMENT ROUTES
@app.route('/product', methods=['POST'])
@login_required
@handle_errors
def add_or_update_product():
    """
    Adds a new product or updates an existing product in the database.

    If a product ID is provided in the request, the function will attempt to 
    update the existing product. If no product ID is given, it will create a 
    new product. The function checks for existing products by ASIN or FSN 
    to prevent duplicates.

    Request JSON structure:
    {
        "id": <int>,              # Optional: ID of the product to update
        "name": <str>,            # Required: Name of the product
        "description": <str>,     # Required: Description of the product
        "asin": <str>,            # Optional: Amazon Standard Identification Number
        "fsn": <str>              # Optional: Flipkart Standard Number
    }

    Returns:
        - 201: Product added or updated successfully
        - 404: Product not found (for updates)
        - 409: Conflict if a product with the same ASIN or FSN already exists
    """
    data = request.json
    product_id = data.get('id')  # Get product ID for updating if provided

    # Check if the request contains a product ID
    if product_id:
        # Attempt to retrieve the existing product by ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404

        # Update product details
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)

        # Check for existing platforms linked to this product
        existing_platforms = ProductPlatform.query.filter_by(product_id=product_id).all()
        existing_asin = any(p.platform == ReviewSource.AMAZON for p in existing_platforms)
        existing_fsn = any(p.platform == ReviewSource.FLIPKART for p in existing_platforms)

        # Add/update ASIN if FSN already exists
        if 'asin' in data and not existing_asin:
            platform = ProductPlatform(product=product, platform=ReviewSource.AMAZON, platform_id=data['asin'])
            db.session.add(platform)

        # Add/update FSN if ASIN already exists
        if 'fsn' in data and not existing_fsn:
            platform = ProductPlatform(product=product, platform=ReviewSource.FLIPKART, platform_id=data['fsn'])
            db.session.add(platform)

    else:
        # Create a new product if no ID is provided
        product = Product(name=data['name'], description=data['description'])

        # Check for existing products by ASIN or FSN to avoid duplicates
        existing_product_by_asin = ProductPlatform.query.filter_by(platform_id=data.get('asin')).first()
        existing_product_by_fsn = ProductPlatform.query.filter_by(platform_id=data.get('fsn')).first()

        if existing_product_by_asin or existing_product_by_fsn:
            return jsonify({'message': 'Product with the same ASIN or FSN already exists.'}), 409

        # Add the new product to the session
        db.session.add(product)

        # Add platforms (e.g., Amazon ASIN, Flipkart FSN) to the ProductPlatform model
        if 'asin' in data:
            platform = ProductPlatform(product=product, platform=ReviewSource.AMAZON, platform_id=data['asin'])
            db.session.add(platform)
        if 'fsn' in data:
            platform = ProductPlatform(product=product, platform=ReviewSource.FLIPKART, platform_id=data['fsn'])
            db.session.add(platform)

    # Commit changes to the database
    db.session.commit()
    
    # Return success message
    return jsonify({'message': 'Product added or updated successfully'}), 201


# PRODUCT RETRIEVAL ROUTE
@app.route('/product/<int:product_id>', methods=['GET'])
@login_required
@handle_errors
def get_product(product_id):
    """
    Retrieves the details of a specific product by its ID.

    This endpoint fetches the product information including its name, 
    description, creation date, and associated platforms (ASIN/FSN) 
    linked to the product.

    Parameters:
        product_id (int): The ID of the product to retrieve.

    Returns:
        - 200: A JSON object containing the product details.
        - 404: If the product with the specified ID does not exist.
    
    Response JSON structure:
    {
        "id": <int>,                     # The unique ID of the product
        "name": <str>,                   # The name of the product
        "description": <str>,            # The description of the product
        "created_at": <str>,             # The creation timestamp of the product
        "platforms": [                   # List of platforms associated with the product
            {
                "platform": <str>,        # The name of the platform (e.g., Amazon, Flipkart)
                "id": <str>               # The platform-specific identifier (ASIN/FSN)
            },
            ...
        ]
    }
    """
    # Fetch the product by ID or return a 404 error if not found
    product = Product.query.get_or_404(product_id)

    # Return product details as a JSON response
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'created_at': product.created_at,
        'platforms': [
            {
                'platform': platform.platform.name,
                'id': platform.platform_id
            } for platform in product.platforms
        ]
    }), 200

# REVIEW MANAGEMENT ROUTES
# PRODUCT REVIEWS RETRIEVAL ROUTE
@app.route('/product/<int:product_id>/reviews', methods=['GET'])
@login_required
@handle_errors
def get_reviews(product_id):
    """
    Retrieves all reviews associated with a specific product.

    This endpoint fetches all the reviews linked to the given product ID.
    Each review includes its text, source (platform), sentiment, and relevance score.

    Parameters:
        product_id (int): The ID of the product for which to retrieve reviews.

    Returns:
        - 200: A JSON array of reviews for the specified product.
        - 404: If the product with the specified ID does not exist or has no reviews.
    
    Response JSON structure:
    [
        {
            "id": <int>,                     # The unique ID of the review
            "review_text": <str>,            # The text content of the review
            "source": <str>,                  # The name of the source platform (e.g., Amazon, Flipkart)
            "sentiment": <str>,               # The sentiment classification of the review (e.g., Positive, Negative, Neutral)
            "relevance_score": <float>        # The relevance score assigned to the review
        },
        ...
        
    ]
    """
    # Fetch all reviews for the specified product ID
    reviews = Review.query.filter_by(product_id=product_id).all()

    # Return the list of reviews as a JSON response
    return jsonify([
        {
            'id': review.id,
            'review_text': review.review_text,
            'source': review.source.name,
            'sentiment': review.sentiment,
            'relevance_score': review.relevance_score
        } for review in reviews
    ]), 200


@app.route('/product/<int:product_id>/reviews', methods=['POST'])
@login_required
@handle_errors
def add_review(product_id):
    data = request.json
    review = Review(product_id=product_id, review_text=data['review_text'], source=ReviewSource[data['source'].upper()], sentiment=data['sentiment'], relevance_score=data.get('relevance_score', 0))
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review added successfully'}), 201

# SENTIMENT ANALYSIS ROUTES
@app.route('/product/<int:product_id>/analyze', methods=['POST'])
@login_required
@handle_errors
def analyze_sentiment(product_id):
    # Logic to trigger sentiment analysis (fetch reviews, process, and update SentimentSummary)
    product = Product.query.get_or_404(product_id)
    
    # Call ML model to analyze reviews and save results in SentimentSummary
    # Placeholder for analysis logic
    sentiment_summary = SentimentSummary(product=product, positive_count=10, neutral_count=5, negative_count=2, word_cloud="Sample Word Cloud")
    db.session.add(sentiment_summary)
    db.session.commit()
    
    # Send notification to the user about analysis completion
    notification = Notification(user_id=current_user.id, content=f'Sentiment analysis for {product.name} is complete.')
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'message': 'Sentiment analysis triggered and data stored.'}), 200

# NOTIFICATION MANAGEMENT ROUTES
@app.route('/notifications', methods=['GET'])
@login_required
@handle_errors
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'id': notification.id, 'content': notification.content, 'is_read': notification.is_read, 'timestamp': notification.timestamp} for notification in notifications]), 200

@app.route('/notifications/<int:notification_id>/mark_read', methods=['POST'])
@login_required
@handle_errors
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)  # Forbidden access
    
    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200

# DASHBOARD DATA ROUTES

# Product-specific dashboard data (providing analysis data for a single product)
@app.route('/product/<int:product_id>/dashboard', methods=['GET'])
@login_required
@handle_errors
def product_dashboard(product_id):
    sentiment_summary = SentimentSummary.query.filter_by(product_id=product_id).first()
    reviews = Review.query.filter_by(product_id=product_id).all()
    positive_reviews = [review for review in reviews if review.sentiment == 'positive']
    neutral_reviews = [review for review in reviews if review.sentiment == 'neutral']
    negative_reviews = [review for review in reviews if review.sentiment == 'negative']

    return jsonify({
        'positive_count': sentiment_summary.positive_count,
        'neutral_count': sentiment_summary.neutral_count,
        'negative_count': sentiment_summary.negative_count,
        'word_cloud': sentiment_summary.word_cloud,
        'reviews': {
            'positive': [{'id': review.id, 'review_text': review.review_text} for review in positive_reviews],
            'neutral': [{'id': review.id, 'review_text': review.review_text} for review in neutral_reviews],
            'negative': [{'id': review.id, 'review_text': review.review_text} for review in negative_reviews]
        }
    }), 200

# Generic dashboard data (providing aggregated sentiment data for all products)
@app.route('/dashboard/overview', methods=['GET'])
@login_required
@handle_errors
def generic_dashboard():
    products = Product.query.all()
    product_summaries = []
    
    for product in products:
        sentiment_summary = SentimentSummary.query.filter_by(product_id=product.id).first()
        if sentiment_summary:
            product_summaries.append({
                'product_id': product.id,
                'name': product.name,
                'positive_count': sentiment_summary.positive_count,
                'neutral_count': sentiment_summary.neutral_count,
                'negative_count': sentiment_summary.negative_count
            })
            
    return jsonify({'products': product_summaries}), 200