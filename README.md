# Challenge resolution: Backend API for inference and model training

## Setup

The Project can be setup either using DevContainer or simple Docker setup. The DevContainer is recommended as it has all the necessary dependencies and configurations, but requires Visual Studio Code and DevContainer Extension installed, together with Docker. The Docker setup is more manual and requires the user to have Docker installed. The first one is simple and only requires the user to open the project in Visual Studio Code and click on the "Reopen in Container" button. The second one requires the user to run the following commands:

```bash
docker-compode up
```

This will setup the following containers:
- mlflow: container with the MLFlow server
- model-api: container with the FastAPI server
- mlflow_db: a MySQL server for MLFlow
- s3: a MinIO server for S3 storage (only for development)

After that, the user needs to upload the datasets to the S3 bucket. The bucket name is "mlflow" and the datasets should be uploaded to the "dataset" folder. The datasets should be in CSV format and have the following columns:

```python
['type', 'sector', 'net_usable_area', 'net_area', 'n_rooms',
       'n_bathroom', 'latitude', 'longitude', 'price']
```

With that done, the user can access the FastAPI server at http://localhost:8000/docs (together with a detailed documentation) and the MLFlow server at http://localhost:5000.
The first step is to get a token from the FastAPI server. This token is necessary to access any of the API's endpoint. To get the token, use the following endpoint:

```json
{
  "username": "johndoe",
  "password": "password1234"
}
```

The token will be returned in the response body and can be used, together with the `username`, to authenticate, as the following example in the `authentication` field:

```json
{
  "username": "johndoe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzM0OTIxMDAxfQ.IyRSmEr8XvV4Mij2lXuueqdILWLmIhFzIoWYh46wtdo"
} 

```

It lasts for 30 minutes, after that, it needs to be renewed.

With the token, the user can then train a model using the endpoint `train_fp_basic_model` with this example body:

```json
{
  "training_data_path": "dataset/train.csv",
  "test_data_path": "dataset/test.csv",
  "s3_bucket": "mlflow",
  "learning_rate": 0.01,
  "n_estimators": 300,
  "max_depth": 5,
  "loss": "absolute_error"
}
 ```

This will generate a new model and store it in the MLFlow server and the `s3` bucket. The user can then use the endpoint `batch_inference_fp_basic_model` to make predictions using the model when the input is a csv file. The body should be like this:

```json
{
  "s3_bucket": "mlflow",
  "data_path": "dataset/test.csv",
  "fp_model_path": "models/property-friends-basic-model-16b48ff485632e764e55c9bdd53ce1aa.pkl"
}
```

Finally, the user has the possibility of doing a single inference using the endpoint `single_inference_fp_basic_model` with the following body:

```json
{
  "s3_bucket": "mlflow",
  "fp_model_path": "models/property-friends-basic-model-16b48ff485632e764e55c9bdd53ce1aa.pkl",
  "input": {
    "type": "casa",
    "sector": "lo barnechea",
    "net_usable_area": 425.0,
    "net_area": 1000.0,
    "n_rooms": 5.0,
    "n_bathroom": 3.0,
    "latitude": -33.52346,
    "longitude": -70.64667
  }
}
```