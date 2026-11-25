# LEWD Modded Exes

A fork of [themrdemonized's Modded Exes](https://github.com/themrdemonized/xray-monolith) for S.T.A.L.K.E.R. Anomaly 1.5.3, with the engine changes LEWD mods need.
It works on plain Anomaly and on GAMMA.

## Branches

| Branch | What it holds |
| --- | --- |
| `main` | This readme and the CI workflows only. |
| `lewd` | Upstream's latest release plus our patch commits on top. This is what gets built and shipped. |

Each LEWD change is one small commit on `lewd`, so it can also be offered upstream as a pull request.
When upstream merges one, the next rebase drops our copy by itself.

## How updates work

- **LEWD upstream sync** runs every 6 hours. When upstream publishes a new release, it rebases `lewd` onto it, builds and publishes `<upstream tag>-lewd.<n>`.
  If our patches conflict, it opens an issue instead, and players keep the previous build.
- **LEWD build** can be run by hand on any ref. With *release* ticked it publishes a release, for example after adding a patch to `lewd`.

Each release has `lewd-modded-exes_<version>.zip` (`bin/` exes, `db/mods/` gamedata, license) and `lewd-exes.json` (version, upstream tag, SHA-256 of every file). The LEWD MO2 plugin reads the manifest.

## Install

The exes go into `<Anomaly>\bin_lewd`, never into `bin`, so GAMMA's updater leaves them alone and the stock exes stay as a fallback.
The `db/mods` gamedata goes into an MO2 mod "Modded Exes - LEWD" at the lowest priority. Add an MO2 executable that points at `bin_lewd\AnomalyDX11AVX.exe` (or `AnomalyDX11.exe` on CPUs without AVX).
The LEWD MO2 plugin does all of this and keeps it updated.

## Setup (once)

Add a repository secret `LEWD_PUSH_TOKEN`: a fine-grained personal access token for this repository only, with **Contents: read and write** and **Workflows: read and write**.
GitHub's built-in token can't push commits that touch `.github/workflows`, and upstream's history has such commits.

## License

The engine code is GSC Game World code under the terms in `License.txt` on the `lewd` branch: free redistribution with the notice kept, no commercial use.
All credit for the Modded Exes goes to themrdemonized and its contributors.
