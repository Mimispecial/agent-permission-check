# Security

## Scope

This repository contains one bounded Intelligent Contract, direct tests, a five-validator GLSim test, and an opt-in StudioNet smoke test. It has no frontend, backend, database, token, payout, proxy upgrade, or repository secret.

## Trust model

Untrusted evidence is delimited as data, model outputs use closed schemas, and validator replay must agree before semantic state is stored.

The deployer is the controller. One different address is the designated agent that submits the ticket and execution attestation; only the controller can approve, deny, or revoke.

## Implemented controls

- Concrete immutable GenVM runner hash; no floating runner dependency.
- Address normalization, explicit role separation, collection caps, one-time actions, and lifecycle locks.
- Bounded text plus strict `[EXPECTED]` and `[LLM_ERROR]` failure classes.
- Sorted, delimited evidence packets and independent validator replay.
- Storage is copied before nondeterministic callbacks; static audit requires zero callback reads from `self`.
- No cross-contract calls, fund custody, transfer, automated purchase, external deletion, or webhook.
- `.env`, caches, artifacts, wallet files, and local secrets are ignored. Live wallets are encrypted outside the workspace.

## Contract-specific safety properties

- At least two capabilities are frozen before the controller invites a ticket.
- Only the designated agent can submit the single action ticket or attest execution.
- The controller cannot approve an AMBIGUOUS or OUTSIDE_SCOPE ticket.
- The AI classification never grants permission and performs no action.

## Residual risks

- The contract does not execute, sandbox, or monitor the proposed action.
- The agent's execution attestation is a declaration, not external proof.
- A capability registry that is vague or incomplete can correctly lead to AMBIGUOUS or OUTSIDE_SCOPE.

Do not use this contract to make legal, medical, financial, employment, admission, credit, or physical-safety decisions beyond the explicit low-risk policy in its source. A new use case requires a fresh deployment and independent domain review.

## Reporting

Report vulnerabilities privately to the repository owner with the contract name, affected method, reproduction, expected invariant, and impact. Never include private keys, wallet passwords, or personal data.
