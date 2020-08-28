# Loan Refinance - Breakeven Interest Rate Analyzer
# This program analyzes the  refinancing of a loan (such as a mortgage).
# The program prepares a list of scenarios for various interest rates up until the 
# refinancing rate leads to a situation where the remaining payments are more 
# than that of the original loan. 
#
# It is assumed that the period for the original loan (e.g., a month) is
# the same as the period for the new loan. 

import tkinter as tk 
import csv

root = tk.Tk()
root.title('Loan Refinance - Interest Rate Analyzer')

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
    q8.delete(0,tk.END)
    z1.set(0)
    
def get_input():
    # This function gets the input needed for the other functions
    global p0,i0,n0,n0_com,cost,i1,i_low,n1,n_per_y
    
    # Information for the initial loan that is to be refinanced
    p0 = w.get()       # principal for initial loan
    i0 = x.get()       # interest rate per period for initial loan
    n0 = y.get()       # number of periods for initial loan
    n0_com = z.get()   # number of periods completed when refinancing is to start
    
    # Information for refinancing
    # cost of refinancing, including penality for terminating initial loan
    cost = w1.get()    
    # interest rate at which to start analysis - this should be less than the rate for the existing loan
    i_low =x1.get()  
    # number of periods for new loan
    n1 = y1.get()    
    # number of payments (and compoundings) per year
    # This is used to convert the interest rates from a decimal per month to nominal yearly rates
    n_per_y = z1.get()
    
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

# Breakeven interest table

    It = []     # Periodic interest rate in increments of .0001
    T_pay = []  # Total payments for new loan at given interest rates
    Epa = []    # Equal payment amounts at given interest rates
    It.append(i0)
    t_pay0 = epa0 * (n0 - n0_com)
    T_pay.append(t_pay0)
    Epa.append(epa0)
    
    # Start with an interest rate .5 of i0 and add .0001 to the rate until
    # the total payments for the new loan are greater than the remaining 
    # payments on the existing loan, i.e., epa0 * (n0 - n0_com)
    
    t_payment = 0 
    interest = i_low
    It.append(interest)
    while t_payment < t_pay0:
        # Compute total payment for new loan with updated interest rate
        g1 = (1 + interest)**n1
        epa = bal * interest * g1/(g1-1)
        Epa.append(epa)
        t_payment = (epa * n1) + cost
        T_pay.append(t_payment)
        
        # Increment interest
        interest = interest + .00005
        It.append(interest)
        
    # Output breakdown to a file
    # In the output file, the first line of data concerns the existing laon.
    # The following lines show total payments and payments per period for different interest, 
    # up to the point where the payments for the new loan are greater than the remaining 
    # payments on the existing loan. 
    
    m = len(T_pay)
    with open('breakeven_int.csv', 'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Interest Rate per Period", "Nominal Annual Interest Rate","Total Payments", "Payment per Period"])
        for k in range(m):
            if k==0:
                writer.writerow([ round(It[k],7), '{:,.2f}%'.format(12*100*It[k]), '${:,.2f}'.format(T_pay[k]), '${:,.2f}'.format(Epa[k]), 'Info for existing loan' ])
            else:
                writer.writerow([ round(It[k],7), '{:,.2f}%'.format(12*100*It[k]), '${:,.2f}'.format(T_pay[k]), '${:,.2f}'.format(Epa[k]) ])
        
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

tk.Label(root, text="Interest rate at which to start analysis - \n should be less than rate for existing loan:").grid(row=8,column=1,padx=3,sticky='w')
x1 = tk.DoubleVar()
q6=tk.Entry(root, textvariable=x1)
q6.grid(row=8, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of periods for refinanced loan:").grid(row=9,column=1,padx=3,sticky='w')
y1 = tk.DoubleVar()
q7=tk.Entry(root, textvariable=y1)
q7.grid(row=9, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of payments per year for refinanced loan:").grid(row=10,column=1,padx=3,sticky='w')
z1 = tk.DoubleVar()
q8=tk.Entry(root, textvariable=z1)
q8.grid(row=10, column=2,padx=5,pady=3,sticky='w')

# Control buttons

button1 = tk.Button(root,text="Analyze refinancing interest rates",command=analyze).grid(row=13,column=1,padx=3,pady=7,sticky='nesw')

button4 = tk.Button(root,text='Clear', command=clear).grid(row=23,column=1,pady=5)

button5 = tk.Button(root,text='Quit', command=quit).grid(row=23,column=2,padx=3, pady=5,sticky='w')

root.mainloop()