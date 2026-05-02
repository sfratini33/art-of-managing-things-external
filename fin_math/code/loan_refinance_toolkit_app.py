"""
Loan Refinance Toolkit (standalone app).

This file is extracted from `loan_refinance_toolkit.ipynb` so it can be packaged
into a Windows executable (e.g., via PyInstaller).
"""

from __future__ import annotations

import csv
import os
import sys
import tkinter as tk
import tkinter.ttk as ttk


# ----------------------------- math helpers ---------------------------------


def periodic_payment(p: float, i: float, n: int) -> float:
    if n <= 0:
        return 0.0
    if i == 0:
        return p / n
    g = (1 + i) ** n
    return p * i * g / (g - 1)


def balance_after_k_payments(p: float, i: float, a: float, k: int) -> float:
    if k <= 0:
        return p
    if i == 0:
        return max(0.0, p - a * k)
    h = (1 + i) ** k
    return max(0.0, h * p - a * (h - 1) / i)


# ----------------------------- UI helpers -----------------------------------


def bring_to_front(win: tk.Tk) -> None:
    win.lift()
    try:
        win.attributes("-topmost", True)
        win.after(250, lambda: win.attributes("-topmost", False))
    except tk.TclError:
        pass


def set_output(box: tk.Text, text: str) -> None:
    try:
        box.config(state="normal")
        box.delete("1.0", tk.END)
        box.insert(tk.END, text)
        box.config(state="disabled")
    except tk.TclError:
        pass


def app_dir() -> str:
    # When packaged as a one-file executable, use the folder containing the exe
    # so CSV output is easy to find.
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# ----------------------------- app ------------------------------------------


