import os
from datetime import datetime

LOG_MODE = {'INFO': 1, 'WARN': 2, 'ERROR': 3}


class Logger:
    def __init__(self, base_path, name, **kwargs):
        self.filename = os.path.join(base_path, 'LOG-%s-' % name + datetime.now().strftime("%d%m%Y-%H%M%S") + '.log')
        self.cache = []
        self.max_cache = kwargs.get('max_cache', 20)
        self.log_level = kwargs.get('log_level', 'INFO')

        # initialize
        if not os.path.exists(base_path):
            os.mkdir(base_path)
            self.add_log('Log folder created at: %s' % base_path)
        return

    def __len__(self):
        return len(self.cache)

    def __getitem__(self, idx):
        return self.cache[idx]

    def __str__(self):
        out = "\n".join(['Log file at: %s' % self.filename,
                         'Cached logs: %d' % len(self.cache),
                         'Max cache: %d' % self.max_cache,
                         'Log level: %s' % self.log_level])
        return out

    def add_log(self, msg, mode='INFO'):
        if mode not in LOG_MODE:
            raise ValueError("Unknown log mode: %s!" % mode)

        # assemble message
        prefix = datetime.now().strftime("[%Y/%m/%d %H:%M:%S") + " %s]: " % mode
        msg = prefix + msg
        self.cache.append(msg)

        # show message
        if LOG_MODE[mode] >= LOG_MODE[self.log_level]:
            print(msg)

        # save log
        if len(self.cache) >= self.max_cache:
            self.flush()
        return

    def flush(self):
        # format content
        content = '\n'.join(self.cache) + '\n'

        # write to file
        with open(self.filename, 'a') as f:
            f.write(content)

        # clear cache
        self.cache = []
        return
