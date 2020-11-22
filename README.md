# yuarcuun-api
API backend for Yuarcuun (both website and mobile app)

Using Python 2 (for now...) and Flask

## Installation

Install required packages:
```
pip install -r requirements.txt
```
You will also need to install HFST and its Python API. On Ubuntu for example you can install the `python-libhfst` package.

## Running the server
Launch Flask server for development:
```
python api.py
```

## Deploy to Heroku
Add Heroku to the Git remote:
```
git remote add heroku git@heroku.com:yuarcuun.git
```
And push to Heroku:
```
git push heroku master
```
