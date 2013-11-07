#-*- encoding: utf8 -*-
"""Import redmine tickets from csv."""
import csv
import logging
import sys

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

try:
    from redmine import Redmine
    from redmine_ldap import get_user_id_from_ldap
except ImportError, exception:
    LOGGER.error(str(exception))
    sys.exit()

REDMINE_SERVER_URL = 'https://my_server'
USER_KEY = '############################'
FILENAME = 'tickets.csv'

CATEGORY_MAP = {
    'décision': 1,
    'livraison': 2,
}

STATUS_MAP = {
    'ouvert': 1,
    'en cours': 2,
    'clos': 3,
}

TRACKER_MAP = {
    'anomalie': 1,
    'évolution': 2,
    'fonction-exigence': 3,
}

FIELDS_TO_REMAP = {
    'assigned_to': get_user_id_from_ldap,
    'category': CATEGORY_MAP.get,
    'status': STATUS_MAP.get,
    #TODO:
    #'parent_issue': SERVER.issues,
    'tracker_id': TRACKER_MAP.get,
}


class RedmineImporter(object):
    """Docstring for MyClass. """

    def __init__(self, red_url=REDMINE_SERVER_URL, user_key=USER_KEY):
        self.tickets_list = None
        try:
            self.redmine_server = Redmine(red_url, user_key, version='2.3')
        except:
            LOGGER.error('Cannot connect to Redmine server, aborting.')

    def create_ticket_list(self, filename):
        """Create ticket list from csv file.

        :returns: tickets_list: list of dicts

        """
        with open(filename) as csv_file:
            csv_tickets = csv.DictReader(csv_file)
            self.tickets_list = [row for row in csv_tickets]

    def import_tickets(self, filename):
        """Create Redmine ticket from tickets_list.

        """
        self.create_ticket_list(filename)
        LOGGER.info('Found %s tickets', len(self.tickets_list))
        for row in self.tickets_list:
            self.create_ticket(row)

    def create_ticket(self, row):
        """Create Redmine ticket from csv row.

        :row: csv row: dict
        :returns: True

        """
        for field in FIELDS_TO_REMAP.viewkeys() & row.viewkeys():
            row[field] = FIELDS_TO_REMAP[field](row[field])
        try:
            issue = self.redmine_server.issues.new(**row)
            LOGGER.info('Created ticket %s', issue)
        except:
            LOGGER.error('Cannot create issue, skipping...')
            return False
        return True

if __name__ == '__main__':
    redmine_server = RedmineImporter()
    LOGGER.info(u'Importing tickets')
    redmine_server.import_tickets(FILENAME)
