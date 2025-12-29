import threading

class TimeoutException(Exception):
    pass

class Timeout:
    def __init__(self, seconds):
        self.seconds = seconds
        self.timer = None

    def timeout_handler(self):
        raise TimeoutException

    def start(self):
        self.timer = threading.Timer(self.seconds, self.timeout_handler)
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()

# timeout = Timeout(5)
# timeout.start()
# import time
# time.sleep(6)
# timeout.cancel()

# from .custom_py.time_out import Timeout, TimeoutException
# try:
#     timeout = Timeout(5)
#     global_html_home = pokemon_display(f, True).replace("`", "'") # wholeCollection
#     timeout.cancel()
# except TimeoutException:
#     return