from random import randint
import subprocess
import sys


def decrypt_byte(y, n, ind, decrypt_block):

    random_block = bytearray()
    for i in range(0, 15):
        random_block.append(randint(0, 10))
    random_block.append(0)

    for i in range(ind, 16):
        xor = decrypt_block[i] ^ (ind-1) ^ (y[n-2][i])
        random_block[i] = xor

    valid = 0
    r_Yn = random_block + y[n-1]
    write_file(r_Yn)

    while valid == 0:
        write_file(r_Yn)
        valid = int(subprocess.check_output(['python3', 'oracle.py', 'randYn']))
        if valid == 1:
            break
        else:
            r_Yn[ind - 1] += 1

    i = r_Yn[ind - 1]

    j = 1
    if ind == 16:
        while j < ind - 1:
            r_Yn[j - 1] = randint(0, 255)
            write_file(r_Yn)
            valid_n = int(subprocess.check_output(['python3', 'oracle.py', 'randYn']))
            if valid_n == 0:
                break
            else:
                j = j + 1

        if j == 15:
            D_yn = i ^ 15
        else:
            D_yn = i ^ (j - 1)

        Xn = D_yn ^ y[n-2][ind - 1]
        return Xn
    else:

        D_yn = i ^ (ind - 1)
        Xn = D_yn ^ y[n-2][ind - 1]
        return Xn


def write_file(r_Yn):
    f = open("randYn", "wb")
    f.write(r_Yn)
    f.close()


def main():
    f = open(sys.argv[1], "rb")
    Cipher = f.read()
    cipher_block_count = len(Cipher) // 16
    Yn = []
    block = []
    for i in range(0, len(Cipher), 16):
        Yn.append(Cipher[i:i+16])
    temp_str = ""
    decrypt_s = ""
    cipher_block = cipher_block_count
    while cipher_block >=1:
        block = [0]*16
        for ind in range(16, 0, -1):
            temp = decrypt_byte(Yn, cipher_block, ind, block)
            block[ind - 1] = temp
        decrypt_s = ''.join(chr(byte) for byte in block) + decrypt_s
        cipher_block-=1

    print(decrypt_s)

    plaintext = open("Plaintext", "w")
    plaintext.write(decrypt_s)
    plaintext.close()


if __name__ == '__main__':
    main()
