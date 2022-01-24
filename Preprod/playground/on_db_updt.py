import psycopg2
from datetime import datetime as dt
import time
import multiprocessing

def get_from_db(symbol):
    
    closes = []
    last_update = 0

    symbol=symbol.strip('\n')

    
    con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
    cur = con.cursor()
    while True:
        cur.execute("SELECT timestamp FROM dbo.init_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 1")

        rows = cur.fetchall()

        for r in rows:
            ts = r[0]
            time_obj = dt.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
            dt.strftime(time_obj, '%y-%m-%d %H:%M:%S%z')
            now = dt.now().minute
            
            if time_obj != last_update:
                cur.execute("SELECT close FROM dbo.init_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 15")
                rows = cur.fetchall()
                for r in rows:
                    close = r[0]
                    closes.append(close)
                print(f"closes for {symbol}")
                print(closes)
                last_update = time_obj
                
                closes = []
                    
            else:
                print(f'not recent for {symbol}')
                time.sleep(10)
        
#file_path = '/input/'+symbols_file
file_path = 'C:\\Users\\nolys\\Desktop\\results\\symbols.txt'
Sym_file = open(file_path,"r")


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=3) as pool:
        pool.map_async(get_from_db,iterable=Sym_file).get() 