import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address


def ok(receipt):
    assert tx_execution_succeeded(receipt)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


@pytest.mark.integration
def test_studionet_agent_action_ticket(default_account, secondary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "agent_permission_check.py")
    deployed = ok(factory.deploy_contract_tx(args=[secondary_account.address, "Documentation assistant", "Agents may prepare local drafts and read public metadata, but only the human controller may authorize publication or another irreversible external change."], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    controller = factory.build_contract(address, account=default_account)
    agent = factory.build_contract(address, account=secondary_account)
    ok(controller.add_capability(args=["DRAFT", "Create and revise local documentation drafts without publishing them."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(controller.add_capability(args=["READ", "Read public repository metadata without changing an external resource."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(controller.invite_action_ticket(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(agent.submit_action_ticket(args=["Prepare a local release-note draft from public repository metadata.", "A local documentation draft file", "The controller needs a draft for review and the agent will not publish it."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = ok(agent.check_ticket_scope(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = controller.get_state(args=[]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["status"] == "CONTROLLER_DECISION"
    assert state["scope_label"] in ("WITHIN_SCOPE", "AMBIGUOUS", "OUTSIDE_SCOPE")
    observed = {"capability": state["matched_capability"], "scope_label": state["scope_label"]}
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": observed}, sort_keys=True))
