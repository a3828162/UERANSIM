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

from aioquic.asyncio.client import connect
from aioquic.h3.connection import H3_ALPN
from aioquic.quic.configuration import QuicConfiguration

# 重用 http3_client 中的 HttpClient
import sys
sys.path.insert(0, os.path.dirname(__file__))
from http3_client import HttpClient

logger = logging.getLogger("yolo_client")


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
        nargs="+",
        help="要检测的图片文件路径（可以指定多个）",
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
        help="每张图片发送的次数（用于性能测试，默认: 1）",
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
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    
    # 检查图片文件是否存在
    for image_path in args.images:
        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return
    
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
    
    # 运行检测
    try:
        asyncio.run(
            batch_detection(
                configuration=configuration,
                server_host=args.host,
                server_port=args.port,
                image_paths=args.images,
                endpoint=args.endpoint,
                iterations=args.iterations,
            )
        )
    except KeyboardInterrupt:
        logger.info("\n用户中断")


if __name__ == "__main__":
    main()
