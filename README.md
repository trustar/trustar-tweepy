# trustar-tweepy

An application that collects tweets and extracts malware names every week. 

Link: [https://ts-tweepy.herokuapp.com/](https://ts-tweepy.herokuapp.com/)

<hr>

#### Steps: 

1. Install Heroku
```
brew install heroku/brew/heroku
```

2. Login
```
heroku login
```

3. Clone the app
```
git clone https://github.com/trustar/trustar-tweepy.git
cd trustar-tweepy
pip install -r requirements.txt
```
(You can obtain your `requirements.txt` with the command `pip freeze > requirements.txt`.)

4. Create the app
```
heroku create ts-tweepy
heroku config:set FLASK_APP=dashapp.py
```
The name of the app should be unique across all the users on Heroku.
Your app will be deployed at `https://ts-tweepy.herokuapp.com/`.

5. Create a Procfile that calls unicorn with the command
```
web: gunicorn dashboard:server
```
The command `dashboard:server` is the same as calling `from dashboard import server`. 
`server` is the flask app. Heroku uses dynamic ports, make sure your app reads the port number from the environment with `int(os.environ.get('PORT')`.

6. Deploy app on Heroku
```
git push heroku master
```

7. Done! You're app should be running. For help or status, use `heroku logs --tail`.