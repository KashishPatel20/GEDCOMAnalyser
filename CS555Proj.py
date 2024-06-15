from pathlib import Path
from prettytable import PrettyTable
from datetime import date

def dateCalc(date):
    med = ""
    if(not ((date[1]).isnumeric())):
        date = "0" + date
    if(date[2:5] == "JAN"):
        med = "01"
    elif(date[2:5] == "FEB"):
        med = "02"
    elif(date[2:5] == "MAR"):
        med = "03"
    elif(date[2:5] == "APR"):
        med = "04"
    elif(date[2:5] == "MAY"):
        med = "05"
    elif(date[2:5] == "JUN"):
        med = "06"
    elif(date[2:5] == "JUL"):
        med = "07"
    elif(date[2:5] == "AUG"):
        med = "08"
    elif(date[2:5] == "SEP"):
        med = "09"
    elif(date[2:5] == "OCT"):
        med = "10"
    elif(date[2:5] == "NOV"):
        med = "11"
    elif(date[2:5] == "DEC"):
        med = "12"
    else:
        #some error
        pass
    date = date[5:] + "-" + med + "-" + date[0:2]
    return date

        
p = Path(__file__).with_name('GEDCOM_DATA.txt')
with p.open('r') as f:
    data = f.read()
    newdata = data.splitlines()
    count = 0
    newcount = 1
    indivTable = PrettyTable()
    indivTable.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]
    IId, IName, IGen, IBirth, IAge, IAlive, IDeath, IChild, ISpouse = "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"
    famTable = PrettyTable()
    famTable.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]
    FId, FMar, FDiv, FHId, FHName, FWId, FWName, FChild = "NA", "NA", "NA", "NA", "NA", "NA", "NA", []
    dateCheck = "NA" #can be BIRT DEAT DIV or MARR
    typeCheck = "" #can be INDI or FAM
    firstPassInd, firstPassFam = 0, 0
    husbName, wifeName = "NA", "NA"
    for e in newdata:
        if(e.strip() == ''):
            count+=1
        else:
            line = newdata[count]
            lineList = line.split(' ')
            count+=1
            level = ''
            tag = ''
            args = ''
            for ele in lineList:
                if(newcount == 1):
                    level = ele
                elif(newcount == 2):
                    tag = ele
                else:
                    args += ele
                newcount+=1
            newcount = 1
            valid = 'Y'
            if(tag == 'INDI' or tag == 'FAM' or tag == 'HEAD' or tag == 'TRLR' or tag == 'NOTE'):
                #0th level cases
                if(args == 'INDI'):
                    IId = args
                elif(args == 'FAM'):
                    #FAM
                    FId = args
                pass
            elif(tag == 'NAME' or tag == 'SEX' or tag == 'BIRT' or tag == 'DEAT' or tag == 'FAMC' or tag == 'FAMS' or tag == 'MARR' or tag == 'HUSB' or tag == 'WIFE' or tag == 'CHIL' or tag == 'DIV'):
                #1st level cases
                if(tag == 'NAME'):
                    IName = args
                elif(tag == 'SEX'):
                    IGend = args
                elif(tag == 'BIRT'):
                    IBirth = args
                    dateCheck = 'BIRT'
                elif(tag == "DEAT"):
                    IDeath = args
                    dateCheck = 'DEAT'
                elif(tag == 'FAMC'):
                    IChild = args
                    ISpouse = "NA"
                elif(tag == 'FAMS'):
                    IChild = "NA"
                    ISpouse = args
                    if(IGend == "M"):
                        husbName = IName
                    elif(IGend == "F"):
                        wifeName = IName
                    else:
                        pass
                elif(tag == 'MARR'):
                    FMar = args
                    FDiv = "NA"
                    dateCheck = 'MARR'
                elif(tag == 'HUSB'):
                    FHId = args
                elif(tag == 'WIFE'):
                    FWId = args
                elif(tag == 'CHIL'):
                    FChild.append(args)
                else:
                    #tag == Div
                    FMar = "NA"
                    FDiv = args
                    dateCheck = 'DIV'
                pass 
            elif(tag == 'DATE'):
                #2nd level case
                if(dateCheck == 'BIRT'):
                    IBirth = args
                elif(dateCheck == 'DEAT'):
                    IDeath = args
                elif(dateCheck == 'MARR'):
                    FMar = args
                else:
                    #dateCheck == 'DIV'
                    FDiv = args
                pass 
            else:
                if(args == 'INDI' or args == 'FAM'):
                    #if tag is INDI or FAM, the 'tag' input wouldve been the identifier, meaning 'args' would hold INDI or FAM
                    if(typeCheck == 'INDI' and firstPassInd >= 1):
                        IBirth = dateCalc(IBirth)
                        if(not (IDeath == "NA")):
                            IDeath = dateCalc(IDeath)
                            IAge = int(IDeath[0:4]) - int(IBirth[0:4])
                            IAlive = False
                        else:
                            today = date.today()
                            IAge = today.year - int(IBirth[0:4])
                            IAlive = True
                        indivTable.add_row([IId, IName, IGend, IBirth, IAge, IAlive, IDeath, IChild, ISpouse])
                        IId, IName, IGen, IBirth, IAge, IAlive, IDeath, IChild, ISpouse = "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"
                        dateCheck = "NA"
                        typeCheck = ""
                    if(typeCheck == 'FAM' and firstPassFam >= 1):
                        if(not (FMar == "NA")):
                            FMar = dateCalc(FMar)
                        if(not (FDiv == "NA")):
                            FDiv = dateCalc(FDiv)
                        if(len(FChild) < 1):
                            FChild = "NA"
                        FHName = husbName
                        FWName = wifeName
                        famTable.add_row([FId, FMar, FDiv, FHId, FHName, FWId, FWName, FChild])
                        FId, FMar, FDiv, FHId, FHName, FWId, FWName, FChild = "NA", "NA", "NA", "NA", "NA", "NA", "NA", []
                        dateCheck = "NA"  
                        typeCheck = ""
                        husbName, wifeName = "NA", "NA"
                    if(args == 'INDI'):
                        IId = tag
                        typeCheck = args
                        firstPassInd +=1
                    else:
                        #FAM
                        FId = tag
                        typeCheck = args
                        firstPassFam +=1
                    pass
                else:
                    valid = 'N'
    if(typeCheck == 'INDI' and firstPassInd == 1):
        IBirth = dateCalc(IBirth)
        if(not (IDeath == "NA")):
            IDeath = dateCalc(IDeath)
            IAge = int(IDeath[0:4]) - int(IBirth[0:4])
            IAlive = False
        else:
            today = date.today()
            IAge = today.year - int(IBirth[0:4])
            IAlive = True
        indivTable.add_row([IId, IName, IGend, IBirth, IAge, IAlive, IDeath, IChild, ISpouse])
        IId, IName, IGen, IBirth, IAge, IAlive, IDeath, IChild, ISpouse = "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"
        dateCheck = "NA"
        typeCheck = ""
    if(typeCheck == 'FAM' and firstPassFam == 1):
        if(not (FMar == "NA")):
            FMar = dateCalc(FMar)
        if(not (FDiv == "NA")):
            FDiv = dateCalc(FDiv)
        if(len(FChild) < 1):
            FChild = "NA"
        FHName = husbName
        FWName = wifeName
        famTable.add_row([FId, FMar, FDiv, FHId, FHName, FWId, FWName, FChild])
        FId, FMar, FDiv, FHId, FHName, FWId, FWName, FChild = "NA", "NA", "NA", "NA", "NA", "NA", "NA", []
        dateCheck = "NA"  
        typeCheck = ""
        husbName, wifeName = "NA", "NA"
    print(indivTable)
    print(famTable)
