# deepseek

import requests
import os
import time
import re
import hashlib
import threading
from queue import Queue
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CrawlResult:
    """爬取结果"""

    url: str
    success: bool
    filename: Optional[str] = None
    filepath: Optional[str] = None
    content_length: int = 0
    error_msg: Optional[str] = None


def sanitize_filename(url: str) -> str:
    """
    清理URL生成安全的文件名

    Args:
        url: 网址

    Returns:
        安全的文件名
    """
    # 移除协议和特殊字符
    safe_name = re.sub(r'https?://', '', url)
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', safe_name)
    # safe_name = safe_name[:30]  # 限制长度

    # 如果包含特殊字符，使用MD5哈希
    if any(ord(c) > 127 for c in safe_name) or len(safe_name) < 5:
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
        safe_name = f"page_{url_hash}"

    return f"{safe_name}.html"


class WebCrawlerThread(threading.Thread):
    """爬虫工作线程"""

    def __init__(
        self,
        thread_id: int,
        url_queue: Queue,
        result_queue: Queue,
        save_dir: str,
        timeout: int = 10,
        max_retries: int = 2,
    ) -> None:
        """
        初始化工作线程

        Args:
            thread_id: 线程ID
            url_queue: URL队列
            result_queue: 结果队列
            save_dir: 保存目录
            timeout: 超时时间
            max_retries: 最大重试次数
        """
        super().__init__()
        self.thread_id = thread_id
        self.url_queue = url_queue
        self.result_queue = result_queue
        self.save_dir = save_dir
        self.timeout = timeout
        self.max_retries = max_retries

        # 创建会话
        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
        )

    def run(self) -> None:
        """线程运行函数"""
        while not self.url_queue.empty():
            try:
                url = self.url_queue.get_nowait()
            except:
                break  # 队列为空，退出线程

            result = self.crawl_single(url)
            self.result_queue.put(result)
            self.url_queue.task_done()

        # 线程结束，关闭会话
        self.session.close()

    def crawl_single(self, url: str) -> CrawlResult:
        """
        爬取单个URL

        Args:
            url: 目标URL

        Returns:
            爬取结果
        """
        for retry in range(self.max_retries + 1):
            try:
                # 发送请求
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # 自动检测编码
                response.encoding = response.apparent_encoding

                # 生成安全的文件名
                filename = sanitize_filename(url)
                filepath = os.path.join(self.save_dir, filename)

                # 保存HTML内容
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)

                return CrawlResult(
                    url=url,
                    success=True,
                    filename=filename,
                    filepath=filepath,
                    content_length=len(response.text),
                )

            except requests.exceptions.RequestException as e:
                if retry < self.max_retries:
                    time.sleep(1)  # 重试前等待1秒
                    continue

                return CrawlResult(url=url, success=False, error_msg=f"请求失败: {e}")
            except Exception as e:
                return CrawlResult(url=url, success=False, error_msg=f"保存失败: {e}")

        return CrawlResult(url=url, success=False, error_msg="达到最大重试次数")


