import datetime

import humanize
from flask import render_template

from whatsup.app import app
from whatsup.app.status import Status


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    date = datetime.datetime.today()
    return history(date.year, date.month, date.day)


@app.route('/history/<int:year>/<int:month>/<int:day>')
def history(year, month, day):
    current = {}
    for stat in Status().history(year, month, day):
        site = current.get(stat['site'], [])
        current[stat['site']] = site + [stat]

    date = datetime.date(year, month, day)
    if date == datetime.datetime.today().date():
        nxt = None
    else:
        nxt = (date + datetime.timedelta(1)).strftime("%Y/%m/%d")
    prv = (date - datetime.timedelta(1)).strftime("%Y/%m/%d")

    date_str = date.strftime('%Y-%m-%d')
    return render_template("index.html",
                           title=("What's up on %s" % date_str),
                           current=current,
                           nxt=nxt,
                           prv=prv)


@app.route('/site/<string:site_id>')
def site(site_id):
    site = Status().site(site_id)
    print site
    return render_template("site.html",
                           title=("What's up at %s" % site_id),
                           site=site)


@app.template_filter('time_ago')
def naturaltime(the_time):
    if isinstance(the_time, str) or isinstance(the_time, unicode):
        the_time = datetime.datetime.strptime(the_time.rsplit('.')[0],
                                              '%Y-%m-%dT%H:%M:%S')
    return humanize.naturaltime(datetime.datetime.now() - the_time)
