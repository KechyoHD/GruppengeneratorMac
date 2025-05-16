import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import csv
import math


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class GroupGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gruppengenerator")
        self.geometry("900x600")
        self.participants = []

    

        self.setup_ui()

    def setup_ui(self):
        self.last_hover_index = None


        # Konfigurieren der Spalten im Hauptfenster, damit sie den Platz gleichmäßig nutzen
        self.grid_columnconfigure(0, weight=0)  # linker Bereich
        self.grid_columnconfigure(1, weight=1)  # rechter Bereich (mehr Gewicht für den rechten Bereich)

        self.grid_rowconfigure(0, weight=1)

        # === Linker Bereich ===
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsw")
        left_frame.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(10, 0), sticky="ew")

        label = ctk.CTkLabel(header_frame, text="Teilnehmerliste", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(side="left", padx=(10, 0))

        clear_button = ctk.CTkButton(header_frame, text="Liste leeren", command=self.clear_participants, width=100, height=28)
        clear_button.pack(side="right", padx=(0,10))

        listbox_frame = ctk.CTkFrame(left_frame)
        listbox_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)

        font_large = tk.font.Font(family="Arial", size=14)  # oder eine andere Schriftart/Größe
        self.participant_listbox = tk.Listbox(listbox_frame, activestyle='none', font=font_large, selectbackground="lightgray", selectforeground="black")

        self.participant_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=self.participant_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.participant_listbox.config(yscrollcommand=scrollbar.set)

        self.participant_listbox.bind("<Leave>", self.on_leave)
        self.participant_listbox.bind("<Motion>", self.on_hover)
        self.participant_listbox.bind("<Button-1>", self.handle_click)

        # Neues Teilnehmerformular
        entry_frame = ctk.CTkFrame(left_frame)
        entry_frame.grid(row=2, column=0, pady=10)

        self.name_entry = ctk.CTkEntry(entry_frame, placeholder_text="Name")
        self.name_entry.grid(row=0, column=0, padx=5)
        self.age_entry = ctk.CTkEntry(entry_frame, placeholder_text="Alter")
        self.age_entry.grid(row=0, column=1, padx=5)
        self.age_entry.bind("<Return>", lambda event: self.add_participant())

        add_button = ctk.CTkButton(entry_frame, text="Hinzufügen", command=self.add_participant)
        add_button.grid(row=0, column=2, padx=5)

        # === Rechter Bereich ===
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")  # sticky="nsew" sorgt dafür, dass der Bereich immer wächst

        control_frame = ctk.CTkFrame(right_frame)
        control_frame.pack(pady=10)

        self.group_var = ctk.StringVar(value="2")
        self.group_dropdown = ctk.CTkOptionMenu(control_frame, values=[str(i) for i in range(2, 16)], variable=self.group_var)
        self.group_dropdown.grid(row=0, column=0, padx=10)

        self.generate_button = ctk.CTkButton(control_frame, text="Gruppen generieren", command=self.generate_groups)
        self.generate_button.grid(row=0, column=1, padx=10)

        # === Scrollbarer Bereich für Gruppenanzeige ===
        self.groups_canvas = tk.Canvas(right_frame, bg="#f0f0f0", highlightthickness=0)
        self.groups_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=self.groups_canvas.yview)
        self.groups_scrollable_frame = ctk.CTkFrame(self.groups_canvas)

        self.groups_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.groups_canvas.configure(
                scrollregion=self.groups_canvas.bbox("all")
            )
        )

        self.canvas_window = self.groups_canvas.create_window(
            (0, 0),
            window=self.groups_scrollable_frame,
            anchor="nw",
            tags="frame"  # wichtig für itemconfig
        )
        self.groups_canvas.bind(
            "<Configure>",
            lambda e: self.groups_canvas.itemconfig("frame", width=e.width, height=e.height)
        )
        self.groups_canvas.configure(yscrollcommand=self.groups_scrollbar.set)

        self.groups_canvas.pack(side="left", fill="both", expand=True, pady=10)
        self.groups_scrollbar.pack(side="right", fill="y")


        self.load_participants_from_csv()



    def clear_participants(self):
        if self.participants:
            if messagebox.askyesno("Liste leeren", "Möchtest du wirklich alle Teilnehmer entfernen?"):
                self.participants.clear()
                self.update_listbox()
                self.save_participants_to_csv()
        else:
            messagebox.showinfo("Liste leer", "Es gibt keine Teilnehmer zu löschen.")



    def add_participant(self):
        name = self.name_entry.get().strip()
        try:
            age = int(self.age_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ungültige Eingabe", "Alter muss eine Zahl sein.")
            return

        if name and age > 0:
            self.participants.append((name, age))
            self.update_listbox()
            self.name_entry.delete(0, tk.END)
            self.age_entry.delete(0, tk.END)
            self.name_entry.focus()
            self.save_participants_to_csv()
            
        else:
            messagebox.showerror("Fehler", "Bitte gültigen Namen und Alter eingeben.")

    def update_listbox(self):
        self.participant_listbox.delete(0, tk.END)
        for i, (name, age) in enumerate(self.participants):
            self.participant_listbox.insert(i, f"{name} ({age})")

    def on_hover(self, event):
        index = self.participant_listbox.nearest(event.y)

        if index != self.last_hover_index:
            # Entferne alte Auswahl
            self.participant_listbox.selection_clear(0, tk.END)

            # Setze neue Auswahl
            self.participant_listbox.selection_set(index)
            self.last_hover_index = index


    def on_leave(self, event):
        self.participant_listbox.selection_clear(0, tk.END)
        self.last_hover_index = None


    def remove_participant(self, index):
        if index < len(self.participants):
            if messagebox.askyesno("Teilnehmer löschen", f"{self.participants[index][0]} wirklich löschen?"):
                del self.participants[index]
                self.update_listbox()

    def generate_groups(self):
        num_groups = int(self.group_var.get())
        if len(self.participants) < num_groups:
            messagebox.showwarning("Zu wenig Teilnehmer", "Nicht genug Teilnehmer für diese Anzahl Gruppen.")
            return



        # start generator
        # shuffled = self.participants[:]
        # random.shuffle(shuffled)
        # groups = [[] for _ in range(num_groups)]
        

        # for i, participant in enumerate(shuffled):
        #     groups[i % num_groups].append(participant)

        # print(groups[1])
        # Ende generator; Ziel: groups = [[("name", int), ("name", int)],[]]: Array mit Arrays an tuples("name", int-alter)

        sortedList = self.participants[:]
        sortedList.sort()

        groups = [[] for _ in range(num_groups)]
        currentGroup = 0
        groupsize = math.ceil(len(sortedList) / num_groups)
        groupAverageAge = sum(age for name, age in sortedList) / len(sortedList)

        for i in range(num_groups):
            groups[i].append(sortedList[int(random.random()*len(sortedList))])
            sortedList.remove(groups[i][0])

        while len(sortedList) > 0:
            if len(groups[currentGroup]) >= groupsize:
                currentGroup += 1

            for i in range(15):
                nextParticipant = sortedList[int(random.random()*len(sortedList))]
                if sum(age for name, age in groups[currentGroup]) / len(groups[currentGroup]) > groupAverageAge:
                    if nextParticipant[1] < groupAverageAge:
                        groups[currentGroup].append(nextParticipant)
                        sortedList.remove(nextParticipant)
                        break
                else:
                    if nextParticipant[1] > groupAverageAge:
                        groups[currentGroup].append(nextParticipant)
                        sortedList.remove(nextParticipant)
                        break
                if i == 14:
                    groups[currentGroup].append(nextParticipant)
                    sortedList.remove(nextParticipant)
                    break
            
            


        # Anzeige aktualisieren
        for widget in self.groups_scrollable_frame.winfo_children():
            widget.destroy()


        for i, group in enumerate(groups):
            group_box = ctk.CTkFrame(self.groups_scrollable_frame)
            group_box.pack(fill="x", padx=10, pady=5)

            names = "\n".join([f"{name} ({age})" for name, age in group])
            avg_age = sum([age for _, age in group]) / len(group)
            group_font = ctk.CTkFont(size=16)  # Oder z. B. 18 für größer
            title_label = ctk.CTkLabel(
                group_box,
                text=f"Gruppe {i+1} - Ø Alter: {avg_age:.1f}",
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w",
                justify="left"
            )
            title_label.pack(anchor="w", padx=10, pady=(5, 0))

            names_label = ctk.CTkLabel(
                group_box,
                text="\n".join([f"{name} ({age})" for name, age in group]),
                font=ctk.CTkFont(size=14),
                anchor="w",
                justify="left"
            )
            names_label.pack(anchor="w", padx=10, pady=(0, 5))

    


    def save_participants_to_csv(self):
        csv_path = os.path.join(os.path.dirname(__file__), "resources", "participants.csv")
        # Speichert die Teilnehmer in einer CSV-Datei
        with open(csv_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Alter"])  # Header
            for name, age in self.participants:
                writer.writerow([name, age])

    def load_participants_from_csv(self):
        csv_path = os.path.join(os.path.dirname(__file__), "resources", "participants.csv")
        if os.path.exists(csv_path):
            with open(csv_path, "r", newline="") as file:
                reader = csv.reader(file)
                try:
                    header = next(reader)  # Header überspringen
                except StopIteration:
                    return  # Datei ist leer → einfach zurückkehren
                self.participants = [(name, int(age)) for name, age in reader]
            self.update_listbox()



            
    def handle_click(self, event):
            index = self.participant_listbox.nearest(event.y)
            if index < len(self.participants):
                if messagebox.askyesno("Teilnehmer löschen", f"{self.participants[index][0]} wirklich löschen?"):
                    del self.participants[index]
                    self.update_listbox()
                    self.save_participants_to_csv()

if __name__ == "__main__":
    app = GroupGeneratorApp()
    app.mainloop()
