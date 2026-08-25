from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "agent_permission_check.py"
SDK = "v0.2.16"
PROMPT = "Classify one designated agent action"
BOUNDARY = "Agents may prepare local drafts and read public project metadata, but only the human controller may authorize publication or another irreversible external change."


def address(account):
    return "0x" + account.hex()


def ticket(vm, direct_deploy, controller, agent):
    vm.sender = controller
    contract = direct_deploy(str(CONTRACT), address(agent), "Documentation assistant", BOUNDARY, sdk_version=SDK)
    contract.add_capability("DRAFT", "Create and revise local documentation drafts without publishing them.")
    contract.add_capability("READ", "Read public repository metadata without changing any external resource.")
    contract.invite_action_ticket()
    vm.sender = agent
    contract.submit_action_ticket(
        "Prepare a local release-note draft from public repository metadata.",
        "A local draft file inside the documentation workspace",
        "The controller needs a draft for review, and the agent will not publish it.",
    )
    return contract


def test_scope_check_controller_approval_and_agent_attestation(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = ticket(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"capability_id": "DRAFT", "scope_label": "WITHIN_SCOPE"}))
    contract.check_ticket_scope()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"capability_id": "READ", "scope_label": "WITHIN_SCOPE"}))
    assert direct_vm.run_validator(leader_result=leader) is False
    direct_vm.sender = direct_alice
    contract.decide_ticket("APPROVE", "Approved for a local draft only; publication remains outside this ticket.")
    direct_vm.sender = direct_bob
    contract.attest_execution("Created the local draft file and made no request to any external publication service.")
    assert contract.get_state()["status"] == "COMPLETE"
    assert contract.get_state()["controller_decision"] == "APPROVE"


def test_ambiguous_scope_cannot_be_approved(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = ticket(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"capability_id": "DRAFT", "scope_label": "AMBIGUOUS"}))
    contract.check_ticket_scope()
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("within_scope_required"):
        contract.decide_ticket("APPROVE", "This attempted approval must fail because a material scope limit is ambiguous.")
    contract.decide_ticket("DENY", "Denied until the agent ticket explicitly excludes all external publication steps.")
    assert contract.get_state()["status"] == "COMPLETE"


def test_designated_agent_and_invalid_capability_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.sender = direct_alice
    contract = direct_deploy(str(CONTRACT), address(direct_bob), "Documentation assistant", BOUNDARY, sdk_version=SDK)
    contract.add_capability("DRAFT", "Create and revise local documentation drafts without publishing them.")
    contract.add_capability("READ", "Read public repository metadata without changing any external resource.")
    contract.invite_action_ticket()
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_designated_agent"):
        contract.submit_action_ticket("Prepare a local release-note draft from public repository metadata.", "A local documentation file", "An undesignated agent must not fill the designated ticket.")
    direct_vm.sender = direct_bob
    contract.submit_action_ticket("Prepare a local release-note draft from public repository metadata.", "A local documentation file", "The controller needs a local draft for review without publication.")
    direct_vm.mock_llm(PROMPT, json.dumps({"capability_id": "PUBLISH", "scope_label": "WITHIN_SCOPE"}))
    with direct_vm.expect_revert("unknown_capability"):
        contract.check_ticket_scope()
    assert contract.get_state()["status"] == "SCOPE_CHECK"
