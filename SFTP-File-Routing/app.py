import sftp
import pgp
import key
import os
import configparser
import time
import re
from sys import argv
import shutil
import traceback
import smtplib

#TODO #Read configuration file from sys.argv
config_file = 'app.config'
config = configparser.ConfigParser()
config.read(config_file)

def log_traceback(ex, ex_traceback=None, log_file='error.log'):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    with open(log_file,'a') as log:
        log.write('\n')
        log.write('ERROR: ' + time.asctime() + '\n')
        log.write(repr(e))
        log.write('\n'.join(tb_lines))

def send_error_email(subject,body):
    try:
        smtpObj = smtplib.SMTP(
            config['Global']['email_server'], 
            config['Global']['email_port']
            ) 
        smtpObj.ehlo()
        smtpObj.starttls()
        if config['Global']['email_auth']=='true':
            smtpObj.login(
                config['Global']['email_username'], 
                config['Global']['email_password']
                )
        smtpObj.sendmail(
            config['Global']['email_from'], 
            config['Global']['email_to'].split(','), 
            'Subject: {0}\nFrom:{1}\nTo:{2}\n\n{3}'.format(
                subject,
                config['Global']['email_from'], 
                config['Global']['email_to'],
                body
                )
                )
        smtpObj.quit()
    except Exception as e:
        log_traceback(ex=e,log_file=config['Global']['log_file'])

try:
        #Read configuration options
    sources = config['Source']['locations'].split(',')
    known_hosts = config['Global']['ssh_known_hosts']

    def copy_files(dest_dir,source_dir='.',file_mask='.*'):
        files = os.listdir(source_dir)
        for f in files:
            if (os.path.isfile(os.path.join(source_dir,f)) and re.search(file_mask,f) is not None):
                dest_file = os.path.join(dest_dir,f)
                if os.path.exists(dest_file):
                    dest_file = os.path.join(dest_dir,time.strftime('%Y%m%d%H%M%S')+f)
                shutil.copy(os.path.join(source_dir,f),dest_file)

    def move_files(dest_dir,source_dir='.',file_mask='.*'):
        files = os.listdir(source_dir)
        for f in files:
            if (os.path.isfile(os.path.join(source_dir,f)) and re.search(file_mask,f) is not None):
                dest_file = os.path.join(dest_dir,f)
                if os.path.exists(dest_file):
                    dest_file = os.path.join(dest_dir,time.strftime('%Y%m%d%H%M%S')+f)
                shutil.move(os.path.join(source_dir,f),dest_file)

    #download encrypted files to staging location
    for source in sources:
        source_server = config[source]['server']
        source_port = config[source]['port']
        source_file_mask = config[source]['file_mask']
        source_username = config[source]['username']
        source_password = key.RetrievePassword(config[source]['password_file'],os.environ[source])
        source_dir = config[source]['source_dir']
        staging_dir = config[source]['staging_dir']
        encryption_type = config[source]['encryption_type']
        destinations = config[source]['destinations'].split(',')
        sftp.download(
            server=source_server,
            username=source_username,
            password=source_password,
            port=int(source_port),
            file_mask=source_file_mask,
            staging_dir=staging_dir,
            source_dir=source_dir,
            known_hosts=known_hosts
            )
    #decrypt files
        if encryption_type == 'pgp':
            pgp.decrypt_files(
                dir=staging_dir,
                file_mask=source_file_mask,
                key=config[source]['encryption_key'],
                pgp_executable=config['Global']['pgp_executable']
            )

    #move sftp files to archive directory at source
        if config[source]['archive_source_files']:
            sftp.move(
                server=source_server,
                username=source_username,
                password=source_password,
                port=int(source_port),
                file_mask=source_file_mask,
                destination=config[source]['archive_dir'],
                source_dir=source_dir,
                known_hosts=known_hosts
            )
    #move staging files to destination directories and then archive to processed folder
        for destination in destinations:
            dest_type = config[destination]['type']
            if dest_type == 'smb':
                copy_files(
                    dest_dir=config[destination]['path'],
                    source_dir=staging_dir,
                    file_mask=config[destination]['file_mask']
                    )
            elif dest_type == 'sftp':
                sftp.upload(
                    server=config[destination]['server'],
                    username=config[destination]['username'],
                    password=key.RetrievePassword(config[destination]['password_file'],os.environ[destination]),
                    port=int(config[destination]['port']),
                    file_mask=config[destination]['file_mask'],
                    source_dir=staging_dir,
                    dest_dir=config[destination]['destination_dir'],
                    known_hosts=known_hosts
                    )
        move_files(dest_dir=config['Global']['processed_dir'],source_dir=staging_dir)
except Exception as e:
    log_traceback(ex=e,log_file=config['Global']['log_file'])
    message = '\n'.join(['The following error has occurred during SFTP Processing:',time.asctime(),repr(e),'\n\nThis should also create an active issue in N-Able.'])
    send_error_email(config['Global']['email_subject'],message)
finally:
    move_files(dest_dir=config['Global']['failed_dir'],source_dir=staging_dir)


    