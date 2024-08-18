from sklearn.base import BaseEstimator, TransformerMixin, OneToOneFeatureMixin
from sklearn.preprocessing import StandardScaler,SplineTransformer,OneHotEncoder
from sklearn.compose import ColumnTransformer
import numpy as np

class SpikeRemover(BaseEstimator, TransformerMixin, OneToOneFeatureMixin):
    """Can be used to clear values (replace with NaN) based on zscore threshold (default) or replace specific values"""
    def __init__(self, cutvalue=5, cutmode='zthresh'):
        self.cutvalue=cutvalue
        self.cutmode=cutmode
    def fit(self, X, y=None):
        self.n_features_in_ = X.shape[1]
        self.feature_names_in_= X.columns.tolist()
        return self
    def transform(self, X, y=None):
        X_dspike = X.copy()
        for column in X.columns:
            zmean=X_dspike[column].mean()
            zstd=X_dspike[column].std()
            if self.cutmode=='zthresh':
                X_dspike[column] = X_dspike[column].transform(lambda x: np.NaN if abs(x - zmean)/ zstd > self.cutvalue else x)
            elif self.cutmode=='value':
                X_dspike[column] = X_dspike[column].transform(lambda x: np.NaN if x == self.cutvalue else x)
        self.FeatNames = X.columns.tolist()
        return X_dspike
        
    
class DailyMeanImputer(BaseEstimator, TransformerMixin, OneToOneFeatureMixin):
    def __init__(self, groupby_name, rolling=0):
        # self.column_name = column_name
        self.groupby_name = groupby_name
        self.rolling=rolling
    def fit(self, X, y=None):
        self.n_features_in_ = X.shape[1]
        self.feature_names_in_= X.columns.tolist()
        self.lookup = X.select_dtypes(include='number').groupby(self.groupby_name).mean()
        # print('fitted')
        return self
    def transform(self, X, y=None):
        X_filled = X.copy()
        for column in X.drop(columns=self.groupby_name).select_dtypes(include='number').columns:
            if self.rolling==0:
                X_filled.loc[X_filled[column].isnull(),column]=X_filled[self.groupby_name].map(self.lookup[column])
                # X_filled[column] = X_filled.groupby(self.groupby_name,observed=False)[column].transform(lambda x: x.fillna(x.mean()))
            else:
                X_filled[column] = X_filled.groupby(self.groupby_name,observed=False)[column].transform(lambda x: x.fillna(x.rolling(self.rolling,min_periods=1,center=True).mean()))
        self.FeatNames = X.columns.tolist()
        return X_filled
    
def periodic_spline_transformer(period, n_splines=None, degree=3):
    if n_splines is None:
        n_splines = period
    n_knots = n_splines + 1  # periodic and include_bias is True
    return SplineTransformer(
        degree=degree,
        n_knots=n_knots,
        knots=np.linspace(0, period, n_knots).reshape(n_knots, 1),
        extrapolation="periodic",
        include_bias=True,
    )


def filtered_transformer(feature_list):
    """ Need to recreate transformer depending on which features are included """
    tra=[]
    if 'Day_Of_Week' in feature_list:
        tra.append(("cyclic_weekday", periodic_spline_transformer(5, n_splines=3), ['Day_Of_Week']))
    if 'Quarter' in feature_list:
        tra.append(("cyclic_quarter", periodic_spline_transformer(4, n_splines=3), ['Quarter']))
    if 'Month' in feature_list:
        tra.append(("cyclic_month", periodic_spline_transformer(12, n_splines=6), ['Month']))
    if 'School_Holiday' in feature_list:
        tra.append(('bin',OneHotEncoder(sparse_output=False,drop='if_binary'),['School_Holiday']))
    return ColumnTransformer(
        transformers=tra,
        remainder=StandardScaler(),
        force_int_remainder_cols=False,
        verbose_feature_names_out=False
    )