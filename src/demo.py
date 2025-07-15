import tree_sitter
from tree_sitter_language_pack import get_language, get_parser

# # --- 步骤 2 中定义的映射 ---
# LANGUAGE_NODE_MAP = {
#     "python": {
#         "function": ["function_definition"],
#         "class": ["class_definition"],
#         # "import": ["import_statement", "from_import_statement"],
#     },
#     "javascript": {
#         "function": ["function_declaration", "arrow_function", "method_definition"],
#         "class": ["class_declaration"],
#         "variable": ["lexical_declaration", "variable_declaration"],
#     },
#     "rust": {
#         "function": ["function_item"],
#         "struct": ["struct_item"],
#         "trait": ["trait_item"],
#         "impl": ["impl_item"],
#     },
# }


LANGUAGE_NODE_MAP = {
    "python": {
        # "import": ["import_statement", "from_import_statement"],
        "function": ["function_definition"],
        "class": ["class_definition"],
        # 'decorated_definition' captures functions/classes with decorators.
        # The query will find both the decorator and the definition itself,
        # so you might get duplicates if you also query for function_definition.
        # It's powerful if you want the whole block including decorators.
        "decorated_definition": ["decorated_definition"],
        "variable_assignment": [
            "assignment"
        ],  # Top-level assignments like 'CONSTANT = 10'
    },
    "go": {
        # 修改查询语法以正确处理注释顺序
        "struct": [
            """
            (
              (comment)* @comment.struct
              .
              (type_declaration
                (type_spec
                  type: (struct_type)
                )
              ) @struct
            )
            """
        ],
        "interface": [
            """
            (
              (comment)* @comment.interface  
              .
              (type_declaration
                (type_spec type: (interface_type))
              ) @interface
            )
            """
        ],
    },
    # We use 'typescript' parser which is a superset and works perfectly for JS.
    "javascript": {
        "import": ["import_statement"],
        "function": ["function_declaration", "method_definition", "arrow_function"],
        "class": ["class_declaration"],
        # 'lexical_declaration' is for `let` and `const`.
        # 'variable_declaration' is for `var`. Captures things like 'const PI = 3.14;'
        "variable": ["lexical_declaration", "variable_declaration"],
        "export": ["export_statement"],
    },
    "typescript": {
        "import": ["import_statement"],
        "function": ["function_declaration", "method_definition", "arrow_function"],
        "class": ["class_declaration"],
        "interface": ["interface_declaration"],
        "type_alias": ["type_alias_declaration"],
        "enum": ["enum_declaration"],
        # 'public_field_definition' is for class properties like 'public name: string;'
        "class_property": ["public_field_definition"],
        "variable": ["lexical_declaration", "variable_declaration"],
        "export": ["export_statement"],
    },
    "java": {
        "import": ["import_declaration"],
        "class": ["class_declaration"],
        "interface": ["interface_declaration"],
        "enum": ["enum_declaration"],
        # In Java, functions are methods or constructors.
        "function": ["method_declaration", "constructor_declaration"],
        # Captures class member variables.
        "field": ["field_declaration"],
    },
    "rust": {
        "import": ["use_declaration"],
        "function": ["function_item"],
        "struct": ["struct_item"],
        "enum": ["enum_item"],
        # 'trait' is Rust's equivalent of an interface.
        "trait": ["trait_item"],
        # 'impl' blocks are implementations of methods for structs or traits.
        "implementation": ["impl_item"],
        "module": ["mod_item"],
        "type_alias": ["type_item"],
        "constant": ["const_item"],
        "macro": ["macro_definition"],
    },
    "lua": {
        # Lua's `require` is a function call, not a keyword.
        # This captures `local mod = require("module")`. The query will grab the whole line.
        "import": ["local_statement"],
        # This captures `function foo() end` and `local function bar() end`.
        "function": ["function_declaration"],
        # Lua has no built-in classes. They are simulated with tables.
        # This captures `MyTable = {}`, a common pattern for creating modules/classes.
        # This is a SYNTACTIC approximation.
        "table_assignment": ["assignment_statement"],
    },
}


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
            for node_type in node_types:
                target_types[node_type] = category
        return target_types

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

    def split_text(self, code: str, language: str) -> dict:
        """
        对源代码进行分割，提取出定义的代码块

        :param code: 源代码字符串
        :param language: 语言名称（如 'python', 'javascript'）
        :return: 一个字典，键是通用类别，值是提取到的代码块列表
        """
        code_bytes = bytes(code, "utf8")
        # 忽略类型检查错误
        parser = get_parser(language)  # type: ignore
        tree = parser.parse(code_bytes)

        target_node_types = self._get_target_node_types(language)
        if not target_node_types:
            return {}

        query = self._build_query(language, target_node_types)
        # 使用 matches() 而不是 captures() 来保持节点关联关系
        matches = query.matches(tree.root_node)

        results = {category: [] for category in self.language_map[language].keys()}
        
        print(f"Total matches: {len(matches)}")

        # 处理每个匹配，每个匹配中的captures是相关联的
        for match in matches:
            # match是一个tuple: (pattern_index, captures_dict)
            pattern_index, captures_dict = match
            
            print(f"Match captures: {list(captures_dict.keys())}")
            
            # 找到目标节点和对应的注释
            for capture_name, nodes in captures_dict.items():
                if not capture_name.startswith("comment."):
                    # 这是目标节点
                    target_type = capture_name
                    comment_key = f"comment.{target_type}"
                    
                    for target_node in nodes:
                        if target_node and hasattr(target_node, 'text') and target_node.text is not None:
                            # 获取这个匹配中对应的注释
                            comments = captures_dict.get(comment_key, [])
                            
                            # 构建完整的代码块（注释 + 目标节点）
                            if comments:
                                # 按位置排序注释（应该在目标节点之前）
                                comments.sort(key=lambda x: x.start_byte)
                                comment_text = "\n".join([c.text.decode("utf8") for c in comments if c.text is not None])
                                target_text = target_node.text.decode("utf8")
                                full_text = comment_text + "\n" + target_text
                            else:
                                full_text = target_node.text.decode("utf8")
                            
                            results[target_type].append(full_text)

        return results


