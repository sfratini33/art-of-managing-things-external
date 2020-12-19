# Arithmetic progressions
import tkinter as tk
import tkinter.ttk as ttk
import math
from functools import partial

root = tk.Tk()
root.title('Arithmetic Progression Calculator')

def quit():
    root.destroy()
    
def clear():
    t.destroy()
    t1.destroy()
    
    s.destroy()
    s1.destroy()
    
    r.destroy()
    r1.destroy()
    
    q1.delete(0,tk.END)
    x.set(0)
    
    q2.delete(0,tk.END)
    y.set(0)
    
    q3.delete(0,tk.END)
    z.set(0)
    
    a = []

def aprog (x,y,z):
# Function that computes the first n terms of an arithmetic progression and the sum of those terms
    global a,t,t1,s,s1
    start = x.get()
    step = y.get()
    n = z.get()
    
    # Array to hold the progression
    a = []
    
    # Compute progression
    next = start
    for i in range(n):
        a.append(next)
        next = next + step

    # Compute sum of the progression
    sum = round((n/2)*(a[0]+a[n-1]),3)

    # Output the progression
    # Compute width of text widgets given that 10 numbers will be print per row
    # This is under the assumption that the terms have three decimal places
    w = math.trunc(abs(start) + n * abs(step))
    # Number of digits in the longest number in the progression, plus the three digits after the decimal point
    # Add two for the comma and space after each number, and one for the decimal point
    w = len(str(w))+6
    if start+n*step > 0: # multiple by 10 to get the amount of space needed for each row of the output
        w = 10*w
    else: # need to add an extra space for the minus sign
        w = 10*(w+1)

    # Create a text widget
    t1= tk.Label(root, text="The progression is :")
    t1.grid(row=7, column=1,padx=3,pady=11)
    t = tk.Text(root, height=7, width=w)
    t.grid(row=7,column=2,padx=3,sticky='w')

    # Create a scrollbar and associate it with the text widget t
    scrollb = ttk.Scrollbar(root, command=t.yview)
    scrollb.grid(row=7, column=3, sticky='nesw')
    t['yscrollcommand'] = scrollb.set

    i=0
    for x in a:
        i=i+1
        if i%10 != 0 and i != n:
            t.insert(tk.END, str(round(x,3)) + ', ')
        elif i != n:
            t.insert(tk.END, str(round(x,3)) + '\n')
        else:
            t.insert(tk.END, str(round(x,3)))

    # Output sum of the progression
    s1 = tk.Label(root, text="The sum of the progression is :")
    s1.grid(row=8, column=1,padx=3,pady=11)
    s = tk.Text(root,height=1,width=w)
    s.insert(tk.END, str(sum))
    s.grid(row=8,column=2,padx=3,sticky='w')

def nth_term (x,y,z):
# Function that computes the nth term in an arithmetic progression
    global r,r1
    start = x.get()
    step = y.get()
    n = z.get()

    # Compute nth term in progression
    n_term = start + (n-1)*step

    # Print nth term 
    r1 = tk.Label(root, text="Term number %s in the progression:" %n)
    r1.grid(row=6, column=1,padx=3,pady=11)
    r = tk.Text(root,height=1,width=11)
    r.insert(tk.END, str(n_term))
    r.grid(row=6,column=2,padx=3,sticky='w')

# Input      
tk.Label(root, text="Initial term in progression:").grid(row=1,column=1)
x = tk.DoubleVar()
q1=tk.Entry(root, textvariable=x)
q1.grid(row=1, column=2,padx=3,sticky='w')

tk.Label(root, text="Length of a step:").grid(row=2,column=1)
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