# tasks.py
from selenium import webdriver
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import random
import string
import time
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import json
from app import app,db
from app.models import ScrapingTask, RawReview, Status, ReviewSource

import pandas as pd
import pickle
import re
import nltk

if os.environ.get('FLASK_ENV') != 'production':
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import plotly.graph_objs as go
from wordcloud import WordCloud
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer


# Function to remove the 'page' parameter and add a new one
def update_url_with_page_parameter(url, page_value):
    # Parse the current URL
    parsed_url = urlparse(url)

    # Parse the query parameters
    query_params = parse_qs(parsed_url.query)

    # Remove the 'page' parameter if it exists
    if 'page' in query_params:
        del query_params['page']

    # Add the new 'page' parameter with the desired value
    query_params['page'] = page_value

    # Rebuild the URL with the new query parameters
    new_query = urlencode(query_params, doseq=True)
    updated_url = urlunparse(parsed_url._replace(query=new_query))

    return updated_url

filterByStar = ['all_stars', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star', 'positive', 'critical']
formatType = ['current_format', 'all_formats']

# Helper to generate random ref for each page
def generate_ref(pagenumber):
    part1 = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
    part2 = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
    return f"{part1}_{part2}_getr_d_paging_btm_next_{pagenumber}"

# Helper to build the product URL
def get_product_url(asin, ref, star='all_stars', format='all_formats', pagenumber=1):
    return f"https://www.amazon.in/product-reviews/{asin}/ref={ref}?ie=UTF8&reviewerType=all_reviews&filterByStar={star}&formatType={format}&pageNumber={pagenumber}"

# Function to extract reviews from a page
def extract_reviews_from_page(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
   
    reviews = soup.find_all('div', {'data-hook': 'review'})
    extracted_reviews = []
    
    def get_text_or_default(element, tag, attributes, default=''):
        found_element = element.find(tag, attributes)
        return found_element.text.strip() if found_element else default
    
    for review in reviews:
        title = get_text_or_default(review, 'a', {'data-hook': 'review-title'})
        pattern = r"^\d+(\.\d+)?\s*out of \d+\s*stars\s*"
        # Use re.sub to remove the matching pattern
        cleaned_title = re.sub(pattern, "", title)
        title = cleaned_title.strip()
        extracted_reviews.append({
            'title': title,
            'rating': get_text_or_default(review, 'i', {'data-hook': 'review-star-rating'}),
            'body': get_text_or_default(review, 'span', {'data-hook': 'review-body'}),
            'author': get_text_or_default(review, 'span', {'class': 'a-profile-name'}),
            'date': get_text_or_default(review, 'span', {'data-hook': 'review-date'})
        })
    
    return extracted_reviews


def scrape_flipkart_reviews(fsn, task_id, product_id, **kwargs):
    with app.app_context():
        print('starting reviews fetch')
        created_by = kwargs.get('created_by')
        task = ScrapingTask(id=task_id, fsn_asin=fsn, platform=ReviewSource.FLIPKART, status=Status.PENDING, created_by=created_by, product_id = product_id)
        db.session.add(task)
        db.session.commit()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(options=chrome_options)
        product_url = f'https://www.flipkart.com/product/p/itme?pid={fsn}'
        review_list = []

        try:
            driver.get(product_url)

            # Close popup if present
            try:
                close_button = driver.find_element(By.XPATH, "//span[@role='button' and contains(@class, '_30XB9F') and text()='✕']")
                close_button.click()
            except NoSuchElementException:
                pass

            # Navigate to reviews section
            try:
                div_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, '_23J90q RcXBOT')]/span[contains(text(), 'All') and contains(text(), 'reviews')]"))
                )
                review_page_anchor = div_element.find_element(By.XPATH, "./ancestor::a")
                review_page_anchor.click()
            except TimeoutException:
                task.status = Status.FAILED
                task.message = "Reviews section not found. Timeout error"
                db.session.commit()
                return json.dumps({"success": False, "message": "Reviews section not found.", "error": 'Timeout Error'})

            # Scraping loop
            page = 1
            flag = True
            while flag:
                try:
                    main_div = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'DOjaWF gdgoEp col-9-12')]"))
                    )
                    soup = BeautifulSoup(main_div.get_attribute('outerHTML'), 'html.parser')
                    nested_divs = soup.find_all("div", class_="cPHDOP col-12-12")

                    for div in nested_divs:
                        review_dict = {}
                        row_elements = div.find_all(class_="row")
                        for row in row_elements:
                            try:
                                review_dict['rating'] = row.find(class_='XQDdHH Ga3i8K').get_text()
                            except:
                                pass
                            try:
                                review_dict['title'] = row.find('p', class_='z9E0IG').get_text()
                            except:
                                pass
                            try:
                                review_text = row.find(class_='ZmyHeo')
                                review_dict['review'] = review_text.get_text(separator=" ", strip=True).split('<span>')[0].rstrip(' READ MORE')
                            except:
                                pass
                        try:
                            userAndDate = div.find(class_='row gHqwa8').find(class_='row')
                            userAndDate = userAndDate.find_all('p')
                            review_dict['buyer'] = userAndDate[0].get_text()
                            review_dict['date'] = userAndDate[-1].get_text()
                        except:
                            pass
                        review_list.append(review_dict)
                except TimeoutException:
                    flag = False

                # Navigate to next page if available
                try:
                    nav_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//nav[@class='WSL9JP']"))
                    )
                    next_button = nav_element.find_element(By.CLASS_NAME, "_9QVEpD")
                    page += 1
                    updated_url = update_url_with_page_parameter(driver.current_url, page_value=page)
                    driver.get(updated_url)
                except (NoSuchElementException, TimeoutException):
                    flag = False
        except Exception as e:
            task.status = Status.FAILED
            task.message = str(e)
            db.session.commit()
            return json.dumps({"success": False, "message": "An unexpected error occurred.", "error": str(e)})
        finally:
            driver.quit()
            db.session.commit()
        review_list = [d for d in review_list if d]
        print('completed reviews fetching')
        for review in review_list:
            new_review = RawReview(
                task_id=task_id,
                title=review.get('title'),
                rating=review.get('rating'),
                body=review.get('review'),
                author=review.get('buyer'),
                date=review.get('date'),
                platform=ReviewSource.FLIPKART,
                product_id=product_id
            )
            db.session.add(new_review)
        task.status = Status.COMPLETED
        db.session.commit()
        return json.dumps({"success": True, "message": "Scraping completed successfully.",'reviews': review_list})  # Return scraped reviews

