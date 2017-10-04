from flask import Flask, request, render_template, flash, redirect, url_for
from query import Query

app = Flask(__name__)
app.debug = False
folder_name = "The Complete Works of William Shakespeare"
query_sys = Query(folder_name)
query_sys.load_articles('articles.pkl')


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        sent = request.form['query']
        return redirect(url_for('search_result', sent=sent))
    else:
        return render_template('search.html')


@app.route('/<sent>')
def search_result(sent):
    if sent == 'favicon.ico':
        return "/static/images/favicon.ico"
    final_set = query_sys.query(sent)
    results = []
    for idx in final_set:
        results.append([query_sys.articles.titles[idx], query_sys.articles.raw_contents[idx][0:10]])
    return render_template('search_result.html', entries=results, sent=sent)


@app.route('/article/<title>', methods=['GET', 'POST'])
def show_article(title):
    sent = request.args.get('sent')
    keywords = query_sys.query_keywords(sent)
    idx = query_sys.articles.titles.index(title)
    raw_content = query_sys.articles.raw_contents[idx]
    return render_template('articles.html', title=title, content=raw_content, keywords=keywords)


# @app.route('/article/<title>', methods=['GET', 'POST'])
# def independent_article(title):
#     idx = query_sys.articles.titles.index(title)
#     raw_content = query_sys.articles.raw_contents[idx]
#     return render_template('articles.html', title=title, content=raw_content, keywords=[])


if __name__ == '__main__':
    app.run()
