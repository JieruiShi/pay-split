import pandas as pd
import numpy as np

InputFileName = 'demo.csv'
groupName = 'Demo Trip'

df = pd.read_csv(InputFileName)
members = list(df['Members'].dropna())
headers = members.copy()
headers.append('note')

#generate oweTable
rows = []
for index, row in df.iterrows():
    if pd.isnull(df.at[index, 'Payer']):
        break
    
    rowData = [0]*len(members)+['']
    
    if pd.isnull(df.at[index,'paidFor']):
        paidFor = members
    else:
        paidFor = [name.strip() for name in row['paidFor'].split(',')]
    
    includeSelf = row['includeSelf'] if not pd.isnull(df.at[index, 'includeSelf']) else True    
    payer = row['Payer']
    if (payer not in paidFor) and includeSelf:
        paidFor.append(payer)   
    
    amount = row['Amount']
    
    payerIndex = members.index(payer) #positive value for paying for the group
    rowData[payerIndex] += amount
    
    for paidMember in paidFor:
        paidIndex = members.index(paidMember) #negative value for being paid
        rowData[paidIndex] -= amount/len(paidFor)
    
    rowData[-1] = row['transaction note'] if not pd.isnull(df.at[index, 'transaction note']) else '\(no note\)'
    
    rows.append(pd.DataFrame(data = [rowData], columns = headers))

oweTable = pd.concat(rows, ignore_index = True)

#Calculate transactions to be made
transactions = []
oweArray = [oweTable[member].sum() for member in members]
oweArray2 = oweArray.copy()
noOfTrans = 0
while noOfTrans < len(oweArray2):
    noOfTrans += 1
    minValue = min(oweArray2)
    if abs(minValue) < 0.005:
        break
           
    minIndex = oweArray2.index(minValue)
    maxValue = max(oweArray2)
    maxIndex = oweArray2.index(maxValue)
    transactions.append((minIndex, maxIndex, round(abs(minValue),2)))
    
    oweArray2[maxIndex] += minValue
    oweArray2[minIndex] = 0

#Write to output file
fileName = '{}.txt'.format(groupName)
with open(fileName, 'w+') as f:
    f.write('Transaction Summary:')
    f.write('\n\n')
    
    for index, member in enumerate(members):
        try:
            transaction = next((transaction for transaction in transactions if transaction[0] == index), None)
            paidIndex, payerIndex, amount = transaction
            line = '    {paid} should pay {payer} {amount}'.format(
                paid = members[paidIndex],payer = members[payerIndex],amount = amount)
            
            f.write(line)
            f.write('\n')
        except:
            pass
        
        
    f.write('\nPayment Breakdown:')
    f.write('\n\n')
    
    for index, member in enumerate(members):
        f.write('{}:\n'.format(member))
        amount = oweArray[index]
        if amount < 0:
            f.write('    owes {} \n\n'.format(round(abs(amount),2)))
        else:
            f.write('    owed {} \n\n'.format(round(abs(amount),2)))
        
        
        payList = list(transaction for transaction in transactions if transaction[0] == index)
        
        if len(payList) > 0:
            f.write('  Should pay:\n')
            paidIndex, payerIndex, amount = payList[0]
            f.write('    {payer}: {amount} \n'.format(payer = members[payerIndex], amount = amount))
            f.write('\n')
        
        paidList = list(transaction for transaction in transactions if transaction[1] == index)
        if len(paidList) > 0:
            f.write('  Should be paid by:\n')
            for transaction in paidList:
                paidIndex, payerIndex, amount = transaction
                f.write('    {paid}: {amount} \n'.format(paid = members[paidIndex], amount = amount))
        
            f.write('\n') 
            
        f.write('  Breakdown: \n')
        for index2, value in oweTable[member].items():
            if value:
                f.write('    {value}: {note} \n'.format(value = round(value,2), note = oweTable.at[index2, 'note']))
        f.write('\n')
    
    