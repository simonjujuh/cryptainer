# Cryptainer

**Cryptainer** is a python-wrapper designed to manage encrypted volumes directly from the command line.

This tool was initially designed to accommodate the preferences of various penetration testers, allowing them to manage their encrypted mission containers using the tool of their choice, while adding several useful features.

Cryptainer is now a generic version that supports two standard tools for creating encrypted volumes, but its code structure makes it easy to support additional tools.

## Installation

Soon...

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

Display the list of volumes present in the configured volumes_dir directory. The type of volume is indicated, with detection based on the volume's extension (e.g., .gocrypt, .vcrypt, etc.).

```bash
cryptainer list
```

Create an encrypted volume. The name must not include an extension or path. The tool automatically adds the appropriate extension based on the type.

```bash
cryptainer create -t gocryptfs name # -s is ignored for gocryptfs
cryptainer create -t veracrypt -s 10G name 
```

Mount an encrypted volume. Auto-completion via <TAB><TAB> can be enabled.

```bash
cryptainer mount $volume_1 $volume_2 $volume_3
```

Unmount an encrypted volume. Auto-completion via <TAB><TAB> can be enabled.

```bash
cryptainer umount $volume_1 $volume_2 $volume_3
```