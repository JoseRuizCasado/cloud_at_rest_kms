import base64
import json

import requests
from cryptography.fernet import Fernet
import click
import os
import pandas as pd


server_address = 'http://127.0.0.1:8000'


@click.group()
def files():
    pass


@click.command(name='encrypt-file')
@click.argument('file', type=str, nargs=1)
@click.argument('output_file', type=str, nargs=1)
def encrypt_file(file, output_file):
    key = Fernet.generate_key()
    fernet_key = Fernet(key)

    with open(file, 'rb') as file_to_encrypt:
        content = file_to_encrypt.read()

    encrypted_content = fernet_key.encrypt(content)

    response = requests.get('http://127.0.0.1:8081/wrapped-key/' + key.decode()).content.decode()
    json_res = json.loads(response)
    WDEK = json_res['DEK'].encode()

    with open(output_file, 'wb') as file_to_save:
        file_to_save.write(encrypted_content)

    d = {'FILE': [output_file], 'DEK': [WDEK.decode()]}
    df = pd.DataFrame(data=d)
    df.to_csv('bd.csv', mode='a', header=False)


@click.command(name='get_file')
@click.argument('file', type=str, nargs=1)
@click.argument('user', type=str, nargs=1)
def get_file(file, user):
    password = click.prompt(f'Please enter {user} password', type=str, hide_input=True)
    # TODO: Comprobar contraseña
    response = requests.get(f'{server_address}/download-file/{file}/{user}')
    try:
        os.mkdir(f'./files/{user}')
    except:
        pass

    with open(f'files/{user}/{file}', 'w') as file_to_save:
        file_to_save.write(response.content.decode('UTF-8'))

    click.echo(f'File saved to files/{user}/{file}')


files.add_command(get_file)
files.add_command(encrypt_file)

if __name__ == '__main__':
    files()
