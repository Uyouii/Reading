# Prometheus TSDB (Part 5): Queries

[link](https://ganeshvernekar.com/blog/prometheus-tsdb-queries)

## Types of TSDB Queries

There are 3 types of queries that we run on persistent blocks at the time of writing this blog post.

1. `LabelNames()`: returns all unique label names present in the block.
2. `LabelValues(name)`: returns all the possible label values for the label name `name` as seen in the index.
3. `Select([]matcher)`: returns the samples for the given slice of matchers for the series. We will talk more about these matchers later.

Before we run any query on the block, we create something called a `Querier` on the block which has the min time (`mint`) and max time (`maxt`) for the query to be run. This `mint` and `maxt` is only applicable to the `Select` query while the other two always look at all the values in the block.

We will discuss how we combine results from multiple blocks after looking at all 3 query types.

## LabelNames()

This returns all the unique label names present in the block. To recap, in the series `{a="b", c="d"}`, the label names are `"a"` and `"c"`.

In Part 4 it was mentioned that the `Label Offset Table` was no longer used and is being written only for backward compatibility. Hence both `LabelNames()` and `LabelValues()` use `Postings Offset Table`.

When the index of the block is loaded on startup (or block creation), we store map *`map[labelName][]postingOffset`* of label name to a list of *some* label value's position in the postings offset table (every 32nd at the moment, including the first and the last label value). Storing only some of the value helps in saving memory. This map is created by iterating through all the entries in `Postings Offset Table` when loading the block.

You can now imagine how we can get the label names - just iterate this in-memory map for its keys and there you have the label names. They are sorted before returning. This is useful for query autocomplete suggestions on UI.

## LabelValues(name)

We saw above that we store positions of the first and the last label value in the memory for all label names. Hence for `LabelValues(name)` query, we take the first and last label value position for the given `name` and iterate on the disk between those two positions to get all the label values for that label name. Another recap here: all the label values for a label name are stored together lexicographically in `Postings Offset Table`.

For example if the series in the block were `{a="b1", c="d1"}`, `{a="b2", c="d2"}` and `{a="b3", c="d3"}`, then `LabelValues("a")` would yield `["b1", "b2", "b3"]`, `LabelValues("c")` would yield `["d1", "d2", "d3"]`.

## Select([]matcher)

This query helps in getting the raw TSDB samples from the series described by the given matchers. Before we talk about this query, we need to know what are matchers.

### Matcher

A matcher tells the label name value combination that should match in a series. For example, a matcher `a="b"` says pick all the series which has the label pair `a="b"`.

There are 4 types of matchers

1. Equal `labelName="<value>"`: the label name should exactly match the given value.
2. Not Equal `labelName!="<value>"`: the label name should not exactly match the given value.
3. Regex Equal `labelName=~"<regex>"`: the label value for the label name should satisfy the given regex.
4. Regex Not Equal `labelName!~"<regex>"`: the label value for the label name should not satisfy the given regex.

The `labelName` is the full label name and no regex is allowed there. The regex matchers should match the entire label value and not partially since it is anchored with `^(?:<regex>)$` before using.

Let's say the series are

- s1 = `{job="app1", status="404"}`
- s2 = `{job="app2", status="501"}`
- s3 = `{job="bar1", status="402"}`
- s4 = `{job="bar2", status="501"}`

Here are some matcher examples

- `status="501"` -> (s2, s4)
- `status!="501"` -> (s1, s3)
- `job=~"app.*"` -> (s1, s2)
- `job!~"app.*"` -> (s3, s4)

And when there are >1 matchers, it is an AND operation (i.e. intersection) between all the matchers.

- `job=~"app.*", status="501"` -> (s1, s2) ∩ (s2, s4) -> (s2)
- `job=~"bar.*", status!~"5.."` -> (s3, s4) ∩ (s1, s3) -> (s3)

### Selecting samples

First step is to get the series that the matchers match. We need to get all the series for individual matchers and then finally intersect them.

We saw in part 4 that a "posting" is the series ID which tells us the position of series info in the index. `Postings Offset Table` and `Postings i` together give all the postings for a label-value pair.

#### Getting postings for a single matcher

If it is an Equal matcher, say `a="b"`, we directly get the postings list position for that from the postings offset table. Since we store positions for only some of the label values for a name, we get the two values between which `"b"` falls for label name `a` and iterate the entries between them till we find `"b"`. The `a="b"` entry in the offset table points to a postings list which is all the series ids that contain `a="b"`. If there is no such entry in the offset table, then it's an empty list of postings for the matcher.

For Regex Equal `a=~"<rgx>"`, we have to iterate through all the label values of `a` in the `Postings Offset Table` and check for the matcher condition. We take the postings list of all the matched entries and merge it (union) to get the sorted postings list for this matcher. Taking an example of `job=~"app.*"` from above, we find `job="app1" -> (s1)` and `job="app2" -> (s2)`, and after merging we have `job=~"app.*" -> (s1, s2)`.

With Not Equal `a!="b"` and Regex Not Equal `a!~"<rgx>"`, it is a little different in how we internally use it. We get Equal and Regex Equal for corresponding Not Equal and Regex Not Equal (i.e. `a!="b"` becomes `a="b"`and `a!~"<rgx>"` becomes `a=~"<rgx>"`) since getting everything that does not match can be pretty huge in practice. Because of this, you cannot use a standalone negation matcher in a query, *you need to have at least one Equal or Regex Equal matcher*. We take these postings after conversion and do a set subtraction instead. See below for example.

#### Postings for multiple matchers

Using the above procedure we first get the postings list for all individual matchers. And, similar to what we discussed about matchers before, we intersect them to finally get the postings list (series) that satisfy all the matchers. Note the change in set operation when we have a negation matcher.

```
job=~"bar.*", status!~"5.*"

-> (job=~"bar.*") ∩ (status!~"5.*")

-> (job=~"bar.*") - (status=~"5.*")

-> ((job="bar1") ∪ (job="bar2")) - (status="501")

-> ((s3) ∪ (s4)) - (s2, s4)

-> (s3, s4) - (s2, s4) -> (s3)
```

Similarly, if the matchers were `a="b", c!="d", e=~"f.*", g!~"h.*"`, then the set operations would be `((a="b") ∩ (e=~"f.*")) - (c="d") - (g=~"h.*")`.

#### Getting the samples finally

Once we have all the series ids (postings) for the matchers, we simply go through those one by one and do the following

1. Go to the series in the `Series` table represented by the series id.
2. Pick all the chunk references from that series which overlap with the time range `mint` through `maxt` specified by the querier.
3. Create an iterator to iterate over these chunks from the `chunks` directory for samples between `mint` and `maxt`.

`Select([]matcher)` finally returns sample iterators for all the series that matches the matchers. The series are sorted w.r.t. their label pairs.

## Some Implementation Details

- When getting the postings for a matcher, all the postings for all the matching entries are not got into the memory at the same time. Since the index is memory-mapped from disk, the postings are lazily iterated and merged to get the final list.
- All the sample iterators for all series are not returned upfront by `Select([]matcher)`; there could be 100s of thousands of series as the result. They follow a similar fashion as above. An iterator is returned which iterates over the series one by one giving its sample iterator. And the sample iterator also lazily loads the chunks when asked for.

## Querying multiple blocks

When you have multiple blocks overlapping with the `mint` through `maxt` of the querier, the querier is actually a merge querier which holds queriers for individual blocks. The 3 queries now effectively do the following:

1. `LabelNames()`: get the sorted label names from all blocks and do a N way merge.
2. `LabelValues(name)`: get the label values from all the blocks and do a N way merge.
3. `Select([]matcher)`: get the series iterator from all the blocks using the Select method and do a lazy N way merge again in an iterator fashion. This is feasible since the individual series iterators return series in sorted order w.r.t. label pairs.

## Querying Head block

The Head block stores the entire map of label-value pairs and all the postings list in the memory (an example Go representation `map[labelName]map[labelValue]postingsList`), hence there is no special care required in accessing them. The remaining procedure for performing the 3 queries remains the same with the map and the postings list.

## Code reference

[`tsdb/index/index.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/index/index.go) has the code for performing the `LabelNames()` and `LabelValues(name)` queries on the persistent block and also for getting the merged postings list for given label name and values (not the matcher itself).

[`tsdb/querier.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/querier.go) has the code for performing the `Select([]matcher)` query on the persistent block including filtering the label values for the matchers before asking the index for postings list. [`tsdb/chunks/chunks.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/chunks/chunks.go) has the code for getting the chunks from the disk.

[`tsdb/head.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/head.go) has the code for performing all 3 queries on the Head block.

[`tsdb/db.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/db.go) and [`storage/merge.go`](https://github.com/prometheus/prometheus/blob/master/storage/merge.go) have the code for the merged querier when there are multiple blocks involved in the query.
