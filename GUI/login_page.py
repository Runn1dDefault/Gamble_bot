from functools import partial
from tkinter import Label, StringVar, Entry, Button, CENTER, messagebox

from api import APIClient
from exceptions import APIError

from GUI.base_frame import BaseFrame


class LoginPage(BaseFrame):
    def __init__(self, master):
        super().__init__(master)
        self.username_label = Label(self, text="Username")
        self.username_input = StringVar()
        self.username_entry = Entry(self, textvariable=self.username_input)

        self.password_label = Label(self, text="Password")
        self.password_input = StringVar()
        self.password_entry = Entry(self, textvariable=self.password_input, show='*')

        self.submit_btn = Button(
            self,
            text="Login",
            command=partial(self._validate_login, self.username_input, self.password_input)
        )
        self._validated = False
        self.api_client = None

    @property
    def validated(self):
        return self._validated

    def setup(self):
        self.username_label.place(relx=0.2, rely=0.35, anchor=CENTER)
        self.username_entry.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.password_label.place(relx=0.2, rely=0.45, anchor=CENTER)
        self.password_entry.place(relx=0.5, rely=0.45, anchor=CENTER)
        self.submit_btn.place(relx=0.5, rely=0.6, anchor=CENTER)

    def _validate_login(self, username_input, password_input):
        username, password = username_input.get(), password_input.get()

        self.api_client = APIClient(username=username, password=password)
        try:
            auth_data = self.api_client.auth()
        except APIError as e:
            messagebox.showinfo(title='Error', message='Something went wrong')
            self.logger.error(e)
            self.api_client = None
        else:
            token = auth_data.get('token')

            if not token:
                messagebox.showinfo(
                    title='Wrong data',
                    message='Please, check if your credentials are correct'
                )
                self.logger.error('Not found Token on auth!')
                self.api_client = None
            else:
                self._validated = True
