# Debian

## Set up security access to remote host

1. Connect to shell via ssh to remote host
  ```
  ssh root@<remotehost>
  ```

2. Create a new user
  ```shell
  $ adduser <username>
  ```

3. Install `sudo` and add the new user to the `sudo` group
  ```shell
  $ apt update && apt -y upgrade && apt install sudo
  $ usermod -aG sudo username
  ```

4. Copy key from local to remote host 
  ```shell
  $ ssh-copy-id -i ~/.ssh/id_rsa.pub <remotehost>
  ```

5. Deny authorization to remote host via password  
  ```shell
  $ vi /etc/ssh/sshd_config
  ```
  Change line starts with `PasswordAuthentication` to
  ```
  PasswordAuthentication no
  ```

6. Restart SSH-server
  ```shell
  systemctl restart ssh
  ```


## Deploy
1. Install dependencies
  ```shell
  $ sudo apt install -y git python3-pip python3-venv python-dev build-essential 
  ```

2. Create user `lawzy` and login
  ```shell
  $ sudo adduser lawzy   
  $ sudo -u lawzy -i
  ```

3. Clone repo and enter to dir
  ```shell
  $ git clone https://github.com/kephircheek/lawzy.git && cd lawzy
  ```

4. Create virtual environment and activate it  
  ```shell
  $ python3 -m venv venv
  $ source venv/bin/activate
  ```

5. Logout, copy `systemd` service script via `sudo` user and run it 
  ```shell
  $ exit
  $ sudo cp -f /home/lawzy/lawzy/debian/lawzy.service /etc/systemd/system/
  $ sudo systemctl start lawzy
  $ sudo systemctl enable lawzy
  ```
