// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC777/ERC777.sol";
import "./Owner.sol";

contract AdvERCToken is ERC777, Owner {
    constructor(uint256 initialSupply,
                string memory symbol,
                address[] memory defaultOperators)
        ERC777("General ERC777 Token", symbol, defaultOperators) {
        _mint(msg.sender, initialSupply, "", "");
    }

    function mint(address _receiver, uint256 amount) isOwner public {
        _mint(_receiver, amount, "", "");
    }
}
