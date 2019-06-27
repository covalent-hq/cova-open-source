# TODO 
1. Dockerize everything (Done)
2. uint128 is no needed in a lot of cases. Audit and fix to reduce cost.
3. Link a smart contract which has all the informations of authorized routing nodes. And link that to Agreements.sol to ensure that the routing node spacific transactions are only made by those spacific routing node addresses.

# Steps to Run Locally
Go to the parent folder and check how to run with docker-compose



# Overview of the smart contract Agreement.sol

* Term Dictionary

    1. `address`: ethereum wallet address.
    2. `msg.sender`: the wallet id of the caller of a function. i.e the user that sends the transasction in the ethereum blockchain.


* Structures
    * agreement:
        * `uint256 task_id` - task_id is uuid of the agreement. 
        * `address from` - ethereum address of the user who is trying to    create the agreement
        * `uint256 dataset_id` - id of the dataset the agreement creator is trying to train on  (TODO: change is to data hash)
        * `uint256 amount` - amount (in COVA) the agreement creator is willing to pay for the task and has approved the smart contract that amount of COVA.
        * `uint256 created_at` - timestamp when the agreement is mined
        * `uint256 expires_at` - timestamp when the agreement expires
        * `bool active` - indicator if the agreement is expired or not (comment: will be removed, useless)
    
* Functions
    * registerDataset
    ``` js 
    function registerDataset(uint256 _dataset_id) public returns (bool)
    ``` 
     This is called by a user to regsiter data in the smart contract. So what happens is the owner of the dataset with hash `did` will be the `msg.sender`.

     * checkDataset
    ``` js 
    function checkDataset(uint256 _dataset_id) public returns (bool)
    ``` 
     This is called by a user to check wheather the dataset with given `_dataset_id` exists or not.


    * createAgreement
    ``` js 
    function createAgreement(uint256 _task_id, uint256 _dataset_id, uint256 _amount, uint256 _alive_time) public returns (uint256)
    ``` 
    This is called by a user to create an agreement for in the smart contract. 
    
    When a user desires to do some compution, the user will ask a rounting node *** about the comutation cost, the routing node will return computation cost and an `_task_id`.

    After knowing how much the computaion will cost, The user is going to call this function as a reciept for his payment using this `_task_id`. 
    
    If this transaction is successful what that will mean is that the user has allowed the smart contract `_amount` amount of COVA and smart contract has transferred that amount of COVA to its address. And there is an entry in agreements table that. And this agreement is valid for `_alive_time` second.

    <b> Note: </b> The user must approve the smart contract the `_amount` amount of COVA to make this transaction call successful.

    * seeAgreement
    ``` js
    function seeAgreement(uint256 _task_id) view public returns (address, uint256,  uint256, uint256, uint256, bool)
    ```
    This function is called to get info of an agreement give the `_task_id`. Will be called by a routing node when user claims to have made payment and created an agreement under an spacific `_task_id`

    * increasExpirationTime 
    ``` js 
    function increasExpirationTime(uint256 _task_id, uint256 _added_time) public returns (bool)
    ``` 
    This is called by a rounting node when computation is not done by the time it should have been done due to some faults of computation nodes to increase the expiration time of the agreement_node.

    * revokeByDataUser
    ``` js
    function revokeByDataUser(uint256 _task_id) public returns (bool)
    ```
    This is called by the owner of the agreement to revoke an agreement. The user can only revoke after expiration time.

    * afterComputationCallBackFromRoutingNode
    ``` js
    function afterComputationCallBackFromRoutingNode(uint256 _task_id, bool _success) public returns (bool)
    ``` 
    This function is called from a routing node after computaion is successfully completed.


# CovaToken.sol

### Functions

**NOTE**: Callers MUST handle `false` from `returns (bool success)`.  Callers MUST NOT assume that `false` is never returned!


#### name

Returns the name of the token - e.g. `"MyToken"`.

OPTIONAL - This method can be used to improve usability,
but interfaces and other contracts MUST NOT expect these values to be present.


``` js
function name() view returns (string name)
```


#### symbol

Returns the symbol of the token. E.g. "HIX".

OPTIONAL - This method can be used to improve usability,
but interfaces and other contracts MUST NOT expect these values to be present.

``` js
function symbol() view returns (string symbol)
```



#### decimals

Returns the number of decimals the token uses - e.g. `8`, means to divide the token amount by `100000000` to get its user representation.

OPTIONAL - This method can be used to improve usability,
but interfaces and other contracts MUST NOT expect these values to be present.

``` js
function decimals() view returns (uint8 decimals)
```


#### totalSupply

Returns the total token supply.

``` js
function totalSupply() view returns (uint256 totalSupply)
```



#### balanceOf

Returns the account balance of another account with address `_owner`.

``` js
function balanceOf(address _owner) view returns (uint256 balance)
```



#### transfer

Transfers `_value` amount of tokens to address `_to`, and MUST fire the `Transfer` event.
The function SHOULD `throw` if the `_from` account balance does not have enough tokens to spend.

*Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.

``` js
function transfer(address _to, uint256 _value) returns (bool success)
```



#### transferFrom

Transfers `_value` amount of tokens from address `_from` to address `_to`, and MUST fire the `Transfer` event.

The `transferFrom` method is used for a withdraw workflow, allowing contracts to transfer tokens on your behalf.
This can be used for example to allow a contract to transfer tokens on your behalf and/or to charge fees in sub-currencies.
The function SHOULD `throw` unless the `_from` account has deliberately authorized the sender of the message via some mechanism.

*Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.

``` js
function transferFrom(address _from, address _to, uint256 _value) returns (bool success)
```



#### approve

Allows `_spender` to withdraw from your account multiple times, up to the `_value` amount. If this function is called again it overwrites the current allowance with `_value`.

**NOTE**: To prevent attack vectors like the one [described here](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/) and discussed [here](https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729),
clients SHOULD make sure to create user interfaces in such a way that they set the allowance first to `0` before setting it to another value for the same spender.
THOUGH The contract itself shouldn't enforce it, to allow backwards compatibility with contracts deployed before

``` js
function approve(address _spender, uint256 _value) returns (bool success)
```


#### allowance

Returns the amount which `_spender` is still allowed to withdraw from `_owner`.

``` js
function allowance(address _owner, address _spender) view returns (uint256 remaining)
```



### Events


#### Transfer

MUST trigger when tokens are transferred, including zero value transfers.

A token contract which creates new tokens SHOULD trigger a Transfer event with the `_from` address set to `0x0` when tokens are created.

``` js
event Transfer(address indexed _from, address indexed _to, uint256 _value)
```



#### Approval

MUST trigger on any successful call to `approve(address _spender, uint256 _value)`.

``` js
event Approval(address indexed _owner, address indexed _spender, uint256 _value)
```


    





    






