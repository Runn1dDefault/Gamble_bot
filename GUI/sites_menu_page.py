from typing import Optional
from tkinter import Button, messagebox, StringVar, OptionMenu, CENTER

from requests import HTTPError
from requests.exceptions import ConnectionError as Ce

from api import APIClient
from config import USE_PROXY
from gamble.launchers import GambleLauncher
from service.utils import rebuild_site_dict_structure

from GUI.base_frame import BaseFrame


class SitesMenuPage(BaseFrame):
    def __init__(self, root, api_client: APIClient):
        super().__init__(root)

        self.api_client = api_client
        self.start_btn = Button(self, text="Start", command=self._on_start)
        self.sites_option_menu = None
        self.selected = None
        self.sites_data = None

    def _on_start(self) -> None:
        if not self.sites_data:
            messagebox.showinfo(title='Error', message='Not found sites!')
            return

        if not self.selected:
            messagebox.showinfo(title='Error', message='You not select any sites!')
            return

        self.started = True
        site_name = self.selected.get()
        site_data = self.sites_data.get(site_name)

        if not site_data:
            messagebox.showinfo(title='Error', message='Not found site {}!'.format(site_name))
            return

        logic = GambleLauncher(
            site_name=site_name,
            ext_value=site_data.get('target_balance', 0.0),
            min_balance_value=site_data.get('min_balance', 0.0),
            min_gamble_amount=site_data.get('min_check', 0.0),
            api_client=self.api_client
        )
        logic.init_game(
            coin_clicks_amount=site_data.get('coin_clicks', 3),
            game_link=site_data.get('link_game'),
            use_proxy=USE_PROXY
        )
        logic.run_game_process()

    def get_sites_data(self) -> Optional[dict]:
        try:
            sites = self.api_client.get_betsites()
            return sites
        except HTTPError:
            self.logger.error('Failed to get sites')

    def sites_update(self):
        try:
            self.sites_data = rebuild_site_dict_structure(self.get_sites_data())
        except Ce as ce:
            self.logger.critical(ce)
            messagebox.showinfo(title='Error', message='Check the connection and restart the program')
            return

        if not self.sites_data:
            return

        sites_options = list(self.sites_data.keys())
        self.selected = StringVar(self)
        self.selected.set(sites_options[0])

        if self.sites_option_menu:
            self.sites_option_menu.destroy()

        self.sites_option_menu = OptionMenu(self, self.selected, *sites_options)
        self.sites_option_menu.place(relx=0.35, rely=0.5, anchor=CENTER)

    def setup(self):
        self.start_btn.place(relx=0.6, rely=0.5, anchor=CENTER)


if __name__ == '__main__':
    from tkinter import Tk, Frame

    root = Tk()
    main_frame = Frame(root)
    main_frame.pack(side="top", fill="both", expand=True)
    root.title('GambleBot')
    root.wm_geometry("400x400")

    api = APIClient(username='conor', password='test759gmail')
    app = SitesMenuPage(root, api_client=api)
    app.setup()
    app.place(in_=main_frame, x=0, y=0, relwidth=1, relheight=1)
    app.sites_update()

    root.mainloop()
