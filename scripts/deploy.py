from brownie import config, accounts, FundMe, network, MockV3Aggregator
import web3
from scripts.helpful_scripts import (
    get_account,
    verify_contracts,
    mock_v3_deploy,
    LOCAL_BLOCKCHAINS_ENVIRONMENTS,
    FORKED_LOCAL_ENVIRONMENTS,
)

# --------------
# Modification following refactoring
# --------------
# 1: add web3
# 2: after being done with mock function in helpful, import mock_v3_deploy from helpful
# 3: now can delete web3 as it is imported in helpful
# from web3 import Web3


def deploy_fund_me():
    # get account
    account = get_account()
    print("get sender account...")
    print("check chain...")
    # deploy the contract fund_me from our wallets as sender
    # -----------------------
    # Modification following the switch from remix to brownie and for not having stuff hard-coded
    # added pricefeed address before sending contract
    # fund_me = FundMe.deploy("0x8A753747A1Fa494EC906cE90E9f37563A8AF630e",{"from": account},publish_source=verify_contracts(),)
    #
    # can also do a if statement in this script or helpful script like this
    # if network.show_active()!="development":
    # price_feed_address= "0x8A753747A1Fa494EC906cE90E9f37563A8AF630e"
    # and pass price_feed_address to or deployment variable instead of the adress
    # but the problem stay the same we are hard coding an address into our contract or scripts.
    # so we can use an environment variable into brownie-config.yaml which will only be hard coded into our computer and ignored when uploading to git
    # and do this as a if statement

    # change : if network.show_active() != "development":
    # for below line and added FORKED_LOCAL_ENVIRONMENTS
    if (
        network.show_active() not in LOCAL_BLOCKCHAINS_ENVIRONMENTS
        or FORKED_LOCAL_ENVIRONMENTS
    ):
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]
        print(network.show_active(), " network detected, grabbing price feed...")
    else:
        print("Development chain detected...")
        # mock v1-simple mock done with brownie-config.yaml: (the true way to do mock is made through contracts -> test -> MockV3Aggregator.sol and chainlink-mix repo)
        # price_feed_address = config["networks"][network.show_active()][
        #    "eth_usd_price_feed"
        # ]

        # print(
        #    network.show_active(),
        #    "network detected. Mock Price Feed address: ",
        #    price_feed_address,
        # )

        # Mock V2 done through MockV3Aggregator
        # print(
        #    f"{network.show_active()} network detected. Access MockV3Aggregator for price feed."
        # )
        # mock_deploy = MockV3Aggregator.deploy(
        #    18, 2000000000000000000000, {"from": account}
        # )
        # print("Mock deployment done. Get price_feed from it...")
        # price_feed_address = mock_deploy.address
        # print(f"Price feed result:{price_feed_address}")

        # --------------
        # Modification following refactoring
        # --------------
        # Mock v2 refactoring:
        # - use web3.toWei to make initial_answer shorter and readable
        # - Instead of deploying each time Mock, to not deploy if already exist
        #  and if want to use for work get the latest version (the only one existing if already deployed in this logic case)
        # Like for our price_feed_address variable
        # - Which makes 'mock_deploy=' useless and can be deleted
        # = since we could have the need to use our mock often and not only for this contract
        # We can place it in hepful_script and only call it here.
        # - Then we can delete couples lines from here
        if len(MockV3Aggregator) <= 0:
            # print(
            #    f"{network.show_active()} network detected. Access MockV3Aggregator for price feed."
            # )
            # mock_deploy =
            # MockV3Aggregator.deploy(18, web3.toWei(2000, "ether"), {"from": account})
            # print("Mock deployment done. Get price_feed from it...")
            print("no mock detected, create deployment for it...")

            mock_v3_deploy()
        print("Found a mock, grabbing the last one deployed...")
        price_feed_address = MockV3Aggregator[-1].address
        print(f"Price feed result:{price_feed_address}")

        # return value of deploy function for the test to access the function

    # fund me deployment using verify contract fix 1 (if else statement from helpful script)
    # fund_me = FundMe.deploy(
    #    price_feed_address,
    #    {"from": account},
    #    publish_source=verify_contracts(),
    # )

    # fund me deployment using verify contract fix 2 from brownie-config.yaml
    fund_me = FundMe.deploy(
        price_feed_address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    print("Contract Deployed")
    return fund_me


# get different account depending of the network
# !!grab it from helpful_scripts.py!!
# def get_account():
#    if network.show_active() == "development":
#        return accounts[0]
#    else:
#        return accounts.add(config["wallets"]["from_key"])


def main():
    deploy_fund_me()
