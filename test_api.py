#!/usr/bin/env python
import sys
import os
sys.path.insert(0, '/Users/huanglu/projects/hl-knowlege-assistant/backend')

# 测试导入
try:
    from rag_chain import RAGChain, DirectEmbeddings
    from llm_config_a import get_llm
    print("✓ 成功导入RAGChain和LLM配置")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试LLM初始化
try:
    llm = get_llm()
    print("✓ 成功初始化LLM")
except Exception as e:
    print(f"❌ LLM初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试RAGChain初始化
try:
    rag_chain = RAGChain(llm)
    print("✓ 成功初始化RAGChain")
except Exception as e:
    print(f"❌ RAGChain初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 检查向量库
if rag_chain.load_vectorstore():
    print("✓ 成功加载向量库")
    
    # 测试ask方法
    try:
        print("\n正在测试问答功能...")
        result = rag_chain.ask("你好")
        print(f"✓ 问答成功")
        print(f"答案: {result['answer']}")
        print(f"来源数量: {len(result['sources'])}")
    except Exception as e:
        print(f"❌ 问答失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠ 向量库为空，跳过问答测试")
