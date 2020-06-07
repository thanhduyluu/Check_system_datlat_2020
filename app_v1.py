from flask import Flask, render_template, request, session, flash, send_file,redirect
from Customer import read_data
import os
from datetime import datetime
import pandas as pd
import string
import random

path = os.path.join(os.getcwd(),"static","ds.xlsx")
path_backup = os.path.join(os.getcwd(),"static","backup","queue")
path_result = os.path.join(os.getcwd(),"static","backup","complete")
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'memcached'


global list_cus_mark, list_cus, all_list_cus_mark, list_completed,setdis, config, dtim_POS, counter_dis, list_pw
counter_dis = dict()
dtim_POS = list()
list_cus = dict()
setdis = set()
list_completed = list()
list_pw = list()


config = dict()
global PASSWORD
PASSWORD = "techhaus"
number_POS = 50
key_cus_mark = ["queue" + str(i) for i in range(number_POS)]
list_cus_mark = [[] for i in range(number_POS)]
all_list_cus_mark = dict(zip(key_cus_mark,list_cus_mark))
try:
    session['logged_in'] = False
except Exception as e:
    print(e)

def rm_all(path):
    for i in os.listdir(path):
        try:
            os.remove(path + "/" + i)
        except:
            continue

def save_backup(content,namefile):
    s = ""
    for li in content:
        for i in li:
            s += str(i.get("bib")) + "\t"
        s += "\n"
    with open(path_backup + "/" + namefile + ".txt","w") as fw:
        fw.write(s)

def save_compelete(content):
    s = ""
    for i in content:
        s += i[0] + "\t" + i[1] + "\t"  + str(i[2]) + "\n"
    with open(path_result + "/complete.txt","a") as fw:
        fw.write(s)

def load_complete():
    namefile = path_result + "/complete.txt"
    with open(namefile, "r") as f:
        for i in f:
            tmp = i.strip("\n").split("\t")
            list_completed.append(tmp[0])
            list_cus.get(tmp[0]).set_pick(tmp[2])
            list_cus.get(tmp[0]).set_pickedup(tmp[1])



def load_backup(content, namefile):
    with open(namefile,"r") as fr:
        for line in fr:
            sub = list()
            for bib in line.strip("\n").split("\t"):
                if bib.strip("\t").strip("\n") != "" and bib.strip("\t").strip("\n") not in list_completed:
                    sub.append(list_cus.get(bib).__dict__)
            content.append(sub)

def randompass():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(6))


@app.route('/admin/',methods=['POST','GET'])
def admin():
    if not session.get('logged_in'):
        return render_template('login.html', error="0")
    else:
        number_pos = [x for x in range(number_POS)]
        data = {"noPOS": number_pos,
                "distance": setdis}
        return render_template("index.html",value=data)

@app.route('/upload', methods=['POST'])
def do_upload():
    try:
        form1 = request.files['file']
        form1.save(path)

        list_cus.clear()
        setdis.clear()

        data_cus_total, dis_total = read_data(path)

        for i in dis_total:
            setdis.add(i)
        for i in setdis:
            counter_dis.update({i:[0,0]})

        for key, val in data_cus_total.items():
            list_cus.update({key:val})
            counter_dis[val.distance][1] += 1

    except Exception as e:
        print(e)

    return redirect("/admin")

@app.route('/config', methods=['POST'])
def do_config():
    try:
        list_pw.clear()
        list_req = request.form.lists()
        key = list()
        val = list()
        for i in list_req:
            key.append(i[0])
            val.append(i[1])
            list_pw.append(randompass())
        config.update(dict(zip(key,val)))
    except Exception as e:
        print(e)
    return redirect("/admin")

