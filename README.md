# OMetaVR's IPA source

A SideStore / AltStore / LiveContainer source for apps I build myself.

**Source URL:** `https://ometavr.github.io/ipa-source/source.json`

- **SideStore:** Sources → `+` → paste the URL, or open `sidestore://source?url=https://ometavr.github.io/ipa-source/source.json`
- **AltStore:** `altstore://source?url=https://ometavr.github.io/ipa-source/source.json`
- **LiveContainer:** add the URL in its sources/repos section

## Apps

| App | Repo |
| --- | --- |
| Distra | [OMetaVR/Distra](https://github.com/OMetaVR/Distra) |

## How it works

IPAs stay in each project's own GitHub releases; nothing is re-uploaded here.

- `config.json` holds the source details and one entry per app: its repo, the IPA asset name, and the metadata shown in the store.
- `scripts/update_source.py` reads each repo's releases, downloads any IPA it hasn't seen yet, and takes the version, build number, minimum iOS version, size, SHA-256 and privacy strings from the IPA itself. It writes `source.json`.
- The **Update source** workflow runs every 6 hours, whenever `config.json` or the script changes, and on demand (Actions → Update source → Run workflow). It commits `source.json` if anything changed.

## Adding an app

1. Publish a GitHub release with the `.ipa` attached in the app's repo.
2. Add an entry to `apps` in `config.json` (copy the Distra one). `bundleIdentifier` must match the IPA's `CFBundleIdentifier`, and `asset` must be the exact file name on the release.
3. Add an icon to `icons/` and point `iconURL` at it.
4. Push. The workflow fills in the versions.

To run it locally: `GITHUB_TOKEN=$(gh auth token) python3 scripts/update_source.py`

## Updates

SideStore offers an update when the version or build number in the source is different from the installed app's. Those numbers come from the IPA's `Info.plist`, not the release tag. So a new release has to change `CFBundleShortVersionString` or `CFBundleVersion`, or installed copies won't see it as an update.
