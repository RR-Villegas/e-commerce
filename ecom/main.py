from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, make_response
import mysql.connector
import smtplib
import random
import string
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'please_amongbus'  # Replace with a strong secret key

app.config['UPLOAD_FOLDER'] = 'static/uploads'  
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create folder if it doesn't exist

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a new database connection."""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='ecom'
    )


def send_email(to_email, subject, body):
    """Send an email notification."""
    from_email = "bigtouhouenjoyer"  # Replace with your email
    from_password = "zhrm rpbw pvcx vevt"  # Replace with your email password

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


def login_required(f):
    """Decorator to check if user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to log in first.', 'error')
            return redirect(url_for('redirectlogin'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def home():
    user_logged_in = 'username' in session
    user_name = session.get('username', 'Guest')
    user_email = session.get('email') if user_logged_in else None
    user_verification = None

    if user_logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT verification FROM accounts WHERE email = %s', (user_email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            user_verification = user_data['verification']

    return render_template('homepage.html', 
                           user_logged_in=user_logged_in, 
                           user_name=user_name, 
                           user_email=user_email, 
                           user_verification=user_verification)

@app.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    # Redirect to the admin verification page
    return redirect(url_for('admin_panel'))

@app.route('/admin_verify', methods=["GET", "POST"])
@login_required
def admin_verify():
    if request.method == 'POST':
        # Handle 2FA verification
        code = request.form['code']
        if code == session.get('2fa_code'):
            session['is_admin'] = True  # Mark user as verified for admin access
            return redirect(url_for('admin_panel'))  # Redirect to admin panel after successful verification
        else:
            flash('Invalid verification code.', 'error')
            return render_template('admin_verify.html')  # Render the page again to enter code

    # If this is a GET request or if the user is not verified, send a new code
    if 'is_admin' not in session:
        email = session.get('email')
        session['2fa_code'] = ''.join(random.choices(string.digits, k=6))  # Generate a 6-digit code
        send_email(email, "Your 2FA Code", f"Your verification code is: {session['2fa_code']}")
        return render_template('admin_verify.html')  # Render a page to input the 2FA code

    return redirect(url_for('admin_panel'))  # Redirect to admin panel if already verified

@app.route('/admin_panel')
@login_required
def admin_panel():
    return render_template('admin_panel.html', show_register=True)

@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html', show_register=True)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO accounts (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
        conn.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('redirectlogin'))  # Redirect to login instead of home
    except mysql.connector.IntegrityError:
        conn.rollback()
        flash('Email already exists. Try a different one.', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('redirectlogin'))  # Ensure to redirect back to login form


@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Check if user exists and verify the password
    if user and check_password_hash(user['password'], password):  # Verify hashed password
        session['id'] = user['id']
        session['email'] = user['email']
        session['username'] = user['username']
        session['verification'] = user['verification']
        
        if user['verification'] == 'admin':  # Check if user is admin
            return redirect(url_for('admin_verify'))  # Redirect to admin verification page
        
        flash('Login successful!', 'success')
        return redirect(url_for('home'))
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return render_template('register.html', show_register=False)


@app.route('/redirectlogin', methods=['GET'])
def redirectlogin():
    return render_template('register.html', show_register=False)  # Ensure to show the login form


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    response = make_response(redirect(url_for('home')))
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/api/fetch_user_accounts/', methods=['GET'])
def fetch_user_accounts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, username, email, verification FROM accounts')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)


@app.route('/api/fetch_seller_applications/', methods=['GET'])
def fetch_seller_applications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT sa.request_id, a.username, a.email, sa.shop_name, sa.shop_description, sa.status
        FROM sellerapplication sa
        JOIN accounts a ON sa.user_id = a.id
        WHERE sa.status = %s
    ''', ('pending',))
    applications = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(applications)


@app.route('/api/update_application_status/<int:request_id>/', methods=['POST'])
def update_application_status(request_id):
    action = request.json.get('action')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT email, username FROM accounts WHERE id = (SELECT user_id FROM sellerapplication WHERE request_id = %s)', (request_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'success': False, 'error': 'User  not found'}), 404

        user_email, username = user

        if action == 'approve':
            cursor.execute('UPDATE accounts SET verification = %s WHERE id = (SELECT user_id FROM sellerapplication WHERE request_id = %s)', ('verified', request_id))
            cursor.execute('UPDATE sellerapplication SET status = %s WHERE request_id = %s', ('approved', request_id))
            subject = "Your Seller Application has been Approved"
            body = f"Dear {username},\n\nCongratulations! Your seller application has been approved. You can now start selling on our platform.\n\nBest regards,\nThe Team"
        elif action == 'reject':
            cursor.execute('UPDATE sellerapplication SET status = %s WHERE request_id = %s', ('rejected', request_id))
            subject = "Your Seller Application has been Rejected"
            body = f"Dear {username},\n\nWe regret to inform you that your seller application has been rejected. If you have any questions, please feel free to contact us.\n\nBest regards,\nThe Team"

        conn.commit()
        send_email(user_email, subject, body)

        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/become_seller', methods=['GET'])
@login_required
def become_seller():
    # Render the not_verified.html page directly
    return render_template('not_verified.html')  # Always render this page

@app.route('/register_verified', methods=['GET', 'POST'])
@login_required
def register_verified():
    if request.method == 'POST':
        # Handle the seller application submission
        shop_name = request.form['shop_name']
        shop_description = request.form['shop_description']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO sellerapplication (user_id, email, shop_name, shop_description, status) VALUES (%s, %s, %s, %s, %s)',
                (session['id'], session['email'], shop_name, shop_description, 'pending')
            )
            conn.commit()
            flash('Your application has been submitted successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to home after successful submission
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

    # Render the seller application form for GET requests
    username = session.get('username', 'Guest')
    email = session.get('email', '')  # Get the user's email
    return render_template('register_verified.html', username=username, email=email)

@app.route('/sellers_panel', methods=['GET'])
@login_required
def sellers_panel():
    return render_template('sellers_panel.html')

@app.route('/sell_product', methods=['POST'])
def sell_product():
    product_name = request.form['product_name']
    product_price = request.form['product_price']
    product_category = request.form['product_category']
    product_description = request.form['product_description']
    product_stock = int(request.form['product_stock'])  # Convert to integer

    product_image = request.files['product_image']
    
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Construct the relative image path using forward slashes
    relative_image_path = f"uploads/{product_image.filename}"  # Use forward slashes directly
    
    # Save the image to the upload folder
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], product_image.filename)
    product_image.save(image_path)

    # Now you can save relative_image_path to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO products (productname, price, productcategory, productdescription, productimage, productstock, ownerid) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (product_name, product_price, product_category, product_description, relative_image_path, product_stock, session['id']))
        conn.commit()
        flash('Product added successfully!', 'success')
    except Exception as e:
        conn.rollback() 
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close() 

    return redirect(url_for('sellers_panel'))

@app.route('/api/products', methods=['GET'])
@login_required
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT productid, productname, price, productcategory, productdescription, productimage, productstock, discount_percentage 
        FROM products 
        WHERE ownerid = %s
    ''', (session['id'],))
    products = cursor.fetchall()
    conn.close()

    return jsonify([{
        'id': product[0],
        'name': product[1],
        'price': product[2],
        'category': product[3],
        'description': product[4],
        'image': product[5],
        'stock': product[6],
        'discount_percentage': product[7]  # Add discount_percentage to the response
    } for product in products])

