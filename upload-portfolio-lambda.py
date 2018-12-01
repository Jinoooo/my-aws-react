import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):


    sns = boto3.resource("sns")
    topic = sns.Topic('arn:aws:sns:us-east-1:502720765509:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3')
        portfolio_bucket = s3.Bucket('portfolio.mike')
        build_bucket = s3.Bucket('portfolio.build.mike')
        
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)
        
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
    except:
        print('job failed due to an error!')
        topic.publish(Subject="Portfolio Failed", Message="Portfolio was not deployed successfully!")
        raise
        
    return "Hello from Lambda"
