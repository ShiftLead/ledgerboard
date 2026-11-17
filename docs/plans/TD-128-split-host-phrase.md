# TD-128: a board split names a host written as a phrase

**Status:** Draft 1, 2026-11-17 (session lb-designer). Class: **in-repo** (one function's warning text and its
SPEC sentence; no file format, reader or consumer changes; cap 4 rounds, cadence.md §4.8). The record:
[docs/reviews/TD-128.md](../reviews/TD-128.md). In plain words: [docs/synopses/TD-128.md](../synopses/TD-128.md).

**Entry:** [TD-128](../ledger/TD-128.md), filed from the v3 moves of 2026-11-16 and handed to design by the grinder
(2026-11-17), whose probe showed the entry's Fix would change the item file's grammar.

## The problem

A v2 board line's head names its session and the machine it ran on: `(session `b8a7317c` on <host>)`, the host
`hostname -s`, one word (SPEC *Appendix: grammar*, `head-name ::= [^#x20#x9`,;()]+`). Hand-written heads sometimes
name the machine as a phrase: `(session b8a7317c on Pat's laptop, main)`. The v2 reader (`item_head()`,
`HEAD_HOST_RE`) reads the host's first word, `Pat's`, as it always has, and `split_board()` writes
`**Session:** b8a7317c on Pat's`. `split_board_notes()` then names what the head held past its session and host as
`head text not carried: laptop, main`.

The cut is the format's rule, so nothing is misread. The harm is the warning: it reads as ordinary head text (a
branch, a PR) dropped, when the first part of it was the rest of the host. The session that runs the split, and
the person reading its PR, cannot see that the Session's host is now a fragment (`Pat's`).

## What is already settled

- **The host is one word.** SPEC's v2 head grammar and the v3 item file's (`session-field ::= "**Session:** "
  head-name ( " on " head-name )?`) both make the host a `head-name`, with no space. `item_file_problem()` flags a
  Session whose host holds a space; the item reader and every host match (`HEAD_HOST_RE`, `item_head()`) read one
  word.
- **The split checks itself.** `_split_check()` compares each v2 line's record (its host by `HEAD_HOST_RE`) with the
  file's; a file host that differs refuses the split (the grinder's probe: `pats` against `pats laptop`).
- **Head text past the session and host is not carried.** SPEC *The board as a directory*, the item's heading: *a
  head's text after its session and host, which no v2 reader reads, is not carried, and `split_board_notes()`
  names it*; and the notes' list names it `head text not carried: <text>` at the item's `Session` line. The v2
  file stays in git history.

## The design

### D1. The host stays one word; the split names a cut host as one

The format is not changed. The Session's host stays the v2 reader's first word, and the split's check is unchanged.
What changes is the note: where the head's text right after the host continues it, the note says the host was
kept to its first word, apart from any other head text.

`_head_extra()` reads the head group as today: the session (`SPLIT_SESSION_RE`) and the host (`HEAD_HOST_RE`) found,
the rest left. That rest is cut in two:

- **The host's run-on**: what follows the host's match directly, one closing backtick dropped, up to the first `,`
  or `;` (or the group's end), whitespace collapsed and trimmed. It is non-empty only when the host was followed by
  a space and more words before any separator (`on Pat's laptop, main` → `laptop`; `on `pats` laptop` → `laptop`).
- **The rest**: the group less the session, less the host's match with its one closing backtick, and less the
  run-on, then collapsed and trimmed of `,`, `;` and spaces, as today's whole extra is. Text before the host stays
  in it (`session s-7 branch z on host-c, pr 2` → `branch z , pr 2`, collapsed; no run-on).

`split_board_notes()` then gives, for an item whose head has a host and a non-empty run-on, the note `host kept to
its first word; not carried: <run-on>` at its `Session` line, and, where the rest is non-empty, `head text not
carried: <rest>` after it at the same line. An item with no run-on gets today's one note, unchanged but for a backticked host: today's host match takes the
opening backtick alone, so `` on `host-a` `` leaves a stray `` ` `` that today's note names (`` head text not carried:
` ``); with the closing backtick dropped, that host gives no note, and `` on `host-a`, x `` gives `x`. A head with no
host (`session s-1 foo, bar`) is read as today: its text past the session is the rest, and no host note is given.

