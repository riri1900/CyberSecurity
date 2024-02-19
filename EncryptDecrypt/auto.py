
from random import randint
import subprocess
import sys

def decrypt_byte(y, n, ind, decrypt_block):

    # Generate a random block r with 15 random bytes.
    r_block = bytearray()
    for i in range(0, 16):
        r_block.append(randint(0, 255))
    r_block[ind - 1] = 0
    
    for i in range(ind, 16):
        xor = decrypt_block[i] ^ (ind-1) ^ (y[n-2][i]) 
        r_block[i] = xor
    
    # Ask the padding oracle if (r|y_n) is valid
    output = 0
    valid = r_block + y[n-1]
    while not output:
        f = open("blockByte", "wb")
        f.write(valid)
        f.close()
        # Checking with padding oracle.
        output = int(subprocess.check_output(['python3', 'oracle.py', 'blockByte']))
        # if oracle returned yes.
        if output:      
            break
        valid[ind - 1] += 1
    i = valid[ind - 1]
    
    if ind == 16:   # y needs to be at 16 bytes
        k = 1
        while k < (ind - 1):    # if the new (r|y_n) has valid padding
            # replacing r
            valid[k-1] = randint(0,255)
            f = open("blockByte", "wb")
            f.write(valid)
            f.close()
            output = int(subprocess.check_output(['python3', 'oracle.py', 'blockByte']))

            # if no valid padding (finished replacing) break the loop
            if not output:
                break
            k += 1
        

        if k == 15:     # if oracle returned yes then D(y_n) = i XOR 15
            d_fcn = i ^ 15
        else:       # if the oracle returned no then D(y_n) = i XOR k-1
            d_fcn = i ^ (k-1)
        
        # the final byte of x_n = D(y_n) XOR y_(n-1,16)
        x = d_fcn ^ (y[n-2][ind - 1])
        return x
    else:
        k = ind
        d_fcn = i ^ (k-1)
        x = d_fcn ^ (y[n-2][ind - 1])
        return x

# Returns a byte string
def byteString(a):
    s = ""
    for i in range(0, len(a)):
        s += chr(a[i])
    return s
    
if __name__ == '__main__' :

    y = open(sys.argv[1], "rb")
    y = y.read()

    n = len(y) // 16
    y = [y[i:i+16] for i in range(0, len(y), 16)]

    decrypt_str = ""
    for j in range(n, 1, -1):
        byte_block = [0 for i in range(0,16)]
        for k in range(16,0,-1):
            byte_block[k-1] = decrypt_byte(y, j, k, byte_block)
        decrypt_str = byteString(byte_block) + decrypt_str    

    print(decrypt_str)

    decrypted_file = open("decrypt_result", "w")
    decrypted_file.write(decrypt_str)
    decrypted_file.close()