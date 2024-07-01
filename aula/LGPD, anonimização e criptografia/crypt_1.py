import pandas as pd
from Crypto.Hash import SHA512


df = pd.read_csv('Dados/Passenger+Crew.csv')
df.head()

# Convert column to string
df['Passager'] = df['Passager'].astype(str)
df['Passager_HASH'] = df['Passager'].apply(
    lambda x: 
        SHA512.new(x.encode()).hexdigest()
)


