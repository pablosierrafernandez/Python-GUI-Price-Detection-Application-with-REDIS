# Python-GUI-Price-Detection-Application-with-REDIS
💹This Python GUI Price Detection Application detects prices of an asset with the help of XML-RPC, Numpy, Pandas, and Redis.

### Requirements

-   Python 3
-   tkinter
-   numpy
-   pandas
-   redis
-   xmlrpc.client
-   xmlrpc.server

### Installation

1.  Clone the repository
2.  Install the required packages

bashCopy code

`pip install tkinter numpy pandas redis xmlrpc.client xmlrpc.server` 

3.  Run the `xmlrpc_cluster.py` file

`python xmlrpc_cluster.py` 

4.  Run the `xmlrpc_server.py` file

`python xmlrpc_server.py` 

5.  Run the `app.py` file

`python app.py` 

### 🤔How to use

1.  Select the .csv file containing the asset's price data.
2.  Enter the price type to be detected (ask/bid).
3.  Add a worker (optional).
4.  Select the type of detection (minimum/maximum).
5.  Click on the Detect button.

### 🤪Code Example

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
    import os
    
    contin=True
    m_list=[]
    filename =None
    price=None
    
    #---in_csv: path of the file
    #---rowsize: number of lines per file or number of nodes
    def split_csv(in_csv, rowsize):
        # csv file name to be read in
        # get the number of lines of the csv file to be read
        print(filename)
        number_lines = sum(1 for row in (open(in_csv)))
        # size of rows of data to write to the csv,
        # you can change the row size according to your need
        rowsize = round(number_lines/rowsize)
        j = 0
        # start looping through data writing it to a new file for each set
        # i=1
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
    
    def RefreshTextERROR(error):
        labelerr['text'] = error
    
    def UploadAction(event=None):
        RefreshTextERROR("")
        global filename
        filename = askopenfilename(initialdir='.')
        # Cut path to the file off
        filename = filename.split('/')[len(filename.split('/'))-1]
        print('Selected:', filename)
        label1['text'] = filename
    
    def UploadAction2(min_max):
        global filename
        RefreshTextERROR("")
        if(price==None):
            RefreshTextERROR("Select Price type")
