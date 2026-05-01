# Contributing

## Development setup

```bash
git clone https://github.com/brianpelow/orbit-platform
cd orbit-platform
uv sync
uv run pytest
```

## Adding OPA policies

1. Add Rego policy to policies/<domain>/
2. Add test data to policies/<domain>/testdata/
3. Test with: opa test policies/<domain>/
4. Document the policy in docs/adr/ if it represents a significant decision

## Standards

- All PRs require passing CI
- Test coverage must not decrease
- OPA policies must have corresponding test cases
- Update CHANGELOG.md for user-facing changes
