#!/usr/bin/env python3
"""Build source.json from config.json and each app's GitHub releases.

For every app in config.json, the script looks at the repo's releases, takes the
IPA asset named in "asset", and reads the version, build number, minimum iOS
version and privacy strings straight from the IPA's Info.plist. Versions already
in source.json are reused, so an IPA is only downloaded once.

Set GITHUB_TOKEN to avoid API rate limits. Standard library only.
"""

import hashlib
import json
import os
import plistlib
import re
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.json"
SOURCE = ROOT / "source.json"
MAX_RELEASES = 10  # how many recent releases to keep per app
# Fields in config.json app entries that are build settings, not source fields.
CONFIG_ONLY = {"repo", "asset", "includePrereleases", "entitlements"}


def request(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "ipa-source"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    return urllib.request.urlopen(req)


def releases(repo):
    with request(f"https://api.github.com/repos/{repo}/releases?per_page=30") as r:
        return json.load(r)


def read_ipa(url):
    """Download an IPA and return (size, sha256, Info.plist dict)."""
    sha = hashlib.sha256()
    size = 0
    with tempfile.TemporaryFile() as tmp:
        with request(url, accept="application/octet-stream") as r:
            while chunk := r.read(1 << 20):
                sha.update(chunk)
                tmp.write(chunk)
                size += len(chunk)
        tmp.seek(0)
        with zipfile.ZipFile(tmp) as z:
            name = next(n for n in z.namelist() if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", n))
            info = plistlib.loads(z.read(name))
    return size, sha.hexdigest(), info


def changelog(release):
    title = release.get("name") or release["tag_name"]
    body = (release.get("body") or "").strip()
    return f"{title}\n\n{body}" if body else title


def build_app(app, existing):
    known = {v["downloadURL"]: v for v in (existing or {}).get("versions", [])}
    versions, privacy = [], (existing or {}).get("appPermissions", {}).get("privacy", {})

    for rel in releases(app["repo"]):
        if rel["draft"] or (rel["prerelease"] and not app.get("includePrereleases")):
            continue
        asset = next((a for a in rel["assets"] if a["name"] == app["asset"]), None)
        if not asset:
            continue
        url = asset["browser_download_url"]
        if url in known and known[url].get("size") == asset["size"]:
            versions.append(known[url])
        else:
            print(f"  reading {url}", file=sys.stderr)
            size, sha, info = read_ipa(url)
            if info["CFBundleIdentifier"] != app["bundleIdentifier"]:
                sys.exit(f"{url}: bundle ID {info['CFBundleIdentifier']} != {app['bundleIdentifier']}")
            if not versions:  # newest release defines the privacy strings
                privacy = {k: v for k, v in info.items() if k.endswith("UsageDescription")}
            versions.append({
                "version": info["CFBundleShortVersionString"],
                "buildVersion": info["CFBundleVersion"],
                "date": rel["published_at"],
                "localizedDescription": changelog(rel),
                "downloadURL": url,
                "size": size,
                "sha256": sha,
                "minOSVersion": info.get("MinimumOSVersion", "14.0"),
            })
        if len(versions) == MAX_RELEASES:
            break

    if not versions:
        print(f"  no releases with {app['asset']} in {app['repo']}", file=sys.stderr)
        return existing

    out = {k: v for k, v in app.items() if k not in CONFIG_ONLY}
    out["versions"] = versions
    out["appPermissions"] = {"entitlements": app.get("entitlements", []), "privacy": privacy}
    # Legacy top-level fields for older SideStore/AltStore builds and LiveContainer.
    latest = versions[0]
    out.update({
        "version": latest["version"],
        "versionDate": latest["date"],
        "versionDescription": latest["localizedDescription"],
        "downloadURL": latest["downloadURL"],
        "size": latest["size"],
    })
    return out


def main():
    config = json.loads(CONFIG.read_text())
    old = json.loads(SOURCE.read_text()) if SOURCE.exists() else {}
    old_apps = {a["bundleIdentifier"]: a for a in old.get("apps", [])}

    apps = []
    for app in config["apps"]:
        print(f"{app['name']} ({app['repo']})", file=sys.stderr)
        built = build_app(app, old_apps.get(app["bundleIdentifier"]))
        if built:
            apps.append(built)

    source = {**config["source"], "apps": apps, "news": old.get("news", [])}
    text = json.dumps(source, indent=2, ensure_ascii=False) + "\n"
    if SOURCE.exists() and SOURCE.read_text() == text:
        print("source.json unchanged", file=sys.stderr)
    else:
        SOURCE.write_text(text)
        print("source.json updated", file=sys.stderr)


if __name__ == "__main__":
    main()
