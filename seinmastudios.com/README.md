[seinmastudios.com](https://seinmastudios.com)
=================
Source code for my [personal website.](https://seinmastudios.com)

Writing a post
--------------
Requires:

- [Hugo](https://gohugo.io)

1. `./bin/new-post my-new-post`
2. (optional) `./bin/edit-post my-new-post`

Publishing
----------

tl;dr: Mark post as non-draft, commit and push to `main`.

Main commits deploy to [the site](https://seinmastudios.com) via a Github Actions workflow that compiles the site and pushes it to Github Pages. You should be able to simply merge into main and see changes reflected on the site within a minute or two.