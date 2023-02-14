// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC20/ERC20.sol";
import "./Owner.sol";

contract ERCToken is ERC20, Owner {
    constructor(uint256 initialSupply, string memory symbol)
        ERC20("General ERC20 Token", symbol) {
        _mint(msg.sender, initialSupply);
    }

    function mint(address _receiver, uint256 amount) isOwner public {
        _mint(_receiver, amount);
    }
}
