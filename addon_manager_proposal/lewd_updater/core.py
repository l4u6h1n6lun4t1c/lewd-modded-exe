"""LEWD Modded Exes updater: logic with no MO2 or Qt imports, so it can be tested on its own.

Layout it manages, inside the Anomaly folder:
    bin_lewd/            our exes + the runtime DLLs copied from bin/ + lewd-exes.json
    bin_lewd.prev/       the previous build, for rollback
and one MO2 mod, "Modded Exes - LEWD", holding the release's db/ gamedata.
GAMMA's bin/ is never written to.
"""

import hashlib
import json
import os
import re
import shutil
import ssl
import tempfile
import urllib.request
import zipfile

DEFAULT_REPO = "l4u6h1n6lun4t1c/lewd-modded-exe"
MANIFEST_NAME = "lewd-exes.json"
BIN_DIR = "bin_lewd"
MOD_NAME = "Modded Exes - LEWD"
USER_AGENT = "lewd-updater"
TIMEOUT = 10


class UpdateError(Exception):
    pass


def version_key(v):
    """'2026.11.22-lewd.3' -> (2026, 11, 22, 3). Unknown or empty sorts lowest."""
    nums = [int(n) for n in re.findall(r"\d+", v or "")]
    return tuple(nums) if nums else (-1,)


def is_newer(remote, local):
    return version_key(remote) > version_key(local)


def _open(url, timeout=TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream, application/json"})
    return urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context())


def fetch_json(url, timeout=TIMEOUT):
    with _open(url, timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def latest_release(repo=DEFAULT_REPO):
    """Returns (manifest dict, {asset name: download url}) of the newest LEWD release."""
    rel = fetch_json(f"https://api.github.com/repos/{repo}/releases/latest")
    assets = {a["name"]: a["browser_download_url"] for a in rel.get("assets", [])}
    if MANIFEST_NAME not in assets:
        raise UpdateError(f"Release {rel.get('tag_name')} has no {MANIFEST_NAME}")
    manifest = fetch_json(assets[MANIFEST_NAME])
    return manifest, assets


def download(url, dest, progress=None):
    with _open(url, timeout=60) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if progress:
                progress(done, total)
    return dest


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def installed_version(game_dir):
    p = os.path.join(game_dir, BIN_DIR, MANIFEST_NAME)
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f).get("version", "")
    except (OSError, ValueError):
        return ""


def extract_verified(zip_path, manifest, out_dir):
    """Unpacks the release zip and checks every file against the manifest's SHA-256 list."""
    expected = manifest.get("files") or {}
    if not expected:
        raise UpdateError("Manifest lists no files")
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            norm = name.replace("\\", "/")
            if norm.startswith("/") or ".." in norm.split("/"):
                raise UpdateError(f"Unsafe path in zip: {name}")
        z.extractall(out_dir)
    for rel, digest in expected.items():
        p = os.path.join(out_dir, *rel.split("/"))
        if not os.path.isfile(p):
            raise UpdateError(f"Missing from zip: {rel}")
        if sha256_file(p) != digest:
            raise UpdateError(f"Checksum mismatch: {rel}")
    return out_dir


