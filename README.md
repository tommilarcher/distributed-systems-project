Description:

The fbprophet library was too big to use it in a lambda function, therefore we had to install it to a EFS filesystem and mounted the filesystem in the lambda functions. We added sys.path.append("/mnt/lambda") inside the lambda code to tell python where to look for the library. To install fbprophet to the filesystem, we used an ec2 instance. 

To execute the workflow run... 
java -jar xAFCL.jar StockPrediction.yaml input.json
...inside the Workflow folder.