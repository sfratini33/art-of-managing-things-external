# Balloon Loan Calculator
# This calculator can be used to compute either the regular payment for 
# a balloon loan, or the present value of a balloon loan given the amount
# of the regular payments.
import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
root.title('Balloon Loan Calculator')

def quit():
    root.destroy()
    
def clear():
    s.destroy()
    t.destroy()
    q1.delete(0,tk.END)
    w.set(0)
    q2.delete(0,tk.END)
    x.set(0)
    q3.delete(0,tk.END)
    y.set(0)
    q5.delete(0,tk.END)
    z1.set(0)
    q6.delete(0,tk.END)
    z2.set(0)
    
    
def adj_input(w,x,y,z1,z2):    
    try: 
        p = w.get()           # current value of loan
    except:
        p = 0                 # All the varioables are initial set to zero in the GUI, but the user may blank out the value
    r = x.get()               # interest rate per payment period
    n = y.get()               # total number of payments 
    b = z1.get()              # amount of the balloon payment
    try:
        epa = z2.get()        # amount of each recurring payment
    except:
        epa = 0               # All the varioables are initial set to zero in the GUI, but the user may blank out the value
    
    return (p,r,n,b,epa) 
    
def compute_var():
# Function computes the unknow variable either P (current value) or 
# the payment amount
    global s,t
    p,r,n,b,epa = adj_input(w,x,y,z1,z2)

    if epa==0:
        # Compute equal payment amount (epa) per period
        g = (1+r)**n
        epa=(r*p*g - r*b)/(g-1)
        
        # Display final amount of regular payment
        t = tk.Label(root, text="The payment amount per period is:")
        t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
        s = tk.Text(root,height=1,width=15)
        s.insert(tk.END, '${:,.2f}'.format(epa))
        s.grid(row=9,column=2,padx=3,sticky='w')
    else:
        # Compute present value of loan
        g = (1+r)**n
        h = (epa * (g-1)) + r*b
        k = r*g
        p = h/k
        
        # Display final amount of regular payment
        t = tk.Label(root, text="The current value of the loan is:")
        t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
        s = tk.Text(root,height=1,width=15)
        s.insert(tk.END, '${:,.2f}'.format(p))
        s.grid(row=9,column=2,padx=3,sticky='w')
    
    return

# Input      
tk.Label(root, text="Amount of loan:").grid(row=1,column=1,padx=3,sticky='w')
w = tk.DoubleVar()
q1=tk.Entry(root, textvariable=w)
q1.grid(row=1, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Interest rate per period:").grid(row=2,column=1,padx=3,sticky='w')
x = tk.DoubleVar()
q2=tk.Entry(root, textvariable=x)
q2.grid(row=2, column=2,padx=5,pady=3,sticky='w')

num_pay=tk.Label(root, text="Total number of payments:")
num_pay.grid(row=3,column=1,padx=3,sticky='w')
y = tk.DoubleVar()
q3=tk.Entry(root, textvariable=y)
q3.grid(row=3, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Amount of the balloon payment:").grid(row=5,column=1,padx=3,sticky='w')
z1 = tk.DoubleVar()
q5=tk.Entry(root, textvariable=z1)
q5.grid(row=5, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Amount of each periodic payment:").grid(row=6,column=1,padx=3,sticky='w')
z2 = tk.DoubleVar()
q6=tk.Entry(root, textvariable=z2)
q6.grid(row=6, column=2,padx=5,pady=3,sticky='w')

# Compute the unknown variable
button1 = tk.Button(root,text="Compute unkown variable",command=compute_var).grid(row=8,column=1,padx=3,pady=7)

# Clear and quit command buttons
button2 = tk.Button(root,text='Clear', command=clear).grid(row=23,column=1,pady=5)

button3 = tk.Button(root,text='Quit', command=quit).grid(row=23,column=2,padx=3, pady=5,sticky='w')

root.mainloop()