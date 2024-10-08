import imghdr
import os
from typing import List

import supervisely.convert.pointcloud.sly.sly_pointcloud_helper as helpers
from supervisely import PointcloudAnnotation, ProjectMeta, logger
from supervisely.convert.base_converter import AvailablePointcloudConverters
from supervisely.convert.pointcloud.pointcloud_converter import PointcloudConverter
from supervisely.io.fs import JUNK_FILES, get_file_ext, get_file_name
from supervisely.io.json import load_json_file
from supervisely.pointcloud.pointcloud import validate_ext as validate_pcd_ext


class SLYPointcloudConverter(PointcloudConverter):

    def __str__(self) -> str:
        return AvailablePointcloudConverters.SLY

    @property
    def ann_ext(self) -> str:
        return ".json"

    @property
    def key_file_ext(self) -> str:
        return ".json"

    def generate_meta_from_annotation(self, ann_path: str, meta: ProjectMeta) -> ProjectMeta:
        meta = helpers.get_meta_from_annotation(ann_path, meta)
        return meta

    def validate_ann_file(self, ann_path: str, meta: ProjectMeta) -> bool:
        try:
            ann_json = load_json_file(ann_path)
            if "annotation" in ann_json:
                ann_json = ann_json["annotation"]
            ann = PointcloudAnnotation.from_json(ann_json, meta)
            return True
        except Exception as e:
            return False

    def validate_key_file(self, key_file_path: str) -> bool:
        try:
            self._meta = ProjectMeta.from_json(load_json_file(key_file_path))
            return True
        except Exception:
            return False

    def validate_format(self) -> bool:
        detected_ann_cnt = 0
        pcd_list, ann_dict, rimg_dict, rimg_ann_dict = [], {}, {}, {}
        used_img_ext = []
        for root, _, files in os.walk(self._input_data):
            for file in files:
                full_path = os.path.join(root, file)
                if file == "key_id_map.json":
                    continue
                if file == "meta.json":
                    is_valid = self.validate_key_file(full_path)
                    if is_valid:
                        continue

                ext = get_file_ext(full_path)
                if file in JUNK_FILES:  # add better check
                    continue
                elif ext in self.ann_ext:
                    dir_name = os.path.basename(root)
                    parent_dir_name = os.path.basename(os.path.dirname(root))
                    if any(
                        p.replace("_", " ") in ["images", "related images", "photo context"]
                        for p in [dir_name, parent_dir_name]
                    ) or dir_name.endswith("_pcd"):
                        rimg_ann_dict[file] = full_path
                    else:
                        ann_dict[file] = full_path
                elif imghdr.what(full_path):
                    rimg_dict[file] = full_path
                    if ext not in used_img_ext:
                        used_img_ext.append(ext)
                else:
                    try:
                        validate_pcd_ext(ext)
                        pcd_list.append(full_path)
                    except:
                        continue

        if self._meta is not None:
            meta = self._meta
        else:
            meta = ProjectMeta()

        # create Items
        self._items = []
        for pcd_path in pcd_list:
            name_noext = get_file_name(pcd_path)
            ann_or_rimg_detected = False
            item = self.Item(pcd_path)
            ann_name = f"{item.name}.json"
            if ann_name not in ann_dict:
                ann_name = f"{name_noext}.json"
            if ann_name in ann_dict:
                ann_path = ann_dict[ann_name]
                if self._meta is None:
                    meta = self.generate_meta_from_annotation(ann_path, meta)
                is_valid = self.validate_ann_file(ann_path, meta)
                if is_valid:
                    item.ann_data = ann_path
                    ann_or_rimg_detected = True
            rimg, rimg_ann = helpers.find_related_items(
                item.name, used_img_ext, rimg_dict, rimg_ann_dict
            )
            if rimg is not None and rimg_ann is not None:
                item.set_related_images((rimg, rimg_ann))
                ann_or_rimg_detected = True

            if ann_or_rimg_detected:
                detected_ann_cnt += 1
            self._items.append(item)
        self._meta = meta
        return detected_ann_cnt > 0

    def to_supervisely(
        self,
        item: PointcloudConverter.Item,
        meta: ProjectMeta = None,
        renamed_classes: dict = None,
        renamed_tags: dict = None,
    ) -> PointcloudAnnotation:
        """Convert to Supervisely format."""
        if meta is None:
            meta = self._meta

        if item.ann_data is None:
            return item.create_empty_annotation()

        try:
            ann_json = load_json_file(item.ann_data)
            if "annotation" in ann_json:
                ann_json = ann_json["annotation"]
            if renamed_classes or renamed_tags:
                ann_json = helpers.rename_in_json(ann_json, renamed_classes, renamed_tags)
            return PointcloudAnnotation.from_json(ann_json, meta)
        except Exception as e:
            logger.warn(f"Failed to convert annotation: {repr(e)}")
            return item.create_empty_annotation()
