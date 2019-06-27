echo $PPID > data_user_logs.txt
port=12000
for value in {1..1}
do
    python data_user.py $port &
    echo $! >> data_user_logs.txt
    ((port++))
done

