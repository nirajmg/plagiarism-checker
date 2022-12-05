from datetime import timedelta

from minio import Minio

client = Minio(
    "play.min.io",
    access_key="GOOGWLIHZ3WKSUWBGHAUTBX5",
    secret_key="489mKcdB7Gp/wdOqChRvLV+AS0y3RO8eA6Q4/Zqu",
)

# Get presigned URL string to upload data to 'my-object' in
# 'my-bucket' with default expiry (i.e. 7 days).
url = client.presigned_put_object("plagiarism-bucket", "user/files/test",expires=timedelta(hours=2))
print(url)


print(url)