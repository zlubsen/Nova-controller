import time

class FrequencyTimer:
    def __init__(self, task_frequency_millisec=500):
        self.frequency_ms = task_frequency_millisec # default to 500 ms
        self.now = lambda: int(round(time.time() * 1000))
        self.last_time_ms = self.now()

    def frequencyElapsed(self):
        current_time_ms = self.now()
        time_diff_ms = current_time_ms - self.last_time_ms
        if time_diff_ms >= self.frequency_ms:
            self.__setLastTime()
            return True
        else:
            return False

    def __setLastTime(self):
        self.last_time_ms = self.now()
