# secret_example.py
# 这是一个示例配置文件，包含敏感信息，请根据实际情况修改并保存为 `secret.py`。

# 邮件配置
# 注意：此文件包含敏感信息，请勿提交到版本控制系统

# QQ邮箱授权码（不是QQ密码）
# 获取方式：
# 1. 登录QQ邮箱网页版
# 2. 点击设置 -> 账户
# 3. 开启POP3/SMTP服务
# 4. 生成授权码
# 请将下面的 'your_authorization_code_here' 替换为你的QQ邮箱授权码
email_password = "test_authorization_code"

# 示例：email_password = "abcdefghijklmnop"

# OpenAI API 配置
# 请将下面的配置替换为您的实际 API 密钥和基础URL
openai_api_key = "sk-1145141919810"
openai_base_url = "https://api.openai.com/v1"

# 如果使用第三方API服务，可以修改base_url，例如：
# openai_base_url = "https://api.deepseek.com/v1"
# openai_base_url = "https://api.anthropic.com/v1"