@app.route('/api/total_products', methods=['GET'])
@login_required
def total_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Execute a simple count query
        cursor.execute('SELECT COUNT(*) AS total FROM products WHERE ownerid = %s', (session['id'],))
        total = cursor.fetchone()  # Fetch the result
        return jsonify({'total_products': total[0]})  # Return the total count
    except Exception as e:
        print(f"Error fetching total products: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500  # Return a JSON error response
    finally:
        cursor.close()
        conn.close()    
        
@app.route('/api/delete_product/<int:product_id>/', methods=['DELETE'])
@login_required
def delete_product(product_id):
    logging.info(f"Starting deletion process for product ID: {product_id}")  # Log when deletion starts
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Ensure the cursor returns dictionaries
    try:
        # Step 1: Retrieve the image path from the database
        cursor.execute('SELECT productimage FROM products WHERE productid = %s AND ownerid = %s', (product_id, session['id']))
        product = cursor.fetchone()

        if not product:
            logging.warning(f"Product ID {product_id} not found or not owned by user ID {session['id']}.")  # Log warning if product not found
            return jsonify({'success': False, 'error': 'Product not found or not owned by you.'}), 404

        image_path = product['productimage']  # This should be something like 'uploads/dress.png'

        # Step 2: Construct the full path to the image file
        full_image_path = os.path.join(app.root_path, 'static', image_path)  # Ensure correct path construction
        logging.info(f"Attempting to delete image at: {full_image_path}")  # Log the full path

        # Step 3: Delete the image file from the server
        try:
            if os.path.exists(full_image_path):
                os.remove(full_image_path)
                logging.info(f"Deleted image: {full_image_path}")
            else:
                logging.warning(f"Image not found, cannot delete: {full_image_path}")
        except Exception as e:
            logging.error(f"Error deleting image: {str(e)}")

        # Step 4: Now delete the product from the database
        cursor.execute('DELETE FROM products WHERE productid = %s AND ownerid = %s', (product_id, session['id']))
        conn.commit()
        logging.info(f"Product ID {product_id} deleted successfully.")  # Log successful deletion

        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error deleting product: {str(e)}")  # Log the error
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')  # Get the search query from the URL
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Example query to fetch products based on the search query
    cursor.execute("SELECT * FROM products WHERE productname LIKE %s", ('%' + query + '%',))
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('search_panel.html', query=query, products=products)

@app.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    # Fetch product details from the database using the product_id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE productid = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if product:
        # Check if stock is zero
        if product['productstock'] == 0:
            product['out_of_stock'] = True  # Add a flag to indicate out of stock
        else:
            product['out_of_stock'] = False

        return render_template('productselect.html', product=product)
    else:
        return "Product not found", 404
    
@app.route('/api/reviews/<int:product_id>', methods=['GET', 'POST'])
@login_required
def reviews(product_id):
    if request.method == 'POST':
        # Check if the user has already reviewed the product
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reviews WHERE product_id = %s AND user_id = %s', (product_id, session['id']))
        existing_review = cursor.fetchone()

        if existing_review:
            return jsonify({'success': False, 'error': 'You have already reviewed this product.'}), 400

        # Handle review submission
        rating = request.json.get('rating')
        comment = request.json.get('comment')
        
        try:
            cursor.execute('INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (%s, %s, %s, %s)',
                           (product_id, session['id'], rating, comment))
            conn.commit()
            return jsonify({'success': True}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    else:
        # Fetch existing reviews
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT r.rating, r.comment, r.created_at, a.username 
            FROM reviews r 
            JOIN accounts a ON r.user_id = a.id 
            WHERE r.product_id = %s
        ''', (product_id,))
        reviews = cursor.fetchall()

        # Fetch the user's review if it exists
        cursor.execute('''
            SELECT rating, comment, created_at 
            FROM reviews 
            WHERE product_id = %s AND user_id = %s
        ''', (product_id, session['id']))
        user_review = cursor.fetchone()

        cursor.close()
        conn.close()

        # Log the fetched data for debugging
        print("Fetched Reviews:", reviews)
        print("Fetched User Review:", user_review)

        # Return both reviews and user's review
        return jsonify({
            'reviews': reviews,
            'user_review': user_review
        })

@app.route('/cart', methods=['GET'])
@login_required
def cart():
    return render_template('cart.html')  

@app.route('/api/cart', methods=['POST',])
@login_required
def add_to_cart():
    product_id = request.json.get('product_id')
    product_name = request.json.get('product_name')
    product_price = request.json.get('product_price')
    quantity = request.json.get('quantity', 1)  # Get the quantity from the request, default to 1

    # Initialize cart in the session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []

    # Check if the product is already in the cart
    existing_product = next((item for item in session['cart'] if item['id'] == product_id), None)
    if existing_product:
        existing_product['quantity'] += quantity  # Increment quantity by the specified amount
    else:
        # Add new product to cart with the specified quantity
        session['cart'].append({
            'id': product_id,
            'name': product_name,
            'price': product_price,
            'quantity': quantity
        })

    session.modified = True  # Mark session as modified
    return jsonify(session['cart'])  # Return the updated cart

@app.route('/api/cart/items', methods=['GET'])
@login_required
def get_cart_items():
    """Fetch the user's cart items from the session."""
    cart = session.get('cart', [])
    return jsonify(cart)  # Return the cart as a JSON response

@app.route('/api/fetch_verified_sellers/', methods=['GET'])
@login_required
def fetch_verified_sellers_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # SQL query to join accounts and verified sellers details
    cursor.execute('''
        SELECT 
            a.id,
            a.username,
            a.email,
            sa.shop_name,
            sa.shop_description,
            sa.created_at,
            sa.province,
            sa.city,
            sa.barangay,
            sa.postal_code,
            sa.phonenumber  -- Ensure phonenumber is included here
        FROM 
            accounts a
        JOIN 
            sellerapplication sa ON a.id = sa.user_id
        WHERE 
            a.verification = 'verified'
    ''')
    
    sellers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(sellers)

@app.route('/checkout', methods=['GET'])
@login_required  # Ensure the user is logged in
def checkout():
    return render_template('checkout.html')

@app.route('/api/checkout', methods=['POST'])
@login_required
def checkout_api():
    """Handle placing an order."""
    try:
        cart_items = session.get('cart', [])
        
        if not cart_items:
            logging.warning('Checkout attempt with empty cart.')
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
        if 'id' not in session or 'email' not in session:
            logging.warning('Checkout attempt by user not logged in.')
            return jsonify({'success': False, 'message': 'User  not logged in'}), 401
        
        order_data = []
        for item in cart_items:
            if 'id' not in item or 'price' not in item or 'quantity' not in item:
                logging.error(f'Invalid cart item data: {item}')
                return jsonify({'success': False, 'message': 'Invalid cart item data'}), 400
            
            # Prepare the order data tuple
            order_data.append((session['id'], item['id'], item['quantity'], item['price'] * item['quantity']))

        # Log the order data for debugging
        logging.debug(f'Order data: {order_data}')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute batch insert for orders
        cursor.executemany('''
            INSERT INTO orders (buyer_id, item_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        ''', order_data)

        # Update product stock
        for item in cart_items:
            product_id = item['id']
            quantity = item['quantity']
            cursor.execute('''
                UPDATE products 
                SET productstock = productstock - %s 
                WHERE productid = %s
            ''', (quantity, product_id))

        conn.commit()
        session.pop('cart', None)  # Clear the cart
        
        logging.info(f'Order placed successfully for user {session["id"]}.')
        return jsonify({'success': True, 'message': 'Order placed successfully!'}), 200
    except Exception as e:
        logging.error(f'Error during checkout: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Internal server error. Please try again later.'}), 500

@app.route('/api/cart/clear', methods=['DELETE'])
@login_required
def clear_cart_api():
    """Clear the user's cart."""
    try:
        session.pop('cart', None)  # Clear the cart from the session
        return jsonify({'success': True, 'message': 'Cart cleared successfully!'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/clothing', methods=['GET'])
@login_required
def clothing():
    return render_template('clothing.html')

@app.route('/api/all_products', methods=['GET'])
@login_required
def get_all_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT productid, productname, price, productcategory, productdescription, productimage, productstock FROM products')
        products = cursor.fetchall()
        conn.close()

        return jsonify(products)  # Return the list of products as JSON
    except Exception as e:
        logger.error(f'Error fetching products: {str(e)}')
        return jsonify({'error': 'Internal server error. Please try again later.'}), 500

@app.route('/category')
@login_required
def category():
    category_name = request.args.get('category')  # Get the category from the URL
    return render_template('category.html', category=category_name)

@app.route('/api/products_by_category', methods=['GET'])
@login_required
def products_by_category():
    category = request.args.get('category')
    if not category:
        return jsonify({'error': 'Category not specified'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT productid, productname, price, productcategory, productdescription, productimage FROM products WHERE productcategory = %s', (category,))
        products = cursor.fetchall()
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/api/store_owner', methods=['GET'])
def get_store_owner():
    product_id = request.args.get('product_id')  # Get product ID from query parameters
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT 
                sa.shop_name
            FROM 
                products p
            LEFT JOIN 
                sellerapplication sa ON p.ownerid = sa.user_id
            WHERE 
                p.productid = %s;
        ''', (product_id,))
        result = cursor.fetchone()

        if result:
            return jsonify({'store_owner': result['shop_name']})  # Return the store name
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/average_rating/<int:product_id>', methods=['GET'])
def average_rating(product_id):
    # Fetch average rating from the database using the product_id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT AVG(r.rating) AS average_rating
        FROM reviews r
        WHERE r.product_id = %s
    ''', (product_id,))
    average_rating = cursor.fetchone()['average_rating']
    
    # Ensure average_rating is a decimal and round it
    average_rating = round(average_rating, 2) if average_rating is not None else 0.0

    cursor.close()
    conn.close()
    
    return jsonify({"average_rating": average_rating})  # Return average rating as JSON

@app.route('/edit_product/<int:product_id>', methods=['GET'])
@login_required
def edit_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE productid = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if product:
        return render_template('edit_product.html', product=product)
    else:
        flash('Product not found.', 'error')
        return redirect(url_for('sellers_panel'))  # Redirect to the sellers panel if not found
    
@app.route('/edit_item', methods=['GET', 'POST'])
@login_required
def edit_item():
    if request.method == 'POST':
        # Handle form submission
        product_id = request.form['id']
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        stock = request.form['stock']
        discount = request.form['discount']

        # Logic to update the product in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products
            SET productname = %s, price = %s, productcategory = %s, productstock = %s, discount_percentage = %s
            WHERE productid = %s
        ''', (name, price, category, stock, discount, product_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Product updated successfully!', 'success')
        return redirect(url_for('sellers_panel'))  # Redirect to the seller's panel

    # Handle GET request to display the edit form
    product_id = request.args.get('id')  # Get product ID from query parameters
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE productid = %s', (product_id,))
    product = cursor.fetchone() 
    cursor.close()
    conn.close()

    if product:
        return render_template('edit_product.html', product=product)
    else:
        flash('Product not found.', 'error')
        return redirect(url_for('sellers_panel'))  # Redirect if product not found

if __name__ == '__main__':
    app.run(debug=True)