# Loan Refinance Calculator
# This program analyzes the refinancing of a loan (such as s mortgage).
#
# It is assumed that the period for the original loan (e.g., a month) is
# the same as the period for the new loan. 

import tkinter as tk 

root = tk.Tk()
root.title('Loan Refinancing Calculator')

def quit():
    root.destroy()
    
def clear():
    # This function clears the various input and output lines in the user interface
    q1.delete(0,tk.END)
    w.set(0)
    q2.delete(0,tk.END)
    x.set(0)
    q3.delete(0,tk.END)
    y.set(0)
    q4.delete(0,tk.END)
    z.set(0)
    
    q5.delete(0,tk.END)
    w1.set(0)
    q6.delete(0,tk.END)
    x1.set(0)
    q7.delete(0,tk.END)
    y1.set(0)
    
    
def get_input():
    # This function gets the input needed for the other functions
    global p0,i0,n0,n0_com,cost,i1,n1
    
    # Information for the initial loan that is to be refinanced
    p0 = w.get()       # principal for initial loan
    i0 = x.get()       # interest rate per period for initial loan
    n0 = y.get()       # number of periods for initial loan
    n0_com = z.get()   # number of periods completed when refinancing is to start
    
    # Information for refinancing
    cost = w1.get()    # Cost of refinancing, including penality for terminating initial loan
    i1 = x1.get()      # interest rate for new loan
    n1 = y1.get()      # number of periods for new loan
    
    print('\n' + '___' + '\n')
    
    
def analyze():
# Function that analyzes a potential refinancing of a loan
    #Get input
    get_input()
    
# Compute equal payment amount (epa0) per period for initial loan
    g = (1+i0)**n0
    epa0 = p0 * i0 * g/(g-1)
    
# Compute balance of initial load at the time of planned refinancing
    h = (1+i0)**n0_com
    bal = h*p0 - epa0*(h-1)/i0
    print("The balance on the initial loan is " + '${:,.2f}'.format(bal) + '\n')
    
# Compute equal payment amount (epa1) per period for refinanced loan
# The initial balance (principal) for the new loan is the balanace from the
# initial loan. 
    g1 = (1+i1)**n1
    epa1 = bal * i1 * g1/(g1-1)

# Refinancing analysis

    # Periodic payments
    print('The periodic payment for the initial loan is ' + '${:,.2f}'.format(epa0))
    print('The periodic payment for the new loan is ' + '${:,.2f}'.format(epa1) + '\n')

    # Comparison of payments (including principal payback) from the time of the refinancing decision point
    # For initial loan if not refinanced
    t_pay0 = epa0 * (n0 - n0_com)
    print('The remaining payments for initial loan, if not refinanced, equal ' + '${:,.2f}'.format(t_pay0))
    print('of which ' + '${:,.2f}'.format(t_pay0 - bal) +' are interest payments.' + '\n')
    
    # For refinanced loan, including cost to terminate initial loan and cost for new loan
    t_pay1 = (epa1 * n1) + cost
    print('The payments in the refinancing scenario, which includes the costs to')
    print('terminate the initial loan and to initiate the new loan, equal ' + '${:,.2f}'.format(t_pay1))
    print('The interest paid in this scenario is ' + '${:,.2f}'.format(t_pay1 - bal) + '\n')
    
    # Amount of time to recover cost of refinancing
    if epa1 < epa0:
        cost_recover = int(cost / (epa0 - epa1)) + 1
        print("It will take " + str(cost_recover) + " periods to recover the cost of refinancing.")
    else:
        print("The new monthly payment would be more than the existing monthly payment, and so, it")
        print("is not recommended to refinance.")
        
#
# Input   
#
tk.Label(root, text="Amount of initial loan:").grid(row=1,column=1,padx=3,sticky='w')
w = tk.DoubleVar()
q1=tk.Entry(root, textvariable=w)
q1.grid(row=1, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Interest rate per period for initial loan:").grid(row=2,column=1,padx=3,sticky='w')
x = tk.DoubleVar()
q2=tk.Entry(root, textvariable=x)
q2.grid(row=2, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of periods for initial loan:").grid(row=3,column=1,padx=3,sticky='w')
y = tk.DoubleVar()
q3=tk.Entry(root, textvariable=y)
q3.grid(row=3, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of periods completed in initial \n loan when refinancing:").grid(row=4,column=1,padx=3,sticky='w')
z = tk.DoubleVar()
q4=tk.Entry(root, textvariable=z)
q4.grid(row=4, column=2,padx=5,pady=3,sticky='w')

# It is assumed that the entire remaining balance on the initial loan is to be refinanced

tk.Label(root, text="Penalities on termination of initial loan \n and financing costs for new loan:").grid(row=7,column=1,padx=3,sticky='w')
w1 = tk.DoubleVar()
q5=tk.Entry(root, textvariable=w1)
q5.grid(row=7, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Interest rate per period for refinanced loan:").grid(row=8,column=1,padx=3,sticky='w')
x1 = tk.DoubleVar()
q6=tk.Entry(root, textvariable=x1)
q6.grid(row=8, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of periods for refinanced loan:").grid(row=9,column=1,padx=3,sticky='w')
y1 = tk.DoubleVar()
q7=tk.Entry(root, textvariable=y1)
q7.grid(row=9, column=2,padx=5,pady=3,sticky='w')

# Control buttons

button1 = tk.Button(root,text="Analyze refinancing",command=analyze).grid(row=13,column=1,padx=3,pady=7,sticky='nesw')

button4 = tk.Button(root,text='Clear', command=clear).grid(row=23,column=1,pady=5)

button5 = tk.Button(root,text='Quit', command=quit).grid(row=23,column=2,padx=3, pady=5,sticky='w')

root.mainloop()