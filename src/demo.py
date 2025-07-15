import tree_sitter
from tree_sitter_language_pack import get_language, get_parser
import argparse

# 在LANGUAGE_NODE_MAP的顶部添加合并配置说明
# 配置说明：
# _merge_config: 指定哪些类别需要合并
# - enabled: 是否启用合并
# - max_gap_lines: 允许的最大行间隔（超过此间隔的代码块不会合并）
# - preserve_order: 是否保持原始顺序

LANGUAGE_NODE_MAP = {
    "python": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_definition) @function
            )
            """
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_definition) @class
            )
            """
        ],
        "decorated_definition": [
            """
            (
              (comment)* @comment.decorated_definition
              .
              (decorated_definition) @decorated_definition
            )
            """
        ],
        "variable_assignment": [
            """
            (
              (comment)* @comment.variable_assignment
              .
              (module
                (expression_statement
                    (assignment) @variable_assignment
                )
              )
            )
            """
        ],
        "import": [
            """
            (
              (comment)* @comment.import
              .
              (import_statement) @import
            )
            """,
            """
            (
              (comment)* @comment.import
              .
              (import_from_statement) @import
            )
            """,
        ],
        # Python import合并配置
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": -1, "preserve_order": True}
        },
    },
    "go": {
        "package": [
            """
            (
              (comment)* @comment.package
              .
              (package_clause) @package
            )
            """
        ],
        "import": [
            """
            (
              (comment)* @comment.import
              .
              (import_declaration) @import
            )
            """
        ],
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
        "type_alias": [
            """
            (
              (comment)* @comment.type_alias
              .
              (type_declaration
                (type_spec
                  type: (type_identifier)
                )
              ) @type_alias
            )
            """
        ],
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_declaration) @function
            )
            """,
            """
            (
              (comment)* @comment.function
              .
              (method_declaration) @function
            )
            """,
        ],
        "variable": [
            """
            (
              (comment)* @comment.variable
              .
              (var_declaration) @variable
            )
            """
        ],
        "constant": [
            """
            (
              (comment)* @comment.constant
              .
              (const_declaration) @constant
            )
            """
        ],
        # Go import和package通常不需要合并，因为Go有import块的概念
        "_merge_config": {
            # Go一般不需要合并，因为有import()语法
        },
    },
    "javascript": {
        "import": [
            """
            (
              (comment)* @comment.import
              .
              (import_statement) @import
            )
            """
        ],
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_declaration) @function
            )
            """,
            """
            (
              (comment)* @comment.function
              .
              (method_definition) @function
            )
            """,
            """
            (
              (comment)* @comment.function
              .
              (lexical_declaration
                (variable_declarator
                    value: (arrow_function)
                )
              ) @function
            )
            """,
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_declaration) @class
            )
            """
        ],
        "variable": [
            """
            (
              (comment)* @comment.variable
              .
              (lexical_declaration) @variable
            )
            """,
            """
            (
              (comment)* @comment.variable
              .
              (variable_declaration) @variable
            )
            """,
        ],
        "export": [
            """
            (
              (comment)* @comment.export
              .
              (export_statement) @export
            )
            """
        ],
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "export": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "variable": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
        },
    },
    "typescript": {
        "import": [
            """
            (
              (comment)* @comment.import
              .
              (import_statement) @import
            )
            """
        ],
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_declaration) @function
            )
            """,
            """
            (
              (comment)* @comment.function
              .
              (method_definition) @function
            )
            """,
            """
            (
              (comment)* @comment.function
              .
              (lexical_declaration
                (variable_declarator
                    value: (arrow_function)
                )
              ) @function
            )
            """,
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_declaration) @class
            )
            """
        ],
        "interface": [
            """
            (
              (comment)* @comment.interface
              .
              (interface_declaration) @interface
            )
            """
        ],
        "type_alias": [
            """
            (
              (comment)* @comment.type_alias
              .
              (type_alias_declaration) @type_alias
            )
            """
        ],
        "enum": [
            """
            (
              (comment)* @comment.enum
              .
              (enum_declaration) @enum
            )
            """
        ],
        "variable": [
            """
            (
              (comment)* @comment.variable
              .
              (lexical_declaration) @variable
            )
            """,
            """
            (
              (comment)* @comment.variable
              .
              (variable_declaration) @variable
            )
            """,
        ],
        "export": [
            """
            (
              (comment)* @comment.export
              .
              (export_statement) @export
            )
            """
        ],
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "export": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "type_alias": {
                "enabled": True,
                "max_gap_lines": -1,
                "preserve_order": True,
            },
            "variable": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
        },
    },
    "java": {
        "import": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.import
              .
              (import_declaration) @import
            )
            """,
        ],
        "class": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.class
              .
              (class_declaration) @class
            )
            """
        ],
        "interface": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.interface
              .
              (interface_declaration) @interface
            )
            """
        ],
        "enum": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.enum
              .
              (enum_declaration
                body:(enum_body)
              ) @enum
            )
            """
        ],
        "function": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.function
              .
              (method_declaration
                body:(block)
              ) @function
            )
            """,
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.function
              .
              (constructor_declaration
                body:(constructor_body)
              ) @function
            )
            """,
        ],
        # Java import合并配置 - 这是最需要的
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": -1, "preserve_order": True}
        },
    },
    "rust": {
        "import": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.import
              .
              (use_declaration) @import
            )
            """
        ],
        "function": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.function
              .
              (function_item) @function
            )
            """
        ],
        "struct": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.struct
              .
              (struct_item) @struct
            )
            """
        ],
        "enum": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.enum
              .
              (enum_item) @enum
            )
            """
        ],
        "trait": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.trait
              .
              (trait_item) @trait
            )
            """
        ],
        "implementation": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.implementation
              .
              (impl_item) @implementation
            )
            """
        ],
        "module": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.module
              .
              (mod_item) @module
            )
            """
        ],
        "type_alias": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.type_alias
              .
              (type_item) @type_alias
            )
            """
        ],
        "constant": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.constant
              .
              (const_item) @constant
            )
            """
        ],
        "macro": [
            """
            (
              [
                (line_comment)
                (block_comment)
              ]* @comment.macro
              .
              (macro_definition) @macro
            )
            """
        ],
        # Rust use语句合并配置
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": 2, "preserve_order": True},
            "type_alias": {"enabled": True, "max_gap_lines": 2, "preserve_order": True},
            "constant": {"enabled": True, "max_gap_lines": 2, "preserve_order": True},
        },
    },
    "c": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_definition) @function
            )
            """
        ],
        "struct": [
            """
            (
              (comment)* @comment.struct
              .
              (type_definition 
                (struct_specifier)
              ) @struct
            )
            """
        ],
        "enum": [
            """
            (
              (comment)* @comment.enum
              .
              (type_definition 
                (enum_specifier)
              ) @enum
            )
            """
        ],
        "typedef": [
            """
            (
              (comment)* @comment.typedef
              .
              (type_definition) @typedef
            )
            """
        ],
        "variable": [
            """
            (
              (comment)* @comment.variable
              .
              (translation_unit
                (declaration) @variable
              )
            )
            """
        ],
        "include": [
            """
            (
              (comment)* @comment.include
              .
              (preproc_include) @include
            )
            """
        ],
        # C include语句合并配置
        "_merge_config": {
            "include": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "variable": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "typedef": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
        },
    },
    "cpp": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_definition) @function
            )
            """
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_specifier) @class
            )
            """
        ],
        "struct": [
            """
            (
              (comment)* @comment.struct
              .
              (struct_specifier) @struct
            )
            """
        ],
        "enum": [
            """
            (
              (comment)* @comment.enum
              .
              (enum_specifier) @enum
            )
            """
        ],
        "namespace": [
            """
            (
              (comment)* @comment.namespace
              .
              (namespace_definition) @namespace
            )
            """
        ],
        "template": [
            """
            (
              (comment)* @comment.template
              .
              (template_declaration) @template
            )
            """
        ],
        "typedef": [
            """
            (
              (comment)* @comment.typedef
              .
              (type_definition) @typedef
            )
            """
        ],
        "include": [
            """
            (
              (comment)* @comment.include
              .
              (preproc_include) @include
            )
            """
        ],
        "macro": [
            """
            (
              (comment)* @comment.macro
              .
              (preproc_def) @macro
            )
            """,
            """
            (
              (comment)* @comment.macro
              .
              (preproc_ifdef) @macro
            )

            """,
        ],
        # C++ include语句合并配置
        "_merge_config": {
            "include": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "macro": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
        },
    },
    "lua": {
        "function": [
            """(function_declaration) @function""",
            """(function_definition) @function""",
        ],
        # "variable": ["""(variable_declaration) @variable"""],
        # "assignment": ["""(assignment_statement) @assignment"""],
        # "table": ["""(table_constructor) @table"""],
        # # Lua合并配置 - 合并相邻的相同类型定义
        # "_merge_config": {
        #     "function": {"enabled": True, "max_gap_lines": 1, "preserve_order": True},
        #     "variable": {"enabled": True, "max_gap_lines": 1, "preserve_order": True},
        # },
    },
    "php": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_definition) @function
            )
            """
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_declaration) @class
            )
            """
        ],
        "interface": [
            """
            (
              (comment)* @comment.interface
              .
              (interface_declaration) @interface
            )
            """
        ],
        "trait": [
            """
            (
              (comment)* @comment.trait
              .
              (trait_declaration) @trait
            )
            """
        ],
        "namespace": [
            """
            (
              (comment)* @comment.namespace
              .
              (namespace_definition) @namespace
            )
            """
        ],
        "include": [
            """
            (
              (comment)* @comment.include
              .
              (include_expression) @include
            )
            """,
            """
            (
              (comment)* @comment.include
              .
              (require_expression) @include
            )
            """,
        ],
        # PHP include/require语句合并配置
        "_merge_config": {
            "include": {"enabled": True, "max_gap_lines": 2, "preserve_order": True}
        },
    },
    "ruby": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (method) @function
            )
            """
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class) @class
            )
            """
        ],
        "module": [
            """
            (
              (comment)* @comment.module
              .
              (module) @module
            )
            """
        ],
        "constant": [
            """
            (
              (comment)* @comment.constant
              .
              (constant) @constant
            )
            """
        ],
    },
    "swift": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_declaration) @function
            )
            """
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_declaration) @class
            )
            """
        ],
        "struct": [
            """
            (
              (comment)* @comment.struct
              .
              (struct_declaration) @struct
            )
            """
        ],
        "enum": [
            """
            (
              (comment)* @comment.enum
              .
              (enum_declaration) @enum
            )
            """
        ],
        "protocol": [
            """
            (
              (comment)* @comment.protocol
              .
              (protocol_declaration) @protocol
            )
            """
        ],
        "extension": [
            """
            (
              (comment)* @comment.extension
              .
              (extension_declaration) @extension
            )
            """
        ],
        "import": [
            """
            (
              (comment)* @comment.import
              .
              (import_declaration) @import
            )
            """
        ],
        # Swift import语句合并配置
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": 1, "preserve_order": True}
        },
    },
    "kotlin": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_declaration) @function
            )
            """
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_declaration) @class
            )
            """
        ],
        "interface": [
            """
            (
              (comment)* @comment.interface
              .
              (interface_declaration) @interface
            )
            """
        ],
        "enum": [
            """
            (
              (comment)* @comment.enum
              .
              (enum_declaration) @enum
            )
            """
        ],
        "object": [
            """
            (
              (comment)* @comment.object
              .
              (object_declaration) @object
            )
            """
        ],
        "import": [
            """
            (
              (comment)* @comment.import
              .
              (import_header) @import
            )
            """
        ],
        # Kotlin import语句合并配置
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": 1, "preserve_order": True}
        },
    },
    "scala": {
        "function": [
            """
            (
              (comment)* @comment.function
              .
              (function_definition) @function
            )
            """
        ],
        "class": [
            """
            (
              (comment)* @comment.class
              .
              (class_definition) @class
            )
            """
        ],
        "object": [
            """
            (
              (comment)* @comment.object
              .
              (object_definition) @object
            )
            """
        ],
        "trait": [
            """
            (
              (comment)* @comment.trait
              .
              (trait_definition) @trait
            )
            """
        ],
        "import": [
            """
            (
              (comment)* @comment.import
              .
              (import_declaration) @import
            )
            """
        ],
        # Scala import语句合并配置
        "_merge_config": {
            "import": {"enabled": True, "max_gap_lines": 2, "preserve_order": True}
        },
    },
}


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
    // 命名空间定义
    namespace App\\Models;
    
    // 文件包含
    require_once 'vendor/autoload.php';
    include_once 'config/database.php';
    
    // 接口定义
    interface UserRepositoryInterface {
        // 用户仓储接口
        public function findById(int $id): ?User;
        public function save(User $user): bool;
    }
    
    // Trait定义
    trait TimestampsTrait {
        // 时间戳特征
        protected $created_at;
        protected $updated_at;
        
        public function updateTimestamps(): void {
            // 更新时间戳
            $this->updated_at = date('Y-m-d H:i:s');
        }
    }
    
    // 类定义
    class User {
        // 用户类
        use TimestampsTrait;
        
        private int $id;
        private string $name;
        private string $email;
        
        // 构造函数
        public function __construct(int $id, string $name, string $email) {
            // 用户构造函数
            $this->id = $id;
            $this->name = $name;
            $this->email = $email;
            $this->created_at = date('Y-m-d H:i:s');
        }
        
        // 方法定义
        public function getName(): string {
            // 获取用户名
            return $this->name;
        }
        
        public function setName(string $name): void {
            // 设置用户名
            $this->name = $name;
            $this->updateTimestamps();
        }
    }
    
    // 函数定义
    function validateEmail(string $email): bool {
        // 验证邮箱格式
        return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
    }
    ?>
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
    --[[
    这是一个旨在覆盖所有 Lua Tree-sitter 节点类型的综合测试文件。
    ]]

    -- 1. 变量声明和字面量 (Variable Declarations & Literals)
    -- 全局变量, nil 和布尔值
    global_var = nil
    is_active = true

    -- 本地变量, 数字 (整数, 浮点数, 科学记数法)
    local num, hex_num = 123, 0xFF
    local float_num = 0.5e-3

    -- 字符串 (单引号, 双引号, 长字符串)
    local single_quote = 'hello'
    local double_quote = "world"
    local long_string = [[
    这是一个
    带有换行的长字符串。
    ]]

    -- 2. Table (构造和索引)
    local my_table = {
    "list_value_1", -- 列表部分
    key = "record_value", -- 记录部分
    ["another-key"] = false,
    [hex_num] = "value from hex key",
    10.5, -- 列表部分
    ; -- 可选的分隔符
    }
    local accessed_val = my_table.key
    local other_val = my_table["another-key"]

    -- 3. 表达式和操作符 (Expressions & Operators)
    -- 算术, 连接, 长度
    local calculation = (num + 1) * 2 ^ 3 / 4 % 3
    local full_str = single_quote .. " " .. double_quote
    local list_len = #my_table

    -- 关系和逻辑
    if (list_len > 1 and not other_val) or global_var ~= nil then
    print("Condition met")
    elseif calculation <= 0 then
    print("Calculation is zero or negative")
    else
    print("Default case")
    end

    -- 位操作 (Lua 5.3+)
    local bit_ops = (num & 0xF0) | (num ~ 0x0F) << 1 >> 2

    -- 4. 函数 (定义, 调用, 方法, 可变参数)
    -- 全局函数
    function global_func(a, b)
    return a + b, a - b -- 多返回值
    end

    -- 本地函数和可变参数
    local function variadic_func(...)
    local args = { ... }
    return #args
    end

    -- 匿名函数 (lambda)
    local mult = function(x, y) return x * y end

    local sum, diff = global_func(10, 4) -- 多重赋值
    local arg_count = variadic_func(1, 2, "a")

    -- 5. 控制流 (Control Flow)
    local i = 5
    while i > 0 do
    i = i - 1
    if i == 2 then
        break -- break 语句
    end
    end

    repeat
    i = i + 1
    until i >= 10

    -- 数字 for 循环
    for j = 1, 10, 2 do
    if j == 5 then goto skip_label end
    end

    ::skip_label:: -- 标签 (label)

    -- 泛型 for 循环
    for k, v in pairs(my_table) do
    print(k, v)
    end

    -- 6. 面向对象和元表 (OOP & Metatables)
    local MyClass = {}
    MyClass.__index = MyClass

    function MyClass:new(name) -- 方法定义 (使用 :)
    local obj = setmetatable({}, self)
    obj.name = name
    return obj
    end

    function MyClass:greet()
    print("Hello, " .. self.name)
    end

    -- 元方法
    setmetatable(MyClass, {
    __tostring = function() return "MyClassType" end,
    __call = function(cls, ...) return cls:new(...) end,
    })

    local instance = MyClass:new("Lua") -- 方法调用
    instance:greet()

    local another_instance = MyClass("Metatable-Call") -- 使用 __call 元方法

    -- 7. 模块系统
    local path = require("path") -- 模块导入

    local aaa = function()
    end

    return my_table -- 模块返回值
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
