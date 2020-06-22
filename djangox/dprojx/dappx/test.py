# testing (remove later)

import numpy as np
import pandas as pd

def display_word(word):
	return word

def display_df():
	df = pd.DataFrame(np.random.randint(0,100,size=(15, 7)), 
		columns=['Name', 'Address', 'City', 'State', 'Zip', 'Stars', 'Reviews'])
	df_html = df.to_html(index=False, col_space='10.1vw')
	return df_html
