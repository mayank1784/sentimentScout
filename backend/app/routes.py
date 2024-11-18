from flask import jsonify, request, abort
from app import app,db, login_manager, bcrypt
from app.models import User, Product, ProductPlatform, Review, SentimentSummary, ReviewSource, ScrapingTask, RawReview, Sentiment, Status
from flask_login import login_user, logout_user, login_required, current_user
from app.errorHandler import handle_errors
from app.tasks import scrape_flipkart_reviews, scrape_amazon_reviews, preprocess_text, fill_missing_ratings, word_distribution
import threading
import uuid
import re
from datetime import datetime


from sqlalchemy.exc import SQLAlchemyError
import pickle
import pandas as pd
from io import BytesIO
import base64
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom unauthorized handler for Flask-Login
@login_manager.unauthorized_handler
def unauthorized_callback():
    """
    This handler is triggered when an unauthorized user attempts to access a route
    decorated with `@login_required`. It returns a JSON response with a 401 status code.

    Returns:
        JSON response with an error message and a 401 status code.
    """
    return jsonify({"message": "User not authenticated"}), 401

@app.route('/')
def get():
    return jsonify({'message':'Welcome to Sentiment Scout Backend API'}), 200

# USER & AUTHENTICATION ROUTES
@app.route('/register', methods=['POST'])
@handle_errors
def register():
    """
    Registers a new user by creating an account with a unique username and email.

    This route accepts a POST request to register a new user. It checks if the provided username or email 
    already exists in the database, and if not, it hashes the user's password and stores the user information 
    securely in the database.

    Args:
        None (data is passed in the request body).

    Request Body (JSON):
        - `username`: The desired username for the new user (string).
        - `email`: The email address of the new user (string).
        - `password`: The password for the new user (string).

    Returns:
        Response (JSON):
            - `message`: A success message if the user is registered successfully, or an error message if the username 
              or email already exists in the system.

    Error Responses:
        - 409: If the username or email already exists in the database.
            - Example: `{"message": "Username or email already exists"}`.
        - 400: If the request body is missing required fields (username, email, or password).
        - 500: Internal server error if something goes wrong during the registration process.

    Example:
        POST /register

        Request Body:
        {
            "username": "new_user",
            "email": "user@example.com",
            "password": "securepassword123"
        }

        Response (on success):
        {
            "message": "User registered successfully"
        }

        Response (on error - username/email exists):
        {
            "message": "Username or email already exists"
        }
    """
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
    """
    Authenticates a user by verifying their username and password.

    This route accepts a POST request to log in a user. It checks if the provided username exists in the database,
    and if so, it verifies the password using bcrypt hashing. If the credentials are valid, the user is logged in 
    and a session is created.

    Args:
        None (data is passed in the request body).

    Request Body (JSON):
        - `username`: The username of the user attempting to log in (string).
        - `password`: The password provided by the user (string).
        - `remember`: A boolean flag indicating whether the session should be remembered (optional, defaults to False).

    Returns:
        Response (JSON):
            - `message`: A success message if the login is successful, or an error message if the username or password 
              is invalid.
            - `user_id`: The ID of the user if the login is successful.

    Error Responses:
        - 401: If the username or password is invalid.
            - Example: `{"message": "Invalid username or password"}`.
        - 400: If the request body is missing required fields (username or password).
        - 500: Internal server error if something goes wrong during the login process.

    Example:
        POST /login

        Request Body:
        {
            "username": "existing_user",
            "password": "securepassword123",
            "remember": true
        }

        Response (on success):
        {
            "message": "Login successful",
            "user_id": 123
        }

        Response (on error - invalid credentials):
        {
            "message": "Invalid username or password"
        }
    """
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
    """
    Logs out the currently authenticated user.

    This route accepts a POST request to log out a user by terminating their session. The user is logged out only if 
    they are authenticated (i.e., they are currently logged in). Once logged out, the session is cleared, and the 
    user will no longer be authenticated for future requests until they log in again.

    Args:
        None (No request body is required).

    Returns:
        Response (JSON):
            - `message`: A success message indicating that the user has been logged out.

    Error Responses:
        - 401: If the user is not logged in (not authenticated).
            - Example: `{"message": "User not authenticated"}`.
        - 500: Internal server error if something goes wrong during the logout process.

    Example:
        POST /logout

        Response (on success):
        {
            "message": "Logout successful"
        }

        Response (on error - user not authenticated):
        {
            "message": "User not authenticated"
        }
    """
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

# UPDATE EMAIL ROUTE
@app.route('/update_email', methods=['PUT'])
@login_required
@handle_errors
def update_email():
    """
    Updates the user's email address after verifying the current password.

    Request Body (JSON):
        - `new_email`: The new email address (string).
        - `password`: The current password for verification (string).

    Returns:
        Response (JSON):
            - `message`: Success message if email is updated, or an error message if password is incorrect.

    Error Responses:
        - 400: If the request body is missing required fields.
        - 401: If the provided password is incorrect.
        - 409: If the new email is already taken by another user.
    """
    data = request.json
    new_email = data.get('new_email')
    password = data.get('password')

    if not new_email or not password:
        return jsonify({'message': 'New email and password are required'}), 400

    # Verify password
    if not bcrypt.check_password_hash(current_user.password_hash, password):
        return jsonify({'message': 'Incorrect password'}), 401

    # Check if new email is already in use
    if User.query.filter_by(email=new_email).first():
        return jsonify({'message': 'Email is already in use'}), 409

    # Update email
    current_user.email = new_email
    current_user.updated_at = datetime.now()
    db.session.commit()

    return jsonify({'message': 'Email updated successfully'}), 200


# UPDATE PASSWORD ROUTE
@app.route('/update_password', methods=['PUT'])
@login_required
@handle_errors
def update_password():
    """
    Updates the user's password after verifying the current password.

    Request Body (JSON):
        - `current_password`: The current password for verification (string).
        - `new_password`: The new password to set (string).

    Returns:
        Response (JSON):
            - `message`: Success message if password is updated, or an error message if the current password is incorrect.

    Error Responses:
        - 400: If the request body is missing required fields.
        - 401: If the provided current password is incorrect.
    """
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'message': 'Current and new password are required'}), 400

    # Verify current password
    if not bcrypt.check_password_hash(current_user.password_hash, current_password):
        return jsonify({'message': 'Incorrect current password'}), 401

    # Update password
    current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    current_user.updated_at = datetime.now()
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200