def scrape_amazon_reviews(asin, task_id, product_id, **kwargs):
    with app.app_context():
        created_by = kwargs.get('created_by')
        print('started amazon reviews fetch')
        task = ScrapingTask(id=task_id, fsn_asin=asin, platform=ReviewSource.AMAZON, status=Status.PENDING, created_by=created_by, product_id=product_id)
        db.session.add(task)
        db.session.commit()
        max_pages = 100
        all_reviews = []
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(options=chrome_options)
        try:
            for star in filterByStar:
                ref = generate_ref(1)
                product_url = get_product_url(asin=asin, ref=ref, star=star, format=formatType[0])

                try:
                    driver.get(product_url)
                    time.sleep(3)
                    current_url = driver.current_url
                    if "/ap/signin" in current_url:
                        try:
                            email_element = driver.find_element(By.ID, 'ap_email')
                            email_element.send_keys('8368918163')
                            time.sleep(2)
                            second_continue_button = driver.find_element(By.XPATH, "//input[@id='continue' and @class='a-button-input']")
                            second_continue_button.click()
                            time.sleep(3)
                            password_field = driver.find_element(By.ID, "ap_password")
                            password_field.send_keys("Vaibhav@123")  # Replace with your actual password

                            # Step 4: Submit the form (assuming there is a 'signInSubmit' button)
                            sign_in_button = driver.find_element(By.ID, "signInSubmit")
                            sign_in_button.click()

                            # Optional: Add more wait or verification to ensure login success
                            time.sleep(3)
                        except Exception as e:
                            task.status = Status.FAILED
                            task.message = 'Login issue at amazon'+str(e)
                            db.session.commit()
                            return json.dumps({"success": False, "message": "Failed to load amazon.", "error": str(e)})
                except Exception as e:
                    task.status = Status.FAILED
                    task.message = str(e)
                    db.session.commit()
                    return json.dumps({"success": False, "message": "Failed to load the initial page.", "error": str(e)})

                current_page = 1
                while current_page <= max_pages:
                    try:
                        # Extract reviews
                        reviews = extract_reviews_from_page(driver.page_source)
                        all_reviews.extend(reviews)

                        # Check if there is a next page
                        try:
                            next_button = driver.find_element(By.CLASS_NAME, 'a-last')
                            if 'a-disabled' in next_button.get_attribute('class'):
                                break  # Stop if there's no next page
                        except Exception as e:
                            break
                        finally:
                            # Generate URL for the next page and navigate
                            current_page+=1
            
                        current_ref = generate_ref(current_page)
                        product_url = get_product_url(asin=asin, ref=current_ref, star=star, format=formatType[0], pagenumber=current_page)
                        driver.get(product_url)
                        time.sleep(3)
                    except Exception as e:
                        task.status = Status.FAILED
                        task.message = str(e)
                        db.session.commit()
                        return json.dumps({"success": False, "message": "Error during scraping process.", "error": str(e)})

        except Exception as e:
            task.status = Status.FAILED
            task.message = str(e)
            db.session.commit()
            return json.dumps({"success": False, "message": "An unexpected error occurred.", "error": str(e)})
        finally:
            driver.quit()
       
        print('completed amazon reviews fetch')
        for review in all_reviews:
            new_review = RawReview(
                task_id=task_id,
                title=review.get('title'),
                rating=review.get('rating'),
                body=review.get('body'),
                author=review.get('author'),
                date=review.get('date'),
                platform=ReviewSource.AMAZON,
                product_id = product_id
            )
            db.session.add(new_review)
        task.status = Status.COMPLETED
        db.session.commit()
        return json.dumps({"success": True, "message": "Scraping completed successfully.", "reviews": all_reviews})
    
    
    

