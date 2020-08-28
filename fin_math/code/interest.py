# Interest Compounding Calculator
import tkinter as tk
import tkinter.ttk as ttk
import math
from functools import partial

root = tk.Tk()
root.title('Interest Compounding Calculator')

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
    y1.set(0)
    q4.delete(0,tk.END)
    y2.set(0)
    q5.delete(0,tk.END)
    z.set(0)
    
def principal (w,x,y1,y2,z):
# Function that computes final principal
    global s,t
    orig_prin = w.get()
    rate = x.get()/100
    try:
        freq = y1.get()
    except:
        freq = 0
    continuous = y2.get()
    time = z.get()
    
# Compute final principal
    if continuous == False:
        fin_prin = orig_prin*(1+(rate/freq))**(freq*time)
    else:
        fin_prin = orig_prin*math.exp(rate*time)
    
# Display final principal
    t = tk.Label(root, text="The final principal is:")
    t.grid(row=7, column=1,padx=3,pady=5,sticky='w')
    s = tk.Text(root,height=1,width=15)
    s.insert(tk.END, round(fin_prin,2))
    s.grid(row=7,column=2,padx=3,sticky='w')

# Input      
tk.Label(root, text="Original principal:").grid(row=1,column=1,padx=3,sticky='w')
w = tk.DoubleVar()
q1=tk.Entry(root, textvariable=w)
q1.grid(row=1, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Annual interest percentage:").grid(row=2,column=1,padx=3,sticky='w')
x = tk.DoubleVar()
q2=tk.Entry(root, textvariable=x)
q2.grid(row=2, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Compounding frequency per year: \n (leave this blank if continuous \n compounding is set to True)").grid(row=3,column=1,padx=3,sticky='w')
y1 = tk.DoubleVar()
q3=tk.Entry(root, textvariable=y1)
q3.grid(row=3, column=2,padx=5,pady=3,sticky='w')

tk.Label(root, text="Continuous compounding (True/False):").grid(row=4,column=1,padx=3,sticky='w')
y2 = tk.BooleanVar()
q4=tk.Entry(root, textvariable=y2)
q4.grid(row=4, column=2,padx=5,pady=3,sticky='w')

# The user can also enter fractions, e.g., 1.25
tk.Label(root, text="Time that interest accrues in years: \n (Need not be a whole number of years)", justify='left').grid(row=5,column=1,padx=3,sticky='w')
z = tk.DoubleVar()
q5=tk.Entry(root, textvariable=z)
q5.grid(row=5, column=2,padx=5,pady=3,sticky='w')

# Call function to compute the final principal
principal = partial(principal,w,x,y1,y2,z)
button1 = tk.Button(root,text="Compute final principal",command=principal).grid(row=6,column=1,padx=3,pady=7)

button2 = tk.Button(root,text='Clear', command=clear).grid(row=11,column=1,pady=5)

button3 = tk.Button(root,text='Quit', command=quit).grid(row=11,column=2,padx=3, pady=5,sticky='w')

root.mainloop()