The note says *kept to its first word* and *not carried*, never *the host was*: the reader cannot tell a host
phrase (`on Pat's laptop`) from a host followed by other words with no comma (`on host-a branch x`), and the note is
true for both. The session that runs the split decides; where the phrase named a machine, it may rewrite the
item's Session to that machine's `hostname -s` by hand in the split PR, which the format allows.

**Options set aside.** *A Session host that may hold spaces* (the entry's Fix): a grammar change to the item file
in every consumer's reader, for a one-time migration; the host names a machine (`hostname -s`), which a phrase
does not, so nothing could match it; and `_split_check()` would refuse it unless the v2 host reader changed too,
which would read every existing v2 line differently. *The phrase carried into the item file elsewhere* (a body
line, a Log line): the body is the item's detail block and the Log its replies, and neither held this text on
the v2 line; writing it there adds words the item never said, in a place a reader acts on. The v2 file in git
history keeps the line whole. *Today's note, unchanged*: true, but it hides that the Session's host is a fragment.

## The SPEC text

**In *The board as a directory (v3.0)*, the notes' list** (today: *then each item whose v2 line's head group held
more than its session and host, at its `Session` line (with none, its heading), `why` `head text not carried:
<text>`: the group's text less the session and the host, which no file holds.*) becomes:

> then each item whose v2 line's head group held more than its session and host, at its `Session` line (with
> none, its heading): where the host's match is followed, after one closing backtick, by a space and words before
> the group's first `,` or `;` (its end, with none), `why` `host kept to its first word; not carried: <run-on>`,
> those words collapsed (v3.N); then, where text remains after that separator, `why` `head text not carried:
> <text>`: the group's text less the session, the host's match with its closing backtick, and its run-on,
> which no file holds; text before the host stays in it.

**In the item's heading paragraph**, the parenthetical *(a head's text after its session and host, which no v2
reader reads, is not carried, and `split_board_notes()` names it)* becomes *(a head's text after its session and
host, which no v2 reader reads, is not carried, and `split_board_notes()` names it, and a host's run-on as `host kept to its first word`)*.

## The fixtures

`fixtures/board_split/host_phrase/` (`board.md`, `expected.json` with `files` and `notes`, as `head_extra/`), every
name invented: an open line `(session s-3 on Pat's laptop, main)` (Session `s-3 on Pat's`; notes `host kept to its
first word; not carried: laptop` then `head text not carried: main`, both at its Session line); a closed line
`(session s-4 on pats work laptop)` (one note, `not carried: work laptop`); a line `(session s-5 on `pats` laptop;
pr 9)` (backticked host, its closing backtick dropped: `laptop`, then `pr 9`); a line `(session s-6, branch y)` with no host (today's one
note, `branch y`); a line `(session s-7 branch z on host-c, pr 2)` with text before the host (no run-on; `head text
not carried: branch z , pr 2`, collapsed as today); and a line `` (session s-8 on `host-d`) `` (no note, the closing
backtick dropped). `head_extra/` and `fixtures/board/split_notes.json` keep their expected notes unchanged: each of
their hosts is followed by a `,`.

## Builds

One build, **B1**: `_head_extra()` returning the run-on and the rest, `split_board_notes()`'s two notes, the SPEC
text above, the fixture, in one PR; the next untagged minor release when it merges (v3.N). No consumer change:
`board.py split` prints the notes as given, and agent-cadence's and ShiftLead's vendored copies take it with the
release.

## Not done

- **No host repair.** The split never guesses a machine name from a phrase; the session that runs it may edit the
  Session by hand.
- **No change to v2 reading.** `HEAD_HOST_RE`, `item_head()` and `_split_check()` read as today. The host is
  `HEAD_HOST_RE`'s match, which takes the word after any ` on ` in the group (`session s-1 based on main branch`
  reads `main` as the host and `branch` as its run-on); that misfire is the v2 reader's, not fixed here, and the
  note's *not carried* stays true of it.
