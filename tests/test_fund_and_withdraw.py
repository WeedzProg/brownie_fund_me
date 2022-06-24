from brownie import config, accounts, network, FundMe, exceptions
from scripts.helpful_scripts import (
    get_account,
    LOCAL_BLOCKCHAINS_ENVIRONMENTS,
    FORKED_LOCAL_ENVIRONMENTS,
)
from scripts.deploy import deploy_fund_me
import pytest

# import necessary dependencies


def test_fund_withdraw():
    account = get_account()

    fund_me = deploy_fund_me()
    entrance_fee = fund_me.getEntranceFee() + 100
    print(f"Entrance fee is:{entrance_fee}")
    print("Making transaction to fund from wallet")
    tx = fund_me.fund({"from": account, "value": entrance_fee})
    print("waiting confirmation...")
    tx.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee

    print("Making transaction to withdraw to wallet")
    tx_withdraw = fund_me.withdraw({"from": account})
    print("waiting confirmation...")
    tx_withdraw.wait(1)

    assert fund_me.addressToAmountFunded(account.address) == 0


def test_only_owner():
    # should revert if detected blockchain isnt a development one
    # for testing this function with mainnet_test_fork change the variable in the if statement
    if network.show_active() not in LOCAL_BLOCKCHAINS_ENVIRONMENTS:
        pytest.skip("only for test networks")

    fund_me = deploy_fund_me()
    # test a bad actor trying to withdraw
    bad_actor = accounts.add()
    # should revert with only owner message
    # raises exception
    with pytest.raises(exceptions.VirtualMachineError):
        # try to withdraw from different account
        fund_me.withdraw({"from": bad_actor})
