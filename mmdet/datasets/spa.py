import copy
import os.path as osp

import mmcv
import numpy as np

from mmdet.datasets.builder import DATASETS
from mmdet.datasets.custom import CustomDataset

@DATASETS.register_module()
class SPADataset(CustomDataset):

    CLASSES = ('Car', 'Pedestrian', 'Cyclist')

    def load_annotations(self, ann_file):
        cat2label = {k: i for i, k in enumerate(self.CLASSES)}
        # load image list from file
        image_list = mmcv.list_from_file(self.ann_file)
    
        data_infos = []
        # convert annotations to middle format


        for image_id in image_list:
            place = image_id.split("*")[0]
            scene = image_id.split("*")[1]
            frame = image_id.split("*")[2]

            for cam_num in [1,2,3,4,5]:
                filename = f'{self.img_prefix}/{place}/{scene}/{"cam_img"}/{cam_num}/{"data_rgb"}/{frame}.png'
                image = mmcv.imread(filename)
                height, width = image.shape[:2]
        
                data_info = dict(filename=filename, width=width, height=height)
                filename = f'{self.img_prefix}/{place}/{scene}/{"cam_img"}/{cam_num}/{"data_rgb"}/'
        
                # load annotations
                label_prefix = filename.replace('cam_img/{}/'.format(cam_num) + "data_rgb", 'label/label_{}'.format(cam_num))
                lines = mmcv.list_from_file(osp.join(label_prefix, f'{frame}.txt'))
        
                content = [line.strip().split(' ') for line in lines]
                bbox_names = [x[0] for x in content]
                # bboxes = [[float(info) for info in x[4:8]] for x in content]
                bboxes = [[float(info) for info in x[5:9]] for x in content]
        
                gt_bboxes = []
                gt_labels = []
                gt_bboxes_ignore = []
                gt_labels_ignore = []
        
                # filter 'DontCare'
                for bbox_name, bbox in zip(bbox_names, bboxes):
                    if bbox_name in cat2label:
                        gt_labels.append(cat2label[bbox_name])
                        gt_bboxes.append(bbox)
                    else:
                        gt_labels_ignore.append(-1)
                        gt_bboxes_ignore.append(bbox)

                data_anno = dict(
                    bboxes=np.array(gt_bboxes, dtype=np.float32).reshape(-1, 4),
                    labels=np.array(gt_labels, dtype=np.long),
                    bboxes_ignore=np.array(gt_bboxes_ignore,
                                        dtype=np.float32).reshape(-1, 4),
                    labels_ignore=np.array(gt_labels_ignore, dtype=np.long))

                data_info.update(ann=data_anno)
                data_infos.append(data_info)

        return data_infos