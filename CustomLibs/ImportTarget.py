import pandas as pd
import sqlalchemy
class ImportTarget:
    """Custom class to handle import from excel and export to sql"""
    def __init__(self,config=None) -> None:
        self.path=''
        if config==None:
            self.config={'path':None,'sheet':0,'cols':None,'frow':0,'types':[],'schema':'Raw','table':''}  
        else:
            self.config=config

    def load_data(self,path=None):
        path=self.config['path'] if path==None else path
        if path.endswith('.csv'):
            with open(path,"r") as filein:
                print(f'Reading: {path}',end='')
                self.df=pd.read_csv(filein,skiprows=int(self.config['frow']),usecols=[int(x) for x in self.config['cols'].split(',')],header=0)
                print(f', read {len(self.df)} rows')
        elif path.endswith('.xlsx'):
            with pd.ExcelFile(path) as filein:
                print(f'Reading: {path}, sheet: {filein.sheet_names[int(self.config["sheet"])]}',end='')
                self.df = pd.read_excel(filein,sheet_name=int(self.config['sheet']),usecols=self.config['cols'],skiprows=int(self.config['frow']),header=0)
                print(f', read {len(self.df)} rows to dataframe')
        else:
            raise TypeError('unsupport file type')
        self.df.index.names=[self.config['table']+'ID']
        self.df.columns=['_'.join(str(x).split()) for x in self.df.columns]
        
    def export_data(self,engine):
        servername=str(engine.url).upper().split('SERVER%3D')[1].split('%3B')[0]
        dbname=str(engine.url).upper().split('DATABASE%3D')[1].split('%3B')[0] 
        with engine.connect() as conn:
            print(f'Writing to: [{servername}].[{dbname}].[{self.config["schema"]}].[{self.config["table"]}], ', end='')
            self.df.to_sql(self.config['table'],conn,schema=self.config['schema'],if_exists='replace',dtype=dict(zip([self.df.index.names]+[*self.df],self.config['types'])))
            with conn.execution_options(yield_per=100).execute(sqlalchemy.text('SELECT COUNT (*) FROM ' + f'[{self.config["schema"]}].[{self.config["table"]}]')) as result:
                print(f'{result.fetchone()[0]} rows written')