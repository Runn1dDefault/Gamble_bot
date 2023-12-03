import os
import re
import subprocess

import zipfile
import platform
from sys import platform as _platform

import requests
import threading

from selenium.webdriver import Chrome
from parsel.selector import Selector
from urllib.parse import urlparse

from config import CHROMEDRIVER_DOWNLOADS_URL
from service.utils import get_chromedriver_path
from service.logger import Logger


try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = os.open(os.devnull, os.O_RDWR)


class ChromedriverUpdaterThread(threading.Thread):

    def __init__(self, logger: Logger):
        # Initialization thread designed to track and record advertising
        threading.Thread.__init__(self)
        self._logger = logger
        self._chromedriver_path = ''
        self._chromedriver_version = ''
        self._chrome_path = ''
        self._chrome_version = ''

    def run(self) -> None:
        # Function that runs the process of tracking advertising (start and end)
        self._logger.info('Starting thread %s.' % self.__class__)
        self._chromedriver_updater()
        self._logger.info('Finished thread %s.' % self.__class__)

    def _chromedriver_updater(self):
        self._chromedriver_path = get_chromedriver_path()
        self._chromedriver_version = self._get_chromedriver_version()
        self._chrome_path = self._get_chrome_path()
        self._chrome_version = self._get_chrome_version()
        self._logger.info(f'Installed Chrome {self._chrome_version} and chromedriver {self._chromedriver_version}')
        self._update_chromedriver(chrome_version=self._chrome_version, chromedriver_version=self._chromedriver_version)

    def _get_chromedriver_version(self):
        return self._get_version_with_version(path_file=self._chromedriver_path)

    def _get_chrome_path(self):
        _chrome_path = ''
        if _platform == "win32" or _platform == "win64":
            _chrome_path = self._path_chrome_from_windows_registry('chrome')
        elif _platform == "darwin":
            _chrome_path = self._path_chrome_mac()
        elif _platform == "linux" or _platform == "linux2":
            _chrome_path = self._path_chrome_linux()
        return _chrome_path

    def _get_chrome_version(self):
        _chrome_version = ''
        if _platform == "win32" or _platform == "win64":
            _chrome_version = self._get_version_with_wmic_datafile(path_file=self._chrome_path)
        elif _platform == "darwin":
            _chrome_version = self._get_version_with_plist_datafile()
        elif _platform == "linux" or _platform == "linux2":
            _chrome_version = self._get_version_chrome_for_linux()
        return _chrome_version

    def _path_chrome_from_windows_registry(self, program_name: str) -> str:
        import winreg
        sub_key = fr"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{program_name}.exe"
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm_hive:
            try:
                with winreg.OpenKey(hklm_hive, sub_key, 0, winreg.KEY_READ) as key:
                    path_chrome = winreg.QueryValue(key, '')
                    self._logger.info(f'Program {program_name}. Path to program {path_chrome} from Windows Registry')
            except FileNotFoundError:
                self._logger.error(f'Program {program_name}. Key {sub_key} not found in Windows Registry')
        return path_chrome

    @staticmethod
    def _path_chrome_mac() -> str:
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    @staticmethod
    def _path_chrome_linux() -> str:
        cmd = 'which'
        program_name = 'google-chrome-stable'
        path_chrome = subprocess.check_output(f'{cmd} {program_name}', shell=True).decode('utf-8').rstrip()
        return path_chrome

    def _get_windows_program_files(self) -> dict:
        program_files_dirs = {}
        if os.environ["PROGRAMFILES"]:
            program_files_dirs['x64'] = os.environ["PROGRAMFILES"]
            self._logger.info(f'Folder Program files for Windows is located {program_files_dirs["x64"]}')
        if os.environ.get("PROGRAMFILES(X86)"):
            program_files_dirs['x86'] = os.environ.get("PROGRAMFILES(X86)")
            self._logger.info(f'Folder Program files for Windows is located {program_files_dirs["x86"]}')
        return program_files_dirs

    def _path_chrome_from_windows_program_files_dir(self, program_name: str) -> str:
        dirs_tuple = self._get_windows_program_files()
        path_chrome = ''
        if platform.system() == "Windows":
            cmd = "where /r"
            for folder in dirs_tuple.values():
                try:
                    path_chrome = subprocess.check_output(f'{cmd} "{folder}" {program_name}.exe', shell=True)\
                                            .decode('utf-8')
                    path_chrome = path_chrome.replace('\n', '').replace('\r', '')

                    self._logger.info(
                        f'Program {program_name}. Path to program {path_chrome} from search in folder {folder}'
                    )
                except subprocess.CalledProcessError:
                    self._logger.error(f'Program {program_name}. Program {path_chrome} not found in folder {folder}')
                else:
                    break
        else:
            # cmd = "which"
            path_chrome = "Need to implementation"
        return path_chrome

    @staticmethod
    def _extract_version_with_re(file_version) -> str:
        match = re.search(r'(\d+\.){3}\d+', file_version)
        version = match[0] if match else ''
        return version

    @staticmethod
    def _convert_str_to_raw(s) -> str:
        s = s.replace('\\', '\\\\')
        return s

    def _get_version_with_version(self, path_file: str) -> str:
        if os.path.isfile(path_file):
            cmd = ''
            if _platform == "win32" or _platform == "win64":
                cmd = f'"{path_file}" --version'
            elif _platform == "linux" or _platform == "linux2" or _platform == "darwin":
                cmd = f'{path_file} --version'

            success_msg = f' Version of file {path_file} successfully checked with command {cmd}'
            file_version = self.get_file_version(cmd, success_msg=success_msg)
        else:
            file_version = 'Not installed'
            self._logger.error('Chromedriver is missing on the computer at {path_file}')
        return file_version

    def get_file_version(self, cmd: str, success_msg: str) -> str:
        try:
            file_version = subprocess.check_output(cmd, stdin=DEVNULL, stderr=DEVNULL, shell=True).decode('utf-8')
            file_version = self._extract_version_with_re(file_version)
        except subprocess.CalledProcessError as e:
            self._logger.error(f'Command {cmd} caused an exception {e}')
            return ''
        else:
            self._logger.info(file_version + success_msg)
            return file_version

    def _get_version_chrome_for_linux(self):
        chrome_name_app = 'google-chrome-stable'
        cmd = f'"{chrome_name_app}" --version'
        success_msg = f' Version of Chrome {chrome_name_app} successfully checked with command {cmd}'
        return self.get_file_version(cmd, success_msg=success_msg)

    def _get_version_with_wmic_datafile(self, path_file: str):
        path_file = self._convert_str_to_raw(path_file)
        cmd = f'wmic datafile where name="{path_file}" get Version /value'
        try:
            version = subprocess.check_output(cmd, stdin=DEVNULL, stderr=DEVNULL, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            self._logger.error(
                f'Command {cmd} caused an exception {e}'
            )
            version = ''
        else:
            version = self._extract_version_with_re(version)
            self._logger.info(
                f'Version {version} of file {path_file} successfully checked with command {cmd}'
            )
        return version

    @staticmethod
    def _get_version_with_plist_datafile():
        path_file = '/Applications/Google Chrome.app/Contents/Info.plist'
        with open(path_file, 'r') as file:
            content = file.read()
            version = re.findall(r'<key>KSVersion</key>\n\t<string>(.+?)</string>', content)[0]
        return version

    def get_version_with_win32api(self, path_file: str) -> str:
        try:
            import win32api
            info = win32api.GetFileVersionInfo(path_file, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = f'{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}'
        except Exception as e:
            self._logger.error(f'Win32api.GetFileVersionInfo with path="{path_file}" caused an exception {e}')
            version = ''  # some appropriate default here.
        else:
            self._logger.info(f'Version of file {path_file} with Win32api.GetFileVersionInfo is {version}')
        return version

    def _get_version_with_selenium(self):
        # Not implemented
        driver = Chrome(executable_path=self._chromedriver_path)
        str1 = driver.capabilities['browserVersion']
        str2 = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
        self._logger.info(str1)
        self._logger.info(str2)
        self._logger.info(str1[0:2])
        self._logger.info(str2[0:2])

    def _update_chromedriver(self, chrome_version: str, chromedriver_version: str):
        if chrome_version[:4] != chromedriver_version[:4]:
            self._create_folder_for_file(self._chromedriver_path)
            chromedriver_version_os_url = self._get_chromedriver_url_by_version_os(
                download_search_url=CHROMEDRIVER_DOWNLOADS_URL, chrome_version=self._chrome_version
            )
            full_name_zip = self._download_chromedriver(chromedriver_url=chromedriver_version_os_url)
            self._change_chromedriver(old_file=self._chromedriver_path, zip_file=full_name_zip)
            self._chrome_version = self._get_chrome_version()
            self._chromedriver_version = self._get_chromedriver_version()
            self._logger.info(
                f'Installed Chrome {self._chrome_version} and chromedriver {self._chromedriver_version}'
            )

    def _get_chromedriver_url_by_version_os(self, download_search_url: str, chrome_version: str) -> str:
        chromedriver_url = ''
        driver_version = ''
        response = requests.get(download_search_url)
        if response.status_code == 200:
            selector = Selector(text=response.text)
            chromedriver_xpath = f'//a[contains(@href, {chrome_version[:4]})]/@href'
            chromedriver_version_url = selector.xpath(chromedriver_xpath).extract_first('')
            driver_version = self._extract_version_with_re(chromedriver_version_url)

        os_name = ''
        if _platform == "win32" or _platform == "win64":
            os_name = "win32"
        elif _platform == "darwin":
            os_name = 'mac64'
        elif _platform == "linux" or _platform == "linux2":
            os_name = 'linux64'

        if not os_name:
            raise Exception('Not supported OS. {}'.format(_platform))

        if driver_version:
            chromedriver_url = f'https://chromedriver.storage.googleapis.com/' \
                               f'{driver_version}/chromedriver_{os_name}.zip'
            self._logger.info(f'Chromedriver {driver_version}. Find download link {chromedriver_url}')
        else:
            self._logger.error(f'Not found new download link for chromedriver')

        return chromedriver_url

    def _download_chromedriver(self, chromedriver_url: str) -> str:
        driver_file_name = os.path.basename(urlparse(chromedriver_url).path)
        driver_dir = os.path.dirname(self._chromedriver_path)
        full_name = os.path.join(driver_dir, driver_file_name)
        content_driver = requests.get(chromedriver_url)
        if content_driver.status_code == 200:
            with open(full_name, "wb") as f:
                f.write(content_driver.content)
                self._logger.info(f'File {full_name} successfully downloaded from link {chromedriver_url}')
        else:
            self._logger.error(f'File {full_name} not downloaded from link {chromedriver_url}')
        return full_name

    def _change_chromedriver(self, old_file: str, zip_file: str):
        try:
            os.remove(old_file)
        except FileNotFoundError:
            self._logger.info(f'File {old_file} is not founded')
        except IOError:
            self._logger.error(f'File {old_file} is not accessible')
        else:
            self._logger.info(f'Old chromedriver {old_file} version {self._chromedriver_version} successfully removed')
        self._extract_chromedriver(zip_path=zip_file)
        if os.name == 'posix':
            self._make_chromedriver_executable()

    def _extract_chromedriver(self, zip_path: str):
        with zipfile.ZipFile(zip_path) as fantasy_zip:
            fantasy_zip.extractall(path=os.path.dirname(zip_path))
        self._logger.info(f'File {zip_path} successfully extracted from zip archive')
        try:
            os.remove(zip_path)
        except IOError:
            self._logger.error(f'File {zip_path} is not accessible')
        else:
            self._logger.info(f'Zip archive {zip_path} successfully removed')

    def _make_chromedriver_executable(self):
        os.system(f'chmod a+x {self._chromedriver_path}')

    def _create_folder_for_file(self, full_path: str):
        folder = os.path.dirname(full_path)
        access_rights = 0o755
        try:
            if not os.path.exists(folder):
                os.makedirs(folder, access_rights)
        except OSError:
            self._logger.error("Create directory %s failed" % folder)
        else:
            self._logger.info(f"Directory {folder} successfully created")
