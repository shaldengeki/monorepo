---
title: "ECLS-K: A General Overview"
date: 2013-01-14T00:09:42-08:00
draft: false
---

So I'm taking classes this winter and spring; finally on track to finish my BA in math. One of the classes I'm taking is an intro sociology class - one of the overarching goals of the course is to understand the interplay between parenting and education, and how these two factors help children become successful later in life. As part of this investigation, we're using data gathered by the [Early Childhood Longitudinal Study, Kindergarten cohort](https://nces.ed.gov/ecls/kindergarten.asp "ECLS-K website") (or ECLS-K). This was a nationwide longitudinal study following a nationally representative sample of 21,000 kindergartners entering in 1998-1999. Unfortunately, I don't have access to every feature in the dataset - I get the feeling that it'd be difficult to know where to start if I did - so we'll be looking at a slice in our class.

Since we'll be working closely with this particular dataset, I figured it'd be interesting and useful if I did a series of posts looking at features and talking about what we can infer from the data. I don't have a whole lot of experience with education-related research; I followed the [LA Times's value-added analysis of teachers in the LA school district](http://www.latimes.com/news/local/teachers-investigation/) with some interest, but nothing really beyond that. It's pretty incredible that a study of this magnitude was able to be done at all, and it's kind of a shame that it's not done more frequently, given how (maybe) important K-12 education is to kids' futures. In addition, this will give me an excuse to brush up on my R/ggplot2 skills and (maybe) post some of my scripts - hopefully they'll be of use to people looking to learn.

In any case, let's get to it! Let's start off by getting a general idea of what the sample of kids we'll be looking at is like. Just a couple of bar charts for now:

![Gender distribution](http://seinmastudios.com/wp-content/uploads/2013/01/ecls-k-gender-hist.png)
![Racial distribution](http://seinmastudios.com/wp-content/uploads/2013/01/ecls-k-race-hist-1024x526.png)

Nothing terribly unexpected here; the US national male/female ratio is slightly under 1, so as far as a nationally-representative sample we've got some over-representation of males here. Looking at race, white non-hispanics make up approximately 56% of the sample and comprised 69% of the population in 2000. Black non-hispanics make up ~15% of our sample and ~12% of the 2000 population, while all hispanics make up ~18% of our sample and ~13% of the 2000 population, so we're over-sampling blacks and hispanics relative to white non-hispanics. Asians make up 6% of our sample, while they comprised 4% of the population, so in general we're over-sampling minorities.

![Age of kindergarten entry](http://seinmastudios.com/wp-content/uploads/2013/01/ecls-k-p1ageent-hist.png)

Looking at the age each child entered kindergarten, we see pretty normal results - a bell-shaped distribution centered around ~65.5 months, or ~5.5 years old. Makes sense, since kids enter kindergarten around age 5-6! The standard deviation of this sample is ~4.30, and you can tell just from looking that the vast majority of the responses fall between 60 and 72 months old. It's pretty interesting just how tight this distribution is - *everyone* falls between 4.5 and 6.7 years old, which I wouldn't have expected, since I remember there being some much older (and really young) kids in my classes later on. It's pretty cool to see parents valuing education so highly!

![Degree expected by parents](http://seinmastudios.com/wp-content/uploads/2013/01/ecls-k-p1expect-hist-1024x526.png)

Finally, a look at parental expectations for their kids. It's clear that college is the absolute gold standard in the US in terms of education; failing to complete a four-year degree is pretty clearly failing the expectations of your average parent (with ~41% of the responses). I honestly expected high school graduation to have a stronger showing here; I was under the impression that there was a much larger population that didn't particularly value undergraduate education, but it's clear that I was wrong. I feel like the proportion of parents expecting their kids to attain a post-graduate degree (~24%) is way out of proportion to what actually happens.

It feels weird having my preconceptions of our country's population corrected so significantly. Turns out I had an overly-pessimistic view of education in a couple of areas, so it'll be interesting to see if this continues to be true. Next time we'll look a little closer at these kids' environments to get a clearer picture of how parenting in the US is "normally" done!
