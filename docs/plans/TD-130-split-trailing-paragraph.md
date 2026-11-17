# TD-130: a board split keeps a paragraph below an item where the v2 reader read it

**Status:** Draft 2 (round 1 applied), 2026-11-17 (session lb-designer). Class: **in-repo** (a decision not to change the split; no
format, code or fixture change; cap 4 rounds, cadence.md §4.8). The record:
[docs/reviews/TD-130.md](../reviews/TD-130.md). In plain words: [docs/synopses/TD-130.md](../synopses/TD-130.md).

**Entry:** [TD-130](../ledger/archive/TD-130.md), the question TD-129's build (#391) left open on purpose.

## The problem

On a v2 board a session sometimes set a paragraph below an item after a blank line, indented, such as
`  **Update 2026-03-02:** moved to next week. Due: 2026-03-09.` The v2 reader never read it as the item's: *the
detail block* is *the lines right under an item indented deeper than its `-`, up to a blank line, a line no deeper,
or another item* (SPEC *The board*). Since TD-129 (#391), `split_board()` carries such a line, in order, to the end
of `README.md`, and `split_board_notes()` names each one, `carried from the board's line <n>, below an item: no item
holds it` (SPEC *The board as a directory*). The update is kept and named, but it no longer sits beside its item.
The question is whether the split should attach it to the item's detail block instead.

## What is already settled

- **The split writes what the v2 reader read.** Every field and the body of an item file are what the v2 reader
  read of its line and detail block, and the split refuses itself when a file reads back otherwise (`_split_check()`,
  the read-back rule in SPEC *The board as a directory*). Nothing is lost: a line no item holds is carried to the
  README and named.
- **The item file's body is free text.** In a v3 item a `Due:` written in the body is not its `**Due:**` field, so
  attaching would not change a field; it would change what the item's text says.
- **The v2 file stays in git history**, and the split runs once per board, in a PR a session reviews.

## The design

### D1. The split does not attach it; the warning stays

`split_board()` keeps carrying a paragraph below an item, after a blank line, to `README.md` as TD-129 built it,
and `split_board_notes()` keeps naming each such line. No code, SPEC text or fixture changes.

The session that runs the split reads the notes in its PR. Where a carried paragraph is an item's update, it moves
it by hand into that item's file (as a `- ` bullet in its body's one part, with no blank line, or as a Log reply,
or into a field the update changed, such as `**Due:**`),
and the PR shows the move; where it is a note about the board, it leaves it in the README.

**Why not attach.** The v2 detail block ends at a blank line, and this package's v2 reader and writers read the paragraph as no
item's (the consumers' tools are not read here; the SPEC definition binds them); attaching it would make the split the one reader that reads it
otherwise, and its read-back check would need an exception for exactly the text it most needs to check. Nor could it attach exactly: an item file's
body is bullets in one part with no blank line inside it (`item_file_problem()`), and the paragraph is neither a
bullet nor joined to the block, so attaching it as written would need a change to the v3 item format. A paragraph with no blank line is already the detail
block's, and the split attaches it (if it is no `- ` bullet, `item_file_problem()` then faults the file, and the
session fixes it in the PR). The shapes
cannot be told apart: an indented paragraph after a blank line is sometimes an item's update and sometimes a note
about the section or the next item, and a rule that guesses (an indent, a bold `Update` label, a date) is format
the package keeps forever for a one-time move. And an attached update that says `Due: 2026-03-09` beside a header
`**Due:** 2026-03-02` reads as two dates, though only the header's is the field, which a session must reconcile by hand anyway; the warning makes it
do so where it can see both.

**Options set aside.** *Attach every indented paragraph after a blank line up to the next item or heading*: reads
a section note as the item's, and moves text the v2 reader never gave the item. *Attach only a paragraph opening
with a bold `Update` label*: a guess at one session's habit, in a vendored format. *Attach and also apply its
fields* (`Due:`, `Context:`): an edit the person never made, chosen by the split.

## The SPEC text

None. SPEC *The board as a directory* already says the split carries such a paragraph to the README and names it
(*a paragraph a session set below an item after a blank line, which the v2 reader never read as that item's, among
them*).

## The fixtures

None new; TD-129's fixtures hold the behaviour.

## Builds

None. On Paul's go this entry archives as decided, TD-129's warning standing.

## Not done

- **No help to move a carried paragraph.** A writer flag that moves a README line into an item's body would be a
  convenience for a one-time move; the PR's hand edit is enough.
