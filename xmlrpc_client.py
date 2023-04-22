import xmlrpc.client
import config
import time
from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
import subprocess
from threading import Thread
import numpy as np
import redis
import pandas as pd
redis_cli = redis.Redis(host="localhost", port=int(config.REDISPORT), decode_responses=True, encoding="utf-8")
proxy_cluster = xmlrpc.client.ServerProxy('http://localhost:'+str(config.CLUSTER))

# esto lo metemos en un for y vamos tratando uno a uno + tratamiento de errores
# proxy_server1 = xmlrpc.client.ServerProxy('http://localhost:9001')
# proxy_server2 = xmlrpc.client.ServerProxy('http://localhost:9002')
import os
contin=True
m_list=[]
filename =None
price=None
#---in_csv: path del archivo
#---rowsize: numero de linias por archivo ó numero de nodos
def UploadAction(event=None):
    RefreshTextERROR("")
    global filename
    filename = askopenfilename(initialdir='.')
    # Cut path to the file off
    filename = filename.split('/')[len(filename.split('/'))-1]
    print('Selected:', filename)
    label1['text'] = filename

def RefreshTextERROR(error):
      labelerr['text'] = error

def UploadAction2(min_max):
   global filename
   RefreshTextERROR("")
   if(price==None):
      RefreshTextERROR("Select Price type")
   elif(filename==None):
      RefreshTextERROR("Select a .csv file")
   elif(int(label4['text'])==0):
      RefreshTextERROR("Please, add a Worker")
   else:
      split_csv(filename, int(label4['text']))
      i=0
      totaltime=0
      time_worker=0
      start_time = time.time()
      if min_max == "min":
            for key in redis_cli.scan_iter("worker:*"):
                  minn,time_worker=xmlrpc.client.ServerProxy(redis_cli.get(key)).get_min('input'+str(i), price)
                  print(time_worker)
                  totaltime=totaltime+float(time_worker)
                  m_list.append(minn)
                  i=i+1
            x = np.array(m_list)
            y = x.astype(np.float64)
            max_value=min(y)
            label2['text'] = max_value
      elif min_max == "max":
            for key in redis_cli.scan_iter("worker:*"):
                  maxx,time_worker=xmlrpc.client.ServerProxy(redis_cli.get(key)).get_min('input'+str(i), price)
                  print(time_worker)
                  totaltime=totaltime+float(time_worker)
                  m_list.append(maxx)
                  i=i+1
            x = np.array(m_list)
            y = x.astype(np.float64)
            max_value=max(y)
            label2['text'] = max_value
######elif --> more options"      
      else:     
            label2['text'] = "ERROR: Please, select min or max price"
      print("Total Time : "+str(time.time() - start_time)+" seconds in "+str(label4['text'])+" worker/s")
      print("Time without connexions: "+str(totaltime)+" seconds in "+str(label4['text'])+" worker/s")

def UploadAction3(price_input):
      RefreshTextERROR("")
      global price
      price=price_input
      
      # Cut path to the file off
def UploadAction4(event=None):
     subprocess.call('start python xmlrpc_server.py', shell=True)
     #label4['text'] = str(int(label4['text'])+1)
     time.sleep(5)

def split_csv(in_csv, rowsize):
      #csv file name to be read in 
      #get the number of lines of the csv file to be read
      print(filename)
      number_lines = sum(1 for row in (open(in_csv)))
      #size of rows of data to write to the csv, 
      #you can change the row size according to your need
      rowsize = round(number_lines/rowsize)
      j = 0
      #start looping through data writing it to a new file for each set
      #i=1
      headers=['Local time','Ask','Bid','AskVolume','BidVolume']

      for i in range(0,number_lines,rowsize):
            df = pd.read_csv(in_csv,
                        sep=',',
                         nrows = rowsize,#number of rows to read at each loop
                        skiprows = i)#skip rows that have been read
            df.columns = headers
            out_csv = 'input' + str(j) + '.csv'
            
            df.to_csv(out_csv,
          index=False,
          header=True,
          mode='a',#append data to csv file
          chunksize=rowsize)
            df=pd.read_csv(out_csv)
            
      
            redis_cli.set('input'+str(j),df.to_json())
            j=j+1
            os.remove(out_csv)
          #size of data to append for each loop
        
def comproveWorkers():
      global contin
      while contin:
         count=0
         for key in redis_cli.scan_iter("worker:*"):
           count=count+1
         label4['text'] = str(count)
         time.sleep(0.5)      


subprocess.call('start python xmlrpc_cluster.py', shell=True)

root= tk.Tk(className='Tick prices')
root.iconbitmap('72-722821_quantitative-traders-icon-analytics-icon-png-transparent-png.ico')
root.geometry("500x500") 
labelerr = tk.Label(fg='red') 
labelerr.pack(padx=5, pady=5)
button1 = tk.Button(text='Select File', command=UploadAction, bg='blue', fg='white')
button1.pack(padx=2, pady=5)
label1 = tk.Label(text='Please choose a file')
label1.pack(padx=2, pady=2)
label2 = tk.Label()

button7 = tk.Button(text='Add worker', command=UploadAction4, bg='blue', fg='white')
button7.pack(padx=2, pady=5)
label4 = tk.Label()
label4.pack(padx=2, pady=2)

n_workers=Thread(target=comproveWorkers)
n_workers.start()

label6 = tk.Label(text='----------------Select price type-----------------')
label6.pack(padx=2, pady=2)
button3 = tk.Button(text='Ask', command=lambda:UploadAction3('Ask'), bg='brown', fg='white')
button3.pack(padx=2, pady=5)
button4 = tk.Button(text='Bid', command=lambda:UploadAction3('Bid'), bg='brown', fg='white')
button4.pack(padx=2, pady=5)
button5 = tk.Button(text='AskVolume', command=lambda:UploadAction3('AskVolume'), bg='brown', fg='white')
button5.pack(padx=2, pady=5)
button6 = tk.Button(text='BidVolume', command=lambda:UploadAction3('BidVolume'), bg='brown', fg='white')
button6.pack(padx=2, pady=5)

label3 = tk.Label(text='---------------------------------------------------------')
label3.pack(padx=2, pady=2)
button2 = tk.Button(text='Compute Low price', command=lambda:UploadAction2("min"), bg='red', fg='white')
button2.pack(padx=2, pady=5)
button8 = tk.Button(text='Compute High price', command=lambda:UploadAction2("max"), bg='green', fg='white')
button8.pack(padx=2, pady=5)
label2.pack(padx=2, pady=2)



root.mainloop()
contin=False
n_workers.join()
for key in redis_cli.scan_iter("worker:*"):
    redis_cli.delete(key)
for key in redis_cli.scan_iter("input*"):
    redis_cli.delete(key)
redis_cli.connection_pool.disconnect()
