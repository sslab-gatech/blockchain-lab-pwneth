from scripts.pwn import *

ROOT = os.path.dirname(__file__)

def deploy_uniswap():
    s = UniswapDeployer.deploy()
    factory = s.newFactory().return_value
    exchange = s.newExchange().return_value
    return (factory, exchange)

def init_uniswap():
    (factory_addr, exchange_addr) = deploy_uniswap()
    factory_abi = json.load(open(os.path.join(ROOT, "uniswap-v1/uniswap_factory.json")))
    factory = Contract.from_abi("Factory", factory_addr, abi=factory_abi)

    factory.initializeFactory(exchange_addr)
    return factory

def new_exchange(factory, token):
    factory.createExchange(token.address)

    exchange_abi = json.load(open(os.path.join(ROOT, "uniswap-v1/uniswap_exchange.json")))
    exchange_addr = factory.getExchange(token.address)
    return Contract.from_abi("Exchange", exchange_addr, abi=exchange_abi)

def main():
    accounts.default = a[0]

    factory = init_uniswap()
