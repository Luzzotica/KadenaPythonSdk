import pytest

from kadena_sdk import KadenaSdk, KeyPair

@pytest.fixture
def key_pair():
  key_pair = KeyPair(type='json', 
    priv_key='5e8b125c89ed409f2cfcc6e863e8aafd60b9d80a4d2333a12592f7a961a62bf8',
    pub_key='ad273a54460305767e2e36f41d1a5fe78c48474a6e3bc18624d53fbbbb5974bb')
  return key_pair

@pytest.fixture
def kadena(key_pair):
  kadena = KadenaSdk(key_pair=key_pair)
  return kadena

@pytest.fixture
def kadena_no_keys():
  kadena_no_keys = KadenaSdk()
  return kadena_no_keys

@pytest.fixture
def payload_hello():
  payload = {
    "exec": {
      "data": {},
      "code": '(format "Test {}" ["hello"])'
    }
  }
  return payload

def test_keypair(key_pair):
  assert(key_pair.get_pub_key() == 'ad273a54460305767e2e36f41d1a5fe78c48474a6e3bc18624d53fbbbb5974bb')
  assert(key_pair.get_priv_key() == '5e8b125c89ed409f2cfcc6e863e8aafd60b9d80a4d2333a12592f7a961a62bf8')

def test_build_command(kadena: KadenaSdk, payload_hello: dict):
  chain_ids = ['0', '1']
  cmds = kadena.build_command(payload_hello, chain_ids)

  for c in chain_ids:
    assert(cmds[c]['networkId'] == 'testnet04')
    assert(cmds[c]['payload'] == payload_hello)
    assert(cmds[c]['signers'][0]['pubKey'] == 'ad273a54460305767e2e36f41d1a5fe78c48474a6e3bc18624d53fbbbb5974bb')
    assert(cmds[c]['meta']['gasLimit'] == 2500)
    assert(cmds[c]['meta']['chainId'] == c)
    assert(cmds[c]['meta']['gasPrice'] == 1.0e-5)
    assert(cmds[c]['meta']['sender'] == 'k:ad273a54460305767e2e36f41d1a5fe78c48474a6e3bc18624d53fbbbb5974bb')
    assert(cmds[c]['meta']['ttl'] == 28000)

def test_local(kadena: KadenaSdk, kadena_no_keys: KadenaSdk, payload_hello: dict):
  chain_ids = ['0', '1']
  cmds = kadena.build_command(payload_hello, chain_ids)
  res = kadena.local(cmds)
  assert(res['0'].json()['result']['data'] == 'Test hello')
  assert(res['1'].json()['result']['data'] == 'Test hello')

  cmds = kadena_no_keys.build_command(payload_hello, chain_ids)
  res = kadena_no_keys.local(cmds)
  assert(kadena_no_keys.key_pair is None)
  assert(res['0'].json()['result']['data'] == 'Test hello')
  assert(res['1'].json()['result']['data'] == 'Test hello')

def text_run_pact(kadena_no_keys: KadenaSdk):
  res = kadena_no_keys.run_pact(
    '(format "Test {}" [(read-msg "test")])', 
    env_data={'test': 'hello'}
  )
  assert(res == 'Test hello')
