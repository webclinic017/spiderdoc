from fsplit.filesplit import Filesplit as fs
import os


file_path = 'C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\\Preprod\\symbols.txt'
Sym_file = open(file_path,"r")
x = len(Sym_file.readlines())
Sym_file.close()

Sym_file = open(file_path,"r")
li= []
for i in range(x):
    li.append(Sym_file.readline().strip('\n'))

Sym_file.close()
line = 0
sym_count = int(x/63)
for i in range(sym_count):
    file_path = 'C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\\Preprod\\lunchers\\sym_files\\symbols_'+str(i)+'.txt'
    Sym_file = open(file_path,"a")
    for k in range(63):
        Sym_file.write(li[line]+'\n')
        line += 1
        

os.system('python "C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\\Preprod\\on_db_updt.py" 1')
