#!/usr/bin/python3
import socket
import os, sys
import threading
import collections

sockfile='/tmp/auto-bgchd.sock'
END='##END##'
HEAD='##HEAD##'
IPC_TIMEOUT_CNT=3

def start_server_thrd(ipc_handler):
    def listen_to_sock_and_respond():
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sockfile)
        sys.stdout.write('start listening...\n')
        sys.stdout.flush()
        server.listen(1)
        conn, addr = server.accept()
        sys.stdout.write('accept connection of {0}\n'.format(addr))
        sys.stdout.flush()
        msg, clip = '', ''
        started=False
        timeout_cnt=0
        while True:
            raw = conn.recv(1024)
            if not raw:
                break
            else:
                clip = raw.decode('utf-8')
                if started == False and clip.startswith(HEAD):
                    started = True

                if started:
                    msg += clip
                else:
                    timeout_cnt += 1

                if clip.endswith(END):
                    sys.stdout.write('send {0} to ipc_handler\n'.format(msg))
                    sys.stdout.flush()
                    res = ipc_handler(msg)
                    conn.sendall(res.encode('utf-8'))
                    break

                if timeout_cnt > IPC_TIMEOUT_CNT:
                    break

        server.close()
        os.remove(sockfile)

    def event_loop():
        while True:
            listen_to_sock_and_respond()

    sys.stdout.write('starting ipc server\n')
    sys.stdout.flush()
    if os.path.exists(sockfile):
        os.remove(sockfile)
    thrd = threading.Thread(target=event_loop, daemon=True)
    thrd.start()
    return thrd

def send_ipc_msg(payload):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(sockfile)
    msg='{0}|{1}|{2}'.format(HEAD, payload, END)
    print('sending ' + msg)
    client.sendall(msg.encode('utf-8'))
    rsp = client.recv(1024)
    client.close()
    return rsp.decode('utf-8')
