import mlflow
import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_percentage_error,
    mean_absolute_error)

from category_encoders import TargetEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from utils import logger, load_data, upload_model_binary, download_model_binary
import pickle
import classes

    
    

def pf_basic_model_training(input: classes.FPTrainingInput, hashes: tuple):
    """
    Train a model to predict the price of a property given a set of 
    features downloaded from the property_friends dataset in S3.

    Args:
        input (FPTrainingInput): the input parameters for the training.
        hashes (tuple): the hashes of the run and execution.
    """
    try:

        mlflow.set_experiment(experiment_name="property_friends")
        mlflow.sklearn.autolog()

        train, test = (
            load_data(input.s3_bucket, input.training_data_path), 
            load_data(input.s3_bucket,input.test_data_path)
        )
        
        train_cols = [
            col for col in train.columns if col not in ['id', 'target']
            ]

        categorical_cols = ["type", "sector"]
        target           = "price"
        
        categorical_transformer = TargetEncoder()

        preprocessor = ColumnTransformer(
            transformers=[
                ('categorical',
                categorical_transformer,
                categorical_cols)
            ])

        steps = [
            ('preprocessor', preprocessor),
            ('model', GradientBoostingRegressor(**{
                "learning_rate":input.learning_rate,
                "n_estimators":input.n_estimators,
                "max_depth":input.max_depth,
                "loss":input.loss
            }))
        ]

        pipeline = Pipeline(steps)
        
        pipeline.fit(train[train_cols], train[target])
        
        test_predictions = pipeline.predict(test[train_cols])
        test_target = test[target].values
        
        logging_message = {
            "RMSE": np.sqrt(mean_squared_error(test_predictions, test_target)),
            "MAPE": mean_absolute_percentage_error(test_predictions, test_target),
            "MAE": mean_absolute_error(test_predictions, test_target)
        }

        model_binary = pickle.dumps(pipeline)
        
        upload_model_binary(
            input.s3_bucket, 
            f"models/property-friends-basic-model-{hashes[0]}.pkl", 
            model_binary)
        
    except Exception as e:
        logger.error(f"An error occurred while training the basic Property Friends model: {e}", run_hash=hashes[0], execution_hash=hashes[1])
    

    