# BankServiceBot 銀行客服機器人

## 專案簡介

此為參考玉山銀行 Q&A 專區，以卓騰 LOKI 語意理解引擎建置的銀行客服機器人專案，透過自然語言互動方式，回答銀行業務相關問題。

※ 本專案語意搜尋功能開發中，目前僅可處理基礎問答。

## 使用說明

1. 至 Line 主畫面右上角點選「加入好友」圖示
2. 搜尋 ID: @696ufyri 將機器人加入好友
3. 跟他說 Hi，即可開始聊天！

## 環境 & 使用技術

+ Python 3.11
+ Flask + Docker (Deployed on Heroku)
+ 卓騰語言科技 Loki 語意理解引擎 / Copytoaster 文件搜尋 (請參考[官方文件](https://api.droidtown.co/document/#Loki))
+ OpenAI API

## 檔案內容

```
│  .gitignore
│  app.py
│  chatbot.json
│  chatbotMaker.py
│  esun_qa.py
│  README.md
│  __init__.py
│  
├─intent
│      Loki_app.py
│      Loki_bsm.py
│      Loki_cardless.py
│      Loki_china_pay.py
│      Loki_corporate.py
│      Loki_credit_card.py
│      Loki_crossboarding.py
│      Loki_customer_service.py
│      Loki_deposit.py
│      Loki_digital_account.py
│      Loki_face_atm.py
│      Loki_foreign.py
│      Loki_insurance.py
│      Loki_line.py
│      Loki_loan.py
│      Loki_paypal.py
│      Loki_small_corp.py
│      Loki_trust_fund.py
│      Loki_wealth.py
│      Loki_web_atm.py
│      Loki_web_bank.py
│      Updater.py
│      USER_DEFINED.json
│      __init__.py
│
├─Loki_backup
│      app.ref
│      bsm.ref
│      cardless.ref
│      china_pay.ref
│      corporate.ref
│      credit_card.ref
│      crossboarding.ref
│      customer_service.ref
│      deposit.ref
│      digital_account.ref
│      face_atm.ref
│      foreign.ref
│      insurance.ref
│      line.ref
│      loan.ref
│      paypal.ref
│      small_corp.ref
│      trust_fund.ref
│      wealth.ref
│      web_atm.ref
│      web_bank.ref
│
├─reply
│      reply_app.json
│      reply_bsm.json
│      reply_cardless.json
│      reply_china_pay.json
│      reply_corporate.json
│      reply_credit_card.json
│      reply_crossboarding.json
│      reply_customer_service.json
│      reply_deposit.json
│      reply_digital_account.json
│      reply_face_atm.json
│      reply_foreign.json
│      reply_insurance.json
│      reply_line.json
│      reply_loan.json
│      reply_paypal.json
│      reply_small_corp.json
│      reply_trust_fund.json
│      reply_wealth.json
│      reply_web_atm.json
│      reply_web_bank.json
```

## 關於作者

+ [GitHub](https://github.com/HS6103)
+ [Medium](https://medium.com/@simonhsiao.hs)
+ <simonhsiao.hs@gmail.com>

## 參考資料

[玉山銀行 Q&A](https://www.esunbank.com/zh-tw/about/faq)
