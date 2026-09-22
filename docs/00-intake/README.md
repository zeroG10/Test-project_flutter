# 00-intake — unsorted drop zone

Put anything here when you are not sure where it belongs. An agent triages it:

1. Reads every file (PDF, DOCX, MD, images, zips are unpacked).
2. Moves or copies it into the right `docs/` folder per [docs/README.md](../README.md).
3. Appends a row to `intake-log.md`: date, original file, destination, one-line summary,
   platform (web / mobile / api / shared).
4. Flags anything that looks like a secret and does NOT move it into the repo.

This folder should be empty after triage. It is tracked so the workflow is visible.
