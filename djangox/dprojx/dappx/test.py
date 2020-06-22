# testing (remove later)

import numpy as np
import pandas as pd

def display_word(word):
	return word

def display_df():
	df = pd.DataFrame(np.random.randint(0,100,size=(15, 4)), columns=list('ABCD'))
	df_html = df.to_html()
	return df_html;

