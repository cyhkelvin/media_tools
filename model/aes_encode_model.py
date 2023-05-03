# reference https://segmentfault.com/a/1190000022528654
import torch
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from io import BytesIO


# 如果byte_string不足16位的倍数就用空格补足为16位
def add_to_16(byte_string):
    if len(byte_string) % 16:
        add = 16 - (len(byte_string) % 16)
    else:
        add = 0
    byte_string = byte_string + (b'\0' * add)
    return byte_string


key = '0123456789abcdef'.encode('utf-8')
mode = AES.MODE_CBC
iv = b'qqqqqqqqqqqqqqqq'



# 加密函数
def Encrypt(byte_string):
    byte_string = add_to_16(byte_string)
    cryptos = AES.new(key, mode, iv)
    cipher_text = cryptos.encrypt(byte_string)
    # 因为AES加密后的字符串不一定是ascii字符集的，输出保存可能存在问题，所以这里转为16进制字符串
    return b2a_hex(cipher_text)


# 解密后，去掉补足的空格用strip() 去掉
def Decrypt(byte_string):
    cryptos = AES.new(key, mode, iv)
    plain_text = cryptos.decrypt(a2b_hex(byte_string))
    return plain_text.rstrip(b'\0')


if __name__ == '__main__':
    #测试向量
    net='./yolov5s.pt'
    load_net = torch.load(net)
    # prevent error of: PytorchStreamReader failed reading zip archive: failed finding central directory
    # https://discuss.pytorch.org/t/error-on-torch-load-pytorchstreamreader-failed/95103/18
    torch.save(load_net, 'tmp.model', _use_new_zipfile_serialization=False)
    
    #加密&写加密文件
    with open('tmp.model','rb') as f1:
        encrypted=Encrypt(f1.read())
        with open('model-encrypted','wb') as f2:
            f2.write(encrypted)

    #解密 加密过的文件
    with open('model-decrypted','wb') as f:
        content=open('model-encrypted','rb').read()
        f.write(Decrypt(content))

    content=open('model-encrypted', 'rb').read()
    de_content = BytesIO(Decrypt(content))
    test = torch.load(de_content)
    print(test)

    # #load原本model
    # net1=torch.load(net)
    # #load解密后的model
    # net2=torch.load('model-decrypted')
