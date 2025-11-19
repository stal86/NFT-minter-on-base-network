# 🎨 NFT Minter on Base network

A user-friendly Streamlit web app to mint NFTs on the Base network with IPFS metadata storage via Pinata.

## ✨ Features

- 🖼️ **Image Upload**: Support for PNG, JPG, JPEG, GIF, WEBP
- 📝 **Metadata Creation**: OpenSea-compatible metadata with custom attributes
- 🌐 **IPFS Storage**: Automatic upload to IPFS via Pinata
- ⛓️ **Base Network**: Deploy on Base Mainnet or Sepolia Testnet
- 💰 **Gas Optimization**: Efficient transaction handling
- 🎯 **User-Friendly**: Clean Streamlit interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MetaMask wallet with Base network configured
- Pinata account (free tier works)
- ETH on Base network for gas fees

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/nft-minter-base.git
cd nft-minter-base
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create and configure your `.env` file**
```env
CONTRACT_ADDRESS=0xYourContractAddress
PRIVATE_KEY=your_private_key_here
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key
```

### Run the Application

```bash
streamlit run nftmint.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 Requirements

```txt
streamlit==1.32.0
web3==6.15.1
python-dotenv==1.0.1
Pillow==10.2.0
requests==2.31.0
```

## 🔧 Configuration

### 1. Deploy Smart Contract

Use [Remix IDE](https://remix.ethereum.org/) to deploy the `MyNFT.sol` contract:

1. Copy the contract code from `MyNFT.sol`
2. Compile with Solidity 0.8.20+
3. Connect MetaMask to Base network
4. Deploy with your address as `initialOwner`
5. Copy the deployed contract address

### 2. Base Network Setup

**Base Mainnet:**
- Network Name: `Base`
- RPC URL: `https://mainnet.base.org`
- Chain ID: `8453`
- Currency Symbol: `ETH`
- Block Explorer: `https://basescan.org`

**Base Sepolia Testnet:**
- Network Name: `Base Sepolia`
- RPC URL: `https://sepolia.base.org`
- Chain ID: `84532`
- Currency Symbol: `ETH`
- Block Explorer: `https://sepolia.basescan.org`

### 3. Pinata Setup

1. Create a free account at [pinata.cloud](https://pinata.cloud)
2. Go to API Keys section
3. Generate a new API Key
4. Copy both API Key and Secret Key to your `.env` file

## 📖 Usage

### Minting an NFT

1. **Upload Image**: Click "Choose an image" and select your NFT artwork
2. **Fill Metadata**:
   - NFT Name (required)
   - Description (required)
   - Recipient Address (optional - defaults to your wallet)
3. **Add Attributes** (optional): Click "Add Attributes" to include OpenSea traits
4. **Click "Create NFT"**: Wait for the process to complete

### Process Flow

```
1. Upload image → IPFS
2. Create metadata → IPFS
3. Mint NFT → Base Blockchain
4. View on OpenSea
```

## 🔒 Security

**⚠️ IMPORTANT SECURITY NOTES:**

- NEVER commit your `.env` file to Git
- NEVER share your private key
- Use a separate wallet for minting (not your main wallet)
- Test on Sepolia testnet before using mainnet
- Keep your Pinata API keys secure

## 🌐 View Your NFTs

After minting, your NFTs will be visible on:

**OpenSea Mainnet:**
```
https://opensea.io/assets/base/{CONTRACT_ADDRESS}/{TOKEN_ID}
```

**OpenSea Testnet:**
```
https://testnets.opensea.io/assets/base-sepolia/{CONTRACT_ADDRESS}/{TOKEN_ID}
```

*Note: It may take a few minutes for NFTs to appear on OpenSea*

## 🐛 Troubleshooting

### Common Issues

**"Invalid private key" error**
- Ensure your private key is in the correct format (no 0x prefix in .env)
- Check for extra spaces or newlines

**"Insufficient payment" error**
- Make sure you have enough ETH for gas fees
- On Base, gas fees are typically very low ($0.01-0.10)

**"Unable to connect to Base" error**
- Check your internet connection
- Verify RPC URL is correct
- Try switching networks in the app

**IPFS upload fails**
- Verify Pinata API keys are correct
- Check Pinata account is active
- Ensure you haven't exceeded free tier limits

**Gas estimation failed**
- Your wallet may not have enough ETH
- The contract may not be deployed correctly
- Public minting might not be active on the contract

## 📝 License

This project is licensed under the MIT License.

## 🔗 Links

- [Base Documentation](https://docs.base.org/)
- [OpenSea Developer Docs](https://docs.opensea.io/)
- [Pinata IPFS](https://pinata.cloud/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🎯 Roadmap

- [ ] Add batch minting support
- [ ] Implement whitelist functionality
- [ ] Add collection statistics dashboard
- [ ] Support for multiple file formats
- [ ] Integration with other IPFS providers

---

Made with ❤️ by dnapog.base.eth
