import pickle
#serialization or flattening 
import numpy as np
import simplekml

kml = simplekml.Kml()

with open('result_dataset4.pkl', 'rb') as f:
    data = pickle.load(f)
    