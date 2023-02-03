// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.4.0 <0.9.0;
contract A {
    struct S {
        uint128 a;
        uint128 b;
        uint[2] staticArray;
        uint[] dynArray;
    }

    uint public x;
    uint256 public y;
    uint128 public z0;
    uint8 public z1;
    uint16 public z2;
    bool public b;
    S public s;
    address public addr;
    mapping (address => uint) public map1;
    mapping (uint => mapping (address => bool)) public map2;
    uint[] public array;
    string public s1;
    bytes public b1;

    function set_x(uint _x) public { x = _x; }
    function set_y(uint256 _y) public { y = _y; }
    function set_z0(uint128 _z0) public { z0 = _z0; }
    function set_z1(uint8 _z1) public { z1 = _z1; }
    function set_z2(uint16 _z2) public { z2 = _z2; }
    function set_b(bool _b) public { b = _b; }
    function set_s(S memory _s) public { s = _s; }
    function set_addr(address _addr) public { addr = _addr; }
    function set_map1(address _k, uint _v) public { map1[_k] = _v; }
    function set_map2(uint _k1, address _k2, bool _v) public { map2[_k1][_k2] = _v; }
    function add_to_array(uint _v) public { array.push(_v); }
    function set_s1(string memory _s1) public { s1 = _s1; }
    function set_b1(bytes memory _b1) public { b1 = _b1; }
}
