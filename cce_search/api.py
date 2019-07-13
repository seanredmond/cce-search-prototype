from flask import current_app, g
import requests

def search(term, page=0, per_page=10):
    r = requests.get(current_app.config['API'] + '/search/fulltext',
                     params={'query': term,
                             'source': 'true',
                             'page': page,
                             'per_page': per_page})
    return r.json()


def reg_search(term, page=0, per_page=10):
    api = current_app.config['API']
    r = requests.get("{}/search/registration/{}".format(api, term),
                     params={'source': 'true',
                             'page': page,
                             'per_page': per_page})
    return r.json()


def ren_search(term, page=0, per_page=10):
    api = current_app.config['API']
    r = requests.get("{}/search/renewal/{}".format(api, term),
                     params={'source': 'true',
                             'page': page,
                             'per_page': per_page})
    return r.json()
    


def registration(cceid):
    r = requests.get('{}/registration/{}'.format(current_app.config['API'],
                                                 cceid))
    r.raise_for_status()
    return r.json()


def renewal(cceid):
    r = requests.get('{}/renewal/{}'.format(current_app.config['API'],
                                            cceid))
    r.raise_for_status()
    return r.json()
