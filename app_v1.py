from flask import Flask, render_template, request, session, flash, send_file,redirect
from Customer import read_data,Customer
import os
from datetime import datetime
import pandas as pd
import string
import random
import json
import requests

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
number_POS = 20
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
        s += i[0] + "\t" + i[1] + "\t"  + str(i[2]) + "\t" + str(i[3]) + "\t" + str(i[4]) + "\n"
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
            list_cus.get(tmp[0]).set_phone_pick(tmp[4])
            list_cus.get(tmp[0]).set_name_pick(tmp[3])



def load_backup(content):
    for key, val in dict(content).items():
        list_completed.append(val["bib"])
        cus = Customer(val["bib"], val["name"], val["code"], val["distance"], val["passport"], val["phone"], val["email"], val["DOB"],val["size"])
        cus.set_name_picked(val["name_picked"])
        cus.set_phone_picked(val["phone_picked"])
        cus.set_pPOS(val["pPOS"])
        cus.set_dtime(val["dtime"])
        cus.edit([val["new_BIB"],val["new_name"],val["new_passport"],val["new_DOB"],val["new_phone"],val["new_email"]])
        cus.set_new_dtime(val["new_dtime"])
        cus.set_new_pPOS(val["new_pPOS"])

        list_cus.update({key:cus})

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
    url = "http://47.241.0.30/api/getcomplete"
    resp = requests.post(url=url)
    print(resp)
    print(resp.json())
    content = json.loads(resp.json())
    print(content)
    load_backup(content)

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

    if id > 20 or id < 0:
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

@app.route('/getall',methods=["GET","POST"])
def downloadFileAll ():

    data_file = {"bib":[],
                 "name":[],
                 "code":[],
                 "distance":[],
                 "passport":[],
                 "phone":[],
                 "DOB":[],
                 "T-shirt": [],
                 "dtime":[],
                 "pPOS":[],
                 "name_picked":[],
                 "phone_pidcked": [],
                 "T_shirt":[],
                 "new_bib":[],
                 "new_name":[],
                 "new_passport":[],
                 "new_DOB": [],
                 "new_phone": [],
                 "new_email":[],
                 "new_pPOS":[],
                 "new_dtime":[]


                 }

    for key, cus in list_cus.items():

        data_file.get("bib").append((cus.bib))
        data_file.get("name").append((cus.name))
        data_file.get("code").append((cus.code))
        data_file.get("distance").append((cus.distance))
        data_file.get("passport").append((cus.passport))
        data_file.get("phone").append((cus.phone))
        data_file.get("DOB").append((cus.DOB))
        data_file.get("T_shirt").append((cus.size))
        data_file.get("dtime").append((cus.dtime))
        data_file.get("pPOS").append(cus.pPOS)
        data_file.get("name_picked").append((cus.name_picked))
        data_file.get("phone_pidcked").append((cus.phone_pidked))
        data_file.get("new_bib").append((cus.new_BIB))
        data_file.get("new_name").append((cus.new_name))
        data_file.get("new_passport").append((cus.new_passport))
        data_file.get("new_DOB").append((cus.new_DOB))
        data_file.get("new_email").append((cus.new_email))
        data_file.get("new_phone").append((cus.new_phone))
        data_file.get("new_pPOS").append((cus.new_pPOS))
        data_file.get("new_dtime").append((cus.set_new_dtime))


        data_file.get("phone_pidcked").append((cus.phone_pidcked))
    df = pd.DataFrame.from_dict(data_file)
    name_file = path_result + "/resutl.xlsx"

    df.to_excel(name_file)
    return send_file(name_file, as_attachment=True)

@app.route('/clear-backup')
def clear():
    rm_all(path_backup)
    rm_all(path_result)
    return admin()

