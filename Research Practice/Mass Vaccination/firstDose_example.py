#Frist implementation for the Mass Vaccination optimization problem - 1st dose simple

from gurobipy import *
import numpy as np
import pandas as pd


# List of indices
dep = 3  #i
stage = 3  #j
vacc = 2  #k
per= 4 #t

#dep= ['Medelllin','Bogota','Cali']
#vac= ['Pfizer','Zeneca','Janssen','Sinovac','Montena']

ind_kitj= tuplelist([(k, i, t, j) for j in range(1,stage+1)
 for t in range(1,per+1) for i in range(1,dep+1) for k in range(1,vacc+1)])

ind_it= tuplelist([(i, t) for t in range(1,per+1)
 for i in range(1,dep+1)])

ind_kt= tuplelist([(k, t) for t in range(0,
per+1) for k in range(1,vacc+1)])

ind_tj= tuplelist([(t, j) for j in range(1,stage+1)
for t in range(1,per+1)])

# Parameters and data

# Fixed costs

C_f= np.array([[100, 120, 150],
                [100,120, 180]])

# Variable costs
C_v=0

# Incidence of the virus

w= np.array([[4,3,2,1],
            [7,6,4,2],
            [3,3,2,2]])

# Total population to be vaccinated

Q= np.array([[10,40,50],
            [20,45,35],
            [5,35,60]])

# Quantity of vaccines which arrive

N= np.array([[15, 45,50, 50],
            [15, 50,50, 25]])

#Permission  for distribution

F= np.array([[1,1,1],
                [1,1,1]])

# Big value
M=10000
#M= 10000000

#Model definition
model = Model(name="Vaccination_model")

# Variables

A= model.addVars(ind_kitj,lb=0.0,ub=float('inf'), vtype= GRB.INTEGER, name = 'A')
S= model.addVars(ind_kitj,lb=0.0,ub=1.0,vtype= GRB.BINARY, name = 'S')
X= model.addVars(ind_it,lb=0.0,ub=float('inf'), vtype= GRB.INTEGER, name = 'X')
I= model.addVars(ind_kt,lb=0.0,ub=float('inf'), vtype= GRB.INTEGER, name = 'I')
R= model.addVars(ind_tj,lb=0.0,ub=1.0,vtype= GRB.BINARY, name = 'R')
Z= model.addVars(4,lb=0.0,ub=float('inf'), vtype= GRB.CONTINUOUS, name= 'Z')
Z_aux= model.addVars(4,lb=0.0,ub=float('inf'), vtype= GRB.CONTINUOUS, name= 'Z_aux')
L= model.addVars(ind_tj,lb=0.0,ub=float('inf'),vtype= GRB.CONTINUOUS, name= 'L')
T= model.addVars(ind_tj,lb=0.0,ub=float('inf'),vtype= GRB.CONTINUOUS, name= 'T')
#Objective Function

# OF 1 - Costs
Z[0]= quicksum(X) + C_v
# OF 2 - Equity

Z[1]= quicksum(L[t,j] - T[t,j] for t in range(1, per+1) for j in range(1,stage+1))

# OF 3 - Life quality
#print(A)
Z[2]= quicksum(w[i-1][t-1]*A[k,i,t,j] for k in range(1,vacc+1) for i in range(1,dep+1) for t in range(1,per+1) for j in range(1,stage+1))

# OF 4 - Time
Z_3=0
for t in range(1,per+1):
    Z_3= Z_3 + quicksum(t*A[k,i,t,j] for k in range(1,vacc+1) for i in range(1,dep+1)  for j in range(1,stage+1))
Z[3]= Z_3
# Objective function assignation
model.setObjective(Z[3]+ Z[0]/1000000,GRB.MINIMIZE)

# Constrains

cont=1


model.addConstr(Z_aux[0]== quicksum(X) + C_v, "Constraints " + str(cont))
cont += 1

model.addConstr(Z_aux[1]== quicksum(L[t,j] - T[t,j] for t in range(1, per+1) for j in range(1,stage+1)), "Constraints " + str(cont))
cont += 1

model.addConstr(Z_aux[2]== quicksum(((w[i-1][t-1]*A[k,i,t,j])) for k in range(1,vacc+1) for i in range(1,dep+1) for t in range(1,per+1) for j in range(1,stage+1)), "Constraints " + str(cont))
cont += 1

