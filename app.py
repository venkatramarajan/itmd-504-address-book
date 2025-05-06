from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
import logging
from urllib.parse import quote_plus
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Determine environment
is_production = os.getenv('FLASK_ENV') == 'production'

app = Flask(__name__)

# Configure CORS with credentials
CORS(app, 
     supports_credentials=True,
     resources={r"/api/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}},
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Session configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SESSION_COOKIE_SECURE'] = is_production  # True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

def update_mysql_user_password():
    try:
        # Create SQL commands
        sql_commands = [
            "ALTER USER 'addressbook_user'@'localhost' IDENTIFIED BY 'AddressBook123!';",
            "FLUSH PRIVILEGES;"
        ]
        
        # Execute MySQL commands using sudo
        for cmd in sql_commands:
            mysql_cmd = f"sudo mysql -e \"{cmd}\""
            result = subprocess.run(mysql_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"MySQL command failed: {result.stderr}")
                raise Exception(f"MySQL command failed: {result.stderr}")
            
        logger.info("Successfully updated MySQL user password")
    except Exception as e:
        logger.error(f"Failed to update MySQL user password: {str(e)}")
        raise

# MySQL Configuration
db_user = os.getenv('DB_USER', 'addressbook_user')
db_password = quote_plus(os.getenv('DB_PASSWORD', 'AddressBook123!'))
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'addressbook')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logger.info(f"Database URI: mysql+pymysql://{db_user}:****@{db_host}/{db_name}")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    contacts = db.relationship('Contact', backref='user', lazy=True)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)
    apartment_unit = db.Column(db.String(20))
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logger.debug(f"Login attempt for username: {data.get('username')}")
        
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Missing username or password in request")
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            logger.error(f"User not found: {data['username']}")
            return jsonify({'error': 'Invalid credentials'}), 401

        if bcrypt.check_password_hash(user.password, data['password']):
            login_user(user, remember=True)
            logger.info(f"User logged in successfully: {user.username}")
            return jsonify({
                'message': 'Logged in successfully',
                'is_admin': user.is_admin,
                'username': user.username
            })
        else:
            logger.error(f"Invalid password for user: {user.username}")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': c.id,
        'firstname': c.firstname,
        'lastname': c.lastname,
        'email': c.email,
        'street_address': c.street_address,
        'apartment_unit': c.apartment_unit,
        'city': c.city,
        'zip_code': c.zip_code,
        'phone': c.phone
    } for c in contacts])

@app.route('/api/contacts', methods=['POST'])
@login_required
def create_contact():
    data = request.get_json()
    new_contact = Contact(
        firstname=data['firstname'],
        lastname=data['lastname'],
        email=data['email'],
        street_address=data['street_address'],
        apartment_unit=data.get('apartment_unit'),
        city=data['city'],
        zip_code=data['zip_code'],
        phone=data['phone'],
        user_id=current_user.id
    )
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({'message': 'Contact created successfully'}), 201

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    if contact.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    contact.firstname = data['firstname']
    contact.lastname = data['lastname']
    contact.email = data['email']
    contact.street_address = data['street_address']
    contact.apartment_unit = data.get('apartment_unit')
    contact.city = data['city']
    contact.zip_code = data['zip_code']
    contact.phone = data['phone']
    
    db.session.commit()
    return jsonify({'message': 'Contact updated successfully'})

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    if contact.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': 'Contact deleted successfully'})

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'is_admin': u.is_admin
    } for u in users])

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        is_admin=data.get('is_admin', False)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Create admin user if not exists
def create_admin_user():
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    try:
        # Update MySQL user password before starting the app
        update_mysql_user_password()
        
        with app.app_context():
            db.create_all()
            create_admin_user()
        
        logger.info("Starting Flask server...")
        if is_production:
            logger.info("Running in PRODUCTION mode")
            # In production, we should use a proper WSGI server
            # This is just for development
            app.run(host='0.0.0.0', port=5000, debug=False)
        else:
            logger.info("Running in DEVELOPMENT mode")
            app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")
        raise 