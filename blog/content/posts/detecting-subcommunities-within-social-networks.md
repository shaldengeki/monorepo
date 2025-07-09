---
title: "Detecting Subcommunities Within Social Networks"
date: 2012-08-26T02:03:46-08:00
draft: false
---

I've been an active member of an online social forum called End of the Internet for a few years now. The site is particularly interesting because it's both closed off to the public and has been relatively long-lived despite the lack of new users; the active posters on the site have been around since the site's founding in early 2004, and watching the topics of discussion shift as the userbase grows and ages has been really interesting.

I've always thought that it would be really fun to generate a map of the social networks on the site, and in recent years the rise of niche-interest megatopics has been of particular concern to the site staff. For a long time, I've been trying to find a metric that accurately describes the distance between users on this forum, and I think I've finally hit upon something that gives sensible results.


1. First, I take the postcounts for a pair of users in all topics in which at least one of them has posted.
2. If the number of topics in which both of them have posted is less than some threshold (20), I throw this pair of users out and move on to the next pair.
3. Then I calculate Pearson's r (correlation coefficient) for this two-dimensional array of post counts. If it's above a certain level (0.2), then I place an edge connecting these two users, weighted by the value of Pearson's r.

Afterwards, I've got a weighted map that I toss into [Gephi](https://gephi.org/) and run Forceatlas2 on for awhile to let the map come to equilibrium. Then I run the [default clustering algorithm](http://lanl.arxiv.org/pdf/0803.0476v2.pdf) in Gephi to assign each node to a community, and do a few small coloring/labeling touchups to make the graph look nice. I throw the resultant gexf file into [SigmaJS](http://sigmajs.org/) and get something like this:

![ETI network graph for 2012](http://seinmastudios.com/wp-content/uploads/2012/08/systemofyetis-1024x594.png)

Pretty cool, huh? Each of these clusters corresponds to an actual niche on the site, which was *really* cool to see just fall out of the data. [You can see an interactive version of the map here](http://llanim.us/etiNetworkGraph.php). It's really interesting to see the degree to which the site has split into niche topics, and in particular it's kind of scary to see just how little each of the largest clusters links with the rest of the map.

There are some issues with the metric I'm using; for one, it doesn't work particularly well for users that don't post in any particular niche megatopics, but nevertheless do have some friendships with users on the site. I'll see if I can't figure out a way to incorporate them better into the network. In the meanwhile, I'm pretty satisfied with how things turned out, and I'm in the process of generating similar graphs for previous years.
