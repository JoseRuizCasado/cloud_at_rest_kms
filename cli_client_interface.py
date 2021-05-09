import json
import requests
from cryptography.fernet import Fernet
import click
import os
from make_chunks import chunk_bytes
from secure_delete import secure_delete

server_address = 'http://127.0.0.1:8000'


@click.group()
def files():
    pass


@click.command(name='encrypt_file')
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
            click.secho(f'{res.status_code}, {res.text}', fg='blue')
    else:
        click.secho(f'{res.status_code}, {res.text}', fg='red')


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
        if response:
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

                click.echo(f'File saved to ', nl=False)
                click.secho(f'files/{user}/{file}', fg='blue')
        else:
            click.secho(f'Seems like something went wrong! File not found.', fg='red')
    else:
        click.secho(res.text, fg='red')


@click.command(name='get_files')
@click.argument('user', type=str, nargs=1)
@click.password_option(help='User password. Should not be passed as an argument, instead it will be asked before execution.')
@click.option('-c', '--count', default=-1, help='Number of files to show.')
def get_files(user, password, count):
    """Get files from user

    USER should be an active user in cloud system
    """

    res = requests.get(f'{server_address}/api-login', data={'user': user, 'pass': password})
    if res.status_code == 200:
        response = requests.get(f'{server_address}/api-get-files/{user}').content.decode()
        if response:
            json_res = json.loads(response)
            click.secho(f'{user}', fg='white')
            for f in json_res:
                click.secho('|-- ', fg='white', nl=False)
                click.secho(f'{f["filename"]}', fg='blue')
        else:
            click.secho(f'Seems like something went wrong! Have you tried uploading something before?', fg='red')

    else:
        click.secho('Invalid User', fg='red')


@click.command(name='delete_file')
@click.argument('user', type=str, nargs=1)
@click.argument('file', type=str, nargs=1)
@click.password_option(help='User password. Should not be passed as an argument, instead it will be asked before execution.')
@click.option('-l', '--local', is_flag=True, default=False, help='Keep file in local.', show_default=True)
def delete_file(file, user, password, local):
    """Delete file from user

    FILE should be an uploaded file in cloud system

    USER should be an active user in cloud system
    """
    res = requests.get(f'{server_address}/api-login', data={'user': user, 'pass': password})
    if res.status_code == 200:
        res = requests.get(f'{server_address}/api-delete-file/{user}/{file}')
        if res.status_code == 200:
            click.secho(f'File deleted from ', nl=False)
            click.secho(f'Cloud', fg='blue')
        else:
            click.secho(f'File not found on cloud', fg='red')

        if not local and os.path.exists(f'files/{user}/{file}'):
            secure_delete.secure_random_seed_init()
            secure_delete.secure_delete(f'files/{user}/{file}')
            click.secho(f'File deleted from ', nl=False)
            click.secho(f'files/{user}/{file}', fg='blue')
    else:
        click.secho(res.text, fg='read')


files.add_command(get_file)
files.add_command(encrypt_file)
files.add_command(get_files)
files.add_command(delete_file)

if __name__ == '__main__':
    files()
