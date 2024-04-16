from requests import delete
from app import app, db
from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime
from sqlalchemy import create_engine, false, true
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app.scrapper import getClient, twitter_verify, twitter_update
from app.visualization import process, processtext, graphplot
from app.SAModle import analysis
from app.wtforms import InfoForm, RegistrationForm, LoginForm, ViewForm, RegisterForm, DeletePost
import pytz
from wtforms.validators import ValidationError
import numpy as np

from app.models import Users, Nicely_post, infos, user_tweets, Counselor, Anonymous_post, Labels
db.create_all()
engine = create_engine('sqlite:///app/userdata.sqlite3', echo=False)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
utc=pytz.UTC

class StatusDenied(Exception):
    pass

@app.errorhandler(StatusDenied)
def redirect_on_status_denied(error):
    return redirect(url_for('login'))

def currently_logged_in():
    user = session.get("user_logged_in")
    if user:
        return
    else:
        flash('You are currently logged out')
        raise StatusDenied

@app.route('/meditation')
def meditation():
    return render_template('meditation.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    registration_form = RegistrationForm()
    # user_logged_in = session.get("user_logged_in")
    # user_active = Users.query.filter_by(username = user_logged_in).first()
    # if user_active:
    #     return redirect("/dashboard", code = 302)

    if request.method == 'POST':
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file = registration_form.post_image.data
        # if Users.query.filter_by(username = registration_form.username.data).first():
        #     flash('This username is already taken, please choose another username')
        #     return redirect('/signup')
        # else:
            username = registration_form.username.data
            password = registration_form.password.data
            account_type = registration_form.account_type.data

            filename_secure = secure_filename(file.filename)
            filename, file_extension = os.path.splitext(filename_secure)
            file.filename = str(time) + filename + file_extension
            user_directory = "/post_videos/"
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+ user_directory, file.filename))
            media_path = "/static/upload" + user_directory + file.filename

            user = Users(username, password, media_path, account_type)
            session['user_logged_in'] = username

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('personalinfo', data = username))
    return render_template("signup.html", form = registration_form)

@app.route('/personal-info', methods = ['GET', 'POST'])
def personalinfo():
    info_form = InfoForm()
    user_logged_in = session.get("user_logged_in")
    if request.method == 'POST':
        if twitter_verify(info_form.twitter_username.data) == False:
            print("twitter false")
            flash('Please enter a correct twitter username without "@" under your profile')
            redirect('/personal-info')
        else: 
            print("twitter true")
            info = infos(user_name = user_logged_in, demographic = info_form.demographic.data, twitter = info_form.twitter_username.data, language = info_form.first_language.data,
                         workstatus = info_form.work_status.data, gender = info_form.gender.data, email = info_form.email.data)
            db.session.add(info)
            print(f"added to the queue, Now fetching social data")
            twitter_name = info_form.twitter_username.data
            resultReturned = getClient(twitter_name, user_logged_in)
            graphplot(resultReturned)
            db.session.commit()
            flash('Records were successfully added')
            redirect('/dashboard')
    return render_template("personalinfo.html", form = info_form)

@app.route('/')
def main():
    return redirect("https://nicely.framer.website/")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = LoginForm()
    user_logged_in = session.get("user_logged_in")
    user_active = Users.query.filter_by(username = user_logged_in).first()
    if user_active:
        return redirect("/dashboard", code = 302)

    if request.method == 'POST':
        user = Users.query.filter_by(username = login_form.username.data).first()
        if user and user.password == login_form.password.data:
            session['user_logged_in'] = login_form.username.data
            return redirect(url_for('dashboard'))
        else:
            flash('invalid password or username, please create a new account if you do not have a existing one')
    return render_template("login.html", form = login_form)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop("user_logged_in", None)
    flash('you are now logged out')
    return redirect(url_for('info'))

def snapshot(data):
    if len(data) > 0:
        result = []
        a = range(1,5)
        for num in a:
            lst = [float(e[num]) for e in data]
            value = round(100 * sum(lst)/len(lst), 2)
            result.append(value)
        return result
    else:     
        return "not available yet, make your first entries to start!"

def process_pie(list):
    result = []
    a = range(0,6)
    print(len(list))

    if len(list) == 1:
        for num in a:
            lst = list[0][num]
            result.append(lst)
    else:
        for num in a:
            lst = list[num]
            result.append(lst)

    return result

