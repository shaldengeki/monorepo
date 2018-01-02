seinmastudios.com
=================
Source code for my personal website.

Writing a post
--------------
Requires:

- [Hugo](https://gohugo.io)

1. `hugo new posts/my-new-post.md && nano content/posts/my-new-post.md`
2. Commit to master & deploy

Deployment
----------
Requires:

- [Ansible](https://www.ansible.com).
- SSH key at `~/.ssh/seinmastudios.production.pem`
- Secrets vault password

To run:
```
ansible-playbook site.yml
```

