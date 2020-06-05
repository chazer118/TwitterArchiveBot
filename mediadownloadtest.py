import os
import sys
import tweepy
import time
import sqlite3
from sqlite3 import Error
import json
import wget

#ENTER YOUR TWITTER DEVELOPER CREDENTIALS HERE:
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

mediaURLs = []
textQuery = 'BLM Protests' #ENTER YOUR TEXT QUERY HERE!!
count = 100

global mediaCount

dbPath = ("db/" + textQuery + ".sqlite")
mediaPath = ("media/")

def main():
    #check if media folder exists
    if not os.path.exists(mediaPath):
        print("Media folder does not exist - will create folder at ~media/")
        os.makedirs(mediaPath)
        print("Media folder has been created.")
    getMediaURLs()

def getMediaURLs():
    try:
        #Pulling the individual tweets from the text query
        for tweet in api.search(q=textQuery, count=count, tweet_mode = 'extended'):

            #check for media in twwet
            if 'media' in tweet.entities:
                media_url = tweet.entities["media"][0]["media_url"]
                print("tweet contains media")
                if(media_url not in mediaURLs):
                    mediaURLs.append(tweet.entities["media"][0]["media_url"])
                else:
                    print("duplicate!")

    except BaseException as e:
        print('failed on_status,',str(e))
        time.sleep(3)

    downloadMedia()

def downloadMedia():
    try:
        for media_url in mediaURLs:
            print("Fetcing URL: ", str(media_url))
            wget.download(media_url, out=mediaPath)

    except BaseException as e:
            print('ERROR RETRIEVING MEDIA: ',str(e))
            time.sleep(3)



if __name__=='__main__':
    while True:
        main()

    except KeyboardInterrupt:
        os.system('clear')
        time.sleep(1)
        print(f"{mediaCount} tweets have been added to the database.")
        print(f"{mediaSkipCount} tweets have been skipped to avoid RTs of the same content.")
        time.sleep(1)
        print("EXITING...")
        sys.exit()