# PRODUCT ADDITION/UPDATION ROUTE
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
        "image: <st>,             # Optional: Image link of the product
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

        # Ensure the product belongs to the logged-in user
        if product.created_by != current_user.id:
            return jsonify({'message': 'You are not authorized to update this product'}), 403

        # Update product details
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.image = data.get('image',product.image)

        #Check for existing platforms linked to this product using the backref
        existing_asin = any(p.platform == ReviewSource.AMAZON for p in product.platforms)
        existing_fsn = any(p.platform == ReviewSource.FLIPKART for p in product.platforms)


        # Add/update ASIN if FSN already exists
        if 'asin' in data and not existing_asin:
            platform = ProductPlatform(product=product, platform=ReviewSource.AMAZON, platform_id=str(data['asin']).upper())
            db.session.add(platform)
            sentiment_summary = SentimentSummary.query.filter_by(platform_id=str(data['asin']).upper()).first()
            if sentiment_summary:
                sentiment_summary.platform_id = str(data.get('asin')).upper()
                db.session.add(sentiment_summary)

        # Add/update FSN if ASIN already exists
        if 'fsn' in data and not existing_fsn:
            platform = ProductPlatform(product=product, platform=ReviewSource.FLIPKART, platform_id=str(data['fsn']).upper())
            db.session.add(platform)
            sentiment_summary = SentimentSummary.query.filter_by(platform_id=str(data['fsn']).upper()).first()
            if sentiment_summary:
                sentiment_summary.platform_id = str(data.get('fsn')).upper()
                db.session.add(sentiment_summary)

    else:
        # Create a new product if no ID is provided
        product = Product(
            name=data['name'], 
            description=data['description'], 
            created_by=current_user.id  # Associate product with logged-in user
        )
        if data['image']:
            product.image = data['image']

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



# USER'S ALL PRODUCT RETRIEVAL ROUTE
@app.route('/products', methods=['GET'])
@login_required
@handle_errors
def get_user_products():
    """
    Retrieves all products belonging to the logged-in user.

    Returns:
        - 200: A JSON object containing the list of products owned by the user.
        - 404: If no products are found for the logged-in user.

    Response JSON structure:
    {
        "products": [
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
        ]
    }
    """
    # Fetch all products for the logged-in user
    products = Product.query.filter_by(created_by=current_user.id).all()

    # If no products exist, return a 404 error
    if not products:
        return jsonify({"message": "No products found for the logged-in user."}), 404

    # Return product list details as a JSON response
    return jsonify({
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'created_at': product.created_at.isoformat(),
                'platforms': [
                    {
                        'platform': platform.platform.name,
                        'id': platform.platform_id
                    } for platform in product.platforms
                ]
            } for product in products
        ]
    }), 200


# SINGLE PRODUCT RETRIEVAL ROUTE
@app.route('/product/<int:product_id>', methods=['GET'])
@login_required
@handle_errors
def get_user_product(product_id):
    """
    Retrieves the details of a specific product by its ID that belongs to the logged-in user.

    Parameters:
        product_id (int): The ID of the product to retrieve.

    Returns:
        - 200: A JSON object containing the product details.
        - 404: If the product with the specified ID does not exist or does not belong to the logged-in user.
    
    Response JSON structure:
    {
        "id": <int>,                     # The unique ID of the product
        "name": <str>,                   # The name of the product
        "description": <str>,            # The description of the product
        "created_at": <str>,             # The creation timestamp of the product
        "image": <str>,                  # Image of Product
        "platforms": [                   # List of platforms associated with the product
            {
                "platform": <str>,        # The name of the platform (e.g., Amazon, Flipkart)
                "id": <str>               # The platform-specific identifier (ASIN/FSN)
            },
            ...
        ]
        
    }
    """
    # Fetch the product by ID that belongs to the logged-in user
    product = Product.query.filter_by(id=product_id, created_by=current_user.id).first()

    # If no such product exists, return a 404 error
    if not product:
        return jsonify({"message": "Product not found or does not belong to the logged-in user."}), 404

    # Return product details as a JSON response
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'image': product.image,
        'created_at': product.created_at.isoformat(),
        'platforms': [
            {
                'platform': platform.platform.name,
                'id': platform.platform_id
            } for platform in product.platforms
        ]
    }), 200


# PRODUCT DELETION ROUTE
@app.route('/product/<int:product_id>', methods=['DELETE'])
@login_required
@handle_errors
def delete_product(product_id):
    """
    Deletes a product and its associated records (platforms, reviews, sentiment summary, raw reviews).

    The route will first ensure the product exists, and if it does, it will delete the product 
    along with the related platforms, reviews, sentiment summary, and raw reviews from the database.

    Args:
        product_id (int): The ID of the product to delete.

    Returns:
        - 200: Product and associated records deleted successfully
        - 404: Product not found
    """
    # Fetch the product to be deleted
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    # Check if the current user is the one who created the product
    if product.created_by != current_user.id:
        return jsonify({'message': 'You do not have permission to delete this product'}), 403

    # Deleting associated records
    # Delete associated reviews, raw reviews, and sentiment summaries
    db.session.query(Review).filter(Review.product_id == product_id).delete()
    db.session.query(SentimentSummary).filter(SentimentSummary.product_id == product_id).delete()
    db.session.query(RawReview).filter(RawReview.product_id == product_id).delete()
    db.session.query(ScrapingTask).filter(ScrapingTask.product_id == product_id).delete()

    # Delete associated product platforms (ASIN/FSN links)
    db.session.query(ProductPlatform).filter(ProductPlatform.product_id == product_id).delete()

    # Now delete the product itself
    db.session.delete(product)

    # Commit all changes to the database
    db.session.commit()

    # Return success message
    return jsonify({'message': 'Product and all associated records deleted successfully'}), 200


