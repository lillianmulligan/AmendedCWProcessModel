# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import xlsxwriter as xlsw
import matplotlib.pyplot as plt 

#read in data from excel 
df = pd.read_excel (r'C:\Users\Lillian\Desktop\PilotCWdata.xlsx', sheet_name='InputData')

#create arrays from excel data
day = np.asarray(list(df['Day']))
P = np.asarray(list(df['Precipitation']))
temp = np.asarray(list(df['Temperature']))
COD_i = np.asarray(list(df['sCOD'])) 
OrgN_i = np.asarray(list(df['Organic N']))       
NH4_i = np.asarray(list(df['Ammonium']))  
NO3_i = np.asarray(list(df['Nitrate']))   
 
########## Water Balance Functions ########
#Horizontal flow CW dimensions
HF_width = 0.7874  #m
HF_length = 1.397  #m 
HF_height = 0.4572 #m 
HF_area = HF_width * HF_length #m2 

#Vertical flow CW dimensions
VF_width = 0.6477  #m
VF_length = 0.6477 #m
VF_height = 0.9398 #m
VF_area = VF_width * VF_length #m2

#create inflow set the same size as the input data
def VF_Qi(): 
 inflow = [0.08] * 172 #m3/day
 return inflow

#store results in an array
VF_Qi = np.asarray(VF_Qi())
#VF outflow equals VF inflow 
VF_Qo = VF_Qi
#HF inflow equals VF outflow
HF_Qi = VF_Qo

#calculate HF outflow (cubic m/day)
def HF_Qo():
    K = 571 #m/day
    A = HF_width*HF_height
    HF_Qo = [K*A*(HF_height/HF_length)/1000] * 172
    return HF_Qo
 
#store results in an array
HF_Qo = np.asarray(HF_Qo())

#calculate evapotranspiration (m/day)
def ET():
    dl = 11    #hours, day length
    I = 167.1  #C,heat index
    a = 6.75*(10**-7)*(I**3)-7.71*(10**-5)*(I**2)+1.792*(10**-2)*I+0.49239 
    ET = 16*dl/12*((10*temp/I)**a)/(30*100)/10
    return ET

#store results in an array
ET = np.asarray(ET())    

######### Water Balances ########
def VF_volume(): 
    VF_volume = 0.08                            #m3
    dVdt = VF_Qi-VF_Qi+(P*VF_area)-(ET*VF_area)  #m3/day
    dVdt = np.asarray(dVdt)                      #m3/day
    VF_volume += dVdt                            #m3
    return VF_volume*1000                        #L

def HF_volume(): 
    HF_volume = 0.099                             #m3
    dVdt = HF_Qi-HF_Qo+(P*HF_area)-(ET*HF_area)  #m3/day
    dVdt = np.asarray(dVdt)                      #m3
    HF_volume += dVdt                            #m3
    return HF_volume*1000                        #L

#store results in an array
VF_volume = np.asarray(VF_volume())    
HF_volume = np.asarray(HF_volume())

########### Oxygen Balance Functions #########
DO_i = 2.0    #mg/L
T = 22.6        #avg. temp of water (C)
VF_kR = .123  # (/day)
HF_kR = .008  # (/day)

#calculate DO saturation
DO_s = 14.652-0.41022*T+0.007991*T**2-0.00007777*T**3 #g/m3

#calculate mass flux 
VF_JO2 = VF_kR*(DO_s-DO_i)
HF_JO2 = HF_kR*(DO_s-DO_i)

#VF Monod Parameters for heterotrophs
VF_HT_Y = 1.23
VF_HT_DO_Ks = 1
VF_HT_TOC_Ks = 50
VF_HT_mu_max = 4
TOC = COD_i
#VF Monod Parameters for autotrophs
VF_NS_Y = 0.084 
VF_NS_DO_Ks = 1
VF_NS_NH4_Ks = 1
VF_NS_mu_max = .001 

#VF Monod equations
VF_HT_growth = VF_HT_mu_max*(TOC/(TOC+VF_HT_TOC_Ks))*(VF_HT_DO_Ks/(DO_i+VF_HT_DO_Ks))
VF_HT_res = VF_HT_growth/VF_HT_Y
VF_NS_growth = VF_NS_mu_max*(NH4_i/(NH4_i+VF_NS_NH4_Ks))*(DO_i/(DO_i+VF_NS_DO_Ks))
VF_NS_res = VF_NS_growth/VF_NS_Y