def main() -> None:
    root = tk.Tk()
    root.title("Loan Refinance Toolkit")
    bring_to_front(root)

    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Tabs
    nb = ttk.Notebook(main_frame)
    nb.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    single_tab = ttk.Frame(nb, padding=10)
    analyzer_tab = ttk.Frame(nb, padding=10)
    nb.add(single_tab, text="Single Refinance")
    nb.add(analyzer_tab, text="Breakeven Rate Table")

    for tab in (single_tab, analyzer_tab):
        tab.columnconfigure(0, weight=1)

    # Shared inputs (appear on both tabs)
    shared: dict[str, tk.Variable] = {
        "p0": tk.DoubleVar(value=0.0),
        "i0": tk.DoubleVar(value=0.0),
        "n0": tk.IntVar(value=0),
        "k": tk.IntVar(value=0),
        "cost": tk.DoubleVar(value=0.0),
    }

    # Single-scenario inputs
    single: dict[str, tk.Variable] = {
        "i1": tk.DoubleVar(value=0.0),
        "n1": tk.IntVar(value=0),
    }

    # Analyzer inputs
    an: dict[str, tk.Variable] = {
        "i_low": tk.DoubleVar(value=0.0),
        "step": tk.DoubleVar(value=0.00005),
        "n1": tk.IntVar(value=0),
        "n_per_y": tk.IntVar(value=12),
    }

    def build_shared_inputs(parent: ttk.Frame, start_row: int = 0) -> int:
        frm = ttk.LabelFrame(parent, text="Shared inputs", padding=10)
        frm.grid(row=start_row, column=0, sticky="ew")
        frm.columnconfigure(1, weight=1)

        rr = 0
        ttk.Label(frm, text="Amount of initial loan (P):").grid(row=rr, column=0, sticky="w", pady=2)
        ttk.Entry(frm, textvariable=shared["p0"]).grid(row=rr, column=1, sticky="ew", pady=2)
        rr += 1

        ttk.Label(frm, text="Interest rate per period for initial loan (i₀):").grid(
            row=rr, column=0, sticky="w", pady=2
        )
        ttk.Entry(frm, textvariable=shared["i0"]).grid(row=rr, column=1, sticky="ew", pady=2)
        rr += 1

        ttk.Label(frm, text="Number of periods for initial loan (n₀):").grid(row=rr, column=0, sticky="w", pady=2)
        ttk.Entry(frm, textvariable=shared["n0"]).grid(row=rr, column=1, sticky="ew", pady=2)
        rr += 1

        ttk.Label(frm, text="Periods completed when refinancing starts (k):").grid(
            row=rr, column=0, sticky="w", pady=2
        )
        ttk.Entry(frm, textvariable=shared["k"]).grid(row=rr, column=1, sticky="ew", pady=2)
        rr += 1

        ttk.Label(frm, text="Refinancing costs (termination + new-loan costs):").grid(
            row=rr, column=0, sticky="w", pady=2
        )
        ttk.Entry(frm, textvariable=shared["cost"]).grid(row=rr, column=1, sticky="ew", pady=2)

        return start_row + 1

    # ----------------------------- Single tab -----------------------------------

    r = build_shared_inputs(single_tab, 0)

    single_specific = ttk.LabelFrame(single_tab, text="Single-refinance inputs", padding=10)
    single_specific.grid(row=r, column=0, sticky="ew", pady=(10, 0))
    single_specific.columnconfigure(1, weight=1)

    rr = 0
    ttk.Label(single_specific, text="Interest rate per period for refinanced loan (i₁):").grid(
        row=rr, column=0, sticky="w", pady=2
    )
    ttk.Entry(single_specific, textvariable=single["i1"]).grid(row=rr, column=1, sticky="ew", pady=2)
    rr += 1

    ttk.Label(single_specific, text="Number of periods for refinanced loan (n₁):").grid(
        row=rr, column=0, sticky="w", pady=2
    )
    ttk.Entry(single_specific, textvariable=single["n1"]).grid(row=rr, column=1, sticky="ew", pady=2)
    rr += 1

    single_out = tk.Text(single_tab, height=16, width=98)
    single_out.grid(row=r + 2, column=0, sticky="w", pady=(10, 0))
    single_out.config(state="disabled")

    def analyze_single() -> None:
        p0 = float(shared["p0"].get())
        i0 = float(shared["i0"].get())
        n0 = int(shared["n0"].get())
        k = int(shared["k"].get())
        cost = float(shared["cost"].get())

        i1 = float(single["i1"].get())
        n1 = int(single["n1"].get())

        if p0 <= 0:
            set_output(single_out, "Error: please enter a positive initial loan amount.")
            return
        if n0 <= 0 or n1 <= 0:
            set_output(single_out, "Error: please enter positive values for n₀ and n₁.")
            return
        if k < 0 or k > n0:
            set_output(single_out, "Error: completed periods (k) must be between 0 and n₀.")
            return
        if i0 < 0 or i1 < 0:
            set_output(single_out, "Error: interest rates must be nonnegative decimals (e.g., 0.005).")
            return

        a0 = periodic_payment(p0, i0, n0)
        bal = balance_after_k_payments(p0, i0, a0, k)
        if bal <= 1e-6:
            set_output(single_out, f"Loan is already paid off by period {k}.")
            return

        a1 = periodic_payment(bal, i1, n1)

        remaining = n0 - k
        t_pay0 = a0 * remaining
        interest0 = t_pay0 - bal

        t_pay1 = a1 * n1 + cost
        interest1 = a1 * n1 - bal

        if a1 < a0:
            savings = a0 - a1
            recover = int(cost / savings) + 1 if cost > 0 else 0
            recover_line = (
                f"It will take {recover} periods to recover the refinancing cost based on payment savings."
            )
        else:
            recover_line = (
                "The new periodic payment is not lower than the existing payment; "
                "refinancing may not make sense based on payment reduction alone."
            )

        text = (
            f"Balance at refinance point: ${bal:,.2f}\n\n"
            f"Periodic payment (existing loan): ${a0:,.2f}\n"
            f"Periodic payment (new loan):      ${a1:,.2f}\n\n"
            f"Remaining payments if NOT refinanced: ${t_pay0:,.2f}\n"
            f"  Interest portion (not refinanced):   ${interest0:,.2f}\n\n"
            f"Refi total payments (includes costs):  ${t_pay1:,.2f}\n"
            f"  Interest portion (excl. costs):      ${interest1:,.2f}\n\n"
            f"{recover_line}"
        )
        set_output(single_out, text)

    ttk.Button(single_specific, text="Analyze single refinance", command=analyze_single).grid(
        row=rr, column=0, columnspan=2, sticky="ew", pady=(10, 0)
    )

    # ----------------------------- Analyzer tab ---------------------------------

    r2 = build_shared_inputs(analyzer_tab, 0)

    an_specific = ttk.LabelFrame(analyzer_tab, text="Analyzer inputs", padding=10)
    an_specific.grid(row=r2, column=0, sticky="ew", pady=(10, 0))
    an_specific.columnconfigure(1, weight=1)

    rr = 0
    ttk.Label(an_specific, text="Refinanced loan periods (n₁):").grid(row=rr, column=0, sticky="w", pady=2)
    ttk.Entry(an_specific, textvariable=an["n1"]).grid(row=rr, column=1, sticky="ew", pady=2)
    rr += 1

    ttk.Label(an_specific, text="Start rate for analysis (i_low):").grid(row=rr, column=0, sticky="w", pady=2)
    ttk.Entry(an_specific, textvariable=an["i_low"]).grid(row=rr, column=1, sticky="ew", pady=2)
    rr += 1

    ttk.Label(an_specific, text="Rate step (Δi):").grid(row=rr, column=0, sticky="w", pady=2)
    ttk.Entry(an_specific, textvariable=an["step"]).grid(row=rr, column=1, sticky="ew", pady=2)
    rr += 1

    ttk.Label(an_specific, text="Payments per year (for nominal annual %):").grid(
        row=rr, column=0, sticky="w", pady=2
    )
    ttk.Entry(an_specific, textvariable=an["n_per_y"]).grid(row=rr, column=1, sticky="ew", pady=2)
    rr += 1

    an_out = tk.Text(analyzer_tab, height=18, width=98)
    an_out.grid(row=r2 + 2, column=0, sticky="w", pady=(10, 0))
    an_out.config(state="disabled")

    def analyze_rates() -> None:
        p0 = float(shared["p0"].get())
        i0 = float(shared["i0"].get())
        n0 = int(shared["n0"].get())
        k = int(shared["k"].get())
        cost = float(shared["cost"].get())

        n1 = int(an["n1"].get())
        i_low = float(an["i_low"].get())
        step = float(an["step"].get())
        n_per_y = int(an["n_per_y"].get())

        if p0 <= 0:
            set_output(an_out, "Error: please enter a positive initial loan amount.")
            return
        if n0 <= 0 or n1 <= 0 or n_per_y <= 0:
            set_output(an_out, "Error: please enter positive values for n₀, n₁, and payments/year.")
            return
        if k < 0 or k > n0:
            set_output(an_out, "Error: completed periods (k) must be between 0 and n₀.")
            return
        if i0 <= 0:
            set_output(an_out, "Error: this analyzer expects i₀ > 0 for the existing loan.")
            return
        if i_low <= 0 or step <= 0:
            set_output(an_out, "Error: please enter positive values for i_low and Δi.")
            return

        a0 = periodic_payment(p0, i0, n0)
        bal = balance_after_k_payments(p0, i0, a0, k)
        if bal <= 1e-6:
            set_output(an_out, f"Loan is already paid off by period {k}.")
            return

        # status quo remaining payments
        t_pay0 = a0 * (n0 - k)

        # Build table until refinance total payments >= status quo remaining payments
        rows: list[list[object]] = []
        rows.append([i0, n_per_y * i0, t_pay0, a0, "Status quo (existing loan)"])

        interest = i_low
        safety = 200000
        while safety > 0:
            safety -= 1
            a1 = periodic_payment(bal, interest, n1)
            t_pay1 = a1 * n1 + cost
            rows.append([interest, n_per_y * interest, t_pay1, a1, ""])
            if t_pay1 >= t_pay0:
                break
            interest += step

        out_path = os.path.join(app_dir(), "breakeven_int.csv")
        with open(out_path, "w", newline="") as f:
            wcsv = csv.writer(f)
            wcsv.writerow(
                [
                    "Interest Rate per Period",
                    "Nominal Annual Interest Rate",
                    "Total Payments",
                    "Payment per Period",
                    "Notes",
                ]
            )
            for (ipr, iann, tpay, pay, note) in rows:
                wcsv.writerow(
                    [
                        round(float(ipr), 7),
                        f"{float(iann) * 100:.2f}%",
                        f"${float(tpay):,.2f}",
                        f"${float(pay):,.2f}",
                        str(note),
                    ]
                )

        preview = min(len(rows), 14)
        lines = [
            f"Wrote: {out_path}",
            "",
            "Preview:",
            "i/period | nominal annual | total payments | payment/period",
            "-" * 74,
        ]
        for idx in range(preview):
            ipr, iann, tpay, pay, _ = rows[idx]
            lines.append(f"{float(ipr):.7f} | {float(iann)*100:.2f}% | ${float(tpay):,.2f} | ${float(pay):,.2f}")
        if preview < len(rows):
            lines.append(f"... ({len(rows) - preview} more rows in CSV)")

        set_output(an_out, "\n".join(lines))

    ttk.Button(
        an_specific,
        text="Generate breakeven table (writes breakeven_int.csv)",
        command=analyze_rates,
    ).grid(row=rr, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    # ----------------------------- bottom buttons -------------------------------

    bottom = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
    bottom.grid(row=1, column=0, sticky="ew")
    bottom.columnconfigure(0, weight=1)
    bottom.columnconfigure(1, weight=1)

    def clear_all() -> None:
        for v in shared.values():
            try:
                v.set(0)
            except tk.TclError:
                pass
        for v in single.values():
            try:
                v.set(0)
            except tk.TclError:
                pass
        for kname, v in an.items():
            if kname == "step":
                v.set(0.00005)
            elif kname == "n_per_y":
                v.set(12)
            else:
                v.set(0)
        set_output(single_out, "")
        set_output(an_out, "")

    ttk.Button(bottom, text="Clear all", command=clear_all).grid(row=0, column=0, sticky="e", padx=(0, 8))
    ttk.Button(bottom, text="Quit", command=root.destroy).grid(row=0, column=1, sticky="w", padx=(8, 0))

    root.mainloop()


if __name__ == "__main__":
    main()

