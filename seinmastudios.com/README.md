seinmastudios.com
=================
Source code for my personal website.

Deployments require [Ansible](https://www.ansible.com). To run it, you can do:
```
ansible-playbook site.yml
```
This requires an SSH key at `~/.ssh/seinmastudios.production.pem`, and the secrets vault password.
