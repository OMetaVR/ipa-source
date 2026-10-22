# Meta's Apps

A SideStore / AltStore / LiveContainer source for apps I build myself, by OMetaVR.

**Source URL:** `https://ometavr.github.io/ipa-source/source.json`

- **SideStore:** Sources → `+` → paste the URL, or open `sidestore://source?url=https://ometavr.github.io/ipa-source/source.json`
- **AltStore:** `altstore://source?url=https://ometavr.github.io/ipa-source/source.json`
- **LiveContainer:** add the URL in its sources/repos section

## Apps

| App | Repo |
| --- | --- |
| Distra | [OMetaVR/Distra](https://github.com/OMetaVR/Distra) |
| uYouEnhanced | [OMetaVR/uYouEnhanced](https://github.com/OMetaVR/uYouEnhanced) |
| EeveeSpotify | [OMetaVR/EeveeSpotifyReincarnated](https://github.com/OMetaVR/EeveeSpotifyReincarnated) |
| Feather | [OMetaVR/feather](https://github.com/OMetaVR/feather) |
| iTorrent | [OMetaVR/iTorrent](https://github.com/OMetaVR/iTorrent) |
| Apollo Reborn | [OMetaVR/Apollo-Reborn](https://github.com/OMetaVR/Apollo-Reborn) |
| TwitchAdBlock | [OMetaVR/TwitchAdBlock](https://github.com/OMetaVR/TwitchAdBlock) |
| YTMusicUltimate | [OMetaVR/YTMusicUltimate](https://github.com/OMetaVR/YTMusicUltimate) |
| SCMusicPlus | [OMetaVR/scmusicplus](https://github.com/OMetaVR/scmusicplus) |
| BHTikTok | [OMetaVR/BHTikTok](https://github.com/OMetaVR/BHTikTok) |
| NeoFreeBird | [OMetaVR/NeoFreeBird](https://github.com/OMetaVR/NeoFreeBird) |
| DiOShonored | [OMetaVR/DiOShonored](https://github.com/OMetaVR/DiOShonored) |

Forks are built by the shared [ipa-pipeline](https://github.com/OMetaVR/ipa-pipeline).

## Tweaks

Listed on [mmeta.cloud/repo](https://mmeta.cloud/repo); SideStore and AltStore don't show tweaks.

| Tweak | Repo |
| --- | --- |
| Un-JailedSpeedAds | [OMetaVR/Un-JailedSpeedAds](https://github.com/OMetaVR/Un-JailedSpeedAds) |

Tweaks ship `.deb`s and/or a dylib but no IPA, and are built by the same pipeline.

## How it works

IPAs stay in each project's own GitHub releases; nothing is re-uploaded here.

- `config.json` holds the source details and one entry per app: its repo, the IPA asset name, and the metadata shown in the store.
- `scripts/update_source.py` reads each repo's releases, downloads any IPA it hasn't seen yet, and takes the version, build number, minimum iOS version, size, SHA-256 and privacy strings from the IPA itself. It writes `source.json`.
- The **Update source** workflow runs every hour, whenever `config.json` or the script changes, and on demand (Actions → Update source → Run workflow). It commits `source.json` if anything changed.

## Adding an app

1. Publish a GitHub release with the `.ipa` attached in the app's repo.
2. Add an entry to `apps` in `config.json` (copy the Distra one). `bundleIdentifier` must match the IPA's `CFBundleIdentifier`, and `asset` is the file name on the release, or a glob like `MyApp_*.ipa` for versioned names.
3. Add an icon to `icons/` and point `iconURL` at it.
4. Push. The workflow fills in the versions.

## Adding a tweak

For a tweak that ships a dylib and/or .debs but no IPA:

1. Publish a GitHub release with the files attached.
2. Add an entry to `tweaks` in `config.json` (create the list if it's not there):

   ```json
   "tweaks": [
     {
       "repo": "OMetaVR/MyTweak",
       "asset": "MyTweak.dylib",
       "includePrereleases": false,
       "name": "MyTweak",
       "identifier": "com.ometavr.mytweak",
       "targetApp": { "name": "Instagram", "bundleIdentifier": "com.burbn.instagram" },
       "developerName": "OMetaVR",
       "subtitle": "One line about what it does",
       "localizedDescription": "Longer description.",
       "iconURL": "https://ometavr.github.io/ipa-source/icons/mytweak.png",
       "tintColor": "#E1306C",
       "category": "social",
       "minOSVersion": "15.0"
     }
   ]
   ```

   `asset` is the main file (a name or glob). The version is taken from the file name (`MyTweak_1.2.0.dylib`), or the release tag without a leading `v` if the name has none. `targetApp` and `minOSVersion` are optional.
3. Push. Tweaks are written to `source.json` under `tweaks`, which SideStore and AltStore ignore, so they don't appear there as installable apps. [mmeta.cloud/repo](https://mmeta.cloud/repo) lists them in their own section, with every file from the release (dylib, rootless/rootful/roothide .debs) in the download menu.

To run it locally: `GITHUB_TOKEN=$(gh auth token) python3 scripts/update_source.py`

## Updates

SideStore offers an update when the version or build number in the source is different from the installed app's. Those numbers come from the IPA's `Info.plist`, not the release tag. So a new release has to change `CFBundleShortVersionString` or `CFBundleVersion`, or installed copies won't see it as an update.
