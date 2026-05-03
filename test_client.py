"""
NapCat Group Info MCP Server - 测试脚本
用于测试 MCP 服务器是否正常工作
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加 src 目录到路径
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from napcat_client import NapCatClient


async def test_napcat_client():
    """测试 NapCat 客户端"""
    print("=" * 60)
    print("NapCat Group Info MCP Server - 测试脚本")
    print("=" * 60)

    # 从环境变量读取配置
    host = os.getenv("NAPCAT_HOST", "http://localhost:3000")
    token = os.getenv("NAPCAT_TOKEN", "")

    print(f"\n配置信息:")
    print(f"  NapCat Host: {host}")
    print(f"  Token: {'已设置' if token else '未设置'}")

    try:
        async with NapCatClient(host=host, token=token) as client:
            print("\n" + "=" * 60)
            print("测试 1: 获取群列表")
            print("=" * 60)
            groups = await client.get_group_list()
            print(f"✓ 成功获取到 {len(groups)} 个群")
            for i, group in enumerate(groups[:5], 1):
                print(f"  {i}. {group.get('group_name', 'Unknown')} (ID: {group.get('group_id')})")
            if len(groups) > 5:
                print(f"  ... 还有 {len(groups) - 5} 个群")

            if not groups:
                print("\n⚠️  没有找到任何群，无法继续测试")
                return

            # 使用第一个群进行测试
            test_group_id = groups[0].get('group_id')
            print(f"\n使用群 {test_group_id} 进行后续测试...")

            print("\n" + "=" * 60)
            print("测试 2: 获取群详细信息")
            print("=" * 60)
            group_info = await client.get_group_info(test_group_id)
            print(f"✓ 群名称: {group_info.get('group_name')}")
            print(f"✓ 群成员数: {group_info.get('member_count')}")
            print(f"✓ 群主: {group_info.get('owner_id')}")

            print("\n" + "=" * 60)
            print("测试 3: 获取群成员列表")
            print("=" * 60)
            members = await client.get_group_member_list(test_group_id)
            print(f"✓ 成功获取到 {len(members)} 个成员")
            for i, member in enumerate(members[:5], 1):
                print(f"  {i}. {member.get('nickname', 'Unknown')} (ID: {member.get('user_id')})")
            if len(members) > 5:
                print(f"  ... 还有 {len(members) - 5} 个成员")

            print("\n" + "=" * 60)
            print("测试 4: 获取群荣誉信息")
            print("=" * 60)
            honor_info = await client.get_group_honor_info(test_group_id, type="all")
            print(f"✓ 成功获取群荣誉信息")
            if honor_info:
                print(f"  数据: {honor_info}")

            print("\n" + "=" * 60)
            print("测试 5: 获取群@全体成员剩余次数")
            print("=" * 60)
            at_all_remain = await client.get_group_at_all_remain(test_group_id)
            print(f"✓ 成功获取@全体成员剩余次数")
            if at_all_remain:
                print(f"  数据: {at_all_remain}")

            print("\n" + "=" * 60)
            print("测试 6: 获取群文件系统信息")
            print("=" * 60)
            file_system_info = await client.get_group_file_system_info(test_group_id)
            print(f"✓ 成功获取群文件系统信息")
            if file_system_info:
                print(f"  数据: {file_system_info}")

            print("\n" + "=" * 60)
            print("测试 7: 获取群根目录文件列表")
            print("=" * 60)
            root_files = await client.get_group_root_files(test_group_id)
            print(f"✓ 成功获取群根目录文件列表")
            if root_files:
                files = root_files.get('files', [])
                folders = root_files.get('folders', [])
                print(f"  文件数: {len(files)}")
                print(f"  文件夹数: {len(folders)}")
                if files:
                    print(f"  文件示例:")
                    for i, file in enumerate(files[:3], 1):
                        print(f"    {i}. {file.get('file_name')}")

            print("\n" + "=" * 60)
            print("测试 8: 获取群历史消息")
            print("=" * 60)
            msg_history = await client.get_group_msg_history(test_group_id, count=10)
            print(f"✓ 成功获取群历史消息")
            if msg_history:
                messages = msg_history.get('messages', [])
                print(f"  消息数: {len(messages)}")
                if messages:
                    print(f"  最新消息预览:")
                    for i, msg in enumerate(messages[:3], 1):
                        sender = msg.get('sender', {}).get('nickname', 'Unknown')
                        content = str(msg.get('content', ''))[:50]
                        print(f"    {i}. {sender}: {content}...")

            print("\n" + "=" * 60)
            print("✅ 所有测试完成!")
            print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n提示: 请确保已设置环境变量 NAPCAT_HOST 和 NAPCAT_TOKEN")
    print("或者在运行前加载 .env 文件: export $(cat .env | xargs)\n")

    asyncio.run(test_napcat_client())
