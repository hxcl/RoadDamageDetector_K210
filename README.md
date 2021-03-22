# 基于 K210 的路面损坏识别系统

## 前言

由于各种各样的原因，随着时间的推移，公路路面上会出现各种各样的损坏情况，例如出现裂缝、出现坑洼和交通标线模糊等。这些损坏情况往往会降低车辆行驶的舒适性，还可能成为交通事故的诱因。因此需要路政部门定期进行道路保养工作。目前大部分地区仍依赖人工检查道路问题，任务繁重而低效。当下，已有多个团队研究了这个领域的自动化检测方法，他们大多使用了目标检测算法寻找路面上可能存在的损坏情况。

## 项目简介

本项目在 Kendryte K210 芯片上部署了一个基于 YOLOv2 的道路损坏检测模型，并能在地图上将数据可视化。效果尚可。开发过程中，我们还尝试过其他的检测算法，由于各种原因没有作为最终的方案。

## Thanks

[MaixPy](https://github.com/sipeed/MaixPy)

[yolo_for_k210](https://github.com/TonyZ1Min/yolo-for-k210)

[MobileNet-Yolo](https://github.com/dog-qiuqiu/MobileNet-Yolo)

[GPS\(GNSS\)Module_for_MaixPy](https://github.com/Liuyufanlyf/GPS-GNSS-_Module_for_MaixPy)

[YOLOv3_TensorFlow2](https://github.com/calmisential/YOLOv3_TensorFlow2)