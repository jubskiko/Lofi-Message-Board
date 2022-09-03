import time
import uuid
import bleach

from flask import Flask, render_template, request, url_for

SITE_TITLE = 'Lofi Hip-Hop Enjoyers Messageboard'
app = Flask(__name__)
topics = []


class Reply():
    def __init__(self, body, image = None) -> None:
        self.time:int = int(time.time())
        self.body: str = body
        self.image = image

    def render(self):
        return render_template('reply.partial.html', body=self.body, image=self.image)


class Topic():
    def __init__(self, title, body, image = None) -> None:
        self.uuid = str(uuid.uuid4().int)
        self.time:int = int(time.time())
        self.title: str = title
        self.body: str = body
        self.image = image
        self.replies = []

    def render(self):
        return render_template('post.partial.html', title=self.title, body=self.body, image=self.image, post_id=self.uuid, replies=self.replies)

    def reply(self, r: Reply):
        self.replies.append(r)


@app.route('/')
def homepage():
    return render_template('index.html', title=SITE_TITLE, posts=topics)


@app.route('/post', methods=['POST'])
def makepost():
    form = request.form.to_dict()
    for k in form.keys():  # escape anything nasty
        form[k] = bleach.clean(form[k])
    success = True

    try:
        topic = Topic(form['title'], form['body'])
        topics.append(topic)
    except KeyError:
        success = False
    return render_template('post_success.html', result='Successful' if success else 'Failed')


@app.route('/reply/<id>', methods=['POST'])
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
                break
        else:
            print('Could not find this post!')
            success = False

    return render_template('post_success.html', result='Successful' if success else 'Failed')


if __name__ == '__main__':
    pass
