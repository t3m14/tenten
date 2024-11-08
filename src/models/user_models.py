from peewee import *
from datetime import datetime

db = SqliteDatabase('dating_app.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    subscription_status = BooleanField(default=False)
    likes_count = IntegerField(default=0)
    last_like_reset = DateTimeField(default=datetime.now)

class Like(BaseModel):
    sender = ForeignKeyField(User, backref='sent_likes')
    receiver = ForeignKeyField(User, backref='received_likes')
    timestamp = DateTimeField(default=datetime.now)
    is_new = BooleanField(default=True)

def create_tables():
    with db:
        db.create_tables([User, Like], safe=True)

def reset_daily_likes():
    today = datetime.now().date()
    User.update(likes_count=0, last_like_reset=datetime.now()).where(
        (User.last_like_reset.date() < today) & (User.likes_count > 0)
    ).execute()

def send_like(sender_id, receiver_id):
    sender = User.get(User.user_id == sender_id)
    receiver = User.get(User.user_id == receiver_id)

    if sender.likes_count >= 10 and sender.last_like_reset.date() == datetime.now().date():
        return False
    if sender == receiver:
        return False
        
    existing_like = Like.select().where(
        (Like.sender == sender) & 
        (Like.receiver == receiver)
    ).exists()
    
    if existing_like:
        return False
        
    Like.create(sender=sender, receiver=receiver)
    sender.likes_count += 1
    sender.save()
    return True
    
def get_received_likes(user_id):
    return (Like
            .select()
            .where(Like.receiver == user_id)
            .order_by(Like.timestamp.desc()))

def get_new_likes_count(user_id):
    return Like.select().where((Like.receiver == user_id) & (Like.is_new == True)).count()

def mark_likes_as_seen(user_id):
    Like.update(is_new=False).where((Like.receiver == user_id) & (Like.is_new == True)).execute()

def get_user_info(user_id):
    try:
        user = User.get(User.user_id == user_id)
        return {
            'user_id': user.user_id,
            'username': user.username,
            'subscription_status': user.subscription_status,
            'likes_count': user.likes_count,
            'last_like_reset': user.last_like_reset
        }
    except User.DoesNotExist:
        return None

def create_user(user_id, username=None):
    return User.get_or_create(user_id=user_id, defaults={'username': username})[0]
def update_user(user_id, **kwargs):
    query = User.update(**kwargs).where(User.user_id == user_id)
    return query.execute()

def delete_user(user_id):
    query = User.delete().where(User.user_id == user_id)
    return query.execute()
