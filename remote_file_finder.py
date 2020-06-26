#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 10:48:28 2017

@author: mohlb
access the neuroimaging files on the remote SSH server
"""
import paramiko
import os
import glob
import pwd

kh = '~/.ssh/known_hosts'
key = '~/.ssh/id_rsa'
port = 22
uname = pwd.getpwuid(os.getuid()).pw_name #generic call to be flexible with multiple users
                        
def get_remote_files(ip, filepath):
    host = ip
    searchCmd = r'glob.glob ' + filepath
    
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys(os.path.expanduser(kh))
        client.connect(hostname=host,port=port,username=uname, key_filename=os.path.expanduser(key))
        stdin, stdout, stderr = client.exec_command(searchCmd)
        return (stdout.read())
    finally:
        client.close()

    return stdout.read()