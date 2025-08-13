"""
Complete video to SVG animation converter
将视频一步转换为SVG动画所需的JSON文件

Requirements:
- ffmpeg (视频处理)
- potrace (位图转SVG)
- Python packages: opencv-python, pillow

Usage:
    python video_to_svg_animation.py input_video.mp4
    python video_to_svg_animation.py input_video.mp4 -o output.json --fps 15 --size 480x360
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from xml.dom import minidom
import cv2
import numpy as np
from PIL import Image

def check_dependencies():
    """检查必要的依赖工具"""
    missing = []
    
    # 检查 FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ ffmpeg is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('ffmpeg')
        print("✗ ffmpeg is not installed")
    
    # 检查 Potrace
    try:
        subprocess.run(['potrace', '--version'], capture_output=True, check=True)
        print("✓ potrace is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('potrace')
        print("✗ potrace is not installed")
    
    if missing:
        print(f"\nPlease install missing dependencies: {', '.join(missing)}")
        print("FFmpeg: https://ffmpeg.org/download.html")
        print("Potrace: http://potrace.sourceforge.net/")
        return False
    return True

def extract_frames_with_opencv(video_path, output_dir, fps=5, size=(480, 360)):
    """使用OpenCV提取视频帧并转换为黑白，优化用于BAS系统"""
    print(f"Extracting frames from {video_path} (optimized for BAS @ {fps}fps)...")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    # 获取视频信息
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / original_fps
    
    print(f"Video info: {original_fps:.2f} fps, {total_frames} frames, {duration:.2f}s")
    
    # 计算帧间隔
    frame_interval = int(original_fps / fps)
    target_frames = int(duration * fps)
    
    print(f"Extracting every {frame_interval} frames, targeting {target_frames} frames at {fps} fps")
    print(f"Estimated output duration: {target_frames/fps:.1f}s at {fps}fps (suitable for BAS)")
    
    frame_count = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            # 调整大小
            resized = cv2.resize(frame, size)
            
            # 修正上下颠倒问题：翻转Y轴
            resized = cv2.flip(resized, 0)
            
            # 转换为灰度
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # 优化的二值化处理 - 使用自适应阈值以获得更好的细节
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # 可选：降噪处理
            kernel = np.ones((2,2), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # 保存为BMP
            output_path = os.path.join(output_dir, f"frame_{extracted_count:04d}.bmp")
            cv2.imwrite(output_path, binary)
            
            extracted_count += 1
            if extracted_count % 50 == 0:  # 更频繁的进度更新
                print(f"Extracted {extracted_count} frames...")
        
        frame_count += 1
    
    cap.release()
    print(f"Extracted {extracted_count} frames total for BAS playback")
    return extracted_count

def convert_bmp_to_svg(bmp_dir, svg_dir, target_width=4800, target_height=3600):
    """使用Potrace将BMP文件转换为SVG，优化用于BAS弹幕系统"""
    print("Converting BMP files to SVG (optimized for BAS)...")
    
    bmp_files = sorted([f for f in os.listdir(bmp_dir) if f.endswith('.bmp')])
    total = len(bmp_files)
    
    for i, bmp_file in enumerate(bmp_files):
        bmp_path = os.path.join(bmp_dir, bmp_file)
        svg_file = bmp_file.replace('.bmp', '.svg')
        svg_path = os.path.join(svg_dir, svg_file)
        
        try:
            # 使用potrace转换，优化参数用于BAS系统
            subprocess.run([
                'potrace', 
                bmp_path,
                '-s',  # SVG输出
                '-W', f'{target_width}pt',  # 设置宽度
                '-H', f'{target_height}pt',  # 设置高度
                '--flat',  # 使用平坦路径，减少复杂性
                '--opttolerance', '0.8',  # 增加容差，简化路径
                '--turnpolicy', 'minority',  # 减少转折点
                '-o', svg_path
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {bmp_file}: {e}")
            continue
        
        if (i + 1) % 50 == 0 or i == total - 1:  # 更频繁的进度更新
            print(f"Converted {i + 1}/{total} files to SVG")
    
    return len([f for f in os.listdir(svg_dir) if f.endswith('.svg')])

def extract_path_data(svg_file):
    """从SVG文件中提取路径数据"""
    try:
        doc = minidom.parse(svg_file)
        paths = doc.getElementsByTagName('path')
        if paths and len(paths) > 0:
            return paths[0].getAttribute('d')
    except Exception as e:
        print(f"Error parsing {svg_file}: {e}")
    return ""

def extract_svg_paths(svg_dir, output_json):
    """从SVG文件中提取所有路径数据并保存为JSON"""
    print("Extracting path data from SVG files...")
    
    svg_files = sorted([f for f in os.listdir(svg_dir) if f.endswith('.svg')])
    path_data = []
    total = len(svg_files)
    
    for i, svg_file in enumerate(svg_files):
        svg_path = os.path.join(svg_dir, svg_file)
        path_d = extract_path_data(svg_path)
        path_data.append(path_d)
        
        if (i + 1) % 100 == 0 or i == total - 1:
            print(f"Processed {i + 1}/{total} SVG files")
    
    # 保存为JSON
    with open(output_json, 'w') as f:
        json.dump(path_data, f, separators=(',', ':'))  # 紧凑格式
    
    print(f"Saved {len(path_data)} path data entries to {output_json}")
    return len(path_data)

def video_to_svg_animation(video_path, output_json, fps=5, size=(480, 360), keep_temp=False):
    """完整的视频转SVG动画流程，优化用于BAS弹幕系统"""
    
    if not check_dependencies():
        return False
    
    print(f"🎯 Optimizing for BAS playback: {fps}fps, {size[0]}x{size[1]}")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix='bas_svg_animation_')
    bmp_dir = os.path.join(temp_dir, 'bmp')
    svg_dir = os.path.join(temp_dir, 'svg')
    
    os.makedirs(bmp_dir)
    os.makedirs(svg_dir)
    
    try:
        print(f"Working in temporary directory: {temp_dir}")
        
        # 步骤1: 提取视频帧 (5fps for BAS)
        frame_count = extract_frames_with_opencv(video_path, bmp_dir, fps, size)
        
        # 步骤2: 转换为SVG (优化用于BAS)
        svg_count = convert_bmp_to_svg(bmp_dir, svg_dir, target_width=4800, target_height=3600)
        
        # 步骤3: 提取路径数据
        path_count = extract_svg_paths(svg_dir, output_json)
        
        # BAS优化统计
        estimated_duration = frame_count / fps
        print(f"\n🎉 BAS-optimized conversion completed!")
        print(f"✓ Processed {frame_count} frames at {fps}fps")
        print(f"✓ Generated {svg_count} SVG files")
        print(f"✓ Extracted {path_count} path data entries")
        print(f"✓ Estimated playback duration: {estimated_duration:.1f}s")
        print(f"✓ Output saved to: {os.path.abspath(output_json)}")
        print(f"📺 Ready for BAS弹幕 deployment!")
        
        return True
        
    except Exception as e:
        print(f"Error during processing: {e}")
        return False
        
    finally:
        # 清理临时文件
        if not keep_temp:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary files")
        else:
            print(f"Temporary files kept at: {temp_dir}")
            print(f"Debug: Check {bmp_dir} for frames and {svg_dir} for SVGs")

def main():
    parser = argparse.ArgumentParser(description="Convert video to SVG animation JSON data")
    parser.add_argument("input", help="Input video file path")
    parser.add_argument("-o", "--output", default="pathdata.json", help="Output JSON file path")
    parser.add_argument("--fps", type=int, default=5, help="Output frame rate (default: 5 for BAS)")
    parser.add_argument("--size", default="480x360", help="Output size as WIDTHxHEIGHT (default: 480x360)")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files for debugging")
    
    args = parser.parse_args()
    
    # 解析尺寸
    try:
        width, height = map(int, args.size.split('x'))
        size = (width, height)
    except ValueError:
        print("Invalid size format. Use WIDTHxHEIGHT (e.g., 480x360)")
        return 1
    
    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        return 1
    
    # 执行转换
    success = video_to_svg_animation(
        args.input, 
        args.output, 
        fps=args.fps, 
        size=size, 
        keep_temp=args.keep_temp
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
