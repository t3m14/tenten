
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
        db.create_tables([User, Like])

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
