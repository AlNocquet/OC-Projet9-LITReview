# LITReview

Django web app that allows users to request or publish reviews on books or articles, and to view a personalized feed based on followed users' activity.



## Technology

Python, Django, HTML/CSS



## Author

Alice Nocquet



## Environment setup and launch

Use the following commands to create a virtual environment, install dependencies, and run the application:

```bash
$ git clone https://github.com/AlNocquet/OC-Projet9-LITReview.git
$ cd OC-Projet9-LITReview
$ python3 -m venv env                # On Windows: python -m venv env
$ source env/bin/activate            # On Windows: env\Scripts\activate
$ pip install -r requirements.txt
$ python manage.py runserver
```

Then open your browser at: [http://127.0.0.1:8000](http://127.0.0.1:8000)



## USAGE

The platform allows users to:

- Publish or request reviews of books or articles (tickets)
- Write a review for any ticket (self-created or by others)
- Follow or unfollow other users
- Access a personalized feed showing:
  - Their own posts
  - Posts from followed users (tickets and reviews)
- Manage their profile and delete their account

Users must be authenticated to access the main features. A homepage offers registration and login.



## Structure

- **Home page**: Sign up / Log in
- **Feed**: Personalized feed of reviews and tickets
- **Posts**: Create or respond to review requests
- **User management**: Profile update, logout, account deletion
- **Follow system**: Subscribe to or unfollow other users on the platform



## PEP8

Code formatting follows PEP8 standards.

Create a `setup.cfg` file with:

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
