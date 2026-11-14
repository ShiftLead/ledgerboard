# TD-111: a shared check for text a person reads

**Status:** design, round 1 (2026-11-14). Entry: [TD-111](../ledger/TD-111.md). Rounds:
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

### D1. It belongs here, with the consumer's words passed in

The check is pure text: tokens, a sentence's words and its end, a word list. Everything in it is the format's
own or plain English, except three word lists, and those split cleanly:

| Part | Whose | Here |
|---|---|---|
| The code-token grammar (spans, paths, file names, calls, snake/dotted/upper/camel names, ranges, commits, options) and `CODE_EXTS` | plain text | a module constant and function |
| One sentence: the word count, its end, the abbreviation stops | plain English | module |
| Pronoun actors: *I, I'll, I'm, I've, I'd; me, my, myself, you, you'll, you're, your, yourself, we, us, our, nobody, no one* | plain English | `ACTOR_WORDS`, module |
| Role nouns (*session, seat, techlead, grinder, designer, manager, director, reviewer, builder, lead, worker, agent*) and the phrases *the home*, *the host agent* | the consumer's: who acts in its process | **passed in**, `actors=` |
| `COINED_TERMS` (*slice, seam, tripwire*) | the consumer's sessions' coinages | **passed in**, `coined=` |
| A person's names | the board's `People:` | passed in, `people=` (as the source) |
| Internal labels: `TD-n`, `<repo>#TD-n`, `#n`, `[A-Z]{1,2}\d+` | the format's own ids and plain label shapes | module |

So the answer to TD-111's first question is yes: no line of the check needs to know a consumer once the two lists
are arguments. **Options weighed:**
- *Carry ShiftLead's nouns as a module constant* (the source's text). Rejected: it is consumer knowledge, which
  the boundary refuses, and a third consumer (or agent-cadence's own process, whose roles are not ShiftLead's)
  would be refused for *the maintainer builds it*.
- *Declare the actors on the board, as `People:` is* (an `Actors:` preamble line). Rejected: who acts is the
  process's, not each board's, a ledger Ask has no board to read it from, and a new preamble line is a format
  change for what a caller can pass.
- *Leave the check to the consumers.* Rejected: it is what TD-111 exists to end; the grammar is the large,
  drift-prone part, and it is all plain text.

**Where the consumers keep their lists** is theirs. So that the two do not drift, the consumer entries this plan
asks for (D4) say that one list serves both — agent-cadence's, since ShiftLead's sessions run agent-cadence's
helpers — but this package names no list and holds none.

### D2. The contract

Five exports, all pure, none reading a file:

```python
class PersonTextProblem(NamedTuple):
    rule: int        # 1 to 4
    refuse: bool     # True for rules 1 to 3, False for rule 4
    line: str        # what failed and its cure, one line

SENTENCE_WORDS = 25
CODE_EXTS = ("py", "md", "yml", "yaml", "toml", "json", "jsonl", "sh", "js", "ts", "html", "css",
             "txt", "cfg", "ini", "lock", "log", "sql", "csv")
ACTOR_WORDS = ("me", "my", "myself", "you", "you'll", "you're", "your", "yourself", "we", "us", "our",
               "nobody", "no one")            # the I-forms are matched case-sensitively, apart (below)

def code_tokens(text: str) -> list[str]
def sentence_problems(text: str, *, question: bool, max_words: int) -> list[PersonTextProblem]
def person_text_problems(sentence: str | None, answers: Sequence[str] = (), context: str | None = None, *,
                         question: bool, people: Sequence[str] = (), actors: Sequence[str] = (),
                         default: str | None = None) -> list[PersonTextProblem]
def title_problems(title: str, *, coined: Sequence[str] = ()) -> list[PersonTextProblem]
```

