import logging
import os
from datetime import datetime

def setup_logging(log_dir="/app/logs", log_level=logging.INFO):
    """
    配置日志系统
    
    Args:
        log_dir: 日志目录路径
        log_level: 日志级别
    """
    # 获取环境变量，判断是否为生产环境
    env = os.getenv("ENV", "dev").lower()
    is_prod = env in ("prod", "production")
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 处理器列表
    handlers = []
    
    # 始终添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    handlers.append(console_handler)
    
    # 仅在生产环境添加文件处理器
    if is_prod:
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名（按日期）
        log_file = os.path.join(log_dir, f"mcp_server_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 添加文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    # 返回日志记录器
    logger = logging.getLogger('mcp_server')
    if is_prod:
        logger.info(f"生产环境 - 日志输出到文件和控制台")
        logger.info(f"日志文件: {log_file}")
    else:
        logger.info(f"开发环境 - 日志仅输出到控制台")
    
    return logger
