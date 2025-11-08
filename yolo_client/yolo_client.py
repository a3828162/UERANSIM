#!/usr/bin/env python3
"""
YOLO Detection Client - 发送图片到服务器进行物体检测
"""

import argparse
import asyncio
import json
import logging
import os
import ssl
import time
from pathlib import Path
from typing import Optional
from datetime import datetime
import csv

from aioquic.asyncio.client import connect
from aioquic.h3.connection import H3_ALPN
from aioquic.quic.configuration import QuicConfiguration

# 重用 http3_client 中的 HttpClient
import sys
sys.path.insert(0, os.path.dirname(__file__))
from http3_client import HttpClient

logger = logging.getLogger("yolo_client")

import paho.mqtt.client as mqtt

# ===== 參數設定 =====
MQTT_BROKER = "140.113.208.76"  # Broker IP
MQTT_PORT = 1883

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 300)

ROOT = os.path.dirname(__file__)
print("[INFO] 伺服器根目錄:", ROOT)

# 檢查並創建 dataset 資料夾
DATASET_DIR = os.path.join(ROOT, "dataset")
if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)
    print(f"[INFO] 已創建 dataset 資料夾: {DATASET_DIR}")
else:
    print(f"[INFO] dataset 資料夾已存在: {DATASET_DIR}")


async def send_image_for_detection(
    client: HttpClient,
    image_path: str,
    server_url: str,
) -> dict:
    """
    发送图片到服务器进行 YOLO 检测
    
    Args:
        client: HTTP3 客户端
        image_path: 图片文件路径
        server_url: 服务器 URL (例如: https://localhost:4433/object-detect)
    
    Returns:
        检测结果字典
    """
    # 读取图片文件
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    file_size = len(image_data)
    logger.info(f"读取图片: {image_path} ({file_size} bytes)")
    
    # 发送 POST 请求
    start_time = time.time()
    
    http_events = await client.post(
        server_url,
        data=image_data,
        headers={
            "content-type": "image/jpeg",
            "content-length": str(file_size),
        },
    )
    
    elapsed = time.time() - start_time
    
    # 解析响应
    response_data = b""
    for event in http_events:
        if hasattr(event, 'data'):
            response_data += event.data
    
    # 解析 JSON 响应
    result = json.loads(response_data.decode())
    
    # 添加传输时间信息
    result["transfer_time"] = elapsed
    result["image_size_bytes"] = file_size
    result["throughput_mbps"] = (file_size * 8) / elapsed / 1_000_000
    # 获取 RTT 信息
    try:
        result["rtt_ms"] = client._quic._loss._rtt_latest * 1000
    except:
        result["rtt_ms"] = None
    
    return result


