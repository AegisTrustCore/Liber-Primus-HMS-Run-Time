# Repository Governance

## Protected branch

The default branch `main` is protected by the active GitHub ruleset **Protect main**.

- Branch deletion is blocked.
- Non-fast-forward updates and force pushes are blocked.
- Changes must enter through a pull request.
- Review threads must be resolved before merge.
- Stale reviews are dismissed when new commits are pushed.
- The `validate` status check is required with strict branch freshness.
- Squash merge is the only enabled merge method, and merged branches are deleted automatically.
- Required approvals are currently `0` because the repository has one owner and GitHub does not permit authors to approve their own pull requests.
- No bypass actor is configured.

When a second trusted maintainer is active, the approval requirement should be raised to at least one and CODEOWNERS review can be enabled for schemas, workflows, release policy, and published research records.

## Merge policy

1. Work on a descriptive branch.
2. Open a draft pull request early.
3. Keep research claims at their smallest defensible scope.
4. Run automated validation and complete the publication checklist.
5. Resolve every review conversation.
6. Move the pull request out of draft only when its public boundary has been reviewed.
7. Merge through GitHub; do not push directly to `main`.

## Authority

A merged file is not automatically a verified scientific claim. Research records must also satisfy [METHODOLOGY.md](METHODOLOGY.md) and [RELEASE_POLICY.md](RELEASE_POLICY.md). Repository administration, software release approval, research publication approval, and Patreon entitlement changes are distinct decisions.
