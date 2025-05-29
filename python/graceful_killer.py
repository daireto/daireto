"""GracefulKiller class for process SIGTERM, SIGHUP and SIGINT signals gracefully."""

import signal


class GracefulKiller:
    kill_now = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GracefulKiller, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, sig, frame):
        self.kill_now = True
