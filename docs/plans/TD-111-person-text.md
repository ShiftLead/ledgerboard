# TD-111: a shared check for text a person reads

**Status:** design, round 6 (2026-11-14). Entry: [TD-111](../ledger/TD-111.md). Rounds:
[docs/reviews/TD-111.md](../reviews/TD-111.md). In plain words: [docs/synopses/TD-111.md](../synopses/TD-111.md).

The text that waits on a person (a board item's question and answers, an entry's Ask, a title) is written by
several writers in two consumers. ShiftLead's design §4.10 *Text a person reads is checked at its writer*
(TD-1845, merged in ShiftLead/shiftlead#3882 on 2026-11-14; called **the source** below) defines six rules and
asks for the check to be this package's, so every writer runs the same code. agent-cadence's TD-268 waits on
that export. This plan settles the four questions TD-111's Fix asks, in its order.

## The problem

Each writer today checks a person's text by its own rules, or not at all, and two copies drift. The source writes
the rules down to the regular expression. What it does not settle is the boundary: as written, the rules carry
ShiftLead's own words (`ACTOR_NOUNS`: *session, seat, techlead, grinder, designer, manager, director* …; the
phrases *the home* and *the host agent*; `COINED_TERMS`: *slice, seam, tripwire*), and AGENTS.md keeps logic that
knows either consumer out of the package.

## What is already settled

- **The boundary** (AGENTS.md; target design §1.1): the module reads only the text passed in; what a caller
  needs from outside the text is passed in, as `pickable()` takes its resolver. Sessions and consumer knowledge
  are never in the package.
- **The rules themselves** are the source's and Paul's (2026-11-14, m-6a8ea75dc422): one plain sentence with no code, answers that say who acts, plain titles, plain context with no
  length cap. This plan adopts them; it decides only where each part lives and its exact contract here.
- **Where the check runs** (the source, *Who refuses and who warns*): in the writers' command paths, never in the
  shared plumbing (`plan_add`, `item_file`, the ledger writers), which the home's gate sweep, the person's **Put
  on the board** and migrations also call. A check runs on a write, never over a board or ledger already written.
- **A minor release** (SPEC *Versions*): new functions that read only their arguments add no field, Log line,
  prefix or item key, and change no file.

## The design

### D1. It belongs here: the grammar is shared, the vocabulary is the caller's

The check is pure text: tokens, a sentence's words and its end, word lists. It splits along one line: what reads
plain English or the format's own ids is the module's, and what names a process's roles, words or labels is the
caller's.

| Part | Whose | Here |
|---|---|---|
| The code-token grammar (spans, paths, file names, calls, snake/dotted/upper/camel names, ranges, commits, options) and `CODE_EXTS` | plain text | module |
| One sentence: the word count, its end, the abbreviation stops | plain English | module |
| Pronoun actors: *I* and its contractions (matched apart, case-sensitive); and in `ACTOR_WORDS` *me, my, myself, you, your, yourself, we, us, our, nobody, no one* and the contractions of *you* and *we* | plain English | `ACTOR_WORDS`, module |
| The format's own ids as labels in a title: `TD-n`, `<repo>#TD-n` (SPEC *The ledger*, `Blocked by`) | the format's | module |
| Role nouns (*session, seat, techlead, grinder, designer, manager, director, reviewer, builder, lead, worker, agent*) and the phrases *the home*, *the host agent* | the process's: who acts in it | **passed in**, `actors=` |
| `COINED_TERMS` (*slice, seam, tripwire*) | the process's sessions' coinages | **passed in**, `coined=` |
| Other label shapes: a build, finding or round id (`[A-Z]{1,2}\d+`: *B4*, *F123*, *R12*), a forge's PR number (`#\d+`) | the process's and the forge's; SPEC names neither | **passed in**, `labels=` (patterns) |
| A person's names | the board's `People:` | passed in, `people=` (as the source) |

So the answer to TD-111's first question is yes: no line of the check knows a consumer once the vocabulary is
arguments. **The grammar is shared and the vocabulary is not**: the grammar is the large, drift-prone part, and it
is plain text; the vocabulary is short, and is the process's. **Options weighed:**
- *Carry ShiftLead's nouns, coined terms and label shapes as module constants* (the source's text). Rejected: they
  are a process's knowledge, which the boundary refuses (`#n` is a forge's, which AGENTS.md names), and a third
  consumer, or a process whose roles differ, would be refused for *the maintainer builds it* or a title naming
  *S3*.
- *Declare them in the repo's files* (an `Actors:` preamble line on the board or the ledger README, as `People:`
  is). Rejected: who acts and what a session coins are the process's, the same across every repo it runs, not each
  repo's; a per-repo line would be copied into every repo and drift there instead.
