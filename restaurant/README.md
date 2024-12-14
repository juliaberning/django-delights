# Django Restaurant App

This Django app helps restaurant employees easily manage ingredient inventory, create menus and recipes with prices, track purchases, and stay informed about low stock levels.

## Getting started

### Prerequisites
Ensure the following are installed on your system:
- **Git** 
- **Python 3.10** or higher (tested on 3.13.1)

```bash
python --version
```

### Installation
1. Clone this repository and navigate into the project directory.

```bash
git clone <Github-link> && cd <project-directory>
```

2. Create and activate a virtual environment:

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
## How to use

### Set up the database
1. Prepare and apply migrations:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

2. Create a superuser for accessing the admin interface by running the following command and following the instructions:
```bash
python3 manage.py createsuperuser
```


### Run the server
Start the server locally: 
```bash
python3 manage.py runserver
```

Access the admin interface at:
http://127.0.0.1:8000/admin/


## Development

### Testing
Run unit tests to verify the functionality: 

```bash
python3 manage.py test
```

### Linting & Formatting
This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Check for linting issues in the current directory:
ruff check . 

# Automatically fix linting issues:
ruff check --fix

# Format all files in the current directory:
ruff format .
``` 

### Github Actions Workflow
This repository uses GitHub Actions for automation. 

##### Configured workflows: 
- Ruff Linter:  Ensures that the code adheres to linting standards.

##### Trigger: 
- On every commit push to any branch.


### Optional: Generate a model diagram
You can generate a visual diagram of your models using Django Extensions and Graphviz.

Install the necessary libraries:
```bash
pip install django-extensions
brew install graphviz
```
Add `django-extensions` to `INSTALLED_APPS` in `settings.py`.

```bash
INSTALLED_APPS = [
    ...,
    'django_extensions',
]
```

Add the following to `settings.py` to enable diagram generation:

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

Convert the .dot file to an image:
```bash
dot -Tpng base_models.dot -o restaurant_models.png
```

For further information on the model diagram you can read the [the django-extensions documentation](https://django-extensions.readthedocs.io/en/latest/graph_models.html).