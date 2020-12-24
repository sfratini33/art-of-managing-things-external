# Discounted Value of Ordinary, Simple, Certain Annuities
# This program covers the payouts from an ordinary, simple, certain annuity
# It is assumed that the compounding and the periodic payouts happen at the same time
# One can enter any two of n, q or r and the program will compute the third:
#    i = interest (per period)
#    n = number of periods
#    q = initial investment amount
#    r = payment to investor per period
import tkinter as tk
from tkinter import *
import math
from functools import partial

root = tk.Tk()
root.title('Simple Annunity Payout Calculator')

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
    
def compute_var(w,x,y,z):
# Function that computes the unknown variable 
    global s, t
    q = w.get()         # initial investment amount
    i = x.get()         # interest (per period)
    try:
        n = y.get()     # number of payouts
    except:
        n = 0           # this is need is the use delete the default setting 
    try:
        r = z.get()     # amount per payout
    except:
        r = 0           # this is need is the use delete the default setting
    
# Determine which one of n, q or r has not be entered and compute the third
# variable and then display the value. 
    if n==0:
        # Compute n
        if r - i*q <= 0: # payout is less than accrued interest per period
            # Display n
            t = tk.Label(root, text="Number of payouts:")
            t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
            s = tk.Text(root,height=1,width=11)
            s.insert(tk.END, 'infinite')
            s.grid(row=9,column=2,padx=3,sticky='w')
            
        elif r > q*(i+1):
            # desired periodic payout is greater than initial investment amount accrued interest in first period
            print('Error: Not possible since requested periodic payout is greater')
            print('than value of initial investment at the end of the first period')
            
        else:
            n = (math.log10(r) - math.log10(r - i*q))/math.log10(1 + i)
            # Display n
            t = tk.Label(root, text="Number of payouts:")
            t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
            s = tk.Text(root,height=1,width=11)
            s.insert(tk.END, round(n,2))
            s.grid(row=9,column=2,padx=3,sticky='w')
        
    elif q==0:
        # Compute q
        q = (r/i)*(1-(1+i)**(-n))
        
        # Display q
        t = tk.Label(root, text="Initial investment:")
        t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
        s = tk.Text(root,height=1,width=11)
        s.insert(tk.END, '${:,.2f}'.format(q))
        s.grid(row=9,column=2,padx=3,sticky='w')
    else:
        # Compute r 
        r = (i*q)/(1-(1+i)**(-n))
        
        # Display r
        t = tk.Label(root, text="Payout per period:")
        t.grid(row=9, column=1,padx=3,pady=5,sticky='w')
        s = tk.Text(root,height=1,width=11)
        s.insert(tk.END, '${:,.2f}'.format(r))
        s.grid(row=9,column=2,padx=3,sticky='w')

# Input      
tk.Label(root, text="Initial investment in annuity:").grid(row=1,column=1,padx=3,sticky='w')
w = tk.DoubleVar()
q1=tk.Entry(root, textvariable=w)
q1.grid(row=1, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Interest per period (must provide a value):").grid(row=2,column=1,padx=3,sticky='w')
x = tk.DoubleVar()
q2=tk.Entry(root, textvariable=x)
q2.grid(row=2, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Number of payouts:").grid(row=3,column=1,padx=3,sticky='w')
y = tk.DoubleVar()
q3=tk.Entry(root, textvariable=y)
q3.grid(row=3, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Amount of each payout:").grid(row=4,column=1,padx=3,sticky='w')
z = tk.DoubleVar()
q4=tk.Entry(root, textvariable=z)
q4.grid(row=4, column=2,padx=5,pady=3,sticky='w')

# Call function to comput unknown variable
compute_var = partial(compute_var,w,x,y,z)
button1 = tk.Button(root,text="Compute Remaining Variable",command=compute_var).grid(row=6,column=1,padx=3,pady=7)

button2 = tk.Button(root,text='Clear', command=clear).grid(row=23,column=1,pady=5)

button3 = tk.Button(root,text='Quit', command=quit).grid(row=23,column=2,padx=3, pady=5,sticky='w')

root.mainloop()