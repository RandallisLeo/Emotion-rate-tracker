import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from joblib import dump


data = pd.read_csv(r"C:\Users\randall\Desktop\heart rate data\数据处理\heart_rate_emotion_dataset-Kmean+knn.csv")


scaler = StandardScaler()
data['HeartRate'] = scaler.fit_transform(data[['HeartRate']])


X_train, X_test, y_train, y_test = train_test_split(data[['HeartRate']], data['Emotion'], test_size=0.2)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)


emotion_mapping = {
    1: 'sad',
    2: 'neutral',
    3: 'happy',
    4: 'angry',
    5: 'fear',
    6: 'surprise',
    7: 'disgust'
}


def predict_emotion(heart_rate_value):
    standardized_value = scaler.transform([[heart_rate_value]])
    emotion_number = knn.predict(standardized_value)[0]
    emotion_label = emotion_mapping[emotion_number]  
    return emotion_label


new_heart_rate = 100  
predicted_emotion = predict_emotion(new_heart_rate)
print(f"The predicted emotion for heart rate {new_heart_rate} is: {predicted_emotion}")


dump(scaler, 'scaler-1103.joblib') 
dump(knn, 'knn-1103.joblib')
