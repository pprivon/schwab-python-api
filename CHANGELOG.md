# Changelog

## 0.1.3

- `getOptionChains` returns one row per (strike, optionRoot). Monthly expiries list an AM and a PM contract under the same strike; 0.1.2 kept only the first and so dropped one root.
- Behaviour change: calls and puts are paired by `optionRoot`, not by list position. A contract with no `optionRoot` on one side is skipped (0.1.2 would have paired it positionally). A root present on only one side is skipped. Non-monthly expiries are unchanged.
