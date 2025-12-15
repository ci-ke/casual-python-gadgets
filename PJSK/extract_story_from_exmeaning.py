# deepseek

import os
import json
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Dict, List, Optional, Any, Tuple
import re


def extract_event_info_from_html(html_content: str) -> Dict[str, Any]:
    """从HTML内容中提取活动信息并返回JSON格式数据

    Args:
        html_content: HTML内容字符串

    Returns:
        Dict[str, Any]: 提取的活动信息（JSON格式）
    """
    soup: BeautifulSoup = BeautifulSoup(html_content, 'html.parser')

    # 提取基本信息
    event_info: Dict[str, Any] = {
        'title': '',
        'title_jp': '',
        'event_id': '',
        'summary': '',
        'plot_summary': '',
        'chapters': [],
    }

    # 提取标题和ID
    title_element: Optional[Tag] = soup.find('h1', class_='event-title')
    if title_element:
        event_info['title'] = title_element.get_text(strip=True)

    title_jp_element: Optional[Tag] = soup.find('p', class_='event-title-jp')
    if title_jp_element:
        event_info['title_jp'] = title_jp_element.get_text(strip=True)

    event_id_element: Optional[Tag] = soup.find('div', class_='event-id-badge')
    if event_id_element:
        event_info['event_id'] = event_id_element.get_text(strip=True)

    # 提取活动概要和剧情总结
    info_cards: List[Tag] = soup.find_all('div', class_='event-info-card')
    for card in info_cards:
        # 活动概要
        summary_title: Optional[Tag] = card.find('h2', class_='info-title')
        if summary_title and '活动概要' in summary_title.get_text():
            summary_content: Optional[Tag] = summary_title.find_next_sibling('p')
            if summary_content:
                event_info['summary'] = summary_content.get_text(strip=True)

        # 剧情总结
        plot_summary_section: Optional[Tag] = card.find('div', class_='info-summary')
        if plot_summary_section:
            plot_content: Optional[Tag] = plot_summary_section.find('p')
            if plot_content:
                event_info['plot_summary'] = plot_content.get_text(strip=True)

    # 提取章节信息
    chapters_section: Optional[Tag] = soup.find('div', class_='chapters-list')
    if chapters_section:
        chapter_cards: List[Tag] = chapters_section.find_all(
            'div', class_='chapter-card'
        )

        for chapter_card in chapter_cards:
            chapter_info: Dict[str, str] = {
                'chapter_number': '',
                'chapter_title': '',
                'chapter_title_jp': '',
                'chapter_summary': '',
            }

            # 章节编号
            number_element: Optional[Tag] = chapter_card.find(
                'div', class_='chapter-number'
            )
            if number_element:
                chapter_info['chapter_number'] = number_element.get_text(strip=True)

            # 章节内容
            content_element: Optional[Tag] = chapter_card.find(
                'div', class_='chapter-content'
            )
            if content_element:
                # 章节标题
                title_element: Optional[Tag] = content_element.find(
                    'h3', class_='chapter-title'
                )
                if title_element:
                    chapter_info['chapter_title'] = title_element.get_text(strip=True)

                # 日文标题
                title_jp_element: Optional[Tag] = content_element.find(
                    'span', class_='chapter-title-jp'
                )
                if title_jp_element:
                    chapter_info['chapter_title_jp'] = title_jp_element.get_text(
                        strip=True
                    )

                # 章节摘要
                summary_element: Optional[Tag] = content_element.find(
                    'p', class_='chapter-summary'
                )
                if summary_element:
                    chapter_info['chapter_summary'] = summary_element.get_text(
                        strip=True
                    )

            event_info['chapters'].append(chapter_info)

    return event_info


def json_to_txt(json_data: Dict[str, Any]) -> str:
    """将JSON数据转换为易读的TXT格式

    Args:
        json_data: 活动信息的JSON数据

    Returns:
        str: 格式化的TXT内容
    """
    content_parts: List[str] = []

    # 标题部分
    content_parts.append(f"活动标题: {json_data.get('title', '')}")
    content_parts.append(f"日文标题: {json_data.get('title_jp', '')}")
    content_parts.append(f"活动ID: {json_data.get('event_id', '')}")
    content_parts.append("=" * 50)
    content_parts.append("")

    # 活动概要
    content_parts.append("📋 活动概要")
    content_parts.append(json_data.get('summary', ''))
    content_parts.append("")

    # 剧情总结
    content_parts.append("📝 剧情总结")
    content_parts.append(json_data.get('plot_summary', ''))
    content_parts.append("")
    content_parts.append("=" * 50)
    content_parts.append("")

    # 章节列表
    content_parts.append("📖 章节列表")
    content_parts.append("")

    for chapter in json_data.get('chapters', []):
        content_parts.append(f"第{chapter.get('chapter_number', '')}章")
        content_parts.append(f"标题: {chapter.get('chapter_title', '')}")
        content_parts.append(f"日文标题: {chapter.get('chapter_title_jp', '')}")
        content_parts.append("内容概要:")
        content_parts.append(chapter.get('chapter_summary', ''))
        content_parts.append("-" * 30)
        content_parts.append("")

    return '\n'.join(content_parts)


