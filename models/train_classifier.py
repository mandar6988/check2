#importing required liabraries

import sys
import nltk
import pickle
nltk.download(['punkt', 'wordnet', 'averaged_perceptron_tagger'])
nltk.download('stopwords')
from sqlalchemy import create_engine
import re
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

def load_data(database_filepath):
    """
    This function is loads database
    
    It takes database filepath as input argument
    And it returns 3 varibles
    """
    engine = create_engine('sqlite:///{}'.format(database_filepath))
    df=pd.read_sql_table('message_table',engine) # loading database
    X = df.message
    Y = df.loc[:, 'related':'direct_report']
    print((Y.shape))
    category_names=list(df.columns[4:] )  # column names                
    return X,Y,category_names


def tokenize(text):
    """
    It takes text as input argumen
    It performs tokenization on input data.
    It Returns cleaned data
    """
    detected_urls = re.findall(url_regex, text)
    for url in detected_urls:
        text = text.replace(url, "urlplaceholder")
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
   
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
    print(clean_tokens)
    clean_tokens = [w for w in clean_tokens if w not in stopwords.words("english")]
    return clean_tokens
    


def build_model():
    """
    This function performs model building to train network.
    
    """
    # Pipeline is defined
    pipeline = Pipeline([('vect', CountVectorizer(tokenizer=tokenize)),
                     ('tfidf', TfidfTransformer()),
                     ('clf', MultiOutputClassifier(RandomForestClassifier()))])
    # Parameters are decided 
    parameters={'vect__ngram_range': ((1, 1), (1, 2))}
    cv=GridSearchCV(pipeline, param_grid=parameters)
    return cv


def evaluate_model(model, X_test, Y_test, category_names):
    """
    Model is evaluated by this function
    Also classification report is printed
    
    """
    Y_pred = model.predict(X_test)
    ytest_df = pd.DataFrame(Y_pred,columns = Y_test.columns)                       
    for column in Y_test.columns:
        print(column,classification_report(Y_test[column],ytest_df[column]))# Printing classification report 
                            
def save_model(model, model_filepath):
    """
    Model is saved by taking 'model' and saving path as a arguments
    """
    pickle.dump(model,open(model_filepath,'wb'))
    

def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...') 
        
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        
        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)
        #model_report(model_filepath)

        print('Trained model saved!')
        

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()