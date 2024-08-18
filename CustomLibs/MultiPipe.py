
import numpy as np
import pandas as pd
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.svm import LinearSVR
from sklearn.model_selection import TimeSeriesSplit, KFold, cross_validate
from sklearn.pipeline import  make_pipeline



class MultiPipe:
    """Custom class to store a set of pipeline components and metrics"""
    def __init__(self,rs=43) -> None:
        ## Initialisation

        ## Regressor Definitions
        self.Regressors = {}
        self.Regressors['Linear Regression']=LinearRegression()
        self.Regressors['Random Forest Regressor']=RandomForestRegressor(random_state=rs)
        self.Regressors['XGBoost Regressor']=XGBRegressor(seed=rs)
        # self.Regressors['KNN Regressor']=KNeighborsRegressor()
        self.Regressors['Linear SVR']=LinearSVR(dual='auto',max_iter=10000,random_state=rs)

        # Empty Dictionaries for storing groups of transformers, pipelines and resulting metrics
        self.Transformers={}
        self.QC_Set = {}
        self.ScoreSet = {}

        ## Scoring Definitions
        self.Scorers = {}
        self.Scorers['Explained Variance'] = 'explained_variance'
        self.Scorers['R^2 Score'] = 'r2'
        self.Scorers['Mean Absolute Error'] = 'neg_mean_absolute_error'
        self.Scorers['Mean Squared Error'] = 'neg_mean_squared_error'
        self.Scorers['RMS Error'] = 'neg_root_mean_squared_error'

        # Cross validation methods
        # self.CV = KFold(n_splits=splits,shuffle=True,random_state=rs)
        self.CV = TimeSeriesSplit(gap=0, max_train_size=None, n_splits=10, test_size=10)


    def AddPreProc(self,pipe,key):
        ## Add a preprocess transformer list to the library
        self.Transformers[key]=pipe

    def PurgeQCSet(self,qc_set_key):
        ## Remove an existing set of pipelines and results from the library
        try:
            del self.QC_Set[qc_set_key]
            del self.ScoreSet[qc_set_key]
        except:
            pass
        

    def AddQCSet(self,preproc_key,qc_set_key=None,regs=None):
        ## A QC set is a combination of a preprocessing flow and, by default, all defined regression models to create
        ## a collection of regression pipelines. A QC set can have multiple associated preprocessing flows if AddQCSet 
        ## is called multiple times. The QCSet is used to group together a collection of tests, like a test family
        ## though each element can have a different preprocess and be tested with a different set of data in CalculateScores method

        regs = self.Regressors.items() if regs == None else regs
        # Pipeset name will default to equal preproc name if not otherwise set
        qc_set_key = preproc_key if qc_set_key == None else qc_set_key
        # Look up the preprocessor - must already exist
        preproc = self.Transformers[preproc_key]
        # If this is the first set of pipes added for this QC set, initialise it as an empty dict for the pipes and the scores otherwise don't overwrite it
        self.QC_Set[qc_set_key]={} if qc_set_key not in self.QC_Set.keys() else self.QC_Set[qc_set_key]
        self.ScoreSet[qc_set_key]={} if qc_set_key not in self.ScoreSet.keys() else self.ScoreSet[qc_set_key]
        # If this is the first call to the qc set and preprocessor, initialise that combo as an empty dict otherwise don't overwrite it
        self.QC_Set[qc_set_key][preproc_key]={} if preproc_key not in self.QC_Set[qc_set_key].keys() else self.QC_Set[qc_set_key][preproc_key]
        self.ScoreSet[qc_set_key][preproc_key]={} if preproc_key not in self.ScoreSet[qc_set_key].keys() else self.ScoreSet[qc_set_key][preproc_key]
        # For each selected regression model, combine with preprocess to create pipeline and store it in the QC set dict
        # At the same time, intialise an empty dict for the scores, overwriting if already exists
        for r in regs:
            p = make_pipeline(preproc,r[1])
            self.QC_Set[qc_set_key][preproc_key][r[0]]=p
            self.ScoreSet[qc_set_key][preproc_key][r[0]]={}
    
    def CalculateScores(self,qc_set_key,preproc_key,data_key,X,y,reg_filter=[],cv=None,verbose=False):
        ## Must be called after adding the QC set, Calculte scores takes the collection of pipes defined for the QC Set / preproc combo, input X and y
        ## and runs cross validate with the defined cv. Can restrict to a subset of the available regression models or add a custom CV when calling. The
        ## Data key is the test name and used on the X axis when presenting results. All defined scorers are used.

        cv=self.CV if cv == None else cv

        # For each pipe in the qc set / preproc group (e.g. for each regression model)
        for reg_key,reg_pipe in self.QC_Set[qc_set_key][preproc_key].items():
            # Check the model is not filtered out
            if reg_key in reg_filter or len(reg_filter) == 0:
                if verbose:
                    print(f'{cv} Cross Validating Regressor: {reg_key}')
                # Calcualte scores, using Scorers and CV
                cv_scores=cross_validate(reg_pipe,X,y,scoring=self.Scorers,cv=cv)
                # Initialise an empty dict
                agg_scores={}
                # Parse the result from cross_validate into something more readable
                for metric in self.Scorers.keys():
                    agg_scores[metric] = (abs(np.mean(cv_scores["test_" + metric])),np.std(cv_scores["test_" + metric]),X.shape[1],X.shape[0])
                # Add this score dictionary to the scoreset using the data_key (test name) as the key.
                self.ScoreSet[qc_set_key][preproc_key][reg_key][data_key]=agg_scores
        
        # Send a copy of scores back to the executing program
        return agg_scores
    

    def GetScores(self,qc_set_keys=None,preproc_keys=None,reg_keys=None,data_keys=None,metric_keys=None,verbose=False,ValFilter=0):
        ## Calculate scores extracts all scorers from scorers, GetScores method allows to subset this, CalculateScores must be run first
        ## Update filter lists, will take everything if fill not passed. By default on a QC set, e.g. a test family needs to be provide
        ## and GetScores will extract all scores for this family into a temporary dataframe as well printint to stdout if verbose, returning
        ## a printable list
        qc_set_keys = self.QC_Set.keys() if qc_set_keys == None else qc_set_keys
        reg_keys = self.Regressors.keys() if reg_keys == None else reg_keys
        self.active_metrics = self.Scorers.keys() if metric_keys == None else metric_keys

        # Output headers
        if verbose:
            print(f'QC_Set'.ljust(20)+'Preprocessor'.ljust(20)+f'Regressor'.ljust(25)+f'Stage'.ljust(20)+f'Features'.ljust(10)+f'Records'.ljust(10)+f'Metric'.ljust(25) + f'Value ('+ u'\u00B1' + 'Std.Dev)')
        # Output headers row for list
        printlist=[['QC_Set','Preprocessor','Regressor','Stage','Features','Records','Metric','Value','Std.Dev']]
        # Start iterating through the nested dictionaries to unpack results if included in filters
        for qc_set_key in self.ScoreSet.keys():
            if qc_set_key in qc_set_keys:
                for preproc_key in self.ScoreSet[qc_set_key].keys():
                    var_preproc_keys = self.ScoreSet[qc_set_key].keys() if preproc_keys == None else preproc_keys
                    if preproc_key in var_preproc_keys:
                        # don't need a var_ intermediary here as the master list is stored in the regression dict, not the scoreset dict
                        for reg_key in self.ScoreSet[qc_set_key][preproc_key].keys():
                            if reg_key in reg_keys:                             
                                for data_key in self.ScoreSet[qc_set_key][preproc_key][reg_key].keys():
                                    var_data_keys = self.ScoreSet[qc_set_key][preproc_key][reg_key].keys() if data_keys == None else data_keys
                                    if data_key in var_data_keys:
                                        for metric_key,metrics in self.ScoreSet[qc_set_key][preproc_key][reg_key][data_key].items():
                                            if metric_key in self.active_metrics:
                                                if verbose:
                                                    print(f'{qc_set_key}'.ljust(20)+f'{preproc_key}'.ljust(20)+f'{reg_key}'.ljust(25)+f'{data_key}'.ljust(20) +f'{metrics[2]}'.ljust(10) +f'{metrics[3]}'.ljust(10) +f'{metric_key}'.ljust(25) + f'{metrics[0]:.5f} ' + u'\u00B1' + f'{metrics[1]:.3f}')
                                                # Can optionally exclude nonsenesical metric values using ValFilter - the same value is used to filter all metrics though!    
                                                # Extract value and stddev from the ScoreSet dict
                                                val = metrics[0] if metrics[0]<ValFilter or ValFilter==0 else np.NaN
                                                sd = metrics[1] if metrics[0]<ValFilter or ValFilter==0 else np.NaN

                                                printlist.append([qc_set_key,preproc_key,reg_key,data_key,metrics[2],metrics[3],metric_key,val,sd])
        # Create a dataframe from the printlist for use with GraphScores
        self.metricframe = pd.DataFrame(printlist[1:],columns=printlist[0])
        # Return the csv lists
        return printlist
   
    def GraphScores(self,qc_set_key,axs,altax=None):
        ## A convenience method which handles creation of consistent metric graphs with centrally controlled settings.
        ## Normally used with a subset of QC keys
        if altax:
            axs2=[]
        df = self.metricframe.loc[self.metricframe['QC_Set']==qc_set_key].groupby('Metric')
        for i,(metric,sub_df) in enumerate(df):
            axs[i].set_title(f'Model {metric}',fontsize=12)
            axs[i].set_ylabel(f'{metric} Value',fontsize=11)
            axs[i].set_xlabel(f'Processing Step',fontsize=11)
            axs[i].tick_params(axis='x', labelrotation=45, labelsize=10)
            axs[i].grid(visible=True,which='Major',axis='both') 
            
            _ = sns.lineplot(data=sub_df,x='Stage',y='Value',hue='Regressor',ax=axs[i])
            if altax:
                axs2.append(axs[i].twinx())
                _ = sns.lineplot(data=sub_df,x='Stage',y=altax,ax=axs2[i],color='r',linestyle='dashed',label=altax)
            axs[i].get_legend().set_visible(False)
        axs[i].legend(loc='upper left')
        axs[i].legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    