class MultiThreadCrawler:
    """多线程爬虫"""

    def __init__(
        self,
        save_dir: str = "html_pages",
        max_threads: int = 5,
        timeout: int = 10,
        max_retries: int = 2,
    ) -> None:
        """
        初始化爬虫

        Args:
            save_dir: 保存目录
            max_threads: 最大线程数
            timeout: 超时时间
            max_retries: 最大重试次数
        """
        self.save_dir = save_dir
        self.max_threads = max_threads
        self.timeout = timeout
        self.max_retries = max_retries

        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)

    def crawl_urls(self, urls: List[str]) -> List[CrawlResult]:
        """
        多线程爬取URL列表

        Args:
            urls: URL列表

        Returns:
            爬取结果列表
        """
        print(f"🚀 开始多线程爬取 {len(urls)} 个网页...")
        print(f"📊 线程数: {self.max_threads}")
        print(f"📁 保存目录: {os.path.abspath(self.save_dir)}")
        print("-" * 60)

        # 创建队列
        url_queue = Queue()
        result_queue = Queue()

        # 将URL加入队列
        for url in urls:
            url_queue.put(url)

        # 记录开始时间
        start_time = time.time()

        # 创建并启动工作线程
        threads: List[WebCrawlerThread] = []

        for i in range(min(self.max_threads, len(urls))):
            thread = WebCrawlerThread(
                thread_id=i + 1,
                url_queue=url_queue,
                result_queue=result_queue,
                save_dir=self.save_dir,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
            thread.start()
            threads.append(thread)
            print(f"📡 启动线程 {i + 1}")

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 收集结果
        results: List[CrawlResult] = []
        while not result_queue.empty():
            results.append(result_queue.get())

        # 计算统计信息
        elapsed_time = time.time() - start_time
        success_count = sum(1 for r in results if r.success)

        # 打印结果
        print("\n" + "=" * 60)
        print("🎉 爬取完成！")
        print("=" * 60)
        print(f"📈 总网页数: {len(urls)}")
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {len(urls) - success_count}")
        print(f"⏱️  耗时: {elapsed_time:.2f}秒")
        print(
            f"⚡ 平均速度: {len(urls)/elapsed_time:.2f}个/秒"
            if elapsed_time > 0
            else "计算中..."
        )

        # 显示结果摘要
        self.print_results_summary(results)

        return results

    def print_results_summary(self, results: List[CrawlResult]) -> None:
        """打印结果摘要"""
        print("\n📋 结果摘要:")
        print("-" * 40)

        for i, result in enumerate(results, 1):
            status = "✅" if result.success else "❌"
            size_info = (
                f"({result.content_length}字符)" if result.content_length > 0 else ""
            )
            print(f"{i:3d}. {status} {result.url[:50]:50} {size_info}")

            if not result.success and result.error_msg:
                print(f"    错误: {result.error_msg}")

    def save_report(self, results: List[CrawlResult]) -> None:
        """保存爬取报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.save_dir, f"crawl_report_{timestamp}.txt")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("网页爬取报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"线程数: {self.max_threads}\n")
            f.write(f"保存目录: {os.path.abspath(self.save_dir)}\n\n")

            f.write("详细结果:\n")
            f.write("-" * 60 + "\n")

            for i, result in enumerate(results, 1):
                status = "成功" if result.success else "失败"
                f.write(f"\n{i}. URL: {result.url}\n")
                f.write(f"   状态: {status}\n")

                if result.success:
                    f.write(f"   文件名: {result.filename}\n")
                    f.write(f"   文件大小: {result.content_length} 字符\n")
                else:
                    f.write(f"   错误: {result.error_msg}\n")

        print(f"\n📄 报告已保存: {report_file}")


def load_urls_from_file(filename: str) -> List[str]:
    """
    从文件加载URL列表

    Args:
        filename: 文件名

    Returns:
        URL列表
    """
    urls: List[str] = []

    if not os.path.exists(filename):
        print(f"⚠️ 文件不存在: {filename}")
        return urls

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # 跳过空行和注释
                    # 确保URL有协议前缀
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    urls.append(url)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

    return urls


def main() -> None:
    """主函数"""
    import sys

    print("=" * 60)
    print("🌐 多线程网页爬取工具")
    print("=" * 60)

    # 配置参数
    max_threads = 5
    save_dir = "html_pages"

    # 从命令行参数获取配置
    if len(sys.argv) > 1:
        max_threads = int(sys.argv[1])
    if len(sys.argv) > 2:
        save_dir = sys.argv[2]

    # 获取URL列表
    urls: List[str] = []

    # 方法1: 从文件读取
    if os.path.exists("urls.txt"):
        print("📁 从 urls.txt 文件加载URL...")
        urls = load_urls_from_file("urls.txt")

    # 方法2: 如果没有文件，使用示例URL
    if not urls:
        print("ℹ️  使用示例URL列表")
        urls = ['https://www.baidu.com', 'https://www.bilibili.com']

    if not urls:
        print("❌ 没有要爬取的URL")
        return

    print(f"📄 准备爬取 {len(urls)} 个网页")

    # 创建爬虫
    crawler = MultiThreadCrawler(
        save_dir=save_dir, max_threads=max_threads, timeout=10, max_retries=1
    )

    # 开始爬取
    results = crawler.crawl_urls(urls)

    # 保存报告
    crawler.save_report(results)


if __name__ == "__main__":
    main()
