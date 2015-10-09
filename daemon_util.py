#!/usr/bin/python3
import os
import sys
import atexit

def daemonize(pidfile, func, infolog=os.devnull, errlog='/tmp/auto-bgchd-err.log'):
    def __cleanup__():
        os.remove(pidfile)
        os.remove(sock)

    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError as err:
        sys.stderr.write('fork failed...err: {0}'.format(err))
        sys.exit(1)

    os.setsid()
    os.umask(0)
    sys.stdout.flush()
    sys.stderr.flush()
    #os.close(sys.stdin.fileno())
    #os.close(sys.stdout.fileno())
    sys.stdout = open(infolog, 'w')
    sys.stderr = open(errlog, 'w')

    atexit.register(__cleanup__)
    pid_str = str(os.getpid())
    with open(pidfile,'w') as f:
    	f.write(pid_str + '\n')
    sys.stdout.write('enter main routine...\n')
    sys.stdout.flush()
    func()

def is_daemon_start(pidfile):
    pidnum = None
    if os.path.exists(pidfile):
        with open(pidfile, 'r') as pidf:
            for line in pidf:
                line=line.strip()
                if line.isdigit():
                    pidnum = int(line)
                    break

    if pidnum == None:
        return False

    if os.path.exists('/proc/{0}'.format(pidnum)):
        statusp = '/proc/{0}/status'.format(pidnum)
        with open(statusp, 'r') as statusf:
            for line in statusf:
                if 'Name:' in line and 'auto-bgchd' in line:
                    return True
                elif 'Name:' in line and 'auto-bgchd' not in line:
                    return False
    else:
        return False
