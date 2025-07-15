import tree_sitter
from tree_sitter_language_pack import get_language, get_parser
import argparse

# 在LANGUAGE_NODE_MAP的顶部添加合并配置说明
# 配置说明：
# _merge_config: 指定哪些类别需要合并
# - enabled: 是否启用合并
# - max_gap_lines: 允许的最大行间隔（超过此间隔的代码块不会合并）
# - preserve_order: 是否保持原始顺序

from lang_node_map import LANGUAGE_NODE_MAP


class CodeBlock:
    """代码块数据结构，包含内容和位置信息"""

    def __init__(self, content: str, start_line: int, end_line: int, category: str):
        self.content = content
        self.start_line = start_line
        self.end_line = end_line
        self.category = category

    def __repr__(self):
        return f"CodeBlock(category={self.category}, lines={self.start_line}-{self.end_line})"


class CodeSplitter:
    def __init__(self, language_map):
        self.language_map = language_map

    def _get_target_node_types(self, language: str) -> dict:
        """获取指定语言的所有目标节点类型"""
        lang_map = self.language_map.get(language)
        if not lang_map:
            raise ValueError(f"Language '{language}' is not configured.")

        # 将 "function": ["a", "b"] 转换为 "a": "function", "b": "function"
        # 方便后续处理查询结果
        target_types = {}
        for category, node_types in lang_map.items():
            if category.startswith("_"):  # 跳过配置项
                continue
            for node_type in node_types:
                target_types[node_type] = category
        return target_types

    def _get_merge_config(self, language: str) -> dict:
        """获取指定语言的合并配置"""
        lang_map = self.language_map.get(language, {})
        return lang_map.get("_merge_config", {})

    def _build_query(self, language: str, target_node_types: dict) -> tree_sitter.Query:
        """根据目标节点类型动态构建查询"""
        query_str = ""
        for node_type, category in target_node_types.items():
            # 检查是否是完整的查询语法（包含@符号和换行符）
            if "@" in node_type and "\n" in node_type:
                # 如果已经是完整查询，直接使用
                query_str += f"{node_type}\n"
            else:
                # 如果是简单节点类型，用标准格式包装
                query_str += f"({node_type}) @{category}\n"

        print(f"Final query: {query_str}")

        # 忽略类型检查错误
        lang_object = get_language(language)  # type: ignore
        return lang_object.query(query_str)

    def _extract_code_blocks(self, code: str, language: str) -> list:
        """提取所有代码块，包含位置信息"""
        code_bytes = bytes(code, "utf8")
        code_lines = code.split("\n")

        # 忽略类型检查错误
        parser = get_parser(language)  # type: ignore
        tree = parser.parse(code_bytes)

        target_node_types = self._get_target_node_types(language)
        if not target_node_types:
            return []

        query = self._build_query(language, target_node_types)
        matches = query.matches(tree.root_node)

        code_blocks = []

        # 处理每个匹配
        for match in matches:
            pattern_index, captures_dict = match

            # 找到目标节点和对应的注释
            for capture_name, nodes in captures_dict.items():
                if not capture_name.startswith("comment."):
                    # 这是目标节点
                    target_type = capture_name
                    comment_key = f"comment.{target_type}"

                    for target_node in nodes:
                        if (
                            target_node
                            and hasattr(target_node, "text")
                            and target_node.text is not None
                        ):
                            # 获取这个匹配中对应的注释
                            comments = captures_dict.get(comment_key, [])

                            # 计算起始和结束行号
                            start_line = (
                                target_node.start_point[0] + 1
                            )  # tree-sitter是0-based
                            end_line = target_node.end_point[0] + 1

                            # 如果有注释，调整起始行号
                            if comments:
                                comments.sort(key=lambda x: x.start_byte)
                                first_comment = comments[0]
                                start_line = min(
                                    start_line, first_comment.start_point[0] + 1
                                )

                                # 构建完整的代码块内容
                                comment_text = "\n".join(
                                    [
                                        c.text.decode("utf8")
                                        for c in comments
                                        if c.text is not None
                                    ]
                                )
                                target_text = target_node.text.decode("utf8")
                                full_text = comment_text + "\n" + target_text
                            else:
                                full_text = target_node.text.decode("utf8")

                            code_blocks.append(
                                CodeBlock(
                                    content=full_text,
                                    start_line=start_line,
                                    end_line=end_line,
                                    category=target_type,
                                )
                            )

        return code_blocks

    def _merge_code_blocks(
        self, code_blocks: list, code_lines: list, merge_config: dict
    ) -> list:
        """根据配置合并代码块"""
        if not code_blocks:
            return code_blocks

        # 按起始行号排序
        code_blocks.sort(key=lambda x: x.start_line)

        merged_blocks = []

        # 按类别分组
        blocks_by_category = {}
        for block in code_blocks:
            if block.category not in blocks_by_category:
                blocks_by_category[block.category] = []
            blocks_by_category[block.category].append(block)

        # 对每个类别进行合并处理
        for category, blocks in blocks_by_category.items():
            category_config = merge_config.get(category, {})

            if not category_config.get("enabled", False):
                # 不需要合并，直接添加
                merged_blocks.extend(blocks)
                continue

            max_gap_lines = category_config.get("max_gap_lines", 1)

            # 合并相邻的代码块
            current_group = [blocks[0]]

            for i in range(1, len(blocks)):
                prev_block = current_group[-1]
                curr_block = blocks[i]

                if max_gap_lines >= 0:
                    # 检查是否应该合并
                    gap = curr_block.start_line - prev_block.end_line - 1

                    if gap <= max_gap_lines:
                        # 合并到当前组
                        current_group.append(curr_block)
                    else:
                        # 完成当前组的合并，开始新组
                        if len(current_group) > 1:
                            merged_block = self._merge_group(current_group, code_lines)
                            merged_blocks.append(merged_block)
                        else:
                            merged_blocks.extend(current_group)

                        current_group = [curr_block]
                else:
                    current_group.append(curr_block)

            # 处理最后一组
            if len(current_group) > 1:
                merged_block = self._merge_group(current_group, code_lines)
                merged_blocks.append(merged_block)
            else:
                merged_blocks.extend(current_group)

        return merged_blocks

    def _merge_group(self, group: list, code_lines: list) -> CodeBlock:
        """合并一组代码块"""
        if len(group) == 1:
            return group[0]

        first_block = group[0]
        last_block = group[-1]

        # 提取完整的代码段（包括中间的空行）
        start_line = first_block.start_line
        end_line = last_block.end_line

        # 获取完整的代码内容
        full_content = "\n".join(code_lines[start_line - 1 : end_line])

        return CodeBlock(
            content=full_content,
            start_line=start_line,
            end_line=end_line,
            category=first_block.category,
        )

    def split_text(self, code: str, language: str) -> dict:
        """
        对源代码进行分割，提取出定义的代码块

        :param code: 源代码字符串
        :param language: 语言名称（如 'python', 'javascript'）
        :return: 一个字典，键是通用类别，值是提取到的代码块列表
        """
        # 提取所有代码块（包含位置信息）
        code_blocks = self._extract_code_blocks(code, language)

        # 获取合并配置
        merge_config = self._get_merge_config(language)

        # 如果有合并配置，执行合并
        if merge_config:
            code_lines = code.split("\n")
            code_blocks = self._merge_code_blocks(code_blocks, code_lines, merge_config)

            # 打印合并统计信息
            original_count = len(self._extract_code_blocks(code, language))
            merged_count = len(code_blocks)
            if original_count != merged_count:
                print(f"📊 合并统计: {original_count} → {merged_count} 个代码块")

                # 显示合并详情
                merge_details = {}
                for category, config in merge_config.items():
                    if config.get("enabled", False):
                        orig_blocks = [
                            b
                            for b in self._extract_code_blocks(code, language)
                            if b.category == category
                        ]
                        merged_blocks = [
                            b for b in code_blocks if b.category == category
                        ]
                        if len(orig_blocks) != len(merged_blocks):
                            merge_details[category] = (
                                f"{len(orig_blocks)} → {len(merged_blocks)}"
                            )

                if merge_details:
                    for category, detail in merge_details.items():
                        print(f"  📦 {category}: {detail}")

        # 转换为原来的字典格式
        results = {}
        target_node_types = self._get_target_node_types(language)

        # 初始化结果字典
        for category in set(block.category for block in code_blocks):
            results[category] = []

        # 添加代码块内容
        for block in code_blocks:
            results[block.category].append(block.content)

        print(f"Total matches: {len(code_blocks)}")

        return results