# --- 使用示例 ---

if __name__ == "__main__":
    splitter = CodeSplitter(LANGUAGE_NODE_MAP)

    #     # === 示例 1: Python 代码 ===
    #     python_code = """
    # import os
    # from math import sqrt
    #
    # class MyClass:
    #     def __init__(self):
    #         self.value = 0
    #
    #     def get_value(self):
    #         return self.value
    #
    # def helper_function(x):
    #     return sqrt(x)
    # """
    #     print("--- Splitting Python Code ---")
    #     python_results = splitter.split_text(python_code, "python")
    #     print(python_results)
    #     # for category, items in python_results.items():
    #     #     print(f"\n## Category: {category}")
    #     #     for i, item in enumerate(items):
    #     #         print(f"  {i + 1}: {item.strip()}")
    #
    #     # === 示例 2: JavaScript 代码 ===
    #     js_code = """
    # import React from 'react';
    #
    # const PI = 3.14;
    #
    # function calculateArea(radius) {
    #     return PI * radius * radius;
    # }
    #
    # class Circle {
    #     constructor(radius) {
    #         this.radius = radius;
    #     }
    #
    #     getArea() {
    #         return calculateArea(this.radius);
    #     }
    # }
    # """
    #     print("\n\n--- Splitting JavaScript Code ---")
    #     js_results = splitter.split_text(js_code, "javascript")
    #     for category, items in js_results.items():
    #         print(f"\n## Category: {category}")
    #         for i, item in enumerate(items):
    #             print(f"  {i + 1}: {item.strip()}")
    #
    #     # === 示例 3: Rust 代码 ===
    #     rust_code = """
    #     struct Point {
    #         x: f64,
    #         y: f64,
    #     }
    #
    #     impl Point {
    #         fn origin() -> Point {
    #             Point { x: 0.0, y: 0.0 }
    #         }
    #     }
    #     """
    #     print("\n\n--- Splitting Rust Code ---")
    #     rust_results = splitter.split_text(rust_code, "rust")
    #     for category, items in rust_results.items():
    #         print(f"\n## Category: {category}")
    #         for i, item in enumerate(items):
    #             print(f"  {i + 1}: {item.strip()}")

    # golang

    golang_code = """
    package server

    import (
        "fmt"
        "io"
        "net"

        "github.com/doodleEsc/godemo/pkg/tlv"
    )

// Handler
// this is for handler
type Handler interface {
	Handle(packet *tlv.Packet, conn io.Writer) error
	ValidTag() byte
}


// Handler2
// this is for handler2
type Handler2 interface {
	Handle(packet *tlv.Packet, conn io.Writer) error
	ValidTag() byte
}

// Server aasdfasdfsaf
// asdfasf
type Server struct {
//asdfasfasfsafsfasdf
	listener net.Listener
	handler  Handler
	done     chan struct{}
}


    // NewServer 创建一个新的TLV服务器
    func NewServer(addr string, handler Handler) (*Server, error) {
        listener, err := net.Listen("tcp", addr)
        if err != nil {
            return nil, fmt.Errorf("failed to listen: %w", err)
        }
        return &Server{
            listener: listener,
            handler:  handler,
            done:     make(chan struct{}),
        }, nil
    }

    // Start 启动服务器
    func (s *Server) Start() error {
        fmt.Printf("Server listening on %s\n", s.listener.Addr())
        for {
            conn, err := s.listener.Accept()
            if err != nil {
                select {
                case <-s.done:
                    return nil // Server is shutting down
                default:
                    fmt.Printf("Failed to accept connection: %v\n", err)
                    continue
                }
            }
            go s.handleConnection(conn)
        }
    }

    // Stop 停止服务器
    func (s *Server) Stop() error {
        close(s.done)
        return s.listener.Close()
    }

    // handleConnection 处理单个客户端连接
    func (s *Server) handleConnection(conn net.Conn) {
        defer conn.Close()
        fmt.Printf("New connection from %s\n", conn.RemoteAddr())

        tlvCodec := tlv.NewTLV()
        for {
            packet, err := tlvCodec.DecodeFrom(conn, s.handler.ValidTag())
            if err != nil {
                if err == io.EOF {
                    fmt.Printf("Connection closed by %s\n", conn.RemoteAddr())
                } else {
                    fmt.Printf("Error decoding TLV packet from %s: %v\n", conn.RemoteAddr(), err)
                }
                return
            }

            if err := s.handler.Handle(packet, conn); err != nil {
                fmt.Printf("Error handling TLV packet from %s: %v\n", conn.RemoteAddr(), err)
                return
            }
        }
    }
    """
    print("\n\n--- Splitting Rust Code ---")
    rust_results = splitter.split_text(golang_code, "go")
    for category, items in rust_results.items():
        print(f"\n## Category: {category}")
        for i, item in enumerate(items):
            print(f"  {i + 1}: {item.strip()}")
