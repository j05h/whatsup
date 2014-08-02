from data import Data
import datetime
import time
import random

class Status(object):
  def session(self):
    return Data().get_session()

  def get(self, status_id):
    return self.session().execute('SELECT * from stats WHERE id = %s' ^ status_id)

  def add(self, dat):
    now = self.today()

    last = self.last_status(dat['site'], dat['service'])

    worst_state = dat['state']
    worst_message = dat['message']

    if last and last['worst_state'] < worst_state:
      worst_state = last['worst_state']
      worst_message = last['worst_message']

    self.session().execute(
        """
        UPDATE stats SET
        updated_at = dateof(now()),
        current_state = %s,
        current_message = %s,
        worst_state = %s,
        worst_message = %s
        WHERE year = %s AND month = %s AND date = %s AND site = %s AND service = %s
        """,
        [
            dat['state'],
            dat['message'],
            worst_state,
            worst_message,
            now.year,
            now.month,
            now.day,
            dat['site'],
            dat['service']
        ]
    )

    t = int(time.time() * 10000)

    self.session().execute(
        """
        UPDATE stats SET
        states[%s] = %s
        WHERE year = %s AND month = %s AND date = %s AND site = %s AND service = %s
        """,
        [
            t,
            ("%s|%s" % (dat['state'], dat['message'])),
            now.year,
            now.month,
            now.day,
            dat['site'],
            dat['service']
        ]
    )

  def last_status(self, site, service):
    lst = self.session().execute(
      """
      SELECT * FROM stats
      WHERE year = %s and month = %s and date = %s and site = %s and service = %s
      """,
      [
        self.today().year,
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

  def current(self):
    return self.session().execute('SELECT * from stats');

  def yesterday(self):
    return self.today() - datetime.timedelta(1)

  def today(self):
    return datetime.date.today()

  def tomorrow(self):
    return self.today() + datetime.timedelta(1)

