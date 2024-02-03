import requests
import json
import pandas as pd

url = "https://api.solana.fm/v1/addresses/96yguar2XfrJqhUAvjnV2mdo9xaq571hJ9Kk21nhULAi/tokens"
#42brAgAVNzMBP7aaktPvAmBSPEkehnFQejiZc53EpJFd
#51Ctg64eDz1Jowhbp9qnkQzujLgfZVi9FFJXAvvq9Vyb

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

jsonResp = json.loads(response.text)
tokens = jsonResp["tokens"]
tokenBalances = []
for key in tokens:
    try:
        #print(key)
        #print(tokens[key]["tokenData"]["tokenMetadata"]["onChainInfo"]["symbol"])
        #print(tokens[key]["balance"])
        tokenBalances.append([tokens[key]["tokenData"]["tokenMetadata"]["onChainInfo"]["symbol"], tokens[key]["balance"]]) 
    except:
        print("An exception occurred")

df = pd.DataFrame(tokenBalances, columns=['Symbol', 'Balance'])
print(df)