# LITReview

Django web app that allows users to request or publish reviews on books or articles, and to view a personalized feed based on followed users' activity.


## Technology

- Python 3.12+
- Django 5.1
- HTML/CSS (Django templates)
- SQLite (default DB via Django ORM)
- Pillow (image support)


## Author

Alice Nocquet


## Environment setup and launch

Use the following commands to create a virtual environment, install dependencies, and run the application:

```bash
git clone https://github.com/AlNocquet/OC-Projet9-LITReview.git
cd OC-Projet9-LITReview

python -m venv env                   # Create virtual environment
env\Scripts\activate                 # On Windows
# OR
source env/bin/activate             # On macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Once the server is running, open the application in your browser at:
http://127.0.0.1:8000/


## USAGE

The platform allows users to:

- Publish or request reviews of books or articles (called "tickets")
- Write a review for any ticket (self-created or by other users)
- Follow or unfollow other users
- Block or unblock users to prevent interactions
- Access a personalized feed showing:
  - Their own posts
  - Posts from followed users (tickets and reviews)
- Manage their profile and delete their account if desired

All main features require user authentication.  
The home page provides access to registration and login.


## Structure

- **Home page**: User registration and login
- **Feed**: Personalized feed of reviews and tickets
- **Posts**: Create or respond to review requests
- **User management**: Update profile, logout, delete account
- **Follow system**: Subscribe to or unfollow other users on the platform


## PEP8 Compliance


Code formatting follows PEP8 standards.

To configure Flake8, create a `setup.cfg` file with:

```
[flake8]
exclude =
    .git,
    .venv,
    env,
    __pycache__,
    .vscode
max-line-length = 119
max-complexity = 10
```

To generate an HTML flake8 report:

```bash
flake8 --format=html --htmldir=flake-report
```