# REVIEW MANAGEMENT ROUTES

# PRODUCT REVIEWS RETRIEVAL ROUTE
@app.route('/product/<int:product_id>/reviews', methods=['GET'])
@login_required
@handle_errors
def get_reviews(product_id):
    """
    Retrieves all reviews associated with a specific product.

    This endpoint fetches all the reviews linked to the given product ID.
    Each review includes its text, source (platform), sentiment, and relevance score, review date and author.
    If no processed reviews are found, it checks for raw reviews and prompts the user to analyze them.

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
        "rating": <int>,                 # The rating given by the reviewer
        "source": <str>,                 # The name of the source platform (e.g., Amazon, Flipkart)
        "sentiment": <str>,              # The sentiment classification of the review (e.g., Positive, Negative, Neutral)
        "relevance_score": <float>,      # The relevance score assigned to the review
        "review_date": <str>,            # The date when the review was posted (string)
        "author": <str>                  # The author of the review (optional)
    },
    ...
    ]
    """
    # Fetch the product by its ID to ensure it exists
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Fetch all processed reviews for the specified product ID
    reviews = Review.query.filter_by(product_id=product_id).all()

    # Check if no processed reviews exist
    if not reviews:
        # Check if there are raw reviews for the product
        raw_reviews = RawReview.query.filter_by(product_id=product_id).all()

        if raw_reviews:
            return jsonify({'message': 'No processed reviews found. Please analyze the raw reviews to generate processed reviews.'}), 404
        else:
            return jsonify({'message': 'No reviews found for this product. Try Scraping and analysing'}), 404

    # Return the list of processed reviews as a JSON response
    return jsonify([
        {
            'id': review.id,
            'review_text': review.review_text,
            'rating': review.rating,
            'source': review.source.name,  # Assuming source is an Enum or has a name field
            'sentiment': review.sentiment.name,
            'relevance_score': review.relevance_score,
            'review_date': review.review_date,
            'author': review.author
        } for review in reviews
    ]), 200



# FLIPKART REVIEWS SCRAPING
@app.route('/scrape_flipkart_reviews/<string:fsn>', methods=['POST'])
@login_required
@handle_errors
def scrape_flipkart_reviews_route(fsn):
    """
    Scrapes Flipkart reviews for a specific product identified by FSN (Flipkart Seller Number).
    
    This endpoint validates the provided FSN, checks if the product exists and belongs to the 
    current user, and ensures that no other scraping task is already in progress for the same FSN.
    If valid, it triggers a scraping task in a separate thread to fetch reviews from Flipkart.

    Parameters:
    - fsn (str): The FSN (Flipkart Seller Number) associated with the product. It must be a 
      16-character alphanumeric string.

    Responses:
    - 400 Bad Request: If FSN is not provided or is invalid.
    - 404 Not Found: If the product associated with the FSN does not exist or is not linked to 
      the current user.
    - 403 Forbidden: If the FSN is already attached to another user's product.
    - 409 Conflict: If there is an ongoing scraping task for the same FSN.
    - 202 Accepted: If the scraping task is successfully initiated. Returns the task ID and a 
      message indicating that the scraping has started.

    Example Responses:
    - If FSN is not valid:
      {
        "error": "FSN is not valid"
      }

    - If product is not found:
      {
        "error": "Product with ASIN <fsn> not found. Kindly add product first"
      }

    - If scraping task is already in progress:
      {
        "error": "Already scraping for this ASIN",
        "task": {
          "task_id": "unique-task-id",
          "fsn_asin": "FSN_VALUE",
          "platform": "flipkart",
          "status": "PENDING",
          "message": "Scraping task is pending",
          "created_at": "2024-11-08T12:34:56"
        }
      }

    - If task is successfully initiated:
      {
        "task_id": "unique-task-id",
        "message": "Scraping started"
      }

    The function utilizes threading to perform the scraping task asynchronously, ensuring that 
    the API responds quickly without waiting for the scraping process to complete.

    """
    fsn_pattern = r'^[A-Z0-9]{16}$'
    if not fsn:
        return jsonify({'error': 'FSN is required'}), 400
    if not re.fullmatch(fsn_pattern, str(fsn).upper()):
        return jsonify({'error': 'FSN is not valid'}), 400
    product = ProductPlatform.query.filter_by(platform_id=str(fsn).upper()).first()
     # If product is not found, return an error response
    if not product:
        return jsonify({'error': f'Product with FSN {fsn} not found. Kindly add product first'}), 404
    if product.product.created_by != current_user.id:
        return jsonify({'error':"FSN already attached with other user's product"}), 403
    
    existing_task = ScrapingTask.query.filter_by(fsn_asin=str(fsn).upper(), status = Status.PENDING).first()
    if existing_task:
        return jsonify({
            'error': 'Already scraping for this FSN',
            'task': {
                'task_id': existing_task.id,
                'fsn_asin': existing_task.fsn_asin,
                'platform': existing_task.platform.name,  #  platform is an Enum
                'status': existing_task.status.name,  #  status is an Enum
                'message': existing_task.message,
                'created_at': existing_task.created_at.isoformat(),  # Format datetime as string
            }
        }), 409
    task_id = str(uuid.uuid4())
    product_id = product.product_id
    task_thread = threading.Thread(target=scrape_flipkart_reviews, args=(str(fsn).upper(),task_id,product_id), kwargs={'created_by': current_user.id})
    task_thread.start()
    return jsonify({"task_id": task_id, "message": "Scraping started"}), 202

