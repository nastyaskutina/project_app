import requests
import matplotlib.pyplot as plt
from flask import Flask, render_template
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer
from nltk.tokenize import word_tokenize
from collections import Counter

app = Flask(__name__)


TOKEN = '8cc5f8108cc5f8108cc5f810298cb78d8a88cc58cc5f810d21e6f5ee77d18ef08eb1a50'
IDS = [-31255891, -33085806, -31570351, -95097458, -79913034, -51644163, -113499737, -39207368]
KEYWORDS = ['любовь', 'любить', 'жизнь', 'слово', 'сказать', 'уйти',
            'боль', 'сердце', 'душа', 'один', 'человек', 'чувство', 'счастье', 'город']
morph = MorphAnalyzer()
sw = stopwords.words('russian')
COUNTS = []


def get_words(text):
    words = word_tokenize(text)
    filtered = [w.lower() for w in words if w.isalnum()
                and w not in sw]
    lemm_text = [morph.parse(w)[0].normal_form for w in filtered]
    return lemm_text


def get_posts(user_id):
    offsets = [0, 100, 200]
    posts = []
    for off in offsets:
        data = requests.get(
            'https://api.vk.com/method/wall.get',
            params={
                'owner_id': user_id,
                'access_token': TOKEN,
                'v': '5.92',
                'offset': off,
                'count': 100,
            }
        ).json()
        posts = posts + data['response']['items']
    return posts


def get_lemms(data):
    all_words = []
    for elem in data:
        text = elem['text']
        lemm_text = get_words(text)
        all_words.extend(lemm_text)
    return all_words


def word_counter(all_words):
    counter = Counter(all_words)
    length = len(all_words)
    count = {'total': length}
    for word in KEYWORDS:
        count[word] = counter[word]
    return count


def total_count():
    tot_count = {'total': 0}
    for word in KEYWORDS:
        tot_count[word] = 0
    for count in COUNTS:
        tot_count['total'] += count['total']
        for word in KEYWORDS:
            tot_count[word] += count[word]
    return tot_count


def get_graphs():
    name_list = ['vtok', 'kkramar', 'ivrublevski', 'dkravchenko', 'pshibeeva',
                 'yuzelvinskaya', 'itrots', 'zzolotova', 'total']
    colours = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'm', 'hotpink', 'pink']
    for i, count in enumerate(COUNTS):
        name = name_list[i]
        x = KEYWORDS
        y = [count[w] / count['total'] * 100 for w in KEYWORDS]
        plt.bar(x, y, color=colours[i])
        plt.xticks(ticks=x, labels=KEYWORDS, rotation=90)
        plt.title('frequency of key words')
        plt.ylabel('frequency')
        plt.xlabel('words')
        picture_name = 'C:/Users/HP/PycharmProjects/project/static/' + name + '.png'
        plt.savefig(picture_name, bbox_inches='tight')
        plt.close(fig=None)


@app.route('/')
def get_counts():
    for user_id in IDS:
        data = get_posts(user_id)
        all_words = get_lemms(data)
        count = word_counter(all_words)
        COUNTS.append(count)
    COUNTS.append(total_count())
    get_graphs()
    return render_template('index.html')


@app.route('/total')
def total():
    name = 'total'
    count = total_count()



if __name__ == '__main__':
    app.run()
