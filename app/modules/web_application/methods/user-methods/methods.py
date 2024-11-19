from datetime import datetime
from werkzeug.utils import secure_filename
import os
from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from flask import current_app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
db = SQLAlchemy(app)
from models import User
class UserService:
    @staticmethod
    def create_user(name: str, email: str, social_login_provider: Optional[str] = None, 
                   profile_picture: Optional[str] = None) -> Optional['User']:
        try:
            user = User(
                name=name,
                email=email,
                social_login_provider=social_login_provider,
                profile_picture=profile_picture,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None
        
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional['User']:
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional['User']:
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_users() -> List['User']:
        return User.query.all()
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> Optional['User']:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return False
        
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
    
    @staticmethod
    def upload_profile_picture(user_id: int, file) -> Optional[str]:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            filename = secure_filename(file.filename)
            unique_filename = f"{user_id}_{int(datetime.utcnow().timestamp())}_{filename}"
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/profile_pictures')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            user.profile_picture = file_path
            db.session.commit()
            
            return file_path
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def search_users(search_term: str) -> List['User']:
        return User.query.filter(
            db.or_(
                User.name.ilike(f"%{search_term}%"),
                User.email.ilike(f"%{search_term}%")
            )
        ).all()

    @staticmethod
    def get_users_by_provider(provider: str) -> List['User']:
        return User.query.filter_by(social_login_provider=provider).all()
