import time

def main():

    time.sleep(50)

    fp = open('Code/output.txt', 'w+')

    fp.write('Successfully executed file')

    fp.close()