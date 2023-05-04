#!/bin/bash

##export FLASK_APP=sesac
##export FLASK_DEBUG=true
##export FLASK_RUN_PORT=8999
##export FLASK_RUN_HOST=0.0.0.0

##source ~/.bashrc 배치 파일 변경 사항 후 저장
##source activate python3
##flask run
source lyrics/bin/activate
nohup python3 app.py &
tail -f nohup.out