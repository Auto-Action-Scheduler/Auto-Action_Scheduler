web: gunicorn AutoActionScheduler.wsgi
worker: celery -A AutoActionScheduler worker --beat --scheduler django --loglevel=info