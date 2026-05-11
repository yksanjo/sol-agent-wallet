# Security Policy

## Beta status

Sol Agent Wallet is **beta software**. It can sign and submit Solana transactions on your behalf. Bugs, malformed LLM tool calls, or supply-chain compromises in dependencies could result in loss of funds.

**Use a burner wallet** with limited funds for any mainnet experimentation. Do not paste your daily-driver wallet's private key into agent configs.

## Supported versions

Only the latest minor version on PyPI receives security fixes during the v0.x series. After 1.0, the latest two minor versions will be supported.

| Version | Supported |
|---|---|
| 0.1.x | ✅ |
| < 0.1 | ❌ |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email **yoshi@musicailab.com** with:

- A description of the issue and its impact
- Steps to reproduce or a proof-of-concept
- The version (`pip show sol-agent-wallet`) and Python version
- Any suggested mitigation

**Response timeline:**

- Acknowledgement: within 72 hours
- Initial assessment: within 7 days
- Fix or mitigation plan: within 30 days for high-severity issues

You'll be credited in the [CHANGELOG](./CHANGELOG.md) for valid reports unless you prefer to remain anonymous.

## Threat model

### In scope

- Transaction-signing path: anything that could cause a transaction to be signed without the user's intent, or that could leak a private key
- Configuration parsing: env-var injection, RPC URL spoofing
- Tool registration: write tools appearing when they shouldn't (read-only mode)
- Tx-cap enforcement: bypasses of the per-transaction SOL limit

### Out of scope

- Phishing prompts that trick the *user* into requesting a malicious transaction through their agent — the LLM/agent UI is the authorization layer
- Solana network behavior, validator issues, RPC outages
- Jupiter routing outcomes (slippage, MEV)
- Operating-system-level keylogging or env-var exfiltration

## Hardening checklist for users

- ✅ Use a burner wallet — never paste a wallet you can't afford to lose
- ✅ Keep `SOLANA_MAX_TX_SOL` low until you trust the workflow
- ✅ Start on devnet (`SOLANA_NETWORK=devnet`, the default)
- ✅ Review every `sol_transfer` / `sol_swap` call in your client's approval UI
- ✅ Pin the version: `uvx sol-agent-wallet==0.1.0` (after audit)
- ✅ Revoke and rotate any private key that ever lived in an env var when you're done
