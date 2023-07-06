# Prometheus TSDB (Part 6): Compaction and Retention

[link](https://ganeshvernekar.com/blog/prometheus-tsdb-compaction-and-retention)

## Compaction

Compaction consists of writing a new block from one or more existing blocks (called the source blocks or parent blocks), and at the end, the source blocks are deleted and the new compacted block is used in place of those source blocks.

But why do we need compaction?

1. As we saw in part 4, any deletions to the data are stored as tombstones in a separate file while the data still stays on disk. So when the tombstones are touching more than some % of the series, we need to remove that data from the disk.
2. With low enough churn, most of the data in the index in adjacent blocks (w.r.t. time) is going to be the same. So by compacting (merging) those adjacent blocks, we can deduplicate a large part of the index and hence save disk space.
3. When a query hits >1 block, we have to merge the result we get from individual blocks and that can be a bit of overhead. By merging adjacent blocks, we prevent this overhead.
4. If there are overlapping blocks (overlapping w.r.t. time), querying them requires deduplication of samples between blocks which is significantly more expensive than just concatenating chunks from different blocks. Merging these overlapping blocks avoid the need for deduplication.

Below are the two steps for single compaction to take place. Every minute we initiate a compaction cycle where we check for step-1 and only proceed to step-2 if step-1 was not empty. The compaction cycle runs these steps in a loop and exits when step-1 is empty.

### Step 1: The "plan”

A "plan" is a list of blocks to be compacted together, picked based on the below conditions in order of priority (highest to lowest). The first condition that is satisfied generates a plan, hence only 1 condition per plan. When none of the conditions meet, the plan is empty.

#### Condition 1: Overlapping blocks

As we saw above, overlapping blocks can make queries slow. Moreover, Prometheus itself does not produce overlapping blocks, it's only possible if you backfill some data into Prometheus. So highest priority goes to removing the overlap and getting the state back to what Prometheus will produce.

The plan can consist >2 blocks. Take this example:

```sh
|---1---|
            |---2---|
      |---3---|
                  |---4---|
```

While there are only 2 blocks per overlap, if you look closely, when we compact one overlap, let say 1 and 3, they together will eventually overlap with 2. So instead of going through multiple cycles to fix all the linked overlaps, the first pass will choose `[1 2 3 4]` as the plan and reduce the number of compactions.

Another example that produces a single plan `[1 2 3]`

```
|-----1-----|
  |--2--|
     |----3----|  
```

Note that overlapping blocks support is not enabled by default in Prometheus, it will error out on startup or runtime if you have overlapping blocks, unless enabled via `--storage.tsdb.allow-overlapping-blocks` flag.

#### Condition 2: Preset time ranges

In this, we pick >1 block to merge to fill some preset time ranges. In Prometheus, by default, time ranges are `[2h 6h 18h 54h 162h 486h]`, i.e. starting at 2h with a multiple of 3.

Let's take an example of `6h` range. We divide the Unix time into buckets as `0-6h, 6h-12h, 12h-18h ...`, and if >1 block falls into any single bucket, that forms a plan and we compact them together to form a block up to 6h long.

We also take care to not compact the newest blocks that do not span the entire bucket together yet. For example, the latest 2 blocks of 2h range won't be compacted together since they are (1) new (2) do not span 6h combined. Since Prometheus produces 2h blocks, when we have >=3 blocks, the blocks falling into the same buckets are compacted together.

Similarly, we check all ranges to see if there is any time bucket that has >1 block falling in it. At the end of the compaction cycle, there will be no time bucket with >1 block for all ranges.

In Prometheus, the maximum size of a block can be either `31d` (i.e. `744h`), or 1/10th of the retention time, whichever is lower.

#### Condition 3: Tombstones covering some % of series

In the end, if any block has tombstones touching >5% of the total series in the block, we pick that for compaction where the data pointed out by tombstones is deleted from the disk (by creating a new block with no samples covered by the tombstones). This produces a plan with only 1 block.

### Step 2: The compaction itself

As we saw in part 4, persistent blocks are immutable. To do any changes, we have to write a new block. Similarly, in compaction, we write an entirely new block, even if it is compaction of a single block. The compaction step only receives the list of blocks to compact together into a single block and is ignorant about the logic used to create this plan.

The compaction logic has been evolving with time with various memory management techniques and faster merging of data. At a higher level, compaction does an N way merge of the series from the source block while iterating through series one by one in a sorted fashion (the order in which they appear in index too).

While the series is deduplicated in the index, when the blocks are not overlapping, the chunks are concatenated together from source blocks. If blocks are overlapping, only the overlapping chunks are uncompressed, samples are deduped (i.e. only keep 1 sample for matching timestamp), and compressed back into >=1 chunk while keeping the max size of chunk to 120 samples.

If there are tombstones in any of the blocks, the chunks of those series are re-written to exclude the time ranges mentioned in the tombstones. The final block won't have any tombstones.

Every compacted block is given a compaction level, which tells the generation of the block, i.e. number of times blocks have been compacted to get this one. It is `max(level of source blocks) + 1` for the new block.

If all samples of a series are deleted, then the series is skipped from the new block entirely. If the block has 0 samples (i.e. empty block), then no block is written to the disk while the source blocks are deleted.

Note that compaction itself does not delete the source blocks, but only marks them as deletable (in their `meta.json`). The loading of new blocks and deletion of source blocks is handled by the TSDB separately after the compaction cycle has ended.

## Head compaction

This is a special kind of compaction where the source is the Head block and the compaction persists part of the Head block into persistent blocks while removing any data pointed by tombstones.

Part 1 has an illustration and explanation of when the Head compaction is done. Head block implements the same interface as that of a persistent block reader, hence we use the same compaction code to also compact the Head block into a persistent block.

The block produced from the Head block has compaction level 1.

## Retention

TSDB allows setting retention policies to limit how much data you store in it. There are 2 of them, time-based and size-based retention. You can either set one of them or both of them. When you set both of them, it is a `OR` between them, i.e. the first one to satisfy will trigger the deletion of relevant data.

### Time based retention

In this, you mention how long should the data span in the TSDB. It is a relative time span calculated w.r.t. the max time of the newest persistent block (and not w.r.t. the Head block). A block is deleted when it goes completely beyond the time retention period and not when part of the block goes beyond the time retention.

For example, if the retention period is `15d`, as soon as the gap between the oldest block's max time and the newest block's max time goes beyond `15d`, the oldest block is deleted.

### Size based retention

In this, you mention the max size of the TSDB on disk. It includes the WAL, checkpoint, m-mapped chunks, and persistent blocks. Although we count all of them to decide any deletion, WAL, checkpoint, and m-mapped chunks are required for the normal operation of TSDB. So even if they together go beyond the size retention, only the blocks are the ones that are deleted. So TSDB may take more than the specified max size if you set it too low.

Size-based retention is stricter compared to time-based retention. As soon as the entire space taken is at least 1 byte more than the max size, the oldest block is deleted.

##  Code reference

[`tsdb/compact.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/compact.go) has the code for the creation of plan and compacting the blocks.

[`storage/merge.go`](https://github.com/prometheus/prometheus/blob/main/storage/merge.go) has the code for concatenating/merging the chunks from different blocks (both for overlapping and non-overlapping chunks).

[`tsdb/db.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/db.go) has the code for initiating the compaction cycle every minute and calling the step-1 & step-2 on blocks and compaction of the Head block. It also has the code for both types of retention.