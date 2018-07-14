# Prerequisites #
The following items are must be performed prior to executing the script:
* Install Python3 (any version) including Pip installer
    * Ensure python executable is in the system path
* Run **pip install -r requirements.txt** from the installation directory
* Add a system environment variable for each Data Location containing a password file:
    * Name = Location name in config file (e.g. **ConcurSource**)
    * Value = Decryption key for the password file
* Install gnupg
* Ensure gpg executable is in the System path
* Import the private key:
	* **gpg.exe --import keys\pgp.priv.asc**
    * Supply the password when prompted

# Running the script #
* The script may be called manually from the commandline or via a schedule task by running:
    * **python.exe app.py**

# Configuration #
All of the config settings are specified in app.config in the installation directory. The specific setting values are commented accordingly. At a high-level, the following should be configured:
1. Specify datasources (currently only SFTP sources implemented)
2. Build a config section for each data source with appropriate connection, file mask, and destination information.
3. Build a config section for each destination (currently SMB and SFTP destinations implemented), with appropriate connection, file mask, and path information.

# Error handling #
All uncaught errors are logged to the error log file specified in the configuration. Additionally, an attempt is made to send an e-mail notification as specified in the configuration.

# Creating a datasource password file #
* Run **python.exe** from the install directory, and execute the following:
    * **import key**
    * **key.GenerateKeyFile('filename')**
    * Supply the password to encrypt when prompted
    * The command will create a password file and associated decryption key

# Getting Known Hosts
* From an Linux/Unix/Mac terminal:
    * **ssh-keyscan _url_**
