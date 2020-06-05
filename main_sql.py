#Author: chaz
#Date: 02/06/20
#Description: A program to search Twitter for content related to a specified text query.

import os
import sys
import tweepy
import time
from datetime import datetime
import sqlite3
from sqlite3 import Error
import urllib

#ENTER YOUR TWITTER DEVELOPER CREDENTIALS HERE:
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
print("Connection to Tweepy API successful!")

tweetCount = 0
tweetSkipCount = 0
mediaCount = 0
mediaSkipCount = 0

#tweepy setup stuff...
tweets = []
mediaURLs = []
textQuery = 'BLM Protests' #ENTER YOUR TEXT QUERY HERE!!
count = 100

#db and media storage paths:
dbPath = ("db/" + textQuery + ".sqlite")
mediaPath = ("media/")

def create_connection(path):
    global conn
    conn = None
    try:
        conn = sqlite3.connect(path)
        print("Connection to SQLite Database successful!")

    except Error as e:
        print(f"The error '{e}' occurred. Please check the directory 'db' exists and is in the same folder as this script!")

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def searchTwitter(): #not needed anymore.
    try:
        #Pulling the individual tweets from the text query
        for tweet in api.search(q=textQuery, count=count, tweet_mode='extended'):
            # Adding tweets to a list that contains all tweets
            tweets.append((tweet.created_at, tweet.id, tweet.full_text, tweet.user))
            print(tweet.created_at, tweet.text)

    except BaseException as e:
        print('failed on_status,',str(e))
        time.sleep(3)

    #print(tweets)

def insertTweetIntoTable(conn):

    global tweetCount #ensuring we can access these variables
    global tweetSkipCount
    global containsPhoto

    try:
        #Pulling the individual tweets from the text query
        for tweet in api.search(q=textQuery, count=count, tweet_mode = 'extended'):

            global tweetId
            global typeOfContent

            date = str(tweet.created_at)
            dateAdded = str(time.time())
            tweetId = tweet.id
            content = tweet.full_text
            user = tweet.user.name
            try:
                containsPhoto = ([medium["type"] == "photo" for medium in tweet.entities["media"]])
            except:
                containsPhoto = False

                #print("TWEET DOES NOT CONTAIN MEDIA")

            sqlite_insert_with_param = """INSERT or IGNORE INTO tweet (date, dateAdded, tweetId, content, user) VALUES (?, ?, ?, ?, ?);"""

            data_tuple = (date, dateAdded, tweetId, content, user)

            c = conn.cursor()
            c.execute("""SELECT content FROM tweet WHERE content=?""", (content,))

            exists = c.fetchall()
            #print(exists)

            if exists:
                #print("TWEET ALREADY EXISTS IN DB: SKIPPING... (most likely a RT)")
                tweetSkipCount = tweetSkipCount + 1
            elif not exists:
                conn.execute(sqlite_insert_with_param, data_tuple)
                conn.commit()
                #print("Data inserted into tweet table")
                tweetCount = tweetCount + 1



            #check if tweet contains photo...
            if containsPhoto:
                #print("TWEET CONTAINS PHOTO")
                media_url = (tweet.entities["media"][0]["media_url"])
                typeOfContent = 'PHOTO'
                getMediaURLs(media_url, tweet)
            else:
                #print("TWEET DOES NOT CONTAIN MEDIA")
                typeOfContent = 'NONE'

    except Error as e:
        #tweet must not have media...
        #print("(TWEET MOST LIKELY DOES NOT CONTAIN MEDIA): ",str(e))
        pass

    except BaseException as e:
        print('failed on_status,',str(e))
        time.sleep(3)

def getMediaURLs(media_url, tweet):
    global mediaSkipCount
    try:
        if(media_url not in mediaURLs):
            mediaURLs.append(media_url)
            #print("Adding URL to MEDIAURLs list")
            downloadMedia(tweet)
        else:
            #print("duplicate!")
            mediaSkipCount = mediaSkipCount + 1

    except Error as e:
        print('failed on_status,',str(e))
        time.sleep(3)

def downloadMedia(tweet):
    global mediaCount
    global date
    global dateAdded
    global tweetId
    global user
    global typeOfContent

    try:
        for media_url in mediaURLs:
            #print("Fetcing URL: ", str(media_url))
            global fileName
            fileName = (str(tweetId) + ".jpg")
            output = mediaPath + fileName
            urllib.request.urlretrieve(media_url, output)
            #print(f"{fileName} has been downloaded!")

            if os.path.exists(output):
                mediaCount = mediaCount + 1
                insertMediaToTable(tweet)

            else:
                pass

    except Error as e:
            print('ERROR RETRIEVING MEDIA: ',str(e))
            time.sleep(3)

def insertMediaToTable(tweet):
    date = str(tweet.created_at)
    dateAdded = str(time.time())
    tweetId = tweet.id
    user = tweet.user.name

    sqlite_insert_with_param = """INSERT or IGNORE INTO media (date, dateAdded, tweetId, user, typeOfContent, fileName) VALUES (?, ?, ?, ?, ?, ?);"""

    data_tuple = (date, dateAdded, tweetId, user, typeOfContent, fileName)

    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    #print("Data inserted into media table")

def main():

    #check if media folder exists
    if not os.path.exists(mediaPath):
        print("Media folder does not exist - will create folder at ~media/")
        os.makedirs(mediaPath)
        print("Media folder has been created.")

    sql_create_tweet_table = """CREATE TABLE IF NOT EXISTS tweet (
                                        date text PRIMARY KEY,
                                        dateAdded text,
                                        tweetId integer,
                                        content text,
                                        user text
                                    );"""
    sql_create_media_table = """CREATE TABLE IF NOT EXISTS media (
                                        date text PRIMARY KEY,
                                        dateAdded text,
                                        tweetId integer,
                                        user text,
                                        typeOfContent text,
                                        fileName text
                                );"""
    #create a db connection
    conn = create_connection(dbPath)

    #create tables
    if conn is not None:
        #create tweet table
        create_table(conn, sql_create_tweet_table)

        #create media table
        create_table(conn, sql_create_media_table)
    else:
        print("ERROR: Cannot create the database connection.")

    while True:
        insertTweetIntoTable(conn)

    conn.close()

if __name__ == '__main__':
    startTime = datetime.now()
    try:
        main()

    except KeyboardInterrupt:
        os.system('clear')
        time.sleep(1)
        now = datetime.now()
        upTime = now - startTime
        print(f"Uptime: {upTime}")
        #BROKEN AT THE MOMENT....
        print(f"{tweetCount} tweets have been added to the database.")
        print(f"{tweetSkipCount} tweets have been skipped to avoid RTs of the same content.")
        print(f"{mediaCount} pieces of media have been added to the database.")
        print(f"{mediaSkipCount} pieces of media have been skipped to avoid duplicates.")
        time.sleep(1)
        print("EXITING...")
        sys.exit()
