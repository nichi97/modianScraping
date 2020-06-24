from bs4 import BeautifulSoup
import re
import requests
import urllib.parse
import pandas as pd

def getOngoingData(liElem):
    # get rid of money sign and comma, convert to int
    moneyAmt = liElem.select("p.status_title")[0].text.strip()[1:].replace(',','')
    title = liElem.select("h3.pro_title")[0].text
    supportAmt = liElem.find_all(lambda x: x.has_attr('backer_count'))[0].text
    supportRate = liElem.find_all(lambda x:x.has_attr('rate'))[0].text
    return (title, moneyAmt, supportAmt, supportRate, "众筹中")

def getFinishedData(liElem):
    # get rid of money sign and comma, convert to int
    moneyAmt = liElem.select("p.status_title")[0].text.strip()[1:].replace(',','')
    title = liElem.select("h3.pro_title")[0].text
    supportAmt = liElem.find_all(lambda x: x.has_attr('backer_count'))[0].text
    supportRate = liElem.find_all(lambda x:x.has_attr('rate'))[0].text
    return (title, moneyAmt, supportAmt, supportRate, "众筹成功")

def getCreativeData(liElem):
    title = liElem.select("h3.pro_title")[0].text
    observerStr = liElem.select("p.gray_ex")[0].text
    observerAmt = re.search(r'\d+', observerStr).group(0) # use regular expression to match the first number
    return (title, observerAmt,  "创意阶段" )

def getPreheatingData(liElem):
    title = liElem.select("h3.pro_title")[0].text
    subAmt = liElem.find_all(lambda x: x.has_attr('subscribe_count'))[0].text
    statusStr = liElem.select("p.status_title")[0].text.strip()
    startingDate = re.search(r'\d{4}-\d{2}-\d{2}', statusStr).group(0)
    return(title, subAmt, startingDate, "预热阶段")

def getFailedData(liElem):
    title = liElem.select("h3.pro_title")[0].text
    return(title, "众筹失败")
    



def getStatus(liElem):
    '''
    return 
    0 - 创意
    1 - 预热
    2 - 众筹中
    3 - 众筹成功
    4 - 众筹失败
    '''
    # if pro_fail class exists, this project failed
    failStatus = liElem.select("p.pro_fail")
    if failStatus:
        return 4

    # if there is span with appointment class, this is 预热阶段
    statusTitle = liElem.select("p.status_title")[0].text
    # if 创意阶段 -> 创意
    if "创意阶段" == statusTitle:
        return 0
    # If 开始 is in the status title, this is 预热
    elif "开始" in statusTitle:
        return 1
    elif "¥" in statusTitle:
        successLogo = liElem.select("div.pro_sucess_logo")
        # if there is success logo, return 众筹成功
        if successLogo:
            return 3
        else:
            return 2

baseURL = "https://zhongchou.modian.com/all/top_time/all"
maxPage = 226

# create list of urls
urlList = [baseURL+f'/{i}' for i in range(maxPage)]

creativeList = []
preheatingList = []
onGoingList = []
finishedList = []
failedList = []
for idx, url in enumerate(urlList):
    print(idx)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # select each li element, compile them into a list
    li_list = soup.select("ul.pro_ul > *")
    
    for li in li_list:
        status = getStatus(li)
        if status == 0:
            creativeList.append(getCreativeData(li))
        elif status == 1:
            preheatingList.append(getPreheatingData(li))
        elif status == 2:
            onGoingList.append(getOngoingData(li))
        elif status == 3:
            finishedList.append(getFinishedData(li))
        elif status == 4:
            failedList.append(getFailedData(li))
            
# convert each list and save them

creativeData = pd.DataFrame(creativeList , columns = ['Title', 'Interested people amount', 'Status'])
creativeData.to_excel('creativeData.xlsx')

preheatingData = pd.DataFrame(preheatingList, columns = ['Title', 'Supporter Amount', 'Starting Date', 'Status'])
preheatingData.to_excel('preheatingData.xlsx')

onGoingData = pd.DataFrame(onGoingList, columns = ['Title', 'Supported Money', 'Supporter Amount', 'Supported Rate', 'Status'])
onGoingData.to_excel('onGoingData.xlsx')

finishedData = pd.DataFrame(finishedList, columns = ['Title', 'Supported Money', 'Supporter Amount', 'Supported Rate', 'Status'])
finishedData.to_excel('finishedData.xlsx')

failedData = pd.DataFrame(failedList, columns = ['Title', 'Status'])
failedData.to_excel('failedData.xlsx')





