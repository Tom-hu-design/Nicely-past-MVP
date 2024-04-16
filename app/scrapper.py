from sqlalchemy import false
import tweepy
from app.SAModle import analysis
import pandas as pd
import numpy as np
import pytz

utc=pytz.UTC
atoken = "1461723003318898699-lExDJDsxfmLMeJdJfKC6gjtKsl4CFq"
atoken_secret = "zisHM6Dcp5c7caDlyRe8BbjotY9mEQZ3rk0lMQKZ02A5p"
ckey = "bUS1uGP1XULGqydcAkKTl1yvN"
ckecret = "Bwk2KYtjPRCegJ1BAXpEhPjiSMh7zu7WzjARnxzmDHWJjMqNjl"
btoken = "AAAAAAAAAAAAAAAAAAAAAHHhVwEAAAAAYrV5OoDlqXpXD8EDQXJEuVJS5Qk%3DAJHQOrwiCJReblQZ7OfA3K1kjn09md9RMhbZ2iRhHhq7ZX3Dh7"

print("Establishing connection...")
client = tweepy.Client(bearer_token=btoken,
                           consumer_key=ckey,
                           consumer_secret=ckecret,
                           access_token=atoken,
                           access_token_secret=atoken_secret,)

def getClient(Twittername, user_logged_in):
    user = client.get_user(username = Twittername)
    print("done establishment, fetching user id...")
    userID = user.data.id
    recentTweet = client.get_users_tweets(id = userID, max_results = 100, tweet_fields=['created_at'])
    print("id fetched, fetching past tweets...")
    tweetdata=recentTweet.data
    print("process completed, starting epoch 1...")
    results = []
    counter = 1
    del(userID, recentTweet)
    for tweet in tweetdata:
        obj = {}
        obj['id'] = tweet.id
        obj['user_name'] = user_logged_in
        obj['text'] = tweet.text
        obj['time'] = tweet.created_at
        number = 1
        print("Current Epoch " + str(counter))
        counter += 1
        for items in analysis(tweet.text):
            obj[f"sentiment{number}"] = items
            number += 1
        results.append(obj)
    del(tweetdata)
    df = pd.DataFrame (results, columns = ['id', 'user_name', 'text' ,'time', 'sentiment1', 'sentiment2', 'sentiment3', 'sentiment4'])
    return df

def twitter_verify(account):
    user = client.get_user(username = account)
    if (user.data == None):
        print("verify false")
        return False
    else:
        print("verify true")
        return True

def twitter_update(Twittername, user_logged_in, filter_time):
    user = client.get_user(username = Twittername)
    print("done establishment, fetching user id...")
    userID = user.data.id
    recentTweet = client.get_users_tweets(id = userID, max_results = 100, tweet_fields=['created_at'])
    print("id fetched, fetching past tweets...")
    tweetdata=recentTweet.data
    print("process completed, starting epoch 1...")
    results = []
    counter = 1
    del(userID, recentTweet)
    for tweet in tweetdata:
        # print("##################")
        # print(tweet.created_at)
        # print(utc.localize(filter_time))
        # print(tweet.created_at > utc.localize(filter_time))
        if (tweet.created_at > utc.localize(filter_time)):
            obj = {}
            obj['id'] = tweet.id
            obj['user_name'] = user_logged_in
            obj['text'] = tweet.text
            obj['time'] = tweet.created_at
            number = 1
            print("Current Epoch " + str(counter))
            counter += 1
            for items in analysis(tweet.text):
                obj[f"sentiment{number}"] = items
                number += 1
            results.append(obj)
        

    del(tweetdata)
    df = pd.DataFrame (results, columns = ['id', 'user_name', 'text' ,'time', 'sentiment1', 'sentiment2', 'sentiment3', 'sentiment4'])
    return df

# recentTweet = getClient()
# recentTweet.to_csv('results2.csv', header=True)
# print(recentTweet)

# recentTweet = getClient()
# number = 0
# for i in recentTweet:
#     number += 1
#     print(i, "| tweet count:", number)
