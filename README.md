# Knowledge based management of security threats

## Chapter2

### Prepare

To install & download the datasets:

```
$ ./install.sh
$ cd apps
$ ./prepare.sh
```

### Prepare ATT&CK dataset

Download and prepare the ATT&CK dataset:

```
$ cd apps
$ ./do_attck_download.sh
$ ./do_attck_parseAsText.sh
```

Results are in data/sets.

To make tripes from ATT&CK texts:

```
$ cd apps
$ ./do_attck_svo.sh
```

Results are in data/results/attck_semantics.

### Short texts estimation

Short texts are in extra/reports_short.
To make triples from them:

```
$ cd apps
$ ./do_reports_short_svo.sh
```

Triples of ATT&CK are in extra/attck_svo.
To compare the short text triples with them:

```
$ cd apps
$ ./do_semantics_attck_reports_short.sh
```

Results are in data/results/semantics_compare_shorts.

