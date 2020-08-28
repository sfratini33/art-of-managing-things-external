# Block Annuity Calculator
# This program computes the total value of a savings annuity over several blocks.
# Each block has a fixed interest rate per period and fixed payment (i.e., investment)
# per period. The interest rate and payment may vary among the blocks. 

import csv, math

class Block:
    # Instances of this class represent one block of a savings annuity
    # Each block has a fixed interest rate per period and a given number of periods.
    # At the end of each period, a fixed investment is made and the existing investment
    # is compounded. The following attributes are required for each block:
    #    i - interest rate per period
    #    r - the amount of money invested by the annuity owner at the end of each period
    #    n - the number of periods in the block
    #    v - value of the block when it ends, i.e., when the interest rate changes and a 
    #        new block is created

    def __init__(blk, i, r, n):
        blk.i = i
        blk.r = r
        blk.n = n
        blk.v = 0
   
    def acc_value(blk):
        # This function comutes the accumulate value of the annuity for the block
        g = (1 + blk.i)**blk.n
        blk.v = blk.r*(g-1)/blk.i
        return blk.v
    
    def fin_value(blk, i_new, n_new):
        # After a block X is complete, i.e., when the interest rate changes and a new block is started,
        # Block X will continue to earn interest based on one or more interest rates for the subsequent
        # blocks, if any. This function needs to be called once for each block subsequent to a given block. 
        blk.i_new = i_new
        blk.n_new = n_new
        blk.v = blk.v  * (1 + blk.i_new)**blk.n_new
        return blk.v

# B is an array that holds the classes that represent the blocks
B = []

# Read in the csv file that has information concerning each block.
# Each line of the csv file represents on block.
# Each line has the payment per period, interest per period and 
# the number of periods for a given block. The items are delimited commas. 
name = input('Enter name of csv file (do not add .csv to the name): ')
with open('%s.csv' % name) as f:
    blocks = csv.reader(f, delimiter=',')
    for row in blocks:
        # Create a class for each block and put the classes in an arry B
        B.append(Block(float(row[0]), float(row[1]), float(row[2])))

num_blocks = len(B)

# V is an array that holds the value for each block
V = []

# Compute the accrued value for each block but only during the period 
# when the block is active. In an second step, the value of the block
# at the end of the term is computed (this includes accrued interest 
# while subsquent blocks are active).
for k in range(num_blocks):
    V.append(B[k].acc_value())

print('')
print('The value of each block without interest accrued during subsequent blocks:')
for k in range(num_blocks):
    print("Block " + str(k) + ': '+ '${:,.2f}'.format(V[k]))

# The second step is to compute the interest accrued to each block during subsequent blocks. 
# This entails multiple calls to the fin-value function.
for k in range(num_blocks-1):
    for j in range(k+1,num_blocks):
        V[k] = B[k].fin_value(B[j].i,B[j].n)

# Print out the value of each block at the end of the annuity's term
print('')
print('The value of each block at the end of the annuity\'s term, \
i.e., with the interest accrued during subsequent blocks:')
for k in range(num_blocks):
    print("Block " + str(k) + ': '+ '${:,.2f}'.format(V[k]))

# Total value of annuity at term
total_value = 0
for k in range(num_blocks):
    total_value = total_value + V[k]
print('')
print('Total value of the annuity at the end of its term:')
print('${:,.2f}'.format(total_value))