- **Departures from the source**, each named here and nowhere silent:
  - *signatures*, each additive: `actors=` on `person_text_problems` and `coined=` on `title_problems` (D1);
    `sentence` may be `None`, which reads no rule 1, so a writer reads rule 4 alone on a detail block's context by
    `person_text_problems(None, context=…, question=False)`; `sentence_problems` returns `PersonTextProblem`s
    (rule 1, refuse true) where the source leaves its type open. `PersonTextProblem` is a tuple, so a caller that
    unpacks `(rule, refuse, line)` as the source says still works.
  - *`sentence_problems` reads the word count and the sentence end only*, never code, as the source says (the card
    reads it as *is one sentence*); `person_text_problems` adds `code_tokens(sentence)` and writes **one** rule-1
    line whose parts name each failure (*this has 41 words and the code token profiles.yml*), so rule 1 gives at
    most one problem.
  - *a phrase in `actors`* (*the host agent*) takes `'s` or `s` on its last word, where the source's phrases, in
    its word list, took neither; *the host agents* passing harms nothing.
  - *`people`*: the source gives no bounds; here a name matches in the actor bounds, case-sensitive, with `'s`, and
    an empty name or one holding a line break, like such an `actors` entry, is a caller's error (`ValueError`).
  - *a coined term* matches with `s` or `es` after it (*slices*, *seams*), where the source says only *its
    plural*.
  - *a form* is defined, where the source used the word without a rule: an answer whose label `is_form()` reads
    as a form (SPEC *The board*, the `Answers:` bullet, v2.8: `Hold: <note>`, `Not right: <what>`, `Other:`) is
    read by its consequence alone; any other answer is read whole, label and consequence.
  - *the lines*: the source gives three examples; the shapes below are this plan's, and where an example disagrees
    with its own rule they follow the rule (rule 4 names the first three tokens, so *grammar.py, one_sentence()
    and 3 more* becomes *grammar.py, one_sentence(), profiles.yml and 2 more* for five tokens).
  - *the actor gaps that depend on role nouns* (*lead-in*, *this leads to*, *US*, *the builds start*) are now the
    caller's `actors`', and the SPEC text names only the gaps of the module's own words.
- **Adopted from the source as written**: the text read (the `’` fold, a link's target and a bare URL dropped,
  the word strip, a code span or fence one token); every code-token pattern and its known false positives and
  gaps; the *One sentence* reading with its stops (*e.g, i.e, vs, etc, cf*) and its end rule; the actor patterns
  (the I-forms case-sensitive; the others case ignored, bounded by `(?<![\w'])…(?![\w']|\.\w)`); `default` read as an answer, named *the default*, skipped when it
  equals an answer's label or whole line; the title's labels; rule 4 as one warning naming the first three tokens
  and the count; a lone `--` is a dash, no option. The source is the definition today; this plan moves it here, and the SPEC text below becomes it.
- **The lines** are pinned word for word by the fixtures, since consumers show them; their shapes are the SPEC
  text's *The lines*. Rule 2's cure names no consumer's noun.
- **Problems come in rule order**, rule 1 before rule 2's answers in their order, the default last among rule 2's.

### D3. The package's writers export it and do not call it

`plan_add`, `plan_new`, `plan_edit` and the module's edits never call it: the source's reason (the gate sweep,
**Put on the board** and migrations write through them, and must not be refused for words a session did not write)
holds here, and a refused rewrite of an old Ask would block an unrelated edit. The package's own command lines
(`python3 -m ledgerboard.board add`, `python3 -m ledgerboard.ledger new|set|edit`) do not call it either:
- **a command line has no actor list of its own**: the check needs the caller's `actors` and `coined`, which the
  package's command line would take as flags on every write that carries a question, a title or answers, and with
  the flags left off it would refuse *a session pins it*, a right answer; the writer that knows who acts in its
  process is the one to run it;
- the package's command line is the reference writer, and SPEC already names a consumer's wrapper as the command
  people run (*The board writer*: *a consumer's wrapper being the command people run*). (Today both consumers
  write through `plan_*` from their own command lines, which this agrees with but does not rest on.)