async def continuous_detection(
    configuration: QuicConfiguration,
    server_host: str,
    server_port: int,
    image_dir: str,
    endpoint: str = "/object-detect",
    interval: float = 1.0,
    max_requests: Optional[int] = None,
    ueid: Optional[str] = None,
) -> None:
    """
    持续从指定目录读取图片并每秒发送进行检测
    
    Args:
        configuration: QUIC 配置
        server_host: 服务器主机名
        server_port: 服务器端口
        image_dir: 图片目录路径
        endpoint: 检测端点路径
        interval: 发送间隔（秒），默认 1.0 秒
        max_requests: 最大请求数（None 表示无限循环）
    """
    edge_dic = {"140.113.208.76": "edge3", "192.168.113.50": "edge1", "192.168.113.60": "edge2"}

    server_url = f"https://{server_host}:{server_port}{endpoint}"

    now = datetime.now().timestamp()
    folder_path = os.path.join(ROOT, f"dataset/")
    print(folder_path)
    os.makedirs(folder_path, exist_ok=True) 

    # 扫描图片目录
    image_dir_path = Path(image_dir)
    if not image_dir_path.exists():
        logger.error(f"图片目录不存在: {image_dir}")
        return
    
    # 获取所有 jpg/jpeg/png 图片
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    image_paths = [
        str(p) for p in image_dir_path.iterdir()
        if p.suffix in image_extensions
    ]
    
    if not image_paths:
        logger.error(f"目录中没有找到图片文件: {image_dir}")
        return
    
    image_paths.sort()  # 排序以保证顺序一致
    logger.info(f"找到 {len(image_paths)} 张图片")
    
    async with connect(
        server_host,
        server_port,
        configuration=configuration,
        create_protocol=HttpClient,
    ) as client:
        client = client
        
        logger.info(f"已连接到服务器: {server_host}:{server_port}")
        logger.info(f"开始持续检测，每 {interval} 秒发送一张图片")
        if max_requests:
            logger.info(f"最大请求数: {max_requests}")
        else:
            logger.info("模式: 无限循环（按 Ctrl+C 停止）")
        
        all_results = []
        request_count = 0
        image_index = 0
        
        try:
            while True:
                # 检查是否达到最大请求数
                if max_requests and request_count >= max_requests:
                    logger.info(f"已达到最大请求数: {max_requests}")
                    break
                
                # 获取当前图片（循环使用）
                current_image = image_paths[image_index % len(image_paths)]
                request_count += 1
                
                try:
                    logger.info(f"\n[请求 #{request_count}] 处理图片: {Path(current_image).name}")
                    
                    loop_start = time.time()
                    
                    result = await send_image_for_detection(
                        client=client,
                        image_path=current_image,
                        server_url=server_url,
                    )
                    
                    # 打印结果
                    logger.info(f"✓ 检测完成!")
                    logger.info(f"  - 图片大小: {result['image_size_bytes'] / 1024:.2f} KB")
                    logger.info(f"  - 传输时间: {result['transfer_time']*1000:.2f} ms")
                    logger.info(f"  - 处理时间: {result.get('processing_time', 0)*1000:.2f} ms")
                    logger.info(f"  - 吞吐量: {result['throughput_mbps']:.2f} Mbps")
                    if result.get('rtt_ms'):
                        logger.info(f"  - RTT: {result['rtt_ms']:.2f} ms")
                    logger.info(f"  - 检测到 {len(result.get('detections', []))} 个物体")

                    expected_fields = [
                        "bitrate",
                        "packetlost",
                        "rtt",
                        "server",  # 新增 size 欄位
                    ]

                    data = {
                        "bitrate": result['throughput_mbps'] * 1000,  # 转换为 kbps
                        "packetlost": 0,  # 这里假设没有丢包信息
                        "rtt": result['transfer_time'] * 1000,  # 转换为 ms
                        "server": edge_dic.get(server_host, "unknown"),
                    }

                    topic = f"edge/performance/{ueid}"
                    mqtt_client.publish(topic, json.dumps(data))

                    # CSV 檔案路徑
                    csv_file = os.path.join(ROOT, f"dataset/performance_{ueid}.csv")
                    file_exists = os.path.exists(csv_file)

                    # print(f"[INFO] 將性能資料寫入 {csv_file}")
                    with open(csv_file, mode="a", newline="") as file:
                        writer = csv.DictWriter(file, fieldnames=expected_fields)
                        # print("[INFO] 寫入資料:", {field: data[field] for field in required_fields})
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow({field: data[field] for field in expected_fields})

                    all_results.append({
                        "request_num": request_count,
                        "image": current_image,
                        "timestamp": time.time(),
                        **result
                    })
                    
                    # 计算剩余等待时间
                    elapsed = time.time() - loop_start
                    wait_time = max(0, interval - elapsed)
                    
                    if wait_time > 0:
                        logger.debug(f"等待 {wait_time:.2f} 秒...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"处理时间 ({elapsed:.2f}s) 超过间隔 ({interval}s)")
                    
                except Exception as e:
                    logger.error(f"✗ 处理图片失败: {e}")
                
                image_index += 1
                
        except KeyboardInterrupt:
            logger.info("\n收到中断信号，正在停止...")
        
        # 打印统计信息
        if all_results:
            logger.info(f"\n{'='*60}")
            logger.info("统计信息")
            logger.info(f"{'='*60}")
            
            transfer_times = [r['transfer_time'] for r in all_results]
            throughputs = [r['throughput_mbps'] for r in all_results]
            processing_times = [r.get('processing_time', 0) for r in all_results]
            
            logger.info(f"总请求数: {len(all_results)}")
            logger.info(f"使用图片数: {len(set(r['image'] for r in all_results))}")
            
            if len(all_results) > 1:
                duration = all_results[-1]['timestamp'] - all_results[0]['timestamp']
                logger.info(f"总运行时间: {duration:.2f} 秒")
                logger.info(f"实际发送速率: {len(all_results) / duration:.2f} 请求/秒")
            
            logger.info(f"传输时间: 平均 {sum(transfer_times)/len(transfer_times)*1000:.2f} ms, "
                       f"最小 {min(transfer_times)*1000:.2f} ms, "
                       f"最大 {max(transfer_times)*1000:.2f} ms")
            logger.info(f"处理时间: 平均 {sum(processing_times)/len(processing_times)*1000:.2f} ms, "
                       f"最小 {min(processing_times)*1000:.2f} ms, "
                       f"最大 {max(processing_times)*1000:.2f} ms")
            logger.info(f"吞吐量: 平均 {sum(throughputs)/len(throughputs):.2f} Mbps, "
                       f"最小 {min(throughputs):.2f} Mbps, "
                       f"最大 {max(throughputs):.2f} Mbps")


async def batch_detection(
    configuration: QuicConfiguration,
    server_host: str,
    server_port: int,
    image_paths: list[str],
    endpoint: str = "/object-detect",
    iterations: int = 1,
) -> None:
    """
    批量发送图片进行检测
    
    Args:
        configuration: QUIC 配置
        server_host: 服务器主机名
        server_port: 服务器端口
        image_paths: 图片文件路径列表
        endpoint: 检测端点路径
        iterations: 每张图片发送的次数（用于性能测试）
    """
    server_url = f"https://{server_host}:{server_port}{endpoint}"
    
    async with connect(
        server_host,
        server_port,
        configuration=configuration,
        create_protocol=HttpClient,
    ) as client:
        client = client
        
        logger.info(f"已连接到服务器: {server_host}:{server_port}")
        logger.info(f"开始检测，共 {len(image_paths)} 张图片，每张 {iterations} 次")
        
        all_results = []
        
        for iteration in range(iterations):
            logger.info(f"\n{'='*60}")
            logger.info(f"迭代 {iteration + 1}/{iterations}")
            logger.info(f"{'='*60}")
            
            for idx, image_path in enumerate(image_paths, 1):
                try:
                    logger.info(f"\n处理图片 {idx}/{len(image_paths)}: {image_path}")
                    
                    result = await send_image_for_detection(
                        client=client,
                        image_path=image_path,
                        server_url=server_url,
                    )
                    
                    # 打印结果
                    logger.info(f"✓ 检测完成!")
                    logger.info(f"  - 图片大小: {result['image_size_bytes'] / 1024:.2f} KB")
                    logger.info(f"  - 传输时间: {result['transfer_time']*1000:.2f} ms")
                    logger.info(f"  - 处理时间: {result.get('processing_time', 0)*1000:.2f} ms")
                    logger.info(f"  - 吞吐量: {result['throughput_mbps']:.2f} Mbps")
                    if result.get('rtt_ms'):
                        logger.info(f"  - RTT: {result['rtt_ms']:.2f} ms")
                    logger.info(f"  - 检测到 {len(result.get('detections', []))} 个物体:")
                    
                    for detection in result.get('detections', []):
                        logger.info(
                            f"    • {detection['class']}: "
                            f"{detection['confidence']:.2%} "
                            f"@ {detection['bbox']}"
                        )
                    
                    all_results.append({
                        "iteration": iteration + 1,
                        "image": image_path,
                        **result
                    })
                    
                except Exception as e:
                    logger.error(f"✗ 处理图片失败: {e}")
        
        # 打印统计信息
        if all_results:
            logger.info(f"\n{'='*60}")
            logger.info("统计信息")
            logger.info(f"{'='*60}")
            
            transfer_times = [r['transfer_time'] for r in all_results]
            throughputs = [r['throughput_mbps'] for r in all_results]
            
            logger.info(f"总请求数: {len(all_results)}")
            logger.info(f"传输时间: 平均 {sum(transfer_times)/len(transfer_times)*1000:.2f} ms, "
                       f"最小 {min(transfer_times)*1000:.2f} ms, "
                       f"最大 {max(transfer_times)*1000:.2f} ms")
            logger.info(f"吞吐量: 平均 {sum(throughputs)/len(throughputs):.2f} Mbps, "
                       f"最小 {min(throughputs):.2f} Mbps, "
                       f"最大 {max(throughputs):.2f} Mbps")


def main():
    parser = argparse.ArgumentParser(
        description="HTTP/3 YOLO Detection Client - 发送图片进行物体检测"
    )
    parser.add_argument(
        "images",
        type=str,
        nargs="*",
        help="批量模式：要检测的图片文件路径（可以指定多个）",
    )
    parser.add_argument(        
        "--host",
        type=str,
        default="localhost",
        help="服务器主机名（默认: localhost）",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8443,
        help="服务器端口（默认: 8443）",
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="/object-detect",
        help="检测端点路径（默认: /object-detect）",
    )
    parser.add_argument(
        "--ca-certs",
        type=str,
        help="CA 证书文件路径",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="不验证服务器证书",
    )
    parser.add_argument(
        "-n",
        "--iterations",
        type=int,
        default=1,
        help="批量模式：每张图片发送的次数（用于性能测试，默认: 1）",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="详细日志输出",
    )
    parser.add_argument(
        "-q",
        "--quic-log",
        type=str,
        help="保存 QUIC 日志到指定目录",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="持续检测模式：从指定目录持续读取图片发送",
    )
    parser.add_argument(
        "--folder",
        type=str,
        help="持续模式：图片目录路径（例如: train2017）",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="持续模式：发送间隔秒数（默认: 1.0）",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        help="持续模式：最大请求数（默认: 无限循环）",
    )
    parser.add_argument(
        "--ueid",
        type=str,
        help="UE ID (for logging purposes only)"
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    
    # 配置 QUIC
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=H3_ALPN,
    )
    
    if args.ca_certs:
        configuration.load_verify_locations(args.ca_certs)
    
    if args.insecure:
        configuration.verify_mode = ssl.CERT_NONE
    
    if args.quic_log:
        from aioquic.quic.logger import QuicFileLogger
        configuration.quic_logger = QuicFileLogger(args.quic_log)
    # 判断运行模式
    if args.continuous:
        # 持续检测模式
        if not args.folder:
            logger.error("错误: 持续模式需要指定 --folder 参数")
            parser.print_help()
            return
        
        logger.info("=" * 60)
        logger.info("运行模式: 持续检测")
        logger.info(f"图片目录: {args.folder}")
        logger.info(f"发送间隔: {args.interval} 秒")
        logger.info(f"目标服务器: {args.host}:{args.port}")
        if args.max_requests:
            logger.info(f"最大请求数: {args.max_requests}")
        else:
            logger.info("模式: 无限循环（按 Ctrl+C 停止）")
        logger.info("=" * 60)
        
        try:
            asyncio.run(
                continuous_detection(
                    configuration=configuration,
                    server_host=args.host,
                    server_port=args.port,
                    image_dir=args.folder,
                    endpoint=args.endpoint,
                    interval=args.interval,
                    max_requests=args.max_requests,
                    ueid=args.ueid,
                )
            )
        except KeyboardInterrupt:
            logger.info("\n用户中断")
    else:
        # 批量检测模式
        if not args.images:
            logger.error("错误: 批量模式需要指定图片路径")
            parser.print_help()
            return
        
        # 检查图片文件是否存在
        for image_path in args.images:
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return
        
        logger.info("=" * 60)
        logger.info("运行模式: 批量检测")
        logger.info(f"图片数量: {len(args.images)}")
        logger.info(f"迭代次数: {args.iterations}")
        logger.info(f"目标服务器: {args.host}:{args.port}")
        logger.info("=" * 60)
        
        try:
            asyncio.run(
                batch_detection(
                    configuration=configuration,
                    server_host=args.host,
                    server_port=args.port,
                    image_paths=args.images,
                    endpoint=args.endpoint,
                    iterations=args.iterations,
                    ueid=args.ueid,
                )
            )
        except KeyboardInterrupt:
            logger.info("\n用户中断")


if __name__ == "__main__":
    main()
