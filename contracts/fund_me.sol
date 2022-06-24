// SPDX-License-Identifier: MIT

// Smart contract that lets anyone deposit ETH into the contract
// Only the owner of the contract can withdraw the ETH
pragma solidity ^0.6.0;

// Get the latest ETH/USD price from chainlink price feed
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract FundMe {
    // safe math library check uint256 for integer overflows
    using SafeMathChainlink for uint256;

    //mapping to store which address depositeded how much ETH
    mapping(address => uint256) public addressToAmountFunded;
    // array of addresses who deposited
    address[] public funders;
    //address of the owner (who deployed the contract)
    address public owner;
    //-----------------------
    // Modification following the switch from remix to brownie and for not having stuff hard-coded
    // Make aggregator and pricefeed global
    AggregatorV3Interface public priceFeed;

    // the first person to deploy the contract is
    // the owner
    //constructor() public {
    //    owner = msg.sender;
    //}

    //-----------------------
    // Modification following the switch from remix to brownie and for not having stuff hard-coded
    // the first person to deploy the contract is the owner
    // New : pricefeed address as input parameters
    // New : variable declaration = to AggregatorV3Interface type with parameters _pricefeed
    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    function fund() public payable {
        // 18 digit number to be compared with donated amount
        uint256 minimumUSD = 50 * 10**18;
        //is the donated amount less than 50USD?
        require(
            getConversionRate(msg.value) >= minimumUSD,
            "You need to spend more ETH!"
        );
        //if not, add to mapping and funders array
        addressToAmountFunded[msg.sender] += msg.value;
        funders.push(msg.sender);
    }

    //function to get the version of the chainlink pricefeed
    // Rinkyby testnet pricefeed ETH USD 0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
    function getVersion() public view returns (uint256) {
        //-----------------------
        // Modification following the switch from remix to brownie and for not having stuff hard-coded
        // Following in comments, can be deleted actually
        // as the address will be passed at the moment we deploy the contract to the global variable of AggregatorV3 we made for this purpose.
        //AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //    0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        //);
        return priceFeed.version();
    }

    function getPrice() public view returns (uint256) {
        //-----------------------
        // Modification following the switch from remix to brownie and for not having stuff hard-coded
        // Following in comments, can be deleted actually
        // as the address will be passed at the moment we deploy the contract to the global variable of AggregatorV3 we made for this purpose.
        //AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //    0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        //);
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        // ETH/USD rate in 18 digit
        return uint256(answer * 10000000000);
    }

    //-----------
    // Newly added function for minimum entrance fee value to be able to fund contract
    // come in place when we start to implement the script for interacting with fund and withdraw functions with brownie
    //-----------

    function getEntranceFee() public view returns (uint256) {
        uint256 minimumUSD = 50 * 10**18;
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        return (minimumUSD * precision) / price;
    }

    // 1000000000
    function getConversionRate(uint256 ethAmount)
        public
        view
        returns (uint256)
    {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1000000000000000000;
        // the actual ETH/USD conversation rate, after adjusting the extra 0s.
        return ethAmountInUsd;
    }

    //modifier: https://medium.com/coinmonks/solidity-tutorial-all-about-modifiers-a86cf81c14cb
    modifier onlyOwner() {
        //is the message sender owner of the contract?
        require(msg.sender == owner);

        _;
    }

    // onlyOwner modifer will first check the condition inside it
    // and
    // if true, withdraw function will be executed
    function withdraw() public payable onlyOwner {
        // If you are using Solidity version v0.8.0 or above,
        // you will need to modify the code below to
        // payable(msg.sender).transfer(address(this).balance);
        msg.sender.transfer(address(this).balance);

        //iterate through all the mappings and make them 0
        //since all the deposited amount has been withdrawn
        for (
            uint256 funderIndex = 0;
            funderIndex < funders.length;
            funderIndex++
        ) {
            address funder = funders[funderIndex];
            addressToAmountFunded[funder] = 0;
        }
        //funders array will be initialized to 0
        funders = new address[](0);
    }
}
