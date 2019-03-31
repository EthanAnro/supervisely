# coding: utf-8

from supervisely_lib.sly_logger import logger, ServiceType, EventType, add_logger_handler, \
    add_default_logging_into_file, get_task_logger, change_formatters_default_values, LOGGING_LEVELS

from supervisely_lib.function_wrapper import main_wrapper, function_wrapper, catch_silently, function_wrapper_nofail

from supervisely_lib.io import fs
from supervisely_lib.io import env

from supervisely_lib.imaging import image
from supervisely_lib.imaging import video
from supervisely_lib.imaging import color

from supervisely_lib.task.paths import TaskPaths

from supervisely_lib.task.progress import epoch_float, Progress, report_import_finished, report_dtl_finished, \
    report_dtl_verification_finished, \
    report_metrics_training, report_metrics_validation, report_inference_finished

from supervisely_lib.project.project import Project, OpenMode
from supervisely_lib.project.project_meta import ProjectMeta

from supervisely_lib.annotation.annotation import ANN_EXT, Annotation
from supervisely_lib.annotation.label import Label
from supervisely_lib.annotation.obj_class import ObjClass, ObjClassJsonFields
from supervisely_lib.annotation.obj_class_collection import ObjClassCollection
from supervisely_lib.annotation.tag_meta import TagMeta, TagValueType
from supervisely_lib.annotation.tag import Tag
from supervisely_lib.annotation.tag_collection import TagCollection
from supervisely_lib.annotation.tag_meta_collection import TagMetaCollection

from supervisely_lib.geometry.bitmap import Bitmap
from supervisely_lib.geometry.point import Point
from supervisely_lib.geometry.point_location import PointLocation
from supervisely_lib.geometry.polygon import Polygon
from supervisely_lib.geometry.polyline import Polyline
from supervisely_lib.geometry.rectangle import Rectangle

from supervisely_lib.geometry.helpers import geometry_to_bitmap

from supervisely_lib.metric.metric_base import MetricsBase
from supervisely_lib.metric.projects_applier import MetricProjectsApplier

from supervisely_lib.metric.iou_metric import IoUMetric
from supervisely_lib.metric.confusion_matrix_metric import ConfusionMatrixMetric
from supervisely_lib.metric.precision_recall_metric import PrecisionRecallMetric
from supervisely_lib.metric.classification_metrics import ClassificationMetrics
from supervisely_lib.metric.map_metric import MAPMetric

from supervisely_lib.worker_api.agent_api import AgentAPI
from supervisely_lib.worker_api.chunking import ChunkSplitter, ChunkedFileWriter, ChunkedFileReader
import supervisely_lib.worker_proto.worker_api_pb2 as api_proto

from supervisely_lib.api.api import Api
from supervisely_lib.api import api
from supervisely_lib.api.module_api import WaitingTimeExceeded

from supervisely_lib._utils import rand_str

from supervisely_lib.aug import aug