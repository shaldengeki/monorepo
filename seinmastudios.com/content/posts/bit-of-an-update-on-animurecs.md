---
title: "Bit of an update on Animurecs"
date: 2013-04-13T00:27:56-08:00
draft: false
---

It's been a long time since I talked about this, but I've been [re-writing Animurecs in PHP](https://github.com/shaldengeki/animurecs "Github repository"), having gotten fed up with feeling like I was working around Rails to get things done. Wasn't an easy decision - there was a lot of work already done, and I hadn't written an MVC framework before. I've had a lot of fun, though, and I feel like my programming skills have benefited from it! The project has evolved from originally a Danbooru-esque anime database to a social network that uses machine learning (largely based off of [Simon Funk's explanations of SVD](http://sifter.org/~simon/journal/20061211.html "Simon Funk blogpost")) to figure out what each user's tastes are and recommend anime they'd like based on that. There's also tons of unexplored ways to encourage people to watch anime together and discuss it in some depth; I'm hoping to encourage that with this project!

On that note, it's reached a point where I'm pretty comfortable putting it into beta status -- [you can find it here](https://animurecs.com "Animurecs"). After registering and confirming your email, you can add a few entries to your anime list -- the SVD is recalculated every hour on the hour, so you should see recommendations popping up for you then. You can also add friends on the site, if they're registered, and the site will figure out potential groupwatches you can join. Check it out!

Finally, the site is under pretty heavy development, so you should expect to encounter a few rough edges here and there. If and when you run into bugs, you should feel free to contact me [via Twitter](https://twitter.com/guocharles "Twitter profile") or [just post on my Animurecs profile](https://animurecs.com/users/shaldengeki)!
