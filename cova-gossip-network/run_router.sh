echo $PPID > router_logs.txt
port=10000
for value in {1..3}
do
    python router.py $port &
    echo $! >> router_logs.txt
    ((port++))
done

