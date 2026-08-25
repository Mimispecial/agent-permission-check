# Agent Permission Check

Checks one designated agent action ticket against a frozen capability registry while keeping approval, revocation, and completion under a human controller.

## Why it is an Intelligent Contract

Match the ticket to one frozen capability or NONE and classify it WITHIN_SCOPE, AMBIGUOUS, or OUTSIDE_SCOPE. GenLayer validators independently replay that semantic judgment before it becomes shared state. Capability registration, designated-agent authorization, the controller's decision, revocation, and the agent's final attestation are deterministic.

## Reusable deployment model

Deploy once for one agent and one controlled system boundary. Create a fresh deployment when the agent, system, global boundary, or capability registry changes.

A completed deployment is an auditable record and is not reset or silently repurposed. Reuse means deploying the same reviewed source with new constructor data.

## Roles and workflow

The deployer is the controller. One different address is the designated agent that submits the ticket and execution attestation; only the controller can approve, deny, or revoke.

State path: `CAPABILITY_SETUP → AGENT_TICKET → SCOPE_CHECK → CONTROLLER_DECISION → APPROVED → COMPLETE, with deterministic deny or revoke exits`

## Evidence boundary

The stored system name, global boundary, ordered capability identifiers and rules, proposed action, target resource, and agent justification. No resource is contacted and no URL is followed.

## Core invariants

- At least two capabilities are frozen before the controller invites a ticket.
- Only the designated agent can submit the single action ticket or attest execution.
- The controller cannot approve an AMBIGUOUS or OUTSIDE_SCOPE ticket.
- The AI classification never grants permission and performs no action.

## Public interface

Write methods: `add_capability, attest_execution, check_ticket_scope, decide_ticket, invite_action_ticket, revoke_approval, submit_action_ticket`

View methods: `get_capability, get_policy, get_state`

`get_policy` exposes the machine-readable operating boundary and confirms that this contract never custodies funds.

## Verification

Pinned GenVM runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/agent_permission_check.py
genvm-lint typecheck contracts/agent_permission_check.py
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The StudioNet smoke test is opt-in and uses three disposable Mimi-only accounts protected outside the workspace. It asserts finalized successful execution and reads committed state with `LATEST_FINAL`.

## Final StudioNet proof

- Contract: https://explorer-studio.genlayer.com/address/0xD11F7c644304E135A49a92D29D800F58f7f76d0a
- Studio import: https://studio.genlayer.com/?import-contract=0xD11F7c644304E135A49a92D29D800F58f7f76d0a
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0xa6b4cd572306bccfd9a94a1e12a073ad3aafb90c06533161f2a8f8a50d973aca
- Intelligent transaction: https://explorer-studio.genlayer.com/tx/0xe2d4ed6feed0c80c25a52b713fd8f71244cd6a1382c816c0bd7e21b93c5543cc
- Observed committed state: `{"capability":"DRAFT","scope_label":"WITHIN_SCOPE"}`
- Audited source SHA-256: `988f4cee1a095a5fecbd9dbdaf9cbad0917f46e15685bf4dec649e02c648324f`

## Limitations

- The contract does not execute, sandbox, or monitor the proposed action.
- The agent's execution attestation is a declaration, not external proof.
- A capability registry that is vague or incomplete can correctly lead to AMBIGUOUS or OUTSIDE_SCOPE.

## Repository map

- `contracts/agent_permission_check.py` — Intelligent Contract source
- `tests/direct` — hardened leader/validator and lifecycle tests
- `tests/integration/test_glsim_consensus.py` — five-validator simulator flow
- `tests/integration/test_studionet_smoke.py` — live opt-in proof
- `deployments/studionet.json` — source-bound public deployment evidence
- `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md` — reviewer material

License: MIT.
