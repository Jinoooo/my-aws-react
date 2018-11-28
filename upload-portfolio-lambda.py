import boto3
import StringIO
import zipfile
import mimetypes

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