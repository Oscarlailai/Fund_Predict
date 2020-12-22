#!/usr/bin/env python
# coding: utf-8

# In[6]:


import requests
from bs4 import BeautifulSoup
import xlrd
import xlwt
from bs4 import BeautifulSoup
import datetime
import time
import json
from os.path import join

def two_fund(): #建立Json與抓取基金資料並計算估值
    number=["1","2","3","4","5","6","7","8","9","10"]
    global stockdetail
    global count
    global total
    data_dict={}
    stockdetail=[]#名稱 漲跌 漲跌率
    count = [] #漲跌 持股
    total = [] #漲跌*持股
    fundkey = ["F0GBR04SN3:FO","F0GBR05VWS:FO","F0GBR04AMX:FO"] #摩根A股分派 摩根A股累計  貝萊德A2
    filename = ['摩根基金-JPM美國(美元)-A股(分派)_十大持股','摩根基金-JPM美國(美元)-A股(累計)_十大持股','貝萊德世界科技基金 A2 美元_十大持股']
    datas = []
    sum1=0
    for keyin in fundkey:
        url = 'https://tw.stock.yahoo.com/fund/holdings/'+keyin
         
        r=requests.get(url)#要求進入上面網址
        soup = BeautifulSoup(r.text, 'html.parser')
        print(url)
        name1 = soup.find('h1',attrs={'class':'Fx(a) M(0) Fz(24px) Fw(b) Lh(32px) C($c-primary-text)'})
        print("name="+name1.text)
        pricename = soup.find('div',attrs={'class':'fh-price D(f) Mt(4px) Ai(fe)'})#抓取淨值和幣別的HTML
        price = pricename.find('span',attrs={'class':'Fz(40px) Fw(b) Lh(1) C($c-primary-text)'}).text#淨值
        name = pricename.find('span',attrs={'class':'Fz(16px) Fw(b) Lh(1.5) Mstart(8px) C($c-primary-text)'}).text#幣別
        change=pricename.find('span',attrs={'Mend(4px) Bds(s)'}).text#漲跌
        try:
            changepercent=pricename.find('span',attrs={'Fz(20px) Fw(b) Lh(1.4) D(f) Ai(c) C($c-trend-down)'}).text#帳跌率
        except:
            changepercent=pricename.find('span',attrs={'Fz(20px) Fw(b) Lh(1.4) D(f) Ai(c) C($c-trend-up)'}).text#帳跌率
        print(price,name,change,changepercent)
       
        fund = soup.find_all('section',attrs={'class':'P(24px) Bdrs(8px) Bgc($c-light-gray)'})#前十大持股在位置4，因此下方用切片取值的方式取出
        fundname = fund[-1].find_all('span',attrs={'class':'Fx(a) Mstart(4px) Fz(16px) C($c-primary-text)'})#前十大持股名稱
        fundrate = fund[-1].find_all('span',attrs={'class':'Fx(n) Mstart(16px) Fz(16px) C($c-primary-text)'})#前十大持股比例
        file = open(filename[sum1]+'.txt', 'r')
        for f in range(10):
            fundkey = file.readline()
            ans = fund_cuttime(fundkey)
            print("持股比 "+fundrate[f].text,end=" ")
            count.append(float(fundrate[f].text.replace("%",""))/100)
            print("持股*漲跌 ",round(count[0]*stockdetail[2],4))
            total.append(round(count[0]*stockdetail[2],4))
            
            stockdetail=[]
            count = []
        file.close()
        sum1 = sum1 + 1
        print("預估變動 ",sum(total),"估值 ",float(price)+sum(total))
        
        datas=[]
        datas.append(data_dict)
        chan = name1.text.replace('\n','')
        file = now.strftime("%Y%m%d_%H%M")
       
        total=[]
        print()

def found_fund(key,cutprice):#計算帳跌語抓取股票資料
    url1='https://tw.stock.yahoo.com/us/q?s='+key
     
    r=requests.get(url1)
    soup=BeautifulSoup(r.text,"html.parser")
    fin = soup.find_all('tr', attrs={'bgcolor': '#ffffff'})
    finname = soup.find_all('font',attrs={'color':'#F70000'})
    fund_name = finname[0].select('b')
    stockdetail.append(fund_name[0].text)
    print("股票名稱："+fund_name[0].text,end="")
    tableT1 = fin[1].select("font") 
    cc = fin[1].select("td") 
    end = cc[-2].text #收盤 
    pas = cutprice #切盤價
    stockdetail.append(str(float(tableT1[1].text)))#漲跌
    print("漲跌 "+tableT1[1].text,end=" ")
    if ',' in end:
        end = end.replace(',','')
    if ',' in str(pas):
        pas = pas.replace(',','')
    stockchange0 = round((float(pas)-float(end))/float(pas),3)#漲跌綠
    print("漲跌率 "+str(stockchange0)+'%',end='')
    stockdetail.append(stockchange0/100)
    count.append(float(tableT1[1].text))
    
def fund_cuttime(key): #抓10:30切盤值
    key = key.strip('\n')
    api_url = 'https://partner-query.finance.yahoo.com/v8/finance/chart/'+key+'?range=1d&comparisons=undefined&includePrePost=false&interval=2m&corsDomain=tw.stock.yahoo.com&.tsrc=yahoo-tw'
    headers = {
        'Host' : "<calculated when request is sent>",
        'User-Agent':"PostmanRuntime/7.26.8",
        'Accept':"*/*",
        'Accept-Encoding':"gzip, deflate, br",
        'Connection':"keep-alive"
    }
     
    response = requests.get(api_url,headers)
    json_dict = json.loads(response.text)

    cutprice = json_dict['chart']['result'][0]['indicators']['quote'][0]['close'][30]
    #print(cutprice)
    found_fund(key,cutprice)
    
now = datetime.datetime.now()
two_fund()


# In[ ]:





# In[ ]:




