"""Authentication Database Module"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
from pathlib import Path


class AuthDB:
    """SQLite database for user authentication"""

    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def init_db(self):
        """Initialize database with users table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email_verified INTEGER DEFAULT 0,
                verification_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"

    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, pwd_hash = stored_hash.split('$')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == pwd_hash
        except:
            return False

    def create_user(self, username, email, password):
        """Create new user with email verification token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            password_hash = self.hash_password(password)
            verification_token = secrets.token_urlsafe(32)

            cursor.execute(
                'INSERT INTO users (username, email, password_hash, verification_token) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, verification_token)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {'success': True, 'user_id': user_id, 'verification_token': verification_token, 'email': email}
        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e):
                return {'success': False, 'error': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
            return {'success': False, 'error': 'User already exists'}

    def authenticate(self, username, password):
        """Authenticate user and return user data (requires verified email)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return {'success': False, 'error': 'Invalid username or password'}

        if not self.verify_password(password, user['password_hash']):
            conn.close()
            return {'success': False, 'error': 'Invalid username or password'}

        # Check if email is verified
        if not user['email_verified']:
            conn.close()
            return {'success': False, 'error': 'Please verify your email before logging in'}

        # Update last login
        cursor.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.now(), user['id'])
        )
        conn.commit()
        conn.close()

        return {
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
        }

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, username, email, created_at FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    def create_session_token(self, user_id):
        """Create session token for user"""
        token = secrets.token_urlsafe(32)
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO sessions (user_id, session_token) VALUES (?, ?)',
            (user_id, token)
        )
        conn.commit()
        conn.close()

        return token

    def get_user_by_token(self, token):
        """Get user by session token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.username, u.email, u.created_at
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.session_token = ?
        ''', (token,))

        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    def delete_session(self, token):
        """Delete session token (logout)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (token,))
        conn.commit()
        conn.close()

    def verify_email(self, token):
        """Verify email using verification token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE verification_token = ?', (token,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return {'success': False, 'error': 'Invalid verification token'}

        if user['email_verified']:
            conn.close()
            return {'success': False, 'error': 'Email already verified'}

        cursor.execute(
            'UPDATE users SET email_verified = 1, verification_token = NULL WHERE id = ?',
            (user['id'],)
        )
        conn.commit()
        conn.close()

        return {'success': True, 'message': 'Email verified successfully'}
