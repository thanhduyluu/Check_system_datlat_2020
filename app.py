from flask import Flask, render_template, Response , redirect, request, url_for
from Customer import read_data
import time
import itertools

app = Flask(__name__)
global list_cus_mark
global list_cus
list_cus = read_data()
list_cus_mark = list()

@app.route('/')
def index():
    return render_template("customer.html")
@app.route('/', methods=["POST"])
def post_index():
    list_valid = []
    key_search = str(request.form.get("id_search"))
    key_complete = str(request.form.get("bib"))
    print(key_search)
    print(key_complete)

    if key_search != "None":
        for i in list_cus:
            if i.compare(key_search):
                list_valid.append(i.__dict__)
        if len(list_valid) != 0:
            return render_template("res_customer.html",value=list_valid)
        else:
            return render_template("notfound.html",value=list_valid)
    elif key_complete != "None":
        for i in list_cus:
            if i.compare_bib(key_complete):
                list_cus_mark.append(i.__dict__)
        return render_template("complete.html")
    else:
        return render_template("customer.html")
@app.route('/clerk/', methods=["POST","GET"])
def index_clerk():
    key_delete = str(request.form.get("bib"))
    if key_delete != "None" and len(list_cus_mark) > 0:
        for index, value in enumerate(list_cus):
            if value.compare_bib(key_delete):
                list_cus_mark.remove(value.__dict__)
                break
    return render_template("clerk.html",value=list_cus_mark)

if __name__ == '__main__':
    app.run(debug=True)