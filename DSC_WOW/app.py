"""
Created on Fri Dec 11 12:46:56 2020

@author: Harish_3055
Team Name    :- Mission I'mpossible
Project Name :- bSafe
Project Desc :- In the recent past we witnessed a lot of vulnerability against women on various occasions.
                To safeguard women we have come up with an idea to build a better environment. Taking 
                into account the google news source of data about crime we have classified the news based 
                on crime rate. So people can use our app to know more about a location and safeguard them
                from danger.
Packages used:-
Flask       ->  We have used the flask to connect the html part and the python part.
flask_ngrok ->  To make the Flask apps running on localhost available over the internet via the excellent ngrok tool.
tensorflow  ->  To load the trained model and to get the predicted result.
GoogleNews  ->  To get the news result on a particular date, location, Country.   
"""
import flask
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, render_template
import tensorflow as tf
from GoogleNews import GoogleNews as gn
from tensorflow.keras.preprocessing.sequence import pad_sequences
#Loaded the trained NLP classification model to get the crime rate of the news
model = tf.keras.models.load_model('H:/DSC_WOW/model_news.h5')
import pickle
with open('H:/DSC_WOW/tokenizer.pickle', 'rb') as handle:
    vec= pickle.load(handle)
app=Flask(__name__)
run_with_ngrok(app)

@app.route('/')
def home():
    return render_template('index.html')#To display the details in html

@app.route('/news',methods=['POST'])
def news():
    country=request.form['country']#to get country
    location=request.form['location']#to get location
    start_date=request.form['start_date']#to get start 
    end_date=request.form['end_date']#to get end date
    
    #to covert yyyy-mm-dd to mm-dd-yyyy
    start_date = start_date[3:5]+"-"+start_date[5:]+"-"+start_date[:3]
    end_date=end_date[3:5]+"-"+end_date[5:]+"-"+end_date[:3]
    start_date=start_date[3:]+start_date[0]
    end_date=end_date[3:]+end_date[0]
    
    #Used Googlenews package to get news based on entered details
    goog = gn(country)# to set the GoogleNews for a particular country
    goog.set_lang('en')#to set the GoogleNoews to English language
    goog.set_time_range(start_date,end_date)# to set the GoogleNews for a particular language
    goog.search(str(location)+' crime woman')# to set the GoogleNews for a particular location
    result=goog.results() #Get the searched result
    
    predicted={}
    pred=[]
    var_link={}
    for i in result:#To predict the correct crime rate for the particular news result 
        txt=[str(i['title'])]
        txt1=str(i['link'])
        key = vec.texts_to_sequences(txt)
        key = pad_sequences(key)
        if txt != ['']:
            f=model.predict(key)[0][0]*100
            predicted[str(i['title'])]=f
            var_link[str(i['title'])]=txt1
            pred.append(round(f,2))
            
    #To arrange the value in descending order based on crime rate to get the dangerous crime first 
    predicted=dict(sorted(predicted.items(), key=lambda item: item[1],reverse=True))
    predicted=list(predicted.keys())
    pred=sorted(pred,reverse=True)
    print(pred)
    color=[]
    link=[]
    for i in range(len(predicted)):
        link.append(var_link[predicted[i]])
    for i in range(len(pred)):
        if pred[i]>=75:
            color.append('red')
        elif pred[i]>=50 and pred[i]<75:
            color.append('orange')
        else:
            color.append('Green')
            
    #To display the predicted output in output.html
    return render_template('output.html',a=predicted,leng=len(predicted),pred=pred,col=color,link=link)
if __name__== '__main__':
    app.run()