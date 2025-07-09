+++
title = "Debugging stories: the inconsistent database"
date = 2022-12-05T09:33:10-05:00
images = []
tags = ['tech', 'bugs', 'debugging', 'war-stories']
categories = []
draft = false
+++

Recently at work I ran across a bug which I thought was kind of interesting, so I figured I'd write it up.

At my company, my team builds and owns the infra that helps other engineers work with schemas - descriptions of how datasets and APIs are structured, that can be shared and reused across different languages and applications to interoperate with the same data and APIs.

One system we rely on is a database that we use to register and store these schemas. (Internally, we call this the _schema registry_.) A user came in reporting that they'd made a change to their schemas awhile ago, but they weren't showing up in the registry, and I started digging in.

The first thing I did was actually verify that the new version of the schemas weren't actually registered. One of these schemas we'll call "schemaB":

```bash
curl http://schema-registry/subjects/schemaB/versions
[]
```

Yep, it was missing all right. That confirmed that there was a real problem.

The next thing to do was to figure out what happened. The thing that actually stores new schema versions in the registry (the _schema publisher_) is an application that we own and emits logs, so I went to take a look at those logs. The logs showed something like this happening:

```text
Checking if schemaA@1.2 exists...
Attempting to register schemaA@1.2...
Success!
Checking if schemaB@1.1 exists...
Attempting to register schemaB@1.1...
ERROR from schema registry: schemaB's dependency schemaA@1.2 does not exist!
```

Here, "1.2" and "1.1" are new versions of the schemas that the user is trying to register. In this case, schemaB depends on schemaA, so we try to publish schemaA@1.2 first, and after that succeeds, we try (and fail) to publish schemaB@1.1.

Note that this is _weird_ - the schema registry was telling us that it registered schemaA@1.2, and then immediately afterwards, complaining that it didn't exist. Wait, _does_ it exist?

```bash
curl http://schema-registry/subjects/schemaA/versions
[1.1, 1.2]
```

Yep, looks like it does. So what I knew was:

- The registry sometimes knows that schemaA@1.2 exists, but
- Sometimes it doesn't.

At this point, I realized that I was asking a question, and _different entities_ were answering, with _different views of the world_. That implied that the schema registry was a distributed system.

To confirm this, I re-ran the above request a few times:

```bash
curl http://schema-registry/subjects/schemaA/versions
[1.1, 1.2]
curl http://schema-registry/subjects/schemaA/versions
[1.1, 1.2]
curl http://schema-registry/subjects/schemaA/versions
[1.1, 1.2]
curl http://schema-registry/subjects/schemaA/versions
[1.1]
```

Bingo - a smoking gun - one of the schema registry's request-servers only knew about 1.1, and not 1.2. This is typical of a distributed system that's _eventually-consistent_ - after you do something that changes state in some way, not all parts of the system get updated immediately, and it might take some time for everyone to get on the same page.

I re-ran the publisher, and:

```text
Checking if schemaA@1.2 exists...
schemaA@1.2 exists, skipping.
Checking if schemaB@1.1 exists...
Attempting to register schemaB@1.1...
Success!
```

I reported back to the user that their problem had been fixed, and discussed some potential fixes with the team.

In our case, we ended up adding some retry logic to the publisher - in the case where a registration attempt failed because of missing upstream dependencies that we'd just published, we'd back off for a little while, then retry publishing (repeating this for a fixed number of attempts in case of failure).

But ideally (at least from the perspective of making the client simpler), the registry should be _strongly-consistent_ instead of just _eventually-consistent_. With strong consistency, the registry would basically wait until all its nodes were aware of the update before returning a successful result. That would eliminate the intermediate inconsistent state - when the registry returned a successful publishing result, subsequent requests depending on that schema would be able to access it. That'd prevent errors like the one we ran into here, at the cost of making registration requests blocking operations.
