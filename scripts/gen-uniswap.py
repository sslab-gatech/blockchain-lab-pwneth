
import os

ROOT = os.path.dirname(__file__)
EXCHANGE = os.path.join(ROOT, "uniswap-v1/bytecode-exchange.txt")
FACTORY = os.path.join(ROOT, "uniswap-v1/bytecode-factory.txt")

OUT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

contract UniswapDeployer {
    function newFactory() public returns (address) {
        bytes memory code = hex"{{factory}}";
        address addr;
        assembly {
           addr := create(0, add(code, 32), mload(code))
        }
        return addr;
    }

    function newExchange() public returns (address) {
        bytes memory code = hex"{{exchange}}";
        address addr;
        assembly {
           addr := create(0, add(code, 32), mload(code))
        }
        return addr;
    }
}
"""

exchange = open(EXCHANGE).read().strip()[2:]
factory = open(FACTORY).read().strip()[2:]

OUT = OUT.replace("{{factory}}", factory)
OUT = OUT.replace("{{exchange}}", exchange)

print(OUT)
