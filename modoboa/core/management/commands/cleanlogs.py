# coding: utf-8

import datetime
from optparse import make_option

from django.db import connection
from django.core.management.base import BaseCommand
from django.utils import timezone

from modoboa.core import load_core_settings
from modoboa.core.models import Log
from modoboa.lib import parameters


class Command(BaseCommand):
    args = ''
    help = 'Log table cleanup'

    option_list = BaseCommand.option_list + (
        make_option('--debug',
                    action='store_true',
                    default=False,
                    help='Activate debug output'),
        make_option('--verbose',
                    action='store_true',
                    default=False,
                    help='Display informational messages')
    )

    def __vprint(self, msg):
        if not self.verbose:
            return
        print msg

    def handle(self, *args, **options):
        if options["debug"]:
            import logging
            l = logging.getLogger("django.db.backends")
            l.setLevel(logging.DEBUG)
            l.addHandler(logging.StreamHandler())
        self.verbose = options["verbose"]

        load_core_settings()
        log_maximum_age = int(parameters.get_admin("LOG_MAXIMUM_AGE"))
        self.__vprint("Deleting logs older than %d days..." % log_maximum_age)
        limit = timezone.now() - datetime.timedelta(log_maximum_age)
        Log.objects.filter(date_created__lt=limit).delete()
        connection.close()
        self.__vprint("Done.")
