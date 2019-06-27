pragma solidity ^"0.4.24";

import "./CovaToken.sol";
import "./SafeMath.sol";

 /**
 * @title Faucet Contract
 *
 */

 contract Faucet {
    using SafeMath for uint256;

    CovaToken private cova;
    address private source;
    uint256 private amount;

    event Funded(
        address indexed user,
        uint256 time
    );

    mapping (address => uint256) private last;

    constructor(CovaToken _cova) public {
        cova = _cova;
        source = msg.sender;
        amount = 100 * (10 ** 18);
    }

    function lastFunded(address _user) public view returns (uint256) {
        return last[_user];
    }

    function fund(address _user) public returns (bool) {
        uint256 time = now;
        require(time >= last[_user].add(604800));
        require(cova.transferFrom(source, _user, amount));
        last[_user] = time;
        emit Funded(_user, time); 
        return true;
    }

    function setAmount(uint256 _amount) public returns (bool) {
    	require(msg.sender == source);
        amount = _amount;
    }
}
