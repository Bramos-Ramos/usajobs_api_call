# USAJOBS Data Pipeline
This project reads data from the USAJOBS API, persists that data into an RDS PostgreSQL database, and deploys the data pipeline using Docker and Terraform.

## Requirements
Before running this project, you'll need the following:

* Python 3
* Docker
* Terraform

You'll also need to set up an AWS account and an IAM user with permissions to create and manage the infrastructure resources required by this project.

## Tasman

For this case specifically, I created a RDS PostgreSQL instance wich I sent the credentials by email earlier on.

Also I created a IAM user so you can check the whole infrastructure.

## API Call

For this project I created a python file which extracts data related to the keyword "data engineering" as requested per the test.

Coming from the API, I assured that the table would be created directly from the python script and ensure there would be no duplicates by creating a surrogate key hashing the columns coming from the API.

## Docker

With the API call script complete, I created a dockerfile with the instructions and requirements for that script to be run and added the environment variables needed to run it.

These variables being:

* ENV DB_HOST=<db-host>
* ENV DB_NAME=<db-name>
* ENV DB_USER=<db-user>
* ENV DB_PASSWORD=<db-password>
* ENV API_KEY=<api-key>
* ENV API_EMAIL=<api-email>

With the last 2 being the information sent by email making the API call possible.

So please ensure to run the command docker build with the variables added to it as in:
```
$ docker build --build-arg DB_HOST="" --build-arg DB_NAME="" --build-arg DB_USER="" --build-arg DB_PASSWORD="" --build-arg API_KEY="" --build-arg API_EMAIL="" -t tasman-test  .
```

## ECR

Having the docker image, make sure to push it to the following public repository by tagging and pushing it as follows:
```
$ docker tag tasman-test:latest public.ecr.aws/n9v1m6p2/tasman-test:latest
```
```
$ docker push public.ecr.aws/n9v1m6p2/tasman-test:latest
```

## Terraform + ECS + Schedulling

Now that you have the Docker image in the public repository, all you need to is run the terraform code which will create a budget to be sure it won't create expenses over 10 USD, create the ECS task, service, and cluster.

After that it will also create the job rule and job target in CloudWatch to be sure it's scheduled to run every 5 minutes. Use the monitoring part to make sure it's properly running.

To run the terraform app you can use:
```
terraform init

terraform plan

terraform apply
```
Which will make sure everything is created and runs properly.

## Next Steps

Having it all running smoothly, the next steps would be to create a CI/CD Pipeline, probably using CodeCommit, CodeBuild, CodeDeploy and CodePipeline in AWS to be sure that every new commit would go through building and testing phases while making sure everything runs automatically.

