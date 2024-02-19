from random import randint
import subprocess
import sys

def check_padding_oracle():
    r_Yn = read_file("randYn")
    write_file(r_Yn)
    valid = int(subprocess.check_output(['python3', 'oracle.py', 'randYn']))
    return valid

def write_file(r_Yn):
    f = open("randYn", "wb")
    f.write(r_Yn)
    f.close()

def decrypt_byte(r, y):
    i = 0
    r_Yn = r + y
    write_file(r_Yn)
    while check_padding_oracle() == 0:
        write_file(r_Yn)
        i += 1
        r_Yn = r_Yn[:-1] + bytes([i])
    D = i ^ 15
    return D ^ y[-1]

def decrypt_block(y, y_prev):
    x = bytearray(len(y))
    for k in range(len(y) - 1, -1, -1):
        r = bytearray([0] * (k + 1)) + y[k + 1:] + y_prev[k + 1:]
        i = 0
        r_Yn = r + y;
        write_file(r_Yn)
        while check_padding_oracle == 0:
            write_file(r_Yn)
            i += 1
            r_Yn[k] = i ^ (k + 1)
        D = i ^ k
        x[k] = D ^ y_prev[k]
    return bytes(x)

def decrypt(ciphertext):
    iv = ciphertext[:16]
    blocks = [ciphertext[i:i+16] for i in range(16, len(ciphertext), 16)]
    y_prev = iv
    plaintext=[]
    for y in blocks:
        x = decrypt_block(y, y_prev)
        plaintext.extend(x)
        y_prev = y
    return plaintext

# Read ciphertext from file
file_path = sys.argv[1]
with open(file_path, "rb") as file:
    ciphertext = file.read()

plaintext = decrypt(ciphertext)
plaintext = ''.join(chr(byte) for byte in plaintext)
print(plaintext)
