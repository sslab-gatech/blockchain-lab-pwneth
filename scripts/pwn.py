import brownie
import json
import requests
import os
import functools
import sys
import subprocess
import solcx
import web3
import pyevmasm
import rlp

from brownie import *

from hexbytes import HexBytes
from pprint import pprint, pformat
from termcolor import colored

from brownie.test.managers.runner import RevertContextManager
from brownie.network.account import Account
from brownie.network.transaction import TransactionReceipt
from brownie.network.contract import Contract, ProjectContract
from brownie.network import priority_fee

from web3._utils.encoding import hex_encode_abi_type, to_hex
from web3._utils.normalizers import abi_ens_resolver
from web3._utils.abi import map_abi_data
from web3._utils.contracts import encode_abi
from web3.types import ABIFunction
from web3.datastructures import AttributeDict

from eth_typing import HexStr
from eth_utils import add_0x_prefix, remove_0x_prefix


# Set a default gas fee for geth
if not "Ganache" in web3.clientVersion:
    priority_fee("2 gwei")

URL = "https://tc.gts3.org/cs8803/2023-spring"
if "DEV" in os.environ:
    URL = "http://localhost:8080"

GAMEDATA = URL + "/assets/gamedata.json"
MAIN = URL + "/assets/abi/Main.json"

# Monkey patch this brownie bug with geth tracing
# https://github.com/eth-brownie/brownie/pull/1585
real_make_request = web3.provider.make_request
def monkey_patched_make_request(method, *args, **kwargs):
    if method == 'debug_traceTransaction':
        # Intercept web3.provider.make_request('debug_traceTransaction', (txid, {params},))
        if len(args) == 1 and type(args[0]) == tuple and len(args[0]) == 2:
            args[0][1]['enableMemory'] = True
    return real_make_request(method, *args, **kwargs)
web3.provider.make_request = monkey_patched_make_request


# pprint for borwnie's repl
def pp_attribute_dict(cls):
    out = ["{"]
    for k, v in cls.items():
        out.append("  %-17s: %s," % (k, pformat(v)))
    out.append("}")
    return "\n".join(out)
AttributeDict.__repr__ = pp_attribute_dict

def pp_hexbytes(cls):
    return pformat(cls.hex())
HexBytes.__repr__ = pp_hexbytes

# direct access to common functions
get_storage_at = web3.eth.get_storage_at
get_balance = web3.eth.get_balance
get_code = web3.eth.get_code
eth = web3.eth
to_wei = web3.toWei
web3.to_wei = to_wei
reverts = RevertContextManager

def encode_with_signature(signature, args):
    selector = web3.sha3(text=signature)[0:4]

    beg = signature.index("(")
    end = signature.rindex(")")
    assert(beg != -1 and end != -1)
    abi_types = signature[beg+1:end].split(",")
    if beg + 1 == end:
        return selector
    assert(len(abi_types) == len(args))

    abi = ABIFunction()
    abi["inputs"] = [{"type": type} for type in abi_types]

    return encode_abi(web3, abi, args, selector)

def _call(self, address, signature, args, kw={}):
    data = encode_with_signature(signature, args)
    tx = {"to": address, "data": data, "from": self.address}
    tx.update(kw)
    if not "gas" in tx:
        tx["gas"] = web3.eth.estimate_gas(tx)

    return web3.eth.sendTransaction(tx)
Account.call = _call

def _add(self, offset):
    return HexBytes(int(self.hex(), 16) + offset)
HexBytes.add = _add

def _int(self):
    return int(self.hex(), 16)
HexBytes.int = _int

def _to_address(self):
    assert self[0:12].int() == 0
    return self[-20:].hex()
HexBytes.to_address = _to_address

def _get_storage_at(self, slot):
    return get_storage_at(self.address, slot)
Contract.get_storage_at = _get_storage_at
ProjectContract.get_storage_at = _get_storage_at

def get_storage_of_array(addr, slot, element=5):
    addr_slot = web3.solidityKeccak(["uint256"], [slot])
    len = get_storage_at(addr, slot)

    print("[%s] len=%s" % (addr_slot.hex(), len.int()))
    for offset in range(element):
        print("  [%02d] %s" % (offset, get_storage_at(addr, addr_slot.add(offset)).hex()))

def _get_storage_of_array(self, slot, element=5):
    return get_storage_of_array(self.address, slot, element)
Contract.get_storage_of_array = _get_storage_of_array
ProjectContract.get_storage_of_array = _get_storage_of_array

#
# utilities for levels
#
@functools.lru_cache
def load_abi(name):
    """Load ABI/json of the label instance"""

    resp = requests.request("GET", URL + "/assets/abi/%s.json" % name)
    return resp.json()

@functools.lru_cache
def load_main():
    """Load the Main contract"""

    gamedata = load_gamedata()

    addr = gamedata["main"]
    abi = load_abi("Main")
    return Contract.from_abi("Main", addr, abi=abi["abi"])

