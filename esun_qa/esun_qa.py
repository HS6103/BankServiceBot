#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki 4.0 Template For Python3

    [URL] https://api.droidtown.co/Loki/BulkAPI/

    Request:
        {
            "username": "your_username",
            "input_list": ["your_input_1", "your_input_2"],
            "loki_key": "your_loki_key",
            "filter_list": ["intent_filter_list"] # optional
        }

    Response:
        {
            "status": True,
            "msg": "Success!",
            "version": "v223",
            "word_count_balance": 2000,
            "result_list": [
                {
                    "status": True,
                    "msg": "Success!",
                    "results": [
                        {
                            "intent": "intentName",
                            "pattern": "matchPattern",
                            "utterance": "matchUtterance",
                            "argument": ["arg1", "arg2", ... "argN"]
                        },
                        ...
                    ]
                },
                {
                    "status": False,
                    "msg": "No matching Intent."
                }
            ]
        }
"""

from copy import deepcopy
from glob import glob
from importlib import import_module
from pathlib import Path
from requests import post
from requests import codes
import json
import math
import os
import re

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

lokiIntentDICT = {}
for modulePath in glob("{}/intent/Loki_*.py".format(BASE_PATH)):
    moduleNameSTR = Path(modulePath).stem[5:]
    modulePathSTR = modulePath.replace(BASE_PATH, "").replace(".py", "").replace("/", ".").replace("\\", ".")[1:]
    globals()[moduleNameSTR] = import_module(modulePathSTR)
    lokiIntentDICT[moduleNameSTR] = globals()[moduleNameSTR]

LOKI_URL = "https://api.droidtown.co/Loki/BulkAPI/"
try:
    accountInfo = json.load(open(os.path.join(BASE_PATH, "account.info"), encoding="utf-8"))
    USERNAME = accountInfo["username"]
    LOKI_KEY = accountInfo["loki_key"]
except Exception as e:
    print("[ERROR] AccountInfo => {}".format(str(e)))
    USERNAME = ""
    LOKI_KEY = ""

# 意圖過濾器說明
# INTENT_FILTER = []        => 比對全部的意圖 (預設)
# INTENT_FILTER = [intentN] => 僅比對 INTENT_FILTER 內的意圖
INTENT_FILTER = []
INPUT_LIMIT = 20

class LokiResult():
    status = False
    message = ""
    version = ""
    balance = -1
    lokiResultLIST = []

    def __init__(self, inputLIST, filterLIST):
        self.status = False
        self.message = ""
        self.version = ""
        self.balance = -1
        self.lokiResultLIST = []
        # filterLIST 空的就採用預設的 INTENT_FILTER
        if filterLIST == []:
            filterLIST = INTENT_FILTER

        try:
            result = post(LOKI_URL, json={
                "username": USERNAME,
                "input_list": inputLIST,
                "loki_key": LOKI_KEY,
                "filter_list": filterLIST
            })

            if result.status_code == codes.ok:
                result = result.json()
                self.status = result["status"]
                self.message = result["msg"]
                if result["status"]:
                    self.version = result["version"]
                    if "word_count_balance" in result:
                        self.balance = result["word_count_balance"]
                    self.lokiResultLIST = result["result_list"]
            else:
                self.message = "{} Connection failed.".format(result.status_code)
        except Exception as e:
            self.message = str(e)

    def getStatus(self):
        return self.status

    def getMessage(self):
        return self.message

    def getVersion(self):
        return self.version

    def getBalance(self):
        return self.balance

    def getLokiStatus(self, index):
        rst = False
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["status"]
        return rst

    def getLokiMessage(self, index):
        rst = ""
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["msg"]
        return rst

    def getLokiLen(self, index):
        rst = 0
        if index < len(self.lokiResultLIST):
            if self.lokiResultLIST[index]["status"]:
                rst = len(self.lokiResultLIST[index]["results"])
        return rst

    def getLokiResult(self, index, resultIndex):
        lokiResultDICT = None
        if resultIndex < self.getLokiLen(index):
            lokiResultDICT = self.lokiResultLIST[index]["results"][resultIndex]
        return lokiResultDICT

    def getIntent(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["intent"]
        return rst

    def getPattern(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["pattern"]
        return rst

    def getUtterance(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["utterance"]
        return rst

    def getArgs(self, index, resultIndex):
        rst = []
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["argument"]
        return rst

def runLoki(inputLIST, filterLIST=[], refDICT={}):
    resultDICT = deepcopy(refDICT)
    lokiRst = LokiResult(inputLIST, filterLIST)
    if lokiRst.getStatus():
        for index, key in enumerate(inputLIST):
            lokiResultDICT = {k: [] for k in refDICT}
            for resultIndex in range(0, lokiRst.getLokiLen(index)):
                if lokiRst.getIntent(index, resultIndex) in lokiIntentDICT:
                    lokiResultDICT = lokiIntentDICT[lokiRst.getIntent(index, resultIndex)].getResult(
                        key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex),
                        lokiResultDICT, refDICT, pattern=lokiRst.getPattern(index, resultIndex))

            # save lokiResultDICT to resultDICT
            for k in lokiResultDICT:
                if k not in resultDICT:
                    resultDICT[k] = []
                if type(resultDICT[k]) != list:
                    resultDICT[k] = [resultDICT[k]] if resultDICT[k] else []
                if type(lokiResultDICT[k]) == list:
                    resultDICT[k].extend(lokiResultDICT[k])
                else:
                    resultDICT[k].append(lokiResultDICT[k])
    else:
        resultDICT["msg"] = lokiRst.getMessage()
    return resultDICT

def execLoki(content, filterLIST=[], splitLIST=[], refDICT={}):
    """
    input
        content       STR / STR[]    要執行 loki 分析的內容 (可以是字串或字串列表)
        filterLIST    STR[]          指定要比對的意圖 (空列表代表不指定)
        splitLIST     STR[]          指定要斷句的符號 (空列表代表不指定)
                                     * 如果一句 content 內包含同一意圖的多個 utterance，請使用 splitLIST 切割 content
        refDICT       DICT           參考內容

    output
        resultDICT    DICT           合併 runLoki() 的結果

    e.g.
        splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？")                      # output => ["今天天氣"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？", splitLIST=splitLIST) # output => ["今天天氣", "後天氣象"]
        resultDICT = execLoki(["今天天氣如何？", "後天氣象如何？"])                # output => ["今天天氣", "後天氣象"]
    """
    resultDICT = deepcopy(refDICT)
    if resultDICT is None:
        resultDICT = {}

    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    if contentLIST:
        if splitLIST:
            # 依 splitLIST 做分句切割
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            inputLIST = []
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # 去除空字串
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # 不做分句切割處理
            inputLIST = contentLIST

        # 依 INPUT_LIMIT 限制批次處理
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST=filterLIST, refDICT=resultDICT)
            if "msg" in resultDICT:
                break

    return resultDICT

def testLoki(inputLIST, filterLIST):
    INPUT_LIMIT = 20
    for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
        resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)

    if "msg" in resultDICT:
        print(resultDICT["msg"])

def testIntent():
    # credit_card
    print("[TEST] credit_card")
    inputLIST = ['如何開卡','信貸申訴陳情','如何補寄簡訊','信用卡申訴陳情','如何停用信用卡','如何查詢結帳日','如何申請信用卡','信用卡遺失怎麼辦','如何使用紅利點數','如何更改戶籍地址','如何申請個人信貸','如何補寄電子帳單','信用卡利息如何計算','信貸繳款有哪些方式','如何查詢繳款截止日','結帳日是否可以更改','信用卡違約金如何計算','如何使用預借現金功能','如何更改銀行基本資料','如何登錄道路救援服務','如何設定預借現金密碼','如何變更我的中文姓名','辦卡有缺資料如何補件','如何補寄簡訊/電子帳單','信用卡繳款方式包含哪些','信用卡額度是否可以調整','個人信貸撥款時間要多久','個人信貸有哪些撥款方式','如何使用信用卡約定扣繳','如何更改信用卡帳單地址','如何查詢信用卡即時交易','如何查詢信用卡帳單金額','如何查詢信用卡繳款紀錄','如何查詢信用卡辦卡進度','如何查詢歷史的消費明細','如何查詢目前可用的額度','如何查詢預借現金的額度','如何計算預借現金手續費','拾獲本行信用卡該怎麼做','拾獲玉山信用卡該怎麼做','申請個人信貸的流程為何','繳款截止日是否可以更改','如何查詢信用卡之持卡狀況','如何查詢信用卡未請款消費','如何查詢個人信貸申辦進度','如何申請提前還款結清貸款','信用卡利息／違約金如何計算','如何查詢信用卡未入帳單交易','帳單有年費問題如何爭取減免','申辦額度調整缺資料如何補件','如何修改帳戶自動扣繳卡費資料','為什麼已經刷退卻還沒收到退款','申請個人信貸需要有玉山帳戶嗎','申請個人信貸需要準備哪些文件','信用卡不限金額消費通知如何設定','信用卡道路救援服務項目包含哪些','哪裡可以查詢信用卡優惠活動內容','如何設定每筆刷卡消費都收到通知','已經有向銀行貸款還可以再申請嗎','信用卡受損感應不良如何申請補換發','持信用卡在國外消費會收取什麼費用','提前還款是否須負擔提前清償違約金','收到逾期簡訊通知是否會有利息產生','如何查詢信用卡未請款消費或即時交易','對當月帳單的消費款項有疑問該怎麼做','TWQR跨機構購物交易是在哪一家商店消費','如何查詢推薦好友辦卡(MGM)是否符合資格','如何申請信用卡帳單使用他行帳戶自動扣繳','TWQR跨機構購物交易疑似遭冒用可以怎麼處理','有其他家銀行貸款是否可申請玉山信貸債務整合','TWQR跨機構購物交易疑似遭冒用或消費爭議可以怎麼處理']
    testLoki(inputLIST, ['credit_card'])
    print("")

    # digital_account
    print("[TEST] digital_account")
    inputLIST = ['如何完成補件','如何上傳照片檔','如何申請網路銀行','數位帳戶申辦流程','數位帳戶是否有存摺','可以不申請網路銀行嗎','數位帳戶享有哪些優惠','補件照片需要注意什麼','如何知道簽帳金融卡進度','數位帳戶可以郵寄銷戶嗎','數位帳戶的申辦資格為何','數位帳戶可以繳信用卡款嗎','數位帳戶可以進行哪些交易','數位帳戶可以開立子帳戶嗎','數位帳戶是否享有優惠利率','數位帳戶是否有提供金融卡','數位帳戶的金融卡要開卡嗎','為什麼我不能申請數位帳戶','為什麼我無法登入補件網頁','驗證有版本或系統的限制嗎','Email驗證超過限制次數怎麼辦','各類數位帳戶的轉帳限額為何','如何知道我已經成功完成補件','如何補換發數位帳戶的金融卡','忘記自然人憑證密碼如何處理','數位帳戶可以作為撥貸帳戶嗎','數位帳戶可以作為薪轉帳戶嗎','數位帳戶有提供哪些臨櫃交易','每人能申請幾個玉山數位帳戶','申請數位帳戶需準備哪些資料','自然人憑證未通過驗證怎麼辦','逾補件期限未完成補件怎麼辦','所有瀏覽器下都可以進行驗證嗎','數位帳戶可以作為證券交割戶嗎','數位帳戶可以接受國外匯入款嗎','數位帳戶金融卡可以國外提款嗎','為什麼一直無法收到簡訊驗證碼','為什麼我收到數位帳戶補件通知','申請數位帳戶後如何拿到金融卡','一直未收到簽帳金融卡該如何處理','信用卡未開卡是否會影響開戶申請','信用卡被管制是否會影響開戶申請','如何確定我的讀卡機是否安裝成功','數位帳戶可以約定為代扣繳帳號嗎','數位帳戶可以進行國外匯出匯款嗎','申請數位帳戶上傳資料有什麼限制','完成補件請問需要多久才能完成審核','數位帳戶可以約定ACH委託轉帳扣款嗎','數位帳戶金融卡可以變更寄送地址嗎','驗證之前需要先進行讀卡機的安裝嗎','如果身分證件資料辨識結果錯誤怎麼辦','數位帳戶之金融卡可以使用轉帳功能嗎','數位帳戶作為證券交割戶時有什麼限制','有數位帳戶可在臨櫃開一般存款帳戶嗎','若領補換資訊超過限制查詢次數怎麼辦','審核期間可以申請信用卡版的網路銀行嗎','數位帳戶可以進行PayPal連結及提領服務嗎','數位帳戶簽帳金融卡可以連結行動支付嗎','為什麼美國納稅義務人不能申請數位帳戶','申請數位帳戶時操作到一半斷線該怎麼辦','審核期間密碼輸入錯誤5次被暫停該怎麼辦','信用卡被管制或未開卡是否會影響開戶申請','已有本行臨櫃帳戶是否可以再申請數位帳戶','數位帳戶至臨櫃辦理業務需要支付手續費嗎','為什麼具他國或地區身分者不能申請數位帳戶','數位帳戶可以作為期貨帳戶的出入金約定帳戶嗎','審核期間忘記信用卡版網銀的使用者密碼該怎麼辦','如果已經有信用卡版的網路銀行是否還需要再次申請','已安裝元件但網頁還是一直顯示需下載安裝元件怎麼辦','如果沒完成數位帳戶申請下一次申請需要重新填寫資料嗎','變更過中文戶名且未至臨櫃更新資訊是否可申請數位帳戶','數位帳戶可以連結街口支付、一卡通Money等電子支付工具嗎','悠遊簽帳金融卡關閉簽帳功能後可以使用悠遊卡自動加值服務嗎','為什麼美國納稅義務人或具他國或地區身分者不能申請數位帳戶','審核期間忘記信用卡版網銀的使用者密碼或輸入錯誤5次被暫停該怎麼辦']
    testLoki(inputLIST, ['digital_account'])
    print("")

    # insurance
    print("[TEST] insurance")
    inputLIST = ['名詞解釋','如何申請理賠','網路投保可以取消嗎','出國多久前可以來投保','如何修改保單寄件地址','如何申辦提早領回年金','宣告利率要去哪裡查詢','年金受益人要如何變更','旅行平安險之保額限制','網路上找不到廠牌車型','可以改年金開始給付日嗎','後續服務是找保險公司嗎','網路投保有什麼應注意呢','網路投保的交易時間為何','規劃退休有適合的保險嗎','非本國籍可以購買保險嗎','國內旅行多久前可以來投保','如何進行玉山銀行網路投保','年金保險是否可以搭配附約','投保過程中有問題能詢問誰','旅行平安保險的商品有那些','網路投保需要具備哪些資格','如何申辦更改年金開始給付日','如何詢問出險或申請理賠問題','投保旅行平安保險之保額限制','旅行綜合險的繳費方式有什麼','是否有終身醫療保險可供參考','身故受益人有什麼身分限制嗎','需要英文投保證明應如何辦理','在國外是否還可投保旅行綜合險','旅行平安保險受益人可以指定誰','辦理網路投保一定要填寫e-mail嗎','可以用我的銀行帳戶幫家人投保嗎','旅行平安保險的「投保流程」為何','有沒有適合小朋友的保險規劃產品','網路投保完成後何時可收到保險單','網路投保完成後如何確定投保成功','寶貝剛出生應該規劃什麼樣的保險呢','已屆壯年的我應該規劃什麼樣的保險','年金給付的方式選擇要注意什麼限制','網路投保年金保險前應注意哪些事項','剛剛成家的我應該規劃什麼樣的保險呢','旅行平安保險的生效從什麼時間點開始','強制汽/機車責任保險是哪家保險公司呢','出發時還沒收到保單是否會影響保險效力','恢復扣繳續期每月定額保險費要如何申辦','是否可以透過網路投保線上執行提前解約','沒有玉山的帳戶還是可以透過網路投保嗎','網路投保過程中如何確認個人的身分驗證','續期每月定額保險費可否從他行帳戶扣款','一定要完成「網路投保註冊」才可以投保嗎','可以用我的銀行帳戶幫家人繳首期保險費嗎','續期每月定額保險費未扣款成功會通知我嗎','強制汽/機車責任保險到期前多久可以來投保','中國人壽更名為凱基人壽保單權益會受影響嗎','如何取得詳細的網路投保商品說明及保險條款','如何確認續期每月定額保險費是否有扣款成功','暫時停止扣繳續期每月定額保險費要如何申辦','沒有玉山的帳戶還是可以透過玉山臨櫃投保嗎','年金給付選擇一次給付或是分期給付的好處為何','未申請扣繳續期每月定額保險費將來要如何申辦','一次繳跟分期繳保費的對我的年金給付有什麼影響','可以用我的銀行帳戶幫家人投保及繳首期保險費嗎','投保時選擇年金一次給付或分期給付將來可以改嗎','沒有玉山的帳戶還是可以透過玉山臨櫃或網路投保嗎','申請續期每月定額保險費繳費成功後何時會開始扣款','透過玉山銀行進行網路投保如何確保我的交易安全性','一定要完成「網路投保註冊暨身分驗證」才可以投保嗎','每月定額保險費的宣告利率與投保時的宣告利率是一樣嗎','如果帳戶餘額不足導致扣款失敗續期每月定額保險費會停扣嗎','透過玉山投保只能向原服務人員所屬分行諮詢保險相關問題嗎','在玉山銀行查詢或下載任何網路投保的相關資訊是否需要另外付費']
    testLoki(inputLIST, ['insurance'])
    print("")

    # app
    print("[TEST] app")
    inputLIST = ['什麼是加入Siri','什麼是最近轉帳','如何使用付款碼','什麼是QR Code轉帳','如何使用加入Siri','夜間靜音服務為何','如何設定簡易密碼','如何變更圖形密碼','如何變更簡易密碼','無法下載行動銀行','無法更新行動銀行','若重複繳費怎麼辦','iOS如何綁定行動裝置','什麼是玉山行動銀行','如何不顯示圖形密碼','如何設定非約定轉帳','密碼之使用規則為何','如何取消加入Siri功能','如何變更Siri呼叫語音','什麼是行動銀行驗證碼','可查詢多久以前的訊息','哪些人可以使用台灣Pay','如何使用手機號碼收款','如何使用手機號碼轉帳','如何使用無卡提款服務','如何取消手機號碼轉帳','如何取消行動裝置綁定','如何申請玉山行動銀行','如何開通簡訊密碼服務','如何隱藏圖形密碼軌跡','iOS使用者如何設定Touch ID','什麼是手機號碼收款轉帳','什麼是玉山行動銀行認證','什麼是玉山銀行人臉辨識','台灣Pay相關功能限額多少','如何設定行動銀行驗證碼','無法下載或更新行動銀行','通知訊息可設定哪些項目','有支援哪些台灣Pay/TWQR功能','如何使用玉山銀行人臉辨識','如何獲得推播通知訊息服務','收不到簡訊驗證碼如何解決','無法登入圖形密碼如何解決','無法綁定圖形密碼如何解決','為何推播通知訊息鈴聲消失了','Touch ID被系統鎖定時該如何解除','台灣Pay相關功能是否有額度限制','如何在行動銀行中刪除常用帳號','如何在行動銀行中編輯常用帳號','忘記使用者名稱請問該如何辦理','想分享我轉帳的結果要如何操作','手機號碼轉帳的額度是怎麼計算','接不到玉山語音OTP電話如何解決','玉山行動銀行相關服務條款為何','如何查詢台灣Pay/TWQR相關交易紀錄','如何在行動銀行查詢安養信託帳號','使用TWQR功能若付款金額錯誤怎麼辦','為何Android使用者無法進行螢幕截圖','使用行動銀行應注意之安全事項為何','如何修改手機號碼收款所連結之帳號','如何在行動銀行中編輯刪除常用帳號','為什麼我無法透過手機號碼成功轉帳','如何在非約定轉帳使用行動銀行驗證碼','如何將玉山行動銀行App調整為深色模式','提升非約定轉帳限額後有哪些通路適用','玉山行動銀行自動登出的時間限制為何','Android使用者如何設定指紋人臉辨識登入','TWQR功能若消費完成後需退款該如何進行','如何變更我手機號碼收款功能的手機號碼','忘記使用者名稱或密碼了請問該如何辦理','操作行動銀行出現畫面空白時該如何解決','Android如何將玉山銀行快捷功能加入小工具','QR Code轉帳收款碼拆帳收款的計算方式為何','玉山行動銀行取用我行動裝置哪些授權項目','加入Siri功能可應用在玉山行動銀行哪些服務','為何我會在同一裝置收到二則以上相同的通知','為何我的信用卡繳款後沒有即時更新待繳金額','為何我的信用卡繳款後行動銀行沒有收到通知','為何於行動銀行設定約定他行同戶名帳號失敗','操作行動銀行出現「畫面空白」時，該如何解決','出現(K041)裝置驗證失敗請再試一次(416)訊息如何解決','可以透過行動銀行查詢到的信託帳號之信託種類為何','收不到簡訊驗證碼或接不到玉山語音OTP電話如何解決','只想開啟指紋或人臉辨識其中一種登入方式該如何設定','如何在行動銀行上查詢每月跨行提款及跨行轉帳優惠次數','如何在付款碼(台灣Pay)/TWQR功能中新增或刪除電子發票載具','轉帳紀錄沒有顯示在最近轉帳列表請問這樣是否有交易成功','哪些銀行APP可掃描玉山行動銀行之QR Code轉帳收款碼進行轉帳','是否可以同時將同一隻手機號碼在多個銀行的連結不同收款帳號','如果我變更留存於本行之簡訊密碼手機號碼原手機號碼還是會連結我的帳戶嗎','如果我註銷留存於本行之簡訊密碼(OTP)手機號碼原手機號碼還是會連結我的帳戶嗎','如果我變更留存於本行之簡訊密碼(OTP)手機號碼原手機號碼還是會連結我的帳戶嗎','如果我變更註銷留存於本行之簡訊密碼(OTP)手機號碼原手機號碼還是會連結我的帳戶嗎']
    testLoki(inputLIST, ['app'])
    print("")

    # deposit
    print("[TEST] deposit")
    inputLIST = ['如何列印扣繳憑單','分公司如何辦理開戶','定期儲蓄存款利息多少','如何辦理籌備處開立帳戶','證券交易明細要怎麼查詢','如何使用金融卡在國外提款','如何保障金融卡的使用安全','如何辦理非個人戶開立帳戶','玉山有哪幾種定期儲蓄存款','金融卡不慎遺失時該怎麼辦','轉帳誤入他人帳戶應如何處理','金融卡在國外提款手續費為何','如何辦理臺幣一般存款帳戶開戶','金融卡每日可以提款多少金額呢','金融卡每日可以轉帳多少金額呢','首次使用金融卡時應該注意些什麼呢','晚上8點還能用行動銀行作外幣定存嗎','沒時間到分行開戶是否可委託他人辦理','為什麼我領了存摺後都沒有之前的明細','金融卡每日可以轉帳及提款多少金額呢','借款利息為何現在變成是下個月1號扣呢','金融卡在國外提款每日限額及手續費為何','北海道也能利用金融卡提款有什麼樣的限制嗎','存款人亡故須徵提何種文件以辦理相關繼承事宜','晚上8點至ATM存款到玉山帳戶會從當日計算利息嗎','外來人口換發「新式統一證號」資料變更提醒事項','下午6點至網路銀行買賣外幣交易額度是算在明天嗎','下午6點至網路銀行買/賣外幣交易額度是算在明天嗎','營業日下午6點使用PayPal提領入新臺幣帳戶之交易額度是算於明日嗎']
    testLoki(inputLIST, ['deposit'])
    print("")

    # web_atm
    print("[TEST] web_atm")
    inputLIST = ['如何安裝pcscd','什麼是玉山WebATM','忘記密碼該怎麼辦','金融卡在國外可使用嗎','金融卡被鎖住該怎麼辦','TLS加密通訊協定調整教學','什麼是「勞動保障卡開卡」','登入WebATM時出現元件未更新','系統一直提示我插入晶片卡','使用玉山WebATM服務的基本條件','如何確定WebATM元件已安裝成功','如何確認Smart Card Service已啓動','透過金融卡交易的流程有哪些','「玉山WebATM」可以在國外使用嗎','如何確認讀卡機是否可正常運作','金融卡可以一直插在讀卡機上嗎','Edge瀏覽器無法正常顯示玉山WebATM','「玉山WebATM」有轉帳金額的限制嗎','如何確定WebATM讀卡機是否安裝成功','為什麼我不能進行非約定帳戶轉帳','Linux上使用玉山WebATM服務的基本需求','消費者透過金融卡交易的流程有哪些','WebATM轉帳成功對方卻表示未入帳怎麼辦','使用Windows 7時元件出現亂碼要怎麼排除','「繳費交易」和「轉出交易」有什麼不同','使用Internet Explorer 11為何WebATM網頁無法正常顯示網頁','下拉選單中沒有看到所安裝的讀卡機型號時應如何處理']
    testLoki(inputLIST, ['web_atm'])
    print("")

    # web_bank
    print("[TEST] web_bank")
    inputLIST = ['如何賣外幣','如何提升限額','如何加開子帳戶','如何進行基金贖回','如何進行基金轉換','如何進行外幣轉帳','如何開通簡訊密碼','無法使用WebATM元件','電話銀行服務內容','如何使用帳戶代扣繳','如何使用綜存轉定存','如何預約繳信用卡款','可以自行取消子帳戶嗎','如何使用代繳明細查詢','如何使用代繳項目終止','如何使用代繳項目變更','如何使用外匯存款結售','如何使用預約交易取消','如何使用預約交易查詢','如何申請基金單筆申購','如何設定約定轉入帳號','如何註銷約定轉入帳號','如何進行臺幣預約轉帳','忘記使用者名稱或密碼','如何設定分行/ATM驗證碼','TLS加密通訊協定調整教學','如何使用預約綜存轉定存','證券櫃檯有哪些服務項目','子帳戶可使用金融卡服務嗎','晶片金融卡被鎖住該怎麼辦','忘記晶片金融卡密碼該怎麼辦','請問我要如何使用帳戶代扣繳','如何使用網路銀行外幣匯出匯款','如何使用網路銀行繳交信用卡款','為什麼無法成功申請帳戶代扣繳','電腦版網路銀行要如何切換模式','如何使用代繳項目查詢/變更/終止','如何才能使用玉山銀行的網路銀行','為何我的臺幣轉帳之預約交易失敗','玉山的網路銀行何時可以開始使用','如何取消網路銀行約定轉入帳號服務','怎麼在電腦版網路銀行更改我的最愛','如何使用網路銀行之預約匯出匯款交易','如何於行動銀行申請基金定期定額申購','電腦版網路銀行要如何切換回完整模式','怎麼沒在電腦版看到能夠切換模式的按鈕','提升非約定轉帳限額後，有哪些通路適用','讀卡機未符合玉山銀行晶片金融卡元件要求','電腦版網路銀行的精簡模式怎麼找更多服務','如何於網路/行動銀行申請基金定期定額申購','怎麼在電腦版網路銀行更改我的最愛裡面的功能','個網銀行動銀行暨數位身分核驗安全宣告注意事項','為什麼進行子帳戶線上銷戶時出現資料輸入錯誤訊息','玉山個人網路銀行使用者名稱與密碼的設定規則為何','讀卡機未符合玉山銀行晶片金融卡元件(WebATM元件)要求','帳戶代扣繳服務如遇帳戶餘額不足是否會動用定存質借','為什麼我會收到玉山網路銀行暨行動銀行帳戶安全提醒通知','在網路銀行進行外幣涉及結匯交易申報書的電子簽章可以用那些方式進行身分驗證呢']
    testLoki(inputLIST, ['web_bank'])
    print("")

    # bsm
    print("[TEST] bsm")
    inputLIST = ['帳款疑義該怎麼處理','為什麼會收到退件通知','是否還會收到信用卡帳單','為什麼沒收到綜合對帳單','可以不要收到綜合對帳單嗎','收到退件通知會有什麼影響','為什麼無法開啟對帳單檔案','綜合對帳單是否可申請補發','綜合對帳單有哪些寄送方式','什麼時間點會收到綜合對帳單','如何變更綜合對帳單寄送方式','每個月都會收到綜合對帳單嗎','綜合對帳單內容包含哪些項目','下載綜合對帳單卻顯示查無資料','如何變更綜合對帳單的收件地址','是否還會收到理財或保險對帳單','電子綜合對帳單可以不要加密嗎']
    testLoki(inputLIST, ['bsm'])
    print("")

    # paypal
    print("[TEST] paypal")
    inputLIST = ['什麼是PayPal','什麼是玉山全球通','查無PayPal帳號權限','PayPal 帳號連結已失效','玉山全球通服務安全嗎','PayPal 餘額突然不能提領','如何查詢PayPal 提領明細','如何申請玉山全球通服務','有 PayPal 帳戶相關問題怎麼辦','提領 PayPal 款項的費用如何計算','為什麼操作 PayPal 連結一直失敗','什麼時候會使用玉山全球通服務','為什麼我不能提領入他行外幣帳戶','為什麼我約定他行臺幣帳戶會失敗','玉山全球通提供哪些PayPal提領功能','申請玉山全球通服務是否有資格限制','跨行提領申請註冊提供的佐證文件為何','數位帳戶可以進行PayPal連結及提領服務嗎','為什麼約定臺幣轉入帳號後還是不能提領','打完PayPal 帳號密碼並點選授權後仍無反應','提領 PayPal 款項是否有時間及金額上限限制','提領 PayPal 款項是否有最低提領金額之限制','甲的 PayPal 款項可以提領至乙的銀行帳戶嗎','PayPal 跨行提領可約定的臺幣入帳銀行有哪些','可以至玉山銀行臨櫃將 PayPal 款項提領出來嗎','為何還沒送出註冊資料卻收到審核失敗通知信','如何確認 PayPal 跨行帳戶基本資料修改失敗原因','如何確認 PayPal 跨行帳戶基本資料註冊失敗原因','打完PayPal 帳號密碼並點選授權後出現轉圈圈的畫面','如何確認 PayPal 跨行帳戶基本資料註冊/修改失敗原因','有玉山銀行帳戶我還能申請使用PayPal跨行提領服務嗎','透過玉山全球通確認提領 PayPal 款項後能否取消交易呢','跳出您尚未完成臺幣轉入帳號驗證敬請驗證的提醒視窗','提領 PayPal 款項至玉山銀行帳戶或其他銀行帳戶需多久時間才會入帳','修改PayPal跨行帳戶基本資料成功將資料送出後須等待多久會收到審核結果','註冊PayPal跨行帳戶基本資料成功將資料送出後須等待多久會收到審核結果','出現「身分證註冊資料不正確，請重新確認資料正確性。驗證錯誤累積達三次(含)，註冊功能將被鎖定30日。」如何處理']
    testLoki(inputLIST, ['paypal'])
    print("")

    # trust_fund
    print("[TEST] trust_fund")
    inputLIST = ['何謂信託','何謂信託借券','儲蓄信託最大特色為何','員工持股最大特色為何','本行信託業務包含哪些','有價證券信託的定義及特色','本行目前可辦理哪些保管業務','財產交付信託業者有什麼保障','員工持股/儲蓄信託最大特色為何','如欲辦理股票簽證業務該如何辦理','公司應於何時辦理其發行股票之簽證','企業辦理員工持股/儲蓄信託之優點為何','符合什麼條件之公司需辦理其股票簽證業務','為何外資欲進行國內投資需指定保管機構為代理人','來臺從事證券投資或期貨交易之大陸地區投資人以何為限','為何外資或陸資欲進行國內投資需指定保管機構為代理人']
    testLoki(inputLIST, ['trust_fund'])
    print("")

    # wealth
    print("[TEST] wealth")
    inputLIST = ['什麼是海外債券','何謂基金之轉換','如何買賣海外ETF','贖回款何時入帳','什麼是結構型商品','如何使用隨行理專','部分贖回有何條件','部分轉換有何條件','信託管理費如何計收','尊榮禮賓服務是什麼','海外ETF交易時間為何','玉山是否有親子帳戶','匯率的基準點如何決定','基金之轉換手續費為何','如何取消海外債券交易','如何進行海外債券交易','如何進行金融商品比較','常見的債券類型有哪些','投資海外債券適合我嗎','贖回款之淨值如何決定','基金之轉換有何限制條件','基金的交易有何時間限制','有哪些類型的結構型商品','申購基金應填寫哪些資料','申購基金應注意哪些事項','海外ETF/股票交易時間為何','如何查詢海外債券庫存損益','如何查詢海外債券成交結果','如何查詢海外債券產品條件','如何訂閱玉山理財電子週報','投資海外債券的風險是什麼','財富管理會員可享何種優惠','如何得知基金的最新淨值報價','如何決定海外股票的委託價格','投資結構型商品的風險是什麼','玉山財富管理是否有會員制度','要如何申請網路基金交易功能','基金的單位數與報酬率如何計算','投資海外ETF所需負擔的稅負為何','為何手續費及配息要按比例攤提','如何決定海外ETF/股票的委託價格','投信基金及境外基金淨值適用說明','海外ETF有哪些投資市場可提供選擇','投資海外ETF/股票所需負擔的稅負為何','「部分轉換」或「部分贖回」有何條件','如何使用財富管理專區的我的觀察清單','如何找到財富管理各項商品的最新公告','如何於行動銀行申請基金定期定額申購','海外ETF/股票有哪些投資市場可提供選擇','如何於網路/行動銀行申請基金定期定額申購']
    testLoki(inputLIST, ['wealth'])
    print("")

    # foreign
    print("[TEST] foreign")
    inputLIST = ['光票託收如何使用','光票託收如何兌現','國外的支票如何使用','國外的支票如何兌現','光票託收是否收取費用','如何查詢匯入款項進度','國外的支票是否收取費用','怎樣將款項匯給國外親友','如何收到外幣匯入匯款通知','如何使用網路銀行的外匯交易','是否有提供ATM提領外幣現鈔服務','是否有提供買賣外幣現鈔服務呢','網路銀行外匯交易的每日承作限額為','網路銀行外匯交易還需注意哪些事項','購買人民幣現鈔金額是否有相關限制','e 化通路承作外匯交易是否有時間限制','網路銀行外匯交易的承作匯率規定為何','日期處有註記「*」符號是代表什麼意思','金額前有標明「-」符號是代表什麼意思','人民幣外幣現鈔存入外幣帳戶有無金額限制','使用網路銀行外匯交易所需負擔的費用為何','外幣現鈔可否存入我在玉山銀行的外幣帳戶呢','玉山銀行外幣帳戶提領外幣現鈔是否需支付手續費','從國外匯入款項至我的玉山銀行帳戶我該提供什麼資料']
    testLoki(inputLIST, ['foreign'])
    print("")

    # china_pay
    print("[TEST] china_pay")
    inputLIST = ['如何退款','什麼是兩岸支付通','特店網站有哪些要求','特店網站有哪些限制','需要標示人民幣價格嗎','大陸消費者付款流程為何','撥款週期及撥款幣別為何','特店的販售商品有哪些要求','特店的販售商品有哪些限制','申請兩岸支付通需要準備哪些資料','兩岸支付通收款需要有支付寶帳號嗎','兩岸支付通服務可以收人民幣款項嗎','申請兩岸支付通服務需要支付哪些費用','可以透過兩岸支付通在淘寶網開店收款嗎','申請兩岸支付通服務需要開立外幣帳戶嗎','兩岸支付通服務是否會開立手續費用的收據','可以透過兩岸支付通儲值我的支付寶帳戶嗎','可以透過兩岸支付通提領回台灣的存款帳戶嗎','可以透過兩岸支付通讓大陸消費者在門市使用支付寶付款嗎']
    testLoki(inputLIST, ['china_pay'])
    print("")

    # cardless
    print("[TEST] cardless")
    inputLIST = ['如何開通無卡提款','忘記無卡交易密碼','變更無卡交易密碼','重設無卡交易密碼','行動無卡提款的限額','跨行無卡提款手續費','如何申請行動無卡提款','如何註銷行動無卡提款','無卡提款序號如何取消','無卡提款序號如何查詢','無卡提款序號逾時怎麼辦','外國人能否使用行動無卡提款','無卡交易密碼錯誤上限是幾次','玉山ATM可以進行跨行無卡提款嗎','可以至他行ATM進行跨行無卡提款嗎','一天可以預約幾筆行動無卡提款序號','身份證字號重號能否使用行動無卡提款','無卡交易密碼錯誤達到上限後應該怎麼辦','金融卡不見了還可以使用行動無卡提款嗎','玉山顧客可以至他行ATM進行跨行無卡提款嗎','開通行動無卡提款成功但是我的金融卡不見了','掛失金融卡需要再重新開通行動無卡提款服務嗎','更換金融卡需要再重新開通行動無卡提款服務嗎','補發金融卡需要再重新開通行動無卡提款服務嗎','APP預約行動無卡提款需於多久時間內至ATM進行交易','行動無卡提款之無卡交易密碼和刷臉提款之無卡交易密碼一樣嗎','開通時使用的金融卡會影響行動無卡提款時能選擇的提領帳戶嗎']
    testLoki(inputLIST, ['cardless'])
    print("")

    # customer_service
    print("[TEST] customer_service")
    inputLIST = ['電話銀行服務內容','行動裝置的系統需求','如何設定約定轉入帳號','如何請求停止電話行銷','語音密碼忘記該怎麼辦','語音密碼鎖住該怎麼辦','語音密碼忘記或鎖住該怎麼辦','不方便講電話如何聯繫客服中心','使用電話銀行時應該注意些什麼呢','申請電話銀行時應該注意些什麼呢','電話銀行轉帳服務有沒有什麼限制','玉山電話銀行台幣綜合存款轉定存服務相關規定']
    testLoki(inputLIST, ['customer_service'])
    print("")

    # crossboarding
    print("[TEST] crossboarding")
    inputLIST = ['手續費會退嗎','退款會退到哪裡','如何綁定郵局帳戶','如何進行外匯申報','跨境網購限額多少','退款匯率如何計算','樂享優惠專區是甚麼','哪些PayPay通路可以使用','哪裡可以使用玉山Wallet','如何了解樂享優惠活動','活動結束時會如何告知','如何使用獨樂樂的購物金','玉山電子支付帳戶是什麼','跨境網購提供了什麼服務','跨境網購是否有額度限制','如何註冊玉山電子支付帳戶','為何無法找到樂享優惠專區','跨境網購服務如何發動退款','身分證認證是否有次數限制','沒有收到驗證碼簡訊該怎麼辦','誰可以使用玉山Wallet電子支付','掃描店家QR Code的付款方式為何','如何提供玉山電子支付補件資料','如何提領玉山電子支付帳戶餘額','如何進行玉山電子支付帳戶儲值','如何驗證玉山電子支付帳戶姓名','為什麼眾樂樂的活動會突然不見','儲值完成後銀行帳號備註欄位為何','如何提升玉山電子支付的交易限額','跨境網購服務為什麼需要外匯申報','電子支付儲值是否會被收取手續費','如何使用玉山Wallet電子支付進行繳費','如何查詢玉山Wallet電子支付繳費紀錄','如何變更玉山電子支付帳戶手機號碼','我可以註冊多少組玉山電子支付帳戶','玉山Wallet電子支付支援哪些繳費項目','玉山電子支付帳戶的交易限額是多少','由店家掃描手機條碼的付款方式為何','身分證認證若多次認證失敗該怎麼辦','使用玉山Wallet電子支付交易失敗怎麼辦','如何查詢活動已結束超過六個月的活動','為什麼玉山電子支付身分證驗證會失敗','玉山Wallet電子支付交易資訊會保留多久','玉山Wallet電子支付交易資訊要怎麼查詢','玉山電子支付簡訊驗證是否有次數上限','誰可以使用玉山電子支付跨境網購服務','跨境網購的超商繳費是否會收取手續費','跨境網購的轉帳付款是否會收取手續費','未收到玉山電子支付Email驗證信該怎麼辦','玉山電子支付Email驗證信是否有時間限制','玉山Wallet電子支付可綁定哪些支付工具呢','玉山Wallet電子支付條碼付的付款方式為何','玉山電子支付帳戶可以綁定幾組提領帳號','逾期帳單可以用玉山Wallet電子支付繳費嗎','如何使用玉山電子支付—跨境網購轉帳付款','為什麼我沒收到玉山電子支付帳戶推播訊息','玉山Wallet電子支付重複繳交水費可以退款嗎','玉山電子支付帳戶提領是否會被收取手續費','開通電子支付帳戶，行動電話為何會被變更','可以使用信用卡儲值玉山電子支付帳戶餘額嗎','如何進行玉山電子支付行動電話驗證人工審核','支付日本PayPay掃碼付服務我需要有外幣帳戶嗎','玉山Wallet電子支付重複繳交水/電費可以退款嗎','使用玉山Wallet電子支付不小心重複繳費了怎麼辦','可使用哪些銀行帳戶做為玉山電子支付提領帳戶','如何設定玉山電子支付帳戶的常用提領銀行帳戶','提領玉山電子支付帳戶餘額至銀行帳戶需要多久','多久才能收到玉山電子支付—跨境網購服務的退款','忘記玉山電子支付網站帳戶登入的會員序號怎麼辦','跨境網購的轉帳付款及超商繳費是否會收取手續費','如何使用玉山電子支付—跨境網購超商繳費(不取貨)','使用玉山Wallet電子支付若發生退款情形我要如何處理','支付日本PayPay掃碼付服務是新臺幣扣款還是日圓扣款','如何查詢玉山電子支付—跨境網購交易紀錄與訂單狀況','為什麼使用玉山Wallet電子支付查詢電費帳單繳費會失敗','為什麼玉山電子支付身分認證結果顯示註冊資料審核中','該如何使用玉山Wallet電子支付於日本PayPay掃碼付服務呢','使用玉山Wallet電子支付若發生退款情形款項會退回至哪裡','如何使用玉山Wallet電子支付綁定水號並設定繳款提醒通知','為什麼我會收到簡訊通知辦理玉山電子支付帳戶定期審查','玉山Wallet電子支付於日本PayPay掃碼付服務的匯率怎麼換算','玉山Wallet電子支付綁定信用卡消費可以獲得信用卡回饋嗎','玉山電子支付帳戶款項轉出完成後銀行帳號備註欄位為何','為什麼使用玉山電子支付—跨境網購服務需要進行身分認證','為何會收到玉山電子支付帳戶通知儲值餘額已達上限的簡訊','如何使用玉山Wallet電子支付綁定水/電號並設定繳款提醒通知','為什麼我會收到簡訊通知「玉山電子支付身分驗證尚未完成」','跨境網購服務身分驗證時出現系統維護作業畫面我該如何處理','為什麼使用玉山Wallet電子支付查詢電費帳單/水費帳單繳費會失敗','出現「信用卡儲值付款交易已達限額，請選擇其他付款方式」怎麼辦','為什麼玉山電子支付身分認證結果顯示「啟用審核中，請稍後再試」','玉山Wallet電子支付「條碼付」(由店家掃描手機條碼) 的付款方式為何','玉山Wallet電子支付於日本PayPay掃碼付服務需要負擔國外交易服務費嗎','跨境網購服務身分驗證結果顯示「電支帳戶姓名未通過驗證」怎麼辦','玉山Wallet電子支付綁定信用卡儲值付款可以使用信用卡紅利點數折抵嗎','於玉山銀行補件平台上傳完成後為何仍顯示近六個月內「查無案件資訊」','為什麼使用玉山電子支付—跨境網購服務身分驗證的行動電話驗證會失敗','為何在日本PayPay商店使用玉山Wallet電子支付綁定該信用卡付款會付款失敗','玉山Wallet電子支付可以綁定非玉山銀行信用卡或銀行帳戶作為支付工具嗎']
    testLoki(inputLIST, ['crossboarding'])
    print("")

    # corporate
    print("[TEST] corporate")
    inputLIST = ['匯出匯款如何收費','外幣定存利率是多少','匯到大陸的時間要多久','外幣票據託收如何收費','外幣票據買入如何收費','如何知道已收到信用狀','外幣定存期間有哪些選擇','外幣收款如何自動化銷帳','外幣票據託收多久會入帳','如何匯款至玉山銀行帳戶','如何辦理公司代表人變更','提供哪些種類的外幣現鈔','外幣活期存款起存額是多少','如何申請辦理外幣票據託收','「全方位代收網」停止支援TLS','可以透過哪些方式開發信用狀','國外票據託收有受理的限制嗎','外幣票據託收、買入如何收費','匯款至國外一般需多久才能入帳','是否有承作遠期信用狀賣斷業務','買賣外幣現鈔需要收多少手續費','法人外幣帳戶開戶需準備什麼文件','可以透過哪些方式辦理匯出匯款交易','外幣活期存款與定期存款起存額是多少','如有未掛牌的特殊外幣匯款需求如何辦理','是否有承作Forfaiting (遠期信用狀賣斷)業務','從玉山銀行外幣帳戶提領外幣現鈔是否需支付費用','如何辦理公司、法人、團體（含管委會）代表人變更','辦理出口信用狀押匯與出口託收都需要申請授信額度嗎','如果沒有玉山銀行的授信額度可以辦理開立信用狀業務嗎']
    testLoki(inputLIST, ['corporate'])
    print("")

    # loan
    print("[TEST] loan")
    inputLIST = ['保證人資格為何','個人信貸是什麼','成績單如何繳交','房貸的流程為何','退學應如何還款','留學貸款期限為何','留學貸款額度為何','個人信貸需要費用嗎','所得清單應如何辦理','申請留學貸款之資格','留學貸款的利率為何','什麼是提前清償違約金','保證人是否有年齡限制','個人信貸期限最長多久','指數型房貸有什麼優點','留學貸款應於何時償還','MyData服務會取得哪些資料','MyData服務會取得那些資料','個人信貸利率最低為多少','多久可以收到貸款契約呢','成績單需於每年幾月繳交','如何使用玉山銀行IXML憑證','如何申請玉山銀行IXML憑證','入出國紀錄文件應如何辦理','家屬可否代為申請所得清單','我可以指定我的繳款日期嗎','我符合申請個人信貸資格嗎','理財型房貸要如何動用資金','留學貸款分期撥貸方式為何','降息對我的貸款有甚麼影響','個人信貸最高可以貸多少金額','如果提前清償貸款有無違約金','房貸簽約時需要攜帶哪些資料','申請留學貸款應檢附哪些文件','留學貸款之利息應該如何繳交','留學貸款之利息應該如何還款','降息對我的貸款有甚麼影響嗎','房屋貸款期間是否可以部分還款','理財型房貸的利息費用如何計算','申請房屋貸款需要準備哪些資料','逾期未還款者會有什麼不良後果','何處可查詢國外大專院校參考名冊','可以提前償還個人信貸全部本金嗎','可以提前償還個人信貸部分本金嗎','家屬可否代為申請入出國紀錄文件','留學貸款的申請人是否需要保證人','留學貸款的申請人為何需要保證人','留學貸款額度及分期撥貸方式為何','薪水多寡跟可以核貸的額度有關嗎','他國所設之分校是否可申貸留學貸款','信用貸款契約中貸款費用會收取幾筆','可否以有條件式入學許可申請本貸款','教育部採認規定之國外大學校院為何','遠距教學之學位是否可申貸留學貸款','住宅補貼如果有其他問題要向哪裡詢問','信用貸款繳款完畢後可以申請結清證明嗎','可以提前償還個人信貸部分或全部本金嗎','如何透過MyData服務將個人資料給玉山銀行','找代辦公司協助辦理貸款利率會比較好嗎','找代辦公司協助辦理貸款額度會比較高嗎','申請個人信貸後需要多久能知道貸款結果','申請留學貸款所訂之家庭年收入標準為何','留學貸款的申請人為何及是否需要保證人','留學貸款之利息及本金應該如何繳交及還款','若留學生在國外可否委託國內之人代為申請','信用貸款在打擊資恐相關法規會有什麼措施呢','信用貸款在防制洗錢相關法規會有什麼措施呢','信用貸款撥款前銀行會再次查我的聯徵資料嗎','工作建議滿多久後再申請貸款對我會比較有利','所修讀之學校學位需較長時間可否延長寬限期','申請留學貸款所訂之家庭年收入標準如何認定','僅由非原就讀學校頒發文憑是否可申貸留學貸款','在薪轉銀行申請貸款個人信貸會比較容易過件嗎','所修讀之學校學位需較長時間可否延長還款期限','所得不需報稅需檢附何種文件認定其家庭年收入','如何知道我的個人信貸每月應該繳款的金額是多少','返國後無法立即償還貸款是否可申請暫緩攤還本息','可否以有條件式入學許可(conditional offer)申請本貸款','依信用貸款契約在什麼情形下會縮短我的借款期限呢','家屬可否代為申請所得清單及留學生入出國紀錄文件','月繳月省房貸的利率減碼優惠是否適用於政策性貸款','信用貸款在防制洗錢及打擊資恐相關法規會有什麼措施呢','找代辦公司協助辦理貸款額度會比較高或利率會比較好嗎','沒收到MyData平台與玉山取檔成功的簡訊通知卻收到補件通知','使用MyData服務提供玉山銀行取用個人資料可在哪裡查詢相關紀錄','使用MyData服務取得相關財證時若發生系統異常導至無法授權或授權失敗該怎麼辦','已先申請到留學貸款者是否可以報考或申請我國政府提供之各項公費或留學獎助學金']
    testLoki(inputLIST, ['loan'])
    print("")

    # face_atm
    print("[TEST] face_atm")
    inputLIST = ['想更新刷臉ID','刷臉提款的限額','如何申請刷臉提款','如何註銷刷臉提款','變更無卡交易密碼','重設無卡交易密碼','如何使用刷臉來提款','刷臉提款時辨識失敗怎麼辦','設定刷臉ID有無特殊注意事項','無卡交易密碼錯誤上限是幾次','無卡交易密碼該如何重新設定呢','金融卡不見了還可以使用刷臉提款嗎','別人拿我的照片來使用刷臉提款怎麼辦','刷臉辨識時如何操作可提升辨識成功率','無卡交易密碼錯誤達到上限後應該怎麼辦','掛失金融卡需要再重新開通刷臉提款服務嗎','更換金融卡需要再重新開通刷臉提款服務嗎','補發金融卡需要再重新開通刷臉提款服務嗎','開通時使用的金融卡會影響刷臉提款時能選擇的提領帳戶嗎','行動無卡提款之無卡交易密碼和刷臉提款之無卡交易密碼一樣嗎']
    testLoki(inputLIST, ['face_atm'])
    print("")

    # line
    print("[TEST] line")
    inputLIST = ['可以設定幾個LINE帳號','如何更改通知訊息項目','如何於LINE查看通知訊息','如何取消LINE個人化通知服務','如何設定LINE個人化通知服務','LINE個人化通知服務提供哪些通知內容']
    testLoki(inputLIST, ['line'])
    print("")

    # small_corp
    print("[TEST] small_corp")
    inputLIST = ['如何申請小型企業貸款','小型企業貸款適用申請對象','如何知道哪種貸款模式最適合我','貸款申請到撥款會經過哪些流程','公司貸款跟個人貸款有什麼不一樣','申請小型企業貸款需要準備哪些文件呢']
    testLoki(inputLIST, ['small_corp'])
    print("")


if __name__ == "__main__":
    # 測試所有意圖
    testIntent()

    # 測試其它句子
    filterLIST = []
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    # 設定參考資料
    refDICT = { # value 必須為 list
        #"key": []
    }
    resultDICT = execLoki("今天天氣如何？後天氣象如何？", filterLIST=filterLIST, refDICT=refDICT)                      # output => {"key": ["今天天氣"]}
    resultDICT = execLoki("今天天氣如何？後天氣象如何？", filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT) # output => {"key": ["今天天氣", "後天氣象"]}
    resultDICT = execLoki(["今天天氣如何？", "後天氣象如何？"], filterLIST=filterLIST, refDICT=refDICT)                # output => {"key": ["今天天氣", "後天氣象"]}