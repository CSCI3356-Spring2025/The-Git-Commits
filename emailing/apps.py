from django.apps import AppConfig
from django.db.backends.signals import connection_created
from sys import argv
from os import environ
from multiprocessing import Process
from time import sleep

# Poll every 30 minutes to see if we need to send an email
POLLING_TIME = 30 * 60

def background_email_process():
    from .emailing import check_and_send
    while True:
        check_and_send()
        sleep(POLLING_TIME)


def start_process(sender, **kwargs):
    p = Process(target=background_email_process)
    print("Starting email background process")
    # check_and_send()
    p.start()

class EmailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emailing'

    def ready(self):
        if "runserver" not in argv:
            return

        connection_created.connect(start_process)
