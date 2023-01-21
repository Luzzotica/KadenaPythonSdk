# To Use

```python
from kadena_sdk import KadenaSdk, KeyPair

# Create your keypair and setup the SDK with the endpoint you desire in life.
key_pair = KeyPair(type='json',
  priv_key='5e8b125c89ed409f2cfcc6e863e8aafd60b9d80a4d2333a12592f7a961a62bf8',
  pub_key='ad273a54460305767e2e36f41d1a5fe78c48474a6e3bc18624d53fbbbb5974bb')

# base_url will default to https://api.testnet.chainweb.com
# KeyPair isn't required, but no sigs will be included in any local/send calls
kadena = KadenaSdk(base_url='https://api.chainweb.com',
  key_pair=key_pair)

# Very open ended: Work directly with the payload.
payload = kadena.build_exec_payload(
  '(format "{}" [(read-msg "test")])', 
  env_data={'test': 'hello'}
)

# SDK works with whichever chains you choose!
chain_ids = ['0', '1']

# Commands is a dictionary where each key is the chain id and the value
# is the command to be sent
cmds = kadena.build_command(payload, chain_ids)

# You can use local or send to dirty read or commit respectively.
# These are the /local and /send endpoints.
res = kadena.local(cmds)

# Responses are in a dictionary with keys being the chains 
# that were interacted with
print(res['0'].json())

# You can also listen to commands. This is a blocking command.
# Pass in the transaction id and the chain you want to listen on.
kadena.listen('tx_id', '0')

## Lastly, if you want to just run some pact code, you can do so
res = kadena.run_pact(
  '(format "Test {}" [(read-msg "test")])', 
  env_data={'test': 'hello'}
)
```

# To Build and Deploy

```bash
python3 -m build
python3 -m twine upload dist/*
```

# To Test

`pytest`