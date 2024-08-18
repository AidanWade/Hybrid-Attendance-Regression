class Config(object):
    params = urllib.parse.quote_plus(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=localhost;'
        r'DATABASE=;'
        r'Trusted_Connection=yes'
    )
    SCHEMA = 'sdmx'
    CONN_STR = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REAPPLY_NOISE=False
    REGEN_RANKINGS=False
    REGEN_RANDOM_SEARCH_RF_TXX=False
    REGEN_RANDOM_SEARCH_RF=False
    REGEN_GRID_SEARCH_RF_TXX=False
    REGEN_GRID_SEARCH_RF=False
    REGEN_GRID_SEARCH_XGB=False #next
    REGEN_GRID_SEARCH_SVR=False
    REGEN_GRID_SEARCH_RIDGE=False
    TEST_TRAIN_RATIO=0.8
    TEST_DATE_CUTOFF='2023-9-30'
    MASK_VALUE=True
