import json
import requests
from cryptography.fernet import Fernet
import click
import os
from make_chunks import chunk_bytes

server_address = 'http://127.0.0.1:8000'


@click.group()
def files():
    pass


@click.command(name='encrypt-file')
@click.argument('file', type=str, nargs=1)
@click.argument('username', type=str, nargs=1)
@click.password_option(help='User password. Should not be passed as an argument, instead it will be asked before execution.')
def encrypt_file(file, username, password):
    """Encrypt local file and upload it to cloud storage

    FILE should be the name of a file in the root of the directory

    USER should be an active user in cloud system"""
    res = requests.get(f'{server_address}/api-login', data={'user': username, 'pass': password})
    if res.status_code == 200:
            res = requests.post(f'{server_address}/upload-file', files={'file': open(file, 'rb')})
            print(res.status_code, res.text)
    else:
        print(res.status_code, res.content)


@click.command(name='get_file')
@click.argument('file', type=str, nargs=1)
@click.argument('user', type=str, nargs=1)
@click.password_option(help='User password. Should not be passed as an argument, instead it will be asked before execution.')
@click.option('-r', '--read', is_flag=True, default=False, help='Shows file content in command prompt.', show_default=True)
def get_file(file, user, password, read):
    """Get file from user

    FILE should be an uploaded file in cloud system

    USER should be an active user in cloud system
    """
    res = requests.get(f'{server_address}/api-login', data={'user': user, 'pass': password})
    if res.status_code == 200:
        response = requests.get(f'{server_address}/api-get-file/{file}/{user}').content.decode()
        json_res = json.loads(response)
        WDEK = json_res['WDEK']
        kms_response = requests.get(url=f'http://127.0.0.1:8081/get-key/{WDEK}').content.decode()
        json_kms_res = json.loads(kms_response)
        fernet_key = Fernet(json_kms_res['DEK'])
        chunked_content = chunk_bytes(size=440, source=json_res['File'].encode())
        content = b''
        for chunk in chunked_content:
            content += fernet_key.decrypt(chunk)

        end = int.from_bytes(content.strip()[-1:], 'big')
        content = content.strip()[:-end]
        if read:
            click.echo(content)
        else:
            try:
                os.makedirs(f'./files/{user}', exist_ok=True)
            except Exception as e:
                print(e)

            with open(f'./files/{user}/{file}', 'w+') as file_to_save:
                file_to_save.write(content.decode('UTF-8'))

            click.echo(f'File saved to files/{user}/{file}')
    else:
        click.echo(res.text)


@click.command(name='get_files')
@click.argument('user', type=str, nargs=1)
@click.password_option(help='User password. Should not be passed as an argument, instead it will be asked before execution.')
@click.option('-c', '--count', default=-1, help='Number of files to show.')
def get_files(user, password, count):
    """Get files from user

    USER should be an active user in cloud system
    """
    res = requests.get(f'{server_address}/api-login', data={'user': user, 'pass': password})
    colors = ['red']
    if res.status_code == 200:
        response = requests.get(f'{server_address}/api-get-files/{user}').content.decode()
        json_res = json.loads(response)
        click.secho(f'{user}', fg='white')
        for f in json_res:
            click.secho('|-- ', fg='white', nl=False)
            click.secho(f'{f["filename"]}', fg='blue')

    else:
        click.secho('Invalid User', fg='red')


files.add_command(get_file)
files.add_command(encrypt_file)
files.add_command(get_files)

if __name__ == '__main__':
    files()
