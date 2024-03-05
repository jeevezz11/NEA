# Version 0.10 for Linux #

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
import os

def regenerate_keys(private_key_path, public_key_path, receipts_directory):

    private_key = rsa.generate_private_key( # generates the private key
        public_exponent=65537,# default value reccomended by docs for its mathematical properties
        key_size=2048, # the size of the key in bits 
        backend=default_backend()) # default backend provided by the cryptography library

    public_key = private_key.public_key() # uses the private key to make a corresponding public key

    with open(private_key_path, 'wb') as private_key_file: # stores the new private key
        private_key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM, # uses the .pem file format to store the key
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_key_path, 'wb') as public_key_file: # the same is done for the public key using the same .pem file format
        public_key_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    sign_files_in_receipts_directory(private_key_path, receipts_directory) # re signs every receipt in the receipts folder provided with the new private key 

def sign_files_in_receipts_directory(private_key_path, receipts_directory):

    private_key = load_key_from_pem_file(private_key_path, True) # function that is defined later on in this script to load the keys from their .pem format

    for date_folder in os.listdir(receipts_directory): # lists every folder in the given receipts directory
        date_folder_path = os.path.join(receipts_directory, date_folder)

        if os.path.isdir(date_folder_path): 
            signatures_folder = os.path.join(date_folder_path, 'signatures') # creates a folder called signatures in each date folder to store the receipts' signatures for that day
            os.makedirs(signatures_folder, exist_ok=True) # doesn't crash if the folder already exists and just continues as normal

            for file_name in os.listdir(date_folder_path): # lists the files within each date folder now
                if file_name.endswith(".txt"): # if they're a text file which is the format receipts are stored in
                    file_path = os.path.join(date_folder_path, file_name)

                    signature = sign_file(private_key_path, file_path) # use the sign file function on the file (defined later in this script) to generate the signature

                    signature_file_path = os.path.join(signatures_folder, file_name + '.signature') # create the signature file for the file that has just been signed
                    save_signature(signature, signature_file_path) # use the save signature function (also defined later in this script) to store the signature file in the signature folder

def save_signature(signature, signature_file_path): # will be passed these parameters
    
    try:
        with open(signature_file_path, 'wb') as signature_file: # adds the signature that has been passed to it to the file path it has been passed and saves it
            signature_file.write(signature)

        return True # returns true if saving the signature was successful
    except:
        return False # otherwise will return false if there was an issue


def sign_file(private_key_path, file_path):

    private_key = load_key_from_pem_file(private_key_path, True) # loads the private key from the path provided

    with open(file_path, 'rb') as file: 
        file_content = file.read() # saves content of the file to a variable

    signature = private_key.sign( # uses the built in sign function on the file content 
        file_content,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), # uses mask generation function 1 (MGF1) as this default and is configured to use the SHA256 hashing algorithm
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature # it then returns the signature that has been created which can be used to make a signature file

def read_signature_from_file(signature_file_path):

    with open(signature_file_path, 'rb') as signature_file: # opens a specified signature file path
        signature = signature_file.read() # saves its content to a variable
        
    return signature # returns the signature 

def verify_file(public_key_file_path, file_path, signature_file_path):
    
    try:
        signature = read_signature_from_file(signature_file_path) # get the signature from the given path
    except:
        return False # if there's an error retrieving this signature it will return false and the system is unable to verify the file
    public_key = load_key_from_pem_file(public_key_file_path, False) # loads the public key from the given path

    try:
        with open(file_path, 'rb') as file:
            file_content = file.read() # saves the content from the file that is being verified to a variable
    except Exception as e:
        return False

    try:
        public_key.verify( # it then uses the built in verify function using the public key from the public key path
            signature, # the signature from the signature path
            file_content, # and the content from the file that is being verified
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True # if it verifies with no issues the system can confirm its integrity 
    except:
        return False # if there is any issues during this process it will return false and the system can't verify the file

def load_key_from_pem_file(file_path, is_private): # the key file path and wether the key you are trying to load is private or not are given to this function. The process to load a private key and a public key are slightly different so the script needs to be made aware of wether it is trying to load a private or public key

    with open(file_path, 'rb') as file: 
        pem_data = file.read() # saves the file data to a variable
    if is_private:
        key = serialization.load_pem_private_key( # uses the private key load function if is_private is true
            pem_data,
            password=None, 
            backend=default_backend()
        )
    else: # otherwise uses the public key load function
        key = serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )

    return key # returns the key that has been loaded


