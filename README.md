# Cryptainer

**Cryptainer** is a python-wrapper designed to manage encrypted volumes directly from the command line.

This tool was initially designed to accommodate the preferences of various penetration testers, allowing them to manage their encrypted mission containers using the tool of their choice, while adding several useful features.

Cryptainer is now a generic version that supports two standard tools for creating encrypted volumes, but its code structure makes it easy to support additional tools.

## Installation

- Build and install the package

```bash
# build package
python3 -m build

# install the package
pip3 install ./dist/cryptainer-$VERSION-py3-none-any.whl
```

- Optional: install auto completion (https://kislyuk.github.io/argcomplete/)

```bash
pip install argcomplete
activate-global-python-argcomplete

echo 'eval "$(register-python-argcomplete cryptainer)"' >> ~/.zshrc
echo 'eval "$(register-python-argcomplete cryptainer)"' >> ~/.bashrc
```

## Usage

### Basic features

Cryptainer is a command-line tool that allows you to perform simple operations on encrypted volumes:

- Create volumes
- Mount volumes
- Unmount volumes
- Display a list of volumes

### Configuration

A configuration file with user preferences is available at `~/.cryptainer/config.ini`.

```ini
[volumes]
volumes_dir =  # path to the directory containing the volumes
mount_dir =  # path to the directory used as the base for mount points
```

### Common commands

* Display the list of volumes present in the configured volumes_dir directory.

```bash
cryptainer list
```

* Create an encrypted volume. The name must not include an extension or path. The tool automatically adds the appropriate extension based on the type.

```bash
cryptainer create -t gocryptfs name # -s is ignored for gocryptfs
cryptainer create -t veracrypt -s 10G name 
```

* Mount an encrypted volume. Auto-completion via <TAB><TAB> can be enabled.

```bash
cryptainer mount name1 name2 name3
```

* Unmount an encrypted volume. Auto-completion via <TAB><TAB> can be enabled.

```bash
cryptainer umount name1 name2 name3
```

### Volume type detection

To detect volumes is complex, and the possibilities vary depending on the type of container. Here are the detection rules that have been implemented:

- gocryptfs container: The container is a directory with a gocryptfs.conf file inside.
- veracrypt container: The container is a file, and it ends with the .hc extension.
    - Veracrypt containers are problematic, as highlighted in this report: https://www.raedts.biz/forensics/detecting-truecrypt-veracrypt-volumes/


## TODO

- [x] Implement auto-mount  
- [x] Implement mounting and unmounting of multiple volumes  
- [x] Implement VeraCrypt containers  
- [ ] Implement the pruning feature  
- [x] Implement the autoclean feature  
- [x] Implement bash or zsh completion  
- [x] Implement a Keepass module  
- [x] Add the installation procedure  
- [x] Harmonize code understanding, particularly regarding paths and project names  
