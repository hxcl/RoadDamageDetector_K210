# road_condition_web
路面情况管理网页端

### 关于 K210

#### KPU

K210 SOC 内部搭载一颗 KPU(Neural Network Processor), KPU 即通用的神经网络处理器，它可以在低功耗的情况下实现卷积神经网络计算，时时获取被检测目标的大小、坐标和种类，对人脸或者物体进行检测和分类。

K210 搭载的 KPU 具备以下几个特点：

1. 支持主流训练框架按照特定限制规则训练出来的定点化模型

2. 对网络层数无直接限制，支持每层卷积神经网络参数单独配置，包括输入输出通道数目、输入输 出行宽列高

3. 支持两种卷积内核 1x1 和 3x3

4. 支持任意形式的激活函数

5. 实时工作时最大支持神经网络参数大小为 5.5MiB 到 5.9MiB

   注：本参数主要受内存限制，若使用 MaixPy 开发，最多只能支持 3MB 左右的模型

6. 非实时工作时最大支持网络参数大小为（Flash 容量-软件体积）

#### K210 的 IO 口

K210 芯片的一个特点是所有的外设都可以任意映射到外部引脚，对于开发者来说极其方便，但要注意一些事项。在 STM32 中，GPIOB15 既是一个 GPIO 外设的名称，也是物理上的一根引脚的名称，**两者是绑定的**。但在 K210 中，GPIO 仅仅是一个外设，和物理上的引脚没有绑定关系， 使用时要映射到特定的物理引脚。K210 在物理上共有 48 个 I/O 引脚，分别为 IO0~IO47。高速和通用 GPIO 加起来则有 40 个，分别为 GPIOHS0~31, GPIO0~7. 使用 GPIO 外设时，要先通过 FPIOA(现场可编程 IO 阵列)将使用的 GPIO 映射到物理 IO 口。 