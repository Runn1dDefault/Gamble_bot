from datetime import datetime, timedelta
from tkinter import messagebox, Tk, Frame

from config import ICON_PATH

from GUI.login_page import LoginPage
from GUI.sites_menu_page import SitesMenuPage


def main():
    running = True
    root = Tk()

    def on_closing():
        nonlocal running, root

        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            running = False
            root.destroy()

    main_frame = Frame(root)
    main_frame.pack(side="top", fill="both", expand=True)

    # Setting icon of master window
    # root.iconbitmap(ICON_PATH)
    root.title('GambleBot')
    root.wm_geometry("400x400")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    login_page = LoginPage(master=root)
    login_page.setup()
    login_page.place(in_=main_frame, x=0, y=0, relwidth=1, relheight=1)

    showed_sites_menu = False
    sites_menu_page = None
    interval = timedelta(seconds=20)
    end_time = datetime.now() + interval

    while running:
        root.update()

        if login_page.validated and showed_sites_menu is False:
            sites_menu_page = SitesMenuPage(root, login_page.api_client)
            sites_menu_page.setup()
            sites_menu_page.place(in_=main_frame, x=0, y=0, relwidth=1, relheight=1)
            sites_menu_page.sites_update()
            login_page.destroy()
            showed_sites_menu = True

        if sites_menu_page is not None:
            now_time = datetime.now()

            if now_time < end_time:
                continue

            end_time = now_time + interval
            sites_menu_page.sites_update()
