import os
import openai
from typing import Optional, Dict, Any
from dotenv import load_dotenv

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
    # 设置API密钥
    if api_key:
        openai.api_key = api_key
    else:
        openai.api_key = os.environ.get("OPENAI_API_KEY")
    # 设置Base URL
    openai.base_url = os.environ.get("OPENAI_BASE_URL")
    if not openai.api_key:
        raise ValueError("未提供OpenAI API密钥，请通过参数传入或设置OPENAI_API_KEY环境变量")
    
    try:
        # 使用新版OpenAI API
        client = openai.OpenAI(
            api_key=openai.api_key,
            base_url=openai.base_url
        )
        
        # 调用OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 提取回复内容
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"生成回复时出错: {str(e)}"


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
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key", "OPENAI_BASE_URL": "https://api.openai.com/v1"}):
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
            mock_openai.assert_called_with(api_key="custom_key", base_url=None)
        
        def test_missing_api_key(self):
            # 测试缺少API密钥的情况
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError):
                    ai_response("测试提示词")
        
        @patch('openai.OpenAI')
        def test_exception_handling(self, mock_openai):
            # 测试异常处理
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            # 模拟API调用抛出异常
            mock_client.chat.completions.create.side_effect = Exception("测试异常")
            
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
                result = ai_response("测试提示词")
            
            self.assertTrue(result.startswith("生成回复时出错"))
            self.assertIn("测试异常", result)
    
    # 运行测试
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    test_ai_response()
