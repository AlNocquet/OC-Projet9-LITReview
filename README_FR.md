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

1. **Cloner le dépôt**
    ```bash
    git clone https://github.com/AlNocquet/OC-Projet9-LITReview.git
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

Alice Nocquet