def preprocess_text(text):
    # Make text lowercase and remove links, text in square brackets, punctuation, and words containing numbers
    text = str(text)
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+|\[.*?\]|[^a-zA-Z\s]+|\w*\d\w*', ' ', text)
    text = re.sub(r'\n', ' ', text)
    pattern = r"^\d+(\.\d+)?\s*out of \d+\s*stars\s*"
    # Use re.sub to remove the matching pattern
    cleaned_text = re.sub(pattern, "", text)
    text = cleaned_text.strip()

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    text = ' '.join(filtered_words).strip()

    # Tokenize
    tokens = nltk.word_tokenize(text)

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    lem_tokens = [lemmatizer.lemmatize(token) for token in tokens]

    
    return ' '.join(lem_tokens)

def convert_rating(rating):
    """
    Convert rating from string format 'X out of 5 stars' to a float.
    If rating is invalid or None, returns None.
    """
    if pd.isna(rating) or not rating.strip():
        return None
    
    try:
        # Extract the numeric rating (before "out of 5 stars")
        rating_value = rating.split(' ')[0]
        return float(rating_value)
    except Exception as e:
        return None
    
def fill_missing_ratings(dataframe):
    """
    Fills missing or invalid ratings with the most frequent valid rating.
    """
    # Apply the convert_rating function to the 'rating' column
    dataframe['rating'] = dataframe['rating'].apply(convert_rating)
    
    # Find the most frequent rating (mode)
    most_frequent_rating = dataframe['rating'].mode().iloc[0]
    
    # Fill NaN or None ratings with the most frequent rating
    dataframe['rating'] = dataframe['rating'].fillna(most_frequent_rating)


# Function to perform word distribution analysis
def word_distribution(text_data, top_n=50):
    sentiment_summary = {
        "features": [],
        "frequency": []
    }
    # Initialize CountVectorizer with max_features to limit to top N tokens
    vectorizer = CountVectorizer(max_features=top_n)
    
    # Fit and transform the text data
    docs = vectorizer.fit_transform(text_data)
    
    # Get feature names and frequencies
    features = vectorizer.get_feature_names_out()
    frequency = docs.sum(axis=0).A1  # Summing frequency across documents
    
    # Populate sentiment_summary
    sentiment_summary["features"] = features.tolist()
    sentiment_summary["frequency"] = frequency.tolist()
    
    return sentiment_summary

