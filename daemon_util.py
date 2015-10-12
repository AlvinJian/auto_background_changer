#!/usr/bin/python3
import os
import sys
import atexit
import fcntl

def daemonize(pidfile, func, infolog=os.devnull, errlog='/tmp/auto-bgchd-err.log', singl=True):
    def __cleanup__():
        os.remove(pidfile)
    
    # don't use open(filename, 'w') here since it will erase the existing pidfile
    pidfd = os.open(pidfile, os.O_RDWR | os.O_CREAT)
    if singl:
        try:
            fcntl.lockf(pidfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except Exception as err:
            raise Exception('{0}\ncannot lock pidfile:{1}. an instance is already running'.format(err, pidfile));
        finally:
            os.close(pidfd)

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
    os.close(sys.stdin.fileno())
    sys.stdout = open(infolog, 'w')
    sys.stderr = open(errlog, 'w')

    atexit.register(__cleanup__)
    pid_str = str(os.getpid())
    with open(pidfile,'w') as fobj:
        fobj.write(pid_str + '\n')
        fobj.flush()
        fcntl.lockf(fobj, fcntl.LOCK_EX | fcntl.LOCK_NB)
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
