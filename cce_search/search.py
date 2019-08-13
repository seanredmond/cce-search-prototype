from cce_search.api import search, reg_search, ren_search, registration, renewal
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import re
from urllib.parse import urlparse, parse_qs, parse_qsl, urlunparse, urlencode
from werkzeug.exceptions import abort
from requests import HTTPError

bp = Blueprint('search', __name__)

@bp.route('/')
def index():
    results = None
    term = None
    paging=None
    search_type = "ft"
    if request.args:
        term = request.args['term']
        if request.args['type'] == 'ft':
            response = search(request.args['term'], request.args.get('page'),
                              request.args.get('per_page'))
        elif request.args['type'] == 'reg':
            search_type = "reg"
            term = term.strip().upper()
            response = reg_search(term,
                                  request.args.get('page'),
                                  request.args.get('per_page'))
        else:
            search_type = "ren"
            term = term.strip().upper()
            response = ren_search(term,
                                  request.args.get('page'),
                                  request.args.get('per_page'))
            
        paging = proc_pagination(response['data']['paging'],
                                 request.args.get('page'))
        results = proc_results(response)
    
    
    return render_template('search/index.html', results=results, term=term,
                           paging=paging, search_type=search_type)


def proc_results(r):
    return [enhance_results(res) for res in r['data']['results']]


def enhance_results(r):
    if r.get('type') == 'renewal':
        return r

    return {**r, **{'original': strip_tags(r.get('xml')),
                    'is_post_1963': is_post_1963(r.get('registrations')),
                    'source_url': ia_url(r.get('source', {}))}}


def strip_tags(xml):
    if xml:
        return re.sub(r"</?.+?>", "", xml).replace("\n", "")
    return ""


def ia_url(src):
    #return src
    return "{}#page/{:d}/mode/1up".format(ia_stream(src.get('url', '')),
                                        src.get('page', 0))

def ia_stream(url):
    return url.replace('details', 'stream')


def is_post_1963(regs):
    return any([r['date'] > '1963' for r in regs])


def proc_pagination(pg, current):
    if not pg['next'] and not pg['previous']:
        return {**pg, **{'has_pages': False}}

    per_page = extract_per_page(pg)

    if current is None:
        current = 1
    else:
        current = int(current) + 1
        
    
    return {**pg, **{'has_pages': True,
                     'current_page': current,
                     'last_page': extract_last(pg),
                     'pages': dict([(p, extract_pg(pg.get(p), per_page))
                               for p in ['first', 'next', 'last',
                                         'previous']])}}

def extract_pg(pg, per_page):
    if pg:
        oq = dict(parse_qsl(urlparse(pg).query))
        t = urlparse(request.url)
        return urlunparse(
            t._replace(query=urlencode({**dict(parse_qsl(t.query)),
                                        **{'page': oq['page'],
                                           'per_page': oq['per_page']}})))

    return None


def extract_per_page(pg):
    return [parse_qs(urlparse(v).query)["per_page"][0]
            for v in pg.values() if v][0]


def extract_last(pg):
    last = pg.get('last')
    if last is None:
        return "1"
    else:
        return int(parse_qs(urlparse(last).query)["page"][0]) + 1


@bp.route('/cceid/<cceid>')
def cceid(cceid):
    try:
        results = registration(cceid)
        return render_template('search/cceid.html', result=results["data"])
    except HTTPError:
        try:
            results = renewal(cceid)
            return render_template('search/cceid.html',
                                   result=results["data"][0])
        except HTTPError:
            pass

    return render_template('search/cceid.html', result=None, error=1)
    
        
