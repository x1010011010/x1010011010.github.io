"""
将SVG路径数据转换为BAS弹幕代码
根据JSON文件生成对应的BAS path函数序列
"""

import json
import argparse

def convert_to_bas_code(json_file, output_file="video.bas", fps=5):
    """将JSON中的SVG路径数据转换为BAS弹幕代码"""
    
    # 读取JSON数据
    with open(json_file, 'r') as f:
        path_data = json.load(f)
    
    print(f"读取到 {len(path_data)} 帧数据")
    
    # 生成BAS代码
    bas_code = []
    
    # 添加文件头注释
    bas_code.append("// BAS弹幕视频播放代码")
    bas_code.append(f"// 总帧数: {len(path_data)}")
    bas_code.append(f"// 帧率: {fps}fps")
    bas_code.append(f"// 播放时长: {len(path_data)/fps:.1f}秒")
    bas_code.append("")
    
    frame_duration_ms = int(1000 / fps)  # 每帧持续时间（毫秒）
    frame_duration_s = f"{frame_duration_ms}ms"  # BAS格式的时间
    
    # 为每一帧生成代码
    valid_frame_count = 0  # 有效帧计数器
    
    for i, path_d in enumerate(path_data):
        if not path_d or path_d.strip() == "":
            continue  # 跳过空帧
        
        # 转义双引号
        escaped_path = path_d.replace('"', '\\"')
        
        # 计算时间 - 按照BAS格式，使用原始帧索引保持时间连续性
        frame_number = i + 1  # 保持原始帧编号
        start_time_ms = i * frame_duration_ms  # 使用原始索引计算开始时间
        total_duration_ms = (i + 1) * frame_duration_ms  # 使用原始索引计算累积时间
        valid_frame_count += 1
        
        # 生成let path定义
        bas_code.append(f'let p{frame_number} = path {{')
        bas_code.append(f'    d = "{escaped_path}"')
        bas_code.append(f'    viewBox = "0 0 1200 900"')
        bas_code.append(f'    width = 100%')
        bas_code.append(f'    duration = {total_duration_ms}ms')
        bas_code.append(f'    alpha = 0')
        bas_code.append(f'}}')
        # 生成时间控制
        bas_code.append(f'set p{frame_number} {{}} {start_time_ms}ms')
        bas_code.append(f'then set p{frame_number} {{alpha = 1}} 0ms')
        bas_code.append("")
        
        # 每50帧显示一次进度
        if valid_frame_count % 50 == 0:
            print(f"已处理 {valid_frame_count} 有效帧 (原始第{i+1}帧)")
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(bas_code))
    
    file_content = '\n'.join(bas_code)
    
    print(f"\n✅ BAS代码生成完成！")
    print(f"📁 输出文件: {output_file}")
    print(f"📊 统计信息:")
    print(f"   - 总帧数: {len(path_data)}")
    print(f"   - 有效帧数: {valid_frame_count}")
    print(f"   - 跳过空帧: {len(path_data) - valid_frame_count}")
    print(f"   - 帧率: {fps}fps ({frame_duration_ms}ms/帧)")
    print(f"   - 播放时长: {len(path_data)/fps:.1f}秒")
    print(f"   - 文件大小: {len(file_content)} 字符")
    print(f"💡 使用方法: 将生成的.bas文件导入到BAS弹幕系统中播放")

def create_optimized_bas(json_file, output_file="video_optimized.bas", fps=5, max_frames=None):
    """生成优化版本的BAS代码（可限制帧数）"""
    
    with open(json_file, 'r') as f:
        path_data = json.load(f)
    
    # 如果设置了最大帧数，则截取
    if max_frames and max_frames < len(path_data):
        path_data = path_data[:max_frames]
        print(f"⚠️  已截取前 {max_frames} 帧（原始总数更多）")
    
    print(f"准备生成优化的BAS代码...")
    
    frame_duration = int(1000 / fps)  # 每帧持续时间（毫秒）
    
    # 简化的BAS代码格式
    bas_lines = []
    bas_lines.append("// 优化版BAS弹幕视频")
    bas_lines.append(f"// 帧率: {fps}fps | 帧间隔: {frame_duration}ms")
    bas_lines.append("")
    
    non_empty_frames = 0
    for i, path_d in enumerate(path_data):
        if path_d and path_d.strip():
            non_empty_frames += 1
            start_time = i * frame_duration
            
            # 使用更简洁的格式
            escaped_path = path_d.replace('"', '\\"')
            
            bas_lines.append(f'let p{i} = path{{ d = "{escaped_path}" viewBox = "0 0 4800 3600" width = 100% duration = {frame_duration}ms alpha = 0 }}')
            bas_lines.append(f'set p{i} {{}} {start_time}ms')
            bas_lines.append(f'then set p{i} {{alpha = 1}} 0ms')
            bas_lines.append("")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(bas_lines))
    
    file_content = '\n'.join(bas_lines)
    
    print(f"\n✅ 优化版BAS代码生成完成！")
    print(f"📁 输出文件: {output_file}")
    print(f"🎯 优化统计:")
    print(f"   - 有效帧数: {non_empty_frames}/{len(path_data)}")
    print(f"   - 播放时长: {len(path_data)/fps:.1f}秒")
    print(f"   - 文件大小: {len(file_content)} 字符")
    print(f"   - 压缩率: {((len(path_data)-non_empty_frames)/len(path_data)*100):.1f}%")

def main():
    parser = argparse.ArgumentParser(description="将SVG路径JSON转换为BAS弹幕代码")
    parser.add_argument("json_file", help="输入的JSON文件路径")
    parser.add_argument("-o", "--output", default="video.bas", help="输出的BAS文件路径")
    parser.add_argument("--fps", type=int, default=5, help="播放帧率 (默认: 5)")
    parser.add_argument("--max-frames", type=int, help="最大帧数限制")
    parser.add_argument("--optimized", action="store_true", help="生成优化版本（跳过空帧）")
    
    args = parser.parse_args()
    
    if args.optimized:
        create_optimized_bas(args.json_file, args.output, args.fps, args.max_frames)
    else:
        convert_to_bas_code(args.json_file, args.output, args.fps)

if __name__ == "__main__":
    main()
