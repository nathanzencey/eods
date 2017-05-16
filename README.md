# EODS: Exploring Open Data Sets
EODS: Exploring Open Data Sets


## Summary

EODS currently consists of a web scraper, `scrape.py`, that looks through [a list of open data portals](https://github.com/sunlightpolicy/opendata/blob/master/USlocalopendataportals.csv) and tests each website to see if it uses Socrata. If a portal uses Socrata, the scraper goes through the site and compiles a list of the metadata (including views) for each of the data sets. It then calculates a normalized number of views (on a scale of 0 to 1) for each data set, so that the relative popularity of specific datasets can be compared across cities. Each of these lists of metadata is then exported as a CSV (found [here](https://github.com/gregjd/eods/tree/master/eods/output)).

The `output` folder (inside the `eods` folder) has sample results. Note that these samples only include the top 90 data sets for each city, and only about half of the Socrata cities. Web scraping this many pages can take quite a while, which is why I limited the results.

The next step is to analyze the data for trends. If we take each word in the title of each data set and assign it the value of either the number of views for that set, the normalized number of views, or the normalized number of views multiplied by the population, we can then sum all of these figures to get an aggregate "words that are in titles of data sets that are most viewed" value. The three respective calculation options will give results weighted for different purposes: the first will be weighted toward those portals that are most viewed, the second will weight all cities/portals equally, and the third will be weighted toward cities with larger populations.

We can also apply that technique to the words in the list of topics for each data set. See "Early results" below for results from doing this analysis on topics using normalized page views.

Moving beyond this, another consideration is that some data sets (like budget data) have a new set uploaded each year. For these, we can replace all the years numbers with text like "<YEAR>" and then sum the number of views for these data sets across years. This will give a better sense of how many views these types of data sets get, as the views won't be split up among a number of separate uploads.


## Motivation

When adopting open data policies and trying to make their data easier to use, one important issue for cities is determining which data sets to prioritize. This prioritization manifests itself in three ways:
- Some open data policies mandate specific data sets  that need to be included in the open data portal.
- For cities that are just starting to open up their data, these priority data sets can be the first ones they focus on making public.
- An important issue with open data is the adoption of [common standards for specific data sets](link). There is much work to be done here, as most open data sets do not conform to any standard structure, limiting the potential for their use. These priority data sets can be some of the first ones the open data community tries to develop common standards for.

I created EODS as a set of tools that can be used to understand and analyze data on the popularity of open data sets across cities, thus assisting with the three points above.


## Early results

A quick analysis of the topics of the most viewed data sets shows these as the top 15:

topic|score
---|---
alcohol|12.66636121
license|11.93841821
police|9.629868164
elections|9.283633078
beer|8.350822551
liquor|7.796312186
wine|7.76299113
shipping|6.76299113
crime|6.601969493
missouri|5.59121643
public safety|4.567057119
results|4.500888592
county|4.333576942
king county|4.06204654
fire|3.429160433

To generate these numbers, I used the technique described in the "Summary" section above, specifically using the list of topics associated with each data set, and using normalized page views. You can find a table with the full results [here](https://github.com/gregjd/eods/blob/master/eods/summaries/top_topics_normalized.csv). Also note that this used my sample data, which consists only of the top 90 data sets for about half the Socrata cities.

There are a few things we can observe here. Many of the top topics relate to alcohol, which likely indicates that one or more highly viewed data sets on this topic were tagged with many alcohol-related topics. Also we can see some geographical noise, with topics like "Missouri" and "King County" appearing prominently (a result of some places tagging many of their data sets with their location).

Still, this list offers some insights. We can see that popular open data set topics include those related to alcohol, licenses, public safety, and elections. If you check out the full list, other prominent topics include salaries, restaurant inspections, labor, health, GIS, open meetings, and transportation.

An important thing to keep in mind is that these topics are at the discretion of the uploaders, so some topics may appear more prominently because many cities use the exact same topic, whereas some other topics of highly viewed data sets might be less prominent on this list if different cities assign different topics to similar data sets.


## Next steps

There are a number of exciting directions for this project. These include:

### Refine techniques for grouping similar data sets

Some data sets may go by several different names across cities, or even within a city across years. For example, data on property taxes goes by names like: Property Valuation and Assessment Data, Residential Assessment, Property Tax Roll, and Property Assessment. Data on public employee salaries includes titles like: Employee Compensation List, Employee Earnings Report, and Citywide Payroll Data. These variations make it harder to assess the aggregate popularity of certain data sets across cities.

### Account for differences in upload date

We can use the number of a views a data set gets to assess its popularity. Currently, the scraper ignores upload date when looking at the number of views a data set has. This is fine for elementary analysis, but it does have shortcomings, namely the fact that data sets that have been online longer have had the chance to accumulate more views. It would be great to account for this fact. But how?

We could divide the number of views by the number of days since a data set was published to see the average number of views per day. Yet a major flaw with this approach is that it doesn't account for the fact that daily views almost certainly change over time.

Another model would be to assume [exponential decay](https://en.wikipedia.org/wiki/Exponential_decay), like what happens with radioactive decay. In this case, a data set might be assumed to have a "half-life," i.e. a length of time it takes for the average daily number of views to fall by half. In this case, a graph of page views over time might resemble this:

![Half-life graph](/eods/images/Half_Life.gif)

This model isn't too bad. But a major question is, what length of a half-life should we assume? I have no clue. It's also worth noting that with a case like this, using the cumulative total number of views isn't a half-bad option; since the number of daily views declines with time, the growth rate of cumulative views slows with time.

One issue with the exponential decay model for daily views is that the number of views will almost certainly not start at its maximum on day one. Instead, there will likely be an increase in daily views with time, followed by a decrease.

A further complicating factor is that some data sets may have patterns in daily views that don't fit into any of these models. For example, a government budget data set for a given fiscal year might get a spike in views not only after it is released but also during budget season in future years.

Obtaining data portal Google Analytics data from some benevolent government that wants to share it would be very valuable in trying to get a better picture of some of these patterns.

### Visualize the data

It would be nice to visualize some of this data on open data set popularity.

### Optimize the scraper

Improving the speed of the scraper (perhaps using [multiprocessing.Pool](https://docs.python.org/3/library/multiprocessing.html#using-a-pool-of-workers)) would be a huge help. Currently, the scraper may take over a minute just for the first nine pages of a single site. This means that running the scraper for all Socrata portals may take a while. This isn't a huge deal or key priority because there isn't really a need to run the scraper that often, but it would be nice.

### Create non-Socrata scrapers

In the long-term, it would be great to build scrapers to grab this kind of information for open data portals that run on non-Socrata platforms, like [CKAN](http://ckan.org/).
