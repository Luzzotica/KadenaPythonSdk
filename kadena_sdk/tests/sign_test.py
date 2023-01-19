from kadena_sdk.signing import hash_and_sign

def test_sign_message():
    # 09dbbe2d2caf283a5da170cc438eed631b5898b921512cae8720232313483a3e
    private_key = '1de84cf16631a778317e1c33a6b729875734c129b0094e809713b7225fd3dfb7'
    message = "Hello, World!"
    hash_code, sig = hash_and_sign(message, private_key)
    assert(hash_code == 'URvIHd4RGAg4xWLIK7NfMiP0YGHr3kqVXCez9InPHgM')
    assert(sig == '756ec1891523f56369c98bf2544a2f91033de9cea53773d7cc4d7812babd9a1d0ab03b706e628bd1636fb5d65083711ba6584bf6ffe471a48657e6a571031306')

    print(hash_code, sig)

