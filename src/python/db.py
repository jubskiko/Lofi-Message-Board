from datetime import datetime
import json
import os
import glob


class Message:
    """
    A message consisting of a body and timestamp.
    This is the data held within one post.
    """

    def __init__(self):
        self.timestamp = datetime.timestamp(datetime.now())
        self.body = ''

    def __repr__(self) -> str:
        return f't={self.timestamp}, m={self.body}'

    @classmethod
    def from_dict(cls, d: dict):
        """
        Creates a new Message from a dictionary
        :param d: the dictionary to read from
        :return: a new Message
        """
        m = Message()
        m.body = d['body']
        m.timestamp = d['timestamp']
        return m


class Post:
    """
    A post consisting of a Tile, and all of its messages
    """

    def __init__(self):
        self.title = ''
        self.index = 0
        self.messages = dict()
        self.timestamp = datetime.timestamp(datetime.now())

    def add_message(self, message: Message) -> None:
        """
        Add a new message to this post
        :param message: the message to add
        :return: None
        """
        self.messages[self.index] = message
        self.index += 1

    def to_dict(self) -> dict:
        """
        :return: the dictionary form of this Post
        """
        d = self.__dict__.copy()
        d['messages'] = dict()
        for k, v in self.messages.items():
            d['messages'][k] = v.__dict__
        return d

    def __repr__(self) -> str:
        return f'n={self.title}, t={self.timestamp}, m={str(self.messages)}'

    @classmethod
    def from_dict(cls, d: dict):
        """
        Creates a new Post from a dictionary
        :param i: the index of this post
        :param d: the dictionary to read from
        :return: a new Post
        """
        p = Post()
        p.title = d['title']
        p.index = int(d['index'])
        p.timestamp = d['timestamp']
        for k, v in d['messages'].items():
            p.messages[k] = Message.from_dict(v)
        return p


class Thread:

    def __init__(self):
        self.index = 0
        self.posts = dict()
        self.name = ''

    def add_post(self, post: Post) -> None:
        """
        Add a new post to this thread
        :param post: the post to add
        :return: None
        """
        self.posts[self.index] = post
        self.index += 1

    def to_dict(self) -> dict:
        """
        :return: the dictionary form of this Post
        """
        d = self.__dict__.copy()
        d['posts'] = dict()
        for k, v in self.posts.items():
            d['posts'][k] = v.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict):
        """
        Creates a new Thread from a dictionary
        :param i: the index of this thread
        :param d: the dictionary to read from
        :return: a new Thread
        """
        b = Thread()
        b.index = int(d['index'])
        b.name = d['name']
        for k, v in d['posts'].items():
            b.posts[k] = Post.from_dict(v)
        return b

    def __repr__(self):
        return f'i={self.index}, n={self.name}, p={str(self.posts)}'


class Group:

    def __init__(self):
        self.index = 0
        self.threads = dict()
        self.name = ''

    def add_thread(self, thread: Thread) -> None:
        """
        Add a new thread to this group
        :param thread: the thread to add
        :return: None
        """
        self.threads[self.index] = thread
        self.index += 1

    def to_dict(self) -> dict:
        """
        :return: the dictionary form of this Post
        """
        d = self.__dict__.copy()
        del d['index']
        d['threads'] = dict()
        for k, v in self.threads.items():
            d['threads'][k] = v.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict):
        """
        Creates a new Group from a dictionary
        :param d: the dictionary to read from
        :return: a new Group
        """
        g = Group()
        g.name = d['name']
        for k, v in d['threads'].items():
            g.threads[k] = Thread.from_dict(v)
        return g

    def __repr__(self):
        return f'n={self.name}, t={str(self.threads)}'


def test():
    write_to_json()
    read_from_json()


def write_to_json():
    msg = Message()
    msg.body = 'This is a message.'

    post = Post()
    post.title = 'Post'
    post.add_message(msg)

    thread = Thread()
    thread.name = 'Thread'
    thread.add_post(post)

    msg = Message()
    msg.body = 'This is another message.'

    post = Post()
    post.title = 'Post 2'
    post.add_message(msg)
    thread.add_post(post)

    group = Group()
    group.name = 'Group'
    group.add_thread(thread)

    if not os.path.isdir('database'):
        os.mkdir('database')

    with open(f'database/{group.name.lower()}.json', "w") as outfile:
        outfile.write(json.dumps(group.to_dict(), sort_keys=True, indent=2, separators=(',', ': ')))


def read_from_json():
    for filename in glob.glob('database/*.json'):
        os.path.join(os.getcwd(), f'database/{filename}')
        with open(os.path.join(os.getcwd(), filename), 'r') as f:  # open in readonly mode
            j = json.load(f)
            group = Group.from_dict(j)
            print(group)


if __name__ == '__main__':
    test()
