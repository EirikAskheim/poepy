import requests
import json
import logging
import time
from pprint import pprint


class Requester:

    login_url = u'https://www.pathofexile.com/login'
    character_url = u'http://www.pathofexile.com/character-window/get-characters'
    stash_url = u'http://www.pathofexile.com/character-window/get-stash-items?league=%s&tabs=1&tabIndex=%d'
    inventory_url = u'http://www.pathofexile.com/character-window/get-items?character=%s'

    def __init__(self, session_id):
        self.logger = logging.getLogger('Requester')
        self.session = requests.Session()
        self.session.cookies.update({'PHPSESSID': session_id})

        self.stash = dict()
        self.inventories = dict()
        self.characters = None

    def get_characters(self, force=False):
        if force == True or self.characters is None:
            self.characters = json.loads(self.session.get(self.character_url))
        return self.self.characters

    def get_stash(self, league, force=False):
        if force == True or league not in self.stash.keys():
            self.logger.info('Refreshing stash tabs for %s', league)
            if league in self.stash.keys():
                del self.stash[league]
            self.stash[league] = dict()
            tab_number = 0
            while True:
                response = self.session.get(self.stash_url % (league, tab_number))
                response_dict = json.loads(response.text)
                total_tabs = response_dict['numTabs']
                self.stash[league][tab_number] = response_dict['items']
                logging.debug('Got tab %d of %d', tab_number, total_tabs)
                if tab_number == total_tabs - 1:
                    break
                tab_number += 1
                time.sleep(0.2)
        else:
            self.logger.info('Not refreshing stash tabs for %s. To force refresh use force=True', league)
        return self.stash[league]

    def get_inventory(self, character, force=False):
        if force == True or character not in self.inventories.keys():
            self.logger.info('Refreshing inventory for %s', character)
            if character in self.inventories.keys():
                del self.inventories[character]
            response = self.session.get(self.inventory_url % (character))
            response_dict = json.loads(response.text)
            self.inventories[character] = response_dict
        else:
            self.logger.info('Not refreshing inventory for %s. To force refresh use force=True', character)
        return self.inventories[character]

    def authenticate(self):
        response = self.session.get(self.login_url)
        self.logger.info('%s', self.session.headers)
        self.logger.info('%s', response.headers)
        return response

if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('poe-api-main')
    if len(sys.argv) < 2:
        logger.error('Takes poe session id as argument')
        sys.exit(1)
    session_id = sys.argv[1]
