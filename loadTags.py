import sqlite3 as sl

con = sl.connect('sdn.db')

sql = 'INSERT INTO tag (title) values(?)'

_tagdata = [
    'SAP S/4HANA Cloud Public Edition Research and Development',
    'SAP BTP cockpit', 'SAP S/4HANA Cloud Public Edition Sourcing and Procurement',
    'SAP Project and Resource Management',
    'SAP Business Data Cloud',
    'SAP Business Data Cloud',
    'SAP SuccessFactors HCM Suite', )
    'Customer Onboarding Services',)
    'SAP Enterprise Support', )
    'SAP S/4HANA Cloud Public Edition Supply Chain',)
    'SAP Enterprise Support', )
    'SAP Enterprise Support, cloud editions',)
    'SAP Sales Cloud Version 2', )
    'SAP Service Cloud Version 2', )
    'SAP S/4HANA Cloud Public Edition Supply Chain',)
    'SAP Emarsys', )
    'SAP S/4HANA Cloud Public Edition Supply Chain',)
    'SAP Enterprise Support', )
    'SAP Enterprise Support, cloud editions',)
    'SAP Sales Cloud Version 2', )
    'SAP Service Cloud Version 2', )
    'SAP S/4HANA Cloud Public Edition Finance')
]


    [('SAP Business Network for Procurement and SAP Business Network for Supply Chain',),('SAP Data Custodian',),('SAP Build Code',),('SAP Build Code',),('Joule',),('SAP Build Code',),('Joule',),('SAP Build Code',),('SAP Build Code',),('ABAP Cloud',),('SAP SuccessFactors Agent Performance Management',),('Joule',),('ABAP Cloud',),('SAP Business Accelerator Hub',),('ABAP Cloud',),('SAP solutions for quote-to-cash management',),('Joule',),('Joule',),('SAP Business Network for Procurement and SAP Business Network for Supply Chain',),('SAP AI Services',),('Joule',),('SAP Build Code',),('Joule',),('SAP Event Broker for SAP cloud applications',),('ABAP Cloud',),('SAP Build Code',),('SAP Signavio Process Navigator',),('Joule',),('Joule',),('SAP Signavio Process Navigator',),('SAP Build Code',),('ABAP Cloud',),('Joule',),('SAP Build Code',),('SAP Build Code',),('SAP Signavio Process Explorer',),('SAP SuccessFactors Territory and Quota',),('SAP SuccessFactors Territory and Quota',),('SAP SuccessFactors Territory and Quota',),('SAP Secure Login Service for SAP GUI',),('SAP AI Services',),('ABAP Cloud',),('SAP Build Code',),('SAP Business Network for Procurement and SAP Business Network for Supply Chain',),('SAP Build Code',),('Joule',),('SAP Build Code',),('SAP Build Code',),('SAP Build Code',),('SAP Build Code',),('SAP Build Code',),('SAP Build Code',),('SAP AI Services',),('Joule',),('SAP Build Code',),('SAP Build Code',),('SAP Build Code',),]


tagdata = [
('SAP Business One Cloud, SAP-hosted option',),
]

with con:
    con.executemany(sql, tagdata)






