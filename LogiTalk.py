import socket
import threading
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x500")
        self.title("LogiTalk")
        self.theme = "Light"
        set_appearance_mode(self.theme)
        self.username = ""
        self.sock = None
        self.connected = False

        self.create_login_screen()

    def create_login_screen(self):
        self.login_frame = CTkFrame(self)
        self.login_frame.pack(expand=True)

        self.theme_button = CTkButton(
            self.login_frame,
            text="Змінити тему",
            command=self.toggle_theme
        )
        self.theme_button.pack(pady=10)

        self.login_label = CTkLabel(
            self.login_frame,
            text="Введіть ваш ник",
            font=("Arial", 20, "bold")
        )
        self.login_label.pack(pady=20)

        self.login_entry = CTkEntry(
            self.login_frame,
            placeholder_text="Ваш ник..."
        )
        self.login_entry.pack(pady=10)

        self.login_entry.bind("<Return>", lambda event: self.confirm_login())

        self.login_button = CTkButton(
            self.login_frame,
            text="Увійти",
            command=self.confirm_login
        )
        self.login_button.pack(pady=10)

    def confirm_login(self):
        name = self.login_entry.get().strip()
        if name == "":
            return

        self.username = name
        self.login_frame.destroy()
        self.create_main_interface()

        self.connect_to_server()

    def create_main_interface(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.sidebar = CTkFrame(self, width=150)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(10, 5), pady=10)

        self.menu_label = CTkLabel(
            self.sidebar,
            text="Настройки",
            font=("Arial", 18, "bold")
        )
        self.menu_label.pack(pady=10)

        self.user_label = CTkLabel(
            self.sidebar,
            text="Ви: " + self.username
        )
        self.user_label.pack(pady=5)

        self.theme_button2 = CTkButton(
            self.sidebar,
            text="Змінити тему",
            command=self.toggle_theme
        )
        self.theme_button2.pack(pady=10)

        self.chat = CTkTextbox(self)
        self.chat.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(10, 5))
        self.chat.configure(state="disabled")

        self.add_message("Система", f"Ласкаво просимо, {self.username}!")

        self.bottom_frame = CTkFrame(self)
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(5, 10))
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.entry = CTkEntry(
            self.bottom_frame,
            placeholder_text="Введіть повідомлення..."
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=5, pady=8)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = CTkButton(
            self.bottom_frame,
            text="відправити",
            command=self.send_message,
            width=120
        )
        self.send_button.grid(row=0, column=1, padx=5, pady=8)

    def toggle_theme(self):
        self.theme = "Dark" if self.theme == "Light" else "Light"
        set_appearance_mode(self.theme)

    def add_message(self, author, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{author}: {text}\n")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(("4.tcp.eu.ngrok.io", 19500))
            self.connected = True

            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode("utf-8"))

            threading.Thread(target=self.recv_message, daemon=True).start()

            self.add_message("Система", "Підключено до сервера")

        except Exception as e:
            self.add_message("Система", f"Не вдалося підключитися до сервера: {e}")

    def send_message(self):
        message = self.entry.get().strip()
        if message == "":
            return

        self.add_message(self.username, message)
        self.entry.delete(0, "end")

        if self.connected and self.sock:
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode("utf-8"))
            except:
                pass

    def recv_message(self):
        buffer = ""

        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break

                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break

        self.sock.close()

    def handle_line(self, line):
        if not line:
            return

        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(author, message)

        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message("Система", f"{author} надіслав(ла) зображення: {filename}")

        else:
            self.add_message("Сервер", line)


app = MainWindow()
app.mainloop()
