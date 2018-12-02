import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource("sns")
    topic = sns.Topic('arn:aws:sns:us-east-1:502720765509:deployPortfolioTopic')

    location = {
        "bucketName": 'portfolio.build.mike',
        "objectKey": 'portfoliobuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")
        if (job):
            for artifact in job["data"]["inputArtifacts"]:
                localtion = artifact["location"]["s3Location"]

        print "Building portfolio from " + str(localtion)
        s3 = boto3.resource('s3')
        portfolio_bucket = s3.Bucket('portfolio.mike')
        build_bucket = s3.Bucket(location["bucketName"])
        
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location['objectKey'],portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                # Get content type guess
                content_type = mimetypes.guess_type(nm)[0]
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': content_type})
                print(nm, content_type)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        print('job done!')
        topic.publish(Subject="Portfolio Deployment", Message="Portfolio deployed successfully!")
        # tell codePipelien lambda completed successfully
        if job:
            codepipeline = boto3.client("codepipeline")
            codepipeline.put_job_success_result(jobId = job["id"]) 
    except:
        print('job failed due to an error!')
        topic.publish(Subject="Portfolio Failed", Message="Portfolio was not deployed successfully!")
        raise
        
    return "Hello from Lambda"