@app.route('/update', methods = ['GET', 'POST'])
def update():
    currently_logged_in()
    user_logged_in = session.get("user_logged_in")
    entry_verify = infos.query.filter_by(user_name = user_logged_in).first()
    verify = user_tweets.query.filter_by(user_name = user_logged_in).order_by(user_tweets.Tweet_time.desc()).first()
    update = twitter_update(entry_verify.twitter, user_logged_in, datetime.strptime(verify.Tweet_time, '%Y-%m-%d %H:%M:%S'))
    # print("$$$$$$$$$")
    # print(update.empty)
    if not update.empty:
        graphplot(update)
        db.session.commit()
    return redirect('/dashboard')

def label_clean(array):
    final_array = []
    for e in array:
        new_e = e[5 : : ]
        raw_e = new_e[:-9:]
        final_array.append(raw_e)
    return final_array

def dashboard_results(user_logged_in, query_num_input):
        raw = pd.read_sql ('SELECT user_name, Anger, Joy, Optimism, Sadness, AveDailyScore, Tweet_time FROM user_tweets ORDER BY Tweet_time;', engine)
        next = raw.loc[raw["user_name"] == user_logged_in]
        query_num = query_num_input
        new = next.iloc[-query_num:]
        new['AveDailyScore'] = pd.to_numeric(new['AveDailyScore'])
        percent_raw = len(new.query("AveDailyScore > 80"))/query_num*100
        percent_positive = round(percent_raw)
        data = new.values.tolist()
        numbers = list(range(0, 6))
        pie = process_pie(data)
        radar = snapshot(data)
        labels = [row[6] for row in data]
        input_labels = label_clean(labels)
        values = [float(row[5]) for row in data]
        values_pie = [[row[1], row[2], row[3], row[4]] for row in pie]

        timeframe = []
        for i in next['Tweet_time']:
            timeframe.append(i.split(' ')[1].split(':')[0])
            y = np.zeros(25)
            for i in range(2,26,2):
                count = 0
                for j in timeframe:
                    if int(j) == i or int(j) == i-1:
                        count += 1
                y[i] = count

        clock = pd.DataFrame(y,columns=['count']).iloc[2::2, :]
        clock_graph = clock['count'].to_list()

        if len(data) > 0:
            EmotionScore = round(sum(values)/len(data), 2)
            if EmotionScore > 80.0:
                risk = "Low"
            if EmotionScore < 60.0:
                risk = "High"
            if EmotionScore < 80.0 and EmotionScore > 60.0:
                risk = "Medium"
        else:
            EmotionScore = "not available yet, make your first entries to start!"

        return user_logged_in, EmotionScore, input_labels, values, radar, values_pie, numbers, risk, percent_positive, clock_graph

def query_labels(username):
    labels_dic = []
    if Labels.query.filter_by(user_name = username).first():
        labels_raw = Labels.query.filter_by(user_name = username).limit(9).all()
        for e in labels_raw:
            labels_dic.append(e.label)
    else:
        labels_dic = ["example","example","example","example","example","example","example","example"]
    return labels_dic


@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    currently_logged_in()
    user_logged_in = session.get("user_logged_in")
    verify = user_tweets.query.filter_by(user_name = user_logged_in).order_by(user_tweets.Tweet_time.desc()).first()
    profile_pic_row = Users.query.filter_by(username = user_logged_in).first()
    profile_directory = profile_pic_row.media_directory
    labels_dic = query_labels(user_logged_in)
    labels_dic_1 = labels_dic[:5]
    labels_dic_2 = labels_dic[6:]


    if verify:
        if request.method == 'POST':
            query_field = int(request.form['query_input'])
            func_results = dashboard_results(user_logged_in, query_field)
        else:
            query_field = 30
            func_results = dashboard_results(user_logged_in, query_field)
        return render_template("dashboard.html", usr = user_logged_in, EmotionScore = func_results[1], labels = func_results[2], 
        values = func_results[3], radar = func_results[4], values_pie = func_results[5], numbers = func_results[6], risk = func_results[7], 
        percent_positive = func_results[8], query_field = query_field, media_dic = profile_directory, clock_graph = func_results[9], labels_dic_1 = labels_dic_1,
        labels_dic_2 = labels_dic_2, labels_dic = labels_dic[5])
    else:
        flash("Please associate your account with valid twitter account")
        return redirect("/personal-info")
    
    

    

@app.route('/scoredetail', methods = ['GET', 'POST'])
def scoredetail():
    currently_logged_in()
    user_logged_in = session.get("user_logged_in")
    labels_dic = query_labels(user_logged_in)
    labels_dic_1 = labels_dic[:5]
    labels_dic_2 = labels_dic[6:]
    profile_pic_row = Users.query.filter_by(username = user_logged_in).first()
    profile_directory = profile_pic_row.media_directory
    resultsback = user_tweets.query.filter_by(user_name = user_logged_in).limit(100).all()
    total = len(resultsback)
    return render_template("scoredetail.html", usr = user_logged_in, data = resultsback, total = total, media_dic = profile_directory, labels_dic_1 = labels_dic_1,
        labels_dic_2 = labels_dic_2, labels_dic = labels_dic[5])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/delete_post', methods = ['GET', 'POST'])
