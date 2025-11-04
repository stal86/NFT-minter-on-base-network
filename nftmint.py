import streamlit as st
import json
import os
from web3 import Web3
import requests
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configuration
st.set_page_config(page_title="NFT Minter on Base", page_icon="🎨", layout="wide")

# Title
st.title("🎨 NFT Creator on Base")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Contract information
    contract_address = st.text_input(
        "Contract Address",
        value=os.getenv("CONTRACT_ADDRESS", ""),
        help="Your deployed smart contract address"
    )
    
    # Private key (warning: never share!)
    private_key = st.text_input(
        "Private Key",
        value=os.getenv("PRIVATE_KEY", ""),
        type="password",
        help="Your private key (keep it secret!)"
    )
    
    # Pinata API Keys for IPFS
    pinata_api_key = st.text_input(
        "Pinata API Key",
        value=os.getenv("PINATA_API_KEY", ""),
        type="password"
    )
    
    pinata_secret_key = st.text_input(
        "Pinata Secret Key",
        value=os.getenv("PINATA_SECRET_KEY", ""),
        type="password"
    )
    
    # Network selection
    network = st.selectbox(
        "Network",
        ["Base Mainnet", "Base Sepolia (Testnet)"],
        help="Choose the Base network"
    )
    
    st.markdown("---")
    st.info("💡 You can also create a .env file with these variables")
    
    # Display wallet address if private key is provided
    if private_key:
        try:
            w3 = Web3()
            account = w3.eth.account.from_key(private_key)
            st.success(f"Wallet: {account.address[:6]}...{account.address[-4:]}")
        except:
            st.error("❌ Invalid private key")

