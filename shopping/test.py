import pandas as pd
# import numpy as np

# # # Create a sample DataFrame
# # data = {'Returning': ['Returning_Visitor', 'New_Visitor', 'Returning_Visitor', 'Other']}
# # df = pd.DataFrame(data)

# # # Use np.where() to replace values in the 'Returning' column
# # df['Returning'] = np.where(df['Returning'] == 'Returning_Visitor', 1, 0)

# # # Display the DataFrame after replacing values
# # print(df)
# arr = np.array([1, 2, 1, 4, 5])
# print((arr == 1).sum())
from shopping import *
evidence, labels = load_data('shopping.csv')
print(evidence.dtypes)
# df = pd.read_csv('shopping.csv')
# print(df['Revenue'].dtype)
