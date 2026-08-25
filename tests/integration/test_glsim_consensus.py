from pathlib import Path
import json

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Classify one designated agent action"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"capability_id": "DRAFT", "scope_label": "WITHIN_SCOPE"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_single_action_ticket():
    controller_account, agent_account = create_accounts(2)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "agent_permission_check.py")
    deployed = factory.deploy_contract_tx(args=[agent_account.address, "Documentation assistant", "Agents may prepare local drafts and read public metadata, but only the human controller may authorize publication or another irreversible external change."], account=controller_account, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    controller = factory.build_contract(address, account=controller_account)
    agent = factory.build_contract(address, account=agent_account)
    ok(controller.add_capability(args=["DRAFT", "Create and revise local documentation drafts without publishing them."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(controller.add_capability(args=["READ", "Read public repository metadata without changing an external resource."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(controller.invite_action_ticket(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(agent.submit_action_ticket(args=["Prepare a local release-note draft from public repository metadata.", "A local documentation draft file", "The controller needs a draft for review and the agent will not publish it."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(agent.check_ticket_scope(args=[]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(controller.decide_ticket(args=["APPROVE", "Approved for a local draft only; publication remains outside the ticket."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(agent.attest_execution(args=["Created the local draft and made no external publication request."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert controller.get_state(args=[]).call()["status"] == "COMPLETE"
