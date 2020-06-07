import pandas as pd
class Customer:
    def __init__(self,bib,name,code,distance,passport,phone,email,DOB):
        self.bib = bib
        self.name = name
        self.code = code
        self.distance = distance
        self.passport = passport
        self.phone = phone
        self.email = email
        self.DOB = DOB
        self.pickup = None
        self.dtime = None
        self.pPOS = None
        self.name_picked = None
        self.phone_pidcked = None

    def compare(self,string):
        return string == self.bib or string == self.name or string == self.code or string == self.passport or string == self.phone or string == self.email

    def compare_bib(self,string):
        return string == self.bib

    def compare_dis(self,string):
        return string == self.distance

    def compare_code(self,string):
        return string == self.code

    def set_pickedup(self, dtime):
        self.pickup = True
        self.dtime = dtime
    def set_pick(self,pPOS):
        self.pPOS = pPOS

def read_data(path):
    df = pd.read_excel(path)
    bib = [str(x) for x in df["BIB NUMBER"]]
    name = [str(x) for x in df["Attendent Name"]]
    code = [str(x) if str(x) != "nan" else "Không có" for x in df["Invoice No"]]
    passport = [str(x) if str(x) != "nan" else "Không có" for x in df["ID/Passport"]]
    phone = [str(x) if str(x) != "nan" else "Không có" for x in df["Phone Number"]]
    email = [str(x) if str(x) != "nan" else "Không có" for x in df["Email"]]
    DOB = [str(x) if str(x) != "nan" else "Không có"  for x in df["DOB"]]
    dis = list()
    setdis = set()
    for x in df["Attendent ticket type name"]:
        dis.append(x)
        setdis.add(x)

    list_cus = []
    for i in range(0,len(bib)):
        list_cus.append(Customer(bib[i], name[i], code[i],dis[i],passport[i],phone[i],email[i],DOB[i]))
    return dict(zip(bib,list_cus)),setdis
if __name__ == '__main__':
    read_data()