import flask
import feedparser
import pytz
import datetime
import time

def get_posts_by_subscription(s, _start=False):
    utc = pytz.utc
    if not _start:
        # I want only posts from "today,"
        # where the day lasts until 2 AM.
        homeTZ = pytz.timezone('US/Arizona')
        dt = datetime.datetime.now(homeTZ)
        if dt.hour < 2:
            dt = dt - timedelta(hours=24)
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        start = start.astimezone(utc)
    else:
        start = datetime.datetime.strptime(_start, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        start = start.astimezone(utc)
    _posts = []
    f = feedparser.parse(s)
    try:
        blog = f['feed']['title']
    except KeyError:
        blog = ""
    for e in f['entries']:
        try:
            when = e['published_parsed']
        except KeyError:
            when = e['updated_parsed']
        when = utc.localize(datetime.datetime.fromtimestamp(time.mktime(when)))
        if when > start:
            title = e['title']
            try:
                body = storage(e['content'][0])['value']
            except:
                body = e['summary']
            link = e['link']
            _posts.append(dict(when=when, blog=blog, title=title, link=link, body=body))
    return _posts

app = flask.Flask(__name__)

@app.route('/', methods=['GET','POST'])
def posts():
    if flask.request.method == 'POST':
        i = flask.request.get_json()
        if i.get('start', False):
            return flask.jsonify(data=get_posts_by_subscription(i['subscription'], i['start']))
        else:
            return flask.jsonify(data=get_posts_by_subscription(i['subscription']))
    else:
        resp = flask.Response("""
Usage
~~~~~

curl -X POST \\
  http://localhost:5000/posts \\
  -H 'Content-Type: application/json' \\
  -d '{
    "subscription": "https://www.stabroeknews.com/feed",
    "start": "2019-11-29"
}'
""")
        resp.headers['content-type'] = 'text/plain'
        return resp

if __name__ == '__main__':
    app.run()