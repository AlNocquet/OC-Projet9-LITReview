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

OC-Projet9-LITReview/
├── config/
│ ├── settings.py
│ ├── urls.py
│ └── ...
├── LITReview/
│ ├── models.py
│ ├── views.py
│ ├── forms.py
│ ├── context_processors.py
│ ├── templates/
│ ├── static/
│ ├── tests/
│ └── ...
├── locale/
├── media/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md

---

## Installation

1. **Clone the repository**
    ```bash
    git clone <repo-url>
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

Project developed for OpenClassrooms P9 ("Book review application, Goodreads style").
Contact for code review or job opportunities.

---

# LITReview (FR)

## Présentation

LITReview est une application web Django permettant de créer et consulter des demandes de critiques (“tickets”) et des critiques, de suivre ou bloquer d’autres utilisateurs, et de gérer ses contenus via une interface responsive.  
Le projet respecte le cahier des charges OpenClassrooms P9 : fonctionnalités complètes, lisibilité du code (PEP8, ligne max 120), et maintenabilité.

---

## Fonctionnalités

- **Comptes utilisateur :** inscription, connexion, déconnexion, modification du profil, suppression de compte
- **Système d’abonnements :** suivre/désabonner d’autres utilisateurs (fil social)
- **Blocage/déblocage d’utilisateur :** possibilité de bloquer/débloquer un utilisateur. Les tickets et critiques des utilisateurs bloqués sont masqués de votre flux, et vous l’êtes aussi pour eux.
- **Tickets :** créer et afficher des demandes de critique (image facultative)
- **Critiques :** écrire et lire des critiques sur tickets, y compris celles faites par des non-suivis ; les reviews orphelines sont gérées (voir ci-dessous)
- **Visibilité des critiques :** toutes les critiques faites sur vos tickets apparaissent dans votre flux, qu’elles proviennent de suivis ou de non-suivis.
- **Flux :** fil unifié antéchronologique :
    - Les tickets sont affichés avec les critiques associées regroupées juste au-dessus (par date)
    - Les reviews orphelines (liées à des tickets non visibles dans le flux) sont aussi affichées par date
    - **L’ensemble du flux est strictement antéchronologique sur la date de chaque élément**
- **Responsive :** optimisé desktop, tablette, mobile (testé via vues adaptatives navigateur)
- **Gestion du mot de passe :**
    - Modifier son mot de passe via l’espace utilisateur (connecté)
    - Réinitialiser son mot de passe par mail en cas d’oubli (console backend pour dev)
- **Comptes de test multi-utilisateurs :** utilisateurs pré-remplis avec tickets, critiques et abonnements

---

## Fonctionnalités avancées et axes d’amélioration

- **Notifications :** affichage de notifications pour signaler les nouveaux posts/critiques depuis la dernière connexion (**à développer**)
- **Bouton “suivre” rapide dans le flux :** ajout d’un bouton “Suivre” à côté de tout utilisateur non-suivi apparaissant dans le flux (ex : s’il répond à vous ou à un abonné) (**à développer**)

---

## Structure du projet

OC-Projet9-LITReview/
├── config/
│ ├── settings.py
│ ├── urls.py
│ └── ...
├── LITReview/
│ ├── models.py
│ ├── views.py
│ ├── forms.py
│ ├── context_processors.py
│ ├── templates/
│ ├── static/
│ ├── tests/
│ └── ...
├── locale/
├── media/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md

---

## Installation

1. **Cloner le dépôt**
    ```bash
    git clone <repo-url>
    cd OC-Projet9-LITReview
    ```

2. **Créer et activer un environnement virtuel**
    ```bash
    python -m venv env
    source env/bin/activate  # (Linux/Mac)
    env\Scripts\activate     # (Windows)
    ```

3. **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

4. **Appliquer les migrations**
    ```bash
    python manage.py migrate
    ```

5. **(Optionnel) Charger des données initiales**
    - Des utilisateurs de démo sont déjà présents en base, ou vous pouvez créer de nouveaux comptes via l’interface.

6. **Lancer le serveur local**
    ```bash
    python manage.py runserver
    ```

---

## Utilisation

- Accéder au site : [http://localhost:8000](http://localhost:8000)
- Se connecter avec un des comptes de démo :
    - **AlN**, mot de passe : `AlNadmin@777`
    - **Olivier**, mot de passe : `Olivieradmin@777`
    - **Sauron**, mot de passe : `Sauronadmin@777`
- Ou créer un nouvel utilisateur pour tester toutes les fonctionnalités (tickets, critiques, suivi/blocage, gestion mot de passe…)

---

## Convention de code / PEP8

- **PEP8 strictement appliqué** (flake8 OK sur tout le projet).
- **max-line-length fixé à 120** pour une meilleure lisibilité (pratique Django en entreprise).
- Indentation, espaces, commentaires homogènes sur tout le code.

---

## Tests

- **Suite de tests complète** (unitaires et intégration) : formulaires, modèles, vues, authentification, toutes fonctionnalités principales.
- Pour lancer tous les tests :
    ```bash
    python manage.py test
    ```
- **Tous les tests doivent être au vert avant toute livraison.**
- Contrôle du style de code :
    ```bash
    flake8 .
    ```

---

## Responsive design

- L’interface est testée et optimisée pour desktop, tablette et mobile.
- Toutes les fonctionnalités sont confortablement utilisables sur tout type d’écran.

---

## Auteur

Projet réalisé dans le cadre d’OpenClassrooms P9 (“Application d’avis de livres type Goodreads”).  
Contact possible pour revue de code ou opportunité professionnelle.