import contextlib
import dataclasses
import os
import random
import shutil
import pathlib
import typing

from . import uris
from . import errors
from . import wandb_client_api
from . import memo

from . import file_util
from . import weave_types as types
from . import artifact_fs
from . import filesystem

if typing.TYPE_CHECKING:
    from wandb.apis.public import Run as WBRun


@memo.memo
def get_wandb_read_run(path: str) -> "WBRun":
    return wandb_client_api.wandb_public_api().run(path)


def wandb_run_dir() -> str:
    d = os.path.join(filesystem.get_filesystem_dir(), "_wandb_runs")
    os.makedirs(d, exist_ok=True)
    return d


@contextlib.contextmanager
def _isolated_download_and_atomic_mover(
    end_path: str,
) -> typing.Generator[typing.Tuple[str, typing.Callable[[str], None]], None, None]:
    rand_part = "".join(random.choice("0123456789ABCDEF") for _ in range(16))
    tmp_dir = os.path.join(wandb_run_dir(), f"tmp_{rand_part}")
    os.makedirs(tmp_dir, exist_ok=True)

    def mover(tmp_path: str) -> None:
        # This uses the same technique as WB artifacts
        pathlib.Path(end_path).parent.mkdir(parents=True, exist_ok=True)
        try:
            os.replace(tmp_path, end_path)
        except AttributeError:
            os.rename(tmp_path, end_path)

    try:
        yield tmp_dir, mover
    finally:
        shutil.rmtree(tmp_dir)


class WandbRunFiles(artifact_fs.FilesystemArtifact):
    def __init__(
        self,
        name: str,
        uri: "WeaveWBRunFilesURI",
    ):
        self.name = name
        self._run_files_uri = uri
        self._read_run = None
        self._local_path: dict[str, str] = {}

    @property
    def run(self) -> "WBRun":
        if self._read_run is None:
            self._read_run = get_wandb_read_run(self.name)
        return self._read_run

    @property
    def is_saved(self) -> bool:
        return True

    @property
    def uri_obj(self) -> "WeaveWBRunFilesURI":
        return self._run_files_uri

    def path(self, path: str) -> str:
        # TODO: Move this logic to `io_service`. We can get rid of the
        # `get_wandb_read_run` as well once we do this

        # First, check if we already downloaded this file:
        if path in self._local_path:
            return self._local_path[path]

        static_file_path = os.path.join(wandb_run_dir(), str(self.name), path)
        # Next, check if another process has already downloaded this file:
        if os.path.exists(static_file_path):
            self._local_path[path] = static_file_path
            return static_file_path

        # Finally, download the file in an isolated directory:
        with _isolated_download_and_atomic_mover(static_file_path) as (tmp_dir, mover):
            with self.run.file(path).download(tmp_dir, replace=True) as fp:
                downloaded_file_path = fp.name
            mover(downloaded_file_path)

        self._local_path[path] = static_file_path
        return static_file_path

    def _path_info(self, path: str) -> "artifact_fs.FilesystemArtifactFile":
        # TODO: In the WBArtifact sister class, we check the manifest to see if
        # a) the file exists
        # b) it is a directory.
        #
        # Here, we blindly assume that the file exists and is not a directory.
        #
        # TODO: Enforce this check similarly.
        return artifact_fs.FilesystemArtifactFile(self, path)

    @contextlib.contextmanager
    def open(
        self, path: str, binary: bool = False
    ) -> typing.Generator[typing.IO, None, None]:
        mode = "rb" if binary else "r"
        p = self.path(path)
        with file_util.safe_open(p, mode) as f:
            yield f


class WandbRunFilesType(artifact_fs.FilesystemArtifactType):
    def save_instance(
        self, obj: typing.Any, artifact: typing.Any, name: str
    ) -> "WandbRunFilesRef":
        return WandbRunFilesRef(obj, None)


WandbRunFilesType.instance_classes = WandbRunFiles


class WandbRunFilesRef(artifact_fs.FilesystemArtifactRef):
    artifact: WandbRunFiles

    def versions(self) -> list[artifact_fs.FilesystemArtifactRef]:
        return [self]

    @classmethod
    def from_uri(cls, uri: "uris.WeaveURI") -> "WandbRunFilesRef":
        if not isinstance(uri, (WeaveWBRunFilesURI)):
            raise errors.WeaveInternalError(
                f"Invalid URI class passed to WandbRunFilesRef.from_uri: {type(uri)}"
            )
        return cls(
            WandbRunFiles(uri.name, uri=uri),
            path=uri.path,
        )


WandbRunFiles.RefClass = WandbRunFilesRef


@dataclasses.dataclass(frozen=True)
class WandbRunFilesRefType(types.RefType):
    pass


WandbRunFilesRefType.instance_class = WandbRunFilesRef
WandbRunFilesRefType.instance_classes = WandbRunFilesRef


@dataclasses.dataclass
class WeaveWBRunFilesURI(uris.WeaveURI):
    SCHEME = "wandb-run-file"
    entity_name: str
    project_name: str
    run_name: str
    path: typing.Optional[str] = None

    @classmethod
    def from_parsed_uri(
        cls,
        uri: str,
        schema: str,
        netloc: str,
        path: str,
        params: str,
        query: dict[str, list[str]],
        fragment: str,
    ) -> "WeaveWBRunFilesURI":
        path = path.strip("/")
        entity_name = netloc
        project_name, run_name, path = path.split("/", 2)
        return cls(netloc, None, entity_name, project_name, run_name, path)

    def to_ref(self) -> WandbRunFilesRef:
        return WandbRunFilesRef.from_uri(self)

    def __str__(self) -> str:
        netloc = f"{self.entity_name}/{self.project_name}/{self.run_name}"
        path = self.path or ""
        if path != "":
            path = f"/{path}"
        return f"{self.SCHEME}://{netloc}{path}"