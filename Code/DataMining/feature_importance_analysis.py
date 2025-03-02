import pandas as pd
from sklearn.tree import DecisionTreeRegressor

# Used to analyze feature importance for all features considered
def analyze_feature_importance(regressor, feature_names):
    # extract feature importance from trained decision tree regressor
    importances = regressor.feature_importances_
    
    # dataframe to store feature names with corresponding importances
    feature_importance_df = pd.DataFrame({'Feature' : feature_names, 'Importance': importances})
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
    
    return feature_importance_df