from cryptography.fernet import Fernet


class FPwd:
    def __init__(self, addr, pin: str = None):
        self.addr = addr
        self.pin = pin
        self.fpwd = Fernet('Ku9AOXmiS01XY28wdqB0Kxrhxb9XlMaVtGOC9PhcMTE='.encode())

    def get_addr(self):
        if self.addr != '':
            return self.fpwd.decrypt(self.addr.encode()).decode()
        else:
            return ''

    def get_pin(self):
        if self.pin != '':
            return self.fpwd.decrypt(self.pin.encode()).decode()
        else:
            return ''


if __name__ == '__main__':
    password = FPwd(addr='gAAAAABkAKjJW5xUjPvCn8g3IgnZ8HOV47-OM2lDVTLb28-DAXOGrOgTdRfH2awumTxUQwGvp19Wv-CFNv1qpGM0HVroqSHfAA==')
    print(password.get_addr())