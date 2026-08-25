# Architecture

## Deployment boundary

Deploy once for one agent and one controlled system boundary. Create a fresh deployment when the agent, system, global boundary, or capability registry changes.

Constructor data establishes the deployment subject and fixed role boundary. Later writes add only the bounded records permitted by the lifecycle; a completed instance cannot be reopened.

## Participants

The deployer is the controller. One different address is the designated agent that submits the ticket and execution attestation; only the controller can approve, deny, or revoke.

Addresses are normalized before authorization comparisons. Role checks and lifecycle gates execute before semantic assessment.

## State machine

`CAPABILITY_SETUP → AGENT_TICKET → SCOPE_CHECK → CONTROLLER_DECISION → APPROVED → COMPLETE, with deterministic deny or revoke exits`

The phase-like field is the primary lifecycle lock. Each write advances that path, performs a documented bounded loop, or fails with an `[EXPECTED]` user error.

## Evidence assembly

The stored system name, global boundary, ordered capability identifiers and rules, proposed action, target resource, and agent justification. No resource is contacted and no URL is followed.

Before consensus, the contract normalizes bounded text, copies required storage into plain local values, serializes a sorted JSON packet, and places it between explicit START/END delimiters. Nondeterministic callbacks do not read contract storage.

## Consensus boundary

Match the ticket to one frozen capability or NONE and classify it WITHIN_SCOPE, AMBIGUOUS, or OUTSIDE_SCOPE.

The leader callback validates exact JSON shape, field types, closed labels, masks or codes, and length bounds. A validator reruns the same semantic operation and rejects disagreement before state is committed.

## Deterministic boundary

Capability registration, designated-agent authorization, the controller's decision, revocation, and the agent's final attestation are deterministic.

Important invariants:

- At least two capabilities are frozen before the controller invites a ticket.
- Only the designated agent can submit the single action ticket or attest execution.
- The controller cannot approve an AMBIGUOUS or OUTSIDE_SCOPE ticket.
- The AI classification never grants permission and performs no action.

No method sends value, pays rewards, escrows assets, deletes external data, calls another contract, or invokes a webhook.

## Failure model

- Invalid caller input or lifecycle use raises `[EXPECTED]` and leaves state unchanged.
- Malformed or out-of-policy model output raises `[LLM_ERROR]` and cannot be stored.
- Validator disagreement cannot commit the semantic result.
- StudioNet proof reads explicitly target `LATEST_FINAL`, avoiding stale pre-final state.
