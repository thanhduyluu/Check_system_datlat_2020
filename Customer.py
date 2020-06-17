import pandas as pd


class Customer:
    def __init__(self, bib, name, code, distance, passport, phone, email, DOB, size):
        self.bib = bib
        self.name = name
        self.code = code
        self.distance = distance
        self.passport = passport
        self.phone = phone
        self.email = email
        self.DOB = DOB
        self.size = size
        self.dtime = None
        self.pPOS = None
        self.name_picked = None
        self.phone_picked = None
        self.new_BIB = None
        self.new_name = None
        self.new_passport = None
        self.new_DOB = None
        self.new_phone = None
        self.new_email = None
        self.new_pPOS = None
        self.new_dtime = None

    def compare(self, string):
        return string == self.bib or string == self.name or string == self.code or string == self.passport or string == self.phone or string == self.email

    def compare_bib(self, string):
        return string == self.bib

    def compare_dis(self, string):
        return string == self.distance

    def compare_code(self, string):
        return string == self.code

    def set_dtime(self, dtime):
        self.dtime = dtime

    def set_pPOS(self, pPOS):
        self.pPOS = pPOS

    def set_new_pPOS(self, new_pPOS):
        self.new_pPOS = new_pPOS

    def set_new_dtime(self, dtime):
        self.new_dtime = dtime

    def set_name_picked(self, name):
        self.name_picked = name

    def set_phone_picked(self, phone):
        self.phone_picked = phone

    def edit(self, list_attribute):
        self.new_BIB = list_attribute[0]
        self.new_name = list_attribute[1]
        self.new_passport= list_attribute[2]
        self.new_DOB = list_attribute[3]
        self.new_phone = list_attribute[4]
        self.new_email = list_attribute[5]


def read_data(path):
    df = pd.read_excel(path)
    bib = [str(x) for x in df["BIB NUMBER"]]
    name = [str(x) for x in df["Attendent Name"]]
    code = [str(x) if str(x) != "nan" else "Không có" for x in df["Invoice No"]]
    passport = [str(x) if str(x) != "nan" else "Không có" for x in df["ID/Passport"]]
    phone = [str(x) if str(x) != "nan" else "Không có" for x in df["Phone Number"]]
    email = [str(x) if str(x) != "nan" else "Không có" for x in df["Email"]]
    DOB = [str(x) if str(x) != "nan" else "Không có" for x in df["DOB"]]
    size = [str(x) if str(x) != "nan" else "Không có" for x in df["T_shirt"]]
    dis = list()
    setdis = set()
    for x in df["Attendent ticket type name"]:
        dis.append(x)
        setdis.add(x)

    list_cus = []
    for i in range(0, len(bib)):
        list_cus.append(Customer(bib[i], name[i], code[i], dis[i], passport[i], phone[i], email[i], DOB[i],size[i]))
    return dict(zip(bib, list_cus)), setdis


if __name__ == '__main__':
    read_data()