# AMAZON REVIEWS SCRAPING
@app.route('/scrape_amazon_reviews/<string:asin>', methods=['POST'])
@login_required
@handle_errors
def scrape_amazon_reviews_route(asin):
    """
    Scrapes Amazon reviews for a specific product identified by ASIN (Amazon Standard Identification Number).
    
    This endpoint validates the provided ASIN, checks if the product exists and belongs to the 
    current user, and ensures that no other scraping task is already in progress for the same ASIN.
    If valid, it triggers a scraping task in a separate thread to fetch reviews from Amazon.

    Parameters:
    - asin (str): The ASIN (Amazon Standard Identification Number) associated with the product. It must be a 
      10-character alphanumeric string.

    Responses:
    - 400 Bad Request: If ASIN is not provided or is invalid.
    - 404 Not Found: If the product associated with the ASIN does not exist or is not linked to 
      the current user.
    - 403 Forbidden: If the ASIN is already attached to another user's product.
    - 409 Conflict: If there is an ongoing scraping task for the same ASIN.
    - 202 Accepted: If the scraping task is successfully initiated. Returns the task ID and a 
      message indicating that the scraping has started.

    Example Responses:
    - If ASIN is not valid:
      {
        "error": "ASIN is not valid"
      }

    - If product is not found:
      {
        "error": "Product with ASIN <asin> not found. Kindly add the product first."
      }

    - If ASIN is already attached to another user's product:
      {
        "error": "ASIN already attached with other user's product"
      }

    - If scraping task is already in progress:
      {
        "error": "Already scraping for this ASIN",
        "task": {
          "task_id": "unique-task-id",
          "fsn_asin": "ASIN_VALUE",
          "platform": "amazon",
          "status": "PENDING",
          "message": "Scraping task is pending",
          "created_at": "2024-11-08T12:34:56"
        }
      }

    - If task is successfully initiated:
      {
        "task_id": "unique-task-id",
        "message": "Scraping started"
      }

    The function utilizes threading to perform the scraping task asynchronously, ensuring that 
    the API responds quickly without waiting for the scraping process to complete.

    """
    asin_pattern = r'^[A-Z0-9]{10}$'
    if not asin:
        return jsonify({'error': 'ASIN is required'}), 400
    if not re.fullmatch(asin_pattern, str(asin).upper()):
        return jsonify({'error': 'ASIN is not valid'}), 400
    # Look for the product by ASIN
    product = ProductPlatform.query.filter_by(platform_id=str(asin).upper()).first()
    if not product:
        return jsonify({'error': f'Product with ASIN {asin} not found. Kindly add the product first.'}), 404
    if product.product.created_by != current_user.id:
        return jsonify({'error':"Asin already attached with other user's product"}), 403
    
    existing_task = ScrapingTask.query.filter_by(fsn_asin=str(asin).upper(), status = Status.PENDING).first()
    if existing_task:
        return jsonify({
            'error': 'Already scraping for this ASIN',
            'task': {
                'task_id': existing_task.id,
                'fsn_asin': existing_task.fsn_asin,
                'platform': existing_task.platform.name,  #  platform is an Enum
                'status': existing_task.status.name,  #  status is an Enum
                'message': existing_task.message,
                'created_at': existing_task.created_at.isoformat(),  # Format datetime as string
            }
        }), 409
    task_id = str(uuid.uuid4())
    product_id = product.product_id
    task_thread = threading.Thread(target=scrape_amazon_reviews, args=(str(asin).upper(),task_id, product_id),kwargs={'created_by': current_user.id})
    task_thread.start()
    return jsonify({"task_id": task_id, "message": "Scraping started"}), 202

# GET SCRAPING STATUS
@app.route('/scraping_task_status/<string:task_id>', methods=['GET'])
@login_required
@handle_errors
def check_task_status(task_id):
    """
    Retrieves the status of a scraping task along with the reviews fetched during the task. 
    
    This endpoint allows the user to check the status of a scraping task that was initiated for a 
    specific product. The status includes whether the scraping task is still in progress, completed, 
    or encountered an error. It also returns the reviews associated with the task.

    Parameters:
    - task_id (str): The unique identifier of the scraping task. It is required to fetch the task details 
      and associated reviews.

    Responses:
    - 404 Not Found: If the task with the specified task ID does not exist.
    - 403 Forbidden: If the current user is not the one who created the task and tries to view the status.
    - 200 OK: If the task exists, and the user is authorized to view it. The response will include:
      - `task_id`: The unique task ID.
      - `status`: The current status of the task (e.g., "PENDING", "COMPLETED", etc.).
      - `message`: Any relevant message regarding the task (e.g., errors, task progress).
      - `reviews`: A list of reviews associated with the task, including each review's title, rating, and body.

    Example Responses:
    - If task is not found:
      {
        "error": "Task not found"
      }

    - If user is not authorized:
      {
        "error": "You are not authorized to view this task's status"
      }

    - If task details and reviews are retrieved successfully:
      {
        "task_id": "unique-task-id",
        "status": "COMPLETED",
        "message": "Scraping completed successfully",
        "reviews": [
          {
            "title": "Great product",
            "rating": 5,
            "body": "I love this product. It exceeded my expectations."
          },
          {
            "title": "Not as expected",
            "rating": 2,
            "body": "The product did not meet my expectations. Quality is poor."
          }
        ]
      }

    This function checks if the current user is the one who created the task and only allows them 
    to view the status. It provides the reviews fetched during the scraping task, if any, to the user.

    """
    # Fetch the task using the task_id
    task = ScrapingTask.query.get(task_id)

    # If the task does not exist, return a 404 error
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Check if the current user is the one who created the task
    if task.created_by != current_user.id:
        return jsonify({"error": "You are not authorized to view this task's status"}), 403

    # Fetch the reviews associated with the task
    reviews = RawReview.query.filter_by(task_id=task_id).all()
    reviews_data = [{"title": review.title, "rating": review.rating, "body": review.body} for review in reviews]

    # Return the task status along with the reviews
    return jsonify({
        "task_id": task.id,
        "status": task.status.value,
        "message": task.message,
        "reviews": reviews_data
    }),200
    

