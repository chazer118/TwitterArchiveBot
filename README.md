# ArchiveBot
**A bot for archiving tweets and associated media under a certain text query to an SQLite database.**

## REQUIREMENTS:<br/>
-python3<br/>
-tweepy api<br/>
-sqlite3<br/>
-urllib<br/>

All of the above can be installed using ```pip install PACKAGENAMEHERE```

**Twitter developer account:**<br/>
https://developer.twitter.com/en

## USE:<br/>
To use this bot you need to create a twitter developer account and submit an application (see Requirements for the link!). Open the ```main_sql.py``` script and input your twitter authentication credentials in their respective fields. To change the search query, change the ```textQuery``` variable. Save and exit the editor. Now just run the 'main_sql.py' script as you would any normal python script! It will create a database with the title as the search query you have entered and a media folder to store any media. **At the moment it only supports downloading of photos but video is on my to-do list!**
```
python3 main_sql.py
```

## ABOUT:<br/>
Currently there are two main scripts:
maincsv.py and mainsql.py. They use CSV and SQLite respectively for storing data. SQLite version is much more up to date. Currently it scans for any tweets under 'BLM Protests' and will store the tweets it finds as long as it doesn't already exist in the database (this is to reduce the database hundreds of thousands of retweets!). It stores the date the tweet was created, tweet id, time the tweet was archived, tweet content and the username of the author.

```mediadownloadtest.py``` is just a script I used while testing the media function before implementing. It's not needed but I left it in there.
