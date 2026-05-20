"""Stock valuation GUI (dividend discount and P/E tools).

Supports:
  - Constant dividend model (perpetuity): P = D / r
  - Gordon Growth Model: P = D1 / (r - g), with D1 = D0 * (1 + g)
  - Required return decomposition: r = D1/P + g
  - P/E ratio (full payout): P/E = 1 / (r - g), with E1 = E0 * (1 + g)

Run directly:

    python stock_valuation.py

From Jupyter:

    from stock_valuation import main
    main()
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

# Shown at top of GUI and echoed on rate field labels.
RATE_DECIMAL_NOTE = (
    "Rates r and g must be decimals per period (type 0.08 for 8%), "
    "not percentages (do not type 8 or 8%)."
)


def money(x: float) -> str:
    ax = abs(x)
    if x < 0:
        return f"(${ax:,.2f})"
    return f"${ax:,.2f}"


def pct(x: float, digits: int = 2) -> str:
    return f"{100.0 * x:.{digits}f}%"


def bring_to_front(win: tk.Tk) -> None:
    win.lift()
    try:
        win.attributes("-topmost", True)
        win.after(250, lambda: win.attributes("-topmost", False))
    except tk.TclError:
        pass


def d1_from_d0(d0: float, g: float) -> float:
    return d0 * (1.0 + g)


def e1_from_e0(e0: float, g: float) -> float:
    return e0 * (1.0 + g)


def constant_dividend_price(d: float, r: float) -> float:
    if r <= 0:
        raise ValueError("Required return r must be positive.")
    return d / r


def constant_dividend_required_return(d: float, p: float) -> float:
    if p <= 0:
        raise ValueError("Price P must be positive.")
    return d / p


def gordon_price(d1: float, r: float, g: float) -> float:
    spread = r - g
    if spread <= 0:
        raise ValueError("Gordon model requires r > g (so r - g > 0).")
    return d1 / spread


def gordon_required_return(d1: float, p: float, g: float) -> float:
    if p <= 0:
        raise ValueError("Price P must be positive.")
    return d1 / p + g


def gordon_growth_rate(d1: float, p: float, r: float) -> float:
    if p <= 0:
        raise ValueError("Price P must be positive.")
    return r - d1 / p


def return_decomposition(d1: float, p: float, g: float) -> tuple[float, float, float]:
    if p <= 0:
        raise ValueError("Price P must be positive.")
    dividend_yield = d1 / p
    capital_gains_yield = g
    total_return = dividend_yield + capital_gains_yield
    return dividend_yield, capital_gains_yield, total_return


def pe_ratio(p: float, e1: float) -> float:
    if e1 <= 0:
        raise ValueError("Earnings E1 must be positive.")
    return p / e1


def earnings_yield(r: float, g: float) -> float:
    spread = r - g
    if spread <= 0:
        raise ValueError("Requires r > g for a positive earnings yield.")
    return spread


def set_output(box: tk.Text, text: str) -> None:
    box.config(state="normal")
    box.delete("1.0", tk.END)
    box.insert(tk.END, text)
    box.config(state="disabled")


def _read_float(entry: ttk.Entry, label: str) -> float:
    raw = entry.get().strip()
    if not raw:
        raise ValueError(f"Enter a value for {label}.")
    return float(raw)


def _optional_float(entry: ttk.Entry) -> float | None:
    raw = entry.get().strip()
    if not raw:
        return None
    return float(raw)


def _warn_rate(name: str, value: float) -> None:
    if value > 0.5:
        messagebox.showwarning(
            "Unusual rate",
            f"{name} = {value:.1%} per period seems very high. {RATE_DECIMAL_NOTE}",
        )


class StockValuationApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Stock Valuation Calculator")
        bring_to_front(root)

        main = ttk.Frame(root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        ttk.Label(
            main,
            text=(
                f"{RATE_DECIMAL_NOTE} "
                "For growth models, enter D0 or E0 only; D1 and E1 are computed as "
                "D0 * (1 + g) and E0 * (1 + g)."
            ),
            wraplength=720,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        nb = ttk.Notebook(main)
        nb.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        self.tab_constant = ttk.Frame(nb, padding=10)
        self.tab_gordon = ttk.Frame(nb, padding=10)
        self.tab_return_split = ttk.Frame(nb, padding=10)
        self.tab_pe = ttk.Frame(nb, padding=10)
        nb.add(self.tab_constant, text="Constant Dividend")
        nb.add(self.tab_gordon, text="Gordon Growth")
        nb.add(self.tab_return_split, text="Return Decomposition")
        nb.add(self.tab_pe, text="P/E Ratio")

        self._build_constant_tab()
        self._build_gordon_tab()
        self._build_return_split_tab()
        self._build_pe_tab()

        ttk.Button(main, text="Quit", command=root.destroy).grid(row=2, column=0, pady=(10, 0), sticky="w")

    def _add_output(self, parent: ttk.Frame, row: int) -> tk.Text:
        out = tk.Text(parent, height=14, width=88, font=("Consolas", 10))
        out.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        out.config(state="disabled")
        parent.columnconfigure(0, weight=1)
        return out

    def _build_constant_tab(self) -> None:
        tab = self.tab_constant
        ttk.Label(
            tab,
            text="Constant dividend (perpetuity):  P = D / r   and   r = D / P  (dividend yield).",
            wraplength=680,
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        self.solve_constant = tk.StringVar(value="Price P")
        ttk.Label(tab, text="Solve for:").grid(row=1, column=0, sticky="w", pady=(8, 2))
        ttk.Combobox(
            tab,
            textvariable=self.solve_constant,
            values=("Price P", "Required return r", "Constant dividend D"),
            state="readonly",
            width=28,
        ).grid(row=1, column=1, sticky="w", pady=(8, 2))

        self.d_constant = self._labeled_entry(tab, 2, "D  (constant dividend per period):")
        self.r_constant = self._labeled_entry(
            tab, 3, "r  (required return; decimal per period, e.g. 0.08 not 8 or 8%):"
        )
        self.p_constant = self._labeled_entry(tab, 4, "P  (stock price):")

        self.out_constant = self._add_output(tab, 6)

        ttk.Button(tab, text="Compute", command=self._compute_constant).grid(row=5, column=0, pady=8, sticky="w")
        ttk.Button(
            tab,
            text="Clear",
            command=lambda: self._clear_tab(
                self.d_constant, self.r_constant, self.p_constant, self.out_constant
            ),
        ).grid(row=5, column=1, pady=8, sticky="w")

    def _build_gordon_tab(self) -> None:
        tab = self.tab_gordon
        ttk.Label(
            tab,
            text=(
                "Gordon Growth Model:  D1 = D0 * (1 + g),   P = D1 / (r - g),   "
                "r = D1/P + g.  Requires r > g."
            ),
            wraplength=680,
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        self.solve_gordon = tk.StringVar(value="Price P")
        ttk.Label(tab, text="Solve for:").grid(row=1, column=0, sticky="w", pady=(8, 2))
        ttk.Combobox(
            tab,
            textvariable=self.solve_gordon,
            values=("Price P", "Required return r", "Growth rate g", "D0 (prior dividend)"),
            state="readonly",
            width=28,
        ).grid(row=1, column=1, sticky="w", pady=(8, 2))

        self.d0_gordon = self._labeled_entry(tab, 2, "D0  (dividend just paid):")
        self.g_gordon = self._labeled_entry(
            tab, 3, "g  (growth rate; decimal per period, e.g. 0.04 not 4 or 4%):"
        )
        self.r_gordon = self._labeled_entry(
            tab, 4, "r  (required return; decimal per period, e.g. 0.08 not 8 or 8%):"
        )
        self.p_gordon = self._labeled_entry(tab, 5, "P  (stock price):")

        self.out_gordon = self._add_output(tab, 7)

        ttk.Button(tab, text="Compute", command=self._compute_gordon).grid(row=6, column=0, pady=8, sticky="w")
        ttk.Button(
            tab,
            text="Clear",
            command=lambda: self._clear_tab(
                self.d0_gordon, self.g_gordon, self.r_gordon, self.p_gordon, self.out_gordon
            ),
        ).grid(row=6, column=1, pady=8, sticky="w")

    def _build_return_split_tab(self) -> None:
        tab = self.tab_return_split
        ttk.Label(
            tab,
            text=(
                "Required return decomposition:  r = D1/P + g.  "
                "Dividend yield = D1/P; capital gains yield = g."
            ),
            wraplength=680,
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        self.d0_return = self._labeled_entry(tab, 1, "D0  (most recent dividend):")
        self.g_return = self._labeled_entry(
            tab, 2, "g  (growth rate; decimal per period, e.g. 0.05 not 5 or 5%):"
        )
        self.p_return = self._labeled_entry(tab, 3, "P  (current stock price):")

        self.out_return = self._add_output(tab, 5)

        ttk.Button(tab, text="Compute", command=self._compute_return_split).grid(
            row=4, column=0, pady=8, sticky="w"
        )
        ttk.Button(
            tab,
            text="Clear",
            command=lambda: self._clear_tab(
                self.d0_return, self.g_return, self.p_return, self.out_return
            ),
        ).grid(row=4, column=1, pady=8, sticky="w")

    def _build_pe_tab(self) -> None:
        tab = self.tab_pe
        ttk.Label(
            tab,
            text=(
                "P/E under full payout:  D1 = E1,   P = E1/(r - g),   "
                "P/E = P/E1 = 1/(r - g).  E1 = E0 * (1 + g)."
            ),
            wraplength=680,
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        self.solve_pe = tk.StringVar(value="Show all (P/E and earnings yield)")
        ttk.Label(tab, text="Solve for:").grid(row=1, column=0, sticky="w", pady=(8, 2))
        ttk.Combobox(
            tab,
            textvariable=self.solve_pe,
            values=(
                "Show all (P/E and earnings yield)",
                "Price P",
                "Required return r",
                "Growth rate g",
                "E0 (prior earnings per share)",
            ),
            state="readonly",
            width=36,
        ).grid(row=1, column=1, sticky="w", pady=(8, 2))

        self.e0_pe = self._labeled_entry(tab, 2, "E0  (most recent EPS):")
        self.g_pe = self._labeled_entry(
            tab, 3, "g  (growth rate; decimal per period, e.g. 0.04 not 4 or 4%):"
        )
        self.r_pe = self._labeled_entry(
            tab, 4, "r  (required return; decimal per period, e.g. 0.08 not 8 or 8%):"
        )
        self.p_pe = self._labeled_entry(tab, 5, "P  (stock price):")

        self.out_pe = self._add_output(tab, 7)

        ttk.Button(tab, text="Compute", command=self._compute_pe).grid(row=6, column=0, pady=8, sticky="w")
        ttk.Button(
            tab,
            text="Clear",
            command=lambda: self._clear_tab(self.e0_pe, self.g_pe, self.r_pe, self.p_pe, self.out_pe),
        ).grid(row=6, column=1, pady=8, sticky="w")

    @staticmethod
    def _labeled_entry(parent: ttk.Frame, row: int, label: str) -> ttk.Entry:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(parent, width=24)
        entry.grid(row=row, column=1, sticky="w", pady=2)
        return entry

    @staticmethod
    def _clear_tab(*widgets: ttk.Entry | tk.Text) -> None:
        for widget in widgets:
            if isinstance(widget, tk.Text):
                widget.config(state="normal")
                widget.delete("1.0", tk.END)
                widget.config(state="disabled")
            else:
                widget.delete(0, tk.END)

    def _compute_constant(self) -> None:
        target = self.solve_constant.get()
        try:
            d = _optional_float(self.d_constant)
            r = _optional_float(self.r_constant)
            p = _optional_float(self.p_constant)

            lines = ["Constant dividend model", "=" * 52, ""]

            if target == "Price P":
                if d is None or r is None:
                    raise ValueError("Enter D and r to solve for price.")
                _warn_rate("r", r)
                price = constant_dividend_price(d, r)
                lines += [
                    f"Given:  D = {money(d)},  r = {pct(r)}",
                    "Formula:  P = D / r",
                    f"Price:  P = {money(price)}",
                ]
            elif target == "Required return r":
                if d is None or p is None:
                    raise ValueError("Enter D and P to solve for required return.")
                req = constant_dividend_required_return(d, p)
                _warn_rate("r", req)
                lines += [
                    f"Given:  D = {money(d)},  P = {money(p)}",
                    "Formula:  r = D / P  (dividend yield)",
                    f"Required return:  r = {pct(req)}  ({req:.6f})",
                ]
            else:
                if r is None or p is None:
                    raise ValueError("Enter r and P to solve for dividend.")
                if r <= 0:
                    raise ValueError("r must be positive.")
                div = r * p
                lines += [
                    f"Given:  r = {pct(r)},  P = {money(p)}",
                    "From P = D / r:  D = r * P",
                    f"Constant dividend:  D = {money(div)} per period",
                ]

            set_output(self.out_constant, "\n".join(lines) + "\n")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Invalid input", str(exc))

    def _compute_gordon(self) -> None:
        target = self.solve_gordon.get()
        try:
            d0 = _optional_float(self.d0_gordon)
            g = _optional_float(self.g_gordon)
            r = _optional_float(self.r_gordon)
            p = _optional_float(self.p_gordon)

            lines = ["Gordon Growth Model", "=" * 52, ""]

            if target == "Price P":
                if d0 is None or g is None or r is None:
                    raise ValueError("Enter D0, g, and r to solve for price.")
                d1 = d1_from_d0(d0, g)
                _warn_rate("r", r)
                _warn_rate("g", g)
                price = gordon_price(d1, r, g)
                lines += [
                    f"D1 = D0 * (1 + g) = {money(d0)} * {1 + g:.6f} = {money(d1)}",
                    f"Given:  r = {pct(r)},  g = {pct(g)}",
                    f"Formula:  P = D1 / (r - g) = {money(d1)} / {pct(r - g)}",
                    f"Price:  P = {money(price)}",
                ]
            elif target == "Required return r":
                if d0 is None or g is None or p is None:
                    raise ValueError("Enter D0, g, and P to solve for r.")
                d1 = d1_from_d0(d0, g)
                req = gordon_required_return(d1, p, g)
                _warn_rate("r", req)
                lines += [
                    f"D1 = D0 * (1 + g) = {money(d1)}",
                    f"Given:  P = {money(p)},  g = {pct(g)}",
                    f"Formula:  r = D1/P + g = {money(d1)}/{money(p)} + {pct(g)}",
                    f"Required return:  r = {pct(req)}  ({req:.6f})",
                ]
            elif target == "Growth rate g":
                if d0 is None or r is None or p is None:
                    raise ValueError("Enter D0, r, and P to solve for g.")
                if p <= 0:
                    raise ValueError("P must be positive.")
                g_implied = (p * r - d0) / (p + d0)
                d1_check = d1_from_d0(d0, g_implied)
                lines += [
                    f"Given:  D0 = {money(d0)},  r = {pct(r)},  P = {money(p)}",
                    "From P = D0 * (1 + g) / (r - g), solving for g:",
                    f"Implied growth:  g = {pct(g_implied)}  ({g_implied:.6f})",
                    f"Check:  D1 = D0 * (1 + g) = {money(d1_check)}",
                    f"Check:  P = D1/(r - g) = {money(gordon_price(d1_check, r, g_implied))}",
                ]
            else:
                if g is None or r is None or p is None:
                    raise ValueError("Enter g, r, and P to solve for D0.")
                spread = r - g
                if spread <= 0:
                    raise ValueError("Requires r > g.")
                d1 = p * spread
                d0_sol = d1 / (1.0 + g)
                lines += [
                    f"Given:  r = {pct(r)},  g = {pct(g)},  P = {money(p)}",
                    f"From P = D1/(r - g):  D1 = P * (r - g) = {money(d1)}",
                    f"From D1 = D0 * (1 + g):  D0 = D1/(1 + g) = {money(d0_sol)}",
                ]

            set_output(self.out_gordon, "\n".join(lines) + "\n")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Invalid input", str(exc))

    def _compute_return_split(self) -> None:
        try:
            d0 = _read_float(self.d0_return, "D0")
            g = _read_float(self.g_return, "g")
            p = _read_float(self.p_return, "P")
            d1 = d1_from_d0(d0, g)
            div_y, cap_y, total = return_decomposition(d1, p, g)
            _warn_rate("g", g)

            lines = [
                "Required return decomposition",
                "=" * 52,
                "",
                f"D1 = D0 * (1 + g) = {money(d0)} * {1 + g:.6f} = {money(d1)}",
                f"P = {money(p)}",
                "",
                f"Dividend yield (D1/P):     {pct(div_y)}",
                f"Capital gains yield (g):   {pct(cap_y)}",
                f"Total required return r:   {pct(total)}  ({total:.6f})",
                "",
                "Formula:  r = D1/P + g",
                f"  {total:.6f} = {d1:.4f}/{p:.4f} + {g:.6f}",
            ]
            set_output(self.out_return, "\n".join(lines) + "\n")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Invalid input", str(exc))

    def _compute_pe(self) -> None:
        target = self.solve_pe.get()
        try:
            e0 = _optional_float(self.e0_pe)
            g = _optional_float(self.g_pe)
            r = _optional_float(self.r_pe)
            p = _optional_float(self.p_pe)

            lines = ["P/E ratio (100% payout: D1 = E1)", "=" * 52, ""]

            if target == "Show all (P/E and earnings yield)":
                if e0 is None or g is None or r is None or p is None:
                    raise ValueError("Enter E0, g, r, and P.")
                e1 = e1_from_e0(e0, g)
                pe = pe_ratio(p, e1)
                ey = earnings_yield(r, g)
                model_p = gordon_price(e1, r, g)
                lines += [
                    f"E1 = E0 * (1 + g) = {money(e0)} * {1 + g:.6f} = {money(e1)}",
                    f"Given:  P = {money(p)},  r = {pct(r)},  g = {pct(g)}",
                    "",
                    f"P/E = P / E1 = {pe:,.2f}",
                    f"Formula:  P/E = 1/(r - g) = 1/{pct(r - g)} = {1 / (r - g):,.2f}",
                    f"Earnings yield (E1/P = r - g):  {pct(ey)}",
                    f"Model price P = E1/(r - g):  {money(model_p)}",
                ]
            elif target == "Price P":
                if e0 is None or g is None or r is None:
                    raise ValueError("Enter E0, g, and r.")
                e1 = e1_from_e0(e0, g)
                price = gordon_price(e1, r, g)
                lines += [
                    f"E1 = E0 * (1 + g) = {money(e1)}",
                    "Formula:  P = E1/(r - g)",
                    f"Price:  P = {money(price)}",
                    f"Implied P/E:  {pe_ratio(price, e1):,.2f}",
                ]
            elif target == "Required return r":
                if e0 is None or g is None or p is None:
                    raise ValueError("Enter E0, g, and P.")
                e1 = e1_from_e0(e0, g)
                req = gordon_required_return(e1, p, g)
                lines += [
                    f"E1 = {money(e1)}",
                    f"From r = E1/P + g:  r = {pct(req)}",
                    f"Earnings yield r - g:  {pct(req - g)}",
                ]
            elif target == "Growth rate g":
                if e0 is None or r is None or p is None:
                    raise ValueError("Enter E0, r, and P.")
                g_implied = (p * r - e0) / (p + e0)
                e1 = e1_from_e0(e0, g_implied)
                lines += [
                    f"Given:  E0 = {money(e0)},  r = {pct(r)},  P = {money(p)}",
                    f"Implied g:  {pct(g_implied)}",
                    f"Check E1 = {money(e1)},  P/E = {pe_ratio(p, e1):,.2f}",
                ]
            else:
                if g is None or r is None or p is None:
                    raise ValueError("Enter g, r, and P.")
                spread = r - g
                if spread <= 0:
                    raise ValueError("Requires r > g.")
                e1 = p * spread
                e0_sol = e1 / (1.0 + g)
                lines += [
                    f"From P = E1/(r - g):  E1 = {money(e1)}",
                    f"From E1 = E0 * (1 + g):  E0 = {money(e0_sol)}",
                ]

            set_output(self.out_pe, "\n".join(lines) + "\n")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Invalid input", str(exc))


def main() -> None:
    root = tk.Tk()
    StockValuationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
