/**
 * BitGenius Bitcoin Agent Test Script using Maestro API
 * Based on https://docs.gomaestro.org/bitcoin
 */

const axios = require('axios');

// Configuration
const MAESTRO_API_KEY = '8diL1zhh3pzQH1tZ7V9LcDSSOTfBekKE';
const CONTRACT_ADDRESS = 'ST24WKXB4QV239PWX5PHHCN7XHP6WMCYA7SRJY3XR';
const CONTRACT_NAME = 'bitgenius';
const NETWORK = 'testnet';

// Maestro API client
const maestro = axios.create({
  baseURL: 'https://api.gomaestro.org/v1',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${MAESTRO_API_KEY}`
  }
});

// Helper function to sleep
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Get Bitcoin network info
async function getBitcoinInfo() {
  try {
    const response = await maestro.get(`/bitcoin/${NETWORK}/info`);
    console.log('Bitcoin Network Info:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error getting Bitcoin info:', error.response?.data || error.message);
  }
}

// Get Bitcoin address details
async function getBitcoinAddressInfo(address) {
  try {
    const response = await maestro.get(`/bitcoin/${NETWORK}/addresses/${address}`);
    console.log(`Bitcoin Address ${address} Info:`, response.data);
    return response.data;
  } catch (error) {
    console.error('Error getting address info:', error.response?.data || error.message);
  }
}

// Get Bitcoin price
async function getBitcoinPrice() {
  try {
    const response = await maestro.get(`/bitcoin/price`);
    console.log('Current Bitcoin Price:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error getting Bitcoin price:', error.response?.data || error.message);
  }
}

// Get Stacks contract info using Hiro API
async function getContractInfo() {
  try {
    const response = await axios.get(
      `https://api.testnet.hiro.so/v2/contracts/interface/${CONTRACT_ADDRESS}/${CONTRACT_NAME}`
    );
    console.log('Contract Info:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error getting contract info:', error.response?.data || error.message);
  }
}

// Call get-all-templates on the contract
async function getAllTemplates() {
  try {
    const response = await axios.get(
      `https://api.testnet.hiro.so/v2/contracts/call-read/${CONTRACT_ADDRESS}/${CONTRACT_NAME}/get-all-templates`,
      { params: { args: [] } }
    );
    console.log('Agent Templates:', response.data);
    return response.data.result;
  } catch (error) {
    console.error('Error getting templates:', error.response?.data || error.message);
    return [];
  }
}

// Simulate a Bitcoin transaction for the auto_dca agent
async function simulateBitcoinDCAPurchase(amount, price) {
  // This is a simulation - in a real scenario you would use Maestro's
  // Bitcoin transaction API to create and broadcast a transaction
  console.log(`\n---- Simulating Bitcoin DCA Purchase ----`);
  console.log(`Amount: ${amount} sats`);
  console.log(`Price: $${price} per BTC`);
  console.log(`USD Value: $${(amount * price / 100000000).toFixed(2)}`);
  console.log(`Transaction would be recorded by BitGenius agent`);
  return {
    simulation: true,
    amount: amount,
    price: price,
    timestamp: new Date().toISOString()
  };
}

// Get Bitcoin transaction history
async function getBitcoinTransactionHistory(address, limit = 5) {
  try {
    const response = await maestro.get(`/bitcoin/${NETWORK}/addresses/${address}/transactions`, {
      params: { limit }
    });
    console.log(`Recent Bitcoin Transactions for ${address}:`, response.data);
    return response.data;
  } catch (error) {
    console.error('Error getting transaction history:', error.response?.data || error.message);
  }
}

// Check if an address is a Taproot address
async function checkTaprootAddress(address) {
  try {
    const response = await maestro.get(`/bitcoin/${NETWORK}/addresses/${address}/is-taproot`);
    console.log(`Is ${address} a Taproot address:`, response.data);
    return response.data;
  } catch (error) {
    console.error('Error checking Taproot address:', error.response?.data || error.message);
  }
}

// Main function to test BitGenius with Bitcoin operations
async function testBitGeniusBitcoinOperations() {
  console.log('***** Starting BitGenius Bitcoin Agent Tests *****\n');
  
  // 1. Get Bitcoin network info
  await getBitcoinInfo();
  console.log('');
  
  // 2. Check the contract's templates
  await getAllTemplates();
  console.log('');
  
  // 3. Get current Bitcoin price
  const priceInfo = await getBitcoinPrice();
  const currentPrice = priceInfo?.price || 64500;
  console.log('');
  
  // 4. Test addresses
  // Bitcoin testnet addresses (these are examples - use your own addresses)
  const testnetAddresses = [
    'tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx',  // P2WPKH address
    'tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7', // P2WSH address
    '2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm' // P2SH address
  ];
  
  for (const address of testnetAddresses) {
    await getBitcoinAddressInfo(address);
    await sleep(1000);
    
    await checkTaprootAddress(address);
    await sleep(1000);
    
    await getBitcoinTransactionHistory(address);
    await sleep(1000);
    
    console.log('');
  }
  
  // 5. Simulate Bitcoin DCA purchase
  await simulateBitcoinDCAPurchase(100000, currentPrice); // 100,000 sats
  console.log('');
  
  // 6. Simulate Arbitrage operation
  console.log(`\n---- Simulating Bitcoin Arbitrage Operation ----`);
  console.log(`Checking price on Exchange A: $${currentPrice}`);
  console.log(`Checking price on Exchange B: $${(currentPrice * 1.015).toFixed(2)}`);
  console.log(`Price difference: 1.5% - Executing arbitrage`);
  console.log(`Purchase amount: 0.01 BTC at $${currentPrice}`);
  console.log(`Sell amount: 0.01 BTC at $${(currentPrice * 1.015).toFixed(2)}`);
  console.log(`Profit: $${(0.01 * currentPrice * 0.015).toFixed(2)}`);
  console.log(`Transaction would be recorded by BitGenius agent`);
  console.log('');
  
  // 7. Simulate Privacy Mixer operation
  console.log(`\n---- Simulating Bitcoin Privacy Mixer Operation ----`);
  console.log(`Input address: tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx`);
  console.log(`Amount: 0.05 BTC`);
  console.log(`Executing mixed transaction through Rebar Shield`);
  console.log(`Output address 1: 2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm (0.02 BTC)`);
  console.log(`Output address 2: tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7 (0.029 BTC)`);
  console.log(`Fee: 0.001 BTC`);
  console.log(`Transaction would be recorded by BitGenius agent`);
  console.log('');
  
  console.log('***** BitGenius Bitcoin Agent Tests Complete *****');
}

// Run the tests
testBitGeniusBitcoinOperations().catch(error => {
  console.error('Error running BitGenius Bitcoin tests:', error);
});