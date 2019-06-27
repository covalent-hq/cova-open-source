const CovaToken = artifacts.require('./CovaToken.sol');
const Agreements = artifacts.require('./Agreements.sol');
const Faucet = artifacts.require('./Faucet.sol');

module.exports = function(deployer) {
    deployer.deploy(CovaToken)
    .then(() => {
        return deployer.deploy(Agreements, CovaToken.address)
        .then(() => {
            return deployer.deploy(Faucet, CovaToken.address)
        })
    })
};
