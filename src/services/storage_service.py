class StorageService:
    def __init__(self, storage_client):
        self.storage_client = storage_client

    def upload_file(self, file, bucket_name, object_name):
        """
        Uploads a file to the specified S3-compatible storage bucket.

        :param file: The file to upload.
        :param bucket_name: The name of the bucket to upload to.
        :param object_name: The name of the object in the bucket.
        :return: The URL of the uploaded file.
        """
        try:
            self.storage_client.upload_file(file, bucket_name, object_name)
            return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def download_file(self, bucket_name, object_name, download_path):
        """
        Downloads a file from the specified S3-compatible storage bucket.

        :param bucket_name: The name of the bucket to download from.
        :param object_name: The name of the object in the bucket.
        :param download_path: The local path to save the downloaded file.
        """
        try:
            self.storage_client.download_file(bucket_name, object_name, download_path)
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")