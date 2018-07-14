import pysftp
import os
from time import sleep
import re

def download(server,username,password,port=22,file_mask='*',staging_dir='.',source_dir='.',known_hosts=None):
    if known_hosts:
        cnopts = pysftp.CnOpts(knownhosts=known_hosts)
        cnopts.hostkeys = None
    cinfo = {
        'host':server,
        'username':username,
        'password':password,
        'port':port
    }
    with pysftp.Connection(**cinfo,cnopts=cnopts) as sftp:
        sftp.chdir(source_dir)
        files = sftp.listdir()
        for d in [download for download in files if re.search(file_mask,download) is not None]:
            if (sftp.isfile(d)):
                sftp.get(d,os.path.join(staging_dir,d))

def move(server,username,password,destination,port=22,file_mask='*',source_dir='.',known_hosts=None):
    if known_hosts:
        cnopts = pysftp.CnOpts(knownhosts=known_hosts)
        cnopts.hostkeys = None
    cinfo = {
        'host':server,
        'username':username,
        'password':password,
        'port':port
    }
    with pysftp.Connection(**cinfo,cnopts=cnopts) as sftp:
        sftp.chdir(source_dir)
        files = sftp.listdir()
        for m in [move for move in files if re.search(file_mask,move) is not None]:
            if (sftp.isfile(m)):
                sftp.rename(sftp.pwd + '/' + m,destination + '/' + m)

def upload(server,username,password,port=22,file_mask='*',source_dir='.',dest_dir='.',known_hosts=None):
    if known_hosts:
        cnopts = pysftp.CnOpts(knownhosts=known_hosts)
        cnopts.hostkeys = None
    cinfo = {
        'host':server,
        'username':username,
        'password':password,
        'port':port
    }
    with pysftp.Connection(**cinfo,cnopts=cnopts) as sftp:
        os.chdir(source_dir)
        files = os.listdir()
        sftp.chdir(dest_dir)
        for u in [upload for upload in files if re.search(file_mask,upload) is not None]:
            if os.path.isfile(u):
                sftp.put(os.path.join(source_dir,u))
            

