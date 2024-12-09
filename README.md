# Cryptainer

A CLI wrapper to manage encrypted volumes from different tools.

## To-Do

- [x] Implement the veracrypt container module
    - [ ] Hide veracrypt output from subprocess calls
    - [ ] Prompt the sudo password when needed
- [x] Implement the gocryptfs container module
- [ ] Find a reliable way to detect the volume TYPE
- [ ] Add support for keepass database
    - [ ] If keepass i set in the config, then keepass can't be user
- [ ] Add pruning feature
- [ ] Add cleaning feature