@app.route('/load', methods=['POST'])
def do_load_Backup():
    load_complete()
    try:

        key_admin = request.form.get("key_admin")
        if key_admin == "1":
            for i in os.listdir(path_backup):
                path_file = os.path.join(path_backup,i)
                key = i.strip(".txt")
                load_backup(all_list_cus_mark.get(key),path_file)
    except Exception as e:
        print(e)
    return redirect("/admin")

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['pw'] == "techhaus":
        session['logged_in'] = True
    else:
        return render_template("login.html", error="1")
    return redirect("/admin")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect("/admin")

@app.route("/session_destroy",methods=["POST","GET"])
def destroy_session():
    session["index_session"] = None
    return redirect("/")

@app.route("/create_session",methods=["POST","GET"])
def init():
    try:
        id = int(request.form["index"]) - 1
        passw = request.form["pw"]
    except:
        return render_template("init.html", value={"error": "1"})

    if id > 50 or id < 0:
        return render_template("init.html", value={"error": "1"})

    if id >= len(list_pw):
        return render_template("init.html", value={"error": "3"})

    if list_pw[id] != passw:
        return render_template("init.html", value={"error": "2"})
    session["index_session"] = id
    return redirect("/")

@app.route('/',methods=["POST","GET"])
def refresh_data():
    if not session.get("index_session") and session.get("index_session") != 0:
        return render_template("init.html", value={"error": "0"})
    else:
        id = session.get("index_session")
        loconf = config.get(str(id))

        if loconf[0] == "True":
            category = "Group"
        else:
            category = loconf[0]
        return render_template('search.html',value={"error": "10","id":session.get("index_session"),"category":category})


@app.route('/download',methods=["GET","POST"])
def downloadFile ():

    data_file = {"bib":[],
                 "name":[],
                 "code":[],
                 "distance":[],
                 "passport":[],
                 "phone":[],
                 "dtime":[],
                 "pPOS":[]}

    for i in list_completed:
        cus = list_cus.get(i)
        data_file.get("bib").append(i)
        data_file.get("name").append(cus.name)
        data_file.get("code").append(cus.code)
        data_file.get("distance").append(cus.distance)
        data_file.get("passport").append(cus.passport)
        data_file.get("phone").append(cus.phone)
        data_file.get("dtime").append(cus.dtime)
        data_file.get("pPOS").append(cus.pPOS)
    df = pd.DataFrame.from_dict(data_file)
    name_file = path_result + "/resutl.xlsx"
    df.to_excel(name_file)
    return send_file(name_file, as_attachment=True)

@app.route('/clear-backup')
def clear():
    rm_all(path_backup)
    rm_all(path_result)
    return admin()

@app.route("/admin/live/",methods=["GET","POST"])
def admin_live():
    return render_template("live_admin.html",value={"total":len(list_cus)})

@app.route("/completed",methods=["GET"])
def count_complete():
    return render_template("couter.html",value=counter_dis,total=[len(list_completed),len(list_cus)])

@app.route("/live",methods=["GET","POST"])
def live():
    res = []
    for i in list_completed:
        res.append(list_cus.get(i).__dict__)

    return render_template("compont_admin.html",value=res)

@app.route("/info",methods=["POST","GET"])
def info():
    key_form = request.form.get('id_search')
    list_valid = []
    if key_form != None:
        for k,i in list_cus.items():
            if i.compare(str(key_form)):
                list_valid.append(i.__dict__)
        if len(list_valid) != 0:
            data = {"data":list_valid,
                    "error": "2"}
            return render_template("search_information.html", value=data)
        else:
            return render_template("search_information.html", value={"error":"3"})
    else:
        return render_template("search_information.html", value={"error":"0"})

@app.route("/cf",methods=["GET","POST"])
def cf():
    k = [int(key) for key,val in config.items()]
    v = [val for key,val in config.items()]
    value = list()

    for idx in range(len(list_pw)):

        value.append([k[idx], v[idx], list_pw[idx]])

    return render_template("cf.html",value=value)

