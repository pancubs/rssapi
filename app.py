import flask
import feedparser

def get_posts_by_subscription(s, _start):
    utc = pytz.utc
    if not _start:
        # I want only posts from "today,"
        # where the day lasts until 2 AM.
        homeTZ = pytz.timezone('US/Arizona')
        dt = datetime.now(homeTZ)
        if dt.hour < 2:
            dt = dt - timedelta(hours=24)
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        start = start.astimezone(utc)
    else:
        start = _start.replace(hour=0, minute=0, second=0, microsecond=0)
        start = start.astimezone(utc)
    _posts = []
    f = fp.parse(s)
    try:
        blog = f['feed']['title']
    except KeyError:
        blog = ""
    for e in f['entries']:
        try:
            when = e['published_parsed']
        except KeyError:
            when = e['updated_parsed']
        when = utc.localize(datetime.fromtimestamp(time.mktime(when)))
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

@app.route('/posts', methods=['POST'])
def posts():
    if flask.request.method == 'POST':
        i = flask.request.form
        if i.get('start', False):
            return flask.jsonify(data=get_posts_by_subscription(i['subscription'], i['start']))
        else:
            return flask.jsonify(data=get_posts_by_subscription(i['subscription']))

if __name__ == '__main__':
    app.run()