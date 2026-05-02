"""Bond Schedule Creator.

This is the canonical implementation used by the book examples in Section 6.

Run directly:

    python bond_schedule_creator.py

From Jupyter, you can run the GUI with:

    from bond_schedule_creator import main
    main()
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass

import tkinter as tk
from tkinter import messagebox


def money(x: float) -> str:
    """Format currency like the book tables; negatives shown in parentheses."""
    ax = abs(x)
    if x < 0:
        return f"(${ax:,.2f})"
    return f"${ax:,.2f}"


def output_csv_path() -> str:
    # Prefer the script directory when running as a file; fall back to cwd (e.g., notebooks).
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:  # pragma: no cover
        here = os.getcwd()
    return os.path.join(here, "bond_schedule.csv")


def bring_to_front(win: tk.Tk) -> None:
    win.lift()
    win.attributes("-topmost", True)
    win.after(250, lambda: win.attributes("-topmost", False))


@dataclass
class BondUI:
    root: tk.Tk
    face: tk.DoubleVar
    periods: tk.DoubleVar
    coupon_rate: tk.DoubleVar
    yield_rate: tk.DoubleVar
    face_entry: tk.Entry
    periods_entry: tk.Entry
    coupon_entry: tk.Entry
    yield_entry: tk.Entry


def parse_inputs(ui: BondUI) -> tuple[float, int, float, float] | None:
    try:
        face = float(ui.face.get())
        n = int(round(float(ui.periods.get())))
        coupon_per_period = float(ui.coupon_rate.get())
        yld_per_period = float(ui.yield_rate.get())
    except (tk.TclError, TypeError, ValueError):
        messagebox.showerror("Invalid input", "Please enter numeric values for all fields.")
        return None

    if face <= 0:
        messagebox.showerror("Invalid input", "Redemption value (face) must be positive.")
        return None
    if n <= 0:
        messagebox.showerror("Invalid input", "Number of payment periods must be a positive integer.")
        return None
    if coupon_per_period < 0:
        messagebox.showerror("Invalid input", "Coupon rate per period must be nonnegative.")
        return None
    if yld_per_period < 0:
        messagebox.showerror("Invalid input", "Yield rate per period must be nonnegative.")
        return None

    return face, n, coupon_per_period, yld_per_period


def purchase_price(face: float, n: int, coupon: float, yld: float) -> float:
    """Standard bond price: PV(coupons) + PV(redemption). Handles yld == 0."""
    if yld == 0.0:
        return face + coupon * n
    g = (1.0 + yld) ** (-n)
    annuity = (1.0 - g) / yld
    return coupon * annuity + face * g


def compute_schedule(ui: BondUI) -> None:
    parsed = parse_inputs(ui)
    if parsed is None:
        return

    face, n, i, yr = parsed
    coupon = face * i
    p = purchase_price(face, n, coupon, yr)

    bv: list[float] = [p]
    adj: list[float] = [0.0]
    ibv: list[float] = [0.0]

    for _ in range(1, n + 1):
        interest = yr * bv[-1]
        adjustment = coupon - interest
        book = bv[-1] - adjustment
        ibv.append(interest)
        adj.append(adjustment)
        bv.append(book)

    # Remove floating-point dust so the final book value matches redemption exactly.
    if bv:
        bv[-1] = float(face)
        if n > 0:
            ibv[-1] = yr * bv[-2]
            adj[-1] = coupon - ibv[-1]

    out_path = output_csv_path()
    try:
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow(
                ["Period", "Coupon", "Interest on Book Value", "Book Value Adjustment", "Book Value"]
            )
            writer.writerow(["0", "-", "-", "-", money(bv[0])])

            for k in range(1, n + 1):
                writer.writerow([k, money(coupon), money(ibv[k]), money(adj[k]), money(bv[k])])

            coupon_total = coupon * n
            ibv_total = sum(ibv[1:])
            adj_total = sum(adj[1:])
            writer.writerow(["Totals", money(coupon_total), money(ibv_total), money(adj_total), "-"])
    except OSError as exc:
        messagebox.showerror("Could not write CSV", f"Failed to write:\n{out_path}\n\n{exc}")
        return

    messagebox.showinfo("Wrote schedule", f"Bond schedule written to:\n{out_path}")


def clear_fields(ui: BondUI) -> None:
    ui.face_entry.delete(0, tk.END)
    ui.periods_entry.delete(0, tk.END)
    ui.coupon_entry.delete(0, tk.END)
    ui.yield_entry.delete(0, tk.END)
    ui.face.set(0)
    ui.periods.set(0)
    ui.coupon_rate.set(0)
    ui.yield_rate.set(0)


def build_ui() -> BondUI:
    root = tk.Tk()
    root.title("Bond Schedule Creator")
    bring_to_front(root)

    tk.Label(
        root,
        text=(
            "Enter rates as decimals per period (for example, type 0.05 for 5% per period). "
            "Do not enter 5 to mean 5%."
        ),
        justify="left",
        wraplength=520,
    ).grid(row=1, column=1, columnspan=2, padx=3, pady=(6, 10), sticky="w")

    tk.Label(root, text="Redemption value of bond:").grid(row=2, column=1, padx=3, sticky="w")
    face = tk.DoubleVar()
    face_entry = tk.Entry(root, textvariable=face)
    face_entry.grid(row=2, column=2, padx=5, pady=3, sticky="w")

    tk.Label(root, text="Number of payment periods:").grid(row=3, column=1, padx=3, sticky="w")
    periods = tk.DoubleVar()
    periods_entry = tk.Entry(root, textvariable=periods)
    periods_entry.grid(row=3, column=2, padx=5, pady=3, sticky="w")

    tk.Label(root, text="Coupon rate per period:").grid(row=5, column=1, padx=3, sticky="w")
    coupon_rate = tk.DoubleVar()
    coupon_entry = tk.Entry(root, textvariable=coupon_rate)
    coupon_entry.grid(row=5, column=2, padx=5, pady=3, sticky="w")

    tk.Label(root, text="Yield rate per period:").grid(row=6, column=1, padx=3, sticky="w")
    yield_rate = tk.DoubleVar()
    yield_entry = tk.Entry(root, textvariable=yield_rate)
    yield_entry.grid(row=6, column=2, padx=5, pady=3, sticky="w")

    ui = BondUI(
        root=root,
        face=face,
        periods=periods,
        coupon_rate=coupon_rate,
        yield_rate=yield_rate,
        face_entry=face_entry,
        periods_entry=periods_entry,
        coupon_entry=coupon_entry,
        yield_entry=yield_entry,
    )

    tk.Button(root, text="Compute bond schedule", command=lambda: compute_schedule(ui)).grid(
        row=8, column=1, padx=3, pady=7
    )
    tk.Button(root, text="Clear", command=lambda: clear_fields(ui)).grid(row=23, column=1, pady=5)
    tk.Button(root, text="Quit", command=root.destroy).grid(row=23, column=2, padx=3, pady=5, sticky="w")

    return ui


def main() -> None:
    ui = build_ui()
    ui.root.mainloop()


if __name__ == "__main__":
    main()
