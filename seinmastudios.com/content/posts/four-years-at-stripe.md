+++
title = "Four years at Stripe"
date = 2022-12-05T10:31:23-05:00
images = []
tags = []
categories = []
draft = true
+++

I recently hit my four-year mark at Stripe. This is more than twice as long as I've been at any prior employer, and I thought it might be fun/interesting to do a little chronology. Be forewarned: a lot of this is going to be me ruminating over past events and be a lot less focused than my typical posts.

# The first month

I joined Stripe late November 2018, right after they had just moved into new offices on Townsend, next to the Caltrain station in San Francisco. My prior employer the day I left was roughly ~1/10th as big as Stripe on the day I joined, and stepping into a huge, shiny, mostly-empty office was definitely a shock. I remember standing in the ground floor presentation space, looking up the central shaft in the middle of the building at all the floors, and thinking to myself: _Well, you've joined a real company._

![Stripe office on Townsend.](/images/2019-07-11-townsend-building.jpg)

The first two weeks were set aside for onboarding -- back to back sessions for hours -- and I remember the flood of information and new people I was absorbing being... a little overwhelming, but also exhilarating. My onboarding class (~25, which was large at the time!) bonded, sort of like you'd imagine survivors of a shipwreck bonding as they're swept from place to place.

I had a daily short 1:1 with my teammate and onboarding buddy - @roberto[^1] - that I was perpetually late to. @roberto, to his great credit, was patient and understanding with how flustered I was.

The Friday of the second week, we transitioned from basic onboarding sessions to /dev/start. /dev/start is Stripe's engineering-specific onboarding - they have the engineers in an onboarding class divide up into teams of 4-6. Each team is led by a (tenured) Stripe engineer on a two-week project to deliver a small, but real, feature. The idea is to give incoming engineers an understanding of what it's like to deliver something at Stripe on an accelerated schedule in an area they'd otherwise not have the opportunity to work on, while also giving tenured Stripes an opportunity for leadership experience and to work on something that might not get prioritized for headcount or other reasons.

I really loved this experience! Our project was building a nicer and safer abstraction layer for emails that'd get sent to Stripe customers, and migrating a small set of emails over to our abstraction layer. It was great to actually work together with people in my onboarding class (@wlue[^2] and @keagan[^3] in particular), and to have access to our mentor (@TODO[^4]) who patiently put up with our incessant questioning about Stripe. /dev/start was a great way for us to safely figure out how to work effectively with other engineers using Stripe's developer tools -- figure out the mechanics of setting up branches, what the process for code reviews & merging work was going to look like, et cetera. I can't recommend this program enough, and I think more companies should do this.

Two weeks later, we delivered the thing, wrote our first shipped email, and I transitioned fully onto my home team.

# Insight/Efficiency

The team I joined was called Insight. It was a pretty unique environment - the fusion of two somewhat-unrelated teams, where one half (really, just @roberto) had some expertise in AWS cost optimization & attribution, and the other half (@markf[^5], @samson[^6], @dfradette[^7]) were more interested in application reliability. @roberto, @samson, and I were based out of the SF office, while @dfradette and @markf were in the Toronto area.

![Row of desks in an office.](/images/2019-03-25-townsend-desks.jpg)
*Row of desks where we worked on the first floor. Later, we moved up to the second floor, which had much better lighting.*

The team was a little bit of an unorthodox fit with a wide mix of competencies, but we learned a ton from each other as a result. I started out working on one of Stripe's reliability tools, simplifying its backend and UI with @dfradette. The UI has stuck around to this day, which I'm happy about.

I also worked on the cost attribution side of things with @roberto. The way that cloud cost attribution worked was a series of data pipelines that had been built by senior engineers who had since moved onto other teams. These data pipelines took various data sources in and outputted a series of rows representing which teams owned how much cloud spend, broken down by platforms they used. We wanted to make the data pipeline include more of our costs, which meant running around to all of our internal platforms and working with them to expose usage data broken out by users, which was no small task - but it was helped considerably by the company deciding around this time that our work was extremely high-priority and saying so very loudly. We'd then take this data in our pipeline and make sure it fed into the downstreams aggregating totals by team.

This was a pretty rough time for me personally. I spent a lot of my time _utterly_ lost as I dug into all these unfamiliar areas, not feeling productive and being under a lot of stress, and wondering if I'd made the right decision joining Stripe. @roberto kept reminding me that we were just looking to do something rough ("directionally-accurate" was the phrase) and improve it over time, which was a huge relief to hear.

For self-promotion reasons, most of the engineers on Insight believed that the math involved in the attribution was complex, having been previously described in intimidatingly-mathy jargon like "flow networks". After reading the code, I realized this was totally mistaken - the math wasn't anything more-complicated than middle-school algebra, just multiplying a series of percentages together in the obvious way. I gave a talk walking everyone on the team through the code piece by piece, and the sentiment was overwhelmingly "... that's it? That's all we do?" This is honestly one of things I'm proudest of during my time here -- the couple of hours I spent on this was _extremely_ valuable and meant that everyone felt comfortable contributing to and explaining a critical codebase that our team owned. Fighting this prior mischaracterization and convincing people that _no, what we're doing is dead-simple and understandable_ was an ongoing battle that we ultimately ended up winning.

