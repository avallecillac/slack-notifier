FunctionExists=$(aws lambda list-functions --region $AWS_DEFAULT_REGION | jq -r '.' | grep -sw $FUNCTION_NAME)
if [[ -n $FunctionExists ]]; then
  echo "Updating function $FUNCTION_NAME"
  echo aws lambda update-function-code --function-name $FUNCTION_NAME --s3-bucket $ARTIFACTS_S3_BUCKET --s3-key $ARTIFACTS_S3_PATH/lambda.zip --region $AWS_DEFAULT_REGION
  aws lambda update-function-code --function-name $FUNCTION_NAME --s3-bucket $ARTIFACTS_S3_BUCKET --s3-key $ARTIFACTS_S3_PATH/lambda.zip --region $AWS_DEFAULT_REGION
else
  echo "Function $FUNCTION_NAME does not exist, no update was triggered"
  exit 0
fi
