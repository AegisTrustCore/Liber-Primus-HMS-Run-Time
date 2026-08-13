# HMS Expedition Design Standard

Status: **ADOPTED FOR FUTURE EXPEDITIONS**

Every Expedition must teach or test a declared research skill. Atmosphere may invite participation, but the intended route and answer may not depend on guessing what the author was thinking.

## Required puzzle contract

Each challenge manifest declares:

- permanent XPD ID and semantic version;
- puzzle class and difficulty;
- research concept and skill taught;
- instrument used, if any;
- source class and evidence ceiling;
- discoverable beginner entry;
- answer digest and local verifier;
- public hint paths and hashes;
- sealed or published solution state;
- campaign state and public solution policy.

Puzzle classes are synthetic training, known-control reproduction, public structural, public research, and later meta Expeditions. Difficulty uses `DECKHAND`, `PILGRIM`, `NAVIGATOR`, `CARTOGRAPHER`, and `ADMIRAL`; difficulty is not a membership entitlement.

## Discoverable entrance

The first screen or page must answer:

1. What am I trying to produce?
2. Where do I begin?
3. What steps transform the supplied material into an answer?
4. What prior knowledge or tool is required?
5. How do I know when I am correct?
6. Is the campaign actually open, and where would a result go?

A beginner route, example, and worksheet are required when the intended difficulty is Deckhand or Pilgrim.

## Progressive hints

Hints move from orientation to analysis to extraction help. They should remove ambiguity one layer at a time and must not create a different answer.

- Observer asks: “Can I solve it?”
- Pilgrim asks: “Can I learn how to approach it?”
- Navigator asks: “Can I see a deeper analytical route?”
- Cartographer asks: “Can I reproduce and organize it?”
- Admiral asks: “Can I validate the puzzle, tooling, and assumptions?”

Higher tiers receive context, worksheets, or validation responsibilities—not merely the answer.

## Quality gate

An Expedition remains closed unless all applicable checks are true:

- objective defined;
- canonical solution exists and verifies;
- answer sealed before launch;
- beginner entry exists;
- progressive hints are prepared and hashed;
- evidence ceiling and source rights are clear;
- critical-leak and public-boundary scans pass;
- tier material is consistent with the public answer;
- the exact packaged verifier accepts the sealed answer and rejects a deliberate nonmatch;
- public solution timing is defined;
- named human approval is bound to the exact campaign package.

A visible README, draft PR, source verifier, or privately built executable does not make a campaign `OPEN`.

## Evidence boundary

Synthetic training puzzles are not Liber Primus evidence. No Expedition may be built around an unreviewed unknown plaintext candidate, key, endpoint, identity claim, frontier selector, or other critical finding. A safe synthetic mirror may teach the method without exposing the real target.

The full solution and reasoning return to public GitHub at campaign close.
