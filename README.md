# diablo-auto-fish

## Introduction

The script bases on the graphics on the screen and emulates mouse and keyboard functions to realize fishing in Diablo Immortal automatically. Due to its nature, the game must run in the foreground for the script to correctly function. Furthermore, because of the potential differences in the color rendering for different operating system and software/hardware versions, the script may require editing (especially in terms of the RGB color) before it correctly functions on a particular machine. 

Note: the script is for discussion and studying purpose and should not be used to break the fairness of the game.

## For windows user:

### $\color{red}\text{Featured Updates}$
- Now support auto salvation (works much better with tesseract, see later sections for installation). With this function enabled, it checks bag capacity after each fishing cycle (when 20 fishes are obtained), and goes back to town to salvage if bag capacity is below the set level.
- Now fishing key bind can be set to a custom keyboard key, with default of ‘5’ (this was fixed to mouse right button previously).
- Items pickup was uptimized to reduce the chance of missing gold dropped.

### Requirements
- Python 3 (python 3.10 tested)
- numpy
- opencv-python
- Pillow
- pyautogui
- $\color{red}\text{pytesseract}$

### 安装
- 安装Python 3；
- 将代码下载到本地后，打开命令提示符（WinKey + R，输入cmd后回车），运行：

```
cd <path-to-directory>
python -m pip install -r requirements.txt
```

- $\color{red}\text{安装Tesseract}$（识别图形中的文字，以找到NPC）：
	- 下载[安装文件](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe) （或在[这里](https://github.com/UB-Mannheim/tesseract/wiki)下载）；
	- 打开安装文件，按提示安装。注意确保 $\color{red}\text{安装路径}$ 为：`C:/Program Files/Tesseract-OCR/`

### Installation
- Install Python 3;
- After cloning this repository to local, in command line (press WinKey + R and input cmd, then enter), run:

```
cd <path-to-directory>
python -m pip install -r requirements.txt
```

- $\color{red}\text{Install Tesseract}$
  - Download [the installer](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe), or from [this link](https://github.com/UB-Mannheim/tesseract/wiki);
  - Run the installer, make sure it is installed $\color{red}\text{in this directory}$: `C:/Program Files/Tesseract-OCR/`.

### 游戏内设定
- 显示器分辨率设置为1920\*1080，游戏以**英文版**运行（以后或许支持中文游戏界面）；
- 显示设置：
  - 图像模式：经典
  - 窗口模式：全屏
  - 环境亮度：50\%
- 图像设置：
  - 画质全部调为最低的选项；
  - 关闭所有特效
- 按键设置：
  - 移动/攻击：**不要**设置鼠标左键
  - 钓鱼技能：~~鼠标右键~~ $\color{red}\text{现在可以设置键盘按键，默认为5}$
  - **鼠标左键不要设置任何技能和操作**
- 站在钓鱼点，注意不要离NPC太远，要在可以对话的距离内。

### In-game Settings
- Diablo Immortal must be running at 1920\*1080 resolution, English version.
- Display setting:
  - Classic mode
  - **full screen**
  - Brightness: 50\%
- Graphic setting:
  - All graphic settings should be set to the lowest.
  - Turn off all effects.
- Set key bindings: 
  - Move/Attack: anything **except** Mouse left (primary) button
  - Fishing Skills: ~~Mouse right (secondary) button~~ $\color{red}\text{Updated: now support keyboard keys, default: 5}$
  - **Do not set Mouse left (primary) button for any skills**
- Stand your character at a fishing spot, preferably not ashwold because there's a mob coming over to attack you once in a while.

### 开始钓鱼
- 确保游戏正在运行中，使用组合键ALT + TAB切出窗口，找到`fishing.py`双击打开；
- 选择鱼的种类和钓鱼地点，亮度条建议保持默认；
- 目前共有3个模式：
  - 循环钓鱼选择第一个选项，会自动卖鱼和买鱼饵；
  - 只钓一轮选第二个选项，会钓完鱼饵或钓满20条鱼；
  - 自动卖鱼和买鱼饵选第三个选项，不钓鱼。
- 开始后，如果要停止或者改变选项，ALT + TAB切出窗口后可以点击停止。

### Start Fishing
- While the game is running, switch out to the folder that contains `fishing.py`, double-click to open;
- Choose fish type and location, and click Auto Fishing.
- To stop, switch out and click Stop Fishing.
- When Auto Fishing, it checks your bag in the end of every fishing cycle (20 fishes) and performs Auto Salvage if bag capacity is below the set percent.
- Auto Fishing in the map Frozen Tundra is not tested yet.


## For Mac Users using sideloadly to run Diablo Immortal on M1/M2 Macs:

To be completed...


## Contact

If you have any questions or concerns, please contact me at q30zhang@gmail.com.
