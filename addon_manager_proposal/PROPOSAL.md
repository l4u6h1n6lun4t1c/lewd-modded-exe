# Proposal: LEWD Modded Exes updater inside the LEWD Addon Manager

For the LEWD MODDING thread "Installer that downloads extras", which owns the LEWD Addon Manager.
This folder is a reference implementation to merge into `lewd_addon_manager.py`, not a second plugin to ship.

## What it adds

- **Check:** on MO2 start (setting `exes_updates`, on by default) read `lewd-exes.json` from
  `https://github.com/l4u6h1n6lun4t1c/lewd-modded-exe/releases/latest/download/lewd-exes.json`
  and compare with `<Anomaly>\bin_lewd\lewd-exes.json`. Offer Install / Update / Later / Skip this version.
- **Install:** download the release zip, check every file's SHA-256 against the manifest, then
  build `bin_lewd.new` = the runtime files of the game's `bin\` (DLLs, ini; no exes, pdbs or logs) + our exes + the manifest,
  and swap it in. The old build is kept as `bin_lewd.prev`. The game's `bin\` is never written to.
- **Gamedata:** the zip's `db\` folder goes into the MO2 mod "Modded Exes - LEWD", enabled, at priority 0 (lowest).
- **Launch:** `onAboutToRun` starts `bin_lewd\X.exe` when MO2 is about to start `bin\X.exe` and that file exists
  (setting `use_lewd_exes`, on by default). Any error falls back to the stock exe. The existing MO2 executables keep working,
  so nothing changes for players' habits, and it works the same on plain Anomaly and GAMMA.
- **Tools panel:** installed version, "Check now", "Use stock exes / Use LEWD exes", "Roll back to the previous build".

## Files

- `lewd_updater/core.py`: the logic, no MO2 or Qt imports, tested on its own (install twice, rollback, launch mapping,
  checksum failure). Fits the Addon Manager's "core" section; it can reuse the Addon Manager's `download()` and
  `file_sha256()` instead of its own.
- `lewd_updater/__init__.py`: the MO2 glue as a standalone plugin, for reference only. Merged into the Addon Manager it
  becomes: two settings, one more startup check after the addon check, one `onAboutToRun` hook, and an "Engine" group
  (or a button) in the LEWD Addons dialog.

## Notes for the merge

- The Addon Manager's help text says it "never touches your game exes". That line needs to change to: it installs the
  LEWD exes into a separate `bin_lewd` folder only, and never changes `bin`.
- First install on a player's PC: tell them to clear the shader cache once in the Anomaly launcher (same as upstream
  Modded Exes).
- `onAboutToRun` signature differs between MO2 versions (path only, or path + dir + args); the hook takes `*rest`.
- Not tested inside MO2 yet. Needs one run on the user's PC: first install, update, rollback, launch from the normal
  GAMMA executable.