def delete_post():
    currently_logged_in()

    form_delete = DeletePost()
    if request.method == 'POST':
        delete_method = form_delete.post_number.data
        entry = Nicely_post.query.filter_by(id = delete_method).first()
        user = session.get("user_logged_in")
        if entry.username == user:
            db.session.delete(entry)
            db.session.commit()
    return redirect('view')

@app.route('/view', methods = ['GET', 'POST'])
def view():
    user_logged_in = session.get("user_logged_in")
    labels_dic = query_labels(user_logged_in)
    labels_dic_1 = labels_dic[:5]
    labels_dic_2 = labels_dic[6:]
    view_form = ViewForm()
    form_delete = DeletePost()
    currently_logged_in()
    profile_pic_row = Users.query.filter_by(username = user_logged_in).first()
    profile_directory = profile_pic_row.media_directory
    if request.method == 'POST':
        print("post complete")
        file = view_form.post_image.data

        if allowed_file(file.filename):
                print("file allowed")
            # if len(file.read()) < 1048576:
                posttext = view_form.post_content.data
                checkStatus = view_form.post_anonymously.data
                print(checkStatus)

                databack = analysis(posttext)
                scoredetail = process(databack)
                Avescore = processtext(scoredetail)

                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename_secure = secure_filename(file.filename)
                filename, file_extension = os.path.splitext(filename_secure)
                file.filename = str(time) + filename + file_extension
                user_directory = "/post_videos/"
                file.save(os.path.join(app.config['UPLOAD_FOLDER']+ user_directory, file.filename))
                media_path = "/static/upload" + user_directory + file.filename
                if checkStatus == True:
                    print("check status true")
                    post = Nicely_post("Anonymous", filename, posttext, media_path, time)
                    post_anonymous = Anonymous_post(user_logged_in, filename, posttext, media_path, time)
                    
                    db.session.add(post, post_anonymous)
                else:
                    print("check status false")
                    post = Nicely_post(user_logged_in, filename, posttext, media_path, time)
                    db.session.add(post)

                entry = user_tweets(user_logged_in, "post_id", posttext, scoredetail[0], scoredetail[1], scoredetail[2], scoredetail[3], Avescore, time)
                    
                db.session.add(entry)
                db.session.commit()
            # else:
            #     flash("The file type you are uploading is too big, please keep the image size under 1MB")
        else:
            flash("The file type you are uploading is not supported")

    user_logged_in = session.get("user_logged_in")
    pastposts = engine.execute('SELECT * FROM Nicely_post ORDER BY user_post_id DESC LIMIT 30;')
    if pastposts :
        return render_template("view.html", posts = pastposts, usr = user_logged_in, filled = True, form = view_form, form_delete = form_delete, media_dic = profile_directory,labels_dic_1 = labels_dic_1,
        labels_dic_2 = labels_dic_2, labels_dic = labels_dic[5])
    return render_template("view.html", usr = user_logged_in, form = view_form, media_dic = profile_directory, labels_dic_1 = labels_dic_1,
        labels_dic_2 = labels_dic_2, labels_dic = labels_dic[5])

@app.route('/explained')
def explained():
    user_logged_in = session.get('user_logged_in')
    return render_template("explained.html", usr = user_logged_in)

@app.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    user_logged_in = session.get('user_logged_in')
    emojilist = ["😁","😄","😐","🙁","😔","😡", "😬", "😍", "😎", "😴", "🤒", "🤯"]
    emoji_data = pd.read_csv("app/static/csv/emoji_Score.csv")

    if request.method == 'POST':
        emoji = request.form.get('emoji')
        entry = request.form.get('entry')

        position = emojilist.index(emoji)
        emoji_results = emoji_data.iloc[position]
        time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        text_score = analysis(entry)
        scoredetail = process(text_score)
        Avescore = processtext(scoredetail)


        emoji_input = user_tweets(user_logged_in, "emoji", emoji, emoji_results[1], emoji_results[2], emoji_results[3], emoji_results[4], emoji_results[5], time)
        db.session.add(emoji_input)
        text_input = user_tweets(user_logged_in, "quiz", entry, scoredetail[0], scoredetail[1], scoredetail[2], scoredetail[3], Avescore, time)
        db.session.add(text_input)
        db.session.commit()

        return redirect('/dashboard')

    return render_template("quiz.html", usr = user_logged_in, emojis = emojilist)

