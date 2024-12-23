# Challenge resolution: Backend API for inference and model training

## Local setup and usage

The Project can be setup either using DevContainer or a simple Docker setup. The DevContainer is recommended as it has all the necessary dependencies and configurations, but requires Visual Studio Code and DevContainer Extension installed, together with Docker. The Docker setup is more manual and requires the user to have Docker installed.

Please note that the user needs to set up the `.env` file in the root folter following the template in `.env.template`. The only requirement is that the value in `SECRET_KEY` should be a `HEX32` string. The user can generate one using the following command:

```bash
openssl rand -hex 32
```

 Then, the first setup is simple and only requires the user to open the project in Visual Studio Code and click on the "Reopen in Container" button. After that, typing the following command in the terminal:

```bash
uvicorn main:app --host=0.0.0.0 --port=8000 --log-config=log_conf.yaml
```
 
The second setup only requires the user to run the following command:

```bash
docker-compode up
```

This will setup the following containers:
- mlflow: container with the MLFlow server
- model-api: container with the FastAPI server
- mlflow_db: a MySQL server for MLFlow
- s3: a MinIO server for S3 storage (only for development)

After that, the user needs to upload the datasets to the S3. This can be done in the address `http://localhost:9001/`, the bucket name is `mlflow` and the datasets should be uploaded to the `dataset` folder. The datasets should be in `CSV` format and have the following columns:

```python
['type', 'sector', 'net_usable_area', 'net_area', 'n_rooms',
       'n_bathroom', 'latitude', 'longitude', 'price']
```

With that done, the user can access the FastAPI server at `http://localhost:8000/docs` (together with a detailed documentation of the endpoints, that can be used with the `Try it out` option) and the MLFlow server at `http://localhost:5000`.
The first step is to get a token from the FastAPI server. This token is necessary to access any of the API's endpoint. To get the token, use the following endpoint `http://localhost:8000/token` with the payload:

```json
{
  "username": "johndoe",
  "password": "password1234"
}
```

In CURL, it would be like this:

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=johndoe&password=password1234&scope=&client_id=&client_secret='
```

The token will be returned in the response body, as in the example:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzM0OTUxODIwfQ.-QnrzF6g6juHdTcQyAXgMRmqsfrituJeiskUQEBgJZk",
  "token_type": "bearer"
}
```

And can be used to authenticate the requiest in the `token` field. It lasts for 30 minutes, after that, it needs to be renewed.

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

 
In CURL, it would be like this:

```bash
curl -X 'POST' \
  'http://localhost:8000/train_fp_basic_model?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzM0OTU2Njg1fQ.jJSNImiBrbDrK_4uU_UWLEpScQVmugK0qxrWnV3lJaY' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "training_data_path": "dataset/train.csv",
  "test_data_path": "dataset/test.csv",
  "s3_bucket": "mlflow",
  "learning_rate": 0.01,
  "n_estimators": 300,
  "max_depth": 5,
  "loss": "absolute_error"
}'
```

 Returning the following response:

 ```json
{
  "status": "success",
  "model": "models/property-friends-basic-model-8d36f60c5a98135d474f8629e5bc7430.pkl"
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

In CURL, it would be like this:

```bash
curl -X 'POST' \
  'http://localhost:8000/batch_inference_fp_basic_model?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzM0OTU2Njg1fQ.jJSNImiBrbDrK_4uU_UWLEpScQVmugK0qxrWnV3lJaY' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "s3_bucket": "mlflow",
  "data_path": "dataset/test.csv",
  "fp_model_path": "models/property-friends-basic-model-16b48ff485632e764e55c9bdd53ce1aa.pkl"
}'
```


And here is the response:

```json
{
  "model": "models/property-friends-basic-model-16b48ff485632e764e55c9bdd53ce1aa.pkl",
  "input_data": "dataset/test.csv",
  "time": 0.24775906899594702,
  "predictions": [
    21534.111506322784,
    10450.683126723623,
    7935.396291542173,
    7424.731251658449,
    13070.575463557223,
  ]
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


In CURL, it would be like this:

```bash
curl -X 'POST' \
  'http://localhost:8000/single_inference_fp_basic_model?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzM0OTU2NDE5fQ.Ne_5N7nkRkQ1L2mmEYqObVKmc4GeS-sLJGyLPjOkhco' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
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
}'
```

Getting the following response:

```json
{
    "model": "models/property-friends-basic-model-16b48ff485632e764e55c9bdd53ce1aa.pkl",
    "input_data": {
        "type": "casa",
        "sector": "lo barnechea",
        "net_usable_area": 425.0,
        "net_area": 1000.0,
        "n_rooms": 5.0,
        "n_bathroom": 3.0,
        "latitude": -33.52346,
        "longitude": -70.64667,
        "price": 0.0
    },
    "time": 0.03163227899494814,
    "prediction": 24386.988824108925
}
```

## Further remarks and improvements

The project is a simple implementation of the requirements. Some improvements can be made, such as:
- A CI/CD pipeline to automate the deployment process.
- Connecting the logger with a database and monitoring system (for example, OpenSearch or BigQuery).
- Unittests for the FastAPI server (triggered in the CI/CD pipeline with coverage check).
- Automated checks for linting, code quality and security (can be done with the CI/CD pipeline).
- Terraform scripts (or other IaC) for the infrastructure setup.
- Better model training in general: automated model selection, hyperparameter tuning, feature engineering, etc. Also, this training can be done in a separate container, using serverless functions, or even cloud specific servricess made for that, as it can be very resource-intensive to be done in the same environment as inference.
- Using a real database for the users and their credentials, and a function to renew the access token automatically, or;
- Instead of in app authentication, in the deploy to the cloud, use a restricted VPC and a VPN to access the API, running it in a private subnet in isolation and leaving the authentication to the cloud provider if necessary, reducing the attack surface and application overhead, as we want to provide inferences as fast as possible.

As a final remark, there is a structure for future connection directly with the client's database, as required. One can use the `app/utils/db_connection.py` module to connect to the database and use its functions to retrieve the data and make a batch prediction and then store the result into the `price` column. It was made this way as it would be very easy to reuse the model inference functions and create a new endpoint to trigger the process. The same can be made for the training process, as a similar function can be written to retrieve the data from the database, split and train the model. The only thing that needs to be done is to create a new endpoint in the FastAPI server to trigger the process.