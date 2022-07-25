from flask import Flask, render_template
from flask import jsonify
import csv
import os
import pandas as pd

app = Flask(__name__)

def readCSV(path):
	file_name=os.path.splitext(os.path.basename(path))[0]
	df = pd.read_csv(path)
	df['file_name'] = file_name
	return df

def readDAT(path):	
	file_name=os.path.splitext(os.path.basename(path))[0]
	datContent = [i.strip().split("|") if "|" in i else i.strip().split(",") for i in open(path).readlines()]
	headers = datContent.pop(0)
	df = pd.DataFrame(datContent, columns=headers)
	df['file_name'] = file_name
	return df

def query1(df):
    df = df[df['worth'] > 1.00]
    df = df[df['file_name'] == "sample_data.1"]
    df.to_csv('Output/consolidated_output.1.csv', encoding='utf-8')

@app.route('/api', methods=['GET'])
def BonusApi():
    path="Input/"
    paths=list()
    try:
        for (root, dirs, file) in os.walk(path):
            for f in file:
                paths.append(root+"/"+f)    
        
        df_list=[]
        for link in paths:
            ext=os.path.splitext(os.path.basename(link))[1]
            file_name=os.path.splitext(os.path.basename(link))[0]
            if file_name == "material_reference":
                mr_df=pd.read_csv(link)            
            else:
                if ext == ".csv":
                    df=readCSV(link)
                else:
                    df=readDAT(link)
                df_list.append(df)      
        
        all_df = pd.concat(df_list)
        convert_dict = {'material_id': int, 'worth':float}
        all_df = all_df.astype(convert_dict)     

        res=pd.merge(all_df, mr_df, left_on="material_id", right_on="id", how="left")        
        return jsonify(res.to_dict('records'))


    except Exception as e:
        raise e

@app.route('/', methods=['GET'])
def BonusUI():
    path="Input/"
    paths=list()
    try:
        for (root, dirs, file) in os.walk(path):
            for f in file:
                paths.append(root+"/"+f)        
        df_list=[]
        for link in paths:
            ext=os.path.splitext(os.path.basename(link))[1]
            file_name=os.path.splitext(os.path.basename(link))[0]
            if file_name == "material_reference":
                mr_df=pd.read_csv(link)            
            else:
                if ext == ".csv":
                    df=readCSV(link)
                else:
                    df=readDAT(link)

                df_list.append(df)      
        
        all_df = pd.concat(df_list)
        convert_dict = {'material_id': int, 'worth':float}
        all_df = all_df.astype(convert_dict)     

        res=pd.merge(all_df, mr_df, left_on="material_id", right_on="id", how="left")
        query1(res)
        return render_template('UI.html',data = enumerate(res.to_dict('records')), name="Vandana M Deshmukh")
    except Exception as e:
        raise e
        


if __name__ == '__main__':
    app.run(debug=True)