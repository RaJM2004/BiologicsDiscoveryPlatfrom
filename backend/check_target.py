from chembl_webresource_client.new_client import new_client
import pandas as pd

target = new_client.target
target_query = target.search('GPR35')
targets = pd.DataFrame.from_dict(target_query)
print(targets[['target_chembl_id', 'pref_name', 'target_type']])
