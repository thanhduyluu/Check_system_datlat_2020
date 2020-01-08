import pandas as pd
class Customer:
    def __init__(self,bib,name,code):
        self.bib = bib
        self.name = name
        self.code = code
    def compare(self,string):
        return string == self.bib or string == self.name or string == self.code
    def compare_bib(self,string):
        return string == self.bib
def read_data():
    df = pd.read_excel("static/ds.xlsx")
    bib = [str(x) for x in df["bib"]]
    name = [str(x) for x in df["name"]]
    code = [str(x) for x in df["code"]]
    list_cus = []
    for i in range(0,len(bib)):
        list_cus.append(Customer(bib[i], name[i], code[i]))
    return list_cus
if __name__ == '__main__':
    read_data()