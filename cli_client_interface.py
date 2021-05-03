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
@click.argument('username', type=str, nargs=1)
@click.password_option()
def encrypt_file(file, username, password):
    res = requests.get(f'{server_address}/api-login', data={'user': username, 'pass': password})
    if res.status_code == 200:
            res = requests.post(f'{server_address}/upload-file', files={'file': open(file, 'rb')})
            print(res.status_code, res.text)
    else:
        print(res.status_code, res.content)


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
