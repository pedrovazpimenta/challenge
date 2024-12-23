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

With that done, the user can access the FastAPI server at `http://localhost:8000/docs` (together with a detailed documentation of the endpoints) and the MLFlow server at `http://localhost:5000`.
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
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzM0OTI0NDIzfQ.z3ZbuQEbYQV-UK7QST0MKssgZlYJXZB4tNQymWkTow4"
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

## Further remarks and improvements

The project is a simple implementation of the requirements. Some improvements can be made, such as:
- A CI/CD pipeline to automate the deployment process.
- Connecting the logger with a database and monitoring system (for example, OpenSearch or BigQuery).
- Unittests for the FastAPI server (triggered in the CI/CD pipeline with coverage check).
- Automated checks for linting, code quality and security (can be done with the CI/CD pipeline).
- Terraform scripts (or other IaC) for the infrastructure setup.
- Better model training in general: automated model selection, hyperparameter tuning, feature engineering, etc.
- Using a real database for the users and their credentials, and a function to renew the access token automatically, or;
- Instead of in app authentication, in the deploy to the cloud, use a restricted VPC and a VPN to access the API, running it in a private subnet in isolation and leaving the authentication to the cloud provider if necessary, reducing the attack surface and application overhead, as we want to provide inferences as fast as possible.

As a final remark, there is a structure for future connection directly with the client's database, as required. One can use the `app/utils/db_connection.py` module to connect to the database and use its functions to retrieve the data and make a batch prediction and then store the result into the `price` column. It was made this way as it would be very easy to reuse the model inference functions and create a new endpoint to trigger the process. The same can be made for the training process, as a similar function can be written to retrieve the data from the database, split and train the model. The only thing that needs to be done is to create a new endpoint in the FastAPI server to trigger the process.