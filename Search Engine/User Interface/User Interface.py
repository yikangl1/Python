import sys
from tkinter import *
import json
from pprint import pprint
import sqlite3
import os
from bs4 import BeautifulSoup
import re
from heapq import nlargest
import math
import webbrowser


conn = sqlite3.connect('inverted_Index_2.db')
c = conn.cursor()


def insert_token(token, frequency, docID):
    with conn:
        c.execute("INSERT INTO index_db VALUES (:token, :frequency, :docID)", {'token': token, 'frequency': frequency, 'docID': docID})
        

def get_emps_by_token(token):
    c.execute("SELECT * FROM index_db WHERE token = :token ", {'token': token})
    return c.fetchall()


def update_fequency_and_docID(token, frequency, docID):
    with conn:
        c.execute(""" UPDATE index_db SET frequency = :frequency, docID = :docID
                    WHERE token = :token """,
                  {'token': token, 'frequency': frequency, 'docID': docID})

def remove_token(token):
    with conn:
        c.execute("DELETE from index_db WHERE token = :token",
                  {'token': token})

def get_all():
    c.execute("SELECT * FROM index_db")
    return c.fetchall()


def callback(event):
    webbrowser.open_new(event.widget.cget("text"))

links = []

def mhello():
    global links
    if links != []:
        for item in links:
            item.destroy()
        links = []
 
    mtext = ment.get().lower()

    temp = ' '.join(mtext.split())
    temp = temp.split(' ')

    for item in temp:
        fre = get_emps_by_token(item)[0][1].split(',')
        doc = get_emps_by_token(item)[0][2].split(',')
        d_f = len(fre)

        new_fre = []
        for item in fre:
            new_fre.append(int(item) * math.log10(75000 / d_f))
        top_ten = nlargest(10, new_fre)

        d = []
        result = []
        for item in top_ten:
            i = new_fre.index(item)
            new_fre[i] = 0
            result.append((doc[i], item))

    result.sort(key = lambda x: x[1])
    new_result = sorted(result, key = lambda x: x[1], reverse = True)
    
    #for item in new_result[0:10]:
    #    print(item)

    
    with open('bookkeeping.json') as f:
        data = json.load(f)

    link = []
    for item in new_result:
        link.append(data[item[0]] )

    #for l in link:
    #    print(l)

    for item in link:
        #mlabel2 = Label(mGui, text = item  ).pack()
        link = Label(text = item, fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", callback)
        links.append(link)
        
    return

mGui = Tk()
ment = StringVar()
mGui.geometry('600x500+300+300')
mGui.title('My Search Engine')
mlabel = Label(mGui, text = 'User Interface').pack()
mbutton = Button(mGui, text = 'Search', command = mhello, fg = 'white', bg = 'blue').pack()
mEntry = Entry(mGui, textvariable = ment).pack()


