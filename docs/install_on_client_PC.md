## Installation:

### Dependencies

1. Download and install cygwin

  Cygwin can be installed from https://cygwin.com/setup-x86.exe

2. Install programs on cygin:

openssh
wget
cron
python
pip
rsync
md5deep
gcc (optional)

Click the + sign next to the Devel category to expand it. Pick each of the following packages by clicking:

gcc-core : C compiler subpackage
gcc-g++ : C++ subpackage
libgcc1 : C runtime library
gdb : The GNU Debugger
make : The GNU version of the 'make' utility

3. setup ssh private key

ssh-keygen -t rsa

cat ~/.ssh/id_rsa.pub

Copy and paste this key to the authorized_keys file (.ssh/authorized_keys) on the server

Or you can do it directly like this:

cat ~/.ssh/id_rsa.pub | ssh yourusername@yourserver 'cat >> .ssh/authorized_keys'

Troubleshooting:

Change the permissions of .ssh to 700
Change the permissions of .ssh/authorized_keys2 to 640


