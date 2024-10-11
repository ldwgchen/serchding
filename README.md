# serchding: Fulltext search for linkding

## Usage

Setup:

```sh
TOKEN=1a3451a3451a3451a3451a3451a3451a3451a345
BASE_URL=https://example.com
serchding auth set -t $TOKEN -b $BASE_URL
serchding sync
```

Search:

```sh
# "statistics" OR "significant"
# matches other word forms: significance etc
serchding search statistics significant

# "brain" AND "anatomy"
serchding search brain AND anatomy

# fuzzy matching within one Levenshtein edit
# matches joe, joker, coke etc
serchding search joke~

# 2 edits
# matches jo, joe, josh, etc
serchding search joke~2

# 1 edit with a 4-char exact prefix
# matches state but not tat
serchding search stat~/4

# globbing
# matches state, status, statistics
serchding search stat*
```

For full reference, see [whoosh docs](https://whoosh.readthedocs.io/en/latest/querylang.html).

Dump JSON-formatted bookmarks:

```sh
mkdir bookmarks
serchding dump bookmarks
```

## Limitations

- Fulltext retrieval doesn't work with javascript-dependent web pages.
