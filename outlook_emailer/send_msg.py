# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 13:27:59 2019

@author: 0042-rudkovsky-ae
"""

import win32com.client as win
import pandas as pd


# ==== Global Consts ================
_outlook_box = r'vsp-equip@omega.sbrf.ru'
#_outlook_box = r'Оборудование ВСП'
_outlook_check_folder = r'заказать планшет'

# ==== Global Vars ================
outlook = win.Dispatch('Outlook.Application')
accounts = outlook.Session.Accounts

#account = accounts[0]

def send_email(to, subject, body, acc):
    msg = outlook.CreateItem(0)
    msg.To = to
    msg.Subject = subject
    msg.HTMLBody = body
    
    for account in accounts:
        if account.DisplayName == acc:
            msg._oleobj_.Invoke(*(64209,0,8,0,account))
            break
        
    msg.Send()


def check_emails():
    global outlook
    outlook = outlook.GetNamespace("MAPI")
    inbox = outlook.Folders(_outlook_box)
    senders = []
    folders = inbox.Folders
    for folder in folders:
        if folder.Name == _outlook_check_folder:
            messages = folder.Items
            
            for message in messages:
               senders.append(message.SentOnBehalfOfName)
            break
    return senders


if __name__ == '__main__':
    senders = check_emails()
    path = r'\\Braga101\Vol2\SUDR_PCP_BR\Оборудование_ТМЦ\01_Аналитика\1_Планшеты\ИСУ\Задача\Сдать планшет.xlsx'
    mails = pd.read_excel(path, 'список к сдаче')
    for i in range(0, len(mails)):
        email = mails['почта'][i]
        name = mails['name'][i]
        body = mails['Текст'][i]
        subject = 'Сдача планшета'
        if email:
            send_email(email, subject, body, _outlook_box)
            print(i, '-', email)
