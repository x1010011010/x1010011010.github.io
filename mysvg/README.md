# SVG Animation Player

## 🎬 使用说明

### 1. 文件结构
确保你的目录包含以下文件：
```
mysvg/
├── video_to_svg_animation.py  # 视频转换脚本
├── player.html               # SVG动画播放器
├── pathdata.json            # 动画数据文件
└── requirements_video_converter.txt
```

### 2. 播放动画
在浏览器中打开 `player.html` 文件，或者运行本地服务器：

```bash
# 方法1: 直接打开
# 双击 player.html 文件

# 方法2: 使用Python启动本地服务器
python -m http.server 8000
# 然后访问 http://localhost:8000/player.html
```

### 3. 播放器功能

#### 🎨 颜色控制
- **Fill Color**: 改变SVG路径的填充颜色
- **Background**: 改变页面背景颜色

#### ⚡ 播放控制
- **Play/Pause**: 播放/暂停动画
- **Reset**: 重置到第一帧
- **FPS滑块**: 调整播放帧率 (1-30 FPS)

#### ⌨️ 键盘快捷键
- `Space`: 播放/暂停
- `R`: 重置
- `←`: 上一帧
- `→`: 下一帧

#### 📊 信息面板
右下角显示：
- 当前帧 / 总帧数
- 当前时间 / 总时长
- 实际FPS

### 4. 转换新视频

要转换新的视频文件：

```bash
# 基本用法
python video_to_svg_animation.py your_video.mp4

# 自定义参数
python video_to_svg_animation.py your_video.mp4 -o custom_name.json --fps 20 --size 600x400

# 保留临时文件用于调试
python video_to_svg_animation.py your_video.mp4 --keep-temp
```

### 5. 技术细节

#### 支持的视频格式
- MP4, AVI, MOV, WMV 等常见格式
- 建议使用较短的视频片段（< 30秒）以获得最佳性能

#### 性能优化建议
- **分辨率**: 480x360 或更小
- **帧率**: 15 FPS 通常足够流畅
- **时长**: 建议不超过1分钟

#### 文件大小估算
- 15fps, 30秒视频 ≈ 450帧
- 每帧路径数据 ≈ 100-500 字节
- 最终JSON文件 ≈ 50KB-200KB

### 6. 故障排除

#### 常见问题
1. **"Error loading data"**: 确保 `pathdata.json` 文件存在且格式正确
2. **空白页面**: 检查浏览器控制台是否有JavaScript错误
3. **转换失败**: 确保FFmpeg和Potrace已正确安装

#### 依赖检查
```bash
# 检查FFmpeg
ffmpeg -version

# 检查Potrace
potrace --version

# 检查Python包
pip list | grep opencv
pip list | grep Pillow
```

### 7. 自定义开发

播放器是完全可定制的，你可以：
- 修改CSS样式
- 添加新的控制功能
- 集成到其他网页项目中
- 添加音频同步功能

### 8. 示例命令

```bash
# 转换一个短视频
python video_to_svg_animation.py sample.mp4

# 高质量转换
python video_to_svg_animation.py sample.mp4 --fps 24 --size 800x600 -o high_quality.json

# 快速预览转换
python video_to_svg_animation.py sample.mp4 --fps 10 --size 320x240 -o preview.json
```

享受你的SVG动画播放器！🎉
