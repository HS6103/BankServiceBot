#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
import json

# 載入 username 和 loki_key
# 若找不到 account.info 則設為 None
try:
    with open("account.info", encoding="utf-8") as f:
        accountDICT = json.load(f)
        username = accountDICT['username']
        toaster_key = accountDICT['toaster_key_small_corp']
        
except Exception:
    username = None
    loki_key = None

def main():
    # 使用 argparse 解析參數
    parser = argparse.ArgumentParser(description="Run toaster_line with a message")
    parser.add_argument("--msg", type=str, help="Message to process", required=True)
    args = parser.parse_args()

    # 傳入的字串參數
    categorySTR = "small_corp"  # 預設分類
    inputSTR = args.msg   # 接收的 msg 參數
    countINT = 1          # 預設數量

    resultDICT = getCopyToasterResult(categorySTR, inputSTR, count=countINT)
    score = resultDICT["result_list"][0]["score"]
    doc = resultDICT["result_list"][0]["document"]
    print((doc,score))
    
if __name__ == "__main__":
    from requests import post
    from time import sleep

    COPYTOASTER_URL = "https://api.droidtown.co/CopyToaster/API/V2/"
    COPYTOASTER_CALL_URL = "https://api.droidtown.co/CopyToaster/Call/"
    POST_INTERVAL_SEC = 5

    def getCopyToasterResult(categorySTR, inputSTR, count=15):
        payloadDICT = {
            "username": username,
            "copytoaster_key": toaster_key,
            "category": categorySTR,
            "input_str": inputSTR,
            "count": count
        }

        while True:
            response = post(COPYTOASTER_URL, json=payloadDICT)
            if response.status_code == 200:
                try:
                    resultDICT = response.json()
                    if resultDICT["status"]:
                        if resultDICT["progress_status"] == "processing":
                            sleep(POST_INTERVAL_SEC)
                            continue
                    return resultDICT
                except Exception as e:
                    return {"status": False, "msg": str(e)}
            else:
                return {"status": False, "msg": "HTTP {}".format(response.status_code)}

    main()