model.addConstr(Z_aux[3]== quicksum(t*A[k,i,t,j] for k in range(1,vacc+1) for i in range(1,dep+1) for t in range(1,per+1) for j in range(1,stage+1)), "Constraints " + str(cont))
cont += 1

#Constraint 1
for i in range(1,dep+1):
    for t in range(1,per+1):
        for j in range(1,stage+1):
            model.addConstr((L[t,j] >= quicksum(A[k,i,t,j] for k in range(1,vacc+1))/Q[i-1][j-1]), "Constraints " + str(cont))
            cont += 1

#Constraint 2
for i in range(1,dep+1):
    for t in range(1,per+1):
        for j in range(1,stage+1):
            model.addConstr((T[t,j] <= quicksum(A[k,i,t,j] for k in range(1,vacc+1))/Q[i-1][j-1]), "Constraints " + str(cont))
            cont += 1

#Constraint 3
for i in range(1,dep+1):
    for t in range(1,per+1):
        for j in range(1,stage+1):
            model.addConstr((quicksum(A[k,i,t,j] for k in range(1,vacc+1)) <= Q[i-1][j-1]*quicksum(R[tau,j] for tau in range(t,per+1))), "Constraints " + str(cont))
            cont += 1

#Constraint 4
for i in range(1,dep+1):
    for j in range(1,stage+1):
        model.addConstr((quicksum(A[k,i,t,j] for k in range(1,vacc+1) for t in range(1,per+1)) >= Q[i-1][j-1]), "Constraints " + str(cont))
        cont += 1

#constraint 5
for k in range(1,vacc+1):
    for i in range(1,dep+1):
        for t in range(2,per+1):
            for j in range(1,stage):
                model.addConstr((quicksum(A[k,i,tau,j2] for j2 in range(j+1,stage+1) for tau in range(1,(t-1)+1)) <= M*(1- S[k,i,t,j])), "Constraints " + str(cont))
                cont += 1

#Constraint 6
for j in range(1,stage+1):
    for t in range(1,per+1):
        model.addConstr((R[t,j] <= quicksum(A[k,i,tau,j] for k in range (1, vacc+1) for i in range(1,dep+1) for tau in range(t,per+1))), "Constraints " + str(cont))
        cont += 1

#constraint 7
for k in range(1,vacc+1):
    for t in range(1,per+1):
        model.addConstr((quicksum(A[k,i,t,j] for i in range(1,dep+1) for j in range(1,stage+1)) + I[k,t] == I[k,t-1] + N[k-1][t-1]), "Constraints " + str(cont))
        cont += 1

#constraint 8
for k in range(1,vacc+1):
        model.addConstr((I[k,0]  == 0), "Constraints " + str(cont))
        cont += 1

#constraint 9
for j in range(1,stage+1):
        model.addConstr((quicksum(R[t,j] for t in range(1,per+1)) == 1), "Constraints " + str(cont))
        cont += 1

#Constraint 10
for k in range(1,vacc+1):
    for i in range(1,dep+1):
        for t in range(1,per+1):
            for j in range(1,stage+1):
                model.addConstr((S[k,i,t,j] <= F[k-1][i-1]), "Constraints " + str(cont))
                cont += 1

#constraint 11
for j in range(1,stage): #just until j-1
        model.addConstr((quicksum(t*R[t,j] for t in range(1,per+1)) <= quicksum(t*R[t,j+1] for t in range(1,per+1))), "Constraints " + str(cont))
        cont += 1

#Constraint 12
for k in range(1,vacc+1):
    for i in range(1,dep+1):
        for t in range(1,per+1):
            for j in range(2,stage+1):
                model.addConstr((S[k,i,t,j] <= quicksum(R[tau,j-1] for tau in range(1,t+1))), "Constraints " + str(cont))
                cont += 1

#Constraint 13
for k in range(1,vacc+1):
    for i in range(1,dep+1):
        for t in range(1,per+1):
            for j in range(1,stage+1):
                model.addConstr((A[k,i,t,j] <= Q[i-1][j-1]*S[k,i,t,j]), "Constraints " + str(cont))
                cont += 1

#Constraint 14
for k in range(1,vacc+1):
    for i in range(1,dep+1):
        for t in range(1,per+1):
            for j in range(1,stage+1):
                model.addConstr((X[i,t] >= C_f[k-1][i-1]*S[k,i,t,j]), "Constraints " + str(cont))
                cont += 1

model.optimize()
model.printAttr('X')