@app.route("/cf",methods=["GET","POST"])
def cf():
    if not session.get('logged_in'):
        return render_template('login.html', error="0")
    else:
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
        if len(key_form) == 0:
            return  redirect("/")
        result_search = []
        is_right = False
        check_pos = []
        pos_checked = ""
        time_checked = ""
        name_pick = ""
        phone_pick = ""
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
                            name_pick = i.name_picked
                            phone_pick = i.phone_picked
                if len(result_search) == 0 and pos_checked != "":
                    return render_template('search.html',value={"error": "5",
                                                                "POS": str(int(id) + 1),
                                                                "pos_check":(int(pos_checked) + 1),
                                                                "time": str(time_checked),
                                                                "phone_pick": str(phone_pick),
                                                                "name_pick":str(name_pick),
                                                                "id":session.get("index_session"),
                                                                "category":category})
                elif len(result_search) == 0 and pos_checked == "":
                    return render_template('search.html',value={"error": "3",
                                                                "POS": str(int(id) + 1),
                                                                 "pos_check":(int(pos_checked) + 1),
                                                                "time": str(time_checked),
                                                                "phone_pick": str(phone_pick),
                                                                "name_pick":str(name_pick),
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
                                name_pick = i.__dict__.get("name_picked")
                                phone_pick = i.__dict__.get("phone_picked")
                                print(name_pick)
                                print(phone_pick)

                        else:
                            check_pos.append(i.__dict__)

                if  len(result_search) != 0 and is_right:
                    return render_template("new_page_clerk.html",value={"data": result_search, "error": "1",
                                                                        "id":session.get("index_session"),
                                                                        "category":category})

                if len(result_search) == 0 and pos_checked != "":
                    return render_template('search.html',value={"error": "5",
                                                                "POS": str(int(id) + 1),
                                                                "pos_check":str(int(pos_checked) + 1),
                                                                "time": str(time_checked),
                                                                "phone_pick": str(phone_pick),
                                                                "name_pick":str(name_pick),
                                                                "id":session.get("index_session"),
                                                                "category":category})

                elif len(check_pos) != 0:
                    return render_template('search.html',value={"error": "6",
                                                                "POS": str(int(id) + 1),
                                                                 "pos_check":(int(pos_checked) + 1),
                                                                "time": str(time_checked),
                                                                "phone_pick": str(phone_pick),
                                                                "name_pick":str(name_pick),
                                                                "id":session.get("index_session"),
                                                                "category":category})

                elif len(check_pos) == 0 and pos_checked == "":
                    return render_template('search.html',value={"error": "3",
                                                                "POS": str(int(id) + 1),
                                                                "time": str(time_checked),
                                                                "id":session.get("index_session"),
                                                                "category":category})


@app.route('/modify', methods=["POST"])
def modif():
    form = request.form.lists()
    key_delete = [x for x in form]
    id = int(request.form.get("id_pos"))

    if len(key_delete) != 0:

        name_picked = key_delete[2][1][0]
        phone_picked = key_delete[3][1][0]
        if name_picked == "":
            cus = list_cus.get(key_delete[1][1][0])
            name_picked = cus.name
            phone_picked = cus.phone
        key_delete = key_delete[1][1]
        content_save = []
        for i in key_delete:
            list_completed.append(i)
            cus = list_cus.get(i)
            cus.set_pPOS(id)
            cus.set_dtime(datetime.now().__str__().split(".")[0])
            cus.set_name_picked(name_picked)
            cus.set_phone_picked(phone_picked)
            content_save.append([i ,datetime.now().__str__().split(".")[0], id, name_picked, phone_picked])
            send(cus.__dict__)
            resp = send_choanhthang(cus,"pick")

        save_compelete(content_save)
    return redirect("/")

@app.route('/change', methods=["GET", "POST"])
def changeinfo():
    key_search = request.form.get("id_search")
    form = request.form.lists()
    key_change = [x for x in form]

    if key_search != None:
        cus = list_cus.get(key_search)
        if cus is None:
            return render_template("changeinfo.html", value={"error":"3"})
        return render_template("changeinfo.html", value={"data": [cus.__dict__],
                                                         "error": "1"})
    if len(key_change) != 0:
        try:
            cus = list_cus.get(key_change[1][1][0])
        except:
            cus = list_cus.get(key_change[0][1][0])
        if cus is None:

            list_attribute = key_change[0][1]
            cus = Customer(list_attribute[0],list_attribute[1],"khong co",list_attribute[5],list_attribute[2]
                           ,list_attribute[4],list_attribute[6],list_attribute[3])
            cus.dtime = datetime.now()
            cus.name_picked = list_attribute[1]
            cus.phone_pidcked = list_attribute[6]
            cus.pPOS = "POS INFOMATION"
            list_cus.update({list_attribute[0] : cus})
            send(cus.__dict__)
            send_choanhthang(cus,"new")


            return render_template("changeinfo.html", value={"error": "4"})
        else:
            cus.edit(key_change[0][1])
            cus.set_new_pPOS("POS INFORMATION")
            cus.set_new_dtime(datetime.now().__str__().split(".")[0])
            send(cus.__dict__)
            send_choanhthang(cus,"update")


            return render_template("changeinfo.html", value={"error": "5"})

    return render_template("changeinfo.html", value={"error":"2"})

def ob2json_pick(cus, type):
    name = str(cus.new_name).split(" ")
    event_id = "5ed8a1585b16db5f7605efb4"
    if type == "pick":
        data_request = {
            "event_id": event_id,
            "bib": cus.bib,
            "pos": cus.pPOS,
            "pick_time":cus.dtime,
            "name_pick":cus.name_picked,
            "phone_pick":cus.phone_picked

        }
    if type == "update":
        data_request = {
            "event_id": event_id,
            "bib": cus.bib,
            "new_data": {
                "bib": cus.new_BIB,
                "first_name": "".join(name[-1]),
                "last_name": " ".join(name[:len(name) - 1]),
                "full_name": str(cus.name),
                "age": 0,
                "gender": "",
                "category_name_vi": cus.distance,
                "category_name_en": cus.distance,
                "group": "",
                "email": cus.new_email,
                "phone": cus.new_phone,
                "id_card": cus.new_passport,
                "blood_type": "",
                "nationality": "",
                "club": "",
                "name_on_bib": "",
                "emergency_contact_name": "",
                "emergency_contact_relationship": "",
                "emergency_contact_phone": "",
                "medicine": "",
                "allergy": "",
                "tshirt_size": "",
                "old_bib": cus.bib,
                "birthday_month": "string",
                "birthday_day": "string",
                "birthday_year": "string",
                "birthday": cus.new_DOB,
                "pos": cus.pPOS,
                "pick_time": cus.dtime,
                "name_pick": cus.name_picked,
                "phone_pick": cus.phone_picked

            }
        }

    return data_request

def send(data):
    url = "http://47.241.0.30/api/complete"
    resp = requests.post(url=url,json=data)
    return resp

def send_choanhthang(data,type):
    url = "https://uat.raceez.vn/api/result/internal/participants/race-kit"
    header = {
        "Authorization": "Basic ZTVhNTc5ZDctZDFlMC00OGFjLTk1ZGItN2UzNThhYTVjYjJiOjRiMWM1MDk4MzAwNGY0MGRiYTljNjk2MTM3MDA1NGNm"
    }

    data_send = ob2json_pick(data,type)
    print(data_send)
    resp = requests.post(url=url,json=data_send,headers=header)
    print("==========================================================")
    print(resp.json())
    return resp.json()

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'memcached'
    app.run(debug=True,port=8000)