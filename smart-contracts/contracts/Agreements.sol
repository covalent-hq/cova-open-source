pragma solidity ^"0.4.24";

import "./CovaToken.sol";
import "./SafeMath.sol";

/**
 * @title Agreement Contract
 *
 */

 contract Agreements {
    CovaToken public cova;
    using SafeMath for uint256;
    
    event Dataset(
        string dataset_id,
        address indexed owner
    );

    event Agreement(
        string task_id,
        address indexed from,
        string dataset_id,
        uint256 amount,
        uint256 expires_at
    );

    event ComputationTimeIncreased(
        string task_id,
        uint256 added_time
    );


    struct agreement {
        string task_id;
        address from;
        string dataset_id;
        uint256 amount;
        uint256 created_at;
        uint256 expires_at;
        bool active;
    }

    mapping (string => agreement) private userAgreementById;
    mapping (string => address) private datasetOwner;

    // mapping (address => address []) private activeUserAgreementsByFromAddress;

    constructor(CovaToken _cova) public {
        cova = _cova;
    }

    function seeAddress() public returns (address){
        return this;
    }

    function registerDataset(string _dataset_id) public returns (bool) {
        require(datasetOwner[_dataset_id] == address(0));
        datasetOwner[_dataset_id] = msg.sender;
        emit Dataset(_dataset_id, msg.sender);
        return true;
    }

    function checkDataset(string _dataset_id) public returns (bool) {
        require(datasetOwner[_dataset_id] != address(0));
        return true;
    }

    function createAgreement(string _task_id, string _dataset_id, uint256 _amount, uint256 _alive_time) public returns (bool) {
        require(cova.transferFrom(msg.sender, address(this), _amount));

        uint256 created_at = now;
        uint256 expires_at = now + _alive_time;
    
        agreement memory userAgreement = agreement({
                                                        task_id: _task_id, 
                                                        from: msg.sender, 
                                                        dataset_id: _dataset_id, 
                                                        amount: _amount, 
                                                        created_at: created_at, 
                                                        expires_at: expires_at, 
                                                        active: true
                                                    }); 
    
        
        userAgreementById[_task_id] = userAgreement; 
        
        // activeUserAgreementsByFromAddress[msg.sender].push(userAgreement)
        
        emit Agreement(_task_id, msg.sender, _dataset_id, _amount, expires_at); 
        return true;
    }

    
    function seeAgreement(string _task_id) view public returns (address, string,  uint256, uint256, uint256, bool){
        agreement memory userAgreement = userAgreementById[_task_id];
        return (userAgreement.from, userAgreement.dataset_id, userAgreement.amount, userAgreement.created_at, userAgreement.expires_at, userAgreement.active);
    }

    /*
    function inavtivateUserAgreement(agreement[] agreements, uint256 _task_id) internal returns (bool){
        for(uint i = 0; i < agreements.length; i++){
            if(agreements[i].task_id == _task_id){
                agreements[i] = agreements[agreements.length - 1];
                delete agreements[agreements.length - 1];
                agreements.length--;
                return true
            }
        }
        return false;
    }
    */
    
    function increasExpirationTime(string _task_id, uint256 _added_time) public returns (bool) {
        // TODO: Check if msg.sender is in the valid routing node address
        userAgreementById[_task_id].expires_at = userAgreementById[_task_id].expires_at.add(_added_time);
        emit ComputationTimeIncreased(_task_id, _added_time);
        return true;
    }

    function revokeByDataUser(string _task_id) public returns (bool) {
        require(msg.sender == userAgreement.from);
        require(now > userAgreement.expires_at);
        require(cova.transfer(userAgreement.from, userAgreement.amount));
        agreement memory userAgreement = userAgreementById[_task_id];
        userAgreementById[_task_id].active = false;
        return true;
    }

    function afterComputationCallBackFromRoutingNode(string _task_id, bool _success) public returns (bool) {
        // TODO: Check if msg.sender is in the valid routing node address
        agreement memory userAgreement = userAgreementById[_task_id];
        if(_success == true){
            require(cova.transfer(datasetOwner[userAgreement.dataset_id], userAgreement.amount));
        }
        else{
            require(cova.transfer(userAgreement.from, userAgreement.amount));
        }
        userAgreementById[_task_id].active = false;
        
        // userAgreement.active = false


        // inactivateUserAgreement(activeUserAgreementsByFromAddress[msg.sender])
        

        // inactiveUserAgreementsByFromAddress[msg.sender].push(userAgreement)
    }
}