import io
from ast import List

from minio import Minio
from minio.error import S3Error

from config import minio_settings


class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=minio_settings.MINIO_ENDPOINT,
            access_key=minio_settings.MINIO_ACCESS_KEY,
            secret_key=minio_settings.MINIO_SECRET_KEY,
            secure=minio_settings.MINIO_SECURE,
        )
        self.project_bucket = minio_settings.MINIO_PROJECT_BUCKET
        self.template_bucket = minio_settings.MINIO_TEMPLATE_BUCKET

    def _ensure_bucket(self, bucket: str) -> None:
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    def get_file_tree(self, project_id: str) -> str:
        self._ensure_bucket(self.project_bucket)

        prefix = f"{project_id}/"
        objects = self.client.list_objects(
            self.project_bucket, prefix=prefix, recursive=True
        )
        paths = []
        for obj in objects:
            relative_path = obj.object_name.removeprefix(prefix)
            if relative_path:
                paths.append(relative_path)

        if not paths:
            return "(empty object)"

        return self._build_tree_string(sorted(paths))

    def _build_tree_string(self, paths: List[str]) -> str:
        tree: dict = {}

        for path in paths:
            parts = path.split("/")
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]

        lines: List[str] = []
        self._format_tree(tree, lines, indent=0)
        return "\n".join(lines)

    def _format_tree(self, tree: dict, lines: List[str], indent: int) -> None:
        for name, children in tree.items():
            prefix = " " * indent
            if children:
                lines.append(f"{prefix}{name}/")
                self._format_tree(children, lines, indent + 1)
            else:
                lines.append(f"{prefix}{name}/")

    def read_file(self, project_id: str, path: str) -> str:
        """
        Read a single file's content from MinIO.

        The full object key is: {project_id}/{path}
        For example: "abc-123/src/App.tsx"
        """
        self._ensure_bucket(self.project_bucket)

        object_name = f"{project_id}/{path}"
        try:
            response = self.client.get_object(self.project_bucket, object_name)
            content = response.read().decode("utf-8")
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            if e.code == "NoSuchKey":
                return f"(file not found: {path})"
            raise

    def write_file(self, project_id: str, path: str, content: str) -> None:
        """
        Write a file to MinIO. Creates or overwrites.

        Converts the string content to bytes, wraps in a BytesIO
        stream (which is what MinIO's put_object expects), and uploads.
        """
        self._ensure_bucket(self.project_bucket)

        object_name = f"{project_id}/{path}"
        data = content.encode("utf-8")
        stream = io.BytesIO(data)

        self.client.put_object(
            self.project_bucket,
            object_name,
            stream,
            length=len(data),
            content_type="text/plain",
        )