def get_all_test_cases():
    """获取所有语言的测试用例"""
    return {
        "python": {
            "name": "Python",
            "code": """
    # 导入声明测试
    import os
    from typing import List, Dict
    
    # 全局变量赋值
    GLOBAL_CONSTANT = "test"
    
    # 装饰器函数测试
    @property
    def decorated_function():
        '''装饰器函数示例'''
        return "decorated"
    
    # 普通函数
    def calculate_area(radius: float) -> float:
        '''计算圆的面积'''
        return 3.14 * radius * radius
    
    # 类定义
    class MyClass:
        '''这是一个示例类'''
        
        def __init__(self, value: int):
            '''构造函数'''
            self.value = value
        
        def get_value(self) -> int:
            '''获取值的方法'''
            return self.value
    """,
        },
        "go": {
            "name": "Go",
            "code": """
    // 包声明
    package main
    
    // 导入声明
    import (
        "fmt"
        "net/http"
    )
    
    // 常量声明
    const (
        // 服务器端口
        PORT = 8080
        // 默认超时时间
        TIMEOUT = 30
    )
    
    // 变量声明
    var (
        // 全局配置
        config map[string]string
        // 服务器实例
        server *http.Server
    )

    
    // 结构体定义
    type User struct {
        // 用户ID
        ID   int    `json:"id"`
        // 用户名
        Name string `json:"name"`
    }
    
    // 接口定义
    type UserService interface {
        // 获取用户信息
        GetUser(id int) (*User, error)
        // 创建用户
        CreateUser(user *User) error
    }
    
    // 类型别名
    type UserID = int
    
    // 函数定义
    func main() {
        // 主函数
        fmt.Println("Hello, World!")
    }
    
    // 方法定义
    func (u *User) String() string {
        // 用户字符串表示
        return fmt.Sprintf("User{ID: %d, Name: %s}", u.ID, u.Name)
    }
    """,
        },
        "javascript": {
            "name": "JavaScript",
            "code": """
    // 导入语句
    import React from 'react';
    import { useState } from 'react';
    
    // 变量声明
    const PI = 3.14159;
    let counter = 0;
    var oldStyle = "deprecated";
    
    // 普通函数
    function calculateArea(radius) {
        // 计算圆面积
        return PI * radius * radius;
    }
    
    // 箭头函数
    const multiply = (a, b) => {
        // 乘法函数
        return a * b;
    };
    
    // 类定义
    class Calculator {
        // 计算器类
        constructor() {
            this.result = 0;
        }
        
        // 方法定义
        add(value) {
            // 加法操作
            this.result += value;
            return this;
        }
    }
    
    // 导出语句
    export default Calculator;
    export { calculateArea, multiply };
    """,
        },
        "typescript": {
            "name": "TypeScript",
            "code": """
    // 导入语句
    import { Component } from '@angular/core';
    
    // 类型别名
    type UserId = number;
    type UserName = string;
    
    // 接口定义
    interface User {
        // 用户接口
        id: UserId;
        name: UserName;
        email?: string;
    }
    
    // 枚举定义
    enum Status {
        // 状态枚举
        PENDING = "pending",
        APPROVED = "approved",
        REJECTED = "rejected"
    }
    
    // 类定义
    class UserService {
        // 用户服务类
        private users: User[] = [];
        
        // 公共属性
        public readonly maxUsers = 1000;
        
        // 方法定义
        addUser(user: User): void {
            // 添加用户方法
            this.users.push(user);
        }
    }
    
    // 函数定义
    function processUser(user: User): Promise<void> {
        // 处理用户函数
        return Promise.resolve();
    }
    
    // 箭头函数
    const validateEmail = (email: string): boolean => {
        // 验证邮箱格式
        return email.includes('@');
    };
    
    // 变量声明
    const config = {
        apiUrl: 'https://api.example.com'
    };
    
    // 导出语句
    export { UserService, Status };
    """,
        },
        "java": {
            "name": "Java",
            "code": """
    /*
     * 多行注释示例
     * 导入必要的类库
     */
    import java.util.List;
    // 单行注释：导入ArrayList
    import java.util.ArrayList;
    
    /**
     * 枚举定义示例
     * 支持块注释
     */
    public enum Status {
        // 单行注释：状态枚举
        ACTIVE, INACTIVE, PENDING
    }
    
    /*
     * 接口定义
     * 用户仓储接口
     */
    public interface UserRepository {
        // 查找用户方法
        User findById(Long id);
        /* 保存用户方法 */
        void save(User user);
    }
    
    /**
     * 用户类定义
     * 包含用户的基本信息和操作
     */
    public class User {
        
        /* 私有字段定义 */
        private Long id;
        // 用户名字段
        private String name;
        /*
         * 用户状态字段
         * 默认为ACTIVE
         */
        private Status status;
        
        /**
         * 用户构造函数
         * @param id 用户ID
         * @param name 用户名
         */
        public User(Long id, String name) {
            // 初始化用户信息
            this.id = id;
            this.name = name;
            /* 设置默认状态 */
            this.status = Status.ACTIVE;
        }
        
        /*
         * 获取用户名方法
         * 返回当前用户的名称
         */
        public String getName() {
            // 返回用户名
            return this.name;
        }
        
        /**
         * 设置用户名方法
         * @param name 新的用户名
         */
        public void setName(String name) {
            // 更新用户名
            this.name = name;
        }
    }
    """,
        },
        "rust": {
            "name": "Rust",
            "code": """
    // 导入语句
    use std::collections::HashMap;
    use serde::{Deserialize, Serialize};
    
    // 常量定义
    const MAX_USERS: usize = 1000;
    
    // 类型别名
    type UserId = u64;
    
    // 结构体定义
    #[derive(Debug, Serialize, Deserialize)]
    pub struct User {
        // 用户结构体
        pub id: UserId,
        pub name: String,
        pub email: Option<String>,
    }
    
    // 枚举定义
    #[derive(Debug)]
    pub enum UserError {
        // 用户错误枚举
        NotFound,
        InvalidData(String),
        DatabaseError,
    }
    
    // Trait定义
    pub trait UserRepository {
        // 用户仓储特征
        fn find_by_id(&self, id: UserId) -> Result<User, UserError>;
        fn save(&mut self, user: User) -> Result<(), UserError>;
    }
    
    // 实现块
    impl User {
        // 用户实现
        
        // 函数定义
        pub fn new(id: UserId, name: String) -> Self {
            // 创建新用户
            Self {
                id,
                name,
                email: None,
            }
        }
    }
    
    // 模块定义
    pub mod utils {
        // 工具模块
        
        // 公共函数
        pub fn validate_email(email: &str) -> bool {
            // 验证邮箱格式
            email.contains('@')
        }
    }
    
    // 宏定义
    macro_rules! create_user {
        // 创建用户宏
        ($id:expr, $name:expr) => {
            User::new($id, $name.to_string())
        };
    }
    """,
        },
        "c": {
            "name": "C",
            "code": """
    // 头文件包含
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    // 宏定义
    #define MAX_NAME_LENGTH 100
    #define PI 3.14159
    
    // 结构体定义
    typedef struct {
        // 用户结构体
        int id;
        char name[MAX_NAME_LENGTH];
        int age;
    } User;
    
    // 枚举定义
    typedef enum {
        // 状态枚举
        STATUS_ACTIVE,
        STATUS_INACTIVE,
        STATUS_PENDING
    } Status;
    
    // 类型定义
    typedef int UserId;
    typedef char* UserName;
    
    // 全局变量
    static int user_count = 0;
    User users[1000];
    
    // 函数声明
    User* create_user(int id, const char* name);
    void print_user(const User* user);
    int find_user_by_id(int id);
    
    // 函数定义
    User* create_user(int id, const char* name) {
        // 创建用户函数
        if (user_count >= 1000) {
            return NULL;
        }
        
        User* user = &users[user_count++];
        user->id = id;
        strncpy(user->name, name, MAX_NAME_LENGTH - 1);
        user->name[MAX_NAME_LENGTH - 1] = '\0';
        user->age = 0;
        
        return user;
    }
    
    void print_user(const User* user) {
        // 打印用户信息
        if (user != NULL) {
            printf("User ID: %d, Name: %s, Age: %d\n", 
                   user->id, user->name, user->age);
        }
    }
    """,
        },
        "cpp": {
            "name": "C++",
            "code": """
    // -------------------------------------------------------------------------
    // 1. 预处理器指令 (Preprocessor Directives)
    // -------------------------------------------------------------------------

    // 头文件包含 (已存在)
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <map>
#include <stdexcept>
#include <functional>

    // 新增：宏定义和条件编译
#define APP_VERSION "1.1.0"
#ifdef _DEBUG
        #define LOG(msg) std::cout << msg << std::endl
#else
        #define LOG(msg)
#endif

    // 新增：防止头文件重复包含的 Pragma
#pragma once

    // 新增：全局常量和变量
    const double PI = 3.1415926535;
    static int globalCounter = 0; // 静态全局变量

    // 新增：C 风格的类型定义
    typedef unsigned long long uint64_t_c_style;

    // 新增：函数前向声明
    void freeFunction(int); 

    // 新增：类前向声明
    class AdvancedUserService;

    // -------------------------------------------------------------------------
    // 2. 命名空间和类/结构体/枚举的深入使用
    // -------------------------------------------------------------------------

    namespace UserManagement {
        // 命名空间 (已存在)

        // 新增：匿名命名空间 (internal linkage)
        namespace {
            const char* INTERNAL_SECRET = "secret_key";
        }

        // 新增：模板特化
        template<typename T>
        class Repository { 
            // ... (内容如前)
        private:
            std::vector<T> items;
        public:
            void add(const T& item) { items.push_back(item); }
            size_t size() const { return items.size(); }
        };

        // 新增：Repository 的模板全特化 (Template Full Specialization)
        template<>
        class Repository<void*> {
        public:
            void add(void* ptr) { /* 特化处理 */ }
            size_t size() const { return 0; }
        };

        struct User { 
            // ... (内容如前)
            int id;
            std::string name;
            int age;
            User(int id, const std::string& name, int age) : id(id), name(name), age(age) {}

            // 新增：友元类 (Friend Class)
            friend class AdvancedUserService;
        };
        
        // 新增：传统枚举 (Unscoped Enum)
        enum LegacyStatus { OK, FAILED, PENDING };

        enum class Status { Active, Inactive, Pending }; // (已存在)
        
        using UserId = int;
        using UserPtr = std::shared_ptr<User>;

        // 新增：接口类 (抽象基类)
        class IUserService {
        public:
            // 新增：纯虚函数和虚析构函数 (Pure Virtual Function & Virtual Destructor)
            virtual ~IUserService() = default;
            virtual User getUser(UserId id) const = 0;
        };

        // 新增：一个更复杂的类，演示更多特性
        class AdvancedUserService final : public IUserService { // 新增：final 和继承
        public:
            // 构造函数 (已存在)
            AdvancedUserService() : userRepository(std::make_unique<Repository<User>>()) {}

            // 新增：override 关键字
            User getUser(UserId id) const override {
                // 新增：Lambda 表达式
                auto findUser = [id](const User& u) -> bool {
                    return u.id == id;
                };
                // 只是示例，实际应在 repository 中查找
                if (findUser(User(1, "test", 1))) {
                    return User(id, "Found User", 30);
                }
                // 新增：异常抛出 (throw)
                throw std::runtime_error("User not found");
            }

            // 新增：noexcept 和 const 成员函数
            size_t getUserCount() const noexcept {
                return userRepository->size();
            }

            // 新增：接收右值引用的成员函数 (Move Semantics)
            void addUser(User&& user) {
                userRepository->add(std::move(user));
            }

            // 新增：模板成员函数
            template<typename V>
            void logValue(V value) {
                std::cout << "Logging value: " << value << std::endl;
            }

            // 新增：静态成员变量和函数
            static const int MAX_USERS = 1000;
            static std::string getMetadata() { return "Service Metadata"; }

            // 新增：友元函数声明
            friend void inspectService(const AdvancedUserService& service);

        protected: // 新增：protected 访问控制符
            std::map<UserId, Status> userStatus;

        private: // (已存在)
            // 新增：使用智能指针作为成员 (unique_ptr)
            std::unique_ptr<Repository<User>> userRepository;
        };

        // 新增：友元函数的实现
        void inspectService(const AdvancedUserService& service) {
            std::cout << "Inspecting service, has " << service.userRepository->size() << " users." << std::endl;
        }

        // 新增：C++20 Concepts
        template<typename T>
        concept Printable = requires(T t) {
            { std::cout << t } -> std::same_as<std::ostream&>;
        };

        // 新增：变参模板函数 (Variadic Template)
        template<Printable... Args>
        void printAll(const Args&... args) {
            // 新增：折叠表达式 (Fold Expression) C++17
            ( (std::cout << args << ' '), ... );
            std::cout << std::endl;
        }

    } // namespace UserManagement


    // -------------------------------------------------------------------------
    // 3. 主函数中的各种语句和表达式
    // -------------------------------------------------------------------------

    // 全局函数 (已存在)
    int main() {
        using namespace UserManagement;
        
        AdvancedUserService service;
        service.addUser(User(1, "John Doe", 25));
        service.addUser({2, "Jane Smith", 30}); // 新增：列表初始化

        LOG("Service created."); // 使用宏

        // 新增：if-else-if-else 控制流
        if (service.getUserCount() > 1) {
            std::cout << "Multiple users exist." << std::endl;
        } else if (service.getUserCount() == 1) {
            std::cout << "One user exists." << std::endl;
        } else {
            std::cout << "No users." << std::endl;
        }

        // 新增：switch-case 语句
        Status currentStatus = Status::Active;
        switch (currentStatus) {
            case Status::Active:
                std::cout << "Status: Active" << std::endl;
                break; // 新增：break 语句
            case Status::Inactive:
                std::cout << "Status: Inactive" << std::endl;
                break;
            default: // 新增：default case
                std::cout << "Status: Unknown" << std::endl;
                break;
        }
        
        // 新增：try-catch 异常处理
        try {
            User u = service.getUser(99);
        } catch (const std::runtime_error& e) {
            std::cerr << "Caught exception: " << e.what() << std::endl;
        } catch (...) { // 新增：捕获所有其他异常
            std::cerr << "Caught an unknown exception." << std::endl;
        }

        // 新增：基于范围的 for 循环 (Range-based for loop)
        std::vector<User> userList = { {3, "Alice", 22}, {4, "Bob", 44} };
        for (const auto& user : userList) {
            // 新增：结构化绑定 (Structured Binding) C++17
            auto [id, name, age] = user;
            std::cout << "User from list: " << name << std::endl;
        }

        // 新增：传统 for 循环和 continue
        for (int i = 0; i < 5; ++i) {
            if (i % 2 == 0) {
                continue; // 新增：continue 语句
            }
            std::cout << "Odd number: " << i << std::endl;
        }

        // 新增：while 和 do-while 循环
        int countdown = 3;
        while (countdown > 0) {
            std::cout << "while countdown: " << countdown-- << std::endl;
        }
        do {
            std::cout << "do-while countdown: " << countdown-- << std::endl;
        } while (countdown > -2);

        // 新增：指针和动态内存 (new/delete)
        User* dynamicUser = new User(5, "Dynamic Dave", 50);
        std::cout << "Dynamic user name: " << dynamicUser->name << std::endl; // 新增：-> 运算符
        delete dynamicUser;

        // 新增：三元运算符 (Ternary Operator)
        std::string userState = (currentStatus == Status::Active) ? "Active" : "Not Active";
        std::cout << "User state: " << userState << std::endl;
        
        // 新增：函数指针
        void (*funcPtr)(const AdvancedUserService&);
        funcPtr = &inspectService;
        funcPtr(service); // 通过函数指针调用

        // 新增：C-style类型转换 和 C++类型转换
        double val = 3.14;
        int int_val_c = (int)val; // C-style cast
        int int_val_cpp = static_cast<int>(val); // static_cast
        const User user_const(6, "Const Carol", 60);
        User* user_non_const = const_cast<User*>(&user_const); // const_cast
        IUserService* base_ptr = &service;
        AdvancedUserService* derived_ptr = dynamic_cast<AdvancedUserService*>(base_ptr); // dynamic_cast
        uintptr_t ptr_val = reinterpret_cast<uintptr_t>(derived_ptr); // reinterpret_cast

        // 新增：sizeof 和 typeid 运算符
        std::cout << "Size of User: " << sizeof(User) << " bytes" << std::endl;
        std::cout << "Type of service: " << typeid(service).name() << std::endl;

        // 新增：goto (仅为展示语法，不推荐使用)
        goto end_label; 
        std::cout << "This line will be skipped." << std::endl;
    end_label:
        std::cout << "Jumped to end_label." << std::endl;

        // 新增：C++17 属性
        [[maybe_unused]] int unused_variable = 0;
        
        printAll("Test", 123, 4.56); // 调用变参模板函数

        return 0;
    }

    """,
        },
        "php": {
            "name": "PHP",
            "code": """
<?php
// 0. 声明严格类型（type_declaration）
declare(strict_types=1);

// 1. 命名空间定义（namespace_definition）
namespace App\\Models;

// 2. 使用声明分组（group_use_declaration）
use App\\{
    Contracts\\Repository,
    Events\\UserEvent
};

// 3. 文件包含（include_expression）
require_once 'vendor/autoload.php';
include 'config/database.php';

// 4. 接口定义（interface_declaration）
interface UserRepositoryInterface {
    public function findById(int $id): ?User;
    public function save(User $user): bool;
}

// 5. Trait定义（trait_declaration）
trait TimestampsTrait {
    protected $created_at;  // property_declaration
    protected $updated_at;
    
    public function updateTimestamps(): void {
        $this->updated_at = date('Y-m-d H:i:s');  // function_call_expression
    }
}

// 6. 类定义（class_declaration）
#[ORM\Entity]  // attribute (PHP8)
final class User implements UserRepositoryInterface {
    use TimestampsTrait;

    const STATUS_ACTIVE = 1;  // class_const_declaration
    public static int $count = 0;  // static_variable_declaration
    
    public function __construct(
        private int $id,          // promoted_property (PHP8)
        private string $name,
        private ?string $email
    ) {
        $this->created_at = date('Y-m-d H:i:s');
        self::$count++;
    }

    // 7. 析构方法（__destruct）
    public function __destruct() {
        self::$count--;
    }

    // 8. 生成器方法（yield_expression）
    public function getPosts(): Generator {
        foreach ($this->posts as $post) {
            yield $post->title;
        }
    }

    // 9. 匿名类（anonymous_class_creation_expression）
    public function createLogger(): object {
        return new class extends Logger {
            public function log(string $message): void {
                file_put_contents('app.log', $message);
            }
        };
    }
}

// 10. 枚举定义（enum_declaration，PHP8.1）
enum UserStatus: int {
    case Active = 1;      // enum_case_declaration
    case Inactive = 0;
}

// 11. 匹配表达式（match_expression，PHP8.0）
function getStatusText(UserStatus $status): string {
    return match($status) {
        UserStatus::Active => 'Active',
        UserStatus::Inactive => 'Inactive'
    };
}

// 12. 箭头函数（arrow_function，PHP7.4）
$multiplier = fn($x) => $x * 2;

// 13. 空安全操作符（nullsafe_member_call_expression，PHP8.0）
$country = $user?->getAddress()?->country;

// 14. 联合类型（union_type，PHP8.0）
function process(int|string $input): mixed {
    // 15. switch语句（switch_statement）
    switch (true) {
        case is_int($input):
            return $input * 2;
        default:
            return strtoupper($input);
    }
}

// 16. try-catch-finally（try_statement）
try {
    new PDO('mysql:host=localhost');
} catch (PDOException $e) {
    error_log($e);
} finally {
    echo 'Cleanup';
}

// 17. 属性语法（attribute，PHP8）
<<<
User
    @@Deprecated("Use newUser instead", 1.2)
>>>  // heredoc_string
class LegacyUser {}

// 18. 可变参数（variadic_parameter）
function merge(...$arrays): array {
    return array_merge(...$arrays);
}

// 19. 类型别名（type_alias）
class_alias('App\\Models\\User', 'User');

// 20. 嵌套HTML（text_interpolation）
?>
<h1>User List</h1>
<?php foreach ($users as $user): ?>
    <p><?= htmlspecialchars($user->name) ?></p>
<?php endforeach; ?>
    """,
        },
        "ruby": {
            "name": "Ruby",
            "code": """
    # 模块定义
    module UserManagement
      # 用户管理模块
      
      # 常量定义
      MAX_USERS = 1000
      DEFAULT_AGE = 18
      
      # 类定义
      class User
        # 用户类
        
        attr_accessor :id, :name, :email
        attr_reader :created_at
        
        # 初始化方法
        def initialize(id, name, email)
          # 用户初始化
          @id = id
          @name = name
          @email = email
          @created_at = Time.now
        end
        
        # 实例方法
        def full_info
          # 获取完整信息
          "#{@name} (#{@email})"
        end
        
        # 类方法
        def self.create_guest
          # 创建访客用户
          new(0, "Guest", "guest@example.com")
        end
        
        # 私有方法
        private
        
        def validate_email
          # 验证邮箱
          @email.include?("@")
        end
      end
      
      # 模块方法
      def self.find_user_by_id(id)
        # 根据ID查找用户
        # 实现查找逻辑
      end
    end
    
    # 包含模块
    include UserManagement
    
    # 全局方法
    def print_user_info(user)
      # 打印用户信息
      puts user.full_info
    end
    """,
        },
        "swift": {
            "name": "Swift",
            "code": """
    // 导入语句
    import Foundation
    import UIKit
    
    // 协议定义
    protocol UserRepositoryProtocol {
        // 用户仓储协议
        func findUser(by id: Int) -> User?
        func saveUser(_ user: User) throws
    }
    
    // 结构体定义
    struct User {
        // 用户结构体
        let id: Int
        var name: String
        var email: String?
        
        // 计算属性
        var displayName: String {
            // 显示名称
            return name.isEmpty ? "Unknown" : name
        }
    }
    
    // 枚举定义
    enum UserError: Error {
        // 用户错误枚举
        case notFound
        case invalidData(String)
        case networkError
    }
    
    // 类定义
    class UserService: UserRepositoryProtocol {
        // 用户服务类
        
        private var users: [User] = []
        
        // 初始化方法
        init() {
            // 用户服务初始化
            self.users = []
        }
        
        // 方法实现
        func findUser(by id: Int) -> User? {
            // 查找用户
            return users.first { $0.id == id }
        }
        
        func saveUser(_ user: User) throws {
            // 保存用户
            if user.name.isEmpty {
                throw UserError.invalidData("Name cannot be empty")
            }
            users.append(user)
        }
    }
    
    // 扩展定义
    extension User {
        // 用户扩展
        
        // 初始化扩展
        init(id: Int, name: String) {
            // 简化初始化
            self.id = id
            self.name = name
            self.email = nil
        }
        
        // 方法扩展
        func isValidEmail() -> Bool {
            // 验证邮箱
            return email?.contains("@") ?? false
        }
    }
    
    // 函数定义
    func createDefaultUser() -> User {
        // 创建默认用户
        return User(id: 0, name: "Default User")
    }
    """,
        },
        "kotlin": {
            "name": "Kotlin",
            "code": """
    // 导入语句
    import kotlin.collections.List
    import kotlinx.coroutines.*
    
    // 接口定义
    interface UserRepository {
        // 用户仓储接口
        suspend fun findById(id: Int): User?
        suspend fun save(user: User): Boolean
    }
    
    // 数据类定义
    data class User(
        // 用户数据类
        val id: Int,
        var name: String,
        var email: String? = null
    ) {
        // 方法定义
        fun getDisplayName(): String {
            // 获取显示名称
            return if (name.isNotEmpty()) name else "Unknown"
        }
    }
    
    // 枚举类定义
    enum class UserStatus {
        // 用户状态枚举
        ACTIVE,
        INACTIVE,
        PENDING;
        
        // 枚举方法
        fun isActive(): Boolean {
            // 检查是否激活
            return this == ACTIVE
        }
    }
    
    // 类定义
    class UserService : UserRepository {
        // 用户服务类
        
        private val users = mutableListOf<User>()
        
        // 重写方法
        override suspend fun findById(id: Int): User? {
            // 根据ID查找用户
            return withContext(Dispatchers.IO) {
                users.find { it.id == id }
            }
        }
        
        override suspend fun save(user: User): Boolean {
            // 保存用户
            return try {
                users.add(user)
                true
            } catch (e: Exception) {
                false
            }
        }
        
        // 普通方法
        fun getUserCount(): Int {
            // 获取用户数量
            return users.size
        }
    }
    
    // 对象定义
    object UserUtils {
        // 用户工具对象
        
        // 常量
        const val MAX_NAME_LENGTH = 100
        
        // 方法
        fun validateEmail(email: String): Boolean {
            // 验证邮箱格式
            return email.contains("@") && email.contains(".")
        }
        
        // 应用方法
        fun apply(id: Int, name: String): User = {
            // 创建用户
            User(id, name)
        }
    }
    
    // 顶层函数
    fun createGuestUser(): User {
        // 创建访客用户
        return User(id = -1, name = "Guest")
    }
    """,
        },
        "scala": {
            "name": "Scala",
            "code": """
    // 导入语句
    import scala.collection.mutable.ListBuffer
    import scala.concurrent.Future
    import scala.util.{Success, Failure}
    
    // 特征定义
    trait UserRepository {
        // 用户仓储特征
        def findById(id: Int): Option[User]
        def save(user: User): Boolean
    }
    
    // 样例类定义
    case class User(
        // 用户样例类
        id: Int,
        name: String,
        email: Option[String] = None
    ) {
        // 方法定义
        def displayName: String = {
            // 显示名称
            if (name.nonEmpty) name else "Unknown"
        }
    }
    
    // 类定义
    class UserService extends UserRepository {
        // 用户服务类
        
        private val users = ListBuffer[User]()
        
        // 方法实现
        override def findById(id: Int): Option[User] = {
            // 根据ID查找用户
            users.find(_.id == id)
        }
        
        override def save(user: User): Boolean = {
            // 保存用户
            try {
                users += user
                true
            } catch {
                case _: Exception => false
            }
        }
        
        // 其他方法
        def getUserCount: Int = {
            // 获取用户数量
            users.length
        }
    }
    
    // 对象定义
    object UserUtils {
        // 用户工具对象
        
        // 常量
        val MaxNameLength = 100
        
        // 方法
        def validateEmail(email: String): Boolean = {
            // 验证邮箱格式
            email.contains("@") && email.contains(".")
        }
        
        // 应用方法
        def apply(id: Int, name: String): User = {
            // 创建用户
            User(id, name)
        }
    }
    
    // 函数定义
    def createDefaultUser(): User = {
        // 创建默认用户
        User(0, "Default")
    }
    """,
        },
        "lua": {
            "name": "Lua",
            "code": """
-- lua/doodle/agent.lua
local utils = require("doodle.utils")
local task = require("doodle.task")
local context = require("doodle.context")
local prompt = require("doodle.prompt")
local tool = require("doodle.tool")
local provider = require("doodle.provider")
local M = {}

-- Agent 状态
M.AGENT_STATUS = {
	IDLE = "idle",
	THINKING = "thinking",
	WORKING = "working",
	PAUSED = "paused",
	STOPPED = "stopped",
}

-- Agent 实例
M.current_agent = nil

-- Agent 类
local Agent = {}
Agent.__index = Agent

local TEstFunction = function(name)
    print(name)
end

-- 创建新的Agent实例
function Agent.new(callbacks)
	local self = setmetatable({}, Agent)

	self.id = utils.generate_uuid()
	self.status = M.AGENT_STATUS.IDLE
	self.callbacks = callbacks or {}
	self.current_task_id = nil
	self.current_context_id = nil
	self.loop_running = false
	self.stop_requested = false
	self.created_at = utils.get_timestamp()

	utils.log("dev", "新 Agent 已创建, ID: " .. self.id)
	return self
end

-- 启动Agent
function Agent:start(query)
	if self.status ~= M.AGENT_STATUS.IDLE then
		utils.log("warn", "Agent 已经在运行中，无法启动新任务")
		return false
	end

	utils.log("dev", "Agent:start 调用, 查询: " .. query)

	self:trigger_callback("on_start")

	self.status = M.AGENT_STATUS.THINKING
	self.stop_requested = false

	utils.log("dev", "Agent 状态设置为 THINKING, 准备思考任务")
	-- 创建新上下文
	self.current_context_id = context.create_context()
	context.add_message(self.current_context_id, "user", query)

	-- 启动思考任务阶段
	self:think_task(query)

	return true
end

-- 思考任务阶段
function Agent:think_task(query)
	self.status = M.AGENT_STATUS.THINKING
	self.stop_requested = false

	utils.log("dev", "Agent 状态设置为 THINKING, 准备启动主循环")
	-- 创建新任务和上下文
	self.current_task_id = task.create_task(query)

	-- 获取可用工具列表
	local available_tools = tool.get_all_function_call_formats()

	-- 调用Provider
	local messages = context.get_formatted_messages(self.current_context_id)
	local options = {
		stream = true,
		tools = available_tools,
		max_tokens = 2048,
	}

	local response_buffer = ""
	local function_call_buffer = {}

	provider.request(messages, options, function(content, meta)
		if meta and meta.error then
			self:output("❌ 错误: " .. (meta.error or "未知错误"))
			self:stop()
			return
		end

		if meta and meta.done then
			-- 处理完整的响应
			if #function_call_buffer > 0 then
				self:handle_function_calls(function_call_buffer)
			elseif response_buffer ~= "" then
				context.add_assistant_message(self.current_context_id, response_buffer)
				self:output("💡 " .. response_buffer)
				-- 直接文本回复完成，停止Agent
				self:stop()
			else
				-- 没有内容，也要停止Agent
				self:stop()
			end
			return
		end

		if meta and meta.type == "content" and content then
			response_buffer = response_buffer .. content
			self:output(content, { append = true })
		elseif meta and meta.type == "function_call" and content then
			table.insert(function_call_buffer, content)
		end
	end)
end

-- 处理函数调用
function Agent:handle_function_calls(function_calls)
	for _, func_call in ipairs(function_calls) do
		local tool_name = func_call.name
		local arguments = func_call.arguments

		-- 解析参数
		local success, parsed_args = pcall(vim.json.decode, arguments)
		if success then
			utils.log("info", "执行工具: " .. tool_name)
			self:output("🔧 执行工具: " .. tool_name)

			-- 执行工具
			local result = tool.execute_tool(tool_name, parsed_args)

			-- 添加工具消息到上下文
			context.add_tool_message(
				self.current_context_id,
				tool_name,
				func_call.call_id or utils.generate_uuid(),
				vim.json.encode(result)
			)

			-- 处理特殊工具的结果
			if tool_name == "think_task" then
				self:handle_think_task_result(result)
			elseif tool_name == "finish_task" then
				self:handle_finish_task_result(result)
			else
				self:output("✅ 工具执行结果: " .. (result.message or "完成"))
			end
		else
			utils.log("error", "解析函数参数失败: " .. arguments)
			self:output("❌ 函数参数解析失败")
		end
	end
end

-- 处理think_task结果
function Agent:handle_think_task_result(result)
	if result.success then
		self.current_task_id = result.task_id
		self:output("📝 任务创建成功!")
		self:output("📋 任务描述: " .. result.task_description)
		self:output("✅ 包含 " .. #result.todos .. " 个待办事项")

		-- 列出todos
		for i, todo in ipairs(result.todos) do
			self:output("  " .. i .. ". " .. todo)
		end

		-- 开始工作循环
		self:start_work_loop()
	else
		self:output("❌ 任务创建失败: " .. (result.error or "未知错误"))
		self:stop()
	end
end

-- 处理finish_task结果
function Agent:handle_finish_task_result(result)
	if result.success then
		self:output("🎉 任务完成!")
		self:output("📄 总结: " .. result.summary)
		self:stop()
	else
		self:output("❌ 任务完成标记失败: " .. (result.error or "未知错误"))
		self:stop()
	end
end

-- 开始工作循环
function Agent:start_work_loop()
	self.status = M.AGENT_STATUS.WORKING
	self.loop_running = true
	self:output("🚀 开始执行任务...")

	-- 异步执行工作循环
	vim.schedule(function()
		self:work_loop()
	end)
end

-- 工作循环
function Agent:work_loop()
	if self.stop_requested or not self.loop_running then
		return
	end

	-- 检查任务是否完成
	if task.is_task_complete(self.current_task_id) then
		self:output("✅ 所有任务已完成")
		self:stop()
		return
	end

	-- 获取下一个待执行的todo
	local next_todo = task.get_next_todo(self.current_task_id)
	if not next_todo then
		self:output("ℹ️  没有更多待办事项，任务可能已完成")
		self:stop()
		return
	end

	-- 标记todo为进行中
	task.update_todo_status(self.current_task_id, next_todo.id, task.TODO_STATUS.IN_PROGRESS)

	self:output("📌 正在处理: " .. next_todo.description)

	-- 处理当前todo
	self:process_todo(next_todo)
end

-- 处理单个todo
function Agent:process_todo(todo)
	-- 准备消息
	local todo_message = "请完成以下任务: " .. todo.description
	context.add_user_message(self.current_context_id, todo_message)

	-- 获取可用工具
	local available_tools = tool.get_all_function_call_formats()

	-- 调用Provider
	local messages = context.get_formatted_messages(self.current_context_id)
	local options = {
		stream = true,
		tools = available_tools,
		max_tokens = 2048,
	}

	local response_buffer = ""
	local function_call_buffer = {}

	provider.request(messages, options, function(content, meta)
		print("agent:process_todo.request.callback" .. content)
		if meta and meta.error then
			self:output("❌ 错误: " .. (meta.error or "未知错误"))
			task.update_todo_status(self.current_task_id, todo.id, task.TODO_STATUS.FAILED, "API请求失败")
			self:continue_work_loop()
			return
		end

		if meta and meta.done then
			-- 处理完整的响应
			if #function_call_buffer > 0 then
				self:handle_function_calls(function_call_buffer)
			elseif response_buffer ~= "" then
				context.add_assistant_message(self.current_context_id, response_buffer)
			end

			-- 继续工作循环
			self:continue_work_loop()
			return
		end

		if meta and meta.type == "content" and content then
			response_buffer = response_buffer .. content
			self:output(content, { append = true })
		elseif meta and meta.type == "function_call" and content then
			table.insert(function_call_buffer, content)
		end
	end)
end

-- 继续工作循环
function Agent:continue_work_loop()
	if self.loop_running and not self.stop_requested then
		-- 延迟一下继续循环，避免过快的递归
		vim.defer_fn(function()
			self:work_loop()
		end, 100)
	end
end

-- 停止Agent
function Agent:stop()
	if self.status == M.AGENT_STATUS.STOPPED then
		utils.log("dev", "Agent.stop 调用但状态已经是STOPPED，跳过")
		return
	end
	utils.log("dev", "Agent.stop 调用, 原状态: " .. self.status)
	self.stop_requested = true
	self.status = M.AGENT_STATUS.STOPPED
	utils.log("dev", "Agent状态已设置为: " .. self.status)
	self:trigger_callback("on_stop")
	utils.log("dev", "Agent.stop 完成，已触发on_stop回调")
end

-- 暂停Agent
function Agent:pause()
	if self.status == M.AGENT_STATUS.WORKING then
		utils.log("dev", "Agent.pause 调用, 状态设置为 PAUSED")
		self.status = M.AGENT_STATUS.PAUSED
		self:trigger_callback("on_pause")
		return true
	end
	return false
end

-- 恢复Agent
function Agent:resume()
	if self.status == M.AGENT_STATUS.PAUSED then
		utils.log("dev", "Agent.resume 调用, 状态恢复为 WORKING")
		self.status = M.AGENT_STATUS.WORKING
		self:trigger_callback("on_resume")
		return true
	end
	return false
end

-- 触发回调
function Agent:trigger_callback(event, ...)
	if self.callbacks and self.callbacks[event] then
		utils.log("dev", "触发回调: " .. event, { ... })
		pcall(self.callbacks[event], ...)
	end
end

-- 输出消息
function Agent:output(message, options)
	print("agent:output" .. message)
	options = options or {}

	if self.callbacks.on_output then
		self.callbacks.on_output(message, options)
	end

	-- 同时记录到日志
	utils.log("info", "Agent输出: " .. message)
end

-- 获取Agent状态
function Agent:get_status()
	return {
		id = self.id,
		status = self.status,
		current_task_id = self.current_task_id,
		current_context_id = self.current_context_id,
		loop_running = self.loop_running,
		stop_requested = self.stop_requested,
		created_at = self.created_at,
	}
end

-- 获取任务进度
function Agent:get_progress()
	if not self.current_task_id then
		return 0
	end

	return task.get_task_progress(self.current_task_id)
end

-- 获取任务详情
function Agent:get_task_details()
	if not self.current_task_id then
		return nil
	end

	return task.get_task_details(self.current_task_id)
end

-- 取消当前任务
function Agent:cancel_task()
	if self.current_task_id then
		task.cancel_task(self.current_task_id)
		self:output("❌ 任务已取消")
		self:stop()
		return true
	end
	return false
end

-- 模块级别的函数

-- 初始化Agent模块
function M.init(config)
	M.config = config
	M.current_agent = nil
	utils.log("info", "Agent模块初始化完成")
end

-- 启动新的Agent
function M.start(query, callbacks)
	local is_active = M.current_agent
		and (M.current_agent.status == M.AGENT_STATUS.THINKING or M.current_agent.status == M.AGENT_STATUS.WORKING)

	-- 添加调试日志
	if M.current_agent then
		utils.log("dev", "检查Agent状态: " .. M.current_agent.status)
		utils.log("dev", "THINKING状态: " .. M.AGENT_STATUS.THINKING)
		utils.log("dev", "WORKING状态: " .. M.AGENT_STATUS.WORKING)
		utils.log("dev", "STOPPED状态: " .. M.AGENT_STATUS.STOPPED)
		utils.log("dev", "is_active结果: " .. tostring(is_active))
	else
		utils.log("dev", "当前没有Agent实例")
	end

	if is_active then
		utils.log("warn", "已有Agent在运行中，请等待其完成后再启动新任务。")
		-- 可以在这里触发一个UI错误提示
		local ui = require("doodle.ui")
		ui.output_error("正在处理中，请等待完成后再发送新消息")
		return false
	end

	M.current_agent = Agent.new(callbacks)
	return M.current_agent:start(query)
end

-- 发送消息给Agent
function M.send_message(message, callbacks)
	-- 获取UI实例用于回调
	local ui = require("doodle.ui")

	-- 设置默认回调
	local default_callbacks = {
		on_start = function()
			ui.on_generate_start()
			utils.log("info", "开始处理消息: " .. message:sub(1, 50) .. "...")
			utils.log("dev", "Agent on_start 回调触发")
		end,

		on_progress = function(progress)
			if progress.type == "tool_use" then
				ui.on_tool_calling(progress.tool_name)
				utils.log("dev", "Agent on_progress 回调触发: tool_use - " .. progress.tool_name)
			end
		end,

		on_chunk = function(chunk)
			if chunk and chunk.content then
				ui.append(chunk.content, { highlight = ui.highlights.ASSISTANT_MESSAGE })
				utils.log("dev", "Agent on_chunk 回调触发, 内容: " .. chunk.content)
			end
		end,

		on_output = function(message, options)
			if options and options.append then
				ui.append(message, { highlight = ui.highlights.ASSISTANT_MESSAGE })
				utils.log("dev", "Agent on_output 回调触发 (streaming), 内容: " .. message)
			else
				ui.output(message, { highlight = ui.highlights.ASSISTANT_MESSAGE })
				utils.log("dev", "Agent on_output 回调触发 (完整消息), 内容: " .. message)
			end
		end,

		on_complete = function(result)
			ui.on_generate_complete()
			utils.log("info", "消息处理完成")
			utils.log("dev", "Agent on_complete 回调触发")
		end,

		on_error = function(error_msg)
			ui.on_generate_error(error_msg)
			utils.log("error", "消息处理失败: " .. (error_msg or "未知错误"))
			utils.log("dev", "Agent on_error 回调触发")
		end,

		on_stop = function()
			ui.on_generate_complete()
			utils.log("info", "Agent已停止")
			utils.log("dev", "Agent on_stop 回调触发")
		end,
	}

	-- 合并用户提供的回调
	if callbacks then
		for key, callback in pairs(callbacks) do
			default_callbacks[key] = callback
		end
	end

	-- 启动新的处理任务
	return M.start(message, default_callbacks)
end

-- 停止当前Agent
function M.stop()
	if M.current_agent then
		M.current_agent:stop()
		return true
	end
	return false
end

-- 暂停当前Agent
function M.pause()
	if M.current_agent then
		return M.current_agent:pause()
	end
	return false
end

-- 恢复当前Agent
function M.resume()
	if M.current_agent then
		return M.current_agent:resume()
	end
	return false
end

-- 获取当前Agent状态
function M.get_status()
	if M.current_agent then
		return M.current_agent:get_status()
	end
	return nil
end

-- 获取当前任务进度
function M.get_progress()
	if M.current_agent then
		return M.current_agent:get_progress()
	end
	return 0
end

-- 获取当前任务详情
function M.get_task_details()
	if M.current_agent then
		return M.current_agent:get_task_details()
	end
	return nil
end

-- 取消当前任务
function M.cancel_task()
	if M.current_agent then
		return M.current_agent:cancel_task()
	end
	return false
end

-- 检查Agent是否在运行
function M.is_running()
	return M.current_agent and M.current_agent.status ~= M.AGENT_STATUS.STOPPED
end

-- 获取Agent历史
function M.get_history()
	if M.current_agent and M.current_agent.current_context_id then
		return context.get_messages(M.current_agent.current_context_id)
	end
	return {}
end

-- 清理Agent资源
function M.cleanup()
	if M.current_agent then
		M.current_agent:stop()

		-- 清理上下文
		if M.current_agent.current_context_id then
			context.delete_context(M.current_agent.current_context_id)
		end

		M.current_agent = nil
	end

	utils.log("info", "Agent资源清理完成")
end

-- 重置Agent
function M.reset()
	M.cleanup()
	utils.log("info", "Agent重置完成")
end

-- 获取Agent统计信息
function M.get_stats()
	local stats = {
		current_agent = M.current_agent and M.current_agent:get_status() or nil,
		is_running = M.is_running(),
		total_tasks = task.count_tasks and task.count_tasks() or 0,
		active_tasks = #task.get_active_tasks(),
	}

	return stats
end

-- 导出Agent数据
function M.export_data()
	local export_data = {
		current_agent_status = M.get_status(),
		history = M.get_history(),
		task_details = M.get_task_details(),
		exported_at = utils.get_timestamp(),
	}

	return export_data
end

return M
    """,
        },
    }