- *Leave the check to the consumers.* Rejected: it is what TD-111 exists to end.

**Who keeps the one vocabulary** is the consumers' to settle: ShiftLead's `msg` road is not an agent-cadence
helper and cannot import agent-cadence's list as code, so the two need one data source both read (for instance a
file agent-cadence ships and ShiftLead's sync copies, as it copies this package). The consumer notes (D4) name
the drift and ask each to settle it in its entry; this package names no list and holds none.

### D2. The contract

All pure, none reading a file, all in `ledgerboard/__init__.py`:

```python
class PersonTextProblem(NamedTuple):
    rule: int        # 1 to 4
    refuse: bool     # True for rules 1 to 3, False for rule 4
    line: str        # what failed and its cure, one line

SENTENCE_WORDS = 25
CODE_EXTS = ("py", "md", "yml", "yaml", "toml", "json", "jsonl", "sh", "js", "ts", "html", "css",
             "txt", "cfg", "ini", "lock", "log", "sql", "csv")
ACTOR_WORDS = ("me", "my", "myself", "you", "you'll", "you're", "you've", "you'd", "your", "yourself",
               "we", "we'll", "we're", "we've", "we'd", "us", "our", "nobody", "no one")
               # the I-forms are matched case-sensitively, apart (SPEC text)

def code_tokens(text: str) -> list[str]
def sentence_problems(text: str, *, question: bool, max_words: int) -> list[PersonTextProblem]
def person_text_problems(sentence: str | None, answers: Sequence[str] = (), context: str | None = None, *,
                         question: bool, people: Sequence[str] | None = (), actors: Sequence[str] = (),
                         default: str | None = None) -> list[PersonTextProblem]
def title_problems(title: str, *, coined: Sequence[str] = (), labels: Sequence[str] = ()) -> list[PersonTextProblem]
```

**Departures from the source**, each named here and nowhere silent:
- *signatures*, each additive: `actors=` (D1), `coined=` and `labels=` (D1) on `title_problems`; `sentence` may be
  `None`, which reads no rule 1, so a writer reads rule 4 alone on a detail block's context; `sentence_problems`
  returns `PersonTextProblem`s where the source leaves its type open. `PersonTextProblem` is a tuple, so a caller
  that unpacks `(rule, refuse, line)` as the source says still works.
- *an empty sentence* is a rule-1 failure (`it is empty`), alone, its length and end unread; the source did not
  name it.
