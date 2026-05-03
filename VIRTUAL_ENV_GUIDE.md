# NapCat Group Info MCP 虚拟环境使用指南

## 问题回顾
用户最初遇到 `ModuleNotFoundError: No module named 'mcp'` 错误，这是因为项目依赖的 `mcp` 包未在系统Python环境中安装。

## 解决方案实施

### 已完成的安装步骤
1. ✅ **创建虚拟环境**
   ```bash
   cd /home/a1/app/tools/napcat_group_info_mcp
   python3 -m venv venv
   ```

2. ✅ **激活虚拟环境并安装依赖**
   ```bash
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   pip install -e .
   ```

3. ✅ **验证安装**
   ```bash
   python -c "import mcp; print('mcp模块导入成功')"
   ```

## 为什么需要虚拟环境

### 核心原因
1. **依赖隔离**：项目需要特定的 `mcp` 包（版本 >=1.0.0）
2. **避免冲突**：系统环境可能已有其他版本的 `httpx`、`pydantic` 等包
3. **项目独立性**：确保NapCat MCP服务器有自己的运行环境

### 技术验证
- 系统环境：缺少 `mcp` 包，导致 `ModuleNotFoundError`
- 虚拟环境：包含所有必要依赖，可以正常运行

## 使用方法

### 每次使用前
```bash
cd /home/a1/app/tools/napcat_group_info_mcp
source venv/bin/activate  # 激活虚拟环境
```

### 运行项目
```bash
# 方式1：直接运行
python run_direct.py

# 方式2：使用启动脚本
./start.sh  # Linux/Mac
start.bat   # Windows

# 方式3：作为模块运行
python -m napcat_group_info_mcp
```

### 退出虚拟环境
```bash
deactivate
```

## 环境配置

### 重要环境变量
在虚拟环境中设置：
```bash
export NAPCAT_HOST=http://localhost:3000
export NAPCAT_TOKEN=your_token_here
export ALLOWED_GROUPS=628101497
```

或创建 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env 文件配置你的NapCat服务器
```

## 虚拟环境管理

### 查看已安装包
```bash
pip list
```

### 更新依赖
```bash
pip install --upgrade -e .
```

### 删除虚拟环境
```bash
rm -rf venv/
```

## 故障排除

### 问题1：激活虚拟环境后命令找不到
```bash
# 确保使用正确的激活命令
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows PowerShell
```

### 问题2：依赖安装失败
```bash
# 使用国内镜像源
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：权限问题
```bash
# 确保有执行权限
chmod +x start.sh
chmod +x venv/bin/python
```

## 项目结构说明
```
napcat_group_info_mcp/
├── venv/                    # 虚拟环境目录（已创建）
├── src/                     # 源代码
├── pyproject.toml          # 依赖配置
├── run_direct.py           # 直接运行脚本
├── start.sh                # Linux启动脚本
├── start.bat               # Windows启动脚本
└── VIRTUAL_ENV_GUIDE.md    # 本指南
```

## 总结

虚拟环境成功解决了原始问题：
1. **隔离了项目依赖**，避免与系统环境冲突
2. **安装了必需的 `mcp` 包**，消除了 `ModuleNotFoundError`
3. **提供了可重复的环境**，确保项目在任何机器上都能一致运行

现在你可以正常使用 NapCat Group Info MCP 服务器了！