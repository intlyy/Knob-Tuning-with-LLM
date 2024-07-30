timestamp=$(date +%s)
nohup python ./main.py > ./history_results/$timestamp &