def generate_filename_from_json(json_data: Dict[str, Any]) -> str:
    """根据JSON数据生成文件名

    Args:
        json_data: 活动信息的JSON数据

    Returns:
        str: 生成的文件名（不含扩展名）
    """
    event_id: str = json_data.get('event_id', '').replace('#', '')
    title: str = json_data.get('title', '')

    if event_id and title:
        filename = f"event_{event_id}_{title}"
    elif event_id:
        filename = f"event_{event_id}"
    elif title:
        filename = f"event_{title}"
    else:
        filename = "unknown_event"

    # 清理文件名中的非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename


def process_single_html_file(
    html_file_path: str, output_dir: str = "txt_output"
) -> Tuple[str, Dict[str, Any]]:
    """处理单个HTML文件并保存为TXT

    Args:
        html_file_path: HTML文件路径
        output_dir: TXT输出目录

    Returns:
        Tuple[str, str]: (生成的TXT文件路径, 提取的JSON数据)
    """
    # 读取HTML文件
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content: str = file.read()

    # 提取信息为JSON格式
    json_data: Dict[str, Any] = extract_event_info_from_html(html_content)

    # 转换为TXT格式
    txt_content: str = json_to_txt(json_data)

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 生成文件名
    filename: str = generate_filename_from_json(json_data)
    txt_path: str = os.path.join(output_dir, f"{filename}.txt")

    # 保存TXT文件
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(txt_content)

    return txt_path, json_data


def process_all_html_files(
    html_folder: str, output_dir: str = "txt_output"
) -> Dict[str, Any]:
    """处理文件夹中的所有HTML文件

    Args:
        html_folder: HTML文件所在文件夹
        output_dir: TXT输出目录

    Returns:
        Dict[str, Any]: 包含所有处理结果的汇总信息
    """
    if not os.path.exists(html_folder):
        raise FileNotFoundError(f"HTML文件夹不存在: {html_folder}")

    # 汇总信息
    summary: Dict[str, Any] = {
        'processed_files': 0,
        'successful_files': 0,
        'failed_files': 0,
        'file_details': [],
        'all_json_data': {},  # 如果需要保存所有JSON数据
    }

    # 处理每个HTML文件
    for filename in os.listdir(html_folder):
        if filename.endswith('.html'):
            html_path: str = os.path.join(html_folder, filename)
            summary['processed_files'] += 1

            try:
                txt_path, json_data = process_single_html_file(html_path, output_dir)
                summary['successful_files'] += 1
                summary['file_details'].append(
                    {
                        'html_file': filename,
                        'txt_file': os.path.basename(txt_path),
                        'title': json_data.get('title', ''),
                        'event_id': json_data.get('event_id', ''),
                    }
                )
                summary['all_json_data'][filename] = json_data

                print(f"✓ 已处理: {filename} -> {os.path.basename(txt_path)}")

            except Exception as e:
                summary['failed_files'] += 1
                print(f"✗ 处理文件 {filename} 时出错: {e}")

    return summary


def main() -> None:
    """主函数"""
    # 配置路径
    html_folder: str = "html_pages"
    txt_output_dir: str = "txt_output"

    try:
        print("开始处理HTML文件...")
        summary: Dict[str, Any] = process_all_html_files(html_folder, txt_output_dir)

        print(f"\n处理完成!")
        print(f"共处理 {summary['processed_files']} 个文件")
        print(f"成功: {summary['successful_files']} 个")
        print(f"失败: {summary['failed_files']} 个")
        print(f"TXT文件保存在: {txt_output_dir}")

        # 可选：保存汇总信息
        summary_path: str = os.path.join(txt_output_dir, "processing_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"处理汇总保存在: {summary_path}")

    except Exception as e:
        print(f"处理过程中出错: {e}")


# 单独使用示例
if __name__ == "__main__":
    # 处理单个文件的示例
    # txt_path, json_data = process_single_html_file("html_pages/event_1.html")
    # print(f"生成文件: {txt_path}")

    # 处理所有文件的示例
    main()
