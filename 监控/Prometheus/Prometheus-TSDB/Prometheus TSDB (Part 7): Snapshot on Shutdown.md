# Prometheus TSDB (Part 7): Snapshot on Shutdown

[link](https://ganeshvernekar.com/blog/prometheus-tsdb-snapshot-on-shutdown)

In this post we will understand more about a new feature introduced in Prometheus v2.30.0: taking snapshots of in-memory data during the shutdown for faster restarts by entirely skipping the WAL replay.

## About snapshot

Snapshot in TSDB is a read-only static view of in-memory data of TSDB at a given time.

The snapshot contains the following (in order):

1. All the time series and the in-memory chunk of each series present in the Head block. ([Part 3](https://ganeshvernekar.com/blog/prometheus-tsdb-mmapping-head-chunks-from-disk/) recap: except the last chunk, everything else is already on disk and m-mapped).
2. All the tombstones in the Head block.
3. All the exemplars in the Head block.

Taking inspiration from the checkpoints in part 2, we name these snapshots as `chunk_snapshot.X.Y`, where `X` is the last WAL segment number that was seen when taking the snapshot, and `Y` is the byte offset up to which the data was written in the `X` WAL segment.

```sh
data
├── 01EM6Q6A1YPX4G9TEB20J22B2R
|   ├── chunks
|   |   ├── 000001
|   |   └── 000002
|   ├── index
|   ├── meta.json
|   └── tombstones
├── chunk_snapshot.000005.12345
|   ├── 000001
|   └── 000002
├── chunks_head
|   ├── 000001
|   └── 000002
└── wal
   ├── checkpoint.000003
   |   ├── 000000
   |   └── 000001
   ├── 000004
   └── 000005
```

We take this snapshot when shutting down the TSDB after stopping all writes. If the TSDB was stopped abruptly, then no new snapshot is taken and the snapshot from the last graceful shutdown remains.

This feature is disabled by default and can be enabled with `--enable-feature=memory-snapshot-on-shutdown`.

## Snapshot format

Snapshot uses the [generic WAL implementation of Prometheus TSDB](https://ganeshvernekar.com/blog/prometheus-tsdb-wal-and-checkpoint#low-level-details-of-writing-to-and-reading-from-wal) and defines 3 new record formats for the snapshots.

The order of records in the snapshot is always:

1. Series record (>=0): This record is a snapshot of a single series. One record is written per series in an unsorted fashion. It includes the metadata of the series and the in-memory chunk data if it exists.
2. Tombstones record (0-1): After all series are done, we write a tombstone record containing all the tombstones of the Head block. A single record is written into the snapshot containing all the tombstones.
3. Exemplar record (>=0): At the end, we write one or more exemplar records while batching up the exemplars in each record. Exemplars are in the order they were written to the circular buffer.

The format of these records can be found [here](https://github.com/prometheus/prometheus/blob/main/tsdb/docs/format/memory_snapshot.md), we won't be discussing them in this blog post.

## Restoring in-memory state

With `chunk_snapshot.X.Y`, we can ignore the WAL before `Xth` segment's `Y` offset and only replay the WAL after that because the snapshot along with m-mapped chunks represents the replayed state until that point in the WAL.

Hence with snapshots enabled, the replay of data to restore the Head goes as follows:

1. Iterate all the m-mapped chunks as described in [part 3](https://ganeshvernekar.com/blog/prometheus-tsdb-mmapping-head-chunks-from-disk#replaying-on-startup#replaying-on-startup) and build the map.

2. Iterate the series records from the latest `chunk_snapshot.X.Y` one by one. For each series record, re-create the series in the memory with the labels and the in-memory chunk in the record.

   Similar to handling the `Series` record in the WAL, we look for corresponding m-mapped chunks for this series reference and attach it to this series.

3. Read the tombstones record if any from the snapshot and restore it into the memory.

4. Iterate the exemplar records one by one if any and put it back into the circular buffer in the same order.

5. After replaying the m-mapped chunks and the snapshot, we continue the replay of the WAL from `Xth` segment's `Y` byte offset as usual. If there are WAL checkpoints numbered `>=X`, we also replay the last checkpoint before replaying the WAL.

In majority cases (i.e. graceful shutdowns), there will be no WAL to be replayed since the snapshot is taken after stopping writes during the shutdown. There will be WAL/Checkpoint to be replayed if Prometheus happens to abruptly crash/shutdown.

## Faster restarts

When we talk about restarts, it is not only the time taken to replay the data on disk to restore the memory state, but also the time taken to shutdown, because snapshotting now adds some delay to shutdown.

Writing snapshots takes time in the magnitude of seconds, and is usually under a minute for 1 million series. And replaying the checkpoint also takes time in the magnitude of seconds. While the WAL replay can take multiple minutes for the same number of series.

By skipping the WAL replay entirely during graceful restart, we have seen anywhere between 50-80% reduction in *restart* time.

## Few things to be aware of

- Snapshot will take additional disk space when enabled and does not replace an existing thing.
- Depending on how many series you have and the write speed of your disk, shutdown can take a little time. Therefore, set your [pod termination grace period](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination-forced) (or equivalent) for Prometheus pod accordingly.

## Pre-answering some questions

*Why take snapshots only on shutdown?*

When we look at the number of times a sample is written on the disk (or re-written during compaction), it is only a handful. If we take snapshots at intervals while Prometheus is running, this can increase the number of times a sample is written to disk by a big %, hence causing unnecessary write amplification. So we chose to go with the majority case of a graceful shutdown while a crash would read part of WAL depending on the last snapshot present on the disk.

*Why do we still need WAL?*

If Prometheus happens to crash due to various reasons, we need the WAL for durability since a snapshot cannot be taken. Additionally, [remote-write](https://prometheus.io/docs/practices/remote_write/) depends on the WAL.

## Code reference

The code for taking the snapshot and reading it is present in [`tsdb/head_wal.go`](https://github.com/prometheus/prometheus/blob/main/tsdb/head_wal.go).