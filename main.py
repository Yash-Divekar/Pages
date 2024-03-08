from flask import Flask, session, render_template, request, redirect
import ast
import requests
from bs4 import BeautifulSoup

# variables
global info
info = {}
global name
global data
global colin
# datastructure


def data_store():
    global data
    global info
    with open('data/info.txt', 'r') as f:
        info = f.read()
    with open('data/book.txt', 'r') as f:
        data = f.read()
    info = ast.literal_eval(info)
    data = ast.literal_eval(data)


lend = {}
"""lend={num : {
            book_name: book name,
            count : book count,
            }}
            """
msg = {'flas': False}

app = Flask(__name__)
app.secret_key = 'Yash'


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/logging', methods=['GET', 'POST'])
def logging():
    if request.method == 'POST':
        global name
        global info
        global data
        data_store()
        name = request.form['username']
        password = request.form['password']
        if info[name]['password'] == password:
            session['username'] = name
            return redirect('/index')
        return render_template('login.html')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        global name
        global info
        global data
        data_store()
        name = request.form['username'].title()
        password = request.form['password']
        info2 = {'password': password,
                 'lend': {}}
        info.update({name: info2})
        with open('data/info.txt', 'w') as f:
            inform = str(info)
            f.write(inform)
        return redirect('/index')


@app.route('/index', methods=['Get', 'Post'])
def index():
    if request.method == 'GET':
        global data
        global info
        data_store()
        mydict = {
            'data': data,
        }
        global colin
        colin=False
        return render_template('index.html', mydict=mydict, info=info, name=name)


@app.route('/lended', methods=['GET', 'POST'])
def lended():
    if request.method == 'POST':
        global data
        num = int(request.form['lend'])
        if data[num]['count'] > 0:
            data[num]['count'] -= 1
            if num not in info[name]['lend']:
                info[name]['lend'].update({num: {'name': data[num]['name'],
                                                 'count': 1,
                                                 'disc': data[num]['disc'],
                                                 }})
            else:
                info[name]['lend'][num]['count'] += 1
            msg['sucess'] = True
        else:
            msg['sucess'] = False

        msg['flas'] = True
        mydict = {
            'data': data,
        }

        with open('data/book.txt', 'w') as f:
            book = str(data)
            f.write(book)
        with open('data/info.txt', 'w') as f:
            inform = str(info)
            f.write(inform)
        return render_template('index.html', name=name, mydict=mydict, info=info, msg=msg)


@app.route('/collection', methods=['GET', 'POST'])
def collection():
    if request.method == 'GET':
        global name
        global data, info
        data_store()
        mydict = {
            'data': info[name]['lend'],
        }
    global colin
    colin=True
    return render_template('collection.html', mydict=mydict, info=info, name=name)


@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        global data
        global name
        num = int(request.form['return'])
        if num in info[name]['lend']:
            if info[name]['lend'][num]['count'] > 0:
                info[name]['lend'][num]['count'] -= 1
                data[num]['count'] += 1
                # error=lib_logic.Lib.Ret(num)
                msg['sucess'] = True
                msg['flas'] = True
                if info[name]['lend'][num]['count'] == 0:
                    del info[name]['lend'][num]
        else:
            msg['flas'] = True
            msg['sucess'] = False

    mydict = {
        'data': info[name]['lend'],
    }

    with open('data/book.txt', 'w') as f:
        book = str(data)
        f.write(book)
    with open('data/info.txt', 'w') as f:
        inform = str(info)
        f.write(inform)
    return render_template('collection.html', mydict=mydict, info=info, msg=msg, name=name)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        mydict = {
            'data': data,
        }
        global name
        return render_template('add.html', mydict=mydict, info=info, name=name)


@app.route('/added', methods=['GET', 'POST'])
def added():
    if request.method == 'POST':
        global data
        num = int(request.form['booknum'])
        book_name = request.form['bookname'].title()
        count = int(request.form['bookcount'])
        if num in data and data[num]['name'] == book_name:
            data[num]['count'] += count

        else:
            try:
                bookname = book_name.replace(' ', '_')

                url = f"https://en.wikipedia.org/wiki/{bookname}"
                r = requests.get(url)
                htmlcont = r.content
                soup = BeautifulSoup(htmlcont, 'html.parser')
                text = soup.find(id='bodyContent')
                cont = text.findChildren('p')
                disc = cont[1].get_text()

            except:
                disc = 'discription not found'

            data.update({num: {'name': book_name,
                               'count': count,
                               'disc': disc,
                               }})

        mydict = {
            'data': data,
        }
        with open('data/book.txt', 'w') as f:
            book = str(data)
            f.write(book)
        return render_template('add.html', mydict=mydict, info=info, name=name)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        global data
        global info
        global name
        global colin
        book_name = request.form['search'].title()
        data_store()
        new_data = {}
        if colin==True:
            for item in info[name]['lend']:
                if book_name in info[name]['lend'][item]['name']:
                    new_data.update({item: info[name]['lend'][item]})
        else:
            for item in data:
                if book_name in data[item]['name']:
                    new_data.update({item: data[item]})
        mydict = {
            'data': new_data,
        }
        return render_template('index.html', mydict=mydict, info=info, name=name)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        global data
        with open('data/book.txt', 'w') as f:
            book = str(data)
            f.write(book)
        with open('data/info.txt', 'w') as f:
            inform = str(info)
            f.write(inform)
        session.pop('username', None)
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
