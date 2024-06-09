try:
    import json
    import sys
    import requests
    import boto3
    import os
    import uuid
    from urllib.parse import unquote_plus
    from shutil import copy
    print("All imports ok ...")
except Exception as e:
    print("Error Imports : {} ".format(e))

s3_client = boto3.client('s3')


def lambda_handler(event, context):
  for record in event['Records']:
      bucket = record['s3']['bucket']['name']

      # local test with lambda runtime with  dummy test evet without S3 interaction
      if bucket =='test':
          copy('./testbook.epub', '/tmp/testbook.epub')
          os.system('pandoc /tmp/testbook.epub -o /tmp/testbook.pdf --pdf-engine=lualatex')
          valid_path_test = os.path.exists('/tmp/testbook.pdf')
          if valid_path_test:
              print ('test conversion succeded!')
              os.remove('/tmp/testbook.epub')
          else:
              print('test conversion failed!')
              os.remove('/tmp/testbook.epub')


      # actuc conversion with S3 interaction
      else:
          key = unquote_plus(record['s3']['object']['key'])
          tmpkey = key.replace('/', '')
          download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
          print(download_path)
          conversion_path = '/tmp/converted-{}'.format(tmpkey) + '.docx'
          upload_path = '/tmp/converted-{}'.format(tmpkey) + '.pdf'
          s3_client.download_file(bucket, key, download_path)
          print('download succeded!')
          os.system('pandoc ' + download_path + ' -o ' + conversion_path)
          os.system('pandoc '+conversion_path+' -o '+upload_path+' --pdf-engine=lualatex')
          valid_path_test = os.path.exists(upload_path)

          if valid_path_test:
              print('conversion succeeded')
              try:
                  s3_client.upload_file(upload_path, '{}-converted'.format(bucket), key + '.pdf')
              except Exception as e:
                  print("Error uploading : {} ".format(e))

              os.remove(download_path)
              os.remove(upload_path)
              os.remove(conversion_path)

          else:
              print('conversion failed')
              os.remove(download_path)