#HF Monod Parametersfor heterotrophs
HF_HT_Y = 1.23
HF_HT_DO_Ks = 1
HF_HT_TOC_Ks = 50
HF_HT_mu_max = 4
TOC = COD_i
#VF Monod Parameters for autotrophs
HF_NS_Y = 0.084 
HF_NS_DO_Ks = 1
HF_NS_NH4_Ks = 1
HF_NS_mu_max = .01

#HF Monod equations
HF_HT_growth = HF_HT_mu_max*(TOC/(TOC+HF_HT_TOC_Ks))*(HF_HT_DO_Ks/(DO_i+HF_HT_DO_Ks))
HF_HT_res = HF_HT_growth/HF_HT_Y
HF_NS_growth = HF_NS_mu_max*(NH4_i/(NH4_i+HF_NS_NH4_Ks))*(DO_i/(DO_i+HF_NS_DO_Ks))
HF_NS_res = HF_NS_growth/HF_NS_Y

#DO mass balances
VF_DO = DO_i + VF_JO2 - VF_HT_res - VF_NS_res
HF_DO = VF_DO + HF_JO2 - HF_HT_res - HF_NS_res

########## COD Balance Functions #########
Q = VF_Qi*1000 #L
Qi = Q
Qo = HF_Qo*1000 #L

#Monod parameters
X = 800 #mg/L 
VF_Y = 0.5613 #mg biomass/mg substrate
VF_Ks = 3.4559 #mg/L
VF_mu_max = 0.0212 #per hour
HF_Y = 0.5611 #mg biomass/mg substrate
HF_Ks = 3.4561 #mg/L
HF_mu_max = 0.049 #per hour

#Monod Equation
VF_rs = (-1/VF_Y)*(VF_mu_max*COD_i)/(VF_Ks+COD_i)*X
HF_rs = (-1/HF_Y)*(HF_mu_max*COD_i)/(HF_Ks+COD_i)*X

#COD mass balance solutions
VF_COD = ((Q*COD_i)+(VF_rs*VF_volume))/Q
HF_COD = ((Qi*VF_COD)+(HF_rs*HF_volume))/Qo

########## Nitrogen Balance Functions #########
#Background concentrations (mg/L)
OrgN_0 = 0.5
NH4_0 = 0     
NO3_0 = 0     
          
######Rate constants (per day)
#plant decomposition
VF_kpd = .35
HF_kpd = .014

#mineralization
km_a = 0.05 #aerobic
km_an = 0.08 #anaerobic

#nitrification
kn_a =  .75 #aerobic 
kn_an = 0.5 #anaerobic

#plant uptake of ammonia 
VF_kpu_NH4 = .05
HF_kpu_NH4 = .15 

#denitrification
kdn_an = 1.5 #aerobic 
kdn_a = 0.95 #anaerobic 

#plant uptake of nitrate
VF_kpu_NO3 = .25
HF_kpu_NO3 = .95

#nitrogen mass balance solutions 
def VF_OrgN():
    if np.any(VF_DO) < 1:
        km = km_an
    else: km = km_a
    VF_OrgN =(Q*OrgN_i)/(Q-(VF_kpd*VF_volume)+(km*VF_volume))+OrgN_0
    return VF_OrgN

def HF_OrgN():
    if np.any(HF_DO) < 1:
        km = km_an
    else: km = km_a
    HF_OrgN =(Qi*OrgN_i)/(Qo-(HF_kpd*VF_volume)+(km_an*HF_volume))+OrgN_0
    return HF_OrgN

def VF_NH4():
    if np.any(VF_DO) < 1:
        kn = kn_an
    else: kn = kn_a 
    VF_NH4 =(Q*NH4_i+(km_a*VF_OrgN()*VF_volume))/(Q+(kn*VF_volume)+(VF_kpu_NH4*VF_volume))
    return VF_NH4

def HF_NH4():
    if np.any(HF_DO) < 1:
        kn = kn_an
    else: kn = kn_a 
    HF_NH4 =(Qi*VF_NH4()+(km_an*HF_OrgN()*HF_volume))/(Qo+(kn*VF_volume)+(HF_kpu_NH4*HF_volume)) 
    return HF_NH4

def VF_NO3():
    if np.any(VF_DO) < 1:
        kdn = kdn_an
    else: kdn = kdn_a
    VF_NO3 = ((Q*NO3_i)+(kn_a*VF_NH4()*VF_volume))/(Q+(kdn*VF_volume)+(VF_kpu_NO3*VF_volume)) 
    return VF_NO3

