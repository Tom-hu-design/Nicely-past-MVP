from app import db

class Users(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(50)) 
    media_directory = db.Column(db.String(150))
    account_type = db.Column(db.String(50))

    def __init__(self, username, password, media_directory, account_type):
        self.username = username
        self.password = password
        self.media_directory = media_directory
        self.account_type = account_type

class infos(db.Model):
    id = db.Column('info_id', db.Integer, primary_key = True)
    user_name = db.Column(db.String(100))
    demographic = db.Column(db.String(20)) 
    twitter = db.Column(db.String(50)) 
    language = db.Column(db.String(20)) 
    workstatus = db.Column(db.String(50)) 
    gender = db.Column(db.String(20)) 
    email = db.Column(db.String(50)) 

    def __init__(self, user_name, demographic, twitter, language, workstatus, gender, email):
        self.user_name = user_name
        self.demographic = demographic
        self.twitter = twitter
        self.language = language
        self.workstatus= workstatus
        self.gender = gender
        self.email = email

class user_tweets(db.Model):
    id = db.Column('user_tweet_id', db.Integer, primary_key = True)
    user_name = db.Column(db.String(50)) 
    Tweet_id = db.Column(db.String(20)) 
    content = db.Column(db.String(100)) 
    Anger = db.Column(db.String(10)) 
    Joy = db.Column(db.String(10)) 
    Optimism = db.Column(db.String(10)) 
    Sadness = db.Column(db.String(10)) 
    AveDailyScore = db.Column(db.String(10)) 
    Tweet_time = db.Column(db.String(50)) 

    def __init__(self, user_name, Tweet_id, content, Anger, Joy, Optimism, Sadness, AveDailyScore, Tweet_time):
        self.user_name = user_name
        self.Tweet_id = Tweet_id
        self.content = content
        self.Anger= Anger
        self.Joy = Joy
        self.Optimism = Optimism
        self.Sadness = Sadness
        self.AveDailyScore= AveDailyScore
        self.Tweet_time = Tweet_time

class Nicely_post(db.Model):
    id = db.Column('user_post_id', db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    file_name = db.Column(db.String(100))
    post_content = db.Column(db.String(100))
    media_directory = db.Column(db.String(100))
    post_time = db.Column(db.String(50))

    def __init__(self, username, file_name, post_content, media_directory, post_time):
        self.username = username
        self.file_name = file_name
        self.post_content = post_content
        self.media_directory = media_directory
        self.post_time = post_time

class Anonymous_post(db.Model):
    id = db.Column('user_post_id', db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    file_name = db.Column(db.String(100))
    post_content = db.Column(db.String(100))
    media_directory = db.Column(db.String(100))
    post_time = db.Column(db.String(50))

    def __init__(self, username, file_name, post_content, media_directory, post_time):
        self.username = username
        self.file_name = file_name
        self.post_content = post_content
        self.media_directory = media_directory
        self.post_time = post_time

class Counselor(db.Model):
    id = db.Column('counselor_id', db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    name = db.Column(db.String(100))
    language= db.Column(db.String(100))
    description = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    media_directory = db.Column(db.String(100))
    email = db.Column(db.String(100))
    number = db.Column(db.String(100))
    fee = db.Column(db.String(50))

    def __init__(self, username, name, gender, language, description, email, number, media_directory, fee):
        self.username = username
        self.name = name
        self.gender = gender
        self.language = language
        self.description = description
        self.email = email
        self.number = number
        self.media_directory = media_directory
        self.fee = fee

class Labels(db.Model):
    id = db.Column('info_id', db.Integer, primary_key = True)
    user_name = db.Column(db.String(100))
    label = db.Column(db.String(80)) 
    label_class = db.Column(db.String(50)) 

    def __init__(self, user_name, label, label_class):
        self.user_name = user_name
        self.label = label
        self.label_class = label_class
