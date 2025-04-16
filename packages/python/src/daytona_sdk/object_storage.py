import os
import hashlib
import tarfile
import boto3

class ObjectStorage:
    """
    A class to handle uploading files/folders to object storage (S3).
    Creates a tar archive of the file/folder and uploads it to the specified bucket.
    """
    
    def __init__(self, endpoint_url, aws_access_key_id, aws_secret_access_key, aws_session_token, 
                 bucket_name="daytona"):
        """
        Initialize the ObjectStorage with S3 connection parameters.
        
        Args:
            endpoint_url: The S3 endpoint URL
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_session_token: AWS session token
            bucket_name: S3 bucket name (defaults to "daytona")
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
    
    def upload(self, path, organization_id, arcname=None, delete_tar=True) -> str:
        """
        Upload a file or directory to S3.
        
        Args:
            path: Path to the file or directory to upload
            organization_id: Organization ID for the S3 prefix
            delete_tar: Whether to delete the local tar file after upload (default: True)
            
        Returns:
            dict: Upload result with keys:
                - uploaded: Whether the file was uploaded or skipped (existed)
                - path_hash: The MD5 hash of the path
                - s3_key: The S3 key where the file was uploaded
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        # Compute hash for the path
        path_hash = self._compute_hash_for_path_md5(path, arcname)
        
        # Define the S3 prefix
        prefix = f"{organization_id}/{path_hash}/"
        s3_key = prefix + "context.tar"
        
        # Check if it already exists in S3
        if self._folder_exists_in_s3(prefix):
            return path_hash
        
        # Create tar archive
        tar_file = self._create_tar_uncompressed(path, arcname, tar_path="context.tar")
        
        # Upload to S3
        self.s3_client.upload_file(tar_file, self.bucket_name, s3_key)
        
        # Delete tar file if requested
        if delete_tar:
            os.remove(tar_file)

        return path_hash

    def _compute_arcname(self, path_str):
        """Computes the arcname for the given path."""
        path_str = os.path.normpath(path_str)
        return path_str.lstrip('/')
    
    def _compute_hash_for_path_md5(self, path_str, arcname=None):
        """Recursively computes an MD5 hash of the path and contents."""
        md5_hasher = hashlib.md5()
        abs_path_str = os.path.abspath(path_str)
        
        if arcname is None:
            arcname = self._compute_arcname(path_str)
        md5_hasher.update(arcname.encode("utf-8"))
        
        if os.path.isfile(abs_path_str):
            with open(abs_path_str, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    md5_hasher.update(chunk)
        else:
            for root, dirs, files in os.walk(abs_path_str):
                if not dirs and not files:
                    rel_dir = os.path.relpath(root, path_str)
                    md5_hasher.update(rel_dir.encode("utf-8"))
                for filename in files:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, abs_path_str)
                    
                    # Incorporate the relative path
                    md5_hasher.update(rel_path.encode("utf-8"))
                    
                    # Incorporate file contents
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(8192), b""):
                            md5_hasher.update(chunk)
        
        return md5_hasher.hexdigest()
    
    def _folder_exists_in_s3(self, prefix):
        """Returns True if there's at least one object with the given prefix in S3."""
        resp = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return 'Contents' in resp
    
    def _create_tar_uncompressed(self, source_path, arcname=None, tar_path="context.tar"):
        """Create an uncompressed tar archive from source_path."""
        source_path = os.path.normpath(source_path)
        
        if arcname is None:
            arcname = self._compute_arcname(source_path)
        
        with tarfile.open(tar_path, mode="w") as tar:
            tar.add(source_path, arcname)
        return tar_path