def HF_NO3():
    if np.any(HF_DO) < 1:
        kdn = kdn_an
    else: kdn = kdn_a 
    HF_NO3 = ((Q*(VF_NO3()))+(kn_an*HF_NH4()*HF_volume))/(Q+(kdn_an*HF_volume)+(HF_kpu_NO3*HF_volume))
    return HF_NO3

#######Adsorbent Amended CWs###########
###### Amended COD in HF ######
#Monod parameters
X = 800 #mg/L 
A_HF_Y = 0.5611 #mg biomass/mg substrate
A_HF_Ks = 3.4561 #mg/L
A_HF_mu_max = .0495 #per hour

#Monod Equation
A_HF_rs = (-1/A_HF_Y)*(HF_mu_max*COD_i)/(A_HF_Ks+COD_i)*X

#mass flux parameters
rho_biochar = 90000 #g/m3
r_biochar = .0015 #m
m_biochar = 2600 #g
a_biochar = (3/r_biochar)*(m_biochar/rho_biochar/HF_volume) #m2/m3
qcod= 49 #mg COD/g biochar
Ds_biochar = (5.5*10**-11)*864000 #m2/day

#mass flux equation
Jcod = -rho_biochar*qcod*Ds_biochar

#amended mass balance solutions 
A_HF_COD = ((Qi*VF_COD)+(A_HF_rs*HF_volume)+(Jcod*a_biochar*HF_volume))/Qo

###### Amended nitrogen functions ######
####Rate constants (per day)
#nitrification
A_kn_a =  1.5 #aerobic 
A_kn_an = .5  #anaerobic

#plant uptake of ammonia 
A_VF_kpu_NH4 = .05
A_HF_kpu_NH4 = 1.5

#denitrification 
A_kdn_an = .5  #aerobic 
A_kdn_a = .008 #anaerobic

#plant uptake of nitrate 
A_VF_kpu_NO3 = .005
A_HF_kpu_NO3 = .10

#mass flux parameters
rho_zeolite = 877000 #g/m3
r_zeolite = .00025 #m
m_zeolite = 23000 #g
a_zeolite = (3/r_zeolite)*(m_zeolite/rho_zeolite/VF_volume) #m2/m3
qNH4= 6.75 #mg NH4/g zeolite
Ds_zeolite = (5.2*10**-12)*864000 #m2/day

#mass flux equation
JNH4 = -rho_zeolite*qNH4*Ds_zeolite 

def A_VF_NH4():
    if np.any(VF_DO) < 1:
        kn = A_kn_an
    else: kn = A_kn_a 
    VF_NH4 =(Q*NH4_i+(km_a*VF_OrgN()*VF_volume)+(JNH4*a_zeolite*VF_volume))/(Q+(kn*VF_volume)+(A_VF_kpu_NH4*VF_volume))
    return VF_NH4

def A_HF_NH4():
    if np.any(HF_DO) < 1:
        kn = kn_an
    else: kn = kn_a 
    HF_NH4 =(Qi*A_VF_NH4()+(km_an*HF_OrgN()*HF_volume))/(Qo+(A_kn_an*VF_volume)+(HF_kpu_NH4*HF_volume)) 
    return HF_NH4

def A_VF_NO3():
    if np.any(VF_DO) < 1:
        kdn = A_kdn_an
    else: kdn = A_kdn_a
    A_VF_NO3 = ((Q*NO3_i)+(A_kn_a*A_VF_NH4()*VF_volume))/(Q+(A_kdn_a*VF_volume)+(A_VF_kpu_NO3*VF_volume)) 
    return A_VF_NO3

def A_HF_NO3():
    if np.any(HF_DO) < 1:
        kdn = A_kdn_an
    else: kdn = A_kdn_a 
    A_HF_NO3 = ((Q*(A_VF_NO3()))+(A_kn_an*A_HF_NH4()*HF_volume))/(Q+(A_kdn_an*HF_volume)+(A_HF_kpu_NO3*HF_volume))
    return A_HF_NO3

#example plot 
plt.title("COD in HF+biochar")
plt.xlabel("Day") 
plt.ylabel("(mg/L)")
xpoints = np.array(day)
ypoints = np.array(A_HF_COD)
plt.ylim(0,600)
plt.plot(xpoints, ypoints)
plt.show()

#write ro excel 
df = pd.DataFrame(HF_COD).T
openpyxl = r'C:\Users\Lillian\Desktop\PilotCWdata.xlsx'
writer = pd.ExcelWriter(openpyxl, engine='openpyxl')
df.to_excel(writer, sheet_name="Effluents", startrow=1, startcol=1, header=False, index=False)