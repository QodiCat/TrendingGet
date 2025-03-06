import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from secret import email_password
from utils.config import load_config

def send_email(date, filename):
    """
    发送邮件功能
    :param date: 日期
    :param filename: 文件名
    :return: 是否发送成功
    """
    # 读取配置
    config = load_config()
    email_config = config.get("email", {})
    
    # 检查是否启用邮件功能
    if not email_config.get("enable", False):
        print("邮件发送功能未启用")
        return False
    
    # 获取邮件配置
    sender = email_config.get("sender", "")
    password = email_password
    receiver = email_config.get("receiver", "")
    smtp_server = email_config.get("smtp_server", "")
    smtp_port = email_config.get("smtp_port", 465)
    
    # 检查配置是否完整
    if not all([sender, password, receiver, smtp_server]):
        print("邮件配置不完整，无法发送邮件")
        return False
    
    try:
        # 读取文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 将Markdown转换为HTML
        try:
            import markdown
            html_content = markdown.markdown(content)
        except ImportError:
            # 如果没有安装markdown库，进行简单的转换
            html_content = content.replace('\n', '<br>')
            html_content = html_content.replace('# ', '<h1>')
            html_content = html_content.replace('## ', '<h2>')
            html_content = html_content.replace('* ', '<li>')
            html_content = f'<html><body>{html_content}</body></html>'
        
        # 添加CSS样式，美化邮件内容
        css_style = """
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                font-size: 24px;
                text-align: center;
            }
            h2 {
                color: #2980b9;
                border-left: 4px solid #3498db;
                padding-left: 10px;
                margin-top: 30px;
                font-size: 20px;
                background-color: #eef7fa;
                padding: 8px 10px;
                border-radius: 3px;
            }
            ul {
                list-style-type: none;
                padding-left: 0;
            }
            li {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            li:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            a {
                color: #3498db;
                text-decoration: none;
                font-weight: bold;
                font-size: 16px;
            }
            a:hover {
                text-decoration: underline;
            }
            .stars {
                color: #f39c12;
                font-weight: bold;
                margin-left: 5px;
            }
            .description {
                color: #555;
                margin-top: 8px;
                padding-left: 10px;
                border-left: 3px solid #eee;
                font-size: 14px;
                line-height: 1.5;
            }
            .footer {
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #7f8c8d;
                border-top: 1px solid #ddd;
                padding-top: 10px;
            }
        </style>
        """
        
        # 处理HTML内容，添加样式和结构
        # 替换星星标记为带样式的星星
        html_content = html_content.replace('⭐', '<span class="stars">⭐</span>')
        
        # 为描述添加样式
        import re
        # 更新正则表达式以匹配新的markdown格式
        html_content = re.sub(r'(<li>.*?</a>.*?</span>)(.*?)(?=<li>|<\/ul>|$)', 
                             r'\1<div class="description">\2</div>', 
                             html_content)
        
        # 添加页脚
        footer = f"""
        <div class="footer">
            GitHub Trending 日报 - {date} - 自动生成
        </div>
        """
        
        # 组合完整的HTML
        full_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            {css_style}
        </head>
        <body>
            {html_content}
            {footer}
        </body>
        </html>
        """
        
        # 创建邮件对象
        message = MIMEMultipart()
        message['From'] = sender  # 简化From头部，只使用邮箱地址
        message['To'] = receiver
        subject = f'GitHub Trending 日报 ({date})'
        message['Subject'] = Header(subject, 'utf-8')
        
        # 添加邮件正文（使用HTML格式）
        message.attach(MIMEText(full_html, 'html', 'utf-8'))
        
        # 发送邮件
        if smtp_port == 465:
            # SSL连接
            smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # 普通连接
            smtp = smtplib.SMTP(smtp_server, smtp_port)
            smtp.starttls()  # 启用TLS加密
            
        smtp.login(sender, password)
        smtp.sendmail(sender, receiver, message.as_string())
        smtp.quit()
        
        print(f"邮件已成功发送到 {receiver}")
        return True
    except Exception as e:
        print(f"发送邮件时出错: {e}")
        return False