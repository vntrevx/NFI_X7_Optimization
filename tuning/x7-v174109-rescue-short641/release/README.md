# Release Bundle

`testx7-v174109-rescue-short641-install-20260523.tar.gz` is the sanitized
install bundle for this research package.

It contains `user_data` strategy/config files only. Internal handoff notes,
private host references, backtest archives, databases, and credentials are not
included.

Expected sha256:

```text
c8803508f146254e1f553015f9ab37b20858004c120a8e6b749203c54382418a
```

This sha differs from `evidence/local-status.json` because this public bundle is
sanitized and excludes internal handoff documents.

See `../INSTALL.md` or `../INSTALL_KO.md` before extracting it into a Freqtrade
checkout.
