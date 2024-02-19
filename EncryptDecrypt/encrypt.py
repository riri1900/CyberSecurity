from random import randint
import subprocess
import sys

# Checking if the padding oracle returns 1
def check_padding_oracle(ciphertext):
    with open("ciphertext", "wb") as f:
        f.write(ciphertext)
    valid = int(subprocess.check_output(['python3', 'oracle.py', 'ciphertext']))
    return valid

# Writing random_block+Yn to the file
def write_file(r_Yn):
    with open("randYn", "wb") as f:
        f.write(r_Yn)

def decrypt_block(Yn, Cipher_block, index, Decrypt_yn):
    Cipher_block = Cipher_block-1
    index = index-1

    random_block = bytearray()
    for i in range(0, 16):
        random_block.append(randint(0, 10))
    random_block[index] = 0
    i = random_block[index]

    for i in range(index+1, 16):
        random_block[i] = Decrypt_yn[i] ^ (index)     

    r_Yn = random_block + Yn[Cipher_block]
    write_file(r_Yn)

    valid = 0
    while valid == 0:
        write_file(r_Yn)
        valid = check_padding_oracle(r_Yn)
        if valid == 0:
            r_Yn[index] += 1
        else:
            break

    i = r_Yn[index]
    
    if index == 16 :
        final_byte, D_yn = get_final_byte(Yn, Cipher_block, index, r_Yn, i)
        return final_byte, D_yn
    else:
        D_yn = i ^ (index)
        Xn = D_yn ^ Yn[Cipher_block - 1][index]
        return Xn, D_yn

# Finding the final byte
def get_final_byte(Yn, Cipher_block, index, r_Yn, i):
    for k in range(1, index, +1):
        r_Yn[k - 1] = randint(0, 10)
        write_file(r_Yn)
        if check_padding_oracle(r_Yn) == 0:
            break
    if k == 15:
        D_yn = i ^ 15
    else:
        D_yn = i ^ (k - 1)

    Xn = D_yn ^ Yn[Cipher_block - 1][index]
    return Xn, D_yn

def decrypt(ciphertext):
    Cipher_block_count = len(ciphertext) // 16
    Yn = []

    for i in range(0, len(ciphertext), 16):
        Yn.append(ciphertext[i:i + 16])

    decrypt_st = ""

    for Cipher_block in range(Cipher_block_count, 1, -1):
        blocks = [0] * 16
        Decrypt_yn = [0] * 16

        for index in range(16, 0, -1):
            temp, Decrypt_yn[index-1] = decrypt_block(Yn, Cipher_block, index, Decrypt_yn)
            blocks[index - 1] = temp

        st = ''.join(chr(byte) for byte in blocks)
        decrypt_st = st + decrypt_st

    return decrypt_st


plaintext = sys.argv[1]

# Encrypt plaintext
iv = bytearray(randint(0, 10) for i in range(16))
ciphertext = iv

for i in range(0, len(plaintext), 16):
    block = plaintext[i:i + 16].encode()
    ciphertext += bytearray(decrypt(block), 'utf-8')

# Print ciphertext and IV
ciphertext = iv.hex() + '|' + ciphertext.hex()
ciphertext_f = open("Ciphertext_encrypt", "w")
ciphertext_f.write(ciphertext)
ciphertext_f.close()
