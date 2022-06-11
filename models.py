from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()  # SQLAlchemy를 사용해 데이터베이스 저장

class User(db.Model):  # 데이터 모델을 나타내는 객체 선언
    __tablename__ = 'user_table'  # 테이블 이름

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    following_list = db.Column(db.String(400))

    def __init__(self, userid, password, **kwargs):
        self.userid = userid
        self.set_password(password)
        self.following_list = ""

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def set_userid(self, userid):
        self.userid = userid
        
    def add_following(self, userid):
        if not self.following_list:
            self.following_list = userid
            return None
        temp = ('temp ' + self.following_list).split()
        temp.append(userid)
        temp.pop(0)
        self.following_list = list_to_string(temp)
        
    def remove_following(self, userid):
        if not self.following_list:
            return None
        temp = ('temp ' + self.following_list).split()
        temp.remove(userid)
        temp.pop(0)
        self.following_list = list_to_string(temp)
    
    def get_following(self):
        if not self.following_list:
            return None
        return self.following_list.split()


class Product(db.Model):
    __tablename__ = 'product_table'
    
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    keyword1 = db.Column(db.String(40), nullable=False)
    keyword2 = db.Column(db.String(40))
    keyword3 = db.Column(db.String(40))
    keyword4 = db.Column(db.String(40))
    keyword5 = db.Column(db.String(40))
    price = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(1000), nullable=False)
    purchased = db.Column(db.Boolean, nullable=False)
    
    def __init__(self, userid, title, keyword1, keyword2, keyword3, keyword4, keyword5, price, contact, picture, detail, **kwargs):
        self.userid = userid
        self.title = title
        self.keyword1 = keyword1
        self.keyword2 = keyword2
        self.keyword3 = keyword3
        self.keyword4 = keyword4
        self.keyword5 = keyword5
        self.price = price
        self.contact = contact
        self.picture = picture
        self.detail = detail
        self.purchased = False
        
    def set_purchased(self):
        self.purchased = not self.purchased
    
    
def list_to_string(str_list):
    result = ""
    if len(str_list) == 1:
        return str_list[0].strip()
    for s in str_list:
        result += s + " "
    return result.strip()