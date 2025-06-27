import os
import openai
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from secret import openai_api_key, openai_base_url

def ai_response(prompt: str, 
                      model: str = "gpt-4o-mini", 
                      temperature: float = 0.7, 
                      max_tokens: int = 1000, 
                      api_key: Optional[str] = None) -> str:
    """
    使用OpenAI模型生成对提示词的回复
    
    参数:
        prompt (str): 输入的提示词
        model (str): 使用的OpenAI模型名称，默认为"gpt-4o-mini"
        temperature (float): 生成文本的随机性，值越高随机性越大，默认为0.7
        max_tokens (int): 生成文本的最大长度，默认为1000
        api_key (Optional[str]): OpenAI API密钥，如果为None则从环境变量获取
        
    返回:
        str: 模型生成的回复文本
    """
    load_dotenv()
    # 设置API密钥 - 优先级：参数 > secret.py > 环境变量
    if api_key:
        api_key_to_use = api_key
    elif openai_api_key and openai_api_key != "your_openai_api_key_here":
        api_key_to_use = openai_api_key
    else:
        api_key_to_use = os.environ.get("OPENAI_API_KEY")
    
    # 设置Base URL - 优先级：secret.py > 环境变量
    if openai_base_url and openai_base_url != "https://api.openai.com/v1":
        base_url_to_use = openai_base_url
    else:
        base_url_to_use = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if not api_key_to_use:
        raise ValueError("未提供OpenAI API密钥，请在secret.py文件中配置、通过参数传入或设置OPENAI_API_KEY环境变量")
    
    try:
        # 使用新版OpenAI API
        client = openai.OpenAI(
            api_key=api_key_to_use,
            base_url=base_url_to_use
        )
        
        # 调用OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的翻译助手。请只返回翻译结果，不要添加任何额外的信息、解释或格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 提取回复内容并清理格式
        content = response.choices[0].message.content.strip()
        
        # 过滤掉可能的GitHub仓库信息格式（如：user/repo ⭐ number）
        import re
        # 移除GitHub仓库格式的内容
        content = re.sub(r'[a-zA-Z0-9_-]+\s*/\s*[a-zA-Z0-9_-]+\s*⭐\s*\d+', '', content)
        # 移除多余的换行和空格
        content = re.sub(r'\n+', ' ', content).strip()
        
        return content
    
    except Exception as e:
        error_msg = f"AI生成内容时出现错误: {str(e)}"
        print(error_msg)  # 只在控制台显示错误信息
        # 返回空字符串，避免在文档和邮件中显示错误信息
        return ""


def test_ai_response():
    """
    测试ai_response函数的功能
    
    测试以下情况:
    1. 正常调用函数并获取回复
    2. 使用自定义API密钥
    3. 缺少API密钥时的错误处理
    4. 异常处理
    """
    import unittest
    from unittest.mock import patch, MagicMock
    
    class TestAIResponse(unittest.TestCase):
        
        @patch('openai.OpenAI')
        @patch('ai.openai_api_key', "test_key")
        @patch('ai.openai_base_url', "https://api.openai.com/v1")
        def test_normal_response(self, mock_openai):
            # 模拟OpenAI客户端和响应
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "这是一个测试回复"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # 测试正常调用
            result = ai_response("测试提示词")
                
            self.assertEqual(result, "这是一个测试回复")
            mock_client.chat.completions.create.assert_called_once()
        
        @patch('openai.OpenAI')
        def test_custom_api_key(self, mock_openai):
            # 测试自定义API密钥
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "自定义密钥测试回复"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            result = ai_response("测试提示词", api_key="custom_key")
            
            self.assertEqual(result, "自定义密钥测试回复")
            mock_openai.assert_called_with(api_key="custom_key", base_url="https://api.openai.com/v1")
        
        @patch('ai.openai_api_key', "your_openai_api_key_here")
        def test_missing_api_key(self):
            # 测试缺少API密钥的情况
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError):
                    ai_response("测试提示词")
        
        @patch('openai.OpenAI')
        @patch('ai.openai_api_key', "test_key")
        def test_exception_handling(self, mock_openai):
            # 测试异常处理
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            # 模拟API调用抛出异常
            mock_client.chat.completions.create.side_effect = Exception("测试异常")
            
            result = ai_response("测试提示词")
            
            # 现在应该返回空字符串而不是错误信息
            self.assertEqual(result, "")
    
    # 运行测试
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    test_ai_response()
