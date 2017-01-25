# Hanabi
### Deployment

* Clone the repository
* Install the dependencies: `pip install -r requirements.txt`
* Set the db access key: eg `mysql://user:pass@host/db`
* Create the tables: 
    -`python manage.py shell`
    -`db.create_all()`