from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from supervisely.api.image_api import ImageInfo
from supervisely.nn.benchmark.visualization.vis_metric_base import MetricVis
from supervisely.nn.benchmark.visualization.vis_widgets import Schema, Widget

if TYPE_CHECKING:
    from supervisely.nn.benchmark.visualization.visualizer import Visualizer


class ModelPredictions(MetricVis):

    def __init__(self, loader: Visualizer) -> None:
        super().__init__(loader)
        self.schema = Schema(
            markdown_predictions_gallery=Widget.Markdown(
                title="Model Predictions", is_header=False
            ),
            markdown_predictions_table=Widget.Markdown(
                title="Prediction details for every image", is_header=True
            ),
            # gallery=Widget.Gallery(is_table_gallery=True),
            table=Widget.Table(),
        )
        self._row_ids = None

    def get_table(self, widget: Widget.Table) -> dict:
        res = {}
        dt_project_id = self._loader.dt_project_info.id

        tmp = set()
        for dt_dataset in self._loader._api.dataset.get_list(dt_project_id):
            names = [x.name for x in self._loader._api.image.get_list(dt_dataset.id)]
            tmp.update(names)
        df = self._loader.mp.prediction_table().round(2)
        df = df[df["Image name"].isin(tmp)]
        columns_options = [
            {"maxWidth": "225px"},
            {"subtitle": "objects count", "tooltip": "Number of ground truth objects on the image"},
            {"subtitle": "objects count", "tooltip": "Number of predicted objects on the image"},
            {
                "subtitle": "objects count",
                "tooltip": "True Positive objects count (correctly detected)",
            },
            {
                "subtitle": "objects count",
                "tooltip": "False Positive objects count (incorrect detections)",
            },
            {
                "subtitle": "objects count",
                "tooltip": "False Negative objects count (missed detections)",
            },
            {"maxValue": 1, "tooltip": "Precision (positive predictive value)"},
            {"maxValue": 1, "tooltip": "Recall (sensitivity)"},
            {"maxValue": 1, "tooltip": "F1 score (harmonic mean of precision and recall)"},
        ]
        table_model_preds = widget.table(df, columns_options=columns_options)
        tbl = table_model_preds.to_json()

        res["columns"] = tbl["columns"]
        res["columnsOptions"] = columns_options
        res["content"] = []

        key_mapping = {}
        for old, new in zip(ImageInfo._fields, self._loader._api.image.info_sequence()):
            key_mapping[old] = new

        self._row_ids = []

        for row in tbl["data"]["data"]:
            name = row["items"][0]
            info = self._loader.dt_images_dct_by_name[name]

            dct = {
                "row": {key_mapping[k]: v for k, v in info._asdict().items()},
                "id": info.name,
                "items": row["items"],
            }

            self._row_ids.append(dct["id"])
            res["content"].append(dct)

        return res

    def get_table_click_data(self, widget: Widget.Table) -> Optional[dict]:
        res = {}
        res["layoutTemplate"] = [
            {"skipObjectTagsFiltering": True, "columnTitle": "Ground Truth"},
            {"skipObjectTagsFiltering": ["outcome"], "columnTitle": "Prediction"},
            {"skipObjectTagsFiltering": ["confidence"], "columnTitle": "Difference"},
        ]
        click_data = res.setdefault("clickData", {})

        optimal_conf = round(self.f1_optimal_conf, 1)
        default_filters = [
            {"type": "tag", "tagId": "confidence", "value": [optimal_conf, 1]},
            # {"type": "tag", "tagId": "outcome", "value": "FP"},
        ]

        l1 = list(self._loader.gt_images_dct.values())
        l2 = list(self._loader.dt_images_dct.values())
        l3 = list(self._loader.diff_images_dct.values())

        pred_anns = self._loader.dt_ann_jsons  # {image_id: ann_json}
        diff_anns = self._loader.diff_ann_jsons  # {image_id: ann_json}

        for gt, pred, diff, pred_ann, diff_ann in zip(
            l1, l2, l3, pred_anns.items(), diff_anns.items()
        ):
            assert gt.name == pred.name == diff.name
            key = click_data.setdefault(str(pred.name), {})
            key["imagesIds"] = [gt.id, pred.id, diff.id]
            key["filters"] = default_filters
            key["title"] = f"Image: {pred.name}"
            image_id, ann_json = pred_ann
            assert image_id == pred.id
            object_bindings = []
            for obj in ann_json["objects"]:
                for tag in obj["tags"]:
                    if tag["name"] == "matched_gt_id":
                        object_bindings.append(
                            [
                                {
                                    "id": obj["id"],
                                    "annotationKey": image_id,
                                },
                                {
                                    "id": int(tag["value"]),
                                    "annotationKey": gt.id,
                                },
                            ]
                        )

            image_id, ann_json = diff_ann
            assert image_id == diff.id
            for obj in ann_json["objects"]:
                for tag in obj["tags"]:
                    if tag["name"] == "matched_gt_id":
                        object_bindings.append(
                            [
                                {
                                    "id": obj["id"],
                                    "annotationKey": image_id,
                                },
                                {
                                    "id": int(tag["value"]),
                                    "annotationKey": pred.id,
                                },
                            ]
                        )
            key["objectsBindings"] = object_bindings

        return res
