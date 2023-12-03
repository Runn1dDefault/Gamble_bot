import os
import zipfile

from config import PLUGINS_DIR


def proxy_zip_completing(plugin_name: str, host: str, port: int, user: str, pwd: str) -> None:
    with open(os.path.join(PLUGINS_DIR, 'manifest.json')) as file:
        manifest_json = file.read()

    with open(os.path.join(PLUGINS_DIR, 'background.js')) as file:
        background_js = file.read() % (host, port, user, pwd)

    filepath = os.path.join(PLUGINS_DIR, plugin_name + '.zip')

    with zipfile.ZipFile(filepath, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)


if __name__ == '__main__':
    proxy_zip_completing(
        plugin_name='',
        host='',
        port=123,
        user='',
        pwd=''
    )
