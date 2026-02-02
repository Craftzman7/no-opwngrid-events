import pwnagotchi.plugins as plugins
import pwnagotchi
import requests
import threading

class NoOpwngridEvents(plugins.Plugin):
    __author__ = "Eve"
    __version__ = "1.0.0"
    __license__ = "None"
    __description__ = "A plugin that replaced opwngrid events in case it goes down."

    def __init__(self):
        self.should_stop = False
        self.check_thread = threading.Thread(target=self.check_loop)

    def check_internet_connectivity(self):
        try:
            # check DNS
            host = 'http://captive.apple.com/hotspot-detect.html'
            headers = {'user-agent': f'pwnagotchi/{pwnagotchi.__version__}'}
            r = requests.get(host, headers=headers, timeout=(30.0, 60.0))
            if r.status_code == 200:
                return True
        except:
            pass
        return False
    
    def check_loop(self):
        while not self.should_stop:
            if self.check_internet_connectivity():
                plugins.on('internet_available', self.agent)
    
    def on_epoch(self, agent, epoch, epoch_data):
        if not self.check_internet_connectivity():
            return
        plugins.on('internet_available', agent)
    
    def on_ready(self, agent):
        self.agent = agent
        if agent.mode == "manual":
            # Run check thread, we don't have epochs in manual mode
            self.check_thread.start()

    def on_unload(self, agent):
        self.should_stop = True
        if self.check_thread.is_alive():
            self.check_thread.join()