#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for line

    Input:
        inputSTR      str,
        utterance     str,
        args          str[],
        resultDICT    dict,
        refDICT       dict,
        pattern       str

    Output:
        resultDICT    dict
"""

from random import sample
import json
import os

DEBUG = True
CHATBOT_MODE = True

userDefinedDICT = {}
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except Exception as e:
    print("[ERROR] userDefinedDICT => {}".format(str(e)))

responseDICT = {}
if CHATBOT_MODE:
    try:
        responseDICT = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.join("reply", "reply_line.json")), encoding="utf-8"))
    except Exception as e:
        print("[ERROR] responseDICT => {}".format(str(e)))

# 將符合句型的參數列表印出。這是 debug 或是開發用的。
def debugInfo(inputSTR, utterance):
    if DEBUG:
        print("[line] {} ===> {}".format(inputSTR, utterance))

def getResponse(utterance, args):
    resultSTR = ""
    if utterance in responseDICT:
        if len(responseDICT[utterance]):
            resultSTR = sample(responseDICT[utterance], 1)[0].format(*args)

    return resultSTR

def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern=""):
    debugInfo(inputSTR, utterance)
    for i in range(len(args)):
        args[i] = args[i].lower().strip(' ')   # 前處理，把argument變小寫並去頭尾空格
    
    if utterance == "[LINE]個人化通知服務提供哪些通知":
        if CHATBOT_MODE:
            if args[0] == 'line':
                resultDICT["response"] = getResponse(utterance, args)
        else:
            pass

    if utterance == "[可以]設定幾[個][LINE][帳號]":
        if CHATBOT_MODE:
            if args[2] == 'line' and args[3] in ['帳號', '帳戶']:
                resultDICT["response"] = getResponse(utterance, args)
        else:
            pass

    if utterance == "如何取消[LINE]個人化通知":
        if CHATBOT_MODE:
            if args[0] == 'line':
                resultDICT["response"] = getResponse(utterance, args)
        else:
            pass

    if utterance == "如何於[LINE]查看通知":
        if CHATBOT_MODE:
            if args[0] == 'line':
                resultDICT["response"] = getResponse(utterance, args)
        else:
            pass

    if utterance == "如何更改通知[訊息項目]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            pass

    if utterance == "如何設定[LINE]個人化通知":
        if CHATBOT_MODE:
            if args[0] == 'line':
                resultDICT["response"] = getResponse(utterance, args)
        else:
            pass
    if utterance == "[Line][可以]設定幾[個][帳號]":
        if CHATBOT_MODE:
            if args[0] == 'line' and args[3] in ['帳號', '帳戶']:
                resultDICT["response"] = getResponse(utterance, args)
        else:
            pass

    if utterance == "[LINE][帳號][可以]設定幾[個]？":
        if CHATBOT_MODE:
            if args[0] == 'line' and args[1] in ['帳號', '帳戶']:
                resultDICT["response"] = getResponse(utterance, args)
        else:
            pass

    return resultDICT