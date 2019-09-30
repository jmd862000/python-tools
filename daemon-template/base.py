# Running tasks
import os
import time
import sys
from signal import SIGTERM

class Service(object):
    def __init__(self):
        self.variable = "Line"
    
    def write_file(self):
        i = 1
        while True:
            with open("/tmp/file.txt", 'a') as output:
                output.write("{}{}\n".format(self.variable,i))
                i += 1
                time.sleep(1)


def launch_daemon():
    import sys, os
    try:
        pid = os.fork()
        if pid > 0:
            # Exit first parent
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (
            e.errno, e.strerror)
        sys.exit(1)
    os.chdir("/")
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork(  )
        if pid > 0:
            # Exit from second parent; print eventual PID before exiting
            print "Daemon PID %d" % pid
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (
            e.errno, e.strerror)
        sys.exit(1)
    pid = str(os.getpid())
    file("/var/run/lock/base.pid",'w+').write("%s\n" % pid)
    main()


def start_stop(action, pidfile="/var/run/lock/base.pid"):
    try:
        pf = file(pidfile, 'r')
        pid = int(pf.read().strip())
        pf.close()
    except IOError:
        pid = None
    if 'stop' == action or 'restart' == action:
        if not pid:
            sys.stderr.write("Could not find %s." % pidfile)
            sys.exit(1)
        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                os.remove(pidfile)
                if 'stop' == action:
                    sys.exit(0)
                action = 'start'
                pid = None
            else:
                print str(err)
                sys.exit(1)
    if 'start' == action:
        if pid:
            msg = "Start aborted: File '%s' exists.\n"
            sys.stderr.write(msg % pidfile)
            sys.exit(1)
        launch_daemon()
        return

def main():
    service = Service()
    service.write_file()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        start_stop(action)
