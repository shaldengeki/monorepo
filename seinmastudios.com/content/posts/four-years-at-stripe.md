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

The team I joined was called Insight. It was a pretty unique environment - the fusion of two somewhat-unrelated teams, where one half (really, just @roberto) had some expertise in AWS cost optimization & attribution, and the other half (@markf[^5], @samson[^6], @dfradette[^7])

<figure>
    <img src="/images/2019-03-25-townsend-desks.jpg" />
    <figcaption>Row of desks we sat at </figcaption>
</figure>

- insight
- checker
- cost attribution (roberto)
- cost graph & solis (andres, sjung)
    - initial MVP
    - mongo, sequins
- targets
- pre-EDP
- RIs & savings plans (jenniferh)
- zstd
- going remote

![Remote office setup at home. Black desk with a monitor and laptop on it in the corner of a room with windows on both sides.](/images/2019-06-04-ssf-office.jpg)


# Scala/Zoolander Infra

- transfer, devprod, nameth
- dc, long
- dev/ij
- JVM monorepo
    - repo merge w/beala, long
    - workspace unification
- log4shell

# Schemas Infra

- tech lead
- schema sharing
- registry
- mentoring

# Looking forward

[^1]: Roberto Fernandez
[^2]: Will
[^3]: Keagan
[^4]: TODO
[^5]: Mark Feeney
[^6]: Samson 
[^7]: Drew Fradette