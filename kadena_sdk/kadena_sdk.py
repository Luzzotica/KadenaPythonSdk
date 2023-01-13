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

  def __init__(self, key_pair: KeyPair, base_url, network_id, chain_id):
    self.key_pair = key_pair
    self.base_url = base_url
    self.network_id = network_id
    self.chain_id = chain_id


  def build_command(self, sender, payload, signers, gas_price=1.0e-5, gas_limit=2500):
    # Create Time Stamp
    t_epoch = time.time()
    t_epoch = round(t_epoch) - 15

    command = {
      "networkId": self.network_id,
      "payload": payload,
      "signers": signers,
      "meta": {
        "gasLimit": gas_limit,
        "chainId": self.chain_id,
        "gasPrice": gas_price,
        "sender": sender,
        "ttl": 28000,
        "creationTime": t_epoch
      },
      "nonce": datetime.now().strftime("%Y%m%d%H%M%S")
    }

    return command


  def send(self, command):
    cmd_json = json.dumps(command)
    hash_code, sig = self.sign(cmd_json)
    
    cmds = {
      'cmds': [
        {
          'hash': hash_code,
          'sigs': [{'sig': sig}],
          'cmd': cmd_json,
        }
      ]
    }

    return requests.post(self.build_url(self.SEND), json=cmds)
  
  
  def local(self, command):
    cmd_json = json.dumps(command)
    hash_code, sig = self.sign(cmd_json)
    
    cmd = {
      'hash': hash_code,
      'sigs': [{'sig': sig}],
      'cmd': cmd_json,
    }

    return requests.post(self.build_url(self.LOCAL), json=cmd)
  

  def listen(self, tx_id):
    data = {
      'listen': tx_id
    }

    return requests.post(self.build_url(self.LISTEN), json=data)
  

  def send_and_listen(self, command):
    result = self.send(command)
    tx_id = result.json()['requestKeys'][0]
    print(f"Listening to tx: {tx_id}")
    return self.listen(tx_id)
  

  def build_url(self, endpoint):
    url = f'{self.base_url}/chainweb/0.0/{self.network_id}/chain/{self.chain_id}/pact/api/v1{endpoint}'
    print(url)
    return url


  def sign(self, command_json):
    return hash_and_sign(command_json, self.key_pair.get_priv_key())