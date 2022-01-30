General Overview :
    this project currently contains 3 dirctories :

        1) automation 
            this directory contains all ansibles and scripts for setting up the infrastructure
            i.e:
                installing docker and all its dependencies automatically - install_nase_BT.yml .
                downloading the repo - getcode
                running the elk stack - docker-compose.yml
        2) BT 
            this directory contains all of the files regarding the BackTest ( running a strategy on historical data )
            i.e:
                BT/containers/SMA - the only completed file redy to run
                under BT/containers/SMA/strategy/luanchers you will find 3 scripts :
                    1) clear_lsat_run.yml - delets all log files from previos run
                    2)dispatch.py get from the user all neccesery input to run - this script invokes other scripts on remote servers
                    3) backtest.py a script which is accesible to all servers and invokes docker build and docker run commands on the current server to run the backtest simulation container.

                    the container outputs csv logs which are collected through a file beat container which sends them to logstash 
                    for processing.

                    NOTE :  the reason i am able to invoke the script on a remote server is becuase the repository sits on the 
                            masater node and its path is mounted on remote servers via NFS .

        3) Preprod 
            this directory contains is the dev enviormnt in preparation for live trading .
            i.e
                Preprod/streamdata - contains all the requeird depedencies for the stream:1.0.0 container
                    this container logs into a live stram of all the minutebars that are being streamed from polygon.io
                    it then write the Open,high,low,close,timestamp and, stock symbol informtion into a postgres DB
                
                playground/on_db_updt - unfineshed as the 'ta-lib' dependency is refusing to install - need to install miniconda first then use conda-forge.
                this container waits for new input on a minute basis to the init_ohlc table then it queries that informations ,processes it, then write this info + additional info it generated to final_ohlc

                