def print_results(language_name, results, test_code=None):
    """输出测试结果的通用函数"""
    print(f"\n{'=' * 80}")
    print(f"  {language_name.upper()} 测试结果")
    print(f"{'=' * 80}")

    # 显示原始测试代码
    if test_code:
        print(f"\n📄 原始测试代码:")
        print(f"{'-' * 60}")
        print(test_code.strip())
        print(f"{'-' * 60}")

    # 显示提取结果
    print(f"\n🔍 提取结果:")
    total_items = sum(len(items) for items in results.values())
    print(f"总共提取到 {total_items} 个代码块")

    for category, items in results.items():
        if items:  # 只显示有内容的类别
            print(f"\n## 📂 类别: {category} ({len(items)} 个)")
            print(f"{'·' * 40}")
            for i, item in enumerate(items, 1):
                print(f"\n  [{i}] 代码块:")
                # 为每行添加缩进以便于阅读
                indented_code = "\n".join(
                    f"      {line}" for line in item.strip().split("\n")
                )
                print(indented_code)
                if i < len(items):  # 如果不是最后一个，添加分隔线
                    print(f"  {'-' * 50}")


def run_test_for_language(splitter, language_key, test_case):
    """运行指定语言的测试"""
    print(f"\n🚀 开始测试 {test_case['name']} 语言...")
    try:
        results = splitter.split_text(test_case["code"], language_key)
        print_results(test_case["name"], results, test_case["code"])
        return True
    except Exception as e:
        print(f"❌ {test_case['name']} 测试失败: {e}")
        return False


