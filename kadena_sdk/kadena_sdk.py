from datetime import datetime
import time
import json
import requests

from kadena_sdk.crypto_lib import *
from kadena_sdk.key_pair import KeyPair
from kadena_sdk.types import *

class KadenaSdk():

  SEND = '/send'
  LOCAL = '/local'
  LISTEN = '/listen'

  def __init__(self, base_url: str='https://api.testnet.chainweb.com', key_pair: KeyPair=None):
    self.base_url = base_url
    self.network_id = requests.get(f'{base_url}/config').json()['chainwebVersion']
    self.key_pair = key_pair


  def build_exec_payload(self, pact_code: str, env_data: dict={}) -> ExecPayload:
    """Builds an execute payload object for use with build_command."""
    return {
      'exec': {
        'code': pact_code,
        'data': env_data
      }
    }


  def build_cont_payload(self, 
    pact_id: str, 
    step: int,
    rollback: bool, 
    proof: str,
    env_data: dict={}) -> ContPayload:
    """Builds an execute payload object for use with build_command."""
    return {
      'cont': {
        'pactId': pact_id,
        'step': step,
        'rollback': rollback,
        'data': env_data,
        'proof': proof,
      }
    }


  def build_command(self, 
    payload: ExecPayload | ContPayload,
    chain_ids: list[str],
    signers: list[str]=None, 
    sender: str=None, 
    gas_price: float=1.0e-5, 
    gas_limit: int=2500):
    """Build a command that can be committed (send) to or locally (local)
    sent to the Kadena network.
    Will create a command for each chain_id in the chain_ids list.
    
    Payload must be in the format:
    {
      "exec": {
        "data": dict,
        "code": str
      }  
    }
    """
    # Create Time Stamp
    t_epoch = time.time()
    t_epoch = round(t_epoch) - 15

    sender_actual = sender
    if sender_actual == None:
      if self.key_pair:
        sender_actual = f'k:{self.key_pair.get_pub_key()}'
      else:
        # If we have no sender, just use an empty sender.
        sender_actual = ''

    signers_actual = signers
    if signers == None:
      if self.key_pair:
        signers_actual = [{ "pubKey": self.key_pair.get_pub_key() }]
      else:
        signers_actual = []

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


  def send(self, cmds: dict):
    """Commits a list of commands to the Kadena network.
    Each command is an object created via build_command.
    Uses the chainId from the command to determine which chain to commit to.
    
    cmds must be in the format:
    {
      "0": command,
      "1": command,
      ...
    }
    """
    ret = {}

    for command in cmds.values():
      cmd_json = json.dumps(command)
      hash_code, sig = self.hash_and_sign(cmd_json)
    
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
  
  
  def local(self, cmds: dict):
    """Locally (dirty) reads from Kadena using a list of commands.
    Each command is an object created via build_command.
    Uses the chainId from the command to determine which chain to read from.
    
    cmds must be in the format:
    {
      "0": command,
      "1": command,
      ...
    }
    """
    ret = {}

    for command in cmds.values():
      cmd_json = json.dumps(command)
      hash_code, sig = self.hash_and_sign(cmd_json)

      sigs = [] if sig is None else [{'sig': sig}]
    
      to_post = {
        'hash': hash_code,
        'sigs': sigs,
        'cmd': cmd_json,
      }

      chain_id = command['meta']['chainId']
      ret[chain_id] = requests.post(
        self.build_url(self.LOCAL, command['meta']['chainId']), 
        json=to_post)

    return ret
  

  def run_pact(self, pact_code: str, env_data: dict={}, chain_id: str='0'):
    """Runs a pact code string on the Kadena network.
    Returns a dict with the results of the local run."""
    
    payload = self.build_exec_payload(pact_code, env_data)

    return self.local(self.build_command(payload, ['0']))['0'].json()['result']


  def listen(self, tx_id: str, chain_id: list):
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
    return self.listen(tx_id, chain_id)
  

  def build_url(self, endpoint, chain_id):
    """Builds a url for a given endpoint and chain_id"""
    url = f'{self.base_url}/chainweb/0.0/{self.network_id}/chain/{chain_id}/pact/api/v1{endpoint}'
    return url


  def hash_and_sign(self, command_json):
    """Signs a command with the private key of the locally stored 
    KeyPair instance."""
    bhash = blake_hash(command_json)
    sig = None

    if self.key_pair:
      sig = sign(bhash, self.key_pair.get_priv_key())

    return bhash, sig
    
  

  def set_key_pair(self, key_pair: KeyPair):
    self.key_pair = key_pair