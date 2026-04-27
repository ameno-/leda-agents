# Generated Artifacts

These files are derived from the parameterized personality source.

Do not edit `generated/` by hand.

Regenerate with:

```bash
python3 scripts/render_profiles.py --sync-legacy
```

Outputs:
- `generated/forms/` — rendered markdown forms
- `generated/system/` — rendered system prompt overlays
- `generated/candidates/` — machine-readable candidate payloads for eval/search runners