# LEWD Modded Exes backlog

Engine changes asked for by LEWD threads. Not started unless marked.

| Item | From | Status | Notes |
| --- | --- | --- | --- |
| Spawn islands (DLTX-style all.spawn merge) | Tarkov level port | Parked: the user wants no engine changes in the level port for now | After loading all.spawn, also read `gamedata\spawns\*.island` and append each as its own game-graph island: next level id, vertex ids after the existing ones, no cross-level edges, own cross table, nothing renumbered (GAMMA's hard-coded GVIDs keep working). Likely hook: `alife_spawn_registry` / `CGameGraph` construction, before scripts run. Island format = the per-level chunk data `spawn_splice.py` writes. References on the user's PC: `H:\ai_modding\LEWD LEVELS\pipeline\xrbuild\spawn_splice.py`, `zone_spawn.py`, `LEWD LEVELS\zone\zone_levels.json`. |
| `lewd_engine_features()` | LEWD MODDING | Planned | One Lua query for all projects, returns a table of feature flags. Each feature commit adds its flag. |
| PBR renderer, bodycam, Monolith hand IK | LEWD MODDING | Planned | Port onto `lewd` as separate commits, off by default where possible, toggled from the LEWD MCM Exe section. |
| B2 contact callbacks, B12 camera cull | LEWD MODDING | Planned | Toggles in the MCM Exe section. |
