web: gunicorn AutoActionScheduler.wsgi
celery: celery -A AutoActionScheduler worker -l INFO
beat: celery -A  AutoActionScheduler beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler