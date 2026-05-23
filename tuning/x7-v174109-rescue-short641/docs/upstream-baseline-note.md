# Upstream Baseline Note

## Verified Upstream Version

The upstream `iterativv/NostalgiaForInfinity` `main` branch was checked against:

- Repository: `https://github.com/iterativv/NostalgiaForInfinity`
- Branch: `main`
- Commit checked: `324dbcedf08cb456225c03ccc45ea3819ef9f28d`
- Commit date: `2026-05-22T16:30:19Z`
- File: `NostalgiaForInfinityX7.py`

The upstream file reports:

```python
def version(self) -> str:
  return "v17.4.109"
```

## Local Baseline Difference

The local baseline used during this tuning run was based on upstream X7
`v17.4.109`, but it was not byte-identical to the upstream raw file.

The confirmed local difference was:

```python
"short_entry_condition_641_enable": False,
"short_entry_condition_642_enable": False,
```

while the upstream raw file had those example lines commented:

```python
# "short_entry_condition_641_enable": True,
# "short_entry_condition_642_enable": True,
```

For public wording, the accurate phrasing is:

> TestX7 tuning research package based on upstream NostalgiaForInfinityX7
> v17.4.109, with local 641/642 default-flag boundary documented.
