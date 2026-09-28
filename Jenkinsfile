pipeline {

    agent any

    environment {
        AWS_REGION = 'ap-south-2'
        ECR_REPO = 'jenkins-devops-demo'
        IMAGE_TAG = "${BUILD_NUMBER}"
        APP_INSTANCE_ID = 'i-079954e229ad4f0ba'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest
                    pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                    -t $ECR_REPO:$IMAGE_TAG .
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                    AWS_ACCOUNT_ID=$(aws sts get-caller-identity \
                    --query Account \
                    --output text)

                    aws ecr get-login-password \
                    --region $AWS_REGION | \
                    docker login \
                    --username AWS \
                    --password-stdin \
                    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                '''
            }
        }

        stage('Push Image to ECR') {
            steps {
                sh '''
                    AWS_ACCOUNT_ID=$(aws sts get-caller-identity \
                    --query Account \
                    --output text)

                    docker tag \
                    $ECR_REPO:$IMAGE_TAG \
                    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG

                    docker push \
                    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                sh '''
                    AWS_ACCOUNT_ID=$(aws sts get-caller-identity \
                    --query Account \
                    --output text)

                    IMAGE_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG

                    COMMAND_ID=$(aws ssm send-command \
                    --region $AWS_REGION \
                    --instance-ids $APP_INSTANCE_ID \
                    --document-name "AWS-RunShellScript" \
                    --parameters commands="[
                      \\"aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com\\",
                      \\"docker pull $IMAGE_URI\\",
                      \\"docker stop jenkins-demo || true\\",
                      \\"docker rm jenkins-demo || true\\",
                      \\"docker run -d --name jenkins-demo -p 80:5000 $IMAGE_URI\\"
                    ]" \
                    --query "Command.CommandId" \
                    --output text)

                    echo "SSM Command ID: $COMMAND_ID"

                    aws ssm wait command-executed \
                    --region $AWS_REGION \
                    --command-id $COMMAND_ID \
                    --instance-id $APP_INSTANCE_ID

                    aws ssm get-command-invocation \
                    --region $AWS_REGION \
                    --command-id $COMMAND_ID \
                    --instance-id $APP_INSTANCE_ID
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }

        failure {
            echo 'Pipeline failed.'
        }
    }
}
