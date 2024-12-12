# Django Restaurant App

This Django app helps restaurant employees easily manage ingredient inventory, create menus and recipes with prices, track purchases, and stay informed about low stock levels.

## Setup Instructions

### 1. Create and activate a virtual environment

Create a virtual environment to keep dependencies isolated:

```bash
python3 -m venv .venv
```
 Activate the virtual environment (use the appropriate command for your OS).

```bash
# On Windows
.venv\Scripts\activate

# On macOS and Linux
source .venv/bin/activate
```
### 2. Install dependencies
Install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Create a superuser
To access the Django admin interface, you’ll need a superuser account. Create one by running:
```bash
python3 manage.py createsuperuser
```
Follow the prompts to set up a username, email, and password.

### 4. Run the server

```bash
python3 manage.py runserver
```

The Django admin interface allows you to manage your application's data and settings. You can access it at the `/admin` route after starting the server. For example:

http://127.0.0.1:8000/admin/

### 5. Make and apply migrations
Migrations are necessary to create and update database tables. Run the following commands to make and apply migrations when first running the app and after any change in the models: 
```bash
# Prepare migrations
python3 manage.py makemigrations

# Apply migrations to the database
python3 manage.py migrate
```

## Optional

### Generate a model diagram
To visualize the relationships between models, you can create a diagram using Django Extensions and Graphviz.

Install the necessary libraries (they are not part of `requirements.txt` as this part is optional):
```bash
pip install django-extensions
brew install graphviz
```
Add `django-extensions` to `INSTALLED_APPS` in `settings.py`.

Add the `GRAPH_MODELS` settings to `settings.py`:

```bash
GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}
```

Generate the model diagram as a .dot file: 
```bash
python3 manage.py graph_models -a --dot -o restaurant_models.dot
```

Convert the .dot file to a .png image:
```bash
dot -Tpng base_models.dot -o restaurant_models.png
```

For further information on the model diagram you can read the [the django-extensions documentation](https://django-extensions.readthedocs.io/en/latest/graph_models.html).