def run_all_tests(splitter, test_cases):
    """运行所有语言的测试"""
    print(f"\n🚀 开始运行所有语言测试...")

    total_tests = len(test_cases)
    successful_tests = 0

    for language_key, test_case in test_cases.items():
        if run_test_for_language(splitter, language_key, test_case):
            successful_tests += 1

    print(f"\n{'=' * 60}")
    print(f"  测试完成! {successful_tests}/{total_tests} 个语言测试成功")
    print(f"{'=' * 60}")


def main():
    """主函数"""
    # 设置命令行参数
    parser = argparse.ArgumentParser(
        description="Tree-sitter 代码分割测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python demo.py                    # 运行所有语言测试
  python demo.py -l python          # 只测试 Python
  python demo.py -l go              # 只测试 Go
  python demo.py --list-languages   # 显示支持的语言列表
        """,
    )

    # 获取所有测试用例
    test_cases = get_all_test_cases()

    # 添加语言选择参数
    parser.add_argument(
        "-l", "--language", choices=list(test_cases.keys()), help="指定要测试的编程语言"
    )

    # 添加列出支持语言的参数
    parser.add_argument(
        "--list-languages", action="store_true", help="显示所有支持的编程语言"
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 如果用户要求列出支持的语言
    if args.list_languages:
        print("支持的编程语言:")
        print("=" * 40)
        for key, test_case in test_cases.items():
            print(f"  {key:<12} - {test_case['name']}")
        print("=" * 40)
        print(f"总共支持 {len(test_cases)} 种编程语言")
        return

    # 初始化代码分割器
    splitter = CodeSplitter(LANGUAGE_NODE_MAP)

    # 根据参数运行测试
    if args.language:
        # 运行指定语言的测试
        test_case = test_cases[args.language]
        print(test_case["code"])
        success = run_test_for_language(splitter, args.language, test_case)


if __name__ == "__main__":
    main()
