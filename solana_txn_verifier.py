# Solana Transaction Verifier - Beacon Labs
# This script tests retrieving and verifying Solana transactions using Beacon Labs.

import requests
from beacon import Task, Agent

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

class SolanaVerifier:
    def __init__(self, tx_signature):
        self.tx_signature = tx_signature
        self.agent = Agent("Solana Transaction Verifier")

    def verify_tx(self):
        task = Task(f"Check the validity and details of Solana transaction: {self.tx_signature}")
        response = self.agent.do(task)

        print("Solana Verification Response:")
        print(response)

    def fetch_tx_data(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [self.tx_signature, "json"]
        }
        response = requests.post(SOLANA_RPC_URL, json=payload)
        return response.json()

if __name__ == "__main__":
    test = SolanaVerifier("EXAMPLE_TX_SIGNATURE")
    test.verify_tx()
    print("Raw Solana Transaction Data:", test.fetch_tx_data())