(Decided with ledgerboard's techlead, 2026-11-14, m-8555d51d71ac.)

What the package does fix is **which writes a writer checks**, as SPEC text (below) a consumer's writer follows:
a `decide` item's question and its detail block's `question` (rules 1, 2 over its answers), an `act` item's head
(rule 1, a statement), their detail blocks' `context` and `recommended` reason (rule 4); an entry's Ask and
Answers on `new`, `edit --section Ask|Answers` and `set --ask` (TD-109's, once built) (rules 1, 2); an entry's
title on `new` and a retitle (`set --title`, v2.8) (rule 3), never on `renumber`, `archive` or `reopen`. Mail
is a consumer's, and SPEC says nothing of it.

**The alternative weighed**: the package's command lines run it too, taking
`--actor NAME` and `--coined WORD` (repeatable), refusing rules 1–3 and warning on rule 4. It would make the
reference writer the rule's example; it costs two flags on several commands that no consumer's people run, and a
check whose actor list is empty by default refuses *a session pins it* when the flags are forgotten.

### D4. The release and the consumers

A minor: the next one after the releases already queued (v3.1 carries TD-109's B1 if it lands first; then v3.2).
It adds eight names to the module (four functions, the class and three constants) and changes no output of any existing function.

The consumers already have entries: agent-cadence's TD-268 (its writers call the check, an event gate on
`person_text_problems` in `ledgerboard/__init__.py`) and ShiftLead's TD-1846 (its `msg` road calls it after its
sync PR). Each needs to know the two departures (D1, D2): the role nouns, the two phrases and the coined terms are
the caller's, passed as `actors=` and `coined=`; ShiftLead's §4.10 text that puts `ACTOR_NOUNS` and `COINED_TERMS`
in this package is ShiftLead's to amend, and so is TD-1846's Fix step 1, which bumps its pin to a commit holding
those two names; its call passes `actors=` or refuses *a session pins it*. On Paul's go the designer sends both question seats one note each (`ao td
add`, drafting a line on each consumer's own entry); on the build's merge, the builder tells agent-cadence's
techlead which release carries it (TD-111's Done when).

## The SPEC text

### A new section, *Text a person reads (v3.N)*, between *The ledger writer* and *Versions*

> ## Text a person reads (v3.N)
>
> Text that waits on a person — a board item's question and its answers, an entry's Ask and Answers, a title — is
> held to four rules by one check, which a writer runs before it writes (`person_text_problems()`,
> `title_problems()`), all in `ledgerboard/__init__.py`. The module only reads the text it is given: who may act in a consumer's process
> (`actors`), its coined words (`coined`) and the board's people (`people`) are the caller's. Each function
> returns a list of `PersonTextProblem(rule, refuse, line)`, empty when the text passes, in rule order; `refuse`
> is true for rules 1 to 3 and false for rule 4; `line` is one line saying what failed and its cure.
>
> 1. **One plain sentence**: at most `SENTENCE_WORDS` (25) words, no sentence end inside it, ending in `?` when it
>    is a question (`sentence_problems(text, question=, max_words=)`, which reads these and nothing else); and no
>    code token (`code_tokens()`). `person_text_problems` reads both and gives at most one rule-1 problem, naming
>    each failure; with `sentence` `None` it reads no rule 1.
> 2. **Every answer says who acts**: each answer, and `default`, names an actor — an I-form (*I, I'll, I'm, I've,
>    I'd*, case-sensitive), a word of `ACTOR_WORDS`, a name in `people`, or an entry of `actors`.
> 3. **A title is plain words** (`title_problems(title, coined=)`): no code token and no internal label — a
>    word matching `[A-Z]{1,2}\d+`, `(?:[\w-]+#)?TD-\d+` or `#\d+`, or a word of `coined` (case ignored, its plural
>    with it).
> 4. **The context is plain words**: its code tokens are named in one warning; never refused, never capped.
>
> **The text read.** Before any test, `’` becomes `'`, and a markdown link's target (`](…)`) and a bare URL
> (`https?://\S+`) are dropped. The text is then read as whitespace-separated words; an inline code span
> (`` `…` ``) or a fenced block is one word whatever it holds. A word is stripped of leading `( [ { " ' * _` and
> trailing `. , ; : ! ? ) ] } " ' * _` before the word patterns below. Every pattern is case-sensitive unless it
> says otherwise.
>
> **A code token** (`code_tokens(text)`: the tokens in the order found, each once): an inline code span or a
> fenced block; a *path*, a word that opens `/`, `~/`, `./` or `../`, or splits on `/` into three parts or more of
> which one holds a letter, or into two whose last is a file name, or holds a `\` between two word characters; a
> *file name*, a word matching `[\w.-]*\w\.(<ext>)` whole, case ignored, `<ext>` one of `CODE_EXTS`; a *call*,
> `[A-Za-z_][\w.]*\(` anywhere in the text, but `(s)` and `(es)`; a *snake_case name*, a word matching
> `[a-z][a-z0-9]*(_[a-z0-9]+)+`; a *dotted name*, a word matching `[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*){2,}`, case
> ignored; an *upper-case name*, `[A-Z][A-Z0-9]*(_[A-Z0-9]+)+`; a *camelCase name*, `[a-z]+[A-Z]\w*`; a *range*,
> a word holding `..` between two word characters; a *commit*, a word of 7 to 40 characters of `[0-9a-f]` holding
> both a digit and a letter; and an *option*, a word opening `--` and a letter (a `--` standing alone is a dash). An id (`TD-1845`, `#3878`, `F12`)
> and a version (`v2.7.1`, whose parts open with digits) are no code token. Known false positives: *yes/no/maybe*, *Node.js*,
> *docs.github.com*, *iPhone*, *macOS*, a word written with `_` on purpose. Known gap: a command written as words
> (*git rebase*) is none.
>
> **One sentence** (rule 1): the text, read as above, has at most `max_words` words and no sentence end before its
> last word — a `.`, `?` or `!` followed by a space, but a stop ending *e.g*, *i.e*, *vs*, *etc* or *cf* (case
> ignored). Its end is read after trailing `) ] " ' *` are dropped: a question ends in `?`; a statement ends in
> `.`, `?`, `!` or nothing. Known false positive: another abbreviation or an id followed by a stop and a space
> (*U.S. law*, *TD-909. Which*), whose line says *write it without the stop*.
>
> **An actor** (rule 2): a match of `(?<![\w'])(I|I'll|I'm|I've|I'd)(?![\w'])`; or, case ignored, of
> `(?<![\w'])(<w>)(?![\w']|\.\w)` for a word `<w>` of `ACTOR_WORDS` (*me, my, myself, you, you'll, you're, your,
> yourself, we, us, our, nobody, no one*); or, case ignored, of an entry of `actors`, a word or a phrase, its last
> word optionally followed by `'s` or `s`, in the same bounds; or of a name in `people`, case-sensitive, optionally
> followed by `'s`, in the same bounds. An entry of `actors` or `people` that is empty or holds a line break is a
> caller's error (`ValueError`). Each answer is read after its `(default)` mark is dropped: whole, label and
> consequence, but an answer whose label is a form (`is_form()`, *The board*: `Hold: <note>`, `Not right: <what>`)
> by its consequence alone, so a form names its actor there. `default` is read as an
> answer is, named *the default* in its line, and skipped when it equals an answer's label or whole line. Known
> gaps: the check sees words, not meaning (*you will not hear of it again* passes), and a word holding an actor
> before a `-` (*agent-cadence*) counts. The gaps of a caller's `actors` are the caller's (a noun *lead* matches
> *lead-in*).
>
> **A title** (rule 3): refused for a code token or an internal label; a label that is a shape (`P0`, `Q3`) is a
> known false positive, whose line says *spell it out*.
>
> **The lines**, one per problem, in rule order (rule 2's answers in their order, the default last):
> - rule 1: `rule 1: the question is one plain sentence of at most <n> words ending in ?: <parts>` for a question,
>   `rule 1: the sentence is one plain sentence of at most <n> words: <parts>` for a statement, `<parts>` the
>   failures in this order, joined with *and*: `this has <m> words`; `this has a sentence end inside it (write it
>   without the stop)`; `this does not end in ?`; `the code token <t>`, or `the code tokens <list>`;
> - rule 2: `rule 2: answer <i> names nobody who acts — say who: I'll…, you…`, then `, a <a>…` when `actors` is not
>   empty (`<a>` its first entry); `the default` in place of `answer <i>`;
> - rule 3: `rule 3: a title is plain words: <list> belong in the body`, the labels and tokens in the order found;
>   a shape label (`[A-Z]{1,2}\d+`) also gives `; <label> may be a label: spell it out` after it;
> - rule 4: `rule 4: the person reads the context in plain words: <list> go behind the link`.
>
> A `<list>` names up to three items: `a`, `a and b`, `a, b and c`, and from four `a, b, c and <k> more` (*grammar.py,
> one_sentence(), profiles.yml and 2 more*). `<i>` counts from 1.
>
> **Which writes a writer checks.** The rules reach text a writer writes for a person, never the writers' `plan_*`
> functions or the module's edits (`item_file()`, `edit_entry()`), which sweeps and migrations also call, and never a file already
> written. A writer runs `person_text_problems()` on a `decide` item's question (its bold head, else its first
> sentence; and its detail block's `question`), with its answers, `question` true; on an `act` item's head, a
> statement; on an entry's Ask, `question` true, with its Answers, when `new`, `edit --section Ask|Answers` or
> `set --ask` (v3.1, TD-109) writes either; and rule 4 alone (`sentence` `None`) on a detail block's
> `context` and `recommended`. It runs
> `title_problems()` on a title `new` or `set --title` writes, never on `renumber`, `archive` or `reopen`. It refuses
> the write on any problem whose `refuse` is true, naming every problem, and writes with rule 4's line shown.
> This package's own command lines do not run it (the writer a person runs is a consumer's).

### In *Versions*, a paragraph for the release

> **v3.N adds the check of text a person reads** (*Text a person reads*): `person_text_problems()`,
> `title_problems()`, `sentence_problems()`, `code_tokens()`, `PersonTextProblem`, `SENTENCE_WORDS`,
> `CODE_EXTS` and `ACTOR_WORDS`. It reads every file v3.0 wrote as v3.0 did, and no existing function's output
> changes; no writer of this package calls the check.

## The fixtures

A new kind, `fixtures/person_text/cases.json` → `expected.json`, each case a call and its problems as
`[rule, refuse, line]` lists (or `{"error": "ValueError"}`):
- **code_tokens**: one case per token kind, and each known false positive (*yes/no/maybe*, *Node.js*,
  *docs.github.com*, *iPhone*, *macOS*) and gap (*git rebase*), an id (*TD-1845*, *#3878*, *F12*) as none, a
  version *v2.7.1* as none, `(s)` and `(es)` as no call, a lone `--`, a commit of 6 and 7 characters, a link's
  target dropped, a fence holding spaces as one token, order and once each.
- **sentence_problems**: 25 and 26 words; a code span as one word, and a code token giving no problem here; a stop inside (*. Which*), each of the five
  abbreviations; a question without `?`; a statement ending in nothing, `!`; trailing `) ] " ' *` before the end;
  `’` folded.
- **person_text_problems**: rule 2 for an I-form, *is* and *i.e.* as no actor, each `ACTOR_WORDS` entry, *you'll*;
  `actors` with a noun, its plural and `'s`, a phrase (*the host agent*), *agent-cadence* (passes, a known gap),
  `actors` empty refusing *a session pins it*; `people` case-sensitive; a form (`Hold: <note> — a session revises
  it` passes, `Hold: <note>` alone and `Not right: <what>` alone refused, `Not right: wrong repo` read whole); `(default)` dropped; `default` equal to a label skipped, unequal and
  actorless named *the default*; rule 4 with one, two, three, four and five tokens; rule 1 as a statement, and with every part failing at once (the
  parts' order); `sentence` `None` reading no rule 1; rule order across all four; an empty `actors`
  entry refused.
- **title_problems**: each label shape, *P0* (a false positive, *spell it out*), a code token, `coined` with
  case and plural, an id written in words passing.

Unit tests in `tests/test_person_text.py` check that the module carries the eight names (the five exports and three constants), and that no `plan_*` calls them.

## Builds

One build, **B1**: the module's functions, constants and `PersonTextProblem`, in `ledgerboard/__init__.py` (where
agent-cadence's TD-268 event gate reads `person_text_problems`); the SPEC section and the
*Versions* paragraph; the fixture kind, its runner function in
`fixtures/run.py`, its cases; and the unit tests, in one PR. On its merge the builder tells agent-cadence's
techlead which release carries it (D4). B1 is `Blocked by: TD-112` (TD-109's build): the SPEC text names
`set --ask`, which TD-112 adds.

## Not done

- **No call from the package's writers** (D3).
- **No vocabulary in the package** beyond plain English pronouns (D1).
- **No check of what is already written**: a board or ledger is never swept for these rules.
- **No mail rules**: the source's rules 5 (pass-ups) and 6 (**Not clear**) are ShiftLead's.
