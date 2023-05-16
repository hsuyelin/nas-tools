SECRET_KEY = "XXX"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "logs/db.sqlite3",
    }
}
# Django 4 warning: The default value of USE_TZ will change from False to True in Django 5.0.
# Set USE_TZ to False in your project settings if you want to keep the current default behavior.
USE_TZ = False
