# Deploying to PythonAnywhere

This project has been converted to a Django-only application for easy deployment on PythonAnywhere.

## 1. Upload the Project
Upload the `talamkopo_django.zip` file to your PythonAnywhere account and extract it.

## 2. Create a Virtual Environment
Open a Bash console on PythonAnywhere and run:
```bash
mkvirtualenv --python=/usr/bin/python3.10 talamkopo-env
pip install -r requirements.txt
```

## 3. Set Up the Web App
1. Go to the **Web** tab on PythonAnywhere.
2. Click **Add a new web app**.
3. Choose **Manual configuration** (not the Django option, as we already have the project).
4. Select the Python version (e.g., 3.10).
5. In the **Virtualenv** section, enter the name of your virtual environment: `talamkopo-env`.
6. In the **Code** section:
   - **Source code:** `/home/YOUR_USERNAME/talamkopo_django`
   - **Working directory:** `/home/YOUR_USERNAME/talamkopo_django`
7. Edit the **WSGI configuration file** (link provided in the Web tab):
   ```python
   import os
   import sys

   path = '/home/YOUR_USERNAME/talamkopo_django'
   if path not in sys.path:
       sys.path.append(path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'talamkopo_project.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

## 4. Database and Static Files
In the Bash console:
```bash
python manage.py migrate
python manage.py collectstatic
```

## 5. Reload the Web App
Go back to the **Web** tab and click **Reload**.

Your site should now be live!
