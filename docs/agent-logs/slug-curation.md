# Signal slug curation

Shortened overly long, mechanically-generated `signal_id` values in
`data/reports/2026-07-13.json` (only report containing these signals; none
recur elsewhere, so no cross-report renames were needed). `sheer-layering`
and `soft-tailoring` were left untouched as instructed.

| Old | New |
|---|---|
| `quiet-luxury-backlash-maximalist-pivot` | `quiet-luxury-backlash` |
| `1970s-boho-revival-styling` | `boho-revival` |
| `resale-secondhand-retail-growth` | `resale-growth` |
| `layered-tops-styling-social` | `layered-tops-styling` |
| `coastal-cowgirl-styling-evolution` | `coastal-cowgirl` |
| `off-duty-varsity-sports-luxe-summer-uniform` | `off-duty-varsity` |

Left unchanged (already at or under ~3 words): `1990s-minimalism-revival`,
`micro-bag-styling`, `menswear-aspirational-realism`,
`textured-maximalist-layering`.

No other fields touched. Verified with `python -m py_compile src/*.py` and
`python src/validate_all_reports.py` (both pass).
