# 2021 PNAS - Responsive Implantable Neuroelectronics

Source PDF: `../../../Resources/Zhao_2021_PNAS_Responsive manipulation of neural circuit pathology by fully implantable front end multiplexed embedded neuroelectronics.pdf`

## Core Message

This paper asks whether an implanted neural interface can record many channels, process signals on board, and deliver stimulation only when pathological brain activity appears. The key engineering idea is multiplex-then-amplify (MTA): reduce electronics size and power by sharing amplifiers after multiplexing, while still supporting multichannel recording and arbitrary-waveform stimulation.

## Audience Hook

如果一个植入式设备能听懂大脑异常信号，并马上做出干预，会发生什么？

## 4-5 Page Xiaohongshu Carousel

### Page 1 - Hook

Title: 大脑异常信号出现时，设备能不能自己反应？

Visual: Hero figure or device overview.

Copy: 当前限制不是不能刺激，而是很难在异常活动刚出现时就立刻识别并干预。

Takeaway: 闭环神经接口 = 记录 + 判断 + 刺激。

### Page 2 - The Bottleneck

Title: 通道越多，电子系统越难小型化

Visual: Figure showing device architecture or channel/electronics layout.

Copy: 多通道往往意味着更多放大器、更高功耗和更大体积，这对长期植入是硬限制。

Takeaway: 高通道数和低功耗之间需要新的架构。

### Page 3 - The Invention

Title: MTA: 先复用，再放大

Visual: Multiplex-then-amplify schematic.

Copy: MTA 用先复用、再放大的架构，把前端组件压下来，同时保住多通道采集能力。

Takeaway: 系统架构本身就是神经接口创新。

### Page 4 - Closed-Loop Function

Title: 不只是记录，还能实时干预

Visual: Recording, processing, stimulation, or onboard workflow figure.

Copy: 这个平台把记录、板载处理、低延迟刺激和存储放进同一个植入系统里。

Takeaway: 设备从"传感器"变成了"响应式系统"。

### Page 5 - Biological Conclusion

Title: 用闭环刺激改变病理性脑网络耦合

Visual: Main epilepsy/network intervention result.

Copy: 在动物实验里，它能压低海马与皮层之间和癫痫样放电相关的异常耦合。

Takeaway: 神经接口的目标不是替代大脑，而是理解并调节异常网络。

## 60-90 Second Dubbed Video Script

0-8s: "这篇 PNAS 论文想回答一个问题：植入式神经接口能不能在大脑异常活动出现时自己反应？"

8-22s: "传统多通道系统要记录更多脑区，往往需要更多放大器，结果就是体积、功耗和复杂度都上升。"

22-38s: "我们的核心设计叫 MTA，multiplex-then-amplify，也就是先复用、再放大。它让高通道记录和小型化植入设备更容易同时实现。"

38-58s: "系统不只记录信号，还能在设备内实时处理，并向多个通道输出任意波形刺激。也就是说，它可以形成记录、判断、干预的闭环。"

58-78s: "在癫痫相关动物模型里，我们用它识别并调节海马和皮层之间的异常网络耦合。这个结果说明，神经接口可以成为研究脑网络疾病的主动工具。"

78-90s: "一句话总结：这不是一个单纯的记录器，而是一个能响应病理脑活动的植入式神经接口。"

## Figure Story Map

- Figure anchor 1: Device/system overview. Use it to explain "what was built."
- Figure anchor 2: MTA circuit architecture. Use it to explain "why it can be smaller/lower power."
- Figure anchor 3: Neural recording quality. Use it to show "the system still hears real spikes."
- Figure anchor 4: Stimulation/closed-loop workflow. Use it to show "the system can act."
- Figure anchor 5: Hippocampus-cortex pathological coupling result. Use it as the scientific conclusion.

## Caption Draft

这篇论文想解决一个很现实的限制：植入式设备如果想多通道记录、实时判断、再马上刺激，体积和功耗很快就会失控。MTA 架构的目标，就是把这些功能塞进一个更小、更低功耗的闭环神经接口里。

## Hashtags

#神经接口 #脑机接口 #癫痫研究 #闭环刺激 #神经工程 #生物电子学 #科研日常 #论文分享

## Asset Checklist

- `figures/01-device-overview.png`
- `figures/02-mta-architecture.png`
- `figures/03-recording-quality.png`
- `figures/04-closed-loop-workflow.png`
- `figures/05-network-intervention.png`
- Optional voiceover: `voice/pnas-2021-voiceover.wav`
