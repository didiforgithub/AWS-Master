import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir


def up_load_s3(file_path):
    s3 = boto3.resource('s3')
    bucket_name = 'aigc-bj-team4'
    s3.Bucket(bucket_name).upload_file(file_path, file_path)
    # Generate a pre-signed URL for the objecct "welcome.txt", valid for 1 hour
    url = s3.meta.client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': file_path
        },
        ExpiresIn=3600
    )
    # Print out the URL
    print(f"upload file {file_path} to s3, URL: {url}")
    return url

def text_to_speech(input_text, voice_id="Joanna"):
    bucket_name = 'aigc-bj-team4'
    polly_client = boto3.client('polly')
    #s3_client = boto3.client("s3")
    
    try:
        # Request speech synthesis
        response = polly_client.synthesize_speech(Text=input_text, OutputFormat="mp3",
                                            VoiceId=voice_id)
        print(response)
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)
    
    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            output = os.path.join(gettempdir(), "speech.mp3")

            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
                    print("Written to %s" % output)
                    #s3_client.upload_file(output, bucket_name, "speech.mp3")
                    url = up_load_s3(output)
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
    
    # Return the URL of the mp3 file stored in S3
    print("audio的网页URL:"+url)
    return url
