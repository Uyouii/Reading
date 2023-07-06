# Prometheus TSDB (Part 2): WAL and Checkpoint

[link](https://ganeshvernekar.com/blog/prometheus-tsdb-wal-and-checkpoint/)

## Introduction

In the [Part 1](https://ganeshvernekar.com/blog/prometheus-tsdb-the-head-block/) of the TSDB blog series I mentioned that we write the incoming [samples](https://prometheus.io/docs/concepts/data_model/#samples) into [Write-Ahead-Log (WAL)](https://en.wikipedia.org/wiki/Write-ahead_logging) first for durability and that when this WAL is truncated, a checkpoint is created. In this blog post, we will briefly discuss the basics of WAL and then dive into how WAL and checkpoints are designed in Prometheus' TSDB.

## WAL Basics

WAL is a *sequential* log of events that occur in a database. Before writing/modifying/deleting the data in the database, the event is first recorded (appended) into the WAL and then the necessary operations are performed in the database.

For whatever reason if the machine or the program decides to crash, you have the events recorded in this WAL which you can replay back in the same order to restore the data. This is particularly useful for in-memory databases where if the database crashes, the entire data in the memory is lost if not for WAL.

This is widely used in relational databases to provide [durability](https://en.wikipedia.org/wiki/Durability_(database_systems)) (D from [ACID](https://en.wikipedia.org/wiki/ACID)) for the database. Similarly, Prometheus has a WAL to provide durability for its Head block. Prometheus also uses WAL for graceful restarts to restore the in-memory state.

In the context of Prometheus, WAL is only used to record the events and restore the in-memory state when starting up. It does not involve in any other way in read or write operations.

## Writing to WAL in Prometheus TSDB

### Types of records

The write request in TSDB consists of label values of the [series](https://prometheus.io/docs/concepts/data_model/) and their corresponding [samples](https://prometheus.io/docs/concepts/data_model/#samples). This gives us two types of records, `Series` and `Samples`.

The `Series` record consists of the label values of all the series in the write request. The creation of series yields a unique reference which can be used to look up the series. Hence the `Samples` record contains the reference of the corresponding series and list of samples that belongs to that series in the write request.

The last type of record is `Tombstones` used for delete requests. It contains the deleted series reference with time ranges to delete.

The format of these records can be found [here](https://github.com/prometheus/prometheus/blob/master/tsdb/docs/format/wal.md)

### WAL Disk Format

The write ahead log operates in segments that are numbered and sequential, e.g. `000000`, `000001`, `000002`, etc., and are limited to 128MB by default. A segment is written to in pages of 32KB. Only the last page of the most recent segment may be partial. A WAL record is an opaque byte slice that gets split up into sub-records should it exceed the remaining space of the current page. Records are never split across segment boundaries. If a single record exceeds the default segment size, a segment with a larger size will be created. The encoding of pages is largely borrowed from [LevelDB's/RocksDB's write ahead log.](https://github.com/facebook/rocksdb/wiki/Write-Ahead-Log-File-Format)

Notable deviations are that the record fragment is encoded as:

```sh
┌───────────┬──────────┬────────────┬──────────────┐
│ type <1b> │ len <2b> │ CRC32 <4b> │ data <bytes> │
└───────────┴──────────┴────────────┴──────────────┘
```

The type flag has the following states:

- `0`: rest of page will be empty
- `1`: a full record encoded in a single fragment
- `2`: first fragment of a record
- `3`: middle fragment of a record
- `4`: final fragment of a record

#### Record encoding

The records written to the write ahead log are encoded as follows:

##### Series records

Series records encode the labels that identifies a series and its unique ID.

```sh
┌────────────────────────────────────────────┐
│ type = 1 <1b>                              │
├────────────────────────────────────────────┤
│ ┌─────────┬──────────────────────────────┐ │
│ │ id <8b> │ n = len(labels) <uvarint>    │ │
│ ├─────────┴────────────┬─────────────────┤ │
│ │ len(str_1) <uvarint> │ str_1 <bytes>   │ │
│ ├──────────────────────┴─────────────────┤ │
│ │  ...                                   │ │
│ ├───────────────────────┬────────────────┤ │
│ │ len(str_2n) <uvarint> │ str_2n <bytes> │ │
│ └───────────────────────┴────────────────┘ │
│                  . . .                     │
└────────────────────────────────────────────┘
```

##### Sample records

Sample records encode samples as a list of triples `(series_id, timestamp, value)`. Series reference and timestamp are encoded as deltas w.r.t the first sample. The first row stores the starting id and the starting timestamp. The first sample record begins at the second row.

```sh
┌──────────────────────────────────────────────────────────────────┐
│ type = 2 <1b>                                                    │
├──────────────────────────────────────────────────────────────────┤
│ ┌────────────────────┬───────────────────────────┐               │
│ │ id <8b>            │ timestamp <8b>            │               │
│ └────────────────────┴───────────────────────────┘               │
│ ┌────────────────────┬───────────────────────────┬─────────────┐ │
│ │ id_delta <uvarint> │ timestamp_delta <uvarint> │ value <8b>  │ │
│ └────────────────────┴───────────────────────────┴─────────────┘ │
│                              . . .                               │
└──────────────────────────────────────────────────────────────────┘
```

##### Tombstone records

Tombstone records encode tombstones as a list of triples `(series_id, min_time, max_time)` and specify an interval for which samples of a series got deleted.

```sh
┌─────────────────────────────────────────────────────┐
│ type = 3 <1b>                                       │
├─────────────────────────────────────────────────────┤
│ ┌─────────┬───────────────────┬───────────────────┐ │
│ │ id <8b> │ min_time <varint> │ max_time <varint> │ │
│ └─────────┴───────────────────┴───────────────────┘ │
│                        . . .                        │
└─────────────────────────────────────────────────────┘
```

### Writing them

The `Samples` record is written for all write requests that contain a sample. The `Series` record is written only once for a series when we see it for the first time (hence "create" it in the Head).

If a write request contains a new series, the `Series` record is always written before the `Samples` record, else during replay the series reference in the `Samples` record won't point to any series if the `Samples` record is placed before `Series`.

The `Series` record is written *after* creation of the series in the Head to also store the reference in the record, while `Samples` record is written *before* adding samples to the Head.

Only one `Series` and `Samples` record is written per write request by grouping all the different time series (and samples of different time series) in the same record. **If the series for all the samples in the request already exist in the Head, only a `Samples` record is written into the WAL.**

When we receive a delete request, we don't immediately delete it from the memory. We store something called "tombstones" which indicates the deleted series and time range of deletion. We write a `Tombstones` record into the WAL before processing the delete request.

### How it looks on disk

The WAL is stored as a sequence of numbered files with **128MiB** each by default. A WAL file here is called a "segment".

```sh
data
└── wal
    ├── 000000
    ├── 000001
    └── 000002
```

The size of a file is bounded to make garbage collection of old files simpler. As you can guess, the sequence number *always* increases.

## WAL truncation and Checkpointing

We need to regularly delete the old WAL segments, else, the disk will eventually fill up and the startup of TSDB will take a lot of time as it has to replay all the events in this WAL (where most of it will be discarded because it’s old). In general, any data that is no longer needed, you want to get rid of it.

### WAL truncation

The WAL truncation is done just *after* the Head block is truncated. The files cannot be deleted at random and the deletion happens for first N files while not creating a gap in the sequence.

Because the write requests can be random, it is not easy or efficient to determine the time range of the samples in a WAL segment without going through all the records. So we delete the first `2/3rd` of the segments.

```
data
└── wal
    ├── 000000
    ├── 000001
    ├── 000002
    ├── 000003
    ├── 000004
    └── 000005
```

In the above example, the files `000000` `000001` `000002` `000003` will be deleted.

There is one catch here: the series records are written only once, so if you blindly delete the WAL segments, you will lose those records and hence can't restore those series on startup. Also, there might be samples in those first `2/3rd` segments which are not truncated from the Head yet, hence you lose them too. This is where checkpoints come into picture.

### Checkpointing

Before truncating the WAL, we create a "checkpoint" from those WAL segments to be deleted. You can consider a checkpoint as a filtered WAL. Consider if the truncation of Head is happening for data before time `T`, taking the above example of WAL layout, the checkpointing operation will go through all the records in `000000` `000001` `000002` `000003` in order and:

1. Drops all the series records for series which are no longer in the Head.
2. Drops all the samples which are before time `T`.
3. Drops all the tombstone records for time ranges before `T`.
4. Retain back remaining series, samples and tombstone records in the same way as you find it in the WAL (in the same order as they appear in the WAL).

The drop operation can also be a re-write operation while dropping the unnecessary items from the record (because a single record can contain more than one series, sample or tombstone).

This way you won't lose the series, samples and tombstones which are still in the Head. The checkpoint is named as `checkpoint.X` where `X` is the last segment number on which the checkpoint was being created (`00003` here; you will know why we do like this in the next section).

After the WAL truncation and checkpointing, the files on disk look something like this (checkpoint looks like yet another WAL):

```sh
data
└── wal
    ├── checkpoint.000003
    |   ├── 000000
    |   └── 000001
    ├── 000004
    └── 000005
```

## Replaying the WAL

We first iterate over the records in order from the last checkpoint (the checkpoint with the biggest number associated with it is the last). For `checkpoint.X`, `X` tells us from which WAL segment we need to continue the replay, and that is `X+1`. So in the above example, after replaying `checkpoint.000003`, we continue the replay from WAL segment `000004`.

You might be thinking why we need to track the segment number in the checkpoint while we anyway delete the WAL segments before it. The thing is, **creation of a checkpoint and deletion of WAL segments are not atomic**. Anything can happen in between and prevent deletion of WAL segments. So we will have to replay the additional `2/3rd` of the WAL segments which would have been deleted, making replay slower.

Talking about individual records, the following actions are taken on them:

1. `Series`: Create the series in the Head with the same reference as mentioned in the record (so that we can match the samples later). There could be multiple series records for the same series which is handled by Prometheus by mapping the references.
2. `Samples`: Add samples from this record to the Head. The reference in the record indicates which series to add to. If no series is found for the reference, the sample is skipped.
3. `Tombstones`: Store those tombstones back in Head by using the reference to identify the series.

## Low level details of writing to and reading from WAL

When the write requests are coming at a high volume, you want to avoid writing to disk randomly to avoid [write amplification](https://en.wikipedia.org/wiki/Write_amplification). Additionally, when you are reading the record, you want to be sure that it is not corrupted (easily possible on abrupt shutdown or faulty disk).

Prometheus has a general implementation of WAL where a record is just a slice of bytes and the caller has to take care of encoding the record. To solve the above two problems, the WAL package does the following:

1. Data is written to the disk one page at a time. One page is 32KiB long. If the record is bigger than 32KiB, it is broken down into smaller pieces with each piece receiving a WAL record header for some bookkeeping to know if the piece is the end of record, or the start, or in the middle (A record receives a WAL record header even if it fits in the page).
2. A checksum of the record is appended at the end to detect any corruption while reading.

The WAL package takes care of seamlessly joining the pieces of records and checks the checksum of the record while iterating through the records for replay.

The WAL records are not heavily compressed by default (or compressed at all). So the WAL package gives an option to compress the records using [Snappy](https://en.wikipedia.org/wiki/Snappy_(compression)) (enabled by default now). This information is stored in the WAL record header, so the compressed and uncompressed records can live together if you plan to enable or disable compression.

## Code reference

The WAL implementation which takes record as slice of bytes and does the low level disk interactions is present in [`tsdb/wal/wal.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/wal/wal.go). This file has the implementation for both writing the byte records and also iterating the records (again as a slice of bytes).

[`tsdb/record/record.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/record/record.go) contains the various records with its encoding and decoding logic.

The checkpointing logic is present in [`tsdb/wal/checkpoint.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/wal/checkpoint.go).

[`tsdb/head.go`](https://github.com/prometheus/prometheus/blob/master/tsdb/head.go) contains the remaining:

1. Creating and encoding the records and calling the WAL write.
2. Calling the checkpointing and WAL truncation.
3. Replaying the WAL records, decoding them and restoring the in-memory state.
