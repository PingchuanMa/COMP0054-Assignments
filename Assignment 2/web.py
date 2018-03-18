from flask import Flask, request, render_template, flash, redirect, url_for
from paper_query import PaperQuery

app = Flask(__name__)
app.debug = True
folder_name = "static/papers"
query_sys = PaperQuery(folder_name)
query_sys.load_parser("papers.pkl")


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
    try:
        final_set = query_sys.query(sent)
    except Exception:
        final_set = []
    results = []
    for idx in final_set:
        results.append([query_sys.pp.title[idx], query_sys.pp.abstract[idx], query_sys.pp.file_names[idx]])
    return render_template('search_result.html', entries=results, sent=sent)


# @app.route('/article/<idx>', methods=['GET', 'POST'])
# def show_article(idx):
#     # sent = request.args.get('sent')
#     # keywords = query_sys.query_keywords(sent)
#     # idx = query_sys.articles.titles.index(title)
#     # raw_content = query_sys.articles.raw_contents[idx]
#     assert idx.isdecimal()
#     return "/papers/" + query_sys.pp.file_names[int(idx)]


# @app.route('/article/<title>', methods=['GET', 'POST'])
# def independent_article(title):
#     idx = query_sys.articles.titles.index(title)
#     raw_content = query_sys.articles.raw_contents[idx]
#     return render_template('articles.html', title=title, content=raw_content, keywords=[])


if __name__ == '__main__':
    app.run()
