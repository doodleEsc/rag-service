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
        "_merge_config": {
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
        "_merge_config": {
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
