# Fernweh

Before doing anything in this repository, read [HANDOVER.md](HANDOVER.md) (how to work here, pitfalls, current state) and [ROADMAP.md](ROADMAP.md) (what was done and what is planned).

The short version:

- Reply to the user in Chinese.
- Commit and push only when the user says so. After a change, stop and ask.
- `fernweh.html` has very long lines: change it with a small Python script that asserts each replacement matches once, then run `node --check` on the script blocks and `python tools/audit.py`.
- Every UI string is `tr('中文','English')`. No helper text, no middots, plain written copy.
- Before a release: `node tools/release.js`. After adding photos: push `E:\fernweh-photos` first, then this repository.
- The user's email is private. Never put it in a request to an outside service.
- Update ROADMAP.md after each piece of work.
