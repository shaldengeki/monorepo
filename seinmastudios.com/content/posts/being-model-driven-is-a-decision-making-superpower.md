---
title: "When in doubt, make a model"
date: 2021-10-24T19:13:53-07:00
draft: true
---

<!-- go, 2021-10-24: Who is this for? -->

At work, I often find myself needing to make decisions about what to work on, or how much time to spend working on something. When this happens, I've found it useful to create a model of the problem or decision, to guide my decisions. I think that this is a skill that anyone (not just software engineers) can exercise and benefit from, so I thought I'd write up a short post walking through what I do.

## Picking what to model

My team is responsible for maintaining a bunch of tools that other engineers use every day. Recently, we were planning on making some changes that would probably break a tool that we knew some folks used. So we were faced with a few questions:

- Should we do some work to keep the tool from breaking?
- Should we wait until it breaks to fix it?
- Should we not fix it at all?
- If we do work to fix it, how much time should we spend?

After chatting with a coworker, I realized that the common thread that we needed to answer these questions was "how much time does the tool save everyone?" If the tool wasn't saving any time, we obviously wouldn't want to spend any time fixing it; if it saved a lot of time, we could justify a big investment in making it work.

## Putting a model together

We sat down and put together a simple model to estimate the time saved by the tool. The first version looked something like this:

```
total time saved = (total time that would otherwise be spent without the tool) - (total time that was spent with the tool)
```

Once we had this, we thought about how we'd estimate or measure the values on the right. The last term on the right was something we could measure directly with timing metrics within the tool itself.

 The first term on the right, though, was difficult to measure without running something like an A/B test, turning the tool off for a subset of users. We decided to split that term up into two parts, making it a little easier to estimate or measure:

```
total time saved = (# of times used) * (average time spent without tool) - (total time spent by tool)
```

That's it! I think it's helpful to keep your model as simple, if you can; it makes decision-making much easier, since there's less stuff to measure and reason about.

## Making a decision

Once we had this model, we plugged in optimistic and pessimistic guesstimates for each of the parameters. This helped us do two things:

1. Sanity-check the model: if it gave us implausible results, we'd know something was wrong with the model
2. Establish the range of potential values: if the time saved was going to be large even under pessimistic estimates (or small under generous estimates), then we'd have our answer immediately

Based on our potential range, it seemed there was a possibility that the tool was moderately useful, so I put together a plan to fix the tool with about a month of engineering work.

In the meanwhile, to get a more precise estimate, we gathered data over a week to measure each of these parameters. The real-world data we gathered indicated that the time savings from this tool was very low, which meant that we weren't going to be able to justify anywhere near the amount of engineering time we'd need to fix it going forward. So we announced that we were going to deprecate it, which let us avoid nearly a month of wasted work fixing something that wasn't helping anyone.

All in all, we spent roughly three days actively working on this, so getting to avoid a month of wasted work seems like a good tradeoff.

<!-- go, 2021-10-24: maybe another example here? -->

<!-- go, 2021-10-24: maybe a general how-to? steps to achieving this? -->

## Why is this useful?

For a lot of reasons! Here's a few:

**Models are shareable and lend themselves to learning.** To put a model together, you have to decide what you're including and excluding, and how those things weigh against each other. If you're including things that other people don't think are important, or leaving out things that other people think are important, then a model lets you clearly trade off between them. This also allows other people to play with your model! In the broken tool example, when we published our decision, we shared our model as well. More than once, I've had a coworker take my model, plug in their own values for parameters, and come back with feedback about how "right" the model feels overall to them. That helps _me_ learn about how other people evaluate and build their own models, and incorporate that into future model-building.

**Models help make your work more visible.** Developing a model for decision-making often helps you quantify the (expected) impact of your work, and can thereby help you make the case for why the work is important to the wider business. I've found this useful on occasion as a way to hold myself accountable, too; more than once I've been surprised by work that I _thought_ was invaluable turning out to be low-impact.

**Models can give you the opportunity to clarify uncertainties.** Sometimes you won't be able to directly measure things in your model, or all you have offhand is a rough estimate. When that happens, it's useful (both to your own credibility as an engineer and to the company's overall decision-making) to point out these places, and point out explicitly what would make you reconsider the decision you're making. That provides some cover if you gather data and your estimates turn out to be wrong (as they are overwhelmingly likely to be).

**Your time is often your most valuable resource.** As a software engineer, I'm used to worrying about performance in computer-oriented ways: CPU cycles, memory limits, storage capacity. I've learned to be sparing with these resources, because historically computers were expensive, relative to human labor. That's no longer the case. For example, a computer with 100GB of memory on Amazon EC2 costs less than $0.25 to rent for an hour, whereas software engineering time in the Bay Area costs hundreds of times more on an hourly basis. I've had to learn that I should treat my own time as an incredibly valuable resource (there's a fixed amount of it, after all), and be willing to invest in optimizing time spent on projects.

**Good prioritization has compounding benefits.** Doing the right work early on unlocks value faster, and enables projects that can build off of that work.

**Knowng how to make a decision can be hard!** Sometimes I find myself in situations where I have a lot of information, but it's not clear how to make a decision based off of that information. In the example of the broken tool, we had a lot of varied feedback from our users about the tool -- some of them liked having the tool around, some of them found it annoying, and some were totally indifferent. The people on my team are super nice and didn't want to make anyone upset, so it was hard to know what the right thing to do was. Having a model helped us boil down what was really important in this situation and make the right decision for everybody.

## What can make this hard?

- Difficult-to-compare axes of value
- When people can't agree on a simple model
- Difficult-to-measure parameters

## Appendix: doesn't everyone do this?

<!-- go, 2021-10-24: add additional sourcing here; want to show this isn't a thing that's necessarily common -->

You'd be surprised! I've personally found that the overwhelming majority of the time, decisions at work are made on the basis of individuals' hazy, ill-specified intuitions.

As an example, a team I was working on was talking about ways we could better support engineers at the company who were new to Python, but needed to use it in their day-to-day work. One person brought up the idea of running classes on a quarterly basis. The manager of our team intervened to say that this idea had been rejected before because it "wasn't worth the time". It turns out that nobody knew whether any data or evidence had been used to assess that classes "weren't worth the time"! [wasnt-worth-time]

As another example, 

***

1. [wasnt-worth-time] I found this particularly notable because not only was a past decision based on (presumably) zero evidence being used to pre-empt future decisions, at this particular company, leadership had recently decided to roll out fixed data retention policies across emails and chats, which deleted all of our email / chat / groups history earlier than X months ago and made it _literally impossible_ to figure out how the decision had actually been made. Data retention is bad, y'all, but that's a topic for another day.

