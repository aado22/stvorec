import random
import tkinter as tk

SIRKA_PLATNA = 600
VYSKA_PLATNA = 400
VELKOST_STVORCA = 50
CAS_HRY = 30
RYCHLOST_PRESUNU = 800


class KlikaciaHra:

    def __init__(self, root):
        self.root = root
        self.root.title("Chyť štvorec – 30s výzva")
        self.root.resizable(False, False)

        self.skore = 0
        self.minutia = 0
        self.zostavajuci_cas = CAS_HRY
        self.hra_bezi = True
        self.casovac_skoku = None
        self.casovac_odpoctu = None
        self.posledna_akcia = "Hra začala"

        self.info_frame = tk.Frame(root, bg="#2c3e50", pady=8, padx=12)
        self.info_frame.pack(fill=tk.X)

        self.skore_label = tk.Label(
            self.info_frame,
            text=f"Skóre: {self.skore}",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        self.skore_label.pack(side=tk.LEFT, padx=(0, 12))

        self.minutia_label = tk.Label(
            self.info_frame,
            text=f"Minuté: {self.minutia}",
            font=("Arial", 14, "bold"),
            fg="#f39c12",
            bg="#2c3e50",
        )
        self.minutia_label.pack(side=tk.LEFT, padx=(0, 12))

        self.presnost_label = tk.Label(
            self.info_frame,
            text="Presnosť: 0.0 %",
            font=("Arial", 14, "bold"),
            fg="#3498db",
            bg="#2c3e50",
        )
        self.presnost_label.pack(side=tk.LEFT, padx=(0, 12))

        self.cas_label = tk.Label(
            self.info_frame,
            text=f"Čas: {self.zostavajuci_cas}s",
            font=("Arial", 14, "bold"),
            fg="#e74c3c",
            bg="#2c3e50",
        )
        self.cas_label.pack(side=tk.LEFT, padx=(0, 12))

        self.restart_btn = tk.Button(
            self.info_frame,
            text="Reštart",
            font=("Arial", 11, "bold"),
            command=self.restartuj_hru,
        )
        self.restart_btn.pack(side=tk.RIGHT)

        self.bonus_btn = tk.Button(
            self.info_frame,
            text="+2 Bonus",
            font=("Arial", 11),
            command=lambda: self.pridaj_body(2),
        )
        self.bonus_btn.pack(side=tk.RIGHT, padx=(0, 8))

        self.stav_label = tk.Label(
            root,
            text="Návod: Klikni na štvorec | R = reštart, Esc = koniec",
            font=("Arial", 10),
            bg="#dfe6e9",
            fg="#2d3436",
            pady=5,
        )
        self.stav_label.pack(fill=tk.X)

        self.platno = tk.Canvas(
            root, width=SIRKA_PLATNA, height=VYSKA_PLATNA, bg="#ecf0f1"
        )
        self.platno.pack()

        self.stvorec = self.platno.create_rectangle(
            0,
            0,
            VELKOST_STVORCA,
            VELKOST_STVORCA,
            fill="#3498db",
            outline="#2980b9",
            width=2,
        )

        self.platno.tag_bind(self.stvorec, "<Button-1>", self.klik_na_stvorec)
        self.platno.bind("<Button-1>", self.klik_na_platno)
        self.root.bind("<Key>", self.stlacenie_klavesu)

        self.presun_stvorec()
        self.odpocet_casu()

    def je_bod_v_stvori(self, x, y):
        """Overí, či súradnice (x, y) ležia v aktuálnom ohraničení štvorca."""
        try:
            bbox = self.platno.bbox(self.stvorec)
            if not bbox:
                return False
            x1, y1, x2, y2 = bbox
            return x1 <= x <= x2 and y1 <= y <= y2
        except Exception:
            return False

    def vypocitaj_presnost(self):
        """Vráti presnosť v percentách (0.0 až 100.0)."""
        zasahy = max(0, int(self.skore))
        minutia = max(0, int(self.minutia))
        celkovo = zasahy + minutia
        if celkovo == 0:
            return 0.0
        return (zasahy / celkovo) * 100.0

    def aktualizuj_statistiky(self):
        """Aktualizuje skóre, minutie aj percentá na jednom mieste."""
        presnost = self.vypocitaj_presnost()
        self.skore_label.config(text=f"Skóre: {self.skore}")
        self.minutia_label.config(text=f"Celkovo: {self.minutia}")
        self.presnost_label.config(text=f"Presnosť: {presnost:.1f} %")

    def aktualizuj_stav_label(self):
        if not self.root.winfo_exists():
            return
        stav = "BEŽÍ" if self.hra_bezi else "KONIEC"
        self.stav_label.config(
            text=(
                f"Stav: {stav} | {self.posledna_akcia} | "
                f"Ovládanie: klik na štvorec, R = reštart, Esc = koniec"
            )
        )

    def pridaj_body(self, pocet):
        """Callback s parametrom cez lambda – pripočíta bonusové body."""
        if not self.hra_bezi:
            return
        try:
            self.skore += int(pocet)
            self.posledna_akcia = f"Pridané body (+{pocet})"
            self.aktualizuj_statistiky()
            self.aktualizuj_stav_label()
        except Exception:
            pass

    # 1. Callback: reaguje na kliknutie ľavým tlačidlom na štvorec
    def klik_na_stvorec(self, event):
        if not self.hra_bezi:
            return
        x = getattr(event, "x", 0)
        y = getattr(event, "y", 0)
        self.skore += 1
        self.posledna_akcia = f"Trafený štvorec na ({x}, {y})"
        self.aktualizuj_statistiky()
        self.aktualizuj_stav_label()
        self.presun_stvorec()

    # 2. Callback: reaguje na kliknutie ľavým tlačidlom na plátno; minutie ráta len mimo štvorca
    def klik_na_platno(self, event):
        x = getattr(event, "x", 0)
        y = getattr(event, "y", 0)
        if not self.hra_bezi:
            self.posledna_akcia = f"Klik po konci hry ({x}, {y})"
            self.aktualizuj_stav_label()
            return

        # Ak používateľ klikol priamo na štvorec, nepočítame to ako minutie
        if self.je_bod_v_stvori(x, y):
            return

        self.minutia += 1
        self.posledna_akcia = f"Minuté na ({x}, {y})"
        self.aktualizuj_statistiky()
        self.aktualizuj_stav_label()

    # 3. Callback: reaguje na stlačenie klávesu (event.keysym)
    def stlacenie_klavesu(self, event):
        klaves = getattr(event, "keysym", "")
        if klaves in ("r", "R"):
            self.restartuj_hru()
        elif klaves == "Escape":
            self.zavri_okno()
        else:
            self.posledna_akcia = f"Kláves: {klaves}"
            self.aktualizuj_stav_label()

    # 4. Callback: reaguje na časovač presunu štvorca
    def presun_stvorec(self):
        if not self.hra_bezi:
            return
        if self.casovac_skoku is not None:
            try:
                self.root.after_cancel(self.casovac_skoku)
            except Exception:
                pass
            self.casovac_skoku = None

        try:
            if self.platno.find_withtag(self.stvorec):
                x = random.randint(0, max(0, SIRKA_PLATNA - VELKOST_STVORCA))
                y = random.randint(0, max(0, VYSKA_PLATNA - VELKOST_STVORCA))
                farby = ["#3498db", "#e67e22", "#2ecc71", "#9b59b6", "#e74c3c"]
                self.platno.coords(
                    self.stvorec, x, y, x + VELKOST_STVORCA, y + VELKOST_STVORCA
                )
                self.platno.itemconfig(self.stvorec, fill=random.choice(farby))
        except Exception:
            pass

        if self.hra_bezi:
            self.casovac_skoku = self.root.after(
                RYCHLOST_PRESUNU, self.presun_stvorec
            )

    # 5. Callback: reaguje na sekundový odpočet času
    def odpocet_casu(self):
        if not self.hra_bezi:
            return
        if self.zostavajuci_cas > 0:
            self.zostavajuci_cas -= 1
            self.cas_label.config(text=f"Čas: {self.zostavajuci_cas}s")
            self.casovac_odpoctu = self.root.after(1000, self.odpocet_casu)
        else:
            self.koniec_hry()

    # 6. Callback: reaguje na tlačidlo Reštart alebo kláves R
    def restartuj_hru(self):
        for casovac in (self.casovac_skoku, self.casovac_odpoctu):
            if casovac is not None:
                try:
                    self.root.after_cancel(casovac)
                except Exception:
                    pass
        self.casovac_skoku = None
        self.casovac_odpoctu = None

        self.skore = 0
        self.minutia = 0
        self.zostavajuci_cas = CAS_HRY
        self.hra_bezi = True
        self.posledna_akcia = "Hra reštartovaná"

        self.cas_label.config(text=f"Čas: {self.zostavajuci_cas}s")
        self.aktualizuj_statistiky()
        self.aktualizuj_stav_label()

        self.platno.delete("all")
        self.stvorec = self.platno.create_rectangle(
            0,
            0,
            VELKOST_STVORCA,
            VELKOST_STVORCA,
            fill="#3498db",
            outline="#2980b9",
            width=2,
        )
        self.platno.tag_bind(self.stvorec, "<Button-1>", self.klik_na_stvorec)

        self.presun_stvorec()
        self.odpocet_casu()

    def koniec_hry(self):
        self.hra_bezi = False
        if self.casovac_skoku is not None:
            try:
                self.root.after_cancel(self.casovac_skoku)
            except Exception:
                pass
            self.casovac_skoku = None

        presnost = self.vypocitaj_presnost()
        self.aktualizuj_statistiky()
        self.posledna_akcia = f"Čas vypršal | Presnosť: {presnost:.1f} %"
        self.aktualizuj_stav_label()

        self.platno.delete("all")
        self.platno.create_text(
            SIRKA_PLATNA / 2,
            VYSKA_PLATNA / 2 - 50,
            text="KONIEC HRY!",
            font=("Arial", 28, "bold"),
            fill="#2c3e50",
        )
        self.platno.create_text(
            SIRKA_PLATNA / 2,
            VYSKA_PLATNA / 2 - 5,
            text=f"Tvoje finálne skóre: {self.skore}",
            font=("Arial", 18),
            fill="#27ae60",
        )
        self.platno.create_text(
            SIRKA_PLATNA / 2,
            VYSKA_PLATNA / 2 + 30,
            text=f"Počet minutí: {self.minutia}",
            font=("Arial", 15),
            fill="#d35400",
        )
        self.platno.create_text(
            SIRKA_PLATNA / 2,
            VYSKA_PLATNA / 2 + 65,
            text=f"Presnosť zásahov: {presnost:.1f} %",
            font=("Arial", 16, "bold"),
            fill="#2980b9",
        )

    def zavri_okno(self):
        self.hra_bezi = False
        try:
            self.root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    okno = tk.Tk()
    hra = KlikaciaHra(okno)
    okno.mainloop()