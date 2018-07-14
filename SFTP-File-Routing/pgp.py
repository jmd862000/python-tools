import io
import shutil
import os
import re
import gnupg

def decrypt_files(key, dir='.',file_mask='^.*pgp$',pgp_executable='gpg'):
    gpg = gnupg.GPG(pgp_executable)
    files = os.listdir(dir)
    for file in files:
        if os.path.isfile(os.path.join(dir,file)) and re.search(file_mask,file) is not None:
            with open(os.path.join(dir,file),'rb') as f:
                output_file = file.rstrip('.pgp')
                gpg.decrypt_file(file=f,passphrase=key,output=os.path.join(dir,output_file))
