from datetime import datetime
import time
import json
import requests

from kadena_sdk.signing import hash_and_sign
from kadena_sdk.key_pair import KeyPair

class KadenaSdk():

  SEND = '/send'
  LOCAL = '/local'
  LISTEN = '/listen'

  def __init__(self, base_url, network_id, key_pair: KeyPair=None):
    self.base_url = base_url
    self.network_id = network_id
    self.key_pair = key_pair


  def build_command(self, 
    payload,
    chain_ids,
    signers=[], 
    sender='', 
    gas_price=1.0e-5, 
    gas_limit=2500):
    """Build a command that can be committed (send) to or locally (local)
    sent to the Kadena network.
    Will create a command for each chain_id in the chain_ids list."""
    # Create Time Stamp
    t_epoch = time.time()
    t_epoch = round(t_epoch) - 15

    sender_actual = sender
    if sender_actual == '':
      sender_actual = f'k:{self.key_pair.get_pub_key()}'

    signers_actual = signers
    if self.key_pair and len(signers) == 0:
      signers_actual.append({ "pubKey": self.key_pair.get_pub_key() })

    cmds = {}
    for chain_id in chain_ids:
      command = {
        "networkId": self.network_id,
        "payload": payload,
        "signers": signers_actual,
        "meta": {
          "gasLimit": gas_limit,
          "chainId": chain_id,
          "gasPrice": gas_price,
          "sender": sender_actual,
          "ttl": 28000,
          "creationTime": t_epoch
        },
        "nonce": datetime.now().strftime("%Y%m%d%H%M%S")
      }
      cmds[chain_id] = command
      # cmds.append(command)

    return cmds


  def send(self, cmds):
    """Commits a list of commands to the Kadena network.
    Each command is an object created via build_command.
    Uses the chainId from the command to determine which chain to commit to."""
    ret = {}

    for command in cmds.values():
      cmd_json = json.dumps(command)
      hash_code, sig = self.sign(cmd_json)
    
      to_post = {
        'cmds': {
          'hash': hash_code,
          'sigs': [{'sig': sig}],
          'cmd': cmd_json,
        }
      }

      chain_id = command['meta']['chainId']
      ret[chain_id] = requests.post(
        self.build_url(self.SEND, chain_id), 
        json=to_post)

    return ret
  
  
  def local(self, cmds):
    """Locally (dirty) reads from Kadena using a list of commands.
    Each command is an object created via build_command.
    Uses the chainId from the command to determine which chain to read from."""
    ret = {}

    for command in cmds.values():
      cmd_json = json.dumps(command)
      hash_code, sig = self.sign(cmd_json)
    
      to_post = {
        'hash': hash_code,
        'sigs': [{'sig': sig}],
        'cmd': cmd_json,
      }

      chain_id = command['meta']['chainId']
      ret[chain_id] = requests.post(
        self.build_url(self.LOCAL, command['meta']['chainId']), 
        json=to_post)

    return ret
  

  def listen(self, tx_id, chain_id):
    """Blocking. Listens to a transaction on the given chain."""
    data = {
      'listen': tx_id
    }

    return requests.post(self.build_url(self.LISTEN, chain_id), json=data)
  

  def send_and_listen(self, command):
    """Commits a command to the Kadena network and listens to the transaction.
    Uses the chainId from the command to determine which chain to listen on."""
    chain_id = command['meta']['chainId']
    result = self.send({ chain_id: command })
    tx_id = result.json()['requestKeys'][0]
    print(f"Listening to tx: {tx_id}")
    return self.listen(tx_id, chain_id)
  

  def build_url(self, endpoint, chain_id):
    """Builds a url for a given endpoint and chain_id"""
    url = f'{self.base_url}/chainweb/0.0/{self.network_id}/chain/{chain_id}/pact/api/v1{endpoint}'
    print(url)
    return url


  def sign(self, command_json):
    """Signs a command with the private key of the locally stored 
    KeyPair instance."""
    return hash_and_sign(command_json, self.key_pair.get_priv_key())