A few months in, the team split up as part of a re-org, and I landed on the new Efficiency team with @roberto, reporting to @smruti[^8]. Working with another team member @andres[^9], @roberto and I built out an interactive web UI, powered by a redesigned cost attribution data pipeline , that let people not just view their attributed cloud costs over time broken out by top-level line-items like "Mongo" and "Hadoop", but also click through to see further breakdowns within each lineitem like individual jobs and database collections, so folks could figure out what was driving changes in their costs and decide where to do optimizations. 

Around this time @sjung[^10] joined, from the Observability team, as did @jenniferh[^11]. This is about when I think the golden era for Efficiency started, and we did a _ton_ of work I'm proud of under our tech lead @djudd[^12], including but not limited to:

- Significantly improving our cost optimizations with better forward-looking Reserved Instance and Savings Plan provisioning (don't sleep on these, the discounts are _massive_)
- Engaging with infra teams on optimizations on their platforms, like rolling zstd compression out to Spark-generated datasets, or utilizing spot instances in CI
- Working with Finance to help drive financial planning with our data
- Moving all of our cost data to include all the various AWS discounts between different products, and based on our Reserved Instance and Savings Plan provisioning
- Controlling our S3 costs by implementing a "brownout" process, where access to unused data would be shut off gradually over time

On the other hand, there were some missteps in retrospect:
- Early on, we made the decision not to invest in AWS Graviton instances, judging that the costs were far too high and the payoffs too uncertain to be worth it. Now it's clear that the payoffs are real, this decision was wrong, and it would have been worth it for us to drop virtually all of our other work to push this.
- We attempted several times to roll out processes whereby teams would set cloud spend targets and try to hit them on some cadence. In retrospect, we should've gotten executive sponsorship and driven this from the top down. Teams repeatedly told us that they couldn't justify prioritizing efficiency work over product work, and we needed a clear reconciliation process between competing priorities.

Either way, looking back, I dove into Efficiency knowing basically nothing about cloud costs, and coming out the other side an expert in a ton of new stuff, having done really impactful work on the top company priority for a decent stretch of time. I couldn't have done it without being surrounded by the incredibly-bright and motivated people I've mentioned, and without being in an environment that trusted and empowered us to take educated risks. This was exactly the sort of experience I was looking to gain by working at Stripe, and even if my time at the company had ended here, I would've felt satisfied.

It also helped that doing good work was rewarded. I was promoted pretty quickly after I joined, and Stripe rewarded me with stock grants and spot bonuses in cash when I did something particularly out of the ordinary. This was pretty great, considering I already felt pretty good about my compensation at Stripe, and the struggle to get a promotion through at my last company was what ultimately pushed me out the door.

# Scala/Zoolander Infra

Backtracking a bit, in May 2019, I took part in a four-month program at Stripe experimenting with converting Bay Area employees to fully-remote status. Stripe paid for all the equipment I needed to set up a remote office -- desk, monitor, chair, the works.

![Remote office setup at home. Black desk with a monitor and laptop on it in the corner of a room with windows on both sides.](/images/2019-06-04-ssf-office.jpg)

For four months, I worked from home more or less full-time. I'd already been working from home once or twice a week before this, and was interested to see how fully-remote would work out for me -- this was one of the reasons I joined Stripe in the first place, as it had a reputation for being remote-friendly. The experience was kind of a letdown in terms of how much of a non-event it was! Basically nothing changed, aside from me having a _ton_ of extra time not spent commuting, and spending a _little_ extra time reading and writing docs.

The reason I mention this is that in late 2019, I started thinking about transferring to another team at Stripe. I'd been talking to my manager (@smruti) for a few months about wanting to do this eventually - I joined Stripe to work on developer productivity and enablement, and Efficiency wasn't the greatest fit for that long-term. In November / December 2019, after talking with @nameth[^13] and then @dc[^14], I decided to pull the trigger and transfer onto the Scala team under the Developer Productivity org. To Stripe's credit, this process was _extremely_ smooth, and happened quickly with (as far as I can remember) no paperwork on my end, other than signing a revised employment contract with my new manager's name on it.

And then in March 2020, COVID-19 happened. I remember Stripe moving quickly and responsibly early in the pandemic -- they shut down offices very quickly, and gave everyone a generous budget to procure home office equipment.

- dc, long
- dev/ij
- JVM monorepo
    - repo merge w/beala, long
    - workspace unification
- log4shell

# Schemas Infra

- tech lead
- schema sharing & registry
- mentoring

# Looking forward

[^1]: Roberto Fernandez
[^2]: Will
[^3]: Keagan
[^4]: TODO
[^5]: Mark Feeney
[^6]: Samson 
[^7]: Drew Fradette
[^8]: Smruti Patel
[^9]: Andres Castenada
[^10]: Stephen Jung
[^11]: Jennifer Hwang
[^12]: David Judd
[^13]: Nameth
[^14]: Dan Crosby