# Contract ABI - COMPLETE VERSION
CONTRACT_ABI = json.loads('''[
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "initialOwner",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "uri",
                "type": "string"
            }
        ],
        "name": "publicMint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "uri",
                "type": "string"
            }
        ],
        "name": "safeMint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            }
        ],
        "name": "tokenURI",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')

# Network configuration
NETWORKS = {
    "Base Mainnet": {
        "rpc": "https://mainnet.base.org",
        "chain_id": 8453,
        "explorer": "https://basescan.org"
    },
    "Base Sepolia (Testnet)": {
        "rpc": "https://sepolia.base.org",
        "chain_id": 84532,
        "explorer": "https://sepolia.basescan.org"
    }
}

def upload_to_pinata(file_bytes, filename):
    """Upload a file to Pinata IPFS"""
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    headers = {
        "pinata_api_key": pinata_api_key,
        "pinata_secret_api_key": pinata_secret_key
    }
    
    files = {
        'file': (filename, file_bytes)
    }
    
    try:
        response = requests.post(url, files=files, headers=headers)
        
        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            st.error(f"Upload error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error to Pinata: {str(e)}")
        return None

def create_metadata(name, description, image_ipfs_hash, attributes=None):
    """Create NFT metadata in OpenSea format"""
    metadata = {
        "name": name,
        "description": description,
        "image": f"ipfs://{image_ipfs_hash}"
    }
    
    if attributes:
        metadata["attributes"] = attributes
    
    return metadata

def upload_metadata_to_pinata(metadata):
    """Upload JSON metadata to Pinata"""
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    
    headers = {
        "Content-Type": "application/json",
        "pinata_api_key": pinata_api_key,
        "pinata_secret_api_key": pinata_secret_key
    }
    
    try:
        response = requests.post(url, json=metadata, headers=headers)
        
        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            st.error(f"Metadata upload error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error to Pinata: {str(e)}")
        return None

def mint_nft(to_address, token_uri, network_config):
    """Mint an NFT on Base blockchain"""
    try:
        # Connect to Base
        w3 = Web3(Web3.HTTPProvider(network_config["rpc"]))
        
        if not w3.is_connected():
            st.error("❌ Unable to connect to Base")
            return None
        
        # Get account from private key
        account = w3.eth.account.from_key(private_key)
        
        # Verify contract address checksum
        contract_address_checksum = Web3.to_checksum_address(contract_address)
        
        # Create contract instance
        contract = w3.eth.contract(address=contract_address_checksum, abi=CONTRACT_ABI)
        
        # Prepare transaction
        nonce = w3.eth.get_transaction_count(account.address)
        
        # Estimate gas
        try:
            gas_estimate = contract.functions.publicMint(
                Web3.to_checksum_address(to_address),
                token_uri
            ).estimate_gas({'from': account.address})
            
            # Add 20% safety margin
            gas_limit = int(gas_estimate * 1.2)
        except Exception as e:
            st.warning(f"Unable to estimate gas, using default value: {str(e)}")
            gas_limit = 300000
        
        # Get current gas price
        base_fee = w3.eth.gas_price
        max_priority_fee = w3.to_wei(0.1, 'gwei')  # Tip for miner
        max_fee = base_fee + max_priority_fee
        
        # Build transaction
        transaction = contract.functions.publicMint(
            Web3.to_checksum_address(to_address),
            token_uri
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': gas_limit,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': max_priority_fee,
            'chainId': network_config["chain_id"]
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        return tx_hash.hex(), network_config["explorer"]
        
    except Exception as e:
        st.error(f"❌ Minting error: {str(e)}")
        return None, None

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Image Upload")
    
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        help="Supported formats: PNG, JPG, JPEG, GIF, WEBP"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview of your NFT", use_container_width=True)
        
        # Display image information
        st.info(f"📏 Size: {image.size[0]}x{image.size[1]} pixels | Format: {image.format}")

with col2:
    st.header("📝 NFT Metadata")
    
    nft_name = st.text_input("NFT Name", placeholder="My Amazing NFT")
    nft_description = st.text_area("Description", placeholder="Description of your NFT...")
    recipient_address = st.text_input(
        "Recipient Address",
        placeholder="0x...",
        help="The address that will receive the NFT (leave empty for your address)"
    )
    
    # Optional attributes
    with st.expander("➕ Add Attributes (optional)"):
        st.markdown("Attributes will appear on OpenSea")
        num_attributes = st.number_input("Number of attributes", min_value=0, max_value=10, value=0)
        
        attributes = []
        for i in range(num_attributes):
            col_a, col_b = st.columns(2)
            with col_a:
                trait_type = st.text_input(f"Type {i+1}", key=f"trait_type_{i}", placeholder="Rarity")
            with col_b:
                value = st.text_input(f"Value {i+1}", key=f"value_{i}", placeholder="Legendary")
            
            if trait_type and value:
                attributes.append({"trait_type": trait_type, "value": value})

st.markdown("---")

# Configuration check
config_ok = all([contract_address, private_key, pinata_api_key, pinata_secret_key])

if not config_ok:
    st.warning("⚠️ Please fill in all configuration information in the sidebar")

# Minting button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    mint_button = st.button("🚀 Create NFT", type="primary", use_container_width=True, disabled=not config_ok)

if mint_button:
    if not uploaded_file:
        st.error("❌ Please upload an image")
    elif not nft_name or not nft_description:
        st.error("❌ Please fill in the name and description")
    else:
        # If no recipient address, use wallet address
        if not recipient_address:
            w3 = Web3()
            account = w3.eth.account.from_key(private_key)
            recipient_address = account.address
            st.info(f"ℹ️ The NFT will be sent to your address: {recipient_address}")
        
        # Verify address
        if not Web3.is_address(recipient_address):
            st.error("❌ Invalid recipient address")
        else:
            network_config = NETWORKS[network]
            
            with st.spinner("🔄 Creating NFT..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Upload image to IPFS
                status_text.text("1️⃣ Uploading image to IPFS...")
                progress_bar.progress(20)
                
                image_hash = upload_to_pinata(uploaded_file.getvalue(), uploaded_file.name)
                
                if image_hash:
                    st.success(f"✅ Image uploaded: ipfs://{image_hash}")
                    progress_bar.progress(40)
                    
                    # Step 2: Create and upload metadata
                    status_text.text("2️⃣ Creating metadata...")
                    progress_bar.progress(60)
                    
                    metadata = create_metadata(
                        nft_name, 
                        nft_description, 
                        image_hash,
                        attributes if attributes else None
                    )
                    
                    metadata_hash = upload_metadata_to_pinata(metadata)
                    
                    if metadata_hash:
                        st.success(f"✅ Metadata uploaded: ipfs://{metadata_hash}")
                        progress_bar.progress(80)
                        
                        # Step 3: Mint NFT
                        status_text.text("3️⃣ Minting NFT on Base...")
                        
                        token_uri = f"ipfs://{metadata_hash}"
                        result = mint_nft(recipient_address, token_uri, network_config)
                        
                        if result[0]:
                            tx_hash, explorer = result
                            progress_bar.progress(100)
                            status_text.text("✅ NFT created successfully!")
                            
                            st.success("✅ NFT created successfully!")
                            st.balloons()
                            
                            # Display information
                            st.markdown("### 🎉 NFT Information")
                            
                            info_col1, info_col2 = st.columns(2)
                            
                            with info_col1:
                                st.markdown("**Transaction Hash:**")
                                st.code(tx_hash, language=None)
                                
                                st.markdown("**Recipient:**")
                                st.code(recipient_address, language=None)
                            
                            with info_col2:
                                st.markdown("**Token URI:**")
                                st.code(token_uri, language=None)
                                
                                st.markdown("**Network:**")
                                st.code(network, language=None)
                            
                            # Links
                            st.markdown("### 🔗 Useful Links")
                            link_col1, link_col2, link_col3 = st.columns(3)
                            
                            with link_col1:
                                st.markdown(f"[📊 View on Explorer]({explorer}/tx/0x{tx_hash})")
                            
                            with link_col2:
                                if network == "Base Mainnet":
                                    st.markdown(f"[🌊 View on OpenSea](https://opensea.io/assets/base/{contract_address})")
                                else:
                                    st.markdown(f"[🌊 View on OpenSea Testnet](https://testnets.opensea.io/assets/base-sepolia/{contract_address})")
                            
                            with link_col3:
                                st.markdown(f"[🖼️ View IPFS Image](https://gateway.pinata.cloud/ipfs/{image_hash})")
                        else:
                            progress_bar.progress(0)
                            status_text.text("")

# Footer
st.markdown("---")
st.markdown("""
### 📚 Quick Instructions

1. **Configuration**: Fill in the information in the sidebar (or create a `.env` file)
2. **Upload**: Upload your image (PNG, JPG, GIF, WEBP)
3. **Metadata**: Fill in the name, description and optionally the recipient address
4. **Attributes** (optional): Add properties that will appear on OpenSea
5. **Minting**: Click on "Create NFT" and wait for confirmation

**⚠️ Security**: Never share your private key! Use a .env file to store it.

**ℹ️ Notes**: 
- NFTs will appear on OpenSea after a few minutes
- Make sure you have enough ETH for gas fees on the Base network
- Test on Base Sepolia first before using Mainnet
""")

# Button to clear data
if st.sidebar.button("🗑️ Clear Configuration", help="Clear configuration fields"):
    st.rerun()