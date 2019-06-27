port=$((11000+$1))
python computer.py $port &
echo $! >> computer_logs.txt