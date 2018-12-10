import sqlite3
import os
from bs4 import BeautifulSoup
import re

# connect to database
conn = sqlite3.connect('inverted_Index.db')
c = conn.cursor()

# create table
try:
    c.execute("""create table index_db (
           token text,
           frequency text,
           docID text
    )""")
except:
    print('table already exist')


# SQLite functions
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


# implementing inverted index

rootdir = 'C:/Users/yk_l/Desktop/WEBPAGES'
inverted_index = {}

i = 0
for subdir_1, dirs_1, files_1 in os.walk(rootdir):
    for subdir_2, dirs_2, files_2 in os.walk(subdir_1):
        for file in files_2:
            #i += 1
            if 'index' not in file and 'book' not in file and 'test' not in file and 'inverted' not in file:
                current_file = os.path.join(subdir_2, file)
                #print(current_file)
                file = open(current_file, encoding= "utf8")
                temp_DocID = current_file[31:].split("\\")
                doc_id = str(temp_DocID[0]) + '/' + str(temp_DocID[1])
                html = file.read()
                soup = BeautifulSoup(html, "lxml")
                data = soup.get_text()
                for word in re.findall(r"[a-zA-Z0-9]+", data):
                    word = word.lower()
                    if inverted_index.get(word, 0) == 0:
                        inverted_index[word] = {}
                        inverted_index[word][doc_id] = 1
                    else:
                        if doc_id in inverted_index[word].keys():
                            inverted_index[word][doc_id] += 1
                        else:
                            inverted_index[word][doc_id] = 1
        
    
#print(inverted_index)          
#print(i)
            

        
# store the inverted index into database

for token in inverted_index:
    new_docID = ''
    new_frequency = ''
    for item in inverted_index[token]:
        new_docID += str(item) + ','
        new_frequency += str(inverted_index[token][item]) + ','
    new_docID = new_docID[:-1]
    new_frequency = new_frequency[:-1]
    insert_token(token, new_frequency, new_docID)
                   

                    
            
#print(get_all())
#print(get_emps_by_token('the'))
                
