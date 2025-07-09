---
title: "Forecasting Using Seasonal Adjustment Factors"
date: 2013-04-14T14:57:29-08:00
draft: false
---

I just happened upon [Analytics Made Skeezy](http://analyticsmadeskeezy.com/), a blog written by John Foreman, Chief Scientist at MailChimp. He posts every so often detailing various techniques used in analytics, ranging from revenue management using price elasticity estimation to clustering and community detection. But there's a twist - all of the posts are written from the perspective of a (presumably fictional) college student who finds himself working business analytics for an international druglord! It's very much a Breaking Bad-esque take on what is already becoming a very sexy field. Go take a look, it's well worth spending an afternoon on if you're at all interested in the topic.

Anyways, I was reading through the posts and I found myself reading the entry on [forecasting demand for drugs based on prior monthly data](http://analyticsmadeskeezy.com/2012/11/15/forecasting-made-skeezy-projecting-meth-demand-using-exponential-smoothing/). Our hapless college student goes through the motions, explaining how to use what are called seasonal adjustment factors to nudge an otherwise-linear regression upwards and downwards to reflect seasonal fluctuation in demand. What really struck me was that this is almost exactly the method I independently worked out a year or two ago on End of the Internet, forecasting user activity numbers from historical data. I started doing this analysis after some major changes were made to the structure of the site and incentives for users to participate, to see how they'd affected the community as a whole.

![ETIStats User activity projections for 2012](http://seinmastudios.com/wp-content/uploads/2013/04/activeUsersWithProjectionsJanuarytoDecember-1024x466.png)

What I did then was a little more elementary with regards to smoothing, and I used a couple of different variables to generate my projection, but the basic method remains the same - for each year, you figure out how much each month in that year deviated from the average value of your metric for that year. Then you either:

1. average all of these monthly deviations for Jan, Feb, Mar, etc. individually to obtain your seasonal adjustment factors, or
2. perform some sort of regression on each month's yearly deviations if you believe that the factors are changing over time.

From there, you can use a simple recursive multiplicative model using the prior month's data and your seasonal adjustment factors to obtain any future month's predicted value.

Back when I was doing this for End of the Internet, it was mostly a passing curiosity - I tracked numbers for a few months using the python daemon I'd already written and wrote a post each month with the new numbers and revisions to the model. I went back today and compared the performance of my (more elementary) ETIStats model to the exponential smoothing model described by John for the year of 2011:

![For the exponential smoothing and ETIStats projection methods](http://seinmastudios.com/wp-content/uploads/2013/04/postCountPredictionErrorsExpSmoothETIStats.png)

As you can see, exponential smoothing outperforms my original model; the RMSE is 67022.55, as opposed to ETIStats's RMSE of 91581.66. Plus, the variation in monthly error seems to be a lot lower for exponential smoothing; the variance in the absolute percent error is almost half that of my original model. Still, the general trends seem to remain largely intact, and given the noisy data I had at the time for the other variables I was tracking, I'm pretty pleased with my original results!
