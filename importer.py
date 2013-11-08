#-*- encoding: utf8 -*-
"""Import redmine tickets from csv."""
import csv
import logging
import sys
import urllib2

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
    """Redmine Importer: create issues list and upload each issue. """

    def __init__(self, red_url=REDMINE_SERVER_URL, user_key=USER_KEY):
        self.issues_list = None
        self.created_issues = []
        self.redmine_server = Redmine(red_url, user_key, version='2.3')

    def create_issues_list(self, filename):
        """Create issues list from csv file.

        :returns: None

        """
        with open(filename) as csv_file:
            csv_issues = csv.DictReader(csv_file)
            self.issues_list = [row for row in csv_issues]

    def import_issues(self, filename):
        """Create Redmine issues from issues_list.

        :returns: Number of successfuly created tickets: int.

        """
        self.create_issues_list(filename)
        LOGGER.info('Found %s issue(s)', len(self.issues_list))
        for row in self.issues_list:
            self.created_issues.append(self.create_issue(row))
        return len(filter(lambda issue: issue, self.created_issues))

    def create_issue(self, row):
        """Create Redmine issue from csv row.

        :row: csv row: dict
        :returns: True or False on success or failure.

        """
        for field in FIELDS_TO_REMAP.viewkeys() & row.viewkeys():
            row[field] = FIELDS_TO_REMAP[field](row[field])
        try:
            issue = self.redmine_server.issues.new(**row)
            LOGGER.info('Created ticket %s', issue)
        except (ValueError, urllib2.URLError) as exception:
            LOGGER.error('Cannot create issue, skipping...')
            LOGGER.error('Please check connection parameters: %s',
                         self.redmine_server._url)
            LOGGER.error(str(exception))
            return False
        return True

if __name__ == '__main__':
    redmine_server = RedmineImporter()
    LOGGER.info('Importing issues.')
    tickets_nbr = redmine_server.import_issues(FILENAME)
    LOGGER.info('Created %s issues.', tickets_nbr)
