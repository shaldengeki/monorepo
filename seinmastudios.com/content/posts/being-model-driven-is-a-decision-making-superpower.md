---
title: "Being model-driven is a decision-making superpower"
date: 2021-10-24T19:13:53-07:00
draft: true
---

Something I find myself doing regularly at work is needing to make decisions about what to work on, or how much time to spend working on something. When this happens, I've recently found it useful to create a model of the problem or decision, to guide my decisions.

<!-- go, 2021-10-24: Who is this for? -->

# What does "being model-driven" mean?

I think an example is useful here. My team at work is responsible for maintaining a bunch of tools that engineers at the company use on a daily basis. We were planning on making some structural changes to a codebase, and some of those changes were probably going to break a tool that we knew some folks used. So we were faced with a few questions:

- Should we do some work _now_ to keep the tool from breaking?
- Should we wait until it breaks to fix it?
- Should we not fix it at all?
- If we do work to fix it, how much time should we spend?

After chatting with a coworker, I realized that the common thread that we needed to answer these questions was "how much time does the tool save people?" If the tool wasn't saving people any time, we obviously wouldn't want to spend any time fixing it; if it saved a lot of time, we could justify a big investment in making it work going forward. We sat down and put together a simple model to estimate this:

```
time saved = (# of times used) * (time spent without tool) - (time spent by tool)
```

Once we had this model, we plugged in optimistic and pessimistic guesstimates for each of the parameters, and got a sense for the potential range of the tool's usefulness. Based on that, it seemed there was a possibility that the tool was moderately useful, so I put together a plan to fix the tool with about a month of engineering work.

To get a precise estimate, we spent roughly a week gathering data to measure each of these parameters. It became clear pretty quickly that we weren't going to be able to justify anywhere near the amount of engineering time we'd need to fix it going forward, so we announced that we were going to deprecate it. This let us avoid nearly a month of wasted work.

<!-- go, 2021-10-24: maybe another example here? -->

<!-- go, 2021-10-24: maybe a general how-to? steps to achieving this? -->

# Why is this useful?

Obviously that's great, but there are many other reasons why being model-driven is a useful approach. First, it forces you to clarify your thinking. To put a model like this together, you have to make totally precise what you're including and excluding. If you're including things that other people don't think are important, or leaving out things that other people think are important, then a model lets you explicitly assess everything and clearly trade off between them.

Second, a model can give you the opportunity to clarify uncertainties. As an example, sometimes you won't be able to directly measure things in your model, or all you have offhand is a rough estimate. When that happens, it's useful (both to your own credibility as an engineer and to the company's overall decision-making) to point out these places, and point out explicitly what would make you reconsider the decision you're making. That provides some cover if you gather data and your estimates turn out to be wrong (as they are overwhelmingly likely to be).

Finally, developing a model for decision-making often helps you quantify the (expected) impact of your work, and can thereby help you make the case for why the work is important to the wider business. I've found this useful on occasion as a way to hold myself accountable, too; more than once I've been surprised by work that I _thought_ was invaluable turning out to be low-impact.

# What can make this hard?

- Difficult-to-compare axes of value
- When people can't agree on a simple model
- Difficult-to-measure parameters

# Appendix: doesn't everyone do this?

<!-- go, 2021-10-24: add additional sourcing here; want to show this isn't a thing that's necessarily common -->

You'd be surprised! I've personally found that the overwhelming majority of the time, decisions at work are made on the basis of individuals' hazy, ill-specified intuitions.

As an example, a team I was working on was talking about ways we could better-support engineers at the company who were new to Python, but needed to use it in their day-to-day work. One person brought up the idea of running classes on a quarterly basis. The manager of our team intervened to say that this idea had been rejected before because it "wasn't worth the time". It turns out that nobody knew whether any data or evidence had been used to assess that classes "weren't worth the time"! [wasnt-worth-time]

As another example, 

***

1. [wasnt-worth-time] I found this particularly notable because not only was a past decision based on (presumably) zero evidence being used to pre-empt future decisions, at this particular company, leadership had recently decided to roll out fixed data retention policies across emails and chats, which made it _literally impossible_ to figure out how the decision had actually been made. Data retention is bad, y'all.

