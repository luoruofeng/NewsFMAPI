#coding=UTF-8

import os
import errno

def write():    
    FIFO = "mypipe2"

    try:
        os.mkfifo(FIFO)
    except OSError as e:
        if (e.errno != errno.EEXIST):
            raise

    with open("temp.txt","r")as rf:
        with open(FIFO,"w") as f:
            f.write(rf.read())


if __name__ == "__main__":
    for i in range(80):
        write()
