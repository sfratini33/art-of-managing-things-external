# Deferred Annuities
# This program determines the present value (q) or the regular payout amount (r) for a
# deferred annuity, given
#    i = interest (per period)
#    n = number of payments
#    m = number of deferral periods before payments start
# To be clear, one needs to enter q or r, and the other value is computed
import tkinter as tk
from tkinter import *
import math
from functools import partial

root = tk.Tk()
root.title('Deferred Annunity Calculator')

def quit():
    root.destroy()
    
def clear():
    try:
        s.destroy()
    except:
        print("No need to destroy attribute")
    try:
        t.destroy()
    except:
        print("No need to destroy attribute")
    q1.delete(0,tk.END)
    w.set(0)
    q2.delete(0,tk.END)
    x.set(0)
    q3.delete(0,tk.END)
    y.set(0)
    q4.delete(0,tk.END)
    z.set(0)
    q5.delete(0,tk.END)
    v.set(0)
    
def compute_var(w,x,y,z,v):
# Function that computes the unknown variable 
    global s, t
    q = w.get()         # initial investment amount
    i = x.get()         # interest (per period)
    n = y.get()         # number of payouts
    m = z.get() - 1     # number of deferral periods
    r = v.get()         # amount per payout
    
# Determine which one of q or r has not be entered and compute the other
# variable, and then display the value. 
    if q==0:
        # Compute q
        a = (1 + i)**(-m-1)
        b = (1 + i)**-n
        c = (1 + i)**-1
        q = r * a * (1 - b)/(1 - c)
        
        # Display n
        t = tk.Label(root, text="Present value of annuity:")
        t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
        s = tk.Text(root,height=1,width=11)
        s.insert(tk.END, '${:,.2f}'.format(q))
        s.grid(row=9,column=2,padx=3,sticky='w')

    else:
        # Compute r 
        a = (1 + i)**(-m-1)
        b = (1 + i)**-n
        c = (1 + i)**-1
        r = q * (1 - c)/(a * (1 - b))
        
        # Display r
        t = tk.Label(root, text="Payout per period:")
        t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
        s = tk.Text(root,height=1,width=11)
        s.insert(tk.END, '${:,.2f}'.format(r))
        s.grid(row=9,column=2,padx=3,sticky='w')

# Input      
tk.Label(root, text="Initial investment, i.e., present value of annuity:").grid(row=1,column=1,padx=3,sticky='w')
w = tk.DoubleVar()
q1=tk.Entry(root, textvariable=w)
q1.grid(row=1, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Interest per period:").grid(row=2,column=1,padx=3,sticky='w')
x = tk.DoubleVar()
q2=tk.Entry(root, textvariable=x)
q2.grid(row=2, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of payouts:").grid(row=3,column=1,padx=3,sticky='w')
y = tk.DoubleVar()
q3=tk.Entry(root, textvariable=y)
q3.grid(row=3, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of deferral periods:").grid(row=4,column=1,padx=3,sticky='w')
z = tk.DoubleVar()
q4=tk.Entry(root, textvariable=z)
q4.grid(row=4, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Amount of each payout:").grid(row=5,column=1,padx=3,sticky='w')
v = tk.DoubleVar()
q5=tk.Entry(root, textvariable=v)
q5.grid(row=5, column=2,padx=5,pady=3,sticky='w')

# Call function to comput unknown variable
compute_var = partial(compute_var,w,x,y,z,v)
button1 = tk.Button(root,text="Compute Unknown Variable",command=compute_var).grid(row=6,column=1,padx=3,pady=7)

button2 = tk.Button(root,text='Clear', command=clear).grid(row=23,column=1,pady=5)

button3 = tk.Button(root,text='Quit', command=quit).grid(row=23,column=2,padx=3, pady=5,sticky='w')

root.mainloop()