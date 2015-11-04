#!/usr/bin/python3
import socket
import os, sys, time
import threading
import collections
import enum
import fcntl

"""
[note]
message format: ##HEAD##|<payload>|##END##
payload format: <command>:<data>, <data>, ...
server response spec (after receiving message from client):
    -1: error
   MSG: <message content>
one response per receiving

daemon(server) support receiving command and data spec:
PLAY:
PAUSE:
NEXT:
PREV:
CONFIG:<bg_dir>,<interval>. change background directory and interval
INFO:
    return payload: MSG:<status>,<bg_dir>,<current wallpaper>,<interval>
"""

sv_addr='/tmp/bgchd.sock'
END='##END##'
HEAD='##HEAD##'
MAX_INVALID_CNT=3
Payload=collections.namedtuple('payload_t',['CMD', 'DATA'])

class IpcCmd(enum.Enum):
    IPC_PLAY = 'PLAY'
    IPC_PAUSE = 'PAUSE'
    IPC_NEXT = 'NEXT'
    IPC_PREV = 'PREV'
    IPC_CONFIG = 'CONFIG'
    IPC_INFO = 'INFO'
    IPC_MSG = 'MSG'

# A socket server wrapper which is responsible for resource recycle
class SockSvObj:
    def __init__(self, addr):
        self.__sv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        fcntl.fcntl(self.__sv.fileno(), fcntl.F_SETFD, fcntl.FD_CLOEXEC)

        try:
            self.__sv.bind(addr)
        except Exception as err:
            self.__sv.close()
            raise err

        self.__sv_addr, self.__cl_addr = addr, ''
        self.__cl = None
        self.__released = False

    def listen_and_accept(self):
        sys.stdout.write('start listening...\n')
        self.__sv.listen(1)
        self.__cl, self.__cl_addr = \
            self.__sv.accept()
        sys.stdout.write('accept connection: {0}\n'.format(self.__cl_addr))
        sys.stdout.flush()

    def is_connect(self):
        return self.__cl is None

    def recv(self, buf_size):
        raw = self.__cl.recv(buf_size)
        return raw

    def send_ipcmsg_to_cl(self, payload):
        msg = get_ipcmsg_by_payload_obj(payload)
        sys.stdout.write('send to client: {0}\n'.format(msg))
        sys.stdout.flush()
        self.__cl.sendall(msg.encode('utf-8'))

    def force_release(self):
        self.__sv.close()
        os.remove(self.__sv_addr)
        sys.stdout.write('socket resource is released\n')
        sys.stdout.flush()
        self.__released = True

    def is_released(self):
        return self.__released

    def __del__(self):
        if not self.__released:
            self.force_release()

def start_server_thrd(ipc_handler):
    def listen_to_sock_and_respond():
        try:
            sock_sv = SockSvObj(sv_addr)
        except Exception as err:
            sys.stdout.write('previous connection is not closed. Err: {0}\n'.format(err))
            sys.stdout.flush()
            time.sleep(0.2)
            return

        sock_sv.listen_and_accept()
        msg, clip = '', ''
        started=False
        invalid_cnt=0
        while True:
            raw = sock_sv.recv(1024)
            if not raw:
                break
            else:
                clip = raw.decode('utf-8')
                if started == False and clip.startswith(HEAD):
                    started = True

                if started:
                    msg += clip
                else:
                    invalid_cnt += 1

                if clip.endswith(END):
                    sys.stdout.write('send {0} to ipc_handler\n'.format(msg))
                    sys.stdout.flush()
                    ipc_handler(sock_sv, msg)
                    break

                if invalid_cnt > MAX_INVALID_CNT:
                    sys.stderr.write('too much invalid message in ipc. closing...\n')
                    sys.stderr.flush()
                    conn.sendall('-1'.encode('utf-8'))
                    break

    def event_loop():
        while True:
            listen_to_sock_and_respond()

    sys.stdout.write('starting ipc server\n')
    sys.stdout.flush()
    if os.path.exists(sv_addr):
        os.remove(sv_addr)
    thrd = threading.Thread(target=event_loop, daemon=True)
    thrd.start()
    return thrd

def get_ipcmsg_by_payload_obj(payload):
    pay_str='{0}:{1}'.format(payload.CMD.value, payload.DATA)
    msg='{0}|{1}|{2}'.format(HEAD, pay_str, END)
    return msg

def send_ipcmsg_to_sv(payload):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    fcntl.fcntl(client.fileno(), fcntl.F_SETFD, fcntl.FD_CLOEXEC)
    client.connect(sv_addr)
    msg = get_ipcmsg_by_payload_obj(payload)
    # print('sending ' + msg)
    client.sendall(msg.encode('utf-8'))
    rsp = client.recv(1024)
    client.close()
    return rsp.decode('utf-8')

def get_payload_obj_from_ipcmsg(msg):
    p = msg.split('|')[1]
    if ':' in p:
        lst = p.split(':')
        if len(lst) == 2:
            return Payload(CMD=IpcCmd(lst[0]), DATA=lst[1])
    raise ValueError('incorrect payload format')
