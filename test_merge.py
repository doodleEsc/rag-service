#!/usr/bin/env python3
"""
测试import语句合并功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from demo import CodeSplitter, LANGUAGE_NODE_MAP

# Java测试代码，包含多个分散的import语句
java_test_code = """
package com.example.app;

// 第一组import
import java.util.List;
import java.util.ArrayList;
import java.util.Map;

// 中间有一些空行和注释
// 这是一些说明

// 第二组import，间隔较远
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;

// 第三组import
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
}
"""

def test_java_import_merge():
    """测试Java import语句合并"""
    print("🔍 测试Java import语句合并功能")
    print("=" * 60)
    
    splitter = CodeSplitter(LANGUAGE_NODE_MAP)
    
    # 测试合并前后的差异
    print("\n📄 原始Java代码:")
    print("-" * 40)
    print(java_test_code.strip())
    
    print("\n🔧 开始代码分割和合并...")
    results = splitter.split_text(java_test_code, "java")
    
    print(f"\n📊 分割结果:")
    for category, blocks in results.items():
        print(f"\n📂 {category} ({len(blocks)} 个代码块):")
        for i, block in enumerate(blocks, 1):
            print(f"\n  [{i}] 代码块:")
            indented_block = "\n".join(f"      {line}" for line in block.strip().split("\n"))
            print(indented_block)
            print(f"      字符数: {len(block)}")

if __name__ == "__main__":
    test_java_import_merge() 