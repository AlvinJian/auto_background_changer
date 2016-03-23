#!/usr/bin/python3
import os
import sys
import atexit
import fcntl
import stat
import signal, time

pidfile='/tmp/bgchd.pid'

def daemonize(func, infolog=os.devnull, errlog='/tmp/bgchd-err.log', replace=True):
    def __cleanup__():
        os.remove(pidfile)

    while True:
        try:
            pidfd = os.open(pidfile, os.O_RDWR | os.O_CREAT)
            fcntl.lockf(pidfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except Exception as err:
            if replace:
                pidnum = get_prev_pid()
                os.kill(pidnum, signal.SIGKILL)
                time.sleep(1)
            else:
                raise Exception('Unable lock pidfile:{0}. An instance is already running'.format(pidfile));
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

    # lock pidfile as quick as possible
    fobj = open(pidfile,'w')
    fcntl.lockf(fobj, fcntl.LOCK_EX | fcntl.LOCK_NB)
    pid_str = str(os.getpid())
    fobj.write(pid_str + '\n')
    fobj.flush()
    # pidfile shall not be modified by other/group but the owner
    os.chmod(pidfile,  stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IROTH)

    sys.stdout.flush()
    sys.stderr.flush()
    os.close(sys.stdin.fileno())
    sys.stdout = open(infolog, 'w')
    sys.stderr = open(errlog, 'w')
    atexit.register(__cleanup__)

    sys.stdout.write('enter main routine...\n')
    sys.stdout.flush()
    func()

def get_prev_pid():
    pidnum = None
    if os.path.exists(pidfile):
        with open(pidfile, 'r') as pidf:
            for line in pidf:
                line=line.strip()
                if line.isdigit():
                    pidnum = int(line)
                    break
    return pidnum

def is_daemon_start(pidfile):
    pidnum = get_prev_pid();
    if pidnum == None:
        return False

    if os.path.exists('/proc/{0}'.format(pidnum)):
        statusp = '/proc/{0}/status'.format(pidnum)
        with open(statusp, 'r') as statusf:
            for line in statusf:
                if 'Name:' in line and 'bgchd' in line:
                    return True
                elif 'Name:' in line and 'bgchd' not in line:
                    return False
    else:
        return False
