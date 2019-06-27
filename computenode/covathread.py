import threading, multiprocessing
import time

class timeoutProcess(multiprocessing.Process):

    def __init__(self, func, arguments, timeout):
        super(timeoutProcess, self).__init__(target = func, args = arguments)
        self.timeout = timeout
        self.isFinished = True

    def checkTimeout(self):
        totalTime = 0

        while totalTime < self.timeout:
            if not self.is_alive():
                break
            time.sleep(1)
            totalTime += 1

        if self.is_alive():
            self.terminate()
            self.isFinished = False

    def startProcess(self):
        self.start()
        p = threading.Thread(target = self.checkTimeout)
        p.start()
        return p
