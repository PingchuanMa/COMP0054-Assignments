from flask import Flask, request, render_template, flash, redirect, url_for
from query import Query
import math
import os

app = Flask(__name__)
app.debug = True
q = Query('index')


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        sent = request.form['query']
        target = request.form['type']
        return redirect(url_for('search_result', sent=sent, target=target, page=1))
    else:
        return render_template('search.html')


@app.route('/<sent>')
def search_result(sent):
    if sent == 'favicon.ico':
        return "/static/images/favicon.ico"
    page = int(request.args.get('page'))
    if page < 1:
        page = 1
    target = request.args.get('target')
    results = q.query(sent, target, page)
    max_page = int(math.ceil(len(results) / 10.0))
    if page > max_page:
        page = max_page
    details = []
    for r in results:
        url = r['url']
        path = r['url'][7:]
        keywords = []
        for field, keyword in r.matched_terms():
            if field == 'content':
                keywords.append(keyword.decode('utf-8'))
        if target == 'website':
            title = r['title']
            brief = r['content'][:50] if len(r['content']) > 50 else r['content']
        else:
            title = r['content']
            brief = r['content']
        details.append((url, path, keywords, title, brief))

    return render_template('search_result.html', sent=sent, target=target, page=page, max_page=max_page, details=details)


@app.route('/article/<path:p>')
def show_article(p):
    return render_template(os.path.join('cache/',p))


# @app.route('/article/<title>', methods=['GET', 'POST'])
# def independent_article(title):
#     idx = query_sys.articles.titles.index(title)
#     raw_content = query_sys.articles.raw_contents[idx]
#     return render_template('articles.html', title=title, content=raw_content, keywords=[])


if __name__ == '__main__':
    app.run()
