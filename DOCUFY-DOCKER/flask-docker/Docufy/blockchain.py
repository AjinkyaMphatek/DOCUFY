# ================== BLOCKCHAIN MODULE ==================

import datetime
import json
import hashlib
import requests
from urllib.parse import urlparse


class Blockchain:

    def __init__(self):
        self.chain = []
        self.nodes = set()

        # Create Genesis Block
        self.create_block(
            proof=1,
            previous_hash="0",
            sha_signature="0"
        )

    # --------------------------------------------------
    # Create a new block
    # --------------------------------------------------
    def create_block(self, proof, previous_hash, sha_signature):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "img_hash": sha_signature
        }

        self.chain.append(block)
        return block

    # --------------------------------------------------
    # Get last block
    # --------------------------------------------------
    def get_previous_block(self):
        return self.chain[-1]

    # --------------------------------------------------
    # Proof of Work
    # --------------------------------------------------
    def proof_of_work(self, previous_proof):
        new_proof = 1

        while True:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()
            ).hexdigest()

            if hash_operation[:4] == "0000":
                return new_proof

            new_proof += 1

    # --------------------------------------------------
    # Hash a block
    # --------------------------------------------------
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # --------------------------------------------------
    # Add image/document to blockchain  ✅ USED BY app.py
    # --------------------------------------------------
    def add_block(self, image_bytes):
        """
        image_bytes : raw bytes of uploaded image
        """

        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]

        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block)

        # Hash the image itself
        sha_signature = hashlib.sha256(image_bytes).hexdigest()

        self.create_block(
            proof=proof,
            previous_hash=previous_hash,
            sha_signature=sha_signature
        )

        return sha_signature

    # --------------------------------------------------
    # Check if chain is valid
    # --------------------------------------------------
    def is_chain_valid(self, chain):
        previous_block = chain[0]

        for index in range(1, len(chain)):
            block = chain[index]

            # Check hash link
            if block["previous_hash"] != self.hash(previous_block):
                return False

            # Check proof
            previous_proof = previous_block["proof"]
            proof = block["proof"]

            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()
            ).hexdigest()

            if hash_operation[:4] != "0000":
                return False

            previous_block = block

        return True

    # --------------------------------------------------
    # Check if image hash exists in blockchain
    # --------------------------------------------------
    def is_check(self, chain, sha_signature):
        for block in chain:
            if block["img_hash"] == sha_signature:
                return True
        return False

    # --------------------------------------------------
    # Add node to network
    # --------------------------------------------------
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # --------------------------------------------------
    # Replace chain with longest valid chain
    # --------------------------------------------------
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for node in network:
            response = requests.get(f"http://{node}/get_chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False
