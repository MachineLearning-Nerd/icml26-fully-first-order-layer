# Evaluator-blind red-team record

## Round 1

The reviewer began only at `README.md`, followed the current-verification link,
then opened the six claim pages and their linked contracts, code, raw data,
checker, and control output. The reviewer was not given repository knowledge.

Files opened included `README.md`, `pages/current/page.md`,
`pages/claims/claim_1/page.md` through `claim_6/page.md`,
`pages/release/page.md`, all linked claim contracts/source audits, the six
aggregate JSON files, Claim 6 per-seed raw files, checker/control output, and
the linked checker sources.

Issue found: the release page initially linked a report path not present in the
Space candidate. It was inaccessible from the artifact and therefore treated
as missing. The page was fixed to keep its complete forecast and risks inline.

## Round 2 after fix

The same canonical traversal was repeated from `README.md`. Every claim page,
exact contract, numerical audit, executable checker, raw link, control,
limitation, Git SHA, seed scope, CPU allocation, and runtime was locatable.
No repository-only fact was used. `release/traversal.json` records the
machine-checked file list. Result: **PASS**, with no missing visibility-matrix
cell.

## Round 3 after independent replication

The reviewer restarted at `README.md` after run `d9c3e026` contradicted the
apparent Claim 6 falsification. The prior default page still presented only
the favorable clean run, so Claim 6 was treated as unsupported. The candidate
was corrected to put `BLOCKED` in navigation, show both complete confidence
intervals inline, link all ten rerun method/seed files, expose the independent
replication checker and its exit-2 missing-run control, and document all four
verification/falsification routes.

The reviewer then repeated the canonical traversal without repository
knowledge. Claims 1–5 retained their current contracts, code, data, checkers,
controls, and limitations. Claim 6's conflicting evidence and reason for
blocking were directly locatable. Result: **PASS**. No favorable Claim 6
verdict is forecast.
