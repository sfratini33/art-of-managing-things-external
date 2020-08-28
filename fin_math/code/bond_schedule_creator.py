# Bond Schedule Creator
# This program creates a schedule of payments for a bond.
# The output (in a csv file) shows the time period, coupon interest,
# interest on book value and book value adjustment for each period.
# The program works for bonds purchased at a premium, at a discount
# and at face value. 

import tkinter as tk
import csv
import numpy as np

root = tk.Tk()
root.title('Bond Schedule Creator')

def quit():
    root.destroy()
    
def clear():
    q2.delete(0,tk.END)
    x.set(0)
    q3.delete(0,tk.END)
    y.set(0)
    q5.delete(0,tk.END)
    z1.set(0)
    q6.delete(0,tk.END)
    z2.set(0)
    
    
def adj_input():    
    face = x.get()     # face value of bond (assumed to be the same as the redemption value)
    n = y.get()        # number of payment periods
    i = z1.get()       # coupon rate (this is applied to the face value to determine periodic payouts)
    yr = z2.get()       # yield rate
    return (face,n,i,yr) 
    
def compute_schedule():
# Function that computes the bond schedule 
    # Retrieve input
    face,n,i,yr = adj_input()

    # Determine the coupon (periodic payment)
    a = face * i
    
    # Determine purchase price that results in given yield
    g = (1 + yr)**(-n)
    h = (1 - g)/yr
    p = a * h + face * g

    # Define arrays to be populated with information for bond schedule table
    bv = []    # array for book value
    adj = []   # array for book value adjustment
    ibv = []   # array for interest on book value
    
    # Initialize arrays
    bv.append(p)
    adj.append(0)
    ibv.append(0)
    
    # Compute book value, book value adjustment and interest on book value for each period
    for k in range(1,int(n)+1):
        ibv.append(yr*bv[k-1])
        adj.append(a - ibv[k])
        bv.append(bv[k-1] - adj[k])
        
    # Generate bond schedule and write to file
    with open('bond_schedule.csv', 'w',newline='') as f:
        writer = csv.writer(f)
        
        # Header row of table 
        writer.writerow(["Period", "Coupon","Interest on Book Value", "Book Value Adjustment","Book Value"])
        
        # Row of table body 
        writer.writerow([ '0','-','-','-','${:,.2f}'.format(bv[0]) ])
        
        # Rest of table body
        for k in range(1,int(n)+1):
             writer.writerow([ k,'${:,.2f}'.format(a),'${:,.2f}'.format(ibv[k]),\
                              '${:,.2f}'.format(adj[k]),'${:,.2f}'.format(bv[k]) ])
        
        # Totals
        coupon_total = n * a
        ibv_total = np.sum(ibv)
        adj_total = np.sum(adj)
        writer.writerow([ 'Totals','${:,.2f}'.format(coupon_total),\
                         '${:,.2f}'.format(ibv_total),'${:,.2f}'.format(adj_total),'-' ])
    
    return

# Input      
tk.Label(root, text="Redemption value of bond:").grid(row=2,column=1,padx=3,sticky='w')
x = tk.DoubleVar()
q2=tk.Entry(root, textvariable=x)
q2.grid(row=2, column=2,padx=5,pady=3,sticky='w')

num_per=tk.Label(root, text="Number of payment periods:")
num_per.grid(row=3,column=1,padx=3,sticky='w')
y = tk.DoubleVar()
q3=tk.Entry(root, textvariable=y)
q3.grid(row=3, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Coupon rate per period:").grid(row=5,column=1,padx=3,sticky='w')
z1 = tk.DoubleVar()
q5=tk.Entry(root, textvariable=z1)
q5.grid(row=5, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Yield rate per period:").grid(row=6,column=1,padx=3,sticky='w')
z2 = tk.DoubleVar()
q6=tk.Entry(root, textvariable=z2)
q6.grid(row=6, column=2,padx=5,pady=3,sticky='w')

# Compute the bond schedule
button1 = tk.Button(root,text="Compute bond schedule",command=compute_schedule).grid(row=8,column=1,padx=3,pady=7)

# Clear and quit command buttons
button2 = tk.Button(root,text='Clear', command=clear).grid(row=23,column=1,pady=5)

button3 = tk.Button(root,text='Quit', command=quit).grid(row=23,column=2,padx=3, pady=5,sticky='w')

root.mainloop()