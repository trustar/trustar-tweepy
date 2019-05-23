# README

This folder will collect Tweets for you up to a week old given a query.

**What you need:**
- You will need a `twitter.csv` file with the following information:
			- API key
            - API secret key
            - Access token
            - Access token secret
- You will also need a `queries` folder with `.txt` files. Each file should contain a search terms per line.

**How to run:**
- On your terminal type `python start_query.py >> queries.log`.

**What it does:**
This process will output your collected tweets in `.txt` file in a `json` format inside a folder named `output`. 
A `tweets.csv` file will get updated with all the tweets collected up to now.

**Extra:**
Twitter only allows to collect a week old tweets. If you wish to automate this process to collect tweets every week (Sunday 11:00:00 p.m., there is a `../crontab.txt` file provided with instructions that need to be run on the terminal.