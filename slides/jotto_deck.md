# Jotto Deck for Trees Lecture (Week 8 Monday)

## The 16 Words

```
DEW  FOX  GEL  INK
JOG  MOB  NAP  NIP
NOR  NUT  OAT  OIL
PUG  SOY  WOO  YAK
```

**Why this set?** Different heuristics produce DIFFERENT decision trees!
- Greedy Minimax: first guess MOB, depth 8
- Information Gain: first guess NIP, depth 7
- Min Average: first guess NAP, depth 6 (same as optimal!)

No anagram pairs in this set.

## Rules

1. One player draws a secret card
2. Other player(s) have the remaining 15 cards visible
3. Guess a word; response is **count of matching letters** (position doesn't matter)
   - FOX vs JOG → 1 (O matches)
   - DEW vs YAK → 0 (no letters in common)
   - NIP vs INK → 2 (I and N match)
4. **Hard mode constraint**: You may only guess words that are **consistent with all previous responses** (i.e., words that could still be the secret)
5. Goal: identify the secret word in fewest guesses

## Deck Design

**Words with O** (tend to overlap — harder to discriminate):
- FOX, JOG, MOB, NOR, OAT, OIL, SOY, WOO

**Probe words** (more distinct letter patterns):
- DEW, GEL, INK, NAP, NIP, NUT, PUG, YAK

## Jotto Score Matrix

```
    DEW FOX GEL INK JOG MOB NAP NIP NOR NUT OAT OIL PUG SOY WOO YAK
DEW  3   0   1   0   0   0   0   0   0   0   0   0   0   0   1   0
FOX  0   3   0   0   1   1   0   0   1   0   1   1   0   1   1   0
GEL  1   0   3   0   1   0   0   0   0   0   0   1   1   0   0   0
INK  0   0   0   3   0   0   1   2   1   1   0   1   0   0   0   1
JOG  0   1   1   0   3   1   0   0   1   0   1   1   1   1   1   0
MOB  0   1   0   0   1   3   0   0   1   0   1   1   0   1   1   0
NAP  0   0   0   1   0   0   3   2   1   1   1   0   1   0   0   1
NIP  0   0   0   2   0   0   2   3   1   1   0   1   1   0   0   0
NOR  0   1   0   1   1   1   1   1   3   1   1   1   0   1   1   0
NUT  0   0   0   1   0   0   1   1   1   3   1   0   1   0   0   0
OAT  0   1   0   0   1   1   1   0   1   1   3   1   0   1   1   1
OIL  0   1   1   1   1   1   0   1   1   0   1   3   0   1   1   0
PUG  0   0   1   0   1   0   1   1   0   1   0   0   3   0   0   0
SOY  0   1   0   0   1   1   0   0   1   0   1   1   0   3   1   1
WOO  1   1   0   0   1   1   0   0   1   0   1   1   0   1   2   0
YAK  0   0   0   1   0   0   1   0   0   0   1   0   0   1   0   3
```

## First Guess Analysis

How many distinct Jotto scores does each word produce against the other 15?

| Word | Score distribution | Distinct outcomes |
|------|-------------------|-------------------|
| DEW  | 0:13, 1:2         | 2 |
| FOX  | 0:8, 1:7          | 2 |
| GEL  | 0:11, 1:4         | 2 |
| INK  | 0:9, 1:5, 2:1     | 3 |
| JOG  | 0:6, 1:9          | 2 |
| MOB  | 0:8, 1:7          | 2 |
| NAP  | 0:8, 1:6, 2:1     | 3 |
| NIP  | 0:9, 1:4, 2:2     | 3 |
| NOR  | 0:4, 1:11         | 2 |
| NUT  | 0:9, 1:6          | 2 |
| OAT  | 0:5, 1:10         | 2 |
| OIL  | 0:5, 1:10         | 2 |
| PUG  | 0:10, 1:5         | 2 |
| SOY  | 0:7, 1:8          | 2 |
| WOO  | 0:7, 1:8          | 2 |
| YAK  | 0:11, 1:4         | 2 |

## Physical Setup

- 17 cards per deck (16 words + 1 rules card or blank)
- 3 decks from a standard 52-card deck
- Write words with sharpie
