import datetime
import requests
from requests.packages import urllib3
import xlrd
import bs4
import pymysql
import json
import time




idnnamelist = []
file = open("./fundlog.txt", "a")  

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "cookie": "jcsession=jHttpSession@1366c9d1",
}
data_dict={}
datas=[]

   


class Fund:
    def __init__(
        self, ID, name, value, change, changepercent
    ):  
        self.ID = ID  
        self.name = name 
        self.netValue = value  
        self.change = change  
        self.changepercent = changepercent  
        self.stock = []  

        self.predictValue = 0.0 
        self.predictChange = 0.0 
        self.predictChangepercent = 0.0  


def EveryFund():
    
    urlpage = "http://fund.api.cnyes.com/fund/api/v1/search/fund?order=priceDate&sort=desc&page=1&institutional=0&isShowTag=1&fundGroup=G1&onshore=1&fields=categoryAbbr,change,classCurrencyLocal,cnyesId,displayNameLocal,displayNameLocalWithKwd,forSale,forSale,inceptionDate,investmentArea,lastUpdate,nav,prevPrice,priceDate,return1Day,return1Month"
    respage = requests.get(urlpage, headers=headers, verify=False)
    
    dictspage = respage.json()
    
    for i in range(0, 3):
        idnnamelist.append([dictspage["items"]["data"][i]["cnyesId"],dictspage["items"]["data"][i]["displayNameLocal"]])
        print(idnnamelist[i][0]+" "+idnnamelist[i][1])
        

    for id in range(0, len(idnnamelist)):
        url = "http://fund.api.cnyes.com/fund/api/v1/funds/" + idnnamelist[id][0] + "/holdings"
        res = requests.get(url, headers=headers,verify=False)
        dicts = res.json()
        navurl = (
            "http://fund.api.cnyes.com/fund/api/v1/funds/"
            + idnnamelist[id][0]
            + "/nav?format=table&page=1"
        )
       
        list = getfundvalue(navurl) 

        idnnamelist[id] = Fund(
            idnnamelist[id][0], idnnamelist[id][1], round(list[0],4), round(list[1],2), round(list[2],2)
        ) 
        print(idnnamelist[id].ID + " " +idnnamelist[id].name)
        print("基金淨值： " + str(idnnamelist[id].netValue))
        print("基金漲跌： " + str(idnnamelist[id].change) )
        print("基金漲跌幅： " + str(idnnamelist[id].changepercent)+"%"+ "\n" )
        
        

        if res.status_code == 200:  
            for i in range(0, len(dicts["items"]["data"])):
                name = dicts["items"]["data"][i]["name"]
                ratio = round(dicts["items"]["data"][i]["value"] / 100,4) 
                code = NameToCode(name)
                a = Fund_Holdings(code) 
                if a[0] != [0.0,0.0]:
                    idnnamelist[id].predictChangepercent += float(a[[0][0]]* ratio/100)
                    idnnamelist[id].stock.append([name, ratio])
                    print(" 名稱："+idnnamelist[id].stock[i][0])
                    print(" 持有比率："+str(idnnamelist[id].stock[i][1]))
                    print(" 該股票波動佔基金漲跌： " + str(round(float(a[[0][0]]* ratio/100),4))+"\n")
                    number=["1","2","3","4","5","6","7","8","9","10"]
                    
                    
            
        elif res.status_code == 404:  
            print("non!")
            idnnamelist[id].stock.append("non")

        
        idnnamelist[id].predictValue = idnnamelist[id].netValue * (1 + idnnamelist[id].predictChangepercent)
        idnnamelist[id].predictChange=round(idnnamelist[id].netValue * idnnamelist[id].changepercent/100,4)
        print("估值:" + str(round(idnnamelist[id].predictValue, 4)))
        print("漲跌：" + str(round(idnnamelist[id].predictChange, 4)))
        print("漲跌幅：" + str(round(idnnamelist[id].predictChangepercent, 4)) + "\n")
        


        


    

   


def getfundvalue(navurl): 
    res = requests.get(navurl, headers=headers,verify=False)
    dicts = res.json()
    navlist = []
  
    navlist.append(dicts["items"]["data"][0]["nav"]) 
    navlist.append(dicts["items"]["data"][0]["change"]) 
    navlist.append(dicts["items"]["data"][0]["changePercent"])  
    return navlist

def NameToCode(name):
    book = xlrd.open_workbook("./stockCode.xls")
    sheet1 = book.sheets()[0]
    nrows = sheet1.nrows
    re = str(-1)
    for i in range(0, nrows):
        po = sheet1.cell(i, 8).value
        if name in po:
            re = str(int(sheet1.cell(i, 7).value))
            print("from list,", type(re))
            
    return re
        



def Fund_Holdings(id):
    print(" 股票ID： "+str(id))
    
    res = requests.get(
        "https://ws.api.cnyes.com/ws/api/v1/quote/quotes/TWS:"
        + id
        + ":STOCK",headers=headers,verify=False
    )
    
   
    info = res.json()  
    change = 0.0
    changeRate = 0.0
    if id != -1:
        if res.status_code == 200:
            if  info["data"][0]["11"] is None:
                print("fuk")
            change = round(info["data"][0]["11"],4)
            changeRate =round(info["data"][0]["56"],4)
             
                
            print(" 該股票的漲跌："+str(change)+" 元")
            print(" 該股票的漲跌幅："+str(changeRate)+"%" )
    return [changeRate, change]


now = datetime.datetime.now()
file.write(now.strftime("%Y-%m-%d %H:%M:%S") +" Program has been run.")
file.write("\n")
print(now.strftime("%Y-%m-%d %H:%M:%S"))
EveryFund()
file.close()
