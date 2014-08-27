import datetime
import time

from flask import json

from whatsup.app.data import Data


class Status(object):
    def session(self):
        return Data().get_session()

    def get(self, status_id):
        return self.session().execute(
            'SELECT * from stats WHERE id = %s' ^ status_id
        )

    def add(self, dat):
        now = self.today()

        last = self.last_status(dat['site'], dat['service'])

        worst_state = dat['state']
        worst_message = dat['message']

        if last and last['worst_state'] < worst_state:
            worst_state = last['worst_state']
            worst_message = last['worst_message']

        t = int(time.time() * 10000)
        j = json.dumps({'created_at': now.isoformat(),
                        'state': dat['state'],
                        'message': dat['message']})

        self.session().execute(
            """
            UPDATE stats SET
            updated_at = dateof(now()),
            current_state = %(state)s,
            current_message = %(message)s,
            worst_state = %(worst_state)s,
            worst_message = %(worst_message)s,
            states = [%(json)s] + states
            WHERE year = %(year)s AND month = %(month)s AND date = %(day)s
            AND site = %(site)s AND service = %(service)s
            """,
            {
                'state': dat.get('state'),
                'message': dat.get('message'),
                'worst_state': worst_state,
                'worst_message': worst_message,
                'json': j,
                'time': now.isoformat(),
                'time_int': t,
                'year': now.year,
                'month': now.month,
                'day': now.day,
                'site': dat.get('site'),
                'service': dat.get('service')
            }
        )

    def last_status(self, site, service):
        lst = self.session().execute(
            """
            SELECT * FROM stats
            WHERE year = %s and month = %s and date = %s and site = %s and service = %s
            """,
            [self.today().year,
             self.today().month,
             self.today().day,
             site,
             service
             ]
        )

        if(len(lst) == 0):
            return None
        else:
            return lst[0]

    def site(self, site):
        return self.map_states(self.session().execute(
            """
            SELECT * FROM stats
            WHERE year = %s and month = %s and date = %s and site = %s
            """,
            [
                self.today().year,
                self.today().month,
                self.today().day,
                site
            ]
        ))

    def current(self):
        return self.history(
            self.today().year,
            self.today().month,
            self.today().day
        )

    def history(self, year, month, day):
        return self.map_states(self.session().execute(
            """
            SELECT * from stats
            WHERE year = %s and month = %s and date = %s
            """,
            [year, month, day]
        ))

    def load_states(self, dictionary):
        return dict([(k, map(json.loads, v) if k == 'states' else v)
                    for k, v in dictionary.items()])

    def map_states(self, lst):
        return map(self.load_states, lst)

    def yesterday(self):
        return self.today() - datetime.timedelta(1)

    def today(self):
        return datetime.datetime.today()

    def tomorrow(self):
        return self.today() + datetime.timedelta(1)
