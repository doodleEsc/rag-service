import tree_sitter
from tree_sitter_language_pack import get_language, get_parser

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
        "merge_config": {
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
        "merge_config": {
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
        "merge_config": {
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
        "merge_config": {
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
        "merge_config": {
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
        "merge_config": {
            "import": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "type_alias": {
                "enabled": True,
                "max_gap_lines": -1,
                "preserve_order": True,
            },
            "constant": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
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
        "merge_config": {
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
        "merge_config": {
            "include": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "macro": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
        },
    },
    "lua": {
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
              (variable_declaration
               (assignment_statement
                (expression_list
                    value:(function_definition)
                )
               )
              ) @function
            )
            """,
        ],
        "variable": [
            """
            (
                (comment)* @comment.variable
                .
                (chunk
                    (variable_declaration
                        (assignment_statement
                            (expression_list
                                value: (function_call)
                            )
                        )
                    ) @variable
                )
            )
            """
        ],
        "assignment": [
            """
            (
                (comment)* @comment.assignment
                .
                (chunk
                    (assignment_statement) @assignment
                )
            )
            """
        ],
        "merge_config": {
            "variable": {"enabled": True, "max_gap_lines": 1, "preserve_order": True},
            "assignment": {
                "enabled": True,
                "max_gap_lines": -1,
                "preserve_order": True,
            },
        },
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
            """,
            """
            (
              (comment)* @comment.namespace
              .
              (namespace_use_declaration) @namespace
            )
            """,
        ],
        "include": [
            """
            (
              (comment)* @comment.include
              .
              (expression_statement
                (include_expression)
              ) @include
            )
            """,
            """
            (
              (comment)* @comment.include
              .
              (expression_statement
                (require_expression)
              ) @include
            )
            """,
            """
            (
              (comment)* @comment.include
              .
              (expression_statement
                (require_once_expression)
              ) @include
            )
            """,
        ],
        # PHP include/require语句合并配置
        "merge_config": {
            "include": {"enabled": True, "max_gap_lines": 2, "preserve_order": True},
            "namespace": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
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
    },
    "kotlin": {
        "function": [
            """
            (
              [(line_comment)(multiline_comment)]* @comment.function
              .
              (function_declaration) @function
            )
            """
        ],
        "class": [
            """
            (
              [(line_comment)(multiline_comment)]* @comment.class
              .
              (class_declaration) @class
            )
            """
        ],
        "enum": [
            """
            (
              [(line_comment)(multiline_comment)]* @comment.enum
              .
              (class_declaration
                (enum_class_body)
              ) @enum
            )
            """
        ],
        "object": [
            """
            (
              [(line_comment)(multiline_comment)]* @comment.object
              .
              (object_declaration) @object
            )
            """
        ],
        "import": [
            """
            (
              [(line_comment)(multiline_comment)]* @comment.import
              .
              (import_header) @import
            )
            """
        ],
        # Kotlin import语句合并配置
        "merge_config": {
            "import": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
            "object": {"enabled": True, "max_gap_lines": -1, "preserve_order": True},
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
        "merge_config": {
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
        return lang_map.get("merge_config", {})

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
