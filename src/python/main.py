import json
import os.path
import time
import uuid
import bleach

from flask import Flask, render_template, request

SITE_TITLE = 'The Lofi Hip-Hop Enjoyers Messageboard'
app = Flask(__name__)

class Reply:
    def __init__(self, body, image=None) -> None:
        self.time: int = int(time.time())
        self.body: str = body
        self.image = image

    def render(self):
        return render_template('reply.partial.html', body=self.body, image=self.image)

    @classmethod
    def from_dict(cls, d: dict):
        """
        Creates a new Message from a dictionary
        :param d: the dictionary to read from
        :return: a new Message
        """
        m = Reply(d['body'], d['image'])
        m.time = d['time']
        return m


class Topic:
    def __init__(self, title, body, image=None) -> None:
        self.uuid = str(uuid.uuid4().int)
        self.time: int = int(time.time())
        self.title: str = title
        self.body: str = body
        self.image = image
        self.replies = []

    def render(self):
        return render_template('post.partial.html', title=self.title, body=self.body, image=self.image,
                               post_id=self.uuid, replies=self.replies)

    def reply(self, r: Reply):
        self.replies.append(r)

    def to_dict(self) -> dict:
        """
        :return: the dictionary form of this Topic
        """
        d = self.__dict__.copy()
        d['replies'] = dict()
        for i in range(len(self.replies)):
            d['replies'][i] = self.replies[i].__dict__
        return d

    @classmethod
    def from_dict(cls, uuid: int, d: dict):
        """
        Creates a new Topic from a dictionary
        :param d: the dictionary to read from
        :return: a new Topic
        """
        t = Topic(d['title'], d['body'], d['image'])
        t.uuid = uuid
        t.time = d['time']
        t.title = d['title']
        t.body = d['body']
        for k, v in d['replies'].items():
            t.replies += [Reply.from_dict(v)]
        return t


def write():
    d = dict()
    for topic in topics:
        d[topic.uuid] = topic.to_dict()

    with open(f'db.json', 'w') as outfile:
        outfile.write(json.dumps(d, indent=2, separators=(',', ': ')))



@app.route('/')
def homepage():
    return render_template('index.html', title=SITE_TITLE, posts=topics)


@app.route('/topic/<id>')
def viewtopic(id):
    for topic in topics:
        if topic.uuid == id:
            post = topic
            break
    else:
        return render_template('post_success.html', result='Failed')

    return render_template('post.html', post=post, site_title=SITE_TITLE)


@app.route('/maketopic', methods=['POST'])
def maketopic():
    form = request.form.to_dict()
    for k in form.keys():  # escape anything nasty
        form[k] = bleach.clean(form[k])
    success = True

    try:
        topic = Topic(form['title'], form['body'])
        topics.append(topic)
    except KeyError:
        success = False
    write()
    return render_template('post_success.html', result='Successful' if success else 'Failed')


@app.route('/makereply/<id>', methods=['POST'])
def makereply(id):
    form = request.form.to_dict()
    for k in form.keys():  # escape anything nasty
        form[k] = bleach.clean(form[k])
    success = True

    try:
        reply = Reply(form['body'])
    except KeyError:
        print('No attribute body!')
        success = False
    else:
        for post in topics:
            if post.uuid == id:
                post.reply(reply)
                write()
                break
        else:
            print('Could not find this post!')
            success = False

    return render_template('post_success.html', result='Successful' if success else 'Failed')


topics = []
# create the db if it does not exist
if not os.path.exists('db.json'):
    with open(f'db.json', 'w') as outfile:
        outfile.write('{}')

# read topics from disk
with open(f'db.json', 'r') as infile:
    print(infile)
    j = json.load(infile)
    for k, v in j.items():
        topics.append(Topic.from_dict(k, v))
