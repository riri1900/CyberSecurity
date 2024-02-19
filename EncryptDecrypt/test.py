from random import randint
import subprocess
import sys

#Checking if the padding oracle returns 1
def checking_padding_oracle():
    valid = int(subprocess.check_output(['python3', 'oracle.py', 'randYn']))
    return valid

#writing random_block+Yn to the file
def write_file(r_Yn):
    with open("randYn", "wb") as f:
        f.write(r_Yn)


def decrypt_block(Yn, Cipher_block, index, Decrypt_yn):
    Cipher_block = Cipher_block-1
    index = index-1

    #creating the random block
    random_block = bytearray()
    for i in range(0, 16):
        random_block.append(randint(0, 10))
    random_block[index]=0
    i= random_block[index]

    #r = (r1|r2| . . . |rkâˆ’1|i|D(y)k+1 âŠ•(k âˆ’1)|D(y)k+2 âŠ•(k âˆ’1)| . . . |D(y)16 âŠ•(k âˆ’1)).

    for i in range(index+1, 16):
        random_block[i]= Decrypt_yn[i] ^ (index)    
         
    #r|Yn = r + Yn
    r_Yn = random_block + Yn[Cipher_block]
    write_file(r_Yn)

    valid=0
    while valid == 0:
        write_file(r_Yn)
        valid = checking_padding_oracle()
        if valid ==0:
            r_Yn[index] += 1
        else:
            break

    i = r_Yn[index]
    #checking if last byte
    if index == 16 :
        final_byte,D_yn = get_final_byte(Yn, Cipher_block, index, r_Yn, i)
        return final_byte, D_yn
    else:
        D_yn = i ^ (index)
        Xn = D_yn ^ Yn[Cipher_block - 1][index]
        return Xn,D_yn

#decrypt the final byte
def get_final_byte(Yn, Cipher_block, index, r_Yn, i):
    for k in range(1, index, +1):
        r_Yn[k - 1] = randint(0, 10)
        write_file(r_Yn)
        if checking_padding_oracle() == 0:
            break
    if k == 15:
        D_yn = i ^ 15
    else:
        D_yn = i ^ (k - 1)

    Xn = D_yn ^ Yn[Cipher_block - 1][index]
    return Xn, D_yn


def decrypt(ciphertext):
    Yn = []

    #ciphertext into blocks of 16bytes each
    for i in range(0, len(ciphertext), 16):
        Yn.append(ciphertext[i:i + 16])

    #number of blocks
    Cipher_block_count = len(Yn)

    decrypt_st = ""
    st=""
    #print(Cipher_block_count)
    for Cipher_block in range(Cipher_block_count,1,-1):
        blocks = [0] * 16
        Decrypt_yn = [0]*16

        for index in range(16, 0, -1):
            temp, Decrypt_yn[index-1] = decrypt_block(Yn, Cipher_block, index, Decrypt_yn)
            blocks[index -1] = temp
        
        #print(len(blocks))
        st = ''.join(chr(b) for b in blocks)
        decrypt_st = st + decrypt_st

    return decrypt_st


# Read ciphertext from file
file_path = sys.argv[1]
with open(file_path, "rb") as file:
    ciphertext = file.read()

plaintext = decrypt(ciphertext)
print(plaintext)
plaintext_f = open("Plaintext", "w")
plaintext_f.write(plaintext)
plaintext_f.close()