@functools.lru_cache
def load_gamedata():
    """Fetch the gamedata from the website"""

    resp = requests.request("GET", GAMEDATA)
    return resp.json()

@functools.lru_cache
def get_instance_abi(name):
    """Get the name of the instance's ABI"""

    sol = None
    gamedata = load_gamedata()
    for c in gamedata["levels"]:
        if c["slug"] == name:
            sol =  c["instanceContract"]
    if sol is None:
        raise Exception("[!] Failed to find the level: %s" % name)
    return sol[:-4]

@functools.lru_cache
def get_gamedata_of_level(name):
    """Get the gamedata of an instance"""

    gamedata = load_gamedata()
    for c in gamedata["levels"]:
        if c["slug"] == name:
            return c
    raise Exception("[!] Failed to find the level: %s" % name)

def new_level(name):
    """Create a new level instance"""

    level = get_gamedata_of_level(name)

    Main = load_main()
    Main.createLevelInstance(name, {"value": level.get("deployFunds", 0)})
    return load_level(name)

def load_level(name):
    """Load an existing instance"""

    Main = load_main()
    addr = Main.getDeployedLevel(name)
    abi = load_abi(get_instance_abi(name))
    return Contract.from_abi(name, addr, abi=abi["abi"])

def submit_level(address):
    """Submit the level instance for grading"""

    Main = load_main()
    Main.submitLevelInstance(address)
    if Main.isSolvedInstance(address):
        print("[%s] Solved: %s!" % (colored('OK', 'green'), address))
    else:
        print("[%s] Failed to solve: %s!" % (colored('FAILED', 'red'), address))

def set_default_account():
    """Set a default account"""

    assert len(accounts) > 0

    if len(accounts) == 1:
        account = accounts[0]
    else:
        for i in range(len(accounts)):
            print("[%d] %s" % (i+1, accounts[i]))
        n = int(input("Which account to use?> "))
        account =  accounts[n-1]

    accounts.default = account

def evm_asm(asm):
    """Assemble EVM bytecodes"""

    return HexBytes(pyevmasm.assemble_hex(asm))

def evm_disasm(hexcode):
    """Disassemble EVM hexcode"""

    def _discard_swarmhash(hexcode):
        if '69706673' in hexcode:
            beg = hexcode.index('69706673')
            return hexcode[:beg-2]
        if '627a7a72' in hexcode:
            beg = hexcode.index('627a7a72')
            return hexcode[:beg-2]
        return hexcode

    if type(hexcode) == HexBytes:
        hexcode = hexcode.hex()
    if hexcode.startswith("0x"):
        hexcode = hexcode[2:]

    hexcode = _discard_swarmhash(hexcode)

    out = subprocess.check_output(["evm", "--input", hexcode, "disasm"],
                                  universal_newlines=True)
    # strip the first line
    return "\n".join(out.splitlines()[1:])

def dump_layout(src):
    """Dump the layout of the solidity contract"""

    layout = solcx.compile_source(src, output_values=["storage-layout"])
    layout = list(layout.values())[0]["storage-layout"]
    storage = layout["storage"]
    types = layout["types"]

    def _dump(storage, types):
        for e in storage:
            t = types[e["type"]]
            print("[%02d]@%03d-%03d %-20s : %s/%03dB %s"
                  % (int(e["slot"]), e["offset"],
                     e["offset"] + int(t["numberOfBytes"]) - 1,
                     e["label"], t["encoding"][0].capitalize(),
                     int(t["numberOfBytes"]), t["label"]))

    _dump(storage, types)

    for k, v in types.items():
        if "members" in v:
            print("\n%s:" % v["label"])
            _dump(v["members"], types)

def new_contract_address(address, nonce):
    """Calculate the address of a new contract (CREATE)"""

    addr = web3.keccak(hexstr=rlp.encode([int(address, 16), rlp.encode(nonce)]).hex())[12:]
    return web3.toChecksumAddress(addr)

def new_contract_address2(address, salt, bytecode):
    """Calculate the address of a new contract (CREATE2)"""

    hash = web3.solidityKeccak(["bytes1", "address", "bytes32", "bytes"],
                               ["0xff", address, salt, web3.keccak(hexstr=bytecode)])
    return web3.toChecksumAddress(hash[-20:])


def help():
    import inspect

    def _get_function_spec(f):
        s = inspect.signature(f)
        return "%s%s" % (f.__name__, s)

    funcs = [load_abi, load_main, load_gamedata, get_instance_abi,
             new_level, load_level, submit_level, set_default_account,
             evm_asm, evm_disasm,
             dump_layout, new_contract_address, new_contract_address2]
    for f in funcs:
        print("%25s: %s" % (_get_function_spec(f), f.__doc__))

    print()
    print(' e.g., lab02 = new_level("lab02")')
    print('       submit_level(lab02.address)')

def main():
    set_default_account()

