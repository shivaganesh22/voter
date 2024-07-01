from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CSVFile
from .serializers import *
import pandas as pd

class FileUpload(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Extract check1 and check2 from the request data

        # Log or process check1 and check2 as needed
        data={}
        # Validate and save the CSV file data
        file_serializer = CSVFileSerializer(data=request.data)
        data_serializer=CollectionSerializer(data=request.data)
        if file_serializer.is_valid() and data_serializer.is_valid():
            csv_file_instance = file_serializer.save()
            # Return the ID of the newly created object
            try:
                df=pd.read_csv(csv_file_instance.csv_file.path)
                if data_serializer.data["check1"]:
                    data["head"]=df.head().to_dict()
                if data_serializer.data["check2"]:
                    data["shape"]=df.shape
                if data_serializer.data["check3"]:
                    data["types"]=df.dtypes.apply(lambda x: x.name).to_dict()
                if data_serializer.data["check4"]:
                    print(df.info())
                    data["info"]=df.info()
                if data_serializer.data["check5"]:
                    data["null_sum"]= df.isnull().sum().to_dict()
                if data_serializer.data["check6"]:
                    data["summary"]=df.describe().to_dict()
                data["id"]=csv_file_instance.id
                return Response(data)
            except Exception as e:
                print(e)
                return Response({"error":"Failed to load data"},status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response({"error":"Invalid request"},status=status.HTTP_400_BAD_REQUEST)
from sklearn.preprocessing import StandardScaler
class PreprocessingView(APIView):
    def post(self,request):
        serializer=PreprocessingSerializer(data=request.data)
        data={}
        if serializer.is_valid():
            try:
                df=pd.read_csv(CSVFile.objects.get(id=serializer.data["id"]).csv_file.path)
                if serializer.data["check1"]:
                    df.drop_duplicates(inplace=True)
                if serializer.data["check2"]:
                    non_numeric_cols = df.select_dtypes(include=['object']).columns
                    if len(non_numeric_cols) > 0:
                        df = df.drop(non_numeric_cols, axis=1)
                    df.fillna(df.mean(), inplace=True)
                if serializer.data["check3"]:
                    df = pd.get_dummies(df)
                if serializer.data["check4"]:
                    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
                    df[numerical_cols] = (df[numerical_cols] - df[numerical_cols].min()) / (df[numerical_cols].max() - df[numerical_cols].min())
                if serializer.data["check5"]:
                    scaler = StandardScaler()
                    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
                return Response(df)
            except:
                return Response({"error":"Failed to load data"},status=status.HTTP_400_BAD_REQUEST)

        return Response({"error":"Invalid request"},status=status.HTTP_400_BAD_REQUEST)
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
class ExplorationView(APIView):
    def post(self,request):
        images = {}
        serializer=ExplorationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                df=pd.DataFrame(serializer.data["csv"])
                if serializer.data["check1"]:
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
                    plt.title('Correlation Matrix Heatmap')
                    img = io.BytesIO()
                    plt.savefig(img, format='png')
                    plt.close()
                    img.seek(0)
                    images['correlation_matrix'] = base64.b64encode(img.read()).decode('utf-8')
                if serializer.data["check2"]:
                    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
                    df[numerical_cols].hist(bins=20, figsize=(12, 10))
                    plt.suptitle('Distribution of Numerical Features', y=1.02)
                    img = io.BytesIO()
                    plt.savefig(img, format='png')
                    plt.close()
                    img.seek(0)
                    images['numerical_distribution'] = base64.b64encode(img.read()).decode('utf-8')
                if serializer.data["check3"]:
                    categorical_cols = df.select_dtypes(include=['object']).columns
                    for col in categorical_cols:
                        plt.figure(figsize=(8, 6))
                        sns.countplot(x=col, data=df)
                        plt.title(f'Count Plot for {col}')
                        plt.xticks(rotation=45)
                        img = io.BytesIO()
                        plt.savefig(img, format='png')
                        plt.close()
                        img.seek(0)
                        images[f'count_plot_{col}'] = base64.b64encode(img.read()).decode('utf-8')
                if serializer.data["check4"]:
                    sns.pairplot(df[numerical_cols])
                    plt.suptitle('Pairplot for Numerical Features', y=1.02)
                    img = io.BytesIO()
                    plt.savefig(img, format='png')
                    plt.close()
                    img.seek(0)
                    images['pairplot'] = base64.b64encode(img.read()).decode('utf-8')
                if serializer.data["check5"]:
                    plt.figure(figsize=(12, 8))
                    sns.boxplot(data=df[numerical_cols])
                    plt.title('Boxplot for Numerical Features')
                    plt.xticks(rotation=45)
                    img = io.BytesIO()
                    plt.savefig(img, format='png')
                    plt.close()
                    img.seek(0)
                    images['boxplot'] = base64.b64encode(img.read()).decode('utf-8')
                images["csv"]=df
                return Response(images)
            except Exception as e:
                print(e)
                return Response({"error":"Failed to load data"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"error":"Invalid Request"},status=status.HTTP_400_BAD_REQUEST)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
class DataPreprocessingView(APIView):
    def post(self,request):
        data = {}
        serializer=DataPreprocessingSerializer(data=request.data)
        if serializer.is_valid():
            try:
                df=pd.DataFrame(serializer.data["csv"])
                X = df.drop(df.columns[-1], axis=1)
                y = df[df.columns[-1]]

                # Check the type of the target variable
                target_type = 'classification' if len(y.unique()) <= 10 else 'regression'

                # if target_type != 'classification':
                #     raise ValueError("The target variable is not suitable for classification.")

                # Convert target variable to integer (for classification)
                y = y.astype(int)
                fig, ax = plt.subplots(1, 2, figsize=(12, 6))

                # Step 4: Fit KNN classifier
                knn = KNeighborsClassifier(n_neighbors=5)
                # return X_train, X_test, y_train, y_test, X_under_train, X_under_test, y_under_train, y_under_test, X_over_train, X_over_test, y_over_train, y_over_test

                if serializer.data["check1"]:
                    # Visualize the original class distribution
                    sns.countplot(y)
                    plt.title('Original Class Distribution')
                    img = io.BytesIO()
                    plt.savefig(img, format='png')
                    plt.close()
                    img.seek(0)
                    data['image1'] = base64.b64encode(img.read()).decode('utf-8')
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    # Original dataset
                    knn.fit(X_train, y_train)
                    y_pred = knn.predict(X_test)
                    data["original_report"]=classification_report(y_test, y_pred)
                    data["original_accuracy"]=accuracy_score(y_test, y_pred)
                if serializer.data["check2"]:
                    # Step 2: Resample the dataset
                    # Undersample the majority class
                    undersampler = RandomUnderSampler(sampling_strategy='auto', random_state=42)
                    X_under, y_under = undersampler.fit_resample(X, y)
                    sns.countplot(y_under, ax=ax[0])
                    ax[0].set_title('Undersampled Class Distribution')
                    X_under_train, X_under_test, y_under_train, y_under_test = train_test_split(X_under, y_under, test_size=0.2, random_state=42)
                    # Undersampled dataset
                    knn.fit(X_under_train, y_under_train)
                    y_under_pred = knn.predict(X_under_test)
                    data["under_report"]=classification_report(y_under_test, y_under_pred)
                    data["under_accuracy"]=accuracy_score(y_under_test, y_under_pred)
                    
                if serializer.data["check3"]:
                    # Oversample the minority class
                    oversampler = SMOTE(sampling_strategy='auto', random_state=42)
                    X_over, y_over = oversampler.fit_resample(X, y)
                    sns.countplot(y_over, ax=ax[1])
                    ax[1].set_title('Oversampled Class Distribution')
                    X_over_train, X_over_test, y_over_train, y_over_test = train_test_split(X_over, y_over, test_size=0.2, random_state=42)
                    # Oversampled dataset
                    knn.fit(X_over_train, y_over_train)
                    y_over_pred = knn.predict(X_over_test)
                    data["over_report"]=classification_report(y_over_test, y_over_pred)
                    data["over_accuracy"]=accuracy_score(y_over_test, y_over_pred)
                img = io.BytesIO()
                plt.savefig(img, format='png')
                plt.close()
                img.seek(0)
                data['image2'] = base64.b64encode(img.read()).decode('utf-8')
                data["csv"]=df
                return Response(data)
            except Exception as e:
                print(e)
                return Response({"error":"Failed to load data"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"error":"Invalid Request"},status=status.HTTP_400_BAD_REQUEST)
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.metrics import mean_squared_error
class TimeSeriesAnalysis(APIView):
    def post(self, request):
        data = {}
        serializer = ExplorationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                df = pd.DataFrame(serializer.data["csv"])
                X = df.drop(df.columns[-1], axis=1)
                y = df[df.columns[-1]]
                y = y.astype(int)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                target_column_name = df.columns[-1]  # Assuming target column is the last column

                if serializer.data["check1"]:
                    model = SARIMAX(df[target_column_name], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
                    results = model.fit()

                    # Make predictions
                    forecast = results.get_forecast(steps=10)
                    data["sarimax"] = {
                        "summary": results.summary().as_text(),  # Convert to string
                        "forecast": forecast.predicted_mean.tolist()  # Convert forecast to list
                    }

                if serializer.data["check2"]:
                    def create_lstm_model():
                        model = Sequential()
                        model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
                        model.add(LSTM(units=50))
                        model.add(Dense(units=1))
                        model.compile(optimizer='adam', loss='mean_squared_error')
                        return model

                    model = create_lstm_model()
                    model.fit(X_train, y_train, epochs=100, batch_size=32)

                    # Make predictions
                    y_pred = model.predict(X_test)
                    mse = mean_squared_error(y_test, y_pred)

                    data["lstm"] = {"mse": mse}

                if serializer.data["check3"]:
                    model = ARIMA(df[target_column_name], order=(5, 1, 0))
                    results = model.fit()

                    # Make predictions
                    forecast = results.forecast(steps=10)
                    data["arima"] = {
                        "summary": results.summary().as_text(),  # Convert to string
                        "forecast": forecast.tolist()  # Convert forecast to list
                    }

                if serializer.data["check4"]:
                    model = ExponentialSmoothing(df[target_column_name])
                    results = model.fit()

                    # Make predictions
                    forecast = results.forecast(steps=10)
                    data["exponential_smoothing"] = {
                        "summary": results.summary().as_text(),  # Convert to string
                        "forecast": forecast.tolist()  # Convert forecast to list
                    }

                if serializer.data["check5"]:
                    train_size = int(len(df) * 0.8)
                    train, test = df.iloc[:train_size], df.iloc[train_size:]

                    # Seasonal naive forecasting
                    # Repeat the last observed value for each season
                    seasonal_naive_forecast = train[target_column_name].iloc[-1]

                    # Evaluate forecast
                    forecast_values = [seasonal_naive_forecast] * len(test)

                    # Calculate Mean Squared Error
                    mse = mean_squared_error(test[target_column_name], forecast_values)

                    plt.figure(figsize=(10, 6))
                    plt.plot(train.index, train[target_column_name], label='Training Data')
                    plt.plot(test.index, test[target_column_name], label='Test Data')
                    plt.plot(test.index, forecast_values, label='Seasonal Naive Forecast', linestyle='--', color='red')
                    plt.xlabel('Date')
                    plt.ylabel('Value')
                    plt.title('Seasonal Naive Forecasting')
                    plt.legend()
                    img = io.BytesIO()
                    plt.savefig(img, format='png')
                    plt.close()
                    img.seek(0)
                    data["forecasting"] = {
                        "mse": mse,
                        "image": base64.b64encode(img.read()).decode('utf-8')
                    }

                data["csv"] = df.to_dict()  # Convert DataFrame to dictionary for serialization
                return Response(data)
            except Exception as e:
                print(e)
                return Response({"error": "Failed to load data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Invalid Request", "k": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)