def build_bin(game_dir, pkg_dir, manifest):
    """Makes bin_lewd.new: runtime files from the game's bin/ (DLLs, ini) + our exes + manifest."""
    src_bin = os.path.join(game_dir, "bin")
    new = os.path.join(game_dir, BIN_DIR + ".new")
    shutil.rmtree(new, ignore_errors=True)
    os.makedirs(new)
    if os.path.isdir(src_bin):
        for name in os.listdir(src_bin):
            p = os.path.join(src_bin, name)
            # Runtime files only: no exes, pdbs, logs or subfolders.
            if os.path.isfile(p) and not name.lower().endswith((".exe", ".pdb", ".log")):
                shutil.copy2(p, new)
    for name in os.listdir(os.path.join(pkg_dir, "bin")):
        shutil.copy2(os.path.join(pkg_dir, "bin", name), new)
    with open(os.path.join(new, MANIFEST_NAME), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return new


def swap_bin(game_dir):
    """bin_lewd -> bin_lewd.prev, bin_lewd.new -> bin_lewd. Fails cleanly if the game holds the exe."""
    cur = os.path.join(game_dir, BIN_DIR)
    new = cur + ".new"
    prev = cur + ".prev"
    if os.path.isdir(cur):
        old_prev = prev + ".old"
        shutil.rmtree(old_prev, ignore_errors=True)
        if os.path.isdir(prev):
            os.rename(prev, old_prev)
        try:
            os.rename(cur, prev)
        except OSError as e:
            if os.path.isdir(old_prev):
                os.rename(old_prev, prev)
            raise UpdateError("Could not replace bin_lewd. Close the game and try again.") from e
        shutil.rmtree(old_prev, ignore_errors=True)
    os.rename(new, cur)


def rollback(game_dir):
    cur = os.path.join(game_dir, BIN_DIR)
    prev = cur + ".prev"
    if not os.path.isdir(prev):
        raise UpdateError("There is no previous build to roll back to.")
    tmp = cur + ".rollback"
    shutil.rmtree(tmp, ignore_errors=True)
    if os.path.isdir(cur):
        try:
            os.rename(cur, tmp)
        except OSError as e:
            raise UpdateError("Could not replace bin_lewd. Close the game and try again.") from e
    os.rename(prev, cur)
    if os.path.isdir(tmp):
        os.rename(tmp, prev)
    return installed_version(game_dir)


def fill_mod(mod_dir, pkg_dir):
    """Replaces the mod's db/ folder with the release's gamedata."""
    src = os.path.join(pkg_dir, "db")
    dst = os.path.join(mod_dir, "db")
    shutil.rmtree(dst, ignore_errors=True)
    if os.path.isdir(src):
        shutil.copytree(src, dst)


def install_release(game_dir, mod_dir, manifest, assets, progress=None):
    """Downloads, verifies and installs a release. mod_dir must already exist."""
    zip_name = manifest.get("zip")
    if not zip_name or zip_name not in assets:
        raise UpdateError("Release zip not found")
    with tempfile.TemporaryDirectory(prefix="lewd_exes_") as tmp:
        zp = download(assets[zip_name], os.path.join(tmp, zip_name), progress)
        pkg = extract_verified(zp, manifest, os.path.join(tmp, "pkg"))
        build_bin(game_dir, pkg, manifest)
        swap_bin(game_dir)
        fill_mod(mod_dir, pkg)
    return manifest.get("version", "")


def lewd_exe_for(game_dir, path):
    """If path is an exe in the game's bin/ and bin_lewd has the same exe, returns that; else None."""
    try:
        p = os.path.normcase(os.path.abspath(path))
        bin_dir = os.path.normcase(os.path.abspath(os.path.join(game_dir, "bin")))
    except (TypeError, ValueError):
        return None
    if os.path.dirname(p) != bin_dir or not p.endswith(".exe"):
        return None
    cand = os.path.join(game_dir, BIN_DIR, os.path.basename(path))
    return cand if os.path.isfile(cand) else None


def self_update(plugin_dir, info, assets):
    """Replaces this plugin's files from the release's updater zip. Returns the new version."""
    name = info.get("zip")
    if not name or name not in assets:
        raise UpdateError("Updater zip not found in the release")
    with tempfile.TemporaryDirectory(prefix="lewd_updater_") as tmp:
        zp = download(assets[name], os.path.join(tmp, name))
        if info.get("sha256") and sha256_file(zp) != info["sha256"]:
            raise UpdateError("Checksum mismatch on the updater zip")
        out = os.path.join(tmp, "out")
        with zipfile.ZipFile(zp) as z:
            z.extractall(out)
        src = os.path.join(out, "lewd_updater")
        if not os.path.isfile(os.path.join(src, "__init__.py")):
            raise UpdateError("Updater zip has an unexpected layout")
        for root, _dirs, files in os.walk(src):
            rel = os.path.relpath(root, src)
            dst = os.path.join(plugin_dir, rel) if rel != "." else plugin_dir
            os.makedirs(dst, exist_ok=True)
            for fn in files:
                shutil.copy2(os.path.join(root, fn), os.path.join(dst, fn))
    return info.get("version", "")
