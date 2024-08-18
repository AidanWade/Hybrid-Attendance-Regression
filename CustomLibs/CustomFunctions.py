import seaborn as sns
import numpy as np
import sqlalchemy
import pickle

def save_to_file(obj,filename):
    with open(filename + '.pickle', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_from_file(filename):
    with open(filename + '.pickle', 'rb') as f:
        return pickle.load(f)

def plot_corr_heatmap(df,ax,method='pearson', **kwargs):
    """Helper Function for plotting correlation matrix heat maps"""
    # Compute the correlation matrix, exclude date,start of month date and named day of week
    corr = df.corr(method=method)

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap,  center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5},ax=ax, **kwargs)
    

def value_to_float(x):
    """Converts a number stored in string with abbreviations to number"""
    if(x is None):
        return x
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return 0.0

from sklearn.inspection import permutation_importance
def plot_permutation_importance(clf, X, y, ax=None):
    result = permutation_importance(clf, X, y, n_repeats=10, random_state=43, n_jobs=2)
    perm_sorted_idx = result.importances_mean.argsort()
    if ax:
        ax.boxplot(
            result.importances[perm_sorted_idx].T,
            vert=False,
            labels=X.columns[perm_sorted_idx],
        )
        ax.axvline(x=0, color="k", linestyle="--")
    return result


def fig_indexes(cols,i,base=0):
    """Small function to calculate 2D index within row*col shape for given int"""
    x= i // cols
    y= i % cols
    return(x+base,y+base)

def sqlcol(dfparam):    
    """Credit: https://stackoverflow.com/questions/34383000/pandas-to-sql-all-columns-as-nvarchar"""
    dtypedict = {}
    for i,j in zip(dfparam.columns, dfparam.dtypes):
        if "object" in str(j):
            dtypedict.update({i: sqlalchemy.types.NVARCHAR(length=255)})
                                 
        if "datetime" in str(j):
            dtypedict.update({i: sqlalchemy.types.DateTime()})

        if "float" in str(j):
            dtypedict.update({i: sqlalchemy.types.Float(precision=3, asdecimal=True)})

        if "int" in str(j):
            dtypedict.update({i: sqlalchemy.types.INT()})

        # if "bool" in str(j):
        #     dtypedict.update({i: sqlalchemy.types.bit()})

    return dtypedict

def what_pct_train(df,ind):
    """Calculate training / test percentage"""
    print(f'Train Pct: {100 * df.loc[:ind].shape[0] / df.shape[0]:.2f}%')