from brownie import (
    network,
    config,
    accounts,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)


LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork"]
DECIMALS = 8
INITIAL_VALUE = 200000000000  # setting eth/usd to 2000 for development env


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}  # this is only for local development


def get_contract(contract_name):
    """This function will grab the contractor addresses from the brownie config if defined, otherwise it will deploy a mock version of that contract and return the mock contract.
    Args:
        contract_name (string)

    Returns:
        brownie.network.contract.ProjectContract: The most recently deployed version of the contractor

    """
    contract_type = contract_to_mock[
        contract_name
    ]  # this is only for local development

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if (
            len(contract_type) <= 0
        ):  # it's same like MockV3Aggregator.length.. if there is no such contract deployed, then deploy one
            deploy_mocks()
        contract = contract_type[-1]  # Get latest deployed contract
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name,
            contract_address,
            contract_type.abi,  # although contract_type is for mocks but the mock contract also has same functions so we can use them.
        )
    return contract


def deploy_mocks(decimal=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimal, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mocks Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")

    tx = link_token.transfer(
        contract_address, amount, {"from": account}
    )  # call transfer directly on link_token contract
    # same can be done by using link token interface

    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funding contract")
    return tx
