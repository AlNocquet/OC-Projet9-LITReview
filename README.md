# LITReview

## Overview

LITReview is a Django web application allowing users to create and read review requests ("tickets") and reviews, follow and block users, and manage their content via a clean, responsive interface.  
This project fully meets the OpenClassrooms P9 specification, with an emphasis on code readability, PEP8 compliance (max-line-length 120), and maintainability.

---

## Features

- **User accounts:** Sign up, login, logout, edit profile, delete account
- **Follow system:** Subscribe/unsubscribe to other users (social feed)
- **User blocking/unblocking:** Block or unblock users. Blocked users’ tickets and reviews are hidden from your feed, and you are also hidden from theirs.
- **Tickets:** Create and view review requests (optionally with image)
- **Reviews:** Write and read reviews on tickets, including from non-followers; orphan reviews are supported (see below)
- **Review visibility:** All reviews of your tickets are shown in your feed, including those written by non-followers and followers.
- **Feed:** Unified, reverse chronological feed:
    - Tickets are displayed with associated reviews grouped directly above the ticket (by date).
    - Orphan reviews (for tickets not visible in the feed) are also shown by date.
    - The **entire feed is strictly reverse chronological by item date**.
- **Responsive design:** Optimized for desktop, tablet, and mobile (browser adaptive view tested)
- **Password management:**
    - Change password from your user account page (while logged in)
    - Reset password by email if forgotten (console backend for dev)
- **Multi-user test data:** Pre-filled demo accounts with tickets, reviews, and follows

---

## Advanced features & future improvements

- **Notifications:** Display notifications for new posts/reviews since the last login (**planned improvement**)
- **Quick follow button in the feed:** Add a "Follow" button next to any non-followed user appearing in the feed (e.g., if they reply to you or a followed user) (**planned improvement**)

---

## Project structure

```text
OC-Projet9-LITReview/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── LITReview/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── context_processors.py
│   ├── templates/
│   ├── static/
│   ├── tests/
│   └── ...
├── locale/
├── media/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/AlNocquet/OC-Projet9-LITReview.git
    cd OC-Projet9-LITReview
    ```

2. **Create and activate a virtual environment**
    ```bash
    python -m venv env
    source env/bin/activate  # (Linux/Mac)
    env\Scripts\activate     # (Windows)
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply database migrations**
    ```bash
    python manage.py migrate
    ```

5. **(Optional) Load initial data**
    - Demo users are already present in the provided database, or you can create new accounts via the interface.

6. **Run the development server**
    ```bash
    python manage.py runserver
    ```

---

## Usage

- Access the site at [http://localhost:8000](http://localhost:8000)
- Log in with a demo account:
    - **AlN**, password: `AlNadmin@777`
    - **Olivier**, password: `Olivieradmin@777`
    - **Sauron**, password: `Sauronadmin@777`
- Or create your own account and test all features (tickets, reviews, follow/block, password management, etc.)

---

## Coding conventions / PEP8

- **Strict PEP8 compliance** across the entire codebase (flake8 OK project-wide).
- **max-line-length set to 120** for code readability and industry best practices in Django teams.
- Consistent indentation, spacing, and comments for a homogeneous codebase.

---

## Tests

- **Comprehensive test suite** (unit and integration) for forms, models, views, authentication, and all main features.
- Run all tests:
    ```bash
    python manage.py test
    ```
- **All tests must pass before any delivery.**
- Style check:
    ```bash
    flake8 .
    ```

---

## Responsive design

- The interface is tested and optimized for desktop, tablet, and mobile devices.
- All features are comfortably usable on any screen size.

---

## Author

Alice Nocquet