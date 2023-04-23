#0.05 START
import requests
import json
from datetime import datetime, timedelta
import logging

def ConvertToBookID(name):
    bookName = {
        "摩羯座": "mt_b17",
        "水瓶座": "mt_b16",
        "雙魚座": "mt_b1",
        "牡羊座": "mt_b2",
        "金牛座": "mt_b3",
        "雙子座": "mt_b4",
        "獅子座": "mt_b6",
        "處女座": "mt_b7",
        "天秤座": "mt_b8",
        "天蠍座": "mt_b9",
        "射手座": "mt_b10",
        "金星": "mt_b11",
        "木星": "mt_b12",
        "水星": "mt_b13",
        "火星": "mt_b14",
        "土星": "mt_b15",
        "充電站": "mt_h1",
        "加油站": "mt_h2",
        "VIP Room": "mt_vip_01"
    }
    return bookName[name]

def BookCheck(book_Name, book_Time):
    debug=False
    book_Id=ConvertToBookID(book_Name)
    if book_Id == "":
        return "無此會議室"
    
    book_obj = datetime.strptime(book_Time, "%Y-%m-%d %H:%M:%S")

    dateStart =  book_obj.strftime("%Y-%m-%d")
    dateObj = book_obj+timedelta(days=1)
    dateEnd = dateObj.strftime("%Y-%m-%d")

    url = "https://meeting.wistronits.com/api/online/GetMTData"
    params = {
        "mt_room": book_Id,
        "date_begin": dateStart,
        "date_end": dateEnd,
    }
    response = requests.get(url, params=params)
    jsonObj = json.loads(response.text)

    logging.info(params)
    logging.info(response.text)
    #if debug:
    #    print(params)
    #    print(response.text)
    
    fnd="可預約"
    for i in range(len(jsonObj["data"])):
        logging.info(jsonObj["data"][i]["mt_start"])
        logging.info(jsonObj["data"][i]["mt_end"])
        #if debug:
        #    print(jsonObj["data"][i]["mt_start"], jsonObj["data"][i]["mt_end"])

        start_obj = datetime.strptime(jsonObj["data"][i]["mt_start"], "%Y-%m-%dT%H:%M:%S")
        end_obj = datetime.strptime(jsonObj["data"][i]["mt_end"], "%Y-%m-%dT%H:%M:%S")
        if start_obj <= book_obj <= end_obj:
            fnd="已被"+jsonObj["data"][i]["ad_display_name"]+"預約(會議時間:"+jsonObj["data"][i]["mt_start"]+"~"+jsonObj["data"][i]["mt_end"]+")"
    return book_Name + book_Time + fnd
#0.05 END