@app.route('/chat_signup', methods = ['GET', 'POST'])
def chat_signup():
    register_form = RegisterForm()
    currently_logged_in()
    if request.method == 'POST':
        username = session.get("user_logged_in")
        name = register_form.register_name.data
        description = register_form.work_experience.data
        fee = register_form.cost.data
        language = register_form.language_preferred.data
        number = register_form.register_number.data
        gender = register_form.register_gender.data
        email = register_form.register_email.data
        file = register_form.register_image.data

        if allowed_file(file.filename):
            filename_secure = secure_filename(file.filename)
            filename, file_extension = os.path.splitext(filename_secure)
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.filename = str(time) + filename + file_extension
            user_directory = "/post_videos/"
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+ user_directory, file.filename))

            media_path = "/static/upload" + user_directory + file.filename
            people = Counselor(username, name, gender, language, description, email, number, media_path, fee)

            db.session.add(people)
            db.session.commit()

        else:
            flash("The file type you are uploading is not supported")

    return render_template("chat_signup.html", form = register_form)

@app.route('/connect')
def chat():
    user_logged_in = session.get('user_logged_in')
    data = Counselor.query.limit(20).all()
    if data :
        return render_template("chat.html", people = data, usr = user_logged_in)
    return render_template("chat.html", usr = user_logged_in)

@app.route('/info')
def info():
    return render_template("info.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/blog')
def blog():
    return render_template("blog.html")

adj_dict = ["Adaptable", "Adventurous", "Passionate", "Diligent", "Humble", "Courageous", "Efficient", "Enchanting", "Generous", 
    "Magnetic", "Likeable", "Sincere", "Lovely", "Trustworthy", "Resourceful", "Well-read", "Wise", "Zealous", "Resilient", 
    "Reliable", "Determined", "Strong", "Stupendous", "Exceptional", "Generous", "Kind", "Persuasive", "Vivacious", "Witty", "Extra-ordinary",
    "Divine", "Breathtaking", "Flawless", "Magnificent", "Lively", "Versatile", "Amazing", "Fun-loving", "Well-travelled", "Outgoing", 
    "Amicable", "Friendly", "Perseverant", "Enthusiastic", "Affectionate", "Thoughtful", "Modest", "Considerate", "Courteous"]

hob_dict = ["Dance", "Writing", "Learning", "Cooking", "Gardening", "Handicraft", "Vlogging", "Gaming", "Board Game", "Shopping", 
    "Drawing", "Chess", "Brewing", "Photography", "Singing", "Woodworking", "Painting", "Glassblowing", "Beekeeping", "Hunting", "Genealogy",
    "Exercise", "Sewing", "Knitting", "Design", "Acting", "Crochet", "Football", "Guitar", "Sports", "Music", "Investment", "Pottery", 
    "Toys", "Filmmaking", "Jigsaw", "Puzzle", "programming", "Carpenter", "Darts", "Running", "Snowboarding", "Archery", "Model", "building"
    , "Parachuting", "Wood Carving", "Marketing", "Internet", "Metalworking", "Tourism", "Advertising", "Dancing"]

goals_list = ["Run a half marathon", "Follow a vegan diet", "Start a business", "Spend more time with family", "Steady passive income",
    "Own your dream home", "Own your dream car", " make a positive impact", "Conquer my fears", "Master a second language", "Rekindle an old relationship",
    "Sleep better", "Mentor someone", "Fall in love", "Take more risks", "Let go of the past", "Learn more", "Time management", "Become a better spouse",
    "better balance", "Travel more", "Meet new people", "Experience new culture", "New job", "Financial Stability", "Earn a million dollars"]

@app.route('/labels', methods = ['GET', 'POST'])
def labels():
    if request.method == 'POST':
        raw_str_1 = request.form.getlist('query_int_1')[0]
        list_1 = list(raw_str_1.split(","))
        raw_str_2 = request.form.getlist('query_int_2')[0]
        list_2 = list(raw_str_2.split(","))
        raw_str_3 = request.form.getlist('query_int_3')[0]
        list_3 = list(raw_str_3.split(","))


        user_logged_in = session.get("user_logged_in")
        for e in list_1:
            entry_1 = Labels(user_name = user_logged_in, label = e, label_class = "adj")
            db.session.add(entry_1)
        for e in list_2:
            entry_2 = Labels(user_name = user_logged_in, label = e, label_class = "hob")
            db.session.add(entry_2)
        for e in list_3:
            entry_3 = Labels(user_name = user_logged_in, label = e, label_class = "goal")
            db.session.add(entry_3)

        db.session.commit()
        return redirect('/dashboard')
    return render_template("labels.html", adj_dict = adj_dict, hob_dict = hob_dict, goals_list = goals_list)
