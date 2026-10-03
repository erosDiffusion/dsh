# dsh-video-scene-extractor

A [DeepSeek Harness](https://deepseek-harness.github.io/deepseek-harness/) **bundle** that
packages the **video-scene-extractor** agent as a shareable plugin:

| What it ships | Where it appears |
|---|---|
| **Agent preset** `Video Scene Extractor` — the creator-mode (cordis) roster verbatim with a video-analysis persona and this package's skill root | Agent presets page (composer hero button) |
| **Skill** `video-scene-extractor` — SKILL.md runbook (deterministic pipeline + output contract + hard-won failure catalog) | `tool-skill` catalog of preset sessions |
| **Pipeline scripts** — `mad_scan.py` (packet-pts + MAD isolated-spike cut detection), `sheet_builder.py` (before/after verification sheets), `consolidate.py` (canonical scenes.json), `extract_frames.py`, `montage.py`, `hashcheck.py`, `check_ffmpeg.py` | `skills/video-scene-extractor/scripts/` in the bundle |
| **`/video-extractor <absolute-video-path> [notes]`** slash command — validates the path and submits a runbook-driven turn | composer input, any session on the profile |
| **`DSH_VIDEO_SKILL_DIR`** shell variable — the bundle's `skills/video-scene-extractor` dir, machine-independent | every agent bash execution |

## How it works

The bundle is an npm package with two cordis patch layers (`dsh.bundle.patch`):

1. `cordis.patch.yml` — one host row (`name: dsh-video-scene-extractor`) loading
   `src/index.js`, which registers the slash command and the `DSH_VIDEO_SKILL_DIR`
   shell-env contributor.
2. `presets/video-scene-extractor.patch.yml` — one `@deepseek-ai/dsh-agent-preset`
   row: the creator-mode roster (persona, tools, planning, compaction, delegation,
   skill-filesystem, …) with `skill-filesystem.customSkillDirs` pointing at this
   package's own `skills/` directory, resolved at compose time via
   `createRequire(baseUrl).resolve('dsh-video-scene-extractor/package.json')` —
   the same idiom the shipped `cordis` preset uses, so the path is
   machine-independent.

Zero runtime dependencies (Node builtins only). The skill's `SKILL.md` invocation
block uses `export SKILL="${DSH_VIDEO_SKILL_DIR}"`, so the agent never needs a
machine-specific path.

## Install

Any DSH ≥ 0.2.1, Node ≥ 22. From the GUI (Plugins → Add plugin) or CLI:

```sh
# from GitHub (recommended; pin the tag)
dsh plugin --profile web add github:YOUR_USER/dsh-video-scene-extractor#v0.1.0

# or npm, once published
dsh plugin --profile web add dsh-video-scene-extractor

# or a local directory / tarball while developing
dsh plugin --profile web add /abs/path/to/dsh-video-scene-extractor
```

The manager runs `pnpm add` inside the profile and selects the bundle in the
profile manifest. It then shows up in the GUI **Plugins** section (name, version,
description, enable toggle) exactly like `dsh-qwen38-local-qol`.

### Requirements (on the machine that runs the agent)

- `python3` with `Pillow` (verification sheets) — the scripts check and fail loud.
- `ffmpeg` ≥ 5 with `libx264` and `lavfi` (`scdet` works on 6.x; `check_ffmpeg.py`
  probes what is present).
- Optional: a whisper install (faster-whisper venv or `whisper-cpp`) for the
  transcript step; the pipeline runs without speech when the video is instrumental.
- **Vision for the agent model (strongly recommended):** the pipeline's
  verification step reads before/after frames. For a text-only model, the runbook
  falls back to MAD/signature flags. For a VLM served via an OpenAI-compatible
  route, declare per-model `input: [text, image]` in the profile patch (do NOT
  put it on the route — other text-only models on the route would over-claim and
  400 mid-turn).

## Usage

1. New session → pick the **Video Scene Extractor** preset in the composer.
2. `/video-extractor /path/to/clip.mp4` (or just describe the task in chat).
3. Deliverables land in the project root (path contract:
   `~/Apps/generated/<video-basename>/`): `scenes.json` (canonical), `scenes.md`
   (tabular cue sheet), `ref2va_prompts.md` (six-section MiniMax-H3 ref2va,
   images referenced by file name — **never embedded**), `frames/scene_NN.png`,
   `data/` intermediates.

### Deliverable formats (fixed contract)

- `scenes.md`: References table → Result line → Scene table (Scene | Start | Frame |
  Dur | Shot description | Start frame | Dialogue) → Cut verification → Notes.
  M cuts → M+1 scenes; times from the packet grid, never container fps.
- `ref2va_prompts.md`: one six-section block — `subject_definitions` / `summary`
  (`[reference generation]`) / `retention_analysis` (`fully_preserved` /
  `partially_preserved`) / `detailed_description` (`[Shot N]`) /
  `overall_soundscape` / `non_diegetic_music`. `<Picture N>` references the
  `frames/` file names.

## Maintenance notes

- **Supersedes hand-rolled presets.** If you had a manual
  `~/.dsh/.agent-presets/video-scene-extractor/` directory (or a local plugin
  registering a `/video-extractor` command), remove it after installing this
  bundle — the preset id would collide and the command name is already taken.
- **Preset edits:** the Web editor's preset overrides layer on top of this row
  (by row id); a bundle update does not clobber saved overrides.
- **Updating:** `dsh plugin --profile web update` (or re-`add` with the new tag);
  scripts and SKILL.md are versioned with the package — the skill dir in
  `node_modules` is read-only code, never a write target.
- **Vision 400s / "video analysis not available":** check the model entry's
  `input` modalities with `dsh --profile <p> --dump-config`.

## License

MIT — see [LICENSE](LICENSE).
