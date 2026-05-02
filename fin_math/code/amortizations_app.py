import csv
import math
import os
import tkinter as tk
import tkinter.ttk as ttk


def next_available_path(base: str, ext: str = ".csv") -> str:
    i = 1
    while True:
        candidate = os.path.abspath(f"{base}_{i}{ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1


def periodic_payment(p: float, r: float, n: int) -> float:
    if n <= 0:
        return 0.0
    if r == 0:
        return p / n
    g = (1 + r) ** n
    return p * r * g / (g - 1)


def max_affordable_loan(a: float, r: float, n: int) -> float:
    if n <= 0 or a <= 0:
        return 0.0
    if r == 0:
        return a * n
    g = (1 + r) ** n
    return a * (g - 1) / (r * g)


def balance_at_period(p: float, r: float, a: float, k: int) -> float:
    if k <= 0:
        return p
    if r == 0:
        return max(0.0, p - k * a)
    g = (1 + r) ** k
    return max(0.0, g * p - a * (g - 1) / r)


def _sim_interest(p: float, r: float, a: float, n: int) -> float:
    balance, total = p, 0.0
    for _ in range(n):
        if balance <= 1e-6:
            break
        interest = r * balance
        total += interest
        principal = min(balance, a - interest) if a > interest else 0.0
        balance -= principal
    return total


def _sim_interest_extra(p: float, r: float, a: float, m: int, c: float) -> float:
    balance, total = p, 0.0
    for _ in range(max(0, m)):
        if balance <= 1e-6:
            return total
        interest = r * balance
        total += interest
        principal = min(balance, a - interest) if a > interest else 0.0
        balance -= principal

    new_pay, safety = a + c, 10**6
    while balance > 1e-6 and safety > 0:
        safety -= 1
        interest = r * balance
        total += interest
        principal = min(balance, new_pay - interest) if new_pay > interest else 0.0
        balance -= principal
    return total


def main() -> None:
    root = tk.Tk()
    root.title("Amortization Calculator")

    state = {
        "p": 0.0,
        "r": 0.0,
        "n": 0,
        "max_a": 0.0,
        "m": 0,
        "c": 0.0,
        "target_n": 0,
    }
    output_widgets: dict[str, tk.Text] = {}

    def quit_app() -> None:
        root.destroy()

    def clear() -> None:
        for widget in output_widgets.values():
            if widget is not None and widget.winfo_exists():
                try:
                    widget.delete("1.0", tk.END)
                except tk.TclError:
                    pass
        for entry in (q1, q2, q3, q4, q5, q6, q7, q8):
            entry.delete(0, tk.END)
        for var in (w, x, y, z, z2, m_var, c_var, target_var):
            var.set(0)

    def read_inputs() -> bool:
        try:
            p = float(w.get())
        except (tk.TclError, ValueError):
            p = 0.0
        try:
            yr_rate = float(x.get())
            pay_per_yr = float(y.get())
            num_yrs = float(z.get())
        except (tk.TclError, ValueError):
            return False
        if pay_per_yr <= 0 or num_yrs <= 0:
            return False
        try:
            max_a = float(z2.get())
        except (tk.TclError, ValueError):
            max_a = 0.0
        state["p"] = p
        state["r"] = (yr_rate / 100.0) / pay_per_yr
        state["n"] = int(round(pay_per_yr * num_yrs))
        state["max_a"] = max_a
        return True

    def read_extra_inputs() -> bool:
        try:
            state["m"] = int(round(float(m_var.get())))
        except (tk.TclError, ValueError):
            state["m"] = 0
        try:
            state["c"] = float(c_var.get())
        except (tk.TclError, ValueError):
            state["c"] = 0.0
        try:
            state["target_n"] = int(round(float(target_var.get())))
        except (tk.TclError, ValueError):
            state["target_n"] = 0
        return True

    def output_parent(row: int) -> ttk.LabelFrame:
        return left_panel if row < 22 else right_panel

    def show_output(key: str, row: int, text: str, height: int = 1, width: int = 78) -> None:
        widget = output_widgets.get(key)
        parent = output_parent(row)
        target_row = row if row < 22 else row - 22
        if widget is None or not widget.winfo_exists() or widget.master != parent:
            widget = tk.Text(parent, height=height, width=width)
            widget.grid(row=target_row, column=0, columnspan=2, padx=6, pady=2, sticky="w")
            output_widgets[key] = widget
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)

    def show_payment() -> float | None:
        if not read_inputs():
            return None
        p, r, n = state["p"], state["r"], state["n"]
        if p <= 0:
            return None
        epa = periodic_payment(p, r, n)
        show_output("s", 9, f"The payment amount per period is: ${epa:,.2f}", height=1, width=52)
        return epa

    def show_max_loan() -> None:
        if not read_inputs():
            return
        a_, r, n = state["max_a"], state["r"], state["n"]
        if a_ <= 0:
            return
        loan = max_affordable_loan(a_, r, n)
        show_output("t", 18, f"Maximum affordable mortgage: ${loan:,.2f}", height=1, width=52)

    def breakdown() -> None:
        epa = show_payment()
        if epa is None:
            return
        p, r, n = state["p"], state["r"], state["n"]
        rows: list[list[object]] = []
        balance = p
        for i in range(1, n + 1):
            interest = r * balance
            if i == n:
                principal = balance
                payment_this_period = principal + interest
            else:
                principal = epa - interest
                payment_this_period = epa
            balance -= principal
            rows.append(
                [
                    i,
                    round(payment_this_period, 2),
                    round(interest, 2),
                    round(principal, 2),
                    round(max(balance, 0.0), 2),
                ]
            )
        out_path = next_available_path("breakdown")
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Period", "Payment", "Interest", "Principal", "Balance"])
            writer.writerows(rows)
        show_output("msg", 20, "Breakdown written to: " + out_path, height=1, width=78)

    def compute_extra_payoff() -> None:
        if not read_inputs() or not read_extra_inputs():
            return
        p, r, n = state["p"], state["r"], state["n"]
        m, c = state["m"], state["c"]
        m = max(0, m)
        if p <= 0 or c <= 0:
            show_output(
                "extra_result",
                30,
                "Please enter a loan amount (P > 0) and extra payment (C > 0).",
                height=2,
            )
            return

        a = periodic_payment(p, r, n)
        b_m = balance_at_period(p, r, a, m)
        if b_m <= 1e-6:
            show_output(
                "extra_result",
                30,
                f"Loan is already paid off by period {m} at the regular payment A.",
                height=2,
            )
            return

        new_pay = a + c
        if r > 0 and new_pay <= r * b_m:
            show_output(
                "extra_result",
                30,
                "Error: extra payment too small -- does not cover the "
                "interest accruing on the remaining balance.",
                height=2,
            )
            return

        k = (
            math.log(new_pay / (new_pay - r * b_m)) / math.log(1 + r)
            if r > 0
            else b_m / new_pay
        )
        k_ceil = max(0, math.ceil(k))
        total_periods = m + k
        periods_saved = max(0, n - (m + k_ceil))

        orig_int = _sim_interest(p, r, a, n)
        new_int = _sim_interest_extra(p, r, a, m, c)

        text = (
            f"Regular payment A:               ${a:,.2f}\n"
            f"Balance after {m} periods:          ${b_m:,.2f}\n"
            f"New total payment (A + C):       ${new_pay:,.2f}\n"
            f"Remaining periods k:              {k:.2f}  (rounds up to {k_ceil} full periods)\n"
            f"Total periods required:           {m} + {k:.2f} = {total_periods:.2f}  -> {m + k_ceil} payments\n"
            f"Periods saved vs. original term:  {periods_saved}\n"
            f"Original total interest:          ${orig_int:,.2f}\n"
            f"New total interest:               ${new_int:,.2f}\n"
            f"Interest saved:                   ${orig_int - new_int:,.2f}"
        )
        show_output("extra_result", 30, text, height=9)

    def compute_required_extra() -> None:
        if not read_inputs() or not read_extra_inputs():
            return
        p, r, n = state["p"], state["r"], state["n"]
        m, t = state["m"], state["target_n"]
        m = max(0, m)

        if p <= 0:
            show_output("target_result", 34, "Please enter a loan amount (P > 0).", height=2)
            return
        if t <= m:
            show_output(
                "target_result",
                34,
                "Error: target total periods must be greater than the number of initial periods m.",
                height=2,
            )
            return
        if t >= n:
            show_output(
                "target_result",
                34,
                "Note: target is at or beyond the original term -- no extra payment is needed.",
                height=2,
            )
            return

        a = periodic_payment(p, r, n)
        b_m = balance_at_period(p, r, a, m)
        if b_m <= 1e-6:
            show_output(
                "target_result",
                34,
                f"Loan is already paid off by period {m} at the regular payment A.",
                height=2,
            )
            return

        k = t - m
        a_new = periodic_payment(b_m, r, k)
        c = a_new - a

        orig_int = _sim_interest(p, r, a, n)
        new_int = _sim_interest_extra(p, r, a, m, max(c, 0.0))
        text = (
            f"Regular payment A:               ${a:,.2f}\n"
            f"Balance after {m} periods:          ${b_m:,.2f}\n"
            f"Target total periods:             {t}  (k = {k} remaining after period {m})\n"
            f"Required total payment (A + C):  ${a_new:,.2f}\n"
            f"Required extra payment C:        ${c:,.2f}\n"
            f"Periods saved vs. original term:  {n - t}\n"
            f"Original total interest:          ${orig_int:,.2f}\n"
            f"New total interest:               ${new_int:,.2f}\n"
            f"Interest saved:                   ${orig_int - new_int:,.2f}"
        )
        show_output("target_result", 34, text, height=9)

    def breakdown_extra() -> None:
        if not read_inputs() or not read_extra_inputs():
            return
        p, r, n = state["p"], state["r"], state["n"]
        m, c = state["m"], state["c"]
        m = max(0, m)
        if p <= 0:
            return

        a = periodic_payment(p, r, n)
        rows: list[list[object]] = []
        balance = p

        for period in range(1, m + 1):
            if balance <= 1e-6:
                break
            interest = r * balance
            payment = a
            if payment >= balance + interest:
                payment = balance + interest
                principal = balance
                balance = 0.0
                phase = "Final (adjusted)"
            else:
                principal = payment - interest
                balance -= principal
                phase = "Regular"
            rows.append(
                [
                    period,
                    round(payment, 2),
                    round(interest, 2),
                    round(principal, 2),
                    round(max(balance, 0.0), 2),
                    phase,
                ]
            )

        new_pay = a + c if c > 0 else a
        period, safety = (int(rows[-1][0]) if rows else 0), 10**6
        while balance > 1e-6 and safety > 0:
            safety -= 1
            period += 1
            interest = r * balance
            if new_pay >= balance + interest:
                payment = balance + interest
                principal = balance
                balance = 0.0
                phase = "Final (adjusted)"
            else:
                payment = new_pay
                principal = payment - interest
                balance -= principal
                phase = "Extra" if c > 0 else "Regular"
            rows.append(
                [
                    period,
                    round(payment, 2),
                    round(interest, 2),
                    round(principal, 2),
                    round(max(balance, 0.0), 2),
                    phase,
                ]
            )

        out_path = next_available_path("breakdown_extra")
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Period", "Payment", "Interest", "Principal", "Balance", "Phase"])
            writer.writerows(rows)
        show_output("extra_msg", 38, out_path, height=1, width=78)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    main_frame = ttk.Frame(root, padding=8)
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    left_panel = ttk.LabelFrame(main_frame, text="Core Loan Calculations", padding=8)
    left_panel.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="nsew")
    left_panel.columnconfigure(1, weight=1)

    right_panel = ttk.LabelFrame(main_frame, text="Additional Principal Payments", padding=8)
    right_panel.grid(row=0, column=1, padx=(8, 0), pady=0, sticky="nsew")
    right_panel.columnconfigure(1, weight=1)

    button_bar = ttk.Frame(main_frame, padding=(0, 8, 0, 0))
    button_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
    button_bar.columnconfigure(0, weight=1)
    button_bar.columnconfigure(1, weight=1)

    tk.Label(
        left_panel,
        text="Amount of loan\n(leave at 0 if using the Max affordable loan option):",
    ).grid(row=1, column=0, padx=3, sticky="w")
    w = tk.DoubleVar()
    q1 = tk.Entry(left_panel, textvariable=w)
    q1.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

    tk.Label(left_panel, text="Annual interest percentage (%):").grid(row=2, column=0, padx=3, sticky="w")
    x = tk.DoubleVar()
    q2 = tk.Entry(left_panel, textvariable=x)
    q2.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

    tk.Label(left_panel, text="Number of payments per year:").grid(row=3, column=0, padx=3, sticky="w")
    y = tk.DoubleVar()
    q3 = tk.Entry(left_panel, textvariable=y)
    q3.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

    tk.Label(left_panel, text="Length of loan in years:").grid(row=4, column=0, padx=3, sticky="w")
    z = tk.DoubleVar()
    q4 = tk.Entry(left_panel, textvariable=z)
    q4.grid(row=4, column=1, padx=5, pady=3, sticky="ew")

    tk.Label(
        left_panel,
        text="Max affordable payment per period\n(e.g., max one can afford to pay per month):",
    ).grid(row=5, column=0, padx=3, sticky="w")
    z2 = tk.DoubleVar()
    q5 = tk.Entry(left_panel, textvariable=z2)
    q5.grid(row=5, column=1, padx=5, pady=3, sticky="ew")

    tk.Button(left_panel, text="Compute periodic payment", command=show_payment).grid(
        row=8, column=0, columnspan=2, padx=3, pady=7, sticky="ew"
    )

    tk.Button(
        left_panel,
        text="Max affordable loan given interest rate,\n"
        "number of payments per year, length of loan,\n"
        "and max affordable payment per period",
        command=show_max_loan,
    ).grid(row=17, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    tk.Button(
        left_panel,
        text="Compute Interest-Principal breakdown\n(result placed in breakdown_N.csv, auto-numbered)",
        command=breakdown,
    ).grid(row=19, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    tk.Label(
        right_panel,
        text="Number of initial periods m\n(extra payment starts at period m + 1; enter 0 to start immediately):",
    ).grid(row=2, column=0, padx=3, sticky="w")
    m_var = tk.DoubleVar()
    q6 = tk.Entry(right_panel, textvariable=m_var)
    q6.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

    tk.Label(right_panel, text="Additional principal payment C per period:").grid(
        row=3, column=0, padx=3, sticky="w"
    )
    c_var = tk.DoubleVar()
    q7 = tk.Entry(right_panel, textvariable=c_var)
    q7.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

    tk.Label(
        right_panel,
        text="Target total payoff periods\n(used only with the 'Compute required extra payment' button):",
    ).grid(row=4, column=0, padx=3, sticky="w")
    target_var = tk.DoubleVar()
    q8 = tk.Entry(right_panel, textvariable=target_var)
    q8.grid(row=4, column=1, padx=5, pady=3, sticky="ew")

    tk.Button(
        right_panel,
        text="Compute payoff with extra payment C\n(shows new term and interest saved)",
        command=compute_extra_payoff,
    ).grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    tk.Button(
        right_panel,
        text="Compute required extra payment for target payoff\n(shows C needed to reach the target total periods)",
        command=compute_required_extra,
    ).grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    tk.Button(
        right_panel,
        text="Full breakdown with extra payments\n(result placed in breakdown_extra_N.csv, auto-numbered)",
        command=breakdown_extra,
    ).grid(row=14, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    tk.Label(right_panel, text="Breakdown written to:").grid(row=15, column=0, padx=3, pady=5, sticky="w")

    tk.Button(button_bar, text="Clear", command=clear).grid(row=0, column=0, pady=8, sticky="e", padx=(0, 6))
    tk.Button(button_bar, text="Quit", command=quit_app).grid(row=0, column=1, pady=8, sticky="w", padx=(6, 0))

    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)

    root.mainloop()


if __name__ == "__main__":
    main()
