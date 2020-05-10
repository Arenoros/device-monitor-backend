from subprocess import Popen, PIPE, DEVNULL

class Shell:
    def run(self, cmd, env):
        out_fd = self.out_fd
        err_fb = self.err_fb
        if self.logger and hasattr(self.logger, 'out') and hasattr(self.logger, 'err'):
            out_fd = self.logger.out
            err_fb = self.logger.err
        p = None
        if out_fd or err_fb:
            p = Popen(cmd, shell=True, stdout=out_fd, stderr=err_fb, env=env, universal_newlines=True)
        else:
            p = Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr, env=env, universal_newlines=True)
        return p.wait()

    def run3(self, cmd, env):
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, env=env, universal_newlines=True)
        out, err = p.communicate()
        return (out, err,  p.returncode)

    def simple(cmd):
        p = Popen(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL, universal_newlines=True)
        return p.wait()

    def __init__(self, logger = None, out:int = None, err:int = None):
        self.logger = logger
        self.out_fd = out
        self.err_fb = err