# GET SCRAPING TASKS OF A USER
@app.route('/user_tasks', methods=['GET'])
@login_required
@handle_errors
def get_user_tasks():
    """
    Retrieves all tasks associated with the current user, optionally filtered by status, platform, and product_id.

    Query Parameters:
        - status (str, optional): The status to filter tasks by ('PENDING', 'FAILED', 'COMPLETED').
        - platform (str, optional): The platform to filter tasks by ('flipkart', 'amazon').
        - product_id (str, optional): The product ID to filter tasks by.

    Returns:
        - 200: A JSON array of tasks for the current user, filtered by status, platform, and product_id if provided.
        - 400: If an invalid status or platform is provided.

    Response JSON structure:
    [
        {
            "id": <str>,                 # The unique ID of the task
            "fsn_asin": <str>,           # The FSN or ASIN for which the task was created
            "platform": <str>,           # The platform ('flipkart' or 'amazon')
            "status": <str>,             # The status of the task ('PENDING', 'COMPLETED', 'FAILED')
            "created_at": <str>,         # Creation timestamp of the task
            "message": <str>             # Message or details related to the task
        },
        ...
    ]
    """
    # Get the query parameters
    status = request.args.get('status')
    platform = request.args.get('platform')
    product_id = request.args.get('product_id')

    # Validate and convert status to match the database format
    if status:
        status_upper = status.upper()
        try:
            status_enum = Status[status_upper]  # Using Status enum to validate
        except KeyError:
            return jsonify({"error": f"Invalid status '{status}'. Valid statuses are 'PENDING', 'FAILED', 'COMPLETED'."}), 400
        # Start the query with status filter
        tasks_query = ScrapingTask.query.filter_by(created_by=current_user.id, status=status_enum)
    else:
        # Start the query with just the user ID if no status is specified
        tasks_query = ScrapingTask.query.filter_by(created_by=current_user.id)

    # Filter by platform if provided
    if platform:
        platform_upper = platform.lower()
        if platform_upper not in ['flipkart', 'amazon']:
            return jsonify({"error": f"Invalid platform '{platform}'. Valid platforms are 'flipkart' and 'amazon'."}), 400
        tasks_query = tasks_query.filter_by(platform=ReviewSource[platform_upper.upper()])

    # Filter by product_id if provided
    if product_id:
        tasks_query = tasks_query.filter_by(product_id=product_id)

    # Fetch the tasks based on the combined filters
    tasks = tasks_query.all()

    # Structure the response data
    tasks_data = [
        {
            "id": task.id,
            "fsn_asin": task.fsn_asin,
            "platform": task.platform.value,
            "status": task.status.value,
            "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "message": task.message,
            "product_id": task.product_id
        }
        for task in tasks
    ]

    return jsonify(tasks_data), 200



