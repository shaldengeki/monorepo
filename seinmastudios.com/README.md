seinmastudios.com
=================
Source code for my personal website.

Writing a post
--------------
Requires:

- [Hugo](https://gohugo.io)

1. `./bin/new-post my-new-post`
2. (optional) `./bin/edit-post my-new-post`

Publishing
----------

Requires:

- [Ansible](https://www.ansible.com).
- SSH key at `~/.ssh/seinmastudios.production.pem`
- Secrets vault password

To publish:

1. `./bin/publish-post my-new-post`
