# Geometric progressions
import tkinter as tk
import tkinter.ttk as ttk
import math
from functools import partial

root = tk.Tk()
root.title('Geometric Progression Calculator')

def quit():
    root.destroy()
    
def clear():
    try:
        t.destroy()
        u.destroy()
    except:
        print('No need to destroy "progression" field')
    
    try:
        s.destroy()
        v.destroy()
    except:
        print('No need to destroy "sum of progression" field')
    
    try:
        r.destroy()
        d.destroy()
    except:
        print('No need to destroy "nth term in progression" field')
    
    q1.delete(0,tk.END)
    x.set(0)
    q2.delete(0,tk.END)
    y.set(0)
    q3.delete(0,tk.END)
    z.set(0)
    a = []

def aprog (x,y,z):
# Function that computes the first n terms of an arithmetic progression and the sum of those terms
    global a,t,s,u,v
    start = x.get()
    ratio = y.get()
    n = z.get()
    
    # Array to hold the progression
    a = []
    
    # Compute progression
    next = start
    for i in range(n):
        a.append(next)
        next = next * ratio

    # Compute sum of the progression
    sum = start*(1-ratio**n)/(1-ratio)

    # Create a text widget
    u = tk.Label(root, text="The progression is :")
    u.grid(row=7, column=1,padx=3,pady=11)
    t = tk.Text(root, height=7, width=25)
    t.grid(row=7,column=2,padx=3,sticky='w')

    # Create a scrollbar and associate it with the text widget t
    scrollb = ttk.Scrollbar(root, command=t.yview)
    scrollb.grid(row=7, column=3, sticky='nesw')
    t['yscrollcommand'] = scrollb.set

    i=0
    for x in a:
        i=i+1
        if i != n:
            t.insert(tk.END, round(x,6))
            t.insert(tk.END,'\n')
        else:
            t.insert(tk.END, round(x,6))

    # Output sum of the progression
    v = tk.Label(root, text="The sum of the progression is :")
    v.grid(row=8, column=1,padx=3,pady=11)
    s = tk.Text(root,height=1,width=25)
    s.insert(tk.END, round(sum,6))
    s.grid(row=8,column=2,padx=3,sticky='w')

def nth_term (x,y,z):
# Function that computes the nth term in an geometric progression
    global r,d
    start = x.get()
    ratio = y.get()
    n = z.get()

    # Compute nth term in progression
    n_term = start*(ratio**(n-1))

    # Print nth term 
    d = tk.Label(root, text="Term number %s in the progression:" %n)
    d.grid(row=6, column=1,padx=3,pady=11)
    r = tk.Text(root,height=1,width=25)
    r.insert(tk.END, round(n_term,6))
    r.grid(row=6,column=2,padx=3,sticky='w')

# Input      
tk.Label(root, text="Initial term in progression:").grid(row=1,column=1)
x = tk.DoubleVar()
q1=tk.Entry(root, textvariable=x)
q1.grid(row=1, column=2,padx=3,sticky='w')

tk.Label(root, text="Common ration:").grid(row=2,column=1)
y = tk.DoubleVar()
q2=tk.Entry(root, textvariable=y)
q2.grid(row=2, column=2,padx=3,sticky='w')

# Enter the number (index) of the final term 
tk.Label(root, text="Number of terms (n):").grid(row=3, column=1)
z = tk.IntVar()
q3=tk.Entry(root, textvariable=z)
q3.grid(row=3,column=2,padx=3,sticky='w')

aprog = partial(aprog,x,y,z)
button1 = tk.Button(root,text="Generate Progression and its Sum",command=aprog).grid(row=4,column=1,padx=3,pady=3)

nth_term = partial(nth_term,x,y,z)
button2 = tk.Button(root,text="Generate nth term in Progression",command=nth_term).grid(row=4,column=2,padx=3,pady=3,sticky='w')

button3 = tk.Button(root,text='Clear', command=clear).grid(row=11, column=1,pady=5)

button4 = tk.Button(root,text='Quit', command=quit).grid(row=11, column=2,padx=3, pady=5,sticky='w')

root.mainloop()