- *a `<list>` names each distinct item once*, where the source's rule-3 line did not say.
- *the `'s` strip*: a word loses an ending `'s` before every pattern (*foo.py's* is a file name), where the source
  stripped punctuation only.
- *punctuation*: `‘ ’` fold to `'` and `“ ”` to `"`; a span or fence is a stand-in word no word list reads, and
  the end is read from the text's last character, so a `?` after a span ends the sentence; a bare URL stops before
  its trailing punctuation; a `. ? !` followed by `) ] } " ' * _` and a space or line break is a sentence end.
  The source read none of these.
- *`sentence_problems` reads the word count, the sentence end and emptiness only*, never code, as the source says
  (the card reads an empty result as *is one sentence*); `person_text_problems` adds `code_tokens(sentence)` and
  writes **one** rule-1 line whose parts name each failure, so rule 1 gives at most one problem.
- *the text read is ordered and its spans defined*: code spans and fences are found first and stand as one word
  each, then link targets and URLs are dropped (a link's text kept), so a URL inside a span cannot break the span;
  the source did not order them, nor say what a span or fence is. Here a span holds no blank line, a backtick
  with no partner is plain, and a fence is *Ledger entries*' fence with three points that passage leaves open settled
  (an info word on the opener, an unclosed fence, the closing line's shape). A sentence end is a stop
  followed by a space *or a line break* (the source: a space).
- *a word holds a letter or a digit*: a standalone `—`, `-`, `&`, `/` or `~/` is no word, counts toward no limit and
  is no token; the source counted every whitespace-separated piece.
- *every word pattern matches the whole stripped word* (`GitHub`, `PowerPoint` and `PhD` are no camelCase name),
  but a *range* and a *call*, which a word *holds*; the source said *whole* of the file name alone.
- *a token's spelling* is fixed: a span as written, backticks included; a fence as `a code block`; a call as its
  name and `()`; any other as the stripped word.
- *the actor words* add the contractions of *we* and *you* the source missed (*we'll* … *you'd*: the source's
  bounds refused *We'll pin it* while passing *you'll*), and an I-form followed by `.` and a word character is no
  actor (*I.e.*).
- *a phrase in `actors`* takes `'s` or `s` on its last word, where the source's phrases took neither; *the host
  agents* passing harms nothing. Entries of `actors` and `people` match as literal text (escaped).
- *`people`*: here a name matches in the actor bounds, case ignored, with `'s`; an empty entry, or one holding a
  line break, in `actors`, `people`, `coined` or `labels` is a caller's error (`ValueError`), and so is a `coined`
  entry holding whitespace and a `labels` entry that is no regular expression; `people` may be `None`.
- *a file name* takes an ending `:\d+` (*foo.py:42*), which the source let pass.
- *a coined term* matches with `s` or `es` after it, where the source says only *its plural*.
- *a form* is defined: an answer whose label `is_form()` reads as a form (`Hold: <note>`, `Not right: <what>`,
  `Other:`) is read by its consequence alone; the label and consequence are `split_answer()`'s.
- *the writes*: the source's ledger row read the whole Ask as the sentence and no context; here the Ask's first
  paragraph is the sentence and its later paragraphs the context, as mail's first paragraph is (an Ask of one
  paragraph holding three sentences is refused for a sentence end inside; the writer's cure is a blank line after
  the question, which makes the rest context). The detail block's context is read whole for
  a `decide` and an `act` (its `caveats`, `recommended` and `otherwise` text with its `context`), where the source
  named `context` and `recommended`'s reason, and its `act` read its `context` alone. The source's `decide` row
  said the line's `Context:` field, which names a gate, is never context; the SPEC text keeps that. The lead is the
  bold run the text *opens* with, where SPEC's *The bold head* takes the first bold run anywhere: a bold word
  mid-question (*Should I merge **#42**?*) must not become the question. A `decide`
  whose text has no lead: the source read its first sentence, which made rule 1's *end inside* unable to fire;
  here the text the writer gives `item_file()` is read whole. The title rule
  runs on `set --title` (v2.8), the retitle path the source said would come (*any retitle path added later*).
- *`people` compares case-insensitively*, as SPEC's *A person's name* does; the source said nothing.
- *the title's labels*: the module keeps the format's ids (`TD-n`, `<repo>#TD-n`), its `<repo>` wider than the
  source's `[\w-]+` (dots and `/`, as SPEC's repo names have) and on purpose wider than SPEC's repo grammar, since
  a label in a title is refused, never parsed, and a near-miss should be refused too; the source's `[A-Z]{1,2}\d+`
  and `#\d+` are the caller's `labels` (D1), and the shape-label cure *spell it out* goes with them, since a
  pattern the caller passes is the caller's to keep free of *P0*.
- *the lines*: the source gives three examples; the shapes in the SPEC text are this plan's, and where an example
  disagrees with its own rule they follow the rule (rule 4 names the first three tokens).
- *the actor bounds* add `/` and `-` (*us-east-1*, *I/O*, *my-app*, *agent-cadence* name no actor), where the
  source's let a word holding an actor before a `-` count.
- *the actor gaps that depend on role nouns* (*this leads to*, *the builds start*) are the
  caller's `actors`', and the SPEC text names only the module's own gaps.

**Adopted from the source as written**: an id (*TD-1845*, *#3878*, *F12*) is no code token, so it may stand in a
question, and only rule 3 refuses one, in a title; the `’` fold; the word strip but its `'s` (above); every code-token pattern but as above; the
known false positives and gaps of the module's own patterns; the *One sentence* stops (*e.g, i.e, vs, etc, cf*, widened below)
and its end rule for a question; `default` read as an answer,
named *the default*, skipped when it equals an answer's label or whole line; rule 4 as one warning; the writer's refusal of an `act` with no bold opening (*an act line leads with its
task in bold*), a writer's message, not a `PersonTextProblem`.

**The fixtures are the grammar's judge** (round 3's view of the recurring topic): the SPEC prose describes the
token grammar exactly enough to build from, and where prose and module disagree the fixtures decide, as SPEC's
opening says of every format (the fixtures' expected values are written from the SPEC text first; a case where
the module and the prose differ is settled by a SPEC fix named in the PR); a false positive or gap found later is a fixture case and a line in the lists, not
a new design round. The abbreviation stops are widened (*Dr.*, *p.m.*, *Nov.*) and an ellipsis is no end, a
departure: the source's five stops refused the commonest plain text.

**The lines** are pinned word for word by the fixtures, since consumers show them; the SPEC text gives every shape
and one full example of each, so the fixtures are checked against the SPEC, not written from the build.

### D3. The package's writers export it and do not call it

`plan_add`, `plan_new`, `plan_edit` and the module's edits never call it: the source's reason (the gate sweep,
**Put on the board** and migrations write through them, and must not be refused for words a session did not write)
holds here, and a refused rewrite of an old Ask would block an unrelated edit. The package's own command lines
(`python3 -m ledgerboard.board add`, `python3 -m ledgerboard.ledger new|set|edit`) do not call it either, because
**a command line has no vocabulary of its own**: the check needs the caller's `actors`, `coined` and `labels`,
which the command line would take as flags on every write that carries a question, a title or answers, and with
the flags left off it would refuse *a session pins it*, a right answer. The writer that knows who acts in its
process is the one to run it. (Decided with ledgerboard's techlead, 2026-11-14, m-8555d51d71ac.)

What the package does fix is **which writes a writer checks**, as SPEC text a consumer's writer follows, each
definition written out there: the text each write's sentence, answers and context are, and where `people` comes
from. Mail is a consumer's, and SPEC says nothing of it.

**The alternative weighed**: the package's command lines run it too, taking `--actor`, `--coined` and `--label`
(repeatable). It would make the reference writer the rule's example; it costs three flags on several commands, and
refuses right answers whenever they are forgotten.

### D4. The release and the consumers

A minor, the next after v3.0 that is cut once B1 merges. It adds eight names to the module (four functions, the
class and three constants) and changes no output of any existing function. It is not held for TD-109's build
(TD-112): the SPEC text names the Ask writes by what they do, and `set --ask` where a writer has it.

The order is AGENTS.md's: this repo's PR, then the release (Paul's), then agent-cadence's vendor PR, then
ShiftLead's sync PR. Both have entries: agent-cadence's TD-268 (its writers call the check; an event gate on
`person_text_problems` in `ledgerboard/__init__.py`) and ShiftLead's TD-1846 (its `msg` road calls it after its
sync PR). Each needs to know the departures (D1, D2): the role nouns, the two phrases, the coined terms and the
label shapes are the caller's, passed as `actors=`, `coined=` and `labels=`, from one vocabulary the two settle
between them (D1). ShiftLead's §4.10 text that puts `ACTOR_NOUNS` and `COINED_TERMS` in this package is
ShiftLead's to amend, and so is TD-1846's Fix step 1, which bumps its pin to a commit holding those two names;
its call passes `actors=` or refuses *a session pins it*. Each consumer's
Ask template changes too: an Ask is now a question of one sentence ending in `?`, with any more in a later
paragraph, where most Asks written today (*Say Go to file the one build, One more round, or Hold with a note*) are
statements; the consumer notes say so. On Paul's go the designer sends both question seats one
note each (`ao td add`); on the build's merge, the builder tells agent-cadence's techlead which release carries it
(TD-111's Done when).

## The SPEC text

### A new section, *Text a person reads (v3.N)*, between *The ledger writer* and *Versions*

> ## Text a person reads (v3.N)
>
> Text that waits on a person — a board item's question and its answers, an entry's Ask and Answers, a title — is
> held to four rules by one check, which a writer runs before it writes (`person_text_problems()`,
> `title_problems()`). The module reads only the text it is given: who may act in the caller's process (`actors`),
> its coined words (`coined`), its label patterns (`labels`) and the board's people (`people`) are the caller's.
> Each function returns a list of `PersonTextProblem(rule, refuse, line)`, empty when the text passes, in rule
> order; `refuse` is true for rules 1 to 3 and false for rule 4; `line` is one line saying what failed and its
> cure. An empty entry (after trimming, for `actors`), or one holding a line break (`\n` or `\r`), in `actors`, `people`, `coined` or `labels`, a `coined`
> entry holding whitespace, or a `labels` entry that is no regular expression, raises `ValueError`. `people` may
> be `None`, read as no names.
>
> 1. **One plain sentence**: not empty, at most `SENTENCE_WORDS` (25) words, no sentence end inside it, ending in
>    `?` when it is a question (`sentence_problems(text, question=, max_words=)`, which reads these and nothing
>    else); and no code token (`code_tokens()`). `person_text_problems` reads both and gives at most one rule-1
>    problem; with `sentence` `None` it reads no rule 1.
> 2. **Every answer says who acts**: each answer, and `default`, names an actor.
> 3. **A title is plain words** (`title_problems(title, coined=, labels=)`): no code token and no label.
> 4. **The context is plain words**: its code tokens are named in one warning; never refused, never capped.
>
> **The text read.** First, `’` and `‘` become `'`, and `“` and `”` become `"`. Then each fenced block — a fence as *Ledger entries and their edits*
> reads one: an opening line of three or more backticks or tildes, indented at most three spaces, then at most an
> info word holding no whitespace (and, after backticks, no backtick); to a closing line of the same character at
> least as long, indented at most three spaces and holding nothing else; or, with no closing line, to the text's
> end — and each code span outside them — a run of n backticks,
> then text holding no run of exactly n backticks and no blank line, then n backticks — is found and replaced, in
> place, by a stand-in (a backtick with no partner is a plain character). A piece holding a stand-in is one word
> that no pattern, `ACTOR_WORDS`, `actors`, `people`, `coined` or `labels` entry reads, so *`foo`'s* is one word
> and *`a`/`b`* one word; each span or fence in it is a code token, spelled as the span is written or as `a code
> block`. Then, outside them, a markdown link's target (`](…)`, the `]` kept) and a bare
> URL are dropped; a bare URL is `https?://\S*` up to and not including a run of `. , ; : ! ? ) ] } " ' * _`
> that ends its piece, so *see https://x.io/guide?* keeps its `?`. The rest is read as whitespace-separated pieces; each is
> stripped of leading `( [ { " ' * _` and trailing `. , ; : ! ? ) ] } " ' * _`, then of an ending `'s`, and a piece holding no letter or
> digit after the strip (`—`, `-`, `&`, `/`, `~/`) is no word; a letter and a digit are Python's (`str.isalnum()`
> of a character), and a pattern's classes are as written. A pattern below matches the whole stripped word unless
> it says *holds*; each is case-sensitive unless it says otherwise. Rules 1, 2 and 3 read these words, so an actor
> or a label inside a span, a fence, a link's target or a URL is not read.
>
> **A code token** (`code_tokens(text)`: in the order of their place in the text, each distinct token once): a
> code span, spelled as written with its backticks; a fenced block, spelled `a code block`; and a word that is
> one of these, spelled as the stripped word unless it says otherwise —
> - a *path*: opens `/`, `~/`, `./` or `../`; or splits on `/` into three parts or more of which one holds a
>   letter, or into two whose last is a file name; or holds a `\` between two word characters;
> - a *file name*: `[\w.-]*\w\.(<ext>)(:\d+)?`, case ignored, `<ext>` one of `CODE_EXTS` (*foo.py:42* is one);
> - a *call*: a piece that, before the strip, holds `[A-Za-z_][\w.]*\(` whose `(` is not followed by `s)` or
>   `es)`, spelled as the name before the `(` and `()` (`one_sentence(x)` gives `one_sentence()`; `file(s)` is no
>   call);
> - a *snake_case name* `[a-z][a-z0-9]*(_[a-z0-9]+)+`; a *dotted name* `[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*){2,}`,
>   case ignored; an *upper-case name* `[A-Z][A-Z0-9]*(_[A-Z0-9]+)+`; a *camelCase name* `[a-z]+[A-Z]\w*`;
> - a *range*: holds `..` between two word characters;
> - a *commit*: 7 to 40 characters of `[0-9a-f]`, holding both a digit and a letter;
> - an *option*: opens `--` and a letter.
>
> A word that is more than one kind is one token. An id (`TD-1845`, `#3878`, `F12`) and a version (`v2.7.1`,
> whose parts open with digits) are no code token. Known false positives: *yes/no/maybe*, *he/she/they*, *A/B/C*,
> *US/EU/UK*, *and/or/else*, *Mon/Wed/Fri* (paths); *a(n)* (a call); *Node.js* (a file name); *docs.github.com*, *U.S.A*, *a.b.c* (dotted); *iPhone*, *iOS*, *macOS*
> (camelCase); a word written with `_` on purpose. Known gaps: a command written as words (*git rebase*), and a
> name whose `_`s the strip removes (`__init__` reads as *init*); a two-part path with no file name
> (*docs/plans*); a variable (`$HOME`), a short option (`-f`), a bare `{"a":1}` and a file with no extension
> (*Makefile*); a path with a line number and no file name (*src/lib:42*), a file name with more than one line number or a
> range (*foo.py:42:7*, *foo.py:42-50*), a dotfile (*.gitignore*), an extension outside
> `CODE_EXTS` (*Foo.java*), a two-part member (*UserService.getName*), a PascalCase name
> (*NullPointerException*), a host and port (*localhost:8080*), an assignment (*DEBUG=1*), an address
> (*dev@example.com*) and a two-part host (*example.com*, where *www.example.com* is dotted).
>
> **One sentence** (rule 1). The sentence is empty when it holds no word; an empty sentence fails with that
> alone, its length and end unread. It has more than `max_words` words when
> its words, a span or fence counting as one, number more. It has a sentence end inside it when a `.`, `?` or `!`,
> then any of `) ] } " ' * _`, then a space or a line break, stands before its last word, but not a `.` ending a word
> that is, case ignored, an abbreviation — *e.g*, *i.e*, *vs*, *etc*, *cf*, *mr*, *mrs*, *ms*, *dr*, *jr*, *sr*,
> *st*, *no*, *approx*, *est*, *a.m*, *p.m*, or a month's (*jan*, *feb*, *mar*, *apr*, *jun*, *jul*, *aug*, *sep*,
> *sept*, *oct*, *nov*, *dec*) — and not an ellipsis (`...` or `…`) (so *Say (really?) what you think?* has one inside).
> Its end is the read text's last character that is not whitespace or one of `) ] } " ' * _` (*_Is it ok?_*
> ends in `?`): a question's must be
> `?` (*Should I run `make test`?* and *Should I "ship it?"* end in `?`); a statement's end is not read. Known false positive: another abbreviation or an id followed by a stop and a
> space (*U.S. law*, *Ph.D. thesis*, *TD-909. Which*), which the line's part names: *write it without the stop*.
> Known gap: *no* is an abbreviation (*No. 5*), so *Say no. Then what?* passes.
>
> **An actor** (rule 2): a match, over the read words joined by single spaces, in the bounds `(?<![\w'/-])` before and `(?![\w'/-]|\.\w)` after (so *us-east-1*, *I/O* and *my-app*
> name no actor), of an I-form (*I,
> I'll, I'm, I've, I'd*, case-sensitive); of a word of `ACTOR_WORDS` (case ignored); of an entry of `actors`, a
> word or a phrase taken as literal text, trimmed and its whitespace collapsed to single spaces (an entry empty after that is a
> `ValueError`), its last word optionally followed by `'s` or `s` (case ignored); or of a
> name in `people`, literal, optionally followed by `'s` (case ignored, as SPEC compares a person's name, so a person named *Will* makes *it will be built* name an
> actor: a known gap). An answer is read through
> `split_answer()`: its label and its consequence, the ` (default)` mark dropped; an answer whose label is a form
> (`is_form()`: `Hold: <note>`, `Not right: <what>`, `Other:`) is read by its consequence alone, and any other by its label
> and consequence. `default` is read as an answer is, and skipped when its label, after `split_answer()`, equals an
> answer's label, or its text with the mark dropped equals an answer's with the mark dropped. Known gaps: the check sees words, not meaning (*you will not hear of it
> again* passes), *US* (*the US market*) reads as *us*, and *me/you* or *you-or-me* names no
> actor (the bounds); a caller's `actors` bring their own (a noun *lead*
> matches *lead* in *take the lead*).
>
> **A label** (rule 3): a word matching `(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+#TD-\d+|TD-\d+` (the format's
> `<repo>#TD-n` and `TD-n`), a word matching any of `labels` (each compiled
> on its own by Python's `re`, case-sensitive unless the pattern says otherwise, and `fullmatch`ed against the
> stripped word, its `'s` already gone, so *TD-5's* is a label), or a word of `coined` (each entry one word,
> refused with `ValueError` if it holds whitespace), case ignored, with `s` or `es` after it or not.
>
> **The lines**, one per problem, rule 1's first, then rule 2's in the answers' order with the default last, then
> rule 4's (`title_problems` gives rule 3's alone). A `<list>` names each distinct item once, up to three, in the order found: `a`,
> `a and b`, `a, b and c`, and from four `a, b, c and <k> more`. `<i>` counts the answers from 1.
> - rule 1: `rule 1: the question is one plain sentence of at most <n> words ending in ?: <parts>` for a question,
>   `rule 1: the sentence is one plain sentence of at most <n> words: <parts>` for a statement; `<parts>` every
>   failure, in this order, joined with `; `: `it is empty`, `this has <m> words`, `this has a sentence end inside
>   it (write it without the stop)`, `this does not end in ?`, and `the code token <list>` (`the code tokens
>   <list>` for two or more). `sentence_problems` writes the same line without the code part. Example: *rule 1:
>   the question is one plain sentence of at most 25 words ending in ?: this has 26 words; this does not end in ?;
>   the code tokens profiles.yml and one_sentence()*.
> - rule 2: `rule 2: answer <i> names nobody who acts — say who: I'll…, you…`, then `, or <a>…` when `actors` is
>   not empty (`<a>` its first entry as given); `the default` in place of `answer <i>`. Example: *rule 2: answer 1
>   names nobody who acts — say who: I'll…, you…, or session…*.
> - rule 3: `rule 3: a title is plain words: <list> belong in the body`, the code tokens and labels in their
>   order in the title. Example: *rule 3: a title is plain words: TD-078, B4 and profiles.yml belong in the body*.
> - rule 4: `rule 4: the person reads the context in plain words: <list> go behind the link`. Example: *rule 4:
>   the person reads the context in plain words: grammar.py, one_sentence(), profiles.yml and 2 more go behind
>   the link*.
>
> **The fixtures decide** (`fixtures/person_text/`), as everywhere in this text: where this prose and the module
> disagree on a word, the fixtures say which is right, and a false positive or gap found later is a fixture case
> first.
>
> **Which writes a writer checks.** The rules reach text a writer writes for a person, never the writers' `plan_*`
> functions or the module's edits (`item_file()`, `edit_entry()`), which sweeps and migrations also call, and never
> a file already written. A writer refuses the write when any problem's `refuse` is true, naming every problem,
> and writes with rule 4's line shown. `people` is the board's `People:` (`board_people()`) for a board
> item (`None`, a board with no such line, reads as no names), and the caller's for a ledger entry. It runs:
> - **a `decide` item**, two calls. The item's text is the text the writer is given for it (`item_file()`'s
>   `text`, after its whitespace collapse, before any line or file is written). Its **lead** is the text between
>   the `**`s of the `**…**` run the text opens with, when that run holds a non-space character; its **tail** is
>   the text after that run. A text that opens with no such run has no lead and no tail. First,
>   `person_text_problems(<lead, else the whole text>, <its answers>, <context>, question=True, people=, actors=,
>   default=)`, the context being the tail, then the detail block's parts `context`, `caveats` and `recommended`
>   and its `otherwise` text, as the writer is given them (the `recommended` before the writer adds the default's
>   label and ` — `), joined by blank lines in that order; never the item's `Context:` field, which names a gate.
>   A text with no lead is read whole, so a second sentence there is refused and belongs in the detail block; a
>   lead is the whole question, so *\*\*Merge the PR\*\* now?* is refused (its lead has no `?`). Second, the
>   detail block's `question`, `person_text_problems(<question>, question=True, people=, actors=)` with the same
>   `people` and `actors`. The writer lists the first call's problems, then the second's, each line after the
>   name of the text it came from (`item: `, `detail question: `; a rule-4 line after `context: `), so a session
>   sees which to rewrite.
> - **an `act` item**: as a `decide`'s first call with no answers and `question=False`, its lead the sentence. An
>   `act` whose text opens with no lead is refused by the writer, with the line *an act item leads with its task in
>   bold* (a writer's refusal, not a `PersonTextProblem`). Example: *Reply to \*\*Dana\*\* about the budget* has
>   no lead and is refused; *Should I merge \*\*#42\*\*?*, a `decide`, has no lead and is read whole.
> - **a `look`, `watch` or `fyi` item, or one with no kind**: not checked (the source checks a `decide` and an
>   `act` alone).
>
>   A detail block part whose value is a list is read as its first string and its nested bullets' strings, one per
>   line.
> - **an entry's Ask**, on any write of it (`new`, `edit --section Ask`, and `set --ask` where the writer has it):
>   the Ask's text after its `**Ask:**` lead, its first paragraph the sentence (it ends at the first blank line outside a fence; a blank line inside a fence ends
>   no paragraph), `question=True`, and its later
>   paragraphs the context. An Ask carries no answers in this format; a ledger that keeps its own `Answers`
>   (a repo's own field or section) passes them, read as a board's `Answers:` value (`parse_answers_value()`);
> - **an entry's title**, on `new` and `set --title`: `title_problems()`; never on `renumber`, `archive` or
>   `reopen`, which carry a title already written.
> This package's own command lines do not run it: the writer that holds the caller's vocabulary does.

### In *Versions*, a paragraph for the release

> **v3.N adds the check of text a person reads** (*Text a person reads*): `person_text_problems()`,
> `title_problems()`, `sentence_problems()`, `code_tokens()`, `PersonTextProblem`, `SENTENCE_WORDS`,
> `CODE_EXTS` and `ACTOR_WORDS`. It reads every file v3.0 wrote as v3.0 did, and no existing function's output
> changes; no writer of this package calls the check.

## The fixtures

A new kind, `fixtures/person_text/cases.json` → `expected.json`, each case a call and its result: `code_tokens`'
list, or the problems as `[rule, refuse, line]` lists, or `{"error": "ValueError"}`. Each SPEC example of the module's
functions is a case, word for word; the examples of the writer's lead and tail are a consumer's cases, since the
module has no function for that split.
- **code_tokens**: *foo.py:42*, *foo.py:42.* and *src/foo.py:42* as one token each, *foo.py:42:7* and
  *foo.py:42-50* as the gap; one case per kind, with each spelling (a span with its backticks, `a code block`, a call's
  `()`); each known false positive and gap; an id (*TD-1845*, *#3878*, *F12*) and *v2.7.1* as none; `file(s)` and
  `item(es)` as no call, `one_sentence(x)` as `one_sentence()`; a lone `--`, `—`, `/` and `~/` as none; a commit of 6 and 7 characters, *deadbeef* and
  *added* as none; *GitHub*, *PowerPoint*, *PhD* as none (whole-word match); a word of two kinds once; a link's
  target and a bare URL dropped; `` `curl https://x.io/a` `` one span; a double-backtick span holding a backtick;
  an unmatched backtick plain; a fence holding spaces and a blank line as one token, and a line ```` ```x``` is y ```` as a span, no fence; order by place, each once.
- **sentence_problems**: empty and blank; 25 and 26 words, and 25 words with a standalone `—` passing; a code span
  as one word, and a code token giving no problem here; a stop inside (*. Which*), each listed abbreviation and a month's;
  a question without `?`; a statement ending in `.`, `!`, `:` and nothing, each passing; trailing `) ] " ' *`
  before the end, and *_Is it ok?_* passing; `’`, `‘`, `“`, `”` folded (*Should I "ship it?"* in curly quotes passing); *Should I run `make
  test`?* passing; *Should I follow https://x.io/guide?* passing; *(see https://x.io/a). Then merge?* and *Say
  (really?) what you think?* each with an end inside; *Nov. 20*, *Dr. Lee*, *9 p.m. tonight* and *Wait... really?* passing; *Ph.D. thesis*
  refused (the known false positive); *Is `foo`'s output ok?* as four words; an empty question failing with *it is
  empty* alone; its line with two and three parts.
- **person_text_problems**: each I-form, *is*, *i.e.* and *I.e.* as no actor; each `ACTOR_WORDS` entry, *We'll pin
  it* passing; *you* inside a span or a URL not read; `actors` with a noun, its plural and `'s`, a phrase (*the host agent*), an entry holding `+`
  (literal); *agent-cadence*, *us-east-1*, *I/O*, *my-app* naming no actor; *the US market* naming one (a known
  gap); `actors` empty refusing *a session pins it*, with the cure
  line's `, or <a>…` absent and present; `people` case ignored, with `'s`, and *Will* matching *will* (the known gap); a form (`Hold: <note> — a session
  revises it` passes; `Hold: <note>`, `Not right: <what>` and `Other:` alone refused; `Not right: wrong repo` read as
  label); `(default)` dropped; `default` equal to a label (marked or not) skipped, unequal and actorless named
  *the default*; rule 4 with one, two, three, four and five tokens; rule 1 as a statement, and with every part
  failing at once (all named, in order); an Ask's `**Ask:**` lead not counted (a writer's case, by its text); `sentence` `None` reading no rule 1; rule order across rules 1, 2 and 4; an
  empty or multi-line entry in each list refused, an `actors` entry *the  host\tagent* matching *the host agent*, an entry of spaces alone refused, and a `coined` entry holding a space; `people=None` read as no
  names; *Say no. Then what?* passing (the known gap).
- **ACTOR_WORDS**: its exact contents, and the I-forms absent from it.
- **title_problems**: `TD-078`, `TD-5's`, `ledgerboard#TD-12`, `acme/tools#TD-5`, `my.repo#TD-5` and a code token refused; `labels` with `[A-Z]{1,2}\d+`
  refusing *B4* and *P0* (the caller's pattern, the caller's false positive), and `#\d+`; a `labels` entry that is
  no regular expression refused; `coined` with case, `s` and `es`; *S3* passing with no `labels`; *US/EU/UK* refused (a path, the known false positive); *B4 B4 and B4s* listing *B4* once with `labels`; `foo.py's` a file name; a label inside a span
  read only as the span, *Fix `foo` B4 and `x`* naming `` `foo` ``, B4 and `` `x` `` once each, `` `a`/`b` `` two
  tokens; an id written in
  words passing.

Unit tests in `tests/test_person_text.py` check that the module carries the eight names, and scan the source of
`ledgerboard/board.py` and `ledgerboard/ledger.py` for no call of the four functions (D3).

## Builds

One build, **B1**: the module's functions, constants and `PersonTextProblem`, in `ledgerboard/__init__.py` (where
agent-cadence's TD-268 event gate reads `person_text_problems`); the SPEC section and the *Versions* paragraph;
the fixture kind, its runner function in `fixtures/run.py`, its cases; and the unit tests, in one PR. The
fixtures' expected results come from this plan's SPEC text and its examples first, never from the module's output;
a case where the build finds the prose wrong is named in the PR, with the SPEC fix beside it. The release number
in the SPEC heading and *Versions* paragraph is the next unreleased minor when B1 merges (v3.2 if TD-109's
release is v3.1). It is not held for TD-112 (D4). On its merge the builder tells agent-cadence's techlead which release carries it.

## Not done

- **No call from the package's writers** (D3).
- **No vocabulary in the package** beyond plain English pronouns and the format's own ids (D1).
- **No check of what is already written**: a board or ledger is never swept for these rules.
- **No port beyond Python**: the `labels` patterns are Python's `re`, and a letter or a digit is
  `str.isalnum()`'s; a port of the package would carry both.
- **No mail rules**: the source's rules 5 (pass-ups) and 6 (**Not clear**) are ShiftLead's.