@app.route("/clear-data", methods=["GET","POST"])
def c():
    list_cus.clear()
    setdis.clear()

    data_cus_total, dis_total = read_data(path)

    for i in dis_total:
        setdis.add(i)
    for i in setdis:
        counter_dis.update({i:[0,0]})

    for key, val in data_cus_total.items():
        list_cus.update({key:val})
        counter_dis[val.distance][1] += 1

    return redirect("/admin")

@app.route("/dashboard", methods=["GET","POS"])
def dashboard():
    return render_template("dashboard.html")

@app.route("/new_clerk", methods=["GET","POST"])
def new_page_clerk():
    if not session.get("index_session") and session.get("index_session") != 0:
        return render_template("init.html", value={"error": "0"})
    else:
        id = session.get("index_session")
        loconf = config.get(str(id))

        if loconf[0] == "True":
            category = "Group"
        else:
            category = loconf[0]
        requests = request.form.lists()
        key_form = [x for x in requests]
        result_search = []
        is_right = False
        check_pos = []
        pos_checked = ""
        time_checked = ""
        if  key_form[0][0] == "id_search":
            key = key_form[0][1][0]
            if category == "Group":
                for k,i in list_cus.items():
                    if i.compare_code(key):
                        if i.bib not in list_completed:
                            result_search.append(i.__dict__)
                        else:
                            pos_checked = str(i.pPOS)
                            time_checked = i.dtime
                if len(result_search) == 0 and pos_checked != "":
                    return render_template('search.html',value={"error": "5",
                                                                "POS": str(int(id) + 1),
                                                                "time": str(time_checked),
                                                                "id":session.get("index_session"),
                                                                "category":category})
                elif len(result_search) == 0 and pos_checked == "":
                    return render_template('search.html',value={"error": "3",
                                                                "POS": str(int(id) + 1),
                                                                "time": str(time_checked),
                                                                "id":session.get("index_session"),
                                                                "category":category})

                else:
                    return render_template("new_page_clerk.html",value={"data": result_search, "error": "2",
                                                                    "id": session.get("index_session"),
                                                                        "category": category})
            else:
                for k,i in list_cus.items():
                    if i.compare(key):
                        if i.distance == category:
                            if i.bib not in list_completed:
                                result_search.append(i.__dict__)
                                is_right = True
                            else:
                                pos_checked = str(i.pPOS)
                                time_checked = i.dtime
                        else:
                            check_pos.append(i.__dict__)
                print(result_search)
                if  len(result_search) != 0 and is_right:
                    return render_template("new_page_clerk.html",value={"data": result_search, "error": "1",
                                                                        "id":session.get("index_session"),
                                                                        "category":category})

                if len(result_search) == 0 and pos_checked != "":
                    return render_template('search.html',value={"error": "5",
                                                                "POS": str(int(id) + 1),
                                                                "time": str(time_checked),
                                                                "id":session.get("index_session"),
                                                                "category":category})

                elif len(check_pos) != 0:
                    return render_template('search.html',value={"error": "6",
                                                                "POS": str(int(id) + 1),
                                                                "time": str(time_checked),
                                                                "id":session.get("index_session"),
                                                                "category":category})

                elif len(check_pos) == 0 and pos_checked == "":
                    return render_template('search.html',value={"error": "3",
                                                                "POS": str(int(id) + 1),
                                                                "time": str(time_checked),
                                                                "id":session.get("index_session"),
                                                                "category":category})


@app.route('/modify', methods=["POST"])
def mo():
    form = request.form.lists()
    key_delete = [x for x in form]
    id = int(request.form.get("id_pos"))

    if len(key_delete) != 0:
        key_delete = key_delete[1][1]
        for i in key_delete:
            list_completed.append(i)
            cus = list_cus.get(i)
            cus.set_pickedup(datetime.now().__str__().split(".")[0])
            cus.set_pick(id)

    return redirect("/")







if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'memcached'
    app.run(debug=True,port=8000)