# SENTIMENT ANALYSER API    
@app.route('/reviews/analyse/<int:product_id>', methods=['POST'])
@login_required
@handle_errors
def classify_multiple_reviews(product_id):
    """
    Classifies the sentiment of reviews for a given product and generates sentiment analysis 
    data including a word cloud and frequency distribution. The reviews are classified based on 
    the sentiment model provided, and the sentiment for each review is stored in the database. 
    Additionally, a sentiment summary and word cloud are generated for the product.

    Parameters:
    - product_id (int): The unique identifier of the product whose reviews are to be analyzed.

    Request Arguments:
    - model_name (str): The name of the sentiment model to be used for classification. Defaults to 'svm'.
    - platform (str): The platform from which reviews are being analyzed. Should be 'amazon' or 'flipkart'. 

    Responses:
    - 400 Bad Request: If the platform is invalid or if the platform ID is not found for the product.
    - 404 Not Found: If no reviews are found for the specified product on the selected platform or if the model is not found.
    - 500 Internal Server Error: In case of any database or unexpected errors.
    - 200 OK: If reviews are successfully classified, sentiment summary and word cloud are generated and stored.
      The response includes:
      - `message`: A message indicating that the reviews were successfully processed.
      - `positive_reviews`: The number of positive reviews.
      - `negative_reviews`: The number of negative reviews.
      - `neutral_reviews`: The number of neutral reviews.
      - `bar_data`: Frequency distribution of words in the reviews.

    Example Responses:
    - On success:
      {
        "message": "Reviews successfully classified and stored/updated, sentiment summary generated/updated.",
        "positive_reviews": 120,
        "negative_reviews": 30,
        "neutral_reviews": 50,
        "bar_data": {
          "features": ["excellent", "good", "poor"],
          "frequency": [50, 60, 10]
        }
      }

    - If the platform is invalid:
      {
        "error": "Invalid platform. Choose either 'amazon' or 'flipkart'."
      }

    - If no reviews found for the given product:
      {
        "error": "No reviews found for the given product on amazon. Kindly first scrape the reviews to proceed"
      }

    Description:
    This function performs the following operations:
    - Validates and processes the request parameters including the platform and model.
    - Fetches reviews from the database for the given product and platform.
    - Loads the sentiment model and vectorizer for text classification.
    - Processes each review by combining the review text and description, and applying text preprocessing.
    - Classifies the sentiment of each review and updates or creates the sentiment summary and individual reviews in the database.
    - Generates a word cloud based on the reviews for the selected platform, and returns it as a base64-encoded image.
    - Provides a frequency distribution of the most common words used in the reviews.

    The word cloud is generated with platform-specific masks, such as Amazon or Flipkart logos. The function returns the sentiment classification data, including the number of positive, negative, and neutral reviews, along with a bar graph of the word frequency distribution.

    The sentiment of each review is classified as 'Positive', 'Negative', or 'Neutral', and stored in the database along with other review details.
    """
    try:
        # Extract model_name and platform from request arguments
        model_name = request.args.get('model_name', 'svm')  # Default model is 'svm'
        platform = request.args.get('platform', '').lower()
        platform_enum = ReviewSource.AMAZON if platform == 'amazon' else ReviewSource.FLIPKART
        # Validate platform
        if platform not in ['amazon', 'flipkart']:
            return jsonify({"error": "Invalid platform. Choose either 'amazon' or 'flipkart'."}), 400
        
        # Fetch the platform ID for the product
        platform_id = ProductPlatform.query.filter_by(product_id=product_id, platform=platform_enum).first().platform_id
        if not platform_id:
            return jsonify({"error": "Platform ID not found for the given product."}), 404
        
        # Fetch reviews for the specified platform
       
        reviews = RawReview.query.filter_by(product_id=product_id, platform=platform_enum).all()
        if not reviews:
            return jsonify({"error": f"No reviews found for the given product on {platform}. Kindly first scrape the reviews to proceed"}), 404

        # Load the model and vectorizer
        with open("models.p", 'rb') as mod:
            model_data = pickle.load(mod)
        vect = model_data['vectorizer']
        model = model_data.get(model_name)
        if not model:
            return jsonify({"error": f"Model '{model_name}' not found."}), 404

        # Prepare the reviews data for processing
        rev_data = [
            {
                "review_id": review.id,
                "review_text": review.title,
                "review_desc": review.body,
                "rating": review.rating,
                'date': review.date,
                'author': review.author
            }
            for review in reviews
        ]
        data = pd.DataFrame(rev_data)
        fill_missing_ratings(data)
        data["overall_review"] = data["review_text"] + " " + data["review_desc"]
        data['processed_review'] = data["overall_review"].apply(preprocess_text)

        # Perform sentiment analysis
        count_positive, count_negative, count_neutral = 0, 0, 0
        sentiments = []
        for review_text in data['processed_review']:
            review_vector = vect.transform([review_text])
            res = model.predict(review_vector)
            sentiments.append(res[0])
            if res[0] == 'Positive':
                count_positive += 1
            elif res[0] == 'Negative':
                count_negative += 1
            else:
                count_neutral += 1
        data["Sentiment"] = sentiments

        # Generate a word cloud with platform-specific mask
        amazon_mask = np.array(Image.open('amazon_PNG4.png')) if platform == 'amazon' else np.array(Image.open('flipkart_PNG4.png'))  # Modify if flipkart mask exists
        wordcloud_data = " ".join(data["processed_review"].astype(str).tolist())
        wordcloud = WordCloud(
            width=300,
            height=200,
            random_state=1,
            background_color='white',
            colormap='Set2',
            collocations=False,
            mask=amazon_mask,
            max_words=100
        ).generate(wordcloud_data)

        # Color and save the word cloud image
        if amazon_mask is not None:
            image_colors = ImageColorGenerator(amazon_mask)
            wordcloud.recolor(color_func=image_colors)
        img_buffer = BytesIO()
        plt.figure(figsize=(6, 6), facecolor="#f6f5f6")
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"{platform.capitalize()} Reviews Word Cloud", fontsize=15)
        plt.savefig(img_buffer, format="png", bbox_inches='tight', pad_inches=0)
        plt.close()
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

        # Prepare frequency bar data
        bar_data = word_distribution(data['processed_review'])

        # Update or create sentiment summary
        sentiment_summary = SentimentSummary.query.filter_by(product_id=product_id, platform_id=platform_id, platform=platform_enum).first()
        if sentiment_summary:
            sentiment_summary.positive_count = count_positive
            sentiment_summary.negative_count = count_negative
            sentiment_summary.neutral_count = count_neutral
            sentiment_summary.word_cloud = img_base64
            sentiment_summary.words = bar_data['features']
            sentiment_summary.frequency = bar_data['frequency']
            sentiment_summary.platform = platform_enum
            sentiment_summary.average_rating = data['rating'].mean()
            sentiment_summary.most_rating = data['rating'].mode()[0]
        else:
            sentiment_summary = SentimentSummary(
                product_id=product_id,
                platform_id=platform_id,
                positive_count=count_positive,
                negative_count=count_negative,
                neutral_count=count_neutral,
                word_cloud=img_base64,
                words=bar_data['features'],
                frequency=bar_data['frequency'],
                platform = platform_enum,
                average_rating = data['rating'].mean(),
                most_rating = data['rating'].mode()[0]
            )
            db.session.add(sentiment_summary)

        # Update or add each review's sentiment
        for _, row in data.iterrows():
            sentiment_value = row['Sentiment']
            sentiment_enum = Sentiment[sentiment_value.upper()] if sentiment_value.upper() in Sentiment.__members__ else Sentiment.NEUTRAL
            existing_review = Review.query.filter_by(
                product_id=product_id,
                review_text=row['overall_review'],
                source=platform_enum
            ).first()
            if existing_review:
                existing_review.rating = row['rating'] if row['rating'] is not None else 5.0
                existing_review.sentiment = sentiment_enum
                existing_review.relevance_score = 1.0
                existing_review.review_date = row['date']
                existing_review.author = row['author']
            else:
                cleaned_review = Review(
                    product_id=product_id,
                    review_text=row['overall_review'],
                    rating=row['rating'] if row['rating'] is not None else 5.0,
                    source=platform_enum,
                    sentiment=sentiment_enum,
                    relevance_score=1.0,
                    review_date=row['date'],
                    author=row['author']
                )
                db.session.add(cleaned_review)
       
        db.session.commit()
        return jsonify({
            "message": "Reviews successfully classified and stored/updated, sentiment summary generated/updated.",
            "positive_reviews": count_positive,
            "negative_reviews": count_negative,
            "neutral_reviews": count_neutral,
            "bar_data": bar_data
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# SENTIMENT SUMMARY
@app.route('/sentiment_summary/<int:product_id>', methods=['GET'])
@login_required
@handle_errors
def get_sentiment_summary(product_id):
    """
    Retrieves a sentiment summary for a specific product based on reviews from one or more platforms 
    (Amazon, Flipkart, or both) and aggregates sentiment metrics such as positive, negative, and neutral 
    review counts, average ratings, most frequent rating, and word frequencies.

    This endpoint aggregates sentiment analysis data across platforms, calculates key sentiment metrics, 
    and returns detailed insights into customer feedback. It also includes word frequencies and word cloud 
    data, which visualizes the most frequent terms mentioned in reviews for the given product.

    Args:
        product_id (int): The unique identifier for the product for which sentiment data is being requested.

    Query Parameters:
        platform (str, optional): A string that specifies which platform(s) to filter reviews by. 
            Accepts:
            - 'amazon': Retrieves sentiment summary data for reviews from Amazon only.
            - 'flipkart': Retrieves sentiment summary data for reviews from Flipkart only.
            - 'all': Aggregates sentiment data from all platforms (Amazon, Flipkart, or others).
            
            Defaults to 'all' if not provided.
        
        Example:
            GET /sentiment_summary/12345?platform=amazon
            GET /sentiment_summary/12345?platform=all

    Returns:
        Response (JSON): A JSON object containing the aggregated sentiment data for the requested product.
        The structure of the response includes:
            - `product_id`: The unique identifier of the product.
            - `positive_reviews`: The total number of positive reviews aggregated across the selected platform(s).
            - `negative_reviews`: The total number of negative reviews aggregated across the selected platform(s).
            - `neutral_reviews`: The total number of neutral reviews aggregated across the selected platform(s).
            - `average_rating`: The average rating based on reviews for the product across the selected platform(s).
            - `most_rating`: The most frequent rating (e.g., 5-star, 4-star) based on the reviews across the selected platform(s).
            - `word_frequencies`: A list of words and their frequencies found in the reviews, aggregated across all selected platforms.
            - `word_clouds`: A list of word clouds for each platform (only included if 'all' is selected). Each word cloud represents 
                the most frequent terms used in reviews for a specific platform.
            - `word_cloud`: The word cloud data for the selected platform (only included if a single platform is specified).

    Error Responses:
        - 400: Bad request due to invalid platform parameter. The platform must be one of ['amazon', 'flipkart', 'all'].
            Example:
            {
                "error": "Invalid platform. Choose from ['amazon', 'flipkart', 'all']."
            }
        - 404: No sentiment summary data was found for the given product and platform combination.
            Example:
            {
                "error": "No sentiment summary found for the specified product and platform."
            }
        - 500: Internal server error, typically in case of database connection issues or unexpected errors.
            Example:
            {
                "error": "An unexpected error occurred: {error_message}"
            }

    Example 1 (with platform='amazon'):
        GET /sentiment_summary/12345?platform=amazon
        
        Response:
        {
            "product_id": 12345,
            "positive_reviews": 150,
            "negative_reviews": 30,
            "neutral_reviews": 45,
            "average_rating": 4.2,
            "most_rating": 5,
            "word_frequencies": [{"word": "good", "frequency": 120}, {"word": "quality", "frequency": 110}],
            "word_cloud": "word_cloud_data_here"
        }

    Example 2 (with platform='all'):
        GET /sentiment_summary/12345?platform=all
        
        Response:
        {
            "product_id": 12345,
            "positive_reviews": 300,
            "negative_reviews": 60,
            "neutral_reviews": 90,
            "average_rating": 4.1,
            "most_rating": 5,
            "word_frequencies": [{"word": "good", "frequency": 240}, {"word": "quality", "frequency": 220}],
            "word_clouds": [
                {
                    "platform": "amazon",
                    "word_cloud": "amazon_word_cloud_data_here"
                },
                {
                    "platform": "flipkart",
                    "word_cloud": "flipkart_word_cloud_data_here"
                }
            ]
        }

    Notes:
        - The `average_rating` is the mean of all ratings across the reviews. If the platform is 'all', 
          the average rating is calculated across all available platforms for the product.
        - The `most_rating` is the most frequent rating value across reviews (e.g., 5-star, 4-star) for the selected platform(s).
        - If `platform` is 'all', both `word_clouds` for Amazon and Flipkart (or other platforms) will be included. If only one platform is chosen, the corresponding `word_cloud` will be included for that platform.
        - Word frequencies are aggregated across reviews for the selected platform(s), and the most frequent words are listed with their corresponding frequency count.
    """
    # Get the platform argument from query parameters
    platform = request.args.get('platform', 'all').lower()
    
    # Validate the platform parameter
    valid_platforms = ['all', 'amazon', 'flipkart']
    if platform not in valid_platforms:
        return jsonify({"error": "Invalid platform. Choose from ['amazon', 'flipkart', 'all']."}), 400
    
    try:
        # Query sentiment summaries based on the platform
        if platform == 'all':
            summaries = SentimentSummary.query.filter_by(product_id=product_id).all()
        else:
            platform_enum = ReviewSource[platform.upper()]
            summaries = SentimentSummary.query.filter_by(product_id=product_id, platform=platform_enum).all()
        
        if not summaries:
            return jsonify({"error": "No sentiment summary found for the specified product and platform."}), 404

        # Initialize aggregated data for all platforms (if 'all' is chosen)
        aggregated_summary = {
            "positive_reviews": 0,
            "negative_reviews": 0,
            "neutral_reviews": 0,
            "word_clouds": [],  # List of word cloud objects for each platform
            "word_frequencies": {},
            "average_rating": 0,
            "most_rating": None
        }


        rating_counts = {}
        # Aggregate data from all platform summaries
        for summary in summaries:
            # Aggregate review counts
            aggregated_summary["positive_reviews"] += summary.positive_count
            aggregated_summary["negative_reviews"] += summary.negative_count
            aggregated_summary["neutral_reviews"] += summary.neutral_count

            # Aggregate word frequencies
            for word, freq in zip(summary.words, summary.frequency):
                if word in aggregated_summary["word_frequencies"]:
                    aggregated_summary["word_frequencies"][word] += freq
                else:
                    aggregated_summary["word_frequencies"][word] = freq

            # If platform is 'all', add each platform's word cloud to the list
            if platform == 'all':
                platform_word_cloud = {
                    "platform": summary.platform.name.lower(),
                    "word_cloud": summary.word_cloud
                }
                aggregated_summary["word_clouds"].append(platform_word_cloud)

            # Retrieve ratings from summary
            aggregated_summary["average_rating"] += summary.average_rating
            # Count most ratings occurrences
            rating_counts[summary.most_rating] = rating_counts.get(summary.most_rating, 0) + 1
            
        # Calculate average of average ratings if 'all' is chosen
        if platform == 'all' and summaries:
            aggregated_summary["average_rating"] /= len(summaries)
            
        # Determine the most common rating if 'all' is chosen
        if rating_counts:
            aggregated_summary["most_rating"] = max(rating_counts, key=rating_counts.get)

        # Prepare the response data
        response_data = {
            "product_id": product_id,
            "positive_reviews": aggregated_summary["positive_reviews"],
            "negative_reviews": aggregated_summary["negative_reviews"],
            "neutral_reviews": aggregated_summary["neutral_reviews"],
            "average_rating": aggregated_summary["average_rating"],
            "most_rating": aggregated_summary["most_rating"],
            "word_frequencies": [{"word": word, "frequency": freq} for word, freq in aggregated_summary["word_frequencies"].items()]
        }

        # If platform is not 'all', include data for just that platform
        if platform != 'all':
            # Ensure to pick the word cloud for that specific platform
            platform_summary = summaries[0]  # We only need the first platform if one is requested
            response_data["word_cloud"] = platform_summary.word_cloud

        # Include word cloud data for all platforms if 'all' is selected
        if platform == 'all':
            response_data["word_clouds"] = aggregated_summary["word_clouds"]

        # Return the aggregated sentiment summary data
        return jsonify(response_data), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/dashboard', methods=['GET'])
@login_required
@handle_errors
def get_dashboard_data():
    """
    Retrieves dashboard data for the current logged-in user. This includes aggregated data from sentiment analysis 
    and scraping tasks, along with key statistics on products, reviews, and sentiment analysis results.

    Returns:
        Response (JSON): A JSON object containing key statistics such as:
            - `total_reviews`: Total number of reviews analyzed.
            - `total_products`: Total number of products.
            - `pending_scraping_tasks`: Number of scraping tasks that are pending.
            - `pending_scraping_task_details`: Details of the pending scraping tasks.
            - `total_positive_reviews`: Total number of positive reviews.
            - `total_negative_reviews`: Total number of negative reviews.
            - `total_neutral_reviews`: Total number of neutral reviews.
            - `average_rating`: The average overall rating across all reviews.
            - `most_rating`: The most frequent rating value.
            - `product_with_most_positive_reviews`: Product with the highest count of positive reviews.
            - `product_with_most_negative_reviews`: Product with the highest count of negative reviews.
            - `product_with_most_neutral_reviews`: Product with the highest count of neutral reviews.

    Error Responses:
        - 500: Internal server error in case of unexpected errors.
    """
    try:
        # Get total reviews analyzed (counting reviews for products created by the current user)
        total_reviews = db.session.query(Review).join(Product).filter(Product.created_by == current_user.id).count()

        # Get total products for the current user
        total_products = db.session.query(Product).filter_by(created_by=current_user.id).count()

        # Get pending scraping tasks (from ScrapingTasks table)
        pending_scraping_tasks = db.session.query(ScrapingTask).filter_by(status=Status.PENDING, created_by=current_user.id).count()

        # Get details of pending scraping tasks
        pending_scraping_task_details = db.session.query(ScrapingTask).filter_by(status=Status.PENDING, created_by=current_user.id).all()

        # Get product_ids created by the current user
        user_product_ids = db.session.query(Product.id).filter_by(created_by=current_user.id).all()
        user_product_ids = [prod[0] for prod in user_product_ids]  # Extract product ids from the query result

        # Aggregate sentiment summary counts (from SentimentSummary table)
        total_positive_reviews = db.session.query(db.func.sum(SentimentSummary.positive_count)) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)).scalar() or 0

        total_negative_reviews = db.session.query(db.func.sum(SentimentSummary.negative_count)) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)).scalar() or 0

        total_neutral_reviews = db.session.query(db.func.sum(SentimentSummary.neutral_count)) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)).scalar() or 0

        # Get average rating across all products for the current user
        average_rating = db.session.query(db.func.avg(SentimentSummary.average_rating)) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)).scalar() or 0
        # Get the most common rating (most rating)
        most_rating = db.session.query(SentimentSummary.most_rating) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)) \
            .group_by(SentimentSummary.most_rating) \
            .order_by(db.func.count().desc()).first()
            
        # Product with most positive reviews
        product_with_most_positive_reviews = db.session.query(SentimentSummary.product_id, db.func.sum(SentimentSummary.positive_count).label('total_positive')) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)) \
            .group_by(SentimentSummary.product_id) \
            .order_by(db.func.sum(SentimentSummary.positive_count).desc()).first()

        # Product with most negative reviews
        product_with_most_negative_reviews = db.session.query(SentimentSummary.product_id, db.func.sum(SentimentSummary.negative_count).label('total_negative')) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)) \
            .group_by(SentimentSummary.product_id) \
            .order_by(db.func.sum(SentimentSummary.negative_count).desc()).first()

        # Product with most neutral reviews
        product_with_most_neutral_reviews = db.session.query(SentimentSummary.product_id, db.func.sum(SentimentSummary.neutral_count).label('total_neutral')) \
            .filter(SentimentSummary.product_id.in_(user_product_ids)) \
            .group_by(SentimentSummary.product_id) \
            .order_by(db.func.sum(SentimentSummary.neutral_count).desc()).first()


        # Prepare response data
        response_data = {
            "total_reviews": total_reviews,
            "total_products": total_products,
            "pending_scraping_tasks": pending_scraping_tasks,
            "pending_scraping_task_details": [
                {
                    "task_id": task.id,
                    "status": task.status.name,
                    "created_at": task.created_at,
                    "message": task.message,
                    "platform": task.platform.name,
                    "product_id": task.product_id
                } for task in pending_scraping_task_details
            ],
            "total_positive_reviews": total_positive_reviews,
            "total_negative_reviews": total_negative_reviews,
            "total_neutral_reviews": total_neutral_reviews,
            "average_rating": average_rating,
            "most_rating": most_rating[0] if most_rating else 0,
            "product_with_most_positive_reviews": product_with_most_positive_reviews[0] if product_with_most_positive_reviews else None,
            "product_with_most_negative_reviews": product_with_most_negative_reviews[0] if product_with_most_negative_reviews else None,
            "product_with_most_neutral_reviews": product_with_most_neutral_reviews[0] if product_with_most_neutral_reviews else None
        }

        # Return the dashboard data
        return jsonify(response_data), 200

    except Exception as e:
        print(e)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

