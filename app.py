"""Desktop chat window. No browser, no localhost port."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import scrolledtext


def main() -> None:
    root = tk.Tk()
    root.title("Two Agent Lab")
    root.geometry("720x560")
    root.minsize(520, 400)

    header = tk.Label(
        root,
        text="Type what you need. Worker writes. Reviewer checks.",
        anchor="w",
        padx=12,
        pady=10,
    )
    header.pack(fill="x")

    log = scrolledtext.ScrolledText(root, wrap="word", state="disabled", height=20)
    log.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    row = tk.Frame(root)
    row.pack(fill="x", padx=12, pady=(0, 12))

    need = tk.Entry(row)
    need.pack(side="left", fill="x", expand=True, ipady=6)

    send = tk.Button(row, text="Send")
    send.pack(side="left", padx=(8, 0), ipadx=10, ipady=4)

    def write(text: str) -> None:
        log.configure(state="normal")
        log.insert("end", text + "\n\n")
        log.see("end")
        log.configure(state="disabled")

    def preload() -> None:
        try:
            import main as lab

            lab.load_settings()
            root.after(0, write, "Lab\nReady.")
        except Exception as error:
            root.after(0, write, f"Lab\nStartup: {type(error).__name__}: {error}")

    def send_task() -> None:
        task = need.get().strip()
        if not task or send["state"] == "disabled":
            return
        need.delete(0, "end")
        write("You\n" + task)
        send.configure(state="disabled")

        def on_status(message: str) -> None:
            root.after(0, write, "Lab\n" + message)

        def work() -> None:
            try:
                from main import execute_task

                on_status("Worker is starting. This can take a minute.")
                record, _md, _json = execute_task(task, on_status=on_status)
            except Exception as error:
                root.after(0, finish_error, f"{type(error).__name__}: {error}")
                return
            root.after(0, finish_ok, record.approved, record.final_result)

        threading.Thread(target=work, daemon=True).start()

    def finish_error(message: str) -> None:
        write("Lab\n" + message)
        send.configure(state="normal")
        need.focus_set()

    def finish_ok(approved: bool, result: str) -> None:
        label = "FINAL RESULT" if approved else "FINAL RESULT (NOT APPROVED)"
        write("Lab\n" + label + "\n\n" + result)
        send.configure(state="normal")
        need.focus_set()

    send.configure(command=send_task)
    need.bind("<Return>", lambda _event: send_task())
    need.focus_set()
    write("Lab\nWindow is ready. Checking keys…")
    threading.Thread(target=preload, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    main()
