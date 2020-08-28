# Amortization Calculator
# The program offers three different capabilities, i.e., 
#   - Compute the periodic payments on a mortgage given the loan amount, interest rate, 
#     number of payments per year and the length of the loan in years (doesn't need to be a whole number)
#   - Compute the maximum affordable loan given the interest rate, number of payments per year, length 
#     of the loan in years and the maximum affordable payment per period
#   - Compute the interest versus principal payback breakdown 

import tkinter as tk
import tkinter.ttk as ttk
import csv

root = tk.Tk()
root.title('Amortization Calculator')

def quit():
    root.destroy()
    
def clear():
    # This function clears the various input and output lines in the user interface
    try:
        s.delete('1.0',tk.END)
    except:
        print('No need to clear epa field')
    try:
        t.delete('1.0',tk.END)
    except: 
        print('No need to clear max_loan field')
    q1.delete(0,tk.END)
    w.set(0)
    q2.delete(0,tk.END)
    x.set(0)
    q3.delete(0,tk.END)
    y.set(0)
    q4.delete(0,tk.END)
    z.set(0)
    q5.delete(0,tk.END)
    z2.set(0)
    
def adj_input(w,x,y,z,z2):
    # This function gets the input needed for the other functions
    global p,r,n,max_a
    try:
        p = w.get()
    except:
        p = 0
    
    yr_rate = x.get()
    pay_per_yr = y.get()
    num_yrs = z.get()
    r = (yr_rate/100)/12     # interest rate per repayment period
    n = pay_per_yr * num_yrs    # total number of payments 
    
    try:
        max_a = z2.get()     #  max amount that user can afford per repayment period
    except:
        max_a = 0
    
def payment():
# Function that equal repayment amounts per time period
    global s
    #Get input
    adj_input(w,x,y,z,z2)
    
# Compute equal payment amount (epa) per period
    g = (1+r)**n
    epa=p*r*g/(g-1)
    
# Display payment amount per period
    tk.Label(root, text="The payment amount per period is:").grid(row=9, column=1,padx=3,pady=5,sticky='w')
    s = tk.Text(root,height=1,width=15)
    s.insert(tk.END, '${:,.2f}'.format(epa))
    s.grid(row=9,column=2,padx=3,sticky='w')
    
    return epa

def max_afford_loan():
    global t
    # Get input
    adj_input(w,x,y,z,z2)
    
    # Compute maximum mortgage that use can afford
    g = (1+r)**n
    max_loan = (max_a*(g-1))/(r*g)
    
    # Display maximum affordable loan
    tk.Label(root, text="Maximum affordable mortgage:").grid(row=18, column=1,padx=3,pady=5,sticky='w')
    t = tk.Text(root,height=1,width=15)
    t.insert(tk.END, '${:,.2f}'.format(max_loan))
    t.grid(row=18,column=2,padx=3,sticky='w')
    
def breakdown():
    global t
    a = payment()
    m = int(n)
    
    It = [] # Interest repayment array
    Pr = [] # Principal repayment array
    It.append(r*p)
    Pr.append(a - It[0])
    for i in range(1,m):  
        It.append((r+1)*It[i-1] - r*a)
        Pr.append(a - It[i])
    
    # Output breakdown to a file
    with open('breakdown.csv', 'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Period", "Interest", "Principal"])
        for i in range(m):
            writer.writerow([i+1,round(It[i],2),round(Pr[i],2)])

# Input      
tk.Label(root, text="Amount of loan:").grid(row=1,column=1,padx=3,sticky='w')
w = tk.DoubleVar()
q1=tk.Entry(root, textvariable=w)
q1.grid(row=1, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Annual interest rate:").grid(row=2,column=1,padx=3,sticky='w')
x = tk.DoubleVar()
q2=tk.Entry(root, textvariable=x)
q2.grid(row=2, column=2,padx=5,pady=3,sticky='w')

num_pay=tk.Label(root, text="Number of payments per year:")
num_pay.grid(row=3,column=1,padx=3,sticky='w')
y = tk.DoubleVar()
q3=tk.Entry(root, textvariable=y)
q3.grid(row=3, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Length of loan in years:").grid(row=4,column=1,padx=3,sticky='w')
z = tk.DoubleVar()
q4=tk.Entry(root, textvariable=z)
q4.grid(row=4, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Max affordable payment per periond \n e.g., max one can afford to pay per month:").\
    grid(row=5,column=1,padx=3,sticky='w')
z2 = tk.DoubleVar()
q5=tk.Entry(root, textvariable=z2)
q5.grid(row=5, column=2,padx=5,pady=3,sticky='w')

# Retrieve and adjust input, and make adjusted input global
adj_input(w,x,y,z,z2)

button1 = tk.Button(root,text="Compute periodic payment",command=payment).grid(row=8,column=1,padx=3,pady=7,sticky='nesw')

button2 = tk.Button(root,text='Max affordable loan given interest rate, \n number of payments per year, \
lenght of loan \n and max affordable paymenet per period', \
                    command=max_afford_loan).grid(row=17,column=1,padx=5, pady=5,sticky='nesw')

button3 = tk.Button(root,text='Compute Interest-Principal breakdown \n Result placed in breakdown.csv', \
                    command=breakdown).grid(row=19,column=1,padx=5, pady=5,sticky='nesw')

button4 = tk.Button(root,text='Clear', command=clear).grid(row=23,column=1,pady=5)

button5 = tk.Button(root,text='Quit', command=quit).grid(row=23,column=2,padx=3, pady=5,sticky='w')

root.mainloop()