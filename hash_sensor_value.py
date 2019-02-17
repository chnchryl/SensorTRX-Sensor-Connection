import ethereum
from web3 import Web3
import math

# private key for sensor, used to determine public address and sign messages
privKeyHex = 'cf749dfd3f6b985ed17acbd528402f28ebfd0bf166da541470ec1876ee963a40'

def get_signed_data(value, time):

    # multiply pH by 10 and trunc the decimals for saving on blockchain, because 
    # float point numbers are not supported by solidity contracts
    int_value = int(math.trunc(value * 10))
    hash_data_bytes = Web3.soliditySha3(['uint8', 'uint256'], [int_value, time])
    hash_data = ethereum.utils.encode_hex(hash_data_bytes)
    hash_string = '0x' + hash_data
    privkey = bytearray.fromhex(privKeyHex)

    prefix = bytes('\u0019Ethereum Signed Message:\n' + str(len(hash_data_bytes)), 'utf-8')
    message = prefix + hash_data_bytes
    data = ethereum.utils.sha3(message)

    vrs = ethereum.utils.ecsign(data, privkey)
    signer = ethereum.utils.encode_hex(ethereum.utils.privtoaddr(privKeyHex))

    ret = {}
    ret['v'] = '0x' + str(ethereum.utils.encode_hex(ethereum.utils.encode_int(vrs[0])))
    ret['r'] = '0x' + str(ethereum.utils.encode_hex(ethereum.utils.encode_int(vrs[1])))
    ret['s'] = '0x' + str(ethereum.utils.encode_hex(ethereum.utils.encode_int(vrs[2])))
    ret['msgHash'] = '0x' + str(hash_data)
    ret['value'] = value
    ret['time'] = time
    ret['signer'] = ethereum.utils.encode_hex(ethereum.utils.privtoaddr(privKeyHex))
    return ret
